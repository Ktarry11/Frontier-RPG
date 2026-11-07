"""
Hand-built Saltspur Landing (68x56): the Horde beachhead on the Arathi coast, levels 37-40.

TOWN ARCHETYPE: THE BEACHHEAD.  One jetty out into the water, one track up off the shingle to a
cut in the bluff, and everything else crammed into the strip of flat ground between them.  The sea
closes the east, the bluff closes the west, and the only two ways out are the gate in the cut and
the boat at the jetty head.  Nothing here was built to last: stores under tarps above the tideline,
a shipwright working on the hull she pulled up, tents rather than houses, and the inn is the one
timber building because somebody decided they were staying.

(Ratchet is the other harbour town and the difference matters: Ratchet is a PORT - a bay with three
piers and a promenade, where the town exists because the boats come.  This is a LANDING, which is a
port that has not happened yet: one jetty, a track, and a camp that is still unpacking.  Same size
on purpose - Kyle, 7 Nov: "keep saltspur small... Saltspur should be ratchet size. A small dock and
some houses.")

HARD CONTRACT - THE SEA AND THE BLUFF ARE THE WALLS.  Deep water east of the shoreline
(walkable=False) and cliff west of the bluff line, so the strand is enclosed without a single wall
sprite.  The jetty is deck laid over water, which kind_from_fields resolves last and so paints
plank over deep.

    bluff cut (2,28) -> Arathi East
      |
    the track  --  THE STRAND  --  jetty --> open water
                   stores, inn,
                   shipwright, tents

HARD CONTRACTS (world/portal_manager.py): portal (2,28) <-> Arathi East (50,96); arrival 3 tiles in.
Prop rule (Kyle): less is more; logical for the room; a few centrepieces.
NPC ids are the ones already in data/npcs/*.json - this module MOVES them, it does not invent any.
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob

KEY = "saltspur_landing"
NAME = "Saltspur Landing"
DESC = "Saltspur Landing. A Horde beachhead on the Arathi coast: one jetty, one track, and a camp still unpacking."
REGION = "Eastern Kingdoms - Arathi Highlands"
W, H = 68, 56
BAKED_DIR = "assets/tiles/saltspur_landing/baked"
IS_TOWN = True
BASE_TILE = "grass"

PORTALS = {(2, 28): "Arathi East"}
ARRIVALS = [(5, 28)]
START = (8, 28)

ROADS = {
    # The track: in at the bluff cut, along the back of the strand, out onto the jetty.
    "track":  ([(1, 28), (9, 28), (18, 27), (28, 28), (36, 29)], 3.4),
    "stores": ([(20, 27), (21, 19), (22, 14)], 2.4),      # up to the stores under the bluff
    "camp":   ([(26, 30), (28, 38), (29, 44)], 2.4),      # down to the tents and the shipwright
}
PLAZA = (28, 28, 7.0, 5.0)           # the landing yard, where the track meets the jetty

#: The jetty: deck laid over water out to the boat.
DECKS = [(36.0, 54.0, 26.6, 29.4)]

_RS = K.RoadSet(ROADS)
road_dist = _RS.dist


def paved(gx, gy):
    cx, cy, rx, ry = PLAZA
    r = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
    return (1 - r) * min(rx, ry)


def shore(gy):
    """x of the waterline. The bay bites in at the jetty and the ground reaches out north and south."""
    gy = np.asarray(gy, float)
    return (38.0 + 4.5 * np.sin(0.11 * gy + 0.6) + 1.2 * np.sin(0.47 * gy)
            - 3.0 * np.exp(-((gy - 28.0) ** 2) / 80.0))


def deck_field(gx, gy):
    best = np.full(np.shape(gx), -9.0)
    for (x0, x1, y0, y1) in DECKS:
        e = np.minimum(np.minimum(gx - x0, x1 - gx), np.minimum(gy - y0, y1 - gy))
        best = np.maximum(best, e)
    return best


def cliff_field(gx, gy):
    """The bluff west, and the rim everywhere the strand is not.

    Same contract as Hammerfall and for the same reason: the enclosure is this
    function, not the scenery. The ONE hole is the bluff cut, carved after the rim
    is forced so a later edit cannot reopen the back of the landing.
    """
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    strand = np.maximum.reduce([
        # the flat strip behind the waterline, wide at the yard and tapering off
        14.0 - np.abs(gy - 28.0) * 0.62,
        # the stores shelf under the bluff, and the camp south of the yard
        9.0 - np.hypot((gx - 21.0) / 1.5, (gy - 17.0) / 1.0),
        9.0 - np.hypot((gx - 28.0) / 1.5, (gy - 41.0) / 1.0),
    ])
    strand = strand + 1.4 * wob(gx * 0.5, gy * 0.5)
    strand = np.maximum(strand, road_dist(gx, gy) + 2.4)
    strand = np.maximum(strand, deck_field(gx, gy) + 1.5)
    # the bluff: rock west of a wavering line
    rock = (11.0 + 2.2 * np.sin(0.17 * gy + 0.5) + 0.9 * np.sin(0.43 * gy)) - gx
    rock = np.maximum(rock, -strand)
    edge = np.minimum.reduce([gx, W - gx, gy, H - gy])
    rock = np.maximum(rock, (3.5 - edge) * 1.4 + 0.3 * wob(gx * 1.3, gy * 1.3))
    cut = (np.abs(gy - 28.0) < 3.0) & (gx < 12)
    rock = np.where(cut, -1.0, rock)
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    # never rock under the jetty - that is water, and deck paints over it
    return np.where(deck_field(gx, gy) > -0.5, -9.0, rock)


def fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    sea = gx - shore(gy)
    cliff = cliff_field(gx, gy)
    return dict(cliff=np.where(sea > 0, -99.0, cliff),
                shallow=sea, deep=sea - 3.2, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


SUBZONES = [
    ("The Landing Yard", 20, 20, 20, 17),
    ("Saltspur Stores", 12, 8, 20, 14),
    ("The Shipwright's Beach", 18, 34, 22, 18),
]

# ---- baker config (read by tools/bake_hillsbrad.py) ------------------------------------------------
BASE = {"shore": 0.40, "dry": 0.24, "rocky": 0.26, "grass": 0.10}
PAINT = {
    "shore":  [(30, 28, 12, 16, 1.0), (32, 44, 8, 9, 0.9), (31, 12, 7, 8, 0.85)],
    "gravel": [(28, 28, 7, 5, 0.85), (20, 27, 6, 4, 0.7)],
    "rocky":  [(13, 14, 7, 7, 0.85), (14, 44, 7, 7, 0.85)],
    "earth":  [(21, 17, 6, 5, 0.8), (28, 41, 6, 5, 0.8)],
}
COBBLE = []

# ---- NPC spots ---------------------------------------------------------------------------------
# SIX NPCs OVER 68x56, one per thing the landing does, instead of six standing in a 12x6 box of
# open coast. Kyle, 7 Nov: "Ensure NPCs, vendors, trainers are spaced out."
NPC_POSITIONS = {
    "saltspur_scout":            (9, 27),    # Scout Vel Ashgrave, watching the bluff cut
    "saltspur_quartermaster":    (21, 16),   # Quartermaster Dreg, up at the stores
    "saltspur_innkeeper":        (24, 31),   # Innkeeper Vara Dunn, at the one timber building
    "saltspur_bosun":            (32, 28),   # Bosun Kaz Tidewright, at the landward end of the jetty  # moved off shallow water 7 Nov
    "saltspur_windrider_master": (33, 22),   # Wind Rider Keeper Ozra, on the rock above the yard
    "saltspur_shipwright":       (28, 43),   # Shipwright Oona Keelsplice, at the hauled-up hull
}
CHESTS = [(15, 10), (16, 48), (50, 28)]

# rim=2 and count=8: at rim=5 the edge planting reached into the strand and put
# pines THROUGH the camp buildings - Kyle, 7 Nov: "don't overlap houses". The
# strand is 14 tiles wide at its widest, so anything reaching 5 tiles in from the
# bluff is standing in the town.
FOREST = dict(seed=63, count=8, rim=2, thorn=9, names=[
    ("ek_thorn_bush", 4, 0.46), ("ek_dead_oak", 6, 0.28), ("ek_pine_trio", 7, 0.26)])


def dress(L):
    p, b = L.prop, L.bld

    # ---- the jetty, and the boat at the end of it
    for x in (38, 44, 50):
        p("ek_scarlet_crates", x, 26, 3)
    b("orc_watch_tower", 36, 32, 11)

    # ---- the landing yard: the one timber building, the stores under the tarp
    b("orc_mess_hall", 24, 33, 11, nudge=2)            # the inn: a beachhead's inn is its mess
    b("orc_supply_store", 20, 18, 10, nudge=2)
    b("orc_quartermaster_post", 25, 14, 9, nudge=2)
    p("ek_scarlet_crates", 26, 26, 4)
    p("ek_signpost", 15, 28, 4)
    p("ek_forsaken_banner", 30, 24, 6)

    # ---- the camp. NOT generic_tent_a/b, which is what shipped here first and
    # what Kyle called "that old Horde one": those two are from the older chunky
    # low-resolution family and - worse - they have a DIRT PATCH PAINTED INTO THE
    # SPRITE, so each one sat on a brown oval of its own that had nothing to do
    # with the ground under it. On shingle that reads as a bug. The orc set from
    # the 30-building sheet is the newer painterly family and has no baked ground.
    b("orc_healer_house", 31, 37, 9, nudge=2)
    b("orc_officers_house", 23, 40, 9, nudge=2)
    # Pulled in off the bluff: at x=19 the strand is barely three tiles wide here
    # and the bluff planting grew straight through the roof.
    b("orc_smokehouse", 24, 45, 8, nudge=2)

    # ---- the shipwright's beach: the hull she pulled up
    p("ek_farm_cart", 32, 46, 4)
    p("ek_scarlet_crates", 23, 47, 4)

    # ---- the bluff cut
    b("orc_great_gatehouse", 6, 28, 12, solid=False, road_ok=True, nudge=0)
    b("orc_watch_tower", 10, 20, 11)
    b("orc_watch_tower", 10, 36, 11)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_saltspur_landing():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/saltspur_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
