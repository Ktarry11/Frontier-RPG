"""
Hand-built Rootwater Isle (180x150), levels 42-44: the reef island where the World Tree's roots meet the sea
(docs/worldtree_brief.md). The first map of the tree.

Three years ago a seed split the reef off Stranglethorn's west coast. The trunk now fills the middle of the island, so
wide that from its foot it reads as a cliff of bark; its roots run out across the island in ridges to the sea, and the
water between them is the Root Lagoons. The trolls who climbed it keep their landing at its south foot. The Bloodsail
are tapping the roots for sap on the south-east beach; the Bloodscalp come up the north-west roots after the trolls;
and in the north-east the bark has started to rot.

    The Grom'gol boat ..... the east shore pier (170,92): to and from Grom'gol
    The Zoram Strand boat . the north-west shore pier (14,46): across the sea to Ashenvale's coast
    Rootwater Landing ..... the trunk's south foot (90,76): the trolls' landing (safe), the island's quest givers
    The Root Lagoons ...... the south-west and south roots and the shallow bays between them, sap-drunk beasts
    Sapwash Beach ......... the south-east root: the Bloodsail's sap camp
    The Bloodscalp Climb .. the north-west root: the Bloodscalp war camp
    The Saproot Thicket ... the north-east root: where the bark is rotting
    The Root Stair ........ against the trunk's east side (114,42): the way up to the Lower Boughs (opened 20 Nov
                            when they're built)

Kyle, 19 Nov 2026: "Lets start building the world tree", the boat from Grom'gol, and "Let's also connect Zoram Strand
to Rootwater". Ground: ROOTWATER_SHEET in tools/bake_ashenvale.py (Kyle's sheet W1). Props and landmarks: W2, W4, W5.

HARD CONTRACTS (world/portal_manager.py)
  portals  Grom'gol (170,92) <-> its west beach (the boat); Zoram Strand (14,46) <-> its pier's T-head (the boat);
           The Lower Boughs (114,46) <-> the top of the Root Stair
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_central_barrens import _gauss
from world.chunk_paths import exists as _chunk_exists  # noqa: E402  (.webp, .jpg or .png)

BAKED_DIR = "assets/tiles/worldtree/baked_rootwater_isle"
NAME = "Rootwater Isle"
W, H = 180, 150
WTP = "assets/tiles/worldtree/props/"
SP = "assets/tiles/stranglethorn/props/"
BLD = "assets/buildings/"

PORTALS = {(170, 92): "Grom'gol", (14, 46): "Zoram Strand", (114, 46): "The Lower Boughs"}
ARRIVALS = [(167, 92), (17, 46), (114, 49)]
LATER_PORTALS = {}
START = (90, 80)       # the landing: everything must be reachable from here

#: the trunk's footprint (cx, cy, rx, ry): a cliff of bark from below
TRUNK = (90, 50, 17, 13)


def coast_r(theta):
    """The island's radius (as a fraction of its ellipse) at angle theta: bays and points."""
    return 1.0 + 0.08 * np.sin(3 * theta + 0.4) + 0.05 * np.sin(5 * theta + 1.9) + 0.03 * np.sin(9 * theta + 0.7)


#: The roots reach out into the sea as long fingers of land (cx, cy) ... (end), half-width: the island isn't a blob,
#: it's the tree's foot with its roots spread across the reef, the lagoons and bays lying between them.
ROOT_ARMS = [
    ([(80, 60), (58, 74), (38, 92), (20, 116), (10, 132)], 9.0),      # south-west, out past the lagoons
    ([(78, 44), (56, 34), (34, 30), (12, 26)], 9.5),                  # north-west, the Bloodscalp root
    ([(104, 58), (128, 76), (150, 96), (174, 112)], 9.0),             # south-east, to the beach and beyond
    ([(102, 40), (124, 28), (150, 18), (172, 10)], 8.5),              # north-east, into the rot
    ([(86, 64), (82, 96), (84, 128), (88, 146)], 8.0),                # south, the long root past the landing
    ([(70, 50), (50, 52), (28, 56), (8, 48)], 7.5),                   # west, out to the Zoram pier
    ([(108, 50), (136, 54), (162, 70), (176, 92)], 7.5),              # east, out to the Grom'gol pier
]


