"""
Gathering node manager - Phase 1 (Herbalism + Mining, early tier only).

WHY THIS SHAPE
---------------
Kyle's ask: nodes should re-roll their positions every time you leave and
re-enter a zone, from a pool of possible spawn points, with only a
percentage of the pool active at once - not fixed coordinates baked into
the map once (that's the recruit/ambient-NPC pattern, which is wrong here
because nodes are meant to feel like they come and go, not be permanent
landmarks), and not a per-tile-step random roll either (that's the
creature encounter pattern, which has no visible object to walk up to -
Kyle explicitly wants a real thing on the ground you interact with).

So this follows CaveSpawnManager's populate()/clear() shape instead:
one manager instance lives on ZoneManager, populate(zone) is called on
every transition into an overworld zone and throws away the previous
layout, which is what gives "re-rolled every visit" for free. Unlike
cave spawns (which get literal authored (x,y) positions from a
generator), node candidate slots are just random walkable tiles rolled
fresh each time - there's no hand-authored coordinate list for "every
patch of grass a Peacebloom could grow on" and there shouldn't be one;
that's exactly the kind of tedious hand-placement the recruit/ambient
tile-carving system exists to avoid needing.

Only 4 starting zones have a node_pools.json entry (Valley of Trials,
Durotar, Razor Hill, Echo Isles) - Phase 1 scope is proving the loop
works, not covering every zone in the game.
"""
import json
import random
from pathlib import Path
from world.zone_keys import zone_key as _zk


class GatheringNode:
    """A single active, gatherable node sitting on a specific tile."""

    def __init__(self, x, y, material_id):
        self.x = x
        self.y = y
        self.material_id = material_id
        self.gathered = False

    def __repr__(self):
        state = "gathered" if self.gathered else "active"
        return f"<GatheringNode {self.material_id} @({self.x},{self.y}) {state}>"


