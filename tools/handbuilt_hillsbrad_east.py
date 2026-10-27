"""
Hand-built Eastern Hillsbrad Foothills (160x160): Tarren Mill and the Syndicate hills, levels 20-24.

Kyle: "Don't forget, hillsbrand is still kind of green. This is classic wow." -- and "We need to split it into eastern
and western Hillsbrad."

THE GREEN: every Lordaeron zone so far (Tirisfal, Silverpine, Fenris) is blighted olive and grey. Hillsbrad is the first
HEALTHY country the player walks into and the contrast IS the content, so the palette is built from the Ashenvale greens
rather than the Silverpine set (measured colours in tools/build_hillsbrad_palette.py), the base ground cover is pasture
rather than forest mat, and the dry khaki meadow appears only at the foot of the mountains so elevation reads without the
zone reading as plagued.

THE SPLIT (Kyle: "Players enter from the west bro"): the Silverpine road enters WESTERN Hillsbrad (20-24), which is the
Classic map - Silverpine borders Hillsbrad's north-WEST, and Tarren Mill sits north-EAST, so the player lands in the farm
country and runs east to reach the Forsaken. This half is therefore the second leg: higher band, Tarren Mill as its hub,
and the zone's heavy set-pieces (Durnholde, the ogre stead, the shut Arathi wall).

Laid out on the REAL Classic Hillsbrad map, eastern half (north is up; Alterac's peaks are the north and east rim, the
sea is the south coast, Arathi lies beyond the south-east wall):
    W     the road in from Western Hillsbrad arrives at (5,86)
    NC    TARREN MILL (62,30): the Forsaken town, the hub, first friendly ground since the Sepulcher
    NW    MUDSNOUT HOLLOW (28,46): gnolls in the northern hills, off the west road
    NE    GAVIN'S NAZE (124,32): a Syndicate camp on the Alterac road
    EC    DURNHOLDE KEEP (108,76): the ruined keep on its bluff, Syndicate-held - the zone's set-piece
    SE    NETHANDER STEAD (122,118): ogres squatting an abandoned farm
    S     DUN GAROK ROAD (92,134): the dwarven fort's approach under the southern ridge
    S     THE EASTERN STRAND (56,142): Daggerspine murlocs on the south sand
    SE    THORADIN'S WALL (136,148): the old wall on the Arathi border, shut like Greymane's

AREA ARCHETYPE: OPEN GREEN HILL COUNTRY ringed by mountains - a long north-south trunk road with five branches, hedgerows
and oak stands instead of pine walls, and one ruined keep dominating the east.

HARD CONTRACTS (world/portal_manager.py)
  portals  Western Hillsbrad <- (5,86)
  Durnholde Keep's interior is a LATER STAGE - the gate is dressed here but no portal is registered until that zone
  exists, because portal_qa checks both directions.
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob, lobe, water_body, rock_spurs

KEY = "eastern_hillsbrad"
NAME = "Eastern Hillsbrad"
#: The Tilemap NAME is the key world/portal_manager.py looks portals up under (it keys on zone.name), and it has
#: to match the name this zone is registered as in create_all_zones. It did not: the map was called
#: "... Foothills" while the registry said "... Hillsbrad", so get_destination never matched and EVERY portal in
#: both Hillsbrad zones was dead - you could walk into Hillsbrad and never walk out. The flavour name lives in
#: DESC and the subzones instead; this one is an identifier.
DESC = "Green hill country under Alterac: Tarren Mill, the Syndicate's camps, and Durnholde's ruin."
REGION = "Eastern Kingdoms - Lordaeron"
W, H = 160, 160
BAKED_DIR = "assets/tiles/hillsbrad_east/baked"
IS_TOWN = False
BASE_TILE = "grass"
SEED = 112

PORTALS = {(5, 86): "Western Hillsbrad",
           (62, 28): "Tarren Mill",                    # the town gate off the mill square
           (109, 74): "Durnholde Keep",                # the keep's fallen archway
           (95, 138): "Dun Garok",                    # the fort door in the southern ridge
           (116, 7): "The Frostward Descent"}         # the fissure north of the Naze, under Alterac
ARRIVALS = [(8, 86), (62, 30), (108, 77), (94, 138), (116, 8)]
START = (14, 86)

ROADS = {
    # the length of the zone: Tarren Mill down to the southern strand. The northern leg used to run up to a
    # Silverpine portal at (46,5); that entrance moved to Western Hillsbrad, so the road starts at the town.
    "trunk":     ([(60, 24), (62, 30), (64, 52), (66, 78), (64, 104), (61, 126)], 3.4),
    # west out of Tarren Mill, past the gnoll hollow, to the Western Hillsbrad road
    "west":      ([(54, 33), (36, 42), (22, 58), (12, 74), (6, 86)], 2.8),
    # east along the top to Gavin's Naze and the Alterac road
    "naze":      ([(68, 28), (92, 26), (112, 28), (124, 33)], 2.6),
    # east across the hills to Durnholde's bluff
    "durnholde": ([(66, 66), (86, 70), (104, 74), (116, 77)], 2.6),
    # south-east to the ogre stead and on to the wall
    "stead":     ([(67, 100), (90, 108), (110, 114), (121, 118)], 2.4),
    "wall":      ([(121, 118), (131, 133), (138, 147)], 2.4),
    # the southern coast road and the dwarven fort's approach
    "garok":     ([(63, 118), (80, 128), (93, 135)], 2.4),
    "strand":    ([(61, 126), (57, 138), (54, 146)], 2.2),
}
_RS = K.RoadSet(ROADS)
road_dist = _RS.dist

# the fishing jetty on the Eastern Strand: (x0, x1, y0, y1)
DECKS = [(50.0, 60.0, 149.0, 151.4)]


def paved(gx, gy):
    """Worn stone under Tarren Mill's square, Durnholde's forecourt and the Naze camp."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    mill = lobe(gx, gy, 62.0, 30.0, 10.0, 7.0) + 0.5 * wob(gx, gy)
    keep = lobe(gx, gy, 109.0, 76.0, 8.0, 6.0) + 0.5 * wob(gx, gy)
    naze = lobe(gx, gy, 124.0, 33.0, 5.5, 4.0) + 0.5 * wob(gx, gy)
    return np.maximum.reduce([mill, keep, naze]) - 1.2


