#!/usr/bin/env python3
"""Carry the last two professions - Cooking and Engineering - to skill 300.

    PYTHONPATH=. python3 tools/build_cooking_engineering_300.py [--apply]

Idempotent. Prints the plan by default; --apply writes it.

=============================================================================
WHY THESE TWO ARE LAST, AND DIFFERENT
=============================================================================

Kyle: "Go to skill 300" for all crafting. Six professions got there by
climbing a gathered ladder that now runs 1-300 with ~22 materials. These two
do not have one:

    COOKING stopped at 225 with FIFTEEN recipes and FIVE meats. Meat is not
    gathered off a node, it drops from beasts (entities/meat_drops.py), so
    the ladder is bounded by creature level - and the highest creature in the
    game is 53, which is skill ~265. Three more cuts fit under that; nothing
    does above it.

    ENGINEERING stopped at 180 on bronze, iron and steel. Those were the top
    bars when it was written. They are not any more: the mining re-anchor put
    Mithril at 175, Thorium at 245 and Elementium at 290, and engineering
    never climbed onto them.

=============================================================================
A RECIPE'S SKILL IS NOT ITS INGREDIENT'S SKILL
=============================================================================

Worth stating because it is what makes Cooking reachable at all. The skill to
GATHER a material and the skill to USE it are different professions' numbers.
Meat tops out around 265 because creatures do, but a Cooking recipe at 300 may
still take that meat - it just asks more of the cook. Same reason a
blacksmithing recipe at 275 can use Elementium Bar, whose gate is mining 300.

So Cooking climbs the last stretch on combinations and reagents rather than on
a cut of meat that no animal in the world is big enough to carry.
"""
import argparse
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MATS = ROOT / "data" / "gathering" / "materials.json"
RECIPES = ROOT / "data" / "crafting" / "recipes.json"
CONSUM = ROOT / "data" / "consumables" / "consumable_types.json"
MEAT_DROPS = ROOT / "entities" / "meat_drops.py"

CEILING = 300
#: Highest level any creature reaches, so the highest meat that can ever drop.
TOP_CREATURE = 53


def spread(lo):
    """Recipe skill_range - the recipe is learnable at `lo`, so the colours
    start just above it."""
    return [lo + 5, lo + 15, lo + 25, lo + 35]


def mat_spread(lo):
    """MATERIAL skill_range, which must START at lo.

    Not the same function as spread(). A material's skill_range[0] IS its gate,
    so adding the recipe offset silently pushed Select Cut from 265 to 270 -
    and 270/5 is a level 54 beast in a game whose highest creature is 53. The
    guard below checked the intended number while the data carried the shifted
    one, so it passed and the cut would have been unobtainable.
    """
    return [lo, lo + 10, lo + 20, lo + 30]


# ---------------------------------------------------------------- cooking
NEW_MEAT = {
    "meat_marbled": dict(name="Marbled Cut", skill=195, tier="late",
                         description="Fat laced right through it. It bastes itself."),
    "meat_aged":    dict(name="Aged Cut", skill=235, tier="endgame",
                         description="Hung in the cold until it turned dark and sweet."),
    # 255, not 265: a level-51 beast. Pinning it to the single highest
    # creature in the game would make the cut a lottery rather than a tier.
    "meat_select":  dict(name="Select Cut", skill=255, tier="endgame",
                         description="The one piece a butcher keeps back and does not put on the board."),
}

#: Appended to entities/meat_drops.py BANDS. Bounded by TOP_CREATURE.
NEW_BANDS = """    (38, 48, {"meat_prime": 3, "meat_marbled": 2}),
    (44, 52, {"meat_prime": 1, "meat_marbled": 3, "meat_aged": 2}),
    (48, 99, {"meat_marbled": 1, "meat_aged": 3, "meat_select": 2}),"""

#: (recipe skill, meal name, inputs, health, buff). The last few climb on
#: combinations and reagents, not on a bigger animal - see docstring.
COOK = [
    (185, "Marbled Steak", {"meat_marbled": 2}, 1100, {"stamina": 14, "strength": 8}),
    (205, "Hunter's Board", {"meat_marbled": 2, "meat_prime": 1, "salt": 1}, 1250,
     {"agility": 14, "stamina": 8}),
    (225, "Aged Roast", {"meat_aged": 2, "salt": 1}, 1400, {"intellect": 15, "spirit": 9}),
    (245, "Feast Platter", {"meat_aged": 2, "meat_marbled": 2, "salt": 2}, 1600,
     {"stamina": 20, "spirit": 10}),
    (265, "Select Cut Dinner", {"meat_select": 2, "salt": 1}, 1800,
     {"strength": 16, "stamina": 12}),
    (280, "Banquet Service", {"meat_select": 2, "meat_aged": 2, "salt": 2}, 2000,
     {"agility": 16, "intellect": 16}),
    (300, "Cook's Own Table", {"meat_select": 3, "meat_aged": 2, "meat_marbled": 2, "salt": 3},
     2400, {"strength": 18, "agility": 18, "intellect": 18, "spirit": 18, "stamina": 18}),
]

