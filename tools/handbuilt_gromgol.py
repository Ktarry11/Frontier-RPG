"""
Hand-built Grom'gol (64x56): the Horde's base camp in Northern Stranglethorn.

TOWN ARCHETYPE: AIRHEAD.  Not a town - a beachhead that arrived by air and has not finished unpacking.
Every other settlement in the game grew where it stands; this one was flown in, and the shape says so.
The zeppelin tower is the first thing built and everything else is laid out under it, because it is the
thing that supplies them.  A single palisade ring, one gate north (the berth
stair) and one gate south (the Vine Road), a parade yard under the tower, the war hall and the forge on
the high side, stores and pens on the low side, and the jungle pressing on the wall everywhere else.
(Razor Hill = walled hill fort, Crossroads = avenue cross, Camp Taurajo = tipi ring, Ratchet = harbour;
this is the only one that is a supply line with a fence round it.)

Grom'gol belongs to ORGRIMMAR, not to a new faction - claude/stranglethorn_design.md: "It is a Horde
base camp, and Orgrimmar already owns the Kalimdor Horde zones."  Booty Bay is the one that gets its own
ladder.  So the two doors into the jungle are owned by two different powers, which is a nice accident of
the geography: whichever way you come in, somebody owns the door.

HARD CONTRACTS (world/portal_manager.py)
  portals  (32,4)  -> Zeppelin Tower (the east berth, which was reserved for exactly this)
           (32,53) -> Northern Stranglethorn (54,96)
  arrivals (32,6) and (32,51)
"""
import sys

import numpy as np

from tools import town_kit as K
from tools.handbuilt_central_barrens import _wob

KEY = "gromgol"
NAME = "Grom'gol"
DESC = "A Horde camp flown in over the range, dug into a jungle clearing and holding."
REGION = "Eastern Kingdoms - Stranglethorn"
W, H = 64, 56
BAKED_DIR = "assets/tiles/gromgol/baked"
IS_TOWN = True
BASE_TILE = "grass"
PORTALS = {(32, 4): "Zeppelin Tower", (32, 53): "Northern Stranglethorn"}
ARRIVALS = [(32, 6), (32, 51)]
START = (32, 8)

ROADS = {
    "spine":  ([(32, 3), (32, 12), (31, 20), (32, 28), (33, 38), (32, 46), (32, 54)], 3.6),
    "east":   ([(33, 24), (42, 22), (50, 24), (56, 28)], 2.6),
    "west":   ([(31, 24), (22, 22), (14, 25), (9, 30)], 2.6),
    "pens":   ([(33, 38), (41, 40), (46, 42)], 2.4),
    "stores": ([(31, 38), (21, 41), (13, 45)], 2.4),
}
PLAZA = (32, 24, 7.5, 5.8)

_RS = K.RoadSet(ROADS)
road_dist = _RS.dist

GAPS = [(32, 4, 6, 5), (32, 52, 6, 5)]
POND = (11, 21, 5.0, 3.4)


def paved(gx, gy):
    cx, cy, rx, ry = PLAZA
    r = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
    return (1 - r) * min(rx, ry)


def water_fields(gx, gy):
    """A spring pond in the west quarter - the camp's water, and the only water in it."""
    cx, cy, rx, ry = POND
    r = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
    sh = (1 - r) * min(rx, ry) + 0.5 * _wob(gx, gy)
    return sh, sh - 2.4


