#!/usr/bin/env python3
"""Tier every vendor's bags and consumables to the vendor's own level.

    PYTHONPATH=. python3 tools/overhaul_vendor_stock.py [--check]

Kyle, 5 Nov 2026: "We have numerous bag icons, I gave an example of 6 slot
bag sold for 10s and you just dropped bags into almost every single vendor
but never above that 6 slot bag. So that's a critical logic flaw. A lvl 3
vendor vs a lvl 50 vendor shouldn't sell identical bags."

He is exactly right and the cause is duller than a logic flaw - it is
copy-paste. Measured across data/npcs/vendors.json:

    small_burlap_sack      (4 slots) on 87 of 150 vendors
    worn_leather_satchel   (6 slots) on 87
    buckled_saddlebag      (6 slots) on 86
    green_dyed_sack        (4 slots) on 85

The same four starter bags, the only four, stamped onto 89 vendors
regardless of tier. Nothing above six slots was purchasable ANYWHERE in the
game, while the catalog quietly contained 8, 10, 12, 16, 18 and 20-slot bags
nobody could reach.

Worth being clear that the generator was never the problem:
LootGenerator.generate_bag already tiers correctly - tier 3 yields 4-6
slots, tier 20 yields 10-12, tier 38 yields 16-18. The hand-written `sells`
lists simply bypassed it.

WHAT THIS DOES

Bags: a vendor that sells bags now stocks the three largest it can justify -
the biggest bags whose required_level is at or under its tier - instead of
the same four sacks. Tier is the vendor's own gear_level, which already
exists and already tracks zone level.

Consumables: vendors stocking nothing drinkable, or nothing within ten
levels of their tier, get a health potion, a mana potion and a food at the
best tier they qualify for. Most vendors are already fine here (median
vendor sells consumables two levels ABOVE its own tier), so this touches
few.

Prices are left alone. Against Kyle's datapoint that a level 12 player holds
2.5g, the existing curve already reads correctly: 6-slot 10s, 8-slot 25s,
10-slot 50s, 12-slot 1g, 16-slot 4g, 18-slot 8g. A 12-slot bag being most of
a level 12 player's purse is a real decision, which is the point.

Idempotent.
"""
import json
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

VENDORS = ROOT / "data/npcs/vendors.json"
BAGS = ROOT / "data/items/bags.json"
CONSUMABLES = ROOT / "data/consumables/consumable_types.json"

#: How many bags a bag-selling vendor stocks.
BAG_SHELF = 3

#: A vendor whose best consumable is this far below its own tier is restocked.
STALE_GAP = 10


ZONE_LEVELS = ROOT / "data/zones/zone_levels.json"

#: How far below its zone's minimum a vendor's tier may sit before it is
#: treated as wrong rather than as a deliberate low-end stall.
BELOW_BAND_SLACK = 3


def _retier_to_zone(rows):
    """Pull vendors whose tier sits below their zone's level band up to it.

    Kyle, 5 Nov 2026: "Ensure this isn't just for bags. It's for consumables,
    food, gear (WHEN APPROPRIATELY SOLD) at the level of the zone the vendor
    is in."

    This is the root cause under all three. 59 of 146 vendors carry a
    gear_level well below the zone they stand in - every vendor in
    Glittervein (a level 46-49 zone) is tier 26, and the Abyssal Sands
    (44-47) are tier 25. gear_level drives the gear roll AND, now, the bag
    shelf and the consumable picks, so one wrong number was making a
    level-48 town sell level-26 everything.

    Corrected to the MIDPOINT of the band. The minimum would leave a player
    finishing the zone with nothing worth buying, and the maximum would sell
    gear they cannot use yet.

    ONLY vendors below their band are moved. Three sit above it - the
    Undercity quartermaster, the Undercity zeppelin stall and Hela Windhoof
    at Camp Taurajo - and those are hubs that serve players well past the
    local zone level, which is a reasonable thing for a capital to do and
    not obviously a mistake. Raising a shop's tier fixes an under-levelled
    shelf; lowering one would take goods away from players who can use them.
    """
    bands = json.loads(ZONE_LEVELS.read_text(encoding="utf-8"))["zones"]
    # zone_levels keys are display names ("Arathi Central"); vendors carry
    # slugs ("arathi_central").
    norm = {k.lower().replace(" ", "_").replace("'", ""): v for k, v in bands.items()}

    fixed = []
    for v in rows:
        band = norm.get((v.get("zone") or "").lower())
        tier = v.get("gear_level")
        if not band or tier is None:
            continue
        low, high = band[0], band[1]
        if tier >= low - BELOW_BAND_SLACK:
            continue
        want = int(round((low + high) / 2))
        fixed.append((v.get("name"), v.get("zone"), tier, want))
        v["gear_level"] = want
    return fixed


def _load():
    bags = json.loads(BAGS.read_text(encoding="utf-8"))["bags"]
    cons = json.loads(CONSUMABLES.read_text(encoding="utf-8"))
    return bags, cons


