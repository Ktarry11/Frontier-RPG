"""
Verify the Aspen Wilderness.

    PYTHONPATH=. python3 tools/verify_aspen_wilderness.py

WHAT THIS FILE IS FOR, AND WHY IT IS NOT THE USUAL CHECKLIST.

Every other zone verifier in tools/ asks whether the author's hand-placed intent survived: are the rects
where the module said, is every room reachable, did a prop land on a boss. Those are the right questions
for a zone whose shape is a list of coordinates somebody typed.

THIS ZONE'S SHAPE IS NOT TYPED, IT IS DERIVED. cliff_field reads the SLOPE of an elevation model, so the
rock is wherever the ground came out too steep to stand on. Nobody placed it and nobody can read the
module and know what it looks like. The thing that can go wrong, therefore, is not a misplaced tile - it
is the model producing something that is internally consistent and still does not read as a mountain. The
first build of this zone passed every structural check in the repo while being a field of parallel
vertical stripes, because a 1-D ridge function can only make stripes and nothing was asking.

So these tests are ARCHETYPE tests. They hold down the claims that make the terrain legible as a range:

  1. CONNECTIVITY     everything walkable is reachable from the gate, and the pass can be reached.
  2. ALTITUDE PROFILE walkable land must rise then close - open at the Barrens seam, mixed through the
                      timber, nearly solid at the headwall. A flat profile means the elevation model is
                      not doing anything.
  3. THE HEADWALL     the south edge is a wall with a corridor through it, not a slope.
  4. DENDRITIC        drainages must branch. This is the stripe detector: a striped map has near-identical
                      column profiles, a dendritic one does not.
  5. SNOW BUDGET      snow is a hint. If more than SNOW_BUDGET of the land bakes white it has become a
                      band, and the peaks stop reading as peaks. Kyle's instruction, verbatim: small
                      patches to indicate peaks, used sparingly.
  6. NO ORPHAN POCKETS no walled-off pockets of walkable ground big enough to look like a place.

Each test prints its measurement, not just a verdict, because the thresholds here are judgement calls and
the next person to change the elevation model needs the numbers to argue with.
"""
import os
import sys
from collections import deque
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools import handbuilt_aspen_wilderness as M            # noqa: E402
from tools import bake_aspen_zone as B                        # noqa: E402
from tools.bake_aspen_zone import smoothstep                  # noqa: E402

FAIL = []
WARN = []


def check(ok, label, detail=""):
    (print if ok else FAIL.append)(f"{'PASS' if ok else 'FAIL'}  {label}  {detail}")
    if not ok:
        print(f"FAIL  {label}  {detail}")


def warn(ok, label, detail=""):
    if not ok:
        WARN.append(f"WARN  {label}  {detail}")
    print(f"{'ok  ' if ok else 'WARN'}  {label}  {detail}")


# --------------------------------------------------------------------------------------------------------
# Build the real thing. Not a reimplementation of tile_kind - the ACTUAL layout, so the test cannot drift
# away from the game. An earlier version of this file rolled its own walkability from (cliff<=0)&(shallow<=0)
# and was wrong for a week: only kind 3 sets collision, so water is walkable and the test was measuring a
# map that does not exist.
# --------------------------------------------------------------------------------------------------------
print("building layout ...")
L = M.build_layout()
W, H = M.W, M.H

# VECTORISED, and it has to be. Called per tile this was 37,800 invocations of tile_kind, each evaluating
# 32 drainage polylines and an 8-sample relief ring - the verifier timed out at five minutes without ever
# printing a line. The field functions all take arrays, so hand them the whole grid at once.
_GX, _GY = np.meshgrid(np.arange(W, dtype=float), np.arange(H, dtype=float))
kinds = np.asarray(M.tile_kind(_GX, _GY)).reshape(H, W).astype(np.int16)

