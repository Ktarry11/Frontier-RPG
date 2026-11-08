#!/usr/bin/env python3
"""Give every plank its three branches - sticks, fiber, pages - the whole way up.

NAMING LEAVES HEADROOM. Kyle, 7 Nov 2026: "I wouldnt give fancy final names
like eternal as we will have another 16 trees out there bro." The top tier
here is NOT the top of the tree ladder - sixteen woods sit parked above skill
300 for the endgame expansion - so these run out at craft terms (Ironbound,
Warded, Gilded) and the superlatives stay unspent for the trees that deserve
them.

    PYTHONPATH=. python3 tools/build_woodworking_300.py [--apply]

Idempotent. Prints the plan by default; --apply writes it.

=============================================================================
THE CHAIN, AS KYLE DESCRIBED IT
=============================================================================

Kyle, 7 Nov 2026: "Each tree produces a log (wood cutting) the log is turned to
a plank (like smelting - this gives exp for wood cutting) then the log can be
turned into pages, sticks, or fiber. This is what is used for crafting." Then,
confirming which step branches: "Planks can turn into sticks, fiber, or pages."

    tree  --gather-->  log  --sawmill-->  plank  -->  stick | fiber | pages

The first two steps were already built correctly. The third was built for SEVEN
planks out of twenty-four, and the stick branch did not exist at all.

    17 of 24 planks fed NOTHING. Silverbark, Goldenleaf, Redbark, Sapglow,
    Marshwillow, Duskwood, Nightshade, Thornveil, Bloodroot, Bloodwood,
    Felbark, Moonpetal, Emberwood, Frostheart, Ebonthorn, Starleaf, Stormoak -
    every one of them a dead end, which means the trees that make them are
    nodes wasting a zone slot.

=============================================================================
WHY STICKS, AND WHY THE TIERS GO DEEPER
=============================================================================

Woodworking already makes 33 staves, 21 bows, 13 wands, 7 polearms and 4
crossbows. Every one of those is a shaft with something on the end, so the
stick branch is the one the weapons actually wanted - it is wired into the
recipes by tools/tier_crafting_reagents.py as woodworking's `shaft` slot,
beside the glue-and-resin `bond` slot, rather than by a second mechanism.

Fiber and pages existed with THREE tiers each, authored when only seven planks
fed them. Spread across twenty-four planks that means a skill-300 Stormoak
plank yields the same Tough Fiber as a skill-75 Bramblewood one, which is not
progression, it is a plateau. Each branch now runs six tiers over the whole
ladder, the original three keeping their names and their places.

A note on counts: Kyle's "around 22 or so materials from 1-300" is a rule for
GATHERABLES - herb, ore, wood, cloth, leather - the things a player harvests.
Sticks, fiber and pages are crafted intermediates, like bars and bolts, and
six tiers each is what the ladder needs to stay even.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MATS = ROOT / "data" / "gathering" / "materials.json"
RECIPES = ROOT / "data" / "crafting" / "recipes.json"

#: (upper plank skill, tier index). A plank at or below the bound takes that tier.
BANDS = [(50, 0), (110, 1), (180, 2), (240, 3), (280, 4), (10 ** 9, 5)]

#: Six tiers per branch. The first three of fiber and pages ALREADY EXIST and
#: keep their ids, names and art - this only adds the upper three.
BRANCHES = {
    "stick": ("sticks", [
        ("stick_green",      "Green Shaft",      "Cut this season. It still has a little give in it."),
        ("stick_seasoned",   "Seasoned Shaft",   "Dried slowly in the dark until it stopped arguing."),
        ("stick_hardened",   "Hardened Shaft",   "Fire-cured and planed true. It will not warp again."),
        ("stick_lacquered",  "Lacquered Shaft",  "Sealed against damp and rot, and it rings when struck."),
        ("stick_banded",     "Banded Shaft",     "Ringed with metal at the stress points so it does not split."),
        ("stick_ironbound",  "Ironbound Shaft",  "Wrapped end to end. Heavy in the hand, and it will outlast you."),
    ]),
    "fiber": ("fibers", [
        ("fiber_coarse",     "Coarse Fiber",     None),
        ("fiber_supple",     "Supple Fiber",     None),
        ("fiber_tough",      "Tough Fiber",      None),
        ("fiber_braided",    "Braided Fiber",    "Three strands worked together; it takes a load without creaking."),
        ("fiber_corded",     "Corded Fiber",     "Twisted tight and tarred. Rope-makers would recognise the work."),
        ("fiber_warded",     "Warded Fiber",     "Steeped in something that keeps the rot and the rats off."),
    ]),
    "pages": ("pages", [
        ("pages_rough",      "Rough Pages",      None),
        ("pages_pressed",    "Pressed Pages",    None),
        ("pages_fine",       "Fine Pages",       None),
        ("pages_vellum",     "Vellum Pages",     "Thin enough to read through, strong enough to argue with."),
        ("pages_leafed",     "Leafed Pages",     "Pressed between boards until every sheet lies flat."),
        ("pages_gilded",     "Gilded Pages",     "Edged in gold leaf. Mostly for show, but the show matters."),
    ]),
}

#: Planks consumed per unit. Pages come thin, shafts come whole.
COST = {"stick": 2, "fiber": 1, "pages": 1}

#: Recipe skill sits a little above the plank's own, so a woodworker who can
#: make the plank can shortly do something with it.
SKILL_OFFSET = {"stick": 5, "fiber": 0, "pages": 10}

TIER_BY_CAP = [(75, "early"), (150, "mid"), (225, "late"), (300, "endgame")]


def tier_name(skill):
    for cap, name in TIER_BY_CAP:
        if skill <= cap:
            return name
    return "endgame"


def band_of(skill):
    for bound, idx in BANDS:
        if skill <= bound:
            return idx
    return len(BANDS) - 1


def spread(lo):
    return [lo + 5, lo + 15, lo + 25, lo + 35]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    mats_doc = json.loads(MATS.read_text())
    mats = mats_doc["materials"]
    rec_doc = json.loads(RECIPES.read_text())
    ww = rec_doc["professions"]["woodworking"]["recipes"]

    planks = sorted((m["skill_range"][0], mid) for mid, m in mats.items()
                    if m["material_type"] == "plank" and m.get("skill_range")
                    and m["skill_range"][0] <= 300)

    new_mats, new_recipes, pending_art = {}, {}, []
    for branch, (folder, tiers) in BRANCHES.items():
        for idx, (mid, name, desc) in enumerate(tiers):
            if mid in mats:
                continue
            new_mats[mid] = dict(
                name=name, material_type=branch, profession="woodworking",
                tier=tier_name(BANDS[idx][0] if BANDS[idx][0] < 10 ** 9 else 300),
                icon_id=mid, stack_limit=20, sell_price=8 + idx * 22,
                description=desc or f"{name}.")
            art = ROOT / "assets" / "gathering_nodes" / folder / f"{mid}.png"
            if not art.exists():
                pending_art.append((name, art.relative_to(ROOT)))

    for skill, plank in planks:
        idx = band_of(skill)
        for branch, (_folder, tiers) in BRANCHES.items():
            out_id = tiers[idx][0]
            rid = f"ww300_{plank[len('plank_'):]}_{branch}"
            if rid in ww:
                continue
            # a recipe already turning this plank into this branch is kept
            if any(isinstance(r, dict) and plank in (r.get("inputs") or {})
                   and (r.get("output") or {}).get("material_id") == out_id
                   for r in ww.values()):
                continue
            sk = min(300, skill + SKILL_OFFSET[branch])
            new_recipes[rid] = dict(
                name=f"{mats[plank]['name'].replace(' Plank', '')} {tiers[idx][1]}",
                skill_required=sk, skill_range=spread(sk), source="trainer",
                station="sawmill" if branch == "stick" else None,
                inputs={plank: COST[branch]},
                output=dict(kind="material", material_id=out_id))
            if new_recipes[rid]["station"] is None:
                del new_recipes[rid]["station"]

    before = max((r.get("skill_required", 0) for r in ww.values()
                  if isinstance(r, dict)), default=0)
    after = max([before] + [r["skill_required"] for r in new_recipes.values()])

    print(f"  woodworking reaches skill {before} -> {after}")
    print(f"  {len(ww)} -> {len(ww) + len(new_recipes)} recipes, "
          f"{len(new_mats)} new materials\n")
    print(f"  chain: tree -> log -> plank -> stick | fiber | pages\n")

    import collections
    fed = collections.Counter()
    for rid, r in new_recipes.items():
        fed[mats[list(r["inputs"])[0]]["name"]] += 1
    dead_before = [p for _, p in planks
                   if not any(isinstance(r, dict) and p in (r.get("inputs") or {})
                              for r in ww.values())]
    print(f"  {len(dead_before)} of {len(planks)} planks fed nothing before; "
          f"every plank now feeds all three branches")

    if new_mats:
        print(f"\n  new materials:")
        for branch, (_f, tiers) in BRANCHES.items():
            made = [n for mid, n, _ in tiers if mid in new_mats]
            if made:
                print(f"    {branch:7}{', '.join(made)}")

    byband = collections.defaultdict(list)
    for skill, plank in planks:
        byband[band_of(skill)].append(mats[plank]["name"].replace(" Plank", ""))
    print(f"\n  {'band':6}{'planks':>7}   stick / fiber / pages")
    for idx in sorted(byband):
        names = [BRANCHES[b][1][idx][1] for b in ("stick", "fiber", "pages")]
        print(f"  {idx + 1:<6}{len(byband[idx]):>7}   {' / '.join(names)}")

    if pending_art:
        print(f"\n  ICON PENDING ({len(pending_art)}) - bag shows a text box until these land:")
        for name, rel in pending_art[:4]:
            print(f"    {name:22}{rel}")
        if len(pending_art) > 4:
            print(f"    ... and {len(pending_art) - 4} more")

    if args.apply:
        mats.update(new_mats)
        MATS.write_text(json.dumps(mats_doc, indent=2) + "\n")
        ww.update(new_recipes)
        RECIPES.write_text(json.dumps(rec_doc, indent=2) + "\n")
        print(f"\n  wrote materials.json, recipes.json")
    else:
        print("\n  dry run - pass --apply to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
