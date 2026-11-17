"""
Hand-built North Felwood (150x180), level 53-55: the demon wastes (claude/felwood_brief.md).

Kyle, 14 Nov 2026: "the southern part will look like a high level Ashenvale, the north is demon wastes.
We can keep shape similar to actual WoW." South Felwood is reclaimed and only its top band bleeds; this
is what it bleeds from. The same valley carries on north, walled by mountains with Hyjal's slopes on the
east, but here the forest is dead or dying, the river runs fel-green and the Legion, the Shadow Council,
the Jadefire satyrs and the Deadwood hold the ground. The Emerald Reclamation has one foothold: a small
Sentinel camp in Talonbranch Glade.

Structure (tile coords, y down), WoW's north Felwood read north-up:

    South gate .......... south edge (70,176): back down into South Felwood's Fel Line
    Jadefire Glen ....... the south-west: the Jadefire satyrs' glen, on satyr-trodden earth
    Bloodvenom Falls .... the river comes off Hyjal's wall (east) into a fel pool and runs south-west,
                          poisoned, on down into South Felwood (it leaves at x=50, where South's enters)
    Jaedenar ............ the Shadow Council's hold, cut into the west wall: the dungeon door
    Felbrand Crater ..... where an infernal came down, west of the road: the Legion's own ground
    Irontree Woods ...... the north-west: dead ironwood forest, warpwood treants
    Felpaw Village ...... the north-east: the Deadwood's village, worse than any camp south
    Talonbranch Glade ... a small Sentinel camp on the road north: quest givers, no inn, no flight
    Timbermaw Gate ...... the north edge: the Timbermaw Tunnel's south mouth (open since 17 Nov 2026)

HARD CONTRACTS (world/portal_manager.py):
    portal   (70,176) <-> South Felwood (70,4)
    later    Jaedenar's door (19,106) and the Timbermaw tunnel (94,4), in LATER_PORTALS until the maps
             behind them exist (qa_portals fails a door that leads nowhere). Their clearings, roads and
             gaps are already cut.
"""
import math

import numpy as np

from tools import ashenvale_engine as E

BAKED_DIR = "assets/tiles/felwood/baked_north"
FP = "assets/tiles/felwood/props/"      # Kyle's Felwood sheet (tools/file_felwood_art.py)
W, H = 150, 180

PORTALS = {(70, 176): "South Felwood", (19, 106): "Jaedenar",
           (94, 4): "Timbermaw Tunnel"}    # open since 17 Nov 2026 (tools/handbuilt_timbermaw_tunnel.py)
ARRIVALS = [(70, 174), (19, 108), (94, 7)]
LATER_PORTALS = {}
START = (70, 170)      # a road tile: everything must be reachable from here

# ------------------------------------------------------------------ the plan
ROADS = {
    # the spine: the Fel Line -> over the Bloodvenom -> Talonbranch -> the Timbermaw gate
    "spine":     ([(70, 177), (71, 166), (74, 154), (77, 142), (78, 130), (77, 118), (78, 104), (81, 90),
                   (85, 76), (90, 62), (94, 50), (96, 38), (95, 26), (94, 14), (94, 4)], 3.4),
    # west to Jaedenar's gate in the wall
    "jaedenar":  ([(77, 116), (64, 113), (50, 110), (36, 107), (26, 107), (19, 108)], 3.0),
    # north-west into the dead ironwood
    "irontree":  ([(84, 80), (70, 72), (56, 62), (46, 50), (40, 41)], 2.8),
    # north-east to the Deadwood
    "felpaw":    ([(92, 58), (104, 54), (116, 50), (125, 46)], 2.6),
    # the trail up to the falls pool
    "falls":     ([(78, 124), (88, 117), (98, 110)], 2.2),
    # south-west into the satyrs' glen
    "glen":      ([(72, 160), (58, 158), (44, 154), (32, 152)], 2.4),
}

RIVERS = [   # (pts, half-width shallow, half-width deep): the Bloodvenom, out of the falls pool
    ([(100, 118), (88, 126), (78, 133), (68, 141), (60, 150), (54, 162), (51, 172), (50, 180)], 3.4, 1.5),
]
FORDS = [(76, 135, 6), (56, 157, 6)]

