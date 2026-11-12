"""
Every stat on every item is a whole number, and bonus armour is part of the armour.

Kyle, 10 Nov, asking a second time: "i asked you to remove these partial values from
gear....still havent." and "when an item gets +armor - it should not appear as a bonus stat
but it should just go into the armor."

  1. stored items (boss loot, epics, quest rewards, vendors, crafted): nothing fractional,
     no "armor" in a stat list                       (tools/whole_number_gear.py --check)
  2. 4,000 generated items across every class, level 5-60 and rarity: the same
  3. the generator does not throw away what rounding removes - a generated item's stats are
     worth at least as much budget, on average, as the unrounded roll
  4. an item built with fractions comes out whole; one built with +armor has it in its
     armour value; and a character wearing it has exactly the armour they had before
  5. an item loaded from an old save with fractional stats comes out whole
"""
import os
import random
import subprocess
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


def bad_stats(item):
    out = []
    for group in (item.primary_stats, item.secondary_stats):
        for stat, value in group.items():
            if stat == "armor":
                out.append(f"armor listed as a stat (+{value})")
            elif isinstance(value, float) or not isinstance(value, int):
                out.append(f"{stat} = {value!r}")
            elif value == 0:
                out.append(f"{stat} is 0 and still listed")
    if not isinstance(item.armor_value, int):
        out.append(f"armor_value = {item.armor_value!r}")
    return out


def main():
    # 1 ------------------------------------------------------------------------------------
    r = subprocess.run([sys.executable, "tools/whole_number_gear.py", "--check"],
                       capture_output=True, text=True)
    check(r.returncode == 0, "stored items still hold fractions or armour-as-a-stat:\n      "
          + "\n      ".join(r.stdout.strip().splitlines()[-8:]))

    # 2 + 3 --------------------------------------------------------------------------------
    from entities.loot_generator import LootGenerator
    from entities.item import Item, whole_stats
    random.seed(11)
    gen = LootGenerator()
    classes = ["Warrior", "Paladin", "Hunter", "Rogue", "Priest", "Shaman", "Mage", "Warlock", "Druid"]
    made, empty_suffixed, with_secondary = 0, 0, 0
    for i in range(4000):
        lvl = random.randint(5, 60)
        rarity = random.choice(["uncommon", "uncommon", "rare", "epic"])
        try:
            item = gen.generate_item_for_class(random.choice(classes), lvl, rarity=rarity)
        except Exception as exc:
            check(False, f"rig: generate_item_for_class failed ({type(exc).__name__}: {exc})")
            break
        if item is None:
            continue
        made += 1
        problems = bad_stats(item)
        check(not problems, f"generated {item.name} (lvl {lvl} {rarity}): " + "; ".join(problems))
        if item.secondary_stats:
            with_secondary += 1
        if not item.primary_stats and not item.secondary_stats and " of " in item.name:
            empty_suffixed += 1
    check(made > 3000, f"rig: only {made} items generated")
    check(empty_suffixed <= made * 0.01,
          f"{empty_suffixed} of {made} generated items are named for a suffix and have no stats at all")
    check(with_secondary >= made * 0.25,
          f"only {with_secondary} of {made} generated items kept any secondary stat - rounding is wiping them")

    # the rounding hand-back, measured on the roll itself
    lost = kept = 0.0
    random.seed(5)
    for _ in range(1500):
        budget = random.uniform(4, 60)
        p, s, _name = gen._roll_stats(random.choice(["str_physical", "agi_physical", "int_caster", "spi_healer"]),
                                      budget, 0, rarity="uncommon", item_level=random.randint(20, 60)) \
            if hasattr(gen, "_roll_stats") else ({}, {}, None)
        spent = sum(v * gen.stat_budget_costs.get(k, 1.0) for k, v in {**p, **s}.items())
        kept += spent
        lost += budget
    if lost:
        check(kept >= lost * 0.90,
              f"generated stats are worth {kept / lost:.0%} of their budget - rounding is costing items value")

    # 4 ------------------------------------------------------------------------------------
    p, s, a = whole_stats({"strength": 4.5}, {"crit_chance_physical": 0.3, "hit_rating": 0.5,
                                              "attack_power": 7.65, "armor": 14.09}, 100)
    check(p == {"strength": 5}, f"4.5 strength should round up to 5, got {p}")
    check(s == {"hit_rating": 1, "attack_power": 8}, f"secondary should be whole with 0.3 dropped, got {s}")
    check(a == 114, f"100 armour + 14.09 bonus armour should be 114, got {a}")

    from entities.character import Character

    def armour_wearing(item):
        c = Character("Hero", "Warrior", 40)
        base = c.armor
        c.inventory.append(item) if hasattr(c, "inventory") and isinstance(c.inventory, list) else None
        ok = c.equip_item(item)
        return c.armor - base, ok

    def chest(sec, armor):
        return Item("t_chest", "Test Chest", "chest", 40, "rare", armor_type="plate",
                    secondary_stats=sec, armor_value=armor, required_level=1)

    folded, ok1 = armour_wearing(chest({"armor": 20}, 200))
    plain, ok2 = armour_wearing(chest({}, 220))
    if check(ok1 is not False and ok2 is not False and plain > 0,
             f"rig: could not equip the test chest (armour gained {plain})"):
        check(folded == plain, f"+20 armour as a stat gives {folded} armour; 220 armour gives {plain}")
    it = chest({"armor": 20}, 200)
    check(it.armor_value == 220 and "armor" not in it.secondary_stats,
          f"an item with +20 armour should read 220 Armor; it reads {it.armor_value} with {it.secondary_stats}")

    # 5 ------------------------------------------------------------------------------------
    old = chest({}, 200).to_dict()
    old["secondary_stats"] = {"dodge_rating": 0.6, "haste": 0.2, "armor": 9.4}
    old["primary_stats"] = {"stamina": 7}
    loaded = Item.from_dict(old)
    check(not bad_stats(loaded) and loaded.secondary_stats == {"dodge_rating": 1} and loaded.armor_value == 209,
          f"an old save's item loads as {loaded.primary_stats} {loaded.secondary_stats} armour {loaded.armor_value}")

    print(f"{made} generated items checked ({with_secondary} with a secondary stat); "
          f"rolled stats worth {kept / lost:.0%} of budget")
    if fails:
        print(f"FAIL {len(fails)}:")
        for f in fails[:30]:
            print("  ", f)
        return 1
    print("whole-number gear OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
