"""
Hand-built Central Barrens (300x300): the golden heart of the Barrens.

Same recipe as Durotar / Echo Isles (see claude/zone_perfection_playbook.md):
  * this module owns the TILE data (walkability, props, portals, subzones) and the
    analytic landform fields (`fields`) the baker paints from, so the painting and the
    collision grid can never drift apart;
  * tools/bake_central_barrens.py turns the same fields into one continuous painting.

COMPOSITION (tile coords, y down).  The Crossroads gate sits dead centre (150,150); every
road leads to it.
    Gold Road ........ N-S spine x~150, N pass (150,3) -> Northern Barrens, S pass (150,296) -> Taurajo
    Durotar Road ..... Southfury bridge (246-262, y30) -> long diagonal SW through Kolkar Plains
    Ratchet Road ..... SE past Raider's Rest to the Ratchet pier (264-290, y270)
    Trade Road West .. Grol'dom Farm, Shrine of the Fallen Warrior
    Wailing Road ..... SW to Lushwater Oasis; cave mouth (75,223) in the bluff south of the lake
    Pools Road ....... NW to the Forgotten Pools, on to the Dreadmist range and the Den
    Dreadmist range .. NW massif (5-72, 3-60) with a hidden box canyon (the Den) at (50,44)
    Kolkar Plains .... E; Kodo Graveyard (205,120); Warcamp (238,112); Outpost (222,160)
    Quilboar camps ... Bramblescar (130,250) / Agama'gor (170,250) flanking the south Gold Road
    Dry riverbeds .... Shrine Wash (Dreadmist -> Lushwater) and Pools Wash (Pools -> Raider's Rest)

HARD CONTRACTS (world/portal_manager.py):
    portals  Northern Barrens (150,4)  Durotar (270,30)  Crossroads (150,150)
             Wailing Caverns (75,223)  Ratchet (285,270)  Camp Taurajo (150,296)
    arrivals are 2 tiles NORTH of the portal tile (cave exits land 1 south of it).
"""
import math
import os

import numpy as np
from PIL import Image
from scipy.spatial import cKDTree

from world.tilemap import Tilemap

BP = "assets/tiles/barrens/props/"
DP = "assets/tiles/dungeon_props/"
BLD = "assets/buildings/"
ENT = "assets/tiles/cave_entrances/"
CP = "assets/tiles/coastal_props/"
BR = "assets/tiles/bridges/"
BAKED_DIR = "assets/tiles/central_barrens/baked"
W, H = 300, 300

PORTALS = {
    (150, 4): "Northern Barrens", (270, 30): "Durotar", (150, 150): "Crossroads",
    (75, 223): "Wailing Caverns", (285, 270): "Ratchet", (150, 296): "Camp Taurajo",
}
ARRIVALS = [(150, 2), (270, 28), (150, 148), (75, 224), (285, 268), (150, 294)]

# ---------------------------------------------------------------- the plan
# roads: waypoints (tile coords), width in tiles
ROADS = {
    # Gold Road: one long meandering spine; every other road BRANCHES off it (Y-junctions),
    # only the E-W trade road actually crosses it at the Crossroads.
    "gold_n":   ([(150, 3), (150, 16), (146, 32), (138, 50), (137, 70), (146, 88), (156, 104),
                  (156, 122), (151, 138)], 3.6),
    "gold_s":   ([(150, 162), (152, 178), (158, 196), (160, 214), (152, 230), (150, 246), (150, 266),
                  (150, 282), (150, 295)], 3.6),
    "plaza":    ([(150, 136), (150, 164)], 3.6),
    "durotar_e": ([(270, 31), (262, 30), (246, 30)], 3.0),
    "durotar":  ([(246, 30), (236, 38), (224, 52), (214, 72), (204, 90), (190, 104), (174, 114),
                  (162, 119), (156, 122)], 3.2),
    "kolkar":   ([(214, 72), (226, 82), (237, 93), (240, 108)], 2.4),
    "east":     ([(150, 150), (164, 152), (178, 150), (192, 153), (206, 158), (220, 160)], 2.8),
    "west":     ([(150, 150), (144, 150), (128, 153), (112, 147), (100, 150), (86, 146), (70, 144),
                  (56, 141), (49, 141)], 3.2),
    "farm":     ([(86, 146), (86, 138)], 2.4),
    "ratchet":  ([(158, 197), (172, 194), (190, 190), (210, 194), (230, 196), (244, 204), (248, 220),
                  (250, 238), (258, 254), (263, 268), (268, 270)], 3.2),
    "raiders":  ([(204, 194), (205, 206), (206, 216)], 2.4),
    "wailing":  ([(152, 178), (140, 186), (126, 194), (112, 206), (98, 218), (86, 224), (76, 225)], 3.0),
    "pools":    ([(137, 70), (124, 74), (110, 80), (100, 86), (92, 88)], 3.0),
    "dreadmist": ([(74, 72), (66, 64), (60, 57), (55, 51)], 2.4),
    "brambles": ([(150, 238), (140, 242), (132, 247)], 2.4),
    "agama":    ([(150, 238), (160, 242), (168, 247)], 2.4),
}

# decks laid over water: (x0, x1, y0, y1)
DECKS = [
    (246.0, 262.0, 28.6, 31.4),     # Southfury bridge
    (264.0, 291.0, 268.6, 271.4),   # Ratchet pier
    (280.0, 291.0, 265.5, 274.5),   # pier-head platform (arrival tile (285,268))
]

