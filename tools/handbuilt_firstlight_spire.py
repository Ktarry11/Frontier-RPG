"""
Hand-built Firstlight Spire (104x92): the blood elves' city on Dawnhaven, the seat of the Sunreach Conclave, 1-9
(docs/dawnhaven_brief.md).

Kyle, 21 Nov 2026: "then their capital city, it's not massive though. Not even close to a capital city. Perhaps a
bloodelf spire city?", and its name, "something that signifies the potential of a new home". A small town on the
headland at the north end of Dawnhaven, built round one great spire the outpost's founders raised and the Conclave
has lit again. It has an inn and the island's flight path, class and trade trainers, a bank and a mailbox, and no
auction house. Its pier sends the boat to Durotar's north-east coast.

    the south gate (52,90) <- Duskfall Woods (80,4)
    the Avenue up from the gate to the Lit Court, the plaza under the spire, with the Sunwell's little sister in it
    Firstlight Spire itself at the head of the court
    the Conclave Hall west of the spire: Grand Magister Velanthe and her quartermaster
    the inn, the bank and the mailbox on the west terrace; the dragonhawk roost below them
    the trainers' row east: the library, the forge and the alchemist
    the pier off the east shore, and the boat to Durotar (98,58)

THE SUNREACH CONCLAVE'S PEOPLE STAY MOVABLE. tl_sunreach_magister and tl_sunreach_quartermaster still give and take no
quests (tools/build_talrendis_landing.py checks), so either can move again.

HARD CONTRACTS (world/portal_manager.py)
  portals  (52,90) <-> Duskfall Woods (80,4); (98,58) <-> Durotar's north-east pier
  NPC ids  written by tools/build_dawnhaven_people.py from NPC_POSITIONS
"""
import sys

import numpy as np

from tools import ashenvale_town_kit as AK

KEY = "firstlight_spire"
NAME = "Firstlight Spire"
DESC = ("The blood elves' city on Dawnhaven: one great spire the outpost's founders raised, lit again, and a small "
        "town at its feet. The seat of the Sunreach Conclave, and the first home many of its people have had in years.")
REGION = "Kalimdor - Dawnhaven"
W, H = 104, 92
BAKED_DIR = "assets/tiles/dawnhaven/baked_firstlight"
SHEET = "firstlight_spire"
PORTALS = {(52, 90): "Duskfall Woods", (98, 58): "Durotar"}
ARRIVALS = [(52, 86), (94, 58)]
START = (52, 84)

ROADS = {
    "avenue":  ([(52, 91), (52, 76), (52, 62), (52, 50)], 3.4),
    "spire":   ([(52, 38), (52, 32)], 3.0),
    "west":    ([(46, 58), (34, 58), (24, 56), (18, 60)], 2.8),
    "conclave": ([(44, 42), (34, 38), (28, 36)], 2.6),
    "east":    ([(58, 58), (70, 58), (82, 58), (88, 58)], 2.8),
    "trainers": ([(70, 58), (72, 48), (74, 40)], 2.4),
    "forge":   ([(70, 58), (70, 70), (68, 76)], 2.4),
}
STREAMS = {}
POOLS = []
PLAZA = (52, 44, 12, 7)            # the Lit Court, under the spire
PAVED_PATCHES = [(52, 28, 9, 6), (28, 36, 7, 5)]
CLEARINGS = [(52, 44, 30, 22), (52, 70, 22, 22), (28, 50, 20, 30), (74, 56, 24, 30), (88, 58, 10, 8), (52, 26, 16, 12)]
ROCKS = []
DECKS = [(86.0, 100.0, 56.0, 61.0)]         # the pier off the east shore
DECK_MAT = "pl_pier"                # plain pier boards (the night elves' violet planks read purple against the gold)
SEA_DEEP = 3.0
CLEARING_GRASS = False
GRADE = (1.28, 1.12)
EXTRA_PATCHES = {"plaza": [(52, 44, 10, 6, 1.6), (52, 28, 7, 4, 1.4)]}


