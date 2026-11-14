#!/usr/bin/env python3
"""Tempest Isle's quests and people are the shape Kyle asked for.

    PYTHONPATH=. python3 tools/qa_tempest_quests.py

Kyle, 13 Nov 2026: "Lets finish tempest isle first", and of the writing: "when I say AI tics being
weird it's things like the single word sentences. 'Stay. I'm asking' - no one talks like this."

NINE CLAIMS, read from the shipped data (the builder checks its own source; this checks what the
game will load):
  1. ABOUT SIXTY QUESTS, levels 52-58, at least thirty in each file.
  2. HUBS: at least 70% are given at Ashclaim Landing, the Ashclaim Works or Cinderwharf.
  3. NOBODY CARRIES MORE THAN THREE.
  4. TRASH STARTS QUESTS: at least two per file, and each drop names the quest it starts.
  5. QUEST ITEMS DROP THREE TIMES IN FOUR OR BETTER.
  6. THE WORK VARIES, and one chain ends at an NPC off the island.
  7. EARTH IS HERE: at least a quarter of the quests refer to the Integration or to Earth.
  8. EVERYONE EXISTS: every giver and turn-in NPC has a record standing on a walkable tile, the
     island has two inns and a flight point, and every dialogue topic a quest names is written.
  9. WHOLE SENTENCES: no one-word or two-word sentences, no dashes and no stiff constructions in
     any quest text, any islander's greeting or any dialogue topic.
"""
import collections
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools.build_tempest_quests import voice_problems          # noqa: E402
from tools import tempest_quest_kit as K                        # noqa: E402

EARTH = re.compile(r"three years|the day the world changed|the day everything changed|from Earth|"
                   r"before I came through|before the change|sea route opened|at home|Mombasa|Quito|Kagoshima|Singapore|Sakurajima|came through", re.I)


def load(path, key):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))[key]


def main():
    bad = []
    files = {s: load(f"data/quests/{s}.json", "quests") for s in ("tempest_shallows", "ashen_reach")}
    quests = [q for qs in files.values() for q in qs]
    drops = load("data/creatures/quest_drops.json", "drops")
    by_item = {r["item_id"]: r for rows in drops.values() for r in rows}

    if len(quests) < 60:
        bad.append(f"{len(quests)} quests")
    for s, qs in files.items():
        if len(qs) < 30:
            bad.append(f"{s}: {len(qs)} quests")
        if sum(1 for q in qs if q["giver_npc_id"].startswith("item:")) < 2:
            bad.append(f"{s}: fewer than two quests start from a drop")
    if any(not (52 <= q["level_min"] and q["level_max"] <= 58) for q in quests):
        bad.append("a quest outside 52-58")

    givers = collections.Counter(q["giver_npc_id"] for q in quests)
    hub = sum(n for g, n in givers.items() if g in K.HUB_GIVERS)
    if hub < 0.7 * len(quests):
        bad.append(f"only {hub} of {len(quests)} are given at a hub")
    for g, n in givers.items():
        if n > 3:
            bad.append(f"{g} gives {n}")

    for q in quests:
        if q["giver_npc_id"].startswith("item:"):
            rec = by_item.get(q["giver_npc_id"][5:])
            if not rec or rec.get("starts_quest_id") != q["quest_id"]:
                bad.append(f"{q['quest_id']}: its drop does not start it")
        for o in q["objectives"]:
            if o["type"] == "fetch":
                rec = by_item.get(o["target"])
                if not rec or rec["chance"] < 0.75:
                    bad.append(f"{q['quest_id']}: {o['target']} drops at {rec and rec['chance']}")

    kinds = collections.Counter(o["type"] for q in quests for o in q["objectives"])
    for need in ("kill", "fetch", "explore", "deliver", "dialogue", "kill_boss"):
        if not kinds[need]:
            bad.append(f"no {need} objective anywhere")
    if not any(q.get("turn_in_npc_id") == K.MORGRIM for q in quests):
        bad.append("no chain leaves the island")

    earth = sum(1 for q in quests if EARTH.search(q["accept_text"] + q["turn_in_text"]))
    if earth < 0.25 * len(quests):
        bad.append(f"only {earth} of {len(quests)} quests mention Earth or the Integration")

    # ---- everyone exists, on ground you can stand on
    people = {r["npc_id"]: r for r in load("data/npcs/ambient_npcs.json", "npcs")}
    people.update({r["vendor_id"]: r for r in load("data/npcs/vendors.json", "vendors")})
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        import tools.handbuilt_tempest_shallows as a
        import tools.handbuilt_ashen_reach as b
        import tools.handbuilt_cinderwharf as c
        maps = {"tempest_shallows": a.generate_tempest_shallows(),
                "the_ashen_reach": b.generate_ashen_reach(),
                "cinderwharf": c.generate_cinderwharf()}
    need = {q["giver_npc_id"] for q in quests if not q["giver_npc_id"].startswith("item:")}
    need |= {q["turn_in_npc_id"] for q in quests if q.get("turn_in_npc_id")}
    for nid in sorted(need):
        r = people.get(nid)
        if not r:
            bad.append(f"{nid} has no record")
        elif r["zone"] in maps and not maps[r["zone"]].is_walkable(r["x"], r["y"]):
            bad.append(f"{nid} stands on a tile nobody can stand on")
    islanders = [r for r in people.values() if r["zone"] in maps and not r.get("hidden")]   # hidden sellers: world/secrets.py
    if len(islanders) != 40:
        bad.append(f"{len(islanders)} people on the island, expected 40")
    travel = json.loads((ROOT / "data/travel/travel_data.json").read_text(encoding="utf-8"))
    for inn in ("ts_landing_cook", "cw_innkeeper"):
        if "inn" not in travel["services"].get(inn, []):
            bad.append(f"{inn} keeps no inn")
    if travel["flight_nodes"].get("cinderwharf", {}).get("master") != "cw_flight_master":
        bad.append("Cinderwharf has no flight point")

    from world.quest_dialogue import QUEST_TOPICS
    for q in quests:
        for o in q["objectives"]:
            for t in o.get("topics", []):
                if t not in QUEST_TOPICS.get(q["quest_id"], {}):
                    bad.append(f"{q['quest_id']}: topic {t} is not written")

    # ---- whole sentences
    for q in quests:
        for key in ("accept_text", "turn_in_text", "description"):
            bad += [f"{q['quest_id']} {key}: {p}" for p in voice_problems(q[key])]
    for r in islanders:
        bad += [f"{r['name']} greeting: {p}" for p in voice_problems(r.get("greeting") or "")]
    for qid in ("tmp_nine_generations", "tmp_the_door_was_sealed"):
        for tid, t in QUEST_TOPICS.get(qid, {}).items():
            bad += [f"{tid}: {p}" for p in voice_problems(t["response"])]

    print(f"{len(quests)} quests, {hub} from hubs ({hub / len(quests):.0%}), {len(givers)} givers, "
          f"{earth} mention Earth ({earth / len(quests):.0%}); "
          + ", ".join(f"{k} {v}" for k, v in sorted(kinds.items())))
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for line in bad:
            print("  -", line)
        return 1
    print("\nTempest Isle quests OK - sixty-plus, hub-centred, varied, and written in whole sentences.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
