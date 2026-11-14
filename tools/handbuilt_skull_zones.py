"""The hidden open-world maps (world/hidden_zones.py, kind "skull").

SPOILERS. Kyle, 14 Nov 2026: "I don't want to see as I want these to be secrets." Nothing here
says how to find them; the doors that lead here are picked by tools/build_secrets.py.

The brief, in Kyle's words: "For hidden zones, they can be new NEW transition zones too. These new
zones will still have the level range but maybe a skull next to them", "when I say new zones. I
mean actually new maps", "Open world will be 2.5x hp and 2.5x damage", "Quests can be in the zone,
but max of like 3 or 4....they're not quest hubs but they CAN have elite quests. I want the wonder
of exploring....and for good measure....I WANT to be rewarded for exploring."

Each is one painted map (playbook section 3), built from a SPEC below by the same recipe as Echo
Isles: analytic landforms -> tile grid AND painting from the same functions, so they can't drift.

  The Saltgrave        grey sandbars and drowned barrows in a cold sea
  The Glasswaste       a sealed red canyon where the sand has been fired to glass
  The Weeping Pines    a dead pine wood round a black mere, in a fog that never lifts

Every map's way out is its one portal; arriving puts you two tiles north of it.
"""
import math
import os

import numpy as np
from PIL import Image

from world.tilemap import Tilemap

DP = "assets/tiles/dungeon_props/"
BAKED = "assets/tiles/hidden/{}/baked"
HF = "assets/tiles/haunted_forest/props/"
ASHX = "assets/tiles/ashenvale_corruption/props/"
STV = "assets/tiles/stranglethorn/props/"
CP = "assets/tiles/coastal_props/"
VEG = "assets/tiles/vegetation/"
NG = "assets/tiles/naga_dungeon/"


def wob(gx, gy, ph=0.0):
    return (0.55 * np.sin(gx * 0.21 + gy * 0.13 + ph) + 0.35 * np.sin(gx * 0.47 - gy * 0.31 + 1.7 * ph)
            + 0.22 * np.sin(-gx * 0.83 + gy * 0.71 + 0.6 * ph))


def ell(gx, gy, cx, cy, rx, ry, rot=0.0):
    dx, dy = gx - cx, gy - cy
    if rot:
        r = math.radians(rot)
        c, s = math.cos(r), math.sin(r)
        dx, dy = c * dx + s * dy, -s * dx + c * dy
    return (1.0 - np.sqrt((dx / rx) ** 2 + (dy / ry) ** 2)) * min(rx, ry)


def seg_dist(gx, gy, pts):
    best = np.full(np.shape(gx), 99.0)
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        dx, dy = bx - ax, by - ay
        t = np.clip(((gx - ax) * dx + (gy - ay) * dy) / (dx * dx + dy * dy or 1), 0.0, 1.0)
        best = np.minimum(best, np.hypot(gx - ax - t * dx, gy - ay - t * dy))
    return best


# ===================================================================================== SPECS
SPECS = {}

