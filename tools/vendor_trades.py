#!/usr/bin/env python3
"""Every shop sells its own trade. Idempotent.

    PYTHONPATH=. python3 tools/vendor_trades.py [--check]

Kyle, 14 Nov 2026: "Shop vendors are boring and sell the SAME stuff" and "I find most vendors very
underwhelming overall."

WHAT WAS WRONG. Measured across the 167 shops in data/npcs/vendors.json before this ran:

    spiced_stew                on 99 shops
    mana_potion_standard       on 98
    healing_potion_standard    on 97
    mushroom_broth             on 89
    runeforged_strongbox       on 49

Two earlier passes each fixed one real problem by stamping the fix onto every shop: one gave every
shop a health potion, a mana potion and a food so nobody was ever far from one, and another gave
every shop with bags the three best bags for its level. Both were right about the problem and both
left a blacksmith selling stew, an innkeeper selling strongboxes and an alchemist selling bows.

WHAT THIS DOES. Each shop gets a trade from the title in its name (Innkeeper, Smith, Apothecary,
Seamstress...), or from what most of its shelf already is when the name has no title. Then:

  1. Anything on the shelf outside that trade goes, unless almost nobody else sells it. A rare item
     (five shops or fewer) is moved to a shop in the same town whose trade it is, or to the town's
     general trader, or kept where it is if neither exists, so a recipe or a regional item is never
     lost.
  2. The trade's own core goods are put on the shelf at the shop's level: an alchemist has the two
     best potion tiers it can sell, an inn the two best meals and drinks, a smith the right flux.
  3. General stores (quartermasters, traders, outfitters) keep a small travelling kit: one potion
     of each kind and one meal and drink, all at their best tier, plus bags and lures. They stop
     being a copy of every other shop in town.

The shop's tier is its gear_level, which tools/qa_vendors.py already keeps in line with the zone.
"""
import argparse
import json
import re
import zlib
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
VENDORS = ROOT / "data/npcs/vendors.json"

#: title words -> trade, checked in order, as whole words in the lowercased name
TITLES = [
    # gem sellers (tools/build_gem_sellers.py): pre-cut gems for people who aren't jewelcrafters
    ("gems", ["gem-trader", "gemcutter", "gemstone"]),
    # enchanters (tools/build_enchanters.py): rods, vials and formulas
    ("enchanting", ["enchanter", "enchantress"]),
    ("travel", ["wind rider", "zeppelin", "stablemaster"]),
    ("inn", ["innkeeper", "tavern", "campkeeper"]),
    ("cook", ["cook", "provisioner", "brewer", "butcher", "grainkeeper", "goodwife",
              "fishmonger", "spice-trader"]),
    ("alchemy", ["alchemist", "apothecary", "herbalist", "herb-seller", "elixir", "poisoner",
                 "vat-tender"]),
    ("reagent", ["reagent-keeper", "reagent", "arcanist", "imp-keeper", "undertaker",
                 "mortician", "spiritcarver", "sage", "relic-keeper"]),
    ("smith", ["smith", "weaponsmith", "armorer", "armourer", "armoursmith", "blacksmith"]),
    ("engineer", ["engineer", "mechanic", "salvager", "powderman", "fuel-trader"]),
    ("tailor", ["seamstress", "tailor", "clothier"]),
    ("leather", ["hide-trader", "tanner", "skinner"]),
    ("bowyer", ["bowyer", "fletcher", "trueshot", "shipwright"]),
    ("beast", ["beastcaller"]),
    ("general", ["quartermaster", "trader", "factor", "broker", "merchant", "supplier", "cargo",
                 "curio", "dockmaster", "scout", "outfitter", "warehouse", "tally-clerk",
                 "clerk", "strongbox", "agent", "fence", "dealer", "keeper", "shaft-warden",
                 "road-agent", "cutter", "chandler"]),
]

