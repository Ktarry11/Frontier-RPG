"""
Hand-built Northern Barrens (280x260): fen-and-spire country under the Mor'shan Rampart.

Same recipe as Central / Southern Barrens (claude/zone_perfection_playbook.md): this module owns
the TILE data (walkability, props, portals, subzones) and the analytic landform fields (`fields`)
the baker (tools/bake_northern_barrens.py) paints from.

DESIGN GOAL: a silhouette unlike Central (one meandering road across open plain + sea) and
Southern (a W-E rift canyon).  The Northern Barrens is a *wet, broken* country:

    Gold Road ........... a long meandering N-S spine from the Crossroads gate (150,256) up to the
                          Rampart gate (150,4), with branch roads (not a ladder of forks)
    Mor'shan Rampart .... two E-W cliff walls across the north with ONE palisade gate gap
    Mor'shan Base Camp .. a flat siege camp on the plain below the wall
    Dry Hills ........... a WEST HIGHLAND of rounded hill-mounds with winding trails; Serena's cave
                          sits at its southern end (60,150)
    Slug Fens ........... BRAIDED WETLAND: wadeable pools + mud islets, a causeway through
    Harpy Roost ......... a loose RING OF SPIRES (not a wall) round a nest bowl, north-east
    Sludge Fen .......... a black oil basin under the east cliffs; Boulder Lode adit at (255,45)
    Stagnant Oasis ...... a round, scummy pond with a camp on its shore
    Far Watch Post ...... a HEADLAND jutting into the sea between two bays
    Merchant Coast ...... a wide south-east BAY with a beach arm

HARD CONTRACTS (world/portal_manager.py):
    portals  Crossroads gate (150,256)   Rampart gate (150,4)   Boulder Lode (255,45)   Serena (60,150)
    arrivals are 2 tiles NORTH of the portal tile; cave exits land 1 south of it.
"""
import math
import os

import numpy as np
from scipy.spatial import cKDTree

from tools import handbuilt_central_barrens as CB
from tools.handbuilt_central_barrens import (BP, DP, BLD, ENT, CP, blob, _wob, _smooth, _gauss, _grove,
                                             ACACIAS, SCRUB, TUFTS, ROCKS, BONES)
from world.tilemap import Tilemap

BAKED_DIR = "assets/tiles/northern_barrens/baked"
W, H = 280, 260

PORTALS = {(150, 256): "Central Barrens", (150, 4): "Ashenvale East",
           (255, 45): "Boulder Lode Mine", (60, 150): "Serena's Hollow"}
ARRIVALS = [(150, 254), (150, 2), (255, 46), (60, 151)]

# ------------------------------------------------------------------ the plan
ROADS = {
    # Gold Road: Crossroads gate -> north, a long lazy S-curve
    "gold_s":   ([(150, 254), (150, 242), (146, 228), (150, 214), (158, 198), (160, 184), (152, 170),
                  (144, 156), (142, 142), (148, 128)], 3.6),
    "gold_n":   ([(148, 128), (152, 114), (146, 100), (140, 86), (142, 72), (148, 58), (146, 44), (144, 32),
                  (148, 20), (150, 6)], 3.6),
    "oasis":    ([(160, 184), (176, 182), (190, 178), (200, 176)], 2.6),
    "farwatch": ([(152, 114), (170, 117), (190, 121), (212, 125), (232, 128), (250, 130), (258, 131)], 2.8),
    "oil":      ([(142, 74), (160, 76), (178, 80), (196, 77), (212, 73), (226, 68), (238, 58), (248, 50),
                  (255, 47)], 2.8),
    "coast":    ([(156, 204), (174, 213), (194, 221), (212, 229), (224, 236)], 2.8),
    "causeway": ([(143, 140), (131, 144), (118, 141), (106, 137), (96, 134), (84, 131), (74, 134), (68, 141),
                  (63, 147), (60, 152)], 2.4),
    "hills":    ([(146, 48), (130, 46), (108, 45), (86, 47), (64, 52), (46, 59), (32, 66), (24, 76)], 2.4),
    "hills_s":  ([(24, 76), (22, 90), (20, 106), (24, 122), (34, 136), (46, 146), (58, 152)], 2.0),
}

