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
    W      ASHCLAIM LANDING (74,66): the jetty from Saltspur. Arrival.
    SW     KHAZ VARUN'S GATE (102,76): the collapsed gate of the old Dark Iron city. The set-piece.
    C      THE GREEN BELT: jungle across the middle, the only easy ground on the island.
    N      THE VOLCANO: its southern half. Open ground west and east of it - the two passes.
    SE     THE SHALLOWS themselves: four islets, wadeable all the way out.

HARD CONTRACTS (world/portal_manager.py)
  (74, 66)   <-> Saltspur Landing      the boat. Saltspur's berth tile was left UNREGISTERED on
                                       7 Nov precisely until this zone existed.
  (58, 4)    <-> The Ashen Reach       the WEST pass, round the volcano's west flank
  (176, 4)   <-> The Ashen Reach       the EAST pass, round its east flank
  (102, 76)  <-> Khaz Varun, the Black Hollow

Prop rule (Kyle): less is more; logical for the room; a few centrepieces.
Earth references scale with zone level - this is the LOW half of the isle, so it stays near silent.
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools import tempest_isle_coast as C
from tools.tirisfal_kit import wob, lobe

KEY = "tempest_shallows"
#: Tilemap NAME is the key world/portal_manager.py looks portals up under, and it must match the
#: name create_all_zones registers. Eastern Hillsbrad shipped once with these out of step and every
#: portal in both zones was dead - you could walk in and never walk out.
NAME = "Tempest Shallows"
DESC = ("The south half of Tempest Isle: jungle under a volcano's southern flank, ringed by sea, "
        "with a dead Dark Iron city inland and a wadeable archipelago off the south-east.")
REGION = "Tempest Isle"
W, H = C.W, C.SHALLOWS_H
BAKED_DIR = "assets/tiles/tempest_shallows/baked"
IS_TOWN = False
BASE_TILE = "grass"
SEED = 521

RU = "assets/tiles/ruins/"

PORTALS = {(74, 66): "Saltspur Landing",
           (58, 4): "The Ashen Reach",
           (176, 4): "The Ashen Reach",
           (102, 76): "Khaz Varun, the Black Hollow"}
#: Arrival is 2 tiles INTO the map off an edge portal (+3 leaving a dungeon), so these columns are
#: kept clear of solid landmarks by hand in dress().
ARRIVALS = [(77, 66), (58, 7), (176, 7), (102, 73)]
START = (84, 66)

# ---- the coast: NOT DEFINED HERE ---------------------------------------------------------------
# tools/tempest_isle_coast.py owns the island, and this zone reads its SOUTHERN half - the Ashen
# Reach reads the northern half of the same curve, so the land either side of the border is one
# row of one coastline rather than two modules' guesses.
#
# THE NORTH HALF IS THE BIGGER ONE, deliberately. Kyle, 10 Nov: "the top one has more landmass!
# this is why we added islands in the southern one". The islets below are not decoration - they
# are how this smaller map gets the area the Reach gets from open ground.
ISLETS = C.ISLETS


def land_field(gx, gy):
    return C.land(KEY, gx, gy)


def islet_field(gx, gy):
    return C.islets(KEY, gx, gy)


def sea_field(gx, gy):
    """>0 in the sea. The islets are land standing in it."""
    import numpy as _np
    return -_np.maximum(land_field(gx, gy), islet_field(gx, gy))


