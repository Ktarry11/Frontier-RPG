"""
Hand-built West Eastern Plaguelands (170x150), level 55-58. docs/plaguelands_design.md.

The western half of WoW's Eastern Plaguelands, read north-up: where the plague went worst. Stratholme's gates stand at
the top of the map behind Plaguewood's webs, Terrordale's dust lies along the Thondroril, the plague carts still meet
at Corin's Crossing, and the Marris Stead is a burned farmhouse nobody rebuilt.

Structure (tile coords, y down):

    West gate .......... (3,80): over the Thondroril from North WPL
    Terrordale ......... the ruined vale along the river in the south-west (26,104)
    The Marris Stead ... a burned farmhouse in the south (64,124)
    Plaguewood ......... the dead, web-hung forest in the north-west (42,46)
    Stratholme ......... the city gates at the top (40,5): the dungeon, its own map
    The Fungal Vale .... a sick hollow of mushrooms north of centre (110,38)
    Corin's Crossing ... the crossroads in the middle (100,82), where the plague carts meet
    East gate .......... (167,80): on to East EPL and Light's Hope

LATER PORTALS (their ground is cut; they go live with their maps): Stratholme (40,5), East EPL (167,80).
"""
import numpy as np

from tools import ashenvale_engine as E

BAKED_DIR = "assets/tiles/plaguelands/baked_epl_west"
EK = "assets/tiles/eastern_kingdoms/props/"
UF = "assets/tiles/undead_farmland/props/"
HF = "assets/tiles/haunted_forest/props/"
CI = "assets/tiles/cursed_isle/props/"
PL = "assets/tiles/plaguelands/props/"
W, H = 170, 150
NAME = "Eastern Plaguelands West"

PORTALS = {(3, 80): "Western Plaguelands North", (167, 80): "Eastern Plaguelands East"}
ARRIVALS = [(7, 80), (163, 80)]
LATER_PORTALS = {
    (40, 5): ("Stratholme", None),
}
START = (12, 80)

ROADS = {
    # the old road east from the river to Corin's Crossing and on toward Light's Hope
    "east":       ([(2, 80), (14, 80), (30, 84), (52, 86), (76, 84), (100, 82), (124, 80), (146, 80), (168, 80)], 3.4),
    # north from the Crossing past the Fungal Vale, then west through Plaguewood to Stratholme's gates
    "strat":      ([(100, 82), (104, 64), (108, 46), (96, 30), (76, 22), (56, 14), (42, 8), (40, 4)], 3.0),
    # south-west into Terrordale and the Marris Stead
    "terrordale": ([(30, 84), (28, 96), (26, 104)], 2.6),
    "marris":     ([(76, 84), (70, 100), (66, 114), (64, 124)], 2.6),
}

RIVERS = [   # the Thondroril's east bank: just the river's edge along the west side
    ([(10, 0), (8, 30), (12, 60), (9, 96), (12, 130), (10, 150)], 3.0, 1.2),
]
FORDS = [(10, 80, 7)]

LAKES = {"ponds": [(132, 120, 6, 4, 0, 0.9), (150, 34, 4, 3, 0, 2.1)]}
DEEP_SHRINK = {"ponds": 2.0}