# west highland: rounded hill-mounds (cx, cy, rx, ry, rot)
HILLS = [
    # chains of overlapping mounds = low ranges, with open valleys between them
    (14, 42, 6, 4.5, 10), (24, 46, 6, 4.5, 0), (34, 40, 5, 4, -10), (44, 36, 5, 3.5, 0),
    (12, 62, 6, 4.5, 0), (50, 70, 6, 4.5, 20), (60, 77, 5.5, 4, 0), (66, 87, 5, 4, -20), (61, 99, 5.5, 4.5, 10),
    (34, 108, 6, 4.5, 0), (42, 115, 5.5, 4.5, 20), (48, 125, 5, 4, 0),
    (13, 118, 5, 4, 0), (11, 131, 5, 4, 10), (15, 143, 5, 4, 0),
    (28, 152, 6, 4, -10), (38, 158, 4.5, 3.5, 0),
    (46, 52, 4, 3, 10), (66, 60, 4, 3, 0), (68, 113, 4, 3, 0),
]

# harpy roost: a loose ring of spires round the nest bowl (cx, cy, rx, ry) - the east Rampart wall
# crumbles into them
SPIRES = [(228, 34, 4.6, 4.0), (224, 48, 5.0, 4.2), (212, 54, 4.4, 3.8), (196, 54, 5.2, 4.2),
          (184, 46, 4.6, 3.8), (180, 34, 5.0, 4.2), (186, 21, 4.4, 3.6), (200, 15, 5.0, 4.0),
          (215, 16, 4.6, 3.8), (227, 22, 4.2, 3.4)]


# cliff massifs: (cx, cy, rx, ry, rot_deg)
MESAS = [
    # cave faces (sprites sit against them)
    (257, 37, 17, 7, 0),      # Boulder Lode face
    (60, 141, 16, 6, 0),      # Serena's Hollow face
    # gate flanks
    (124, 8, 14, 4, 0), (178, 8, 16, 4, 0), (122, 255, 14, 4, 0), (182, 255, 16, 4, 0),
    # Far Watch headland: cliff drops north and south of the point
    (246, 111, 13, 4.5, 12), (244, 151, 13, 4.5, -12),
    # Merchant bay headlands
    (251, 204, 12, 5, 20), (248, 251, 10, 4, 0),
    # open-country formations, tilted
    (50, 202, 10, 5, 15), (62, 209, 5, 3, 0), (100, 228, 12, 5, -10), (30, 236, 9, 4, 5),
    (112, 72, 6, 4, -10), (190, 92, 8, 4, 10), (232, 162, 8, 5, -20), (100, 192, 8, 4, 20),
    (172, 238, 9, 4, 0), (204, 150, 6, 3.5, 10),
] + [(cx, cy, rx, ry, rot) for (cx, cy, rx, ry, rot) in HILLS] + [(cx, cy, rx, ry, 0) for (cx, cy, rx, ry) in SPIRES]

RINGS = []


# long ridges: (waypoints, half-width) - tapered at both ends
RIDGES = [
    # Mor'shan Rampart: two walls, one gate gap between (150,27)
    ([(8, 27), (28, 24), (52, 27), (78, 25), (104, 28), (128, 26), (141, 27)], 3.8),
    ([(159, 27), (170, 25), (182, 28)], 3.8),
    # east terrace scarps, cut by the Far Watch road
    ([(176, 96), (196, 92), (220, 98), (240, 92)], 3.0),
    ([(186, 146), (206, 142), (226, 148)], 2.8),
    # south-west scarp curve
    ([(20, 190), (40, 185), (70, 190), (92, 202)], 3.0),
    # fen bluff spur north of the causeway
    ([(76, 94), (92, 90), (110, 94)], 2.4),
    # coast cliffs north of the oasis, and a low spine south of the causeway
    ([(206, 196), (222, 190), (240, 196)], 2.6), ([(110, 176), (128, 182), (140, 178)], 2.4),
]

