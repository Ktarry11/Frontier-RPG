"""
Hand-built East Eastern Plaguelands (170x150), level 56-60. docs/plaguelands_design.md.

The eastern half of WoW's Eastern Plaguelands, read north-up: the Argent Dawn's chapel at Light's Hope, the Scarlet
fortress town of Tyr's Hand on the southern coast, Darrowshire's ghosts, Crown Guard Tower in the middle, and the far
north-east where Zul'Mashar's trolls and Quel'Lithien's elves held out longest.

THE PURE 60 RULE: this map runs to 60 but starts at 56, so it is NOT pure 60. Nothing post-game grows or drops here.

Structure (tile coords, y down):

    West gate ............ (3,80): from West EPL
    Crown Guard Tower .... the old tower on the road (52,78), empty: its camp moved into Light's Hope (Kyle, 16 Nov 2026:
                           "Also fold Crown Guard Camp into Lights Hope")
    Darrowshire .......... the ghost village in the south-west (34,124)
    Blackwood Lake ....... in the middle (88,54)
    Light's Hope Chapel .. the Argent Dawn's town, its own map (tools/handbuilt_lights_hope.py); its gate is up the
                           spur at (128,72), north of the Tyr's Hand road
    Tyr's Hand ........... the Scarlet fortress town on the south coast (134,128)
    Quel'Lithien Lodge ... the elves' lodge in the north (92,16)
    Zul'Mashar ........... the troll ruins in the far north-east (148,22)
    The Pestilent Scar ... a blighted gash east of centre (110,60)
"""
import numpy as np

from tools import ashenvale_engine as E

BAKED_DIR = "assets/tiles/plaguelands/baked_epl_east"
EK = "assets/tiles/eastern_kingdoms/props/"
UF = "assets/tiles/undead_farmland/props/"
HF = "assets/tiles/haunted_forest/props/"
CI = "assets/tiles/cursed_isle/props/"
PL = "assets/tiles/plaguelands/props/"
W, H = 170, 150
NAME = "Eastern Plaguelands East"

PORTALS = {(3, 80): "Eastern Plaguelands West", (106, 60): "The Bone Mines", (128, 72): "Light's Hope Chapel"}
ARRIVALS = [(7, 80), (106, 58), (128, 75)]
LATER_PORTALS = {}
START = (12, 80)

ROADS = {
    # the road east from the west gate past Crown Guard to Light's Hope
    "east":       ([(2, 80), (20, 80), (40, 78), (52, 78), (72, 82), (96, 84), (116, 86), (128, 86)], 3.4),
    # south from Light's Hope down to Tyr's Hand
    "tyr":        ([(128, 86), (130, 100), (132, 114), (134, 126)], 3.0),
    # south-west from Crown Guard to Darrowshire
    "darrowshire": ([(52, 78), (46, 96), (40, 112), (34, 124)], 2.6),
    # north from Crown Guard past Blackwood Lake to Quel'Lithien, then east to Zul'Mashar
    "north":      ([(52, 78), (62, 62), (78, 46), (88, 30), (92, 16)], 2.6),
    "zulmashar":  ([(92, 22), (112, 22), (132, 22), (148, 22)], 2.4),
    # the spur up to Light's Hope's gate
    "lights_hope": ([(128, 86), (128, 79), (128, 72)], 3.0),
}

LAKES = {
    "blackwood": [(84, 56, 9, 6, 0, 0.8)],
    # the sea along the south-east coast, south of Tyr's Hand
    "coast": [(168, 150, 40, 18, 0, 0.4), (110, 156, 30, 10, 0, 1.4), (176, 112, 14, 26, 0, 2.2)],
}
DEEP_SHRINK = {"blackwood": 2.5, "coast": 6.0}

