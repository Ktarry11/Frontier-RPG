"""
Hand-built Arathi West (180x170): the moor behind Thoradin's Wall, levels 28-33.

Kyle, 2026-11-01: "let's do arathi highlands. Directly from hillsbrand. So arathi we can split into East,
central, and west. West can be 28-33."

WHY HERE. tools/audit_content_by_level.py measured the game's two content troughs: levels 28-30 (quests
available fall from 90 at level 24 to 24 at level 29) and 38-40. Arathi is three zones laid straight across
both of them, and the door was already built - Eastern Hillsbrad has Thoradin's Wall at (136,148), dressed,
shut, with Ada Rook standing at the gap who has never seen the far side. This zone is what she has not seen.

ARCHETYPE: THE ESCARPMENT. Every other Lordaeron zone is country ringed by mountains - a bowl you move
around inside. Arathi West is a bowl cut in HALF. One rock scarp runs north-west to south-east across the
whole map, and it divides the zone into two countries that do not look alike:

    ABOVE IT, the high moor. Windswept, treeless, heather and exposed bedrock. The ogres and the trolls are
    up here because nobody else wants it. Big sky, no cover, you can see what is coming and so can it.
    BELOW IT, the sheltered lowland. The old Arathor farmland in the lee of the scarp, where the soil stayed
    and the trees grew - and where Stromgarde's ruin sits, because that is where people built.

There are exactly THREE ways through the scarp (SCARP_GAPS). That is the zone's shape: wherever you are,
getting to the other half means committing to a gap, and the gaps are where the roads and the fights are.

The scarp is also why this zone does not read as more Hillsbrad even though it borders it. Hillsbrad is
green hedgerow hill country with a mountain ring; this is dry open moor with a wall through the middle of
it, and the palette (BASE/PAINT below) moves off Hillsbrad's pasture greens onto heather, bracken and bare
rock. The green stops at the wall, which is the point of a border.

PLACES, laid out on the real Classic Arathi map (north is up; Hillsbrad lies west beyond the wall, Arathi
Central east beyond the seam):
    W     THORADIN'S WALL (4,118): the gate, finally open. Arrival.
    SW    STROMGARDE KEEP (34,146): the ruined Arathor capital, Syndicate squatting it. The set-piece.
    WC    REFUGE POINTE (66,104): the hold-outs' camp in the lee of the scarp. The zone's friendly ground.
    NW    BOULDER'GOR (44,36): the ogre cave mouth, high on the moor.
    NE    WITHERBARK HOLLOW (142,40): a forward troll camp, the first sign of what Central is full of.
    SE    GO'SHEK FARM (124,124): a working farm the Syndicate took, below the scarp.
    E     THE EASTERN SEAM (176,84): on to Arathi Central.

HARD CONTRACTS (world/portal_manager.py)
  (4, 118)   <-> Eastern Hillsbrad       through Thoradin's Wall. Both directions, or portal_qa fails.
  (176, 84)  <-> Arathi Central          the east seam
  (44, 34)   <-> Boulder'gor             the ogre cave, this zone's one cave
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob, lobe, water_body, rock_spurs

KEY = "arathi_west"
#: Tilemap NAME is the key world/portal_manager.py looks portals up under (it keys on zone.name) and it must
#: match the name create_all_zones registers. Eastern Hillsbrad shipped once with these out of step and every
#: portal in both Hillsbrad zones was dead - you could walk in and never walk out. Flavour lives in DESC.
NAME = "Arathi West"
DESC = ("High moor behind Thoradin's Wall, split by a rock scarp: ogres and trolls above it, Stromgarde's "
        "ruin and the hold-outs below.")
REGION = "Eastern Kingdoms - Arathi Highlands"
W, H = 180, 170
BAKED_DIR = "assets/tiles/arathi_west/baked"
IS_TOWN = False
BASE_TILE = "grass"
SEED = 331

RU = "assets/tiles/ruins/"

PORTALS = {(4, 118): "Eastern Hillsbrad",
           (176, 84): "Arathi Central",
           (44, 34): "Boulder'gor"}
#: Arrival is 2 tiles SOUTH of the registered destination tile for an overworld portal (+3 leaving a cave),
#: so these columns are kept clear of solid landmarks by hand in dress().
ARRIVALS = [(4, 120), (176, 86), (44, 36)]
START = (10, 118)

# ---- roads --------------------------------------------------------------------------------------------
# The trunk is the old Arathor road: in at the wall, east along the FOOT of the scarp to Refuge Pointe, then
# up through the middle gap onto the moor and out the east seam. Branches hang off it. Every road is carved
# clear of rock in cliff_field, so a road through a gap is what makes that gap exist.
ROADS = {
    "trunk":      ([(4, 118), (24, 115), (48, 110), (66, 106), (88, 98), (106, 90), (134, 86), (176, 84)], 3.2),
    # south-west to Stromgarde's gate, through the lowland oaks
    "stromgarde": ([(28, 114), (26, 128), (32, 142), (40, 148)], 2.6),
    # north out of Refuge Pointe, up the WEST gap onto the moor and across to the ogre cave
    "boulder":    ([(62, 100), (56, 80), (50, 60), (46, 44), (44, 36)], 2.4),
    # the moor crossing, east along the top from the west gap to the troll camp
    "moor":       ([(52, 58), (80, 52), (108, 46), (132, 42), (142, 40)], 2.4),
    # the EAST gap: down off the moor to Go'Shek Farm and back onto the trunk
    "goshek":     ([(136, 60), (134, 86), (130, 106), (124, 122)], 2.4),
}
_RS = K.RoadSet(ROADS)
road_dist = _RS.dist


def paved(gx, gy):
    """Worn stone: Stromgarde's forecourt, Refuge Pointe's muster ground, the wall's gate road."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    keep = lobe(gx, gy, 36.0, 146.0, 13.0, 9.0) + 0.5 * wob(gx, gy)
    camp = lobe(gx, gy, 66.0, 104.0, 8.0, 6.0) + 0.5 * wob(gx, gy)
    gate = lobe(gx, gy, 8.0, 118.0, 6.0, 5.0) + 0.5 * wob(gx, gy)
    return np.maximum.reduce([keep, camp, gate]) - 1.2


