"""
Shared analytic-landform engine for the hand-built Ashenvale zones (West, East).

Same recipe as the Barrens zones (claude/zone_perfection_playbook.md) - the layout module owns the tile
data and the analytic fields, the baker paints from the same fields - but parameterised by a `Spec`
so West and East share one implementation, plus what a FOREST zone needs that a savanna does not:

  * WOODS   - dense impassable woodland massifs / belts / rims (collision tile "cliff", painted by the
              baker as a canopy rather than rock);  clearings are carved back out of them
  * RIVERS  - spline rivers with a wadeable bank, a deep core, and named FORDS where roads cross
  * a forest-density field + fast tree scatter (hundreds of canopy sprites, deliberate not random)

tile kinds (tile_kind):  0 land  1 shallow  2 deep  3 rock cliff  4 deck  5 woods
"""
import collections
import math
import os

import numpy as np
from scipy.spatial import cKDTree

from tools import handbuilt_central_barrens as CB
from tools.handbuilt_central_barrens import blob, _wob, _smooth, _gauss
from world.tilemap import Tilemap

AP = "assets/tiles/ashenvale/props/"
XP = "assets/tiles/ashenvale_corruption/props/"


def _ell(gx, gy, cx, cy, rx, ry, rot=0.0):
    dx, dy = gx - cx, gy - cy
    if rot:
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        dx, dy = c * dx + s * dy, -s * dx + c * dy
    r = np.sqrt((dx / rx) ** 2 + (dy / ry) ** 2)
    return (1 - r) * min(rx, ry)


