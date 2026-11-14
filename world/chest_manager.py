"""
Chest manager - gives the "chest" interaction tile a real purpose.

WHY THIS EXISTS
----------------
Every dungeon/cave generator (The Den, Burning Blade Coven, Skull Rock,
Tiragarde Keep, ...) has placed a "chest" tile near its boss for a while
now via Tilemap.set_tile(x, y, "chest", "interaction") - but nothing in
the game ever read interaction_type="chest" off that tile. Walking onto
one and pressing Space fell all the way through overworld_screen.py's
vendor -> recruit -> ambient_npc -> gathering_node -> forge -> portal
chain to "try portal", which silently did nothing since there's no
portal there either. Every chest placed to date has been pure decoration.

Kyle's real spec (2026-09-18):
- Not boss-only. Regular chests belong in random side-rooms too, not
  just next to a boss.
- Regular chest loot: mostly Poor/Common/Uncommon ("basic whites or
  greens"), same weighting a trash mob already rolls.
- Boss chest loot: can roll Rare or - rarely - Epic ("blues, or very
  very rare epics"), same floored-rarity treatment a boss KILL already
  gets in combat via LootGenerator.generate_boss_loot().
- Chest level = the dungeon's own level, not the player's. Sourced from
  the dungeon's highest-level is_boss creature in creatures.json (e.g.
  Skull Rock's Gazz'uz, level 11) rather than inventing a second
  hand-authored "zone level" field - that data already exists and stays
  in sync with the bestiary automatically.
- Sometimes empty - a chest is not a guaranteed vending machine. This
  also leaves the empty branch as the natural place to hang vendor
  trash / crafting reagents later (Kyle: "eventually we can add other
  shit") without restructuring anything.
- "We will hash it out more later" - this is Phase 1 scope, not a
  claim that chest loot is a finished, tuned system.

SHAPE
------
Mirrors GatheringNodeManager's structure directly (see that file's own
docstring for why): one manager instance lives on ZoneManager,
get_chest_at_location() is the per-tile lookup overworld_screen.py
calls on Space, and opening a chest is a one-shot action - once opened
it clears its own interaction tile and remembers not to reroll, exactly
like a gathered node can't be gathered twice.

Unlike gathering nodes, chest POSITIONS are NOT re-rolled on every zone
visit - they're baked into the tilemap by each dungeon's own generator
(hand-placed near a boss, or at a handful of side-room spots), same as
recruit/ambient NPC tiles. What resets per-visit is nothing; a looted
chest stays looted (tracked by (zone_name, x, y) in _looted, persisted
the same way gathered-node / defeated-boss state already persists
elsewhere in this codebase - see ZoneManager's save/load).
"""
import random
from pathlib import Path