MESAS = [
    (74, 48, 7, 6, 10), (130, 56, 6, 9, 0), (46, 140, 6, 5, 0), (96, 120, 6, 6, 0), (150, 100, 5, 7, 0),
    (128, 30, 5, 5, 0),
]
RIDGES = [
    ([(18, 24), (26, 14), (34, 20)], 2.4),        # the shoulder west of Stratholme's gates
    ([(48, 22), (58, 26), (64, 20)], 2.2),        # ... and east of them
]
#: Plaguewood is the densest dead forest anywhere: the woods here are mostly in the north-west
WOODS = [
    (32, 46, 14, 12, 0, 1.0), (58, 56, 8, 8, 0, 2.2), (20, 66, 6, 6, 0, 0.4), (138, 132, 9, 7, 0, 1.7),
    (156, 56, 6, 9, 0, 2.6), (84, 132, 7, 5, 0, 0.8),
]
BELTS = []
CLEARINGS = [
    (12, 80, 8, 6),             # the west gate
    (26, 104, 13, 10),          # Terrordale
    (64, 124, 11, 8),           # the Marris Stead
    (42, 44, 9, 7),             # a clearing deep in Plaguewood
    (40, 10, 10, 7),            # Stratholme's gates
    (110, 38, 13, 10),          # the Fungal Vale
    (100, 82, 12, 9),           # Corin's Crossing
    (160, 80, 8, 6),            # the east gate
]
GAPS = [
    ("ell", 3, 80, 7, 6), ("ell", 40, 5, 9, 6), ("ell", 167, 80, 7, 6),
    ("ell", 26, 104, 11, 8), ("ell", 64, 124, 9, 7), ("ell", 42, 44, 7, 6), ("ell", 110, 38, 11, 8),
    ("ell", 100, 82, 10, 8),
]

SPEC = E.Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK,
              mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={"north": 4, "south": 4}, rock_rim={"west": 3, "east": 6}, gaps=GAPS, fords=FORDS,
              thicket=(0.76, 9.0, 2.3))

NPC_POSITIONS = {}

SUBZONES = [
    ("Terrordale", 8, 90, 36, 28, None),
    ("The Marris Stead", 50, 112, 28, 22, None),
    ("Plaguewood", 14, 26, 56, 40, None),
    ("Stratholme Gates", 26, 2, 30, 18, None),
    ("The Fungal Vale", 94, 24, 32, 28, None),
    ("Corin's Crossing", 86, 70, 30, 26, None),
]


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}

TREES = {   # Kyle's dead oaks in the open; the Plaguewood's purple-crowned dead fill the woods
    "big": [(PL + "pl_dead_oak.png", 9), (CI + "cursed_dead_tree_cluster.png", 9), (PL + "pl_plaguewood_tree.png", 9)],
    "mid": [(PL + "pl_dead_oak.png", 8), (UF + "dead_tree_bare.png", 7), (HF + "dead_pine_cluster.png", 7)],
    "small": [(UF + "dead_tree_bare.png", 6), (PL + "pl_dead_oak.png", 6)],
    "woods": [(PL + "pl_plaguewood_tree.png", 9), (PL + "pl_blight_pine.png", 9), (CI + "cursed_dead_tree_cluster.png", 9)],
}

BLUEBELL_PATCHES = [(64, 124, 9, 6), (100, 82, 8, 6)]
CORRUPT_PATCHES = [(110, 38, 12, 9), (42, 44, 14, 12), (40, 10, 9, 6), (26, 104, 9, 7)]
BURNED_PATCHES = [(64, 124, 6, 4), (100, 82, 6, 5)]
PAVED_PATCHES = [(40, 8, 7, 4)]
GRADE = (0.95, 1.05)


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "Where the plague went worst: Plaguewood's webs, Terrordale's dust, the carts still meeting "
                             "at Corin's Crossing, and Stratholme's gates at the top of the road.",
                             "Eastern Kingdoms - Lordaeron", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    for (px, py) in LATER_PORTALS:
        L.z.collision_layer[py][px] = None
    E.seal_unreachable(L, START)
    dress(L)
    E.build_free_mask(L, NPC_POSITIONS.values())
    for lm in L.z.landmarks:
        ax, ay, w, h = lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]
        L.free_mask[max(0, ay):ay + h + 1, max(0, ax - 1):ax + w + 1] = False
    E.scatter_trees(L, TREES, seed=6301, spacing=7.0, scale=1.0)
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def sprinkle(L):
    import random
    rnd = random.Random(6303)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = {"web": 0, "thorn": 0, "rock": 0}
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        if n["web"] < 16 and r < 0.012 and x < 75 and y < 70:
            n["web"] += bool(L.prop("ek_web_boulder", x, y, 3, path_dir=EK, solid=False, nudge=0))
        elif n["thorn"] < 30 and r < 0.026:
            n["thorn"] += bool(L.prop("ek_thorn_bush", x, y, 3, path_dir=EK, solid=False, nudge=0))
        elif n["rock"] < 16 and r < 0.034:
            n["rock"] += bool(L.prop("rock_outcrop_small", x, y, 4, path_dir=E.AP, solid=False, nudge=0))
    L.clutter = n