# THE SALTGRAVE. Sandbars in a grey sea, three barrows the sea came over, and a fourth, the King's,
# out on its own to the north. Shallows join them; everywhere else is cold deep water.
SPECS["The Saltgrave"] = dict(
    slug="saltgrave", W=100, H=86, region="Arathi East", seed=931,
    desc="A drowned barrow-field out past the last island: grey sand, grey water, and the old dead "
         "of the highlands, who never stopped guarding what was buried with them.",
    mode="islands", shore_w=3.0,
    land=[(50, 74, 15, 6, 0), (24, 54, 12, 8, 15), (78, 50, 12, 8, -20), (49, 42, 9, 5, 0),
          (51, 16, 14, 9, 5), (14, 26, 5, 4, 0), (86, 24, 6, 4, 0)],
    flats=[(50, 60, 4.5, 9), (36, 48, 9, 4.5), (64, 46, 9, 4.5), (50, 30, 4.5, 9),
           (19, 38, 4, 9), (82, 36, 4, 9)],
    rocks=[(22, 50, 3.4, 2.6), (80, 46, 3.2, 2.6), (51, 12, 4.2, 3.0), (60, 20, 1.8, 1.6),
           (40, 18, 1.8, 1.6)],
    roads=[],
    portal=(50, 78),
    giver=("hz_saltgrave_maud", (43, 73)),
    subzones=[("The Landing Bar", 34, 66, 32, 16), ("The West Barrow", 10, 44, 28, 20),
              ("The East Barrow", 64, 40, 28, 20), ("The Middle Bar", 38, 36, 22, 12),
              ("The King's Barrow", 34, 4, 34, 24)],
    materials={"land": ("echo_isles/materials/echo_wetsand", None),
               "grass": ("hillsbrad/materials/hb_dry", None),
               "barrow": ("hillsbrad/materials/hb_rocky", "hillsbrad/materials/hb_moss_rock"),
               "water_s": ("hillsbrad/materials/hb_sea_shallow", None),
               "water_d": ("hillsbrad/materials/hb_sea_deep", None),
               "rock": ("hillsbrad/materials/hb_cliff_a", "hillsbrad/materials/hb_cliff_b")},
    regions={"grass": [(24, 56, 8, 5), (78, 52, 8, 5), (51, 19, 10, 6)],
             "barrow": [(22, 51, 6, 4), (80, 47, 6, 4), (51, 13, 7, 5)]},
    tint=(0.86, 0.90, 0.95), dark=0.10,
    props=[
        ("stv_bleached_log", STV, 44, 76, 2, False), ("stv_fish_bones", STV, 57, 75, 2, False),
        ("stv_driftwood", STV, 38, 73, 2, False), ("skull_pile", DP, 26, 57, 3, False),
        ("sarcophagus", DP, 17, 55, 3, "core"), ("bbc_skull_pile", DP, 75, 54, 3, False),
        ("sarcophagus", DP, 84, 52, 3, "core"), ("stv_broken_mast", STV, 70, 48, 4, "core"),
        ("grotto_pirate_skeletons", DP, 46, 43, 3, False), ("stv_chain_heap", STV, 53, 43, 2, False),
        ("crypt_mausoleum", HF, 51, 22, 5, "core"), ("skull_pile", DP, 44, 21, 3, False),
        ("skull_pile", DP, 58, 21, 3, False), ("stv_shells", STV, 14, 27, 2, False),
        ("stv_boat_wreck", STV, 86, 25, 3, "core"),
    ],
)

# THE GLASSWASTE. A canyon the Kolkar never went into: whatever burned here burned hot enough to
# turn the sand to glass. Red walls all round, mesas inside, and fire still walking about.
SPECS["The Glasswaste"] = dict(
    slug="glasswaste", W=96, H=80, region="Durotar", seed=932,
    desc="A sealed red canyon behind Durotar's cliffs, where something burned so hot the sand "
         "turned to glass. It hasn't finished burning.",
    mode="canyon", shore_w=1.5,
    lakes=[], flats=[],
    open=[(48, 70, 9, 6, 0), (30, 50, 16, 11, 20), (64, 46, 15, 10, -15), (50, 30, 7, 5, 0),
          (58, 14, 20, 8, 5), (18, 27, 8, 7, 0), (82, 26, 7, 9, 10)],
    passes=[([(48, 70), (40, 60), (32, 52)], 6), ([(48, 70), (58, 58), (64, 48)], 5),
            ([(30, 50), (28, 36), (20, 28)], 5), ([(64, 46), (56, 34), (52, 26), (56, 16)], 6),
            ([(64, 46), (78, 36), (82, 26), (74, 14)], 5)],
    rocks=[(30, 48, 4, 3), (66, 44, 3, 4), (58, 14, 3, 2), (24, 56, 2, 2)],
    roads=[([(48, 74), (44, 62), (36, 52), (30, 40), (40, 32), (52, 26), (58, 16)], 2.2)],
    portal=(48, 76),
    giver=("hz_glasswaste_durek", (53, 70)),
    subzones=[("The Scorched Mouth", 34, 62, 28, 16), ("The Shard Fields", 8, 30, 36, 30),
              ("The Kiln Rise", 52, 30, 38, 30), ("Blister's Hollow", 40, 4, 40, 22)],
    materials={"land": ("vot_cluster/vot_clay_a", "vot_cluster/vot_clay_pebbles"),
               "glass": ("vot_cluster/vot_cinder", None),
               "dune": ("vot_cluster/vot_dune", None),
               "bone": ("vot_cluster/vot_bonesand", None),
               "road": ("vot_cluster/vot_hardpan", None),
               "water_s": ("vot_cluster/vot_water_shallow", None),
               "water_d": ("vot_cluster/vot_water_deep", None),
               "rock": ("vot_cluster/vot_cliff_a", None)},
    regions={"glass": [(24, 44, 14, 12), (60, 12, 14, 8), (76, 44, 10, 9)],
             "dune": [(44, 56, 12, 8)], "bone": [(60, 12, 6, 4)]},
    tint=(1.04, 0.92, 0.86), dark=0.06,
    props=[
        ("vot_dead_tree", DP, 40, 70, 4, "core"), ("vot_beast_ribcage", DP, 58, 66, 3, False),
        ("rf_lava_fissure", DP, 22, 40, 3, False), ("rf_obsidian_spikes", DP, 16, 52, 3, "core"),
        ("rf_lava_fissure", DP, 30, 50, 3, False), ("bbc_obsidian_spikes", DP, 66, 36, 3, "core"),
        ("rf_steam_vent", DP, 78, 46, 3, False), ("vot_mesa_pillar", DP, 58, 44, 5, "core"),
        ("rf_golem_husk", DP, 74, 28, 4, "core"), ("vot_beast_ribcage", DP, 56, 10, 3, False),
        ("rf_lava_pool", DP, 66, 12, 4, False), ("vot_scorpid_burrow", DP, 46, 18, 3, False),
        ("bbc_red_stalagmites", DP, 36, 22, 4, "core"),
    ],
)

