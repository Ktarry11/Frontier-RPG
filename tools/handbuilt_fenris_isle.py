"""
Hand-built Fenris Isle (160x140): the cursed island in Lordamere Lake, levels 17-22.

Laid out as a real island, north up, ringed by wadeable shallows and then deep water:
    S    THE FERRY PIER (80,129): the Decrepit Ferry's landing; BLOODMOON VILLAGE (80,104) crowds up the shore behind it, the only
         roofed ground on the isle
    SW   THE DROWNED DOCKS (44,110): a wrecked jetty, a beached hull and the drowned crew that never left it
    W    the west arm and the rock face over SHADOWPINE ALTAR (30,55): a ritual arch cut into the ridge
    N    FENRIS PROPER (80,30): Baron Ashbury's manor on the northern rise, behind a shattered wall and one cracked gate
    E    CUR'S GRAVE (128,74): the hound-boneyard lobe, graves, kennels, bone-pillars
    all the rest is THE CURSED SHORE: dead pine, thorn, driftwood and wreckage

AREA ARCHETYPE: AN ISLAND WITH A SPINE.  One road rises from the pier through the village and runs the island's length to the manor;
two spurs branch off it (west to the altar's ridge, east to the grave), and a shore track hugs the south-west to the docks.  Everything
that is not road is open shore - you can walk the whole coast.

HARD CONTRACTS (world/portal_manager.py)
  portals  Silverpine South ferry (151,44) -> here (80,129) [arrive (80,127), on the pier]
           Shadowpine Altar (75,115) -> here (30,55) [arrive (30,57)]; this (30,55) -> Shadowpine Altar (75,115)
           this (80,129) -> Silverpine South (149,46)
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob, lobe, water_body, rock_spurs

KEY = "fenris_isle"
NAME = "Fenris Isle"
DESC = "Fenris Isle. A cursed island in Lordamere Lake, haunted by worgen, drowned sailors and a baron who would not stay buried."
REGION = "Eastern Kingdoms - Lordaeron"
W, H = 160, 140
BAKED_DIR = "assets/tiles/fenris_isle/baked"
IS_TOWN = False
BASE_TILE = "grass"
SEED = 97

PORTALS = {(80, 129): "Silverpine South", (30, 55): "Shadowpine Altar"}
ARRIVALS = [(80, 127), (30, 57)]
START = (80, 118)

ROADS = {
    "pier":   ([(80, 123), (80, 114), (80, 106)], 3.0),
    "spine":  ([(80, 106), (81, 92), (80, 78), (81, 64), (80, 52), (80, 44), (80, 39)], 3.2),
    "west":   ([(80, 72), (66, 67), (52, 63), (40, 59), (31, 56)], 2.6),
    "east":   ([(81, 72), (96, 73), (110, 75), (122, 74), (132, 72)], 2.6),
    "docks":  ([(76, 108), (64, 110), (52, 112), (44, 112)], 2.4),
}
_RS = K.RoadSet(ROADS)
road_dist = _RS.dist

DECKS = [(78.0, 82.0, 122.0, 131.5),            # the ferry pier
         (41.0, 45.0, 116.0, 124.0)]            # the Drowned Docks' broken jetty


def paved(gx, gy):
    """Flags under the village square and the manor's forecourt."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    sq = lobe(gx, gy, 80.0, 104.0, 9.0, 6.0) + 0.5 * wob(gx, gy)
    ct = lobe(gx, gy, 80.0, 38.0, 9.0, 5.0) + 0.5 * wob(gx, gy)
    return np.maximum(sq, ct) - 1.2


# ---- the island: a union of lobes ------------------------------------------------------------------------------------
LOBES = [
    (80.0, 62.0, 52.0, 40.0, 0.0),          # the main body
    (80.0, 108.0, 30.0, 18.0, 0.0),         # the southern shore: the village and the pier
    (36.0, 62.0, 22.0, 15.0, 0.0),          # the west arm (the altar's ridge)
    (128.0, 74.0, 22.0, 20.0, 0.0),         # the east lobe (Cur's Grave)
    (80.0, 28.0, 24.0, 13.0, 0.0),          # the northern headland (the manor)
    (46.0, 108.0, 16.0, 12.0, 0.0),         # the south-west shore (the docks)
]


