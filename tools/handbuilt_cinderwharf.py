"""
Hand-built Cinderwharf (104x84): the Ashclaim's town on Tempest Isle's north-east coast.

TOWN ARCHETYPE: THE JOINT VENTURE. Cinderwharf is two settlements that got welded together and
still do not match, because that is literally what the faction is - Thane Durgan Ashhold holds the
claim to Khaz Varun and Underwriter Nix Brackwhistle holds the paper on the claim. The town says
that in stone before anybody says a word:

    THE HOLD, west, by the gate. Dark Iron. Dressed granite and iron banding, a gatehouse, the
    Thane's Hall, a shrine. Quiet, square, built to outlast everyone in it - and built out of
    Khaz Varun's own salvaged stone, which the dwarves call a homecoming and the goblins call
    freight they did not have to buy.
    THE SEAM, middle. Where the two halves meet, and therefore where the shops are. The inn sits
    here on purpose: it is the one building both sides use.
    THE WHARF, east, on the water. Goblin. Crane gantry, ore store, the flight master, cargo
    stacked where it fell. Loud, cheap, and visibly temporary next to the granite.

You enter from the WEST, off the Ashen Reach, so you walk through the dwarves to reach the
goblins. That order is the joke and it is deliberate.

HARD CONTRACT - THE SEA AND THE RIM ARE THE WALLS. Towns are their own zones, enclosed by the
terrain field rather than by wall sprites: the rim is forced solid and the gate is cut afterwards,
so a later edit cannot quietly reopen the back of the town. Deep water east of the shoreline does
the same job on that side without a single fence.

NPCs ARE SPREAD, NOT CLUSTERED. Kyle, 10 Nov: "ensure the npcs are actually spread out!!" - and
7 Nov, of Saltspur: "Ensure NPCs, vendors, trainers are spaced out." Eleven NPCs over 104x84, one
per thing the town does, each standing where their work is: the thane in his hall, the smith at
the forge, the flight master on the pad, the broker at the cargo. Nobody is more than a few tiles
off a road, and no two share a quarter.

HARD CONTRACTS (world/portal_manager.py): portal (2,42) <-> The Ashen Reach (186,96).
Prop rule (Kyle): less is more; logical for the room; a few centrepieces.
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob

KEY = "cinderwharf"
NAME = "Cinderwharf"
DESC = ("The Ashclaim's town: a goblin wharf welded onto a Dark Iron hold, on Tempest Isle's "
        "north-east coast.")
REGION = "Tempest Isle"
W, H = 104, 84
BAKED_DIR = "assets/tiles/cinderwharf/baked"
IS_TOWN = True
BASE_TILE = "grass"
SEED = 613

PORTALS = {(2, 42): "The Ashen Reach"}
ARRIVALS = [(5, 42)]
START = (9, 42)

# ---- roads ---------------------------------------------------------------------------------------
# One high street from the gate to the jetty head, with three short spurs: up to the hall, down to
# the shrine, and out along the quay. A town this size does not need more, and more would turn the
# seam into a junction instead of a street.
ROADS = {
    "high":   ([(2, 42), (16, 42), (34, 44), (52, 44), (66, 44), (76, 44)], 3.4),
    "hall":   ([(24, 43), (24, 30), (26, 24)], 2.6),
    "shrine": ([(32, 45), (34, 58), (36, 66)], 2.4),
    "quay":   ([(64, 44), (66, 30), (68, 24)], 2.4),
    "yard":   ([(58, 45), (60, 58), (62, 66)], 2.4),
}
PLAZA = (52.0, 44.0, 8.0, 6.0)          # the market, on the seam between the two halves
_RS = K.RoadSet(ROADS)
road_dist = _RS.dist

#: The jetty: deck laid over water out to the moored hulls.
DECKS = [(76.0, 92.0, 40.0, 46.0)]
BOAT_SPRITE = (92, 43)


#: Streets are cut stone, not a dirt track. See ROAD_MAT in tools/bake_tempest.py.
ROAD_MAT = "cobble"


def paved(gx, gy):
    """Worked ground over the WHOLE town, not just a market square.

    A Dark Iron hold is paved; the first pass painted stone only in small blobs and the painter's
    flat 0.60 grass baseline won everywhere else, so the town came out as jungle with buildings
    standing in it. Inside the walls the ground is worked, and the green stops at the gate.
    """
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    cx, cy, rx, ry = PLAZA
    market = (1 - np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)) * min(rx, ry)
    hall = (1 - np.sqrt(((gx - 25.0) / 13.0) ** 2 + ((gy - 29.0) / 10.0) ** 2)) * 8.0
    gate = (1 - np.sqrt(((gx - 11.0) / 9.0) ** 2 + ((gy - 42.0) / 7.0) ** 2)) * 6.0
    street = 5.5 - np.abs(gy - 44.0) * 0.80
    shrine = (1 - np.sqrt(((gx - 36.0) / 9.0) ** 2 + ((gy - 64.0) / 7.0) ** 2)) * 5.0
    # The WHARF is deliberately NOT paved - it is goblin ground: slag, gravel and whatever was
    # cheapest. That contrast is the whole town, so paving it all would erase the joint venture.
    return np.maximum.reduce([market, hall, gate, street, shrine]) \
        + 0.6 * wob(gx * 0.8, gy * 0.8)


def shore(gy):
    """x of the EAST waterline. Bites in at the jetty so the wharf has a basin."""
    gy = np.asarray(gy, float)
    return (78.0 + 4.0 * np.sin(0.10 * gy + 0.5) + 1.2 * np.sin(0.43 * gy)
            - 3.0 * np.exp(-((gy - 43.0) ** 2) / 90.0))


def north_shore(gx):
    """y of the NORTH waterline. Kyle, 10 Nov: "Ensure northern part of cinderwarf and Eastern
    part is water." So the town is a HEADLAND - sea wrapping two sides, land only to the south
    and west, and the gate is the single landward way in."""
    gx = np.asarray(gx, float)
    return 15.0 + 3.2 * np.sin(0.09 * gx + 0.7) + 1.2 * np.sin(0.41 * gx)


def sea_field(gx, gy):
    """>0 in the sea: east of the east shore, or north of the north shore."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    return np.maximum(gx - shore(gy), north_shore(gx) - gy)