# ---- water --------------------------------------------------------------------------------------------
# No sea in this zone - the coast is Arathi East's, by Kyle's split. What water there is belongs to the
# scarp: a river running along its foot (where the runoff goes) and two tarns caught on the moor above.
# Analytic with integer harmonics only, so the painted shoreline and the tile grid come from one function.
RIVER = [(20, 126), (44, 120), (70, 114), (96, 104), (120, 96), (150, 92), (178, 90)]
RIVER_W = 1.7
TARNS = [(74.0, 44.0, 5.0, 3.4, 0.2), (116.0, 34.0, 4.2, 3.0, -0.3)]


def river_field(gx, gy):
    d = np.full(np.shape(gx), 1e9)
    for (x0, y0), (x1, y1) in zip(RIVER, RIVER[1:]):
        d = np.minimum(d, K.seg_dist(gx, gy, x0, y0, x1, y1)
                       if hasattr(K, "seg_dist") else T.seg_dist(gx, gy, x0, y0, x1, y1))
    return (RIVER_W - d) + 0.30 * wob(gx * 1.3, gy * 1.3)


def tarn_field(gx, gy):
    p = np.full(np.shape(gx), -99.0)
    for (cx, cy, rx, ry, rot) in TARNS:
        p = np.maximum(p, water_body(gx, gy, cx, cy, rx, ry, rot))
    return p


def water_field(gx, gy):
    return np.maximum(river_field(gx, gy), tarn_field(gx, gy))


