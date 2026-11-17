"""
Hand-built Southshore (96x80): the Alliance's harbour town on Hillsbrad's south coast, levels 22-26.

Kyle, 17 Nov 2026: "lets just make southshore an actual town at this point." It was five buildings and nine people
standing on the open coast of Western Hillsbrad, inside the same field the marines patrol. Now it's a map of its own,
the way every town in the game is, with its people inside and the gate on the trunk road.

THE TOWN'S STANCE IS UNCHANGED (backlog [72]). This is a human town and the player is Horde. Nobody here starts a
fight on their own street, but nobody here likes you either: there's no bed, no flight and no trainer for you. The
innkeeper sells food through the window and that's as far as it goes. The marines and the militia you fight are
out on the approaches in Western Hillsbrad, where they always were.

TOWN ARCHETYPE: THE HARBOUR STREET.  One street runs straight down from the north gate, across the square, to the
strand and out along the quay to where the ship ties up. The town hangs off it: the chapel and the farm plots to the
west, the inn and the militia hall to the east, the fishers along the beach. Hedged farmland closes the sides and
the sea closes the south.

    north gate (48,1) <- Western Hillsbrad (94,127), the end of the trunk road through the fields
      |
    the high street, the square and the well, Captain Callard
      west: the townhouse, the chapel (Brother Venn), Holloway's plots
      east: the inn (Beatrix Rowe sells through the window), the militia hall
      |
    the strand: the boathouse, the fishery, Rose's nets, the watchtower
      |
    the quay, out to the T-head and the ship (Dockmaster Pryce)

HARD CONTRACTS (world/portal_manager.py): portal (48,1) <-> Western Hillsbrad (94,127). Arrivals land two tiles
north of the destination tile: you come in at (48,8) under the gatehouse and go out at (94,125) on the trunk road.
NPC ids are the hbw_ss_* people already in data/npcs/*.json; tools/sync_hillsbrad_npcs.py moves them here.
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob

KEY = "southshore"
NAME = "Southshore"
DESC = "Southshore. The Alliance's harbour town on Hillsbrad's south coast: one street down to the quay, and not a "\
       "friendly face on it."
REGION = "Eastern Kingdoms - Lordaeron"
W, H = 96, 80
BAKED_DIR = "assets/tiles/southshore/baked"
IS_TOWN = True
BASE_TILE = "grass"
SEED = 131

PORTALS = {(48, 1): "Western Hillsbrad"}
ARRIVALS = [(48, 8)]
START = (48, 12)

ROADS = {
    # the high street: gate, square, strand, quay foot
    "high":   ([(48, 1), (48, 12), (48, 30), (48, 53)], 3.2),
    # the cross row through the square, west to the plots and east to the militia hall
    "row":    ([(12, 31), (30, 31), (48, 30), (66, 31), (84, 29)], 2.6),
    # up to the chapel
    "chapel": ([(30, 31), (24, 23), (21, 19)], 2.2),
    # along the strand above the tide line
    "strand": ([(16, 52), (32, 53), (48, 52), (64, 53), (82, 52)], 2.4),
}
PLAZA = (48, 31, 8.0, 5.5)           # the square round the well
QUAY_YARD = (48, 51, 7.0, 2.6)       # worn stone at the foot of the quay

#: the quay: (x0, x1, y0, y1) plank decks over the water, the long pier and its T-head
DECKS = [(45.6, 50.4, 52.0, 70.0),
         (38.0, 58.0, 66.0, 70.6)]

_RS = K.RoadSet(ROADS)
road_dist = _RS.dist


def paved(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    out = np.full(gx.shape, -9.0)
    for cx, cy, rx, ry in (PLAZA, QUAY_YARD):
        r = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
        out = np.maximum(out, (1 - r) * min(rx, ry))
    return out


def shore_y(gx):
    gx = np.asarray(gx, float)
    return 56.5 + 1.6 * np.sin(gx * 0.13) + 0.9 * np.sin(gx * 0.31 + 1.0)


def sea_field(gx, gy):
    """Tiles inside the sea (>0 is water): everything south of the tide line."""
    return np.asarray(gy, float) - shore_y(gx)


def deck_field(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    d = np.full(gx.shape, -9.0)
    for (x0, x1, y0, y1) in DECKS:
        d = np.maximum(d, np.minimum.reduce([gx - x0, x1 - gx, gy - y0, y1 - gy]))
    return d


def cliff_field(gx, gy):
    """The hedged rim on three sides, the gap at the north gate, and nothing over the sea or a road."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    edge = np.minimum.reduce([gx, W - gx, gy])
    rock = (3.6 + 1.3 * wob(gx * 0.6, gy * 0.6)) - edge
    gate = (np.abs(gx - 48.0) < 2.6) & (gy < 8)
    rock = np.where(gate, np.minimum(rock, -1.0), rock)
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    rock = np.where(sea_field(gx, gy) > -1.0, np.minimum(rock, -0.5), rock)
    rock = np.where(deck_field(gx, gy) > -1.0, np.minimum(rock, -0.5), rock)
    return rock


