"""
Hand-built Booty Bay (70x60): the deep-water port at the bottom of the world.

TOWN ARCHETYPE: THERE IS NO GROUND.  Kyle, 29 Oct 2026: "Bootybay is a dock-based town bro" - and the
first version of this file got that wrong in the most ordinary way, by building a cove with some piers
bolted onto it.  Booty Bay is not a town beside the water.  It is a town ON the water: a three-level
timber complex standing on pilings over a sheltered lagoon, with the cliff at its back and nothing
underneath it but the tide.  It is a RING of galleries rather than one platform - an upper market row
along the back of the cove, a lower deck under it, a back walk against the cliff, an east walk inside
the arm, and one cross bridge straight over open water - so the lagoon shows through the middle of the
town and you are always walking beside the drop rather than across a floor.

So the land budget here is almost nothing on purpose.  The only soil in the zone is the shelf along the
top of the northern headland, and the only reason it exists is that the road has to land somewhere: you
come in at the clifftop gate (35,4), walk the headland east under the bone arch, and take the one ramp
down onto the boards.  From the moment your boots hit planking you do not touch ground again.  Every
building, every vendor, the Baron's office and the holding cages are all out over the water, and the
three piers run further out from the promenade into the bay.  The boat to Ratchet ties up at the head of
the middle one.

The lagoon is the other half of the look.  The cove shelves slowly inside the arms of the headland, so
most of the water you can see from the boards is a pale turquoise shelf rather than open sea, and the
dark only starts out past the pier heads.

WHY IT IS ITS OWN FACTION.  claude/stranglethorn_design.md: when the land road south turned to rock,
Booty Bay stopped being one of the Steamwheedle Cartel's franchises and became the only deep-water
harbour that still connects anything to anything.  Gazlowe signs the manifests in Ratchet.  Baron
Revilgaz decides what actually sails.  The practical consequence for the town's shape is the LANDING
FEE: the ramp is the only way down and there is a toll post on it, so you cannot reach the boards
without walking past somebody who wants paying.

HARD CONTRACTS (world/portal_manager.py)
  portal   (35,4)  -> Southern Stranglethorn (36,150);  arrival (35,6)
  boat     (64,34) -> Ratchet (62,32), the middle pier head; registered, not flavour
"""
import sys

import numpy as np

from tools import town_kit as K
from tools.handbuilt_central_barrens import _wob, _smooth, _gauss

JP = "assets/tiles/echo_isles/props/"
CPD = "assets/tiles/coastal_props/"

KEY = "booty_bay"
NAME = "Booty Bay"
DESC = "A goblin port standing on pilings over a lagoon. Nothing sails without the Baron."
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
    # the headland shelf: in at the gate, east and down to the head of the ramp. This is the ONLY road,
    # because it is the only ground.
    "gate": ([(35, 3), (35, 8), (38, 12), (42, 16), (45, 19)], 3.4),
}
PLAZA = None

# ---------------------------------------------------------------- the boards
# (x0, x1, y0, y1). These ARE the town - three levels plus the piers. The upper and lower galleries
# overlap the quay deliberately: a gap of even one tile reads as a hole you fall through.
DECKS = [
    (42.0, 52.0, 16.0, 23.0),        # the ramp foot - where the road lands on planking
    (19.0, 50.0, 21.5, 28.5),        # UPPER GALLERY: the market row, along the back of the cove
    (16.0, 24.0, 24.0, 50.5),        # the back walk, hard against the cliff
    (19.0, 46.0, 42.5, 50.5),        # LOWER GALLERY: the Baron's office and the cages
    (38.0, 46.0, 24.0, 47.0),        # the east walk, inside the arm
    (24.0, 42.0, 32.5, 37.0),        # the cross bridge, straight over open water
    (44.0, 62.0, 24.6, 27.4),        # north pier
    (44.0, 66.0, 32.6, 35.6),        # middle pier
    (58.5, 69.0, 30.2, 38.8),        # middle pier head platform (boat at 64,34)
    (44.0, 58.0, 44.6, 47.4),        # south pier
]

_RS = K.RoadSet(ROADS)
road_dist = _RS.dist
GAPS = [(35, 4, 5, 5)]