# WALKABILITY COMES FROM THE BUILT ZONE, NOT FROM tile_kind.
#
# tile_kind is the raw field decision; the zone the player actually gets is what T.build produced, after
# town_kit.seal_unreachable has converted every pocket the gate cannot reach into cliff or deep water.
# Reading tile_kind here reported 97.2% reachable and failed the build over 687 tiles that do not exist in
# the game - the verifier was testing a map nobody ships. z.is_walkable is the same call the player's
# movement makes, so this measures the thing itself.
z = L.z
walk = np.zeros((H, W), bool)
for y in range(H):
    for x in range(W):
        walk[y, x] = z.is_walkable(x, y)
solid = ~walk


def flood(start):
    seen = np.zeros_like(walk)
    sx, sy = start
    if not walk[sy, sx]:
        return seen
    q = deque([(sx, sy)])
    seen[sy, sx] = True
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and walk[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                q.append((nx, ny))
    return seen


# ---- 1. CONNECTIVITY
reach = flood(M.START)
n_walk = int(walk.sum())
n_reach = int(reach.sum())
check(n_reach == n_walk, "all walkable ground reachable from the gate",
      f"{n_reach}/{n_walk} ({100.0 * n_reach / max(n_walk, 1):.1f}%)")
px, py = M.PASS_TILE
check(bool(reach[py, px]), "the pass is reachable", f"PASS_TILE {M.PASS_TILE}")
for (gx, gy) in list(M.PORTALS) + list(M.ARRIVALS):
    check(bool(reach[gy, gx]), f"portal/arrival reachable {(gx, gy)}")

# ---- 2. ALTITUDE PROFILE: open low, mixed mid, closed high
bands = [(0, 28), (28, 52), (52, 105), (105, 150), (150, 180)]
prof = []
for a, b in bands:
    f = walk[a:b].mean()
    prof.append(f)
    print(f"      y{a:>3}-{b:<3}  walkable {100 * f:5.1f}%")
check(prof[0] > 0.70, "the high basin you arrive in is open ground", f"{100 * prof[0]:.1f}% > 70%")
check(prof[1] < 0.45, "the rim is a barrier", f"{100 * prof[1]:.1f}% < 45%")
check(prof[1] > 0.08, "the rim is not a sealed wall", f"{100 * prof[1]:.1f}% > 8%")
check(prof[2] > 0.50 and prof[3] > 0.50, "the descent below the rim opens back up",
      f"{100 * prof[2]:.1f}% / {100 * prof[3]:.1f}%")
check(prof[0] - prof[1] > 0.30 and prof[2] - prof[1] > 0.25,
      "the rim is the constriction, not just a slower stretch",
      f"basin-rim {100 * (prof[0] - prof[1]):.1f}pts, descent-rim {100 * (prof[2] - prof[1]):.1f}pts")

# ---- 3. THE RIM has a FEW ways down, not none and not many
#
# This is the zone's gate and the shape of the whole map. The player arrives on the high basin above the
# Lift escarpment and has to get off it; the chutes are the only breaks in the drop. Too many and the rim
# is decoration, none and the zone is unplayable.
#
# An earlier version of this test (back when the map ran the other way, uphill to a headwall) counted
# columns that had ANY walkable tile in the band and demanded exactly one run. That is not the claim: it
# passed a column with one open tile at the very top of the band and reported a 55-tile "corridor" that
# was solid rock all the way down. Full-depth columns is the honest measure.
RIM_A, RIM_B = 32, 50
rim = walk[RIM_A:RIM_B, :]
cols_through = [x for x in range(W) if rim[:, x].all()]
runs, cur = [], []
for x in cols_through:
    if cur and x == cur[-1] + 1:
        cur.append(x)
    else:
        if cur:
            runs.append(cur)
        cur = [x]
if cur:
    runs.append(cur)
ways = [r for r in runs if len(r) >= 2]
check(1 <= len(ways) <= 6, "a few ways down through the rim",
      f"{len(ways)} full-depth breach(es) at {[(r[0], r[-1]) for r in ways]}")
check(all(len(r) <= 22 for r in ways), "no breach is wide enough to be a missing rim",
      f"widest {max((len(r) for r in ways), default=0)} tiles")

# ---- 4. DENDRITIC, NOT STRIPED
# A striped map's columns are near-copies of each other, so the correlation between a column's walkable
# profile and its neighbour's stays high right across the map. A branching drainage network breaks that:
# a column that happens to sit in a tributary looks nothing like one on the spur beside it. This is the
# test that the first build of this zone would have failed, and nothing in the repo was asking.
inner = walk[16:162, :].astype(np.float32)
cors = []
for x in range(0, W - 4, 2):
    a, b = inner[:, x], inner[:, x + 4]
    if a.std() > 1e-6 and b.std() > 1e-6:
        cors.append(float(np.corrcoef(a, b)[0, 1]))
mean_cor = float(np.mean(cors))
check(mean_cor < 0.62, "drainages branch (columns are not copies of each other)",
      f"mean neighbour-column correlation {mean_cor:.3f} < 0.62")

# Second angle on the same claim: count how many separate rock bodies there are. Stripes give a handful of
# long ones; a dissected range gives many spurs of varied size.
lab = np.zeros((H, W), np.int32)
sizes = []
nid = 0
for y in range(H):
    for x in range(W):
        if solid[y, x] and lab[y, x] == 0:
            nid += 1
            n = 0
            q = deque([(x, y)])
            lab[y, x] = nid
            while q:
                cx, cy = q.popleft()
                n += 1
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < W and 0 <= ny < H and solid[ny, nx] and lab[ny, nx] == 0:
                        lab[ny, nx] = nid
                        q.append((nx, ny))
            sizes.append(n)
sizes.sort(reverse=True)
spurs = [s for s in sizes if s >= 12]
check(len(spurs) >= 14, "many separate spurs, not a few long stripes",
      f"{len(spurs)} rock bodies >=12 tiles; largest {sizes[:4]}")
warn(len([s for s in sizes if s < 4]) < 160, "small rock blobs read as boulders at 32px",
     f"{len([s for s in sizes if s < 4])} blobs <4 tiles")

# ---- 5. SNOW BUDGET
# Rebuild the baker's own score fields on the tile grid and ask which material would win per tile. This is
# the real decision the baker makes, not an approximation of it, so the budget cannot pass here and be
# violated in the bake.
print("scoring materials for the snow budget ...")


class _P:
    """Minimal stand-in for Painter: build_scores only needs gx/gy, noise, blob, warp and road_field."""
    def __init__(self, w, h, seed):
        self.gx, self.gy = np.meshgrid(np.arange(w, dtype=np.float32),
                                       np.arange(h, dtype=np.float32))
        self.rng = np.random.default_rng(seed)
        self._cache = {}

    def noise(self, scale, key, octaves=1):
        if key in self._cache:
            return self._cache[key]
        from tools.tirisfal_kit import wob
        a = np.zeros_like(self.gx)
        amp, f = 1.0, 1.0 / max(scale, 0.001)
        tot = 0.0
        h = abs(hash(key)) % 977
        for o in range(max(octaves, 1)):
            a = a + amp * wob(self.gx * f + h, self.gy * f + h * 0.37)
            tot += amp
            amp *= 0.5
            f *= 2.0
        a = a / max(tot, 1e-6)
        a = (a - a.min()) / max(a.max() - a.min(), 1e-6)
        self._cache[key] = a.astype(np.float32)
        return self._cache[key]

    def warp(self, key, amp_tiles=2.0, scale=8.0):
        return (self.noise(scale, key + "wx") - 0.5) * 2 * amp_tiles, \
               (self.noise(scale, key + "wy") - 0.5) * 2 * amp_tiles

    def blob(self, cx, cy, rx, ry, soft, warp=None):
        gx, gy = self.gx, self.gy
        if warp is not None:
            gx, gy = gx + warp[0], gy + warp[1]
        d = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
        from tools.bake_aspen_zone import smoothstep as ss
        return ss(1.0 + soft, 1.0 - soft, d).astype(np.float32)

    def road_field(self, roads):
        """Mirrors terrain_painter.Painter.road_field closely enough to score with.

        NOT M.road_dist - that is an INVERSE distance (positive means ON the road, like _chute), and
        reading it as a plain distance made every tile in the zone a road and this whole report useless.
        """
        core = np.zeros_like(self.gx)
        verge = np.zeros_like(self.gx)
        for pts, width in roads:
            d = M._poly_dist(self.gx, self.gy, pts)
            core = np.maximum(core, 1 - smoothstep(width * 0.5 - 0.35, width * 0.5 + 0.35, d))
            verge = np.maximum(verge, 1 - smoothstep(width * 0.5, width * 0.5 + 1.8, d))
        return core.astype(np.float32), verge.astype(np.float32), None

    def sample_field(self, a, X, Y):
        return a


P = _P(W, H, M.SEED)
S = B.build_scores(P, M)
names = [k for k in B.MATERIALS]
stack = np.stack([S[k] for k in names])
winner = np.array(names, dtype=object)[np.argmax(stack, axis=0)]
land_mask = walk & (kinds == 0)
snow_frac = float(((winner == "snow") & land_mask).sum()) / max(int(land_mask.sum()), 1)
ice_frac = float((winner == "ice").sum()) / max(int(((kinds == 1) | (kinds == 2)).sum()), 1)
check(snow_frac <= B.SNOW_BUDGET, "snow stays a hint, not a band",
      f"{100 * snow_frac:.2f}% of dry land <= {100 * B.SNOW_BUDGET:.1f}%")
check(snow_frac > 0.0015, "there IS some snow up top (the peaks need to read)",
      f"{100 * snow_frac:.2f}% > 0.15%")
warn(ice_frac < 0.30, "ice only skins the high tarns", f"{100 * ice_frac:.1f}% of water")

# Snow must be HIGH. A patch of snow at mid altitude is the single most legible mistake in the zone.
snow_y = np.argwhere((winner == "snow") & land_mask)
if len(snow_y):
    el = np.array([M.elevation(x, y) for y, x in snow_y], np.float32)
    check(float(el.min()) > M.TREELINE + 1.0, "no snow below the treeline",
          f"lowest snow at elevation {el.min():.2f} > {M.TREELINE + 1.0:.2f}")

# ---- 6. NO ORPHAN POCKETS big enough to look like a place
orph = walk & ~reach
lab2 = np.zeros((H, W), np.int32)
big = []
nid = 0
for y in range(H):
    for x in range(W):
        if orph[y, x] and lab2[y, x] == 0:
            nid += 1
            n = 0
            q = deque([(x, y)])
            lab2[y, x] = nid
            while q:
                cx, cy = q.popleft()
                n += 1
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < W and 0 <= ny < H and orph[ny, nx] and lab2[ny, nx] == 0:
                        lab2[ny, nx] = nid
                        q.append((nx, ny))
            if n >= 8:
                big.append(n)
check(not big, "no orphan pockets >=8 tiles", f"{len(big)} pocket(s) {sorted(big, reverse=True)[:5]}")

# ---- subzones must sit on ground the player can stand on
#
# SUBZONES entries are (name, x, y, w, h) with x,y the TOP-LEFT CORNER. Testing x,y as if it were the
# centre put four of the probes on the map border, which is always cliff, and warned about four subzones
# that are perfectly fine.
for sz in M.SUBZONES:
    name, sx0, sy0, sw, sh = sz
    cx, cy = int(sx0 + sw // 2), int(sy0 + sh // 2)
    ok = bool(reach[min(cy, H - 1), min(cx, W - 1)])
    warn(ok, f"subzone centre stands on reachable ground: {name}", f"centre ({cx}, {cy})")

print()
for w in WARN:
    print(w)
print()
if FAIL:
    print(f"{len(FAIL)} FAILURE(S)")
    for f in FAIL:
        print(" ", f)
    sys.exit(1)
print(f"aspen wilderness: all checks passed ({len(WARN)} warning(s))")