# ---- water -----------------------------------------------------------------------------------------------------
# The sea along the south rim only (the big west coast belongs to Western Hillsbrad). Analytic, integer harmonics only,
# so the painted shoreline and the tile grid come from one function.
SEA_S = (58.0, 186.0, 92.0, 42.0)
POOLS = [(88.0, 58.0, 4.4, 3.0, 0.2), (34.0, 96.0, 4.0, 2.8, -0.3)]      # two hill tarns


def sea_field(gx, gy):
    return water_body(gx, gy, *SEA_S)


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
# Alterac along the north and east, the Arathi shoulder in the south-east. Gaps are carved as corridors, not squares,
# so roads never dead-end into painted cliff (playbook section 3). The WEST rim is deliberately open - that edge is the
# seam with Western Hillsbrad and the road has to walk straight out of it.
SPURS = [
    (0, 12, 34, 8, 3.2),            # the north-west shoulder beside the Silverpine pass
    (64, 6, 112, 9, 3.0),           # the ridge the Naze road runs under
    (128, 4, 160, 16, 3.6),         # Alterac's corner above the Naze
    (152, 24, 160, 62, 3.6),        # the east rim, Alterac proper
    (148, 62, 160, 96, 3.2),        # the shoulder behind Durnholde
    (150, 98, 160, 130, 3.0),       # the Arathi shoulder
    (118, 152, 160, 152, 3.2),      # Thoradin's Wall rock
    (84, 146, 112, 150, 2.8),       # the southern ridge over the Dun Garok road
]
OUTCROPS = [
    (40, 36, 2.6, 2.0), (84, 40, 2.4, 2.0), (108, 48, 2.6, 2.0), (30, 70, 2.4, 2.0), (118, 100, 2.6, 2.2),
    (140, 70, 2.8, 2.2), (46, 108, 2.4, 2.0), (96, 92, 2.6, 2.0), (138, 128, 2.6, 2.0), (26, 28, 2.4, 2.0),
    (78, 118, 2.2, 1.8), (104, 122, 2.4, 2.0), (20, 110, 2.4, 2.0),
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
    ("Tarren Mill", 42, 14, 46, 34),
    ("Mudsnout Hollow", 10, 32, 34, 30),
    ("Gavin's Naze", 100, 14, 56, 30),
    ("Durnholde Keep", 88, 58, 54, 36),
    ("Nethander Stead", 100, 98, 50, 30),
    ("The Eastern Strand", 32, 126, 44, 30),
    ("Dun Garok Road", 76, 120, 40, 30),
    ("Thoradin's Wall", 116, 134, 44, 22),
]

