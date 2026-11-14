"""
Hand-built Silverpine South (160x160): the southern pine woods, Pyrewood and the Gilnean border, levels 15-20.

Laid out on the REAL Silverpine Forest map (north is up; the Great Sea is the west coast, Lordamere Lake the east):
    N    the road down from the Forsaken Rear Guard comes in at the top (80,5)
    NW   BUCKLEBREE FARM (38,32): a plague-ruined farm; OLIVIA'S POND (30,62) below it, a stagnant marsh
    W    DEEP ELEM MINE (22,98): a collapsed kobold mine in the western rock; the sea bites into the SW rim
    C    VALGAN'S FIELD (82,52): the Forsaken forward camp on a battle-scarred farm
    E    THE DECREPIT FERRY (146,44): a timber pier into Lordamere (portal -> Fenris Isle); AMBERMILL (122,78): the Dalaran
         lumber village with the waygate to Ambermill Tower (138,90)
    C/S  PYREWOOD VILLAGE (88,100): the burnt Gilnean-style village, worgen and cultists
    SW   BERARD'S TALON (46,126) and SHADOWFANG KEEP (48,144): the keep's portcullis gate under the ridge
    S/SE BEREN'S PERIL (96,126) worgen hills, then the GREYMANE WALL along the south rim (the Gilnean gate stands shut)

AREA ARCHETYPE: OPEN FARM-AND-FOREST COUNTRY with four set-pieces: a marsh pond, a timber pier, a ridge with a castle gate and the
long ruined wall.  The trunk road branches seven ways; pine groves separate the districts.

HARD CONTRACTS (world/portal_manager.py)
  portals  Silverpine North <- (80,5)   Shadowfang Keep (48,144)   Ambermill Tower (138,90)   Fenris Isle ferry (151,44)
           Western Hillsbrad (138,155) - the south-east pass out of Lordaeron, added with the Hillsbrad cluster
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob, lobe, superlobe, water_body, rock_spurs

KEY = "silverpine_south"
NAME = "Silverpine South"
DESC = "The southern pine woods: farms gone to blight, worgen villages and the shut Gilnean wall."
REGION = "Eastern Kingdoms - Lordaeron"
W, H = 160, 160
BAKED_DIR = "assets/tiles/silverpine_south/baked"
IS_TOWN = False
BASE_TILE = "grass"
SEED = 83

PORTALS = {(80, 5): "Silverpine North", (48, 144): "Shadowfang Keep", (138, 90): "Ambermill Tower", (151, 44): "Fenris Isle",
           (138, 155): "Western Hillsbrad"}
ARRIVALS = [(80, 9), (48, 145), (138, 91), (149, 44), (138, 151)]
START = (80, 22)

ROADS = {
    "trunk":      ([(80, 5), (80, 24), (79, 44), (82, 64), (84, 84), (88, 100)], 3.4),
    "farm":       ([(80, 24), (64, 27), (46, 32), (34, 36)], 2.6),
    "pond":       ([(79, 46), (62, 54), (44, 60), (34, 64)], 2.4),
    "mine":       ([(44, 62), (38, 76), (30, 90), (24, 100)], 2.4),
    "ferry":      ([(82, 30), (100, 31), (120, 35), (136, 40), (146, 44)], 2.6),
    "ambermill":  ([(83, 66), (100, 70), (116, 76), (128, 84), (138, 91)], 2.6),
    "shadowfang": ([(86, 102), (72, 114), (62, 126), (54, 138), (48, 145)], 2.8),
    "peril":      ([(90, 104), (98, 118), (106, 130), (116, 144)], 2.4),
    "wall":       ([(116, 144), (130, 148)], 2.4),
    # on into Hillsbrad: the pass out of Lordaeron's south-east corner
    "hillsbrad":  ([(130, 148), (136, 152), (138, 156)], 2.6),
}
_RS = K.RoadSet(ROADS)
road_dist = _RS.dist

# the ferry pier laid over the lake: (x0, x1, y0, y1)
DECKS = [(141.0, 153.0, 42.8, 45.2)]


def paved(gx, gy):
    """Worn stone under Valgan's camp yard, Pyrewood's green and the keep's forecourt."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    camp = lobe(gx, gy, 74.0, 50.0, 8.0, 6.0) + 0.5 * wob(gx, gy)
    green = lobe(gx, gy, 88.0, 98.0, 7.0, 5.0) + 0.5 * wob(gx, gy)
    keep = lobe(gx, gy, 49.0, 148.0, 7.0, 4.0) + 0.5 * wob(gx, gy)
    mill = lobe(gx, gy, 120.0, 80.0, 6.0, 4.5) + 0.5 * wob(gx, gy)
    return np.maximum.reduce([camp, green, keep, mill]) - 1.2


