"""
Hand-built Ashenvale East (220x200): the contested half - Horde lumber camps in the west, the Burning Legion's
satyr and twilight cults in the north and east, and the Demon Wastes in the south-east.

Ashenvale West and East are ONE continuous country split at x=220/x=0 (the seam road at y=100 matches).  The
corruption is NOT the whole zone (the old procedural East was one big dead dirt rect): the west third is healthy
forest and it frays into dead ground only around the three real trouble spots.  Structure (tile coords, y down):

    Greenwood Gate ...... west seam (4,100): the road continues from Ashenvale West
    Talondeep River ..... north -> south at x~65-78, fords where the seam road crosses (62,100);
                          it fills Raynewood Pool (56,132) and drains out the south rim
    Warsong Lumber Camp . Horde logging camp (42,50), a spur off the seam road
    Raynewood Retreat ... a quiet night elf retreat (30,152), a spur off the seam road
    The Crossing ........ the hub (96,104): north to the Satyrs, east to the Barrow, south to Splintertree
    Splintertree Post ... town zone, gate (110,160) on the flats; the Barrens road enters at (110,195)
    Satyr's Throne ...... rocky basin north-centre; the throne yard (135,66)
    Twilight Barrow ..... east: void crystals (180,105) / (195,130), a ring of ruined columns (186,108)
    Howling Barrows ..... cave in the north-east cliff face (200,40), reached by a canyon road from the Barrow
    The Demon Wastes .... scorched south-east; fel braziers; Grom's Rest cave (165,175) on the south road

HARD CONTRACTS (world/portal_manager.py):
    portals  West seam (4,100)  Grom's Rest (165,175)  Northern Barrens (110,195)  Howling Barrows (200,40)
             Splintertree Post (110,160)
    arrivals are 2 tiles NORTH of the portal tile; cave exits land 1 south of it.
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_central_barrens import BP, DP, BLD, ENT, CP, blob, _gauss, _smooth

BAKED_DIR = "assets/tiles/ashenvale/baked_east"
W, H = 220, 200

PORTALS = {(4, 100): "Ashenvale West", (165, 175): "Grom's Rest", (110, 195): "Northern Barrens",
           (200, 40): "Howling Barrows", (110, 160): "Splintertree Post"}
ARRIVALS = [(4, 98), (165, 176), (110, 193), (200, 41), (110, 158)]
START = (30, 102)      # a seam-road tile: everything must be reachable from here

# ------------------------------------------------------------------ the plan
ROADS = {
    # the seam road: Greenwood Gate -> river ford -> The Crossing
    "seam":      ([(3, 100), (16, 101), (30, 102), (46, 102), (58, 100), (66, 99), (80, 101), (96, 104)], 3.4),
    # spurs off the seam road, west of the river
    "lumber":    ([(30, 102), (29, 86), (31, 70), (36, 58), (42, 51)], 2.8),
    "raynewood": ([(30, 102), (26, 118), (26, 134), (29, 148), (31, 156)], 2.8),
    # The Crossing -> Splintertree (south), Barrens road (south edge)
    "south":     ([(96, 104), (98, 120), (102, 136), (106, 148), (110, 158)], 3.4),
    "barrens":   ([(110, 196), (110, 184), (112, 172), (110, 160)], 3.6),
    # The Crossing -> Satyr's Throne (north-east)
    "satyr":     ([(96, 104), (100, 90), (110, 78), (122, 71), (133, 67)], 3.0),
    # The Crossing -> Twilight Barrow (east)
    "barrow":    ([(96, 104), (112, 106), (128, 103), (144, 99), (160, 100), (174, 104), (185, 108)], 3.2),
    # the canyon road north to Howling Barrows
    "howling":   ([(185, 108), (188, 92), (192, 76), (196, 60), (199, 48), (200, 42)], 2.8),
    # Splintertree -> the Demon Wastes -> Grom's Rest
    "wastes":    ([(110, 160), (124, 164), (138, 170), (152, 176), (160, 178), (165, 177)], 3.0),
    # a rough trail linking the Wastes north to the Barrow road, round the Felmire
    "ember":     ([(140, 170), (146, 152), (148, 136), (152, 120), (158, 104)], 2.2),
    # the old logging trail: Lumber Camp east to the river
    "logtrail":  ([(42, 51), (54, 46), (66, 44)], 2.2),
}

RIVERS = [   # (pts, half-width shallow, half-width deep)
    # Talondeep River: from the north rim down into Raynewood Pool
    ([(78, 0), (75, 22), (71, 46), (68, 70), (64, 92), (62, 108), (60, 120)], 3.6, 1.7),
    # the pool's outflow, draining south under the rim
    ([(52, 143), (49, 160), (46, 176), (44, 190)], 3.2, 1.4),
]
FORDS = [(62, 100, 7), (50, 150, 4)]

LAKES = {
    "pool": [(56, 132, 15, 11, 0, 0.5)],
    "tarns": [(162, 131, 6, 4.5, 0, 0.5), (44, 35, 5, 3.8, 0, 1.4), (104, 60, 5, 4, 0, 2.0),
              (126, 130, 4, 3, 0, 1.0)],
}
DEEP_SHRINK = {"pool": 3.6, "tarns": 2.0}

# ---- rock (impassable cliffs)
MESAS = [
    # Satyr's Throne basin
    (106, 56, 6, 10, 0), (118, 44, 8, 5, 15), (148, 42, 10, 6, -10), (168, 58, 7, 10, 0), (174, 80, 6, 5, 10),
    (128, 90, 5, 4, 0), (158, 74, 5, 4, -12),
    # Twilight Barrow country
    (206, 92, 5, 10, 0), (204, 128, 6, 8, 0), (174, 88, 5, 3.5, 0), (170, 142, 6, 4, -15), (196, 100, 4, 4, 0),
    (176, 118, 4, 3, -15), (190, 124, 4, 3, 0),
    # Howling canyon walls and the cave face (cave sprite sits just under the mesa at (200,40))
    (200, 31, 16, 6, 0), (182, 68, 5, 12, -8), (212, 66, 6, 16, 0), (184, 30, 8, 7, 0),
    # Demon Wastes crags
    (150, 160, 4, 3, 0), (184, 162, 6, 4, 10), (196, 184, 6, 5, 0), (144, 188, 5, 4, 0), (176, 190, 8, 4, 0),
    (165, 166, 14, 4, 0),              # the face behind Grom's Rest
    # west bluffs
    (14, 140, 5, 8, 0), (60, 74, 4, 5, 0), (86, 130, 5, 4, 15), (12, 60, 5, 6, 0), (82, 150, 5, 4, 0),
]
RIDGES = [
    ([(118, 12), (134, 16), (150, 12)], 3.0),
    ([(160, 22), (172, 28), (184, 26)], 2.8),
    ([(130, 120), (136, 134), (132, 146)], 2.2),
    ([(92, 130), (88, 142), (92, 154)], 2.0),
    # Satyr's Throne basin walls (the road and the yard stay open: roads carve their own gaps)
    ([(102, 40), (126, 33), (152, 32)], 2.6),
    ([(180, 40), (183, 54), (179, 68)], 2.4),
    ([(102, 44), (104, 58), (102, 70)], 2.2),
    # Twilight Barrow: broken ground north-west and south of the ring
    ([(160, 92), (168, 86), (178, 84)], 2.2),
    ([(160, 138), (176, 142), (192, 140)], 2.4),
]

# ---- woods (impassable dense forest): (cx, cy, rx, ry, rot, phase)
WOODS = [
    # healthy forest, west of the river
    (20, 76, 8, 14, 0, 1.2), (46, 78, 8, 12, -8, 0.7), (22, 18, 12, 12, 0, 0.3), (56, 16, 10, 10, 0, 1.4),
    (14, 120, 6, 14, 0, 2.2), (46, 118, 6, 8, 0, 0.9), (16, 180, 12, 8, 0, 1.8), (36, 184, 10, 6, 0, 2.5),
    (60, 176, 8, 10, 0, 0.4), (70, 60, 5, 12, 0, 3.0), (10, 40, 6, 10, 0, 1.0),
    # east bank healthy forest
    (88, 30, 10, 14, 0, 0.6), (96, 66, 6, 10, 0, 1.7), (88, 124, 5, 8, 0, 0.5), (80, 160, 8, 12, 0, 2.1),
    (124, 188, 12, 6, 0, 2.6), (96, 186, 12, 8, 0, 0.8), (130, 150, 8, 8, 0, 1.3), (92, 84, 5, 6, 0, 3.1),
    (120, 124, 5, 8, 0, 2.0),
    # sparse dead forest in the corrupt lands
    (122, 22, 10, 7, 0, 1.1), (160, 40, 6, 6, 0, 0.2), (150, 100, 4, 5, 0, 1.6), (196, 150, 8, 8, 0, 2.2),
    (206, 180, 8, 12, 0, 0.9), (136, 176, 5, 6, 0, 2.8), (182, 142, 5, 5, 0, 1.9),
]
BELTS = [
    ([(4, 68), (10, 78), (14, 90)], 2.5),
]
CLEARINGS = [   # carved back out of the woods
    (4, 100, 10, 9),            # Greenwood Gate
    (96, 104, 14, 10),          # The Crossing
    (110, 160, 24, 12),         # Splintertree flats
    (110, 190, 14, 8),          # the Barrens gate
    (42, 50, 20, 13),           # Warsong Lumber Camp
    (30, 153, 16, 11),          # Raynewood Retreat
    (135, 66, 20, 14),          # Satyr's Throne yard
    (186, 108, 18, 13),         # Twilight Barrow
    (200, 44, 12, 9),           # Howling Barrows approach
    (165, 175, 16, 11),         # Grom's Rest
    (150, 176, 14, 8),          # the Wastes road camp
]
# painting-only patches for the baker (cx, cy, rx, ry)
BLUEBELL_PATCHES = [(30, 153, 12, 8), (20, 100, 12, 6), (96, 110, 8, 5)]
CORRUPT_PATCHES = [(135, 66, 26, 18), (118, 48, 11, 8), (160, 52, 10, 8),               # Satyr's Throne
                   (186, 108, 22, 17), (196, 130, 10, 8), (194, 70, 8, 12),               # Twilight Barrow
                   (168, 174, 32, 20), (150, 158, 14, 9), (190, 184, 12, 8), (142, 176, 8, 6)]  # Demon Wastes
BURNED_PATCHES = [(166, 172, 18, 12), (186, 184, 9, 6), (141, 168, 7, 5), (138, 64, 6, 5), (200, 44, 6, 5)]
PAVED_PATCHES = [(4, 100, 5, 5), (110, 159, 10, 4.5), (110, 193, 6, 3.5), (96, 104, 4, 3.5), (186, 108, 5, 4)]
MOON_POOLS = []


def satyr_field(P, wp):
    """Satyr camp earth round the throne yard (baker hook)."""
    return np.maximum(P.blob(135, 66, 15, 10, 0.8, wp), P.blob(122, 74, 7, 5, 0.8, wp)) * 0.95


GAPS = [
    ("ell", 4, 100, 8, 8),
    ("ell", 110, 195, 9, 6),
    ("ell", 110, 160, 9, 6),
    ("ell", 165, 175, 8, 6),
    ("ell", 200, 40, 7, 6),
    ("ell", 96, 104, 7, 6),
    ("ell", 42, 51, 9, 7),
    ("ell", 30, 153, 8, 7),
    ("ell", 135, 66, 10, 8),
    ("ell", 186, 108, 9, 7),
]

SPEC = E.Spec("Ashenvale East", W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK,
              mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={"north": 6, "south": 8, "west": 5}, rock_rim={"east": 5}, gaps=GAPS, fords=FORDS,
              thicket=(0.68, 10.0, 2.0))

NPC_POSITIONS = {}      # East is wilderness: its quests are given from Splintertree Post


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {   # portal tile -> (sprite, w, h)
    (200, 40): ("ent_burial_barrow", 9, 7),
    (165, 175): ("ent_fel_obsidian_cave", 9, 7),
}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("Raynewood Retreat", 6, 120, 52, 62, None),
    ("Warsong Lumber Camp", 12, 26, 66, 52, None),
    ("The Demon Wastes", 136, 148, 64, 52, None),
    ("Twilight Barrow", 158, 78, 52, 64, None),
    ("Satyr's Throne", 98, 36, 84, 66, None),
]

TREES = {
    "big": [("large_canopy_tree", 10), ("canopy_tree_cluster", 9), ("large_canopy_tree", 9)],
    "mid": [("medium_canopy_tree", 8), ("large_canopy_tree", 8), ("canopy_tree_cluster", 7)],
    "small": [("medium_canopy_tree", 6), ("medium_canopy_tree", 7)],
    "woods": [("large_canopy_tree", 9), ("canopy_tree_cluster", 8), ("large_canopy_tree", 10)],
}


def corruption(x, y):
    """0 = clean forest .. 1 = fully corrupt, from the same patches the baker paints (for tree choice)."""
    best = 0.0
    for (cx, cy, rx, ry) in CORRUPT_PATCHES:
        d = np.hypot((x - cx) / rx, (y - cy) / ry)
        best = max(best, float(np.clip(1.4 - d, 0, 1)))
    return best


def build_layout():
    AL = E.make_layout_class(SPEC, "Ashenvale East",
                             "Horde logging camps give way to satyr strongholds, twilight cults and the scorched Demon Wastes.",
                             "Kalimdor - Eastern Forest", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.seal_unreachable(L, START)
    dress(L)
    E.build_free_mask(L, NPC_POSITIONS.values())
    for lm in L.z.landmarks:
        ax, ay, w, h = lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]
        L.free_mask[max(0, ay):ay + h + 1, max(0, ax - 1):ax + w + 1] = False
    # corrupt lands keep dead trees only: stop the lush scatter where the ground is dead
    ys, xs = np.mgrid[0:H, 0:W]
    dead = np.zeros((H, W), bool)
    for (cx, cy, rx, ry) in CORRUPT_PATCHES:
        dead |= np.hypot((xs - cx) / rx, (ys - cy) / ry) < 0.85
    L.dead_mask = dead
    saved = L.free_mask.copy()
    L.free_mask = saved & ~dead
    E.scatter_trees(L, TREES, seed=2102, spacing=4.0)
    L.free_mask = saved & dead & (L.free_mask | True)
    dead_trees(L)
    L.free_mask = saved
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def dead_trees(L):
    """Sparse burned trunks across the corrupt lands (a few, not a graveyard)."""
    import random
    rnd = random.Random(404)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = 0
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if n >= 70:
            break
        if not L.free_mask[y, x]:
            continue
        if rnd.random() < 0.05:
            if L.prop("dead_corrupted_tree", x, y, rnd.choice((6, 7, 8)), path_dir=E.AP, solid="core", nudge=0):
                L.free_mask[max(0, y - 3):y + 4, max(0, x - 3):x + 4] = False
                n += 1
    L.dead_trees = n


def sprinkle(L):
    """Ground clutter on free ground: ferns in the clean forest, rock outcrops and logs everywhere - a little."""
    import random
    rnd = random.Random(78)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    ferns = logs = rocks = 0
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        dead = L.dead_mask[y, x]
        if ferns < 120 and r < 0.040 and not dead:
            if L.prop("fern_cluster", x, y, 3, path_dir=E.AP, solid=False, nudge=0):
                ferns += 1
        elif logs < 24 and r < 0.046 and not dead:
            if L.prop("fallen_log", x, y, 3, path_dir=E.AP, solid=False, nudge=0):
                logs += 1
        elif rocks < 34 and r < 0.056:
            if L.prop("rock_outcrop_small", x, y, 4, path_dir=E.AP, solid=False, nudge=0):
                rocks += 1
    L.clutter = (ferns, logs, rocks)


CHEST_SPOTS = [
    (14, 95), (24, 64), (16, 160), (40, 150), (62, 56), (78, 108), (100, 118), (116, 150), (104, 72),
    (126, 78), (140, 54), (166, 70), (150, 108), (178, 98), (196, 116), (190, 56), (192, 40),
    (146, 168), (176, 180), (122, 180),
]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    P = L.prop
    A = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=E.AP, **kw)
    X = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=E.XP, **kw)

    # ---- Greenwood Gate: the ruined elven arch the seam road passes under (west seam) -----------------------
    P("ent_elven_ruin_arch", 12, 104, 8, path_dir=ENT, solid=False, road_ok=True)
    A("large_canopy_tree", 10, 94, 11)
    A("large_canopy_tree", 11, 112, 11)
    P("br_signpost", 18, 106, 5)

    # ---- The Crossing: the hub - a ranger waystation, signposts, the fork stones ------------------------------
    P("br_signpost", 100, 109, 5)
    L.bld("generic_tent_a", 90, 100, 4)
    L.dp("vot_fire_pit", 91, 107, 2, solid=False)
    L.dp("vot_crate_stack", 87, 103, 3)

    # ---- Warsong Lumber Camp: a Horde logging camp in a stump-field clearing ---------------------------------
    L.bld("frontier_barracks", 50, 47, 9)
    L.bld("generic_tent_b", 36, 45, 4)
    L.bld("generic_tent_a", 34, 54, 4)
    L.bld("hide_tanners_hut", 48, 57, 5)
    L.bld("watchtower", 52, 57, 9)
    P("br_caravan_wagon", 40, 59, 4)
    for (lx, ly) in ((44, 44), (47, 52), (37, 50), (55, 52)):
        A("fallen_log", lx, ly, 3, solid=False)
    L.dp("vot_war_banner", 43, 48, 5)
    L.dp("vot_fire_pit", 41, 52, 2, solid=False)
    L.dp("vot_crate_stack", 39, 56, 3)
    L.dp("weapon_rack", 56, 45, 3)
    P("br_signpost", 46, 61, 5)

    # ---- Raynewood Retreat: a quiet night elf retreat, ring of ancient trees --------------------------------
    import math
    for k in range(7):
        ang = k * 2 * math.pi / 7 + 0.5
        A("large_canopy_tree", int(round(30 + 12.5 * math.cos(ang))), int(round(153 + 9.0 * math.sin(ang))),
          12 if k % 2 == 0 else 11)
    L.bld("nightelf_house_small", 25, 151, 7)
    L.bld("nightelf_house_small", 35, 150, 7)
    L.bld("druid_priestess_hut", 30, 146, 7)
    L.dp("vot_fire_pit", 30, 156, 2, solid=False)
    A("ash_elune_statue", 30, 160, 7)
    A("ash_moon_lantern", 23, 156, 6, solid="core")
    A("ash_moon_lantern", 37, 156, 6, solid="core")
    A("ash_living_gate_arch", 28, 141, 8, solid=False, road_ok=True)
    A("ash_glow_mushroom_ring", 21, 150, 3, solid=False)
    A("ash_foxglove_patch", 39, 153, 3, solid=False)
    A("fern_cluster", 23, 157, 3, solid=False)
    A("fern_cluster", 37, 157, 3, solid=False)
    A("fallen_log", 22, 146, 3, solid=False)
    P("br_signpost", 31, 162, 5)

    # ---- Splintertree Post gate (the post itself is its own zone south of this clearing) -----------------------
    L.bld("watchtower", 101, 157, 10)
    L.bld("watchtower", 121, 157, 10)
    L.dp("vot_war_banner", 107, 156, 5)
    L.dp("vot_war_banner", 113, 156, 5)
    P("br_signpost", 114, 166, 5)
    A("large_canopy_tree", 96, 152, 11)
    A("large_canopy_tree", 128, 153, 11)

    # ---- the Barrens road: south gate -------------------------------------------------------------------------
    P("br_kodo_tusk_gate", 110, 189, 7, solid=False, road_ok=True)
    P("br_signpost", 116, 186, 5)
    A("rock_outcrop_large", 104, 190, 5)

    # ---- Satyr's Throne: a ritual yard under the basin wall ---------------------------------------------------
    X("satyr_throne", 135, 64, 8)
    for (tx, ty) in ((126, 62), (144, 63), (130, 74), (141, 74)):
        L.dp("rf_cult_banner", tx, ty, 5)
    for (tx, ty) in ((122, 58), (150, 60)):
        X("twisted_dead_tree_cluster", tx, ty, 6, solid=False)
    L.dp("rf_obsidian_spikes", 133, 72, 3)
    L.dp("rf_sacrificial_altar", 125, 70, 4)
    L.dp("bbc_fel_brazier", 138, 70, 4, solid=False)
    L.dp("bbc_fel_brazier", 131, 61, 4, solid=False)
    L.dp("skull_pile", 148, 70, 2)
    # a smaller satyr camp up the western wall
    X("ashx_satyr_tent", 113, 70, 7)
    X("ashx_skull_fence", 128, 77, 4)
    X("ashx_skull_fence", 142, 78, 4)
    L.dp("bbc_fel_bonfire", 109, 68, 2, solid=False)

    # ---- Twilight Barrow: a ring of ruined columns round a void-crystal altar ---------------------------------
    for k in range(8):
        ang = k * 2 * math.pi / 8 + 0.2
        L.dp("temple_column" if k % 2 == 0 else "broken_column", int(round(186 + 11.0 * math.cos(ang))),
             int(round(108 + 8.0 * math.sin(ang))), 5 if k % 2 == 0 else 3)
    L.dp("twilight_altar", 186, 106, 4)
    X("void_crystal_formation", 180, 105, 5)
    X("void_crystal_formation", 195, 130, 5)
    L.dp("rf_void_crystals", 192, 98, 3)
    L.dp("sarcophagus", 178, 114, 3)
    L.dp("ritual_circle", 190, 114, 3, solid=False)
    X("ashx_twilight_stone", 174, 103, 6)
    X("ashx_twilight_stone", 198, 111, 6)
    X("ashx_corrupt_moonwell", 188, 120, 5)
    X("ashx_obsidian_spires", 196, 98, 6)

    # ---- Howling Barrows: the furbolg burial cave and its totems -----------------------------------------------
    A("furbolg_totem", 193, 44, 6, solid="core")
    A("furbolg_totem", 207, 44, 6, solid="core")
    L.dp("vot_beast_ribcage", 195, 50, 3)
    L.dp("skull_pile", 205, 49, 2)
    P("br_signpost", 197, 52, 5)
    A("dead_corrupted_tree", 189, 54, 7)
    X("ashx_howling_standard", 196, 47, 7)
    X("ashx_ice_stalagmites", 191, 47, 4)
    X("ashx_ice_stalagmites", 209, 48, 4)
    X("ashx_icicle_pillar", 206, 54, 5)

    # ---- The Demon Wastes: fel fire and wreckage -------------------------------------------------------------------
    for (bx, by) in ((150, 168), (160, 181), (174, 184), (180, 172)):
        X("fel_fire_brazier", bx, by, 5, solid=False)
    L.dp("vot_fel_crystals", 172, 168, 4)
    L.dp("vot_fel_crystals", 188, 178, 3)
    L.dp("rf_lava_fissure", 178, 178, 3, solid=False)
    L.dp("rf_skull_spears", 148, 183, 3)
    L.dp("bbc_skull_pile", 158, 187, 2)
    L.dp("rf_fallen_pillar", 146, 174, 3)
    X("ashx_demon_gate", 150, 178, 9, solid=False, road_ok=True)
    X("ashx_charred_trunks", 144, 162, 6)
    X("ashx_charred_trunks", 174, 187, 6)
    X("ashx_demon_ribcage", 156, 186, 4)
    X("ashx_burned_caravan", 142, 167, 5)
    X("ashx_burned_treehouse", 187, 167, 9)
    X("ashx_obsidian_spires", 190, 176, 6)
    X("ashx_obsidian_spires", 144, 182, 5)
    X("ashx_demon_skull_altar", 172, 184, 6)
    X("ashx_orc_hero_tomb", 182, 182, 4)
    X("ashx_nightmare_thorns", 156, 170, 3, solid=False)
    X("ashx_nightmare_thorns", 175, 172, 3, solid=False)
    # Grom's Rest: Hellscream's memorial pillars flank the road to the cave
    L.dp("temple_column", 156, 178, 5)
    L.dp("temple_column", 174, 178, 5)
    X("ashx_orc_memorial", 160, 175, 6)
    X("ashx_shattered_orc_statue", 171, 175, 7)
    P("br_signpost", 160, 182, 5)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_ashenvale_east():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/ae_shape.png"
    if len(sys.argv) > 2 and sys.argv[2] == "build":
        import time
        t = time.time()
        L = build_layout()
        seen, walk, _ = E.reachable_report(L, START)
        print(f"built {time.time()-t:.1f}s  placed={L.placed} trees={L.trees} scattered={L.scattered} "
              f"woods_deco={L.woods_deco} landmarks={len(L.z.landmarks)} sealed={L.sealed} "
              f"clutter={L.clutter} dead={L.dead_trees} walkable={walk} reachable={seen} skipped={len(L.skipped)}")
        for sk in L.skipped:
            if sk[0] not in ("fallen_log", "rock_outcrop_small", "fern_cluster"):
                print("  skipped", sk)
        SPEC.shape_preview(out, 4, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()), layout=L)
    else:
        SPEC.shape_preview(out, 4, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
    print("wrote", out)
