#!/usr/bin/env python3
"""The resistance scale is exactly the one Kyle specified.

    PYTHONPATH=. python3 tools/qa_resistance_scale.py

This locks a formula that is now load-bearing in two directions and easy to
break silently. Kyle's spec, 6 Nov, is a worked example rather than a
constant, so the test is the example:

    "something can have resistance, but it will never go over 75%
    resistance to an element. But we can also have negative resistances.
    For example a fireball hits an enemy for 100 damage. On a fire elemental
    it will hit for 25 damage. on an ice elemental it can hit for 150. This
    is why a caster will want to aim to get at least 60 spell penetration
    and we can work the math backwards since resistances wont change.
    Essentially a monster with 60 resistance will resist 75% of damage."

and then, on penetration:

    "1 point spell pen reduces 2 points resistance... I kind of want it in
    line with hit rating. It's unfair for a physical DPS to need hit rating
    or armor penetration to improve DPS where casters generally only have
    hit rating."

Four things are checked, each of which was a real bug or a real near-miss
while this was being built:

  1. THE SCALE. 60 -> 25 damage and -40 -> 150 damage, off a 100-damage hit,
     through the real take_damage rather than the formula in isolation.
  2. THE CLAMPS, both ways. Resistance past 60 is still 75% and past -60 is
     still +75%, so a stacking bug cannot make anything immune or delete a
     character.
  3. PENETRATION CANNOT TOUCH A VULNERABILITY. The call sites all read
     `max(0, res - pen)`, which was correct while resistance could not go
     below zero and became a bug the moment it could: an ice elemental at
     -40 would have been read as 0 by any attacker carrying any penetration
     at all, cancelling the vulnerability with the stat meant to cut
     resistance.
  4. 30 PENETRATION IS ENOUGH AND 31 IS WASTE, which is what "in line with
     hit rating" means - the caster's stat has a reachable end, like the
     27-point hit cap, rather than the 60 it needed at 1:1.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from entities.character import Character                      # noqa: E402
from combat.status_effects import DamageSchool                 # noqa: E402

fails = []


def check(ok, label, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f"  {detail}" if detail else ""))
    if not ok:
        fails.append(f"{label} {detail}".strip())


class Pen:
    """An attacker carrying nothing but spell penetration."""
    def __init__(self, pen):
        self.spell_penetration = pen


def landed(resistance, pen=0, amount=100):
    """What a `amount`-damage Fireball does to a target at `resistance`."""
    c = Character("Dummy", "Warrior", 60)
    c.max_health = 10 ** 7
    c.current_health = 10 ** 7
    c.fire_resistance = resistance
    # Avoidance is physical-only and rows/level are neutral here, so this is
    # the resistance path and nothing else.
    c.row = None
    return c.take_damage(amount, DamageSchool.FIRE, attacker_level=60,
                         attacker=Pen(pen) if pen else None)


print("--- Kyle's worked example, through take_damage")
check(Character.RESIST_CAP == 0.75, "60 resistance resists 75%",
      f"cap {Character.RESIST_CAP:.2%}")
check(abs(landed(60) - 25) <= 1, "a fire elemental takes 25 from a 100 Fireball",
      f"{landed(60)}")
check(abs(landed(-40) - 150) <= 1, "an ice elemental takes 150 from the same",
      f"{landed(-40)}")
check(landed(0) == 100, "a neutral target takes it in full", f"{landed(0)}")

print("\n--- the clamps, both directions")
check(landed(600) == landed(60), "resistance past 60 does nothing more",
      f"600 -> {landed(600)}, 60 -> {landed(60)}")
check(landed(-600) == landed(-60), "vulnerability past -60 does nothing more",
      f"-600 -> {landed(-600)}, -60 -> {landed(-60)}")
check(landed(-60) == 175, "the worst vulnerability is +75% damage",
      f"{landed(-60)}")

print("\n--- spell penetration")
check(Character.SPELL_PEN_PER_RESIST == 2,
      "one point of penetration removes two of resistance",
      f"{Character.SPELL_PEN_PER_RESIST}")
check(Character.SPELL_PEN_USEFUL_MAX == 30,
      "so 30 cancels the worst resistance in the game",
      f"{Character.SPELL_PEN_USEFUL_MAX}")
check(landed(60, pen=30) == 100, "30 penetration takes a 75% resist to zero",
      f"{landed(60, pen=30)}")
check(landed(60, pen=31) == landed(60, pen=30),
      "and 31 does nothing a 30th did not", f"{landed(60, pen=31)}")
check(abs(landed(60, pen=15) - 62) <= 2, "half of it is half the resistance",
      f"{landed(60, pen=15)}")

print("\n--- penetration never touches a vulnerability")
for pen in (1, 15, 30, 60):
    check(landed(-40, pen=pen) == landed(-40),
          f"{pen} penetration leaves a -40 target at 150", f"{landed(-40, pen=pen)}")

print("\n--- the full scale is level-60 content only")
# Kyle, 6 Nov: "We only set anything UNDER lvl 60 at a max of 30
# resistances... This will make it so getting 15 wont be hard."
check(Character.RESIST_MAX_PRE_60 == 30,
      "below 60, nothing carries more than 30 resistance",
      f"{Character.RESIST_MAX_PRE_60}")
for lv, want in ((1, 30), (20, 30), (59, 30), (60, 60), (70, 60)):
    got = Character.resist_ceiling_for_level(lv)
    check(got == want, f"level {lv} ceiling is {want}", f"{got}")
check(Character.clamp_resistance_for_level(60, 40) == 30,
      "a 60 authored on a level 40 creature reads as 30")
check(Character.clamp_resistance_for_level(-40, 40) == -30,
      "and a -40 vulnerability reads as -30, symmetrically")
check(Character.clamp_resistance_for_level(60, 60) == 60,
      "at 60 the full value stands")
print(f"  so a levelling caster needs "
      f"{Character.RESIST_MAX_PRE_60 // Character.SPELL_PEN_PER_RESIST}"
      f" penetration, and a level 60 one "
      f"{Character.SPELL_PEN_USEFUL_MAX}")

print("\n--- creatures really obey it, through the manager")
from world.creature_manager import CreatureManager                 # noqa: E402
cm = CreatureManager()
worst = []
for name in list(__import__("json").loads(
        (ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]):
    m = cm.spawn_creature(name)
    if m is None:
        continue
    ceiling = Character.resist_ceiling_for_level(m.level)
    for school in ("fire", "frost", "nature", "shadow", "arcane", "holy"):
        v = m.get_resistance(school)
        if abs(v) > ceiling:
            worst.append(f"{name} (level {m.level}) {school} {v}")
check(not worst, "no creature exceeds its level's ceiling in any school",
      f"{len(worst)} over: {worst[:3]}")

print("\n--- in line with hit rating, which is the point of the 30")
print(f"  spell penetration useful max {Character.SPELL_PEN_USEFUL_MAX}"
      f"   hit rating cap {Character.HIT_RATING_CAP:.0f}")
check(abs(Character.SPELL_PEN_USEFUL_MAX - Character.HIT_RATING_CAP) <= 5,
      "the two chase stats end within a few points of each other",
      f"{Character.SPELL_PEN_USEFUL_MAX} vs {Character.HIT_RATING_CAP:.0f}")

print("\n" + ("resistance scale OK" if not fails else f"FAIL ({len(fails)})"))
for f in fails:
    print(f"  - {f}")
sys.exit(1 if fails else 0)
