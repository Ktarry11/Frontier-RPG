"""
Hand-built Middle Boughs (180x150), levels 45-47: the tree's heart above the Great Settlement (docs/worldtree_brief.md).

You come up the High Lift from the city and step out on the far side of the trunk. It's colder up here and the light is
hazy. The trunk is a wall of bark along the whole west edge, and the ledge at its foot is old troll stone: terraces,
shrines and watchtowers the first climbers built up the trunk long before the Settlement, mostly empty now. The
Highbough's shadow hunters hold one of them, Heartwatch, because of what's at their back: the Heartwood Hollow, a split in
the trunk that goes down into the heartwood, where something is eating the tree. Three boughs run east from the ledge
over a drop that's all mist now, the canopy long gone below it.

    The High Lift ......... the ledge's south end (16,128): down to the Great Settlement
    The Root Stair ........ the ledge's north end (16,18): on up to the Upper Boughs
    The Heartwood Hollow .. the split in the trunk behind Heartwatch (16,46): the dungeon (a door for later)
    Shriekhollow .......... a hollow in the trunk off the Rotting Bough's root (16,82): the harpies' nest, the cave
    Heartwatch ............ the shadow hunters' stone outpost on the terraces (safe)
    The Old Terraces ...... the ledge along the trunk, the first climbers' stone
    The Lichen Reach ...... the north bough: pale lichen, old shrines, and a construct that fell out of the sky
    The Rotting Bough ..... the middle bough: bark rot, sap blight, and the things that live in the rot
    The Hollow Bough ...... the south bough: hollows in the bark where the harpies roost

THE DROP is the module's sea field, painted with the mist tile and turned into collision (no water over the void). The
only water is rain held in hollows of the bark.

Ground: MIDDLE_BOUGHS_SHEET in tools/bake_ashenvale.py (Kyle's sheet W1): lichen bark on the boughs, the rot as the
"corrupt" patches, sap blight as the "burned" ones, harpy litter as the "bluebell" ones, the old troll stone as paving,
and lashed planks on the bridges (plaza_field).

HARD CONTRACTS (world/portal_manager.py)
  portals  The Great Settlement (16,128) <-> the city's High Lift (162,14); Shriekhollow (16,82) <-> its mouth
  later    The Upper Boughs (16,18); The Heartwood Hollow (16,46)
"""
import numpy as np

from tools import ashenvale_engine as E
from world.chunk_paths import exists as _chunk_exists  # noqa: E402  (.webp, .jpg or .png)

BAKED_DIR = "assets/tiles/worldtree/baked_middle_boughs"
NAME = "The Middle Boughs"
W, H = 180, 150
WTP = "assets/tiles/worldtree/props/"
SP = "assets/tiles/stranglethorn/props/"
BLD = "assets/buildings/"

PORTALS = {(16, 128): "The Great Settlement", (16, 82): "Shriekhollow", (16, 18): "The Upper Boughs"}
ARRIVALS = [(20, 128), (20, 82), (20, 18)]
#: drawn now, opened later: the stair on up the trunk and the dungeon in the heartwood
LATER_PORTALS = {(16, 46): "The Heartwood Hollow"}
START = (34, 50)        # Heartwatch: everything must be reachable from here

#: the trunk: a wall of bark along the west edge
TRUNK_DEPTH = 14
#: the terraces run the length of the trunk's foot, this far out from it
LEDGE_OUT = 21.0
#: Heartwatch's platform, built out from the terraces over the drop (cx, cy, rx, ry)
HEARTWATCH = (36, 51, 16, 12)

