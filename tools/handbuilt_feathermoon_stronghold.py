"""
Hand-built Feathermoon Stronghold (124x104): the Sentinels' island fortress off the Forgotten Coast, Feralas, 46-48
(docs/feralas_brief.md).

Kyle, 19 Nov 2026: both towns, each its own map with an inn and a flight path, and the Feathermoon Sentinels as
Feralas's new faction, led by Shandris Feathermoon. Transplants are factionless (Kyle's lore), so the night elves let
you land and work for them.

ORIENTATION FOLLOWS THE OVERWORLD. Feathermoon Landing is on the mainland's west shore, and the island lies west of it
out at sea, so the boat comes in on the island's EAST side: the harbour is on the east, the fortress stands on the high
ground in the middle, and the open sea is all round.

    the harbour pier (116,52), east <- the boat from Feathermoon Landing (The Forgotten Coast, 62,118)
    the harbour: the boathouse, the cargo, the inn just up from the water
    the fortress in the middle: the great hall, the barracks, the walls and their towers, the moonwell
    the roost on the north rise, the garrison's archery ground on the south

THE ART: built before Kyle's Feralas sheets (Kyle, 19 Nov 2026: "Build without art for now"), from the night elf pieces
already in the game (Felwood's Sentinel hall and towers, Moonglade's houses, inn and moonwell). docs/feralas_art_prompts.md
sheet 4 is Feathermoon's own set.

HARD CONTRACTS (world/portal_manager.py)
  portal   (116,52) <-> The Forgotten Coast (62,118): you arrive at (111,52) coming in and (65,118) going out
  NPC ids  fm_*, ct_feathermoon, pt_fm_*: written by tools/build_feralas_towns.py from NPC_POSITIONS
"""
import sys

import numpy as np

from tools import ashenvale_town_kit as AK

KEY = "feathermoon_stronghold"
NAME = "Feathermoon Stronghold"
DESC = ("The Sentinels' fortress on its island off the Forgotten Coast: pale stone, moon lanterns and a harbour, and "
        "Shandris Feathermoon watching the sea.")
REGION = "Kalimdor - Feralas"
W, H = 124, 104
BAKED_DIR = "assets/tiles/feralas/baked_feathermoon"
SHEET = "feralas_forgotten_coast"
PORTALS = {(116, 52): "The Forgotten Coast"}
ARRIVALS = [(111, 52)]
START = (104, 52)

ROADS = {
    "harbour": ([(110, 52), (96, 52), (82, 52)], 3.2),
    # the fortress street, round the great hall
    "ring":    ([(82, 52), (74, 40), (60, 34), (44, 40), (38, 52), (44, 66), (60, 72), (74, 66), (82, 52)], 3.0),
    "roost":   ([(60, 34), (60, 22), (62, 14)], 2.6),
    "range":   ([(60, 72), (58, 84)], 2.6),
    "inn":     ([(96, 52), (96, 40)], 2.4),
}
STREAMS = {}
POOLS = []
PLAZA = (60, 52, 9, 7)
PAVED_PATCHES = [(60, 52, 16, 13)]
#: the whole island is open ground (the woods would paint over the sea); the trees are placed in dress()
CLEARINGS = [(62, 52, 46, 36), (62, 52, 90, 80)]
ROCKS = []
DECKS = [(100.0, 120.0, 49.5, 54.5),          # the harbour pier, out to the boat
         (104.0, 108.0, 54.5, 62.0)]          # the boathouse's slip
DECK_MAT = "pl_elf"
SEA_DEEP = 5.0
CLEARING_GRASS = True
GRADE = (1.22, 1.10)
EXTRA_PATCHES = {"rocky": [(20, 30, 8, 6, 0.9), (30, 80, 6, 5, 0.9)]}


