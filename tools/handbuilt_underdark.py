"""
Hand-built The Crystalline Underdark (170x170): the cavern under Alterac that was not there three years ago.
Levels 33-37.  Frontier's first home-brew zone.

ARCHETYPE: THE ROOFED COUNTRY.  Reference point is Blackreach, arcane rather than Dwemer.

The single thing this map has to get right is that IT MUST NOT READ AS A CAVE. Every interior in Frontier so far
is close walls and corridors; Blackreach's trick is that it feels OUTDOORS - long sightlines, enormous scale, a
ceiling too far up to register as a lid, and light coming from the flora and from one huge thing overhead. So
this is built with the OPEN-ZONE kit (tools/town_kit + tools/tirisfal_kit), exactly like Hillsbrad or Silverpine,
and not with the cave kit. The rock is where the sky would be. Distant cliffs stand in for a horizon, the
galleries are separated by spurs rather than joined by tunnels, and the middle of the map is deliberately the
most open ground in it.

THE GIANT MUSHROOMS ARE THE TREES. They are scattered by the same forest pass that scatters pines in Silverpine,
they break sightlines at mid distance, and they are what makes a roofed country read as country. Four silhouettes
at tree scale; the small cluster is ground scatter, not canopy.

THE LUMEN hangs over the centre and lights the whole cavern. It brightens and dims on a cycle the Crimson Codex
set their watches by - "high lumen" and "low lumen" - and they have spent three years arguing about why a cave
has an opinion about time. It is lore and art, NOT a system: no world clock, no engine work. Its two jobs are to
give an underground zone a sense of day for free, and to be the landmark that makes a roofed country navigable.
You always know where you are because you can see it. What it actually IS stays unanswered.

HARD CONTRACTS (world/portal_manager.py)
  (85, 12)   <-> The Frostward Descent (58, 8)   the way back up to Hillsbrad
  (72, 80)   <-> Kael's Bastion                  the Codex holdfast (its own map)
  (150, 62)  <-> The Hollow Geode                the cave
  (34, 142)  <-> The Deep Bloom                  the dungeon
The last three are carved and marked here; their links register as those maps are built. An unregistered portal
tile fails safe (zone_manager.try_use_portal returns False), so they are harmless until then.
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob, lobe, water_body, rock_spurs

KEY = "crystalline_underdark"
#: Must match the name this zone is registered as in create_all_zones - portal_manager keys on zone.name.
#: Both Hillsbrad zones shipped with this mismatched and every portal in them was silently dead.
NAME = "The Crystalline Underdark"
DESC = ("A cavern the size of a county, lit from above by something nobody can name. Mushroom forest, crystal, "
        "and Dalaran masonry that nobody carried down here.")
REGION = "Eastern Kingdoms - Alterac"
W, H = 170, 170
BAKED_DIR = "assets/tiles/underdark/baked"
IS_TOWN = False
BASE_TILE = "dirt"
SEED = 907

UDP = "assets/tiles/underdark/props/"

PORTALS = {
    (85, 12): "The Frostward Descent",
    (72, 80): "Kael's Bastion",
    (150, 62): "The Hollow Geode",
    (34, 142): "The Deep Bloom",
}
ARRIVALS = [(85, 16), (72, 84), (146, 62), (34, 138)]
START = (85, 18)

#: The Codex have cut paths between their workings. Deliberately few and deliberately wide - a road through a
#: roofed country is a convenience, not the only way across, and the open ground between them is the point.
ROADS = {
    "spine":   ([(85, 14), (84, 34), (82, 56), (78, 76), (76, 96), (72, 118), (66, 140), (58, 156)], 3.4),
    "shard":   ([(80, 44), (56, 40), (34, 44), (20, 52)], 2.6),
    "lattice": ([(88, 40), (112, 38), (132, 42), (146, 48)], 2.6),
    "geode":   ([(90, 66), (116, 62), (138, 62), (150, 62)], 2.6),
    "marsh":   ([(80, 96), (106, 100), (126, 106), (138, 114)], 2.4),
    "archive": ([(76, 120), (104, 128), (126, 136), (138, 142)], 2.4),
    "bloom":   ([(66, 134), (50, 138), (38, 142)], 2.4),
    "dim":     ([(58, 150), (36, 150), (20, 146)], 2.2),
}
_RS = K.RoadSet(ROADS)
road_dist = _RS.dist

#: Codex workings - trodden flat and flagged where they have been standing for three years.
PAVED = [(72, 80, 11.0, 8.0),      # the Bastion's forecourt
         (132, 140, 9.0, 6.5),     # the Sunken Archive dig
         (147, 60, 6.0, 4.5)]      # the Geode mouth camp


def paved(gx, gy):
    out = np.full(np.shape(gx), -9.0)
    for cx, cy, rx, ry in PAVED:
        r = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
        out = np.maximum(out, (1 - r) * min(rx, ry))
    return out


# ---- water: the Lumen Marsh, and glowing seeps elsewhere -------------------------------------------------------
POOLS = [(124, 108, 16.0, 11.0, 0.9),     # the Lumen Marsh proper
         (108, 96, 7.0, 5.0, 0.3),
         (140, 122, 6.5, 4.5, 0.2),
         (44, 112, 5.5, 4.0, -0.1),       # a seep in the Mycelial Reach
         (30, 60, 5.0, 3.6, -0.2)]        # one out on the Shardfields


def water_field(gx, gy):
    w = np.full(np.shape(gx), -99.0)
    for (cx, cy, rx, ry, k) in POOLS:
        w = np.maximum(w, water_body(gx, gy, cx, cy, rx, ry, k=0.7) + k)
    return w


def deck_field(gx, gy):
    return np.full(np.shape(gx), -9.0)


#: The cavern wall, and the spurs that divide the galleries. Fewer and thinner than an open zone's ridges -
#: this country is meant to be crossed, and a spur is a thing you walk AROUND, not a wall you are stopped by.
SPURS = [
    (0, 0, 170, 0, 5.0), (0, 170, 170, 170, 5.0), (0, 0, 0, 170, 5.0), (170, 0, 170, 170, 5.0),
    (108, 22, 108, 54, 3.0),        # between the Hollow Dawn and the Lattice
    (52, 26, 52, 56, 2.8),          # between the Dawn and the Shardfields
    (26, 84, 56, 92, 2.6),          # the shoulder over the Mycelial Reach
    (100, 76, 126, 84, 2.6),        # between the Sporefall and the Marsh
    (96, 120, 120, 126, 2.6),       # above the Sunken Archive
    (36, 120, 54, 126, 2.4),        # the Dim Reaches' shoulder
    (132, 16, 150, 30, 3.0),        # the Riftward's edge, where the map is unfinished
]
OUTCROPS = [
    (64, 30, 3.0, 2.4), (116, 60, 2.8, 2.2), (40, 72, 2.6, 2.0), (92, 108, 2.8, 2.2),
    (148, 92, 3.0, 2.4), (24, 36, 2.6, 2.0), (60, 150, 2.6, 2.0), (118, 156, 2.8, 2.2),
    (152, 120, 2.6, 2.0), (16, 100, 2.4, 2.0), (86, 140, 2.4, 2.0), (136, 76, 2.6, 2.0),
]


def cliff_field(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    edge = np.minimum.reduce([gx, W - gx, gy, H - gy])
    # A thicker rim than an open zone gets: this is a cavern, and the wall is where the sky would be.
    rock = (7.0 + 3.0 * wob(gx * 0.5, gy * 0.5) + 1.2 * wob(gx * 1.4, gy * 1.4)) - edge
    rock = np.maximum(rock, rock_spurs(gx, gy, SPURS, OUTCROPS))
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    rock = np.where(water_field(gx, gy) > -1.0, np.minimum(rock, -0.5), rock)
    rock = np.where(paved(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    return rock


def fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    w = water_field(gx, gy)
    return dict(cliff=cliff_field(gx, gy), shallow=w, deep=w - 3.2, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


# ---- subzones (x, y, w, h) -------------------------------------------------------------------------------------
SUBZONES = [
    ("The Hollow Dawn", 62, 4, 48, 30),
    ("The Shardfields", 10, 34, 46, 40),
    ("The Lattice", 110, 26, 50, 38),
    ("The Riftward", 128, 4, 40, 26),
    ("The Sporefall", 52, 54, 58, 46),
    ("The Lumen Marsh", 100, 86, 52, 40),
    ("The Mycelial Reach", 14, 86, 44, 42),
    ("The Weeping Colonnade", 56, 104, 42, 36),
    ("The Sunken Archive", 104, 128, 54, 34),
    ("The Dim Reaches", 6, 132, 46, 34),
]

# ---- baker config (read by tools/bake_underdark_zone.py) --------------------------------------------------------
#: Base is bare cavern floor; fungus and crystal are painted where they belong rather than scattered everywhere,
#: because a cavern that is uniformly mushroom-covered stops reading as a cavern with a forest in it.
BASE = {"cavern": 0.58, "fungal": 0.20, "moss": 0.12, "shard": 0.14}
PAINT = {
    "fungal":  [(80, 76, 30, 24, 1.0), (36, 106, 22, 18, 1.0), (72, 60, 16, 12, 0.8)],
    "moss":    [(70, 90, 20, 15, 0.9), (30, 100, 16, 12, 0.9), (96, 70, 14, 10, 0.7)],
    "myc":     [(34, 106, 20, 16, 1.0), (56, 96, 12, 9, 0.7)],
    "shard":   [(30, 52, 24, 18, 1.0), (134, 46, 20, 15, 0.9), (20, 66, 12, 9, 0.8)],
    "crystal": [(134, 44, 22, 16, 1.0), (150, 20, 14, 11, 0.9), (118, 58, 12, 9, 0.7)],
    "lattice": [(136, 42, 12, 9, 1.0), (152, 18, 9, 7, 0.9)],
    "dalaran": [(74, 120, 18, 14, 1.0), (130, 140, 16, 12, 1.0)],
    "dim":     [(26, 148, 22, 16, 1.0), (14, 134, 12, 9, 0.8)],
    "rift":    [(150, 14, 16, 12, 1.0)],
    "glow":    [(124, 108, 18, 13, 0.8), (44, 112, 7, 5, 0.6)],
}
COBBLE = [(72, 80, 11, 8, 0.95), (132, 140, 9, 6.5, 0.85), (147, 60, 6, 4.5, 0.8)]

# ---- NPC spots (filled in the NPC pass; the Codex work out of the Bastion and three field camps) ----------------
NPC_POSITIONS = {
    "ud_dawn_watch": (86, 20),
    "ud_dawn_cartographer": (80, 24),
    "ud_shard_harvester": (32, 50),
    "ud_lattice_surveyor": (134, 44),
    "ud_geode_campkeeper": (146, 58),
    "ud_marsh_naturalist": (114, 92),  # moved off shallow water 7 Nov
    "ud_colonnade_scholar": (76, 118),
    "ud_archive_overseer": (132, 138),
    "ud_archive_digger": (128, 144),
    "ud_dim_scout": (30, 146),
    "ud_bloom_warden": (44, 138),
    "ud_sporefall_forager": (78, 74),
}
CHESTS = [(22, 40), (158, 24), (18, 118), (156, 100), (92, 150), (62, 62)]

#: The giant mushrooms, scattered like forest. `rim` is large because unlike a pine wood these are not clustered
#: against the rock - they stand in open ground, which is exactly what makes the country feel walked rather than
#: tunnelled.
FOREST = dict(seed=97, count=132, rim=40, thorn=0, names=[
    (UDP + "ud_shroom_tall_violet.png", 8, 0.32),
    (UDP + "ud_shroom_squat_ochre.png", 7, 0.40),
    (UDP + "ud_shroom_cluster_blue.png", 7, 0.36),
    (UDP + "ud_shroom_canopy.png", 9, 0.32),
])


def dress(L):
    p = L.prop
    U = lambda n: UDP + n + ".png"   # noqa: E731 - the kit treats any path with a "/" as literal

    # ---- The Hollow Dawn: you come out on a shelf and the whole cavern is in front of you
    p(U("ud_crystal_spire"), 78, 18, 8)
    p(U("ud_crystal_spire"), 94, 18, 8)
    p(U("ud_glow_pool"), 86, 24, 3)
    p(U("ud_survey_tripod"), 80, 22, 4)
    p(U("ud_codex_banner"), 90, 22, 6)
    p(U("ud_shroom_canopy"), 70, 28, 10)          # the first one you see, and it is enormous
    p(U("ud_moss_curtain"), 100, 14, 6)

    # ---- The Shardfields: open, exposed, the gathering ground
    p(U("ud_crystal_violet"), 26, 44, 6)
    p(U("ud_crystal_cyan"), 40, 56, 6)
    p(U("ud_crystal_spire"), 20, 62, 8)
    p(U("ud_geode_open"), 34, 48, 5)
    p(U("ud_crystal_float"), 30, 66, 4)
    p(U("ud_codex_crates"), 33, 51, 3)

    # ---- The Lattice: the clearest tell that this place is unfinished
    p(U("ud_lattice_growth"), 126, 36, 7)
    p(U("ud_lattice_growth"), 140, 48, 7)
    p(U("ud_lattice_growth"), 134, 34, 6)
    p(U("ud_crystal_spire"), 148, 40, 8)
    p(U("ud_survey_tripod"), 132, 46, 4)
    p(U("ud_field_desk"), 136, 50, 3)

    # ---- The Riftward: geometry that has not been finished
    p(U("ud_floating_stone"), 150, 12, 5)
    p(U("ud_crystal_float"), 158, 18, 4)
    p(U("ud_floating_stone"), 142, 20, 5)
    p(U("ud_rune_stone"), 154, 26, 6)

    # ---- The Sporefall: the forest. The scatter does the work; these are the centrepieces.
    p(U("ud_shroom_canopy"), 64, 66, 11)
    p(U("ud_shroom_tall_violet"), 96, 70, 10)
    p(U("ud_spore_vent"), 76, 68, 4)
    p(U("ud_spore_vent"), 88, 84, 4)
    p(U("ud_lichen_boulder"), 60, 86, 4)
    p(U("ud_glow_pool"), 84, 90, 3)
    p(U("ud_codex_tent"), 80, 72, 5)
    p(U("ud_arcane_brazier"), 76, 78, 5)

    # ---- The Lumen Marsh: standing water lit from underneath
    p(U("ud_moss_curtain"), 112, 92, 6)
    p(U("ud_lichen_boulder"), 136, 100, 4)
    p(U("ud_shroom_cluster_blue"), 108, 112, 7)
    p(U("ud_shroom_small"), 132, 118, 4)
    p(U("ud_specimen_rack"), 118, 94, 4)

    # ---- The Mycelial Reach: no Codex here, and the growth is organised
    p(U("ud_fungal_node"), 34, 104, 6)
    p(U("ud_fungal_shelf"), 24, 96, 5)
    p(U("ud_fungal_shelf"), 46, 116, 5)
    p(U("ud_cocooned_shape"), 30, 118, 5)
    p(U("ud_shelf_fungus"), 20, 110, 4)
    p(U("ud_spore_vent"), 40, 98, 4)

    # ---- The Weeping Colonnade: masonry nobody carried down here
    p(U("ud_broken_column"), 66, 112, 7)
    p(U("ud_broken_column"), 86, 116, 7)
    p(U("ud_fallen_arch"), 76, 124, 6)
    p(U("ud_statue_armless"), 73, 131, 6)
    p(U("ud_masonry_rubble"), 90, 128, 3)
    p(U("ud_rune_stone"), 60, 126, 6)

    # ---- The Sunken Archive: the Codex's prize, and their dig
    p(U("ud_dig_scaffold"), 126, 136, 7)
    p(U("ud_broken_column"), 140, 134, 7)
    p(U("ud_field_desk"), 134, 142, 3)
    p(U("ud_codex_crates"), 138, 146, 3)
    p(U("ud_arcane_brazier"), 128, 144, 5)
    p(U("ud_codex_banner"), 122, 140, 6)
    p(U("ud_fallen_arch"), 148, 140, 6)

    # ---- The Dim Reaches: where the Lumen does not reach
    p(U("ud_stalagmites"), 24, 142, 5)
    p(U("ud_stalagmites"), 38, 152, 5)
    p(U("ud_cocooned_shape"), 18, 150, 5)
    p(U("ud_shelf_fungus"), 32, 158, 4)
    p(U("ud_masonry_rubble"), 44, 148, 3)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_underdark():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/underdark_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
