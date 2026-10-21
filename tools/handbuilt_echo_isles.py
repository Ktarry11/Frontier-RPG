"""
Hand-built Echo Isles (160x160): the Darkspear archipelago.

Seven real islands in a deep sea, linked three different ways:
  * THREE ROPE BRIDGES (east-west spans, sized to the bridge sprites - the art is
    side-on, so a bridge only ever runs east-west):
        Echo Landing <-> Troll Camp isle   (short)
        Echo Landing <-> Grotto isle       (short)
        Echo Landing <-> Hollow isle       (long, the dramatic one)
  * WADEABLE SHALLOW FORDS between the other islands (walkable shallow_water that
    is painted pale turquoise against the dark deep sea):
        Wreck Shallows    Troll isle   -> The Lost Fleet
        Drowned Causeway  Troll isle   -> Hollow isle   (a second, wetter way in)
        Sunken Steps      Grotto isle  -> Naga Ruins
        Razorjaw Shallows Echo Landing -> Razorjaw Reef
  * TIDAL FLATS: an open lagoon of shallows with sand cays off Echo Landing.
  Every ford / flat is registered as a SHALLOW-WATER SUBZONE (Tilemap.add_subzone
  base_tiles=("shallow_water",)) so wading creatures live only in the water.
  Two timber piers (north / south dock) carry the Durotar links.

Same recipe as Valley of Trials / Durotar (claude/zone_perfection_playbook.md):
this module owns the TILE data and the analytic landform fields the baker
(tools/bake_echo_isles.py) paints from, so collision and painting cannot drift.
Every object is placed at an explicit coordinate (no random scatter).

HARD CONTRACTS (world/portal_manager.py)
  north dock (80,8)  <-> Durotar (110,150)     south dock (80,152) -> Durotar (105,150)
  Sunken Temple Grotto and Zalazane's Hollow entrances: GROTTO / HOLLOW below.
"""
import math
import os

import numpy as np
from PIL import Image

from world.tilemap import Tilemap

DP = "assets/tiles/dungeon_props/"
BLD = "assets/buildings/"
ENT = "assets/tiles/cave_entrances/"
EP = "assets/tiles/echo_isles/props/"
SB = "assets/tiles/seabed/"
NG = "assets/tiles/naga_dungeon/"
BR = "assets/tiles/bridges/"
VEG = "assets/tiles/vegetation/"
BAKED_DIR = "assets/tiles/echo_isles/baked"
W, H = 160, 160

NORTH_DOCK = (80, 8)
SOUTH_DOCK = (80, 152)
GROTTO = (24, 98)          # portal tile of Sunken Temple Grotto
HOLLOW = (141, 117)        # portal tile of Zalazane's Hollow

SHORE_W = 2.6              # width of the natural wadeable shore band (tiles)

# ---------------------------------------------------------------- islands
# (cx, cy, rx, ry) ellipses, unioned per island.  Land extent = (1-r)*min(rx,ry).
ISLANDS = {
    "echo":   [(80, 44, 18, 14), (77, 66, 22, 18), (82, 89, 25, 22), (82, 113, 20, 16), (66, 100, 12, 12)],
    "troll":  [(128, 54, 17, 15), (121, 62, 10, 9)],
    "fleet":  [(147, 22, 13, 11), (138, 28, 7, 6)],
    "hollow": [(139, 106, 14, 14), (131, 100, 8, 8)],
    "grotto": [(30, 90, 14, 13), (24, 84, 8, 7)],
    "naga":   [(24, 48, 13, 12), (34, 52, 7, 7)],
    "reef":   [(46, 138, 15, 10), (56, 142, 8, 7)],
    # sand cays on the Tidal Flats
    "cays":   [(109, 129, 2.6, 2.0), (100, 132, 2.2, 1.8), (113, 124, 2.0, 1.7)],
    # bridge footings: land under every pylon so the sprites never float
    "footings": [(96, 59, 3.0, 3.0), (112, 58, 3.0, 3.0),
                 (59, 90, 3.0, 3.0), (43, 90, 3.0, 3.0),
                 (101, 104, 3.0, 3.0), (125, 104, 3.0, 3.0)],
}

# rope bridges: (x0, x1, y_center, sprite) - sprite is drawn x0..x1 wide
BRIDGES = [
    (95.0, 113.0, 59.0, "bridge_short"),      # Echo Landing -> Troll Camp
    (42.0, 60.0, 90.0, "bridge_short"),       # Echo Landing -> Grotto
    (99.5, 126.5, 104.0, "bridge_long"),      # Echo Landing -> Hollow
]

