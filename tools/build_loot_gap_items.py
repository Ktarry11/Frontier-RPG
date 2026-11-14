#!/usr/bin/env python3
"""Author the items the weapon-type gaps were missing, and place them.

    PYTHONPATH=. python3 tools/build_loot_gap_items.py          # report
    PYTHONPATH=. python3 tools/build_loot_gap_items.py --apply  # write

WHY. Kyle, 29 Oct 2026: "fix loot balance. Throw in an item throughout caves
or Dungeons or quest rewards." tools/audit_weapon_proficiency.py had five
under-authored types - a weapon class many characters can hold and the game
barely contains:

    tome          7 items   20 classes can hold one
    thrown        4 items   11
    fist_weapon  17 items   20
    libram        0 items    3   (added as a type the same day)
    idol          0 items    1

Widening proficiency earlier that day made these worse, not better: more
classes could hold a tome and there were still seven of them. Four of the five
are off-hand or ranged slots, so the practical effect was characters walking
around with an empty slot because nothing that fits it exists.

WHAT THIS IS NOT. Two-handed melee was also reported as thin on the strength
of 72 items across three types against 376 across the five one-handed ones.
Per class that is sword_2h 1.85, axe_2h 1.93 and mace_2h 1.88 - all above the
audit's 1.5 threshold and in the normal band. The absolute-count framing
overstated it, so nothing is added there.

HOW THE NUMBERS ARE DERIVED. Every item goes through make() from
tools/build_durotar_content.py, the same helper the existing hand-authored
loot uses: stats come from the real suffix weights and the item-level budget,
and weapon damage from the damage_tier table. Nothing here is a hand-typed
stat. Relics and tomes come out as stat sticks with no auto-attack damage,
which is the rule generate_weapon always applied and this helper did not until
the same day - every Totem and Tome previously authored by hand shipped WITH
weapon damage.

PLACEMENT. Levels are spread across the content's real range (item level 2-43)
rather than clustered, and split between cave/dungeon boss pools and quest
rewards. A boss pool is a list, so the item joins it as another possible drop;
a quest reward goes in that quest's unique_item_defs, which
world/quest.py:363 gives priority over the procedural gear reward. Each item
is placed in a file whose existing level band contains it, so nothing lands
somewhere a player could not reasonably be.
"""

from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

