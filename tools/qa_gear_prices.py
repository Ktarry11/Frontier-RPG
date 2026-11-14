"""
Gear is worth something, on one curve, wherever it came from.

Kyle, 10 Nov: "lvl 58 blues selling for 1 silver 2 copper?" / "1000% we need to revamp
buy/sell price of gear."

  1. the curve itself: a level 58 blue chest sells for over a gold; value rises with level
     and with rarity; a two-hander is worth more than a one-hander, a chest more than a ring
  2. every source prices by it - generated drops, boss loot, epics, quest rewards
  3. starting gear and a recruit's own kit are still worthless (no selling recruits' gear)
  4. bags and recipe scrolls keep their own hand-set prices
  5. a vendor charges four times what it pays
  6. against quest money: a green of a quest's level sells for less than that quest pays, so
     the reward money still matters, and for more than a twentieth of it, so a drop matters too
  7. an upgraded item keeps its premium through a save and load
"""
import json
import os
import random
import statistics
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)
    return ok


def main():
    from entities.pricing import gear_sell_price as price
    from entities.item import Item
    from entities.coins import coins

    # 1 ------------------------------------------------------------------------------------
    check(price(58, "rare", "chest") >= 10000,
          f"a level 58 blue chest sells for {coins(price(58, 'rare', 'chest'))} - under a gold")
    check(price(58, "rare", "ring1") >= 5000, f"a level 58 blue ring sells for {coins(price(58, 'rare', 'ring1'))}")
    for slot in ("chest", "ring1", "main_hand"):
        last = 0
        for lvl in range(1, 61):
            p = price(lvl, "uncommon", slot)
            check(p >= last, f"{slot}: level {lvl} is worth less than level {lvl - 1}")
            last = p
    order = ["poor", "common", "uncommon", "rare", "epic"]
    vals = [price(40, r, "chest") for r in order]
    check(vals == sorted(vals) and len(set(vals)) == len(vals), f"rarity does not raise the price: {dict(zip(order, vals))}")
    check(price(40, "rare", "main_hand", "sword_2h") > price(40, "rare", "main_hand", "sword_1h"),
          "a two-hander is not worth more than a one-hander")
    check(price(40, "rare", "chest") > price(40, "rare", "ring1") > 0, "a chest is not worth more than a ring")
    check(price(40, "rare", "ring1") == price(40, "rare", "ring2"), "ring1 and ring2 are priced differently")

    def on_curve(item, where):
        want = price(item.item_level, item.rarity, item.slot, item.weapon_type)
        check(item.sell_price >= want,
              f"{where}: {item.name} (lvl {item.item_level} {item.rarity} {item.slot}) sells for "
              f"{coins(item.sell_price)}, the curve says {coins(want)}")

    # 2 ------------------------------------------------------------------------------------
    from entities.loot_generator import LootGenerator
    random.seed(2)
    gen = LootGenerator()
    n = 0
    for _ in range(600):
        it = gen.generate_item_for_class(random.choice(["Warrior", "Mage", "Hunter", "Priest"]),
                                         random.randint(3, 60),
                                         rarity=random.choice(["common", "uncommon", "rare", "epic"]))
        if it is not None:
            n += 1
            on_curve(it, "generated")
    check(n > 400, f"rig: only {n} generated items")

    from entities import boss_loot
    build = next((getattr(boss_loot, f) for f in ("build_item", "_build_item", "item_from_def", "_item_from_def", "make_item")
                  if hasattr(boss_loot, f)), None)
    nb = 0
    if check(build is not None, "rig: cannot find boss_loot's item builder"):
        for f in sorted((ROOT / "data/loot").glob("*boss_loot.json")):
            for boss, defs in json.loads(f.read_text(encoding="utf-8")).items():
                for d in (defs.values() if isinstance(defs, dict) else defs):
                    if isinstance(d, dict) and d.get("item_level") and d.get("slot"):
                        try:
                            it = build(d)
                        except TypeError:
                            it = build(d, boss)
                        if it is not None:
                            nb += 1
                            on_curve(it, f.name)
        check(nb > 300, f"rig: only {nb} boss items built")

    from world.quest import build_unique_reward_set
    nq = 0
    pay_by_level = {}
    for f in sorted((ROOT / "data/quests").glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        quests = data.get("quests", data) if isinstance(data, dict) else data
        for q in (quests.values() if isinstance(quests, dict) else quests):
            if not isinstance(q, dict):
                continue
            if q.get("level_min") and q.get("reward_gold"):
                pay_by_level.setdefault(q["level_min"], []).append(q["reward_gold"])
            defs = [d for d in (q.get("rewards") or []) if isinstance(d, dict) and d.get("slot")]
            if defs:
                for r in build_unique_reward_set(defs):
                    r = getattr(r, "item", r)
                    if isinstance(r, Item) and r.slot != "recipe" and not r.bag_capacity:
                        nq += 1
                        on_curve(r, f"quest {q.get('quest_id')}")
    check(nq > 500, f"rig: only {nq} quest reward items found")

    # 3 ------------------------------------------------------------------------------------
    from entities.character import Character
    from entities.starting_gear import grant_starting_gear
    c = Character("Hero", "Warrior", 1)
    grant_starting_gear(c)
    worn = [i for i in list(c.equipment.get_all_equipped()) + list(c.inventory) if isinstance(i, Item)]
    check(worn, "rig: a new character has no gear")
    for it in worn:
        check(it.sell_price <= 1, f"starting gear {it.name} sells for {coins(it.sell_price)}")

    # 4 ------------------------------------------------------------------------------------
    bags = json.loads((ROOT / "data/items/bags.json").read_text(encoding="utf-8"))
    bag_defs = bags.get("bags", bags)
    bag_id = next(iter(bag_defs)) if isinstance(bag_defs, dict) else bag_defs[0].get("item_id")
    bag = gen.generate_bag(bag_id=bag_id)
    if check(bag is not None, f"rig: could not build bag {bag_id}"):
        raw = bag_defs[bag_id] if isinstance(bag_defs, dict) else bag_defs[0]
        check(bag.sell_price == raw["sell_price"], f"bag {bag.name}: sell price {bag.sell_price}, data says {raw['sell_price']}")

    # 5 ------------------------------------------------------------------------------------
    src = (ROOT / "ui/screens/vendor_screen.py").read_text(encoding="utf-8")
    # One function now (14 Nov 2026): the three copies disagreed about None, and a recipe scroll
    # crashed every shop that sold one. Price is 4x sell, and the list, tooltip and buy all use it.
    check("sell_price\", 0) or 0) * 4" in src and src.count("self._unit_price(item)") >= 2,
          "the vendor no longer charges 4x the sell price through one function everywhere")

    # 6 ------------------------------------------------------------------------------------
    for lvl in (10, 20, 30, 40, 50):
        pays = [g for l, gs in pay_by_level.items() if abs(l - lvl) <= 3 for g in gs]
        if not check(len(pays) >= 5, f"rig: only {len(pays)} quests near level {lvl}"):
            continue
        quest = statistics.median(pays)
        green = price(lvl, "uncommon", "chest")
        check(green < quest, f"level {lvl}: a green chest sells for {coins(green)}, more than a quest pays ({coins(int(quest))})")
        check(green > quest / 20, f"level {lvl}: a green chest sells for {coins(green)}, under 1/20 of a quest ({coins(int(quest))})")

    # 7 ------------------------------------------------------------------------------------
    it = gen.generate_item_for_class("Warrior", 40, slot="chest", rarity="rare")
    it.sell_price = int(it.sell_price * 1.2)
    back = Item.from_dict(it.to_dict())
    check(back.sell_price == it.sell_price, f"an upgraded item's price went {it.sell_price} -> {back.sell_price} on load")

    print(f"{n} generated, {nb} boss, {nq} quest-reward items priced")
    print("level 58 blue chest:", coins(price(58, "rare", "chest")), "| level 40 green chest:",
          coins(price(40, "uncommon", "chest")), "| level 10 green ring:", coins(price(10, "uncommon", "ring1")))
    if fails:
        print(f"FAIL {len(fails)}:")
        for f in fails[:30]:
            print("  ", f)
        return 1
    print("gear prices OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