def sea(gx, gy):
    """The sea all round the island. Extent > 0 is sea."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    r = np.sqrt(((gx - 60) / 52.0) ** 2 + ((gy - 52) / 44.0) ** 2)
    wob = 0.04 * np.sin(np.arctan2(gy - 52, gx - 60) * 5 + 0.7) + 0.025 * np.sin(np.arctan2(gy - 52, gx - 60) * 11)
    return (r - 1.0 - wob) * 44.0


NPC_POSITIONS = {
    # the harbour
    "fm_harbour_sentinel": (100, 48),   # the Sentinel on the pier
    "fm_innkeeper":        (96, 38),    # Innkeeper Shyria, the inn up from the water
    "fm_provisioner":      (88, 60),
    # the fortress
    "fm_shandris":         (60, 44),    # Shandris Feathermoon, before the great hall
    "fm_latronicus":       (46, 46),    # Latronicus Moonspear, keeper of the ruins
    "fm_selarin":          (76, 46),    # Sentinel Selarin, the coast watch
    "fm_kindal":           (52, 66),    # Kindal Moonweaver, the druid, by the moonwell
    "fm_jalara":           (68, 66),    # Huntress Jalara Nightwind
    "fm_quartermaster":    (40, 58),    # Quartermaster Lyriel Dawnbough (gives no quests: she can move)
    "fm_smith":            (78, 62),    # the armoury
    "ct_feathermoon":      (42, 36),    # the class trainer
    "pt_fm_herbs":         (70, 80),    # herbs and alchemy
    "pt_fm_fish":          (108, 58),   # cooking and fishing, on the slip
    # the roost
    "fm_flight_master":    (64, 18),    # Fyldren Moonfeather
}
CHESTS = []


def dress(L):
    A, B, V = L.p, L.b, L.v
    # ---- the harbour
    V("dock_lantern_post", 118, 49, 4)
    V("fish_crates_traps", 104, 47, 3)
    B("bd_boat_shed", 106, 66, 7)
    A("ash_supply_crates", 92, 58, 3)
    A("ash_moon_barrels", 88, 46, 3)
    B("mg_elf_inn", 96, 36, 9)
    # ---- the fortress: the great hall, walls and towers, the moonwell
    B("fw_sentinel_hall", 60, 40, 11)
    B("sentinel_outpost_hall", 76, 34, 9)
    B("fw_sentinel_tower", 34, 34, 11)
    B("moon_guard_tower", 84, 70, 10)
    B("fw_sentinel_tower", 34, 72, 11)
    B("mg_moonwell", 60, 66, 5)
    A("ash_elune_statue", 60, 58, 7)
    A("ash_moon_lantern", 50, 52, 4)
    A("ash_moon_lantern", 70, 52, 4)
    B("mg_elf_house", 44, 76, 8)
    B("nightelf_house_small", 26, 54, 7)
    B("mg_elf_cottage", 30, 64, 7)
    B("mg_herb_stall", 72, 78, 5)
    A("ash_sentinel_weapon_rack", 80, 58, 3)
    A("ash_sentinel_banner", 50, 34, 5)
    A("ash_sentinel_banner", 70, 34, 5)
    # ---- the roost on the north rise
    B("fw_hippogryph_roost", 62, 14, 10, nudge=3)
    A("ash_hippogryph_perch", 74, 18, 5)
    # ---- the archery ground on the south
    A("ash_archery_butts", 52, 88, 4)
    A("ash_archery_butts", 62, 90, 4)
    B("fw_sentinel_tent", 72, 88, 6)
    # ---- the island's trees, round the walls
    for (x, y, n, h) in [(20, 40, "large_canopy_tree", 12), (24, 70, "medium_canopy_tree", 10), (40, 88, "canopy_tree_cluster", 11),
                         (86, 84, "large_canopy_tree", 12), (94, 24, "medium_canopy_tree", 10), (36, 18, "large_canopy_tree", 12),
                         (84, 14, "canopy_tree_cluster", 11), (16, 56, "medium_canopy_tree", 10), (100, 76, "medium_canopy_tree", 9)]:
        A(n, x, y, h)
    A("ash_moonstone_crystals", 22, 30, 4)
    A("rock_outcrop_small", 28, 82, 4)


AK.install(sys.modules[__name__])
