"""
Hand-built Amberleaf Glade (150x130), levels 1-6: the southern end of Dawnhaven, the blood elves' island off Azshara,
where new arrivals wake (docs/dawnhaven_brief.md).

Kyle, 21 Nov 2026: "an island off the coast of Azshara. Has a level 1-6 and a level 5-9 zone that eventually has a
boat to take you to Durotar from their main city", "the zones should be autumn style, very azshara / fall / bloodelf",
and "A story of survival, rebirth, and progress". The island was a high elf outpost long before the change; the
Sunreach Conclave has taken it back, and it takes in whoever wakes up on its shore.

    The Waking Shore .... the south beach (75,112): where the sea gives up the people the change brings
    Amberwatch .......... the hub (75,88): the Conclave's camp in the outpost's ruined outer gatehouse
    Leafwhisper Grove ... the west (34,78): old gold woods, lynxes and boars and stags
    Amberleaf Mere ...... the lake (48,52)
    The Fallen Wardstones the east (116,52): the outpost's broken ward pylons, where the mana wyrms feed and the
                          leaves get up and walk
    Brinecoil Cove ...... the south-east (122,100): the naga's landing, and their sea cave, Brinecoil Grotto (126,94)
    The Silent Barrow ... the north-west (34,26): the outpost's burial ground, and the vault under it, the Quiet
                          Vault (34,20)
    The Duskfall road ... north edge (75,4): on into Duskfall Woods

THE ART is Kyle's Azshara sheets for now (tools/bake_ashenvale.py dawnhaven_amberleaf paints from AZSHARA_SHEET), the
be_ blood elf buildings, and Azshara's trees and ruins. Kyle: "Existing art now, sheets later".

HARD CONTRACTS (world/portal_manager.py)
  portals  Duskfall Woods (75,4) <-> its south road (80,136); Brinecoil Grotto (126,94) <-> its way out;
           the Quiet Vault (34,20) <-> its way out
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_central_barrens import _gauss
from world.chunk_paths import exists as _chunk_exists  # noqa: E402  (.webp, .jpg or .png)

NAME = "Amberleaf Glade"
BAKED_DIR = "assets/tiles/dawnhaven/baked_amberleaf"
AZP = "assets/tiles/azshara/props/"
BLD = "assets/buildings/"
DHP = "assets/tiles/dawnhaven/props/"           # Kyle's DH2 and DH4 (docs/dawnhaven_art_prompts.md)
W, H = 150, 130

PORTALS = {(75, 4): "Duskfall Woods", (126, 94): "Brinecoil Grotto", (34, 20): "The Quiet Vault"}
ARRIVALS = [(75, 7), (126, 97), (34, 23)]
START = (75, 110)      # the Waking Shore: where a new arrival stands up

# ------------------------------------------------------------------ the plan
ROADS = {
    # up off the beach to Amberwatch
    "shore":  ([(75, 113), (75, 104), (74, 95), (75, 88)], 3.2),
    # north from Amberwatch, past the mere and the wardstones' turn, to Duskfall Woods
    "north":  ([(75, 88), (73, 76), (76, 62), (78, 48), (76, 34), (75, 18), (75, 4)], 3.2),
    # west into Leafwhisper Grove
    "grove":  ([(73, 87), (60, 85), (46, 81), (34, 78)], 2.8),
    # east to the Fallen Wardstones
    "wards":  ([(77, 58), (92, 56), (106, 54), (116, 52)], 2.8),
    # south-east to Brinecoil Cove and the grotto's mouth
    "cove":   ([(78, 92), (94, 96), (108, 100), (120, 101), (126, 96)], 2.6),
    # north-west to the Silent Barrow and the Quiet Vault
    "barrow": ([(76, 36), (60, 32), (46, 27), (34, 22)], 2.6),
}

LAKES = {"mere": [(48, 52, 9, 6, 0.2, 0.9)]}
DEEP_SHRINK = {"mere": 2.4}


def coast_south(gx):
    """The south shore: the Waking Shore's long beach in the middle, and Brinecoil Cove biting north in the east."""
    gx = np.asarray(gx, float)
    return (119.0 + 1.5 * np.sin(0.13 * gx) + 1.0 * np.sin(0.31 * gx + 1.0) - 9.0 * _gauss(gx, 124, 9)
            + 4.0 * _gauss(gx, 30, 14))


