#!/usr/bin/env python3
"""Buildings must not be drawn through each other.

    PYTHONPATH=. python3 tools/qa_building_overlap.py [zone ...]

Kyle, 7 Nov: "And don't overlap houses."

WHY ANCHOR DISTANCE DOES NOT ANSWER THIS. The obvious check - are two buildings
within N tiles of each other - is the one I ran first, and it reported Saltspur
Landing clean while the screenshot plainly showed a smokehouse drawn through a
longhouse. Anchors were five tiles apart; the sprites are nine and eleven tiles
tall. A building is not its anchor, it is a rectangle standing on it, and only
the rectangles can say whether two of them collide.

So this uses the footprint the zone actually stores - width_tiles, height_tiles -
and treats a sprite as anchored at bottom-centre, which is how the renderer
draws it.

TOLERANCE. Buildings in a town are MEANT to crowd; a terrace is not a bug. What
is a bug is one roof drawn over another, so the test is on how much of the
SMALLER building is covered. Up to a third is a close-packed street. Past that
you are looking at one building through another.

Props are excluded - a crate against a wall or a banner on a doorpost is
deliberate, and so is a tree at the edge of a roof. Only sprites from
assets/buildings/ are checked.
"""
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: Fraction of the smaller building that may be covered before it is a failure.
MAX_COVERED = 0.34

#: Empty, and that is the point.
#:
#: This started as 21 baselined pairs - overlaps older than the check, kept out
#: of the failure count so the suite would not ship permanently red. Kyle, 7
#: Nov: "If you want to fix the building overlap, go for it. I don't imagine
#: that'd be hard." It was not hard, it was fiddly, and all 21 are fixed, so
#: the list is empty and the check is now simply: no building is drawn through
#: another, anywhere.
#:
#: If something has to go in here again, it is debt with a date on it, not a
#: decision.
KNOWN = set()


def _rect(lm):
    """(x0, y0, x1, y1) in tiles. Anchored bottom-centre, as drawn."""
    w = float(lm.get("width_tiles") or 0)
    h = float(lm.get("height_tiles") or 0)
    ax = float(lm.get("anchor_x", 0))
    ay = float(lm.get("anchor_y", 0))
    return (ax - w / 2.0, ay - h, ax + w / 2.0, ay)


def _overlap(a, b):
    ox = min(a[2], b[2]) - max(a[0], b[0])
    oy = min(a[3], b[3]) - max(a[1], b[1])
    if ox <= 0 or oy <= 0:
        return 0.0
    area = ox * oy
    sa = (a[2] - a[0]) * (a[3] - a[1])
    sb = (b[2] - b[0]) * (b[3] - b[1])
    smaller = min(sa, sb)
    return area / smaller if smaller > 0 else 0.0


def main():
    from world.zone_generator import create_all_zones

    want = set(sys.argv[1:])
    zones = create_all_zones()
    findings = defaultdict(list)
    baselined = []
    checked = 0

    for name, z in zones.items():
        if want and name not in want:
            continue
        blds = [lm for lm in (getattr(z, "landmarks", []) or [])
                if "assets/buildings/" in str(lm.get("sprite_key", ""))]
        checked += len(blds)
        for i in range(len(blds)):
            for j in range(i + 1, len(blds)):
                frac = _overlap(_rect(blds[i]), _rect(blds[j]))
                if frac <= MAX_COVERED:
                    continue
                a, b = blds[i], blds[j]
                key = (name, Path(str(a["sprite_key"])).stem, a["anchor_x"], a["anchor_y"],
                       Path(str(b["sprite_key"])).stem, b["anchor_x"], b["anchor_y"])
                if key in KNOWN:
                    baselined.append(key)
                    continue
                findings[name].append((frac, a, b))

    print(f"  {checked} buildings across {len(zones) if not want else len(want)} zones, "
          f"tolerance {MAX_COVERED:.0%} of the smaller one")
    if baselined:
        print(f"  {len(baselined)} baselined overlap(s) - see KNOWN, debt with a date on it")

    if findings:
        total = sum(len(v) for v in findings.values())
        print(f"\n  {total} overlapping pair(s):\n")
        for name in sorted(findings, key=lambda n: -len(findings[n])):
            print(f"    {name}")
            for frac, a, b in sorted(findings[name], key=lambda t: -t[0])[:8]:
                an = Path(str(a["sprite_key"])).stem
                bn = Path(str(b["sprite_key"])).stem
                print(f"      {frac:5.0%}  {an} ({a['anchor_x']},{a['anchor_y']})"
                      f"  through  {bn} ({b['anchor_x']},{b['anchor_y']})")
            if len(findings[name]) > 8:
                print(f"      ... and {len(findings[name]) - 8} more")
        print("\nFAIL")
        return 1

    print("\n  no NEW building is drawn through another")
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
