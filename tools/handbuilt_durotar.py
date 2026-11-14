"""
Hand-built Durotar (130x220): the red-clay road from Orgrimmar's gate south to
the sea, with Thunder Ridge, the Skull Rock coast, Kolkar Crag, Rocktusk Farm,
Scuttle Coast and Tiragarde's headland.

Same recipe as Valley of Trials (see claude/zone_perfection_playbook.md):
  * this module owns the TILE data (walkability, props, portals, subzones) and
    the analytic landform fields (`fields`) the baker paints from, so the
    painting and the collision grid can never drift apart;
  * tools/bake_durotar_terrain.py turns the same fields into one continuous
    painting registered as ground+water+obstacle chunks.

Every object is placed at an explicit coordinate (no random scatter).

HARD CONTRACTS (other zones reference these exact coordinates):
  portals  Orgrimmar (65,26)  Drygulch (95,25)  Zeppelin (112,35)  Skull Rock (118,60)
           Sunken Grotto (120,40)  Central Barrens (5,85)  Razor Hill (65,108)
           Dustwind (40,130)  Valley of Trials (28,150)  Echo Isles (110,150)
           Tiragarde (95,178)  Thunder Ridge (55,45)
  arrivals (105,150) Echo Isles south dock
"""
import math
import os

import numpy as np
from PIL import Image
from scipy.spatial import cKDTree

from world.tilemap import Tilemap

DP = "assets/tiles/dungeon_props/"
BLD = "assets/buildings/"
ENT = "assets/tiles/cave_entrances/"
BAKED_DIR = "assets/tiles/durotar/baked"
W, H = 130, 220

PORTALS = {
    (65, 26): "Orgrimmar", (95, 25): "Drygulch Ravine", (112, 35): "Zeppelin Tower",
    (118, 60): "Skull Rock", (120, 40): "Sunken Grotto of the Deep",
    (5, 85): "Central Barrens", (65, 108): "Razor Hill", (40, 130): "Dustwind Cave",
    (28, 150): "Valley of Trials", (110, 150): "Echo Isles", (95, 178): "Tiragarde Keep",
    (55, 45): "Thunder Ridge",
}
ARRIVALS = [(105, 150)]

# ---------------------------------------------------------------- the plan
# roads: waypoints (tile coords), width in tiles.  Every cave road ends one
# tile SOUTH of its portal so the cave mouth faces the approach.
ROADS = {
    "gate":     ([(65, 24), (65, 30), (68, 36), (72, 41)], 3.6),
    "main":     ([(72, 41), (78, 49), (78, 58), (73, 68), (67, 78), (64, 88), (66, 98), (65, 107)], 3.4),
    "thunder":  ([(74, 43), (68, 47), (61, 50), (56, 49), (55, 46)], 2.4),
    "drygulch": ([(66, 31), (75, 30), (85, 30), (93, 28), (95, 26)], 2.4),
    "east":     ([(78, 52), (89, 52), (99, 50), (106, 45), (111, 38), (112, 36)], 2.6),
    "grotto":   ([(106, 45), (113, 46), (119, 44), (120, 41)], 2.2),
    "skull":    ([(98, 50), (103, 57), (110, 63), (118, 63), (118, 61)], 2.4),
    "west":     ([(65, 107), (54, 103), (42, 97), (30, 92), (19, 88), (11, 85), (5, 85)], 2.8),
    "crag":     ([(63, 109), (58, 118), (53, 127), (46, 134), (41, 134), (40, 131)], 2.4),
    "farm":     ([(46, 134), (45, 144), (41, 153), (36, 160), (32, 168)], 2.2),
    "vot":      ([(37, 158), (32, 155), (28, 151)], 2.2),
    "coast":    ([(65, 109), (70, 120), (82, 132), (95, 142), (104, 149), (111, 150)], 2.8),
    "tira":     ([(70, 122), (72, 138), (77, 152), (83, 165), (89, 174), (95, 179)], 2.6),
}

# decks laid over water: (x0, x1, y0, y1, kind)
DECKS = [
    (0.0, 14.6, 83.6, 86.4, "bridge"),
    (100.0, 111.6, 148.6, 151.4, "pier"),
]

