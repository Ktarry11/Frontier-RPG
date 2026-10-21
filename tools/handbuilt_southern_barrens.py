"""
Hand-built Southern Barrens (260x240): kodo-bone badlands cut by a great dry canyon.

Same recipe as Central Barrens / Durotar (claude/zone_perfection_playbook.md): this module owns
the TILE data (walkability, props, portals, subzones) and the analytic landform fields
(`fields`) the baker (tools/bake_southern_barrens.py) paints from.

DESIGN GOAL: every district has its OWN silhouette so the zone does not read as one pattern
repeated (Kyle: "hand crafted but they're starting to look similar").  Central Barrens is a
meandering N-S road across an open plain with a sea; Southern is a *rift country*:

    The Rift ............ a winding dry canyon running W-E across the whole map (y~130).  Two
                          tapered cliff walls with a walkable gravel floor between them; the roads
                          cross it at natural ramps (gaps), plus a few extra breaks.
    Giant's Road ........ N-S spine from the Taurajo gate (130,2) over the Rift to the Field of Giants
    Bael'dun Keep ....... a WALLED FORT: closed cliff ring on a plateau, one east gate, one sally port
    Bael Modan .......... a STEPPED QUARRY: two open-ended crescent terraces round a flooded pit,
                          entered NE and stepped round to the SW (a zig-zag descent)
    Blackthorn Ridge .... BROKEN GROUND: diagonal thorn-mound fragments, no parallel walls
    Razorfen approach ... a HORSESHOE bowl open to the north, cave face at its back (55,175)
    Raptor Grounds ...... a VALLEY: two long ridges, spring pond between, exits W and S
    Field of Giants ..... OPEN BONE PLAIN: salt pan, giant ribcage arches, the Giant's Throne butte
    Broodspiral crater .. a SINKHOLE in a cracked basin (stone stair, radial cracks), SE corner
    NE hoodoos .......... spire garden / scarp; a hunter camp and a wrecked dwarven caravan

HARD CONTRACTS (world/portal_manager.py):
    portals  Camp Taurajo (130,2)   Razorfen Kraul (55,175)   The Broodspiral (225,220)
    arrivals are 2 tiles NORTH of the portal tile; cave exits land 1 south of it.
"""
import math
import os

import numpy as np
from PIL import Image
from scipy.spatial import cKDTree

from tools import handbuilt_central_barrens as CB
from tools.handbuilt_central_barrens import (BP, DP, BLD, ENT, CP, blob, _wob, _smooth, _gauss, _grove,
                                             ACACIAS, SCRUB, TUFTS, ROCKS, BONES)
from world.tilemap import Tilemap

BAKED_DIR = "assets/tiles/southern_barrens/baked"
W, H = 260, 240

PORTALS = {(130, 2): "Camp Taurajo", (55, 175): "Razorfen Kraul", (225, 220): "The Broodspiral"}
ARRIVALS = [(130, 0), (55, 176), (225, 221)]

# ------------------------------------------------------------------ the Rift
RIFT = [(6, 142), (28, 136), (48, 130), (68, 130), (88, 136), (108, 132), (130, 128), (152, 132),
        (174, 138), (196, 134), (216, 140), (238, 136), (254, 146)]
_RX = np.array([p[0] for p in RIFT], float)
_RY = np.array([p[1] for p in RIFT], float)


def rift_y(x):
    """centreline height at x (piecewise-smooth through the waypoints)."""
    return np.interp(x, _RX, _RY)


def _wall(x0, x1, off, step=8):
    xs = list(range(x0, x1 + 1, step))
    if xs[-1] != x1:
        xs.append(x1)
    return [(int(x), round(float(rift_y(x)) + off, 1)) for x in xs]