#: (weapon_type, item_level, suffix, name, flavor, label)
#:
#: Names and flavour are hand-written in the voice the existing loot uses -
#: concrete, short, and about the object rather than the stats.
ITEMS = [
    # ---------------- tome: 25. A held-in-off-hand stat stick, usable by any
    # class (it carries no proficiency), so these spread the whole range.
    ("tome", 6, "of the Seer", "Novice's Water-Stained Primer",
     "Someone has corrected the margins in a firmer hand than the text.", "Tome (Spi)"),
    ("tome", 9, "of the Prophet", "Deathknell Hymnal",
     "Forty hymns. Thirty-one are about dirt.", "Tome (Int/Spi)"),
    ("tome", 11, "of the Invoker", "Ledger of Small Debts",
     "Every name is crossed out. None of them are paid.", "Tome (Int)"),
    ("tome", 13, "of the Seer", "Tidewatcher's Almanac",
     "Charts for a coast that has since moved.", "Tome (Spi)"),
    ("tome", 14, "of the Archmage", "Sealed Apprentice Workbook",
     "The seal is a precaution and the handwriting explains why.", "Tome (Int)"),
    ("tome", 16, "of the Hierophant", "Sepulcher Psalter",
     "Bound in something that was recently warm.", "Tome (Int/Spi)"),
    ("tome", 17, "of the Prophet", "Codex of the Patient Flame",
     "It only opens to pages you have already read.", "Tome (Int/Spi)"),
    ("tome", 18, "of the Restorer", "Field Surgeon's Casebook",
     "Each entry ends in a number and most of the numbers are low.", "Tome (Spi)"),
    ("tome", 19, "of the Seer", "Grimoire of Borrowed Weather",
     "Instructions for rain. The rain is not consulted.", "Tome (Spi)"),
    ("tome", 21, "of the Invoker", "Quartermaster's Cipher-Book",
     "Half of it is a code and the other half is complaints.", "Tome (Int)"),
    ("tome", 22, "of the Archmage", "Treatise on Unhelpful Doors",
     "Nine chapters. The doors remain unhelpful.", "Tome (Int)"),
    ("tome", 23, "of the Hierophant", "Chantry of the Drowned Choir",
     "The notation goes underwater at the fourth bar and stays there.", "Tome (Int/Spi)"),
    ("tome", 25, "of the Prophet", "Fenris Confessional Record",
     "The confessor's side is blank throughout.", "Tome (Int/Spi)"),
    ("tome", 26, "of the Restorer", "Bindings and Their Failures",
     "A practical book. The failures are more thorough than the bindings.", "Tome (Spi)"),
    ("tome", 27, "of the Seer", "Hollow's Dream-Register",
     "Names, dates, and what each sleeper saw. The last column is empty.", "Tome (Spi)"),
    ("tome", 29, "of the Archmage", "Index of Things That Answer",
     "Alphabetical. Not recommended.", "Tome (Int)"),
    ("tome", 31, "of the Invoker", "Kraul Rootkeeper's Tally",
     "Counts of a harvest nobody ate.", "Tome (Int)"),
    ("tome", 32, "of the Hierophant", "Antiphon for Thin Light",
     "Written for a choir of two, one of them absent.", "Tome (Int/Spi)"),
    ("tome", 34, "of the Prophet", "Plague-Depths Dosing Book",
     "The doses increase on every page and so does the handwriting's hurry.", "Tome (Int/Spi)"),
    ("tome", 35, "of the Restorer", "Needle-Priest's Compendium",
     "Bound with surgical thread, which it keeps for emergencies.", "Tome (Spi)"),
    ("tome", 36, "of the Archmage", "Lexicon of the Sealed Stacks",
     "Lists every book nobody is permitted to read, including itself.", "Tome (Int)"),
    ("tome", 38, "of the Seer", "Drowning Floor Soundings",
     "Depths, in a column that runs off the bottom of the page.", "Tome (Spi)"),
    ("tome", 39, "of the Invoker", "Grimoire of the Quiet Hour",
     "Meant to be read aloud. Nobody has.", "Tome (Int)"),
    ("tome", 41, "of the Hierophant", "Tome of the Unlit Chancel",
     "Gilt edges, and a thumbprint burned through the frontispiece.", "Tome (Int/Spi)"),
    ("tome", 43, "of the Archmage", "Codex Interminable",
     "The page count disagrees with the pages.", "Tome (Int)"),

    # ---------------- thrown: 14. Ranged slot for the martial classes, and
    # the thinnest type in the game at four items.
    ("thrown", 7, "of the Hunt", "Notched Throwing Iron",
     "Balanced by someone who threw it a great deal.", "Thrown (Agi)"),
    ("thrown", 11, "of the Marksman", "Razor Hill Pitching Spike",
     "Issued in threes. Most come back.", "Thrown (Agi)"),
    ("thrown", 14, "of the Assassin", "Sepulcher Bone-Dart",
     "Fletched with something that was recently attached to a person.", "Thrown (Agi)"),
    ("thrown", 16, "of the Hunt", "Hooked Fishing Javelin",
     "For fish that fight back, and, lately, for the other thing.", "Thrown (Agi)"),
    ("thrown", 18, "of the Beast", "Barrens Hurl-Axe",
     "Short haft, heavy head, no subtlety at all.", "Thrown (Str)"),
    ("thrown", 20, "of the Marksman", "Scout's Weighted Knife",
     "The grip is wrapped for a hand smaller than most.", "Thrown (Agi)"),
    ("thrown", 23, "of the Assassin", "Brood-Barbed Dart",
     "The barb is a leg. It is still articulated.", "Thrown (Agi)"),
    ("thrown", 25, "of the Hunt", "Isle-Keeper's Cast-Spear",
     "Notched once for each thing worth notching.", "Thrown (Agi)"),
    ("thrown", 27, "of the Beast", "Boar-Tusk Throwing Maul",
     "Mostly tusk. The handle is an afterthought and feels like one.", "Thrown (Str)"),
    ("thrown", 30, "of the Marksman", "Aspen Snow-Dart",
     "Weighted for still air, which the Aspen rarely provides.", "Thrown (Agi)"),
    ("thrown", 33, "of the Assassin", "Rootfang Spine",
     "Pulled from something larger and thrown at something larger still.", "Thrown (Agi)"),
    ("thrown", 36, "of the Hunt", "Needle-Point Caltrop-Spike",
     "Thrown, dropped, or left where someone will find it.", "Thrown (Agi)"),
    ("thrown", 39, "of the Beast", "Depths-Forged Hurling Wedge",
     "Cast in a mould that cracked. The crack is part of the balance now.", "Thrown (Str)"),
    ("thrown", 42, "of the Marksman", "Stackwarden's Silent Dart",
     "Made to be thrown in a library and never to be heard landing.", "Thrown (Agi)"),

    ("thrown", 13, "of the Hunt", "Gravewatch Hurl-Stone",
     "Smooth from the river, notched once so it does not slip.", "Thrown (Agi)"),
    ("thrown", 29, "of the Assassin", "Blight-Tipped Harpoon",
     "The tip is hollow and has been refilled more than once.", "Thrown (Agi)"),
    ("thrown", 38, "of the Beast", "Sounding-Weight",
     "Lead, roped, and meant to be dropped. It throws well enough.", "Thrown (Str)"),

    # ---------------- fist_weapon: 15. Twenty classes can hold one and the
    # game had seventeen.
    ("fist_weapon", 8, "of the Assassin", "Knotted Rope-Knuckles",
     "Wet, then dried, then wet again. Hard as a stone now.", "Fist (Agi)"),
    ("fist_weapon", 12, "of the Beast", "Scorpid Claw-Grips",
     "Two pincers, reversed, and a strap to keep them shut.", "Fist (Str)"),
    ("fist_weapon", 15, "of the Duelist", "Sparring Iron",
     "Dented on the inside, which tells you how it was held.", "Fist (Agi)"),
    ("fist_weapon", 17, "of the Assassin", "Gravedigger's Hand-Spade",
     "Short, flat, and sharpened on the edge that does not dig.", "Fist (Agi)"),
    ("fist_weapon", 19, "of the Champion", "Ragefire Cinder-Fist",
     "Still warm. It has not been near a fire in weeks.", "Fist (Str)"),
    ("fist_weapon", 21, "of the Beast", "Thornhide Gauntlet-Claw",
     "The thorns face inward as often as out.", "Fist (Str)"),
    ("fist_weapon", 23, "of the Duelist", "Fenris Duelling Catch",
     "Built to trap a blade. It has trapped several.", "Fist (Agi)"),
    ("fist_weapon", 25, "of the Assassin", "Cavern Silt-Knuckles",
     "Packed with grit that will not wash out and is no longer meant to.", "Fist (Agi)"),
    ("fist_weapon", 27, "of the Gladiator", "Pit-Warden's Clasp",
     "Worn by whoever was still standing. Resized often.", "Fist (Str)"),
    ("fist_weapon", 29, "of the Champion", "Hillsbrad Millstone Fist",
     "A grinding-wheel fragment with a grip cut into it.", "Fist (Str)"),
    ("fist_weapon", 31, "of the Duelist", "Grom's Rest Hand-Hook",
     "For holding a shield down while you deal with the man behind it.", "Fist (Agi)"),
    ("fist_weapon", 33, "of the Beast", "Kraul Burrow-Claws",
     "Made for digging. Repurposed without modification.", "Fist (Str)"),
    ("fist_weapon", 35, "of the Assassin", "Needle-Thin Punch-Dagger",
     "Narrow enough to go between plates and nothing else.", "Fist (Agi)"),
    ("fist_weapon", 37, "of the Gladiator", "Floodwater Grapple-Fist",
     "Barnacled. The barnacles have been left on deliberately.", "Fist (Str)"),
    ("fist_weapon", 40, "of the Champion", "Underdark Crystal Knuckle",
     "A single grown facet, set in a grip of plain leather.", "Fist (Str)"),

    # ---------------- libram: 5. A ranged-slot relic for Paladin, Sun Cleric
    # and Templar, added as a type the same day with nothing to drop.
    ("libram", 14, "of the Hierophant", "Libram of the Second Watch",
     "Thumbed to softness at exactly one page.", "Libram (Int/Spi)"),
    ("libram", 21, "of the Restorer", "Libram of Unearned Mercy",
     "The mercy is not described. The conditions are, at length.", "Libram (Spi)"),
    ("libram", 28, "of the Champion", "Libram of the Standing Oath",
     "Sworn by nine. Signed by three.", "Libram (Str)"),
    ("libram", 34, "of the Hierophant", "Libram of Thin Dawn",
     "Written for the hour before light, by someone who waited it out.", "Libram (Int/Spi)"),
    ("libram", 41, "of the Restorer", "Libram of the Last Rite",
     "Short. It is meant to be finished.", "Libram (Spi)"),

    # ---------------- idol: 2. The Druid relic, same situation.
    ("idol", 18, "of the Seer", "Idol of the Patient Root",
     "Carved from a root that is still, by any honest measure, growing.", "Idol (Spi)"),
    ("idol", 37, "of the Beast", "Idol of the Long Winter",
     "Antler, bound with gut, and warm to hold in any weather.", "Idol (Str)"),
]

