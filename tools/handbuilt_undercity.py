"""
Hand-built Undercity (200x200): the Forsaken capital, a round cavern city under the ruins of Lordaeron.

ARCHETYPE: THE WHEEL.  A great round cavern ringed by a skull-wall rim.  In the middle sits the TRADE QUARTER, an open
plaza around the Seal (bank, auction hall, inn, market stalls).  A green SEWER CANAL runs round the plaza in a ring and four
stone BRIDGES cross it, one on each compass point; each bridge opens onto an AVENUE that runs out to the rim:

    N avenue  - the Long Descent: the Ruins elevator at its head (the way in from Eastern Tirisfal)
    S avenue  - ends in the Deeps Gate, the portcullis down into the Plague Depths
    E / W     - run out to sealed old sluice / sally gates (decoration; the dead have no more roads to build)

The four avenues divide the ring beyond the canal into four crescent QUARTERS, each walled, each with two gates and one
great round hall at its heart:

    NW  Royal Quarter      - the Dark Lady's throne hall, the Forsaken command, the quartermaster
    NE  Magic Quarter      - the Violet Spire (mages, warlocks, priests), the archive, the enchanter
    SW  War Quarter        - the Warriors' Arena, the forge, the barracks, the rogues' alley
    SE  Apothecarium       - the Royal Apothecary Society's lab, plague vats, the alchemists

Same recipe as Orgrimmar / Brill (see claude/zone_perfection_playbook.md): this module owns the TILE data and the analytic
fields the baker (tools/bake_undercity.py) paints from, so collision and painting cannot drift apart.  Every object is
placed at an explicit coordinate (no random scatter); `pol(r, deg)` gives city coordinates from the centre.

HARD CONTRACTS (world/portal_manager.py)
  portal   (100,11)  elevator    -> Eastern Tirisfal (10,108)   (arrival is 2 tiles NORTH of the registered tile, so the
                                    link into Undercity is registered at (100,17) and you land at (100,15))
  portal   (100,185) Deeps Gate  -> Plague Depths    (arrival 2 north: (100,183))
  NPC ids  are referenced by data/quests/*.json - positions are written back to data/npcs/*.json by
           tools/sync_undercity_npcs.py
"""
import math
import os

import numpy as np
from PIL import Image

from world.tilemap import Tilemap

DP = "assets/tiles/dungeon_props/"
UP = "assets/tiles/undercity/props/"
EKP = "assets/tiles/eastern_kingdoms/props/"
BLD = "assets/buildings/"
ENT = "assets/tiles/cave_entrances/"
BAKED_DIR = "assets/tiles/undercity/baked"
W, H = 200, 200
CX, CY = 100.0, 100.0

ELEVATOR = (100, 11)         # the way up (portal tile)
ELEV_ARRIVE = (100, 15)      # you land here coming in (registered (100,17) in portal_manager)
DEEPS = (100, 185)           # the Deeps Gate (portal tile into the Plague Depths)

CANAL_R, CANAL_HALF = 53.25, 3.25       # the sewer ring: r in [50, 56.5]
QUARTER_IN = 60.0                        # inner wall of each quarter
AVENUE_HALF = 6.0                        # avenues are 12 wide, wall to wall 94..106
RIM_R = 94.0
WALL_HALF = 1.0
BUILDING_SCALE = 1.25


def pol(r, deg):
    """City coordinates r tiles from the centre at compass-ish `deg` (0=east, 90=south, 180=west, 270=north)."""
    a = math.radians(deg)
    return (CX + r * math.cos(a), CY + r * math.sin(a))


def ipol(r, deg):
    x, y = pol(r, deg)
    return (int(round(x)), int(round(y)))


# ----------------------------------------------------------------- quarters, halls, gates
QUARTERS = {                              # name: (x0, y0, x1, y1)  - clipped to r > QUARTER_IN; the rect runs out past the
    "royal": (-40, -40, 94, 94),          # rim on its outer sides (the cavern wall closes it), so only the avenue-facing
    "magic": (106, -40, 240, 94),         # edges and the inner arc carry a wall
    "war":   (-40, 106, 94, 240),
    "apoth": (106, 106, 240, 240),
}
QUARTER_NAMES = {"royal": "The Royal Quarter", "magic": "The Magic Quarter", "war": "The War Quarter",
                 "apoth": "The Apothecarium"}
