"""
Hand-built Western Hillsbrad Foothills (160x160): the farms, the strands and Southshore, levels 23-27.

The ARRIVAL half of Kyle's split, and the one that carries Hillsbrad's signature. Kyle: "Players enter from the west
bro" - which is the Classic map: Silverpine borders Hillsbrad's north-WEST, so the player drops out of the pine woods
into farm country and runs east from here to reach Tarren Mill in Eastern Hillsbrad (23-27).

The FIELDS are the thing people remember about this zone in Classic: wide, worked, green, with Alliance farmers and
militia on them. Southshore sits on the south coast as a hostile port rather than a hub, which is the point of coming
here at all - so the player's own hub is SOUTHPOINT TOWER, the ruined watchtower on the western road that the Forsaken
have camped under. That is a real Hillsbrad landmark, and it keeps the arrival zone from being hubless without moving
Tarren Mill off the map square Classic puts it on.

Same green brief as the east (see tools/build_hillsbrad_palette.py for the measured colours): grass is the base ground
cover everywhere, the Ashenvale greens rather than the Silverpine olives, and the dry khaki only at the mountain foot.
This half leans harder on `field` paint than the east, because this is the farm country.

Laid out on the REAL Classic Hillsbrad map, western half (north is up; the sea is the west AND south coast, Alterac's
foothills the north rim):
    N     the pass down from Silverpine comes in at (40,5)
    NW    SOUTHPOINT TOWER (46,24): the ruined watchtower, now a Forsaken camp - the player's hub in this half
    E     the road on to Eastern Hillsbrad leaves at (155,86)
    C     HILLSBRAD FIELDS (96,74): the green heart - working farms, hedgerows, Alliance militia
    N     THE FOOTHILL PASTURES (74,32): high grazing under the peaks, yeti country
    W     AZURELODE MINE (36,62): the silver mine in the western rock, kobolds and Syndicate
    W     THE WESTERN STRAND (16,100): Daggerspine murlocs on the sand
    S     SOUTHSHORE (94,128): the Alliance port - hostile ground, the zone's set-piece
    SW    PURGATION SHORE (30,142): the wreck-strewn south-west coast, looking out at the isle
    SE    HILLSBRAD ORCHARD (130,118): an overgrown orchard gone feral

AREA ARCHETYPE: WIDE WORKED FARMLAND on a double coast - the trunk road comes in from the east, bends south through the
fields to Southshore's gate, and throws branches west to the mine and the strand. Hedgerows and oak stands divide the
plots; the only high ground is the northern pasture.

HARD CONTRACTS (world/portal_manager.py)
  portals  Silverpine South <- (40,5)    Eastern Hillsbrad <- (155,86)
  Azurelode Mine's interior and Purgation Isle are LATER STAGES - both landmarks are dressed here but no portal is
  registered until those zones exist, because portal_qa checks both directions.
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob, lobe, water_body, rock_spurs

KEY = "western_hillsbrad"
NAME = "Western Hillsbrad"
#: The Tilemap NAME is the key world/portal_manager.py looks portals up under (it keys on zone.name), and it has
#: to match the name this zone is registered as in create_all_zones. It did not: the map was called
#: "... Foothills" while the registry said "... Hillsbrad", so get_destination never matched and EVERY portal in
#: both Hillsbrad zones was dead - you could walk into Hillsbrad and never walk out. The flavour name lives in
#: DESC and the subzones instead; this one is an identifier.
DESC = "Hillsbrad's farm country: worked fields, murloc strands, and Southshore's hostile port."
REGION = "Eastern Kingdoms - Lordaeron"
W, H = 160, 160
BAKED_DIR = "assets/tiles/hillsbrad_west/baked"
IS_TOWN = False
BASE_TILE = "grass"
SEED = 118

PORTALS = {(40, 5): "Silverpine South", (155, 86): "Eastern Hillsbrad",
           (33, 60): "Azurelode Mine"}                 # the flooded adit in the western rock
ARRIVALS = [(40, 9), (152, 86), (33, 63)]
START = (44, 20)

ROADS = {
    # the Silverpine pass down past Southpoint Tower into the fields - the player's first road in Hillsbrad
    "pass":      ([(40, 5), (44, 18), (47, 30), (56, 44), (70, 56), (86, 66), (98, 74)], 3.4),
    # on east through the fields, and south to Southshore's gate
    "trunk":     ([(155, 86), (138, 84), (120, 80), (104, 76), (96, 86), (94, 104), (94, 124)], 3.4),
    # the farm lane that loops the plots
    "farm":      ([(100, 74), (88, 66), (76, 70), (72, 84), (82, 92)], 2.2),
    # west to the mine
    "mine":      ([(92, 74), (74, 70), (56, 66), (42, 63)], 2.6),
    # down the west rock to the strand
    "strand":    ([(44, 66), (32, 80), (22, 94), (18, 104)], 2.4),
    # north to the high pastures
    "pasture":   ([(102, 70), (90, 54), (80, 42), (74, 34)], 2.4),
    # the south coast road out of Southshore, west to the wrecks and east to the orchard
    "coast":     ([(92, 126), (72, 134), (52, 140), (36, 144)], 2.4),
    "orchard":   ([(96, 122), (112, 120), (126, 118)], 2.4),
}
_RS = K.RoadSet(ROADS)
road_dist = _RS.dist

# Southshore's quay, laid over the south bay: (x0, x1, y0, y1)
DECKS = [(88.0, 100.0, 137.0, 139.6)]


def paved(gx, gy):
    """Worn stone under Southshore's quay yard, the farm yards and the mine head."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    shore = lobe(gx, gy, 94.0, 129.0, 10.0, 6.5) + 0.5 * wob(gx, gy)
    tower = lobe(gx, gy, 46.0, 24.0, 6.5, 5.0) + 0.5 * wob(gx, gy)
    farm = lobe(gx, gy, 96.0, 76.0, 6.0, 4.2) + 0.5 * wob(gx, gy)
    mine = lobe(gx, gy, 38.0, 62.0, 5.5, 4.0) + 0.5 * wob(gx, gy)
    return np.maximum.reduce([shore, farm, mine, tower]) - 1.2