# ---- water -----------------------------------------------------------------------------------------------------
POOLS = [(31.0, 62.0, 7.0, 4.8, 0.3), (104.0, 94.0, 4.8, 3.4, -0.2)]
LAKE = (178.0, 66.0, 33.0, 50.0)                      # Lordamere, off the east rim
BAY = (-8.0, 130.0, 20.0, 30.0)                       # the sea bay in the SW rim


def sea_field(gx, gy):
    return water_body(gx, gy, *BAY)


def lake_field(gx, gy):
    return water_body(gx, gy, *LAKE)


def pool_field(gx, gy):
    p = np.full(np.shape(gx), -99.0)
    for (cx, cy, rx, ry, rot) in POOLS:
        p = np.maximum(p, water_body(gx, gy, cx, cy, rx, ry, rot))
    return p


def water_field(gx, gy):
    return np.maximum.reduce([sea_field(gx, gy), lake_field(gx, gy), pool_field(gx, gy)])


def deck_field(gx, gy):
    d = np.full(np.shape(gx), -9.0)
    for (x0, x1, y0, y1) in DECKS:
        d = np.maximum(d, np.minimum.reduce([gx - x0, x1 - gx, gy - y0, y1 - gy]))
    return d


# ---- rock ------------------------------------------------------------------------------------------------------
SPURS = [
    (0, 74, 16, 80, 2.6),          # the western rock over Deep Elem
    (0, 108, 14, 106, 2.4),
    (24, 134, 62, 134, 2.8),       # the ridge behind Shadowfang's gate
    (160, 118, 134, 112, 2.8),     # the east shoulder under Ambermill
    (118, 86, 152, 86, 2.4),       # the cliff behind the waygate
    (60, 160, 160, 160, 3.2),      # the Greymane Wall's rock
    (100, 0, 96, 12, 2.4),
]
OUTCROPS = [
    (62, 40, 2.4, 2.0), (96, 56, 2.4, 2.0), (60, 80, 2.6, 2.0), (106, 106, 2.4, 2.0), (126, 124, 2.8, 2.2),
    (110, 138, 2.4, 2.0), (36, 120, 2.6, 2.0), (70, 124, 2.4, 2.0), (20, 24, 2.6, 2.0), (124, 24, 2.4, 2.0),
    (146, 104, 2.6, 2.0), (28, 150, 2.4, 2.0),
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
    deep = np.maximum.reduce([sea_field(gx, gy) - 2.8, lake_field(gx, gy) - 2.8, pool_field(gx, gy) - 2.2])
    return dict(cliff=cliff_field(gx, gy), shallow=w, deep=deep, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


# ---- subzones (x, y, w, h[, display]) ---------------------------------------------------------------------------
SUBZONES = [
    ("Bucklebree Farm", 18, 18, 44, 34),
    ("Olivia's Pond", 12, 52, 40, 28),
    ("Deep Elem Mine", 10, 80, 36, 32),
    ("Valgan's Field", 62, 36, 42, 34),
    ("The Decrepit Ferry", 104, 22, 52, 36),
    ("Ambermill", 104, 58, 52, 40),
    ("Pyrewood Village", 64, 76, 40, 36),
    ("Berard's Talon", 24, 112, 46, 36),
    ("Beren's Peril", 72, 112, 60, 30),
    ("The Greymane Wall", 72, 142, 88, 16),
]

# ---- baker config (read by tools/bake_silverpine.py) -------------------------------------------------------------
BASE = {"pine": 0.50, "fern": 0.30, "mulch": 0.26, "rocky": 0.14}
PAINT = {
    "grass":  [(80, 16, 12, 8, 1.0), (40, 34, 14, 10, 1.0), (82, 50, 16, 10, 0.9), (122, 78, 12, 8, 0.9), (88, 98, 10, 7, 0.8)],
    "field":  [(40, 40, 12, 7, 1.0), (30, 28, 8, 5, 0.9), (84, 58, 14, 7, 1.0), (92, 46, 10, 5, 0.9)],
    "meadow": [(100, 33, 12, 6, 0.8), (60, 44, 8, 5, 0.6), (110, 126, 10, 6, 0.6)],
    "earth":  [(74, 50, 7, 5, 0.9), (96, 56, 6, 4, 0.7)],
    "cursed": [(36, 34, 8, 5, 0.6), (88, 100, 8, 5, 0.6), (70, 50, 6, 4, 0.5)],
    "bog":    [(31, 62, 12, 8, 1.0), (24, 72, 10, 6, 0.9), (104, 94, 8, 5, 0.8), (40, 56, 8, 5, 0.7), (146, 38, 6, 4, 0.5)],
    "den":    [(98, 124, 12, 8, 1.0), (112, 134, 10, 6, 0.9)],
    "web":    [(46, 124, 6, 5, 0.5)],
    "rocky":  [(24, 100, 8, 6, 0.7), (50, 138, 12, 6, 0.6), (140, 90, 10, 5, 0.6), (118, 152, 20, 5, 0.6)],
    "gravel": [(24, 100, 7, 5, 0.7), (80, 12, 9, 5, 0.5)],
    "shore":  [(143, 44, 6, 6, 0.5)],
}
COBBLE = [(74, 50, 8, 6, 0.9), (88, 98, 7, 5, 0.9), (49, 148, 7, 4, 0.9), (120, 80, 6, 4.5, 0.9)]

# ---- NPC spots ----------------------------------------------------------------------------------------------------
NPC_POSITIONS = {
    "sp_talon_trapper": (81, 43),             # the March: Trapper Hask, the hill
    "sp_wall_corporal": (66, 49),             # the March: Corporal Teague, the Greymane Wall
    "sp_pond_marshwalker": (75, 55),          # the March: Marshwalker Thorne, Olivia's Pond
    "sp_peril_packbreaker": (75, 41),         # the March: Packbreaker Rynn, the Peril
    "sp_amber_millwright": (70, 44),          # the March: Millwright Haskell, Ambermill
    "sp_amber_magister": (81, 48),            # the March: Magister Orsolo, Ambermill
    "sp_sfk_gatekeeper": (74, 45),            # the March: Gatekeeper Marl, Shadowfang Keep
    "sp_south_gate_scout": (82, 12),
    "sp_south_hunter": (77, 38),
    "sp_buckle_farmer": (39, 33),
    "sp_buckle_goodwife": (34, 31),
    "sp_elem_foreman": (27, 99),
    "sp_south_march_sergeant": (70, 48),      # Sergeant Dallow
    "sp_valgan_surgeon": (77, 53),
    "sp_south_quartermaster": (72, 53),       # vendor
    "sp_pyre_hearthwarden": (84, 95),
    "sp_ferryman": (143, 41),
    "sp_ferry_dockhand": (137, 44),
}
CHESTS = [(22, 46), (110, 100), (136, 62), (28, 128), (96, 138)]

FOREST = dict(seed=47, count=140, rim=26, thorn=14, names=[
    ("ek_pine_tall", 9, 0.28), ("ek_pine_tall", 8, 0.28), ("ek_pine_trio", 7, 0.32), ("ek_pine_trio", 7, 0.32),
    (T.HFP + "dead_pine_cluster.png", 5, 0.40), ("ek_dead_oak", 6, 0.34)])

PINES = [("ek_pine_tall", 9, 0.28), ("ek_pine_tall", 8, 0.28), ("ek_pine_trio", 7, 0.32), ("ek_pine_trio", 7, 0.32)]
DEADS = [(T.HFP + "dead_pine_cluster.png", 5, 0.4), ("ek_dead_oak", 6, 0.34)]


def dress(L):
    p, b = L.prop, L.bld
    HF, CI, UF = T.HFP, T.CIP, T.UFP
    ENT, CO, RU = T.ENT, "assets/tiles/coastal_props/", "assets/tiles/ruins/"
    # ---- the road in from the Rear Guard
    p("ek_forsaken_banner", 76, 8, 5)
    p("ek_forsaken_banner", 84, 8, 5)
    p("ek_signpost", 84, 14, 4)
    p("ek_ruin_wall", 70, 10, 4)
    p("ek_ruin_wall", 92, 10, 4)
    # ---- Bucklebree Farm: a plague-ruined farm
    b("forsaken_house_small", 40, 28, 8, nudge=2)
    p(HF + "burned_house_ruin.png", 30, 26, 7)
    p("ek_farm_well", 46, 34, 4)
    p("ek_farm_cart", 34, 38, 4)
    for x in (26, 32, 38, 44, 50):
        p("ek_farm_fence", x, 46, 3, solid=True)
    for (x, y) in [(28, 32), (50, 28), (44, 42), (36, 42)]:
        p("ek_haystack", x, y, 4)
    p("ek_scarecrow", 42, 38, 4)
    p("ek_scarecrow", 52, 36, 4)
    p("ek_signpost", 62, 32, 4)
    p("ek_toadstools", 24, 36, 2, solid=False)
    T.grove(L, 24, 24, 8, 6, 6, DEADS, seed=3)
    # ---- Olivia's Pond: a marsh with a rotting rowboat and willows
    for (x, y) in [(22, 58), (26, 68), (38, 66), (40, 58), (24, 62), (36, 70)]:
        p(HF + "bog_reeds_cluster.png", x, y, 3, solid=False, shore_ok=True)
    p("ek_willow", 20, 54, 7)
    p("ek_willow", 44, 68, 7)
    p(CO + "rowboat_wreck.png", 28, 66, 3, shore_ok=True)
    p("ek_toadstools", 42, 60, 2, solid=False)
    p("ek_open_grave", 46, 56, 3)
    p("ek_signpost", 52, 58, 4)
    # ---- Deep Elem Mine: a collapsed kobold dig in the western rock
    p(ENT + "ent_collapsed_mine.png", 18, 96, 7, solid=True, nudge=0)
    p("ek_plague_cart", 28, 96, 4)
    p("ek_ruin_wall", 18, 100, 4)
    p("ek_signpost", 32, 92, 4)
    p("ek_gibbet", 20, 106, 6)
    for (x, y) in [(30, 104), (26, 108)]:
        p(HF + "dead_pine_cluster.png", x, y, 5)
    # ---- Valgan's Field: the Forsaken forward camp on a ruined farm
    b("forsaken_house_medium", 66, 44, 9, nudge=2)                # the field HQ
    b("forsaken_house_small", 87, 44, 8, nudge=2)
    p(HF + "burned_house_ruin.png", 96, 60, 7)
    p("ek_forsaken_banner", 64, 52, 5)
    p("ek_forsaken_banner", 78, 56, 5)
    p("ek_plague_cauldron", 74, 56, 3)
    p("ek_plague_cart", 68, 58, 4)
    p("ek_gibbet", 88, 42, 6)
    p("ek_pillory", 84, 50, 4)
    for (x, y) in [(92, 50), (100, 46), (90, 62), (102, 62)]:
        p("ek_scarecrow", x, y, 4)
    for (x, y) in [(94, 54), (98, 64), (86, 66)]:
        p("ek_haystack", x, y, 4)
    for x in (84, 90, 96, 102):
        p("ek_farm_fence", x, 40, 3, solid=True)
    p("ek_open_grave", 100, 54, 3)
    p("ek_signpost", 76, 36, 4)
    # ---- The Decrepit Ferry: a pier into Lordamere
    b("forsaken_house_small", 134, 38, 8, nudge=2)                # the ferryman's shack
    p(CO + "mooring_posts.png", 148, 41, 3, road_ok=True, shore_ok=True, allow_overlap=True, nudge=0)
    p(CO + "mooring_posts.png", 148, 47, 3, road_ok=True, shore_ok=True, allow_overlap=True, nudge=0)
    p(CO + "dock_lantern_post.png", 146, 41, 4, road_ok=True, shore_ok=True, allow_overlap=True, nudge=0)
    p(CO + "dock_lantern_post.png", 146, 47, 4, road_ok=True, shore_ok=True, allow_overlap=True, nudge=0)
    p(CO + "fish_crates_traps.png", 138, 47, 4)
    p(CO + "rowboat_wreck.png", 130, 48, 3, shore_ok=True)
    p("ek_signpost", 126, 36, 4)
    p("ek_ruin_wall", 128, 30, 4)
    p("ek_willow", 134, 52, 7)
    # ---- Ambermill: Dalaran's lumber village and the waygate
    b("forsaken_house_small", 114, 72, 8, nudge=2)
    b("forsaken_house_medium", 128, 74, 9, nudge=2)
    p(HF + "burned_house_ruin.png", 108, 82, 7)
    p("ek_farm_well", 120, 76, 4)
    p("ek_farm_cart", 112, 84, 4)
    p("ek_haystack", 126, 82, 4)
    p("ek_forsaken_banner", 118, 88, 5)
    p("ek_signpost", 100, 68, 4)
    L.cave(138, 90, "ent_runed_waygate", 7, 6)                    # the waygate over the portal
    p(RU + "ruin_stone_ring.png", 128, 92, 4, solid=False)
    # ---- Pyrewood Village: burnt, Gilnean-style cottages and a ruined hall
    b("forsaken_house_medium", 78, 90, 9, nudge=2)
    b("forsaken_house_small", 96, 90, 8, nudge=2)
    b("forsaken_house_medium", 100, 106, 9, nudge=2)
    p(HF + "burned_house_ruin.png", 74, 104, 7)
    p(HF + "burned_house_ruin.png", 70, 92, 7)
    b("forsaken_town_hall", 88, 84, 10, nudge=1)                  # Pyrewood Hall
    p("ek_farm_well", 86, 102, 4)
    p("ek_dry_fountain", 90, 98, 5)
    for x in (72, 78, 94, 100):
        p("ek_farm_fence", x, 80, 3, solid=True)
    p("ek_gibbet", 82, 108, 6)
    p("ek_cross_crows", 96, 100, 4)
    p("ek_open_grave", 74, 98, 3)
    p("ek_signpost", 86, 76, 4)
    T.grove(L, 66, 100, 4, 8, 6, DEADS, seed=6)
    # ---- Berard's Talon + Shadowfang Keep's gate under the ridge
    L.cave(48, 144, "ent_castle_portcullis", 11, 8)               # the keep's gate over the portal
    p("ek_forsaken_banner", 41, 143, 5)
    p("ek_forsaken_banner", 56, 143, 5)
    p("ek_ruin_wall", 38, 140, 4)
    p("ek_ruin_wall", 60, 140, 4)
    p("ek_cemetery_fence", 40, 150, 3, solid=True)
    p("ek_cemetery_fence", 58, 150, 3, solid=True)
    p("ek_gibbet", 62, 146, 6)
    p(RU + "ruin_wall_arch.png", 44, 118, 6)
    p(RU + "ruin_stone_ring.png", 52, 122, 4, solid=False)
    p("ek_grave_hand", 40, 126, 3)
    p("ek_signpost", 66, 120, 4)
    p("ek_web_boulder", 36, 128, 4)
    # ---- Beren's Peril: worgen hills
    for (x, y) in [(92, 122), (104, 126), (112, 120), (98, 134), (118, 130), (88, 130)]:
        p(HF + "dead_pine_cluster.png", x, y, 5)
    p("ek_grave_hand", 100, 128, 3)
    p("ek_toadstools", 108, 122, 2, solid=False)
    p(HF + "twisted_root_arch.png", 112, 126, 6)
    p("ek_signpost", 92, 118, 4)
    p("ek_open_grave", 94, 128, 3)
    # ---- the Greymane Wall: a ruined wall with the Gilnean gate shut
    p(RU + "ruin_archway.png", 126, 150, 8, solid=True, nudge=0, road_ok=True, allow_overlap=True)
    for x in (80, 90, 100, 110, 120, 138, 146, 154):
        p(RU + "ruin_wall_arch.png", x, 152, 6)
    p("ek_forsaken_banner", 112, 142, 5)
    p("ek_forsaken_banner", 118, 142, 5)
    p("ek_plague_cart", 108, 146, 4)
    p("ek_signpost", 122, 144, 4)
    # ---- the trunk road
    p("ek_signpost", 82, 62, 4)
    p("ek_forsaken_banner", 86, 72, 5)
    p("ek_ruin_wall", 74, 70, 4)
    # ---- pine groves that wall the districts from one another
    T.grove(L, 60, 28, 8, 5, 8, PINES, seed=11)
    T.grove(L, 100, 14, 12, 7, 10, PINES, seed=12)
    T.grove(L, 54, 72, 8, 5, 8, PINES, seed=13)
    T.grove(L, 112, 56, 8, 4, 6, PINES, seed=14)
    T.grove(L, 68, 66, 6, 4, 6, PINES, seed=15)
    T.grove(L, 56, 106, 10, 5, 8, PINES, seed=16)
    T.grove(L, 124, 108, 14, 7, 12, PINES, seed=17)
    T.grove(L, 80, 140, 12, 5, 10, PINES, seed=18)
    T.grove(L, 28, 114, 8, 5, 8, PINES + DEADS, seed=19)
    T.grove(L, 12, 40, 5, 8, 8, PINES, seed=20)
    T.grove(L, 138, 20, 12, 6, 10, PINES, seed=21)
    T.grove(L, 70, 18, 6, 6, 6, PINES, seed=22)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_silverpine_south():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/sps_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
