#!/usr/bin/env python3
"""Every NPC's appearance_variant must have art on disk.

    PYTHONPATH=. python3 tools/qa_npc_appearance.py

An appearance variant is an ART DIRECTORY, not a free integer: assets/npcs/<race>/<race>_<n>/.
Point one at a number the sheet does not reach and nothing crashes - the NPC simply renders as
whatever the loader falls back to, forever, and it never appears in a diff or a test.

Three Glittervein and Abyssal NPCs shipped at 25 and 26 when the goblin sheet stops at 24. Finding
those found thirty-seven more across the game, written long before this pass, which is the real
reason this tool exists: the failure is silent, so it accumulates.

VARIANT 0 IS NOT A GAP. Twenty-five NPCs use it - Thrall, Gazlowe, most trainers - and it is the
loader's documented default rather than a missing directory.
"""
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)


def main():
    avail = {}
    for race in sorted(os.listdir("assets/npcs")):
        d = ROOT / "assets/npcs" / race
        if not d.is_dir():
            continue
        ns = {int(m.group(1)) for n in os.listdir(d)
              if (m := re.fullmatch(rf"{race}_(\d+)", n))}
        if ns:
            avail[race] = ns

    rows = []
    for path, key in (("data/npcs/vendors.json", "vendors"),
                      ("data/npcs/ambient_npcs.json", "npcs")):
        for r in json.loads((ROOT / path).read_text(encoding="utf-8"))[key]:
            race, var = r.get("race"), r.get("appearance_variant", 0)
            if race in avail and var and var not in avail[race]:
                rows.append((race, var, r.get("name"), r.get("zone")))

    if not rows:
        print("every NPC appearance variant has art on disk")
        return 0

    by = defaultdict(list)
    for (race, var, name, zone) in rows:
        by[race].append((var, name, zone))
    print(f"{len(rows)} NPC(s) point at appearance art that does not exist:\n")
    for race in sorted(by):
        top = max(avail[race])
        want = sorted({v for (v, _n, _z) in by[race]})
        print(f"  {race:11} art goes to {race}_{top:<3} | {len(by[race]):2} NPCs ask for {want}")
        for (var, name, zone) in sorted(by[race]):
            print(f"      {name or '?':34} {race}_{var}  ({zone})")
    print(f"\nEach race needs art up to its highest requested variant, or those NPCs need "
          f"renumbering into the range that exists.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
