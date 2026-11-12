"""
A boat floats.

Kyle, 10 Nov: "can we stop putting boats on dry land (this is in 'south shore')" - a
full-rigged ship stood on the sand four tiles above the tideline. Arathi East had an orc boat
parked on top of its own jetty, and Booty Bay's and Tempest Shallows' sat across their piers.

The cause is in the layout kit: prop() refuses deep water and DROPS the sprite silently, so
the only place a ship could ever be put was the beach. Vessels go down with deco() instead.

Every INTACT vessel on every map (not wrecks, hulls, beached canoes or ship's fittings, which
belong on shore) must have at least half of its waterline - the bottom row of its sprite - on
water tiles.
"""
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

VESSEL = re.compile(r"^(boat_(human|orc|troll)|ash_orc_skiff|bloodsail_galleon)")


def main():
    from world.zone_manager import ZoneManager
    zm = ZoneManager()
    seen, bad = 0, []
    for zone, entry in zm.zones.items():
        t = entry["tilemap"]
        for lm in getattr(t, "landmarks", []) or []:
            name = os.path.basename(lm["sprite_key"]).lower()
            if not VESSEL.match(name):
                continue
            seen += 1
            y = lm["anchor_y"] + lm["height_tiles"] - 1
            row = [(x, y) for x in range(lm["anchor_x"], lm["anchor_x"] + lm["width_tiles"])]
            wet = sum(1 for (x, yy) in row if 0 <= x < t.width and 0 <= yy < t.height
                      and "water" in str(t.get_tile(x, yy, "base")))
            if wet * 2 < len(row):
                bad.append(f"{zone}: {name} at ({lm['anchor_x']},{lm['anchor_y']}) has "
                           f"{wet} of {len(row)} waterline tiles on water")
    if seen < 8:
        print(f"FAIL only {seen} vessels found - the rig is not seeing them (a vessel placed "
              f"with prop() on deep water is dropped without a word)")
        return 1
    print(f"{seen} intact vessels")
    if bad:
        print(f"FAIL {len(bad)}:")
        for b in bad:
            print("  ", b)
        return 1
    print("boats OK - every one is on the water.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