MESAS = [
    (70, 110, 6, 6, 0), (100, 108, 6, 5, 10), (34, 52, 6, 8, 0), (118, 44, 5, 6, 0), (150, 64, 5, 8, 0),
    (20, 110, 5, 6, 0),
]
RIDGES = [
    ([(104, 70), (112, 60), (118, 66)], 2.4),     # the Pestilent Scar's lip
]
WOODS = [
    (24, 30, 12, 10, 0, 1.0), (66, 26, 8, 7, 0, 2.1), (124, 40, 6, 7, 0, 0.5), (160, 40, 6, 9, 0, 1.6),
    (80, 128, 9, 6, 0, 2.6), (18, 140, 8, 6, 0, 0.3),
]
BELTS = []
CLEARINGS = [
    (12, 80, 8, 6),
    (52, 78, 12, 9),            # Crown Guard camp
    (34, 124, 13, 10),          # Darrowshire
    (128, 86, 14, 10),          # Light's Hope
    (134, 126, 16, 11),         # Tyr's Hand
    (92, 16, 11, 7),            # Quel'Lithien Lodge
    (148, 22, 12, 9),           # Zul'Mashar
    (110, 60, 9, 7),            # the Pestilent Scar
]
GAPS = [
    ("ell", 3, 80, 7, 6), ("ell", 128, 74, 5, 5), ("ell", 52, 78, 10, 7), ("ell", 34, 124, 11, 8), ("ell", 128, 86, 12, 8),
    ("ell", 134, 126, 13, 9), ("ell", 92, 16, 9, 6), ("ell", 148, 22, 10, 7), ("ell", 110, 60, 7, 6),
]

SPEC = E.Spec(NAME, W, H, ROADS, lakes=LAKES, deep_shrink=DEEP_SHRINK,
              mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={"north": 4}, rock_rim={"west": 6, "east": 5}, gaps=GAPS, thicket=(0.80, 9.0, 1.2))

NPC_POSITIONS = {
    # Light's Hope's people and Crown Guard's are in Light's Hope's own map now (tools/handbuilt_lights_hope.py)
    "epl_ds_pamela": (30, 127),
}

SUBZONES = [
    ("Crown Guard Tower", 44, 66, 18, 16, None),
    ("Darrowshire", 18, 110, 34, 28, None),
    ("Blackwood Lake", 72, 44, 26, 22, None),
    ("Light's Hope Gate", 120, 68, 16, 12, None),
    ("Tyr's Hand", 114, 112, 42, 28, None),
    ("Quel'Lithien Lodge", 78, 6, 28, 20, None),
    ("Zul'Mashar", 132, 8, 36, 28, None),
    ("The Pestilent Scar", 98, 50, 24, 22, None),
]


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


#: the cave mouths (tools/handbuilt_plaguelands_caves.py MOUTHS): portal tile -> (sprite, w, h)
CAVES = {(106, 60): ("ent_collapsed_mine", 8, 6)}

TREES = {   # Kyle's Plaguelands trees; Quel'Lithien's pines in the north woods
    "big": [(PL + "pl_dead_oak.png", 9), (PL + "pl_blight_pine.png", 9), (EK + "ek_pine_tall.png", 9)],
    "mid": [(PL + "pl_dead_oak.png", 8), (UF + "dead_tree_bare.png", 7), (PL + "pl_blight_pine.png", 8)],
    "small": [(UF + "dead_tree_bare.png", 6), (PL + "pl_blight_pine.png", 7)],
    "woods": [(PL + "pl_blight_pine.png", 9), (EK + "ek_pine_trio.png", 9), (PL + "pl_dead_oak.png", 9)],
}

BLUEBELL_PATCHES = [(34, 124, 10, 7)]
CORRUPT_PATCHES = [(110, 60, 9, 7), (34, 124, 6, 5)]
BURNED_PATCHES = [(34, 124, 9, 7), (148, 22, 7, 5)]
PAVED_PATCHES = [(128, 86, 8, 6), (134, 126, 12, 8), (52, 78, 5, 4)]
GRADE = (0.95, 1.05)


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "The Argent Dawn's chapel at Light's Hope, the Scarlet fortress of Tyr's Hand on the "
                             "coast, Darrowshire's ghosts, and the far north-east where the trolls and elves held out.",
                             "Eastern Kingdoms - Lordaeron", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.seal_unreachable(L, START)
    dress(L)
    E.build_free_mask(L, NPC_POSITIONS.values())
    for lm in L.z.landmarks:
        ax, ay, w, h = lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]
        L.free_mask[max(0, ay):ay + h + 1, max(0, ax - 1):ax + w + 1] = False
    E.scatter_trees(L, TREES, seed=6401, spacing=7.6, scale=1.0)
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def sprinkle(L):
    import random
    rnd = random.Random(6403)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = {"thorn": 0, "rock": 0}
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        if n["thorn"] < 30 and r < 0.020:
            n["thorn"] += bool(L.prop("ek_thorn_bush", x, y, 3, path_dir=EK, solid=False, nudge=0))
        elif n["rock"] < 18 and r < 0.030:
            n["rock"] += bool(L.prop("rock_outcrop_small", x, y, 4, path_dir=E.AP, solid=False, nudge=0))
    L.clutter = n