def shore(gy):
    """x of the waterline. The two arms of the headland reach east at the top and the bottom of the
    map; between them the water comes almost all the way to the back wall, which is why the town had
    to be built on pilings in the first place."""
    gy = np.asarray(gy, float)
    return (15.0 + 42.0 * (1 - _smooth(11, 23, gy)) + 40.0 * _smooth(43, 55, gy)
            - 3.0 * _gauss(gy, 33, 13) + 1.1 * np.sin(0.44 * gy + 0.8) + 0.6 * np.sin(0.95 * gy))


def water_fields(gx, gy):
    """A LAGOON, not open sea: the cove shelves slowly inside the arms, so most of the water visible
    from the boards is a pale shelf and the dark starts out past the pier heads."""
    sea = gx - shore(gy)
    sheltered = np.exp(-((gy - 34.0) / 19.0) ** 2)
    return sea, sea - (3.4 + 13.0 * sheltered)


def deck_field(gx, gy):
    best = np.full(np.shape(gx), -9.0)
    for (x0, x1, y0, y1) in DECKS:
        e = np.minimum(np.minimum(gx - x0, x1 - gx), np.minimum(gy - y0, y1 - gy))
        best = np.maximum(best, e)
    return best


def cliff_field(gx, gy):
    """EVERY piece of land here is rock except the road corridor. That is the whole archetype: the
    headland is a cliff, the back wall is a cliff, and the town is not on either of them."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    inland = shore(gy) - gx                       # >0 on the land side of the waterline
    out = inland * 1.6 + 1.0 * _wob(gx, gy)
    # knuckles standing out of the water: the stacks off the cove mouth and one inside the arms
    for (cx, cy, rx, ry) in [(63, 12, 5.0, 3.6), (56, 54, 4.6, 3.2), (52, 40, 3.0, 2.4)]:
        r = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
        out = np.maximum(out, (1 - r) * min(rx, ry))
    clear = np.full(gx.shape, -99.0)
    for (cx, cy, rx, ry) in GAPS:
        d = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
        clear = np.maximum(clear, (1 - d) * min(rx, ry))
    clear = np.maximum(clear, road_dist(gx, gy) + 2.4)
    clear = np.maximum(clear, deck_field(gx, gy) + 1.5)
    return np.minimum(out, -clear)


def fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    sh, dp = water_fields(gx, gy)
    return dict(cliff=cliff_field(gx, gy), shallow=sh, deep=dp, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


# ---- painter config -----------------------------------------------------------------------------------
WATER = "sea"
BASE = {"jungle": 1.0, "fern": 0.65, "clay": 0.15, "hard": 0.22}
PAINT = {
    "camp":  [(38, 10, 8, 4, 0.8)],
    "hard":  [(38, 10, 6, 3, 0.7)],
    "mulch": [(28, 8, 8, 4, 0.5)],
}

NPC_POSITIONS = {
    # NPCs stand on the OUTER edge of each gallery and the buildings sit against the inner edge. A
    # walkway six or seven boards wide cannot hold both down its middle, and the first version of this
    # roster proved it by refusing half the buildings.
    # the headland and the ramp: you pay before your boots touch planking
    "bootybay_gate_guard": (36, 8),            # Bruiser Kolk, clifftop gate
    "bootybay_lookout": (31, 7),               # Lookout Minzi, the cape watch
    "bootybay_toll_collector": (45, 19),       # Tollkeeper Nizzik, head of the ramp
    "bootybay_harbourmaster": (49, 22),        # Harbourmaster Sprocket, tower door
    # the upper gallery - the market row, sellers along the rail
    "bootybay_trader": (30, 22),               # Trader Nixxle
    "bootybay_shipping_clerk": (36, 22),       # Clerk Bexx
    "bootybay_cartel_factor": (25, 22),        # Factor Weezel - still signs for Ratchet, and says so
    "bootybay_street_kid": (33, 22),           # Scrip
    "bootybay_crane_hand": (44, 22),           # Crane-Hand Durgo
    # the back walk, against the cliff
    "bootybay_weapon_dealer": (23, 31),        # Dealer Sark
    "bootybay_fence": (23, 36),                # The Quiet Man
    "bootybay_shipwright": (23, 41),           # Shipwright Vella
    # the cross bridge and the east walk
    "bootybay_tavern_keeper": (28, 34),        # Keeper Marla
    "bootybay_dockmaster": (45, 30),           # Dockmaster Brek
    "bootybay_troll_pilot": (45, 38),          # Pilot Zan'rek, knows the reef
    "bootybay_fishmonger": (47, 46),           # Gurgle, the south pier
    # the lower gallery
    "bootybay_baron": (34, 44),                # Baron Revilgaz, outside his own door
    "bootybay_baron_aide": (29, 44),           # Aide Fipple
    "bootybay_bloodsail_captive": (24, 44),    # a Bloodsail nobody has decided what to do with
}
FORGE = (23, 27)
EXTRA_NPC_XY = [FORGE]
#: NOT town_kit's CHESTS. Layout.chest() refuses any tile whose base is "path", which is the right rule
#: everywhere else - a chest in the middle of a road is a bug - but every walkable tile in this town is
#: decking, and decking is laid down as "path". So the chests are placed directly on the boards below,
#: as crates on the quay, which is where they would actually be in a port.
CHESTS = []
DECK_CHESTS = [(18, 26), (59, 26), (62, 34), (18, 49), (40, 35)]


def dress(L):
    P, B, D, C = L.prop, L.bld, L.dp, L.cp
    J = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=JP, **kw)
    z = L.z

    # ---- the boat to Ratchet, at the head of the middle pier -------------------------------------
    z.collision_layer[BOAT[1]][BOAT[0]] = None
    z.set_tile(BOAT[0], BOAT[1], "boat", "interaction")
    L.deco("boat_orc", 67, 37, 8)
    L.deco("boat_troll", 61, 29, 7)

    # ---- the headland: the gate, the bone arch, the only soil in the zone ------------------------
    C("crab_claw_arch", 35, 11, 9, solid=False, road_ok=True, nudge=0)
    P("br_signpost", 40, 14, 5, road_ok=True)
    # the headland is rock, so nothing STANDS on it - the growth hangs over the road from above, which
    # is what L.deco is for: a sprite with no collision and no placement check.
    for (x, y) in [(26, 12), (45, 9), (22, 7), (49, 14), (18, 11), (41, 6), (30, 16), (53, 10)]:
        L.deco("jungle_banyan", x, y, 11, path_dir=CPD)
    for (x, y) in [(21, 9), (48, 11), (16, 15), (44, 15)]:
        L.deco("bamboo_grove", x, y, 8, path_dir=CPD)
    L.deco("palm_lean_a", 40, 7, 10, path_dir=JP)
    L.deco("palm_cluster", 24, 5, 10, path_dir=JP)

    # ---- the ramp foot: toll post and the harbourmaster's tower, first thing off the cliff --------
    B("guard_post", 47, 21, 6, nudge=2)
    B("harbor_tower", 46, 28, 10, nudge=3)
    D("vot_crate_stack", 44, 21, 3)
    P("br_signpost", 43, 22, 5)

    # ---- the upper gallery: the market row ------------------------------------------------------
    B("bazaar_stall_row", 29, 28, 5)
    B("mixed_trading_post", 37, 28, 6)
    B("trading_post", 46, 26, 6, nudge=3)
    D("rf_supply_crates", 33, 28, 3)
    D("vot_crate_stack", 24, 28, 3)

    # ---- the back walk and the cross bridge -----------------------------------------------------
    B("the_broken_keel", 20, 40, 9, nudge=2)
    B("generic_shack_a", 19, 30, 6, nudge=2)
    D("rf_tool_rack", 19, 34, 3)
    D("vot_fire_pit", 32, 36, 2, solid=False)
    D("rf_supply_crates", 37, 36, 3)

    # ---- the east walk: the working side, clear of all three pier junctions ----------------------
    B("ratchet_docks_warehouse", 41, 42, 8, nudge=2)
    B("supply_cache_shed", 40, 31, 5, nudge=2)
    C("fish_drying_rack", 39, 39, 4)
    C("fish_crates_traps", 40, 29, 3)

    # ---- the lower gallery: the Baron's office, the cages, the holding yard ----------------------
    B("gazlowes_office", 36, 50, 10, nudge=3)
    B("generic_shack_b", 26, 50, 6, nudge=2)
    D("rf_prison_cage", 21, 49, 5)
    D("vot_crate_stack", 31, 50, 3)
    C("driftwood_pile", 43, 48, 3)

    # ---- pier furniture: cranes, lanterns, traps, what a working harbour leaves lying about ------
    for (x, y) in [(46, 25), (52, 25), (58, 25)]:
        L.deco("dock_lantern_post", x, y, 4)
    for (x, y) in [(47, 33), (54, 33), (62, 33)]:
        L.deco("dock_lantern_post", x, y, 4)
    for (x, y) in [(47, 45), (54, 45)]:
        L.deco("dock_lantern_post", x, y, 4)
    for (x, y) in [(21, 23), (27, 22), (41, 22), (21, 45), (34, 44), (18, 38), (18, 27),
                   (25, 34), (37, 34), (40, 28), (40, 44), (45, 50)]:
        L.deco("dock_lantern_post", x, y, 4)
    L.deco("mooring_posts", 52, 36, 3)
    L.deco("mooring_posts", 60, 36, 3)
    L.deco("mooring_posts", 52, 48, 3)
    L.deco("fish_crates_traps", 50, 27, 3)
    L.deco("fish_crates_traps", 66, 38, 3)
    L.deco("outrigger_canoe", 49, 48, 4)
    L.deco("rowboat_wreck", 60, 50, 4)

    # ---- the lagoon and the cliffs it is cut into ------------------------------------------------
    L.deco("coral_reef_outcrop", 62, 44, 4)
    L.deco("coral_reef_outcrop", 56, 52, 4)
    L.deco("sea_stack_spire", 66, 21, 10)
    L.deco("sunken_totem", 41, 52, 5)
    L.deco("tide_pool", 52, 56, 3, path_dir=JP)
    # The jungle comes down the back wall and over both arms, and nobody cuts it because nobody can
    # reach it. All of this is deco: it hangs over rock, where a placement check would refuse it and
    # be right to, since none of it is standing on anything a player could walk on.
    for (x, y) in [(11, 18), (9, 48), (13, 55), (14, 26), (13, 44), (52, 57), (21, 57), (10, 36),
                   (58, 16), (60, 52), (16, 10), (12, 60)]:
        L.deco("jungle_banyan", x, y, 11, path_dir=CPD)
    for (x, y) in [(8, 30), (11, 41), (10, 13), (57, 9), (17, 52), (45, 57), (7, 56), (14, 33)]:
        L.deco("bamboo_grove", x, y, 8, path_dir=CPD)
    for (x, y) in [(12, 35), (9, 24), (15, 48), (55, 12), (31, 57), (13, 39)]:
        L.deco("banana_plant", x, y, 6, path_dir=CPD)
    for (x, y) in [(13, 29), (10, 38), (14, 21), (51, 11), (27, 57), (39, 57), (15, 43)]:
        L.deco("hibiscus_bush", x, y, 3, path_dir=CPD)
    for (x, y) in [(13, 15), (10, 52), (47, 6), (19, 11), (15, 57)]:
        L.deco("palm_cluster" if (x + y) % 2 else "palm_lean_b", x, y, 10, path_dir=JP)
    L.deco("mangrove_thicket", 16, 22, 6, path_dir=CPD)
    L.deco("mangrove_thicket", 16, 47, 6, path_dir=CPD)
    L.deco("tiki_totem", 17, 16, 7, path_dir=CPD)   # older than the port, and nobody moves it


def deck_chests(L):
    """Crates on the boards. See DECK_CHESTS for why these do not go through Layout.chest()."""
    z = L.z
    for (x, y) in DECK_CHESTS:
        if z.is_walkable(x, y) and z.interaction_layer[y][x] is None and z.collision_layer[y][x] is None:
            z.set_tile(x, y, "chest", "interaction")
            L.chests.append((x, y))
        else:
            L.skipped.append(("deck chest", x, y, "occupied"))


def build_layout():
    L = K.build(sys.modules[__name__])
    deck_chests(L)
    return L


def generate_booty_bay():
    L = build_layout()
    K.register_baked(L.zone, sys.modules[__name__])
    return L.zone