# ------------------------------------------------------------------ the plan
ROADS = {
    # Giant's Road: gate -> Keep fork -> Modan fork -> Raptor/Kraul fork -> over the Rift -> Giants
    "giants_n":  ([(130, 2), (130, 12), (134, 28), (136, 44), (130, 60), (126, 76), (130, 92), (134, 104)], 3.6),
    "giants_s":  ([(134, 104), (138, 116), (132, 130), (124, 146), (118, 162), (124, 176), (122, 188), (128, 196)], 3.6),
    "to_brood":  ([(128, 196), (144, 202), (164, 208), (186, 212), (206, 218), (222, 221)], 3.2),
    "keep":      ([(134, 28), (124, 30), (114, 32), (100, 34), (88, 34)], 2.8),
    "modan":     ([(126, 76), (112, 74), (96, 70), (80, 64), (66, 60), (54, 58)], 3.0),
    "quarry":    ([(54, 58), (46, 56), (38, 58), (30, 66), (24, 72), (30, 78), (40, 76)], 2.4),
    "kraul":     ([(134, 106), (114, 110), (96, 112), (80, 114), (70, 122), (64, 134), (60, 146), (56, 158),
                   (55, 172)], 3.0),
    "blackthorn": ([(96, 112), (84, 104), (70, 100), (56, 100), (46, 102)], 2.4),
    "east":      ([(134, 100), (150, 98), (168, 98), (186, 98), (200, 100), (212, 102), (226, 104)], 3.0),
    "raptor_s":  ([(226, 104), (232, 122), (236, 148), (234, 168), (230, 188), (228, 204), (226, 218)], 2.8),
    "giants_w":  ([(122, 182), (104, 186), (92, 182)], 2.4),
    "giants_e":  ([(124, 194), (148, 186), (170, 184)], 2.4),
    "hunters":   ([(136, 44), (152, 42), (170, 40), (190, 44)], 2.4),
}

# cliff massifs: (cx, cy, rx, ry, rot_deg)
MESAS = [
    # north-gate flanks
    (110, 5, 12, 5, 0), (152, 5, 14, 5, 0),
    # Wailing-style cave face north of the Kraul portal (sprite sits against it)
    (55, 168, 15, 5, 0),
    # Giant's Throne, the butte in the Field of Giants (+ talus)
    (166, 178, 9, 6.5, -15), (175, 184, 4.5, 3.5, 20),
    # open-country formations, tilted
    (86, 204, 8, 4.5, 20), (95, 210, 4, 3, 0), (198, 182, 7, 4, 30), (205, 189, 4, 3, 0),
    (150, 224, 14, 4.5, -6), (184, 230, 10, 4, 8),
]

# open crescents / rings: (cx, cy, rx, ry, rot, thickness)  - cliff where inner<r<1 (full ring)
RINGS = [
    (86, 32, 30, 19, 0, 0.22),       # Bael'dun Keep wall
    (222, 212, 20, 15, 0, 0.34),     # Broodspiral crater lip
]


def _arc(cx, cy, rx, ry, a0, a1, n=None):
    n = n or max(4, int(abs(a1 - a0) / 22))
    return [(round(cx + rx * math.cos(math.radians(a)), 1), round(cy + ry * math.sin(math.radians(a)), 1))
            for a in np.linspace(a0, a1, n + 1)]


# long ridges: (waypoints, half-width) - tapered at both ends
RIDGES = [
    # the Rift: one long wall each side (roads and two ramps cut it), floor ~8 tiles between
    (_wall(10, 250, -7.5, 10), 4.0), (_wall(10, 250, 7.5, 10), 4.0),
    # Bael Modan stepped quarry: outer terrace opens NE, inner terrace opens SW (zig-zag descent)
    (_arc(34, 64, 23, 19, 20, 310), 2.8),
    (_arc(34, 64, 12, 9.5, 205, 450), 2.3),
    # Blackthorn: diagonal fragments (broken ground, not walls)
    ([(22, 100), (31, 108), (38, 118)], 2.4), ([(44, 90), (54, 96), (66, 94)], 2.4),
    ([(52, 110), (60, 116), (70, 112)], 2.2), ([(76, 92), (84, 98), (90, 92)], 2.0),
    # Razorfen horseshoe (open north), the cave face is the mesa above
    ([(40, 150), (33, 162), (35, 178), (46, 190), (64, 193), (78, 187), (84, 172), (78, 152)], 3.2),
    # Raptor Grounds valley walls
    ([(196, 84), (210, 81), (226, 81), (244, 85)], 3.4),
    ([(196, 117), (212, 120), (230, 120), (246, 116)], 3.2),
    # NE scarp
    ([(176, 22), (196, 30), (214, 26), (234, 34)], 2.8),
    # south scarps framing the Giants' bone-field
    ([(88, 224), (104, 230), (124, 232)], 2.6), ([(10, 190), (14, 206), (10, 220)], 2.6),
    ([(16, 208), (32, 203), (50, 209)], 2.9), ([(36, 224), (54, 230), (76, 226)], 2.9),
    ([(246, 166), (250, 184), (246, 200)], 2.7), ([(200, 158), (214, 166), (220, 182)], 2.7),
]

