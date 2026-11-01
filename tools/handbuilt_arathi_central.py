"""
Hand-built Arathi Central (190x170): the basin, the stone rings and Hammerfall. Levels 33-37.

Kyle, 2026-11-01: "central can be 33-37. We can have hammerfall in the central and a kobold dungeon from
37-40 in the central." And on the town: "hammerfall needs a wind rider and an inn, shops etc. It'll be a
full town."

ARCHETYPE: THE BASIN AND THE RINGS. Arathi West is a map split by a wall. This one is the opposite shape -
a wide shallow bowl with everything draining toward the middle, ringed by low ridges you look down from.
Where West makes you commit to a gap, Central lets you see the whole zone at once from any edge, and what
you see from every edge is the same thing: a line of four enormous stone rings running east to west across
the floor of the basin.

THE CIRCLE OF INNER BINDING is the zone's spine and its only straight line. Four rings on one axis, older
than Arathor, older than anything anyone here can name, and the roads and the factions arrange themselves
around them without ever quite admitting that is what they are doing. Hammerfall was sited to watch them.
The Witherbark built their village at the west end of the line. The ogres hold the ring nobody goes to.

That gives the zone its playable shape: the RINGS are the road. You travel the axis, and everything that
matters hangs off it within sight of the next ring.

PLACES (north is up; Arathi West lies west, Arathi East beyond the seam):
    W     the west seam (4,84): back to Arathi West
    WC    WITHERBARK VILLAGE (44,112): the troll hold at the west end of the ring line
    NW    BOULDERFIST HALL (38,42): the ogre cave mouth, up on the north ridge
    C     THE CIRCLE OF INNER BINDING (60..150, y~86): the four rings, the zone's axis
    NE    HAMMERFALL (142,54): the Horde garrison on its bluff. A full town.
    SC    THE REFUGE ROAD (96,138): the southern track under the ridge
    E     DRYWHISKER GORGE (168,116): the kobold dig, and the dungeon door
    E     the east seam (186,92): on to Arathi East

HARD CONTRACTS (world/portal_manager.py)
  (4, 84)    <-> Arathi West              seam. Arathi West's east portal is (176,84).
  (186, 92)  <-> Arathi East              seam
  (38, 40)   <-> Boulderfist Hall         the ogre cave, this zone's one cave
  (170, 114) <-> Drywhisker Deeps         the kobold dungeon, tuned 37-40 - above this zone on purpose
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob, lobe, water_body, rock_spurs

KEY = "arathi_central"
NAME = "Arathi Central"
DESC = ("The basin at the heart of the highlands: four ancient stone rings on one axis, a Horde garrison "
        "watching them, and a kobold dig in the eastern gorge.")
REGION = "Eastern Kingdoms - Arathi Highlands"
W, H = 190, 170
BAKED_DIR = "assets/tiles/arathi_central/baked"
IS_TOWN = False
BASE_TILE = "grass"
SEED = 332

RU = "assets/tiles/ruins/"

PORTALS = {(4, 84): "Arathi West",
           (186, 92): "Arathi East",
           (38, 40): "Boulderfist Hall",
           (170, 114): "Drywhisker Deeps"}
#: Arrival is 2 tiles SOUTH of the registered tile for an overworld portal, +3 leaving a cave. Those
#: columns are kept clear of solid landmarks by hand in dress().
ARRIVALS = [(4, 86), (186, 94), (38, 42), (170, 116)]
START = (10, 84)

# ---- roads -----------------------------------------------------------------------------------------
# The trunk IS the ring axis - it runs the line of the four circles, west seam to east seam, because that
# is the one route everybody in the zone's history has taken. Branches drop off it to each holding.
ROADS = {
    "rings":      ([(4, 84), (30, 86), (62, 88), (94, 88), (122, 88), (150, 90), (186, 92)], 3.2),
    # north out of the second ring, up the bluff to Hammerfall's gate
    "hammerfall": ([(120, 84), (130, 72), (138, 60), (142, 56)], 2.8),
    # north-west off the first ring to the ogre cave on the ridge
    "boulderfist": ([(46, 84), (42, 66), (38, 48), (38, 42)], 2.4),
    # south-west to the troll village
    "witherbark": ([(54, 92), (48, 104), (44, 112)], 2.4),
    # the southern track, under the south ridge and back up to the east end
    "refuge":     ([(60, 92), (78, 124), (96, 138), (128, 130), (152, 110), (166, 98)], 2.4),
    # east off the last ring down into the gorge
    "drywhisker": ([(156, 92), (164, 104), (170, 114)], 2.4),
}
_RS = K.RoadSet(ROADS)
road_dist = _RS.dist


def paved(gx, gy):
    """Worn stone: Hammerfall's muster yard, and the flagged floor inside each of the four rings."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    town = lobe(gx, gy, 142.0, 56.0, 20.0, 15.0) + 0.5 * wob(gx, gy)
    out = town
    for (cx, cy) in RINGS:
        out = np.maximum(out, lobe(gx, gy, cx, cy, 7.0, 6.0) + 0.4 * wob(gx, gy))
    return out - 1.2


