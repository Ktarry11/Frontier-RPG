"""
Shared plumbing for the hand-built Ashenvale towns (Astranaar, Splintertree Post, Zoram Strand).

Same idea as tools/town_kit.py (Barrens towns) but the landforms are Ashenvale's: a forest CLEARING cut out of dense
woods (the woods are the walls), streams / ponds / moon pools / sea, plank decks, and a paved plaza.  A town module
(tools/handbuilt_<town>.py) is config + dress():

    KEY NAME DESC REGION W H BAKED_DIR PORTALS ARRIVALS START NPC_POSITIONS
    ROADS (name -> (pts, width))   CLEARINGS [(cx, cy, rx, ry)]   GAPS   ROCKS   POOLS / STREAMS / sea()   DECKS
    PLAZA / PAVED_PATCHES / MOON_POOLS / EXTRA_PATCHES (painter hints)      dress(L)

and finishes with `AK.install(sys.modules[__name__])`, which defines fields / tile_kind / road_dist / paved / SPEC /
build_layout / generate_<key> on the module.  The painting (tools/bake_ashenvale_towns.py) reads the SAME fields.
"""
import os
import random

import numpy as np

from tools import handbuilt_central_barrens as CB
from tools import town_kit as K
from tools.handbuilt_central_barrens import _wob
from world.tilemap import Tilemap

AP = "assets/tiles/ashenvale/props/"
XP = "assets/tiles/ashenvale_corruption/props/"
GP = "assets/tiles/goblin_shared/props/"

_DIRS = [AP, XP, GP, "assets/tiles/barrens/props/", "assets/tiles/dungeon_props/", "assets/tiles/coastal_props/",
         "assets/buildings/"]
INDEX = {}
for _d in _DIRS:
    if os.path.isdir(_d):
        for _f in os.listdir(_d):
            if _f.endswith(".png"):
                INDEX.setdefault(_f[:-4], _d)        # first directory wins (Ashenvale first)


# ------------------------------------------------------------------------------------------ landform fields
def _ell(gx, gy, cx, cy, rx, ry):
    r = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
    return (1 - r) * min(rx, ry)


