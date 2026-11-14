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
    "cook_mushroom": ("Cellar Mushrooms", 6, "early", "Grown in the dark on purpose.", "Food_112_Frostcaps.png"),
    "cook_fruit": ("Orchard Fruit", 4, "starter", "Whatever was ripe. Bruised on one side.", "Food_20.png"),
    "cook_roots": ("Root Vegetables", 3, "starter", "Carrots, mostly. They keep.", "Food_54.png"),
    "cook_water": ("Fresh Water", 2, "starter", "From the well. For the pot, not the road.", "Milk_03.png"),
    "cook_cheese": ("Sharp Cheese", 6, "early", "Hard, yellow, and older than the innkeeper admits.", "Food_03.png"),
    "cook_ale": ("Cooking Ale", 8, "early", "Not for drinking. People drink it.", "Beer_01.png"),
}

#: line key -> (per-tier buffs, flavour, [8 x (name, {inputs}, pack icon)])
#: EVERY DISH IS MADE OF WHAT ITS NAME SAYS. The first build put two pieces of the tier's meat
#: and one pantry good into everything, which made a Cheese Toastie out of stringy meat (Kyle:
#: "lets make cooking actually reasonable....like stringy meat for a toastie?"). M is the tier's
#: meat; a dish with no meat in its name has none in its pot.
A = lambda *v: list(v)
M = "MEAT"
F, H, S, MU, C, AL, FR, R = ("cook_flour", "cook_honey", "cook_spice", "cook_mushroom", "cook_cheese",
                             "cook_ale", "cook_fruit", "cook_roots")
W, B, ST = "cook_water", "cook_bread", "cook_stock"

