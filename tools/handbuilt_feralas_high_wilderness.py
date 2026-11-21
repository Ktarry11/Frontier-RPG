"""
Hand-built The High Wilderness (220x160), levels 44-46: Feralas's east arm (docs/feralas_brief.md).

Kyle, 19 Nov 2026: "For 44-49 we can do feralas... Feralas can remain largely unchanged due to the integration and
follows the same L shape", three maps, the east arm first, in from "the west end of the Aspen Wilderness", where the
Rockies come down into the giant forest. So you arrive on the east edge at the foot of the range and walk west along
the arm toward the coast.

    The Aspen Descent ...... the east edge (216,80): down out of the aspens, the forest starting at the foot of the rock
    Camp Mojache ........... its door (160,86): the tauren camp, its own map
    Woodpaw Hills .......... the north-east hills: the gnolls
    The Hive Fields ........ the south-east: the silithid mounds, and the Zukk'ash Hive's mouth (176,142)
    The Lower Wilds ........ the south: the river marsh
    Grimtotem Compound ..... the north: the Grimtotem on the ground the tauren left
    The Gate of Dire Maul .. the middle: the ogres round the great gate (84,66), which leads nowhere yet
    Gordunni Outpost ....... the west: the ogres' forward camp
    The coast road ......... the west edge (4,110): on to the Forgotten Coast

THE ART: built before Kyle's Feralas sheets (Kyle, 19 Nov 2026: "Build without art for now"). The ground paints from
FERALAS_SHEET in tools/bake_ashenvale.py (Ashenvale's and Stonetalon's materials, greened), the giant trees are
Ashenvale's canopy trees and Stonetalon's sequoias, and the entrances are the cave_entrances library. When the sheets
come (docs/feralas_art_prompts.md), the sheet's stems and the props below swap over.

HARD CONTRACTS (world/portal_manager.py)
  portals  The Aspen Wilderness (216,80) <-> its west bench (2,152); Camp Mojache (160,86) <-> its gate;
           The Forgotten Coast (4,110) <-> its east road (196,110); The Zukk'ash Hive (176,142) <-> its way out
"""
import numpy as np

from tools import ashenvale_engine as E
from world.chunk_paths import exists as _chunk_exists  # noqa: E402  (.webp, .jpg or .png)

BAKED_DIR = "assets/tiles/feralas/baked_high_wilderness"
NAME = "The High Wilderness"
W, H = 220, 160
AV = E.AP
STP = "assets/tiles/stonetalon/props/"
ENT = "assets/tiles/cave_entrances/"

PORTALS = {(216, 80): "The Aspen Wilderness", (160, 86): "Camp Mojache", (4, 110): "The Forgotten Coast",
           (176, 142): "The Zukk'ash Hive"}
ARRIVALS = [(213, 80), (160, 89), (7, 110), (176, 139)]
#: Dire Maul's gate stands with its clearing cut and its door shut (the dungeon is 55-60, later)
LATER_PORTALS = {(84, 66): "Dire Maul"}
START = (160, 92)      # outside Camp Mojache: everything must be reachable from here

# ------------------------------------------------------------------ the plan
ROADS = {
    # down out of the aspens to Camp Mojache
    "descent":  ([(216, 80), (204, 82), (190, 86), (176, 88), (160, 90)], 3.4),
    # west from Mojache along the arm, past the gate, to the coast
    "arm":      ([(160, 90), (140, 92), (118, 94), (100, 90), (84, 80), (66, 88), (46, 98), (26, 106), (4, 110)], 3.4),
    # up to the gate of Dire Maul
    "gate":     ([(84, 80), (84, 72), (84, 66)], 3.0),
    # north from the arm to the Grimtotem Compound
    "compound": ([(118, 94), (116, 76), (112, 56), (110, 40)], 2.6),
    # north-east from Mojache into Woodpaw Hills
    "woodpaw":  ([(160, 90), (164, 70), (170, 52), (176, 36)], 2.6),
    # south from Mojache to the Hive Fields and the Zukk'ash Hive
    "hive":     ([(160, 90), (164, 108), (170, 124), (176, 142)], 2.8),
    # south-west from the arm down into the Lower Wilds
    "wilds":    ([(118, 94), (116, 112), (112, 130), (104, 144)], 2.6),
    # north-west from the arm to the Gordunni Outpost
    "outpost":  ([(46, 98), (42, 80), (40, 62), (40, 48)], 2.6),
}

