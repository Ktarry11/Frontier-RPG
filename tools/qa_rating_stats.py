#!/usr/bin/env python3
"""No item carries a rating that still reads as a percent.

    PYTHONPATH=. python3 tools/qa_rating_stats.py           # check
    PYTHONPATH=. python3 tools/qa_rating_stats.py --fix     # round every rating to whole points, at least 5

Kyle, 15 Nov 2026: "changing stats from % to rating where 10 rating is 1%." The switch turned every authored
percent into rating points (entities/power_scale.py), and Kyle's floor is that no rating is under 5 points (14 Nov:
"No rating under 5 points"). The guard was on the backlog and never written, and by 18 Nov 121 ratings on items had
slipped under it: curve fits scaling a rating down to 2 or 4, or leaving it fractional (+5.9 Parry Rating, +29.1
Block Rating). A 2 next to a rating reads as the old 2%, so this checks, across every item in data/:
  1. every rating stat is a whole number of points
  2. and at least MIN_RATING (5, 0.5%).
Stat-free items, gems and enchant rows aren't items with an item level and aren't read.
"""
import glob
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from entities.power_scale import RATING_KEYS  # noqa: E402
from entities.item_budget import MIN_RATING  # noqa: E402


def bad_ratings(item):
    out = []
    for group in ("primary_stats", "secondary_stats"):
        for k, v in (item.get(group) or {}).items():
            if k in RATING_KEYS and isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0:
                if not float(v).is_integer() or v < MIN_RATING:
                    out.append((group, k, v))
    return out


def walk(o, found, fix):
    n = 0
    if isinstance(o, dict):
        if o.get("item_level") and ("primary_stats" in o or "secondary_stats" in o):
            for group, k, v in bad_ratings(o):
                found.append((o.get("name", "?"), k, v))
                if fix:
                    o[group][k] = max(MIN_RATING, int(round(v)))
                    n += 1
        for v in o.values():
            n += walk(v, found, fix)
    elif isinstance(o, list):
        for v in o:
            n += walk(v, found, fix)
    return n


def main():
    fix = "--fix" in sys.argv
    found = []
    files = 0
    for f in sorted(glob.glob("data/**/*.json", recursive=True)):
        try:
            with open(f, encoding="utf-8") as fh:
                doc = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue
        before = len(found)
        changed = walk(doc, found, fix)
        if len(found) > before:
            files += 1
        if changed:
            text = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(text)
    if fix:
        print(f"rounded {len(found)} ratings in {files} files")
        return 0
    if found:
        print(f"FAIL {len(found)} ratings read as a percent (fractional, or under {MIN_RATING}) in {files} files:")
        for name, k, v in found[:20]:
            print(f"  {name}: {k} {v}")
        return 1
    print(f"rating stats OK: every rating on every item is whole points, {MIN_RATING} or more.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