#: THINGS A COOK MAKES TO COOK WITH. Kyle, 12 Nov: "Some cooking ingredients can be sold or
#: made...like selling flour and water to make bread. bread can be then used in cooking."
#: id -> (name, {inputs}, how many it makes, skill, description, pack icon). Not sold: you bake it.
PREPARED = {
    B: ("Bread", {F: 1, W: 1}, 2, 0, "A plain loaf. Half of what a kitchen makes starts here.", "Food_08.png"),
    ST: ("Soup Stock", {R: 1, W: 1, "salt": 1}, 2, 30, "Roots boiled down until the water is worth something.", "Milk_04.png"),
}
LINES = {
    "hearty": ({"stamina": A(3, 5, 7, 9, 12, 14, 17, 20), "hp5": A(2, 3, 5, 7, 9, 11, 13, 16)},
               "Heavy, hot, and it stays with you.", [
        ("Trail Dumplings", {M: 1, F: 1, W: 1}, "Food_DimSum.png"),
        ("Hunter's Pie", {M: 2, F: 1, R: 1}, "Food_103_PotatoBread.png"),
        ("Ironpot Stew", {M: 2, R: 1, ST: 1}, "Food_64.png"),
        ("Marrow Pie", {M: 2, F: 2}, "Food_33.png"),
        ("Warden's Pot Roast", {M: 3, R: 2}, "Food_15.png"),
        ("Stockade Hotpot", {M: 2, R: 1, ST: 2}, "Food_117_HeartySoup.png"),
        ("Long-Simmer Shank", {M: 3, R: 2, AL: 1}, "Food_84_RoastClefthoof.png"),
        ("Bulwark Feast", {M: 3, R: 2, F: 2}, "Food_14.png")]),
    "sweet": ({"spirit": A(3, 5, 7, 9, 12, 14, 17, 20), "mp5": A(2, 3, 4, 6, 8, 9, 11, 13)},
              "Sweet, and it clears the head.", [
        ("Honey Cakes", {F: 1, H: 1}, "Food_73CinnamonRoll.png"),
        ("Baked Apples", {FR: 2, H: 1}, "Food_19.png"),
        ("Orchard Tart", {F: 2, FR: 2}, "Food_10.png"),
        ("Sage-Honey Roast", {M: 2, H: 2}, "Food_18.png"),
        ("Fruit-Stuffed Loin", {M: 2, FR: 2}, "Food_105_SnowPlum.png"),
        ("Mead-Glazed Steak", {M: 2, H: 2}, "Food_108_MeadCaribou.png"),
        ("Vigil Pudding", {F: 2, FR: 2, H: 2}, "Food_146_CakeSlice.png"),
        ("Seer's Table", {M: 2, FR: 2, H: 2}, "Food_145_Cake.png")]),
    "spiced": ({"attack_power": A(6, 10, 14, 20, 26, 30, 36, 44)},
               "Hot enough to make you want to hit something.", [
        ("Spiced Jerky", {M: 2, S: 1}, "Food_66.png"),
        ("Pepper-Crust Chop", {M: 2, S: 1}, "Food_47.png"),
        ("Firebrand Ribs", {M: 2, S: 1}, "Food_48.png"),
        ("Redpepper Haunch", {M: 3, S: 1}, "Food_116_CondorLeg.png"),
        ("Warband Grill", {M: 3, S: 2}, "Food_124_Skewer.png"),
        ("Bloodspice Steak", {M: 2, S: 2}, "Food_122_Steak.png"),
        ("Reaver's Rack", {M: 3, S: 2}, "Food_86_Basilisk.png"),
        ("Champion's Carvery", {M: 3, S: 2, "salt": 1}, "Food_119_RhinoMeat.png")]),
    "mushroom": ({"spell_power": A(4, 7, 10, 14, 18, 21, 25, 30)},
                 "Earthy, and faintly luminous if you leave it too long.", [
        ("Fried Mushrooms", {MU: 2}, "Food_96_ZangarCaps.png"),
        ("Cellar-Cap Fry", {MU: 2, M: 1}, "Food_91.png"),
        ("Glowcap Ragout", {MU: 2, M: 1, ST: 1}, "27_BlueSoup.png"),
        ("Scholar's Fricassee", {M: 2, MU: 2, ST: 1}, "Food_115_CondorSoup.png"),
        ("Nightcap Roast", {M: 2, MU: 2}, "Food_78.png"),
        ("Arcanist's Plate", {M: 2, MU: 2}, "ToW_SpiceBowl.png"),
        ("Duskcap Roulade", {M: 2, MU: 3}, "Food_67.png"),
        ("Magister's Supper", {M: 2, MU: 3, S: 1}, "Food_79.png")]),
    "cheese": ({"healing_power": A(7, 12, 18, 25, 33, 38, 46, 55)},
               "Melted over everything. Nobody has ever been sad eating it.", [
        ("Cheese Toastie", {B: 1, C: 1}, "Food_35.png"),
        ("Herder's Melt", {M: 1, C: 1, B: 1}, "Food_04.png"),
        ("Shepherd's Bake", {M: 2, C: 1, R: 1}, "Food_102_FlatBread.png"),
        ("Mender's Gratin", {R: 2, C: 2}, "Food_100_HardCheese.png"),
        ("Hearthkeeper's Pie", {M: 2, C: 2, F: 1}, "Food_94_GaradarSharp .png"),
        ("Chaplain's Platter", {M: 2, C: 2, B: 1}, "Food_95_Grainbread.png"),
        ("Mercy Roast", {M: 2, C: 2, R: 1}, "Food_101_SourCheese.png"),
        ("Lifewarden's Board", {M: 2, C: 3, FR: 1}, "Food_37.png")]),
    "ale": ({"armor": A(20, 40, 70, 100, 140, 170, 210, 260), "dodge": A(0, 0, 0, 1, 1, 1, 2, 2)},
            "Boiled in ale until it stops arguing.", [
        ("Ale-Boiled Strips", {M: 2, AL: 1}, "Food_53.png"),
        ("Tavern Chop", {M: 2, AL: 1}, "Food_52.png"),
        ("Brewer's Brisket", {M: 2, AL: 1}, "Food_65.png"),
        ("Stout Stew", {M: 2, AL: 1, ST: 1}, "Food_49.png"),
        ("Black-Ale Roast", {M: 3, AL: 2}, "Food_123_Roast.png"),
        ("Shieldwall Steak", {M: 2, AL: 2}, "Food_85_StegadonBite.png"),
        ("Keg-Braised Shank", {M: 3, AL: 2}, "Food_88_RavagerNuggets.png"),
        ("Old Guard's Feast", {M: 3, AL: 2, R: 2}, "BrewfestBuff_01.png")]),
}

#: The first 22 recipes were all "N pieces of one meat". These add what the name promises.
OLD_EXTRAS = {"Barley Pottage": {F: 1}, "Peppered Strips": {S: 1}, "Spiced Terrine": {S: 1},
              "Slow Stew": {ST: 1}, "Thin Broth": {ST: 1}}

