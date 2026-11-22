"""
Hand-built Dawnrest (90x76), levels 5-9: the old waystation on the road between Amberleaf Glade and Duskfall Woods, as
its own small map. Kyle, 22 Nov 2026: "For duskfall we can have a small town (just a little 'hub' near the entrance
between duskfall and amberleaf perhaps." The Conclave put a roof back on the outpost's old waystation and the camp grew
round it into a village: the Lightwarden and the Magister's tables under the roof, the huntress's lodge, an inn for the
people working the woods, the carpenters, and the newcomers walking up from the Waking Shore. The road runs straight
through it, so everyone going north to the woods passes the hearth on the way.

It's Dawnhaven's own style, autumn and blood elf (Duskfall's red woods and Kyle's DH sheets): the waystation and the be_
houses, Conclave banners, lamp posts, leaf piles and the red trees all round the clearing.

ORIENTATION FOLLOWS THE OVERWORLD. The road runs south to north: up from Amberleaf Glade into the south gate, out of the
north gate into the south of Duskfall Woods, exactly where the road always came in.

    the Glade Gate (45,73), south <- Amberleaf Glade's north road (75,4)
    the Woods Gate (45,2), north -> Duskfall Woods' Glade road (80,136)
    the Waystation: the old roofed waystation beside the road, the Lightwarden and the Magister
    the Huntress's Lodge: Lyra and the hunters, west
    the Ember Hearth: the inn and the mail, east
    the Quartermaster's Row: the quartermaster and the cook, along the road
    the Carpenters' Yard: the timber stock and the skiff on its stocks, south-east
    the Newcomers' Camp: bedrolls and a fire for the people walking up from the shore, south-west

HARD CONTRACTS (world/portal_manager.py)
  portals  (45,73) <-> Amberleaf Glade (75,4): arrive (45,69) coming up, (75,7) going back down
           (45,2) <-> Duskfall Woods (80,136): arrive (45,6) coming back, (80,133) going on into the woods
  NPC ids  dh_* and dr_*: written by tools/build_dawnhaven_people.py from NPC_POSITIONS
"""
import numpy as np

from tools import ashenvale_engine as E
from world.chunk_paths import exists as _chunk_exists  # noqa: E402  (.webp, .jpg or .png)

NAME = "Dawnrest"
BAKED_DIR = "assets/tiles/dawnhaven/baked_dawnrest"
AZP = "assets/tiles/azshara/props/"
BLD = "assets/buildings/"
DHP = "assets/tiles/dawnhaven/props/"
W, H = 90, 76

PORTALS = {(45, 73): "Amberleaf Glade", (45, 2): "Duskfall Woods"}
ARRIVALS = [(45, 69), (45, 6)]
START = (45, 69)

ROADS = {
    "road":   ([(45, 75), (45, 52), (44, 38), (45, 20), (45, 0)], 3.0),
    "lodge":  ([(44, 40), (30, 42), (18, 40)], 2.4),
    "hearth": ([(45, 34), (60, 32), (72, 34)], 2.4),
    "camp":   ([(45, 56), (30, 60), (20, 62)], 2.2),
    "yard":   ([(45, 58), (60, 62), (70, 64)], 2.2),
}

LAKES = {}
DEEP_SHRINK = {}


def sea(gx, gy):
    """No sea: the clearing's in the middle of the woods."""
    return np.full(np.shape(np.asarray(gx, float)), -99.0)


WOODS = [(8, 10, 7, 6, 0, 0.4), (82, 12, 7, 6, 0, 1.3), (6, 70, 6, 5, 0, 2.2), (84, 70, 6, 5, 0, 0.9)]
BELTS = []
CLEARINGS = [(45, 38, 30, 26), (45, 6, 8, 5), (45, 70, 8, 5)]
BLUEBELL_PATCHES = [(20, 60, 6, 4)]
CORRUPT_PATCHES = []
BURNED_PATCHES = []
LUSH = 0.9
GRADE = (1.24, 1.10)
PAVED_PATCHES = [(34, 35, 8, 5), (66, 34, 6, 4)]
GAPS = [("ell", 45, 6, 6, 4), ("ell", 45, 70, 6, 4), ("ell", 34, 36, 9, 6)]

SPEC = E.Spec(NAME, W, H, ROADS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea,
              woods=WOODS, belts=BELTS, clearings=CLEARINGS, rim={"east": 6, "west": 6}, gaps=GAPS,
              thicket=(0.86, 10.0, 1.6))

