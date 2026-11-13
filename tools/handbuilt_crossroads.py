"""
Hand-built Crossroads (70x70): the Barrens' roadside trade hub.

TOWN ARCHETYPE: PLUS-SHAPED AVENUE TOWN.  Two broad roads cross at a paved round plaza that holds the
iconic Crossroads watchtower.  The south avenue runs in from the portal gate; the north avenue ends at
the Town Hall steps (Sergra Darkthorn); the west and east avenues end at barred caravan gatehouses
(the roads Central Barrens' trade routes arrive on).  Four quarters: NW garrison + stables, NE market
+ depot, SW inn + smithy + fletcher, SE alchemist, well and the orc-and-goblin camp.  (Razor Hill is a
walled hilltop with a single spine; Orgrimmar is a capital - this one is an open cross.)

Same recipe as Razor Hill / Central Barrens (claude/zone_perfection_playbook.md): this module owns the
tile data + landform fields; tools/bake_barrens_towns.py paints from the same fields.

HARD CONTRACTS (world/portal_manager.py)
  portal   (35,65) -> Central Barrens (150,150);  arrival (35,63)
  NPC ids  referenced by data/quests/*.json; positions below are written back by tools/sync_barrens_town_npcs.py
"""
import sys

import numpy as np

from tools import town_kit as K
from tools.handbuilt_central_barrens import _wob

KEY = "crossroads"
NAME = "Crossroads"
DESC = "The Crossroads. Every road in the Barrens meets here."
REGION = "The Barrens"
W, H = 70, 70
BAKED_DIR = "assets/tiles/crossroads/baked"
PORTALS = {(35, 65): "Central Barrens"}
ARRIVALS = [(35, 63)]
START = (35, 62)

ROADS = {
    "south": ([(35, 66), (35, 60), (35, 52), (35, 43)], 3.8),
    "north": ([(35, 27), (35, 22), (35, 17)], 3.8),
    "west":  ([(7, 35), (14, 35), (22, 34.6), (28, 35)], 3.8),
    "east":  ([(42, 35), (48, 35.4), (56, 35), (63, 35)], 3.8),
    "nw":    ([(31, 29), (26, 25), (19, 22)], 2.2),
    "ne":    ([(39, 29), (45, 25), (52, 22)], 2.2),
    "sw":    ([(31, 41), (26, 46), (20, 49)], 2.2),
    "se":    ([(39, 41), (45, 46), (52, 49)], 2.2),
}
PLAZA = (35, 35, 8.2, 6.8)         # paved round plaza (cx, cy, rx, ry)

_RS = K.RoadSet(ROADS)
road_dist = _RS.dist


def paved(gx, gy):
    cx, cy, rx, ry = PLAZA
    r = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
    return (1 - r) * min(rx, ry)