# shallow fords: (waypoints, width)
FORDS = {
    "wreck":     ([(134, 41), (137, 36), (141, 31)], 5.0),
    "causeway":  ([(128, 69), (131, 78), (133, 86), (133, 93)], 5.2),
    "steps":     ([(27, 77), (28, 69), (27, 61)], 4.8),
    "razorjaw":  ([(66, 121), (64, 129), (62, 138)], 6.0),
}
# open shallow flats: (cx, cy, rx, ry)
FLATS = {
    "wreck":     (138, 36, 8, 5),
    "razorjaw":  (65, 130, 9, 7),
    "tidal":     (105, 128, 11, 7.5),
}

# timber piers / platforms: (x0, x1, y0, y1)
DECKS = [
    (77.6, 82.4, 2.0, 31.5),      # north pier
    (73.0, 87.0, 3.0, 12.0),      # north dock platform
    (77.6, 82.4, 128.5, 157.0),   # south pier
    (73.0, 87.0, 148.0, 157.0),   # south dock platform
]

# sea stacks / rock: (cx, cy, rx, ry)  - un-walkable rock rising from the water
STACKS = [(108, 20, 3, 4), (20, 122, 3.5, 3), (110, 146, 3, 3.5), (146, 140, 3, 3), (12, 22, 3, 3.5),
          (8, 70, 3, 3), (150, 76, 3, 3), (98, 10, 2.5, 3), (30, 150, 3, 3), (130, 140, 2.5, 2.5),
          (60, 6, 3, 2.5), (152, 56, 2.5, 3)]

# inland rock massifs on the islands: (cx, cy, rx, ry, rot_deg)
MASSIFS = [
    (66, 68, 6, 8, 12), (93, 82, 5, 7, -10), (73, 103, 6, 5, 0),            # Echo Landing
    (141, 110, 7, 6, 0),                                                    # Hollow (cave face)
    (22, 93, 7, 6, 0),                                                      # Grotto (cave face)
    (30, 44, 4, 5, 0),                                                      # Naga Ruins back wall
    (124, 49, 4, 5, 0),                                                     # Troll isle bluff
]

# footpaths (sand trails): (waypoints, width)
ROADS = {
    "north_pier": ([(80, 31), (80, 38), (79, 47)], 3.2),
    "village":    ([(79, 47), (80, 56), (79, 66)], 3.0),
    "east_trail": ([(80, 58), (90, 59), (97, 59)], 2.6),
    "west_trail": ([(79, 66), (70, 78), (62, 88), (58, 90)], 2.6),
    "south_trail": ([(79, 66), (82, 82), (80, 100), (80, 118), (80, 129)], 3.0),
    "hollow_trail": ([(82, 96), (92, 101), (99, 104)], 2.6),
    "flats_trail": ([(82, 110), (92, 116), (100, 122)], 2.4),
    "reef_trail": ([(72, 117), (68, 121)], 2.4),
    # troll isle
    "troll_in":   ([(112, 59), (118, 57), (124, 58)], 2.8),
    "troll_n":    ([(124, 58), (130, 50), (134, 42)], 2.6),
    "troll_s":    ([(124, 58), (126, 64), (128, 69)], 2.6),
    # hollow isle
    "hollow_w":   ([(125, 104), (131, 106), (134, 112)], 2.6),
    "hollow_n":   ([(133, 93), (134, 98), (134, 104)], 2.6),
    "hollow_cave": ([(134, 104), (136, 112), (141, 116)], 2.6),
    # grotto isle
    "grotto_in":  ([(43, 90), (36, 92), (28, 95), (24, 97)], 2.6),
    "grotto_n":   ([(34, 91), (30, 84), (27, 77)], 2.4),
    # naga ruins / fleet / reef
    "naga_in":    ([(27, 61), (26, 54), (24, 49)], 2.4),
    "fleet_in":   ([(141, 31), (143, 26), (146, 22)], 2.4),
    "reef_in":    ([(62, 138), (57, 140), (50, 139)], 2.4),
}

RIM_STEP = 0.0