# gaps carved through the above/rim: ("ell", cx, cy, rx, ry)
GAPS = [
    ("ell", 130, 3, 11, 9),          # Camp Taurajo gate
    ("ell", 55, 178, 7, 5),          # Kraul cave landing
    ("ell", 225, 221, 8, 6),         # Broodspiral stairs landing
    ("ell", 113, 32, 6, 5),          # Keep gate
    ("ell", 86, 51, 4, 3.2),         # Keep sally port
    ("ell", 58, 148, 8, 5),          # Kraul horseshoe mouth
    ("ell", 100, 126, 4.5, 6),       # Rift north-wall ramp
    ("ell", 176, 144, 5, 6),         # Rift south-wall ramp
    ("ell", 41, 40, 6, 4),           # quarry north rim (hidden shortcut)
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
LAKES = {
    "quarry": [(34, 64, 8.5, 6.2, 0, 0.8)],
    "spring": [(214, 95, 8.0, 4.6, 0, 2.0)],
}
DEEP_SHRINK = {"quarry": 3.0, "spring": 2.0}


def water_fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    sh = np.full(gx.shape, -99.0)
    dp = np.full(gx.shape, -99.0)
    for key, shapes in LAKES.items():
        for (cx, cy, rx, ry, rot, ph) in shapes:
            s = blob(gx, gy, cx, cy, rx, ry, rot, ph)
            sh = np.maximum(sh, s)
            dp = np.maximum(dp, s - DEEP_SHRINK[key])
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
    for (cx, cy, rx, ry, rot, th) in RINGS:
        dx, dy = gx - cx, gy - cy
        r = np.sqrt((dx / rx) ** 2 + (dy / ry) ** 2)
        ring = np.minimum(1 - r, r - (1 - th)) * min(rx, ry)
        out = np.maximum(out, ring)
    for (rpts, rhw) in RIDGES:
        out = np.maximum(out, _ridge(rpts, rhw, gx, gy))
    west = (7.0 + 3.0 * np.sin(0.05 * gy + 0.9) + 1.5 * np.sin(0.13 * gy + 1.0) + 0.8 * np.sin(0.37 * gy)) - gx
    east = gx - (253.0 - 2.6 * np.sin(0.06 * gy + 0.3) - 1.2 * np.sin(0.17 * gy + 1.0) - 0.7 * np.sin(0.41 * gy))
    north = (6.0 + 2.4 * np.sin(0.05 * gx + 1.0) + 1.2 * np.sin(0.11 * gx) + 0.7 * np.sin(0.31 * gx + 1.0)) - gy
    south = gy - (233.0 - 2.6 * np.sin(0.06 * gx + 2.0) - 1.0 * np.sin(0.13 * gx) - 0.7 * np.sin(0.29 * gx + 2.0))
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
    "rift_floor": (RIFT, 4.4),
    "giants_wash": ([(170, 196), (160, 180), (150, 160), (146, 146), (150, 132)], 3.0),
    "spring_wash": ([(206, 98), (200, 108), (204, 122)], 2.4),
    "quarry_wash": ([(46, 78), (60, 100), (66, 122)], 2.6),
}

CAMP_PATCHES = {   # name -> (cx, cy, rx, ry): trampled earth / paving
    "taurajo": (130, 8, 10, 6), "keep": (88, 33, 21, 12), "quarry": (30, 70, 10, 8), "kraul": (56, 176, 9, 6),
    "brood": (225, 218, 10, 8), "hunters": (192, 46, 7, 5), "razormane": (46, 106, 8, 6),
    "kraul_camp": (58, 160, 12, 8), "raptor": (232, 100, 9, 7), "caravan": (176, 62, 6, 4),
    "giants": (126, 186, 8, 6),
}

SALT_PANS = [(142, 190, 30, 14), (206, 40, 5, 3)]      # (cx, cy, rx, ry) painted only

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


