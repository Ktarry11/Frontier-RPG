#!/usr/bin/env python3
"""Who can actually equip the weapons the game has authored?

    PYTHONPATH=. python3 tools/audit_weapon_proficiency.py

WHY THIS EXISTS. Kyle, 29 Oct 2026: "Bro we 100% need to audit what classes
can use weapons." It started as one finding from tools/audit_loot.py - that
polearms were usable by a single class - and the full sweep turned up the
same shape in both directions, plus one class quietly starved of weapons
altogether.

The question this answers is not "is the class_weapon_map valid" (it is -
every entry names a real weapon type). It is whether the map and the ITEM
POOL agree with each other, because those two are authored in different
places by different passes and nothing has ever compared them:

  * A weapon type with many items and almost no users is dead content. The
    items exist, are hand-named, roll real stats, and 29 of 30 characters
    can never pick them up.

  * A weapon type many classes want with almost no items is an empty slot.
    Eighteen classes can equip a tome and the game contains seven.

  * A CLASS can be starved even when every type it owns is well stocked, if
    it owns too few types. Summing the pool its proficiencies actually reach
    is the only way to see that, and it is the number that surprised me
    most.

THE SCYTHE QUESTION, since it will come up again. A scythe is a polearm -
same weapon class, not a new one (Kyle, 29 Oct: "Scythe is a polearm bro,
same weapon class. Don't make a new one"). Three of the polearm items in
the game are named scythes already. So a class the lore describes as a
scythe wielder should carry `polearm`, and nothing new needs inventing.

WHAT THIS TOOL WILL NOT TELL YOU. It reports mismatches, not verdicts. A
concentrated weapon type can be a deliberate class signature, and a
class with few weapons can be deliberately austere. The sidekick reference
decides which, and this tool points at the rows worth checking there.
"""

from __future__ import annotations

import json
import pathlib
from collections import Counter
import statistics

ROOT = pathlib.Path(__file__).resolve().parent.parent

#: A type with at least this many items and at most CONCENTRATED_CLASSES
#: users is flagged. Below this an under-used type is just a rare weapon.
CONCENTRATED_ITEMS = 20
CONCENTRATED_CLASSES = 2

#: Fewer than this many items per class that can use the type means most of
#: those classes will never see one drop for them.
STARVED_PER_CLASS = 1.5

#: A class reaching less than this fraction of the MEDIAN class's pool is
#: flagged.
#:
#: Measured against the RICHEST class first, and that was a bad instrument:
#: giving Warrior polearm and bow - both correct changes - raised the
#: denominator and re-flagged six classes that had not moved at all, while
#: the genuinely starved one barely changed rank. A metric that cries wolf
#: every time someone enriches a top class will be ignored by the third
#: person who runs it. The median does not move when one end does, so a flag
#: here means the class really is behind the field rather than behind
#: whoever happens to be best stocked.
STARVED_CLASS_RATIO = 0.6


def load():
    d = json.loads((ROOT / "data/items/weapon_types.json").read_text())
    return d["weapon_types"], d["class_weapon_map"]


def count_items(types):
    """Every item in data/ carrying a weapon_type, by type.

    Walks all of data/ rather than a hand-listed set of files, because
    weapons are authored in loot tables, quest rewards, boss drops, vendor
    stock and crafting recipes, and a list of directories goes stale the
    first time someone adds a sixth place.
    """
    counts = Counter()
    names: dict[str, list[str]] = {}

    def walk(node):
        if isinstance(node, dict):
            w = node.get("weapon_type")
            if isinstance(w, str) and w in types:
                counts[w] += 1
                if node.get("name"):
                    names.setdefault(w, []).append(node["name"])
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    for path in sorted((ROOT / "data").rglob("*.json")):
        try:
            walk(json.loads(path.read_text()))
        except Exception:                                      # noqa: BLE001
            continue                        # not an item file; nothing to do
    return counts, names