class Spec:
    """All the plan data for one zone + the field functions derived from it."""

    def __init__(self, name, W, H, roads, rivers=(), lakes=None, deep_shrink=None, islets=(), sea=None,
                 mesas=(), ridges=(), woods=(), belts=(), clearings=(), rim=None, gaps=(), decks=(),
                 fords=(), rock_rim=None, road_corridor=3.2, woods_corridor=3.4, thicket=None):
        self.name, self.W, self.H = name, W, H
        self.roads = roads                  # name -> (pts, width)
        self.rivers = list(rivers)          # (pts, hw_shallow, hw_deep)
        self.lakes = lakes or {}            # key -> [(cx,cy,rx,ry,rot,ph)]
        self.deep_shrink = deep_shrink or {}
        self.islets = list(islets)
        self.sea = sea                      # fn(gx, gy) -> extent (>0 = sea)
        self.mesas = list(mesas)            # rock (cx,cy,rx,ry,rot)
        self.ridges = list(ridges)          # rock (pts, hw)
        self.woods = list(woods)            # (cx,cy,rx,ry,rot,ph)
        self.belts = list(belts)            # (pts, hw)
        self.clearings = list(clearings)    # (cx,cy,rx,ry)
        self.rim = rim or {}                # edge -> woods rim thickness
        self.rock_rim = rock_rim or {}      # edge -> rock rim thickness
        self.gaps = list(gaps)              # ("ell", cx, cy, rx, ry)
        self.decks = list(decks)
        self.fords = list(fords)            # (x, y, r): river deep core suppressed near these
        self.thicket = thicket               # (threshold, amp, phase) dense organic thickets from low-frequency noise
        self.road_corridor = road_corridor
        self.woods_corridor = woods_corridor
        self._rt, self._rv, self._bt, self._rg = {}, {}, {}, {}
        self._ford_xy = np.array([[f[0], f[1]] for f in self.fords]) if self.fords else None

    # ------------------------------------------------------------- roads
    def _road_tree(self, n):
        if n not in self._rt:
            from tools.terrain_painter import Painter
            pts, w = self.roads[n]
            self._rt[n] = (cKDTree(Painter.spline(pts)), w)
        return self._rt[n]

    def road_dist(self, gx, gy, names=None):
        q = np.stack([np.ravel(gx), np.ravel(gy)], 1)
        best = None
        for n in (names or self.roads):
            tree, w = self._road_tree(n)
            d, _ = tree.query(q)
            e = (w * 0.5) - d
            best = e if best is None else np.maximum(best, e)
        return best.reshape(np.shape(gx))

    # ------------------------------------------------------------- water
    def _river_tree(self, i):
        if i not in self._rv:
            from tools.terrain_painter import Painter
            self._rv[i] = cKDTree(Painter.spline(self.rivers[i][0]))
        return self._rv[i]

    def water_fields(self, gx, gy):
        gx = np.asarray(gx, float)
        gy = np.asarray(gy, float)
        sh = np.full(gx.shape, -99.0)
        dp = np.full(gx.shape, -99.0)
        if self.sea is not None:
            s = self.sea(gx, gy)
            sh, dp = s, s - 3.4
        q = np.stack([gx.ravel(), gy.ravel()], 1)
        for i, (pts, hws, hwd) in enumerate(self.rivers):
            tree = self._river_tree(i)
            d, idx = tree.query(q)
            t = idx / max(1, tree.n - 1)
            taper = 0.45 + 0.55 * np.clip(t * 6.0, 0, 1)          # source is a trickle, widens downstream
            wob = 0.5 * _wob(gx.ravel(), gy.ravel())
            s = hws * taper + wob - d
            dd = hwd * taper + wob - d
            if self._ford_xy is not None:
                near = np.zeros(q.shape[0])
                for k, (fx, fy, fr) in enumerate(self.fords):
                    near = np.maximum(near, np.clip(1 - np.hypot(q[:, 0] - fx, q[:, 1] - fy) / fr, 0, 1))
                dd = dd - 9.0 * near
            sh = np.maximum(sh, s.reshape(gx.shape))
            dp = np.maximum(dp, dd.reshape(gx.shape))
        for key, shapes in self.lakes.items():
            for (cx, cy, rx, ry, rot, ph) in shapes:
                s = blob(gx, gy, cx, cy, rx, ry, rot, ph)
                sh = np.maximum(sh, s)
                dp = np.maximum(dp, s - self.deep_shrink.get(key, 3.0))
        for (cx, cy, rx, ry, rot, ph) in self.islets:
            isl = blob(gx, gy, cx, cy, rx, ry, rot, ph)
            sh = np.minimum(sh, -isl)
            dp = np.minimum(dp, -isl)
        return sh, dp

    def deck_field(self, gx, gy):
        best = np.full(np.shape(gx), -9.0)
        for (x0, x1, y0, y1) in self.decks:
            e = np.minimum(np.minimum(gx - x0, x1 - gx), np.minimum(gy - y0, y1 - gy))
            best = np.maximum(best, e)
        return best

    # ------------------------------------------------------------- gaps
    def gap_extent(self, gx, gy, corridor=None):
        best = np.full(np.shape(gx), -99.0)
        for g in self.gaps:
            _, cx, cy, rx, ry = g
            d = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
            best = np.maximum(best, (1 - d) * min(rx, ry))
        best = np.maximum(best, self.road_dist(gx, gy) + (corridor or self.road_corridor))
        best = np.maximum(best, self.deck_field(gx, gy) + 1.5)
        return best

    # ------------------------------------------------------------- rock
    def _ridge(self, key, pts, hw, gx, gy, store):
        if key not in store:
            from tools.terrain_painter import Painter
            store[key] = cKDTree(Painter.spline(pts))
        tree = store[key]
        d, idx = tree.query(np.stack([gx.ravel(), gy.ravel()], 1))
        t = idx / max(1, tree.n - 1)
        taper = 0.30 + 0.70 * np.sin(np.pi * t) ** 0.6
        return (hw * taper).reshape(gx.shape) + 0.7 * _wob(gx, gy) - d.reshape(gx.shape)

    def _edge(self, edge, gx, gy, base, amp_a=2.4, amp_b=1.2):
        """Wavy rim along one edge; extent > 0 inside the rim (tiles)."""
        W, H = self.W, self.H
        if edge == "west":
            return (base + 3.0 * np.sin(0.05 * gy + 0.9) + 1.5 * np.sin(0.13 * gy + 1.0) + 0.8 * np.sin(0.37 * gy)) - gx
        if edge == "east":
            return gx - (W - base - 3.0 * np.sin(0.06 * gy + 0.3) - 1.4 * np.sin(0.17 * gy + 1.0) - 0.7 * np.sin(0.41 * gy))
        if edge == "north":
            return (base + amp_a * np.sin(0.05 * gx + 1.0) + amp_b * np.sin(0.11 * gx) + 0.7 * np.sin(0.31 * gx + 1.0)) - gy
        return gy - (H - base - amp_a * np.sin(0.06 * gx + 2.0) - 1.0 * np.sin(0.13 * gx) - 0.7 * np.sin(0.29 * gx + 2.0))

    def cliff_raw(self, gx, gy):
        gx = np.asarray(gx, float)
        gy = np.asarray(gy, float)
        out = np.full(gx.shape, -99.0)
        for (cx, cy, rx, ry, rot) in self.mesas:
            out = np.maximum(out, _ell(gx, gy, cx, cy, rx, ry, rot))
        for i, (rpts, rhw) in enumerate(self.ridges):
            out = np.maximum(out, self._ridge(("r", i), rpts, rhw, gx, gy, self._rg))
        for edge, base in (self.rock_rim or {}).items():
            out = np.maximum(out, self._edge(edge, gx, gy, base))
        return out + 1.1 * _wob(gx, gy)

    # ------------------------------------------------------------- woods
    def woods_raw(self, gx, gy):
        gx = np.asarray(gx, float)
        gy = np.asarray(gy, float)
        out = np.full(gx.shape, -99.0)
        for (cx, cy, rx, ry, rot, ph) in self.woods:
            out = np.maximum(out, blob(gx, gy, cx, cy, rx, ry, rot, ph, wob=0.16))
        for i, (bpts, bhw) in enumerate(self.belts):
            out = np.maximum(out, self._ridge(("b", i), bpts, bhw, gx, gy, self._bt))
        for edge, base in self.rim.items():
            if base:
                out = np.maximum(out, self._edge(edge, gx, gy, base))
        if self.thicket:
            thr, amp, ph = self.thicket
            n = 0.5 + 0.5 * (0.55 * np.sin(0.13 * gx + 1.7 + ph) * np.sin(0.15 * gy + 0.3)
                             + 0.30 * np.sin(0.085 * gx + 0.11 * gy + 2.2 + ph)
                             + 0.15 * np.sin(0.21 * gx - 0.07 * gy + 0.9))
            out = np.maximum(out, (n - thr) * amp)
        clear = np.full(gx.shape, -99.0)
        for (cx, cy, rx, ry) in self.clearings:
            clear = np.maximum(clear, blob(gx, gy, cx, cy, rx, ry, 0.0, 0.7, wob=0.12))
        out = np.minimum(out, -clear)
        return out + 1.3 * _wob(gx, gy)

    # ------------------------------------------------------------- combined
    def fields(self, gx, gy):
        gx = np.asarray(gx, float)
        gy = np.asarray(gy, float)
        sh, dp = self.water_fields(gx, gy)
        cl = np.minimum(self.cliff_raw(gx, gy), -self.gap_extent(gx, gy))
        wd = np.minimum(self.woods_raw(gx, gy), -self.gap_extent(gx, gy, self.woods_corridor))
        return dict(cliff=cl, woods=wd, shallow=sh, deep=dp, deck=self.deck_field(gx, gy))

    def tile_kind(self, gx, gy):
        f = self.fields(gx, gy)
        kind = np.zeros(np.shape(gx), int)
        kind[f["shallow"] > 0] = 1
        kind[f["deep"] > 0] = 2
        w = (f["woods"] > 0) & (kind == 0)
        kind[w] = 5
        kind[(f["woods"] > 1.5) & (kind != 3)] = 5
        r = (f["cliff"] > 0) & (kind == 0)
        kind[r] = 3
        kind[(f["cliff"] > 1.5)] = 3
        kind[f["deck"] > 0] = 4
        return kind

    # forest density 0..1 for walkable woodland (trees thicker near woods massifs, thin near the open)
    def density(self, gx, gy, f=None):
        f = f or self.fields(gx, gy)
        n = (0.5 + 0.5 * (0.55 * np.sin(0.071 * gx + 0.9) * np.sin(0.083 * gy + 0.4)
                          + 0.30 * np.sin(0.157 * gx + 0.063 * gy + 2.0)
                          + 0.15 * np.sin(0.043 * gx - 0.191 * gy + 4.1)))
        near_w = np.clip(1.0 - (-f["woods"]) / 18.0, 0, 1) * 0.55
        return np.clip(0.30 + 0.45 * n + near_w, 0, 1)

    # --------------------------------------------------------------- preview
    def shape_preview(self, path, scale=4, portals=(), npc=(), layout=None):
        from PIL import Image
        ys, xs = np.mgrid[0:self.H, 0:self.W]
        kind = self.tile_kind(xs + 0.5, ys + 0.5)
        pal = {0: (84, 130, 70), 1: (110, 190, 210), 2: (40, 90, 150), 3: (120, 108, 110), 4: (160, 120, 60),
               5: (24, 62, 36)}
        img = np.zeros((self.H, self.W, 3), np.uint8)
        for k, c in pal.items():
            img[kind == k] = c
        rd = self.road_dist(xs + 0.5, ys + 0.5)
        img[(rd > 0) & ((kind == 0) | (kind == 4))] = (222, 200, 140)
        for (px, py) in portals:
            img[max(py - 1, 0):py + 2, max(px - 1, 0):px + 2] = (255, 0, 255)
        big = np.array(Image.fromarray(img).resize((self.W * scale, self.H * scale), Image.NEAREST))
        if layout is not None:
            for lm in layout.z.landmarks:
                key = lm["sprite_key"]
                cx = (lm["anchor_x"] + lm["width_tiles"] / 2) * scale
                by = (lm["anchor_y"] + lm["height_tiles"] - 1) * scale
                tree = "canopy" in key
                col = (6, 30, 14) if tree else (255, 190, 40)
                r = 3 if tree else 4
                x0, y0 = int(cx) - r, int(by) - r
                big[max(0, y0):max(0, y0 + 2 * r), max(0, x0):max(0, x0 + 2 * r)] = col
            for (cx_, cy_) in getattr(layout, "chests", []):
                big[cy_ * scale:cy_ * scale + scale + 2, cx_ * scale:cx_ * scale + scale + 2] = (255, 255, 255)
        for (px, py) in npc:
            big[py * scale:py * scale + scale + 2, px * scale:px * scale + scale + 2] = (255, 255, 0)
        Image.fromarray(big).save(path)
        return kind


