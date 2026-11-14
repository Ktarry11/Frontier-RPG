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


def poly_field(gx, gy, pts, amp=1.4, ph=0.0):
    """Signed distance to a closed polygon (tiles; >0 inside), its edge roughened. Lets a map's
    outline be any shape at all - a wedge, an L, a crescent - instead of a stamp of ellipses."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    closed = list(pts) + [pts[0]]
    d = seg_dist(gx, gy, closed)
    inside = np.zeros(np.shape(gx), bool)
    for (x0, y0), (x1, y1) in zip(closed, closed[1:]):
        cond = ((y0 > gy) != (y1 > gy))
        xin = (x1 - x0) * (gy - y0) / ((y1 - y0) if y1 != y0 else 1e-9) + x0
        inside ^= cond & (gx < xin)
    return np.where(inside, d, -d) + amp * wob(gx * 0.9, gy * 0.9, ph) + 0.6 * amp * wob(gx * 2.1, gy * 2.1, ph + 2)


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
    materials={"land": ("stranglethorn/materials/stv_jungle", "stranglethorn/materials/stv_jungle_b"),
               "mud": ("stranglethorn/materials/stv_mud", None),
               "ruin": ("stranglethorn/materials/stv_ruin", None),
               "water_s": ("stranglethorn/materials/stv_sea_s", None),
               "water_d": ("stranglethorn/materials/stv_sea_d", None),
               "rock": ("stranglethorn/materials/stv_cliff_a", "stranglethorn/materials/stv_cliff_b")},
    regions={"ruin": [(50, 40, 7, 5), (50, 12, 6, 4), (24, 56, 5, 4), (76, 58, 5, 4)],
             "mud": [(50, 78, 10, 4)]},
    tint=(0.86, 0.96, 0.90), dark=0.12,
    mode="islands", shore_w=3.0,
    # AN ATOLL. A ring of jungle round a lagoon, broken where the sea comes through, and out in the
    # lagoon the islets the Gurubashi sank their gods by. Nothing like the open sandbars elsewhere.
    land=[(52, 40, 6, 5, 0), (38, 30, 4, 3, 0), (66, 50, 4, 3, 0)],
    atoll_poly=[([(14, 30), (30, 12), (58, 8), (82, 18), (90, 40), (80, 62), (60, 72), (36, 70), (18, 56)],
                 7, [(15, 44, 4.5)])],
    flats=[(52, 58, 3.5, 12), (45, 35, 7, 3), (59, 45, 7, 3)],
    rocks=[(30, 12, 2.5, 2), (86, 30, 2.5, 2)],
    roads=[],
    portal=(50, 73),
    giver=("hz_idols_fizzle", (44, 71)),
    subzones=[("The Idol Landing", 30, 62, 44, 16), ("The Western Idols", 6, 20, 22, 46),
              ("The Eastern Idols", 74, 20, 22, 46), ("The Jade Isles", 24, 2, 62, 16),
              ("The Sunken Altar", 32, 24, 14, 12), ("The Last God's Isle", 44, 32, 18, 18)],
    props=[
        ("stv_troll_idol_head", STV, 38, 32, 3, "core"), ("stv_troll_idol_head", STV, 66, 52, 3, "core"),
        ("stv_troll_serpent_head", STV, 52, 40, 4, "core"), ("stv_troll_altar", STV, 54, 43, 3, "core"),
        ("stv_troll_obelisk", STV, 16, 40, 5, "core"), ("stv_troll_obelisk", STV, 84, 44, 5, "core"),
        ("stv_troll_column", STV, 30, 14, 5, "core"), ("stv_troll_column", STV, 70, 14, 5, "core"),
        ("stv_troll_column_fallen", STV, 20, 52, 3, False), ("stv_mangrove", STV, 36, 72, 5, "core"),
        ("stv_tree_vined", STV, 64, 74, 6, "core"), ("stv_tree_strangler", STV, 18, 28, 6, "core"),
        ("stv_tree_strangler", STV, 82, 28, 6, "core"), ("stv_troll_skull_pile", STV, 50, 12, 3, False),
        ("stv_palm_young", STV, 76, 66, 4, "core"), ("stv_palm_young", STV, 24, 66, 4, "core"),
    ],
)

# THE BURIED CARAVAN. A whole trading caravan, and the town it was going to, under the dunes in a
# bowl of sandstone. The sand moves at night. Things walk out of it.
SPECS["The Buried Caravan"] = dict(
    slug="buried_caravan", W=100, H=84, region="Northern Tanaris", seed=936,
    desc="A bowl of sandstone off the Tanaris trade road where a whole caravan, and the town it was "
         "bound for, went under the dunes in a single night. They're still trying to arrive.",
    materials={"land": ("shimmering_flats/materials/tan_sand_gold", None),
               "dune": ("shimmering_flats/materials/tan_dune_ripple", None),
               "paving": ("shimmering_flats/materials/tan_flagstone_buried", None),
               "road": ("shimmering_flats/materials/tan_wadi_gravel", None),
               "water_s": ("vot_cluster/vot_water_shallow", None),
               "water_d": ("vot_cluster/vot_water_deep", None),
               "rock": ("shimmering_flats/materials/tan_sandstone_floor", None)},
    regions={"dune": [(28, 52, 12, 9), (82, 24, 7, 7)], "paving": [(70, 50, 12, 8), (50, 30, 12, 7), (50, 10, 8, 4)]},
    tint=(1.02, 0.96, 0.88), dark=0.08,
    mode="canyon", shore_w=1.5,
    # A BURIED TOWN. Open dunes, and in the north the roofs of the town the caravan was bound for,
    # standing up out of the sand in rows, so the streets between them are still streets.
    lakes=[], flats=[],
    open=[],
    outline=[[(6, 34), (16, 18), (36, 10), (60, 10), (84, 16), (94, 32), (90, 52), (78, 44), (62, 36),
              (42, 38), (28, 48), (30, 62), (42, 70), (52, 74), (58, 80), (44, 82), (26, 74), (12, 62), (6, 48)]],
    passes=[([(50, 84), (48, 74)], 8)],
    rocks=[(14, 46, 3, 3)],
    rock_grid=[(28, 16, 76, 28, 8, 2.6, (3, 7))],
    roads=[([(50, 80), (40, 70), (28, 56), (22, 40), (34, 24), (52, 20), (76, 24), (88, 36)], 2.2)],
    portal=(50, 81),
    giver=("hz_caravan_rizzo", (46, 77)),
    subzones=[("The Last Dune", 30, 64, 32, 20), ("The Wagon Graves", 4, 36, 26, 30),
              ("The Drowned Market", 62, 24, 34, 30), ("The Buried Gate", 24, 10, 38, 24),
              ("The Caravan Master's Rest", 62, 6, 30, 16)],
    props=[
        ("vot_broken_cart", DP, 38, 66, 3, "core"), ("tan_skeleton", SFP, 50, 72, 2, False),
        ("tan_dead_palm", SFP, 14, 54, 5, "core"), ("vot_broken_cart", DP, 20, 48, 3, "core"),
        ("sf_wheel_stack", SFP, 12, 40, 3, "core"), ("sf_crate_stack", SFP, 82, 30, 3, "core"),
        ("tan_ruin_block", SFP, 88, 44, 3, "core"), ("tan_obelisk", SFP, 70, 12, 5, "core"),
        ("tan_obelisk", SFP, 82, 14, 5, "core"), ("tan_skeleton", SFP, 66, 40, 2, False),
        ("tan_thorn_scrub", SFP, 30, 58, 2, False),
    ],
)


EK = "assets/tiles/eastern_kingdoms/props/"
BR = "assets/tiles/barrens/props/"
AV = "assets/tiles/ashenvale/props/"
UF = "assets/tiles/undead_farmland/props/"

# THE SUNKEN KRAAL. A sinkhole in the Barrens that swallowed a whole quillboar kraal, thorn-walls and
# all. The quillboar down here never stopped worshipping, and never stopped dying.
SPECS["The Sunken Kraal"] = dict(
    slug="sunken_kraal", W=96, H=84, region="Central Barrens", seed=937,
    desc="A sinkhole under the Barrens that swallowed a quillboar kraal whole. The thorns kept "
         "growing in the dark, and so did whatever the quillboar were praying to.",
    materials={"land": ("vot_cluster/vot_clay_a", "vot_cluster/vot_clay_pebbles"),
               "bone": ("vot_cluster/vot_bonesand", None),
               "burrow": ("vot_cluster/vot_burrow", None),
               "road": ("vot_cluster/vot_hardpan", None),
               "water_s": ("vot_cluster/vot_water_shallow", None),
               "water_d": ("vot_cluster/vot_water_deep", None),
               "rock": ("vot_cluster/vot_cliff_a", None)},
    regions={"bone": [(70, 56, 10, 8), (48, 10, 7, 4)], "burrow": [(26, 56, 10, 8), (22, 20, 8, 6)]},
    tint=(0.96, 0.90, 0.84), dark=0.16,
    mode="canyon", shore_w=1.6,
    # ONE SINKHOLE, FOUR LEDGES. A round pit with ledges stepping down to a pool in the middle; every
    # ledge wall has one gate, each on a different side, so the way down goes round and round.
    lakes=[(57, 44, 4, 3, 0)], flats=[],
    open=[],
    outline=[[(12, 30), (22, 12), (42, 8), (58, 14), (74, 10), (88, 24), (86, 44), (78, 58), (62, 70),
              (54, 76), (42, 76), (30, 66), (16, 56), (10, 42)]],
    passes=[([(48, 84), (48, 72)], 8)],
    rock_rings=[(50, 40, 30, 22, 2.2, [100]), (54, 42, 20, 14, 2.0, [300]), (56, 44, 11, 7, 2.0, [150])],
    rocks=[],
    roads=[],
    portal=(48, 81),
    giver=("hz_kraal_brannoc", (51, 78)),
    subzones=[("The Sinkhole Floor", 38, 74, 22, 10), ("The Thornwalls", 8, 6, 80, 70),
              ("The Bone Pens", 21, 17, 54, 54), ("The Drowned Shrine-Pool", 31, 27, 34, 34),
              ("The Thorn-Mother's Seat", 38, 34, 20, 20)],
    props=[
        ("br_quilboar_hut", BR, 20, 40, 4, "core"), ("br_quilboar_hut", BR, 30, 20, 4, "core"),
        ("br_quilboar_hut", BR, 70, 16, 4, "core"), ("br_quilboar_hut", BR, 82, 36, 4, "core"),
        ("br_quilboar_hut", BR, 72, 60, 4, "core"), ("vot_totem_pole", DP, 68, 55, 4, "core"),
        ("vot_totem_pole", DP, 34, 54, 4, "core"), ("vot_totem_pole", DP, 34, 30, 4, "core"),
        ("vot_totem_pole", DP, 70, 30, 4, "core"), ("rf_sacrificial_altar", DP, 57, 40, 3, "core"),
        ("br_razorfen_bramble_gate", BR, 48, 74, 5, False), ("br_kodo_skeleton", BR, 26, 60, 3, False),
        ("bbc_skull_pile", DP, 50, 12, 3, False), ("vot_beast_ribcage", DP, 16, 32, 3, False),
    ],
)

# THE MOONLESS GLADE. A grove in Ashenvale where the moon has never once been seen. The night elves
# sealed it with their own hands, and wrote nothing down about why.
SPECS["The Moonless Glade"] = dict(
    slug="moonless_glade", W=96, H=86, region="Ashenvale West", seed=938,
    desc="A grove behind Ashenvale's oldest trees where the moon has never once been seen. The "
         "Kaldorei sealed it long ago and wrote down nothing about why.",
    materials={"land": ("ashenvale/materials/av_forest_floor", "ashenvale/materials/av_needle_mulch"),
               "night": ("ashenvale/materials/av_nightmare_glade", None),
               "fern": ("ashenvale/materials/av_fern_floor", None),
               "road": ("ashenvale/materials/av_mossy_cobble", None),
               "water_s": ("ashenvale/materials/av_moon_water", None),
               "water_d": ("ashenvale/materials/av_lake_deep", None),
               "rock": ("ashenvale/materials/av_cliff_a", "ashenvale/materials/av_cliff_b")},
    regions={"night": [(72, 58, 10, 9), (50, 8, 8, 4)], "fern": [(26, 58, 10, 9), (18, 26, 7, 7)]},
    tint=(0.78, 0.82, 1.0), dark=0.22,
    mode="canyon", shore_w=1.8,
    # ONE LONG WAY IN. A single gorge that winds back and forth across the map, a dark pool where
    # it widens, side pockets you'd miss, and the sealed shrine at the very end of it.
    lakes=[(40, 40, 4, 2.6, 0), (73, 17, 3.6, 2.4, 0)], flats=[],
    open=[(12, 60, 5, 4, 0), (62, 54, 5, 4, 0), (88, 36, 4, 5, 0), (22, 8, 9, 5, 0)],
    passes=[([(48, 84), (44, 74), (28, 68), (16, 56), (20, 44), (38, 38), (58, 46), (74, 42), (84, 30),
              (74, 16), (56, 12), (40, 18), (28, 10)], 9),
            ([(62, 46), (62, 54)], 4), ([(84, 32), (88, 36)], 4), ([(14, 58), (12, 60)], 4)],
    rocks=[],
    roads=[],
    portal=(48, 83),
    giver=("hz_glade_ithrael", (47, 78)),
    subzones=[("The Shadowed Path", 30, 62, 30, 24), ("The Silent Grove", 4, 36, 28, 28),
              ("The Dark Pool", 30, 30, 30, 22), ("The Twisted Hollow", 56, 22, 36, 34),
              ("The Sealed Shrine", 8, 2, 30, 16)],
    props=[
        ("canopy_tree_cluster", AV, 36, 80, 6, "core"), ("canopy_tree_cluster", AV, 58, 76, 6, "core"),
        ("ash_elf_statue_head", AV, 12, 62, 4, "core"), ("ash_moon_rune_stone", AV, 22, 48, 3, "core"),
        ("ash_glow_mushroom_ring", AV, 44, 42, 2, False), ("dead_corrupted_tree", AV, 62, 50, 6, "core"),
        ("dead_corrupted_tree", AV, 76, 46, 6, "core"), ("ash_root_curtain", AV, 88, 34, 4, False),
        ("ash_elven_ruin_wall", AV, 64, 14, 4, "core"), ("ash_moon_sigil_stone", AV, 46, 14, 3, "core"),
        ("ash_elune_statue", AV, 20, 7, 5, "core"), ("ash_root_arch", AV, 30, 12, 5, False),
        ("dead_corrupted_tree", AV, 28, 34, 6, "core"),
    ],
)

# THE STORMCRAG. A high table of moor above Arathi that's always under a storm. Old stones stand
# in rings up there, and the lightning comes down on them like it's being called.
SPECS["The Stormcrag"] = dict(
    slug="stormcrag", W=100, H=84, region="Arathi Central", seed=939,
    desc="A storm-wrapped table of moor high above the Arathi Highlands, ringed with standing "
         "stones the lightning keeps coming back to.",
    materials={"land": ("hillsbrad/materials/hb_meadow", "hillsbrad/materials/hb_meadow2"),
               "rocky": ("hillsbrad/materials/hb_rocky", None),
               "heath": ("hillsbrad/materials/hb_dry", None),
               "water_s": ("hillsbrad/materials/hb_pool_shallow", None),
               "water_d": ("hillsbrad/materials/hb_pool_deep", None),
               "rock": ("hillsbrad/materials/hb_cliff_a", "hillsbrad/materials/hb_cliff_b")},
    regions={"rocky": [(50, 28, 10, 7), (50, 8, 8, 4)], "heath": [(28, 52, 12, 9), (72, 52, 11, 9)]},
    tint=(0.84, 0.86, 0.96), dark=0.18,
    mode="canyon", shore_w=1.6,
    # A TABLE CUT BY CHASMS. One great plateau, and the storm has split it: deep clefts run through
    # it and what's left is a lattice of ridges and stone bridges. Two stone circles stand on it.
    lakes=[(30, 66, 3.5, 2.6, 0)], flats=[],
    open=[],
    outline=[[(30, 80), (20, 70), (14, 56), (18, 44), (30, 36), (36, 22), (48, 10), (62, 6), (80, 8),
              (90, 18), (86, 30), (74, 38), (68, 52), (58, 62), (54, 72), (58, 80)]],
    passes=[([(50, 84), (46, 74)], 8)],
    rocks=[(28, 58, 4, 6), (44, 46, 5, 3), (56, 30, 4, 6), (70, 22, 6, 3), (40, 26, 3, 4), (62, 44, 3, 4)],
    rock_rings=[(26, 48, 5.5, 1.3, [0, 90, 180, 270]), (64, 16, 5.5, 1.3, [45, 135, 225, 315])],
    roads=[],
    portal=(50, 81),
    giver=("hz_storm_halvard", (46, 76)),
    subzones=[("The Crag Path", 30, 64, 32, 20), ("The West Ring", 10, 38, 30, 26),
              ("The East Ring", 54, 6, 22, 22), ("The Thunder Table", 30, 18, 30, 30),
              ("The Calling Stone", 74, 4, 20, 16)],
    props=[
        ("vot_mesa_pillar", DP, 26, 43, 4, "core"), ("vot_mesa_pillar", DP, 26, 54, 4, "core"),
        ("vot_mesa_pillar", DP, 59, 13, 4, "core"), ("vot_mesa_pillar", DP, 69, 21, 4, "core"),
        ("ek_dead_oak", EK, 38, 72, 5, "core"), ("ek_thorn_bush", EK, 54, 68, 2, False),
        ("vot_trail_cairn", DP, 34, 32, 3, "core"), ("vot_trail_cairn", DP, 52, 20, 3, "core"),
        ("bbc_rune_pillar", DP, 82, 13, 5, "core"), ("bbc_rune_pillar", DP, 77, 10, 4, "core"),
    ],
)

# THE ASHEN ORCHARD. Before the plague, Tirisfal's best apples came from an orchard nobody can find
# any more. It's still there, behind the hills. The trees still fruit. Nobody should eat it.
SPECS["The Ashen Orchard"] = dict(
    slug="ashen_orchard", W=92, H=80, region="Western Tirisfal", seed=940,
    desc="Tirisfal's lost orchard, folded away behind the hills. The plague got here first, and "
         "the trees still fruit for the dead who tend them.",
    materials={"land": ("tirisfal/materials/tf_dead_grass", "tirisfal/materials/tf_withered_meadow"),
               "plague": ("tirisfal/materials/tf_plague_ground", None),
               "leaf": ("tirisfal/materials/tf_leaf_litter", None),
               "road": ("tirisfal/materials/tf_old_cobble", None),
               "water_s": ("tirisfal/materials/tf_pond_shallow", None),
               "water_d": ("tirisfal/materials/tf_plague_slime", None),
               "rock": ("tirisfal/materials/tf_cliff_a", "tirisfal/materials/tf_cliff_b")},
    regions={"plague": [(66, 48, 12, 9), (46, 24, 10, 6)], "leaf": [(26, 48, 12, 9)]},
    tint=(0.92, 0.94, 0.82), dark=0.14,
    mode="canyon", shore_w=1.6,
    # PLANTED IN ROWS. An orchard is a grid, and walking a dead one row by row is the whole feeling
    # of the place: long straight lanes of grey trees, the cider house at the end of them.
    lakes=[(78, 32, 4, 2.6, 0)], flats=[],
    open=[],
    outline=[[(8, 14), (54, 10), (60, 24), (84, 26), (86, 58), (66, 62), (58, 72), (36, 72), (28, 60), (10, 58)]],
    passes=[([(46, 80), (46, 68)], 8)],
    rocks=[],
    roads=[([(46, 78), (46, 56), (46, 20)], 2.2), ([(12, 36), (80, 40)], 1.8)],
    prop_rows=[("dead_tree_bare", UF, 14, 18, 40, 52, 6, 6, 4)],
    portal=(46, 77),
    giver=("hz_orchard_marta", (49, 74)),
    subzones=[("The Orchard Gate", 32, 62, 28, 18), ("The Grey Rows", 8, 14, 36, 46),
              ("The Cider House", 56, 24, 32, 38), ("The Old Tree", 40, 6, 22, 16)],
    props=[
        ("farmhouse_ruin", UF, 72, 46, 6, "core"), ("ek_plague_cauldron", EK, 64, 52, 3, "core"),
        ("hay_bale_rotted", UF, 80, 52, 3, False), ("ek_farm_cart", EK, 40, 66, 3, "core"),
        ("ek_scarecrow", EK, 54, 60, 4, "core"), ("ek_willow", EK, 52, 16, 7, "core"),
        ("gravestone_cluster", UF, 44, 14, 3, False), ("ek_farm_well", EK, 66, 34, 3, "core"),
        ("ek_farm_fence", EK, 82, 44, 3, False),
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
        # an ATOLL: a ring of land round a lagoon, with gaps in it where the sea comes through
        for n, (cx, cy, rx, ry, w, gaps) in enumerate(spec.get("atolls", [])):
            r = np.hypot((gx - cx) / rx, (gy - cy) / ry) * (rx + ry) / 2
            a = np.degrees(np.arctan2(gy - cy, gx - cx)) % 360
            band = w / 2 - np.abs(r - (rx + ry) / 2) + 0.8 * wob(gx, gy, 5.0 + n)
            for g in gaps:
                d = np.minimum(np.abs(a - g), 360 - np.abs(a - g))
                band = np.where(d < 9, np.minimum(band, (d - 9) * 0.6), band)
            land = np.maximum(land, band)
        # an atoll drawn as a polygon: the land is a band along the outline, cut where the sea gets in
        for n, (pts, w, cuts) in enumerate(spec.get("atoll_poly", [])):
            closed = list(pts) + [pts[0]]
            band = w / 2 - seg_dist(gx, gy, closed) + 0.9 * wob(gx, gy, 7.0 + n)
            for (cx_, cy_, rc) in cuts:
                band = np.where(np.hypot(gx - cx_, gy - cy_) < rc, np.minimum(band, -1.0), band)
            land = np.maximum(land, band)
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
        for n, pts in enumerate(spec.get("outline", [])):
            opn = np.maximum(opn, poly_field(gx, gy, pts, 1.4, n * 1.9))
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
    # RINGS OF ROCK with gates: the ledges of a sinkhole, the walls of a stone circle
    for n, ring in enumerate(spec.get("rock_rings", [])):
        if len(ring) == 5:
            cx, cy, r, w, gates = ring
            ry_ = r
        else:
            cx, cy, r, ry_, w, gates = ring
        rr = np.hypot(gx - cx, (gy - cy) * r / ry_)
        a = np.degrees(np.arctan2(gy - cy, gx - cx)) % 360
        band = w / 2 - np.abs(rr - r) + 0.3 * wob(gx * 1.5, gy * 1.5, n)
        for g in gates:
            d = np.minimum(np.abs(a - g), 360 - np.abs(a - g)) * np.pi / 180 * r     # arc length, tiles
            band = np.where(d < 2.6, np.minimum(band, d - 2.6), band)
        rock = np.maximum(rock, band)
    # A GRID of blocks: the roofs of a buried town, standing up out of the sand
    for (x0, y0, x1, y1, step, half, skip) in spec.get("rock_grid", []):
        for bx in range(x0, x1 + 1, step):
            for by in range(y0, y1 + 1, step):
                if (bx * 7 + by * 3) % 11 in skip:
                    continue
                blk = np.minimum(half - np.abs(gx - bx), half - 0.4 - np.abs(gy - by))
                rock = np.maximum(rock, blk)
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
    props = list(spec["props"])
    # ROWS: an orchard is planted in lines, and the lines are the point of it
    for (pname, pdir, x0, y0, x1, y1, dx, dy, h) in spec.get("prop_rows", []):
        for yy in range(y0, y1 + 1, dy):
            for xx in range(x0, x1 + 1, dx):
                props.append((pname, pdir, xx + ((yy // dy) % 2), yy, h, "core"))
    for (pname, pdir, cx, by, h, solid) in props:
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
