"""
Hand-built The Forgotten Coast (200x200), levels 46-48: the corner of Feralas's L and the coast running north from it
(docs/feralas_brief.md).

You come in from the High Wilderness on the east edge and the sea is in front of you: the whole west side and the
south-west corner are open water, with two islands off the shore. This is also where the Integration shows: part of
the forest here came from our world, a Pacific Northwest rainforest of redwoods, sword ferns and fog, and a few
transplants live under it.

    East road ............. the east edge (196,110): from the High Wilderness
    The Fog Groves ........ the south-east: the grafted rainforest, redwoods and fog
    Cedar Hollow .......... in the Fog Groves (150,152): the settlers' cabins (safe)
    Ruins of Isildien ..... the north-middle: the Highborne dome, the Gordunni digging it out
    Frayfeather Highlands . the north-east: open high meadow and rock, the hippogryphs
    The Hatecrest Shore ... the north-west coast: the naga's beaches
    Feathermoon Landing ... the west shore (62,118): the Sentinels' pier, the boat to the island (safe)
    Sardor Isle ........... off the north-west shore, over a sandbar: the naga's island
    The Isle of Dread ..... off the south-west shore, over a sandbar: the chimaeras' island
    North road ............ the north edge (112,4): on to the Twin Colossals

THE ART: built before Kyle's Feralas sheets (Kyle, 19 Nov 2026: "Build without art for now"). The ground paints from
FERALAS_COAST_SHEET in tools/bake_ashenvale.py: the Fog Groves are the "corrupt" patches, painted with Stonetalon's
redwood duff, so the graft reads as its own ground; Isildien's and the naga's camps are the "satyr" ground.

HARD CONTRACTS (world/portal_manager.py)
  portals  The High Wilderness (196,110) <-> its west road (4,110); Feathermoon Stronghold (62,118) <-> its harbour
           (the boat); The Twin Colossals (112,4) <-> its south road
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_central_barrens import _gauss, _smooth
from world.chunk_paths import exists as _chunk_exists  # noqa: E402  (.webp, .jpg or .png)

BAKED_DIR = "assets/tiles/feralas/baked_forgotten_coast"
NAME = "The Forgotten Coast"
W, H = 200, 200
AV = E.AP
STP = "assets/tiles/stonetalon/props/"
ENT = "assets/tiles/cave_entrances/"
BLD = "assets/buildings/"

PORTALS = {(196, 110): "The High Wilderness", (62, 118): "Feathermoon Stronghold", (112, 4): "The Twin Colossals"}
ARRIVALS = [(193, 110), (65, 118), (112, 7)]
LATER_PORTALS = {}
START = (150, 112)     # the crossroads in the forest: everything must be reachable from here


def coast_x(gy):
    """The west shore: a headland at the Hatecrest beaches, the landing's bay, then the shore swinging east to the
    south-west corner."""
    gy = np.asarray(gy, float)
    return (52.0 + 10.0 * _gauss(gy, 40, 14) - 8.0 * _gauss(gy, 118, 12) + 26.0 * _smooth(150, 200, gy)
            + 1.8 * np.sin(0.21 * gy + 0.6) + 1.0 * np.sin(0.47 * gy + 1.3))


def sea(gx, gy):
    """The sea west of the shore and across the south-west corner. Extent > 0 is sea."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    west = coast_x(gy) - gx
    south = gy - (184.0 + 10.0 * _smooth(60, 120, gx) + 1.5 * np.sin(0.2 * gx))
    return np.maximum(west, np.where(gx < 120, south, -99.0))


#: Sardor Isle and the Isle of Dread, each joined to the shore by a sandbar you can wade
ISLETS = [(26, 58, 14, 12, 0, 0.9), (40, 61, 12, 2.6, 0, 0.0),
          (40, 178, 15, 10, 0, 1.4), (58, 170, 10, 2.6, -25, 0.0)]

