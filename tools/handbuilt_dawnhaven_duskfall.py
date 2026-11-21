"""
Hand-built Duskfall Woods (160x140), levels 5-9: the north of Dawnhaven, deep red forest under a low sun, the old
outpost's heart and the road up to Firstlight Spire (docs/dawnhaven_brief.md).

    The Glade road ....... south edge (80,136): up from Amberleaf Glade
    Dawnrest ............. the hub (80,108): an old waystation the Conclave has put a roof back on
    The Red Hollow ....... the west (34,96): the deepest woods, bears and lynxes and the spiders in the leaves
    Duskmere ............. the dark tarn (52,70)
    The Wildmana Thicket . the middle north (82,56): where the outpost's spilled magic pooled and woke
    Saltspine Shore ...... the north-west coast (28,40): the naga's main camp, and their warren under it, Saltspine
                           Hollow (20,32)
    The Withered Spires .. the east (124,78): the outpost's inner quarter, where its dead still keep their posts
    The Lightwell Court .. north of the spires (124,52): the dark Lightwell that once fed the whole outpost, and the
                           stair down under it, the Lightwell Deep (124,44)
    The Spire road ....... north edge (80,4): up the headland to Firstlight Spire

HARD CONTRACTS (world/portal_manager.py)
  portals  Amberleaf Glade (80,136) <-> its north road (75,4); Firstlight Spire (80,4) <-> its south gate;
           Saltspine Hollow (20,32) <-> its way out; the Lightwell Deep (124,44) <-> its way out
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_central_barrens import _gauss
from world.chunk_paths import exists as _chunk_exists  # noqa: E402  (.webp, .jpg or .png)

NAME = "Duskfall Woods"
BAKED_DIR = "assets/tiles/dawnhaven/baked_duskfall"
AZP = "assets/tiles/azshara/props/"
BLD = "assets/buildings/"
W, H = 160, 140

PORTALS = {(80, 136): "Amberleaf Glade", (80, 4): "Firstlight Spire", (20, 32): "Saltspine Hollow",
           (124, 44): "The Lightwell Deep"}
ARRIVALS = [(80, 133), (80, 7), (20, 35), (124, 47)]
START = (80, 130)

# ------------------------------------------------------------------ the plan
ROADS = {
    "south":  ([(80, 137), (80, 124), (80, 108)], 3.2),
    "north":  ([(80, 108), (78, 94), (82, 78), (80, 62), (78, 44), (80, 24), (80, 4)], 3.2),
    "hollow": ([(78, 106), (62, 102), (46, 98), (34, 96)], 2.8),
    "shore":  ([(79, 60), (62, 52), (46, 44), (32, 38), (20, 34)], 2.6),
    "spires": ([(82, 104), (98, 96), (112, 86), (124, 78)], 2.8),
    "court":  ([(124, 78), (126, 64), (124, 50), (124, 46)], 2.8),
}

LAKES = {"duskmere": [(52, 72, 9, 6, -0.2, 1.3)]}
DEEP_SHRINK = {"duskmere": 2.6}


def coast_west(gy):
    """The west shore, with the naga's bay cutting in at the north-west."""
    gy = np.asarray(gy, float)
    return 7.0 + 2.0 * np.sin(0.19 * gy + 0.3) + 7.0 * _gauss(gy, 24, 10) - 3.0 * _gauss(gy, 90, 12)


def coast_east(gy):
    gy = np.asarray(gy, float)
    return 151.0 + 2.0 * np.sin(0.15 * gy + 1.1) + 1.2 * np.sin(0.43 * gy) - 6.0 * _gauss(gy, 20, 12)


def coast_north(gx):
    """The north shore either side of the Spire's headland, which runs straight up the middle to the town's gate."""
    gx = np.asarray(gx, float)
    return 10.0 + 6.0 * (1 - _gauss(gx, 80, 14)) - 9.0 * _gauss(gx, 80, 9) + 1.2 * np.sin(0.27 * gx)


