"""
Hand-built Valley of Trials (120x120) - level 1-6 orc starter valley.

Every object here is placed at an explicit coordinate (no random scatter).
The ground/water/cliff look is a baked painting (tools/terrain_painter.py,
run via tools/bake_vot_terrain.py); this module owns the TILE data
(walkability, props, portals, subzones, chests) and the `PLAN` (roads +
regions) that the baker paints from, so art and gameplay can't drift apart.

HARD CONTRACTS (other zones/data reference these exact coordinates):
  portals  (40,30)->The Den   (95,22)->Burning Blade Coven   (115,60)->Durotar
  NPCs     Marta (60,20), forge (63,20), Nakhtar (60,25), Valley Grunt (54,29),
           Kuraw (65,35), Grulnok (58,40), Fizzcrank (63,42), Rhaka (50,45),
           Torgak (70,38), Remains (72,50), Grosk (55,48)
  spawns   (61,20) (83,75) (97,89) kept off solid tiles
"""
import math
import os

from PIL import Image

from world.tilemap import Tilemap

DP = "assets/tiles/dungeon_props/"
ENT = "assets/tiles/cave_entrances/"
BAKED_DIR = "assets/tiles/valley_of_trials/baked"
W = H = 120

NPCS = [(60, 20), (63, 20), (60, 25), (54, 29), (65, 35), (58, 40), (63, 42),
        (50, 45), (70, 38), (72, 50), (55, 48)]
PORTALS = {(40, 30): "The Den", (95, 22): "Burning Blade Coven", (115, 60): "Durotar"}

# ---------------------------------------------------------------- the plan
# roads: (waypoints in tile coords, width in tiles)
ROADS = {
    "main": ([(60, 16), (60, 24), (61, 33), (59, 42), (60, 50), (63, 56), (71, 58),
              (84, 60), (98, 61), (108, 60), (115, 60)], 3.0),
    "den": ([(60, 29), (52, 30), (46, 31), (40, 31)], 2.0),
    "bbc": ([(62, 21), (72, 22), (82, 25), (90, 25), (95, 24)], 2.0),
    "train": ([(58, 19), (48, 19), (41, 22), (36, 26)], 2.0),
    "lake_west": ([(59, 50), (47, 54), (37, 62), (32, 72), (33, 82), (37, 92)], 2.0),
    "lake_east": ([(71, 58), (79, 68), (83, 80), (77, 91), (63, 97), (49, 95), (37, 92)], 2.0),
    "dunes": ([(96, 61), (92, 49), (91, 38), (88, 27)], 1.6),
}

LAKE = (55, 68, 16)          # cx, cy, r

_ASPECT = {}


def _aspect(path):
    if path not in _ASPECT:
        with Image.open(path) as im:
            _ASPECT[path] = im.size[0] / im.size[1]
    return _ASPECT[path]


def _road_points():
    from tools.terrain_painter import Painter
    out = {}
    for k, (pts, w) in ROADS.items():
        out[k] = (Painter.spline(pts), w)
    return out


