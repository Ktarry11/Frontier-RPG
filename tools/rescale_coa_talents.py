#!/usr/bin/env python3
"""Bring CoA talent throughput down to the WoW-Classic band the vanilla trees use.

    PYTHONPATH=. python3 tools/rescale_coa_talents.py [--apply]

Kyle, 6 Nov: "We want CoA balanced closer to WoW classic."

THE GAP IS BY HERITAGE. The nine vanilla-derived classes were authored
against real WoW numbers - Shadow Power is five ranks of 2%, same as its
namesake. The 21 CoA classes were ported from a game with far larger trees
and nobody rescaled on the way in. Measured at full rank (value x
max_points), median per family:

    family            vanilla      CoA     ratio
    pet damage          0.100    0.250     2.50x
    all damage          0.050    0.100     2.00x
    healing             0.120    0.225     1.88x
    ability damage      0.135    0.250     1.85x
    ability crit        6.000   10.000     1.67x
    ability cost        0.150    0.200     1.33x
    damage taken        0.060    0.075     1.25x
    haste               5.500    6.000     1.09x
    crit chance         5.000    4.000     0.80x

It is concentrated in THROUGHPUT - damage, healing, pet damage - which is
exactly what makes a class feel twice as strong. The utility families are
already close, and CoA is actually BELOW vanilla on flat crit chance, so
this tool leaves all of those alone. Touching them would be tidying numbers
that are not wrong.

ONE FACTOR PER FAMILY, SOLVED NOT PICKED, exactly as
tools/rescale_creature_armor.py does it:

    factor = median(vanilla full-rank) / median(CoA full-rank)

A single factor per family preserves the spread BETWEEN CoA classes and
between talents inside a tree. A Tinker stays the biggest hitter among the
CoA classes; it just stops being double a Mage.

VANILLA TREES ARE NEVER TOUCHED. They are the reference, and they are the
numbers with a real source behind them.

DESCRIPTIONS ARE REPAIRED WHERE UNAMBIGUOUS. A talent whose description
quotes exactly one percentage matching its OLD full-rank total gets that
number replaced with the new one. Where the description quotes several
numbers, or none that match, it is left alone and listed - a wrong number
is better than a confidently wrong rewrite. This matters less than it used
to: as of this session the tooltip computes "Per rank: X%  At N/N: Y%" from
effects, so the description is flavour and the computed line is the truth.
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

VANILLA = {"warrior", "rogue", "hunter", "mage", "priest",
           "paladin", "shaman", "druid", "warlock"}

#: Only the families where CoA genuinely outruns vanilla, and only the ones
#: that are throughput. Utility (cost, haste, damage taken) is within ~30%
#: already and flat crit chance is lower on CoA, so none of it is here.
FAMILIES = {
    # NOT ability_X_crit_damage - that key also ends in _damage, and crit
    # damage is a multiplier on crits, not flat throughput. Including it
    # cut 19 CoA crit-damage talents by up to 46% in 4837ce4.
    "ability damage": r"^ability_.+(?<!_crit)_damage$",
    "healing": r"healing",
    "pet damage": r"^pet_damage",
    "all damage": r"^all_damage$",
    "ability crit": r"^ability_.+_crit$",
}

PCT = re.compile(r"(\d+(?:\.\d+)?)\s*%")


def _tidy(value):
    """Round a rescaled effect to something a human would have typed.

    A solved factor produces 0.5402 and 0.1801, and a description quoting
    "16.2065%" is worse than the imbalance it fixes. Fractions keep three
    decimals (0.054 is a real 5.4% per rank); display-unit values keep one.
    """
    magnitude = abs(value)
    if magnitude < 1.0:
        return round(value, 3)
    return round(value, 1)


def load():
    docs = {}
    for path in sorted(TALENTS.glob("*.json")):
        docs[path] = json.loads(path.read_text(encoding="utf-8"))
    return docs


def family_of(key):
    for name, pattern in FAMILIES.items():
        if re.search(pattern, key):
            return name
    return None


def solve_factors(docs):
    """median(vanilla) / median(CoA), per family, at full rank."""
    totals = collections.defaultdict(lambda: collections.defaultdict(list))
    for path, doc in docs.items():
        origin = "vanilla" if path.stem.split("_")[0] in VANILLA else "CoA"
        for node in doc.get("nodes", []):
            if not isinstance(node, dict):
                continue
            ranks = node.get("max_points") or 1
            for key, value in (node.get("effects") or {}).items():
                if not isinstance(value, (int, float)) or not value:
                    continue
                family = family_of(key)
                if family:
                    totals[family][origin].append(abs(value) * ranks)

    factors = {}
    for family in FAMILIES:
        van, coa = totals[family]["vanilla"], totals[family]["CoA"]
        if len(van) < 4 or len(coa) < 4:
            print(f"  {family:16} SKIPPED - too few samples "
                  f"(vanilla {len(van)}, CoA {len(coa)})")
            continue
        mv, mc = statistics.median(van), statistics.median(coa)
        factors[family] = mv / mc
    return factors, totals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    docs = load()
    factors, totals = solve_factors(docs)

    print("solved factors (vanilla median / CoA median, at full rank):\n")
    print(f"{'family':18}{'vanilla':>10}{'CoA':>10}{'factor':>9}")
    for family, factor in factors.items():
        van = statistics.median(totals[family]["vanilla"])
        coa = statistics.median(totals[family]["CoA"])
        print(f"  {family:16}{van:>10.3f}{coa:>10.3f}{factor:>9.3f}")

    changed = collections.Counter()
    desc_fixed, desc_skipped = 0, []
    for path, doc in docs.items():
        if path.stem.split("_")[0] in VANILLA:
            continue
        for node in doc.get("nodes", []):
            if not isinstance(node, dict):
                continue
            ranks = node.get("max_points") or 1
            effects = node.get("effects") or {}
            old_totals, new_effects = {}, {}
            for key, value in effects.items():
                if not isinstance(value, (int, float)) or not value:
                    continue
                family = family_of(key)
                if family not in factors:
                    continue
                old_totals[key] = abs(value) * ranks
                new_effects[key] = _tidy(value * factors[family])
                changed[family] += 1
            if not new_effects:
                continue
            effects.update(new_effects)

            # Repair the description only when it quotes exactly one
            # percentage and that percentage is the OLD full-rank total.
            desc = node.get("description") or ""
            said = PCT.findall(desc)
            if len(said) == 1 and old_totals:
                old_pct = max(old_totals.values()) * 100
                if abs(float(said[0]) - old_pct) <= 0.75:
                    # Quote the number the player will actually see, which
                    # is the TIDIED effect times its ranks - not the raw
                    # factored figure, or the sentence and the computed
                    # tooltip line would disagree by a rounding step.
                    biggest = max(old_totals, key=old_totals.get)
                    new_pct = round(abs(new_effects[biggest]) * ranks * 100, 1)
                    node["description"] = PCT.sub(
                        lambda m: f"{new_pct:g}%", desc, count=1)
                    desc_fixed += 1
                else:
                    desc_skipped.append((path.stem, node.get("name")))
            elif said:
                desc_skipped.append((path.stem, node.get("name")))

    print(f"\n{sum(changed.values())} CoA effect values rescaled:")
    for family, count in changed.most_common():
        print(f"  {family:16}{count:>5}  (x{factors[family]:.3f})")
    print(f"\ndescriptions repaired: {desc_fixed}")
    print(f"descriptions left alone (several numbers, or no match): "
          f"{len(desc_skipped)}")
    print("  the computed tooltip line is authoritative for all of them")

    if not args.apply:
        print("\n(report only; pass --apply to write)")
        return 0
    for path, doc in docs.items():
        path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nwrote {len(docs)} talent files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
