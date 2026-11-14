#!/usr/bin/env python3
"""Where the quest overhaul stands, zone by zone, measured from the game.

    PYTHONPATH=. python3 tools/quest_overhaul_status.py            # the table
    PYTHONPATH=. python3 tools/quest_overhaul_status.py --md       # the same, as markdown

Kyle, 12 Nov 2026: "Since there are a lot of quests and npc text, you need to be systematic
about this!... Keep records of what's done as you work."

One row per quest file, in level order - the order a player meets them, and the order the
overhaul goes in. Every number is counted, none is typed in:

    quests     how many (the target is about 30 per zone)
    types      how many of the seven objective types the zone uses
    chains     quests that are a link in a chain / the longest chain
    leaves     quests with an objective or a next step outside their own zone
    dir        directions: WRONG + SILENT from tools/audit_quest_directions.py
    load       the most quests any one giver carries
    greet      NPC greetings in the zone (each one is a line to check)

DONE is the one thing a person decides: tools/quest_overhaul_done.json lists the zones that
have been through the pass, with the date and what was done.
"""
import glob
import json
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
os.chdir(ROOT)
DONE_PATH = "tools/quest_overhaul_done.json"


def rows():
    import audit_quest_directions as A
    world = A.World()
    findings, _seen, _judged = A.audit(world, [])
    dirs = {}
    for kind in ("WRONG", "SILENT"):
        for stem, _title, _why in findings[kind]:
            dirs.setdefault(stem, [0, 0])[0 if kind == "WRONG" else 1] += 1
    greet = {}
    for path in ("data/npcs/ambient_npcs.json",):
        data = json.load(open(path, encoding="utf-8"))
        for n in (data.get("npcs", data) if isinstance(data, dict) else data):
            if isinstance(n, dict) and n.get("greeting"):
                greet[A.slug(n.get("zone"))] = greet.get(A.slug(n.get("zone")), 0) + 1
    done = json.load(open(DONE_PATH, encoding="utf-8")) if os.path.isfile(DONE_PATH) else {}
    out = []
    for path in sorted(glob.glob("data/quests/*.json")):
        stem = os.path.basename(path)[:-5]
        quests = json.load(open(path, encoding="utf-8")).get("quests", [])
        quests = [q for q in quests if isinstance(q, dict) and q.get("objectives")]
        if not quests:
            continue
        ids = {q["quest_id"] for q in quests}
        levels = [q.get("level_min", 0) for q in quests if q.get("level_min")]
        types = {o.get("type") for q in quests for o in q["objectives"]}
        nxt = {q["quest_id"]: q.get("next_quest_id") for q in quests}
        heads = ids - {v for v in nxt.values() if v}
        longest = 0
        for h in heads:
            n, cur, guard = 1, h, 0
            while nxt.get(cur) in ids and guard < 40:
                cur, n, guard = nxt[cur], n + 1, guard + 1
            longest = max(longest, n)
        in_chain = sum(1 for q in quests if q.get("next_quest_id") or q["quest_id"] in set(nxt.values()))
        zones = {A.slug(q.get("zone")) for q in quests}
        leaves = sum(1 for q in quests
                     if any(o.get("zone") and A.slug(o["zone"]) not in zones for o in q["objectives"])
                     or (q.get("next_quest_id") and q["next_quest_id"] not in ids)
                     or q.get("requires_quests"))
        load = {}
        for q in quests:
            load[q.get("giver_npc_id")] = load.get(q.get("giver_npc_id"), 0) + 1
        w, s = dirs.get(stem, [0, 0])
        out.append({
            "zone": stem, "lo": min(levels or [0]), "hi": max(levels or [0]),
            "mid": statistics.median(levels or [0]), "quests": len(quests), "types": len(types),
            "in_chain": in_chain, "longest": longest, "leaves": leaves, "wrong": w, "silent": s,
            "load": max(load.values()), "greet": sum(greet.get(z, 0) for z in zones),
            "done": done.get(stem, {}).get("date", ""),
        })
    out.sort(key=lambda r: (r["mid"], r["zone"]))
    return out


def main():
    data = rows()
    md = "--md" in sys.argv
    head = ["zone", "levels", "quests", "types", "chains (longest)", "leaves", "dir W/S", "load", "greet", "done"]
    lines = []
    for r in data:
        lines.append([r["zone"], f"{r['lo']}-{r['hi']}", r["quests"], f"{r['types']}/7",
                      f"{r['in_chain']} ({r['longest']})", r["leaves"], f"{r['wrong']}/{r['silent']}",
                      r["load"], r["greet"], r["done"] or "-"])
    if md:
        print("| " + " | ".join(head) + " |")
        print("|" + "---|" * len(head))
        for l in lines:
            print("| " + " | ".join(str(c) for c in l) + " |")
    else:
        widths = [max(len(str(x)) for x in col) for col in zip(head, *lines)]
        for l in [head] + lines:
            print("  ".join(str(c).ljust(w) for c, w in zip(l, widths)))
    tot = lambda k: sum(r[k] for r in data)
    print(f"\n{len(data)} quest files, {tot('quests')} quests; directions: {tot('wrong')} wrong, {tot('silent')} silent; "
          f"{tot('leaves')} quests leave their zone; {tot('greet')} greetings; "
          f"{sum(1 for r in data if r['done'])} zones through the pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
