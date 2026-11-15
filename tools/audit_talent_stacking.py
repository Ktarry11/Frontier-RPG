#!/usr/bin/env python3
"""How much does a full talent tree pile onto ONE ability? Per-ability bonuses summed at max points.

    PYTHONPATH=. python3 tools/audit_talent_stacking.py [--limit 0.30]

Found 15 Nov 2026 (Kyle's check of four spells): Restoration's talents put +39% on Healing Wave alone (Improved
Healing Wave 5x3% + Healing Way 3x8%; Classic's Healing Way is 18% and Improved Healing Wave is cast time), while
Holy Light gets +12%: same data, same coefficient, and a geared Healing Wave healed 2x a Holy Light. The spec auras
level a spec's TOTAL, so a stacked button makes the rest of the kit weak beside it. This lists every ability whose
summed per-ability talent bonus (ability_<id>_damage / _healing, at max points, across ALL of its class's trees)
passes --limit.

REPORT ONLY (tried and reverted, 15 Nov): an automatic cap at +60% per tree garbles the data - several nodes
share one number across two abilities (Rockadier, Turbo Upgrade!, Master Mixologist) and the biggest stacks are CoA
capstones that transform the ability (Jungle Booms, Turbo Upgrade!, Rockadier). Only 8 abilities pass +60% within
one tree; any trim is a hand edit, node by node, with its description.
"""
import argparse
import collections
import glob
import json
import os
import re
import sys

PER = re.compile(r"^ability_(.+)_(damage|healing)$")


def nodes_of(d):
    n = d.get("nodes") or d.get("talents") or d
    return n if isinstance(n, list) else [x for x in n.values() if isinstance(x, dict)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=float, default=0.30)
    args = ap.parse_args()
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    per = collections.defaultdict(list)
    for f in sorted(glob.glob("data/talents/*.json")):
        tree = os.path.basename(f)[:-5]
        for n in nodes_of(json.load(open(f, encoding="utf-8"))):
            mp = n.get("max_points") or 1
            for k, v in (n.get("effects") or {}).items():
                m = PER.match(k)
                if m and isinstance(v, (int, float)):
                    per[(m.group(1), m.group(2))].append((tree, n.get("name"), mp, v, v * mp))
    rows = sorted(((sum(x[4] for x in lst), aid, kind, lst) for (aid, kind), lst in per.items()), reverse=True)
    hi = [r for r in rows if r[0] > args.limit + 1e-9]
    print(f"{len(rows)} abilities have per-ability talent bonuses; {len(hi)} pass +{args.limit:.0%}:")
    for tot, aid, kind, lst in hi:
        print(f"  +{tot:4.0%} {kind:<7} {aid:<40} " + "; ".join(f"{t.split('_',1)[-1]}/{nm} {mp}x{v:g}" for t, nm, mp, v, _ in lst))
    return 0


if __name__ == "__main__":
    sys.exit(main())