# ---- baker config (read by tools/bake_hillsbrad.py) ---------------------------------------------------------------
# Green-dominant: grass is the base everywhere, oak/fern only in the stands, `dry` reserved for the mountain foot.
BASE = {"grass": 0.62, "forest": 0.22, "fern": 0.16, "rocky": 0.12}
PAINT = {
    "grass":  [(56, 56, 26, 22, 1.0), (88, 86, 24, 18, 1.0), (40, 30, 16, 12, 0.9), (112, 60, 16, 12, 0.8),
               (70, 116, 16, 12, 0.8), (124, 108, 12, 9, 0.7)],
    "meadow": [(44, 54, 12, 8, 0.9), (82, 50, 12, 8, 0.9), (36, 86, 10, 7, 0.8), (100, 96, 10, 7, 0.7),
               (70, 94, 9, 6, 0.7)],
    "field":  [(60, 34, 12, 7, 1.0), (70, 24, 10, 6, 0.9), (122, 116, 10, 6, 0.9), (52, 44, 9, 5, 0.8)],
    "dry":    [(58, 16, 16, 9, 0.8), (104, 18, 14, 8, 0.7), (134, 44, 10, 7, 0.7), (28, 26, 10, 6, 0.6),
               (100, 146, 14, 6, 0.6)],
    "forest": [(30, 56, 12, 9, 0.8), (92, 44, 12, 8, 0.8), (46, 116, 10, 7, 0.7), (122, 90, 10, 7, 0.7)],
    "earth":  [(62, 31, 7, 5, 0.8), (109, 76, 6, 4, 0.8), (124, 33, 5, 4, 0.8)],
    "rocky":  [(109, 76, 9, 6, 0.7), (136, 148, 16, 5, 0.7), (94, 136, 8, 5, 0.6), (24, 108, 8, 5, 0.6)],
    "gravel": [(8, 86, 7, 5, 0.6), (124, 34, 6, 4, 0.6), (93, 136, 6, 4, 0.5)],
    "shore":  [(56, 148, 18, 6, 0.9), (88, 150, 14, 5, 0.8)],
}
COBBLE = [(62, 30, 10, 7, 0.9), (109, 76, 8, 6, 0.9), (124, 33, 5.5, 4, 0.8)]

