"""
Hand-built Camp Taurajo (64x56): the tauren waystation on the southern Barrens road.

TOWN ARCHETYPE: RING CAMP.  No walls and no grid: a loose circle of hide tipis round a great fire and a
carved totem, the lodge and the Elder's roundhouse behind it to the north, a kodo corral against the
rocks in the east, a spring pond with the healer and the totem-carver in the south-west.  The only
road is the old trail between the two gates - N (32,2) to Central Barrens, S (32,53) to Southern
Barrens - bending round the ring.  (Razor Hill = walled hill fort, Crossroads = avenue cross, Ratchet =
harbour; this one reads as a camp, not a town.)

HARD CONTRACTS (world/portal_manager.py)
  portals  (32,2) -> Central Barrens (150,296)   arrival (32,0)
           (32,53) -> Southern Barrens (130,2)   arrival (32,51)
  NPC ids  referenced by data/quests/*.json; positions below are written back by tools/sync_barrens_town_npcs.py
"""
import math
import sys

import numpy as np

from tools import town_kit as K
from tools.handbuilt_central_barrens import _wob, blob

KEY = "camp_taurajo"
NAME = "Camp Taurajo"
DESC = "A tauren hunting camp of hide tents and drying racks, guarding the southern road."
REGION = "The Barrens"
W, H = 64, 56
BAKED_DIR = "assets/tiles/camp_taurajo/baked"
PORTALS = {(32, 2): "Central Barrens", (32, 53): "Southern Barrens"}
ARRIVALS = [(32, 0), (32, 51)]
START = (32, 10)

ROADS = {
    "trail_n": ([(32, 1), (34, 9), (31, 17), (30, 24)], 3.2),
    "trail_s": ([(33, 35), (35, 42), (32, 48), (32, 54)], 3.2),
    "west":   ([(25, 29), (18, 28), (12, 28)], 2.0),
    "east":   ([(39, 29), (46, 28), (52, 28)], 2.0),
    "sw":     ([(27, 33), (22, 39), (19, 45)], 1.9),
    "se":     ([(37, 33), (41, 40), (44, 46)], 1.9),
    "ne":     ([(35, 22), (41, 17), (45, 15)], 1.9),
    "nw":     ([(28, 22), (23, 18), (19, 16)], 1.9),
}
PLAZA = (32, 29, 7.0, 5.6)

_RS = K.RoadSet(ROADS)
road_dist = _RS.dist

RIDGES = [([(46, 50), (52, 47), (58, 46), (61, 42)], 2.2),     # windbreak behind the corral
          ([(48, 6), (54, 8), (60, 12)], 2.0)]                 # north-east shoulder
GAPS = [(32, 3, 6, 5), (32, 52, 6, 5)]
POND = (16, 43, 5.5, 3.6, 0, 0.9)

_RIDGE_TREES = {}


def paved(gx, gy):
    cx, cy, rx, ry = PLAZA
    r = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
    return (1 - r) * min(rx, ry)


def _ridge(pts, hw, gx, gy):
    from scipy.spatial import cKDTree
    key = id(pts)
    if key not in _RIDGE_TREES:
        from tools.terrain_painter import Painter
        _RIDGE_TREES[key] = cKDTree(Painter.spline(pts))
    tree = _RIDGE_TREES[key]
    d, idx = tree.query(np.stack([gx.ravel(), gy.ravel()], 1))
    t = idx / max(1, tree.n - 1)
    taper = 0.30 + 0.70 * np.sin(np.pi * t) ** 0.6
    return (hw * taper).reshape(gx.shape) + 0.7 * _wob(gx, gy) - d.reshape(gx.shape)