def deck_field(gx, gy):
    """The jetty at Ashclaim Landing: deck laid over water out to the boat. kind_from_fields
    resolves deck last, so this paints plank over sea rather than leaving the player on water."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    return np.minimum.reduce([gx - 66.0, 82.0 - gx, gy - 64.0, 68.0 - gy])


# ---- roads --------------------------------------------------------------------------------------------
# The trunk is the Ashclaim's own cart track, cut this season: up off the jetty, east through the
# green belt, and forked north round BOTH flanks of the volcano. The ruin road runs the other way
# and is older and worse, because the dwarves did not cut it - they re-found it.
ROADS = {
    "trunk":   ([(76, 66), (92, 60), (116, 52), (142, 46), (166, 40), (182, 32)], 3.2),
    "west":    ([(92, 60), (76, 42), (62, 22), (58, 6)], 2.6),       # round the volcano's west flank
    "east":    ([(166, 40), (174, 22), (176, 6)], 2.6),              # round its east flank
    "ruin":    ([(88, 66), (94, 72), (102, 76)], 2.4),               # along to Khaz Varun's gate
    "strand":  ([(142, 46), (156, 64), (168, 80), (176, 92)], 2.2),  # out to the shallows
}
_RS = K.RoadSet(ROADS)
road_dist = _RS.dist


def paved(gx, gy):
    """Worn stone: the landing apron, and Khaz Varun's forecourt under the rubble."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    apron = lobe(gx, gy, 84.0, 66.0, 8.0, 6.0) + 0.5 * wob(gx, gy)
    gate = lobe(gx, gy, 102.0, 74.0, 9.0, 7.0) + 0.5 * wob(gx, gy)
    return np.maximum(apron, gate) - 1.2


# ---- the volcano --------------------------------------------------------------------------------
# Defined in tempest_isle_coast.py, because it sits exactly ON the seam and a mountain half-owned
# by two modules drifts the moment one of them is edited. This map sees its SOUTHERN half; the
# Reach sees the northern half and owns the Emberdeep's door.
def volcano_field(gx, gy):
    return C.volcano(KEY, gx, gy)


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
    iy = gy + float(C.SEAM_Y)          # islets are authored in ISLAND space
    for (cx, cy, rx, ry) in ISLETS:
        shelf = np.maximum(shelf, 30.0 - np.sqrt((gx - cx) ** 2 + (iy - cy) ** 2))
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
    ("Ashclaim Landing", 68, 54, 32, 26),
    ("The Green Belt", 104, 40, 60, 34),
    ("Khaz Varun's Gate", 86, 62, 38, 30),
    ("The Scoured Slope", 56, 6, 120, 30),
    ("The Tempest Shallows", 140, 60, 86, 76),
]

# ---- baker config -------------------------------------------------------------------------------------
# Tropical below, volcanic above. `grass`/`forest` carry the green belt, `dry`/`rocky` take over as
# the ground climbs toward the volcano, and `shore` runs the whole coast and the archipelago.
BASE = {"grass": 0.40, "forest": 0.24, "shore": 0.18, "dry": 0.07, "rocky": 0.11}
PAINT = {
    "grass":  [(118, 46, 36, 20, 1.0), (152, 40, 30, 16, 0.95), (92, 60, 24, 14, 0.9),
               (170, 54, 20, 14, 0.8)],
    "forest": [(114, 50, 22, 13, 0.95), (148, 44, 20, 12, 0.9), (96, 64, 16, 10, 0.8),
               (166, 58, 14, 10, 0.7)],
    "shore":  [(80, 66, 12, 12, 1.0), (176, 92, 18, 12, 0.95), (194, 82, 14, 10, 0.9),
               (160, 74, 14, 10, 0.85), (66, 30, 10, 12, 0.7), (118, 86, 16, 9, 0.8)],
    # Scorched ground HUGS THE VOLCANO. At full strength and out in the middle of the map this
    # read as a desert dropped into a jungle; it is ash-stained ground at the foot of a mountain,
    # so it is weaker and it stays near the slope.
    "dry":    [(84, 28, 22, 9, 0.55), (150, 26, 20, 9, 0.5), (116, 32, 26, 8, 0.45)],
    "rocky":  [(116, 20, 40, 15, 0.95), (76, 24, 20, 10, 0.85), (158, 22, 20, 10, 0.85),
               (102, 74, 14, 10, 0.85)],
    "earth":  [(84, 66, 7, 5, 0.9), (102, 74, 8, 6, 0.9), (168, 80, 7, 5, 0.7)],
    "gravel": [(58, 8, 7, 5, 0.7), (176, 8, 7, 5, 0.7), (94, 72, 6, 5, 0.6)],
    "marsh":  [(150, 72, 10, 7, 0.6)],
}
COBBLE = [(102, 74, 10, 7, 0.9), (84, 66, 7, 5, 0.8)]

