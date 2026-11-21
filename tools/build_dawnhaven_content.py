#!/usr/bin/env python3
"""Dawnhaven's creatures, rares, cave bosses, encounter tables, loot, gathering and fishing (1-9): Amberleaf Glade,
Duskfall Woods and their four caves. Idempotent.

    PYTHONPATH=. python3 tools/build_dawnhaven_content.py [--dry]

docs/dawnhaven_brief.md. Kyle, 21 Nov 2026, on what you fight: "Naga on the coast, Autumn wildlife, Elementals are fine
too - remnants of high elves (undead creatures)". Sprites are already in the game: Azshara's naga, ghosts, wyrm and
treant, the Plaguelands' Eversong lynx and mana wyrm, and stock beasts.

    AMBERLEAF GLADE (1-6)
      The Waking Shore        crabs on the beach                                     rare: Old Barnacle
      Leafwhisper Grove       boars and lynxes in the gold woods                     rare: Goldmane
      The Fallen Wardstones   mana wyrms on the broken wards, the woods walking
      Brinecoil Cove          the naga's landing
      The Silent Barrow       the outpost's dead
      Brinecoil Grotto (cave)                                               boss: Tidecaller Sszelith
      The Quiet Vault (cave)                                                boss: Warden Isilien
    DUSKFALL WOODS (5-9)
      The Red Hollow          prowlers, bears and the leafweaver spiders             rare: Ruddy, the Hollow King
      The Wildmana Thicket    the outpost's spilled magic, woken
      Saltspine Shore         the naga's camp
      The Withered Spires     the outpost's dead still keeping their posts           rare: The Grieving Lady
      Saltspine Hollow (cave)                                       bosses: Sea-Witch Ilthessa, Old Saltspine
      The Lightwell Deep (cave)                                     bosses: The Starved Light, Archivist Lorethas

THE NUMBERS are the start zones' (Deathknell's and the Valley's): a creature's basic hit 14 + 4 x its level, a rare's
or a boss's 30 + 7 x its level, rares at x1.8, cave bosses at x2.2 to x2.5; ONE item per kill from four, item level the
creature's level + 3 (+ 2 for cave bosses), primary stats only below item level 10.
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
from tools.build_tempest_openworld import enrage, stun  # noqa: E402

RARE_LOOT = ROOT / "data/loot/dawnhaven_rare_loot.json"
CAVE_LOOT = ROOT / "data/loot/dawnhaven_caves_boss_loot.json"
AL, DF = "Amberleaf Glade", "Duskfall Woods"
GROTTO, VAULT, HOLLOW, DEEP = "Brinecoil Grotto", "The Quiet Vault", "Saltspine Hollow", "The Lightwell Deep"


def T(level):
    return 14 + 4 * level


def B(level):
    return 30 + 7 * level


#: name -> (template, lo, hi, rare/boss multiplier or None, sprite, kit shape, school, [ability names])
ROSTER = {
    # ================================================================ AMBERLEAF GLADE
    "Tideshell Crab":       ("beast_basic", 1, 2, None, "az_shore_crab", "beast", "physical",
                             ["Pinch", "Sideways Snap", "Shell Grind"]),
    "Sunmane Boar":         ("beast_basic", 2, 3, None, "az_russet_boar", "beast", "physical",
                             ["Tusk", "Bristling Charge", "Gored"]),
    "Amberleaf Lynx":       ("beast_fast", 2, 4, None, "ps_eversong_lynx", "beast", "physical",
                             ["Rake", "Pounce From the Leaves", "Bleeding Scratch"]),
    "Ward-Drinker Wyrm":    ("elemental_caster", 2, 4, None, "ps_mana_wyrm", "caster", "arcane",
                             ["Arcane Spark", "Mana Burst", "Drained"]),
    "Amberwood Wanderer":   ("elemental_bruiser", 3, 5, None, "az_autumn_treant", "bruiser", "nature",
                             ["Branch Slam", "Storm of Leaves", "Rooted"]),
    "Brinecoil Scout":      ("humanoid_warrior", 3, 5, None, "az_naga_tidehunter", "warrior", "physical",
                             ["Trident Jab", "Tidal Lunge", "Scaled Hide"]),
    "Brinecoil Siren":      ("humanoid_caster", 4, 5, None, "az_naga_siren", "caster", "frost",
                             ["Frost Bolt", "Siren's Song", "Sea Chill"]),
    "Restless Sentinel":    ("undead_warrior", 4, 6, None, "ps_dead_elf_ranger", "warrior", "physical",
                             ["Spectral Blade", "Old Drill", "Unyielding"]),
    "Forlorn Spirit":       ("undead_caster", 4, 6, None, "az_ghost_tormented", "caster", "shadow",
                             ["Wail", "Grief Made Cold", "Haunting"]),
    "Old Barnacle":         ("beast_large", 3, 3, 1.8, "crab_giant_1", "rare", "physical",
                             ["Crushing Claw", "Shell Spin", "Clamped Fast", "Barnacled Fury"]),
    "Goldmane":             ("beast_fast", 4, 4, 1.8, "ps_eversong_lynx", "rare", "physical",
                             ["Golden Rake", "Leap From the Gold", "Pinned Down", "Hunter's Fury"]),
    # ================================================================ DUSKFALL WOODS
    "Duskfall Prowler":     ("beast_fast", 5, 7, None, "panther_3", "beast", "physical",
                             ["Claw", "Spring From the Dusk", "Torn Flank"]),
    "Hollow Bear":          ("beast_large", 6, 8, None, "bear_2", "bruiser", "physical",
                             ["Maul", "Heavy Swipe", "Knocked Flat"]),
    "Leafweaver Spider":    ("beast_fast", 5, 7, None, "spider_2", "beast", "nature",
                             ["Bite", "Silk Spray", "Leafweaver Venom"]),
    "Wildmana Sprite":      ("elemental_caster", 6, 8, None, "wisp_2", "caster", "arcane",
                             ["Wild Spark", "Spilled Light", "Mana-Sick"]),
    "Wildmana Elemental":   ("elemental_bruiser", 7, 8, None, "elemental_arcane", "bruiser", "arcane",
                             ["Arcane Fist", "Unbound Pulse", "Overcharged"]),
    "Saltspine Warrior":    ("humanoid_warrior", 6, 8, None, "naga_myrmidon_1", "warrior", "physical",
                             ["Saltspine Blade", "Coiling Strike", "Hardened Scales"]),
    "Saltspine Siren":      ("humanoid_caster", 7, 8, None, "az_naga_siren", "caster", "frost",
                             ["Frost Bolt", "Drowning Song", "Deep Chill"]),
    "Unresting Guardian":   ("undead_warrior", 7, 9, None, "az_ghost_guard", "warrior", "physical",
                             ["Guardian's Blade", "Shield of the Dead", "Still on Watch"]),
    "Withered Magister":    ("undead_caster", 7, 9, None, "az_ghost_arcanist", "caster", "arcane",
                             ["Fading Bolt", "Arcane Echo", "Withering"]),
    "Ruddy, the Hollow King": ("beast_large", 8, 8, 1.8, "bear_5", "rare", "physical",
                               ["Crown of Claws", "Hollow Roar", "Bowled Over", "King's Rage"]),
    "The Grieving Lady":    ("undead_caster", 8, 8, 1.8, "az_ghost_handmaiden", "rare", "shadow",
                             ["Sorrow", "The Long Lament", "Heart Stopped", "Grief Undying"]),
}
RARES = {n for n, r in ROSTER.items() if r[3]}

#: cave -> {name: row}; trash rolls from the cave's table, bosses are pinned by tools/handbuilt_dawnhaven_caves.py
CAVE_ROSTERS = {
    GROTTO: {
        "Brinecoil Raider":     ("humanoid_warrior", 3, 5, None, "naga_warrior", "warrior", "physical",
                                 ["Barbed Spear", "Raider's Rush", "Wet Scales"]),
        "Brinecoil Priestess":  ("humanoid_caster", 4, 5, None, "fe_naga_priestess", "caster", "frost",
                                 ["Tide Bolt", "Undertow", "Brine Chill"]),
        "Grotto Crab":          ("beast_basic", 3, 4, None, "wt_reef_crab", "beast", "physical",
                                 ["Snip", "Scuttle", "Grinding Claw"]),
        "Tidecaller Sszelith":  ("humanoid_caster", 5, 5, 2.3, "az_naga_siren", "boss", "frost",
                                 ["Tide's Call", "Crashing Wave", "The Undertow Takes You", "Spray of the Deep"]),
    },
    VAULT: {
        "Vault Wraith":         ("undead_caster", 5, 6, None, "wraith_1", "caster", "shadow",
                                 ["Grave Touch", "Wail in the Dark", "Cold Breath"]),
        "Bone-Bound Guard":     ("undead_warrior", 5, 6, None, "az_ghost_guard", "warrior", "physical",
                                 ["Rusted Blade", "Guard the Dead", "Bound Bones"]),
        "Ossuary Shade":        ("undead_basic", 5, 6, None, "spectre_1", "beast", "shadow",
                                 ["Shadow Claw", "Flicker", "Shade's Chill"]),
        "Warden Isilien":       ("undead_caster", 6, 6, 2.4, "banshee", "boss", "shadow",
                                 ["Warden's Lament", "Seal of the Dead", "Bound to the Vault", "Keening"]),
    },
    HOLLOW: {
        "Saltspine Myrmidon":   ("humanoid_warrior", 7, 9, None, "naga_myrmidon_2", "warrior", "physical",
                                 ["Myrmidon's Blade", "Crushing Coil", "Scale Guard"]),
        "Saltspine Tidecaller": ("humanoid_caster", 7, 8, None, "fe_naga_priestess", "caster", "frost",
                                 ["Brine Bolt", "Rising Tide", "Salt Sting"]),
        "Hollow Crab":          ("beast_basic", 7, 8, None, "crab_giant_1", "beast", "physical",
                                 ["Claw", "Shell Charge", "Pincered"]),
        "Sea-Witch Ilthessa":   ("humanoid_caster", 9, 9, 2.4, "az_naga_sea_witch", "boss", "frost",
                                 ["Witch's Tide", "Black Water", "Drowned in Salt", "The Sea Answers"]),
        "Old Saltspine":        ("beast_large", 8, 8, 2.2, "crab_giant_2", "boss", "physical",
                                 ["Great Claw", "Shell Quake", "Dragged Under", "Snapping Frenzy"]),
    },
    DEEP: {
        "Hungering Remnant":    ("elemental_caster", 8, 9, None, "ps_arcane_remnant", "caster", "arcane",
                                 ["Starved Bolt", "Drain the Light", "Hollowed"]),
        "Mana-Starved Wyrm":    ("elemental_caster", 8, 9, None, "az_mana_wyrm_leader", "caster", "arcane",
                                 ["Arcane Bite", "Mana Lash", "Siphoned"]),
        "Lorebound Shade":      ("undead_caster", 8, 9, None, "scholo_ghost_servant", "caster", "shadow",
                                 ["Faded Word", "Recitation", "Lost Page"]),
        "The Starved Light":    ("elemental_caster", 9, 9, 2.5, "dw_arcane_anomaly", "boss", "arcane",
                                 ["Hungering Ray", "Devour the Light", "Darkness Where It Fed", "Starburst"]),
        "Archivist Lorethas":   ("undead_caster", 9, 9, 2.3, "az_ghost_noble", "boss", "arcane",
                                 ["Archivist's Bolt", "Words Unwritten", "Bound in Ink", "Last Entry"]),
    },
}
CAVE_ROSTER = {n: r for d in CAVE_ROSTERS.values() for n, r in d.items()}
CAVE_BOSSES = {n for n, r in CAVE_ROSTER.items() if r[3]}
ALL = {**ROSTER, **CAVE_ROSTER}


def sprite(name):
    return ALL[name][4]


RULES_START = "    # DAWNHAVEN (generated by tools/build_dawnhaven_content.py; do not edit by hand)\n"
RULES_END = "    # END DAWNHAVEN\n"


def write_sprite_rules():
    path = ROOT / "creature_sprites.py"
    s = path.read_text(encoding="utf-8")
    block = RULES_START + "".join(f'    (r"^{re.escape(n.lower())}$", "{sprite(n)}"),\n' for n in ALL) + RULES_END
    if RULES_START in s:
        a = s.index(RULES_START)
        b = s.index(RULES_END) + len(RULES_END)
        s = s[:a] + block + s[b:]
    else:
        anchor = "    # THE LOWER BOUGHS (generated by tools/build_lower_boughs_content.py; do not edit by hand)\n"
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
                dot(names[2], max(2, int(t * 0.27)), 3, 3, school=s,
                    **({"dispel_type": dispel} if s != "physical" else {}))]
    if shape == "warrior":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.86), cooldown=3, school=s),
                buff(names[2], 6, 3, {"armor": 12 * hi})]
    if shape == "caster":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.84), cooldown=5, school=s, is_aoe=True),
                dot(names[2], max(2, int(t * 0.27)), 3, 3, school=s, dispel_type=dispel)]
    if shape == "bruiser":
        return [dmg(names[0], t + 4, school=s), dmg(names[1], int(t * 0.84), cooldown=4, school=s, is_aoe=True),
                debuff(names[2], 5, 2, {"dodge_rating": -(4 + 2 * hi)}, school=s)]
    b = B(hi)
    if shape == "boss":
        # a start-zone cave boss: a hard hit, a party hit, a dangerous one with a tell, a lingering one, a last stand
        return [dmg(names[0], b, school=s), dmg(names[1], int(b * 1.25), cooldown=4, school=s),
                dmg(names[3], int(b * 0.7), cooldown=5, school=s, is_aoe=True),
                stun(names[2], int(b * 0.9), cooldown=6, school=s),
                dot(f"{names[1]}, Lingering", int(b * 0.35), 5, 4, school=s, dispel_type=dispel),
                dict(name="Last Stand", kind="buff", amount=0, cooldown=99, mana_cost=0, school=s, duration=30,
                     self_only=True, hp_below=0.3, stat_mods={"attack_power": int(b * 0.3)})]
    # an open-world rare: a heavy basic, a party hit, a stun, and its last stand
    return [dmg(names[0], b, school=s), dmg(names[1], int(b * 0.8), cooldown=4, school=s, is_aoe=True),
            stun(names[2], int(b * 0.8), cooldown=5, school=s), enrage(names[3], int(b * 0.15), s)]


TABLES = {
    AL: {
        "open_zone": {"Amberleaf Lynx": 3, "Sunmane Boar": 3, "Tideshell Crab": 1},
        "subzones": {
            "The Waking Shore": {"Tideshell Crab": 6, "Old Barnacle": 0},
            "Amberwatch": None,
            "Leafwhisper Grove": {"Sunmane Boar": 5, "Amberleaf Lynx": 4, "Goldmane": 0},
            "Amberleaf Mere": {"Sunmane Boar": 3, "Amberleaf Lynx": 3, "Ward-Drinker Wyrm": 2},
            "The Fallen Wardstones": {"Ward-Drinker Wyrm": 6, "Amberwood Wanderer": 4},
            "Brinecoil Cove": {"Brinecoil Scout": 5, "Brinecoil Siren": 3, "Tideshell Crab": 2},
            "The Silent Barrow": {"Restless Sentinel": 5, "Forlorn Spirit": 4},
            "The Duskfall Road": {"Amberleaf Lynx": 3, "Amberwood Wanderer": 3, "Forlorn Spirit": 1},
        },
    },
    DF: {
        "open_zone": {"Duskfall Prowler": 3, "Leafweaver Spider": 3},
        "subzones": {
            "Dawnrest": None,
            "The Red Hollow": {"Duskfall Prowler": 4, "Hollow Bear": 4, "Leafweaver Spider": 4,
                               "Ruddy, the Hollow King": 0},
            "Duskmere": {"Leafweaver Spider": 3, "Duskfall Prowler": 3, "Wildmana Sprite": 2},
            "The Wildmana Thicket": {"Wildmana Sprite": 5, "Wildmana Elemental": 4},
            "Saltspine Shore": {"Saltspine Warrior": 5, "Saltspine Siren": 4},
            "The Withered Spires": {"Unresting Guardian": 5, "Withered Magister": 4, "The Grieving Lady": 0},
            "The Lightwell Court": {"Unresting Guardian": 4, "Withered Magister": 4, "Wildmana Sprite": 1},
            "The Spire Road": {"Duskfall Prowler": 3, "Hollow Bear": 2, "Wildmana Sprite": 1},
        },
    },
}
CAVE_PARENT = {GROTTO: AL, VAULT: AL, HOLLOW: DF, DEEP: DF}

#: rare or boss -> four (name, slot, suffix, (a|w, type) or None, template)
POOLS = {
    "Old Barnacle": [
        ("Barnacled Shell Buckler", "off_hand", "of Stamina", ("w", "shield"), "str_physical"),
        ("Tidepool Waders", "feet", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Brine-Washed Cord", "waist", "of the Owl", ("a", "cloth"), "spi_healer"),
        ("Crab-Claw Cudgel", "main_hand", "of the Bear", ("w", "mace_1h"), "str_physical")],
    "Goldmane": [
        ("Goldmane Pelt Cloak", "back", "of Agility", None, "agi_physical"),
        ("Lynx-Fang Dirk", "main_hand", "of the Tiger", ("w", "dagger"), "agi_physical"),
        ("Gold-Furred Gloves", "hands", "of the Eagle", ("a", "mail"), "str_int_hybrid"),
        ("Leafwhisper Circlet", "head", "of Intellect", ("a", "cloth"), "int_caster")],
    "Ruddy, the Hollow King": [
        ("Hollow King's Mantle", "shoulder", "of the Bear", ("a", "plate"), "str_physical"),
        ("Bear-Hide Jerkin", "chest", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Ruddy's Claw Necklace", "neck", "of the Wolf", None, "agi_int_hybrid"),
        ("Redwood Greatclub", "two_hand", "of Strength", ("w", "mace_2h"), "str_physical")],
    "The Grieving Lady": [
        ("Veil of the Grieving Lady", "head", "of the Owl", ("a", "cloth"), "spi_healer"),
        ("Lament Wand", "ranged", "of Intellect", ("w", "wand"), "int_caster"),
        ("Mourning Band", "ring", "of Spirit", None, "spi_healer"),
        ("Black-Ribbon Wristguards", "wrist", "of the Eagle", ("a", "mail"), "str_int_hybrid")],
}
CAVE_POOLS = {
    "Tidecaller Sszelith": [
        ("Tidecaller's Coral Rod", "main_hand", "of Intellect", ("w", "mace_1h"), "int_caster"),
        ("Brinecoil Scale Vest", "chest", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Kelp-Woven Sandals", "feet", "of the Owl", ("a", "cloth"), "spi_healer"),
        ("Grotto Harpoon", "two_hand", "of the Tiger", ("w", "polearm"), "agi_physical")],
    "Warden Isilien": [
        ("Warden's Vault Key", "neck", "of Stamina", None, "str_physical"),
        ("Cloister Robe", "chest", "of Spirit", ("a", "cloth"), "spi_healer"),
        ("Sentinel's Old Greaves", "legs", "of the Bear", ("a", "plate"), "str_physical"),
        ("Isilien's Moonbow", "ranged", "of Agility", ("w", "bow"), "agi_physical")],
    "Sea-Witch Ilthessa": [
        ("Sea-Witch's Coral Crown", "head", "of the Eagle", ("a", "mail"), "str_int_hybrid"),
        ("Saltspine Trident", "two_hand", "of Strength", ("w", "polearm"), "str_physical"),
        ("Black Water Wraps", "wrist", "of Intellect", ("a", "cloth"), "int_caster"),
        ("Tide-Pearl Ring", "ring", "of the Owl", None, "spi_healer")],
    "Old Saltspine": [
        ("Saltspine Shell Spaulders", "shoulder", "of Stamina", ("a", "plate"), "str_physical"),
        ("Crab-Shell Bracers", "wrist", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Barnacle-Crusted Belt", "waist", "of the Boar", ("a", "mail"), "str_int_hybrid"),
        ("Great Claw Knuckles", "main_hand", "of the Tiger", ("w", "fist_weapon"), "agi_physical")],
    "The Starved Light": [
        ("Shard of the Lightwell", "off_hand", "of Intellect", ("w", "tome"), "int_caster"),
        ("Robe of the Rekindled Font", "chest", "of the Owl", ("a", "cloth"), "spi_healer"),
        ("Lightwarden's Gauntlets", "hands", "of Strength", ("a", "plate"), "str_physical"),
        ("Hungerless Blade", "main_hand", "of Agility", ("w", "sword_1h"), "agi_physical")],
    "Archivist Lorethas": [
        ("Archivist's Last Ledger", "off_hand", "of Spirit", ("w", "tome"), "spi_healer"),
        ("Inkstained Leggings", "legs", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Underworks Hauberk", "chest", "of the Eagle", ("a", "mail"), "str_int_hybrid"),
        ("Lorethas's Quill-Staff", "two_hand", "of Intellect", ("w", "staff"), "int_caster")],
}

#: gathering at 1-9: the start zones' herbs, copper in the stones, ashwood and oakheart in the woods (mageroyal and tin
#: are skill 50 and 65, past a 5-9 zone's window, so Duskfall has more of the first herbs and copper instead)
NODES = {
    "amberleaf_glade": {"slots": 14, "active_percent": 0.5, "table": {
        "herb_peacebloom": 3, "herb_silverleaf": 3, "herb_earthroot": 2, "ore_copper": 3, "ore_weakstone": 2,
        "wood_ashwood": 2, "wood_oakheart_stump": 1}},
    "duskfall_woods": {"slots": 16, "active_percent": 0.48, "table": {
        "herb_peacebloom": 3, "herb_silverleaf": 3, "herb_earthroot": 4, "ore_copper": 4, "ore_weakstone": 1,
        "wood_ashwood": 2, "wood_oakheart_stump": 2}},
}


def fishing(lo, hi):
    from tools.build_fishing import FISH, window
    s_lo, s_hi = window(lo, hi)
    fits = sorted([(fid, sk) for fid, _n, sk, _i, _d in FISH if s_lo <= sk <= s_hi], key=lambda f: f[1])[:4]
    return {"slots": 5, "active_percent": 0.6, "table": {fid: 3 if n else 2 for n, (fid, _s) in enumerate(fits)}}


def build_loot(pools, roster, lift, prefix):
    from tools.build_deathknell_content import mk
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
            d = mk(name, slot, suffix, ilvl, "", **kw)
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
    for zone, mod in ((AL, "handbuilt_dawnhaven_amberleaf"), (DF, "handbuilt_dawnhaven_duskfall")):
        m = importlib.import_module(f"tools.{mod}")
        declared = {s[0] for s in m.SUBZONES}
        if set(TABLES[zone]["subzones"]) != declared:
            bad.append(f"{zone}: subzones disagree with the map: {sorted(set(TABLES[zone]['subzones']) ^ declared)}")
        if RARES & set(TABLES[zone]["open_zone"]):
            bad.append(f"{zone}: a rare is in the open-zone table")
    named = set()
    for z in TABLES.values():
        named |= set(z["open_zone"])
        for s in z["subzones"].values():
            named |= set(s or {})
    if named != set(ROSTER) or set(POOLS) != RARES:
        bad.append(f"tables, roster and pools differ: {sorted(named ^ set(ROSTER))} {sorted(set(POOLS) ^ RARES)}")
    from tools import handbuilt_dawnhaven_caves as DC
    for cave in DC.CAVES:
        DC.build(cave)
        want = {n for n, r in CAVE_ROSTERS[cave].items() if r[3]}
        if set(DC.BOSSES[cave]) != want:
            bad.append(f"{cave}'s bosses differ: map {sorted(DC.BOSSES[cave])}, roster {sorted(want)}")
    if set(CAVE_POOLS) != CAVE_BOSSES:
        bad.append(f"cave pools and bosses differ: {sorted(set(CAVE_POOLS) ^ CAVE_BOSSES)}")
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
    rare_loot, rows = build_loot(POOLS, ROSTER, 3, "dhi_")
    cave_loot, crows = build_loot(CAVE_POOLS, CAVE_ROSTER, 2, "dhc_")
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
    for zone, table in TABLES.items():
        entry = enc["zones"].setdefault(zone, {})
        entry["name"] = zone
        entry["open_zone"] = {"name": zone, "creatures": dict(table["open_zone"])}
        entry["subzones"] = {s: ({"name": s, "safe": True, "creatures": {}} if c is None else
                                 {"name": s, "creatures": dict(c)}) for s, c in table["subzones"].items()}
        entry["caves"] = {}
    for cave, roster in CAVE_ROSTERS.items():
        enc["zones"][CAVE_PARENT[cave]]["caves"][cave] = {
            "name": cave, "creatures": {n: (0 if r[3] else 4) for n, r in roster.items()}}
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False) + ("\n" if newline else ""),
                          encoding="utf-8")
    np_path = ROOT / "data/gathering/node_pools.json"
    nd = json.loads(np_path.read_text(encoding="utf-8"))
    nodes = json.loads(json.dumps(NODES))
    nodes["amberleaf_glade"]["fishing"] = fishing(1, 6)
    nodes["duskfall_woods"]["fishing"] = fishing(5, 9)
    nd["zones"].update(nodes)
    np_path.write_text(json.dumps(nd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = {"_notes": ("Dawnhaven's open-world rares (1-9). ONE item per kill from the rare's four; item_level = the "
                      "rare's level + 3. Hand-authored in tools/build_dawnhaven_content.py.")}
    out.update(rare_loot)
    RARE_LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = {"_notes": ("Boss loot for Dawnhaven's four caves. ONE item per kill from the boss's four; item_level = boss "
                      "level + 2. Hand-authored in tools/build_dawnhaven_content.py.")}
    out.update(cave_loot)
    CAVE_LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True, stdout=subprocess.DEVNULL)
    print(f"{len(ROSTER)} open-world creatures ({len(RARES)} rares), {len(CAVE_ROSTER)} in the caves "
          f"({len(CAVE_BOSSES)} bosses); {len(rows) + len(crows)} items; gathering and fishing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
