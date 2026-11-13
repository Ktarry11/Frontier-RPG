#!/usr/bin/env python3
"""No high-tier material reaches a player before level 60. Ever.

    PYTHONPATH=. python3 tools/qa_tier_floor.py

Kyle, 2026-10-28: "we can have frontier stuff in there. That is 100% fine. But none of the high-tier
stuff will EVER appear before lvl 60!"

THIS ROLLS THE ACTUAL DICE RATHER THAN READING THE BANDS, because reading the bands is how the leak
got through in the first place. The bands say Moonsilk starts at 58. The filter is supposed to hold it
to 60. Which of those two is true is a question about what the code DOES, so this calls roll_cloth and
roll_leather at every level from 1 to 99 and looks at what comes out.

That is not paranoia about the filter, it is a specific bug this caught: in_reach originally returned
the unfiltered table whenever filtering emptied it, on the theory that an empty table was a mistake
worth surfacing. At level 58 every cloth band in range is high-tier and nothing else, so the
"surface the mistake" path fired on a perfectly normal level and handed out Moonsilk. A band-reading
check would have reported a pass.

Also checks the gathering node pools, which are a separate route to the same materials and would
otherwise be an open back door.
"""
import json
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from entities.cloth_drops import roll_cloth                      # noqa: E402
from entities.material_tiers import HIGH_TIER, HIGH_TIER_FLOOR   # noqa: E402
from entities.skinning_drops import roll_leather                 # noqa: E402

#: Kills per level per ladder. High enough that a weight of 1 against 5 shows up at every level.
SAMPLES = 250


class _Dummy:
    def __init__(self, name, level, template=None):
        self.name, self.level, self.template = name, level, template


def main():
    random.seed(0)
    fails = []

    for label, roll, dummy in (
        ("cloth", lambda e: roll_cloth(e), _Dummy("Galak Outrider", 1, "humanoid_warrior")),
        ("leather", lambda e: roll_leather(e), _Dummy("Plainstrider", 1)),
    ):
        for level in range(1, HIGH_TIER_FLOOR):
            dummy.level = level
            seen = set()
            for _ in range(SAMPLES):
                for mid, _qty in roll(dummy):
                    seen.add(mid)
            early = sorted(seen & HIGH_TIER)
            if early:
                fails.append(f"{label}: level {level} can drop {', '.join(early)}")

        # And confirm the ladder actually opens up at the floor, so this is a gate and not a wall.
        # (13 Nov 2026: the line is now the material's skill, 300. The first raid tier is banded in
        # the 70s, so "opens" is checked from the floor upward rather than at exactly 60.)
        opened = set()
        for level in range(HIGH_TIER_FLOOR, 100):
            dummy.level = level
            for _ in range(40):
                for mid, _qty in roll(dummy):
                    opened.add(mid)
        if not (opened & HIGH_TIER):
            fails.append(f"{label}: nothing high-tier drops at any level from {HIGH_TIER_FLOOR} up - "
                         f"the floor is a wall")

        # ...and everything BELOW the line is really reachable before 60: about 22 of each.
        from entities.material_tiers import pre60_ladder
        kind = "cloth" if "cloth" in label.lower() else "leather"
        want = {mid for mid, _s in pre60_ladder(kind)}
        got = set()
        for level in range(1, HIGH_TIER_FLOOR):
            dummy.level = level
            for _ in range(SAMPLES):
                for mid, _qty in roll(dummy):
                    got.add(mid)
        if not (20 <= len(want) <= 22):
            fails.append(f"{label}: {len(want)} materials before 60, Kyle asked for 20-22")
        if want - got:
            fails.append(f"{label}: never drops before 60: {', '.join(sorted(want - got))}")

    pools = json.loads((ROOT / "data/gathering/node_pools.json").read_text())["zones"]
    for zone, v in pools.items():
        early = sorted(set(v.get("table", {})) & HIGH_TIER)
        if early:
            fails.append(f"node pool {zone} offers {', '.join(early)}")

    print(f"== rolled {SAMPLES} kills at each of levels 1-{HIGH_TIER_FLOOR - 1}, both ladders, "
          f"plus {len(pools)} node pools")
    print(f"== {len(HIGH_TIER)} materials are above the top Classic rung and held to "
          f"level {HIGH_TIER_FLOOR}\n")
    if fails:
        print(f"FAIL ({len(fails)})")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("PASS - nothing above the Classic ladder reaches a player before 60")
    return 0


if __name__ == "__main__":
    sys.exit(main())
