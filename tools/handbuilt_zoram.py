"""
Hand-built Zoram Strand (60x50): the night elves' fishing cove on Ashenvale's western coast.

TOWN ARCHETYPE: SHELTERED COVE WITH A SINGLE PIER.  The forest ends at a pale beach; the sea bites a small bay into
the coast and one long plank pier runs out to a T-head where the boats tie up.  A moon-guard lookout watches the
north headland, a Sentinel tent and a handful of houses sit above the tide line, and the fishers' racks and a market
stall line the beach.  (Smallest town in the game by design: a quiet end-of-the-road outpost.)

HARD CONTRACTS (world/portal_manager.py)
  portal   (50,25) -> Ashenvale West (15,30);  arrival (50,23)
  NPC ids  positions / records written by tools/sync_ashenvale_town_npcs.py
"""
import sys

import numpy as np

from tools import ashenvale_town_kit as AK
from tools.handbuilt_central_barrens import _gauss

KEY = "zoram"
NAME = "Zoram Strand"
DESC = "A rocky coastline on Ashenvale's western edge, boats bound for distant shores."
REGION = "Kalimdor - Western Forest"
W, H = 60, 50
BAKED_DIR = "assets/tiles/zoram_strand/baked"
PORTALS = {(50, 25): "Ashenvale West"}
ARRIVALS = [(50, 23)]
START = (48, 25)

ROADS = {
    "main":  ([(52, 25), (44, 25), (35, 26), (27, 25), (19, 25)], 3.0),
    "north": ([(35, 25), (34, 19), (31, 13), (26, 11)], 2.4),
    "south": ([(33, 26), (34, 32), (36, 38)], 2.4),
}
CLEARINGS = [(30, 25, 26, 17), (50, 25, 8, 6), (26, 12, 7, 6), (30, 38, 12, 6)]
DECKS = [(3.0, 19.5, 23.8, 26.2),              # the pier
         (2.5, 7.5, 19.0, 31.0)]               # its T-head
DECK_MAT = "pl_pier"
SEA_DEEP = 3.8
PAVED_PATCHES = []
EXTRA_PATCHES = {"grass": [(40, 25, 12, 9, 1.7), (36, 12, 8, 4, 1.3), (38, 38, 8, 4, 1.3)]}


def shore(gy):
    gy = np.asarray(gy, float)
    return (13.0 + 4.5 * _gauss(gy, 25, 7.0) + 1.3 * np.sin(0.42 * gy + 0.6) + 0.8 * np.sin(0.97 * gy))


def sea(gx, gy):
    return shore(gy) - np.asarray(gx, float)


NPC_POSITIONS = {
    "zoram_boatwright": (14, 24),         # Boatwright Illyen - pier
    "zoram_fisher": (25, 33),             # Old Maelis - drying racks
    "zoram_sentinel": (26, 15),           # Lookout Taelanor - tower foot
    "zoram_fishmonger": (29, 27),         # vendor: Fishmonger Sylra - beside the stall
}
CHESTS = [(44, 40), (20, 10)]


def dress(L):
    A, B, F, V = L.p, L.b, L.f, L.v
    # ---- pier furniture (visual, over the planks)
    V("ash_moon_lantern", 6, 21, 5)
    V("ash_moon_lantern", 6, 29, 5)
    V("ash_moon_lantern", 12, 24, 5)
    V("fish_crates_traps", 10, 26, 3)
    # ---- north headland: lookout tower, glow ring
    B("moon_guard_tower", 26, 14, 14)
    A("ash_glow_mushroom_ring", 20, 12, 4)
    A("ash_silver_saplings", 31, 9, 6)
    # ---- above the tide line: houses, Sentinel tent, market
    B("nightelf_house_small", 38, 18, 10)
    B("nightelf_house_small", 40, 33, 10)
    B("ash_sentinel_tent", 29, 36, 7)
    A("ash_sentinel_banner", 33, 30, 6)
    A("ash_market_stall", 29, 24, 6)
    A("ash_signpost", 41, 27, 5)
    # ---- the beach: racks, boats, driftwood
    A("fish_drying_rack", 24, 31, 4)
    A("fish_crates_traps", 21, 28, 3)
    A("rowboat_wreck", 16, 37, 4, shore_ok=True)
    A("driftwood_pile", 14, 20, 3, shore_ok=True)
    A("ash_orc_skiff", 16, 32, 5, shore_ok=True)          # a Horde skiff beached by the coastguard's watch
    V("ash_pier_segment", 11, 33, 5)                       # its little landing stage over the shallows
    A("ash_elune_statue", 44, 20, 8)
    for (x, y) in [(36, 41), (24, 20), (47, 31)]:
        F("ash_foxglove_patch", x, y, 3)
    L.edge_canopy(seed=29)


AK.install(sys.modules[__name__])
