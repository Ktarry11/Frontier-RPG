#!/usr/bin/env python3
"""Per-ability damage talents are 3x stronger on CoA classes than vanilla ones.

    PYTHONPATH=. python3 tools/audit_talent_scalars.py [--key-prefix ability_]

Kyle, 6 Nov: "we REEEEEAAAALLLLY need to revamp CoA talents after this to be
more in line with class. Like shaman is 2/4/6/8/10% more lightning bolt
damage, then i look at pryomancer is like... 30/60/90% lmao"

Measured across all 97 trees, the 526 talents whose effect key matches
`ability_<id>_damage`, totalled at full rank (value x max_points):

    shaman        10.0%        barbarian     30.0%
    warlock       10.0%        knight        30.0%
    hunter        10.5%        tinker        30.0%
    priest        12.0%        necromancer   30.0%
    mage          12.5%        reaper        30.0%
    druid         12.5%        stormbringer  30.0%
    paladin       15.0%        ranger        30.0%
    rogue         20.0%        venomancer    30.0%
    warrior       20.0%        bloodmage     25.0%

THE SPLIT IS BY HERITAGE, NOT BY DESIGN. Every one of the nine
vanilla-derived classes sits at 10-20% at full rank, because they were
authored against real WoW numbers (Shadow Power is 5 ranks of 2%, and so is
its namesake). Every CoA class sits at 25-30%, because they were ported from
a game whose talent trees are an order of magnitude bigger and nobody
rescaled on the way in. It is the same failure as the creature armour
unification and the resistance rework: a scale changed and the values
authored for the old one stayed put. Third instance.

So "pyromancer is 30/60/90" is not a Pyromancer bug. Pyromancer's median is
actually 20%, BELOW its CoA peers. The bug is that the whole CoA half of the
roster is 2.5-3x the vanilla half, and a player who levels a Shaman after a
Tinker feels it immediately.

A HANDFUL OF ABSOLUTE OUTLIERS SIT ON TOP, worth fixing whichever way the
rescale goes - these are single talents granting +100% damage to an ability:

    tinker_mechanics          Turbo Upgrade!        1.00 x1
    tinker_demolition         Rockadier             1.00 x1
    priest_shadow             Shadow Power          0.20 x5
    witch_hunter_inquisition  Sinner                0.3333 x3
    tinker_demolition         Duobombers            0.3333 x3

This tool only measures. Which way to converge - pull CoA down, lift vanilla
up, or set a target band and solve per class the way
tools/rescale_creature_armor.py does - is a design call.
"""

import argparse
import collections
import json
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TALENTS = ROOT / "data/talents"

#: Trees whose class existed in WoW and was authored against real numbers.
VANILLA = {"warrior", "rogue", "hunter", "mage", "priest",
           "paladin", "shaman", "druid", "warlock"}


def collect(pattern):
    rows = []
    for path in sorted(TALENTS.glob("*.json")):
        tree = path.stem
        cls = tree.split("_")[0]
        for node in json.loads(path.read_text()).get("nodes", []):
            if not isinstance(node, dict):
                continue
            ranks = node.get("max_points") or node.get("max_rank") or 1
            for key, value in (node.get("effects") or {}).items():
                if not isinstance(value, (int, float)) or not value:
                    continue
                if pattern.match(key):
                    rows.append(dict(cls=cls, tree=tree, name=node.get("name"),
                                     key=key, per_rank=value, ranks=ranks,
                                     total=round(value * ranks, 4)))
    return rows


PCT = re.compile(r"(\d+(?:\.\d+)?)\s*%")


