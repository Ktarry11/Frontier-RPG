#!/usr/bin/env python3
"""Every crafting trade has something to make at skill 0, and nothing asks for exactly 1.

    PYTHONPATH=. python3 tools/qa_recipes_start_at_zero.py

Kyle, 16 Nov 2026: "we need to have these start at skill 0 so we can actually start crafting. Let's spread out
enchanting a bit from 0 to 30 as these all start at 1.... also make stange rune ink start at 0". A trade learned
through the test menu starts at 0, and a first recipe at 1 locked it out entirely. If a builder is ever re-run and
puts a first recipe back at 1, this says which.

Also holds the enchanter's first formulas to the spread Kyle asked for: at least five different skills from 0 to 30.
"""
import collections
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def main():
    from world.recipe_manager import _load_all_recipes
    by_prof = collections.defaultdict(list)
    for rid, (prof, r) in _load_all_recipes().items():
        by_prof[prof].append((int(r.get("skill_required", 0) or 0), rid))
    bad = []
    for prof, rows in sorted(by_prof.items()):
        low = min(s for s, _ in rows)
        if low != 0:
            bad.append(f"{prof}: the first recipe needs {low}, not 0")
        ones = [rid for s, rid in rows if s == 1]
        if ones:
            bad.append(f"{prof}: {len(ones)} recipe(s) need exactly 1 ({ones[:3]})")
    ench = sorted({s for s, _ in by_prof.get("enchanting", []) if s <= 30})
    if len(ench) < 5:
        bad.append(f"enchanting's first formulas sit at only {ench}; Kyle asked for a spread from 0 to 30")
    rc = dict((rid, s) for s, rid in by_prof.get("runecrafting", []))
    if rc.get("rc_rune_ink_strange") != 0:
        bad.append(f"Strange Rune Ink needs {rc.get('rc_rune_ink_strange')}, not 0")
    print(f"{len(by_prof)} trades; enchanting's first formulas at {ench}")
    if bad:
        print(f"FAIL ({len(bad)})")
        for b in bad:
            print("  -", b)
        return 1
    print("PASS - every trade starts at 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