#: the walkable bark running east over the drop. (points, half-width, tapers)
BOUGHS = [
    ([(30, 26), (58, 22), (90, 15), (122, 21), (150, 15), (172, 20)], 10.0, True),     # the Lichen Reach
    ([(30, 76), (58, 70), (88, 79), (118, 70), (146, 80), (164, 74)], 11.5, True),     # the Rotting Bough
    ([(30, 120), (54, 126), (84, 133), (114, 127), (142, 137), (170, 139)], 10.0, True),  # the Hollow Bough
    ([(104, 75), (112, 58), (118, 46)], 5.5, True),                                    # a spur off the Rotting Bough
    ([(112, 127), (124, 110), (132, 100)], 6.0, True),                                 # the hollow fork
]
#: rope-and-plank walkways across the drop between the boughs
BRIDGES = [
    ([(118, 46), (121, 36), (124, 27)], 2.6),                  # the spur up to the Lichen Reach
    ([(150, 24), (150, 46), (149, 70)], 2.6),                  # the Reach down to the Rotting Bough's far end
    ([(132, 100), (130, 90), (128, 80)], 2.6),                 # the hollow fork up to the Rotting Bough
    ([(70, 84), (70, 102), (70, 118)], 2.6),                   # the Rotting Bough down to the Hollow Bough
]


def _seg_dist(gx, gy, pts):
    out = np.full(np.shape(gx), 1e9)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        vx, vy = x1 - x0, y1 - y0
        t = np.clip(((gx - x0) * vx + (gy - y0) * vy) / float(vx * vx + vy * vy), 0, 1)
        out = np.minimum(out, np.hypot(gx - (x0 + t * vx), gy - (y0 + t * vy)))
    return out


def _wob(gx, gy):
    return 1.3 * np.sin(0.23 * gy + 0.4) + 1.1 * np.sin(0.19 * gx + 1.6) + 0.6 * np.sin(0.41 * gy - 0.37 * gx)


def sea(gx, gy):
    """The drop: everything that isn't bough, terrace or bridge. Extent > 0 is a fall into the mist."""
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
    # the terraces run right up to the trunk: no drop between them; Heartwatch stands on a great stone platform
    land = np.minimum(land, gx - (TRUNK_DEPTH + LEDGE_OUT) + 0.6 * wob)
    cx, cy, rx, ry = HEARTWATCH
    land = np.minimum(land, (np.hypot((gx - cx) / rx, (gy - cy) / ry) - 1.0) * min(rx, ry) + 0.5 * wob)
    edge = np.maximum.reduce([gx - (W - 3.0), 2.0 - gy, gy - (H - 3.0)])
    return np.maximum(land, edge * 3.0)


