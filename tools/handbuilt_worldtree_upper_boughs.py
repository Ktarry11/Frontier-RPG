"""
Hand-built Upper Boughs (180x150), levels 47-48: thin air and wind at the top of the World Tree (docs/worldtree_brief.md).

You come up the Root Stair from the Middle Boughs and the trunk is finally narrow enough to walk round. It stands in
the middle of everything, a column of pale wind-scoured bark going on up into the cloud, and a ledge rings it. Six
branches spiral out from the ledge, every one bent the same way by a wind that never stops, and below them, close
enough to feel the damp of, are the tops of the clouds. The trolls' last camp before the cloud, Highrest, sits on the
ring's south side. Out on the branches are the wyverns' roosts, the storm-struck bough, the harpies in the gale, and the
first wreckage to fall out of the sky that anyone could call a ship: the Fallen Skiff, lying across the gap between two
branch tips.

    The Root Stair ........ the trunk's south-west face (74,86): down to the Middle Boughs
    The Stormsplit ........ the trunk's west face (68,66): a lightning-split hollow in the trunk, the tier's cave
    The Cloud Way ......... the ring's north side (90,52): the stair on up into the cloud, the Cloudbreak
    Highrest .............. the last troll camp, on the ring's south side (safe)
    The Trunk Ring ........ the ledge round the trunk
    The Wyvern Roosts ..... the east branch, bending south
    The Storm Bough ....... the south-east branch, blackened by lightning
    The Gale .............. the two western branches, where the harpies ride the wind
    The Thunderhawk Reach . the north branch, bending east
    The Skiff Wreck ....... the north-east branch and the Fallen Skiff across the gap

THE DROP is the module's sea field, painted with the cloud tops and turned into collision (no water over the void).

THE SHAPE (Kyle, 20 Nov 2026: "Prevents you from making everything blobs"): the Lower Boughs hang off a wall to the
north and the Middle Boughs off a wall to the west; here the trunk is the middle of a pinwheel, and the branches all
curve the same way, because up here the wind decides everything.

HARD CONTRACTS (world/portal_manager.py)
  portals  The Middle Boughs (74,86) <-> its Root Stair (16,18); The Stormsplit (68,66) <-> its mouth;
           The Cloudbreak (90,52) <-> the foot of its ladder
"""
import numpy as np

from tools import ashenvale_engine as E
from world.chunk_paths import exists as _chunk_exists  # noqa: E402  (.webp, .jpg or .png)

BAKED_DIR = "assets/tiles/worldtree/baked_upper_boughs"
NAME = "The Upper Boughs"
W, H = 180, 150
WTP = "assets/tiles/worldtree/props/"
BLD = "assets/buildings/"

#: the trunk, in the middle: a column of bark (the engine's mesa) and the ledge that rings it
TRUNK = (90, 70, 15, 13)
RING = (90, 71, 27, 24)
#: Highrest's platform, lashed onto the ring's south side over the drop
HIGHREST = (90, 99, 18, 7)

PORTALS = {(74, 86): "The Middle Boughs", (68, 66): "The Stormsplit", (90, 52): "The Cloudbreak"}
ARRIVALS = [(76, 89), (65, 68), (90, 55)]
LATER_PORTALS = {}
START = (90, 96)        # Highrest: everything must be reachable from here

#: the branches, spiralling out from the ring, every one bent the same way. (points, half-width, tapers)
BOUGHS = [
    ([(112, 66), (138, 62), (158, 70), (170, 88), (166, 106)], 9.5, True),        # the Wyvern Roosts, east
    ([(104, 90), (118, 110), (114, 130), (96, 144)], 9.5, True),                 # the Storm Bough, south-east
    ([(74, 90), (58, 108), (36, 116), (14, 110)], 9.0, True),                    # the Gale, south-west
    ([(66, 64), (40, 58), (20, 44), (14, 24)], 9.0, True),                       # the Gale, west
    ([(84, 48), (80, 28), (92, 12), (116, 6)], 8.5, True),                       # the Thunderhawk Reach, north
    ([(106, 52), (124, 38), (142, 34)], 8.0, True),                              # the Skiff Wreck, north-east
    ([(150, 64), (152, 52)], 5.0, True),                                         # a spur off the roosts to the skiff
]
#: plank and rope across the drop: the Fallen Skiff's deck across the gap, and one rope walk on the west
BRIDGES = [
    ([(142, 36), (148, 44), (152, 52)], 3.0),                  # the Fallen Skiff, across two branch tips
    ([(24, 46), (22, 70), (30, 96)], 2.6),                     # the old rope walk between the Gale's branches
]


