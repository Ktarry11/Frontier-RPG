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
    "Ridge Cougar":             ("beast_fast",        26, 28, None, "st_cougar"),
    "Grey Elk":                 ("beast_fast",        26, 27, None, "st_bull_elk"),
    "Black Bear":               ("beast_large",       26, 28, None, "st_black_bear"),
    "Ash Vulture":              ("beast_fast",        26, 27, None, "vulture_1"),
    # the Blowdown
    "Ash Drifter":              ("elemental_caster",  27, 28, None, "st_ash_elemental"),
    # the Venture Salvage Yard
    "Venture Co. Salvager":     ("humanoid_warrior",  27, 28, None, "st_venture_logger"),
    "Venture Co. Bucker":       ("humanoid_warrior",  27, 28, None, "st_venture_sawyer"),
    "Venture Co. Blaster":      ("humanoid_ranged",   27, 28, None, "st_venture_demolitionist"),
    "Venture Co. Yard Foreman": ("humanoid_caster",   28, 28, None, "st_venture_foreman"),
    # Windshear Crag
    "Windshear Harpy":          ("humanoid_rogue",    27, 29, None, "st_windshear_harpy"),
    "Windshear Wind Witch":     ("humanoid_caster",   28, 29, None, "st_windshear_witch"),
    "Windshear Talon":          ("humanoid_warrior",  28, 29, None, "harpy_3"),
    # the Standing Grove
    "Bull Elk":                 ("beast_large",       27, 28, None, "st_bull_elk"),
    # the Grimtotem Compound
    "Grimtotem Raider":         ("humanoid_warrior",  28, 29, None, "st_grim_warrior"),
    "Grimtotem Mystic":         ("humanoid_caster",   28, 29, None, "st_grim_mystic"),
    "Grimtotem Spearhunter":    ("humanoid_ranged",   28, 29, None, "st_grim_hunter"),
    "Grimtotem Brute":          ("humanoid_warrior",  29, 29, None, "st_grim_brute"),
    "Grimtotem Firecaller":     ("humanoid_caster",   28, 29, None, "st_grim_shaman"),
    # the Mulgore Rim
    "Risen Tauren":             ("undead_warrior",    29, 29, None, "st_risen_tauren"),
    "Risen Stalker":            ("undead_warrior",    29, 29, None, "st_risen_stalker"),
    "Rim Carrion Bird":         ("beast_fast",        28, 29, None, "vulture_3"),
    # the rares, one per place
    "Old Greyhide":             ("beast_large",       28, 28, 2.0, "st_bull_elk"),
    "Yard Boss Krizzle":        ("humanoid_warrior",  28, 28, 2.1, "st_venture_foreman"),
    "Matron Shrieka":           ("humanoid_caster",   29, 29, 2.1, "harpy_matriarch"),
    "Broadpaw":                 ("beast_large",       28, 28, 2.1, "st_black_bear"),
    "Hargol Bloodhorn":         ("humanoid_warrior",  29, 29, 2.2, "st_grim_elder"),
    "The Risen Hunter":         ("undead_warrior",    29, 29, 2.2, "st_risen_tauren"),
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
    "Grimtotem Firecaller": [dmg("Fire Totem's Lash", 66, school="fire"), dmg("Searing Burst", 72, cooldown=5,
                                                                              school="fire", is_aoe=True),
                             buff("Blood Fury", 6, 3, {"spell_power": 24})],
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
                                                 "Grimtotem Firecaller": 3,
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