# THE WEEPING PINES. A pine wood that died standing up, round a mere so still it shows the trees
# that aren't there any more. Fog, and something in the water that weeps.
SPECS["The Weeping Pines"] = dict(
    slug="weeping_pines", W=96, H=86, region="Silverpine North", seed=933,
    desc="A dead pine wood round a black mere, hidden in the folds of Silverpine. The fog never "
         "lifts, and on still nights something in the water weeps.",
    mode="canyon", shore_w=2.2,
    lakes=[(50, 40, 12, 8, 10), (72, 58, 4.5, 3, 0)],
    flats=[],
    open=[(48, 74, 12, 8, 0), (28, 52, 13, 16, 10), (50, 40, 21, 15, 10), (72, 58, 11, 9, -10),
          (28, 18, 12, 8, -15), (58, 14, 17, 8, 5), (82, 32, 7, 10, 0), (14, 34, 6, 7, 0)],
    passes=[([(48, 74), (36, 64), (30, 56)], 6), ([(48, 74), (62, 66), (70, 60)], 5),
            ([(28, 40), (26, 28)], 6), ([(38, 18), (48, 14)], 6), ([(70, 18), (80, 26)], 5),
            ([(82, 40), (78, 50)], 5), ([(20, 38), (16, 36)], 4)],
    rocks=[(22, 22, 3, 2), (86, 30, 2, 3)],
    roads=[([(48, 80), (46, 70), (34, 60), (28, 44), (28, 28), (40, 16), (58, 14), (74, 20), (82, 32)], 2.0)],
    portal=(48, 82),
    giver=("hz_pines_ilsabet", (55, 76)),
    subzones=[("The Fogbound Track", 30, 64, 36, 20), ("The Weeping Mere", 32, 26, 38, 30),
              ("The Hanging Wood", 8, 28, 24, 36), ("The Stillwater Shrine", 40, 6, 40, 20),
              ("The Drowned Copse", 60, 46, 26, 20)],
    materials={"land": ("silverpine/materials/sp_needle_mulch", "silverpine/materials/sp_pine_floor"),
               "moss": ("silverpine/materials/sp_cursed_ground", None),
               "bog": ("silverpine/materials/sp_bog_mud", "silverpine/materials/sp_peat"),
               "road": ("silverpine/materials/sp_gravel", None),
               "water_s": ("silverpine/materials/sp_pool_shallow", None),
               "water_d": ("silverpine/materials/sp_pool_deep", None),
               "rock": ("silverpine/materials/sp_cliff_a", "silverpine/materials/sp_rock_wall")},
    regions={"moss": [(20, 44, 12, 18), (60, 14, 14, 7)], "bog": [(52, 40, 20, 14), (70, 56, 10, 7)]},
    tint=(0.84, 0.90, 0.92), dark=0.14,
    props=[
        ("dead_pine_cluster", HF, 30, 74, 6, "core"), ("dead_pine_cluster", HF, 64, 72, 6, "core"),
        ("dead_pine_cluster", HF, 14, 36, 6, "core"), ("dead_pine_cluster", HF, 22, 54, 6, "core"),
        ("dead_pine_cluster", HF, 82, 46, 6, "core"), ("dead_pine_cluster", HF, 30, 14, 6, "core"),
        ("dead_pine_cluster", HF, 74, 10, 6, "core"), ("dead_pine_cluster", HF, 86, 60, 6, "core"),
        ("twisted_root_arch", HF, 26, 32, 5, "core"), ("bog_reeds_cluster", HF, 38, 44, 3, False),
        ("bog_reeds_cluster", HF, 62, 34, 3, False), ("bog_reeds_cluster", HF, 66, 60, 3, False),
        ("ashx_spirit_brazier", ASHX, 44, 14, 4, "core"), ("ashx_spirit_brazier", ASHX, 58, 14, 4, "core"),
        ("burned_house_ruin", HF, 74, 64, 6, "core"), ("crypt_mausoleum", HF, 51, 11, 5, "core"),
        ("vot_fallen_log", DP, 40, 62, 2, False),
        # the wood itself: dead pines standing in clumps all round the mere
        ("dead_pine_cluster", HF, 20, 46, 6, "core"), ("dead_pine_cluster", HF, 36, 50, 5, "core"),
        ("dead_pine_cluster", HF, 18, 62, 5, "core"), ("dead_pine_cluster", HF, 40, 30, 5, "core"),
        ("dead_pine_cluster", HF, 62, 28, 5, "core"), ("dead_pine_cluster", HF, 66, 48, 5, "core"),
        ("dead_pine_cluster", HF, 78, 62, 5, "core"), ("dead_pine_cluster", HF, 56, 76, 5, "core"),
        ("dead_pine_cluster", HF, 38, 78, 5, "core"), ("dead_pine_cluster", HF, 22, 22, 5, "core"),
        ("dead_pine_cluster", HF, 66, 14, 5, "core"), ("dead_pine_cluster", HF, 84, 38, 5, "core"),
        ("dead_pine_cluster", HF, 12, 34, 5, "core"), ("dead_pine_cluster", HF, 34, 18, 5, "core"),
    ],
)