def _wob(gx, gy):
    return (0.45 * np.sin(0.37 * gx + 1.3) * np.sin(0.29 * gy + 0.7)
            + 0.30 * np.sin(0.83 * gx + 0.21 * gy + 2.0)
            + 0.25 * np.sin(0.19 * gx - 0.57 * gy + 4.1))


def _ell(gx, gy, cx, cy, rx, ry, rot=0.0):
    dx, dy = gx - cx, gy - cy
    if rot:
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        dx, dy = c * dx + s * dy, -s * dx + c * dy
    r = np.sqrt((dx / rx) ** 2 + (dy / ry) ** 2)
    return (1 - r) * min(rx, ry)


_TREES = {}


def _poly_dist(key, pts, gx, gy):
    from scipy.spatial import cKDTree
    from tools.terrain_painter import Painter
    if key not in _TREES:
        _TREES[key] = cKDTree(Painter.spline(pts))
    d, _ = _TREES[key].query(np.stack([np.ravel(gx), np.ravel(gy)], 1))
    return d.reshape(np.shape(gx))


def road_dist(gx, gy, names=None):
    best = None
    for n in (names or ROADS):
        pts, w = ROADS[n]
        e = (w * 0.5) - _poly_dist(("road", n), pts, gx, gy)
        best = e if best is None else np.maximum(best, e)
    return best


def ford_field(gx, gy):
    """>0 inside any wadeable ford or flat (tiles)."""
    best = np.full(np.shape(gx), -99.0)
    for n, (pts, w) in FORDS.items():
        best = np.maximum(best, w * 0.5 - _poly_dist(("ford", n), pts, gx, gy))
    for n, (cx, cy, rx, ry) in FLATS.items():
        best = np.maximum(best, _ell(gx, gy, cx, cy, rx, ry))
    return best


def land_field(gx, gy):
    """>0 on dry land (tiles); smooth, wobbled shorelines."""
    w = 1.15 * _wob(gx, gy)
    best = np.full(np.shape(gx), -99.0)
    for blobs in ISLANDS.values():
        for (cx, cy, rx, ry) in blobs:
            best = np.maximum(best, _ell(gx, gy, cx, cy, rx, ry))
    return best + w


def deck_field(gx, gy):
    best = np.full(np.shape(gx), -9.0)
    for (x0, x1, y0, y1) in DECKS:
        e = np.minimum(np.minimum(gx - x0, x1 - gx), np.minimum(gy - y0, y1 - gy))
        best = np.maximum(best, e)
    return best


def bridge_field(gx, gy):
    """>0 on the walkable plank line of each rope bridge (2 tiles tall)."""
    best = np.full(np.shape(gx), -9.0)
    for (x0, x1, yc, _s) in BRIDGES:
        e = np.minimum(np.minimum(gx - (x0 + 1.5), (x1 - 1.5) - gx), 1.0 - np.abs(gy - (yc + 0.0)))
        best = np.maximum(best, e)
    return best


def rock_field(gx, gy, notch=True):
    """>0 inside un-walkable rock: sea stacks + inland massifs."""
    w = 1.0 * _wob(gx * 1.3, gy * 1.3)
    best = np.full(np.shape(gx), -99.0)
    for (cx, cy, rx, ry) in STACKS:
        best = np.maximum(best, _ell(gx, gy, cx, cy, rx, ry))
    for (cx, cy, rx, ry, rot) in MASSIFS:
        best = np.maximum(best, _ell(gx, gy, cx, cy, rx, ry, rot))
    best = best + w
    for (px, py) in ((GROTTO, HOLLOW) if notch else ()):
        notch = np.minimum(np.minimum(gx - (px - 2.2), (px + 3.2) - gx),
                           np.minimum(gy - (py - 6.0), (py + 1.6) - gy))
        best = np.where(notch > -0.2, -2.0, best)
    return best


def fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    land = land_field(gx, gy)
    wet = -land                                   # >0 = water
    ford = ford_field(gx, gy)
    deep = np.minimum(wet - SHORE_W, -ford)       # >0 = deep (fords cut shallow channels)
    return dict(land=land, wet=wet, deep=deep, ford=ford, deck=deck_field(gx, gy),
                bridge=bridge_field(gx, gy), rock=rock_field(gx, gy),
                rock_vis=rock_field(gx, gy, notch=False))


