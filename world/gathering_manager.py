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
        #: Fishing spots only: the pool sprite to draw and the WATER tile to draw it on (the node
        #: itself is on the shore). None for every other node, and for a spot with no pool art.
        self.pool = None
        self.pool_tile = None
        #: How many fish have come out of this pool so far (see GatheringNodeManager.POOL_STAYS).
        self.catches = 0

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
            with open(materials_file, 'r', encoding="utf-8") as f:
                self.materials = json.load(f).get("materials", {})

        pools_file = data_dir / "node_pools.json"
        if pools_file.exists():
            with open(pools_file, 'r', encoding="utf-8") as f:
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
        self._populate_fishing(tilemap, zone_name, pool.get("fishing"))
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
        candidates = self._roll_candidate_tiles(tilemap, slots,
                                                avoid=self._settlement_test(tilemap, zone_name))
        chosen = candidates[:num_active]

        material_ids = list(table.keys())
        weights = list(table.values())

        for (x, y) in chosen:
            material_id = random.choices(material_ids, weights=weights, k=1)[0]
            self.active_nodes.append(GatheringNode(x, y, material_id))
            tilemap.set_tile(x, y, "gathering_node", "interaction")

    def _populate_fishing(self, tilemap, zone_name, fishing):
        """Fishing spots: nodes on walkable tiles beside water, rolled from the zone's own
        "fishing" pool (tools/build_fishing.py). You fish by stepping on one, like any node."""
        if not fishing or not fishing.get("table"):
            return
        avoid = self._settlement_test(tilemap, zone_name)
        spots = [t for t in shore_tiles(tilemap)
                 if tilemap.get_tile(t[0], t[1], "interaction") is None and not (avoid and avoid(*t))]
        random.shuffle(spots)
        want = max(1, round(fishing.get("slots", 0) * fishing.get("active_percent", 0.0)))
        ids, weights = list(fishing["table"].keys()), list(fishing["table"].values())
        self._fishing_table = (ids, weights)
        from world.fishing_pools import pools_for
        pool_names = pools_for(self._zone_key(zone_name))
        placed = []
        for (x, y) in spots:
            if len(placed) >= want:
                break
            if any(abs(x - px) + abs(y - py) < 6 for px, py in placed):      # spread along the shore
                continue
            placed.append((x, y))
            node = GatheringNode(x, y, random.choices(ids, weights=weights, k=1)[0])
            node.pool_tile = _water_beside(tilemap, x, y)
            if pool_names:
                node.pool = random.choice(pool_names)
            self.active_nodes.append(node)
            tilemap.set_tile(x, y, "gathering_node", "interaction")

    #: Two nodes are never closer than this many tiles on either axis.
    NODE_SPACING = 3

    #: A node keeps this far from any single NPC, and this far from a cluster of them.
    NPC_CLEARANCE = 3
    SETTLEMENT_RADIUS = 9
    SETTLEMENT_NPCS = 3

    def _settlement_test(self, tilemap, zone_name):
        """Returns avoid(x, y): True where a gathering node must NOT spawn.

        Kyle, 10 Nov: "gatherables shouldn't spawn in towns."

        A town that is its own map is already covered (tilemap.is_town, above). But most
        settlements are not their own map - Camp Taurajo, the Crossroads, a quest camp - they
        are a cluster of NPCs inside an open zone, and nothing told the node roller they were
        there, so ore and herbs came up between the vendors.

        No list of settlement rectangles exists and one would rot, so this reads the
        settlement off the thing that makes it one: PEOPLE. A tile is off-limits if it is
          - within NPC_CLEARANCE of any NPC (nobody stands on a copper vein), or
          - within SETTLEMENT_RADIUS of SETTLEMENT_NPCS or more (that is a camp), or
          - inside a subzone flagged "safe" in encounters.json (a declared settlement).
        A lone quest giver in the wilderness therefore only clears the ground at their feet.
        """
        npcs = []
        layer = getattr(tilemap, "interaction_layer", None) or []
        for y, row in enumerate(layer):
            for x, kind in enumerate(row):
                if kind == "npc":
                    npcs.append((x, y))

        safe_keys = set()
        try:
            path = Path(__file__).parent.parent / "data" / "creatures" / "encounters.json"
            declared = json.loads(path.read_text(encoding="utf-8")).get("zones", {}).get(zone_name, {})
            safe_keys = {key for key, sz in declared.get("subzones", {}).items()
                         if isinstance(sz, dict) and sz.get("safe")}
        except (OSError, ValueError):
            pass

        near, wide, need = self.NPC_CLEARANCE, self.SETTLEMENT_RADIUS, self.SETTLEMENT_NPCS

        def avoid(x, y):
            crowd = 0
            for (nx, ny) in npcs:
                d = max(abs(nx - x), abs(ny - y))
                if d <= near:
                    return True
                if d <= wide:
                    crowd += 1
                    if crowd >= need:
                        return True
            if safe_keys:
                sz = tilemap.get_subzone_at(x, y)
                if sz and sz.get("table_key") in safe_keys:
                    return True
            return False

        return avoid

    def _roll_candidate_tiles(self, tilemap, count, max_attempts=500, avoid=None):
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
            if avoid is not None and avoid(x, y):
                continue
            # NOT SHOULDER TO SHOULDER. A node is drawn a tile and a half wide, so two on
            # neighbouring tiles overlap and the one drawn second leaves a sliver of the first
            # showing beside it. Kyle, 13 Nov 2026, twice: "why are we having so many issues
            # cropping gatherables?" / "there it is again bro! why!?!?!" - it was never the crop.
            if any(abs(x - fx) < self.NODE_SPACING and abs(y - fy) < self.NODE_SPACING
                   for (fx, fy) in found):
                continue
            # ...AND NOT BESIDE A FISHING SPOT. Those are placed first, by _populate_fishing, and
            # this roll only knew about its own picks - so an ore vein could land diagonal to a
            # pool on the shore, which is the same overlap by another door. Found 13 Nov when a
            # new zone shifted the random stream and Southern Stranglethorn rolled one.
            if any(abs(x - n.x) < self.NODE_SPACING and abs(y - n.y) < self.NODE_SPACING
                   for n in self.active_nodes):
                continue
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

    #: How near a fishing pool you must stand to cast into it, in tiles (Chebyshev), measured to
    #: the spot on the bank OR to the pool on the water. Kyle, 13 Nov: "We need to find a way to
    #: fish other than clicking in the water" - it used to be one exact, unmarked bank tile.
    FISHING_REACH = 2
    #: ...and how far you can cast: tiles from where you stand to the POOL. Kyle, 13 Nov: "The
    #: ability to fish from a distance allows pools to be in deeper water."
    CAST_RANGE = 5
    #: A pool sits up to this many tiles out from the bank.
    POOL_MAX_OUT = 4
    #: The chance a pool is still there after its 1st, 2nd and 3rd fish. Kyle, 13 Nov: "100% for
    #: 1 fish, then a 66% chance it sticks around for a 2nd fish. Then 33% it sticks around for a
    #: 3rd fish. Then 10% it sticks around for a 4th fish." Nothing after the fourth.
    POOL_STAYS = (0.66, 0.33, 0.10)

    def fishing_node_near(self, x, y):
        """The nearest unfished pool you can cast into from (x, y), or None."""
        best, best_d = None, None
        for node in self.active_nodes:
            if node.gathered or not node.pool_tile:
                continue
            to_bank = max(abs(node.x - x), abs(node.y - y))
            to_pool = max(abs(node.pool_tile[0] - x), abs(node.pool_tile[1] - y))
            if to_bank > self.FISHING_REACH and to_pool > self.CAST_RANGE:
                continue
            if best_d is None or to_pool < best_d:
                best, best_d = node, to_pool
        return best

    def gather(self, node, tilemap):
        """Mark a node gathered, clear its interaction tile, and return
        the material_id it dropped. Returns None if the node was already
        gathered (double-interact guard) - callers shouldn't rely on this
        for validation, get_node_at already excludes gathered nodes, but
        it's cheap insurance against a stale reference.
        """
        if node.gathered:
            return None
        caught = node.material_id
        if node.pool_tile:
            # A FISHING POOL MAY HOLD MORE THAN ONE FISH (POOL_STAYS). If it stays, the next fish
            # is rolled fresh from the zone's table, so a pool is not four of the same catch.
            node.catches += 1
            k = node.catches - 1
            if k < len(self.POOL_STAYS) and random.random() < self.POOL_STAYS[k]:
                table = getattr(self, "_fishing_table", None)
                if table:
                    node.material_id = random.choices(table[0], weights=table[1], k=1)[0]
                return caught
        node.gathered = True
        tilemap.set_tile(node.x, node.y, None, "interaction")
        return caught

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

    #: Chance that an ore vein also yields a crystal, and which crystal each ore
    #: TIER produces. Kyle, 2026-10-31: "Crystals can be found in ore veins."
    #:
    #: Crystals used to be their own node type under Essence Harvesting, which is
    #: now deleted. Rather than invent a second node that competes with ore for
    #: spawn points, a vein simply sometimes has a crystal in it - which is also
    #: how it works in the ground. Engineering is the only consumer and its ladder
    #: is tier-gated, so an early vein must never hand out a mid crystal: a level
    #: 12 miner cracking a copper vein should not be able to build a void regulator.
    CRYSTAL_FROM_VEIN = {
        "early":   ["crystal_quartz", "crystal_azure"],
        "mid":     ["crystal_emberglass", "crystal_tideglass", "crystal_voidglass"],
        "late":    ["crystal_emberglass", "crystal_voidglass"],
        "endgame": ["crystal_voidglass"],
    }
    CRYSTAL_FROM_VEIN_CHANCE = 0.18

    #: Crystals that come from ONE specific ore rather than from a whole tier,
    #: checked before CRYSTAL_FROM_VEIN and at their own rate.
    #:
    #: Kyle, 7 Nov 2026, on Arcane Crystal: "the crystal has a chance from
    #: thorium." Not from any endgame vein - from Thorium, which is how Classic
    #: does it (Arcane Crystal is a rare extra out of Rich Thorium) and why
    #: Arcanite is worth what it is. A tier entry would have handed it out of
    #: Elementium too.
    #:
    #: The rate is deliberately far below CRYSTAL_FROM_VEIN_CHANCE. Arcane
    #: Crystal is the gate on Arcanite Bar, which is the gate on the terminal
    #: blacksmithing plans, so it is the scarcest link in the traditional
    #: crafting chain and it should feel like it.
    CRYSTAL_FROM_MATERIAL = {
        "ore_thorium": ("crystal_arcane", 0.07),
    }

    def roll_material_crystal(self, material_id, rng=None):
        """-> a crystal this SPECIFIC ore sometimes yields, or None.

        Separate from roll_vein_crystal's tier table because the two answer
        different questions, and rolled first: a Thorium vein that produces an
        Arcane Crystal has already produced its crystal and does not also roll
        the endgame tier pool.
        """
        import random as _r
        rng = rng or _r
        entry = self.CRYSTAL_FROM_MATERIAL.get(material_id)
        if not entry:
            return None
        crystal, chance = entry
        return crystal if rng.random() < chance else None

    def roll_vein_crystal(self, material_id, rng=None):
        """-> a crystal material_id this ore vein also yielded, or None.

        Only ore yields crystals; herbs, wood, cloth and the rest return None, so
        this is safe to call on every gather rather than at one ore-only call site
        (one rule, one implementation - the thing this codebase keeps getting wrong
        is having two).
        """
        import random as _r
        rng = rng or _r
        data = self.materials.get(material_id) or {}
        if data.get("material_type") != "ore":
            return None
        # A per-material crystal wins and ends the roll - see
        # roll_material_crystal. Called from in here rather than beside it so
        # that every existing caller of roll_vein_crystal picks this up without
        # being changed: one rule, one implementation, which is the thing this
        # codebase keeps getting wrong.
        specific = self.roll_material_crystal(material_id, rng=rng)
        if specific:
            return specific
        pool = self.CRYSTAL_FROM_VEIN.get(data.get("tier"))
        if not pool:
            return None
        if rng.random() >= self.CRYSTAL_FROM_VEIN_CHANCE:
            return None
        return rng.choice(pool)

    def gem_table(self):
        """{ore id: [(gem id, chance), ...]} from data/gathering/gem_drops.json, read once."""
        table = getattr(self, "_gem_table", None)
        if table is None:
            import json as _json
            path = Path(__file__).parent.parent / "data" / "gathering" / "gem_drops.json"
            try:
                raw = _json.loads(path.read_text(encoding="utf-8")).get("drops", {})
            except (OSError, ValueError):
                raw = {}
            table = {ore: [(g, float(c)) for g, c in rows] for ore, rows in raw.items()}
            self._gem_table = table
        return table

    def roll_vein_gem(self, material_id, rng=None):
        """-> a gemstone this ore vein also gave up, or None.

        Kyle, 12 Nov: "Start adding gemstones and crystals to ore (think of wow!)". Every ore
        has gems of its own - Malachite and Tigerseye in copper, Star Ruby in mithril - each at
        a few percent a swing. Rolled separately from the crafting crystals (roll_vein_crystal),
        so a vein can give both; but one gem at most, the first that comes up.
        """
        import random as _r
        rng = rng or _r
        for gem_id, chance in self.gem_table().get(material_id, ()):
            if gem_id in self.materials and rng.random() < chance:
                return gem_id
        return None

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
            if node.pool and node.pool_tile:
                # A fishing spot is drawn as a pool ON THE WATER beside it, not as a fish on the bank.
                result.append((node.pool_tile[0], node.pool_tile[1], "fishing_pool", node.pool))
            else:
                result.append((node.x, node.y, data["material_type"], data.get("icon_id")))
        return result


