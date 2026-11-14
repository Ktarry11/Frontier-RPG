"""Secrets: hidden paths, hidden people, one-time caches, and a map that lies about them.

Kyle, 14 Nov 2026: "we can have hidden stuff as well....like people behind buildings and exploration
is rewarded. Like pathways on maps that look like they can't be walked through, but they can. I
suggest you check grim dawn style." And: "don't tell me where they are. I want to be surprised too!
Like is it possible to have the map LIE to you?"

THE DATA is data/world/secrets.json, written by tools/build_secrets.py. Each secret is one place:

    {"id", "zone",
     "passage": [[x, y], ...]   tiles drawn as rock, trees or a wall that can be walked through
     "area":    [[x, y], ...]   the hidden ground the passage leads to
     "kind":    glade | island | behind
                                a glade is cut out of rock, cliff or trees; an island is ground in
                                deep water with a ford of shallows to it; "behind" is a spot already
                                there, hidden by a building's picture, and changes nothing
     "ground":  base tile for the carved ground; "shallow": base tile for an island's ford
     "mask":    tile id         what the map shows over passage and area until it is found
     "cache":   {"x", "y", "level"} or null   a one-time chest, never respawns
     "vendor":  vendor id or null             a hidden seller standing in the area
     "door":    {"x", "y", "to", "tx", "ty"} or null
                                a portal in the area to a hidden zone (world/hidden_zones.py); the
                                portal manager links it both ways, and its glow is only drawn once
                                you are in there with it}

THREE THINGS HAPPEN AT RUNTIME.
  1. apply_all() lets the passage tiles be walked (Tilemap.secret_walkable; the art is untouched),
     puts each cache's chest down, and paints the passage and area into the tilemap's map_mask.
  2. The map screen draws map_mask instead of the truth, and never draws a dot for a hidden seller
     or a hidden cache. That is the lie: the map shows rock where there is a path.
  3. on_step() notices the first time the player stands on a secret's ground and says so. The map
     keeps lying even after: Kyle, 14 Nov, "Don't have map redraw. It can stay blank." Found
     secrets are saved, so the message comes once per character.

A cache opens once per character for a guaranteed good item (Grim Dawn's one-shot chests): rare at
worst, epic about a third of the time, and it never comes back.
"""
import json
import random
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "data" / "world" / "secrets.json"

#: Chance a cache gives an epic instead of a rare.
CACHE_EPIC_CHANCE = 0.35


