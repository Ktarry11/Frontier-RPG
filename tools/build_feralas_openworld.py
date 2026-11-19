#!/usr/bin/env python3
"""Feralas's open-world creatures, rares, encounter tables, rare loot and gathering. Idempotent.

    PYTHONPATH=. python3 tools/build_feralas_openworld.py

docs/feralas_brief.md. Kyle, 19 Nov 2026: three maps, east arm first, and the peoples he kept: the Gordunni ogres, the
Woodpaw gnolls, the naga of the coast, the giants of the Twin Colossals, plus the wildlife and the Grimtotem. Sprites
are Kyle's Feralas creature sheet (docs/feralas_art_prompts.md sheet 7, the fe_* sprites), with Stonetalon's
Grimtotem, the old sprite darter, stag, crocolisk and hyena art filling out the rest.

WAITING ON THE ART AND THE MAPS: check() wants every sprite on disk and the three map modules
(tools/handbuilt_feralas_{high_wilderness,forgotten_coast,twin_colossals}.py) declaring the same subzones. Nothing is
written until both are in.

    THE HIGH WILDERNESS (44-46), the east arm
      The Aspen Descent       where the Rockies come down: wolves, stags, sprite darters
      Woodpaw Hills           the Woodpaw gnolls                                    rare: Grimfang
      The Lower Wilds         the river marsh: crocolisks and ironfur bears         rare: Old Grizzlegut
      Grimtotem Compound      the Grimtotem who moved on the tauren's ground        rare: Pathfinder Harrok
      Gordunni Outpost        the ogres' forward camp
      The Gate of Dire Maul   the ogres holding the gate                            rare: Gash'tok the Gatekeeper
      The Hive Fields         where the dig breaks the surface: the Zukk'ash
    THE FORGOTTEN COAST (46-48), the corner and the south coast
      The Fog Groves          the grafted rainforest: elk, bears, stalkers          rare: Old Seven-Point
      Cedar Hollow            the settlers                                          safe
      Feathermoon Landing     the Sentinels' pier                                   safe
      Ruins of Isildien       the Gordunni digging in the Highborne dome            rare: Skull-Taker Murg
      The Hatecrest Shore     the naga's beaches
      Sardor Isle             the naga's island                                     rare: Tidelord Ssaravel
      The Isle of Dread       the chimaeras' island                                 rare: the Dread Matriarch
      Frayfeather Highlands   the hippogryphs                                       rare: Antilus the Soarer
    THE TWIN COLOSSALS (47-49), the north coast
      The Twin Colossals      the giants walking the arches                         rare: the Old Walker
      Rage Scar Hold          the yetis                                             rare: Rage Scar Old Bull
      Ruins of Ravenwind      the naga's second foothold                            rare: Lady Szaressa
      The Dream Bough         the tree whose roots reach into the Dream
      The Sentinels' Watch    the quest camp                                        safe

THE NUMBERS follow the 40s open world: trash basic 4L - 10, a rare's 10L - 200 at boss multiplier 2.2 (world/difficulty
then scales a rare by its own row). Rares sit in subzone tables at weight 0, one item from four, item level = the
rare's level + 3.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_return_voyage_content import (  # noqa: E402
    CREATURES, KITS, ENCOUNTERS, kit_slug, merge_json, _detect_format, dmg, dot, debuff, buff, loot_audit)
from tools.build_tempest_openworld import enrage, stun, shield  # noqa: E402

LOOT = ROOT / "data/loot/feralas_rare_loot.json"
HW, FC, TC = "The High Wilderness", "The Forgotten Coast", "The Twin Colossals"
MAP_MODULES = {HW: "handbuilt_feralas_high_wilderness", FC: "handbuilt_feralas_forgotten_coast",
               TC: "handbuilt_feralas_twin_colossals"}


def T(level):
    return 4 * level - 10


def B(level):
    return 10 * level - 200


#: name -> (template, lo, hi, rare multiplier or None, sprite, kit shape, school, [three ability names])
ROSTER = {
    # ---------------------------------------------------------------- The High Wilderness
    "Longtooth Runner":      ("beast_fast", 44, 45, None, "fe_longtooth_wolf", "beast", "physical",
                              ["Bite", "Run Down", "Hamstring"]),
    "Feralas Stag":          ("beast_basic", 44, 45, None, "stag", "warrior", "physical",
                              ["Antler Gore", "Rearing Kick", "Bracing Stance"]),
    "Feralas Sprite Darter": ("beast_fast", 44, 46, None, "sprite_darter", "caster", "arcane",
                              ["Arcane Spark", "Faerie Dazzle", "Mana Nip"]),
    "Woodpaw Reaver":        ("humanoid_warrior", 44, 45, None, "fe_woodpaw_reaver", "warrior", "physical",
                              ["Hack", "Savage Chop", "Hide Armour"]),
    "Woodpaw Trapper":       ("humanoid_ranged", 44, 45, None, "fe_woodpaw_trapper", "beast", "physical",
                              ["Thrown Hatchet", "Snare Net", "Jagged Trap"]),
    "Woodpaw Mystic":        ("humanoid_caster", 44, 45, None, "fe_woodpaw_mystic", "caster", "nature",
                              ["Bone Rattle Bolt", "Howl of the Pack", "Mangy Curse"]),
    "Woodpaw Brute":         ("humanoid_warrior", 45, 45, None, "fe_woodpaw_brute", "bruiser", "physical",
                              ["Log Shield Bash", "Pack Swing", "Battered"]),
    "Woodpaw Hyena":         ("beast_fast", 44, 45, None, "fe_hyena", "beast", "physical",
                              ["Bite", "Cackling Lunge", "Infected Bite"]),
    "Lower Wilds Crocolisk": ("beast_large", 45, 46, None, "crocolisk_2", "bruiser", "physical",
                              ["Snap", "Death Roll", "Muddied"]),
    "Ironfur Bear":          ("beast_large", 45, 46, None, "fe_ironfur_bear", "warrior", "physical",
                              ["Maul", "Swipe", "Thick Hide"]),
    "Grimtotem Usurper":     ("humanoid_warrior", 45, 46, None, "st_grim_warrior", "warrior", "physical",
                              ["Halberd Chop", "Trample", "Usurper's Hide"]),
    "Grimtotem Bonecaller":  ("humanoid_caster", 45, 46, None, "st_grim_shaman", "caster", "nature",
                              ["Lightning Bolt", "Chain Lightning", "Bonecaller's Hex"]),
    "Grimtotem Earthbreaker": ("humanoid_warrior", 46, 46, None, "st_grim_brute", "bruiser", "physical",
                               ["Earthbreaker Maul", "War Stomp", "Cracked Ground"]),
    "Grimtotem Pathfinder":  ("humanoid_ranged", 45, 46, None, "st_grim_hunter", "beast", "physical",
                              ["Spear Throw", "Pinning Throw", "Barbed Spear"]),
    "Gordunni Brute":        ("humanoid_warrior", 45, 46, None, "fe_gordunni_brute", "bruiser", "physical",
                              ["Tree-Trunk Club", "Ground Slam", "Dazed"]),
    "Gordunni Ogre Mage":    ("humanoid_caster", 45, 46, None, "fe_gordunni_mage", "caster", "fire",
                              ["Fireball", "Two-Headed Argument", "Burning"]),
    "Gordunni Shaman":       ("humanoid_caster", 45, 46, None, "fe_gordunni_shaman", "caster", "nature",
                              ["Skull Totem Bolt", "Bloodlust Howl", "Gordunni Curse"]),
    "Gordunni Mauler":       ("humanoid_warrior", 46, 46, None, "fe_gordunni_mauler", "bruiser", "physical",
                              ["Iron Knuckles", "Pound", "Battered Senseless"]),
    "Gordunni Warlord":      ("humanoid_warrior", 46, 46, None, "fe_gordunni_warlord", "warrior", "physical",
                              ["Great Axe", "Cleaving Swing", "Looted Plate"]),
    "Zukk'ash Tunneler":     ("vermin_swarm", 45, 46, None, "fe_silithid_tunneler", "warrior", "physical",
                              ["Digging Claw", "Burrow Strike", "Chitin Plates"]),
    "Zukk'ash Swarmer":      ("vermin_swarm", 45, 46, None, "fe_silithid_swarmer", "beast", "nature",
                              ["Sting", "Swarm", "Venom"]),
    "Grimfang":              ("humanoid_warrior", 46, 46, 2.2, "fe_woodpaw_alpha", "rare", "physical",
                              ["Spiked Club", "Alpha's Howl", "Pinned Down", "Pack Fury"]),
    "Old Grizzlegut":        ("beast_large", 46, 46, 2.2, "fe_ironfur_bear", "rare", "physical",
                              ["Grizzled Maul", "Roar", "Bear Hug", "Old Fury"]),
    "Pathfinder Harrok":     ("humanoid_warrior", 46, 46, 2.2, "st_grim_elder", "rare", "nature",
                              ["Stolen Totem Strike", "Earthshock Wave", "Rooted", "Grimtotem Pride"]),
    "Gash'tok the Gatekeeper": ("humanoid_warrior", 46, 46, 2.2, "fe_gordunni_lord", "rare", "physical",
                                ["Gatekeeper's Cudgel", "Shake the Gate", "Stomped Flat", "Nobody Gets In"]),
    # ---------------------------------------------------------------- The Forgotten Coast
    "Fog Grove Elk":         ("beast_large", 46, 47, None, "fe_roosevelt_elk", "warrior", "physical",
                              ["Antler Rake", "Charge", "Bull's Stand"]),
    "Feralas Stalker":       ("beast_fast", 46, 47, None, "fe_feralas_stalker", "beast", "physical",
                              ["Claw", "Pounce", "Rend"]),
    "Fog Grove Ironfur":     ("beast_large", 46, 47, None, "fe_ironfur_bear", "warrior", "physical",
                              ["Maul", "Swipe", "Thick Hide"]),
    "Isildien Brute":        ("humanoid_warrior", 46, 47, None, "fe_gordunni_brute", "bruiser", "physical",
                              ["Marble Club", "Ground Slam", "Dazed"]),
    "Isildien Ogre Mage":    ("humanoid_caster", 47, 47, None, "fe_gordunni_mage", "caster", "arcane",
                              ["Stolen Arcane Bolt", "Two-Headed Argument", "Highborne Hex"]),
    "Isildien Digger":       ("humanoid_warrior", 46, 47, None, "fe_gordunni_brute", "warrior", "physical",
                              ["Shovel", "Rubble Throw", "Dig In"]),
    "Hatecrest Raider":      ("humanoid_warrior", 46, 47, None, "fe_naga_raider", "warrior", "physical",
                              ["Barbed Harpoon", "Haul In", "Scaled Hide"]),
    "Hatecrest Ruin-Digger": ("humanoid_warrior", 46, 47, None, "fe_naga_digger", "beast", "physical",
                              ["Pick Strike", "Thrown Relic", "Gouge"]),
    "Hatecrest Tide Priestess": ("humanoid_caster", 47, 47, None, "fe_naga_priestess", "caster", "frost",
                                 ["Tide Bolt", "Breaking Wave", "Chilling Brine"]),
    "Hatecrest Makrura":     ("aquatic_basic", 46, 47, None, "fe_makrura", "warrior", "physical",
                              ["Claw", "Tail Snap", "Shell Up"]),
    "Hatecrest Coral Guardian": ("humanoid_warrior", 47, 48, None, "fe_naga_guardian", "warrior", "physical",
                                 ["Coral Spear", "Shield Slam", "Coral Hide"]),
    "Sardor Hydra":          ("beast_large", 47, 48, None, "fe_coast_hydra", "bruiser", "nature",
                              ["Three Bites", "Thrashing Heads", "Hydra Venom"]),
    "Dread Chimaera":        ("beast_large", 47, 48, None, "fe_chimaera", "caster", "nature",
                              ["Twin Bite", "Acid Breath", "Lightning Spit"]),
    "Frayfeather Skystalker": ("beast_fast", 46, 47, None, "fe_skystalker", "beast", "physical",
                               ["Talon", "Dive", "Raking Claws"]),
    "Frayfeather Windwing":  ("beast_fast", 47, 47, None, "fe_windwing", "beast", "nature",
                              ["Beak Stab", "Gust", "Torn Wing"]),
    "Old Seven-Point":       ("beast_large", 47, 47, 2.2, "fe_roosevelt_elk", "rare", "physical",
                              ["Seven-Point Gore", "Bugle", "Pinned to a Cedar", "Rut"]),
    "Skull-Taker Murg":      ("humanoid_warrior", 47, 47, 2.2, "fe_gordunni_warlord", "rare", "physical",
                              ["Trophy Axe", "Skull Toss", "Murg's Grip", "Skull-Taker's Rage"]),
    "Tidelord Ssaravel":     ("humanoid_caster", 48, 48, 2.2, "fe_naga_priestess", "rare", "frost",
                              ["Tidal Lance", "The Isle Floods", "Dragged Under", "Sardor's Ward"]),
    "The Dread Matriarch":   ("beast_large", 48, 48, 2.2, "fe_chimaera_matriarch", "rare", "nature",
                              ["Matriarch's Bite", "Venom Breath", "Wing Pin", "Nest Fury"]),
    "Antilus the Soarer":    ("beast_fast", 48, 48, 2.2, "fe_skystalker", "rare", "physical",
                              ["Soaring Talon", "Stoop", "Carried Off", "Highland Fury"]),
    # ---------------------------------------------------------------- The Twin Colossals
    "Colossal Land Walker":  ("elemental_bruiser", 48, 49, None, "fe_forest_giant", "bruiser", "nature",
                              ["Granite Fist", "Earthquake Step", "Moss-Grown"]),
    "Colossal Sea Walker":   ("elemental_bruiser", 48, 49, None, "fe_sea_giant", "bruiser", "frost",
                              ["Barnacled Fist", "Wave Stomp", "Sea-Soaked"]),
    "Rage Scar Yeti":        ("beast_large", 47, 48, None, "fe_rage_scar_yeti", "warrior", "physical",
                              ["Pummel", "Hurl", "Shaggy Hide"]),
    "Rage Scar Matriarch":   ("beast_large", 48, 48, None, "fe_rage_scar_matriarch", "bruiser", "physical",
                              ["Crushing Pummel", "Bellow", "Fury of the Hold"]),
    "Ravenwind Raider":      ("humanoid_warrior", 47, 48, None, "fe_naga_raider", "warrior", "physical",
                              ["Barbed Harpoon", "Haul In", "Scaled Hide"]),
    "Ravenwind Sea Witch":   ("humanoid_caster", 48, 49, None, "fe_naga_priestess", "caster", "frost",
                              ["Frost Bolt", "Cold Surge", "Siren's Chill"]),
    "Ravenwind Guardian":    ("humanoid_warrior", 48, 49, None, "fe_naga_guardian", "warrior", "physical",
                              ["Coral Halberd", "Shield Slam", "Coral Hide"]),
    "Ravenwind Hydra":       ("beast_large", 48, 49, None, "fe_coast_hydra", "bruiser", "nature",
                              ["Three Bites", "Thrashing Heads", "Hydra Venom"]),
    "Dream Bough Darter":    ("beast_fast", 47, 48, None, "sprite_darter", "caster", "nature",
                              ["Dream Spark", "Faerie Dazzle", "Drowsy"]),
    "Dream-Touched Treant":  ("elemental_bruiser", 48, 49, None, "treant_2", "bruiser", "nature",
                              ["Branch Slam", "Dream Pollen", "Rooted"]),
    "The Old Walker":        ("elemental_bruiser", 49, 49, 2.2, "fe_forest_giant", "rare", "nature",
                              ["Mountain's Fist", "The Ground Shakes", "Pinned Under Stone", "Ten Thousand Years"]),
    "Rage Scar Old Bull":    ("beast_large", 49, 49, 2.2, "fe_rage_scar_matriarch", "rare", "physical",
                              ["Old Bull's Pummel", "Bellow", "Hurled Against Rock", "Last Rage"]),
    "Lady Szaressa":         ("humanoid_caster", 49, 49, 2.2, "fe_naga_priestess", "rare", "frost",
                              ["Frost Lance", "Ravenwind Tide", "Drowning Grip", "Szaressa's Ward"]),
}
RARES = {n for n, r in ROSTER.items() if r[3]}

#: BUILT BEFORE THE ART (Kyle, 19 Nov 2026: "Build without art for now"). Until a fe_* sprite from Kyle's Feralas
#: creature sheet is on disk, its creature draws as the nearest thing already in the game. Slice the sheet, re-run
#: this script, and every creature picks up its own sprite with no other change.
PLACEHOLDER = {
    "fe_longtooth_wolf": "ps_dire_wolf", "fe_woodpaw_reaver": "gnoll_1", "fe_woodpaw_trapper": "gnoll_2",
    "fe_woodpaw_mystic": "gnoll_2", "fe_woodpaw_brute": "gnoll_1", "fe_woodpaw_alpha": "gnoll_1",
    "fe_hyena": "hyena_1", "fe_ironfur_bear": "st_black_bear", "fe_gordunni_brute": "ogre_1",
    "fe_gordunni_mage": "ogre_2", "fe_gordunni_shaman": "ogre_2", "fe_gordunni_mauler": "dw_ogre_brute",
    "fe_gordunni_warlord": "ogre_1", "fe_gordunni_lord": "dw_ogre_brute", "fe_silithid_tunneler": "silithid_worker_1",
    "fe_silithid_swarmer": "silithid_worker_3", "fe_roosevelt_elk": "st_bull_elk", "fe_feralas_stalker": "panther_2",
    "fe_naga_raider": "naga_warrior", "fe_naga_digger": "naga_myrmidon_1", "fe_naga_priestess": "az_naga_sea_witch",
    "fe_makrura": "crab_giant_1", "fe_naga_guardian": "az_naga_royal_guard", "fe_coast_hydra": "serpent_2",
    "fe_chimaera": "az_blue_drake", "fe_chimaera_matriarch": "az_blue_drake", "fe_skystalker": "az_cliff_hippogryph",
    "fe_windwing": "az_cliff_hippogryph", "fe_forest_giant": "mountain_giant_granite",
    "fe_sea_giant": "mountain_giant_sandstone", "fe_rage_scar_yeti": "yeti_1", "fe_rage_scar_matriarch": "yeti_2",
}


def sprite(name):
    """The sprite a creature draws as now: its own once Kyle's sheet is sliced, its placeholder until then."""
    own = ROSTER[name][4]
    if (ROOT / "assets/creatures" / f"{own}.png").exists():
        return own
    return PLACEHOLDER.get(own, own)