class ChestManager:
    """Owns loot generation for world chest tiles and tracks which
    (zone_name, x, y) chests have already been opened."""

    #: Chance a non-boss chest actually contains an item. The rest of
    #: the time it's empty - "not a guaranteed vending machine" per
    #: Kyle. Boss chests always contain something (matches
    #: generate_boss_loot()'s own no-drop-chance-roll guarantee).
    REGULAR_CHEST_DROP_CHANCE = 0.55

    #: CHESTS COME BACK. Kyle, 10 Nov: "chests respawn - very low chance overworld, much higher
    #: in dungeons." Each looted chest gets one roll when you ENTER its zone:
    RESPAWN_CHANCE_OVERWORLD = 0.05
    RESPAWN_CHANCE_DUNGEON = 0.40
    #: ...and not again for this long (real seconds), whatever the roll said. Without it,
    #: stepping in and out of a dungeon door would re-roll every chest inside on each pass and
    #: 40% would turn into "always" for the price of a short walk.
    RESPAWN_RETRY_SECONDS = 600

    def __init__(self):
        self._looted = set()   # {(zone_name, x, y), ...}
        self._next_roll = {}   # {(zone_name, x, y): earliest time.time() it may roll again}
        self._loot_generator = None   # lazy - see _get_loot_generator
        self._creatures_data = None   # lazy - see _dungeon_level_for_zone

    # ------------------------------------------------------------------
    # Lazy singletons - avoids a hard import-time dependency on
    # entities/loot_generator.py and data/creatures/creatures.json from
    # every module that merely imports chest_manager.py, same reasoning
    # combat_engine.py already applies to its own LootGenerator().
    # ------------------------------------------------------------------

    def _get_loot_generator(self):
        if self._loot_generator is None:
            from entities.loot_generator import LootGenerator
            self._loot_generator = LootGenerator()
        return self._loot_generator

    def _get_creatures_data(self):
        if self._creatures_data is None:
            import json
            path = Path(__file__).parent.parent / "data" / "creatures" / "creatures.json"
            with open(path, "r", encoding="utf-8") as f:
                self._creatures_data = json.load(f).get("creatures", {})
        return self._creatures_data

    # ------------------------------------------------------------------
    # Dungeon level lookup
    # ------------------------------------------------------------------

    def chest_level(self, zone_name, player_level):
        """The level a chest in this zone rolls its loot at. THE ZONE DECIDES, NOT THE PARTY.

        Kyle, 10 Nov: "chest items should be based on zone not on party level! i opened a
        chest in STV and got a lvl 58 item."

        A dungeon's chest already used the dungeon's level. An OPEN-WORLD chest had no level
        of its own, so it fell back to whoever opened it - a level 60 walking through a
        level 30 zone was handed level 58 gear from every chest. It now rolls inside the
        zone's own level band (world/zone_levels.py, derived from what actually spawns
        there). The opener's level is used only where a zone has no band at all, and even
        then it can only lower the result, never raise it.
        """
        dungeon_level = self._dungeon_level_for_zone(zone_name)
        if dungeon_level is not None:
            return dungeon_level
        from world.zone_levels import band
        b = band(zone_name)
        if b:
            return random.randint(int(b[0]), int(b[1]))
        return player_level

    def _dungeon_level_for_zone(self, zone_name):
        """The dungeon's own level, sourced from its highest-level
        is_boss creature in creatures.json (e.g. Skull Rock -> Gazz'uz,
        level 11) rather than a separately hand-authored field - stays
        in sync with the bestiary automatically, and correctly prefers
        a real final boss (Gazz'uz) over a mid-cave miniboss (Neru
        Fireblade) purely by picking the HIGHEST is_boss level in the
        zone's table, not just the first one found.

        Falls back to encounters.json's real per-creature data for this
        zone's "caves" entry (matched by table_key, which every
        dedicated cave generator's add_subzone() call already sets to
        the zone's own name) rather than the zone's open-area trash
        table, so a cave's level isn't accidentally read from its
        parent overworld zone's much lower baseline.

        Returns None if nothing resolves (zone has no cave encounter
        table, or no is_boss creature in it) - callers treat that as
        "use the player's own level instead", never crash.
        """
        import json
        enc_path = Path(__file__).parent.parent / "data" / "creatures" / "encounters.json"
        try:
            with open(enc_path, "r", encoding="utf-8") as f:
                enc = json.load(f).get("zones", {})
        except (OSError, json.JSONDecodeError):
            return None

        creatures = self._get_creatures_data()
        best_level = None
        for zone_data in enc.values():
            cave_table = zone_data.get("caves", {}).get(zone_name)
            if cave_table is None:
                continue
            for creature_name in cave_table.get("creatures", {}):
                cdata = creatures.get(creature_name)
                if not cdata or not cdata.get("is_boss"):
                    continue
                level_range = cdata.get("level_range")
                if not level_range:
                    continue
                level = max(level_range)
                if best_level is None or level > best_level:
                    best_level = level
            break  # table_key is unique across zones, no need to keep scanning
        return best_level

    # ------------------------------------------------------------------
    # Lookup / open
    # ------------------------------------------------------------------

    def get_chest_at_location(self, tilemap, x, y):
        """True if there's a real, unlooted chest tile at (x, y) in
        this tilemap - same "check the actual interaction layer" shape
        as every other get_X_at_location, not a separate position list
        to keep in sync (see this module's docstring on why chest
        POSITIONS aren't tracked separately the way gathering nodes are)."""
        if tilemap is None:
            return False
        if (tilemap.name, x, y) in self._looted:
            return False
        return tilemap.interaction_layer[y][x] == "chest"

    def open_chest(self, tilemap, x, y, player_level, is_boss_chest=False):
        """Open the chest at (x, y), returning an Item or None (empty).

        Marks the chest looted (clears its interaction tile, same
        double-open guard GatheringNodeManager.gather uses) regardless
        of whether it actually contained anything - an emptied chest
        should never re-roll on a second interact.

        is_boss_chest: True for a chest placed at/near a dungeon's real
        boss_position (floored at Rare, always drops something,
        matching LootGenerator.generate_boss_loot()'s own guarantee).
        False for a regular side-room chest (REGULAR_CHEST_DROP_CHANCE
        odds of being empty, no rarity floor - "basic whites or
        greens" per the normal rarity weights).
        """
        if (tilemap.name, x, y) in self._looted:
            return None
        self._looted.add((tilemap.name, x, y))
        self._next_roll[(tilemap.name, x, y)] = self._now() + self.RESPAWN_RETRY_SECONDS
        tilemap.set_tile(x, y, None, "interaction")

        effective_level = self.chest_level(tilemap.name, player_level)

        loot_gen = self._get_loot_generator()

        if is_boss_chest:
            return loot_gen.generate_boss_loot(
                creature_level=effective_level,
                player_level=player_level,
            )

        if random.random() > self.REGULAR_CHEST_DROP_CHANCE:
            # Empty - a real, intended outcome, not a bug. This is also
            # the natural spot to roll vendor trash / crafting reagents
            # instead of nothing once those exist (Kyle: "eventually we
            # can add other shit") - just add that roll here rather
            # than always returning None on the miss branch.
            return None

        return loot_gen.generate_loot_for_creature(
            creature_level=effective_level,
            player_level=player_level,
            drop_chance=1.0,  # the empty/not-empty roll already happened above
        )

    # ------------------------------------------------------------------
    # Persistence - same shape as any other "which world objects have
    # already been consumed" state (defeated cave bosses, gathered
    # nodes once they stop re-rolling, etc).
    # ------------------------------------------------------------------

    def open_secret_cache(self, tilemap, x, y, player_level):
        """A hidden cache (world/secrets.py): opens once, always holds something good, never returns."""
        key = (tilemap.name, x, y)
        if key in self._looted:
            return None
        self._looted.add(key)
        tilemap.set_tile(x, y, None, "interaction")
        from world.secrets import get_secrets
        return get_secrets().open_cache(tilemap.name, x, y, player_level)

    @staticmethod
    def _now():
        import time
        return time.time()

    def on_enter_zone(self, tilemap, is_dungeon=False):
        """Called when the player arrives in `tilemap`. Rolls each looted chest there for a
        respawn and puts the ones that pass back on the map. Returns how many came back.

        A chest that fails its roll, or was just looted, is not rolled again until
        RESPAWN_RETRY_SECONDS have passed.
        """
        if tilemap is None:
            return 0
        chance = self.RESPAWN_CHANCE_DUNGEON if is_dungeon else self.RESPAWN_CHANCE_OVERWORLD
        now = self._now()
        back = 0
        from world.secrets import get_secrets
        secrets = get_secrets()
        for key in [k for k in self._looted if k[0] == tilemap.name]:
            if secrets.is_cache(*key):
                continue        # a hidden cache is found once and never comes back
            if now < self._next_roll.get(key, 0):
                continue
            if random.random() < chance:
                _zone, x, y = key
                self._looted.discard(key)
                self._next_roll.pop(key, None)
                tilemap.set_tile(x, y, "chest", "interaction")
                back += 1
            else:
                self._next_roll[key] = now + self.RESPAWN_RETRY_SECONDS
        return back

    def apply_to_world(self, zones):
        """Take every looted chest off its map. `zones` is {zone_name: tilemap}.

        The world is rebuilt from scratch on startup with every chest in place, and looted
        chests were never written to the save - so loading a game put all of them back.
        """
        for zone_name, x, y in self._looted:
            tilemap = zones.get(zone_name)
            if tilemap is not None and tilemap.get_tile(x, y, "interaction") == "chest":
                tilemap.set_tile(x, y, None, "interaction")

    def to_dict(self):
        now = self._now()
        return {"looted": [list(t) for t in sorted(self._looted)],
                # Stored as seconds REMAINING, not a clock time, so the wait is play time across
                # a save and load rather than something that expires while the game is closed.
                "wait": [[z, x, y, int(max(0, t - now))] for (z, x, y), t in sorted(self._next_roll.items())
                         if (z, x, y) in self._looted and t > now]}

    def load_dict(self, data):
        data = data or {}
        self._looted = set(tuple(t) for t in data.get("looted", []))
        now = self._now()
        self._next_roll = {(z, x, y): now + left for z, x, y, left in data.get("wait", [])}


_chest_manager = None


def get_chest_manager():
    """Module-level singleton, same access pattern as
    world.gathering_manager.get_gathering_node_manager()."""
    global _chest_manager
    if _chest_manager is None:
        _chest_manager = ChestManager()
    return _chest_manager
