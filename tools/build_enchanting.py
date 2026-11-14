#!/usr/bin/env python3
"""Enchanting: disenchant gear for dust, essences and shards, and put enchantments on gear.
Idempotent.

    PYTHONPATH=. python3 tools/build_enchanting.py
    PYTHONPATH=. python3 tools/vendor_trades.py        # then stock the shops

Kyle, 14 Nov 2026: "Next up we need to build enchanting and runecrafting. Enchanting first. Rods
will be made by Blacksmiths or sold by vendors (they can get very pricy very fast). We can use
traditional wow-style materials for enchanting. Eventually we can introduce higher end frontier
dusts, essences, and shards. But let's start wow classic style + additional enchants to help fill
in the gaps and aim for more hybrid classes rather than the standard."

His answers: materials come from DISENCHANTING, WoW-style. The town enchanters teach it. A handful
of proc weapon enchants. Wands and weapon oils too.

WHAT THIS WRITES

  data/gathering/materials.json   the WoW classic materials (five dusts, ten essences, eight shards
                                  and the Nexus Crystal), five runed rods, and one enchantment
                                  scroll per formula
  data/enchanting/enchants.json   every enchantment (what it does, what it goes on) and the
                                  disenchant table; read by world/enchanting.py
  data/enchanting/recipes.json    the formulas, wands and oils
  data/blacksmithing/recipes.json the rods, which blacksmiths make
  data/consumables/consumable_types.json   weapon oils (a fifth buff slot, "oil")
  data/professions/professions.json, data/training/trainers.json   the profession and its trainers
  assets/gathering_nodes/enchanting/  the icons, copied from assets/icons

HOW AN ENCHANTMENT GETS ON GEAR. A formula makes a scroll that holds the enchantment. The
inventory's Enchant button reads a scroll onto a piece of gear (yours or anything the party is
wearing). That is the WotLK vellum idea, and it is what lets one screen do the work for the whole
party.

ONE FORMULA FOR NUMBERS, as with gems: an enchantment of level L is worth
`L x 0.36 x 1.3 x share` stat-budget points, spent through each stat's real cost, and `share`
depends on what it goes on (a 2H weapon most, a cloak least). At the top tier that lands on the
classic numbers: +8 Strength on bracers, +15 on a weapon, +23 Agility on a two-hander.

HYBRIDS. Beside every classic single-stat enchantment there are pairs for the classes who need two
things at once: Valor (Strength and Intellect), Wildheart (Agility and Intellect), Battlemage (Attack
Power and Spell Power), Devotion (Strength and Healing), Stormcaller (Agility and Spell Power), and
the plainer Vigor, Swiftness, Sagacity and Warding. Two weapon procs are hybrid too: Bladesong (your
swings raise your spell power) and Spellblade (your spells raise your attack power).
"""
import json
import math
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_jewelcrafting import load, save, skill_range  # noqa: E402

MATS = ROOT / "data/gathering/materials.json"
OUT_ENCH = ROOT / "data/enchanting/enchants.json"
OUT_RECIPES = ROOT / "data/enchanting/recipes.json"
BS = ROOT / "data/blacksmithing/recipes.json"
CONS = ROOT / "data/consumables/consumable_types.json"
PROFS = ROOT / "data/professions/professions.json"
TRAINERS = ROOT / "data/training/trainers.json"
ICONS = ROOT / "assets/icons"
ART = ROOT / "assets/gathering_nodes/enchanting"

# ------------------------------------------------------------------ materials
#: id -> (name, icon in assets/icons/materials or a path under assets/icons, sell price)
DUSTS = [
    ("strange_dust", "Strange Dust", "materials/inv_enchant_duststrange.png", 30),
    ("soul_dust", "Soul Dust", "materials/inv_enchant_dustsoul.png", 90),
    ("vision_dust", "Vision Dust", "materials/inv_enchant_dustvision.png", 200),
    ("dream_dust", "Dream Dust", "materials/inv_enchant_dustdream.png", 400),
    ("illusion_dust", "Illusion Dust", "materials/inv_enchant_dustillusion.png", 700),
]
ESSENCES = [
    ("magic", "Magic", 40), ("astral", "Astral", 120), ("mystic", "Mystic", 260),
    ("nether", "Nether", 500), ("eternal", "Eternal", 900),
]
ESSENCE_ICON = {"magic": "magic", "astral": "astral", "mystic": "mystical", "nether": "nether",
                "eternal": "eternal"}