# ---- NPC spots ----------------------------------------------------------------------------------------
# SPREAD, one per thing the landing does, rather than six standing in a box.
# Kyle, 7 Nov: "Ensure NPCs, vendors, trainers are spaced out." This is the Ashclaim's forward camp -
# the town proper is Cinderwharf, in the high zone, so this stays a camp.
NPC_POSITIONS = {
    "ts_landing_bosun": (84, 64),         # off the jetty head, first face you see
    "ts_landing_quartermaster": (90, 70),
    "ts_landing_surveyor": (88, 56),      # the goblin who is costing the island
    "ts_gate_watch": (98, 70),            # watching Khaz Varun's gate from outside it
    "ts_belt_prospector": (126, 50),      # out in the green belt
    "ts_shallows_wader": (160, 68),       # at the head of the strand road
}

CHESTS = [(176, 92), (194, 82), (116, 72), (144, 56), (70, 22), (190, 44), (138, 46)]

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
    L.deco("boat_orc", 68, 66, 7, path_dir=CO)
    # The portal tile (12,104) and the column beside it stay clear of solid props, or the player
    # arrives inside one. Durnholde shipped that wrong once.
    for (x, y) in ((82, 62), (82, 70)):
        p("ek_scarlet_crates", x, y, 3)
    b("orc_supply_store", 90, 72, 10, nudge=2)
    b("orc_mess_hall", 88, 58, 10, nudge=2)
    p("ek_signpost", 92, 66, 4)
    p("ek_forsaken_banner", 94, 62, 6)

    # ---- Khaz Varun's gate: the collapsed front of a Dark Iron city --------------------------------
    # The set-piece, and the thing the whole faction is about. No roof anywhere, and the arch over
    # the door is passable because the dungeon portal is under it.
    p(RU + "ruin_archway.png", 102, 76, 10, solid=False, nudge=0, road_ok=True, allow_overlap=True)
    for (x, y) in ((94, 78), (112, 78), (96, 86), (112, 86)):
        p(RU + "ruin_wall_arch.png", x, y, 7)
    p(RU + "ruin_tower_skulls.png", 98, 84, 9)
    p(RU + "ruin_tower_skulls.png", 112, 84, 8)
    p("ek_signpost", 96, 68, 4)
    p("ek_dead_oak", 88, 80, 6)
    p("ek_web_boulder", 118, 76, 5)

    # ---- the green belt: the only easy ground on the island -----------------------------------------
    T.grove(L, 114, 50, 8, 6, 8, PALMS, seed=4)
    T.grove(L, 148, 44, 7, 6, 7, PALMS, seed=5)
    T.grove(L, 96, 62, 7, 5, 6, PALMS, seed=6)
    p("ek_signpost", 128, 48, 4)
    b("ek_wayshrine", 156, 38, 5, nudge=2)

    # ---- the two passes: round the volcano's flanks --------------------------------------------------
    # Both arrival columns ((32,7) and (140,7)) are left clear; the markers sit beside the road.
    p("ek_signpost", 54, 14, 4)
    p("ek_signpost", 180, 14, 4)
    for (x, y) in ((68, 18), (74, 26), (166, 18), (160, 26)):
        p("ek_web_boulder", x, y, 6)

    # ---- the shallows: four islets, each with a reason to wade out ------------------------------------
    L.deco("boat_orc", 186, 100, 6, path_dir=CO)          # a barge that did not make the harbour
    p("ek_scarlet_crates", 178, 94, 3)
    p(RU + "ruin_stone_ring.png", 194, 84, 5, solid=False)
    p("ek_web_boulder", 188, 112, 5)
    p("ek_signpost", 168, 78, 4)
    p("ek_dead_oak", 168, 110, 5)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_tempest_shallows():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/tempest_shallows_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
