"""
Hand-built West Azshara (200x200), levels 52-55: the autumn forest where Azshara meets Ashenvale and Orgrimmar
(docs/azshara_brief.md).

Kyle, 17 Nov 2026: Azshara is three maps (West 52-55, Central 54-57, the East coast 56-59) with "a frontier twist":
Zin-Azshari is rising out of the sea. West is where you arrive, and it's still Classic's Azshara here, red and gold
autumn forest full of Highborne ruins, with the sea a long way east. It holds the zone's two hubs, each its own map:
Talrendis Landing (the orc and blood elf salvage camp) on the point in the south-west, and Timbermaw Hold (the
furbolgs' caldera city) up the Ursolan pass in the northern mountains.

    Ashenvale road ...... west edge (4,104): from Ashenvale East
    Talrendis Point ..... the south-west: the lake, and the Landing's gate (40,150)
    Ravencrest Monument . the crossroads (100,104): a broken Highborne monument where the roads meet
    Ursolan ............. the northern mountains: the pass up to Timbermaw Hold's gate (62,4)
    Shadowsong Shrine ... the north-east: a night elf moon shrine, its priestesses long dead and not all gone
    Haldarr Encampment .. the south-east: the satyrs' camp, and their den's mouth (166,154)
    The Sundering Mere .. the lake in the south-east the river runs into
    Valormok ............ on the Orgrimmar road: a Horde waystation the satyrs burned
    Orgrimmar road ...... south edge (120,196): down to Orgrimmar's north gate
    East road ........... east edge (196,96): on into Central Azshara

THE ART is Kyle's Azshara sheets (docs/azshara_art_prompts.md, 17 Nov 2026): tools/bake_ashenvale.py azshara_west
paints the ground from sheet 1 (AZSHARA_SHEET), and the trees, ruins and salvage are sheet 2's.

HARD CONTRACTS (world/portal_manager.py)
  portals  Ashenvale East (4,104) <-> its east road (215,102); Orgrimmar (120,196) <-> its north gate (134,1);
           Talrendis Landing (40,150) <-> its gate (30,1); Timbermaw Hold (62,4) <-> its south gate (120,198);
           Central Azshara (196,96) <-> its west road (4,96); Haldarr Den (166,154) <-> its way out (48,97)
"""
import numpy as np

from tools import ashenvale_engine as E
from world.chunk_paths import exists as _chunk_exists  # noqa: E402  (.webp, .jpg or .png)

BAKED_DIR = "assets/tiles/azshara/baked_west"
AZP = "assets/tiles/azshara/props/"      # Kyle's Azshara props sheet (docs/azshara_art_prompts.md sheet 2)
W, H = 200, 200

PORTALS = {(4, 104): "Ashenvale East", (120, 196): "Orgrimmar", (40, 150): "Talrendis Landing",
           (62, 4): "Timbermaw Hold", (196, 96): "Central Azshara", (166, 154): "Haldarr Den"}
ARRIVALS = [(6, 104), (120, 194), (40, 148), (62, 7), (194, 96), (166, 152)]
#: the doors whose maps come next; their clearings, roads and gaps are already cut
LATER_PORTALS = {}
START = (100, 106)     # the crossroads: everything must be reachable from here

# ------------------------------------------------------------------ the plan
ROADS = {
    # west from Ashenvale to the crossroads at Ravencrest Monument
    "ashenvale": ([(4, 104), (20, 106), (40, 110), (62, 112), (84, 110), (100, 106)], 3.4),
    # south from the crossroads, past Valormok, down to Orgrimmar
    "orgrimmar": ([(100, 106), (108, 124), (114, 144), (118, 166), (120, 184), (120, 197)], 3.4),
    # east from the crossroads to Central Azshara
    "east":      ([(100, 106), (122, 100), (146, 96), (170, 96), (196, 96)], 3.2),
    # north up the Ursolan pass to Timbermaw Hold's gate
    "ursolan":   ([(100, 106), (96, 88), (86, 70), (74, 50), (66, 30), (62, 14), (62, 4)], 3.0),
    # south-west down the point to Talrendis Landing's gate
    "talrendis": ([(40, 110), (38, 124), (39, 138), (40, 150)], 2.8),
    # north-east to Shadowsong Shrine
    "shrine":    ([(146, 96), (151, 80), (156, 64)], 2.6),
    # south-east, over the river, to Haldarr
    "haldarr":   ([(114, 144), (130, 148), (146, 152), (160, 154), (166, 154)], 2.6),
}

RIVERS = [   # (pts, half-width shallow, half-width deep): out of the Ursolan snows into the Sundering Mere
    ([(140, 0), (136, 24), (130, 48), (126, 72), (124, 90), (128, 110), (134, 128), (142, 148), (148, 164)],
     3.2, 1.4),
]
FORDS = [(125, 99, 6), (143, 150, 6)]