#: Large Glimmering and both Radiant shards have no art of their own yet (see the doc's prompts)
SHARDS = [
    ("small_glimmering_shard", "Small Glimmering Shard", "materials/inv_enchant_shardgleamingsmall.png", 150),
    ("large_glimmering_shard", "Large Glimmering Shard", "materials/inv_enchant_shardgleamingsmall.png", 300),
    ("small_glowing_shard", "Small Glowing Shard", "materials/inv_enchant_shardglowingsmall.png", 450),
    ("large_glowing_shard", "Large Glowing Shard", "materials/inv_enchant_shardglowinglarge.png", 800),
    ("small_radiant_shard", "Small Radiant Shard", "materials/inv_enchant_shardprismaticlarge.png", 1000),
    ("large_radiant_shard", "Large Radiant Shard", "materials/inv_enchant_shardprismaticlarge.png", 1600),
    ("small_brilliant_shard", "Small Brilliant Shard", "materials/inv_enchant_shardbrilliantsmall.png", 2000),
    ("large_brilliant_shard", "Large Brilliant Shard", "materials/inv_enchant_shardbrilliantlarge.png", 3500),
    ("nexus_crystal", "Nexus Crystal", "materials/inv_enchant_shardnexuslarge.png", 12000),
]

#: the rods: (id, name, bar, second input, skill to use, BS skill, vendor price in copper, icon)
#: Kyle: "Rods will be made by Blacksmiths or sold by vendors (they can get very pricy very fast)."
RODS = [
    ("runed_copper_rod", "Runed Copper Rod", ("bar_copper", 2), ("flux_weak", 1), 1, 25, 500,
     "gear/gear_inv_staff_01.png"),
    ("runed_silver_rod", "Runed Silver Rod", ("bar_silver", 2), ("flux_weak", 1), 100, 100, 3000,
     "gear/gear_inv_staff_02.png"),
    ("runed_golden_rod", "Runed Golden Rod", ("bar_gold", 2), ("flux_medium", 1), 150, 150, 20000,
     "gear/gear_epic_wand_1.png"),
    ("runed_truesilver_rod", "Runed Truesilver Rod", ("bar_truesilver", 2), ("flux_strong", 1), 200, 200,
     80000, "gear/gear_epic_wand_2.png"),
    ("runed_arcanite_rod", "Runed Arcanite Rod", ("bar_arcanite", 2), ("bar_thorium", 2), 275, 275, 300000,
     "gear/gear_epic_wand_3.png"),
]
ROD_IDS = [r[0] for r in RODS]

# ------------------------------------------------------------------ the tiers
#: (prefix, level, skill, rod, dust, essence, shard)
TIERS = [
    ("Minor", 8, 1, "runed_copper_rod", "strange_dust", "lesser_magic_essence", None),
    ("Lesser", 18, 60, "runed_copper_rod", "strange_dust", "greater_magic_essence", "small_glimmering_shard"),
    ("", 28, 115, "runed_silver_rod", "soul_dust", "greater_astral_essence", "large_glimmering_shard"),
    ("Greater", 38, 170, "runed_golden_rod", "vision_dust", "greater_mystic_essence", "large_glowing_shard"),
    ("Superior", 48, 225, "runed_truesilver_rod", "dream_dust", "greater_nether_essence", "large_radiant_shard"),
    ("Major", 58, 280, "runed_arcanite_rod", "illusion_dust", "greater_eternal_essence", "large_brilliant_shard"),
]

#: what an enchantment goes on: label, budget share, how much material it takes
GROUPS = {
    "bracer": ("Bracer", 0.30, 1.0),
    "boots": ("Boots", 0.26, 1.2),
    "gloves": ("Gloves", 0.30, 1.2),
    "cloak": ("Cloak", 0.22, 1.0),
    "chest": ("Chest", 0.40, 1.2),
    "shield": ("Shield", 0.28, 1.2),
    "weapon": ("Weapon", 0.55, 1.6),
    "2h": ("2H Weapon", 0.85, 2.0),
}