def audit_descriptions():
    """Does a multi-rank talent's description state the PER-RANK value or
    the FULL-RANK TOTAL, and does it say which?

    This is the bug Kyle actually hit. Pyromancer's Searing Flames stores
    0.1 across 3 ranks - a sane 30% total - and describes itself as
    "Increases the damage of Lava Shard by 30%." Shaman's Lightning Mastery
    stores 0.02 across 5 ranks and describes itself as "...by 2% PER RANK".

    Both numbers are honest. The conventions are not the same, and a player
    who learned the Shaman phrasing reads 30% on a 0/3 node as 30/60/90.
    """
    tol = 0.75  # percentage points, to absorb 0.1167 x 3 = 35.01 vs "35%"
    buckets = collections.Counter()
    mismatched = []
    offenders = collections.Counter()
    for path in sorted(TALENTS.glob("*.json")):
        tree = path.stem
        for node in json.loads(path.read_text()).get("nodes", []):
            if not isinstance(node, dict):
                continue
            ranks = node.get("max_points") or 1
            if ranks < 2:
                continue
            desc = node.get("description") or ""
            said = [float(x) for x in PCT.findall(desc)]
            vals = [abs(v) for v in (node.get("effects") or {}).values()
                    if isinstance(v, (int, float)) and v]
            if not said or not vals:
                continue
            says_per_rank = "per rank" in desc.lower()
            kind = None
            for v in vals:
                for scale in (100, 1):
                    if any(abs(x - v * scale) <= tol for x in said):
                        kind = "per_rank"
                        break
                    if any(abs(x - v * ranks * scale) <= tol for x in said):
                        kind = "total"
                        break
                if kind:
                    break
            if kind is None:
                kind = "neither"
                mismatched.append((tree, node.get("name"), said, vals[:2], ranks))
            buckets[f"{kind}/{'per rank' if says_per_rank else 'bare'}"] += 1
            if kind == "total" and not says_per_rank:
                offenders[tree.split("_")[0]] += 1

    total = sum(buckets.values())
    print(f"\n{total} multi-rank talents state a percentage in their "
          f"description\n")
    for key, count in buckets.most_common():
        print(f"  {count:>5} ({count / total:4.0%})  {key}")

    amb = buckets["total/bare"]
    print(f"\n  {amb} ({amb / total:.0%}) state the FULL-RANK TOTAL with no "
          f"'per rank' qualifier.")
    van = sum(n for c, n in offenders.items() if c in VANILLA)
    coa = sum(n for c, n in offenders.items() if c not in VANILLA)
    print(f"  vanilla classes: {van}      CoA classes: {coa}")
    if van == 0:
        print("  The split is total: every vanilla class says 'per rank', "
              "no CoA class does.")
    print("  worst:", ", ".join(f"{c} {n}" for c, n in offenders.most_common(8)))

    print(f"\n  {len(mismatched)} descriptions match NEITHER reading - real "
          f"data bugs, not convention:")
    for tree, name, said, vals, ranks in mismatched:
        print(f"    {tree:26}{str(name)[:24]:26}says {said}  data {vals} x{ranks}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--descriptions", action="store_true",
                    help="audit per-rank vs total wording instead of magnitudes")
    ap.add_argument("--pattern", default=r"ability_(.+)_damage$",
                    help="effect-key regex to audit (default: per-ability damage)")
    args = ap.parse_args()

    if args.descriptions:
        audit_descriptions()
        return 0

    rows = collect(re.compile(args.pattern))
    if not rows:
        print(f"no effect keys match {args.pattern!r}")
        return 1

    by_class = collections.defaultdict(list)
    for r in rows:
        by_class[r["cls"]].append(r["total"])

    print(f"{len(rows)} talents match {args.pattern!r}, "
          f"across {len(by_class)} classes\n")
    print(f"{'class':16}{'origin':10}{'n':>4}{'median':>9}{'min':>8}{'max':>8}")
    groups = collections.defaultdict(list)
    for cls, totals in sorted(by_class.items(),
                              key=lambda x: statistics.median(x[1])):
        origin = "vanilla" if cls in VANILLA else "CoA"
        groups[origin].append(statistics.median(totals))
        print(f"  {cls:14}{origin:10}{len(totals):>4}"
              f"{statistics.median(totals):>9.1%}"
              f"{min(totals):>8.0%}{max(totals):>8.0%}")

    print()
    for origin in ("vanilla", "CoA"):
        meds = groups[origin]
        if meds:
            print(f"  {origin:8} classes: median of medians "
                  f"{statistics.median(meds):.1%}  "
                  f"(range {min(meds):.0%} - {max(meds):.0%})")
    if groups["vanilla"] and groups["CoA"]:
        ratio = statistics.median(groups["CoA"]) / statistics.median(groups["vanilla"])
        print(f"\n  CoA classes are {ratio:.1f}x the vanilla classes at full rank.")

    print("\noutliers - single talents at or above +45% to one ability:")
    seen = set()
    for r in sorted(rows, key=lambda r: -r["total"]):
        if r["total"] < 0.45:
            break
        sig = (r["tree"], r["name"])
        if sig in seen:
            continue
        seen.add(sig)
        print(f"  {r['total']:>6.0%}  {r['tree']:26}{str(r['name'])[:26]:28}"
              f"{r['per_rank']} x{r['ranks']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
