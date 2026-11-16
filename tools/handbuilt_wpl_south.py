"""
Hand-built South Western Plaguelands (180x160), level 51-54. docs/plaguelands_design.md.

Kyle, 16 Nov 2026: "WPL and EPL? School, strath, and maybe a new Scarlet Crusade dungeon? Keep the similar cauldron
quests", and "The Geography can be somewhat similar with minor adjustments as the integration didn't change this too
too much geographically. It should feel familar-ish for players."

So this is WoW's Western Plaguelands read north-up, cut across the middle. The southern half holds what a player
remembers arriving to: the Bulwark on the Tirisfal border, the cauldrons at Felstone Field, Dalson's Tears and the
Writhing Haunt, Andorhal's ruins, Sorrow Hill and Uther's Tomb, and Darrowmere Lake with Caer Darrow on its island.
North WPL (Gahrron's Withering, Northridge, the Thondroril and Hearthglen's gates) is the next map up.

Structure (tile coords, y down):

    West gate .......... (3,84): the road from Eastern Tirisfal, straight into the Bulwark
    The Bulwark ........ the Forsaken front line (20,84): apothecaries, an inn, the bats, the cauldron quests
    Felstone Field ..... a farm and its cauldron in the north-west (38,40)
    Dalson's Tears ..... a farm, a barn and a cauldron, north of the crossroads (90,36)
    The Writhing Haunt . a haunted homestead and its cauldron in the east (146,62), over the creek
    Andorhal ........... the ruined city in the south-west (56,116): Scourge and Forsaken fighting through it
    Sorrow Hill ........ the Order of the Pale Flame's keep (100,128) and Uther's Tomb (114,142)
    Darrowmere Lake .... the south-east (150,128); Caer Darrow is the island, reached by a causeway
    North gate ......... (96,3): on into North WPL

LATER PORTALS (laid when the maps behind them exist; the ground for each is already cut):
    North WPL (96,3), the Alterac foothills road (40,157), the Undercity sewer door (6,102), Scholomance (156,128).
"""
import math

import numpy as np

from tools import ashenvale_engine as E

BAKED_DIR = "assets/tiles/plaguelands/baked_wpl_south"
EK = "assets/tiles/eastern_kingdoms/props/"
UF = "assets/tiles/undead_farmland/props/"
HF = "assets/tiles/haunted_forest/props/"
CI = "assets/tiles/cursed_isle/props/"
PL = "assets/tiles/plaguelands/props/"
PL = "assets/tiles/plaguelands/props/"          # Kyle's Plaguelands sheet 3, when it lands
W, H = 180, 160
NAME = "Western Plaguelands South"

PORTALS = {(3, 84): "Eastern Tirisfal", (96, 3): "Western Plaguelands North"}
ARRIVALS = [(7, 84), (96, 7)]
#: Doors whose ground is cut and which go live when the map behind them exists (qa_portals fails a door that leads
#: nowhere): (tile) -> (target map, its arrival tile)
LATER_PORTALS = {
    (40, 157): ("The Alterac Foothills", None),
    (6, 102): ("Undercity", None),                 # the sewer door, opened by the Bulwark's quest chain
    (156, 128): ("Scholomance", None),
}
START = (12, 84)

# ------------------------------------------------------------------ the plan
ROADS = {
    # the King's Road: the west gate, the Bulwark, the crossroads, the north gate
    "kings":      ([(2, 84), (12, 84), (24, 84), (40, 83), (56, 81), (72, 79), (84, 72), (90, 58), (92, 44),
                    (94, 28), (96, 14), (96, 2)], 3.4),
    # south from the crossroads to Sorrow Hill, then east to the lake
    "sorrow":     ([(72, 79), (82, 92), (92, 108), (98, 122), (106, 128), (120, 129), (132, 128)], 3.0),
    # the causeway to Caer Darrow (a deck over the water)
    "causeway":   ([(132, 128), (146, 128)], 2.2),
    # south-west into Andorhal and on toward the Alterac foothills
    "andorhal":   ([(56, 81), (54, 94), (56, 106), (54, 120), (48, 136), (42, 150), (40, 158)], 3.0),
    # north-west to Felstone Field
    "felstone":   ([(30, 84), (32, 70), (36, 56), (38, 44)], 2.6),
    # east over the creek to the Writhing Haunt
    "haunt":      ([(84, 72), (100, 70), (116, 68), (130, 64), (144, 62)], 2.6),
    # the Bulwark's south track to the sewer door
    "sewer":      ([(14, 86), (10, 94), (6, 102)], 2.0),
    # the farm lane to Dalson's Tears
    "dalson":     ([(92, 44), (86, 38)], 2.2),
}

