"""
Hand-built The Great Settlement (184x160): the Highbough Tribes' city in the heart of the World Tree, above the Lower
Boughs (docs/worldtree_brief.md).

Kyle, 19 Nov 2026: "a massive central city in the middle of it", the tree's town, the trolls'; then "Great settlement will
be large but not capital city large." So it's a full town, every service a city has, built smaller than a capital
(Timbermaw Hold is 220x200; this is 184x160 and most of it is the hollow).

THE SHAPE. The city stands in the hollow heart of the tree on great platforms of heartwood and plank, each a district,
joined by plank bridges over the drop. Far below them, through the lanterns, are the lower tiers. The main trunk is the
north wall, with a ledge along its foot that carries the two lifts and the High Chieftain's palace.

    THE LIFTFOOT (the ledge's west end): the Great Lift up from the Lower Boughs comes in here, behind the city gate
    THE CHIEFTAIN'S RISE (the ledge's middle): the Heart Palace wrapped round the trunk, the loa temple, Zan'kaji
    THE HIGH LIFT (the ledge's east end): the lift on up to the Middle Boughs
    THE MARKET (the great middle platform): the inn, the bank and the auction house with the mail between them (Kyle,
      17 Nov 2026: "an auction house, a bank, and a mailbox close together"), the stalls, the tea house, the
      quartermaster, and the sky-bone wall where the scholars show what's fallen from the clouds
    THE TRADES TERRACE (east): the forge, the alchemist, the tanner, the herbalist, the cook, and the trainers' lodge
    THE LANTERN WARD (south-west): homes packed together on the biggest of the lower platforms
    THE ROOST (south-east): the bat roost (the flight path) and the scholars' hall
    THE GARDENS (west of the Market): the terrace where the ward grows its food
    THE FALLS (south): a waterfall pours through the city from the branches above into a pool, and off the platform's
      edge into the hollow; the waterfall shrine beside it

THE DROP is the hollow inside the tree: the module's sea field, painted with W1's lantern-lit drop, and
turned to collision like the Lower Boughs'. The falls pool is real water.

Ground: GREAT_SETTLEMENT_SHEET in tools/bake_ashenvale.py (Kyle's sheet W1, the city row). Buildings: W3 (gs_*),
landmarks W5 (gs_heart_palace, gs_great_gate). People: tools/build_great_settlement.py.

HARD CONTRACTS (world/portal_manager.py)
  portal  (24,14) <-> the Lower Boughs' Great Lift (130,16): you arrive at (24,18) here and (130,20) there
"""
import numpy as np

from tools import ashenvale_engine as E
from tools import handbuilt_worldtree_lower_boughs as LB

BAKED_DIR = "assets/tiles/worldtree/baked_great_settlement"
NAME = "The Great Settlement"
W, H = 184, 160
WTP = "assets/tiles/worldtree/props/"
BLD = "assets/buildings/"
SP = "assets/tiles/stranglethorn/props/"

PORTALS = {(24, 14): "The Lower Boughs", (162, 14): "The Middle Boughs"}
ARRIVALS = [(24, 18), (162, 18)]
LATER_PORTALS = {}
START = (92, 70)        # the Market: everything must be reachable from here

TRUNK_DEPTH = 11

