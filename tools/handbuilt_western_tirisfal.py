"""
Hand-built Western Tirisfal (118x140): the Glades between Deathknell and Brill, levels 4-10.

Laid out on the REAL Tirisfal map (Brill 60,55 is the pivot; 1 map unit = 2.6 tiles, origin 14,22):
    SW   Deathknell's rock fills the south-west corner; its pass opens onto the road east
    S    NIGHTMARE VALE (47,66): the dark wooded valley the Deathknell road runs through
    SE   COLD HEARTH MANOR (54,60), then the road's end at BRILL'S west gate (113,84)
    W    SOLLIDEN FARMSTEAD (36,49) + the Scarlet CRUSADER OUTPOST (32,46), STILLWATER POND (48,51)
    NW   the sea: a bay with WHISPERING SHORE (36,41) on its south-east rim
    N    AGAMAND MILLS (45,36) and, on the north rim, the AGAMAND FAMILY CRYPT (48,27)
    NE   GARREN'S HAUNT (58,38) at the zone edge; a bypass road north of Brill to Eastern Tirisfal

AREA ARCHETYPE: COASTAL GLADE.  Deathknell is a cliff-ringed valley of separate lobes; this is one broad open dead meadow
with the sea biting a bay out of the north-west and a thin tree-line rim elsewhere - long sight-lines, roads as the spine.

Same recipe as Deathknell (claude/zone_perfection_playbook.md): this module owns the TILE data + landform fields; the baker
(tools/bake_tirisfal.py western_tirisfal) paints from the same fields.

HARD CONTRACTS (world/portal_manager.py)
  portals  Deathknell(60,106)  Brill(113,84)  Eastern Tirisfal(116,62)
  NPC ids  referenced by data/quests/*.json; positions below are written back by tools/sync_tirisfal_npcs.py
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob, lobe, superlobe, water_body, rock_spurs

KEY = "western_tirisfal"
NAME = "Western Tirisfal"
DESC = "The sallow glades west of Brill. A cold sea wind off the bay, and the Scarlet banners are never far."
REGION = "Eastern Kingdoms - Lordaeron"
W, H = 118, 140
BAKED_DIR = "assets/tiles/western_tirisfal/baked"
IS_TOWN = False
BASE_TILE = "grass"

PORTALS = {(60, 106): "Deathknell", (113, 84): "Brill", (116, 62): "Eastern Tirisfal"}
ARRIVALS = [(64, 106), (110, 88), (112, 62)]
START = (84, 108)

ROADS = {
    "deathknell": ([(60, 106), (72, 108), (84, 108), (94, 104), (102, 100), (107, 94), (110, 88), (113, 85)], 3.2),
    "north":      ([(107, 94), (105, 84), (102, 74), (100, 64), (100, 54), (104, 46), (110, 42)], 3.0),
    "bypass":     ([(102, 72), (108, 67), (112, 63), (116, 62)], 2.6),
    "solliden":   ([(102, 74), (94, 70), (84, 68), (72, 68), (60, 68), (52, 66), (46, 62)], 2.8),
    "shore":      ([(66, 68), (62, 60), (60, 52)], 2.2),
    "agamand":    ([(100, 56), (94, 48), (86, 40), (82, 36), (84, 26), (88, 16)], 2.6),
    "nightmare":  ([(84, 108), (84, 116), (88, 124), (90, 131)], 2.4),
    "manor":      ([(102, 100), (100, 96), (98, 92)], 2.2),
}

_RS = K.RoadSet(ROADS)
road_dist = _RS.dist

SEA = (8.0, 12.0, 48.0, 34.0)      # the north-west bay (cx, cy, rx, ry) - reaches off the map
POND = (88, 79, 8.5, 5.8)           # Stillwater Pond

SPURS = [
    (60, 138, 70, 118, 3.0),        # a rock tongue from the south rim that shoulders Nightmare Vale
    (118, 52, 106, 56, 2.4),        # shoulders the bypass gate from the north
    (70, 2, 70, 14, 2.4),           # north rim
]
OUTCROPS = [
    (112, 38, 3.2, 2.6), (116, 48, 2.6, 3.2), (106, 34, 2.4, 2.0),     # the crescent round Garren's Haunt (open SW)
    (92, 58, 2.6, 2.0), (40, 80, 2.8, 2.4), (74, 90, 2.4, 2.0), (96, 118, 3.0, 2.4), (50, 56, 2.2, 1.8),
]


def sea_field(gx, gy):
    return lobe(gx, gy, *SEA) + 0.8 * wob(gx * 0.9, gy * 0.9)


def cliff_field(gx, gy):
    """>0 inside rock.  One huge wobbly basin + a west bulge; Deathknell's massif in the SW; the sea clears a shore band."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    floor = np.maximum(superlobe(gx, gy, 82.0, 72.0, 52.0, 62.0, 3.0), superlobe(gx, gy, 48.0, 72.0, 46.0, 28.0, 2.6))
    floor = floor + 3.0 * wob(gx * 0.42, gy * 0.42) + 1.2 * wob(gx, gy)
    sea = sea_field(gx, gy)
    floor = np.maximum(floor, sea + 7.0)                                 # a broad shore band of land round the bay
    floor = np.maximum(floor, road_dist(gx, gy) + 2.4)
    floor = np.maximum(floor, water_body(gx, gy, *POND) + 3.0)
    rock = -floor
    rock = np.maximum(rock, lobe(gx, gy, 28.0, 122.0, 34.0, 28.0) * 1.0 + 1.0 * wob(gx * 0.5, gy * 0.5))     # Deathknell's massif
    rock = np.maximum(rock, rock_spurs(gx, gy, SPURS, OUTCROPS))
    edge = np.minimum.reduce([gx, W - gx, gy, H - gy])               # the map edge is always rock (sea excepted)
    rock = np.maximum(rock, (3.5 - edge) * 1.2 + 0.3 * wob(gx * 1.3, gy * 1.3))
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    rock = np.where((sea > -1.0) | (water_body(gx, gy, *POND) > -1.0), np.minimum(rock, -0.5), rock)
    return rock