# ---- water -----------------------------------------------------------------------------------------------------
# The sea wraps the south-west: a long south bay and a deep bite out of the west rim, which is the Western Strand.
# Analytic, integer harmonics only, so painted shoreline and tile grid come from one function.
SEA_S = (74.0, 184.0, 104.0, 44.0)       # the south coast, Southshore's bay
SEA_W = (-8.0, 96.0, 34.0, 54.0)         # the west bite, the Western Strand
POOLS = [(106.0, 62.0, 4.6, 3.2, 0.2), (76.0, 100.0, 4.2, 3.0, -0.3)]    # two farm ponds


def sea_field(gx, gy):
    return np.maximum(water_body(gx, gy, *SEA_S), water_body(gx, gy, *SEA_W))


def pool_field(gx, gy):
    p = np.full(np.shape(gx), -99.0)
    for (cx, cy, rx, ry, rot) in POOLS:
        p = np.maximum(p, water_body(gx, gy, cx, cy, rx, ry, rot))
    return p


def water_field(gx, gy):
    return np.maximum(sea_field(gx, gy), pool_field(gx, gy))


def deck_field(gx, gy):
    d = np.full(np.shape(gx), -9.0)
    for (x0, x1, y0, y1) in DECKS:
        d = np.maximum(d, np.minimum.reduce([gx - x0, x1 - gx, gy - y0, y1 - gy]))
    return d


