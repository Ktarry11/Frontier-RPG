#!/usr/bin/env python3
"""The named epics: world drops and the occasional dungeon purple. Idempotent.

    PYTHONPATH=. python3 tools/build_epic_drops.py

Kyle, 2026-10-28: "We can get the occasional drops as epic after lvl 30 in Dungeons and also for
world drop after lvl 30. Think of how wow does it with world drops."

WHAT THE AUDIT FOUND. All 892 hand-authored dungeon items are rarity rare - there is not one epic
drop anywhere in the game - while two upgrade kits take any crafted piece to epic plus five item
levels. So there was no gear reason to run a dungeon. The procedural roller already gates epic at
level 30 exactly as Kyle describes, but hand-authored boss pools bypass it: get_fixed_boss_loot
returns a fixed item before the procedural roll ever happens, and all 44 bosses above level 30 have
one.

WOW'S WORLD-DROP MODEL IS WHY THESE ARE NAMED AND FEW. A world epic in WoW is memorable because it
is a specific item - people know the name, they know roughly what drops it, and almost nobody has
one. A purple generated on the fly from a stat budget cannot do that however rare you make it, so
these are hand-authored: twenty-two items, each with its own name and its own reason to exist.

STATS COME FROM THE ENGINE, NOT FROM ME. Only the identity is authored here - name, slot, type,
item level, who it suits. LootGenerator fills in the actual numbers at epic budget, which is the
same code path every other item in the game goes through. Hand-writing stat blocks for 22 epics
would mean hand-deriving the armour and damage curves, and the first one I got slightly wrong would
sit there being slightly wrong forever.

SPREAD IS CHECKED, NOT ASSUMED, because Kyle's standing rule is that loot must not be lopsided
toward one armour class or weapon type. The audit() at the bottom fails the build if it is.
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: (name, slot, kind, type, item_level, stat_template, flavour)
#: Found anywhere in the world, off anything, at level 30 and up. These are the ones people trade
#: stories about, so each is a thing rather than a stat line.
WORLD = [
    ("Hollowmade Crown", "head", "armor", "cloth", 34, "int_caster",
     "Light as nothing. The smith who made it left no other work behind."),
    ("The Long Patience", "legs", "armor", "plate", 38, "str_physical",
     "Somebody stood in these for a very long time, in one place, on purpose."),
    ("Tidewidow's Wrap", "back", "armor", "cloth", 32, "spi_healer",
     "Still damp at the hem. It has been dry storage for three years."),
    ("Scavenger's Honest Grip", "hands", "armor", "leather", 33, "agi_physical",
     "Worn through at the fingertips and nowhere else, which says what the work was."),
    ("Bluefinger", "main_hand", "weapon", "dagger", 35, "agi_physical",
     "Named for what it does to a hand that holds it wrong."),
    ("Oathless", "main_hand", "weapon", "sword_2h", 40, "str_physical",
     "No maker's mark, no inscription, nothing promised to anybody. Unusual for a blade this good."),
    ("Rimeworn Pauldrons", "shoulder", "armor", "mail", 36, "agi_physical",
     "The frost pattern is in the metal, not on it."),
    ("The Quiet Argument", "main_hand", "weapon", "mace_1h", 37, "spi_healer",
     "Carried by someone who preferred to be reasonable and came prepared not to be."),
    ("Ninefold Belt", "waist", "armor", "leather", 39, "agi_int_hybrid",
     "Nine layers, nine different hides. Eight of them are from animals anybody can name."),
    ("Lamplighter's Coat", "chest", "armor", "cloth", 41, "int_caster",
     "Scorched in a ring around the cuffs, from reaching into places that were already lit."),
    ("Stonewake Greaves", "feet", "armor", "plate", 42, "str_physical",
     "Heavy enough that the wearer's route can be followed a week later."),
    ("The Second Opinion", "main_hand", "weapon", "staff", 42, "int_caster",
     "Found alongside a first opinion, which had not worked."),
]

#: Occasional drops from bosses at level 30 and up, themed to the dungeons that exist up there -
#: the Crystalline Underdark's archive, the Drowning Floor, the Southern Needles.
DUNGEON = [
    ("Marginalia", "wrist", "armor", "cloth", 38, "int_caster",
     "Somebody wrote on the inside of the cuff, in a hand too small to read without light."),
    ("The Corrected Edition", "chest", "armor", "plate", 40, "str_int_hybrid",
     "An earlier version of this exists. It is not clear what was wrong with it."),
    ("Shardmaw's Underjaw", "main_hand", "weapon", "fist_weapon", 37, "agi_physical",
     "Set into a grip by somebody who had to pry it loose first."),
    ("The Unlisted Name", "head", "armor", "leather", 39, "agi_int_hybrid",
     "Every piece down there is catalogued. This one is not, and the gap has been tidied."),
    ("Footnote", "main_hand", "weapon", "dagger", 36, "agi_physical",
     "Small, late in the argument, and the part people remember."),
    ("The Deep Bloom's Root", "main_hand", "weapon", "staff", 43, "spi_healer",
     "Cut, and still putting out pale shoots along its length."),
    ("Yearmaw's Toothmark", "chest", "armor", "mail", 36, "agi_physical",
     "Punched through and beaten flat again from the inside. Whoever did the repair survived."),
    ("What the Tide Kept", "off_hand", "weapon", "shield", 35, "str_physical",
     "Salt has got into every seam and made it heavier than it was built to be."),
    ("Galak Tollbreaker", "main_hand", "weapon", "axe_2h", 38, "str_physical",
     "Carried by the first person who declined to pay, and recovered from where they fell."),
    ("Thermal-Borne Greaves", "legs", "armor", "mail", 36, "agi_physical",
     "Updraft off a mesa top will hold a feather for an hour. These were found at the bottom."),
]


def audit(rows):
    """Kyle's standing rule: boss and quest loot must not lean on one armour class or weapon type."""
    armour = Counter(t for _n, _s, k, t, _il, _st, _f in rows if k == "armor")
    weapons = Counter(t for _n, _s, k, t, _il, _st, _f in rows if k == "weapon")
    templates = Counter(st for *_x, st, _f in rows)
    problems = []
    for cls in ("cloth", "leather", "mail", "plate"):
        if armour[cls] < 2:
            problems.append(f"only {armour[cls]} {cls} pieces - the spread is lopsided")
    if max(weapons.values(), default=0) > 3:
        hog = max(weapons, key=weapons.get)
        problems.append(f"{weapons[hog]} of the weapons are {hog}")
    if len(templates) < 5:
        problems.append(f"only {len(templates)} stat templates represented of 6")
    print(f"  armour: {dict(armour)}")
    print(f"  weapons: {dict(weapons)}")
    print(f"  stat templates: {dict(templates)}")
    return problems