def lake_field(gx, gy):
    return np.maximum(sea_field(gx, gy) - 0.0, water_body(gx, gy, *POND))


def fields(gx, gy):
    gx = np.asarray(gx, float)
    w = lake_field(gx, gy)
    return dict(cliff=cliff_field(gx, gy), shallow=w, deep=w - 2.5, deck=np.full(gx.shape, -9.0))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


# ---- subzones (x, y, w, h[, display]) -------------------------------------------------------------
SUBZONES = [
    ("Whispering Shore", 36, 34, 30, 28),
    ("Crusader Outpost", 34, 54, 22, 20),
    ("Solliden Farmstead", 46, 60, 30, 26),
    ("Stillwater Pond", 74, 66, 28, 24),
    ("Agamand Mills", 62, 22, 40, 30),
    ("Agamand Family Crypt", 74, 4, 28, 22),
    ("Garren's Haunt", 98, 28, 20, 28),
    ("Cold Hearth Manor", 88, 84, 22, 22),
    ("Nightmare Vale", 66, 100, 40, 40),
]

# ---- baker config (read by tools/bake_tirisfal.py) -------------------------------------------------
BASE = {"meadow": 0.55, "mist": 0.30, "litter": 0.25, "rocky": 0.15}
PAINT = {
    "field":  [(58, 74, 11, 8, 1.0)],                                   # Solliden's pumpkin fields
    "earth":  [(88, 14, 9, 6, 0.9), (50, 62, 5, 3, 0.5)],               # the Agamand family graveyard, the outpost camp
    "gravel": [(88, 12, 6, 4, 0.6)],
    "blight": [(80, 36, 9, 7, 0.8)],                                    # the mills' poisoned race
    "burned": [(112, 44, 4, 3, 0.7)],
    "marsh":  [(88, 80, 12, 8, 0.8), (88, 118, 14, 10, 0.5)],
    "litter": [(86, 118, 20, 16, 1.0), (72, 108, 8, 6, 0.7)],           # Nightmare Vale's dark floor
    "rocky":  [(104, 94, 6, 5, 0.5)],
}