HALL_R, HALL_DEG = 77.0, {"royal": 225, "magic": 315, "war": 135, "apoth": 45}
HALLS = {                                 # name: (cx, cy, radius)
    "royal": (*pol(HALL_R, 225), 12.5),
    "magic": (*pol(HALL_R, 315), 12.0),
    "war":   (*pol(HALL_R, 135), 13.5),
    "apoth": (*pol(HALL_R, 45), 12.5),
}
# each quarter has a gate onto each of the two avenues that flank it: (cx, cy, radius)
QUARTER_GATES = {
    "royal": [(94, 30, 5.0), (30, 94, 5.0)],
    "magic": [(106, 30, 5.0), (170, 94, 5.0)],
    "war":   [(94, 170, 5.0), (30, 106, 5.0)],
    "apoth": [(106, 170, 5.0), (170, 106, 5.0)],
}


def _hall_gates():
    """Each hall opens toward both avenue gates of its quarter."""
    out = []
    for n, (hx, hy, hr) in HALLS.items():
        for (gx_, gy_, _r) in QUARTER_GATES[n]:
            d = math.hypot(gx_ - hx, gy_ - hy)
            out.append((hx + (gx_ - hx) / d * hr, hy + (gy_ - hy) / d * hr, 4.2))
    return out


HALL_GATES = _hall_gates()
ALL_GATES = [g for gs in QUARTER_GATES.values() for g in gs] + HALL_GATES

# painted routes (waypoints, width in tiles).  The avenues run clean through the plaza.
ROADS = {
    "ns":        ([(100, 13), (100, 60), (100, 100), (100, 140), (100, 186)], 11.0),
    "ew":        ([(12, 100), (60, 100), (100, 100), (140, 100), (188, 100)], 11.0),
    "ring":      ([pol(24, d) for d in range(0, 361, 20)], 5.0),
    "promenade": ([pol(58.4, d) for d in range(0, 361, 15)], 3.0),
}


def _lanes():
    """Short lanes: avenue gate -> hall gate inside each quarter."""
    for n, (hx, hy, hr) in HALLS.items():
        for k, (gx_, gy_, _r) in enumerate(QUARTER_GATES[n]):
            d = math.hypot(gx_ - hx, gy_ - hy)
            tx, ty = hx + (gx_ - hx) / d * hr, hy + (gy_ - hy) / d * hr
            ROADS[f"lane_{n}_{k}"] = ([(gx_, gy_), ((gx_ + tx) / 2, (gy_ + ty) / 2), (tx, ty)], 4.0)


_lanes()


def _wob(gx, gy):
    return (0.45 * np.sin(0.37 * gx + 1.3) * np.sin(0.29 * gy + 0.7)
            + 0.30 * np.sin(0.83 * gx + 0.21 * gy + 2.0)
            + 0.25 * np.sin(0.19 * gx - 0.57 * gy + 4.1))


def rrect(gx, gy, x0, y0, x1, y1, r):
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    hx, hy = (x1 - x0) / 2.0 - r, (y1 - y0) / 2.0 - r
    qx = np.abs(gx - cx) - hx
    qy = np.abs(gy - cy) - hy
    out = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r
    return -out


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


def radius(gx, gy):
    return np.hypot(np.asarray(gx, float) - CX, np.asarray(gy, float) - CY)


