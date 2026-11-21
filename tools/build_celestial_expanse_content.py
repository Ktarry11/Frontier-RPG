#!/usr/bin/env python3
"""The Celestial Expanse's creatures, rares, encounter tables, loot, gathering and fishing (49-51). Idempotent.

    PYTHONPATH=. python3 tools/build_celestial_expanse_content.py [--dry]

docs/worldtree_brief.md: "The old sky ruins wake (Kharad-age machinery, sky-golems); Ascendancy patrols; sky beasts".
The Kharad's war-golems were lying where they fell on the Golem Fields until the seal cracked at the Crown; now they're
getting up, and the forge that made them is warming. The Ascendancy watches the river from the Lancer's Perch.

    open islands           rams and young boars between the places
    Crashfall              scuttlers on the wreck, ward-sparks where the old wards fired
    The Broad Isle         skymane lions, gale hawks, crystalback boars                   rare: Old Goldmane
    The Golem Fields       waking war-golems, Kharad sentinels, rubble                     rare: The Unbound Core
    The Silent Forge       forge guardians, ancestral smiths, molten crystal              rare: Forge-Elder Ommun
    The Orbiting Ruins     wind wyrms and bell sprites round the ring                     rare: Ringwarden Kozh
    The Whale Shallows     deep-sky whales, cloud serpents, skimming rays                 rare: The Pale Serpent
    The Lancer's Perch     the Ascendancy's binders, inquisitors, scouts and lancers      rare: Spire-Captain Alun Vesk
    The Spillway           eels, crabs and rift crawlers where Aurelion's water falls     rare: Old Mouth of the Spill
    Halcyon Rest, Tethertown, the Last Falls, the Aurelion Approach: safe
    The Golem Vault (cave) the golem crews asleep in the stone, and the storm in the cores   bosses: Stormwright Yrvald,
                           Vault-Thane Brask

THE NUMBERS follow the tiers (tools/build_sunward_crown_content.py): trash basic 4L - 10, a rare's 10L - 200 at
multiplier 2.2, item level = the rare's level + 3.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_return_voyage_content import (  # noqa: E402
    CREATURES, KITS, ENCOUNTERS, kit_slug, merge_json, _detect_format, dmg, dot, debuff, buff, loot_audit)
from tools.build_tempest_openworld import enrage, stun, shield  # noqa: E402
from tools.build_scarlet_monastery_content import opener, stun_hit, heal  # noqa: E402

RARE_LOOT = ROOT / "data/loot/celestial_expanse_rare_loot.json"
CAVE_LOOT = ROOT / "data/loot/golem_vault_boss_loot.json"
CAVE = "The Golem Vault"
CAVE2 = "The Storm-Well"
ZONE = "The Celestial Expanse"
MAP_MODULE = "handbuilt_worldtree_celestial_expanse"


def T(level):
    return 4 * level - 10


def B(level):
    return 10 * level - 200


#: name -> (template, lo, hi, rare multiplier or None, sprite, kit shape, school, [ability names])
ROSTER = {
    # ---------------------------------------------------------------- the open islands
    "Cloudfleece Ram":        ("beast_fast", 49, 49, None, "sk_cloud_sheep", "beast", "physical",
                               ["Horn Butt", "Headlong", "Bruised"]),
    "Young Crystalback":      ("beast_fast", 49, 49, None, "sk_young_boar", "beast", "physical",
                               ["Tusk", "Crystal Charge", "Gashed"]),
    # ---------------------------------------------------------------- Crashfall
    "Crashfall Scuttler":     ("vermin_swarm", 49, 49, None, "sk_sky_crab", "warrior", "physical",
                               ["Pincer", "Scuttle In", "Hard Shell"]),
    "Ward-Spark":             ("elemental_caster", 49, 49, None, "sk_fading_wisp", "caster", "arcane",
                               ["Spark", "Ward Flash", "Burning Sigil"]),
    # ---------------------------------------------------------------- the Broad Isle
    "Skymane Lion":           ("beast_large", 49, 50, None, "sk_sky_lion", "bruiser", "physical",
                               ["Maul", "Pounce", "Knocked Down"]),
    "Gale Hawk":              ("beast_fast", 49, 50, None, "sk_gale_hawk", "beast", "nature",
                               ["Talons", "Stoop", "Wind-Torn"]),
    "Crystalback Boar":       ("beast_large", 49, 50, None, "sk_crystal_boar", "bruiser", "arcane",
                               ["Gore", "Crystal Rush", "Shard-Struck"]),
    "Old Goldmane":           ("beast_large", 50, 50, 2.2, "sk_sky_lion", "rare", "physical",
                               ["Goldmane's Jaws", "The Pride's Roar", "Pinned in the Grass", "Old King's Fury"]),
    # ---------------------------------------------------------------- the Golem Fields
    "Waking War-Golem":       ("elemental_bruiser", 49, 50, None, "kh_gravity_golem", "bruiser", "physical",
                               ["Stone Fist", "Gravity Slam", "Crushed"]),
    "Kharad Sentinel":        ("humanoid_warrior", 49, 50, None, "kh_sentinel_construct", "warrior", "arcane",
                               ["Sentinel's Strike", "Ward Beam", "Warded"]),
    "Golem-Field Rubble":     ("elemental_bruiser", 49, 50, None, "kh_mineral_elemental", "bruiser", "nature",
                               ["Rock Fist", "Rubble Burst", "Grit"]),
    "The Unbound Core":       ("elemental_caster", 50, 50, 2.2, "kh_unbound_core_rare", "rare", "arcane",
                               ["Core Pulse", "Every Golem Wakes", "Held in the Field", "Unbound"]),
    # ---------------------------------------------------------------- the Silent Forge
    "Forge Guardian":         ("humanoid_warrior", 50, 51, None, "kh_temple_guardian", "warrior", "physical",
                               ["Guardian's Hammer", "Anvil Blow", "Forge-Hardened"]),
    "Ancestral Smith":        ("humanoid_caster", 50, 51, None, "kh_ancestral_spirit", "caster", "fire",
                               ["Forge-Flame", "Quench Steam", "Searing Ash"]),
    "Molten Crystal Elemental": ("elemental_caster", 50, 51, None, "sk_crystal_elemental", "caster", "fire",
                                 ["Molten Shard", "Crystal Flare", "Glass Burn"]),
    "Forge-Elder Ommun":      ("humanoid_caster", 51, 51, 2.2, "kh_elder", "rare", "fire",
                               ["Elder's Hammer", "The Forge Wakes", "Struck on the Anvil", "First Fire"]),
    # ---------------------------------------------------------------- the Orbiting Ruins
    "Ringwind Wyrm":          ("beast_fast", 50, 51, None, "sk_wind_wyrm", "beast", "nature",
                               ["Bite", "Coiling Gust", "Wind-Scoured"]),
    "Bellringer Sprite":      ("elemental_caster", 50, 51, None, "sk_gust_sprite", "caster", "nature",
                               ["Toll", "Ringing Gust", "Deafened"]),
    "Ringwarden Kozh":        ("elemental_bruiser", 51, 51, 2.2, "kh_stonewarden", "rare", "physical",
                               ["Warden's Fist", "The Ring Turns", "Knocked Off the Ring", "The Citadel Stands"]),
    # ---------------------------------------------------------------- the Whale Shallows
    "Deep-Sky Whale":         ("beast_large", 50, 51, None, "sk_sky_whale", "bruiser", "physical",
                               ["Tail Sweep", "Breach", "Winded"]),
    "Cloud Serpent":          ("beast_fast", 50, 51, None, "sk_cloud_serpent", "beast", "frost",
                               ["Bite", "Coil Through the Cloud", "Chill Venom"]),
    "Skimming Ray":           ("beast_fast", 50, 51, None, "sk_sky_ray", "beast", "physical",
                               ["Wing Slap", "Barbed Tail", "Barbed"]),
    "The Pale Serpent":       ("beast_fast", 51, 51, 2.2, "sk_cloud_serpent", "rare", "frost",
                               ["Pale Fangs", "Out of the White", "Coiled", "Old Cold"]),
    # ---------------------------------------------------------------- the Lancer's Perch
    "Ascendancy Gravity-Binder": ("humanoid_caster", 50, 51, None, "ae_gravity_binder", "caster", "arcane",
                                  ["Weight", "Gravity Well", "Bound Heavy"]),
    "Ascendancy Inquisitor":  ("humanoid_caster", 50, 51, None, "ae_inquisitor", "caster", "holy",
                               ["Judgement", "Sentence", "Searing Verdict"]),
    "Ascendancy Scout Construct": ("humanoid_warrior", 50, 51, None, "ae_scout_construct", "bruiser", "arcane",
                                   ["Beam", "Sweep", "Marked"]),
    "Perch Lancer":           ("humanoid_rogue", 50, 51, None, "ae_sky_lancer", "warrior", "arcane",
                               ["Crystal Lance", "Lance Charge", "Lancer's Guard"]),
    "Spire-Captain Alun Vesk": ("humanoid_warrior", 51, 51, 2.2, "ae_high_commander", "rare", "arcane",
                                ["Captain's Blade", "The Spire's Guns", "Pinned by Orders", "Ascendant"]),
    # ---------------------------------------------------------------- the Spillway
    "Spillway Eel":           ("beast_fast", 50, 51, None, "sk_sky_eel", "beast", "nature",
                               ["Bite", "Coil and Strike", "Eel Venom"]),
    "Crystal Crab":           ("vermin_swarm", 50, 51, None, "sk_sky_crab", "warrior", "arcane",
                               ["Pincer", "Crystal Snap", "Hard Shell"]),
    "Rift Crawler":           ("beast_fast", 50, 51, None, "sk_rift_crawler", "beast", "shadow",
                               ["Rending Claws", "Out of the Crack", "Rift-Sick"]),
    "Old Mouth of the Spill": ("beast_large", 51, 51, 2.2, "sk_rift_crawler", "rare", "shadow",
                               ["Mouth of the Spill", "The Water Goes Dark", "Dragged Under", "Hunger"]),
}
RARES = {n for n, r in ROSTER.items() if r[3]}

#: the Golem Vault (tools/handbuilt_golem_vault.py) and its second floor, the Storm-Well (tools/handbuilt_storm_well.py):
#: the golem crews who lay down in the stone beside their work, the storm the wrights bound into the cores, and the two
#: who kept the vault. Trash rolled from each floor's own table, the bosses pinned by the maps. The crews are Kharad, the
#: giants who were here first: sheet KH's figures. CAVE_FLOOR says which floor each one lives on.
CAVE_ROSTER = {
    "Vault Sleeper":          ("humanoid_warrior", 50, 51, None, "kh_infantry", "warrior", "physical",
                               ["Hammer and Shield", "Shield-Wall", "Stone Skin"]),
    "Thunder-Binder Sleeper": ("humanoid_caster", 50, 51, None, "kh_thunder_mage", "caster", "nature",
                               ["Bound Lightning", "Thunder in the Stone", "Static"]),
    "Golem-Wright Sleeper":   ("humanoid_warrior", 50, 51, None, "kh_mason", "bruiser", "physical",
                               ["Wright's Hammer", "Mallet Sweep", "Hammered Flat"]),
    "Bound Gale":             ("elemental_caster", 51, 51, None, "sk_gale_elemental", "caster", "nature",
                               ["Gust", "Howl Through the Vault", "Wind-Cut"]),
    "Core-Charged Golem":     ("elemental_bruiser", 51, 51, None, "kh_gravity_golem", "bruiser", "nature",
                               ["Charged Fist", "Discharge", "Shocked"]),
    "Vault-Thane Brask":      ("humanoid_warrior", 51, 51, 2.3, "kh_champion", "boss", "physical",
                               ["Thane's Blade", "The Vault's Oath", "Shield-Bash", "Every Sleeper Wakes"]),
    "Stormwright Yrvald":     ("humanoid_caster", 51, 51, 2.5, "kh_high_priest", "boss", "nature",
                               ["Bound Bolt", "The Storm in the Core", "Struck Still", "The Well Overflows"]),
}
CAVE_BOSSES = {n for n, r in CAVE_ROSTER.items() if r[3]}
CAVE_FLOOR = {"Vault Sleeper": CAVE, "Golem-Wright Sleeper": CAVE, "Thunder-Binder Sleeper": CAVE,
              "Vault-Thane Brask": CAVE,
              "Bound Gale": CAVE2, "Core-Charged Golem": CAVE2, "Stormwright Yrvald": CAVE2}
ALL = {**ROSTER, **CAVE_ROSTER}


def sprite(name):
    return ALL[name][4]


RULES_START = "    # THE CELESTIAL EXPANSE (generated by tools/build_celestial_expanse_content.py; do not edit by hand)\n"
RULES_END = "    # END THE CELESTIAL EXPANSE\n"


def write_sprite_rules():
    path = ROOT / "creature_sprites.py"
    s = path.read_text(encoding="utf-8")
    block = RULES_START + "".join(f'    (r"^{re.escape(n.lower())}$", "{sprite(n)}"),\n' for n in ALL) + RULES_END
    if RULES_START in s:
        a = s.index(RULES_START)
        b = s.index(RULES_END) + len(RULES_END)
        s = s[:a] + block + s[b:]
    else:
        anchor = "    # THE SUNWARD CROWN (generated by tools/build_sunward_crown_content.py; do not edit by hand)\n"
        assert anchor in s
        s = s.replace(anchor, block + anchor, 1)
    path.write_text(s, encoding="utf-8")


def kit(name):
    template, lo, hi, mult, _s, shape, school, names = ALL[name]
    t = T(hi)
    s = school
    dispel = {"nature": "poison", "shadow": "curse"}.get(s, "magic")
    if shape == "beast":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.86), cooldown=3, school=s),
                dot(names[2], int(t * 0.27), 3, 3, school=s, **({"dispel_type": dispel} if s != "physical" else {}))]
    if shape == "warrior":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.86), cooldown=3, school=s),
                buff(names[2], 6, 3, {"armor": 190})]
    if shape == "caster":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.84), cooldown=5, school=s, is_aoe=True),
                dot(names[2], int(t * 0.27), 3, 3, school=s, dispel_type=dispel)]
    if shape == "bruiser":
        return [dmg(names[0], t + 8, school=s), dmg(names[1], int(t * 0.84), cooldown=4, school=s, is_aoe=True),
                debuff(names[2], 5, 2, {"dodge_rating": -20}, school=s)]
    b = B(hi)
    if shape == "boss":
        # a cave boss: an opener, a hard hit, a party hit, a stun, something dangerous, a heal or a flood, last stand
        kit_ = [opener(names[0], b, s), dmg(names[1], int(b * 0.88), cooldown=4, school=s),
                dmg(f"{names[0]}, Twice", int(b * 1.3), cooldown=4, school=s),
                dmg(names[3], int(b * 0.7), cooldown=5, school=s, is_aoe=True),
                stun_hit(names[2], int(b * 1.1), 6, school=s) if s != "physical" else stun_hit(names[2], int(b * 1.1), 6),
                dot(f"{names[1]}, Deep", int(b * 0.45), 5, 4, school=s, **({"dispel_type": dispel} if s != "physical"
                                                                            else {}))]
        if name == "Vault-Thane Brask":
            kit_.append(heal("Stone Sleep", int(b * 1.1), 6, school=s))
        else:
            kit_.append(dmg("Lightning Through the Vault", int(b * 1.8), cooldown=4, school=s))
        kit_.append(dict(name="Last Stand", kind="buff", amount=0, cooldown=99, mana_cost=0, school=s,
                         duration=30, self_only=True, hp_below=0.3, stat_mods={"attack_power": int(b * 0.4)}))
        return kit_
    # an open-world rare: a heavy basic, a party hit, a stun with a hammer behind it, and its last stand
    last = (shield(names[3], int(b * 1.2), school=s) if s in ("arcane", "frost") else enrage(names[3], int(b * 0.15), s))
    return [dmg(names[0], b, school=s), dmg(names[1], int(b * 0.8), cooldown=4, school=s, is_aoe=True),
            stun(names[2], int(b * 0.85), cooldown=5, school=s), dmg(f"{names[0]}, Again", int(b * 1.7), cooldown=5,
                                                                   school=s), last]


TABLE = {
    "open_zone": {"Cloudfleece Ram": 5, "Young Crystalback": 4},
    "subzones": {
        "Crashfall": {"Crashfall Scuttler": 5, "Ward-Spark": 4},
        "The Broad Isle": {"Skymane Lion": 4, "Gale Hawk": 4, "Crystalback Boar": 4, "Cloudfleece Ram": 1,
                           "Old Goldmane": 0},
        "The Golem Fields": {"Waking War-Golem": 5, "Kharad Sentinel": 4, "Golem-Field Rubble": 3,
                             "The Unbound Core": 0},
        "The Silent Forge": {"Forge Guardian": 5, "Ancestral Smith": 4, "Molten Crystal Elemental": 3,
                             "Forge-Elder Ommun": 0},
        "The Orbiting Ruins": {"Ringwind Wyrm": 6, "Bellringer Sprite": 5, "Ringwarden Kozh": 0},
        "The Whale Shallows": {"Cloud Serpent": 5, "Skimming Ray": 4, "Deep-Sky Whale": 2, "The Pale Serpent": 0},
        "The Lancer's Perch": {"Perch Lancer": 4, "Ascendancy Gravity-Binder": 4, "Ascendancy Inquisitor": 3,
                               "Ascendancy Scout Construct": 3, "Spire-Captain Alun Vesk": 0},
        "The Spillway": {"Spillway Eel": 4, "Crystal Crab": 4, "Rift Crawler": 4, "Old Mouth of the Spill": 0},
        "Halcyon Rest": None,
        "Tethertown": None,
        "The Last Falls": None,
        "The Aurelion Approach": None,
    },
}

#: rare -> four (name, slot, suffix, (a|w, type) or None, template)
POOLS = {
    "Old Goldmane": [
        ("Goldmane Pelt Cloak", "back", "of the Monkey", None, "agi_physical"),
        ("Pride-King's Helm", "head", "of the Bear", ("a", "plate"), "str_physical"),
        ("Lionheart Leggings", "legs", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Sunlit Mane Wraps", "wrist", "of the Prophet", ("a", "cloth"), "spi_healer")],
    "The Unbound Core": [
        ("Shard of the Unbound Core", "trinket", "of the Sorcerer", None, "int_caster"),
        ("Golem-Plate Breastplate", "chest", "of the Gorilla", ("a", "plate"), "str_int_hybrid"),
        ("Field-Wired Gauntlets", "hands", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Core-Lit Robe", "chest", "of the Prophet", ("a", "cloth"), "spi_healer")],
    "Forge-Elder Ommun": [
        ("Ommun's Forge Hammer", "two_hand", "of the Champion", ("w", "mace_2h"), "str_physical"),
        ("First Fire Mantle", "shoulder", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Anvil-Struck Girdle", "waist", "of the Bear", ("a", "plate"), "str_physical"),
        ("Smith's Ember Signet", "ring", "of the Invoker", None, "int_caster")],
    "Ringwarden Kozh": [
        ("Ringwarden's Bulwark", "off_hand", "of the Gorilla", ("w", "shield"), "str_int_hybrid"),
        ("Citadel Stone Treads", "feet", "of the Bear", ("a", "plate"), "str_physical"),
        ("Bell-Bronze Hauberk", "chest", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Orbit-Turned Band", "ring", "of the Monkey", None, "agi_physical")],
    "The Pale Serpent": [
        ("Pale Serpent Fang", "main_hand", "of the Tiger", ("w", "dagger"), "agi_physical"),
        ("Cloudscale Leggings", "legs", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Serpent-Cold Circlet", "head", "of the Prophet", ("a", "cloth"), "spi_healer"),
        ("Coil of the White", "neck", "of the Sorcerer", None, "int_caster")],
    "Spire-Captain Alun Vesk": [
        ("Spire-Captain's Saber", "main_hand", "of the Champion", ("w", "sword_1h"), "str_physical"),
        ("Ascendant Officer's Coat", "chest", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Perch-Watch Spaulders", "shoulder", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Vesk's Crystal Longbow", "ranged", "of the Monkey", ("w", "bow"), "agi_physical")],
    "Old Mouth of the Spill": [
        ("Spill-Dark Staff", "two_hand", "of the Prophet", ("w", "staff"), "spi_healer"),
        ("Crawler-Hide Jerkin", "chest", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Undertow Greaves", "legs", "of the Bear", ("a", "plate"), "str_physical"),
        ("Drowned Light Pendant", "neck", "of the Invoker", None, "int_caster")],
}

#: the vault's bosses: item level = boss level + 2
CAVE_POOLS = {
    "Vault-Thane Brask": [
        ("Thane's Oathblade", "main_hand", "of the Champion", ("w", "sword_1h"), "str_physical"),
        ("Vault-Warden's Shield", "off_hand", "of the Bear", ("w", "shield"), "str_physical"),
        ("Sleeper's Stone Mantle", "shoulder", "of the Gorilla", ("a", "plate"), "str_int_hybrid"),
        ("Knotwork Bracers", "wrist", "of the Monkey", ("a", "leather"), "agi_physical")],
    "Stormwright Yrvald": [
        ("Yrvald's Storm-Staff", "two_hand", "of the Sorcerer", ("w", "staff"), "int_caster"),
        ("Core-Binder's Robe", "chest", "of the Prophet", ("a", "cloth"), "spi_healer"),
        ("Thunder-Rune Hauberk", "chest", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Bound Storm Talisman", "neck", "of the Invoker", None, "int_caster")],
}

#: gathering at 49-51 in the open sky: the high 40s and low 50s herbs on the meadows, mithril, truesilver and thorium in
#: the islands' rock, and wood off the silver groves. Fishing: the Great Sky River and its pools.
NODES = {"celestial_expanse": {"slots": 36, "active_percent": 0.42, "table": {
    "herb_sungrass": 3, "herb_purple_lotus": 3, "herb_firebloom": 2, "herb_khadgar": 2,
    "ore_mithril": 3, "ore_truesilver": 2, "ore_thorium": 2,
    "wood_thornveil_stump": 5}}}


def fishing():
    from tools.build_fishing import FISH, window
    s_lo, s_hi = window(49, 51)
    fits = sorted([(fid, sk) for fid, _n, sk, _i, _d in FISH if s_lo <= sk <= s_hi], key=lambda f: -f[1])[:4]
    return {"slots": 8, "active_percent": 0.6, "table": {fid: 3 if n else 2 for n, (fid, _s) in enumerate(fits)}}


def build_loot(pools, roster, lift, prefix):
    from tools.build_durotar_content import make
    from entities.item_budget import budget_ratio, fit_to_curve
    out, rows = {}, []
    for who, items in pools.items():
        ilvl = roster[who][2] + lift
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
            d["item_id"] = prefix + kit_slug(name)
            r = budget_ratio(d)
            if r is not None and not 0.65 <= r <= 1.45:
                fit_to_curve(d)
            built.append(d)
            rows.append((name, slot, "weapon" if typ and typ[0] == "w" else "armor", typ[1] if typ else None,
                         template))
        out[who] = built
    return out, rows


def check(loot):
    import importlib
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    bad = []
    mod = importlib.import_module(f"tools.{MAP_MODULE}")
    declared = {s[0] for s in mod.SUBZONES}
    if set(TABLE["subzones"]) != declared:
        bad.append(f"subzones disagree with the map: {sorted(set(TABLE['subzones']) ^ declared)}")
    named = set(TABLE["open_zone"])
    if RARES & named:
        bad.append("a rare is in the open-zone table")
    for s in TABLE["subzones"].values():
        named |= set(s or {})
    if named != set(ROSTER) or set(POOLS) != RARES:
        bad.append(f"tables, roster and pools differ: {sorted(named ^ set(ROSTER))} {sorted(set(POOLS) ^ RARES)}")
    from tools import handbuilt_golem_vault as GV, handbuilt_storm_well as SW
    GV.build_golem_vault_baked()
    SW.build_storm_well_baked()
    if set(CAVE_FLOOR) != set(CAVE_ROSTER):
        bad.append(f"a cave creature with no floor: {sorted(set(CAVE_FLOOR) ^ set(CAVE_ROSTER))}")
    for mod, floor in ((GV, CAVE), (SW, CAVE2)):
        want = {n for n in CAVE_BOSSES if CAVE_FLOOR.get(n) == floor}
        if set(mod.BOSSES) != want:
            bad.append(f"{floor}'s bosses differ: map {sorted(mod.BOSSES)}, roster {sorted(want)}")
    if set(CAVE_POOLS) != CAVE_BOSSES:
        bad.append(f"the cave pools differ from the bosses: {sorted(set(CAVE_POOLS) ^ CAVE_BOSSES)}")
    existing = json.loads(CREATURES.read_text(encoding="utf-8"))["creatures"]
    for name, r in ALL.items():
        if not (ROOT / "assets/creatures" / f"{sprite(name)}.png").exists():
            bad.append(f"{name}'s sprite {sprite(name)} is not on disk")
        prev = existing.get(name)
        if prev and (prev.get("ability_kit") != kit_slug(name) or list(prev.get("level_range") or [])[:2] != list(r[1:3])):
            bad.append(f"{name} is already a different creature in creatures.json")
    names = [i["name"] for v in loot.values() for i in v]
    dup = [n for n, c in Counter(names).items() if c > 1]
    if dup:
        bad.append(f"duplicate item names: {dup}")
    import creature_sprites as CS
    for name, r in ALL.items():
        if CS.sprite_for(name, r[0]) != sprite(name):
            bad.append(f"creature_sprites.py draws {name} as {CS.sprite_for(name, r[0])}, not {sprite(name)}")
    return bad


def main():
    write_sprite_rules()
    import importlib
    import creature_sprites
    importlib.reload(creature_sprites)
    rare_loot, rows = build_loot(POOLS, ROSTER, 3, "cei_")
    cave_loot, crows = build_loot(CAVE_POOLS, CAVE_ROSTER, 2, "gvi_")
    bad = check({**rare_loot, **cave_loot}) + loot_audit(rows + crows)
    if "--dry" in sys.argv or bad:
        print("\n".join(bad) if bad else f"dry run clean: {len(ALL)} creatures, {len(RARES)} rares, "
                                         f"{len(CAVE_BOSSES)} cave bosses")
        return 1 if bad else 0
    creatures = {}
    for name, (template, lo, hi, mult, *_rest) in ALL.items():
        e = {"template": template, "level_range": [lo, hi], "is_boss": bool(mult), "ability_kit": kit_slug(name)}
        if mult:
            e["boss_multiplier"] = mult
        creatures[name] = e
    merge_json(CREATURES, "creatures", creatures, "creatures.json")
    merge_json(KITS, "kits", {kit_slug(n): kit(n) for n in ALL}, "ability_kits.json")
    raw = ENCOUNTERS.read_text(encoding="utf-8")
    enc = json.loads(raw)
    indent, newline = _detect_format(json.loads(raw), raw)
    entry = enc["zones"].setdefault(ZONE, {})
    entry["name"] = ZONE
    entry["open_zone"] = {"name": ZONE, "creatures": dict(TABLE["open_zone"])}
    entry["subzones"] = {s: ({"name": s, "safe": True, "creatures": {}} if c is None else
                             {"name": s, "creatures": dict(c)}) for s, c in TABLE["subzones"].items()}
    for floor in (CAVE, CAVE2):
        entry.setdefault("caves", {})[floor] = {"name": floor, "creatures": {
            n: (0 if r[3] else 4) for n, r in CAVE_ROSTER.items() if CAVE_FLOOR[n] == floor}}
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False) + ("\n" if newline else ""),
                          encoding="utf-8")
    np_path = ROOT / "data/gathering/node_pools.json"
    nd = json.loads(np_path.read_text(encoding="utf-8"))
    nodes = json.loads(json.dumps(NODES))
    nodes["celestial_expanse"]["fishing"] = fishing()
    nd["zones"].update(nodes)
    np_path.write_text(json.dumps(nd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = {"_notes": ("The Celestial Expanse's open-world rares (50-51). ONE item per kill from the rare's four; item_level = "
                      "the rare's level + 3. Hand-authored in tools/build_celestial_expanse_content.py.")}
    out.update(rare_loot)
    RARE_LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = {"_notes": ("Boss loot for the Golem Vault and the Storm-Well (under the Celestial Expanse's Golem Fields, "
                      "50-51). ONE item per "
                      "kill from the boss's four; item_level = boss level + 2. Hand-authored in "
                      "tools/build_celestial_expanse_content.py.")}
    out.update(cave_loot)
    CAVE_LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True, stdout=subprocess.DEVNULL)
    print(f"{len(ROSTER)} open-world creatures ({len(RARES)} rares), {len(CAVE_ROSTER)} in the cave "
          f"({len(CAVE_BOSSES)} bosses); {len(rows) + len(crows)} items; gathering and fishing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
