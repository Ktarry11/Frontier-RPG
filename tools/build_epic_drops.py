#!/usr/bin/env python3
"""The named epics: world drops and the occasional dungeon purple. Idempotent.

    PYTHONPATH=. python3 tools/build_epic_drops.py

Kyle, 2026-10-28: "We can get the occasional drops as epic after lvl 30 in Dungeons and also for
world drop after lvl 30. Think of how wow does it with world drops."

Kyle, 2026-10-29: "Each epic should be unique bro and spread across the classes... i'd like to see
more and more 'open world' epics pop up... These will be hand crafted. But also we can get the open
world epics that are just procedurally generated with affixes like the greens/blues... Also some of
the dungeons can drop them at a small chance."

WHAT THE AUDIT FOUND. All 892 hand-authored dungeon items are rarity rare - there is not one epic
drop anywhere in the game - while two upgrade kits take any crafted piece to epic plus five item
levels. So there was no gear reason to run a dungeon. The procedural roller already gates epic at
level 30 exactly as Kyle describes, but hand-authored boss pools bypass it: get_fixed_boss_loot
returns a fixed item before the procedural roll ever happens, and all 44 bosses above level 30 have
one.

WOW'S WORLD-DROP MODEL IS WHY THESE ARE NAMED AND FEW. A world epic in WoW is memorable because it
is a specific item - people know the name, they know roughly what drops it, and almost nobody has
one. A purple generated on the fly from a stat budget cannot do that however rare you make it, so
these are hand-authored: thirty-six items, each with its own name and its own reason to exist.

STATS COME FROM THE ENGINE, NOT FROM ME. Only the identity is authored here - name, slot, type,
item level, who it suits. LootGenerator fills in the actual numbers at epic budget, which is the
same code path every other item in the game goes through. Hand-writing stat blocks for 36 epics
would mean hand-deriving the armour and damage curves, and the first one I got slightly wrong would
sit there being slightly wrong forever.

THREE GUARDS, each of which exists because the thing it guards against already happened:

  * strict=True on generate_weapon. "The Quiet Argument" was authored as a spi_healer mace and
    "The Deep Bloom's Root" as a spi_healer staff; spi_healer was valid on no weapon type, so
    generate_weapon substituted valid_templates[0] and both became int_caster items. Silently.
    The table still said healer. Both weapon types now accept spi_healer, and a future mismatch
    raises instead of lying.

  * coherent(). A stat template only gates which gear SUFFIXES are eligible, so "agi_physical"
    means "may roll any physical-ish suffix" rather than "carries agility". An agility 2H mace
    came back carrying agility in 1 roll of 8, and 17 of 36 epics had no primary stats at all.
    Each item is rerolled until it carries the stat it is named for, meaningfully. The engine is
    untouched - that randomness is correct for procedural drops and wrong for a named item.

  * ranged slots. 24 ranged weapons were authored into main_hand, so equipping a bow took the
    melee weapon off. That was fixed in the data and in Equipment._resolve_slot, and then I
    reintroduced it here by regenerating from a source that still said main_hand. The check is
    upstream of the build now, on the table itself.

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
    # --- the 43-50 band, which did not exist. Kyle asked for the agility polearm, the agility
    # two-handed sword and the agility two-handed mace by name; all three are here.
    ("The Understudy", "shoulder", "armor", "plate", 44, "str_int_hybrid",
     "Built to the measurements of somebody more famous, and never collected."),
    ("The Standing Order", "main_hand", "weapon", "polearm", 45, "agi_physical",
     "Nobody has rescinded it. Nobody remembers issuing it either."),
    ("Threshing Day", "main_hand", "weapon", "mace_2h", 46, "agi_physical",
     "A farm tool that got good at something else and never went back."),
    ("Last Word on the Matter", "main_hand", "weapon", "sword_2h", 47, "agi_physical",
     "The argument it ended is not recorded. The ending is well attested."),
    ("Saltmother's Shawl", "back", "armor", "cloth", 48, "spi_healer",
     "Knitted by somebody who had buried enough people to know what the living need."),
    ("Three Winters' Boots", "feet", "armor", "mail", 49, "agi_physical",
     "Resoled twice, by two different hands, neither of them a cobbler's."),
    ("The Inventory", "waist", "armor", "plate", 50, "str_physical",
     "Every pouch labelled, in a hand that expected somebody else to read it."),
    ("Quietkeep", "off_hand", "weapon", "tome", 50, "spi_healer",
     "Half the pages are blank. The other half are names, and the list is still going."),

    # ---- the 51-58 band. Kyle, 13 Nov 2026: "make about 5 new world epics that drop at 50+",
    # and "TRINKETS CAN DO THINGS NOW - MOVE THE 50+ TRINKETS SLOWLY FROM BEING BASIC STAT
    # STICKS". Two of the five are trinkets with a proc (PROCS below). The other three fill
    # weapon types no epic had used (bow, axe_1h) and the hands slot.
    ("Long Way Round", "ranged", "weapon", "bow", 52, "agi_physical",
     "Somebody carried it the whole length of two worlds and never found a reason to draw it "
     "until the last mile."),
    ("Kindling", "main_hand", "weapon", "axe_1h", 53, "str_physical",
     "It was a wood axe for forty years, and the man who owned it would be upset to see what "
     "it gets used for now."),
    ("The Borrowed Hour", "trinket", "armor", "accessory", 54, "spi_healer",
     "A pocket watch that stopped on the day of the Integration and has been right about "
     "everything since."),
    ("The Even Hand", "hands", "armor", "leather", 56, "agi_int_hybrid",
     "The left glove is more worn than the right, because whoever owned them kept the right "
     "hand free for shaking."),
    ("Witness", "trinket", "armor", "accessory", 57, "agi_physical",
     "A brass spyglass lens with a crack across it, kept by someone who saw a thing happen and "
     "was never asked about it."),
]

#: Occasional drops from bosses at level 30 and up, themed to the dungeons that exist up there -
#: the Crystalline Underdark's archive, the Drowning Floor, the Southern Needles, and from 47 up
#: the two Bloodsail ships of the Return Voyage.
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
    ("Thermal-Borne Greaves", "legs", "armor", "mail", 36, "agi_int_hybrid",
     "Updraft off a mesa top will hold a feather for an hour. These were found at the bottom."),
    # --- the Bloodsail band, 44-50.
    ("Scuttler's Own Hook", "main_hand", "weapon", "fist_weapon", 44, "agi_physical",
     "He kept the hand. He just found the hook more use in a boarding action."),
    ("The Ledger of Debts", "chest", "armor", "cloth", 46, "int_caster",
     "Every name crossed out, and the crossings-out are in a different ink to the names."),
    ("Dace's Long Count", "legs", "armor", "leather", 47, "agi_int_hybrid",
     "Tally marks down both thighs, in groups of five, running out of room."),
    ("Breakwater", "off_hand", "weapon", "shield", 48, "str_physical",
     "Took the whole sea at Booty Bay for a season and gave none of it back."),
    ("What Floated Back", "head", "armor", "mail", 49, "agi_physical",
     "The ship did not. This did, three weeks later, on the same tide."),
    ("The Admiral's Last Order", "main_hand", "weapon", "sword_1h", 50, "str_int_hybrid",
     "Given in a cabin, to nobody who outlived the giving of it."),

    # ---- TEMPEST ISLE, 51-58. Two from each dungeon, and every one of them fills a slot that
    # had NO epic at all. Checked rather than asserted: across the 36 existing epics, the slots
    # neck, finger, trinket and ranged were empty, and the weapon types axe_1h, bow, crossbow,
    # gun and wand had never been used. Thirteen of the 36 are main_hand, which is exactly the
    # lopsidedness Kyle's standing rule is about, so not one of these four is a main-hand.
    ("Ashhold's Writ", "neck", "armor", "accessory", 54, "str_int_hybrid",
     "The deed to a hall four hundred feet down, carried from hall to rented room to a bunk on a "
     "goblin barge, and never once sold."),
    ("The Unbanked Fire", "trinket", "armor", "accessory", 55, "int_caster",
     "They walked out of Khaz Varun in a hurry and nobody damped the forge. It has been burning "
     "ever since, on nothing."),
    ("The Mountain's Signet", "ring", "armor", "accessory", 57, "spi_healer",
     "Found in the crack in its chest, which is the only part of a mountain that can be reached "
     "into."),
    ("Ashfall", "ranged", "weapon", "gun", 58, "agi_physical",
     "Dark Iron barrel, goblin firing mechanism, and an argument about the trigger that is still "
     "going on in Cinderwharf."),
    # Three more for the isle (Kyle, 13 Nov 2026: "about 3 new epic items from the boss drops.
    # Since we want to keep a healthy amount of epics"). A two-handed mace, the first wand, and
    # a tank trinket that does something.
    ("The Unmaking", "main_hand", "weapon", "mace_2h", 57, "str_physical",
     "Thane Morrun swung it at the wall of his own hall for a hundred years, and the wall still "
     "shows where."),
    ("Serpent's Second Skin", "trinket", "armor", "accessory", 60, "str_physical",
     "A scale the Molten Serpent shed while it was under the lava, and it has never fully "
     "cooled."),
    ("What the Oracle Saw", "ranged", "weapon", "wand", 61, "int_caster",
     "Ysmel looked into the caldera every day until it looked back, and this is the rod she was "
     "holding when it did."),
]

#: Trinkets that DO something. Kyle, 10 Nov: "trinkets over 50+ WILL AND MUST start to
#: actually do stuff." The payload is a StatusEffect proc dict - the same engine talents use
#: (combat/status_effects.py, fire_proc_trigger) - carried by the item and hung on the wearer
#: by Character._sync_equipment_procs while it is equipped.
#:
#: The Unbanked Fire is Wrath of Cenarius: damaging spells sometimes flood the caster with
#: spell power for a few turns. Sized against a level 55 caster's gear, a spike of roughly a
#: third of their spell power, which is where Wrath of Cenarius sat in its own tier.
PROCS = {
    "The Unbanked Fire": {
        "trigger": "on_damage_cast",
        "chance": 8,
        "icd": 5,
        "apply_effect": {
            "effect_id": "unbanked_fire_blaze",
            "name": "Uninsured Blaze",
            "effect_type": "buff",
            "duration": 3,
            "stat_mods": {"spell_power": 40},
            "on_target": False,
        },
        "describe": "Your damaging spells have a chance to grant 40 spell power for 3 turns.",
    },
    # The healer's version of the same idea.
    "The Borrowed Hour": {
        "trigger": "on_heal_cast", "chance": 10, "icd": 5,
        "apply_effect": {"effect_id": "borrowed_hour_minute", "name": "A Spare Minute",
                         "effect_type": "buff", "duration": 3,
                         "stat_mods": {"healing_power": 60}, "on_target": False},
        "describe": "Your healing spells have a chance to grant 60 healing power for 3 turns.",
    },
    # Crits feed it, for anyone who hits with a weapon.
    "Witness": {
        "trigger": "on_crit", "chance": 20, "icd": 4,
        "apply_effect": {"effect_id": "witness_clear_sight", "name": "Clear Sight",
                         "effect_type": "buff", "duration": 3,
                         "stat_mods": {"attack_power": 70}, "on_target": False},
        "describe": "Your critical strikes have a chance to grant 70 attack power for 3 turns.",
    },
    # A tank trinket: being hit sometimes heals you. heal_flat lands on the wearer.
    "Serpent's Second Skin": {
        "trigger": "on_damage_taken", "chance": 12, "icd": 4, "heal_flat": 220,
        "describe": "When you are hit, you have a chance to heal for 220.",
    },
}

#: An item named for a stat has to carry it. See coherent().
LEAD_SHARE = 0.25
MAX_REROLLS = 200


def lead_stats(gen, stat_template):
    """The primary stat(s) this template exists to deliver."""
    return gen._TEMPLATE_LEAD.get(stat_template, frozenset())


def templateless(gen, kind, atype):
    """True for an item type the engine generates without consulting a stat
    template at all - a shield, whose budget goes to stamina, armour and
    block value by construction. Asking such an item to carry strength is
    asking for something generate_weapon never promised, and the first run
    of the coherence guard spent 200 rerolls discovering that about "What
    the Tide Kept" before failing the build. The table still names a
    template for a shield, because the name and the icon come from it."""
    if kind != "weapon":
        return False
    wt = gen.weapon_types["weapon_types"].get(atype, {})
    return not wt.get("valid_stat_templates")


def coherent(item, gen, stat_template, kind=None, atype=None):
    """True if the item carries the stat it is named for, meaningfully.

    Items the engine builds without a template (shields) are coherent by
    construction and exempt. Everything else must put at least LEAD_SHARE of
    its primary stat points into one of its template's lead stats -
    present-but-trivial is the failure mode this catches, where an "agility"
    weapon rolls 1 agility and 40 stamina.
    """
    if kind is not None and templateless(gen, kind, atype):
        return True
    leads = lead_stats(gen, stat_template)
    if not leads:
        return True
    primaries = item.primary_stats or {}
    total = sum(primaries.values())
    if not total:
        return False
    best = max((primaries.get(s, 0) for s in leads), default=0)
    return best >= LEAD_SHARE * total


def build_one(gen, name, slot, kind, atype, ilvl, template):
    """Generate until the item is coherent, or report which one would not be."""
    for _ in range(MAX_REROLLS):
        if kind == "armor":
            item = gen.generate_armor_piece(slot, atype, template, ilvl, "epic")
        else:
            item = gen.generate_weapon(slot, atype, template, ilvl, "epic", strict=True)
        if item is None:
            return None, f"the generator would not build {name} ({atype} {slot})"
        if coherent(item, gen, template, kind, atype):
            return item, None
    return None, (f"{name} ({atype}, {template}) never rolled {int(LEAD_SHARE * 100)}% of its "
                  f"primary stats into {'/'.join(sorted(lead_stats(gen, template)))} "
                  f"in {MAX_REROLLS} tries - the suffix pool for this template may have no "
                  f"suffix that leads with it")


def check_ranged_slots(rows):
    """A ranged weapon type authored into a melee slot - the regression I
    reintroduced after fixing it once, so the check sits on the table."""
    wt = json.loads((ROOT / "data/items/weapon_types.json").read_text(encoding="utf-8"))["weapon_types"]
    ranged = {k for k, v in wt.items() if v.get("hand") == "ranged"}
    return [f"{name} is a {atype} (ranged) but authored into slot '{slot}'"
            for name, slot, kind, atype, _il, _st, _f in rows
            if kind == "weapon" and atype in ranged and slot != "ranged"]


def audit(rows):
    """Kyle's standing rule: boss and quest loot must not lean on one armour class or weapon type."""
    armour = Counter(t for _n, _s, k, t, _il, _st, _f in rows if k == "armor")
    weapons = Counter(t for _n, _s, k, t, _il, _st, _f in rows if k == "weapon")
    templates = Counter(st for *_x, st, _f in rows)
    problems = []
    for cls in ("cloth", "leather", "mail", "plate"):
        if armour[cls] < 2:
            problems.append(f"only {armour[cls]} {cls} pieces - the spread is lopsided")
    cap = 3
    if max(weapons.values(), default=0) > cap:
        hog = max(weapons, key=weapons.get)
        problems.append(f"{weapons[hog]} of the weapons are {hog} (cap {cap})")
    if len(templates) < 6:
        missing = {"str_physical", "agi_physical", "int_caster", "spi_healer",
                   "str_int_hybrid", "agi_int_hybrid"} - set(templates)
        problems.append(f"only {len(templates)} stat templates of 6 - missing "
                        f"{', '.join(sorted(missing))}")
    share = max(templates.values(), default=0) / max(len(rows), 1)
    if share > 0.40:
        hog = max(templates, key=templates.get)
        problems.append(f"{templates[hog]} of {len(rows)} epics are {hog} "
                        f"({share:.0%}) - Kyle: \"spread across the classes\"")
    names = [n for n, *_r in rows]
    dupes = [n for n, c in Counter(names).items() if c > 1]
    if dupes:
        problems.append(f"duplicate names: {', '.join(dupes)} - Kyle: \"Each epic should be unique\"")
    print(f"  armour: {dict(armour)}")
    print(f"  weapons: {dict(weapons)}")
    print(f"  stat templates: {dict(templates)}")
    return problems


