"""
Hand-built East Azshara (200x200), levels 56-59: the coast, where Zin-Azshari is coming up out of the sea
(docs/azshara_brief.md).

Kyle, 17 Nov 2026: "The drowned shore where Zin-Azshari comes up: reefs, temple ruins, the Tower of Eldara. Later the
risen district, and the Vault's door in it." And the palette: "The East coast turns to drowned teal and silver, with
wet white marble and coral, as the city comes up."

THE DISTRICT HAS ALREADY RISEN. The brief first had it come up mid-questline (a save-flag swap). Kyle, 18 Nov 2026: "i
dont want change with quests - too much work and will fuck up on prestige". So the Drowned Court is permanent ground,
joined to the promenade by a causeway, and every run sees the same coast. The rising is story: it came up with the
Integration, and the naga came up with it.

So the map runs from Central's autumn forest on the west into shell silt, wet marble and coral on the shore, with the
open sea down the whole east side:

    West road ............ west edge (4,130): from Central Azshara's east road (196,130)
    Stormwatch ........... the crossroads (92,112): a Horde lookout over the coast road
    The Bitter Reaches ... the north coast: storm surf, wrecks and naga
    Tower of Eldara ...... the northern cape: the Highborne tower, still standing, still humming
    The Drowned Promenade  the middle of the shore: a Highborne boulevard running into the sea, walked by ghosts who
                           think it's ten thousand years ago
    The Drowned Court .... offshore from the promenade, over a causeway: a district of Zin-Azshari that came up out of
                           the sea, still wet, its spires standing in tide pools. The Vault's door (178,92) is in it
    Temple of Zin-Malor .. the southern headland: a sea temple the naga have taken back
    The Jagged Reef ...... the rocks off the south-east coast

THE ART is Kyle's Azshara sheets (docs/azshara_art_prompts.md): tools/bake_ashenvale.py azshara_east paints the ground
from sheet 1 (AZSHARA_EAST_SHEET: wet and barnacled marble for the paving, drowned mosaic in the temple and on the
promenade, coral stone, tide-pool rock, and shell silt washing up from the shore through `satyr_field`), and the
props are sheet 2's. Trees stop where the forest does.

HARD CONTRACTS (world/portal_manager.py)
  portals  Central Azshara (4,130) <-> its east road (196,130). Later the Vault of Zin-Azshari (178,92), in
           LATER_PORTALS until the dungeon exists
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_central_barrens import _gauss, _smooth

BAKED_DIR = "assets/tiles/azshara/baked_east"
AZP = "assets/tiles/azshara/props/"      # Kyle's Azshara props sheet (sheet 2)
BLD = "assets/buildings/"                # the Landing's camp pieces (sheet 3)
W, H = 200, 200

PORTALS = {(4, 130): "Central Azshara"}
ARRIVALS = [(6, 130)]
#: the door whose map comes later: the Vault of Zin-Azshari, at the head of the Drowned Court
LATER_PORTALS = {(178, 92): "The Vault of Zin-Azshari"}
START = (92, 114)      # Stormwatch: everything must be reachable from here
FOREST_EDGE = 104      #: trees stop east of a wavy line round here (forest_edge); the shore is open


def forest_edge(gy):
    """Where the forest gives out to the shore: a ragged line, not a ruled one."""
    gy = np.asarray(gy, float)
    return FOREST_EDGE + 8.0 * np.sin(0.07 * gy + 0.5) + 4.0 * np.sin(0.19 * gy + 1.3) + 2.0 * np.sin(0.41 * gy)

# ------------------------------------------------------------------ the plan
ROADS = {
    # in from Central to Stormwatch
    "west":      ([(4, 130), (24, 128), (46, 124), (70, 118), (92, 112)], 3.4),
    # north-east along the old Highborne road to the Tower of Eldara on the cape
    "eldara":    ([(92, 112), (104, 92), (120, 72), (140, 54), (158, 40), (172, 34)], 3.0),
    # off the Eldara road down to the Bitter Reaches
    "reaches":   ([(120, 72), (126, 52), (132, 36), (138, 26)], 2.6),
    # east to the Drowned Promenade, over the causeway, and up the Drowned Court to the Vault's door
    "promenade": ([(92, 112), (116, 112), (134, 112), (148, 110)], 3.2),
    "court":     ([(148, 110), (158, 110), (168, 112), (176, 106), (178, 96), (178, 92)], 3.0),
    # south-east to the Temple of Zin-Malor on the headland
    "temple":    ([(116, 112), (122, 134), (130, 152), (146, 164), (162, 170)], 2.8),
}

LAKES = {
    "tarn": [(40, 92, 7, 5, 0, 0.5)],
    "pools": [(128, 142, 4, 3, 0, 0.4), (132, 84, 3.5, 2.5, 0, 1.1), (110, 164, 8, 5, 20, 0.8)],   # tide pools, a lagoon
}
DEEP_SHRINK = {"tarn": 2.2, "pools": 1.8}


def coast_x(gy):
    """The east shore: the northern cape (the Tower of Eldara), a bay under it, the long middle shore facing the
    Drowned Court, then the southern headland (the Temple of Zin-Malor) and a cove under that."""
    return (152.0 + 38.0 * _gauss(gy, 30, 14) - 14.0 * _gauss(gy, 60, 11) + 22.0 * _gauss(gy, 168, 10)
            - 10.0 * _gauss(gy, 192, 7) + 1.8 * np.sin(0.23 * gy + 0.6) + 1.1 * np.sin(0.47 * gy + 1.3))


def sea(gx, gy):
    """The open sea down the east, and the north coast (the Bitter Reaches) east of x~120. Extent > 0 is sea."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    east = gx - coast_x(gy)
    north = (-40.0 + 56.0 * _smooth(100, 140, gx) + 1.8 * np.sin(0.19 * gx + 0.3) + 1.0 * np.sin(0.43 * gx)) - gy
    return np.maximum(east, north)