# ---- rock ------------------------------------------------------------------------------------------------------
# Alterac's foothills along the north, the western rock over Azurelode, a short shoulder in the south-east. The EAST
# rim is deliberately open - that edge is the seam with Eastern Hillsbrad and the trunk road walks straight out of it.
SPURS = [
    (0, 10, 48, 8, 3.2),            # the north-west corner
    (60, 6, 120, 10, 3.2),          # the northern foothills over the pastures
    (130, 8, 160, 22, 3.0),         # the north-east shoulder
    (0, 30, 14, 52, 3.0),           # the western rock over Azurelode
    (0, 120, 12, 138, 2.6),         # the south-west rock above Purgation Shore
    (142, 104, 160, 136, 2.8),      # the south-east shoulder behind the orchard
]
OUTCROPS = [
    (54, 44, 2.6, 2.0), (112, 44, 2.4, 2.0), (30, 54, 2.6, 2.0), (66, 104, 2.4, 2.0), (118, 96, 2.6, 2.2),
    (44, 118, 2.8, 2.2), (134, 70, 2.4, 2.0), (86, 110, 2.6, 2.0), (24, 112, 2.6, 2.0), (140, 92, 2.4, 2.0),
    (62, 124, 2.2, 1.8), (108, 134, 2.4, 2.0),
]