# cliff massifs: (cx, cy, rx, ry, rot_deg)
MESAS = [
    # Thunder Ridge massif (NW) + the face behind its cave mouth
    (21, 46, 12, 16, 8), (17, 30, 11, 8, 0), (40, 31, 8, 6.5, -10), (53, 35, 9, 6, 0),
    # north wall buttresses (Orgrimmar's mountains are not a straight line)
    (84, 19, 9, 4.5, 0), (104, 18, 8, 5, 0), (30, 22, 8, 4, 0), (116, 20, 8, 5, 0),
    # NE: behind Sunken Grotto / Skull Rock; Zeppelin stands in the open
    (122, 34, 8, 5, 0), (120, 54, 9, 6, 0), (126, 64, 6, 9, 0),
    # Kolkar Crag bowl walls (open middle) + the face behind Dustwind
    (12, 112, 9, 13, 0), (10, 138, 8, 9, 0), (40, 122, 9, 4.5, 0), (23, 146, 8, 5, 0),
    # Valley of Trials gateway canyon
    (28, 143, 9, 5.5, 0), (19, 152, 5.5, 6, 0), (38, 147, 5, 5, 0),
    # mesa clusters in the open country (composition, cover, landmarks)
    (88, 70, 6, 4, 20), (95, 76, 3.5, 3, 0), (103, 88, 5, 7, -15),
    (53, 78, 5, 3.5, 0), (46, 84, 3, 2.5, 0),
    (84, 115, 6, 4, 10), (91, 120, 3, 3, 0), (100, 104, 6, 4, 0),
    (92, 130, 5, 4, 0), (57, 143, 6, 5, 0), (62, 150, 3, 3, 0),
    (60, 170, 7, 5, 0), (30, 183, 8, 5, 0), (112, 118, 6, 6, 0),
    # coastal rock points forming Scuttle Cove
    (116, 132, 5, 8, 0), (112, 169, 6, 5, 0),
]

# long ridges: (waypoints, half-width) - canyon walls that shape the routes
RIDGES = [
    ([(14, 73), (28, 75), (42, 71), (52, 66)], 3.0),          # south wall of Thunder Ridge
    ([(12, 100), (26, 98), (36, 100), (46, 106)], 2.8),        # north wall of Kolkar Crag
    ([(97, 64), (108, 70), (118, 73), (127, 74)], 2.6),        # Skull Rock escarpment
    ([(84, 92), (92, 98), (98, 108), (100, 112)], 2.4),        # dune ridge
    ([(58, 152), (64, 160), (66, 172), (60, 184)], 2.4),       # west of the Tiragarde road
    ([(14, 160), (20, 170), (24, 186), (22, 198)], 2.8),       # Rocktusk's river wall
]

# gaps carved through the above: ("ell", cx, cy, rx, ry)
GAPS = [
    ("ell", 65, 27, 14, 8),          # Orgrimmar gate plaza
    ("ell", 55, 45, 4.5, 4.5),       # Thunder Ridge landing
    ("ell", 95, 25, 4.5, 4.5),       # Drygulch landing
    ("ell", 112, 36, 5, 4.5),        # Zeppelin landing
    ("ell", 120, 40, 4.5, 4.5),      # Sunken Grotto landing
    ("ell", 118, 60, 4.5, 4.5),      # Skull Rock landing
    ("ell", 40, 130, 4.5, 4.5),      # Dustwind landing
    ("ell", 28, 150, 4.5, 4.5),      # VoT landing
    ("ell", 65, 106, 13, 9),         # Razor Hill crossing
    ("ell", 95, 177, 7, 5),          # Tiragarde landing
]

_ROAD_TREES = {}


def _road_tree(name):
    if name not in _ROAD_TREES:
        from tools.terrain_painter import Painter
        pts, w = ROADS[name]
        line = Painter.spline(pts)
        _ROAD_TREES[name] = (cKDTree(line), w)
    return _ROAD_TREES[name]


def road_dist(gx, gy, names=None):
    q = np.stack([np.ravel(gx), np.ravel(gy)], 1)
    best = None
    for n in (names or ROADS):
        tree, w = _road_tree(n)
        d, _ = tree.query(q)
        e = (w * 0.5 + 0.0) - d            # >0 on the road surface
        best = e if best is None else np.maximum(best, e)
    return best.reshape(np.shape(gx))


def _wob(gx, gy):
    return (0.45 * np.sin(0.37 * gx + 1.3) * np.sin(0.29 * gy + 0.7)
            + 0.30 * np.sin(0.83 * gx + 0.21 * gy + 2.0)
            + 0.25 * np.sin(0.19 * gx - 0.57 * gy + 4.1))


def _smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------ water shapes
def river_center(gy):
    return 9.8 + 2.0 * np.sin(0.040 * gy + 0.8) + 1.2 * np.sin(0.11 * gy + 2.0)


def river_halfwidth(gy):
    return 4.4 + 0.8 * np.sin(0.07 * gy + 1.0)