# THE TANGLEWOOD SHOALS. Reached from a secret island off Echo Isles (Kyle asked for this one by
# shape: "first skull zone is from a hidden island off the coast....within that NEW skull zone, the
# frontier zone entrance is hidden behind a massive tree"). Mangrove islets in green water round one
# big island, and on its north shore, backed against the rock, a tree older than the Darkspear.
EP = "assets/tiles/echo_isles/props/"
SPECS["The Tanglewood Shoals"] = dict(
    slug="tanglewood_shoals", W=104, H=90, region="Echo Isles", seed=934,
    desc="Mangrove islets far out past the Echo Isles, in water gone green with sap. The trolls "
         "have a word for this place, and they don't say it.",
    mode="islands", shore_w=3.0,
    land=[(52, 80, 12, 6, 0), (52, 40, 22, 15, 0), (20, 54, 10, 7, 10), (86, 48, 10, 8, -10),
          (22, 18, 9, 6, 0), (84, 16, 9, 6, 0)],
    flats=[(52, 66, 4.5, 9), (35, 50, 8, 4.5), (70, 46, 8, 4.5), (21, 35, 4.5, 10), (85, 31, 4.5, 10)],
    rocks=[(52, 20, 11, 5), (38, 30, 3, 2.5), (68, 31, 3, 2.5)],
    roads=[],
    portal=(52, 84),
    giver=("hz_tangle_kojira", (46, 78)),
    great_tree=("stv_tree_buttress", STV, 52, 34, 13),
    tree_leads_to="The World-Root Hollow",
    subzones=[("The Mangrove Landing", 38, 72, 28, 16), ("The Rootward Isle", 28, 22, 48, 36),
              ("The West Tangle", 8, 44, 24, 20), ("The East Tangle", 74, 38, 24, 20),
              ("The Northern Shoals", 10, 8, 86, 18)],
    materials={"land": ("echo_isles/materials/echo_jungle_a", "echo_isles/materials/echo_jungle_b"),
               "sand": ("echo_isles/materials/echo_wetsand", None),
               "mud": ("echo_isles/materials/vot_mudshore", None),
               "water_s": ("vot_cluster/vot_water_shallow", None),
               "water_d": ("vot_cluster/vot_water_deep", None),
               "rock": ("echo_isles/materials/echo_rock_a", "echo_isles/materials/echo_rock_b")},
    regions={"sand": [(52, 80, 12, 6)], "mud": [(20, 54, 9, 6), (86, 48, 9, 7), (52, 50, 12, 5)]},
    tint=(0.82, 0.98, 0.86), dark=0.12,
    props=[
        ("stv_mangrove", STV, 40, 80, 5, "core"), ("stv_mangrove", STV, 63, 78, 5, "core"),
        ("stv_palm_young", STV, 58, 82, 4, "core"), ("stv_fern_clump", STV, 44, 82, 2, False),
        ("stv_tree_vined", STV, 36, 44, 7, "core"), ("stv_tree_vined", STV, 68, 46, 7, "core"),
        ("stv_tree_strangler", STV, 40, 52, 6, "core"), ("stv_tree_strangler", STV, 66, 52, 6, "core"),
        ("stv_root_tangle", STV, 46, 47, 3, False), ("stv_root_tangle", STV, 60, 44, 3, False),
        ("stv_troll_idol_head", STV, 52, 52, 4, "core"), ("stv_moss_curtain", STV, 34, 38, 4, False),
        ("stv_mangrove", STV, 16, 56, 5, "core"), ("stv_mangrove", STV, 24, 50, 5, "core"),
        ("stv_lily_pads", STV, 27, 58, 2, False), ("stv_mangrove", STV, 90, 50, 5, "core"),
        ("stv_tree_leaning", STV, 82, 45, 6, "core"), ("stv_stump_fungus", STV, 88, 53, 2, False),
        ("stv_tree_cluster", STV, 20, 18, 6, "core"), ("stv_troll_obelisk", STV, 26, 16, 4, "core"),
        ("stv_tree_cluster", STV, 86, 16, 6, "core"), ("stv_turtle_shell", STV, 80, 18, 2, False),
    ],
)


