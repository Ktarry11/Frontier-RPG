#!/usr/bin/env python3
"""Accept, finish and hand in every quest in the game, through the real engine.

WHY THIS EXISTS. Every quest check in this repo before today was an
INSPECTION: read data/quests/*.json, read the engine, decide whether they
agree. Those checks pass on quests that cannot be finished in play, for the
same reason tools/audit_pet_combat.py had to exist - what a quest DOES is
decided by QuestManager.record_kill / record_zone_entered /
record_position_reached / refresh_gather_progress / turn_in_quest and by the
zone key the overworld happens to pass them, not by whether the JSON is
well-formed. Four quests in Ashenvale were shipped with `"target": null` on
an EXPLORE objective and the place name parked in `zone`, where nothing
reads it; two in the Sepulcher name the zone "sepulcher" while the live map
is called "The Sepulcher" and the overworld passes "the_sepulcher". All six
load without a warning, accept without a warning, and can never be turned
in. No amount of schema checking sees that. Playing them does.

So this plays them:

  PHASE 1  RESOLVE   - every objective against what the game can actually
                       produce: creatures.json for existence, the real
                       encounter tables + the live tilemaps' pinned spawns
                       for spawnability, quest_drops.json for item sources,
                       the NPC rosters for givers and collectors, the zone
                       list for explore targets, the smelting/profession
                       recipe tables for CRAFT.
  PHASE 2  REWARDS   - build every reward through world.quest's own
                       build_unique_reward_set and try to EQUIP the result
                       on a real Character, because an item with a slot the
                       Equipment has no pocket for is built, awarded, and
                       then silently goes nowhere.
  PHASE 3  CHAINS    - walk next_quest_id / requires_quests, and mark every
                       quest sitting behind something Phase 4 could not
                       finish as transitively unreachable.
  PHASE 4  PLAY      - one real Character + Party + QuestManager. In
                       dependency order: accept_quest, satisfy each
                       objective through the engine's own progress hooks,
                       then turn_in_quest. A quest that does not reach
                       COMPLETED here cannot be completed in the game.
  PHASE 5  LEVELS    - is there a continuous ladder of accept-able quests
                       from 1 to 60, and which level bands have nothing.
  PHASE 6  RULES     - the project's standing content rules: no escort
                       quests, no quests built around rares, nothing from
                       Earth in the world yet, the Integration was three
                       years ago, and no stat-sheet numbers in the prose.

    python3 tools/audit_quests.py
    python3 tools/audit_quests.py --quest sep_keep_tour
    python3 tools/audit_quests.py --no-zones      # faster, less accurate
    python3 tools/audit_quests.py --counts        # full prose-count list

HOW THIS TOOL HAS BEEN WRONG, written down so the next reader distrusts the
instrument before the engine (eleven audits in this repo have "found" bugs
that were really a misread key):

  * The first spawnability pass called every is_boss creature in a subzone
    table a "rare" and reported 124 quests as violating the no-rares rule.
    They are not rares in any sense the engine has: CreatureManager carries
    QUEST_RARE_SPAWN_CHANCE and a `wanted_rares` branch that exists
    SPECIFICALLY so a named subzone boss a quest wants turns up at 25%
    instead of 6%. The engine was built for those quests. See
    classify_boss_reachability.
  * The second pass reported the three Frostward Descent bosses as
    unspawnable because they sit at weight 0 in an `open_zone` table. They
    are pinned in that zone's live boss_positions, which only the built
    tilemaps know. That is why --no-zones is not the default.
  * A prose-vs-count check that merely looked for numbers reported 98
    quests; almost all of them were "three weeks", "eleven nights" and
    other prose that has nothing to do with an objective. The check that
    survived requires the number to sit within two words of the
    objective's own target noun.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

QUEST_DIR = ROOT / "data" / "quests"

#: Objective types whose target is an inventory item counted out of the bag.
ITEM_TYPES = {"gather", "fetch", "deliver"}
#: Objective types whose target is a creature name.
KILL_TYPES = {"kill", "kill_boss"}


def slug(s):
    """The zone key the overworld actually passes the quest system.

    ZoneManager.transition_to_zone and ui/screens/combat_screen.py both
    build it the same way - `current_zone.name.lower().replace(" ", "_")
    .replace("'", "")` - and crucially they do NOT strip a leading "The".
    ZoneManager._normalize_zone_key DOES strip it, for NPC placement, and
    that difference is the whole of the Sepulcher bug: a quest authored
    against the NPC-side spelling ("sepulcher") never matches the
    combat/transition-side spelling ("the_sepulcher"). Matching this
    function to the hooks' spelling rather than to the prettier one is the
    point of this tool.
    """
    return str(s).lower().replace(" ", "_").replace("'", "")


# ---------------------------------------------------------------------------
# data loading
# ---------------------------------------------------------------------------


def load_json(rel):
    with open(ROOT / rel, encoding="utf-8") as fh:
        return json.load(fh)


def raw_quests():
    """Every quest as authored, with its file - the audit needs the file name
    for every finding so a fix has somewhere to go, and QuestManager throws
    that away when it indexes by quest_id."""
    out = []
    for path in sorted(QUEST_DIR.glob("*.json")):
        data = load_json(path.relative_to(ROOT))
        qs = data.get("quests", [])
        for q in (qs if isinstance(qs, list) else list(qs.values())):
            out.append((path.name, q))
    return out


def text_overlays():
    """data/quests/text/*.json, the rewrite layer QuestManager applies over
    the generated zone files. Any prose check that reads the zone file alone
    is reading text the player never sees."""
    overlay = {}
    for path in sorted((QUEST_DIR / "text").glob("*.json")):
        for qid, fields in load_json(path.relative_to(ROOT)).items():
            if isinstance(fields, dict):
                overlay[qid] = fields
    return overlay


def quest_prose(q, overlay):
    ov = overlay.get(q["quest_id"], {})
    return {k: str(ov.get(k) or q.get(k) or "")
            for k in ("title", "description", "accept_text", "turn_in_text")}


# ---------------------------------------------------------------------------
# world model: what the game can actually produce
# ---------------------------------------------------------------------------


class World:
    """Everything the audit needs to answer "does this exist, and can a
    player get at it" - assembled from the same files the game spawns from,
    never from a hand-maintained list in this tool."""

    def __init__(self, use_zones=True):
        self.creatures = load_json("data/creatures/creatures.json")["creatures"]
        self.encounters = load_json("data/creatures/encounters.json")
        self.quest_drops = load_json("data/creatures/quest_drops.json")["drops"]
        # Gathering nodes are the other way an item legitimately reaches a bag - see item_sources.
        self.gather_pools = load_json("data/gathering/node_pools.json")["zones"]

        self.ambient = {n["npc_id"] for n in
                        load_json("data/npcs/ambient_npcs.json")["npcs"]}
        self.vendors = {v["vendor_id"] for v in
                        load_json("data/npcs/vendors.json")["vendors"]}
        recruits = load_json("data/npcs/recruits.json")
        rl = recruits if isinstance(recruits, list) else recruits.get("recruits", [])
        self.recruits = {r.get("recruit_id") for r in rl} if isinstance(rl, list) else set(rl)

        self.slots = set(load_json("data/items/slots.json")["slots"])
        self.weapon_types = set(load_json("data/items/weapon_types.json")["weapon_types"])
        at = load_json("data/items/armor_types.json")
        self.armor_types = set(at.get("armor_types", at))
        self.rarities = set(load_json("data/items/rarity.json")["rarity_tiers"])

        # placement[creature] = {(kind, where, weight)} straight out of the
        # encounter tables, and reach[zone_key] = {creature} for "could I
        # fight this while standing on that map". Both are needed: the first
        # answers "is it placed anywhere at all", the second answers the
        # zone-restricted KILL question, and they disagree for caves (a cave
        # is its own map, so its creatures are NOT reachable from the parent
        # zone's key even though the data nests them under it).
        self.placement = defaultdict(set)
        self.reach = defaultdict(set)
        self._index_encounters()

        self.zones = {}
        self.pinned = defaultdict(set)
        if use_zones:
            self._index_live_zones()

    # -- encounter tables ---------------------------------------------------

    def _index_encounters(self):
        for zname, zdata in self.encounters.get("zones", {}).items():
            zkey = slug(zname)
            for name, w in (zdata.get("open_zone") or {}).get("creatures", {}).items():
                self.placement[name].add(("open_zone", zname, w))
                self.reach[zkey].add(name)
            for sname, sub in (zdata.get("subzones") or {}).items():
                for name, w in (sub.get("creatures") or {}).items():
                    self.placement[name].add(("subzone", f"{zname}/{sname}", w))
                    # A subzone is a rectangle inside the parent map, not a
                    # map of its own - so a kill there reports the PARENT
                    # zone's key to record_kill.
                    self.reach[zkey].add(name)
            for cname, cave in (zdata.get("caves") or {}).items():
                for name, w in (cave.get("creatures") or {}).items():
                    self.placement[name].add(("cave", f"{zname}/{cname}", w))
                    # A cave IS its own map, so combat reports the cave's
                    # name, not the parent's. Collapsing these two cases is
                    # how a zone-restricted kill quest gets cleared by an
                    # audit and still never advances in play.
                    self.reach[slug(cname)].add(name)

        def walk(node, path):
            if not isinstance(node, dict):
                return
            creatures = node.get("creatures")
            if isinstance(creatures, dict):
                for name, w in creatures.items():
                    self.placement[name].add(("dungeon", "/".join(path), w))
                    self.reach[slug(path[0])].add(name)
            for key, val in node.items():
                if key != "creatures":
                    walk(val, path + [key])

        for top, val in self.encounters.items():
            if top != "zones":
                walk(val, [top])

    # -- live tilemaps ------------------------------------------------------

    def _index_live_zones(self):
        """Pinned spawns and walkability, from the zones the game builds.

        This costs about a minute of tilemap generation and it is not
        optional for correctness: three Frostward Descent bosses sit at
        weight 0 in an `open_zone` table, which the encounter tables alone
        make look unspawnable, and are in fact pinned in that zone's
        boss_positions. Without this pass the audit accuses three
        working quests.
        """
        import os
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        from world.zone_manager import ZoneManager

        zm = ZoneManager()
        for name, data in zm.zones.items():
            tilemap = data["tilemap"]
            self.zones[slug(name)] = tilemap
            bosses = list(getattr(tilemap, "boss_positions", None) or [])
            single = getattr(tilemap, "boss_position", None)
            if single and len(single) >= 3:
                bosses.append(single)
            for entry in bosses:
                if len(entry) >= 3:
                    self.pinned[slug(name)].add(entry[2])
                    self.reach[slug(name)].add(entry[2])
            for entry in (getattr(tilemap, "trash_spawns", None) or []):
                if len(entry) >= 3:
                    self.pinned[slug(name)].add(entry[2])
                    self.reach[slug(name)].add(entry[2])

    # -- queries ------------------------------------------------------------

    @property
    def zone_keys(self):
        """The zone keys the overworld can ever pass. Falls back to the
        encounter tables' spelling when zones were not built, which is why
        --no-zones prints a warning: encounters.json does not list every
        map (hand-built dungeons have no table), so an explore target can
        look wrong under --no-zones and be fine."""
        return set(self.zones) if self.zones else set(self.reach)

    def is_boss(self, creature):
        return bool(self.creatures.get(creature, {}).get("is_boss"))

    def item_sources(self, item_id):
        """Everything in the game that can put `item_id` in a player's bags.

        QUEST DROPS ARE NOT THE ONLY SOURCE, and reading them as if they were is what made this
        check report five working objectives as broken. A GATHER objective - "hold 8 liferoot" -
        is meant to point at a REAL gatherable: world/quest.py's own definition is "hold N of a
        QuestItem/material", and a material comes off a node, not off a corpse. Arathi's
        herbalist, prospector and shipwright all ask for things that are in
        data/gathering/node_pools.json for the zone the quest is set in, and all three read as
        unobtainable here until the pools were part of the answer.

        Pays for a player's existing profession instead of inventing a seventh kind of bandit
        who inexplicably carries herbs, which is the alternative and is worse.
        """
        out = [c for c, drops in self.quest_drops.items()
               if any(d.get("item_id") == item_id for d in drops)]
        out += [f"gathered:{zone}" for zone, z in self.gather_pools.items()
                if item_id in (z.get("table") or {})]
        return out

    def npc_exists(self, npc_id):
        return (npc_id in self.ambient or npc_id in self.vendors
                or npc_id in self.recruits or str(npc_id).startswith("item:"))

    def classify_boss_reachability(self, creature):
        """How a player gets at an is_boss creature: 'pinned', 'subzone',
        or 'unreachable'.

        The three answers come from three different pieces of the engine and
        conflating them is the mistake this docstring exists to stop:

        pinned      - the creature has a fixed chamber (a cave boss placed
                      by CaveSpawnManager from the cave's own table, or a
                      hand-built zone's boss_positions entry). Deterministic:
                      walk in, it is there.
        subzone     - the creature is named in a SUBZONE's table.
                      CreatureManager.get_random_creature's subzone branch
                      rolls rare_names at RARE_SPAWN_CHANCE, or at
                      QUEST_RARE_SPAWN_CHANCE when an active quest wants
                      this very creature. Low per-roll, certain eventually.
                      This is the engine's designed home for a named
                      open-world boss a quest is built around - it is NOT a
                      rule violation, see this module's docstring.
        unreachable - the creature appears ONLY in an `open_zone` table.
                      get_random_encounter builds trash_table by filtering
                      is_boss OUT, and the rare roll it then does is gated
                      on location_type == "subzone", so an open_zone boss is
                      excluded from the only two code paths that could
                      produce it. Weight 0 makes no difference; weight 5
                      would make no difference either.
        """
        kinds = {k for k, _, _ in self.placement.get(creature, ())}
        if creature in {c for names in self.pinned.values() for c in names}:
            return "pinned"
        if "cave" in kinds or "dungeon" in kinds:
            return "pinned"
        if "subzone" in kinds:
            return "subzone"
        return "unreachable"


# ---------------------------------------------------------------------------
# PHASE 1 - resolve objectives
# ---------------------------------------------------------------------------


def resolve_objectives(world, rows):
    """One finding per objective that cannot resolve to something real.

    Each finding is (severity, quest_id, file, message). "broken" means a
    player cannot finish it; "suspect" means it resolves but something about
    it will not behave as authored.
    """
    findings = []
    #: Every quest-item id any quest hands over, anywhere - see the DELIVER
    #: branch below for why this has to be global rather than per-quest.
    granted_items = {d["item_id"] for _, q in rows
                     for defs in (q.get("grant_items") or {}).values()
                     for d in defs}
    all_ids = {q["quest_id"] for _, q in rows}

    for fname, q in rows:
        qid = q["quest_id"]

        if not world.npc_exists(q["giver_npc_id"]):
            findings.append(("broken", qid, fname,
                             f"giver_npc_id {q['giver_npc_id']!r} is in no NPC roster"))
        collector = q.get("turn_in_npc_id") or q["giver_npc_id"]
        if not world.npc_exists(collector):
            findings.append(("broken", qid, fname,
                             f"turn-in NPC {collector!r} is in no NPC roster - "
                             f"nothing can collect this quest"))

        for idx, o in enumerate(q.get("objectives", [])):
            otype = o.get("type")
            target = o.get("target")
            where = f"objective {idx} ({otype})"

            if otype in KILL_TYPES:
                names = [t for t in [target] + list(o.get("alt_targets") or []) if t]
                if not names:
                    findings.append(("broken", qid, fname, f"{where} names no creature"))
                    continue
                for name in names:
                    if name not in world.creatures:
                        findings.append(("broken", qid, fname,
                                         f"{where} kills {name!r}, which is not in "
                                         f"data/creatures/creatures.json"))
                        continue
                    if otype == "kill_boss" and not world.is_boss(name):
                        # record_kill skips a KILL_BOSS objective unless the
                        # call said is_boss=True, and combat takes that
                        # straight off the Monster, which CreatureManager
                        # sets from creatures.json. A kill_boss objective on
                        # a non-boss creature can never advance.
                        findings.append(("broken", qid, fname,
                                         f"{where} is kill_boss but {name!r} has "
                                         f"is_boss=false - record_kill can never "
                                         f"credit it"))
                    if world.is_boss(name):
                        how = world.classify_boss_reachability(name)
                        if how == "unreachable":
                            findings.append(("broken", qid, fname,
                                             f"{where} kills {name!r}, an is_boss "
                                             f"creature placed only in an open_zone "
                                             f"table - excluded from trash_table and "
                                             f"from the subzone rare roll, so nothing "
                                             f"spawns it"))
                    elif not world.placement.get(name):
                        findings.append(("broken", qid, fname,
                                         f"{where} kills {name!r}, which is in no "
                                         f"encounter table and no pinned spawn"))

                zone = o.get("zone")
                if zone:
                    zkey = slug(zone)
                    if zkey not in world.zone_keys:
                        findings.append(("broken", qid, fname,
                                         f"{where} is restricted to zone {zkey!r}, "
                                         f"which is not a zone key the overworld can "
                                         f"ever pass record_kill"))
                    elif not any(n in world.reach.get(zkey, ()) for n in names):
                        findings.append(("broken", qid, fname,
                                         f"{where} is restricted to zone {zkey!r} but "
                                         f"{names[0]!r} is not reachable while standing "
                                         f"on that map - the kill never counts"))

            elif otype in ITEM_TYPES:
                if not target:
                    findings.append(("broken", qid, fname, f"{where} names no item"))
                    continue
                # A DELIVER item is usually handed over by THIS quest's own
                # grant_items, but not always: ucq_pd_report delivers
                # uc_sable_report, which ucq_pd_zulketh grants on turn-in.
                # Checking only the quest's own grants reported that working
                # chain as a broken quest - so the index is global, and
                # Phase 4 is what proves the chain really hands it over.
                if target not in granted_items and not world.item_sources(target):
                    findings.append(("broken", qid, fname,
                                     f"{where} wants {target!r}, which nothing drops "
                                     f"(data/creatures/quest_drops.json) and no quest's "
                                     f"grant_items hands over"))

            elif otype == "explore":
                if not target:
                    # The exact shape of the four Ashenvale bugs: the place
                    # name went into `zone`, which record_zone_entered never
                    # reads, and `target` - the only field it compares - was
                    # left null.
                    findings.append(("broken", qid, fname,
                                     f"{where} has target=null"
                                     + (f" (place name is parked in zone={o['zone']!r},"
                                        f" which no explore hook reads)" if o.get("zone")
                                        else "")))
                    continue
                tkey = slug(target)
                if tkey not in world.zone_keys:
                    findings.append(("broken", qid, fname,
                                     f"{where} explores {tkey!r}, which is not a live "
                                     f"zone key - record_zone_entered/"
                                     f"record_position_reached compare against the "
                                     f"map's own name and never match"))
                elif o.get("target_x") is not None and world.zones:
                    tilemap = world.zones[tkey]
                    x, y = o["target_x"], o["target_y"]
                    if not (0 <= x < tilemap.width and 0 <= y < tilemap.height):
                        findings.append(("broken", qid, fname,
                                         f"{where} gates on ({x},{y}), outside "
                                         f"{tkey} ({tilemap.width}x{tilemap.height})"))
                    elif not _reachable_within(tilemap, x, y, o.get("radius", 6)):
                        # record_position_reached needs the player to get
                        # within radius, and the player can only stand on
                        # walkable tiles - a gate whose whole radius is wall
                        # is a quest you cannot finish by walking.
                        findings.append(("broken", qid, fname,
                                         f"{where} gates on ({x},{y}) r={o.get('radius', 6)} "
                                         f"in {tkey}, where no tile in range is walkable"))

            elif otype == "craft":
                if not _craftable(target):
                    findings.append(("broken", qid, fname,
                                     f"{where} wants {target!r} crafted, which is "
                                     f"neither a profession recipe nor a smelting "
                                     f"output - record_craft is never called with it"))

            elif otype == "dialogue":
                from world.quest_dialogue import get_all_topics
                authored = {t for t, _ in get_all_topics(qid)}
                for topic in (o.get("topics") or []):
                    if topic not in authored:
                        findings.append(("broken", qid, fname,
                                         f"{where} needs topic {topic!r} asked, which "
                                         f"world/quest_dialogue.py has no content for - "
                                         f"the dialog screen renders no button for it"))

            elif otype != "story":
                findings.append(("suspect", qid, fname,
                                 f"{where} has unknown objective type {otype!r}"))

        for defs in (q.get("grant_items") or {}).values():
            for d in defs:
                starts = d.get("starts_quest_id")
                if starts and starts not in all_ids:
                    findings.append(("broken", qid, fname,
                                     f"grant_items item {d['item_id']!r} starts quest "
                                     f"{starts!r}, which does not exist"))
    return findings


def _reachable_within(tilemap, x, y, radius):
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            if dx * dx + dy * dy > radius * radius:
                continue
            tx, ty = x + dx, y + dy
            if 0 <= tx < tilemap.width and 0 <= ty < tilemap.height:
                try:
                    if tilemap.is_walkable(tx, ty):
                        return True
                except Exception:          # noqa: BLE001 - defensive only
                    return True
    return False


_CRAFT_IDS = None


def _craftable(recipe_id):
    """CRAFT targets are 'a Blacksmithing recipe id or a Smelting output id'
    per ObjectiveType.CRAFT, and record_craft is called with both spellings
    (world/crafting_manager.py passes the recipe id AND each output id,
    world/smelting_manager.py passes the output id). Checking only the
    recipe side reports every `bar_*` smelting quest as broken - it was the
    first thing this check got wrong."""
    global _CRAFT_IDS
    if _CRAFT_IDS is None:
        ids = set()
        from world.smelting_manager import get_smelting_manager
        ids |= set(get_smelting_manager().recipes)
        from world.recipe_manager import make_recipe_scroll
        _CRAFT_IDS = (ids, make_recipe_scroll)
    ids, make_scroll = _CRAFT_IDS
    return recipe_id in ids or make_scroll(recipe_id) is not None


# ---------------------------------------------------------------------------
# PHASE 2 - resolve rewards
# ---------------------------------------------------------------------------


def resolve_rewards(world, rows):
    findings = []
    from world.quest import build_unique_reward_set
    from entities.character import Character
    from world.recipe_manager import make_recipe_scroll

    # One Character, reused: equip() is a pure slot-table lookup
    # (Equipment._resolve_slot -> `target_slot not in self.slots` -> None),
    # so what is already worn cannot change the answer, and building a
    # Character per quest costs a talent-tree load each time.
    probe = Character(name="Audit", char_class="Warrior", level=60)

    for fname, q in rows:
        qid = q["quest_id"]

        # THIS RULE WAS TRUE AND IS NOT ANY MORE, AND THAT IS WORSE THAN NEVER HAVING HAD IT.
        #
        # `rewards` really was unread once; QuestManager._build_quest now does
        #     unique_item_defs=q_def.get("unique_item_defs") or q_def.get("rewards")
        # and has for a while. The rule was never retired with the fix, so it reported 215
        # quests across eleven files - Hillsbrad, the Underdark, Southern Needles, Arathi - as
        # awarding no gear while they all award gear perfectly well. 215 false findings in a
        # list of 244 is not a noisy check, it is a check that hides the real ones: the two
        # genuinely broken deliver objectives in this same run were sitting underneath them.
        #
        # An audit that is wrong in the safe direction still costs you the audit.

        for key in ("unique_item_defs", "rewards"):
            for d in (q.get(key) or []):
                label = d.get("name", "?")
                if d.get("slot") not in world.slots:
                    findings.append(("broken", qid, fname,
                                     f"reward {label!r} has slot {d.get('slot')!r}, "
                                     f"which is not a slot in data/items/slots.json - "
                                     f"Equipment.equip returns None and the item goes "
                                     f"nowhere"))
                if d.get("weapon_type") and d["weapon_type"] not in world.weapon_types:
                    findings.append(("broken", qid, fname,
                                     f"reward {label!r} has weapon_type "
                                     f"{d['weapon_type']!r}, not in weapon_types.json"))
                if d.get("armor_type") and d["armor_type"] not in world.armor_types:
                    findings.append(("broken", qid, fname,
                                     f"reward {label!r} has armor_type "
                                     f"{d['armor_type']!r}, not in armor_types.json"))
                if d.get("rarity") not in world.rarities:
                    findings.append(("suspect", qid, fname,
                                     f"reward {label!r} has rarity {d.get('rarity')!r}, "
                                     f"not in rarity.json"))

        # Build them for real, then try to wear them. A reward that builds
        # fine and cannot be equipped is the bug validate_content.py already
        # documents for crafted gear ("crafted fine, then equip() silently
        # put them nowhere") - quest rewards go through the same Equipment.
        if q.get("unique_item_defs"):
            try:
                choices = build_unique_reward_set(q["unique_item_defs"])
            except Exception as exc:                     # noqa: BLE001
                findings.append(("broken", qid, fname,
                                 f"build_unique_reward_set raised "
                                 f"{type(exc).__name__}: {exc}"))
                continue
            for choice in choices:
                if probe.equipment.equip(choice.item) is None:
                    findings.append(("broken", qid, fname,
                                     f"reward {choice.item.name!r} cannot be equipped "
                                     f"(slot {choice.item.slot!r})"))

        if q.get("reward_recipe") and make_recipe_scroll(q["reward_recipe"]) is None:
            findings.append(("broken", qid, fname,
                             f"reward_recipe {q['reward_recipe']!r} is not a real "
                             f"recipe - turn_in_quest warns and awards nothing"))
    return findings


# ---------------------------------------------------------------------------
# PHASE 3 - chains
# ---------------------------------------------------------------------------


def build_chain_graph(rows):
    """deps[quest] = quests that must be COMPLETED first, exactly as
    QuestManager._is_unlocked decides it: the quest that names this one as
    its next_quest_id, plus every entry in requires_quests."""
    by_id = {q["quest_id"]: q for _, q in rows}
    deps = {qid: set() for qid in by_id}
    predecessors = defaultdict(list)
    findings = []

    for fname, q in rows:
        qid = q["quest_id"]
        nxt = q.get("next_quest_id")
        if nxt:
            if nxt not in by_id:
                findings.append(("broken", qid, fname,
                                 f"next_quest_id {nxt!r} does not exist"))
            else:
                predecessors[nxt].append(qid)
                deps[nxt].add(qid)
        for req in (q.get("requires_quests") or []):
            if req not in by_id:
                findings.append(("broken", qid, fname,
                                 f"requires_quests names {req!r}, which does not exist"))
            else:
                deps[qid].add(req)

    for qid, preds in predecessors.items():
        if len(preds) > 1:
            # _is_unlocked only consults _find_predecessor, which returns
            # the FIRST quest whose next_quest_id matches. With two, which
            # one gates is dict-order luck.
            findings.append(("suspect", qid, by_id[qid].get("_file", "?"),
                             f"{len(preds)} quests name this as next_quest_id "
                             f"({', '.join(sorted(preds))}) - _find_predecessor "
                             f"returns only the first, so the gate is iteration order"))
    return deps, findings


def topo_order(deps):
    """Dependency order, so Phase 4 reaches a quest only after really
    turning in everything that gates it. Cycles are returned separately -
    a cycle is a set of quests no player can ever enter."""
    ready = [q for q, d in deps.items() if not d]
    remaining = {q: set(d) for q, d in deps.items()}
    order, done = [], set()
    while ready:
        qid = ready.pop()
        order.append(qid)
        done.add(qid)
        for other, d in remaining.items():
            if qid in d:
                d.discard(qid)
                if not d and other not in done and other not in ready:
                    ready.append(other)
    cyclic = sorted(set(deps) - done)
    return order, cyclic


# ---------------------------------------------------------------------------
# PHASE 4 - play every quest through the real engine
# ---------------------------------------------------------------------------


def play_all(world, rows, deps, only=None):
    """Accept, satisfy and hand in every quest on one real Character.

    Returns (results, findings). results[qid] is a dict with 'ok' and, when
    it failed, 'why'.

    Design notes that are load-bearing:

    * ONE QuestManager for the whole run, walked in dependency order. A
      chained quest's gate is "is my predecessor COMPLETED", so the honest
      way to test it is to have genuinely completed the predecessor through
      turn_in_quest - not to poke quest.status. A quest that fails here
      because its prerequisite failed is reported as blocked, not broken, so
      one real bug does not inflate into forty.
    * LEVEL 60. level_min is a real gate (accept_quest refuses below it) and
      is NOT what this phase is testing - Phase 5 tests the ladder. Running
      at 60 keeps a level gate from masquerading as a broken objective, the
      same reason audit_pet_combat summons at 60 rather than the template
      minimum.
    * The objectives are satisfied through the engine's own hooks with the
      arguments the GAME would pass: a real zone key, and is_boss read from
      creatures.json rather than hard-coded True. Passing is_boss=True
      unconditionally would have hidden every kill_boss-on-a-non-boss bug,
      and passing the objective's own zone string rather than a real runtime
      key would have hidden the Sepulcher and Drowning Floor bugs - the
      instrument has to be as fussy as the engine is.
    """
    from entities.character import Character
    from entities.party import Party
    from entities.loot_item import add_loot_item
    from world.quest_manager import QuestManager
    from world.quest import ObjectiveType, QuestStatus

    mgr = QuestManager()
    player = Character(name="Auditor", char_class="Warrior", level=60)
    party = Party(player)
    # Bag pressure is a real accept_quest failure mode (it sets last_error
    # and refuses), but it is not what is under test here, so the bag is
    # emptied before every quest below. inventory_capacity is a live
    # property off equipped bags and has no setter, so it cannot be raised -
    # the 24 base slots are plenty for one quest's grants plus one stacked
    # fetch item, and an "accept_quest refused (bag full)" line in the
    # report would be the instrument's fault, not the quest's.

    order, cyclic = topo_order(deps)
    results, findings = {}, []
    for qid in cyclic:
        results[qid] = {"ok": False, "why": "in a prerequisite cycle - never unlockable"}

    by_file = {q["quest_id"]: f for f, q in rows}

    for qid in order:
        if only and qid != only:
            continue
        quest = mgr.quests.get(qid)
        if quest is None:
            results[qid] = {"ok": False, "why": "QuestManager did not load it"}
            continue

        blocked = [d for d in deps.get(qid, ())
                   if not results.get(d, {}).get("ok", False)]
        if blocked and not only:
            results[qid] = {"ok": False, "blocked_by": sorted(blocked),
                            "why": f"prerequisite(s) could not be completed: "
                                   f"{', '.join(sorted(blocked))}"}
            continue

        player.inventory = []

        if not mgr._is_unlocked(qid):
            # With every prerequisite genuinely COMPLETED, the only thing
            # left that _is_unlocked consults is the faction standing gate
            # in data/factions/factions.json. That is a deliberate gate,
            # not a bug, so it is reported as such.
            results[qid] = {"ok": False, "gated": True,
                            "why": "_is_unlocked() is False with every prerequisite "
                                   "completed - a faction standing gate"}
            continue

        if not mgr.accept_quest(qid, player_level=player.level, player=player):
            results[qid] = {"ok": False,
                            "why": f"accept_quest refused "
                                   f"({mgr.last_error or 'no reason given'})"}
            continue

        for o in quest.objectives:
            _satisfy(world, mgr, player, quest, o, ObjectiveType, add_loot_item)

        mgr.refresh_gather_progress(player)

        if quest.status != QuestStatus.READY_TO_TURN_IN:
            unmet = [f"{o.objective_type.value}:{o.target!r} "
                     f"{o.progress}/{o.count}"
                     for o in quest.objectives if not o.is_complete()]
            results[qid] = {"ok": False,
                            "why": f"objectives never completed through the real hooks: "
                                   f"{'; '.join(unmet)}"}
            findings.append(("broken", qid, by_file.get(qid, "?"), results[qid]["why"]))
            continue

        # The collector has to be able to SEE it, not just hold the id -
        # quests_by_collector is built at load time from collector_npc_id,
        # and a quest the collector's own list does not contain is a quest
        # the dialog screen never offers to hand in.
        if quest not in mgr.get_turn_in_ready_quests(quest.collector_npc_id):
            results[qid] = {"ok": False,
                            "why": f"ready to turn in, but "
                                   f"get_turn_in_ready_quests({quest.collector_npc_id!r}) "
                                   f"does not list it"}
            findings.append(("broken", qid, by_file.get(qid, "?"), results[qid]["why"]))
            continue

        if not mgr.turn_in_quest(qid, player, party):
            results[qid] = {"ok": False, "why": "turn_in_quest refused"}
            findings.append(("broken", qid, by_file.get(qid, "?"), results[qid]["why"]))
            continue

        if quest.status != QuestStatus.COMPLETED:
            results[qid] = {"ok": False,
                            "why": f"turn_in_quest returned True but status is "
                                   f"{quest.status.value}"}
            findings.append(("broken", qid, by_file.get(qid, "?"), results[qid]["why"]))
            continue

        results[qid] = {"ok": True}

    return results, findings


def _satisfy(world, mgr, player, quest, o, ObjectiveType, add_loot_item):
    """Do the thing a player would do, through the hook the game calls."""
    t = o.objective_type

    if t in (ObjectiveType.KILL, ObjectiveType.KILL_BOSS):
        name = o.target
        # The zone argument matters: record_kill drops the kill when the
        # objective has a zone and it does not match. Feeding it the
        # objective's own zone string unconditionally would make every
        # mis-keyed zone restriction pass. So: send the key the overworld
        # would really send from a map where this creature can be fought,
        # and only fall back to the objective's own spelling when no such
        # map exists (in which case the objective is already reported).
        zone = o.zone
        if zone:
            real = [zk for zk in world.reach
                    if zk == zone and name in world.reach[zk]]
            zone = real[0] if real else o.zone
        else:
            candidates = [zk for zk, names in world.reach.items() if name in names]
            zone = candidates[0] if candidates else None
        for _ in range(o.count):
            mgr.record_kill(name, zone, is_boss=world.is_boss(name))

    elif t in (ObjectiveType.GATHER, ObjectiveType.FETCH, ObjectiveType.DELIVER):
        add_loot_item(player, o.target, o.display_label(), category="quest",
                      amount=o.count, quest_id=quest.quest_id)
        mgr.refresh_gather_progress(player)

    elif t == ObjectiveType.EXPLORE:
        # Only a key the overworld can really produce counts. Handing
        # record_zone_entered the objective's own target string would make
        # every explore objective pass by construction, including the six
        # that cannot be finished in play.
        key = slug(o.target) if o.target else None
        if key in world.zone_keys:
            if o.target_x is None:
                mgr.record_zone_entered(key)
            else:
                mgr.record_position_reached(key, o.target_x, o.target_y)

    elif t == ObjectiveType.CRAFT:
        mgr.record_craft(o.target, o.count)

    elif t == ObjectiveType.DIALOGUE:
        from world.quest_dialogue import get_topic
        for topic in o.topics:
            # Only topics with authored content, because that is all the
            # dialog screen can render a button for.
            if get_topic(quest.quest_id, topic):
                o.ask_topic(topic)
        if quest.is_complete():
            from world.quest import QuestStatus
            quest.status = QuestStatus.READY_TO_TURN_IN


# ---------------------------------------------------------------------------
# PHASE 5 - level gating
# ---------------------------------------------------------------------------


def level_bands(rows, deps, results):
    """Which levels have quests a player could actually be doing.

    A quest counts for level L when level_min <= L and every quest gating it
    is itself completable - a quest behind a broken prerequisite is not
    content at level L however low its level_min is. level_max is not a gate
    (Quest.get_scaled_exp_reward tapers, it does not refuse), so a quest
    counts from level_min up to level_max where one is set, and for the ten
    levels after level_min where it is not, which is the widest band the
    taper still pays real XP over.
    """
    per_level = defaultdict(list)
    for _, q in rows:
        qid = q["quest_id"]
        if not results.get(qid, {}).get("ok", False):
            continue
        lo = q.get("level_min", 1)
        hi = q.get("level_max") or min(60, lo + 10)
        for lvl in range(max(1, lo), min(60, hi) + 1):
            per_level[lvl].append(qid)
    empty = [lvl for lvl in range(1, 61) if not per_level.get(lvl)]
    thin = [(lvl, len(per_level[lvl])) for lvl in range(1, 61)
            if 0 < len(per_level.get(lvl, [])) < 4]
    return per_level, empty, thin


# ---------------------------------------------------------------------------
# PHASE 6 - project content rules
# ---------------------------------------------------------------------------

#: An escort is not expressible in this engine - ObjectiveType has no
#: follow/protect/survive member and nothing in QuestManager tracks an NPC
#: moving - so the only way one could exist is as a quest whose PROSE asks
#: for one while its objectives do something else. That is what this looks
#: for, and it is why a prose hit alone is not a violation: "drovers are
#: starting to ask for an escort" is world-building in a kill quest, and
#: three of those read as escorts to a keyword search.
ESCORT_PROSE = re.compile(
    r"\bescort\b|\baccompany\b|walk (him|her|them) (back|to)\b|"
    r"see (him|her|them) (safely|home)\b|"
    r"(keep|get) (him|her|them) alive (until|while|as)\b|"
    r"travel(?:ling|ing)? with (me|him|her|us)\b", re.I)

#: Earth infrastructure. Deliberately excludes "highway", "traffic" and
#: "highwayman": Durotar's road IS called the highway in eighteen quests, a
#: highwayman is a bandit, and cart traffic on a bridge is cart traffic. A
#: first draft that included them reported sixteen violations and every one
#: was a false accusation.
REAL_WORLD = re.compile(
    r"\b(skyscraper|parking lot|car park|petrol station|gas station|asphalt|"
    r"tarmac|power line|pylon|telephone|streetlight|street light|lamppost|"
    r"billboard|airport|runway|subway|supermarket|apartment block|office block|"
    r"guardrail|overpass|underpass|chain-?link|railway|railroad|freeway|"
    r"motorway|interstate|helicopter|automobile)\b", re.I)

#: The Integration was three years ago (claude/integration_timeline.md). A
#: wrong elapsed time is a span attached to the EVENT, not any span in the
#: prose - "forty years of Alterac winter" and "eight years of service" are
#: a climate and a career. So the number has to sit next to language about
#: the merge itself.
INTEGRATION_SPAN = re.compile(
    r"\b(?:one|two|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty|"
    r"thirty|forty|fifty|a|\d+)\s+(?:years?|decades?|centur(?:y|ies))\s+"
    r"(?:ago|since|back)[^.]{0,80}?"
    r"(?:integration|came through|came across|crossed over|the merge|"
    r"your lot|you lot|arrived|the change|your world|that blue planet)"
    r"|(?:integration|the merge|crossed over|came through)[^.]{0,80}?"
    r"\b(?:one|two|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty|"
    r"thirty|forty|fifty|\d+)\s+(?:years?|decades?|centur(?:y|ies))\b", re.I)

#: Stat-sheet numbers. A level, a damage figure or a percentage in quest
#: prose is the thing the writing guide bans outright; a bare count is
#: handled by prose_count_mismatches instead, which can say whether it is
#: also WRONG.
STAT_PROSE = re.compile(
    r"\b(?:level\s*\d+|\d+\s*(?:dps|damage|armou?r|hp|mana|stamina|intellect|"
    r"strength|agility|spirit)\b|\d+%|\+\d+\s*(?:str|agi|int|sta|spi))", re.I)

_NUM_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
              "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
              "twelve": 12, "dozen": 12, "fifteen": 15, "twenty": 20}
#: LEADING \b IS LOAD-BEARING. Without it the alternation matched the tail
#: of ordinary words: "Redstone scorpids" read as "one scorpids", "rimebone
#: hounds" as "one hounds", "gone and the charges" as "one and the charges"
#: and "Forgotten Pools" as "ten Pools". Fourteen of the fifteen findings
#: left after the real count mismatches were fixed were this, which is the
#: way a check like this stops being read.
_NUM_RE = r"\b(?:" + "|".join(_NUM_WORDS) + r"|\d{1,2})"


def prose_count_mismatches(rows, overlay):
    """Prose that tells the player a different number than the objective.

    HOW THIS WAS WRONG FIRST. Looking for any count-shaped number in the
    text reported 98 quests, nearly all of them "three weeks" or "eleven
    nights". The surviving rule: the number must sit within two words of a
    word from the objective's own target name. That turns "Eight worg
    prowlers" against a count of 6 into a hit and leaves prose about
    weather alone.
    """
    out = []
    for fname, q in rows:
        prose = quest_prose(q, overlay)
        text = " ".join([prose["description"], prose["accept_text"]])
        for o in q.get("objectives", []):
            if o.get("type") not in KILL_TYPES | ITEM_TYPES:
                continue
            count = o.get("count", 1)
            words = [w for w in re.split(r"[\s_]+", str(o.get("target") or ""))
                     if len(w) > 3]
            for word in words:
                stem = re.escape(word.rstrip("s"))
                m = re.search(_NUM_RE + r"\s+(?:\w+\s+){0,2}" + stem + r"s?\b",
                              text, re.I)
                if not m:
                    continue
                token = re.match(_NUM_RE, m.group(0), re.I).group(0).lower()
                said = _NUM_WORDS.get(token, int(token) if token.isdigit() else None)
                if said is not None and said != count:
                    out.append((fname, q["quest_id"], o.get("target"),
                                count, said, m.group(0).strip()))
                break
    return out


def content_rules(world, rows, overlay):
    findings, cleared = [], Counter()
    for fname, q in rows:
        qid = q["quest_id"]
        prose = quest_prose(q, overlay)
        text = " ".join(prose.values())
        types = {o.get("type") for o in q.get("objectives", [])}

        m = ESCORT_PROSE.search(text)
        if m:
            # The engine cannot express an escort, so the only real
            # violation would be a quest whose objectives try to fake one.
            # Everything else is prose about escorts, which is allowed.
            if types <= {"kill", "kill_boss", "fetch", "gather", "deliver",
                         "explore", "story", "dialogue", "craft"}:
                cleared["escort wording in a non-escort quest"] += 1
            else:
                findings.append(("violation", qid, fname,
                                 f"ESCORT: {m.group(0)!r} with objectives {types}"))

        m = REAL_WORLD.search(text)
        if m:
            findings.append(("violation", qid, fname,
                             f"REAL-WORLD CONTENT: {m.group(0)!r}"))

        m = INTEGRATION_SPAN.search(text)
        if m:
            span = re.match(r"\S+\s+\S+", m.group(0))
            if "three year" not in m.group(0).lower():
                findings.append(("violation", qid, fname,
                                 f"ELAPSED TIME: {(span.group(0) if span else m.group(0))!r} "
                                 f"attached to the Integration, which was three years ago"))

        m = STAT_PROSE.search(text)
        if m:
            findings.append(("violation", qid, fname,
                             f"STAT NUMBERS IN PROSE: {m.group(0)!r}"))

        # Rares. The engine has no is_rare; what it has is a subzone roll
        # whose chance RISES when a quest wants the creature, so a named
        # subzone boss as a quest target is the designed case, not a
        # violation. The real failure mode is the one Phase 1 reports:
        # an is_boss creature nothing spawns at all.
        for o in q.get("objectives", []):
            if o.get("type") in KILL_TYPES and world.is_boss(o.get("target")):
                how = world.classify_boss_reachability(o["target"])
                if how == "subzone":
                    cleared["quest targets a named subzone boss "
                            "(QUEST_RARE_SPAWN_CHANCE path - by design)"] += 1
    return findings, cleared


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------


def main(argv):
    only = argv[argv.index("--quest") + 1] if "--quest" in argv else None
    use_zones = "--no-zones" not in argv
    show_counts = "--counts" in argv

    rows = raw_quests()
    overlay = text_overlays()
    print(f"{len(rows)} quests in {len(set(f for f, _ in rows))} files, "
          f"{len(overlay)} text overlays")
    if not use_zones:
        print("WARNING: --no-zones skips the live tilemaps, so pinned dungeon")
        print("         bosses and explore-coordinate walkability cannot be")
        print("         checked and may be reported wrongly.")
    print("building world model" + (" (tilemaps take ~1 min)" if use_zones else ""))
    world = World(use_zones=use_zones)
    print(f"  {len(world.creatures)} creatures, {len(world.placement)} placed, "
          f"{len(world.zone_keys)} zone keys, "
          f"{len(world.ambient) + len(world.vendors) + len(world.recruits)} NPCs")

    findings = []
    findings += resolve_objectives(world, rows)
    findings += resolve_rewards(world, rows)
    deps, chain_findings = build_chain_graph(rows)
    findings += chain_findings

    print("\nplaying every quest through the real engine")
    results, play_findings = play_all(world, rows, deps, only=only)
    findings += play_findings

    broken = sorted({(q, f, m) for sev, q, f, m in findings if sev == "broken"})
    suspect = sorted({(q, f, m) for sev, q, f, m in findings if sev == "suspect"})

    failed = {q: r for q, r in results.items() if not r.get("ok")}
    direct = {q: r for q, r in failed.items() if "blocked_by" not in r
              and not r.get("gated")}
    blocked = {q: r for q, r in failed.items() if "blocked_by" in r}
    gated = {q: r for q, r in failed.items() if r.get("gated")}

    print(f"\n{'=' * 78}\nPLAYED: {len(results) - len(failed)} of {len(results)} "
          f"quests reached COMPLETED through accept -> objectives -> turn-in")
    print(f"{'=' * 78}")

    if direct:
        print(f"\nCANNOT BE COMPLETED ({len(direct)}) - the real code path refuses:")
        for qid, r in sorted(direct.items()):
            print(f"  {qid:36} {r['why']}")
    if blocked:
        print(f"\nBLOCKED BY A BROKEN PREREQUISITE ({len(blocked)}) - nothing wrong")
        print("  with these quests themselves; they sit behind one of the above:")
        for qid, r in sorted(blocked.items()):
            print(f"  {qid:36} needs {', '.join(r['blocked_by'])}")
    if gated:
        print(f"\nINTENTIONALLY GATED ({len(gated)}) - a faction standing requirement,")
        print("  not a bug. Listed so 'did not complete' is never read as 'broken':")
        for qid, r in sorted(gated.items()):
            print(f"  {qid:36} {r['why']}")

    if broken:
        print(f"\nRESOLUTION FAILURES ({len(broken)}) - an objective, reward or chain")
        print("  link that does not point at anything the game has:")
        for qid, fname, msg in broken:
            print(f"  [{fname}] {qid}\n      {msg}")
    if suspect:
        print(f"\nSUSPECT ({len(suspect)}):")
        for qid, fname, msg in suspect:
            print(f"  [{fname}] {qid}\n      {msg}")

    per_level, empty, thin = level_bands(rows, deps, results)
    print(f"\n{'=' * 78}\nLEVEL LADDER (completable quests only)\n{'=' * 78}")
    print("  lvl " + " ".join(f"{l:>3}" for l in range(1, 61, 1)))
    print("    n " + " ".join(f"{len(per_level.get(l, [])):>3}" for l in range(1, 61)))
    if empty:
        print(f"\n  NOTHING TO DO at level(s): {_ranges(empty)}")
    else:
        print("\n  Every level from 1 to 60 has at least one completable quest.")
    if thin:
        print(f"  THIN (<4 quests): "
              f"{', '.join(f'{l}({n})' for l, n in thin)}")

    rule_findings, cleared = content_rules(world, rows, overlay)
    print(f"\n{'=' * 78}\nPROJECT CONTENT RULES\n{'=' * 78}")
    if rule_findings:
        for sev, qid, fname, msg in sorted(rule_findings, key=lambda r: r[3]):
            print(f"  [{fname}] {qid}\n      {msg}")
    else:
        print("  No escort quests, no Earth content, no wrong elapsed time, no")
        print("  stat numbers in prose.")
    for label, n in cleared.most_common():
        print(f"  CLEARED: {n} x {label}")

    mismatches = prose_count_mismatches(rows, overlay)
    if mismatches:
        print(f"\n  PROSE CONTRADICTS THE OBJECTIVE ({len(mismatches)}): the text names")
        print("  a required count that is not the count the journal tracks. The")
        print("  writing guide bans counts in prose outright, so the fix is to")
        print("  drop the number, not to retune the objective.")
        show = mismatches if show_counts else mismatches[:12]
        for fname, qid, target, count, said, snippet in show:
            print(f"    [{fname}] {qid}: says {snippet!r}, objective wants "
                  f"{count} {target!r}")
        if not show_counts and len(mismatches) > len(show):
            print(f"    ... {len(mismatches) - len(show)} more (--counts for all)")

    bad = len(direct) + len(broken) + len(rule_findings)
    print(f"\n{'=' * 78}")
    print(f"{bad} blocking problem(s); {len(blocked)} quest(s) blocked behind them; "
          f"{len(gated)} gated by design.")
    return 1 if bad else 0


def _ranges(nums):
    out, start, prev = [], None, None
    for n in nums:
        if start is None:
            start = prev = n
            continue
        if n == prev + 1:
            prev = n
            continue
        out.append(f"{start}" if start == prev else f"{start}-{prev}")
        start = prev = n
    if start is not None:
        out.append(f"{start}" if start == prev else f"{start}-{prev}")
    return ", ".join(out)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