def make_layout_class(spec, title, desc, region, portals, arrivals, npc_positions):
    class AL(CB.Layout):
        W, H = spec.W, spec.H
        portal_tiles = list(portals)
        arrival_tiles = list(arrivals)

        def road_fn(self, gx, gy):
            return spec.road_dist(gx, gy)

        def __init__(self):
            self.zone = Tilemap(title, spec.W, spec.H, desc)
            self.z = self.zone
            self.z.region = region
            self.skipped = []
            self.chests = []
            self.placed = 0
            self.npc_xy = list(npc_positions.values())
            self.spec = spec
            self.trees = 0

        # -- fast tree placement from precomputed masks (see scatter) --
        def tree(self, name, cx, base_y, height, solid=True, fraction=0.12):
            path = f"{AP}{name}.png" if "/" not in name else name
            wt = max(1, round(height * CB._aspect(path)))
            ax, ay = cx - wt // 2, base_y - height + 1
            core = []
            if solid:
                rows = max(1, round(height * fraction))
                # trunk only: one row, ~2 tiles wide (was ~3x2) - the crown is drawn over the player, so the look is unchanged
                x0 = ax + int(wt * 0.4)
                x1 = max(ax + int(wt * 0.62), x0 + 1)
                for y in range(ay + height - rows, ay + height):
                    for x in range(x0, x1):
                        core.append((x, y))
            probe = core or [(cx, base_y)]
            m = self.free_mask
            for (x, y) in probe:
                if not (0 <= x < self.W and 0 <= y < self.H) or not m[y, x]:
                    return False
                if self.z.collision_layer[y][x] is not None:
                    return False
            self.z.add_landmark(path, ax, ay, wt, height, solid=False)
            for (x, y) in core:
                self.z.collision_layer[y][x] = "landmark"
                self.free_mask[y, x] = False
            self.trees += 1
            return True

    return AL