def main():
    from entities.loot_generator import LootGenerator
    gen = LootGenerator()

    print(f"spread check over {len(WORLD) + len(DUNGEON)} epics:")
    problems = audit(WORLD + DUNGEON)
    if problems:
        print("\nFAILED - fix the table, not the check:")
        for p in problems:
            print(f"  - {p}")
        return 1

    out = {"_notes": ("Named epic drops (2026-10-28). WORLD items drop from anything at level 30+ "
                      "at a very low rate; DUNGEON items are the occasional purple off a level 30+ "
                      "boss. Identity is hand-authored in tools/build_epic_drops.py; every stat "
                      "below came from LootGenerator at epic budget, so these sit on the same "
                      "curves as the rest of the game's loot. Rolled by entities/epic_drops.py.")}

    for key, rows in (("world", WORLD), ("dungeon", DUNGEON)):
        items = []
        for name, slot, kind, atype, ilvl, template, flavour in rows:
            if kind == "armor":
                it = gen.generate_armor_piece(slot, atype, template, ilvl, "epic")
            else:
                it = gen.generate_weapon(slot, atype, template, ilvl, "epic")
            if it is None:
                print(f"FAILED: the generator would not build {name} ({atype} {slot})")
                return 1
            d = it.to_dict() if hasattr(it, "to_dict") else {}
            d["name"] = name
            d["flavor_text"] = flavour
            # The generated item_id carries a uuid, which would make this file churn on every run.
            d["item_id"] = "epic_" + name.lower().replace("'", "").replace(" ", "_")
            items.append(d)
        out[key] = items
        print(f"\n  {key}: {len(items)} items, item level "
              f"{min(i['item_level'] for i in items)}-{max(i['item_level'] for i in items)}")

    p = ROOT / "data/loot/epic_drops.json"
    p.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"\nwrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