#: the districts, each a platform over the hollow built out in lobes (never one round blob; Kyle on earlier maps: "Still
#: doing a lot of circular blobs"): a list of (cx, cy, rx, ry) ellipses whose union is the platform
DISTRICTS = {
    "market":  [(92, 70, 31, 16), (74, 82, 18, 12), (112, 62, 18, 12), (106, 84, 16, 10), (92, 90, 14, 8)],
    "trades":  [(152, 56, 22, 13), (168, 66, 13, 11), (142, 68, 13, 8), (152, 44, 12, 7)],
    "lantern": [(36, 100, 24, 14), (22, 116, 15, 12), (50, 116, 16, 10), (40, 86, 15, 8)],
    "roost":   [(146, 112, 20, 12), (160, 122, 13, 10), (136, 122, 11, 8), (152, 100, 13, 7)],
    "falls":   [(92, 130, 18, 12), (82, 142, 11, 7), (104, 140, 10, 7)],
    # Kyle, 20 Nov 2026: "Let's have a bit more land mass for gs": a garden terrace between the Liftfoot's bridge and
    # the Market, where the ward grows its food
    "gardens": [(54, 56, 15, 11), (44, 66, 10, 7)],
}
#: the ledge along the trunk's foot
LEDGE = ([(4, 21), (40, 23), (92, 25), (140, 23), (180, 21)], 12.0)
#: plank bridges over the hollow: (points, half-width)
BRIDGES = [
    ([(92, 32), (92, 54)], 4.0),                        # the Rise's great stair down to the Market
    ([(30, 30), (34, 88)], 3.0),                        # the Liftfoot down to the Lantern Ward
    ([(120, 66), (134, 60)], 3.2),                      # the Market to the Trades Terrace
    ([(68, 84), (54, 94)], 3.2),                        # the Market to the Lantern Ward
    ([(112, 88), (130, 104)], 3.2),                     # the Market to the Roost
    ([(92, 90), (92, 118)], 3.4),                       # the Market to the Falls
    ([(154, 44), (154, 30)], 3.0),                      # the Trades Terrace up to the ledge
    ([(108, 132), (128, 122)], 2.6),                    # the Falls to the Roost
]


def _ell(gx, gy, cx, cy, rx, ry):
    return (np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2) - 1.0) * min(rx, ry)