# cliff massifs: (cx, cy, rx, ry, rot_deg) --------------------------------
# Only formations big enough to read as landforms; small rocks are PROPS (spires, boulders).
MESAS = [
    # Dreadmist range (NW) - a ring of massifs around a box canyon (the Den at 50,44)
    (16, 16, 15, 12, 10), (40, 11, 14, 8, -8), (60, 17, 11, 9, 12), (72, 34, 7, 14, 0),
    (20, 42, 12, 15, -6), (33, 44, 6, 11, 0), (47, 31, 13, 5.5, 0), (66, 45, 5.5, 10, 0),
    (40, 60, 11, 5, 0), (22, 68, 9, 8, 0), (8, 55, 8, 12, 0),
    # Wailing bluff south of Lushwater (cave face at 75,223)
    (75, 214, 19, 5.5, 0), (53, 220, 6, 8, 0), (98, 222, 6, 7, 0), (72, 244, 16, 6, 0),
    # Northern pass flanks (Gold Road gate)
    (127, 12, 12, 8, 4), (174, 14, 14, 9, 0), (116, 4, 8, 5, 0), (186, 5, 7, 4, 0),
    # Southern pass flanks (Taurajo gate)
    (123, 284, 15, 9, 6), (179, 288, 12, 7, -8),
    # tilted formations (each a pair, long axis varying) - not round blobs
    (108, 58, 9, 4.5, -22), (118, 63, 5, 3, 12),
    (28, 100, 7, 4.5, 68), (24, 111, 4, 3, 20),
    (96, 168, 8, 4, -24), (105, 174, 4, 3, 10),
    (176, 228, 9, 4.5, 14), (187, 234, 4.5, 3, -10),
    (234, 176, 7.5, 4, 32), (243, 183, 4, 3, 0),
    # Fallen Warrior bluff (the shrine sits in its lee)
    (38, 124, 8, 5, 0), (60, 132, 5, 3.5, 0),
]

# long ridges: (waypoints, half-width) - tapered at both ends
RIDGES = [
    ([(196, 18), (203, 32), (209, 48), (211, 56)], 3.0),               # Kolkar escarpment, north
    ([(212, 80), (214, 98), (218, 118), (222, 136), (222, 148)], 3.2),  # Kolkar escarpment, south
    ([(114, 102), (118, 93), (126, 87), (135, 86)], 3.7),               # Sentinel ridge, west arm
    ([(172, 94), (181, 99), (185, 108), (183, 118)], 3.5),              # Sentinel ridge, east arm
    ([(104, 252), (118, 262), (132, 268)], 2.4),                        # Bramblescar bluff
    ([(196, 252), (182, 262), (168, 268)], 2.4),                        # Agama'gor bluff
    ([(40, 148), (46, 160), (54, 172)], 2.4),                           # Shrine ridge
    ([(226, 236), (234, 248), (240, 264)], 2.8),                        # Raider's Rest scarp
    ([(12, 238), (24, 250), (38, 266), (56, 280)], 3.2),                # south-west scarp
    ([(14, 120), (18, 138), (13, 158)], 2.6),                           # far-west shelf
]

