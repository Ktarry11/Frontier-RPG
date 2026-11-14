#!/usr/bin/env python3
"""Cooking: meat into meals, and the four dead cloth tiers. Idempotent.

  PYTHONPATH=. python3 tools/build_cooking.py

Kyle, 2026-10-28: "we need to build the cooking system and also expand out our crafting system again.
We need to ensure each harvestable is being used... the higher level or different materials cant end up
being useless."

WHAT THE AUDIT ACTUALLY FOUND, because the scary number was not the real one. 151 of 260 materials are
never a recipe input, which sounds like a catastrophe and is not: most are upgrade kits (outputs, not
inputs) or tiers for levels 45-99 that no zone reaches yet. Filtered to what the world hands you AT OR
BELOW level 42 - the real ceiling, since the Underdark tops out at 40 - exactly FOUR materials are dead
ends, and all four are cloth:

    cloth_spidersilk    drops from 25
    cloth_dusk_velvet   drops from 34
    cloth_gossamer      drops from 38
    cloth_thistledown   drops from 42

The cause is one missing link, not a missing profession. Tailoring has 113 recipes and a ceiling of
skill 240, but the chain is cloth -> BOLT -> armour and there are only seven cloth-to-bolt recipes. The
ladder simply stops, so every cloth above silk falls on the floor. Four recipes fix it.

COOKING IS A NEW PROFESSION AND NEEDED A NEW INPUT. Nothing in the game dropped meat - skinning gives
leather, and that was all a beast was worth. entities/meat_drops.py adds it, mirroring the skinning
model rather than inventing a second answer to "which beast gives which tier".

COOKED FOOD DOES BOTH THINGS AT ONCE, which is what finally reconciles the two meanings of "food" this
codebase has been carrying. Vendor meals restore a bar over time. The old "food" consumables are a stat
buff in a buff slot. A COOKED meal is both: it restores more than the vendor version AND carries the
Well Fed buff, which is the whole reason to cook rather than shop.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: (id, name, tier_level, description) - the raw stock, dropped by entities/meat_drops.py
MEATS = [
    ("meat_stringy", "Stringy Meat", 1, "Tough, lean and not much of it. Boil it long enough and it gives in."),
    ("meat_lean", "Lean Cut", 8, "Honest meat off an honest animal."),
    ("meat_thick", "Thick Cut", 16, "A proper joint. Heavy enough to notice in a pack."),
    ("meat_rich", "Rich Cut", 24, "Marbled and dark. Worth the weight."),
    ("meat_prime", "Prime Cut", 32, "The piece a cook puts aside before anybody else sees the carcass."),
]

#: (recipe_id, name, meat, qty, skill, total restored, seconds, {stat buffs}, flavour)
#: Restores roughly 30% more than the vendor meal of the same tier AND carries a Well Fed buff, which
#: is the entire argument for cooking instead of shopping.
COOKED = [
    ("cook_campfire_strips", "Campfire Strips", "meat_stringy", 2, 0, 250, 20,
     {"stamina": 3}, "Cut thin, hung over the fire, eaten before it cools."),
    ("cook_seared_cut", "Seared Cut", "meat_lean", 2, 50, 380, 22,
     {"stamina": 5, "strength": 3}, "Hard sear, pink middle. A cook's first real trick."),
    ("cook_herb_roast", "Herb-Crusted Roast", "meat_thick", 2, 100, 520, 24,
     {"stamina": 7, "strength": 5}, "Rolled in whatever grows nearby. It is never the same twice."),
    ("cook_slow_stew", "Slow Stew", "meat_rich", 3, 150, 690, 26,
     {"stamina": 9, "spirit": 5}, "On the fire all day. The sort of thing a camp gathers around."),
    ("cook_feast_roast", "Feast Roast", "meat_prime", 3, 200, 900, 30,
     {"stamina": 12, "strength": 7, "spirit": 5}, "Enough for a table. Cooked by somebody showing off."),
]

#: The four missing links. Cloth tiers in the live level range with nowhere to go.
NEW_BOLTS = [
    ("tail_bolt_spidersilk", "Bolt of Spidersilk", "cloth_spidersilk", "bolt_spidersilk", 3, 130),
    ("tail_bolt_dusk_velvet", "Bolt of Dusk Velvet", "cloth_dusk_velvet", "bolt_dusk_velvet", 4, 165),
    ("tail_bolt_gossamer", "Bolt of Gossamer", "cloth_gossamer", "bolt_gossamer", 4, 195),
    ("tail_bolt_thistledown", "Bolt of Thistledown", "cloth_thistledown", "bolt_thistledown", 5, 225),
]


def main():
    # ---------------------------------------------------------------- materials
    mp = ROOT / "data/gathering/materials.json"
    mdata = json.loads(mp.read_text(encoding="utf-8"))
    mats = mdata.get("materials", mdata)
    # FIELD SHAPE COPIED FROM A WORKING RECORD, not guessed. make_material_instance reads
    # data["profession"] directly and KeyErrors without it - the first build dropped meat that then
    # could not be instantiated, so the kill log said nothing and the bag stayed empty.
    TIER_NAME = {1: "starter", 8: "early", 16: "early", 24: "mid", 32: "mid"}
    for mid, name, tier, desc in MEATS:
        mats[mid] = {
            "name": name,
            "material_type": "meat",
            "tier": TIER_NAME.get(tier, "mid"),
            "skill_range": [max(0, tier * 5 - 5), tier * 5 + 20, tier * 5 + 45, tier * 5 + 70],
            "sell_price": 2 + tier,
            "stack_limit": 20,
            "profession": "cooking",
            "icon_id": mid,
            "description": desc,
        }
    mp.write_text(json.dumps(mdata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ---------------------------------------------------------------- profession
    pp = ROOT / "data/professions/professions.json"
    pdata = json.loads(pp.read_text(encoding="utf-8"))
    profs = pdata.get("professions", pdata)
    sibling = profs.get("alchemy", {})
    profs["cooking"] = {
        **{k: v for k, v in sibling.items() if k not in ("description", "name")},
        "name": "Cooking",
        "description": "Turn meat into meals that restore health and leave you well fed.",
    }
    pp.write_text(json.dumps(pdata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ---------------------------------------------------------------- consumables
    cp = ROOT / "data/consumables/consumable_types.json"
    cdata = json.loads(cp.read_text(encoding="utf-8"))
    cooked = []
    for rid, name, meat, qty, skill, total, secs, bonuses, flavour in COOKED:
        tier = next(t for m, _n, t, _d in MEATS if m == meat)
        bonus_str = ", ".join(f"+{v} {k.title()}" for k, v in bonuses.items())
        cooked.append({
            "consumable_id": rid.replace("cook_", "meal_cooked_"),
            "name": name,
            "consumable_type": "meal",
            "description": f"{flavour} Restores {total} health over {secs} seconds while you rest, "
                           f"and leaves you well fed ({bonus_str}) for 30 minutes.",
            "effect_value": total,
            "effect_duration": secs,
            "level_multiplier": 0.0,
            "required_level": max(1, tier),
            "cooldown_seconds": 2,
            "stack_limit": 20,
            "vendor_price": 0,          # not sold: the point is that you made it
            "sell_price": 5 + tier,
            # BOTH EFFECTS ON ONE ITEM. consumable.use applies the regen for a "meal" and, when
            # stat_bonuses are present, the Well Fed buff too - see the change in that file.
            "buff_category": "food",
            "stat_bonuses": bonuses,
        })
    cdata["cooked_meals"] = cooked
    cp.write_text(json.dumps(cdata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ---------------------------------------------------------------- recipes
    rp = ROOT / "data/crafting/recipes.json"
    rdata = json.loads(rp.read_text(encoding="utf-8"))
    profs_r = rdata["professions"]
    cook = profs_r.setdefault("cooking", {"recipes": {}})
    cook.setdefault("recipes", {})
    for rid, name, meat, qty, skill, total, secs, bonuses, flavour in COOKED:
        cook["recipes"][rid] = {
            "name": name,
            "inputs": {meat: qty},
            "skill_required": skill,
            "output": {"kind": "consumable",
                       "consumable_id": rid.replace("cook_", "meal_cooked_"), "count": 1},
        }
    tail = profs_r.setdefault("tailoring", {"recipes": {}})
    for rid, name, cloth, bolt, qty, skill in NEW_BOLTS:
        tail["recipes"][rid] = {
            "name": name,
            "inputs": {cloth: qty},
            "skill_required": skill,
            "output": {"kind": "material", "material_id": bolt, "count": 1},
        }
    rp.write_text(json.dumps(rdata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ---------------------------------------------------------------- the last dead crystal
    # crystal_tideglass was added to node pools with the Drowning Floor and Southern Needles this
    # same day and nothing consumed it - a material introduced and orphaned in one session, which is
    # exactly how the other 51 orphans happened. Every sibling crystal feeds an Engineering part, so
    # this one does too: tideglass comes out of water-cut stone, so it makes a seal.
    eng = profs_r.setdefault("engineering", {"recipes": {}})
    eng["recipes"]["eng_part_tide_seal"] = {
        "name": "Tideglass Seal",
        "inputs": {"crystal_tideglass": 2, "bar_bronze": 1},
        "skill_required": 72,
        "output": {"kind": "material", "material_id": "part_tide_seal", "count": 1},
    }
    mats["part_tide_seal"] = {
        "name": "Tideglass Seal",
        "material_type": "part",
        "tier": "early",
        "skill_range": [60, 85, 110, 135],
        "sell_price": 14,
        "stack_limit": 20,
        "profession": "engineering",
        "icon_id": "part_tide_seal",
        "description": "Ground tideglass set in a bronze ring. Keeps water out of things that mind.",
    }
    mp.write_text(json.dumps(mdata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    rp.write_text(json.dumps(rdata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"cooking: {len(MEATS)} meats, {len(COOKED)} recipes")
    print(f"tailoring: +{len(NEW_BOLTS)} bolt recipes, closing the cloth ladder to level 42")


if __name__ == "__main__":
    main()