def fields(gx, gy):
    gx = np.asarray(gx, float)
    sea = sea_field(gx, gy)
    return dict(cliff=cliff_field(gx, gy), shallow=sea, deep=sea - 4.0, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


SUBZONES = [
    ("Southshore", 0, 0, W, H),
    ("Southshore Square", 38, 24, 20, 14),
    ("Southshore Quay", 34, 48, 28, 24),
]

# ---- baker config (read by tools/bake_hillsbrad.py; the same green country as the fields outside the gate) ----------
BASE = {"grass": 0.66, "forest": 0.14, "fern": 0.12, "rocky": 0.10}
PAINT = {
    "field":  [(16, 41, 8, 5, 1.0), (80, 40, 7, 4, 0.8)],             # Holloway's plots and the back gardens
    "earth":  [(48, 9, 4, 3, 0.8), (78, 22, 6, 4, 0.7), (36, 52, 5, 2, 0.7)],
    "meadow": [(28, 14, 8, 5, 0.8), (70, 12, 9, 5, 0.7)],
    "gravel": [(62, 51, 5, 2, 0.6)],
    "forest": [(8, 12, 7, 6, 0.7), (88, 14, 7, 6, 0.7)],
}
COBBLE = [(48, 31, 8, 5.5, 0.95), (48, 51, 7, 2.6, 0.85)]

# ---- NPC spots ------------------------------------------------------------------------------------------------------
#: The nine hbw_ss_* people (tools/hillsbrad_npc_roster.py), moved in off Western Hillsbrad's coast.
NPC_POSITIONS = {
    "hbw_ss_sentry_garrick":   (44, 11),     # either side of the gate, inside it
    "hbw_ss_sentry_ivy":       (52, 11),
    "hbw_ss_captain_callard":  (54, 35),     # on the square, in front of the street to the hall
    "hbw_ss_child_pip":        (41, 35),     # the square's south-west corner
    "hbw_ss_innkeeper_rowe":   (66, 32),     # at the inn's window, on the row
    "hbw_ss_brother_venn":     (25, 21),     # at the chapel door
    "hbw_ss_farmer_holloway":  (17, 35),     # at the top of his plots
    "hbw_ss_netmender_rose":   (60, 53),     # at the nets on the strand
    "hbw_ss_dockmaster_pryce": (48, 61),     # out on the quay
}
CHESTS = []

OAKS = [("ek_willow", 8, 0.30), ("ek_pine_trio", 7, 0.32), ("ek_pine_tall", 8, 0.28)]
FOREST = dict(seed=131, count=30, rim=6, thorn=10, names=[
    ("ek_willow", 7, 0.30), ("ek_pine_trio", 7, 0.32), ("ek_pine_tall", 8, 0.28), ("ek_thorn_bush", 4, 0.40)])

CO = "assets/tiles/coastal_props/"


def dress(L):
    p, b = L.prop, L.bld
    # ---- the north gate: the gatehouse stands over the door (it's entrance art: world/portal_art.py)
    L.deco("ek_gatehouse", 48, 6, 7, path_dir="assets/buildings/")
    p("ek_signpost", 53, 14, 4)
    # ---- the west side: the townhouse, the chapel, Holloway's plots
    b("ek_townhouse", 33, 27, 9, nudge=2)
    b("ek_village_chapel", 20, 17, 9, nudge=2)
    p("ek_scarecrow", 15, 41, 4)
    p("ek_haystack", 23, 38, 3)
    p("ek_farm_fence", 10, 46, 3, solid=False)
    p("ek_farm_fence", 18, 47, 3, solid=False)
    p("ek_farm_cart", 26, 41, 4)
    b("ek_cottage_small", 30, 45, 6, nudge=2)
    b("ek_barn", 9, 40, 8, nudge=2)
    b("ek_granary", 26, 39, 6, nudge=2)
    # ---- up the high street from the gate: the town's own houses
    b("ek_cottage_medium", 39, 20, 8, nudge=2)
    b("ek_townhouse", 58, 20, 9, nudge=2)
    b("ek_cottage_small", 39, 12, 6, nudge=2)
    # ---- the square: the well in the middle of it
    p("ek_farm_well", 44, 30, 4, road_ok=True)
    # ---- the east side: the inn, the militia hall, the back gardens
    b("ek_village_inn", 66, 28, 10, nudge=2)
    b("ek_barracks_hall", 79, 21, 9, nudge=2)
    b("ek_cottage_medium", 81, 43, 8, nudge=2)
    b("ek_cottage_small", 67, 45, 6, nudge=2)
    b("ek_smithy_forge", 57, 43, 7, nudge=2)
    b("ek_stable_block", 70, 13, 7, nudge=2)
    b("ek_trading_post", 38, 43, 7, nudge=2)
    p("ek_farm_fence", 76, 46, 3, solid=False)
    # ---- the strand: the boathouse, the fishery and its nets, the watchtower on the point
    b("ek_boathouse", 36, 52, 7, nudge=2, shore_ok=True)
    b("ek_fishery_shed", 63, 50, 7, nudge=2, shore_ok=True)
    b("ek_border_watchtower", 85, 52, 9, nudge=2, shore_ok=True)
    p(CO + "fish_drying_rack.png", 57, 52, 4, shore_ok=True)
    p(CO + "driftwood_pile.png", 22, 55, 3, shore_ok=True)
    p(CO + "rowboat_wreck.png", 74, 57, 3, shore_ok=True)
    # ---- the quay: lanterns, crates and posts over the planks, and the ship tied up at the T-head
    L.deco("dock_lantern_post", 46, 58, 4, path_dir=CO)
    L.deco("dock_lantern_post", 50, 64, 4, path_dir=CO)
    L.deco("fish_crates_traps", 52, 69, 3, path_dir=CO)
    L.deco("mooring_posts", 40, 69, 3, path_dir=CO)
    L.deco("boat_human", 66, 77, 10, path_dir=CO)
    T.grove(L, 10, 22, 5, 5, 4, OAKS, seed=31)
    T.grove(L, 88, 32, 4, 6, 4, OAKS, seed=32)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_southshore():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/southshore_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