def _seg_dist(gx, gy, pts):
    out = np.full(np.shape(gx), 1e9)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        vx, vy = x1 - x0, y1 - y0
        t = np.clip(((gx - x0) * vx + (gy - y0) * vy) / float(vx * vx + vy * vy), 0, 1)
        out = np.minimum(out, np.hypot(gx - (x0 + t * vx), gy - (y0 + t * vy)))
    return out


def _wob(gx, gy):
    return 1.2 * np.sin(0.21 * gx + 0.5) + 1.0 * np.sin(0.17 * gy + 1.9) + 0.6 * np.sin(0.43 * gx - 0.31 * gy)


def sea(gx, gy):
    """The drop: everything that isn't branch, ring or bridge. Extent > 0 is a fall into the cloud."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    wob = _wob(gx, gy)
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
    cx, cy, rx, ry = RING
    land = np.minimum(land, (np.hypot((gx - cx) / rx, (gy - cy) / ry) - 1.0) * min(rx, ry) + 0.6 * wob)
    cx, cy, rx, ry = HIGHREST
    land = np.minimum(land, (np.hypot((gx - cx) / rx, (gy - cy) / ry) - 1.0) * min(rx, ry) + 0.4 * wob)
    edge = np.maximum.reduce([2.0 - gx, gx - (W - 3.0), 2.0 - gy, gy - (H - 3.0)])
    return np.maximum(land, edge * 3.0)


def bridge_mask(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    out = np.full(np.shape(gx), 99.0)
    for pts, hw in BRIDGES:
        out = np.minimum(out, _seg_dist(gx, gy, pts) - hw)
    return out


def plaza_field(P, wp):
    """The rope walk's planks and the skiff's deck (the "plaza" layer), strong enough to win near the drop."""
    from tools.bake_ashenvale import smoothstep
    return 1.7 * (1.0 - smoothstep(-0.4, 1.2, bridge_mask(P.gx, P.gy)))


ISLETS = []
#: rain caught in the forks: a little water up here, and the only fishing
LAKES = {"pools": [(140, 66, 3, 2, 0, 0.6), (44, 60, 3, 2, 0, 1.4)]}
DEEP_SHRINK = {"pools": 9.0}
RIVERS = []
FORDS = []

#: the trunk itself: a column of bark in the middle of the ring
MESAS = [(TRUNK[0], TRUNK[1], TRUNK[2], TRUNK[3], 0)]
RIDGES = []
WOODS = []
BELTS = []
CLEARINGS = [
    (90, 96, 12, 6),            # Highrest
    (76, 89, 5, 4),             # the Root Stair
    (65, 68, 5, 4),             # before the Stormsplit
    (90, 54, 6, 3),             # the Cloud Way
    (164, 96, 8, 6),            # the wyverns' high roost
    (112, 124, 8, 6),           # the lightning-struck crown of the Storm Bough
    (30, 112, 8, 6),            # the harpies' gale-perch
    (100, 10, 8, 4),            # the thunderhawks' eyrie
    (146, 44, 8, 6),            # the Fallen Skiff
]
#: storm-struck bark on the Storm Bough ("burned"), the wind-scoured tips ("corrupt" -> pale), sunlit gold at the
#: branch tips where the light comes down from above ("bluebell"), and the camp's planks ("paved")
CORRUPT_PATCHES = [(160, 82, 7, 9), (20, 36, 6, 9), (96, 16, 9, 5)]
BURNED_PATCHES = [(114, 118, 7, 9), (106, 138, 6, 5)]
BLUEBELL_PATCHES = [(166, 102, 5, 5), (98, 142, 5, 3), (16, 108, 5, 4), (14, 26, 5, 5), (114, 8, 5, 3)]
PAVED_PATCHES = [(90, 96, 10, 4), (76, 89, 4, 3), (90, 49, 5, 3)]
LUSH = 0.0
GRADE = None
#: the baker's depth pass over the drop: the cloud tops close below, bright and white, shaded by the branches
DROP = {"haze": (236, 240, 246), "fade": 0.22, "sat": 0.95, "shadow": (3.0, 5.0)}

GAPS = [("ell", 76, 89, 4, 3), ("ell", 65, 68, 4, 3), ("ell", 90, 54, 5, 3), ("ell", 90, 96, 10, 5)]

ROADS = {
    "ring":     ([(90, 96), (110, 90), (116, 72), (108, 52), (90, 46), (70, 52), (64, 72), (72, 90), (90, 96)], 2.6),
    "stair":    ([(80, 92), (76, 88)], 2.2),
    "hollow":   ([(65, 72), (65, 68)], 2.2),
    "cloud":    ([(90, 52), (90, 56)], 2.2),
    "roosts":   ([(116, 68), (138, 63), (156, 70), (166, 88)], 2.6),
    "storm":    ([(106, 92), (117, 110), (112, 128)], 2.6),
    "gale_s":   ([(72, 92), (58, 108), (38, 115)], 2.6),
    "gale_w":   ([(64, 62), (40, 57), (22, 44)], 2.6),
    "reach":    ([(84, 46), (81, 28), (92, 13)], 2.4),
    "wreck":    ([(106, 50), (123, 39), (138, 35)], 2.4),
}


class _Spec(E.Spec):
    """No leafy masses up here: the wind's taken them."""

    def woods_raw(self, gx, gy):
        out = super().woods_raw(gx, gy)
        return np.minimum(out, -(np.asarray(sea(gx, gy)) + 3.0))


