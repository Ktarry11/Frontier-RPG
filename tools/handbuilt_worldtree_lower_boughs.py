"""
Hand-built Lower Boughs (180x150), levels 44-45: the World Tree's first lived-on tier (docs/worldtree_brief.md).

You come up the Root Stair from Rootwater Isle and step out onto the trunk's ledge. The trunk is a wall of bark along the
whole north edge, too big to see round; three great boughs run south from it over the drop, each as wide as a road,
and far below them is the jungle canopy in a green haze. The trolls' first village, Mossroof, sits where the Great Bough
leaves the trunk: moss-roofed treehouses on platforms, ladders and lanterns. A river runs down the Great Bough in a
channel worn in its bark and falls off its tip. The apes have the west bough, the spiders the east, and the Bloodscalp
come up over the far end of the Great Bough on ropes from the jungle below.

    The Root Stair ........ the ledge's west end (40,16): down to Rootwater Isle
    The Knothollow ........ a great knot in the trunk off the ledge (62,16): the cave into the wood
    The Great Lift ........ the ledge's east end (130,16): up to the Great Settlement (opens when it's built)
    Mossroof .............. the trolls' village at the foot of the Great Bough (safe)
    The Trunk Ledge ....... the ledge along the trunk's foot
    The Greenwater Bough .. the Great Bough and its river
    The Howling Bough ..... the west bough, the sap-drunk apes
    The Silkwood .......... the east bough, webbed over by canopy spiders
    The Climbers' Cut ..... the Great Bough's far end, where the Bloodscalp come up on ropes

THE DROP. Everything that isn't bark is a long fall into the canopy, "unwalkable the way water is" (the brief). It's the
module's sea field, so the baker paints it with W1's drop tiles (the canopy far below, the haze nearer the edges), and
build_layout turns it into collision afterwards: no water tiles, so nobody fishes off the edge of a branch. The river on
the Great Bough is real water and is where the fishing is.

Kyle, 19 Nov 2026: the tree is the road up, built tier by tier ("Do NOT skip out on design of going from azeroth to the
sky"). Ground: LOWER_BOUGHS_SHEET in tools/bake_ashenvale.py (Kyle's sheet W1). Props and landmarks: W2, W4, W5.

HARD CONTRACTS (world/portal_manager.py)
  portals  Rootwater Isle (40,16) <-> the Root Stair's foot on the island; The Knothollow (62,16) <-> its mouth
"""
import numpy as np

from tools import ashenvale_engine as E

BAKED_DIR = "assets/tiles/worldtree/baked_lower_boughs"
NAME = "The Lower Boughs"
W, H = 180, 150
WTP = "assets/tiles/worldtree/props/"
SP = "assets/tiles/stranglethorn/props/"
BLD = "assets/buildings/"

PORTALS = {(40, 16): "Rootwater Isle", (62, 16): "The Knothollow"}
ARRIVALS = [(40, 20), (62, 20)]
LATER_PORTALS = {(130, 16): "The Great Settlement"}   # the Great Lift: its door opens when the city is built
START = (92, 30)        # Mossroof: everything must be reachable from here

#: the trunk: a wall of bark along the north edge (the rock rim, painted with W1's trunk wall)
TRUNK_DEPTH = 13

#: the walkable bark: the ledge along the trunk's foot and the boughs running out from it over the drop.
#: (points, half-width, tapers): a bough narrows toward its tip; a bridge doesn't.
BOUGHS = [
    ([(2, 24), (40, 23), (70, 25), (92, 26), (120, 25), (150, 24), (178, 24)], 10.5, False),   # the trunk ledge
    ([(90, 30), (91, 60), (87, 92), (90, 122), (90, 144)], 12.5, True),                       # the Great Bough
    ([(36, 30), (31, 56), (23, 84), (19, 112), (24, 138)], 9.5, True),                        # the west bough
    ([(148, 30), (154, 58), (162, 86), (166, 116), (168, 134)], 9.5, True),                   # the east bough
    ([(86, 82), (66, 92), (48, 104)], 6.5, True),                                             # the west fork
    ([(92, 70), (116, 82), (132, 98), (140, 120)], 6.5, True),                                # the east fork
]
#: rope-and-plank walkways across the drop between the forks and the outer boughs
BRIDGES = [
    ([(50, 104), (36, 105), (26, 106)], 2.6),
    ([(130, 97), (146, 96), (158, 95)], 2.6),
]