#: the Drowned Court (the risen district) and the causeway out to it: land standing in the sea
ISLETS = [(177, 110, 15, 22, 0, 0.9), (157, 110, 9, 3.2, 0, 0.0)]

# ---- rock: a hill in the north-west woods, one in the south-west, and the Jagged Reef's rocks standing in the sea
#: none: rock reads as a pit on this ground (and under the sea), so the Jagged Reef is coral and stone standing in the
#: water (dress), and the forest's high ground is woods
MESAS = []
RIDGES = []

# ---- woods (impassable autumn forest), all in the west half: (cx, cy, rx, ry, rot, phase)
WOODS = [
    (24, 100, 10, 8, 0, 1.0), (30, 160, 10, 9, 0, 2.0), (60, 64, 10, 8, 0, 0.6), (76, 150, 9, 7, 0, 1.4),
    (100, 142, 8, 7, 0, 0.9), (86, 40, 9, 7, 0, 2.4), (20, 60, 8, 8, 0, 1.7), (64, 92, 7, 6, 0, 0.3),
    (40, 40, 11, 9, 0, 2.1), (60, 172, 9, 7, 0, 1.2),
]
BELTS = [
    ([(0, 195), (60, 197), (120, 195), (140, 193)], 6.0),                  # the south rim
    ([(0, 4), (60, 3), (100, 6)], 6.0),                                     # the north rim, west of the coast
]
CLEARINGS = [   # carved back out of the woods
    (92, 112, 10, 8),           # Stormwatch
    (8, 130, 9, 7),             # the west road in
    (40, 92, 11, 8),            # the tarn
]
#: open ground the tree scatter leaves alone, on top of everything east of forest_edge()
OPEN_GROUND = [(92, 112, 8, 6), (40, 92, 10, 7)]

BLUEBELL_PATCHES = [(146, 96, 5, 4), (148, 128, 5, 4), (166, 158, 5, 4), (164, 44, 5, 4)]   # coral stone
LUSH = 0.6
GRADE = (1.26, 1.12)
PAVED_PATCHES = [(140, 110, 9, 13), (160, 168, 11, 7), (172, 34, 7, 5),      # wet marble
                 (177, 110, 13, 20), (157, 110, 8, 2.5)]                       # ...all through the Drowned Court