#: Where each level band can live. Boss pools are caves and dungeons; quest
#: files are the reward route. Both get used so neither source carries all of
#: it, per Kyle's "throughout caves or Dungeons or quest rewards".
#:
#: Ranges are the files' own existing item_level bands (see the survey in the
#: commit message), so nothing is placed outside content a player of that
#: level would be in.
BOSS_FILES = [
    ("data/loot/deathknell_boss_loot.json", 6, 11),
    ("data/loot/durotar_cave_boss_loot.json", 11, 16),
    ("data/loot/tirisfal_boss_loot.json", 10, 16),
    ("data/loot/echo_isles_boss_loot.json", 15, 18),
    ("data/loot/ragefire_chasm_boss_loot.json", 17, 20),
    ("data/loot/silverpine_boss_loot.json", 17, 23),
    ("data/loot/northern_barrens_boss_loot.json", 19, 23),
    ("data/loot/silverpine_dungeon_loot.json", 20, 28),
    ("data/loot/wailing_caverns_boss_loot.json", 22, 27),
    ("data/loot/broodspiral_boss_loot.json", 22, 27),
    ("data/loot/southern_barrens_boss_loot.json", 23, 27),
    ("data/loot/fenris_boss_loot.json", 24, 27),
    ("data/loot/howling_barrows_boss_loot.json", 26, 27),
    ("data/loot/moonwell_hollow_boss_loot.json", 27, 28),
    ("data/loot/hillsbrad_boss_loot.json", 27, 33),
    ("data/loot/aspen_boss_loot.json", 30, 34),
    ("data/loot/groms_rest_boss_loot.json", 31, 35),
    ("data/loot/razorfen_kraul_boss_loot.json", 31, 37),
    ("data/loot/plague_depths_boss_loot.json", 34, 37),
    ("data/loot/southern_needles_boss_loot.json", 35, 37),
    ("data/loot/drowning_floor_boss_loot.json", 37, 38),
    ("data/loot/underdark_boss_loot.json", 36, 43),
]
QUEST_FILES = [
    ("data/quests/deathknell.json", 3, 11),
    ("data/quests/razor_hill.json", 7, 11),
    ("data/quests/durotar.json", 8, 16),
    ("data/quests/silverpine_north.json", 11, 17),
    ("data/quests/sepulcher.json", 13, 15),
    ("data/quests/echo_isles.json", 13, 18),
    ("data/quests/silverpine_south.json", 15, 20),
    ("data/quests/silverpine_dungeons.json", 16, 25),
    ("data/quests/northern_barrens_hub.json", 17, 23),
    ("data/quests/fenris_isle.json", 17, 24),
    ("data/quests/central_barrens_hub.json", 15, 27),
    ("data/quests/hillsbrad.json", 20, 31),
    ("data/quests/southern_barrens_hub.json", 21, 37),
    ("data/quests/ashenvale_dungeons.json", 22, 32),
    ("data/quests/hillsbrad_dungeons.json", 23, 31),
    ("data/quests/aspen.json", 24, 31),
    ("data/quests/southern_needles.json", 29, 35),
    ("data/quests/underdark_dungeons.json", 31, 40),
    ("data/quests/underdark.json", 33, 39),
]