# ---- NPC spots -----------------------------------------------------------------------------------------------------
NPC_POSITIONS = {
    # Tarren Mill - the hub
    "hbe_mill_magistrate": (60, 28),
    "hbe_mill_apothecary": (66, 29),
    "hbe_mill_quartermaster": (63, 34),      # vendor
    "hbe_mill_deathguard": (56, 31),
    "hbe_mill_caravan_master": (68, 34),
    "hbe_mill_hunter": (58, 38),
    # the road in from Silverpine
    "hbe_west_gate_scout": (12, 88),
    # the hollow and the west road
    "hbe_hollow_trapper": (32, 48),
    "hbe_west_outrider": (20, 62),
    # the Naze
    "hbe_naze_infiltrator": (119, 33),
    # Durnholde
    "hbe_durnholde_watcher": (100, 75),
    "hbe_durnholde_scholar": (104, 80),
    # the south
    "hbe_stead_outrider": (114, 116),
    "hbe_garok_sapper": (86, 131),
    "hbe_strand_tidewatcher": (58, 134),
    "hbe_wall_sentry": (130, 142),
}
CHESTS = [(34, 38), (96, 52), (26, 96), (134, 96), (84, 140), (58, 112)]

OAKS = [("ek_willow", 8, 0.30), ("ek_pine_trio", 7, 0.32), ("ek_pine_tall", 8, 0.28), ("ek_willow", 7, 0.30)]

FOREST = dict(seed=61, count=118, rim=24, thorn=12, names=[
    ("ek_willow", 8, 0.30), ("ek_willow", 7, 0.30), ("ek_pine_trio", 7, 0.32), ("ek_pine_tall", 8, 0.28),
    ("ek_thorn_bush", 4, 0.40)])