class Secrets:
    def __init__(self):
        self.secrets = []
        self.found = set()
        self._by_tile = {}      # (zone, x, y) -> secret id, for passage and area tiles
        self._caches = {}       # (zone, x, y) -> secret
        self._hidden_vendors = set()
        self._vendor_secret = {}  # vendor id -> secret
        self._doors = {}        # (zone, x, y) -> secret, for doors to hidden zones
        self._tiles = {}        # secret id -> its passage and area tiles
        self.load()

    # ------------------------------------------------------------------ data
    def load(self):
        try:
            doc = json.loads(_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            doc = {}
        self.secrets = list(doc.get("secrets") or [])
        self._by_tile, self._caches, self._hidden_vendors = {}, {}, set()
        self._vendor_secret, self._tiles, self._doors = {}, {}, {}
        for s in self.secrets:
            tiles = {(x, y) for x, y in list(s.get("passage") or []) + list(s.get("area") or [])}
            self._tiles[s["id"]] = tiles
            for x, y in tiles:
                self._by_tile[(s["zone"], x, y)] = s["id"]
            c = s.get("cache")
            if c:
                self._caches[(s["zone"], c["x"], c["y"])] = s
            if s.get("vendor"):
                self._hidden_vendors.add(s["vendor"])
                self._vendor_secret[s["vendor"]] = s
            d = s.get("door")
            if d:
                self._doors[(s["zone"], d["x"], d["y"])] = s

    def by_id(self, sid):
        return next((s for s in self.secrets if s["id"] == sid), None)

    # ------------------------------------------------------------------ world
    def apply_all(self, zones):
        """zones: {name: tilemap}. Open the passages, place the caches, write the map's lies."""
        for s in self.secrets:
            tm = zones.get(s["zone"])
            if tm is None:
                continue
            self._carve(tm, s)
            c = s.get("cache")
            if c and tm.get_tile(c["x"], c["y"], "interaction") is None:
                tm.set_tile(c["x"], c["y"], "chest", "interaction")
            d = s.get("door")
            if d:
                tm.set_tile(d["x"], d["y"], "portal", "interaction")
                tm.secret_walkable.add((d["x"], d["y"]))
            self._mask(tm, s)

    @staticmethod
    def _carve(tm, s):
        """Make the secret's ground real. A glade's hollow becomes open ground and its way in stays
        drawn as the mass it cuts through; an island and its ford become ground and shallow water."""
        kind = s.get("kind", "glade")
        ground = s.get("ground") or "grass"
        # A GLADE IS NOT CARVED. Most maps are one baked painting (tools/terrain_painter.py), and a
        # painting cannot grow a clearing at runtime, so the hollow and its way in are simply made
        # walkable and keep looking like the rock or trees they are: a room inside the wall.
        for x, y in s.get("area") or []:
            if kind == "glade":
                tm.secret_walkable.add((x, y))
            elif kind == "island":
                tm.collision_layer[y][x] = None
                tm.base_layer[y][x] = ground
        for x, y in s.get("passage") or []:
            if kind == "island":
                tm.collision_layer[y][x] = None
                tm.base_layer[y][x] = s.get("shallow") or "shallow_water"
            else:
                tm.secret_walkable.add((x, y))

    def _mask(self, tm, s):
        mask = getattr(tm, "map_mask", None)
        if mask is None:
            mask = tm.map_mask = {}
        for x, y in list(s.get("passage") or []) + list(s.get("area") or []):
            mask[(x, y)] = s.get("mask", "rock")
        c = s.get("cache")
        if c:
            mask[(c["x"], c["y"])] = s.get("mask", "rock")

    def _unmask(self, tm, s):
        mask = getattr(tm, "map_mask", None) or {}
        for x, y in list(s.get("passage") or []) + list(s.get("area") or []):
            mask.pop((x, y), None)
        c = s.get("cache")
        if c:
            mask.pop((c["x"], c["y"]), None)
        tm.map_mask_version = getattr(tm, "map_mask_version", 0) + 1

    def on_step(self, tm, x, y):
        """The player stepped on (x, y). Returns a message the first time a secret is found."""
        sid = self._by_tile.get((tm.name, x, y))
        if sid is None or sid in self.found:
            return None
        self.found.add(sid)
        s = self.by_id(sid)
        return s.get("found_text") or "You've found a hidden place."

    # ------------------------------------------------------------------ map and chests
    #: How close you have to be before a hidden cache or seller is drawn at all.
    SHOW_WITHIN = 3

    def shows(self, zone_name, x, y, player_pos, vendor_id=None):
        """Is the cache or hidden seller at (x, y) drawn? Kyle, 14 Nov: "Hidden should be HIIIIIDEN"
        and "They need to be off screen so you don't just straight up see the chest there". So a
        secret's chest or seller is not drawn at all until you are in its secret ground (on the
        hidden path, in the room in the wall, on the island) and close to it. Behind a building
        it is enough to be close, because the building is drawn over it anyway. Anything that is
        not a secret always shows."""
        s = self._vendor_secret.get(vendor_id) if vendor_id else None
        if s is None:
            s = self._caches.get((zone_name, x, y)) or self._doors.get((zone_name, x, y))
        if s is None:
            return True
        if not player_pos:
            return False
        px, py = player_pos[0], player_pos[1]
        if max(abs(px - x), abs(py - y)) > self.SHOW_WITHIN:
            return False
        if s.get("kind") == "behind":
            return True
        return (px, py) in self._tiles.get(s["id"], ()) or (px, py) == (x, y)

    def is_hidden_vendor(self, vendor_id):
        return vendor_id in self._hidden_vendors

    def is_cache(self, zone_name, x, y):
        return (zone_name, x, y) in self._caches

    def hidden_points(self, zone_name):
        """Tiles the map must not mark: hidden sellers and caches."""
        out = {(x, y) for (z, x, y) in self._caches if z == zone_name}
        out |= {(x, y) for (z, x, y) in self._doors if z == zone_name}
        return out

    def is_door(self, zone_name, x, y):
        return (zone_name, x, y) in self._doors

    def doors(self):
        """[(zone, x, y, to_zone, to_x, to_y)] for every secret door."""
        return [(s["zone"], s["door"]["x"], s["door"]["y"], s["door"]["to"], s["door"]["tx"], s["door"]["ty"])
                for s in self.secrets if s.get("door")]

    def open_cache(self, zone_name, x, y, player_level, char_class=None):
        """The item in a cache: rare at worst, epic about a third of the time."""
        s = self._caches.get((zone_name, x, y))
        level = (s.get("cache") or {}).get("level", player_level) if s else player_level
        from entities.loot_generator import LootGenerator
        gen = LootGenerator()
        rarity = "epic" if random.random() < CACHE_EPIC_CHANCE else "rare"
        cls = char_class or random.choice(["Warrior", "Rogue", "Priest", "Shaman"])
        try:
            return gen.generate_item_for_class(cls, max(1, level + 2), rarity=rarity,
                                               player_level=player_level)
        except Exception:
            return gen.generate_boss_loot(creature_level=level, player_level=player_level)

    # ------------------------------------------------------------------ save
    def to_dict(self):
        return {"found": sorted(self.found)}

    def load_dict(self, data, zones=None):
        """Restore found secrets; with zones given, re-mask the map from scratch."""
        self.found = set((data or {}).get("found") or [])
        if zones:
            for tm in zones.values():
                if getattr(tm, "map_mask", None):
                    tm.map_mask.clear()
                    tm.map_mask_version = getattr(tm, "map_mask_version", 0) + 1
            for s in self.secrets:
                tm = zones.get(s["zone"])
                if tm is not None:
                    self._mask(tm, s)


_secrets = None


def get_secrets():
    global _secrets
    if _secrets is None:
        _secrets = Secrets()
    return _secrets
