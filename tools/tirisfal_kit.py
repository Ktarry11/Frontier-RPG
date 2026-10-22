"""
Shared plumbing for the hand-built Tirisfal zones (Western Tirisfal, Eastern Tirisfal, Brill).

Same idea as tools/town_kit.py (which it builds on): each zone module (tools/handbuilt_<zone>.py) is a CONFIG + analytic
landform fields, and this kit does the grid, portals, subzones, NPC tiles, forest scatter, pocket-sealing, chests, shape
preview and baked-chunk registration.  tools/bake_tirisfal.py paints from the SAME fields so collision and painting cannot drift.

Zone module contract
  KEY NAME DESC REGION W H BAKED_DIR PORTALS(dict tile->dest) ARRIVALS START ROADS(dict name->(pts,width))
  fields(gx,gy) -> dict(cliff, shallow, deep, deck)      (cliff>0 rock; shallow>0 water; deep>0 deep water; tile units)
  road_dist(gx,gy)      NPC_POSITIONS      SUBZONES [(name,x,y,w,h[,display])]      CHESTS
  dress(L)              hand-placed props/buildings
  FOREST = dict(seed, count, rim, names=[(prop, height, fraction)], thorn)         (optional)
  IS_TOWN (default False here)   BASE_TILE (default "grass")
  baker config: BASE / PAINT / PAVED_BLOBS / WATER_TINT (read by tools/bake_tirisfal.py)
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from tools import town_kit as K

BLD = "assets/buildings/"
EKP = "assets/tiles/eastern_kingdoms/props/"
HFP = "assets/tiles/haunted_forest/props/"
CIP = "assets/tiles/cursed_isle/props/"
UFP = "assets/tiles/undead_farmland/props/"
UCP = "assets/tiles/undercity/props/"
GP = "assets/tiles/goblin_shared/props/"
ENT = "assets/tiles/cave_entrances/"


def wob(gx, gy):
    return (0.45 * np.sin(0.37 * gx + 1.3) * np.sin(0.29 * gy + 0.7)
            + 0.30 * np.sin(0.83 * gx + 0.21 * gy + 2.0)
            + 0.25 * np.sin(0.19 * gx - 0.57 * gy + 4.1))


def lobe(gx, gy, cx, cy, rx, ry, rot=0.0):
    """Positive inside, ~tile distance from the rim (scaled by the smaller radius)."""
    dx, dy = gx - cx, gy - cy
    if rot:
        import math
        c, s = math.cos(rot), math.sin(rot)
        dx, dy = c * dx + s * dy, -s * dx + c * dy
    return (1.0 - np.sqrt((dx / rx) ** 2 + (dy / ry) ** 2)) * min(rx, ry)


def superlobe(gx, gy, cx, cy, rx, ry, p=3.0):
    s = (np.abs(gx - cx) / rx) ** p + (np.abs(gy - cy) / ry) ** p
    return (1.0 - s ** (1.0 / p)) * min(rx, ry)


def seg_dist(gx, gy, x0, y0, x1, y1):
    vx, vy = x1 - x0, y1 - y0
    t = np.clip(((gx - x0) * vx + (gy - y0) * vy) / (vx * vx + vy * vy), 0.0, 1.0)
    return np.hypot(gx - (x0 + t * vx), gy - (y0 + t * vy))


def water_body(gx, gy, cx, cy, rx, ry, rot=0.0, k=0.7):
    """Tile-distance inside a wobbly pond/lake (>0 inside)."""
    return lobe(gx, gy, cx, cy, rx, ry, rot) + k * wob(gx * 1.3, gy * 1.3)


def rock_spurs(gx, gy, spurs, outcrops, k=1.2):
    """>0 inside rock: thick segments reaching in from the rim + free-standing stacks."""
    rock = np.full(np.shape(gx), -99.0)
    for (x0, y0, x1, y1, t) in spurs:
        rock = np.maximum(rock, (t - seg_dist(gx, gy, x0, y0, x1, y1)) * k + 0.25 * wob(gx * 1.7, gy * 1.7))
    for (cx, cy, rx, ry) in outcrops:
        rock = np.maximum(rock, (1.0 - np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)) * 3.0 - 0.2)
    return rock


class OutdoorLayout(K.TownLayout):
    """TownLayout with Tirisfal prop defaults (eastern_kingdoms props; a path with '/' is taken as is)."""

    def prop(self, name, cx, base_y, height, **kw):
        if "/" in name:
            kw["path_dir"] = ""
        else:
            kw.setdefault("path_dir", EKP)
        kw.setdefault("nudge", 2)
        return super().prop(name, cx, base_y, height, **kw)

    def cave(self, cx, cy, sprite, w=7, h=5):
        super().cave(cx, cy, sprite, w, h)


def add_subzones(L):
    for sz in getattr(L.M, "SUBZONES", []):
        name, x, y, w, h = sz[:5]
        if len(sz) > 5 and sz[5]:
            L.z.add_subzone(name, x, y, w, h, display_name=sz[5])
        else:
            L.z.add_subzone(name, x, y, w, h)


def forest(L):
    """Dead timber and thorn, seeded: dense along the rock rim, sparse towards the paths."""
    M = L.M
    cfg = getattr(M, "FOREST", None)
    if not cfg:
        return
    rng = np.random.default_rng(cfg.get("seed", 11))
    ys, xs = np.mgrid[0:M.H, 0:M.W]
    f = M.fields(xs + 0.5, ys + 0.5)
    floor = (f["cliff"] <= 0) & (f["shallow"] <= 0)
    d_rock = ndi.distance_transform_edt(f["cliff"] <= 0)
    names = cfg["names"]
    rim = cfg.get("rim", 9)
    count, tries, n = cfg.get("count", 60), 0, 0
    while n < count and tries < 8000:
        tries += 1
        x, y = int(rng.integers(3, M.W - 3)), int(rng.integers(3, M.H - 3))
        if not floor[y, x] or d_rock[y, x] > rim:
            continue
        if d_rock[y, x] > rim * 0.55 and rng.random() < 0.8:
            continue
        nm, hh, fr = names[int(rng.integers(0, len(names)))]
        if L.prop(nm, x, y, hh, fraction=fr, nudge=0):
            n += 1
    for _ in range(cfg.get("thorn", 14)):
        x, y = int(rng.integers(4, M.W - 4)), int(rng.integers(4, M.H - 4))
        if floor[y, x]:
            L.prop("ek_thorn_bush", x, y, 2, solid=False, nudge=0)


def grove(L, cx, cy, rx, ry, n, names, seed=1, **kw):
    """A hand-aimed clump of trees/props inside an ellipse (seeded)."""
    rng = np.random.default_rng(seed)
    placed = 0
    for _ in range(n * 12):
        if placed >= n:
            break
        a, r = rng.random() * 6.283, np.sqrt(rng.random())
        x, y = int(cx + np.cos(a) * rx * r), int(cy + np.sin(a) * ry * r)
        nm, hh, fr = names[int(rng.integers(0, len(names)))]
        if L.prop(nm, x, y, hh, fraction=fr, nudge=0, **kw):
            placed += 1
    return placed


def build(M):
    L = OutdoorLayout(M)
    K.build_terrain(L)
    K.place_portals(L)
    add_subzones(L)
    for (x, y) in M.NPC_POSITIONS.values():
        if L.z.is_walkable(x, y):
            L.z.set_tile(x, y, "npc", "interaction")
    M.dress(L)
    forest(L)
    K.seal_unreachable(L, M.START)
    for (x, y) in getattr(M, "CHESTS", []):
        L.chest(x, y)
    return L


def shape_preview(M, path, scale=8):
    ys, xs = np.mgrid[0:M.H, 0:M.W]
    f = M.fields(xs + 0.5, ys + 0.5)
    img = np.zeros((M.H, M.W, 3), np.uint8)
    img[:] = (120, 130, 70)
    img[f["cliff"] > 0] = (70, 60, 55)
    rd = M.road_dist(xs + 0.5, ys + 0.5)
    img[(rd > 0) & (f["cliff"] <= 0)] = (200, 180, 120)
    if hasattr(M, "paved"):
        img[(M.paved(xs + 0.5, ys + 0.5) > 0) & (f["cliff"] <= 0)] = (170, 165, 150)
    img[(f["shallow"] > 0) & (f["cliff"] <= 0)] = (60, 110, 120)
    img[(f["deep"] > 0) & (f["cliff"] <= 0)] = (20, 50, 70)
    img[(f.get("deck", np.full(f["cliff"].shape, -9.0)) > 0)] = (150, 110, 60)
    for sz in getattr(M, "SUBZONES", []):
        x, y, w, h = sz[1:5]
        for xx in range(x, min(x + w, M.W)):
            for yy in (y, min(y + h, M.H) - 1):
                img[yy, xx] = (img[yy, xx] * 0.6 + np.array([200, 80, 80]) * 0.4).astype(np.uint8)
        for yy in range(y, min(y + h, M.H)):
            for xx in (x, min(x + w, M.W) - 1):
                img[yy, xx] = (img[yy, xx] * 0.6 + np.array([200, 80, 80]) * 0.4).astype(np.uint8)
    for (x, y) in M.PORTALS:
        img[max(0, y - 1):y + 2, max(0, x - 1):x + 2] = (255, 0, 255)
    for (x, y) in M.NPC_POSITIONS.values():
        img[y, x] = (30, 200, 255)
    Image.fromarray(img).resize((M.W * scale, M.H * scale), Image.NEAREST).save(path)


def register_baked(zone, M):
    K.register_baked(zone, M)


def generate(M):
    L = build(M)
    K.register_baked(L.zone, M)
    return L.zone


def build_layout(M):
    return build(M)