def _bag_shelf_for(tier, bags, vendor_id=""):
    """The best BAG_SHELF bags this tier can justify, smallest first.

    Picks by capacity among everything the tier qualifies for, so the shelf
    moves up with the vendor instead of being frozen at the starter sacks.
    The smallest tiers naturally still get the sacks - there is nothing else
    they qualify for - which is correct rather than a fallback.
    """
    eligible = [b for b in bags if b.get("required_level", 1) <= tier]
    if not eligible:
        eligible = sorted(bags, key=lambda b: b.get("required_level", 1))[:1]
    # One bag per CAPACITY. The catalog carries colour variants at the same
    # size (two 4s, two 6s, two 8s...), and taking the top three by capacity
    # alone produced shelves like [12, 12, 16] - two identical-sized bags
    # burning a slot that could have shown the next tier up. The player reads
    # a shelf for what sizes exist, not how many recolours do.
    #
    # WHICH variant is chosen rotates by vendor, and that is not cosmetic.
    # Picking the alphabetically-first every time made Small Burlap Sack and
    # Worn Leather Satchel unobtainable ANYWHERE - they have no craft recipe
    # either, so two bags simply left the game, which qa_bags_obtainable
    # caught. Rotating by vendor id keeps every variant on sale somewhere and
    # means two neighbouring towns do not show identical shelves, which is
    # the point of having the icon variety at all.
    by_capacity = {}
    grouped = {}
    for b in sorted(eligible, key=lambda b: b["item_id"]):
        grouped.setdefault(b["bag_capacity"], []).append(b)
    for capacity, variants in grouped.items():
        # zlib.crc32, NOT hash(): Python randomises string hashing per
        # process (PYTHONHASHSEED), so hash() would pick a different variant
        # on every run and rewrite the file forever. A tool that is not
        # deterministic is not idempotent, whatever its --check says.
        pick = zlib.crc32(f"{vendor_id}:{capacity}".encode()) % len(variants)
        by_capacity[capacity] = variants[pick]
    shelf = [by_capacity[c] for c in sorted(by_capacity)][-BAG_SHELF:]
    return [b["item_id"] for b in shelf]


def _consumable_picks(tier, cons):
    """One health potion, one mana potion and one food at this vendor's tier."""
    picks = []
    for category in ("health_potions", "mana_potions", "food"):
        rows = [r for r in cons.get(category, []) if r.get("required_level", 1) <= tier]
        if rows:
            rows.sort(key=lambda r: r.get("required_level", 1))
            picks.append(rows[-1]["consumable_id"])
    return picks


def main():
    check = "--check" in sys.argv
    bags, cons = _load()
    bag_ids = {b["item_id"] for b in bags}
    cons_req = {}
    for rows in cons.values():
        for row in (rows if isinstance(rows, list) else []):
            cons_req[row["consumable_id"]] = row.get("required_level", 1)

    doc = json.loads(VENDORS.read_text(encoding="utf-8"))
    vendors = doc.get("vendors", doc)
    rows = list(vendors.values()) if isinstance(vendors, dict) else vendors

    bag_changed = cons_changed = 0
    spread = {}

    tier_fixed = _retier_to_zone(rows)

    for v in rows:
        tier = v.get("gear_level") or 10
        sells = list(v.get("sells") or [])

        # ---- bags, only for vendors that already sell them. Which vendors
        # stock bags is a content decision someone made deliberately; this
        # fixes WHICH bags, not WHO.
        had = [x for x in sells if x in bag_ids]
        if had:
            want = _bag_shelf_for(tier, bags, v.get("vendor_id", ""))
            if sorted(had) != sorted(want):
                sells = [x for x in sells if x not in bag_ids]
                # Bags go at the front so they are not buried under reagents
                # on a long shelf.
                sells = want + sells
                bag_changed += 1
            caps = [b["bag_capacity"] for b in bags if b["item_id"] in want]
            spread.setdefault(tier, sorted(caps))

        # ---- consumables, checked PER CATEGORY.
        #
        # Checking the best consumable overall hid the real problem. Hela
        # Windhoof, tier 32, passed because she sells a level 30 meal - while
        # her health potions stopped at level 10. A tier 32 vendor with
        # starter potions is exactly the "appropriate level food or potions"
        # complaint, and one healthy category was covering for two stale ones.
        picks = []
        for category in ("health_potions", "mana_potions", "food"):
            in_category = {r["consumable_id"] for r in cons.get(category, [])}
            rows_c = [r for r in cons.get(category, []) if r.get("required_level", 1) <= tier]
            if not rows_c:
                continue
            rows_c.sort(key=lambda r: r.get("required_level", 1))
            best_available = rows_c[-1].get("required_level", 1)
            best_here = [cons_req[x] for x in sells if x in in_category]
            # "Is anything better available to this vendor" rather than a
            # fixed staleness window. The window was 10 levels, which was fine
            # when potions existed only at 1/10/25/40 but is a whole tier of
            # slack now the ladder runs every 8-9 levels - it left a tier 48
            # shop selling level 40 potions with a level 48 potion on the
            # shelf next door. The question was never "how stale", it is
            # "could this vendor do better".
            if best_here and max(best_here) >= best_available:
                continue
            best = rows_c[-1]["consumable_id"]
            if best not in sells:
                picks.append(best)
        if picks:
            sells = sells + picks
            cons_changed += 1

        v["sells"] = sells

    print(f"vendors re-levelled to their zone: {len(tier_fixed)}")
    for name, zone, was, now in sorted(tier_fixed, key=lambda r: r[2] - r[3])[:8]:
        print(f"   {str(name)[:26]:26s} {zone:22s} {was} -> {now}")
    if len(tier_fixed) > 8:
        print(f"   ... and {len(tier_fixed) - 8} more")
    print(f"vendors re-tiered for bags: {bag_changed}")
    print(f"vendors restocked with consumables: {cons_changed}")
    print("\nbag shelf by vendor tier (capacities):")
    for tier in sorted(spread):
        print(f"   tier {tier:>2}: {spread[tier]}")

    if check:
        print("\n--check: nothing written")
        return 0

    VENDORS.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {VENDORS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
