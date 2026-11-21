#!/usr/bin/env python3
"""Every recruit in the world has everything.

    PYTHONPATH=. python3 tools/qa_recruit_complete.py

Kyle, 21 Nov 2026: "If they're in the game, they need it. Any and all recruits must have everything when
added in the world." Everything is the full set the four waves make:

  Wave 1   a profile in docs/recruits/, listed in its README, and a personal kit
  Wave 2   a bond (data/npcs/bonds.json) and party banter (data/banter/lines.json)
  Wave 3   traits and lines (data/npcs/relationships.json)
  Wave 4   a Sworn skill (data/npcs/sworn_skills.json) and a keepsake (data/npcs/keepsakes.json)

A recruit placed without one of these fails here, so nobody goes into the world half written. Asher is
never touched, so he's left out.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDED = {"asher_coleman", "asher_paladin", "asher"}


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main():
    recruits = [r for r in load("data/npcs/recruits.json")["recruits"] if r["recruit_id"] not in EXCLUDED]
    have = {
        "personal kit": set(load("data/npcs/personal_kits.json")),
        "bond": set(load("data/npcs/bonds.json")["bonds"]),
        "banter": set(load("data/banter/lines.json")["lines"]),
        "Wave 3 traits": set(load("data/npcs/relationships.json")["traits"]),
        "Sworn skill": set(load("data/npcs/sworn_skills.json")),
        "keepsake": set(load("data/npcs/keepsakes.json")["keepsakes"]),
    }
    readme = (ROOT / "docs/recruits/README.md").read_text(encoding="utf-8")
    rows = {}
    for m in re.finditer(r"^\| \d+ \| ([^|]+?) \| [^|]+ \| [^|]+ \| `([^`]+\.md)` \|", readme, re.M):
        rows[m.group(1).strip()] = m.group(2)

    problems = []
    for r in recruits:
        rid, name = r["recruit_id"], r["name"]
        missing = [what for what, ids in have.items() if rid not in ids]
        doc = rows.get(name)
        if doc is None:
            missing.append("a README row")
        elif not (ROOT / "docs/recruits" / doc).exists():
            missing.append(f"its profile ({doc})")
        if missing:
            problems.append(f"{rid} ({name}) has no {', '.join(missing)}")

    for p in problems:
        print("  -", p)
    if problems:
        print(f"{len(problems)} recruit(s) aren't complete")
        return 1
    print(f"recruits complete: all {len(recruits)} have a profile, kit, bond, banter, Wave 3 traits, "
          f"Sworn skill and keepsake")
    return 0


if __name__ == "__main__":
    sys.exit(main())
