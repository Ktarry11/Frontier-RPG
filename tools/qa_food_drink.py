#!/usr/bin/env python3
"""Food and drink are worth carrying, cheap to buy, and cannot be used as a second potion.

    PYTHONPATH=. python3 tools/qa_food_drink.py

Kyle, 2026-10-28: "a proper food system that recovers health and mana... these items need to be easily
bought throughout vendors."

THE THREE WAYS A RESTING ITEM FAILS, none of which raise anything:

  * IT CANNOT BE BOUGHT. A level 3 character who cannot find bread never forms the habit, and the whole
    system is dead content with a data file behind it. So: every tier is stocked somewhere, and a
    vendor's stock matches the level of the people who shop there.
  * IT IS A BETTER POTION. If food can be eaten mid-fight it replaces potions outright and an entire
    item class dies. The interrupt rule is the design; it is asserted here, not assumed.
  * IT RESTORES THE WRONG AMOUNT. Too little and nobody sits for it; too much and the healer is
    pointless. Each tier should restore a bit more than a full bar for the level it unlocks at - which
    is a thing to MEASURE against real characters, not eyeball in a table.
"""
import copy
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from entities.character import Character  # noqa: E402
from entities.consumable_manager import get_consumable_manager  # noqa: E402


def pools(level):
    """(typical health, typical mana) at a level - measured, not assumed."""
    w = Character("w", "Warrior")
    w.level = level
    m = Character("m", "Mage")
    m.level = level
    for c in (w, m):
        c._initialize_class_stats()
        try:
            c.recalculate_stats()
        except Exception:
            pass
    return w.health, getattr(m, "mana", 0)


def main():
    cm = get_consumable_manager()
    data = json.loads((ROOT / "data/consumables/consumable_types.json").read_text())
    meals = data.get("meals", [])
    drinks = data.get("drinks", [])
    fails = []

    print(f"== {len(meals)} meals, {len(drinks)} drinks\n")
    print(f"{'item':<26}{'req':>4}{'restores':>10}{'secs':>6}{'copper':>8}   vs a full bar at that level")
    for e in meals + drinks:
        hp, mana = pools(e["required_level"])
        bar = hp if e["consumable_type"] == "meal" else mana
        ratio = e["effect_value"] / max(1, bar)
        note = f"{ratio:.0%} of {round(bar)}"
        if ratio < 0.60:
            fails.append(f"{e['consumable_id']}: restores {ratio:.0%} of a bar - not worth sitting for")
            note += "  TOO LITTLE"
        elif ratio > 2.5:
            fails.append(f"{e['consumable_id']}: restores {ratio:.0%} of a bar - trivialises healing")
            note += "  TOO MUCH"
        print(f"{e['name']:<26}{e['required_level']:>4}{e['effect_value']:>10}{e['effect_duration']:>6}"
              f"{e['vendor_price']:>8}   {note}")

    print("\n== every tier is actually on sale somewhere")
    vendors = json.loads((ROOT / "data/npcs/vendors.json").read_text())["vendors"]
    sold = {i for v in vendors for i in v.get("sells", [])}
    missing = [e["consumable_id"] for e in meals + drinks if e["consumable_id"] not in sold]
    carriers = sum(1 for v in vendors
                   if any(i.startswith(("meal_", "drink_")) for i in v.get("sells", [])))
    print(f"  {carriers} of {len(vendors)} vendors stock food or drink")
    print(f"  tiers never sold anywhere: {missing or 'none'}")
    for m in missing:
        fails.append(f"{m} is not sold by any vendor - unbuyable content")

    print("\n== a vendor's stock suits the people who shop there")
    bad = []
    for v in vendors:
        tier = v.get("gear_level") or 10
        for i in v.get("sells", []):
            e = next((x for x in meals + drinks if x["consumable_id"] == i), None)
            if e and e["required_level"] > tier + 4:
                bad.append((v["vendor_id"], i, tier, e["required_level"]))
    print(f"  {len(bad)} vendors selling food above their own tier")
    for vid, i, t, r in bad[:5]:
        fails.append(f"{vid} (tier {t}) sells {i} (needs {r})")

    print("\n== eating and drinking at once, and a fight stopping both")
    c = Character("QA", "Mage")
    c.level = 5
    try:
        c.recalculate_stats()
    except Exception:
        pass
    c.current_health, c.current_mana = 10, 10
    for cid in ("meal_tough_jerky", "drink_waterskin"):
        copy.deepcopy(cm.get_consumable(cid)).use(c, [])
    both = len(c.consumable_regen_active())
    print(f"  active at once: {both}")
    if both != 2:
        fails.append(f"only {both} resting effect(s) active - food and drink must run together")
    c.tick_consumable_regen(5.0)
    gained = c.current_health > 10 and c.current_mana > 10
    print(f"  both bars moved after 5s: {gained}")
    if not gained:
        fails.append("ticking did not move both bars")
    c.break_consumable_regen()
    hp_before = c.current_health
    c.tick_consumable_regen(5.0)
    print(f"  stopped by combat: {not c.consumable_regen_active()} "
          f"(hp unchanged: {c.current_health == hp_before})")
    if c.consumable_regen_active() or c.current_health != hp_before:
        fails.append("combat did not stop resting - food would replace potions outright")

    print("\n== it does not burn the potion cooldown")
    c2 = Character("QA2", "Mage")
    c2.level = 5
    copy.deepcopy(cm.get_consumable("meal_tough_jerky")).use(c2, [])
    print(f"  consumable_cooldown after eating: {c2.consumable_cooldown}")
    if c2.consumable_cooldown:
        fails.append("eating set the shared potion cooldown - you could not then drink, or pot")

    print()
    if fails:
        print(f"FAIL ({len(fails)})")
        for f in fails:
            print("  -", f)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
