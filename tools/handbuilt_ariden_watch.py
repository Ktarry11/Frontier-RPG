"""
Hand-built Ariden's Watch (100x80): the liquidators' camp in Deadwind Pass, the pass's one town (docs/deadwind_brief.md,
docs/deadwind_quest_plan.md).

Kyle, 18 Nov 2026: the outpost is its own map, and it's Ariden's Watch, named for the hermit who has been watching
Karazhan for forty years from the other side of the gorge. The liquidators (Earth transplants who've lived next to a
fallout zone, or cleaned one up) hold it with the Forsaken apothecaries, who can walk where the living can't.

ORIENTATION FOLLOWS THE OVERWORLD. Deadwind West's gate to the Watch (96,74) is on the south side of Deadman's
Crossing, with the road coming down from the north, so the gate here is on the north edge.

BUILT ROUND THE PYRE. The camp is a working quarantine, so it's laid out the way one would be, not down a street:

    the gate (48,1), and the wash troughs straight inside it: everybody scrubs before they come any further
    THE PYRE in the middle, which has never gone out, and the board of names beside it
    the command house north-east, where Halyna Bondar runs the camp; Kenji's survey tent east of it
    the infirmary west, and the Forsaken apothecaries' laboratory and sample racks south-west
    the inn to the south, the quartermaster and the smithy south-east, and the bat roost on the far side
    the quarantine fence all the way round, inside the dead forest

The buildings are Kyle's outpost sheet (docs/deadwind_art_prompts.md sheet 4, the dw_ set in assets/buildings) and
the props his Deadwind props sheets. The ground is Deadwind's (tools/bake_ashenvale.py ARIDEN_SHEET).

HARD CONTRACTS (world/portal_manager.py)
  portal   (48,1) <-> Deadwind West (96,74): you arrive at (48,5) coming in and (96,72) going out
  NPC ids  dw_*, written by tools/build_deadwind.py from NPC_POSITIONS
"""
import sys

import numpy as np  # noqa: F401

from tools import ashenvale_town_kit as AK

KEY = "ariden_watch"
NAME = "Ariden's Watch"
DESC = ("The liquidators' camp in Deadwind Pass: a quarantine line, a pyre that never goes out, and a board with more "
        "names on it every week.")
REGION = "Eastern Kingdoms - Deadwind Pass"
W, H = 100, 80
BAKED_DIR = "assets/tiles/deadwind/baked_ariden_watch"
SHEET = "ariden_watch"
PORTALS = {(48, 1): "Deadwind West"}
ARRIVALS = [(48, 5)]
START = (48, 8)

SUBZONES = [   # 22 Nov 2026, for the townsfolk
    ("The Wash Line", 34, 4, 30, 18),
    ("The Pyre", 36, 26, 24, 22),
    ("The Command House", 62, 14, 30, 30),
    ("The Infirmary", 8, 26, 28, 20),
    ("The Laboratory", 8, 48, 30, 22),
    ("The Inn Yard", 38, 58, 26, 16),
    ("The Supply Yard", 64, 44, 30, 26),
]

ROADS = {
    "gate":   ([(48, 0), (48, 12), (48, 22)], 3.2),
    # the ring round the pyre
    "ring":   ([(48, 22), (62, 26), (66, 38), (60, 50), (48, 54), (36, 50), (30, 38), (36, 26), (48, 22)], 2.8),
    "inn":    ([(48, 54), (48, 64)], 3.0),
    "east":   ([(66, 38), (78, 40), (88, 42)], 2.4),
    "roost":  ([(60, 50), (70, 57), (80, 63)], 2.4),
    "lab":    ([(36, 50), (26, 56)], 2.4),
    "ward":   ([(30, 38), (20, 36)], 2.4),
}
STREAMS = {}
POOLS = []
PLAZA = None
PAVED_PATCHES = []
CLEARINGS = [(48, 38, 36, 25), (48, 8, 11, 9), (80, 60, 14, 10), (48, 67, 18, 9), (22, 48, 13, 16),
             (84, 36, 11, 11), (70, 20, 12, 9)]
ROCKS = []
DECKS = []
CLEARING_GRASS = False
LIFT = (1.10, 1.32)
EXTRA_PATCHES = {"satyr": [(48, 38, 22, 15, 1.2), (48, 8, 6, 5, 1.0)], "scorch": [(48, 34, 7, 5, 1.4)],
                 "burned": [(60, 30, 3, 2, 1.0), (24, 60, 3, 2, 0.8)]}