#: A NAME THAT CARRIES A PLACE HAS TO LAND IN THAT PLACE. Placing purely by
#: level band put "Sepulcher Psalter" in the Central Barrens, which reads as
#: sloppy in a world where everything else is named for where it came from.
#: Items whose names are zone-specific are pinned here; the rest float by
#: level, which is what the neutral names are for.
HOMES = {
    "Deathknell Hymnal": "data/quests/deathknell.json",
    "Gravewatch Hurl-Stone": "data/loot/tirisfal_boss_loot.json",
    "Sounding-Weight": "data/loot/drowning_floor_boss_loot.json",
    "Sepulcher Psalter": "data/quests/sepulcher.json",
    "Sepulcher Bone-Dart": "data/quests/sepulcher.json",
    "Razor Hill Pitching Spike": "data/quests/razor_hill.json",
    "Scorpid Claw-Grips": "data/loot/durotar_cave_boss_loot.json",
    "Ragefire Cinder-Fist": "data/loot/ragefire_chasm_boss_loot.json",
    "Barrens Hurl-Axe": "data/quests/northern_barrens_hub.json",
    "Brood-Barbed Dart": "data/loot/broodspiral_boss_loot.json",
    "Cavern Silt-Knuckles": "data/loot/wailing_caverns_boss_loot.json",
    "Fenris Confessional Record": "data/loot/fenris_boss_loot.json",
    "Fenris Duelling Catch": "data/quests/fenris_isle.json",
    "Isle-Keeper's Cast-Spear": "data/quests/fenris_isle.json",
    "Hollow's Dream-Register": "data/loot/moonwell_hollow_boss_loot.json",
    "Hillsbrad Millstone Fist": "data/loot/hillsbrad_boss_loot.json",
    "Aspen Snow-Dart": "data/loot/aspen_boss_loot.json",
    "Grom's Rest Hand-Hook": "data/loot/groms_rest_boss_loot.json",
    "Kraul Rootkeeper's Tally": "data/loot/razorfen_kraul_boss_loot.json",
    "Kraul Burrow-Claws": "data/loot/razorfen_kraul_boss_loot.json",
    "Rootfang Spine": "data/loot/razorfen_kraul_boss_loot.json",
    "Plague-Depths Dosing Book": "data/loot/plague_depths_boss_loot.json",
    "Depths-Forged Hurling Wedge": "data/loot/plague_depths_boss_loot.json",
    "Needle-Priest's Compendium": "data/loot/southern_needles_boss_loot.json",
    "Needle-Point Caltrop-Spike": "data/quests/southern_needles.json",
    "Drowning Floor Soundings": "data/loot/drowning_floor_boss_loot.json",
    "Floodwater Grapple-Fist": "data/loot/drowning_floor_boss_loot.json",
    "Lexicon of the Sealed Stacks": "data/loot/underdark_boss_loot.json",
    "Stackwarden's Silent Dart": "data/quests/underdark.json",
    "Underdark Crystal Knuckle": "data/quests/underdark_dungeons.json",
}

