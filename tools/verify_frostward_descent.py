"""
Verify The Frostward Descent.

    PYTHONPATH=. python3 tools/verify_frostward_descent.py

The archetype is a WARREN that trends downward, which makes its test the exact inverse of Tarren Mill's. The
millrace had to prove a chokepoint EXISTS (remove the bridges, the banks must part). This map has to prove
chokepoints DO NOT exist: block any single passage and the way down must still be open. A warren with one
mandatory corridor is not a warren, it is a corridor with rooms attached, and it would read as one.

Also checks the usual: everything reachable, nothing skipped by hand, both portals walkable and out of the rock,
and that the three bands are actually stacked so the ice-to-arcane crossing cannot be skipped.
"""
import collections
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((64, 64))

import tools.handbuilt_frostward_descent as FD  # noqa: E402


def flood(z, start, blocked=frozenset()):
    seen, q = {start}, collections.deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if (0 <= n[0] < z.width and 0 <= n[1] < z.height
                    and n not in seen and n not in blocked and z.is_walkable(*n)):
                seen.add(n)
                q.append(n)
    return seen


def main():
    z, L = FD.build_frostward_descent()
    FD.dress(z, L)
    FD.finish(z, L)
    fails = []

    scatter = set()
    hand = [s for s in L.skipped if s[0] not in scatter]
    print(f"props placed {L.placed}, skipped {len(hand)}")
    for s in hand:
        fails.append(f"hand-placed prop skipped: {s}")

    for label, t in (("entrance", FD.PORTAL), ("exit", FD.EXIT)):
        if not z.is_walkable(*t):
            fails.append(f"{label} portal {t} is not walkable")

    reach = flood(z, FD.PORTAL)
    print(f"reachable from the entrance: {len(reach)} tiles")
    for n, t in FD.BOSSES.items():
        if tuple(t) not in reach:
            fails.append(f"boss {n} at {t} unreachable")
    for c in FD.CHESTS:
        if tuple(c) not in reach:
            fails.append(f"chest {c} unreachable")
    if FD.EXIT not in reach:
        fails.append("the exit is unreachable from the entrance")

    # ---- the bands really are stacked, so the crossing cannot be skipped
    for name, y0, y1 in (("ice", 100, 140), ("seam", 56, 100), ("arcane", 8, 56)):
        n = sum(1 for (x, y) in reach if y0 <= y < y1)
        print(f"  {name:7} band: {n} reachable tiles")
        if n < 300:
            fails.append(f"the {name} band is barely walkable ({n} tiles)")

    # ---- THE WARREN TEST: no single passage may be load-bearing
    print("\nblocking each passage in turn (the exit must survive every one):")
    choke = []
    for i, (pts, w) in enumerate(FD.PASSAGES):
        blocked = set()
        for (px, py) in pts:
            for dy in range(-w - 2, w + 3):
                for dx in range(-w - 2, w + 3):
                    blocked.add((px + dx, py + dy))
        if FD.EXIT not in flood(z, FD.PORTAL, blocked=blocked):
            choke.append(i)
    if choke:
        print(f"  load-bearing passages: {choke}")
        for i in choke:
            fails.append(f"passage {i} {FD.PASSAGES[i][0]} is a single point of failure")
    else:
        print(f"  none of {len(FD.PASSAGES)} passages is load-bearing - it is a warren")

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
