"""
Hand-built Grom'gol (64x56): the Horde's base camp in Northern Stranglethorn.

TOWN ARCHETYPE: AIRHEAD.  Not a town - a literal beachhead. It arrived by air, it is dug in on the
west shore of the jungle, and it has not finished unpacking.
Every other settlement in the game grew where it stands; this one was flown in, and the shape says so.
The zeppelin tower is the first thing built and everything else is laid out under it, because it is the
thing that supplies them.  A single palisade ring, one gate north (the berth
stair) and one gate south (the Vine Road), a parade yard under the tower, the war hall and the forge on
the high side, stores and pens on the low side, and the jungle pressing on the wall everywhere else - except the
west side, which is not walled at all, because the west side is the beach.  The sea is the wall there,
and there is a wrecked hull on the sand that was already there when the airship came in.
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

SP = "assets/tiles/stranglethorn/props/"
#: a couple of shared sprites that Sheet C and E did not replace - the signal
#: beacon and the hulls - still live with the other coastal art.
CPD = "assets/tiles/coastal_props/"

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
    "west":   ([(31, 24), (22, 22), (15, 25), (11, 29)], 2.6),
    "pens":   ([(33, 38), (41, 40), (46, 42)], 2.4),
    "stores": ([(31, 38), (21, 41), (14, 45)], 2.4),
    "strand": ([(15, 25), (13, 34), (14, 42)], 2.0),
}
PLAZA = (32, 24, 7.5, 5.8)

_RS = K.RoadSet(ROADS)
road_dist = _RS.dist

GAPS = [(32, 4, 6, 5), (32, 52, 6, 5)]


def paved(gx, gy):
    cx, cy, rx, ry = PLAZA
    r = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
    return (1 - r) * min(rx, ry)


def shore(gy):
    """x of the waterline on the west beach. The strand widens toward the middle of the camp, which is
    where the boats come in and where the wreck is."""
    gy = np.asarray(gy, float)
    return (7.5 + 2.6 * np.sin(0.052 * gy + 0.6) + 1.3 * np.sin(0.137 * gy + 1.7)
            + 0.6 * np.sin(0.33 * gy) + 1.8 * np.exp(-((gy - 28.0) / 16.0) ** 2))


def water_fields(gx, gy):
    """Same shelving as Booty Bay's cove: a wide pale shallow before the drop, because the camp sits
    on a strand rather than on a cliff."""
    sea = shore(gy) - gx
    return sea, sea - 5.5


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
    out = np.maximum(-inside + 1.0 * _wob(gx, gy),
                     np.minimum(rock, -road_dist(gx, gy) - 2.0))
    # The sea is the west wall. Without this the ring's own rim would win over the water in
    # kind_from_fields (cliff > 1.5 overrides shallow) and paint a stone lip across the beach.
    sea, _ = water_fields(gx, gy)
    return np.minimum(out, -sea - 1.2)


def fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    sh, dp = water_fields(gx, gy)
    return dict(cliff=cliff_field(gx, gy), shallow=sh, deep=dp, deck=np.full(gx.shape, -9.0))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


# ---- painter config -----------------------------------------------------------------------------------
WATER = "sea"
#: The ring round this clearing is jungle, not stone - see the WALL branch in tools/bake_stranglethorn.py.
#: ROCK lists the two outcrops inside it that really are rock (they match cliff_field below).
WALL = "canopy"
ROCK = [(52, 12, 6, 4.5), (11, 11, 5, 4)]
BASE = {"jungle": 1.0, "fern": 0.70, "mulch": 0.22, "clay": 0.15}
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
    "gromgol_innkeeper": (24, 30),            # Innkeeper Rukha - the camp's only bunk and the hearth
    "gromgol_flight_master": (38, 20),        # Windrider-Keeper Pazzik, the roost by the stair
    "gromgol_scout": (24, 16),                # Scout Hanzo
    "gromgol_quartermaster": (28, 28),        # Quartermaster Ghal
    # the parade yard and the wall
    "gromgol_drillmaster": (34, 30),          # Drillmaster Ukko
    "gromgol_south_sentry": (30, 48),         # Sentry Vrak, south gate
    "gromgol_wounded_runner": (26, 33),       # Runner Teza
    "gromgol_field_medic": (22, 36),          # Field-Medic Sulaa
    # the trades
    "gromgol_smith": (52, 23),                # Smith Dorgun
    "gromgol_beast_handler": (41, 47),        # Beast-Handler Kozza, the pens
    "gromgol_storesman": (24, 44),            # Storesman Pell
    "gromgol_cartographer": (16, 20),         # Mapmaker Ashi
    "gromgol_troll_attache": (41, 24),        # Attaché Zul'jana - Darkspear, and from here
    # vendors
    "gromgol_trader": (34, 32),               # Trader Burg
    "gromgol_provisioner": (20, 41),          # Provisioner Nakka
    "gromgol_weaponsmith": (51, 27),          # Weaponsmith Trag
    "gromgol_herbalist": (12, 32),            # Herbalist Mossa, at the top of the sand
}
FORGE = (54, 22)
EXTRA_NPC_XY = [FORGE]
CHESTS = [(14, 10), (52, 10), (14, 48), (51, 34)]


JP = "assets/tiles/echo_isles/props/"


def dress(L):
    P, B, D = L.prop, L.bld, L.dp
    C = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=SP, **kw)
    J = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=SP, **kw)

    # ---- the north gate: the stair head up to the mooring tower ----------------------------------
    # The tower itself is a zone of its own now and stands outside the wall; what is left in here is
    # the foot of its stair and the traffic that comes down it.
    # AT THE STAIR HEAD, NOT ACROSS THE ROAD BELOW IT. With its base at y=16 the tower's
    # solid foot sat on the road three tiles south of where the zeppelin stair sets you down,
    # so the first thing anyone did in Grom'gol was walk round a watchtower. Kyle, 10 Nov:
    # "imagine opening a door and the wall is RIGHT there. this also happens when you get off
    # the zepplin in Grom'gol." It now stands over the stair itself (base y=6), not solid -
    # you come down through its foot - and the road south is clear to the parade yard.
    B("gg_watchtower", 32, 6, 12, road_ok=True, nudge=0, solid=False, allow_overlap=True)

    D("vot_war_banner", 26, 14, 5)
    D("vot_war_banner", 38, 14, 5)
    D("vot_crate_stack", 24, 10, 3)
    D("vot_crate_stack", 41, 10, 3)
    P("br_signpost", 36, 12, 5)
    L.prop("stv_troll_totem", 20, 8, 7, path_dir=SP)                    # the trolls got here first; the orcs left it standing

    # ---- the beach: the wreck, the boats, and the sand the camp actually landed on ---------------
    J("stv_wreck_hull", 18, 41, 11, shore_ok=True)
    J("stv_wreck_bow", 10, 15, 7, shore_ok=True)
    L.prop("boat_orc", 12, 27, 6, shore_ok=True, path_dir=CPD)
    L.prop("stv_outrigger", 11, 22, 4, shore_ok=True, path_dir=SP)
    L.prop("stv_bollard", 13, 30, 3, shore_ok=True, path_dir=SP)
    J("stv_tide_pool", 9, 46, 3, solid=False, shore_ok=True)
    J("stv_shells", 10, 11, 3, solid=False, shore_ok=True)
    L.prop("stv_driftwood", 12, 50, 3, shore_ok=True, path_dir=SP)
    L.prop("stv_mangrove", 14, 53, 6, shore_ok=True, path_dir=SP)
    L.prop("stv_mangrove", 13, 6, 6, shore_ok=True, path_dir=SP)
    for (x, y) in [(15, 11), (16, 18), (15, 32), (17, 48), (14, 7), (16, 54)]:
        J("stv_palm_frond" if (x + y) % 2 else "stv_screw_pine", x, y, 10)

    # ---- the high side: war hall, forge, weapon racks ---------------------------------------------
    B("gg_longhouse", 44, 33, 11)
    B("gg_forge", 56, 20, 8)
    D("vot_training_dummy", 46, 30, 4)
    D("vot_training_dummy", 49, 31, 4)
    D("vot_archery_target", 56, 32, 4)
    D("rf_tool_rack", 58, 25, 3)
    D("vot_war_drum", 42, 30, 3)

    # ---- the parade yard: fire, totem, the drillmaster's ground -----------------------------------
    D("vot_fire_pit", 32, 24, 3, solid=False, road_ok=True)
    # Beside the road, not planted in the middle of it (it was at x=32, dead ahead of the stair).
    D("vot_totem_pole", 21, 20, 9)
    D("vot_war_banner", 28, 26, 5)
    D("vot_war_banner", 36, 26, 5)

    # ---- the low side: stores, provisioner, the medic's tent --------------------------------------
    B("gg_supply_store", 22, 46, 8)
    B("gg_command_tent", 21, 38, 5)
    B("gg_command_tent", 30, 44, 5)
    B("gg_supply_store", 19, 29, 6)
    B("gg_command_tent", 21, 34, 6)
    D("vot_crate_stack", 18, 46, 3)
    D("vot_crate_stack", 18, 43, 3)
    D("vot_hide_rack", 24, 40, 3)

    # ---- the pens: raptors the camp has stopped pretending it has not tamed ------------------------
    for (x, y) in [(44, 44), (46, 44), (48, 44), (50, 44), (52, 44), (52, 46), (52, 48),
                   (50, 48), (48, 48), (46, 48), (44, 48), (44, 46)]:
        D("vot_palisade", x, y, 3, solid=True, nudge=0)
    L.prop("stv_raptor_nest", 48, 46, 4, path_dir=SP)
    L.prop("stv_trough", 42, 44, 3, path_dir=SP)
    B("bb_lean_shack", 56, 41, 6)

    # ---- the palisade ring itself: posts on the inside of the wall, gates marked -------------------
    for (x, y) in [(22, 6), (42, 6), (58, 22), (58, 34), (22, 53), (46, 53), (56, 10), (54, 46)]:
        D("vot_palisade", x, y, 4, solid=False, nudge=1)
    B("orc_great_gatehouse", 26, 52, 8, road_ok=True, nudge=1)
    B("gg_watchtower", 38, 47, 10, nudge=3)
    D("vot_war_banner", 30, 50, 5)
    L.prop("stv_arena_standard", 36, 49, 5, path_dir=SP)

    # ---- WHAT THE WALL IS HOLDING BACK, and what it is not --------------------------------------
    # A palisade keeps people out. It does nothing about the jungle, which has been coming back over
    # the wall for three years and is winning. The INSIDE stays open, because a fort clears its own
    # ground and that is most of what a garrison does all day - the density belongs against the wall,
    # on the strand, and in the few places nobody has a reason to walk.
    for (x, y) in [(50, 42), (20, 51), (44, 51), (54, 35), (24, 8), (42, 9), (48, 20), (30, 10)]:
        L.prop("stv_tree_buttress", x, y, 11, path_dir=SP)
    for (x, y) in [(55, 28), (20, 47), (20, 10), (46, 10), (18, 53), (40, 48), (56, 16), (52, 50)]:
        L.prop("stv_bamboo", x, y, 8, path_dir=SP)
    for (x, y) in [(26, 21), (41, 20), (24, 31), (44, 32), (30, 46), (18, 18), (50, 30)]:
        J("stv_palm_young" if (x + y) % 3 else "stv_palm_frond", x, y, 10)
    for (x, y) in [(13, 35), (50, 35), (26, 7), (38, 52), (21, 34), (44, 36), (29, 50), (17, 14),
                   (51, 52), (35, 7), (33, 43), (56, 44)]:
        L.prop("stv_hibiscus", x, y, 3, solid=False, path_dir=SP)
    for (x, y) in [(27, 42), (37, 45), (19, 26), (46, 25), (23, 15), (48, 44)]:
        L.prop("stv_banana_clump", x, y, 6, path_dir=SP)
    for (x, y) in [(55, 24), (22, 49), (45, 49), (50, 10)]:
        L.prop("stv_boulder_mossy", x, y, 4, path_dir=SP)
    # the troll stonework the camp was pitched on top of
    J("stv_troll_ziggurat_block", 31, 50, 8, nudge=8)
    J("stv_troll_idol_head", 51, 17, 8, nudge=5)


def build_layout():
    return K.build(sys.modules[__name__])


def generate_gromgol():
    L = build_layout()
    K.register_baked(L.zone, sys.modules[__name__])
    return L.zone