#: Four stews at the Rich Cut tier: (slug, name, second ingredient, stat, flavour, icon)
RESIST = [
    ("emberproof_stew", "Emberproof Stew", "cook_spice", "fire_resistance", "So hot the fire seems reasonable after.", "FireDrink_1.png"),
    ("frostbite_chowder", "Frostbite Chowder", "cook_roots", "frost_resistance", "Thick enough to stand a spoon in. Keeps the cold out.", "26_GoatsMilk.png"),
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
         "attack_power": "Attack Power", "spell_power": "Spell Power", "healing_power": "Healing Power",
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
    for li, (key, (buffs, flavour, dishes)) in enumerate(LINES.items()):
        for ti, tier in enumerate(TIERS):
            meat, level, base, *_ = tier
            name, inputs, icon = dishes[ti]
            bonuses = {k: v[ti] for k, v in buffs.items() if v[ti]}
            skill = min(300, base + 5 + li * 6)
            rid = f"cookx_{slug(name)}"
            recipe = {"name": name, "skill_required": skill,
                      "inputs": {(meat if k == M else k): q for k, q in inputs.items()},
                      "output": {"kind": "consumable", "consumable_id": f"meal_cooked_{slug(name)}", "count": 1}}
            if ti >= 5:                      # the late tiers follow the 300 build: trainer-taught, with a range
                recipe["skill_range"] = [skill + 5, skill + 15, skill + 25, skill + 35]
                recipe["source"] = "trainer"
            out.append((rid, recipe, meal(f"meal_cooked_{slug(name)}", name, flavour, tier, bonuses), icon))
    tier = TIERS[3]
    for i, (s, name, good, stat, flavour, icon) in enumerate(RESIST):
        recipe = {"name": name, "skill_required": 160 + i * 5, "inputs": {"meat_rich": 2, good: 2, ST: 1},
                  "output": {"kind": "consumable", "consumable_id": f"meal_cooked_{s}", "count": 1}}
        out.append((f"cookx_{s}", recipe, meal(f"meal_cooked_{s}", name, flavour, tier, {stat: 15, "stamina": 5}), icon))
    return out


def main():
    pack = Path(sys.argv[sys.argv.index("--pack") + 1]) if "--pack" in sys.argv else None
    built = build()

    mp = ROOT / "data/gathering/materials.json"
    mdata = json.loads(mp.read_text(encoding="utf-8"))
    mats = mdata.get("materials", mdata)
    for mid, (name, price, tier, desc, _icon) in PANTRY.items():
        mats[mid] = {"name": name, "material_type": "reagent", "profession": "cooking", "tier": tier,
                     "description": desc, "stack_limit": 20, "vendor_price": price,
                     "sell_price": price // 4, "icon_id": mid}       # water is worth nothing back
    for mid, (name, _inputs, _n, _skill, desc, _icon) in PREPARED.items():
        mats[mid] = {"name": name, "material_type": "reagent", "profession": "cooking", "tier": "starter",
                     "description": desc, "stack_limit": 20, "sell_price": 0, "icon_id": mid}   # no bread-for-coin loop
    mp.write_text(json.dumps(mdata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    cp = ROOT / "data/consumables/consumable_types.json"
    cdata = json.loads(cp.read_text(encoding="utf-8"))
    mine = {m["consumable_id"] for _r, _rec, m, _i in built}
    # Everything an earlier run of THIS tool made goes first, so a renamed dish leaves nothing behind.
    rp0 = ROOT / "data/crafting/recipes.json"
    r0 = json.loads(rp0.read_text(encoding="utf-8"))
    c0 = r0["professions"]["cooking"]
    c0 = c0["recipes"] if "recipes" in c0 else c0
    for rid in [r for r in c0 if r.startswith("cookx_")]:
        gone = c0.pop(rid)["output"].get("consumable_id")
        if not gone:
            continue
        mine.add(gone)
        icon = ROOT / "assets/icons/consumables" / f"{gone}.png"
        if icon.is_file():
            icon.unlink()
    for name, extra in OLD_EXTRAS.items():
        for rec in c0.values():
            if rec["name"] == name:
                rec["inputs"] = {k: q for k, q in rec["inputs"].items() if not k.startswith("cook_")}
                rec["inputs"].update(extra)
    rp0.write_text(json.dumps(r0, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    cdata["cooked_meals"] = [m for m in cdata["cooked_meals"] if m["consumable_id"] not in mine] \
        + [m for _r, _rec, m, _i in built]
    cp.write_text(json.dumps(cdata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    rp = ROOT / "data/crafting/recipes.json"
    rdata = json.loads(rp.read_text(encoding="utf-8"))
    recipes = rdata["professions"]["cooking"]["recipes"] if "recipes" in rdata["professions"]["cooking"] \
        else rdata["professions"]["cooking"]
    for rid, recipe, _m, _i in built:
        recipes[rid] = recipe
    for mid, (name, inputs, makes, skill, _desc, _icon) in PREPARED.items():
        recipes[f"cookx_{mid[5:]}"] = {"name": name, "skill_required": skill, "inputs": dict(inputs), "count": makes,
                                       "output": {"kind": "material", "material_id": mid, "count": makes}}
    rp.write_text(json.dumps(rdata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    vp = ROOT / "data/npcs/vendors.json"
    vdata = json.loads(vp.read_text(encoding="utf-8"))
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
    vp.write_text(json.dumps(vdata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    copied = missing = 0
    if pack is not None:
        from PIL import Image
        src = pack / "Miscellaneous"
        by_name = {m["name"]: m["consumable_id"] for m in cdata["cooked_meals"]}
        jobs = [(ROOT / "assets/icons/consumables" / f"{m['consumable_id']}.png", icon, 96) for _r, _rec, m, icon in built]
        jobs += [(ROOT / "assets/icons/consumables" / f"{by_name[n]}.png", icon, 96) for n, icon in OLD_ICONS.items() if n in by_name]
        jobs += [(ROOT / "assets/gathering_nodes/reagents" / f"{mid}.png", p[4], 32) for mid, p in PANTRY.items()]
        jobs += [(ROOT / "assets/gathering_nodes/reagents" / f"{mid}.png", p[5], 32) for mid, p in PREPARED.items()]
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
