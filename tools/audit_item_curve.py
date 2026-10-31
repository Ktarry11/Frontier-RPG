#!/usr/bin/env python3
"""Every item's stats match its item level, under one formula.

    PYTHONPATH=. python3 tools/audit_item_curve.py            # audit
    PYTHONPATH=. python3 tools/audit_item_curve.py --fit      # re-fit STAT_MOD and print it
    PYTHONPATH=. python3 tools/audit_item_curve.py --list 40  # show the 40 worst

Kyle: "as long as ours has SOME formula, It can be home-brew but it MUST MUST be consistent!"

WHAT WENT WRONG WITHOUT ONE. Unbeaten's Notching Axe is the first boss of a five-boss gauntlet,
item level 39, and its stats are worth item level 21. Shelf-King's Roadbreaker is an OPEN-WORLD
drop at the same level with the same damage and the same rarity, and it is worth 39. So the
dungeon's opening reward was strictly worse than something lying around outside, and nothing
anywhere could say so, because "what should an item level 39 rare be worth" was not written
down - it only existed in whatever the author had in their head that day.

THE FIT. The five primaries cost 1.0 each by definition. Every other stat's cost was never
documented, so --fit solves for it against the items that already agree with the curve: start
from primaries only, keep the items whose implied level lands near their declared one, then
for each remaining stat pick the cost that best explains the items carrying it, and repeat.
That makes the formula a DESCRIPTION of what Frontier already does, not an import - the curve
was already in the data, it just had nowhere to live.

Fitting on the agreeing items is deliberate: fit on everything and the broken items drag the
curve toward themselves, and a formula bent to fit its own violations reports that all is well.
"""
import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from entities.item_budget import (  # noqa: E402
    PRIMARY, STAT_MOD, RARITY_MULT, SLOT_K, budget_ratio, expected_budget, slot_key, stat_value)

#: How far off its own line an item may sit before it is a finding, as a RATIO of what it is
#: allowed to spend. Deliberately relative rather than "N item levels": at level 8 a whole
#: point of Stamina moves an item several levels, so a flat tolerance reports every low-level
#: item and hides the high-level ones. 0.65-1.45 is wider than the real spread (most slots sit
#: within an interquartile band of 0.2) so what it catches is not authoring noise.
LOW, HIGH = 0.65, 1.45

ITEM_DIRS = ["data/loot", "data/items", "data/crafting", "data/leatherworking",
             "data/blacksmithing", "data/quests"]


def items():
    """Every object anywhere in the data that looks like a statted item, with where it lives."""
    out = []
    seen = set()
    for d in ITEM_DIRS:
        root = ROOT / d
        if not root.exists():
            continue
        for f in sorted(root.rglob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            stack = [data]
            while stack:
                o = stack.pop()
                if isinstance(o, dict):
                    if o.get("item_level") and o.get("rarity") in RARITY_MULT and (
                            o.get("primary_stats") or o.get("secondary_stats")):
                        key = (o.get("name"), o["item_level"], str(f))
                        if key not in seen:
                            seen.add(key)
                            out.append((o, str(f.relative_to(ROOT))))
                    stack.extend(o.values())
                elif isinstance(o, list):
                    stack.extend(o)
    return out


def fit(pool, rounds=6):
    """Solve for each non-primary stat's cost against the items that already fit the curve."""
    mods = dict(STAT_MOD)
    stats = sorted({s for it, _ in pool
                    for grp in ("primary_stats", "secondary_stats")
                    for s in (it.get(grp) or {}) if s not in PRIMARY})
    for _ in range(rounds):
        # the agreeing items define the curve; everything else is what we are trying to find
        good = [(it, src) for it, src in pool
                if (lambda r: r is not None and LOW <= r <= HIGH)(budget_ratio(it, mods))]
        if not good:
            break
        for stat in stats:
            users = [it for it, _ in good if (it.get("secondary_stats") or {}).get(stat)
                     or (it.get("primary_stats") or {}).get(stat)]
            if len(users) < 4:
                continue        # too few to fit; leave it at whatever it is
            best, best_err = mods.get(stat, 0.0), None
            for cand in [x / 200.0 for x in range(0, 4001)]:
                trial = dict(mods)
                trial[stat] = cand
                err = sorted(abs((budget_ratio(it, trial) or 0) - 1.0) for it in users)
                med = err[len(err) // 2]
                if best_err is None or med < best_err:
                    best, best_err = cand, med
            mods[stat] = best
    return mods


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fit", action="store_true")
    ap.add_argument("--list", type=int, default=0)
    args = ap.parse_args()

    pool = items()
    if not pool:
        print("no items found")
        return 1

    if args.fit:
        mods = fit(pool)
        print("STAT_MOD = {")
        print("    " + ", ".join(f'"{s}": 1.0' for s in PRIMARY) + ",")
        for s in sorted(k for k in mods if k not in PRIMARY):
            print(f'    "{s}": {mods[s]:.3f},')
        print("}")
        return 0

    mods = STAT_MOD
    unknown = defaultdict(int)
    rows = []
    for it, src in pool:
        for s in (it.get("secondary_stats") or {}):
            if s not in mods:
                unknown[s] += 1
        r = budget_ratio(it, mods)
        if r is None:
            continue
        rows.append((r, it, src))

    bad = [x for x in rows if not (LOW <= x[0] <= HIGH)]
    rows.sort(key=lambda x: x[0])

    print(f"{len(rows)} statted items checked against one curve "
          f"(allowed {LOW:.2f}-{HIGH:.2f} of their slot's budget)")
    print(f"  on curve : {len(rows) - len(bad)}  ({100 * (len(rows) - len(bad)) / max(1, len(rows)):.0f}%)")
    print(f"  off curve: {len(bad)}")
    if unknown:
        print(f"  NOT PRICED, so their items are judged on their other stats only: "
              f"{dict(sorted(unknown.items(), key=lambda kv: -kv[1]))}")

    if bad:
        under = [r for r in bad if r[0] < LOW]
        over = [r for r in bad if r[0] > HIGH]
        print(f"\n  {len(under)} under-budget (weaker than their level claims), "
              f"{len(over)} over-budget")
        by_src = defaultdict(int)
        for _d, _it, src in bad:
            by_src[src] += 1
        print("  worst files:")
        for src, n in sorted(by_src.items(), key=lambda kv: -kv[1])[:10]:
            print(f"    {n:4d}  {src}")

    if args.list:
        print(f"\n  the {args.list} furthest off curve:")
        worst = sorted(bad, key=lambda x: -abs(x[0] - 1.0))[:args.list]
        for r, it, src in worst:
            print(f"    {r * 100:5.0f}% of budget  ilvl {it['item_level']:3d} "
                  f"{slot_key(it) or '?':17s} {it.get('name', '?')[:32]:34s} {src.split('/')[-1]}")

    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
