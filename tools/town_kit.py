"""
Shared plumbing for the hand-built Barrens towns (Crossroads, Camp Taurajo, Ratchet).

Each town module (tools/handbuilt_<town>.py) is a small CONFIG + landform fields:
    NAME DESC REGION W H PORTALS ARRIVALS NPC_POSITIONS ROADS
    road_dist(gx, gy)   fields(gx, gy) -> dict(cliff, shallow, deep, deck)   tile_kind(gx, gy)
    PAINT / BASE / WATER  (read by tools/bake_barrens_towns.py)
    dress(L)              hand-placed props
and uses this kit for the grid, sealing, portals and baked-chunk registration.  The prop placement
logic itself is the Central Barrens `Layout` (parametric), so props never overlap water/cliff/roads/NPCs.
"""
import collections
import os

import numpy as np
from scipy.spatial import cKDTree

from tools import handbuilt_central_barrens as CB
from world.tilemap import Tilemap


class RoadSet:
    def __init__(self, roads):
        self.roads = roads
        self._trees = {}

    def dist(self, gx, gy):
        from tools.terrain_painter import Painter
        q = np.stack([np.ravel(gx), np.ravel(gy)], 1)
        best = None
        for n, (pts, w) in self.roads.items():
            if n not in self._trees:
                self._trees[n] = cKDTree(Painter.spline(pts))
            d, _ = self._trees[n].query(q)
            e = (w * 0.5) - d
            best = e if best is None else np.maximum(best, e)
        return best.reshape(np.shape(gx))


def kind_from_fields(f, shape):
    kind = np.zeros(shape, int)
    kind[f["shallow"] > 0] = 1
    kind[f["deep"] > 0] = 2
    kind[(f["cliff"] > 0) & (kind == 0)] = 3
    kind[f["cliff"] > 1.5] = 3
    kind[f["deck"] > 0] = 4
    return kind


class TownLayout(CB.Layout):
    def __init__(self, M):
        self.M = M
        self.W, self.H = M.W, M.H
        self.portal_tiles = list(M.PORTALS)
        self.arrival_tiles = list(M.ARRIVALS)
        self.zone = Tilemap(M.NAME, M.W, M.H, M.DESC)
        self.z = self.zone
        self.z.region = M.REGION
        self.z.is_town = True                 # no gathering nodes in towns
        self.skipped, self.chests, self.placed = [], [], 0
        self.npc_xy = list(M.NPC_POSITIONS.values()) + list(getattr(M, "EXTRA_NPC_XY", []))

    def road_fn(self, gx, gy):
        return self.M.road_dist(gx, gy)


def build_terrain(L):
    M, z = L.M, L.z
    z.fill("dirt", "base")
    ys, xs = np.mgrid[0:M.H, 0:M.W]
    kind = M.tile_kind(xs + 0.5, ys + 0.5)
    L.kind = kind
    rd = M.road_dist(xs + 0.5, ys + 0.5)
    paved = M.paved(xs + 0.5, ys + 0.5) if hasattr(M, "paved") else None
    for y in range(M.H):
        for x in range(M.W):
            k = kind[y, x]
            if k == 1:
                z.set_tile(x, y, "shallow_water", "base")
            elif k == 2:
                z.set_tile(x, y, "deep_water", "base")
            elif k == 3:
                z.set_tile(x, y, "cliff", "collision")
            elif k == 4 or rd[y, x] > 0 or (paved is not None and paved[y, x] > 0):
                z.set_tile(x, y, "path", "base")


def place_portals(L):
    z, M = L.z, L.M
    for (px, py) in M.PORTALS:
        z.collision_layer[py][px] = None
        z.set_tile(px, py, "portal", "interaction")
    for (px, py) in M.ARRIVALS:
        z.collision_layer[py][px] = None


def seal_unreachable(L, start):
    z, M = L.z, L.M
    seen = {start}
    q = collections.deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < M.W and 0 <= n[1] < M.H and n not in seen and z.is_walkable(*n):
                seen.add(n)
                q.append(n)
    sealed = 0
    L.sealed_land, L.sealed_water = [], []          # so a baker can paint sealed pockets as walls / deep water
    for y in range(M.H):
        for x in range(M.W):
            if (x, y) not in seen and z.is_walkable(x, y):
                if z.base_layer[y][x] == "shallow_water":
                    z.set_tile(x, y, "deep_water", "base")
                    L.sealed_water.append((x, y))
                else:
                    z.set_tile(x, y, "cliff", "collision")
                    L.sealed_land.append((x, y))
                sealed += 1
    L.sealed = sealed


def register_baked(zone, M, chunk=20):
    for cy in range(0, M.H, chunk):
        for cx in range(0, M.W, chunk):
            fn = f"{M.BAKED_DIR}/ground_{cx}_{cy}.jpg"
            if not os.path.exists(fn):
                raise FileNotFoundError(f"{fn} - run python3 tools/bake_barrens_towns.py {M.KEY}")
            w, h = min(chunk, M.W - cx), min(chunk, M.H - cy)
            zone.add_ground_chunk(fn, cx, cy, w, h)
            zone.ground_chunks[-1]["exact"] = True
            zone.add_water_chunk(fn, cx, cy, w, h)
            zone.add_obstacle_chunk(fn, cx, cy, w, h)


def build(M):
    """Common build: terrain -> portals -> dressing -> seal -> chests."""
    L = TownLayout(M)
    build_terrain(L)
    place_portals(L)
    M.dress(L)
    seal_unreachable(L, M.START)
    for (x, y) in getattr(M, "CHESTS", []):
        L.chest(x, y)
    return L