# a slow creek out of the north, down the east side into Darrowmere
RIVERS = [
    ([(124, 0), (126, 24), (132, 50), (134, 66), (138, 88), (142, 106), (146, 116)], 3.0, 1.2),
]
FORDS = [(131, 64, 6)]

LAKES = {
    "darrowmere": [(152, 130, 24, 19, 0, 0.6), (168, 112, 8, 8, 0, 1.4)],
    "ponds": [(58, 22, 5, 3.5, 0, 0.9), (18, 132, 4, 3, 0, 2.1)],
}
DEEP_SHRINK = {"darrowmere": 4.0, "ponds": 1.8}
ISLETS = [(156, 128, 9, 6.5, 0, 0.8)]           # Caer Darrow
DECKS = [(133, 150, 127, 129)]                   # the causeway's planks (x0, x1, y0, y1)

# ---- rock (impassable): hills between the farms, the ridges that hold the map's edges
MESAS = [
    (62, 50, 7, 5, 15), (118, 40, 6, 9, 0), (24, 108, 5, 7, 0), (80, 108, 5, 4, -10),
    (126, 96, 4, 6, 0), (70, 140, 6, 5, 0), (160, 80, 5, 7, 0), (112, 16, 5, 6, 0),
]
RIDGES = [
    ([(4, 60), (14, 54), (22, 60)], 2.4),          # shoulders the Bulwark's north
    ([(106, 92), (114, 104), (110, 114)], 2.2),    # between the crossroads and the lake
    ([(140, 30), (152, 40), (162, 36)], 2.6),      # the east hills above the Haunt
]

# ---- dead woods (impassable thickets of grey, plague-killed trees)
WOODS = [
    (20, 28, 10, 8, 0, 1.2), (68, 18, 8, 7, 0, 0.4), (150, 20, 9, 8, 0, 2.0), (112, 54, 6, 7, 0, 1.6),
    (28, 140, 8, 7, 0, 0.8), (82, 150, 9, 5, 0, 2.4), (160, 64, 6, 8, 0, 0.3), (40, 100, 5, 6, 0, 1.1),
]
BELTS = []
CLEARINGS = [
    (12, 84, 8, 6),             # the west gate
    (22, 84, 13, 10),           # the Bulwark
    (38, 42, 13, 10),           # Felstone Field
    (88, 36, 14, 10),           # Dalson's Tears
    (146, 62, 13, 10),          # the Writhing Haunt
    (56, 116, 20, 16),          # Andorhal
    (102, 130, 15, 12),         # Sorrow Hill
    (114, 144, 7, 5),           # Uther's Tomb
    (72, 80, 9, 7),             # the crossroads
    (96, 8, 9, 6),              # the north gate
    (40, 152, 8, 6),            # the foothills road
]

GAPS = [
    ("ell", 3, 84, 7, 6), ("ell", 96, 3, 8, 6), ("ell", 40, 157, 7, 5), ("ell", 6, 102, 5, 4),
    ("ell", 22, 84, 11, 8), ("ell", 38, 42, 10, 8), ("ell", 88, 36, 11, 8), ("ell", 146, 62, 10, 8),
    ("ell", 56, 116, 17, 13), ("ell", 102, 130, 12, 10), ("ell", 114, 144, 6, 4), ("ell", 72, 80, 8, 6),
]

