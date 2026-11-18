"""
Hand-built Central Azshara (200x200), levels 54-57: the middle of Azshara, between West Azshara's autumn forest and
the drowned East coast (docs/azshara_brief.md).

Kyle, 17 Nov 2026: Central is "the Highborne ruins and the salvage dig, Lake Mennar and the leylines the blues guard,
the satyr and demon camps, and the naga grotto on the Bay of Storms." Still Classic's red-gold autumn here, but the sea
comes in: the north coast and the Bay of Storms in the north-east, Southridge Beach in the south-east. Drowned spires
already stand out in the bay, the first sign of Zin-Azshari coming up.

    West road ........... west edge (4,96): from West Azshara's east road (196,96)
    The Eldarath Road ... the crossroads (104,98)
    Legash Encampment ... the north, under the mountains: the satyrs' war camp
    Lake Mennar ......... the south-west: the lake, and the Mennar Font on its north-east shore, where the leylines
                          meet and the blue dragonflight stands guard over them
    Ruins of Eldarath ... the south-middle: the biggest Highborne ruin on this side of the sea, and the Talrendis crews'
                          main dig in it
    Forlorn Ridge ....... the south-west: the Legion's leftovers, round a gate that never quite closed
    Bay of Storms ....... the north-east: the bay, with spires standing in it
    Hetaera's Clutch .... the headland east of the bay: the naga's beachhead, and the grotto's mouth in its crag
    Southridge Beach .... the south-east coast: wrecks, and the naga coming ashore
    East road ........... east edge (196,130): on to the East coast

THE ART is Kyle's Azshara sheets (docs/azshara_art_prompts.md): tools/bake_ashenvale.py azshara_central paints the
ground from sheet 1 (AZSHARA_CENTRAL_SHEET: leyline grass round the Font, dig earth in the Eldarath dig, arcane water
in the Font itself), and the props are sheet 2's and the Landing's salvage pieces from sheet 3.

HARD CONTRACTS (world/portal_manager.py)
  portals  West Azshara (4,96) <-> its east road (196,96); East Azshara (196,130) <-> its west road (4,130). Later
           Hetaera's Grotto (186,58) <-> its way out (50,97)
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_central_barrens import blob, _smooth

BAKED_DIR = "assets/tiles/azshara/baked_central"
AZP = "assets/tiles/azshara/props/"      # Kyle's Azshara props sheet (sheet 2)
BLD = "assets/buildings/"                # the Landing's salvage pieces (sheet 3)
W, H = 200, 200

PORTALS = {(4, 96): "West Azshara", (196, 130): "East Azshara", (186, 58): "Hetaera's Grotto"}
ARRIVALS = [(6, 96), (194, 130), (186, 56)]
#: the doors whose maps come next; their clearings, roads and gaps are already cut
LATER_PORTALS = {}
START = (104, 100)     # the crossroads: everything must be reachable from here

# ------------------------------------------------------------------ the plan
ROADS = {
    # in from West Azshara to the crossroads on the Eldarath Road
    "west":     ([(4, 96), (22, 97), (40, 99), (56, 100), (74, 98), (90, 96), (104, 98)], 3.4),
    # north from the crossroads up into the foothills to Legash Encampment
    "legash":   ([(104, 98), (101, 82), (94, 66), (85, 54), (78, 46)], 3.0),
    # south to the Ruins of Eldarath and the dig
    "eldarath": ([(104, 98), (106, 114), (108, 128), (112, 142)], 3.2),
    # off the west road to the Mennar Font
    "mennar":   ([(74, 98), (77, 108), (82, 114), (86, 118)], 2.6),
    # east past the bay to the East coast
    "east":     ([(104, 98), (122, 104), (140, 114), (156, 122), (174, 126), (196, 130)], 3.2),
    # north up the headland to Hetaera's Clutch and the grotto's mouth
    "clutch":   ([(174, 126), (182, 114), (186, 98), (186, 80), (186, 62)], 2.6),
    # south to Southridge Beach
    "beach":    ([(140, 114), (146, 134), (150, 154), (156, 170), (160, 178)], 2.6),
    # south-west from the dig, over the outflow, to Forlorn Ridge
    "forlorn":  ([(112, 142), (98, 150), (84, 160), (68, 168), (54, 172)], 2.6),
}

RIVERS = [   # (pts, half-width shallow, half-width deep)
    # down out of the northern mountains into Lake Mennar
    ([(46, 20), (48, 44), (50, 68), (54, 92), (57, 112), (60, 128)], 3.0, 1.3),
    # Lake Mennar's outflow, south-east to the sea past Southridge
    ([(74, 148), (84, 158), (96, 168), (110, 178), (124, 188), (134, 199)], 3.0, 1.3),
]
FORDS = [(54, 98, 6), (88, 160, 6)]

LAKES = {
    "mennar": [(62, 140, 18, 12, 10, 0.8)],
    "font": [(87, 124, 4.5, 3.5, 0, 0.5)],         # the Mennar Font, where the leylines meet
}
DEEP_SHRINK = {"mennar": 3.0, "font": 1.6}
MOON_POOLS = [(87, 124, 6)]        # the Font paints as arcane water


def sea(gx, gy):
    """The north coast (the sea along the top east of x~115), the Bay of Storms biting south into it, and Southridge
    Beach's coast along the bottom east of x~130. Extent > 0 is sea."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    north = (-44.0 + 66.0 * _smooth(98, 126, gx) + 2.2 * np.sin(0.21 * gx + 0.4) + 1.3 * np.sin(0.37 * gx + 1.1)) - gy
    south = gy - (244.0 - 56.0 * _smooth(110, 144, gx) - 2.0 * np.sin(0.17 * gx + 0.8) - 1.2 * np.sin(0.41 * gx))
    bay = np.maximum(blob(gx, gy, 152, 60, 19, 36, 6, 1.1), blob(gx, gy, 150, 26, 24, 12, 0, 0.4))   # and its mouth
    return np.maximum(np.maximum(north, south), bay)