# ------------------------------------------------------------ engineering
#: (skill, name, inputs, output spec). Built on the bars the mining re-anchor
#: put above steel - Mithril 175, Truesilver/Dark Iron 230, Thorium 245,
#: Arcanite 280, Elementium 290 - which engineering had never reached.
ENG = [
    (190, "Mithril Blunderbuss", {"bar_mithril": 6, "part_steel_barrel": 1,
                                  "part_wooden_stock": 1},
     dict(kind="weapon", slot="ranged", weapon_type="gun",
          stat_template="agi_physical")),
    (205, "Mithril Field Goggles", {"bar_mithril": 4, "part_glass_lens": 2},
     dict(kind="armor", slot="head", armor_type="mail",
          stat_template="agi_int_hybrid")),
    (220, "Voidglass Targeting Scope", {"crystal_voidglass": 2, "bar_mithril": 2,
                                        "part_precision_sight": 1},
     dict(kind="armor", slot="trinket", armor_type="accessory",
          stat_template="agi_physical")),
    (235, "Truesilver Repeater", {"bar_truesilver": 6, "part_steel_barrel": 1,
                                  "part_precision_sight": 1},
     dict(kind="weapon", slot="ranged", weapon_type="gun",
          stat_template="agi_int_hybrid")),
    (250, "Dark Iron Bombard", {"bar_dark_iron": 8, "part_steel_barrel": 2,
                                "part_unstable_trigger": 1},
     dict(kind="weapon", slot="ranged", weapon_type="gun",
          stat_template="agi_physical")),
    (260, "Thorium Shellguard", {"bar_thorium": 6, "part_iron_casing": 2},
     dict(kind="armor", slot="hands", armor_type="mail",
          stat_template="agi_physical")),
    (270, "Thorium Gyro-Visor", {"bar_thorium": 5, "part_glass_lens": 2,
                                 "part_gear_assembly": 1},
     dict(kind="armor", slot="head", armor_type="mail",
          stat_template="agi_int_hybrid")),
    (285, "Arcanite Dragonling Core", {"bar_arcanite": 3, "crystal_arcane": 1,
                                       "part_resonant_core": 1},
     dict(kind="armor", slot="trinket", armor_type="accessory",
          stat_template="int_caster")),
    (295, "Arcanite Longrifle", {"bar_arcanite": 4, "crystal_arcane": 1,
                                 "part_precision_sight": 1, "part_wooden_stock": 1},
     dict(kind="weapon", slot="ranged", weapon_type="gun",
          stat_template="agi_physical")),
    (300, "Elementium Siege Harness", {"bar_elementium": 5, "bar_arcanite": 2,
                                       "part_gear_assembly": 2},
     dict(kind="armor", slot="chest", armor_type="mail",
          stat_template="agi_physical")),
]

EPIC_FROM, RARE_FROM = 265, 150


def item_level(skill):
    return max(1, int(skill * 60 / 300) + 1)


def rarity(skill):
    return "epic" if skill >= EPIC_FROM else ("rare" if skill >= RARE_FROM else "uncommon")


