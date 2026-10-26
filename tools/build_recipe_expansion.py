"""
Massive recipe expansion (Oct 2026).

Design goals:
  - ~60% trainer source (baseline gear progression, every skill bracket)
  - ~40% open world drop / dungeon drop / vendor (tied to real zones/dungeons from world_level_table)
  - Every armor type (cloth, leather, mail, plate) covers ALL stat archetypes worn by that type
  - Every weapon type has representations across relevant stat templates
  - Professions:
      Blacksmithing  = mail + plate  (new: INT/STR plate, INT mail, AGI/INT mail, STR/INT mail)
      Leatherworking = leather + mail (new: STR leather, INT leather, AGI/INT leather, INT mail, STR/INT mail)
      Tailoring      = cloth (new: AGI/INT cloth, STR cloth, STR/INT cloth)
      Alchemy        = potions/elixirs — expand consumable breadth
      Woodworking    = bows/staves/wands/polearms — stat breadth for ranged/caster classes

Stat templates in use:
  str_physical      Warriors, Guardians, Barbarians
  agi_physical      Rogues, Hunters, Rangers
  int_caster        Mages, Warlocks, Priests, Druids, Shamans (elemental)
  spi_healer        Priests (holy), Druids (resto), Shamans (resto), Paladins (holy)
  str_int_hybrid    Paladins, Cultists, Sun Clerics, Knight of Xoroth, Starcaller, Primalist
  agi_int_hybrid    Tinkers, Witch Doctors, Felsworn, Bloodmages

Armor-class to stat mapping:
  Cloth  → int_caster, spi_healer, agi_int_hybrid (Bloodmage/Felsworn)
  Leather→ agi_physical, str_physical, int_caster, agi_int_hybrid, str_int_hybrid
  Mail   → agi_physical, int_caster, str_int_hybrid, agi_int_hybrid
  Plate  → str_physical, str_int_hybrid, spi_healer (Paladin healer)

Drop location assignment (real dungeons from world_level_table.md):
  Level 5-10  : Valley of Trials, Durotar open world
  Level 10-15 : Echo Isles, Ragefire Chasm, Burning Blade Coven
  Level 15-20 : Widow's Lair, Night Web's Hollow, Scarlet Crypt
  Level 20-25 : Shadowfang Keep, Ambermill Tower, Shadowpine Altar
  Level 25-30 : Razorfen Kraul, Broodspiral, Grom's Rest
  Level 28-35 : Plague Depths, Wailing Caverns, Blackfathom Deeps

Vendor assignments:
  Razor Hill, The Crossroads, Orgrimmar, Camp Taurajo, Astranaar,
  Splintertree Post, Ratchet, Silverpine (The Sepulcher), Undercity,
  Hidden vendor (Zoram Strand, Razorfen approach, Fenris Isle)
"""

import json
from pathlib import Path

REPO = Path(__file__).parent.parent

def sr(req):
    """skill_range list from skill_required."""
    return [req + 5, req + 15, req + 25, req + 35]

# ── Material tier mapping (skill_required → material_tier name)
# These match the upgrade kit tiers already in the system.
BS_MATERIAL_TIERS = {
    # copper = req 0-100, bronze = 101-200, iron = 201-300
    range(0, 101): ("copper", "bar_copper"),
    range(101, 201): ("bronze", "bar_bronze"),
    range(201, 301): ("iron", "bar_iron"),
}

LW_MATERIAL_TIERS = {
    range(0, 21): ("scrap_leather", "leather_scrap"),
    range(21, 75): ("light_leather", "leather_light"),
    range(75, 150): ("medium_leather", "leather_medium"),
    range(150, 210): ("heavy_leather", "leather_heavy"),
    range(210, 280): ("thick_leather", "leather_thick"),
    range(280, 301): ("rugged_leather", "leather_rugged"),
}

def bs_mat(req):
    for r, (tier, mat) in BS_MATERIAL_TIERS.items():
        if req in r:
            return tier, mat
    return "iron", "bar_iron"

def lw_mat(req):
    for r, (tier, mat) in LW_MATERIAL_TIERS.items():
        if req in r:
            return tier, mat
    return "rugged_leather", "leather_rugged"

def ilvl(req):
    """item_level from skill_required (WoW-style linear, skill 300 = ilvl 60)."""
    return max(1, int(req * 60 / 300) + 1)

def bs_inputs(req, qty_main, qty_secondary=0, secondary_mat=None):
    _, mat = bs_mat(req)
    inp = {mat: qty_main}
    if qty_secondary and secondary_mat:
        inp[secondary_mat] = qty_secondary
    return inp

def lw_inputs(req, qty_main, qty_secondary=0, secondary_mat=None):
    _, mat = lw_mat(req)
    inp = {mat: qty_main}
    if qty_secondary and secondary_mat:
        inp[secondary_mat] = qty_secondary
    return inp

def bs_recipe(name, req, slot, armor_type, stat_template, rarity, source,
              inputs=None, drop_zone=None, vendor_location=None):
    tier, _ = bs_mat(req)
    r = {
        "name": name,
        "skill_required": req,
        "skill_range": sr(req),
        "source": source,
        "inputs": inputs or bs_inputs(req, 6 if rarity == "common" else 10),
        "output": {
            "kind": "armor",
            "slot": slot,
            "armor_type": armor_type,
            "stat_template": stat_template,
            "item_level": ilvl(req),
            "rarity": rarity,
            "material_tier": tier,
        }
    }
    if drop_zone: r["drop_zone"] = drop_zone
    if vendor_location: r["vendor_location"] = vendor_location
    return r

def bs_weapon(name, req, slot, weapon_type, stat_template, rarity, source,
              inputs=None, drop_zone=None, vendor_location=None):
    tier, _ = bs_mat(req)
    r = {
        "name": name,
        "skill_required": req,
        "skill_range": sr(req),
        "source": source,
        "inputs": inputs or bs_inputs(req, 8 if rarity == "common" else 14),
        "output": {
            "kind": "weapon",
            "slot": slot,
            "weapon_type": weapon_type,
            "stat_template": stat_template,
            "item_level": ilvl(req),
            "rarity": rarity,
            "material_tier": tier,
        }
    }
    if drop_zone: r["drop_zone"] = drop_zone
    if vendor_location: r["vendor_location"] = vendor_location
    return r

def lw_recipe(name, req, slot, armor_type, stat_template, rarity, source,
              inputs=None, drop_zone=None, vendor_location=None):
    tier, _ = lw_mat(req)
    r = {
        "name": name,
        "skill_required": req,
        "skill_range": sr(req),
        "source": source,
        "inputs": inputs or lw_inputs(req, 4 if rarity == "common" else 8),
        "output": {
            "kind": "armor",
            "slot": slot,
            "armor_type": armor_type,
            "stat_template": stat_template,
            "item_level": ilvl(req),
            "rarity": rarity,
            "material_tier": tier,
        }
    }
    if drop_zone: r["drop_zone"] = drop_zone
    if vendor_location: r["vendor_location"] = vendor_location
    return r

# ════════════════════════════════════════════════════════════════════════════
# BLACKSMITHING
# ════════════════════════════════════════════════════════════════════════════
# Current: 7 trainer + 2 drop + 1 vendor = 10 total (very thin)
# Target:  ~50 trainer + ~35 drop/vendor = ~85 total

