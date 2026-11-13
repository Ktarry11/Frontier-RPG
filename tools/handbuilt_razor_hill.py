"""
Hand-built Razor Hill (60x60): the Horde's hilltop crossroads fort in central
Durotar.  A squarish plateau of red clay ringed by cliff, a palisade wall and
gatehouse across the south approach, a main road running north to the
barracks, a plaza with the fire pit at its heart, the inn / smithy / training
yard / market around it, and a ragged refugee camp tucked in the south-east.

Same recipe as Valley of Trials / Durotar (see claude/zone_perfection_playbook.md):
this module owns the TILE data and the analytic landform fields the baker
(tools/bake_razor_hill.py) paints from, so collision and painting can't drift.

HARD CONTRACTS
  portal   (30,55) -> Durotar (65,108)   (world/portal_manager.py)
  NPC ids  are referenced by data/quests/razor_hill.json - positions below are
           written back to data/npcs/*.json by tools/sync_razor_hill_npcs.py
"""
import math
import os

import numpy as np
from PIL import Image

from world.tilemap import Tilemap

DP = "assets/tiles/dungeon_props/"
BLD = "assets/buildings/"
BAKED_DIR = "assets/tiles/razor_hill/baked"
W, H = 60, 60
PORTAL = (30, 55)

# roads: waypoints (tile coords), width in tiles
ROADS = {
    "gate":   ([(30, 57), (30, 50), (30, 44), (30, 37)], 3.4),
    "spine":  ([(30, 37), (30, 30), (30, 22), (30, 17)], 3.2),
    "west":   ([(30, 33), (25, 34), (19, 35)], 2.2),
    "east":   ([(30, 30), (37, 30), (43, 29)], 2.2),
    "smithy": ([(24, 26), (19, 24), (14, 22)], 1.8),
    "yard":   ([(22, 40), (17, 43), (13, 46)], 1.8),
    "camp":   ([(33, 40), (37, 41), (41, 42)], 1.8),
}
PLAZA = (30, 30, 7.0, 5.6)      # cx, cy, rx, ry


def _wob(gx, gy):
    return (0.45 * np.sin(0.37 * gx + 1.3) * np.sin(0.29 * gy + 0.7)
            + 0.30 * np.sin(0.83 * gx + 0.21 * gy + 2.0)
            + 0.25 * np.sin(0.19 * gx - 0.57 * gy + 4.1))


_TREES = {}


def road_dist(gx, gy, names=None):
    from scipy.spatial import cKDTree
    from tools.terrain_painter import Painter
    q = np.stack([np.ravel(gx), np.ravel(gy)], 1)
    best = None
    for n in (names or ROADS):
        if n not in _TREES:
            pts, w = ROADS[n]
            _TREES[n] = (cKDTree(Painter.spline(pts)), w)
        tree, w = _TREES[n]
        d, _ = tree.query(q)
        e = (w * 0.5) - d
        best = e if best is None else np.maximum(best, e)
    return best.reshape(np.shape(gx))