#: family -> (name, stat weights, value multiplier, hybrid)
FAMILIES = {
    "sta": ("Stamina", {"stamina": 1.0}, 1.0, False),
    "str": ("Strength", {"strength": 1.0}, 1.0, False),
    "agi": ("Agility", {"agility": 1.0}, 1.0, False),
    "int": ("Intellect", {"intellect": 1.0}, 1.0, False),
    "spi": ("Spirit", {"spirit": 1.0}, 1.0, False),
    "def": ("Deflection", {"defense_rating": 1.0}, 1.0, False),
    "heal": ("Healing", {"healing_power": 1.0}, 1.0, False),
    "sp": ("Spell Power", {"spell_power": 1.0}, 1.0, False),
    "mp5": ("Mana Regeneration", {"mp5": 1.0}, 1.0, False),
    "armor": ("Protection", {"armor": 1.0}, 1.0, False),
    "block": ("Blocking", {"block_value": 1.0}, 1.0, False),
    # five stats, of which a character uses two or three: worth more points than one stat
    "stats": ("Stats", {"stamina": .2, "strength": .2, "agility": .2, "intellect": .2, "spirit": .2},
              1.6, False),
    # hybrids (Kyle: "aim for more hybrid classes rather than the standard")
    "valor": ("Valor", {"strength": .5, "intellect": .5}, 1.0, True),
    "wild": ("Wildheart", {"agility": .5, "intellect": .5}, 1.0, True),
    "battlemage": ("Battlemage", {"attack_power": .5, "spell_power": .5}, 1.0, True),
    "devotion": ("Devotion", {"strength": .5, "healing_power": .5}, 1.0, True),
    "storm": ("Stormcaller", {"agility": .5, "spell_power": .5}, 1.0, True),
    "vigor": ("Vigor", {"strength": .5, "stamina": .5}, 1.0, True),
    "swift": ("Swiftness", {"agility": .5, "stamina": .5}, 1.0, True),
    "sagacity": ("Sagacity", {"intellect": .5, "spirit": .5}, 1.0, True),
    # stamina and armour: defense rating costs 7.5 a point, so a split left it at +1 on every rank
    "warding": ("Warding", {"stamina": .6, "armor": .4}, 1.0, True),
}

#: group -> [(family, first tier)]
LADDERS = {
    "bracer": [("sta", 0), ("str", 0), ("spi", 0), ("agi", 1), ("int", 1), ("mp5", 2),
               ("heal", 3), ("valor", 2), ("wild", 2), ("devotion", 3)],
    "boots": [("sta", 0), ("agi", 0), ("spi", 1), ("swift", 2), ("vigor", 3), ("storm", 4)],
    "gloves": [("str", 1), ("agi", 1), ("sp", 3), ("heal", 3), ("battlemage", 2), ("storm", 3),
               ("valor", 4)],
    # no Deflection: defense rating costs 7.5 a point, so it came out +1 at every rank
    "cloak": [("armor", 0), ("agi", 1), ("warding", 3)],
    "chest": [("sta", 0), ("int", 0), ("stats", 1), ("spi", 2), ("sagacity", 2), ("vigor", 3),
              ("devotion", 4)],
    "shield": [("sta", 0), ("spi", 0), ("block", 1), ("int", 2), ("warding", 2), ("valor", 3)],
    "weapon": [("spi", 1), ("str", 2), ("agi", 2), ("int", 2), ("sp", 3), ("heal", 3), ("valor", 3),
               ("wild", 3), ("battlemage", 4), ("storm", 4)],
    "2h": [("int", 1), ("spi", 1), ("str", 2), ("agi", 2), ("sp", 4), ("valor", 3), ("wild", 4)],
}