def _seg_dist(gx, gy, pts):
    out = np.full(np.shape(gx), 1e9)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        vx, vy = x1 - x0, y1 - y0
        t = np.clip(((gx - x0) * vx + (gy - y0) * vy) / float(vx * vx + vy * vy), 0, 1)
        out = np.minimum(out, np.hypot(gx - (x0 + t * vx), gy - (y0 + t * vy)))
    return out


def sea(gx, gy):
    """The sea round and between the roots. Extent > 0 is sea."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    dx, dy = (gx - 92.0) / 52.0, (gy - 70.0) / 42.0
    r = np.sqrt(dx * dx + dy * dy)
    th = np.arctan2(dy, dx)
    core = (r / coast_r(th) - 1.0) * 40.0
    wob = 1.4 * np.sin(0.21 * gx + 0.7) + 1.2 * np.sin(0.17 * gy + 2.1)
    arms = np.full(np.shape(gx), 99.0)
    for pts, hw in ROOT_ARMS:
        # a root narrows toward its tip
        d = _seg_dist(gx, gy, pts)
        tip = np.hypot(gx - pts[-1][0], gy - pts[-1][1])
        span = max(np.hypot(pts[-1][0] - pts[0][0], pts[-1][1] - pts[0][1]), 1.0)
        taper = 0.55 + 0.45 * np.clip(tip / span, 0, 1)
        arms = np.minimum(arms, d - hw * taper + wob)
    edge = np.maximum.reduce([3.0 - gx, gx - (W - 4.0), 3.0 - gy, gy - (H - 4.0)])
    return np.maximum(np.minimum(core, arms), edge * 3.0)


#: the two piers' points of land
ISLETS = [(168, 92, 6, 3, 0, 0.0), (16, 46, 6, 3, 0, 0.0)]

LAKES = {
    "lagoons": [(132, 64, 6, 4, 0, 0.9), (56, 62, 4, 3, 0, 2.1)],
}
DEEP_SHRINK = {"lagoons": 3.0}
RIVERS = []
FORDS = []

# ---- the trunk, and the roots running out from it to the sea as ridges of bark
MESAS = []             # the trunk is the landmark (wt_tree_foot_rising), not painted rock: rock from above read as a pit
RIDGES = []            # the roots are bark ground along the arms (CORRUPT_PATCHES), not walls: walls read as trenches

WOODS = [
    (40, 52, 10, 8, 0, 1.0), (60, 104, 8, 6, 0, 2.0), (140, 108, 9, 7, 0, 0.6), (150, 46, 10, 9, 0, 1.4),
    (110, 128, 10, 6, 0, 2.2), (26, 70, 7, 8, 0, 1.1), (126, 18, 8, 6, 0, 2.6), (60, 18, 9, 6, 0, 0.4),
]
BELTS = []
CLEARINGS = [
    (90, 78, 13, 9),            # Rootwater Landing
    (146, 72, 13, 9),           # Sapwash Beach, the Bloodsail camp
    (32, 28, 12, 8),            # the Bloodscalp war camp
    (148, 22, 12, 8),           # the Saproot Thicket's heart
    (36, 104, 9, 7),            # the lagoon shore
    (160, 92, 7, 6),            # the Grom'gol pier
    (22, 46, 7, 6),             # the Zoram pier
    (114, 48, 7, 5),            # the foot of the Root Stair
]
#: the ground of the roots near the trunk ("corrupt" -> root bark), the rot ("burned" -> rotting bark), the camps
CORRUPT_PATCHES = [(90, 52, 26, 16),                       # the bark round the trunk's foot
                   (64, 66, 12, 6), (60, 40, 12, 6), (118, 66, 12, 6), (118, 38, 12, 6),   # the roots leaving it
                   (86, 100, 6, 14), (46, 52, 12, 5), (136, 58, 12, 5),
                   (40, 86, 10, 7), (36, 30, 10, 5), (146, 86, 10, 6), (140, 24, 10, 5)]
BURNED_PATCHES = [(148, 22, 22, 12)]
BLUEBELL_PATCHES = [(70, 92, 8, 6), (112, 86, 7, 5)]
PAVED_PATCHES = [(90, 78, 8, 5)]
LUSH = 1.1
GRADE = None           # Kyle's own sheet (W1) carries the look

GAPS = [
    ("ell", 170, 92, 6, 5), ("ell", 14, 46, 6, 5), ("ell", 90, 78, 10, 7), ("ell", 114, 46, 6, 5),
]

ROADS = {
    # from the Grom'gol pier west to the landing
    "east":     ([(170, 92), (152, 92), (132, 88), (112, 84), (90, 80)], 3.2),
    # from the landing north-west round the trunk to the Zoram pier
    "zoram":    ([(90, 80), (70, 76), (54, 64), (40, 54), (24, 47), (14, 46)], 3.0),
    # south-west down to the lagoons
    "lagoons":  ([(70, 76), (60, 94), (52, 108)], 2.6),
    # up the south-east root to the Bloodsail's camp
    "beach":    ([(124, 84), (136, 76), (146, 72)], 2.6),
    # north round the trunk to the Root Stair, then out along the north-east root into the rot
    "stair":    ([(112, 84), (118, 70), (118, 56), (114, 46), (122, 34), (134, 26), (148, 22)], 2.6),
    # up the north-west root to the Bloodscalp camp
    "climb":    ([(54, 64), (48, 50), (42, 38), (32, 30)], 2.4),
}


def reef(gx, gy):
    """> 0 inside the reef that rings the island: the bays between the roots there are the Root Lagoons, shallow
    enough to wade, with a few deep holes; outside it is open sea."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    dx, dy = (gx - 92.0) / 84.0, (gy - 72.0) / 66.0
    return 1.0 - np.sqrt(dx * dx + dy * dy)


