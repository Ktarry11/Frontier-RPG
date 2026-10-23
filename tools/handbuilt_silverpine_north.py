"""
Hand-built Silverpine North (160x160): the pine woods south of the Tirisfal border, levels 12-17.

Laid out on the REAL Silverpine Forest map (north is up; the Great Sea is the west coast, Lordamere Lake the east):
    N    the FORSAKEN REAR GUARD (80,16) - the palisade camp just inside the border; the Tirisfal road comes in at the top (80,5)
    NW   OLSEN'S FARTHING (40,30): a dead farm in a pine-ringed clearing
    W    RAVEN HILL CEMETERY (36,62) on its rise above the sea cliffs; the sea bay bites into the west rim
    W/SW THE SEPULCHER (34,98): the Forsaken crypt-keep and town; the gate (portal) is on this side. MALDEN'S ORCHARD (44,126) below it
    E    THE DEAD FIELD (112,52): blighted farmland, scarecrows and the bones of the harvest
    E    THE SKITTERING DARK (140,84) in the east wall: the spider cave (Widow's Lair); the NE corner is a tip of Lordamere Lake
    SE   SHADOWSPRING POOLS (112,108): three teal spring-fed pools in a bog
    S    the trunk road runs on to Silverpine South at the bottom (80,156)

AREA ARCHETYPE: PINE WOODS.  Tirisfal's zones are lobes and ridges; this one is open forest floor with a trunk road, pine groves
that wall the clearings off from one another, a sea bay in the west rim and spring pools in the south-east.  Few cliffs; the
forest itself is the wall.

HARD CONTRACTS (world/portal_manager.py)
  portals  Eastern Tirisfal <- (80,5)   The Sepulcher (32,98)   Widow's Lair (150,84)   Silverpine South (80,156)
  NPC ids  referenced by data/quests/*.json; positions below are written back by tools/sync_silverpine_npcs.py
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob, lobe, superlobe, water_body, rock_spurs

KEY = "silverpine_north"
NAME = "Silverpine North"
DESC = "Cold pine woods south of Tirisfal. The Forsaken hold the north; worgen and spiders hold the rest."
REGION = "Eastern Kingdoms - Lordaeron"
W, H = 160, 160
BAKED_DIR = "assets/tiles/silverpine_north/baked"
IS_TOWN = False
BASE_TILE = "grass"
SEED = 71

PORTALS = {(80, 5): "Eastern Tirisfal", (32, 98): "The Sepulcher", (150, 84): "Widow's Lair", (80, 156): "Silverpine South"}
ARRIVALS = [(80, 9), (32, 100), (150, 85), (80, 152)]
START = (80, 22)

ROADS = {
    "trunk":       ([(80, 5), (80, 18), (78, 34), (76, 52), (72, 70), (70, 88), (72, 106), (76, 124), (80, 140), (80, 156)], 3.4),
    "olsen":       ([(78, 22), (64, 24), (50, 28), (40, 30)], 2.6),
    "raven":       ([(75, 58), (60, 60), (46, 62), (36, 62)], 2.6),
    "deadfield":   ([(78, 40), (94, 44), (110, 48), (124, 52)], 2.6),
    "sepulcher":   ([(71, 94), (58, 95), (46, 97), (32, 98)], 3.0),
    "skittering":  ([(72, 72), (92, 76), (112, 80), (130, 84), (150, 84)], 2.6),
    "shadowspring": ([(71, 106), (88, 107), (104, 109), (118, 112)], 2.4),
    "orchard":     ([(74, 120), (62, 123), (50, 125), (40, 126)], 2.4),
}
_RS = K.RoadSet(ROADS)
road_dist = _RS.dist


def paved(gx, gy):
    """Worn stone under the Rear Guard's yard and in front of the Sepulcher's gate."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    yard = lobe(gx, gy, 80.0, 16.0, 15.0, 9.0) + 0.5 * wob(gx, gy)
    gate = lobe(gx, gy, 36.0, 98.0, 7.0, 6.0) + 0.5 * wob(gx, gy)
    return np.maximum(yard, gate) - 1.2


# ---- water -----------------------------------------------------------------------------------------------------
POOLS = [(108.0, 100.0, 7.5, 5.0, 0.2), (123.0, 108.0, 6.0, 4.5, -0.3), (112.0, 119.0, 5.5, 4.0, 0.5)]
LAKE = (160.0, 22.0, 17.0, 20.0)                     # Lordamere's tip, off the NE corner
BAY = (-5.0, 88.0, 21.0, 46.0)                       # the sea bay in the west rim


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