SPEC = _Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
             mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
             rim={}, rock_rim={}, gaps=GAPS, fords=FORDS, thicket=(0.99, 10.0, 2.0))

#: Highrest and the people out on the branches (tools/build_upper_boughs_people.py writes their records)
NPC_POSITIONS = {
    "ub_windwarden":     (90, 97),    # Highrest's warden, the last of the climbers' captains
    "ub_wyvern_tamer":   (95, 99),    # wants a wyvern egg, and then a wyvern
    "ub_storm_shaman":   (85, 100),     # listens to the storms
    "ub_skywatcher":     (96, 96),     # the Settlement's skywatcher, after the skiff
    "ub_old_climber":    (84, 96),     # the oldest troll who's ever been this high
    "ub_transplant":     (102, 101),    # a transplant who climbed for the weather
    "ub_provisioner":    (79, 99),     # food and drink
    "ub_trader":         (110, 98),   # the camp's trader
    "ub_stairwarden":    (79, 90),     # at the top of the Root Stair
    "ub_ladderkeeper":   (95, 55),     # at the foot of the Cloud Way
    "ub_scout_roosts":   (140, 66),    # watching the wyverns
    "ub_scout_wreck":    (124, 41),    # watching the skiff
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("The Trunk Ring", 60, 44, 62, 56, None),
    ("The Wyvern Roosts", 122, 50, 58, 70, None),
    ("The Storm Bough", 96, 100, 40, 50, None),
    ("The Gale", 0, 20, 70, 110, None),
    ("The Thunderhawk Reach", 70, 0, 52, 44, None),
    ("The Skiff Wreck", 104, 18, 56, 34, None),
    ("Highrest", 70, 88, 42, 16, None),
]

#: greenery this high: wind-bent branches, lichen, the last leaves turning gold where the light comes down
TREES = {
    "big":   [(WTP + "wt_wind_branch.png", 7), (WTP + "wt_side_branch.png", 7)],
    "mid":   [(WTP + "wt_wind_branch.png", 5), (WTP + "wt_dead_stub.png", 5), (WTP + "wt_gold_branch_tip.png", 5)],
    "small": [(WTP + "wt_lichen_tuft.png", 3), (WTP + "wt_shelf_fungus.png", 3)],
    "woods": [(WTP + "wt_wind_branch.png", 7)],
}


