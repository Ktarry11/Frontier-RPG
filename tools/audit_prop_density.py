#!/usr/bin/env python3
"""Measure prop density LOCALLY - per screen-sized window - across every zone.

Kyle, 2026-10-31: "demon wastes in ashenvale is crowded full of stuff. sometimes
less is more. we should drop down overall props slightly when we can across the
world."

TWO EARLIER VERSIONS OF THIS TOOL WERE WRONG, both in the same way: they
inferred "prop" from the collision layer, where a cave's WALL is the tile id
"rock" and a zone's shape is indistinguishable from its clutter. One of them
reported Orgrimmar and Durotar at 0.0% props; the other reported a set of caves
at 87% because it was measuring the cave.

The honest record is zone.landmarks. Every prop placed by the handbuilt engines
goes through Tilemap.add_landmark with a real footprint (x, y, w, h), because
that is how the renderer draws it. Terrain does not. So a landmark IS a prop, by
construction, and no guessing is involved.

AND IT IS MEASURED LOCALLY. A zone average is the wrong number: Demon Wastes is
one corner of Ashenvale East, and a zone can sit at a comfortable average while
one quarter of it is impassable with scenery. This walks a window roughly the
size of what is on screen and reports the worst windows, because "crowded" is
something you experience standing in one spot, not an average over 200x200
tiles.

Coverage = landmark footprint area inside the window / the window's open tiles.
It can exceed 100%: props overlap, and that is itself a sign of a jammed area.
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

WIN_W, WIN_H = 24, 18     # about one screen of tiles
STEP = 12                 # overlapping windows, so a hotspot cannot fall between two
CROWDED = 0.30            # a third of the ground in view is something to walk around


def windows(zone):
    for wy in range(0, max(1, zone.height - WIN_H + 1), STEP):
        for wx in range(0, max(1, zone.width - WIN_W + 1), STEP):
            yield wx, wy


def measure(zone):
    """-> (worst_coverage, worst_xy, mean_coverage, n_crowded, n_windows)

    Coverage = tiles you must walk AROUND / open ground in view.

    The measured thing is collision tiles whose id is exactly "landmark", which
    Tilemap.add_landmark writes for a prop's solid footprint and nothing else
    writes at all. Terrain keeps its own ids (cliff, rock, wall, water), so this
    separates clutter from the shape of the zone without any guessing - which is
    what the first two versions of this tool got wrong in both directions.

    It also correctly discounts the forest. A tree is a landmark with a big
    canopy, but add_landmark is called with solid=False and only its TRUNK tiles
    are blockers, because the crown draws over the player's head. Measuring the
    canopy footprint instead reported Ashenvale at 3598% and Stranglethorn at
    4698%, which is a true statement about leaves and a useless one about
    crowding. What Kyle means by "crowded full of stuff" is what you have to
    path around, and that is this.
    """
    results = []
    for wx, wy in windows(zone):
        x1, y1 = min(wx + WIN_W, zone.width), min(wy + WIN_H, zone.height)
        open_tiles = props = 0
        for y in range(wy, y1):
            row = zone.collision_layer[y]
            for x in range(wx, x1):
                c = row[x]
                if c is None:
                    open_tiles += 1
                elif c == "landmark":
                    props += 1
                    open_tiles += 1
        if open_tiles < 40:        # nearly all cliff or water; tells us nothing
            continue
        results.append((props / open_tiles, wx, wy))

    if not results:
        return None
    results.sort(reverse=True)
    worst = results[0]
    mean = sum(r[0] for r in results) / len(results)
    return (worst[0], (worst[1], worst[2]), mean,
            sum(1 for r in results if r[0] >= CROWDED), len(results))


def main():
    from world.zone_generator import create_all_zones
    zones = create_all_zones()

    rows = []
    for name, z in zones.items():
        if not hasattr(z, "collision_layer"):
            continue
        m = measure(z)
        if m is None:
            continue
        worst, at, mean, ncrowd, nwin = m
        rows.append((ncrowd, worst, name, at, mean, nwin))

    rows.sort(reverse=True)
    print(f"  window {WIN_W}x{WIN_H} tiles (about one screen), step {STEP}, "
          f"crowded >= {CROWDED*100:.0f}% of open ground blocked by props\n")
    print(f"  {'crowded':>7} {'/win':>5}  {'worst':>7}  {'mean':>6}  zone (worst window)")
    for ncrowd, worst, name, at, mean, nwin in rows[:30]:
        flag = "   <-- THIN THIS" if ncrowd else ""
        print(f"  {ncrowd:7d} {nwin:5d}  {worst*100:6.0f}%  {mean*100:5.0f}%  "
              f"{name} @{at}{flag}")

    tot = sum(r[0] for r in rows)
    print(f"\n  {tot} crowded windows across {len(rows)} zones; "
          f"{sum(1 for r in rows if r[0])} zones have at least one")
    return 0


if __name__ == "__main__":
    sys.exit(main())