#: the proc weapon enchantments ("Yes, a handful"): on the weapon group, so any weapon takes them.
#: (id, name, tier, skill, source, extra inputs, proc)
PROCS = [
    ("fiery", "Fiery Weapon", 3, 190, "vendor", {"crystal_emberglass": 2},
     {"trigger": "on_weapon_swing", "chance": 15, "icd": 0, "damage_flat": 40, "school": "fire",
      "describe": "Your attacks have a chance to burn the target for 40 fire damage."}),
    ("bladesong", "Bladesong", 4, 220, "vendor", {"crystal_azure": 2},
     {"trigger": "on_weapon_swing", "chance": 15, "icd": 3,
      "apply_effect": {"effect_id": "ench_bladesong", "name": "Bladesong", "effect_type": "buff",
                       "duration": 3, "stat_mods": {"spell_power": 30}, "on_target": False},
      "describe": "Your attacks have a chance to grant 30 spell power for 3 turns."}),
    ("spellblade", "Spellblade", 4, 230, "drop", {"crystal_arcane": 1},
     {"trigger": "on_damage_cast", "chance": 15, "icd": 3,
      "apply_effect": {"effect_id": "ench_spellblade", "name": "Spellblade", "effect_type": "buff",
                       "duration": 3, "stat_mods": {"attack_power": 60}, "on_target": False},
      "describe": "Your damaging spells have a chance to grant 60 attack power for 3 turns."}),
    ("lifestealing", "Lifestealing", 4, 235, "drop", {"crystal_voidglass": 2},
     {"trigger": "on_weapon_swing", "chance": 12, "icd": 0, "damage_flat": 30, "school": "shadow",
      "heal_flat": 30,
      "describe": "Your attacks have a chance to steal 30 health from the target."}),
    ("spellsurge", "Spellsurge", 4, 240, "vendor", {"crystal_tideglass": 2},
     {"trigger": "on_cast", "chance": 10, "icd": 3, "grant_resource": {"resource": "mana", "amount": 60},
      "describe": "Your spells have a chance to give you back 60 mana."}),
    ("battlemaster", "Battlemaster", 5, 275, "drop", {"herb_golden_sansam": 4},
     {"trigger": "on_weapon_swing", "chance": 10, "icd": 2, "heal_flat": 60,
      "describe": "Your attacks have a chance to heal you for 60."}),
    ("crusader", "Crusader", 5, 290, "drop", {"herb_black_lotus": 1},
     {"trigger": "on_weapon_swing", "chance": 12, "icd": 2, "heal_flat": 40,
      "apply_effect": {"effect_id": "ench_crusader", "name": "Holy Strength", "effect_type": "buff",
                       "duration": 3, "stat_mods": {"strength": 60}, "on_target": False},
      "describe": "Your attacks have a chance to heal you for 40 and grant 60 Strength for 3 turns."}),
]

# ------------------------------------------------------------------ wands and oils
#: (id, name, level, skill, source, inputs, rarity)
WANDS = [
    ("lesser_magic_wand", "Lesser Magic Wand", 12, 70, "trainer",
     {"plank_softpine": 1, "lesser_magic_essence": 1}, "uncommon"),
    ("greater_magic_wand", "Greater Magic Wand", 17, 110, "trainer",
     {"plank_oakheart": 1, "greater_magic_essence": 1}, "uncommon"),
    ("lesser_mystic_wand", "Lesser Mystic Wand", 30, 155, "trainer",
     {"plank_redbark": 1, "lesser_mystic_essence": 1, "soul_dust": 1}, "uncommon"),
    ("greater_mystic_wand", "Greater Mystic Wand", 35, 175, "vendor",
     {"plank_duskwood": 1, "greater_mystic_essence": 1, "vision_dust": 1}, "uncommon"),
    ("lesser_nether_wand", "Lesser Nether Wand", 43, 215, "trainer",
     {"plank_bloodroot": 1, "lesser_nether_essence": 1, "vision_dust": 2}, "uncommon"),
    ("greater_nether_wand", "Greater Nether Wand", 48, 240, "vendor",
     {"plank_felbark": 1, "greater_nether_essence": 1, "dream_dust": 2}, "uncommon"),
    ("lesser_eternal_wand", "Lesser Eternal Wand", 54, 270, "trainer",
     {"plank_starleaf": 1, "lesser_eternal_essence": 1, "dream_dust": 3, "small_brilliant_shard": 1},
     "uncommon"),
    ("greater_eternal_wand", "Greater Eternal Wand", 59, 295, "drop",
     {"plank_stormoak": 1, "greater_eternal_essence": 2, "illusion_dust": 3, "large_brilliant_shard": 1},
     "rare"),
]