#: ---- STONETALON WEST (29-32): the giants the blast didn't reach
WEST = "Stonetalon West"
WEST_ROSTER = {
    # the open forest
    "Roosevelt Elk":            ("beast_large",       29, 31, None, "st_bull_elk"),
    "Fog Cougar":               ("beast_fast",        29, 31, None, "st_cougar"),
    "Greatwood Bear":           ("beast_large",       30, 31, None, "st_black_bear"),
    "Ridge Eagle":              ("beast_fast",        29, 31, None, "st_bald_eagle"),
    # Greatwood Vale
    "Bark Beetle":              ("vermin_swarm",      29, 30, None, "st_bark_beetle"),
    "Mistwood Owl":             ("beast_fast",        30, 31, None, "st_canopy_owl"),
    "Redwood Ancient":          ("elemental_bruiser", 31, 32, None, "st_redwood_ancient"),
    # the Sequoia Slopes
    "Sap Ooze":                 ("elemental_bruiser", 30, 31, None, "st_sap_ooze"),
    # Stonetalon Peak
    "Vent Steamling":           ("elemental_caster",  31, 32, None, "st_steam_elemental"),
    "Basalt Hulk":              ("elemental_bruiser", 31, 32, None, "st_basalt_elemental"),
    "Crater Ash Wraith":        ("elemental_caster",  31, 32, None, "st_ash_elemental"),
    "Peak Sky Serpent":         ("beast_fast",        31, 32, None, "st_sky_serpent"),
    # the Venture Cutline
    "Venture Co. Rigger":       ("humanoid_rogue",    30, 31, None, "st_venture_rigger"),
    "Venture Co. Feller":       ("humanoid_warrior",  30, 31, None, "st_venture_sawyer"),
    "Venture Co. Cut Foreman":  ("humanoid_caster",   31, 31, None, "st_venture_foreman"),
    "Venture Co. Shredder":     ("humanoid_warrior",  31, 32, None, "st_venture_shredder"),
    # the rares
    "Gnawheart":                ("beast_large",       31, 31, 2.1, "st_beetle_mother"),
    "Grandfather Burl":         ("elemental_bruiser", 32, 32, 2.2, "st_redwood_ancient"),
    "Skyreach":                 ("beast_fast",        32, 32, 2.2, "st_sky_serpent"),
    "Saw-Boss Brakka":          ("humanoid_warrior",  32, 32, 2.3, "st_venture_shredder"),
}
WEST_KITS = {
    "Roosevelt Elk": [dmg("Antler Gore", 76), dmg("Bellowing Charge", 92, cooldown=4), buff("Rut", 6, 3, {"attack_power": 26})],
    "Fog Cougar": [dmg("Pounce From the Fog", 74), dmg("Rake", 88, cooldown=3), dot("Torn Flank", 20, 3, 3)],
    "Greatwood Bear": [dmg("Swipe", 78), dmg("Maul", 94, cooldown=4), buff("Thick Fur", 6, 4, {"armor": 60})],
    "Ridge Eagle": [dmg("Talon Strike", 72), dmg("Stoop", 90, cooldown=3), debuff("Buffeting Wings", 5, 2, {"hit_rating": -9})],
    "Bark Beetle": [dmg("Mandibles", 70), dot("Bored Through", 20, 3, 3),
                    debuff("Swarming", 5, 2, {"dodge_rating": -26})],
    "Mistwood Owl": [dmg("Silent Talons", 74), dmg("Dive From Above", 90, cooldown=3),
                     debuff("Screech", 5, 2, {"spell_power": -24})],
    "Redwood Ancient": [dmg("Root Slam", 82), dmg("Thrashing Limbs", 92, cooldown=4, is_aoe=True),
                        buff("Bark Skin", 6, 4, {"armor": 70})],
    "Sap Ooze": [dmg("Engulf", 74, school="nature"), dot("Sticky Sap", 20, 3, 3, school="nature"),
                 debuff("Stuck Fast", 5, 2, {"dodge_rating": -28})],
    "Vent Steamling": [dmg("Scalding Jet", 78, school="fire"), dot("Scald", 22, 3, 3, school="fire"),
                       debuff("Steam Cloud", 5, 2, {"hit_rating": -9})],
    "Basalt Hulk": [dmg("Basalt Fist", 84), dmg("Magma Crack", 94, cooldown=4, school="fire", is_aoe=True),
                    buff("Cooling Crust", 6, 4, {"armor": 80})],
    "Crater Ash Wraith": [dmg("Choking Ash", 76, school="fire"), dot("Hot Cinders", 22, 3, 3, school="fire"),
                          debuff("Ash in the Eyes", 5, 2, {"hit_rating": -9})],
    "Peak Sky Serpent": [dmg("Feathered Bite", 78), dmg("Coil and Strike", 92, cooldown=3, school="nature"),
                         dot("Venom", 22, 3, 3, school="nature", dispel_type="poison")],
    "Venture Co. Rigger": [dmg("Climbing Spike", 74), dmg("Drop From the Ropes", 90, cooldown=3),
                           dot("Spiked Boots", 20, 3, 3)],
    "Venture Co. Feller": [dmg("Crosscut Saw", 78), dmg("Big Swing", 94, cooldown=4, is_aoe=True), dot("Ragged Cut", 20, 3, 3)],
    "Venture Co. Cut Foreman": [dmg("Shotgun", 78), dmg("Cut Faster", 84, cooldown=4),
                                buff("Overtime", 6, 3, {"attack_power": 28})],
    "Venture Co. Shredder": [dmg("Saw Arm", 84), dmg("Shred", 96, cooldown=4, is_aoe=True),
                             buff("Plating", 6, 4, {"armor": 90})],
    "Gnawheart": [dmg("Crushing Mandibles", 150), dmg("Swarm Call", 118, cooldown=4, is_aoe=True),
                  dot("Bored to the Core", 40, 3, 4), shield("Chitin Shell", 520)],
    "Grandfather Burl": [dmg("Burl Slam", 158), dmg("The Forest's Anger", 124, cooldown=4, is_aoe=True),
                         stun("Rooted", 112, school="nature"), shield("Thousand-Year Bark", 540, school="nature")],
    "Skyreach": [dmg("Plunging Bite", 156), dmg("Storm Coil", 122, cooldown=4, school="nature", is_aoe=True),
                 dot("Skyreach Venom", 42, 3, 4, school="nature"), enrage("Rising Storm", 62)],
    "Saw-Boss Brakka": [dmg("Twin Saws", 162), dmg("Clear-Cut", 126, cooldown=4, is_aoe=True),
                        stun("Sawdust Blast", 114), shield("Reinforced Cockpit", 560)],
}
WEST_TABLES = {
    WEST: {
        "open_zone": {"name": WEST,
                      "creatures": {"Roosevelt Elk": 4, "Fog Cougar": 4, "Greatwood Bear": 3, "Ridge Eagle": 3}},
        "subzones": {
            "Greatwood Vale": {"name": "Greatwood Vale",
                               "creatures": {"Bark Beetle": 5, "Mistwood Owl": 4, "Redwood Ancient": 3,
                                             "Fog Cougar": 3, "Gnawheart": 0}},
            "The Sequoia Slopes": {"name": "The Sequoia Slopes",
                                   "creatures": {"Sap Ooze": 5, "Redwood Ancient": 3, "Ridge Eagle": 3,
                                                 "Bark Beetle": 3, "Grandfather Burl": 0}},
            "Stonetalon Peak": {"name": "Stonetalon Peak",
                                "creatures": {"Vent Steamling": 5, "Basalt Hulk": 4, "Crater Ash Wraith": 4,
                                              "Peak Sky Serpent": 3, "Skyreach": 0}},
            "The Venture Cutline": {"name": "The Venture Cutline",
                                    "creatures": {"Venture Co. Rigger": 5, "Venture Co. Feller": 5,
                                                  "Venture Co. Cut Foreman": 2, "Venture Co. Shredder": 3,
                                                  "Saw-Boss Brakka": 0}},
            "Mistwalker Camp": {"name": "Mistwalker Camp", "safe": True, "creatures": {}},
        },
    },
}
#: item level = level + 3; hand-authored, and spread so West adds what East's rares are thin on
WEST_POOLS = {
    "Gnawheart": (34, [
        ("Chitin-Plated Vest", "chest", "armor", "mail", "bear"),
        ("Gnawheart's Mandible", "main_hand", "weapon", "dagger", "rogue_crit"),
        ("Beetle-Wing Cloak", "back", "armor", None, "physical"),
        ("Bored-Heartwood Wand", "ranged", "weapon", "wand", "precise_caster"),
    ]),
    "Grandfather Burl": (35, [
        ("Burlwood Staff", "main_hand", "weapon", "staff", "high_healer"),
        ("Grandfather's Mossy Mantle", "shoulder", "armor", "leather", "high_healer"),
        ("Rootbound Greaves", "feet", "armor", "plate", "crusader"),
        ("Living Bark Idol", "ranged", "weapon", "idol", "bear"),
    ]),
    "Skyreach": (35, [
        ("Feathered Serpent Hood", "head", "armor", "leather", "wildheart"),
        ("Skyreach Scale Legguards", "legs", "armor", "mail", "mail_caster"),
        ("Stormfang Crossbow", "ranged", "weapon", "crossbow", "hunter_crit"),
        ("Coil of the Peak", "neck", "armor", None, "caster_crit"),
    ]),
    "Saw-Boss Brakka": (35, [
        ("Brakka's Twin-Saw", "main_hand", "weapon", "sword_2h", "strength_crit"),
        ("Cockpit Plate Gauntlets", "hands", "armor", "plate", "tank"),
        ("Clear-Cut Shield", "off_hand", "weapon", "shield", "shield_tank"),
        ("Sawdust-Caked Bracers", "wrist", "armor", "cloth", "healer"),
    ]),
}
WEST_RARES = {n for n, r in WEST_ROSTER.items() if r[3]}


