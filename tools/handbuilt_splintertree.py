"""
Hand-built Splintertree Post (90x70): the Horde's lumber stockade in southern Ashenvale.

TOWN ARCHETYPE: LUMBER STOCKADE ON A WAR YARD.  A fortified clearing cut out of the forest: the palisade gatehouse
and two watchtowers close the south; the road runs straight up the middle of a sawdust war yard to a plank dais in
front of the command tent.  Barracks and the forge sit west, the supply depot and the lumber yard east (felled logs,
tool racks), the inn and staging tents south-east - and the west flank is burned black, a reminder of why the post is
here.  (Razor Hill = hill fort, Crossroads = avenue cross, Taurajo = tipi ring, Ratchet = harbour, Astranaar = moon
pool terraces; this is the only plank-and-palisade military camp.)

HARD CONTRACTS (world/portal_manager.py)
  portal   (45,66) -> Ashenvale East (110,160);  arrival (45,64)
  NPC ids  referenced by data/quests/ashenvale.json; positions are written back by tools/sync_ashenvale_town_npcs.py
"""
import sys

from tools import ashenvale_town_kit as AK

KEY = "splintertree"
NAME = "Splintertree Post"
DESC = "A Horde outpost carved out of Ashenvale's southern reaches, staging ground against the demon incursion."
REGION = "Kalimdor - Eastern Forest"
W, H = 90, 70
BAKED_DIR = "assets/tiles/splintertree_post/baked"
PORTALS = {(45, 66): "Ashenvale East"}
ARRIVALS = [(45, 64)]
START = (45, 62)

ROADS = {
    "main": ([(45, 67), (45, 60), (46, 51), (45, 41)], 4.0),
    "west": ([(41, 47), (32, 45), (24, 43), (17, 42)], 3.2),
    "east": ([(50, 47), (60, 45), (70, 45), (79, 46)], 3.2),
    "se":   ([(47, 56), (54, 58), (61, 60)], 2.6),
    "sw":   ([(43, 56), (36, 57), (30, 58), (26, 59)], 2.6),
    "ne":   ([(52, 38), (60, 32), (66, 27)], 2.6),
    "lumber": ([(77, 45), (78, 38), (77, 31)], 2.6),
}
CLEARINGS = [(45, 40, 34, 24), (45, 60, 13, 9), (72, 24, 12, 10), (45, 21, 15, 10), (14, 56, 9, 8), (22, 36, 11, 9), (72, 58, 10, 8)]
DECKS = [(35.5, 54.5, 31.0, 37.5)]           # the command dais
DECK_MAT = "pl_horde"
PAVED_PATCHES = []
EXTRA_PATCHES = {
    "sawdust": [(45, 45, 14, 8, 1.9), (73, 25, 10, 7, 1.9), (22, 40, 6, 4, 1.4), (45, 35, 12, 5, 1.6)],
    "burned": [(12, 56, 9, 7, 1.0)],
    "scorch": [(11, 55, 6, 4, 1.0)],
    "root": [(45, 62, 10, 4, 0.6)],
}

NPC_POSITIONS = {
    "splintertree_commander": (45, 33),              # Overseer Gorada - on the dais
    "splintertree_barracks_sergeant": (20, 38),      # Krull - barracks door
    "splintertree_watch_sentry": (56, 62),           # Mokka - gate tower
    "splintertree_guard": (77, 28),                  # lumber yard gate
    "splintertree_quartermaster": (67, 43),          # Huln - supply depot
    "splintertree_scout": (12, 49),                  # Veyra - burned flank
    "splintertree_flight_master": (66, 29),          # roost at the end of the NE road
    "splintertree_war_mage": (51, 41),               # Grimtotem
    "splintertree_grunt": (30, 43),                  # Bloodfang
    "splintertree_interrogator": (58, 36),           # Vashj
    "splintertree_innkeeper": (66, 57),              # Rukka
}
FORGE = (27, 57)
EXTRA_NPC_XY = [FORGE]
CHESTS = [(34, 24), (78, 54)]


def dress(L):
    A, B, F, V = L.p, L.b, L.f, L.v
    # ---- the south gate: palisade gatehouse over the road, towers either side, banners
    V("orc_great_gatehouse", 45, 60, 9)
    B("watchtower", 35, 65, 13)
    B("watchtower", 55, 65, 13)
    A("vot_war_banner", 40, 63, 6)
    # ---- the war yard and the command dais
    B("command_war_tent", 45, 30, 14)
    A("vot_war_banner", 34, 36, 6)
    A("vot_war_banner", 56, 36, 6)
    F("vot_fire_pit", 45, 44, 2)
    A("rf_brazier", 38, 33, 4)
    A("ash_orc_trophy_pole", 39, 41, 6, solid="core")        # captured glaives, tattered banner: why the post is here
    A("rf_brazier", 52, 33, 4)
    # ---- west: barracks, forge, the burned flank
    B("orc_barracks_longhouse", 21, 36, 9)
    A("weapon_rack", 29, 38, 4)
    B("grand_forge", 26, 56, 9)
    A("rf_tool_rack", 33, 55, 3)
    A("ashx_burned_treehouse", 12, 61, 10)
    A("ashx_charred_trunks", 19, 53, 6)
    A("ashx_charred_trunks", 8, 57, 6)
    A("ashx_demon_ribcage", 17, 62, 4)
    # ---- east: supply depot and the lumber yard
    B("supply_depot", 67, 41, 11)
    A("rf_supply_crates", 65, 41, 3)
    B("orc_guard_post", 80, 27, 8)
    for (x, y) in [(66, 21), (77, 21)]:
        A("vot_fallen_log", x, y, 3, solid="core")
    A("ash_log_pile", 71, 20, 4)
    A("ash_sawbuck", 67, 25, 3)
    A("ash_felled_tree", 74, 24, 4, solid="core")
    A("vot_hide_rack", 69, 26, 4)
    A("rf_tool_rack", 79, 23, 3)
    A("gob_tarp_leanto", 71, 31, 6)
    # ---- south-east: inn, staging tents, well
    B("orc_mess_hall", 68, 55, 10)
    B("orc_smokehouse", 56, 53, 6)
    B("orc_quartermaster_post", 77, 61, 8)
    B("orc_supply_store", 69, 64, 7)
    A("vot_crate_stack", 60, 55, 3)
    # ---- the north flank: a roost for the flight master, trees
    A("vot_totem_pole", 62, 24, 7)
    A("vot_war_banner", 69, 29, 6)
    A("vot_fallen_log", 28, 22, 3)
    A("rf_supply_crates", 36, 24, 3)
    for (x, y) in [(40, 50), (58, 49), (30, 50), (60, 34)]:
        F("br_thorn_scrub", x, y, 3)
    L.edge_canopy(seed=77)


AK.install(sys.modules[__name__])
