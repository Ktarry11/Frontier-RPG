"""
Hand-built Tempest Shallows (170x150): the south half of Tempest Isle, levels 52-55.

Kyle, 7 Nov 2026: "It'll be from saltspur to Tempest Isle" / "Isles in south east are shallow
watch reachable as the north map is bigger than the south map. That's why they are there."

WHY HERE. This is the back half of the game's last content hole. audit_content_by_level.py put the
remaining "nothing to do" range at 53-60, and there are no creatures or bosses above level 52
anywhere. The Shallows takes 52-55 and the Ashen Reach takes 55-58.

=========================================================================================
IT IS AN ISLAND. THE SEA IS THE EDGE ON EVERY SIDE BUT ONE.
=========================================================================================

Kyle, 10 Nov: "the ENTIRE thing should be surrounded by water bro? No mountains, this is an
ISLAND". There is NO rim rock in this zone - no cliff spurs, no mountain ring, none of the
enclosure every mainland zone uses. What closes the map is open water, and the coast is a single
lobed curve rather than four straight edges.

The ONE exception is the north edge, which is not an edge at all: it is the internal border with
the Ashen Reach, and the island continues across it.

THE VOLCANO IS A MASSIF IN THE MIDDLE, NOT A WALL ACROSS THE TOP. The drawing is explicit - one
round mountain sitting ON the border with the dashed line running through it, and an arrow crossing
the border on EITHER SIDE of it. You walk AROUND its flanks to reach the high zone.

This shipped wrong once as a continuous band across the whole north with two circular holes punched
in it (Kyle: "the circle up top is weird bro. The volcano should be in the middle!"). The holes read
as holes because they were. A wall is simply the wrong primitive for a mountain: a massif is one
round thing with open country beside it, and the passes ARE that open country rather than anything
carved out.

PLACES (north is up; the Ashen Reach lies north across the border):
    W      ASHCLAIM LANDING (28,104): the jetty from Saltspur. Arrival.
    SW     KHAZ VARUN'S GATE (54,128): the collapsed gate of the old Dark Iron city. The set-piece.
    C      THE GREEN BELT: jungle across the middle, the only easy ground on the island.
    N      THE VOLCANO: its southern half. Open ground west and east of it - the two passes.
    SE     THE SHALLOWS themselves: four islets, wadeable all the way out.

HARD CONTRACTS (world/portal_manager.py)
  (28, 104)  <-> Saltspur Landing      the boat. Saltspur's berth tile was left UNREGISTERED on
                                       7 Nov precisely until this zone existed.
  (32, 4)    <-> The Ashen Reach       the WEST pass, round the volcano's west flank
  (140, 4)   <-> The Ashen Reach       the EAST pass, round its east flank
  (54, 128)  <-> Khaz Varun, the Black Hollow

Prop rule (Kyle): less is more; logical for the room; a few centrepieces.
Earth references scale with zone level - this is the LOW half of the isle, so it stays near silent.
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob, lobe

KEY = "tempest_shallows"
#: Tilemap NAME is the key world/portal_manager.py looks portals up under, and it must match the
#: name create_all_zones registers. Eastern Hillsbrad shipped once with these out of step and every
#: portal in both zones was dead - you could walk in and never walk out.
NAME = "Tempest Shallows"
DESC = ("The south half of Tempest Isle: jungle under a volcano's southern flank, ringed by sea, "
        "with a dead Dark Iron city inland and a wadeable archipelago off the south-east.")
REGION = "Tempest Isle"
W, H = 170, 150
BAKED_DIR = "assets/tiles/tempest_shallows/baked"
IS_TOWN = False
BASE_TILE = "grass"
SEED = 521

RU = "assets/tiles/ruins/"

PORTALS = {(28, 104): "Saltspur Landing",
           (32, 4): "The Ashen Reach",
           (140, 4): "The Ashen Reach",
           (54, 128): "Khaz Varun, the Black Hollow"}
#: Arrival is 2 tiles INTO the map off an edge portal (+3 leaving a dungeon), so these columns are
#: kept clear of solid landmarks by hand in dress().
ARRIVALS = [(31, 104), (32, 7), (140, 7), (54, 125)]
START = (38, 104)

# ---- the coast: one lobed curve, sea outside it ------------------------------------------------------
# ONE function decides land and sea, so the painted shoreline and the tile grid cannot disagree.
# A radial lobe around the island's centre rather than per-edge shorelines: an island has one coast,
# and expressing it as four edges is what produces a rectangle with rounded corners.
ISLE_CX, ISLE_CY = 86.0, 58.0
ISLE_SQUASH = 0.95          # very slightly taller than wide


def land_field(gx, gy):
    """>0 on land, <0 at sea. Distance inside the coast, in tiles."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    dx = gx - ISLE_CX
    dy = (gy - ISLE_CY) * ISLE_SQUASH
    d = np.sqrt(dx * dx + dy * dy)
    th = np.arctan2(dy, dx)
    # Integer harmonics only, so the coast is a closed curve that cannot disagree with itself where
    # it wraps. The drawing's coast is deeply lobed - bays and headlands, not a circle.
    r = (74.0 + 13.0 * np.sin(th + 0.6) + 8.5 * np.sin(2 * th - 0.9)
         + 5.5 * np.sin(3 * th + 2.1) + 3.0 * np.sin(5 * th - 0.3))
    coast = (r - d) + 1.8 * wob(gx * 0.5, gy * 0.5)

    # THE NORTH EDGE IS NOT A COAST. It is the border with the Ashen Reach and the island runs
    # across it, so land is forced to meet y=0 between the two pass columns. Without this the lobe
    # curves away from the top edge and both passes are open sea.
    border = (np.minimum.reduce([gx - 20.0, 152.0 - gx, 16.0 - gy])
              + 2.2 * wob(gx * 0.7, gy * 0.7))
    return np.maximum(coast, border)


