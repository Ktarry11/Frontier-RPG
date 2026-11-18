"""
Hand-built Talrendis Landing (112x92): the Horde's arcane salvage camp on Talrendis Point, West Azshara, 52-55
(docs/azshara_brief.md).

Kyle, 17 Nov 2026: one of Azshara's two hubs is "a mixture of orcs and bloodelves", an arcane salvage camp.
Orgrimmar provides the muscle and the blood elves provide the magisters, and together they're stripping Highborne magic
out of the ruins. Neither trusts the other.

ORIENTATION FOLLOWS THE OVERWORLD (Kyle: "ensure the orientation is accurate"). West Azshara's gate to the Landing
(40,150) is on the north shore of the lake on Talrendis Point, with the road coming down from the north and the water
to the south and south-west. So here the gate is on the north edge and the lake fills the south and comes up the
west side.

NOT SOUTHSHORE (Kyle: "that city looks identical to south shore"). The first draft had Southshore's bones: a gate at
the top, one street straight down to the water, a cross row and piers. The Landing is built round the work instead:

    the gate (30,1), north-west <- West Azshara (40,150)
    the shared ground by the gate: the inn and the wind rider roost
    THE DIG in the middle: an excavated Highborne courtyard, old flagstone under the mud, a broken spire still standing
      in it, and a ring road round it
    the orcs on the high ground north-east: the command hall, the barracks, the forge, the watchtower
    the Sunreach Conclave on the lakeshore west: the pavilion, the research tent, the field spire
    a jetty off the south-east for the orcs' longboat, and a short one off the west beach for the elves' skiff

The buildings are Kyle's Landing sheet (docs/azshara_art_prompts.md sheet 3, the tl_ set) and the ruins his Azshara
props sheet (sheet 2). The ground is West Azshara's (tools/bake_ashenvale.py AZSHARA_SHEET).

THE SUNREACH CONCLAVE'S PEOPLE ARE MOVABLE. Kyle: "Don't tie leader or anything to a quest so they can be moved" and
"The elves can get an island later". tl_sunreach_magister and tl_sunreach_quartermaster give and take no quests.

HARD CONTRACTS (world/portal_manager.py)
  portal   (30,1) <-> West Azshara (40,150): you arrive at (30,5) coming in and (40,148) going out
  NPC ids  tl_*, written by tools/build_talrendis_landing.py from NPC_POSITIONS
"""
import sys

import numpy as np

from tools import ashenvale_town_kit as AK
from tools.handbuilt_central_barrens import _gauss

KEY = "talrendis_landing"
NAME = "Talrendis Landing"
DESC = ("The Horde's salvage camp on Talrendis Point: orc muscle, blood elf magisters, and a yard full of Highborne "
        "stone that both of them say is theirs.")
REGION = "Kalimdor - Azshara"
W, H = 112, 92
BAKED_DIR = "assets/tiles/azshara/baked_talrendis"
SHEET = "azshara_west"
PORTALS = {(30, 1): "West Azshara"}
ARRIVALS = [(30, 5)]
START = (30, 8)

ROADS = {
    "gate":  ([(30, 0), (30, 10), (36, 20), (44, 26)], 3.2),
    # the ring round the dig
    "ring":  ([(44, 26), (60, 21), (78, 26), (85, 40), (78, 54), (60, 59), (42, 54), (36, 40), (44, 26)], 2.8),
    "mooring": ([(42, 54), (32, 60), (24, 65)], 2.4),
    "jetty": ([(78, 54), (88, 62)], 2.4),
    "orcs":  ([(78, 26), (90, 22), (100, 22)], 2.4),
}
STREAMS = {}
POOLS = []
PLAZA = None
#: the dig's floor: the Highborne courtyard they've uncovered, white marble with gold inlay under the mud
PAVED_PATCHES = []                 # the dig's old flagstone is an EXTRA_PATCHES "plaza" blob (white marble read as a smear)
CLEARINGS = [(62, 40, 48, 30), (30, 10, 12, 9), (96, 30, 12, 16), (19, 40, 12, 20),
             (58, 70, 58, 11),               # the waterfront: open ground right down to the beach, so no woods
             (19, 60, 12, 9)]                # paint against the water
ROCKS = [(104, 6, 5, 4)]
DECKS = [(86.0, 89.5, 62.0, 84.0),           # the orcs' jetty
         (80.0, 96.0, 82.0, 86.0),           # its head
         (22.5, 25.5, 64.0, 78.0)]           # the elves' short jetty off the west beach