def rim_radius(gx, gy):
    """The cavern wall's radius at each point (wobbly; deeper niche at the elevator head)."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    th = np.arctan2(gy - CY, gx - CX)
    base = (RIM_R + 1.5 * np.sin(5 * th + 0.7) + 1.1 * np.sin(9 * th + 2.0) + 0.8 * np.sin(13 * th + 1.1)
            + 0.9 * _wob(gx * 1.3, gy * 1.3))
    niche = 5.5 * np.exp(-((gx - CX) / 9.0) ** 4) * (gy < 40)          # the elevator shaft
    south = 3.0 * np.exp(-((gx - CX) / 10.0) ** 4) * (gy > 160)        # the Deeps Gate mouth
    return base + niche + south


def cliff_field(gx, gy):
    """>0 inside the rock beyond the cavern wall (tiles)."""
    return radius(gx, gy) - rim_radius(gx, gy)


def canal_field(gx, gy):
    """>0 on the sewer ring (bridges cut it back out)."""
    return CANAL_HALF - np.abs(radius(gx, gy) - CANAL_R)


def bridge_field(gx, gy):
    """>0 on the four stone bridges over the canal."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    r = radius(gx, gy)
    along = 6.2 - np.abs(r - CANAL_R)
    ns = np.minimum(5.5 - np.abs(gx - CX), along)
    ew = np.minimum(5.5 - np.abs(gy - CY), along)
    return np.maximum(ns, ew)


def quarter_sd(gx, gy, name):
    x0, y0, x1, y1 = QUARTERS[name]
    return np.minimum(rrect(gx, gy, x0, y0, x1, y1, 6.0), radius(gx, gy) - QUARTER_IN)


def hall_sd(gx, gy, name):
    hx, hy, hr = HALLS[name]
    return hr - np.hypot(np.asarray(gx, float) - hx, np.asarray(gy, float) - hy)


def gate_extent(gx, gy, gates=None):
    best = np.full(np.shape(gx), -99.0)
    for (cx, cy, rad) in (gates or ALL_GATES):
        best = np.maximum(best, rad - np.hypot(gx - cx, gy - cy))
    return best