LAKES = {
    "bloodvenom": [(108, 113, 9, 6, 0, 0.6)],
    "tarns": [(28, 126, 5, 4, 0, 1.1), (60, 28, 4, 3, 0, 0.4), (122, 140, 3.5, 2.6, 0, 2.2)],
}
DEEP_SHRINK = {"bloodvenom": 3.0, "tarns": 1.8}
MOON_POOLS = []     # nothing up here is pure

# ---- rock (impassable): Hyjal's wall on the east, the west wall Jaedenar is cut into, crater rims
MESAS = [
    # the falls: the cliff the Bloodvenom comes off
    (128, 108, 7, 11, 0), (122, 96, 5, 5, 0),
    # Felbrand Crater's rim, broken
    (40, 78, 3.5, 2.5, 10), (57, 81, 3, 2.2, -10), (45, 95, 3.2, 2.4, 0), (54, 93, 2.6, 2.0, 0),
    # the notch in the west wall Jaedenar stands in
    (14, 92, 6, 8, 0), (14, 121, 6, 7, 0),
    # the narrows above the south gate
    (54, 169, 6, 5, 0), (88, 169, 7, 5, 0),
    # the narrows below the Timbermaw gate
    (82, 11, 6, 5, 0), (108, 11, 6, 5, 0),
    # east foothills and west crags
    (127, 152, 8, 12, 0), (128, 64, 6, 10, 0), (16, 152, 5, 6, 0), (16, 60, 6, 8, 0),
]
RIDGES = [
    ([(100, 140), (108, 152), (104, 164)], 2.2),     # east of the road above the gate
    ([(112, 70), (118, 82), (114, 92)], 2.2),        # between Felpaw and the falls
    ([(60, 96), (66, 103), (63, 108)], 2.0),         # the crater's east shoulder
]

# ---- woods (impassable dead forest): (cx, cy, rx, ry, rot, phase)
WOODS = [
    # Irontree Woods: dead ironwood standing too thick to pass
    (24, 26, 8, 7, 0, 1.2), (60, 50, 5, 6, 0, 0.8), (22, 50, 5, 6, 0, 2.2), (66, 16, 6, 5, 0, 0.3),
    # the rest of the valley, dying
    (110, 140, 6, 8, 0, 1.4), (40, 136, 6, 5, 0, 0.7), (100, 90, 5, 6, 0, 2.0), (122, 24, 6, 6, 0, 0.9),
    (62, 128, 4, 5, 0, 1.6), (108, 74, 4, 4, 0, 2.6), (34, 168, 7, 5, 0, 0.5), (104, 170, 7, 5, 0, 1.1),
]
BELTS = []
CLEARINGS = [   # carved back out of the woods
    (70, 172, 10, 7),           # the south gate
    (32, 152, 14, 11),          # Jadefire Glen
    (20, 106, 12, 10),          # Jaedenar's gate
    (48, 87, 13, 10),           # Felbrand Crater
    (40, 42, 16, 13),           # the heart of Irontree Woods
    (124, 46, 14, 10),          # Felpaw Village
    (96, 34, 12, 9),            # Talonbranch Glade
    (100, 108, 8, 5),           # the falls pool's north shore
    (96, 120, 10, 7),           # where the Bloodvenom leaves the pool
    (94, 8, 10, 6),             # the Timbermaw gate
]

# ---- the painting. North Felwood is painted from the corruption palette everywhere (the baker's
# NORTH materials in tools/bake_ashenvale.py): blighted earth, fel water, Hyjal's black rock.
CORRUPT_PATCHES = [(38, 40, 46, 46), (112, 40, 46, 46), (38, 112, 46, 46), (112, 112, 46, 46),
                   (75, 160, 60, 30), (75, 80, 30, 40)]
