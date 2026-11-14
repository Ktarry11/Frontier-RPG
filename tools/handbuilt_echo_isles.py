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
CP = "assets/tiles/coastal_props/"
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
    # SECRET ISLETS (tools/build_secrets.py, world/secrets.py). Kyle, 14 Nov: "a shallow water you can
    # walk to an island that doesn't even appear [on the map]". Real land, baked into the painting; the
    # map draws it and its ford as open sea. Don't describe where they are to Kyle.
    "secret_a": [(22, 10, 5.0, 4.0), (25, 8, 3.0, 2.6)],
    "secret_b": [(143, 147, 4.6, 3.8), (146, 149, 2.8, 2.4)],
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
#: THE SECRET ISLETS' WAYS OUT. Kyle, 14 Nov, on the first try: "they can't be that obvious. Tone shift
#: the natural water or put a bit of land under it. No one is going to call that a secret." So these
#: are WALKABLE (tile_kind makes them shallow) but PAINTED as deep sea, a shade lighter than the water
#: around them. You find them by looking hard or by walking where you shouldn't.
SECRET_FORDS = {
    "secret_a":  ([(24, 37), (23, 27), (22, 16)], 2.4),
    "secret_b":  ([(140, 119), (141, 130), (142, 141)], 2.4),
}


def secret_ford_field(gx, gy):
    best = np.full(np.shape(gx), -99.0)
    for n, (pts, w) in SECRET_FORDS.items():
        best = np.maximum(best, w * 0.5 - _poly_dist(("secret", n), pts, gx, gy))
    return best
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
    sford = secret_ford_field(gx, gy)
    deep = np.where(sford > 0, np.minimum(deep, 1.4), deep)   # painted deep, a shade lighter
    return dict(land=land, wet=wet, deep=deep, ford=ford, secret_ford=sford, deck=deck_field(gx, gy),
                bridge=bridge_field(gx, gy), rock=rock_field(gx, gy),
                rock_vis=rock_field(gx, gy, notch=False))


