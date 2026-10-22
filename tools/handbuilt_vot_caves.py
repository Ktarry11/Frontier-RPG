"""
Hand-built layouts for the two Valley of Trials caves:

  The Den               85x70   spider/scorpid brood cave   (portal 42,66 / boss 42,12)
  Burning Blade Coven   100x85  fel-ritual orc stronghold   (portal 50,81 / boss 78,50)

Both are drawn room by room with tools.dungeon_builder.Builder, dressed with a
SMALL number of logical props (centrepieces + biome-appropriate clusters), and
painted by tools/bake_vot_caves.py (tools/terrain_painter.py) into one
continuous painting per cave, registered exactly like the outdoor zone.

Prop rule (Kyle): less is more. Common props must make sense where they sit
(eggs in a nursery, bookshelves in a library, fel crystals around a fel
portal), plus a few centrepieces. Every prop goes through CaveLayout.prop,
which refuses placements that sit on water/markers or that would wall off any
part of the cave.
"""
import math
import os
from collections import deque

import numpy as np

from world.tilemap import Tilemap

DP = "assets/tiles/dungeon_props/"
OLD_DEN = "assets/tiles/the_den/props/"
BAKED_DEN = "assets/tiles/the_den/baked"
BAKED_BBC = "assets/tiles/burning_blade_coven/baked"


# ------------------------------------------------------------------ pools
def pool_fields(pools, gx, gy):
    """Analytic smooth pools shared by the layout and the baker.
    pools: [(cx, cy, rx, ry, phase)].  Returns (shallow_extent, deep_extent)
    in tiles (>0 inside).  Integer harmonics only (no seam)."""
    s_best = np.full(np.shape(gx), -99.0, np.float32)
    d_best = np.full(np.shape(gx), -99.0, np.float32)
    for (cx, cy, rx, ry, ph) in pools:
        dx, dy = (gx - cx) / rx, (gy - cy) / ry
        a = np.arctan2(dy, dx)
        r = np.hypot(dx, dy)
        f = 1 + 0.10 * np.sin(2 * a + ph) + 0.07 * np.sin(3 * a + ph * 1.7) + 0.04 * np.sin(5 * a + ph * 0.3)
        sc = (rx + ry) / 2
        s_best = np.maximum(s_best, ((f * 0.95 - r) * sc).astype(np.float32))
        d_best = np.maximum(d_best, ((f * 0.60 - r) * sc).astype(np.float32))
    return s_best, d_best


DEN_POOLS = [(42, 39, 9.0, 6.5, 0.7), (14, 22, 3.8, 3.2, 2.1)]
BBC_FEL_POOLS = [(50, 40, 6.5, 4.2, 1.3)]          # shallow fel puddle (walkable, painted green)
BBC_DARK_POOLS = [(20, 28, 4.2, 3.2, 0.4)]          # deep dark pool in the crystal cavern


def _apply_pools(zone, pools, deep_ok=True, shallow_only=False):
    from tools.dungeon_builder import Builder  # noqa: F401  (ensures import order)
    h, w = zone.height, zone.width
    ys, xs = np.mgrid[0:h, 0:w]
    s, d = pool_fields(pools, xs + 0.5, ys + 0.5)
    for y in range(h):
        for x in range(w):
            if zone.collision_layer[y][x] == "rock":
                continue
            if d[y, x] > 0 and not shallow_only:
                zone.set_tile(x, y, "deep_water", "base")
                zone.collision_layer[y][x] = None
            elif s[y, x] > 0:
                zone.set_tile(x, y, "shallow_water", "base")
                zone.collision_layer[y][x] = None