# ---- rock ------------------------------------------------------------------------------------------------------
SPURS = [
    (0, 40, 18, 44, 2.6),         # the cliffs over the bay's north shore
    (0, 134, 20, 128, 2.6),       # and its south shore
    (160, 62, 136, 60, 2.8),      # the east ridge above the Dead Field
    (160, 112, 134, 114, 2.6),    # the east ridge below the spider road
    (106, 0, 102, 12, 2.4),       # a buttress at the border
    (150, 160, 148, 142, 2.4),
]
OUTCROPS = [
    (62, 44, 2.4, 2.0), (92, 62, 2.6, 2.0), (56, 76, 2.4, 2.0), (92, 92, 2.4, 2.0), (60, 108, 2.6, 2.0),
    (96, 134, 2.8, 2.2), (28, 76, 2.2, 1.8), (124, 28, 2.4, 2.0), (144, 100, 2.6, 2.0), (22, 150, 2.4, 2.0),
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
    return rock


def fields(gx, gy):
    gx = np.asarray(gx, float)
    w = water_field(gx, gy)
    deep = np.maximum.reduce([sea_field(gx, gy) - 2.8, lake_field(gx, gy) - 2.8, pool_field(gx, gy) - 2.2])
    return dict(cliff=cliff_field(gx, gy), shallow=w, deep=deep, deck=np.full(gx.shape, -9.0))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


# ---- subzones (x, y, w, h[, display]) ---------------------------------------------------------------------------
SUBZONES = [
    ("Forsaken Rear Guard", 58, 2, 44, 36),
    ("Olsen's Farthing", 20, 12, 46, 34),
    ("Raven Hill Cemetery", 16, 46, 46, 36),
    ("The Dead Field", 90, 34, 50, 38),
    ("The Sepulcher Grounds", 22, 84, 36, 30),
    ("Malden's Orchard", 16, 112, 52, 40),
    ("Shadowspring Pools", 90, 90, 50, 42),
    ("The Skittering Dark", 114, 72, 44, 28),
]

# ---- baker config (read by tools/bake_silverpine.py) -------------------------------------------------------------
BASE = {"pine": 0.55, "fern": 0.30, "mulch": 0.30, "rocky": 0.12}
PAINT = {
    "grass":   [(80, 18, 14, 9, 1.0), (40, 30, 14, 9, 1.0), (112, 52, 18, 10, 0.7), (46, 126, 12, 8, 0.8)],
    "field":   [(38, 30, 11, 6, 1.0), (108, 50, 18, 8, 1.0), (118, 58, 9, 5, 0.8)],
    "meadow":  [(98, 56, 10, 6, 0.8), (50, 126, 8, 5, 0.6)],
    "earth":   [(36, 64, 11, 8, 1.0)],
    "cursed":  [(110, 50, 8, 5, 0.6), (40, 126, 8, 5, 0.6), (30, 60, 5, 4, 0.5)],
    "bog":     [(108, 100, 16, 10, 1.0), (122, 110, 14, 9, 0.9), (112, 120, 12, 8, 0.8)],
    "web":     [(142, 84, 12, 12, 1.0)],
    "rocky":   [(146, 84, 8, 10, 0.6), (30, 82, 8, 5, 0.5)],
    "gravel":  [(80, 16, 10, 6, 0.6)],
}
COBBLE = [(80, 16, 13, 8, 0.9), (36, 98, 7, 6, 0.9)]

# ---- NPC spots ----------------------------------------------------------------------------------------------------
NPC_POSITIONS = {
    "sp_rg_captain": (84, 18),            # Captain of the Rear Guard
    "sp_rg_apothecary": (75, 15),
    "sp_rg_cleric": (86, 13),
    "sp_rg_quartermaster": (73, 21),      # vendor
    "sp_north_scout": (81, 34),           # on the trunk road
    "sp_farthing_gaffer": (44, 32),
    "sp_farthing_widow": (36, 27),
    "sp_north_cemetery_keeper": (42, 64),  # Keeper Oswin
    "sp_rh_acolyte": (36, 69),
    "sp_df_huntress": (110, 50),
    "sp_df_farmhand": (104, 57),
    "sp_sep_gatewarden": (39, 100),
    "sp_orchard_warden": (46, 127),
    "sp_north_pools_warden": (101, 104),  # Warden Yaelis
    "sp_sd_webhunter": (137, 87),
}
CHESTS = [(28, 44), (126, 66), (118, 126), (30, 138), (96, 18)]

FOREST = dict(seed=41, count=150, rim=26, thorn=14, names=[
    ("ek_pine_tall", 9, 0.28), ("ek_pine_tall", 8, 0.28), ("ek_pine_trio", 7, 0.32), ("ek_pine_trio", 7, 0.32),
    (T.HFP + "dead_pine_cluster.png", 5, 0.40), ("ek_dead_oak", 6, 0.34)])

PINES = [("ek_pine_tall", 9, 0.28), ("ek_pine_tall", 8, 0.28), ("ek_pine_trio", 7, 0.32), ("ek_pine_trio", 7, 0.32)]
DEADS = [(T.HFP + "dead_pine_cluster.png", 5, 0.4), ("ek_dead_oak", 6, 0.34)]


def dress(L):
    p, b = L.prop, L.bld
    UF, HF, CI = T.UFP, T.HFP, T.CIP
    # ---- the border gate and the Forsaken Rear Guard's palisade camp
    p("ek_cemetery_gate", 80, 9, 8, road_ok=True, allow_overlap=True, nudge=0)
    p("ek_forsaken_banner", 76, 8, 5)
    p("ek_forsaken_banner", 84, 8, 5)
    b("forsaken_house_small", 68, 14, 8, nudge=2)                 # the barracks
    b("forsaken_house_medium", 92, 13, 9, nudge=2)                # the captain's hall
    b("gallows_post", 62, 26, 7, nudge=2)
    p("ek_plague_cart", 90, 22, 4)
    p("ek_plague_cauldron", 74, 12, 3)                            # Apothecary Pell's pot
    p("ek_forsaken_banner", 78, 26, 5)
    p("ek_forsaken_banner", 82, 26, 5)
    p("ek_signpost", 84, 31, 4)
    for x in (68, 72, 88, 94):
        p("ek_farm_fence", x, 28, 3, solid=True)
    p("ek_ruin_wall", 62, 18, 4)
    p("ek_ruin_wall", 100, 18, 4)
    # ---- Olsen's Farthing: a dead farm in a clearing
    b("forsaken_house_small", 40, 24, 8, nudge=2)
    p(HF + "burned_house_ruin.png", 30, 30, 7)
    p("ek_farm_well", 46, 28, 4)
    p("ek_farm_cart", 34, 36, 4)
    for x in (30, 36, 42, 48):
        p("ek_farm_fence", x, 38, 3, solid=True)
    for (x, y) in [(32, 25), (48, 33), (42, 36)]:
        p("ek_haystack", x, y, 4)
    p("ek_scarecrow", 40, 32, 4)
    p("ek_scarecrow", 28, 34, 4)
    p("ek_signpost", 56, 26, 4)
    T.grove(L, 40, 30, 22, 14, 6, DEADS, seed=3)
    # ---- Raven Hill Cemetery: mausoleum, rows of stones, crows
    p(HF + "crypt_mausoleum.png", 36, 58, 9, fraction=0.5)
    for (x, y) in [(28, 62), (46, 62), (30, 70), (44, 70), (36, 74)]:
        p(CI + "worn_tombstone_row.png", x, y, 3)
    p("ek_angel_statue", 38, 66, 6)
    p("ek_open_grave", 32, 66, 3)
    p("ek_open_grave", 48, 66, 3)
    p("ek_cross_crows", 26, 66, 4)
    p("ek_cemetery_fence", 22, 66, 3, solid=True)
    p("ek_cemetery_fence", 52, 66, 3, solid=True)
    p("ek_cemetery_gate", 56, 62, 7, road_ok=True, allow_overlap=True, nudge=0)
    p("ek_grave_hand", 40, 72, 3)
    p("ek_willow", 22, 56, 7)
    p("ek_signpost", 62, 62, 4)
    # ---- the Sepulcher: the Forsaken crypt-keep above the sea bay (the town is the interior zone)
    L.cave(32, 98, "ent_iron_crypt_gate", 9, 7)                   # the gate over the portal
    b("crypt_chapel", 24, 92, 11, nudge=1)
    b("forsaken_town_hall", 43, 91, 11, nudge=1)
    p("ek_forsaken_banner", 27, 103, 5)
    p("ek_forsaken_banner", 38, 103, 5)
    p("ek_cemetery_fence", 22, 104, 3, solid=True)
    p("ek_cemetery_fence", 44, 104, 3, solid=True)
    p("ek_angel_statue", 32, 106, 6)
    p("ek_signpost", 56, 96, 4)
    p("ek_gibbet", 50, 100, 6)
    # ---- Malden's Orchard: a dead orchard behind a ruined house
    p(HF + "burned_house_ruin.png", 52, 122, 7)
    for (x, y) in [(36, 120), (44, 118), (52, 130), (60, 128), (40, 132), (48, 136), (58, 134)]:
        p("ek_dead_oak", x, y, 6)
    p("ek_farm_cart", 62, 120, 4)
    p("ek_farm_well", 58, 128, 4)
    p("ek_haystack", 44, 130, 4)
    p("ek_toadstools", 38, 126, 2, solid=False)
    # ---- the Dead Field: rows of blighted crop, scarecrows, a plague cart
    for (x, y) in [(100, 46), (106, 44), (116, 44), (122, 48), (104, 60), (118, 62)]:
        p("ek_scarecrow", x, y, 4)
    for (x, y) in [(98, 52), (126, 56), (112, 64)]:
        p("ek_haystack", x, y, 4)
    for x in (96, 102, 108, 118, 124, 130):
        p("ek_farm_fence", x, 40, 3, solid=True)
    p("ek_plague_cart", 130, 50, 4)
    p("ek_farm_well", 94, 54, 4)
    p(HF + "burned_house_ruin.png", 128, 60, 7)
    p("ek_signpost", 90, 44, 4)
    p("ek_gibbet", 120, 40, 6)
    # ---- Shadowspring Pools: reeds, toadstools, a willow, a spring shrine
    for (x, y) in [(100, 96), (112, 94), (118, 104), (128, 104), (116, 112), (108, 122), (118, 124)]:
        p(HF + "bog_reeds_cluster.png", x, y, 3, solid=False, shore_ok=True)
    p("ek_willow", 96, 112, 7)
    p("ek_willow", 130, 112, 7)
    p("ek_toadstools", 104, 112, 2, solid=False)
    p("ek_toadstools", 124, 98, 2, solid=False)
    p("ek_ruin_wall", 100, 114, 4)
    p("ek_signpost", 92, 108, 4)
    p(HF + "twisted_root_arch.png", 128, 122, 6)
    # ---- the Skittering Dark: webs, egg sacs, the spider cave in the east wall
    L.cave(150, 84, "ent_spider_lair", 8, 6)
    for (x, y) in [(138, 76), (144, 90), (134, 82), (146, 96), (140, 80)]:
        p("ek_web_boulder", x, y, 4)
    for (x, y) in [(142, 86), (136, 92), (146, 78)]:
        p("ek_egg_sacs", x, y, 4)
    p("ek_signpost", 126, 83, 4)
    # ---- the trunk road: lanterns of the dead
    p("ek_forsaken_banner", 76, 66, 5)
    p("ek_signpost", 75, 60, 4)
    p("ek_signpost", 79, 121, 4)
    p("ek_forsaken_banner", 84, 148, 5)
    p("ek_ruin_wall", 90, 152, 4)
    # ---- pine groves that wall the clearings from one another
    T.grove(L, 56, 44, 12, 7, 9, PINES, seed=11)
    T.grove(L, 98, 22, 14, 7, 10, PINES, seed=12)
    T.grove(L, 64, 80, 8, 10, 10, PINES, seed=13)
    T.grove(L, 92, 70, 8, 5, 6, PINES, seed=14)
    T.grove(L, 86, 118, 10, 8, 12, PINES, seed=15)
    T.grove(L, 30, 112, 9, 5, 8, PINES + DEADS, seed=16)
    T.grove(L, 134, 134, 12, 10, 14, PINES, seed=17)
    T.grove(L, 52, 144, 14, 7, 12, PINES, seed=18)
    T.grove(L, 112, 82, 8, 4, 7, DEADS, seed=19)
    T.grove(L, 20, 20, 9, 7, 10, PINES, seed=20)
    T.grove(L, 128, 26, 10, 8, 10, PINES, seed=21)
    T.grove(L, 70, 140, 8, 6, 8, PINES, seed=22)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_silverpine_north():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/spn_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
