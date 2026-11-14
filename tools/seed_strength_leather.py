#!/usr/bin/env python3
"""Author the strength-leather gear that does not exist above ilvl 40. Idempotent.

    PYTHONPATH=. python3 tools/seed_strength_leather.py [--check]

Kyle, 29 Oct 2026: "some str leather, yes."

THE HOLE. Barbarian is the only class in the game wearing leather with strength - the
leather/str_physical niche holds two specs, Ancestry and Brutality, against 13 in leather/agility.
tools/audit_class_gear_coverage.py reports it as the one real gap left after the spec-level rebuild:

    barbarian_ancestry   leather/str_physical   22/41  68/87  72/64  44/46   2/5
                                                 1-10  11-20  21-30  31-40  41-50

Those two pieces at ilvl 41-50 are accessories, which have no armour type and so serve on stats
alone. The real count of strength LEATHER armour above ilvl 40 is ZERO. Every one of the 16 leather
pieces in that band carries agility, or carries no primary stats at all. A Barbarian levelling into
the forties finds nothing.

WHY NEW ITEMS RATHER THAN MORE CONVERSION. The agility seeding passes earlier today were conversions
- rename the stat, budget unchanged, no items created - and they were zero-sum by construction:
Barbarian's own weapon options fell from 112 to 87 at ilvl 11-20 because strength weapons became
agility ones. Taking leather agility away to pay for leather strength at the top end would repeat
that trick on the armour side and rob Rogues, Druids, Templars, Rangers, Bloodmages and Felsworn -
13 specs - to pay 2. So these five are authored.

WHERE THEY GO, and why it costs nothing. Every one of these tables drops ONE item per kill from the
boss's pool, which each file's own _notes states. A fifth entry therefore adds variety rather than
loot: the same single drop, chosen from five pieces instead of four. That is also what Kyle asked
for in the same breath as balance - "i want gear to be unique, diverse".

Each piece takes a slot its pool does not already use, so no boss ends up offering two of the same
slot, and each is sized from the formula in tools/audit_item_budgets.py at str_physical's documented
70/30 split of strength to stamina.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: (file stem, boss) -> the new piece. Slots chosen against each pool's existing four so nothing
#: doubles up: Myzrai already offers leather feet, Saltgorge leather shoulder, The Cargo leather
#: chest, Ssaren leather shoulder, and Vantch no leather at all.
NEW_ITEMS = [
    ("stranglethorn_cave_boss_loot", "Tide-Priestess Myzrai", {
        "name": "Hall-Keeper's Legguards",
        "slot": "legs", "item_level": 45, "rarity": "rare", "required_level": 42,
        "flavor_text": "Cut heavy at the thigh, for standing in moving water without being moved.",
        "primary_stats": {"strength": 19, "stamina": 8},
        "secondary_stats": {}, "armor_type": "leather", "armor_value": 114,
    }),
    ("stranglethorn_cave_boss_loot", "Saltgorge", {
        "name": "Doorway-Watcher's Grips",
        "slot": "hands", "item_level": 45, "rarity": "rare", "required_level": 42,
        "flavor_text": "Something held the jamb hard enough to leave the shape of its hand in it.",
        "primary_stats": {"strength": 10, "stamina": 4},
        "secondary_stats": {}, "armor_type": "leather", "armor_value": 57,
    }),
    ("stranglethorn_openworld_loot", "The Cargo", {
        "name": "Crate-Hauler's Belt",
        "slot": "waist", "item_level": 43, "rarity": "rare", "required_level": 40,
        "flavor_text": "Worn by whoever was carrying it, before it started carrying itself.",
        "primary_stats": {"strength": 9, "stamina": 4},
        "secondary_stats": {}, "armor_type": "leather", "armor_value": 54,
    }),
    ("stranglethorn_openworld_loot", "Ssaren the Salvage-Taker", {
        "name": "Salvage-Hauler's Hood",
        "slot": "head", "item_level": 44, "rarity": "rare", "required_level": 41,
        "flavor_text": "The stitching at the crown is a repair. So is the repair.",
        "primary_stats": {"strength": 14, "stamina": 6},
        "secondary_stats": {}, "armor_type": "leather", "armor_value": 84,
    }),
    ("stranglethorn_openworld_loot", "Captain Orlee Vantch", {
        "name": "Bar-Hauler's Jerkin",
        "slot": "chest", "item_level": 45, "rarity": "rare", "required_level": 42,
        "flavor_text": "Salt-stiff across the shoulders from hauling a line that did not want hauling.",
        "primary_stats": {"strength": 19, "stamina": 8},
        "secondary_stats": {}, "armor_type": "leather", "armor_value": 114,
    }),
]


def main():
    check = "--check" in sys.argv

    import importlib.util
    spec = importlib.util.spec_from_file_location("_aib", ROOT / "tools/audit_item_budgets.py")
    aib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(aib)

    problems, planned = [], []
    for stem, boss, item in NEW_ITEMS:
        path = ROOT / f"data/loot/{stem}.json"
        if not path.exists():
            problems.append(f"{stem}.json does not exist")
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        rows = doc.get("bosses", doc)
        if boss not in rows:
            problems.append(f"{boss!r} is not in {stem}.json")
            continue
        pool = rows[boss]
        if any(e.get("name") == item["name"] for e in pool):
            continue  # already seeded
        # Refuse to double up a slot inside one pool - the whole point of the slot choices.
        clash = [e["name"] for e in pool
                 if e.get("slot") == item["slot"] and e.get("armor_type") == item["armor_type"]]
        if clash:
            problems.append(f"{boss}: already offers leather {item['slot']} ({clash[0]})")
            continue
        budget, armor, _d = aib.budget_for(item)
        ratio = aib.spend(item) / budget
        if abs(ratio - 1.0) > 0.25:
            problems.append(f"{item['name']}: {ratio:.2f}x of budget {budget:.1f} - re-stat it")
            continue
        if armor and abs(item["armor_value"] / armor - 1.0) > 0.25:
            problems.append(f"{item['name']}: armor {item['armor_value']} vs expected {armor}")
            continue
        planned.append((stem, boss, item, ratio, armor))

    if problems:
        for p in problems:
            print(f"  {p}")
        raise SystemExit("refusing to write")

    print(f"{len(planned)} new strength-leather piece(s)\n")
    for stem, boss, item, ratio, armor in planned:
        print(f"  {item['name']:30} ilvl{item['item_level']} {item['slot']:9} "
              f"str {item['primary_stats']['strength']:2} / sta {item['primary_stats']['stamina']:2}"
              f"   budget {ratio:.2f}x   armor {item['armor_value']}/{armor}")
        print(f"      -> {boss} [{stem}]")

    if check:
        return 1 if planned else 0
    if not planned:
        print("nothing to do - already seeded")
        return 0

    by_file = {}
    for stem, boss, item, _r, _a in planned:
        by_file.setdefault(stem, []).append((boss, item))
    for stem, entries in by_file.items():
        path = ROOT / f"data/loot/{stem}.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        rows = doc.get("bosses", doc)
        for boss, item in entries:
            rows[boss].append(item)
        # The notes on two of these files assert "pool of four". They are now pools of five where
        # a piece was added, and a stale note is how the next reader concludes the data is wrong.
        notes = rows.get("_notes") if isinstance(rows.get("_notes"), str) else doc.get("_notes")
        if notes and "pool of four" in notes:
            fixed = notes.replace(
                "pool of four",
                "pool (four, or five where a strength-leather piece was added 29 Oct 2026 - "
                "Barbarian had no leather above ilvl 40)")
            if isinstance(rows.get("_notes"), str):
                rows["_notes"] = fixed
            else:
                doc["_notes"] = fixed
        path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        print(f"  wrote {path.name} (+{len(entries)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