def coast_east(gy):
    return (126.0 - 16.0 * _smooth(78, 118, gy) - 4.0 * _smooth(118, 150, gy)
            + 1.8 * np.sin(gy * 0.09 + 1.0) + 1.0 * np.sin(gy * 0.21))


def coast_south(gx):
    return 201.5 + 2.0 * np.sin(gx * 0.11 + 0.5) + 1.2 * np.sin(gx * 0.27)


#: A SECRET ISLET off the east coast (tools/build_secrets.py): land in the sea and a narrow ford of
#: shallows out to it. The map draws both as open sea. Don't describe where it is to Kyle.
SECRET_ISLETS = [(122.0, 186.0, 3.6, 3.0)]
SECRET_FORDS = [((107.0, 185.0), (120.0, 186.0), 1.5)]     # (from, to, half-width)


def _secret_isle(gx, gy):
    best = np.full(np.shape(gx), -99.0)
    for (cx, cy, rx, ry) in SECRET_ISLETS:
        d = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
        best = np.maximum(best, (1.0 - d) * min(rx, ry))
    return best


def _secret_ford(gx, gy):
    best = np.full(np.shape(gx), -99.0)
    for (a, b, hw) in SECRET_FORDS:
        ax, ay = a
        bx, by = b
        dx, dy = bx - ax, by - ay
        t = np.clip(((gx - ax) * dx + (gy - ay) * dy) / (dx * dx + dy * dy), 0.0, 1.0)
        dist = np.sqrt((gx - ax - t * dx) ** 2 + (gy - ay - t * dy) ** 2)
        best = np.maximum(best, hw - dist)
    return best