def tile_kind(gx, gy):
    """0 land, 1 shallow, 2 deep, 3 rock, 4 deck/bridge at tile centres."""
    f = fields(gx, gy)
    kind = np.zeros(np.shape(gx), int)
    kind[f["wet"] > 0] = 1
    kind[f["deep"] > 0] = 2
    kind[f["rock"] > 0] = 3
    kind[(f["deck"] > 0) | (f["bridge"] > 0)] = 4
    return kind


# ----------------------------------------------------------------- NPC spots
NPC_POSITIONS = {
    # Darkspear village (Echo Landing, north)
    "echo_isles_spirit_elder": (82, 52),
    "echo_isles_fisher": (76, 54),
    "echo_isles_net_mender": (84, 55),
    "echo_isles_camp_quartermaster": (77, 49),
    "echo_isles_camp_lookout": (83, 47),
    "echoisle_vendor": (82, 57),
    # Troll Camp isle
    "echo_isles_troll_beachcomber": (116, 56),
    "echo_isles_troll_healer": (121, 60),
    "echo_isles_troll_elder": (125, 54),
    # Hollow isle landing / Grotto isle
    "echo_isles_goblin_salvager": (130, 105),
    "echo_isles_shaman": (36, 87),
    "echo_isles_young_diver": (33, 95),
    # Tidal Flats cay
    "echo_isles_shipwreck_bones": (109, 129),
}
RECRUITS = {"carolina_shaman": (75, 50)}

_ASPECT = {}


def _aspect(path):
    if path not in _ASPECT:
        with Image.open(path) as im:
            _ASPECT[path] = im.size[0] / im.size[1]
    return _ASPECT[path]


