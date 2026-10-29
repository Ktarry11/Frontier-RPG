"""
Hand-built Booty Bay (70x60): the deep-water port at the bottom of the world.

TOWN ARCHETYPE: TERRACED COVE.  Ratchet is a harbour with a bluff behind it; this is the opposite shape -
a cove bitten out of a headland, with the only land approach on TOP of the cliff and the whole town
hanging off the water below it.  You come in at the clifftop gate (35,4), walk east along the headland,
and take the one ramp down past the harbourmaster's tower into the cove.  Below that there is no soil at
all: the quay, the market and the inn stand on timber decking over the water, and the three piers run
out from the promenade into the bay.  The boat to Ratchet ties up at the head of the middle one.

WHY IT IS ITS OWN FACTION.  claude/stranglethorn_design.md: when the land road south turned to rock,
Booty Bay stopped being one of the Steamwheedle Cartel's franchises and became the only deep-water
harbour that still connects anything to anything.  Gazlowe signs the manifests in Ratchet.  Baron
Revilgaz decides what actually sails.  The Cartel has not formally lost the port and will tell you so.
The practical consequence for the town's shape is the LANDING FEE: the ramp is a choke point, there is a
toll post on it, and you cannot reach the quay without walking past somebody who wants paying.

HARD CONTRACTS (world/portal_manager.py)
  portal   (35,4)  -> Southern Stranglethorn (36,150);  arrival (35,6)
  boat     (64,34) -> Ratchet (64,30), the middle pier head; registered, not flavour
"""
import sys

import numpy as np

from tools import town_kit as K
from tools.handbuilt_central_barrens import _wob, _smooth, _gauss

KEY = "booty_bay"
NAME = "Booty Bay"
DESC = "A goblin port in a cove, built on decking over the water. Nothing sails without the Baron."
REGION = "Eastern Kingdoms - Stranglethorn"
W, H = 70, 60
BAKED_DIR = "assets/tiles/booty_bay/baked"
IS_TOWN = True
BASE_TILE = "grass"
PORTALS = {(35, 4): "Southern Stranglethorn"}
ARRIVALS = [(35, 6)]
START = (35, 8)
BOAT = (64, 34)

ROADS = {
    # the clifftop: in at the gate, east along the headland to the ramp head
    "gate":  ([(35, 3), (35, 9), (39, 13), (45, 16)], 3.4),
    # the one way down into the cove
    "ramp":  ([(45, 16), (48, 22), (44, 28), (39, 33)], 3.0),
    # the quay, west along the water
    "quay":  ([(39, 33), (31, 35), (22, 37), (13, 39)], 3.2),
    # down to the lower shelf: warehouses and the Baron's own stair
    "lower": ([(28, 36), (27, 44), (25, 51)], 2.6),
    # the headland's west end - the lookout over the cape
    "look":  ([(33, 9), (24, 10), (15, 12), (9, 15)], 2.4),
}
PLAZA = (34, 35, 7.0, 4.4)

# decks laid over water: (x0, x1, y0, y1)
DECKS = [
    (43.0, 46.6, 23.0, 49.0),        # the promenade boardwalk, north-south
    (46.0, 60.0, 24.6, 26.4),        # north pier
    (46.0, 66.0, 32.8, 35.2),        # middle pier
    (59.0, 69.0, 30.4, 38.6),        # middle pier head platform (boat at 64,34)
    (46.0, 58.0, 44.6, 46.4),        # south pier
    (36.0, 44.0, 32.0, 38.0),        # the quay apron - the town's floor
]

_RS = K.RoadSet(ROADS)
road_dist = _RS.dist
_RIDGE_TREES = {}
# the headland scarp: the cliff the town hangs off, open only where the ramp comes down (east of x 40)
RIDGES = [([(2, 19), (12, 21), (22, 18), (32, 20), (39, 17)], 3.6)]
GAPS = [(35, 4, 5, 5)]


def paved(gx, gy):
    cx, cy, rx, ry = PLAZA
    r = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
    return (1 - r) * min(rx, ry)


def shore(gy):
    """x of the waterline.  The headland reaches east at the top, the cove bites in below it, and the
    southern cape comes back out again."""
    gy = np.asarray(gy, float)
    return (44.0 + 15.0 * (1 - _smooth(13, 24, gy)) + 13.0 * _smooth(48, 58, gy)
            - 3.2 * _gauss(gy, 34, 10) + 1.2 * np.sin(0.42 * gy + 0.8) + 0.7 * np.sin(0.93 * gy))


def water_fields(gx, gy):
    sea = gx - shore(gy)
    return sea, sea - 3.4


def deck_field(gx, gy):
    best = np.full(np.shape(gx), -9.0)
    for (x0, x1, y0, y1) in DECKS:
        e = np.minimum(np.minimum(gx - x0, x1 - gx), np.minimum(gy - y0, y1 - gy))
        best = np.maximum(best, e)
    return best