MOSAICS = [(143, 110, 3, 6), (162, 168, 5, 3), (178, 116, 5, 4), (178, 96, 3, 3)]   # the drowned mosaic floors

GAPS = [
    ("ell", 4, 130, 8, 7), ("ell", 92, 112, 9, 7), ("ell", 172, 34, 8, 6), ("ell", 160, 168, 10, 7),
    ("ell", 178, 94, 5, 4),
]


class _Spec(E.Spec):
    """No woods in the water, and none on the shore: the forest thins out to the east and stops at forest_edge()."""

    def woods_raw(self, gx, gy):
        out = super().woods_raw(gx, gy)
        sh, _dp = self.water_fields(gx, gy)
        out = np.minimum(out, -(np.asarray(sh) + 2.5))
        return out - 0.6 * np.clip(np.asarray(gx, float) - (forest_edge(gy) - 20), 0, None)


SPEC = _Spec("East Azshara", W, H, ROADS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
             mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
             rim={"west": 6}, gaps=GAPS, thicket=(0.74, 10.0, 1.1))

#: Most of Azshara's quests are given in its two hubs (Kyle's ~70%); the open-world people come with the quest pass.
NPC_POSITIONS = {}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


def plaza_field(P, wp):
    """The baker's plaza layer: the drowned mosaic floors (AZSHARA_EAST_SHEET)."""
    return np.maximum.reduce([P.blob(*m, 0.6, wp) for m in MOSAICS])


def satyr_field(P, wp):
    """The baker's satyr layer, used here for SHELL SILT washing up from the shore: none in the forest, more and more
    toward the sea (AZSHARA_EAST_SHEET maps it to az_shell_silt)."""
    gx = P.gx
    toward = _smooth(-10.0, 16.0, gx - forest_edge(P.gy) + 6.0 * (P.noise(6.0, "silt", octaves=2) - 0.5))
    return toward * (0.7 + 0.3 * _smooth(0.3, 0.7, P.noise(2.5, "siltfine", octaves=2)))


CAVES = {}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("Stormwatch", 72, 96, 40, 32, None),
    ("The Bitter Reaches", 110, 4, 56, 40, None),
    ("Tower of Eldara", 150, 10, 50, 40, None),
    ("The Drowned Promenade", 126, 88, 30, 46, None),
    ("The Drowned Court", 160, 84, 40, 52, None),
    ("Temple of Zin-Malor", 132, 150, 50, 36, None),
    ("The Jagged Reef", 164, 132, 36, 68, None),
]

TREES = {
    "big":   [(AZP + "az_autumn_tree.png", 10), (AZP + "az_gold_tree.png", 9), (AZP + "az_autumn_tree.png", 11)],
    "mid":   [(AZP + "az_gold_tree.png", 8), (AZP + "az_autumn_tree.png", 9), (AZP + "az_birch_trio.png", 8)],
    "small": [(AZP + "az_birch_trio.png", 7), (AZP + "az_gold_tree.png", 7)],
    "woods": [(AZP + "az_autumn_tree.png", 10), (AZP + "az_gold_tree.png", 9), (AZP + "az_autumn_tree.png", 11)],
}