def deck_field(gx, gy):
    # One plank crossing where the trunk road meets the river, below Refuge Pointe.
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    return np.minimum.reduce([gx - 62.0, 72.0 - gx, gy - 108.0, 111.0 - gy])


# ---- rock: the scarp, and the rim -----------------------------------------------------------------------
# THE SCARP IS THE ZONE. One band of rock from the north-west corner to the south-east, pierced in exactly
# three places. It is expressed as distance from a polyline rather than as a list of spurs, because a scarp
# is one continuous thing and a list of segments produces a dotted line of outcrops instead of a wall.
SCARP = [(10, 92), (40, 84), (72, 76), (104, 68), (134, 62), (160, 52), (180, 44)]
SCARP_T = 7.0
#: (x, y, radius). Carved OUT of the scarp - the three ways through. Each one is wider than the scarp is
#: deep, per playbook section 3: a gap narrower than the band leaves roads dead-ending into painted cliff.
SCARP_GAPS = [(52.0, 80.0, 7.5),        # the west gap, the Boulder'gor road
              (104.0, 68.0, 7.5),       # the middle gap, the trunk road onto the moor
              (136.0, 61.0, 7.5)]       # the east gap, down to Go'Shek Farm

SPURS = [
    (0, 6, 60, 10, 3.4),            # the north rim, the Hinterlands shoulder
    (96, 4, 180, 12, 3.6),          # the north-east rim
    (168, 20, 180, 150, 3.4),       # the east rim, south of the seam
    (0, 140, 18, 168, 3.2),         # the south-west corner behind Stromgarde
    (40, 162, 150, 166, 3.4),       # the south rim: the cliffs above the cove country
    (0, 96, 6, 140, 3.0),           # the wall's own rock, north and south of the gate
    (0, 30, 8, 92, 3.2),
]
OUTCROPS = [
    (30, 52, 2.8, 2.2), (66, 30, 2.6, 2.0), (92, 30, 2.4, 2.0), (120, 52, 2.6, 2.2), (154, 34, 2.8, 2.2),
    (24, 134, 2.6, 2.0), (56, 136, 2.4, 2.0), (96, 128, 2.6, 2.0), (148, 116, 2.8, 2.2), (152, 146, 2.6, 2.0),
    (86, 150, 2.4, 2.0), (112, 150, 2.6, 2.0), (18, 70, 2.4, 2.0), (142, 88, 2.4, 2.0),
]