RULES_START = "    # FERALAS'S OPEN WORLD (generated by tools/build_feralas_openworld.py; do not edit by hand)\n"
RULES_END = "    # END FERALAS'S OPEN WORLD\n"


def write_sprite_rules():
    """Exact-name rules in creature_sprites._RULES, just above Azshara's, rewritten every run."""
    import re
    path = ROOT / "creature_sprites.py"
    s = path.read_text(encoding="utf-8")
    block = RULES_START + "".join(f'    (r"^{re.escape(n.lower())}$", "{sprite(n)}"),\n' for n in ROSTER) + RULES_END
    if RULES_START in s:
        a = s.index(RULES_START)
        b = s.index(RULES_END) + len(RULES_END)
        s = s[:a] + block + s[b:]
    else:
        anchor = "    # AZSHARA'S OPEN WORLD (tools/build_azshara_openworld.py)"
        s = s.replace(anchor, block + anchor, 1)
    path.write_text(s, encoding="utf-8")


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
                buff(names[2], 6, 3, {"armor": 180})]
    if shape == "caster":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.84), cooldown=5, school=s, is_aoe=True),
                dot(names[2], int(t * 0.27), 3, 3, school=s, dispel_type=dispel)]
    if shape == "bruiser":
        return [dmg(names[0], t + 8, school=s), dmg(names[1], int(t * 0.84), cooldown=4, school=s, is_aoe=True),
                debuff(names[2], 5, 2, {"dodge_rating": -20}, school=s)]
    # a rare: a heavy basic, a party hit, a stun with a hammer behind it, and its last stand or its ward
    b = B(hi)
    last = (shield(names[3], int(b * 1.2), school=s) if s in ("arcane", "frost") else enrage(names[3], int(b * 0.15), s))
    return [dmg(names[0], b, school=s), dmg(names[1], int(b * 0.8), cooldown=4, school=s, is_aoe=True),
            stun(names[2], int(b * 0.85), cooldown=5, school=s), dmg(f"{names[0]}, Again", int(b * 1.7), cooldown=5,
                                                                   school=s), last]


