"""
Pass 2 — push tailoring and woodworking closer to 60/40 trainer/world.
Adds ~20 more drop/vendor recipes to each, focusing on complete stat coverage gaps.
"""
import json
from pathlib import Path

REPO = Path(__file__).parent.parent

def sr(req):
    return [req + 5, req + 15, req + 25, req + 35]

def ilvl(req):
    return max(1, int(req * 60 / 300) + 1)

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

def wood_recipe(name, req, slot, weapon_type, stat_template, rarity, source,
                inputs=None, drop_zone=None, vendor_location=None):
    plank = "plank_light" if req < 100 else ("plank_medium" if req < 200 else "plank_hardwood")
    default_inputs = {plank: max(4, req // 25), "component_string": 1} if weapon_type == "bow" else {plank: max(3, req // 30)}
    r = {
        "name": name,
        "skill_required": req,
        "skill_range": sr(req),
        "source": source,
        "inputs": inputs or default_inputs,
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

# ── MORE TAILORING DROPS ─────────────────────────────────────────────────
# (existing: 8 drop, 4 vendor → target ~35 drop+vendor total)
EXTRA_TAILORING = {
    # Ragefire Chasm — fire-woven
    "tai_fireweave_cowl":           cloth_recipe("Fireweave Cowl",           88, "head",    "int_caster",    "uncommon", "drop",   drop_zone="Ragefire Chasm"),
    "tai_ember_cloth_leggings":     cloth_recipe("Ember Cloth Leggings",     92, "legs",    "agi_int_hybrid","uncommon", "drop",   drop_zone="Ragefire Chasm"),
    "tai_blazethread_robes":        cloth_recipe("Blazethread Robes",        95, "chest",   "int_caster",    "uncommon", "drop",   drop_zone="Ragefire Chasm"),

    # Echo Isles — troll voodoo cloth
    "tai_hex_cloth_gloves":         cloth_recipe("Hex Cloth Gloves",         18, "hands",   "agi_int_hybrid","common",   "drop",   drop_zone="Echo Isles"),
    "tai_fetish_belt":              cloth_recipe("Fetish Belt",               22, "waist",   "agi_int_hybrid","common",   "drop",   drop_zone="Echo Isles"),
    "tai_mojo_bracers":             cloth_recipe("Mojo Bracers",              25, "wrist",   "agi_int_hybrid","common",   "drop",   drop_zone="Echo Isles"),

    # Widow's Lair — silk-spun spiderweb
    "tai_silkspun_robe":            cloth_recipe("Silkspun Robe",            108, "chest",   "spi_healer",    "uncommon", "drop",   drop_zone="Widow's Lair"),
    "tai_webweave_spaulders":       cloth_recipe("Webweave Spaulders",       105, "shoulders","int_caster",   "uncommon", "drop",   drop_zone="Widow's Lair"),
    "tai_venom_cord_belt":          cloth_recipe("Venom Cord Belt",          102, "waist",   "agi_int_hybrid","uncommon", "drop",   drop_zone="Widow's Lair"),

    # Broodspiral — chitin-threaded
    "tai_chitin_thread_vest":       cloth_recipe("Chitin-Thread Robe",       118, "chest",   "agi_int_hybrid","uncommon", "drop",   drop_zone="The Broodspiral"),
    "tai_carapace_mantle":          cloth_recipe("Carapace Mantle",          115, "shoulders","int_caster",   "uncommon", "drop",   drop_zone="The Broodspiral"),

    # Wailing Caverns — nature-threaded
    "tai_mistweave_robe_drop":      cloth_recipe("Mistweave Robe",           100, "chest",   "spi_healer",    "uncommon", "drop",   drop_zone="Wailing Caverns"),
    "tai_vine_woven_leggings":      cloth_recipe("Vine-Woven Leggings",       98, "legs",    "int_caster",    "uncommon", "drop",   drop_zone="Wailing Caverns"),

    # Razorfen Kraul — quilboar bristle woven
    "tai_briarweave_robe":          cloth_recipe("Briarweave Robe",          172, "chest",   "str_int_hybrid","rare",     "drop",   drop_zone="Razorfen Kraul"),
    "tai_bristle_spaulders":        cloth_recipe("Bristle Spaulders",        168, "shoulders","int_caster",   "uncommon", "drop",   drop_zone="Razorfen Kraul"),

    # Scarlet Crypt (lvl 15-20 — undead scar theme)
    "tai_bloodsoaked_robe":         cloth_recipe("Bloodsoaked Robe",          75, "chest",   "int_caster",    "uncommon", "drop",   drop_zone="Scarlet Crypt"),
    "tai_scarlet_sash":             cloth_recipe("Scarlet Sash",              72, "waist",   "spi_healer",    "common",   "drop",   drop_zone="Scarlet Crypt"),

    # Ambermill — arcane scholar robes
    "tai_arcane_scholar_robe":      cloth_recipe("Arcane Scholar's Robe",    150, "chest",   "int_caster",    "rare",     "drop",   drop_zone="Ambermill Tower"),
    "tai_amber_inscribed_hood":     cloth_recipe("Amber-Inscribed Hood",     147, "head",    "int_caster",    "rare",     "drop",   drop_zone="Ambermill Tower"),

    # Grom's Rest — demonic cloth
    "tai_soulscorch_vestments":     cloth_recipe("Soulscorch Vestments",     195, "chest",   "agi_int_hybrid","rare",     "drop",   drop_zone="Grom's Rest"),
    "tai_voidthread_leggings":      cloth_recipe("Voidthread Leggings",      192, "legs",    "agi_int_hybrid","rare",     "drop",   drop_zone="Grom's Rest"),
    "tai_infernal_cowl":            cloth_recipe("Infernal Cowl",            190, "head",    "int_caster",    "rare",     "drop",   drop_zone="Grom's Rest"),

    # Vendor expansions — specific towns
    "tai_silverpine_mournerobe":    cloth_recipe("Silverpine Mournerobe",    135, "chest",   "spi_healer",    "uncommon", "vendor", vendor_location="The Sepulcher"),
    "tai_hillsbrad_rustic_robe":    cloth_recipe("Hillsbrad Rustic Robe",     40, "chest",   "spi_healer",    "common",   "vendor", vendor_location="Hillsbrad (Southshore)"),
    "tai_camp_taurajo_wardrobe":    cloth_recipe("Taurajo Warbands",          55, "chest",   "str_int_hybrid","common",   "vendor", vendor_location="Camp Taurajo"),
    "tai_orgrimmar_felweave":       cloth_recipe("Orgrimmar Felweave Robe",  128, "chest",   "agi_int_hybrid","uncommon", "vendor", vendor_location="Orgrimmar"),
    "tai_razor_hill_traveler":      cloth_recipe("Traveler's Cloth Robe",     12, "chest",   "int_caster",    "common",   "vendor", vendor_location="Razor Hill"),
}

# ── MORE WOODWORKING DROPS ────────────────────────────────────────────────
# (existing: 6 drop, 5 vendor → target ~25 drop+vendor total)
EXTRA_WOODWORKING = {
    # Ragefire Chasm — char-oak bows
    "ww_charoak_bow":               wood_recipe("Charred Oak Bow",           90, "ranged",  "bow",    "agi_physical",  "uncommon", "drop",   {"plank_light": 5, "component_string": 2}, drop_zone="Ragefire Chasm"),
    "ww_ember_staff":               wood_recipe("Emberwood Staff",           88, "two_hand","staff",  "int_caster",    "uncommon", "drop",   {"plank_light": 4}, drop_zone="Ragefire Chasm"),

    # Echo Isles — troll-carved
    "ww_tiki_staff":                wood_recipe("Tiki Staff",                30, "two_hand","staff",  "agi_int_hybrid","common",   "drop",   {"plank_light": 3}, drop_zone="Echo Isles"),
    "ww_bone_wand":                 wood_recipe("Bone-Tipped Wand",          28, "ranged",  "wand",   "agi_int_hybrid","common",   "drop",   {"plank_light": 2}, drop_zone="Echo Isles"),

    # Widow's Lair — venom-soaked
    "ww_venom_stave":               wood_recipe("Venomwood Staff",           120, "two_hand","staff",  "int_caster",    "uncommon", "drop",   {"plank_medium": 4}, drop_zone="Widow's Lair"),
    "ww_silk_bow":                  wood_recipe("Silkweb Shortbow",          118, "ranged",  "bow",    "agi_physical",  "uncommon", "drop",   {"plank_medium": 4, "component_string": 2}, drop_zone="Widow's Lair"),

    # Broodspiral — chitin-hafted
    "ww_chitin_haft_polearm":       wood_recipe("Chitin-Hafted Polearm",     115, "two_hand","polearm","agi_physical",  "uncommon", "drop",   {"plank_medium": 5}, drop_zone="The Broodspiral"),
    "ww_brood_wand":                wood_recipe("Brood-Stung Wand",          112, "ranged",  "wand",   "agi_int_hybrid","uncommon", "drop",   {"plank_medium": 2}, drop_zone="The Broodspiral"),

    # Wailing Caverns — serpentwood
    "ww_serpentwood_staff":         wood_recipe("Serpentwood Staff",          95, "two_hand","staff",  "int_caster",    "uncommon", "drop",   {"plank_medium": 4}, drop_zone="Wailing Caverns"),
    "ww_venomthorn_bow":            wood_recipe("Venomthorn Bow",             93, "ranged",  "bow",    "agi_physical",  "uncommon", "drop",   {"plank_medium": 4, "component_string": 2}, drop_zone="Wailing Caverns"),
    "ww_fang_polearm":              wood_recipe("Fang-Tipped Spear",          88, "two_hand","polearm","agi_physical",  "uncommon", "drop",   {"plank_medium": 4}, drop_zone="Wailing Caverns"),

    # Ambermill — arcane-etched
    "ww_amber_wand_arcane":         wood_recipe("Amber-Etched Wand",         145, "ranged",  "wand",   "int_caster",    "rare",     "drop",   {"plank_medium": 3}, drop_zone="Ambermill Tower"),
    "ww_amberwood_staff":           wood_recipe("Amberwood Staff",           148, "two_hand","staff",  "spi_healer",    "rare",     "drop",   {"plank_medium": 5}, drop_zone="Ambermill Tower"),

    # Scarlet Crypt — blessed ash
    "ww_scarlet_ash_wand":          wood_recipe("Scarlet Ash Wand",           72, "ranged",  "wand",   "spi_healer",    "common",   "drop",   {"plank_light": 2}, drop_zone="Scarlet Crypt"),
    "ww_piety_staff":               wood_recipe("Staff of Piety",             75, "two_hand","staff",  "spi_healer",    "common",   "drop",   {"plank_light": 3}, drop_zone="Scarlet Crypt"),

    # Vendor expansions
    "ww_crossroads_shortbow":       wood_recipe("Barrens Short Bow",          45, "ranged",  "bow",    "agi_physical",  "common",   "vendor", {"plank_light": 3, "component_string": 1}, vendor_location="The Crossroads"),
    "ww_sepulcher_shadow_wand":     wood_recipe("Shadow-Burned Wand",        135, "ranged",  "wand",   "int_caster",    "uncommon", "vendor", {"plank_medium": 3}, vendor_location="The Sepulcher"),
    "ww_ratchet_blunderbuss":       wood_recipe("Ratchet Blunderbuss",        78, "ranged",  "bow",    "agi_int_hybrid","uncommon", "vendor", {"plank_light": 5, "component_string": 2}, vendor_location="Ratchet"),
    "ww_taurajo_spirit_staff":      wood_recipe("Taurajo Spirit Staff",       88, "two_hand","staff",  "spi_healer",    "uncommon", "vendor", {"plank_medium": 4}, vendor_location="Camp Taurajo"),
    "ww_undercity_cursed_wand":     wood_recipe("Undercity Cursed Wand",     188, "ranged",  "wand",   "agi_int_hybrid","rare",     "vendor", {"plank_hardwood": 3}, vendor_location="Undercity"),
    "ww_astranaar_elven_bow":       wood_recipe("Astranaar Elven Bow",        162, "ranged",  "bow",    "agi_physical",  "rare",     "vendor", {"plank_medium": 6, "component_string": 2}, vendor_location="Astranaar"),
}

def write_tailoring_pass2():
    path = REPO / "data/crafting/recipes.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    tai = data["professions"]["tailoring"]["recipes"]
    before = len(tai)
    tai.update(EXTRA_TAILORING)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Tailoring: {before} → {len(tai)} (+{len(tai)-before})")

def write_woodworking_pass2():
    path = REPO / "data/crafting/recipes.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    ww = data["professions"]["woodworking"]["recipes"]
    before = len(ww)
    ww.update(EXTRA_WOODWORKING)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Woodworking: {before} → {len(ww)} (+{len(ww)-before})")

if __name__ == "__main__":
    write_tailoring_pass2()
    write_woodworking_pass2()

    import sys
    sys.path.insert(0, str(REPO))
    import world.recipe_manager as rm
    rm._RECIPE_SOURCES = None
    all_r = rm._load_all_recipes()

    by_prof = {}
    for rid, (prof, r) in all_r.items():
        src = r.get("source", "trainer")
        by_prof.setdefault(prof, {"trainer": 0, "drop": 0, "vendor": 0})
        by_prof[prof][src] = by_prof[prof].get(src, 0) + 1

    total_trainer = total_world = 0
    for prof, counts in sorted(by_prof.items()):
        t = counts.get("trainer", 0)
        d = counts.get("drop", 0)
        v = counts.get("vendor", 0)
        total = t + d + v
        pct = 100 * t / total if total else 0
        print(f"  {prof:15s}: {total:3d} total | trainer={t:3d} ({pct:.0f}%) drop={d:2d} vendor={v:2d}")
        total_trainer += t
        total_world += d + v

    grand = total_trainer + total_world
    print(f"\n  GRAND TOTAL: {grand} | trainer={total_trainer} ({100*total_trainer/grand:.0f}%) world={total_world} ({100*total_world/grand:.0f}%)")