SPEC = E.Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, islets=ISLETS,
              mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={"north": 4, "south": 4}, rock_rim={"west": 7, "east": 6}, gaps=GAPS, decks=DECKS, fords=FORDS,
              thicket=(0.78, 9.0, 1.7))

#: The Bulwark and Sorrow Hill are this map's two hubs (each with an inn and a flight master); everyone else stands
#: where their trade is. Written into data/npcs by tools/sync_wpl_south_npcs.py when the roster lands.
NPC_POSITIONS = {
    # ---- the Bulwark (Forsaken)
    "wpl_bulwark_commander": (24, 80),
    "wpl_bulwark_apothecary": (30, 88),       # the cauldron quests
    "wpl_bulwark_innkeeper": (16, 88),
    "wpl_bulwark_bat_handler": (14, 78),
    "wpl_bulwark_quartermaster": (28, 79),
    "wpl_bulwark_sewer_agent": (12, 92),      # the Undercity door chain
    # ---- Sorrow Hill (the Order of the Pale Flame)
    "wpl_pf_flamekeeper": (100, 125),         # Flamekeeper Rory Callahan
    "wpl_pf_quartermaster": (106, 133),
    "wpl_pf_innkeeper": (94, 133),
    "wpl_pf_bat_keeper": (110, 126),          # the Order keeps a hawk roost; a flight master all the same
    "wpl_pf_drillmaster": (82, 128),
    "wpl_pf_chaplain": (118, 140),            # by Uther's Tomb
}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("Felstone Field", 22, 28, 34, 28, None),
    ("Dalson's Tears", 72, 22, 34, 28, None),
    ("The Writhing Haunt", 130, 46, 34, 32, None),
    ("Andorhal", 32, 96, 50, 42, None),
    ("Darrowmere Lake", 128, 106, 52, 46, None),
    ("Caer Darrow", 145, 120, 22, 16, None),
    ("Sorrow Hill", 84, 114, 36, 30, None),
    ("Uther's Tomb", 106, 136, 18, 14, None),
    ("The Bulwark", 8, 72, 32, 24, None),
]


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}

#: dead trees only: the plague killed everything that had leaves
TREES = {   # Kyle's dead oaks lead; his purple blight pines only show up inside the woods
    "big": [(PL + "pl_dead_oak.png", 9), (EK + "ek_dead_oak.png", 9), (HF + "dead_pine_cluster.png", 8)],
    "mid": [(PL + "pl_dead_oak.png", 8), (UF + "dead_tree_bare.png", 7), (EK + "ek_dead_oak.png", 8)],
    "small": [(UF + "dead_tree_bare.png", 6), (PL + "pl_dead_oak.png", 6)],
    "woods": [(PL + "pl_dead_oak.png", 9), (HF + "dead_pine_cluster.png", 9), (PL + "pl_blight_pine.png", 9)],
}