NPC_POSITIONS = {
    # the gate and the troughs
    "dw_harrow":        (43, 9),      # Deathguard Harrow, the gate captain
    # the pyre and the board
    "dw_tobiah":        (54, 39),     # Old Tobiah, the pyrekeeper
    # the command house and the survey tent
    "dw_halyna":        (68, 25),     # Chief Liquidator Halyna Bondar
    "dw_kenji":         (79, 42),     # Kenji Watanabe, at his map table
    # the infirmary and the laboratory
    "dw_aigerim":       (25, 38),     # Dr. Aigerim Seitkali, the camp's doctor
    "dw_morwen":        (27, 58),     # Master Apothecary Morwen Ashgrave
    "dw_lisbeth":       (17, 56),     # Apothecary Lisbeth Vane, Morwen's second
    # the yard
    "dw_luiz":          (62, 46),     # Luiz Ferreira, the camp's salvager
    "dw_peg":           (56, 62),     # Peg Thwaite, who feeds the camp
    "dw_rine":          (38, 25),     # Rine Lajuon, the spire crew's boss
    # the inn, the shelf, the forge and the roost
    "dw_innkeeper":     (44, 66),     # Innkeeper Sela Crowe
    "dw_quartermaster": (70, 51),     # the Liquidators' quartermaster
    "dw_smith":         (80, 55),     # the camp's smith
    "dw_bat_handler":   (84, 63),     # the bat handler
}
CHESTS = []


def dress(L):
    A, B, V = L.p, L.b, L.v
    # ---- the gate, and the wash troughs straight inside it
    B("dw_fence_gate", 48, 4, 6, solid=False, road_ok=True)
    B("dw_quarantine_fence", 40, 4, 5)
    B("dw_quarantine_fence", 56, 4, 5)
    B("dw_wash_trough", 40, 15, 4)
    B("dw_wash_trough", 56, 15, 4)
    B("dw_scrub_station", 37, 20, 5)
    B("dw_water_tank", 60, 11, 7)
    B("dw_mask_rack", 59, 19, 4)
    # ---- the pyre and the board of names
    B("dw_great_pyre", 48, 36, 6)
    B("dw_names_board", 40, 31, 5)
    B("dw_body_cart", 57, 32, 4)
    B("dw_stretchers", 56, 43, 3)
    B("dw_body_sacks", 41, 44, 3)
    A("dw_pyre_unlit", 62, 34, 4)
    # ---- the command house and Kenji's survey tent
    B("dw_command_house", 70, 21, 10)
    B("dw_watchtower", 80, 18, 9)
    B("dw_canvas_tent", 86, 34, 7)
    B("dw_map_table", 79, 39, 4)
    A("dw_sample_crate", 90, 40, 3)
    # ---- the infirmary
    B("dw_infirmary", 19, 33, 8)
    B("dw_exam_table", 28, 42, 4)
    B("dw_candle_shrine", 12, 42, 5)
    # ---- the laboratory and the sample racks
    B("dw_laboratory", 22, 53, 9)
    B("dw_copper_still", 32, 58, 5)
    B("dw_vial_rack", 35, 52, 4)
    B("dw_sample_coffer", 15, 61, 3)
    B("dw_sealed_store", 30, 65, 5)
    # ---- the yard's south side: the inn, the mess, the shelf, the forge
    B("dw_inn", 49, 72, 10)
    B("dw_mess_table", 58, 64, 4)
    B("dw_lean_to", 38, 64, 5)
    B("dw_quartermaster", 70, 48, 6)
    B("dw_supply_stack", 64, 54, 4)
    B("dw_salt_barrel", 76, 50, 3)
    B("dw_smithy", 88, 52, 7)
    B("dw_burn_bin", 82, 45, 3)
    # ---- the roost and the barracks on the far side
    B("dw_bat_roost", 86, 62, 8)
    B("dw_barracks", 72, 64, 7)
    # ---- the fence round the camp
    B("dw_quarantine_fence", 8, 48, 5)
    B("dw_quarantine_fence", 93, 28, 5)
    A("dw_quarantine_stake", 10, 60, 4)
    A("dw_iron_lamp", 44, 26, 4)
    A("dw_iron_lamp", 53, 50, 4)
    L.edge_canopy(seed=233, names=(("dw_dead_tree", 10), ("dw_dead_birches", 9), ("dw_split_tree", 9)))


AK.install(sys.modules[__name__])
