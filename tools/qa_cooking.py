"""Cooking is a real profession: a meal for every role at every tier, and Well Fed that lasts.

Kyle, 12 Nov: "food should give buffs! And we can expand out a lot more cooking." Two things
were wrong before the expansion: every meal's buff lasted the ~20 seconds it took to eat it
(not the 30 minutes its text promised), and there were three stat sticks per tier.
"""
import json
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

ROLES = ("stamina", "hp5", "mp5", "attack_power", "spell_power", "healing_power", "armor")
MEATS = ("meat_stringy", "meat_lean", "meat_thick", "meat_rich", "meat_prime", "meat_marbled", "meat_aged", "meat_select")


def main():
    bad = []
    recipes = json.load(open("data/crafting/recipes.json", encoding="utf-8"))["professions"]["cooking"]
    recipes = recipes.get("recipes", recipes)
    meals = {m["consumable_id"]: m for m in json.load(open("data/consumables/consumable_types.json", encoding="utf-8"))["cooked_meals"]}
    mats = json.load(open("data/gathering/materials.json", encoding="utf-8"))
    mats = mats.get("materials", mats)
    vendors = json.load(open("data/npcs/vendors.json", encoding="utf-8"))
    vendors = vendors.get("vendors", vendors)
    vendors = vendors if isinstance(vendors, list) else list(vendors.values())
    sold = {i for v in vendors for i in (v.get("sells") or [])}

    caught = {f for p in json.load(open("data/gathering/node_pools.json", encoding="utf-8"))["zones"].values()
              for f in (p.get("fishing") or {}).get("table", {})}
    LEVELS = (1, 8, 16, 24, 32, 38, 46, 54)
    by_tier = {lv: set() for lv in LEVELS}
    made = {r["output"]["material_id"] for r in recipes.values() if r["output"].get("kind") == "material"}
    meatless = 0
    for rid, r in recipes.items():
        for mid in r["inputs"]:
            if mid not in mats:
                bad.append(f"{r['name']}: needs {mid}, which does not exist")
            elif mid in caught:
                continue                     # fish: caught at a fishing spot (tools/qa_fishing.py)
            elif not mid.startswith("meat_") and mid not in sold and mid not in made:
                bad.append(f"{r['name']}: needs {mid}, which nobody sells and no recipe makes")
            elif not mid.startswith("meat_") and not os.path.isfile(f"assets/gathering_nodes/reagents/{mats[mid]['icon_id']}.png"):
                bad.append(f"{mid}: no icon")
        if r["output"].get("kind") == "material":
            continue                                   # bread, stock: made to cook with
        cid = r["output"].get("consumable_id")
        meal = meals.get(cid)
        if meal is None:
            bad.append(f"{r['name']}: makes {cid}, which is not a meal")
            continue
        if not os.path.isfile(f"assets/icons/consumables/{cid}.png"):
            bad.append(f"{r['name']}: no icon")
        if not meal.get("stat_bonuses"):
            bad.append(f"{r['name']}: leaves you with no Well Fed buff")
        if "hp5" in meal["stat_bonuses"] and "Health per turn" not in meal["description"]:
            bad.append(f"{r['name']}: gives hp5 and its text does not say so")
        if "healing_power" in meal["stat_bonuses"] and "Healing Power" not in meal["description"]:
            bad.append(f"{r['name']}: its text does not call Healing Power by its name")
        if not any(m.startswith("meat_") for m in r["inputs"]):
            meatless += 1
        if meal["required_level"] in by_tier:
            by_tier[meal["required_level"]].update(meal["stat_bonuses"])
    for lv, stats in by_tier.items():
        missing = [r for r in ROLES if r not in stats]
        if missing:
            bad.append(f"level {lv} tier has no meal for: {', '.join(missing)}")
    # A dish is made of what its name says.
    by_name = {r["name"]: r["inputs"] for r in recipes.values()}
    if any(m.startswith("meat_") for m in by_name.get("Cheese Toastie", {"meat_x": 1})):
        bad.append("a Cheese Toastie has meat in it")
    if "cook_bread" not in by_name.get("Cheese Toastie", {}):
        bad.append("a Cheese Toastie is not made of bread")
    if by_name.get("Bread") != {"cook_flour": 1, "cook_water": 1}:
        bad.append("Bread is not flour and water")
    if meatless < 5:
        bad.append("almost every dish is still meat-and-one-thing")
    if len(recipes) < 70:
        bad.append(f"only {len(recipes)} cooking recipes")

    # Well Fed, in the game: eaten once, it is still there twenty minutes later and gone after thirty.
    from entities.character import Character
    from entities.consumable_manager import get_consumable_manager
    hero = Character("Hero", "Warrior", 20)
    base_hp5 = hero.hp5_total()
    dumplings = get_consumable_manager().get_consumable("meal_cooked_trail_dumplings")
    if dumplings is None:
        bad.append("Trail Dumplings cannot be created")
    else:
        hero.current_health = 1
        dumplings.use(hero)
        hero._recalculate_derived_stats()
        if hero.food_buff is None:
            bad.append("eating a cooked meal leaves no buff")
        else:
            if hero.hp5_total() - base_hp5 != dumplings.stat_bonuses["hp5"]:
                bad.append(f"Trail Dumplings: hp5 went {base_hp5} -> {hero.hp5_total()}, expected +{dumplings.stat_bonuses['hp5']}")
            hero.update_buff_timers(20 * 60)
            if hero.food_buff is None:
                bad.append("Well Fed is gone after twenty minutes - it should last thirty")
            hero.update_buff_timers(11 * 60)
            if hero.food_buff is not None:
                bad.append("Well Fed never runs out")

    print(f"{len(recipes)} cooking recipes, {len(meals)} cooked meals, "
          f"{len([m for m in mats if m.startswith('cook_')])} pantry goods")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad[:25]:
            print("  -", b)
        return 1
    print("\ncooking OK - a meal for every role at every tier, every one with art, and Well Fed lasts half an hour.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