# gaps carved through the above/rim: ("ell", cx, cy, rx, ry)
GAPS = [
    ("ell", 150, 257, 11, 9),      # Crossroads gate
    ("ell", 150, 3, 11, 9),        # Rampart gate
    ("ell", 150, 27, 10, 7),       # Rampart palisade gap
    ("ell", 255, 47, 7, 5),        # Boulder Lode landing
    ("ell", 60, 152, 7, 5),        # Serena's landing
    ("ell", 210, 95, 5, 5),        # terrace pass (oil road)
    ("ell", 236, 128, 5, 5),       # terrace pass (farwatch)
    ("ell", 196, 145, 4, 5),
]

_ROAD_TREES = {}
_RIDGE_TREES = {}


def _road_tree(name):
    if name not in _ROAD_TREES:
        from tools.terrain_painter import Painter
        pts, w = ROADS[name]
        _ROAD_TREES[name] = (cKDTree(Painter.spline(pts)), w)
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


# ------------------------------------------------------------ water shapes
FENS = [   # braided wetland: chains of overlapping pools = waterways, with mud islets between
    (80, 102, 12, 4, 10, 0.3), (96, 100, 10, 3.6, -5, 1.2), (110, 104, 9, 3.6, 8, 2.2), (124, 110, 8, 3.4, 20, 0.5),
    (76, 120, 9, 3.8, -10, 3.0), (90, 124, 11, 4.2, 5, 0.7), (104, 126, 9, 4.0, -10, 1.9), (118, 130, 8, 3.6, 15, 2.8),
    (130, 124, 6, 3.2, 0, 1.4),
    (82, 146, 10, 4.0, 5, 2.5), (98, 150, 10, 4.2, -5, 0.9), (112, 152, 9, 4.0, 10, 3.3), (126, 156, 7, 3.6, 0, 1.7),
    (78, 162, 9, 3.8, 0, 2.1), (92, 166, 8, 3.4, 10, 0.2), (106, 168, 7, 3.2, 0, 2.6),
    (86, 112, 3, 5.5, 0, 0.6), (70, 134, 4, 3.0, 0, 1.0), (96, 158, 3, 4.5, 0, 1.5), (118, 116, 3, 4.5, 0, 2.0),
    (134, 142, 5, 3.2, 0, 2.1),
]
LAKES = {
    "fens":   FENS,
    "sludge": [(232, 70, 11, 6.8, 8, 1.1), (222, 82, 5, 3.4, 0, 2.0)],
    "oasis":  [(204, 172, 9, 6, 0, 0.8)],
}
DEEP_SHRINK = {"fens": 2.2, "sludge": 3.2, "oasis": 3.0}
ISLETS = [(266, 96, 5.0, 3.4, 20, 0.6), (270, 176, 4.4, 3.0, 0, 1.4), (258, 214, 3.4, 2.6, 0, 2.2)]


def coast_x(gy):
    """East shore: Far Watch headland between two bays, and the big Merchant bay in the south-east."""
    return (266.0 + 8.0 * _gauss(gy, 131, 13) - 16.0 * _gauss(gy, 104, 10) - 14.0 * _gauss(gy, 164, 12)
            - 31.0 * _gauss(gy, 232, 19) + 2.0 * np.sin(0.33 * gy + 0.5) + 1.8 * np.sin(0.19 * gy) + 1.2 * np.sin(0.53 * gy + 1.0))


