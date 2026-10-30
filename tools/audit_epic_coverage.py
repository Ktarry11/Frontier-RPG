#!/usr/bin/env python3
"""Which of the 30 classes can actually use an epic. Per class, not per item.

    PYTHONPATH=. python3 tools/audit_epic_coverage.py

Kyle, 2026-10-29: "Each epic should be unique bro and spread across the
classes... i'd like to see more and more 'open world' epics pop up."

build_epic_drops already audits the spread it can see from the table: how
many cloth pieces, how many of each weapon type, how many of each stat
template. That is a check on the SHAPE of the list, and it will happily pass
a list of 36 items that no Druid can equip - armour class and weapon
proficiency are what decide that, and the table does not mention either.

So this asks the question from the other end. For each of the 30 classes:
which epics can it wear or wield at all, and how many of those carry the
stat its role actually wants?

AN IDOL IS NOT A TOME, and that distinction is the reason this exists. A
Vekka's-pool item got authored as an idol, which serves exactly one class
(Druid), so a four-item boss pool was effectively three items for everybody
else. Swapping it for a tome - 20 classes - fixed the pool without changing
its size, and nothing in a spread audit over armour classes would have said
a word about it.
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: A class with fewer usable epics than this is reported. Low on purpose:
#: 36 epics over 30 classes is thin by construction, and the point is to
#: catch a class with NOTHING rather than to demand an even split.
MIN_USABLE = 3
#: ... of which at least this many should suit its role, or the class can
#: equip epics and wants none of them.
MIN_ON_ROLE = 1


def load():
    wt = json.loads((ROOT / "data/items/weapon_types.json").read_text())
    at = json.loads((ROOT / "data/items/armor_types.json").read_text())
    epics = json.loads((ROOT / "data/loot/epic_drops.json").read_text())
    return wt, at, epics


def main():
    from entities.loot_generator import LootGenerator
    gen = LootGenerator()
    wt, at, epics = load()
    class_weapons = wt["class_weapon_map"]
    class_armor = at["class_armor_map"]
    weapon_types = wt["weapon_types"]

    items = [(k, it) for k in ("world", "dungeon") for it in epics.get(k, [])]
    print(f"{len(items)} epics, {len(class_weapons)} classes\n")

    # Which primary stats does this class's armour class and weapon list
    # suggest it wants? Derived from the stat templates that its own gear
    # rolls, rather than a hand-kept list of roles that would drift.
    lead_by_template = gen._TEMPLATE_LEAD

    findings = []
    rows = []
    for cls in sorted(class_weapons):
        armor = class_armor.get(cls)
        weapons = set(class_weapons.get(cls, []))
        usable = []
        for _src, it in items:
            if it.get("armor_type"):
                if it["armor_type"] == armor:
                    usable.append(it)
            elif it.get("weapon_type"):
                if it["weapon_type"] in weapons:
                    usable.append(it)
        # On-role: the item's template leads with a stat that appears on this
        # class's own armour class elsewhere in the epic list. A class whose
        # only usable epics are another role's stats has coverage on paper.
        on_role = []
        for it in usable:
            leads = lead_by_template.get(it.get("stat_template"), frozenset())
            pri = it.get("primary_stats") or {}
            if leads and any(pri.get(s) for s in leads):
                on_role.append(it)
        rows.append((cls, armor, len(usable), len(on_role)))
        if len(usable) < MIN_USABLE:
            findings.append(f"{cls} ({armor}) can use only {len(usable)} of "
                            f"{len(items)} epics")
        elif len(on_role) < MIN_ON_ROLE:
            findings.append(f"{cls} ({armor}) can equip {len(usable)} epics but none "
                            f"carries a stat its templates lead with")

    width = max(len(c) for c, *_ in rows)
    for cls, armor, n_usable, n_role in sorted(rows, key=lambda r: r[2]):
        bar = "#" * n_usable
        print(f"  {cls:{width}} {str(armor):8} {n_usable:2} usable "
              f"({n_role:2} on role)  {bar}")

    # How narrow is each weapon type? An idol serves one class; a tome serves
    # twenty. A pool built out of narrow types is smaller than it looks.
    print("\n  weapon types in the epic list, by how many classes can use them:")
    for atype, count in sorted(Counter(
            it["weapon_type"] for _s, it in items if it.get("weapon_type")).items()):
        serves = sum(1 for c in class_weapons if atype in set(class_weapons[c]))
        note = "  <-- serves almost nobody" if serves <= 2 else ""
        print(f"    {atype:12} {count} item(s), usable by {serves:2} of "
              f"{len(class_weapons)} classes{note}")
        if serves <= 2:
            findings.append(f"{count} epic(s) are {atype}, which only {serves} "
                            f"class(es) can use - that is a near-dead item slot")

    print()
    if not findings:
        print("every class has epics it can use and wants")
        return 0
    print(f"{len(findings)} FINDING(S)")
    for f in findings:
        print(f"  * {f}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
