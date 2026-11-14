"""
Hand-built Arathi East (200x170): the highlands running out into a drowned coast. Levels 37-40.

Kyle, 2026-11-01: "east can be 37-40... the far east will be more oceanfront and islands (we can have the
land broken. So for the eastern highlands we start a bit with the highlands but we have an archipelago
there as well full of pirates and two sea caves)."

ARCHETYPE: THE COAST THAT ARRIVED. West is a map split by a wall; Central is a bowl you see all of at
once. This one is a map that STOPS. You come in on the same highland you have walked for two zones, and a
third of the way across it simply ends - not at a cliff, at a waterline - and everything east of that is
the tops of hills with the sea in between them.

THE ISLANDS ARE ARATHI. That is the whole idea and it is why this zone is not just "a pirate cove tacked
onto the highlands". Every island out there is a highland hilltop with the same heather and the same bare
rock as the mainland, and the things on them are Arathi things that used to be inland - a barrow, a
boundary wall running into the water, a shepherd's bothy on what is now a rock in the sea. The Integration
put the sea where the valleys were. You can read the old country in the shapes.

THE WRACKLINE are what moved in. The wrack line is the band of weed and wreckage a tide leaves on a
beach, and the crew named themselves after it because that is what they live on. Not Bloodsail - Kyle's
call was faithful inland, ORIGINAL at sea, and the Bloodsail are a Stranglethorn fixture three zones
south. These are local: Arathi coast people whose villages went under, working the drowned ones.

HOW THE WATER WORKS. sea_field is positive east of the mainland coastline and negative on any island
blob, so one function makes both shorelines. Everything within SHORE_W of a shore is shallow and
wadeable; past that it is deep and you need a crossing. FLATS force shallow where two islands should be
linked on foot, so the archipelago has a walkable spine and a swimmable remainder rather than being a set
of unreachable rocks.

PLACES (north is up; Arathi Central lies west):
    W     the west seam (4,92): back to Arathi Central
    WC    SALTSPUR LANDING (46,96): the Horde beachhead on the last of the solid ground. A camp, not a town.
    NW    THE DROWNED BARROW (34,40): a hill barrow with the sea in its mouth. This zone's land cave.
    C     THE WRACKLINE SHORE (84..100): where the highland stops
    E     THE ARCHIPELAGO (100..196): six islands, the old hilltops
    E     WRACKLINE HOLD (150,62): the crew's sea cave, under Gallowmast
    SE    THE TIDEWRACK (160,134): a flooded sea cave on the southern rocks

HARD CONTRACTS (world/portal_manager.py)
  (4, 92)    <-> Arathi Central        seam. Arathi Central's east portal is (186,92).
  (34, 38)   <-> The Drowned Barrow    the land cave
  (150, 60)  <-> Wrackline Hold        sea cave one, the crew's hold
  (160, 132) <-> The Tidewrack         sea cave two
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob, lobe, rock_spurs

KEY = "arathi_east"
NAME = "Arathi East"
DESC = ("The highlands run out into water: a drowned coast and six island hilltops held by the Wrackline, "
        "who live off what the tide leaves.")
REGION = "Eastern Kingdoms - Arathi Highlands"
W, H = 200, 170
BAKED_DIR = "assets/tiles/arathi_east/baked"
IS_TOWN = False
BASE_TILE = "grass"
SEED = 333

RU = "assets/tiles/ruins/"
CO = "assets/tiles/coastal_props/"

PORTALS = {(4, 92): "Arathi Central",
           (34, 38): "The Drowned Barrow",
           (150, 60): "Wrackline Hold",
           (160, 132): "The Tidewrack"}
ARRIVALS = [(4, 94), (34, 40), (150, 62), (160, 134)]
START = (10, 92)

#: How wide the wadeable band is around every shore. Past this you are swimming. Raised from 3.2
#: on Kyle's note that "deep water is nice but too much is wasted space" - a wider wadeable
#: shelf turns the gaps between islands into places you fight rather than places you cross.
SHORE_W = 4.6

# ---- roads -----------------------------------------------------------------------------------------
# Only the MAINLAND has roads. Out in the archipelago there is no road, because nobody out there builds
# one - you follow the flats between islands or you swim, and that difference in how you move is what
# makes the crossing read as leaving the land behind.
ROADS = {
    "coast":   ([(4, 92), (24, 94), (44, 96), (62, 98), (78, 100)], 3.0),
    "barrow":  ([(40, 88), (36, 66), (34, 46), (34, 40)], 2.4),
    "south":   ([(30, 100), (40, 124), (58, 138), (76, 130)], 2.4),
}
_RS = K.RoadSet(ROADS)
road_dist = _RS.dist


def paved(gx, gy):
    """Worn stone: Saltspur Landing's hard standing, and the barrow's forecourt."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    camp = lobe(gx, gy, 46.0, 96.0, 9.0, 7.0) + 0.5 * wob(gx, gy)
    barrow = lobe(gx, gy, 34.0, 42.0, 6.0, 5.0) + 0.5 * wob(gx, gy)
    return np.maximum(camp, barrow) - 1.2


