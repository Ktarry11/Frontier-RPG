"""
Hand-built Camp Mojache (124x96): the tauren camp in the High Wilderness, Feralas, 44-46 (docs/feralas_brief.md).

Kyle, 19 Nov 2026: Mojache is "grown with refugees": the tauren who walked out of Mulgore came south through the Needles
and the camp took them in. It answers to Elder Longtread at Camp Taurajo. A town is always its own map (Kyle, 16 Nov
2026), with an inn and the flight path for this part of Feralas.

ORIENTATION FOLLOWS THE OVERWORLD. The High Wilderness's door to the camp (160,86) stands on the north side of the arm
road, so the camp lies north of it: the gate is on the south edge and the camp climbs north into the clearing.

    the gate (62,95), south <- The High Wilderness (160,86)
    the old camp in the middle: Mojache's great totem in a ring of lodges, the chieftain's lodge north of it
    the inn and the wind rider roost either side of the gate road, where travellers come in
    the trades on the east side: the forge, the hide frames, the herbalist
    the refugees' quarter in the north-west: lean-tos and patched tents put up in a hurry, the memorial pole
    the kodo pen and the hunters' ground in the north-east

THE ART: built before Kyle's Feralas sheets (Kyle, 19 Nov 2026: "Build without art for now"), from the tauren pieces
already in the game (Camp Taurajo's, Thunder Bluff's in Moonglade, the Aspen camp's). docs/feralas_art_prompts.md
sheet 3 is Mojache's own set.

HARD CONTRACTS (world/portal_manager.py)
  portal   (62,95) <-> The High Wilderness (160,86): you arrive at (62,91) coming in and (160,89) going out
  NPC ids  moj_*, ct_mojache, pt_moj_*: written by tools/build_feralas_towns.py from NPC_POSITIONS
"""
import sys

from tools import ashenvale_town_kit as AK

KEY = "camp_mojache"
NAME = "Camp Mojache"
DESC = ("The tauren camp in Feralas's giant forest, twice the size it was. The ones who walked out of Mulgore came "
        "here, and Mojache took every one of them in.")
REGION = "Kalimdor - Feralas"
W, H = 124, 96
BAKED_DIR = "assets/tiles/feralas/baked_mojache"
SHEET = "feralas_mojache"
PORTALS = {(62, 95): "The High Wilderness"}
ARRIVALS = [(62, 91)]
START = (62, 88)

ROADS = {
    "gate":   ([(62, 96), (62, 80), (62, 62)], 3.4),
    # the ring round the great totem
    "ring":   ([(62, 62), (78, 56), (82, 44), (74, 32), (62, 28), (48, 32), (42, 44), (46, 56), (62, 62)], 3.0),
    "trades": ([(82, 44), (96, 46), (108, 50)], 2.6),
    "refuge": ([(48, 32), (36, 24), (24, 22)], 2.6),
    "pen":    ([(74, 32), (88, 22), (100, 18)], 2.4),
    "inn":    ([(62, 74), (46, 74), (36, 74)], 2.6),
    "roost":  ([(62, 74), (80, 74), (90, 72)], 2.6),
}
STREAMS = {"creek": ([(124, 64), (112, 70), (102, 80), (98, 96)], 1.6)}
POOLS = []
PLAZA = (62, 44, 9, 7)
PAVED_PATCHES = []
CLEARINGS = [(62, 48, 50, 34), (62, 84, 14, 12), (24, 24, 16, 12), (100, 20, 16, 12), (104, 52, 14, 12),
             (36, 74, 12, 8), (90, 72, 12, 8)]
ROCKS = [(8, 60, 5, 5), (116, 30, 4, 6)]
DECKS = []
CLEARING_GRASS = True
GRADE = None
EXTRA_PATCHES = {"satyr": [(24, 24, 14, 9, 1.2), (100, 20, 12, 8, 1.0)], "mud": [(62, 44, 18, 13, 0.9)],
                 "scorch": [(98, 50, 3, 2, 1.0)]}