def wall_extent(gx, gy):
    """>0 inside a quarter wall or hall wall band (gates cut out)."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    best = np.full(np.shape(gx), -99.0)
    for n in QUARTERS:
        best = np.maximum(best, WALL_HALF - np.abs(quarter_sd(gx, gy, n)))
        best = np.maximum(best, WALL_HALF - np.abs(hall_sd(gx, gy, n)))
    return np.minimum(best, -gate_extent(gx, gy))


def fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    return dict(cliff=cliff_field(gx, gy), wall=wall_extent(gx, gy), canal=canal_field(gx, gy),
                bridge=bridge_field(gx, gy))


def tile_kind(gx, gy):
    """0 floor, 3 cliff, 5 wall, 2 canal water (deep), 4 bridge deck - the single source of truth for the tile grid."""
    F = fields(gx, gy)
    kind = np.zeros(np.shape(gx), int)
    kind[F["canal"] > 0] = 2
    kind[F["bridge"] > 0] = 4
    kind[(F["wall"] > 0) & (kind != 4)] = 5
    kind[F["cliff"] > 0] = 3
    return kind


_ASPECT = {}


def _aspect(path):
    if path not in _ASPECT:
        with Image.open(path) as im:
            _ASPECT[path] = im.size[0] / im.size[1]
    return _ASPECT[path]


def quarter_of(x, y):
    for n in QUARTERS:
        if quarter_sd(np.array([x + 0.5]), np.array([y + 0.5]), n)[0] > 2:
            return n
    return None


# ================================================================== layout
class Layout:
    def __init__(self):
        self.zone = Tilemap("Undercity", W, H,
                            "The Forsaken capital, a round cavern city under the ruins of Lordaeron. Skull walls, "
                            "a green sewer ring, and the Dark Lady's court.")
        self.z = self.zone
        self.z.region = "Eastern Kingdoms - Lordaeron"
        self.z.is_town = True
        self.skipped = []
        self.placed = 0
        self.npc_xy = []

    def road_clear(self, x, y, margin=0.9):
        return road_dist(np.array([x + 0.5]), np.array([y + 0.5]))[0] < -margin

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
            if z.base_layer[y][x] in ("deep_water", "shallow_water") and not allow_overlap:
                return "water", core, ax, ay
            if any(abs(x - nx) <= 1 and abs(y - ny) <= 1 for nx, ny in self.npc_xy):
                return "NPC", core, ax, ay
            if not portal_ok and any(abs(x - px) <= 2 and abs(y - py) <= 2 for px, py in (ELEVATOR, DEEPS)):
                return "portal", core, ax, ay
            if not road_ok and not self.road_clear(x, y, 0.6):
                return "road", core, ax, ay
        return None, core, ax, ay

    def prop(self, name, cx, base_y, height, solid="core", fraction=0.4, road_ok=False,
             path_dir=UP, allow_overlap=False, nudge=2, portal_ok=False):
        cx, base_y = int(round(cx)), int(round(base_y))
        path = f"{path_dir}{name}.png" if not name.endswith(".png") else f"{path_dir}{name}"
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
        self.skipped.append((name, cx, base_y, first_bad))
        return False

    def bld(self, name, cx, base_y, height, **kw):
        height = int(round(height * BUILDING_SCALE))
        kw.setdefault("path_dir", BLD)
        kw.setdefault("fraction", 0.5)
        return self.prop(name, cx, base_y, height, **kw)

    def pp(self, name, r, deg, height, **kw):
        """Place a prop at polar coordinates."""
        x, y = pol(r, deg)
        return self.prop(name, x, y, height, **kw)

    def bb(self, name, r, deg, height, **kw):
        x, y = pol(r, deg)
        return self.bld(name, x, y, height, **kw)



# ----------------------------------------------------------------- NPC spots
def _P(r, deg):
    return ipol(r, deg)


NPC_POSITIONS = {
    "et_scarlet_watch_scout": (105, 32),      # quest hub: Scout Hollowmere, the Scarlet Watch Post
    "et_cult_warden": (108, 28),              # quest hub: Warden Ysolde Grave, the Cult's farm
    "et_hunter_ravel": (93, 26),              # quest hub: Huntress Ravel, the Venomweb Vale
    "et_gunther_lorn": (105, 26),             # quest hub: Gunther Lorn, Brightwater Lake
    # ---- the Long Descent / elevator
    "uc_guard_1": (97, 18),
    "uc_guard_2": (103, 46),
    # ---- the Trade Quarter (plaza)
    "uc_innkeeper": (124, 135),
    "uc_banker": _P(36, 225),
    "uc_auctioneer": _P(36, 315),
    "uc_undertaker": _P(36, 135),
    "uc_riding_trainer": (115, 111),
    "uc_trader": _P(33, 22.5),
    "uc_market_embalmer": _P(33, 67.5),
    "uc_market_food": _P(33, 112.5),
    "uc_market_herbs": _P(33, 157.5),
    "uc_market_scribe": _P(33, 202.5),
    "uc_market_gems": _P(33, 247.5),
    "uc_market_tailor": _P(33, 292.5),
    "uc_market_relics": _P(33, 337.5),
    "uc_market_butcher": (113, 76),
    # ---- the Royal Quarter (NW)
    "uc_sylvanas": (43, 43),
    "uc_royal_guard_1": (53, 52),
    "uc_royal_guard_2": (40, 52),
    "uc_executor": (72, 32),
    "uc_deathstalker": (82, 22),
    "uc_quartermaster": (26, 77),
    "uc_provisioner": (28, 88),
    # ---- the Magic Quarter (NE)
    "uc_mage_trainer": (150, 42),
    "uc_warlock_trainer": (159, 42),
    "uc_priest_trainer": (154, 52),
    "uc_summoning_master": (162, 50),
    "uc_enchanter": (172, 77),
    "uc_scholar": (127, 33),
    "uc_demonic_vendor": (168, 60),
    "uc_arcane_vendor": (176, 87),
    # ---- the War Quarter (SW)
    "uc_warrior_trainer": (42, 152),
    "uc_hunter_trainer": (60, 168),
    "uc_beastmaster": (68, 179),
    "uc_rogue_trainer": (20, 121),
    "uc_poison_vendor": (23, 135),  # in front of the grand forge, not inside it
    "uc_blacksmith": (24, 136),
    "uc_weaponsmith": (44, 128),
    "uc_drillmaster": (50, 146),
    # ---- the Apothecarium (SE)
    "uc_apothecary": (150, 152),
    "uc_master_apothecary": (178, 133),
    "uc_alchemist": (159, 158),
    "uc_elixir_trader": (172, 150),
    "uc_reagent_vendor": (130, 172),
    "uc_surgeon": (164, 156),
    "uc_lab_assistant": (156, 162),
    "uc_wanderer": _P(58.2, 155),
    # ---- the Deeps Gate (S avenue end)
    "uc_gatewarden": (97, 178),
    "uc_deeps_guard": (103, 178),
}
RECRUITS = {"marco_paladin": (104, 96), "sophia_mage": (146, 47), "ryan_warlock": (162, 44)}
FORGE = (28, 138)


def _terrain(L):
    z = L.z
    z.fill("stone", "base")
    ys, xs = np.mgrid[0:H, 0:W]
    kind = tile_kind(xs + 0.5, ys + 0.5)
    rd = road_dist(xs + 0.5, ys + 0.5)
    L.kind = kind
    for y in range(H):
        for x in range(W):
            k = kind[y, x]
            if k == 3:
                z.set_tile(x, y, "cliff", "collision")
            elif k == 5:
                z.set_tile(x, y, "wall", "collision")
            elif k == 2:
                z.set_tile(x, y, "deep_water", "base")
            elif k == 4 or rd[y, x] > 0:
                z.set_tile(x, y, "path", "base")


def _portals(L):
    z = L.z
    for (px, py) in (ELEVATOR, DEEPS):
        z.collision_layer[py][px] = None
        z.set_tile(px, py, "portal", "interaction")
    ax, ay = ELEV_ARRIVE
    z.collision_layer[ay][ax] = None


def build_terrain():
    L = Layout()
    _terrain(L)
    _portals(L)
    return L


def hc(q, r, deg):
    """Coordinates r tiles from a quarter hall's centre."""
    hx, hy, _ = HALLS[q]
    a = math.radians(deg)
    return (hx + r * math.cos(a), hy + r * math.sin(a))


