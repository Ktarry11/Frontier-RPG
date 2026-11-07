"""
Hand-built Ratchet (70x60): the goblin free port on the Barrens' east coast.

TOWN ARCHETYPE: CRESCENT HARBOUR WITH A TERRACED BLUFF.  The sea bites a crescent bay out of the east
side; a long boardwalk promenade follows the waterline and three piers run out over the water (the
middle one ends in a platform with the boat).  Behind the harbour the land climbs by a scarp to a goblin
upper town - Gazlowe's office and the scrapyard - reached by two ramps; a headland to the north-east
carries the harbour tower and the signal light.  (Razor Hill = hill fort, Crossroads = avenue cross,
Camp Taurajo = tipi ring; this is the only waterfront.)

HARD CONTRACTS (world/portal_manager.py)
  portal   (2,30) -> Central Barrens (285,270);  arrival (2,28)
  boat     interaction tile at (64,30) (flavour; zone_manager has no link for it)
  NPC ids  referenced by data/quests/*.json; positions are written back by tools/sync_barrens_town_npcs.py
"""
import sys

import numpy as np

from tools import town_kit as K
from tools.handbuilt_central_barrens import _wob, _smooth, _gauss

KEY = "ratchet"
NAME = "Ratchet"
DESC = "A goblin free port. Neutral ground, inflated prices, and a boat to anywhere."
REGION = "The Barrens"
W, H = 70, 60
BAKED_DIR = "assets/tiles/ratchet/baked"
PORTALS = {(2, 30): "Central Barrens"}
ARRIVALS = [(2, 28)]
START = (6, 30)
BOAT = (64, 30)

ROADS = {
    "main":    ([(1, 30), (10, 30), (20, 31), (30, 30), (41, 30)], 3.6),
    "gazlowe": ([(27, 30), (26, 24), (28, 18), (30, 12)], 3.0),
    "scrap":   ([(14, 30), (12, 24), (11, 18), (10, 14)], 2.6),
    "keel":    ([(16, 30), (15, 35), (14, 40)], 2.4),
    "south":   ([(32, 30), (34, 38), (36, 46), (36, 53)], 2.8),
    "n_pier":  ([(30, 28), (36, 24), (44, 20.4), (47, 20)], 2.6),
    "s_pier":  ([(34, 36), (40, 40), (47, 42)], 2.6),
    "head":    ([(30, 12), (40, 10), (50, 10), (57, 10)], 2.4),
}
PLAZA = (31, 31, 6.5, 4.8)

# decks laid over water: (x0, x1, y0, y1)
DECKS = [
    (46.0, 61.0, 18.6, 21.4),        # north pier
    (41.0, 66.0, 28.8, 31.2),        # main pier
    (60.0, 69.0, 26.4, 33.6),        # main pier head platform (boat at 64,30)
    (46.0, 58.0, 40.6, 43.4),        # south pier
    (41.5, 44.5, 17.0, 44.0),        # promenade boardwalk
]

_RS = K.RoadSet(ROADS)
road_dist = _RS.dist
_RIDGE_TREES = {}
RIDGES = [([(3, 20), (12, 22), (21, 19.5), (29, 22), (36, 18), (41, 15)], 3.2)]      # the goblin bluff scarp
GAPS = [(2, 30, 4, 5), (30, 12, 5, 4)]


def paved(gx, gy):
    cx, cy, rx, ry = PLAZA
    r = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
    return (1 - r) * min(rx, ry)


def shore(gy):
    """x of the waterline.  North headland and south spit reach out, the bay bites in."""
    gy = np.asarray(gy, float)
    return (47.0 + 17.0 * (1 - _smooth(12, 22, gy)) + 11.0 * _smooth(40, 52, gy)
            - 4.0 * _gauss(gy, 30, 9) + 1.4 * np.sin(0.45 * gy + 1.0) + 0.8 * np.sin(0.93 * gy))