NPC_POSITIONS = {
    # the gate and the travellers' ground
    "moj_innkeeper":      (38, 77),     # Innkeeper Greul, the inn west of the gate road
    "moj_flight_master":  (88, 76),     # Wind Rider Master Shyn, the roost east of it
    "moj_gate_brave":     (57, 88),     # a brave at the gate
    # the old camp, round the great totem
    "moj_chieftain":      (62, 26),     # Chieftain Ahanu Swiftstrider, at her lodge
    "moj_hadoken":        (78, 40),     # Hadoken Swiftstrider, the camp's hunter
    "moj_elder_nayeli":   (46, 48),     # Elder Nayeli Cloudhoof, who walked out of Mulgore
    "moj_krueg":          (70, 58),     # Krueg Skullsplitter, Orgrimmar's man
    "ct_mojache":         (52, 60),     # the class trainer
    # the refugees' quarter
    "moj_brann":          (28, 30),     # Brann Tallgrass and his list
    # the trades
    "moj_orwin":          (96, 40),     # Orwin Gizzmick, the trader
    "moj_smith":          (106, 56),    # the forge
    "pt_moj_hide":        (112, 46),    # skinning and leather, by the hide frames
    "pt_moj_herbs":       (92, 54),     # herbs and alchemy
    "moj_provisioner":    (46, 70),     # by the inn
}
CHESTS = []


def dress(L):
    """Kyle's Camp Mojache sheet (docs/feralas_art_prompts.md sheet 3, 19 Nov 2026); Camp Taurajo's and Moonglade's
    tauren pieces stood in before it. The collapsed lodge stays: it's the refugees' shelter."""
    A, B, V = L.p, L.b, L.v
    # ---- the gate and the travellers' ground
    B("moj_gate", 62, 89, 7, solid=False, road_ok=True)   # north of the arrival (62,91), so it stands on the road
    B("moj_inn", 34, 72, 10)
    B("moj_windrider_roost", 92, 70, 11)
    A("tau_hitching_post", 70, 84, 3)
    A("ash_horde_signpost", 68, 80, 4)
    B("moj_watchtower", 80, 88, 7, nudge=6)
    B("moj_lantern_pole", 56, 84, 4)
    B("moj_firewood", 22, 76, 3)
    # ---- the old camp: the great totem in the middle, the lodges round it
    B("moj_great_totem", 62, 46, 9)
    B("moj_spirit_fire", 62, 52, 3)
    B("moj_chief_lodge", 62, 22, 10)
    B("moj_tent_lodge", 80, 34, 9)
    B("moj_tent_medium", 44, 38, 8)
    B("moj_trainer_shelter", 46, 58, 7)
    B("moj_tent_lodge", 80, 56, 8)
    B("moj_totem_pair", 52, 30, 6)
    B("moj_totem_pair", 72, 30, 6)
    # ---- the refugees' quarter: patched tents, bedrolls, the memorial pole for Thunder Bluff
    B("moj_memorial_pole", 30, 36, 7)
    B("moj_tent_medium", 18, 22, 6)
    B("moj_tent_small", 32, 18, 6)
    B("moj_lean_to", 14, 32, 5)
    B("moj_tent_small", 24, 14, 5)
    A("tau_lodge_collapsed", 40, 16, 6)
    B("moj_cookfire", 22, 28, 3)
    B("moj_bedrolls", 34, 26, 3)
    # ---- the trades
    B("moj_trader_stall", 98, 34, 7)
    B("moj_baskets", 106, 30, 3)
    B("moj_leather_frame", 112, 42, 4)
    B("moj_hide_frame", 116, 54, 4)
    B("moj_forge", 104, 64, 7)
    B("moj_herbalist_tent", 90, 50, 7)
    B("moj_drum_circle", 70, 66, 3)
    B("moj_well", 54, 70, 4)
    # ---- the kodo pen and the hunters' ground
    B("moj_kodo_pen", 100, 14, 6)
    B("moj_trophy_rack", 88, 18, 4)
    B("moj_travois", 108, 24, 3)
    L.edge_canopy(seed=4411, names=(("fe_giant_tree", 12), ("fe_moss_curtain_tree", 10), ("fe_vine_giant", 11)))


AK.install(sys.modules[__name__])

#: the districts, where the townsfolk live (Kyle, 22 Nov 2026: "ensure ALL towns are actually populated"; names made up to
#: fit). (key, x, y, w, h, display name)
SUBZONES = [
    ('Camp Mojache', 0, 0, 124, 96, None),
    ('The Old Camp', 4, 6, 36, 36, None),
    ("The Chief's Lodge", 40, 6, 44, 26, None),
    ("The Traders' Ring", 86, 6, 38, 38, None),
    ('The Great Totem', 42, 34, 40, 22, None),
    ('The Craft Frames', 86, 44, 38, 28, None),
    ('The Inn Fire', 10, 58, 42, 28, None),
    ('The Drum Circle', 54, 56, 30, 22, None),
    ('The Gate', 44, 78, 40, 18, None),
]