# ---- rock: the mountains across the north-west, the headland's crag, Forlorn Ridge in the south-west
MESAS = [
    (22, 22, 20, 16, 0), (64, 16, 18, 11, 0), (100, 14, 12, 8, 0),       # the northern mountains
    (189, 48, 8, 9, 0),                                                    # the crag the grotto opens under
    (14, 184, 12, 12, 0),                                                  # Forlorn Ridge's end
]
RIDGES = [
    ([(14, 150), (26, 160), (34, 172), (30, 186)], 3.2),                   # Forlorn Ridge
    ([(30, 40), (36, 50), (34, 60)], 2.4),                                 # a spur off the mountains
]

# ---- woods (impassable autumn forest): (cx, cy, rx, ry, rot, phase)
WOODS = [
    (28, 64, 11, 9, 0, 1.0), (118, 62, 8, 9, 0, 0.6), (34, 130, 7, 8, 0, 2.0), (136, 166, 10, 8, 0, 1.4),
    (174, 152, 9, 10, 0, 0.9), (80, 74, 10, 8, 0, 2.4), (124, 128, 7, 6, 0, 1.7), (20, 112, 8, 7, 0, 0.5),
    (142, 140, 7, 7, 0, 2.2), (36, 84, 8, 7, 0, 1.3), (96, 180, 9, 6, 0, 0.8), (112, 36, 8, 7, 0, 2.7),
    (166, 100, 5, 8, 0, 1.9), (66, 160, 6, 5, 0, 0.3),
]
BELTS = [
    ([(0, 194), (30, 196), (70, 196), (100, 194), (116, 190)], 6.0),       # the south-west rim
    ([(199, 64), (198, 100), (199, 122)], 5.0),                            # the east edge, north of the road out
    ([(199, 138), (198, 162), (199, 180)], 5.0),                           # ...and south of it
]
CLEARINGS = [   # carved back out of the woods
    (104, 98, 12, 9),           # the crossroads
    (78, 46, 16, 11),           # Legash Encampment
    (112, 144, 22, 15),         # Ruins of Eldarath and the dig
    (84, 119, 10, 7),           # the Mennar Font
    (54, 172, 12, 9),           # Forlorn Ridge's demon camp
    (160, 178, 14, 8),          # Southridge Beach
    (182, 76, 10, 14),          # Hetaera's Clutch
    (10, 96, 9, 7),             # the west road in
    (188, 130, 9, 7),           # the east road out
    (60, 124, 9, 5),            # Lake Mennar's north shore, where the stream comes in
    (140, 114, 8, 6),           # the beach turn
]
BLUEBELL_PATCHES = [(86, 119, 9, 6), (97, 128, 7, 4), (70, 116, 7, 4), (112, 136, 8, 5)]   # leyline grass
CORRUPT_PATCHES = [(78, 46, 13, 9), (54, 172, 10, 7)]       # Legash and the demon camp
BURNED_PATCHES = [(54, 172, 6, 4)]                          # the gate's ground, burned
LUSH = 1.0
GRADE = (1.30, 1.14)
PAVED_PATCHES = [(112, 144, 11, 7), (104, 98, 5, 3)]        # Highborne paving through Eldarath
DIGS = [(121, 151, 7, 5), (101, 152, 4, 3)]                  # the Talrendis crews' trenches (dig earth)

