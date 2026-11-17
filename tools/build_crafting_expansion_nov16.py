#!/usr/bin/env python3
"""Cooking, alchemy and engineering, filled out from 0 to 300. Idempotent: keyed by id and replaced.

    PYTHONPATH=. python3 tools/build_crafting_expansion_nov16.py

Kyle, 16 Nov 2026: "alchemy can use around an extra 100 potions / elixirs or things spread between level 0 to 300, it
is very bare... we need around another 75 or so engineering items to be made between 1 to 300. Cooking could use
another 75 to 100 or so. Keep in mind cooking we can have a food buff and a drink buff!"

WHAT IT ADDS
  COOKING (90)    five lines of meals and five of drinks, nine levels each. A meal restores health and leaves you
                  well fed; a drink restores mana and leaves you refreshed, in its own slot (Character.drink_buff),
                  so the two stack. Every dish is made of what its name says.
  ALCHEMY (100)   eight families of tonics and draughts (battle and guardian elixirs) at nine levels, ten more
                  healing and mana potions between the old ones, eight flasks at the top, and protection potions.
  ENGINEERING (75) goggles for every armour type, guns, bracers, bombs, gadgets and shot, between the old tiers.

NUMBERS sit on the lines the old recipes already draw (measured 16 Nov 2026): a battle elixir's main stat is about
0.45 x its level, a meal's about a third of its level plus two; health and mana restored follow the existing meals'
and drinks' curves; bombs, gadgets and shot follow engineering's own.

SKILL is level x 5, less 5, so a level 1 thing is skill 0 and a level 60 thing is 295. SOURCE alternates: half are
taught, half drop in the world (entities/recipe_drops), which keeps every trade inside Kyle's 50-55% band.

ICONS: every new consumable gets a copy of the closest existing icon (assets/icons/consumables/<id>.png), and the
gear is authored by tools/build_crafted_gear.author, which picks its one fixed icon the way every crafted piece does.
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

RECIPES = ROOT / "data/crafting/recipes.json"
CONS = ROOT / "data/consumables/consumable_types.json"
ICONS = ROOT / "assets/icons/consumables"
TAG = "16 Nov 2026 crafting expansion (tools/build_crafting_expansion_nov16.py)"

LEVELS = [5, 12, 19, 26, 33, 40, 47, 53, 59]
ADJ = ["Campfire", "Roadside", "Hearthside", "Riverbank", "Frontier", "Highland", "Old Country", "Wildland", "Grand"]


def skill_of(level):
    return max(0, min(300, 5 * level - 5))


def skill_range(s):
    from tools.build_jewelcrafting import skill_range as sr
    return sr(s)


def interp(table, lv):
    lv = max(table[0][0], min(table[-1][0], lv))
    for (a, va), (b, vb) in zip(table, table[1:]):
        if a <= lv <= b:
            return va + (vb - va) * (lv - a) / max(1, b - a)
    return table[-1][1]


def pick(table, level):
    """The best thing on a [(level, id)] ladder at or below this level."""
    best = table[0][1]
    for lv, iid in table:
        if lv <= level:
            best = iid
    return best


MEATS = [(1, "meat_stringy"), (8, "meat_lean"), (16, "meat_thick"), (24, "meat_rich"), (32, "meat_prime"),
         (38, "meat_marbled"), (46, "meat_aged"), (54, "meat_select")]
FISH = [(1, "fish_brilliant_smallfish"), (6, "fish_longjaw_mud_snapper"), (11, "fish_bristle_whisker_catfish"),
        (16, "fish_rainbow_fin_albacore"), (19, "fish_sagefish"), (24, "fish_deviate_fish"),
        (29, "fish_rockscale_cod"), (34, "fish_greater_sagefish"), (40, "fish_stonescale_eel"),
        (44, "fish_nightfin_snapper"), (48, "fish_winter_squid"), (54, "fish_darkclaw_lobster"),
        (57, "fish_lightning_eel")]
HERBS = [(1, "herb_peacebloom"), (4, "herb_earthroot"), (7, "herb_dewgrass"), (11, "herb_mageroyal"),
         (15, "herb_briarthorn"), (18, "herb_stranglekelp"), (21, "herb_bruiseweed"), (24, "herb_wild_steelbloom"),
         (26, "herb_kingsblood"), (31, "herb_liferoot"), (33, "herb_fadeleaf"), (35, "herb_goldthorn"),
         (38, "herb_khadgar"), (42, "herb_firebloom"), (43, "herb_purple_lotus"), (47, "herb_sungrass"),
         (48, "herb_blindweed"), (53, "herb_golden_sansam"), (55, "herb_dreamfoil"), (59, "herb_icecap")]
#: Eggs (Kyle, 16 Nov 2026: "eggs from birds"): taken from egg-laying beasts by entities/meat_drops.roll_eggs.
EGGS = [(1, "egg_small"), (20, "egg_speckled"), (40, "egg_giant")]
EGG_MATS = {
    "egg_small": {"name": "Small Egg", "material_type": "meat", "profession": "cooking", "tier": "early",
                  "icon_id": "egg_small", "stack_limit": 20, "sell_price": 6, "skill_range": [0, 25, 50, 75],
                  "description": "Lifted from a nest while its owner was busy with you."},
    "egg_speckled": {"name": "Speckled Egg", "material_type": "meat", "profession": "cooking", "tier": "mid",
                     "icon_id": "egg_speckled", "stack_limit": 20, "sell_price": 40,
                     "skill_range": [95, 120, 145, 170],
                     "description": "Bigger than your fist, and still warm."},
    "egg_giant": {"name": "Giant Egg", "material_type": "meat", "profession": "cooking", "tier": "late",
                  "icon_id": "egg_giant", "stack_limit": 20, "sell_price": 150, "skill_range": [195, 225, 255, 285],
                  "description": "One of these feeds a camp. Carry it with both hands."},
}
HP_MEAL = [(1, 250), (8, 380), (16, 520), (24, 690), (32, 900), (38, 1100), (46, 1400), (54, 1800), (60, 2400)]
MP_DRINK = [(1, 420), (10, 640), (20, 870), (30, 1090), (38, 1380), (46, 1670), (55, 2000), (60, 2200)]
SECS = [(1, 20), (20, 24), (40, 30), (60, 36)]


def vial(level):
    return "vial_empty" if level < 25 else ("vial_leaded" if level < 45 else "vial_crystal")


def stat_words(stats):
    from entities.consumable import bonus_text
    return bonus_text(stats)


def mat_name(mid):
    return MATS[mid]["name"]


MATS = {}


# ================================================================== cooking
def cooking():
    """-> [(recipe id, recipe, consumable)] for 45 meals and 45 drinks."""
    out = []
    meal_lines = [
        # key, noun, what it's made of (level -> {inputs}), stats (B -> {}), icon to copy, words
        ("skewers", "Hunter's Skewers", lambda L: {pick(MEATS, L): 2, "cook_spice": 1},
         lambda B: {"agility": round(B * 0.6), "stamina": round(B * 0.5)}, "meal_cooked_cutlets",
         "Meat on a stick, rubbed hot and turned over the coals."),
        ("stew", "Brawler's Stew", lambda L: {pick(MEATS, L): 2, "cook_roots": 1, "cook_water": 1},
         lambda B: {"strength": round(B * 0.6), "stamina": round(B * 0.5)}, "meal_cooked_seared_cut",
         "Meat and roots boiled until the spoon stands up in it."),
        ("pie", "Fisher's Pie", lambda L: {pick(FISH, L): 2, "cook_flour": 1},
         lambda B: {"intellect": round(B * 0.6), "spirit": round(B * 0.5)}, "meal_cooked_sagefish_delight",
         "Flaked fish under a lid of pastry."),
        ("ribs", "Ale-Smoked Ribs", lambda L: {pick(MEATS, L): 2, "cook_ale": 1},
         lambda B: {"attack_power": round(B * 1.3)}, "meal_cooked_firebrand_ribs",
         "Ribs smoked slow over a fire doused with ale."),
        ("omelette", "Omelette", lambda L: {pick(EGGS, L): 2, "cook_cheese": 1, "cook_mushroom": 1},
         lambda B: {"stamina": round(B * 0.6), "hp5": max(1, round(B * 0.25))}, "meal_cooked_trail_dumplings",
         "Eggs whipped with cheese and cellar mushrooms, folded in a hot pan."),
        ("chowder", "Scholar's Chowder", lambda L: {pick(FISH, L): 2, "cook_mushroom": 1, "cook_water": 1},
         lambda B: {"spell_power": round(B * 1.1)}, "meal_cooked_scholar_s_fricassee",
         "Fish and cellar mushrooms in a thick white broth."),
    ]
    for (key, noun, inputs, stats, icon, words) in meal_lines:
        for i, L in enumerate(LEVELS):
            B = round(L / 3) + 2
            st = stats(B)
            name = f"{ADJ[i]} {noun}"
            cid = f"meal_cooked_x16_{key}_{L}"
            hp = int(round(interp(HP_MEAL, L) / 10) * 10)
            secs = int(round(interp(SECS, L)))
            cons = {"consumable_id": cid, "name": name, "consumable_type": "meal",
                    "description": f"{words} Restores health over {secs} seconds while you rest, and leaves you "
                                   f"well fed ({stat_words(st)}) for 30 minutes.",
                    "effect_value": hp, "effect_duration": secs, "level_multiplier": 0.0, "required_level": L,
                    "cooldown_seconds": 2, "stack_limit": 20, "vendor_price": 0, "sell_price": 4 + L * 2,
                    "buff_category": "food", "stat_bonuses": st, "_source": TAG, "_icon_from": icon}
            out.append((f"cook_x16_{key}_{L}", name, inputs(L), L, cons))
    drink_lines = [
        ("tea", "Tea", lambda L: {pick(HERBS, L): 1, "cook_water": 1, "cook_honey": 1},
         lambda B: {"spirit": round(B * 0.6), "mp5": max(1, round(B * 0.2))}, "drink_spring_flask",
         "Leaves steeped in hot water with a spoon of honey.", True),
        ("cider", "Cider", lambda L: {"cook_fruit": 2, "cook_water": 1},
         lambda B: {"stamina": round(B * 0.6), "hp5": max(1, round(B * 0.2))}, "drink_barley_beer",
         "Pressed fruit, left in the cask until it bites back.", False),
        ("mead", "Mead", lambda L: {"cook_honey": 2, "cook_ale": 1},
         lambda B: {"attack_power": round(B * 1.2)}, "drink_honeyed_mead",
         "Honey and ale, and more honey than ale.", False),
        ("wine", "Spiced Wine", lambda L: {"cook_fruit": 2, "cook_spice": 1},
         lambda B: {"spell_power": round(B * 1.0)}, "drink_birch_wine",
         "Fruit wine warmed with a twist of hot spice.", False),
        ("infusion", "Infusion", lambda L: {pick(HERBS, L): 2, "cook_water": 1},
         lambda B: {"healing_power": round(B * 2.0)}, "drink_deepwell_cordial",
         "A herb left in water until the water tastes of nothing else.", True),
    ]
    for (key, noun, inputs, stats, icon, words, herbal) in drink_lines:
        for i, L in enumerate(LEVELS):
            B = round(L / 3) + 2
            st = stats(B)
            herb = pick(HERBS, L)
            name = (f"{mat_name(herb)} {noun}" if herbal else f"{ADJ[i]} {noun}")
            cid = f"drink_cooked_x16_{key}_{L}"
            mp = int(round(interp(MP_DRINK, L) / 10) * 10)
            secs = int(round(interp(SECS, L)))
            cons = {"consumable_id": cid, "name": name, "consumable_type": "drink",
                    "description": f"{words} Restores mana over {secs} seconds while you rest, and leaves you "
                                   f"refreshed ({stat_words(st)}) for 30 minutes. A drink's buff stacks with a "
                                   f"meal's.",
                    "effect_value": mp, "effect_duration": secs, "level_multiplier": 0.0, "required_level": L,
                    "cooldown_seconds": 2, "stack_limit": 20, "vendor_price": 0, "sell_price": 4 + L * 2,
                    "buff_category": "drink", "stat_bonuses": st, "_source": TAG, "_icon_from": icon}
            out.append((f"cook_x16_{key}_{L}", name, inputs(L), L, cons))
    return out


# ================================================================== alchemy
TIER_WORDS = ["Weak", "Lesser", "Simple", "Strong", "Potent", "Greater", "Superior", "Mighty", "Supreme"]
ALCH_LEVELS = [10, 20, 25, 35, 40, 45, 50, 55, 60]


def alchemy():
    out = []
    fams = [
        ("might", "Tonic of Might", "battle", lambda L: {"strength": round(L * 0.45)}, "elixir_of_greater_strength"),
        ("grace", "Tonic of Grace", "battle", lambda L: {"agility": round(L * 0.45)}, "elixir_agility_greater"),
        ("clarity", "Tonic of Clarity", "battle", lambda L: {"intellect": round(L * 0.45)}, "elixir_intellect_greater"),
        ("fury", "Tonic of Fury", "battle", lambda L: {"attack_power": round(L * 0.9)}, "elixir_attackpower_greater"),
        ("sorcery", "Tonic of Sorcery", "battle", lambda L: {"spell_power": round(L * 0.75)}, "elixir_of_lesser_firepower"),
        ("vigor", "Draught of Vigor", "guardian", lambda L: {"stamina": round(L * 0.5)}, "elixir_fortitude_greater"),
        ("calm", "Draught of Calm", "guardian", lambda L: {"spirit": round(L * 0.4), "mp5": max(1, round(L * 0.12))},
         "elixir_mana_regen_greater"),
        ("mending", "Draught of Mending", "guardian", lambda L: {"healing_power": round(L * 1.4)}, "elixir_of_holy_fury"),
    ]
    for (key, noun, slot, stats, icon) in fams:
        for i, L in enumerate(ALCH_LEVELS):
            st = stats(L)
            name = f"{TIER_WORDS[i]} {noun}"
            cid = f"alch_x16_{key}_{L}"
            cons = {"consumable_id": cid, "name": name, "consumable_type": "elixir",
                    "description": f"{stat_words(st)} for 30 minutes. "
                                   f"{'Battle' if slot == 'battle' else 'Guardian'} elixir: one at a time.",
                    "effect_value": 0, "effect_duration": 1800, "level_multiplier": 0.0, "required_level": L,
                    "cooldown_seconds": 5, "stack_limit": 20, "vendor_price": 0, "sell_price": 10 + L * 3,
                    "buff_category": slot, "stat_bonuses": st, "_source": TAG, "_icon_from": icon}
            herb, herb2 = pick(HERBS, L), pick(HERBS, max(1, L - 12))
            out.append((cid.replace("alch_x16_", "alch_x16r_"), name, {herb: 2, herb2: 1, vial(L): 1}, L, cons))
    # potions between the old ones
    for L, word in ((5, "Lesser"), (14, "Strong"), (22, "Potent"), (29, "Fine"), (37, "Distilled")):
        usual = 150 + (1100 - 150) * (L - 1) / 54
        for kind, bar, icon in (("health_potion", "Healing", "healing_potion_greater"),
                                ("mana_potion", "Mana", "mana_potion_greater")):
            name = f"{word} {bar} Potion"
            cid = f"{'healing' if kind == 'health_potion' else 'mana'}_potion_x16_{L}"
            cons = {"consumable_id": cid, "name": name, "consumable_type": kind,
                    "description": f"Restores {'health' if bar == 'Healing' else 'mana'} at once.",
                    "effect_value": int(round(usual)), "effect_duration": 0, "level_multiplier": 0.0,
                    "required_level": L, "cooldown_seconds": 5, "stack_limit": 20, "vendor_price": 0,
                    "sell_price": 5 + L * 2, "buff_category": None, "_source": TAG, "_icon_from": icon}
            herb = pick(HERBS, L)
            out.append((f"alch_x16r_{cid}", name, {herb: 2, vial(L): 1}, L, cons))
    # flasks at the top
    flasks = [("titans", "Flask of the Titans", {"stamina": 60}), ("power", "Flask of Supreme Power", {"spell_power": 70}),
              ("wisdom", "Flask of Distilled Wisdom", {"intellect": 45, "mp5": 8}),
              ("warlord", "Flask of the Warlord", {"attack_power": 110}), ("wilds", "Flask of the Wilds", {"agility": 45}),
              ("giant", "Flask of the Giant", {"strength": 45}), ("restoration", "Flask of Restoration",
                                                                   {"healing_power": 150}),
              ("chromatic", "Flask of Chromatic Wards", {"fire_resistance": 25, "frost_resistance": 25,
                                                         "nature_resistance": 25, "shadow_resistance": 25,
                                                         "arcane_resistance": 25})]
    for i, (key, name, st) in enumerate(flasks):
        L = 55 + (i % 6)
        cid = f"flask_x16_{key}"
        cons = {"consumable_id": cid, "name": name, "consumable_type": "elixir",
                "description": f"{stat_words(st)} for 30 minutes. A flask is a guardian elixir: one at a time.",
                "effect_value": 0, "effect_duration": 1800, "level_multiplier": 0.0, "required_level": L,
                "cooldown_seconds": 5, "stack_limit": 20, "vendor_price": 0, "sell_price": 1500,
                "buff_category": "guardian", "stat_bonuses": st, "_source": TAG, "_icon_from": "flask_mending"}
        out.append((f"alch_x16r_{cid}", name, {"herb_black_lotus": 1, pick(HERBS, L): 3, "vial_crystal": 1}, L,
                    cons))
    # protection potions
    for school, icon in (("fire", "elixir_ward_fire_greater"), ("frost", "elixir_ward_frost_greater"),
                         ("nature", "elixir_ward_nature_greater"), ("shadow", "elixir_ward_shadow_greater"),
                         ("arcane", "elixir_of_warding")):
        for L, word, amt in ((40, "", 40), (55, "Major ", 55)):
            st = {f"{school}_resistance": amt}
            name = f"{word}{school.title()} Protection Potion"
            cid = f"alch_x16_{school}_protection_{L}"
            cons = {"consumable_id": cid, "name": name, "consumable_type": "elixir",
                    "description": f"{stat_words(st)} for 30 minutes. Guardian elixir: one at a time.",
                    "effect_value": 0, "effect_duration": 1800, "level_multiplier": 0.0, "required_level": L,
                    "cooldown_seconds": 5, "stack_limit": 20, "vendor_price": 0, "sell_price": 60 + L * 3,
                    "buff_category": "guardian", "stat_bonuses": st, "_source": TAG, "_icon_from": icon}
            out.append((f"alch_x16r_{school}_protection_{L}", name, {pick(HERBS, L): 2, "herb_stranglekelp": 1,
                                                                      vial(L): 1}, L, cons))
    return out


# ================================================================== engineering
ENG_LEVELS = [8, 14, 20, 26, 32, 38, 44, 50, 56]
BARS = [(1, "bar_copper"), (14, "bar_bronze"), (26, "bar_iron"), (34, "bar_steel"), (36, "bar_mithril"),
        (47, "bar_truesilver"), (50, "bar_thorium"), (57, "bar_arcanite")]
PARTS = [(1, "part_copper_bolts"), (9, "part_bronze_framework"), (13, "part_gear_assembly"),
         (17, "part_iron_casing"), (25, "part_resonant_core"), (29, "part_void_regulator")]
LENSES = [(1, "part_glass_lens"), (13, "part_sight_glass"), (23, "part_precision_sight")]
LEATHERS = [(0, "leather_light"), (100, "leather_medium"), (150, "leather_heavy"), (200, "leather_thick"),
            (250, "leather_rugged")]
#: gems by the skill a jewelcrafter finds them at (data/gathering/materials.json skill_range)
GEMS = [(0, "gem_malachite"), (20, "gem_tigerseye"), (40, "gem_bloodstone"), (65, "gem_shadowgem"),
        (75, "gem_lesser_moonstone"), (95, "gem_carnelian"), (125, "gem_jade"), (155, "gem_topaz"),
        (175, "gem_aquamarine"), (205, "gem_fire_opal"), (230, "gem_black_diamond"), (245, "gem_blue_sapphire"),
        (260, "gem_cinder_agate"), (290, "gem_elementium_prism")]
CRYSTALS = [(1, "crystal_quartz"), (4, "crystal_azure"), (10, "crystal_emberglass"), (11, "crystal_tideglass"),
            (14, "crystal_voidglass")]


def engineering():
    """-> (consumable recipes [(rid, name, inputs, level, cons)], gear recipes [(rid, recipe dict, ident)])."""
    cons_out, gear_out = [], []
    # bombs: three schools, each at three levels the old ones skip
    bomb_lines = [("fire", "Incendiary Charge", "fire", None), ("frost", "Rime Grenade", "frost", 1),
                  ("thunder", "Thunderclap Bomb", "nature", None), ("shard", "Shardstorm Charge", "physical", 1),
                  ("hex", "Hexed Canister", "shadow", None)]
    bomb_levels = [12, 32, 54]
    for bi, (key, noun, school, stun) in enumerate(bomb_lines):
        for j, L in enumerate(bomb_levels):
            dmg = int(round(interp([(5, 40), (16, 120), (26, 260), (38, 360), (50, 450), (57, 500), (60, 520)], L) * 0.9))
            name = f"{['Crude', 'Heavy', 'Masterwork'][j]} {noun}"
            cid = f"bomb_x16_{key}_{L}"
            c = {"consumable_id": cid, "name": name, "consumable_type": "explosive",
                 "description": f"Hits every enemy for {dmg} {school} damage (more as you level). Uses your turn.",
                 "effect_value": dmg, "effect_duration": 0, "level_multiplier": 0.0, "required_level": L,
                 "cooldown_seconds": 30, "stack_limit": 20, "vendor_price": 0, "sell_price": 20 + L * 4,
                 "damage_school": school, "_source": TAG, "_icon_from": "bomb_iron"}
            if stun:
                c["apply_effect_targets"] = {"effect_id": f"{cid}_stagger", "name": "Staggered",
                                             "effect_type": "debuff", "duration": 1, "is_stun": True}
                c["description"] = c["description"].replace(" Uses your turn.", " Staggers them. Uses your turn.")
            cons_out.append((f"eng_x16_{key}_{L}", name, {pick(BARS, L): 1, pick(CRYSTALS, L): 1,
                                                          pick(PARTS, L): 1}, L, c))
    # gadgets: a stat for a while, in the gadget slot
    gadgets = [("visor", "Tinted Visor", lambda L: {"hit_rating": round(L * 0.5), "spell_hit_rating": round(L * 0.5)}),
               ("plating", "Bolt-On Plating", lambda L: {"armor": round(L * 5)}),
               ("ticker", "Pocket Ticker", lambda L: {"haste": round(L * 0.9)}),
               ("rangefinder", "Rangefinder", lambda L: {"crit_chance_physical": round(L * 0.6)}),
               ("focuser", "Arcane Focuser", lambda L: {"crit_chance_spell": round(L * 0.6)}),
               ("brace", "Shock Brace", lambda L: {"stamina": round(L * 0.35), "armor": round(L * 2)})]
    for gi, (key, noun, stats) in enumerate(gadgets):
        for j, L in enumerate((18, 42)):
            st = stats(L)
            name = f"{['Field', 'Precision'][j]} {noun}"
            cid = f"device_x16_{key}_{L}"
            c = {"consumable_id": cid, "name": name, "consumable_type": "gadget",
                 "description": f"Strap it on: {stat_words(st)} for 30 minutes. Gadget (one at a time).",
                 "effect_value": 0, "effect_duration": 1800, "level_multiplier": 0.0, "required_level": L,
                 "cooldown_seconds": 0, "stack_limit": 20, "vendor_price": 0, "sell_price": 30 + L * 4,
                 "buff_category": "gadget", "stat_bonuses": st, "_source": TAG, "_icon_from": "device_goggleset"}
            cons_out.append((f"eng_x16_{key}_{L}", name, {pick(BARS, L): 2, pick(LENSES, L): 1, pick(PARTS, L): 1},
                             L, c))
    # shot: between the old ones
    for L, word, mat in ((8, "Copper Slug", "bar_copper"), (11, "Weighted Shot", "bar_copper"),
                         (17, "Bronze Ball", "bar_bronze"), (24, "Iron-Cored Shot", "bar_iron"),
                         (33, "Steel Ball", "bar_steel"), (42, "Hollow Mithril Shot", "bar_mithril"),
                         (46, "Truesilver Slug", "bar_truesilver"), (48, "Explosive Round", "bar_truesilver"),
                         (55, "Thorium Slug", "bar_thorium"), (60, "Arcanite Slug", "bar_arcanite")):
        ap = int(round(interp([(1, 4), (14, 8), (19, 10), (26, 13), (29, 15), (38, 18), (52, 22), (57, 26), (60, 28)], L)))
        cid = f"shot_x16_{L}"
        c = {"consumable_id": cid, "name": word, "consumable_type": "ammo",
             "description": f"Grants +{ap} Attack Power for 30 minutes. Ammo buff (one pouch at a time).",
             "effect_value": 0, "effect_duration": 1800, "level_multiplier": 0.0, "required_level": L,
             "cooldown_seconds": 0, "stack_limit": 200, "vendor_price": 0, "sell_price": 4 + L,
             "buff_category": "ammo", "stat_bonuses": {"attack_power": ap}, "_source": TAG, "_icon_from": "shot_iron"}
        cons_out.append((f"eng_x16_shot_{L}", word, {mat: 1}, L, c))
    # GOGGLES, 1 to 60, of leather and gems (Kyle, 16 Nov 2026: "Head piece (goggles made with leather and gems
    # throughout the entire 1-60)"). Seven levels for each armour type, and each type's roles take turns, so a
    # healer, a caster, a tank and a fighter all find a pair along the way.
    goggle_lines = {
        "cloth": ("Spectacles", ["caster", "healer", "caster_crit", "high_healer", "precise_caster", "healer",
                                 "haste_caster"]),
        "leather": ("Goggles", ["agility", "healer", "feral", "rogue_crit", "tide_healer", "assassin", "bear"]),
        "mail": ("Lenses", ["hunter", "tide_healer", "hunter_crit", "mail_caster", "hunter_precise", "earthen",
                            "hunter"]),
        "plate": ("Visor", ["strength", "tank", "plate_healer", "strength_crit", "tank_any", "crusader",
                            "strength_hit"]),
    }
    words = ["Tinker's", "Flash-Lensed", "Bronze-Rimmed", "Clockwork", "Gyroscopic", "Mithril-Framed",
             "Arcanite-Lensed"]
    for atype, (noun, idents) in goggle_lines.items():
        for j, L in enumerate((6, 15, 24, 33, 42, 51, 58)):
            name = f"{words[j]} {noun}"
            rid = f"eng_x16_goggles_{atype}_{L}"
            out = {"kind": "armor", "slot": "head", "armor_type": atype, "stat_template": None,
                   "item_level": L + 2, "rarity": "uncommon" if L < 40 else "rare", "material_tier": None}
            sk = skill_of(L)
            gear_out.append((rid, name, out, idents[j], L,
                             {pick(LEATHERS, sk): 2 + j // 2, pick(GEMS, sk): 1 + j // 3, pick(LENSES, L): 1}))
    # GUNS FOR EVERY ROLE (Kyle: "guns for healers, guns for DPS, guns for tanks with defense rating"). Who holds
    # one: fighters (warriors, rogues, hunters, rangers), tanks (Protection warriors, the Black Knight, the
    # Fortitude venomancer), and the Tinker's and Vizier's healers and the Demolition tinker, whose spec gun is
    # a gun (data/items/spec_gear.json).
    guns = [
        # level, name, identity
        (10, "Brassbound Blunderbuss", "agility"), (22, "Gyro-Sight Carbine", "hunter_crit"),
        (34, "Steelbore Longrifle", "hunter_precise"), (46, "Mithril Repeater", "rogue_crit"),
        (56, "Thorium Deadeye", "hunter_crit"),
        (16, "Rivet-Stock Scattergun", "strength"), (40, "Dwarven Handcannon", "strength_crit"),
        (18, "Bulwark Musket", "tank_weapon"), (32, "Ironwall Arquebus", "tank_weapon"),
        (44, "Bastion Bombard", "bear_weapon"), (58, "Siegewarden's Rampart Gun", "tank_weapon"),
        (20, "Tinkerer's Mending Pistol", "tide_healer"), (38, "Salve-Charged Dart Rifle", "healer"),
        (54, "Lifespark Auto-Injector", "tide_healer"),
        (28, "Sparkcoil Pistol", "hunter"), (50, "Arc-Lightning Carbine", "wildheart"),
    ]
    for L, name, ident in guns:
        rid = f"eng_x16_gun_{L}_{ident}"
        out = {"kind": "weapon", "slot": "ranged", "weapon_type": "gun", "stat_template": None,
               "item_level": L + 2, "rarity": "uncommon" if L < 40 else "rare", "material_tier": None}
        extra = pick(GEMS, skill_of(L)) if ident in ("tide_healer", "healer", "hunter", "wildheart") else \
            pick(PARTS, L)
        gear_out.append((rid, name, out, ident, L,
                         {pick(BARS, L): 4, "part_steel_barrel" if L >= 19 else "part_bronze_tube": 1,
                          "part_wooden_stock": 1, extra: 1}))
    for j, (L, name, atype, ident) in enumerate(((16, "Spring-Loaded Bracers", "leather", "agility"),
                                                 (30, "Piston Bracers", "mail", "hunter"),
                                                 (42, "Gearwork Bracers", "plate", "strength"),
                                                 (54, "Arcane Coil Bracers", "cloth", "caster"),
                                                 (20, "Coil-Wound Wristguards", "mail", "earthen"),
                                                 (46, "Dynamo Wristguards", "leather", "feral"),
                                                 (34, "Capacitor Cuffs", "cloth", "healer"),
                                                 (58, "Thorium Gauntlets of the Sapper", "plate", "tank"))):
        slot = "hands" if "Gauntlets" in name else "wrist"
        rid = f"eng_x16_wrist_{atype}_{L}"
        out = {"kind": "armor", "slot": slot, "armor_type": atype, "stat_template": None,
               "item_level": L + 2, "rarity": "uncommon" if L < 40 else "rare", "material_tier": None}
        gear_out.append((rid, name, out, ident, L, {pick(BARS, L): 3, pick(PARTS, L): 2}))
    return cons_out, gear_out


# ================================================================== write it
def main():
    global MATS
    MATS = json.loads((ROOT / "data/gathering/materials.json").read_text(encoding="utf-8"))["materials"]
    mdoc = json.loads((ROOT / "data/gathering/materials.json").read_text(encoding="utf-8"))
    if any(mdoc["materials"].get(k) != v for k, v in EGG_MATS.items()):
        mdoc["materials"].update(EGG_MATS)
        (ROOT / "data/gathering/materials.json").write_text(json.dumps(mdoc, indent=2, ensure_ascii=False) + "\n",
                                                            encoding="utf-8")
        MATS = mdoc["materials"]
    rd = json.loads(RECIPES.read_text(encoding="utf-8"))
    cd = json.loads(CONS.read_text(encoding="utf-8"))
    profs = rd["professions"]
    # the names already in use, so nothing new shares one
    taken = set()
    for lst in cd.values():
        if isinstance(lst, list):
            taken |= {c["name"] for c in lst if not str(c.get("_source", "")).startswith("16 Nov 2026 crafting")}
    for p in profs.values():
        taken |= {r["name"] for rid, r in (p.get("recipes") or {}).items() if "x16" not in rid}
    taken |= {m["name"] for m in MATS.values()}
    bad = []
    lists = {"cooking": cooking(), "alchemy": alchemy()}
    eng_cons, eng_gear = engineering()
    lists["engineering"] = eng_cons
    new_cons = {}
    counts = {}
    for prof, rows in lists.items():
        R = profs[prof]["recipes"]
        for k in [k for k in R if "x16" in k]:
            del R[k]
        for i, (rid, name, inputs, L, cons) in enumerate(rows):
            if name in taken:
                bad.append(f"{prof}: {name} is already a name")
            for mid in inputs:
                if mid not in MATS:
                    bad.append(f"{prof}: {name} needs {mid}, which doesn't exist")
            sk = skill_of(L)
            R[rid] = {"name": name, "inputs": dict(inputs), "skill_required": sk, "skill_range": skill_range(sk),
                      "output": {"kind": "consumable", "consumable_id": cons["consumable_id"]},
                      "source": "trainer" if i % 2 == 0 else "drop"}
            if cons["consumable_type"] == "ammo":
                R[rid]["count"] = 20
            elif cons["consumable_type"] == "explosive":
                R[rid]["count"] = 3
            new_cons[cons["consumable_id"]] = cons
            counts[prof] = counts.get(prof, 0) + 1
    # engineering gear, authored the way every crafted piece is
    import build_crafted_gear as CG
    from crafted_icon_palette import Picker
    CG.PICKER = Picker()
    R = profs["engineering"]["recipes"]
    for i, (rid, name, out, ident, L, inputs) in enumerate(eng_gear):
        if name in taken:
            bad.append(f"engineering: {name} is already a name")
        out = dict(out)
        out["stat_template"] = CG.IDENTITIES[ident][1]
        recipe = {"name": name, "output": out}
        out["item"] = CG.author(rid, recipe, ident, "Clever, a little loud, and better than it looks.")
        if "_goggles_" in rid:
            # goggles look like goggles: their own tinted art (tools/make_goggle_icons.py)
            from make_goggle_icons import icon_id as goggle_icon
            out["item"]["icon_id"] = goggle_icon(out["armor_type"], L)
            CG._ASSIGNED = None
        sk = skill_of(L)
        R[rid] = {"name": name, "inputs": dict(inputs), "skill_required": sk, "skill_range": skill_range(sk),
                  "output": out, "source": "trainer" if i % 2 == 0 else "drop"}
        counts["engineering"] = counts.get("engineering", 0) + 1
    # the gear's icons are written down where build_crafted_gear.icon_for reads them, so a rebuild keeps them
    ic_path = ROOT / "data/items/crafted_icons.json"
    ic = json.loads(ic_path.read_text(encoding="utf-8"))
    for rid, r in R.items():
        if "x16" in rid and r["output"].get("item"):
            ic["icons"][r["output"]["item"]["name"]] = r["output"]["item"]["icon_id"]
    ic_path.write_text(json.dumps(ic, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if bad:
        print("FAILED - fix the data, not the check:")
        for b in bad:
            print("  -", b)
        return 1
    # consumables into their lists
    homes = {"meal": "cooked_meals", "drink": "cooked_drinks", "elixir": "elixirs", "health_potion": "health_potions",
             "mana_potion": "mana_potions", "explosive": "explosives", "gadget": "gadgets", "ammo": "ammos"}
    for lst in list(cd.values()):
        if isinstance(lst, list):
            lst[:] = [c for c in lst if not str(c.get("_source", "")).startswith("16 Nov 2026 crafting")]
    ICONS.mkdir(parents=True, exist_ok=True)
    missing_icons = []
    for cid, c in new_cons.items():
        src = c.pop("_icon_from")
        cd.setdefault(homes[c["consumable_type"]], []).append(c)
        dst = ICONS / f"{cid}.png"
        if not dst.exists():
            s = ICONS / f"{src}.png"
            if s.exists():
                shutil.copyfile(s, dst)
            else:
                missing_icons.append(cid)
    RECIPES.write_text(json.dumps(rd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    CONS.write_text(json.dumps(cd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{sum(counts.values())} recipes: {counts}; {len(new_cons)} consumables")
    if missing_icons:
        print("  no icon to copy for:", missing_icons[:10])
    return 0


if __name__ == "__main__":
    sys.exit(main())
