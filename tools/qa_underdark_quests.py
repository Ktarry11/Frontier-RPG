"""
QA the Crystalline Underdark quest set and its three inbound bridges.

    PYTHONPATH=. python3 tools/qa_underdark_quests.py

Checks the things that are silently wrong rather than loudly wrong - a quest whose giver does not exist is not a
crash, it is a quest nobody is ever offered, and a kill target that does not spawn in the stated zone is an
objective that can never tick. Both of those ship happily.

  1. every giver and turn-in NPC exists in data/npcs/*.json AND has a position in its layout
  2. every requires_quests id exists; no self-dependency and no cycles
  3. every deliver item is granted on accept or dropped by a starter mob
  4. every fetch target appears in data/creatures/quest_drops.json
  5. every craft target is a real recipe or smelting output
  6. every kill / kill_boss target actually appears in that zone's encounter table
  7. every explore target is inside its map and on a walkable tile
  8. starter drops name a quest that exists, and that quest's giver is the matching item:<id>
  9. quest text stays inside the dialog's 760-character cap
 10. the whole set loads through QuestManager with no warnings
 11. NO OBJECTIVE TARGETS A NAMED RARE. Kyle's standing rule, and the one check the Hillsbrad version of
     this file did not have: the six rares in this cluster roll at about 6% in their own subzone, so a
     quest that wants one is a quest that can stall for an hour through no fault of the player. They are
     lore and loot. They are never an objective.
 12. kill counts are not absurd for how common the target is - a 10-kill objective on a creature with
     weight 2 in one subzone is a different quest from the same objective on a weight-5 creature.
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((64, 64))

import tools.handbuilt_kaels_bastion as KB  # noqa: E402
import tools.handbuilt_underdark as UD  # noqa: E402
from world.zone_manager import ZoneManager  # noqa: E402

OURS = ["underdark", "underdark_dungeons"]
INBOUND_IDS = {"hbe_fissure_north", "hbe_route_card", "uc_dalaran_question"}
def zone_map(zm):
    """quest zone key -> real zone display name, DERIVED, never typed.

    This was a hand-written dict of the six zones this script happened to
    test, so any quest pointing anywhere else failed as "does not exist"
    whether or not it was real. arw_through_the_wall explores
    `arathi_west`, which is exactly what the engine normalises "Arathi
    West" to (QuestManager.record_zone_entered and record_position_reached
    both go through world/zone_keys.zone_slug) - the quest worked in game
    and failed here, which is the worst way round.

    world/zone_keys.py exists because six managers each wrote their own
    normaliser and three of them disagreed; a seventh copy typed out by
    hand in a QA script is the same mistake in the place that is supposed
    to catch it. Keyed off the real zone list through the real function.
    """
    from world.zone_keys import zone_slug
    return {zone_slug(name): name for name in zm.zones}


def load(name):
    d = json.loads((ROOT / f"data/quests/{name}.json").read_text())
    return d["quests"] if isinstance(d, dict) and "quests" in d else d


def main():
    _ZM = ZoneManager()
    ZONE_MAP = zone_map(_ZM)
    fails, warns = [], []

    quests = []
    for n in OURS:
        quests += load(n)
    for n in ("hillsbrad", "tirisfal"):
        quests += [q for q in load(n) if q["quest_id"] in INBOUND_IDS]
    ours = {q["quest_id"]: q for q in quests}
    print(f"{len(quests)} quests under test ({len(INBOUND_IDS)} of them inbound from other zones)")

    # every quest id in the game, for requires_quests
    all_ids = set()
    for f in sorted((ROOT / "data/quests").glob("*.json")):
        all_ids |= {q["quest_id"] for q in load(f.stem)}

    # ---- 1. givers and hand-in NPCs
    npcs = {r["npc_id"] for r in json.loads(Path("data/npcs/ambient_npcs.json").read_text())["npcs"]}
    npcs |= {r["vendor_id"] for r in json.loads(Path("data/npcs/vendors.json").read_text())["vendors"]}
    placed = set(KB.NPC_POSITIONS) | set(UD.NPC_POSITIONS)
    for q in quests:
        for role in ("giver_npc_id", "turn_in_npc_id"):
            nid = q.get(role)
            if not nid or nid.startswith("item:"):
                continue
            if nid not in npcs:
                fails.append(f"{q['quest_id']}: {role} '{nid}' is not in data/npcs")
            elif nid.startswith(("kb_", "ud_")) and nid not in placed:
                fails.append(f"{q['quest_id']}: {role} '{nid}' has no position in its layout")

    # ---- 2. prerequisites
    for q in quests:
        for req in q.get("requires_quests", []):
            if req not in all_ids:
                fails.append(f"{q['quest_id']}: requires '{req}', which does not exist")
            if req == q["quest_id"]:
                fails.append(f"{q['quest_id']}: requires itself")

    def cyclic(qid, seen):
        if qid in seen:
            return True
        q = ours.get(qid)
        if not q:
            return False
        return any(cyclic(r, seen | {qid}) for r in q.get("requires_quests", []))

    for qid in ours:
        if cyclic(qid, frozenset()):
            fails.append(f"{qid}: prerequisite cycle")

    # ---- 3/4/5. objective sources
    drops_raw = json.loads(Path("data/creatures/quest_drops.json").read_text())
    drops_raw = drops_raw.get("drops", drops_raw)
    dropped, starters = set(), {}
    for creature, items in drops_raw.items():
        for it in items:
            dropped.add(it["item_id"])
            if it.get("starts_quest"):
                starters[it["item_id"]] = (it["starts_quest"], creature)

    recipes = set()
    rp = json.loads(Path("data/crafting/recipes.json").read_text())["professions"]
    for prof, v in rp.items():
        recs = v["recipes"] if isinstance(v, dict) and "recipes" in v else v
        recipes |= set(recs) if isinstance(recs, dict) else {x.get("recipe_id") or x.get("id") for x in recs}
    bs = json.loads(Path("data/blacksmithing/recipes.json").read_text())
    bs = bs.get("recipes", bs)
    recipes |= set(bs) if isinstance(bs, dict) else {x.get("recipe_id") for x in bs}
    sm = json.loads(Path("data/gathering/smelting_recipes.json").read_text())
    sm = sm.get("recipes", sm)
    recipes |= set(sm) if isinstance(sm, dict) else {x.get("output_id") for x in sm}

    for q in quests:
        granted = {g["item_id"] for g in q.get("grant_items", {}).get("on_accept", [])}
        for o in q["objectives"]:
            t, typ = o.get("target"), o["type"]
            if typ == "deliver" and t not in granted and t not in dropped:
                fails.append(f"{q['quest_id']}: delivers '{t}' but nothing grants or drops it")
            if typ in ("fetch", "gather") and t not in dropped:
                fails.append(f"{q['quest_id']}: fetches '{t}' but no creature drops it")
            if typ == "craft" and t not in recipes:
                fails.append(f"{q['quest_id']}: crafts '{t}', which is not a recipe or smelting output")

    # ---- 6. kill targets actually spawn where the objective says
    enc = json.loads(Path("data/creatures/encounters.json").read_text())["zones"]
    spawns = {}
    for zname, z in enc.items():
        s = set(z.get("open_zone", {}).get("creatures", {}))
        for sub in z.get("subzones", {}).values():
            s |= set(sub["creatures"])
        spawns[zname] = spawns.get(zname, set()) | s
        for cname, cv in z.get("caves", {}).items():
            # UNION, NOT ASSIGN. A cave and a top-level zone entry can carry
            # the same name, and a plain assignment let whichever came last
            # in file order win silently. encounters.json had a stale
            # top-level "The Frostward Descent" holding a copy of the cave's
            # roster from before its bosses were added, so this line
            # overwrote the real table and the three pinned bosses read as
            # not spawning in their own cave. The duplicate is gone; the
            # union is here so the next one cannot hide the same way.
            spawns[cname] = spawns.get(cname, set()) | set(cv["creatures"])
    for q in quests:
        for o in q["objectives"]:
            if o["type"] not in ("kill", "kill_boss"):
                continue
            zk = o.get("zone")
            zname = ZONE_MAP.get(zk, zk)
            if zname not in spawns:
                warns.append(f"{q['quest_id']}: kill zone '{zk}' has no encounter table")
            elif o["target"] not in spawns[zname]:
                fails.append(f"{q['quest_id']}: '{o['target']}' does not spawn in {zname}")

    # ---- 7. explore targets
    zm = _ZM
    for q in quests:
        for o in q["objectives"]:
            if o["type"] != "explore":
                continue
            zname = ZONE_MAP.get(o["target"], o["target"])
            z = zm.get_zone_by_name(zname)
            if z is None:
                fails.append(f"{q['quest_id']}: explore zone '{o['target']}' does not exist")
                continue
            x, y = o["target_x"], o["target_y"]
            if not (0 <= x < z.width and 0 <= y < z.height):
                fails.append(f"{q['quest_id']}: explore point ({x},{y}) is off {zname}")
            elif not z.is_walkable(x, y):
                fails.append(f"{q['quest_id']}: explore point ({x},{y}) in {zname} is not walkable")

    # ---- 8. starter drops line up with their quests
    for item_id, (qid, creature) in starters.items():
        if qid not in all_ids:
            continue
        q = ours.get(qid)
        if q is None:
            continue
        if q["giver_npc_id"] != f"item:{item_id}":
            fails.append(f"{qid}: started by '{item_id}' but its giver is '{q['giver_npc_id']}'")
        if not q.get("turn_in_npc_id"):
            fails.append(f"{qid}: item-started quests need a turn_in_npc_id")
        if creature not in {c for s in spawns.values() for c in s}:
            fails.append(f"{qid}: starter mob '{creature}' does not spawn anywhere")

    # ---- 9. dialog length
    for q in quests:
        for field in ("description", "accept_text", "turn_in_text"):
            n = len(q.get(field) or "")
            if n > 760:
                fails.append(f"{q['quest_id']}: {field} is {n} chars (cap 760)")
            elif n > 700:
                warns.append(f"{q['quest_id']}: {field} is {n} chars, close to the 760 cap")

    # ---- 10. loads clean
    import io
    import contextlib
    from world.quest_manager import QuestManager
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        qm = QuestManager()
    noise = [ln for ln in buf.getvalue().splitlines()
             if "underdark" in ln.lower() or "bloom" in ln.lower() or "warn" in ln.lower()]
    for ln in noise:
        warns.append(f"QuestManager: {ln.strip()}")
    missing = [qid for qid in ours if qid not in qm.quests]
    if missing:
        fails.append(f"QuestManager did not load: {missing[:5]}")
    print(f"QuestManager loaded {len(qm.quests)} quests in total")

    # ---- 11. no quest is built around a named rare (Kyle's standing rule)
    cre = json.loads(Path("data/creatures/creatures.json").read_text())["creatures"]
    #: A rare is a boss that is ALSO weighted 0 in an open-zone/subzone table - it rolls at about 6% where
    #: it lives. A dungeon or cave boss is also is_boss and also weight 0, but it is hand-placed at a fixed
    #: point, so it is always there. The difference is the map, not the record.
    fixed = set()
    for mod in ("handbuilt_frostward_descent", "handbuilt_hollow_geode", "handbuilt_deep_bloom"):
        m = __import__(f"tools.{mod}", fromlist=["x"])
        fn = next(f for f in dir(m) if f.startswith("build_") and not f.endswith("_baked"))
        getattr(m, fn)()
        fixed |= set(m.BOSSES)
    rares = {n for n, c in cre.items() if c.get("is_boss") and n not in fixed}
    for q in quests:
        for o in q["objectives"]:
            if o["type"] in ("kill", "kill_boss") and o["target"] in rares:
                fails.append(f"{q['quest_id']}: objective targets the RARE '{o['target']}' - "
                             f"rares roll at ~6%%, so this quest can stall indefinitely")

    # ---- 12. kill counts against how common the target actually is
    weights = {}
    for zname, z in enc.items():
        for block in [z.get("open_zone", {})] + list(z.get("subzones", {}).values()) \
                + list(z.get("caves", {}).values()):
            for cname, w in block.get("creatures", {}).items():
                weights[cname] = max(weights.get(cname, 0), w)
    for q in quests:
        for o in q["objectives"]:
            if o["type"] != "kill":
                continue
            w = weights.get(o["target"], 0)
            n = o.get("count", 1)
            if w and n > w * 3:
                warns.append(f"{q['quest_id']}: {n}x '{o['target']}' but its best spawn weight is {w} - "
                             f"that is a long grind")

    print()
    for w in warns:
        print(f"  warn  {w}")
    if fails:
        print(f"\nFAILED ({len(fails)}):")
        for f in fails:
            print("  -", f)
        return 1
    print(f"\nall checks pass ({len(warns)} warnings)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