def bridge_mask(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    out = np.full(np.shape(gx), 99.0)
    for pts, hw in BRIDGES:
        out = np.minimum(out, _seg_dist(gx, gy, pts) - hw)
    return out


def plaza_field(P, wp):
    """The bridges' lashed planks (the "plaza" layer). A bridge is narrow, so every plank is near the drop, where the
    baker's wet-edge layer scores high; the planks score higher, so they win all the way across."""
    from tools.bake_ashenvale import smoothstep
    d = bridge_mask(P.gx, P.gy)
    return 1.7 * (1.0 - smoothstep(-0.4, 1.2, d))


ISLETS = []
#: rain held in hollows of the bark: the only water, and the only fishing
LAKES = {"pools": [(64, 30, 3, 2, 0, 0.6), (98, 80, 4, 2, 0, 1.7), (140, 128, 3, 2, 0, 0.3)]}
DEEP_SHRINK = {"pools": 9.0}
RIVERS = []
FORDS = []

MESAS = []
RIDGES = []
#: the last leafy masses: fewer up here, and greyer
WOODS = [(84, 30, 4, 3, 0, 1.0), (128, 70, 4, 3, 0, 2.0), (98, 132, 4, 3, 0, 0.6)]
BELTS = []
CLEARINGS = [
    (34, 50, 12, 10),           # Heartwatch
    (20, 128, 6, 5),            # the High Lift
    (20, 82, 6, 5),             # before Shriekhollow
    (20, 46, 6, 5),             # before the Heartwood Hollow
    (20, 18, 6, 5),             # the Root Stair
    (150, 18, 10, 6),           # the crashed construct
    (60, 22, 8, 5),             # the old shrine on the Reach
    (120, 72, 9, 6),            # the rot's heart on the Rotting Bough
    (146, 79, 8, 6),            # the rot's far end
    (130, 106, 8, 6),           # the harpies' great hollow
    (88, 132, 9, 6),            # the harpies' roosts
]
#: the rot, the sap blight, the harpies' litter, the old troll stone
CORRUPT_PATCHES = [(116, 72, 16, 8), (150, 75, 10, 7), (84, 74, 8, 5), (40, 76, 5, 4)]
BURNED_PATCHES = [(122, 74, 6, 4), (146, 77, 5, 3), (92, 72, 4, 3)]
BLUEBELL_PATCHES = [(130, 104, 7, 6), (90, 126, 8, 5), (148, 132, 6, 4), (56, 122, 5, 4)]
PAVED_PATCHES = [(36, 51, 13, 10), (24, 18, 6, 4), (24, 128, 6, 4), (26, 96, 5, 4), (26, 104, 5, 4),
                 (60, 24, 5, 4), (24, 70, 4, 3)]
LUSH = 0.35
GRADE = None
#: the baker's depth pass over the drop: mist below, cool and grey, shaded by the boughs above it
DROP = {"haze": (164, 174, 178), "fade": 0.42, "sat": 0.8, "shadow": (3.0, 5.0)}

GAPS = [("ell", 20, 128, 5, 4), ("ell", 20, 82, 5, 4), ("ell", 20, 46, 5, 4), ("ell", 20, 18, 5, 4),
        ("ell", 34, 50, 10, 8)]

ROADS = {
    "terraces": ([(27, 10), (28, 40), (29, 74), (28, 100), (27, 142)], 3.0),
    "stair":    ([(27, 18), (18, 18)], 2.4),
    "heart":    ([(28, 46), (18, 46)], 2.6),
    "hollow":   ([(29, 82), (18, 82)], 2.4),
    "lift":     ([(27, 128), (18, 128)], 2.6),
    "reach":    ([(28, 26), (58, 22), (90, 16), (122, 21), (144, 17)], 2.8),
    "rot":      ([(29, 76), (58, 70), (88, 79), (118, 70), (144, 79)], 3.0),
    "hollows":  ([(28, 120), (54, 126), (84, 132), (114, 126), (140, 135)], 2.8),
    "spur":     ([(104, 76), (111, 59)], 2.2),
    "fork":     ([(114, 126), (124, 111)], 2.2),
}


class _Spec(E.Spec):
    """No leafy masses in the drop, on the bridges, or on Heartwatch's stone."""

    def woods_raw(self, gx, gy):
        gx = np.asarray(gx, float)
        gy = np.asarray(gy, float)
        out = super().woods_raw(gx, gy)
        out = np.minimum(out, -(np.asarray(sea(gx, gy)) + 3.0))
        out = np.minimum(out, bridge_mask(gx, gy) - 2.0)
        cx, cy, rx, ry = HEARTWATCH
        return np.minimum(out, (np.hypot((gx - cx) / rx, (gy - cy) / ry) - 1.1) * 8.0)


SPEC = _Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
             mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
             rim={}, rock_rim={"west": TRUNK_DEPTH}, gaps=GAPS, fords=FORDS, thicket=(0.80, 10.0, 2.0))

#: Heartwatch and the people out on the boughs (tools/build_middle_boughs_people.py writes their records)
NPC_POSITIONS = {
    "mb_shadowhunter":   (34, 44),     # Heartwatch's shadow hunter, keeper of the Heartwood Hollow
    "mb_loa_speaker":    (40, 52),     # the loa-speaker who listens to the tree
    "mb_bark_doctor":    (28, 56),     # treats the rot
    "mb_huntmaster":     (42, 44),     # hunts the harpies
    "mb_stonekeeper":    (28, 38),     # keeps the old terraces
    "mb_scholar":        (44, 58),     # the Settlement's scholar after the fallen construct
    "mb_transplant":     (38, 60),     # a transplant who came up to work the rot
    "mb_provisioner":    (32, 58),     # food and drink
    "mb_trader":         (46, 49),     # the outpost's trader
    "mb_liftkeeper":     (24, 124),    # at the High Lift
    "mb_scout_reach":    (100, 18),    # out on the Lichen Reach
    "mb_scout_hollows":  (60, 125),    # watching the harpies' bough
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("The Old Terraces", 0, 0, 40, 150, None),
    ("The Lichen Reach", 40, 0, 140, 46, None),
    ("The Rotting Bough", 40, 46, 140, 44, None),
    ("The Hollow Bough", 40, 90, 140, 60, None),
    ("Heartwatch", 18, 36, 34, 30, None),
]