def sea(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    return np.maximum.reduce([coast_north(gx) - gy, gx - coast_east(gy), coast_west(gy) - gx])


WOODS = [
    (24, 118, 9, 7, 0, 1.0), (104, 120, 8, 6, 0, 2.0), (56, 32, 9, 6, 0, 0.6), (122, 22, 17, 12, 0, 1.4),
    (138, 104, 7, 8, 0, 0.9), (60, 86, 5, 4, 0, 1.7), (100, 64, 6, 5, 0, 2.4), (146, 50, 5, 7, 0, 0.3),
    (34, 66, 5, 6, 0, 1.2),
]
BELTS = []
CLEARINGS = [
    (80, 108, 13, 9),           # Dawnrest
    (34, 96, 12, 9),            # the Red Hollow
    (82, 56, 12, 9),            # the Wildmana Thicket
    (28, 40, 11, 8),            # Saltspine Shore
    (124, 78, 13, 10),          # the Withered Spires
    (124, 52, 11, 8),           # the Lightwell Court
    (80, 132, 8, 6),            # the Glade road in
    (80, 10, 8, 6),             # the Spire road out
    (52, 72, 12, 9),            # Duskmere
]
BLUEBELL_PATCHES = [(82, 56, 9, 6), (52, 72, 11, 8)]          # moss and toadstools
CORRUPT_PATCHES = [(124, 78, 10, 7)]        # the spires' dead ground
BURNED_PATCHES = []
LUSH = 0.9
GRADE = (1.24, 1.10)
PAVED_PATCHES = [(80, 108, 6, 4), (124, 78, 8, 6), (124, 52, 6, 4)]

GAPS = [
    ("ell", 80, 134, 7, 5), ("ell", 80, 6, 7, 5), ("ell", 20, 34, 6, 5), ("ell", 124, 46, 6, 5),
    ("ell", 80, 108, 9, 7), ("ell", 124, 78, 9, 7), ("ell", 124, 52, 8, 6),
]


class _Spec(E.Spec):
    def woods_raw(self, gx, gy):
        out = super().woods_raw(gx, gy)
        sh, _dp = self.water_fields(gx, gy)
        return np.minimum(out, -(np.asarray(sh) + 3.0))


SPEC = _Spec(NAME, W, H, ROADS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea,
             woods=WOODS, belts=BELTS, clearings=CLEARINGS, rim={"south": 5}, gaps=GAPS,
             thicket=(0.80, 10.0, 1.6))

NPC_POSITIONS = {
    # Dawnrest
    "dh_selanne": (76, 104),        # Lightwarden Selanne Dawnsworn: the Lightwell, and putting the outpost back
    "dh_dorian": (86, 105),         # Magister Dorian Ashveil: the wild magic, and what woke in it
    "dh_lyra": (72, 112),           # Huntress Lyra Swiftbough: the Red Hollow
    "dh_joost": (88, 113),          # Joost Achterberg, a harbour pilot from Rotterdam, who means to build a boat
    "dh_dawnrest_trader": (84, 100),
    # the Withered Spires: the outpost's last commander, still on watch
    "dh_thalor": (116, 82),
    # Saltspine Shore: a Conclave scout watching the naga camp from the trees
    "dh_scout_nerys": (44, 50),
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {(20, 32): ("ent_naga_temple_door", 8, 7), (124, 44): ("ent_door_stairs_down", 6, 5)}

SUBZONES = [
    ("The Spire Road", 64, 0, 32, 22, None),
    ("Saltspine Shore", 8, 22, 40, 34, None),
    ("The Wildmana Thicket", 64, 42, 36, 28, None),
    ("The Lightwell Court", 108, 38, 34, 26, None),
    ("Duskmere", 36, 60, 32, 24, None),
    ("The Withered Spires", 104, 64, 44, 30, None),
    ("The Red Hollow", 10, 82, 46, 40, None),
    ("Dawnrest", 64, 96, 32, 24, None),
]

TREES = {
    "big":   [(AZP + "az_autumn_tree.png", 10), (AZP + "az_autumn_tree.png", 11), (AZP + "az_gold_tree.png", 10)],
    "mid":   [(AZP + "az_autumn_tree.png", 9), (AZP + "az_gold_tree.png", 8), (AZP + "az_birch_trio.png", 8)],
    "small": [(AZP + "az_birch_trio.png", 7), (AZP + "az_autumn_tree.png", 7)],
    "woods": [(AZP + "az_autumn_tree.png", 10), (AZP + "az_autumn_tree.png", 11), (AZP + "az_gold_tree.png", 9)],
}

#: low dusk light through the red woods
SCREEN_LIGHT = {"layer": "light_dusk", "strength": 0.38, "breathe": 0.2}
SCREEN_SHADE = {"layer": "shade_canopy_dapple", "strength": 0.42, "tile": 10, "drift": (1.6, 0.4)}
SCREEN_PARTICLES = {"sprites": ["p_leaf_maple", "p_leaf_dry", "p_leaf_elven", "p_leaf_oak"], "count": 14,
                    "size": 0.55, "fall": 30, "wind": -12, "sway": 22, "spin": 70}


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "The north of Dawnhaven, deep red woods under a low sun, where the old outpost's heart "
                             "still stands and its dead still keep their posts. The road goes on up to Firstlight Spire.",
                             "Kalimdor - Dawnhaven", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.seal_unreachable(L, START)
    dress(L)
    E.build_free_mask(L, NPC_POSITIONS.values())
    for lm in L.z.landmarks:
        ax, ay, w, h = lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]
        L.free_mask[max(0, ay):ay + h + 1, max(0, ax - 1):ax + w + 1] = False
    E.scatter_trees(L, TREES, seed=6201, spacing=6.6, grove_keep=0.82)
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def sprinkle(L):
    import random
    rnd = random.Random(6203)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    bush = logs = rocks = 0
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        if bush < 26 and r < 0.016:
            if L.prop("az_crimson_bush", x, y, 3, path_dir=AZP, solid=False, nudge=0):
                bush += 1
        elif logs < 16 and r < 0.042:
            if L.prop("az_autumn_log", x, y, 3, path_dir=AZP, solid=False, nudge=0):
                logs += 1
        elif rocks < 16 and r < 0.050:
            if L.prop("az_lichen_boulder", x, y, 4, path_dir=AZP, solid=False, nudge=0):
                rocks += 1
    L.clutter = (bush, logs, rocks)


CHEST_SPOTS = [(20, 104), (44, 120), (62, 40), (100, 44), (140, 70), (130, 120), (96, 132), (40, 76), (112, 104)]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    P = L.prop
    Z = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=AZP, **kw)          # noqa: E731
    B = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=BLD, **kw)          # noqa: E731
    D = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir="assets/tiles/dungeon_props/", **kw)  # noqa: E731

    # ---- Dawnrest: the waystation with its roof back on, and the camp round it
    B("be_great_hall", 80, 99, 10, solid="core")
    B("be_pavilion", 70, 108, 6, solid="core")
    B("be_storehouse", 92, 110, 6, solid="core")
    B("be_market_stall", 86, 101, 4, solid="core")
    Z("az_relic_crate", 94, 104, 3, solid="core")
    Z("az_dig_cart", 66, 114, 4, solid="core")
    P("br_signpost", 84, 118, 4)
    # Joost's boat taking shape on its stocks behind the storehouse
    Z("az_wreck_prow", 97, 115, 5, solid="core")
    # ---- the Red Hollow: the old hunting lodge's ruins
    B("be_ruined_house", 28, 92, 6, solid="core")
    Z("az_toppled_column", 40, 100, 4, solid="core")
    # ---- Duskmere
    Z("az_moon_arch", 44, 66, 6, solid="core")
    # ---- the Wildmana Thicket: the outpost's spilled magic, crystals grown out of the ground
    Z("az_arcane_crystal", 76, 52, 5, solid="core")
    Z("az_arcane_crystal", 90, 58, 4, solid="core")
    Z("az_crystal_tree", 84, 48, 8, solid="core")
    Z("az_leyline_node", 74, 62, 4, solid="core")
    # ---- Saltspine Shore: the naga's camp on the beach
    Z("az_naga_banner", 26, 44, 5, solid="core")
    Z("az_naga_banner", 34, 36, 5, solid="core")
    Z("az_tide_altar", 30, 46, 4, solid="core")
    Z("az_scale_pile", 36, 42, 3, solid=False)
    Z("az_coral_cluster", 16, 42, 4, solid="core")
    Z("az_giant_clam", 22, 48, 3, solid=False)
    # ---- the Withered Spires: the outpost's inner quarter, roofless, its towers still standing
    B("be_ruined_tower", 114, 72, 10, solid="core")
    B("be_ruined_tower", 136, 74, 10, solid="core")
    B("be_ruined_house", 132, 86, 6, solid="core")
    Z("az_noble_statue", 124, 72, 7, solid="core")
    Z("az_ruin_wall", 118, 88, 4, solid="core")
    D("broken_column", 128, 90, 4, solid="core")
    Z("az_broken_spire", 140, 82, 9, solid="core")
    # ---- the Lightwell Court: the dark well, and the stair down under it
    B("be_arcane_well", 124, 54, 6, solid="core")
    Z("az_mana_tower", 112, 50, 9, solid="core")
    Z("az_mana_tower", 136, 50, 9, solid="core")
    # ---- the Spire road: an elven arch where the headland starts
    Z("az_moon_arch", 80, 16, 7, solid=False, road_ok=True)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and _chunk_exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_duskfall_woods():
    L = build_layout()
    register_baked(L.zone)
    L.zone.light = dict(SCREEN_LIGHT)
    L.zone.shade = dict(SCREEN_SHADE)
    L.zone.particles = dict(SCREEN_PARTICLES)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