def cliff_field(gx, gy):
    """>0 inside rock.  A superellipse clearing with a wobbly rim; roads keep a clear corridor."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    p = 3.4
    sq = (np.abs(gx - 35.0) / 31.5) ** p + (np.abs(gy - 35.0) / 30.5) ** p
    inside = (1.0 - sq ** (1 / p)) * 15.0
    inside = np.maximum(inside, road_dist(gx, gy) + 2.0)
    inside = inside + 1.0 * _wob(gx, gy)
    return -inside


def fields(gx, gy):
    gx = np.asarray(gx, float)
    return dict(cliff=cliff_field(gx, gy), shallow=np.full(gx.shape, -99.0), deep=np.full(gx.shape, -99.0),
                deck=np.full(gx.shape, -9.0))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


# ---- painter config (read by tools/bake_barrens_towns.py) ----------------------------------------
WATER = None
BASE = {"cracked": 0.55, "sparse": 0.45, "hard": 0.35}          # material -> weight of its noise patches
PAINT = {                                                       # material -> [(cx, cy, rx, ry, strength)]
    "camp":  [(35, 35, 9.5, 8.0, 1.0), (35, 16, 12, 5, 0.8), (22, 48, 6, 4, 0.7), (56, 50, 8, 5, 0.7),
              (12, 28, 7, 5, 0.7), (50, 24, 8, 5, 0.6)],
    "hard":  [(35, 35, 7.0, 5.8, 1.0), (50, 28, 8, 5, 0.7), (35, 12, 10, 4, 0.7)],
    "dust":  [(10, 55, 10, 6, 0.6), (60, 12, 8, 6, 0.6)],
    "bone":  [(58, 58, 5, 4, 0.5)],
    "thorn": [(8, 10, 8, 6, 0.6), (62, 62, 7, 5, 0.6)],
    "tall":  [(55, 60, 7, 4, 0.5)],
}

# ---- NPC spots -----------------------------------------------------------------------------------
NPC_POSITIONS = {
    "crossroads_sergra": (35, 19),               # Town Hall steps
    "crossroads_guard_1": (31, 61),              # south gate
    "crossroads_caravan_guard": (21, 26),        # guard post
    "crossroads_quartermaster": (53, 21),        # supply depot
    "crossroads_runner": (40, 32),               # plaza
    "crossroads_bounty_reader": (30, 34),        # plaza notice-post
    "crossroads_retired_warrior": (24, 51),      # outside the inn
    "crossroads_goblin_peddler": (56, 32),       # bazaar
    "crossroads_beltelf_envoy": (47, 40),
    "crossroads_human_traveler": (30, 55),
    "crossroads_child": (39, 43),
    "crossroads_traveler": (47, 53),
    # vendors
    "crossroads_provisioner": (57, 38),
    "crossroads_alchemist": (55, 47),
    "crossroads_general_goods": (50, 28),
    "crossroads_weaponsmith": (14, 44),
    "crossroads_stablemaster": (13, 31),
    "crossroads_fletcher": (17, 54),
}
FORGE = (11, 46)
EXTRA_NPC_XY = [FORGE]
CHESTS = [(8, 60), (58, 9), (64, 56), (6, 12)]


def dress(L):
    P, B, D = L.prop, L.bld, L.dp
    # ---- south gate: palisade gatehouse over the approach, tusk gate, tauren totems
    B("palisade_gatehouse", 35, 59, 7, solid=False, road_ok=True, nudge=0)
    B("watchtower", 27, 59, 9, nudge=1)
    B("watchtower", 43, 59, 9, nudge=1)
    P("br_signpost", 38, 62, 5)
    P("br_caravan_wagon", 28, 63, 4)
    P("br_hitching_trough", 42, 63, 3)
    for x in (22, 25, 45, 48):
        D("vot_palisade", x, 60, 3, solid=True, nudge=1)
    # ---- west and east gatehouses: the trade roads arrive here, gates barred (the zone's only exit is south)
    B("palisade_gatehouse", 7, 39, 7, solid=True, road_ok=True, allow_overlap=True, nudge=0)
    B("palisade_gatehouse", 63, 39, 7, solid=True, road_ok=True, allow_overlap=True, nudge=0)
    P("br_signpost", 13, 38, 5)
    P("br_signpost", 57, 38, 5)
    # ---- the iconic Crossroads watchtower, centre of the plaza
    P("br_crossroads_watchtower", 35, 36, 13, solid="core", fraction=0.25, nudge=0, road_ok=True)
    for (x, y) in [(28, 38), (43, 31), (29, 30), (42, 40)]:
        P("br_signpost" if (x + y) % 2 else "br_hitching_trough", x, y, 4)
    P("br_caravan_wagon", 27, 33, 4)
    P("br_caravan_wagon", 44, 37, 4)
    D("vot_war_banner", 31, 34, 5)
    D("vot_war_banner", 39, 34, 5)
    # ---- north: the Town Hall at the head of the avenue, towers and barracks flank it
    B("crossroads_town_hall", 35, 15, 10, solid="core", fraction=0.5, nudge=0, road_ok=True)
    B("watchtower", 25, 14, 9, nudge=1)
    B("watchtower", 45, 14, 9, nudge=1)
    B("frontier_barracks", 55, 14, 6)
    D("vot_training_dummy", 52, 19, 3)
    D("vot_archery_target", 58, 20, 3)
    P("br_tauren_totem", 29, 20, 7)
    P("br_tauren_totem", 41, 20, 7)
    # ---- NW: guard post, stables, corral
    B("guard_post", 19, 27, 6)
    B("crossroads_stable", 12, 35, 7)
    D("vot_palisade", 11, 39, 3, solid=True)
    D("vot_palisade", 15, 39, 3, solid=True)
    P("br_hitching_trough", 17, 32, 3)
    P("br_caravan_wagon", 22, 21, 4)
    D("vot_hide_rack", 16, 22, 3)
    # ---- NE: market and the supply depot
    B("mixed_trading_post", 50, 31, 6)
    B("bazaar_stall_row", 61, 31, 5)
    B("supply_depot", 53, 25, 6)
    D("vot_crate_stack", 46, 28, 3)
    D("vot_crate_stack", 61, 28, 3)
    B("generic_tent_b", 62, 22, 5)                   # goblin peddler's pitch
    D("vot_fire_pit", 56, 31, 2, solid=False)
    # ---- SW: the inn, smithy and fletcher
    B("crossroads_inn", 22, 47, 9)
    B("smithy", 13, 48, 6)
    D("rf_tool_rack", 9, 49, 3)
    D("vot_crate_stack", 17, 50, 3)
    B("generic_shack_a", 16, 58, 5)
    D("vot_fire_pit", 28, 50, 2, solid=False)
    D("vot_hide_rack", 28, 55, 3)
    P("br_hitching_trough", 26, 44, 3)
    # ---- SE: alchemist, well, the orc-and-goblin camp
    B("shamans_hut", 56, 52, 6)
    B("well_house", 45, 44, 5)
    B("generic_tent_a", 50, 57, 5)
    B("plain_orc_house_a", 60, 60, 5)
    D("vot_broken_cart", 44, 54, 3)
    D("vot_fire_pit", 54, 58, 2, solid=False)
    P("br_umbrella_acacia", 42, 51, 7)
    # ---- the scatter a roadside hub has: thorn, cactus, bones, boulders in the rim
    for (x, y) in [(7, 8), (62, 8), (6, 60), (63, 63), (9, 22), (60, 44), (36, 8), (12, 16)]:
        P("br_thorn_scrub" if (x * y) % 3 else "br_agave_spike", x, y, 3)
    for (x, y) in [(7, 25), (63, 18), (8, 52), (61, 54)]:
        P("br_sandstone_boulders", x, y, 4)
    P("br_dead_tree_vulture", 8, 14, 7)
    P("br_dead_tree_vulture", 63, 48, 7)
    P("br_tumbleweed_bones", 40, 58, 3)
    for (x, y) in [(15, 18), (46, 20), (30, 63), (56, 56), (10, 41), (50, 48), (20, 40), (40, 24)]:
        P("br_golden_grass_tuft", x, y, 2, solid=False)


def build_layout():
    return K.build(sys.modules[__name__])


def generate_crossroads():
    L = build_layout()
    K.register_baked(L.zone, sys.modules[__name__])
    return L.zone