#: what grows this high: lichen, moss, side branches and dead stubs; the leaves are thinning
TREES = {
    "big":   [(WTP + "wt_side_branch.png", 8), (WTP + "wt_moss_curtain.png", 7), (WTP + "wt_leaf_crown.png", 7)],
    "mid":   [(WTP + "wt_dead_stub.png", 5), (WTP + "wt_moss_curtain.png", 6), (WTP + "wt_lichen_tuft.png", 4)],
    "small": [(WTP + "wt_lichen_tuft.png", 3), (WTP + "wt_ferns.png", 3), (WTP + "wt_shelf_fungus.png", 3)],
    "woods": [(WTP + "wt_side_branch.png", 8), (WTP + "wt_moss_curtain.png", 7), (WTP + "wt_leaf_crown.png", 7)],
}


def drop_mask(L):
    ys, xs = np.mgrid[0:H, 0:W]
    return sea(xs + 0.5, ys + 0.5) > 0


def on_heartwatch():
    ys, xs = np.mgrid[0:H, 0:W]
    cx, cy, rx, ry = HEARTWATCH
    return np.hypot((xs + 0.5 - cx) / rx, (ys + 0.5 - cy) / ry) < 1.05


def on_a_bridge(pad=1.5):
    """Tiles on (or right beside) a bridge's planks: no trees, clutter or props there, or a bridge gets plugged."""
    ys, xs = np.mgrid[0:H, 0:W]
    return bridge_mask(xs + 0.5, ys + 0.5) < pad


def open_the_drop(L):
    """The drop is collision, not water: nothing to swim, fish or wade."""
    z = L.z
    m = drop_mask(L)
    for y, x in zip(*np.nonzero(m)):
        z.set_tile(int(x), int(y), "grass", "base")
        z.set_tile(int(x), int(y), "cliff", "collision")


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "The tree's heart above the Great Settlement: the first climbers' stone terraces up the "
                             "trunk, three boughs over a drop gone to mist, the rot, and the harpies in the hollows.",
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
    L.free_mask[on_a_bridge()] = False          # nothing grows on the planks
    L.free_mask[on_heartwatch()] = False        # nor on Heartwatch's stone
    E.scatter_trees(L, TREES, seed=4701, spacing=8.0, grove_keep=0.45)
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def sprinkle(L):
    """Lichen, fallen leaves, shelf fungus and rot fungus on the bark; nothing on the roads or over the drop."""
    import random
    rnd = random.Random(4703)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = {"wt_lichen_tuft": 0, "wt_fallen_leaf": 0, "wt_shelf_fungus": 0, "wt_rot_fungus": 0, "wt_knot_hole": 0}
    cap = {"wt_lichen_tuft": 22, "wt_fallen_leaf": 12, "wt_shelf_fungus": 10, "wt_rot_fungus": 10, "wt_knot_hole": 5}
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        name = ("wt_lichen_tuft" if r < 0.012 else "wt_fallen_leaf" if r < 0.018 else "wt_shelf_fungus" if r < 0.023
                else "wt_knot_hole" if r < 0.025 else None)
        if 46 <= y <= 90 and x > 60 and r < 0.03:
            name = "wt_rot_fungus"          # the rot's fungus only grows on the Rotting Bough
        if name and n[name] < cap[name]:
            if L.prop(name, x, y, 3, path_dir=WTP, solid=False, nudge=0):
                n[name] += 1
    L.clutter = tuple(n.values())