NEW_BS_RECIPES = {

    # ── COPPER TIER (skill 0-100) ── trainer baseline ──────────────────────

    # mail - agi_physical (Hunter/Ranger/Rogue — already have bracers/vest/belt)
    "bs_copper_chain_gloves":       bs_recipe("Copper Chain Gloves",      5,  "hands",    "mail",  "agi_physical",  "common",   "trainer", bs_inputs(5, 4)),
    "bs_copper_chain_boots":        bs_recipe("Copper Chain Boots",       18, "feet",     "mail",  "agi_physical",  "common",   "trainer", bs_inputs(18, 5)),
    "bs_copper_chain_coif":         bs_recipe("Copper Chain Coif",        25, "head",     "mail",  "agi_physical",  "common",   "trainer", bs_inputs(25, 5)),
    "bs_copper_chain_spaulders":    bs_recipe("Copper Chain Spaulders",   45, "shoulders","mail",  "agi_physical",  "common",   "trainer", bs_inputs(45, 6)),
    "bs_copper_chain_leggings":     bs_recipe("Copper Chain Leggings",    55, "legs",     "mail",  "agi_physical",  "common",   "trainer", bs_inputs(55, 8)),
    "bs_copper_scale_bracers":      bs_recipe("Copper Scale Bracers",     65, "wrist",    "mail",  "agi_physical",  "uncommon", "trainer", bs_inputs(65, 8)),
    "bs_copper_scale_helm":         bs_recipe("Copper Scale Helm",        80, "head",     "mail",  "agi_physical",  "uncommon", "trainer", bs_inputs(80, 10)),

    # mail - int_caster (Shaman elemental — need trainer baseline)
    "bs_copper_spellchain_belt":    bs_recipe("Copper Spellchain Belt",   10, "waist",    "mail",  "int_caster",    "common",   "trainer", bs_inputs(10, 4)),
    "bs_copper_spellchain_boots":   bs_recipe("Copper Spellchain Boots",  20, "feet",     "mail",  "int_caster",    "common",   "trainer", bs_inputs(20, 5)),
    "bs_copper_runic_bracers":      bs_recipe("Copper Runic Bracers",     40, "wrist",    "mail",  "int_caster",    "common",   "trainer", bs_inputs(40, 6)),
    "bs_copper_runic_coif":         bs_recipe("Copper Runic Coif",        60, "head",     "mail",  "int_caster",    "common",   "trainer", bs_inputs(60, 8)),
    "bs_copper_runic_leggings":     bs_recipe("Copper Runic Leggings",    75, "legs",     "mail",  "int_caster",    "uncommon", "trainer", bs_inputs(75, 10)),

    # mail - str_int_hybrid (Primalist/Starcaller)
    "bs_copper_warden_gloves":      bs_recipe("Copper Warden Gloves",     30, "hands",    "mail",  "str_int_hybrid","common",   "trainer", bs_inputs(30, 5)),
    "bs_copper_warden_leggings":    bs_recipe("Copper Warden Leggings",   70, "legs",     "mail",  "str_int_hybrid","uncommon", "trainer", bs_inputs(70, 9)),

    # plate - str_physical (Warrior/Guardian — trainer baseline)
    "bs_bronze_plate_belt":         bs_recipe("Bronze Plate Belt",       102, "waist",    "plate", "str_physical",  "common",   "trainer", bs_inputs(102, 8)),
    "bs_bronze_plate_gloves":       bs_recipe("Bronze Plate Gloves",     106, "hands",    "plate", "str_physical",  "common",   "trainer", bs_inputs(106, 8)),
    "bs_bronze_plate_helm":         bs_recipe("Bronze Plate Helm",       112, "head",     "plate", "str_physical",  "uncommon", "trainer", bs_inputs(112, 12)),
    "bs_bronze_plate_spaulders":    bs_recipe("Bronze Plate Spaulders",  118, "shoulders","plate", "str_physical",  "uncommon", "trainer", bs_inputs(118, 12)),
    "bs_bronze_plate_boots":        bs_recipe("Bronze Plate Boots",      122, "feet",     "plate", "str_physical",  "uncommon", "trainer", bs_inputs(122, 10)),
    "bs_bronze_plate_bracers":      bs_recipe("Bronze Plate Bracers",    125, "wrist",    "plate", "str_physical",  "uncommon", "trainer", bs_inputs(125, 8)),

    # plate - str_int_hybrid (Paladin/Cultist — trainer baseline)
    "bs_bronze_crusader_belt":      bs_recipe("Bronze Crusader Belt",    110, "waist",    "plate", "str_int_hybrid","common",   "trainer", bs_inputs(110, 8)),
    "bs_bronze_crusader_gloves":    bs_recipe("Bronze Crusader Gloves",  114, "hands",    "plate", "str_int_hybrid","common",   "trainer", bs_inputs(114, 8)),
    "bs_bronze_crusader_helm":      bs_recipe("Bronze Crusader Helm",    120, "head",     "plate", "str_int_hybrid","uncommon", "trainer", bs_inputs(120, 12)),
    "bs_bronze_crusader_spaulders": bs_recipe("Bronze Crusader Spaulders",126,"shoulders","plate","str_int_hybrid","uncommon", "trainer", bs_inputs(126, 12)),
    "bs_bronze_crusader_boots":     bs_recipe("Bronze Crusader Boots",   130, "feet",     "plate", "str_int_hybrid","uncommon", "trainer", bs_inputs(130, 10)),

    # plate - spi_healer (Paladin holy/Sun Cleric — trainer baseline)
    "bs_bronze_chaplain_helm":      bs_recipe("Bronze Chaplain Helm",    116, "head",     "plate", "spi_healer",    "common",   "trainer", bs_inputs(116, 10)),
    "bs_bronze_chaplain_gloves":    bs_recipe("Bronze Chaplain Gloves",  124, "hands",    "plate", "spi_healer",    "common",   "trainer", bs_inputs(124, 8)),

    # IRON TIER (skill 150-300) — trainer baseline ────────────────────────
    "bs_iron_plate_belt":           bs_recipe("Iron Plate Belt",         155, "waist",    "plate", "str_physical",  "uncommon", "trainer", bs_inputs(155, 10)),
    "bs_iron_plate_boots":          bs_recipe("Iron Plate Boots",        160, "feet",     "plate", "str_physical",  "uncommon", "trainer", bs_inputs(160, 10)),
    "bs_iron_plate_gloves":         bs_recipe("Iron Plate Gloves",       165, "hands",    "plate", "str_physical",  "uncommon", "trainer", bs_inputs(165, 10)),
    "bs_iron_plate_leggings":       bs_recipe("Iron Plate Leggings",     170, "legs",     "plate", "str_physical",  "uncommon", "trainer", bs_inputs(170, 14)),
    "bs_iron_plate_helm":           bs_recipe("Iron Plate Helm",         175, "head",     "plate", "str_physical",  "uncommon", "trainer", bs_inputs(175, 12)),
    "bs_iron_plate_spaulders":      bs_recipe("Iron Plate Spaulders",    180, "shoulders","plate", "str_physical",  "uncommon", "trainer", bs_inputs(180, 12)),
    "bs_iron_plate_cuirass":        bs_recipe("Iron Plate Cuirass",      185, "chest",    "plate", "str_physical",  "uncommon", "trainer", bs_inputs(185, 16)),
    "bs_iron_plate_bracers":        bs_recipe("Iron Plate Bracers",      165, "wrist",    "plate", "str_physical",  "uncommon", "trainer", bs_inputs(165, 8)),

    "bs_iron_crusader_leggings":    bs_recipe("Iron Crusader Leggings",  162, "legs",     "plate", "str_int_hybrid","uncommon", "trainer", bs_inputs(162, 14)),
    "bs_iron_crusader_cuirass":     bs_recipe("Iron Crusader Cuirass",   190, "chest",    "plate", "str_int_hybrid","uncommon", "trainer", bs_inputs(190, 16)),
    "bs_iron_crusader_helm":        bs_recipe("Iron Crusader Helm",      195, "head",     "plate", "str_int_hybrid","uncommon", "trainer", bs_inputs(195, 12)),
    "bs_iron_crusader_bracers":     bs_recipe("Iron Crusader Bracers",   168, "wrist",    "plate", "str_int_hybrid","uncommon", "trainer", bs_inputs(168, 8)),

    "bs_iron_mail_belt":            bs_recipe("Iron Scale Belt",         152, "waist",    "mail",  "agi_physical",  "uncommon", "trainer", bs_inputs(152, 8)),
    "bs_iron_mail_boots":           bs_recipe("Iron Scale Boots",        157, "feet",     "mail",  "agi_physical",  "uncommon", "trainer", bs_inputs(157, 8)),
    "bs_iron_mail_gloves":          bs_recipe("Iron Scale Gloves",       163, "hands",    "mail",  "agi_physical",  "uncommon", "trainer", bs_inputs(163, 8)),
    "bs_iron_mail_leggings":        bs_recipe("Iron Scale Leggings",     172, "legs",     "mail",  "agi_physical",  "uncommon", "trainer", bs_inputs(172, 12)),
    "bs_iron_mail_helm":            bs_recipe("Iron Scale Helm",         178, "head",     "mail",  "agi_physical",  "uncommon", "trainer", bs_inputs(178, 10)),
    "bs_iron_mail_cuirass":         bs_recipe("Iron Scale Cuirass",      188, "chest",    "mail",  "agi_physical",  "uncommon", "trainer", bs_inputs(188, 14)),

    "bs_iron_runic_leggings":       bs_recipe("Iron Runic Leggings",     158, "legs",     "mail",  "int_caster",    "uncommon", "trainer", bs_inputs(158, 12)),
    "bs_iron_runic_cuirass":        bs_recipe("Iron Runic Cuirass",      182, "chest",    "mail",  "int_caster",    "uncommon", "trainer", bs_inputs(182, 14)),

    # Weapons — trainer baseline
    "bs_copper_sword":              bs_weapon("Copper Shortsword",        5,  "main_hand","sword",  "str_physical",  "common",   "trainer", bs_inputs(5, 5)),
    "bs_copper_axe":                bs_weapon("Copper Hand Axe",          15, "main_hand","axe",    "str_physical",  "common",   "trainer", bs_inputs(15, 5)),
    "bs_copper_mace":               bs_weapon("Copper Mace",              25, "main_hand","mace",   "str_physical",  "common",   "trainer", bs_inputs(25, 5)),
    "bs_copper_shield":             bs_weapon("Copper Shield",            10, "off_hand", "shield", "str_physical",  "common",   "trainer", bs_inputs(10, 6)),
    "bs_bronze_longsword":          bs_weapon("Bronze Longsword",        103, "main_hand","sword",  "str_physical",  "common",   "trainer", bs_inputs(103, 8)),
    "bs_bronze_battle_axe":         bs_weapon("Bronze Battle Axe",       107, "main_hand","axe",    "str_physical",  "common",   "trainer", bs_inputs(107, 8)),
    "bs_bronze_warhammer":          bs_weapon("Bronze Warhammer",        113, "main_hand","mace",   "str_int_hybrid","common",   "trainer", bs_inputs(113, 9)),
    "bs_bronze_shield":             bs_weapon("Bronze Heater Shield",    108, "off_hand", "shield", "str_physical",  "common",   "trainer", bs_inputs(108, 8)),
    "bs_bronze_2h_sword":           bs_weapon("Bronze Greatsword",       119, "two_hand", "sword",  "str_physical",  "uncommon", "trainer", bs_inputs(119, 14)),
    "bs_bronze_2h_axe":             bs_weapon("Bronze Great Axe",        127, "two_hand", "axe",    "str_physical",  "uncommon", "trainer", bs_inputs(127, 14)),
    "bs_iron_sword":                bs_weapon("Iron Longsword",          155, "main_hand","sword",  "str_physical",  "uncommon", "trainer", bs_inputs(155, 10)),
    "bs_iron_axe":                  bs_weapon("Iron Battle Axe",         162, "main_hand","axe",    "str_physical",  "uncommon", "trainer", bs_inputs(162, 10)),
    "bs_iron_mace":                 bs_weapon("Iron Warhammer",          168, "main_hand","mace",   "str_int_hybrid","uncommon", "trainer", bs_inputs(168, 10)),
    "bs_iron_shield":               bs_weapon("Iron Tower Shield",       170, "off_hand", "shield", "str_physical",  "uncommon", "trainer", bs_inputs(170, 10)),
    "bs_iron_2h_sword":             bs_weapon("Iron Claymore",           176, "two_hand", "sword",  "str_physical",  "uncommon", "trainer", bs_inputs(176, 16)),
    "bs_iron_2h_polearm":           bs_weapon("Iron Halberd",            183, "two_hand", "polearm","str_int_hybrid","uncommon", "trainer", bs_inputs(183, 14)),

    # Upgrade kits — trainer
    "bs_upgrade_kit_iron":   {
        "name": "Iron Upgrade Kit", "skill_required": 170, "skill_range": sr(170),
        "source": "trainer",
        "inputs": {"bar_iron": 4},
        "output": {"kind": "material", "material_id": "lw_kit_iron"},
    },

    # ── WORLD DROP / DUNGEON DROP ──────────────────────────────────────────

    # Ragefire Chasm drops (lvl 15-17)
    "bs_smelted_plate_gauntlets":   bs_recipe("Smelted Plate Gauntlets",  115, "hands",   "plate", "str_physical",  "uncommon", "drop",   bs_inputs(115, 12), drop_zone="Ragefire Chasm"),
    "bs_forgeborn_spaulders":       bs_recipe("Forgeborn Spaulders",      118, "shoulders","plate","str_physical",  "uncommon", "drop",   bs_inputs(118, 14), drop_zone="Ragefire Chasm"),

    # Shadowfang Keep drops (lvl 21-25)
    "bs_silverfang_greaves":        bs_recipe("Silverfang Greaves",       150, "legs",     "plate", "str_int_hybrid","uncommon", "drop",   bs_inputs(150, 14), drop_zone="Shadowfang Keep"),
    "bs_duskplate_cuirass":         bs_recipe("Duskplate Cuirass",        155, "chest",    "plate", "str_int_hybrid","rare",     "drop",   bs_inputs(155, 18), drop_zone="Shadowfang Keep"),
    "bs_moonhowl_mail_vest":        bs_recipe("Moonhowl Mail Vest",       148, "chest",    "mail",  "int_caster",    "uncommon", "drop",   bs_inputs(148, 12), drop_zone="Shadowfang Keep"),

    # Widow's Lair / Silverpine drops (lvl 17-19)
    "bs_carapace_mail_gloves":      bs_recipe("Carapace Mail Gloves",     130, "hands",    "mail",  "agi_int_hybrid","uncommon", "drop",   bs_inputs(130, 10), drop_zone="Widow's Lair"),
    "bs_venomed_scale_bracers":     bs_recipe("Venomed Scale Bracers",    132, "wrist",    "mail",  "agi_int_hybrid","uncommon", "drop",   bs_inputs(132, 8),  drop_zone="Widow's Lair"),

    # Plague Depths / Undercity drops (lvl 30-34)
    "bs_plague_iron_helm":          bs_recipe("Plagued Iron Helm",        210, "head",     "plate", "str_physical",  "rare",     "drop",   bs_inputs(210, 16), drop_zone="Plague Depths"),
    "bs_putrid_mail_cuirass":       bs_recipe("Putrid Mail Cuirass",      205, "chest",    "mail",  "int_caster",    "rare",     "drop",   bs_inputs(205, 14), drop_zone="Plague Depths"),
    "bs_rotboned_shield":           bs_weapon("Rotboned Bulwark",         208, "off_hand", "shield","str_int_hybrid","rare",     "drop",   bs_inputs(208, 12), drop_zone="Plague Depths"),

    # Wailing Caverns drops (lvl 16-24)
    "bs_thornscale_mail_spaulders": bs_recipe("Thornscale Spaulders",    138, "shoulders","mail",  "agi_physical",  "uncommon", "drop",   bs_inputs(138, 10), drop_zone="Wailing Caverns"),
    "bs_serpentscale_bracers":      bs_recipe("Serpentscale Bracers",    140, "wrist",    "mail",  "agi_int_hybrid","uncommon", "drop",   bs_inputs(140, 8),  drop_zone="Wailing Caverns"),
    "bs_fangplate_gloves":          bs_recipe("Fangplate Gauntlets",     145, "hands",    "plate", "str_int_hybrid","uncommon", "drop",   bs_inputs(145, 10), drop_zone="Wailing Caverns"),

    # Razorfen Kraul drops (lvl 25-34)
    "bs_boarplate_cuirass":         bs_recipe("Boarplate Cuirass",       180, "chest",    "plate", "str_physical",  "rare",     "drop",   bs_inputs(180, 18), drop_zone="Razorfen Kraul"),
    "bs_razortusk_2h_axe":          bs_weapon("Razortusk Cleaver",       185, "two_hand", "axe",   "str_physical",  "rare",     "drop",   bs_inputs(185, 20), drop_zone="Razorfen Kraul"),
    "bs_blademark_mail_helm":       bs_recipe("Blademark Mail Helm",     175, "head",     "mail",  "agi_physical",  "uncommon", "drop",   bs_inputs(175, 12), drop_zone="Razorfen Kraul"),

    # Blackfathom Deeps drops (lvl 24-27)
    "bs_deepsea_mail_vest":         bs_recipe("Deepsea Mail Vest",       165, "chest",    "mail",  "int_caster",    "rare",     "drop",   bs_inputs(165, 14), drop_zone="Blackfathom Deeps"),
    "bs_tideguard_shield":          bs_weapon("Tideguard Bulwark",       168, "off_hand", "shield","spi_healer",    "uncommon", "drop",   bs_inputs(168, 10), drop_zone="Blackfathom Deeps"),

    # Ambermill Tower / Silverpine drops (lvl 21-23)
    "bs_arcane_plate_bracers":      bs_recipe("Arcane Plate Bracers",    148, "wrist",    "plate", "spi_healer",    "uncommon", "drop",   bs_inputs(148, 8),  drop_zone="Ambermill Tower"),
    "bs_stormblessed_mail_helm":    bs_recipe("Stormblessed Coif",       143, "head",     "mail",  "str_int_hybrid","uncommon", "drop",   bs_inputs(143, 10), drop_zone="Ambermill Tower"),

    # Echo Isles / low-level drops
    "bs_saltcrusted_mail_gloves":   bs_recipe("Saltcrusted Mail Gloves",  52, "hands",    "mail",  "agi_int_hybrid","common",   "drop",   bs_inputs(52, 6),   drop_zone="Echo Isles"),
    "bs_troll_bronze_axe":          bs_weapon("Troll-Wrought Axe",        50, "main_hand","axe",   "agi_physical",  "uncommon", "drop",   bs_inputs(50, 6),   drop_zone="Echo Isles"),

    # Grom's Rest drops (lvl 26-32)
    "bs_demonshard_mail_bracers":   bs_recipe("Demonshard Mail Bracers",  188, "wrist",   "mail",  "agi_int_hybrid","rare",     "drop",   bs_inputs(188, 10), drop_zone="Grom's Rest"),
    "bs_felhewn_plate_helm":        bs_recipe("Felhewn Plate Helm",       192, "head",    "plate", "str_int_hybrid","rare",     "drop",   bs_inputs(192, 14), drop_zone="Grom's Rest"),
    "bs_accursed_2h_sword":         bs_weapon("Accursed Greatsword",      195, "two_hand","sword", "str_int_hybrid","rare",     "drop",   bs_inputs(195, 20), drop_zone="Grom's Rest"),

    # ── VENDOR RECIPES ────────────────────────────────────────────────────
    # Orgrimmar vendor (warsong-themed, aggressive AGI warrior items)
    "bs_warsong_mail_helm":         bs_recipe("Warsong Chain Coif",        90, "head",    "mail",  "agi_physical",  "uncommon", "vendor", bs_inputs(90, 10),  vendor_location="Orgrimmar"),
    "bs_warsong_plate_spaulders":   bs_recipe("Warsong Plate Spaulders",  128, "shoulders","plate","str_physical",  "uncommon", "vendor", bs_inputs(128, 12), vendor_location="Orgrimmar"),

    # Crossroads vendor (crossroads-themed, open plains hunter/shaman)
    "bs_plains_scale_vest":         bs_recipe("Plains Scale Vest",         85, "chest",   "mail",  "str_int_hybrid","uncommon", "vendor", bs_inputs(85, 12),  vendor_location="The Crossroads"),
    "bs_thunderfist_gauntlets":     bs_recipe("Thunderfist Gauntlets",    135, "hands",   "plate", "str_int_hybrid","uncommon", "vendor", bs_inputs(135, 10), vendor_location="The Crossroads"),
    "bs_stonemace":                 bs_weapon("Stonemace",                 95, "main_hand","mace", "str_int_hybrid","uncommon", "vendor", bs_inputs(95, 8),   vendor_location="The Crossroads"),

    # Sepulcher / Silverpine vendor (undead gothic flavour)
    "bs_bonegraft_mail_spaulders":  bs_recipe("Bonegraft Mail Spaulders", 132, "shoulders","mail", "int_caster",    "uncommon", "vendor", bs_inputs(132, 10), vendor_location="The Sepulcher"),
    "bs_shroudsteel_helm":          bs_recipe("Shroudsteel Helm",         138, "head",     "plate","spi_healer",    "uncommon", "vendor", bs_inputs(138, 10), vendor_location="The Sepulcher"),

    # Undercity vendor (apothecary-themed arcane plate / mail)
    "bs_runeplate_cuirass":         bs_recipe("Runeplate Cuirass",        200, "chest",   "plate", "str_int_hybrid","rare",     "vendor", bs_inputs(200, 18), vendor_location="Undercity"),
    "bs_runescale_leggings":        bs_recipe("Runescale Leggings",       198, "legs",    "mail",  "int_caster",    "rare",     "vendor", bs_inputs(198, 14), vendor_location="Undercity"),

    # Camp Taurajo vendor (Barrens — tauren themed mail)
    "bs_stonehoof_mail_boots":      bs_recipe("Stonehoof Mail Boots",     105, "feet",    "mail",  "str_int_hybrid","common",   "vendor", bs_inputs(105, 8),  vendor_location="Camp Taurajo"),
    "bs_earthshaker_mace":          bs_weapon("Earthshaker Mace",         112, "main_hand","mace", "str_int_hybrid","uncommon", "vendor", bs_inputs(112, 10), vendor_location="Camp Taurajo"),

    # Hidden vendor Zoram Strand (coastal, hard to find)
    "bs_naga_scale_vest":           bs_recipe("Naga Scale Vest",          160, "chest",   "mail",  "int_caster",    "rare",     "vendor", bs_inputs(160, 14), vendor_location="Zoram Strand (hidden)"),
    "bs_tidesurge_shield":          bs_weapon("Tidesurge Bulwark",        162, "off_hand","shield","spi_healer",    "rare",     "vendor", bs_inputs(162, 10), vendor_location="Zoram Strand (hidden)"),
}


