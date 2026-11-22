"""
Hand-built The Pale Watch (88x72): the Order of the Pale Flame's forward town on the road under Hearthglen
(docs/plaguelands_towns_plan.md).

Kyle, 16 Nov 2026: "The Bulwark, The Pale Watch need to be seperate zones and stand alone towns", and "Bro you KNOW
this - when a town is made it's always a seperate map." It was seven people and two tents beside the King's Road. Now
it's a small walled town of its own, the last bed and the last flight before Hearthglen's walls, and North WPL had
neither.

    the gate ........... east (85,36): the King's Road, a short walk south of Hearthglen Fields
    the street ......... west from the gate to the captain's tent on the square
    the north row ...... the inn, the command tent, the watchtower that looks up the hill at Hearthglen
    the south side ..... the hawk roost, the medic's tents, the woodwright's shed, and the creek Oona fishes
    the back ........... the clerk's hall and the sister's shrine, as far from Hearthglen as the walls allow

It has its own innkeeper and roostkeeper: the first bed and the first flight anyone's had this close to Hearthglen.

HARD CONTRACTS (world/portal_manager.py)
  portal   (85,36) -> Western Plaguelands North (83,112);  arrival (82,36)
  NPC ids  wpln_pf_*, written by tools/sync_wpl_north_npcs.py from NPC_POSITIONS
"""
import sys

from tools import ashenvale_town_kit as AK

KEY = "pale_watch"
NAME = "The Pale Watch"
DESC = ("The Order of the Pale Flame's walled town on the King's Road, close enough to see Hearthglen's walls and be "
        "seen from them. The last bed and the last flight before the Crusade.")
REGION = "Eastern Kingdoms - Lordaeron"
W, H = 88, 72
BAKED_DIR = "assets/tiles/plaguelands/baked_pale_watch"
SHEET = "wpl_north"
PORTALS = {(85, 36): "Western Plaguelands North"}
ARRIVALS = [(82, 36)]
START = (80, 36)

SUBZONES = [   # 22 Nov 2026, for the townsfolk
    ("The Watch Square", 34, 26, 32, 14),
    ("The Inn Row", 16, 22, 18, 14),
    ("The Back", 4, 10, 16, 28),
    ("The South Side", 40, 42, 44, 14),
    ("The Creek Bank", 4, 52, 70, 14),
]

ROADS = {
    "street": ([(86, 36), (72, 36), (58, 36), (44, 36), (30, 37), (18, 38)], 3.6),
    "inn":    ([(26, 36), (26, 31)], 2.6),
    "tower":  ([(62, 36), (62, 30)], 2.4),
    "south":  ([(44, 36), (44, 46), (52, 52)], 2.6),
    "back":   ([(18, 38), (14, 26), (16, 18)], 2.4),
}
STREAMS = {"creek": ([(2, 60), (14, 58), (28, 62), (40, 64), (54, 62), (66, 66), (80, 70), (88, 70)], 2.4)}
STREAM_SHRINK = 1.0
POOLS = []
PLAZA = (44, 36, 8.0, 4.5)
PAVED_PATCHES = [(26, 32, 4, 2.5), (82, 36, 4, 3)]
CLEARINGS = [(44, 38, 40, 28), (16, 22, 12, 10), (84, 36, 6, 6), (40, 62, 34, 8)]
DECKS = []
CLEARING_GRASS = False
DECK_PAINT = False
GRADE = (1.0, 1.05)

NPC_POSITIONS = {
    "wpln_pf_watch_captain": (44, 32),    # Watch Captain Lena Fischer, at the command tent on the square
    "wpln_pf_scout":         (65, 32),    # Scout Mateo Brandt, under the watchtower
    "wpln_pf_innkeeper":     (26, 32),    # Innkeeper Beatriz Couto
    "wpln_pf_roostkeeper":   (64, 52),    # Roostkeeper Liam Doherty and the hawks
    "wpln_pf_field_medic":   (30, 48),    # Field Medic Noah Kowal, at the tents
    "wpln_pf_woodwright":    (76, 50),    # Woodwright Jonah Lind, at his shed
    "wpln_pf_angler":        (40, 59),    # Oona Byrne, on the creek bank
    "wpln_pf_clerk":         (20, 20),    # Clerk Wendel Ashby, at the hall
    "wpln_pf_sister":        (10, 30),    # Sister Amalie Crane, at the shrine
}
CHESTS = [(70, 18), (8, 48)]


def dress(L):
    A, B, F, V = L.p, L.b, L.f, L.v
    # ---- the gate and the walls
    V("pf_gate", 84, 32, 8)
    A("ek_signpost", 78, 41, 4)
    for x in (72, 52):
        A("pf_banner", x, 41, 5)
    # ---- the north row
    B("ek_village_inn", 26, 30, 10)
    B("ek_command_tent", 44, 30, 9)
    B("ek_border_watchtower", 62, 29, 11)
    A("pf_weapon_rack", 52, 31, 3)
    A("pf_weapon_rack", 36, 31, 3)
    # ---- the south side
    B("lh_flight_perch", 64, 50, 10)
    A("pf_field_tent", 26, 46, 5)
    A("pf_field_tent", 36, 50, 5)
    B("ek_sawmill_shed", 76, 48, 7)
    A("ek_farm_cart", 70, 54, 3)
    B("pf_training_yard", 52, 48, 5)
    # ---- the back: the hall and the shrine
    B("pf_hall", 20, 18, 8)
    B("ek_wayshrine", 10, 28, 7)
    A("pf_banner", 28, 22, 5)
    # ---- what they can see from the tower: Hearthglen's pyres on the hill, past the north wall
    V("sc_pyre", 70, 8, 5)
    V("sc_pyre", 52, 6, 5)
    L.edge_canopy(seed=83, names=(("pl_dead_oak", 9), ("pl_blight_pine", 9), ("dead_pine_cluster", 8)))


AK.install(sys.modules[__name__])