#: (x, y, rx, ry) - the four islets, standing in the sea off the south-east. NOT scenery: they are
#: shallow-water reachable, and they exist because the north map is bigger - they are how the south
#: zone gets the area the Reach gets from open ground. Same rule Arathi East follows.
ISLETS = [(152.0, 128.0, 9.0, 6.5),
          (160.0, 112.0, 6.5, 5.0),
          (150.0, 143.0, 6.0, 4.5),
          (132.0, 143.0, 5.5, 4.0)]


def islet_field(gx, gy):
    p = np.full(np.shape(gx), -99.0)
    for (cx, cy, rx, ry) in ISLETS:
        p = np.maximum(p, lobe(gx, gy, cx, cy, rx, ry) + 0.45 * wob(gx * 1.2, gy * 1.2))
    return p


def sea_field(gx, gy):
    """>0 in the sea. The islets are land standing in it."""
    return -np.maximum(land_field(gx, gy), islet_field(gx, gy))


def deck_field(gx, gy):
    """The jetty at Ashclaim Landing: deck laid over water out to the boat. kind_from_fields
    resolves deck last, so this paints plank over sea rather than leaving the player on water."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    return np.minimum.reduce([gx - 22.0, 36.0 - gx, gy - 102.0, 106.0 - gy])


# ---- roads --------------------------------------------------------------------------------------------
# The trunk is the Ashclaim's own cart track, cut this season: up off the jetty, east through the
# green belt, and forked north round BOTH flanks of the volcano. The ruin road runs the other way
# and is older and worse, because the dwarves did not cut it - they re-found it.
ROADS = {
    "trunk":   ([(36, 104), (52, 98), (74, 90), (96, 82), (118, 74), (134, 64), (142, 52)], 3.2),
    "west":    ([(48, 98), (40, 72), (34, 40), (32, 6)], 2.6),       # round the west flank
    "east":    ([(134, 64), (140, 36), (140, 6)], 2.6),              # round the east flank
    "ruin":    ([(44, 106), (48, 116), (54, 124), (54, 128)], 2.4),  # down to Khaz Varun's gate
    "strand":  ([(118, 74), (126, 94), (134, 110), (138, 120)], 2.2),  # out to the shallows
}
_RS = K.RoadSet(ROADS)
road_dist = _RS.dist


def paved(gx, gy):
    """Worn stone: the landing apron, and Khaz Varun's forecourt under the rubble."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    apron = lobe(gx, gy, 40.0, 104.0, 8.0, 6.0) + 0.5 * wob(gx, gy)
    gate = lobe(gx, gy, 54.0, 126.0, 9.0, 7.0) + 0.5 * wob(gx, gy)
    return np.maximum(apron, gate) - 1.2


# ---- the volcano ---------------------------------------------------------------------------------------
# The ONLY rock in the zone. Its centre sits above the top edge, ON the border, so the Ashen Reach
# gets the northern half and the dungeon door on the far face. Nothing is carved out of it: the
# passes are the open ground to its west and east.
VOLCANO = (86.0, -8.0)
VOLCANO_R = 46.0


