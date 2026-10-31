#!/usr/bin/env python3
"""Does a vendor sell things worth buying AT THE LEVEL YOU MEET THEM?

    PYTHONPATH=. python3 tools/qa_vendor_stock.py

Kyle: "we need to ensure that vendors in these zones sell unique level appropriate stuff."

Two different failures, and only the second is obvious from a vendor record:

  UNDER-LEVELLED   the vendor sells a consumable whose required_level is far below the band of the
                   zone it stands in, WHEN A BETTER TIER OF THE SAME THING EXISTS. A level 25
                   Superior Healing Potion in a 46-49 camp is not flavour, it is the shopkeeper
                   handing a level 47 player a potion that heals for a third of their health bar,
                   while the level 40 Mega tier sits in the data unsold.
  NOT STOCKED      the best tier the player can actually use is not for sale ANYWHERE in the band.
                   This is the one that matters: a tier nobody sells might as well not exist, and
                   it is invisible from any single vendor's record.

A vendor is matched to its zone's band through data/zones/zone_levels.json, so the thresholds move
with the encounter tables rather than being restated here.

NOTE ON THE FIRST VERSION OF THIS CHECK. It built the level lookup with `it.get("id")`, the field
is `consumable_id`, so the dict came out EMPTY and the audit cheerfully reported "0 under" for
every vendor in the game - including the ones I already knew were wrong. Hence `_levels()`
asserting that it resolved a plausible number of ids and that a known id is among them: a lookup
that silently finds nothing turns this whole file into a check that passes for free.
"""
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

#: how far below a zone's floor a consumable may sit before it counts as under-levelled. A shop
#: should stock things a player arriving at the zone floor can use; 8 is roughly one tier's worth
#: of slack, so a 46-49 zone selling a level 40 item is fine and a level 25 one is not.
SLACK = 8

#: consumable groups where tiers REPLACE each other, so selling an old tier is a defect. Reagents,
#: vials, flux and the like have no tiers and are excluded - a whetstone is a whetstone.
TIERED = {"health_potions", "mana_potions", "food", "meals", "drinks", "cooked_meals",
          "ammo", "ammos", "elixirs", "explosives", "gadgets"}


def _levels():
    """consumable_id -> (required_level, group, name). Asserts it actually found things."""
    d = json.loads(Path("data/consumables/consumable_types.json").read_text(encoding="utf-8"))
    lv = {}
    for grp, lst in d.items():
        if not isinstance(lst, list):
            continue
        for it in lst:
            if isinstance(it, dict) and it.get("consumable_id"):
                lv[it["consumable_id"]] = (int(it.get("required_level") or 0), grp,
                                           it.get("name", it["consumable_id"]))
    if len(lv) < 50 or "healing_potion_superior" not in lv:
        raise SystemExit(f"the consumable level lookup resolved {len(lv)} ids and is missing a "
                         f"known one - the record shape changed, and every claim in this file is "
                         f"worthless until the lookup is fixed rather than the threshold relaxed.")
    return lv


def _vendor_bands(bands):
    """vendor record -> (zone display name, band), for vendors whose zone we can place."""
    def slug(n):
        return n.lower().removeprefix("the ").replace(" ", "_").replace("'", "")

    by_slug = {}
    for z, b in bands.items():
        by_slug.setdefault(slug(z), (z, b))
        by_slug.setdefault(slug(z).split("_")[-1], (z, b))
    out = {}
    for r in json.loads(Path("data/npcs/vendors.json").read_text(encoding="utf-8"))["vendors"]:
        hit = by_slug.get(str(r.get("zone", "")).lower())
        if hit:
            out[r["vendor_id"]] = (r, hit[0], hit[1])
    return out


def main():
    lv = _levels()
    bands = {z: b for z, b in
             json.loads(Path("data/zones/zone_levels.json").read_text(encoding="utf-8"))["zones"].items()}
    vend = _vendor_bands(bands)

    # best tier of each tiered group, by level
    tiers = defaultdict(list)
    for cid, (rl, grp, name) in lv.items():
        if grp in TIERED:
            tiers[grp].append((rl, cid, name))
    for g in tiers:
        tiers[g].sort()

    under = defaultdict(list)       # vendor -> [(lv, cid, better tier)]
    sold_in_band = defaultdict(set)  # band floor bucket -> set of cids on sale

    for vid, (r, zn, b) in vend.items():
        lo = b[0]
        for cid in r.get("sells", []):
            if cid not in lv:
                continue
            rl, grp, name = lv[cid]
            sold_in_band[lo].add(cid)
            if grp not in TIERED or rl == 0 or rl >= lo - SLACK:
                continue
            better = [(l, c, n) for (l, c, n) in tiers[grp] if rl < l <= lo]
            if better:
                under[(zn, tuple(b), r["name"])].append((rl, cid, better[-1]))

    print("=== UNDER-LEVELLED STOCK (a better tier exists and the player can use it) ===")
    if not under:
        print("  none")
    for (zn, b, who) in sorted(under, key=lambda k: (-k[1][0], k[0], k[2])):
        rows = under[(zn, b, who)]
        print(f"\n  {zn} ({b[0]}-{b[1]})  -  {who}")
        for rl, cid, (bl, bc, bn) in sorted(rows):
            print(f"      sells {cid:34} lvl {rl:2}   ->  should be {bc:30} lvl {bl}")

    print("\n=== TIERS NOBODY IN THE BAND SELLS ===")
    floors = sorted(sold_in_band)
    gaps = 0
    for lo in floors:
        if lo < 20:
            continue
        on_sale = sold_in_band[lo]
        for grp, rows in sorted(tiers.items()):
            usable = [(l, c, n) for (l, c, n) in rows if l <= lo]
            if not usable:
                continue
            best = usable[-1]
            if best[1] not in on_sale and any(c in on_sale for (_, c, _) in rows):
                print(f"  band {lo:2}+: best {grp[:14]:14} is {best[2]} (lvl {best[0]}) "
                      f"- not sold; band stocks {sorted(c for (_, c, _) in rows if c in on_sale)}")
                gaps += 1
    if not gaps:
        print("  none")

    print(f"\n{sum(len(v) for v in under.values())} under-levelled listings across "
          f"{len(under)} vendors, {gaps} unsold best-tiers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