def _dress(L):
    p, b = L.prop, L.bld
    L.npc_xy = list(NPC_POSITIONS.values()) + list(RECRUITS.values()) + [FORGE]
    ek = lambda n, x, y, h, **kw: p(n, x, y, h, path_dir=EKP, **kw)
    dp = lambda n, x, y, h, **kw: p(n, x, y, h, path_dir=DP, **kw)

    # ================================================================ THE LONG DESCENT (north avenue)
    p("uc_elevator", 100, 12, 8, solid=False, portal_ok=True, allow_overlap=True, road_ok=True, nudge=0)
    for x in (97, 103):
        p("uc_royal_banner", x, 22, 8, road_ok=True, nudge=0)
    for x in (97, 102):
        p("uc_skull_pillar", x, 27, 8, road_ok=True, nudge=0)
    for y in (31, 42):
        for x in (96, 103):
            p("uc_lantern_post", x, y, 6, road_ok=True, nudge=1)
    p("uc_skull_arch", 100, 36, 11, solid=False, road_ok=True, allow_overlap=True, nudge=0)

    # ================================================================ THE TRADE QUARTER (plaza)
    p("uc_obelisk", 100, 98, 9, road_ok=True, allow_overlap=True, nudge=0)          # the Seal
    for k, d in enumerate((45, 135, 225, 315)):
        x, y = pol(11.5, d)
        p("uc_skull_pillar", x, y, 7, road_ok=True, nudge=1)
    for d in (0, 90, 180, 270):
        x, y = pol(12.5, d + 22.5)
        p("uc_bench", x, y, 3, road_ok=True, nudge=1)
    # eight market stalls round the ring road, a lantern post between each pair
    for k in range(8):
        d = 22.5 + 45 * k
        x, y = pol(37.5, d)
        p("uc_stall_bottles" if k % 2 == 0 else "uc_stall_goods", x, y, 5, nudge=2)
        if (d + 22.5) % 90 != 0:                      # the avenues run through the cardinal gaps
            x, y = pol(37, d + 22.5)
            p("uc_lantern_post", x, y, 6, nudge=2)
    # the Inn
    b("forsaken_house_medium", 131, 132, 9)
    p("uc_bench", 124, 140, 3)
    p("uc_lantern_post", 118, 134, 6)
    # the Bank of Undercity
    p("uc_vault_door", 74, 71, 6, solid=True)
    p("uc_crate_stack", 67, 72, 3)
    p("uc_crate_stack", 81, 71, 3)
    p("uc_lantern_post", 68, 80, 6)
    # the Auction House
    b("forsaken_town_hall", 128, 70, 11)
    p("uc_lantern_post", 118, 80, 6)
    p("uc_crate_stack", 135, 72, 3)
    # the Mortuary
    b("crypt_chapel", 72, 123, 11)
    p("uc_coffin_stack", 82, 123, 4)
    dp("sarcophagus", 64, 126, 4)
    ek("ek_open_grave", 66, 134, 3)
    p("uc_lantern_post", 80, 133, 6)
    # the stable / riding trainer's yard
    p("uc_bone_heap", 111, 106, 3)
    p("uc_bench", 118, 108, 3)
    p("uc_crate_stack", 120, 114, 3)
    p("uc_lantern_post", 111, 118, 6)
    # sewer outfalls feeding the canal, grates in the pavement
    for d in (45, 135, 225, 315):
        x, y = pol(47.5, d)
        p("uc_sewer_outlet", x, y, 6, solid="core", nudge=3)
    for d in (22.5, 112.5, 202.5, 292.5):
        x, y = pol(17, d)
        p("uc_floor_grate", x, y, 2, solid=False, road_ok=True, nudge=2)
    # bridge heads: lantern posts and a skull pillar on each bank
    for (dx, dy) in ((0, -1), (0, 1), (-1, 0), (1, 0)):
        for sd in (-1, 1):
            x = CX + dx * 49 + (sd * 7 if dx == 0 else 0)
            y = CY + dy * 49 + (sd * 7 if dy == 0 else 0)
            p("uc_lantern_post", x, y, 6, road_ok=True, nudge=1)
            x2 = CX + dx * 63 + (sd * 7 if dx == 0 else 0)
            y2 = CY + dy * 63 + (sd * 7 if dy == 0 else 0)
            p("uc_lantern_post", x2, y2, 6, road_ok=True, nudge=1)

    # ================================================================ THE ROYAL QUARTER (NW)  - the Dark Lady's court
    p("uc_throne", 39, 40, 9, solid="core")
    for d in (180, 270):
        x, y = hc("royal", 10.5, d)
        p("uc_royal_banner", x, y, 8, nudge=1)
    for d in (155, 205, 245, 295):
        x, y = hc("royal", 11.0, d)
        p("uc_skull_pillar", x, y, 7, nudge=1)
    for d in (30, 120, 330, 60):
        x, y = hc("royal", 8.5, d)
        dp("spirit_brazier", x, y, 5, nudge=2)
    for d in (320, 130):
        x, y = hc("royal", 8.0, d)
        ek("ek_angel_statue", x, y, 7, nudge=2)
    # High Command (Executor Wrenfall)
    b("forsaken_town_hall", 74, 27, 13)
    ek("ek_forsaken_banner", 64, 34, 8)
    ek("ek_forsaken_banner", 88, 36, 8)
    p("uc_weapon_rack", 66, 22, 4)
    p("uc_weapon_rack", 82, 22, 4)
    p("uc_lantern_post", 74, 40, 6, road_ok=True)
    # Quartermaster and provisioner
    b("forsaken_house_small", 20, 74, 8)
    p("uc_weapon_rack", 30, 74, 4)
    p("uc_crate_stack", 14, 82, 3)
    p("uc_stall_goods", 27, 92, 5)
    p("uc_lantern_post", 20, 86, 6)
    # barracks of the Royal Guard
    b("forsaken_house_medium", 64, 47, 10)
    p("uc_weapon_rack", 62, 52, 4)
    p("uc_lantern_post", 44, 66, 6)

    # ================================================================ THE MAGIC QUARTER (NE) - the Violet Spire
    x, y = hc("magic", 0, 0)
    p("uc_obelisk", x, y - 2, 11, solid="core", nudge=1)
    dp("ritual_circle", x, y + 8, 8, solid=False, allow_overlap=True, nudge=1)
    for d in (0, 72, 144, 216, 288):
        x, y = hc("magic", 9.5, d + 36)
        dp("spirit_brazier", x, y, 6, nudge=2)
    for d in (240, 300):
        x, y = hc("magic", 7.0, d)
        p("uc_lectern", x, y, 4, nudge=1)
    # the Archive
    b("forsaken_house_medium", 128, 30, 9)
    dp("bbc_bookshelf", 120, 24, 5)
    dp("wizard_desk", 136, 36, 4)
    p("uc_lantern_post", 122, 40, 6)
    # Warlock summoning grounds
    dp("rf_summoning_circle", 166, 66, 7, solid=False, allow_overlap=True, nudge=2)
    dp("rf_sacrificial_altar", 160, 60, 6)
    dp("bbc_fel_brazier", 172, 56, 5)
    # Enchanter, reagent and demon vendors
    b("forsaken_house_small", 174, 72, 8)
    p("uc_stall_bottles", 178, 90, 5)
    p("uc_stall_goods", 168, 63, 5, nudge=1)
    dp("broken_column", 142, 46, 5)
    dp("bbc_candelabra", 182, 64, 4)
    dp("bbc_candelabra", 136, 62, 4)
    p("uc_lantern_post", 180, 80, 6)

    # ================================================================ THE WAR QUARTER (SW) - the Warriors' Arena
    for (dx, dy) in ((-5, -3), (5, -3), (-5, 5), (5, 5)):
        x, y = hc("war", 0, 0)
        p("uc_dummy", x + dx, y + dy, 4, nudge=2)
    p("uc_weapon_rack", 38, 160, 4)
    p("uc_weapon_rack", 54, 160, 4)
    p("uc_tool_rack", 38, 152, 4)
    p("uc_cage_cell", 55, 161, 5)
    ek("ek_gibbet", 33, 142, 8)
    ek("ek_pillory", 52, 152, 5)
    for d in (45, 135, 225, 315):
        x, y = hc("war", 11.5, d)
        p("uc_skull_pillar", x, y, 7, nudge=1)
    # the forge
    b("grand_forge", 22, 133, 7)
    dp("rf_steam_vent", 30, 143, 4)
    p("uc_tool_rack", 17, 142, 4)
    p("uc_crate_stack", 38, 140, 3)
    # weaponsmith
    p("uc_weapon_rack", 46, 124, 4)
    b("forsaken_house_medium", 58, 120, 10)               # the barracks
    # rogues' alley
    b("forsaken_house_small", 28, 114, 8)
    p("uc_stall_bottles", 30, 130, 5)
    p("uc_crate_stack", 17, 128, 3)
    # hunters' lodge
    b("forsaken_house_small", 74, 160, 8)
    b("forsaken_house_small", 72, 186, 8)
    ek("ek_scarecrow", 66, 176, 5)
    p("uc_lantern_post", 62, 156, 6)
    p("uc_lantern_post", 30, 156, 6)

    # ================================================================ THE APOTHECARIUM (SE) - the Royal Apothecary Society
    for (dx, dy) in ((-5, -4), (5, -4), (0, 6)):
        x, y = hc("apoth", 0, 0)
        p("uc_plague_vat", x + dx, y + dy, 6, nudge=2)
    p("uc_alchemy_table", 160, 158, 4)
    p("uc_alchemy_table", 148, 148, 4)
    p("uc_copper_still", 168, 150, 5)
    p("uc_jar_shelf", 143, 160, 4)
    p("uc_operating_table", 163, 164, 4)
    p("uc_pipe_cluster", 168, 142, 6)
    p("uc_pipe_cluster", 142, 144, 6)
    ek("ek_plague_cauldron", 150, 165, 5)
    dp("bbc_candelabra", 160, 142, 4)
    dp("bbc_candelabra", 146, 168, 4)
    # Society HQ
    b("crypt_chapel", 180, 128, 11)
    p("uc_crate_stack", 170, 128, 3)
    p("uc_plague_vat", 188, 138, 6)
    p("uc_stall_bottles", 172, 156, 5)
    p("uc_stall_goods", 131, 176, 5)
    ek("ek_plague_cart", 128, 168, 5)
    p("uc_lantern_post", 136, 162, 6)
    p("uc_lantern_post", 176, 150, 6)

    # ================================================================ AVENUE ENDS
    p("uc_portcullis", 16, 104, 11, solid="core", road_ok=True, allow_overlap=True, nudge=0)
    p("uc_sluice_gate", 185, 104, 9, solid="core", road_ok=True, allow_overlap=True, nudge=0)
    p("uc_portcullis", 100, 190, 12, solid=False, road_ok=True, portal_ok=True, allow_overlap=True, nudge=0)
    for x in (96, 103):
        p("uc_skull_pillar", x, 184, 8, road_ok=True, portal_ok=True, nudge=0)
    for x in (92, 108):
        dp("spirit_brazier", x, 178, 6, road_ok=True, nudge=1)
    for x in (95, 105):
        p("uc_lantern_post", x, 168, 6, road_ok=True, nudge=1)
    p("uc_bone_heap", 90, 188, 3)
    p("uc_bone_heap", 112, 187, 3)
    for y in (126, 146):
        for x in (94, 106):
            p("uc_lantern_post", x, y, 6, road_ok=True, nudge=1)