BURNED_PATCHES = [(48, 87, 14, 10), (18, 106, 9, 7), (124, 47, 10, 7), (96, 34, 4, 3)]
#: the North's "bluebell" layer is the Twisting Nether showing through (void floor): round Jaedenar's
#: gate, the crater's summoning dais and the Council's camp
BLUEBELL_PATCHES = [(16, 106, 7, 5), (48, 87, 4, 3), (30, 112, 4, 3)]
PAVED_PATCHES = [(16, 106, 5, 4), (96, 34, 3, 2.5), (94, 8, 4, 3)]
LUSH = 0.0
GRADE = None
LIFT = (1.25, 1.55)     # (saturation, value) over the whole map: the blighted textures are dark at source


def satyr_field(P, wp):
    """The Jadefire satyrs' trodden earth (baker hook)."""
    return np.maximum(P.blob(32, 152, 13, 9, 0.8, wp), P.blob(22, 140, 6, 4, 0.8, wp)) * 0.95


GAPS = [
    ("ell", 70, 176, 8, 7),
    ("ell", 94, 4, 8, 7),
    ("ell", 19, 106, 7, 6),
    ("ell", 32, 152, 9, 7),
    ("ell", 48, 87, 9, 7),
    ("ell", 40, 42, 10, 8),
    ("ell", 124, 46, 9, 7),
    ("ell", 96, 34, 8, 6),
    ("ell", 100, 108, 6, 4),
]

SPEC = E.Spec("North Felwood", W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK,
              mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={"north": 5, "south": 6}, rock_rim={"west": 9, "east": 11}, gaps=GAPS, fords=FORDS,
              thicket=(0.70, 10.0, 3.1))

#: Talonbranch Glade, the Reclamation's camp (people written by tools/sync_felwood_north_npcs.py)
NPC_POSITIONS = {
    "fn_talonbranch_captain": (98, 32),      # the camp's captain, at the tower door
    "fn_talonbranch_druid":   (91, 36),      # a druid keeping the camp's ground clean
    "fn_talonbranch_scout":   (101, 38),     # a Timbermaw scout who knows the north
    "fn_talonbranch_medic":   (94, 39),      # a transplant who came north with the Sentinels
    "fn_talonbranch_supply":  (89, 31),      # the camp's supply keeper: repairs, arrows, water
    "fn_timbermaw_guard":     (97, 10),      # the Timbermaw at their door
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("Jadefire Glen", 12, 136, 40, 32, None),
    ("Bloodvenom Falls", 84, 96, 46, 40, None),
    ("Jaedenar", 9, 92, 36, 30, None),
    ("Felbrand Crater", 32, 72, 34, 28, None),
    ("Irontree Woods", 12, 14, 58, 46, None),
    ("Felpaw Village", 106, 30, 36, 32, None),
    ("Talonbranch Glade", 84, 24, 24, 20, None),
    ("Timbermaw Gate", 80, 2, 30, 13, None),
]

_T = lambda n: FP + n + ".png"      # noqa: E731
TREES = {   # a forest dying: corrupted trunks, dead ironwood, a few still half-alive
    "big": [(_T("fw_corrupted_tree"), 10), (_T("fw_dead_ironwood"), 11), (_T("fw_corrupted_tree"), 11)],
    "mid": [(_T("fw_corrupted_tree"), 9), (_T("fw_dead_ironwood"), 9), ("dead_corrupted_tree", 8)],
    "small": [("dead_corrupted_tree", 7), (_T("fw_corrupted_tree"), 8)],
    "woods": [(_T("fw_dead_ironwood"), 11), (_T("fw_corrupted_tree"), 10), ("dead_corrupted_tree", 9)],
}


