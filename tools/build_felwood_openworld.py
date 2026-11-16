#!/usr/bin/env python3
"""Felwood's open-world creatures, rares, encounter tables and rare loot. Idempotent.

    PYTHONPATH=. python3 tools/build_felwood_openworld.py

claude/felwood_brief.md. Kyle, 14 Nov 2026: "basically a giant ass Elves vs Demons." The South is
the contested half, so what lives in it is the corruption arriving: animals going sick in the
living forest, the Deadwood furbolgs gone fel-mad in their village, Jadefire satyrs in the
Highborne ruins and the raided watch, and the Legion itself in the craters where it came down.

    SOUTH FELWOOD (51-53) - RECLAIMED. Kyle: "southern felwood will NOT get fel stuff bro, it is
    reclaimed"; only the top band "STARTS to get some fel... so it's not jarring when they go north".
      the open forest       nightsabers, old-growth grizzlies, timberline wolves, silverhorn stags
      Morlos'Aren           safe: the Sentinels' retaken watch
      Iris Lake             snapjaws and crocolisks in the purified lake
      Hollowbark Glade      old growth: treants, thornpaw sabers, restless wisps
      Ruins of Constellas   the forest's ruins now: prowlers, wisps, ivybound treants
      Shatter Scar Vale     healed craters: boars and bears in the regrowth
      The Fel Line          North Felwood bleeding through: blighted wolves, imps, a felhound, a felguard

The Deadwood, the Jadefire satyrs, the Shadow Council and the Legion proper are the North's:

    NORTH FELWOOD (53-55) - THE DEMON WASTES
      the open wastes       plaguefang wolves, fel-rotted bears, jadefire stags, seepage oozes
      Jadefire Glen         the Jadefire satyrs and their imps               rare: Prince Aelvorn the Unmade
      Bloodvenom Falls      oozes and sick animals at the poisoned pool      rare: The Bloodvenom Rot
      Jaedenar              the Shadow Council outside its hold, a turncoat  rare: Vor'alith the Turncloak
      Felbrand Crater       the Legion where it came down                    rare: Pyrrhax the Fallen Star
      Irontree Woods        warpwood treants in the dead ironwood            rare: Ironbark the Blighted
      Felpaw Village        the Deadwood                                     rare: Chieftain Grimpelt
      Talonbranch Glade, Timbermaw Gate   safe

Every creature has its own sprite from Kyle's Felwood sheet (creature_sprites._RULES). Rares are in
subzone tables only, at weight 0 (the rare roll picks them), in final form on sturdy bodies, and
their loot is item level = level + 3.
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

LOOT = ROOT / "data/loot/felwood_rare_loot.json"
SOUTH = "South Felwood"

#: name -> (template, lo, hi, boss multiplier or None, sprite)

#: name -> (template, lo, hi, boss multiplier or None, sprite)
ROSTER = {
    # the reclaimed forest, everywhere south of the Fel Line
    "Greywood Nightsaber":      ("beast_fast",        51, 52, None, "panther_1"),
    "Old-Growth Grizzly":       ("beast_large",       51, 53, None, "bear_2"),
    "Timberline Wolf":          ("beast_fast",        51, 52, None, "worg_3"),
    "Silverhorn Stag":          ("beast_fast",        51, 52, None, "stag"),
    # Iris Lake
    "Iris Snapjaw":             ("beast_large",       51, 52, None, "turtle_snapping"),
    "Lakeshore Crocolisk":      ("beast_large",       51, 52, None, "crocolisk_2"),
    # Hollowbark Glade
    "Hollowbark Treant":        ("elemental_bruiser", 52, 53, None, "treant_1"),
    "Restless Wisp":            ("elemental_caster",  52, 53, None, "wisp_1"),
    "Thornpaw Saber":           ("beast_fast",        52, 53, None, "saber_cat"),
    # the Ruins of Constellas
    "Ruin Prowler":             ("beast_fast",        52, 53, None, "panther_3"),
    "Moonlit Wisp":             ("elemental_caster",  52, 53, None, "wisp_2"),
    "Ivybound Treant":          ("elemental_bruiser", 52, 53, None, "treant_2"),
    # Shatter Scar Vale, healed
    "Moss-Tusk Boar":           ("beast_basic",       52, 53, None, "boar_3"),
    # the Fel Line: North Felwood bleeding through
    "Blighted Wolf":            ("beast_fast",        52, 53, None, "fw_blighted_wolf"),
    "Felwood Imp":              ("demon_caster",      52, 53, None, "fw_imp"),
    "Border Felhound":          ("demon_hound",       53, 53, None, "fw_felhound"),
    "Felguard Sentry":          ("humanoid_warrior",  53, 53, None, "fw_felguard"),
    # the rares, one per place
    "Old Mossback":             ("beast_large",       52, 52, 2.0, "turtle_snapping"),
    "Grandfather Hollowbark":   ("elemental_bruiser", 53, 53, 2.2, "treant_2"),
    "Saberfang the Elder":      ("beast_fast",        53, 53, 2.0, "saber_cat"),
    "Ursa Mossjaw":             ("beast_large",       53, 53, 2.1, "bear_5"),
    "Hask'zar the Scarred":     ("humanoid_warrior",  53, 53, 2.3, "fw_doomguard"),
}
RARES = {n for n, r in ROSTER.items() if r[3]}

KITSETS = {
    "Greywood Nightsaber": [dmg("Pounce", 196), dmg("Rake", 168, cooldown=3), dot("Torn Flank", 52, 3, 3)],
    "Old-Growth Grizzly": [dmg("Heavy Swipe", 204), dmg("Maul", 176, cooldown=4),
                           buff("Thick Hide", 6, 4, {"armor": 110})],
    "Timberline Wolf": [dmg("Bite", 194), dmg("Pack Lunge", 166, cooldown=3),
                        debuff("Hamstring", 5, 2, {"dodge_rating": -40})],
    "Silverhorn Stag": [dmg("Antler Gore", 196), dmg("Charge", 170, cooldown=4),
                        debuff("Trampled", 5, 2, {"attack_power": -40})],
    "Iris Snapjaw": [dmg("Snap", 200), dmg("Shell Slam", 172, cooldown=4), buff("Withdraw", 6, 2, {"armor": 160})],
    "Lakeshore Crocolisk": [dmg("Jaws", 202), dmg("Death Roll", 174, cooldown=4), dot("Deep Bite", 52, 3, 3)],
    "Hollowbark Treant": [dmg("Root Lash", 206), dmg("Thrashing Limbs", 172, cooldown=4, is_aoe=True),
                          debuff("Grasping Roots", 5, 2, {"dodge_rating": -44})],
    "Restless Wisp": [dmg("Moonfire", 198, school="arcane"), dot("Starlight Burn", 54, 3, 3, school="arcane"),
                      debuff("Dazzle", 5, 2, {"hit_rating": -10})],
    "Thornpaw Saber": [dmg("Saber Bite", 204), dmg("Shred", 172, cooldown=3), dot("Thorn Claws", 54, 3, 3)],
    "Ruin Prowler": [dmg("Pounce", 198), dmg("Ravage", 174, cooldown=4), buff("Prowl", 6, 2, {"dodge_rating": 60})],
    "Moonlit Wisp": [dmg("Starfire Mote", 200, school="arcane"), dmg("Moonburst", 168, cooldown=5, school="arcane", is_aoe=True),
                     debuff("Pale Light", 5, 3, {"spell_power": -42})],
    "Ivybound Treant": [dmg("Ivy Whip", 204), dmg("Uproot", 176, cooldown=4),
                        buff("Bark Skin", 6, 4, {"armor": 120})],
    "Moss-Tusk Boar": [dmg("Gore", 200), dmg("Boar Charge", 172, cooldown=4), buff("Bristle", 6, 3, {"armor": 90})],
    "Blighted Wolf": [dmg("Fevered Bite", 198), dmg("Pack Lunge", 168, cooldown=3),
                      dot("Rot in the Wound", 54, 3, 3, school="nature", dispel_type="disease")],
    "Felwood Imp": [dmg("Firebolt", 194, school="fire"), dmg("Fel Spark", 166, cooldown=3, school="fire"),
                    debuff("Taunting Cackle", 5, 2, {"hit_rating": -10})],
    "Border Felhound": [dmg("Fel Bite", 204), dmg("Mana Burn", 172, cooldown=4, school="shadow"),
                        debuff("Spell Lock", 6, 2, {"spell_power": -50})],
    "Felguard Sentry": [dmg("Axe of the Legion", 214), dmg("Cleave", 182, cooldown=4, is_aoe=True),
                        debuff("Intercept", 5, 1, {"dodge_rating": -50})],
    # ---- the rares, in final form
    "Old Mossback": [dmg("Ancient Jaws", 318), dmg("Shell Crush", 256, cooldown=4, is_aoe=True),
                     stun("Pinned Under", 236), shield("Mossback Shell", 950)],
    "Grandfather Hollowbark": [dmg("Elder Root Slam", 336), dmg("Forest's Anger", 268, cooldown=4, is_aoe=True),
                               stun("Entangle", 246, school="nature"), shield("Heartwood", 1000, school="nature")],
    "Saberfang the Elder": [dmg("Saber Bite", 330), dmg("Rend and Tear", 262, cooldown=4),
                            dot("Bleeding Out", 86, 3, 4), enrage("Last Hunt", 115)],
    "Ursa Mossjaw": [dmg("Crushing Maul", 338), dmg("Mossjaw Roar", 264, cooldown=4, is_aoe=True),
                     stun("Bowled Over", 248), enrage("Old Bear's Rage", 120)],
    "Hask'zar the Scarred": [dmg("Burning Whip", 340, school="fire"), dmg("War Stomp", 270, cooldown=4, is_aoe=True),
                             stun("Lash Around the Throat", 250, school="fire"), enrage("The Legion's Wrath", 120)],
}

TABLES = {
    SOUTH: {
        "open_zone": {"name": SOUTH,
                      "creatures": {"Greywood Nightsaber": 5, "Old-Growth Grizzly": 4, "Timberline Wolf": 4,
                                    "Silverhorn Stag": 3}},
        "subzones": {
            # the Sentinels' watch: retaken, and a hub like every camp
            "Morlos'Aren": {"name": "Morlos'Aren", "safe": True, "creatures": {}},
            "Iris Lake": {"name": "Iris Lake",
                          "creatures": {"Iris Snapjaw": 6, "Lakeshore Crocolisk": 5, "Silverhorn Stag": 3,
                                        "Old Mossback": 0}},
            "Hollowbark Glade": {"name": "Hollowbark Glade",
                                 "creatures": {"Hollowbark Treant": 5, "Restless Wisp": 4, "Thornpaw Saber": 5,
                                               "Grandfather Hollowbark": 0}},
            "Ruins of Constellas": {"name": "Ruins of Constellas",
                                    "creatures": {"Ruin Prowler": 5, "Moonlit Wisp": 5, "Ivybound Treant": 4,
                                                  "Saberfang the Elder": 0}},
            "Shatter Scar Vale": {"name": "Shatter Scar Vale",
                                  "creatures": {"Moss-Tusk Boar": 6, "Old-Growth Grizzly": 4, "Silverhorn Stag": 3,
                                                "Ursa Mossjaw": 0}},
            # North Felwood bleeding through: the only demons south of the line
            "The Fel Line": {"name": "The Fel Line",
                             "creatures": {"Blighted Wolf": 5, "Felwood Imp": 4, "Border Felhound": 3,
                                           "Felguard Sentry": 2, "Hask'zar the Scarred": 0}},
        },
    },
}

POOLS = {
    "Old Mossback": (55, [
        ("Mossback Shell Pauldrons", "shoulder", "armor", "plate", "str_physical"),
        ("Iris-Washed Robe", "chest", "armor", "cloth", "spi_healer"),
        ("Lakeshore Treads", "feet", "armor", "leather", "agi_int_hybrid"),
        ("Old Mossback's Fang", "main_hand", "weapon", "dagger", "agi_physical"),
    ]),
    "Grandfather Hollowbark": (56, [
        ("Heartwood Legguards", "legs", "armor", "mail", "agi_int_hybrid"),
        ("Hollowbark Crown", "head", "armor", "leather", "spi_healer"),
        ("Grandfather's Bough", "main_hand", "weapon", "staff", "int_caster"),
        ("Rootbound Girdle", "waist", "armor", "plate", "str_int_hybrid"),
    ]),
    "Saberfang the Elder": (56, [
        ("Saberfang Hide Jerkin", "chest", "armor", "leather", "agi_physical"),
        ("Elder Hunter's Hood", "head", "armor", "mail", "agi_physical"),
        ("Constellas Moonsilk Gloves", "hands", "armor", "cloth", "int_caster"),
        ("Saberfang's Claw", "main_hand", "weapon", "fist_weapon", "agi_physical"),
    ]),
    "Ursa Mossjaw": (56, [
        ("Mossjaw Warplate Leggings", "legs", "armor", "plate", "str_physical"),
        ("Scar-Healed Mantle", "shoulder", "armor", "cloth", "spi_healer"),
        ("Grizzlehide Bracers", "wrist", "armor", "leather", "agi_physical"),
        ("Mossjaw's Great Maul", "main_hand", "weapon", "mace_2h", "str_physical"),
    ]),
    "Hask'zar the Scarred": (56, [
        ("Scar-Forged Breastplate", "chest", "armor", "plate", "str_physical"),
        ("Fel Line Sentry Boots", "feet", "armor", "mail", "agi_physical"),
        ("Brand of the Scarred", "main_hand", "weapon", "dagger", "int_caster"),
        ("Hask'zar's Burning Whip", "main_hand", "weapon", "axe_1h", "str_physical"),
    ]),
}

NORTH = "North Felwood"

#: North Felwood (53-55), the demon wastes (claude/felwood_brief.md). Names never repeat the South's: a
#: creature is one entry in creatures.json, and the South's Blighted Wolf (52-53) isn't the North's.
NORTH_ROSTER = {
    # the open wastes
    "Plaguefang Wolf":          ("beast_fast",        53, 54, None, "fw_blighted_wolf"),
    "Fel-Rotted Bear":          ("beast_large",       53, 54, None, "fw_fel_bear"),
    "Jadefire Stag":            ("beast_fast",        53, 54, None, "fw_jadefire_stag"),
    "Warpwood Treant":          ("elemental_bruiser", 54, 55, None, "fw_warpwood_treant"),
    # Jadefire Glen
    "Jadefire Rogue":           ("humanoid_rogue",    53, 54, None, "fw_satyr_rogue"),
    "Jadefire Trickster":       ("humanoid_caster",   53, 54, None, "fw_satyr_trickster"),
    "Jadefire Shadowstalker":   ("humanoid_rogue",    54, 55, None, "fw_satyr_shadowstalker"),
    "Jadefire Hellcaller":      ("humanoid_caster",   54, 55, None, "fw_satyr_hellcaller"),
    "Jadefire Imp":             ("demon_caster",      53, 54, None, "fw_imp"),
    # Bloodvenom Falls
    "Seepage Ooze":             ("elemental_bruiser", 53, 54, None, "fw_toxic_ooze"),
    # Jaedenar's grounds: the Shadow Council and its turncoats
    "Shadow Council Acolyte":   ("humanoid_caster",   54, 55, None, "fw_council_acolyte"),
    "Shadow Council Warlock":   ("humanoid_caster",   54, 55, None, "fw_council_warlock"),
    "Jaedenar Hound Handler":   ("humanoid_warrior",  54, 55, None, "fw_hound_handler"),
    "Jadefire Felsworn":        ("humanoid_warrior",  54, 55, None, "fw_satyr_felsworn"),
    # Felpaw Village
    "Deadwood Warrior":         ("humanoid_warrior",  54, 55, None, "fw_deadwood_warrior"),
    "Deadwood Den Watcher":     ("humanoid_warrior",  54, 55, None, "fw_deadwood_watcher"),
    "Deadwood Pathfinder":      ("humanoid_ranged",   54, 55, None, "fw_deadwood_pathfinder"),
    "Deadwood Shaman":          ("humanoid_caster",   54, 55, None, "fw_deadwood_shaman"),
    "Deadwood Gardener":        ("humanoid_caster",   53, 54, None, "fw_deadwood_gardener"),
    # Felbrand Crater: the Legion
    "Felbrand Infernal":        ("elemental_bruiser", 55, 55, None, "fw_infernal"),
    "Felbrand Felguard":        ("humanoid_warrior",  54, 55, None, "fw_felguard"),
    "Felbrand Hellhound":       ("demon_hound",       54, 55, None, "fw_felhound"),
    "Crater Imp":               ("demon_caster",      54, 54, None, "fw_imp"),
    # the rares, one per place
    "Prince Aelvorn the Unmade": ("humanoid_caster",  54, 54, 2.2, "fw_satyr_lord"),
    "The Bloodvenom Rot":       ("elemental_bruiser", 54, 54, 2.0, "fw_toxic_ooze"),
    "Vor'alith the Turncloak":  ("humanoid_warrior",  55, 55, 2.2, "fw_satyr_felsworn"),
    "Pyrrhax the Fallen Star":  ("elemental_bruiser", 55, 55, 2.3, "fw_infernal"),
    "Ironbark the Blighted":    ("elemental_bruiser", 55, 55, 2.2, "fw_warpwood_treant"),
    "Chieftain Grimpelt":       ("humanoid_warrior",  55, 55, 2.3, "fw_deadwood_alpha"),
}

NORTH_KITS_BASE = {
    "Plaguefang Wolf": [dmg("Fevered Bite", 194), dmg("Pack Lunge", 166, cooldown=3),
                      dot("Rot in the Wound", 52, 3, 3, school="nature", dispel_type="disease")],
    "Fel-Rotted Bear": [dmg("Heavy Swipe", 204), dmg("Maul", 176, cooldown=4),
                        debuff("Reek of Rot", 5, 3, {"attack_power": -42})],
    "Jadefire Stag": [dmg("Burning Antlers", 196, school="fire"), dmg("Charge", 170, cooldown=4),
                      dot("Jadefire", 54, 3, 3, school="fire")],
    "Warpwood Treant": [dmg("Root Lash", 206), dmg("Thrashing Limbs", 172, cooldown=4, is_aoe=True),
                        debuff("Grasping Roots", 5, 2, {"dodge_rating": -44})],
    "Jadefire Rogue": [dmg("Twin Daggers", 196), dmg("Behind You", 178, cooldown=3),
                       dot("Fel-Edged Cut", 52, 3, 3, school="fire")],
    "Jadefire Trickster": [dmg("Jadefire Bolt", 196, school="fire"), dot("Smouldering Hex", 54, 3, 3, school="fire"),
                           debuff("Laughing Mischief", 5, 2, {"spell_power": -44})],
    "Jadefire Shadowstalker": [dmg("From the Shadows", 204), dmg("Cheap Shot", 170, cooldown=4),
                               buff("Fade", 6, 2, {"dodge_rating": 60})],
    "Jadefire Felsworn": [dmg("Glaive Sweep", 206), dmg("Cleave", 176, cooldown=4, is_aoe=True),
                          buff("Fel Oath", 6, 4, {"attack_power": 62})],
    "Jadefire Hellcaller": [dmg("Hellfire Bolt", 206, school="fire"),
                            dmg("Rain of Jadefire", 172, cooldown=5, school="fire", is_aoe=True),
                            dot("Immolate", 56, 3, 3, school="fire")],
    "Crater Imp": [dmg("Firebolt", 190, school="fire"), dmg("Fel Spark", 164, cooldown=3, school="fire"),
                debuff("Taunting Cackle", 5, 2, {"hit_rating": -10})],
    "Seepage Ooze": [dmg("Acid Slap", 194, school="nature"), dot("Corrosive Ooze", 54, 3, 3, school="nature"),
                     debuff("Dissolve Armour", 5, 3, {"armor": -120})],
    "Deadwood Warrior": [dmg("Spiked Club", 206), dmg("Fel-Drunk Swing", 178, cooldown=4),
                         buff("Frenzy", 6, 3, {"attack_power": 60})],
    "Deadwood Den Watcher": [dmg("Spear Thrust", 200), dmg("Shield Bash", 170, cooldown=4),
                             buff("Guard the Den", 6, 4, {"armor": 110})],
    "Deadwood Pathfinder": [dmg("Bark Arrow", 198), dmg("Pinning Shot", 170, cooldown=4),
                            dot("Rot-Tipped Arrow", 52, 3, 3, school="nature", dispel_type="poison")],
    "Deadwood Shaman": [dmg("Fel Lightning", 204, school="nature"), dot("Rotting Totem", 54, 4, 3, school="nature"),
                        debuff("Mad Chant", 5, 3, {"spell_power": -44, "attack_power": -44})],
    "Deadwood Gardener": [dmg("Seed Sling", 190, school="nature"), dot("Fel Bloom", 52, 3, 4, school="nature"),
                          debuff("Choking Spores", 5, 2, {"hit_rating": -10})],
    "Felbrand Infernal": [dmg("Burning Slam", 214, school="fire"), dmg("Immolation", 176, cooldown=4, school="fire", is_aoe=True),
                      buff("Stone Skin", 6, 4, {"armor": 140})],
    "Felbrand Felguard": [dmg("Axe of the Legion", 214), dmg("Cleave", 182, cooldown=4, is_aoe=True),
                        debuff("Intercept", 5, 1, {"dodge_rating": -50})],
    "Felbrand Hellhound": [dmg("Fel Bite", 200), dmg("Mana Burn", 170, cooldown=4, school="shadow"),
                      debuff("Spell Lock", 6, 2, {"spell_power": -50})],
    # ---- the rares, in final form
    "Vor'alith the Turncloak": [dmg("Turncloak's Glaive", 330), dmg("Sweep the Watch", 268, cooldown=4, is_aoe=True),
                                stun("Hilt to the Jaw", 240), enrage("Fel Oath Kept", 110)],
    "The Bloodvenom Rot": [dmg("Engulf", 318, school="nature"), dot("Riverbed Rot", 84, 3, 4, school="nature"),
                           dmg("Burst of Spores", 254, cooldown=4, school="nature", is_aoe=True),
                           shield("Gelid Skin", 900, school="nature")],
    "Chieftain Grimpelt": [dmg("Log Maul", 340), dmg("Earth-Shaking Stomp", 270, cooldown=4, is_aoe=True),
                           stun("Knocked Flat", 250), enrage("Blood Madness", 120)],
    "Prince Aelvorn the Unmade": [dmg("Jadefire Lance", 330, school="fire"),
                                  dmg("Ruin of the Highborne", 262, cooldown=5, school="fire", is_aoe=True),
                                  dot("Highborne Curse", 88, 3, 4, school="shadow"),
                                  shield("Mantle of Thorns", 950, school="fire")],
    "Pyrrhax the Fallen Star": [dmg("Meteor Fist", 344, school="fire"),
                                dmg("Crater Shock", 272, cooldown=4, school="fire", is_aoe=True),
                                stun("Buried in Ash", 250, school="fire"), enrage("Burning Core", 120)],
    "Ironbark the Blighted": [dmg("Ironwood Crush", 340), dmg("Thrash of the Dead Wood", 268, cooldown=4, is_aoe=True),
                              debuff("Rooted in Rot", 5, 3, {"dodge_rating": -60}),
                              shield("Petrified Bark", 950)],
    "Jadefire Imp": [dmg("Firebolt", 190, school="fire"), dmg("Fel Spark", 164, cooldown=3, school="fire"),
                     debuff("Taunting Cackle", 5, 2, {"hit_rating": -10})],
    "Shadow Council Acolyte": [dmg("Shadow Bolt", 198, school="shadow"), dot("Corruption", 54, 3, 4, school="shadow"),
                               shield("Demon Skin", 420, school="shadow")],
    "Shadow Council Warlock": [dmg("Shadow Bolt", 206, school="shadow"),
                               dmg("Hellfire", 170, cooldown=5, school="fire", is_aoe=True),
                               dot("Curse of Agony", 56, 3, 4, school="shadow")],
    "Jaedenar Hound Handler": [dmg("Spiked Whip", 204), dmg("Sic 'Em", 176, cooldown=4),
                               buff("Hound's Fury", 6, 3, {"attack_power": 60})],
}



def _lift(kit, k):
    """A kit written for 52-53, lifted to the North's 53-55 (damage and shields; debuffs stay)."""
    out = []
    for ab in kit:
        ab = dict(ab)
        if ab.get("amount"):
            ab["amount"] = int(round(ab["amount"] * k))
        if ab.get("absorb"):
            ab["absorb"] = int(round(ab["absorb"] * k))
        out.append(ab)
    return out


