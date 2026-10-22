"""
Hand-built Deathknell (100x90): the Forsaken starter hollow, levels 1-5.

A cliff-ringed valley of sallow grass and dead timber.  The newly risen wake in the SHADOW GRAVE (a walled crypt-yard, south), walk
north through the DEATHKNELL GRAVES (the mass-grave field) to the ruined village and its square, and from there three roads fan out:
    NW  -> THE OVERRUN CLAIM, the spider-ridden goldmine (cave: Night Web's Hollow)
    NE  -> the Scarlet-held crypt on the hill (cave: Scarlet Crypt)
    E   -> the cliff pass out to Tirisfal (Western Tirisfal / Brill)
plus a spur south-east to a burned farmstead, and a stagnant pond on the west side.

Same recipe as Valley of Trials / Razor Hill (claude/zone_perfection_playbook.md): this module owns the TILE data and the analytic
landform fields (`fields`) the baker paints from (tools/bake_deathknell.py), so collision and painting cannot drift apart.

HARD CONTRACTS (world/portal_manager.py)
  portals  Night Web's Hollow (17,21)  Scarlet Crypt (83,19)  Western Tirisfal (96,47)
  NPC ids  referenced by data/quests/forsaken_lands.json - positions below are written back to data/npcs/*.json by
           tools/sync_deathknell_npcs.py
"""
import math
import os

import numpy as np
from PIL import Image

from world.tilemap import Tilemap

BLD = "assets/buildings/"
ENT = "assets/tiles/cave_entrances/"
EKP = "assets/tiles/eastern_kingdoms/props/"
HFP = "assets/tiles/haunted_forest/props/"
CIP = "assets/tiles/cursed_isle/props/"
GP = "assets/tiles/goblin_shared/props/"
BAKED_DIR = "assets/tiles/deathknell/baked"
W, H = 100, 90

PORTALS = {"nwh": (17, 21), "crypt": (83, 19), "exit": (96, 47)}

# roads: waypoints (tile coords), width in tiles.  Cave roads end one tile SOUTH of the portal so the mouth faces the approach.
ROADS = {
    "spine":  ([(50, 69), (50, 62), (50, 54), (50, 47), (50, 44)], 3.2),
    "east":   ([(54, 44), (64, 45), (75, 47), (86, 47), (96, 48)], 3.0),
    "claim":  ([(47, 40), (39, 34), (30, 29), (22, 25), (17, 23)], 2.6),
    "crypt":  ([(55, 38), (65, 31), (75, 25), (83, 21)], 2.6),
    "farm":   ([(55, 50), (64, 58), (72, 64), (77, 68)], 2.2),
}
PLAZA = (50, 42, 8.5, 5.5)          # cx, cy, rx, ry   (village square)
GRAVES = (50, 57, 12.0, 6.5)        # the mass-grave field
YARD = (50, 76, 14.0, 8.0)          # Shadow Grave crypt-yard
CLAIM = (19, 21, 10.0, 7.0)         # goldmine camp
CRYPT = (82, 21, 9.0, 6.5)          # Scarlet crypt forecourt
FARM = (77, 70, 8.5, 6.0)           # burned farmstead
POND = (24, 62, 9.0, 6.0)           # stagnant pond (cx, cy, rx, ry)
OUTCROPS = [(68, 36, 3.4, 2.6), (30, 36, 2.6, 2.2), (10, 40, 2.8, 3.4)]


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


def _clear(gx, gy, cx, cy, rx, ry, k=5.0):
    return (1.0 - np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)) * k


def _lobe(gx, gy, cx, cy, rx, ry, rot=0.0):
    """Valley-floor lobe: tile-distance-ish positive inside, negative outside."""
    dx, dy = gx - cx, gy - cy
    if rot:
        c, s = math.cos(rot), math.sin(rot)
        dx, dy = c * dx + s * dy, -s * dx + c * dy
    return (1.0 - np.sqrt((dx / rx) ** 2 + (dy / ry) ** 2)) * min(rx, ry)


def _seg(gx, gy, x0, y0, x1, y1):
    vx, vy = x1 - x0, y1 - y0
    t = np.clip(((gx - x0) * vx + (gy - y0) * vy) / (vx * vx + vy * vy), 0.0, 1.0)
    return np.hypot(gx - (x0 + t * vx), gy - (y0 + t * vy))