#: deep holes in the lagoons (cx, cy, r)
LAGOON_HOLES = [(44, 112, 5), (60, 132, 4), (118, 110, 4)]


class _Spec(E.Spec):
    """No woods in the sea or on the beach; the lagoons inside the reef are shallow."""

    def water_fields(self, gx, gy):
        sh, dp = super().water_fields(gx, gy)
        gx = np.asarray(gx, float)
        gy = np.asarray(gy, float)
        # the lagoons hug the roots: shallow within a ragged band of the shore and only in the bays, never a ring
        band = 11.0 + 4.0 * np.sin(0.13 * gx + 0.9) * np.cos(0.11 * gy + 0.3) + 2.5 * np.sin(0.31 * gx - 0.21 * gy)
        inside = (reef(gx, gy) > 0) & (np.asarray(sh) < band)
        hole = np.full(np.shape(gx), -99.0)
        for (cx, cy, r) in LAGOON_HOLES:
            hole = np.maximum(hole, r - np.hypot(gx - cx, gy - cy))
        dp = np.where(inside, np.minimum(dp, np.maximum(-1.0, hole)), dp)
        return sh, dp

    def woods_raw(self, gx, gy):
        out = super().woods_raw(gx, gy)
        sh, _dp = self.water_fields(gx, gy)
        return np.minimum(out, -(np.asarray(sh) + 3.0))


SPEC = _Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
             mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
             rim={}, gaps=GAPS, fords=FORDS, thicket=(0.74, 10.0, 2.3))

#: the trolls at the landing and out on the island (tools/build_rootwater_isle.py writes their records)
NPC_POSITIONS = {
    "rw_chieftain":     (90, 74),     # the landing's headwoman
    "rw_witch_doctor":  (82, 78),     # the loa's voice at the landing
    "rw_hunter":        (98, 78),     # the landing's hunter
    "rw_dockhand":      (102, 84),    # the goblin who built the lifts
    "rw_provisioner":   (80, 84),     # food and drink
    "rw_outfitter":     (96, 86),     # the landing's trader
    "rw_herbalist":     (86, 86),     # sap and herbs
    "rw_settler":       (104, 76),    # a transplant who came over on the Zoram boat
    "rw_ferryman_east": (162, 90),    # at the Grom'gol pier
    "rw_ferryman_west": (22, 44),     # at the Zoram pier
    "rw_scout_lagoons": (56, 98),     # a troll scout watching the lagoons
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("The Root Lagoons", 6, 90, 96, 58, None),
    ("Sapwash Beach", 124, 56, 54, 32, None),
    ("The Bloodscalp Climb", 6, 8, 60, 34, None),
    ("The Saproot Thicket", 118, 2, 60, 40, None),
    ("Rootwater Landing", 74, 66, 34, 24, None),
]

