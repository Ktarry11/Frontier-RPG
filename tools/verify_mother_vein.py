"""
Measure the two claims the Glittervein dungeon's archetype makes, on BOTH of its maps.

    PYTHONPATH=. python3 tools/verify_mother_vein.py

The docstring in tools/handbuilt_mother_vein.py says the map is a SEAM: narrow galleries that
branch and rejoin, swelling into wide vugs. Both halves of that are measurable, and a claim about
a map that is only ever stated is a claim that quietly stops being true the first time somebody
moves a node.

CLAIM 1 - IT ANASTOMOSES. Every gallery between two vugs is doubled, so severing any single one of
them leaves the map's far end reachable - the downshaft on the upper half, the outflow on the lower.

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

import tools.handbuilt_mother_vein as MV  # noqa: E402
import tools.handbuilt_cistern as CI  # noqa: E402
from tools import seam_kit  # noqa: E402

#: (module, build fn, start portal, far-end target name or portal, extra non-vug rooms)
#: The far end of the upper half is the DOWNSHAFT, not a boss - the claim is that you can always
#: reach the next map, and on the lower half it is the outflow, which is the way home.
MAPS = [
    ("The Mother Vein", MV, MV.build_mother_vein, lambda: MV.PORTAL, lambda: MV.DOWNSHAFT,
     [("dighead", 90, 106), ("gallery", 76, 90)]),
    ("The Cistern", CI, CI.build_cistern, lambda: CI.ENTRANCE, lambda: CI.OUTFLOW, []),
]

#: how far from a node counts as "in the vug rather than in the gallery"
NODE_RADIUS = 11


def _reach(zone, start, W, H):
    seen = {start}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if (0 <= n[0] < W and 0 <= n[1] < H and n not in seen
                    and zone.is_walkable(*n)):
                seen.add(n)
                q.append(n)
    return seen


def _far_end_reachable(mod, build, start_fn, far_fn, omit):
    """Build the REAL map with those galleries not carved, and ask whether its far end is still
    reachable from its entrance.

    No reimplementation of Builder.corridor anywhere in this file. The first version of this test
    reconstructed which tiles each gallery occupied and blocked those - a second implementation of
    the same walk, which landed on slightly different tiles, left slivers of the real gallery open,
    and let every negative control pass straight through them.

    No dress, no finish: this is a topology question, and finish() checks the REAL map's packs,
    which a geometry-only build does not have. Props only ever close routes, and each map's own
    finish() already proves every pack, boss and chest reachable with them in place.
    """
    zone, _L = build(omit=omit)
    sx, sy = start_fn()
    return far_fn() in _reach(zone, (sx, sy - 2), mod.W, mod.H)


def check(name, mod, build, start_fn, far_fn, rooms):
    bad = []
    zone, L = build()
    mod.dress(zone, L)
    mod.finish(zone, L)
    sx, sy = start_fn()
    start = (sx, sy - 2)
    base = _reach(zone, start, mod.W, mod.H)
    assert far_fn() in base, f"{name}: the far end is unreachable with nothing removed"
    print(f"\n=== {name} ({mod.W}x{mod.H}) ===")
    print(f"  walkable {sum(1 for y in range(mod.H) for x in range(mod.W) if zone.is_walkable(x, y))}"
          f", reachable {len(base)}, far end {far_fn()}")
    print(f"  chamber clearances: {seam_kit.clearances(mod.NODES, mod.VUGS, rooms=rooms)}")

    # ---------- CLAIM 1: branch and rejoin ----------
    paths = mod.gallery_paths()
    by_seg = {}
    for (i, bow, _pts) in paths:
        by_seg.setdefault(i, []).append(bow)

    severed_ok, control_ok = 0, 0
    for i, bows in sorted(by_seg.items()):
        assert len(bows) == 2, f"{name}: segment {i} has {len(bows)} galleries, not a pair"
        for bow in bows:
            if _far_end_reachable(mod, build, start_fn, far_fn, {(i, bow)}):
                severed_ok += 1
            else:
                bad.append(f"{name} segment {i} gallery {bow:+d}: removing it cuts the far end "
                           f"off - it is the only route, so the seam does not rejoin there")
        if not _far_end_reachable(mod, build, start_fn, far_fn, {(i, bows[0]), (i, bows[1])}):
            control_ok += 1
        else:
            bad.append(f"{name} segment {i} NEGATIVE CONTROL FAILED: removing BOTH galleries "
                       f"still leaves the far end reachable, so some third route carries this "
                       f"segment and the two single-gallery passes proved nothing about it")

    print(f"  removed one gallery at a time: {severed_ok}/{len(paths)} kept the far end reachable")
    print(f"  negative control (both): {control_ok}/{len(by_seg)} correctly cut it off")

    # ---------- CLAIM 2: cracks between rooms ----------
    walk = np.zeros((mod.H, mod.W), bool)
    for y in range(mod.H):
        for x in range(mod.W):
            walk[y, x] = zone.is_walkable(x, y)
    clear = ndi.distance_transform_edt(walk)

    near_node = np.zeros((mod.H, mod.W), bool)
    ys, xs = np.mgrid[0:mod.H, 0:mod.W]
    for (i, _rx, _ry) in mod.VUGS:
        nx, ny = mod.NODES[i]
        near_node |= (np.hypot(xs - nx, ys - ny) <= NODE_RADIUS)
    cut = np.zeros((mod.H, mod.W), bool)
    for (_lab, y0, y1) in rooms:              # rooms people cut, not rock
        cut[y0:y1, :] = True

    gal = walk & ~near_node & ~cut
    vug = walk & near_node
    g_med, v_med = float(np.median(clear[gal])), float(np.median(clear[vug]))
    print(f"  clearance: galleries median {g_med:.2f} (n={int(gal.sum())}), "
          f"vugs median {v_med:.2f} (n={int(vug.sum())})")
    if v_med < g_med * 1.6:
        bad.append(f"{name}: the vugs are not meaningfully wider than the galleries "
                   f"({v_med:.2f} vs {g_med:.2f}) - a cave with lumps in it, not a seam")
    return bad


def main():
    bad = []
    for (name, mod, build, start_fn, far_fn, rooms) in MAPS:
        bad += check(name, mod, build, start_fn, far_fn, rooms)
    if bad:
        print("\nFAILED:")
        for line in bad:
            print("  - " + line)
        raise SystemExit(1)
    print("\nBoth halves are a seam: they branch, they rejoin, and their galleries are cracks.")


if __name__ == "__main__":
    main()