NORTH_KITS = {n: _lift(k, 1.07) for n, k in NORTH_KITS_BASE.items()}

NORTH_TABLES = {
    NORTH: {
        "open_zone": {"name": NORTH,
                      "creatures": {"Plaguefang Wolf": 5, "Fel-Rotted Bear": 4, "Jadefire Stag": 3,
                                    "Seepage Ooze": 2}},
        "subzones": {
            "Jadefire Glen": {"name": "Jadefire Glen",
                              "creatures": {"Jadefire Rogue": 5, "Jadefire Trickster": 4, "Jadefire Shadowstalker": 4,
                                            "Jadefire Hellcaller": 3, "Jadefire Imp": 3,
                                            "Prince Aelvorn the Unmade": 0}},
            "Bloodvenom Falls": {"name": "Bloodvenom Falls",
                                 "creatures": {"Seepage Ooze": 6, "Fel-Rotted Bear": 3, "Plaguefang Wolf": 3,
                                               "The Bloodvenom Rot": 0}},
            "Jaedenar": {"name": "Jaedenar",
                         "creatures": {"Shadow Council Acolyte": 5, "Shadow Council Warlock": 4,
                                       "Jaedenar Hound Handler": 3, "Jadefire Felsworn": 3,
                                       "Vor'alith the Turncloak": 0}},
            "Felbrand Crater": {"name": "Felbrand Crater",
                                "creatures": {"Felbrand Felguard": 5, "Felbrand Hellhound": 4, "Felbrand Infernal": 3,
                                              "Crater Imp": 4, "Pyrrhax the Fallen Star": 0}},
            "Irontree Woods": {"name": "Irontree Woods",
                               "creatures": {"Warpwood Treant": 6, "Fel-Rotted Bear": 3, "Jadefire Stag": 3,
                                             "Plaguefang Wolf": 2, "Ironbark the Blighted": 0}},
            "Felpaw Village": {"name": "Felpaw Village",
                               "creatures": {"Deadwood Warrior": 5, "Deadwood Den Watcher": 4,
                                             "Deadwood Pathfinder": 4, "Deadwood Shaman": 3,
                                             "Deadwood Gardener": 3, "Chieftain Grimpelt": 0}},
            # the Reclamation's camp, and the Timbermaw at their door
            "Talonbranch Glade": {"name": "Talonbranch Glade", "safe": True, "creatures": {}},
            "Timbermaw Gate": {"name": "Timbermaw Gate", "safe": True, "creatures": {}},
        },
    },
}