CHEST_SPOTS = [(24, 140), (24, 10), (70, 22), (170, 24), (164, 78), (100, 64), (164, 136), (138, 96), (46, 112),
               (108, 130)]


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

    # ---- the trunk's doors: the lift down to the city, the stair on up, the split into the heartwood, the hollow
    B("gs_rope_lift", 15, 126, 12, road_ok=True, allow_overlap=True)
    B("wt_root_stair", 14, 16, 9, road_ok=True, allow_overlap=True)
    B("wt_heartwood_hollow", 14, 44, 12, road_ok=True, allow_overlap=True)
    G("wt_knot_hole", 15, 80, 9, road_ok=True, allow_overlap=True, nudge=1)
    # ---- Heartwatch: the shadow hunters' stone outpost on the old terraces
    G("wt_stone_tower", 24, 40, 12)
    G("wt_stone_tower_squat", 44, 40, 8)
    G("wt_old_shrine", 46, 58, 7)
    # the totem and the fires guard the sealed split, not the middle of the platform
    B("gs_loa_totem", 22, 52, 6)
    B("gs_brazier", 21, 40, 4)
    B("gs_brazier", 22, 49, 4)
    B("gs_prayer_streamers", 36, 38, 5)
    B("gs_lantern_post", 26, 60, 4)
    B("gs_lantern_post", 42, 62, 4)
    G("wt_bark_leanto", 36, 66, 5)
    G("wt_sap_barrels", 24, 64, 4)
    # ---- the Old Terraces: the first climbers' towers and cairns up and down the trunk
    G("wt_stone_tower", 22, 98, 12)
    G("wt_stone_tower_squat", 30, 108, 7)
    G("wt_stone_cairn", 30, 30, 4)
    G("wt_stone_cairn", 32, 90, 4)
    G("wt_old_shrine", 24, 70, 6)
    G("wt_stone_tower_squat", 30, 138, 7)
    B("gs_lantern_post", 24, 120, 4)
    B("gs_lantern_post", 24, 136, 4)
    # ---- the Lichen Reach: an old shrine, a lookout, and the construct that fell out of the sky
    G("wt_old_shrine", 60, 20, 7)
    G("wt_stone_cairn", 66, 28, 4)
    G("wt_high_lookout", 96, 16, 9)
    G("wt_crashed_construct", 152, 20, 9, allow_overlap=True)
    G("wt_bronze_scrap", 144, 26, 4)
    G("wt_engine_housing", 158, 15, 5)
    G("wt_crystal_shard", 140, 18, 4)
    G("wt_wind_charms", 65, 21, 4)               # an offering hung beside the old shrine
    # ---- the Rotting Bough: rot pits, sacs, sap split open, and a treant gone wrong in it
    G("wt_rot_pit", 116, 70, 6)
    G("wt_rot_sac", 124, 76, 4)
    G("wt_rot_sac", 108, 74, 4)
    G("wt_dark_sap_split", 120, 66, 6)
    G("wt_rot_pit", 150, 74, 5)
    G("wt_rot_sac", 156, 78, 4)
    G("wt_sap_blister", 88, 72, 5)
    G("wt_dead_stub", 142, 70, 5)
    G("wt_fallen_branch", 70, 76, 6)
    # ---- the Hollow Bough: the harpies' nests in the hollows of the bark
    G("wt_harpy_nest", 130, 104, 6)
    G("wt_harpy_nest", 88, 128, 6)
    G("wt_harpy_nest", 96, 122, 5)
    G("wt_harpy_nest", 148, 134, 5)
    G("wt_knot_hole", 136, 100, 5)
    G("wt_knot_hole", 78, 128, 5)
    G("wt_dead_stub", 60, 128, 5)
    G("wt_seed_pod", 116, 130, 4)
    G("wt_rope_post", 75, 84, 4)
    G("wt_rope_post", 76, 122, 4)
    G("wt_rope_hooks", 137, 100, 4)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and _chunk_exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_middle_boughs():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS) + list(LATER_PORTALS),
                              npc=list(NPC_POSITIONS.values()))