def coast_east(gy):
    gy = np.asarray(gy, float)
    return 140.0 + 2.0 * np.sin(0.17 * gy) + 1.2 * np.sin(0.41 * gy + 0.6) - 8.0 * _gauss(gy, 100, 8)


def coast_west(gy):
    gy = np.asarray(gy, float)
    return 7.0 + 2.0 * np.sin(0.21 * gy + 0.4) + 5.0 * _gauss(gy, 62, 12)


def sea(gx, gy):
    """The sea round three sides; the north runs on into Duskfall Woods. Extent > 0 is sea."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    return np.maximum.reduce([gy - coast_south(gx), gx - coast_east(gy), coast_west(gy) - gx])


# ---- woods (impassable gold and red forest): (cx, cy, rx, ry, rot, phase)
WOODS = [
    (30, 100, 7, 5, 0, 1.0), (112, 76, 9, 7, 0, 2.0), (100, 22, 7, 6, 0, 0.6), (50, 12, 9, 5, 0, 1.4),
    (96, 74, 5, 4, 0, 2.4), (60, 66, 5, 4, 0, 1.2), (98, 40, 5, 5, 0, 2.2),
]
BELTS = []
CLEARINGS = [   # carved back out of the woods
    (75, 88, 13, 9),            # Amberwatch
    (75, 110, 14, 6),           # the Waking Shore
    (34, 78, 12, 9),            # Leafwhisper Grove
    (116, 52, 12, 10),          # the Fallen Wardstones
    (34, 26, 12, 9),            # the Silent Barrow
    (120, 100, 10, 7),          # Brinecoil Cove
    (75, 9, 8, 6),              # the Duskfall road out
    (48, 52, 13, 9),            # Amberleaf Mere
]
BLUEBELL_PATCHES = [(34, 78, 9, 6), (48, 52, 12, 8), (75, 88, 9, 6)]      # moss and toadstools under the gold trees
CORRUPT_PATCHES = [(34, 26, 9, 6)]          # the barrow's dead ground
BURNED_PATCHES = []
LUSH = 1.0
GRADE = (1.28, 1.13)
PAVED_PATCHES = [(75, 88, 6, 4), (116, 52, 6, 4), (34, 26, 5, 3)]          # the outpost's old paving

GAPS = [
    ("ell", 75, 6, 7, 6), ("ell", 126, 96, 6, 5), ("ell", 34, 22, 6, 5), ("ell", 75, 88, 9, 7),
    ("ell", 75, 110, 10, 5), ("ell", 116, 52, 8, 6),
]


class _Spec(E.Spec):
    """No woods on the beach or in the sea."""

    def woods_raw(self, gx, gy):
        out = super().woods_raw(gx, gy)
        sh, _dp = self.water_fields(gx, gy)
        return np.minimum(out, -(np.asarray(sh) + 3.0))


SPEC = _Spec(NAME, W, H, ROADS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea,
             woods=WOODS, belts=BELTS, clearings=CLEARINGS, rim={"north": 6}, gaps=GAPS,
             thicket=(0.80, 10.0, 0.4))

#: the people (tools/build_dawnhaven_people.py writes them from here)
NPC_POSITIONS = {
    # the Waking Shore: the ranger who meets every new arrival, and the first person you talk to
    "dh_saelis": (78, 108),
    # Amberwatch, the Conclave's camp in the old gatehouse
    "dh_iriel": (69, 85),           # Magistrix Iriel Brightleaf: the wards and the wyrms
    "dh_thaelen": (82, 91),         # Apothecary Thaelen: herbs, the sick, the dead
    "dh_rosa": (66, 92),            # Rosa Quintero, a carpenter from Valparaiso, putting roofs back on
    "dh_kaelen": (80, 84),          # Scout Kaelen Swiftarrow: the coast and the naga
    "dh_amberwatch_trader": (87, 87),
    "ct_amberwatch": (64, 86),
    "pt_dawnhaven_herbs": (84, 95),
    "pt_dawnhaven_forge": (68, 96),
    "pt_dawnhaven_skins": (56, 90),
    # the priestess who keeps the names of the outpost's dead, at the memorial stone in camp
    "dh_aldaria": (74, 97),
    # the island's recruits (Yiannis on the shore, Rhodri at Amberwatch): tools/build_sheet7_recruits.py
    "dh_shore_newcomer_a": (72, 115),  # townsfolk
    "dh_shore_newcomer_b": (80, 114),  # townsfolk
    "dh_amberwatch_gate": (75, 81),  # townsfolk
    "dh_amberwatch_sentry": (59, 97),  # townsfolk
    "dh_amberwatch_hauler": (72, 90),  # townsfolk
    "dh_rosa_helper": (64, 95),  # townsfolk
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {(126, 94): ("ent_sea_cave", 9, 7), (34, 20): ("ent_crypt_mausoleum", 8, 7)}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("The Duskfall Road", 58, 0, 34, 24, None),
    ("The Silent Barrow", 12, 8, 42, 34, None),
    ("Amberleaf Mere", 32, 40, 34, 26, None),
    ("The Fallen Wardstones", 94, 36, 50, 32, None),
    ("Leafwhisper Grove", 10, 64, 44, 34, None),
    ("Brinecoil Cove", 102, 84, 46, 40, None),
    ("The Waking Shore", 48, 102, 58, 28, None),
    ("Amberwatch", 60, 78, 30, 20, None),
]

TREES = {
    "big":   [(AZP + "az_gold_tree.png", 10), (DHP + "dh_autumn_tree.png", 10), (AZP + "az_gold_tree.png", 11)],
    "mid":   [(AZP + "az_gold_tree.png", 8), (DHP + "dh_autumn_tree.png", 9), (DHP + "dh_maple_sapling.png", 8)],
    "small": [(DHP + "dh_maple_sapling.png", 7), (AZP + "az_birch_trio.png", 7)],
    "woods": [(AZP + "az_gold_tree.png", 10), (DHP + "dh_autumn_tree.png", 9), (AZP + "az_gold_tree.png", 11)],
}

#: gold light through the canopy (Kyle, 21 Nov 2026, on the sky's sunbeams: "They give a sense of depth")
SCREEN_LIGHT = {"layer": "light_autumn_rays", "strength": 0.42, "breathe": 0.18}
#: leaf shadow on the ground, and leaves coming down (docs/environment_effects_art_prompts.md)
SCREEN_SHADE = {"layer": "shade_canopy_dapple", "strength": 0.32, "tile": 11, "drift": (2.0, 0.5)}
SCREEN_PARTICLES = {"sprites": ["p_leaf_maple", "p_leaf_aspen", "p_leaf_oak", "p_leaf_elven"], "count": 12,
                    "size": 0.55, "fall": 34, "wind": 14, "sway": 24, "spin": 80}


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "The south of Dawnhaven, gold and red to the shore, where the sea gives up the people the "
                             "change brings. The Sunreach Conclave keeps a camp in the old outpost's gatehouse.",
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
    E.scatter_trees(L, TREES, seed=6101, spacing=7.0, grove_keep=0.80)
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def sprinkle(L):
    """Ground clutter, a little: crimson brush, fallen logs, lichened stones."""
    import random
    rnd = random.Random(6103)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    bush = logs = rocks = 0
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        if bush < 22 and r < 0.014:
            if L.prop("dh_crimson_shrub", x, y, 3, path_dir=DHP, solid=False, nudge=0):
                bush += 1
        elif logs < 14 and r < 0.040:
            if L.prop("dh_red_log", x, y, 3, path_dir=DHP, solid=False, nudge=0):
                logs += 1
        elif rocks < 16 and r < 0.050:
            if L.prop("az_lichen_boulder", x, y, 4, path_dir=AZP, solid=False, nudge=0):
                rocks += 1
    L.clutter = (bush, logs, rocks)


CHEST_SPOTS = [(22, 76), (54, 40), (96, 30), (132, 60), (110, 112), (40, 112), (64, 20), (88, 70)]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    P = L.prop
    Z = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=AZP, **kw)          # noqa: E731
    B = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=BLD, **kw)          # noqa: E731
    D = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir="assets/tiles/dungeon_props/", **kw)  # noqa: E731
    K = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=DHP, **kw)          # noqa: E731
    H = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir="assets/tiles/haunted_forest/props/", **kw)  # noqa: E731

    # ---- the Waking Shore: what the tide leaves, and the ranger's lookout over it
    Z("az_wreck_prow", 92, 114, 5, solid="core")
    Z("az_relic_crate", 62, 112, 3, solid="core")
    Z("az_giant_clam", 54, 116, 3, solid=False)
    B("be_guard_post", 84, 104, 6, solid="core")
    # ---- Amberwatch: the outpost's outer gatehouse, half standing, with the Conclave's camp in its lee
    B("dh_amberwatch_gate", 75, 80, 9, solid="core")
    B("be_command_tent", 66, 82, 6, solid="core")
    B("be_pavilion", 86, 92, 6, solid="core")
    B("be_market_stall", 88, 84, 4, solid="core")
    B("be_ruined_house", 60, 94, 6, solid="core")
    Z("az_dig_scaffold", 63, 97, 5, solid="core")        # Rosa's roof going back on
    K("dh_sun_crates", 70, 97, 3, solid="core")
    K("dh_conclave_banner", 81, 82, 4, solid="core")
    K("dh_camp_hearth", 78, 89, 3, solid=False)
    K("dh_bedrolls", 64, 88, 3, solid="core")
    P("br_signpost", 79, 98, 4)
    # ---- Leafwhisper Grove: old gold woods round a fallen statue
    K("dh_toppled_ranger", 30, 74, 4, solid="core")
    Z("az_toppled_column", 40, 74, 4, solid="core")
    # ---- Amberleaf Mere: an elven boat-stair going down into the water
    K("dh_broken_arch", 40, 46, 5, solid="core")
    Z("az_moon_arch", 58, 46, 6, solid="core")
    # ---- the Fallen Wardstones: the ward pylons, broken, and the leyline still running under them
    K("dh_wardstone_broken", 110, 46, 6, solid="core")
    K("dh_wardstone_broken", 124, 48, 6, solid="core")
    Z("az_broken_spire", 116, 44, 9, solid="core")
    K("dh_wardstone_lit", 112, 58, 5, solid="core")      # the one stone the Conclave has woken
    Z("az_arcane_crystal", 122, 58, 4, solid="core")
    Z("az_toppled_column", 104, 52, 4, solid="core")
    # ---- Brinecoil Cove: the naga's landing on the beach
    K("dh_naga_totem", 114, 104, 5, solid="core")
    Z("az_tide_altar", 118, 108, 4, solid="core")
    Z("az_scale_pile", 108, 106, 3, solid=False)
    Z("az_coral_cluster", 130, 104, 4, solid="core")
    # ---- the Silent Barrow: the outpost's dead, and the stone that names them
    B("be_ruined_tower", 22, 22, 9, solid="core")
    Z("az_ruin_wall", 44, 22, 4, solid="core")
    H("crypt_mausoleum", 26, 32, 6, solid="core")
    D("broken_column", 40, 34, 4, solid="core")
    K("dh_memorial_stone", 30, 34, 4, solid="core")
    K("dh_spirit_lantern", 34, 28, 5, solid=False)
    # ---- the Duskfall road out: an elven arch over it
    Z("az_moon_arch", 75, 12, 7, solid=False, road_ok=True)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and _chunk_exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_amberleaf_glade():
    L = build_layout()
    register_baked(L.zone)
    L.zone.light = dict(SCREEN_LIGHT)
    L.zone.shade = dict(SCREEN_SHADE)
    L.zone.particles = dict(SCREEN_PARTICLES)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