#: painting-only patches for the baker (cx, cy, rx, ry). The baker's names are Ashenvale's: "bluebell" paints the dead
#: crop rows here, "corrupt" the blight round each cauldron, "burned" Andorhal's ash.
BLUEBELL_PATCHES = [(38, 42, 12, 8), (88, 36, 13, 8), (146, 62, 10, 7), (24, 60, 8, 5), (110, 80, 9, 6)]
CORRUPT_PATCHES = [(38, 44, 6, 4), (88, 38, 6, 4), (148, 64, 6, 4), (56, 116, 9, 7)]
BURNED_PATCHES = [(56, 116, 18, 14), (140, 56, 6, 4)]
PAVED_PATCHES = [(22, 84, 9, 6), (100, 128, 9, 7), (114, 144, 5, 3), (158, 126, 5, 4)]
GRADE = (1.0, 1.05)        # (saturation, value): Kyle's ground sheet is lit already; a touch of lift


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "Lordaeron's old farmland, plague-killed and still fought over. The Forsaken hold the "
                             "Bulwark, the Order of the Pale Flame holds Sorrow Hill, and the Scourge's cauldrons "
                             "keep the fields sick.",
                             "Eastern Kingdoms - Lordaeron", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    for (px, py) in LATER_PORTALS:              # their ground stays open so the doors can go in without a rebake
        L.z.collision_layer[py][px] = None
    E.seal_unreachable(L, START)
    dress(L)
    E.build_free_mask(L, NPC_POSITIONS.values())
    for lm in L.z.landmarks:
        ax, ay, w, h = lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]
        L.free_mask[max(0, ay):ay + h + 1, max(0, ax - 1):ax + w + 1] = False
    E.scatter_trees(L, TREES, seed=6101, spacing=7.6, scale=1.0)       # less is more: a dead land, thinly treed
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def sprinkle(L):
    """A little ground clutter: graves and thorn, never much."""
    import random
    rnd = random.Random(6103)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = {"thorn": 0, "grave": 0, "rock": 0}
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        if n["thorn"] < 40 and r < 0.020:
            n["thorn"] += bool(L.prop("ek_thorn_bush", x, y, 3, path_dir=EK, solid=False, nudge=0))
        elif n["grave"] < 14 and r < 0.024:
            n["grave"] += bool(L.prop("gravestone_cluster", x, y, 3, path_dir=UF, solid=False, nudge=0))
        elif n["rock"] < 18 and r < 0.030:
            n["rock"] += bool(L.prop("rock_outcrop_small", x, y, 4, path_dir=E.AP, solid=False, nudge=0))
    L.clutter = n