class GatheringNodeManager:
    """Owns material definitions and the current zone's active node layout.

    One instance lives on ZoneManager, same as CaveSpawnManager. populate()
    is called on every transition into a zone with a node pool and replaces
    whatever nodes were there before - that IS the "re-roll every visit"
    behavior, no separate timer or dirty-flag needed.
    """

    #: How close the player must stand to a node to gather it. Matches
    #: CaveSpawnManager.TRIGGER_RADIUS's convention of 1 (must be
    #: standing adjacent-or-on, not "somewhere in view").
    TRIGGER_RADIUS = 0

    def __init__(self):
        self.materials = {}      # material_id -> material def dict (raw JSON, not Material instances - see get_material_instance)
        self.node_pools = {}     # normalized zone key -> pool config dict
        self.active_nodes = []   # GatheringNode list for the CURRENT zone only
        self.zone_key = None
        self._load_data()

    def _load_data(self):
        data_dir = Path(__file__).parent.parent / "data" / "gathering"

        materials_file = data_dir / "materials.json"
        if materials_file.exists():
            with open(materials_file, 'r') as f:
                self.materials = json.load(f).get("materials", {})

        pools_file = data_dir / "node_pools.json"
        if pools_file.exists():
            with open(pools_file, 'r') as f:
                # NORMALISE THE KEYS AT LOAD. The lookup side goes through _zone_key, so the index
                # side has to as well or the two disagree the moment a zone name contains an article
                # or an apostrophe - which is exactly the asymmetry that hid three broken rosters.
                raw = json.load(f).get("zones", {})
                self.node_pools = {self._zone_key(k): v for k, v in raw.items()}

        self._synthesize_cave_pools()

    def _synthesize_cave_pools(self):
        """Build an ore-only node pool for each cave in CAVE_TO_PARENT_ZONE,
        derived from its parent zone's already-authored table, and add it
        to self.node_pools under the cave's own zone key. This is what
        lets populate() treat a mining cave exactly like any other zone
        with a pool entry - no separate cave-vs-overworld branch needed
        there, it just looks up the cave's key and finds a real (synthetic)
        entry waiting for it.

        Herb entries are dropped entirely (caves are mining spots, not
        foraging spots - Kyle never asked for herb nodes underground).
        Ore weights carry over at CAVE_ORE_DENSITY_MULT versus the
        parent's own weights, then the whole table is renormalized to
        integers - materials that were plain zero-ore parents (none exist
        right now, but a future zone might have herb-only tables) simply
        produce an empty ore table, which populate() already treats as a
        safe no-op (see its `if not table` check).
        """
        for cave_name, parent_zone_name in CAVE_TO_PARENT_ZONE.items():
            parent_key = self._zone_key(parent_zone_name)
            parent_pool = self.node_pools.get(parent_key)
            if parent_pool is None:
                continue

            parent_table = parent_pool.get("table", {})
            ore_table = {}
            for material_id, weight in parent_table.items():
                data = self.materials.get(material_id)
                if data is None or data.get("material_type") != "ore":
                    continue
                ore_table[material_id] = weight

            if not ore_table:
                continue

            # Renormalize to clean integers after applying the density
            # multiplier, rather than leaving fractional weights -
            # random.choices accepts floats fine, but keeping this data
            # shape identical to every hand-authored table in
            # node_pools.json (plain ints) means nothing downstream ever
            # needs to know a given table was synthesized vs hand-written.
            ore_table = {mid: max(1, round(weight * CAVE_ORE_DENSITY_MULT))
                        for mid, weight in ore_table.items()}

            cave_key = self._zone_key(cave_name)
            self.node_pools[cave_key] = {
                "slots": parent_pool.get("slots", 10),
                "active_percent": parent_pool.get("active_percent", 0.4),
                "table": ore_table,
            }

    @staticmethod
    def _zone_key(zone):
        """Same normalization every other zone-keyed lookup in this
        codebase uses (ZoneManager._normalize_zone_key, VendorManager,
        race_registry, quest zone_key) - lowercase, spaces to
        underscores, strip apostrophes."""
        return _zk(zone)

    # ------------------------------------------------------------------
    # Layout

    def clear(self):
        self.active_nodes = []
        self.zone_key = None

    def populate(self, tilemap, zone_name):
        """Roll a fresh node layout for entering `zone_name`. Wipes
        whatever was active before (matches CaveSpawnManager.populate),
        which is exactly what gives "different nodes every time you come
        back" - there's no separate reroll trigger to remember to call.

        No-ops (clears and returns) if this zone has no node_pools.json
        entry, so calling populate() unconditionally on every zone
        transition is safe and doesn't require ZoneManager to know in
        advance which zones have gathering.
        """
        self.clear()
        key = self._zone_key(zone_name)

        # Hard stop for real Dungeons regardless of what's in node_pools -
        # CAVE_TO_PARENT_ZONE is hand-curated to never include one, but
        # this guard means a future mistake there (or node_pools.json
        # somehow gaining a dungeon entry) fails safe instead of silently
        # placing ore in a lore-built boss room. See
        # world/zone_classification.py for the confirmed Dungeon list and
        # why it's kept as its own source of truth.
        from world.zone_classification import is_dungeon
        if is_dungeon(zone_name):
            return

        # Hard stop for towns (Kyle, 2026-09-12: "Towns don't have ore" -
        # and no herbs either, same safe-town-design convention every
        # other town-only system in this codebase already follows).
        # Before this check, towns were only excluded by ACCIDENT - no
        # zone here ever got a node_pools.json entry written for it, but
        # nothing actually stopped one from working if it had. Checking
        # tilemap.is_town directly (set on the real Tilemap by every town
        # generator - Brill, The Sepulcher, Astranaar, Zoram Strand,
        # Splintertree Post, Orgrimmar, Ratchet, ...) means this is now a
        # real guarantee instead of a coincidence that happened to hold
        # up so far.
        if getattr(tilemap, "is_town", False):
            return

        pool = self.node_pools.get(key)
        if pool is None:
            return

        self.zone_key = key
        slots = pool.get("slots", 0)
        active_percent = pool.get("active_percent", 0.0)
        table = pool.get("table", {})
        if not table or slots <= 0 or active_percent <= 0:
            return

        num_active = max(1, round(slots * active_percent)) if slots > 0 else 0

        # Roll `slots` distinct random walkable tiles as candidate points,
        # then only the first num_active become real nodes. Rolling ALL
        # slots first (not just num_active) means the "phantom" unused
        # slots still cost a walkability check, matching how a real WoW
        # zone has more possible node spots than are ever active at once.
        candidates = self._roll_candidate_tiles(tilemap, slots)
        chosen = candidates[:num_active]

        material_ids = list(table.keys())
        weights = list(table.values())

        for (x, y) in chosen:
            material_id = random.choices(material_ids, weights=weights, k=1)[0]
            self.active_nodes.append(GatheringNode(x, y, material_id))
            tilemap.set_tile(x, y, "gathering_node", "interaction")

    def _roll_candidate_tiles(self, tilemap, count, max_attempts=500):
        """Pick up to `count` distinct random walkable tiles. Avoids
        collision tiles (via is_walkable) and avoids the exact tile the
        player is not necessarily known to be on here - ZoneManager
        re-checks walkability implicitly since a node can only be placed
        on an already-walkable tile, so this never blocks a path.

        Caps at max_attempts rather than looping forever on a
        pathologically small/dense map - worst case you just get fewer
        nodes than requested that visit, which is a quiet degrade, not
        a crash.
        """
        found = []
        seen = set()
        attempts = 0
        while len(found) < count and attempts < max_attempts:
            attempts += 1
            x = random.randint(0, tilemap.width - 1)
            y = random.randint(0, tilemap.height - 1)
            if (x, y) in seen:
                continue
            seen.add((x, y))
            if tilemap.is_walkable(x, y) and tilemap.get_tile(x, y, "interaction") is None:
                found.append((x, y))
        return found

    # ------------------------------------------------------------------
    # Interaction

    def get_node_at(self, x, y):
        """Active, ungathered node at this exact tile, or None."""
        for node in self.active_nodes:
            if node.x == x and node.y == y and not node.gathered:
                return node
        return None

    def gather(self, node, tilemap):
        """Mark a node gathered, clear its interaction tile, and return
        the material_id it dropped. Returns None if the node was already
        gathered (double-interact guard) - callers shouldn't rely on this
        for validation, get_node_at already excludes gathered nodes, but
        it's cheap insurance against a stale reference.
        """
        if node.gathered:
            return None
        node.gathered = True
        tilemap.set_tile(node.x, node.y, None, "interaction")
        return node.material_id

    def get_material_def(self, material_id):
        """Raw material definition dict (name, profession, tier, icon_id,
        ...) for a material_id, or None."""
        return self.materials.get(material_id)

    def make_material_instance(self, material_id):
        """Build a real Material entity from a material_id, ready to hand
        to Character.add_material(). Returns None for an unknown id."""
        from entities.material import Material
        data = self.materials.get(material_id)
        if data is None:
            return None
        return Material(
            material_id=material_id,
            name=data["name"],
            material_type=data["material_type"],
            profession=data["profession"],
            tier=data["tier"],
            description=data.get("description", ""),
            stack_limit=data.get("stack_limit", 20),
            sell_price=data.get("sell_price", 0),
            icon_id=data.get("icon_id"),
            skill_range=data.get("skill_range"),
            vendor_price=data.get("vendor_price", 0),
        )

    def roll_skill_up(self, material_id, current_skill):
        """Roll whether gathering this material grants a skill-up, using
        the material's skill_range (see materials.json's _comment for the
        full orange/yellow/green/grey explanation). Returns True/False.

        No skill_range on the material (or no material found) always
        succeeds - a material authored without an explicit range
        shouldn't silently block all progress, same "fail open" instinct
        as most of this codebase's other missing-data fallbacks.

        current_skill is the character's CURRENT skill in this
        material's profession, checked BEFORE this gather - so the very
        first gather at skill 0 is always evaluated against orange_ends,
        never accidentally against a skill value this gather hasn't
        granted yet.
        """
        data = self.materials.get(material_id)
        if data is None:
            return True
        skill_range = data.get("skill_range")
        if not skill_range:
            return True

        orange_ends, yellow_ends, green_ends, grey_at = skill_range

        if current_skill < orange_ends:
            return True
        if current_skill >= grey_at:
            return False
        if current_skill < yellow_ends:
            return random.random() < 0.75
        if current_skill < green_ends:
            return random.random() < 0.35
        # Between green_ends and grey_at: still possible, just rare.
        return random.random() < 0.10

    def active_nodes_render_data(self):
        """Shape active_nodes into plain (x, y, material_type, icon_id)
        tuples for the renderer - mirrors CaveSpawnManager.active_positions()'s
        job of keeping tilemap_renderer.py decoupled from manager/entity
        internals, it only ever needs to know how to draw a tuple.
        Gathered (already-collected) nodes are excluded, same as
        get_node_at, so a just-emptied node disappears immediately rather
        than lingering as a picked-clean sprite."""
        result = []
        for node in self.active_nodes:
            if node.gathered:
                continue
            data = self.materials.get(node.material_id)
            if data is None:
                continue
            result.append((node.x, node.y, data["material_type"], data.get("icon_id")))
        return result


