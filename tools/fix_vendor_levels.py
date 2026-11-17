#!/usr/bin/env python3
"""Vendors sell food, drink, potions and ammunition at the level of the zone they stand in. Idempotent.

    PYTHONPATH=. python3 tools/fix_vendor_levels.py [--check]

Kyle, 16 Nov 2026: "ensure that vendors sell at the appropriate level! Looking at a vendor sell lvl 1 food in a lvl 55
zone is fun and all, but this keeps happening."

WHY IT KEPT HAPPENING. tools/qa_vendor_stock.py listed the problem every time it ran (256 under-levelled listings on
92 vendors) and then returned 0, so it never failed anything. It also matched a vendor to its zone with a slug of its
own that missed every "the_" zone (21 vendors it never looked at) instead of the game's own world/zone_keys.

THE RULE. Each consumable below is on a CHAIN, the tiers that replace each other (Bread and Cheese -> Roasted Meat ->
Spiced Stew...). A vendor in a zone whose band starts at L sells nothing on a chain more than SLACK levels under L
when a better tier exists. An under-levelled item is swapped for the best tier at or under L (what a player arriving
at the zone can use). Two swaps that land on the same tier become one listing. Everything else on the shelf (reagents,
recipes, flavour drinks, elixirs, gadgets) is untouched: those aren't tiers of each other.

The chains are written out rather than read from consumable_types.json's groups, because the groups mix tiers with
side items: Sansam and Dreamfoil potions, the x16 crafted shots and flasks are not the next step of anything.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

SLACK = 8

CHAINS = {
    "health potions": ["healing_potion_minor", "healing_potion_standard", "healing_potion_greater",
                       "healing_potion_superior", "healing_potion_major", "healing_potion_mega",
                       "healing_potion_masterwork", "healing_potion_supreme"],
    "mana potions": ["mana_potion_minor", "mana_potion_standard", "mana_potion_greater", "mana_potion_superior",
                     "mana_potion_major", "mana_potion_mega", "mana_potion_masterwork", "mana_potion_supreme"],
    # the food group's three level-10 side dishes (spiced wine, honeyed fruit, mushroom broth) are tier 10 of it
    "food": ["bread_and_cheese", "roasted_meat", "spiced_wine", "honeyed_fruit", "mushroom_broth", "spiced_stew",
             "hunters_brace_platter", "high_table_feast"],
    "drinks": ["drink_waterskin", "drink_barley_beer", "drink_spring_flask", "drink_honeyed_mead", "drink_birch_wine",
               "drink_deepwell_cordial", "drink_starfall_wine"],
    "meals": ["meal_tough_jerky", "meal_trailbread", "meal_river_fish", "meal_spiced_haunch", "meal_kodo_ribs",
              "meal_saltback_roast", "meal_ember_glazed_ribs"],
    "arrows": ["rough_arrows", "sturdy_arrows", "heavy_arrows", "broadhead_arrows", "barbed_arrows",
               "starleaf_arrows"],
    "bolts": ["rough_bolts", "sturdy_bolts", "heavy_bolts", "quarrel_bolts", "barbed_bolts", "starleaf_bolts"],
    "shot": ["shot_rough", "shot_iron", "shot_charged", "shot_mithril", "shot_thorium", "shot_arcanite"],
}

#: when a chain has several items at one level, the one a swap lands on
PREFERRED = {"roasted_meat"}


def levels():
    d = json.loads(Path("data/consumables/consumable_types.json").read_text(encoding="utf-8"))
    return {it["consumable_id"]: int(it.get("required_level") or 0)
            for lst in d.values() if isinstance(lst, list) for it in lst
            if isinstance(it, dict) and it.get("consumable_id")}


def bands():
    """zone key (world/zone_keys) -> (display name, (lo, hi))"""
    from world.zone_keys import zone_key
    z = json.loads(Path("data/zones/zone_levels.json").read_text(encoding="utf-8"))["zones"]
    return {zone_key(name): (name, tuple(b)) for name, b in z.items()}


def chain_of(lv):
    """item id -> (chain name, [(level, id)] sorted). PREFERRED sorts first among items of one level."""
    out = {}
    for name, ids in CHAINS.items():
        missing = [i for i in ids if i not in lv]
        if missing:
            raise SystemExit(f"chain {name} names items that don't exist: {missing}")
        tiers = sorted((lv[i], i not in PREFERRED, i) for i in ids)
        tiers = [(l, i) for (l, _p, i) in tiers]
        for i in ids:
            out[i] = (name, tiers)
    return out


def best_at(tiers, lo):
    usable = [(l, i) for (l, i) in tiers if l <= lo]
    top = usable[-1][0]
    at_top = [i for (l, i) in usable if l == top]
    pref = [i for i in at_top if i in PREFERRED]
    return (pref or at_top)[0]


def under_levelled(vendor, lo, lv, chains):
    """[(item, chain, the tier it should be)] for this vendor's shelf in a band starting at lo"""
    bad = []
    for cid in vendor.get("sells", []):
        if cid not in chains:
            continue
        name, tiers = chains[cid]
        rl = lv[cid]
        if rl >= lo - SLACK:
            continue
        want = best_at(tiers, lo)
        if lv[want] > rl:
            bad.append((cid, name, want))
    return bad


def main():
    from world.zone_keys import zone_key
    check = "--check" in sys.argv
    lv = levels()
    chains = chain_of(lv)
    bz = bands()
    path = ROOT / "data/npcs/vendors.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    changed, swaps, unplaced = 0, 0, []
    for v in doc["vendors"]:
        hit = bz.get(zone_key(v.get("zone", "")))
        if hit is None:
            unplaced.append((v["vendor_id"], v.get("zone")))
            continue
        lo = hit[1][0]
        bad = under_levelled(v, lo, lv, chains)
        if not bad:
            continue
        # Two old tiers of one chain become the two best tiers in reach, not one listing twice: a cook who sold
        # bread, meat and stew at a level-1 inn sells the zone's dish and the one under it, while that's still
        # within SLACK. Only when the chain has nothing more in reach do they fold into one.
        swap, taken = {}, set(v["sells"])
        for cid, name, want in bad:
            tiers = chains[cid][1]
            reach = [i for (l, i) in sorted(tiers, reverse=True) if lo - SLACK <= l <= lo and i not in taken]
            pick = reach[0] if reach else want
            swap[cid] = pick
            taken.add(pick)
        new, seen = [], set()
        for cid in v["sells"]:
            cid = swap.get(cid, cid)
            if cid not in seen:
                seen.add(cid)
                new.append(cid)
        print(f"  {hit[0]} ({lo}+) {v['name']}: " + ", ".join(f"{c} -> {swap[c]}" for c, _n, _w in bad))
        swaps += len(bad)
        changed += 1
        v["sells"] = new
    if unplaced:
        print(f"  {len(unplaced)} vendor(s) in a zone with no level band: {unplaced}")
    print(f"{swaps} listing(s) on {changed} vendor(s) {'would be' if check else 'were'} brought up to level")
    if changed and not check:
        path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
