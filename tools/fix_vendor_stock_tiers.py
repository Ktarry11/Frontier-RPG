#!/usr/bin/env python3
"""Upgrade every vendor's consumables to the best tier the zone's players can use. Idempotent.

    PYTHONPATH=. python3 tools/fix_vendor_stock_tiers.py [--apply]

Kyle: "we need to ensure that vendors in these zones sell unique level appropriate stuff."

tools/qa_vendor_stock.py found 193 under-levelled listings across 57 vendors, and the one that
says it best: MEGA HEALING POTION AND MEGA MANA POTION (level 40) ARE SOLD BY NOBODY IN THE GAME.
They have been in data/consumables/consumable_types.json the whole time while the level 46-49 camp
at the bottom of the Glittervein cenote sold the level 25 Superior tier.

THE UPGRADE IS WITHIN A GROUP, NOT A REPLACEMENT OF THE LIST, and that is the whole design of this
tool. The obvious fix - give every high-level vendor one canonical "best stuff" list - would make
all 25 vendors in the high zones sell the same eight things, which is the SECOND half of what Kyle
asked for and the opposite of it. So:

  * a listing is only ever swapped for a HIGHER TIER OF ITS OWN GROUP: food for food, mana potion
    for mana potion, ammo for ammo. A cook keeps selling meals, a brewer keeps selling elixirs,
    and the shop's character survives the rebalance.
  * nothing is added and nothing is removed. A vendor with four things still has four things.
  * elixirs are EXCLUDED. They are not a ladder - "Elixir of the Wind" and "Elixir of Greater
    Endurance" buff different stats, so swapping one for a higher-level one changes WHAT the shop
    sells rather than how good it is. qa_vendor_stock flags them as under-levelled because by
    level they are; the answer there is to stock more elixirs, which is a content decision and not
    this tool's business.
  * untiered goods (whetstone, flux, vials, parchment, coal) are untouched. A whetstone is a
    whetstone.

Tiers below the zone floor are left alone when there is no better tier to move to, so a starter
zone selling starter goods is not "fixed" into selling something that does not exist yet.

--apply writes data/npcs/vendors.json. Without it, this only prints the diff.
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

VENDORS = Path("data/npcs/vendors.json")

#: GROUPS THAT ARE A TRUE QUALITY LADDER - the whole correctness of this tool rests on this set,
#: and my first version got it wrong by assuming a "group" in consumable_types.json IS a ladder.
#: It is not. The group `food` holds bread_and_cheese (1), roasted_meat (10), honeyed_fruit (10),
#: mushroom_broth (10), spiced_wine (10) and spiced_stew (25) - so "upgrade to the best usable
#: tier" turned a fishmonger's bread and cheese into SPICED WINE, picked arbitrarily from three
#: items tied at level 10. A level test cannot catch that: `explosives` and `gadgets` have no tied
#: levels at all and are still not ladders, because a Brine Flask is not an upgrade of a Static
#: Charge and a Grapple Launcher is not an upgrade of a Clockwork Lantern - they are different
#: TOOLS that happen to be sorted by level.
#:
#: So this set is decided by meaning, not by the data's shape: these are the five groups where the
#: item's name literally is "<tier> of the same thing", one item per level, and a higher one makes
#: the lower one pointless.
LADDER = {"health_potions", "mana_potions", "meals", "drinks", "cooked_meals"}

#: Deliberately NOT ladders, each for its own reason, and none of them this tool's business:
#:   elixirs     different stats - swapping changes WHAT the shop sells
#:   food        mixes meals and a drink, with three items tied at level 10
#:   explosives  different effects (brine / static / ember / void), not tiers
#:   gadgets     different tools
#:   ammos       elemental shot varieties, not a quality ladder
#: Where these have nothing above level ~30 for a level 46 player, that is a CONTENT gap - items
#: that do not exist yet - and writing it into a vendor list would not create them.
NOT_A_LADDER = {"elixirs", "food", "explosives", "gadgets", "ammos"}

#: `ammo` is a ladder PER KIND: rough/sturdy/heavy arrows and rough/sturdy/heavy bolts are two
#: separate tracks sharing one group, so an archer's arrows must never become bolts.
KIND_SUFFIX = {"ammo"}

#: a vendor may stock one tier below the zone floor without it counting as stale; shops carry a
#: little of the cheap stuff. Beyond this the listing is upgraded.
SLACK = 8


def levels():
    d = json.loads(Path("data/consumables/consumable_types.json").read_text(encoding="utf-8"))
    lv = {}
    for grp, lst in d.items():
        if not isinstance(lst, list):
            continue
        for it in lst:
            if isinstance(it, dict) and it.get("consumable_id"):
                lv[it["consumable_id"]] = (int(it.get("required_level") or 0), grp,
                                           it.get("name", it["consumable_id"]))
    if len(lv) < 50 or "healing_potion_mega" not in lv:
        raise SystemExit(f"consumable lookup resolved {len(lv)} ids and is missing a known one - "
                         f"the record shape changed. Fix the lookup, not the threshold.")
    return lv


def bands():
    b = json.loads(Path("data/zones/zone_levels.json").read_text(encoding="utf-8"))["zones"]

    def slug(n):
        return n.lower().removeprefix("the ").replace(" ", "_").replace("'", "")

    by = {}
    for z, v in b.items():
        by.setdefault(slug(z), (z, v))
        by.setdefault(slug(z).split("_")[-1], (z, v))
    return by


def main():
    apply = "--apply" in sys.argv
    lv = levels()
    by_slug = bands()

    tiers = defaultdict(list)
    for cid, (rl, grp, name) in lv.items():
        tiers[grp].append((rl, cid, name))
    for g in tiers:
        tiers[g].sort()

    doc = json.loads(VENDORS.read_text(encoding="utf-8"))
    changed = 0
    touched = []

    for r in doc["vendors"]:
        hit = by_slug.get(str(r.get("zone", "")).lower())
        if not hit:
            continue
        zn, b = hit
        lo = b[0]
        swaps = []
        for i, cid in enumerate(list(r.get("sells", []))):
            if cid not in lv:
                continue
            rl, grp, _ = lv[cid]
            if grp in NOT_A_LADDER or rl == 0 or rl >= lo - SLACK:
                continue
            if grp not in LADDER and grp not in KIND_SUFFIX:
                continue
            # the best tier of THIS group the zone's floor player can use
            usable = [(l, c, n) for (l, c, n) in tiers[grp] if l <= lo and l > rl]
            if grp in KIND_SUFFIX:
                # same track only: arrows stay arrows, bolts stay bolts
                kind = cid.rsplit("_", 1)[-1]
                usable = [u for u in usable if u[1].rsplit("_", 1)[-1] == kind]
            if not usable:
                continue
            # A TIE MEANS WE DO NOT KNOW WHICH ONE IS THE UPGRADE, so change nothing. Everything
            # in LADDER has one item per level today; this is here so that adding a second
            # level-40 potion later makes this tool stop rather than guess.
            best = usable[-1][0]
            if sum(1 for u in usable if u[0] == best) > 1:
                continue
            nl, nc, nn = usable[-1]
            if nc in r["sells"]:          # already stocks the better tier; drop the stale one
                continue
            r["sells"][i] = nc
            swaps.append((cid, rl, nc, nl))
            changed += 1
        # a swap can collide with something already in the list
        seen, dedup = set(), []
        for c in r["sells"]:
            if c not in seen:
                seen.add(c)
                dedup.append(c)
        r["sells"] = dedup
        if swaps:
            touched.append((zn, b, r["name"], swaps))

    for zn, b, who, swaps in sorted(touched, key=lambda t: (-t[1][0], t[0], t[2])):
        print(f"\n  {zn} ({b[0]}-{b[1]})  {who}")
        for cid, rl, nc, nl in swaps:
            print(f"      {cid:32} lvl {rl:2}  ->  {nc:30} lvl {nl}")

    print(f"\n{changed} listings upgraded across {len(touched)} vendors.")
    if apply:
        VENDORS.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"-> wrote {VENDORS}")
    else:
        print("(dry run - pass --apply to write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
