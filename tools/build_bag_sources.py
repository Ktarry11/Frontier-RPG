#!/usr/bin/env python3
"""Make every bag in the catalog obtainable, by craft or by shop.

Kyle, 2026-10-31: "We need to ensure bags can be made through tailoring or sold
via some vendors. We have about 20 bag icons on file. So there's no shortage
there." Asked right after he discovered his bags were full and had been reading
that as six bosses dropping nothing.

MEASURED FIRST. data/items/bags.json holds 13 bags. Of those:
  - 3 were craftable (linen, wool, silk - tailoring)
  - 0 were on any vendor's sells list
  - 0 dropped from any boss (the bag_capacity hits in the loot files are all
    `"bag_capacity": 0` on ordinary gear)
  - 6 showed up in shops via the random GEAR roll

So 7 of 13 could not be obtained at all, and - the part that matters - the six
that shops did offer were all MID AND HIGH tier. The random gear roll carries a
deliberate level floor, so the starter bags were exactly what it never produced.
A level 5 character with 24 slots and no bag had no way to buy one anywhere in
the world. That is the player Kyle just was.

This fixes both ends:
  - TAILORING gains 6 recipes, so all 9 cloth-appropriate bags are craftable
    across the skill ladder rather than stopping at silk
  - the 4 STARTER bags go on general-goods vendors by name, which puts them on
    the shelf permanently instead of leaving them to a roll that excludes them
"""
import sys, os, json, pathlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = pathlib.Path(__file__).resolve().parent.parent

#: (recipe_id, bag_id, bolt, count, skill_required, skill_range)
#: Skills placed against the tiers tailoring already uses for that bolt, so a
#: bag sits with the rest of its cloth rather than inventing a new rung.
NEW_RECIPES = [
    ("tail_cotton_bag",    "rose_clasped_bag",      "bolt_cotton",      4,  45, [50, 60, 70, 80]),
    ("tail_hempen_bag",    "violet_clasped_bag",    "bolt_hempen",      4,  75, [80, 90, 100, 110]),
    ("tail_mageweave_bag", "frostward_pack",        "bolt_mageweave",   5, 140, [145, 155, 165, 175]),
    ("tail_spidersilk_bag","runeforged_strongbox",  "bolt_spidersilk",  5, 175, [180, 190, 200, 210]),
    ("tail_gossamer_bag",  "flameward_coffer",      "bolt_gossamer",    6, 205, [210, 220, 230, 240]),
    ("tail_runecloth_bag", "verdant_reagent_case",  "bolt_runecloth",   8, 255, [260, 270, 280, 290]),
]

#: The four the gear roll's level floor can never offer. Sold by name instead.
STARTER_BAGS = ["small_burlap_sack", "green_dyed_sack",
                "worn_leather_satchel", "buckled_saddlebag"]


def main():
    write = "--write" in sys.argv
    bags = {b["item_id"]: b for b in json.load(open(ROOT / "data/items/bags.json", encoding="utf-8"))["bags"]}

    # ---- 1. tailoring -----------------------------------------------------------------
    rpath = ROOT / "data/crafting/recipes.json"
    rdoc = json.load(open(rpath, encoding="utf-8"))
    tail = rdoc["professions"]["tailoring"]
    recs = tail.get("recipes", tail)
    added = []
    for rid, bag_id, bolt, n, skill, rng in NEW_RECIPES:
        if bag_id not in bags:
            print(f"  REFUSING: {rid} names unknown bag '{bag_id}'")
            return 1
        if rid in recs:
            continue
        recs[rid] = {
            "name": bags[bag_id]["name"],
            "inputs": {bolt: n},
            "skill_required": skill,
            "output": {"kind": "bag", "bag_id": bag_id},
            "skill_range": rng,
            "source": "trainer",
        }
        added.append((rid, bags[bag_id]["name"], bags[bag_id]["bag_capacity"], bolt, n, skill))

    # ---- 2. starter bags onto general-goods vendors ------------------------------------
    vpath = ROOT / "data/npcs/vendors.json"
    vdoc = json.load(open(vpath, encoding="utf-8"))
    #: A general store: sells food or drink, and is not a high-tier quartermaster.
    stocked = []
    for v in vdoc["vendors"]:
        sells = v.get("sells") or []
        general = any(str(s).startswith(("meal_", "drink_", "bread", "roasted", "spiced"))
                      for s in sells)
        if not general or (v.get("gear_level") or 0) > 30:
            continue
        missing = [b for b in STARTER_BAGS if b not in sells]
        if missing:
            v["sells"] = sells + missing
            stocked.append((v["name"], v.get("zone"), len(missing)))

    print(f"  {len(added)} tailoring recipes added "
          f"(tailoring had 3 bag recipes, now {3 + len(added)} of 13 bags craftable)")
    for rid, name, cap, bolt, n, skill in added:
        print(f"      {rid:22s} {name:26s} {cap:2d} slots  {n}x {bolt} @ skill {skill}")
    print(f"\n  {len(stocked)} general stores now carry the 4 starter bags")
    for name, zone, n in stocked[:12]:
        print(f"      {name} ({zone})")
    if len(stocked) > 12:
        print(f"      ... and {len(stocked)-12} more")

    if write:
        json.dump(rdoc, open(rpath, "w", encoding="utf-8"), indent=2)
        json.dump(vdoc, open(vpath, "w", encoding="utf-8"), indent=2)
        print("\n  written")
    else:
        print("\n  dry run - pass --write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
