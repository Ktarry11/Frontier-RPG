#!/usr/bin/env python3
"""Where is the game thin? Content per level band, measured rather than guessed.

    PYTHONPATH=. python3 tools/audit_content_by_level.py

Kyle, 2026-11-01: "Other than high level, where's the lowest content amount?"

Counts, for every level 1 to 60, the things a player at that level can actually
reach: zones whose creature range covers them, quests whose level_min/max admit
them, dungeons, recruits, and the vendors and trainers in those zones.

TWO THINGS THIS DELIBERATELY DOES NOT DO.

A raw count per level double-counts wide content: a zone spanning 11-27 is one
place to be, not seventeen. So each row also reports what is UNIQUE to that band
- content whose range sits mostly inside it - which is what "somewhere new to go"
actually means.

And it reports per LEVEL, not per band total, because the bands are not the same
width in play: levelling slows down, so a thin stretch at 40 hurts longer than
the same count at 10.
"""
import collections
import json
import glob
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MAX_LEVEL = 60


def zone_levels():
    d = json.load(open("data/zones/zone_levels.json"))["zones"]
    return {name: tuple(rng) for name, rng in d.items()}


def quests():
    out = []
    for p in glob.glob("data/quests/*.json"):
        d = json.load(open(p))
        for q in (d.get("quests") or []):
            lo = q.get("level_min")
            hi = q.get("level_max")
            if lo is None:
                continue
            out.append((q["quest_id"], lo, hi if hi is not None else lo))
    return out


def recruits():
    d = json.load(open("data/npcs/recruits.json"))
    block = d.get("recruits", d)
    recs = block if isinstance(block, list) else list(block.values())
    return [(r["recruit_id"], r.get("level") or r.get("recruit_level") or 1) for r in recs]


def dungeon_zones(zl):
    """Zones that are instanced content rather than open world.

    Read off data/dungeons rather than guessed from names - a 'Cave' may be a
    pocket and a 'Hollow' may be a full dungeon.
    """
    names = set()
    for p in glob.glob("data/dungeons/*.json"):
        d = json.load(open(p))
        for key in ("dungeons", "packs", "trash_packs"):
            block = d.get(key)
            if isinstance(block, dict):
                names.update(block.keys())
            elif isinstance(block, list):
                for item in block:
                    if isinstance(item, dict) and item.get("dungeon"):
                        names.add(item["dungeon"])
    return names


def main():
    zl = zone_levels()
    qs = quests()
    rs = recruits()

    per_level = collections.defaultdict(lambda: collections.Counter())
    for name, (lo, hi) in zl.items():
        for lv in range(max(1, lo), min(MAX_LEVEL, hi) + 1):
            per_level[lv]["zones"] += 1
    for _qid, lo, hi in qs:
        for lv in range(max(1, lo), min(MAX_LEVEL, hi) + 1):
            per_level[lv]["quests"] += 1
    for _rid, lv in rs:
        if 1 <= lv <= MAX_LEVEL:
            per_level[lv]["recruits"] += 1

    # Content that BELONGS to a level, so wide zones stop flattering every band
    # they touch: credit a zone to the middle of its own range.
    anchor = collections.Counter()
    for name, (lo, hi) in zl.items():
        anchor[(lo + hi) // 2] += 1
    q_anchor = collections.Counter()
    for _qid, lo, hi in qs:
        q_anchor[(lo + hi) // 2] += 1

    BANDS = [(1, 10), (11, 20), (21, 30), (31, 40), (41, 50), (51, 60)]
    print("CONTENT AVAILABLE AT EACH LEVEL (averaged within the band)\n")
    print(f"  {'band':8s} {'zones':>7s} {'quests':>8s} {'recruits':>9s}"
          f"   {'zones new':>10s} {'quests new':>11s}")
    rows = []
    for lo, hi in BANDS:
        levels = range(lo, hi + 1)
        z = statistics.mean(per_level[lv]["zones"] for lv in levels)
        q = statistics.mean(per_level[lv]["quests"] for lv in levels)
        r = sum(per_level[lv]["recruits"] for lv in levels)
        zn = sum(anchor[lv] for lv in levels)
        qn = sum(q_anchor[lv] for lv in levels)
        rows.append((lo, hi, z, q, r, zn, qn))
        print(f"  {lo:2d}-{hi:<5d} {z:7.1f} {q:8.1f} {r:9d}   {zn:10d} {qn:11d}")

    print("\nQUESTS PER LEVEL, the sharpest signal (a gap here is a grind)\n")
    worst = sorted(range(1, MAX_LEVEL + 1), key=lambda lv: per_level[lv]["quests"])
    for lv in range(1, MAX_LEVEL + 1):
        n = per_level[lv]["quests"]
        bar = "#" * min(60, n)
        flag = "   <-- thinnest" if lv in worst[:8] else ""
        print(f"  lvl {lv:2d}  {n:3d}  {bar}{flag}")

    print("\nZONES ANCHORED TO EACH BAND (somewhere genuinely new to go)")
    for lo, hi in BANDS:
        named = sorted(n for n, (a, b) in zl.items() if lo <= (a + b) // 2 <= hi)
        print(f"  {lo:2d}-{hi:<3d} {len(named):2d}  {', '.join(named[:8])}"
              + (" ..." if len(named) > 8 else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