#: open ground the tree scatter leaves alone: the camps and the ruin need room to read as places
OPEN_GROUND = [(104, 98, 7, 5), (78, 45, 19, 13), (112, 145, 21, 13), (86, 121, 13, 9), (52, 172, 12, 8),
               (184, 78, 7, 14), (160, 178, 12, 5)]

GAPS = [
    ("ell", 4, 96, 8, 7), ("ell", 196, 130, 8, 7), ("ell", 186, 61, 5, 3), ("ell", 104, 98, 9, 7),
    ("ell", 78, 46, 10, 7), ("ell", 112, 144, 14, 10), ("ell", 160, 178, 9, 5), ("ell", 54, 172, 8, 6),
]


class _Spec(E.Spec):
    """No woods in the water: the shared thicket noise knows nothing of the sea and the lakes, and woods win over
    water in tile_kind, so the forest is pulled back off every shore here."""

    def woods_raw(self, gx, gy):
        out = super().woods_raw(gx, gy)
        sh, _dp = self.water_fields(gx, gy)
        return np.minimum(out, -(np.asarray(sh) + 2.5))


SPEC = _Spec("Central Azshara", W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea,
             mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
             rock_rim={"west": 7}, gaps=GAPS, fords=FORDS, thicket=(0.70, 10.0, 2.3))

#: Most of Azshara's quests are given in its two hubs (Kyle's ~70%); the open-world people come with the quest pass.
NPC_POSITIONS = {}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


def plaza_field(P, wp):
    """The baker's plaza layer: the dig's trenches (AZSHARA_CENTRAL_SHEET paints it as dig earth)."""
    return np.maximum.reduce([P.blob(*d, 0.6, wp) for d in DIGS])


CAVES = {(186, 58): ("ent_sea_cave", 9, 7)}     # Hetaera's Grotto's mouth

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("Forlorn Ridge", 4, 140, 70, 56, None),
    ("Lake Mennar", 40, 110, 56, 46, None),
    ("Ruins of Eldarath", 88, 126, 50, 36, None),
    ("Legash Encampment", 56, 30, 46, 32, None),
    ("Bay of Storms", 126, 18, 50, 86, None),
    ("Hetaera's Clutch", 172, 22, 28, 92, None),
    ("Southridge Beach", 132, 166, 68, 34, None),
]

TREES = {
    "big":   [(AZP + "az_autumn_tree.png", 10), (AZP + "az_gold_tree.png", 9), (AZP + "az_autumn_tree.png", 11)],
    "mid":   [(AZP + "az_gold_tree.png", 8), (AZP + "az_autumn_tree.png", 9), (AZP + "az_birch_trio.png", 8)],
    "small": [(AZP + "az_birch_trio.png", 7), (AZP + "az_gold_tree.png", 7)],
    "woods": [(AZP + "az_autumn_tree.png", 10), (AZP + "az_gold_tree.png", 9), (AZP + "az_autumn_tree.png", 11)],
}