LAKES = {
    "pools": [(130, 64, 6, 4, 0, 0.5), (176, 150, 5, 4, 0, 1.2)],
}
DEEP_SHRINK = {"pools": 2.0}
RIVERS = [   # a creek down out of the highlands, past the groves, to the sea south of the landing
    ([(184, 40), (170, 64), (150, 84), (130, 102), (112, 122), (94, 138), (76, 146), (56, 150)], 2.6, 1.0),
]
FORDS = [(139, 93, 6), (92, 138, 6), (116, 118, 6)]

# ---- rock: the Frayfeather crags in the north-east, outcrops in the forest
MESAS = [(176, 24, 14, 10, 0), (192, 70, 6, 12, 0), (152, 40, 6, 5, 0), (96, 160, 6, 5, 0)]
RIDGES = [([(150, 14), (160, 24), (154, 34)], 2.2)]

WOODS = [
    (110, 140, 10, 8, 0, 1.0), (80, 82, 8, 7, 0, 2.0), (172, 104, 7, 6, 0, 0.6), (134, 186, 12, 6, 0, 1.4),
    (100, 40, 8, 6, 0, 0.4), (180, 186, 10, 6, 0, 2.2), (70, 150, 7, 6, 0, 1.1), (190, 132, 6, 8, 0, 2.6),
]
BELTS = [([(120, 197), (160, 198), (200, 197)], 5.0), ([(60, 2), (90, 3), (140, 2), (200, 3)], 4.0)]
CLEARINGS = [
    (150, 112, 12, 9),          # the crossroads
    (150, 152, 12, 10),         # Cedar Hollow
    (118, 62, 16, 12),          # Ruins of Isildien
    (68, 118, 10, 8),           # Feathermoon Landing
    (70, 46, 12, 12),           # the Hatecrest Shore
    (176, 56, 12, 10),          # Frayfeather Highlands
    (186, 110, 9, 7),           # the east road in
    (112, 12, 9, 8),            # the north road out
    (40, 178, 8, 6),            # the Isle of Dread's tower ground (the giant trees filled the island, 19 Nov 2026)
]
#: the Fog Groves (the graft): painted as "corrupt" ground, which FERALAS_COAST_SHEET maps to redwood duff
CORRUPT_PATCHES = [(150, 150, 30, 26), (124, 168, 14, 12), (176, 136, 12, 14)]
BLUEBELL_PATCHES = [(146, 170, 10, 7), (130, 140, 8, 6), (178, 140, 6, 6)]   # redwood sorrel in the groves
PAVED_PATCHES = [(118, 62, 9, 7)]                                    # Isildien's paving
LUSH = 1.2
GRADE = None           # Kyle's own ground (19 Nov 2026) is rich already; the lift was for the borrowed Ashenvale ground

GAPS = [
    ("ell", 196, 110, 8, 7), ("ell", 112, 4, 7, 7), ("ell", 62, 118, 6, 5), ("ell", 150, 152, 10, 8),
    ("ell", 118, 62, 10, 8),
]

ROADS = {
    # west from the High Wilderness to the crossroads
    "east":       ([(196, 110), (176, 112), (150, 112)], 3.4),
    # on west to Feathermoon Landing
    "landing":    ([(150, 112), (126, 108), (100, 112), (80, 117), (62, 118)], 3.2),
    # north from the crossroads through Isildien to the north road
    "north":      ([(150, 112), (140, 92), (126, 74), (118, 62), (114, 40), (112, 20), (112, 4)], 3.2),
    # south into the Fog Groves and Cedar Hollow
    "groves":     ([(150, 112), (152, 130), (150, 152)], 2.8),
    # north-east up into the Frayfeather Highlands
    "highlands":  ([(140, 92), (156, 74), (176, 56)], 2.6),
    # north-west along the shore to the Hatecrest beaches and the sandbar to Sardor
    "shore":      ([(80, 117), (74, 96), (70, 74), (70, 52), (60, 60), (50, 61)], 2.6),
    # south-west down to the sandbar to the Isle of Dread
    "dread":      ([(100, 112), (90, 136), (80, 156), (66, 166)], 2.4),
}