#: weapon oils: (id, name, level, skill, source, weights, icon family, herb)
OIL_SHARE = 0.8
OILS = [
    ("minor_wizard_oil", "Minor Wizard Oil", 10, 30, "trainer", {"spell_power": 1.0}, "elixir_spellpower_lesser", "herb_silverleaf"),
    ("lesser_wizard_oil", "Lesser Wizard Oil", 25, 105, "trainer", {"spell_power": 1.0}, "elixir_spellpower_lesser", "herb_bruiseweed"),
    ("wizard_oil", "Wizard Oil", 40, 180, "vendor", {"spell_power": 1.0}, "elixir_spellpower_greater", "herb_firebloom"),
    ("brilliant_wizard_oil", "Brilliant Wizard Oil", 55, 255, "drop",
     {"spell_power": .8, "crit_chance_spell": .2}, "elixir_spellpower_greater", "herb_dreamfoil"),
    ("minor_mana_oil", "Minor Mana Oil", 20, 80, "trainer", {"mp5": 1.0}, "elixir_intellect_lesser", "herb_briarthorn"),
    ("lesser_mana_oil", "Lesser Mana Oil", 38, 170, "trainer", {"mp5": 1.0}, "elixir_intellect_lesser", "herb_goldthorn"),
    ("brilliant_mana_oil", "Brilliant Mana Oil", 55, 260, "drop",
     {"mp5": .6, "healing_power": .4}, "elixir_intellect_greater", "herb_dreamfoil"),
    # hybrids
    ("battlemage_oil", "Battlemage's Oil", 32, 140, "trainer",
     {"attack_power": .5, "spell_power": .5}, "elixir_attackpower_lesser", "herb_kingsblood"),
    ("superior_battlemage_oil", "Superior Battlemage's Oil", 52, 245, "vendor",
     {"attack_power": .5, "spell_power": .5}, "elixir_attackpower_greater", "herb_sungrass"),
    ("oil_of_devotion", "Oil of Devotion", 45, 210, "vendor",
     {"strength": .5, "healing_power": .5}, "elixir_strength_greater", "herb_purple_lotus"),
]

# ------------------------------------------------------------------ disenchanting
#: Classic's table, by the item's level: (top level of the band, dust, dust count, essence,
#: essence count, the shard a blue gives, enchanting skill needed)
DISENCHANT = [
    (10, "strange_dust", [1, 2], "lesser_magic_essence", [1, 1], "small_glimmering_shard", 1),
    (15, "strange_dust", [2, 3], "greater_magic_essence", [1, 1], "small_glimmering_shard", 1),
    (20, "strange_dust", [2, 3], "greater_magic_essence", [1, 2], "small_glimmering_shard", 1),
    (25, "strange_dust", [4, 6], "lesser_astral_essence", [1, 2], "small_glimmering_shard", 25),
    (30, "soul_dust", [1, 2], "greater_astral_essence", [1, 2], "large_glimmering_shard", 50),
    (35, "soul_dust", [2, 5], "lesser_mystic_essence", [1, 2], "small_glowing_shard", 75),
    (40, "vision_dust", [1, 2], "greater_mystic_essence", [1, 2], "large_glowing_shard", 100),
    (45, "vision_dust", [2, 5], "lesser_nether_essence", [1, 2], "small_radiant_shard", 125),
    (50, "dream_dust", [1, 2], "greater_nether_essence", [1, 2], "large_radiant_shard", 150),
    (55, "dream_dust", [2, 5], "lesser_eternal_essence", [1, 2], "small_brilliant_shard", 175),
    (60, "illusion_dust", [1, 2], "greater_eternal_essence", [1, 2], "large_brilliant_shard", 200),
    (999, "illusion_dust", [2, 5], "greater_eternal_essence", [2, 3], "large_brilliant_shard", 225),
]


def budget(level, share, mult=1.0):
    return level * 0.36 * 1.3 * share * mult


def slug(s):
    return s.lower().replace("'", "").replace(" ", "_")


def copy_icon(src, icon_id):
    ART.mkdir(parents=True, exist_ok=True)
    dst = ART / f"{icon_id}.png"
    if not dst.exists():
        shutil.copyfile(ICONS / src, dst)
    return icon_id