# ---- NPC spots -------------------------------------------------------------------------------------
NPC_POSITIONS = {
    "wt_vale_ranger": (81, 111),             # Ranger Corvin Ashe, where the Deathknell road enters Nightmare Vale
    "wt_coldhearth_watcher": (100, 90),      # Watcher Pell, at Cold Hearth Manor's gate
    "wt_shore_fisher": (40, 39),             # Fisher Quillon, on the Whispering Shore
    "wt_outpost_scout": (40, 66),            # Scout Dessa Vane, watching the Crusader Outpost from the thorn-line
    "wt_solliden_farmer": (63, 71),          # Widow Marren, on the Solliden road
    "wt_pond_hermit": (80, 71),              # Hermit Oswin, Stillwater Pond
    "wt_agamand_envoy": (82, 42),            # Envoy Sorren, Agamand Mills
    "wt_crypt_keeper": (85, 16),             # Keeper Halvard, the Agamand family crypt gate
    "wt_garren_warden": (104, 49),           # Warden Brask, Garren's Haunt
}
CHESTS = [(70, 100), (54, 78), (96, 24), (106, 50), (76, 86)]

FOREST = dict(seed=23, count=90, rim=10, thorn=22, names=[
    ("ek_dead_oak", 6, 0.34), ("ek_dead_oak", 6, 0.34), (T.HFP + "dead_pine_cluster.png", 5, 0.40),
    (T.HFP + "dead_pine_cluster.png", 5, 0.40), (T.CIP + "cursed_dead_tree_cluster.png", 4, 0.40),
    ("ek_pine_trio", 6, 0.34)])