def build_layout():
    AL = E.make_layout_class(SPEC, "North Felwood",
                             "The demon wastes: dead forest, a poisoned river, and the Legion's hold on the "
                             "north of the valley. The Emerald Reclamation keeps one camp in Talonbranch Glade.",
                             "Kalimdor - Felwood", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.seal_unreachable(L, START)
    dress(L)
    E.build_free_mask(L, NPC_POSITIONS.values())
    for lm in L.z.landmarks:
        ax, ay, w, h = lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]
        L.free_mask[max(0, ay):ay + h + 1, max(0, ax - 1):ax + w + 1] = False
    # the camp keeps its own ground clear
    L.free_mask[24:44, 84:108] = False
    E.scatter_trees(L, TREES, seed=5301, spacing=8.5)
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def sprinkle(L):
    """Ground clutter, a little: fel crystals and mushrooms, bones, rotten logs, rock."""
    import random
    rnd = random.Random(5303)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = {"crystal": 0, "shroom": 0, "bones": 0, "log": 0, "rock": 0}
    cap = {"crystal": 22, "shroom": 34, "bones": 16, "log": 22, "rock": 24}
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        if r < 0.010 and n["crystal"] < cap["crystal"]:
            ok = L.prop("fw_fel_crystals", x, y, 3, path_dir=FP, solid=False, nudge=0)
            k = "crystal"
        elif r < 0.026 and n["shroom"] < cap["shroom"]:
            ok = L.prop("fw_fel_mushrooms", x, y, 3, path_dir=FP, solid=False, nudge=0)
            k = "shroom"
        elif r < 0.034 and n["bones"] < cap["bones"]:
            ok = L.prop("fw_demon_bones", x, y, 2, path_dir=FP, solid=False, nudge=0)
            k = "bones"
        elif r < 0.046 and n["log"] < cap["log"]:
            ok = L.prop("fw_corrupted_log", x, y, 3, path_dir=FP, solid=False, nudge=0)
            k = "log"
        elif r < 0.058 and n["rock"] < cap["rock"]:
            ok = L.prop("rock_outcrop_small", x, y, 4, path_dir=E.AP, solid=False, nudge=0)
            k = "rock"
        else:
            continue
        if ok:
            n[k] += 1
            L.free_mask[max(0, y - 1):y + 2, max(0, x - 1):x + 2] = False
    L.clutter = tuple(n.values())


