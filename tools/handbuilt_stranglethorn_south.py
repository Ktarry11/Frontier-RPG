"""
Hand-built Southern Stranglethorn (200x180): the bottom third of the jungle, levels 38-42.

Kyle, 29 Oct 2026: "stranglethorn can be split into northern, central, southern ... One cave in each
zone ... Lots of jungle and troll flavour throughout the STV."

THE SHAPE OF THE COUNTRY.  This is the cape at the end of the continent, and it has to read as the same
jungle as the two zones above it - same canopy, same troll stonework rotting in it - but running out.
The jungle holds the top of the map and then thins: by the time the Cape Road is halfway down it the
sea is on the right of you going south-west, and by the bottom the land is headlands and sand bars
with water on two sides.  The only built thing left down here is a goblin harbour gate, and the only
reason anyone comes this far is the ruin.

    The Cape Road ......... north seam (100,3) -> south-west -> Booty Bay's gate (36,150)
    Booty Bay ............. town zone, gate (36,150).  The gate sits on a shelf above the harbour;
                            this zone owns the apron in front of it and nothing past it
    Zul'Kundaraz .......... east-centre.  The biggest troll ruin in the jungle: a terraced stone city
                            on and around a rocky shelf, courts full of vine, one road climbing in
    The Drowned Coast ..... east-south.  The sea came up and took the bottom of the ruin.  Shallow
                            water standing over cut stone, mangrove at the edges
    The Drowned Shrine .... cave (170,116), a sea cave in the drowned ruin's flank
    Bloodsail Shallows .... the south coast.  Beach, bars, three wrecks and whoever put them there
    Jaguero Spit .......... the far south-west.  A sand spit past the cape, palms, nothing else.
                            Walk out it if you want; the walk back is the same walk

HARD CONTRACTS (world/portal_manager.py):
    portals  Central Stranglethorn (100,3)   Booty Bay (36,150)   The Drowned Shrine (170,116)
    arrivals 2 tiles INTO the map off an edge portal; a cave exit lands 1 tile SOUTH of its mouth.

ART.  Nothing here waits on new art.  Ground and water are baked by tools/bake_stranglethorn.py from
the Echo Isles tropical materials; the props are the Ashenvale canopy set, the Echo Isles palms and
ruin, and the coastal set for the wrecks and the mangrove.  claude/stranglethorn_design.md carries the
prompts for the troll architecture that would improve Zul'Kundaraz and none of it is load-bearing.
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_central_barrens import BP, DP, BLD, ENT, CP  # noqa: F401

JP = "assets/tiles/echo_isles/props/"

SP = "assets/tiles/stranglethorn/props/"
#: a couple of shared sprites that Sheet C and E did not replace - the signal
#: beacon and the hulls - still live with the other coastal art.
CPD = "assets/tiles/coastal_props/"

KEY = "stranglethorn_south"
NAME = "Southern Stranglethorn"
DESC = ("The jungle thins into headlands and the sea takes the rest. A troll city stands in the vines "
        "with its feet under water.")
REGION = "Eastern Kingdoms - Stranglethorn"
BAKED_DIR = "assets/tiles/stranglethorn/baked_south"
W, H = 200, 180
IS_TOWN = False

PORTALS = {(100, 3): "Central Stranglethorn", (36, 150): "Booty Bay", (170, 116): "The Drowned Shrine"}
ARRIVALS = [(100, 5), (36, 148), (170, 117)]
START = (99, 10)

# ------------------------------------------------------------------ the plan
ROADS = {
    # the Cape Road: the Vine Road comes over the seam and takes this name for the rest of its life
    "cape":     ([(100, 2), (97, 16), (93, 32), (89, 48), (84, 64), (77, 80), (69, 95), (61, 110),
                  (52, 124), (44, 137), (37, 151)], 3.4),
    # the climb east to Zul'Kundaraz - the one way into the ruin that is not a scramble
    "kundaraz": ([(89, 48), (104, 53), (119, 58), (132, 67), (141, 77), (149, 86)], 2.8),
    # down the ruin's back into the drowned part and the sea cave
    "shrine":   ([(149, 86), (156, 96), (162, 105), (167, 113), (170, 117)], 2.4),
    # the beach track along the south coast - sand, not road
    "shallows": ([(45, 134), (56, 141), (68, 146), (81, 149), (94, 151), (105, 150)], 2.2),
    # the walk down onto the spit
    "spit":     ([(40, 144), (34, 150), (30, 155)], 2.0),
}

RIVERS = [   # (pts, hw_shallow, hw_deep)
    # the Kundaraz river: off the north-east, right across the zone, out the west coast
    ([(152, 14), (137, 26), (121, 36), (105, 44), (89, 53), (73, 60), (57, 68), (42, 74), (26, 78)],
     3.4, 1.6),
    # the ruin's own water: down the OUTSIDE of the east shelf, then in through the drowned courts.
    # It has to stay clear of the Kundaraz mesas or the rock swallows it and the river dead-ends.
    ([(190, 54), (189, 70), (188, 86), (186, 102), (182, 114), (176, 124)], 2.8, 1.2),
]
FORDS = [(86, 54, 7), (171, 116, 8)]

LAKES = {
    # standing water over cut stone - never deep, you wade the whole drowned quarter.
    # The bottom two run it down into the bay, because the bay is where the water came from.
    "drowned": [(175, 112, 15, 10, 0, 0.7), (166, 126, 12, 8, 0, 1.9), (182, 97, 8, 6, 0, 1.2),
                (160, 112, 7, 5, 0, 2.4), (171, 136, 11, 8, 0, 1.5), (178, 146, 9, 7, 0, 0.9)],
    "pools":   [(110, 100, 6, 4, 0, 1.3), (78, 136, 5, 4, 0, 0.4), (147, 139, 6, 5, 0, 2.1),
                (57, 58, 5, 4, 0, 0.8)],
}
DEEP_SHRINK = {"drowned": 9.0, "pools": 2.2}


def _seg_dist(gx, gy, x0, y0, x1, y1):
    """Distance to the segment (x0,y0)-(x1,y1).  Used to cut the Spit back out of the sea."""
    vx, vy = x1 - x0, y1 - y0
    t = np.clip(((gx - x0) * vx + (gy - y0) * vy) / (vx * vx + vy * vy), 0.0, 1.0)
    return np.hypot(gx - (x0 + t * vx), gy - (y0 + t * vy))


SPIT = (31.0, 153.0, 12.0, 171.0)       # Jaguero Spit's spine
BARS = [   # (x0, y0, x1, y1, halfwidth) - sand bars off the south coast; they stay ankle deep
    (52.0, 157.0, 75.0, 163.0, 5.0),
    (86.0, 160.0, 113.0, 162.0, 5.0),
    (121.0, 166.0, 143.0, 170.0, 4.5),
]
BAR_LEVEL = 2.4                         # sea extent clamped to this over a bar: wet, never deep


def sea(gx, gy):
    """West coast and south coast, max'd together so they meet cleanly at the south-west cape.

    >0 is water.  The west shoreline drifts east as it goes south (the land is running out), so the
    two shorelines close on each other and the corner between them is the cape.  The bulge in the
    south shoreline around x~176 is the bay that drowned the bottom of Zul'Kundaraz.

    Two things are then cut back out of the finished field.  The sand bars off the south coast clamp
    the extent to BAR_LEVEL, which is shallow but not land - that is Bloodsail Shallows, and it is why
    a wreck can sit a long way off the beach and still be walked to.  Jaguero Spit clamps to
    (distance - 1.7) instead, so its spine comes out of the water as a 3-tile ribbon of dry sand with
    the same shallow bar either side of it.
    """
    west = (24.5 + 0.052 * gy + 5.2 * np.sin(0.039 * gy + 0.6) + 2.4 * np.sin(0.101 * gy + 1.8)
            + 1.0 * np.sin(0.29 * gy)) - gx
    base = (23.0 + 4.0 * np.sin(0.030 * gx + 0.4) + 1.8 * np.sin(0.083 * gx + 1.2)
            + 0.9 * np.sin(0.24 * gx) + 23.0 * np.exp(-((gx - 176.0) / 22.0) ** 2))
    south = gy - (H - base)
    ext = np.maximum(west, south)
    for (x0, y0, x1, y1, hw) in BARS:
        d = _seg_dist(gx, gy, x0, y0, x1, y1)
        ext = np.where(d < hw, np.minimum(ext, BAR_LEVEL), ext)
    d = _seg_dist(gx, gy, *SPIT)
    return np.where(d < 7.0, np.minimum(ext, d - 1.7), ext)


ISLETS = [(14, 52, 4, 3, 0, 0.9), (11, 100, 5, 3.5, 0, 2.0), (18, 136, 4, 3, 0, 1.4),
          (62, 170, 5, 3.5, 0, 0.5), (116, 172, 4, 3, 0, 2.2), (150, 168, 4.5, 3, 0, 1.1)]

# ---- rock.  The east edge is the shoulder the ruin is built against; the rest is headland.
MESAS = [
    # Zul'Kundaraz: one rock shelf with its terraces stacked round it.  The city is the SHAPE of
    # this - the road climbs the north-west side and the courts are cut back out of it in GAPS.
    (152, 80, 21, 13, 0), (134, 76, 9, 8, -20), (147, 62, 10, 7, 0), (168, 70, 11, 9, 10),
    (176, 88, 9, 11, 0), (158, 97, 14, 9, 0), (138, 94, 8, 7, 0), (166, 108, 7, 6, 0),
    # the drowned quarter's walls, still standing out of the water
    (187, 136, 6, 5, 0), (178, 132, 5, 4, 0),
    # inland crags
    (71, 30, 6, 5, 0), (113, 78, 5, 4, 15), (126, 120, 6, 5, 0),
    # headlands on the west coast
    (32, 42, 5, 6, 0), (31, 96, 4, 7, 0), (37, 126, 5, 5, 0),
    # broken ground either side of the north seam
    (84, 12, 6, 5, 0), (119, 10, 7, 5, 0),
    # the last rock before the south beach
    (97, 140, 6, 4, 0), (136, 150, 7, 5, -10),
]
RIDGES = [
    ([(144, 60), (150, 50), (146, 38)], 2.2),
    ([(176, 40), (184, 50), (182, 62)], 2.0),
    ([(66, 100), (58, 92), (60, 80)], 2.0),
    ([(106, 112), (114, 122), (112, 134)], 2.0),
]

# ---- jungle (impassable dense growth): (cx, cy, rx, ry, rot, phase)
# Heavy across the top, patchy through the middle, nearly gone below the beach track.
WOODS = [
    # the north: still proper Stranglethorn
    (58, 22, 12, 11, 0, 0.7), (90, 26, 11, 10, 0, 2.0), (126, 24, 11, 10, 0, 1.3),
    (160, 28, 10, 9, 0, 0.5), (46, 48, 9, 10, 0, 1.9), (186, 44, 7, 10, 0, 1.6),
    # the middle: broken by the river and the two roads
    (70, 64, 10, 10, 0, 1.1), (104, 70, 10, 11, 0, 2.6), (128, 48, 9, 9, 0, 0.4),
    (52, 88, 9, 10, 0, 2.2), (88, 98, 9, 10, 0, 1.5), (176, 60, 8, 9, 0, 1.4),
    # the thinning south: smaller, scrubbier, further apart
    (66, 120, 8, 8, 0, 0.9), (98, 122, 7, 8, 0, 2.3), (132, 110, 8, 9, 0, 2.0),
    (146, 128, 7, 7, 0, 0.6), (86, 148, 6, 6, 0, 1.2),
]
BELTS = [
    ([(76, 44), (86, 38), (98, 42)], 2.6),
    ([(118, 92), (126, 100), (122, 110)], 2.4),
]
CLEARINGS = [
    (100, 3, 15, 9),           # the north seam
    (36, 150, 17, 13),         # the Booty Bay gate apron
    (152, 86, 22, 15),         # the Zul'Kundaraz courts
    (170, 116, 15, 11),        # the Drowned Shrine's mouth
    (86, 54, 12, 9),           # the Kundaraz river ford
    (61, 110, 13, 10),         # the road camp halfway down the cape
    (105, 150, 15, 11),        # the Bloodsail camp on the south beach
    (30, 155, 13, 10),         # the head of the spit
    (140, 72, 13, 10),         # the ruin's lower approach
    (119, 58, 11, 8),          # the fork on the climb
]

# painting-only patches for the baker
TRAMPLED = [(36, 150, 11, 8), (100, 3, 9, 6), (105, 150, 8, 6), (61, 110, 7, 5), (140, 72, 6, 4)]
RUIN_STONE = [(152, 84, 24, 16), (166, 68, 10, 8), (140, 94, 9, 7), (176, 112, 14, 10),
              (182, 124, 8, 6), (119, 58, 7, 5), (144, 62, 7, 5), (160, 104, 9, 7)]
ROT_PATCHES = [(172, 120, 20, 16), (150, 122, 12, 10), (158, 136, 11, 8), (144, 106, 10, 8),
               (184, 102, 10, 9)]
MANGROVE = [(170, 126, 16, 11), (24, 140, 10, 8), (28, 82, 8, 7)]

GAPS = [
    ("ell", 100, 3, 9, 7),
    ("ell", 36, 150, 10, 7),
    # the courts of Zul'Kundaraz, cut back out of the shelf: the great court, the upper court,
    # the east terrace, and the little one behind the steps that has a tree growing through it
    ("ell", 155, 86, 8, 6),
    ("ell", 145, 79, 6, 4),
    ("ell", 167, 80, 5, 4),
    ("ell", 141, 90, 5, 4),
    ("ell", 170, 116, 9, 7),
    ("ell", 140, 72, 9, 7),
    ("ell", 105, 150, 9, 7),
    ("ell", 30, 155, 9, 7),
    ("ell", 86, 54, 7, 5),
    ("ell", 61, 110, 8, 6),
    ("ell", 119, 58, 7, 5),
]

SPEC = E.Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, islets=ISLETS,
              sea=sea, mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={"north": 7}, rock_rim={"east": 6}, gaps=GAPS, fords=FORDS,
              thicket=(0.62, 10.5, 1.6))

NPC_POSITIONS = {}      # wilderness: its quests are given from Booty Bay


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {   # portal tile -> (sprite, w, h)
    (170, 116): ("ent_sea_cave", 9, 7),
}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("The Cape Road", 28, 0, 90, 164, None),
    ("Zul'Kundaraz", 124, 54, 76, 56, None),
    ("The Drowned Coast", 152, 96, 48, 84, None),
    ("Bloodsail Shallows", 40, 132, 92, 48, None),
    # the spit box stops short of x=36 on purpose: Booty Bay's gate is not on the spit
    ("Jaguero Spit", 2, 148, 32, 32, None),
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
    # the drowned quarter keeps rotted trunks instead of the lush scatter
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
    """Standing dead where the salt got into the ground - a scatter, not a graveyard."""
    import random
    rnd = random.Random(3402)
    ys, xs = np.nonzero(L.free_mask & L.dead_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = 0
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if n >= 34:
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
        if ferns < 150 and r < 0.055 and not dead:
            if L.prop("stv_fern_clump", x, y, 3, path_dir=SP, solid=False, nudge=0):
                ferns += 1
        elif bram < 56 and r < 0.064:
            if L.prop("stv_bramble", x, y, 4, path_dir=SP, solid=False, nudge=0):
                bram += 1
        elif logs < 30 and r < 0.070:
            if L.prop("stv_log_mossy", x, y, 3, path_dir=SP, solid=False, nudge=0):
                logs += 1
        elif rocks < 36 and r < 0.078:
            if L.prop("stv_boulder_mossy", x, y, 4, path_dir=SP, solid=False, nudge=0):
                rocks += 1
    L.clutter = (ferns, bram, logs, rocks)


CHEST_SPOTS = [
    (92, 14), (112, 20), (72, 20), (46, 30), (134, 36), (160, 44), (98, 40), (66, 46),
    (40, 62), (82, 70), (112, 62), (144, 50), (182, 72), (56, 78), (96, 88), (128, 86),
    (152, 90), (168, 76), (44, 108), (74, 116), (108, 132), (140, 118), (118, 148), (60, 136),
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

    # ---- the north seam: the Vine Road comes over and changes its name --------------------------------
    P("br_signpost", 104, 8, 5)
    A("stv_tree_buttress", 90, 8, 12)
    A("stv_tree_buttress", 112, 10, 12)
    J("stv_troll_idol_head", 94, 14, 8)
    A("stv_bramble", 108, 16, 5, solid=False)

    # ---- the Kundaraz ford, where the road and the river argue about who was there first -------------
    A("stv_gangplank", 86, 54, 4, solid=False, road_ok=True, shore_ok=True)
    A("stv_tide_pool", 93, 52, 3, solid=False, shore_ok=True)
    A("stv_stone_pile", 80, 58, 5)
    L.prop("stv_boulder_mossy", 91, 60, 5, path_dir=SP)
    L.prop("stv_tree_buttress", 76, 48, 11, path_dir=SP)

    # ---- the cape road: a camp halfway down, where you stop whether you meant to or not -------------
    P("br_signpost", 65, 106, 5)
    L.bld("gg_command_tent", 57, 106, 5)
    A("stv_crate_stack", 60, 110, 3)
    A("stv_driftwood", 66, 113, 4)
    L.prop("stv_troll_cookfire", 54, 112, 4, path_dir=SP)
    A("stv_troll_hide_rack", 64, 116, 4)
    L.prop("stv_bamboo", 70, 104, 8, path_dir=SP)

    # ---- the west coast on the way down: headland, mangrove, one boat nobody came back for ---------
    L.prop("stv_mangrove", 29, 84, 7, shore_ok=True, path_dir=SP)
    L.prop("stv_mangrove", 26, 90, 7, shore_ok=True, path_dir=SP)
    J("stv_tide_pool", 28, 64, 3, solid=False, shore_ok=True)
    L.prop("stv_sea_stack", 20, 50, 10, shore_ok=True, path_dir=SP)
    L.prop("stv_boat_wreck", 30, 118, 5, shore_ok=True, path_dir=SP)
    J("stv_palm_frond", 35, 112, 8)
    J("stv_palm_young", 38, 132, 9)
    J("stv_shells", 27, 138, 3, solid=False, shore_ok=True)

    # ---- Booty Bay's gate: the goblins' shelf.  Everything here faces the water ---------------------
    P("br_signpost", 42, 146, 5)
    L.prop("stv_bollard", 32, 155, 4, shore_ok=True, path_dir=SP)
    L.prop("stv_dock_lantern", 40, 153, 6, path_dir=SP)
    L.prop("stv_fish_crates", 44, 152, 4, path_dir=SP)
    L.prop("stv_fish_rack", 30, 146, 5, path_dir=SP)
    L.prop("stv_driftwood", 46, 156, 4, shore_ok=True, path_dir=SP)
    L.prop("signal_tower", 44, 140, 12, path_dir=CPD)
    J("stv_palm_young", 28, 142, 9)

    # ---- Jaguero Spit: palms and sand.  No camp, no idol, nobody ----------------------------------
    J("stv_screw_pine", 27, 158, 8, shore_ok=True)
    J("stv_palm_young", 23, 162, 9, shore_ok=True)
    J("stv_palm_frond", 19, 166, 8, shore_ok=True)
    J("stv_screw_pine", 15, 170, 8, shore_ok=True)
    L.prop("stv_driftwood", 21, 158, 4, shore_ok=True, path_dir=SP)
    J("stv_tide_pool", 25, 166, 3, solid=False, shore_ok=True)

    # ---- Bloodsail Shallows: three wrecks on the bars and a camp that uses them for timber ---------
    J("stv_wreck_hull", 72, 158, 10, shore_ok=True)
    J("stv_wreck_bow", 54, 152, 7, shore_ok=True)
    L.prop("stv_boat_wreck", 92, 158, 5, shore_ok=True, path_dir=SP)
    L.prop("stv_outrigger", 100, 155, 5, shore_ok=True, path_dir=SP)
    L.bld("gg_command_tent", 103, 148, 5)
    A("stv_crate_stack", 108, 150, 3)
    L.prop("stv_troll_cookfire", 100, 148, 4, path_dir=SP)
    L.prop("stv_arena_standard", 110, 146, 9, path_dir=SP)
    J("stv_shells", 84, 156, 3, solid=False, shore_ok=True)
    L.prop("stv_bone_arch", 120, 156, 7, shore_ok=True, path_dir=SP)
    J("stv_palm_young", 64, 148, 9)
    J("stv_palm_frond", 116, 148, 8)

    # ---- Zul'Kundaraz: the climb, then the courts.  All of it is holding up vine ------------------
    A("stv_troll_steps", 136, 73, 6, solid=False, road_ok=True)
    A("stv_troll_steps", 141, 79, 6, solid=False, road_ok=True)
    A("stv_troll_steps", 146, 84, 6, solid=False, road_ok=True)
    A("stv_troll_arch", 143, 72, 9, solid=False, road_ok=True)
    A("stv_troll_column", 146, 78, 9)
    A("stv_troll_column", 158, 79, 9)
    A("stv_troll_column", 150, 92, 9)
    A("stv_troll_ziggurat_block", 142, 88, 7)
    A("stv_troll_ziggurat_block", 162, 90, 7)
    A("stv_troll_obelisk", 156, 72, 11)
    A("stv_moss_curtain", 164, 80, 7, solid=False)
    A("stv_liana_arch", 136, 86, 7, solid=False)
    J("stv_troll_idol_head", 148, 74, 9)
    J("stv_troll_idol_head", 160, 86, 9)
    J("stv_troll_ziggurat_block", 140, 82, 8)
    J("stv_troll_ziggurat_block", 166, 94, 8)
    L.prop("stv_troll_totem", 154, 88, 7, path_dir=SP)
    L.prop("stv_arena_standard", 144, 94, 9, path_dir=SP)
    X("stv_troll_skull_fence", 150, 84, 4)
    X("stv_troll_skull_fence", 158, 94, 4)
    A("stv_mushroom_ring", 138, 90, 3, solid=False)

    # ---- the Drowned Coast: the courts the sea took, and the cave in the flank --------------------
    A("stv_troll_steps", 166, 104, 5, solid=False, shore_ok=True)
    L.prop("stv_troll_totem", 172, 110, 7, shore_ok=True, path_dir=SP)
    L.prop("stv_troll_totem", 164, 122, 7, shore_ok=True, path_dir=SP)
    J("stv_troll_ziggurat_block", 180, 116, 8, shore_ok=True)
    L.prop("stv_mangrove", 176, 128, 7, shore_ok=True, path_dir=SP)
    L.prop("stv_mangrove", 166, 132, 7, shore_ok=True, path_dir=SP)
    A("stv_dock_rail", 174, 120, 4, solid=False, shore_ok=True)
    A("stv_tide_pool", 173, 102, 3, solid=False, shore_ok=True)
    X("stv_tree_dead_giant", 184, 104, 9)
    X("stv_bramble", 178, 100, 5)
    J("stv_troll_idol_head", 168, 108, 8)
    A("stv_stone_pile", 176, 106, 6)
    L.prop("stv_coral_outcrop", 186, 130, 6, shore_ok=True, path_dir=SP)

    # ---- odd things in the jungle between the roads, so the middle is not just trees -------------
    L.prop("stv_troll_hut", 112, 100, 9, path_dir=SP)
    L.prop("stv_troll_hut", 108, 106, 9, path_dir=SP)
    J("stv_troll_ziggurat_block", 118, 64, 8)
    L.prop("stv_banana_clump", 104, 48, 6, path_dir=SP)
    L.prop("stv_hibiscus", 94, 94, 4, path_dir=SP)
    L.prop("stv_tree_buttress", 66, 76, 11, path_dir=SP)
    A("stv_mushroom_ring", 50, 96, 4, solid=False)
    A("stv_log_mossy", 122, 56, 4)
    L.prop("stv_boulder_mossy", 130, 128, 5, path_dir=SP)
    J("stv_troll_idol_head", 128, 118, 8)


def generate_zone():
    L = build_layout()
    E.register_baked(L.zone, BAKED_DIR, W, H)
    return L.zone