RIVERS = [   # (pts, half-width shallow, half-width deep): down out of the hills, through the Lower Wilds, away south
    ([(140, 0), (136, 20), (130, 44), (128, 70), (126, 96), (122, 116), (112, 132), (96, 146), (84, 160)], 3.6, 1.6),
]
FORDS = [(126, 94, 6)]

LAKES = {
    "wilds": [(96, 128, 13, 8, 0, 0.7), (134, 144, 9, 6, 0, 1.4)],     # the marsh pools
    "tarns": [(196, 30, 4, 3, 0, 0.4), (30, 140, 5, 4, 0, 1.8)],
}
DEEP_SHRINK = {"wilds": 3.0, "tarns": 1.8}

# ---- rock: the range along the east (where the Rockies come down), crags across the north, outcrops in the forest
MESAS = [
    (210, 30, 12, 26, 0), (212, 132, 10, 24, 0),        # the range either side of the descent
    (64, 22, 14, 10, 0), (150, 18, 10, 8, 0),            # the northern crags
    (60, 132, 8, 6, 0), (140, 66, 5, 4, 0), (24, 72, 6, 5, 0),
]
RIDGES = [
    ([(196, 60), (190, 50), (196, 40)], 2.4),           # the descent's north wall
    ([(196, 100), (190, 112), (198, 120)], 2.4),        # and its south wall
]

# ---- woods (impassable giant forest): (cx, cy, rx, ry, rot, phase)
WOODS = [
    (30, 130, 12, 10, 0, 1.0), (60, 108, 9, 8, 0, 2.0), (140, 120, 9, 8, 0, 0.6), (196, 152, 10, 6, 0, 1.4),
    (88, 36, 10, 8, 0, 0.4), (136, 38, 8, 9, 0, 2.2), (10, 40, 10, 12, 0, 1.1), (100, 66, 6, 6, 0, 2.6),
    (186, 66, 7, 5, 0, 0.9), (150, 152, 9, 5, 0, 1.7), (20, 90, 8, 6, 0, 0.3),
]
BELTS = [
    ([(0, 156), (60, 157), (120, 155), (180, 157), (220, 156)], 5.0),     # the south rim
    ([(0, 3), (60, 2), (120, 4), (180, 2), (220, 3)], 5.0),               # the north rim
]
CLEARINGS = [   # carved back out of the woods
    (160, 90, 14, 10),          # outside Camp Mojache
    (84, 72, 14, 10),           # the gate of Dire Maul
    (112, 42, 14, 10),          # the Grimtotem Compound
    (174, 40, 14, 10),          # Woodpaw Hills
    (174, 132, 14, 12),         # the Hive Fields
    (40, 56, 12, 10),           # the Gordunni Outpost
    (204, 82, 10, 8),           # the foot of the descent
    (10, 110, 9, 7),            # the coast road out
]
#: the Hive Fields' churned ground and the Gordunni camps' trampled earth paint as "corrupt" and "satyr" ground
CORRUPT_PATCHES = [(174, 132, 12, 10)]
BURNED_PATCHES = []
BLUEBELL_PATCHES = [(100, 128, 12, 8), (196, 82, 8, 6), (60, 90, 8, 6)]      # wildflowers in the Wilds and below the pass
PAVED_PATCHES = [(84, 70, 7, 5)]          # the Highborne paving at the gate
LUSH = 1.2
GRADE = None           # Kyle's own ground (19 Nov 2026) is rich already; the lift was for the borrowed Ashenvale ground