def drop_mask(L):
    ys, xs = np.mgrid[0:H, 0:W]
    return sea(xs + 0.5, ys + 0.5) > 0


def on_a_bridge(pad=1.5):
    """Tiles on or beside the planks: nothing grows or stands there, or a bridge gets plugged."""
    ys, xs = np.mgrid[0:H, 0:W]
    return bridge_mask(xs + 0.5, ys + 0.5) < pad


def at_highrest():
    ys, xs = np.mgrid[0:H, 0:W]
    return (np.abs(xs + 0.5 - 90) < 22) & (np.abs(ys + 0.5 - 96) < 9)


def open_the_drop(L):
    """The drop is collision, not water: nothing to swim, fish or wade."""
    z = L.z
    m = drop_mask(L)
    for y, x in zip(*np.nonzero(m)):
        z.set_tile(int(x), int(y), "grass", "base")
        z.set_tile(int(x), int(y), "cliff", "collision")


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "The top of the World Tree: the trunk a column you can walk round, six wind-bent branches "
                             "spiralling out over the cloud tops, wyverns, storms, and a ship that fell out of the sky.",
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
    L.free_mask[on_a_bridge()] = False
    L.free_mask[at_highrest()] = False
    # Greenery may be scattered; objects may not (Kyle, 20 Nov 2026: "dropping totems in the middle of the thing or on a
    # branch isnt [fine]. greenery is fine"). Every totem, charm, post and barrel is placed in dress() where it belongs.
    E.scatter_trees(L, TREES, seed=4801, spacing=9.0, grove_keep=0.4)
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def sprinkle(L):
    """Lichen, shelf fungus and the odd gold leaf on the bark; nothing on the roads or over the drop."""
    import random
    rnd = random.Random(4803)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = {"wt_lichen_tuft": 0, "wt_fallen_leaf": 0, "wt_shelf_fungus": 0}
    cap = {"wt_lichen_tuft": 24, "wt_fallen_leaf": 10, "wt_shelf_fungus": 8}
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        name = ("wt_lichen_tuft" if r < 0.014 else "wt_fallen_leaf" if r < 0.019 else "wt_shelf_fungus" if r < 0.023
                else None)
        if name and n[name] < cap[name]:
            if L.prop(name, x, y, 3, path_dir=WTP, solid=False, nudge=0):
                n[name] += 1
    L.clutter = tuple(n.values())