NPC_POSITIONS = {
    # the Waystation
    "dh_selanne": (30, 34),             # Lightwarden Selanne Dawnsworn: the Lightwell, and putting the outpost back
    "dh_aeron": (38, 35),               # Magister Aeron Ashveil: the wild magic, and what woke in it
    # the Huntress's Lodge
    "dh_lyra": (20, 44),                # Huntress Lyra Swiftbough: the Red Hollow
    "dh_dawnrest_hunter": (26, 46),     # townsfolk
    # the Ember Hearth
    "dr_innkeeper": (67, 37),           # the inn
    "mailbox_dr_innkeeper": (61, 38),   # the Ember Hearth's mailbox
    # the Quartermaster's Row
    "dh_dawnrest_trader": (49, 46),
    "dh_dawnrest_cook": (39, 47),       # Giulia Ferraro, a cook from Bologna, feeding Dawnrest
    # the Glade Gate and the Woods Gate
    "dh_dawnrest_guard": (49, 66),      # townsfolk
    # the Carpenters' Yard
    "dh_dawnrest_carpenter": (64, 60),  # townsfolk
    # the Newcomers' Camp
    "dh_dawnrest_newcomer": (24, 60),   # townsfolk
}
MAILBOX = NPC_POSITIONS["mailbox_dr_innkeeper"]


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}
SUBZONES = [
    ("Dawnrest", 0, 0, W, H, None),
    ("The Woods Gate", 34, 0, 22, 14, None),
    ("The Waystation", 22, 18, 22, 22, None),
    ("The Huntress's Lodge", 6, 30, 26, 22, None),
    ("The Ember Hearth", 58, 22, 26, 22, None),
    ("The Quartermaster's Row", 32, 40, 26, 12, None),
    ("The Newcomers' Camp", 6, 52, 30, 18, None),
    ("The Carpenters' Yard", 54, 52, 30, 18, None),
    ("The Glade Gate", 34, 62, 22, 14, None),
]

TREES = {
    "big":   [(DHP + "dh_autumn_tree.png", 10), (AZP + "az_autumn_tree.png", 11)],
    "mid":   [(DHP + "dh_autumn_tree.png", 9), (DHP + "dh_maple_sapling.png", 8)],
    "small": [(DHP + "dh_maple_sapling.png", 7), (AZP + "az_birch_trio.png", 7)],
    "woods": [(DHP + "dh_autumn_tree.png", 10), (AZP + "az_autumn_tree.png", 11), (DHP + "dh_autumn_tree.png", 9)],
}

#: the same low dusk light as the woods
SCREEN_LIGHT = {"layer": "light_dusk", "strength": 0.30, "breathe": 0.2}
SCREEN_PARTICLES = {"sprites": ["p_leaf_maple", "p_leaf_dry", "p_leaf_elven"], "count": 10,
                    "size": 0.55, "fall": 30, "wind": -12, "sway": 22, "spin": 70}


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "The old waystation on the road between the Glade and the woods, its roof back on, and the "
                             "village the Conclave's camp grew into round it.",
                             "Kalimdor - Dawnhaven", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.seal_unreachable(L, START)
    dress(L)
    E.build_free_mask(L, NPC_POSITIONS.values())
    for lm in L.z.landmarks:
        ax, ay, w, h = lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]
        L.free_mask[max(0, ay):ay + h + 1, max(0, ax - 1):ax + w + 1] = False
    L.free_mask[14:64, 12:78] = False           # the village itself: no wild trees among the houses
    E.scatter_trees(L, TREES, seed=6301, spacing=6.4, grove_keep=0.82)
    E.seal_unreachable(L, START)
    E.register_subzones(L, SUBZONES)
    L.z.is_town = True          # a small town: safe, no gathering, the inn and the mail (the island's flight is the Spire's)
    return L


def dress(L):
    B = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=BLD, **kw)          # noqa: E731
    K = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=DHP, **kw)          # noqa: E731

    # ---- the Waystation
    B("dh_dawnrest", 33, 30, 10, solid="core")
    K("dh_conclave_banner", 25, 31, 5, solid="core")
    K("dh_conclave_banner", 41, 31, 5, solid="core")
    K("dh_camp_hearth", 34, 37, 3, solid=False)
    # ---- the Huntress's Lodge
    B("be_house_small", 16, 40, 6, solid="core")
    K("dh_weapon_rack", 26, 39, 3, solid="core")
    K("dh_training_dummy", 12, 48, 3, solid="core")
    # ---- the Ember Hearth
    B("be_inn", 70, 33, 8, solid="core")
    K("dh_inn_table", 74, 39, 3, solid="core")
    K("dh_lamp_post", 59, 32, 4, solid="core")
    # ---- the Quartermaster's Row
    B("be_market_stall", 53, 44, 4, solid="core")
    K("dh_stall_fruit", 36, 44, 4, solid="core")
    K("dh_sun_crates", 57, 47, 3, solid="core")
    # ---- the Newcomers' Camp
    K("dh_bedrolls", 18, 58, 3, solid=False)
    K("dh_camp_hearth", 28, 62, 3, solid=False)
    B("be_pavilion", 16, 64, 6, solid="core")
    # ---- the Carpenters' Yard
    K("dh_building_stock", 70, 58, 3, solid="core")
    K("dh_wrecked_skiff", 72, 66, 4, solid="core")
    B("be_storehouse", 58, 56, 6, solid="core")
    K("dh_handcart", 66, 64, 3, solid="core")
    # ---- the houses along the road, the people who've stayed
    B("be_house_small", 18, 26, 6, solid="core")
    B("be_house_medium", 62, 24, 7, solid="core")
    B("be_house_small", 30, 54, 6, solid="core")
    K("dh_street_lamp", 41, 20, 4, solid="core")
    K("dh_street_lamp", 49, 56, 4, solid="core")
    K("dh_notice_board", 49, 12, 4, solid="core")
    K("dh_leaf_pile", 22, 30, 3, solid=False)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and _chunk_exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_dawnrest():
    L = build_layout()
    register_baked(L.zone)
    L.zone.light = dict(SCREEN_LIGHT)
    L.zone.particles = dict(SCREEN_PARTICLES)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