# THE DROWNED IDOLS. A lagoon the jungle closed over: the Gurubashi sank their old gods here when
# the new ones took over, and the idols are still looking up out of the water.
SFP = "assets/tiles/shimmering_flats/props/"
SPECS["The Drowned Idols"] = dict(
    slug="drowned_idols", W=100, H=88, region="Northern Stranglethorn", seed=935,
    desc="A jungle lagoon behind the cliffs of Stranglethorn, where the Gurubashi drowned the gods "
         "they stopped praying to. The gods haven't stopped listening.",
    mode="islands", shore_w=3.2,
    land=[(50, 78, 13, 6, 0), (24, 56, 12, 9, 20), (76, 58, 12, 9, -20), (50, 40, 10, 7, 0),
          (24, 22, 11, 8, -10), (76, 22, 11, 8, 10), (50, 12, 8, 5, 0)],
    flats=[(37, 68, 9, 4.5), (63, 68, 9, 4.5), (36, 47, 8, 4.5), (64, 47, 8, 4.5), (24, 39, 4.5, 9),
           (76, 39, 4.5, 9), (37, 16, 8, 4), (63, 16, 8, 4)],
    rocks=[(24, 52, 3, 2.5), (76, 54, 3, 2.5), (50, 9, 4, 2.6)],
    roads=[],
    portal=(50, 82),
    giver=("hz_idols_fizzle", (44, 77)),
    subzones=[("The Idol Landing", 36, 70, 28, 16), ("The Western Idols", 10, 46, 28, 20),
              ("The Eastern Idols", 62, 48, 28, 20), ("The Sunken Altar", 38, 32, 24, 16),
              ("The Jade Isles", 10, 12, 80, 20), ("The Last God's Isle", 40, 4, 20, 14)],
    materials={"land": ("stranglethorn/materials/stv_jungle", "stranglethorn/materials/stv_jungle_b"),
               "mud": ("stranglethorn/materials/stv_mud", None),
               "ruin": ("stranglethorn/materials/stv_ruin", None),
               "water_s": ("stranglethorn/materials/stv_sea_s", None),
               "water_d": ("stranglethorn/materials/stv_sea_d", None),
               "rock": ("stranglethorn/materials/stv_cliff_a", "stranglethorn/materials/stv_cliff_b")},
    regions={"ruin": [(50, 40, 7, 5), (50, 12, 6, 4), (24, 56, 5, 4), (76, 58, 5, 4)],
             "mud": [(50, 78, 10, 4)]},
    tint=(0.86, 0.96, 0.90), dark=0.12,
    props=[
        ("stv_troll_idol_head", STV, 24, 60, 5, "core"), ("stv_troll_idol_head", STV, 76, 62, 5, "core"),
        ("stv_troll_serpent_head", STV, 50, 44, 5, "core"), ("stv_troll_obelisk", STV, 44, 40, 5, "core"),
        ("stv_troll_obelisk", STV, 56, 40, 5, "core"), ("stv_troll_column_fallen", STV, 30, 24, 3, False),
        ("stv_troll_column", STV, 18, 20, 5, "core"), ("stv_troll_column", STV, 82, 20, 5, "core"),
        ("stv_troll_altar", STV, 50, 14, 4, "core"), ("stv_mangrove", STV, 40, 80, 5, "core"),
        ("stv_tree_vined", STV, 60, 78, 6, "core"), ("stv_lily_pads", STV, 36, 66, 2, False),
        ("stv_troll_skull_pile", STV, 72, 24, 3, False), ("stv_tree_strangler", STV, 28, 50, 6, "core"),
        ("stv_tree_strangler", STV, 72, 52, 6, "core"), ("stv_moss_curtain", STV, 20, 54, 4, False),
    ],
)