def build_layout():
    AL = E.make_layout_class(SPEC, "East Azshara",
                             "Azshara's drowned coast, where the forest gives out to wet marble and coral and the "
                             "old capital is coming up out of the sea, one spire at a time.",
                             "Kalimdor - Azshara", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.seal_unreachable(L, START)
    dress(L)
    E.build_free_mask(L, NPC_POSITIONS.values())
    for lm in L.z.landmarks:
        ax, ay, w, h = lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]
        L.free_mask[max(0, ay):ay + h + 1, max(0, ax - 1):ax + w + 1] = False
    shore_mask = L.free_mask.copy()
    ys, xs = np.mgrid[0:H, 0:W]
    shore = xs >= forest_edge(ys)
    L.free_mask[shore] = False
    for (cx, cy, rx, ry) in OPEN_GROUND:
        L.free_mask[((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2 < 1.0] = False
    E.scatter_trees(L, TREES, seed=5601, spacing=5.8, grove_keep=0.68)
    forest_mask = L.free_mask
    L.free_mask = (shore_mask & forest_mask) | (shore_mask & shore)
    L.shore = shore
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def sprinkle(L):
    """Ground clutter: logs and bushes in the forest; shells, coral and scale piles on the shore."""
    import random
    rnd = random.Random(5603)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = {"bush": 0, "log": 0, "rock": 0, "coral": 0, "clam": 0, "scale": 0}
    cap = {"bush": 14, "log": 12, "rock": 18, "coral": 16, "clam": 10, "scale": 8}
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        shore = bool(L.shore[y, x])
        if shore:
            kind, name, h = (("coral", "az_coral_cluster", 3) if r < 0.010 else
                             ("clam", "az_giant_clam", 3) if r < 0.016 else
                             ("scale", "az_scale_pile", 3) if r < 0.020 else
                             ("rock", "az_lichen_boulder", 3) if r < 0.026 else (None, None, 0))
        else:
            kind, name, h = (("bush", "az_crimson_bush", 3) if r < 0.012 else
                             ("log", "az_autumn_log", 3) if r < 0.036 else
                             ("rock", "az_lichen_boulder", 4) if r < 0.046 else (None, None, 0))
        if kind and n[kind] < cap[kind]:
            if L.prop(name, x, y, h, path_dir=AZP, solid=False, nudge=0):
                n[kind] += 1
    L.clutter = n


CHEST_SPOTS = [
    (20, 120), (52, 80), (70, 40), (104, 60), (138, 80), (180, 40), (130, 100), (124, 140), (152, 150),
    (40, 140), (88, 170), (166, 180),
]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    P = L.prop
    B = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=BLD, **kw)         # noqa: E731
    Z = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=AZP, **kw)         # noqa: E731
    W_ = lambda n, x, y, h: L.deco(n, x, y, h, path_dir=AZP)                     # noqa: E731  (standing in the sea)

    # ---- the roads: signposts
    P("br_signpost", 12, 124, 5)
    P("br_signpost", 120, 78, 4)
    P("br_signpost", 120, 118, 4)
    # ---- Stormwatch: a Horde lookout over the coast road
    B("tl_log_watchtower", 86, 106, 10, solid="core")
    B("tl_war_tent", 98, 104, 6, solid="core")
    B("tl_shared_fire", 94, 118, 4, solid="core")
    B("tl_sandbags", 102, 116, 3, solid="core")
    B("tl_notice_board", 84, 118, 4, solid="core")
    # ---- Tower of Eldara: the Highborne tower on the cape, still standing, still humming
    Z("az_mana_tower", 178, 30, 16, solid="core")
    Z("az_broken_spire", 166, 28, 10, solid="core")
    Z("az_moon_arch", 170, 42, 8, solid="core")
    Z("az_noble_statue", 156, 32, 7, solid="core")
    Z("az_noble_statue", 186, 30, 7, solid="core")
    Z("az_arcane_crystal", 188, 36, 5, solid="core")
    Z("az_leyline_node", 162, 36, 5, solid="core")
    Z("az_ruin_wall", 156, 24, 5, solid="core")
    # ---- the Bitter Reaches: storm surf, wrecks, naga
    Z("az_wreck_prow", 130, 22, 6, solid="core", shore_ok=True)
    Z("az_naga_banner", 142, 28, 6, solid="core")
    Z("az_tide_altar", 136, 30, 5, solid="core")
    Z("az_scale_pile", 146, 32, 3, solid="core")
    Z("az_coral_cluster", 126, 28, 4, solid="core")
    W_("az_wreck_prow", 150, 10, 7)
    # ---- the Drowned Promenade: a Highborne boulevard running down into the sea
    Z("az_moon_arch", 140, 100, 8, solid="core")
    Z("az_moon_arch", 140, 122, 8, solid="core")
    Z("az_noble_statue", 136, 104, 7, solid="core")
    Z("az_noble_statue", 136, 118, 7, solid="core")
    Z("az_dry_fountain", 144, 112, 5, solid="core")
    Z("az_toppled_column", 130, 100, 5, solid="core")
    Z("az_toppled_column", 132, 124, 5, solid="core")
    Z("az_barnacle_statue", 148, 98, 7, solid="core", shore_ok=True)
    Z("az_barnacle_statue", 148, 124, 7, solid="core", shore_ok=True)
    Z("az_ruin_wall", 128, 108, 5, solid="core")
    # ---- the Drowned Court: the district that came up, still wet, its spires standing in tide pools
    Z("az_drowned_spire", 168, 100, 14, solid="core")
    Z("az_drowned_spire", 188, 108, 13, solid="core")
    Z("az_drowned_spire", 170, 126, 12, solid="core")
    Z("az_drowned_spire", 186, 124, 11, solid="core")
    Z("az_drowned_obelisk", 166, 106, 7, solid="core")
    Z("az_drowned_obelisk", 166, 118, 7, solid="core")
    Z("az_coral_arch", 172, 114, 7, solid="core")
    Z("az_barnacle_statue", 172, 94, 7, solid="core")       # the two who still guard the Vault's door
    Z("az_barnacle_statue", 184, 94, 7, solid="core")
    Z("az_moon_arch", 178, 90, 9, solid=False, road_ok=True)     # the Vault's door (opens with the dungeon)
    Z("az_coral_cluster", 182, 116, 4, solid="core")
    Z("az_giant_clam", 176, 128, 3, solid="core")
    Z("az_toppled_column", 184, 102, 5, solid="core")
    Z("az_tide_altar", 178, 120, 5, solid="core")
    # ...and more of the city still under the water round it
    W_("az_drowned_spire", 194, 92, 10)
    W_("az_drowned_spire", 160, 136, 10)
    W_("az_drowned_obelisk", 194, 132, 7)
    # ---- Temple of Zin-Malor: a sea temple on the headland, the naga's now
    Z("az_broken_spire", 166, 162, 12, solid="core")
    Z("az_drowned_obelisk", 152, 164, 7, solid="core")
    Z("az_drowned_obelisk", 170, 176, 7, solid="core")
    Z("az_coral_arch", 160, 160, 7, solid="core")
    Z("az_barnacle_statue", 154, 174, 7, solid="core")
    Z("az_tide_altar", 162, 170, 5, solid="core")
    Z("az_naga_banner", 150, 170, 6, solid="core")
    Z("az_naga_banner", 174, 166, 6, solid="core")
    Z("az_giant_clam", 168, 172, 3, solid="core")
    # ---- the Jagged Reef: coral and stone breaking the surface, and a wreck caught on them
    for (x, y, n, h) in ((172, 140, "az_coral_cluster", 4), (176, 142, "az_lichen_boulder", 4),
                         (186, 150, "az_coral_cluster", 4), (183, 152, "az_lichen_boulder", 3),
                         (192, 170, "az_coral_cluster", 4), (178, 186, "az_lichen_boulder", 4),
                         (174, 188, "az_coral_cluster", 3), (188, 160, "az_lichen_boulder", 3),
                         (166, 192, "az_coral_cluster", 3), (194, 182, "az_drowned_obelisk", 6)):
        W_(n, x, y, h)
    W_("az_wreck_prow", 182, 180, 7)
    # ---- Highborne stones in the forest
    Z("az_toppled_column", 58, 110, 5, solid="core")
    Z("az_ruin_wall", 36, 132, 5, solid="core")
    Z("az_moon_arch", 106, 86, 7, solid="core")


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_azshara_east():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS) + list(LATER_PORTALS),
                              npc=list(NPC_POSITIONS.values()))