def build_layout():
    L = Layout()
    _terrain(L)
    _portals(L)
    _dress(L)
    _seal_pockets(L)
    return L


def _seal_pockets(L):
    """Walkable tiles cut off from the elevator arrival (nooks behind a throne, between props) become solid."""
    import collections
    z = L.z
    seen = {ELEV_ARRIVE}
    q = collections.deque([ELEV_ARRIVE])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < W and 0 <= n[1] < H and n not in seen and z.is_walkable(*n):
                seen.add(n)
                q.append(n)
    L.sealed = 0
    for y in range(H):
        for x in range(W):
            if (x, y) not in seen and z.is_walkable(x, y):
                z.collision_layer[y][x] = "landmark"
                L.sealed += 1


def register_baked(zone, baked_dir=BAKED_DIR, chunk=20):
    """Register the baked painting as ground + water + obstacle chunks."""
    for cy in range(0, H, chunk):
        for cx in range(0, W, chunk):
            fn = f"{baked_dir}/ground_{cx}_{cy}.jpg"
            if not os.path.exists(fn):
                raise FileNotFoundError(f"{fn} - run python3 tools/bake_undercity.py")
            w, h = min(chunk, W - cx), min(chunk, H - cy)
            zone.add_ground_chunk(fn, cx, cy, w, h)
            zone.ground_chunks[-1]["exact"] = True
            zone.add_water_chunk(fn, cx, cy, w, h)
            zone.add_obstacle_chunk(fn, cx, cy, w, h)


