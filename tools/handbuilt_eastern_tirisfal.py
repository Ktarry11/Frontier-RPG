"""
Hand-built Eastern Tirisfal (90x140): the road east of Brill, levels 7-12.

Laid out on the REAL Tirisfal map (Brill 60,55 is the pivot; 1 map unit = 2.6 tiles, origin 58,22):
    W    BRILL's east gate (the road out), the BYPASS road in from Western Tirisfal north of town
    SW   the ZEPPELIN LANDING, the road down to the RUINS OF LORDAERON (the Undercity gate, 62,65) and the SILVERPINE road south
    NW   BRIGHTWATER LAKE (68,42) with Gunther's Retreat on its shore; the sea along the whole north: THE NORTH COAST (66,29)
    N/NE the SCARLET WATCH POST (78,33), and beyond it the barred gate of the SCARLET MONASTERY (85,33) - sealed, a dungeon for later
    E    the CRUSADER OUTPOST (78,51), FAOL'S REST (82,45), and VENOMWEB VALE (87,49) on the far east rim
    SE   BALNIR FARMSTEAD (73,62) with the Cult of the Damned's cellar (Scourge Cave), and the barred BULWARK road (84,70):
         the way on to the Plaguelands is closed

AREA ARCHETYPE: RIDGE ROAD.  Western is one open glade and Deathknell a lobed valley; this zone is a long, winding trade road
that climbs through three rock-ridge steps - each step opens onto its own pocket (lakeshore, watch, vale, farm).  Ridges, not rings.

HARD CONTRACTS (world/portal_manager.py)
  portals  Western Tirisfal(4,62)  Brill(6,86)  Zeppelin Tower(21,97)  Undercity(10,112)  Silverpine North(16,136)  Scourge Cave(52,112)
  NPC ids  referenced by data/quests/*.json; positions below are written back by tools/sync_tirisfal_npcs.py
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob, lobe, superlobe, water_body, rock_spurs

KEY = "eastern_tirisfal"
NAME = "Eastern Tirisfal"
DESC = "Rot-eaten farmland, the Scarlet Crusade's watchfires, and the long road to the Undercity gate."
REGION = "Eastern Kingdoms - Lordaeron"
W, H = 90, 140
BAKED_DIR = "assets/tiles/eastern_tirisfal/baked"
IS_TOWN = False
BASE_TILE = "grass"

PORTALS = {(4, 62): "Western Tirisfal", (6, 86): "Brill", (21, 97): "Undercity Zeppelin Tower", (10, 112): "Undercity",
           (16, 136): "Silverpine North", (52, 112): "Scourge Cave"}
ARRIVALS = [(8, 62), (10, 88), (21, 100), (10, 108), (16, 132), (52, 116)]
START = (28, 87)

ROADS = {
    "brill":      ([(6, 86), (16, 87), (28, 86), (40, 82), (52, 76)], 3.2),
    "faol":       ([(52, 76), (57, 68), (62, 60), (66, 56)], 2.8),
    "venomweb":   ([(62, 60), (68, 64), (74, 68), (78, 72)], 2.4),
    "bypass":     ([(4, 62), (14, 62), (22, 63), (30, 60), (36, 56)], 3.0),
    "north":      ([(36, 56), (42, 46), (46, 38), (50, 32), (52, 28)], 2.8),
    "monastery":  ([(52, 28), (60, 28), (66, 29)], 2.4),
    "link":       ([(28, 86), (30, 74), (32, 64), (32, 60)], 2.6),
    "zeppelin":   ([(14, 93), (15, 99), (21, 99)], 2.6),
    "ruins":      ([(14, 93), (12, 102), (10, 110)], 3.0),
    "silverpine": ([(12, 104), (14, 118), (16, 130), (16, 136)], 2.8),
    "balnir":     ([(40, 82), (40, 92), (40, 100), (40, 104)], 2.6),
    "cult":       ([(40, 104), (46, 110), (52, 114)], 2.2),
    "bulwark":    ([(46, 110), (58, 118), (66, 124)], 2.6),
    "lakeshore":  ([(22, 63), (26, 60), (30, 60)], 2.0),
}

_RS = K.RoadSet(ROADS)
road_dist = _RS.dist

LAKE = (26.0, 50.0, 12.0, 7.5)      # Brightwater Lake

SPURS = [
    (88, 48, 60, 50, 2.8),          # the Venomweb ridge: splits the Watch's plateau from the eastern vale (gap at its west tip)
    (2, 76, 24, 74, 2.4),           # shoulders Brill's gate from the bypass road (gap east of it)
    (88, 100, 62, 98, 2.6),         # the Balnir ridge: Bulwark road below, Venomweb above
    (50, 138, 50, 124, 2.4),
]
OUTCROPS = [
    (58, 40, 2.8, 2.2), (70, 56, 2.4, 2.0), (30, 96, 2.8, 2.2), (24, 118, 2.4, 2.0), (66, 86, 3.0, 2.4),
    (82, 62, 2.6, 2.0), (44, 66, 2.4, 2.0), (6, 70, 2.2, 1.8),
]


def sea_field(gx, gy):
    """The North Coast: water above a wavy line (tile distance inside the water)."""
    return (8.5 + 2.4 * np.sin(gx / 9.0 + 0.7) + 1.6 * wob(gx * 0.6, gy * 0.6)) - gy


def lake_field(gx, gy):
    return np.maximum(water_body(gx, gy, *LAKE), sea_field(gx, gy))


def cliff_field(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    floor = np.maximum.reduce([
        superlobe(gx, gy, 30.0, 88.0, 29.0, 38.0, 2.6),         # Brill's east, the landing, the ruins road, Balnir
        superlobe(gx, gy, 28.0, 50.0, 27.0, 23.0, 2.6),         # the lakeshore and the bypass
        superlobe(gx, gy, 57.0, 30.0, 28.0, 22.0, 2.6),         # the Scarlet Watch's plateau
        superlobe(gx, gy, 70.0, 68.0, 26.0, 26.0, 2.6),         # Faol's Rest and Venomweb Vale
        superlobe(gx, gy, 50.0, 114.0, 33.0, 22.0, 2.6),        # the farm's south, the cellar, the Bulwark road
        superlobe(gx, gy, 20.0, 128.0, 19.0, 16.0, 2.6),        # the Silverpine corner
    ])
    floor = floor + 2.6 * wob(gx * 0.42, gy * 0.42) + 1.2 * wob(gx, gy)
    sea = sea_field(gx, gy)
    floor = np.maximum(floor, sea + 5.0)
    floor = np.maximum(floor, road_dist(gx, gy) + 2.4)
    floor = np.maximum(floor, water_body(gx, gy, *LAKE) + 3.0)
    rock = -floor
    rock = np.maximum(rock, rock_spurs(gx, gy, SPURS, OUTCROPS))
    edge = np.minimum.reduce([gx, W - gx, gy, H - gy])
    rock = np.maximum(rock, (3.5 - edge) * 1.2 + 0.3 * wob(gx * 1.3, gy * 1.3))
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    rock = np.where((sea > -1.0) | (water_body(gx, gy, *LAKE) > -1.0), np.minimum(rock, -0.5), rock)
    return rock


def fields(gx, gy):
    gx = np.asarray(gx, float)
    w = lake_field(gx, gy)
    return dict(cliff=cliff_field(gx, gy), shallow=w, deep=w - 2.5, deck=np.full(gx.shape, -9.0))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


# ---- subzones (x, y, w, h[, display]) -------------------------------------------------------------
SUBZONES = [
    ("Brightwater Lake", 10, 38, 34, 28),
    ("The North Coast", 4, 4, 40, 18),
    ("Scarlet Watch Post", 40, 14, 30, 30),
    ("Scarlet Monastery Gate", 60, 18, 28, 22),
    ("Faol's Rest", 52, 48, 22, 22),
    ("Crusader's Outpost", 40, 66, 22, 22),
    ("Venomweb Vale", 66, 52, 22, 36),
    ("Zeppelin Landing", 4, 88, 28, 16),
    ("Ruins of Lordaeron", 2, 104, 24, 18),
    ("Balnir Farmstead", 26, 90, 28, 24),
    ("Cult of the Damned Farm", 40, 106, 24, 18),
    ("The Bulwark Road", 50, 108, 28, 28),
]

# ---- baker config (read by tools/bake_tirisfal.py) -------------------------------------------------
BASE = {"meadow": 0.55, "mist": 0.30, "litter": 0.25, "rocky": 0.15}
PAINT = {
    "field":   [(38, 98, 12, 8, 1.0), (30, 104, 7, 5, 0.7)],             # Balnir's rotted fields
    "burned":  [(36, 100, 4, 3, 0.7)],
    "earth":   [(62, 58, 8, 6, 0.9)],                                   # Faol's Rest graveyard
    "gravel":  [(56, 28, 6, 4, 0.7)],                                   # the Watch's drill yard
    "web":     [(78, 70, 10, 14, 1.0)],                                 # Venomweb Vale
    "rocky":   [(78, 70, 9, 12, 0.5), (74, 124, 12, 6, 0.7)],
    "marsh":   [(14, 58, 8, 5, 0.5), (74, 92, 8, 6, 0.5)],
    "scourge": [(52, 112, 6, 4, 0.9), (14, 126, 6, 5, 0.5)],
    "blight":  [(10, 112, 8, 6, 0.8)],                                  # the Undercity gate's poisoned ground
    "litter":  [(46, 70, 8, 6, 0.8), (26, 112, 10, 8, 0.6)],
    }
COBBLE = [(10, 112, 6, 4, 0.9), (21, 98, 7, 4, 0.9)]

# ---- NPC spots -------------------------------------------------------------------------------------
NPC_POSITIONS = {
    "et_deathguard_linnea": (17, 93),        # Deathguard Linnea, Zeppelin Landing
    "et_gravekeeper_morvyn": (61, 64),       # Gravekeeper Morvyn, Faol's Rest
    "et_gunther_lorn": (38, 59),             # Warden Gunther Lorn, Brightwater Lake
    "et_scout_hallam": (44, 82),             # Scout Hallam, Crusader's Outpost
    "et_hunter_ravel": (78, 69),             # Huntress Ravel, Venomweb Vale
    "et_balnir_edric": (36, 99),             # Stablehand Edric, Balnir Farmstead
    "et_cult_warden": (49, 116),             # Warden Ysolde Grave, Cult of the Damned Farm
    "et_cave_warden": (55, 114),             # Boneward Calder, beside the Scourge Cave mouth
    "et_scarlet_watch_scout": (46, 40),      # Scout Hollowmere, watching the Watch Post from the lakeside slope
}
CHESTS = [(36, 70), (20, 122), (70, 80), (60, 34), (44, 122)]

FOREST = dict(seed=37, count=80, rim=10, thorn=18, names=[
    ("ek_dead_oak", 6, 0.34), ("ek_dead_oak", 6, 0.34), (T.HFP + "dead_pine_cluster.png", 5, 0.40),
    (T.HFP + "dead_pine_cluster.png", 5, 0.40), (T.CIP + "cursed_dead_tree_cluster.png", 4, 0.40),
    ("ek_pine_trio", 6, 0.34)])


def dress(L):
    p, b = L.prop, L.bld
    UF, HF, CI, UC = T.UFP, T.HFP, T.CIP, T.UCP
    # ---- Brill's east gate and the bypass road in from Western Tirisfal
    # (no orc palisade gatehouse in Tirisfal - world/exit_frames.py stands a lychgate over the road)
    p("ek_forsaken_banner", 10, 83, 5)
    p("ek_signpost", 14, 85, 4)
    p("ek_signpost", 10, 60, 4)
    p("ek_forsaken_banner", 7, 65, 5)
    # ---- the Zeppelin Landing: the tower, crates, a banner
    b("zep_tower_undead", 21, 94, 11, nudge=1)                  # the Undercity zeppelin tower (portal tile at 21,97)
    p("ek_scarlet_crates", 26, 97, 3)
    p("ek_forsaken_banner", 16, 96, 5)
    p("ek_signpost", 12, 96, 4)
    # ---- the Ruins of Lordaeron: the Undercity gate under a broken wall
    p(UC + "uc_skull_arch.png", 10, 115, 6, solid=False, road_ok=True, nudge=0)
    for (x, y) in [(5, 108), (16, 108), (4, 116), (17, 116), (14, 120)]:
        p("ek_ruin_wall", x, y, 4)
    for (x, y) in [(7, 111), (13, 111)]:
        p(UC + "uc_skull_pillar.png", x, y, 5, nudge=3)
    p("ek_plague_cart", 18, 112, 4)
    p("ek_gibbet", 6, 119, 6)
    p("ek_plague_cauldron", 16, 105, 3)
    p(UF + "dead_tree_bare.png", 18, 109, 6)
    # ---- the Silverpine road
    p("ek_signpost", 19, 133, 4)
    p("ek_forsaken_banner", 13, 134, 5)
    p("ek_gibbet", 20, 126, 6)
    p(HF + "twisted_root_arch.png", 8, 126, 6)
    # ---- Brightwater Lake: Gunther's Retreat on the shore, reeds, willows
    p(CI + "cursed_village_hut.png", 30, 44, 7)
    p(UF + "gravestone_cluster.png", 25, 43, 3)
    for (x, y) in [(15, 52), (22, 59), (38, 54), (34, 42), (16, 44)]:
        p(HF + "bog_reeds_cluster.png", x, y, 3, solid=False, shore_ok=True)
    p("ek_willow", 12, 56, 7)
    p("ek_willow", 38, 58, 7)
    p("ek_toadstools", 14, 60, 2, solid=False)
    p("ek_signpost", 34, 62, 4)
    # ---- the North Coast: a Scarlet lookout on the cliffs, driftwood and reeds
    p("ek_scarlet_tent", 56, 14, 6)
    p("ek_scarlet_banner", 53, 13, 5)
    p("ek_scarlet_banner", 60, 13, 5)
    p("ek_scarlet_crates", 52, 16, 3)
    for (x, y) in [(14, 12), (28, 11), (46, 12)]:
        p(HF + "bog_reeds_cluster.png", x, y, 3, solid=False, shore_ok=True)
    p("ek_dead_oak", 20, 16, 6)
    p("ek_ruin_wall", 36, 15, 4)
    # ---- the Scarlet Watch Post: camp, barricade, drill yard
    for (x, y) in [(48, 28), (56, 26), (52, 34)]:
        p("ek_scarlet_tent", x, y, 6)
    for (x, y) in [(46, 25), (59, 24), (50, 31), (58, 32)]:
        p("ek_scarlet_banner", x, y, 5)
    p("ek_scarlet_crates", 44, 31, 3)
    p("ek_scarlet_crates", 62, 30, 3)
    p("ek_pillory", 54, 30, 4)
    p("ek_plague_cauldron", 50, 22, 3)
    for x in (44, 48, 56, 60):
        p("ek_farm_fence", x, 38, 3, solid=True)
    p("ek_ruin_wall", 64, 24, 4)
    p("ek_signpost", 47, 40, 4)
    # ---- the Scarlet Monastery's gate: barred, a dungeon for later
    p("ek_cemetery_gate", 70, 30, 7, road_ok=True, allow_overlap=True, nudge=0)
    p("ek_angel_statue", 66, 26, 6)
    p("ek_angel_statue", 75, 26, 6)
    p("ek_scarlet_banner", 68, 24, 5)
    p("ek_scarlet_banner", 73, 24, 5)
    p("ek_ruin_wall", 79, 30, 4)
    p("ek_scarlet_crates", 64, 33, 3)
    for x in (66, 74):
        p("ek_cemetery_fence", x, 33, 3, solid=True)
    # ---- Faol's Rest: a mausoleum yard on the Venomweb road
    p(HF + "crypt_mausoleum.png", 62, 54, 9, fraction=0.5)
    for (x, y) in [(56, 56), (68, 56), (57, 62), (67, 62)]:
        p(CI + "worn_tombstone_row.png", x, y, 3)
    p("ek_angel_statue", 62, 59, 6)
    p("ek_open_grave", 58, 64, 3)
    p("ek_cross_crows", 66, 66, 4)
    p("ek_cemetery_fence", 56, 58, 3, solid=True)
    p("ek_cemetery_fence", 69, 58, 3, solid=True)
    p("ek_willow", 53, 56, 7)
    # ---- the Crusader's Outpost: a Scarlet camp across the road
    for (x, y) in [(46, 72), (56, 78)]:
        p("ek_scarlet_tent", x, y, 6)
    for (x, y) in [(44, 69), (50, 72), (57, 75)]:
        p("ek_scarlet_banner", x, y, 5)
    p("ek_scarlet_crates", 48, 76, 3)
    p("ek_ruin_wall", 42, 74, 4)
    for x in (46, 52, 58):
        p("ek_farm_fence", x, 81, 3, solid=True)
    p("ek_signpost", 49, 83, 4)
    # ---- Venomweb Vale: webs, egg sacs, spiders' wood
    for (x, y) in [(76, 62), (82, 70), (74, 78), (80, 84)]:
        p("ek_web_boulder", x, y, 4)
    for (x, y) in [(78, 66), (72, 72), (84, 76), (76, 82)]:
        p("ek_egg_sacs", x, y, 4)
    T.grove(L, 79, 72, 7, 11, 14, [(HF + "dead_pine_cluster.png", 5, 0.4), ("ek_dead_oak", 6, 0.34)], seed=9)
    p("ek_toadstools", 73, 66, 2, solid=False)
    p("ek_signpost", 72, 62, 4)
    # ---- Balnir Farmstead: a rotted farm on the south road
    b("forsaken_house_small", 34, 97, 8, nudge=2)
    p(HF + "burned_house_ruin.png", 31, 100, 7)
    p("ek_farm_well", 44, 102, 4)
    p("ek_farm_cart", 34, 106, 4)
    for (x, y) in [(36, 108), (42, 108), (48, 106)]:
        p("ek_farm_fence", x, y, 3, solid=True)
    for (x, y) in [(33, 96), (47, 99), (38, 104)]:
        p("ek_haystack", x, y, 4)
    p("ek_scarecrow", 37, 102, 4)
    p(UF + "scarecrow.png", 30, 104, 4)
    p("ek_signpost", 43, 90, 4)
    # ---- the Cult of the Damned's cellar: the Scourge Cave mouth
    L.cave(52, 112, "ent_plague_cave", 7, 5)
    p("ek_plague_cauldron", 47, 114, 3)
    p("ek_open_grave", 57, 115, 3)
    p("ek_plague_cart", 36, 113, 4)
    p("ek_grave_hand", 56, 110, 3)
    # ---- the Bulwark road: barred, the way on closed
    p("ek_cemetery_gate", 67, 125, 7, road_ok=True, allow_overlap=True, nudge=0)
    p("ek_forsaken_banner", 63, 122, 5)
    p("ek_forsaken_banner", 71, 122, 5)
    p("ek_ruin_wall", 74, 128, 4)
    p("ek_signpost", 60, 121, 4)
    # ---- road furniture
    p("ek_signpost", 30, 84, 4)
    p("ek_signpost", 36, 58, 4)
    p("ek_pillory", 18, 85, 4)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_eastern_tirisfal():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/et_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
