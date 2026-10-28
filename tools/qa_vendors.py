#!/usr/bin/env python3
"""Shops sell things worth buying, at the level of the people who shop there.

    PYTHONPATH=. python3 tools/qa_vendors.py [--stock]

Kyle, 2026-10-28, after playing the Underdark: "the shops are selling garbage, low level items... they
are falling back into generic trash."

He was right, and the cause was three separate things that all look the same from the shop window:

  1. STALE gear_level. It is a hand-set number in vendors.json and nothing ever checked it against the
     zone, so it rots silently every time a zone's level band moves. Kael's Bastion sat at 22 inside a
     32-40 zone; the Undercity at 16 inside 30-34.
  2. A 70% COMMON rarity roll. Even at the right level, "Plain Wand / Simple Cloak / Plain Amulet" is
     strictly worse than any quest green. A capital's quartermaster selling mostly whites IS generic
     trash, whatever its item level says.
  3. BAGS WITH NO FLOOR. generate_bag filters required_level <= tier, which caps the ceiling and
     ignores the bottom, so a tier-22 vendor happily offered a level-1 Worn Leather Satchel.

TOWNS HAVE NO MOBS, so a town vendor's tier cannot be derived from its own zone - it comes from the
region the town serves, which is a judgement and therefore written down in TOWN_REGION below rather
than guessed. That map is the part a human has to maintain; everything else here is derived.

--stock rolls and prints each vendor's actual shelf, which is the only way to see what a player sees.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

#: Which region's level band a town's shops are priced for. A town is where you resupply BEFORE and
#: AFTER the country around it, so the tier tracks the top of that band, not its middle.
TOWN_REGION = {
    "razor_hill": "Durotar",
    # A capital outfits people heading INTO the country around it, not people farming its own
    # streets, so Orgrimmar is priced for the Barrens its gates open onto.
    "orgrimmar": "Central Barrens",
    "crossroads": "Northern Barrens",
    "camp_taurajo": "Southern Barrens",
    "tarren_mill": "Eastern Hillsbrad",
    "kaels_bastion": "The Crystalline Underdark",
    "freewind_post": "Southern Thousand Needles",
    "undercity": "Undercity",
    "sepulcher": "Silverpine North",
    "brill": "Eastern Tirisfal",
    "splintertree_post": "Ashenvale East",
    "ratchet": "Northern Barrens",
}

#: How far a vendor's tier may sit from the TOP of its band before it is wrong. Slightly under is
#: correct - you outgrow a town's stock as you work the zone - but 14 levels under is not "slightly".
LOW, HIGH = -5, 3


def key(s):
    return str(s).lower().replace(" ", "_").replace("'", "")


def zone_bands():
    e = json.loads((ROOT / "data/creatures/encounters.json").read_text())["zones"]
    c = json.loads((ROOT / "data/creatures/creatures.json").read_text())["creatures"]
    out = {}
    for zn, zd in e.items():
        lv = []
        tables = [zd.get("open_zone", {})] + list(zd.get("subzones", {}).values()) \
            + list(zd.get("caves", {}).values())
        for t in tables:
            for n in t.get("creatures", {}):
                r = c.get(n, {}).get("level_range")
                if r:
                    lv += list(r)
        if lv:
            out[key(zn)] = (min(lv), max(lv))
    return out


def main():
    bands = zone_bands()
    vendors = json.loads((ROOT / "data/npcs/vendors.json").read_text())["vendors"]
    gear = [v for v in vendors if v.get("sells_gear", True)]
    fails, warns = [], []

    print(f"== {len(vendors)} vendors, {len(gear)} of them sell gear\n")
    print(f"{'vendor':<30}{'zone':<24}{'tier':>5}  {'band':<10}{'from':<28}verdict")
    for v in sorted(gear, key=lambda v: (v.get("zone", ""), v["vendor_id"])):
        z = key(v.get("zone", ""))
        tier = v.get("gear_level")
        # TOWN_REGION WINS WHERE IT HAS AN OPINION. A town's own encounters are incidental to what its
        # shops are for - Orgrimmar's streets are level 13-17 and its quartermaster outfits people
        # walking out into a 12-24 Barrens. Deriving from the town's own mobs priced the capital for
        # its own rats.
        region = TOWN_REGION.get(z)
        if region and bands.get(key(region)):
            src, b = region, bands[key(region)]
        else:
            src, b = z, bands.get(z)
        if b is None:
            fails.append(f"{v['vendor_id']}: zone '{z}' has no level band and no TOWN_REGION entry - "
                         f"add one, or its tier can never be checked")
            verdict, src = "NO BAND", "?"
        elif tier is None:
            fails.append(f"{v['vendor_id']}: no gear_level, so it falls back to the flat default")
            verdict = "NO TIER"
        else:
            off = tier - b[1]
            if off < LOW:
                verdict = f"TOO LOW by {-off}"
                fails.append(f"{v['vendor_id']}: tier {tier} against a band topping out at {b[1]} "
                             f"({src}) - sells gear {-off} levels below what the zone kills")
            elif off > HIGH:
                verdict = f"high by {off}"
                warns.append(f"{v['vendor_id']}: tier {tier} is {off} above its band ({src})")
            else:
                verdict = "ok"
        print(f"{v['vendor_id']:<30}{z:<24}{str(tier):>5}  {str(b):<10}{src:<28}{verdict}")

    # ---- the two engine-level defects, checked rather than assumed
    print("\n== rarity mix")
    from world.vendor_manager import VENDOR_GEAR_RARITY_WEIGHTS as W
    tot = sum(W.values())
    print("  " + "  ".join(f"{k} {100*v/tot:.0f}%" for k, v in W.items()))
    if W.get("common", 0) / tot > 0.5:
        fails.append(f"vendor gear is {100*W['common']/tot:.0f}% common - a shelf of whites is the "
                     f"'generic trash' complaint whatever its item level")

    print("\n== what the shelves actually hold")
    # ROLL THE REAL VENDORS, not generate_bag directly. The first version of this check called the
    # generator with the raw tier and kept failing after the fix was in, because the floor lives on the
    # VENDOR's call - testing the function tested a path no player ever walks.
    import random
    from entities.loot_generator import LootGenerator
    from world.vendor_manager import get_vendor_manager
    random.seed(11)
    lg = LootGenerator()
    vm = get_vendor_manager()
    worst_bag, mix, seen_bags = {}, {"common": 0, "uncommon": 0, "rare": 0}, {}
    # Identify bags by the CATALOG, not by looking for "Bag"/"Sack" in the name. The keyword version
    # missed Coffer, Strongbox, Case and Pack, which both undercounted bags and quietly filed rare
    # bags as rare GEAR - that is where a phantom "17% rare gear" reading came from.
    _bags = json.loads((ROOT / "data/items/bags.json").read_text())
    bag_names = {b["name"] for b in (_bags["bags"] if isinstance(_bags, dict) and "bags" in _bags
                                     else _bags)}
    for v in sorted(gear, key=lambda v: v["vendor_id"]):
        nv = vm.get_vendor(v["vendor_id"])
        if nv is None:
            fails.append(f"{v['vendor_id']}: in vendors.json but VendorManager cannot resolve it")
            continue
        for _ in range(12):                      # several shelves, since stock is cached per instance
            nv._gear_stock = None
            for it in nv.get_gear_stock(lg):
                r = getattr(it, "rarity", "common")
                mix[r] = mix.get(r, 0) + 1
                rl = getattr(it, "required_level", 0)
                if getattr(it, "name", None) in bag_names:
                    seen_bags.setdefault(nv.vendor_id, set()).add(it.name)
                    worst_bag[nv.vendor_id] = min(worst_bag.get(nv.vendor_id, 99), rl)
    bag_pool = {vid: len(v) for vid, v in seen_bags.items()}
    tot = sum(mix.values()) or 1
    print("  rolled %d items: %s" % (tot, "  ".join(f"{k} {100*n/tot:.0f}%" for k, n in mix.items())))
    # EPICS ARE THE MAX-REP REWARD (Kyle, 2026-10-28), so no shop may sell one at any tier. This
    # caught a real regression: putting a FLOOR on bag level collapsed tier-38 vendors onto the one
    # required_level 30 epic in the catalog and sold it on every shelf.
    if mix.get("epic") or mix.get("legendary"):
        fails.append(f"vendors rolled {mix.get('epic', 0)} epic and {mix.get('legendary', 0)} "
                     f"legendary items - shops must stop at rare, epics are earned at max reputation")

    # THE BAR IS "NO STARTER BAGS", NOT "BAGS AT TIER". data/items/bags.json holds thirteen bags
    # topping out at required_level 30, and the top one is the epic a shop may not sell - so at tier 38
    # a strict floor leaves exactly one candidate and the vendor becomes a vending machine for it. That
    # is the regression this check exists to catch, so it asserts the two things that actually matter:
    # nothing from the starter end of the catalog, and never a pool of one.
    STARTER = 20
    bad_bags = {vid: lvl for vid, lvl in worst_bag.items()
                if lvl < min(STARTER, max(1, (vm.get_vendor(vid).gear_level or 10) // 2))}
    print(f"  {len(worst_bag)} vendors offered a bag; {len(bad_bags)} offered one from the starter end")
    for vid, lvl in sorted(bad_bags.items()):
        fails.append(f"{vid} (tier {vm.get_vendor(vid).gear_level}) offers a required_level {lvl} bag")
    thin = sorted(vid for vid, n in bag_pool.items() if n == 1)
    print(f"  {len(thin)} vendors have a bag pool of exactly one item")
    for vid in thin:
        fails.append(f"{vid}: every bag roll returns the same item - the catalog has nothing else in "
                     f"range, so it reads as a vending machine")

    print()
    for w in warns:
        print("  note:", w)
    if fails:
        print(f"\nFAIL ({len(fails)})")
        for f in fails:
            print("  -", f)
        return 1
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
