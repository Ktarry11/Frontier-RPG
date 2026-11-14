#!/usr/bin/env python3
"""Quests come from hubs, not from the spot where the work is.

    PYTHONPATH=. python3 tools/qa_quest_hubs.py

Kyle (backlog [69] + [74]): "I want towns to feel more like hubs people bother to return to," and
"a huge issue ... is that NPCs for quests are placed RIGHT at that subzone, this is... lame."

The rule: about 70% of a region's quests are handed out in its towns, so a quest sends you out and
you come back to turn it in. The rest can come from people who belong in the wild (a road
traveller, a ferryman, a gate guard).

WHAT IS CHECKED. For each region below, every quest whose zone is one of the region's quest zones
is counted, by where its giver stands:
  - in town: the giver's zone is one of the region's hub zones (Razor Hill, Brill, the Undercity),
    or the giver stands within the radius of a hub that sits inside a bigger map (the March in
    Silverpine South);
  - in the wild: anywhere else.
Quests that start from an item you loot have no giver and are left out.

A region listed in FLOORS must have at least that share from town. Raise a floor when a region is
moved; never lower one. Every other region is printed so the next one to fix is easy to see.
"""
import glob
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

#: region -> (quest zones, hub zones, hubs inside a bigger map: {zone: [(x, y, radius)]})
REGIONS = {
    "Durotar": (["durotar", "razor_hill"], ["razor_hill", "orgrimmar"], {}),
    "Tirisfal": (["western_tirisfal", "eastern_tirisfal", "brill"], ["brill", "undercity", "deathknell"], {}),
    "Silverpine": (["silverpine_north", "silverpine_south", "sepulcher"], ["sepulcher"],
                   {"silverpine_south": [(75, 48, 16)], "silverpine_north": [(84, 15, 10)]}),
    # The Barrens and Hillsbrad are next. They have hubs INSIDE their maps (the Barrens hub files),
    # so they need their inner hub points measured before their numbers mean anything.
}
#: the share of a region's quests that must come from town. Never lower one.
FLOORS = {"Durotar": 0.70, "Tirisfal": 0.70, "Silverpine": 0.70}


def norm(s):
    return (s or "").lower().replace(" ", "_").replace("'", "")


def main():
    people = {}
    for n in json.loads(Path("data/npcs/ambient_npcs.json").read_text(encoding="utf-8"))["npcs"]:
        people[n["npc_id"]] = n
    for v in json.loads(Path("data/npcs/vendors.json").read_text(encoding="utf-8"))["vendors"]:
        people.setdefault(v["vendor_id"], v)
    quests = [q for f in sorted(glob.glob("data/quests/*.json"))
              for q in json.loads(Path(f).read_text(encoding="utf-8"))["quests"]]

    bad = []
    for region, (qzones, hubs, inner) in REGIONS.items():
        town = wild = 0
        wild_givers = Counter()
        for q in quests:
            if norm(q.get("zone")) not in qzones:
                continue
            g = q.get("giver_npc_id") or ""
            if g.startswith("item:"):
                continue
            n = people.get(g)
            if n is None:
                bad.append(f"{region}: {q['quest_id']} is given by {g}, who does not exist")
                continue
            z = norm(n.get("zone"))
            in_town = z in hubs or any(abs(n.get("x", -99) - x) + abs(n.get("y", -99) - y) <= r
                                       for x, y, r in inner.get(z, []))
            if in_town:
                town += 1
            else:
                wild += 1
                wild_givers[f"{g} ({z})"] += 1
        total = town + wild
        share = town / total if total else 1.0
        floor = FLOORS.get(region)
        mark = "" if floor is None else (" ok" if share >= floor else " BELOW FLOOR")
        print(f"{region:11} {town:3}/{total:<3} from town ({share:.0%})"
              + (f", floor {floor:.0%}{mark}" if floor else ""))
        if floor is not None:
            for who, k in wild_givers.most_common():
                print(f"              in the wild: {who} x{k}")
            if share < floor:
                bad.append(f"{region}: only {share:.0%} of quests come from town (floor {floor:.0%})")

    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad:
            print("  -", b)
        return 1
    print("\nQuest hubs OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