# ------------------------------------------------------------------ helper
class CaveLayout:
    """Builder wrapper: guarded props, flood-fill QA."""

    def __init__(self, zone, start):
        from tools.dungeon_builder import Builder, _aspect
        self.z = zone
        self.b = Builder(zone, wall_id="rock", floor_id="dirt")
        self._aspect = _aspect
        self.start = start
        self.critical = []
        self.skipped = []
        self.placed = 0

    def mark(self, kind, x, y):
        self.z.set_tile(x, y, kind, "interaction")
        if kind in ("portal", "boss_marker", "chest"):
            self.critical.append((x, y))

    def _reach(self, blocked=frozenset()):
        z = self.z
        seen = {self.start}
        q = deque([self.start])
        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if n not in seen and n not in blocked and z.is_walkable(*n):
                    seen.add(n)
                    q.append(n)
        return seen

    def prop(self, name, cx, base_y, height, solid=False, fraction=0.5, avoid=2,
             where=DP, near_ok=False):
        path = f"{where}{name}.png"
        z = self.z
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        if not z.is_walkable(cx, base_y) or z.base_layer[base_y][cx] in ("shallow_water", "deep_water", "lava"):
            self.skipped.append((name, cx, base_y, "base not dry floor"))
            return False
        if not near_ok:
            for (qx, qy) in self.critical:
                if max(abs(qx - cx), abs(qy - base_y)) <= avoid:
                    self.skipped.append((name, cx, base_y, "near marker"))
                    return False
        wt = max(1, round(height * self._aspect(path)))
        ax, ay = cx - wt // 2, base_y - height + 1
        blocked = set()
        if solid:
            if solid is True:
                rows, c0, c1 = height, ax, ax + wt
            else:
                rows = max(1, round(height * fraction))
                c0 = ax + int(wt * 0.2)
                c1 = ax + max(int(wt * 0.8), int(wt * 0.2) + 1)
            for y in range(ay + height - rows, ay + height):
                for x in range(c0, c1):
                    if 0 <= x < z.width and 0 <= y < z.height and z.is_walkable(x, y):
                        blocked.add((x, y))
            if any((qx, qy) in blocked for (qx, qy) in self.critical):
                self.skipped.append((name, cx, base_y, "covers marker"))
                return False
            before = self._reach()
            after = self._reach(frozenset(blocked))
            lost = (before - blocked) - after
            if lost:
                self.skipped.append((name, cx, base_y, f"would isolate {len(lost)} tiles"))
                return False
        self.b.prop(path, cx, base_y, height, solid=solid, fraction=fraction)
        self.placed += 1
        return True

    def finish(self, targets):
        """Flood-fill QA: raise on unreachable markers or isolated walkable pockets."""
        seen = self._reach()
        missing = [t for t in targets if tuple(t[:2]) not in seen]
        if missing:
            raise AssertionError(f"{self.z.name}: unreachable {missing}")
        total = sum(self.z.is_walkable(x, y) for y in range(self.z.height) for x in range(self.z.width))
        if total != len(seen):
            raise AssertionError(f"{self.z.name}: {total - len(seen)} walkable tiles unreachable (isolated pockets)")
        return len(seen)


# ================================================================== THE DEN
DEN_PORTAL = (42, 66)
DEN_BOSS = (42, 12)
DEN_CHESTS = [(42, 10), (63, 52), (21, 58)]