def dress(L):
    p, b = L.prop, L.bld
    HF, CO, RU, ENT = T.HFP, "assets/tiles/coastal_props/", "assets/tiles/ruins/", T.ENT

    # ---- the west road in from Western Hillsbrad
    p("ek_signpost", 12, 82, 4)
    p("ek_ruin_wall", 10, 92, 4)
    T.grove(L, 18, 76, 6, 6, 6, OAKS, seed=2)

    # ---- Tarren Mill: the Forsaken town, the only friendly ground in the zone
    b("forsaken_town_hall", 62, 25, 10, nudge=2)
    b("forsaken_house_medium", 54, 30, 9, nudge=2)
    b("forsaken_house_small", 70, 27, 8, nudge=2)
    b("forsaken_house_small", 68, 36, 8, nudge=2)
    b("forsaken_house_small", 52, 38, 8, nudge=2)
    p("ek_forsaken_banner", 57, 26, 5)
    p("ek_forsaken_banner", 67, 32, 5)
    p("ek_farm_well", 62, 34, 4)
    p("ek_plague_cauldron", 66, 24, 4)
    p("ek_plague_cart", 72, 32, 4)
    p("ek_signpost", 52, 28, 4)
    for x in (46, 52):
        p("ek_farm_fence", x, 44, 3, solid=True)
    for (x, y) in [(74, 22), (76, 28)]:
        p("ek_haystack", x, y, 4)
    p("ek_scarecrow", 72, 42, 4)

    # ---- Mudsnout Hollow: a gnoll camp in the northern hills
    p("ek_haystack", 26, 44, 4)
    p("ek_haystack", 34, 50, 4)
    for (x, y) in [(22, 42), (30, 42), (36, 54)]:
        p("ek_thorn_bush", x, y, 3, solid=False)
    p("ek_farm_cart", 28, 52, 4)
    p("ek_signpost", 38, 46, 4)
    T.grove(L, 18, 50, 7, 5, 7, OAKS, seed=3)

    # ---- Gavin's Naze: a Syndicate camp on the Alterac road
    p("ek_scarlet_tent", 121, 30, 6)
    p("ek_scarlet_tent", 127, 36, 6)
    p("ek_scarlet_crates", 124, 38, 4)
    p("ek_signpost", 115, 31, 4)
    p("ek_dead_oak", 132, 28, 6)
    p("ek_gibbet", 130, 38, 6)

    # ---- Durnholde Keep: the ruined keep on its bluff, the zone's set-piece
    # The archway stands over the PORTAL tile (109,74) -> Durnholde Keep, so it is drawn but passable:
    # solid here would wall off the dungeon door it advertises (same mistake as Azurelode's adit).
    p(RU + "ruin_archway.png", 109, 72, 9, solid=False, nudge=0, road_ok=True, allow_overlap=True)
    for (x, y) in [(102, 70), (116, 70), (102, 82), (116, 82)]:
        p(RU + "ruin_wall_arch.png", x, y, 6)
    p(RU + "ruin_tower_skulls.png", 113, 80, 8)
    p(RU + "ruin_stone_ring.png", 104, 86, 4, solid=False)
    p("ek_scarlet_banner", 105, 78, 5)
    p("ek_scarlet_banner", 115, 86, 5)
    p("ek_gibbet", 118, 76, 6)
    p("ek_signpost", 96, 75, 4)
    p("ek_dead_oak", 100, 88, 6)

    # ---- Nethander Stead: ogres squatting an abandoned farm
    b("generic_shack_b", 122, 114, 8, nudge=2)
    p(HF + "burned_house_ruin.png", 130, 120, 7)
    p("ek_farm_cart", 116, 120, 4)
    p("ek_haystack", 126, 108, 4)
    p("ek_scarecrow", 114, 110, 4)
    for x in (112, 118, 124):
        p("ek_farm_fence", x, 124, 3, solid=True)
    p("ek_signpost", 108, 114, 4)

    # ---- Dun Garok Road: the dwarven fort's approach under the southern ridge
    # The fort door is the PORTAL tile (95,138), cut into the ridge rock that starts at y=139. Drawn but
    # passable - a solid prop here would wall off the door it advertises (the mistake Azurelode's adit and
    # Durnholde's archway both had).
    p(ENT + "ent_cliff_road_tunnel.png", 95, 138, 8, solid=False, nudge=0, allow_overlap=True)
    p("ek_forsaken_banner", 90, 136, 5)
    p("ek_signpost", 84, 130, 4)
    p(RU + "ruin_wall_arch.png", 96, 140, 6)
    p(RU + "ruin_wall_arch.png", 104, 142, 6)
    p("ek_scarlet_crates", 90, 134, 4)
    p("ek_dead_oak", 80, 136, 6)

    # ---- the Eastern Strand: murlocs on the south sand
    for (x, y) in [(46, 144), (60, 146), (40, 140)]:
        p(CO + "driftwood_pile.png", x, y, 3, shore_ok=True)
    p(CO + "rowboat_wreck.png", 52, 146, 3, shore_ok=True)
    p(CO + "fish_drying_rack.png", 62, 140, 4)
    p(CO + "mooring_posts.png", 54, 149, 3, shore_ok=True)
    p(CO + "coral_reef_outcrop.png", 44, 150, 3, shore_ok=True)
    p("ek_signpost", 64, 132, 4)

    # ---- Thoradin's Wall: the Arathi border, shut
    for x in (120, 128, 136, 144, 152):
        p(RU + "ruin_wall_arch.png", x, 154, 6)
    p(RU + "ruin_archway.png", 140, 152, 8, solid=True, nudge=0, road_ok=True, allow_overlap=True)
    p("ek_signpost", 134, 144, 4)
    p("ek_dead_oak", 124, 148, 6)

    # ---- hedgerows and oak stands that break the hills up
    T.grove(L, 44, 62, 6, 8, 8, OAKS, seed=7)
    T.grove(L, 86, 96, 8, 6, 8, OAKS, seed=8)
    T.grove(L, 34, 114, 7, 6, 7, OAKS, seed=9)
    T.grove(L, 78, 60, 7, 5, 7, OAKS, seed=10)
    T.grove(L, 128, 60, 7, 5, 7, OAKS, seed=11)
    T.grove(L, 92, 20, 8, 5, 8, OAKS, seed=12)
    T.grove(L, 140, 108, 6, 8, 7, OAKS, seed=13)
    T.grove(L, 20, 86, 5, 6, 6, OAKS, seed=14)
    T.grove(L, 104, 106, 6, 5, 6, OAKS, seed=15)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_hillsbrad_east():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/hbe_shape.png"
    T.shape_preview(sys.modules[__name__], out)
