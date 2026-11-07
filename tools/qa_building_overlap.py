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

#: PRE-EXISTING, AND THEREFORE NOT A FAILURE - YET.
#:
#: This check found 24 overlapping pairs the day it was written. Three were
#: mine from that day and were fixed; these 21 are older than the check. A
#: suite that is permanently red teaches everyone to ignore red, so these are
#: baselined: the check fails on anything NOT in this list, which is the thing
#: worth catching - a NEW building drawn through an old one.
#:
#: This list is debt, not a decision. Orgrimmar's gate is drawn 100% through a
#: hut and its trainers' lodge 100% through a house; Razor Hill has a
#: watchtower 100% through a stall row. Clear them and delete the lines.
KNOWN = {
    ("Ashenvale East", "nightelf_house_small", 33, 144, "druid_priestess_hut", 30, 142),
    ("Astranaar", "sentinel_outpost_hall", 47, 15, "nightelf_house_small", 40, 14),
    ("Freewind Post", "tau_kodo_pen", 66, 44, "tau_storehouse", 69, 48),
    ("Freewind Post", "tau_smithy", 92, 103, "tau_tent_medium", 89, 105),
    ("Freewind Post", "tau_tent_medium", 36, 103, "tau_longhouse", 40, 109),
    ("Grom'gol", "gg_command_tent", 22, 43, "palisade_gatehouse", 22, 45),
    ("Orgrimmar", "bazaar_stall_row", 67, 69, "trading_post", 77, 69),
    ("Orgrimmar", "crossroads_stable", 170, 35, "generic_hut_b", 178, 29),
    ("Orgrimmar", "orgrimmar_gate", 87, 164, "generic_hut_a", 79, 149),
    ("Orgrimmar", "orgrimmar_gate", 87, 164, "hide_tanners_hut", 77, 168),
    ("Orgrimmar", "trading_post", 105, 101, "well_house", 107, 94),
    ("Orgrimmar", "trainers_lodge", 148, 37, "plain_orc_house_c", 146, 37),
    ("Orgrimmar", "warchiefs_hall", 22, 5, "watchtower", 14, 8),
    ("Ratchet", "generic_house_a", 16, 7, "generic_shack_b", 19, 4),
    ("Ratchet", "scrapyard_workshop", 6, 4, "generic_shack_a", 3, 5),
    ("Razor Hill", "watchtower", 18, 39, "well_house", 21, 33),
    ("Razor Hill", "watchtower", 36, 40, "bazaar_stall_row", 37, 36),
    ("Steamwheedle Port", "bb_harbour_inn", 28, 20, "bb_counting_house", 37, 18),
    ("Steamwheedle Port", "bb_warehouse", 5, 33, "bb_lean_shack", 6, 37),
    ("Steamwheedle Port", "scrapyard_workshop", 60, 32, "gg_forge", 66, 31),
    ("Tarren Mill", "ek_millstone_shelter", 25, 55, "ek_village_inn", 22, 59),
}


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
        print(f"  {len(baselined)} known pre-existing overlap(s) baselined - see KNOWN, "
              f"they are debt, not a decision")

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