WATER_TILES = ("shallow_water", "deep_water")


def _water_beside(tilemap, x, y):
    """The water tile next to a shore tile that is furthest out: the neighbour with the most water
    round it, so the pool sits in the water and not half on the bank. None if there is none."""
    base = getattr(tilemap, "base_layer", None)
    if base is None:
        return None
    best, best_n = None, -1
    for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1)):
        wx, wy = x + dx, y + dy
        if not (0 <= wx < tilemap.width and 0 <= wy < tilemap.height) or base[wy][wx] not in WATER_TILES:
            continue
        n = sum(1 for ax in (-1, 0, 1) for ay in (-1, 0, 1)
                if 0 <= wx + ax < tilemap.width and 0 <= wy + ay < tilemap.height
                and base[wy + ay][wx + ax] in WATER_TILES)
        if n > best_n:
            best, best_n, step = (wx, wy), n, (dx, dy)
    if best is not None:
        # OUT INTO THE WATER, up to POOL_MAX_OUT tiles from the bank. You cast to a pool, you do
        # not stand on it, so it can sit in deep water; and a pool is three tiles across, so one
        # drawn hard against the bank covers whoever is standing there to fish it. It stops one
        # tile short of the far side of a narrow river.
        want = random.randint(2, GatheringNodeManager.POOL_MAX_OUT)
        for _ in range(want - 1):
            fx, fy = best[0] + step[0], best[1] + step[1]
            gx, gy = fx + step[0], fy + step[1]
            if not (0 <= gx < tilemap.width and 0 <= gy < tilemap.height):
                break
            if base[fy][fx] not in WATER_TILES or base[gy][gx] not in WATER_TILES:
                break
            best = (fx, fy)
    return best