TABLES = {
    HW: {
        "open_zone": {"Longtooth Runner": 4, "Feralas Stag": 3, "Feralas Sprite Darter": 3, "Ironfur Bear": 2},
        "subzones": {
            "The Aspen Descent": {"Longtooth Runner": 5, "Feralas Stag": 4, "Feralas Sprite Darter": 3},
            "Woodpaw Hills": {"Woodpaw Reaver": 5, "Woodpaw Trapper": 4, "Woodpaw Mystic": 4, "Woodpaw Brute": 3,
                              "Woodpaw Hyena": 3, "Grimfang": 0},
            "The Lower Wilds": {"Lower Wilds Crocolisk": 5, "Ironfur Bear": 4, "Feralas Sprite Darter": 2,
                                "Old Grizzlegut": 0},
            "Grimtotem Compound": {"Grimtotem Usurper": 5, "Grimtotem Bonecaller": 4, "Grimtotem Pathfinder": 4,
                                   "Grimtotem Earthbreaker": 3, "Pathfinder Harrok": 0},
            "Gordunni Outpost": {"Gordunni Brute": 5, "Gordunni Ogre Mage": 4, "Gordunni Shaman": 4},
            "The Gate of Dire Maul": {"Gordunni Mauler": 4, "Gordunni Warlord": 4, "Gordunni Ogre Mage": 3,
                                      "Gordunni Brute": 3, "Gash'tok the Gatekeeper": 0},
            "The Hive Fields": {"Zukk'ash Tunneler": 5, "Zukk'ash Swarmer": 5},
        },
    },
    FC: {
        "open_zone": {"Feralas Stalker": 4, "Fog Grove Ironfur": 3, "Frayfeather Skystalker": 3},
        "subzones": {
            "The Fog Groves": {"Fog Grove Elk": 5, "Fog Grove Ironfur": 4, "Feralas Stalker": 4, "Old Seven-Point": 0},
            "Cedar Hollow": None,
            "Feathermoon Landing": None,
            "Ruins of Isildien": {"Isildien Brute": 5, "Isildien Ogre Mage": 4, "Isildien Digger": 4,
                                  "Skull-Taker Murg": 0},
            "The Hatecrest Shore": {"Hatecrest Raider": 5, "Hatecrest Ruin-Digger": 4, "Hatecrest Makrura": 4,
                                    "Hatecrest Tide Priestess": 3},
            "Sardor Isle": {"Hatecrest Coral Guardian": 5, "Hatecrest Tide Priestess": 4, "Sardor Hydra": 3,
                            "Tidelord Ssaravel": 0},
            "The Isle of Dread": {"Dread Chimaera": 6, "Hatecrest Makrura": 2, "The Dread Matriarch": 0},
            "Frayfeather Highlands": {"Frayfeather Skystalker": 5, "Frayfeather Windwing": 4, "Antilus the Soarer": 0},
        },
    },
    TC: {
        "open_zone": {"Rage Scar Yeti": 3, "Feralas Stalker": 3, "Frayfeather Windwing": 2},
        "subzones": {
            "The Twin Colossals": {"Colossal Land Walker": 5, "Colossal Sea Walker": 4, "The Old Walker": 0},
            "Rage Scar Hold": {"Rage Scar Yeti": 6, "Rage Scar Matriarch": 3, "Rage Scar Old Bull": 0},
            "Ruins of Ravenwind": {"Ravenwind Raider": 5, "Ravenwind Sea Witch": 4, "Ravenwind Guardian": 4,
                                   "Ravenwind Hydra": 3, "Lady Szaressa": 0},
            "The Dream Bough": {"Dream Bough Darter": 5, "Dream-Touched Treant": 4},
            "The Sentinels' Watch": None,
        },
    },
}