COVES = [(138.0, 40.0, 13.0, 9.0, 0.3), (30.0, 38.0, 13.0, 8.0, -0.3), (108.0, 124.0, 11.0, 8.0, 0.0)]


def land_field(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    land = np.full(gx.shape, -99.0)
    for (cx, cy, rx, ry, rot) in LOBES:
        land = np.maximum(land, lobe(gx, gy, cx, cy, rx, ry, rot))
    land = land + 1.3 * wob(gx * 0.6, gy * 0.6) + 0.7 * wob(gx * 1.5, gy * 1.5)
    for (cx, cy, rx, ry, rot) in COVES:                     # bites out of the coast
        c = lobe(gx, gy, cx, cy, rx, ry, rot)
        land = np.where(c > 0, np.minimum(land, -c * 0.9), land)
    return land


def sea_field(gx, gy):
    """Lordamere around the isle (>0 in the water): the island is a lake island, all the rest is open water."""
    return -land_field(gx, gy)


POOLS = []


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


# ---- rock ------------------------------------------------------------------------------------------------------------
SPURS = [
    (52, 41, 70, 42, 2.4),         # the manor's wall, west of the gate
    (90, 42, 108, 40, 2.4),        # ... and east of it
    (10, 49, 52, 49, 3.6),         # the altar's ridge: the cave mouth cuts into its southern face
    (112, 50, 152, 55, 2.8),       # the north bank of Cur's Grave
    (110, 94, 142, 92, 2.4),       # the south bank of Cur's Grave
    (26, 82, 54, 86, 2.2),         # the rock between the west arm and the docks
]
OUTCROPS = [
    (62, 56, 2.6, 2.0), (98, 60, 2.6, 2.0), (66, 88, 2.4, 2.0), (100, 90, 2.4, 2.0), (56, 34, 2.6, 2.0),
    (106, 32, 2.4, 2.0), (30, 74, 2.4, 2.0), (136, 82, 2.6, 2.0), (118, 62, 2.4, 2.0), (70, 30, 2.0, 1.6),
]


def cliff_field(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    edge = np.minimum.reduce([gx, W - gx, gy, H - gy])
    rock = (4.0 + 2.0 * wob(gx * 0.5, gy * 0.5)) - edge
    rock = np.maximum(rock, rock_spurs(gx, gy, SPURS, OUTCROPS))
    wf = water_field(gx, gy)
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    rock = np.where(wf > -1.0, np.minimum(rock, -3.0), rock)        # open water: no rim shading at the map edge
    rock = np.where(deck_field(gx, gy) > -1.0, np.minimum(rock, -3.0), rock)
    return rock


def fields(gx, gy):
    gx = np.asarray(gx, float)
    w = water_field(gx, gy)
    deep = np.maximum(sea_field(gx, gy) - 2.6, pool_field(gx, gy) - 2.2)
    return dict(cliff=cliff_field(gx, gy), shallow=w, deep=deep, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


# ---- subzones (x, y, w, h[, display]) --------------------------------------------------------------------------------
SUBZONES = [
    ("Fenris Proper", 54, 14, 52, 34),
    ("The Drowned Docks", 24, 94, 42, 34),
    ("Cur's Grave", 104, 52, 50, 46),
    ("Bloodmoon Village", 62, 94, 38, 32),
]

# ---- baker config (read by tools/bake_silverpine.py) -------------------------------------------------------------------
BASE = {"pine": 0.30, "fern": 0.18, "mulch": 0.30, "rocky": 0.16}
PAINT = {
    "grass":  [(70, 70, 14, 9, 0.8), (100, 70, 12, 8, 0.8), (60, 90, 10, 6, 0.6)],
    "cursed": [(80, 32, 22, 11, 1.0), (62, 22, 10, 5, 0.7), (100, 24, 10, 5, 0.7), (80, 54, 14, 6, 0.6)],
    "earth":  [(128, 74, 18, 14, 1.0), (116, 82, 10, 6, 0.8), (140, 68, 8, 5, 0.8)],
    "bog":    [(40, 118, 8, 4, 0.5)],
    "rocky":  [(30, 58, 12, 6, 0.8), (84, 42, 10, 4, 0.5), (40, 84, 10, 5, 0.6)],
    "gravel": [(30, 56, 8, 5, 0.8), (80, 34, 8, 4, 0.4)],
    "den":    [(124, 66, 8, 5, 0.6)],
    "shore":  [(80, 124, 8, 5, 0.6), (44, 118, 8, 4, 0.7)],
}
COBBLE = [(80, 104, 9, 6, 0.9), (80, 38, 9, 5, 0.9)]

# ---- NPC spots ------------------------------------------------------------------------------------------------------
NPC_POSITIONS = {
    "fenris_pier_warden": (83, 120),
    "bloodmoon_elder": (76, 102),                  # Elder Gravemoss
    "fenris_village_elder": (85, 101),             # Huntsman Corwell
    "fenris_provisioner": (89, 107),               # vendor
    "fenris_keep_scout": (83, 47),
    "fenris_altar_warden": (35, 59),
    "fenris_grave_hunter": (118, 73),
}
CHESTS = [(92, 28), (40, 106), (140, 82), (24, 66), (100, 98)]

FOREST = dict(seed=53, count=110, rim=30, thorn=22, names=[
    (T.HFP + "dead_pine_cluster.png", 5, 0.40), (T.HFP + "dead_pine_cluster.png", 6, 0.40), ("ek_dead_oak", 6, 0.34),
    (T.CIP + "cursed_dead_tree_cluster.png", 6, 0.40), ("ek_pine_tall", 8, 0.28)])

DEADS = [(T.HFP + "dead_pine_cluster.png", 5, 0.4), ("ek_dead_oak", 6, 0.34), (T.CIP + "cursed_dead_tree_cluster.png", 6, 0.4)]


def dress(L):
    p, b = L.prop, L.bld
    HF, CI = T.HFP, T.CIP
    CO, RU = "assets/tiles/coastal_props/", "assets/tiles/ruins/"
    # ---- the ferry pier: moorings, lanterns, a few crates
    p(CO + "mooring_posts.png", 78, 123, 3, road_ok=True, shore_ok=True, allow_overlap=True, nudge=0)
    p(CO + "mooring_posts.png", 81, 123, 3, road_ok=True, shore_ok=True, allow_overlap=True, nudge=0)
    p(CO + "dock_lantern_post.png", 76, 121, 4, road_ok=True, shore_ok=True, allow_overlap=True, nudge=0)
    p(CO + "dock_lantern_post.png", 84, 121, 4, road_ok=True, shore_ok=True, allow_overlap=True, nudge=0)
    p(CO + "fish_crates_traps.png", 88, 122, 4)
    p(CO + "rowboat_wreck.png", 70, 124, 3, shore_ok=True)
    p("ek_signpost", 85, 117, 4)
    # ---- Bloodmoon Village: the only roofed ground on the isle
    b("forsaken_house_medium", 68, 98, 9, nudge=2)                  # the elder's lodge
    b("forsaken_house_small", 92, 96, 8, nudge=2)
    p(CI + "cursed_village_hut.png", 66, 108, 6)
    p(CI + "cursed_village_hut.png", 94, 110, 6)
    p(CI + "cursed_village_hut.png", 60, 100, 6)
    p("ek_farm_well", 80, 98, 4)
    p("ek_farm_cart", 72, 111, 4)
    p("ek_haystack", 88, 112, 4)
    p("ek_forsaken_banner", 74, 94, 5)
    p("ek_forsaken_banner", 87, 94, 5)
    p("ek_gibbet", 96, 104, 6)
    p("ek_signpost", 82, 90, 4)
    T.grove(L, 54, 96, 5, 5, 4, DEADS, seed=3)
    T.grove(L, 104, 104, 5, 5, 4, DEADS, seed=4)
    # ---- The Drowned Docks: a broken jetty, a beached hull, the crew's gear
    p(CI + "shipwreck_hull.png", 36, 116, 9, shore_ok=True)
    p(CO + "mooring_posts.png", 43, 115, 3, road_ok=True, shore_ok=True, allow_overlap=True, nudge=0)
    p(CO + "dock_lantern_post.png", 40, 119, 4, road_ok=True, shore_ok=True, allow_overlap=True, nudge=0)
    p(CO + "fish_crates_traps.png", 52, 106, 4)
    p(CO + "driftwood_pile.png", 32, 108, 3, shore_ok=True)
    p(CO + "rowboat_wreck.png", 56, 118, 3, shore_ok=True)
    p("ek_open_grave", 50, 100, 3)
    p("ek_signpost", 58, 110, 4)
    # ---- Shadowpine Altar's ridge: the ritual arch
    L.cave(30, 55, "ent_moonlit_arch", 9, 6)
    p(RU + "ruin_stone_ring.png", 38, 60, 4, solid=False)
    p("ek_forsaken_banner", 24, 57, 5)
    p("ek_grave_hand", 36, 52, 3)
    p(HF + "twisted_root_arch.png", 46, 62, 6)
    p("ek_signpost", 46, 58, 4)
    # ---- Fenris Proper: Baron Ashbury's manor on the northern rise
    b("forsaken_town_hall", 80, 29, 12, nudge=1)                    # the manor
    p("ek_ruin_wall", 62, 38, 4)
    p("ek_ruin_wall", 98, 38, 4)
    p("ek_ruin_wall", 66, 22, 4)
    p("ek_ruin_wall", 94, 22, 4)
    p("ek_cemetery_gate", 80, 43, 5, solid="core", road_ok=True, allow_overlap=True, nudge=0)
    p("ek_dry_fountain", 80, 36, 5, solid="core", nudge=1)
    p("ek_angel_statue", 70, 34, 5)
    p("ek_angel_statue", 90, 34, 5)
    p("ek_forsaken_banner", 74, 40, 5)
    p("ek_forsaken_banner", 86, 40, 5)
    p("ek_gibbet", 66, 30, 6)
    p("ek_open_grave", 94, 30, 3)
    p("ek_cross_crows", 62, 28, 4)
    p("ek_signpost", 82, 50, 4)
    T.grove(L, 60, 48, 5, 4, 4, DEADS, seed=5)
    T.grove(L, 100, 50, 5, 4, 4, DEADS, seed=6)
    # ---- Cur's Grave: hound bones, markers and a rotten kennel
    for (x, y) in [(120, 66), (128, 62), (136, 70), (124, 82), (134, 78)]:
        p(CI + "worn_tombstone_row.png", x, y, 4)
    p(RU + "ruin_bone_pillars.png", 128, 72, 6, solid="core")
    p("ek_open_grave", 118, 80, 3)
    p("ek_open_grave", 138, 64, 3)
    p("ek_grave_hand", 142, 74, 3)
    p("ek_grave_hand", 114, 70, 3)
    p("ek_cross_crows", 130, 84, 4)
    p("ek_plague_cart", 112, 78, 4)
    p("ek_signpost", 108, 74, 4)
    # ---- the Cursed Shore: wreckage and a lone watch-cairn
    p(CI + "shipwreck_hull.png", 62, 21, 9, shore_ok=True)
    p(CO + "driftwood_pile.png", 108, 29, 3, shore_ok=True)
    p(CO + "rowboat_wreck.png", 140, 96, 3, shore_ok=True)
    p("ek_toadstools", 98, 52, 2, solid=False)
    p("ek_grave_hand", 70, 78, 3)
    p("ek_web_boulder", 52, 70, 4)
    p(RU + "ruin_stone_ring.png", 60, 76, 4, solid=False)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_fenris_isle():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/fenris_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
