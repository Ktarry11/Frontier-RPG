"""
Measure the two claims The Mother Vein's archetype makes.

    PYTHONPATH=. python3 tools/verify_mother_vein.py

The docstring in tools/handbuilt_mother_vein.py says the map is a SEAM: narrow galleries that
branch and rejoin, swelling into wide vugs. Both halves of that are measurable, and a claim about
a map that is only ever stated is a claim that quietly stops being true the first time somebody
moves a node.

CLAIM 1 - IT ANASTOMOSES. Every gallery between two vugs is doubled, so severing any single one of
them leaves the heart reachable. Fourteen galleries, fourteen severings.

    AND THE NEGATIVE CONTROL IS PART OF THE TEST. "Blocking one branch leaves the heart reachable"
    is satisfied trivially by a map where the branches are not load-bearing at all - if some third
    route exists, every severing passes and the test has measured nothing. So for each segment this
    also blocks BOTH branches and requires that the heart becomes UNREACHABLE. If it does not, the
    pair is not a pair, and the cycle it is supposed to prove is somewhere else.

    This is the lesson the Abyssal Sands taught the expensive way: a check whose negative control
    was never run turned out to have been skipping its own assertion, and reported the zone fine
    while the only descent into it was broken.

CLAIM 2 - THE GALLERIES ARE CRACKS AND THE VUGS ARE ROOMS. Measured as clearance: for every
walkable tile, the distance to the nearest wall. Gallery tiles and vug tiles are separated by
whether they are near a node, and the two distributions have to be clearly apart - a seam whose
galleries are as wide as its chambers is a cave with lumps in it.
"""
import os
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import numpy as np  # noqa: E402
from scipy import ndimage as ndi  # noqa: E402

import tools.handbuilt_mother_vein as M  # noqa: E402

HEART = None

#: how far from a node counts as "in the vug rather than in the gallery"
NODE_RADIUS = 11


def _reach(zone, start):
    seen = {start}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if (0 <= n[0] < M.W and 0 <= n[1] < M.H and n not in seen
                    and zone.is_walkable(*n)):
                seen.add(n)
                q.append(n)
    return seen


def _heart_reachable(omit):
    """Build the REAL map with those galleries not carved, and ask whether the heart is reachable.

    No reimplementation of Builder.corridor anywhere in this file. The first version of this test
    reconstructed which tiles each gallery occupied and blocked those - a second implementation of
    the same walk, which landed on slightly different tiles, left slivers of the real gallery open,
    and let every negative control pass straight through them.
    """
    zone, _L = M.build_mother_vein(omit=omit)
    # No dress, no finish: this is a topology question, and finish() checks the REAL map's packs,
    # which are not in a geometry-only build. Props only ever close routes, and the real build's
    # own finish() already proves every pack, boss and chest reachable with them in place.
    return HEART in _reach(zone, (M.PORTAL[0], M.PORTAL[1] - 2))


def main():
    global HEART
    zone, L = M.build_mother_vein()
    M.dress(zone, L)
    M.finish(zone, L)
    start = (M.PORTAL[0], M.PORTAL[1] - 2)
    heart = M.BOSSES["The Thirst"]
    HEART = heart

    base = _reach(zone, start)
    assert heart in base, "the heart is not reachable even with nothing blocked"
    print(f"walkable {sum(1 for y in range(M.H) for x in range(M.W) if zone.is_walkable(x, y))}, "
          f"reachable {len(base)}, heart at {heart}")

    # ---------- CLAIM 1: branch and rejoin ----------
    paths = M.gallery_paths()
    by_seg = {}
    for (i, bow, _pts) in paths:
        by_seg.setdefault(i, []).append(bow)

    severed_ok, control_ok, bad = 0, 0, []
    for i, bows in sorted(by_seg.items()):
        assert len(bows) == 2, f"segment {i} has {len(bows)} galleries, not a pair"
        for bow in bows:
            if _heart_reachable({(i, bow)}):
                severed_ok += 1
            else:
                bad.append(f"segment {i} gallery {bow:+d}: removing it cuts the heart off - it is "
                           f"the only route, so the seam does not rejoin there")
        if not _heart_reachable({(i, bows[0]), (i, bows[1])}):
            control_ok += 1
        else:
            bad.append(f"segment {i} NEGATIVE CONTROL FAILED: removing BOTH galleries still leaves "
                       f"the heart reachable, so some third route carries this segment and the two "
                       f"single-gallery passes above proved nothing about it")

    print(f"removed one gallery at a time: {severed_ok}/{len(paths)} kept the heart reachable")
    print(f"negative control (both): {control_ok}/{len(by_seg)} correctly cut it off")

    # ---------- CLAIM 2: cracks between rooms ----------
    walk = np.zeros((M.H, M.W), bool)
    for y in range(M.H):
        for x in range(M.W):
            walk[y, x] = zone.is_walkable(x, y)
    clear = ndi.distance_transform_edt(walk)

    near_node = np.zeros((M.H, M.W), bool)
    ys, xs = np.mgrid[0:M.H, 0:M.W]
    for (nx, ny) in M.NODES[1:]:
        near_node |= (np.hypot(xs - nx, ys - ny) <= NODE_RADIUS)
    dig = np.zeros((M.H, M.W), bool)
    dig[128:, :] = True                       # the dig head is cut by goblins, not by rock

    gal = walk & ~near_node & ~dig
    vug = walk & near_node
    g_med, v_med = float(np.median(clear[gal])), float(np.median(clear[vug]))
    print(f"clearance: galleries median {g_med:.2f} (n={int(gal.sum())}), "
          f"vugs median {v_med:.2f} (n={int(vug.sum())})")
    if v_med < g_med * 1.6:
        bad.append(f"the vugs are not meaningfully wider than the galleries "
                   f"({v_med:.2f} vs {g_med:.2f}) - this is a cave with lumps in it, not a seam")

    if bad:
        print("\nFAILED:")
        for line in bad:
            print("  - " + line)
        raise SystemExit(1)
    print("\nThe Mother Vein is a seam: it branches, it rejoins, and its galleries are cracks.")


if __name__ == "__main__":
    main()
