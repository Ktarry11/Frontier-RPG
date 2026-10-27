"""
Verify Tarren Mill's layout, and in particular the one claim the whole town rests on: THE RACE IS A BARRIER.

    PYTHONPATH=. python3 tools/verify_tarren_mill.py

The archetype is "two banks joined by three bridges and nothing else". That is a claim a map can pass by
accident - it renders correctly whether or not the water actually divides anything - so it is tested by its
NEGATIVE: fill the three bridge decks in and the two banks must fall into separate components. Azurelode shipped
with decorative water that looked right and divided nothing, and Durnholde's keep was never sealed; both passed
"it renders" and failed "block it and re-run the flood fill". This is that flood fill, kept.

Checks:
  1. every hand-placed building and prop was placed (the forest scatter is allowed to skip - it retries by design)
  2. portal, arrival and start are walkable, and none of them is in the water
  3. every NPC spot, chest and the portal is reachable from START
  4. WITH the bridges, both banks are one component
  5. WITHOUT the bridges, they are not - and each bridge on its own restores the join
"""
import collections
import os
import sys

import numpy as np

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((64, 64))

import tools.handbuilt_tarren_mill as TM  # noqa: E402

WEST_PROBE = (24, 52)        # the smithy's door, west bank
EAST_PROBE = (68, 56)        # the apothecary's yard, east bank


def flood(z, start, blocked=frozenset()):
    seen = {start}
    q = collections.deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if (0 <= n[0] < z.width and 0 <= n[1] < z.height
                    and n not in seen and n not in blocked and z.is_walkable(*n)):
                seen.add(n)
                q.append(n)
    return seen


def bridge_tiles(which=None):
    """Walkable tiles belonging to bridge `which` (or all of them)."""
    out = set()
    ys, xs = np.mgrid[0:TM.H, 0:TM.W]
    gx, gy = xs + 0.5, ys + 0.5
    for i, (x0, x1, y0, y1) in enumerate(TM.BRIDGES):
        if which is not None and i != which:
            continue
        inside = np.minimum(np.minimum(gx - x0, x1 - gx), np.minimum(gy - y0, y1 - gy))
        for (y, x) in zip(*np.where(inside > 0)):
            out.add((int(x), int(y)))
    return out


def main():
    L = TM.build_layout()
    z = L.zone
    fails = []

    # ---- 1. placement
    scatter = {"ek_pine_trio", "ek_pine_tall", "ek_willow", "ek_thorn_bush"}
    hand_skips = [s for s in L.skipped if s[0] not in scatter]
    print(f"props placed {L.placed}, sealed pockets {L.sealed}, hand-placed skips {len(hand_skips)}")
    for s in hand_skips:
        fails.append(f"hand-placed prop skipped: {s}")

    # ---- 2. the doors
    portal = list(TM.PORTALS)[0]
    for label, t in (("portal", portal), ("arrival", TM.ARRIVALS[0]), ("start", TM.START)):
        if not z.is_walkable(*t):
            fails.append(f"{label} {t} is not walkable")
        if z.base_layer[t[1]][t[0]] in ("deep_water", "shallow_water"):
            fails.append(f"{label} {t} is in the water")

    # ---- 3. reachability
    reach = flood(z, TM.START)
    print(f"reachable from start: {len(reach)} tiles")
    for name, t in TM.NPC_POSITIONS.items():
        if tuple(t) not in reach:
            fails.append(f"NPC {name} at {t} unreachable")
    for c in TM.CHESTS:
        if tuple(c) not in reach:
            fails.append(f"chest {c} unreachable")
    if portal not in reach:
        fails.append(f"portal {portal} unreachable from start")

    # ---- 4/5. THE BARRIER TEST
    west_ok = WEST_PROBE in reach
    east_ok = EAST_PROBE in reach
    print(f"with bridges:    west bank {'OK' if west_ok else 'UNREACHABLE'}, "
          f"east bank {'OK' if east_ok else 'UNREACHABLE'}")
    if not (west_ok and east_ok):
        fails.append("a bank is unreachable even WITH the bridges")

    allb = bridge_tiles()
    cut = flood(z, WEST_PROBE, blocked=allb)
    print(f"bridges removed: east bank {'STILL REACHED - the race divides nothing' if EAST_PROBE in cut else 'cut off (correct)'}"
          f"  [{len(reach)} -> {len(cut)} tiles]")
    if EAST_PROBE in cut:
        fails.append("THE RACE IS DECORATION: the banks stay joined with every bridge removed")

    # each bridge alone must restore the crossing, or it is not really a crossing
    for i in range(len(TM.BRIDGES)):
        others = bridge_tiles() - bridge_tiles(i)
        solo = flood(z, WEST_PROBE, blocked=others)
        ok = EAST_PROBE in solo
        print(f"  bridge {i} alone: {'joins the banks' if ok else 'JOINS NOTHING'}")
        if not ok:
            fails.append(f"bridge {i} does not actually cross the race")

    print()
    if fails:
        print(f"FAILED ({len(fails)}):")
        for f in fails:
            print("  -", f)
        return 1
    print("all checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