def materials(mats):
    out = {}
    for mid, name, icon, sell in DUSTS:
        out[mid] = {"name": name, "material_type": "enchant_mat", "profession": "enchanting",
                    "tier": "early", "description": "Disenchanted from magic gear. Enchanters use it.",
                    "stack_limit": 20, "sell_price": sell, "icon_id": copy_icon(icon, mid)}
    for key, word, sell in ESSENCES:
        for size, icon_size, mult in (("lesser", "small", 1), ("greater", "large", 3)):
            mid = f"{size}_{key}_essence"
            out[mid] = {"name": f"{size.capitalize()} {word} Essence", "material_type": "enchant_mat",
                        "profession": "enchanting", "tier": "early",
                        "description": "Disenchanted from magic gear, more often from weapons. Three "
                                       "lesser essences make a greater one." if size == "lesser" else
                                       "Disenchanted from magic gear, more often from weapons. It "
                                       "breaks down into three lesser essences.",
                        "stack_limit": 20, "sell_price": sell * mult,
                        "icon_id": copy_icon(f"materials/inv_enchant_essence{ESSENCE_ICON[key]}{icon_size}.png", mid)}
    for mid, name, icon, sell in SHARDS:
        out[mid] = {"name": name, "material_type": "enchant_mat", "profession": "enchanting",
                    "tier": "early",
                    "description": "Disenchanted from rare and epic gear." if mid != "nexus_crystal" else
                                   "Disenchanted from epic gear of the highest levels. Rare.",
                    "stack_limit": 20, "sell_price": sell, "icon_id": copy_icon(icon, mid)}
    for rid, name, _bar, _x, skill, _bs, price, icon in RODS:
        out[rid] = {"name": name, "material_type": "rod", "profession": "enchanting", "tier": "early",
                    "description": f"An enchanter's rod, cut with runes. Formulas from skill {skill} need "
                                   f"this or a better rod in your bags. It isn't used up. Blacksmiths "
                                   f"make them, and enchanters sell them.",
                    "stack_limit": 1, "vendor_price": price, "sell_price": price // 4,
                    "icon_id": copy_icon(icon, rid)}
    copy_icon("quest_items/qi_scroll.png", "enchant_scroll")
    return out


def enchantments():
    """[(enchant id, record)] for every stat enchantment and proc, in list order."""
    from world import jewelcrafting as J
    out = []
    for group, ladder in LADDERS.items():
        label, share, _cost = GROUPS[group]
        for family, first in ladder:
            fname, weights, mult, hybrid = FAMILIES[family]
            tiers = sorted(set(range(first, 6, 2)) | {5})
            for rank, t in enumerate(tiers):
                prefix, level = TIERS[t][0], TIERS[t][1]
                title = f"{prefix} {fname}".strip()
                stats = J.stats_for(weights, budget(level, share, mult))
                eid = f"enchant_{group}_{slug(title)}"
                out.append((eid, {"name": f"Enchant {label}: {title}", "title": title, "group": group,
                                  "family": family, "tier": t, "rank": rank, "level": level,
                                  "skill": TIERS[t][2] + (5 if hybrid else 0), "stats": stats,
                                  "hybrid": hybrid}))
    for pid, name, t, skill, _src, _extra, proc in PROCS:
        out.append((f"enchant_weapon_{pid}", {"name": f"Enchant Weapon: {name}", "title": name,
                                              "group": "weapon", "family": pid, "tier": t, "rank": 0,
                                              "level": TIERS[t][1], "skill": skill, "stats": {},
                                              "proc": proc, "hybrid": pid in ("bladesong", "spellblade")}))
    return out


def inputs_for(e):
    """Dust, essence and (from the third tier, or on weapons) a shard, more for bigger slots."""
    _p, _l, _s, _rod, dust, essence, shard = TIERS[e["tier"]]
    cost = GROUPS[e["group"]][2]
    inp = {dust: max(1, round((1 + e["tier"] * 0.4) * cost)), essence: max(1, round(cost * (0.6 + 0.2 * e["rank"])))}
    if shard and (e["group"] in ("weapon", "2h") or e["tier"] >= 3):
        inp[shard] = 2 if (e["group"] == "2h" and e["tier"] >= 4) else 1
    if e.get("proc"):
        inp[dust] += 2
        inp.update(next(p[5] for p in PROCS if f"enchant_weapon_{p[0]}" == e["_id"]))
    return inp