# valley-floor lobes: (cx, cy, rx, ry, rot)
LOBES = [
    (47, 40, 27, 16, 0.10),     # village basin
    (51, 57, 21, 12, -0.10),    # the graves
    (50, 77, 19, 10, 0.0),      # Shadow Grave yard
    (20, 22, 15, 11, 0.35),     # the claim
    (82, 22, 12, 10, -0.3),     # Scarlet forecourt
    (76, 69, 14, 11, 0.25),     # the farmstead
    (22, 62, 15, 12, 0.0),      # pond hollow
    (80, 46, 18, 7, 0.0),       # the pass
]
# rock spurs reaching in from the rim: (x0, y0, x1, y1, half_thickness)
SPURS = [
    (4, 47, 26, 49, 2.6),       # splits the pond hollow from the village basin (gap east of it)
    (96, 58, 74, 55, 2.4),      # keeps the pass apart from the farm (gap at its tip)
]


def cliff_field(gx, gy):
    """>0 inside rock (tiles), <0 on the valley floor."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    floor = np.maximum.reduce([_lobe(gx, gy, *l) for l in LOBES])
    floor = floor + 1.5 * _wob(gx * 0.6, gy * 0.6) + 1.0 * _wob(gx, gy)
    floor = np.maximum(floor, road_dist(gx, gy) + 2.2)          # roads keep a clear corridor
    rock = -floor
    for (x0, y0, x1, y1, t) in SPURS:
        rock = np.maximum(rock, (t - _seg(gx, gy, x0, y0, x1, y1)) * 1.2 + 0.25 * _wob(gx * 1.7, gy * 1.7))
    for (cx, cy, rx, ry) in OUTCROPS:                           # rock stacks standing in the valley
        rock = np.maximum(rock, _clear(gx, gy, cx, cy, rx, ry, 3.0) - 0.2)
    # roads, plazas and cave forecourts must stay open
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    return rock


def pond_field(gx, gy):
    """>0 in the pond; >0.45 = deep (impassable), 0..0.45 = shallow (wadeable)."""
    cx, cy, rx, ry = POND
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    r = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
    return (1.0 - r) + 0.07 * _wob(gx * 1.3, gy * 1.3)


def fields(gx, gy):
    return dict(cliff=cliff_field(gx, gy), pond=pond_field(gx, gy))


_ASPECT = {}


def _aspect(path):
    if path not in _ASPECT:
        with Image.open(path) as im:
            _ASPECT[path] = im.size[0] / im.size[1]
    return _ASPECT[path]


# ----------------------------------------------------------------- NPC spots
NPC_POSITIONS = {
    "dk_quest_overseer": (50, 38),        # Overseer Krell, outside the town hall's south face
    "dk_elder": (43, 42),                 # Death Knight Instructor, on the square
    "dk_risen": (53, 60),                 # the Newly Risen, among the graves
    "deathknell_undertaker": (58, 41),    # Undertaker Mordo (vendor), beside the chapel
    "dk_foreman_gresk": (23, 24),         # Foreman Gresk, at the Overrun Claim's mine camp
    "dk_mourner_isolde": (34, 58),        # Mourner Isolde, on the Weeping Pond's bank
    "dk_gardener_orrel": (73, 68),        # Gardener Orrel, among the burned farmstead's furrows
    "dk_scout_verrick": (72, 28),         # Scout Verrick, watching the Scarlet forecourt from the rocks
    "dk_sexton_marrow": (47, 72),         # Sexton Marrow, in the Shadow Grave crypt-yard
}
# fixed spawn points (data/creatures/spawn_points.json) - kept on open ground away from roads and props
SPAWNS = [("Mangy Duskbat", 41, 27), ("Mangy Duskbat", 66, 27), ("Mangy Duskbat", 18, 70),
          ("Ragged Scavenger", 33, 44), ("Ragged Scavenger", 63, 53)]
CHESTS = [(33, 52), (60, 80), (23, 18), (88, 27), (80, 72)]


class Layout:
    def __init__(self):
        self.zone = Tilemap("Deathknell", W, H, "A small undead settlement. The dead walk here.")
        self.z = self.zone
        self.z.region = "Eastern Kingdoms - Lordaeron"
        self.skipped = []
        self.placed = 0
        self.chests = []
        self.npc_xy = list(NPC_POSITIONS.values())
        ys, xs = np.mgrid[0:H, 0:W]
        self.pond = pond_field(xs + 0.5, ys + 0.5)
        self.rd = road_dist(xs + 0.5, ys + 0.5)

    def road_clear(self, x, y, margin=0.9):
        return self.rd[y, x] < -margin

    def _try(self, wt, height, cx, base_y, solid, fraction, road_ok, allow_overlap, portal_ok):
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
            if z.base_layer[y][x] in ("deep_water", "shallow_water"):
                return "water", core, ax, ay
            if any(abs(x - nx) <= 1 and abs(y - ny) <= 1 for nx, ny in self.npc_xy):
                return "NPC", core, ax, ay
            if not portal_ok and any(abs(x - px) <= 2 and abs(y - py) <= 2 for px, py in PORTALS.values()):
                return "portal", core, ax, ay
            if not road_ok and not self.road_clear(x, y, 0.6):
                return "road", core, ax, ay
        return None, core, ax, ay

    def prop(self, name, cx, base_y, height, solid="core", fraction=0.4, road_ok=False,
             path_dir=EKP, allow_overlap=False, nudge=2, portal_ok=False):
        path = name if "/" in name else f"{path_dir}{name}.png"
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        z = self.z
        wt = max(1, round(height * _aspect(path)))
        offs = sorted(((dx, dy) for dx in range(-nudge, nudge + 1) for dy in range(-nudge, nudge + 1)),
                      key=lambda d: (d[0] ** 2 + d[1] ** 2, abs(d[0])))
        first_bad = None
        for (dx, dy) in offs:
            bad, core, ax, ay = self._try(wt, height, cx + dx, base_y + dy, solid, fraction,
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
        self.skipped.append((os.path.basename(path), cx, base_y, first_bad))
        return False

    def bld(self, name, cx, base_y, height, **kw):
        kw.setdefault("path_dir", BLD)
        kw.setdefault("fraction", 0.5)
        return self.prop(name, cx, base_y, height, **kw)

    def row(self, name, xs, base_y, height, **kw):
        return sum(bool(self.prop(name, x, base_y, height, **kw)) for x in xs)

    def cave(self, key, sprite, w, h):
        """Cave-mouth art standing on the portal tile: the mouth is the bottom-centre tile."""
        px, py = PORTALS[key]
        z = self.z
        z.add_landmark(f"{ENT}{sprite}.png", px - w // 2, py - h + 1, w, h, mouth_offset=(w // 2, h - 1))

    def chest(self, x, y):
        z = self.z
        for r in range(0, 7):
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


def _terrain(L):
    z = L.z
    z.fill("grass", "base")
    ys, xs = np.mgrid[0:H, 0:W]
    cl = cliff_field(xs + 0.5, ys + 0.5)
    pf = pond_field(xs + 0.5, ys + 0.5)
    for y in range(H):
        for x in range(W):
            if cl[y, x] > 0:
                z.set_tile(x, y, "cliff", "collision")
            elif pf[y, x] > 0.45:
                z.set_tile(x, y, "deep_water", "base")
            elif pf[y, x] > 0.0:
                z.set_tile(x, y, "shallow_water", "base")
            elif L.rd[y, x] > 0:
                z.set_tile(x, y, "path", "base")
    # plaza paving + graveyard earth are painted; base layer marks them as path / stone for footsteps
    cx, cy, rx, ry = PLAZA
    for y in range(H):
        for x in range(W):
            if z.collision_layer[y][x] is None and z.base_layer[y][x] == "grass" and \
                    ((x + .5 - cx) / rx) ** 2 + ((y + .5 - cy) / ry) ** 2 < 1:
                z.set_tile(x, y, "path", "base")


def _portals(L):
    z = L.z
    for key, (px, py) in PORTALS.items():
        z.collision_layer[py][px] = None
        z.set_tile(px, py, "portal", "interaction")


def _subzones(L):
    z = L.z
    z.add_subzone("Shadow Grave", 33, 66, 34, 20)
    z.add_subzone("Deathknell Graves", 36, 50, 28, 15)
    z.add_subzone("The Overrun Claim", 7, 11, 26, 20)
    z.add_subzone("Weeping Pond", 13, 55, 23, 13, display_name="The Weeping Pond")
    z.add_subzone("Burned Farmstead", 68, 64, 18, 13, display_name="The Burned Farmstead")
    z.add_subzone("Scarlet Forecourt", 72, 15, 19, 15)


def _dress(L):
    p, b, row = L.prop, L.bld, L.row
    # ---- the village square: town hall north of the square, chapel + houses around it
    b("forsaken_town_hall", 50, 36, 10, road_ok=False, nudge=1)
    b("crypt_chapel", 63, 40, 9, nudge=1)
    b("forsaken_house_small", 37, 40, 8, nudge=1)
    b("forsaken_house_medium", 38, 49, 9, nudge=1)
    b("forsaken_house_small", 62, 50, 8, nudge=1)
    b("gallows_post", 56, 47, 6, nudge=1, road_ok=True)
    p("ek_farm_well", 46, 44, 4, nudge=1)
    p("ek_forsaken_banner", 44, 36, 5, nudge=2)
    p("ek_forsaken_banner", 55, 38, 5, nudge=2)
    p("ek_signpost", 59, 49, 4, nudge=2)
    p("ek_plague_cauldron", 58, 38, 3, nudge=1)
    p("ek_pillory", 54, 41, 4, nudge=1)
    p("ek_plague_cart", 44, 47, 4, nudge=1)
    # ---- the Deathknell Graves: rows of stones, open graves, one angel
    for (x, y) in [(41, 55), (45, 58), (55, 55), (59, 58), (42, 61), (58, 62)]:
        p(CIP + "worn_tombstone_row.png", x, y, 3, nudge=1)
    p("ek_open_grave", 47, 54, 3, nudge=1)
    p("ek_open_grave", 56, 60, 3, nudge=1)
    p("ek_grave_hand", 44, 52, 3, nudge=1)
    p("ek_cross_crows", 54, 53, 4, nudge=1)
    p("ek_angel_statue", 45, 57, 6, nudge=2)
    # ---- the Shadow Grave: gate, fence either side, the mausoleum where you wake
    p("ek_cemetery_gate", 50, 68, 5, nudge=0, road_ok=True, allow_overlap=True)
    for x in (44, 56):
        p("ek_cemetery_fence", x, 69, 3, nudge=1, solid=True)
    p(HFP + "crypt_mausoleum.png", 50, 79, 9, nudge=1, road_ok=True, fraction=0.5)
    p("ek_open_grave", 42, 74, 3, nudge=1)
    p("ek_open_grave", 58, 76, 3, nudge=1)
    p("ek_cross_crows", 40, 80, 4, nudge=1)
    p("ek_cross_crows", 60, 71, 4, nudge=1)
    p("ek_gibbet", 62, 78, 6, nudge=1)
    # ---- the Overrun Claim: collapsed mine mouth, rails, tailings, web
    L.cave("nwh", "ent_spider_lair", 7, 5)
    p(GP + "gob_mine_frame.png", 26, 22, 5, nudge=2)
    p(GP + "gob_ore_cart.png", 14, 26, 3, nudge=1, path_dir="")
    p(GP + "gob_ore_pile.png", 25, 20, 3, nudge=1, path_dir="")
    p("ek_egg_sacs", 12, 22, 4, nudge=1)
    p("ek_web_boulder", 22, 16, 4, nudge=1)
    p("ek_toadstools", 27, 23, 2, nudge=1, solid=False)
    p(HFP + "twisted_root_arch.png", 9, 28, 6, nudge=2)
    # ---- the Scarlet forecourt: gate, banners, tent, crates, ruined wall
    L.cave("crypt", "ent_scarlet_gate", 7, 5)
    p("ek_scarlet_banner", 78, 22, 5, nudge=1)
    p("ek_scarlet_banner", 88, 22, 5, nudge=1)
    p("ek_scarlet_tent", 87, 27, 6, nudge=2)
    p("ek_scarlet_crates", 78, 28, 3, nudge=1)
    p("ek_ruin_wall", 70, 22, 4, nudge=2)
    p("ek_ruin_wall", 92, 20, 4, nudge=2)
    # ---- the burned farmstead
    p(HFP + "burned_house_ruin.png", 79, 66, 7, nudge=1)
    p("ek_haystack", 72, 72, 4, nudge=1)
    p("ek_scarecrow", 82, 74, 4, nudge=1)
    p("ek_farm_cart", 71, 66, 4, nudge=1)
    for x in (76, 80, 84):
        p("ek_farm_fence", x, 77, 3, nudge=1, solid=True)
    # ---- the pond: reeds, willow, toadstools
    p(HFP + "bog_reeds_cluster.png", 17, 57, 3, nudge=1, solid=False)
    p(HFP + "bog_reeds_cluster.png", 31, 66, 3, nudge=1, solid=False)
    p("ek_willow", 16, 66, 7, nudge=2)
    p("ek_toadstools", 30, 58, 2, nudge=1, solid=False)
    # ---- the pass out: signpost and a gibbet warning
    p("ek_signpost", 90, 50, 4, nudge=1)
    p("ek_forsaken_banner", 92, 45, 5, nudge=1, road_ok=False)


def _forest(L, seed=11):
    """Dead timber and thorn around the valley, explicit but seeded: dense along the cliff rim, sparse towards the paths."""
    rng = np.random.default_rng(seed)
    z = L.z
    cl = cliff_field(*np.meshgrid(np.arange(W) + 0.5, np.arange(H) + 0.5))
    # distance from rock, in tiles (crudely: how deep a floor tile is)
    from scipy import ndimage as ndi
    floor = (cl <= 0)
    d_rock = ndi.distance_transform_edt(floor)
    names = [("ek_dead_oak", 6, 0.34), ("ek_dead_oak", 6, 0.34), (HFP + "dead_pine_cluster.png", 5, 0.40), (HFP + "dead_pine_cluster.png", 5, 0.40), (CIP + "cursed_dead_tree_cluster.png", 4, 0.40)]
    tries = 0
    count = 0
    while count < 34 and tries < 4000:
        tries += 1
        x, y = int(rng.integers(3, W - 3)), int(rng.integers(3, H - 3))
        if not floor[y, x] or d_rock[y, x] > 9:
            continue
        if d_rock[y, x] > 5 and rng.random() < 0.8:
            continue
        nm, hh, fr = names[int(rng.integers(0, len(names)))]
        if L.prop(nm, x, y, hh, fraction=fr, nudge=0):
            count += 1
    for _ in range(14):
        x, y = int(rng.integers(4, W - 4)), int(rng.integers(4, H - 4))
        if floor[y, x]:
            L.prop("ek_thorn_bush", x, y, 2, solid=False, nudge=0)


def _seal_pockets(L, start=(50, 66)):
    """Any walkable tile the spine cannot reach (a sliver the rock field cut off) becomes rock, so nothing is unreachable."""
    from collections import deque
    z = L.z
    seen = {start}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and z.is_walkable(*n):
                seen.add(n)
                q.append(n)
    for y in range(H):
        for x in range(W):
            if z.is_walkable(x, y) and (x, y) not in seen:
                z.collision_layer[y][x] = "cliff"
                z.interaction_layer[y][x] = None


def build_layout():
    L = Layout()
    _terrain(L)
    _portals(L)
    _subzones(L)
    for (x, y) in NPC_POSITIONS.values():
        L.z.set_tile(x, y, "npc", "interaction")
    _dress(L)
    _forest(L)
    for (x, y) in CHESTS:
        L.chest(x, y)
    _seal_pockets(L)
    return L


def shape_preview(path, scale=10):
    ys, xs = np.mgrid[0:H, 0:W]
    f = fields(xs + 0.5, ys + 0.5)
    img = np.zeros((H, W, 3), np.uint8)
    img[:] = (120, 130, 70)
    img[f["cliff"] > 0] = (70, 60, 55)
    rd = road_dist(xs + 0.5, ys + 0.5)
    img[(rd > 0) & (f["cliff"] <= 0)] = (200, 180, 120)
    img[(f["pond"] > 0)] = (60, 110, 120)
    img[(f["pond"] > 0.45)] = (20, 50, 70)
    for (x, y) in PORTALS.values():
        img[y, x] = (255, 0, 255)
    for (x, y) in NPC_POSITIONS.values():
        img[y, x] = (30, 200, 255)
    Image.fromarray(img).resize((W * scale, H * scale), Image.NEAREST).save(path)


def register_baked(zone, baked_dir=BAKED_DIR, chunk=20):
    """Register the baked painting as ground + water + obstacle chunks."""
    for cy in range(0, H, chunk):
        for cx in range(0, W, chunk):
            fn = f"{baked_dir}/ground_{cx}_{cy}.jpg"
            if not os.path.exists(fn):
                raise FileNotFoundError(f"{fn} - run python3 tools/bake_deathknell.py")
            w, h = min(chunk, W - cx), min(chunk, H - cy)
            zone.add_ground_chunk(fn, cx, cy, w, h)
            zone.ground_chunks[-1]["exact"] = True
            zone.add_water_chunk(fn, cx, cy, w, h)
            zone.add_obstacle_chunk(fn, cx, cy, w, h)


def generate_deathknell():
    L = build_layout()
    register_baked(L.zone)
    return L.zone
