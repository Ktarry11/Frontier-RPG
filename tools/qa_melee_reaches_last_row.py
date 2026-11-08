"""Melee must reach the back row once the front rank is dead.

THE BUG THIS EXISTS FOR (Kyle, 2026-11-08, relaying his friend): a druid in
BEAR FORM, partied with a priest, could not melee the back row when
everything in front of it was already dead - "he had to let the priest kill
it". A fight that cannot be finished by the person whose whole job is
hitting things.

The rule in combat/rows.py is that once every front-row enemy is dead the
BACK ROW IS THE FRONT ROW, so melee reaches it. The failure mode is a melee
reach gate that checks `row == FRONT_ROW` literally instead of asking
`front_rank` what counts as the front right now - which looks correct in
isolation and is wrong only at the end of a fight.

Bear form is in here by name because that is where it was reported, and
because shifting changes the druid's abilities, resource pool and stats -
enough moving parts that "it works for a warrior" is not an answer.

What this checks is REACH, not damage: whether the engine offers the
back-row enemy as a legal target at all.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from combat import rows as rowrules
from entities.party import FRONT_ROW, BACK_ROW

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}  {detail}")
        failures.append(label)


class Dummy:
    """Minimal combatant: a row and whether it is still standing."""

    def __init__(self, name, row, alive=True):
        self.name = name
        self.row = row
        self._alive = alive

    def is_alive(self):
        return self._alive

    def __repr__(self):
        return self.name


class Swing:
    """A melee ability - no explicit reach, ordinary damage effect_type."""
    effect_type = "damage"
    name = "Maul"


class Bolt:
    effect_type = "spell_damage"
    name = "Smite"


class Cleave:
    effect_type = "damage"
    name = "Swipe"


bear = Dummy("Bear-form druid", FRONT_ROW)
priest = Dummy("Priest", BACK_ROW)

print("== the ability's reach is read correctly")
check("a swing is melee", rowrules.reach_of(Swing()) == rowrules.MELEE)
check("a spell is ranged", rowrules.reach_of(Bolt()) == rowrules.RANGED)

print("\n== with the front rank alive, melee is held off the back row")
front = Dummy("Grunt", FRONT_ROW)
back = Dummy("Marksman", BACK_ROW)
reach = rowrules.reachable(bear, Swing(), [front, back])
check("melee reaches only the front rank", reach == [front], f"got {reach}")
check("the priest still reaches the back row",
      back in rowrules.reachable(priest, Bolt(), [front, back]))

print("\n== THE REPORTED BUG: front rank dead, one back-row enemy left")
front._alive = False
reach = rowrules.reachable(bear, Swing(), [front, back])
check("the back-row enemy is reachable by melee", reach == [back], f"got {reach}")
check("front_rank reports the back row as the front now",
      rowrules.front_rank([front, back]) == BACK_ROW)

print("\n== and with several back-row enemies, melee reaches all of them")
back2 = Dummy("Acolyte", BACK_ROW)
reach = rowrules.reachable(bear, Swing(), [front, back, back2])
check("every surviving back-row enemy is reachable",
      sorted(r.name for r in reach) == ["Acolyte", "Marksman"], f"got {reach}")

print("\n== a melee AoE can be aimed at the back row once the front is gone")
rows_before = rowrules.targetable_rows(bear, Cleave(), [Dummy("Grunt", FRONT_ROW), back])
check("cleave is stuck on the front rank while it lives", rows_before == [FRONT_ROW],
      f"got {rows_before}")
rows_after = rowrules.targetable_rows(bear, Cleave(), [front, back])
check("cleave reaches the back row once the front is dead", rows_after == [BACK_ROW],
      f"got {rows_after}")

print("\n== an all-dead enemy side offers nothing rather than crashing")
back._alive = back2._alive = False
check("no reachable targets", rowrules.reachable(bear, Swing(), [front, back, back2]) == [])
check("no front rank", rowrules.front_rank([front, back, back2]) is None)
check("no targetable rows", rowrules.targetable_rows(bear, Cleave(), [front, back]) == [])

print("\n== a taunt still crosses rows (it is what lets a tank peel a caster)")
live_front = Dummy("Grunt", FRONT_ROW)
live_back = Dummy("Marksman", BACK_ROW)
reach = rowrules.reachable(bear, Swing(), [live_front, live_back], taunted_by=live_back)
check("a taunted attacker is forced onto its taunter across rows",
      reach == [live_back], f"got {reach}")

print("\n== the rule is symmetric: enemy melee is held off the party back line")
enemy = Dummy("Grunt", FRONT_ROW)
party = [Dummy("Warrior", FRONT_ROW), Dummy("Priest", BACK_ROW)]
reach = rowrules.reachable(enemy, Swing(), party)
check("enemy melee reaches only the party front row",
      [r.name for r in reach] == ["Warrior"], f"got {reach}")
party[0]._alive = False
reach = rowrules.reachable(enemy, Swing(), party)
check("and reaches the healer once the front line falls",
      [r.name for r in reach] == ["Priest"], f"got {reach}")

print()
if failures:
    print(f"FAILED ({len(failures)}): " + ", ".join(failures))
    sys.exit(1)
print("All melee reach checks passed.")