class _Layout:
    def __init__(self):
        self.zone = Tilemap("Valley of Trials", W, H,
                            "A sheltered red-sand valley ringed by mountains, with a spring-fed lake at its heart.")
        self.z = self.zone
        self.roads = _road_points()
        self.skipped = []
        self.chests = []

    # ------------------------------------------------------------ helpers
    def road_clear(self, x, y, margin=0.9):
        for pts, w in self.roads.values():
            d = ((pts[:, 0] - x) ** 2 + (pts[:, 1] - y) ** 2) ** 0.5
            if d.min() < w * 0.5 + margin:
                return False
        return True

    def prop(self, name, cx, base_y, height, solid="core", fraction=0.4, road_ok=False,
             path_dir=DP, allow_overlap=False):
        """Place sprite `name` with bottom-centre on (cx, base_y). solid: False
        decor | True whole footprint | "core" base only. Rejected (and logged)
        if it would sit on a road, NPC, portal or an existing solid prop."""
        path = f"{path_dir}{name}.png" if not name.endswith(".png") else f"{path_dir}{name}"
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        z = self.z
        wt = max(1, round(height * _aspect(path)))
        ax, ay = cx - wt // 2, base_y - height + 1
        core = []
        rows = max(1, round(height * fraction))
        for y in range(ay, ay + height):
            for x in range(ax, ax + wt):
                if solid is True or (solid == "core" and y >= ay + height - rows
                                     and ax + int(wt * 0.2) <= x < max(ax + int(wt * 0.8), ax + int(wt * 0.2) + 1)):
                    core.append((x, y))
        bad = None
        for (x, y) in core:
            if not (0 <= x < W and 0 <= y < H):
                bad = "off-map"
            elif z.collision_layer[y][x] is not None and not allow_overlap:
                bad = "overlaps solid"
            elif z.base_layer[y][x] in ("deep_water",):
                bad = "deep water"
            elif any(abs(x - nx) <= 1 and abs(y - ny) <= 1 for nx, ny in NPCS):
                bad = "NPC"
            elif any(abs(x - px) <= 2 and abs(y - py) <= 2 for px, py in PORTALS):
                bad = "portal"
            elif not road_ok and not self.road_clear(x, y, 0.6):
                bad = "road"
            if bad:
                break
        if bad:
            self.skipped.append((name, cx, base_y, bad))
            return False
        z.add_landmark(path, ax, ay, wt, height, solid=False)
        for (x, y) in core:
            if z.interaction_layer[y][x] is None:
                z.collision_layer[y][x] = "landmark"
        return True

    def row(self, name, xs, base_y, height, **kw):
        n = 0
        for x in xs:
            n += bool(self.prop(name, x, base_y, height, **kw))
        return n

    def chest(self, x, y):
        z = self.z
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if z.collision_layer[y + dy][x + dx] in ("landmark",):
                    z.collision_layer[y + dy][x + dx] = None
        z.set_tile(x, y, "chest", "interaction")
        self.chests.append((x, y))


# ------------------------------------------------------------ terrain shape
def _ring_and_lake(L):
    z = L.z
    z.fill("sand", "base")
    border_depth = 14
    # carve-outs through the cliff ring: ("rect", x0, x1, y0, y1) / ("ell", cx, cy, rx, ry)
    gaps = [("rect", 98, 117, 54, 66),          # Durotar gateway corridor
            ("ell", 60, 11, 21.5, 8.5),         # north pocket: longhouse + weapon shelter
            ("ell", 40, 30, 5, 5), ("ell", 95, 22, 5, 5)]

    def in_gap(x, y):
        for g in gaps:
            if g[0] == "rect":
                if g[1] <= x <= g[2] and g[3] <= y <= g[4]:
                    return True
            elif ((x - g[1]) / g[3]) ** 2 + ((y - g[2]) / g[4]) ** 2 <= 1.0:
                return True
        return False

    for y in range(H):
        for x in range(W):
            ed = min(x, W - 1 - x, y, H - 1 - y)
            if ed >= border_depth + 6 or in_gap(x, y):
                continue
            pos = y if y < H / 2 else H - y
            posx = x if x < W / 2 else W - x
            along = pos if min(x, W - 1 - x) < min(y, H - 1 - y) else posx
            jitter = (3.2 * math.sin(along * 0.12 + 0.7) + 2.2 * math.sin(along * 0.31 + 1.9)
                      + 1.4 * math.sin(along * 0.053 + 4.0))
            if ed < border_depth + jitter:
                z.set_tile(x, y, "cliff", "collision")

    cx, cy, r = LAKE
    for dy in range(-r - 6, r + 7):
        for dx in range(-r - 6, r + 7):
            x, y = cx + dx, cy + dy
            if not (0 <= x < W and 0 <= y < H):
                continue
            kind = lake_kind(x + 0.5, y + 0.5)
            if kind == 2:
                z.set_tile(x, y, "deep_water", "base")
                z.collision_layer[y][x] = None
            elif kind == 1:
                z.set_tile(x, y, "shallow_water", "base")
                z.collision_layer[y][x] = None