def cliff_field(gx, gy):
    """The wall of the clearing: jungle and rock all round, open only at the two gates."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    p = 2.8
    sq = (np.abs(gx - 32.0) / 30.0) ** p + (np.abs(gy - 28.0) / 26.0) ** p
    inside = (1.0 - sq ** (1 / p)) * 14.0
    for (cx, cy, rx, ry) in GAPS:
        d = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
        inside = np.maximum(inside, (1 - d) * min(rx, ry))
    inside = np.maximum(inside, road_dist(gx, gy) + 2.2)
    # two outcrops inside the ring: the high side the war hall sits on
    rock = np.full(gx.shape, -99.0)
    for (cx, cy, rx, ry) in [(52, 12, 6, 4.5), (11, 11, 5, 4)]:
        r = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
        rock = np.maximum(rock, (1 - r) * min(rx, ry))
    return np.maximum(-inside + 1.0 * _wob(gx, gy),
                      np.minimum(rock, -road_dist(gx, gy) - 2.0))


def fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    sh, dp = water_fields(gx, gy)
    return dict(cliff=cliff_field(gx, gy), shallow=sh, deep=dp, deck=np.full(gx.shape, -9.0))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


# ---- painter config -----------------------------------------------------------------------------------
WATER = "lake"
BASE = {"jungle": 0.7, "mulch": 0.45, "clay": 0.3}
PAINT = {
    "camp":  [(32, 24, 13, 10, 1.0), (32, 10, 9, 5, 0.9), (47, 40, 9, 6, 0.8), (17, 43, 8, 5, 0.8),
              (50, 24, 7, 5, 0.7), (13, 27, 7, 5, 0.7)],
    "hard":  [(32, 24, 7, 5.5, 0.9), (32, 8, 6, 4, 0.8)],
    "clay":  [(44, 41, 7, 5, 0.6)],
    "mulch": [(8, 20, 7, 6, 0.5), (56, 48, 7, 5, 0.5)],
}

NPC_POSITIONS = {
    # command, under and around the tower
    "gromgol_commander": (44, 36),            # Overseer Mokra, war hall door
    "gromgol_berth_master": (27, 18),         # Berth-Master Zekka, foot of the tower stair
    "gromgol_signalman": (37, 17),            # Signalman Grut
    "gromgol_scout": (24, 16),                # Scout Hanzo
    "gromgol_quartermaster": (28, 28),        # Quartermaster Ghal
    # the parade yard and the wall
    "gromgol_drillmaster": (36, 28),          # Drillmaster Ukko
    "gromgol_south_sentry": (30, 48),         # Sentry Vrak, south gate
    "gromgol_wounded_runner": (26, 33),       # Runner Teza
    "gromgol_field_medic": (22, 36),          # Field-Medic Sulaa
    # the trades
    "gromgol_smith": (52, 23),                # Smith Dorgun
    "gromgol_beast_handler": (41, 47),        # Beast-Handler Kozza, the pens
    "gromgol_storesman": (16, 44),            # Storesman Pell
    "gromgol_cartographer": (12, 28),         # Mapmaker Ashi
    "gromgol_troll_attache": (44, 26),        # Attaché Zul'jana - Darkspear, and from here
    # vendors
    "gromgol_trader": (34, 32),               # Trader Burg
    "gromgol_provisioner": (20, 41),          # Provisioner Nakka
    "gromgol_weaponsmith": (51, 27),          # Weaponsmith Trag
    "gromgol_herbalist": (10, 30),            # Herbalist Mossa
}
FORGE = (54, 22)
EXTRA_NPC_XY = [FORGE]
CHESTS = [(8, 8), (56, 8), (8, 50), (56, 50)]


def dress(L):
    P, B, D, C = L.prop, L.bld, L.dp, L.cp

    # ---- the berth: the tower, the stair down, the airship riding above it ------------------------
    B("zep_tower_orc", 32, 16, 14, road_ok=True, nudge=0)
    L.deco("zeppelin_orc", 32, 7, 10)
    D("vot_war_banner", 26, 14, 5)
    D("vot_war_banner", 38, 14, 5)
    D("vot_crate_stack", 24, 10, 3)
    D("vot_crate_stack", 41, 10, 3)
    P("br_signpost", 36, 12, 5)
    C("tiki_totem", 20, 8, 7)                    # the trolls got here first; the orcs left it standing

    # ---- the spring: the camp's water, and the only water in it ----------------------------------
    D("vot_reeds", 15, 22, 3, solid=False, shore_ok=True)
    D("vot_reeds", 8, 18, 3, solid=False, shore_ok=True)
    C("mangrove_thicket", 6, 25, 6, shore_ok=True)
    D("vot_spring_boulder", 14, 17, 4)

    # ---- the high side: war hall, forge, weapon racks ---------------------------------------------
    B("clan_hall", 44, 33, 11)
    B("smithy", 56, 20, 8)
    D("vot_training_dummy", 46, 30, 4)
    D("vot_training_dummy", 49, 31, 4)
    D("vot_archery_target", 56, 32, 4)
    D("rf_tool_rack", 58, 25, 3)
    D("vot_war_drum", 42, 30, 3)

    # ---- the parade yard: fire, totem, the drillmaster's ground -----------------------------------
    D("vot_fire_pit", 32, 24, 3, solid=False, road_ok=True)
    D("vot_totem_pole", 32, 20, 9, road_ok=True)
    D("vot_war_banner", 28, 26, 5)
    D("vot_war_banner", 36, 26, 5)

    # ---- the low side: stores, provisioner, the medic's tent --------------------------------------
    B("supply_depot", 14, 42, 8)
    B("generic_tent_a", 21, 38, 5)
    B("generic_tent_b", 25, 44, 5)
    B("plain_orc_house_a", 17, 28, 6)
    B("plain_orc_house_b", 11, 33, 6)
    D("vot_crate_stack", 18, 46, 3)
    D("vot_crate_stack", 10, 38, 3)
    D("vot_hide_rack", 24, 40, 3)

    # ---- the pens: raptors the camp has stopped pretending it has not tamed ------------------------
    for (x, y) in [(44, 45), (46, 45), (48, 45), (50, 45), (52, 45), (54, 45), (54, 47), (54, 49),
                   (52, 49), (50, 49), (48, 49), (46, 49), (44, 49), (44, 47)]:
        D("vot_palisade", x, y, 3, solid=True, nudge=0)
    P("br_raptor_nest", 49, 47, 4)
    P("br_hitching_trough", 42, 44, 3)
    B("generic_shack_a", 56, 41, 6)

    # ---- the palisade ring itself: posts on the inside of the wall, gates marked -------------------
    for (x, y) in [(22, 6), (42, 6), (6, 22), (6, 34), (58, 22), (58, 34), (20, 50), (44, 50)]:
        D("vot_palisade", x, y, 4, solid=False, nudge=1)
    B("palisade_gatehouse", 26, 52, 8, road_ok=True, nudge=1)
    B("watchtower", 38, 47, 10, nudge=3)
    D("vot_war_banner", 30, 50, 5)
    C("troll_war_banner", 38, 48, 5)

    # ---- what the wall is holding back ------------------------------------------------------------
    for (x, y) in [(10, 16), (53, 11), (10, 42), (52, 42), (18, 49), (45, 52), (8, 32), (56, 35)]:
        C("jungle_banyan", x, y, 10)
    for (x, y) in [(15, 13), (58, 29), (15, 47), (49, 52), (18, 9), (46, 8)]:
        C("bamboo_grove", x, y, 7)
    for (x, y) in [(13, 35), (50, 35), (26, 7), (38, 52)]:
        C("hibiscus_bush", x, y, 3, solid=False)
    for (x, y) in [(7, 25), (57, 26), (19, 48), (47, 51)]:
        C("mossy_jungle_boulder", x, y, 4)
    for (x, y) in [(23, 31), (41, 35), (15, 20), (53, 28)]:
        C("banana_plant", x, y, 5)


def build_layout():
    return K.build(sys.modules[__name__])


def generate_gromgol():
    L = build_layout()
    K.register_baked(L.zone, sys.modules[__name__])
    return L.zone