def sea(gx, gy):
    """The hollow: everything that isn't a district, the ledge or a bridge. Extent > 0 is a fall into the tree."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    wob = 1.1 * np.sin(0.21 * gx + 1.3) + 0.9 * np.sin(0.17 * gy + 0.4) + 0.5 * np.sin(0.37 * gx - 0.31 * gy)
    land = np.full(np.shape(gx), 99.0)
    for lobes in DISTRICTS.values():
        for (cx, cy, rx, ry) in lobes:
            land = np.minimum(land, _ell(gx, gy, cx, cy, rx, ry) + wob)
    pts, hw = LEDGE
    land = np.minimum(land, LB._seg_dist(gx, gy, pts) - hw + wob)
    for pts, hw in BRIDGES:
        land = np.minimum(land, LB._seg_dist(gx, gy, pts) - hw + 0.15 * wob)
    land = np.minimum(land, gy - (TRUNK_DEPTH + 8.0))
    edge = np.maximum.reduce([2.0 - gx, gx - (W - 3.0), gy - (H - 3.0)])
    return np.maximum(land, edge * 3.0)


ISLETS = []
#: the falls pool, under the waterfall from the branches above
LAKES = {"falls": [(92, 132, 6, 4, 0, 0.3)]}
DEEP_SHRINK = {"falls": 3.0}
RIVERS = [([(92, 135), (93, 140), (92, 146)], 1.8, -4.0)]    # the overflow running off the platform's edge
FORDS = []
MESAS = []
RIDGES = []
WOODS = []
BELTS = []
CLEARINGS = [(c[0], c[1], c[2] - 3, c[3] - 3) for lobes in DISTRICTS.values() for c in lobes] + [(24, 20, 10, 6), (92, 22, 16, 6),
                                                                              (162, 20, 10, 6)]
#: the city's floors: the Market's planks and plaza, the Rise's stone, the Trades' clay yards, the Ward's heartwood
PAVED_PATCHES = [(92, 72, 24, 14), (92, 24, 18, 5), (24, 21, 8, 4), (162, 21, 8, 4), (148, 114, 15, 10),
                 (92, 128, 12, 8)]
CORRUPT_PATCHES = [(38, 104, 20, 13)]                  # the Lantern Ward's carved bark between the homes
BURNED_PATCHES = [(154, 58, 16, 10)]                   # the Trades Terrace's red clay yards
BLUEBELL_PATCHES = [(30, 112, 6, 4), (52, 98, 5, 3), (54, 58, 11, 7), (44, 66, 7, 4)]   # garden soil: homes, the Gardens
LUSH = 0.0
GRADE = None
DROP = {"haze": (70, 54, 30), "fade": 0.16, "sat": 1.0, "shadow": (2.5, 4.0)}

GAPS = [("ell", 24, 17, 6, 4), ("ell", 162, 17, 6, 4)]

ROADS = {
    "ledge":   ([(8, 22), (24, 21), (60, 23), (92, 26), (130, 24), (162, 22), (176, 21)], 3.2),
    "lift":    ([(24, 21), (24, 16)], 2.6),
    "high":    ([(162, 22), (162, 16)], 2.6),
    "stair":   ([(92, 26), (92, 56)], 3.6),
    "market":  ([(66, 72), (92, 72), (118, 72)], 3.4),
    "trades":  ([(118, 70), (134, 61), (154, 58), (154, 28)], 3.0),
    "ward":    ([(30, 24), (32, 60), (36, 100)], 2.8),
    "wardx":   ([(70, 82), (52, 96), (36, 104)], 2.8),
    "roost":   ([(110, 86), (130, 104), (148, 112)], 2.8),
    "falls":   ([(92, 88), (92, 122)], 3.0),
}


class _Spec(E.Spec):
    pass


SPEC = _Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
             mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
             rim={}, rock_rim={"north": TRUNK_DEPTH}, gaps=GAPS, fords=FORDS, thicket=(0.99, 10.0, 2.0))

#: everyone in the city (tools/build_great_settlement.py writes their records); each stands in front of their door
NPC_POSITIONS = {
    # ---- the Chieftain's Rise
    "gs_zankaji":         (92, 22),      # High Chieftain Zan'kaji, before the Heart Palace
    "gs_loa_priest":      (68, 24),      # at the loa temple
    "gs_orc_envoy":       (110, 24),     # Orgrimmar's envoy, waiting on the chieftain
    # ---- the Liftfoot and the High Lift
    "gs_liftkeeper":      (30, 19),      # at the Great Lift down to Mossroof
    "gs_gate_guard":      (52, 26),      # at the city gate
    "gs_highlift_keeper": (156, 19),     # at the High Lift up to the Middle Boughs
    # ---- the Market
    "gs_innkeeper":       (70, 73),      # the inn
    "gs_banker":          (84, 86),      # MerchantTusk, at the bank's door
    "gs_auctioneer":      (106, 86),     # at the auction hall's door
    "gs_quartermaster":   (100, 64),     # the Highbough shelf
    "gs_provisioner":     (80, 67),      # food and drink, at the red stall
    "gs_trader":          (112, 70),     # general goods, at the moneylender's
    "gs_scholar":         (86, 61),      # at the sky-bone wall
    "gs_transplant_a":    (104, 67),     # a transplant who sells in the market, at the teal stall
    "gs_transplant_b":    (66, 86),      # a transplant at the tea house
    # ---- the Trades Terrace
    "gs_smith":           (142, 59),     # the forge's smith (sells gear)
    "ct_great_settlement": (166, 61),    # the class trainer, at the trainers' lodge
    "pt_gs_forge":        (138, 60),     # mining and blacksmithing
    "pt_gs_hide":         (141, 70),     # skinning and leatherworking
    "pt_gs_herbs":        (171, 71),     # herbalism and alchemy
    "pt_gs_cloth":        (160, 66),     # tailoring and enchanting
    "pt_gs_gems":         (160, 71),     # jewelcrafting and engineering
    "pt_gs_wood":         (166, 64),     # woodcutting and woodworking
    "pt_gs_cook":         (137, 70),     # cooking and fishing
    # ---- the Lantern Ward
    "gs_ward_elder":      (30, 108),     # the ward's elder
    "gs_ward_child":      (56, 109),     # a child of the ward
    "gs_ward_weaver":     (24, 115),     # a weaver at her door
    # ---- the Roost
    "gs_flight_master":   (140, 112),    # the bat handler
    "gs_scholar_hall":    (160, 125),    # the scholars' hall
    # ---- the Falls
    "gs_falls_keeper":    (82, 130),     # the waterfall shrine
    # ---- the Gardens
    "gs_gardener":        (56, 62),      # the ward's gardener
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("The Great Settlement", 0, 0, W, H, None),
    ("The Lantern Ward", 10, 84, 56, 40, None),
    ("The Trades Terrace", 130, 42, 50, 32, None),
    ("The Roost", 126, 98, 46, 32, None),
    ("The Falls", 72, 116, 40, 32, None),
    ("The Market", 60, 52, 64, 40, None),
    ("The Chieftain's Rise", 56, 10, 72, 22, None),
]

TREES = {
    "big":   [(WTP + "wt_leaf_crown.png", 6)],
    "mid":   [(SP + "stv_tree_fern.png", 5)],
    "small": [(WTP + "wt_bromeliads.png", 3), (WTP + "wt_ferns.png", 3)],
    "woods": [(WTP + "wt_leaf_crown.png", 6)],
}


def drop_mask(L):
    ys, xs = np.mgrid[0:H, 0:W]
    return sea(xs + 0.5, ys + 0.5) > 0


def open_the_drop(L):
    z = L.z
    for y, x in zip(*np.nonzero(drop_mask(L))):
        z.set_tile(int(x), int(y), "grass", "base")
        z.set_tile(int(x), int(y), "cliff", "collision")


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "The Highbough Tribes' city in the heart of the World Tree: lantern-lit districts on great "
                             "platforms between the trunks, bridges over the hollow, and waterfalls falling through it.",
                             "Eastern Kingdoms - The World Tree", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    L.z.is_town = True          # a town: no gathering, the town's rules
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
    E.scatter_trees(L, TREES, seed=4601, spacing=11.0, grove_keep=0.3)
    E.seal_unreachable(L, START)
    E.register_subzones(L, SUBZONES)
    return L


def dress(L):
    def B(n, x, y, h, **kw):
        kw.setdefault("solid", "core")
        kw.setdefault("nudge", 2)
        return L.prop(n, x, y, h, path_dir=BLD, **kw)

    def G(n, x, y, h, **kw):
        kw.setdefault("solid", "core")
        kw.setdefault("nudge", 2)
        return L.prop(n, x, y, h, path_dir=WTP, **kw)

    # ---- the trunk ledge: the two lifts, the gate, the palace wrapped round the trunk, the temple, homes on the trunk
    B("wt_great_lift", 24, 13, 13, road_ok=True, allow_overlap=True)
    B("gs_rope_lift", 162, 14, 12, road_ok=True, allow_overlap=True)
    B("gs_great_gate", 46, 23, 15, road_ok=True, allow_overlap=True)
    B("gs_heart_palace", 92, 17, 24, allow_overlap=True)
    B("gs_loa_temple", 68, 20, 15)
    B("gs_trunk_tower_house", 120, 18, 14)
    B("gs_trunk_stair", 134, 15, 9)
    B("gs_waterfall_shrine", 146, 17, 10)
    B("gs_trunk_tower_house", 176, 18, 12)
    B("gs_guard_post", 12, 24, 6)
    B("gs_guard_post", 60, 28, 6)
    B("gs_prayer_streamers", 80, 29, 6)
    B("gs_prayer_streamers", 104, 29, 6)
    # ---- the Market: the inn, the bank and the auction hall with the mail between them
    B("gs_inn", 70, 70, 16)
    B("gs_bank", 84, 83, 14)
    B("gs_auction_hall", 106, 83, 15)
    B("gs_tea_house", 72, 89, 8)
    B("gs_moneylender", 118, 67, 10)
    B("gs_stall_red", 80, 64, 6)
    B("gs_stall_teal", 104, 64, 6)
    B("gs_stall_masks", 112, 58, 6)
    B("gs_stall_spice", 74, 78, 6)
    B("gs_loa_totem", 92, 72, 8, road_ok=True)
    B("gs_brazier", 86, 72, 4, road_ok=True)
    B("gs_brazier", 98, 72, 4, road_ok=True)
    G("wt_engine_housing", 82, 58, 7)                    # the sky-bone wall: a broken construct from the clouds
    G("wt_bronze_wing", 90, 58, 6)
    B("gs_planter", 110, 72, 4, road_ok=True)
    # ---- the Trades Terrace
    B("gs_forge", 140, 56, 13)
    B("gs_trainers_lodge", 166, 58, 14)
    B("gs_tanner", 146, 69, 8)
    B("gs_alchemist", 171, 68, 10)
    B("gs_herbalist", 160, 63, 9)
    B("gs_cook_stall", 137, 67, 8)
    B("gs_crates", 148, 60, 4)
    # ---- the Lantern Ward: homes packed together
    B("gs_house_large", 24, 98, 13)
    B("gs_house_medium", 30, 105, 11)
    B("gs_hut_round", 52, 104, 9)
    B("gs_trunk_tower_house", 16, 110, 14)
    B("gs_balcony_house", 24, 112, 11)
    B("gs_stilt_row", 40, 114, 10)
    B("gs_house_medium", 50, 118, 11)
    B("gs_hut_round", 20, 124, 9)
    B("gs_lantern_post", 46, 108, 5)
    B("gs_planter", 42, 112, 4)
    # ---- the Roost
    B("gs_bat_roost", 148, 109, 15)
    B("gs_balcony_house", 160, 122, 12)                  # the scholars' hall
    B("gs_house_medium", 136, 120, 9)
    B("gs_lantern_post", 134, 108, 5)
    G("wt_crystal_shard", 166, 114, 5)
    # ---- the Falls
    G("wt_branch_falls", 92, 125, 12, allow_overlap=True, road_ok=True)
    B("gs_waterfall_shrine", 82, 127, 11)
    B("gs_lantern_post", 104, 128, 5)
    G("wt_pool_reeds", 100, 135, 4, solid=False)
    # ---- the Gardens: plots, planters and the gardener's hut
    B("gs_hut_round", 48, 52, 9)
    B("gs_herbalist", 62, 52, 8)
    for (x, y) in [(50, 60), (58, 58), (46, 66), (62, 62), (54, 66)]:
        B("gs_planter", x, y, 4)
    G("wt_blossoms", 40, 64, 3, solid=False)
    # ---- the wider ledge: more homes on the trunk
    B("gs_balcony_house", 12, 31, 9)
    B("gs_house_medium", 140, 30, 9)
    B("gs_trunk_tower_house", 104, 14, 12)
    # ---- the Market's south end
    B("gs_stall_spice", 84, 93, 6)
    B("gs_stall_red", 100, 93, 6)
    # ---- the Lantern Ward and the Roost, grown
    B("gs_house_large", 40, 84, 11)
    B("gs_hut_round", 12, 120, 8)
    B("gs_balcony_house", 58, 120, 9)
    B("gs_house_medium", 150, 98, 9)
    B("gs_hut_round", 166, 128, 8)
    B("gs_house_medium", 130, 126, 8)
    # ---- the Falls, grown: a tea house by the water
    B("gs_tea_house", 106, 142, 8)
    B("gs_lantern_post", 80, 144, 5)
    # ---- lanterns down the bridges and the ledge
    for (x, y) in [(88, 40), (96, 48), (126, 64), (36, 28), (128, 28), (170, 28)]:
        B("gs_lantern_post", x, y, 5)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_great_settlement():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS) + list(LATER_PORTALS),
                              npc=list(NPC_POSITIONS.values()))
