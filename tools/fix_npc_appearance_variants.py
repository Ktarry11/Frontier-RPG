#!/usr/bin/env python3
"""Point every NPC at appearance art that exists.

    PYTHONPATH=. python3 tools/fix_npc_appearance_variants.py [--apply]

WHAT WAS WRONG. tools/qa_npc_appearance.py: 40 NPCs across four races carry
an appearance_variant with no art directory behind it. An appearance variant
is a folder (assets/npcs/<race>/<race>_<n>/), not a free integer, so these
NPCs render with nothing - and the number kept climbing because each zone
pass numbered its new people on from wherever the last pass stopped, with
nothing checking the count on disk:

    blood_elf   art 1-11   asked for up to 22   (12 NPCs)
    forsaken    art 1-16   asked for up to 21   ( 9 NPCs)
    orc         art 1-22   asked for 23 and 24  ( 2 NPCs)
    tauren      art 1-20   asked for up to 36   (16 NPCs)
    troll       art 1-20   asked for 23         ( 1 NPC)

THE CHOICE IS REUSE OR BLANK, and reuse wins. The script's own suggestion is
"those NPCs need renumbering into the range that exists", and the alternative
- 46 new art variants - is Kyle's art pipeline, not something a tool can
produce. Ambient NPCs reusing a body is ordinary; a whole Tauren town
rendering as nothing is not.

REUSE IS SPREAD WITHIN A ZONE, not taken modulo. A plain `(var - 1) % n + 1`
would have mapped tauren_21..36 straight back onto 1..16, and since those
were already in use at Freewind Post it would have put two identical Tauren
on half the stalls in one square. Each NPC instead takes the variant that
appears LEAST often in its own zone, so a zone only repeats a body once it
has used every one it has. Ties break on the lowest number and the NPCs are
visited in id order, so the result is the same every run.
"""

import argparse
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = (("data/npcs/vendors.json", "vendors"),
         ("data/npcs/ambient_npcs.json", "npcs"))


def art_on_disk():
    avail = {}
    for race in sorted(os.listdir(ROOT / "assets/npcs")):
        d = ROOT / "assets/npcs" / race
        if not d.is_dir():
            continue
        ns = {int(m.group(1)) for n in os.listdir(d)
              if (m := re.fullmatch(rf"{race}_(\d+)", n))}
        if ns:
            avail[race] = ns
    return avail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    avail = art_on_disk()
    loaded = [(path, key, json.loads((ROOT / path).read_text(encoding="utf-8")))
              for path, key in FILES]

    # What each zone already uses, counted only over NPCs whose variant is
    # real - a broken one is about to move and should not weight the spread.
    in_use = Counter()
    for _path, key, data in loaded:
        for r in data[key]:
            race, var = r.get("race"), r.get("appearance_variant", 0)
            if race in avail and var in avail[race]:
                in_use[(r.get("zone"), race, var)] += 1

    moves = []
    for _path, key, data in loaded:
        for r in sorted(data[key], key=lambda x: str(x.get("npc_id")
                                                     or x.get("vendor_id") or x.get("name"))):
            race, var = r.get("race"), r.get("appearance_variant", 0)
            if race not in avail or not var or var in avail[race]:
                continue
            zone = r.get("zone")
            pick = min(sorted(avail[race]),
                       key=lambda n: (in_use[(zone, race, n)], n))
            in_use[(zone, race, pick)] += 1
            r["appearance_variant"] = pick
            moves.append((race, r.get("name"), zone, var, pick))

    by_race = Counter(m[0] for m in moves)
    print(f"{len(moves)} NPC(s) repointed at art that exists")
    for race, n in sorted(by_race.items()):
        print(f"  {race:11} {n:2} moved, into art 1-{max(avail[race])}")
    print()
    for race, name, zone, old, new in moves:
        print(f"  {str(name):34} {race}_{old} -> {race}_{new:<3} ({zone})")

    if not args.apply:
        print("\n(report only; pass --apply to write)")
        return 0
    for path, _key, data in loaded:
        (ROOT / path).write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\nwrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