def install(M):
    """Attach the field functions and builders to town module M (called at the bottom of every town module)."""
    rs = K.RoadSet(M.ROADS)
    M.road_dist = rs.dist
    streams = K.RoadSet(getattr(M, "STREAMS", {})) if getattr(M, "STREAMS", None) else None

    def paved(gx, gy):
        out = np.full(np.shape(gx), -99.0)
        if getattr(M, "PLAZA", None):
            out = np.maximum(out, _ell(gx, gy, *M.PLAZA))
        for b in getattr(M, "PAVED_PATCHES", []):
            out = np.maximum(out, _ell(gx, gy, b[0], b[1], b[2], b[3]))
        return out
    M.paved = paved

    def deck_field(gx, gy):
        best = np.full(np.shape(gx), -9.0)
        for (x0, x1, y0, y1) in getattr(M, "DECKS", []):
            e = np.minimum(np.minimum(gx - x0, x1 - gx), np.minimum(gy - y0, y1 - gy))
            best = np.maximum(best, e)
        return best

    def fields(gx, gy):
        gx = np.asarray(gx, float)
        gy = np.asarray(gy, float)
        deck = deck_field(gx, gy)
        # ---- clearing = union of ellipses; everything else is dense woods (impassable canopy)
        clear = np.full(gx.shape, -99.0)
        for (cx, cy, rx, ry) in M.CLEARINGS:
            clear = np.maximum(clear, _ell(gx, gy, cx, cy, rx, ry))
        clear = clear + 1.1 * _wob(gx, gy)
        for (cx, cy, rx, ry) in getattr(M, "GAPS", []):
            clear = np.maximum(clear, _ell(gx, gy, cx, cy, rx, ry))
        clear = np.maximum(clear, M.road_dist(gx, gy) + 2.6)
        clear = np.maximum(clear, deck + 1.5)
        woods = -clear
        # ---- rock knuckles (optional) that never block a road or a deck
        rock = np.full(gx.shape, -99.0)
        for (cx, cy, rx, ry) in getattr(M, "ROCKS", []):
            rock = np.maximum(rock, _ell(gx, gy, cx, cy, rx, ry))
        rock = np.minimum(rock + 0.8 * _wob(gx, gy), -np.maximum(M.road_dist(gx, gy) + 2.2, deck + 1.5))
        # ---- water: ponds, streams, sea
        sh = np.full(gx.shape, -99.0)
        dp = np.full(gx.shape, -99.0)
        for (cx, cy, rx, ry, shrink) in getattr(M, "POOLS", []):
            f = _ell(gx, gy, cx, cy, rx, ry)
            sh = np.maximum(sh, f)
            dp = np.maximum(dp, f - shrink)
        if streams is not None:
            f = streams.dist(gx, gy)
            sh = np.maximum(sh, f)
            dp = np.maximum(dp, f - getattr(M, "STREAM_SHRINK", 1.0))
        if getattr(M, "sea", None):
            s = M.sea(gx, gy)
            sh = np.maximum(sh, s)
            dp = np.maximum(dp, s - getattr(M, "SEA_DEEP", 3.6))
        return dict(cliff=rock, woods=woods, shallow=sh, deep=dp, deck=deck)
    M.fields = fields

    def tile_kind(gx, gy):
        f = fields(gx, gy)
        g = dict(f)
        g["cliff"] = np.maximum(f["cliff"], f["woods"])
        return K.kind_from_fields(g, np.shape(gx))
    M.tile_kind = tile_kind

    class _Spec:                         # the baker (tools/bake_ashenvale.build_scores) reads M.SPEC.fields / .fords
        fords = []

    _Spec.fields = staticmethod(fields)
    M.SPEC = _Spec

    if not hasattr(M, "plaza_field") and getattr(M, "PLAZA", None):
        M.plaza_field = lambda P, wp: P.blob(M.PLAZA[0], M.PLAZA[1], M.PLAZA[2], M.PLAZA[3], 0.45, wp)
    if not hasattr(M, "BLUEBELL_PATCHES"):
        M.BLUEBELL_PATCHES = []

    import sys
    mod = sys.modules[M.__name__]

    def build_layout():
        return build(mod)
    M.build_layout = build_layout

    def generate():
        L = build_layout()
        K.register_baked(L.zone, mod)
        return L.zone
    setattr(M, f"generate_{M.KEY}", generate)