# --------------------------------------------------------------------------- shared build steps
def terrain(L):
    z, spec = L.z, L.spec
    z.fill("grass", "base")
    ys, xs = np.mgrid[0:spec.H, 0:spec.W]
    kind = spec.tile_kind(xs + 0.5, ys + 0.5)
    L.kind = kind
    rd = spec.road_dist(xs + 0.5, ys + 0.5)
    L.rd = rd
    for y in range(spec.H):
        for x in range(spec.W):
            k = kind[y, x]
            if k == 1:
                z.set_tile(x, y, "shallow_water", "base")
            elif k == 2:
                z.set_tile(x, y, "deep_water", "base")
            elif k in (3, 5):
                z.set_tile(x, y, "cliff", "collision")
            elif k == 4:
                z.set_tile(x, y, "path", "base")
            elif rd[y, x] > 0:
                z.set_tile(x, y, "path", "base")


def seal_unreachable(L, start):
    z, spec = L.z, L.spec
    W, H = spec.W, spec.H
    seen = {start}
    q = collections.deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < W and 0 <= n[1] < H and n not in seen and z.is_walkable(*n):
                seen.add(n)
                q.append(n)
    n_sealed = 0
    if not hasattr(L, "sealed_land"):
        L.sealed_land, L.sealed_water = [], []        # so the baker can paint sealed pockets as canopy / deep water
    for y in range(H):
        for x in range(W):
            if (x, y) not in seen and z.is_walkable(x, y):
                if z.base_layer[y][x] == "shallow_water":
                    z.set_tile(x, y, "deep_water", "base")
                    L.sealed_water.append((x, y))
                else:
                    z.set_tile(x, y, "cliff", "collision")
                    L.sealed_land.append((x, y))
                n_sealed += 1
    L.sealed = n_sealed