def sea(gx, gy):
    """The headland: sea to the west, the north and the east, the land running south to the gate."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    west = 7.0 + 1.5 * np.sin(gy * 0.17) + 3.0 * np.exp(-((gy - 20) / 10) ** 2) - gx
    east = gx - (88.0 + 1.5 * np.sin(gy * 0.21 + 0.6) - 3.0 * np.exp(-((gy - 18) / 10) ** 2))
    north = 6.0 + 1.2 * np.sin(gx * 0.19) - gy
    return np.maximum.reduce([west, east, north])


NPC_POSITIONS = {
    # the Lit Court and the spire
    "dh_lorien": (52, 36),                  # Spire-Keeper Lorien Ashbloom, who lit it again
    # the Conclave Hall (the two who move give no quests)
    "tl_sunreach_magister": (26, 40),
    "tl_sunreach_quartermaster": (33, 40),
    # the west terrace
    "dh_innkeeper": (22, 52),
    "dh_flight_master": (14, 66),
    "dh_banker": (36, 64),
    "mailbox_dh_innkeeper": (40, 60),
    # the trainers' row, east
    "ct_firstlight": (78, 44),
    "pt_firstlight_forge": (64, 74),
    "pt_firstlight_alchemy": (76, 70),
    "pt_firstlight_cloth": (82, 64),
    "pt_firstlight_enchanting": (68, 42),
    # the pier
    "dh_joost": (86, 55),
    "dh_spire_provisioner": (60, 52),
    "dh_spire_gate_south": (48, 84),  # townsfolk
    "dh_spire_gate_pier": (84, 59),  # townsfolk
    "dh_spire_citizen": (46, 50),  # townsfolk
    "dh_spire_student": (66, 46),  # townsfolk
    "dh_pier_fisher": (96, 57),  # townsfolk
    "dh_spire_settler": (29, 57),  # townsfolk
}
CHESTS = []


def dress(L):
    """Kyle's DH3 buildings and DH4 street props (docs/dawnhaven_art_prompts.md, 21 Nov 2026). The bank keeps the
    bank's own art, and the shop keeps be_shop (DH3 has no shop)."""
    A, B, V, F = L.p, L.b, L.v, L.f
    # ---- the south gate
    B("ent_town_highelf_gate", 52, 89, 7, solid=False, road_ok=True)
    A("dh_runed_obelisk", 44, 84, 5)
    A("dh_runed_obelisk", 60, 84, 5)
    # ---- the spire, at the head of the Lit Court
    B("dh_firstlight_spire", 52, 30, 22)
    # ---- the Lit Court: the phoenix fountain in the middle, the founder, the stalls round it
    B("dh_fountain", 52, 46, 5)
    A("dh_founder_statue", 52, 38, 5)
    A("dh_stall_fruit", 42, 50, 4)
    A("dh_stall_cloth", 62, 50, 4)
    A("dh_stall_arcane", 41, 44, 4)
    A("dh_stall_fish", 63, 44, 4)
    A("dh_street_lamp", 46, 54, 4)
    A("dh_street_lamp", 58, 54, 4)
    F("dh_bench", 47, 41, 2)
    F("dh_bench", 57, 41, 2)
    A("dh_notice_board", 56, 62, 3)
    # ---- the Conclave Hall, west of the spire
    B("dh_conclave_hall", 28, 34, 11)
    A("dh_garden_arch", 38, 40, 5)
    A("dh_planter", 22, 40, 2)
    # ---- the west terrace: the inn, the bank, the mailbox, and the roost below
    B("dh_spire_inn", 20, 49, 10)
    A("dh_inn_table", 27, 54, 3)
    B("bank_blood_elf", 34, 61, 9)
    B("dh_hawk_roost", 16, 74, 8)
    B("dh_house_small", 12, 40, 6)
    # ---- the trainers' row, east
    B("dh_library_tower", 76, 40, 10)
    A("dh_book_stand", 70, 44, 3)
    B("dh_forge", 66, 80, 8)
    A("dh_anvil", 60, 77, 2)
    B("dh_alchemist", 80, 76, 8)
    B("be_shop", 84, 70, 7)
    A("dh_training_dummy", 74, 52, 3)
    A("dh_weapon_rack", 80, 52, 3)
    B("dh_townhouse", 84, 30, 9)
    # ---- the houses down the Avenue: the first homes, and the ones still going up
    B("dh_townhouse", 40, 76, 8)
    B("dh_house_small", 64, 66, 6)
    B("dh_house_small", 30, 84, 6)
    B("dh_house_small", 72, 86, 6)
    A("dh_building_stock", 46, 70, 2)
    A("dh_marble_wall", 58, 72, 2)
    A("dh_handcart", 46, 64, 2)
    A("dh_barrels", 62, 58, 2)
    # ---- the pier and the boat
    V("tl_elf_skiff", 97, 66, 5)
    V("dh_mooring_post", 88, 55, 3)
    V("dh_mooring_post", 99, 55, 3)
    V("fish_crates_traps", 90, 63, 3)
    V("dh_rowboat", 92, 64, 2)
    L.edge_canopy(seed=611, names=(("dh_autumn_tree", 10), ("az_gold_tree", 10), ("dh_maple_sapling", 7)))


AK.install(sys.modules[__name__])

#: the districts, where the townsfolk live (Kyle, 22 Nov 2026: "ensure ALL towns are actually populated"; names made up to
#: fit). (key, x, y, w, h, display name)
SUBZONES = [
    ('Firstlight Spire', 0, 0, 104, 92, None),
    ('The Conclave Hall', 4, 14, 32, 24, None),
    ('The Spire Court', 36, 6, 32, 36, None),
    ('The Library', 68, 20, 32, 28, None),
    ('The Inn Steps', 4, 38, 32, 18, None),
    ('The Bank Row', 24, 54, 26, 16, None),
    ('The Hawk Roost', 2, 60, 24, 22, None),
    ("The Crafters' Lane", 56, 60, 40, 28, None),
    ('The Pier Steps', 84, 48, 20, 18, None),
    ('The South Gate', 38, 70, 20, 22, None),
]
