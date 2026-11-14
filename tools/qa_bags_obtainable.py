#!/usr/bin/env python3
"""Every bag must be gettable, and the starter ones must be gettable EARLY.

Kyle, 2026-10-31: "We need to ensure bags can be made through tailoring or sold
via some vendors." Asked straight after discovering his bags were full, having
read that as six Grom's Rest bosses dropping nothing.

What was wrong was not that bags were missing - the system, the catalog and the
icons all existed. It was that 7 of 13 bags had no route to a player at all,
and, worse, the 6 that shops did offer were all mid-and-high tier. Vendors get
their bags from the random GEAR roll, and that roll carries a deliberate LEVEL
FLOOR, so the starter bags were precisely what it could never produce. A level 5
character with 24 slots could not buy a bag anywhere in the world.

So this checks the thing that actually broke:
  1. every bag in the catalog has SOME route (craft, or a vendor's sells list)
  2. the starter bags are on shelves a LOW-LEVEL player can reach

The second is the one with teeth. A check that only asserted (1) would have
passed happily on the state Kyle hit.
"""
import sys, os, json, pathlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = pathlib.Path(__file__).resolve().parent.parent
STARTER_LEVEL = 10          # "a low-level player"


def main():
    bags = {b["item_id"]: b for b in json.load(open(ROOT / "data/items/bags.json", encoding="utf-8"))["bags"]}
    recipes = json.load(open(ROOT / "data/crafting/recipes.json", encoding="utf-8"))["professions"]
    vendors = json.load(open(ROOT / "data/npcs/vendors.json", encoding="utf-8"))["vendors"]

    craftable = {}
    for prof, pdata in recipes.items():
        recs = pdata.get("recipes", pdata) if isinstance(pdata, dict) else {}
        for rid, rec in recs.items():
            if not isinstance(rec, dict):
                continue
            out = rec.get("output") or {}
            if out.get("kind") == "bag" and out.get("bag_id"):
                craftable.setdefault(out["bag_id"], []).append((prof, rid))

    sold = {}
    for v in vendors:
        for iid in (v.get("sells") or []):
            if iid in bags:
                sold.setdefault(iid, []).append(v)

    print(f"  {len(bags)} bags in the catalog\n")
    fails = []
    for bid, b in sorted(bags.items(), key=lambda kv: kv[1]["required_level"]):
        c = craftable.get(bid, [])
        s = sold.get(bid, [])
        routes = []
        if c:
            routes.append(f"craft({c[0][0]})")
        if s:
            routes.append(f"{len(s)} shops")
        mark = "" if routes else "   <-- UNOBTAINABLE"
        if not routes:
            fails.append(f"{b['name']} has no craft recipe and no vendor")
        print(f"    {b['name']:26s} {b['bag_capacity']:2d} slots  lvl {b['required_level']:2d}  "
              f"{', '.join(routes) or 'nothing'}{mark}")

    # THE CHECK WITH TEETH: can a new character actually buy one?
    early = [bid for bid, b in bags.items()
             if b["required_level"] <= STARTER_LEVEL and sold.get(bid)]
    print(f"\n  bags a level {STARTER_LEVEL} character can buy: {len(early)}")
    if not early:
        fails.append(f"no bag with required_level <= {STARTER_LEVEL} is on any vendor's "
                     f"sells list - the random gear roll's level floor excludes them, so a "
                     f"new character has no way to buy a bag")

    if fails:
        print()
        for f in fails:
            print(f"  FAIL - {f}")
    print("\nPASS" if not fails else "\nFAIL")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