# THE BURIED CARAVAN. A whole trading caravan, and the town it was going to, under the dunes in a
# bowl of sandstone. The sand moves at night. Things walk out of it.
SPECS["The Buried Caravan"] = dict(
    slug="buried_caravan", W=100, H=84, region="Northern Tanaris", seed=936,
    desc="A bowl of sandstone off the Tanaris trade road where a whole caravan, and the town it was "
         "bound for, went under the dunes in a single night. They're still trying to arrive.",
    mode="canyon", shore_w=1.5,
    lakes=[], flats=[],
    open=[(50, 74, 12, 7, 0), (28, 52, 15, 12, 15), (70, 50, 16, 11, -10), (50, 30, 18, 10, 0),
          (20, 22, 9, 8, 0), (82, 24, 9, 9, 0), (50, 10, 10, 5, 0)],
    passes=[([(50, 74), (38, 62), (30, 54)], 6), ([(50, 74), (62, 62), (70, 52)], 6),
            ([(30, 46), (40, 34)], 6), ([(70, 44), (60, 34)], 6), ([(34, 30), (22, 24)], 5),
            ([(66, 30), (80, 26)], 5), ([(50, 22), (50, 12)], 6)],
    rocks=[(26, 50, 3, 3), (72, 48, 4, 3), (50, 30, 3, 2)],
    roads=[([(50, 78), (48, 66), (36, 56), (40, 40), (50, 30), (50, 12)], 2.4)],
    portal=(50, 80),
    giver=("hz_caravan_rizzo", (56, 75)),
    subzones=[("The Last Dune", 36, 66, 28, 16), ("The Wagon Graves", 12, 40, 32, 24),
              ("The Drowned Market", 54, 38, 34, 24), ("The Buried Gate", 32, 20, 36, 20),
              ("The Caravan Master's Rest", 38, 3, 24, 14)],
    materials={"land": ("shimmering_flats/materials/tan_sand_gold", None),
               "dune": ("shimmering_flats/materials/tan_dune_ripple", None),
               "paving": ("shimmering_flats/materials/tan_flagstone_buried", None),
               "road": ("shimmering_flats/materials/tan_wadi_gravel", None),
               "water_s": ("vot_cluster/vot_water_shallow", None),
               "water_d": ("vot_cluster/vot_water_deep", None),
               "rock": ("shimmering_flats/materials/tan_sandstone_floor", None)},
    regions={"dune": [(28, 52, 12, 9), (82, 24, 7, 7)], "paving": [(70, 50, 12, 8), (50, 30, 12, 7), (50, 10, 8, 4)]},
    tint=(1.02, 0.96, 0.88), dark=0.08,
    props=[
        ("vot_broken_cart", DP, 44, 70, 3, "core"), ("tan_skeleton", SFP, 58, 70, 2, False),
        ("tan_dead_palm", SFP, 22, 46, 5, "core"), ("vot_broken_cart", DP, 30, 58, 3, "core"),
        ("sf_crate_stack", SFP, 36, 50, 3, "core"), ("sf_wheel_stack", SFP, 20, 56, 3, "core"),
        ("tan_ruin_block", SFP, 64, 46, 3, "core"), ("tan_ruin_block", SFP, 78, 54, 3, "core"),
        ("tan_obelisk", SFP, 42, 26, 5, "core"), ("tan_obelisk", SFP, 58, 26, 5, "core"),
        ("tan_skeleton", SFP, 82, 26, 2, False), ("tan_thorn_scrub", SFP, 18, 20, 2, False),
        ("vot_beast_ribcage", DP, 76, 46, 3, False), ("tan_dune_grass", SFP, 46, 78, 2, False),
        ("sf_crate_stack", SFP, 54, 8, 3, "core"),
    ],
)


