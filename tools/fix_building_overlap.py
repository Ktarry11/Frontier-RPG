#!/usr/bin/env python3
"""Suggest anchor moves that pull overlapping buildings apart.

    PYTHONPATH=. python3 tools/fix_building_overlap.py [zone ...]

Kyle, 7 Nov: "If you want to fix the building overlap, go for it. I don't
imagine that'd be hard."

It is not hard, but it is fiddly in exactly the way that invites doing it by
eye and getting it wrong - the anchors live in hand-written module source, the
sprites are eight to fourteen tiles tall, and moving one building to clear a
neighbour can push it into a third. So this does the arithmetic and prints the
edits; a person still applies them, because the modules carry comments about
WHY a building sits where it does and a script would trample them.

HOW IT PICKS A MOVE. For each overlapping pair it moves the SMALLER building -
the big one is usually the landmark the district is built around - along
whichever axis needs the least travel, far enough to clear plus a tile of
margin. It then checks the new anchor is walkable and is not inside a road or a
portal tile, and it re-checks every other building in the zone so a fix cannot
create a worse overlap than it solved. Pairs it cannot solve are reported as
such rather than guessed at.
"""
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from qa_building_overlap import _rect, _overlap, MAX_COVERED  # noqa: E402


def _area(r):
    return (r[2] - r[0]) * (r[3] - r[1])


def _try_moves(a, b):
    """Candidate (dx, dy) that clear b out of a, cheapest first."""
    ra, rb = _rect(a), _rect(b)
    out = []
    # push right / left / down / up, just past the overlap plus a tile
    out.append((int(ra[2] - rb[0]) + 1, 0))
    out.append((-(int(rb[2] - ra[0]) + 1), 0))
    out.append((0, int(ra[3] - rb[1]) + 1))
    out.append((0, -(int(rb[3] - ra[1]) + 1)))
    return sorted(out, key=lambda d: abs(d[0]) + abs(d[1]))


def main():
    from world.zone_generator import create_all_zones

    want = set(sys.argv[1:])
    zones = create_all_zones()
    for name, z in zones.items():
        if want and name not in want:
            continue
        blds = [lm for lm in (getattr(z, "landmarks", []) or [])
                if "assets/buildings/" in str(lm.get("sprite_key", ""))]
        pairs = []
        for i in range(len(blds)):
            for j in range(i + 1, len(blds)):
                if _overlap(_rect(blds[i]), _rect(blds[j])) > MAX_COVERED:
                    pairs.append((blds[i], blds[j]))
        if not pairs:
            continue
        print(f"\n{name}: {len(pairs)} overlapping pair(s)")
        for a, b in pairs:
            # move the smaller one
            if _area(_rect(a)) < _area(_rect(b)):
                a, b = b, a
            an, bn = Path(str(a["sprite_key"])).stem, Path(str(b["sprite_key"])).stem
            bx, by = b["anchor_x"], b["anchor_y"]
            fixed = None
            for dx, dy in _try_moves(a, b):
                nx, ny = bx + dx, by + dy
                if not (0 <= nx < z.width and 0 <= ny < z.height) or not z.is_walkable(nx, ny):
                    continue
                if z.get_tile(nx, ny, "interaction"):
                    continue
                moved = dict(b, anchor_x=nx, anchor_y=ny)
                if any(_overlap(_rect(moved), _rect(o)) > MAX_COVERED
                       for o in blds if o is not b):
                    continue
                fixed = (nx, ny)
                break
            if fixed:
                print(f"   move {bn} ({bx},{by}) -> ({fixed[0]},{fixed[1]})   [clears {an}]")
            else:
                print(f"   NO CLEAN MOVE for {bn} ({bx},{by}) against {an} - needs a human")
    return 0


if __name__ == "__main__":
    sys.exit(main())
