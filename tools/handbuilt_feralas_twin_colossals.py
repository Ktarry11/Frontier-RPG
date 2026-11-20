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
GRADE = None           # Kyle's own ground (19 Nov 2026) is rich already; the lift was for the borrowed Ashenvale ground

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

#: Kyle's Feralas nature sheet (docs/feralas_art_prompts.md sheet 2, 19 Nov 2026): the giant forest's north coast.
FE = "assets/tiles/feralas/props/"
TREES = {
    "big":   [(FE + "fe_giant_tree.png", 13), (FE + "fe_vine_giant.png", 12), (FE + "fe_giant_tree_hollow.png", 13)],
    "mid":   [(FE + "fe_root_bridge_tree.png", 10), (FE + "fe_sitka_spruce.png", 11), (FE + "fe_bigleaf_maple.png", 9)],
    "small": [(FE + "fe_tree_fern.png", 6), (FE + "fe_sitka_spruce.png", 7)],
    "woods": [(FE + "fe_giant_tree.png", 13), (FE + "fe_vine_giant.png", 12), (FE + "fe_sitka_spruce.png", 11)],
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
    E.scatter_trees(L, TREES, seed=4701, spacing=5.8, grove_keep=0.5)          # Kyle, 19 Nov 2026: "Keep in mind the number of collisions (Trees) in feralas" (0.8 before: a quarter fewer groves)
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
    G = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=FE, **kw)                       # noqa: E731
    B = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=BLD, **kw)                      # noqa: E731

    A("ash_signpost", 104, 168, 4)
    A("ash_signpost", 100, 86, 4)
    # ---- the Sentinels' Watch: a camp, not a town
    B("fm_field_tent", 102, 182, 5, solid="core", nudge=10)
    B("fm_field_tent", 120, 182, 5, solid="core", nudge=10)
    B("fm_tree_lookout", 112, 178, 7, solid="core", nudge=10)
    B("fm_banner", 108, 192, 5, solid="core", nudge=10)
    B("fm_glaive_rack", 118, 192, 3, solid="core", nudge=10)
    # ---- the Twin Colossals: the two great arches over the granite
    B("fe_twin_colossal", 76, 126, 14, solid="core", nudge=10)
    B("fe_twin_colossal", 120, 86, 14, solid="core", nudge=10)
    G("fe_granite_outcrop", 68, 150, 6, solid="core", nudge=10)
    G("fe_granite_outcrop", 128, 108, 6, solid="core", nudge=10)
    # ---- Rage Scar Hold: the yetis' hollow in the east hills
    B("fe_rage_scar_mouth", 158, 114, 8, solid="core", nudge=10)
    G("fe_bone_pile", 146, 126, 3, solid="core", nudge=10)
    G("fe_dead_snag", 160, 128, 6, solid="core", nudge=10)
    # ---- Ruins of Ravenwind: Highborne stone on the coast, the naga digging in it
    G("fe_highborne_arch", 60, 28, 7, solid="core", nudge=10)
    G("fe_ruin_window", 50, 36, 5, solid="core", nudge=10)
    G("fe_ivy_column", 70, 38, 6, solid="core", nudge=10)
    G("fe_naga_shrine", 54, 22, 6, solid="core", nudge=10)
    G("fe_dug_relics", 64, 44, 3, solid="core", nudge=10)
    # ---- the Dream Bough: the great tree, and the shimmer between its roots
    B("fe_dream_bough", 150, 30, 15, solid="core", nudge=10)
    G("fe_dream_flowers", 138, 44, 3, solid=False, nudge=10)
    G("fe_dream_sapling", 160, 42, 5, solid="core", nudge=10)
    G("fe_dream_flowers", 164, 34, 3, solid=False, nudge=10)


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