def shore_tiles(tilemap):
    """Walkable tiles with water on at least one side - where a line can be cast."""
    base = getattr(tilemap, "base_layer", None)
    if base is None:
        return []
    out = []
    w, h = tilemap.width, tilemap.height
    for y in range(1, h - 1):
        row = base[y]
        for x in range(1, w - 1):
            if row[x] in WATER_TILES or not tilemap.is_walkable(x, y):
                continue
            if (base[y][x - 1] in WATER_TILES or base[y][x + 1] in WATER_TILES
                    or base[y - 1][x] in WATER_TILES or base[y + 1][x] in WATER_TILES):
                out.append((x, y))
    return out


_gathering_node_manager = None


#: material_type -> actual asset folder name under assets/gathering_nodes/.#: NOT a blind "+s" pluralization - "ore" stays singular (its folder is
#: assets/gathering_nodes/ore/, not "ores"), while "herb" does pluralize
#: to "herbs". A naive f"{material_type}s" template silently broke ore
#: icons everywhere (tilemap_renderer.py AND inventory_screen.py both
#: had the same bug, caught via a real rendered screenshot showing ore
#: falling back to overflowing text instead of its sprite - herbs
#: happened to work by coincidence since "herb"+"s" is actually correct).
#: Single source of truth here so both renderers stay in sync, and so
#: future material_types (wood, hide, ...) only need one entry
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
    "fish": "fish",
    # Crafting intermediates (Oct 2026). Art for these is still to come (prompts: claude/crafting_art_prompts.md);
    # until a PNG exists the UI falls back to the usual text/rarity box.
    "plank": "planks",
    "fiber": "fibers",
    "pages": "pages",
    # Shafts - the third branch off a plank, beside fiber and pages. Kyle,
    # 7 Nov 2026: "Planks can turn into sticks, fiber, or pages." Listed
    # explicitly because the .get() fallback below uses the bare material_type
    # as the folder name, which would look in sticks/ for "stick" and find
    # nothing - the same silent miss that left part/meat/kit unresolved.
    "stick": "sticks",
    "cloth": "cloth",
    "leather": "leather",  # 40-tier ladder art staged (Skinning not built yet)
    # BOLTS LIVE IN THE CLOTH FOLDER. All 40 bolt icons were drawn and staged alongside the cloth
    # they come from - assets/gathering_nodes/cloth holds 80 files, cloth_* and bolt_* - but this
    # pointed at a "bolts" directory that has never existed, so every bolt in the game rendered as
    # a text box while its art sat on disk. Found 2026-10-28 by diffing every material's icon path
    # against the files actually present.
    "bolt": "cloth",
    # Crystals. Kyle, 2026-10-31: "Crystals can be found in ore veins." These
    # were the world-node half of the deleted Essence Harvesting profession;
    # the elemental-drop half (the ten essence_* motes) is gone outright and
    # the crystals moved to MINING, which is where a thing you pry out of rock
    # belongs anyway. They come out of ore veins as a bonus roll rather than
    # spawning their own node type - see CRYSTAL_FROM_VEIN below. No art yet;
    # the UI falls back to its text box until there is.
    "crystal": "crystals",
    # Gemstones, out of ore veins (tools/build_gems.py). Art goes in
    # assets/gathering_nodes/gems/<icon_id>.png; until it lands the UI uses its text box.
    "gem": "gems",
    # Cut gems (tools/build_jewelcrafting.py) draw the stone they were cut from.
    "cut_gem": "gems",
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