def place_portals(L, portals, arrivals, caves=None):
    z = L.z
    for (px, py) in portals:
        z.collision_layer[py][px] = None
        z.set_tile(px, py, "portal", "interaction")
    for (px, py) in arrivals:
        z.collision_layer[py][px] = None
    for (px, py), (spr, w, h) in (caves or {}).items():
        L.cave(px, py, spr, w, h)


def register_subzones(L, subzones):
    for key, x, y, w, h, disp in subzones:
        L.z.add_subzone(key, x, y, w, h, display_name=disp)


def build_free_mask(L, npc_xy, margin_road=2.0):
    """True where a tree trunk may stand: dry walkable land, off roads/portals/NPCs, no existing collision."""
    z, spec = L.z, L.spec
    free = np.zeros((spec.H, spec.W), bool)
    rd = L.rd
    for y in range(spec.H):
        for x in range(spec.W):
            free[y, x] = (z.is_walkable(x, y) and z.collision_layer[y][x] is None
                          and z.base_layer[y][x] not in ("deep_water", "shallow_water", "path")
                          and rd[y, x] < -margin_road and z.interaction_layer[y][x] is None)
    for (nx, ny) in list(npc_xy) + list(L.portal_tiles) + list(L.arrival_tiles):
        free[max(0, ny - 2):ny + 3, max(0, nx - 2):nx + 3] = False
    L.free_mask = free


GROVE_MIN_DENSITY = 0.55    # forest density below which no grove is seeded
GROVE_KEEP = 0.6            # chance a seed point above that becomes a grove
GROVE_SPACING = 11          # min distance between grove centres (tiles)

#: Radius^2 of the merged trunk mass drawn round each tree in a grove. Kyle,
#: 2026-10-31: "sometimes less is more. we should drop down overall props
#: slightly when we can across the world."
#:
#: This is the lever that thins WITHOUT touching the look. A grove's canopy is
#: drawn over the player's head and is not a blocker; this disc is the part you
#: have to walk around. Shrinking it takes obstruction out of the forest floor
#: while every tree stays exactly where it was and the painted woods read the
#: same. Measured per screen-sized window by tools/audit_prop_density.py - the
#: zones that were worst are all forest, and this is why.
#:
#: Was 4.6, with GROVE_SPACING 10.
GROVE_TRUNK_R2 = 3.6


