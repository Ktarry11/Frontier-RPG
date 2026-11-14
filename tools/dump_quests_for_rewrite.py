"""Compact view of a quest file for rewriting its text: python3 tools/dump_quests_for_rewrite.py ashenvale [more...]
Shows id, title, giver (name/race), objectives, chain links and the CURRENT text (overlay-aware)."""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
npcs = {n["npc_id"]: n for n in json.load(open("data/npcs/ambient_npcs.json", encoding="utf-8"))["npcs"]}
overlay = {}
for p in glob.glob("data/quests/text/*.json"):
    overlay.update(json.load(open(p, encoding="utf-8")))
for name in sys.argv[1:]:
    qs = json.load(open(f"data/quests/{name}.json", encoding="utf-8"))["quests"]
    by_next = {q.get("next_quest_id"): q["quest_id"] for q in qs if q.get("next_quest_id")}
    for q in qs:
        g = npcs.get(q["giver_npc_id"], {})
        t = npcs.get(q.get("turn_in_npc_id") or "", {})
        o = overlay.get(q["quest_id"], {})
        objs = "; ".join(f'{x["type"]} {x.get("count","")} {x.get("target","")}'.strip() + (f' @{x["zone"]}' if x.get("zone") else "")
                         for x in q["objectives"])
        print(f'## {q["quest_id"]} | {q["title"]} | L{q.get("level_min")} | giver: {g.get("name", q["giver_npc_id"])} ({g.get("race","?")}, {q["zone"]})'
              + (f' | hand-in: {t.get("name", q.get("turn_in_npc_id"))}' if q.get("turn_in_npc_id") else "")
              + (f' | after: {by_next[q["quest_id"]]}' if q["quest_id"] in by_next else "")
              + (f' | next: {q["next_quest_id"]}' if q.get("next_quest_id") else "")
              + (f' | requires: {q["requires_quests"]}' if q.get("requires_quests") else "") + (" | [REWRITTEN]" if o else ""))
        print(f'   OBJ: {objs}')
        print(f'   D: {o.get("description", q["description"])}')
        print(f'   A: {o.get("accept_text", q.get("accept_text",""))}')
        print(f'   T: {o.get("turn_in_text", q.get("turn_in_text",""))}')