def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def pick_file(files, ilvl, used):
    """A file whose own level band contains ilvl, preferring an unused one so
    the additions spread rather than piling into whichever file sorts first."""
    fits = [f for f, lo, hi in files if lo <= ilvl <= hi]
    if not fits:
        # Nearest band, so an item at the very top of the range still lands
        # somewhere sensible rather than being dropped.
        fits = [min(files, key=lambda t: min(abs(ilvl - t[1]), abs(ilvl - t[2])))[0]]
    fresh = [f for f in fits if used.get(f, 0) == min(used.get(x, 0) for x in fits)]
    return sorted(fresh)[0]


def main(argv):
    apply = "--apply" in argv
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "bdc", ROOT / "tools/build_durotar_content.py")
    bdc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bdc)

    writes: dict[str, dict] = {}
    used_boss: dict[str, int] = {}
    used_quest: dict[str, int] = {}
    placed = []

    for i, (wt, ilvl, suffix, name, flavor, label) in enumerate(ITEMS):
        slot = "off_hand" if wt == "tome" else (
            "ranged" if wt in ("thrown", "libram", "idol") else "main_hand")
        rarity = "uncommon" if ilvl < 20 else "rare"
        item = bdc.make(name, slot, suffix, max(10, ilvl), flavor,
                        weapon_type=wt, rarity=rarity)
        item["item_level"] = ilvl
        item["required_level"] = max(1, ilvl - 3)
        item["label"] = label
        if wt in ("tome", "libram", "idol"):
            item["attack_speed"] = 0.0

        # Alternate sources so neither caves/dungeons nor quests carry it all.
        pinned = HOMES.get(name)
        if pinned:
            rel = pinned
            to_quest = "/quests/" in rel
        else:
            to_quest = (i % 2 == 1)
            rel = (pick_file(QUEST_FILES, ilvl, used_quest) if to_quest
                   else pick_file(BOSS_FILES, ilvl, used_boss))
        (used_quest if to_quest else used_boss)[rel] = \
            (used_quest if to_quest else used_boss).get(rel, 0) + 1

        data = writes.setdefault(rel, load(rel))
        if to_quest:
            quests = [q for q in data.get("quests", [])
                      if (q.get("level_min") or 1) <= max(1, ilvl - 3)]
            target = (max(quests, key=lambda q: q.get("level_min") or 1)
                      if quests else data["quests"][0])
            target.setdefault("unique_item_defs", []).append(item)
            where = f"{rel}  quest {target.get('quest_id')}"
        else:
            bosses = [k for k in data if not k.startswith("_")
                      and isinstance(data[k], list)]
            boss = sorted(bosses)[i % len(bosses)]
            # THE POOL SETS THE ITEM LEVEL, not this file's authored table.
            # The level above was chosen to fill a band; the boss is chosen
            # separately, by index, so the two had nothing to do with each
            # other and 29 of these items ended up in a pool whose every
            # other drop sat at a different level - an Aspen Snow-Dart at 30
            # among four items at 33. A boss's drops should look like they
            # came off the same boss, and the per-zone content checks were
            # right to call it. The offset is deliberately NOT hardcoded:
            # most pools in the game sit at creature level + 2 and the Aspen
            # and Underdark ones at + 3, so the pool's own items are the only
            # honest authority. See tools/fix_gap_item_levels.py, which did
            # the one-off repair and carries the same rule.
            from tools.fix_gap_item_levels import pool_level, rescale
            want = pool_level(data[boss])
            if want is not None and want != item["item_level"]:
                rescale(item, item["item_level"], want)
                item["item_level"] = want
                item["required_level"] = max(1, want - 3)
            data[boss].append(item)
            where = f"{rel}  boss {boss}"
        placed.append((wt, ilvl, name, where))

    from collections import Counter
    print(f"{len(ITEMS)} items authored\n")
    for wt, n in Counter(w for w, *_ in ITEMS).most_common():
        print(f"   {wt:12} +{n}")
    print(f"\n   into {len(used_boss)} boss pools and {len(used_quest)} quest files")
    print(f"\n{'type':12}{'ilvl':>5}  {'name':40} where")
    for wt, ilvl, name, where in placed:
        print(f"  {wt:12}{ilvl:>5}  {name:40} {where}")

    if not apply:
        print("\n(report only; pass --apply to write)")
        return 0
    for rel, data in writes.items():
        (ROOT / rel).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nwrote {len(writes)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
