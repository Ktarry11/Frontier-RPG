"""
You do not arrive facing a prop.

Kyle, 12 Nov: "imagine opening a door and the wall is RIGHT there." Three places he named:
entering the Drowned Barrow (its own gate stood three tiles in front of you), entering
Wrackline Hold (a rock island in the mouth of the entry nook), and stepping off the zeppelin
in Grom'gol (the watchtower's foot, then a totem pole, on the road below the stair).

For each, from the tile the game actually sets the player down on, the way they naturally
walk must be clear for at least six tiles.

Only these three are pinned: which way is "ahead" has to be judged per door, and the rest are
listed in the backlog to be done by eye.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: (source zone, exit tile in it, destination, heading as (dx, dy), what was in the way)
CASES = [
    ("Arathi East", (34, 38), "The Drowned Barrow", (0, -1), "the barrow's own gate"),
    ("Arathi East", (150, 60), "Wrackline Hold", (0, -1), "a rock island"),
    ("Grom'gol Zeppelin Tower", None, "Grom'gol", (0, 1), "the watchtower and a totem pole"),
]
NEED = 6


def main():
    from world.zone_manager import ZoneManager
    zm = ZoneManager()
    links = zm.portal_manager._links
    bad = []
    for src, tile, dest, (ux, uy), what in CASES:
        table = links.get(src, {})
        hit = [(k, v) for k, v in table.items() if v[0] == dest and (tile is None or k == tile)]
        if not hit:
            bad.append(f"rig: no link from {src} to {dest}")
            continue
        (_k, (_d, ax, ay)) = hit[0]
        zm.transition_to_zone(src, _k[0], _k[1], via_portal=False)
        zm.transition_to_zone(dest, ax, ay)          # the real arrival, nudges and all
        t = zm.current_zone
        x, y = zm.player_x, zm.player_y
        clear = 0
        cx, cy = x + ux, y + uy
        while clear < NEED and 0 <= cx < t.width and 0 <= cy < t.height and t.is_walkable(cx, cy):
            clear += 1
            cx += ux
            cy += uy
        if clear < NEED:
            blocker = t.collision_layer[cy][cx] if (0 <= cx < t.width and 0 <= cy < t.height) else "the map edge"
            bad.append(f"{dest}: arriving at ({x},{y}), only {clear} clear tile(s) ahead before "
                       f"{blocker} (it used to be {what})")
        else:
            print(f"  ok   {dest}: arrive at ({x},{y}), {clear}+ tiles clear ahead")
    if bad:
        print(f"FAIL {len(bad)}:")
        for b in bad:
            print("  ", b)
        return 1
    print("arrivals OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