GAPS = [
    ("ell", 216, 80, 8, 7), ("ell", 4, 110, 8, 7), ("ell", 160, 86, 7, 6), ("ell", 176, 142, 6, 5),
    ("ell", 84, 66, 8, 6), ("ell", 112, 42, 9, 7), ("ell", 174, 40, 9, 7), ("ell", 40, 56, 9, 7),
]

SPEC = E.Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK,
              mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={"west": 5, "south": 5, "north": 4}, rock_rim={"east": 8}, gaps=GAPS, fords=FORDS,
              thicket=(0.70, 10.0, 2.3))

#: the open-world people (the quest pass, docs/feralas_quest_plan.md): Mojache's lookout at the foot of the descent
NPC_POSITIONS = {"fe_scout_wapi": (200, 86)}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("The Aspen Descent", 184, 56, 36, 50, None),
    ("Woodpaw Hills", 146, 14, 54, 44, None),
    ("The Hive Fields", 150, 112, 50, 44, None),
    ("The Lower Wilds", 76, 108, 72, 48, None),
    ("Grimtotem Compound", 92, 18, 44, 44, None),
    ("The Gate of Dire Maul", 64, 56, 42, 32, None),
    ("Gordunni Outpost", 20, 36, 42, 40, None),
]

#: Kyle's Feralas nature sheet (docs/feralas_art_prompts.md sheet 2, 19 Nov 2026): the giant trees of the east arm.
FE = "assets/tiles/feralas/props/"
TREES = {
    "big":   [(FE + "fe_giant_tree.png", 13), (FE + "fe_giant_tree_hollow.png", 13), (FE + "fe_vine_giant.png", 12)],
    "mid":   [(FE + "fe_moss_curtain_tree.png", 10), (FE + "fe_root_bridge_tree.png", 10), (FE + "fe_bigleaf_maple.png", 9)],
    "small": [(FE + "fe_tree_fern.png", 6), (FE + "fe_bigleaf_maple.png", 7)],
    "woods": [(FE + "fe_giant_tree.png", 13), (FE + "fe_vine_giant.png", 12), (FE + "fe_moss_curtain_tree.png", 11)],
}


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "Feralas's east arm, where the Rockies come down into a forest of giant trees. Camp "
                             "Mojache took in the tauren who walked out of Mulgore; the Gordunni hold Dire Maul's gate.",
                             "Kalimdor - Feralas", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.seal_unreachable(L, START)
    dress(L)
    E.build_free_mask(L, NPC_POSITIONS.values())
    for lm in L.z.landmarks:
        ax, ay, w, h = lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]
        L.free_mask[max(0, ay):ay + h + 1, max(0, ax - 1):ax + w + 1] = False
    E.scatter_trees(L, TREES, seed=4401, spacing=5.6, grove_keep=0.5)          # Kyle, 19 Nov 2026: "Keep in mind the number of collisions (Trees) in feralas" (0.8 before: a quarter fewer groves)
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def sprinkle(L):
    """Ground clutter, a little: ferns and logs under the giant trees, mossy boulders."""
    import random
    rnd = random.Random(4403)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    ferns = logs = rocks = 0
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        if ferns < 26 and r < 0.014:
            if L.prop("st_ferns_big", x, y, 3, path_dir=STP, solid=False, nudge=0):
                ferns += 1
        elif logs < 16 and r < 0.040:
            if L.prop("st_nurse_log", x, y, 3, path_dir=STP, solid=False, nudge=0):
                logs += 1
        elif rocks < 22 and r < 0.050:
            if L.prop("st_moss_boulder", x, y, 3, path_dir=STP, solid=False, nudge=0):
                rocks += 1
    L.clutter = (ferns, logs, rocks)


