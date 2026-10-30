"""
Hand-built Central Stranglethorn (200x180): the middle third of the jungle, levels 33-37.

Kyle, 29 Oct 2026: "stranglethorn can be split into northern, central, southern ... One cave in each
zone ... Lots of jungle and troll flavour throughout the STV."

THE SHAPE OF THE COUNTRY.  This is the only STV zone with no town in it, and that is the point of it.
Northern Stranglethorn ends at a seam and this one picks the road straight up again - same jungle, same
sea on the west, same Vine Road - and carries it to the southern seam without ever offering a bed.  You
walk it or you don't get south.  Everything here hangs off that road:

    The Vine Road ........ north seam (100,3) -> south seam (100,177).  Two fords, four spurs
    Veilfall Basin ....... north-west.  A river comes off the shelf, runs west, and goes over a lip into
                           a plunge pool.  The cave mouth sits on the dry shoulder of the lip, so you
                           hear it before you see it.  Prettiest corner of the zone
    Veilfall Cave ........ cave (40,58), in the lip above the pool
    Gurbashi Flats ....... east-centre.  Trampled bare ground in otherwise solid jungle, the arena gate
                           at (150,100).  People come here to watch, so the spur off the Vine Road is a
                           proper wide road with a staging apron in front of the gate
    Gurbashi Arena ....... dungeon gate (150,100).  The interior is somebody else's zone - here it is a
                           gate, an apron and the camp that feeds it
    Mosh'Ogg Shelf ....... north-east.  Ogre country on raised broken ground.  Mesas all round it and
                           exactly one road up, which is why the ogres have kept it
    The Snapjaw Marsh .... south-west.  Brackish standing water, mangrove, rotted trunks, crocolisks

HARD CONTRACTS (world/portal_manager.py):
    portals  north seam (100,3)  south seam (100,177)  Veilfall Cave (40,58)  Gurbashi Arena (150,100)
    arrivals an edge portal lands 2 tiles INTO the map; a cave/dungeon mouth lands 1 tile SOUTH of it.

ART.  Nothing here waits on new art.  Floor, rock and water are baked by tools/bake_stranglethorn.py
from the same tropical materials the north zone uses, and the props are the Ashenvale canopy set (right
leaf shape, wrong hue - the baker's tint fixes that) plus the Echo Isles palms and idols and the coastal
troll kit.  The painting-only patch lists below (TRAMPLED, RUIN_STONE, ROT_PATCHES, MANGROVE) are read
by the baker by name; TRAMPLED is the big one here because the Flats are bare dirt.
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_central_barrens import BP, DP, BLD, ENT, CP  # noqa: F401

JP = "assets/tiles/echo_isles/props/"

SP = "assets/tiles/stranglethorn/props/"
#: a couple of shared sprites that Sheet C and E did not replace - the signal
#: beacon and the hulls - still live with the other coastal art.
CPD = "assets/tiles/coastal_props/"

KEY = "stranglethorn_central"
NAME = "Central Stranglethorn"
DESC = ("The middle of the jungle, with no town in it. The Vine Road runs through and the arena drums "
        "carry a long way east.")
REGION = "Eastern Kingdoms - Stranglethorn"
BAKED_DIR = "assets/tiles/stranglethorn/baked_central"
W, H = 200, 180
IS_TOWN = False

PORTALS = {(100, 3): "Northern Stranglethorn",
           (100, 177): "Southern Stranglethorn",
           (40, 58): "Veilfall Cave",
           (150, 100): "Gurbashi Arena"}
ARRIVALS = [(100, 5), (100, 175), (40, 59), (150, 101)]
START = (99, 10)

# ------------------------------------------------------------------ the plan
ROADS = {
    # the Vine Road: straight through, north seam to south seam, bending round the worst of the jungle
    "vine":     ([(100, 2), (98, 14), (104, 28), (108, 42), (104, 58), (96, 72), (92, 88), (96, 104),
                  (104, 118), (102, 134), (98, 150), (100, 178)], 3.4),
    # west off the Vine Road to the basin and the cave mouth
    "veilfall": ([(106, 54), (92, 58), (78, 60), (64, 60), (52, 58), (42, 58), (40, 59)], 2.6),
    # the high road: off the basin road, over the ford, along the top of the fall and back to the Vine
    "falls":    ([(70, 59), (68, 48), (72, 38), (84, 30), (101, 23)], 2.0),
    # east to the arena: the widest road in the zone, because half the jungle walks it on fight days
    "gurbashi": ([(92, 88), (108, 91), (124, 95), (138, 99), (147, 102), (150, 104)], 4.2),
    # the staging apron: a loop across the front of the gate, so a crowd can get in and out of it
    "flats":    ([(141, 102), (148, 114), (162, 108), (157, 99)], 3.4),
    # the one way up onto the Mosh'Ogg Shelf
    "shelf":    ([(104, 28), (118, 28), (132, 26), (144, 30), (158, 34), (166, 42)], 2.6),
    # south-west into the marsh - a track on fill, sinking at both ends
    "marsh":    ([(99, 146), (84, 151), (70, 156), (58, 158), (48, 156)], 2.2),
    # the coast trail: down off the basin's south lip, along the shore, into the marsh
    "coast":    ([(44, 60), (42, 74), (38, 88), (34, 102), (36, 116), (40, 130), (46, 144), (50, 156)], 2.2),
}

RIVERS = [   # (pts, hw_shallow, hw_deep)
    # the Veilfall: off the shelf's western shoulder, west across the zone, over the lip into the pool
    ([(134, 14), (124, 24), (114, 32), (102, 38), (90, 42), (78, 45), (66, 47), (54, 49), (46, 52)],
     3.2, 1.5),
    # the Snapjaw drainage: out of the central jungle, south-west, loses itself in the marsh
    ([(122, 124), (108, 132), (94, 140), (80, 148), (68, 156), (56, 162)], 2.8, 1.2),
]
FORDS = [(107, 37, 8), (68, 47, 8), (70, 156, 8)]

LAKES = {
    "plunge": [(36, 68, 10, 7, 0, 0.6)],
    "marsh":  [(44, 164, 15, 9, 0, 0.6), (28, 150, 11, 7, 0, 1.4), (66, 170, 11, 6, 0, 2.1),
               (34, 172, 9, 5, 0, 0.9)],
    "pools":  [(126, 66, 6, 4, 0, 1.1), (182, 118, 6, 5, 0, 2.0), (108, 152, 5, 4, 0, 0.7),
               (90, 110, 5, 4, 0, 1.6)],
}
DEEP_SHRINK = {"plunge": 3.4, "marsh": 4.6, "pools": 2.2}


def sea(gx, gy):
    """The west coast, continued from the north zone. >0 is water: shoreline wanders x~14 to x~26."""
    edge = 20.0 + 3.6 * np.sin(0.042 * gy + 0.7) + 1.8 * np.sin(0.107 * gy + 1.9) + 0.9 * np.sin(0.31 * gy)
    return edge - gx


ISLETS = [(13, 44, 4, 3, 0, 0.9), (11, 106, 5, 3.5, 0, 2.0)]

# ---- rock
MESAS = [
    # the Mosh'Ogg Shelf: a ring of mesas with one notch in it, which the shelf road goes through
    (152, 16, 18, 8, 0), (178, 20, 12, 10, 0), (190, 44, 10, 14, 0), (172, 56, 13, 7, 0),
    (146, 50, 11, 8, -10), (136, 34, 7, 10, 0), (160, 30, 7, 5, 15), (176, 38, 6, 5, 0),
    # the Veilfall basin walls - the river has to come over them, which is the whole idea
    (26, 52, 8, 7, 0), (22, 78, 7, 9, 0), (48, 70, 7, 6, 0), (52, 46, 6, 5, 0),
    # rock in the eastern jungle, round the Flats
    (168, 88, 7, 6, 0), (172, 116, 8, 7, 0),
    # the east edge
    (194, 80, 6, 12, 0), (190, 128, 7, 8, 0), (186, 160, 8, 7, 0),
    # broken ground either side of the south seam
    (120, 164, 8, 6, 0), (158, 170, 9, 6, 0), (82, 172, 7, 5, 0),
]
RIDGES = [
    ([(118, 60), (126, 72), (122, 84)], 2.2),
    ([(132, 110), (140, 120), (136, 132)], 2.2),
    ([(72, 100), (64, 110), (68, 122)], 2.0),
    ([(166, 70), (174, 78), (170, 90)], 2.0),
]

# ---- jungle (impassable dense growth): (cx, cy, rx, ry, rot, phase)
WOODS = [
    # the north-west: the belt between the coast and the Vine Road
    (50, 18, 10, 11, 0, 1.2), (62, 34, 9, 10, 0, 0.5), (76, 16, 11, 10, 0, 2.1), (36, 36, 8, 10, 0, 1.7),
    (88, 30, 9, 10, 0, 0.9), (118, 48, 9, 10, 0, 2.4),
    # the west-centre, downhill of the basin
    (58, 72, 9, 11, 0, 0.3), (66, 90, 8, 10, 0, 1.5), (52, 98, 8, 9, 0, 2.2), (60, 116, 9, 10, 0, 0.8),
    # the east: the solid stuff the Flats are cut out of
    (128, 78, 10, 11, 0, 1.3), (132, 122, 10, 10, 0, 0.4), (170, 78, 10, 11, 0, 2.0),
    (176, 104, 9, 10, 0, 1.1), (168, 130, 10, 10, 0, 0.6), (150, 138, 9, 10, 0, 2.5),
    (186, 92, 7, 9, 0, 1.9),
    # the south, thinning into the marsh
    (80, 128, 9, 10, 0, 1.0), (118, 146, 9, 9, 0, 2.3), (84, 160, 8, 8, 0, 0.4),
    (140, 164, 8, 7, 0, 1.6), (172, 154, 9, 8, 0, 2.1),
]
BELTS = [
    ([(78, 56), (86, 62), (94, 58)], 2.6),
    ([(110, 160), (118, 168), (112, 176)], 2.4),
]
CLEARINGS = [
    (100, 3, 14, 9),           # the north seam
    (100, 177, 15, 9),         # the south seam
    (40, 58, 14, 10),          # the cave mouth on the lip
    (36, 68, 16, 11),          # the plunge pool shore
    (68, 46, 10, 7),           # the ford on the high side
    (92, 88, 12, 9),           # the Vine Road / arena fork
    (122, 94, 10, 7),          # a stop halfway along the arena road
    (150, 100, 24, 16),        # Gurbashi Flats
    (152, 112, 16, 10),        # the staging apron
    (164, 40, 14, 10),         # the Mosh'Ogg clearing on top
    (158, 34, 10, 7),          # the shelf road's last bend
    (48, 156, 16, 11),         # the marsh landing
]

# painting-only patches for the baker
TRAMPLED = [(150, 100, 16, 11), (152, 112, 11, 7), (150, 88, 9, 6), (138, 106, 8, 5), (160, 110, 7, 5),
            (164, 40, 9, 6), (92, 88, 7, 5)]
RUIN_STONE = [(40, 58, 8, 6), (164, 40, 10, 7), (150, 100, 9, 6), (122, 94, 5, 4)]
ROT_PATCHES = [(44, 158, 24, 18), (30, 148, 13, 10), (64, 168, 12, 8)]
MANGROVE = [(44, 160, 18, 12), (28, 150, 11, 8), (66, 170, 10, 6)]

GAPS = [
    ("ell", 100, 3, 9, 7),
    ("ell", 100, 177, 9, 7),
    ("ell", 40, 58, 8, 7),
    ("ell", 68, 46, 7, 5),
    ("ell", 92, 88, 8, 6),
    ("ell", 150, 100, 12, 9),
    ("ell", 152, 112, 9, 7),
    ("ell", 164, 40, 9, 7),
    ("ell", 48, 156, 9, 7),
]

SPEC = E.Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, islets=ISLETS,
              sea=sea, mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={"east": 5, "north": 7, "south": 6}, gaps=GAPS, fords=FORDS,
              thicket=(0.60, 11.0, 1.4))

NPC_POSITIONS = {}      # wilderness: its quests come from Grom'gol in the north and Booty Bay in the south


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {   # portal tile -> (sprite, w, h)
    (40, 58): ("ent_jungle_waterfall_cave", 9, 7),
    (150, 100): ("ent_troll_skull_cave", 10, 8),
}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("The Vine Road", 66, 0, 70, 180, None),
    ("Veilfall Basin", 18, 36, 56, 56, None),
    ("Gurbashi Flats", 118, 72, 70, 60, None),
    ("Mosh'Ogg Shelf", 126, 6, 70, 58, None),
    ("The Snapjaw Marsh", 18, 128, 72, 52, None),
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
    # the marsh keeps rotted trunks instead of the lush scatter
    ys, xs = np.mgrid[0:H, 0:W]
    rot = np.zeros((H, W), bool)
    for (cx, cy, rx, ry) in ROT_PATCHES:
        rot |= np.hypot((xs - cx) / rx, (ys - cy) / ry) < 0.85
    L.dead_mask = rot
    saved = L.free_mask.copy()
    L.free_mask = saved & ~rot
    E.scatter_trees(L, TREES, seed=3401, spacing=3.8)
    L.free_mask = saved
    rot_trees(L)
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def rot_trees(L):
    """Standing dead in the marsh - a scatter, not a graveyard."""
    import random
    rnd = random.Random(3402)
    ys, xs = np.nonzero(L.free_mask & L.dead_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = 0
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if n >= 44:
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
    rnd = random.Random(3403)
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
    (34, 46), (30, 94), (36, 124), (44, 148), (60, 40), (56, 62), (72, 111), (72, 132),
    (92, 21), (84, 70), (88, 118), (92, 162), (112, 20), (114, 62), (116, 110), (122, 140),
    (130, 60), (136, 88), (142, 120), (148, 60), (156, 92), (164, 120), (171, 63), (160, 129),
]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    P = L.prop
    A = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=SP, **kw)
    X = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=SP, **kw)
    J = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=SP, **kw)
    C = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=SP, **kw)

    # ---- the north seam: the road comes out of the other zone and nobody has marked it but trolls ----
    P("br_signpost", 96, 10, 5)
    J("stv_troll_idol_head", 92, 8, 8)
    A("stv_tree_buttress", 88, 14, 12)
    A("stv_tree_buttress", 110, 12, 12)
    A("stv_bramble", 106, 8, 5, solid=False)

    # ---- the Vine Road's north ford: flat stones laid in the Veilfall, worn hollow ------------------
    A("stv_gangplank", 107, 37, 4, solid=False, road_ok=True, shore_ok=True)
    A("stv_tide_pool", 113, 34, 3, solid=False, shore_ok=True)
    A("stv_tide_pool", 100, 40, 3, solid=False, shore_ok=True)
    A("stv_stone_pile", 112, 42, 5)

    # ---- the falls spur: a ford on the high side, and a lookout the trolls got to first --------------
    A("stv_gangplank", 68, 47, 4, solid=False, road_ok=True, shore_ok=True)
    J("stv_troll_idol_head", 72, 42, 9)
    A("stv_troll_column", 66, 40, 9)
    A("stv_boulder_mossy", 74, 50, 4, solid=False)

    # ---- Veilfall Basin: the lip, the cave mouth on its dry shoulder, the pool underneath -----------
    # the water goes over at about (42,56) and the mouth sits just west of the notch, out of the spray
    A("stv_tide_pool", 40, 64, 7, solid=False, shore_ok=True)
    A("stv_tide_pool", 34, 70, 6, solid=False, shore_ok=True)
    A("stv_tide_pool", 44, 54, 3, solid=False, shore_ok=True)
    A("stv_moss_curtain", 44, 60, 8, solid=False)
    A("stv_troll_obelisk", 46, 50, 10)
    A("stv_troll_steps", 44, 62, 5, solid=False)
    A("stv_troll_steps", 42, 66, 5, solid=False)
    A("stv_mushroom_ring", 38, 62, 3, solid=False)
    A("stv_mushroom_ring", 32, 62, 4, solid=False)
    A("stv_gangplank", 30, 74, 4, shore_ok=True, solid=False)
    J("stv_troll_ziggurat_block", 50, 64, 7)
    A("stv_troll_ziggurat_block", 34, 56, 7)
    A("stv_troll_arch", 46, 58, 8, solid=False, road_ok=True)
    J("stv_palm_young", 30, 50, 9)
    J("stv_screw_pine", 26, 64, 8)
    L.prop("stv_hibiscus", 36, 54, 3, solid=False, path_dir=SP)

    # ---- the coast: the sea the north zone starts, carried on south ---------------------------------
    J("stv_wreck_bow", 24, 90, 7, shore_ok=True)
    J("stv_tide_pool", 22, 110, 3, solid=False, shore_ok=True)
    J("stv_shells", 25, 132, 3, solid=False, shore_ok=True)
    L.prop("stv_sea_stack", 18, 42, 10, shore_ok=True, path_dir=SP)
    L.prop("stv_driftwood", 27, 120, 3, solid=False, shore_ok=True, path_dir=SP)
    J("stv_palm_frond", 32, 98, 8)
    J("stv_palm_young", 30, 136, 9)

    # ---- Mosh'Ogg Shelf: the notch, then ogres.  Big crude stuff and bones, no stonework ------------
    A("stv_troll_steps", 150, 32, 5, solid=False, road_ok=True)
    A("stv_stone_pile", 142, 34, 6)
    A("stv_stone_pile", 156, 28, 6)
    L.prop("stv_troll_hut", 160, 40, 8, path_dir=SP)
    L.prop("stv_troll_hut", 170, 44, 8, path_dir=SP)
    A("stv_troll_cookfire", 164, 44, 5)
    L.prop("stv_troll_skull_pile", 158, 46, 4, path_dir=SP)
    L.prop("stv_troll_skull_pile", 170, 36, 6, path_dir=SP)
    X("stv_troll_skull_fence", 156, 42, 4)
    X("stv_troll_skull_fence", 168, 48, 4)
    A("stv_driftwood", 166, 38, 4)
    A("stv_palisade_wall", 154, 38, 5)
    L.prop("stv_boulder_mossy", 148, 24, 5, path_dir=SP)

    # ---- Gurbashi Flats: bare dirt, banners, and the gate at the top of the apron -------------------
    P("br_signpost", 120, 92, 5)
    L.bld("gg_command_tent", 126, 98, 5)
    A("stv_crate_stack", 130, 94, 3)
    L.prop("stv_arena_standard", 144, 108, 9, path_dir=SP)
    L.prop("stv_arena_standard", 158, 108, 9, path_dir=SP)
    L.prop("stv_troll_cookfire", 150, 116, 4, path_dir=SP)
    L.prop("stv_troll_hut", 140, 116, 9, path_dir=SP)
    L.prop("stv_troll_hut", 162, 116, 9, path_dir=SP)
    L.prop("stv_troll_totem", 146, 104, 7, path_dir=SP)
    L.prop("stv_troll_totem", 156, 104, 7, path_dir=SP)
    A("stv_troll_platform", 166, 114, 10)
    A("stv_palisade_wall", 136, 110, 5)
    A("stv_palisade_wall", 170, 108, 5)
    L.prop("stv_trough", 134, 104, 4, path_dir=SP)
    J("stv_troll_ziggurat_block", 158, 96, 8)
    J("stv_troll_idol_head", 142, 96, 9)
    A("stv_bramble", 164, 92, 5, solid=False)

    # ---- the arena road: a stop halfway, where the jungle gets one more crack at the crowd ----------
    A("stv_log_mossy", 118, 96, 4)
    A("stv_driftwood", 124, 98, 4)
    L.bld("bb_lean_shack", 122, 90, 6)
    A("stv_troll_hide_rack", 126, 92, 4)
    J("stv_troll_idol_head", 112, 94, 8)

    # ---- the fork: where the arena road leaves the Vine Road ----------------------------------------
    P("br_signpost", 90, 92, 5)
    A("stv_troll_steps", 88, 84, 4, solid=False)
    A("stv_tree_buttress", 86, 96, 12)
    A("stv_tree_buttress", 100, 84, 12)

    # ---- The Snapjaw Marsh: water that does not move, and what grows in it -------------------------
    L.prop("stv_mangrove", 50, 150, 7, shore_ok=True, path_dir=SP)
    L.prop("stv_mangrove", 38, 142, 7, shore_ok=True, path_dir=SP)
    L.prop("stv_mangrove", 60, 160, 7, shore_ok=True, path_dir=SP)
    L.prop("stv_mangrove", 46, 152, 8, path_dir=SP)
    L.prop("stv_mangrove", 32, 160, 8, path_dir=SP)
    L.prop("stv_lily_pads", 54, 166, 3, solid=False, shore_ok=True, path_dir=SP)
    L.prop("stv_lily_pads", 40, 170, 3, solid=False, shore_ok=True, path_dir=SP)
    A("stv_gangplank", 70, 156, 4, solid=False, road_ok=True, shore_ok=True)
    L.prop("stv_dock_rail", 48, 158, 3, solid=False, road_ok=True, shore_ok=True, path_dir=SP)
    X("stv_tree_dead_giant", 56, 146, 9)
    X("stv_tree_dead_giant", 36, 134, 9)
    X("stv_bramble", 44, 144, 5)
    L.prop("stv_boat_wreck", 58, 172, 5, shore_ok=True, path_dir=SP)
    L.prop("stv_troll_totem", 30, 166, 6, shore_ok=True, path_dir=SP)
    L.bld("gg_command_tent", 52, 154, 5)
    A("stv_troll_hide_rack", 56, 156, 4)
    A("stv_mushroom_ring", 64, 150, 4, solid=False)

    # ---- the south seam: the road goes on, and somebody keeps repainting the idol -------------------
    P("br_signpost", 104, 172, 5)
    J("stv_troll_idol_head", 94, 170, 8)
    A("stv_bramble", 108, 168, 5, solid=False)
    A("stv_tree_buttress", 90, 176, 12)
    A("stv_tree_buttress", 112, 174, 12)


def generate_zone():
    L = build_layout()
    E.register_baked(L.zone, BAKED_DIR, W, H)
    return L.zone