def tile_kind(gx, gy):
    """0 land, 1 shallow, 2 deep, 3 rock, 4 deck/bridge at tile centres."""
    f = fields(gx, gy)
    kind = np.zeros(np.shape(gx), int)
    kind[f["wet"] > 0] = 1
    kind[f["deep"] > 0] = 2
    kind[(f["secret_ford"] > 0) & (kind == 2)] = 1      # walkable, though it doesn't look it
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
    "echo_isles_camp_lookout": (82, 43),
    "echoisle_vendor": (82, 57),
    # Troll Camp isle
    "echo_isles_troll_beachcomber": (116, 56),
    "echo_isles_troll_healer": (121, 60),
    "echo_isles_troll_elder": (125, 54),
    # Hollow isle landing / Grotto isle
    "echo_isles_goblin_salvager": (130, 105),
    "echo_isles_shaman": (36, 87),
    "echo_isles_young_diver": (32, 93),
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
    L.cave(GROTTO[0], GROTTO[1], "ent_naga_temple_door", 8, 7)     # drowned naga doorway
    L.cave(HOLLOW[0], HOLLOW[1], "ent_troll_skull_cave", 8, 7)     # troll skull lair
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
    """Hand-placed props.  Less is more: each cluster is something the spot would
    really have (huts round a cook-fire, crates on a dock, coral in the shallows)."""
    cp = lambda n, x, y, h, **k: L.prop(n, x, y, h, path_dir=CP, **k)
    ep = lambda n, x, y, h, **k: L.prop(n, x, y, h, path_dir=EP, **k)
    dp = lambda n, x, y, h, **k: L.prop(n, x, y, h, path_dir=DP, **k)
    deck = dict(road_ok=True, solid=False)           # props that stand ON a pier

    # ---------------- piers: lanterns, mooring, crates (decks are walkable path tiles)
    for (x, y) in ((78, 16), (81, 16), (78, 26), (81, 26)):
        cp("dock_lantern_post", x, y, 4, **deck)
    cp("mooring_posts", 75, 10, 3, **deck)
    cp("mooring_posts", 86, 10, 3, **deck)
    cp("fish_crates_traps", 75, 5, 3, **deck)
    cp("fish_crates_traps", 85, 5, 3, **deck)
    for (x, y) in ((78, 136), (81, 136), (78, 144), (81, 144)):
        cp("dock_lantern_post", x, y, 4, **deck)
    cp("mooring_posts", 75, 152, 3, **deck)
    cp("mooring_posts", 86, 152, 3, **deck)
    cp("fish_crates_traps", 76, 156, 3, **deck)
    cp("outrigger_canoe", 70, 33, 3, shore_ok=True, solid=False)

    # ---------------- Echo Landing: the Darkspear village (north hub)
    cp("troll_stilt_hut", 71, 51, 7)
    cp("troll_stilt_hut", 89, 50, 7)
    cp("troll_stilt_hut", 72, 60, 7)
    cp("troll_stilt_hut", 88, 61, 7)
    cp("tiki_totem", 87, 40, 7)
    cp("troll_war_banner", 76, 46, 6)
    cp("troll_war_banner", 84, 47, 6)
    cp("troll_cookfire", 78, 56, 4, fraction=0.5)
    cp("fish_drying_rack", 85, 53, 4)
    cp("fish_crates_traps", 75, 62, 3)
    cp("signal_tower", 92, 36, 7)
    cp("outrigger_canoe", 63, 56, 3, shore_ok=True, solid=False)
    cp("hibiscus_bush", 74, 45, 3)
    cp("banana_plant", 69, 47, 4)
    cp("banana_plant", 91, 56, 4)
    cp("bamboo_grove", 66, 54, 5)
    ep("palm_lean_a", 64, 42, 6)
    ep("palm_lean_a", 94, 44, 6)
    ep("palm_lean_b", 67, 37, 6)
    ep("palm_lean_b", 96, 52, 6)

    # ---------------- Echo Landing: jungle interior (west/east/south)
    cp("jungle_banyan", 69, 72, 8)
    cp("jungle_banyan", 90, 74, 8)
    cp("jungle_banyan", 76, 84, 8)
    cp("jungle_banyan", 72, 108, 8)
    cp("jungle_banyan", 90, 108, 8)
    cp("mossy_jungle_boulder", 66, 66, 4)
    cp("mossy_jungle_boulder", 93, 79, 4)
    cp("mossy_jungle_boulder", 72, 100, 4)
    cp("bamboo_grove", 66, 80, 5)
    cp("bamboo_grove", 96, 92, 5)
    cp("hibiscus_bush", 74, 76, 3)
    cp("hibiscus_bush", 87, 70, 3)
    cp("hibiscus_bush", 78, 94, 3)
    cp("banana_plant", 70, 90, 4)
    cp("banana_plant", 92, 96, 4)
    cp("banana_plant", 84, 112, 4)
    ep("palm_lean_a", 60, 74, 6)
    ep("palm_lean_a", 98, 70, 6)
    ep("palm_lean_b", 62, 96, 6)
    ep("palm_lean_b", 100, 86, 6)
    ep("palm_lean_a", 96, 116, 6)
    ep("palm_lean_a", 66, 114, 6)
    cp("driftwood_pile", 99, 98, 3, shore_ok=True)
    cp("rowboat_wreck", 61, 82, 3, shore_ok=True)
    cp("driftwood_pile", 62, 106, 3, shore_ok=True)
    cp("mooring_posts", 98, 60, 3, shore_ok=True, solid=False)

    # ---------------- Troll Camp isle (east of the north bridge)
    cp("troll_stilt_hut", 119, 51, 7)
    cp("troll_stilt_hut", 132, 50, 7)
    cp("troll_stilt_hut", 133, 61, 7)
    cp("tiki_totem", 123, 51, 7)
    cp("tiki_totem", 114, 62, 7)
    cp("troll_war_banner", 116, 54, 6)
    cp("troll_war_banner", 116, 61, 6)
    cp("troll_cookfire", 126, 58, 4, fraction=0.5)
    cp("fish_drying_rack", 129, 55, 4)
    cp("fish_crates_traps", 120, 64, 3)
    cp("signal_tower", 137, 46, 7)
    cp("outrigger_canoe", 142, 62, 3, shore_ok=True, solid=False)
    cp("banana_plant", 121, 47, 4)
    cp("hibiscus_bush", 135, 57, 3)
    cp("bamboo_grove", 127, 47, 5)
    ep("palm_lean_a", 141, 54, 6)
    ep("palm_lean_b", 114, 48, 6)

    # ---------------- The Lost Fleet (north-east)
    ep("shipwreck_full", 141, 24, 9, solid="core", shore_ok=True)
    ep("shipwreck_fragment", 152, 17, 5, shore_ok=True)
    cp("rowboat_wreck", 148, 28, 3, shore_ok=True)
    cp("buried_treasure_chest", 152, 24, 2)
    cp("driftwood_pile", 136, 25, 3, shore_ok=True)
    cp("crab_claw_arch", 144, 29, 4, road_ok=True, solid=False)
    cp("driftwood_pile", 143, 14, 3, shore_ok=True)
    ep("palm_lean_b", 150, 28, 6)
    ep("palm_lean_a", 138, 18, 6)

    # ---------------- Hollow isle (south-east): goblin salvage + the troll lair
    cp("rowboat_wreck", 128, 108, 3, shore_ok=True)
    cp("fish_crates_traps", 132, 103, 3)
    cp("driftwood_pile", 126, 102, 3, shore_ok=True)
    cp("tiki_totem", 135, 117, 7)
    cp("tiki_totem", 147, 117, 7)
    cp("banana_plant", 130, 98, 4)
    cp("bamboo_grove", 146, 100, 5)
    cp("hibiscus_bush", 134, 96, 3)
    cp("mossy_jungle_boulder", 148, 110, 4)
    ep("palm_lean_b", 150, 104, 6)
    ep("palm_lean_a", 129, 116, 6)

    # ---------------- Grotto isle (west): the drowned naga door
    cp("sunken_totem", 15, 106, 5, shore_ok=True)
    cp("coral_reef_outcrop", 31, 106, 4, shore_ok=True)
    cp("murloc_hut", 42, 98, 5, shore_ok=True)
    cp("mangrove_thicket", 18, 86, 6, shore_ok=True)
    cp("hibiscus_bush", 36, 83, 3)
    cp("banana_plant", 40, 90, 4)
    cp("mossy_jungle_boulder", 35, 96, 4)
    ep("tide_pool", 28, 100, 3)
    ep("palm_lean_a", 22, 84, 6)
    ep("palm_lean_a", 40, 85, 6)

    # ---------------- Naga Ruins (north-west)
    dp("temple_archway", 25, 58, 7, road_ok=True, solid=False)
    dp("grotto_naga_column", 20, 51, 5, solid="core")
    dp("grotto_naga_column", 30, 51, 5, solid="core")
    dp("grotto_naga_priestess_statue", 21, 45, 5, solid="core")
    dp("grotto_naga_warrior_statue", 29, 45, 5, solid="core")
    dp("grotto_shell_altar", 25, 46, 3, solid="core")
    dp("grotto_naga_rune_stone", 17, 49, 4, solid="core")
    dp("grotto_serpent_skeleton", 33, 56, 4)
    ep("overgrown_ruin", 15, 42, 6, solid="core")
    ep("jungle_idol", 35, 47, 5, solid="core")
    cp("mangrove_thicket", 12, 54, 6, shore_ok=True)
    cp("banana_plant", 16, 55, 4)
    ep("palm_lean_b", 20, 38, 6)

    # ---------------- Razorjaw Reef (south-west)
    cp("coral_reef_outcrop", 36, 134, 4, shore_ok=True)
    cp("coral_reef_outcrop", 61, 148, 4, shore_ok=True)
    cp("coral_reef_outcrop", 41, 150, 4, shore_ok=True)
    cp("murloc_hut", 33, 141, 5, shore_ok=True)
    cp("sunken_totem", 64, 140, 5, shore_ok=True)
    cp("crab_claw_arch", 55, 140, 4, road_ok=True, solid=False)
    cp("mangrove_thicket", 48, 147, 6, shore_ok=True)
    dp("grotto_giant_clam", 44, 133, 3)
    dp("grotto_crab_nest", 40, 141, 4, solid="core")
    cp("driftwood_pile", 50, 134, 3)
    cp("rowboat_wreck", 58, 133, 3, shore_ok=True)
    ep("palm_lean_b", 38, 137, 6)

    # ---------------- Tidal Flats (south-east of Echo Landing)
    cp("coral_reef_outcrop", 98, 124, 4, shore_ok=True)
    cp("coral_reef_outcrop", 115, 131, 4, shore_ok=True)
    cp("mangrove_thicket", 104, 135, 6, shore_ok=True)
    cp("buried_treasure_chest", 113, 124, 2)
    cp("driftwood_pile", 100, 132, 3)
    ep("tide_pool", 108, 126, 3, shore_ok=True)

    # ---------------- sea stacks: the real rock spires
    for (cx, cy, rx, ry) in STACKS:
        cp("sea_stack_spire", int(cx), int(cy + 1), 7, solid=False, shore_ok=True, allow_overlap=True, road_ok=True, nudge=0)


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