CHEST_SPOTS = [(166, 100), (100, 140), (18, 110), (16, 28), (112, 8), (140, 32), (128, 112), (50, 58), (156, 66),
               (40, 114)]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    def B(n, x, y, h, **kw):
        kw.setdefault("solid", "core")
        kw.setdefault("nudge", 2)
        return L.prop(n, x, y, h, path_dir=BLD, **kw)

    def G(n, x, y, h, **kw):
        kw.setdefault("solid", "core")
        kw.setdefault("nudge", 3)
        return L.prop(n, x, y, h, path_dir=WTP, **kw)

    # ---- the trunk's doors: the stair down, the lightning split, the stair up into the cloud
    B("wt_root_stair", 73, 85, 9, road_ok=True, allow_overlap=True)
    G("wt_lightning_stump", 67, 64, 8, road_ok=True, allow_overlap=True, nudge=1)
    B("wt_cloud_way", 90, 50, 14, road_ok=True, allow_overlap=True)
    # ---- the trunk itself: the loa's face in the bark, and the climbers' homes built against it
    B("wt_loa_face", 90, 82, 13, allow_overlap=True)
    B("gs_trunk_tower_house", 103, 81, 13, allow_overlap=True)
    B("gs_trunk_stair", 80, 82, 9, allow_overlap=True)
    # ---- Highrest: a camp, not a scatter. One fire in the middle with the people round it; the lookout on the outer
    #      edge watching the cloud, with the camp's totem guarding the edge beside it; the lean-to and the hammock along
    #      the far rim; the trader's barrels stacked behind his stall; charms hung on the windward rim, not in the way.
    B("gs_brazier", 90, 101, 4)
    G("wt_high_lookout", 76, 104, 9)
    B("gs_loa_totem", 70, 101, 6)
    G("wt_bark_leanto", 100, 105, 5)
    G("wt_hammock", 106, 104, 4)
    G("wt_sap_barrels", 113, 100, 4)
    G("wt_wind_charms", 84, 106, 5)
    G("wt_wind_charms", 95, 106, 5)
    # ---- the ring: nothing standing on the walkway; the shade's growth sits against the trunk
    G("wt_shelf_fungus", 106, 82, 4)
    G("wt_knot_hole", 112, 76, 5)
    # ---- the Wyvern Roosts
    G("wt_wyvern_nest", 162, 96, 6)
    G("wt_wyvern_nest", 168, 84, 5)
    G("wt_wyvern_nest", 150, 66, 5)
    G("wt_wind_branch", 134, 58, 6)
    # ---- the Storm Bough: lightning-struck, burned black
    G("wt_lightning_stump", 114, 122, 7)
    G("wt_lightning_stump", 104, 138, 6)
    G("wt_dead_stub", 118, 108, 5)
    # ---- the Gale: the harpies' perches and charms they took from the climbers
    G("wt_harpy_nest", 30, 112, 6)
    G("wt_harpy_nest", 18, 104, 5)
    G("wt_harpy_nest", 18, 30, 5)
    # the rope walk's posts stand either side of each end, where the ropes are tied off
    G("wt_rope_post", 21, 48, 4)
    G("wt_rope_post", 27, 48, 4)
    G("wt_rope_post", 27, 94, 4)
    G("wt_rope_post", 33, 94, 4)
    # ---- the wind: it turns one way round the trunk, so every bough is bent the same way, and the branches it's
    #      stripped and bent stand on the outside of each bend, where it hits
    G("wt_wind_branch", 164, 64, 6)              # the roosts' bend
    G("wt_wind_branch", 125, 110, 6)             # the Storm Bough's bend
    G("wt_wind_branch", 37, 123, 6)              # the south Gale's bend
    G("wt_wind_branch", 13, 46, 6)               # the west Gale's bend
    G("wt_wind_branch", 73, 30, 6)               # the Reach's bend
    # ---- the light: gold only at the very tips, where the sun first comes down through the cloud, and the leaves it
    #      turns gold falling just below them
    for (tx, ty), (lx, ly) in [((166, 104), (162, 100)), ((97, 142), (101, 138)), ((15, 110), (20, 112)),
                               ((14, 26), (17, 31)), ((114, 7), (108, 9))]:
        G("wt_gold_branch_tip", tx, ty, 5)
        G("wt_fallen_leaf", lx, ly, 2, solid=False)
    # ---- the shade: lichen and shelf fungus on the north side of the ring, where the trunk keeps the sun off
    for (x, y) in [(76, 54), (82, 50), (100, 50), (106, 54)]:
        G("wt_lichen_tuft", x, y, 3, solid=False)
    G("wt_shelf_fungus", 72, 60, 4, solid=False)
    G("wt_shelf_fungus", 109, 60, 4, solid=False)
    # ---- the Thunderhawk Reach
    G("wt_wyvern_nest", 104, 10, 5)
    G("wt_gold_branch_tip", 116, 6, 5)
    # ---- the Skiff Wreck: the ship across the gap, and what fell out of it
    B("wt_fallen_skiff", 147, 47, 13, allow_overlap=True, solid=False)
    G("wt_sky_lance", 132, 36, 5)
    G("wt_crystal_shard", 138, 30, 4)
    G("wt_bronze_scrap", 126, 44, 4)
    G("wt_engine_housing", 154, 58, 5)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and _chunk_exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_upper_boughs():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS) + list(LATER_PORTALS),
                              npc=list(NPC_POSITIONS.values()))