# ============================================================================== THE LANDFORMS
def fields(spec, gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    W, H = spec["W"], spec["H"]
    if spec["mode"] == "islands":
        land = np.full(np.shape(gx), -30.0)
        for n, (cx, cy, rx, ry, rot) in enumerate(spec["land"]):
            land = np.maximum(land, ell(gx, gy, cx, cy, rx, ry, rot) + 0.9 * wob(gx, gy, n * 1.3))
        flat = np.full(np.shape(gx), -30.0)
        for (cx, cy, rx, ry) in spec["flats"]:
            flat = np.maximum(flat, ell(gx, gy, cx, cy, rx, ry))
        wet = -land
        deep = np.minimum(wet - spec["shore_w"], -flat)
        edge = np.full(np.shape(gx), -9.0)
    if spec["mode"] == "canyon":
        # ground where the chambers and the passes between them are; rock everywhere else
        opn = np.full(np.shape(gx), -30.0)
        for n, (cx, cy, rx, ry, rot) in enumerate(spec["open"]):
            opn = np.maximum(opn, ell(gx, gy, cx, cy, rx, ry, rot) + 0.9 * wob(gx, gy, n * 1.7))
        for n, (pts, w) in enumerate(spec["passes"]):
            opn = np.maximum(opn, w / 2 - seg_dist(gx, gy, pts) + 0.5 * wob(gx * 1.3, gy * 1.3, n))
        e = np.minimum.reduce([gx, W - gx, gy, H - gy])
        opn = np.minimum(opn, e - 2.5)
    if spec["mode"] != "islands":
        lake = np.full(np.shape(gx), -30.0)
        for n, (cx, cy, rx, ry, rot) in enumerate(spec["lakes"]):
            lake = np.maximum(lake, ell(gx, gy, cx, cy, rx, ry, rot) + 0.7 * wob(gx, gy, n * 2.1))
        land = -lake
        wet = lake
        flat = np.full(np.shape(gx), -30.0)
        for (cx, cy, rx, ry) in spec["flats"]:
            flat = np.maximum(flat, ell(gx, gy, cx, cy, rx, ry))
        deep = np.minimum(wet - spec["shore_w"], -flat)
        edge = -opn
    rock = edge
    for n, (cx, cy, rx, ry) in enumerate(spec["rocks"]):
        rock = np.maximum(rock, ell(gx, gy, cx, cy, rx, ry) + 0.5 * wob(gx * 1.6, gy * 1.6, n))
    rd = np.full(np.shape(gx), 99.0)
    for pts, w in spec["roads"]:
        rd = np.minimum(rd, seg_dist(gx, gy, pts) - w / 2)
    rock = np.where(rd < 1.2, np.minimum(rock, -0.6), rock)
    # the way in and out is never rock, and neither is the column you arrive on
    px, py = spec["portal"]
    near_portal = np.maximum(np.abs(gx - (px + 0.5)) - 2.5, np.abs(gy - (py - 1.0)) - 4.0)
    rock = np.where(near_portal < 0, np.minimum(rock, -0.6), rock)
    return dict(land=land, wet=wet, deep=deep, rock=rock, road=-rd)


def tile_kind(spec, gx, gy):
    """0 land, 1 shallow, 2 deep, 3 rock."""
    f = fields(spec, gx, gy)
    kind = np.zeros(np.shape(gx), int)
    kind[f["wet"] > 0] = 1
    kind[f["deep"] > 0] = 2
    kind[f["rock"] > 0] = 3
    return kind


# =============================================================================== THE TILE MAP
_ASPECT = {}


def _aspect(path):
    if path not in _ASPECT:
        with Image.open(path) as im:
            _ASPECT[path] = im.size[0] / im.size[1]
    return _ASPECT[path]


def build_zone(name):
    spec = SPECS[name]
    W, H = spec["W"], spec["H"]
    z = Tilemap(name, W, H, spec["desc"])
    z.region = spec["region"]
    z.is_town = False
    z.hidden_skull = True
    z.fill("grass", "base")
    ys, xs = np.mgrid[0:H, 0:W]
    gx, gy = xs + 0.5, ys + 0.5
    f = fields(spec, gx, gy)
    kind = tile_kind(spec, gx, gy)
    for y in range(H):
        for x in range(W):
            k = kind[y, x]
            if k == 1:
                z.set_tile(x, y, "shallow_water", "base")
            elif k == 2:
                z.set_tile(x, y, "deep_water", "base")
            elif k == 3:
                z.set_tile(x, y, "dirt", "base")
                z.set_tile(x, y, "cliff", "collision")
            elif f["road"][y, x] > 0:
                z.set_tile(x, y, "path", "base")
            elif spec["mode"] == "islands" and f["land"][y, x] < 1.5:
                z.set_tile(x, y, "sand", "base")
    px, py = spec["portal"]
    z.collision_layer[py][px] = None
    z.set_tile(px, py, "portal", "interaction")
    gid, (gx0, gy0) = spec["giver"]
    npcs = [(gx0, gy0)]
    # props: guarded, never on water, a portal, the giver or the road
    placed, skipped = 0, []
    for (pname, pdir, cx, by, h, solid) in spec["props"]:
        path = f"{pdir}{pname}.png"
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        wt = max(1, round(h * _aspect(path)))
        ax, ay = cx - wt // 2, by - h + 1
        core = []
        if solid:
            rows = max(1, round(h * 0.4))
            for yy in range(ay + h - rows, ay + h):
                for xx in range(ax + int(wt * 0.2), max(ax + int(wt * 0.8), ax + int(wt * 0.2) + 1)):
                    core.append((xx, yy))
        bad = None
        for (xx, yy) in core or [(cx, by)]:
            if not (0 <= xx < W and 0 <= yy < H):
                bad = "off-map"
            elif kind[yy, xx] in (1, 2):
                bad = "water"
            elif abs(xx - px) <= 2 and abs(yy - py) <= 4:
                bad = "portal"
            elif any(abs(xx - nx) <= 1 and abs(yy - ny) <= 1 for nx, ny in npcs):
                bad = "npc"
            elif f["road"][yy, xx] > -0.6:
                bad = "road"
        if bad:
            skipped.append((pname, cx, by, bad))
            continue
        z.add_landmark(path, ax, ay, wt, h, solid=False)
        for (xx, yy) in core:
            if z.interaction_layer[yy][xx] is None:
                z.collision_layer[yy][xx] = "landmark"
        placed += 1
    if spec.get("great_tree"):
        z.great_tree_door = _great_tree(z, spec, kind)
    z.add_subzone(name, 0, 0, W, H)
    for (sn, x, y, w, h) in spec["subzones"]:
        z.add_subzone(sn, x, y, w, h)
    _seal_unreachable(z, (px, py - 2))
    z.props_skipped = skipped
    return z


def _great_tree(z, spec, kind):
    """The great tree: drawn over everything under it, its roots solid, the ground under its crown
    walkable. Returns the tile behind the trunk where a secret door can stand (world/secrets.py,
    kind "behind"): the renderer draws the tree back over whatever is hidden there, and goes
    see-through only when you're standing under it yourself."""
    pname, pdir, cx, by, h = spec["great_tree"]
    path = f"{pdir}{pname}.png"
    wt = max(1, round(h * _aspect(path)))
    ax, ay = cx - wt // 2, by - h + 1
    z.add_landmark(path, ax, ay, wt, h, solid=False)
    z.landmarks[-1]["occluder"] = True
    # the trunk and roots: the bottom three rows, the middle half
    for yy in range(by - 2, by + 1):
        for xx in range(ax + wt // 4, ax + wt - wt // 4):
            if 0 <= xx < z.width and 0 <= yy < z.height and kind[yy, xx] == 0:
                z.collision_layer[yy][xx] = "landmark"
    # under the crown: open ground, so you can get round behind the trunk
    for yy in range(ay + 1, by - 2):
        for xx in range(ax + 1, ax + wt - 1):
            if 0 <= xx < z.width and 0 <= yy < z.height and kind[yy, xx] == 0 \
                    and z.collision_layer[yy][xx] == "landmark":
                z.collision_layer[yy][xx] = None
    return (cx, by - 6)


def _seal_unreachable(z, start):
    from collections import deque
    seen = {start}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < z.width and 0 <= n[1] < z.height and n not in seen and z.is_walkable(*n):
                seen.add(n)
                q.append(n)
    sealed = 0
    for y in range(z.height):
        for x in range(z.width):
            if (x, y) not in seen and z.is_walkable(x, y) and (x, y) != start:
                if z.base_layer[y][x] == "shallow_water":
                    z.set_tile(x, y, "deep_water", "base")
                else:
                    z.set_tile(x, y, "cliff", "collision")
                sealed += 1
    z.sealed = sealed


def register_baked(zone, baked_dir, chunk=20):
    for cy in range(0, zone.height, chunk):
        for cx in range(0, zone.width, chunk):
            fn = f"{baked_dir}/ground_{cx}_{cy}.jpg"
            if not os.path.exists(fn):
                return False
            w, h = min(chunk, zone.width - cx), min(chunk, zone.height - cy)
            zone.add_ground_chunk(fn, cx, cy, w, h)
            zone.ground_chunks[-1]["exact"] = True
            zone.add_water_chunk(fn, cx, cy, w, h)
            zone.add_obstacle_chunk(fn, cx, cy, w, h)
    return True


#: each map's portal tile (its way out, and where its secret door leads)
PORTALS = {n: s["portal"] for n, s in SPECS.items()}

#: hidden zones whose door is not a room in a wall but stands on a secret island
#: (tools/build_secrets.BAKED_ISLANDS): the island's map and its centre as BAKED_ISLANDS gives it
ISLAND_DOORS = {"The Saltgrave": ("Arathi East", (151, 10)),
                "The Tanglewood Shoals": ("Echo Isles", (23, 9))}

#: hidden zones whose door is placed by hand in a skull zone's layout: zone -> (parent, door tile)
def placed_doors():
    out = {}
    for name, spec in SPECS.items():
        if spec.get("great_tree") and spec.get("tree_leads_to"):
            pname, pdir, cx, by, h = spec["great_tree"]
            out[spec["tree_leads_to"]] = (name, (cx, by - 6))
    return out

#: quest givers: npc id -> (zone, x, y)
GIVERS = {s["giver"][0]: (n, *s["giver"][1]) for n, s in SPECS.items()}


def generate_all():
    out = {}
    for name, spec in SPECS.items():
        z = build_zone(name)
        register_baked(z, BAKED.format(spec["slug"]))
        out[name] = z
    return out