_gathering_node_manager = None


#: material_type -> actual asset folder name under assets/gathering_nodes/.#: NOT a blind "+s" pluralization - "ore" stays singular (its folder is
#: assets/gathering_nodes/ore/, not "ores"), while "herb" does pluralize
#: to "herbs". A naive f"{material_type}s" template silently broke ore
#: icons everywhere (tilemap_renderer.py AND inventory_screen.py both
#: had the same bug, caught via a real rendered screenshot showing ore
#: falling back to overflowing text instead of its sprite - herbs
#: happened to work by coincidence since "herb"+"s" is actually correct).
#: Single source of truth here so both renderers stay in sync, and so
#: future material_types (wood, hide, essence, ...) only need one entry
#: added instead of two matching guesses.
MATERIAL_TYPE_FOLDERS = {
    "ore": "ore",
    "herb": "herbs",
    "bar": "bars",
    # No real sprite art exists for upgrade kits yet (Oct 2026,
    # Blacksmithing's upgrade_kit_copper/upgrade_kit_bronze) - mapped here
    # anyway so the lookup has a defined destination the moment art is
    # added, rather than silently falling back to "upgrade_kit" as a
    # folder name (the .get() fallback elsewhere in this codebase doesn't
    # crash on a missing folder, but a real entry here is one less thing
    # to remember to add later).
    "upgrade_kit": "upgrade_kits",
    # Woodcutting (Oct 2026) - real art already exists on disk at
    # assets/gathering_nodes/wood/ (all 40 named woods from Kyle's
    # reference chart, staged ahead of the data - only the 4 Early Woods
    # are wired as real materials.json entries so far). Folder is
    # singular "wood" on disk, matching "ore" staying singular rather
    # than the "herb"->"herbs" pluralization.
    "wood": "wood",
    # Crafting intermediates (Oct 2026). Art for these is still to come (prompts: claude/crafting_art_prompts.md);
    # until a PNG exists the UI falls back to the usual text/rarity box.
    "plank": "planks",
    "fiber": "fibers",
    "pages": "pages",
    "cloth": "cloth",
    "leather": "leather",  # 40-tier ladder art staged (Skinning not built yet)
    # BOLTS LIVE IN THE CLOTH FOLDER. All 40 bolt icons were drawn and staged alongside the cloth
    # they come from - assets/gathering_nodes/cloth holds 80 files, cloth_* and bolt_* - but this
    # pointed at a "bolts" directory that has never existed, so every bolt in the game rendered as
    # a text box while its art sat on disk. Found 2026-10-28 by diffing every material's icon path
    # against the files actually present.
    "bolt": "cloth",
    # Essence Harvesting (Oct 2026) - the Frontier-original gathering
    # profession feeding Engineering. "essence" drops off slain elementals
    # (entities/essence_drops.py); "crystal" comes out of world nodes and so
    # is the first NEW node type since wood - it renders on the ground through
    # this same mapping, which is why the entry matters here and not only in
    # the bag. No art yet for either; the UI falls back to its text box until
    # there is.
    "essence": "essences",
    "crystal": "crystals",
    # Crafting reagents bought from vendors rather than gathered (thread,
    # vials, flux, ...). They never appear as a world node, but they do show
    # in the bag and on vendor rows, both of which route through here.
    "reagent": "reagents",
    # These three had no entry at all, so the .get() fallback used the bare material_type as the
    # folder name - "part", "meat", "kit" - which does not match the plural convention every other
    # entry here follows. Named explicitly now, with art installed from Kyle's icon pack
    # (tools/install_icon_pack.py).
    "part": "parts",
    "meat": "meat",
    "kit": "kits",
}