LAKES = {
    "talrendis": [(22, 164, 12, 9, 0, 0.7)],
    "mere": [(152, 176, 14, 9, 0, 1.3)],
    "tarns": [(176, 60, 4, 3, 0, 0.4), (56, 76, 3.5, 2.6, 0, 1.8)],
}
DEEP_SHRINK = {"talrendis": 3.0, "mere": 3.0, "tarns": 1.8}
MOON_POOLS = [(156, 60, 5)]        # the Shadowsong moonwell paints silver

# ---- rock: the Ursolan mountains across the north, crags along the east, outcrops in the forest
MESAS = [
    (30, 36, 16, 14, 0), (104, 34, 18, 12, 0), (176, 30, 14, 14, 0),     # the Ursolan peaks
    (44, 64, 6, 5, 0), (182, 128, 7, 12, 0), (80, 132, 5, 4, 0), (186, 180, 8, 8, 0),
    (52, 22, 5, 6, 0), (74, 22, 5, 6, 0),                                  # the pass's walls
]
RIDGES = [
    ([(150, 40), (162, 48), (168, 40)], 2.4),       # behind the shrine
    ([(64, 88), (56, 96), (50, 92)], 2.2),          # a spur west of the crossroads
]

# ---- woods (impassable autumn forest): (cx, cy, rx, ry, rot, phase)
WOODS = [
    (28, 76, 12, 10, 0, 1.0), (160, 122, 10, 12, 0, 2.0), (70, 152, 10, 8, 0, 0.6), (176, 184, 10, 8, 0, 1.4),
    (20, 192, 12, 6, 0, 0.4), (84, 182, 8, 8, 0, 2.2), (140, 64, 8, 8, 0, 1.1), (70, 128, 6, 6, 0, 2.6),
    (170, 76, 8, 6, 0, 0.9), (60, 182, 6, 6, 0, 1.7),
]
BELTS = []
CLEARINGS = [   # carved back out of the woods
    (100, 104, 14, 10),         # the crossroads, Ravencrest Monument
    (40, 148, 10, 8),           # Talrendis Landing's gate
    (156, 64, 12, 9),           # Shadowsong Shrine
    (160, 152, 14, 10),         # Haldarr Encampment
    (62, 12, 8, 10),            # the Ursolan pass
    (20, 104, 12, 8),           # the Ashenvale road in
    (118, 170, 12, 9),          # Valormok
    (120, 190, 10, 8),          # the Orgrimmar road out
    (186, 96, 10, 8),           # the east road out
]
BLUEBELL_PATCHES = [(100, 104, 10, 7), (40, 148, 8, 6), (156, 64, 10, 7), (118, 170, 9, 6), (60, 112, 10, 6)]
CORRUPT_PATCHES = [(160, 152, 12, 8)]       # Haldarr: the satyrs' cursed ground
BURNED_PATCHES = [(118, 170, 7, 5)]         # Valormok, burned
LUSH = 1.0
GRADE = (1.30, 1.14)
PAVED_PATCHES = [(100, 104, 6, 4), (156, 64, 5, 4)]

GAPS = [
    ("ell", 4, 104, 8, 7), ("ell", 120, 196, 8, 7), ("ell", 196, 96, 8, 7), ("ell", 62, 6, 7, 8),
    ("ell", 40, 150, 7, 6), ("ell", 166, 154, 6, 5), ("ell", 100, 104, 9, 7), ("ell", 156, 64, 8, 6),
    ("ell", 160, 152, 9, 7),
]

SPEC = E.Spec("West Azshara", W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK,
              mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={"west": 5, "south": 6}, rock_rim={"north": 12, "east": 7}, gaps=GAPS, fords=FORDS,
              thicket=(0.70, 10.0, 2.3))

#: Most of Azshara's quests are given in its two hubs (Kyle's ~70%); the open-world people come with the quest pass.
#: Valormok's last grunt (tools/build_sunreach_conclave.py writes him; docs/azshara_quest_plan.md)
NPC_POSITIONS = {"az_valormok_grunt": (116, 172)}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("Ursolan", 30, 4, 70, 40, None),
    ("Shadowsong Shrine", 136, 44, 40, 36, None),
    ("Ravencrest Monument", 82, 88, 38, 32, None),
    ("Talrendis Point", 4, 126, 52, 56, None),
    ("Haldarr Encampment", 140, 136, 44, 30, None),
    ("The Sundering Mere", 132, 164, 44, 30, None),
    ("Valormok", 100, 158, 36, 26, None),
]

TREES = {
    "big":   [(AZP + "az_autumn_tree.png", 10), (AZP + "az_gold_tree.png", 9), (AZP + "az_autumn_tree.png", 11)],
    "mid":   [(AZP + "az_gold_tree.png", 8), (AZP + "az_autumn_tree.png", 9), (AZP + "az_birch_trio.png", 8)],
    "small": [(AZP + "az_birch_trio.png", 7), (AZP + "az_gold_tree.png", 7)],
    "woods": [(AZP + "az_autumn_tree.png", 10), (AZP + "az_gold_tree.png", 9), (AZP + "az_autumn_tree.png", 11)],
}