TREES = {
    "big":   [(SP + "stv_tree_buttress.png", 11), (SP + "stv_tree_vined.png", 10), (SP + "stv_tree_strangler.png", 11)],
    "mid":   [(SP + "stv_tree_cluster.png", 9), (WTP + "wt_palm.png", 9), (SP + "stv_tree_leaning.png", 9)],
    "small": [(SP + "stv_palm_young.png", 7), (SP + "stv_tree_fern.png", 6), (WTP + "wt_palm.png", 8)],
    "woods": [(SP + "stv_tree_buttress.png", 10), (SP + "stv_tree_vined.png", 10), (SP + "stv_tree_strangler.png", 11)],
}


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "The reef island where the World Tree's roots meet the sea. The trunk fills the middle "
                             "of it like a cliff, and the trolls who climbed it keep a landing at its foot.",
                             "Eastern Kingdoms - The World Tree", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.seal_unreachable(L, START)
    dress(L)
    E.build_free_mask(L, NPC_POSITIONS.values())
    for lm in L.z.landmarks:
        ax, ay, w, h = lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]
        L.free_mask[max(0, ay):ay + h + 1, max(0, ax - 1):ax + w + 1] = False
    E.scatter_trees(L, TREES, seed=4201, spacing=6.0, grove_keep=0.6)
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def sprinkle(L):
    """Ferns and root knuckles on the island, a few blossoms; nothing on the roads."""
    import random
    rnd = random.Random(4203)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = {"wt_ferns": 0, "wt_root_knuckle": 0, "wt_bromeliads": 0, "wt_fallen_leaf": 0}
    cap = {"wt_ferns": 26, "wt_root_knuckle": 12, "wt_bromeliads": 12, "wt_fallen_leaf": 10}
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        name = ("wt_ferns" if r < 0.012 else "wt_root_knuckle" if r < 0.020 else
                "wt_bromeliads" if r < 0.028 else "wt_fallen_leaf" if r < 0.034 else None)
        if name and n[name] < cap[name]:
            if L.prop(name, x, y, 3, path_dir=WTP, solid=False, nudge=0):
                n[name] += 1
    L.clutter = tuple(n.values())