def source_for(e):
    """Kyle's rule: 50 to 55% of recipes from a trainer. The classic single-stat ladders are
    mostly taught, every other rank found in the world; a hybrid's first rank is taught and the
    rest are found; procs are all found."""
    if e.get("proc"):
        return next(p[4] for p in PROCS if f"enchant_weapon_{p[0]}" == e["_id"])
    if e["hybrid"]:
        return "trainer" if e["rank"] == 0 else ("vendor" if e["rank"] % 2 else "drop")
    if e["rank"] % 2 == 0:
        return "trainer"
    return "vendor" if (e["tier"] + len(e["family"])) % 2 else "drop"


def rods_for(skill):
    """A formula needs a rod of its tier or any better one."""
    i = max(n for n, r in enumerate(RODS) if r[4] <= max(1, skill))
    return ROD_IDS[i:]


def main():
    from world import jewelcrafting as J
    doc = load(MATS)
    mats = doc["materials"]
    for k in [k for k, v in mats.items() if v.get("profession") == "enchanting"]:
        del mats[k]
    new = materials(mats)
    clash = [k for k in new if k in mats]
    assert not clash, f"ids already used: {clash}"
    mats.update(new)

    enchants, recipes = {}, {}
    for eid, e in enchantments():
        e["_id"] = eid
        source = source_for(e)
        inp = inputs_for(e)
        del e["_id"]
        enchants[eid] = e
        mats[eid] = {"name": e["name"], "material_type": "enchant_scroll", "profession": "enchanting",
                     "tier": "early",
                     "description": f"A scroll holding an enchantment for {GROUPS[e['group']][0].lower()}s"
                                    f"{' (any weapon)' if e['group'] == 'weapon' else ''}. Read it onto "
                                    f"gear with the Enchant button in your bags.",
                     "stack_limit": 20, "sell_price": max(10, e["level"] * 8), "icon_id": "enchant_scroll"}
        recipes[f"ench_{eid[8:]}"] = {
            "name": e["name"], "inputs": inp, "skill_required": e["skill"],
            "output": {"kind": "material", "material_id": eid},
            "tool": rods_for(e["skill"]), "skill_range": skill_range(e["skill"]), "source": source}

    # ---- essences, both ways (Kyle, 14 Nov 2026: "3 lesser for 1 greater or 1 greater breaks to 3
    # lesser"). Taught at skill 1, no rod, no skill-ups: it's tidying the bags, not a craft.
    for key, word, _sell in ESSENCES:
        lesser, greater = f"lesser_{key}_essence", f"greater_{key}_essence"
        recipes[f"ench_combine_{key}_essence"] = {
            "name": f"Greater {word} Essence (from 3 Lesser)", "inputs": {lesser: 3}, "skill_required": 1,
            "output": {"kind": "material", "material_id": greater}, "count": 1,
            "skill_range": [0, 0, 0, 0], "source": "trainer", "no_xp": True}
        recipes[f"ench_split_{key}_essence"] = {
            "name": f"Lesser {word} Essence (3, from a Greater)", "inputs": {greater: 1}, "skill_required": 1,
            "output": {"kind": "material", "material_id": lesser}, "count": 3,
            "skill_range": [0, 0, 0, 0], "source": "trainer", "no_xp": True}

    # ---- wands
    for wid, name, level, skill, source, inp, rarity in WANDS:
        for m in inp:
            assert m in mats, f"{wid}: no material {m}"
        recipes[f"ench_{wid}"] = {
            "name": name, "inputs": inp, "skill_required": skill,
            "output": {"kind": "weapon", "slot": "ranged", "weapon_type": "wand",
                       "stat_template": "int_caster", "item_level": level, "rarity": rarity},
            "tool": rods_for(skill), "skill_range": skill_range(skill), "source": source}

    # ---- weapon oils
    cons = load(CONS)
    oils = []
    for oid, name, level, skill, source, weights, icon, herb in OILS:
        stats = J.stats_for(weights, budget(level, OIL_SHARE))
        text = J.stat_text(stats)
        vial = "vial_empty" if level < 20 else ("vial_leaded" if level < 40 else "vial_crystal")
        t = max(i for i, tr in enumerate(TIERS) if tr[1] <= level + 4)
        oils.append({
            "consumable_id": oid, "name": name, "consumable_type": "elixir",
            "description": f"Rub it on your weapon: {text} for 30 minutes. One weapon oil at a time.",
            "effect_value": 0, "effect_duration": 1800, "level_multiplier": 0.0,
            "required_level": max(1, level - 5), "cooldown_seconds": 5, "stack_limit": 20,
            "vendor_price": 0, "sell_price": level * 6, "buff_category": "oil", "stat_bonuses": stats})
        recipes[f"ench_{oid}"] = {
            "name": name, "inputs": {vial: 1, TIERS[t][4]: 1 + t // 2, herb: 1 + (level >= 40)},
            "skill_required": skill, "output": {"kind": "consumable", "consumable_id": oid}, "count": 1,
            "skill_range": skill_range(skill), "source": source}
        dst = ICONS / "consumables" / f"{oid}.png"
        if not dst.exists() and (ICONS / "consumables" / f"{icon}.png").exists():
            shutil.copyfile(ICONS / "consumables" / f"{icon}.png", dst)
    cons["weapon_oils"] = oils
    save(CONS, cons)

    for r in recipes.values():
        for m in r["inputs"]:
            assert m in mats, f"{r['name']}: no material {m}"

    # ---- the rods, at the blacksmith
    bs = load(BS)
    for k in [k for k in bs["recipes"] if k.startswith("bs_runed_")]:
        del bs["recipes"][k]
    for rid, name, (bar, n), (other, m), _skill, bskill, _price, _icon in RODS:
        bs["recipes"][f"bs_{rid}"] = {
            "name": name, "inputs": {bar: n, other: m}, "skill_required": bskill,
            "output": {"kind": "material", "material_id": rid},
            "skill_range": skill_range(bskill), "source": "vendor" if rid == "runed_arcanite_rod" else "trainer",
            "_source": "Enchanting rods (tools/build_enchanting.py). Kyle, 14 Nov 2026: rods will be "
                       "made by Blacksmiths or sold by vendors."}
    save(BS, bs)

    # ---- the profession and its trainers
    profs = load(PROFS)
    profs["professions"]["enchanting"] = {
        "name": "Enchanting", "kind": "crafting",
        "description": "Disenchant magic gear for dust, essences and shards, and enchant gear with "
                       "them. Make wands and weapon oils. Formulas need a runed rod."}
    save(PROFS, profs)
    tr = load(TRAINERS)
    for nid in TRAINER_NPCS:
        tr["profession_trainers"][nid] = ["enchanting"]
    save(TRAINERS, tr)

    save(MATS, doc)
    save(OUT_ENCH, {"_doc": "Written by tools/build_enchanting.py; read by world/enchanting.py.",
                    "groups": {g: {"label": v[0], "share": v[1]} for g, v in GROUPS.items()},
                    "enchants": enchants,
                    "disenchant": [dict(zip(("max_level", "dust", "dust_count", "essence",
                                             "essence_count", "shard", "skill"), row)) for row in DISENCHANT],
                    "rods": ROD_IDS})
    save(OUT_RECIPES, {"_comment": "Enchanting. Written by tools/build_enchanting.py.", "recipes": recipes})

    by_source = {}
    for r in recipes.values():
        by_source[r["source"]] = by_source.get(r["source"], 0) + 1
    hybrids = sum(1 for e in enchants.values() if e["hybrid"])
    print(f"{len(enchants)} enchantments ({hybrids} hybrid, {len(PROCS)} procs), {len(WANDS)} wands, "
          f"{len(OILS)} oils, {len(recipes)} recipes {by_source} "
          f"({100 * by_source.get('trainer', 0) // len(recipes)}% trainer)")
    return 0


#: Kyle: "The town enchanters" teach it. Orgrimmar, Undercity and Kael's Bastion already had one
#: standing in the street; Steamwheedle Port and Onyxhollow get one (tools/build_enchanters.py).
TRAINER_NPCS = ["org_enchanter", "uc_enchanter", "kb_enchanter", "stw_enchanter", "oh_enchanter"]


if __name__ == "__main__":
    sys.exit(main())
