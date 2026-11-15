#!/usr/bin/env python3
"""Do every class's abilities grow sensibly from the level they're learned to 60?

    PYTHONPATH=. python3 tools/audit_ability_ranks.py [--class Mage] [--verbose]

Kyle, 15 Nov 2026: "There's very little skill difference between lvl 15 skills and lvl 60." and "You'll be
spending almost all day fixing classes. All 9 classic classes and coa classes. All specs, ability ranks....."

Reads the authored ranks (data/abilities/*.json, what a fix edits) with the level curve from
combat/ability_scaling.py applied, because that's what a player casts. Basic attacks are skipped. For every ability whose effect_value is a
strength (damage, heals, DoTs, HoTs):

  stalls      learned by 40 but its last rank is learned before 40, so it stops growing for 20+ levels
              while everything around it keeps going
  few ranks   learned by 20 with fewer than 3 ranks: one or two numbers have to cover 40 levels
  gap         two ranks more than 14 levels apart
  wobble      a later rank is weaker than an earlier one, or costs less
  level order ranks not in level order, or two ranks at one level
  flat        grows less than its level does: top rank / first rank < (top level + 10) / (first level + 10)
  cost        a rank that does 2x+ the work for the same cost as the one before, or a cost that rises much
              faster than the effect
"""
import argparse
import glob
import json
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

CURVED = {"damage", "spell_damage", "ranged_damage", "dot", "spell_dot", "heal", "hot", "damage_and_heal",
          "damage_and_restore_mana"}
CLASSIC = {"warrior", "rogue", "hunter", "mage", "warlock", "priest", "shaman", "druid", "paladin"}


def abilities(only=None):
    for path in sorted(glob.glob("data/abilities/*.json")):
        cls = os.path.basename(path)[:-5]
        if cls.startswith("_") or cls == "asher_unique" or (only and cls != only):
            continue
        d = json.load(open(path, encoding="utf-8"))
        L = d if isinstance(d, list) else d.get("abilities", d)
        for a in (L.values() if isinstance(L, dict) else L):
            if isinstance(a, dict) and a.get("ranks") and not str(a.get("ability_id", "")).endswith("_attack"):
                yield cls, a


def findings(a):
    out = []
    ranks = a["ranks"]
    et = a.get("effect_type")
    levels = [r.get("level_req", 0) for r in ranks]
    if levels != sorted(levels) or len(set(levels)) != len(levels):
        out.append(("level order", f"levels {levels}"))
    if et not in CURVED:
        return out
    # what a player gets: the authored ranks with the level curve on top (combat/ability_scaling.py)
    from combat.ability_scaling import curved_ranks
    ranks = curved_ranks(a)
    first, last = ranks[0], ranks[-1]
    lv0, lv1 = first["level_req"], last["level_req"]
    ev = [r.get("effect_value", 0) or 0 for r in ranks]
    cost = [r.get("cost", 0) or 0 for r in ranks]
    talent = a.get("requires_talent")
    if lv0 <= 40 and lv1 < 40 and lv0 < 60:
        out.append(("stalls", f"learned {lv0}, last rank at {lv1}"))
    if lv0 <= 20 and len(ranks) < 3 and not talent:
        out.append(("few ranks", f"{len(ranks)} rank(s) from {lv0}"))
    for (a_lv, b_lv) in zip(levels, levels[1:]):
        if b_lv - a_lv > 14:
            out.append(("gap", f"{a_lv} -> {b_lv}"))
            break
    if any(b < a for a, b in zip(ev, ev[1:])):
        out.append(("wobble", f"effect {ev}"))
    if any(b < a for a, b in zip(cost, cost[1:])):
        out.append(("wobble", f"cost {cost}"))
    if len(ranks) > 1 and ev[0] and ev[-1] / ev[0] < (lv1 + 10) / (lv0 + 10) * 0.9:
        out.append(("flat", f"{ev[0]} at {lv0} -> {ev[-1]} at {lv1} ({ev[-1] / ev[0]:.1f}x over "
                            f"{(lv1 + 10) / (lv0 + 10):.1f}x of level)"))
    for i in range(1, len(ranks)):
        if ev[i - 1] and cost[i - 1] and cost[i]:
            work = ev[i] / ev[i - 1]
            price = cost[i] / cost[i - 1]
            if work >= 2 and price <= 1.05:
                out.append(("cost", f"rank {i + 1} does {work:.1f}x for {price:.2f}x the cost"))
                break
            if price > work * 1.6 and price > 1.5:
                out.append(("cost", f"rank {i + 1} costs {price:.1f}x for {work:.1f}x the effect"))
                break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--class", dest="only")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    per_class = defaultdict(lambda: defaultdict(list))
    seen = defaultdict(int)
    for cls, a in abilities(args.only):
        if a.get("effect_type") in CURVED:
            seen[cls] += 1
        for kind, detail in findings(a):
            per_class[cls][kind].append(f"{a['name']} ({a['ability_id']}): {detail}")
    kinds = ["stalls", "few ranks", "flat", "gap", "wobble", "level order", "cost"]
    print(f"{'class':<18} {'scaled':>6} " + " ".join(f"{k:>11}" for k in kinds))
    total = defaultdict(int)
    for cls in sorted(seen, key=lambda c: (c not in CLASSIC, c)):
        row = per_class[cls]
        for k in kinds:
            total[k] += len(row[k])
        print(f"{('*' if cls in CLASSIC else ' ') + cls:<18} {seen[cls]:>6} " +
              " ".join(f"{len(row[k]) or '':>11}" for k in kinds))
    print(f"{'TOTAL':<18} {sum(seen.values()):>6} " + " ".join(f"{total[k]:>11}" for k in kinds))
    print("  * = classic class")
    if args.verbose or args.only:
        for cls in sorted(per_class):
            print(f"\n=== {cls}")
            for k in kinds:
                for line in per_class[cls][k]:
                    print(f"  {k:<11} {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