def water_fields(gx, gy):
    sea = gx - shore(gy)
    return sea, sea - 3.6


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
    west = (1.8 + 0.9 * np.sin(0.21 * gy + 0.4)) - gx
    north = (3.2 + 1.2 * np.sin(0.13 * gx + 1.0) + 0.7 * np.sin(0.37 * gx)) - gy
    south = gy - (56.6 - 1.2 * np.sin(0.15 * gx + 2.0) - 0.7 * np.sin(0.41 * gx))
    out = np.maximum(out, np.maximum(west, np.maximum(north, south)))
    # a rocky knuckle at the tip of the north headland and one on the south spit
    for (cx, cy, rx, ry) in [(64.5, 6.5, 4.5, 3.2), (57.5, 55.0, 4.0, 2.8)]:
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


# ---- painter config ------------------------------------------------------------------------------------
WATER = "sea"
BASE = {"hard": 0.6, "cracked": 0.5, "dust": 0.35}
PAINT = {
    "camp":  [(31, 31, 9, 7, 1.0), (30, 14, 8, 4.5, 0.9), (11, 13, 7, 5, 0.9), (36, 25, 8, 5, 0.7),
              (16, 38, 7, 5, 0.7), (56, 10, 6, 4, 0.6)],
    "hard":  [(12, 30, 10, 3, 0.7), (38, 36, 6, 4, 0.7), (30, 12, 6, 4, 0.8)],
    "dust":  [(8, 48, 9, 6, 0.7), (24, 52, 8, 4, 0.6)],
    "gold":  [(6, 8, 6, 4, 0.5), (22, 8, 8, 4, 0.5)],
    "salt":  [(45, 52, 5, 3, 0.4)],
}

NPC_POSITIONS = {
    "ratchet_gazlowe": (30, 16),              # office door
    "ratchet_dock_worker": (50, 20),          # Grizzik, north pier
    "ratchet_sailor": (53, 30),               # Salty Pete, main pier
    "ratchet_merchant": (22, 39),             # Fizzle Brassbolt
    "ratchet_fishmonger": (42, 46),           # Gribble, by the drying racks
    "ratchet_smuggler": (7, 24),              # Fintan, back alley
    "ratchet_dock_laborer": (38, 27),         # Hask, warehouse
    "ratchet_bounty_hunter": (6, 38),         # Drask
    "ratchet_drunk_sailor": (19, 34),         # Barnacle Bill, outside the inn
    "ratchet_customs_officer": (6, 28),       # Prynn, at the gate
    "ratchet_goblin_child": (26, 33),         # Little Gribs
    "ratchet_human_expat": (20, 47),          # Delia Thorne
    "ratchet_troll_dockhand": (50, 42),       # Zulraka, south pier
    # vendors
    "ratchet_trader": (25, 43),               # Nixx
    "ratchet_dockmaster": (45, 24),           # Brindle
    "ratchet_shipping_trader": (35, 33),      # Cargo Master Blix
    "ratchet_explosives_dealer": (9, 18),     # Fuzzek Boomwick, by the scrapyard
    "ratchet_black_market_fence": (5, 21),    # The Fence
    "ratchet_tavern_keeper": (16, 36),        # Molka
}
RECRUITS = {"silas_rogue": (33, 34)}
FORGE = (13, 17)
EXTRA_NPC_XY = list(RECRUITS.values()) + [FORGE]
CHESTS = [(6, 52), (62, 10), (28, 53), (20, 8)]