def lake_radius(a):
    """Smooth lake outline: integer harmonics only (no seam at +-pi)."""
    return LAKE[2] * (1.0 + 0.13 * math.sin(2 * a + 1.0) + 0.09 * math.sin(3 * a + 2.1)
                      + 0.07 * math.sin(4 * a) + 0.04 * math.sin(7 * a + 0.6))


def lake_fields(gx, gy):
    """numpy (gx, gy in tile units) -> (shallow_extent, deep_extent) signed
    distances in tiles: >0 inside the shallow / deep body.  Shared with the baker."""
    import numpy as np
    dx, dy = gx - LAKE[0], gy - LAKE[1]
    a = np.arctan2(dy, dx)
    rr = LAKE[2] * (1.0 + 0.13 * np.sin(2 * a + 1.0) + 0.09 * np.sin(3 * a + 2.1)
                    + 0.07 * np.sin(4 * a) + 0.04 * np.sin(7 * a + 0.6))
    d = np.hypot(dx, dy)
    return rr * 0.86 - d, rr * 0.60 - d


def lake_kind(gx, gy):
    """0 land, 1 shallow, 2 deep at a tile centre."""
    s, d = lake_fields(gx, gy)
    return 2 if d > 0 else (1 if s > 0 else 0)


def _carve_landing(z, px, py, radius):
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            x, y = px + dx, py + dy
            if 0 <= x < W and 0 <= y < H:
                if z.base_layer[y][x] in ("deep_water", "shallow_water"):
                    z.set_tile(x, y, "sand", "base")
                z.collision_layer[y][x] = None


def _paint_roads(L):
    """Mark road tiles 'path' in the base layer (data matches the painting)."""
    z = L.z
    for pts, w in L.roads.values():
        for (px, py) in pts:
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    x, y = int(px) + dx, int(py) + dy
                    if (0 <= x < W and 0 <= y < H
                            and math.hypot(x + 0.5 - px, y + 0.5 - py) <= w * 0.5
                            and z.base_layer[y][x] == "sand"
                            and z.collision_layer[y][x] is None):
                        z.set_tile(x, y, "path", "base")