def slug(name):
    return name.lower().replace("'", "").replace(" ", "_").replace("-", "_")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    mats_doc = json.loads(MATS.read_text())
    mats = mats_doc["materials"]
    rec_doc = json.loads(RECIPES.read_text())
    cook = rec_doc["professions"]["cooking"]["recipes"]
    eng = rec_doc["professions"]["engineering"]["recipes"]
    con_doc = json.loads(CONSUM.read_text())

    # ---- new meat
    new_mats = {}
    for mid, spec in NEW_MEAT.items():
        if mid in mats:
            continue
        if spec["skill"] / 5 > TOP_CREATURE:
            print(f"  WARN  {spec['name']} at skill {spec['skill']} needs a level "
                  f"{spec['skill'] // 5} beast; nothing above {TOP_CREATURE} exists. Skipped.")
            continue
        new_mats[mid] = dict(
            name=spec["name"], material_type="meat", profession="cooking",
            tier=spec["tier"], icon_id=mid, stack_limit=20,
            sell_price=20 + spec["skill"], skill_range=mat_spread(spec["skill"]),
            description=spec["description"])

    # ---- cooking recipes + meals
    new_cook, new_meals = {}, []
    have_meals = {m["consumable_id"] for m in con_doc.get("cooked_meals", [])}
    for sk, name, inputs, hp, buff in COOK:
        cid = f"meal_cooked_{slug(name)}"
        rid = f"cook300_{slug(name)}"
        missing = [i for i in inputs if i not in mats and i not in new_mats]
        if missing:
            print(f"  WARN  {name} needs {missing}, skipped")
            continue
        if rid not in cook:
            new_cook[rid] = dict(
                name=name, skill_required=sk, skill_range=spread(sk), source="trainer",
                inputs=inputs,
                output=dict(kind="consumable", consumable_id=cid, count=1))
        if cid not in have_meals:
            stats = ", ".join(f"+{v} {k.replace('_', ' ').title()}" for k, v in buff.items())
            new_meals.append(dict(
                consumable_id=cid, name=name, consumable_type="meal",
                description=f"Restores {hp} health over 30 seconds while you rest, and leaves "
                            f"you well fed ({stats}) for 30 minutes.",
                effect_value=hp, effect_duration=30, level_multiplier=0.0,
                required_level=max(1, sk // 5), cooldown_seconds=2, stack_limit=20,
                vendor_price=0, sell_price=40 + sk // 4,
                buff_category="food", stat_bonuses=buff))

    # ---- engineering
    new_eng = {}
    for sk, name, inputs, out in ENG:
        rid = f"eng300_{slug(name)}"
        if rid in eng:
            continue
        missing = [i for i in inputs if i not in mats]
        if missing:
            print(f"  WARN  {name} needs {missing}, skipped")
            continue
        spec = dict(out, item_level=item_level(sk), rarity=rarity(sk),
                    material_tier=slug(name).split("_")[0])
        new_eng[rid] = dict(name=name, skill_required=sk, skill_range=spread(sk),
                            source="trainer", inputs=inputs, output=spec)

    cb = max((r.get("skill_required", 0) for r in cook.values() if isinstance(r, dict)), default=0)
    eb = max((r.get("skill_required", 0) for r in eng.values() if isinstance(r, dict)), default=0)
    ca = max([cb] + [r["skill_required"] for r in new_cook.values()])
    ea = max([eb] + [r["skill_required"] for r in new_eng.values()])

    print(f"  cooking      {cb} -> {ca}   {len(cook)} -> {len(cook) + len(new_cook)} recipes, "
          f"{len(new_mats)} new cuts, {len(new_meals)} meals")
    print(f"  engineering  {eb} -> {ea}   {len(eng)} -> {len(eng) + len(new_eng)} recipes\n")

    if new_mats:
        print("  new meat (bounded by the level-53 creature ceiling):")
        for mid, m in new_mats.items():
            print(f"    {m['name']:16}skill {m['skill_range'][0]:>4}  needs a level "
                  f"{m['skill_range'][0] // 5} beast")
    if new_cook:
        print(f"\n  {'skill':>6}  cooking")
        for rid, r in sorted(new_cook.items(), key=lambda kv: kv[1]["skill_required"]):
            ins = ", ".join(f"{k.split('_', 1)[-1]}x{v}" for k, v in r["inputs"].items())
            print(f"  {r['skill_required']:>6}  {r['name'][:26]:28}{ins}")
    if new_eng:
        print(f"\n  {'skill':>6}  engineering{'':18}{'rarity':>9}{'ilvl':>6}")
        for rid, r in sorted(new_eng.items(), key=lambda kv: kv[1]["skill_required"]):
            o = r["output"]
            print(f"  {r['skill_required']:>6}  {r['name'][:28]:30}"
                  f"{o['rarity']:>9}{o['item_level']:>6}  {o.get('weapon_type') or o.get('slot')}")

    if args.apply:
        mats.update(new_mats)
        MATS.write_text(json.dumps(mats_doc, indent=2) + "\n")
        cook.update(new_cook)
        eng.update(new_eng)
        RECIPES.write_text(json.dumps(rec_doc, indent=2) + "\n")
        con_doc.setdefault("cooked_meals", []).extend(new_meals)
        CONSUM.write_text(json.dumps(con_doc, indent=2) + "\n")

        # extend the beast tables so the new cuts can actually drop
        src = MEAT_DROPS.read_text()
        if "meat_marbled" not in src and new_mats:
            src = src.replace(
                '    (40, 99, {"meat_rich": 2, "meat_prime": 3}),',
                '    (40, 99, {"meat_rich": 2, "meat_prime": 3}),\n' + NEW_BANDS)
            src = src.replace(
                "FIVE TIERS, matching the five cooked-meal tiers",
                "EIGHT TIERS now, matching the cooked-meal tiers")
            MEAT_DROPS.write_text(src)
            print("\n  extended entities/meat_drops.py BANDS for the new cuts")
        print("  wrote materials.json, recipes.json, consumable_types.json")
    else:
        print("\n  dry run - pass --apply to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