def build_den():
    zone = Tilemap("The Den", 85, 70,
                   "A scorpid-and-spider brood cave beneath the Valley of Trials.")
    zone.is_cave = True
    zone.region = "Valley of Trials"
    zone.fixed_spawns = False
    L = CaveLayout(zone, DEN_PORTAL)
    b = L.b

    # --- rooms (entrance in the south, boss in the north, a loop around the lake)
    b.lobes([(42, 63, 9, 4), (34, 61, 4, 3), (50, 61, 4, 3)])               # Burrow Mouth
    b.corridor([(42, 59), (42, 51)], width=3)
    b.corridor([(49, 61), (55, 57), (60, 53)], width=2)                       # to the larder
    b.lobes([(62, 52, 7, 4), (67, 55, 3, 3)])                                 # The Larder
    b.lobes([(42, 40, 16, 11), (29, 36, 6, 5), (55, 35, 6, 5), (42, 29, 5, 3)])  # Weeping Pool hall
    b.corridor([(27, 36), (21, 40), (15, 45), (15, 50)], width=2)             # west route
    b.lobes([(16, 54, 9, 6), (9, 59, 4, 3), (23, 59, 5, 3)])                  # Husk Warren
    b.corridor([(28, 33), (22, 28), (17, 25)], width=2)                       # north-west route
    b.lobes([(14, 22, 9, 7), (7, 27, 3, 3)])                                  # Mushroom Grotto
    b.corridor([(17, 17), (21, 13), (29, 12)], width=2)                       # grotto -> boss (loop)
    b.corridor([(56, 34), (62, 30), (66, 28)], width=2)                       # east route
    b.lobes([(68, 24, 9, 7), (75, 29, 4, 3)])                                 # The Nursery
    b.corridor([(64, 18), (58, 14), (54, 12)], width=2)                       # nursery -> boss (loop)
    b.corridor([(42, 28), (42, 21)], width=3)                                 # north: boss approach
    b.lobes([(42, 12, 13, 8), (31, 11, 5, 4), (53, 11, 5, 4), (42, 5, 7, 3)])  # Brood Throne

    _apply_pools(zone, DEN_POOLS)

    for name, x, y, w, h in [("The Burrow Mouth", 28, 56, 30, 14), ("The Larder", 54, 47, 20, 14),
                             ("The Weeping Pool", 24, 27, 38, 26), ("The Husk Warren", 4, 47, 26, 17),
                             ("The Mushroom Grotto", 3, 14, 22, 18), ("The Nursery", 58, 16, 24, 20),
                             ("The Brood Throne", 26, 2, 34, 22)]:
        zone.add_subzone(name, x, y, w, h)
    zone.add_subzone("The Den", 0, 0, zone.width, zone.height)

    # --- markers
    L.mark("portal", *DEN_PORTAL)
    L.mark("boss_marker", *DEN_BOSS)
    for c in DEN_CHESTS:
        L.mark("chest", *c)
    zone.boss_position = DEN_BOSS
    zone.boss_positions = [(DEN_BOSS[0], DEN_BOSS[1], "Nest Guardian")]

    # --- props: few, logical.  Eggs in nurseries, webs near silk, mushrooms in
    # the damp, husks where prey was dragged; one big centrepiece in the throne.
    p = L.prop
    # burrow mouth: a torch either side of the door, one web in a corner
    p("den_torch", 36, 63, 4)
    p("den_torch", 48, 63, 4)
    p("den_web_wall", 33, 60, 4)
    # weeping pool hall: glow mushrooms on the damp shore, stalagmites as a frame
    p("den_glow_mushrooms", 30, 42, 3)
    p("den_glow_mushrooms", 55, 43, 3)
    p("den_stalagmites", 28, 33, 4, solid="core")
    p("den_stalagmite_pair", 56, 31, 4, solid="core")
    # larder: cocoons of the unlucky
    p("den_web_cocoon", 59, 53, 4)
    p("den_web_cocoon", 65, 50, 4)
    p("den_dead_recruit", 66, 54, 3)
    p("den_backpack", 60, 55, 2)
    # husk warren
    p("den_chitin_husk", 13, 55, 3)
    p("den_chitin_husk", 21, 56, 3)
    p("den_leg_bones", 10, 60, 2)
    p("den_eggshell_pile", 17, 52, 2)
    # mushroom grotto
    p("den_glow_mushrooms", 11, 19, 3)
    p("den_glow_mushrooms", 18, 26, 3)
    p("den_rock_rubble", 8, 25, 2)
    # nursery: the eggs
    p("den_egg_cluster", 66, 22, 4, solid="core")
    p("den_egg_cluster", 72, 26, 4, solid="core")
    p("den_egg_cluster", 69, 19, 4, solid="core")
    p("den_eggshell_pile", 64, 27, 2)
    # brood throne: the nest mound is the centrepiece
    p("den_nest_mound", 42, 8, 6, solid="core", avoid=1)
    p("den_egg_cluster", 34, 10, 4, solid="core")
    p("den_egg_cluster", 50, 10, 4, solid="core")
    p("den_web_wall", 36, 5, 5)
    p("den_web_wall", 48, 5, 5)

    L.finish([DEN_PORTAL, DEN_BOSS] + DEN_CHESTS)

    # --- hand-placed, VISIBLE trash (the pinned-boss cave used to rely on a 2% per-step roll, so a normal
    # walk through could meet nothing at all).  Room by room, levels ramping with depth; no respawns until
    # you leave and re-enter.  Each point snaps to the nearest walkable tile that is not a marker.
    keep_clear = [DEN_PORTAL, DEN_BOSS] + DEN_CHESTS
    wanted = [
        # Burrow Mouth - the welcome party (L2-3)
        (37, 61, "Cave Skitterer", 2), (47, 61, "Cave Skitterer", 2), (42, 56, "Den Webspinner", 3),
        # The Larder (L3-4)
        (59, 51, "Den Webspinner", 3), (65, 53, "Den Webspinner", 3), (62, 49, "Husk Crawler", 4),
        # Weeping Pool hall (L3-4)
        (33, 44, "Den Webspinner", 3), (51, 45, "Cave Skitterer", 3), (42, 47, "Husk Crawler", 4),
        (30, 36, "Den Webspinner", 4), (55, 36, "Cave Skitterer", 3),
        # Husk Warren (L4-5)
        (13, 53, "Husk Crawler", 4), (20, 56, "Husk Crawler", 5), (9, 59, "Cave Skitterer", 4), (15, 58, "Husk Crawler", 5),
        # Mushroom Grotto (L3-4)
        (12, 21, "Cave Skitterer", 3), (17, 25, "Den Webspinner", 4), (9, 27, "Cave Skitterer", 3),
        # The Nursery (L4-5): egg tenders guard the clutches
        (65, 23, "Egg Tender", 4), (72, 22, "Egg Tender", 4), (74, 28, "Egg Tender", 5), (68, 27, "Husk Crawler", 5),
        # Brood Throne approach and hall (L5)
        (40, 23, "Husk Crawler", 5), (44, 23, "Husk Crawler", 5), (33, 12, "Egg Tender", 5), (51, 12, "Egg Tender", 5),
    ]
    taken = []
    zone.trash_spawns = []
    for (wx, wy, name, lvl) in wanted:
        spot = None
        for r in range(0, 6):
            ring = [(wx + dx, wy + dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1)
                    if max(abs(dx), abs(dy)) == r]
            for (x, y) in ring:
                if (zone.is_walkable(x, y) and zone.get_tile(x, y, "base") not in ("deep_water", "shallow_water")
                        and all(abs(x - kx) + abs(y - ky) > 3 for kx, ky in keep_clear)
                        and all(abs(x - tx) + abs(y - ty) > 3 for tx, ty in taken)):
                    spot = (x, y)
                    break
            if spot:
                break
        if spot is None:
            raise RuntimeError(f"Den trash '{name}' near ({wx},{wy}) found no walkable tile")
        taken.append(spot)
        zone.trash_spawns.append((spot[0], spot[1], name, lvl))
    zone.fixed_spawns = True
    return zone, L