CHEST_SPOTS = [
    (60, 166), (94, 158), (24, 160), (46, 142), (116, 128), (88, 100), (30, 116), (60, 78),
    (24, 36), (56, 40), (134, 40), (118, 58), (70, 98), (108, 20),
]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    P = L.prop
    A = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=E.AP, **kw)
    F = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=FP, **kw)

    # ---- the south gate: up out of the Fel Line ------------------------------------------------------------
    P("br_signpost", 75, 167, 5)
    F("fw_corrupted_tree", 62, 172, 9)
    F("fw_dead_ironwood", 80, 172, 9)
    L.bld("fw_stake_barricade", 64, 162, 5)              # the Sentinels' furthest line, abandoned
    F("fw_demon_bones", 78, 160, 2, solid=False)

    # ---- Jadefire Glen: the satyrs' glen -----------------------------------------------------------------------
    for k in range(5):
        ang = k * 2 * math.pi / 5 + 0.5
        F("fw_fel_brazier", int(round(32 + 10.0 * math.cos(ang))), int(round(152 + 7.0 * math.sin(ang))), 4)
    F("fw_fel_obelisk", 32, 148, 7)
    F("fw_highborne_column", 24, 146, 5)                 # they built on what the Highborne left
    F("fw_highborne_column", 40, 158, 4)
    F("fw_fel_pool", 26, 158, 4, solid=False)
    F("fw_corrupted_tree", 44, 146, 9)
    F("fw_corrupted_tree", 20, 156, 9)

    # ---- Bloodvenom Falls: the river turns here ----------------------------------------------------------------
    F("fw_fel_crystals", 116, 104, 4)
    F("fw_fel_crystals", 98, 104, 4)
    F("fw_fel_mushrooms", 112, 122, 3)
    F("fw_corrupted_log", 104, 106, 3, solid=False)
    F("fw_fel_pool", 92, 128, 4, solid=False)
    F("fw_corrupted_tree", 94, 102, 9)
    P("br_signpost", 82, 120, 5)

    # ---- Jaedenar: the Shadow Council's hold, cut into the west wall ---------------------------------------------
    # the gatehouse IS the way in: drawn over the dungeon door (entrance art, world/portal_art.py)
    L.deco("fw_jaedenar_gatehouse", 19, 107, 11, path_dir="assets/buildings/")
    L.bld("fw_cult_tent", 26, 98, 6)
    L.bld("fw_cult_tent", 30, 114, 6)
    L.bld("fw_cult_tent", 22, 116, 6)
    F("fw_fel_brazier", 26, 102, 4)
    F("fw_fel_brazier", 26, 112, 4)
    F("fw_shard_cage", 34, 100, 5)                       # whoever the Council took
    F("fw_summoning_dais", 30, 110, 4, solid=False)
    F("fw_fel_obelisk", 38, 104, 7)
    F("fw_demon_bones", 28, 104, 2, solid=False)

    # ---- Felbrand Crater: where the Legion came down ----------------------------------------------------------
    F("fw_infernal_crater", 48, 88, 6, solid=False)
    F("fw_demon_portal", 48, 82, 8)
    F("fw_fel_crystals", 42, 86, 4)
    F("fw_fel_crystals", 55, 89, 4)
    F("fw_fel_obelisk", 40, 92, 7)
    F("fw_fel_brazier", 56, 84, 4)
    F("fw_demon_bones", 52, 92, 2, solid=False)

    # ---- Irontree Woods: dead ironwood -------------------------------------------------------------------------
    for k in range(7):
        ang = k * 2 * math.pi / 7 + 0.2
        F("fw_dead_ironwood", int(round(40 + 13.0 * math.cos(ang))), int(round(42 + 9.0 * math.sin(ang))), 11)
    F("fw_corrupted_log", 36, 44, 3, solid=False)
    F("fw_fel_mushrooms", 44, 40, 3)
    F("fw_half_cleansed_tree", 50, 34, 9, nudge=4)             # the druids got this far once
    A("rock_outcrop_large", 30, 32, 5)

    # ---- Felpaw Village: the Deadwood ----------------------------------------------------------------------------
    for (x, y) in [(118, 40), (130, 42), (122, 54), (132, 52)]:
        L.bld("fw_deadwood_hut", x, y, 7)
    F("fw_deadwood_totem", 124, 46, 6)
    F("fw_deadwood_totem", 114, 50, 6)
    F("fw_fel_brazier", 126, 41, 4)
    F("fw_demon_bones", 120, 47, 2, solid=False)
    F("fw_corrupted_log", 134, 47, 3, solid=False)

    # ---- Talonbranch Glade: the Reclamation's camp --------------------------------------------------------------
    L.bld("fw_sentinel_tower", 101, 30, 10)
    L.bld("fw_sentinel_tent", 90, 30, 6)
    L.bld("fw_sentinel_tent", 103, 40, 6)
    L.bld("fw_stake_barricade", 86, 40, 5)
    L.bld("fw_stake_barricade", 106, 26, 5)
    F("fw_purified_moonwell", 95, 35, 4)                 # a little clean water they brought with them
    A("ash_moon_lantern", 92, 33, 5, solid="core")
    A("ash_moon_lantern", 99, 37, 5, solid="core")
    A("ash_sentinel_weapon_rack", 88, 35, 4)
    F("fw_moonflowers", 96, 38, 3, solid=False)

    # ---- the Timbermaw gate: the Timbermaw Tunnel's south mouth (open since 17 Nov 2026) ---------------------------------------------------------
    F("fw_timbermaw_totem", 89, 9, 7)
    F("fw_timbermaw_totem", 100, 9, 7)
    A("rock_outcrop_large", 86, 5, 5)
    A("rock_outcrop_large", 103, 5, 5)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_felwood_north():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/fwn_shape.png"
    if len(sys.argv) > 2 and sys.argv[2] == "build":
        import time
        t = time.time()
        L = build_layout()
        seen, walk, _ = E.reachable_report(L, START)
        print(f"built {time.time()-t:.1f}s  placed={L.placed} trees={L.trees} scattered={L.scattered} "
              f"woods_deco={L.woods_deco} landmarks={len(L.z.landmarks)} sealed={L.sealed} "
              f"clutter={L.clutter} walkable={walk} reachable={seen} skipped={len(L.skipped)}")
        for sk in L.skipped:
            if sk[0] not in ("fw_corrupted_log", "rock_outcrop_small", "fw_fel_mushrooms", "fw_fel_crystals",
                             "fw_demon_bones"):
                print("  skipped", sk)
        SPEC.shape_preview(out, 4, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()), layout=L)
    else:
        SPEC.shape_preview(out, 4, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
    print("wrote", out)
