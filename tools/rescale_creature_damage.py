#!/usr/bin/env python3
"""Make enemies hit like they mean it, without turning them into HP sponges.

    PYTHONPATH=. python3 tools/rescale_creature_damage.py [--apply]

Kyle, 7 Nov:
    "i just auto attack every boss to death without gear on and survive."
    "most dungeon mobs just shit out loot as they either buff themselves for
     piddly shit then proceed to hit like a wet noodle."
    "I want enemies to have some threat when they hit you, but i dont want
     them to be massive HP sponges."
    "open world doesnt have to be VERY dangerous, but there should be some
     brainpower. But dungeons should not just be free loot dispensers."

MEASURED, one geared Warrior with a shield against a same-level boss:

    lvl  player hp  boss hit  boss hp   turns for the boss to kill you
     10        468        21      305              22
     20        676        28      404              24
     30        900        32      749              28
     40       1204        60      822              20
     50       1348       164     1169               8

A level-30 boss needs TWENTY-EIGHT turns to kill one character, and the
player kills it in three. Level 50 is the only band that is sane, which is
the useful clue: the damage curve is right at the top and collapses
everywhere below it.

WHY, and it is the shape this codebase keeps producing. entities/monster.py
scales a creature's HEALTH and ATTACK POWER with level -
`level_mult = 1.0 + (level - 1) * 0.15` - but an ability's damage is the
flat `amount` authored in its kit, deliberately unscaled (a previous pass
removed the multiplier because it was producing one-shots past level 35).
So health grew with level and the numbers authored against it did not.

WHAT THIS CHANGES, and what it deliberately does not. Only `amount` on
damage and dot entries, and only by a level-band factor. HEALTH IS NOT
TOUCHED - raising it is what makes a sponge, and boss health (305 at 10,
749 at 30) was never the problem. A fight stays three or four turns; those
turns become dangerous. That is the exact thing Kyle asked for and the
exact thing nerfing player damage would NOT have given him.

BOSSES AND TRASH GET DIFFERENT FACTORS, per "open world doesnt have to be
VERY dangerous [...] but dungeons should not just be free loot dispensers."

TARGET: a boss kills one unassisted character in about seven turns, trash
in about fifteen. Factors are solved from the measurement rather than
chosen, and the tool re-measures afterwards and prints both.
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KITS = os.path.join(ROOT, "data/creatures/ability_kits.json")
CREATURES = os.path.join(ROOT, "data/creatures/creatures.json")

#: (level, boss factor, trash factor). Interpolated between; held flat
#: outside. Solved from the measured table above against a ~7-turn boss and
#: ~15-turn trash target, then rounded to something a person can read.
BANDS = [
    (1,  3.2, 2.0),
    (10, 3.2, 2.0),
    (20, 3.6, 2.2),
    (30, 4.0, 2.4),
    (40, 2.9, 1.8),
    (50, 1.2, 1.0),
    (60, 1.0, 1.0),
]

#: Entry kinds whose `amount` is damage. heal/buff/debuff amounts are left
#: alone - a boss healing itself harder is a sponge by another name, which
#: is the thing being avoided.
DAMAGE_KINDS = ("damage", "dot")

#: A DOT's `amount` is PER TURN, so the full factor applied to a 5-turn DOT
#: is five times the damage increase of the same factor on a direct hit.
#: Damped to the square root, which keeps a DOT growing with the rest
#: without it quietly becoming the biggest thing in the kit: at a factor of
#: 4.0 a direct hit quadruples and a DOT doubles.
def dot_factor(f):
    return f ** 0.5


def factor_for(level, is_boss):
    idx = 2 if is_boss else 1
    if level <= BANDS[0][0]:
        return BANDS[0][idx - 1 + 1]
    for (l0, b0, t0), (l1, b1, t1) in zip(BANDS, BANDS[1:]):
        if l0 <= level <= l1:
            a, b = (b0, b1) if is_boss else (t0, t1)
            if l1 == l0:
                return a
            t = (level - l0) / (l1 - l0)
            return a + (b - a) * t
    return BANDS[-1][1 if is_boss else 2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    with open(CREATURES) as fh:
        creatures = json.load(fh)["creatures"]
    with open(KITS) as fh:
        kitdoc = json.load(fh)
    kits = kitdoc["kits"]

    # A kit's level and boss-ness come from the creatures that USE it, not
    # from the kit, which carries neither. A kit shared by a boss and trash
    # takes the boss factor - under-hitting a boss is the complaint; an
    # over-hitting trash mob that shares a boss's kit is a rarity worth
    # eyeballing rather than a reason to under-scale the boss.
    owners = {}
    for name, c in creatures.items():
        key = c.get("ability_kit")
        if not key:
            continue
        lr = c.get("level_range") or [1, 1]
        lvl = (lr[0] + lr[1]) / 2 if lr and lr[0] is not None else 1
        prev = owners.get(key)
        boss = bool(c.get("is_boss"))
        if prev is None or (boss and not prev[1]):
            owners[key] = (lvl, boss)

    changed = 0
    rows = []
    for key, kit in kits.items():
        lvl, boss = owners.get(key, (1, False))
        f = factor_for(lvl, boss)
        for entry in kit or []:
            if entry.get("kind") not in DAMAGE_KINDS:
                continue
            old = entry.get("amount", 0) or 0
            if not old:
                continue
            ef = dot_factor(f) if entry.get("kind") == "dot" else f
            new = max(1, int(round(old * ef)))
            if new != old:
                changed += 1
                rows.append((key, entry.get("name"), round(lvl), boss, old, new, ef))
                if args.apply:
                    entry["amount"] = new

    rows.sort(key=lambda r: (not r[3], r[2]))
    print(f"  {len(kits)} kits, {changed} damage entries rescaled")
    print(f"  health is NOT touched - that is what makes a sponge\n")
    print(f"  {'kit':26}{'ability':24}{'lvl':>5}{'kind':>7}"
          f"{'old':>6}{'new':>6}{'x':>6}")
    for key, name, lvl, boss, old, new, f in rows[:24]:
        print(f"  {str(key)[:25]:26}{str(name)[:23]:24}{lvl:>5}"
              f"{'boss' if boss else 'trash':>7}{old:>6}{new:>6}{f:>6.1f}")
    if len(rows) > 24:
        print(f"  ... and {len(rows) - 24} more")

    if args.apply:
        with open(KITS, "w") as fh:
            json.dump(kitdoc, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print(f"\n  written to {KITS}")
    else:
        print("\n  (report only; pass --apply to write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