def generate_undercity():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=5, L=None):
    ys, xs = np.mgrid[0:H, 0:W]
    gx, gy = xs + 0.5, ys + 0.5
    F = fields(gx, gy)
    img = np.zeros((H, W, 3), np.uint8)
    img[:] = (70, 110, 105)
    for n in QUARTERS:
        img[quarter_sd(gx, gy, n) > 0] = (95, 95, 120)
        img[hall_sd(gx, gy, n) > 0] = (140, 120, 160)
    img[radius(gx, gy) < 50] = (60, 140, 130)
    rd = road_dist(gx, gy)
    img[rd > 0] = (200, 190, 150)
    img[F["canal"] > 0] = (60, 170, 70)
    img[F["bridge"] > 0] = (150, 120, 80)
    img[F["wall"] > 0] = (230, 230, 240)
    img[F["cliff"] > 0] = (35, 30, 30)
    for (px, py) in (ELEVATOR, DEEPS):
        img[py, px] = (255, 0, 255)
    for (cx, cy, r) in ALL_GATES:
        img[int(cy), int(cx)] = (255, 220, 0)
    Image.fromarray(img).resize((W * scale, H * scale), Image.NEAREST).save(path)


if __name__ == "__main__":
    import sys
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    shape_preview(sys.argv[1] if len(sys.argv) > 1 else "undercity_shape.png")
