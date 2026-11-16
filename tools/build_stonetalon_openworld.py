#!/usr/bin/env python3
"""Stonetalon's open-world creatures, rares, encounter tables, rare loot and gathering. Idempotent.

    PYTHONPATH=. python3 tools/build_stonetalon_openworld.py

docs/stonetalon_brief.md. Kyle, 15 Nov 2026: Stonetalon, 26-32, two zones, scarred vs untouched. The enemies he
picked: the Venture Co., the Grimtotem, the Windshear harpies, and Earth beasts and elementals.

    STONETALON EAST (26-29): the side the volcano knocked flat
      the open ground        ridge cougars, grey elk, black bears, ash vultures
      The Blowdown           ash drifters off the volcano, elk and vultures in the grey   rare: Old Greyhide
      Venture Salvage Yard   the Venture Co. cutting up the fallen giants                 rare: Yard Boss Krizzle
      Windshear Crag         the Windshear harpies                                        rare: Matron Shrieka
      The Standing Grove     the forest the blast missed: bears, cougars, bull elk        rare: Broadpaw
      Grimtotem Compound     the hardline clan                                            rare: Hargol Bloodhorn
      The Mulgore Rim        what used to be tauren, walking at the edge of the dark      rare: The Risen Hunter

SPRITES are stand-ins until Kyle's Stonetalon creature sheet lands (docs/stonetalon_art_prompts.md sheet 4):
goblin sappers and the overseer for the Venture Co., the tauren brave for the Grimtotem, panthers for cougars,
the stag for elk, zombies and ghouls for the risen. The rules in creature_sprites.py swap to the st_ sprites
when they're filed.

Rares are in subzone tables only, at weight 0, and their loot is item level = level + 3, HAND-AUTHORED from the
crafted-gear identities (no rolled stats), spread across armour types, weapon types and every kind of spec
(strength leather, a mail healer, a caster's shield, a plate healer, a bear tank's chest).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_return_voyage_content import (  # noqa: E402
    CREATURES, KITS, ENCOUNTERS, kit_slug, merge_json, _detect_format,
    dmg, dot, debuff, buff, loot_audit,
)
from tools.build_tempest_openworld import enrage, stun, shield  # noqa: E402

LOOT = ROOT / "data/loot/stonetalon_rare_loot.json"
EAST = "Stonetalon East"

#: name -> (template, lo, hi, boss multiplier or None, sprite)
ROSTER = {
    # the open ground
    "Ridge Cougar":             ("beast_fast",        26, 28, None, "panther_2"),
    "Grey Elk":                 ("beast_fast",        26, 27, None, "stag"),
    "Black Bear":               ("beast_large",       26, 28, None, "bear_1"),
    "Ash Vulture":              ("beast_fast",        26, 27, None, "vulture_1"),
    # the Blowdown
    "Ash Drifter":              ("elemental_caster",  27, 28, None, "elemental_air_3"),
    # the Venture Salvage Yard
    "Venture Co. Salvager":     ("humanoid_warrior",  27, 28, None, "goblin_sapper_1"),
    "Venture Co. Bucker":       ("humanoid_warrior",  27, 28, None, "goblin_sapper_2"),
    "Venture Co. Blaster":      ("humanoid_ranged",   27, 28, None, "goblin_sapper_1"),
    "Venture Co. Yard Foreman": ("humanoid_caster",   28, 28, None, "goblin_overseer"),
    # Windshear Crag
    "Windshear Harpy":          ("humanoid_rogue",    27, 29, None, "harpy_1"),
    "Windshear Wind Witch":     ("humanoid_caster",   28, 29, None, "harpy_2"),
    "Windshear Talon":          ("humanoid_warrior",  28, 29, None, "harpy_3"),
    # the Standing Grove
    "Bull Elk":                 ("beast_large",       27, 28, None, "stag"),
    # the Grimtotem Compound
    "Grimtotem Raider":         ("humanoid_warrior",  28, 29, None, "tauren_brave"),
    "Grimtotem Mystic":         ("humanoid_caster",   28, 29, None, "tauren_brave"),
    "Grimtotem Spearhunter":    ("humanoid_ranged",   28, 29, None, "tauren_brave"),
    "Grimtotem Brute":          ("humanoid_warrior",  29, 29, None, "tauren_brave"),
    # the Mulgore Rim
    "Risen Tauren":             ("undead_warrior",    29, 29, None, "zombie_3"),
    "Risen Stalker":            ("undead_warrior",    29, 29, None, "ghoul_gaunt"),
    "Rim Carrion Bird":         ("beast_fast",        28, 29, None, "vulture_3"),
    # the rares, one per place
    "Old Greyhide":             ("beast_large",       28, 28, 2.0, "stag"),
    "Yard Boss Krizzle":        ("humanoid_warrior",  28, 28, 2.1, "goblin_overseer"),
    "Matron Shrieka":           ("humanoid_caster",   29, 29, 2.1, "harpy_matriarch"),
    "Broadpaw":                 ("beast_large",       28, 28, 2.1, "bear_3"),
    "Hargol Bloodhorn":         ("humanoid_warrior",  29, 29, 2.2, "tauren_brave"),
    "The Risen Hunter":         ("undead_warrior",    29, 29, 2.2, "zombie_5"),
}
RARES = {n for n, r in ROSTER.items() if r[3]}

KITSETS = {
    "Ridge Cougar": [dmg("Pounce", 64), dmg("Rake", 76, cooldown=3), dot("Torn Flank", 17, 3, 3)],
    "Grey Elk": [dmg("Antler Butt", 60), dmg("Charge", 74, cooldown=4),
                 debuff("Trampled", 5, 2, {"attack_power": -16})],
    "Black Bear": [dmg("Swipe", 66), dmg("Maul", 80, cooldown=4), buff("Thick Fur", 6, 4, {"armor": 50})],
    "Ash Vulture": [dmg("Peck", 58), dmg("Dive", 72, cooldown=3), dot("Festering Peck", 16, 3, 3)],
    "Ash Drifter": [dmg("Choking Ash", 62, school="fire"), dot("Hot Cinders", 18, 3, 3, school="fire"),
                    debuff("Ash in the Eyes", 5, 2, {"hit_rating": -8})],
    "Venture Co. Salvager": [dmg("Hatchet Chop", 64), dmg("Crowbar Smack", 76, cooldown=3),
                             debuff("Kneecapped", 5, 2, {"dodge_rating": -24})],
    "Venture Co. Bucker": [dmg("Crosscut Saw", 66), dmg("Big Swing", 80, cooldown=4, is_aoe=True),
                           dot("Ragged Cut", 17, 3, 3)],
    "Venture Co. Blaster": [dmg("Pistol Shot", 62), dmg("Tossed Charge", 72, cooldown=4, school="fire", is_aoe=True),
                            debuff("Ringing Ears", 5, 2, {"hit_rating": -8})],
    "Venture Co. Yard Foreman": [dmg("Shotgun", 66), dmg("Get Back to Work", 70, cooldown=4),
                                 buff("Overtime", 6, 3, {"attack_power": 24})],
    "Windshear Harpy": [dmg("Talon Rake", 62), dmg("Shriek and Dive", 76, cooldown=3), dot("Rending Talons", 17, 3, 3)],
    "Windshear Wind Witch": [dmg("Gust Bolt", 64, school="nature"), dmg("Squall", 70, cooldown=5, school="nature",
                                                                         is_aoe=True),
                             debuff("Buffeted", 5, 2, {"hit_rating": -8})],
    "Windshear Talon": [dmg("Hooked Claws", 66), dmg("Wing Buffet", 78, cooldown=4),
                        buff("Ruffled", 6, 3, {"dodge_rating": 30})],
    "Bull Elk": [dmg("Antler Gore", 66), dmg("Bellowing Charge", 82, cooldown=4),
                 buff("Rut", 6, 3, {"attack_power": 22})],
    "Grimtotem Raider": [dmg("Totem Axe", 68), dmg("Gore", 80, cooldown=4), debuff("War Stomp", 6, 1, {"dodge_rating": -24})],
    "Grimtotem Mystic": [dmg("Searing Bolt", 66, school="fire"), dot("Flame Shock", 18, 3, 3, school="fire"),
                         buff("Blood Ward", 6, 3, {"armor": 50})],
    "Grimtotem Spearhunter": [dmg("Thrown Spear", 64), dmg("Pinning Spear", 76, cooldown=4),
                              dot("Barbed Wound", 17, 3, 3)],
    "Grimtotem Brute": [dmg("Stone Maul", 72), dmg("Earth-Shaking Blow", 82, cooldown=4, is_aoe=True),
                        buff("Hardline", 6, 4, {"armor": 60})],
    "Risen Tauren": [dmg("Dead Hands", 70), dmg("Horn Toss", 80, cooldown=4),
                     dot("Grave Rot", 18, 3, 3, school="shadow", dispel_type="disease")],
    "Risen Stalker": [dmg("Dragging Chain", 68), dmg("Lunge From the Dark", 84, cooldown=3),
                      debuff("Dread", 5, 2, {"attack_power": -18, "spell_power": -18})],
    "Rim Carrion Bird": [dmg("Tearing Beak", 62), dmg("Dive", 74, cooldown=3), dot("Festering Peck", 17, 3, 3)],
    # ---- the rares, in final form
    "Old Greyhide": [dmg("Ash-Caked Antlers", 128), dmg("Stampede", 104, cooldown=4, is_aoe=True),
                     stun("Bowled Over", 96), enrage("Old Bull's Fury", 50)],
    "Yard Boss Krizzle": [dmg("Two-Handed Saw", 132), dmg("Everybody Duck", 108, cooldown=4, school="fire", is_aoe=True),
                          stun("Clipboard to the Face", 96), shield("Hard Hat", 420)],
    "Matron Shrieka": [dmg("Cutting Gale", 130, school="nature"), dmg("Windshear", 106, cooldown=4, school="nature",
                                                                      is_aoe=True),
                       dot("Talon Wounds", 34, 3, 4), shield("Wall of Wind", 430, school="nature")],
    "Broadpaw": [dmg("Crushing Swipe", 134), dmg("Roar", 104, cooldown=4, is_aoe=True),
                 stun("Pinned Down", 98), enrage("Mother Bear", 52)],
    "Hargol Bloodhorn": [dmg("Bloodhorn Axe", 138), dmg("War Stomp", 110, cooldown=4, is_aoe=True),
                         stun("Gored", 100), enrage("Grimtotem Blood", 54)],
    "The Risen Hunter": [dmg("Dead Man's Spear", 136), dmg("The Hunt Goes On", 108, cooldown=4),
                         dot("Mulgore's Dark", 36, 3, 4, school="shadow"), shield("Doesn't Stay Down", 440,
                                                                                    school="shadow")],
}

TABLES = {
    EAST: {
        "open_zone": {"name": EAST,
                      "creatures": {"Ridge Cougar": 4, "Grey Elk": 4, "Black Bear": 3, "Ash Vulture": 3}},
        "subzones": {
            "The Blowdown": {"name": "The Blowdown",
                             "creatures": {"Ash Drifter": 6, "Grey Elk": 4, "Ash Vulture": 4, "Ridge Cougar": 2,
                                           "Old Greyhide": 0}},
            "Venture Salvage Yard": {"name": "Venture Salvage Yard",
                                     "creatures": {"Venture Co. Salvager": 5, "Venture Co. Bucker": 5,
                                                   "Venture Co. Blaster": 4, "Venture Co. Yard Foreman": 2,
                                                   "Yard Boss Krizzle": 0}},
            "Windshear Crag": {"name": "Windshear Crag",
                               "creatures": {"Windshear Harpy": 6, "Windshear Wind Witch": 4, "Windshear Talon": 4,
                                             "Matron Shrieka": 0}},
            "The Standing Grove": {"name": "The Standing Grove",
                                   "creatures": {"Black Bear": 5, "Ridge Cougar": 4, "Bull Elk": 5, "Broadpaw": 0}},
            "Grimtotem Compound": {"name": "Grimtotem Compound",
                                   "creatures": {"Grimtotem Raider": 5, "Grimtotem Mystic": 4,
                                                 "Grimtotem Spearhunter": 4, "Grimtotem Brute": 3,
                                                 "Hargol Bloodhorn": 0}},
            "The Mulgore Rim": {"name": "The Mulgore Rim",
                                "creatures": {"Risen Tauren": 5, "Risen Stalker": 4, "Rim Carrion Bird": 4,
                                              "The Risen Hunter": 0}},
        },
    },
}

#: (item level, [(name, slot, kind, armour or weapon type, identity)]). Item level = the rare's level + 3.
#: HAND-AUTHORED, not rolled: each piece is a crafted-gear identity (tools/build_crafted_gear.py IDENTITIES), so its
#: stats are fixed and logical with no drip stats, and a shield can be a caster's (the random generator can't do
#: that: its shields only roll Stamina). Spread across every kind of spec, not the classic nine (Kyle, 15 Nov
#: 2026): strength leather for the Barbarian, a mail healer for the Tinker and the Vizier, a caster's shield, a
#: plate healer, a bear tank's chest, a strength/intellect hybrid's legs, a totem, a fist weapon and a polearm.
POOLS = {
    "Old Greyhide": (31, [
        ("Greyhide Mantle", "shoulder", "armor", "leather", "agility"),
        ("Ash-Walker's Boots", "feet", "armor", "mail", "tide_healer"),
        ("Antler-Bone Wand", "ranged", "weapon", "wand", "caster_crit"),
        ("Greyhide Girdle", "waist", "armor", "plate", "tank"),
    ]),
    "Yard Boss Krizzle": (31, [
        ("Salvage Boss Gauntlets", "hands", "armor", "leather", "strength_crit"),
        ("Rigging-Chain Leggings", "legs", "armor", "mail", "agility"),
        ("Krizzle's Ledger", "off_hand", "weapon", "tome", "healer"),
        ("The Bucking Saw", "main_hand", "weapon", "axe_2h", "strength"),
    ]),
    "Matron Shrieka": (32, [
        ("Windshear Feathered Cowl", "head", "armor", "cloth", "caster"),
        ("Talon-Hook Bracers", "wrist", "armor", "mail", "hunter"),
        ("Shrieka's Gale Shield", "off_hand", "weapon", "shield", "haste_caster"),
        ("Featherfall Slippers", "feet", "armor", "cloth", "healer"),
    ]),
    "Broadpaw": (31, [
        ("Broadpaw Hide Vest", "chest", "armor", "leather", "bear"),
        ("Grove-Runner's Coif", "head", "armor", "mail", "agility"),
        ("Broadpaw's Claw", "main_hand", "weapon", "fist_weapon", "rogue_crit"),
        ("Mossbark Robe", "chest", "armor", "cloth", "spirit_healer"),
    ]),
    "Hargol Bloodhorn": (32, [
        ("Bloodhorn Breastplate", "chest", "armor", "plate", "strength_crit"),
        ("Grimtotem Spirit Mantle", "shoulder", "armor", "mail", "mail_caster"),
        ("Bloodhorn Totem", "ranged", "weapon", "totem", "mail_caster"),
        ("Hargol's War Spear", "main_hand", "weapon", "polearm", "strength"),
    ]),
    "The Risen Hunter": (32, [
        ("Rim-Walker's Legplates", "legs", "armor", "plate", "crusader"),
        ("Dead Hunter's Longbow", "ranged", "weapon", "bow", "hunter_crit"),
        ("Hollow-Eye Gloves", "hands", "armor", "leather", "healer"),
        ("Sunless Pauldrons", "shoulder", "armor", "plate", "plate_healer"),
    ]),
}

#: ---- WINDSHEAR MINE (27-30): the Venture Co.'s dig under the crag, broken through into a chimney to the sky.
#: Trash is random from the cave's table; two bosses pinned by the map (tools/handbuilt_windshear_mine.py).
MINE = "Windshear Mine"
CAVE_ROSTER = {
    "Venture Co. Shaft Miner":  ("humanoid_warrior",  27, 29, None, "goblin_sapper_2"),
    "Venture Co. Powder Monkey": ("humanoid_ranged",  27, 29, None, "goblin_sapper_1"),
    "Venture Co. Shift Boss":   ("humanoid_caster",   28, 29, None, "goblin_overseer"),
    "Pumice Shard":             ("elemental_bruiser", 28, 29, None, "elemental_earth_1"),
    "Chimney Harpy":            ("humanoid_rogue",    28, 29, None, "harpy_3"),
    # the bosses
    "Driller Mozzik":           ("humanoid_warrior",  30, 30, 2.4, "goblin_overseer"),
    "Old Pumice":               ("elemental_bruiser", 30, 30, 2.3, "elemental_earth_2"),
}
CAVE_KITS = {
    "Venture Co. Shaft Miner": [dmg("Pickaxe", 66), dmg("Overhead Swing", 80, cooldown=4),
                                debuff("Rock Dust", 5, 2, {"hit_rating": -8})],
    "Venture Co. Powder Monkey": [dmg("Lit Fuse", 64, school="fire"),
                                  dmg("Bundle of Charges", 74, cooldown=4, school="fire", is_aoe=True),
                                  debuff("Ringing Ears", 5, 2, {"hit_rating": -8})],
    "Venture Co. Shift Boss": [dmg("Shotgun", 68), dmg("Double Shift", 72, cooldown=4),
                               buff("Hurry Up", 6, 3, {"attack_power": 24})],
    "Pumice Shard": [dmg("Grinding Slam", 70), dmg("Shard Burst", 76, cooldown=4, is_aoe=True),
                     buff("Porous Skin", 6, 4, {"armor": 60})],
    "Chimney Harpy": [dmg("Diving Talons", 66), dmg("Down the Chimney", 80, cooldown=3), dot("Torn Skin", 17, 3, 3)],
    "Driller Mozzik": [dmg("Drill Arm", 156), dmg("Grinding Spin", 120, cooldown=4, is_aoe=True),
                       stun("Steam Blast", 108, school="fire"), shield("Rig Plating", 520),
                       enrage("Full Throttle", 60)],
    "Old Pumice": [dmg("Pumice Fist", 152), dmg("Rockfall", 118, cooldown=4, is_aoe=True),
                   stun("Buried", 104), shield("Porous Shell", 500), enrage("Cracked Open", 58)],
}
CAVE_TABLES = {
    MINE: {"name": MINE,
           "creatures": {"Venture Co. Shaft Miner": 4, "Venture Co. Powder Monkey": 3, "Venture Co. Shift Boss": 2,
                         "Pumice Shard": 3, "Chimney Harpy": 2, "Driller Mozzik": 0, "Old Pumice": 0}},
}
CAVE_BOSSES = {n for n, r in CAVE_ROSTER.items() if r[3]}
#: boss pools: item level = the boss's level + 2 (the boss-pool offset), hand-authored like the rares
BOSS_POOLS = {
    "Driller Mozzik": (32, [
        ("Drillbit Mace", "main_hand", "weapon", "mace_1h", "strength_crit"),
        ("Overcharged Blasting Rifle", "ranged", "weapon", "gun", "hunter_precise"),
        ("Powder-Burned Gloves", "hands", "armor", "cloth", "caster_crit"),
        ("Rig-Hand's Belt", "waist", "armor", "plate", "tank"),
    ]),
    "Old Pumice": (32, [
        ("Pumice-Stone Charm", "trinket", "armor", None, "tank_any"),
        ("Ash-Glass Ring", "ring", "armor", None, "precise_caster"),
        ("Pumice-Grit Leggings", "legs", "armor", "leather", "agility"),
        ("Old Pumice's Core", "off_hand", "weapon", "tome", "spirit_healer"),
    ]),
}
BOSS_LOOT = ROOT / "data/loot/stonetalon_boss_loot.json"


#: Gathering, the same 25-30 band as the Aspen: wood heavy (it's a logging country), with the Aspen's herbs and
#: ore. Fishing in Ashfall Creek and the pond under Sun Rock.
NODES = {
    "stonetalon_east": {
        "slots": 24, "active_percent": 0.42,
        "table": {"wood_redbark_tree": 4, "wood_frostpine": 3, "wood_duskwood_stump": 3, "wood_silverbark_tree": 2,
                  "herb_briarthorn": 3, "herb_bruiseweed": 3, "herb_liferoot": 2, "herb_kingsblood": 2,
                  "herb_wild_steelbloom": 2, "ore_iron": 2, "ore_tin": 2, "ore_coal": 1, "ore_living_copper": 1},
    },
}


def main():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import tools.handbuilt_stonetalon_east as SE

    declared = {s[0] for s in SE.SUBZONES}
    if set(TABLES[EAST]["subzones"]) != declared:
        print(f"FAILED: {EAST} subzones disagree with the map: {sorted(set(TABLES[EAST]['subzones']) ^ declared)}")
        return 1
    existing = json.loads(CREATURES.read_text(encoding="utf-8"))["creatures"]
    named = set()
    for t in TABLES.values():
        named |= set(t["open_zone"]["creatures"])
        if RARES & set(t["open_zone"]["creatures"]):
            print("FAILED: a rare is in an open-zone table")
            return 1
        for s in t["subzones"].values():
            named |= set(s["creatures"])
    if named != set(ROSTER) or set(KITSETS) != set(ROSTER) or set(POOLS) != RARES:
        print(f"FAILED: tables, roster, kits and pools differ: {sorted(named ^ set(ROSTER))} "
              f"{sorted(set(KITSETS) ^ set(ROSTER))} {sorted(set(POOLS) ^ RARES)}")
        return 1
    for name, (_t, lo, hi, mult, sprite) in ROSTER.items():
        if mult and POOLS[name][0] != hi + 3:
            print(f"FAILED: {name} is level {hi} and its loot is item level {POOLS[name][0]}")
            return 1
        if not (ROOT / "assets/creatures" / f"{sprite}.png").exists():
            print(f"FAILED: {name}'s sprite {sprite} is not on disk")
            return 1
        prev = existing.get(name)
        if prev and prev.get("ability_kit") != kit_slug(name):
            print(f"FAILED: {name} is already a different creature in creatures.json")
            return 1

    import tools.handbuilt_windshear_mine as WM
    WM.build_windshear_mine()          # fills WM.BOSSES from the map
    if set(WM.BOSSES) != CAVE_BOSSES or set(CAVE_KITS) != set(CAVE_ROSTER) or set(BOSS_POOLS) != CAVE_BOSSES \
            or set(CAVE_TABLES[MINE]["creatures"]) != set(CAVE_ROSTER):
        print("FAILED: Windshear Mine's map, roster, kits, table and pools disagree")
        return 1
    for name, (_t, lo, hi, mult, sprite) in CAVE_ROSTER.items():
        if name in ROSTER or name in existing and existing[name].get("ability_kit") != kit_slug(name):
            print(f"FAILED: {name} is already another creature")
            return 1
        if not (ROOT / "assets/creatures" / f"{sprite}.png").exists():
            print(f"FAILED: {name}'s sprite {sprite} is not on disk")
            return 1
        if mult and BOSS_POOLS[name][0] != hi + 2:
            print(f"FAILED: {name} is level {hi} and its loot is item level {BOSS_POOLS[name][0]}")
            return 1
    creatures = {}
    for name, (template, lo, hi, mult, _sprite) in {**ROSTER, **CAVE_ROSTER}.items():
        e = {"template": template, "level_range": [lo, hi], "is_boss": bool(mult), "ability_kit": kit_slug(name)}
        if mult:
            e["boss_multiplier"] = mult
        creatures[name] = e
    merge_json(CREATURES, "creatures", creatures, "creatures.json")
    merge_json(KITS, "kits", {kit_slug(n): k for n, k in {**KITSETS, **CAVE_KITS}.items()}, "ability_kits.json")

    raw = ENCOUNTERS.read_text(encoding="utf-8")
    enc = json.loads(raw)
    indent, newline = _detect_format(enc, raw)
    for zone, table in TABLES.items():
        entry = enc.setdefault("zones", {}).setdefault(zone, {})
        entry["open_zone"] = table["open_zone"]
        entry["subzones"] = table["subzones"]
    enc["zones"][EAST].setdefault("caves", {}).update(CAVE_TABLES)
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False) + ("\n" if newline else ""),
                          encoding="utf-8")
    for zone, table in TABLES.items():
        print(f"  encounters.json: {zone}, open zone + {len(table['subzones'])} subzones")

    np_path = ROOT / "data/gathering/node_pools.json"
    nd = json.loads(np_path.read_text(encoding="utf-8"))
    for key, pool in NODES.items():
        fish = (nd["zones"].get("aspen_wilderness") or {}).get("fishing")
        nd["zones"][key] = dict(pool, **({"fishing": fish} if fish else {}))
    np_path.write_text(json.dumps(nd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  node_pools.json: {', '.join(NODES)}")

    sys.path.insert(0, str(ROOT / "tools"))
    import build_crafted_gear as C
    out = {"_notes": ("Stonetalon's open-world rares. Hand-authored in tools/build_stonetalon_openworld.py: each "
                      "piece is a crafted-gear identity at rare budget, fixed stats, no rolls.")}
    bout = {"_notes": ("Stonetalon's cave and dungeon bosses. Hand-authored in tools/build_stonetalon_openworld.py "
                       "from the crafted-gear identities at rare budget.")}
    rows, bad = [], []
    for boss, (ilvl, items) in list(POOLS.items()) + list(BOSS_POOLS.items()):
        built = []
        for (name, slot, kind, typ, ident) in items:
            o = {"kind": kind, "slot": slot, "item_level": ilvl, "rarity": "rare",
                 "stat_template": C.IDENTITIES[ident][1]}
            if kind == "weapon":
                o["weapon_type"] = typ
                ident = C.weapon_identity(typ, ident)
            else:
                o["armor_type"] = typ
            rid = "st_" + name.lower().replace("'", "").replace(" ", "_").replace("-", "_").replace(".", "")
            d = C.author(rid, {"name": name, "output": o}, ident, "")
            bad += C.audit_item("loot", rid, d)
            d["item_id"] = rid
            d.pop("flavor_text", None)
            built.append(d)
            rows.append((name, slot, kind, typ, C.IDENTITIES[ident][1]))
        (bout if boss in BOSS_POOLS else out)[boss] = built
    if bad:
        print("FAILED - the authored pieces don't pass the crafted-gear audit:")
        for b_ in bad:
            print(f"  - {b_}")
        return 1
    problems = loot_audit(rows)
    if problems:
        print("\nFAILED - fix the pools, not the check:")
        for pr in problems:
            print(f"  - {pr}")
        return 1
    LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    BOSS_LOOT.write_text(json.dumps(bout, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  {LOOT.relative_to(ROOT)} and {BOSS_LOOT.relative_to(ROOT)}: {len(POOLS) + len(BOSS_POOLS)} pools, "
          f"{len(rows)} items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
