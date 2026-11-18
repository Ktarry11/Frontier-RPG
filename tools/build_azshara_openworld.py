#!/usr/bin/env python3
"""Azshara's open-world creatures, rares, encounter tables, rare loot and gathering. Idempotent.

    PYTHONPATH=. python3 tools/build_azshara_openworld.py

docs/azshara_brief.md. The enemies Kyle picked on 17 Nov 2026: the naga coming up with the city, the Highborne ghosts,
the satyrs and demons (the Legion's leftovers and the fel rot), and the blue dragonflight guarding the leylines,
plus the autumn forest's beasts. Sprites are Kyle's Azshara creature sheet (sheet 5), with Felwood's satyrs and imp
filling out the camps.

    WEST AZSHARA (52-55)     the open forest: timber wolves, russet boars, cliff hippogryphs, autumn treants
      Ursolan                 the pass to the Hold: wolves and hippogryphs
      Shadowsong Shrine       the Sentinels who never left it
      Ravencrest Monument     Highborne shades round the old monument
      Haldarr Encampment      Haldarr's satyrs above the den                        rare: Vrexx the Hornbreaker
      The Sundering Mere      thunder lizards in the shallows                       rare: Old Stormhide
      Talrendis Point, Valormok   safe
    CENTRAL AZSHARA (54-57)
      Legash Encampment       the satyrs' war camp                                  rare: Warlord Seth'rak
      Forlorn Ridge           the Legion's leftovers round the gate                 rare: Gatekeeper Azgaroth
      Lake Mennar             the blues and the mana wyrms at the Font              rare: Azurewing
      Ruins of Eldarath       shades and constructs round the dig
      Bay of Storms, Hetaera's Clutch   the naga's beachhead
      Southridge Beach        crabs and serpent hatchlings
    EAST AZSHARA (56-59)
      The Bitter Reaches      naga raiders among the wrecks                         rare: Captain Ssarith
      Tower of Eldara         its guardians and the wyrms it feeds                  rare: Magus Valethion
      The Drowned Promenade   the ghosts on the boulevard
      The Drowned Court       the risen district's dead and the naga's guard        rare: The Weeping Duchess
      Temple of Zin-Malor     the naga's temple                                     rare: High Priestess Naz'eth
      The Jagged Reef         crabs and hydra hatchlings
      Stormwatch              safe

THE NUMBERS are the game's 50s open world (North Felwood, measured): trash basic 4L - 10, a rare's 10L - 200 at
boss multiplier 2.2. Rares sit in subzone tables at weight 0, one item from four, item level = the rare's level + 3.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_return_voyage_content import (  # noqa: E402
    CREATURES, KITS, ENCOUNTERS, kit_slug, merge_json, _detect_format, dmg, dot, debuff, buff, loot_audit)
from tools.build_tempest_openworld import enrage, stun, shield  # noqa: E402

LOOT = ROOT / "data/loot/azshara_rare_loot.json"
WEST, CENTRAL, EAST = "West Azshara", "Central Azshara", "East Azshara"


def T(level):
    return 4 * level - 10


def B(level):
    return 10 * level - 200


#: name -> (template, lo, hi, rare multiplier or None, sprite, kit shape, school, [three ability names])
ROSTER = {
    # ---------------------------------------------------------------- West Azshara
    "Autumn Timber Wolf":    ("beast_fast", 52, 56, None, "az_timber_wolf", "beast", "physical",
                              ["Bite", "Pack Lunge", "Torn Flank"]),
    "Russet Boar":           ("beast_large", 52, 54, None, "az_russet_boar", "warrior", "physical",
                              ["Tusk", "Boar Charge", "Bristle"]),
    "Cliff Hippogryph":      ("beast_fast", 53, 55, None, "az_cliff_hippogryph", "beast", "physical",
                              ["Talon Strike", "Dive", "Raking Claws"]),
    "Autumn Treant":         ("elemental_bruiser", 53, 55, None, "az_autumn_treant", "bruiser", "nature",
                              ["Branch Slam", "Leaf Storm", "Rooted"]),
    "Shadowsong Sentinel":   ("undead_warrior", 53, 55, None, "az_ghost_guard", "warrior", "shadow",
                              ["Moonglaive", "Glaive Toss", "Sentinel's Vigil"]),
    "Ravencrest Shade":      ("undead_caster", 53, 55, None, "az_ghost_noble", "caster", "shadow",
                              ["Shade Bolt", "Ten Thousand Years", "Highborne Scorn"]),
    "Haldarr Rogue":         ("humanoid_rogue", 54, 55, None, "fw_satyr_rogue", "beast", "physical",
                              ["Hooked Knife", "Backstab", "Poisoned Blade"]),
    "Haldarr Trickster":     ("humanoid_caster", 54, 55, None, "fw_satyr_trickster", "caster", "shadow",
                              ["Shadow Bolt", "Trickster's Ruse", "Curse of Haldarr"]),
    "Haldarr Felsworn":      ("humanoid_warrior", 54, 55, None, "fw_satyr_felsworn", "warrior", "fire",
                              ["Felblade", "Fel Cleave", "Sworn to the Fel"]),
    "Mere Thunderhide":      ("beast_large", 54, 55, None, "az_thunder_lizard", "bruiser", "nature",
                              ["Crushing Bite", "Thunderclap", "Static Hide"]),
    "Mere Mudclaw":          ("aquatic_basic", 53, 55, None, "az_shore_crab", "warrior", "physical",
                              ["Pinch", "Claw Sweep", "Shell Up"]),
    "Vrexx the Hornbreaker": ("humanoid_warrior", 55, 55, 2.2, "fw_satyr_hellcaller", "rare", "fire",
                              ["Hornbreaker", "Fel Stomp", "Gored", "Hellfire Rage"]),
    "Old Stormhide":         ("beast_large", 55, 55, 2.2, "az_thunder_lizard", "rare", "nature",
                              ["Stormjaw", "Thunder Stomp", "Pinned in the Mud", "Lightning Hide"]),
    # ---------------------------------------------------------------- Central Azshara
    "Leyline Prowler":       ("beast_large", 55, 57, None, "az_ley_beast", "bruiser", "arcane",
                              ["Leyline Maul", "Arcane Roar", "Mana Burn"]),
    "Legash Satyr":          ("humanoid_rogue", 55, 56, None, "az_satyr_cursed", "beast", "physical",
                              ["Hooked Blade", "Gore", "Cursed Cut"]),
    "Legash Shadowcaster":   ("humanoid_caster", 55, 56, None, "az_satyr_sorcerer", "caster", "shadow",
                              ["Shadow Bolt", "Shadow Nova", "Curse of Legash"]),
    "Legash Felhound":       ("demon_hound", 55, 56, None, "az_felhound", "beast", "fire",
                              ["Fel Bite", "Mana Snap", "Fel Burn"]),
    "Forlorn Eredar":        ("demon_caster", 56, 57, None, "az_eredar_warlock", "caster", "fire",
                              ["Fel Fireball", "Rain of Fire", "Immolate"]),
    "Forlorn Doomguard":     ("humanoid_warrior", 56, 57, None, "az_doomguard_sentinel", "bruiser", "fire",
                              ["Doom Blade", "Cleaving Strike", "War Stomp"]),
    "Forlorn Imp":           ("demon_caster", 55, 56, None, "fw_imp", "caster", "fire",
                              ["Firebolt", "Fire Shield Burst", "Scorch"]),
    "Mennar Mana Wyrm":      ("elemental_caster", 55, 56, None, "az_mana_wyrm_leader", "caster", "arcane",
                              ["Arcane Bite", "Mana Spark", "Mana Drain"]),
    "Azure Whelp":           ("beast_fast", 55, 56, None, "az_blue_whelp", "beast", "frost",
                              ["Frost Bite", "Frost Breath", "Chilled"]),
    "Azure Dragonspawn":     ("humanoid_warrior", 56, 57, None, "az_blue_dragonspawn", "bruiser", "arcane",
                              ["Leyward Glaive", "Arcane Sweep", "Warder's Stand"]),
    "Eldarath Shade":        ("undead_caster", 55, 56, None, "az_ghost_tormented", "caster", "shadow",
                              ["Wailing Bolt", "Lament", "Despair"]),
    "Eldarath Construct":    ("elemental_bruiser", 56, 57, None, "az_arcane_construct", "bruiser", "arcane",
                              ["Crystal Fist", "Arcane Pulse", "Mana Lock"]),
    "Stormbay Tidehunter":   ("humanoid_warrior", 55, 57, None, "az_naga_tidehunter", "warrior", "physical",
                              ["Trident", "Net", "Impale"]),
    "Stormbay Siren":        ("humanoid_caster", 55, 57, None, "az_naga_siren", "caster", "frost",
                              ["Frost Bolt", "Cold Wave", "Siren Song"]),
    "Stormbay Myrmidon":     ("humanoid_warrior", 56, 57, None, "az_naga_brute", "bruiser", "physical",
                              ["Stone Club", "Tail Sweep", "Barnacle Hide"]),
    "Southridge Shorecrab":  ("aquatic_basic", 54, 56, None, "az_shore_crab", "warrior", "physical",
                              ["Pinch", "Claw Sweep", "Shell Up"]),
    "Southridge Hatchling":  ("beast_fast", 55, 56, None, "az_serpent_hatchling", "beast", "nature",
                              ["Snap", "Writhe", "Venom Bite"]),
    "Warlord Seth'rak":      ("humanoid_warrior", 57, 57, 2.2, "fw_satyr_lord", "rare", "shadow",
                              ["Legash Glaive", "Warcry", "Pinned to the Throne", "Lord of Legash"]),
    "Gatekeeper Azgaroth":   ("humanoid_warrior", 57, 57, 2.2, "az_doomguard_sentinel", "rare", "fire",
                              ["Gatekeeper's Blade", "Fel Wave", "Doom", "The Gate Holds"]),
    "Azurewing":             ("beast_large", 57, 57, 2.2, "az_blue_drake", "rare", "frost",
                              ["Azure Claw", "Frost Breath", "Wing Buffet", "Leyline Shield"]),
    # ---------------------------------------------------------------- East Azshara
    "Reef Shorecrab":        ("aquatic_basic", 56, 58, None, "az_shore_crab", "warrior", "physical",
                              ["Barnacled Pinch", "Claw Sweep", "Shell Up"]),
    "Drowned Hound":         ("undead_beast", 57, 58, None, "az_ghost_hound", "beast", "shadow",
                              ["Spectral Bite", "Lunge", "Drowning Howl"]),
    "Bitter Reaches Raider": ("humanoid_warrior", 56, 57, None, "az_naga_tidehunter", "warrior", "physical",
                              ["Hooked Trident", "Net", "Plunder"]),
    "Bitter Reaches Wavecaller": ("humanoid_caster", 57, 58, None, "az_naga_sea_witch", "caster", "frost",
                                  ["Tidal Bolt", "Crashing Wave", "Brine"]),
    "Bitter Reaches Brute":  ("humanoid_warrior", 57, 58, None, "az_naga_brute", "bruiser", "physical",
                              ["Anchor Swing", "Tail Sweep", "Barnacle Hide"]),
    "Eldara Arcane Guardian": ("elemental_bruiser", 57, 58, None, "az_arcane_construct", "bruiser", "arcane",
                               ["Guardian's Fist", "Arcane Pulse", "Mana Lock"]),
    "Eldara Mana Wyrm":      ("elemental_caster", 56, 57, None, "az_mana_wyrm_leader", "caster", "arcane",
                              ["Arcane Bite", "Mana Spark", "Mana Drain"]),
    "Promenade Noble":       ("undead_caster", 57, 58, None, "az_ghost_noble", "caster", "frost",
                              ["Drowned Touch", "Courtly Disdain", "Lungful of Sea"]),
    "Promenade Handmaiden":  ("undead_caster", 57, 58, None, "az_ghost_handmaiden", "caster", "frost",
                              ["Chilling Touch", "Mourning Wail", "Courtly Curse"]),
    "Court Sentinel":        ("undead_warrior", 58, 59, None, "az_ghost_guard", "warrior", "physical",
                              ["Moonblade", "Shield Bash", "Shield Wall"]),
    "Court Tormented":       ("undead_basic", 58, 59, None, "az_ghost_tormented", "beast", "shadow",
                              ["Wailing Grasp", "Lament", "Drowned Despair"]),
    "Court Naga Guard":      ("humanoid_warrior", 58, 59, None, "az_naga_royal_guard", "warrior", "physical",
                              ["Halberd Cleave", "Shield Slam", "Hold the Line"]),
    "Zin-Malor Priestess":   ("humanoid_caster", 58, 59, None, "az_naga_sea_witch", "caster", "frost",
                              ["Tide Bolt", "Riptide", "Drown"]),
    "Zin-Malor Warden":      ("humanoid_warrior", 58, 59, None, "az_naga_royal_guard", "warrior", "physical",
                              ["Temple Halberd", "Pin", "Warden's Stand"]),
    "Zin-Malor Myrmidon":    ("humanoid_warrior", 58, 59, None, "az_naga_brute", "bruiser", "physical",
                              ["Coral Club", "Tail Sweep", "Coral Hide"]),
    "Reef Hydra Hatchling":  ("beast_fast", 57, 58, None, "az_serpent_hatchling", "beast", "nature",
                              ["Many Bites", "Writhe", "Hydra Venom"]),
    "Captain Ssarith":       ("humanoid_warrior", 58, 58, 2.2, "az_naga_royal_guard", "rare", "physical",
                              ["Wreck-Iron Trident", "Broadside", "Keelhauled", "Captain's Due"]),
    "Magus Valethion":       ("undead_caster", 58, 58, 2.2, "az_ghost_arcanist", "rare", "arcane",
                              ["Arcane Lance", "Tower's Fury", "Bound in Light", "Eldara Ward"]),
    "The Weeping Duchess":   ("undead_caster", 59, 59, 2.2, "az_ghost_handmaiden", "rare", "frost",
                              ["Tears of the Sea", "Weeping Wail", "Drowned Embrace", "Her Grief"]),
    "High Priestess Naz'eth": ("humanoid_caster", 59, 59, 2.2, "az_naga_sea_witch", "rare", "frost",
                               ["Tidal Lance", "The Temple Floods", "Drag Below", "Zin-Malor's Blessing"]),
}
RARES = {n for n, r in ROSTER.items() if r[3]}


def kit(name):
    template, lo, hi, mult, _s, shape, school, names = ROSTER[name]
    t = T(hi)
    s = school
    dispel = {"nature": "poison", "shadow": "curse"}.get(s, "magic")
    if shape == "beast":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.86), cooldown=3, school=s),
                dot(names[2], int(t * 0.27), 3, 3, school=s, **({"dispel_type": dispel} if s != "physical" else {}))]
    if shape == "warrior":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.86), cooldown=3, school=s),
                buff(names[2], 6, 3, {"armor": 220})]
    if shape == "caster":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.84), cooldown=5, school=s, is_aoe=True),
                dot(names[2], int(t * 0.27), 3, 3, school=s, dispel_type=dispel)]
    if shape == "bruiser":
        return [dmg(names[0], t + 10, school=s), dmg(names[1], int(t * 0.84), cooldown=4, school=s, is_aoe=True),
                debuff(names[2], 5, 2, {"dodge_rating": -24}, school=s)]
    # a rare: a heavy basic, a party hit, a stun with a hammer behind it, and its last stand or its ward
    b = B(hi)
    last = (shield(names[3], int(b * 1.2), school=s) if s in ("arcane", "frost") else enrage(names[3], int(b * 0.15), s))
    return [dmg(names[0], b, school=s), dmg(names[1], int(b * 0.8), cooldown=4, school=s, is_aoe=True),
            stun(names[2], int(b * 0.85), cooldown=5, school=s), dmg(f"{names[0]}, Again", int(b * 1.7), cooldown=5,
                                                                   school=s), last]


SAFE = {"name": None, "safe": True, "creatures": {}}
TABLES = {
    WEST: {
        "open_zone": {"Autumn Timber Wolf": 4, "Russet Boar": 4, "Cliff Hippogryph": 3, "Autumn Treant": 3},
        "subzones": {
            "Ursolan": {"Autumn Timber Wolf": 5, "Cliff Hippogryph": 4},
            "Shadowsong Shrine": {"Shadowsong Sentinel": 6, "Autumn Treant": 2},
            "Ravencrest Monument": {"Ravencrest Shade": 6, "Shadowsong Sentinel": 2},
            "Talrendis Point": None,
            "Haldarr Encampment": {"Haldarr Rogue": 5, "Haldarr Trickster": 4, "Haldarr Felsworn": 4,
                                   "Vrexx the Hornbreaker": 0},
            "The Sundering Mere": {"Mere Thunderhide": 5, "Mere Mudclaw": 4, "Old Stormhide": 0},
            "Valormok": None,
        },
    },
    CENTRAL: {
        "open_zone": {"Autumn Timber Wolf": 4, "Leyline Prowler": 3, "Russet Boar": 2},
        "subzones": {
            "Forlorn Ridge": {"Forlorn Eredar": 4, "Forlorn Doomguard": 4, "Forlorn Imp": 5, "Gatekeeper Azgaroth": 0},
            "Lake Mennar": {"Mennar Mana Wyrm": 5, "Azure Whelp": 4, "Azure Dragonspawn": 4, "Leyline Prowler": 3,
                            "Azurewing": 0},
            "Ruins of Eldarath": {"Eldarath Shade": 5, "Eldarath Construct": 4, "Mennar Mana Wyrm": 2},
            "Legash Encampment": {"Legash Satyr": 5, "Legash Shadowcaster": 4, "Legash Felhound": 4,
                                  "Warlord Seth'rak": 0},
            "Bay of Storms": {"Stormbay Tidehunter": 5, "Stormbay Siren": 4},
            "Hetaera's Clutch": {"Stormbay Tidehunter": 4, "Stormbay Siren": 4, "Stormbay Myrmidon": 4},
            "Southridge Beach": {"Southridge Shorecrab": 5, "Southridge Hatchling": 4},
        },
    },
    EAST: {
        "open_zone": {"Reef Shorecrab": 4, "Drowned Hound": 3, "Autumn Timber Wolf": 2},
        "subzones": {
            "Stormwatch": None,
            "The Bitter Reaches": {"Bitter Reaches Raider": 5, "Bitter Reaches Wavecaller": 4,
                                   "Bitter Reaches Brute": 4, "Captain Ssarith": 0},
            "Tower of Eldara": {"Eldara Arcane Guardian": 5, "Eldara Mana Wyrm": 5, "Magus Valethion": 0},
            "The Drowned Promenade": {"Promenade Noble": 5, "Promenade Handmaiden": 4, "Drowned Hound": 3},
            "The Drowned Court": {"Court Sentinel": 5, "Court Tormented": 4, "Court Naga Guard": 4,
                                  "The Weeping Duchess": 0},
            "Temple of Zin-Malor": {"Zin-Malor Priestess": 4, "Zin-Malor Warden": 5, "Zin-Malor Myrmidon": 4,
                                    "High Priestess Naz'eth": 0},
            "The Jagged Reef": {"Reef Shorecrab": 5, "Reef Hydra Hatchling": 4},
        },
    },
}

#: rare -> four (name, slot, suffix, (a|w, type) or None, template)
POOLS = {
    "Vrexx the Hornbreaker": [
        ("Hornbreaker's Girdle", "waist", "of the Bear", ("a", "plate"), "str_physical"),
        ("Satyr-Hide Boots", "feet", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Fel-Singed Cowl", "head", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Haldarr Fang", "main_hand", "of the Tiger", ("w", "dagger"), "agi_physical")],
    "Old Stormhide": [
        ("Stormhide Jerkin", "chest", "of the Wolf", ("a", "leather"), "agi_int_hybrid"),
        ("Thunderscale Gauntlets", "hands", "of the Prophet", ("a", "mail"), "spi_healer"),
        ("Mere-Stalker's Bracers", "wrist", "of the Gorilla", ("a", "plate"), "str_int_hybrid"),
        ("Charged Scale Pendant", "neck", "of the Sorcerer", None, "int_caster")],
    "Warlord Seth'rak": [
        ("Seth'rak's War Glaive", "main_hand", "of the Champion", ("w", "polearm"), "str_physical"),
        ("Legash Warplate Legguards", "legs", "of the Bear", ("a", "plate"), "str_physical"),
        ("Shadowcaster's Wraps", "wrist", "of the Invoker", ("a", "cloth"), "int_caster"),
        ("Satyr Lord's Cloak", "back", "of the Monkey", None, "agi_physical")],
    "Gatekeeper Azgaroth": [
        ("Gatekeeper's Pauldrons", "shoulder", "of the Gorilla", ("a", "plate"), "str_int_hybrid"),
        ("Felforged Hauberk", "chest", "of the Hunt", ("a", "mail"), "agi_physical"),
        ("Doom-Etched Wand", "ranged", "of the Sorcerer", ("w", "wand"), "int_caster"),
        ("Forlorn Ridge Treads", "feet", "of the Physician", ("a", "cloth"), "spi_healer")],
    "Azurewing": [
        ("Azure Drakescale Mantle", "shoulder", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Leyline-Woven Robe", "chest", "of the Prophet", ("a", "cloth"), "spi_healer"),
        ("Azurewing's Talon", "main_hand", "of the Sorcerer", ("w", "staff"), "int_caster"),
        ("Drakehide Leggings", "legs", "of the Tiger", ("a", "leather"), "agi_physical")],
    "Captain Ssarith": [
        ("Wreck-Iron Trident", "main_hand", "of the Hunt", ("w", "polearm"), "agi_physical"),
        ("Captain's Barnacled Helm", "head", "of the Champion", ("a", "mail"), "str_physical"),
        ("Salvaged Sea-Silk Sash", "waist", "of the Physician", ("a", "cloth"), "spi_healer"),
        ("Ssarith's Plunder Ring", "ring", "of the Tiger", None, "agi_physical")],
    "Magus Valethion": [
        ("Valethion's Spellblade", "main_hand", "of the Sorcerer", ("w", "sword_1h"), "int_caster"),
        ("Eldara Mage-Gloves", "hands", "of the Invoker", ("a", "cloth"), "int_caster"),
        ("Tower Warden's Spaulders", "shoulder", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Ward-Bound Girdle", "waist", "of the Owl", ("a", "mail"), "spi_healer")],
    "The Weeping Duchess": [
        ("Duchess's Tear", "neck", "of the Physician", None, "spi_healer"),
        ("Drowned Court Leggings", "legs", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Mourning Plate Helm", "head", "of the Bear", ("a", "plate"), "str_physical"),
        ("Courtly Grief Wraps", "wrist", "of the Wolf", ("a", "leather"), "agi_int_hybrid")],
    "High Priestess Naz'eth": [
        ("Zin-Malor Tidecaller", "main_hand", "of the Prophet", ("w", "mace_1h"), "spi_healer"),
        ("Priestess's Coral Shield", "off_hand", "of the Gorilla", ("w", "shield"), "str_int_hybrid"),
        ("Temple Scale Boots", "feet", "of the Hunt", ("a", "mail"), "agi_physical"),
        ("Naz'eth's Pearl Hood", "head", "of the Owl", ("a", "leather"), "spi_healer")],
}

#: gathering: the 50s tier, ore and herbs heavier inland, wood in the forest, and the sea on the coast
NODES = {
    "west_azshara": {"slots": 24, "active_percent": 0.42, "table": {
        "herb_golden_sansam": 3, "herb_dreamfoil": 3, "herb_blindweed": 2, "herb_sungrass": 2,
        "ore_thorium": 4, "ore_truesilver": 2, "ore_ashen_steel": 2,
        "wood_starleaf_tree": 3, "wood_moonpetal_tree": 4}},
    "central_azshara": {"slots": 24, "active_percent": 0.42, "table": {
        "herb_golden_sansam": 3, "herb_dreamfoil": 4, "herb_blindweed": 3,
        "ore_thorium": 3, "ore_ashen_steel": 3, "ore_elementium": 1, "ore_dark_iron": 2,
        "wood_starleaf_tree": 3, "wood_stormoak_tree": 2}},
    "east_azshara": {"slots": 22, "active_percent": 0.42, "table": {
        "herb_dreamfoil": 4, "herb_icecap": 2, "herb_golden_sansam": 2,
        "ore_ashen_steel": 3, "ore_elementium": 2, "ore_thorium": 2,
        "wood_stormoak_tree": 3, "wood_starleaf_tree": 2}},
}


def build_loot():
    from tools.build_durotar_content import make
    from entities.item_budget import budget_ratio, fit_to_curve
    out, rows = {}, []
    for rare, items in POOLS.items():
        ilvl = ROSTER[rare][2] + 3
        built = []
        for (name, slot, suffix, typ, template) in items:
            kw = {}
            if typ and typ[0] == "a":
                kw["armor_type"] = typ[1]
            elif typ:
                kw["weapon_type"] = typ[1]
            d = make(name, slot, suffix, ilvl, "", **kw)
            d.pop("flavor_text", None)
            d["stat_template"] = template
            d["item_id"] = "azw_" + kit_slug(name)
            r = budget_ratio(d)
            if r is not None and not 0.65 <= r <= 1.45:
                fit_to_curve(d)
            built.append(d)
            rows.append((name, slot, "weapon" if typ and typ[0] == "w" else "armor", typ[1] if typ else None,
                         template))
        out[rare] = built
    return out, rows


def check():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    from tools import handbuilt_azshara_west as W, handbuilt_azshara_central as C, handbuilt_azshara_east as E
    bad = []
    for zone, mod in ((WEST, W), (CENTRAL, C), (EAST, E)):
        declared = {s[0] for s in mod.SUBZONES}
        if set(TABLES[zone]["subzones"]) != declared:
            bad.append(f"{zone} subzones disagree with the map: {sorted(set(TABLES[zone]['subzones']) ^ declared)}")
    named = set()
    for t in TABLES.values():
        named |= set(t["open_zone"])
        if RARES & set(t["open_zone"]):
            bad.append("a rare is in an open-zone table")
        for s in t["subzones"].values():
            named |= set(s or {})
    if named != set(ROSTER) or set(POOLS) != RARES:
        bad.append(f"tables, roster and pools differ: {sorted(named ^ set(ROSTER))} {sorted(set(POOLS) ^ RARES)}")
    existing = json.loads(CREATURES.read_text(encoding="utf-8"))["creatures"]
    for name, r in ROSTER.items():
        if not (ROOT / "assets/creatures" / f"{r[4]}.png").exists():
            bad.append(f"{name}'s sprite {r[4]} is not on disk")
        prev = existing.get(name)
        if prev and prev.get("ability_kit") != kit_slug(name):
            bad.append(f"{name} is already a different creature in creatures.json")
    import creature_sprites as CS
    for name, r in ROSTER.items():
        if CS.sprite_for(name, r[0]) != r[4]:
            bad.append(f"creature_sprites.py draws {name} as {CS.sprite_for(name, r[0])}, not {r[4]}")
    return bad


def main():
    bad = check()
    loot, rows = build_loot()
    bad += loot_audit(rows)
    if bad:
        print("FAILED - fix the data, not the check:")
        for b in bad:
            print("  -", b)
        return 1
    creatures = {}
    for name, (template, lo, hi, mult, *_rest) in ROSTER.items():
        e = {"template": template, "level_range": [lo, hi], "is_boss": bool(mult), "ability_kit": kit_slug(name)}
        if mult:
            e["boss_multiplier"] = mult
        creatures[name] = e
    merge_json(CREATURES, "creatures", creatures, "creatures.json")
    merge_json(KITS, "kits", {kit_slug(n): kit(n) for n in ROSTER}, "ability_kits.json")

    raw = ENCOUNTERS.read_text(encoding="utf-8")
    enc = json.loads(raw)
    indent, newline = _detect_format(json.loads(raw), raw)
    for zone, table in TABLES.items():
        entry = enc["zones"].setdefault(zone, {})
        entry["name"] = zone
        entry["open_zone"] = {"name": zone, "creatures": dict(table["open_zone"])}
        entry["subzones"] = {s: ({"name": s, "safe": True, "creatures": {}} if c is None else
                                 {"name": s, "creatures": dict(c)}) for s, c in table["subzones"].items()}
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False) + ("\n" if newline else ""),
                          encoding="utf-8")
    np_path = ROOT / "data/gathering/node_pools.json"
    nd = json.loads(np_path.read_text(encoding="utf-8"))
    fish = (nd["zones"].get("north_felwood") or {}).get("fishing")
    for key, pool in NODES.items():
        nd["zones"][key] = dict(pool, **({"fishing": fish} if fish else {}))
    np_path.write_text(json.dumps(nd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = {"_notes": ("Azshara's open-world rares (52-59). ONE item per kill from the rare's four; item_level = the "
                      "rare's level + 3. Hand-authored in tools/build_azshara_openworld.py.")}
    out.update(loot)
    LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True, stdout=subprocess.DEVNULL)
    print(f"{len(ROSTER)} creatures ({len(RARES)} rares) over {len(TABLES)} maps; {len(rows)} rare items; "
          f"gathering on {', '.join(NODES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