# ------------------------------------------------------------------ content
def _buildings(L):
    z = L.z
    S = 0.67
    for sprite, ax, ay, w, h in [
        ("assets/buildings/novice_longhouse.png", 49, 5, 15, 12),
        ("assets/buildings/weapon_rack_shelter.png", 58, 6, 12, 9),
        ("assets/buildings/trial_hut.png", 33, 17, 9, 9),
        ("assets/buildings/elders_tent.png", 65, 15, 9, 9),
        ("assets/buildings/generic_house_a.png", 47, 30, 9, 9),
        ("assets/buildings/generic_hut_a.png", 62, 25, 9, 9),
    ]:
        nw, nh = max(1, round(w * S)), max(1, round(h * S))
        z.add_landmark(sprite, ax + (w - nw) // 2, ay + (h - nh) // 2, nw, nh)


def _portals(L):
    z = L.z
    for (cx, cy, sprite) in [(40, 30, "cave_entrance_torches"), (95, 22, "cave_entrance_banners")]:
        _carve_landing(z, cx, cy, 2)
        z.set_tile(cx, cy, "portal", "interaction")
        z.add_landmark(f"{ENT}{sprite}.png", cx - 3, cy - 3, 6, 4, mouth_offset=(3, 3))
    _carve_landing(z, 115, 60, 3)
    z.set_tile(115, 60, "portal", "interaction")
    _carve_landing(z, 60, 20, 1)
    z.set_tile(60, 20, "npc", "interaction")
    for (sx, sy) in [(61, 20), (83, 75), (97, 89)]:
        z.collision_layer[sy][sx] = None


def _dress_camp(L):
    """Valley Camp: plaza, banners, fires, training yard, recruit yard."""
    p = L.prop
    # plaza
    p("vot_fire_pit", 56, 24, 3)
    p("vot_war_banner", 50, 24, 5)
    p("vot_war_banner", 67, 25, 5)
    p("vot_hide_rack", 70, 29, 3)
    # recruit yard south of the plaza
    p("vot_crate_stack", 68, 44, 3)
    p("vot_broken_cart", 67, 47, 3)
    p("vot_training_dummy", 59, 36, 3)
    p("vot_archery_target", 56, 43, 3)
    # palisade: two gently angled runs flanking the camp, gaps at every road
    L.row("vot_palisade", [46, 49], 17, 3)
    L.row("vot_palisade", [75, 78], 18, 3)


def _dress_training_yard(L):
    """Sagebrush Flat: the recruits' training ground around the trial hut."""
    p = L.prop
    L.row("vot_training_dummy", [24, 28], 24, 3)
    L.row("vot_archery_target", [23, 27], 34, 3)
    p("vot_war_banner", 20, 28, 5)
    p("vot_sagewood_sapling", 26, 19, 4)
    # Den approach
    p("den_torch", 36, 33, 3, road_ok=True)
    p("den_torch", 44, 33, 3, road_ok=True)


def _dress_grove(L):
    """Sagewood Grove: the one genuinely green, shaded patch."""
    p = L.prop
    for (x, y, h) in [(76, 31, 7), (80, 37, 7), (86, 40, 7)]:
        p("vot_sagewood_tree", x, y, h)
    for (x, y) in [(85, 33), (77, 38)]:
        p("vot_sagewood_sapling", x, y, 4)
    p("vot_spring_boulder", 82, 34, 4)
    p("vot_fallen_log", 77, 34, 2)


def _dress_nest(L):
    """Scorpid Nest + the Burning Blade approach."""
    p = L.prop
    for (x, y) in [(84, 15), (91, 11), (98, 14), (86, 31), (103, 18), (105, 29)]:
        p("vot_scorpid_burrow", x, y, 3)
    p("vot_beast_ribcage", 87, 21, 3)
    p("vot_dead_tree", 82, 20, 6)
    p("den_chitin_husk", 93, 29, 3)
    # Burning Blade taint at the cave mouth
    p("bbc_banner", 89, 25, 5, road_ok=True)
    p("bbc_banner", 101, 25, 5, road_ok=True)
    p("bbc_fel_brazier", 91, 27, 3, road_ok=True)
    p("bbc_fel_brazier", 99, 27, 3, road_ok=True)
    p("vot_fel_crystals", 103, 26, 3)


def _dress_dunes(L):
    """Windrift Dunes + Durotar gateway."""
    p = L.prop
    for (x, y) in [(90, 44), (101, 55), (95, 68)]:
        p("vot_barrel_cactus", x, y, 3)
    p("vot_dead_tree", 100, 47, 6)
    p("vot_mesa_pillar", 103, 36, 7)
    p("vot_thornbush", 98, 50, 2, solid=False)
    p("vot_trail_cairn", 93, 63, 3)
    # gateway: just the arch framing the Durotar portal tile + one banner pair
    p("vot_rock_arch", 114, 63, 8, solid=False, road_ok=True)
    p("vot_war_banner", 103, 56, 5)
    p("vot_war_banner", 103, 64, 5)


def _dress_lake(L):
    """Trailwater Spring."""
    p = L.prop
    # reed beds hugging the shore (decor, walkable)
    for (x, y) in [(41, 62), (51, 51), (69, 57), (72, 66), (62, 85), (41, 77), (46, 84)]:
        p("vot_reeds", x, y, 3, solid=False)
    p("vot_sagewood_tree", 40, 74, 7)
    p("vot_fallen_log", 66, 82, 2)


def _dress_cinder(L):
    """Cinderjaw Wastes."""
    p = L.prop
    for (x, y) in [(24, 88), (31, 96), (44, 90)]:
        p("vot_dead_tree", x, y, 6)
    for (x, y) in [(35, 87), (47, 94)]:
        p("vot_thornbush", x, y, 2, solid=False)
    for (x, y) in [(30, 100), (49, 88)]:
        p("bbc_red_stalagmites", x, y, 4)
    p("bbc_obsidian_spikes", 34, 99, 4)


def _dress_south(L):
    """The open southern valley floor: pillars, a wrecked caravan, cairns."""
    p = L.prop
    p("vot_mesa_pillar", 68, 102, 8)
    p("vot_mesa_pillar", 92, 95, 7)
    p("vot_broken_cart", 79, 94, 3)
    p("vot_crate_stack", 83, 95, 3)
    p("vot_fire_pit", 81, 97, 3)
    p("vot_trail_cairn", 55, 92, 3)
    p("vot_barrel_cactus", 70, 86, 3)
    p("vot_dead_tree", 85, 88, 6)


def _mountain_dressing(L):
    """Rock formations tucked against the inner ring so the wall has depth."""
    p = L.prop
    spots = [(26, 17, 6), (74, 15, 6), (104, 78, 7), (88, 104, 6), (17, 48, 6)]
    for (x, y, h) in spots:
        p("vot_mesa_pillar", x, y, h)


def _chests(L):
    for (x, y) in [(86, 97), (28, 96), (101, 53), (83, 42), (47, 36)]:
        # find nearest free walkable tile
        for r in range(0, 5):
            done = False
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    xx, yy = x + dx, y + dy
                    if (L.z.is_walkable(xx, yy) and L.z.interaction_layer[yy][xx] is None
                            and L.z.base_layer[yy][xx] not in ("deep_water", "shallow_water")
                            and L.road_clear(xx, yy, 0.2)):
                        L.chest(xx, yy)
                        done = True
                        break
                if done:
                    break
            if done:
                break


def _subzones(L):
    z = L.z
    z.add_subzone("Scorpid Nest", 78, 8, 34, 30)
    z.add_subzone("Trailwater Spring", LAKE[0] - 12, LAKE[1] - 12, 24, 24)
    z.add_subzone("Sagewood Grove", 63, 23, 24, 22)
    z.add_subzone("Sagebrush Flat", 18, 18, 22, 22, display_name="Sagebrush Flat")
    z.add_subzone("Cinderjaw Wastes", 18, 82, 40, 22)
    z.add_subzone("Windrift Dunes", 84, 30, 22, 40, display_name="Windrift Dunes")


def build_layout():
    L = _Layout()
    _ring_and_lake(L)
    _portals(L)
    _paint_roads(L)
    _buildings(L)
    _dress_camp(L)
    _dress_training_yard(L)
    _dress_grove(L)
    _dress_nest(L)
    _dress_dunes(L)
    _dress_lake(L)
    _dress_cinder(L)
    _dress_south(L)
    _mountain_dressing(L)
    _chests(L)
    _subzones(L)
    return L


def register_baked(zone, baked_dir=BAKED_DIR, chunk=20):
    """Register the baked painting as ground + water + obstacle chunks."""
    for cy in range(0, H, chunk):
        for cx in range(0, W, chunk):
            fn = f"{baked_dir}/ground_{cx}_{cy}.jpg"
            if not os.path.exists(fn):
                raise FileNotFoundError(f"{fn} - run python3 tools/bake_vot_terrain.py")
            w, h = min(chunk, W - cx), min(chunk, H - cy)
            zone.add_ground_chunk(fn, cx, cy, w, h)
            zone.ground_chunks[-1]["exact"] = True   # seamless painting: skip feather pass
            zone.add_water_chunk(fn, cx, cy, w, h)
            zone.add_obstacle_chunk(fn, cx, cy, w, h)


def generate_valley_of_trials():
    L = build_layout()
    register_baked(L.zone)
    return L.zone