def scarp_field(gx, gy):
    """>0 inside the scarp. The gaps are subtracted, which is what makes them passable."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    d = np.full(np.shape(gx), 1e9)
    for (x0, y0), (x1, y1) in zip(SCARP, SCARP[1:]):
        d = np.minimum(d, T.seg_dist(gx, gy, x0, y0, x1, y1))
    # A LOW wobble amplitude on purpose. At 0.8 the band broke into a dotted line of outcrops
    # and stopped reading as one wall, which is the only thing this zone is built around.
    band = (SCARP_T - d) + 0.35 * wob(gx * 0.9, gy * 0.9)
    for (cx, cy, r) in SCARP_GAPS:
        cut = r - np.sqrt((gx - cx) ** 2 + (gy - cy) ** 2)
        band = np.where(cut > 0, np.minimum(band, -1.0), band)
    return band


def cliff_field(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    edge = np.minimum.reduce([gx, W - gx, gy, H - gy])
    rock = (5.0 + 3.0 * wob(gx * 0.5, gy * 0.5) + 1.2 * wob(gx * 1.4, gy * 1.4)) - edge
    rock = np.maximum(rock, rock_spurs(gx, gy, SPURS, OUTCROPS))
    rock = np.maximum(rock, scarp_field(gx, gy))
    # Roads, water and the deck always win over rock, in that order, so nothing is ever painted shut.
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    rock = np.where(water_field(gx, gy) > -1.0, np.minimum(rock, -0.5), rock)
    rock = np.where(deck_field(gx, gy) > -1.0, np.minimum(rock, -0.5), rock)
    return rock


def fields(gx, gy):
    gx = np.asarray(gx, float)
    w = water_field(gx, gy)
    # The river is wadeable its whole length (shallow only); the tarns have a deep middle.
    deep = tarn_field(gx, gy) - 2.0
    return dict(cliff=cliff_field(gx, gy), shallow=w, deep=deep, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


# ---- subzones (x, y, w, h) -------------------------------------------------------------------------------
# Later registration wins on overlap. Table keys must equal the encounters.json keys for this zone.
SUBZONES = [
    ("Thoradin's Wall", 0, 100, 26, 42),
    ("The Lowland Oaks", 20, 110, 44, 36),
    ("Stromgarde Keep", 16, 130, 48, 38),
    ("Refuge Pointe", 52, 92, 32, 26),
    ("The High Moor", 40, 24, 80, 44),
    ("Boulder'gor Crags", 26, 22, 42, 34),
    ("Witherbark Hollow", 120, 24, 50, 32),
    ("Go'Shek Farm", 106, 106, 50, 34),
]

# ---- baker config (read by tools/bake_arathi.py) ---------------------------------------------------------
# Heather and bracken rather than Hillsbrad's pasture: `dry` and `rocky` carry the high moor, `grass` and
# `forest` only survive in the lee of the scarp. That split IS the zone, so the painting has to say it too.
BASE = {"dry": 0.46, "grass": 0.26, "rocky": 0.20, "forest": 0.12}
PAINT = {
    "dry":    [(70, 40, 44, 24, 1.0), (116, 36, 34, 20, 0.95), (44, 44, 26, 18, 0.9), (150, 48, 22, 16, 0.8),
               (96, 58, 28, 14, 0.8), (30, 30, 20, 14, 0.7)],
    "rocky":  [(104, 68, 30, 10, 0.9), (52, 80, 24, 9, 0.85), (136, 61, 24, 9, 0.85), (36, 146, 14, 10, 0.8),
               (8, 118, 10, 8, 0.8), (44, 36, 12, 9, 0.7), (160, 50, 16, 10, 0.7)],
    "grass":  [(40, 120, 34, 20, 1.0), (72, 108, 30, 16, 0.95), (112, 112, 28, 16, 0.9), (24, 108, 18, 12, 0.8),
               (146, 100, 18, 12, 0.7)],
    "forest": [(34, 124, 18, 12, 0.9), (58, 132, 16, 11, 0.85), (104, 128, 14, 10, 0.8), (140, 118, 12, 9, 0.7)],
    "meadow": [(66, 104, 14, 9, 0.9), (124, 124, 14, 9, 0.85), (44, 112, 12, 8, 0.7)],
    "field":  [(124, 124, 16, 10, 1.0), (118, 114, 12, 8, 0.85)],
    "earth":  [(36, 146, 8, 6, 0.9), (66, 104, 7, 5, 0.9), (142, 40, 7, 5, 0.8), (44, 36, 6, 4, 0.8)],
    "gravel": [(8, 118, 7, 5, 0.7), (176, 84, 7, 5, 0.6), (104, 68, 8, 4, 0.6)],
    "shore":  [(70, 112, 10, 4, 0.7), (74, 44, 8, 4, 0.6)],
}
COBBLE = [(36, 146, 12, 8, 0.95), (66, 104, 8, 6, 0.9), (8, 118, 6, 5, 0.85)]

# ---- NPC spots ---------------------------------------------------------------------------------------
NPC_POSITIONS = {
    # Refuge Pointe - the hub. Every town needs an inn and a flight master (standing rule); this is a camp
    # rather than a town, so the inn is a field tent and the flight master keeps a hitched gryphon.
    # SPREAD, NOT REBUILT. Kyle, 7 Nov: "leave refuge point as external. DONT make
    # it into a town" - so this stays a camp on the open moor, which is what a
    # forward camp should look like. But the five of them were standing in a 14x10
    # box of it, which is the cramming complaint and applies to a camp as much as a
    # town. Now they sit one per thing the camp does, across 22x16: the scout out
    # west watching the road in, the commander at the tent, the quartermaster by
    # the stores, the innkeeper at the inn and the wind rider keeper out at the
    # stable, where the wyverns are.
    "arathi_refuge_commander": (64, 96),
    "arathi_refuge_quartermaster": (74, 104),
    "arathi_refuge_innkeeper": (58, 110),
    "arathi_refuge_flightmaster": (76, 113),  # moved off shallow water 7 Nov
    "arathi_refuge_scout": (54, 98),
    # the wall, and the road in
    "arathi_wall_warden": (12, 118),
    # Stromgarde's edge - someone watching the ruin from outside it
    "arathi_stromgarde_antiquarian": (46, 140),
    # the moor
    # ON the moor road, not in the scarp: (60,72) sat inside the escarpment band and the
    # flood-fill caught him standing in solid rock.
    "arathi_moor_shepherd": (62, 56),
    # above Go'Shek, out of the farm's sight
    "arathi_goshek_informant": (134, 108),
}

CHESTS = [(38, 40), (78, 46), (124, 36), (30, 148), (58, 138), (128, 126), (150, 96), (20, 112)]

#: Trees survive only below the scarp. FOREST scatters within `rim` tiles of rock, which on this map is the
#: lowland side of the escarpment and the southern cliffs - exactly where the shelter is.
OAKS = [("ek_willow", 8, 0.30), ("ek_pine_trio", 7, 0.32), ("ek_dead_oak", 7, 0.28), ("ek_willow", 7, 0.30)]
FOREST = dict(seed=37, count=86, rim=16, thorn=10, names=[
    ("ek_willow", 8, 0.30), ("ek_dead_oak", 7, 0.28), ("ek_pine_trio", 7, 0.32),
    ("ek_thorn_bush", 4, 0.40)])


def dress(L):
    p, b = L.prop, L.bld
    ENT = T.ENT

    # ---- Thoradin's Wall: the gate, from the Arathi side ------------------------------------------------
    # The portal tile (4,118) must stay walkable, so the gatehouse is placed BESIDE the road and the arch
    # over it is passable. Durnholde shipped this wrong once - a solid prop on the door it advertises.
    b("ek_ruined_gatehouse", 9, 114, 10, nudge=2)
    p(RU + "ruin_archway.png", 4, 116, 9, solid=False, nudge=0, road_ok=True, allow_overlap=True)
    for (x, y) in ((6, 106), (6, 128), (12, 102), (12, 132)):
        p(RU + "ruin_wall_arch.png", x, y, 6)
    p("ek_signpost", 16, 118, 4)
    b("ek_wayshrine", 20, 124, 5, nudge=2)

    # ---- Refuge Pointe: hold-outs camped in the lee of the scarp -----------------------------------------
    b("ek_command_tent", 66, 100, 8, nudge=2)
    b("ek_village_inn", 60, 106, 9, nudge=2)
    b("ek_border_watchtower", 74, 98, 11, nudge=2)
    b("ek_stable_block", 70, 110, 8, nudge=2)
    p("ek_farm_well", 70, 103, 4)
    p("ek_signpost", 56, 104, 4)
    for (x, y) in ((58, 96), (76, 104)):
        p("ek_farm_fence", x, y, 3, solid=True)
    p("ek_haystack", 78, 108, 4)

    # ---- Stromgarde Keep: the Arathor capital, fallen. The zone's set-piece -------------------------------
    # Arathor is what every human kingdom was carved out of, and this is the city it was run from. It gets
    # the biggest footprint on the map and no roof anywhere.
    p(RU + "ruin_archway.png", 36, 140, 10, solid=False, nudge=0, road_ok=True, allow_overlap=True)
    for (x, y) in ((24, 140), (48, 140), (24, 154), (48, 154)):
        p(RU + "ruin_wall_arch.png", x, y, 7)
    p(RU + "ruin_tower_skulls.png", 30, 152, 9)
    p(RU + "ruin_tower_skulls.png", 44, 150, 8)
    p(RU + "ruin_stone_ring.png", 36, 158, 4, solid=False)
    for (x, y) in ((28, 146), (44, 144), (38, 152)):
        p(RU + "ruin_wall_arch.png", x, y, 5)
    b("ek_burnt_cottage", 54, 146, 8, nudge=2)
    b("ek_syndicate_house", 20, 146, 8, nudge=2)
    p("ek_gibbet", 50, 152, 6)
    p("ek_dead_oak", 18, 136, 6)

    # ---- Boulder'gor: the ogre cave, high on the moor ----------------------------------------------------
    # Portal at (44,34), arrival (44,36): the mouth is drawn ABOVE the tile and the column below it is left
    # clear, because an ogre midden placed on the arrival tile is a player stuck inside a boulder.
    for (x, y) in ((36, 30), (52, 30)):
        p("ek_web_boulder", x, y, 6)
    p("ek_haystack", 38, 42, 4)          # ogre bedding, such as it is
    p("ek_farm_cart", 50, 42, 4)         # robbed off the Go'Shek road
    p("ek_signpost", 46, 46, 4)

    # ---- Witherbark Hollow: the forward troll camp, the warning shot for Central --------------------------
    b("ek_forsaken_field_tent", 142, 38, 7, nudge=2)
    b("ek_forsaken_field_tent", 150, 44, 7, nudge=2)
    p(RU + "ruin_bone_pillars.png", 146, 34, 7)
    p("ek_gibbet", 138, 46, 6)
    p("ek_cross_crows", 154, 36, 5)
    for (x, y) in ((134, 40), (156, 48)):
        p("ek_thorn_bush", x, y, 3, solid=False)

    # ---- Go'Shek Farm: a working farm the Syndicate took -------------------------------------------------
    b("ek_barn", 122, 120, 9, nudge=2)
    b("ek_cottage_medium", 132, 126, 8, nudge=2)
    b("ek_granary", 116, 126, 8, nudge=2)
    p("ek_scarlet_tent", 128, 132, 6)
    p("ek_farm_cart", 120, 130, 4)
    p("ek_scarecrow", 112, 120, 4)
    for x in (110, 116, 122):
        p("ek_farm_fence", x, 136, 3, solid=True)
    p("ek_haystack", 136, 120, 4)

    # ---- the moor itself: stone circles, and nothing else ------------------------------------------------
    # Arathi's signature. They are pre-Arathor, nobody in the zone will tell you what they are for, and on a
    # treeless moor a ring of standing stones is the only vertical thing for half a mile.
    for (x, y) in ((70, 56), (98, 38), (124, 58), (56, 36)):
        p(RU + "ruin_stone_ring.png", x, y, 5, solid=False)
    for (x, y) in ((82, 62), (110, 30), (140, 66), (64, 26)):
        p("ek_web_boulder", x, y, 5)

    # ---- the lowland oaks, below the scarp ----------------------------------------------------------------
    T.grove(L, 34, 120, 8, 6, 8, OAKS, seed=4)
    T.grove(L, 56, 130, 7, 6, 7, OAKS, seed=5)
    T.grove(L, 104, 124, 7, 5, 6, OAKS, seed=6)
    p("ek_signpost", 92, 100, 4)
    b("ek_wayshrine", 118, 92, 5, nudge=2)

    # ---- the east seam ------------------------------------------------------------------------------------
    p("ek_signpost", 168, 86, 4)
    p(RU + "ruin_wall_arch.png", 172, 78, 6)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_arathi_west():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/arathi_west_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