CHEST_SPOTS = [(26, 136), (48, 112), (70, 40), (100, 30), (150, 36), (150, 76), (110, 100), (160, 120),
               (90, 70), (24, 60)]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    P = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=EK, **kw)
    Q = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=PL, **kw)      # Kyle's Plaguelands props
    BQ = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=PL, fraction=0.5, **kw)
    B = L.bld

    # ---- Crown Guard Tower: empty now, a landmark on the road
    B("crown_guard_tower", 52, 70, 10)
    P("ek_signpost", 58, 86, 4)
    P("ek_ruin_wall", 44, 76, 4)

    # ---- Light's Hope's gate, up the spur (the town is behind it: tools/handbuilt_lights_hope.py)
    B("ek_gatehouse", 128, 71, 9)
    P("ek_angel_statue", 136, 80, 6)
    P("ek_signpost", 122, 88, 4)

    # ---- Tyr's Hand: the Scarlet fortress town
    B("sc_courtyard_gate", 130, 116, 8, road_ok=True)
    B("tyr_town_hall", 136, 128, 8)
    B("tyr_abbey", 122, 126, 8)
    B("sc_town_house", 144, 124, 7)
    B("sc_bell_tower", 128, 136, 8)
    B("tyr_harbour_tower", 150, 134, 9)
    B("tyr_dock_warehouse", 142, 140, 6, shore_ok=True, nudge=5)
    B("sc_stable", 116, 136, 6)
    for (x, y) in [(120, 118), (146, 118)]:
        P("ek_scarlet_banner", x, y, 5)
    Q("sc_war_tent", 154, 124, 5)

    # ---- Darrowshire: the ghost village
    BQ("pl_farmhouse_burned", 26, 118, 7)
    BQ("pl_ruin_wall", 40, 118, 6)
    BQ("pl_barn_plagued", 30, 132, 7)
    Q("pl_darrowshire_doll", 34, 124, 3, solid=False)
    Q("pl_stall_burned", 42, 128, 4)
    P("ek_cemetery_fence", 44, 134, 3, solid=False)

    # ---- Quel'Lithien Lodge
    B("ek_cottage_medium", 92, 12, 7)
    Q("ql_lantern_post", 98, 18, 5)
    Q("ql_lantern_post", 86, 18, 5)
    P("ek_pine_trio", 82, 22, 8)

    # ---- Zul'Mashar: troll ruins
    BQ("zm_ruin_block", 142, 18, 6)
    BQ("zm_ruin_block", 154, 24, 6)
    P("ek_ruin_wall", 148, 30, 4)
    P("ek_cross_crows", 136, 26, 4)

    # ---- the Pestilent Scar
    Q("pl_cauldron_dead", 110, 60, 4)
    Q("pl_ghoul_pit", 116, 64, 3, solid=False)
    Q("pl_necro_obelisk", 104, 56, 6)
    Q("pl_skull_pile", 112, 54, 3, solid=False)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_epl_east():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/epl_east_shape.png"
    L = build_layout()
    seen, walk, _ = E.reachable_report(L, START)
    print(f"placed={L.placed} trees={L.trees} sealed={L.sealed} walkable={walk} reachable={seen} skipped={len(L.skipped)}")
    for sk in L.skipped:
        if sk[0] not in ("ek_thorn_bush", "rock_outcrop_small"):
            print("  skipped", sk)
    SPEC.shape_preview(out, 4, portals=list(PORTALS) + list(LATER_PORTALS), npc=list(NPC_POSITIONS.values()), layout=L)
    print("wrote", out)
