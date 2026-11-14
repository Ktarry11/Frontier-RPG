#!/usr/bin/env python3
"""Jewelcrafting's data: gem colours, cut gems, settings, the kit, and every recipe. Idempotent.

    PYTHONPATH=. python3 tools/build_jewelcrafting.py

Kyle, 14 Nov 2026: "How about we start to build jewel crafting. Since we have gemstones dropping
from ore. Which means we need colours, sockets inside armor (let's have only gear over 30 with
sockets). Jewel crafting also lets you craft rings, necklaces, trinkets. Let's flesh this out. We
have a lot of stuff to work with it. Vendors can sell jewel cutting kits and even sets for
gemstones (for rings or necklaces or they can make them with blacksmith)."

Rules live in world/jewelcrafting.py. This writes:

  data/jewelcrafting/gems.json      every raw gem's colour, quality and level; every cut gem's stats
  data/jewelcrafting/recipes.json   cutting, Prospecting, rings, necklaces and figurine trinkets
  data/gathering/materials.json     cut gems, ring and necklace settings, the Jeweler's Kit
  data/blacksmithing/recipes.json   settings, so a blacksmith can make what a vendor sells
  data/professions/professions.json Jewelcrafting itself
  data/training/trainers.json       taught at the forge, beside mining and blacksmithing

HOW THE GEMS WORK. Colour comes from the stone itself (a ruby is red, a jade is green). Each colour
has its cuts, the way TBC did: a red stone can be cut Bold (strength), Delicate (agility), Bright
(attack power), Runed (spell power) or Teardrop (healing). A hybrid colour's cuts carry half of each
of its two colours. A stone's level comes from the ore it's found in, so a cut gem matches the gear
of the levels where you mine it; the rarer stone in a vein cuts into a rare-quality gem worth more.

RECIPE SOURCES (Kyle, 12 Nov: about half from trainers, the rest from the world). For every stone
its first cut is taught at the trainer; the others are designs, sold by forge-town smiths or
found as drops. Rings, necklaces and Prospecting are trainer-taught. The four figurines that do
something when worn (trinkets over 50 must, Kyle 10 Nov) are drops.
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

MATS = ROOT / "data/gathering/materials.json"
GEM_DROPS = ROOT / "data/gathering/gem_drops.json"
OUT_GEMS = ROOT / "data/jewelcrafting/gems.json"
OUT_RECIPES = ROOT / "data/jewelcrafting/recipes.json"
BS = ROOT / "data/blacksmithing/recipes.json"
PROFS = ROOT / "data/professions/professions.json"
TRAINERS = ROOT / "data/training/trainers.json"

COLOUR = {
    "malachite": "green", "tigerseye": "yellow", "rock_crystal": "prismatic", "bloodstone": "red",
    "azurite": "blue", "moss_agate": "green", "shadowgem": "purple", "lesser_moonstone": "blue",
    "carnelian": "orange", "garnet": "red", "jet": "purple", "honey_amber": "yellow",
    "jade": "green", "citrine": "yellow", "rime_opal": "blue", "topaz": "yellow",
    "pyrite_star": "orange", "peridot": "green", "aquamarine": "blue", "star_ruby": "red",
    "felfire_shard": "green", "heartsblood_garnet": "red", "fire_opal": "orange",
    "deepearth_geode": "purple", "black_diamond": "red", "huge_emerald": "green",
    "truesilver_zircon": "yellow", "amethyst": "purple", "blue_sapphire": "blue",
    "large_opal": "prismatic", "azure_diamond": "blue", "cinder_agate": "orange",
    "elementium_prism": "prismatic", "prismatic_shard": "prismatic",
    # above skill 300, parked with their ores until the level 60 content exists
    "glacier_sapphire": "blue", "sylvan_emerald": "green", "magma_ruby": "red", "sunstone": "yellow",
    "nightshard_onyx": "purple", "abyssal_pearlstone": "blue", "void_amethyst": "purple",
    "stormglass": "blue", "ebon_spinel": "purple", "sundered_tourmaline": "green",
    "starfall_diamond": "prismatic", "astral_moonstone": "blue", "hourglass_topaz": "yellow",
    "titans_eye": "orange", "wyrmheart_ruby": "red", "cataclysm_opal": "orange",
    "dreamers_jade": "green", "primordial_amber": "yellow", "worldheart_crystal": "prismatic",
}

#: colour -> [(cut name, {stat: weight})], TBC's names where TBC had one. Kyle sent the TBC gem list
#: (tbc-bis-guide.com/gems) on 14 Nov; every cut on it that maps onto a stat Frontier has is here.
#: Adapted, not copied (Kyle: "We won't do direct copy paste"): Steady was TBC's resilience gem and
#: Frontier has no resilience, so here it's hit and stamina (TBC's Vivid).
CUTS = {
    "red": [("Bold", {"strength": 1}), ("Delicate", {"agility": 1}),
            ("Runed", {"spell_power": 1}), ("Teardrop", {"healing_power": 1}),
            ("Bright", {"attack_power": 1})],
    "yellow": [("Brilliant", {"intellect": 1}), ("Smooth", {"crit_chance_physical": 1}),
               ("Gleaming", {"crit_chance_spell": 1}), ("Rigid", {"hit_rating": 1}),
               ("Thick", {"defense_rating": 1}), ("Quick", {"haste": 1})],
    "blue": [("Solid", {"stamina": 1}), ("Sparkling", {"spirit": 1}), ("Lustrous", {"mp5": 1}),
             ("Stormy", {"spell_penetration": 1})],
    "orange": [("Inscribed", {"strength": .5, "crit_chance_physical": .5}),
               ("Glinting", {"agility": .5, "hit_rating": .5}),
               ("Potent", {"spell_power": .5, "crit_chance_spell": .5}),
               ("Luminous", {"healing_power": .5, "intellect": .5}),
               ("Wicked", {"attack_power": .5, "crit_chance_physical": .5}),
               ("Etched", {"strength": .5, "hit_rating": .5}),
               ("Veiled", {"spell_power": .5, "hit_rating": .5})],
    "green": [("Jagged", {"crit_chance_physical": .5, "stamina": .5}),
              ("Enduring", {"defense_rating": .5, "stamina": .5}),
              ("Dazzling", {"intellect": .5, "mp5": .5}),
              ("Sundered", {"crit_chance_physical": .5, "mp5": .5}),
              ("Lambent", {"hit_rating": .5, "mp5": .5})],
    "purple": [("Sovereign", {"strength": .5, "stamina": .5}),
               ("Shifting", {"agility": .5, "stamina": .5}),
               ("Glowing", {"spell_power": .5, "stamina": .5}),
               ("Royal", {"healing_power": .5, "mp5": .5}),
               ("Balanced", {"attack_power": .5, "stamina": .5}),
               ("Regal", {"dodge_rating": .5, "stamina": .5}),
               ("Purified", {"healing_power": .5, "spirit": .5}),
               ("Fluorescent", {"spell_power": .5, "spirit": .5})],
    "prismatic": [("Prismatic", {"strength": .2, "agility": .2, "intellect": .2, "stamina": .2,
                                 "spirit": .2})],
}
MAX_SKILL = 300          # recipes for stones above this wait with their ores
RARE_CHANCE = 0.025      # a stone this rare in its vein cuts into a rare-quality gem

#: ring and necklace tiers: (metal, bar, skill, item level, stones by colour to set in them)
TIERS = [
    ("copper", "bar_copper", 20, 12, {"red": "bloodstone", "yellow": "tigerseye", "blue": "azurite"}),
    ("silver", "bar_silver", 90, 24, {"red": "garnet", "yellow": "honey_amber", "blue": "lesser_moonstone"}),
    ("gold", "bar_gold", 160, 36, {"red": "carnelian", "yellow": "citrine", "blue": "rime_opal"}),
    ("mithril", "bar_mithril", 195, 44, {"red": "star_ruby", "yellow": "topaz", "blue": "aquamarine"}),
    ("truesilver", "bar_truesilver", 240, 52, {"red": "black_diamond", "yellow": "truesilver_zircon",
                                                "blue": "blue_sapphire"}),
    ("thorium", "bar_thorium", 275, 58, {"red": "heartsblood_garnet", "yellow": "large_opal",
                                         "blue": "azure_diamond"}),
]
#: (kind, slot, template, stone colour, name pattern)
JEWELLERY = [
    ("ring", "ring", "str_physical", "red", "{stone} Signet"),
    ("ring", "ring", "agi_physical", "red", "{stone} Band"),
    ("ring", "ring", "int_caster", "yellow", "{stone} Loop"),
    ("ring", "ring", "spi_healer", "blue", "{stone} Circle"),
    ("necklace", "neck", "str_physical", "red", "{stone} Pendant"),
    ("necklace", "neck", "int_caster", "yellow", "{stone} Choker"),
    ("necklace", "neck", "spi_healer", "blue", "{stone} Locket"),
]
VENDOR_SETTINGS = ("copper", "silver", "gold")   # higher settings come from a blacksmith

TRINKETS = [
    dict(id="jc_jade_owl", name="Jade Owl", skill=120, item_level=30, rarity="uncommon",
         inputs={"gem_jade": 2, "bar_iron": 2}, source="trainer",
         primary_stats={"intellect": 6, "spirit": 4}),
    dict(id="jc_carnelian_fox", name="Carnelian Fox", skill=150, item_level=34, rarity="uncommon",
         inputs={"gem_carnelian": 2, "bar_iron": 2}, source="trainer",
         primary_stats={"agility": 7, "stamina": 4}),
    dict(id="jc_star_ruby_lion", name="Star Ruby Lion", skill=255, item_level=54, rarity="rare",
         inputs={"gem_star_ruby": 2, "gem_topaz": 2, "bar_truesilver": 3}, source="drop",
         primary_stats={"strength": 12, "stamina": 9},
         proc={"trigger": "on_crit", "chance": 15, "icd": 5,
               "apply_effect": {"effect_id": "jc_lion_roar", "name": "Lion's Roar",
                                "effect_type": "buff", "duration": 3,
                                "stat_mods": {"attack_power": 46}, "on_target": False},
               "describe": "Your critical strikes have a chance to grant 46 attack power for 3 turns."}),
    dict(id="jc_aquamarine_heron", name="Aquamarine Heron", skill=265, item_level=56, rarity="rare",
         inputs={"gem_aquamarine": 3, "gem_huge_emerald": 1, "bar_truesilver": 3}, source="drop",
         primary_stats={"intellect": 9, "spirit": 9},
         proc={"trigger": "on_heal_cast", "chance": 10, "icd": 5,
               "apply_effect": {"effect_id": "jc_heron_still_water", "name": "Still Water",
                                "effect_type": "buff", "duration": 3,
                                "stat_mods": {"healing_power": 42}, "on_target": False},
               "describe": "Your healing spells have a chance to grant 42 healing power for 3 turns."}),
    dict(id="jc_black_diamond_crab", name="Black Diamond Crab", skill=275, item_level=57, rarity="rare",
         inputs={"gem_black_diamond": 2, "gem_amethyst": 2, "bar_thorium": 3}, source="drop",
         primary_stats={"stamina": 14}, secondary_stats={"defense_rating": 1},
         proc={"trigger": "on_damage_taken", "chance": 10, "icd": 5,
               "apply_effect": {"effect_id": "jc_crab_shell", "name": "Diamond Shell",
                                "effect_type": "buff", "duration": 3,
                                "stat_mods": {"armor": 400}, "on_target": False},
               "describe": "When you are hit, you have a chance to gain 400 armour for 3 turns."}),
    dict(id="jc_blue_sapphire_owl", name="Blue Sapphire Owl", skill=285, item_level=58, rarity="rare",
         inputs={"gem_blue_sapphire": 3, "gem_large_opal": 1, "bar_thorium": 3}, source="drop",
         primary_stats={"intellect": 11, "stamina": 8},
         proc={"trigger": "on_damage_cast", "chance": 8, "icd": 5,
               "apply_effect": {"effect_id": "jc_owl_night_sight", "name": "Night Sight",
                                "effect_type": "buff", "duration": 3,
                                "stat_mods": {"spell_power": 34}, "on_target": False},
               "describe": "Your damaging spells have a chance to grant 34 spell power for 3 turns."}),
]
TRINKET_ICONS = {"jc_jade_owl": "gear_inv_jewelry_talisman_01",
                 "jc_carnelian_fox": "gear_inv_jewelry_talisman_03",
                 "jc_star_ruby_lion": "gear_inv_jewelry_talisman_04",
                 "jc_aquamarine_heron": "gear_inv_jewelry_talisman_01",
                 "jc_black_diamond_crab": "gear_inv_jewelry_talisman_03",
                 "jc_blue_sapphire_owl": "gear_inv_jewelry_talisman_04"}


#: META GEMS, written but switched off (Kyle, 14 Nov 2026: "Let's do meta gem code but not integrate
#: it yet"). Cut from the Starfall Diamond, which sits above skill 300 with its ore, so nothing can
#: make one until both are turned on. Adapted from TBC's meta gems, not copied: each pairs a
#: stat with an effect and a condition on the wearer's other gems.
META = [
    ("relentless", {"agility": 1}, {"crit_damage_pct": 3}, {"at_least": {"red": 2, "yellow": 2, "blue": 2}},
     "+3% critical strike damage"),
    ("chaotic", {"crit_chance_spell": 1}, {"spell_crit_damage_pct": 3}, {"at_least": {"blue": 2}},
     "+3% spell critical damage"),
    ("powerful", {"stamina": 1}, {"stun_resist_pct": 5}, {"at_least": {"blue": 3}},
     "5% chance to resist a stun"),
    ("insightful", {"intellect": 1}, {"mana_on_cast_pct": 2}, {"each": 2},
     "Your spells have a chance to restore mana"),
    ("bracing", {"healing_power": 1}, {"threat_pct": -2}, {"more": ["red", "blue"]},
     "2% less threat"),
    ("eternal", {"defense_rating": 1}, {"block_value_pct": 10}, {"at_least": {"blue": 2, "yellow": 1}},
     "+10% shield block value"),
]


def meta_gems(J):
    out = {}
    level = 60
    for name, weights, effects, req, effect_text in META:
        stats = J.stats_for(weights, J.gem_budget(level, "rare") * 1.5)
        out[f"meta_{name}_starfall_diamond"] = {
            "name": f"{name.capitalize()} Starfall Diamond", "color": "meta", "level": level,
            "stats": stats, "effects": effects, "requires": req,
            "describe": effect_text + ". " + J.requirement_text(req) + "."}
    return out


def skill_range(skill):
    return [skill, skill + 10, skill + 20, skill + 30]


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def save(p, d):
    """Write in whatever layout the file already had, so a diff shows only what changed."""
    p.parent.mkdir(parents=True, exist_ok=True)
    style = (2, False)
    if p.exists():
        raw = p.read_text(encoding="utf-8")
        old = json.loads(raw)
        style = next(((i, asc) for i in (2, 4, 1, None) for asc in (False, True)
                      if json.dumps(old, indent=i, ensure_ascii=asc) == raw.rstrip("\n")), style)
    p.write_text(json.dumps(d, indent=style[0], ensure_ascii=style[1]) + "\n", encoding="utf-8")


def main():
    from world import jewelcrafting as J
    doc = load(MATS)
    mats = doc["materials"]
    drops = load(GEM_DROPS)["drops"]
    ore_of = {g: ore for ore, rows in drops.items() for g, _c in rows}
    chance_of = {g: c for rows in drops.values() for g, c in rows}

    # ---- clear what this script wrote last time
    for k in [k for k, v in mats.items() if v.get("material_type") == "cut_gem"
              or k.startswith("setting_") or k == "jewelers_kit"]:
        del mats[k]

    raw, cuts, recipes = {}, {}, {}
    rng = random.Random(14112026)
    for gid, m in list(mats.items()):
        if m.get("material_type") != "gem":
            continue
        key = gid[4:]
        colour = COLOUR.get(key)
        assert colour, f"{gid} has no colour"
        ore = ore_of[gid]
        skill = mats[ore]["skill_range"][0]
        level = max(5, min(60, skill // 5 + 5))
        quality = "rare" if chance_of[gid] <= RARE_CHANCE else "uncommon"
        raw[gid] = {"color": colour, "quality": quality, "level": level, "ore": ore, "skill": skill}
        budget = J.gem_budget(level, quality)
        n = -1
        for cut, weights in CUTS[colour]:
            cid = f"cut_{cut.lower()}_{key}"
            name = m["name"] if cut == "Prismatic" and "Prism" in m["name"] else f"{cut} {m['name']}"
            costs = J.stat_costs()
            raw_vals = {st: budget * w / costs.get(st, 1.0) for st, w in weights.items()}
            if cut == "Prismatic":
                # a little of everything, as far as the budget goes: a low stone gives one point
                order = ["stamina", "strength", "agility", "intellect", "spirit"]
                points = max(1, int(budget + 0.5))
                stats = {st: points // 5 + (1 if i < points % 5 else 0) for i, st in enumerate(order)}
                stats = {k: v for k, v in stats.items() if v}
            elif min(raw_vals.values()) < 0.5:
                # ONE FORMULA: a cut whose costly stat would round up from almost nothing (a 1%
                # crit gem at level 5) isn't offered on that stone; it would be worth ten times
                # its level. It appears on the stones high enough to pay for it.
                continue
            else:
                stats = J.stats_for(weights, budget)
            cuts[cid] = {"name": name, "color": colour, "quality": quality, "level": level,
                         "stats": stats, "raw": gid, "cut": cut}
            stat_text = ", ".join(f"+{v} {k.replace('_', ' ')}" for k, v in stats.items())
            fits = " or ".join(sorted(J.FITS[colour])) if colour != "prismatic" else "any"
            mats[cid] = {
                "name": name, "material_type": "cut_gem", "profession": "jewelcrafting",
                "tier": m["tier"],
                "description": f"A cut {colour} gem: {stat_text}. Fits a {fits} socket.",
                "stack_limit": 20, "sell_price": int(m["sell_price"] * 1.5),
                "icon_id": m["icon_id"], "skill_range": list(m["skill_range"]),
            }
            n += 1
            if skill > MAX_SKILL:
                continue
            # the first two cuts of every stone are taught; the rest are designs found in the world
            source = "trainer" if n == 0 else ("vendor" if n % 2 == 1 else "drop")
            rskill = max(1, skill) + (0 if n == 0 else 10)
            recipes[f"jc_{cid}"] = {
                "name": name, "inputs": {gid: 1}, "skill_required": rskill,
                "output": {"kind": "material", "material_id": cid}, "tool": "jewelers_kit",
                "skill_range": skill_range(rskill), "source": source,
            }

    # ---- Prospecting: crush five ore for that ore's stones
    for ore, rows in drops.items():
        skill = mats[ore]["skill_range"][0]
        if skill > MAX_SKILL:
            continue
        rskill = max(20, skill)
        recipes[f"jc_prospect_{ore[4:]}"] = {
            "name": f"Prospect {mats[ore]['name']}", "inputs": {ore: 5}, "skill_required": rskill,
            "output": {"kind": "prospect", "ore": ore}, "tool": "jewelers_kit",
            "skill_range": skill_range(rskill), "source": "trainer",
        }

    # ---- the kit and the settings
    mats["jewelers_kit"] = {
        "name": "Jeweler's Kit", "material_type": "kit", "profession": "jewelcrafting",
        "tier": "starter",
        "description": "Files, a loupe, tweezers and a polishing wheel in a roll of leather. Every "
                       "jewelcrafting recipe needs one in your bags. It isn't used up.",
        "stack_limit": 1, "vendor_price": 250, "sell_price": 60, "icon_id": "jewelers_kit"}
    bs = load(BS)
    for k in [k for k in bs["recipes"] if k.startswith("bs_setting_")]:
        del bs["recipes"][k]
    for metal, bar, skill, _il, _stones in TIERS:
        price = mats[bar].get("sell_price", 10)
        for kind, n_bars in (("ring", 1), ("necklace", 2)):
            sid = f"setting_{kind}_{metal}"
            mats[sid] = {
                "name": f"{metal.capitalize()} {kind.capitalize()} Setting", "material_type": "part",
                "profession": "jewelcrafting", "tier": mats[bar]["tier"],
                "description": f"A plain {metal} {'band' if kind == 'ring' else 'chain and clasp'} "
                               f"with an empty mount, waiting for a stone. Blacksmiths make them; "
                               f"some shops sell the plainer ones.",
                "stack_limit": 20, "vendor_price": price * n_bars * 4, "sell_price": price * n_bars,
                "icon_id": sid}
            bskill = max(1, skill - 15)
            bs["recipes"][f"bs_{sid}"] = {
                "name": mats[sid]["name"],
                "inputs": {bar: n_bars + 1, "flux_weak" if skill < 100 else
                           ("flux_medium" if skill < 200 else "flux_strong"): 1},
                "skill_required": bskill,
                "output": {"kind": "material", "material_id": sid},
                "skill_range": skill_range(bskill), "source": "trainer",
                "_source": "Jewelcrafting settings (tools/build_jewelcrafting.py). Kyle, 14 Nov 2026: "
                           "vendors can sell settings for gemstones, or they can make them with "
                           "blacksmith."}

    # ---- rings and necklaces
    for t, (metal, bar, skill, il, stones) in enumerate(TIERS):
        for i, (kind, slot, template, colour, pattern) in enumerate(JEWELLERY):
            stone = stones[colour]
            gid = f"gem_{stone}"
            rarity = "rare" if t >= 4 and i in (0, 3, 4) else "uncommon"
            rskill = skill + (i % 4) * 5
            stone_name = mats[gid]["name"]
            rid = f"jc_{slot}_{metal}_{template}"
            recipes[rid] = {
                "name": pattern.format(stone=stone_name),
                "inputs": {f"setting_{kind}_{metal}": 1, bar: 1, gid: 1 if rarity == "uncommon" else 2},
                "skill_required": rskill,
                "output": {"kind": "armor", "slot": slot, "armor_type": None,
                           "stat_template": template, "item_level": il + (i % 4), "rarity": rarity,
                           "material_tier": metal},
                "tool": "jewelers_kit", "skill_range": skill_range(rskill), "source": "trainer"}

    # ---- figurines
    for tk in TRINKETS:
        item = {"name": tk["name"], "slot": "trinket", "item_level": tk["item_level"],
                "rarity": tk["rarity"], "required_level": tk["item_level"] - 2,
                "primary_stats": tk["primary_stats"],
                "secondary_stats": tk.get("secondary_stats", {}),
                "icon_id": TRINKET_ICONS[tk["id"]]}
        if tk.get("proc"):
            item["proc"] = tk["proc"]
        recipes[tk["id"]] = {
            "name": tk["name"], "inputs": tk["inputs"], "skill_required": tk["skill"],
            "output": {"kind": "fixed", "item": item}, "tool": "jewelers_kit",
            "skill_range": skill_range(tk["skill"]), "source": tk["source"]}

    # ---- the profession and its trainers
    profs = load(PROFS)
    profs["professions"]["jewelcrafting"] = {
        "name": "Jewelcrafting", "kind": "crafting",
        "description": "Cut gems for sockets, crush ore for stones, and make rings, necklaces and "
                       "figurines. Needs a Jeweler's Kit."}
    save(PROFS, profs)
    tr = load(TRAINERS)
    taught = 0
    for nid, plist in tr["profession_trainers"].items():
        if "mining" in plist and "blacksmithing" in plist:
            if "jewelcrafting" not in plist:
                plist.append("jewelcrafting")
            taught += 1
    save(TRAINERS, tr)
    for path in (ROOT / "data/npcs/ambient_npcs.json", ROOT / "data/npcs/vendors.json"):
        d = load(path)
        rows = d.get("npcs") or d.get("vendors") or []
        for r in rows:
            tp = r.get("trains_profession")
            if isinstance(tp, list) and "mining" in tp and "blacksmithing" in tp \
                    and "jewelcrafting" not in tp:
                tp.append("jewelcrafting")
        save(path, d)

    save(MATS, doc)
    save(BS, bs)
    save(OUT_GEMS, {"_doc": "Written by tools/build_jewelcrafting.py; read by world/jewelcrafting.py.",
                    "raw_gems": raw, "cut_gems": cuts, "meta_gems": meta_gems(J)})
    save(OUT_RECIPES, {"_comment": "Jewelcrafting. Written by tools/build_jewelcrafting.py.",
                       "recipes": recipes})
    by_source = {}
    for r in recipes.values():
        by_source[r["source"]] = by_source.get(r["source"], 0) + 1
    print(f"{len(raw)} stones, {len(cuts)} cuts, {len(recipes)} recipes {by_source}, "
          f"{taught} forge trainers teach it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