def dress(L):
    P, B, D, C = L.prop, L.bld, L.dp, L.cp
    z = L.z
    # ---- the boat (flavour interaction tile at the end of the main pier)
    z.collision_layer[BOAT[1]][BOAT[0]] = None
    z.set_tile(BOAT[0], BOAT[1], "boat", "interaction")
    # ---- gate: customs post just inside the portal, signpost, crates
    B("guard_post", 7, 33, 6)
    P("br_signpost", 7, 27, 5)
    D("vot_crate_stack", 4, 35, 3)
    # ---- upper town on the bluff: Gazlowe, scrapyard, forge, houses
    B("gazlowes_office", 30, 14, 10, road_ok=True, nudge=0)
    B("scrapyard_workshop", 10, 12, 8)
    D("rf_tool_rack", 15, 14, 3)
    D("rf_ore_cart", 6, 16, 3)
    D("rf_supply_crates", 18, 16, 3)
    B("generic_house_a", 20, 13, 7)
    B("generic_shack_a", 6, 14, 5)
    B("generic_house_b", 38, 11, 6)
    B("generic_shack_b", 24, 11, 5)
    P("br_signpost", 29, 20, 5)
    # ---- the headland: harbour tower and signal light
    B("harbor_tower", 51, 13, 9, road_ok=True)
    C("signal_tower", 62, 12, 9, nudge=1)
    D("rf_supply_crates", 46, 14, 3)
    # ---- lower town: plaza, bazaar, inn, trading post
    D("vot_war_drum", 31, 29, 3)
    B("bazaar_stall_row", 25, 37, 5)
    B("the_broken_keel", 15, 41, 9)
    B("trading_post", 24, 47, 6)
    B("generic_hut_a", 8, 41, 6)
    B("generic_hut_b", 9, 50, 6)
    B("plain_orc_house_b", 29, 51, 5)
    B("generic_tent_a", 4, 46, 5)
    B("supply_cache_shed", 39, 39, 5)
    D("vot_fire_pit", 20, 36, 2, solid=False)
    D("rf_supply_crates", 33, 36, 3)
    # ---- the waterfront: warehouse on the north pier road, drying racks, wrecks
    B("ratchet_docks_warehouse", 39, 24, 9, nudge=1, road_ok=True)
    C("fish_drying_rack", 41, 49, 4, nudge=2)
    C("fish_crates_traps", 37, 45, 3)
    C("rowboat_wreck", 52, 50, 4, shore_ok=True)
    C("driftwood_pile", 47, 38, 3, shore_ok=True)
    C("driftwood_pile", 46, 25, 3, shore_ok=True)
    C("outrigger_canoe", 56, 54, 4, shore_ok=True)
    # ---- dock furniture (non-solid, over the decks)
    for (x, y) in [(48, 18), (54, 18), (59, 18)]:
        L.deco("dock_lantern_post", x, y, 4)
    for (x, y) in [(48, 29), (55, 29), (62, 29)]:
        L.deco("dock_lantern_post", x, y, 4)
    for (x, y) in [(48, 39), (55, 39)]:
        L.deco("dock_lantern_post", x, y, 4)
    L.deco("mooring_posts", 52, 32, 3)
    L.deco("mooring_posts", 60, 32, 3)
    L.deco("fish_crates_traps", 50, 21, 3)
    L.deco("fish_crates_traps", 66, 33, 3)
    L.deco("mooring_posts", 54, 44, 3)
    L.deco("fish_crates_traps", 43, 36, 3)
    # ---- bridges' worth of planking is the deck field itself; scatter on the bluff and spit
    for (x, y) in [(4, 5), (36, 6), (16, 20), (48, 52), (10, 56), (32, 55)]:
        P("br_thorn_scrub" if (x * y) % 3 else "br_agave_spike", x, y, 3)
    for (x, y) in [(6, 53), (44, 14), (26, 20)]:
        P("br_sandstone_boulders", x, y, 4)
    P("br_dead_tree_vulture", 5, 44, 7)
    P("br_tumbleweed_bones", 43, 52, 3)
    for (x, y) in [(8, 26), (14, 24), (20, 52), (30, 8), (46, 12), (12, 44)]:
        P("br_golden_grass_tuft", x, y, 2, solid=False)


def build_layout():
    return K.build(sys.modules[__name__])


def generate_ratchet():
    L = build_layout()
    K.register_baked(L.zone, sys.modules[__name__])
    return L.zone