class _Spec(E.Spec):
    """No woods in the sea or on the beach."""

    def woods_raw(self, gx, gy):
        out = super().woods_raw(gx, gy)
        sh, _dp = self.water_fields(gx, gy)
        return np.minimum(out, -(np.asarray(sh) + 3.0))


SPEC = _Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
             mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
             rim={"east": 5}, gaps=GAPS, fords=FORDS, thicket=(0.72, 10.0, 1.6))

#: the settlers of Cedar Hollow and the Sentinel at the landing (the quest pass, docs/feralas_quest_plan.md)
NPC_POSITIONS = {"fe_settler_june": (146, 150), "fe_settler_walt": (156, 148), "fe_settler_rosa": (148, 153),
                 "fe_settler_sam": (142, 156), "fe_landing_sentinel": (72, 114)}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("The Fog Groves", 112, 120, 88, 70, None),
    ("Cedar Hollow", 138, 140, 26, 24, None),
    ("Ruins of Isildien", 96, 44, 44, 38, None),
    ("Frayfeather Highlands", 150, 30, 50, 52, None),
    ("The Hatecrest Shore", 44, 20, 46, 76, None),
    ("Feathermoon Landing", 54, 106, 28, 22, None),
    ("Sardor Isle", 8, 42, 40, 34, None),
    ("The Isle of Dread", 20, 164, 40, 30, None),
]

#: Kyle's Feralas nature sheet (docs/feralas_art_prompts.md sheet 2, 19 Nov 2026): the giant forest. The coast
#: redwoods and cedars came over from our world, so they stand in the Fog Groves only (dress()); the spruce has spread.
FE = "assets/tiles/feralas/props/"
TREES = {
    "big":   [(FE + "fe_giant_tree.png", 13), (FE + "fe_giant_tree_hollow.png", 13), (FE + "fe_vine_giant.png", 12)],
    "mid":   [(FE + "fe_moss_curtain_tree.png", 10), (FE + "fe_sitka_spruce.png", 11), (FE + "fe_bigleaf_maple.png", 9)],
    "small": [(FE + "fe_tree_fern.png", 6), (FE + "fe_bigleaf_maple.png", 7)],
    "woods": [(FE + "fe_giant_tree.png", 13), (FE + "fe_vine_giant.png", 12), (FE + "fe_moss_curtain_tree.png", 11)],
}


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "Feralas's wild west coast, where the giant forest meets a grey-green sea. Part of the "
                             "forest came from another world, and a few of the people who did too live under it.",
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
    E.scatter_trees(L, TREES, seed=4601, spacing=5.8, grove_keep=0.5)          # Kyle, 19 Nov 2026: "Keep in mind the number of collisions (Trees) in feralas" (0.8 before: a quarter fewer groves)
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def sprinkle(L):
    """Sword ferns and nurse logs in the groves, driftwood-grey boulders by the sea."""
    import random
    rnd = random.Random(4603)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    ferns = logs = rocks = 0
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        if ferns < 30 and r < 0.016:
            if L.prop("st_ferns_big", x, y, 3, path_dir=STP, solid=False, nudge=0):
                ferns += 1
        elif logs < 16 and r < 0.040:
            if L.prop("st_nurse_log", x, y, 3, path_dir=STP, solid=False, nudge=0):
                logs += 1
        elif rocks < 20 and r < 0.050:
            if L.prop("st_moss_boulder", x, y, 3, path_dir=STP, solid=False, nudge=0):
                rocks += 1
    L.clutter = (ferns, logs, rocks)