def main():
    types, cwm = load()
    counts, names = count_items(types)
    users = {w: sorted(c for c, l in cwm.items() if w in l) for w in types}
    reach = {c: sum(counts.get(w, 0) for w in l) for c, l in cwm.items()}
    richest = max(reach.values()) or 1
    typical = statistics.median(reach.values()) or 1

    print(f"{len(types)} weapon types, {len(cwm)} classes, "
          f"{sum(counts.values())} authored weapons\n")

    print("WEAPON TYPE -> ITEMS -> CLASSES THAT CAN EQUIP THEM")
    print(f"  {'type':14}{'items':>7}{'classes':>9}{'per class':>11}")
    for w in sorted(types, key=lambda w: -counts.get(w, 0)):
        n, nc = counts.get(w, 0), len(users[w])
        per = n / nc if nc else 0.0
        print(f"  {w:14}{n:>7}{nc:>9}{per:>11.1f}")

    print("\nITEMS EACH CLASS CAN ACTUALLY REACH")
    for c in sorted(reach, key=lambda c: reach[c]):
        bar = "#" * int(28 * reach[c] / richest)
        print(f"  {reach[c]:>5}  {c:18} {bar}")

    findings = []

    for w in sorted(types):
        n, who = counts.get(w, 0), users[w]
        if not who and n:
            findings.append(
                f"[orphan] {w}: {n} authored item(s) and NO class can equip "
                f"them - every one is unreachable")
        elif n >= CONCENTRATED_ITEMS and len(who) <= CONCENTRATED_CLASSES:
            top = ", ".join(sorted(Counter(
                nm.split()[-1].lower() for nm in names.get(w, [])
            ).keys())[:6])
            findings.append(
                f"[concentrated] {w}: {n} items usable only by "
                f"{', '.join(who)} - dead content for the other "
                f"{len(cwm) - len(who)} classes (items are mostly {top})")
        elif who and n / len(who) < STARVED_PER_CLASS:
            findings.append(
                f"[under-authored] {w}: {len(who)} classes can equip it and "
                f"the game has {n} - {n/len(who):.1f} per class, so most "
                f"will never see one")

    for c in sorted(reach, key=lambda c: reach[c]):
        if reach[c] < typical * STARVED_CLASS_RATIO:
            # SAY WHICH SLOTS THE CLASS CAN EVEN FILL. A melee-only chassis
            # reaches fewer items because it has fewer slots to fill, not
            # because it is short of weapons - Felsworn, Reaper, Cultist and
            # Knight of Xoroth have no ranged-capable type, which matches
            # their Death Knight and Demon Hunter analogues having no ranged
            # slot at all. Without this the finding reads as a defect when it
            # is a design, and the previous version of this check already had
            # to be rewritten once for crying wolf.
            slots = []
            for label, hands in (("main", {"main_or_off", "two_hand"}),
                                 ("off", {"off_hand", "main_or_off"}),
                                 ("ranged", {"ranged"})):
                if any(types[w].get("hand") in hands for w in cwm[c]):
                    slots.append(label)
            msg = (f"[starved class] {c} reaches {reach[c]} weapons against "
                   f"a field median of {typical:.0f} ({reach[c]/typical:.0%}) "
                   f"from only {len(cwm[c])} proficiencies: "
                   f"{', '.join(cwm[c])}")
            missing = [s for s in ("main", "off", "ranged") if s not in slots]
            if missing:
                # Only say this when it is true. It was printed
                # unconditionally for one revision, and stayed on the
                # Felsworn line after Kyle gave it a thrown weapon - a
                # finding that explains itself wrongly is worse than one
                # that does not explain itself at all.
                msg += (f"\n        cannot fill: {', '.join(missing)}"
                        f" - a class with no type for a slot reaches fewer"
                        f" items by design, not by shortage")
            else:
                msg += (f"\n        fills all three weapon slots, so this is"
                        f" a deliberately narrow kit rather than a gap")
            findings.append(msg)

    print("\nFINDINGS")
    if findings:
        for f in findings:
            print(f"  * {f}\n")
    else:
        print("  none - every weapon type has users and every class has reach")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