#: (item level, [(name, slot, kind, type, stat template)]). Item level = the rare's level + 3.
NORTH_POOLS = {
    "Prince Aelvorn the Unmade": (57, [
        ("Unmade Prince's Circlet", "head", "armor", "cloth", "int_caster"),
        ("Jadefire Glen Legwraps", "legs", "armor", "leather", "agi_int_hybrid"),
        ("Satyr-Lord's Horned Helm", "head", "armor", "plate", "str_int_hybrid"),
        ("Aelvorn's Jadefire Wand", "ranged", "weapon", "wand", "int_caster"),
    ]),
    "The Bloodvenom Rot": (57, [
        ("Falls-Bottom Treads", "feet", "armor", "leather", "agi_int_hybrid"),
        ("Venom-Washed Robe", "chest", "armor", "cloth", "spi_healer"),
        ("Rot-Etched Girdle", "waist", "armor", "mail", "agi_int_hybrid"),
        ("Bloodvenom Staff", "main_hand", "weapon", "staff", "spi_healer"),
    ]),
    "Vor'alith the Turncloak": (58, [
        ("Turncloak's Sentinel Hauberk", "chest", "armor", "mail", "agi_physical"),
        ("Moonwatch Cowl", "head", "armor", "cloth", "int_caster"),
        ("Oathbreaker Shoulderguards", "shoulder", "armor", "plate", "str_physical"),
        ("Vor'alith's Moonglaive", "main_hand", "weapon", "sword_1h", "agi_physical"),
    ]),
    "Pyrrhax the Fallen Star": (58, [
        ("Starfall Breastplate", "chest", "armor", "plate", "str_physical"),
        ("Infernal-Ash Boots", "feet", "armor", "mail", "agi_physical"),
        ("Crater-Glass Mantle", "shoulder", "armor", "cloth", "int_caster"),
        ("Fist of the Fallen Star", "main_hand", "weapon", "mace_1h", "str_physical"),
    ]),
    "Ironbark the Blighted": (58, [
        ("Dead Ironwood Legplates", "legs", "armor", "plate", "str_physical"),
        ("Blighted Bark Jerkin", "chest", "armor", "leather", "agi_physical"),
        ("Irontree Bracers", "wrist", "armor", "mail", "int_caster"),
        ("Ironbark Greatstaff", "main_hand", "weapon", "staff", "int_caster"),
    ]),
    "Chieftain Grimpelt": (58, [
        ("Grimpelt's Hide Mantle", "shoulder", "armor", "leather", "agi_physical"),
        ("Felpaw Warplate Leggings", "legs", "armor", "plate", "str_physical"),
        ("Fel-Drunk Shaman's Gloves", "hands", "armor", "mail", "int_caster"),
        ("Grimpelt's Log Maul", "main_hand", "weapon", "mace_2h", "str_physical"),
    ]),
}
NORTH_RARES = {n for n, r in NORTH_ROSTER.items() if r[3]}