#: Skill cap per profession TIER, not an absolute profession cap - "early"
#: is the only tier that exists right now (see materials.json), so this
#: is effectively the current hard cap on herbalism/mining until Mid tier
#: materials and their own skill_range values are authored. Matches
#: WoW's real 1-75 bracket for a profession's first tier. When Mid tier
#: is added later, a character's cap becomes early_cap + mid_cap, same
#: incremental-tier-cap pattern WoW itself uses (75 -> 150 -> 225 -> 300).
TIER_SKILL_CAPS = {
    "early": 75,
    "mid": 150,
}

#: cave_name -> parent overworld zone name, for the caves that should get
#: an ore-only node pool (Kyle, 2026-09-12: "caves (and keeps) are fine,
#: just not dungeons"). Sourced directly from zone_generator.py's
#: cave_specs list. The canonical Dungeon list (which never gets ore, no
#: exceptions) lives in world/zone_classification.py - see that module
#: for why it exists as its own file and the full confirmed list.
#: "Sunken Temple Grotto" here (a cave_specs entry, under Echo Isles) is
#: NOT the same zone as "Sunken Grotto of the Deep" (a real Dungeon, on
#: the zone_classification.py list) - easy to conflate by name, worth
#: flagging explicitly since it's the kind of mix-up that silently sends
#: gathering nodes into a lore dungeon if it's ever gotten wrong.
#: Only the caves whose PARENT zone already has a node_pools.json entry
#: are listed - a cave under Ashenvale/Deathknell/Eastern Tirisfal has
#: nothing to inherit an ore table FROM yet, so it's left out rather than
#: guessed at, same reasoning node_pools.json's zones list stays small.
CAVE_TO_PARENT_ZONE = {
    "The Den": "Valley of Trials",
    "Burning Blade Coven": "Valley of Trials",
    "Skull Rock": "Durotar",
    "Tiragarde Keep": "Durotar",
    "Dustwind Cave": "Durotar",
    "Sunken Temple Grotto": "Echo Isles",
    "Zalazane's Hollow": "Echo Isles",
    "Night Web's Hollow": "Deathknell",
    "Scarlet Crypt": "Deathknell",
    "Scourge Cave": "Eastern Tirisfal",
    # A silver mine that flooded. It inherits Western Hillsbrad's ore table, which carries ore_silver at
    # weight 2 precisely because this mine is the reason that silver is in the zone at all.
    "Azurelode Mine": "Western Hillsbrad",
    # A dwarf hold cut into the ridge - not a Dungeon, so it keeps ore, which is the whole reason dwarves
    # dug there. Inherits Eastern Hillsbrad's table (iron-heavy, with coal and a little silver).
    "Dun Garok": "Eastern Hillsbrad",
    # A Venture Co. MINING CLAIM that shipped with no ore in it - found while auditing every cave for
    # gathering after Hillsbrad went in. The other caves missing from this map are correctly missing:
    # Moonwell Hollow, Howling Barrows and Serena's Hollow are a flooded moonwell, a long barrow and a
    # harpy roost, and the synthesized cave pool is ore-only by design ("caves are mining spots, not
    # foraging spots"), so giving them an inherited ore table would be worse than leaving them bare.
    "Boulder Lode Mine": "Northern Barrens",
    # The ice chambers were meant to carry Frostpine, but a synthesized cave pool is ore-only by design
    # ("caves are mining spots, not foraging spots"), so the Descent gets Eastern Hillsbrad's iron and
    # silver and the wood idea moves to the Underdark proper, which is a zone rather than a cave.
    "The Frostward Descent": "Eastern Hillsbrad",
    "The Hollow Geode": "The Crystalline Underdark",
    # A silithid hive dug through a salt pan - ore is exactly what is down there, and the Flats'
    # own quests are built on the tunnelers bringing spoil UP and leaving it. Two mouths, one
    # cave; the parent key is the same either way, so both entrances inherit the same table.
    "The Undercrust": "The Shimmering Flats",
    # A sea cave the pirates took off whoever was salvaging it - and whoever that was, they were
    # down there for the rock. Inherits Northern Tanaris's table ore-only, which means it is also
    # the first place in the game a player can mine mithril underground.
    "The Drownbell": "Northern Tanaris",
    # Stranglethorn's three caves, each under its own zone. All three inherit a parent table that stops
    # at the existing tier-40 ladder, so nothing new enters the material ladder here - Southern
    # Stranglethorn runs to 42 and still gathers exactly what the 38-40 band gathers. The Gurbashi
    # Arena is deliberately absent: it is on the zone_classification.py Dungeon list, and dungeons
    # never get nodes.
    "Rotvine Hollow": "Northern Stranglethorn",
    "Veilfall Cave": "Central Stranglethorn",
    "The Drowned Shrine": "Southern Stranglethorn",
}

#: How much more ore-dense a cave's inherited pool is versus its parent
#: zone's own ore ratio - Kyle: "maybe 10-15% more ore" concentrated
#: underground. Applied as a flat multiplier on ore weights only (herb
#: weights are dropped entirely - caves are mining spots, not foraging
#: spots), then renormalized so heavier ore weighting doesn't just mean
#: "more total nodes", it means "of the nodes that spawn, more are ore
#: relative to each other" - which for an ore-only pool is really just
#: "keep the same relative ore-to-ore ratios the parent zone already had".
#: The multiplier still matters once a cave has any non-ore materials in
#: a future tier (e.g. Essence Harvesting nodes sharing cave space).
CAVE_ORE_DENSITY_MULT = 1.125  # midpoint of Kyle's 10-15% range


def get_gathering_node_manager():
    """Module-level singleton, same access pattern as
    world.ambient_npc_manager.get_ambient_npc_manager() /
    world.vendor_manager.get_vendor_manager()."""
    global _gathering_node_manager
    if _gathering_node_manager is None:
        _gathering_node_manager = GatheringNodeManager()
    return _gathering_node_manager
