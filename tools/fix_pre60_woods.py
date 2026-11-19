#!/usr/bin/env python3
"""Nothing under level 60 is made of a level-60 material: Emberwood, Frostheart and Ebonthorn join the pre-60 ladder.

    PYTHONPATH=. python3 tools/fix_pre60_woods.py           # report
    PYTHONPATH=. python3 tools/fix_pre60_woods.py --write

Kyle, 18 Nov 2026: "Fix up woodworking. Nothing sub 60 should use lvl 60 materials."

Measured that day: woodworking's level 50-56 tier (the Emberwood, Frostheart and Ebonthorn staves, codices, wands,
idols, the banded sticks, corded fibre and leafed pages, and three upgrade kits) was built on three woods sitting at
skill 310, 320 and 330, above the pre-60 line (entities/material_tiers.PRE_60_SKILL_CEILING). None of them grew on
any map, so every one of those recipes could never be made. Sunheart planks (310) sat above their own wood (300) and
fed the level-59 Sunheart pieces.

The fix keeps every name, icon, recipe, vendor and quest reward as it is and moves the woods instead:
  * Emberwood 245, Frostheart 268 and Ebonthorn 275 fill the ladder's gaps (Moonpetal 230, Starleaf 260, Stormoak
    280, Sunheart 300), with their planks on the same numbers and prices between their neighbours;
  * Sunheart planks come down to 300, their wood's;
  * each grows where its neighbours do: Emberwood beside Moonpetal, Frostheart beside Starleaf, Ebonthorn beside
    Stormoak (data/gathering/node_pools.json).
Level 60's woods (material_tiers.LEVEL60_TOP) become the next two up, Voidwood (310) and Dreamwillow (320).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MATS = ROOT / "data/gathering/materials.json"
POOLS = ROOT / "data/gathering/node_pools.json"

#: id -> (skill range, sell price)
RETIER = {
    "wood_emberwood_stump": ([245, 265, 285, 315], 270),
    "plank_emberwood": ([245, 265, 285, 315], 540),
    "wood_frostheart_tree": ([268, 288, 303, 318], 320),
    "plank_frostheart": ([268, 288, 303, 318], 640),
    "wood_ebonthorn_stump": ([275, 295, 310, 325], 340),
    "plank_ebonthorn": ([275, 295, 310, 325], 680),
    "plank_sunheart": ([300, 325, 345, 375], 800),
}
#: the new wood grows in every zone that grows its neighbour, at this weight
GROWS_WITH = {"wood_emberwood_stump": "wood_moonpetal_tree", "wood_frostheart_tree": "wood_starleaf_tree",
              "wood_ebonthorn_stump": "wood_stormoak_tree"}
WEIGHT = 2


def main():
    write = "--write" in sys.argv
    mats = json.loads(MATS.read_text(encoding="utf-8"))
    mm = mats.get("materials", mats)
    changed = 0
    for mid, (rng, price) in RETIER.items():
        if mm[mid]["skill_range"] != rng or mm[mid].get("sell_price") != price:
            print(f"  {mid}: skill {mm[mid]['skill_range'][0]} -> {rng[0]}, sells {mm[mid].get('sell_price')} -> {price}")
            mm[mid]["skill_range"], mm[mid]["sell_price"] = rng, price
            changed += 1
    pools = json.loads(POOLS.read_text(encoding="utf-8"))
    from world.hidden_zones import registry
    hidden = {k.lower().replace(" ", "_").replace("'", "") for k in registry()}
    # a node of skill S fits a zone of levels lo-hi when (lo-15)*5 <= S <= hi*5 (tools/retable_gathering_nodes.py,
    # held by qa_node_levels), so a wood only joins a table it fits
    sys.path.insert(0, str(ROOT / "tools"))
    import retable_gathering_nodes as R
    _m, levels, sk, _kind, _high, zone_key = R.load()
    sk = dict(sk, **{m: v[0][0] for m, v in RETIER.items()})     # judged at the new skill
    added = 0
    for zone, z in pools["zones"].items():
        table = z.get("table") or {}
        if zone in hidden:
            continue                                  # hidden places keep their own tables
        for new, beside in GROWS_WITH.items():
            if beside in table and new not in table:
                table[new] = WEIGHT
                if R.unfit({zone: {"table": {new: WEIGHT}}}, levels, sk, _kind, zone_key):
                    del table[new]
                    continue
                added += 1
            elif new in table and R.unfit({zone: {"table": {new: WEIGHT}}}, levels, sk, _kind, zone_key):
                del table[new]
                added -= 1
    print(f"  {changed} materials re-tiered, {added} zone table changes (added, or taken out where too high)")
    if write and (changed or added):
        MATS.write_text(json.dumps(mats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        POOLS.write_text(json.dumps(pools, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("  written")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    sys.exit(main())