def _ridge(pts, hw, gx, gy):
    from scipy.spatial import cKDTree
    key = id(pts)
    if key not in _RIDGE_TREES:
        from tools.terrain_painter import Painter
        _RIDGE_TREES[key] = cKDTree(Painter.spline(pts))
    tree = _RIDGE_TREES[key]
    d, idx = tree.query(np.stack([gx.ravel(), gy.ravel()], 1))
    t = idx / max(1, tree.n - 1)
    taper = 0.35 + 0.65 * np.sin(np.pi * t) ** 0.6
    return (hw * taper).reshape(gx.shape) + 0.7 * _wob(gx, gy) - d.reshape(gx.shape)


def cliff_field(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    out = np.full(gx.shape, -99.0)
    for (pts, hw) in RIDGES:
        out = np.maximum(out, _ridge(pts, hw, gx, gy))
    west = (5.0 + 1.4 * np.sin(0.19 * gy + 0.4) + 0.8 * np.sin(0.47 * gy)) - gx
    north = (2.8 + 1.1 * np.sin(0.14 * gx + 1.0) + 0.6 * np.sin(0.39 * gx)) - gy
    south = gy - (56.4 - 1.3 * np.sin(0.16 * gx + 2.0) - 0.7 * np.sin(0.43 * gx))
    out = np.maximum(out, np.maximum(west, np.maximum(north, south)))
    # sea stacks standing off the cove mouth, and the knuckle the harbourmaster's tower sits on
    for (cx, cy, rx, ry) in [(62, 12, 5.0, 3.6), (50, 54, 4.2, 3.0), (52, 20, 3.4, 2.6)]:
        r = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
        out = np.maximum(out, (1 - r) * min(rx, ry))
    clear = np.full(gx.shape, -99.0)
    for (cx, cy, rx, ry) in GAPS:
        d = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
        clear = np.maximum(clear, (1 - d) * min(rx, ry))
    clear = np.maximum(clear, road_dist(gx, gy) + 2.4)
    clear = np.maximum(clear, deck_field(gx, gy) + 1.5)
    return np.minimum(out + 1.0 * _wob(gx, gy), -clear)


def fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    sh, dp = water_fields(gx, gy)
    return dict(cliff=cliff_field(gx, gy), shallow=sh, deep=dp, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


# ---- painter config -----------------------------------------------------------------------------------
WATER = "sea"
BASE = {"jungle": 0.75, "clay": 0.22, "hard": 0.35}
PAINT = {
    "camp":  [(34, 35, 10, 6, 1.0), (26, 46, 8, 6, 0.8), (35, 8, 8, 5, 0.9), (20, 38, 9, 5, 0.8),
              (14, 13, 8, 5, 0.7)],
    "hard":  [(34, 35, 7, 4.5, 0.9), (46, 20, 6, 5, 0.8)],
    "clay":  [(25, 50, 7, 5, 0.6)],
    "mulch": [(10, 24, 7, 6, 0.5), (18, 54, 7, 5, 0.5)],
}

NPC_POSITIONS = {
    # the ramp: you pay before you reach the water
    "bootybay_toll_collector": (46, 20),       # Tollkeeper Nizzik
    "bootybay_harbourmaster": (47, 19),        # Harbourmaster Sprocket, tower door
    "bootybay_gate_guard": (37, 7),            # Bruiser Kolk, clifftop gate
    "bootybay_lookout": (11, 14),              # Lookout Minzi, the cape watch
    # the quay
    "bootybay_baron": (33, 52),                # Baron Revilgaz
    "bootybay_baron_aide": (30, 48),           # Aide Fipple
    "bootybay_dockmaster": (41, 30),           # Dockmaster Brek
    "bootybay_crane_hand": (44, 27),           # Crane-Hand Durgo
    "bootybay_shipwright": (19, 40),           # Shipwright Vella
    "bootybay_cartel_factor": (24, 34),        # Factor Weezel - still signs for Ratchet, and says so
    "bootybay_fence": (16, 42),                # The Quiet Man
    "bootybay_bloodsail_captive": (26, 53),    # a Bloodsail nobody has decided what to do with
    "bootybay_troll_pilot": (36, 39),          # Pilot Zan'rek, knows the reef
    "bootybay_street_kid": (33, 32),           # Scrip
    # vendors
    "bootybay_trader": (31, 37),               # Trader Nixxle
    "bootybay_tavern_keeper": (21, 49),        # Keeper Marla
    "bootybay_shipping_clerk": (38, 35),       # Clerk Bexx
    "bootybay_fishmonger": (43, 44),           # Gurgle
    "bootybay_weapon_dealer": (14, 38),        # Dealer Sark
}
FORGE = (18, 36)
EXTRA_NPC_XY = [FORGE]
CHESTS = [(8, 24), (12, 53), (41, 10), (23, 11)]


def dress(L):
    P, B, D, C = L.prop, L.bld, L.dp, L.cp
    z = L.z

    # ---- the boat to Ratchet, at the head of the middle pier -------------------------------------
    z.collision_layer[BOAT[1]][BOAT[0]] = None
    z.set_tile(BOAT[0], BOAT[1], "boat", "interaction")
    L.deco("boat_orc", 67, 36, 8)

    # ---- the clifftop gate and the headland walk --------------------------------------------------
    B("palisade_gatehouse", 31, 7, 8, road_ok=True, nudge=1)
    P("br_signpost", 38, 10, 5)
    C("sea_stack_spire", 58, 9, 11)
    L.deco("sea_stack_spire", 66, 21, 9)
    B("frontier_watchtower", 9, 12, 10)
    C("jungle_banyan", 29, 16, 10)
    C("jungle_banyan", 30, 11, 10)
    C("bamboo_grove", 15, 8, 7)
    C("mossy_jungle_boulder", 25, 7, 4)

    # ---- the ramp: the toll post and the harbourmaster's tower on the knuckle ---------------------
    B("guard_post", 48, 19, 6, nudge=2)
    B("harbor_tower", 50, 16, 10, nudge=2)
    C("signal_tower", 56, 17, 9, nudge=2)
    D("vot_crate_stack", 47, 25, 3)
    P("br_signpost", 44, 22, 5)

    # ---- the quay: the floor of the town, and what stands on it ----------------------------------
    B("the_broken_keel", 21, 47, 9)
    B("trading_post", 32, 40, 6)
    B("bazaar_stall_row", 20, 36, 5)
    B("mixed_trading_post", 14, 35, 6)
    B("ratchet_docks_warehouse", 36, 30, 9, nudge=2, road_ok=True)
    B("supply_cache_shed", 12, 43, 5)
    D("vot_fire_pit", 24, 37, 2, solid=False)
    D("rf_supply_crates", 34, 38, 3)
    D("rf_tool_rack", 17, 34, 3)

    # ---- the lower shelf: the Baron's stair, the cages, the holding yard --------------------------
    B("gazlowes_office", 33, 50, 10, nudge=2)
    B("generic_shack_a", 20, 50, 6)
    B("generic_shack_b", 15, 48, 6)
    D("rf_prison_cage", 24, 54, 5)
    D("vot_crate_stack", 32, 53, 3)
    C("driftwood_pile", 34, 48, 3)

    # ---- the piers: cranes, lanterns, traps, the things a working harbour leaves lying about ------
    for (x, y) in [(48, 24), (54, 24), (59, 24)]:
        L.deco("dock_lantern_post", x, y, 4)
    for (x, y) in [(49, 33), (56, 33), (63, 33)]:
        L.deco("dock_lantern_post", x, y, 4)
    for (x, y) in [(48, 44), (55, 44)]:
        L.deco("dock_lantern_post", x, y, 4)
    for (x, y) in [(44, 28), (44, 41), (44, 47)]:
        L.deco("dock_lantern_post", x, y, 4)
    L.deco("mooring_posts", 52, 36, 3)
    L.deco("mooring_posts", 61, 36, 3)
    L.deco("mooring_posts", 53, 47, 3)
    L.deco("fish_crates_traps", 50, 26, 3)
    L.deco("fish_crates_traps", 66, 37, 3)
    L.deco("fish_crates_traps", 45, 45, 3)
    L.deco("fish_drying_rack", 46, 42, 4)
    L.deco("outrigger_canoe", 47, 48, 4)
    L.deco("rowboat_wreck", 58, 50, 4)

    # ---- the cove's edges: reef, wrecks, and the jungle coming down the south wall ----------------
    L.deco("coral_reef_outcrop", 60, 44, 4)
    L.deco("coral_reef_outcrop", 54, 52, 4)
    C("crab_claw_arch", 40, 53, 6, shore_ok=True)
    C("mangrove_thicket", 38, 50, 6, shore_ok=True)
    C("jungle_banyan", 9, 31, 10)
    C("jungle_banyan", 10, 54, 10)
    C("bamboo_grove", 8, 45, 7)
    C("banana_plant", 19, 31, 5)
    C("hibiscus_bush", 30, 30, 3, solid=False)
    C("hibiscus_bush", 13, 50, 3, solid=False)
    C("tiki_totem", 35, 52, 7)                   # older than the port, and nobody moves it


def build_layout():
    return K.build(sys.modules[__name__])


def generate_booty_bay():
    L = build_layout()
    K.register_baked(L.zone, sys.modules[__name__])
    return L.zone