# ---- the water, and the islands --------------------------------------------------------------------
#: The mainland coastline: x of the waterline as a function of y. Integer harmonics only - a
#: non-integer harmonic leaves a seam where the function wraps, and the painted shore and the tile grid
#: are both derived from this one curve.
def coast_x(gy):
    gy = np.asarray(gy, float)
    a = gy / H * 2.0 * np.pi
    return 88.0 + 6.0 * np.sin(a) + 3.5 * np.sin(2.0 * a + 1.1) + 2.0 * np.sin(3.0 * a + 0.4)


#: THE ISLANDS. Kyle, 2026-11-01: "Make the islands more random and less anal beads" and "Islands can
#: be odd shapes too bro." He was right - the first pass was six near-identical ellipses in two tidy
#: rows, which is a string of beads and not a drowned country.
#:
#: Each island is now a LIST OF LOBES (cx, cy, rx, ry, rot) unioned together, so the silhouette comes
#: out of how the lobes overlap rather than being one smooth oval, and each one gets a deliberately
#: distinct shape:
#:
#:   The Wrack          a comma - a round head with a tail trailing south-west
#:   Gallowmast Isle    a boomerang, with a sheltered bay in the crook. The crew's wharf is in the bay,
#:                      which is WHY the hold is on this island and not another one.
#:   The Far Cairn      a long thin spit running north-east, barely wide enough to stand on in places
#:   Bothy Rock         a crescent open to the south, the bothy on the inside of the curve
#:   The Tidewrack      three lobes barely touching: a hill that broke rather than drowned
#:   The Bonepicker     a near-column, tall and narrow, which is why only birds use it
#:
#: SKERRIES carry no content and exist so the water is not empty between the six that do.
#: Each island also gets its own wobble amplitude and phase (the last two numbers) so the outlines are
#: not all smoothed the same way - the big sheltered one is smooth, the broken one is ragged.
ISLANDS = {
    "The Wrack": ([(113.0, 52.0, 10.0, 9.0, 0.0),
                   (120.0, 60.0, 6.5, 5.0, 35.0),
                   (125.0, 66.0, 3.4, 2.8, 0.0)], 1.3, 0.0),
    "Gallowmast Isle": ([(146.0, 56.0, 13.0, 8.0, 25.0),
                         (156.0, 70.0, 9.0, 12.0, 15.0),
                         (139.0, 68.0, 7.0, 6.0, 0.0)], 0.9, 1.7),
    "The Far Cairn": ([(178.0, 56.0, 9.0, 4.5, -35.0),
                       (188.0, 46.0, 7.5, 4.0, -35.0),
                       (195.0, 38.0, 4.5, 3.4, 0.0)], 1.1, 3.1),
    "Bothy Rock": ([(118.0, 104.0, 7.5, 6.0, 0.0),
                    (126.0, 108.0, 6.5, 5.0, 40.0),
                    (129.0, 118.0, 7.0, 6.0, -20.0)], 1.2, 0.8),
    "The Tidewrack": ([(152.0, 128.0, 8.0, 6.5, 20.0),
                       (163.0, 134.0, 7.0, 5.5, -30.0),
                       (155.0, 142.0, 5.5, 4.5, 0.0)], 1.9, 2.4),
    "The Bonepicker": ([(189.0, 108.0, 5.0, 9.5, 10.0),
                        (186.0, 118.0, 4.0, 4.5, 0.0)], 1.0, 4.2),
    # ---- the middle band. Kyle, 2026-11-01: "make sure the top and bottom are connected if possible
    # by shallows. Deep water is nice but too much is wasted space." These three sit in what was an
    # empty trench between the north and south chains and turn two dead ends into one loop.
    "The Teeth": ([(106.0, 74.0, 4.0, 7.0, 25.0),
                   (111.0, 81.0, 3.4, 5.0, -15.0),
                   (102.0, 69.0, 3.0, 3.0, 0.0)], 1.8, 1.1),        # jagged, close inshore
    "The Middenstone": ([(134.0, 86.0, 9.0, 7.0, -20.0),
                         (142.0, 92.0, 6.0, 5.5, 30.0),
                         (128.0, 93.0, 5.0, 4.0, 0.0)], 1.2, 3.6),  # the hinge of the loop
    "Saltquern": ([(170.0, 82.0, 7.5, 5.0, 40.0),
                   (176.0, 90.0, 5.0, 6.5, 0.0),
                   (164.0, 76.0, 4.0, 3.4, 0.0)], 1.4, 2.0),        # a mill-stone shape, east side
    # The south-west quarter of the sea was still one dead trench after the middle band went in. This
    # fills it and gives the southern loop a second way round.
    "The Spindrift": ([(106.0, 138.0, 6.0, 9.0, -25.0),
                       (113.0, 148.0, 5.5, 4.5, 15.0),
                       (99.0, 130.0, 4.0, 3.4, 0.0)], 1.6, 0.4),
    # skerries - scenery, no content, no flats to them
    "_skerries": ([(134.0, 40.0, 3.6, 2.6, 20.0),
                   (108.0, 84.0, 3.0, 4.2, 0.0),
                   (173.0, 94.0, 4.0, 2.8, -25.0),
                   (180.0, 150.0, 3.4, 3.0, 0.0),
                   (128.0, 80.0, 2.6, 2.2, 0.0),
                   (196.0, 70.0, 3.0, 4.0, 15.0)], 1.5, 5.0),
}

