#!/usr/bin/env python3
"""Creatures, ability kits, encounter tables and boss loot for the Return Voyage. Idempotent.

    PYTHONPATH=. python3 tools/build_return_voyage_content.py

THE ROSTER IS READ FROM THE ZONE MODULES, not retyped here. An earlier pass had placeholder names
in the trash tables and real names in creatures.json, they did not match, and world/cave_spawns
raises on zone entry for a spawn whose creature is unknown - so the dungeon was broken from the
first step into it and nothing before that step said so. Importing the modules makes the zone
layout the single source of truth for who is in it: if a name is wrong, this script fails here
rather than the game failing there.

LEVELS 43-52 DID NOT EXIST BEFORE THIS. The game topped out at 42, so the galleon's whole roster is
new and its numbers are extrapolated rather than copied: at 40-42 trash abilities sit at 85-110 and
bosses at 120-175, which is about +4 a level, so 47-51 trash lands at 115-145 and a level 52 boss
at 190-240. The raider reuses the three Bloodsail trash types already in the game, because they are
already authored at exactly 38-42 - her rank and file predate her.

THE DOUBLE BOSS. Crane is FROST and Dace is PHYSICAL, deliberately, so that no single resistance or
armour answer covers both; and both carry an AoE on a 5-turn cooldown, so the party is under spread
damage while the tank can only face one of them. Kyle, asked whether to soften a fight that is
about 5x a normal boss's health: "No, boss fight should be hard." Both keep the full 2.5x. If it
plays as a slog rather than a scare, cut the health and leave those two facts alone.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CREATURES = ROOT / "data/creatures/creatures.json"
KITS = ROOT / "data/creatures/ability_kits.json"
ENCOUNTERS = ROOT / "data/creatures/encounters.json"
LOOT = ROOT / "data/loot/return_voyage_boss_loot.json"

BOSS_MULT = 2.5

# ----------------------------------------------------------------- creatures
#: name -> (template, level_lo, level_hi, is_boss)
ROSTER = {
    # The raider's rank and file already exist at 38-42; only her officers are new.
    "Bosun Harl Greave":        ("humanoid_warrior", 40, 40, True),
    "Topman Yanni Sear":        ("humanoid_rogue",   41, 41, True),
    "First Mate Oskar Vane":    ("humanoid_warrior", 41, 41, True),
    "Captain Ruel Scuttler":    ("humanoid_warrior", 42, 42, True),
    # The galleon. All new, because 43-52 was past the end of the game.
    "Bloodsail Marine":         ("humanoid_warrior", 47, 49, False),
    "Bloodsail Gunner":         ("humanoid_ranged",  47, 49, False),
    "Bloodsail Deckmaster":     ("humanoid_warrior", 48, 50, False),
    "Bloodsail Reaver":         ("humanoid_rogue",   49, 51, False),
    "Bloodsail Stormcaller":    ("humanoid_caster",  49, 51, False),
    "Shorebreaker Teska Vohl":  ("humanoid_warrior", 48, 48, True),
    "Quartermaster Ilsa Renn":  ("humanoid_ranged",  48, 48, True),
    "Mastmaster Corbin Ake":    ("humanoid_rogue",   49, 49, True),
    "Powdermaster Juno Felk":   ("humanoid_caster",  50, 50, True),
    "Keelwarden Orso Brann":    ("humanoid_warrior", 51, 51, True),
    "Admiral Hedessa Crane":    ("humanoid_caster",  52, 52, True),
    "Fleet-Captain Orin Dace":  ("humanoid_warrior", 52, 52, True),
}


# -------------------------------------------------------------- encounters
#: {zone name: {creature: weight}}. Bosses sit at weight 0: cave_spawns requires a pinned boss to
#: BE in its zone's table, and splits the table by is_boss rather than by weight, so a 0 keeps them
#: listed without putting them in the scatter pool.
#:
#: THE CABIN'S TABLE HOLDS NOTHING BUT ITS TWO BOSSES, and that is load-bearing. A fixed-spawn zone
#: with no trash_packs falls past populate()'s packs and authored-list branches and SCATTERS
#: SINGLES off its table - an empty zone.trash_spawns does not save it, because an empty list is
#: falsy and the roll is the elif after it. Three weighted entries that looked like harmless
#: flavour once put fifteen one-mob fights in front of the double boss. With only is_boss entries
#: here, the trash dict comes out empty and there is nothing to scatter.
TABLES = {
    "The Bloodsail Raider": {"Bloodsail Swab": 3, "Bloodsail Cannoneer": 2, "Bloodsail Bosun": 1,
                             "Bosun Harl Greave": 0, "Topman Yanni Sear": 0},
    "The Raider's Hold": {"Bloodsail Swab": 3, "Bloodsail Cannoneer": 2, "Bloodsail Bosun": 1,
                          "First Mate Oskar Vane": 0, "Captain Ruel Scuttler": 0},
    "The Bloodsail Anchorage": {"Bloodsail Marine": 3, "Bloodsail Gunner": 2,
                                "Bloodsail Deckmaster": 1,
                                "Shorebreaker Teska Vohl": 0, "Quartermaster Ilsa Renn": 0},
    "The Galleon's Weather Deck": {"Bloodsail Reaver": 3, "Bloodsail Stormcaller": 2,
                                   "Bloodsail Deckmaster": 1, "Mastmaster Corbin Ake": 0},
    "The Galleon's Hold": {"Bloodsail Reaver": 3, "Bloodsail Stormcaller": 2,
                           "Bloodsail Deckmaster": 1,
                           "Powdermaster Juno Felk": 0, "Keelwarden Orso Brann": 0},
    "The Captain's Cabin": {"Admiral Hedessa Crane": 0, "Fleet-Captain Orin Dace": 0},
}

# -------------------------------------------------------------- boss loot
#: boss -> (item level, [(name, slot, kind, type, stat_template), ...])
#: Identity is authored; every stat comes from LootGenerator at rare budget, so these sit on the
#: same curves as the rest of the game's loot rather than on numbers I made up.
POOLS = {
    "Bosun Harl Greave": (42, [
        ("Bosun's Knotted Cord", "waist", "armor", "leather", "agi_physical"),
        ("Starter's Grip", "hands", "armor", "mail", "str_physical"),
        ("Watch-Keeper's Hauberk", "chest", "armor", "mail", "agi_physical"),
        ("Rope-Burned Bracers", "wrist", "armor", "cloth", "int_caster"),
    ]),
    "Topman Yanni Sear": (43, [
        ("Topman's Light Boots", "feet", "armor", "leather", "agi_physical"),
        ("Rigging Knife", "main_hand", "weapon", "dagger", "agi_physical"),
        ("Crosstrees Cowl", "head", "armor", "cloth", "spi_healer"),
        ("Shroud-Gripping Gloves", "hands", "armor", "leather", "agi_int_hybrid"),
    ]),
    "First Mate Oskar Vane": (43, [
        ("First Mate's Sabre", "main_hand", "weapon", "sword_1h", "str_physical"),
        ("Hatchway Shield", "off_hand", "weapon", "shield", "str_physical"),
        ("Press-Gang Pauldrons", "shoulder", "armor", "plate", "str_physical"),
        ("Ledger-Keeper's Robe", "chest", "armor", "cloth", "int_caster"),
    ]),
    "Captain Ruel Scuttler": (44, [
        ("Scuttler's Boarding Axe", "main_hand", "weapon", "axe_1h", "str_physical"),
        ("Captain's Longcoat", "chest", "armor", "leather", "agi_physical"),
        ("Cabin-Door Girdle", "waist", "armor", "plate", "str_int_hybrid"),
        ("Salt-Stained Tome", "off_hand", "weapon", "tome", "spi_healer"),
    ]),
    "Shorebreaker Teska Vohl": (50, [
        ("Shorebreaker's Maul", "main_hand", "weapon", "mace_2h", "str_physical"),
        ("Tideline Greaves", "legs", "armor", "plate", "str_physical"),
        ("Wet Sand Treads", "feet", "armor", "mail", "agi_physical"),
        ("Surf-Worn Mantle", "shoulder", "armor", "cloth", "int_caster"),
    ]),
    "Quartermaster Ilsa Renn": (50, [
        ("Quartermaster's Carbine", "ranged", "weapon", "gun", "agi_physical"),
        ("Signal-Flag Cloak", "back", "armor", "cloth", "int_caster"),
        ("Powder-Measure Gloves", "hands", "armor", "mail", "agi_int_hybrid"),
        ("Bombardier's Helm", "head", "armor", "plate", "str_physical"),
    ]),
    "Mastmaster Corbin Ake": (51, [
        ("Marlinspike", "main_hand", "weapon", "dagger", "agi_physical"),
        ("Mastmaster's Harness", "chest", "armor", "leather", "agi_physical"),
        ("Backstay Bindings", "wrist", "armor", "mail", "agi_int_hybrid"),
        ("Yardarm Cudgel", "main_hand", "weapon", "mace_1h", "spi_healer"),
    ]),
    "Powdermaster Juno Felk": (52, [
        ("Slow-Match Staff", "main_hand", "weapon", "staff", "int_caster"),
        ("Powderkeg Gloves", "hands", "armor", "cloth", "int_caster"),
        ("Magazine Warden's Belt", "waist", "armor", "mail", "str_int_hybrid"),
        ("Scorched Sabatons", "feet", "armor", "plate", "str_physical"),
    ]),
    "Keelwarden Orso Brann": (53, [
        ("Keelwarden's Maul", "main_hand", "weapon", "mace_2h", "str_physical"),
        ("Bulkhead Bulwark", "off_hand", "weapon", "shield", "str_physical"),
        ("Orlop-Deck Legguards", "legs", "armor", "plate", "str_physical"),
        ("Bilge-Damp Vestments", "chest", "armor", "cloth", "spi_healer"),
    ]),
    # TEN, because Kyle asked for "3 pieces of loot at once from a pool of 10" and three distinct
    # draws out of ten is what makes the pair worth killing more than once.
    "Admiral Hedessa Crane": (54, [
        ("Admiral's Rimed Circlet", "head", "armor", "cloth", "int_caster"),
        ("Hoarfrost Shoulderguards", "shoulder", "armor", "mail", "agi_int_hybrid"),
        ("The Fleet's Writ", "off_hand", "weapon", "tome", "int_caster"),
        ("Cold Water Greatsword", "main_hand", "weapon", "sword_2h", "str_physical"),
        ("Dace's Own Sabre", "main_hand", "weapon", "sword_1h", "str_physical"),
        ("Flag-Captain's Cuirass", "chest", "armor", "plate", "str_int_hybrid"),
        ("Stern-Gallery Slippers", "feet", "armor", "cloth", "spi_healer"),
        ("Boarding-Net Gauntlets", "hands", "armor", "leather", "agi_physical"),
        ("Winter-Sailed Leggings", "legs", "armor", "leather", "agi_int_hybrid"),
        ("The Last Order", "main_hand", "weapon", "dagger", "agi_physical"),
    ]),
}


def kit_slug(name):
    return (name.lower().replace("'", "").replace("-", "_")
            .replace(" ", "_").replace(".", ""))


def dmg(name, amount, cooldown=0, school="physical", **kw):
    return dict(name=name, kind="damage", amount=amount, cooldown=cooldown,
                mana_cost=0, school=school, **kw)


def dot(name, amount, cooldown, duration, school="physical", **kw):
    return dict(name=name, kind="dot", amount=amount, cooldown=cooldown,
                mana_cost=0, school=school, duration=duration, **kw)


def debuff(name, cooldown, duration, stat_mods, school="physical"):
    return dict(name=name, kind="debuff", amount=0, cooldown=cooldown, mana_cost=0,
                school=school, duration=duration, stat_mods=stat_mods)


def buff(name, cooldown, duration, stat_mods, school="physical"):
    return dict(name=name, kind="buff", amount=0, cooldown=cooldown, mana_cost=0,
                school=school, duration=duration, stat_mods=stat_mods, self_only=True)


KITSETS = {
    # ---- the galleon's rank and file
    "Bloodsail Marine": [
        dmg("Boarding Cutlass", 122),
        dmg("Shield Shove", 96, cooldown=3),
        debuff("Hamstring", 4, 2, {"agility": -34}),
    ],
    "Bloodsail Gunner": [
        dmg("Musket Shot", 128),
        dmg("Point-Blank Volley", 142, cooldown=4),
        dot("Powder Burn", 36, 3, 3, school="fire"),
    ],
    "Bloodsail Deckmaster": [
        dmg("Belaying Pin", 130),
        dmg("Drive Them On", 104, cooldown=3,
            rider={"effect": "buff", "duration": 3, "stat_mods": {"attack_power": 26}}),
        buff("Hold The Deck", 6, 4, {"defense_rating": 30}),
    ],
    "Bloodsail Reaver": [
        dmg("Gutting Hook", 138),
        dmg("Throat Cut", 158, cooldown=4),
        dot("Deep Bleed", 44, 3, 3),
    ],
    "Bloodsail Stormcaller": [
        dmg("Squall Bolt", 134, school="nature"),
        dmg("Breaking Wave", 112, cooldown=5, school="frost", is_aoe=True),
        debuff("Soaked", 4, 3, {"fire_resistance": -30}),
    ],
    # ---- the raider's officers
    "Bosun Harl Greave": [
        dmg("Bosun's Starter", 132, boss_rework=1),
        dmg("Crack of the Rope", 118, cooldown=3),
        dmg("Lay About You", 104, cooldown=5, is_aoe=True),
        buff("Rally the Watch", 8, 4, {"attack_power": 34}),
    ],
    "Topman Yanni Sear": [
        dmg("Drop from the Rigging", 146, boss_rework=1),
        dot("Rigging Knife", 42, 3, 3),
        dmg("Swing Across", 128, cooldown=4),
        debuff("Cut the Lines", 5, 3, {"agility": -38}),
    ],
    "First Mate Oskar Vane": [
        dmg("First Mate's Sabre", 148, boss_rework=1),
        dmg("Press-Gang Shove", 122, cooldown=3),
        dmg("Clear the Hatchway", 116, cooldown=5, is_aoe=True),
        buff("No One Passes", 7, 4, {"defense_rating": 44}),
    ],
    "Captain Ruel Scuttler": [
        dmg("Scuttler's Cutlass", 164, boss_rework=1),
        dmg("Pistol at the Belt", 140, cooldown=3),
        dmg("Sweep the Cabin", 126, cooldown=5, is_aoe=True),
        dot("Rusted Blade", 48, 4, 3),
        buff("Fight for the Ship", 99, 30, {"attack_power": 50}, ),
    ],
    # ---- the galleon's officers
    "Shorebreaker Teska Vohl": [
        dmg("Shorebreaker's Maul", 172, boss_rework=1),
        dmg("Drive Into the Sand", 144, cooldown=3),
        dmg("Wave Over the Neck", 132, cooldown=5, school="frost", is_aoe=True),
        debuff("Footing Gone", 4, 2, {"dodge_rating": -40}),
    ],
    # KYLE'S IDEA, and it belongs to her because of where she stands: the second neck is at the
    # head of the cove, directly under the galleon's broadside. "a cool idea for an attack would
    # be him getting the ship cannons to attack the party as an AoE bombardment." So she does not
    # fire anything herself - she signals, and the ship answers. Two abilities rather than one, on
    # offset cooldowns, so there is a beat between the flag going up and the beach coming apart.
    "Quartermaster Ilsa Renn": [
        dmg("Quartermaster's Carbine", 156, boss_rework=1),
        debuff("Run Up the Signal", 6, 2, {"dodge_rating": -36}),
        dmg("Broadside from the Anchorage", 168, cooldown=5, is_aoe=True),
        dot("Splinter Wounds", 46, 4, 3),
    ],
    "Mastmaster Corbin Ake": [
        dmg("Marlinspike", 178, boss_rework=1),
        dmg("Down the Backstay", 152, cooldown=3),
        dmg("Let Fall the Yard", 138, cooldown=5, is_aoe=True),
        debuff("Tangled in the Sheets", 5, 3, {"agility": -42}),
    ],
    "Powdermaster Juno Felk": [
        dmg("Scattering Charge", 182, school="fire", boss_rework=1),
        dmg("Slow Match", 150, cooldown=3, school="fire"),
        dmg("The Whole Magazine", 164, cooldown=5, school="fire", is_aoe=True),
        dot("Burning Wadding", 56, 4, 3, school="fire"),
    ],
    "Keelwarden Orso Brann": [
        dmg("Keelwarden's Maul", 196, boss_rework=1),
        dmg("Against the Bulkhead", 168, cooldown=3),
        dmg("Shake Her Timbers", 150, cooldown=5, is_aoe=True),
        buff("Set Against the Door", 7, 4, {"defense_rating": 52}),
    ],
    # FROST, and nothing she does is physical. Pair this with Dace below.
    "Admiral Hedessa Crane": [
        dmg("Admiral's Rime", 214, school="frost", boss_rework=1),
        dmg("Hoarfrost Lash", 186, cooldown=3, school="frost"),
        dmg("The Cold Off the Water", 172, cooldown=5, school="frost", is_aoe=True),
        debuff("Still the Blood", 5, 3, {"haste": -30, "agility": -40}, school="frost"),
        buff("The Fleet Does Not Strike", 99, 30, {"spell_power": 60}, school="frost"),
    ],
    # PHYSICAL, and nothing he does is magic. One resistance answer cannot cover the pair.
    "Fleet-Captain Orin Dace": [
        dmg("Fleet-Captain's Sabre", 218, boss_rework=1),
        dmg("Run Him Through", 190, cooldown=3),
        dmg("Across the Cabin", 176, cooldown=5, is_aoe=True),
        dot("Opened Up", 62, 4, 3),
        buff("Hold Her Cabin", 99, 30, {"attack_power": 64}),
    ],
}


def loot_audit(rows):
    """Kyle's standing rule: loot must not lean on one armour class or weapon type.

    Checked over the WHOLE set, not per pool - a four-item pool cannot carry all four armour
    classes and demanding it would just produce four identical-looking pools.

    THE THRESHOLDS SCALE WITH THE SET. They were fixed numbers tuned for the Return Voyage's 46
    items, and the first thing that happened when Rocky Pass reused this function was four
    failures on a 16-item set that is, in fact, evenly spread: 3 cloth, 3 leather, 3 mail, 2
    plate out of 11 armour pieces is as flat as 11 pieces can be. A check whose bar is set by a
    different data set's size is a check that fails on correct data, which is the fastest way to
    train somebody to ignore it."""
    from collections import Counter
    armour = Counter(t for _n, _s, k, t, _st in rows if k == "armor")
    weapons = Counter(t for _n, _s, k, t, _st in rows if k == "weapon")
    templates = Counter(st for *_x, st in rows)
    problems = []
    n_armour = sum(armour.values())
    n_weapons = sum(weapons.values())
    # Each armour class should carry at least half an even share, and never fewer than 2.
    floor_each = max(2, int(n_armour / 4 * 0.5))
    for cls in ("cloth", "leather", "mail", "plate"):
        if armour[cls] < floor_each:
            problems.append(f"only {armour[cls]} {cls} pieces of {n_armour} armour items "
                            f"(at least {floor_each} expected)")
    # No weapon type may be more than a third of the weapons, and never fewer than 3 allowed.
    cap = max(3, int(n_weapons / 3))
    if max(weapons.values(), default=0) > cap:
        hog = max(weapons, key=weapons.get)
        problems.append(f"{weapons[hog]} of {n_weapons} weapons are {hog} (cap {cap})")
    missing = {"str_physical", "agi_physical", "int_caster", "spi_healer",
               "str_int_hybrid", "agi_int_hybrid"} - set(templates)
    if missing:
        problems.append(f"no items for {', '.join(sorted(missing))}")
    dupes = [n for n, c in Counter(n for n, *_r in rows).items() if c > 1]
    if dupes:
        problems.append(f"duplicate item names: {', '.join(dupes)}")
    print(f"  armour: {dict(armour)}")
    print(f"  weapons: {dict(weapons)}")
    print(f"  templates: {dict(templates)}")
    return problems


def merge_json(path, key, additions, label):
    """Add entries to a big shared data file WITHOUT reformatting the rest of it.

    The first version wrote the whole file back at indent=1 and produced a
    43,000-line diff for a 16-entry change - which is not a diff anybody can
    review, and churns a file every other zone in the game depends on. So the
    existing formatting is detected from the file itself rather than assumed,
    and the write is refused if it would rewrite lines it did not mean to.
    """
    original = path.read_text(encoding="utf-8")
    data = json.loads(original)
    bucket = data[key] if key in data else data
    before = len(bucket)

    indent, newline = _detect_format(data, original)
    bucket.update(additions)
    out = json.dumps(data, indent=indent, ensure_ascii=False) + ("\n" if newline else "")
    path.write_text(out, encoding="utf-8")
    print(f"  {label}: {len(bucket) - before} new, {len(bucket)} total "
          f"(indent={indent}, {len(out.splitlines()) - len(original.splitlines())} lines added)")


def _detect_format(data, original):
    """(indent, trailing_newline) that reproduces `original` byte for byte."""
    for indent in (2, 4, 1, None):
        body = json.dumps(data, indent=indent, ensure_ascii=False)
        for newline in (True, False):
            if body + ("\n" if newline else "") == original:
                return indent, newline
    raise AssertionError("cannot reproduce this file's formatting - writing it back would "
                         "reformat every line, so refusing rather than churning it")


def main():
    import tools.handbuilt_bloodsail_raider as R
    import tools.handbuilt_bloodsail_galleon as G

    # ---- the roster the zones actually declare, so a typo fails here
    declared = set(R.TRASH) | set(R.DECK_BOSSES) | set(R.HOLD_BOSSES)
    declared |= set(G.TRASH_LOW) | set(G.TRASH_HIGH) | set(G.ANCHORAGE_BOSSES)
    declared |= {G.DECK_BOSS, G.CABIN_LEAD, G.CABIN_SECOND} | set(G.HOLD_BOSSES)
    existing = set(json.loads(CREATURES.read_text())["creatures"])
    unknown = declared - set(ROSTER) - existing
    if unknown:
        print("FAILED: the zone modules name creatures that nothing defines:")
        for n in sorted(unknown):
            print(f"  - {n}")
        return 1
    unused = set(ROSTER) - declared
    if unused:
        print("FAILED: this file defines creatures no zone places:")
        for n in sorted(unused):
            print(f"  - {n}")
        return 1
    print(f"roster agrees: {len(declared)} creatures named by the zones, all defined")

    creatures = {}
    for name, (template, lo, hi, is_boss) in ROSTER.items():
        entry = {"template": template, "level_range": [lo, hi], "is_boss": is_boss,
                 "ability_kit": kit_slug(name)}
        if is_boss:
            entry["boss_multiplier"] = BOSS_MULT
        creatures[name] = entry
    merge_json(CREATURES, "creatures", creatures, "creatures.json")
    merge_json(KITS, "kits", {kit_slug(n): k for n, k in KITSETS.items()}, "ability_kits.json")

    # ---- encounter tables, hung off the parent zone each dungeon declares as its .region
    enc_raw = ENCOUNTERS.read_text(encoding="utf-8")
    enc = json.loads(enc_raw)
    indent, newline = _detect_format(enc, enc_raw)
    # UNDER "zones", NOT AT THE TOP LEVEL. CreatureManager loads
    # json.load(f).get("zones", {}) and nothing else, so a table written beside that key is
    # invisible to the game while looking perfectly correct in the file. Written at the top level
    # first, every one of the six zones populated with ZERO bosses and ZERO trash - populate()
    # returns early on an empty table, silently, so the dungeons were simply empty. The top-level
    # keys that DO exist there ("Widow's Lair" and friends) are a different structure read by
    # world/quest_locator, which is exactly why it looked like the right place.
    region = enc.setdefault("zones", {}).setdefault("The Crossing", {})
    caves = region.setdefault("caves", {})
    for zone_name, table in TABLES.items():
        caves[zone_name] = {"creatures": dict(table)}
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False)
                          + ("\n" if newline else ""), encoding="utf-8")
    print(f"  encounters.json: {len(TABLES)} tables under 'The Crossing'")

    # ---- boss loot
    from entities.loot_generator import LootGenerator
    gen = LootGenerator()
    out = {"_notes": ("Return Voyage boss pools. Identity is hand-authored in "
                      "tools/build_return_voyage_content.py; every stat came from LootGenerator "
                      "at rare budget, so these sit on the same curves as the rest of the game's "
                      "loot. Admiral Hedessa Crane's pool of ten is the shared hoard for the "
                      "double boss - see entities/boss_loot.MULTI_DROP / SHARED_HOARD.")}
    rows = []
    for boss, (ilvl, items) in POOLS.items():
        built = []
        for (name, slot, kind, atype, template) in items:
            if kind == "armor":
                it = gen.generate_armor_piece(slot, atype, template, ilvl, "rare")
            else:
                it = gen.generate_weapon(slot, atype, template, ilvl, "rare", strict=True)
            if it is None:
                print(f"FAILED: the generator would not build {name} ({atype} {slot})")
                return 1
            d = it.to_dict() if hasattr(it, "to_dict") else {}
            d["name"] = name
            d["item_id"] = "rv_" + name.lower().replace("'", "").replace(" ", "_")
            built.append(d)
            rows.append((name, slot, kind, atype, template))
        out[boss] = built
    problems = loot_audit(rows)
    if problems:
        print("\nFAILED - fix the pools, not the check:")
        for pr in problems:
            print(f"  - {pr}")
        return 1
    LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  {LOOT.relative_to(ROOT)}: {len(POOLS)} pools, {len(rows)} items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
