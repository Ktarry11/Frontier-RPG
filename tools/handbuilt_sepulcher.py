"""
Hand-built The Sepulcher (88x72): the Forsaken crypt-keep above Silverpine's north-western pines.

TOWN ARCHETYPE: TERRACED CRYPT-KEEP.  One processional avenue climbs from the south gate through three stone terraces separated by
cliff bands - the lower court (inn, curio stalls, mortician), the middle terrace (apothecary, bone-carver, relic hall) and the
upper terrace where the Keep Hall and its mausoleums stand - with the Raven Hill graveyard terrace wing to the west and the
chapel yard to the east, both reached by short stair-lanes off the middle terrace.  (Brill is a high street strung along a road;
Crossroads a plus-shaped avenue town; this is a vertical keep: you climb into the dead.)

Same recipe as Brill (tools/town_kit.py + tools/tirisfal_kit.py); the baker is tools/bake_silverpine.py sepulcher.

HARD CONTRACTS (world/portal_manager.py)
  portal   Silverpine North <- (44,67)        North's (32,98) enters at (44,65) -> arrive (44,63)
  NPC ids  the sepulcher_* records in data/npcs/*.json (positions below are written by tools/build_silverpine_npcs.py)
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob, superlobe

KEY = "sepulcher"
NAME = "The Sepulcher"
DESC = "The Sepulcher. A Forsaken crypt-keep, terrace over terrace, built into the hills of north-western Silverpine."
REGION = "Eastern Kingdoms - Lordaeron"
W, H = 88, 72
BAKED_DIR = "assets/tiles/sepulcher/baked"
IS_TOWN = True
BASE_TILE = "grass"
SEED = 91

PORTALS = {(44, 67): "Silverpine North"}
ARRIVALS = [(44, 63)]
START = (44, 62)

ROADS = {
    "avenue": ([(44, 67), (44, 58), (45, 49), (44, 40), (44, 31), (44, 22), (44, 19)], 3.4),
    "lower":  ([(22, 56), (33, 57), (44, 57), (56, 56), (66, 56)], 2.4),
    "grave":  ([(30, 36), (22, 36), (15, 35)], 2.2),
    "chapel": ([(58, 36), (66, 35), (75, 34)], 2.2),
}
PLAZA = (44, 56, 10.0, 5.0)          # the lower court's flagged floor
KEEP = (44, 18, 12.0, 6.0)           # the upper terrace's flagstones

_RS = K.RoadSet(ROADS)
road_dist = _RS.dist


def paved(gx, gy):
    out = -9.0
    for cx, cy, rx, ry in (PLAZA, KEEP):
        r = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
        out = np.maximum(out, (1 - r) * min(rx, ry))
    return out


def cliff_field(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    floor = np.maximum.reduce([
        superlobe(gx, gy, 44.0, 56.0, 30.0, 9.0, 2.6),           # the lower court
        superlobe(gx, gy, 44.0, 36.0, 17.0, 7.0, 2.6),           # the middle terrace
        superlobe(gx, gy, 44.0, 16.0, 25.0, 8.0, 2.6),           # the upper terrace (Keep Hall)
        superlobe(gx, gy, 13.0, 33.0, 10.0, 10.0, 2.6),          # the graveyard wing
        superlobe(gx, gy, 75.0, 33.0, 9.0, 9.0, 2.6),            # the chapel yard
    ])
    floor = floor + 1.5 * wob(gx * 0.5, gy * 0.5) + 0.8 * wob(gx, gy)
    floor = np.maximum(floor, road_dist(gx, gy) + 2.4)
    rock = -floor
    edge = np.minimum.reduce([gx, W - gx, gy, H - gy])
    rock = np.maximum(rock, (3.5 - edge) * 1.2 + 0.3 * wob(gx * 1.3, gy * 1.3))
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    return rock


def fields(gx, gy):
    gx = np.asarray(gx, float)
    return dict(cliff=cliff_field(gx, gy), shallow=np.full(gx.shape, -99.0), deep=np.full(gx.shape, -99.0),
                deck=np.full(gx.shape, -9.0))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


SUBZONES = [
    ("The Lower Court", 14, 47, 60, 20),
    ("The Keep Hall", 20, 8, 48, 18),
    ("Raven Hill Terrace", 3, 23, 22, 22),
]

# ---- baker config (read by tools/bake_silverpine.py) ----------------------------------------------
BASE = {"pine": 0.3, "mulch": 0.3, "rocky": 0.25, "fern": 0.15}
PAINT = {
    "earth":  [(13, 33, 8, 7, 1.0)],                                       # the graveyard wing
    "gravel": [(13, 29, 4, 3, 0.5)],
    "cobble": [(44, 56, 11, 6, 1.0), (44, 18, 12, 6, 1.0), (75, 34, 6, 5, 0.9), (44, 36, 8, 4, 0.8)],
}
COBBLE = []

# ---- NPC spots ------------------------------------------------------------------------------------
NPC_POSITIONS = {
    "sepulcher_crypt_guard": (41, 63),         # Molsen, at the south gate
    "sepulcher_pilgrim": (48, 62),
    "sepulcher_innkeeper": (34, 58),           # Doss, at the Hollow Cask
    "sepulcher_mortician_supplier": (24, 58),
    "sepulcher_relic_dealer": (55, 58),        # Fenn's curio stall
    "sepulcher_hermit": (66, 58),
    "sepulcher_lost_soul": (17, 52),
    "sepulcher_reagent_seller": (38, 38),      # Wrenn, at the apothecary
    "sepulcher_bone_carver": (51, 38),
    "sepulcher_relic_hunter": (46, 33),
    "sepulcher_gravestone_reader": (15, 36),
    "sepulcher_mourner": (11, 31),
    "sepulcher_tomb_keeper": (74, 36),         # Ellowyn, in the chapel yard
    "sepulcher_commander": (44, 20),           # Commander Vane, before the Keep Hall
    "sepulcher_adjutant": (50, 20),
}
CHESTS = [(9, 37), (80, 30), (26, 14), (62, 14)]

FOREST = dict(seed=47, count=34, rim=8, thorn=10, names=[
    ("ek_dead_oak", 6, 0.34), (T.HFP + "dead_pine_cluster.png", 5, 0.40), (T.CIP + "cursed_dead_tree_cluster.png", 4, 0.40)])


def dress(L):
    p, b = L.prop, L.bld
    UF, HF, CI, UC = T.UFP, T.HFP, T.CIP, T.UCP
    # ---- the south gate
    p("ek_forsaken_banner", 38, 64, 5)
    p("ek_forsaken_banner", 50, 64, 5)
    p("ek_signpost", 47, 66, 4)
    # ---- the lower court: the inn, the stalls, the well
    b("forsaken_house_medium", 31, 52, 10, nudge=1)                       # the Hollow Cask
    p("ek_plague_cauldron", 35, 55, 3)
    p("ek_signpost", 38, 56, 4)
    b("forsaken_house_small", 24, 52, 8, nudge=1)                         # the mortician's
    p("ek_open_grave", 19, 59, 3)
    p(UC + "uc_stall_goods.png", 55, 54, 4)
    p(UC + "uc_stall_bottles.png", 61, 54, 4)
    p(UC + "uc_crate_stack.png", 64, 60, 3)
    p("ek_farm_well", 44, 52, 4)
    b("forsaken_house_small", 70, 53, 8, nudge=1)                         # the hermit's lean-to
    for x in (28, 40, 52, 62):
        p(UC + "uc_lantern_post.png", x, 61 if x % 8 == 4 else 55, 5, solid=False)
    # ---- the middle terrace: apothecary, bone-carver's and relic hall
    b("forsaken_house_small", 36, 35, 8, nudge=1)                         # the apothecary
    p(UC + "uc_alchemy_table.png", 40, 40, 3)
    p(UC + "uc_plague_vat.png", 31, 38, 4)
    b("forsaken_house_small", 55, 33, 8, nudge=1)                         # the bone-carver's
    p("ek_scarecrow", 57, 39, 4)
    p("ek_forsaken_banner", 41, 33, 5)
    p("ek_forsaken_banner", 48, 33, 5)
    # ---- the upper terrace: the Keep Hall and its crypts
    b("forsaken_town_hall", 44, 15, 12, solid="core", fraction=0.5, nudge=0)
    p("ek_forsaken_banner", 37, 16, 5)
    p("ek_forsaken_banner", 51, 16, 5)
    p("ek_gibbet", 62, 18, 6)
    p("ek_cross_crows", 28, 19, 4)
    p(HF + "crypt_mausoleum.png", 26, 12, 9, fraction=0.5)
    p(HF + "crypt_mausoleum.png", 62, 12, 9, fraction=0.5)
    p("ek_pillory", 40, 21, 4)
    # ---- the graveyard wing (Raven Hill terrace)
    p("ek_cemetery_gate", 22, 36, 5, road_ok=True, allow_overlap=True, nudge=0)
    for (x, y) in [(8, 28), (12, 27), (16, 29), (7, 34), (11, 38), (17, 40)]:
        p(CI + "worn_tombstone_row.png", x, y, 3)
    p("ek_open_grave", 14, 32, 3)
    p("ek_angel_statue", 10, 33, 6)
    p("ek_willow", 6, 38, 7)
    # ---- the chapel yard
    b("crypt_chapel", 76, 28, 10, nudge=1)
    p(CI + "worn_tombstone_row.png", 70, 36, 3)
    p(CI + "worn_tombstone_row.png", 80, 36, 3)
    p("ek_cross_crows", 71, 29, 4)
    p("ek_signpost", 66, 37, 4)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_the_sepulcher():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/sepulcher_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