CHEST_SPOTS = [(176, 120), (130, 160), (164, 178), (100, 92), (140, 40), (186, 40), (76, 66), (26, 56),
               (40, 180), (96, 132), (120, 186)]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    A = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=AV, **kw)                       # noqa: E731
    G = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=FE, **kw)                       # noqa: E731
    B = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=BLD, **kw)                      # noqa: E731

    A("ash_horde_signpost", 156, 106, 5)
    A("ash_signpost", 104, 106, 4)
    # ---- the Fog Groves: the redwoods and cedars that came over, standing in their own fog
    for (x, y, n, h) in [(132, 136, "fe_coast_redwood", 14), (166, 128, "fe_red_cedar", 12),
                         (172, 166, "fe_coast_redwood", 14), (128, 176, "fe_red_cedar", 11),
                         (186, 150, "fe_coast_redwood", 14), (118, 150, "fe_red_cedar", 12),
                         (160, 182, "fe_red_cedar", 11)]:
        G(n, x, y, h, solid="core", nudge=6)
    G("fe_nurse_log", 148, 176, 4, solid="core")
    G("fe_swordferns", 136, 166, 3, solid=False)
    G("fe_swordferns", 178, 140, 3, solid=False)
    # ---- Cedar Hollow: the settlers' cabins, built by hand from what was lying about
    G("fe_cabin", 142, 146, 6, solid="core")
    G("fe_small_cabin", 160, 146, 5, solid="core")
    G("fe_smokehouse", 152, 160, 5, solid="core")
    G("fe_garden_bed", 140, 160, 3, solid="core")
    G("fe_woodpile", 158, 158, 3, solid="core")
    G("fe_rail_fence", 146, 158, 3, solid="core")
    # ---- the Ruins of Isildien: the broken dome, the Gordunni digging it out
    B("fe_isildien_dome", 118, 56, 10, solid="core", nudge=9)
    G("fe_ruin_window", 106, 60, 5, solid="core")
    G("fe_highborne_arch", 130, 60, 6, solid="core")
    G("fe_statue_head", 110, 72, 4, solid="core")
    G("fe_ivy_column", 128, 72, 6, solid="core")
    G("fe_fallen_column", 104, 68, 3, solid="core")
    G("fe_ogre_tent", 124, 46, 5, solid="core")
    # ---- the Hatecrest Shore: the naga's camp on the beach
    G("fe_naga_shrine", 66, 38, 6, solid="core")
    G("fe_coral_brazier", 76, 48, 4, solid="core")
    G("fe_naga_tent", 62, 52, 5, solid="core")
    G("fe_dug_relics", 72, 30, 3, solid="core")
    # ---- Feathermoon Landing: the Sentinels' pier; the boat goes to the island
    B("fe_feathermoon_landing", 60, 118, 8, solid=False, road_ok=True)
    B("fm_field_tent", 76, 112, 5, solid="core")
    B("fm_banner", 70, 110, 5, solid="core")
    B("fm_moon_lantern", 66, 124, 4, solid="core")
    B("fm_cargo", 78, 122, 3, solid="core")
    # ---- Frayfeather Highlands: nests on the crags
    G("fe_hippogryph_nest", 170, 46, 4, solid="core")
    G("fe_hippogryph_nest", 184, 62, 4, solid="core")
    G("fe_highland_flowers", 166, 64, 3, solid=False)
    G("fe_granite_outcrop", 190, 48, 5, solid="core")
    # ---- Sardor Isle and the Isle of Dread
    G("fe_ruin_window", 22, 54, 5, solid="core")
    G("fe_naga_shrine", 26, 50, 6, solid="core")
    B("fe_dread_tower", 32, 180, 8, solid="core", nudge=4)
    G("fe_hippogryph_nest", 44, 172, 4, solid="core")
    G("fe_sea_stack", 30, 182, 5, solid="core")
    # ---- the shore
    G("fe_driftwood", 54, 140, 3, solid="core")
    G("fe_tide_pool", 48, 92, 3, solid=False, shore_ok=True, nudge=6)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and _chunk_exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_forgotten_coast():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