def main():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import tools.handbuilt_felwood_south as FS
    import tools.handbuilt_felwood_north as FN
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

    for zone, mod in ((SOUTH, FS), (NORTH, FN)):
        declared = {s[0] for s in mod.SUBZONES}
        if set(TABLES[zone]["subzones"]) != declared:
            print(f"FAILED: {zone} subzones disagree with the map: "
                  f"{sorted(set(TABLES[zone]['subzones']) ^ declared)}")
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
    for name, (_t, lo, hi, mult, _s) in ROSTER.items():
        if mult and POOLS[name][0] != hi + 3:
            print(f"FAILED: {name} is level {hi} and its loot is item level {POOLS[name][0]}")
            return 1
        if not (ROOT / "assets/creatures" / f"{ROSTER[name][4]}.png").exists():
            print(f"FAILED: {name}'s sprite {ROSTER[name][4]} is not on disk")
            return 1

    creatures = {}
    for name, (template, lo, hi, mult, _sprite) in ROSTER.items():
        e = {"template": template, "level_range": [lo, hi], "is_boss": bool(mult),
             "ability_kit": kit_slug(name)}
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
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False)
                          + ("\n" if newline else ""), encoding="utf-8")
    for zone, table in TABLES.items():
        print(f"  encounters.json: {zone}, open zone + {len(table['subzones'])} subzones")

    from entities.loot_generator import LootGenerator
    from entities.item_budget import fit_to_curve
    from tools.fit_rares_to_curve import give_lead
    gen = LootGenerator()
    out = {"_notes": ("Felwood's open-world rares. Identity hand-authored in tools/build_felwood_openworld.py; "
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
            d["item_id"] = "fw_" + name.lower().replace("'", "").replace(" ", "_").replace("-", "_")
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