def cliff_field(gx, gy):
    """>0 inside rock (tiles), <0 on the plateau."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    sq = (np.abs(gx - 30.0) / 26.0) ** 3.2 + (np.abs(gy - 26.5) / 22.5) ** 3.2
    plateau = (1.0 - sq ** (1 / 3.2)) * 22.0
    appr = (1.0 - np.sqrt(((gx - 30.0) / 8.0) ** 2 + ((gy - 53.0) / 4.8) ** 2)) * 4.8
    inside = np.maximum(plateau, appr)
    inside = np.maximum(inside, road_dist(gx, gy) + 2.0)        # roads keep a clear corridor
    inside = inside + 0.9 * _wob(gx, gy)
    return -inside


def fields(gx, gy):
    return dict(cliff=cliff_field(gx, gy))


_ASPECT = {}


def _aspect(path):
    if path not in _ASPECT:
        with Image.open(path) as im:
            _ASPECT[path] = im.size[0] / im.size[1]
    return _ASPECT[path]


# ----------------------------------------------------------------- NPC spots
NPC_POSITIONS = {
    "razorhill_guard_1": (27, 17),        # barracks door
    "razorhill_guard_2": (27, 51),        # gate sentries (outside the gatehouse)
    "razorhill_guard_3": (33, 51),
    "razorhill_smith": (14, 22),
    "razorhill_trainer": (15, 43),
    "razorhill_innkeep": (21, 32),
    "razorhill_goblin_trader": (48, 37),
    "razorhill_vendor": (41, 37),
    "razorhill_beltelf_scribe": (35, 25),
    "razorhill_human_defector": (34, 39),
    "razorhill_orc_farmer": (11, 36),
    "razorhill_child": (30, 38),
    "razorhill_elder_orc": (10, 30),
    "razorhill_goblin_engineer": (46, 25),
    "razorhill_troll_refugee": (47, 45),
}
RECRUITS = {"ama_priest": (30, 30)}
FORGE = (11, 22)


class Layout:
    def __init__(self):
        self.zone = Tilemap("Razor Hill", W, H,
                            "A frontier orc fort on a red-clay hill, hub of central Durotar.")
        self.z = self.zone
        self.z.region = "Durotar"
        self.skipped = []
        self.placed = 0
        self.npc_xy = list(NPC_POSITIONS.values()) + list(RECRUITS.values()) + [FORGE]

    def road_clear(self, x, y, margin=0.9):
        return road_dist(np.array([x + 0.5]), np.array([y + 0.5]))[0] < -margin

    def _try(self, path, wt, height, cx, base_y, solid, fraction, road_ok, allow_overlap, portal_ok=False):
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
            if any(abs(x - nx) <= 1 and abs(y - ny) <= 1 for nx, ny in self.npc_xy):
                return "NPC", core, ax, ay
            if not portal_ok and abs(x - PORTAL[0]) <= 2 and abs(y - PORTAL[1]) <= 2:
                return "portal", core, ax, ay
            if not road_ok and not self.road_clear(x, y, 0.6):
                return "road", core, ax, ay
        return None, core, ax, ay

    def prop(self, name, cx, base_y, height, solid="core", fraction=0.4, road_ok=False,
             path_dir=DP, allow_overlap=False, nudge=2, portal_ok=False):
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
                                          road_ok, allow_overlap, portal_ok)
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

    def rim_y(self, x):
        """Lowest plateau row at column x (for the palisade line)."""
        for y in range(H - 1, 0, -1):
            if self.z.collision_layer[y][x] is None and y < 52:
                return y
        return None


def _terrain(L):
    z = L.z
    z.fill("sand", "base")
    ys, xs = np.mgrid[0:H, 0:W]
    cl = cliff_field(xs + 0.5, ys + 0.5)
    rd = road_dist(xs + 0.5, ys + 0.5)
    for y in range(H):
        for x in range(W):
            if cl[y, x] > 0:
                z.set_tile(x, y, "cliff", "collision")
            elif rd[y, x] > 0:
                z.set_tile(x, y, "path", "base")
    # plaza paving (base layer only)
    cx, cy, rx, ry = PLAZA
    for y in range(H):
        for x in range(W):
            if z.collision_layer[y][x] is None and ((x + .5 - cx) / rx) ** 2 + ((y + .5 - cy) / ry) ** 2 < 1:
                z.set_tile(x, y, "path", "base")


def _portal(L):
    z = L.z
    px, py = PORTAL
    z.collision_layer[py][px] = None
    z.set_tile(px, py, "portal", "interaction")


def _dress(L):
    p, b = L.prop, L.bld
    z = L.z
    # ---- the south gate: palisade across the neck, gatehouse over the road
    b("palisade_gatehouse", 30, 49, 7, solid=False, road_ok=True, allow_overlap=True, nudge=0)
    b("watchtower", 21, 48, 9, nudge=1)
    b("watchtower", 39, 48, 9, nudge=1)
    for x in (13, 16, 18, 42, 44, 46):
        ry = L.rim_y(x)
        if ry:
            p("vot_palisade", x, ry - 1, 3, solid=True, nudge=1)
    # ---- the barracks and its parade ground (north)
    b("frontier_barracks", 30, 14, 9)
    b("watchtower", 11, 12, 9)
    b("watchtower", 49, 12, 9)
    b("plain_orc_house_a", 18, 11, 4)
    b("plain_orc_house_c", 42, 11, 5)
    p("vot_training_dummy", 20, 19, 3)
    p("vot_training_dummy", 23, 21, 3)
    p("vot_archery_target", 38, 20, 3)
    # ---- the plaza: fire pit, drum, banners, well
    p("vot_fire_pit", 30, 26, 3, road_ok=True)
    p("vot_war_drum", 25, 31, 3)
    p("vot_war_banner", 24, 27, 5)
    p("vot_war_banner", 36, 27, 5)
    p("vot_totem_pole", 35, 34, 6)
    b("well_house", 26, 40, 5, nudge=1)       # (29,36) was on the road and never appeared
    # ---- west: smithy, inn, elder, garden, training lodge + yard
    b("smithy", 13, 19, 7)
    p("vot_crate_stack", 18, 22, 3)
    p("bbc_weapon_rack", 8, 22, 3)
    b("crossroads_inn", 17, 31, 8)
    p("vot_hide_rack", 23, 28, 3)
    b("elders_tent", 8, 29, 5)
    p("vot_sagewood_sapling", 8, 37, 3, solid=False)
    p("vot_sagewood_sapling", 12, 39, 3, solid=False)
    b("trainers_lodge", 14, 41, 7)
    p("vot_training_dummy", 9, 46, 3)
    p("vot_training_dummy", 13, 47, 3)
    p("vot_archery_target", 18, 46, 3)
    p("vot_hide_rack", 9, 43, 3)
    # ---- east: market, engineer's workshop, shack, refugee camp
    b("trading_post", 44, 35, 6)
    p("vot_crate_stack", 50, 33, 3)
    b("bazaar_stall_row", 44, 40, 4)
    b("scrapyard_workshop", 46, 23, 6)
    p("vot_broken_cart", 44, 42, 3)
    b("generic_tent_b", 51, 44, 5)
    p("vot_fire_pit", 48, 43, 3)
    p("vot_hide_rack", 50, 48, 3)
    # ---- the scatter a real hill has: cactus, thorn, bones, a cairn
    for (x, y) in [(8, 17), (52, 20), (7, 41), (53, 36)]:
        p("vot_barrel_cactus", x, y, 3)
    for (x, y) in [(20, 14), (40, 15), (50, 28), (29, 41), (15, 26)]:
        p("vot_thornbush", x, y, 2, solid=False)
    p("vot_dead_tree", 9, 9, 6)
    p("vot_dead_tree", 53, 17, 6)
    p("vot_mesa_pillar", 53, 30, 6)
    p("vot_trail_cairn", 21, 51, 3)
    p("vot_trail_cairn", 40, 52, 3)
    p("vot_rock_arch", 30, 57, 7, solid=False, road_ok=True, portal_ok=True, allow_overlap=True, nudge=0)
    p("vot_war_banner", 26, 55, 5, portal_ok=True)
    p("vot_war_banner", 34, 55, 5, portal_ok=True)
    # forge fixed interaction tile (smelting) beside the smith
    fx, fy = FORGE
    z.collision_layer[fy][fx] = None


def build_layout():
    L = Layout()
    _terrain(L)
    _portal(L)
    _dress(L)
    return L


def shape_preview(path, scale=12):
    ys, xs = np.mgrid[0:H, 0:W]
    cl = cliff_field(xs + 0.5, ys + 0.5)
    img = np.zeros((H, W, 3), np.uint8)
    img[:] = (205, 130, 80)
    img[cl > 0] = (70, 50, 45)
    rd = road_dist(xs + 0.5, ys + 0.5)
    img[(rd > 0) & (cl <= 0)] = (235, 200, 120)
    img[PORTAL[1], PORTAL[0]] = (255, 0, 255)
    for (x, y) in NPC_POSITIONS.values():
        img[y, x] = (30, 200, 255)
    Image.fromarray(img).resize((W * scale, H * scale), Image.NEAREST).save(path)


def register_baked(zone, baked_dir=BAKED_DIR, chunk=20):
    """Register the baked painting as ground + water + obstacle chunks."""
    for cy in range(0, H, chunk):
        for cx in range(0, W, chunk):
            fn = f"{baked_dir}/ground_{cx}_{cy}.jpg"
            if not os.path.exists(fn):
                raise FileNotFoundError(f"{fn} - run python3 tools/bake_razor_hill.py")
            w, h = min(chunk, W - cx), min(chunk, H - cy)
            zone.add_ground_chunk(fn, cx, cy, w, h)
            zone.ground_chunks[-1]["exact"] = True
            zone.add_water_chunk(fn, cx, cy, w, h)
            zone.add_obstacle_chunk(fn, cx, cy, w, h)


def generate_razor_hill():
    L = build_layout()
    register_baked(L.zone)
    return L.zone