CHEST_SPOTS = [(28, 110), (16, 130), (84, 134), (166, 104), (18, 22), (54, 24), (166, 12), (132, 30),
               (158, 60), (40, 60)]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    G = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=WTP, **kw)                      # noqa: E731
    B = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=BLD, **kw)                      # noqa: E731

    # ---- the tree: its foot (the trolls' dock under it), the loa's face on the trunk, the stair up the root
    # the trunk itself: its foot with the trolls' dock, rising out of view (the top fades: it doesn't end)
    B("wt_tree_foot_rising", 90, 68, 40, solid="core", fraction=0.35, allow_overlap=True, nudge=0, road_ok=True)
    B("wt_root_stair", 116, 44, 12, solid="core", road_ok=True, nudge=4)
    # ---- Rootwater Landing: the trolls' treehouses and platforms at the trunk's foot
    G("wt_treehouse", 78, 70, 8, solid="core", nudge=4)
    G("wt_treehouse_small", 104, 70, 6, solid="core", nudge=4)
    G("wt_cook_shelter", 80, 88, 5, solid="core", nudge=3)
    G("wt_platform_ladder", 100, 90, 5, solid="core", nudge=3)
    G("wt_hammock", 108, 80, 4, solid="core", nudge=3)
    G("wt_rope_post", 86, 90, 4, solid="core", nudge=3)
    B("gs_loa_totem", 94, 72, 5, solid="core", nudge=3)
    B("gs_lantern_post", 84, 76, 4, solid="core", nudge=3)
    B("gs_lantern_post", 98, 76, 4, solid="core", nudge=3)
    # ---- the two piers
    B("gs_lantern_post", 164, 88, 4, solid="core", nudge=3)
    G("wt_sap_barrels", 158, 96, 3, solid="core", nudge=3)
    B("gs_lantern_post", 24, 50, 4, solid="core", nudge=4)
    B("gs_crates", 24, 50, 3, solid="core", nudge=3)
    # ---- the Root Lagoons: mangrove roots standing in the water, coral and driftwood, the root arch over the path
    G("wt_mangrove_roots", 26, 98, 6, solid="core", shore_ok=True, nudge=6)
    G("wt_mangrove_roots", 70, 112, 6, solid="core", shore_ok=True, nudge=6)
    G("wt_root_coral", 20, 120, 4, solid="core", shore_ok=True, nudge=6)
    G("wt_root_driftwood", 92, 124, 3, solid="core", shore_ok=True, nudge=6)
    G("wt_root_arch", 64, 90, 8, solid="core", nudge=5)
    G("wt_mangrove_roots", 82, 140, 6, solid="core", shore_ok=True, nudge=6)
    # ---- Sapwash Beach: the Bloodsail's sap camp on the south-east root
    G("wt_pirate_tent", 144, 66, 7, solid="core", nudge=4)
    G("wt_sap_tap", 154, 70, 5, solid="core", nudge=4)
    G("wt_sap_tap", 136, 80, 5, solid="core", nudge=4)
    G("wt_sap_barrels", 150, 78, 4, solid="core", nudge=4)
    G("wt_cannon", 160, 76, 4, solid="core", nudge=4)
    G("wt_rowboat", 166, 64, 4, solid="core", shore_ok=True, nudge=6)
    G("wt_pirate_lookout", 138, 62, 7, solid="core", nudge=4)
    # ---- the Bloodscalp Climb: the war camp out on the north-west root
    G("wt_bloodscalp_tent", 26, 26, 6, solid="core", nudge=4)
    G("wt_bloodscalp_tent", 40, 30, 6, solid="core", nudge=4)
    G("wt_skull_rack", 34, 22, 5, solid="core", nudge=4)
    G("wt_war_totem", 22, 34, 6, solid="core", nudge=4)
    G("wt_skull_bonfire", 32, 30, 4, solid="core", nudge=4)
    G("wt_bamboo_cage", 46, 24, 5, solid="core", nudge=4)
    G("wt_stake_barricade", 46, 36, 4, solid="core", nudge=4)
    # ---- the Saproot Thicket: the rot along the north-east root
    G("wt_rot_fungus", 140, 18, 4, solid="core", nudge=4)
    G("wt_rot_sac", 154, 18, 5, solid="core", nudge=4)
    G("wt_dead_stub", 136, 28, 5, solid="core", nudge=4)
    G("wt_pale_mushrooms", 150, 28, 3, solid=False, nudge=4)
    G("wt_dark_sap_split", 160, 14, 5, solid="core", nudge=4)
    G("wt_rot_pit", 164, 20, 4, solid="core", nudge=4)
    # ---- the tree's own life round the island
    G("wt_sap_blister", 70, 56, 5, solid="core", nudge=4)
    G("wt_seed_pod", 116, 64, 4, solid="core", nudge=4)
    G("wt_side_branch", 70, 64, 8, solid="core", nudge=5)
    G("wt_leaf_crown", 120, 58, 6, solid="core", nudge=5)
    G("wt_blossoms", 72, 92, 3, solid=False, nudge=4)
    G("wt_blossoms", 110, 88, 3, solid=False, nudge=4)
    # ---- what's started falling out of the sky: a piece of something nobody here has seen made
    G("wt_bronze_wing", 60, 30, 4, solid="core", nudge=5)
    G("wt_crystal_shard", 66, 34, 4, solid="core", nudge=5)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and _chunk_exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_rootwater_isle():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS) + list(LATER_PORTALS),
                              npc=list(NPC_POSITIONS.values()))
