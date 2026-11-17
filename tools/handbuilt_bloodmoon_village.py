"""
Hand-built Bloodmoon Village (46x36): the one roofed ground on Fenris Isle, levels 17-22.

Kyle, 17 Nov 2026, on the quest-hub pass ("NPCs for quests are placed RIGHT at that subzone, this is... lame"): "Did you
want to make Bloodmoon village into a tiny hub? Actual map - but small and seperate". Until today the village was a
handful of huts on the isle's southern shore and only two of the isle's six quest-givers stood in it; the altar warden,
the keep scout and the grave hunter stood at the places they send you. Now the village is its own small map and all
of them stand in it, so a quest sends you out across the isle and you come back here to hand it in.

TOWN ARCHETYPE: THE HELD VILLAGE.  A cursed hamlet that has not been abandoned because the people in it have nowhere
else to go.  One lane in from the south gate to a well in the square; the elder's lodge to the north-west, a few
houses and huts round the square, a gibbet nobody has taken down, and a scrap of graveyard at the east end.  Dead
forest closes the edges, so it encloses without a wall sprite.

    north: the elder's lodge, the watch corner
    square: the well, Huntsman Corwell
    south gate (23,35) -> Fenris Isle (58,104), the lane off the island road between the pier and the manor

HARD CONTRACTS (world/portal_manager.py): portal (23,35) <-> Fenris Isle (58,104).  Arrivals land two tiles north of
the destination tile, so you come in at (23,33) on the lane and go out at (58,102) past the isle's gatehouse.
The gatehouse stands across the lane a few tiles in from each door: a decor building may not stand within two tiles
of a door or an arrival, nor be drawn over a door (tools/handbuilt_central_barrens.Layout._try).
NPC ids are the ones already in data/npcs/*.json - this module MOVES them, it does not invent any.
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob

KEY = "bloodmoon_village"
NAME = "Bloodmoon Village"
DESC = "Bloodmoon Village. The one roofed ground on Fenris Isle, held by people who have nowhere else to go."
REGION = "Eastern Kingdoms - Lordaeron"
W, H = 46, 36
BAKED_DIR = "assets/tiles/bloodmoon_village/baked"
IS_TOWN = True
BASE_TILE = "grass"
SEED = 98

PORTALS = {(23, 35): "Fenris Isle"}
ARRIVALS = [(23, 33)]
START = (23, 28)

ROADS = {
    "lane": ([(23, 35), (23, 27), (23, 19)], 3.0),          # in from the south gate to the square
    "west": ([(21, 17), (14, 14), (10, 12)], 2.2),          # up to the elder's lodge
    "east": ([(26, 18), (33, 20), (38, 23)], 2.2),          # out to the graves
}
PLAZA = (23, 17, 7.0, 5.0)           # the square round the well
DECKS = []

_RS = K.RoadSet(ROADS)
road_dist = _RS.dist


def paved(gx, gy):
    cx, cy, rx, ry = PLAZA
    r = np.sqrt(((np.asarray(gx, float) - cx) / rx) ** 2 + ((np.asarray(gy, float) - cy) / ry) ** 2)
    return (1 - r) * min(rx, ry)


def deck_field(gx, gy):
    return np.full(np.shape(gx), -9.0)


def cliff_field(gx, gy):
    """The dead-forest rim all round, and the one gap in it: the south gate, carved after the rim is forced."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    edge = np.minimum.reduce([gx, W - gx, gy, H - gy])
    rock = (3.4 + 1.2 * wob(gx * 0.6, gy * 0.6)) - edge
    gate = (np.abs(gx - 23.0) < 2.6) & (gy > H - 8)
    rock = np.where(gate, np.minimum(rock, -1.0), rock)
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    return rock


def fields(gx, gy):
    gx = np.asarray(gx, float)
    none = np.full(gx.shape, -99.0)
    return dict(cliff=cliff_field(gx, gy), shallow=none, deep=none, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


SUBZONES = [
    ("Bloodmoon Village", 2, 2, 42, 32),
]

# ---- baker config (read by tools/bake_silverpine.py; the same ground as Fenris Isle outside the gate) -------------
BASE = {"mulch": 0.34, "fern": 0.16, "grass": 0.30, "rocky": 0.20}
PAINT = {
    "earth":  [(23, 26, 4, 7, 0.8), (36, 24, 5, 4, 0.7)],
    "cursed": [(38, 25, 5, 4, 0.8)],
    "gravel": [(23, 17, 6, 4, 0.6)],
    "grass":  [(12, 24, 6, 5, 0.7), (32, 10, 6, 4, 0.6)],
}
COBBLE = [(23, 17, 7, 5, 0.9)]

# ---- NPC spots ---------------------------------------------------------------------------------------------------
# One per thing the village does. The three who used to stand out at the altar, the keep and the grave stand here
# now and send you out to them.
NPC_POSITIONS = {
    "bloodmoon_elder":      (13, 15),    # Elder Gravemoss, at the door of the lodge
    "fenris_village_elder": (26, 15),    # Huntsman Corwell, by the well
    "fenris_provisioner":   (30, 22),    # vendor, at the stores
    "fenris_altar_warden":  (9, 21),     # Warden Orlan, the west corner, facing the altar's ridge
    "fenris_keep_scout":    (33, 11),    # Scout Merrin, the north corner, facing the manor
    "fenris_grave_hunter":  (37, 20),    # Gravehunter Selke, the east end, by the village's own graves
}
CHESTS = []

DEADS = [(T.HFP + "dead_pine_cluster.png", 5, 0.4), ("ek_dead_oak", 6, 0.34),
         (T.CIP + "cursed_dead_tree_cluster.png", 6, 0.4)]
FOREST = dict(seed=71, count=10, rim=2, thorn=8, names=DEADS)


def dress(L):
    p, b = L.prop, L.bld
    CI = T.CIP
    # ---- the gate and the lane in
    b("ek_ruined_gatehouse", 23, 30, 9, solid=False, road_ok=True, nudge=0)
    p("ek_forsaken_banner", 19, 26, 5)
    p("ek_forsaken_banner", 27, 26, 5)
    p("ek_signpost", 26, 24, 4)
    # ---- the square
    p("ek_farm_well", 20, 18, 4)
    p("ek_farm_cart", 28, 26, 4)
    # ---- the elder's lodge and the houses
    b("forsaken_house_medium", 11, 10, 9, nudge=2)
    b("forsaken_house_small", 31, 8, 8, nudge=2)
    p(CI + "cursed_village_hut.png", 7, 26, 6)
    p(CI + "cursed_village_hut.png", 15, 28, 6)
    p(CI + "cursed_village_hut.png", 33, 27, 6)
    p("ek_haystack", 11, 22, 4)
    # ---- the stores
    p("ek_scarlet_crates", 32, 23, 3)
    # ---- the east end: a gibbet nobody has taken down, and the village's own graves
    p("ek_gibbet", 40, 15, 6)
    p(CI + "worn_tombstone_row.png", 39, 26, 4)
    p("ek_open_grave", 41, 22, 3)
    p("ek_cross_crows", 36, 30, 4)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_bloodmoon_village():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/bloodmoon_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
