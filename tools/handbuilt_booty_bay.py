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

SP = "assets/tiles/stranglethorn/props/"

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
    "bootybay_lookout": (30, 6),               # Lookout Minzi, the cape watch
    "bootybay_toll_collector": (45, 18),       # Tollkeeper Nizzik, head of the ramp
    "bootybay_harbourmaster": (50, 22),        # Harbourmaster Sprocket, tower door
    "bootybay_banker": (26, 26),               # MerchantTusk - the Baron's vault, on the market row
    "bootybay_flight_master": (41, 25),        # Wind-Rider Zekki, the roost over the north pier
    # the upper gallery - the market row, sellers along the rail
    "bootybay_trader": (30, 22),               # Trader Nixxle
    "bootybay_shipping_clerk": (36, 22),       # Clerk Bexx
    "bootybay_cartel_factor": (25, 22),        # Factor Weezel - still signs for Ratchet, and says so
    "bootybay_street_kid": (33, 22),           # Scrip
    "bootybay_crane_hand": (42, 23),           # Crane-Hand Durgo
    # the back walk, against the cliff
    "bootybay_weapon_dealer": (23, 31),        # Dealer Sark
    "bootybay_fence": (23, 36),                # The Quiet Man
    "bootybay_shipwright": (23, 41),           # Shipwright Vella
    # the cross bridge and the east walk
    "bootybay_tavern_keeper": (28, 34),        # Keeper Marla
    "bootybay_dockmaster": (45, 31),           # Dockmaster Brek
    "bootybay_troll_pilot": (45, 38),          # Pilot Zan'rek, knows the reef
    "bootybay_fishmonger": (47, 46),           # Gurgle, the south pier
    # the lower gallery
    "bootybay_baron": (44, 35),                # Baron Revilgaz, on the gallery above his warehouse
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


