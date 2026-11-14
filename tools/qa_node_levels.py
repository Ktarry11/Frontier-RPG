#!/usr/bin/env python3
"""Every herb, ore and wood node fits the level of the zone it is in (backlog I [58]).

    PYTHONPATH=. python3 tools/qa_node_levels.py

The rule and the exceptions live in tools/retable_gathering_nodes.py: a node of skill S fits a
zone of levels lo-hi when (lo-15)*5 <= S <= hi*5. Excused: the Tempest Isle tables designed by
hand, rare nodes, and any material a quest sends you to gather.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))


def main():
    import retable_gathering_nodes as R
    mats, levels, skill, kind, _high, zone_key = R.load()
    pools = json.load(open(ROOT / "data/gathering/node_pools.json", encoding="utf-8"))["zones"]
    bad = R.unfit(pools, levels, skill, kind, zone_key)
    # negative control: copper in a level 40 zone must read as too low
    fake = {"the_shimmering_flats": {"table": {"ore_copper": 1}}}
    if not R.unfit(fake, levels, skill, kind, zone_key):
        print("negative control failed: copper in the Shimmering Flats reads as fitting")
        return 1
    print(f"{sum(len(p.get('table', {})) for p in pools.values())} node entries in {len(pools)} zones")
    if bad:
        for zone, mat, s, way, lv in bad[:20]:
            print(f"  - {zone} {lv}: {mat} (skill {s}) is too {way}")
        return 1
    print("\nnode levels OK - nothing in a zone is too low to be worth picking or too high to pick.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