CHEST_SPOTS = [
    (30, 30), (52, 36), (104, 26), (78, 46), (158, 52), (138, 74), (36, 112), (68, 124), (48, 132),
    (122, 136), (90, 140), (160, 128), (14, 120), (118, 82),
]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    P = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=EK, **kw)
    Q = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=PL, **kw)      # Kyle's Plaguelands props
    U = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=UF, **kw)
    B = L.bld
    BQ = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=PL, fraction=0.5, **kw)   # prop-sheet buildings

    # ---- the west gate and the Bulwark: the Forsaken's front line -------------------------------------------------
    B("pl_bulwark_gate", 9, 82, 8)
    B("pl_bulwark_palisade", 10, 72, 8)
    B("pl_bulwark_bat_roost", 14, 74, 10)
    B("pl_bulwark_barracks", 26, 76, 7)
    B("pl_bulwark_apothecary", 34, 90, 7)
    B("forsaken_inn", 16, 94, 8)
    B("pl_bulwark_wagon_shed", 38, 80, 6)
    Q("pl_cauldron_live", 30, 84, 4)
    P("ek_forsaken_banner", 18, 80, 5)
    P("ek_forsaken_banner", 28, 86, 5)
    Q("pl_corpse_sacks", 22, 90, 3)
    P("ek_signpost", 40, 86, 4)

    # ---- Felstone Field: a farm and its cauldron --------------------------------------------------------------------
    BQ("pl_barn_plagued", 30, 38, 7)
    BQ("pl_farmhouse_burned", 44, 36, 7)
    Q("pl_cauldron_platform", 38, 46, 6)
    Q("pl_runoff_pool", 46, 48, 3, solid=False)
    U("scarecrow", 50, 46, 4)
    Q("pl_wheat_stook", 32, 46, 4)
    Q("pl_pumpkin_rot", 24, 42, 4, solid=False)
    Q("pl_fence_broken", 26, 50, 3, solid=False)
    Q("pl_fence_broken", 52, 40, 3, solid=False)

    # ---- Dalson's Tears: the farm whose family is still here, after a fashion ---------------------------------------
    BQ("pl_barn_plagued", 80, 30, 8)
    BQ("pl_farmhouse_burned", 94, 30, 7, nudge=5)
    Q("pl_windmill_broken", 72, 30, 9)
    Q("pl_cauldron_live", 88, 38, 4)
    P("ek_farm_well", 98, 40, 4)
    U("scarecrow", 82, 42, 4)
    Q("pl_wheat_stook", 76, 38, 4)
    Q("pl_meat_wagon", 102, 36, 4)

    # ---- the Writhing Haunt: a homestead nobody left -----------------------------------------------------------------
    BQ("pl_farmhouse_burned", 140, 56, 7)
    Q("pl_cauldron_live", 148, 64, 4)
    Q("pl_ghoul_pit", 152, 58, 3, solid=False)
    P("ek_cross_crows", 138, 66, 4)
    U("gravestone_cluster", 156, 66, 3, solid=False)
    Q("pl_corpse_sacks", 132, 62, 3, nudge=4)

    # ---- Andorhal: the ruined city ------------------------------------------------------------------------------------
    for (x, y) in [(44, 106), (70, 122), (58, 132)]:
        BQ("pl_farmhouse_burned", x, y, 7)
    BQ("pl_ruin_wall", 66, 106, 6)
    BQ("pl_ruin_wall", 42, 124, 6)
    B("ek_ruined_gatehouse", 56, 100, 9, road_ok=True)
    Q("pl_clock_stump", 56, 116, 7)                  # what's left of Andorhal's clock tower
    Q("pl_ruin_arch", 48, 114, 5)
    Q("pl_stall_burned", 64, 116, 5)
    Q("pl_meat_wagon", 50, 122, 4)
    Q("pl_scourge_banner", 62, 126, 5)
    Q("pl_skull_pile", 46, 130, 3, solid=False)
    P("ek_forsaken_banner", 46, 98, 5)          # the Forsaken's line through the north of the city
    P("ek_forsaken_banner", 66, 98, 5)

    # ---- the crossroads ------------------------------------------------------------------------------------------------
    P("ek_signpost", 76, 82, 4)
    P("ek_gibbet", 66, 76, 5)

    # ---- Sorrow Hill: the Order of the Pale Flame's keep, and Uther's Tomb ---------------------------------------------
    B("pf_keep", 100, 121, 9, nudge=5)
    B("pf_chapel", 116, 124, 9, nudge=2)
    B("pf_training_yard", 84, 124, 6)
    B("pf_hall", 92, 141, 7)
    B("pf_stable", 110, 134, 6)
    Q("pf_banner", 96, 128, 5)
    Q("pf_banner", 106, 128, 5)
    Q("pf_weapon_rack", 88, 132, 3)
    Q("pl_knight_statue", 114, 142, 6)              # Uther's Tomb
    P("ek_cemetery_fence", 106, 146, 3, solid=False)
    P("ek_cemetery_fence", 122, 146, 3, solid=False)

    # ---- Darrowmere Lake and Caer Darrow ----------------------------------------------------------------------------------
    B("scholo_entrance", 156, 126, 9, nudge=1)           # Caer Darrow and the way down into Scholomance
    Q("pl_dead_oak", 128, 118, 7)
    Q("pl_dead_oak", 124, 140, 7)

    # ---- the north gate -----------------------------------------------------------------------------------------------
    P("ek_signpost", 100, 12, 4)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_wpl_south():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS) + list(LATER_PORTALS),
                              npc=list(NPC_POSITIONS.values()))


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/wpl_south_shape.png"
    if len(sys.argv) > 2 and sys.argv[2] == "build":
        L = build_layout()
        seen, walk, _ = E.reachable_report(L, START)
        print(f"placed={L.placed} trees={L.trees} landmarks={len(L.z.landmarks)} sealed={L.sealed} "
              f"clutter={L.clutter} walkable={walk} reachable={seen} skipped={len(L.skipped)}")
        for sk in L.skipped:
            if sk[0] not in ("ek_thorn_bush", "gravestone_cluster", "rock_outcrop_small") and "dead" not in str(sk[0]):
                print("  skipped", sk)
        SPEC.shape_preview(out, 4, portals=list(PORTALS) + list(LATER_PORTALS), npc=list(NPC_POSITIONS.values()),
                           layout=L)
    else:
        shape_preview(out)
    print("wrote", out)
