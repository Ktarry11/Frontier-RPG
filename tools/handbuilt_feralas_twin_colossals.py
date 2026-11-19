"""
Hand-built The Twin Colossals (180x220), levels 47-49: Feralas's north coast (docs/feralas_brief.md).

The top of the L. You come up the coast road from the south and the two great arches stand over the middle of the
map, with the sea down the west side.

    South road ............ the south edge (112,216): from the Forgotten Coast
    The Sentinels' Watch .. the south (110,186): the Sentinels' camp, a few quest givers (safe)
    The Twin Colossals .... the middle: two great granite arches, giants walking between them
    Rage Scar Hold ........ the east hills: the yetis' hollow
    Ruins of Ravenwind .... the north-west coast: the naga's second foothold
    The Dream Bough ....... the north-east: a great tree whose roots reach into the Dream

THE ART: built before Kyle's Feralas sheets (Kyle, 19 Nov 2026: "Build without art for now"). The ground paints from
FERALAS_SHEET; the arches are Stonetalon's wind arch and spires standing in for the Colossals until sheet 6.

HARD CONTRACTS (world/portal_manager.py)
  portals  The Forgotten Coast (112,216) <-> its north road (112,4)
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_central_barrens import _gauss

BAKED_DIR = "assets/tiles/feralas/baked_twin_colossals"
NAME = "The Twin Colossals"
W, H = 180, 220
AV = E.AP
STP = "assets/tiles/stonetalon/props/"
ENT = "assets/tiles/cave_entrances/"
BLD = "assets/buildings/"

PORTALS = {(112, 216): "The Forgotten Coast"}
ARRIVALS = [(112, 213)]
LATER_PORTALS = {}
START = (110, 190)     # the Sentinels' Watch


def coast_x(gy):
    gy = np.asarray(gy, float)
    return (40.0 + 14.0 * _gauss(gy, 40, 16) - 6.0 * _gauss(gy, 110, 14) + 4.0 * _gauss(gy, 170, 12)
            + 1.6 * np.sin(0.23 * gy + 0.4) + 1.0 * np.sin(0.51 * gy + 1.1))


def sea(gx, gy):
    gx = np.asarray(gx, float)
    return coast_x(gy) - gx


ROADS = {
    "south":     ([(112, 216), (112, 200), (110, 186)], 3.4),
    # north from the Watch between the Colossals
    "colossals": ([(110, 186), (104, 160), (96, 132), (92, 104), (94, 80), (100, 60)], 3.2),
    # north-west to Ravenwind on the coast
    "ravenwind": ([(94, 80), (78, 60), (64, 42), (58, 28)], 2.8),
    # north-east to the Dream Bough
    "bough":     ([(100, 60), (118, 46), (136, 36), (148, 30)], 2.8),
    # east from the Colossals to Rage Scar Hold
    "ragescar":  ([(96, 132), (118, 128), (138, 124), (154, 118)], 2.8),
}

LAKES = {"tarns": [(140, 160, 6, 4, 0, 0.5), (74, 100, 4, 3, 0, 1.2)]}
DEEP_SHRINK = {"tarns": 1.8}
RIVERS = [([(170, 80), (150, 96), (128, 104), (108, 112), (84, 120), (60, 126), (44, 128)], 2.4, 1.0)]
FORDS = [(93, 116, 6), (140, 99, 5)]

# ---- the Colossals: two great granite masses either side of the road, the arches dressed on them
MESAS = [(76, 140, 12, 16, 0), (120, 98, 12, 14, 0),
         (164, 136, 10, 18, 0), (166, 40, 10, 12, 0), (60, 190, 8, 8, 0)]
RIDGES = [([(150, 106), (158, 116), (152, 128)], 2.4)]

WOODS = [
    (130, 170, 10, 8, 0, 1.0), (70, 170, 8, 7, 0, 2.0), (140, 70, 8, 7, 0, 0.6), (80, 40, 7, 6, 0, 1.4),
    (150, 196, 10, 6, 0, 0.4), (120, 150, 6, 6, 0, 2.2), (60, 80, 6, 6, 0, 1.1),
]
BELTS = [([(40, 2), (100, 3), (180, 2)], 5.0), ([(40, 217), (90, 218), (140, 217), (180, 218)], 4.0)]
CLEARINGS = [
    (110, 188, 12, 9),          # the Sentinels' Watch
    (98, 120, 14, 12),          # between the Colossals
    (60, 34, 12, 10),           # Ruins of Ravenwind
    (146, 34, 14, 12),          # the Dream Bough
    (150, 120, 12, 10),         # Rage Scar Hold
    (112, 208, 8, 7),           # the south road in
]
BLUEBELL_PATCHES = [(146, 34, 12, 9)]       # the Dream Bough's flowers
PAVED_PATCHES = [(60, 34, 8, 6)]            # Ravenwind's Highborne paving
LUSH = 1.15
GRADE = (1.22, 1.10)

GAPS = [("ell", 112, 216, 8, 7), ("ell", 110, 188, 10, 8), ("ell", 98, 120, 10, 9), ("ell", 146, 34, 9, 8),
        ("ell", 150, 120, 9, 7), ("ell", 60, 34, 9, 7)]


class _Spec(E.Spec):
    def woods_raw(self, gx, gy):
        out = super().woods_raw(gx, gy)
        sh, _dp = self.water_fields(gx, gy)
        return np.minimum(out, -(np.asarray(sh) + 3.0))


SPEC = _Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea,
             mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
             rim={"east": 5}, rock_rim={"east": 4}, gaps=GAPS, fords=FORDS, thicket=(0.72, 10.0, 0.9))

#: the Sentinels' Watch (the quest pass, docs/feralas_quest_plan.md), and the Circle's dreamwatcher at the Bough
NPC_POSITIONS = {"fe_watch_captain": (106, 184), "fe_watch_tahu": (116, 184), "fe_dreamwatcher": (140, 40)}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}

SUBZONES = [
    ("The Twin Colossals", 62, 86, 74, 70, None),
    ("Rage Scar Hold", 132, 100, 44, 44, None),
    ("Ruins of Ravenwind", 30, 10, 54, 50, None),
    ("The Dream Bough", 120, 12, 56, 44, None),
    ("The Sentinels' Watch", 94, 174, 32, 26, None),
]

TREES = {
    "big":   [(AV + "large_canopy_tree.png", 11), (STP + "st_sequoia_great.png", 13), (AV + "ash_giant_ash_tree.png", 12)],
    "mid":   [(AV + "medium_canopy_tree.png", 9), (STP + "st_sequoia_mature.png", 10), (AV + "canopy_tree_cluster.png", 9)],
    "small": [(STP + "st_sequoia_young.png", 7), (AV + "medium_canopy_tree.png", 7)],
    "woods": [(AV + "large_canopy_tree.png", 11), (STP + "st_sequoia_great.png", 13), (AV + "canopy_tree_cluster.png", 10)],
}


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "Feralas's north coast under two great stone arches. Giants walk between them, the naga "
                             "dig at Ravenwind, and in the north-east a tree's roots reach somewhere else.",
                             "Kalimdor - Feralas", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.seal_unreachable(L, START)
    dress(L)
    E.build_free_mask(L, NPC_POSITIONS.values())
    for lm in L.z.landmarks:
        ax, ay, w, h = lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]
        L.free_mask[max(0, ay):ay + h + 1, max(0, ax - 1):ax + w + 1] = False
    E.scatter_trees(L, TREES, seed=4701, spacing=5.8, grove_keep=0.8)
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def sprinkle(L):
    import random
    rnd = random.Random(4703)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    ferns = logs = rocks = 0
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        if ferns < 22 and r < 0.014:
            if L.prop("st_ferns_big", x, y, 3, path_dir=STP, solid=False, nudge=0):
                ferns += 1
        elif logs < 12 and r < 0.036:
            if L.prop("st_nurse_log", x, y, 3, path_dir=STP, solid=False, nudge=0):
                logs += 1
        elif rocks < 26 and r < 0.050:
            if L.prop("st_moss_boulder", x, y, 3, path_dir=STP, solid=False, nudge=0):
                rocks += 1
    L.clutter = (ferns, logs, rocks)


CHEST_SPOTS = [(130, 190), (80, 196), (60, 120), (130, 80), (160, 100), (150, 160), (84, 20), (160, 20), (50, 64),
               (108, 30)]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    A = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=AV, **kw)                       # noqa: E731
    S = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=STP, **kw)                      # noqa: E731
    N = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=ENT, **kw)                      # noqa: E731
    F = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir="assets/tiles/felwood/props/", **kw)  # noqa: E731

    A("ash_signpost", 104, 168, 4)
    A("ash_signpost", 100, 86, 4)
    # ---- the Sentinels' Watch: a camp, not a town
    A("ash_sentinel_tent", 102, 182, 5, solid="core")
    A("ash_sentinel_tent", 120, 182, 5, solid="core")
    A("ash_watch_platform", 112, 178, 7, solid="core")
    A("ash_sentinel_banner", 108, 192, 5, solid="core")
    A("ash_sentinel_weapon_rack", 118, 192, 3, solid="core")
    # ---- the Twin Colossals: the arches over the granite (Stonetalon's wind arch until sheet 6)
    S("st_wind_arch", 76, 126, 14, solid="core")
    S("st_wind_arch", 120, 86, 14, solid="core")
    S("st_wind_spire", 68, 150, 10, solid="core")
    S("st_wind_spire", 128, 108, 10, solid="core")
    # ---- Rage Scar Hold: the yetis' hollow in the east hills
    N("ent_savanna_cave", 158, 114, 6, solid="core")
    A("ash_log_pile", 146, 126, 3, solid="core")
    S("st_giant_snag", 160, 128, 7, solid="core")
    # ---- Ruins of Ravenwind: Highborne stone on the coast, the naga digging in it
    F("fw_highborne_arch", 60, 28, 8, solid="core")
    A("ash_elven_ruin_wall", 50, 36, 5, solid="core")
    A("ash_ivy_pillar", 70, 38, 6, solid="core")
    N("ent_naga_temple_door", 54, 22, 7, solid="core")
    # ---- the Dream Bough: the great tree, and the shimmer between its roots
    S("st_sequoia_great", 150, 24, 15, solid="core")
    N("ent_moonlit_arch", 150, 30, 7, solid="core")
    A("ash_glow_mushroom_ring", 138, 44, 3, solid=False)
    A("ash_nightbloom_bush", 158, 42, 3, solid="core")
    A("ash_moonstone_crystals", 136, 32, 4, solid="core")


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_twin_colossals():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