# ---- the rings -------------------------------------------------------------------------------------
#: The Circle of Inner Binding. Four, on one axis, evenly spaced - the only straight line in Arathi and
#: the reason the trunk road goes where it goes.
RINGS = [(62.0, 88.0), (94.0, 88.0), (122.0, 88.0), (150.0, 90.0)]
RING_R = 9.0
RING_T = 2.2


def ring_field(gx, gy):
    """>0 on the standing stones themselves: an annulus per circle, not a filled disc.

    A ring has to be a RING. Drawn as a disc it is a rock blob and the player walks around it; drawn as
    an annulus with a gap carved for the road you walk INTO it, which is the whole experience of the
    thing. The roads already cut rock in cliff_field, so each ring gets its doorway for free from the
    trunk passing through.
    """
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    out = np.full(np.shape(gx), -99.0)
    for (cx, cy) in RINGS:
        r = np.sqrt((gx - cx) ** 2 + (gy - cy) ** 2)
        out = np.maximum(out, RING_T - np.abs(r - RING_R) + 0.25 * wob(gx * 1.6, gy * 1.6))
    return out


# ---- water -----------------------------------------------------------------------------------------
# The basin drains to its own middle, so the water here is a shallow mere on the floor between rings two
# and three, plus the gorge stream in the east. Analytic, integer harmonics only.
MERE = (108.0, 104.0, 13.0, 8.0, 0.25)
GORGE_STREAM = [(186, 128), (170, 120), (160, 108), (152, 98)]
STREAM_W = 1.6


def mere_field(gx, gy):
    return water_body(gx, gy, *MERE)


def stream_field(gx, gy):
    d = np.full(np.shape(gx), 1e9)
    for (x0, y0), (x1, y1) in zip(GORGE_STREAM, GORGE_STREAM[1:]):
        d = np.minimum(d, T.seg_dist(gx, gy, x0, y0, x1, y1))
    return (STREAM_W - d) + 0.3 * wob(gx * 1.3, gy * 1.3)


def water_field(gx, gy):
    return np.maximum(mere_field(gx, gy), stream_field(gx, gy))


def deck_field(gx, gy):
    # A plank causeway over the mere's north shallows, carrying the trunk road's southern loop.
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    return np.minimum.reduce([gx - 100.0, 116.0 - gx, gy - 95.0, 98.0 - gy])


# ---- rock -------------------------------------------------------------------------------------------
# A BOWL: ridges around the whole rim, low and continuous, so the basin reads as one room. The gorge is
# cut INTO the east ridge rather than placed beside it.
SPURS = [
    (0, 10, 70, 16, 3.6),           # the north ridge, west half
    (70, 16, 150, 12, 3.4),         # the north ridge, east half - Hammerfall's bluff sits under it
    (150, 12, 190, 26, 3.6),        # the north-east shoulder
    (176, 30, 190, 150, 3.4),       # the east ridge, pierced by the gorge
    (0, 30, 8, 150, 3.4),           # the west ridge, pierced by the seam
    (16, 152, 120, 160, 3.6),       # the south ridge
    (120, 156, 190, 150, 3.4),      # the south-east shoulder
    (128, 44, 176, 38, 2.6),        # the shelf Hammerfall is built on, behind the town
]
OUTCROPS = [
    (28, 60, 2.8, 2.2), (70, 40, 2.6, 2.0), (104, 36, 2.6, 2.0), (160, 62, 2.6, 2.2),
    (24, 100, 2.6, 2.0), (34, 134, 2.8, 2.2), (78, 146, 2.6, 2.0), (116, 144, 2.6, 2.0),
    (150, 134, 2.8, 2.2), (170, 80, 2.6, 2.0), (90, 116, 2.4, 1.8), (136, 110, 2.6, 2.0),
    (54, 70, 2.4, 1.8), (180, 100, 2.4, 2.0),
]