def build_layout():
    AL = E.make_layout_class(SPEC, "Central Azshara",
                             "The heart of Azshara: Highborne ruins in the red-gold forest, the leylines over Lake "
                             "Mennar, satyrs in the hills, and the sea coming in at the Bay of Storms.",
                             "Kalimdor - Azshara", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.seal_unreachable(L, START)
    dress(L)
    E.build_free_mask(L, NPC_POSITIONS.values())
    ys, xs = np.mgrid[0:H, 0:W]
    for (cx, cy, rx, ry) in OPEN_GROUND:
        L.free_mask[((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2 < 1.0] = False
    for lm in L.z.landmarks:
        ax, ay, w, h = lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]
        L.free_mask[max(0, ay):ay + h + 1, max(0, ax - 1):ax + w + 1] = False
    E.scatter_trees(L, TREES, seed=5401, spacing=5.6, grove_keep=0.75)
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def sprinkle(L):
    """Ground clutter, a little: crimson bushes and logs in the forest, rocks everywhere, glowing shrooms by the Font."""
    import random
    rnd = random.Random(5403)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    ferns = logs = rocks = 0
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        if ferns < 20 and r < 0.012:
            if L.prop("az_crimson_bush", x, y, 3, path_dir=AZP, solid=False, nudge=0):
                ferns += 1
        elif logs < 18 and r < 0.040:
            if L.prop("az_autumn_log", x, y, 3, path_dir=AZP, solid=False, nudge=0):
                logs += 1
        elif rocks < 26 and r < 0.050:
            if L.prop("az_lichen_boulder", x, y, 4, path_dir=AZP, solid=False, nudge=0):
                rocks += 1
    L.clutter = (ferns, logs, rocks)


CHEST_SPOTS = [
    (24, 98), (60, 82), (96, 60), (132, 96), (170, 112), (190, 88), (176, 170), (140, 186), (88, 176),
    (32, 150), (70, 128), (124, 160), (44, 110),
]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    P = L.prop
    X = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=E.XP, **kw)        # noqa: E731
    B = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=BLD, **kw)         # noqa: E731
    Z = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=AZP, **kw)         # noqa: E731
    W_ = lambda n, x, y, h: L.deco(n, x, y, h, path_dir=AZP)                     # noqa: E731  (standing in the sea)

    # ---- the roads: signposts at the crossroads and the turns
    P("br_signpost", 12, 92, 5)
    P("br_signpost", 108, 92, 5)
    P("br_signpost", 144, 108, 4)
    P("br_signpost", 178, 122, 4)
    # ---- Legash Encampment: the satyrs' war camp under the mountains
    X("ashx_satyr_tent", 70, 42, 6, solid="core")
    X("ashx_satyr_tent", 86, 40, 6, solid="core")
    X("satyr_throne", 78, 38, 6, solid="core")
    Z("az_satyr_totem", 68, 52, 6, solid="core")
    Z("az_fel_bonfire", 78, 48, 4, solid="core")
    Z("az_cursed_tree", 92, 50, 9, solid="core")
    X("ashx_satyr_weapon_rack", 88, 52, 4, solid="core")
    X("ashx_skull_fence", 64, 46, 4, solid="core")
    Z("az_noble_statue", 72, 34, 7, solid="core")              # a Highborne lord's statue, defaced
    Z("az_fel_bonfire", 70, 48, 4, solid="core")
    Z("az_satyr_totem", 90, 44, 6, solid="core")
    Z("az_cursed_tree", 62, 40, 8, solid="core")
    X("twisted_dead_tree_cluster", 94, 36, 6, solid="core")
    X("ashx_corrupt_furbolg_totem", 84, 54, 5, solid="core")   # a Timbermaw totem the satyrs took
    # ---- the Mennar Font: where the leylines meet, the blues' charge, and the salvage crews' pylons tapping it
    Z("az_mana_tower", 96, 118, 10, solid="core")
    Z("az_leyline_node", 80, 114, 5, solid="core")
    Z("az_leyline_node", 94, 128, 5, solid="core")
    Z("az_arcane_crystal", 78, 122, 5, solid="core")
    Z("az_arcane_crystal", 92, 112, 5, solid="core")
    Z("az_crystal_tree", 74, 112, 8, solid="core")
    Z("az_crystal_tree", 100, 126, 8, solid="core")
    Z("az_containment_pylon", 88, 114, 5, solid="core")
    Z("az_glow_shrooms", 82, 128, 3, solid=False)
    # ---- Ruins of Eldarath: the great ruin...
    Z("az_broken_spire", 104, 136, 12, solid="core")
    Z("az_broken_spire", 126, 138, 10, solid="core")
    Z("az_moon_arch", 112, 132, 8, solid="core")
    Z("az_dry_fountain", 112, 146, 5, solid="core")
    Z("az_noble_statue", 98, 144, 7, solid="core")
    Z("az_toppled_column", 132, 146, 5, solid="core")
    Z("az_toppled_column", 94, 156, 5, solid="core")
    Z("az_ruin_wall", 96, 132, 5, solid="core")
    Z("az_ruin_wall", 130, 156, 5, solid="core")
    # ...and the Talrendis crews' dig in it
    B("tl_research_tent", 118, 140, 6, solid="core")
    B("tl_stone_crane", 126, 150, 8, solid="core")
    B("tl_sorting_shed", 106, 152, 6, solid="core")
    B("tl_ward_pylon", 114, 156, 6, solid="core")
    B("tl_survey_tower", 134, 140, 8, solid="core")
    B("tl_sandbags", 120, 158, 3, solid="core")
    Z("az_dig_scaffold", 122, 148, 6, solid="core")
    Z("az_dig_cart", 116, 150, 4, solid="core")
    Z("az_relic_crate", 110, 150, 3, solid="core")
    Z("az_covered_find", 100, 150, 4, solid="core")
    Z("az_survey_stakes", 106, 128, 4, solid="core")
    # ---- Forlorn Ridge: the Legion's leftovers round a gate that never quite closed
    X("ashx_demon_gate", 50, 166, 9, solid="core")
    X("ashx_demon_skull_altar", 60, 172, 5, solid="core")
    X("ashx_demon_ribcage", 44, 176, 5, solid="core")
    X("fel_fire_brazier", 56, 164, 4, solid="core")
    X("fel_fire_brazier", 62, 178, 4, solid="core")
    X("ashx_obsidian_spires", 40, 168, 6, solid="core")
    X("ashx_demon_egg", 58, 180, 3, solid="core")
    # ---- Hetaera's Clutch: the naga's beachhead on the headland
    Z("az_naga_banner", 180, 70, 6, solid="core")
    Z("az_naga_banner", 188, 84, 6, solid="core")
    Z("az_tide_altar", 182, 80, 5, solid="core")
    Z("az_scale_pile", 178, 88, 3, solid="core")
    Z("az_coral_arch", 190, 66, 6, solid="core")
    Z("az_barnacle_statue", 176, 76, 7, solid="core")
    Z("az_giant_clam", 184, 92, 3, solid="core")
    # ---- the Bay of Storms: the first drowned spires standing up out of the water
    W_("az_drowned_spire", 150, 50, 12)
    W_("az_drowned_spire", 158, 74, 10)
    W_("az_drowned_obelisk", 144, 84, 7)
    # ---- Southridge Beach: wrecks, and the naga coming ashore
    Z("az_wreck_prow", 150, 182, 6, solid="core", shore_ok=True)
    Z("az_coral_cluster", 168, 184, 4, solid="core", shore_ok=True)
    Z("az_giant_clam", 174, 180, 3, solid="core", shore_ok=True)
    Z("az_naga_banner", 164, 176, 6, solid="core")
    Z("az_scale_pile", 156, 178, 3, solid="core")
    W_("az_drowned_spire", 176, 194, 11)
    # ---- the north shore of Lake Mennar, and a column in the shallows
    Z("az_toppled_column", 52, 128, 5, solid="core")
    Z("az_moon_arch", 66, 124, 7, solid="core")


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_azshara_central():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS) + list(LATER_PORTALS),
                              npc=list(NPC_POSITIONS.values()))