CHEST_SPOTS = [(22, 112), (44, 100), (60, 136), (30, 36), (64, 40), (120, 28), (126, 46), (88, 96), (120, 96),
               (148, 120), (150, 44), (80, 64)]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    P = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=EK, **kw)
    Q = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=PL, **kw)      # Kyle's Plaguelands props
    BQ = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=PL, fraction=0.5, **kw)
    B = L.bld

    # ---- Terrordale: the ruined vale
    BQ("pl_farmhouse_burned", 18, 98, 7)
    BQ("pl_ruin_wall", 32, 100, 6)
    BQ("pl_farmhouse_burned", 24, 112, 7)
    Q("pl_ruin_arch", 28, 106, 5)
    Q("pl_skull_pile", 36, 110, 3, solid=False)
    Q("pl_bone_barricade", 14, 106, 4)

    # ---- the Marris Stead
    BQ("pl_farmhouse_burned", 62, 120, 8)
    BQ("pl_barn_plagued", 74, 116, 7)
    Q("pl_fence_broken", 54, 126, 3, solid=False)
    P("ek_farm_well", 70, 126, 4)
    P("ek_scarecrow", 58, 130, 4)
    Q("pl_pumpkin_rot", 66, 132, 4, solid=False)

    # ---- Plaguewood: webs, the dead, and a Scourge spire
    P("ek_egg_sacs", 38, 42, 3)
    P("ek_egg_sacs", 48, 50, 3)
    P("ek_web_boulder", 44, 46, 3)
    B("scourge_spire", 30, 40, 10, nudge=8)
    Q("pl_necro_obelisk", 54, 38, 6)
    Q("pl_plague_mushrooms", 24, 52, 4, nudge=8)

    # ---- Stratholme's gates (the city is its own map)
    B("strat_gates", 40, 12, 10, road_ok=True, nudge=0)
    P("ek_gibbet", 28, 14, 5)
    Q("pl_meat_wagon", 52, 16, 4)
    Q("pl_scourge_banner", 32, 18, 5)
    Q("pl_scourge_banner", 48, 18, 5)

    # ---- the Fungal Vale
    Q("pl_plague_mushrooms", 106, 36, 4)
    Q("pl_plague_mushrooms", 116, 40, 4)
    P("ek_toadstools", 110, 44, 3)
    Q("pl_runoff_pool", 100, 44, 3, solid=False)

    # ---- Corin's Crossing: where the plague carts meet, and the Scourge's ziggurat
    BQ("pl_farmhouse_burned", 92, 76, 7)
    B("scourge_ziggurat", 110, 74, 9)
    BQ("pl_ruin_wall", 94, 90, 6)
    Q("pl_meat_wagon", 100, 86, 4)
    Q("pl_cauldron_live", 106, 88, 4)
    Q("pl_ghoul_pit", 112, 92, 3, solid=False)
    Q("pl_butcher_block", 88, 86, 3)
    P("ek_signpost", 104, 80, 4)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_epl_west():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/epl_west_shape.png"
    L = build_layout()
    seen, walk, _ = E.reachable_report(L, START)
    print(f"placed={L.placed} trees={L.trees} sealed={L.sealed} walkable={walk} reachable={seen} skipped={len(L.skipped)}")
    for sk in L.skipped:
        if sk[0] not in ("ek_thorn_bush", "rock_outcrop_small", "ek_web_boulder"):
            print("  skipped", sk)
    SPEC.shape_preview(out, 4, portals=list(PORTALS) + list(LATER_PORTALS), npc=list(NPC_POSITIONS.values()), layout=L)
    print("wrote", out)