class Layout:
    def __init__(self):
        self.zone = Tilemap("Echo Isles", W, H,
                            "A tropical archipelago off Durotar's coast: rope bridges, tidal fords "
                            "and drowned causeways link the Darkspear's islands.")
        self.z = self.zone
        self.z.region = "Durotar"
        self.skipped = []
        self.placed = 0
        self.npc_xy = []
        self.kind = None
        self.chests = []

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
            b = z.base_layer[y][x]
            if b == "deep_water" or (b == "shallow_water" and not shore_ok):
                return "water", core, ax, ay
            if b == "path" and self.kind is not None and self.kind[y, x] == 4 and not road_ok:
                return "deck", core, ax, ay
            if any(abs(x - nx) <= 1 and abs(y - ny) <= 1 for nx, ny in self.npc_xy):
                return "NPC", core, ax, ay
            if any(abs(x - px) <= 2 and abs(y - py) <= 2 for px, py in PORTAL_TILES):
                return "portal", core, ax, ay
            if not road_ok and not self.road_clear(x, y, 0.6):
                return "road", core, ax, ay
        return None, core, ax, ay

    def prop(self, name, cx, base_y, height, solid="core", fraction=0.4, road_ok=False,
             path_dir=DP, allow_overlap=False, shore_ok=False, nudge=2):
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

    def ep(self, name, cx, base_y, height, **kw):
        kw.setdefault("path_dir", EP)
        return self.prop(name, cx, base_y, height, **kw)

    def cave(self, cx, cy, sprite, w=7, h=5):
        self.z.add_landmark(f"{ENT}{sprite}.png", cx - w // 2, cy - h + 1, w, h, mouth_offset=(w // 2, h - 1))


PORTAL_TILES = [NORTH_DOCK, SOUTH_DOCK, GROTTO, HOLLOW]


def _terrain(L):
    z = L.z
    z.fill("grass", "base")
    ys, xs = np.mgrid[0:H, 0:W]
    gx, gy = xs + 0.5, ys + 0.5
    F = fields(gx, gy)
    kind = tile_kind(gx, gy)
    L.kind = kind
    rd = road_dist(gx, gy)
    for y in range(H):
        for x in range(W):
            k = kind[y, x]
            if k == 1:
                z.set_tile(x, y, "shallow_water", "base")
            elif k == 2:
                z.set_tile(x, y, "deep_water", "base")
            elif k == 3:
                # base stays dry ground so the engine draws no water shimmer over the rock
                z.set_tile(x, y, "sand", "base")
                z.set_tile(x, y, "cliff", "collision")
            elif k == 4:
                z.set_tile(x, y, "path", "base")
            elif F["land"][y, x] < 2.3:
                z.set_tile(x, y, "sand", "base")
            elif rd[y, x] > 0:
                z.set_tile(x, y, "path", "base")


def _portals(L):
    z = L.z
    for (px, py) in PORTAL_TILES:
        z.collision_layer[py][px] = None
        z.set_tile(px, py, "portal", "interaction")


BRIDGE_SPRITE_H = {"bridge_short": 6, "bridge_long": 5}

# land subzones (rect x,y,w,h) and shallow-water subzones (same rect, only on shallow tiles)
LAND_SUBZONES = [
    ("Troll Camps", 111, 39, 36, 34),
    ("Razorjaw Reef", 31, 128, 33, 22),
    ("Naga Ruins", 10, 36, 32, 26),
    ("The Lost Fleet", 133, 9, 28, 26),
]
WATER_SUBZONES = [
    ("Wreck Shallows", 127, 26, 20, 20, "Wreck Shallows"),
    ("Drowned Causeway", 120, 62, 20, 36, "Drowned Causeway"),
    ("Sunken Steps", 18, 56, 20, 26, "Sunken Steps"),
    ("Razorjaw Shallows", 55, 112, 22, 30, "Razorjaw Shallows"),
    ("Tidal Flats", 90, 114, 30, 24, "Tidal Flats"),
]


def _bridges(L):
    for (x0, x1, yc, sprite) in BRIDGES:
        wt = int(round(x1 - x0))
        ht = BRIDGE_SPRITE_H[sprite]
        L.z.add_landmark(f"{BR}{sprite}.png", int(round(x0)), int(round(yc)) - ht // 2 - 0, wt, ht, solid=False)


def _caves(L):
    L.cave(GROTTO[0], GROTTO[1], "entrance_dark_blue")
    L.cave(HOLLOW[0], HOLLOW[1], "entrance_dark_mossy")
    # arrival column: the cave exits drop you 2 tiles north of the mouth
    for (px, py) in (GROTTO, HOLLOW):
        for dy in (1, 2, 3):
            L.z.collision_layer[py - dy][px] = None


def _subzones(L):
    z = L.z
    z.add_subzone("Echo Isles", 0, 0, W, H, display_name="Echo Landing")
    for key, x, y, w, h in LAND_SUBZONES:
        z.add_subzone(key, x, y, w, h)
    for key, x, y, w, h, disp in WATER_SUBZONES:
        z.add_subzone(key, x, y, w, h, display_name=disp, base_tiles=("shallow_water",))


def _seal_unreachable(L, start=(80, 12)):
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
    sealed = 0
    for y in range(H):
        for x in range(W):
            if (x, y) not in seen and z.is_walkable(x, y):
                if z.base_layer[y][x] == "shallow_water":
                    z.set_tile(x, y, "deep_water", "base")
                else:
                    z.set_tile(x, y, "cliff", "collision")
                sealed += 1
    L.sealed = sealed


def _dress(L):
    pass


def build_layout():
    L = Layout()
    _terrain(L)
    _portals(L)
    _bridges(L)
    _caves(L)
    _subzones(L)
    _dress(L)
    _seal_unreachable(L)
    return L


def register_baked(zone, baked_dir=BAKED_DIR, chunk=20):
    for cy in range(0, H, chunk):
        for cx in range(0, W, chunk):
            fn = f"{baked_dir}/ground_{cx}_{cy}.jpg"
            if not os.path.exists(fn):
                raise FileNotFoundError(f"{fn} - run python3 tools/bake_echo_isles.py")
            w, h = min(chunk, W - cx), min(chunk, H - cy)
            zone.add_ground_chunk(fn, cx, cy, w, h)
            zone.ground_chunks[-1]["exact"] = True
            zone.add_water_chunk(fn, cx, cy, w, h)
            zone.add_obstacle_chunk(fn, cx, cy, w, h)


def generate_echo_isles():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=6):
    ys, xs = np.mgrid[0:H, 0:W]
    kind = tile_kind(xs + 0.5, ys + 0.5)
    pal = {0: (90, 150, 70), 1: (110, 200, 210), 2: (25, 70, 110), 3: (80, 75, 70), 4: (150, 105, 55)}
    img = np.zeros((H, W, 3), np.uint8)
    for k, c in pal.items():
        img[kind == k] = c
    rd = road_dist(xs + 0.5, ys + 0.5)
    img[(rd > 0) & (kind == 0)] = (225, 200, 140)
    for (px, py) in PORTAL_TILES:
        img[py, px] = (255, 0, 255)
    Image.fromarray(img).resize((W * scale, H * scale), Image.NEAREST).save(path)