#: ---- WINDSHEAR MINE (27-30): the Venture Co.'s dig under the crag, broken through into a chimney to the sky.
#: Trash is random from the cave's table; two bosses pinned by the map (tools/handbuilt_windshear_mine.py).
MINE = "Windshear Mine"
CAVE_ROSTER = {
    "Venture Co. Shaft Miner":  ("humanoid_warrior",  27, 29, None, "st_venture_logger"),
    "Venture Co. Powder Monkey": ("humanoid_ranged",  27, 29, None, "st_venture_demolitionist"),
    "Venture Co. Shift Boss":   ("humanoid_caster",   28, 29, None, "st_venture_foreman"),
    "Pumice Shard":             ("elemental_bruiser", 28, 29, None, "st_pumice_golem"),
    "Chimney Harpy":            ("humanoid_rogue",    28, 29, None, "st_windshear_harpy"),
    # the bosses
    "Driller Mozzik":           ("humanoid_warrior",  30, 30, 2.4, "st_venture_shredder"),
    "Old Pumice":               ("elemental_bruiser", 30, 30, 2.3, "st_basalt_elemental"),
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


#: ---- THE ASHVENT (30-32): a lava tube in Stonetalon Peak's flank. Two bosses pinned by the map
#: (tools/handbuilt_ashvent.py); trash random from the cave's table.
ASHVENT = "The Ashvent"
ASHVENT_ROSTER = {
    "Ashvent Steamling":        ("elemental_caster",  30, 32, None, "st_steam_elemental"),
    "Ashvent Basalt Brute":     ("elemental_bruiser", 31, 32, None, "st_basalt_elemental"),
    "Ashvent Cinderwraith":     ("elemental_caster",  30, 32, None, "st_ash_elemental"),
    "Cinder Beetle":            ("vermin_swarm",      30, 31, None, "st_bark_beetle"),
    "Magmacore":                ("elemental_bruiser", 32, 32, 2.5, "st_basalt_elemental"),
    "The Ash Mother":           ("elemental_caster",  32, 32, 2.3, "st_ash_elemental"),
}
ASHVENT_KITS = {
    "Ashvent Steamling": [dmg("Scalding Jet", 76, school="fire"), dot("Scald", 22, 3, 3, school="fire"),
                          debuff("Steam Cloud", 5, 2, {"hit_rating": -9})],
    "Ashvent Basalt Brute": [dmg("Basalt Fist", 84), dmg("Crack the Crust", 94, cooldown=4, school="fire", is_aoe=True),
                             buff("Cooling Crust", 6, 4, {"armor": 80})],
    "Ashvent Cinderwraith": [dmg("Cinder Lash", 78, school="fire"), dot("Smoulder", 22, 3, 4, school="fire"),
                             debuff("Choking Smoke", 5, 2, {"spell_power": -26, "attack_power": -26})],
    "Cinder Beetle": [dmg("Hot Mandibles", 72, school="fire"), dot("Burrowing Burn", 20, 3, 3, school="fire"),
                      debuff("Swarming", 5, 2, {"dodge_rating": -26})],
    "Magmacore": [dmg("Molten Fist", 168, school="fire"), dmg("Eruption", 130, cooldown=4, school="fire", is_aoe=True),
                  stun("Crushed Under Stone", 118), shield("Crust Shell", 600, school="fire"),
                  enrage("Breaking Open", 66)],
    "The Ash Mother": [dmg("Ashfall", 160, school="fire"), dmg("Smothering Cloud", 126, cooldown=4, school="fire",
                                                              is_aoe=True),
                       dot("Ash in the Lungs", 44, 3, 4, school="fire"), shield("Veil of Ash", 560, school="fire")],
}
ASHVENT_TABLE = {ASHVENT: {"name": ASHVENT,
                           "creatures": {"Ashvent Steamling": 4, "Ashvent Basalt Brute": 3, "Ashvent Cinderwraith": 3,
                                         "Cinder Beetle": 3, "Magmacore": 0, "The Ash Mother": 0}}}
ASHVENT_BOSSES = {n for n, r in ASHVENT_ROSTER.items() if r[3]}
ASHVENT_POOLS = {
    "Magmacore": (34, [
        ("Magmacore Heart", "trinket", "armor", None, "caster_crit"),
        ("Obsidian-Edge Axe", "main_hand", "weapon", "axe_1h", "agility"),
        ("Crust-Forged Breastplate", "chest", "armor", "plate", "plate_healer"),
        ("Lava-Tube Treads", "feet", "armor", "mail", "hunter"),
    ]),
    "The Ash Mother": (34, [
        ("Ash Mother's Shroud", "chest", "armor", "cloth", "haste_caster"),
        ("Cinder-Woven Belt", "waist", "armor", "leather", "strength"),
        ("Totem of the Smouldering Vent", "ranged", "weapon", "totem", "tide_healer"),
        ("Basalt Throwing Axes", "ranged", "weapon", "thrown", "agility"),
    ]),
}


#: ---- THE ELDEST SEQUOIA (30-33): the dungeon, two maps (tools/handbuilt_eldest_sequoia.py). Packs of 3-5 hand-
#: placed by the map; six bosses, each asking one thing of the party:
#:   Rigboss Gazzle       keeps calling riggers down the ropes: kill them or be buried in them
#:   the Heartrot Queen   her borers keep coming and her bite lowers your armour: burst her
#:   Ambermaw (optional)  sticky sap slows dodging, and a goblin's still inside: a long fight, heal through it
#:   Old Talonwing        storm dives hit everyone: spread the healing
#:   Topper Kezzik        a plated walker that shields itself: armour pen and burst between shields
#:   The Eldest           the tree's own spirit, everything at once, and it roots you
TRUNK, CROWN = "The Eldest Sequoia", "The Eldest's Crown"
DUNGEON_ROSTER = {
    "Venture Co. Trunk Rigger": ("humanoid_rogue",    30, 31, None, "st_venture_rigger"),
    "Venture Co. Hauler":       ("humanoid_warrior",  30, 31, None, "st_venture_logger"),
    "Venture Co. Sap Tapper":   ("humanoid_caster",   31, 32, None, "st_venture_foreman"),
    "Heartrot Borer":           ("vermin_swarm",      31, 32, None, "st_bark_beetle"),
    "Heartrot Drone":           ("beast_fast",        31, 32, None, "st_beetle_mother"),
    "Living Sap":               ("elemental_bruiser", 31, 32, None, "st_sap_ooze"),
    "Crown Owl":                ("beast_fast",        32, 33, None, "st_canopy_owl"),
    "Crown Sky Serpent":        ("beast_fast",        32, 33, None, "st_sky_serpent"),
    "Venture Co. Topper":       ("humanoid_warrior",  32, 33, None, "st_venture_rigger"),
    "Venture Co. Crown Shredder": ("humanoid_warrior", 33, 33, None, "st_venture_shredder"),
    "Eldest's Warden":          ("elemental_bruiser", 32, 33, None, "st_redwood_ancient"),
    "Rigboss Gazzle":           ("humanoid_ranged",   31, 31, 2.5, "st_boss_rigboss_gazzle"),
    "The Heartrot Queen":       ("beast_large",       32, 32, 2.6, "st_boss_heartrot_queen"),
    "Ambermaw":                 ("elemental_bruiser", 32, 32, 2.6, "st_boss_ambermaw"),
    "Old Talonwing":            ("beast_fast",        33, 33, 2.6, "st_boss_old_talonwing"),
    "Topper Kezzik":            ("humanoid_warrior",  33, 33, 2.7, "st_boss_topper_kezzik"),
    "The Eldest":               ("elemental_bruiser", 33, 33, 3.0, "st_boss_the_eldest"),
}


def _summon(name, who, template, kit, count, cooldown, max_alive=3, max_casts=3):
    return dict(name=name, kind="summon", amount=0, cooldown=cooldown, mana_cost=0, school="physical", duration=0,
                summon={"name": who, "template": template, "kit": kit, "count": count, "level_offset": -1,
                        "max_alive": max_alive, "max_casts": max_casts}, authored_mechanic="summon")


DUNGEON_KITS = {
    "Venture Co. Trunk Rigger": [dmg("Climbing Spike", 74), dmg("Drop From the Ropes", 90, cooldown=3),
                                 dot("Spiked Boots", 20, 3, 3)],
    "Venture Co. Hauler": [dmg("Hatchet", 78), dmg("Heave", 92, cooldown=4), buff("Hard Hat", 6, 3, {"armor": 70})],
    "Venture Co. Sap Tapper": [dmg("Tapping Spike", 74), dmg("Boiling Sap", 84, cooldown=4, school="fire", is_aoe=True),
                               debuff("Sticky", 5, 2, {"dodge_rating": -28})],
    "Heartrot Borer": [dmg("Bore", 72), dot("Heartrot", 22, 3, 3, school="nature", dispel_type="disease"),
                       debuff("Chewed Armour", 5, 3, {"armor": -90})],
    "Heartrot Drone": [dmg("Diving Mandibles", 78), dmg("Wing Buzz", 84, cooldown=4, is_aoe=True),
                       debuff("Droning", 5, 2, {"hit_rating": -9})],
    "Living Sap": [dmg("Engulf", 80, school="nature"), dot("Sticky Sap", 22, 3, 3, school="nature"),
                   debuff("Stuck Fast", 5, 2, {"dodge_rating": -30})],
    "Crown Owl": [dmg("Silent Talons", 80), dmg("Dive From Above", 96, cooldown=3),
                  debuff("Screech", 5, 2, {"spell_power": -26})],
    "Crown Sky Serpent": [dmg("Feathered Bite", 82), dmg("Coil and Strike", 96, cooldown=3, school="nature"),
                          dot("Venom", 24, 3, 3, school="nature", dispel_type="poison")],
    "Venture Co. Topper": [dmg("Topping Saw", 84), dmg("Swing From the Rope", 98, cooldown=3), dot("Ragged Cut", 22, 3, 3)],
    "Venture Co. Crown Shredder": [dmg("Saw Arm", 90), dmg("Shred", 100, cooldown=4, is_aoe=True),
                                   buff("Plating", 6, 4, {"armor": 100})],
    "Eldest's Warden": [dmg("Root Slam", 88), dmg("Thrashing Limbs", 98, cooldown=4, is_aoe=True),
                        buff("Bark Skin", 6, 4, {"armor": 80})],
    "Rigboss Gazzle": [dmg("Rig Shotgun", 170), dmg("Swinging Pulley", 214, cooldown=4),
                       dmg("Cut the Rope", 132, cooldown=5, is_aoe=True),
                       _summon("Riggers, Down!", "Venture Co. Trunk Rigger", "humanoid_rogue",
                               "venture_co_trunk_rigger", 2, 5),
                       enrage("Hazard Pay", 40)],
    "The Heartrot Queen": [dmg("Queen's Mandibles", 180), dot("Heartrot", 40, 3, 4, school="nature"),
                           debuff("Chewed Through", 5, 3, {"armor": -160}),
                           _summon("The Brood Wakes", "Heartrot Borer", "vermin_swarm", "heartrot_borer", 2, 4,
                                   max_alive=4, max_casts=4),
                           enrage("Egg-Sac Bursts", 44)],
    "Ambermaw": [dmg("Engulf", 176, school="nature"), dot("Sap in the Lungs", 42, 3, 4, school="nature"),
                 debuff("Stuck Fast", 5, 3, {"dodge_rating": -60}),
                 shield("Hardening Amber", 640, school="nature"), dmg("The Goblin Inside Kicks", 120, cooldown=6)],
    "Old Talonwing": [dmg("Talon Rake", 184), dmg("Storm Dive", 150, cooldown=3, school="nature", is_aoe=True),
                      stun("Pinned to the Branch", 130), enrage("Thunder in the Feathers", 46)],
    "Topper Kezzik": [dmg("Chainsaw Arm", 192), dmg("Spider Legs", 156, cooldown=4, is_aoe=True),
                      shield("Plating Up", 720), stun("Saw Through the Branch", 132),
                      buff("Overdrive", 7, 3, {"attack_power": 50})],
    "The Eldest": [dmg("The Weight of a Thousand Years", 200, school="nature"),
                   dmg("The Forest Answers", 160, cooldown=4, school="nature", is_aoe=True),
                   stun("Rooted", 140, school="nature"), shield("Heartwood", 760, school="nature"),
                   _summon("Wardens of the Eldest", "Eldest's Warden", "elemental_bruiser", "eldests_warden", 1, 6,
                           max_alive=2, max_casts=2),
                   enrage("It Will Not Fall", 52)],
}
DUNGEON_TABLES = {
    TRUNK: {"name": TRUNK, "creatures": {"Venture Co. Trunk Rigger": 3, "Venture Co. Hauler": 3,
                                         "Venture Co. Sap Tapper": 2, "Heartrot Borer": 3, "Heartrot Drone": 2,
                                         "Living Sap": 2, "Rigboss Gazzle": 0, "The Heartrot Queen": 0,
                                         "Ambermaw": 0}},
    CROWN: {"name": CROWN, "creatures": {"Crown Owl": 3, "Crown Sky Serpent": 3, "Venture Co. Topper": 3,
                                         "Venture Co. Crown Shredder": 2, "Eldest's Warden": 3,
                                         "Old Talonwing": 0, "Topper Kezzik": 0, "The Eldest": 0}},
}
DUNGEON_BOSSES = {n for n, r in DUNGEON_ROSTER.items() if r[3]}
#: boss pools: item level = level + 2, five each, hand-authored and spread across every kind of spec
DUNGEON_POOLS = {
    "Rigboss Gazzle": (33, [
        ("Rigboss's Harness", "chest", "armor", "leather", "agility"),
        ("Pulley-Wheel Shield", "off_hand", "weapon", "shield", "shield_tank"),
        ("Gazzle's Rig Shotgun", "ranged", "weapon", "gun", "hunter_crit"),
        ("Rope-Burned Gloves", "hands", "armor", "mail", "tide_healer"),
        ("Hard Hat of the Trunk Crew", "head", "armor", "plate", "strength"),
    ]),
    "The Heartrot Queen": (34, [
        ("Chitin Pauldrons", "shoulder", "armor", "plate", "tank"),
        ("Queen's Egg-Sac Robe", "chest", "armor", "cloth", "healer"),
        ("Borer's Mandible", "main_hand", "weapon", "fist_weapon", "wildheart"),
        ("Heartrot Girdle", "waist", "armor", "leather", "caster"),
        ("Ring of the Brood", "ring", "armor", None, "physical"),
    ]),
    "Ambermaw": (34, [
        ("Amber-Sealed Tome", "off_hand", "weapon", "tome", "caster_crit"),
        ("Sap-Stiffened Legguards", "legs", "armor", "leather", "bear"),
        ("Goblin-in-Amber Trinket", "trinket", "armor", None, "high_healer"),
        ("Amberwood Longbow", "ranged", "weapon", "bow", "hunter"),
        ("Sticky Sabatons", "feet", "armor", "plate", "crusader"),
    ]),
    "Old Talonwing": (35, [
        ("Stormfeather Cloak", "back", "armor", None, "caster"),
        ("Talonwing's Grasp", "hands", "armor", "leather", "rogue_crit"),
        ("Thunder-Roc Mantle", "shoulder", "armor", "mail", "haste_caster"),
        ("Nest-Woven Bracers", "wrist", "armor", "plate", "plate_healer"),
        ("Feather of the Storm", "ranged", "weapon", "totem", "healer"),
    ]),
    "Topper Kezzik": (35, [
        ("Topper's Chainsaw", "main_hand", "weapon", "axe_2h", "strength_crit"),
        ("Walker-Plate Breastplate", "chest", "armor", "plate", "tank"),
        ("Kezzik's Spider-Leg Spaulders", "shoulder", "armor", "leather", "agility"),
        ("Overdrive Goggles", "head", "armor", "mail", "hunter"),
        ("Saw-Tooth Polearm", "main_hand", "weapon", "polearm", "agility"),
    ]),
    "The Eldest": (35, [
        ("Heartwood of the Eldest", "main_hand", "weapon", "staff", "caster_crit"),
        ("Eldest's Living Bough", "main_hand", "weapon", "staff", "bear_weapon"),
        ("Crown of a Thousand Years", "head", "armor", "cloth", "high_healer"),
        ("Rootbound Warplate", "legs", "armor", "plate", "strength"),
        ("Bark-Grown Hauberk", "chest", "armor", "mail", "agility"),
        ("Idol of the Eldest", "ranged", "weapon", "idol", "caster"),
        ("Libram of the Standing Giants", "ranged", "weapon", "libram", "plate_healer"),
    ]),
}

CAVE_ROSTER.update(ASHVENT_ROSTER)
CAVE_KITS.update(ASHVENT_KITS)
BOSS_POOLS.update(ASHVENT_POOLS)
CAVE_BOSSES |= ASHVENT_BOSSES
CAVE_ROSTER.update(DUNGEON_ROSTER)
CAVE_KITS.update(DUNGEON_KITS)
BOSS_POOLS.update(DUNGEON_POOLS)
CAVE_BOSSES |= DUNGEON_BOSSES

#: Gathering, the same 25-30 band as the Aspen: wood heavy (it's a logging country), with the Aspen's herbs and
#: ore. Fishing in Ashfall Creek and the pond under Sun Rock.
NODES = {
    "stonetalon_east": {
        "slots": 24, "active_percent": 0.42,
        "table": {"wood_redbark_tree": 4, "wood_frostpine": 3, "wood_duskwood_stump": 3, "wood_silverbark_tree": 2,
                  "herb_briarthorn": 3, "herb_bruiseweed": 3, "herb_liferoot": 2, "herb_kingsblood": 2,
                  "herb_wild_steelbloom": 2, "ore_iron": 2, "ore_tin": 2, "ore_coal": 1, "ore_living_copper": 1},
    },
    # the West: the standing forest, so more wood; the volcano's ore on the peak
    "stonetalon_west": {
        "slots": 26, "active_percent": 0.42,
        "table": {"wood_redbark_tree": 5, "wood_frostpine": 3, "wood_silverbark_tree": 3, "wood_duskwood_stump": 2,
                  "herb_liferoot": 3, "herb_kingsblood": 3, "herb_wild_steelbloom": 3, "herb_briarthorn": 2,
                  "herb_bruiseweed": 2, "ore_iron": 4, "ore_coal": 2, "ore_living_copper": 1},
    },
}


# the two zones' open worlds are one roster, one kit set, one pool set; names never repeat across them
assert not (set(WEST_ROSTER) & set(ROSTER)), set(WEST_ROSTER) & set(ROSTER)
ROSTER.update(WEST_ROSTER)
KITSETS.update(WEST_KITS)
TABLES.update(WEST_TABLES)
POOLS.update(WEST_POOLS)
RARES |= WEST_RARES


def main():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import tools.handbuilt_stonetalon_east as SE

    import tools.handbuilt_stonetalon_west as SW
    for zone, mod in ((EAST, SE), (WEST, SW)):
        declared = {s[0] for s in mod.SUBZONES}
        if set(TABLES[zone]["subzones"]) != declared:
            print(f"FAILED: {zone} subzones disagree with the map: {sorted(set(TABLES[zone]['subzones']) ^ declared)}")
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
    import tools.handbuilt_ashvent as AVT
    AVT.build_ashvent()
    import tools.handbuilt_eldest_sequoia as ESQ
    ESQ.build_trunk()
    ESQ.build_crown()
    dungeon_bosses = set(ESQ.BOSSES["trunk"]) | set(ESQ.BOSSES["crown"])
    tabled = set(CAVE_TABLES[MINE]["creatures"]) | set(ASHVENT_TABLE[ASHVENT]["creatures"])
    for t in DUNGEON_TABLES.values():
        tabled |= set(t["creatures"])
    placed = {m for f in (ESQ._trash_trunk, ESQ._trash_crown) for pk in f() for (_x, _y, m, _l) in pk}
    if placed - set(DUNGEON_ROSTER):
        print(f"FAILED: the dungeon places creatures nobody wrote: {sorted(placed - set(DUNGEON_ROSTER))}")
        return 1
    if set(WM.BOSSES) | set(AVT.BOSSES) | dungeon_bosses != CAVE_BOSSES or set(CAVE_KITS) != set(CAVE_ROSTER) \
            or set(BOSS_POOLS) != CAVE_BOSSES or tabled != set(CAVE_ROSTER):
        print("FAILED: the caves' maps, rosters, kits, tables and pools disagree")
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
    enc["zones"][WEST].setdefault("caves", {}).update(ASHVENT_TABLE)
    enc["zones"][WEST]["caves"].update(DUNGEON_TABLES)
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