# ------------------------------------------------------------------------------------------ layout / placement
class AshTown(K.TownLayout):
    """TownLayout + prop helpers that find the right asset folder by name."""

    def _dir(self, name):
        if name not in INDEX:
            raise FileNotFoundError(name)
        return INDEX[name]

    def p(self, name, cx, by, h, **kw):
        """Solid-core prop (nudged to the nearest free spot, else logged in L.skipped)."""
        kw["path_dir"] = self._dir(name)
        return self.prop(name, cx, by, h, **kw)

    def b(self, name, cx, by, h, **kw):
        kw.setdefault("fraction", 0.5)
        return self.p(name, cx, by, h, **kw)

    def f(self, name, cx, by, h, **kw):
        """Flat / walk-through decor: no collision."""
        kw.setdefault("solid", False)
        return self.p(name, cx, by, h, **kw)

    def v(self, name, cx, by, h):
        """Purely visual sprite, no checks at all (lanterns over a road, dock furniture over planks)."""
        path = f"{self._dir(name)}{name}.png"
        wt = max(1, round(h * CB._aspect(path)))
        self.z.add_landmark(path, cx - wt // 2, by - h + 1, wt, h, solid=False)

    def edge_canopy(self, seed, names=(("large_canopy_tree", 12), ("medium_canopy_tree", 10), ("canopy_tree_cluster", 11)),
                    spacing=3.3, lo=0.9, hi=7.0, prob=0.62):
        """Visual treeline: canopy sprites over the woods just outside the clearing (the painted woods are the wall)."""
        rnd = random.Random(seed)
        M = self.M
        ys, xs = np.mgrid[0:M.H, 0:M.W]
        F = M.fields(xs + 0.5, ys + 0.5)
        w, wet = F["woods"], F["shallow"]
        n = 0
        y = 0.5
        while y < M.H + 4:
            x = 0.5
            while x < M.W + 2:
                ix, iy = int(x + rnd.uniform(-1.3, 1.3)), int(y + rnd.uniform(-1.3, 1.3))
                if (0 <= ix < M.W and 0 <= iy < M.H and lo < w[iy, ix] < hi and wet[iy, ix] < -0.6
                        and rnd.random() < prob):
                    name, h = names[rnd.randrange(len(names))]
                    if any(abs(ix - px) <= 1 and abs(iy - py) <= 1 for px, py in self.portal_tiles + self.arrival_tiles):
                        x += spacing
                        continue
                    self.v(name, ix, iy, h)
                    n += 1
                x += spacing
            y += spacing
        self.canopy = n


def build(M):
    L = AshTown(M)
    K.build_terrain(L)
    K.place_portals(L)
    M.dress(L)
    K.seal_unreachable(L, M.START)
    for (x, y) in getattr(M, "CHESTS", []):
        L.chest(x, y)
    return L


def report(L):
    """Reachability of every portal / arrival / NPC / chest / forge from START."""
    import collections
    M, z = L.M, L.z
    seen = {M.START}
    q = collections.deque([M.START])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < M.W and 0 <= n[1] < M.H and n not in seen and z.is_walkable(*n):
                seen.add(n)
                q.append(n)
    pts = {}
    pts.update({f"portal{p}": p for p in M.PORTALS})
    pts.update({f"arrival{p}": p for p in M.ARRIVALS})
    pts.update(M.NPC_POSITIONS)
    pts.update({f"chest{c}": c for c in L.chests})
    for k, v in getattr(M, "RECRUITS", {}).items():
        pts[k] = v
    if getattr(M, "FORGE", None):
        pts["forge"] = M.FORGE
    bad = {k: v for k, v in pts.items() if tuple(v) not in seen}
    return len(seen), bad


def preview(L, path, scale=8):
    """Quick structural picture: water / woods / roads / props (red = solid core) / NPCs / portals."""
    from PIL import Image, ImageDraw
    M, z = L.M, L.z
    img = np.zeros((M.H, M.W, 3), np.uint8)
    for y in range(M.H):
        for x in range(M.W):
            b = z.base_layer[y][x]
            c = (96, 130, 70)
            if b == "shallow_water":
                c = (110, 190, 210)
            elif b == "deep_water":
                c = (40, 90, 150)
            elif b == "path":
                c = (190, 170, 120)
            if z.collision_layer[y][x] == "cliff":
                c = (30, 60, 35)
            elif z.collision_layer[y][x] == "landmark":
                c = (200, 70, 60)
            img[y, x] = c
    im = Image.fromarray(img).resize((M.W * scale, M.H * scale), Image.NEAREST)
    d = ImageDraw.Draw(im)
    for lm in z.landmarks:
        d.rectangle([lm["anchor_x"] * scale, lm["anchor_y"] * scale,
                     (lm["anchor_x"] + lm["width_tiles"]) * scale, (lm["anchor_y"] + lm["height_tiles"]) * scale],
                    outline=(255, 255, 255))
    for k, (x, y) in M.NPC_POSITIONS.items():
        d.ellipse([x * scale, y * scale, (x + 1) * scale, (y + 1) * scale], fill=(255, 255, 0))
    for (x, y) in M.PORTALS:
        d.ellipse([x * scale, y * scale, (x + 1) * scale, (y + 1) * scale], fill=(255, 0, 255))
    im.save(path)