CHEST_SPOTS = [
    (196, 100), (150, 40), (186, 22), (120, 30), (70, 50), (30, 60), (60, 96), (96, 112), (126, 138),
    (160, 126), (190, 136), (40, 120), (140, 106),
]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    A = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=AV, **kw)                       # noqa: E731
    S = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=STP, **kw)                      # noqa: E731
    G = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=FE, **kw)                       # noqa: E731
    B = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir="assets/buildings/", **kw)      # noqa: E731

    # ---- the roads: signposts at the forks
    A("ash_horde_signpost", 154, 96, 5)
    A("ash_signpost", 112, 98, 4)
    A("ash_signpost", 50, 104, 4)
    # ---- the Aspen Descent: the pass out of the range, the aspens giving way to the giant trees
    B("fe_aspen_pass", 216, 76, 9, solid=False, road_ok=True)
    G("fe_granite_outcrop", 206, 72, 4, solid="core")
    G("fe_dead_snag", 196, 72, 6, solid="core")
    # ---- Camp Mojache's gate: the camp is its own map behind it
    B("moj_gate", 160, 82, 7, solid=False, road_ok=True)
    B("moj_great_totem", 152, 84, 6, solid="core")
    B("moj_totem_pair", 168, 84, 5, solid="core")
    # ---- Woodpaw Hills: the gnolls' huts, snares and bones
    G("fe_gnoll_hut", 166, 34, 5, solid="core")
    G("fe_gnoll_tent", 182, 30, 5, solid="core")
    G("fe_gnoll_totem", 176, 46, 5, solid="core")
    G("fe_bone_pile", 186, 44, 3, solid="core")
    G("fe_gnoll_lookout", 190, 36, 6, solid="core")
    G("fe_gnoll_snare", 170, 44, 3, solid="core")
    # ---- the Hive Fields: the dig breaking the surface, and the Zukk'ash Hive's mouth
    B("fe_writhing_deep_mouth", 176, 138, 8, solid=False, road_ok=True)
    G("fe_hive_mound", 164, 128, 5, solid="core")
    G("fe_dig_mound", 186, 124, 3, solid="core")
    G("fe_resin_tree", 158, 138, 6, solid="core")
    G("fe_dark_sand_drift", 190, 140, 3, solid="core")
    G("fe_resin_spire", 168, 144, 5, solid="core")
    G("fe_sinking_tree", 184, 132, 5, solid="core")
    # ---- the Grimtotem Compound: the Grimtotem's own camp (Stonetalon's Grimtotem pieces are theirs)
    S("st_grim_palisade", 102, 34, 5, solid="core")
    S("st_grim_palisade", 122, 34, 5, solid="core")
    S("st_grim_war_totem", 112, 36, 7, solid="core")
    S("st_grim_stone_circle", 106, 48, 4, solid="core")
    S("st_grim_drum", 120, 48, 3, solid="core")
    S("st_grim_tent", 98, 44, 5, solid="core")
    # ---- the Gate of Dire Maul: Highborne stone, barricaded by ogres; the dungeon comes later
    B("fe_dire_maul_gate", 84, 62, 11, solid=False, road_ok=True)
    G("fe_highborne_arch", 70, 70, 7, solid="core")
    G("fe_statue_head", 98, 72, 4, solid="core")
    G("fe_ivy_column", 70, 62, 6, solid="core")
    G("fe_ruin_window", 98, 62, 6, solid="core")
    G("fe_ogre_gate", 84, 74, 6, solid=False, road_ok=True)
    G("fe_ogre_bonfire", 92, 78, 3, solid="core")
    # ---- the Gordunni Outpost: the ogres' forward camp
    G("fe_ogre_hut", 34, 50, 6, solid="core")
    G("fe_ogre_tent", 46, 52, 5, solid="core")
    G("fe_ogre_skull_totem", 40, 64, 5, solid="core")
    G("fe_ogre_spit", 30, 62, 3, solid="core")
    # ---- the Lower Wilds: reeds and old stones in the marsh
    G("fe_reeds", 100, 140, 3, solid=False)
    G("fe_river_boulders", 118, 146, 4, solid="core")
    G("fe_broken_stair", 78, 122, 4, solid="core")
    G("fe_fallen_giant", 92, 132, 4, solid="core", nudge=8)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and _chunk_exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_high_wilderness():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