#: Shallow crossings. Without these the islands are unreachable rocks; with them the archipelago has a
#: walkable spine (mainland -> Wrack -> Gallowmast -> Far Cairn) and a southern loop you have to wade.
#: Each one is checked against coast_x(y) and the real lobe edges, not by eye - see the note on FLATS
#: being the thing that silently strands an island.
FLATS = [
    (101.0, 55.0, 14.0, 6.0),       # the shore to The Wrack
    (130.0, 57.0, 9.0, 5.0),        # Wrack to Gallowmast
    (167.0, 58.0, 10.0, 5.0),       # Gallowmast to the Far Cairn
    (100.0, 102.0, 16.0, 6.0),      # the shore to Bothy Rock
    (142.0, 124.0, 10.0, 6.0),      # Bothy to the Tidewrack rocks
    # Reshaping the islands moved both ends of this one: the Tidewrack now reaches east to ~x170
    # at y~134 and the Bonepicker hangs south to y~122, so the flat has to span the DIAGONAL
    # between them. At (176,120) it missed and the Bonepicker sealed to rock - 0 walkable tiles.
    (176.0, 126.0, 11.0, 9.0),      # Tidewrack to the Bonepicker
    # ---- the middle band, north-south. These are what make the archipelago a LOOP instead of two
    # dead-end strings, and they are the reason the trench between the chains is no longer dead water.
    (102.0, 64.0, 8.0, 7.0),        # The Wrack down to The Teeth
    (110.0, 90.0, 8.0, 7.0),        # The Teeth down toward Bothy Rock
    (122.0, 88.0, 9.0, 6.0),        # The Teeth across to The Middenstone
    (138.0, 76.0, 8.0, 8.0),        # Gallowmast down to The Middenstone
    (134.0, 102.0, 8.0, 7.0),       # The Middenstone down to Bothy Rock
    (156.0, 84.0, 9.0, 6.0),        # The Middenstone across to Saltquern
    (176.0, 72.0, 7.0, 9.0),        # Saltquern up to the Far Cairn
    (182.0, 98.0, 7.0, 8.0),        # Saltquern down to the Bonepicker
    # Wide on purpose: at (99,120,8,9) this stopped three tiles short of Bothy Rock's west lobe
    # and The Spindrift sealed. The gap between two islands is measured lobe edge to lobe edge.
    (104.0, 122.0, 13.0, 11.0),     # Bothy Rock down to The Spindrift
    (124.0, 142.0, 11.0, 7.0),      # The Spindrift east to the Tidewrack rocks
]


