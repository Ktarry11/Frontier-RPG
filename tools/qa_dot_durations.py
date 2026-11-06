#!/usr/bin/env python3
"""A dot or hot must fit inside the fights the game actually has.

    PYTHONPATH=. python3 tools/qa_dot_durations.py [--report]

WHY THERE IS A CEILING AT ALL, and where the number comes from.

effect_value on a dot rank is the TOTAL damage across the whole duration,
and per-turn potency is that divided by duration (abilities.py:2695). So a
dot only pays out in full if the fight lasts at least as long as the dot.
Any turn of duration past the end of the fight is damage that never
happens.

FIGHT LENGTH WAS MEASURED, NOT ASSUMED. tools/sim_class_balance.py plays
real fights through CombatEngine with real gear, and a boss-multiplier run
(2.5x health, per world/creature_manager.py) covers the long end:

    trash, level 20    median 3.0 turns   p90 5    max 9
    trash, level 40    median 3.0         p90 4    max 6
    trash, level 60    median 2.0         p90 4    max 9
    boss,  level 20    median 6.5         p90 10   max 15
    boss,  level 40    median 6.0         p90 10   max 14
    boss,  level 60    median 5.0         p90 8    max 13

Realised damage for a dot applied on turn one, against those
distributions:

    2 turns   100% trash / 100% boss      3 turns    91% / 100%
    4 turns    78% /  98%                 5 turns    66% /  94%
    6 turns    57% /  88%                 8 turns    44% /  75%
   10 turns    35% /  63%

THAT IS WHY CoA'S OWN NUMBERS CANNOT BE PORTED. CoA writes 18-24 second
dots because it is a group MMO with long fights. Translated literally at
~3 seconds per turn those become 6-8 turns, which in Frontier delivers
under half their damage. Chronomancer's dots were lengthened to 8-10 turns
on 6 Nov 2026 on exactly that reasoning and had to be reversed the same
day once the fights were measured - the change had made the class worse
than before it was touched.

THE TAXONOMY, five buckets, ceiling 6:

    2  burst          emergency AoE heal, delayed nuke. Fat ticks, always
                      completes. Wild Growth, Gravity Bomb.
    3  standard       the workhorse default. Rejuvenation, Rake, Starfall.
    4  tail           a direct effect with a trailing one, or a bleed you
                      reapply. Regrowth, Moonfire, Timerend.
    5  sustained      the dot-class signature. Decomposition.
    6  boss finisher  the ceiling. Melt Reality. Nothing longer.

Duration is a spell's IDENTITY, not a number to normalise - Kyle,
5 Nov 2026: "we KNOW rejuv should not be the same duration as regrowth or
wild growth etc." He was right, and ours had Regrowth tied for shortest.
Because per-turn derives from duration, the bucket IS the burst-versus-
throughput dial: hold the total and a short dot hits hard and fast, a long
one trickles.

WHAT THIS REPORTS: anything outside 2-6, which is a real design error, and
with --report the whole distribution so a pass over the remaining dots has
somewhere to start. It does NOT try to police which bucket a given spell
belongs in - that is a judgement about the spell's role, and a checker that
guessed at it would be wrong constantly.
"""

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: Measured window. Below 2 a "dot" is a direct hit wearing a dot's
#: clothing; above 6 it cannot finish even a boss fight's median.
FLOOR, CEILING = 2, 6

#: Realised fraction of a dot's total, by duration, from the measured
#: fight-length distributions. Used for the report, not the pass/fail.
REALISED = {1: (1.00, 1.00), 2: (1.00, 1.00), 3: (0.91, 1.00),
            4: (0.78, 0.98), 5: (0.66, 0.94), 6: (0.57, 0.88),
            7: (0.50, 0.80), 8: (0.44, 0.75), 9: (0.39, 0.69),
            10: (0.35, 0.63)}

BUCKETS = {2: "burst", 3: "standard", 4: "tail", 5: "sustained",
           6: "boss-finisher"}

#: Deliberate exceptions, each with a reason. A long effect that is not
#: really a damage/healing dot does not have to fit the damage window.
ALLOW = {
    # Not a dot in play: a maintained stance whose "duration" is just how
    # long the stance lasts, with no per-turn total to lose.
    "chronomancer_arc_collision": None,  # placeholder, removed below
}
ALLOW = {}


def realised(duration):
    return REALISED.get(duration, (0.30, 0.55))


def main():
    report = "--report" in sys.argv
    rows, bad = [], []
    for path in sorted((ROOT / "data/abilities").glob("*.json")):
        for a in json.loads(path.read_text()).get("abilities", []):
            if a.get("effect_type") not in ("dot", "spell_dot", "hot"):
                continue
            d = a.get("duration") or 0
            rows.append((path.stem, a["ability_id"], a["effect_type"], d))
            if a["ability_id"] in ALLOW:
                continue
            if d < FLOOR or d > CEILING:
                bad.append((path.stem, a["ability_id"], a["effect_type"], d))

    dist = Counter(d for *_, d in rows)
    print(f"  {len(rows)} dot/hot abilities across "
          f"{len(set(r[0] for r in rows))} classes")
    print(f"  window {FLOOR}-{CEILING} turns, measured from real fights "
          f"(trash 2-3, boss 5-6)")

    if report:
        print("\n  duration   count   bucket          realised trash/boss")
        for d in sorted(dist):
            t, b = realised(d)
            flag = "" if FLOOR <= d <= CEILING else "   <-- OUT OF WINDOW"
            print(f"  {d:>8}   {dist[d]:>5}   "
                  f"{BUCKETS.get(d, '-'):<14}  {t:>7.0%} / {b:<5.0%}{flag}")
        spread = sum(1 for d in dist if FLOOR <= d <= CEILING)
        print(f"\n  {spread} of {len(dist)} distinct durations are in window")

    if not bad:
        print(f"\n  0 OUTSIDE THE {FLOOR}-{CEILING} TURN WINDOW\n\nPASS")
        return 0

    print(f"\n  {len(bad)} DOT/HOT ABILITIES OUTSIDE THE WINDOW")
    print("  Each wastes most of its damage, or is not really a dot.\n")
    for cls, aid, kind, d in sorted(bad, key=lambda r: -r[3]):
        t, b = realised(d)
        why = (f"only {t:.0%} lands on trash, {b:.0%} on a boss"
               if d > CEILING else "too short to be a dot at all")
        print(f"    {aid:44s} {kind:10s} {d:>3}t   {why}")
    print("\n  Fix: move it into a bucket (2 burst, 3 standard, 4 tail, "
          "5 sustained,\n  6 boss finisher) and scale effect_value so "
          "PER-TICK is preserved -\n  effect_value is the TOTAL, so duration "
          "alone just thins it.")
    print("\nFAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