# gaps carved through the above/rim: ("ell", cx, cy, rx, ry)
GAPS = [
    ("ell", 150, 3, 11, 9),          # Northern pass (Gold Road gate)
    ("ell", 150, 295, 11, 9),        # Southern pass (Taurajo gate)
    ("ell", 150, 150, 15, 15),       # Crossroads plaza
    ("ell", 270, 30, 7, 7),          # Durotar landing
    ("ell", 285, 270, 8, 8),         # Ratchet pier-head
    ("ell", 75, 226, 7, 5),          # Wailing Caverns mouth landing
    ("ell", 50, 44, 8, 6.5),         # Dreadmist Den floor
    ("ell", 56, 52, 4.5, 6),         # Den approach
    ("ell", 90, 88, 6, 5),           # Pools landing
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
        e = (w * 0.5) - d
        best = e if best is None else np.maximum(best, e)
    return best.reshape(np.shape(gx))


def _wob(gx, gy):
    return (0.45 * np.sin(0.37 * gx + 1.3) * np.sin(0.29 * gy + 0.7)
            + 0.30 * np.sin(0.83 * gx + 0.21 * gy + 2.0)
            + 0.25 * np.sin(0.19 * gx - 0.57 * gy + 4.1))


def _smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def blob(gx, gy, cx, cy, rx, ry, rot=0.0, ph=0.0, wob=0.10):
    """Organic ellipse: >0 inside (tiles).  Integer harmonics only (no seams)."""
    dx, dy = gx - cx, gy - cy
    if rot:
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        dx, dy = c * dx + s * dy, -s * dx + c * dy
    a = np.arctan2(dy / ry, dx / rx)
    r = np.sqrt((dx / rx) ** 2 + (dy / ry) ** 2)
    k = 1 + wob * np.sin(3 * a + ph) + 0.6 * wob * np.sin(5 * a + 2 * ph)
    return (1 - r / k) * min(rx, ry)


# ------------------------------------------------------------ water shapes
# lakes: name -> list of (cx, cy, rx, ry, rot, phase) shallow shapes; deep = shrunk copy
LAKES = {
    "lushwater": [(75, 198, 17, 10.5, 0, 0.6)],
    "raiders":   [(222, 216, 16, 10, 8, 2.1)],
    "pools":     [(71, 74, 7.5, 5.5, 10, 0.3), (92, 82, 7.5, 6, -12, 1.4), (79, 94, 6.5, 4.8, 0, 2.6),
                  (62, 88, 5, 3.8, 20, 3.4), (100, 98, 4.5, 3.4, 0, 4.2)],
}
DEEP_SHRINK = {"lushwater": 3.6, "raiders": 4.0, "pools": 2.4}
ISLANDS = [(226, 214, 4.0, 2.8, 0, 1.0)]       # Raider's Rest island (land inside the lake)


def _gauss(gy, c, w):
    return np.exp(-((gy - c) / w) ** 2)


def coast_x(gy):
    """East shore: headlands and bays (the Ratchet spit hooks out in the south)."""
    spit = 15.0 * _smooth(246, 262, gy) * (1 - _smooth(284, 296, gy))
    swing = (-8.0 * _gauss(gy, 88, 15) + 5.0 * _gauss(gy, 128, 12) - 8.0 * _gauss(gy, 176, 15)
             + 4.0 * _gauss(gy, 214, 11) - 3.0 * _gauss(gy, 240, 6))
    swing = swing * _smooth(56, 72, gy)
    return 257.0 + swing + 1.8 * np.sin(0.19 * gy) + 1.2 * np.sin(0.53 * gy + 1.0) + spit


def river_c(gy):
    return 254.0 + 1.6 * np.sin(0.21 * gy + 0.4) + 0.8 * np.sin(0.47 * gy)


def river_hw(gy):
    return (4.2 + 0.5 * np.sin(0.13 * gy + 1.0)) * (1 - _smooth(52, 60, gy))


def bank_south(gx):
    return 48.0 + 3.0 * np.sin(0.13 * gx + 0.5) + 1.4 * np.sin(0.41 * gx)


def water_fields(gx, gy):
    """(shallow_extent, deep_extent): >0 inside, in tiles."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    # sea: east of the coast, but the NE (Durotar) bank stays land
    sea = gx - coast_x(gy)
    bank = np.minimum(np.minimum(gx - (river_c(gy) + 4.4), 292.0 + 1.5 * np.sin(0.31 * gy) - gx),
                      bank_south(gx) - gy)
    sea = np.minimum(sea, -bank)
    sea = np.maximum(sea, gx - (293.5 + 1.5 * np.sin(0.31 * gy)))       # far-east sea
    sea_d = sea - 3.4
    # river
    r_s = river_hw(gy) - np.abs(gx - river_c(gy))
    r_s = np.where(gy < 62, r_s, -9.0)
    r_d = r_s - 2.2 + 7.0 * _smooth(26, 10, gy)     # fully deep (impassable) towards the north
    sh = np.maximum(sea, r_s)
    dp = np.maximum(sea_d, r_d)
    # lakes
    for key, shapes in LAKES.items():
        for (cx, cy, rx, ry, rot, ph) in shapes:
            s = blob(gx, gy, cx, cy, rx, ry, rot, ph)
            d = blob(gx, gy, cx, cy, rx, ry, rot, ph) - DEEP_SHRINK[key] * (0.6 if key == "pools" else 1.0)
            sh = np.maximum(sh, s)
            dp = np.maximum(dp, d)
    for (cx, cy, rx, ry, rot, ph) in ISLANDS:
        isl = blob(gx, gy, cx, cy, rx, ry, rot, ph)
        sh = np.minimum(sh, -isl)
        dp = np.minimum(dp, -isl)
    return sh, dp


def deck_field(gx, gy):
    best = np.full(np.shape(gx), -9.0)
    for (x0, x1, y0, y1) in DECKS:
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
    best = np.maximum(best, road_dist(gx, gy) + 2.4)
    best = np.maximum(best, deck_field(gx, gy) + 1.5)
    return best


_RIDGE_TREES = {}


def _ridge(pts, hw, gx, gy):
    key = id(pts)
    if key not in _RIDGE_TREES:
        from tools.terrain_painter import Painter
        _RIDGE_TREES[key] = cKDTree(Painter.spline(pts))
    tree = _RIDGE_TREES[key]
    d, idx = tree.query(np.stack([gx.ravel(), gy.ravel()], 1))
    t = idx / max(1, tree.n - 1)
    taper = 0.30 + 0.70 * np.sin(np.pi * t) ** 0.6
    return (hw * taper).reshape(gx.shape) + 0.7 * _wob(gx, gy) - d.reshape(gx.shape)


def cliff_raw(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
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
    west = (7.5 + 3.4 * np.sin(0.045 * gy + 0.4) + 1.6 * np.sin(0.13 * gy + 1.0) + 0.8 * np.sin(0.37 * gy)) - gx
    north = (6.0 + 2.4 * np.sin(0.05 * gx + 1.0) + 1.2 * np.sin(0.11 * gx) + 0.7 * np.sin(0.31 * gx + 1.0)) - gy
    south = gy - (293.0 - 2.4 * np.sin(0.06 * gx + 2.0) - 1.0 * np.sin(0.13 * gx) - 0.7 * np.sin(0.29 * gx + 2.0))
    out = np.maximum(out, np.maximum(west, np.maximum(north, south)))
    return out + 1.1 * _wob(gx, gy)


def fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    sh, dp = water_fields(gx, gy)
    cl = np.minimum(cliff_raw(gx, gy), -gap_extent(gx, gy))
    return dict(cliff=cl, shallow=sh, deep=dp, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    """0 land, 1 shallow, 2 deep, 3 cliff, 4 deck at tile centres (arrays)."""
    f = fields(gx, gy)
    kind = np.zeros(np.shape(gx), int)
    kind[f["shallow"] > 0] = 1
    kind[f["deep"] > 0] = 2
    kind[(f["cliff"] > 0) & (kind == 0)] = 3
    kind[f["cliff"] > 1.5] = 3
    kind[f["deck"] > 0] = 4
    return kind


# ------------------------------------------------------- painted-only fields
# (no collision): dry riverbeds, oasis rims, camp earth, thorn litter, farm tilth.
WASHES = {
    "shrine_wash": ([(40, 66), (34, 84), (30, 104), (36, 122), (46, 138), (56, 156), (64, 176), (70, 190)], 3.4),
    "pools_wash":  ([(98, 100), (116, 118), (134, 138), (140, 148), (160, 166), (184, 184), (204, 198),
                     (212, 206)], 3.0),
}

CAMP_PATCHES = {   # name -> (cx, cy, rx, ry): trampled camp earth
    "kolkar_war": (238, 112, 11, 8), "kolkar_out": (222, 160, 9, 7),
    "brambles": (130, 252, 11, 8), "agamagor": (170, 252, 11, 8),
    "raiders": (206, 218, 8, 6), "farm": (85, 146, 12, 8), "den": (50, 44, 9, 6),
    "dorn": (182, 152, 5, 4), "crossroads": (150, 150, 11, 9), "shrine": (50, 140, 7, 6), "wc": (75, 226, 7, 4),
    "durotar": (270, 30, 8, 7), "southfury": (258, 36, 5, 4), "kodo_yard": (205, 120, 10, 7),
}


def wash_dist(gx, gy):
    from tools.terrain_painter import Painter
    best = None
    q = np.stack([np.ravel(gx), np.ravel(gy)], 1)
    for name, (pts, w) in WASHES.items():
        tree = cKDTree(Painter.spline(pts))
        d, _ = tree.query(q)
        e = w * 0.5 + 0.8 * _wob(np.ravel(gx), np.ravel(gy)) - d
        best = e if best is None else np.maximum(best, e)
    return best.reshape(np.shape(gx))


# --------------------------------------------------------------- NPC spots
# id -> (x, y).  Existing ids are kept (quests reference ids, never coordinates).
NPC_POSITIONS = {
    "barrens_herder_1": (142, 83),       # Herder Magra, under the Sentinel Rocks
    "barrens_scout_2": (182, 154),       # Plainswatcher Dorn, east road
    "groldom_farmer": (85, 148),         # Kranal Fiss, Grol'dom Farm
    "cb_waterkeeper": (88, 207),         # Waterkeeper Sanu, Lushwater
    "cb_pools_warden": (96, 95),         # Pilgrim-Warden Torga, Forgotten Pools
    "cb_caravan_master": (203, 218),     # Caravan-Master Dogan, Raider's Rest
    "cb_shrine_keeper": (52, 144),       # Keeper Ahnmar, Shrine of the Fallen Warrior
    "cb_dreadmist_scout": (66, 61),      # Scout Zarla, Dreadmist road
    "cb_quilboar_ranger": (146, 234),    # Ranger Kishi, between the quilboar camps
    "cb_bridgewarden": (262, 34),        # Bridgewarden Karga, Durotar landing
}

CAVES = {   # portal tile -> (sprite, w, h)
    (75, 223): ("ent_wailing_maw", 9, 7),
}

_ASPECT = {}


def _aspect(path):
    if path not in _ASPECT:
        with Image.open(path) as im:
            _ASPECT[path] = im.size[0] / im.size[1]
    return _ASPECT[path]


class Layout:
    # parametric hooks so other hand-built zones (Southern Barrens) can reuse the placement logic
    W, H = W, H
    portal_tiles = list(PORTALS)
    arrival_tiles = list(ARRIVALS)

    def road_fn(self, gx, gy):
        return road_dist(gx, gy)

    def __init__(self):
        self.zone = Tilemap("Central Barrens", W, H,
                            "Golden savanna stretching to every horizon. The Crossroads stands at the heart of it all.")
        self.z = self.zone
        self.z.region = "Kalimdor - Central"
        self.skipped = []
        self.chests = []
        self.placed = 0
        self.npc_xy = list(NPC_POSITIONS.values())

    def road_clear(self, x, y, margin=0.9):
        return self.road_fn(np.array([x + 0.5]), np.array([y + 0.5]))[0] < -margin

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
            if not (0 <= x < self.W and 0 <= y < self.H):
                return "off-map", core, ax, ay
            if z.collision_layer[y][x] is not None and not allow_overlap:
                return "overlaps solid", core, ax, ay
            if z.base_layer[y][x] == "deep_water" or (z.base_layer[y][x] == "shallow_water" and not shore_ok):
                return "water", core, ax, ay
            if any(abs(x - nx) <= 1 and abs(y - ny) <= 1 for nx, ny in self.npc_xy):
                return "NPC", core, ax, ay
            if any(abs(x - px) <= 2 and abs(y - py) <= 2 for px, py in self.portal_tiles + self.arrival_tiles):
                return "portal", core, ax, ay
            if not road_ok and not self.road_clear(x, y, 0.6):
                return "road", core, ax, ay
        return None, core, ax, ay

    def prop(self, name, cx, base_y, height, solid="core", fraction=0.4, road_ok=False,
             path_dir=BP, allow_overlap=False, shore_ok=False, nudge=3):
        """Sprite `name` with bottom-centre on (cx, base_y).  solid: False decor | True whole
        footprint | "core" base only.  Spot taken -> nearest free spot within `nudge`, else logged."""
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

    def deco(self, name, cx, base_y, height, path_dir=CP):
        """Purely visual sprite (no collision, no checks) - dock furniture over water."""
        path = f"{path_dir}{name}.png"
        wt = max(1, round(height * _aspect(path)))
        self.z.add_landmark(path, cx - wt // 2, base_y - height + 1, wt, height, solid=False)

    def bld(self, name, cx, base_y, height, **kw):
        kw["path_dir"] = BLD
        kw.setdefault("fraction", 0.5)
        return self.prop(name, cx, base_y, height, **kw)

    def dp(self, name, cx, base_y, height, **kw):
        kw["path_dir"] = DP
        return self.prop(name, cx, base_y, height, **kw)

    def cp(self, name, cx, base_y, height, **kw):
        kw["path_dir"] = CP
        return self.prop(name, cx, base_y, height, **kw)

    def row(self, name, xs, base_y, height, **kw):
        return sum(bool(self.prop(name, x, base_y, height, **kw)) for x in xs)

    def cave(self, cx, cy, sprite, w=6, h=4):
        self.z.add_landmark(f"{ENT}{sprite}.png", cx - w // 2, cy - h + 1, w, h, mouth_offset=(w // 2, h - 1))

    def chest(self, x, y):
        z = self.z
        for r in range(0, 6):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    xx, yy = x + dx, y + dy
                    if (0 <= xx < self.W and 0 <= yy < self.H and z.is_walkable(xx, yy)
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
    z.fill("dirt", "base")
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


def _seal_unreachable(L, start=(150, 152)):
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


SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("Kolkar Plains", 190, 20, 100, 200, None),
    ("Southfury Banks", 256, 0, 44, 52, None),
    ("Kolkar Outpost", 206, 144, 36, 32, None),
    ("Kodo Graveyard", 188, 104, 34, 30, None),
    ("Kolkar War Camp", 222, 94, 36, 34, None),
    ("Sentinel Rocks", 108, 80, 76, 36, None),
    ("Dreadmist Peak", 5, 3, 68, 58, None),
    ("The Forgotten Pools", 55, 62, 52, 48, None),
    ("Lushwater Oasis", 50, 180, 52, 42, None),
    ("Raider's Rest Oasis", 198, 196, 54, 40, None),
    ("Grol'dom Farm", 71, 133, 28, 24, None),
    ("Shrine of the Fallen Warrior", 40, 130, 20, 20, None),
    ("Bramblescar", 116, 238, 28, 24, None),
    ("Agama'gor", 156, 238, 28, 24, None),
    ("Dreadmist Den", 40, 37, 20, 14, None),
]


def _subzones(L):
    for key, x, y, w, h, disp in SUBZONES:
        L.z.add_subzone(key, x, y, w, h, display_name=disp)


# ------------------------------------------------------------------ dressing
def _grove(L, items, cx, cy, rx, ry, n, seed, gap=4.0, **kw):
    """Deliberate cluster: n props from `items` [(name, height)] jittered inside a hand-placed
    ellipse, keeping `gap` tiles between members.  Deterministic per seed."""
    import random
    rnd = random.Random(seed)
    pts, tries = [], 0
    while len(pts) < n and tries < n * 40:
        tries += 1
        a, r = rnd.uniform(0, 6.2832), math.sqrt(rnd.random())
        x, y = cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)
        if all((x - px) ** 2 + (y - py) ** 2 >= gap * gap for px, py in pts):
            pts.append((x, y))
    for (x, y) in pts:
        name, h = items[rnd.randrange(len(items))]
        L.prop(name, int(round(x)), int(round(y)), h, **kw)


ACACIAS = [("acacia_tree", 8), ("br_umbrella_acacia", 7)]
SCRUB = [("br_thorn_scrub", 3), ("br_agave_spike", 3), ("barrens_cactus", 4)]
TUFTS = [("br_golden_grass_tuft", 2)]
ROCKS = [("br_sandstone_boulders", 4), ("br_mossy_boulder", 3)]
BONES = [("br_tumbleweed_bones", 3), ("br_driftwood_skull", 3), ("kodo_skull", 3)]


def dress(L):
    P = L.prop
    # bridges (side-on art, E-W): Southfury over the river, the Ratchet pier over the sea
    L.z.add_landmark(BR + "bridge_long.png", 246, 28, 16, 3, solid=False)
    L.z.add_landmark(BR + "bridge_plank.png", 264, 268, 27, 3, solid=False)

    # ---- gates & portal landmarks -----------------------------------------
    # North pass: a kodo-tusk gate arched over the Gold Road, totems either side
    P("br_kodo_tusk_gate", 150, 12, 7, solid=False, road_ok=True)
    P("br_tauren_totem", 143, 9, 7)
    P("br_tauren_totem", 158, 9, 7)
    P("br_signpost", 155, 15, 5)
    # South pass (Taurajo): tauren side
    P("br_tauren_totem", 143, 290, 7)
    P("br_tauren_totem", 158, 290, 7)
    P("br_signpost", 154, 286, 5)
    P("br_kodo_skeleton", 140, 281, 4)
    # Crossroads gate: twin watchtowers, trough, wagon
    P("br_crossroads_watchtower", 139, 146, 9)
    P("br_crossroads_watchtower", 161, 146, 9)
    P("br_hitching_trough", 143, 141, 3)
    P("br_caravan_wagon", 158, 140, 4)
    P("br_signpost", 146, 135, 5)
    L.bld("palisade_gatehouse", 150, 143, 7, solid=False, road_ok=True)
    # Durotar landing
    P("br_crossroads_watchtower", 278, 24, 9)
    L.bld("guard_post", 265, 37, 5)
    P("br_caravan_wagon", 273, 40, 4)
    P("br_signpost", 263, 26, 5)
    P("br_agave_spike", 283, 33, 3)
    P("br_agave_spike", 268, 22, 3)
    # Ratchet pier head
    L.bld("harbor_tower", 262, 261, 7)
    L.bld("ratchet_docks_warehouse", 268, 263, 5, shore_ok=True)
    L.deco("fish_crates_traps", 289, 274, 3)
    L.deco("mooring_posts", 270, 272, 3)
    L.deco("dock_lantern_post", 273, 269, 4)
    L.deco("dock_lantern_post", 280, 266, 4)
    L.deco("dock_lantern_post", 289, 266, 4)
    L.deco("dock_lantern_post", 282, 274, 4)
    L.cp("driftwood_pile", 260, 262, 3, shore_ok=True)
    # Wailing Caverns mouth: serpent shrine, bones, raptor nest
    P("br_wc_serpent_shrine", 65, 227, 7)
    P("br_tumbleweed_bones", 84, 228, 3)
    P("br_vulture_roost", 88, 224, 4)
    P("br_raptor_nest", 62, 232, 3)
    P("br_thorn_scrub", 69, 230, 3)

    # ---- Sentinel Rocks (north of the Crossroads) --------------------------
    P("br_sandstone_arch", 130, 104, 6, solid="core", fraction=0.3)
    P("br_sandstone_spire", 122, 97, 7)
    P("br_sandstone_spire", 138, 91, 7)
    P("br_sandstone_spire", 173, 114, 7)
    P("br_sandstone_arch", 166, 108, 6, solid="core", fraction=0.3)

    # ---- Kolkar war camp (238,112) -----------------------------------------
    P("br_kolkar_tent", 232, 108, 6)
    P("br_kolkar_tent", 244, 106, 6)
    P("br_kolkar_tent", 249, 115, 6)
    P("br_kolkar_tent", 227, 116, 6)
    P("br_kolkar_tent", 238, 121, 6)
    L.dp("vot_fire_pit", 238, 113, 2, solid=False)
    L.dp("vot_war_drum", 241, 117, 3)
    L.dp("vot_war_banner", 233, 113, 5)
    L.dp("vot_war_banner", 244, 112, 5)
    L.dp("vot_totem_pole", 238, 105, 6)
    L.dp("vot_hide_rack", 230, 122, 3)
    L.dp("vot_palisade", 231, 102, 3)
    L.dp("vot_palisade", 247, 102, 3)
    P("br_kodo_tusk_gate", 238, 98, 7, solid=False, road_ok=True)
    P("br_tauren_totem", 232, 97, 7)
    P("br_tauren_totem", 245, 97, 7)
    # Kolkar outpost (222,160)
    P("br_kolkar_tent", 218, 156, 6)
    P("br_kolkar_tent", 227, 158, 6)
    P("br_kolkar_tent", 220, 166, 6)
    P("br_crossroads_watchtower", 214, 150, 9)
    L.dp("vot_fire_pit", 222, 161, 2, solid=False)
    L.dp("vot_hide_rack", 228, 165, 3)
    P("br_caravan_wagon", 212, 164, 4)
    # Kodo graveyard (205,120)
    for (x, y, n, h) in [(200, 118, "br_kodo_skeleton", 4), (209, 123, "br_kodo_skeleton", 4),
                         (196, 126, "br_kodo_skeleton", 4), (206, 114, "br_kodo_skeleton", 4),
                         (212, 118, "kodo_skull", 3), (202, 128, "kodo_skull", 3),
                         (193, 118, "br_vulture_roost", 4), (214, 127, "br_vulture_roost", 4),
                         (199, 111, "br_dead_tree_vulture", 7), (210, 108, "br_dead_tree_vulture", 7),
                         (190, 124, "br_dead_tree_vulture", 7)]:
        P(n, x, y, h)
    L.dp("vot_beast_ribcage", 204, 121, 3)
    _grove(L, BONES, 205, 121, 12, 8, 6, 11, gap=3.5, solid=False)

    # ---- quilboar camps: Razormane (thorn-and-bramble hold) vs Bristleback (bone-and-tusk warren) ----
    for (x, y) in [(123, 246), (133, 244), (126, 255), (139, 253), (131, 260)]:
        P("br_quilboar_hut", x, y, 6)
    L.dp("vot_fire_pit", 131, 252, 2, solid=False)
    L.dp("vot_hide_rack", 137, 249, 3)
    P("br_termite_mound", 121, 258, 5)
    P("br_razorfen_bramble_gate", 131, 238, 6, solid=False, road_ok=True)
    _grove(L, [("br_thorn_scrub", 3), ("br_agave_spike", 3)], 130, 254, 15, 10, 7, 130, gap=4.0)
    for (x, y) in [(177, 245), (167, 243), (174, 254), (163, 252), (170, 260)]:
        P("br_quilboar_hut", x, y, 6)
    L.dp("vot_fire_pit", 170, 251, 2, solid=False)
    L.dp("vot_hide_rack", 163, 247, 3)
    L.dp("vot_beast_ribcage", 178, 253, 3)
    P("br_vulture_roost", 160, 258, 4)
    P("br_kodo_skeleton", 182, 258, 4)
    P("br_kodo_tusk_gate", 170, 238, 7, solid=False, road_ok=True)
    _grove(L, BONES + [("br_sandstone_boulders", 4)], 170, 254, 15, 10, 6, 170, gap=4.5)
    P("br_razorfen_bramble_gate", 140, 241, 6, solid=False, road_ok=True)

    # ---- Raider's Rest (south-east oasis) ------------------------------------
    for (x, y) in [(213, 211), (199, 222), (212, 224)]:
        L.bld("generic_tent_a", x, y, 5)
    L.dp("vot_fire_pit", 206, 220, 2, solid=False)
    P("br_caravan_wagon", 196, 214, 4)
    P("br_hitching_trough", 211, 216, 3)
    P("br_umbrella_acacia", 238, 203, 7)
    P("br_umbrella_acacia", 244, 222, 7)
    P("br_baobab", 214, 232, 11)
    P("br_signpost", 200, 207, 5)
    _grove(L, TUFTS + SCRUB, 225, 214, 24, 16, 12, 5, gap=3.5, shore_ok=False, solid=False)

    # ---- Lushwater Oasis (south-west) ----------------------------------------
    P("br_baobab", 54, 196, 11)
    P("br_green_oak", 96, 200, 8)
    P("br_green_oak", 92, 184, 8)
    P("br_umbrella_acacia", 58, 182, 7)
    P("br_umbrella_acacia", 85, 212, 7)
    P("br_hitching_trough", 86, 206, 3)
    P("br_caravan_wagon", 93, 211, 4)
    P("br_tauren_tipi", 96, 192, 6)
    P("br_tauren_tipi", 59, 210, 6)
    _grove(L, TUFTS, 75, 198, 28, 16, 14, 6, gap=3.0, solid=False)

    # ---- Forgotten Pools (north-west) ----------------------------------------
    P("br_baobab", 66, 66, 11)
    P("br_baobab", 102, 90, 11)
    P("br_dead_tree_vulture", 60, 80, 7)
    P("br_dead_tree_vulture", 88, 70, 7)
    P("br_dry_waterhole", 70, 100, 3, solid=False)
    P("br_raptor_nest", 83, 102, 3)
    P("br_vulture_roost", 108, 84, 4)
    P("br_tumbleweed_bones", 96, 104, 3)
    _grove(L, [("br_green_oak", 8)] + TUFTS, 82, 86, 26, 18, 10, 7, gap=4.5, solid="core")

    # ---- Grol'dom Farm ----------------------------------------------------------
    L.bld("generic_house_a", 79, 141, 6)
    L.bld("generic_shack_a", 93, 140, 5)
    L.bld("generic_shack_b", 90, 156, 4)
    P("br_hitching_trough", 84, 150, 3)
    P("br_caravan_wagon", 96, 149, 4)
    P("br_signpost", 74, 147, 5)
    for fy in (152, 154, 156):
        L.row("br_golden_grass_tuft", range(72, 88, 3), fy, 2, solid=False)

    # ---- Shrine of the Fallen Warrior ---------------------------------------
    L.dp("den_sword_stone", 50, 138, 4, solid="core")
    P("br_tauren_totem", 45, 134, 7)
    P("br_tauren_totem", 55, 134, 7)
    L.dp("vot_trail_cairn", 44, 142, 3)
    L.dp("vot_trail_cairn", 56, 142, 3)
    L.dp("vot_war_banner", 47, 146, 5)
    L.dp("vot_war_banner", 53, 146, 5)
    _grove(L, ROCKS + TUFTS, 50, 140, 12, 9, 7, 8, gap=4, solid=False)

    # ---- Dreadmist Den and its approach -----------------------------------------
    L.dp("bbc_summon_circle", 50, 45, 5, solid=False)
    L.dp("bbc_candelabra", 44, 42, 4)
    L.dp("bbc_candelabra", 56, 42, 4)
    L.dp("bbc_altar", 50, 40, 4)
    L.dp("bbc_skull_pile", 45, 48, 3)
    L.dp("bbc_skull_pile", 56, 48, 3)
    L.dp("bbc_tent", 43, 37, 5)
    L.dp("bbc_tent", 58, 37, 5)
    L.dp("bbc_banner", 47, 50, 5)
    L.dp("bbc_banner", 53, 50, 5)
    L.dp("bbc_banner", 56, 56, 5)
    L.dp("bbc_skull_pile", 62, 62, 3)
    P("br_dead_tree_vulture", 66, 68, 7)
    P("br_dead_tree_vulture", 49, 60, 7)

    # ---- roadside composition (hand-placed groves, not scatter) --------------------
    for (cx, cy, rx, ry, n, sd) in [
            (136, 40, 9, 14, 5, 21), (164, 66, 9, 12, 5, 22), (140, 190, 9, 10, 4, 23),
            (162, 205, 8, 10, 4, 24), (120, 130, 12, 6, 5, 25), (186, 135, 10, 6, 4, 26),
            (136, 220, 8, 9, 4, 27), (172, 180, 8, 8, 3, 28), (108, 164, 9, 8, 4, 29)]:
        _grove(L, ACACIAS, cx, cy, rx, ry, n, sd, gap=7)
    for (cx, cy, rx, ry, n, sd) in [
            (110, 60, 12, 10, 8, 31), (196, 70, 12, 10, 7, 32), (30, 90, 10, 12, 7, 33),
            (45, 175, 12, 10, 8, 34), (240, 170, 10, 10, 6, 35), (110, 205, 10, 8, 6, 36),
            (255, 130, 8, 12, 5, 37), (180, 30, 12, 8, 6, 38), (120, 28, 10, 8, 5, 39),
            (140, 270, 10, 8, 5, 40), (90, 262, 14, 10, 7, 41), (215, 262, 14, 10, 7, 42),
            (30, 230, 10, 10, 6, 43), (252, 90, 8, 10, 5, 44)]:
        _grove(L, SCRUB + ROCKS, cx, cy, rx, ry, n, sd, gap=4, solid="core")
    for (cx, cy, rx, ry, n, sd) in [
            (150, 60, 22, 20, 10, 51), (150, 110, 18, 10, 6, 52), (95, 120, 20, 12, 7, 53),
            (190, 100, 20, 14, 8, 54), (150, 190, 22, 14, 9, 55), (205, 160, 20, 12, 7, 56),
            (125, 218, 14, 10, 6, 57), (230, 60, 18, 14, 7, 58), (30, 140, 10, 14, 5, 59)]:
        _grove(L, TUFTS, cx, cy, rx, ry, n, sd, gap=3.5, solid=False)

    # ---- lone landmarks that break up the open country ----------------------------
    # wrecked caravan, south-west
    P("br_caravan_wagon", 44, 256, 4)
    P("br_kodo_skeleton", 52, 259, 4)
    P("br_tumbleweed_bones", 38, 261, 3)
    P("br_vulture_roost", 47, 250, 4)
    # standing-stone circle of the Tauren hunters, far west
    for (x, y) in [(18, 196), (26, 190), (26, 202), (34, 196)]:
        P("br_tauren_totem", x, y, 7)
    P("br_tauren_tipi", 26, 196, 6, solid=False)
    # hunter's blind, north-east of the road
    P("br_tauren_tipi", 182, 44, 6)
    P("br_tauren_tipi", 190, 48, 6)
    L.dp("vot_hide_rack", 186, 52, 3)
    # south-east kodo bones
    P("br_kodo_skeleton", 224, 276, 4)
    P("br_kodo_skeleton", 233, 272, 4)
    P("br_dead_tree_vulture", 228, 268, 7)
    # sun-baked waterhole & raptor roost, mid-west
    P("br_dry_waterhole", 112, 176, 3, solid=False)
    P("br_raptor_nest", 120, 180, 3)
    P("br_raptor_nest", 105, 182, 3)
    # Barrens mile-markers on the long roads
    P("br_signpost", 153, 100, 5)
    P("br_signpost", 153, 205, 5)
    P("br_signpost", 192, 100, 5)

    # ---- chests ---------------------------------------------------------------------
    for (x, y) in [(196, 124), (56, 58), (88, 160), (98, 108), (226, 60), (236, 208), (60, 202),
                   (132, 262), (176, 258), (116, 66), (30, 112), (248, 150)]:
        L.chest(x, y)


def build_layout():
    L = Layout()
    _terrain(L)
    _portals(L)
    dress(L)
    _subzones(L)
    _seal_unreachable(L)
    return L


def register_baked(zone, baked_dir=BAKED_DIR, chunk=20):
    for cy in range(0, H, chunk):
        for cx in range(0, W, chunk):
            fn = f"{baked_dir}/ground_{cx}_{cy}.jpg"
            if not os.path.exists(fn):
                raise FileNotFoundError(f"{fn} - run python3 tools/bake_central_barrens.py")
            w, h = min(chunk, W - cx), min(chunk, H - cy)
            zone.add_ground_chunk(fn, cx, cy, w, h)
            zone.ground_chunks[-1]["exact"] = True
            zone.add_water_chunk(fn, cx, cy, w, h)
            zone.add_obstacle_chunk(fn, cx, cy, w, h)


def generate_central_barrens():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    ys, xs = np.mgrid[0:H, 0:W]
    kind = tile_kind(xs + 0.5, ys + 0.5)
    pal = {0: (214, 178, 96), 1: (110, 190, 210), 2: (40, 90, 150), 3: (96, 62, 48), 4: (140, 100, 50)}
    img = np.zeros((H, W, 3), np.uint8)
    for k, c in pal.items():
        img[kind == k] = c
    wd = wash_dist(xs + 0.5, ys + 0.5)
    img[(wd > 0) & (kind == 0)] = (190, 150, 90)
    rd = road_dist(xs + 0.5, ys + 0.5)
    img[(rd > 0) & (kind == 0)] = (240, 215, 150)
    for (px, py) in PORTALS:
        img[max(py - 1, 0):py + 2, max(px - 1, 0):px + 2] = (255, 0, 255)
    Image.fromarray(img).resize((W * scale, H * scale), Image.NEAREST).save(path)
    return kind
