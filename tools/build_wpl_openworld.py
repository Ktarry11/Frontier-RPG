#!/usr/bin/env python3
"""The Western Plaguelands' open-world creatures, rares, encounter tables and rare loot. Idempotent.

    PYTHONPATH=. python3 tools/build_wpl_openworld.py

docs/plaguelands_design.md. Kyle, 16 Nov 2026: "WPL and EPL? ... Keep the similar cauldron quests", and "It should feel
familar-ish for players." So what lives here is what lived in WoW's: the Scourge working the cauldrons and holding
Andorhal, the plague in everything that breathes, the Cult of the Damned tending it all, and the Scarlet Crusade
pushing patrols down from Hearthglen.

    SOUTH WESTERN PLAGUELANDS (51-54)
      the open fields       plagued wolves, diseased bears, carrion vultures, wandering skeletons
      Felstone Field        the cauldron: cultists, ghouls, a cauldron lord          rare: Farmer Felstone
      Dalson's Tears        the cauldron and the barn: ghouls, skeletons, a bound spirit  rare: The Dalson Ghost
      The Writhing Haunt    the cauldron: banshees, crypt fiends, cultists            rare: Mother of the Haunt
      Andorhal              the Scourge's city: skeletons, abominations, necromancers;
                            Scarlet patrols pushing in from the north                 rare: Magistrate Andor
      Darrowmere Lake       drowned dead and lake beasts                              rare: Old Darrowjaw
      Caer Darrow           the island's restless dead, outside Scholomance           rare: The Groundskeeper
      Sorrow Hill           the Order left it for the Bulwark; the dead came back up the hill
      Bulwark Gate, Uther's Tomb   safe (the Bulwark itself is a town map now, tools/handbuilt_bulwark.py)

THE PURE 60 RULE (entities/material_tiers.py): nothing here is pure 60, so nothing here may drop or grow a post-game
material, and the rares' loot is item level = level + 3 like every rare.
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

LOOT = ROOT / "data/loot/plaguelands_rare_loot.json"
SOUTH = "Western Plaguelands South"

#: name -> (template, lo, hi, boss multiplier or None, sprite)
ROSTER = {
    # the open fields
    "Plague-Ridden Wolf":       ("beast_fast",        51, 52, None, "worg_4"),
    "Diseased Black Bear":      ("beast_large",       51, 53, None, "bear_3"),
    "Plaguewing Vulture":          ("beast_fast",        51, 52, None, "vulture_2"),
    "Wandering Skeleton":       ("undead_warrior",    51, 52, None, "skeleton_warrior_2"),
    # Felstone Field
    "Felstone Cultist":         ("humanoid_caster",   51, 52, None, "cultist_robed_2"),
    "Felstone Ghoul":           ("undead_basic",      51, 52, None, "ghoul_1"),
    "Felstone Cauldron Lord":   ("undead_warrior",    52, 52, None, "abomination_1"),
    # Dalson's Tears
    "Dalson's Ghoul":           ("undead_basic",      52, 53, None, "ghoul_2"),
    "Dalson's Skeleton":        ("undead_warrior",    52, 53, None, "skeleton_warrior_1"),
    "Cauldron Necrolyte":       ("undead_caster",     52, 53, None, "necromancer"),
    # the Writhing Haunt
    "Haunt Banshee":            ("undead_caster",     52, 53, None, "banshee"),
    "Writhing Crypt Fiend":     ("undead_beast",      52, 53, None, "spider_broodmother_1"),
    "Haunt Cult Tender":        ("humanoid_caster",   52, 53, None, "cultist_robed_4"),
    # Andorhal
    "Andorhal Skeleton":        ("undead_warrior",    53, 54, None, "skeleton_warrior_2"),
    "Andorhal Abomination":     ("undead_warrior",    53, 54, None, "abomination_2"),
    "Andorhal Necromancer":     ("undead_caster",     53, 54, None, "necromancer"),
    "Andorhal Skeletal Archer": ("undead_warrior",    53, 54, None, "skeleton_archer"),
    "Scarlet Outrider":         ("humanoid_warrior",  53, 54, None, "scarlet_crusader"),
    "Scarlet Field Chaplain":   ("humanoid_caster",   53, 54, None, "scarlet_priest"),
    # Darrowmere Lake
    "Drowned Lakewalker":       ("undead_basic",      52, 53, None, "zombie_4"),
    "Darrowmere Snapjaw":       ("beast_large",       52, 53, None, "turtle_snapping"),
    # Caer Darrow
    "Caer Darrow Shade":        ("undead_caster",     53, 54, None, "wraith_pale"),
    "Caer Darrow Ghoul":        ("undead_basic",      53, 54, None, "ghoul_gaunt"),
    # the rares, one per place
    "Farmer Felstone":          ("undead_warrior",    52, 52, 2.1, "scarecrow_golem"),
    "The Dalson Ghost":         ("undead_caster",     53, 53, 2.0, "wraith_2"),
    "Mother of the Haunt":      ("undead_caster",     53, 53, 2.1, "banshee"),
    "Magistrate Andor":         ("undead_caster",     54, 54, 2.3, "necromancer"),
    "Old Darrowjaw":            ("beast_large",       53, 53, 2.0, "turtle_snapping"),
    "The Groundskeeper":        ("undead_warrior",    54, 54, 2.2, "abomination_1"),
}
RARES = {n for n, r in ROSTER.items() if r[3]}

KITSETS = {
    "Plague-Ridden Wolf": [dmg("Fevered Bite", 192), dmg("Pack Lunge", 164, cooldown=3),
                           dot("Plague Bite", 50, 3, 3, school="nature", dispel_type="disease")],
    "Diseased Black Bear": [dmg("Heavy Swipe", 200), dmg("Maul", 172, cooldown=4),
                            debuff("Reek of Sickness", 5, 3, {"attack_power": -40})],
    "Plaguewing Vulture": [dmg("Tearing Beak", 190), dmg("Dive", 164, cooldown=3),
                        dot("Carrion Rot", 48, 3, 3, school="nature", dispel_type="disease")],
    "Wandering Skeleton": [dmg("Rusted Blade", 194), dmg("Bone Bash", 166, cooldown=3),
                           buff("Bone Armour", 6, 3, {"armor": 100})],
    "Felstone Cultist": [dmg("Shadow Bolt", 194, school="shadow"), dot("Plague Cloud", 52, 3, 3, school="nature",
                                                                     dispel_type="disease"),
                         shield("Dark Ward", 380, school="shadow")],
    "Felstone Ghoul": [dmg("Ghoulish Claw", 194), dmg("Gnaw", 166, cooldown=3),
                       dot("Ghoul Rot", 50, 3, 3, school="nature", dispel_type="disease")],
    "Felstone Cauldron Lord": [dmg("Hook Swing", 210), dmg("Cauldron Slop", 176, cooldown=4, school="nature", is_aoe=True),
                               buff("Stitched Hide", 6, 4, {"armor": 130})],
    "Dalson's Ghoul": [dmg("Ghoulish Claw", 196), dmg("Gnaw", 168, cooldown=3),
                       dot("Ghoul Rot", 52, 3, 3, school="nature", dispel_type="disease")],
    "Dalson's Skeleton": [dmg("Rusted Blade", 198), dmg("Bone Bash", 170, cooldown=3),
                          buff("Bone Armour", 6, 3, {"armor": 104})],
    "Cauldron Necrolyte": [dmg("Shadow Bolt", 200, school="shadow"), dot("Wasting Curse", 54, 3, 4, school="shadow"),
                           debuff("Enfeeble", 5, 3, {"attack_power": -44})],
    "Haunt Banshee": [dmg("Wail", 198, school="shadow"), dmg("Keening", 166, cooldown=5, school="shadow", is_aoe=True),
                      debuff("Deafening Scream", 5, 2, {"spell_power": -44})],
    "Writhing Crypt Fiend": [dmg("Crypt Bite", 204), dmg("Web Spray", 170, cooldown=4),
                             dot("Crypt Poison", 54, 3, 3, school="nature", dispel_type="poison")],
    "Haunt Cult Tender": [dmg("Shadow Bolt", 198, school="shadow"), dot("Plague Cloud", 54, 3, 3, school="nature",
                                                                      dispel_type="disease"),
                          buff("Dark Offering", 6, 3, {"spell_power": 50})],
    "Andorhal Skeleton": [dmg("Notched Sword", 204), dmg("Shield Bash", 172, cooldown=4),
                          buff("Bone Armour", 6, 3, {"armor": 110})],
    "Andorhal Abomination": [dmg("Cleaver", 214), dmg("Poison Cloud", 178, cooldown=4, school="nature", is_aoe=True),
                             buff("Stitched Hide", 6, 4, {"armor": 140})],
    "Andorhal Necromancer": [dmg("Shadow Bolt", 206, school="shadow"), dot("Unholy Rot", 56, 3, 4, school="shadow"),
                             shield("Bone Shield", 420, school="shadow")],
    "Andorhal Skeletal Archer": [dmg("Bone Arrow", 200), dmg("Volley", 170, cooldown=5, is_aoe=True),
                                 debuff("Pinned", 5, 2, {"dodge_rating": -44})],
    "Scarlet Outrider": [dmg("Crusader Strike", 206), dmg("Holy Strike", 176, cooldown=4, school="holy"),
                         buff("Devotion", 6, 4, {"armor": 120})],
    "Scarlet Field Chaplain": [dmg("Smite", 200, school="holy"), dmg("Holy Fire", 172, cooldown=4, school="holy"),
                               shield("Power Word: Shield", 420, school="holy")],
    "Drowned Lakewalker": [dmg("Waterlogged Fist", 198), dmg("Drag Under", 168, cooldown=4),
                           dot("Lakewater Rot", 52, 3, 3, school="nature", dispel_type="disease")],
    "Darrowmere Snapjaw": [dmg("Snap", 202), dmg("Shell Slam", 172, cooldown=4), buff("Withdraw", 6, 2, {"armor": 160})],
    "Caer Darrow Shade": [dmg("Chill of the Grave", 204, school="frost"), dot("Haunting", 56, 3, 4, school="shadow"),
                          debuff("Fear's Touch", 5, 2, {"hit_rating": -10})],
    "Caer Darrow Ghoul": [dmg("Ghoulish Claw", 202), dmg("Gnaw", 172, cooldown=3),
                          dot("Ghoul Rot", 54, 3, 3, school="nature", dispel_type="disease")],
    # ---- the rares, in final form
    "Farmer Felstone": [dmg("Rusted Scythe", 316), dmg("Reaping Sweep", 254, cooldown=4, is_aoe=True),
                        stun("Pitchfork Pin", 232), enrage("The Harvest Won't Wait", 110)],
    "The Dalson Ghost": [dmg("Grieving Touch", 322, school="shadow"),
                         dmg("A Father's Wail", 258, cooldown=4, school="shadow", is_aoe=True),
                         dot("Bound to the Barn", 84, 3, 4, school="shadow"), shield("Spectral Veil", 900, school="shadow")],
    "Mother of the Haunt": [dmg("Shriek", 326, school="shadow"),
                            dmg("Chorus of the Dead", 262, cooldown=4, school="shadow", is_aoe=True),
                            stun("Paralysing Wail", 238, school="shadow"), shield("Grave Mist", 920, school="shadow")],
    "Magistrate Andor": [dmg("Death Bolt", 336, school="shadow"),
                         dmg("Edict of Andorhal", 268, cooldown=5, school="shadow", is_aoe=True),
                         dot("Withering Decree", 88, 3, 4, school="shadow"), shield("Bone Barrier", 980, school="shadow")],
    "Old Darrowjaw": [dmg("Ancient Jaws", 324), dmg("Lake-Bottom Crush", 258, cooldown=4, is_aoe=True),
                      stun("Dragged Under", 240), shield("Mossback Shell", 940)],
    "The Groundskeeper": [dmg("Spade Cleave", 340), dmg("Grave-Turning Slam", 270, cooldown=4, is_aoe=True),
                          stun("Buried Alive", 248), enrage("Keep Off the Grass", 120)],
}

TABLES = {
    SOUTH: {
        "open_zone": {"name": SOUTH,
                      "creatures": {"Plague-Ridden Wolf": 5, "Diseased Black Bear": 3, "Plaguewing Vulture": 4,
                                    "Wandering Skeleton": 3}},
        "subzones": {
            "Bulwark Gate": {"name": "Bulwark Gate", "safe": True, "creatures": {}},
            "Sorrow Hill": {"name": "Sorrow Hill", "creatures": {"Wandering Skeleton": 5, "Andorhal Skeleton": 3}},
            "Uther's Tomb": {"name": "Uther's Tomb", "safe": True, "creatures": {}},
            "Felstone Field": {"name": "Felstone Field",
                               "creatures": {"Felstone Cultist": 5, "Felstone Ghoul": 6, "Felstone Cauldron Lord": 2,
                                             "Farmer Felstone": 0}},
            "Dalson's Tears": {"name": "Dalson's Tears",
                               "creatures": {"Dalson's Ghoul": 6, "Dalson's Skeleton": 5, "Cauldron Necrolyte": 3,
                                             "The Dalson Ghost": 0}},
            "The Writhing Haunt": {"name": "The Writhing Haunt",
                                   "creatures": {"Haunt Banshee": 5, "Writhing Crypt Fiend": 4, "Haunt Cult Tender": 4,
                                                 "Mother of the Haunt": 0}},
            "Andorhal": {"name": "Andorhal",
                         "creatures": {"Andorhal Skeleton": 6, "Andorhal Abomination": 3, "Andorhal Necromancer": 4,
                                       "Andorhal Skeletal Archer": 4, "Scarlet Outrider": 2,
                                       "Scarlet Field Chaplain": 1, "Magistrate Andor": 0}},
            "Darrowmere Lake": {"name": "Darrowmere Lake",
                                "creatures": {"Drowned Lakewalker": 5, "Darrowmere Snapjaw": 5, "Plaguewing Vulture": 2,
                                              "Old Darrowjaw": 0}},
            "Caer Darrow": {"name": "Caer Darrow",
                            "creatures": {"Caer Darrow Shade": 5, "Caer Darrow Ghoul": 5, "The Groundskeeper": 0}},
        },
    },
}

#: (item level, [(name, slot, kind, type, stat template)]). Item level = the rare's level + 3.
POOLS = {
    "Farmer Felstone": (55, [
        ("Felstone Harvester's Mantle", "shoulder", "armor", "plate", "str_physical"),
        ("Cauldron-Stained Gloves", "hands", "armor", "cloth", "int_caster"),
        ("Scarecrow's Jerkin", "chest", "armor", "leather", "agi_physical"),
        ("Felstone's Rusted Scythe", "main_hand", "weapon", "polearm", "str_physical"),
    ]),
    "The Dalson Ghost": (56, [
        ("Dalson's Mourning Shroud", "back", "armor", "cloth", "spi_healer"),
        ("Barn-Loft Treads", "feet", "armor", "mail", "agi_int_hybrid"),
        ("Father's Last Belt", "waist", "armor", "leather", "spi_healer"),
        ("Tearstained Locket", "neck", "armor", None, "int_caster"),
    ]),
    "Mother of the Haunt": (56, [
        ("Haunt-Mother's Veil", "head", "armor", "cloth", "int_caster"),
        ("Writhing Legguards", "legs", "armor", "mail", "agi_physical"),
        ("Keening Bracers", "wrist", "armor", "plate", "str_int_hybrid"),
        ("Wail of the Haunt", "ranged", "weapon", "wand", "int_caster"),
    ]),
    "Magistrate Andor": (57, [
        ("Magistrate's Robes of Office", "chest", "armor", "cloth", "int_caster"),
        ("Andorhal Gatewarden's Helm", "head", "armor", "plate", "str_physical"),
        ("Edict-Bound Leggings", "legs", "armor", "leather", "agi_int_hybrid"),
        ("Rod of the Fallen City", "main_hand", "weapon", "staff", "int_caster"),
    ]),
    "Old Darrowjaw": (56, [
        ("Darrowjaw Shell Shoulders", "shoulder", "armor", "mail", "agi_physical"),
        ("Lakebed Robe", "chest", "armor", "cloth", "spi_healer"),
        ("Darrowmere Waders", "feet", "armor", "leather", "agi_physical"),
        ("Darrowjaw's Fang", "main_hand", "weapon", "dagger", "agi_physical"),
    ]),
    "The Groundskeeper": (57, [
        ("Groundskeeper's Spade", "main_hand", "weapon", "mace_2h", "str_physical"),
        ("Caer Darrow Gardening Gloves", "hands", "armor", "leather", "spi_healer"),
        ("Gravedigger's Girdle", "waist", "armor", "plate", "str_physical"),
        ("Island-Keeper's Cord", "waist", "armor", "cloth", "int_caster"),
    ]),
}


NORTH = "Western Plaguelands North"

#: North WPL (53-56): the Scarlet Crusade's country under Hearthglen, and the fourth cauldron. Names never repeat
#: the South's: a creature is one entry in creatures.json.
NORTH_ROSTER = {
    # the open hills
    "Rotting Worg":             ("beast_fast",        53, 54, None, "worg_6"),
    "Blighted Stag":            ("beast_fast",        53, 54, None, "stag"),
    "Plague Bat":               ("beast_fast",        53, 54, None, "bat"),
    "Skeletal Wanderer":        ("undead_warrior",    53, 54, None, "skeleton_warrior_1"),
    # Northridge Lumber Camp
    "Scarlet Lumberjack":       ("humanoid_warrior",  53, 54, None, "scarlet_crusader"),
    "Scarlet Sawyer":           ("humanoid_warrior",  53, 54, None, "scarlet_crusader"),
    "Scarlet Woodsman Archer":  ("humanoid_ranged",   53, 54, None, "scarlet_archer"),
    # Gahrron's Withering
    "Withering Ghoul":          ("undead_basic",      54, 55, None, "ghoul_gaunt"),
    "Withering Cultist":        ("humanoid_caster",   54, 55, None, "cultist_robed_5"),
    "Cauldron Sludge":          ("elemental_bruiser", 54, 55, None, "slime_green_1"),
    # Hearthglen Fields
    "Scarlet Sentry":           ("humanoid_warrior",  55, 56, None, "scarlet_crusader"),
    "Hearthglen Inquisitor":       ("humanoid_caster",   55, 56, None, "scarlet_priest"),
    "Scarlet Crossbowman":      ("humanoid_ranged",   55, 56, None, "scarlet_archer"),
    "Scarlet War Hound":        ("beast_fast",        55, 56, None, "worg_5"),
    # the Thondroril
    "Thondroril Snapjaw":       ("beast_large",       54, 55, None, "turtle_snapping"),
    "Riverbank Ghoul":          ("undead_basic",      54, 55, None, "zombie_5"),
    # the rares
    "Foreman Harrow":           ("humanoid_warrior",  55, 55, 2.1, "scarlet_crusader"),
    "Gahrron the Withered":     ("undead_warrior",    56, 56, 2.2, "abomination_2"),
    "High Inquisitor Faulk":    ("humanoid_caster",   56, 56, 2.3, "scarlet_priest"),
    "Old Thondroril":           ("beast_large",       55, 55, 2.0, "turtle_snapping"),
}

NORTH_KITS_BASE = {
    "Rotting Worg": [dmg("Fevered Bite", 194), dmg("Pack Lunge", 166, cooldown=3),
                     dot("Plague Bite", 52, 3, 3, school="nature", dispel_type="disease")],
    "Blighted Stag": [dmg("Dead Antlers", 196), dmg("Charge", 170, cooldown=4),
                      debuff("Trampled", 5, 2, {"attack_power": -40})],
    "Plague Bat": [dmg("Bite", 190), dmg("Screech", 160, cooldown=4, is_aoe=True),
                   dot("Plague Fever", 50, 3, 3, school="nature", dispel_type="disease")],
    "Skeletal Wanderer": [dmg("Rusted Blade", 198), dmg("Bone Bash", 170, cooldown=3),
                          buff("Bone Armour", 6, 3, {"armor": 104})],
    "Scarlet Lumberjack": [dmg("Woodsman's Axe", 204), dmg("Felling Blow", 174, cooldown=4),
                           buff("Zeal", 6, 3, {"attack_power": 56})],
    "Scarlet Sawyer": [dmg("Bucksaw", 200), dmg("Splinter", 170, cooldown=3),
                       dot("Ragged Cut", 52, 3, 3)],
    "Scarlet Woodsman Archer": [dmg("Longbow Shot", 200), dmg("Pinning Shot", 170, cooldown=4),
                                debuff("Pinned", 5, 2, {"dodge_rating": -44})],
    "Withering Ghoul": [dmg("Ghoulish Claw", 202), dmg("Gnaw", 172, cooldown=3),
                        dot("Ghoul Rot", 54, 3, 3, school="nature", dispel_type="disease")],
    "Withering Cultist": [dmg("Shadow Bolt", 202, school="shadow"),
                          dot("Plague Cloud", 54, 3, 3, school="nature", dispel_type="disease"),
                          shield("Dark Ward", 400, school="shadow")],
    "Cauldron Sludge": [dmg("Acid Slap", 198, school="nature"), dot("Corrosive Ooze", 54, 3, 3, school="nature"),
                        debuff("Dissolve Armour", 5, 3, {"armor": -120})],
    "Scarlet Sentry": [dmg("Crusader Strike", 210), dmg("Shield Bash", 178, cooldown=4),
                       buff("Devotion", 6, 4, {"armor": 124})],
    "Hearthglen Inquisitor": [dmg("Smite", 206, school="holy"), dmg("Purifying Fire", 176, cooldown=4, school="holy"),
                           debuff("Interrogate", 5, 2, {"spell_power": -46})],
    "Scarlet Crossbowman": [dmg("Crossbow Bolt", 206), dmg("Volley", 172, cooldown=5, is_aoe=True),
                            debuff("Pinned", 5, 2, {"dodge_rating": -46})],
    "Scarlet War Hound": [dmg("Savage Bite", 204), dmg("Hamstring Lunge", 172, cooldown=3),
                          debuff("Hamstring", 5, 2, {"dodge_rating": -44})],
    "Thondroril Snapjaw": [dmg("Snap", 204), dmg("Shell Slam", 174, cooldown=4), buff("Withdraw", 6, 2, {"armor": 164})],
    "Riverbank Ghoul": [dmg("Waterlogged Fist", 202), dmg("Drag Under", 170, cooldown=4),
                        dot("River Rot", 54, 3, 3, school="nature", dispel_type="disease")],
    "Foreman Harrow": [dmg("Foreman's Axe", 330), dmg("Timber!", 262, cooldown=4, is_aoe=True),
                       stun("Log to the Head", 240), enrage("Behind Schedule", 110)],
    "Gahrron the Withered": [dmg("Withering Hook", 342), dmg("Cauldron Spill", 272, cooldown=4, school="nature", is_aoe=True),
                             dot("Withering", 90, 3, 4, school="nature", dispel_type="disease"),
                             shield("Stitched Bulk", 1000)],
    "High Inquisitor Faulk": [dmg("Searing Light", 338, school="holy"),
                              dmg("Pyre of the Faithful", 268, cooldown=5, school="holy", is_aoe=True),
                              stun("Hammer of Judgement", 246, school="holy"), shield("Zealot's Ward", 980, school="holy")],
    "Old Thondroril": [dmg("Ancient Jaws", 328), dmg("Riverbed Crush", 262, cooldown=4, is_aoe=True),
                       stun("Dragged Under", 242), shield("River Shell", 950)],
}

NORTH_TABLES = {
    NORTH: {
        "open_zone": {"name": NORTH,
                      "creatures": {"Rotting Worg": 5, "Blighted Stag": 3, "Plague Bat": 4, "Skeletal Wanderer": 3}},
        "subzones": {
            "Pale Watch Gate": {"name": "Pale Watch Gate", "safe": True, "creatures": {}},
            "Northridge Lumber Camp": {"name": "Northridge Lumber Camp",
                                       "creatures": {"Scarlet Lumberjack": 5, "Scarlet Sawyer": 5,
                                                     "Scarlet Woodsman Archer": 4, "Foreman Harrow": 0}},
            "Gahrron's Withering": {"name": "Gahrron's Withering",
                                    "creatures": {"Withering Ghoul": 6, "Withering Cultist": 4, "Cauldron Sludge": 3,
                                                  "Gahrron the Withered": 0}},
            "Hearthglen Fields": {"name": "Hearthglen Fields",
                                  "creatures": {"Scarlet Sentry": 5, "Hearthglen Inquisitor": 4, "Scarlet Crossbowman": 4,
                                                "Scarlet War Hound": 4, "High Inquisitor Faulk": 0}},
            "The Thondroril": {"name": "The Thondroril",
                               "creatures": {"Thondroril Snapjaw": 5, "Riverbank Ghoul": 5, "Plague Bat": 2,
                                             "Old Thondroril": 0}},
        },
    },
}

NORTH_POOLS = {
    "Foreman Harrow": (58, [
        ("Northridge Foreman's Hauberk", "chest", "armor", "mail", "agi_physical"),
        ("Sawdust-Caked Gloves", "hands", "armor", "plate", "str_physical"),
        ("Timberline Cowl", "head", "armor", "leather", "agi_int_hybrid"),
        ("Harrow's Felling Axe", "main_hand", "weapon", "axe_2h", "str_physical"),
    ]),
    "Gahrron the Withered": (59, [
        ("Withered Farmer's Mantle", "shoulder", "armor", "leather", "agi_physical"),
        ("Cauldron-Keeper's Robe", "chest", "armor", "cloth", "int_caster"),
        ("Stitched Warplate Legs", "legs", "armor", "plate", "str_physical"),
        ("Gahrron's Plague Hook", "main_hand", "weapon", "sword_1h", "str_physical"),
    ]),
    "High Inquisitor Faulk": (59, [
        ("Inquisitor's Crimson Vestments", "chest", "armor", "cloth", "spi_healer"),
        ("Faulk's Judgement Gauntlets", "hands", "armor", "plate", "str_int_hybrid"),
        ("Pyrewatch Girdle", "waist", "armor", "mail", "int_caster"),
        ("Hammer of the Faithful Pyre", "main_hand", "weapon", "mace_1h", "spi_healer"),
    ]),
    "Old Thondroril": (58, [
        ("Thondroril Shell Pauldrons", "shoulder", "armor", "plate", "str_physical"),
        ("Riverstone Treads", "feet", "armor", "mail", "agi_int_hybrid"),
        ("Rivermoss Bracers", "wrist", "armor", "cloth", "spi_healer"),
        ("Old Thondroril's Tooth", "main_hand", "weapon", "dagger", "agi_physical"),
    ]),
}
NORTH_RARES = {n for n, r in NORTH_ROSTER.items() if r[3]}


def _lift(kit, k):
    out = []
    for ab in kit:
        ab = dict(ab)
        if ab.get("amount"):
            ab["amount"] = int(round(ab["amount"] * k))
        if ab.get("absorb"):
            ab["absorb"] = int(round(ab["absorb"] * k))
        out.append(ab)
    return out


NORTH_KITS = {n: _lift(k, 1.06) for n, k in NORTH_KITS_BASE.items()}


def main():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import tools.handbuilt_wpl_south as WS
    import tools.handbuilt_wpl_north as WN
    global ROSTER, KITSETS, TABLES, POOLS, RARES
    clash = set(ROSTER) & set(NORTH_ROSTER)
    if clash:
        print(f"FAILED: the South and the North share creature names: {sorted(clash)}")
        return 1
    ROSTER = {**ROSTER, **NORTH_ROSTER}
    KITSETS = {**KITSETS, **NORTH_KITS}
    TABLES = {**TABLES, **NORTH_TABLES}
    POOLS = {**POOLS, **NORTH_POOLS}
    RARES = RARES | NORTH_RARES

    for zone, mod in ((SOUTH, WS), (NORTH, WN)):
        declared = {s[0] for s in mod.SUBZONES}
        if set(TABLES[zone]["subzones"]) != declared:
            print(f"FAILED: {zone} subzones disagree with the map: {sorted(set(TABLES[zone]['subzones']) ^ declared)}")
            return 1
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
    existing = json.loads(CREATURES.read_text(encoding="utf-8"))["creatures"]
    kits_now = json.loads(KITS.read_text(encoding="utf-8"))["kits"]
    owners = {v.get("ability_kit"): n for n, v in existing.items()}
    for name in ROSTER:
        k = kit_slug(name)
        if k in kits_now and owners.get(k, name) != name:
            print(f"FAILED: {name}'s kit '{k}' already belongs to {owners[k]}; pick another name")
            return 1
    for name, (_t, lo, hi, mult, sprite) in ROSTER.items():
        if mult and POOLS[name][0] != hi + 3:
            print(f"FAILED: {name} is level {hi} and its loot is item level {POOLS[name][0]}")
            return 1
        if not (ROOT / "assets/creatures" / f"{sprite}.png").exists():
            print(f"FAILED: {name}'s sprite {sprite} is not on disk")
            return 1
        prior = existing.get(name)
        if prior and prior.get("level_range") != [lo, hi]:
            print(f"FAILED: {name} already exists elsewhere ({prior.get('level_range')}); names never repeat")
            return 1

    creatures = {}
    for name, (template, lo, hi, mult, _sprite) in ROSTER.items():
        e = {"template": template, "level_range": [lo, hi], "is_boss": bool(mult), "ability_kit": kit_slug(name)}
        if mult:
            e["boss_multiplier"] = mult
        creatures[name] = e
    merge_json(CREATURES, "creatures", creatures, "creatures.json")
    merge_json(KITS, "kits", {kit_slug(n): k for n, k in KITSETS.items()}, "ability_kits.json")

    raw = ENCOUNTERS.read_text(encoding="utf-8")
    enc = json.loads(raw)
    indent, newline = _detect_format(enc, raw)
    for zone, table in TABLES.items():
        entry = enc.setdefault("zones", {}).setdefault(zone, {})
        entry["open_zone"] = table["open_zone"]
        entry["subzones"] = table["subzones"]
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False) + ("\n" if newline else ""),
                          encoding="utf-8")
    for zone, table in TABLES.items():
        print(f"  encounters.json: {zone}, open zone + {len(table['subzones'])} subzones")

    from entities.loot_generator import LootGenerator
    from entities.item_budget import fit_to_curve
    from tools.fit_rares_to_curve import give_lead
    gen = LootGenerator()
    out = {"_notes": ("The Plaguelands' open-world rares. Identity hand-authored in tools/build_wpl_openworld.py; "
                      "stats from LootGenerator at rare budget.")}
    rows = []
    for boss, (ilvl, items) in POOLS.items():
        built = []
        for (name, slot, kind, atype, template) in items:
            if kind == "armor":
                it = gen.generate_armor_piece(slot, atype, template, ilvl, "rare")
            else:
                it = gen.generate_weapon(slot, atype, template, ilvl, "rare", strict=True)
            if it is None:
                print(f"FAILED: the generator would not build {name}")
                return 1
            d = it.to_dict()
            give_lead(d)        # on the item curve (tools/fit_rares_to_curve.py, Kyle 16 Nov)
            fit_to_curve(d)
            d["name"] = name
            d["item_id"] = "pl_" + name.lower().replace("'", "").replace(" ", "_").replace("-", "_")
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