def volcano_field(gx, gy):
    """>0 inside the volcano's skirt."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    cx, cy = VOLCANO
    d = np.sqrt((gx - cx) ** 2 + (gy - cy) ** 2)
    # A ragged foot, because a volcano's skirt is lava lobes and scree rather than a drawn circle.
    # Higher wobble than a wall would want: here a lumpy edge is correct, not a failure.
    return (VOLCANO_R - d) + 2.6 * wob(gx * 0.55, gy * 0.55) + 1.1 * wob(gx * 1.3, gy * 1.3)


def cliff_field(gx, gy):
    """Impassable ground. NO RIM: the sea is the edge, so the only cliff here is the volcano."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    rock = volcano_field(gx, gy)
    # Roads, sea and the jetty always win over rock, in that order, so nothing is ever painted shut.
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    rock = np.where(sea_field(gx, gy) > -1.0, np.minimum(rock, -0.5), rock)
    rock = np.where(deck_field(gx, gy) > -1.0, np.minimum(rock, -0.5), rock)
    return rock


def fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    sea = sea_field(gx, gy)
    cliff = cliff_field(gx, gy)
    # THE ARCHIPELAGO IS WADEABLE, AND THAT HAS TO BE MEASURED RATHER THAN BOXED. A rectangle
    # over the south-east left the two southern islets standing in deep water, unreachable -
    # which is the exact failure the islets exist to avoid (Kyle: "Isles in south east are
    # shallow watch reachable"). The shelf is now distance to the nearest islet, so it follows
    # them wherever they are and a later edit that moves one cannot strand it.
    shelf = np.full(np.shape(gx), -99.0)
    for (cx, cy, rx, ry) in ISLETS:
        shelf = np.maximum(shelf, 30.0 - np.sqrt((gx - cx) ** 2 + (gy - cy) ** 2))
    # Open ocean away from the shelf still drops off fast, so the island reads as surrounded
    # rather than as one big sandbank.
    deep = sea - np.where(shelf > 0.0, 16.0, 3.0)
    return dict(cliff=np.where(sea > 0, -99.0, cliff),
                shallow=sea, deep=deep, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


# ---- subzones (x, y, w, h) ---------------------------------------------------------------------------
# Later registration wins on overlap. Keys must equal the encounters.json keys for this zone.
SUBZONES = [
    ("Ashclaim Landing", 30, 92, 30, 26),
    ("The Green Belt", 64, 64, 64, 38),
    ("Khaz Varun's Gate", 40, 110, 44, 34),
    ("The Scoured Slope", 36, 24, 104, 32),
    ("The Tempest Shallows", 112, 100, 56, 48),
]

# ---- baker config -------------------------------------------------------------------------------------
# Tropical below, volcanic above. `grass`/`forest` carry the green belt, `dry`/`rocky` take over as
# the ground climbs toward the volcano, and `shore` runs the whole coast and the archipelago.
BASE = {"grass": 0.40, "forest": 0.24, "shore": 0.18, "dry": 0.07, "rocky": 0.11}
PAINT = {
    "grass":  [(90, 84, 36, 22, 1.0), (116, 74, 30, 18, 0.95), (58, 94, 24, 16, 0.9),
               (136, 62, 20, 14, 0.8)],
    "forest": [(82, 88, 22, 14, 0.95), (108, 78, 20, 13, 0.9), (64, 102, 16, 11, 0.8),
               (128, 66, 14, 10, 0.7)],
    "shore":  [(38, 104, 12, 14, 1.0), (152, 128, 18, 12, 0.95), (150, 143, 14, 10, 0.9),
               (134, 112, 14, 10, 0.85), (34, 70, 8, 12, 0.7), (80, 134, 16, 9, 0.8)],
    # Scorched ground HUGS THE VOLCANO. At full strength and out in the middle of the map this
    # read as a desert dropped into a jungle; it is ash-stained ground at the foot of a mountain,
    # so it is weaker and it stays near the slope.
    "dry":    [(60, 36, 22, 9, 0.55), (112, 34, 20, 9, 0.5), (86, 40, 26, 8, 0.45)],
    "rocky":  [(86, 30, 38, 15, 0.95), (54, 34, 20, 10, 0.85), (120, 32, 20, 10, 0.85),
               (54, 126, 14, 10, 0.85)],
    "earth":  [(40, 104, 7, 5, 0.9), (54, 126, 8, 6, 0.9), (138, 118, 7, 5, 0.7)],
    "gravel": [(32, 10, 7, 5, 0.7), (140, 10, 7, 5, 0.7), (48, 116, 6, 5, 0.6)],
    "marsh":  [(128, 104, 10, 7, 0.6)],
}
COBBLE = [(54, 126, 10, 7, 0.9), (40, 104, 7, 5, 0.8)]

# ---- NPC spots ----------------------------------------------------------------------------------------
# SPREAD, one per thing the landing does, rather than six standing in a box.
# Kyle, 7 Nov: "Ensure NPCs, vendors, trainers are spaced out." This is the Ashclaim's forward camp -
# the town proper is Cinderwharf, in the high zone, so this stays a camp.
NPC_POSITIONS = {
    "ts_landing_bosun": (38, 102),        # off the jetty head, first face you see
    "ts_landing_quartermaster": (44, 110),
    "ts_landing_surveyor": (44, 96),      # the goblin who is costing the island
    "ts_gate_watch": (58, 118),           # watching Khaz Varun's gate from outside it
    "ts_belt_prospector": (92, 86),       # out in the green belt
    "ts_shallows_wader": (132, 112),      # at the head of the strand road
}

CHESTS = [(152, 128), (148, 141), (70, 126), (100, 120), (64, 44), (44, 78), (124, 44)]

#: Jungle, and only below the volcano. FOREST scatters within `rim` tiles of rock, which on this map
#: is the volcano's foot - so the planting hugs the slope, which is where the shelter is.
PALMS = [("ek_willow", 8, 0.30), ("ek_pine_trio", 7, 0.30), ("ek_thorn_bush", 4, 0.40)]
FOREST = dict(seed=59, count=78, rim=16, thorn=10, names=[
    ("ek_willow", 8, 0.32), ("ek_pine_trio", 7, 0.30),
    ("ek_dead_oak", 7, 0.24), ("ek_thorn_bush", 4, 0.40)])


def dress(L):
    p, b = L.prop, L.bld
    CO = "assets/tiles/coastal_props/"

    # ---- Ashclaim Landing: the jetty from Saltspur -------------------------------------------------
    # deco(), not prop(): prop() checks the ground under a sprite and refuses when it is not
    # placeable, which is right for a building and wrong for a hull - the whole point of a moored
    # boat is that it is standing on water.
    L.deco("boat_orc", 24, 104, 7, path_dir=CO)
    # The portal tile (12,104) and the column beside it stay clear of solid props, or the player
    # arrives inside one. Durnholde shipped that wrong once.
    for (x, y) in ((37, 100), (37, 108)):
        p("ek_scarlet_crates", x, y, 3)
    b("orc_supply_store", 46, 108, 10, nudge=2)
    b("orc_mess_hall", 44, 98, 10, nudge=2)
    p("ek_signpost", 48, 104, 4)
    p("ek_forsaken_banner", 50, 100, 6)

    # ---- Khaz Varun's gate: the collapsed front of a Dark Iron city --------------------------------
    # The set-piece, and the thing the whole faction is about. No roof anywhere, and the arch over
    # the door is passable because the dungeon portal is under it.
    p(RU + "ruin_archway.png", 54, 128, 10, solid=False, nudge=0, road_ok=True, allow_overlap=True)
    for (x, y) in ((44, 128), (64, 128), (46, 138), (64, 138)):
        p(RU + "ruin_wall_arch.png", x, y, 7)
    p(RU + "ruin_tower_skulls.png", 48, 134, 9)
    p(RU + "ruin_tower_skulls.png", 62, 136, 8)
    p("ek_signpost", 52, 118, 4)
    p("ek_dead_oak", 42, 122, 6)
    p("ek_web_boulder", 70, 130, 5)

    # ---- the green belt: the only easy ground on the island -----------------------------------------
    T.grove(L, 82, 86, 8, 6, 8, PALMS, seed=4)
    T.grove(L, 108, 76, 7, 6, 7, PALMS, seed=5)
    T.grove(L, 66, 100, 7, 5, 6, PALMS, seed=6)
    p("ek_signpost", 90, 86, 4)
    b("ek_wayshrine", 112, 72, 5, nudge=2)

    # ---- the two passes: round the volcano's flanks --------------------------------------------------
    # Both arrival columns ((32,7) and (140,7)) are left clear; the markers sit beside the road.
    p("ek_signpost", 28, 16, 4)
    p("ek_signpost", 136, 16, 4)
    for (x, y) in ((40, 26), (46, 34), (130, 28), (126, 38)):
        p("ek_web_boulder", x, y, 6)

    # ---- the shallows: four islets, each with a reason to wade out ------------------------------------
    L.deco("boat_orc", 144, 134, 6, path_dir=CO)          # a barge that did not make the harbour
    p("ek_scarlet_crates", 152, 126, 3)
    p(RU + "ruin_stone_ring.png", 160, 112, 5, solid=False)
    p("ek_web_boulder", 153, 145, 5)
    p("ek_signpost", 136, 116, 4)
    p("ek_dead_oak", 129, 145, 5)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_tempest_shallows():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/tempest_shallows_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