# Quest hubs (tools/build_southern_barrens_quests.py; positions synced by tools/sync_southern_barrens_npcs.py)
NPC_POSITIONS = {
    "sb_rift_warden": (137, 116),        # Rift-Warden Brakka, Waystation (north ramp of the Rift)
    "sb_waystation_vendor": (138, 113),  # Provisioner Hemma
    "sb_bonehunter": (128, 172),         # Bonehunter Rurk, Field of Giants gate
    "sb_thornwatch": (62, 141),          # Thornwatch Ranger Oggra, Razorfen approach
    "sb_keep_spy": (121, 41),            # Spy Zhuul, east of the Bael'dun gate
    "sb_modan_scout": (63, 57),          # Dig-Scout Tarrik, quarry rim
    "sb_hoodoo_huntress": (195, 49),     # Huntress Alamir, the hunter's blind
    "sb_crater_digger": (209, 222),      # Excavator Fizzwick, crater rim
}

CAVES = {   # portal tile -> (sprite, w, h)
    (55, 175): ("ent_razorfen_gate", 9, 8),
    (225, 220): ("ent_sinkhole_stairs", 8, 7),
}


class SLayout(CB.Layout):
    W, H = W, H
    portal_tiles = list(PORTALS)
    arrival_tiles = list(ARRIVALS)

    def road_fn(self, gx, gy):
        return road_dist(gx, gy)

    def __init__(self):
        self.zone = Tilemap("Southern Barrens", W, H,
                            "Dangerous lands of kodo bones and dwarf ruins, split by a great dry rift.")
        self.z = self.zone
        self.z.region = "Kalimdor - South"
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


def _seal_unreachable(L, start=(130, 14)):
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
    ("Field of Giants", 90, 150, 100, 72, None),
    ("Razorfen Approach", 15, 135, 80, 75, None),
    ("Blackthorn Ridge", 14, 84, 80, 46, None),
    ("Bael Modan", 6, 40, 52, 46, None),
    ("Bael'dun Keep", 56, 10, 62, 44, None),
    ("Hoodoo Spires", 186, 38, 66, 40, None),
    ("Raptor Grounds", 196, 78, 52, 44, None),
    ("Sinkhole Crater", 198, 196, 56, 42, None),
]


def _rift_rects(step=24, half=9):
    """The Rift follows a wandering centreline; cover it with a chain of rectangles (registered last so
    they win over the Razorfen / Blackthorn / Field boxes they overlap)."""
    rects = []
    for x0 in range(0, W, step):
        xs = np.arange(x0, min(W, x0 + step) + 1)
        ys = rift_y(xs)
        y0 = int(ys.min() - half)
        y1 = int(ys.max() + half)
        rects.append(("The Rift", x0, y0, min(step, W - x0), y1 - y0, None))
    return rects


def _subzones(L):
    for key, x, y, w, h, disp in SUBZONES + _rift_rects():
        L.z.add_subzone(key, x, y, w, h, display_name=disp)


# ------------------------------------------------------------------ dressing
THORNS = [("br_thorn_scrub", 3), ("br_agave_spike", 3)]
DEAD = [("br_dead_tree_vulture", 7)]