def _seg_dist(gx, gy, pts):
    out = np.full(np.shape(gx), 1e9)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        vx, vy = x1 - x0, y1 - y0
        t = np.clip(((gx - x0) * vx + (gy - y0) * vy) / float(vx * vx + vy * vy), 0, 1)
        out = np.minimum(out, np.hypot(gx - (x0 + t * vx), gy - (y0 + t * vy)))
    return out


def sea(gx, gy):
    """The drop: everything that isn't bough, ledge or bridge. Extent > 0 is a fall into the canopy."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    wob = 1.3 * np.sin(0.23 * gx + 0.7) + 1.1 * np.sin(0.19 * gy + 2.1) + 0.6 * np.sin(0.41 * gx - 0.37 * gy)
    land = np.full(np.shape(gx), 99.0)
    for pts, hw, tapers in BOUGHS:
        d = _seg_dist(gx, gy, pts)
        if tapers:
            tip = np.hypot(gx - pts[-1][0], gy - pts[-1][1])
            span = max(np.hypot(pts[-1][0] - pts[0][0], pts[-1][1] - pts[0][1]), 1.0)
            hw = hw * (0.55 + 0.45 * np.clip(tip / span, 0, 1))
        land = np.minimum(land, d - hw + wob)
    for pts, hw in BRIDGES:
        land = np.minimum(land, _seg_dist(gx, gy, pts) - hw + 0.15 * wob)
    # the ledge runs right up to the trunk: no drop between them
    land = np.minimum(land, gy - (TRUNK_DEPTH + 9.0))
    edge = np.maximum.reduce([2.0 - gx, gx - (W - 3.0), gy - (H - 3.0)])
    return np.maximum(land, edge * 3.0)


ISLETS = []
LAKES = {"pools": [(60, 30, 3, 2, 0, 0.6), (112, 112, 3, 2, 0, 1.7)]}     # rain pools held in hollows of the bark
DEEP_SHRINK = {"pools": 9.0}
#: the river down the middle of the Great Bough, in a channel worn in its bark; shallow enough to wade all the way
RIVERS = [([(94, 32), (95, 48), (94, 64), (91, 80), (90, 96), (93, 112), (93, 128), (92, 147)], 2.4, -4.0)]
FORDS = []

MESAS = []
RIDGES = []
#: leafy masses where a bough is widest: impassable, painted as the canopy over the bark
WOODS = [
    (78, 52, 5, 4, 0, 1.0), (104, 104, 4, 5, 0, 2.0), (16, 70, 4, 4, 0, 0.6), (160, 70, 4, 4, 0, 1.4),
    (80, 128, 4, 3, 0, 2.2),
]
BELTS = []
CLEARINGS = [
    (92, 30, 14, 9),            # Mossroof
    (40, 22, 7, 5),             # the top of the Root Stair
    (62, 21, 6, 4),             # before the Knothollow
    (130, 22, 7, 5),            # the Great Lift
    (90, 132, 12, 8),           # the Bloodscalp's camp at the Great Bough's end
    (24, 92, 9, 7),             # the apes' feeding ground
    (162, 102, 9, 7),           # the spiders' web-hall
    (60, 96, 6, 5),             # the sky-bones on the west fork
    (128, 92, 6, 5),            # the sky-bones on the east fork
]
#: sunlit bark ("corrupt" -> dappled light), the spiders' gloom ("burned" -> shade), the planks of the bridges and
#: Mossroof's decks ("paved" -> lashed planks)
CORRUPT_PATCHES = [(90, 60, 10, 14), (30, 60, 8, 10), (156, 60, 8, 10), (70, 26, 18, 5), (120, 25, 16, 5)]
BURNED_PATCHES = []
BLUEBELL_PATCHES = [(22, 120, 6, 8), (88, 104, 7, 6)]
PAVED_PATCHES = [(92, 28, 10, 5), (32, 105, 6, 3), (44, 104, 6, 3), (138, 96, 6, 3), (150, 96, 6, 3),
                 (40, 21, 5, 3), (130, 21, 5, 3)]
LUSH = 0.9
GRADE = None           # Kyle's own sheet (W1) carries the look
#: the baker's depth pass over the drop (tools/bake_ashenvale.drop_depth): the canopy far below in a green-gold haze,
#: shaded by the boughs above it
DROP = {"haze": (104, 138, 104), "fade": 0.34, "shadow": (3.0, 5.0)}

GAPS = [("ell", 62, 18, 5, 4), ("ell", 40, 18, 5, 4), ("ell", 130, 18, 5, 4), ("ell", 92, 30, 10, 7)]

ROADS = {
    "ledge":  ([(6, 26), (40, 24), (70, 26), (92, 28), (120, 26), (150, 26), (174, 25)], 3.0),
    "stair":  ([(40, 24), (40, 18)], 2.6),
    "knot":   ([(62, 25), (62, 18)], 2.4),
    "lift":   ([(130, 26), (130, 18)], 2.6),
    "great":  ([(90, 28), (84, 40), (83, 60), (80, 92), (82, 120), (84, 136)], 3.0),
    "west":   ([(36, 26), (32, 56), (25, 84), (20, 112), (23, 132)], 2.8),
    "east":   ([(148, 26), (153, 58), (160, 86), (164, 112), (166, 128)], 2.8),
    "wfork":  ([(80, 84), (66, 93), (52, 103)], 2.4),            # the bridge beyond is planks, not road
    "efork":  ([(83, 70), (100, 74), (114, 83), (128, 96)], 2.4),
}


class _Spec(E.Spec):
    """No leafy masses on the bridges or in the drop."""

    def woods_raw(self, gx, gy):
        out = super().woods_raw(gx, gy)
        return np.minimum(out, -(np.asarray(sea(gx, gy)) + 3.0))


SPEC = _Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
             mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
             rim={}, rock_rim={"north": TRUNK_DEPTH}, gaps=GAPS, fords=FORDS, thicket=(0.76, 10.0, 2.0))

#: the trolls of Mossroof and out on the boughs (tools/build_lower_boughs_people.py writes their records)
NPC_POSITIONS = {
    "lb_elder":          (92, 24),     # Mossroof's elder
    "lb_hunter":         (84, 30),     # the bough-hunter
    "lb_shaman":         (100, 30),    # the river's shaman
    "lb_ropemaster":     (106, 24),    # keeps the bridges and the ropes
    "lb_scholar":        (78, 24),     # buys sky-bones for the Settlement's scholars
    "lb_transplant":     (98, 36),     # a transplant who climbed for the view and stayed
    "lb_provisioner":    (82, 36),     # food and drink
    "lb_trader":         (104, 36),    # the village's trader
    "lb_stairwarden":    (44, 22),     # at the top of the Root Stair
    "lb_liftkeeper":     (126, 22),    # at the Great Lift
    "lb_scout_west":     (34, 72),     # watching the apes from the west bough
    "lb_scout_south":    (86, 112),    # watching for climbers on the Great Bough
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("The Trunk Ledge", 0, 10, 180, 30, None),
    ("The Howling Bough", 2, 40, 62, 110, None),
    ("The Silkwood", 112, 40, 68, 100, None),
    ("The Greenwater Bough", 64, 40, 50, 80, None),
    ("The Climbers' Cut", 64, 118, 52, 32, None),
    ("Mossroof", 72, 14, 40, 28, None),
]

#: what grows on a branch: leaf crowns, curtains of moss and vine, side branches, ferns
TREES = {
    "big":   [(WTP + "wt_leaf_crown.png", 7), (WTP + "wt_side_branch.png", 8), (WTP + "wt_moss_curtain.png", 7)],
    "mid":   [(WTP + "wt_vine_curtain.png", 6), (WTP + "wt_leaf_crown.png", 6), (SP + "stv_tree_fern.png", 6)],
    "small": [(SP + "stv_tree_fern.png", 5), (WTP + "wt_bromeliads.png", 3), (WTP + "wt_ferns.png", 3)],
    "woods": [(WTP + "wt_leaf_crown.png", 7), (WTP + "wt_moss_curtain.png", 7), (WTP + "wt_side_branch.png", 8)],
}


def drop_mask(L):
    """Tiles over the drop, from the same field the baker paints."""
    ys, xs = np.mgrid[0:H, 0:W]
    return sea(xs + 0.5, ys + 0.5) > 0


def open_the_drop(L):
    """The drop is collision, not water: nothing to swim, fish or wade."""
    z = L.z
    m = drop_mask(L)
    for y, x in zip(*np.nonzero(m)):
        z.set_tile(int(x), int(y), "grass", "base")
        z.set_tile(int(x), int(y), "cliff", "collision")


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "The World Tree's first lived-on tier: boughs as wide as roads over a long drop into the "
                             "jungle canopy, and the trolls' village of Mossroof at the trunk's foot.",
                             "Eastern Kingdoms - The World Tree", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    open_the_drop(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.seal_unreachable(L, START)
    dress(L)
    E.build_free_mask(L, NPC_POSITIONS.values())
    for lm in L.z.landmarks:
        ax, ay, w, h = lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]
        L.free_mask[max(0, ay):ay + h + 1, max(0, ax - 1):ax + w + 1] = False
    L.free_mask[drop_mask(L)] = False
    E.scatter_trees(L, TREES, seed=4401, spacing=7.0, grove_keep=0.55)
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def sprinkle(L):
    """Ferns, fallen leaves and shelf fungus on the bark; nothing on the roads or over the drop."""
    import random
    rnd = random.Random(4403)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = {"wt_ferns": 0, "wt_fallen_leaf": 0, "wt_shelf_fungus": 0, "wt_bromeliads": 0, "wt_knot_hole": 0}
    cap = {"wt_ferns": 24, "wt_fallen_leaf": 16, "wt_shelf_fungus": 8, "wt_bromeliads": 12, "wt_knot_hole": 5}
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        name = ("wt_ferns" if r < 0.012 else "wt_fallen_leaf" if r < 0.020 else "wt_shelf_fungus" if r < 0.024 else
                "wt_bromeliads" if r < 0.030 else "wt_knot_hole" if r < 0.032 else None)
        if name and n[name] < cap[name]:
            if L.prop(name, x, y, 3, path_dir=WTP, solid=False, nudge=0):
                n[name] += 1
    L.clutter = tuple(n.values())


CHEST_SPOTS = [(12, 28), (172, 30), (20, 128), (40, 108), (64, 100), (170, 126), (150, 98), (138, 116),
               (96, 140), (82, 66)]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    G = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=WTP, **kw)                      # noqa: E731
    B = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=BLD, **kw)                      # noqa: E731

    # ---- the trunk: the stair up from the island, the lift to the city, the loa's face in the bark
    B("wt_root_stair", 40, 14, 9, solid="core", road_ok=True, nudge=2)
    B("wt_great_lift", 130, 14, 12, solid="core", road_ok=True, nudge=2)
    B("wt_loa_face", 92, 12, 12, solid="core", allow_overlap=True, nudge=2)
    G("wt_stair_landing", 46, 20, 4, solid="core", nudge=3)
    G("wt_knot_hole", 62, 13, 9, solid="core", road_ok=True, allow_overlap=True, nudge=1)
    # ---- Mossroof: moss-roofed treehouses on platforms at the trunk's foot
    G("wt_treehouse", 80, 20, 8, solid="core", nudge=4)
    G("wt_treehouse", 106, 20, 8, solid="core", nudge=4)
    G("wt_treehouse_small", 74, 32, 6, solid="core", nudge=4)
    G("wt_treehouse_small", 112, 32, 6, solid="core", nudge=4)
    G("wt_platform_ladder", 70, 22, 5, solid="core", nudge=3)
    G("wt_cook_shelter", 84, 40, 5, solid="core", nudge=3)
    G("wt_hammock", 102, 40, 4, solid="core", nudge=3)
    G("wt_cistern_house", 116, 22, 6, solid="core", nudge=4)
    B("gs_loa_totem", 92, 34, 5, solid="core", nudge=3)
    B("gs_lantern_post", 86, 26, 4, solid="core", nudge=3)
    B("gs_lantern_post", 98, 26, 4, solid="core", nudge=3)
    B("gs_lantern_post", 46, 26, 4, solid="core", nudge=3)
    B("gs_lantern_post", 124, 26, 4, solid="core", nudge=3)
    B("gs_prayer_streamers", 100, 22, 5, solid="core", nudge=3)
    G("wt_rope_post", 88, 44, 4, solid="core", nudge=3)
    G("wt_rope_post", 52, 102, 4, solid="core", nudge=3)
    G("wt_rope_post", 128, 100, 4, solid="core", nudge=3)
    G("wt_rope_hooks", 24, 110, 4, solid="core", nudge=3)
    G("wt_rope_hooks", 160, 98, 4, solid="core", nudge=3)
    # ---- the Greenwater Bough: the river, its pools and its fall off the bough's tip
    G("wt_pool_reeds", 99, 58, 3, solid=False, nudge=4)
    G("wt_pool_reeds", 92, 100, 3, solid=False, nudge=4)
    G("wt_bark_pool", 80, 76, 4, solid="core", nudge=4)
    G("wt_branch_falls", 93, 144, 8, solid="core", allow_overlap=True, nudge=3)
    G("wt_sap_drip", 82, 58, 4, solid="core", nudge=4)
    G("wt_sap_blister", 80, 108, 5, solid="core", nudge=4)
    G("wt_seed_pod", 102, 86, 4, solid="core", nudge=4)
    # ---- the Howling Bough: the apes' feeding ground and the old troll shrine they've taken
    G("wt_fallen_branch", 18, 96, 6, solid="core", nudge=5)
    G("wt_old_shrine", 28, 88, 6, solid="core", nudge=4)
    G("wt_seed_pod", 16, 88, 4, solid="core", nudge=4)
    G("wt_ruined_hut", 30, 64, 6, solid="core", nudge=4)
    G("wt_fork_boulder", 22, 120, 5, solid="core", nudge=4)
    # ---- the Silkwood: webs hung between the leaf crowns, a hollow knot where the spiders nest
    G("wt_vine_curtain", 158, 104, 6, solid="core", nudge=4)
    G("wt_moss_curtain", 168, 98, 6, solid="core", nudge=4)
    G("wt_knot_hole", 164, 110, 5, solid="core", nudge=4)
    G("wt_pale_mushrooms", 156, 80, 3, solid=False, nudge=4)
    G("wt_shelf_fungus", 150, 66, 4, solid="core", nudge=4)
    G("wt_dead_stub", 166, 120, 5, solid="core", nudge=4)
    # ---- the Climbers' Cut: the Bloodscalp's ropes up from the jungle, and their camp on the bough's end
    G("wt_climber_camp", 90, 130, 7, solid="core", nudge=4)
    G("wt_bloodscalp_tent", 80, 136, 6, solid="core", nudge=4)
    G("wt_war_totem", 100, 132, 6, solid="core", nudge=4)
    G("wt_skull_rack", 84, 126, 5, solid="core", nudge=4)
    G("wt_skull_bonfire", 92, 138, 4, solid="core", nudge=4)
    G("wt_stake_barricade", 90, 120, 4, solid="core", nudge=4)
    G("wt_rope_hooks", 82, 142, 4, solid="core", nudge=3)
    # ---- sky-bones: what's fallen out of the sky and caught in the branches
    G("wt_bronze_scrap", 60, 96, 4, solid="core", nudge=5)
    G("wt_engine_housing", 128, 90, 5, solid="core", nudge=5)
    G("wt_crystal_shard", 132, 104, 4, solid="core", nudge=5)
    G("wt_bronze_wing", 140, 116, 4, solid="core", nudge=5)
    # ---- the tree's own life on the ledge
    G("wt_moss_curtain", 14, 22, 6, solid="core", nudge=4)
    G("wt_vine_curtain", 166, 22, 6, solid="core", nudge=4)
    G("wt_shelf_fungus", 54, 20, 4, solid="core", nudge=4)
    G("wt_blossoms", 64, 30, 3, solid=False, nudge=4)
    G("wt_blossoms", 140, 30, 3, solid=False, nudge=4)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_lower_boughs():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS) + list(LATER_PORTALS),
                              npc=list(NPC_POSITIONS.values()))