# ════════════════════════════════════════════════════════════════════════════
# LEATHERWORKING
# ════════════════════════════════════════════════════════════════════════════
# Current: 56 trainer + 2 drop + 1 vendor = 59 total (all agi_physical!)
# Target: ~85 trainer + ~55 drop/vendor covering ALL stat templates

NEW_LW_RECIPES = {
    # ── SCRAP LEATHER TIER (0-20) — trainer ──────────────────────────────
    "lw_scrap_str_boots":           lw_recipe("Scrapbound Boots",          2,  "feet",    "leather","str_physical",  "common",   "trainer", lw_inputs(2, 2)),
    "lw_scrap_int_gloves":          lw_recipe("Tattered Spirit Gloves",    8,  "hands",   "leather","int_caster",    "common",   "trainer", lw_inputs(8, 2)),

    # ── LIGHT LEATHER TIER (21-74) — trainer ─────────────────────────────
    # STR leather (Barbarian)
    "lw_light_str_gloves":          lw_recipe("Light Leather Gauntlets",   22, "hands",   "leather","str_physical",  "common",   "trainer", lw_inputs(22, 3)),
    "lw_light_str_bracers":         lw_recipe("Roughhide Bracers",         28, "wrist",   "leather","str_physical",  "common",   "trainer", lw_inputs(28, 3)),
    "lw_light_str_boots":           lw_recipe("Roughhide Boots",           32, "feet",    "leather","str_physical",  "common",   "trainer", lw_inputs(32, 3)),
    "lw_light_str_helm":            lw_recipe("Roughhide Helm",            45, "head",    "leather","str_physical",  "common",   "trainer", lw_inputs(45, 5)),
    "lw_light_str_leggings":        lw_recipe("Roughhide Leggings",        55, "legs",    "leather","str_physical",  "common",   "trainer", lw_inputs(55, 6)),
    "lw_light_str_vest":            lw_recipe("Roughhide Vest",            65, "chest",   "leather","str_physical",  "uncommon", "trainer", lw_inputs(65, 8)),

    # INT leather (Druid, Bloodmage)
    "lw_light_int_gloves":          lw_recipe("Spirithide Gloves",         24, "hands",   "leather","int_caster",    "common",   "trainer", lw_inputs(24, 3)),
    "lw_light_int_belt":            lw_recipe("Spirithide Belt",           26, "waist",   "leather","int_caster",    "common",   "trainer", lw_inputs(26, 3)),
    "lw_light_int_boots":           lw_recipe("Spirithide Boots",          34, "feet",    "leather","int_caster",    "common",   "trainer", lw_inputs(34, 4)),
    "lw_light_int_bracers":         lw_recipe("Spirithide Bracers",        38, "wrist",   "leather","int_caster",    "common",   "trainer", lw_inputs(38, 3)),
    "lw_light_int_helm":            lw_recipe("Spirithide Helm",           48, "head",    "leather","int_caster",    "common",   "trainer", lw_inputs(48, 5)),
    "lw_light_int_leggings":        lw_recipe("Spirithide Leggings",       58, "legs",    "leather","int_caster",    "common",   "trainer", lw_inputs(58, 6)),
    "lw_light_int_vest":            lw_recipe("Spirithide Vest",           68, "chest",   "leather","int_caster",    "uncommon", "trainer", lw_inputs(68, 8)),

    # AGI/INT hybrid leather (Witch Doctor, Felsworn)
    "lw_light_agint_bracers":       lw_recipe("Hexhide Bracers",           30, "wrist",   "leather","agi_int_hybrid","common",   "trainer", lw_inputs(30, 3)),
    "lw_light_agint_belt":          lw_recipe("Hexhide Belt",              42, "waist",   "leather","agi_int_hybrid","common",   "trainer", lw_inputs(42, 4)),
    "lw_light_agint_helm":          lw_recipe("Hexhide Helm",              52, "head",    "leather","agi_int_hybrid","common",   "trainer", lw_inputs(52, 5)),
    "lw_light_agint_leggings":      lw_recipe("Hexhide Leggings",          60, "legs",    "leather","agi_int_hybrid","uncommon", "trainer", lw_inputs(60, 7)),

    # STR/INT hybrid leather (Templar, Ranger tank)
    "lw_light_stint_gloves":        lw_recipe("Ironhide Leather Gloves",   36, "hands",   "leather","str_int_hybrid","common",   "trainer", lw_inputs(36, 4)),
    "lw_light_stint_helm":          lw_recipe("Ironhide Leather Helm",     50, "head",    "leather","str_int_hybrid","common",   "trainer", lw_inputs(50, 5)),

    # ── MEDIUM LEATHER TIER (75-149) — trainer ────────────────────────────
    # STR leather (Barbarian tier-up)
    "lw_medium_str_gloves":         lw_recipe("Toughened Leather Gloves",  78, "hands",   "leather","str_physical",  "uncommon", "trainer", lw_inputs(78, 5)),
    "lw_medium_str_bracers":        lw_recipe("Toughened Leather Bracers", 82, "wrist",   "leather","str_physical",  "uncommon", "trainer", lw_inputs(82, 4)),
    "lw_medium_str_helm":           lw_recipe("Toughened Leather Helm",    90, "head",    "leather","str_physical",  "uncommon", "trainer", lw_inputs(90, 6)),
    "lw_medium_str_vest":           lw_recipe("Toughened Leather Vest",   105, "chest",   "leather","str_physical",  "uncommon", "trainer", lw_inputs(105, 9)),
    "lw_medium_str_leggings":       lw_recipe("Toughened Leather Leggings",112,"legs",    "leather","str_physical",  "uncommon", "trainer", lw_inputs(112, 8)),

    # INT leather (Druid tier-up)
    "lw_medium_int_bracers":        lw_recipe("Mistweave Bracers",         80, "wrist",   "leather","int_caster",    "uncommon", "trainer", lw_inputs(80, 4)),
    "lw_medium_int_helm":           lw_recipe("Mistweave Helm",            88, "head",    "leather","int_caster",    "uncommon", "trainer", lw_inputs(88, 6)),
    "lw_medium_int_spaulders":      lw_recipe("Mistweave Spaulders",       93, "shoulders","leather","int_caster",  "uncommon", "trainer", lw_inputs(93, 6)),
    "lw_medium_int_vest":           lw_recipe("Mistweave Vest",           108, "chest",   "leather","int_caster",    "uncommon", "trainer", lw_inputs(108, 9)),
    "lw_medium_int_leggings":       lw_recipe("Mistweave Leggings",       118, "legs",    "leather","int_caster",    "uncommon", "trainer", lw_inputs(118, 8)),

    # AGI/INT hybrid (Witch Doctor tier-up)
    "lw_medium_agint_spaulders":    lw_recipe("Voodoo Spaulders",          85, "shoulders","leather","agi_int_hybrid","uncommon","trainer", lw_inputs(85, 6)),
    "lw_medium_agint_vest":         lw_recipe("Voodoo Vest",              103, "chest",   "leather","agi_int_hybrid","uncommon", "trainer", lw_inputs(103, 9)),
    "lw_medium_agint_helm":         lw_recipe("Voodoo Helm",              110, "head",    "leather","agi_int_hybrid","uncommon", "trainer", lw_inputs(110, 7)),

    # STR/INT hybrid (Templar tier-up)
    "lw_medium_stint_spaulders":    lw_recipe("Ironweald Spaulders",       87, "shoulders","leather","str_int_hybrid","uncommon","trainer", lw_inputs(87, 6)),
    "lw_medium_stint_vest":         lw_recipe("Ironweald Vest",           106, "chest",   "leather","str_int_hybrid","uncommon", "trainer", lw_inputs(106, 9)),

    # MAIL entries for LW (heavy+ leather becomes mail) — INT + STR/INT + AGI/INT
    "lw_heavy_int_mail_boots":      lw_recipe("Ironweave Mail Boots",     128, "feet",    "mail",  "int_caster",    "uncommon", "trainer", lw_inputs(128, 5)),
    "lw_heavy_int_mail_belt":       lw_recipe("Ironweave Mail Belt",      133, "waist",   "mail",  "int_caster",    "uncommon", "trainer", lw_inputs(133, 5)),
    "lw_heavy_int_mail_gloves":     lw_recipe("Ironweave Mail Gloves",    137, "hands",   "mail",  "int_caster",    "uncommon", "trainer", lw_inputs(137, 5)),
    "lw_heavy_int_mail_helm":       lw_recipe("Ironweave Mail Helm",      145, "head",    "mail",  "int_caster",    "uncommon", "trainer", lw_inputs(145, 7)),
    "lw_heavy_int_mail_vest":       lw_recipe("Ironweave Mail Vest",      148, "chest",   "mail",  "int_caster",    "uncommon", "trainer", lw_inputs(148, 9)),

    "lw_heavy_stint_mail_boots":    lw_recipe("Earthbound Mail Boots",    126, "feet",    "mail",  "str_int_hybrid","uncommon", "trainer", lw_inputs(126, 5)),
    "lw_heavy_stint_mail_helm":     lw_recipe("Earthbound Mail Helm",     142, "head",    "mail",  "str_int_hybrid","uncommon", "trainer", lw_inputs(142, 7)),
    "lw_heavy_stint_mail_vest":     lw_recipe("Earthbound Mail Vest",     146, "chest",   "mail",  "str_int_hybrid","uncommon", "trainer", lw_inputs(146, 9)),

    "lw_heavy_agint_mail_gloves":   lw_recipe("Predator Mail Gloves",     130, "hands",   "mail",  "agi_int_hybrid","uncommon", "trainer", lw_inputs(130, 5)),
    "lw_heavy_agint_mail_vest":     lw_recipe("Predator Mail Vest",       144, "chest",   "mail",  "agi_int_hybrid","uncommon", "trainer", lw_inputs(144, 9)),

    # ── THICK / RUGGED / HIGH TIER (150-300) — trainer ───────────────────
    "lw_thick_str_helm":            lw_recipe("Warbear Helm",             158, "head",    "leather","str_physical",  "uncommon", "trainer", lw_inputs(158, 8)),
    "lw_thick_str_vest":            lw_recipe("Warbear Vest",             165, "chest",   "leather","str_physical",  "uncommon", "trainer", lw_inputs(165, 12)),
    "lw_thick_int_helm":            lw_recipe("Wildwood Helm",            160, "head",    "leather","int_caster",    "uncommon", "trainer", lw_inputs(160, 8)),
    "lw_thick_int_vest":            lw_recipe("Wildwood Vest",            168, "chest",   "leather","int_caster",    "uncommon", "trainer", lw_inputs(168, 12)),
    "lw_thick_agint_helm":          lw_recipe("Shadowfell Helm",          163, "head",    "leather","agi_int_hybrid","uncommon", "trainer", lw_inputs(163, 8)),
    "lw_thick_agint_vest":          lw_recipe("Shadowfell Vest",          170, "chest",   "leather","agi_int_hybrid","uncommon", "trainer", lw_inputs(170, 12)),
    "lw_thick_int_mail_vest":       lw_recipe("Mistscale Mail Vest",      173, "chest",   "mail",  "int_caster",    "uncommon", "trainer", lw_inputs(173, 10)),
    "lw_rugged_str_vest":           lw_recipe("Ironhide Vest",            220, "chest",   "leather","str_physical",  "rare",     "trainer", lw_inputs(220, 14)),
    "lw_rugged_int_vest":           lw_recipe("Archdruid Vest",           225, "chest",   "leather","int_caster",    "rare",     "trainer", lw_inputs(225, 14)),
    "lw_rugged_agint_vest":         lw_recipe("Hexbinder Vest",           228, "chest",   "leather","agi_int_hybrid","rare",     "trainer", lw_inputs(228, 14)),
    "lw_rugged_int_mail_vest":      lw_recipe("Stormcaller Mail Vest",    232, "chest",   "mail",  "int_caster",    "rare",     "trainer", lw_inputs(232, 12)),

    # ── WORLD / DUNGEON DROPS ─────────────────────────────────────────────
    # Wailing Caverns (lvl 16-24) — snake-theme, nature-infused
    "lw_serpentkin_leather_vest":   lw_recipe("Serpentkin Leather Vest",   95, "chest",   "leather","agi_int_hybrid","uncommon", "drop",   lw_inputs(95, 10),  drop_zone="Wailing Caverns"),
    "lw_fang_leather_spaulders":    lw_recipe("Fang Leather Spaulders",    92, "shoulders","leather","str_physical", "uncommon", "drop",   lw_inputs(92, 7),   drop_zone="Wailing Caverns"),
    "lw_serpent_int_mail_helm":     lw_recipe("Serpent Mail Coif",         97, "head",    "mail",  "int_caster",    "uncommon", "drop",   lw_inputs(97, 7),   drop_zone="Wailing Caverns"),
    "lw_verdant_scale_gloves":      lw_recipe("Verdant Scale Gloves",      90, "hands",   "mail",  "agi_int_hybrid","uncommon", "drop",   lw_inputs(90, 6),   drop_zone="Wailing Caverns"),

    # Shadowfang Keep (lvl 19-25)
    "lw_shadowpelt_cloak":          lw_recipe("Shadowpelt Cloak",         140, "back",    "leather","agi_int_hybrid","rare",     "drop",   lw_inputs(140, 10), drop_zone="Shadowfang Keep"),
    "lw_cursed_leather_leggings":   lw_recipe("Cursed Leather Leggings",  143, "legs",    "leather","int_caster",    "rare",     "drop",   lw_inputs(143, 10), drop_zone="Shadowfang Keep"),
    "lw_cursed_mail_bracers":       lw_recipe("Cursed Mail Bracers",      138, "wrist",   "mail",  "int_caster",    "uncommon", "drop",   lw_inputs(138, 6),  drop_zone="Shadowfang Keep"),

    # Broodspiral (lvl 18-24)
    "lw_chitin_leather_helm":       lw_recipe("Chitinous Leather Helm",   110, "head",    "leather","str_physical",  "uncommon", "drop",   lw_inputs(110, 8),  drop_zone="The Broodspiral"),
    "lw_chitinscale_mail_vest":     lw_recipe("Chitinscale Mail Vest",    115, "chest",   "mail",  "agi_physical",  "uncommon", "drop",   lw_inputs(115, 9),  drop_zone="The Broodspiral"),
    "lw_brood_venom_bracers":       lw_recipe("Broodvenom Bracers",       108, "wrist",   "leather","agi_int_hybrid","uncommon", "drop",   lw_inputs(108, 6),  drop_zone="The Broodspiral"),

    # Razorfen Kraul (lvl 25-34)
    "lw_quilboar_spined_spaulders": lw_recipe("Quilboar Spined Spaulders",175, "shoulders","leather","str_physical", "rare",     "drop",   lw_inputs(175, 10), drop_zone="Razorfen Kraul"),
    "lw_razorboar_mail_helm":       lw_recipe("Razorboar Mail Helm",      180, "head",    "mail",  "str_int_hybrid","rare",     "drop",   lw_inputs(180, 9),  drop_zone="Razorfen Kraul"),
    "lw_razorfang_leather_vest":    lw_recipe("Razorfang Leather Vest",   178, "chest",   "leather","agi_physical",  "rare",     "drop",   lw_inputs(178, 12), drop_zone="Razorfen Kraul"),

    # Blackfathom Deeps (lvl 24-27)
    "lw_deepscale_leather_vest":    lw_recipe("Deepscale Leather Vest",   160, "chest",   "leather","agi_int_hybrid","rare",     "drop",   lw_inputs(160, 12), drop_zone="Blackfathom Deeps"),
    "lw_brine_mail_gloves":         lw_recipe("Brine Mail Gloves",        155, "hands",   "mail",  "int_caster",    "uncommon", "drop",   lw_inputs(155, 7),  drop_zone="Blackfathom Deeps"),

    # Plague Depths (lvl 30-34)
    "lw_plagued_leather_helm":      lw_recipe("Plagued Leather Helm",     212, "head",    "leather","int_caster",    "rare",     "drop",   lw_inputs(212, 10), drop_zone="Plague Depths"),
    "lw_rot_scale_mail_vest":       lw_recipe("Rotscale Mail Vest",       215, "chest",   "mail",  "agi_int_hybrid","rare",     "drop",   lw_inputs(215, 12), drop_zone="Plague Depths"),
    "lw_putrescent_leggings":       lw_recipe("Putrescent Leggings",      210, "legs",    "leather","str_int_hybrid","rare",     "drop",   lw_inputs(210, 10), drop_zone="Plague Depths"),

    # Grom's Rest (lvl 26-32)
    "lw_demonhide_vest":            lw_recipe("Demonhide Vest",           192, "chest",   "leather","agi_int_hybrid","rare",     "drop",   lw_inputs(192, 12), drop_zone="Grom's Rest"),
    "lw_nightstalker_spaulders":    lw_recipe("Nightstalker Spaulders",   188, "shoulders","leather","agi_physical","rare",     "drop",   lw_inputs(188, 8),  drop_zone="Grom's Rest"),

    # Echo Isles (lvl 10-15) — low-level drop recipes
    "lw_tidal_leather_belt":        lw_recipe("Tidal Leather Belt",        35, "waist",   "leather","int_caster",    "common",   "drop",   lw_inputs(35, 4),   drop_zone="Echo Isles"),
    "lw_scaled_isle_boots":         lw_recipe("Scaled Isle Boots",         42, "feet",    "leather","agi_int_hybrid","common",   "drop",   lw_inputs(42, 4),   drop_zone="Echo Isles"),

    # Widow's Lair (lvl 17-19) — spider-silk hybrid
    "lw_silkweb_leather_bracers":   lw_recipe("Silkweb Leather Bracers",  123, "wrist",   "leather","agi_int_hybrid","uncommon", "drop",   lw_inputs(123, 6),  drop_zone="Widow's Lair"),
    "lw_venom_sac_spaulders":       lw_recipe("Venom Sac Spaulders",      120, "shoulders","leather","str_int_hybrid","uncommon","drop",   lw_inputs(120, 7),  drop_zone="Widow's Lair"),

    # ── VENDOR RECIPES ────────────────────────────────────────────────────
    # Astranaar — druid / nature theme
    "lw_astranaar_druid_helm":      lw_recipe("Moonleaf Helm",            135, "head",    "leather","int_caster",    "uncommon", "vendor", lw_inputs(135, 8),  vendor_location="Astranaar"),
    "lw_astranaar_druid_spaulders": lw_recipe("Moonleaf Spaulders",       140, "shoulders","leather","int_caster",  "uncommon", "vendor", lw_inputs(140, 8),  vendor_location="Astranaar"),

    # Ratchet — eclectic trade port, agi/int tinker/witch doctor gear
    "lw_ratchet_goblin_gloves":     lw_recipe("Goblin-Stitched Gloves",    72, "hands",   "leather","agi_int_hybrid","uncommon", "vendor", lw_inputs(72, 7),   vendor_location="Ratchet"),
    "lw_ratchet_tinker_vest":       lw_recipe("Copper-Seam Leather Vest",  75, "chest",   "leather","agi_int_hybrid","uncommon", "vendor", lw_inputs(75, 9),   vendor_location="Ratchet"),

    # Splintertree Post — ashenvale, int mail for shamans
    "lw_splintertree_shaman_helm":  lw_recipe("Galewind Mail Coif",       152, "head",    "mail",  "int_caster",    "uncommon", "vendor", lw_inputs(152, 8),  vendor_location="Splintertree Post"),

    # Camp Taurajo — tauren theme, str/int mail (Primalist)
    "lw_taurajo_primalist_vest":    lw_recipe("Earthwalker Mail Vest",    148, "chest",   "mail",  "str_int_hybrid","uncommon", "vendor", lw_inputs(148, 10), vendor_location="Camp Taurajo"),

    # Undercity — dark themed, rare spi_healer leather (Druid healer)
    "lw_undercity_shade_vest":      lw_recipe("Shade-Blessed Leather Vest",200,"chest",  "leather","spi_healer",    "rare",     "vendor", lw_inputs(200, 14), vendor_location="Undercity"),

    # Hidden vendor Fenris Isle
    "lw_fenris_mail_spaulders":     lw_recipe("Fenris Mail Spaulders",    162, "shoulders","mail", "str_int_hybrid","rare",     "vendor", lw_inputs(162, 10), vendor_location="Fenris Isle (hidden)"),
    "lw_wolfhide_helm":             lw_recipe("Wolfhide Helm",            158, "head",    "leather","str_physical",  "rare",     "vendor", lw_inputs(158, 9),  vendor_location="Fenris Isle (hidden)"),

    # Hidden vendor Razorfen approach
    "lw_razorfen_tusk_bracers":     lw_recipe("Razorfen Tusk Bracers",    168, "wrist",   "leather","str_int_hybrid","rare",     "vendor", lw_inputs(168, 7),  vendor_location="Razorfen Approach (hidden)"),
}