def dress(L):
    p, b, row = L.prop, L.bld, L.row
    UF, HF, CI = T.UFP, T.HFP, T.CIP
    # ---- Deathknell pass: the way back down the hill
    p("ek_signpost", 66, 104, 4)
    p("ek_forsaken_banner", 63, 102, 5)
    p("ek_cross_crows", 70, 112, 4)
    # ---- Nightmare Vale: a dark wood, a Scarlet outpost hacked into it
    T.grove(L, 86, 122, 16, 12, 30, [(HF + "dead_pine_cluster.png", 5, 0.4), ("ek_dead_oak", 6, 0.34), (CI + "cursed_dead_tree_cluster.png", 4, 0.4)], seed=5)
    for (x, y) in [(76, 118), (96, 126), (80, 130), (100, 112)]:
        p(HF + "twisted_root_arch.png", x, y, 6)
    for (x, y) in [(82, 120), (92, 118), (78, 126)]:
        p("ek_toadstools", x, y, 2, solid=False)
    p("ek_scarlet_tent", 94, 128, 6)
    p("ek_scarlet_banner", 89, 124, 5)
    p("ek_scarlet_banner", 99, 125, 5)
    p("ek_scarlet_crates", 90, 131, 3)
    p("ek_ruin_wall", 104, 120, 4)
    p("ek_signpost", 85, 112, 4)
    # ---- Cold Hearth Manor: a ruined estate, its yard gone to blight
    b("forsaken_house_medium", 98, 88, 9, nudge=2)
    p("ek_ruin_wall", 91, 90, 4)
    p("ek_ruin_wall", 105, 88, 4)
    p("ek_cemetery_fence", 94, 96, 3, solid=True)
    p("ek_cemetery_fence", 104, 96, 3, solid=True)
    p(UF + "gravestone_cluster.png", 92, 94, 3)
    p(UF + "gravestone_cluster.png", 96, 98, 3)
    p(UF + "dead_tree_bare.png", 90, 86, 6)
    p(UF + "dead_tree_bare.png", 101, 82, 6)
    p("ek_cross_crows", 98, 95, 4)
    p("ek_thorn_bush", 96, 91, 2, solid=False)
    # ---- Brill's west gate
    b("palisade_gatehouse", 113, 88, 7, solid=False, road_ok=True, nudge=0)
    b("watchtower", 105, 80, 9, nudge=1)
    p("ek_forsaken_banner", 109, 82, 5)
    p("ek_forsaken_banner", 109, 84, 5, nudge=1)
    p("ek_signpost", 106, 93, 4, nudge=1)
    b("gallows_post", 113, 96, 6, nudge=1)
    # ---- the bypass gate to Eastern Tirisfal
    p("ek_signpost", 110, 66, 4)
    p("ek_forsaken_banner", 114, 60, 5)
    # ---- Stillwater Pond
    for (x, y) in [(81, 80), (95, 78), (88, 85), (84, 74)]:
        p(HF + "bog_reeds_cluster.png", x, y, 3, solid=False, shore_ok=True)
    p("ek_willow", 80, 84, 7)
    p("ek_willow", 97, 83, 7)
    p("ek_toadstools", 93, 75, 2, solid=False)
    p("ek_open_grave", 78, 76, 3)
    p("ek_grave_hand", 98, 76, 3)
    # ---- Solliden Farmstead: pumpkin fields, a farmhouse, Scarlet hands working it
    b("forsaken_house_small", 52, 72, 8, nudge=2)
    p(HF + "burned_house_ruin.png", 66, 66, 7)
    p("ek_farm_well", 61, 71, 4)
    p("ek_farm_cart", 48, 76, 4)
    for (x, y) in [(56, 80), (62, 80), (68, 78)]:
        p("ek_farm_fence", x, y, 3, solid=True)
    for (x, y) in [(56, 76), (65, 74), (60, 82)]:
        p("ek_haystack", x, y, 4)
    p("ek_haystack", 70, 73, 4)
    p("ek_scarecrow", 58, 74, 4)
    p(UF + "scarecrow.png", 64, 77, 4)
    p("ek_scarlet_banner", 54, 66, 5)
    p("ek_scarlet_tent", 46, 68, 6)
    # ---- the Crusader Outpost: Scarlet camp in the trees west of the farm
    p("ek_scarlet_crates", 36, 63, 3)
    p("ek_scarlet_tent", 44, 64, 6)
    p("ek_scarlet_tent", 38, 66, 6)
    p("ek_scarlet_banner", 42, 59, 5)
    p("ek_scarlet_banner", 47, 61, 5)
    p("ek_scarlet_crates", 41, 64, 3)
    p("ek_ruin_wall", 36, 60, 4)
    p("ek_signpost", 52, 65, 4)
    # ---- Whispering Shore: wreckage and reeds along the bay
    p(CI + "shipwreck_hull.png", 46, 42, 7, shore_ok=True)
    for (x, y) in [(40, 36), (52, 44), (36, 40), (58, 52)]:
        p(HF + "bog_reeds_cluster.png", x, y, 3, solid=False, shore_ok=True)
    p("ek_dead_oak", 54, 50, 6)
    p("ek_toadstools", 56, 46, 2, solid=False)
    p("ek_signpost", 61, 54, 4)
    # ---- Agamand Mills: an overrun mill, its race poisoned
    b("forsaken_house_medium", 80, 36, 9, nudge=2)
    b("well_house", 74, 42, 5, nudge=2)
    p("ek_plague_cart", 88, 40, 4)
    p("ek_plague_cauldron", 78, 42, 3)
    p("ek_farm_fence", 92, 46, 3, solid=True)
    p("ek_farm_fence", 70, 36, 3, solid=True)
    p("ek_haystack", 86, 34, 4)
    p("ek_toadstools", 76, 32, 2, solid=False)
    p("ek_signpost", 98, 58, 4)
    # ---- the Agamand Family Crypt: a walled graveyard under the north rim
    p(HF + "crypt_mausoleum.png", 88, 14, 9, fraction=0.5, road_ok=True)
    p("ek_cemetery_gate", 88, 21, 5, road_ok=True, allow_overlap=True, nudge=0)
    for x in (82, 94):
        p("ek_cemetery_fence", x, 22, 3, solid=True)
    for (x, y) in [(80, 16), (96, 16), (82, 12), (94, 12)]:
        p(CI + "worn_tombstone_row.png", x, y, 3)
    p("ek_angel_statue", 90, 18, 6)
    p("ek_open_grave", 84, 18, 3)
    p("ek_cross_crows", 92, 20, 4)
    p("ek_gibbet", 78, 20, 6)
    # ---- Garren's Haunt: the burned house in its crescent of rock
    p(HF + "burned_house_ruin.png", 110, 40, 7)
    p(UF + "gravestone_cluster.png", 106, 44, 3)
    p("ek_gibbet", 114, 46, 6)
    p("ek_cross_crows", 108, 48, 4)
    p("ek_ruin_wall", 106, 38, 4)
    p(UF + "dead_tree_bare.png", 112, 34, 6)
    p("ek_toadstools", 108, 44, 2, solid=False)
    # ---- road furniture
    p("ek_signpost", 98, 66, 4)
    p("ek_signpost", 86, 104, 4)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_western_tirisfal():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/wt_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