def cliff_field(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    edge = np.minimum.reduce([gx, W - gx, gy, H - gy])
    rock = (5.0 + 3.0 * wob(gx * 0.5, gy * 0.5) + 1.2 * wob(gx * 1.4, gy * 1.4)) - edge
    rock = np.maximum(rock, rock_spurs(gx, gy, SPURS, OUTCROPS))
    wf = water_field(gx, gy)
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    rock = np.where(wf > -1.0, np.minimum(rock, -0.5), rock)
    rock = np.where(deck_field(gx, gy) > -1.0, np.minimum(rock, -0.5), rock)
    return rock


def fields(gx, gy):
    gx = np.asarray(gx, float)
    w = water_field(gx, gy)
    deep = np.maximum(sea_field(gx, gy) - 3.0, pool_field(gx, gy) - 2.0)
    return dict(cliff=cliff_field(gx, gy), shallow=w, deep=deep, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


# ---- subzones (x, y, w, h) ---------------------------------------------------------------------------------------
SUBZONES = [
    ("Southpoint Tower", 28, 10, 40, 28),
    ("The Foothill Pastures", 70, 14, 46, 28),
    ("Hillsbrad Fields", 68, 54, 58, 44),
    ("Azurelode Mine", 18, 44, 40, 32),
    ("The Western Strand", 2, 80, 32, 46),
    ("Hillsbrad Orchard", 110, 100, 46, 32),
    ("Southshore", 72, 110, 48, 36),
    ("Purgation Shore", 14, 128, 44, 28),
]

# ---- baker config (read by tools/bake_hillsbrad.py) ---------------------------------------------------------------
# Farm country: more `field` paint than the east, grass everywhere under it.
BASE = {"grass": 0.64, "forest": 0.20, "fern": 0.14, "rocky": 0.12}
PAINT = {
    "grass":  [(92, 70, 28, 22, 1.0), (70, 100, 22, 16, 1.0), (118, 60, 16, 12, 0.9), (56, 46, 16, 12, 0.8),
               (126, 114, 14, 10, 0.8), (46, 118, 14, 10, 0.7)],
    "meadow": [(80, 58, 12, 8, 0.9), (108, 86, 12, 8, 0.9), (60, 86, 10, 7, 0.8), (88, 46, 10, 7, 0.8),
               (130, 104, 9, 6, 0.7)],
    "field":  [(92, 72, 16, 10, 1.0), (80, 82, 13, 8, 1.0), (106, 68, 12, 7, 1.0), (84, 62, 10, 6, 0.9),
               (100, 92, 11, 7, 0.9), (128, 118, 10, 6, 0.8), (70, 76, 9, 5, 0.8)],
    "dry":    [(88, 24, 16, 9, 0.8), (112, 22, 12, 8, 0.7), (26, 36, 9, 6, 0.6), (24, 134, 12, 6, 0.6)],
    "forest": [(58, 58, 12, 9, 0.8), (118, 48, 12, 8, 0.8), (60, 116, 10, 7, 0.7), (134, 92, 10, 7, 0.7)],
    "earth":  [(94, 129, 7, 5, 0.8), (38, 62, 6, 4, 0.9), (96, 76, 5, 4, 0.7), (46, 24, 6, 4, 0.8)],
    "rocky":  [(38, 62, 8, 6, 0.8), (20, 112, 8, 5, 0.6), (146, 118, 10, 5, 0.6), (30, 140, 10, 5, 0.6)],
    "gravel": [(39, 63, 6, 4, 0.7), (94, 126, 6, 4, 0.5), (40, 8, 8, 5, 0.6)],
    "shore":  [(18, 102, 10, 16, 0.9), (94, 136, 20, 6, 0.9), (36, 146, 18, 6, 0.9)],
}
COBBLE = [(94, 129, 10, 6.5, 0.9), (96, 76, 6, 4.2, 0.8), (38, 62, 5.5, 4, 0.8), (46, 24, 6.5, 5, 0.9)]

# ---- NPC spots -----------------------------------------------------------------------------------------------------
NPC_POSITIONS = {
    # Southpoint Tower - the hub for this half
    "hbw_southpoint_commander": (44, 22),
    "hbw_southpoint_quartermaster": (48, 26),   # vendor
    "hbw_southpoint_apothecary": (42, 27),
    "hbw_southpoint_deathguard": (49, 21),
    "hbw_pass_scout": (42, 11),
    # the road on to Eastern Hillsbrad
    "hbw_road_outrider": (146, 85),
    # the fields - a Forsaken forward post watching the farms
    "hbw_fields_agent": (98, 78),
    "hbw_fields_quartermaster": (101, 82),   # vendor
    "hbw_fields_poacher": (84, 88),
    "hbw_fields_scout": (90, 64),
    # the pastures
    "hbw_pasture_herder": (90, 36),
    # the mine
    "hbw_mine_overseer": (44, 62),
    "hbw_mine_surveyor": (48, 68),
    # the strand
    "hbw_strand_tidewatcher": (28, 94),
    # Southshore - watched from the treeline, never entered in comfort
    "hbw_southshore_spy": (82, 116),
    "hbw_southshore_saboteur": (86, 120),
    # the south-west and the orchard
    "hbw_purgation_castaway": (44, 140),
    "hbw_orchard_forager": (122, 116),
}
CHESTS = [(62, 40), (116, 64), (24, 86), (132, 107), (56, 136), (104, 100)]

OAKS = [("ek_willow", 8, 0.30), ("ek_pine_trio", 7, 0.32), ("ek_pine_tall", 8, 0.28), ("ek_willow", 7, 0.30)]

FOREST = dict(seed=67, count=112, rim=24, thorn=12, names=[
    ("ek_willow", 8, 0.30), ("ek_willow", 7, 0.30), ("ek_pine_trio", 7, 0.32), ("ek_pine_tall", 8, 0.28),
    ("ek_thorn_bush", 4, 0.40)])


def dress(L):
    p, b = L.prop, L.bld
    HF, CO, RU, ENT = T.HFP, "assets/tiles/coastal_props/", "assets/tiles/ruins/", T.ENT

    # ---- the Silverpine pass: the blight ends at this signpost, and the green starts
    p("ek_signpost", 44, 12, 4)
    p("ek_ruin_wall", 34, 10, 4)
    p("ek_ruin_wall", 48, 9, 4)
    T.grove(L, 30, 16, 7, 5, 6, OAKS, seed=16)

    # ---- Southpoint Tower: the ruined watchtower the Forsaken have camped under. The player's hub here.
    p(RU + "ruin_tower_skulls.png", 46, 20, 9, solid=True, nudge=0)
    b("forsaken_house_small", 40, 26, 8, nudge=2)
    b("forsaken_house_small", 52, 26, 8, nudge=2)
    b("command_war_tent", 46, 30, 8, nudge=2)
    p("ek_forsaken_banner", 42, 21, 5)
    p("ek_forsaken_banner", 51, 21, 5)
    p("ek_farm_well", 46, 27, 4)
    p("ek_plague_cauldron", 54, 23, 4)
    p("ek_signpost", 38, 22, 4)
    for x in (36, 42):
        p("ek_farm_fence", x, 34, 3, solid=True)
    T.grove(L, 58, 18, 6, 5, 6, OAKS, seed=17)

    # ---- the road on east to Eastern Hillsbrad
    p("ek_signpost", 148, 82, 4)
    p("ek_ruin_wall", 142, 90, 4)
    T.grove(L, 140, 76, 6, 6, 6, OAKS, seed=2)

    # ---- Hillsbrad Fields: the green heart. Worked farms, hedgerows, scarecrows.
    b("ek_cottage_medium", 94, 72, 9, nudge=2)
    b("ek_townhouse", 108, 84, 9, nudge=2)
    b("ek_cottage_small", 78, 86, 7, nudge=2)
    b("ek_townhouse", 82, 60, 9, nudge=2)
    p("ek_farm_well", 98, 78, 4)
    p("ek_farm_cart", 104, 74, 4)
    p("ek_farm_cart", 82, 90, 4)
    for x in (80, 86, 92, 98, 104):
        p("ek_farm_fence", x, 56, 3, solid=True)
    for x in (84, 90, 96, 102, 108):
        p("ek_farm_fence", x, 96, 3, solid=True)
    for (x, y) in [(88, 80), (112, 76), (74, 78), (114, 92)]:
        p("ek_haystack", x, y, 4)
    p("ek_scarecrow", 96, 88, 4)
    p("ek_scarecrow", 86, 70, 4)
    p("ek_scarecrow", 110, 66, 4)
    p("ek_signpost", 88, 68, 4)
    p("ek_signpost", 100, 98, 4)
    T.grove(L, 120, 62, 6, 5, 6, OAKS, seed=5)
    T.grove(L, 70, 62, 6, 5, 6, OAKS, seed=6)

    # ---- The Foothill Pastures: high grazing under the peaks
    p("ek_farm_fence", 82, 30, 3, solid=True)
    p("ek_farm_fence", 90, 30, 3, solid=True)
    p("ek_farm_fence", 98, 32, 3, solid=True)
    p("ek_haystack", 86, 38, 4)
    p("ek_haystack", 102, 36, 4)
    p("ek_farm_cart", 94, 40, 4)
    p("ek_signpost", 80, 40, 4)
    T.grove(L, 74, 28, 7, 5, 7, OAKS, seed=3)
    T.grove(L, 110, 30, 7, 5, 7, OAKS, seed=4)

    # ---- Azurelode Mine: the silver mine in the western rock
    # The adit is the PORTAL tile (33,60) -> Azurelode Mine, so the mouth is drawn but not solid:
    # a solid prop here would wall off the entrance it is advertising.
    p(ENT + "ent_collapsed_mine.png", 33, 60, 7, solid=False, nudge=0)
    p("ek_farm_cart", 42, 64, 4)
    p("ek_ruin_wall", 34, 68, 4)
    p("ek_signpost", 48, 60, 4)
    for (x, y) in [(40, 56), (46, 70)]:
        p("ek_scarlet_crates", x, y, 4)
    p("ek_gibbet", 30, 68, 6)
    T.grove(L, 52, 50, 7, 6, 7, OAKS, seed=7)

    # ---- The Western Strand: Daggerspine murlocs on the sand
    for (x, y) in [(16, 92), (22, 104), (14, 112), (24, 116)]:
        p(CO + "driftwood_pile.png", x, y, 3, shore_ok=True)
    p(CO + "rowboat_wreck.png", 20, 106, 3, shore_ok=True)
    p(CO + "fish_drying_rack.png", 26, 96, 4)
    p(CO + "coral_reef_outcrop.png", 12, 102, 3, shore_ok=True)
    p(CO + "mooring_posts.png", 18, 112, 3, shore_ok=True)
    p("ek_signpost", 32, 90, 4)

    # ---- Southshore: the Alliance port. Hostile ground - no inn for you.
    b("crossroads_inn", 90, 124, 10, nudge=2)
    b("ek_cottage_medium", 102, 126, 9, nudge=2)
    b("ek_border_watchtower", 84, 132, 9, nudge=2)
    b("ek_boathouse", 100, 134, 7, nudge=2)
    b("ek_townhouse", 78, 124, 9, nudge=2)
    p(CO + "mooring_posts.png", 92, 136, 3, shore_ok=True)
    p(CO + "fish_crates_traps.png", 96, 135, 3)
    p(CO + "dock_lantern_post.png", 89, 135, 4)
    # IN THE WATER. It was at y=138, four tiles up the beach from the first wet tile, a
    # full-rigged ship standing on the sand beside the dock. Kyle, 10 Nov: "can we stop
    # putting boats on dry land (this is in 'south shore')."
    # deco, not prop: prop() refuses deep water and DROPS the sprite without a word (it is
    # only appended to L.skipped), which is why a ship could only ever be placed on the beach.
    L.deco("boat_human", 98, 147, 5, path_dir=CO)
    p("ek_farm_fence", 76, 118, 3, solid=True)
    p("ek_farm_fence", 108, 126, 3, solid=True)
    p("ek_signpost", 94, 114, 4)

    # ---- Purgation Shore: wrecks on the south-west coast, the isle out beyond
    for (x, y) in [(28, 146), (44, 148), (20, 142)]:
        p(CO + "driftwood_pile.png", x, y, 3, shore_ok=True)
    p(CO + "rowboat_wreck.png", 36, 148, 3, shore_ok=True)
    p(CO + "boat_human.png", 50, 150, 5, shore_ok=True)
    p("ek_cross_crows", 30, 138, 4)
    p("ek_signpost", 46, 136, 4)
    p("ek_dead_oak", 24, 140, 6)

    # ---- Hillsbrad Orchard: gone feral
    for (x, y) in [(118, 110), (126, 108), (134, 112), (122, 122), (132, 124), (140, 116)]:
        p("ek_willow", x, y, 7)
    p("ek_farm_cart", 128, 116, 4)
    p("ek_scarecrow", 136, 120, 4)
    p("ek_farm_fence", 116, 126, 3, solid=True)
    p("ek_farm_fence", 124, 128, 3, solid=True)
    p("ek_signpost", 114, 114, 4)
    p("ek_toadstools", 130, 112, 2, solid=False)

    # ---- hedgerows and oak stands dividing the plots
    T.grove(L, 64, 72, 6, 8, 8, OAKS, seed=8)
    T.grove(L, 112, 96, 8, 6, 8, OAKS, seed=9)
    T.grove(L, 56, 104, 7, 6, 7, OAKS, seed=10)
    T.grove(L, 70, 128, 7, 5, 7, OAKS, seed=11)
    T.grove(L, 128, 76, 7, 5, 7, OAKS, seed=12)
    T.grove(L, 42, 78, 5, 6, 6, OAKS, seed=13)
    T.grove(L, 106, 110, 6, 5, 6, OAKS, seed=14)
    T.grove(L, 40, 100, 5, 6, 6, OAKS, seed=15)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_hillsbrad_west():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/hbw_shape.png"
    T.shape_preview(sys.modules[__name__], out)