def _ell(gx, gy, cx, cy, rx, ry, rot=0.0):
    dx, dy = gx - cx, gy - cy
    if rot:
        r = np.radians(rot)
        c, s_ = np.cos(r), np.sin(r)
        dx, dy = c * dx + s_ * dy, -s_ * dx + c * dy
    return (1.0 - np.sqrt((dx / rx) ** 2 + (dy / ry) ** 2)) * min(rx, ry)


def island_field(gx, gy):
    """>0 on any island. Unions every lobe of every island, each group wobbled by its own amount.

    The per-group wobble is what stops the archipelago reading as one artist's hand: the sheltered
    boomerang comes out smooth at 0.9 and the broken hill comes out ragged at 1.9, from the same
    function.
    """
    best = np.full(np.shape(gx), -99.0)
    for (lobes, amp, ph) in ISLANDS.values():
        grp = np.full(np.shape(gx), -99.0)
        for (cx, cy, rx, ry, rot) in lobes:
            grp = np.maximum(grp, _ell(gx, gy, cx, cy, rx, ry, rot))
        best = np.maximum(best, grp + amp * wob(gx + ph * 7.0, gy + ph * 5.0))
    return best


def flat_field(gx, gy):
    best = np.full(np.shape(gx), -99.0)
    for (cx, cy, rx, ry) in FLATS:
        best = np.maximum(best, _ell(gx, gy, cx, cy, rx, ry))
    return best


#: Where each named island sits, for subzones, props and QA - the centroid of its lobes.
ISLAND_CENTRES = {n: (sum(l[0] for l in lobes) / len(lobes), sum(l[1] for l in lobes) / len(lobes))
                  for n, (lobes, _a, _p) in ISLANDS.items() if not n.startswith("_")}


def water_field(gx, gy):
    """>0 in water. East of the mainland coast AND not standing on an island."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    return np.minimum(gx - coast_x(gy), -island_field(gx, gy))


def deck_field(gx, gy):
    """The jetty at Saltspur Landing, and the crew's plank wharf under Gallowmast."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    best = np.full(np.shape(gx), -9.0)
    for (x0, x1, y0, y1) in ((82.0, 96.0, 99.0, 101.4), (136.0, 148.0, 75.0, 77.4)):
        best = np.maximum(best, np.minimum.reduce([gx - x0, x1 - gx, gy - y0, y1 - gy]))
    return best


# ---- rock -------------------------------------------------------------------------------------------
# The mainland keeps the highland ridges. Out at sea the rock is SEA STACKS: cliff collision on a sand
# base, so the engine draws no water shimmer over them (playbook section 3).
SPURS = [
    (0, 8, 70, 14, 3.6),            # the north ridge, mainland
    (0, 28, 8, 150, 3.4),           # the west ridge, pierced by the seam
    (12, 150, 80, 158, 3.6),        # the south ridge
    (56, 30, 80, 70, 3.0),          # the headland spine above the landing
]
OUTCROPS = [
    (24, 62, 2.8, 2.2), (58, 50, 2.6, 2.0), (20, 118, 2.8, 2.2), (62, 116, 2.6, 2.0), (46, 140, 2.6, 2.0),
    (70, 86, 2.4, 1.8),
]
#: Sea stacks, out in the water between the islands - the drowned country's chimneys.
#: Three of these were swallowed by the new middle-band islands and moved out into open water.
STACKS = [(90, 108, 2.6, 2.2), (146, 112, 2.8, 2.4), (190, 134, 2.6, 2.2), (112, 136, 2.6, 2.2),
          (196, 60, 2.4, 2.0), (146, 150, 2.6, 2.2), (176, 36, 2.4, 2.0)]


