#!/usr/bin/env python3
"""Make creature armour mean something again.

    PYTHONPATH=. python3 tools/rescale_creature_armor.py [--apply] [--target N]

WHAT WENT WRONG. Monsters used to mitigate physical damage on their own
inline curve, `rating / (rating + 100)`, and every template's base_armor was
authored against it - 27 armour really was 21%, and 56 was 36%. That curve
was then unified onto Character's, under a comment that is entirely right
about why:

    "ONE CURVE FOR EVERYONE. This used to be its own inline
     `rating / (rating + 100)`, a second copy of a formula Character already
     owned, and when that formula changed to scale with attacker level the
     two would silently have disagreed."

The unification was correct and the rescale that had to come with it never
did. Character's curve is `rating / (rating + 200 + 35*level)`, whose
denominator at level 60 is 2300 against the old 100, so every creature's
armour quietly became decorative. Measured across all 1102:

    level band   median armour   mitigates
      0-9             11           2.8%
     20-29            34           3.1%
     40-49            56           3.1%
     50-59            59           2.7%

against a level 13 companion TANK at 644 armour and 49.6%. Players were
roughly 24 times better armoured than the things they fight, and 100% armor
penetration against a Vile Plague Abomination moved a 1000-damage hit from
951 to 1000 - which is why armor penetration could not be a gear stat.

THE MULTIPLIER IS DERIVED, NOT PICKED. Both sides are linear in level -
armour is base * (1 + 0.15*(level-1)) and the denominator is 200 + 35*level
- so the shortfall is near-constant at every level and ONE factor fixes the
whole curve. It is solved for a target mitigation on the reference template
rather than typed:

    armour needed = target/(1-target) * (200 + 35*level)
    factor        = needed / (what humanoid_warrior carries today)

Kyle, 6 Nov, having been shown this costs ~25-30% of all physical damage
against creatures: "Thats fine, we can have longer fights."

THE SPREAD BETWEEN TEMPLATES IS PRESERVED, because the factor is applied to
every base_armor equally. A vermin_swarm stays the squishiest thing in the
game and an elemental_bruiser stays the hardest; they just both land
somewhere a player can feel.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "data/creatures/templates.json"

#: The template the factor is solved against - the ordinary armoured
#: humanoid, which is what most of the game's enemies are.
REFERENCE = "humanoid_warrior"
#: What that reference should mitigate once this is done.
DEFAULT_TARGET = 0.30
#: The level the solve is done at. Any level gives nearly the same factor
#: (both sides are linear), and 60 is where the numbers are largest and so
#: where being wrong would show most.
SOLVE_LEVEL = 60

#: Monster.__init__: base_armor = template["base_armor"] * level_mult
LEVEL_MULT_PER_LEVEL = 0.15


def level_mult(level):
    return 1.0 + (level - 1) * LEVEL_MULT_PER_LEVEL


def denominator(level):
    """Character.mitigation_from's denominator - MITIGATION_BASE +
    MITIGATION_PER_LEVEL * level. Read from Character so a change there
    cannot leave this tool describing a curve the game no longer uses."""
    from entities.character import Character
    return Character.MITIGATION_BASE + Character.MITIGATION_PER_LEVEL * level


def mitigation(armor, level):
    from entities.character import Character
    return Character.mitigation_from(armor, level)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--target", type=float, default=DEFAULT_TARGET,
                    help=f"mitigation the {REFERENCE} should reach "
                         f"(default {DEFAULT_TARGET})")
    args = ap.parse_args()

    doc = json.loads(TEMPLATES.read_text())
    tmpl = doc.get("templates", doc)

    ref_base = tmpl[REFERENCE]["base_armor"]
    have = ref_base * level_mult(SOLVE_LEVEL)
    need = args.target / (1 - args.target) * denominator(SOLVE_LEVEL)
    factor = need / have

    print(f"solving on {REFERENCE} at level {SOLVE_LEVEL}:")
    print(f"  carries today   {have:.0f} armour  ->  "
          f"{mitigation(have, SOLVE_LEVEL):.1%}")
    print(f"  wants           {need:.0f} armour  ->  {args.target:.1%}")
    print(f"  factor          x{factor:.2f}\n")

    print(f"{'template':20}{'base':>6}{'->':>5}"
          f"{'  mitigation at 15':>20}{'  at 40':>10}{'  at 60':>10}")
    for key in sorted(tmpl):
        old = tmpl[key]["base_armor"]
        new = max(1, round(old * factor))
        cells = ""
        for lv in (15, 40, 60):
            before = mitigation(old * level_mult(lv), lv)
            after = mitigation(new * level_mult(lv), lv)
            cells += f"  {before:5.1%} -> {after:5.1%}"
        print(f"{key:20}{old:>6}{new:>5}{cells}")
        tmpl[key]["base_armor"] = new

    print(f"\n...and what armor penetration is then worth, against the "
          f"{REFERENCE} at 60:")
    base = tmpl[REFERENCE]["base_armor"] * level_mult(SOLVE_LEVEL)
    full = mitigation(base, SOLVE_LEVEL)
    for pct in (0.0, 0.10, 0.20, 0.30, 0.50):
        m = mitigation(base * (1 - pct), SOLVE_LEVEL)
        print(f"  {pct:4.0%} penetration -> target mitigates {m:5.1%}, "
              f"a 1000-damage hit lands for {1000*(1-m):6.0f} "
              f"(+{1000*(full-m):.0f} over no penetration)")

    if not args.apply:
        print("\n(report only; pass --apply to write)")
        return 0
    TEMPLATES.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    print(f"\nwrote {TEMPLATES}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