def cliff_field(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    edge = np.minimum.reduce([gx, W - gx, gy, H - gy])
    rock = (5.0 + 3.0 * wob(gx * 0.5, gy * 0.5) + 1.2 * wob(gx * 1.4, gy * 1.4)) - edge
    rock = np.maximum(rock, rock_spurs(gx, gy, SPURS, OUTCROPS))
    rock = np.maximum(rock, ring_field(gx, gy))
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    rock = np.where(water_field(gx, gy) > -1.0, np.minimum(rock, -0.5), rock)
    rock = np.where(deck_field(gx, gy) > -1.0, np.minimum(rock, -0.5), rock)
    return rock


def fields(gx, gy):
    gx = np.asarray(gx, float)
    w = water_field(gx, gy)
    deep = mere_field(gx, gy) - 4.0          # the mere has a deep middle; the gorge stream is wadeable
    return dict(cliff=cliff_field(gx, gy), shallow=w, deep=deep, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


# ---- subzones (x, y, w, h) ---------------------------------------------------------------------------
SUBZONES = [
    ("The Ring Road", 10, 76, 170, 26),
    ("Boulderfist Hall", 20, 26, 44, 36),
    ("Witherbark Village", 24, 96, 44, 36),
    ("Hammerfall", 118, 36, 54, 36),
    ("The Sunken Mere", 90, 92, 42, 28),
    ("The Refuge Road", 60, 118, 76, 34),
    ("Drywhisker Gorge", 146, 96, 44, 44),
    ("The North Shelf", 64, 20, 60, 26),
]

# ---- baker config (read by tools/bake_arathi.py) ------------------------------------------------------
# The basin floor is grass going to meadow at the mere; the rim and the ring stones are rocky; the moor
# dryness of Arathi West survives only up on the shelves, which is how the two zones read as one country
# without looking like the same map.
BASE = {"grass": 0.42, "dry": 0.28, "rocky": 0.20, "forest": 0.10}
PAINT = {
    "grass":  [(90, 90, 46, 26, 1.0), (50, 92, 30, 20, 0.95), (140, 96, 32, 20, 0.9), (108, 120, 26, 16, 0.8)],
    "dry":    [(70, 36, 36, 20, 0.95), (120, 30, 34, 18, 0.9), (168, 60, 20, 16, 0.8), (30, 50, 22, 16, 0.8),
               (150, 130, 22, 14, 0.7)],
    "rocky":  [(62, 88, 12, 11, 0.95), (94, 88, 12, 11, 0.95), (122, 88, 12, 11, 0.95), (150, 90, 12, 11, 0.95),
               (168, 116, 20, 16, 0.9), (38, 42, 12, 9, 0.8), (142, 56, 14, 10, 0.7)],
    "meadow": [(108, 104, 20, 13, 0.95), (96, 136, 20, 12, 0.85), (44, 112, 14, 10, 0.8)],
    "field":  [(142, 56, 16, 11, 0.9), (44, 112, 12, 8, 0.8)],
    "forest": [(36, 126, 16, 11, 0.85), (82, 142, 14, 10, 0.8), (128, 136, 14, 10, 0.75)],
    "earth":  [(142, 56, 9, 6, 0.9), (44, 112, 7, 5, 0.85), (38, 42, 6, 4, 0.8), (170, 114, 7, 5, 0.8)],
    "gravel": [(4, 86, 7, 5, 0.6), (186, 94, 7, 5, 0.6), (164, 104, 8, 5, 0.6)],
    "shore":  [(108, 104, 16, 5, 0.8), (168, 120, 8, 4, 0.6)],
}
COBBLE = [(142, 56, 16, 12, 0.95), (62, 88, 8, 7, 0.8), (94, 88, 8, 7, 0.8), (122, 88, 8, 7, 0.8),
          (150, 90, 8, 7, 0.8)]

# ---- NPC spots -----------------------------------------------------------------------------------------
# HAMMERFALL IS A FULL TOWN (Kyle: "wind rider and an inn, shops etc"). Rep is split across the three Horde
# factions by WHO the NPC is, not by where they stand - Kyle: "quest rep will be mixture of orgrimmar,
# undercity, and thunderbluff depending on npcs." The orc garrison answers to Orgrimmar, the apothecary
# wing to the Forsaken, and the two tauren who came up with the supply caravan to Thunder Bluff.
NPC_POSITIONS = {
    # --- Hammerfall: command (Orgrimmar)
    "hammerfall_commander": (142, 50),
    "hammerfall_quartermaster": (134, 58),
    "hammerfall_sergeant": (150, 52),
    # --- Hammerfall: services
    "hammerfall_innkeeper": (136, 64),
    "hammerfall_windrider_master": (154, 62),      # the wind rider
    "hammerfall_weaponsmith": (128, 60),
    "hammerfall_general_goods": (146, 66),
    "hammerfall_reagent_vendor": (132, 68),
    "hammerfall_stablemaster": (156, 56),
    # --- Hammerfall: the Forsaken wing (the_forsaken)
    "hammerfall_apothecary": (122, 54),
    "hammerfall_deathguard": (124, 62),
    # --- Hammerfall: the Thunder Bluff caravan (thunder_bluff)
    "hammerfall_tauren_envoy": (148, 44),
    "hammerfall_tauren_herbalist": (152, 46),
    # --- out in the zone
    # OUTSIDE the stones. (94,80) is 8 tiles from ring two's centre, which is inside the
    # annulus - the flood-fill caught him standing in a standing stone.
    "arathi_ring_scholar": (94, 74),               # camped off the second ring, counting stones
    "arathi_gorge_prospector": (160, 108),         # watching the kobold dig from above
    "arathi_refuge_runner": (96, 134),             # on the southern track
}

#: Two of these were inside ring stones on the first build (RING_R 9 +/- RING_T 2.2, so anything
#: 7-11 tiles from a ring centre is rock) and moved clear.
CHESTS = [(36, 48), (74, 100), (104, 74), (130, 96), (166, 122), (46, 118), (92, 142), (156, 74)]

OAKS = [("ek_willow", 8, 0.30), ("ek_pine_trio", 7, 0.32), ("ek_dead_oak", 7, 0.28), ("ek_willow", 7, 0.30)]
FOREST = dict(seed=38, count=78, rim=14, thorn=9, names=[
    ("ek_willow", 8, 0.30), ("ek_pine_trio", 7, 0.32), ("ek_dead_oak", 7, 0.28),
    ("ek_thorn_bush", 4, 0.40)])


def dress(L):
    p, b = L.prop, L.bld
    ENT = T.ENT

    # ---- HAMMERFALL: the Horde garrison on its bluff -----------------------------------------------
    # Built out of the orc garrison sheet rather than the Valley-of-Trials huts, because this hold has
    # stood in hostile country for years and hide-over-poles says the opposite (claude/orc_building_
    # prompts.md). The Forsaken wing is west of the yard, the tauren caravan north of it.
    b("orc_great_gatehouse", 142, 44, 13, nudge=2)
    b("orc_war_hall", 142, 54, 12, nudge=2)
    b("orc_warchief_lodge", 150, 50, 12, nudge=2)
    b("orc_barracks_longhouse", 132, 50, 10, nudge=2)
    b("orc_mess_hall", 136, 64, 10, nudge=2)         # the inn: a Horde garrison's inn is its mess hall
    b("orc_quartermaster_post", 146, 66, 9, nudge=2)
    b("orc_war_forge", 128, 60, 10, nudge=2)
    b("orc_supply_store", 132, 68, 9, nudge=2)
    b("orc_warbeast_stable", 156, 56, 9, nudge=2)    # the wind rider roost
    b("orc_watch_tower", 160, 48, 13, nudge=2)
    b("orc_guard_post", 124, 46, 9, nudge=2)
    # the Forsaken wing
    b("orc_forsaken_apothecary", 122, 54, 10, nudge=2)
    b("orc_deathguard_post", 124, 62, 9, nudge=2)
    # the tauren caravan, camped north of the yard rather than housed in it
    b("orc_totem_court", 148, 42, 7, nudge=2)
    p("ek_farm_well", 142, 60, 4)
    p("ek_signpost", 128, 74, 4)
    for (x, y) in ((126, 42), (158, 42)):
        p(RU + "ruin_wall_arch.png", x, y, 6)

    # ---- THE CIRCLE OF INNER BINDING: four rings on one axis ----------------------------------------
    # The stones themselves are rock (ring_field), so what goes here is what has accumulated AROUND them:
    # the scholar's camp at the second, offerings at the third, and the ogres' squat at the fourth.
    p(RU + "ruin_stone_ring.png", 62, 88, 6, solid=False, allow_overlap=True)
    p(RU + "ruin_stone_ring.png", 94, 88, 6, solid=False, allow_overlap=True)
    p(RU + "ruin_stone_ring.png", 122, 88, 6, solid=False, allow_overlap=True)
    p(RU + "ruin_stone_ring.png", 150, 90, 6, solid=False, allow_overlap=True)
    b("ek_command_tent", 90, 78, 7, nudge=2)          # the scholar's camp at ring two
    p("ek_scarlet_crates", 98, 80, 4)
    p(RU + "ruin_bone_pillars.png", 122, 80, 7)       # offerings at ring three
    p("ek_web_boulder", 146, 82, 5)
    p("ek_signpost", 78, 90, 4)
    p("ek_signpost", 136, 90, 4)

    # ---- BOULDERFIST HALL: the ogre cave on the north ridge -----------------------------------------
    # Portal (38,40), arrival (38,42): mouth drawn ABOVE the tile, column below left clear.
    p(ENT + "cave_entrance_plain.png", 38, 38, 8, solid=False, nudge=0, road_ok=True, allow_overlap=True)
    for (x, y) in ((30, 36), (46, 36)):
        p("ek_web_boulder", x, y, 6)
    p("ek_farm_cart", 44, 48, 4)
    p("ek_haystack", 32, 48, 4)
    p(RU + "ruin_bone_pillars.png", 38, 52, 6)

    # ---- WITHERBARK VILLAGE: the troll hold at the west end of the line -----------------------------
    b("ek_forsaken_field_tent", 44, 110, 8, nudge=2)
    b("ek_forsaken_field_tent", 52, 116, 8, nudge=2)
    b("ek_forsaken_field_tent", 36, 118, 8, nudge=2)
    p(RU + "ruin_bone_pillars.png", 44, 104, 8)
    p("ek_gibbet", 54, 108, 6)
    p("ek_cross_crows", 34, 110, 5)
    p("ek_plague_cauldron", 46, 120, 4)
    for (x, y) in ((28, 114), (58, 120)):
        p("ek_thorn_bush", x, y, 3, solid=False)

    # ---- DRYWHISKER GORGE: the kobold dig, and the door down ---------------------------------------
    # Tuned 37-40, above this zone on purpose (Kyle's call): the entrance is here, you come back for it.
    p(ENT + "cave_entrance_plain.png", 170, 112, 8, solid=False, nudge=0, road_ok=True, allow_overlap=True)
    b("bd_winch_house", 164, 118, 8, nudge=2)        # the kobolds took the dig gear with the dig
    p("ek_farm_cart", 176, 118, 4)
    p("ek_scarlet_crates", 166, 124, 4)
    p("ek_signpost", 160, 110, 4)
    for (x, y) in ((158, 120), (178, 108)):
        p("ek_web_boulder", x, y, 5)

    # ---- the mere, and the southern track ------------------------------------------------------------
    p("ek_willow", 98, 112, 7)
    p("ek_willow", 120, 110, 7)
    T.grove(L, 36, 128, 8, 6, 8, OAKS, seed=7)
    T.grove(L, 84, 142, 7, 5, 7, OAKS, seed=8)
    T.grove(L, 128, 136, 7, 5, 6, OAKS, seed=9)
    b("ek_wayshrine", 96, 134, 5, nudge=2)
    p("ek_signpost", 118, 132, 4)

    # ---- the seams -----------------------------------------------------------------------------------
    p("ek_signpost", 12, 86, 4)
    p("ek_signpost", 178, 94, 4)
    p(RU + "ruin_wall_arch.png", 8, 78, 6)
    p(RU + "ruin_wall_arch.png", 182, 86, 6)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_arathi_central():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/arathi_central_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