#: CUMULATIVE skill cap for a material of each tier - the skill a character
#: may reach by working that tier, not an increment to be added to the others.
#: These deliberately mirror Character.PROFESSION_TIER_CAPS (the trainer
#: ladder: Apprentice 75, Journeyman 150, Expert 225, Artisan 300) because
#: they answer the same question, and when the two disagreed the answer
#: depended on which bar you happened to smelt.
#:
#: ALL FOUR TIERS ARE LISTED, which matters more than it looks. A tier missing
#: from this dict reads back as None, and smelting_manager treated None as
#: "no cap", so a character smelting a `late` bar ran to the trainer cap while
#: one smelting a `mid` bar stopped at 225. Keep every tier that appears in
#: materials.json here, or the cap silently depends on the material.
#:
#: Kyle, 7 Nov 2026, re-anchoring the ore ladder to WoW's real values
#: ("Mithril shouldn't be skill 80"): Thorium sits at 245 and Elementium at
#: 300, both above the old 225, so an `endgame` entry is required for them to
#: be reachable at all.
TIER_SKILL_CAPS = {
    "early": 75,
    "mid": 150,
    "late": 225,
    "endgame": 300,
    "kit": 300,
    "starter": 75,
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
    # The void under the Sands: the Sands' table, ore-only like every cave.
    "The Dry Deep": "The Abyssal Sands",
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