def water_fields(gx, gy):
    """(shallow_extent, deep_extent): >0 inside, in tiles."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    sea = np.minimum(gx - coast_x(gy), (gy - 78.0) * 2.0)
    sea_d = sea - 3.4
    sh, dp = sea, sea_d
    for key, shapes in LAKES.items():
        for (cx, cy, rx, ry, rot, ph) in shapes:
            s = blob(gx, gy, cx, cy, rx, ry, rot, ph)
            sh = np.maximum(sh, s)
            dp = np.maximum(dp, s - DEEP_SHRINK[key])
    for (cx, cy, rx, ry, rot, ph) in ISLETS:
        isl = blob(gx, gy, cx, cy, rx, ry, rot, ph)
        sh = np.minimum(sh, -isl)
        dp = np.minimum(dp, -isl)
    return sh, dp


def deck_field(gx, gy):
    return np.full(np.shape(gx), -9.0)


# ----------------------------------------------------------------- cliffs
def gap_extent(gx, gy):
    best = np.full(np.shape(gx), -99.0)
    for g in GAPS:
        _, cx, cy, rx, ry = g
        d = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
        best = np.maximum(best, (1 - d) * min(rx, ry))
    best = np.maximum(best, road_dist(gx, gy) + 2.4)
    return best


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
    west = (7.0 + 3.0 * np.sin(0.05 * gy + 0.9) + 1.5 * np.sin(0.13 * gy + 1.0) + 0.8 * np.sin(0.37 * gy)) - gx
    east = gx - (268.0 + 9.0 * _smooth(70, 84, gy) - 2.6 * np.sin(0.06 * gy + 0.3) - 1.2 * np.sin(0.17 * gy + 1.0) - 0.7 * np.sin(0.41 * gy))
    north = (7.5 + 2.4 * np.sin(0.05 * gx + 1.0) + 1.2 * np.sin(0.11 * gx) + 0.7 * np.sin(0.31 * gx + 1.0)) - gy
    south = gy - (252.5 - 2.6 * np.sin(0.06 * gx + 2.0) - 1.0 * np.sin(0.13 * gx) - 0.7 * np.sin(0.29 * gx + 2.0))
    out = np.maximum(out, np.maximum(np.maximum(west, east), np.maximum(north, south)))
    return out + 1.1 * _wob(gx, gy)


def fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    sh, dp = water_fields(gx, gy)
    cl = np.minimum(cliff_raw(gx, gy), -gap_extent(gx, gy))
    return dict(cliff=cl, shallow=sh, deep=dp, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    f = fields(gx, gy)
    kind = np.zeros(np.shape(gx), int)
    kind[f["shallow"] > 0] = 1
    kind[f["deep"] > 0] = 2
    kind[(f["cliff"] > 0) & (kind == 0)] = 3
    kind[f["cliff"] > 1.5] = 3
    return kind


# ------------------------------------------------------- painted-only fields
WASHES = {
    "fen_runoff": ([(106, 168), (114, 186), (126, 204), (140, 222), (156, 236)], 2.6),
    "oil_runoff": ([(226, 80), (214, 96), (206, 110), (200, 126)], 2.2),
    "hill_wash": ([(40, 58), (36, 88), (30, 118), (40, 140)], 2.4),
    "coast_wash": ([(190, 190), (204, 206), (216, 222)], 2.2),
}

CAMP_PATCHES = {   # name -> (cx, cy, rx, ry): trampled earth / paving
    "rampart": (150, 31, 14, 6), "basecamp": (145, 65, 15, 12), "farwatch": (256, 130, 11, 9),
    "dryhills": (26, 68, 8, 6), "fens": (139, 148, 7, 6), "sludge": (222, 77, 9, 6),
    "lode": (249, 52, 8, 5), "hollow": (66, 156, 8, 5), "oasis": (194, 182, 8, 6),
    "coast": (222, 237, 11, 6), "gold": (148, 206, 8, 6),
}

OIL_STAIN = [(232, 70, 20, 12), (222, 82, 9, 6)]       # painted dark ground round the oil pools
SALT_PANS = [(190, 122, 8, 3), (126, 214, 7, 3)]       # painted only
NEST_BOWL = (206, 36, 14, 11)                          # painted bone-and-feather ground


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


# Quest hubs (tools/build_northern_barrens_quests.py; positions synced by tools/sync_northern_barrens_npcs.py)
NPC_POSITIONS = {
    "farwatch_officer": (258, 130),      # Far Watch Post
    "morshan_outrider": (145, 65),       # Mor'shan Base Camp
    "nb_basecamp_vendor": (150, 66),     # Quartermaster at the Base Camp
    "nb_rampart_captain": (157, 31),     # south of the Rampart gate
    "nb_dryhills_huntress": (26, 68),    # Dry Hills trailhead
    "nb_fen_warden": (139, 147),         # fen causeway mouth on the Gold Road
    "nb_sludge_inspector": (222, 76),    # Sludge Fen oil rig
    "nb_lode_surveyor": (249, 51),       # below the Boulder Lode adit
    "nb_hollow_shaman": (66, 155),       # Serena's Hollow approach
    "nb_oasis_scout": (194, 182),        # Stagnant Oasis shore
    "nb_coast_sergeant": (222, 236),     # Merchant Coast beach
    "nb_road_warden": (148, 206),        # Gold Road waystation
}

CAVES = {   # portal tile -> (sprite, w, h)
    (255, 45): ("ent_collapsed_mine", 9, 8),
    (60, 150): ("ent_savanna_cave", 9, 8),
}


class NLayout(CB.Layout):
    W, H = W, H
    portal_tiles = list(PORTALS)
    arrival_tiles = list(ARRIVALS)

    def road_fn(self, gx, gy):
        return road_dist(gx, gy)

    def __init__(self):
        self.zone = Tilemap("Northern Barrens", W, H,
                            "Fen and spire country under the Mor'shan Rampart; the Gold Road runs through it all.")
        self.z = self.zone
        self.z.region = "Kalimdor - Central"
        self.skipped = []
        self.chests = []
        self.placed = 0
        self.npc_xy = list(NPC_POSITIONS.values())


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
            elif rd[y, x] > 0:
                z.set_tile(x, y, "path", "base")


def _seal_unreachable(L, start=(150, 252)):
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
    ("Dry Hills", 6, 30, 66, 138, None),
    ("Slug Fens", 70, 92, 76, 80, None),
    ("Gold Road", 140, 95, 30, 130, None),
    ("Harpy Roost", 174, 10, 60, 50, None),
    ("Mor'shan Rampart", 100, 8, 76, 26, None),
    ("Mor'shan Base Camp", 129, 51, 32, 28, None),
    ("Sludge Fen", 212, 50, 44, 40, None),
    ("Stagnant Oasis", 185, 160, 32, 30, None),
    ("Far Watch Post", 240, 114, 36, 34, None),
    ("Merchant Coast", 215, 198, 60, 56, None),
]


def _subzones(L):
    for key, x, y, w, h, disp in SUBZONES:
        L.z.add_subzone(key, x, y, w, h, display_name=disp)


# ------------------------------------------------------------------ dressing
FEN_REEDS = [("vot_reeds", 3)]
FEN_TREES = [("vot_dead_tree", 6)]
THORNS = [("br_thorn_scrub", 3), ("br_agave_spike", 3)]


def dress(L):
    P = L.prop

    # ---- Mor'shan Rampart: the palisade gate in the wall ----------------------------------------
    L.bld("palisade_gatehouse", 150, 30, 8, solid=False, road_ok=True)
    L.bld("frontier_watchtower", 134, 30, 9)
    L.bld("frontier_watchtower", 166, 30, 9)
    L.dp("vot_palisade", 138, 32, 3, solid=True)
    L.dp("vot_palisade", 162, 32, 3, solid=True)
    L.dp("vot_war_banner", 144, 34, 5)
    L.dp("vot_war_banner", 156, 34, 5)
    L.dp("vot_fire_pit", 160, 35, 2, solid=False)
    L.bld("generic_tent_a", 163, 33, 5)
    P("br_signpost", 152, 40, 5)
    # north of the wall: the road to Ashenvale, an abandoned Sentinel signal fire
    L.dp("rf_brazier", 144, 14, 3)
    L.dp("rf_brazier", 156, 14, 3)
    P("br_sandstone_boulders", 130, 15, 4)
    P("br_sandstone_boulders", 172, 14, 4)

    # ---- Mor'shan Base Camp: the siege camp below the wall ------------------------------------------
    L.bld("generic_tent_a", 138, 62, 5)
    L.bld("generic_tent_b", 152, 61, 5)
    L.bld("generic_tent_a", 141, 73, 5)
    L.dp("vot_fire_pit", 146, 68, 2, solid=False)
    L.dp("vot_war_drum", 150, 69, 3)
    L.dp("vot_hide_rack", 135, 68, 3)
    L.dp("vot_crate_stack", 155, 72, 3)
    L.dp("vot_palisade", 132, 58, 3, solid=True)
    L.dp("vot_palisade", 135, 56, 3, solid=True)
    L.dp("vot_palisade", 157, 56, 3, solid=True)
    L.dp("vot_war_banner", 146, 58, 5)
    P("br_kolkar_tent", 130, 76, 6)
    P("br_kolkar_tent", 160, 78, 6)
    P("br_caravan_wagon", 128, 66, 4)
    P("br_signpost", 143, 55, 5)

    # ---- Dry Hills: the huntress's blind at the trailhead, a quiet harpy-feather cairn --------------
    L.bld("generic_tent_a", 30, 70, 5)
    L.dp("vot_fire_pit", 24, 72, 2, solid=False)
    L.dp("vot_hide_rack", 21, 66, 3)
    L.dp("vot_trail_cairn", 36, 76, 3)
    P("br_signpost", 38, 62, 5)
    P("br_vulture_roost", 54, 76, 4)
    P("br_dead_tree_vulture", 28, 108, 7)
    P("br_dead_tree_vulture", 50, 134, 7)
    P("br_sandstone_spire", 46, 100, 7)
    P("br_sandstone_spire", 18, 78, 7)
    P("br_sandstone_spire", 40, 142, 7)
    P("br_raptor_nest", 40, 116, 3)

    # ---- Serena's Hollow approach: the shaman's stones ----------------------------------------------
    L.bld("generic_tent_b", 71, 158, 5)
    L.dp("vot_fire_pit", 63, 158, 2, solid=False)
    L.dp("vot_totem_pole", 56, 156, 5)
    L.dp("vot_totem_pole", 76, 154, 5)
    L.dp("vot_hide_rack", 68, 162, 3)
    P("br_vulture_roost", 50, 156, 4)
    P("br_signpost", 66, 146, 5)

    # ---- Slug Fens: reeds, dead trees and a causeway marker -------------------------------------------
    _grove(L, FEN_REEDS, 100, 132, 38, 30, 16, 61, gap=5.0, solid=False, shore_ok=True, path_dir=DP)
    _grove(L, FEN_TREES, 104, 130, 36, 30, 7, 62, gap=9.0, path_dir=DP)
    _grove(L, [("br_mossy_boulder", 3)], 100, 134, 36, 28, 5, 63, gap=8.0)
    P("br_driftwood_skull", 98, 140, 3)
    P("br_signpost", 142, 134, 5)
    # fen warden's hut on the causeway mouth
    L.bld("generic_hut_a", 135, 150, 5)
    L.dp("vot_fire_pit", 141, 151, 2, solid=False)
    L.dp("vot_crate_stack", 144, 150, 3)
    L.dp("vot_hide_rack", 133, 144, 3)

    # ---- Harpy Roost: bone-and-feather nest bowl inside the spires --------------------------------------
    for (x, y) in [(202, 34), (212, 31), (208, 42), (198, 26)]:
        P("br_raptor_nest", x, y, 3)
    P("br_vulture_roost", 194, 40, 4)
    P("br_vulture_roost", 218, 38, 4)
    P("br_dead_tree_vulture", 210, 24, 7)
    P("br_dead_tree_vulture", 196, 48, 7)
    L.dp("vot_beast_ribcage", 214, 46, 4)
    P("br_tumbleweed_bones", 204, 47, 3)
    P("br_driftwood_skull", 218, 28, 3)

    # ---- Sludge Fen: the Venture Co. oil rig ----------------------------------------------------------------
    L.bld("scrapyard_workshop", 216, 72, 7)
    L.bld("generic_tent_a", 224, 79, 5)
    L.dp("vot_broken_cart", 212, 80, 3)
    L.dp("vot_broken_cart", 242, 74, 3)
    L.dp("rf_supply_crates", 228, 84, 3)
    L.dp("rf_supply_crates", 218, 86, 3)
    L.dp("rf_tool_rack", 220, 70, 3)
    L.dp("grotto_barrel_stack", 246, 64, 3)
    L.dp("grotto_barrel_stack", 236, 60, 3)
    L.dp("grotto_barrel_stack", 244, 82, 3)
    L.dp("rf_golem_husk", 240, 86, 5)
    L.dp("vot_crate_stack", 234, 82, 3)
    P("br_signpost", 206, 76, 5)

    # ---- Boulder Lode: surveyor's claim below the adit ------------------------------------------------------
    L.bld("generic_tent_a", 244, 54, 5)
    L.dp("rf_ore_cart", 252, 56, 3)
    L.dp("rf_tool_rack", 242, 50, 3)
    L.dp("rf_supply_crates", 247, 58, 3)
    L.dp("vot_fire_pit", 250, 55, 2, solid=False)
    L.dp("den_rock_rubble", 258, 52, 3, solid=False)
    L.dp("den_rock_rubble", 238, 48, 3, solid=False)

    # ---- Stagnant Oasis: a camp on the near shore ----------------------------------------------------------------
    L.bld("generic_tent_b", 188, 186, 5)
    L.dp("vot_fire_pit", 193, 187, 2, solid=False)
    L.dp("vot_hide_rack", 186, 180, 3)
    P("br_dry_waterhole", 214, 182, 3, shore_ok=True)
    P("br_dead_tree_vulture", 212, 164, 7)
    P("br_umbrella_acacia", 196, 164, 7)
    P("br_termite_mound", 216, 176, 5)

    # ---- Far Watch Post: the headland tower ---------------------------------------------------------------------------
    P("br_crossroads_watchtower", 262, 122, 9)
    L.bld("generic_tent_a", 252, 136, 5)
    L.bld("generic_tent_b", 262, 137, 5)
    L.dp("vot_fire_pit", 256, 135, 2, solid=False)
    L.dp("vot_palisade", 246, 126, 3, solid=True)
    L.dp("vot_palisade", 246, 132, 3, solid=True)
    L.dp("vot_war_banner", 252, 124, 5)
    L.dp("vot_crate_stack", 266, 132, 3)
    P("br_kolkar_tent", 244, 140, 6)
    P("br_kolkar_tent", 240, 118, 6)
    P("br_signpost", 236, 132, 5)
    L.cp("signal_tower", 268, 128, 7, shore_ok=True)

    # ---- Merchant Coast: wrecked cargo along the beach ---------------------------------------------------------------
    L.bld("trading_post", 214, 232, 7)
    L.bld("generic_tent_a", 228, 232, 5)
    L.cp("rowboat_wreck", 232, 240, 4, shore_ok=True)
    L.cp("fish_crates_traps", 224, 242, 3)
    L.cp("driftwood_pile", 236, 226, 3, shore_ok=True)
    L.cp("mooring_posts", 230, 220, 3, shore_ok=True)
    L.cp("outrigger_canoe", 238, 234, 3, shore_ok=True)
    L.dp("vot_crate_stack", 210, 240, 3)
    L.dp("vot_crate_stack", 220, 228, 3)
    L.dp("grotto_ship_cannon", 238, 218, 4, shore_ok=True)
    L.dp("grotto_barrel_stack", 216, 244, 3)
    L.deco("sea_stack_spire", 262, 232, 6)
    P("br_signpost", 206, 222, 5)

    # ---- Gold Road waystation ------------------------------------------------------------------------------------------------
    L.bld("generic_tent_a", 142, 208, 5)
    L.dp("vot_fire_pit", 144, 211, 2, solid=False)
    L.dp("vot_hide_rack", 139, 204, 3)
    P("br_hitching_trough", 154, 210, 3)
    P("br_caravan_wagon", 160, 222, 4)
    P("br_signpost", 146, 236, 5)
    # gate welcome: Crossroads side
    P("br_kodo_tusk_gate", 150, 246, 7, solid=False, road_ok=True)
    P("br_tauren_totem", 143, 249, 7)
    P("br_tauren_totem", 157, 249, 7)

    # ---- the plains: sparing, deliberate groves (less is more) ------------------------------------------------------------------
    for (cx, cy, rx, ry, n, sd) in [(120, 200, 16, 12, 5, 21), (80, 224, 14, 10, 4, 22),
                                    (176, 150, 12, 8, 3, 23), (176, 56, 10, 8, 3, 24)]:
        _grove(L, ACACIAS, cx, cy, rx, ry, n, sd, gap=8)
    for (cx, cy, rx, ry, n, sd) in [(70, 190, 12, 8, 5, 31), (190, 100, 14, 8, 5, 32), (116, 90, 10, 8, 5, 33),
                                    (120, 24, 14, 6, 5, 34), (214, 120, 12, 6, 4, 35), (180, 232, 12, 6, 4, 36),
                                    (240, 100, 8, 8, 4, 37), (112, 238, 12, 6, 4, 38), (30, 188, 8, 6, 3, 39)]:
        _grove(L, SCRUB + ROCKS, cx, cy, rx, ry, n, sd, gap=4, solid="core")
    for (cx, cy, rx, ry, n, sd) in [(180, 200, 20, 12, 8, 51), (100, 216, 26, 12, 9, 52), (128, 38, 24, 8, 7, 53),
                                    (196, 112, 24, 10, 8, 54), (170, 170, 14, 10, 5, 55)]:
        _grove(L, TUFTS, cx, cy, rx, ry, n, sd, gap=3.5, solid=False)
    for (cx, cy, rx, ry, n, sd) in [(30, 52, 14, 8, 4, 61)]:
        _grove(L, THORNS, cx, cy, rx, ry, n, sd, gap=4, solid="core")


def _chests(L):
    for (x, y) in [(18, 80), (62, 38), (46, 130), (108, 82), (96, 118), (130, 26), (176, 40), (206, 60),
                   (240, 74), (232, 140), (202, 184), (150, 190), (84, 214), (232, 226), (170, 110),
                   (36, 142)]:
        L.chest(x, y)


def build_layout():
    L = NLayout()
    _terrain(L)
    _portals(L)
    dress(L)
    _subzones(L)
    _seal_unreachable(L)
    _chests(L)          # after sealing, so no chest can end up inside a sealed pocket
    return L


def register_baked(zone, baked_dir=BAKED_DIR, chunk=20):
    for cy in range(0, H, chunk):
        for cx in range(0, W, chunk):
            fn = f"{baked_dir}/ground_{cx}_{cy}.jpg"
            if not os.path.exists(fn):
                raise FileNotFoundError(f"{fn} - run python3 tools/bake_northern_barrens.py")
            w, h = min(chunk, W - cx), min(chunk, H - cy)
            zone.add_ground_chunk(fn, cx, cy, w, h)
            zone.ground_chunks[-1]["exact"] = True
            zone.add_water_chunk(fn, cx, cy, w, h)
            zone.add_obstacle_chunk(fn, cx, cy, w, h)


def generate_northern_barrens():
    L = build_layout()
    register_baked(L.zone)
    return L.zone