def main():
    from entities.loot_generator import LootGenerator
    gen = LootGenerator()

    rows = WORLD + DUNGEON
    print(f"spread check over {len(rows)} epics:")
    problems = audit(rows) + check_ranged_slots(rows)
    if problems:
        print("\nFAILED - fix the table, not the check:")
        for p in problems:
            print(f"  - {p}")
        return 1

    out = {"_notes": ("Named epic drops. WORLD items drop from anything at level 30+ at a very "
                      "low rate; DUNGEON items are the occasional purple off a level 30+ boss. "
                      "Identity is hand-authored in tools/build_epic_drops.py; every stat below "
                      "came from LootGenerator at epic budget, so these sit on the same curves "
                      "as the rest of the game's loot, and each was rerolled until it carried "
                      "the stat it is named for. Rolled by entities/epic_drops.py.")}

    # KEEP WHAT IS ALREADY THERE. The stats come from LootGenerator, which is random, so this
    # script used to re-roll EVERY epic in the game each time it ran. Adding four new epics on
    # 10 Nov silently re-rolled the other 36 - stats that had been checked against the rares in
    # 280a61e - and it went out in the push before anyone noticed. An epic is now rolled once,
    # when it first appears in the table, and kept by item_id from then on. To deliberately
    # re-roll one, delete its entry from the JSON and run this again.
    p = ROOT / "data/loot/epic_drops.json"
    try:
        existing = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        existing = {}

    rerolled = 0
    kept = 0
    for key, table in (("world", WORLD), ("dungeon", DUNGEON)):
        have = {d.get("item_id"): d for d in existing.get(key, [])}
        items = []
        for name, slot, kind, atype, ilvl, template, flavour in table:
            item_id = "epic_" + name.lower().replace("'", "").replace(" ", "_")
            if item_id in have:
                d = dict(have[item_id])
                kept += 1
            else:
                item, err = build_one(gen, name, slot, kind, atype, ilvl, template)
                if err:
                    print(f"FAILED: {err}")
                    return 1
                d = item.to_dict() if hasattr(item, "to_dict") else {}
                if not coherent(item, gen, template, kind, atype):
                    rerolled += 1
            d["name"] = name
            d["flavor_text"] = flavour
            # The generated item_id carries a uuid, which would make this file churn on every run.
            d["item_id"] = item_id
            # Procs are authored here, never rolled, so they are applied every run.
            if name in PROCS:
                d["proc"] = PROCS[name]
            else:
                d.pop("proc", None)
            items.append(d)
        out[key] = items
        print(f"\n  {key}: {len(items)} items, item level "
              f"{min(i['item_level'] for i in items)}-{max(i['item_level'] for i in items)}")

    p.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nkept {kept} existing epics unchanged, rolled {len(rows) - kept} new")
    print(f"wrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