def dress(L):
    P = L.prop

    # ---- Camp Taurajo gate (north): tusk gate over the road, totems, tower, wagon ------------
    P("br_kodo_tusk_gate", 130, 12, 7, solid=False, road_ok=True)
    P("br_tauren_totem", 123, 8, 7)
    P("br_tauren_totem", 137, 8, 7)
    P("br_crossroads_watchtower", 119, 13, 9)
    P("br_signpost", 135, 16, 5)
    P("br_caravan_wagon", 142, 14, 4)
    P("br_hitching_trough", 124, 17, 3)

    # ---- Bael'dun Keep: the walled fort ----------------------------------------------------
    L.bld("palisade_gatehouse", 113, 36, 7, solid=False, road_ok=True)
    L.bld("frontier_barracks", 76, 28, 6)
    L.bld("outpost_barracks", 96, 25, 6)
    L.bld("supply_depot", 72, 38, 6)
    L.bld("smithy", 98, 41, 5)
    L.bld("weapon_rack_shelter", 85, 44, 4)
    L.bld("well_house", 86, 33, 4)
    L.bld("frontier_watchtower", 66, 25, 8)
    L.bld("frontier_watchtower", 106, 23, 8)
    L.dp("rf_supply_crates", 79, 40, 3)
    L.dp("rf_tool_rack", 92, 31, 3)
    L.dp("rf_ore_cart", 106, 41, 3)
    L.dp("rf_brazier", 82, 34, 3)
    L.dp("rf_brazier", 91, 36, 3)
    L.dp("vot_war_banner", 84, 24, 5)
    L.dp("vot_war_banner", 92, 24, 5)
    L.dp("weapon_rack", 100, 30, 3)
    P("br_signpost", 120, 36, 5)

    # ---- Bael Modan: stepped quarry round a flooded pit --------------------------------------
    for (x, y) in [(48, 52), (52, 66), (46, 72)]:
        L.bld("generic_tent_a", x, y, 5)
    L.dp("vot_fire_pit", 50, 60, 2, solid=False)
    L.dp("rf_ore_cart", 56, 54, 3)
    L.dp("rf_ore_cart", 24, 82, 3)
    L.dp("rf_tool_rack", 44, 66, 3)
    L.dp("rf_tool_rack", 20, 56, 3)
    L.dp("rf_supply_crates", 53, 62, 3)
    L.dp("rf_supply_crates", 37, 80, 3)
    L.dp("rf_supply_crates", 18, 70, 3)
    L.dp("rf_golem_husk", 42, 52, 5)
    L.dp("rf_fallen_pillar", 24, 46, 4)
    L.dp("rf_fallen_pillar", 16, 62, 4)
    L.dp("broken_column", 30, 84, 4)
    L.dp("broken_column", 12, 76, 4)
    L.dp("rf_brazier", 36, 74, 3)
    L.dp("rf_brazier", 27, 52, 3)
    L.dp("den_rock_rubble", 22, 66, 3, solid=False)
    L.dp("den_rock_rubble", 44, 60, 3, solid=False)
    P("br_signpost", 60, 56, 5)

    # ---- Blackthorn Ridge: a Razormane camp in the broken ground -----------------------------
    for (x, y) in [(40, 104), (50, 102), (46, 112), (36, 98)]:
        P("br_quilboar_hut", x, y, 6)
    L.dp("vot_fire_pit", 45, 106, 2, solid=False)
    L.dp("vot_hide_rack", 52, 108, 3)
    P("br_razorfen_bramble_gate", 70, 118, 6, solid=False, road_ok=True)
    _grove(L, THORNS + DEAD, 56, 104, 30, 14, 12, 61, gap=4.0)
    for (x, y) in [(28, 92), (62, 88), (80, 104), (70, 96)]:
        L.dp("vot_thornbush", x, y, 3)

    # ---- Razorfen approach: the thorn horseshoe -----------------------------------------------
    P("br_razorfen_bramble_gate", 58, 146, 6, solid=False, road_ok=True)
    for (x, y) in [(44, 158), (68, 158), (42, 170), (70, 168), (62, 182)]:
        P("br_quilboar_hut", x, y, 6)
    L.dp("vot_fire_pit", 55, 163, 2, solid=False)
    L.dp("vot_hide_rack", 49, 165, 3)
    L.dp("vot_beast_ribcage", 66, 175, 3)
    P("br_termite_mound", 40, 184, 5)
    P("br_vulture_roost", 74, 180, 4)
    _grove(L, THORNS, 58, 166, 20, 14, 8, 62, gap=4.0)
    P("br_signpost", 62, 138, 5)

    # ---- The Giant's Road across the Rift: waystone camp at the north ramp -------------------
    P("br_tauren_tipi", 139, 118, 6)
    L.dp("vot_fire_pit", 136, 121, 2, solid=False)
    P("br_caravan_wagon", 120, 124, 4)
    P("br_signpost", 132, 112, 5)

    # ---- Raptor Grounds: the valley -------------------------------------------------------------
    for (x, y) in [(232, 94), (238, 102), (226, 108), (236, 110), (246, 100), (220, 112)]:
        P("br_raptor_nest", x, y, 3)
    P("br_vulture_roost", 244, 92, 4)
    P("br_vulture_roost", 230, 114, 4)
    P("br_tumbleweed_bones", 240, 106, 3)
    P("br_termite_mound", 204, 110, 5)
    P("br_dead_tree_vulture", 218, 90, 7)
    P("br_dead_tree_vulture", 242, 112, 7)
    P("br_sandstone_spire", 200, 90, 7)
    P("br_sandstone_spire", 248, 106, 7)
    _grove(L, SCRUB + TUFTS, 224, 102, 22, 9, 10, 71, gap=3.5, solid=False)

    # ---- Field of Giants: bone plain ------------------------------------------------------------
    P("br_kodo_tusk_gate", 124, 168, 9, solid=False, road_ok=True)
    L.dp("vot_beast_ribcage", 110, 192, 9)
    L.dp("vot_beast_ribcage", 142, 200, 9)
    L.dp("vot_beast_ribcage", 150, 176, 8)
    L.dp("vot_beast_ribcage", 176, 200, 8)
    L.dp("vot_beast_ribcage", 96, 170, 7)
    for (x, y, n, h) in [(106, 176, "br_kodo_skeleton", 5), (132, 210, "br_kodo_skeleton", 5),
                         (160, 194, "br_kodo_skeleton", 5), (186, 190, "br_kodo_skeleton", 5),
                         (118, 204, "br_kodo_skeleton", 5), (140, 168, "br_kodo_skeleton", 4),
                         (130, 180, "kodo_skull", 4), (152, 208, "kodo_skull", 4),
                         (100, 198, "kodo_skull", 4), (176, 170, "kodo_skull", 4),
                         (190, 204, "br_vulture_roost", 4), (112, 214, "br_vulture_roost", 4),
                         (136, 190, "br_dead_tree_vulture", 7), (168, 210, "br_dead_tree_vulture", 7),
                         (96, 188, "br_dead_tree_vulture", 7), (182, 176, "br_dead_tree_vulture", 7)]:
        P(n, x, y, h)
    _grove(L, BONES + ROCKS, 142, 190, 40, 16, 12, 81, gap=5.0, solid="core")
    P("br_signpost", 126, 196, 5)

    # ---- Broodspiral crater ---------------------------------------------------------------------
    for (x, y) in [(212, 207), (232, 207), (213, 218), (234, 218)]:
        L.dp("den_burrow_hole", x, y, 3, solid=False)
    for (x, y) in [(211, 213), (233, 213), (226, 205)]:
        L.dp("den_nest_mound", x, y, 4)
    L.dp("den_chitin_husk", 219, 207, 3)
    L.dp("den_chitin_husk", 231, 220, 3)
    L.dp("den_egg_cluster", 215, 221, 3)
    L.dp("den_leg_bones", 229, 209, 3, solid=False)
    L.dp("den_eggshell_pile", 234, 224, 3, solid=False)
    P("br_signpost", 206, 220, 5)

    # ---- NE hoodoos and the lonely camps -----------------------------------------------------------
    for (x, y, h) in [(206, 54, 8), (216, 62, 7), (224, 50, 8), (232, 66, 7), (196, 74, 7), (240, 48, 7)]:
        P("br_sandstone_spire", x, y, h)
    P("br_sandstone_arch", 212, 46, 6, solid="core", fraction=0.3)
    P("br_sandstone_arch", 188, 62, 6, solid="core", fraction=0.3)
    # hunter's blind at the end of the north spur
    P("br_tauren_tipi", 192, 44, 6)
    P("br_tauren_tipi", 198, 48, 6)
    L.dp("vot_hide_rack", 194, 50, 3)
    L.dp("vot_fire_pit", 196, 46, 2, solid=False)
    # wrecked dwarven caravan
    P("br_caravan_wagon", 176, 62, 4)
    L.dp("rf_supply_crates", 172, 64, 3)
    L.dp("rf_ore_cart", 182, 60, 3)
    P("br_kodo_skeleton", 168, 68, 4)

    # ---- the Rift floor: bones and boulders in the gravel ---------------------------------------
    for (x, y, n, h) in [(30, 138, "br_tumbleweed_bones", 3), (76, 134, "br_driftwood_skull", 3),
                         (96, 138, "br_sandstone_boulders", 4), (150, 134, "kodo_skull", 3),
                         (184, 138, "br_tumbleweed_bones", 3), (206, 140, "br_sandstone_boulders", 4),
                         (240, 140, "br_driftwood_skull", 3), (60, 133, "br_dead_tree_vulture", 7),
                         (118, 130, "br_dead_tree_vulture", 7)]:
        P(n, x, y, h)

    # ---- quest hubs: small camps round the givers ----------------------------------------------------------
    # Rift Waystation (north ramp): the Horde's one proper foothold south of Taurajo
    L.bld("generic_tent_a", 143, 114, 5)
    L.bld("generic_tent_b", 131, 119, 5)
    L.dp("vot_hide_rack", 135, 113, 3)
    L.dp("vot_crate_stack", 146, 121, 3)
    P("br_hitching_trough", 144, 124, 3)
    P("br_tauren_totem", 140, 110, 7)
    # Field of Giants gate: bone-hunter's camp
    L.bld("generic_tent_b", 133, 170, 5)
    L.dp("vot_fire_pit", 129, 175, 2, solid=False)
    L.dp("vot_hide_rack", 121, 173, 3)
    L.dp("vot_crate_stack", 134, 176, 3)
    # Razorfen approach: Thornwatch post
    L.bld("generic_tent_a", 67, 141, 5)
    L.dp("vot_fire_pit", 59, 143, 2, solid=False)
    L.dp("vot_palisade", 56, 140, 3, solid=True)
    L.dp("vot_palisade", 59, 139, 3, solid=True)
    L.dp("vot_war_banner", 66, 137, 5)
    # Bael'dun east gate: the spy's lean-to
    L.bld("generic_tent_b", 125, 43, 5)
    L.dp("vot_crate_stack", 119, 45, 3)
    L.dp("vot_fire_pit", 123, 38, 2, solid=False)
    # Bael Modan rim: the scout's dig watch
    L.bld("generic_tent_a", 67, 60, 5)
    L.dp("vot_fire_pit", 62, 61, 2, solid=False)
    L.dp("rf_tool_rack", 68, 55, 3)
    # Sinkhole rim: goblin dig camp
    L.bld("generic_tent_a", 212, 226, 5)
    L.dp("vot_crate_stack", 206, 225, 3)
    L.dp("rf_ore_cart", 213, 220, 3)
    L.dp("vot_fire_pit", 209, 227, 2, solid=False)

    # ---- groves: acacias are rare down here, thorn and scrub rule ----------------------------------
    for (cx, cy, rx, ry, n, sd) in [(150, 60, 14, 12, 4, 21), (110, 92, 12, 8, 4, 22),
                                    (160, 112, 12, 8, 3, 23), (100, 150, 10, 8, 3, 24)]:
        _grove(L, ACACIAS, cx, cy, rx, ry, n, sd, gap=8)
    for (cx, cy, rx, ry, n, sd) in [(64, 80, 12, 8, 6, 31), (170, 80, 14, 10, 6, 32), (30, 150, 10, 10, 5, 33),
                                    (24, 210, 10, 8, 5, 34), (86, 220, 14, 6, 5, 35), (200, 150, 12, 10, 6, 36),
                                    (250, 160, 5, 14, 4, 37), (112, 52, 10, 8, 5, 38), (152, 24, 12, 8, 5, 39),
                                    (180, 226, 12, 6, 5, 40)]:
        _grove(L, SCRUB + ROCKS, cx, cy, rx, ry, n, sd, gap=4, solid="core")
    for (cx, cy, rx, ry, n, sd) in [(150, 80, 24, 16, 9, 51), (100, 130, 20, 8, 6, 52), (180, 160, 22, 12, 8, 53),
                                    (70, 210, 24, 12, 7, 54), (30, 120, 12, 10, 4, 55)]:
        _grove(L, TUFTS, cx, cy, rx, ry, n, sd, gap=3.5, solid=False)


def _chests(L):
    for (x, y) in [(24, 74), (100, 22), (88, 135), (240, 98), (70, 172), (172, 188), (214, 222),
                   (212, 58), (32, 106), (30, 216), (246, 168), (146, 50)]:
        L.chest(x, y)


def build_layout():
    L = SLayout()
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
                raise FileNotFoundError(f"{fn} - run python3 tools/bake_southern_barrens.py")
            w, h = min(chunk, W - cx), min(chunk, H - cy)
            zone.add_ground_chunk(fn, cx, cy, w, h)
            zone.ground_chunks[-1]["exact"] = True
            zone.add_water_chunk(fn, cx, cy, w, h)
            zone.add_obstacle_chunk(fn, cx, cy, w, h)


def generate_southern_barrens():
    L = build_layout()
    register_baked(L.zone)
    return L.zone