#: trade -> the kinds of thing it sells
TRADE_KINDS = {
    "gems": {"cut_gem", "gem", "jc_supply"},
    "enchanting": {"ench_supply", "recipe_enchanting", "alch_supply"},
    "inn": {"food", "drink", "buff_food", "cook_ingredient", "recipe_cooking"},
    "cook": {"food", "drink", "buff_food", "cook_ingredient", "recipe_cooking", "fish"},
    "alchemy": {"potion", "elixir", "alch_supply", "herb", "recipe_alchemy"},
    "reagent": {"alch_supply", "scribe", "elixir", "herb", "mana_potion", "recipe_enchanting", "ench_supply",
                "recipe_alchemy", "raw_crystal"},
    "smith": {"smith_supply", "raw_bar", "raw_ore", "recipe_blacksmithing", "shot",
              "upgrade_kit", "jc_supply", "recipe_jewelcrafting"},
    "engineer": {"engineering_goods", "raw_part", "recipe_engineering", "shot", "smith_supply"},
    "tailor": {"tailor_supply", "raw_cloth", "raw_bolt", "recipe_tailoring", "bag"},
    "leather": {"leather_supply", "raw_leather", "recipe_leatherworking", "bag"},
    "bowyer": {"arrow", "wood_supply", "raw_plank", "raw_wood", "recipe_woodworking"},
    "beast": {"lure", "food", "drink", "meat"},
    "travel": {"drink", "food", "lure"},
    "general": {"bag", "potion", "mana_potion", "food", "drink", "lure", "travel_kit", "jc_kit",
                "scribe", "arrow", "shot"},
}
#: in a general store, these kinds are capped to this many items, best tier first
GENERAL_CAPS = {"potion": 1, "mana_potion": 1, "food": 1, "drink": 1, "buff_food": 0}
RARE = 5        # an item on this many shops or fewer counts as a speciality and is never dropped


def _cons():
    c = json.loads((ROOT / "data/consumables/consumable_types.json").read_text(encoding="utf-8"))
    out = {}
    group_kind = {"health_potions": "potion", "mana_potions": "mana_potion", "elixirs": "elixir",
                  "food": "buff_food", "meals": "food", "cooked_meals": "food", "drinks": "drink",
                  "ammo": "arrow", "ammos": "shot", "explosives": "engineering_goods",
                  "gadgets": "engineering_goods", "lures": "lure"}
    for g, rows in c.items():
        if not isinstance(rows, list):
            continue
        for r in rows:
            out[r["consumable_id"]] = (group_kind.get(g, g), int(r.get("required_level") or 1))
    for k in ("kit_field_repair",):
        if k in out:
            out[k] = ("travel_kit", out[k][1])
    return out


def _mats():
    m = json.loads((ROOT / "data/gathering/materials.json").read_text(encoding="utf-8"))["materials"]
    by_id = {
        "vial_empty": "alch_supply", "vial_leaded": "alch_supply", "vial_crystal": "alch_supply",
        "oil_blackmouth": "alch_supply", "oil_fire": "alch_supply", "oil_stonescale": "alch_supply",
        "parchment": "scribe", "thread_coarse": "tailor_supply", "thread_fine": "tailor_supply",
        "thread_silken": "tailor_supply", "dye_mild": "tailor_supply", "dye_bright": "tailor_supply",
        "bleach": "tailor_supply", "flux_weak": "smith_supply", "flux_medium": "smith_supply",
        "flux_strong": "smith_supply", "coal": "smith_supply", "whetstone": "smith_supply",
        "salt": "leather_supply", "tanning_reagent": "leather_supply",
        "curing_salt": "leather_supply", "sinew": "leather_supply",
        "component_string": "wood_supply", "fletching": "wood_supply", "resin": "wood_supply",
        "glue": "wood_supply",
        # jewelcrafting (tools/build_jewelcrafting.py): the kit and the settings are supplies a
        # smith stocks; a general store keeps a kit for the passing jeweller
        "jewelers_kit": "jc_supply",
    }
    out = {}
    for k, v in m.items():
        t, p = v.get("material_type"), v.get("profession")
        if k in by_id:
            out[k] = by_id[k]
        elif k.startswith("setting_"):
            out[k] = "jc_supply"
        elif t == "rod":
            out[k] = "ench_supply"                      # runed rods (tools/build_enchanting.py)
        elif t in ("enchant_mat", "enchant_scroll"):
            out[k] = t                                  # disenchanted or made; never stocked
        elif t == "cut_gem":
            out[k] = "cut_gem"
        elif p == "cooking":
            out[k] = "meat" if t == "meat" else "cook_ingredient"
        elif t == "herb":
            out[k] = "herb"
        elif t == "fish":
            out[k] = "fish"
        elif t == "upgrade_kit":
            out[k] = "upgrade_kit"
        else:
            out[k] = f"raw_{t}"
    return out


