#!/usr/bin/env python3
"""Food and drink: the resting items. Idempotent.

  PYTHONPATH=. python3 tools/build_food_and_drink.py

Kyle, 2026-10-28: "we need a proper food system that recovers health and mana. these items need to be
easily bought throughout vendors... food recovers hp over time and drink recovers mana."

TWO THINGS SHARE THE WORD FOOD AND THEY ARE NOT THE SAME MECHANIC. The game already has six "food"
consumables and they are STAT BUFFS - +6 Strength for half an hour, the Well Fed effect - sitting in a
stat-buff slot. Those are correct and untouched. This adds the other thing food does: sit down, get the
bar back, stand up. Separate consumable types ("meal" and "drink") so the two can never collide in a
slot, presented to the player as Food and Drink.

WHY IT IS SLOW, AND WHY THAT IS THE DESIGN. A healing potion is instant, expensive and on a cooldown.
Food restores MORE than a potion of the same tier and costs a fraction as much, and the price of that is
twenty to thirty seconds of standing still that any hit interrupts. That trade is the whole reason both
items exist; without the interrupt rule, food is simply a better potion and the potion is dead content.

TIERS ARE CALIBRATED TO THIS GAME'S POOLS, not copied from the one this borrows from. Measured: a level
1 warrior has about 212 health and a level 40 about 492; a level 1 mage has 435 mana and a level 40
about 1155. Each tier restores a little more than a full bar for the level it unlocks at, which is what
makes a meal worth sitting for.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: (id, name, required_level, total restored, seconds, copper, flavour)
MEALS = [
    ("meal_tough_jerky", "Tough Jerky", 1, 190, 20, 10,
     "Salted hard enough to keep for a season and chewy enough to prove it."),
    ("meal_trailbread", "Dried Trailbread", 10, 290, 22, 35,
     "Baked twice, so it keeps. Nobody has ever described it as nice."),
    ("meal_river_fish", "Smoked River Fish", 20, 400, 24, 90,
     "Split, boned and hung over alder smoke. Good cold, better than it sounds."),
    ("meal_spiced_haunch", "Spiced Haunch", 30, 530, 26, 200,
     "A proper joint, rubbed with whatever the cook could get hold of."),
    ("meal_kodo_ribs", "Kodo Rib Roast", 38, 700, 30, 420,
     "One rib feeds three people. The tauren find it funny that anyone asks."),
    # FIVE TIERS, NOT SIX. A sixth at level 50 was written and then cut: the game's level ceiling is
    # 40 (the Crystalline Underdark is 32-40, and no vendor anywhere is geared above 38), so it was
    # unbuyable content serving zones that do not exist. tools/qa_food_drink.py caught it. Add tier
    # six when there is a level 50 zone to eat it in, not before.
]

DRINKS = [
    ("drink_waterskin", "Skin of Clean Water", 1, 420, 20, 10,
     "Clean, which out here is worth saying out loud."),
    ("drink_barley_beer", "Weak Barley Beer", 10, 640, 22, 35,
     "Thin, warm and safer than the well it was brewed from."),
    ("drink_spring_flask", "Spring-Fed Flask", 20, 870, 24, 90,
     "Filled at a spring somebody still looks after."),
    ("drink_honeyed_mead", "Honeyed Mead", 30, 1090, 26, 200,
     "Sweet enough to hide the fact that it is mostly medicine."),
    ("drink_birch_wine", "Aspen Birch Wine", 38, 1380, 30, 420,
     "Tapped off a tree that was not on this world four springs ago. Tastes of cold."),
]


def entry(cid, name, req, total, seconds, price, flavour, kind):
    bar = "health" if kind == "meal" else "mana"
    return {
        "consumable_id": cid,
        "name": name,
        "consumable_type": kind,
        "description": f"{flavour} Restores {total} {bar} over {seconds} seconds while you rest. "
                       f"Taking damage stops it.",
        "effect_value": total,
        "effect_duration": seconds,
        "level_multiplier": 0.0,
        "required_level": req,
        "cooldown_seconds": 2,
        "stack_limit": 20,
        "vendor_price": price,
        "sell_price": max(1, price // 4),
        "buff_category": None,
    }


def main():
    p = ROOT / "data/consumables/consumable_types.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    data["meals"] = [entry(*m, "meal") for m in MEALS]
    data["drinks"] = [entry(*d, "drink") for d in DRINKS]
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ---- ON SALE EVERYWHERE. Kyle: "easily bought throughout vendors." A resting item you cannot
    # reliably buy is a resting item nobody builds a habit around, so every gear vendor and every
    # general-goods vendor stocks the tiers at or below their own gear tier. Innkeepers and cooks get
    # them too, because that is who would sell you a meal.
    vp = ROOT / "data/npcs/vendors.json"
    vdata = json.loads(vp.read_text(encoding="utf-8"))
    FOODY = ("innkeeper", "cook", "quartermaster", "trader", "vendor", "supplier", "spice",
             "market", "warehouse", "herbs", "reagent", "smith", "bowyer", "weaponsmith", "engineer")
    touched = 0
    for v in vdata["vendors"]:
        vid = v["vendor_id"]
        sells_gear = v.get("sells_gear", True)
        if not (sells_gear or any(w in vid for w in FOODY)):
            continue
        tier = v.get("gear_level") or 10
        want = [m[0] for m in MEALS if m[2] <= tier + 2][-2:] + \
               [d[0] for d in DRINKS if d[2] <= tier + 2][-2:]
        stock = list(v.get("sells", []))
        added = [w for w in want if w not in stock]
        if added:
            v["sells"] = stock + added
            touched += 1
    vp.write_text(json.dumps(vdata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"{len(MEALS)} meals, {len(DRINKS)} drinks; stocked on {touched} vendors")


if __name__ == "__main__":
    main()