#: rare -> four (name, slot, suffix, (a|w, type) or None, template). Spread across the armour classes, weapon types
#: and roles the 30 classes gear for (data/items/spec_gear.json), not the classic nine.
POOLS = {
    "Grimfang": [
        ("Grimfang's Spiked Club", "main_hand", "of the Bear", ("w", "mace_1h"), "str_physical"),
        ("Woodpaw Pelt Jerkin", "chest", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Mystic's Bone Fetish", "off_hand", "of the Prophet", ("w", "tome"), "spi_healer"),
        ("Alpha's Fang Necklace", "neck", "of the Tiger", None, "agi_physical")],
    "Old Grizzlegut": [
        ("Grizzlegut Hide Leggings", "legs", "of the Wolf", ("a", "leather"), "agi_int_hybrid"),
        ("Ironfur Shoulderguards", "shoulder", "of the Bear", ("a", "mail"), "str_physical"),
        ("Riverbank Waders", "feet", "of the Physician", ("a", "cloth"), "spi_healer"),
        ("Old Grizzlegut's Claw", "main_hand", "of the Monkey", ("w", "fist_weapon"), "agi_physical")],
    "Pathfinder Harrok": [
        ("Harrok's Painted Hide Shield", "off_hand", "of the Prophet", ("w", "shield"), "spi_healer"),
        ("Pathfinder's Spear", "main_hand", "of the Hunt", ("w", "polearm"), "agi_physical"),
        ("Grimtotem Earthbinder Belt", "waist", "of the Sorcerer", ("a", "mail"), "int_caster"),
        ("Usurper's Plate Bracers", "wrist", "of the Gorilla", ("a", "plate"), "str_int_hybrid")],
    "Gash'tok the Gatekeeper": [
        ("Gatekeeper's Cudgel", "two_hand", "of the Champion", ("w", "mace_2h"), "str_physical"),
        ("Looted Highborne Circlet", "head", "of the Invoker", ("a", "cloth"), "int_caster"),
        ("Gate-Chain Girdle", "waist", "of the Bear", ("a", "plate"), "str_physical"),
        ("Dire Maul Key-Ring", "ring", "of the Owl", None, "spi_healer")],
    "Old Seven-Point": [
        ("Seven-Point Antler Staff", "two_hand", "of the Wolf", ("w", "staff"), "agi_physical"),
        ("Fog-Damp Cedar Bracers", "wrist", "of the Prophet", ("a", "leather"), "spi_healer"),
        ("Bullhide Gauntlets", "hands", "of the Bear", ("a", "mail"), "str_physical"),
        ("Velvet Antler Charm", "trinket", "of the Sorcerer", None, "int_caster")],
    "Skull-Taker Murg": [
        ("Murg's Trophy Axe", "main_hand", "of the Tiger", ("w", "axe_1h"), "agi_physical"),
        ("Skull-Strung Pauldrons", "shoulder", "of the Champion", ("a", "plate"), "str_physical"),
        ("Isildien Dome-Dust Robe", "chest", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Head-Taker's Boots", "feet", "of the Owl", ("a", "mail"), "spi_healer")],
    "Tidelord Ssaravel": [
        ("Ssaravel's Tide Staff", "two_hand", "of the Invoker", ("w", "staff"), "int_caster"),
        ("Sardor Scale Leggings", "legs", "of the Hunt", ("a", "mail"), "agi_physical"),
        ("Coral-Studded Helm", "head", "of the Gorilla", ("a", "plate"), "str_int_hybrid"),
        ("Tidelord's Pearl", "neck", "of the Physician", None, "spi_healer")],
    "The Dread Matriarch": [
        ("Matriarch's Horn Bow", "ranged", "of the Hunt", ("w", "bow"), "agi_physical"),
        ("Chimaera-Hide Vest", "chest", "of the Wolf", ("a", "leather"), "agi_int_hybrid"),
        ("Acid-Etched Gloves", "hands", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Dread Isle Greaves", "legs", "of the Bear", ("a", "plate"), "str_physical")],
    "Antilus the Soarer": [
        ("Antilus's Pinion Cloak", "back", "of the Monkey", None, "agi_physical"),
        ("Soarer's Feathered Mantle", "shoulder", "of the Prophet", ("a", "cloth"), "spi_healer"),
        ("Highland Talon Dagger", "main_hand", "of the Sorcerer", ("w", "dagger"), "int_caster"),
        ("Skystalker Hauberk", "chest", "of the Gorilla", ("a", "mail"), "str_int_hybrid")],
    "The Old Walker": [
        ("Old Walker's Granite Heart", "trinket", "of the Bear", None, "str_physical"),
        ("Moss-Grown Breastplate", "chest", "of the Prophet", ("a", "plate"), "spi_healer"),
        ("Colossal Stone Maul", "two_hand", "of the Champion", ("w", "mace_2h"), "str_physical"),
        ("Walker's Lichen Wraps", "wrist", "of the Wolf", ("a", "leather"), "agi_int_hybrid")],
    "Rage Scar Old Bull": [
        ("Old Bull's Shaggy Hood", "head", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Rage Scar Hide Boots", "feet", "of the Bear", ("a", "mail"), "str_physical"),
        ("Yeti-Bone Wand", "ranged", "of the Physician", ("w", "wand"), "spi_healer"),
        ("Bellowing Signet", "ring", "of the Sorcerer", None, "int_caster")],
    "Lady Szaressa": [
        ("Szaressa's Coral Scepter", "main_hand", "of the Sorcerer", ("w", "mace_1h"), "int_caster"),
        ("Ravenwind Sea-Silk Leggings", "legs", "of the Physician", ("a", "cloth"), "spi_healer"),
        ("Drowning-Grip Gauntlets", "hands", "of the Tiger", ("a", "leather"), "agi_physical"),
        ("Ravenwind Coral Shield", "off_hand", "of the Gorilla", ("w", "shield"), "str_int_hybrid")],
}

#: gathering: the 40s forest tier: Khadgar's Whisker, Purple Lotus, Sungrass and Goldthorn; mithril and truesilver,
#: verdant iron in the green; bloodwood and moonpetal in the giant forest
NODES = {
    "the_high_wilderness": {"slots": 26, "active_percent": 0.42, "table": {
        "herb_khadgar": 4, "herb_goldthorn": 3, "herb_purple_lotus": 2, "herb_fadeleaf": 2,
        "ore_mithril": 4, "ore_verdant_iron": 3, "ore_truesilver": 1,
        "wood_bloodwood_tree": 4, "wood_bloodroot_stump": 2}},
    "the_forgotten_coast": {"slots": 26, "active_percent": 0.42, "table": {
        "herb_khadgar": 3, "herb_purple_lotus": 3, "herb_sungrass": 2, "herb_goldthorn": 2,
        "ore_mithril": 3, "ore_truesilver": 2, "ore_verdant_iron": 2,
        "wood_bloodwood_tree": 3, "wood_moonpetal_tree": 3}},
    "the_twin_colossals": {"slots": 24, "active_percent": 0.42, "table": {
        "herb_sungrass": 3, "herb_purple_lotus": 3, "herb_khadgar": 2,
        "ore_mithril": 3, "ore_truesilver": 3, "ore_thorium": 1,
        "wood_moonpetal_tree": 4, "wood_bloodwood_tree": 2}},
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
            d["item_id"] = "fer_" + kit_slug(name)
            r = budget_ratio(d)
            if r is not None and not 0.65 <= r <= 1.45:
                fit_to_curve(d)
            built.append(d)
            rows.append((name, slot, "weapon" if typ and typ[0] == "w" else "armor", typ[1] if typ else None,
                         template))
        out[rare] = built
    return out, rows


def check(maps=True):
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import importlib
    bad = []
    if maps:
        for zone, modname in MAP_MODULES.items():
            try:
                mod = importlib.import_module(f"tools.{modname}")
            except ImportError:
                bad.append(f"{zone}'s map ({modname}) isn't built yet")
                continue
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
        if not (ROOT / "assets/creatures" / f"{sprite(name)}.png").exists():
            bad.append(f"{name}'s sprite {sprite(name)} is not on disk")
        prev = existing.get(name)
        if prev and prev.get("ability_kit") != kit_slug(name):
            bad.append(f"{name} is already a different creature in creatures.json")
    if maps:
        import creature_sprites as CS
        for name, r in ROSTER.items():
            if CS.sprite_for(name, r[0]) != sprite(name):
                bad.append(f"creature_sprites.py draws {name} as {CS.sprite_for(name, r[0])}, not {sprite(name)}")
    return bad


def main():
    write_sprite_rules()
    if "--dry" in sys.argv:
        # what can be checked before the art and the maps: names, tables, pools and the loot's spread
        bad = [b for b in check(maps=False) if "not on disk" not in b]
        _loot, rows = build_loot()
        bad += loot_audit(rows)
        print("\n".join(bad) if bad else f"dry run clean: {len(ROSTER)} creatures, {len(RARES)} rares, {len(rows)} items")
        return 1 if bad else 0
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
    fish = (nd["zones"].get("glittervein") or {}).get("fishing")
    for key, pool in NODES.items():
        nd["zones"][key] = dict(pool, **({"fishing": fish} if fish else {}))
    np_path.write_text(json.dumps(nd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = {"_notes": ("Feralas's open-world rares (46-49). ONE item per kill from the rare's four; item_level = the "
                      "rare's level + 3. Hand-authored in tools/build_feralas_openworld.py.")}
    out.update(loot)
    LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True, stdout=subprocess.DEVNULL)
    print(f"{len(ROSTER)} creatures ({len(RARES)} rares) over {len(TABLES)} maps; {len(rows)} rare items; "
          f"gathering on {', '.join(NODES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
