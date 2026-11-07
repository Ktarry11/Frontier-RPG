#!/usr/bin/env python3
"""An epic must beat a rare of the same item level. Every time, no exceptions.

    PYTHONPATH=. python3 tools/qa_epic_superiority.py

Kyle, 7 Nov: "We need to ensure that epics are better than rares."

WHY THIS NEEDS A TEST AND NOT JUST A FIX. The generator already guarantees it
- rarity multipliers are 1.7 for rare and 2.2 for epic, so a generated epic is
1.29x a generated rare on stats, armour and weapon damage alike. The hole is
HAND-AUTHORED items, which are written by eye and checked against nothing. Of
36 authored epics, 12 carried less armour than a RARE of the same item level
would have had. One of them, Lamplighter's Coat, was a purple with 67 armour
where a blue would have carried 67 and an epic should carry 87.

Nothing failed. Every suite passed. The items simply read as weak and there
was no way to notice except by equipping one.

THE FLOOR, and why it is the rare multiplier rather than the epic target.
Holding authored epics to their full epic budget would fail items that are
deliberately below-budget for a reason - a weapon trading stats for damage,
say. Threshing Day carries 26 stat points where a rare 2H mace carries 30,
and it is not broken: it hits 29% harder, which for a two-hander is where the
value lives. What is NEVER acceptable is an epic a player would be right to
pass over for a blue. So the bar is the rare-equivalent target, 1.7/2.2 =
0.773 of the item's own epic budget, applied per axis.

An axis only counts if the item has one: a cloak is not failed for carrying no
weapon damage.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from audit_item_budgets import spend, budget_for, collect, _RARITY  # noqa: E402

RARE = _RARITY["rare"]["stat_budget_multiplier"]
EPIC = _RARITY["epic"]["stat_budget_multiplier"]
FLOOR = RARE / EPIC


def main():
    checked = 0
    failures = []
    for source, owner, item in collect():
        if item.get("rarity") != "epic":
            continue
        checked += 1
        budget, armor, damage = budget_for(item)
        bad = []

        if budget:
            got = spend(item)
            if got < budget * FLOOR:
                bad.append(f"stats {got:.0f} < {budget * FLOOR:.0f}")
        if armor and item.get("armor_value") is not None:
            if item["armor_value"] < armor * FLOOR:
                bad.append(f"armor {item['armor_value']} < {armor * FLOOR:.0f}")
        if damage and item.get("weapon_damage_max"):
            got = (item["weapon_damage_min"] + item["weapon_damage_max"]) / 2
            if got < damage * FLOOR:
                bad.append(f"damage {got:.0f} < {damage * FLOOR:.0f}")

        if bad:
            failures.append((item.get("name", "?"), item.get("item_level"),
                             source, owner, bad))

    print(f"  {checked} epics checked against a rare-equivalent floor "
          f"({RARE}/{EPIC} = {FLOOR:.3f} of their own epic budget)")

    if failures:
        print(f"\n  {len(failures)} epic(s) a player would be right to pass over "
              f"for a blue:\n")
        for name, ilvl, source, owner, bad in failures:
            print(f"    {name[:36]:38}ilvl {ilvl:<5}{', '.join(bad)}")
            print(f"      {source} / {owner}")
        print("\nFAIL")
        return 1

    print("\n  every epic clears a same-level rare on every axis it has")
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