def cliff_field(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    edge = np.minimum.reduce([gx, W - gx, gy, H - gy])
    # The map edge wall only applies to the MAINLAND side and the far rim; the sea runs to the border
    # elsewhere, which is what stops the archipelago reading as a pond in a box.
    rock = (5.0 + 3.0 * wob(gx * 0.5, gy * 0.5) + 1.2 * wob(gx * 1.4, gy * 1.4)) - edge
    rock = np.where((gx > 92.0) & (gy > 6.0) & (gy < H - 6.0), -9.0, rock)
    rock = np.maximum(rock, rock_spurs(gx, gy, SPURS, OUTCROPS))
    for (cx, cy, rx, ry) in STACKS:
        rock = np.maximum(rock, _ell(gx, gy, cx, cy, rx, ry) + 0.4 * wob(gx * 1.7, gy * 1.7))
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    rock = np.where(deck_field(gx, gy) > -1.0, np.minimum(rock, -0.5), rock)
    return rock


def fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    wet = water_field(gx, gy)
    # Deep is water further than SHORE_W from any shore, EXCEPT where a flat forces a crossing.
    deep = np.minimum(wet - SHORE_W, -flat_field(gx, gy))
    return dict(cliff=cliff_field(gx, gy), shallow=wet, deep=deep, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


# ---- subzones (x, y, w, h) ---------------------------------------------------------------------------
SUBZONES = [
    ("The Last Highland", 8, 60, 60, 46),
    ("The Drowned Barrow", 16, 24, 40, 34),
    ("Saltspur Landing", 32, 84, 36, 26),
    ("The Southern Moor", 20, 112, 56, 42),
    ("The Wrackline Shore", 72, 40, 32, 110),
    # Derived from each island's real lobe bounding box, not drawn by eye - reshaping the islands
    # moved every one of them and a subzone rectangle that no longer covers its island is a table
    # that never rolls.
    ("The Wrack", 101, 41, 31, 31),
    ("Gallowmast Isle", 130, 44, 39, 41),
    ("The Far Cairn", 168, 32, 35, 34),
    ("Bothy Rock", 108, 96, 31, 32),
    ("The Tidewrack", 142, 119, 31, 31),
    ("The Bonepicker", 180, 96, 18, 30),
    ("The Teeth", 96, 60, 22, 30),
    ("The Middenstone", 120, 76, 32, 26),
    ("Saltquern", 157, 69, 28, 30),
    ("The Spindrift", 92, 118, 30, 40),
]

# ---- baker config -------------------------------------------------------------------------------------
# Same heather and rock as the rest of Arathi, with shore and sand only at the waterlines. The ISLANDS
# use the same materials as the mainland on purpose - they are highland hilltops, not tropical cays, and
# reading that off the ground is the zone's one idea.
BASE = {"grass": 0.38, "dry": 0.26, "rocky": 0.24, "forest": 0.12}
PAINT = {
    "grass":  [(40, 92, 30, 20, 1.0), (30, 124, 26, 18, 0.9), (116, 58, 13, 10, 0.9), (150, 64, 17, 13, 0.9),
               (124, 112, 14, 11, 0.85), (158, 132, 15, 12, 0.85)],
    "dry":    [(40, 50, 26, 18, 0.95), (62, 74, 20, 16, 0.85), (184, 52, 12, 11, 0.8),
               (188, 110, 11, 9, 0.8), (22, 68, 18, 14, 0.8)],
    "rocky":  [(34, 42, 12, 9, 0.9), (150, 60, 12, 9, 0.85), (160, 132, 12, 9, 0.85),
               (106, 80, 6, 5, 0.8), (134, 92, 6, 5, 0.8), (170, 88, 6, 5, 0.8), (62, 50, 14, 11, 0.7)],
    "shore":  [(88, 90, 8, 60, 1.0), (116, 58, 15, 12, 0.9), (150, 64, 19, 15, 0.9), (184, 52, 14, 13, 0.9),
               (124, 112, 16, 13, 0.9), (158, 132, 17, 14, 0.9), (188, 110, 13, 11, 0.9)],
    "meadow": [(46, 96, 12, 9, 0.85), (36, 112, 12, 9, 0.7)],
    "forest": [(26, 130, 14, 10, 0.8), (54, 134, 12, 9, 0.75), (18, 78, 12, 9, 0.7)],
    "earth":  [(46, 96, 8, 6, 0.9), (34, 42, 6, 4, 0.85), (150, 62, 7, 5, 0.8)],
    "gravel": [(4, 94, 7, 5, 0.6), (88, 100, 8, 4, 0.6)],
}
COBBLE = [(46, 96, 8, 6, 0.9), (34, 42, 6, 5, 0.85)]

# ---- NPC spots -----------------------------------------------------------------------------------------
# Saltspur Landing is a CAMP, not a town - so no inn and no flight master, and the standing "every town
# needs both" rule does not bite. Hammerfall one zone west is the hub for this whole stretch.
NPC_POSITIONS = {
    # SALTSPUR'S SIX MOVED OUT on 7 Nov - the landing is its own zone now
    # (tools/handbuilt_saltspur_landing.py). They are listed there, spread one per
    # thing the landing does instead of six in a 12x6 box of open coast. Leaving
    # them here would paint "npc" interaction tiles on ground nobody stands on.
    # The inn and the flight master go WITH them: the reasoning that earned this
    # beachhead both - only settlement in the 37-40 band, across an archipelago
    # from anywhere else - is unchanged by which zone they stand in.
    "arathi_barrow_warden": (38, 50),          # outside the barrow, not going in
    "arathi_wreck_salvager": (82, 108),        # working the shore south of the jetty
    "arathi_bothy_hermit": (120, 105),         # on Bothy Rock, the only soul out there
}

#: (188,45) was on the Far Cairn before the islands were reshaped and ended up in open water.
CHESTS = [(30, 46), (58, 86), (36, 128), (114, 53), (156, 68), (189, 44), (122, 107), (157, 136),
          (134, 86), (170, 82), (107, 75), (106, 138)]

OAKS = [("ek_willow", 8, 0.30), ("ek_pine_trio", 7, 0.32), ("ek_dead_oak", 7, 0.28), ("ek_willow", 7, 0.30)]
FOREST = dict(seed=39, count=58, rim=13, thorn=8, names=[
    ("ek_willow", 8, 0.30), ("ek_dead_oak", 7, 0.28), ("ek_pine_trio", 7, 0.32),
    ("ek_thorn_bush", 4, 0.40)])


def dress(L):
    p, b = L.prop, L.bld
    ENT = T.ENT

    # ---- SALTSPUR LANDING: the cut in the bluff, and what is outside it ----------------------------
    # The landing itself became its own zone on 7 Nov. What stays on this side is the
    # way in and the working shore around it, so the coast road ends at a door rather
    # than at a thickening of props. Portal tile (50,96) - world/portal_manager.py.
    # Spaced by FOOTPRINT, not by anchor distance. First pass put the tower six
    # tiles from the gatehouse, which sounds clear and is not: these are twelve
    # and thirteen tiles tall, so the gate was drawn 94% through the tower.
    # tools/qa_building_overlap.py measures the rectangles.
    b("orc_great_gatehouse", 50, 94, 13, solid=False, road_ok=True, nudge=0)
    b("orc_signal_beacon", 60, 88, 11, nudge=2)
    p("ek_signpost", 56, 98, 4)
    p(CO + "fish_drying_rack.png", 48, 104, 4)
    p(CO + "fish_crates_traps.png", 40, 106, 4)
    p(CO + "dock_lantern_post.png", 84, 100, 5)
    # MOORED BESIDE the jetty, not parked on top of it: the jetty is the strip of ground at
    # y=99-100 and the boat's keel was on it. Four tiles south puts it in the water alongside.
    # deco, not prop: prop() refuses deep water and silently drops the sprite.
    L.deco("boat_orc", 92, 106, 5, path_dir=CO)

    # ---- THE DROWNED BARROW: a hill barrow with the sea coming into its mouth -----------------------
    for (x, y) in ((26, 34), (42, 34)):
        p("ek_web_boulder", x, y, 6)
    p(RU + "ruin_stone_ring.png", 34, 48, 5, solid=False)
    p("ek_grave_hand", 28, 46, 3, solid=False)
    p("ek_open_grave", 40, 48, 3, solid=False)

    # ---- THE WRACKLINE SHORE: where the highland stops -----------------------------------------------
    # The boundary wall is the zone's thesis in one object: an Arathi field wall running off the land
    # and into the water, because it was built when there was no water here.
    for (x, y) in ((86, 62), (88, 70), (90, 78)):
        p(RU + "ruin_wall_arch.png", x, y, 5, solid=False, allow_overlap=True)
    p(CO + "driftwood_pile.png", 84, 120, 4)
    p(CO + "driftwood_pile.png", 88, 46, 4)
    p(CO + "rowboat_wreck.png", 92, 134, 7)

    # ---- THE WRACK: the stepping stone ----------------------------------------------------------------
    p(RU + "ruin_stone_ring.png", 113, 52, 5, solid=False)
    p(CO + "driftwood_pile.png", 122, 63, 4)
    b("bd_sentry_leanto", 119, 58, 6, nudge=2)

    # ---- GALLOWMAST ISLE: the crew's island, and the hold under it -----------------------------------
    # The Wrackline get the BANDIT sheet, not a tropical pirate set: they are Arathi coast people whose
    # villages went under, working the drowned ones, so their buildings are the ones they grew up in.
    # The wharf sits in the crook of the boomerang - the sheltered bay is why the hold is here.
    b("bd_warehouse", 156, 72, 9, nudge=2)
    b("bd_lookout_tower", 145, 53, 12, nudge=2)
    b("bd_fence_shop", 140, 68, 8, nudge=2)
    p(CO + "fish_crates_traps.png", 153, 66, 4)
    p(CO + "dock_lantern_post.png", 151, 70, 5)
    p("ek_gibbet", 152, 58, 6)

    # ---- THE FAR CAIRN: the outermost, and the oldest ------------------------------------------------
    p(RU + "ruin_bone_pillars.png", 188, 46, 7)
    p(RU + "ruin_stone_ring.png", 179, 56, 5, solid=False)
    p("ek_web_boulder", 194, 39, 5)

    # ---- BOTHY ROCK: a shepherd's hut on what is now a rock in the sea --------------------------------
    # The bothy sits on the INSIDE of the crescent, which is the only sheltered ground on it.
    b("bd_sentry_leanto", 124, 109, 6, nudge=2)
    p("ek_farm_fence", 118, 104, 3, solid=True)
    p("ek_farm_fence", 129, 117, 3, solid=True)
    p(CO + "driftwood_pile.png", 130, 121, 4)

    # ---- THE TIDEWRACK: the flooded cave, and the rocks round it --------------------------------------
    p(CO + "rowboat_wreck.png", 155, 142, 7)
    p(CO + "driftwood_pile.png", 163, 134, 4)
    b("bd_boat_shed", 152, 128, 8, nudge=2)

    # ---- THE BONEPICKER: a bird rock, and what they have picked ---------------------------------------
    p("ek_cross_crows", 189, 105, 5)
    p(RU + "ruin_bone_pillars.png", 186, 118, 6)

    # ---- the mainland moor and the seam ----------------------------------------------------------------
    T.grove(L, 26, 130, 8, 6, 8, OAKS, seed=10)
    T.grove(L, 54, 136, 7, 5, 6, OAKS, seed=11)
    b("ek_wayshrine", 30, 104, 5, nudge=2)
    p("ek_signpost", 14, 92, 4)
    p(RU + "ruin_wall_arch.png", 10, 84, 6)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_arathi_east():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/arathi_east_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