# ════════════════════════════════════════════════════════════════════════════
# TAILORING — cloth only
# ════════════════════════════════════════════════════════════════════════════
# Current: 53 trainer (all int_caster + spi_healer — already good)
# Need: AGI/INT cloth (Bloodmage/Felsworn), STR cloth (rare), STR/INT cloth (Sun Cleric support)
# Plus drop/vendor flavour

def cloth_mat(req):
    if req < 50:   return "cloth_linen",   "bolt_linen"
    if req < 100:  return "cloth_cotton",  "bolt_cotton"
    if req < 175:  return "cloth_wool",    "bolt_wool"
    if req < 240:  return "cloth_silk",    "bolt_silk"
    return "cloth_mageweave", "bolt_mageweave"

def cloth_recipe(name, req, slot, stat_template, rarity, source,
                 inputs=None, drop_zone=None, vendor_location=None):
    tier, mat = cloth_mat(req)
    bolts = max(1, req // 20)
    r = {
        "name": name,
        "skill_required": req,
        "skill_range": sr(req),
        "source": source,
        "inputs": inputs or {mat: bolts},
        "output": {
            "kind": "armor",
            "slot": slot,
            "armor_type": "cloth",
            "stat_template": stat_template,
            "item_level": ilvl(req),
            "rarity": rarity,
            "material_tier": tier,
        }
    }
    if drop_zone: r["drop_zone"] = drop_zone
    if vendor_location: r["vendor_location"] = vendor_location
    return r

NEW_TAILORING_RECIPES = {
    # ── AGI/INT cloth (Bloodmage, Felsworn) — trainer ─────────────────────
    "tai_linen_agint_gloves":       cloth_recipe("Bloodweave Gloves",       5,  "hands",   "agi_int_hybrid","common",   "trainer"),
    "tai_linen_agint_belt":         cloth_recipe("Bloodweave Belt",         12, "waist",   "agi_int_hybrid","common",   "trainer"),
    "tai_linen_agint_bracers":      cloth_recipe("Bloodweave Bracers",      18, "wrist",   "agi_int_hybrid","common",   "trainer"),
    "tai_cotton_agint_boots":       cloth_recipe("Felstitched Boots",        55, "feet",   "agi_int_hybrid","common",   "trainer"),
    "tai_cotton_agint_helm":        cloth_recipe("Felstitched Cowl",         65, "head",   "agi_int_hybrid","common",   "trainer"),
    "tai_cotton_agint_leggings":    cloth_recipe("Felstitched Leggings",     70, "legs",   "agi_int_hybrid","uncommon", "trainer"),
    "tai_cotton_agint_vest":        cloth_recipe("Felstitched Robe",         75, "chest",  "agi_int_hybrid","uncommon", "trainer"),
    "tai_wool_agint_spaulders":     cloth_recipe("Darkweave Spaulders",     105, "shoulders","agi_int_hybrid","uncommon","trainer"),
    "tai_wool_agint_helm":          cloth_recipe("Darkweave Hood",          112, "head",   "agi_int_hybrid","uncommon", "trainer"),
    "tai_wool_agint_vest":          cloth_recipe("Darkweave Robe",          118, "chest",  "agi_int_hybrid","uncommon", "trainer"),
    "tai_silk_agint_spaulders":     cloth_recipe("Soulthread Spaulders",    182, "shoulders","agi_int_hybrid","uncommon","trainer"),
    "tai_silk_agint_helm":          cloth_recipe("Soulthread Hood",         188, "head",   "agi_int_hybrid","uncommon", "trainer"),
    "tai_silk_agint_vest":          cloth_recipe("Soulthread Robe",         195, "chest",  "agi_int_hybrid","uncommon", "trainer"),

    # ── STR/INT cloth (Sun Cleric, Cultist pre-plate) — trainer ───────────
    "tai_linen_stint_gloves":       cloth_recipe("Pilgrim's Gloves",         8, "hands",   "str_int_hybrid","common",   "trainer"),
    "tai_cotton_stint_helm":        cloth_recipe("Pilgrim's Hood",           60, "head",   "str_int_hybrid","common",   "trainer"),
    "tai_wool_stint_vest":          cloth_recipe("Pilgrim's Robe",          100, "chest",  "str_int_hybrid","uncommon", "trainer"),
    "tai_silk_stint_vest":          cloth_recipe("Radiant Robe",            175, "chest",  "str_int_hybrid","uncommon", "trainer"),

    # ── World / dungeon drop tailoring ────────────────────────────────────
    # Shadowfang Keep — caster robes
    "tai_shadowfang_robe":          cloth_recipe("Shadowfang Robes",        145, "chest",  "int_caster",    "rare",     "drop",   drop_zone="Shadowfang Keep"),
    "tai_shadowweave_hood":         cloth_recipe("Shadowweave Hood",        143, "head",   "agi_int_hybrid","rare",     "drop",   drop_zone="Shadowfang Keep"),

    # Plague Depths — apothecary-themed
    "tai_plagueweave_robe":         cloth_recipe("Plagueweave Robe",        208, "chest",  "int_caster",    "rare",     "drop",   drop_zone="Plague Depths"),
    "tai_virulentthread_gloves":    cloth_recipe("Virulent-Thread Gloves",  205, "hands",  "agi_int_hybrid","rare",     "drop",   drop_zone="Plague Depths"),

    # Ambermill Tower — arcane-infused
    "tai_amberweave_spaulders":     cloth_recipe("Amberweave Spaulders",   148, "shoulders","int_caster",   "uncommon", "drop",   drop_zone="Ambermill Tower"),

    # Blackfathom Deeps — naga-silk
    "tai_nagasilk_robe":            cloth_recipe("Nagasilk Robe",           162, "chest",  "int_caster",    "rare",     "drop",   drop_zone="Blackfathom Deeps"),

    # Grom's Rest — demonic thread
    "tai_demonthread_leggings":     cloth_recipe("Demonthread Leggings",    192, "legs",   "agi_int_hybrid","rare",     "drop",   drop_zone="Grom's Rest"),

    # Wailing Caverns — nature weave
    "tai_verdant_robe":             cloth_recipe("Verdant Druid Robe",      100, "chest",  "int_caster",    "uncommon", "drop",   drop_zone="Wailing Caverns"),

    # ── Vendor recipes ────────────────────────────────────────────────────
    # Undercity — dark elegance
    "tai_undercity_darkrobe":       cloth_recipe("Dark Elegance Robe",      195, "chest",  "agi_int_hybrid","rare",     "vendor", vendor_location="Undercity"),
    # Orgrimmar — battle mage
    "tai_org_battlemage_robe":      cloth_recipe("Battlemage Robe",         122, "chest",  "str_int_hybrid","uncommon", "vendor", vendor_location="Orgrimmar"),
    # Astranaar — mooncloth-adjacent
    "tai_astranaar_moonrobe":       cloth_recipe("Astranaar Moonrobe",      165, "chest",  "spi_healer",    "rare",     "vendor", vendor_location="Astranaar"),
    # Ratchet — hodge-podge merchant
    "tai_ratchet_felrobe":          cloth_recipe("Fel-Stitched Robe",        80, "chest",  "agi_int_hybrid","uncommon", "vendor", vendor_location="Ratchet"),
}


# ════════════════════════════════════════════════════════════════════════════
# ALCHEMY — expand consumable breadth
# ════════════════════════════════════════════════════════════════════════════
# Current: 18 trainer, 0 drop/vendor
# Keep simple — just add a few world-drop/vendor rare potions + missing stat types

def alch_recipe(name, req, consumable_id, source, count=1,
                inputs=None, drop_zone=None, vendor_location=None):
    r = {
        "name": name,
        "skill_required": req,
        "skill_range": sr(req),
        "count": count,
        "source": source,
        "inputs": inputs or {"herb_peacebloom": 2, "vial_empty": 1},
        "output": {
            "kind": "consumable",
            "consumable_id": consumable_id,
        }
    }
    if drop_zone: r["drop_zone"] = drop_zone
    if vendor_location: r["vendor_location"] = vendor_location
    return r

NEW_ALCHEMY_RECIPES = {
    # World drop rare potions (named bosses drop the recipe, not the potion)
    "alch_elixir_fortitude_drop":       alch_recipe("Elixir of Fortitude",        95,  "elixir_fortitude",      "drop",   inputs={"herb_kingsblood": 2, "vial_empty": 1}, drop_zone="Wailing Caverns"),
    "alch_potion_free_action_drop":     alch_recipe("Free Action Potion",        130,  "potion_free_action",    "drop",   inputs={"herb_stranglekelp": 2, "herb_liferoot": 1, "vial_empty": 1}, drop_zone="Shadowfang Keep"),
    "alch_elixir_shadow_power_drop":    alch_recipe("Elixir of Shadow Power",    160,  "elixir_shadow_power",   "drop",   inputs={"herb_fadeleaf": 2, "vial_empty": 1}, drop_zone="Plague Depths"),
    "alch_flask_mending_drop":          alch_recipe("Flask of Mending",          200,  "flask_mending",         "drop",   inputs={"herb_goldthorn": 3, "herb_blindweed": 1, "vial_empty": 1}, drop_zone="Blackfathom Deeps"),
    "alch_elixir_agility_drop":         alch_recipe("Elixir of Greater Agility", 175,  "elixir_greater_agility","drop",   inputs={"herb_sungrass": 2, "vial_empty": 1}, drop_zone="Razorfen Kraul"),

    # Vendor recipes
    "alch_transmute_iron_gold_vendor":  alch_recipe("Transmute: Iron to Gold",   225,  "transmute_iron_gold",   "vendor", inputs={"bar_iron": 4, "herb_goldthorn": 2}, vendor_location="Undercity"),
    "alch_potion_invulnerability_vendor":alch_recipe("Potion of Invulnerability",195,  "potion_invulnerability","vendor", inputs={"herb_blindweed": 3, "herb_firebloom": 1, "vial_empty": 1}, vendor_location="Ratchet"),
}


# ════════════════════════════════════════════════════════════════════════════
# WOODWORKING — staves, bows, polearms, wands
# ════════════════════════════════════════════════════════════════════════════
# Current: 57 trainer, 0 drop/vendor
# Need: more stat templates, drop recipes for caster staves and rare bows

def wood_recipe(name, req, slot, weapon_type, stat_template, rarity, source,
                inputs=None, drop_zone=None, vendor_location=None):
    plank = "plank_light" if req < 100 else ("plank_medium" if req < 200 else "plank_hardwood")
    r = {
        "name": name,
        "skill_required": req,
        "skill_range": sr(req),
        "source": source,
        "inputs": inputs or {plank: max(4, req // 25), "component_string": 1} if weapon_type == "bow" else {plank: max(3, req // 30)},
        "output": {
            "kind": "weapon",
            "slot": slot,
            "weapon_type": weapon_type,
            "stat_template": stat_template,
            "item_level": ilvl(req),
            "rarity": rarity,
        }
    }
    if drop_zone: r["drop_zone"] = drop_zone
    if vendor_location: r["vendor_location"] = vendor_location
    return r

NEW_WOODWORKING_RECIPES = {
    # Trainer — fill in missing stat templates on staves
    "ww_staff_agint_light":         wood_recipe("Shadowroot Staff",         15, "two_hand","staff",  "agi_int_hybrid","common",   "trainer"),
    "ww_staff_agint_medium":        wood_recipe("Darkthorn Staff",          80, "two_hand","staff",  "agi_int_hybrid","uncommon", "trainer"),
    "ww_staff_agint_heavy":         wood_recipe("Felwood Staff",           160, "two_hand","staff",  "agi_int_hybrid","uncommon", "trainer"),
    "ww_staff_spi_light":           wood_recipe("Healer's Ashwood Staff",   20, "two_hand","staff",  "spi_healer",    "common",   "trainer"),
    "ww_staff_spi_medium":          wood_recipe("Grove-Blessed Staff",      90, "two_hand","staff",  "spi_healer",    "uncommon", "trainer"),
    "ww_staff_spi_heavy":           wood_recipe("Lifebark Staff",          170, "two_hand","staff",  "spi_healer",    "uncommon", "trainer"),
    "ww_staff_stint_light":         wood_recipe("Pilgrim's Staff",          25, "two_hand","staff",  "str_int_hybrid","common",   "trainer"),
    "ww_staff_stint_medium":        wood_recipe("Warden's Staff",           95, "two_hand","staff",  "str_int_hybrid","uncommon", "trainer"),
    "ww_staff_stint_heavy":         wood_recipe("Crusader's Staff",        175, "two_hand","staff",  "str_int_hybrid","uncommon", "trainer"),

    # Wands — trainer
    "ww_wand_int_light":            wood_recipe("Thornwood Wand",            5, "ranged",  "wand",   "int_caster",    "common",   "trainer", {"plank_light": 2}),
    "ww_wand_int_medium":           wood_recipe("Mystic Oak Wand",          70, "ranged",  "wand",   "int_caster",    "common",   "trainer", {"plank_light": 3}),
    "ww_wand_spi_light":            wood_recipe("Healer's Wand",            10, "ranged",  "wand",   "spi_healer",    "common",   "trainer", {"plank_light": 2}),
    "ww_wand_spi_medium":           wood_recipe("Blessed Ashwand",          75, "ranged",  "wand",   "spi_healer",    "common",   "trainer", {"plank_light": 3}),
    "ww_wand_agint_light":          wood_recipe("Hexwood Wand",             12, "ranged",  "wand",   "agi_int_hybrid","common",   "trainer", {"plank_light": 2}),

    # Polearms — trainer
    "ww_polearm_agi_light":         wood_recipe("Ashwood Spear",            30, "two_hand","polearm","agi_physical",  "common",   "trainer"),
    "ww_polearm_agi_medium":        wood_recipe("Ironwood Lance",          105, "two_hand","polearm","agi_physical",  "uncommon", "trainer"),
    "ww_polearm_stint_medium":      wood_recipe("Warden's Halberd",         98, "two_hand","polearm","str_int_hybrid","uncommon", "trainer"),

    # World / dungeon drop recipes
    "ww_bow_wailing_caverns":       wood_recipe("Serpentwood Bow",          88, "ranged",  "bow",    "agi_physical",  "uncommon", "drop",   {"plank_medium": 5, "component_string": 2}, drop_zone="Wailing Caverns"),
    "ww_staff_blackfathom":         wood_recipe("Naga Driftwood Staff",    158, "two_hand","staff",  "int_caster",    "rare",     "drop",   {"plank_medium": 6}, drop_zone="Blackfathom Deeps"),
    "ww_staff_plague_depths":       wood_recipe("Plague-Bleached Staff",   205, "two_hand","staff",  "agi_int_hybrid","rare",     "drop",   {"plank_hardwood": 5}, drop_zone="Plague Depths"),
    "ww_bow_sfk":                   wood_recipe("Shadowfang Longbow",      142, "ranged",  "bow",    "agi_physical",  "rare",     "drop",   {"plank_medium": 6, "component_string": 2}, drop_zone="Shadowfang Keep"),
    "ww_wand_grom":                 wood_recipe("Demon-Touched Wand",      192, "ranged",  "wand",   "agi_int_hybrid","rare",     "drop",   {"plank_hardwood": 3}, drop_zone="Grom's Rest"),
    "ww_polearm_rfk":               wood_recipe("Razortusk Polearm",       178, "two_hand","polearm","str_physical",  "rare",     "drop",   {"plank_hardwood": 6}, drop_zone="Razorfen Kraul"),

    # Vendor recipes
    "ww_staff_orgrimmar_vendor":    wood_recipe("Stormcaller's Staff",     118, "two_hand","staff",  "str_int_hybrid","uncommon", "vendor", {"plank_medium": 5}, vendor_location="Orgrimmar"),
    "ww_bow_crossroads_vendor":     wood_recipe("Plains Longbow",           82, "ranged",  "bow",    "agi_physical",  "uncommon", "vendor", {"plank_light": 5, "component_string": 2}, vendor_location="The Crossroads"),
    "ww_wand_undercity_vendor":     wood_recipe("Shadow-Etched Wand",      195, "ranged",  "wand",   "int_caster",    "rare",     "vendor", {"plank_hardwood": 3}, vendor_location="Undercity"),
    "ww_staff_astranaar_vendor":    wood_recipe("Grove Staff",             155, "two_hand","staff",  "spi_healer",    "rare",     "vendor", {"plank_medium": 6}, vendor_location="Astranaar"),
    "ww_polearm_ratchet_vendor":    wood_recipe("Ratchet War-Spear",        65, "two_hand","polearm","agi_physical",  "common",   "vendor", {"plank_light": 4}, vendor_location="Ratchet"),
}


# ════════════════════════════════════════════════════════════════════════════
# WRITE TO FILES
# ════════════════════════════════════════════════════════════════════════════

def write_bs():
    path = REPO / "data/blacksmithing/recipes.json"
    with open(path) as f:
        data = json.load(f)
    before = len(data["recipes"])
    data["recipes"].update(NEW_BS_RECIPES)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    added = len(data["recipes"]) - before
    print(f"BS: {before} → {len(data['recipes'])} recipes (+{added})")

def write_lw():
    path = REPO / "data/leatherworking/recipes.json"
    with open(path) as f:
        data = json.load(f)
    existing = {k: v for k, v in data["recipes"].items() if isinstance(v, dict)}
    before = len(existing)
    existing.update(NEW_LW_RECIPES)
    data["recipes"] = existing
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    added = len(existing) - before
    print(f"LW: {before} → {len(existing)} recipes (+{added})")

def write_tailoring():
    path = REPO / "data/crafting/recipes.json"
    with open(path) as f:
        data = json.load(f)
    tai = data["professions"]["tailoring"]["recipes"]
    before = len(tai)
    tai.update(NEW_TAILORING_RECIPES)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Tailoring: {before} → {len(tai)} recipes (+{len(tai)-before})")

def write_alchemy():
    path = REPO / "data/crafting/recipes.json"
    with open(path) as f:
        data = json.load(f)
    alch = data["professions"]["alchemy"]["recipes"]
    before = len(alch)
    alch.update(NEW_ALCHEMY_RECIPES)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Alchemy: {before} → {len(alch)} recipes (+{len(alch)-before})")

def write_woodworking():
    path = REPO / "data/crafting/recipes.json"
    with open(path) as f:
        data = json.load(f)
    ww = data["professions"]["woodworking"]["recipes"]
    before = len(ww)
    ww.update(NEW_WOODWORKING_RECIPES)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Woodworking: {before} → {len(ww)} recipes (+{len(ww)-before})")

if __name__ == "__main__":
    write_bs()
    write_lw()
    write_tailoring()
    write_alchemy()
    write_woodworking()

    # Final audit
    print("\n── Final source breakdown ──")
    import sys
    sys.path.insert(0, str(REPO))
    from world.recipe_manager import _load_all_recipes, _RECIPE_SOURCES
    import world.recipe_manager as rm
    rm._RECIPE_SOURCES = None
    all_r = rm._load_all_recipes()

    by_prof = {}
    for rid, (prof, r) in all_r.items():
        src = r.get("source", "trainer")
        by_prof.setdefault(prof, {"trainer": 0, "drop": 0, "vendor": 0, "quest": 0})
        by_prof[prof][src] = by_prof[prof].get(src, 0) + 1

    total_trainer = total_world = 0
    for prof, counts in sorted(by_prof.items()):
        t = counts.get("trainer", 0)
        d = counts.get("drop", 0)
        v = counts.get("vendor", 0)
        total = t + d + v
        pct_trainer = 100 * t / total if total else 0
        print(f"  {prof:15s}: {total:3d} total | trainer={t:3d} ({pct_trainer:.0f}%) drop={d:2d} vendor={v:2d}")
        total_trainer += t
        total_world += d + v

    grand = total_trainer + total_world
    print(f"\n  GRAND TOTAL: {grand} recipes | trainer={total_trainer} ({100*total_trainer/grand:.0f}%) world={total_world} ({100*total_world/grand:.0f}%)")