def cliff_field(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    p = 2.7
    sq = (np.abs(gx - 32.0) / 30.5) ** p + (np.abs(gy - 28.0) / 26.5) ** p
    inside = (1.0 - sq ** (1 / p)) * 13.0
    for (cx, cy, rx, ry) in GAPS:
        d = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
        inside = np.maximum(inside, (1 - d) * min(rx, ry))
    inside = np.maximum(inside, road_dist(gx, gy) + 2.0)
    rock = np.full(gx.shape, -99.0)
    for (pts, hw) in RIDGES:
        rock = np.maximum(rock, _ridge(pts, hw, gx, gy))
    out = np.maximum(-inside + 1.0 * _wob(gx, gy), np.minimum(rock, -road_dist(gx, gy) - 2.0))
    return out


def water_fields(gx, gy):
    cx, cy, rx, ry, rot, ph = POND
    s = blob(gx, gy, cx, cy, rx, ry, rot, ph)
    return s, s - 1.9


def fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    sh, dp = water_fields(gx, gy)
    return dict(cliff=cliff_field(gx, gy), shallow=sh, deep=dp, deck=np.full(gx.shape, -9.0))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


# ---- painter config -----------------------------------------------------------------------------------
WATER = "lake"
BASE = {"gold": 0.7, "tall": 0.55, "sparse": 0.35}
PAINT = {
    "camp":  [(32, 29, 12, 9.5, 1.0), (42, 16, 9, 4.5, 0.8), (56, 36, 7, 5.5, 0.9), (44, 47, 7, 4, 0.8),
              (12, 27, 6, 4, 0.7), (20, 15, 7, 4, 0.7)],
    "hard":  [(32, 29, 6.5, 5.0, 0.9)],
    "dust":  [(56, 20, 6, 5, 0.5)],
    "bone":  [(57, 33, 4, 3, 0.5)],
    "tall":  [(20, 44, 8, 6, 0.6), (50, 10, 8, 6, 0.5)],
}

NPC_POSITIONS = {
    "taurajo_guard": (30, 6),                 # Camp Sentry, north gate
    "taurajo_elder": (20, 19),                # Elder Longtread, roundhouse door
    "taurajo_hunter_1": (49, 18),             # Windrunner Kala
    "taurajo_totem_carver": (14, 23),         # Carver Ahonen
    "taurajo_hide_tanner": (11, 31),          # Tanner Mosswalker
    "taurajo_drum_keeper": (36, 31),          # Drum-Keeper Rohan, by the fire
    "taurajo_kodo_wrangler": (50, 28),        # Wrangler Tull, corral gate
    "taurajo_young_calf": (28, 33),           # Little Rundu
    "taurajo_warband_scout": (38, 9),         # Scout Ashhoof
    "taurajo_orc_liaison": (44, 43),          # Liaison Grukdar
    "taurajo_healer": (22, 44),               # Earthsong Mara, by the spring
    # vendors
    "taurajo_quartermaster": (39, 25),        # Hela Windhoof
    "taurajo_hide_trader": (10, 36),          # Trader Bloodhorn
    "taurajo_provisioner": (40, 45),          # Grainkeeper Yura
    "taurajo_totem_crafter": (18, 38),        # Spiritcarver Dennok
    "taurajo_beast_trainer": (47, 36),        # Beastcaller Nira
}
CHESTS = [(8, 12), (56, 12), (52, 49), (6, 30)]


def dress(L):
    P, B, D = L.prop, L.bld, L.dp
    # ---- north gate: tusk gate over the trail, totems, sentry post
    P("br_kodo_tusk_gate", 32, 9, 7, solid=False, road_ok=True)
    P("br_tauren_totem", 26, 6, 7)
    P("br_tauren_totem", 38, 6, 7)
    B("watchers_perch", 26, 12, 9)
    P("br_signpost", 35, 13, 5)
    # ---- the lodge court (north): lodge + elder's roundhouse
    B("taurajo_lodge", 43, 16, 10)
    B("elders_roundhouse", 19, 16, 8)
    D("vot_hide_rack", 49, 14, 3)
    D("vot_war_banner", 36, 17, 5)
    D("vot_war_banner", 38, 17, 5)
    # ---- the great fire and the ring of tipis
    D("vot_fire_pit", 32, 29, 3, solid=False, road_ok=True)
    # KYLE, [5]: "Camp Taurajo is overloaded with props." It had 81 on a 64x56 map: ten tipis
    # in a ring with an eleven-tile totem in the middle of them, totems in pairs at both
    # gates and in the carver's yard (several drawn through a tipi), and scatter on every
    # patch of grass. Thinned to what tells you where you are: six tipis round the fire, one
    # totem by it, one pair at the north gate, and about half the scatter.
    P("br_tauren_totem", 32, 24, 8, road_ok=True)
    D("vot_war_drum", 28, 30, 3)
    for k in range(6):
        a = math.radians(30 + 60 * k)
        P("br_tauren_tipi", int(round(32 + 17 * math.cos(a))), int(round(29 + 12 * math.sin(a))), 7, nudge=3)
    # ---- west: tanner, carver, trader. Tauren buildings (Kyle, 14 Nov 2026: "do proper art in the
    # proper towns"); these were the generic Valley of Trials huts.
    B("tau_tannery", 9, 30, 7, nudge=2)
    B("tau_carver_shop", 11, 22, 6, nudge=2)
    B("tau_trading_post", 7, 37, 6, nudge=2)
    D("vot_hide_rack", 14, 33, 3)
    # ---- south-west: the spring - healer's tent, the totem-carver's yard
    B("tau_herb_hut", 24, 47, 5, nudge=2)        # the healer
    P("br_tauren_totem", 15, 43, 7)
    D("vot_trail_cairn", 24, 41, 3)
    for (x, y) in [(9, 47)]:
        D("vot_thornbush", x, y, 2, solid=False)
    # ---- east: the kodo corral, stables, beast trainer
    B("taurajo_stables", 56, 25, 7)
    for (x, y) in [(50, 33), (52, 33), (54, 33), (56, 33), (58, 33), (58, 35), (58, 37), (58, 39),
                   (58, 41), (56, 41), (54, 41), (52, 41), (50, 41), (50, 39), (50, 37), (50, 35)]:
        D("vot_palisade", x, y, 3, solid=True, nudge=0)
    P("br_hitching_trough", 53, 30, 3)
    # ---- south-east: quartermaster, granary, the orc liaison
    B("tau_storehouse", 38, 24, 5, nudge=2)      # the quartermaster
    B("taurajo_granary", 40, 50, 8)
    B("plain_orc_house_a", 46, 45, 5)
    D("vot_crate_stack", 36, 48, 3)
    D("vot_crate_stack", 44, 50, 3)
    P("br_caravan_wagon", 41, 38, 4)
    # ---- south gate: the Southern Barrens signpost (the gate itself is the totem gate
    # world/exit_frames.py stands over the door)
    P("br_signpost", 36, 46, 5)
    P("br_kodo_skeleton", 25, 52, 4)
    P("br_dead_tree_vulture", 40, 52, 7)
    # ---- plains scatter: acacia, scrub, boulders, tufts
    for (x, y) in [(8, 8), (57, 9), (9, 52), (53, 20), (24, 37)]:
        P("br_umbrella_acacia" if (x + y) % 3 else "acacia_tree", x, y, 7)
    for (x, y) in [(15, 10), (47, 9), (54, 45), (6, 20), (16, 52)]:
        P("br_thorn_scrub" if (x * y) % 3 else "br_agave_spike", x, y, 3)
    for (x, y) in [(8, 41), (57, 14)]:
        P("br_sandstone_boulders", x, y, 4)
    for (x, y) in [(14, 25), (42, 22), (30, 38), (12, 47), (46, 12)]:
        P("br_golden_grass_tuft", x, y, 2, solid=False)


def build_layout():
    return K.build(sys.modules[__name__])


def generate_camp_taurajo():
    L = build_layout()
    K.register_baked(L.zone, sys.modules[__name__])
    return L.zone
