"""
Hand-built Northern Stranglethorn (200x180): the top third of the jungle, levels 30-34.

Kyle, 29 Oct 2026: "stranglethorn can be split into northern, central, southern. Northern will be
level 30-34 ... One cave in each zone ... Lots of jungle and troll flavour throughout the STV."

THE SHAPE OF THE COUNTRY.  Stranglethorn is NOT reachable overland - claude/integration_geography.md
settled that ("the land route from the Barrens south is gone"), so the north edge of this zone is the
range itself: solid rock, no gate, nothing beyond it.  You arrive by zeppelin into Grom'gol and you
leave south.  That makes the geography read the right way round: the only two doors into the whole
jungle are a Horde airship berth at the top and a goblin harbour at the bottom, and the three zones
between them are the only road.

    Grom'gol ............. town zone, gate (54,96).  Orcish base camp, the zeppelin berth is inside it
    The Vine Road ........ Grom'gol -> south seam (100,177) -> Central Stranglethorn
    Marosh River ......... off the north range, runs south-west into the sea; ONE ford, on the coast trail
    Mistvale Lagoon ...... brackish inland water south-west of Grom'gol, mangrove country
    Zul'Marosh Steps ..... a troll stair-temple built up the side of a crag, north-east
    Rotvine Hollow ....... cave (150,40), in the crag face above the Steps
    Rotvine Fen .......... the rotting east, downhill of the Hollow's outflow

HARD CONTRACTS (world/portal_manager.py):
    portals  Grom'gol (54,96)   Rotvine Hollow (150,40)   Central Stranglethorn (100,177)
    arrivals 2 tiles NORTH of an edge portal; a cave exit lands 1 tile SOUTH of its mouth.

ART.  Nothing here waits on new art.  The jungle floor, rock and water are baked by
tools/bake_stranglethorn.py from the Echo Isles tropical materials; the props are the Ashenvale canopy
set (correct leaf shape, wrong hue - the baker's tint handles that) plus the Echo Isles palms, idol and
overgrown ruin.  claude/stranglethorn_design.md carries the four prompts for the art that WOULD improve
this (troll architecture above all) and none of it is load-bearing.
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_central_barrens import BP, DP, BLD, ENT, CP  # noqa: F401

JP = "assets/tiles/echo_isles/props/"

SP = "assets/tiles/stranglethorn/props/"
#: a couple of shared sprites that Sheet C and E did not replace - the signal
#: beacon and the hulls - still live with the other coastal art.
CPD = "assets/tiles/coastal_props/"

KEY = "stranglethorn_north"
NAME = "Northern Stranglethorn"
DESC = ("Jungle so thick the light arrives green. Troll stonework rots in the vines, and the only road "
        "runs south.")
REGION = "Eastern Kingdoms - Stranglethorn"
BAKED_DIR = "assets/tiles/stranglethorn/baked_north"
W, H = 200, 180
IS_TOWN = False

PORTALS = {(54, 96): "Grom'gol", (150, 40): "Rotvine Hollow", (100, 177): "Central Stranglethorn"}
ARRIVALS = [(54, 94), (150, 41), (100, 175)]
START = (54, 100)

# ------------------------------------------------------------------ the plan
ROADS = {
    # the Vine Road: Grom'gol's gate, south-east through the jungle, out the south seam
    "vine":     ([(54, 95), (58, 106), (64, 118), (74, 131), (86, 145), (95, 159), (100, 178)], 3.4),
    # east off the gate: the only cut line across the middle of the zone
    "cutline":  ([(54, 96), (70, 93), (86, 90), (102, 89), (116, 90)], 3.0),
    # up to the Steps and the Hollow above them
    "steps":    ([(116, 90), (126, 78), (134, 64), (141, 52), (148, 42)], 2.8),
    # east into the fen - a rotting causeway, barely a road
    "fen":      ([(116, 90), (132, 97), (148, 105), (162, 113), (172, 122)], 2.2),
    # the coast trail north out of Grom'gol, over the Marosh ford
    "coast":    ([(54, 96), (44, 87), (37, 74), (33, 60), (31, 47), (32, 34)], 2.4),
    # the lagoon spur: south-west off the Vine Road to the mangroves
    "lagoon":   ([(60, 110), (52, 120), (44, 128), (38, 137)], 2.0),
}

RIVERS = [   # (pts, hw_shallow, hw_deep)
    # the Marosh: off the range, south-west, into the sea north of Grom'gol
    ([(152, 8), (142, 22), (130, 34), (116, 44), (102, 52), (86, 58), (68, 62), (50, 65), (34, 68), (18, 70)],
     3.4, 1.6),
    # the Hollow's outflow, east into the fen
    ([(152, 46), (158, 60), (164, 76), (168, 94), (170, 110)], 2.8, 1.2),
]
FORDS = [(34, 68, 7)]

LAKES = {
    "lagoon": [(42, 136, 15, 10, 0, 0.6)],
    "pools":  [(166, 130, 7, 5, 0, 1.3), (176, 148, 6, 4.5, -10, 0.4), (120, 150, 5, 4, 0, 2.1),
               (88, 36, 5, 4, 0, 0.8)],
}
DEEP_SHRINK = {"lagoon": 3.8, "pools": 2.2}


def sea(gx, gy):
    """The west coast. >0 is water: the shoreline wanders between x~13 and x~24."""
    edge = 18.0 + 5.0 * np.sin(0.042 * gy + 0.7) + 2.4 * np.sin(0.107 * gy + 1.9) + 1.1 * np.sin(0.31 * gy)
    return edge - gx


ISLETS = [(11, 58, 4, 3, 0, 0.9), (9, 122, 5, 3.5, 0, 2.0)]

# ---- rock.  The north edge IS the range: there is no gate in it anywhere.
MESAS = [
    # the Zul'Marosh crag - the Steps climb it and the Hollow is in its face
    (150, 30, 18, 9, 0), (134, 44, 7, 6, -15), (164, 44, 8, 7, 10), (158, 22, 9, 8, 0),
    # inland crags along the cutline
    (96, 68, 6, 5, 0), (112, 62, 5, 4, 15), (78, 74, 5, 4, 0),
    # the fen's eastern shoulder
    (188, 100, 6, 14, 0), (184, 134, 7, 6, 0), (190, 160, 8, 7, 0), (176, 168, 6, 4, -10),
    # headlands on the coast
    (24, 24, 5, 6, 0), (22, 108, 4, 7, 0), (26, 162, 6, 5, 0),
    # broken ground either side of the south seam
    (82, 170, 6, 5, 0), (120, 172, 7, 5, 0),
]
RIDGES = [
    ([(96, 110), (104, 122), (100, 136)], 2.2),
    ([(140, 140), (148, 152), (144, 166)], 2.2),
    ([(62, 150), (54, 160), (56, 172)], 2.0),
    ([(132, 108), (140, 118), (152, 120)], 2.0),
]

# ---- jungle (impassable dense growth): (cx, cy, rx, ry, rot, phase)
WOODS = [
    # the belt between the Vine Road and the coast
    (36, 22, 10, 12, 0, 1.2), (40, 50, 9, 11, 0, 0.4), (44, 104, 8, 10, 0, 2.3), (34, 156, 9, 9, 0, 1.6),
    # the middle jungle, either side of the cutline
    (70, 30, 12, 11, 0, 0.7), (96, 24, 11, 10, 0, 2.0), (74, 110, 10, 12, 0, 1.1), (92, 128, 9, 10, 0, 0.3),
    (112, 112, 9, 11, 0, 2.6), (64, 134, 8, 8, 0, 1.9), (116, 136, 8, 9, 0, 0.9),
    # the east: older, wetter, meaner
    (138, 82, 10, 10, 0, 1.4), (158, 92, 8, 9, 0, 0.2), (150, 128, 9, 10, 0, 2.2), (170, 60, 9, 11, 0, 1.7),
    (132, 158, 10, 8, 0, 0.6), (166, 160, 9, 8, 0, 2.4), (182, 76, 7, 9, 0, 1.0),
]
BELTS = [
    ([(60, 76), (70, 80), (82, 78)], 2.6),
    ([(104, 148), (112, 158), (108, 170)], 2.4),
]
CLEARINGS = [
    (54, 96, 16, 12),          # the Grom'gol gate apron
    (100, 177, 15, 9),         # the south seam
    (148, 42, 13, 10),         # the Hollow's mouth
    (134, 60, 18, 12),         # the Steps' lower court
    (116, 90, 13, 10),         # the cutline fork
    (42, 136, 20, 13),         # Mistvale Lagoon shore
    (172, 122, 14, 10),        # the fen landing
    (32, 34, 11, 9),           # the coast trail's north end
    (86, 90, 10, 7),           # a cutline camp
]

# painting-only patches for the baker
TRAMPLED = [(54, 96, 10, 7), (116, 90, 7, 5), (148, 42, 7, 5), (172, 122, 7, 5), (86, 90, 6, 4)]
RUIN_STONE = [(134, 60, 14, 9), (150, 50, 6, 4), (120, 86, 5, 4)]
ROT_PATCHES = [(170, 124, 26, 22), (164, 150, 14, 11), (178, 108, 10, 9), (42, 138, 14, 9)]
MANGROVE = [(42, 136, 18, 12), (30, 150, 9, 7)]

GAPS = [
    ("ell", 54, 96, 9, 7),
    ("ell", 100, 177, 9, 7),
    ("ell", 150, 40, 7, 6),
    ("ell", 116, 90, 7, 6),
    ("ell", 134, 60, 9, 7),
    ("ell", 42, 136, 9, 7),
    ("ell", 172, 122, 8, 6),
    ("ell", 32, 34, 7, 6),
]

SPEC = E.Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, islets=ISLETS,
              sea=sea, mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={"east": 5, "south": 6}, rock_rim={"north": 9}, gaps=GAPS, fords=FORDS,
              thicket=(0.60, 11.0, 1.4))

NPC_POSITIONS = {}      # wilderness: its quests are given from Grom'gol


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {   # portal tile -> (sprite, w, h)
    (150, 40): ("ent_mangrove_cave", 9, 7),
}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("The Vine Road", 44, 86, 70, 94, None),
    ("Mistvale Lagoon", 18, 112, 54, 68, None),
    ("Zul'Marosh Steps", 108, 36, 62, 56, None),
    ("Rotvine Fen", 140, 98, 60, 82, None),
    ("The Green Cut", 60, 60, 66, 40, None),
]

TREES = {
    "big":   [(SP + "stv_tree_buttress.png", 11), (SP + "stv_tree_vined.png", 10), (SP + "stv_tree_buttress.png", 10)],
    "mid":   [(SP + "stv_tree_cluster.png", 9), (SP + "stv_palm_young.png", 9), (SP + "stv_tree_vined.png", 8)],
    "small": [(SP + "stv_tree_cluster.png", 7), (SP + "stv_palm_frond.png", 7), (SP + "stv_screw_pine.png", 7)],
    "woods": [(SP + "stv_tree_buttress.png", 10), (SP + "stv_tree_vined.png", 9), (SP + "stv_tree_buttress.png", 11)],
}


def build_layout():
    AL = E.make_layout_class(SPEC, NAME, DESC, REGION, PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.seal_unreachable(L, START)
    dress(L)
    E.build_free_mask(L, NPC_POSITIONS.values())
    for lm in L.z.landmarks:
        ax, ay, w, h = lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]
        L.free_mask[max(0, ay):ay + h + 1, max(0, ax - 1):ax + w + 1] = False
    # the fen keeps rotted trunks instead of the lush scatter
    ys, xs = np.mgrid[0:H, 0:W]
    rot = np.zeros((H, W), bool)
    for (cx, cy, rx, ry) in ROT_PATCHES:
        rot |= np.hypot((xs - cx) / rx, (ys - cy) / ry) < 0.85
    L.dead_mask = rot
    saved = L.free_mask.copy()
    L.free_mask = saved & ~rot
    E.scatter_trees(L, TREES, seed=3301, spacing=3.8)
    L.free_mask = saved
    rot_trees(L)
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def rot_trees(L):
    """Standing dead in the fen - a scatter, not a graveyard."""
    import random
    rnd = random.Random(3302)
    ys, xs = np.nonzero(L.free_mask & L.dead_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = 0
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if n >= 48:
            break
        if not L.free_mask[y, x]:
            continue
        if L.prop("stv_tree_dead_giant", x, y, rnd.choice((6, 7, 8)), path_dir=SP, solid="core", nudge=0):
            L.free_mask[max(0, y - 3):y + 4, max(0, x - 3):x + 4] = False
            n += 1
    L.rot_trees = n


def sprinkle(L):
    """Jungle floor clutter: ferns everywhere, bramble in the thickets, rock and logs a little."""
    import random
    rnd = random.Random(3303)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    ferns = logs = rocks = bram = 0
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        dead = L.dead_mask[y, x]
        if ferns < 190 and r < 0.055 and not dead:
            if L.prop("stv_fern_clump", x, y, 3, path_dir=SP, solid=False, nudge=0):
                ferns += 1
        elif bram < 70 and r < 0.064:
            if L.prop("stv_bramble", x, y, 4, path_dir=SP, solid=False, nudge=0):
                bram += 1
        elif logs < 36 and r < 0.070:
            if L.prop("stv_log_mossy", x, y, 3, path_dir=SP, solid=False, nudge=0):
                logs += 1
        elif rocks < 40 and r < 0.078:
            if L.prop("stv_boulder_mossy", x, y, 4, path_dir=SP, solid=False, nudge=0):
                rocks += 1
    L.clutter = (ferns, bram, logs, rocks)


CHEST_SPOTS = [
    (30, 40), (28, 80), (34, 118), (30, 168), (48, 60), (62, 36), (66, 100), (58, 128),
    (80, 56), (88, 104), (94, 150), (106, 76), (112, 100), (124, 70), (130, 128), (140, 54),
    (146, 96), (156, 118), (166, 140), (174, 86), (180, 128), (118, 164), (74, 166), (44, 150),
]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    P = L.prop
    A = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=SP, **kw)
    X = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=SP, **kw)
    J = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=SP, **kw)

    # ---- the Grom'gol gate apron: the road out of the camp, orc marks on it -------------------------
    P("br_signpost", 60, 100, 5)
    A("stv_trophy_pole", 48, 92, 8)
    A("stv_palisade_wall", 50, 90, 5)
    A("stv_palisade_wall", 58, 90, 5)
    A("stv_driftwood", 62, 93, 4)
    A("stv_tree_buttress", 46, 104, 12)
    A("stv_tree_buttress", 64, 108, 12)

    # ---- the coast trail: the Marosh ford, and a wrecked skiff on the beach ------------------------
    A("stv_gangplank", 34, 68, 4, solid=False, road_ok=True, shore_ok=True)
    A("stv_tide_pool", 40, 67, 3, solid=False, shore_ok=True)
    J("stv_wreck_bow", 22, 54, 7, shore_ok=True)
    J("stv_palm_frond", 26, 46, 8)
    J("stv_palm_young", 29, 38, 9)
    A("stv_stone_pile", 36, 44, 5)
    J("stv_tide_pool", 20, 96, 3, solid=False, shore_ok=True)
    J("stv_shells", 23, 130, 3, solid=False, shore_ok=True)
    J("stv_wreck_hull", 24, 164, 9, shore_ok=True)

    # ---- Mistvale Lagoon: mangrove water, a troll fishing camp gone to rot ------------------------
    J("stv_palm_young", 36, 126, 9)
    J("stv_palm_young", 52, 142, 9)
    J("stv_screw_pine", 32, 144, 8)
    A("stv_gangplank", 46, 130, 4, shore_ok=True, solid=False)
    A("stv_troll_hide_rack", 50, 134, 4)
    A("stv_frond_litter", 38, 148, 3)
    J("stv_troll_ziggurat_block", 30, 138, 7)
    A("stv_mushroom_ring", 44, 146, 3, solid=False)
    A("stv_mushroom_ring", 56, 152, 4, solid=False)

    # ---- the Green Cut: the cutline fork, a woodcutters' stop that the jungle is taking back -------
    P("br_signpost", 112, 94, 5)
    A("stv_log_mossy", 104, 92, 4)
    A("stv_troll_post", 100, 94, 4)
    A("stv_driftwood", 96, 92, 4)
    L.bld("gg_command_tent", 88, 88, 5)
    A("stv_crate_stack", 84, 92, 3)
    A("stv_troll_steps", 120, 86, 4, solid=False)

    # ---- Zul'Marosh Steps: the stair-temple up the crag face -------------------------------------
    A("stv_troll_steps", 134, 58, 6, solid=False, road_ok=True)
    A("stv_troll_steps", 136, 53, 6, solid=False, road_ok=True)
    A("stv_troll_steps", 139, 48, 6, solid=False, road_ok=True)
    J("stv_troll_idol_head", 128, 62, 9)
    J("stv_troll_idol_head", 142, 64, 9)
    A("stv_troll_column", 130, 56, 9)
    A("stv_troll_column", 140, 57, 9)
    A("stv_troll_ziggurat_block", 126, 68, 7)
    A("stv_troll_obelisk", 146, 56, 10)
    A("stv_troll_arch", 134, 66, 8, solid=False, road_ok=True)
    J("stv_troll_ziggurat_block", 120, 72, 8)
    J("stv_troll_ziggurat_block", 148, 70, 8)
    A("stv_moss_curtain", 144, 46, 7, solid=False)
    X("stv_troll_skull_fence", 130, 50, 4)
    X("stv_troll_skull_fence", 138, 44, 4)

    # ---- Rotvine Hollow's mouth: the outflow comes out below it ----------------------------------
    A("stv_liana_arch", 154, 44, 7, solid=False)
    A("stv_mushroom_ring", 146, 46, 3, solid=False)
    A("stv_stone_pile", 158, 50, 6)

    # ---- Rotvine Fen: the causeway, the standing water, the smell -------------------------------
    A("stv_tide_pool", 160, 108, 3, solid=False, shore_ok=True)
    A("stv_gangplank", 166, 118, 4, solid=False, road_ok=True, shore_ok=True)
    X("stv_tree_dead_giant", 174, 130, 9)
    X("stv_tree_dead_giant", 164, 144, 9)
    X("stv_bramble", 170, 136, 5)
    X("stv_bramble", 180, 120, 5)
    A("stv_mushroom_ring", 176, 142, 4, solid=False)
    J("stv_troll_idol_head", 172, 118, 8)
    L.bld("gg_command_tent", 176, 124, 5)
    A("stv_troll_hide_rack", 180, 126, 4)

    # ---- the south seam: the Vine Road leaves, and somebody marked it ---------------------------
    P("br_signpost", 96, 172, 5)
    J("stv_troll_idol_head", 92, 168, 8)
    A("stv_bramble", 106, 170, 5, solid=False)
    A("stv_tree_buttress", 88, 174, 12)
    A("stv_tree_buttress", 112, 176, 12)


def generate_zone():
    L = build_layout()
    E.register_baked(L.zone, BAKED_DIR, W, H)
    return L.zone