DECK_MAT = "pl_horde"
SEA_DEEP = 4.0
CLEARING_GRASS = False
GRADE = (1.25, 1.10)
EXTRA_PATCHES = {"plaza": [(60, 40, 11, 7, 1.8)], "mud": [(60, 40, 20, 14, 1.4)], "rocky": [(90, 16, 12, 7, 0.9)], "sawdust": [(92, 34, 6, 4, 1.0)],
                 "scorch": [(98, 42, 4, 3, 1.0)]}


def _ell(gx, gy, cx, cy, rx, ry):
    return (1 - np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)) * min(rx, ry)


def shore(gx):
    """The lake's edge: along the south, easing north on the west side (the lake lies south-west of the gate).
    Kept gentle on purpose: a steep diagonal shore paints its beach as a staircase (Kyle: "tiles here look weird")."""
    gx = np.asarray(gx, float)
    return 72.0 + 1.4 * np.sin(gx * 0.11) + 0.8 * np.sin(gx * 0.29 + 0.7) - 9.0 * np.exp(-gx / 15.0)


def sea(gx, gy):
    return np.asarray(gy, float) - shore(gx)


NPC_POSITIONS = {
    # by the gate, shared
    "tl_gate_grunt":         (26, 7),     # an orc at the gate
    "tl_gate_spellbreaker":  (38, 8),     # and a blood elf on the other side, not talking
    "tl_innkeeper":          (17, 26),    # the inn
    "tl_flight_master":      (51, 17),    # the wind rider roost
    # the orcs' high ground
    "tl_overseer":           (66, 19),    # Orgrimmar's man in charge of the dig, where he can see all of it
    "tl_smith":              (94, 44),    # the forge
    # the Sunreach Conclave's lakeshore, west (the magister and the quartermaster give no quests: they move later)
    "tl_sunreach_magister":  (28, 51),
    "tl_sunreach_quartermaster": (21, 61),
    # the mess by the water
    "tl_provisioner":        (53, 64),
}
CHESTS = []


def dress(L):
    A, B, V = L.p, L.b, L.v
    # ---- the gate, and the shared ground inside it
    B("tl_gatehouse", 30, 10, 8, solid=False, road_ok=True)
    A("tl_signpost", 38, 15, 4)
    B("tl_inn", 16, 23, 10)
    B("tl_wind_rider_roost", 47, 14, 11)
    A("tl_notice_board", 25, 28, 4)
    # ---- THE DIG: the courtyard they've uncovered, the spire still standing in it, and the work going on round it
    A("az_broken_spire", 66, 36, 12)
    A("az_moon_arch", 52, 35, 7)
    A("az_noble_statue", 68, 49, 7)
    A("az_toppled_column", 52, 48, 4)
    B("tl_stone_crane", 74, 46, 7)
    A("tl_relic_cage", 47, 31, 4)
    A("tl_rail_cart", 72, 31, 4)
    B("tl_dig_entrance", 55, 44, 5)
    A("tl_column_pile", 44, 46, 4)
    # ---- the orcs' high ground
    B("tl_command_hall", 68, 16, 10)
    B("tl_orc_barracks", 88, 20, 9)
    B("tl_log_watchtower", 101, 16, 9, nudge=3)
    B("tl_orc_forge", 98, 41, 8)
    A("tl_lumber_stack", 92, 33, 5)
    B("tl_war_tent", 100, 30, 7)
    A("tl_survey_tower", 101, 56, 7)
    # ---- the Sunreach Conclave's lakeshore, west
    B("tl_magister_pavilion", 24, 47, 8)
    B("tl_research_tent", 12, 38, 8)
    B("tl_scribes_canopy", 31, 38, 6)
    B("tl_quartermaster", 15, 58, 6)
    A("tl_mana_cell_rack", 8, 50, 4)
    A("tl_field_spire", 34, 58, 7)
    A("tl_ward_pylon", 9, 60, 5)
    # ---- the mess by the water, where both sides eat and neither sits with the other
    B("tl_mess_table", 48, 63, 6)
    A("tl_shared_fire", 60, 66, 3)
    A("tl_sandbags", 76, 66, 3)
    A("tl_cairn", 96, 64, 5)
    # ---- the water
    V("tl_orc_longboat", 94, 80, 4)
    V("tl_elf_skiff", 19, 79, 4)
    V("dock_lantern_post", 90, 64, 4)
    V("fish_crates_traps", 84, 70, 3)
    L.edge_canopy(seed=211, names=(("az_autumn_tree", 11), ("az_gold_tree", 9), ("az_birch_trio", 9)))


AK.install(sys.modules[__name__])