# ===================================================== BURNING BLADE COVEN
BBC_PORTAL = (50, 81)
BBC_BOSS = (78, 50)
BBC_CHESTS = [(78, 47), (14, 66), (86, 67), (26, 22), (50, 14)]


def build_bbc():
    zone = Tilemap("Burning Blade Coven", 100, 85,
                   "A fel-tainted Burning Blade stronghold carved into the rock beneath the Valley of Trials.")
    zone.is_cave = True
    zone.region = "Valley of Trials"
    zone.fixed_spawns = False
    L = CaveLayout(zone, BBC_PORTAL)
    b = L.b

    b.lobes([(50, 78, 11, 5), (41, 76, 4, 3), (59, 76, 4, 3)])                 # Vestibule
    b.corridor([(50, 73), (50, 68)], width=3)
    b.lobes([(50, 60, 15, 9), (37, 59, 5, 5), (63, 59, 5, 5), (50, 52, 6, 3)])  # Summoning Hall
    b.corridor([(36, 60), (29, 62)], width=3)
    b.lobes([(21, 62, 11, 8), (13, 58, 4, 4), (14, 67, 4, 3)])                 # Acolyte Cells
    b.corridor([(64, 60), (71, 62)], width=3)
    b.lobes([(79, 63, 11, 8), (87, 58, 4, 4), (86, 68, 4, 3)])                 # Ritual Library
    b.corridor([(50, 51), (50, 45)], width=3)
    b.lobes([(50, 38, 14, 8), (38, 36, 5, 5), (62, 36, 5, 5)])                 # Fel Court
    b.corridor([(37, 34), (30, 32), (25, 30)], width=2)
    b.lobes([(22, 28, 10, 7), (14, 31, 4, 4), (25, 21, 5, 4)])                 # Crystal Cavern
    b.corridor([(16, 34), (16, 44), (17, 54)], width=2)                        # cavern -> cells (loop)
    b.corridor([(63, 35), (70, 38), (75, 42)], width=2)                        # court -> sanctum
    b.lobes([(78, 47, 12, 8), (68, 47, 5, 4), (88, 47, 5, 4), (78, 39, 6, 3)])  # Yarrog's Sanctum
    b.corridor([(80, 58), (80, 54)], width=2)                                  # library -> sanctum (loop)
    b.corridor([(50, 30), (50, 22)], width=2)
    b.lobes([(50, 16, 9, 6)])                                                  # Tribute Vault

    # lava basins flank the sanctum and the vault (impassable by design)
    b.lobes([(70, 50, 3, 3), (86, 50, 3, 3), (43, 16, 2, 3), (57, 16, 2, 3)], base="lava")
    _apply_pools(zone, BBC_FEL_POOLS, shallow_only=True)
    _apply_pools(zone, BBC_DARK_POOLS)

    for name, x, y, w, h in [("The Vestibule", 36, 71, 30, 12), ("The Summoning Hall", 33, 50, 36, 20),
                             ("The Acolyte Cells", 6, 52, 30, 20), ("The Ritual Library", 66, 54, 28, 20),
                             ("The Fel Court", 34, 29, 34, 18), ("The Crystal Cavern", 8, 16, 30, 24),
                             ("Yarrog's Sanctum", 62, 34, 32, 24), ("The Tribute Vault", 40, 8, 20, 16)]:
        zone.add_subzone(name, x, y, w, h)
    zone.add_subzone("Burning Blade Coven", 0, 0, zone.width, zone.height)

    L.mark("portal", *BBC_PORTAL)
    L.mark("boss_marker", *BBC_BOSS)
    for c in BBC_CHESTS:
        L.mark("chest", *c)
    zone.boss_position = BBC_BOSS
    zone.boss_positions = [(BBC_BOSS[0], BBC_BOSS[1], "Yarrog Baneshadow")]

    p = L.prop
    # vestibule: archway frames the corridor in, banners either side of the door
    p("bbc_archway", 50, 72, 6)
    p("bbc_banner", 44, 77, 5)
    p("bbc_banner", 56, 77, 5)
    # summoning hall: the circle is the centrepiece
    p("bbc_summon_circle", 50, 61, 5, avoid=0)
    p("bbc_fel_brazier", 42, 56, 4, solid="core")
    p("bbc_fel_brazier", 58, 56, 4, solid="core")
    p("bbc_rune_pillar", 36, 57, 5, solid="core")
    p("bbc_rune_pillar", 64, 57, 5, solid="core")
    # acolyte cells
    p("bbc_cage", 17, 60, 5, solid="core")
    p("bbc_cage", 24, 66, 5, solid="core")
    p("bbc_weapon_rack", 22, 57, 4)
    # ritual library: shelves, a desk, two candelabra
    p("bbc_bookshelf", 75, 58, 5, solid="core")
    p("bbc_bookshelf", 84, 58, 5, solid="core")
    p("bbc_warlock_desk", 79, 66, 3, solid="core")
    p("bbc_candelabra", 73, 62, 4)
    p("bbc_candelabra", 86, 62, 4)
    # fel court: the bonfire, two pylons
    p("bbc_fel_bonfire", 50, 33, 5, solid="core")
    p("bbc_fel_pylon", 39, 41, 5, solid="core")
    p("bbc_fel_pylon", 61, 41, 5, solid="core")
    # crystal cavern: crystals ARE the room
    p("vot_fel_crystals", 13, 29, 4, solid="core")
    p("bbc_red_stalagmites", 14, 33, 4, solid="core")
    p("vot_fel_crystals", 28, 25, 3)
    p("bbc_obsidian_spikes", 19, 22, 4)
    # sanctum: the throne, banners, powder kegs of fel
    p("bbc_throne", 78, 42, 6, solid="core", avoid=3)
    p("bbc_banner", 70, 44, 5)
    p("bbc_banner", 86, 44, 5)
    p("bbc_fel_barrels", 73, 53, 3)
    p("bbc_skull_pile", 84, 53, 3)
    # tribute vault
    p("bbc_skull_pile", 46, 18, 3)
    p("bbc_skull_pile", 54, 18, 3)

    L.finish([BBC_PORTAL, BBC_BOSS] + BBC_CHESTS)
    return zone, L


# ------------------------------------------------------------- registration
def register_baked(zone, baked_dir, chunk=20):
    for cy in range(0, zone.height, chunk):
        for cx in range(0, zone.width, chunk):
            fn = f"{baked_dir}/ground_{cx}_{cy}.jpg"
            if not os.path.exists(fn):
                raise FileNotFoundError(f"{fn} - run python3 tools/bake_vot_caves.py")
            w, h = min(chunk, zone.width - cx), min(chunk, zone.height - cy)
            zone.add_ground_chunk(fn, cx, cy, w, h)
            zone.ground_chunks[-1]["exact"] = True
            zone.add_water_chunk(fn, cx, cy, w, h)
            zone.add_obstacle_chunk(fn, cx, cy, w, h)


def generate_the_den():
    zone, _ = build_den()
    register_baked(zone, BAKED_DEN)
    return zone


def generate_burning_blade_coven():
    zone, _ = build_bbc()
    register_baked(zone, BAKED_BBC)
    return zone