def water_fields(gx, gy):
    """(shallow_extent, deep_extent): >0 inside, in tiles. Union of river + sea."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    r_s = river_halfwidth(gy) - np.abs(gx - river_center(gy))
    r_d = r_s - 2.2
    se = gx - coast_east(gy)
    ss = gy - coast_south(gx)
    s_ext = np.maximum(se, ss)
    sea_s, sea_d = s_ext, s_ext - 3.2
    isle = _secret_isle(gx, gy)
    sea_s = np.minimum(sea_s, -isle)                              # the islet is land
    sea_d = np.minimum(sea_d, np.minimum(-(isle + 2.2), -_secret_ford(gx, gy)))   # ringed and forded by shallows
    return np.maximum(r_s, sea_s), np.maximum(r_d, sea_d)


def deck_field(gx, gy):
    """signed extent inside any deck rect (tiles); also returns per-kind."""
    best = np.full(np.shape(gx), -9.0)
    for (x0, x1, y0, y1, _k) in DECKS:
        e = np.minimum(np.minimum(gx - x0, x1 - gx), np.minimum(gy - y0, y1 - gy))
        best = np.maximum(best, e)
    return best


# ----------------------------------------------------------------- cliffs
def gap_extent(gx, gy):
    best = np.full(np.shape(gx), -99.0)
    for g in GAPS:
        _, cx, cy, rx, ry = g
        d = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
        best = np.maximum(best, (1 - d) * min(rx, ry))
    # every road keeps a clear corridor (surface + margin)
    best = np.maximum(best, road_dist(gx, gy) + 2.6)
    # decks over water stay clear
    best = np.maximum(best, deck_field(gx, gy) + 1.5)
    return best


_RIDGE_TREES = {}


def _ridge(pts, hw, gx, gy):
    key = id(pts)
    if key not in _RIDGE_TREES:
        from tools.terrain_painter import Painter
        _RIDGE_TREES[key] = cKDTree(Painter.spline(pts))
    d, _ = _RIDGE_TREES[key].query(np.stack([gx.ravel(), gy.ravel()], 1))
    return (hw + 0.7 * _wob(gx, gy) * 1.0 - d.reshape(gx.shape))


def cliff_raw(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    w = _wob(gx, gy)
    out = np.full(gx.shape, -99.0)
    for (cx, cy, rx, ry, rot) in MESAS:
        dx, dy = gx - cx, gy - cy
        if rot:
            c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
            dx, dy = c * dx + s * dy, -s * dx + c * dy
        r = np.sqrt((dx / rx) ** 2 + (dy / ry) ** 2)
        out = np.maximum(out, (1 - r) * min(rx, ry))
    for (rpts, rhw) in RIDGES:
        out = np.maximum(out, _ridge(rpts, rhw, gx, gy))
    north = (21.0 + 2.4 * np.sin(0.17 * gx + 0.5) + 1.6 * np.sin(0.43 * gx + 1.7)) - gy
    west = (4.8 + 0.8 * np.sin(0.21 * gy + 1.0)) - gx
    rim = np.minimum(gx - (123.2 + 1.5 * np.sin(0.23 * gy + 0.4) + 1.0 * np.sin(0.57 * gy)),
                     (82.0 - gy))
    out = np.maximum(out, np.maximum(north, np.maximum(west, rim)))
    return out + 1.1 * w


def fields(gx, gy):
    """All analytic landform fields. Shared by tiles and the baker."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    sh, dp = water_fields(gx, gy)
    cl = np.minimum(cliff_raw(gx, gy), -gap_extent(gx, gy) + 0.0)
    return dict(cliff=cl, shallow=sh, deep=dp, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    """0 land, 1 shallow, 2 deep, 3 cliff, 4 deck at tile centres (arrays)."""
    f = fields(gx, gy)
    kind = np.zeros(np.shape(gx), int)
    kind[f["shallow"] > 0] = 1
    kind[f["deep"] > 0] = 2
    # the west rim cliff sits over the river's far bank; cliffs win on land only
    kind[(f["cliff"] > 0) & (kind == 0)] = 3
    # a cliff rim over water edge: treat as cliff too (keeps banks solid)
    kind[(f["cliff"] > 1.5)] = 3
    kind[f["deck"] > 0] = 4
    return kind


# --------------------------------------------------------------- NPC spots
# id -> (x, y).  tools/sync_durotar_npcs.py writes these into data/npcs/*.json
# (quests reference npc ids, never coordinates, so they are free to move).
NPC_POSITIONS = {
    # ambient NPCs (data/npcs/ambient_npcs.json)
    "durotar_orgrimmar_gate_guard": (61, 28),
    "durotar_patrol_1": (81, 46),
    "durotar_traveler": (80, 72),
    "durotar_kid": (82, 74),
    "durotar_skeleton_marker": (107, 57),
    "durotar_vot_road_traveler": (34, 156),
    "durotar_razorhill_road_merchant": (68, 95),
    "durotar_tiragarde_scout": (88, 172),
    # vendors / forge (data/npcs/vendors.json, forges.json)
    "durotar_vendor": (68, 108),
    "southern_durotar_trader": (69, 110),
    "durotar_forge": (71, 108),
}

CAVES = {   # portal tile -> (sprite, w, h)
    (55, 45): ("cave_entrance_plain", 6, 4),
    (95, 25): ("cave_entrance_plain", 6, 4),
    (120, 40): ("cave_entrance_plain", 6, 4),
    (118, 60): ("cave_entrance_banners", 7, 5),
    (40, 130): ("cave_entrance_plain", 6, 4),
}

_ASPECT = {}


def _aspect(path):
    if path not in _ASPECT:
        with Image.open(path) as im:
            _ASPECT[path] = im.size[0] / im.size[1]
    return _ASPECT[path]


class Layout:
    def __init__(self):
        self.zone = Tilemap("Durotar", W, H,
                            "A harsh red land of canyons and dust, running from Orgrimmar's gates "
                            "down to the southern sea.")
        self.z = self.zone
        self.z.region = "Kalimdor - East Coast"
        self.skipped = []
        self.chests = []
        self.placed = 0
        self.npc_xy = list(NPC_POSITIONS.values())

    # ------------------------------------------------------------ helpers
    def road_clear(self, x, y, margin=0.9):
        return road_dist(np.array([x + 0.5]), np.array([y + 0.5]))[0] < -margin

    def _try(self, path, wt, height, cx, base_y, solid, fraction, road_ok, allow_overlap, shore_ok):
        z = self.z
        ax, ay = cx - wt // 2, base_y - height + 1
        core = []
        rows = max(1, round(height * fraction))
        for y in range(ay, ay + height):
            for x in range(ax, ax + wt):
                if solid is True or (solid == "core" and y >= ay + height - rows
                                     and ax + int(wt * 0.2) <= x < max(ax + int(wt * 0.8), ax + int(wt * 0.2) + 1)):
                    core.append((x, y))
        probe = core or [(cx, base_y)]
        for (x, y) in probe:
            if not (0 <= x < W and 0 <= y < H):
                return "off-map", core, ax, ay
            if z.collision_layer[y][x] is not None and not allow_overlap:
                return "overlaps solid", core, ax, ay
            if z.base_layer[y][x] == "deep_water" or (z.base_layer[y][x] == "shallow_water" and not shore_ok):
                return "water", core, ax, ay
            if any(abs(x - nx) <= 1 and abs(y - ny) <= 1 for nx, ny in self.npc_xy):
                return "NPC", core, ax, ay
            if any(abs(x - px) <= 2 and abs(y - py) <= 2 for px, py in list(PORTALS) + ARRIVALS):
                return "portal", core, ax, ay
            if not road_ok and not self.road_clear(x, y, 0.6):
                return "road", core, ax, ay
        return None, core, ax, ay

    def prop(self, name, cx, base_y, height, solid="core", fraction=0.4, road_ok=False,
             path_dir=DP, allow_overlap=False, shore_ok=False, nudge=3):
        """Sprite `name` with bottom-centre on (cx, base_y). solid: False decor |
        True whole footprint | "core" base only.  If the spot is taken (road, NPC,
        portal, water, cliff, another prop) the nearest free spot within `nudge`
        tiles is used; otherwise it is logged in `skipped`."""
        path = f"{path_dir}{name}.png" if not name.endswith(".png") else f"{path_dir}{name}"
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        z = self.z
        wt = max(1, round(height * _aspect(path)))
        offs = sorted(((dx, dy) for dx in range(-nudge, nudge + 1) for dy in range(-nudge, nudge + 1)),
                      key=lambda d: (d[0] ** 2 + d[1] ** 2, abs(d[0])))
        first_bad = None
        for (dx, dy) in offs:
            bad, core, ax, ay = self._try(path, wt, height, cx + dx, base_y + dy, solid, fraction,
                                          road_ok, allow_overlap, shore_ok)
            if first_bad is None:
                first_bad = bad
            if bad is None:
                z.add_landmark(path, ax, ay, wt, height, solid=False)
                for (x, y) in core:
                    if z.interaction_layer[y][x] is None:
                        z.collision_layer[y][x] = "landmark"
                self.placed += 1
                return True
        self.skipped.append((name, cx, base_y, first_bad))
        return False

    def bld(self, name, cx, base_y, height, **kw):
        kw.setdefault("path_dir", BLD)
        kw.setdefault("fraction", 0.5)
        return self.prop(name, cx, base_y, height, **kw)

    def row(self, name, xs, base_y, height, **kw):
        return sum(bool(self.prop(name, x, base_y, height, **kw)) for x in xs)

    def cave(self, cx, cy, sprite, w=6, h=4):
        z = self.z
        z.add_landmark(f"{ENT}{sprite}.png", cx - w // 2, cy - h + 1, w, h, mouth_offset=(w // 2, h - 1))

    def chest(self, x, y):
        z = self.z
        for r in range(0, 6):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    xx, yy = x + dx, y + dy
                    if (0 <= xx < W and 0 <= yy < H and z.is_walkable(xx, yy)
                            and z.interaction_layer[yy][xx] is None
                            and z.base_layer[yy][xx] not in ("deep_water", "shallow_water", "path")
                            and z.collision_layer[yy][xx] is None
                            and self.road_clear(xx, yy, 0.4)
                            and not any(abs(xx - nx) <= 1 and abs(yy - ny) <= 1 for nx, ny in self.npc_xy)):
                        z.set_tile(xx, yy, "chest", "interaction")
                        self.chests.append((xx, yy))
                        return True
        self.skipped.append(("chest", x, y, "no free tile"))
        return False


# ------------------------------------------------------------ terrain shape
def _terrain(L):
    z = L.z
    z.fill("sand", "base")
    ys, xs = np.mgrid[0:H, 0:W]
    kind = tile_kind(xs + 0.5, ys + 0.5)
    L.kind = kind
    rd = road_dist(xs + 0.5, ys + 0.5)
    for y in range(H):
        for x in range(W):
            k = kind[y, x]
            if k == 1:
                z.set_tile(x, y, "shallow_water", "base")
            elif k == 2:
                z.set_tile(x, y, "deep_water", "base")
            elif k == 3:
                z.set_tile(x, y, "cliff", "collision")
            elif k == 4:
                z.set_tile(x, y, "path", "base")
            elif rd[y, x] > 0:
                z.set_tile(x, y, "path", "base")


def _seal_unreachable(L, start=(65, 28)):
    """Anything walkable that cannot be reached from the gate plaza is sealed
    (land -> cliff, water -> deep water) so there are no stranded pockets."""
    import collections
    z = L.z
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
    for y in range(H):
        for x in range(W):
            if (x, y) not in seen and z.is_walkable(x, y):
                if z.base_layer[y][x] == "shallow_water":
                    z.set_tile(x, y, "deep_water", "base")
                else:
                    z.set_tile(x, y, "cliff", "collision")
                n_sealed += 1
    L.sealed = n_sealed


def _portals(L):
    z = L.z
    for (px, py) in PORTALS:
        z.collision_layer[py][px] = None
        z.set_tile(px, py, "portal", "interaction")
    for (px, py) in ARRIVALS:
        z.collision_layer[py][px] = None
    for (px, py), (spr, w, h) in CAVES.items():
        L.cave(px, py, spr, w, h)


# ------------------------------------------------------------------ dressing
def _dress_gate(L):
    """Orgrimmar's gate and the plaza before it."""
    z = L.z
    z.add_landmark(f"{BLD}orgrimmar_gate.png", 58, 13, 14, 11)
    p, b = L.prop, L.bld
    p("vot_war_banner", 58, 28, 5)
    p("vot_war_banner", 72, 28, 5)
    p("vot_fire_pit", 60, 31, 3)
    b("watchtower", 51, 29, 9)
    b("watchtower", 79, 29, 9)


def _dress_drygulch(L):
    p, b = L.prop, L.bld
    p("vot_trail_cairn", 91, 29, 3)
    p("bbc_rubble" if False else "den_rock_rubble", 99, 27, 2, solid=False)
    p("vot_totem_pole", 98, 29, 6)
    b("guard_post", 88, 25, 4)


def _dress_thunder(L):
    p, b = L.prop, L.bld
    b("guard_post", 49, 49, 5)
    b("watchers_perch", 61, 53, 8)
    p("vot_mesa_pillar", 63, 62, 7)
    p("vot_mesa_pillar", 46, 62, 6)
    for (x, y) in [(55, 60), (66, 58), (44, 55)]:
        p("vot_thornbush", x, y, 2, solid=False)
    p("vot_dead_tree", 52, 66, 6)
    p("vot_trail_cairn", 59, 47, 3)


def _dress_highway(L):
    """The long road: a watchpost, a burnt caravan, a prospector's dig, cairns."""
    p, b = L.prop, L.bld
    b("watchtower", 84, 47, 9)
    p("vot_trail_cairn", 80, 51, 3)
    # prospector's dig by the east road
    b("generic_tent_b", 90, 58, 4)
    p("vot_crate_stack", 95, 58, 3)
    p("den_rock_rubble", 97, 62, 2)
    p("vot_hide_rack", 93, 51, 3)
    # the burnt caravan
    p("vot_broken_cart", 70, 85, 3)
    p("vot_crate_stack", 72, 87, 3)
    p("vot_beast_ribcage", 63, 83, 3)
    # campfire where travellers rest
    p("vot_fire_pit", 78, 74, 3)
    p("vot_fallen_log", 75, 75, 2)
    for (x, y) in [(86, 62), (68, 60), (82, 86), (74, 100), (60, 92)]:
        p("vot_barrel_cactus", x, y, 3)
    for (x, y) in [(72, 52), (84, 80), (62, 96)]:
        p("vot_thornbush", x, y, 2, solid=False)
    p("vot_dead_tree", 85, 66, 6)
    p("vot_dead_tree", 56, 80, 6)
    p("vot_mesa_pillar", 90, 74, 7)
    p("vot_trail_cairn", 66, 90, 3)


def _dress_ne(L):
    """Zeppelin landing, the Grotto's naga-touched mouth, Skull Rock's taint."""
    z = L.z
    p, b = L.prop, L.bld
    b("zep_tower_orc", 112, 32, 10, nudge=2)               # the zeppelin tower (portal tile at 112,35)
    p("vot_crate_stack", 108, 37, 3)
    p("vot_crate_stack", 116, 37, 3)
    p("vot_war_banner", 105, 36, 5)
    # Sunken Grotto
    p("grotto_naga_rune_stone", 116, 42, 5)
    p("grotto_tide_pool", 123, 45, 3, solid=False)
    p("grotto_barnacle_pillar" if False else "vot_mesa_pillar", 119, 29, 6)
    # Skull Rock: Searing Blade stronghold approach
    p("bbc_banner", 112, 63, 5)
    p("bbc_banner", 124, 63, 5)
    p("bbc_fel_brazier", 114, 65, 3, road_ok=True)
    p("bbc_fel_brazier", 122, 65, 3, road_ok=True)
    p("bbc_skull_pile", 110, 61, 3)
    p("vot_beast_ribcage", 106, 54, 3)
    p("vot_dead_tree", 104, 62, 6)
    p("vot_dead_tree", 108, 47, 6)
    p("vot_barrel_cactus", 100, 55, 3)
    p("vot_thornbush", 114, 52, 2, solid=False)


def _dress_razor_hill(L):
    """Razor Hill crossing: palisade gate arched over the road, market, houses."""
    z = L.z
    p, b = L.prop, L.bld
    z.add_landmark(f"{BLD}palisade_gatehouse.png", 60, 99, 11, 7, solid=False)
    L.row("vot_palisade", [54, 56], 104, 3)
    L.row("vot_palisade", [74, 76], 104, 3)
    b("watchers_perch", 52, 105, 8)
    b("watchers_perch", 78, 105, 8)
    b("plain_orc_house_a", 56, 98, 5)
    b("plain_orc_house_b", 74, 98, 5)
    b("well_house", 60, 112, 5)
    b("supply_cache_shed", 76, 113, 5)
    p("vot_war_banner", 62, 109, 5)
    p("vot_war_banner", 68, 105, 5)
    p("vot_crate_stack", 72, 110, 3)
    p("vot_fire_pit", 64, 112, 3)
    p("vot_hide_rack", 70, 112, 3)


def _dress_crag(L):
    """Kolkar Crag: a centaur war-camp in a rock bowl, Dustwind's scorpid burrows."""
    p, b = L.prop, L.bld
    b("generic_tent_a", 20, 121, 5)
    b("generic_tent_b", 28, 120, 5)
    b("generic_tent_a", 24, 128, 5)
    p("vot_fire_pit", 24, 124, 3)
    p("vot_totem_pole", 31, 125, 6)
    p("vot_war_drum", 19, 126, 3)
    p("vot_hide_rack", 27, 116, 3)
    p("vot_war_banner", 22, 117, 5)
    p("vot_palisade", 33, 130, 3)
    for (x, y) in [(18, 112), (30, 134), (16, 135)]:
        p("vot_thornbush", x, y, 2, solid=False)
    p("vot_dead_tree", 34, 114, 6)
    # Dustwind Cave mouth
    for (x, y) in [(36, 135), (45, 129), (35, 124)]:
        p("vot_scorpid_burrow", x, y, 3)
    p("vot_beast_ribcage", 44, 136, 3)
    p("den_chitin_husk", 34, 130, 2)


def _dress_farm(L):
    """Rocktusk Farm: quilboar homestead among tilled plots."""
    p, b = L.prop, L.bld
    b("generic_shack_b", 36, 168, 5)
    b("generic_shack_a", 24, 169, 5)
    b("hide_tanners_hut", 46, 176, 5)
    p("vot_hide_rack", 31, 171, 3)
    p("vot_broken_cart", 40, 172, 3)
    p("vot_totem_pole", 26, 181, 6)
    L.row("vot_palisade", [18, 20, 22], 160, 3)
    L.row("vot_palisade", [38, 40, 42], 160, 3)
    for (x, y) in [(22, 185), (34, 185), (45, 169), (17, 173), (43, 163)]:
        p("vot_thornbush", x, y, 2, solid=False)
    for (x, y) in [(30, 178), (44, 182)]:
        p("vot_barrel_cactus", x, y, 3)
    p("vot_dead_tree", 40, 186, 6)
    # the Valley of Trials gateway
    z = L.z
    p("vot_rock_arch", 28, 152, 8, solid=False, road_ok=True)
    p("vot_war_banner", 24, 154, 5)
    p("vot_war_banner", 33, 154, 5)
    p("vot_trail_cairn", 38, 156, 3)


def _dress_coast(L):
    """Scuttle Coast: murloc huts on the shore, a wreck, the Echo Isles pier."""
    p, b = L.prop, L.bld
    M = "assets/tiles/scuttle_coast/props/"
    p("murloc_hut_stilted", 106, 134, 7, path_dir=M)
    p("murloc_hut_net", 99, 140, 7, path_dir=M)
    p("murloc_hut_basket", 106, 160, 7, path_dir=M)
    p("grotto_fishing_net", 103, 137, 2, solid=False)
    p("grotto_ship_bow", 108, 168, 6, shore_ok=True)
    p("grotto_pirate_skeletons", 103, 166, 2, solid=False)
    p("grotto_barrel_stack", 101, 153, 3)
    p("vot_war_banner", 98, 147, 5)
    p("vot_trail_cairn", 100, 146, 3)
    for (x, y) in [(96, 130), (94, 154), (92, 164)]:
        p("vot_barrel_cactus", x, y, 3)
    p("vot_dead_tree", 90, 150, 6)
    for (x, y) in [(112, 140), (109, 156), (110, 146)]:
        p("vot_reeds", x, y, 3, solid=False, shore_ok=True)
    # the dry pan
    p("vot_beast_ribcage", 80, 142, 3)
    p("vot_dead_tree", 78, 134, 6)
    p("vot_mesa_pillar", 70, 134, 7)
    p("vot_fallen_log", 84, 146, 2)


def _dress_tiragarde(L):
    z = L.z
    p, b = L.prop, L.bld
    z.add_landmark(f"{ENT}entrance_tiragarde_castle.png", 91, 171, 9, 8, mouth_offset=(4, 7))
    p("broken_column", 86, 177, 3)
    p("broken_column", 102, 175, 3)
    p("grotto_ship_cannon", 99, 182, 3)
    p("grotto_barrel_stack", 90, 183, 3)
    p("grotto_anchor", 86, 183, 2, solid=False)
    p("vot_dead_tree", 80, 186, 6)
    p("vot_thornbush", 98, 186, 2, solid=False)
    p("vot_trail_cairn", 82, 170, 3)


def _dress_river_and_barrens(L):
    p, b = L.prop, L.bld
    # reed beds along the east bank, a few sagewoods where the fringe is green
    for (x, y) in [(15, 30), (14, 52), (16, 70), (17, 100), (14, 128), (17, 147), (19, 175)]:
        p("vot_reeds", x, y, 3, solid=False, shore_ok=True)
    for (x, y) in [(18, 60), (19, 118), (16, 190)]:
        p("vot_sagewood_tree", x, y, 7)
    # Barrens bridge: banners and a toll post at the east end
    p("vot_war_banner", 17, 83, 5)
    p("vot_war_banner", 17, 89, 5)
    b("guard_post", 22, 82, 4)
    # the road to the Barrens
    p("vot_trail_cairn", 40, 96, 3)
    p("vot_dead_tree", 28, 90, 6)
    p("vot_barrel_cactus", 48, 99, 3)
    p("vot_mesa_pillar", 50, 89, 6)


def _chests(L):
    for (x, y) in [(70, 36), (62, 70), (53, 62), (96, 40), (116, 50), (88, 100),
                   (47, 92), (22, 126), (38, 158), (80, 140), (110, 165), (92, 190)]:
        L.chest(x, y)


def _subzones(L):
    z = L.z
    z.add_subzone("Thunder Ridge", 38, 40, 30, 34, display_name="Thunder Ridge Approach")
    z.add_subzone("Skull Rock Approach", 96, 28, 34, 46)
    z.add_subzone("Kolkar Crag", 8, 100, 40, 48)
    z.add_subzone("Rocktusk Farm", 14, 152, 36, 40)
    z.add_subzone("Scuttle Coast", 92, 120, 36, 60)


def build_layout():
    L = Layout()
    _terrain(L)
    _portals(L)
    _dress_gate(L)
    _dress_drygulch(L)
    _dress_thunder(L)
    _dress_highway(L)
    _dress_ne(L)
    _dress_razor_hill(L)
    _dress_crag(L)
    _dress_farm(L)
    _dress_coast(L)
    _dress_tiragarde(L)
    _dress_river_and_barrens(L)
    _chests(L)
    _subzones(L)
    _seal_unreachable(L)
    return L


def register_baked(zone, baked_dir=BAKED_DIR, chunk=20):
    """Register the baked painting as ground + water + obstacle chunks."""
    for cy in range(0, H, chunk):
        for cx in range(0, W, chunk):
            fn = f"{baked_dir}/ground_{cx}_{cy}.jpg"
            if not os.path.exists(fn):
                raise FileNotFoundError(f"{fn} - run python3 tools/bake_durotar_terrain.py")
            w, h = min(chunk, W - cx), min(chunk, H - cy)
            zone.add_ground_chunk(fn, cx, cy, w, h)
            zone.ground_chunks[-1]["exact"] = True   # seamless painting: skip feather pass
            zone.add_water_chunk(fn, cx, cy, w, h)
            zone.add_obstacle_chunk(fn, cx, cy, w, h)


def generate_durotar():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=6):
    ys, xs = np.mgrid[0:H, 0:W]
    kind = tile_kind(xs + 0.5, ys + 0.5)
    pal = {0: (205, 120, 70), 1: (110, 190, 210), 2: (40, 90, 150), 3: (70, 50, 45), 4: (140, 100, 50)}
    img = np.zeros((H, W, 3), np.uint8)
    for k, c in pal.items():
        img[kind == k] = c
    rd = road_dist(xs + 0.5, ys + 0.5)
    img[(rd > 0) & (kind == 0)] = (235, 200, 120)
    for (px, py) in PORTALS:
        img[py, px] = (255, 0, 255)
    Image.fromarray(img).resize((W * scale, H * scale), Image.NEAREST).save(path)
    return kind