def build_layout():
    AL = E.make_layout_class(SPEC, "West Azshara",
                             "Azshara's autumn forest, red and gold to the mountains, where the Highborne built and the "
                             "satyrs stayed. The Horde's salvage camp is on the point; the Timbermaw are up the pass.",
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
    E.scatter_trees(L, TREES, seed=5201, spacing=5.6, grove_keep=0.86)
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def sprinkle(L):
    """Ground clutter, a little: ferns and logs in the forest, rocks everywhere."""
    import random
    rnd = random.Random(5203)
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
        elif logs < 20 and r < 0.042:
            if L.prop("az_autumn_log", x, y, 3, path_dir=AZP, solid=False, nudge=0):
                logs += 1
        elif rocks < 26 and r < 0.052:
            if L.prop("az_lichen_boulder", x, y, 4, path_dir=AZP, solid=False, nudge=0):
                rocks += 1
    L.clutter = (ferns, logs, rocks)


CHEST_SPOTS = [
    (30, 120), (64, 96), (88, 140), (132, 118), (176, 104), (170, 62), (124, 64), (84, 58), (40, 92),
    (24, 184), (100, 186), (176, 168), (152, 34),
]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    P = L.prop
    A = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=E.AP, **kw)        # noqa: E731
    X = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=E.XP, **kw)        # noqa: E731
    F = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir="assets/tiles/felwood/props/", **kw)  # noqa: E731
    B = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir="assets/buildings/", **kw)           # noqa: E731
    D = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir="assets/tiles/dungeon_props/", **kw)  # noqa: E731
    Z = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=AZP, **kw)                          # noqa: E731

    # ---- the roads in: signposts
    P("br_signpost", 14, 100, 5)
    P("br_signpost", 124, 188, 5)
    P("br_signpost", 106, 98, 5)
    # ---- Ravencrest Monument: the broken Highborne monument at the crossroads
    Z("az_noble_statue", 96, 100, 8, solid="core")
    Z("az_broken_spire", 108, 96, 11, solid="core")
    Z("az_toppled_column", 92, 112, 5, solid="core")
    Z("az_moon_arch", 100, 94, 8, solid="core")
    # ...and the salvage crews' first dig beside it
    Z("az_dig_scaffold", 112, 112, 6, solid="core")
    Z("az_relic_crate", 116, 108, 3, solid="core")
    Z("az_survey_stakes", 88, 104, 4, solid="core")
    # ---- Talrendis Point: the Landing's gate, on the point by the lake
    B("tl_gatehouse", 40, 152, 8, solid=False, road_ok=True)
    P("br_signpost", 44, 140, 4)
    # ---- Ursolan: the pass up to the Hold, between two Timbermaw totems
    F("fw_timbermaw_totem", 56, 12, 7, solid="core")
    F("fw_timbermaw_totem", 68, 12, 7, solid="core")
    A("furbolg_totem", 66, 36, 5, solid="core")
    B("tm_totem_gate", 62, 9, 8, solid=False, road_ok=True)     # the Hold's gate at the top of the pass
    # ---- Shadowsong Shrine: a night elf moon shrine on the hill
    B("fw_moonwell_shrine", 156, 58, 10, solid="core")
    A("ash_moon_rune_stone", 148, 66, 6, solid="core")
    A("ash_moon_sigil_stone", 164, 68, 5, solid="core")
    F("fw_fallen_statue", 162, 74, 6, solid="core")
    Z("az_leyline_node", 140, 84, 5, solid="core")
    Z("az_mana_tower", 172, 54, 10, solid="core")
    # ---- Haldarr Encampment: the satyrs' camp, and the den's mouth
    Z("az_satyr_totem", 152, 148, 6, solid="core")
    Z("az_fel_bonfire", 158, 150, 4, solid="core")
    Z("az_cursed_tree", 172, 144, 9, solid="core")
    A("furbolg_den_entrance", 166, 152, 7, solid=False, road_ok=True)
    X("ashx_skull_fence", 156, 158, 4, solid="core")
    X("ashx_satyr_weapon_rack", 150, 156, 4, solid="core")
    X("ashx_demon_skull_altar", 162, 144, 5, solid="core")
    # ---- Valormok: the Horde waystation the satyrs burned
    B("ek_burnt_cottage", 112, 166, 6, solid="core")
    P("br_signpost", 124, 164, 4)
    D("broken_column", 126, 174, 4, solid="core")
    # ---- the Sundering Mere and the river: a few Highborne stones in the shallows
    Z("az_toppled_column", 140, 170, 5, solid="core")
    Z("az_moon_arch", 30, 150, 7, solid="core")
    Z("az_ruin_wall", 28, 144, 5, solid="core")


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and _chunk_exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_azshara_west():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
