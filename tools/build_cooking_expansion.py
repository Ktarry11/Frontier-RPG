#!/usr/bin/env python3
"""Cooking, widened: six more lines of food, six pantry goods, and a real icon for every meal.

    PYTHONPATH=. python3 tools/build_cooking_expansion.py [--pack "/path/to/WoW Icon Pack"]

Kyle, 12 Nov 2026, looking at the Cooking tab for the first time (it had no tab until today):
"Lets use some WoW icons we have on file for cooking bro. Also food should give buffs! And we
can expand out a lot more cooking too rather than....whatever that is."

WHAT WAS THERE: 22 recipes, every one "N pieces of one meat", three buffs per tier (stamina,
agility, intellect), and a recipe row that showed the meat and never said what the meal did.

WHAT THIS ADDS. Six lines, one meal per meat tier each (48), so a cook has something for every
role at every level instead of three stat sticks:

    line        pantry good        well fed
    Hearty      Flour              Stamina + health every turn   (the hp5 tank's dinner)
    Sweet       Wild Honey         Spirit + mana every turn
    Spiced      Hot Spices         Attack Power
    Mushroom    Cellar Mushrooms   Spell Power
    Cheese      Sharp Cheese       Healing
    Ale         Cooking Ale        Armor (+ Dodge from the fourth tier)

plus four resistance stews at the Rich Cut tier. The pantry goods are bought, a few copper
each, wherever salt already is and from every innkeeper and camp cook, so the meat is still
what you hunt and the profession is not gated behind a second gathering skill.

ICONS come from the WoW icon pack; with --pack every cooked meal (old and new) and each pantry
good gets its own. Without it the data is still built and only missing art is reported.

Idempotent: everything is keyed by id and replaced, nothing appended twice. It never touches
the 22 recipes that already exist beyond giving them an icon.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: meat, level, base skill, health restored, seconds, sell price
TIERS = [
    ("meat_stringy", 1, 0, 250, 20, 8),
    ("meat_lean", 8, 50, 380, 22, 15),
    ("meat_thick", 16, 100, 520, 24, 22),
    ("meat_rich", 24, 150, 690, 26, 30),
    ("meat_prime", 32, 200, 900, 28, 38),
    ("meat_marbled", 38, 195, 1100, 30, 88),
    ("meat_aged", 46, 235, 1400, 32, 98),
    ("meat_select", 54, 270, 1800, 34, 108),
]

#: id -> (name, vendor price, tier word, description, pack icon)
PANTRY = {
    "cook_flour": ("Flour", 3, "starter", "Milled fine. Thickens a stew, wraps a pie.", "Food_Wheat_01.png"),
    "cook_honey": ("Wild Honey", 8, "early", "Dark, and it does not pour so much as give way.", "Food_109_HoneyLichen.png"),
    "cook_spice": ("Hot Spices", 8, "early", "A twist of paper. Do not touch your eyes.", "ToW_SpicePotion01.png"),
    "cook_mushroom": ("Cellar Mushrooms", 6, "early", "Grown in the dark on purpose.", "Food_96_ZangarCaps.png"),
    "cook_cheese": ("Sharp Cheese", 6, "early", "Hard, yellow, and older than the innkeeper admits.", "Food_03.png"),
    "cook_ale": ("Cooking Ale", 8, "early", "Not for drinking. People drink it.", "Beer_01.png"),
}

#: line key -> (pantry good, per-tier buffs, flavour, [8 names], [8 pack icons])
A = lambda *v: list(v)
LINES = {
    "hearty": ("cook_flour",
               {"stamina": A(3, 5, 7, 9, 12, 14, 17, 20), "hp5": A(2, 3, 5, 7, 9, 11, 13, 16)},
               "Heavy, hot, and it stays with you.",
               ["Trail Dumplings", "Hunter's Pie", "Ironpot Stew", "Marrow Pie", "Warden's Pot Roast",
                "Stockade Hotpot", "Long-Simmer Shank", "Bulwark Feast"],
               ["Food_DimSum.png", "Food_10.png", "Food_64.png", "Food_103_PotatoBread.png", "Food_15.png",
                "Food_117_HeartySoup.png", "Food_84_RoastClefthoof.png", "Food_115_CondorSoup.png"]),
    "sweet": ("cook_honey",
              {"spirit": A(3, 5, 7, 9, 12, 14, 17, 20), "mp5": A(2, 3, 4, 6, 8, 9, 11, 13)},
              "Sweet over smoke. It clears the head.",
              ["Honeyed Strips", "Orchard-Glaze Cut", "Applewood Chop", "Sage-Honey Roast", "Fruit-Stuffed Loin",
               "Mead-Braised Steak", "Vigil Supper", "Seer's Table"],
              ["25_HoneyTea.png", "Food_106_FjordPeach.png", "Food_19.png", "Food_73CinnamonRoll.png",
               "Food_105_SnowPlum.png", "Food_108_MeadCaribou.png", "Food_104_TundraBerries.png", "Food_145_Cake.png"]),
    "spiced": ("cook_spice",
               {"attack_power": A(6, 10, 14, 20, 26, 30, 36, 44)},
               "Hot enough to make you want to hit something.",
               ["Spiced Jerky", "Pepper-Crust Chop", "Firebrand Ribs", "Redpepper Haunch", "Warband Grill",
                "Bloodspice Steak", "Reaver's Rack", "Champion's Carvery"],
               ["Food_66.png", "Food_47.png", "Food_48.png", "Food_116_CondorLeg.png", "Food_124_Skewer.png",
                "Food_122_Steak.png", "Food_86_Basilisk.png", "Food_119_RhinoMeat.png"]),
    "mushroom": ("cook_mushroom",
                 {"spell_power": A(4, 7, 10, 14, 18, 21, 25, 30)},
                 "Earthy, and faintly luminous if you leave it too long.",
                 ["Mushroom Skewer", "Cellar-Cap Fry", "Glowcap Ragout", "Scholar's Fricassee", "Nightcap Roast",
                  "Arcanist's Plate", "Duskcap Roulade", "Magister's Supper"],
                 ["Food_87_SporelingSnack.png", "Food_91.png", "Food_112_Frostcaps.png", "27_BlueSoup.png",
                  "Food_78.png", "ToW_SpiceBowl.png", "Food_67.png", "Food_79.png"]),
    "cheese": ("cook_cheese",
               {"healing_power": A(7, 12, 18, 25, 33, 38, 46, 55)},
               "Melted over everything. Nobody has ever been sad eating it.",
               ["Cheese Toastie", "Melted Cut", "Herder's Bake", "Mender's Gratin", "Hearthkeeper's Pie",
                "Chaplain's Platter", "Mercy Roast", "Lifewarden's Board"],
               ["Food_35.png", "Food_04.png", "Food_102_FlatBread.png", "Food_100_HardCheese.png",
                "Food_94_GaradarSharp .png", "Food_95_Grainbread.png", "Food_101_SourCheese.png", "Food_37.png"]),
    "ale": ("cook_ale",
            {"armor": A(20, 40, 70, 100, 140, 170, 210, 260), "dodge": A(0, 0, 0, 1, 1, 1, 2, 2)},
            "Boiled in ale until it stops arguing.",
            ["Ale-Boiled Strips", "Tavern Chop", "Brewer's Brisket", "Stout Stew", "Black-Ale Roast",
             "Shieldwall Steak", "Keg-Braised Shank", "Old Guard's Feast"],
            ["Food_53.png", "Food_52.png", "Food_65.png", "Food_49.png", "Food_123_Roast.png",
             "Food_85_StegadonBite.png", "Food_88_RavagerNuggets.png", "BrewfestBuff_01.png"]),
}

#: Four stews at the Rich Cut tier: (slug, name, second ingredient, stat, flavour, icon)
RESIST = [
    ("emberproof_stew", "Emberproof Stew", "cook_spice", "fire_resistance", "So hot the fire seems reasonable after.", "FireDrink_1.png"),
    ("frostbite_chowder", "Frostbite Chowder", "cook_flour", "frost_resistance", "Thick enough to stand a spoon in. Keeps the cold out.", "26_GoatsMilk.png"),
    ("greenroot_broth", "Greenroot Broth", "cook_mushroom", "nature_resistance", "Bitter. Whatever bites you afterwards regrets it.", "Food_57.png"),
    ("gravewatch_pottage", "Gravewatch Pottage", "cook_cheese", "shadow_resistance", "What the night watch eats. They are still here.", "ShadowEgg.png"),
]

#: Icons for the 22 meals that already existed, by name.
OLD_ICONS = {
    "Campfire Strips": "Food_133_Meat.png", "Fire-Charred Skewers": "Food_68.png", "Thin Broth": "Food_63.png",
    "Seared Cut": "Food_135_Meat.png", "Peppered Strips": "Food_72.png", "Barley Pottage": "Food_11.png",
    "Herb-Crusted Roast": "Food_69.png", "Quickfire Cutlets": "Food_70.png", "Clear Consomme": "Milk_03.png",
    "Slow Stew": "Food_27.png", "Seared Medallions": "Food_50.png", "Spiced Terrine": "Food_89.png",
    "Feast Roast": "Food_121_ButterMeat.png", "Blackened Loin": "Food_90.png", "Roast Royale": "Food_99.png",
    "Marbled Steak": "FOOD_80.png", "Hunter's Board": "Food_107_Venison.png", "Aged Roast": "FOOD_82.png",
    "Feast Platter": "Food_98_Talbuk.png", "Select Cut Dinner": "FOOD_83_TALBUKSTEAK.png",
    "Banquet Service": "Food_134_Meat.png", "Cook's Own Table": "Food_77.png",
}

LABEL = {"stamina": "Stamina", "spirit": "Spirit", "hp5": "Health per turn", "mp5": "Mana per turn",
         "attack_power": "Attack Power", "spell_power": "Spell Power", "healing_power": "Healing",
         "armor": "Armor", "dodge": "% Dodge", "fire_resistance": "Fire Resistance",
         "frost_resistance": "Frost Resistance", "nature_resistance": "Nature Resistance",
         "shadow_resistance": "Shadow Resistance"}


def slug(name):
    return "".join(c if c.isalnum() else "_" for c in name.lower()).strip("_").replace("__", "_").replace("__", "_")


def buff_text(bonuses):
    return ", ".join(f"+{v}{LABEL[k]}" if LABEL[k].startswith("%") else f"+{v} {LABEL[k]}"
                     for k, v in bonuses.items())


def meal(cid, name, flavour, tier, bonuses):
    _meat, level, _skill, total, secs, sell = tier
    return {
        "consumable_id": cid, "name": name, "consumable_type": "meal",
        "description": f"{flavour} Restores {total} health over {secs} seconds while you rest, "
                       f"and leaves you well fed ({buff_text(bonuses)}) for 30 minutes.",
        "effect_value": total, "effect_duration": secs, "level_multiplier": 0.0,
        "required_level": level, "cooldown_seconds": 2, "stack_limit": 20,
        "vendor_price": 0, "sell_price": sell, "buff_category": "food", "stat_bonuses": bonuses,
    }


def build():
    """[(recipe_id, recipe, meal, pack icon)] for everything this adds."""
    out = []
    for li, (key, (good, buffs, flavour, names, icons)) in enumerate(LINES.items()):
        for ti, tier in enumerate(TIERS):
            meat, level, base, *_ = tier
            name = names[ti]
            bonuses = {k: v[ti] for k, v in buffs.items() if v[ti]}
            skill = min(300, base + 5 + li * 6)
            rid = f"cookx_{slug(name)}"
            recipe = {"name": name, "skill_required": skill,
                      "inputs": {meat: 2 if ti < 3 else 3, good: 1 if ti < 5 else 2},
                      "output": {"kind": "consumable", "consumable_id": f"meal_cooked_{slug(name)}", "count": 1}}
            if ti >= 5:                      # the late tiers follow the 300 build: trainer-taught, with a range
                recipe["skill_range"] = [skill + 5, skill + 15, skill + 25, skill + 35]
                recipe["source"] = "trainer"
            out.append((rid, recipe, meal(f"meal_cooked_{slug(name)}", name, flavour, tier, bonuses), icons[ti]))
    tier = TIERS[3]
    for i, (s, name, good, stat, flavour, icon) in enumerate(RESIST):
        recipe = {"name": name, "skill_required": 160 + i * 5, "inputs": {"meat_rich": 2, good: 2},
                  "output": {"kind": "consumable", "consumable_id": f"meal_cooked_{s}", "count": 1}}
        out.append((f"cookx_{s}", recipe, meal(f"meal_cooked_{s}", name, flavour, tier, {stat: 15, "stamina": 5}), icon))
    return out


def main():
    pack = Path(sys.argv[sys.argv.index("--pack") + 1]) if "--pack" in sys.argv else None
    built = build()

    mp = ROOT / "data/gathering/materials.json"
    mdata = json.loads(mp.read_text())
    mats = mdata.get("materials", mdata)
    for mid, (name, price, tier, desc, _icon) in PANTRY.items():
        mats[mid] = {"name": name, "material_type": "reagent", "profession": "cooking", "tier": tier,
                     "description": desc, "stack_limit": 20, "vendor_price": price,
                     "sell_price": max(1, price // 4), "icon_id": mid}
    mp.write_text(json.dumps(mdata, indent=2, ensure_ascii=False) + "\n")

    cp = ROOT / "data/consumables/consumable_types.json"
    cdata = json.loads(cp.read_text())
    mine = {m["consumable_id"] for _r, _rec, m, _i in built}
    cdata["cooked_meals"] = [m for m in cdata["cooked_meals"] if m["consumable_id"] not in mine] \
        + [m for _r, _rec, m, _i in built]
    cp.write_text(json.dumps(cdata, indent=2, ensure_ascii=False) + "\n")

    rp = ROOT / "data/crafting/recipes.json"
    rdata = json.loads(rp.read_text())
    recipes = rdata["professions"]["cooking"]["recipes"] if "recipes" in rdata["professions"]["cooking"] \
        else rdata["professions"]["cooking"]
    for rid, recipe, _m, _i in built:
        recipes[rid] = recipe
    rp.write_text(json.dumps(rdata, indent=2, ensure_ascii=False) + "\n")

    vp = ROOT / "data/npcs/vendors.json"
    vdata = json.loads(vp.read_text())
    vendors = vdata.get("vendors", vdata)
    vendors = vendors if isinstance(vendors, list) else list(vendors.values())
    stocked = 0
    for v in vendors:
        sells = v.get("sells")
        if not isinstance(sells, list):
            continue
        vid = str(v.get("vendor_id", ""))
        if "salt" in sells or "innkeeper" in vid or vid.endswith("_cook") or "cook" in vid.split("_"):
            for mid in PANTRY:
                if mid not in sells:
                    sells.append(mid)
            stocked += 1
    vp.write_text(json.dumps(vdata, indent=2, ensure_ascii=False) + "\n")

    copied = missing = 0
    if pack is not None:
        from PIL import Image
        src = pack / "Miscellaneous"
        by_name = {m["name"]: m["consumable_id"] for m in cdata["cooked_meals"]}
        jobs = [(ROOT / "assets/icons/consumables" / f"{m['consumable_id']}.png", icon, 96) for _r, _rec, m, icon in built]
        jobs += [(ROOT / "assets/icons/consumables" / f"{by_name[n]}.png", icon, 96) for n, icon in OLD_ICONS.items() if n in by_name]
        jobs += [(ROOT / "assets/gathering_nodes/reagents" / f"{mid}.png", p[4], 32) for mid, p in PANTRY.items()]
        for dest, icon, size in jobs:
            if not (src / icon).is_file():
                print("  no such pack icon:", icon)
                missing += 1
                continue
            Image.open(src / icon).convert("RGBA").resize((size, size), Image.LANCZOS).save(dest)
            copied += 1
    print(f"cooking: +{len(built)} recipes ({len(recipes)} in all), {len(PANTRY)} pantry goods at {stocked} vendors, "
          f"{copied} icons installed" + (f", {missing} missing" if missing else ""))


if __name__ == "__main__":
    main()