def scatter_trees(L, kit, seed, spacing=4.2, scale=1.0, woods_deco=True):
    """Deliberate forest: jittered grid, density field decides where, tree size by density.
    kit = {"big": [(name,h)], "mid": [...], "small": [...]}.  Woodland trees get a trunk collision core;
    the woods massif edge gets purely visual canopy sprites so the painted woods read as real forest."""
    import random
    rnd = random.Random(seed)
    spec = L.spec
    ys, xs = np.mgrid[0:spec.H, 0:spec.W]
    f = spec.fields(xs + 0.5, ys + 0.5)
    dens = spec.density(xs + 0.5, ys + 0.5, f)
    # ---- GROVES, not lone trunks (Kyle 2026-10-22: keep the look and the big blockers, lose the dozens of tiny ones).
    # The old scatter put ~400 single trees (each its own 3x2 collision post) across the open forest.  Now trees come in
    # groves: a handful of trees around a centre whose trunks are merged into ONE solid mass you walk around, with open
    # forest floor between groves.  Lone trees are gone.
    n = 0
    centres = []
    y = 3.0
    while y < spec.H - 3:
        x = 3.0
        while x < spec.W - 3:
            jx, jy = x + rnd.uniform(-2.5, 2.5), y + rnd.uniform(-2.5, 2.5)
            ix, iy = int(jx), int(jy)
            if 0 <= ix < spec.W and 0 <= iy < spec.H and L.free_mask[iy, ix]:
                d = dens[iy, ix]
                if d >= GROVE_MIN_DENSITY and rnd.random() < d * GROVE_KEEP:
                    centres.append((ix, iy, d))
            x += spacing
        y += spacing
    placed = []
    for (cx, cy, d) in centres:
        if any(abs(cx - px) < GROVE_SPACING and abs(cy - py) < GROVE_SPACING for (px, py) in placed):
            continue
        k = rnd.randint(4, 7)
        trees = []
        for _ in range(k):
            ang, rr = rnd.uniform(0, 6.283), rnd.uniform(0.0, 3.1)
            tx, ty = int(round(cx + rr * math.cos(ang))), int(round(cy + 0.8 * rr * math.sin(ang)))
            tier = "big" if d > 0.72 else ("mid" if d > 0.45 else "small")
            pool = kit.get(tier) or kit["mid"]
            name, h = pool[rnd.randrange(len(pool))]
            if 0 <= tx < spec.W and 0 <= ty < spec.H and L.free_mask[ty, tx]:
                trees.append((tx, ty, name, int(round(h * scale))))
        if len(trees) < 3:
            continue
        placed.append((cx, cy))
        # the merged trunk mass: a disc round every tree's base, only on free ground
        for (tx, ty, name, h) in sorted(trees, key=lambda t: t[1]):
            if L.tree(name, tx, ty, h, solid=False):
                n += 1
        for (tx, ty, _n, _h) in trees:
            for yy in range(ty - 2, ty + 2):
                for xx in range(tx - 2, tx + 3):
                    if 0 <= xx < spec.W and 0 <= yy < spec.H and L.free_mask[yy, xx] \
                            and (xx - tx) ** 2 + 1.4 * (yy - ty + 0.5) ** 2 <= GROVE_TRUNK_R2 \
                            and L.z.collision_layer[yy][xx] is None:
                        L.z.collision_layer[yy][xx] = "landmark"
                        L.free_mask[yy, xx] = False
    L.scattered = n
    # visual canopy over the massif edge (no collision: the painted woods are already the obstacle)
    if woods_deco:
        m = 0
        y = 1.0
        while y < spec.H - 1:
            x = 1.0
            while x < spec.W - 1:
                jx, jy = x + rnd.uniform(-1.4, 1.4), y + rnd.uniform(-1.4, 1.4)
                ix, iy = int(jx), int(jy)
                if 0 <= ix < spec.W and 0 <= iy < spec.H:
                    w = f["woods"][iy, ix]
                    if 0.8 < w < 7.5 and L.kind[iy, ix] == 5 and rnd.random() < 0.55:
                        pool = kit.get("woods") or kit["big"]
                        name, h = pool[rnd.randrange(len(pool))]
                        # Same rule as Layout.tree(): a bare name is an Ashenvale prop, a name with a
                        # "/" in it is already a path. Stranglethorn's canopy lives in its own
                        # directory and this line used to send every one of its woods sprites to
                        # assets/tiles/ashenvale/props/ and crash.
                        path = f"{AP}{name}.png" if "/" not in name else name
                        wt = max(1, round(h * CB._aspect(path)))
                        L.z.add_landmark(path, ix - wt // 2, iy - h + 1, wt, h, solid=False)
                        m += 1
                x += 3.4
            y += 3.4
        L.woods_deco = m
    return n


def reachable_report(L, start):
    z, spec = L.z, L.spec
    seen = {start}
    q = collections.deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < spec.W and 0 <= n[1] < spec.H and n not in seen and z.is_walkable(*n):
                seen.add(n)
                q.append(n)
    walk = sum(1 for y in range(spec.H) for x in range(spec.W) if z.is_walkable(x, y))
    return len(seen), walk, seen


def register_baked(zone, baked_dir, W, H, chunk=20):
    for cy in range(0, H, chunk):
        for cx in range(0, W, chunk):
            fn = f"{baked_dir}/ground_{cx}_{cy}.jpg"
            if not os.path.exists(fn):
                raise FileNotFoundError(f"{fn} - run the zone's baker")
            w, h = min(chunk, W - cx), min(chunk, H - cy)
            zone.add_ground_chunk(fn, cx, cy, w, h)
            zone.ground_chunks[-1]["exact"] = True
            zone.add_water_chunk(fn, cx, cy, w, h)
            zone.add_obstacle_chunk(fn, cx, cy, w, h)