def _veg(L, name, cx, base_y, height, path_dir=SP, max_push=14):
    """Place a jungle sprite so its canopy does NOT hang over the walkable boards.

    Kyle, 2026-10-31: "booty bay is an absolute mess bro. so much wasted space and everything is
    crammed to shit."

    Measured before touching anything: 123% of the walkable deck sat under a prop footprint, and
    53% of that was jungle vegetation. Sixteen tree buttresses and seven bamboo clumps were
    drawing over the boards.

    The intent in dress() was already right - the comment there says this growth "hangs over
    rock, where a placement check would refuse it and be right to". The problem is that deco()
    does no check at all, and these sprites are eleven tiles tall: anchored against the cliff
    they still spread a canopy several tiles wide over the deck in front of them. An anchor on
    rock does not mean a FOOTPRINT on rock.

    So this does the check deco() deliberately skips, for vegetation only: push the sprite away
    from the town centre until its footprint clears the deck, and shrink it if pushing is not
    enough. Nothing is deleted - the jungle still comes down the back wall, it just stops
    standing in the market.
    """
    import numpy as np
    from tools.handbuilt_central_barrens import _aspect

    z = L.z
    path = f"{path_dir}{name}.png"

    def clear(ax, ay, h):
        wt = max(1, round(h * _aspect(path)))
        x0, y0 = ax - wt // 2, ay - h + 1
        for yy in range(max(0, y0), min(z.height, ay + 1)):
            for xx in range(max(0, x0), min(z.width, x0 + wt)):
                if z.is_walkable(xx, yy):
                    return False
        return True

    # Away from the middle of the map is away from the town, which is built around it.
    dx = 1 if cx >= W // 2 else -1
    dy = 1 if base_y >= H // 2 else -1
    for push in range(0, max_push + 1):
        for h in (height, max(3, int(height * 0.7)), max(3, int(height * 0.5))):
            if clear(cx + dx * push, base_y + dy * (push // 2), h):
                L.deco(name, cx + dx * push, base_y + dy * (push // 2), h, path_dir=path_dir)
                return True
    return False        # nowhere for it: better absent than drawn across the boards


def dress(L):
    P, B, D = L.prop, L.bld, L.dp
    C = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=SP, **kw)
    J = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=SP, **kw)
    z = L.z

    # ---- the boat to Ratchet, at the head of the middle pier -------------------------------------
    z.collision_layer[BOAT[1]][BOAT[0]] = None
    z.set_tile(BOAT[0], BOAT[1], "boat", "interaction")
    # OFF THE DOCK AND INTO THE WATER. The boat was drawn across the head of the pier, on
    # top of the boarding tile it is supposed to mark. Kyle, 10 Nov: "boat portal from BB to
    # ratchet is blocked by a boat, move that prop off the dock and into the water." It now
    # rides just south of the pier, where the boarding tile reads as the way onto it.
    L.deco("boat_orc", 65, 46, 8)
    L.deco("boat_troll", 61, 29, 7)

    # ---- the headland: the gate, the bone arch, the only soil in the zone ------------------------
    L.prop("stv_bone_arch", 35, 11, 9, solid=False, road_ok=True, nudge=0, path_dir=SP)
    P("br_signpost", 40, 14, 5, road_ok=True)
    # the headland is rock, so nothing STANDS on it - the growth hangs over the road from above, which
    # is what L.deco is for: a sprite with no collision and no placement check.
    for (x, y) in [(26, 12), (45, 9), (22, 7), (49, 14), (18, 11), (41, 6), (30, 16), (53, 10)]:
        _veg(L, "stv_tree_buttress", x, y, 11, path_dir=SP)
    for (x, y) in [(21, 9), (48, 11), (16, 15), (44, 15)]:
        _veg(L, "stv_bamboo", x, y, 8, path_dir=SP)
    _veg(L, "stv_palm_frond", 40, 7, 10, path_dir=SP)
    _veg(L, "stv_palm_young", 24, 5, 10, path_dir=SP)

    # ---- the ramp foot: toll post and the harbourmaster's tower, first thing off the cliff --------
    B("bb_lean_shack", 47, 21, 6, nudge=2)
    B("bb_harbourmaster_tower", 46, 28, 10, nudge=3)
    D("vot_crate_stack", 44, 21, 3)
    P("br_signpost", 43, 22, 5)

    # ---- the upper gallery: the market row ------------------------------------------------------
    B("bb_trade_shop", 29, 28, 5)
    B("bb_trade_shop", 37, 28, 6)
    # A third shop stood here at (46, 26), drawn through the harbourmaster's tower. The gallery
    # has no room for it east of the tower, so it is gone until Booty Bay is rebuilt (backlog C [51]).
    D("rf_supply_crates", 33, 28, 3)
    D("vot_crate_stack", 24, 28, 3)

    # ---- the back walk and the cross bridge -----------------------------------------------------
    B("bb_harbour_inn", 20, 40, 9, nudge=2)
    B("bb_lean_shack", 19, 30, 6, nudge=2)
    D("rf_tool_rack", 19, 34, 3)
    D("vot_fire_pit", 32, 36, 2, solid=False)
    D("rf_supply_crates", 37, 36, 3)

    # ---- the east walk: the working side, clear of all three pier junctions ----------------------
    B("bb_warehouse", 42, 42, 7, nudge=5)
    B("gg_supply_store", 40, 31, 5, nudge=2)
    L.prop("stv_fish_rack", 39, 39, 4, path_dir=SP)
    L.prop("stv_fish_crates", 40, 29, 3, path_dir=SP)

    # ---- the lower gallery: the Baron's office, the cages, the holding yard ----------------------
    B("bb_counting_house", 36, 50, 10, nudge=3)
    B("bb_lean_shack", 26, 50, 6, nudge=2)
    D("rf_prison_cage", 21, 49, 5)
    D("vot_crate_stack", 31, 50, 3)
    L.prop("stv_driftwood", 43, 48, 3, path_dir=SP)

    # ---- pier furniture: cranes, lanterns, traps, what a working harbour leaves lying about ------
    for (x, y) in [(46, 25), (52, 25), (58, 25)]:
        L.deco("stv_dock_lantern", x, y, 4, path_dir=SP)
    for (x, y) in [(47, 33), (54, 33), (62, 33)]:
        L.deco("stv_dock_lantern", x, y, 4, path_dir=SP)
    for (x, y) in [(47, 45), (54, 45)]:
        L.deco("stv_dock_lantern", x, y, 4, path_dir=SP)
    for (x, y) in [(21, 23), (27, 22), (41, 22), (21, 45), (34, 44), (18, 38), (18, 27),
                   (25, 34), (37, 34), (40, 28), (40, 44), (45, 50)]:
        L.deco("stv_dock_lantern", x, y, 4, path_dir=SP)
    L.deco("stv_bollard", 52, 36, 3, path_dir=SP)
    L.deco("stv_bollard", 60, 36, 3, path_dir=SP)
    L.deco("stv_bollard", 52, 48, 3, path_dir=SP)
    L.deco("stv_fish_crates", 50, 27, 3, path_dir=SP)
    L.deco("stv_fish_crates", 66, 38, 3, path_dir=SP)
    L.deco("stv_outrigger", 49, 48, 4, path_dir=SP)
    L.deco("stv_boat_wreck", 60, 50, 4, path_dir=SP)

    # ---- the lagoon and the cliffs it is cut into ------------------------------------------------
    L.deco("stv_coral_outcrop", 62, 44, 4, path_dir=SP)
    L.deco("stv_coral_outcrop", 56, 52, 4, path_dir=SP)
    L.deco("stv_sea_stack", 66, 21, 10, path_dir=SP)
    L.deco("stv_troll_totem", 41, 52, 5, path_dir=SP)
    L.deco("stv_tide_pool", 52, 56, 3, path_dir=SP)
    # The jungle comes down the back wall and over both arms, and nobody cuts it because nobody can
    # reach it. All of this is deco: it hangs over rock, where a placement check would refuse it and
    # be right to, since none of it is standing on anything a player could walk on.
    for (x, y) in [(11, 18), (9, 48), (13, 55), (14, 26), (13, 44), (52, 57), (21, 57), (10, 36),
                   (58, 16), (60, 52), (16, 10), (12, 60)]:
        _veg(L, "stv_tree_buttress", x, y, 11, path_dir=SP)
    for (x, y) in [(8, 30), (11, 41), (10, 13), (57, 9), (17, 52), (45, 57), (7, 56), (14, 33)]:
        _veg(L, "stv_bamboo", x, y, 8, path_dir=SP)
    for (x, y) in [(12, 35), (9, 24), (15, 48), (55, 12), (31, 57), (13, 39)]:
        _veg(L, "stv_banana_clump", x, y, 6, path_dir=SP)
    for (x, y) in [(13, 29), (10, 38), (14, 21), (51, 11), (27, 57), (39, 57), (15, 43)]:
        _veg(L, "stv_hibiscus", x, y, 3, path_dir=SP)
    for (x, y) in [(13, 15), (10, 52), (47, 6), (19, 11), (15, 57)]:
        _veg(L, "stv_palm_young" if (x + y) % 2 else "stv_screw_pine", x, y, 10, path_dir=SP)
    _veg(L, "stv_mangrove", 16, 22, 6, path_dir=SP)
    _veg(L, "stv_mangrove", 16, 47, 6, path_dir=SP)
    L.deco("stv_troll_totem", 17, 16, 7, path_dir=SP)   # older than the port, and nobody moves it


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