def deck_field(gx, gy):
    best = np.full(np.shape(gx), -9.0)
    for (x0, x1, y0, y1) in DECKS:
        e = np.minimum(np.minimum(gx - x0, x1 - gx), np.minimum(gy - y0, y1 - gy))
        best = np.maximum(best, e)
    return best


def cliff_field(gx, gy):
    """The rim, and nothing else.

    Same contract as Hammerfall and Saltspur: THE ENCLOSURE IS THIS FUNCTION, not the scenery.
    The one hole is the gate cut, carved AFTER the rim is forced, so an edit to the dressing can
    never open the back of the town.
    """
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    # the built ground: a broad band along the high street, widening at the market and the hold
    town = np.maximum.reduce([
        24.0 - np.abs(gy - 44.0) * 0.72,
        17.0 - np.hypot((gx - 25.0) / 1.5, (gy - 29.0) / 1.0),     # the hold, north-west
        15.0 - np.hypot((gx - 36.0) / 1.5, (gy - 62.0) / 1.0),     # the shrine terrace, south
        15.0 - np.hypot((gx - 62.0) / 1.4, (gy - 62.0) / 1.0),     # the yard, south-east
        14.0 - np.hypot((gx - 67.0) / 1.4, (gy - 27.0) / 1.0),     # the quay stores, north-east
    ])
    town = town + 1.5 * wob(gx * 0.5, gy * 0.5)
    town = np.maximum(town, road_dist(gx, gy) + 2.6)
    town = np.maximum(town, deck_field(gx, gy) + 1.5)
    rock = -town
    edge = np.minimum.reduce([gx, W - gx, gy, H - gy])
    rock = np.maximum(rock, (4.0 - edge) * 1.5 + 0.3 * wob(gx * 1.3, gy * 1.3))
    cut = (np.abs(gy - 42.0) < 3.5) & (gx < 14)
    rock = np.where(cut, -1.0, rock)
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    rock = np.where(sea_field(gx, gy) > -1.0, np.minimum(rock, -0.5), rock)
    # never rock under the jetty - that is water, and deck paints over it
    return np.where(deck_field(gx, gy) > -0.5, -9.0, rock)


def fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    sea = sea_field(gx, gy)
    cliff = cliff_field(gx, gy)
    return dict(cliff=np.where(sea > 0, -99.0, cliff),
                shallow=sea, deep=sea - 3.0, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


SUBZONES = [
    ("The Hold", 12, 16, 32, 28),
    ("The Seam", 40, 32, 28, 24),
    ("The Wharf", 56, 16, 30, 22),
    ("The Shrine Terrace", 24, 52, 28, 24),
    ("The Salvage Yard", 50, 52, 30, 24),
]

# ---- baker config (tools/bake_tempest.py) ----------------------------------------------------
# A town on a volcanic island: worked stone and iron underfoot, black sand at the tideline, and
# no jungle inside the walls - the green stops at the gate, which is what a hold is for.
BASE = {"rocky": 0.38, "gravel": 0.24, "shore": 0.16, "dry": 0.12, "grass": 0.10}
PAINT = {
    "cobble": [(52, 44, 10, 7, 1.0), (25, 28, 9, 7, 0.95), (10, 42, 7, 5, 0.9),
               (36, 62, 7, 5, 0.8)],
    "rocky":  [(26, 34, 24, 20, 1.0), (16, 44, 14, 12, 0.95), (34, 60, 16, 12, 0.9),
               (44, 26, 16, 10, 0.85)],
    "gravel": [(66, 44, 18, 13, 0.9), (68, 28, 15, 10, 0.85), (64, 62, 15, 10, 0.85)],
    # goblin ground: iron slag trodden flat, where the cargo and the cranes are
    "slag":   [(68, 36, 14, 10, 0.85), (66, 52, 13, 9, 0.8), (70, 26, 12, 8, 0.75)],
    "ash":    [(28, 22, 10, 7, 0.5), (40, 68, 10, 6, 0.45)],
    "shore":  [(74, 44, 8, 16, 0.95), (74, 26, 7, 8, 0.8), (74, 62, 7, 8, 0.8)],
    "earth":  [(25, 27, 7, 5, 0.8), (62, 62, 7, 5, 0.8)],
    "grass":  [(20, 64, 9, 7, 0.6), (44, 20, 8, 6, 0.55)],
}
COBBLE = [(52, 44, 9, 6, 0.95), (25, 28, 8, 6, 0.9), (10, 42, 6, 5, 0.85)]

# ---- NPC spots -----------------------------------------------------------------------------------
# ELEVEN NPCs ACROSS 104x84, one per thing the town does. The rule this exists for: six NPCs in a
# 12x6 box is the cramming complaint, and it applies to a town more than anywhere, because a town
# is the one place the player expects to walk between people. Each stands where their work is.
NPC_POSITIONS = {
    # the hold, west - Dark Iron
    "cw_thane_ashhold":        (25, 26),   # the Thane's Hall, at the top of its own road
    "cw_quartermaster":        (17, 36),   # rep-gated stock, inside the gate
    "cw_blacksmith":           (31, 32),   # the forge, off the hall road
    "cw_armoursmith":          (20, 50),   # plate and mail, south side of the hold
    "cw_shrine_keeper":        (36, 66),   # the shrine terrace, far south-west
    # the seam, middle - where the two halves meet
    "cw_innkeeper":            (46, 40),   # The Tapped Vein, on the street
    "cw_underwriter":          (54, 50),   # Nix Brackwhistle, the Merchant House
    "cw_general_goods":        (58, 38),   # the shuttered counter hatch
    # the wharf, east - goblin
    "cw_flight_master":        (68, 26),   # the pad, out over the water
    "cw_alchemist":            (62, 60),   # volcanic reagents, by the yard
    "cw_salvage_broker":       (70, 62),   # buys the dungeon's trash, at the cargo
    "cw_harbourmaster":        (76, 32),   # the berth office on the wharf
    "cw_archivist":            (22, 22),   # the rolls, beside the hall
    "cw_claims_clerk":         (50, 46),   # the Merchant House front desk
}

CHESTS = [(28, 20), (18, 58), (44, 68), (72, 56), (70, 20)]

#: Almost nothing grows inside the walls, and what does is at the edges. count is deliberately
#: tiny: at Saltspur, rim planting at rim=5 grew pines straight through the camp buildings.
FOREST = dict(seed=83, count=10, rim=2, thorn=10, names=[
    ("ek_thorn_bush", 4, 0.5), ("ek_dead_oak", 6, 0.3), ("ek_pine_trio", 7, 0.2)])


def dress(L):
    p, b = L.prop, L.bld
    CO = "assets/tiles/coastal_props/"

    # ---- the gate, west. The portal tile (2,42) and its column stay clear of solid props ------
    b("orc_great_gatehouse", 8, 42, 12, solid=False, road_ok=True, nudge=0)
    b("orc_watch_tower", 12, 34, 11, nudge=2)
    b("orc_watch_tower", 12, 50, 11, nudge=2)
    p("ek_signpost", 16, 42, 4)

    # ---- THE HOLD, west: Dark Iron, built out of Khaz Varun's own salvaged stone --------------
    b("ek_command_tent", 25, 24, 10, nudge=2)          # the Thane's Hall
    b("ek_border_watchtower", 33, 24, 11, nudge=2)
    b("orc_quartermaster_post", 18, 34, 9, nudge=2)
    b("orc_officers_house", 30, 34, 9, nudge=2)        # the forge
    b("orc_healer_house", 20, 48, 9, nudge=2)          # the armoursmith
    p("ek_forsaken_banner", 28, 30, 6)
    p("ek_farm_well", 22, 32, 4)

    # ---- the shrine terrace, south-west -------------------------------------------------------
    b("ek_wayshrine", 36, 64, 6, nudge=2)
    p("ek_web_boulder", 30, 68, 5)
    p("ek_dead_oak", 42, 66, 6)

    # ---- THE SEAM, middle: the market, and the one building both sides use --------------------
    b("ek_village_inn", 46, 38, 10, nudge=2)           # The Tapped Vein
    b("orc_supply_store", 58, 36, 10, nudge=2)
    b("orc_mess_hall", 54, 52, 10, nudge=2)            # the Merchant House
    p("ek_signpost", 52, 44, 4)
    for (x, y) in ((48, 46), (56, 42)):
        p("ek_scarlet_crates", x, y, 3)

    # ---- THE WHARF, east: goblin, and visibly temporary next to the granite -------------------
    # deco(), not prop(): prop() checks the ground under a sprite and refuses when it is not
    # placeable, which is right for a building and wrong for a hull.
    L.deco("boat_orc", BOAT_SPRITE[0], BOAT_SPRITE[1], 7, path_dir=CO)
    b("orc_watch_tower", 68, 24, 11, nudge=2)          # the flight pad
    b("orc_smokehouse", 62, 58, 9, nudge=2)
    b("orc_supply_store", 70, 60, 9, nudge=2)          # the salvage broker's shed
    for (x, y) in ((74, 36), (74, 50), (78, 44)):
        p("ek_scarlet_crates", x, y, 3)
    p("ek_farm_cart", 66, 48, 4)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_cinderwharf():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/cinderwharf_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
