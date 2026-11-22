"""
Hand-built Light's Hope Chapel (96x80): the Argent Dawn's chapel town in the east of the Eastern Plaguelands
(docs/plaguelands_towns_plan.md).

Kyle, 16 Nov 2026: "Move Crown Guard into Lights Hope Chapel and Make it as a seperate town (similar to everything else
in the game)", then "Also fold Crown Guard Camp into Lights Hope". So the chapel is its own map, and the people who
held Crown Guard's camp moved in behind its walls. The old tower stays out on the road, empty, as a landmark.

    the gate ............ south (48,77): up the spur from the road between the tower and Tyr's Hand
    the chapel .......... north, on its square: the Commander, the Lightwarden, the Scourgestone turn-ins
    the infirmary ....... west: the field hospital is the inn, Marisol's patients, Greta's kitchen
    the command row ..... east: the quartermaster's post, the command tent, the bat perch
    Crown Guard's corner  south-west by the gate: the captain's palisade tent, the well, the outrider's horses
    the cemetery ........ south-east: the Dawn buries everyone who needs it, and the gravewarden keeps the list

One inn and one flight master: Jessa's beds and Aldous's bats. Crown Guard's innkeeper and bat handler came with their
camp and help where they're needed.

HARD CONTRACTS (world/portal_manager.py)
  portal   (48,77) -> Eastern Plaguelands East (128,75), its gate up the spur off the Tyr's Hand road;  arrival (48,74)
  NPC ids  epl_lh_*, epl_cg_*, written by tools/sync_epl_east_npcs.py from NPC_POSITIONS
"""
import sys

from tools import ashenvale_town_kit as AK

KEY = "lights_hope"
NAME = "Light's Hope Chapel"
DESC = ("The Argent Dawn's chapel town, on holy ground the dead won't cross. Crown Guard's people live here now, and "
        "the road to Stratholme starts at the gate.")
REGION = "Eastern Kingdoms - Lordaeron"
W, H = 96, 80
BAKED_DIR = "assets/tiles/plaguelands/baked_lights_hope"
SHEET = "epl_east"
PORTALS = {(48, 77): "Eastern Plaguelands East"}
ARRIVALS = [(48, 74)]
START = (48, 72)

SUBZONES = [   # 22 Nov 2026, for the townsfolk
    ("The Chapel Square", 34, 22, 30, 20),
    ("The Infirmary", 8, 36, 26, 16),
    ("The Command Row", 62, 30, 30, 20),
    ("Crown Guard's Corner", 6, 52, 30, 18),
    ("The Cemetery", 56, 58, 30, 14),
    ("The Gate Road", 38, 46, 18, 26),
]

ROADS = {
    "gate":     ([(48, 78), (48, 66), (48, 54), (48, 42)], 4.0),
    "west":     ([(48, 54), (36, 50), (24, 44)], 3.0),
    "east":     ([(48, 54), (62, 50), (74, 42)], 3.0),
    "crown":    ([(48, 66), (36, 66), (24, 64)], 2.6),
    "cemetery": ([(48, 66), (62, 68), (72, 70)], 2.4),
    "perch":    ([(62, 50), (78, 56)], 2.4),
}
STREAMS = {}
POOLS = []
PLAZA = (48, 38, 12.0, 6.0)
PAVED_PATCHES = [(48, 30, 9, 4), (48, 74, 4, 3)]
CLEARINGS = [(48, 46, 42, 32), (48, 70, 30, 10), (48, 16, 22, 8)]
DECKS = []
CLEARING_GRASS = True          # holy ground: the one place in the east where the grass came back
DECK_PAINT = False
GRADE = (1.05, 1.10)

NPC_POSITIONS = {
    # ---- the Argent Dawn
    "epl_lh_commander":     (48, 35),    # Commander Eligor Dawnbringer, on the chapel steps
    "epl_lh_lightwarden":   (41, 34),    # Lightwarden Ysolde Carrow
    "epl_lh_scourgestones": (55, 34),    # Archmage Lysander Hale, who takes the Scourgestones
    "epl_lh_innkeeper":     (24, 45),    # Innkeeper Jessa Moonfield, at the field hospital
    "epl_lh_volunteer":     (31, 46),    # Sergeant Marisol Reyes, the infirmary
    "epl_lh_quartermaster": (72, 43),    # Quartermaster Hasana Reed
    "epl_lh_knight":        (82, 38),    # Ser Roland Ashcombe, at the command tent
    "epl_lh_flight":        (80, 60),    # Flight Master Aldous Grey, at the perch
    "epl_lh_ranger":        (86, 46),    # Ranger Faelis Dawnreach
    "epl_lh_huntress":      (64, 56),    # Huntress Kaia Lindgren
    # ---- Crown Guard's people
    "epl_cg_captain":       (22, 66),    # Captain Joss Varden, at the palisade tent
    "epl_cg_corporal":      (32, 64),    # Corporal Ines Duarte, at the well
    "epl_cg_outrider":      (14, 60),    # Outrider Bram Tolliver, with the horses
    "epl_cg_widow":         (38, 70),    # Edda Marris
    "epl_cg_innkeeper":     (17, 46),    # Greta Lowe, in the hospital's kitchen now
    "epl_cg_flight":        (84, 60),    # Gwen Pike, with the bats that come in hurt
    "epl_cg_mycologist":    (60, 62),    # Dr. Sun Li, at her tent
    "epl_cg_gravewarden":   (70, 72),    # Gravewarden Osric Vey, at the cemetery
}
CHESTS = [(78, 22), (10, 34)]


def dress(L):
    A, B, F, V = L.p, L.b, L.f, L.v
    # ---- the gate
    V("pf_gate", 48, 79, 7)
    A("ek_signpost", 54, 70, 4)
    # ---- the chapel on its square
    B("lh_chapel", 48, 32, 13)
    A("ek_angel_statue", 38, 42, 6)
    A("ek_angel_statue", 58, 42, 6)
    A("ek_wayshrine", 30, 30, 7)
    A("ek_wayshrine", 66, 30, 7)
    # ---- the infirmary, west
    B("lh_field_hospital", 24, 43, 9)
    A("pf_field_tent", 34, 40, 5)
    A("ek_farm_cart", 14, 48, 3)
    # ---- the command row, east
    B("ek_trading_post", 72, 41, 9)
    B("lh_command_tent", 84, 36, 8)
    B("lh_flight_perch", 82, 58, 11)
    A("pf_weapon_rack", 66, 44, 3)
    # ---- Crown Guard's corner, by the gate
    B("cg_palisade_tent", 22, 64, 8)
    A("ek_farm_well", 30, 62, 4)
    B("ek_stable_block", 12, 58, 7)
    A("ek_haystack", 18, 56, 3)
    A("pf_field_tent", 60, 60, 5)                 # Dr. Sun Li's tent
    # ---- the cemetery
    for (x, y) in [(66, 74), (74, 75), (78, 66)]:
        A("gravestone_cluster", x, y, 3)
    A("ek_open_grave", 76, 70, 2)
    F("ek_cemetery_fence", 64, 68, 3)
    F("ek_cemetery_fence", 82, 66, 3)
    L.edge_canopy(seed=85, names=(("pl_dead_oak", 9), ("ek_dead_oak", 9), ("dead_pine_cluster", 8)))


AK.install(sys.modules[__name__])
