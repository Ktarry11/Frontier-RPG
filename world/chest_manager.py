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

    def __init__(self):
        self._looted = set()   # {(zone_name, x, y), ...}
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
            with open(path, "r") as f:
                self._creatures_data = json.load(f).get("creatures", {})
        return self._creatures_data

    # ------------------------------------------------------------------
    # Dungeon level lookup
    # ------------------------------------------------------------------

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
            with open(enc_path, "r") as f:
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
        tilemap.set_tile(x, y, None, "interaction")

        dungeon_level = self._dungeon_level_for_zone(tilemap.name)
        effective_level = dungeon_level if dungeon_level is not None else player_level

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

    def to_dict(self):
        return {"looted": [list(t) for t in self._looted]}

    def load_dict(self, data):
        self._looted = set(tuple(t) for t in data.get("looted", []))


_chest_manager = None


def get_chest_manager():
    """Module-level singleton, same access pattern as
    world.gathering_manager.get_gathering_node_manager()."""
    global _chest_manager
    if _chest_manager is None:
        _chest_manager = ChestManager()
    return _chest_manager