def _bags():
    b = json.loads((ROOT / "data/items/bags.json").read_text(encoding="utf-8"))["bags"]
    return {x["item_id"] for x in b}


def classifier():
    cons, mats, bags = _cons(), _mats(), _bags()
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        from world.recipe_manager import get_recipe_info

    def kind(i):
        if i in cons:
            return cons[i][0]
        if i in mats:
            return mats[i]
        if i in bags:
            return "bag"
        prof, _r = get_recipe_info(i)
        if prof:
            return "recipe_" + ("cooking" if prof == "fishing" else prof)
        return "unknown"

    return kind, cons


def trade_of(vendor, kind):
    name = vendor["name"].lower()
    for trade, words in TITLES:
        for w in words:
            if re.search(rf"(?<![\w-]){re.escape(w)}(?![\w])", name):
                return trade
    # no title: the trade most of the shelf already belongs to
    score = Counter()
    for i in vendor.get("sells", []):
        k = kind(i)
        for t, ks in TRADE_KINDS.items():
            if t not in ("general", "travel") and k in ks:
                score[t] += 1
    if score and score.most_common(1)[0][1] >= max(3, len(vendor.get("sells", [])) // 3):
        return score.most_common(1)[0][0]
    return "general"


def best(cons, kind_name, tier, n):
    rows = sorted(((lvl, i) for i, (k, lvl) in cons.items() if k == kind_name and lvl <= tier),
                  reverse=True)
    # the cooked meals are crafted, not sold; only the shop meal and drink lines are core stock
    rows = [r for r in rows if not r[1].startswith("meal_cooked_")]
    return [i for _l, i in rows[:n]]


def _rods(tier):
    """Kyle, 14 Nov 2026: rods "sold by vendors (they can get very pricy very fast)". Every runed
    rod up to the town's level; the arcanite one only a blacksmith makes."""
    return ["runed_copper_rod"] + (["runed_silver_rod"] if tier >= 20 else []) + \
        (["runed_golden_rod"] if tier >= 35 else []) + (["runed_truesilver_rod"] if tier >= 48 else [])


def core(trade, tier, cons):
    """What a shop of this trade always has, at its tier."""
    if trade in ("inn", "cook"):
        return best(cons, "food", tier, 2) + best(cons, "drink", tier, 2) + \
            best(cons, "buff_food", tier, 1)
    if trade == "alchemy":
        return best(cons, "potion", tier, 2) + best(cons, "mana_potion", tier, 2) + ["vial_empty"]
    if trade == "reagent":
        # the best runed rod for the town's level, for the passing enchanter
        return best(cons, "mana_potion", tier, 1) + ["vial_empty", "parchment"] + _rods(tier)[-1:]
    if trade == "enchanting":
        vial = "vial_empty" if tier < 20 else "vial_leaded" if tier < 40 else "vial_crystal"
        return _rods(tier) + [vial]
    if trade == "smith":
        flux = "flux_weak" if tier < 20 else "flux_medium" if tier < 40 else "flux_strong"
        # Kyle, 14 Nov 2026: "Vendors can sell jewel cutting kits and even sets for gemstones"
        # - the plain settings; mithril and finer come from a blacksmith
        metals = ["copper"] + (["silver"] if tier >= 15 else []) + (["gold"] if tier >= 28 else [])
        settings = [f"setting_{k}_{m}" for m in metals[-2:] for k in ("ring", "necklace")]
        return ["whetstone", "coal", flux, "jewelers_kit"] + settings
    if trade == "tailor":
        thread = "thread_coarse" if tier < 20 else "thread_fine" if tier < 40 else "thread_silken"
        return [thread, "dye_mild", "bleach"]
    if trade == "leather":
        return ["salt", "tanning_reagent", "sinew"] + (["curing_salt"] if tier >= 30 else [])
    if trade == "bowyer":
        return ["component_string", "fletching", "resin"] + best(cons, "arrow", tier, 1)
    if trade == "engineer":
        return best(cons, "shot", tier, 1) + ["flux_weak" if tier < 30 else "flux_medium"]
    if trade in ("general", "travel", "beast"):
        return best(cons, "potion", tier, 1) + best(cons, "mana_potion", tier, 1) + \
            best(cons, "food", tier, 1) + best(cons, "drink", tier, 1)
    return []


#: trade -> the profession whose recipes it sells
TRADE_RECIPES = {"inn": "cooking", "cook": "cooking", "alchemy": "alchemy", "smith": "blacksmithing",
                 "engineer": "engineering", "tailor": "tailoring", "leather": "leatherworking",
                 "bowyer": "woodworking", "enchanting": "enchanting"}


def _pick(pool, vid, n):
    """n items from pool, chosen by the shop's own id, so two shops of one trade differ."""
    pool = sorted(pool)
    if len(pool) <= n:
        return pool
    import random
    return random.Random(zlib.crc32(vid.encode("utf-8"))).sample(pool, n)


def extras(trade, tier, vid, cons, recipes):
    """Each shop's own picks within its trade: what makes two smiths in two towns differ."""
    out = []
    prof = TRADE_RECIPES.get(trade)
    if prof:
        skill = min(300, tier * 5)
        pool = [r for r, (p, sk) in recipes.items() if p == prof and skill - 60 <= sk <= skill + 10]
        out += _pick(pool, vid, 6 if trade == "enchanting" else 3)
    if trade == "smith":
        # jewelcrafting designs: a smith's shop is where a jeweller buys supplies
        skill = min(300, tier * 5)
        pool = [r for r, (p, sk) in recipes.items() if p == "jewelcrafting" and skill - 60 <= sk <= skill + 10]
        out += _pick(pool, vid + "j", 2)
    if trade == "reagent":
        # enchanting formulas: a reagent shop is where an enchanter buys vials and rods
        skill = min(300, tier * 5)
        pool = [r for r, (p, sk) in recipes.items() if p == "enchanting" and skill - 60 <= sk <= skill + 10]
        out += _pick(pool, vid + "f", 2)
    if trade in ("alchemy", "reagent"):
        pool = [i for i, (k, lvl) in cons.items() if k == "elixir" and tier - 12 <= lvl <= tier]
        out += _pick(pool, vid + "e", 3 if trade == "alchemy" else 2)
    if trade == "engineer":
        pool = [i for i, (k, lvl) in cons.items() if k == "engineering_goods" and tier - 15 <= lvl <= tier]
        out += _pick(pool, vid + "g", 4)
    if trade == "general":
        pool = [i for i, (k, lvl) in cons.items() if k in ("lure", "travel_kit") and lvl <= tier]
        out += _pick(pool, vid + "l", 2)
    return out


def _vendor_recipes():
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        from world.recipe_manager import all_recipes_by_source
        rs = all_recipes_by_source("vendor")
    return {r: (v[0], int(v[1].get("skill_required") or 1)) for r, v in rs.items()}


def plan(vendors, kind, cons):
    recipes = _vendor_recipes()
    seller_count = Counter(i for v in vendors for i in set(v.get("sells", [])))
    trades = {v["vendor_id"]: trade_of(v, kind) for v in vendors}
    by_zone = defaultdict(list)
    for v in vendors:
        by_zone[v.get("zone")].append(v)
    new = {v["vendor_id"]: [] for v in vendors}
    moves = []
    for v in vendors:
        vid, trade = v["vendor_id"], trades[v["vendor_id"]]
        allowed = TRADE_KINDS[trade]
        tier = int(v.get("gear_level") or 1)
        keep = []
        for i in v.get("sells", []):
            k = kind(i)
            if k in allowed or k == "unknown":
                keep.append(i)
                continue
            if seller_count[i] > RARE:
                continue                                   # common elsewhere: just drop it
            home = next((w for w in by_zone[v.get("zone")] if w is not v
                         and k in TRADE_KINDS[trades[w["vendor_id"]]]), None)
            if home is None and trade != "general":
                # no shop of its trade in town: the town's general trader carries odd goods
                home = next((w for w in by_zone[v.get("zone")] if w is not v
                             and trades[w["vendor_id"]] == "general"), None)
            if home is not None:
                moves.append((i, vid, home["vendor_id"]))
            else:
                keep.append(i)                              # nowhere better in town: stays
        if trade in ("general", "travel", "beast"):
            # a travelling kit, not a copy of the alchemist and the inn: the best tier only
            capped, seen = [], Counter()
            ranked = sorted(keep, key=lambda i: -(cons.get(i, ("", 0))[1]))
            for i in ranked:
                k = kind(i)
                cap = GENERAL_CAPS.get(k)
                if cap is not None and seller_count[i] > RARE:
                    if seen[k] >= cap:
                        continue
                    seen[k] += 1
                capped.append(i)
            keep = [i for i in keep if i in capped]
        for i in core(trade, tier, cons) + extras(trade, tier, vid, cons, recipes):
            if i not in keep and kind(i) != "unknown":
                keep.append(i)
        new[vid] = keep
    for i, src, dst in moves:
        if i not in new[dst]:
            new[dst].append(i)
    # nothing that could be bought before may become unbuyable: an item no shop sells any more
    # goes back to the shops that had it, preferring the ones whose trade it is
    still = Counter(i for s in new.values() for i in s)
    for i in seller_count:
        if still[i]:
            continue
        had = [v for v in vendors if i in v.get("sells", [])]
        fit = [v for v in had if kind(i) in TRADE_KINDS[trades[v["vendor_id"]]]] or had
        for v in fit[:RARE]:
            new[v["vendor_id"]].append(i)
    # every vendor-source recipe is on some shelf: one nobody picked goes to the shop of its trade
    # whose level is closest to the recipe's skill
    still = Counter(i for s in new.values() for i in s)
    for rid, (prof, sk) in recipes.items():
        if still[rid]:
            continue
        shops = [v for v in vendors if TRADE_RECIPES.get(trades[v["vendor_id"]]) == prof
                 or (prof == "jewelcrafting" and trades[v["vendor_id"]] == "smith")
                 or (prof == "enchanting" and trades[v["vendor_id"]] == "reagent")]
        if shops:
            best_shop = min(shops, key=lambda v: abs(int(v.get("gear_level") or 1) * 5 - sk))
            new[best_shop["vendor_id"]].append(rid)
    return trades, new, moves


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only, write nothing")
    args = ap.parse_args()
    data = json.loads(VENDORS.read_text(encoding="utf-8"))
    vendors = data["vendors"]
    kind, cons = classifier()
    trades, new, moves = plan(vendors, kind, cons)

    before = Counter(i for v in vendors for i in v.get("sells", []))
    after = Counter(i for s in new.values() for i in s)
    print("shops by trade:", dict(Counter(trades.values()).most_common()))
    print(f"{len(moves)} speciality items moved to the right shop in the same town")
    print("the most repeated items, before -> after:")
    for i, n in before.most_common(12):
        print(f"  {i:<28} {n:>4} -> {after[i]}")
    same = Counter(tuple(sorted(s)) for s in new.values() if s)
    print(f"shops whose shelf is identical to another shop's: before "
          f"{sum(n for n in Counter(tuple(sorted(v['sells'])) for v in vendors).values() if n > 1)}"
          f", after {sum(n for n in same.values() if n > 1)}")
    unknown = sorted({i for s in new.values() for i in s if kind(i) == "unknown"})
    if unknown:
        print(f"{len(unknown)} ids nothing recognises (kept): {unknown[:12]}")
    if args.check:
        return 0
    for v in vendors:
        v["sells"] = new[v["vendor_id"]]
    VENDORS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {VENDORS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
