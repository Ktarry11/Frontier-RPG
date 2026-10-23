"""
Hand-built Ashenvale West (220x200): the night elf heartland - ancient forest, silver rivers, moonwells.

Ashenvale West and East are ONE continuous country split at x=220/x=0 (the seam road at y=100 matches on
both sides).  West is the old, living half: Kaldorei Sentinels, furbolg clans, druid groves and a long
wild coast.  Structure (tile coords, y down):

    Zoram Strand gate ... NW sand cove (15,30); Blackfathom Deeps cliff-cave at (30,20) on the headland
    Coast Road .......... a long road down the west bluff from Zoram to Astranaar, fords at the river mouth
    Maestra's Post ...... Sentinel camp (85,53) on the east shore of Lake Maestra (70,55)
    Silverwind River .... Lake Maestra -> south past the Moonwell -> Lake Elune'ara (104,132) -> the bay
    Mystral Falls River . from the Ragged Highlands (150,18) south into Lake Elune'ara, fords at the roads
    The Moonwell ........ a real surface moonwell pool (110,90) in a clearing; the cave portal (110,82)
                          sits on its north rim (Moonwell Hollow lies beneath)
    Ragged Highlands .... NE rock plateaus and furbolg country; den (165,45), totem (145,35)
    Moonwhisper Grove ... SE-central druid glade: a ring of ancient trees round a moon pond (178,108)
    Astranaar ........... town zone, gate (110,160) south of Lake Elune'ara
    Greenwood Gate ...... the east seam (215,100): a ruined stone arch in the woods, continues in East at x=4
    The Night Run ....... SE dense forest trails, nightsaber country; Starfall Pond + ruined arch (175,120)

HARD CONTRACTS (world/portal_manager.py):
    portals  East seam (215,100)  Blackfathom (30,20)  Moonwell Hollow (110,82)  Astranaar (110,160)
             Zoram Strand (15,30)
    arrivals are 2 tiles NORTH of the portal tile; cave exits land 1 south of it.
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_central_barrens import BP, DP, BLD, ENT, CP, blob, _gauss, _smooth

BAKED_DIR = "assets/tiles/ashenvale/baked_west"
W, H = 220, 200

PORTALS = {(215, 100): "Ashenvale East", (30, 20): "Blackfathom Deeps", (110, 82): "Moonwell Hollow",
           (110, 160): "Astranaar", (15, 30): "Zoram Strand"}
ARRIVALS = [(215, 98), (30, 21), (110, 83), (110, 158), (15, 31)]

# ------------------------------------------------------------------ the plan
ROADS = {
    # the great road: east seam -> Moonwhisper -> river ford -> the Moonwell clearing
    "seam":      ([(216, 100), (204, 101), (192, 104), (181, 106)], 3.4),
    "great":     ([(181, 106), (168, 104), (156, 101), (144, 97), (132, 92), (122, 91)], 3.4),
    # Moonwell clearing -> Maestra's Post -> lake north shore -> the coast
    "maestra":   ([(102, 86), (96, 78), (92, 68), (88, 58), (86, 54)], 3.0),
    "lakeshore": ([(86, 54), (84, 44), (74, 38), (60, 37), (46, 40), (34, 44), (24, 46)], 2.8),
    # coast road: Astranaar -> west -> up the bluff -> Zoram
    "astra_w":   ([(110, 158), (98, 162), (84, 166), (72, 166), (60, 162), (52, 152), (49, 138), (47, 122),
                   (44, 106), (42, 92), (40, 78), (36, 64), (30, 54), (24, 46), (19, 38), (15, 32)], 3.0),
    "bfd":       ([(24, 46), (26, 36), (29, 27), (30, 22)], 2.6),
    # Moonwell -> Elune'ara east shore -> Astranaar
    "astra_n":   ([(118, 94), (122, 104), (124, 114), (128, 126), (130, 138), (126, 148), (118, 156), (110, 158)], 3.2),
    # Highlands trail up to the furbolg den
    "highlands": ([(168, 104), (166, 90), (161, 76), (158, 62), (160, 50), (163, 42)], 2.8),
    # the Night Run + ruins
    "ruins":     ([(130, 138), (144, 142), (158, 140), (170, 132), (176, 124)], 2.4),
    "nightrun":  ([(126, 150), (140, 160), (156, 168), (172, 172), (188, 166)], 2.2),
    "starfall":  ([(170, 132), (182, 144), (186, 152)], 2.0),
    # Moonwell clearing spur to the pool rim
    "moonrim":   ([(102, 86), (110, 84), (118, 91)], 3.2),
}

# the sea: west coast with a cove at Zoram, a headland at Blackfathom and two bays
def coast_x(gy):
    return (18.0 + 14.0 * _gauss(gy, 80, 22) + 20.0 * _gauss(gy, 150, 18) + 6.0 * _gauss(gy, 188, 9)
            - 12.0 * _gauss(gy, 35, 14) + 2.0 * np.sin(0.33 * gy + 0.5) + 1.5 * np.sin(0.19 * gy)
            + 1.0 * np.sin(0.53 * gy + 1.0))


def sea(gx, gy):
    return coast_x(gy) - gx


RIVERS = [   # (pts, half-width shallow, half-width deep)
    # Silverwind: Lake Maestra -> Moonwell glade west -> Lake Elune'ara north shore
    ([(74, 63), (82, 72), (90, 80), (97, 92), (100, 104), (102, 118)], 3.4, 1.6),
    # Elune'ara outflow -> south-west to the bay
    ([(88, 140), (78, 150), (68, 157), (58, 160), (48, 158), (40, 154)], 3.6, 1.6),
    # Mystral Falls: from the Highlands down into Lake Elune'ara (east)
    ([(150, 14), (148, 30), (146, 48), (145, 66), (143, 84), (140, 100), (134, 114), (124, 124)], 3.8, 1.8),
]
FORDS = [(143, 97, 6), (127, 122, 5), (58, 160, 6), (97, 90, 5), (60, 162, 5), (76, 150, 4)]

LAKES = {
    "maestra": [(70, 55, 13, 10, 0, 0.6)],
    "elune": [(104, 132, 16, 11, 8, 0.9), (90, 139, 9, 6, -10, 2.2), (118, 124, 8, 6, 10, 1.1)],
    "tarns": [(138, 58, 5, 3.8, 0, 1.2), (60, 128, 6, 4, 10, 2.1), (186, 152, 8, 6, 0, 0.4),
              (30, 100, 4, 3, 0, 3.0)],
    "moonwell": [(110, 91, 5.6, 4.6, 0, 0.0)],
    "glade": [(178, 110, 5.2, 4.0, 0, 1.0)],
}
DEEP_SHRINK = {"maestra": 3.4, "elune": 4.0, "tarns": 2.0, "moonwell": 2.6, "glade": 2.2}
ISLETS = [(106, 131, 3.4, 2.6, 0, 0.7)]

# ---- rock (impassable cliffs)
MESAS = [
    (30, 12, 15, 6, 0),                # Blackfathom headland cliff (cave face at 30,20)
    (110, 75, 15, 6, 0),               # Moonwell bluff (cave face)
    (150, 24, 12, 7, -10), (176, 21, 14, 8, 8), (190, 44, 9, 12, 0), (134, 44, 5, 9, 0),
    (172, 62, 8, 5, -15), (196, 72, 6, 9, 0), (120, 30, 7, 5, 20),
    (36, 106, 5, 9, 0), (60, 92, 6, 4, 20), (66, 112, 4, 3, 0),
    (186, 134, 6, 4, -20), (150, 118, 5, 3.5, 12), (196, 112, 5, 4, 0),
]
RIDGES = [
    ([(128, 8), (144, 12), (158, 10)], 3.0),
    ([(196, 22), (205, 36), (207, 52)], 3.2),
    ([(26, 70), (30, 84), (28, 98)], 2.6),
    ([(90, 100), (96, 112), (94, 124)], 2.2),
    ([(160, 82), (174, 80), (186, 84)], 2.4),
]

# ---- woods (impassable dense forest): (cx, cy, rx, ry, rot, phase)
WOODS = [
    (112, 52, 9, 24, 6, 1.2), (126, 70, 6, 14, 0, 0.4),
    (52, 76, 7, 12, -8, 0.7), (52, 112, 6, 14, 6, 2.1), (62, 144, 7, 9, 0, 3.0),
    (76, 100, 7, 9, 10, 1.7), (84, 124, 5, 8, 0, 0.5), (130, 124, 3, 7, 0, 2.2),
    (60, 186, 34, 9, 0, 0.3), (160, 186, 40, 10, 0, 1.4), (110, 190, 14, 8, 0, 2.6),
    (206, 66, 10, 22, 0, 0.9), (206, 148, 10, 30, 0, 1.9), (190, 176, 16, 8, 0, 2.4),
    (150, 148, 8, 9, 0, 0.8), (168, 156, 9, 7, 0, 2.0), (140, 78, 5, 8, 0, 1.0),
    (20, 126, 4, 14, 0, 1.2), (24, 168, 5, 12, 0, 2.4),
    (88, 28, 10, 7, 0, 0.6), (190, 90, 6, 10, 0, 1.3), (146, 112, 6, 7, 0, 2.7), (40, 52, 6, 7, 0, 3.3),
    (136, 168, 8, 6, 0, 0.9), (84, 176, 12, 6, 0, 1.8), (195, 125, 6, 8, 0, 2.5),
]
BELTS = [
    ([(8, 60), (16, 68), (24, 76)], 2.5),
]
CLEARINGS = [   # carved back out of the woods
    (110, 90, 14, 10),          # the Moonwell glade
    (178, 108, 20, 16),         # Moonwhisper Grove
    (68, 52, 26, 20),           # Maestra's vale
    (108, 154, 22, 10),         # Astranaar flats
    (163, 44, 14, 10),          # furbolg den yard
    (176, 124, 10, 7),          # ruined arch
    (26, 40, 14, 10),           # Zoram approach
    (215, 100, 8, 8),           # Greenwood Gate
]
# painting-only patches for the baker (cx, cy, rx, ry)
BLUEBELL_PATCHES = [(178, 108, 17, 13), (110, 90, 12, 8), (68, 52, 13, 9), (108, 154, 12, 5)]
CORRUPT_PATCHES = [(165, 46, 12, 9), (134, 66, 6, 5), (182, 172, 9, 6), (152, 166, 5, 4)]
BURNED_PATCHES = [(161, 50, 5, 4), (181, 171, 4, 3)]
PAVED_PATCHES = [(110, 159, 9, 4.5), (215, 100, 5, 5), (110, 85, 7, 3.2), (96, 56, 4, 3.5)]
MOON_POOLS = [(110, 91, 9), (178, 110, 8)]      # lakes drawn with moon water instead of lake water

GAPS = [
    ("ell", 215, 100, 8, 8),
    ("ell", 30, 21, 6, 5),
    ("ell", 110, 84, 7, 5),
    ("ell", 110, 159, 8, 6),
    ("ell", 15, 31, 6, 5),
]

SPEC = E.Spec("Ashenvale West", W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK,
              islets=ISLETS, sea=sea, mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={"north": 6, "south": 8, "east": 5}, gaps=GAPS, fords=FORDS, thicket=(0.66, 10.0, 0.0))

# Quest hubs (positions synced by tools/sync_ashenvale_npcs.py); existing ids keep their ids
NPC_POSITIONS = {
    "ashenvale_maestra": (85, 53),       # Sentinel Maestra, Maestra's Post
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)



CAVES = {   # portal tile -> (sprite, w, h)
    (30, 20): ("ent_sea_cave", 9, 7),
    (110, 82): ("ent_druid_grove_cave", 9, 7),
}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("The Night Run", 110, 138, 110, 62, None),
    ("Silverwind Vale", 76, 58, 56, 90, None),
    ("Coast Bluffs", 18, 56, 44, 120, None),
    ("Zoram Coast", 0, 0, 62, 52, None),
    ("Lake Elune'ara", 80, 112, 56, 40, None),
    ("Maestra's Post", 45, 30, 50, 45, None),
    ("Ragged Highlands", 126, 6, 84, 62, None),
    ("Moonwhisper Grove", 160, 96, 50, 64, None),
    ("The Moonwell", 96, 76, 28, 26, None),
]

TREES = {
    "big": [("large_canopy_tree", 10), ("canopy_tree_cluster", 9), ("large_canopy_tree", 9)],
    "mid": [("medium_canopy_tree", 8), ("large_canopy_tree", 8), ("canopy_tree_cluster", 7)],
    "small": [("medium_canopy_tree", 6), ("medium_canopy_tree", 7)],
    "woods": [("large_canopy_tree", 9), ("canopy_tree_cluster", 8), ("large_canopy_tree", 10)],
}


def build_layout():
    from tools.handbuilt_central_barrens import _grove  # noqa: F401  (re-export for dress helpers)
    AL = E.make_layout_class(SPEC, "Ashenvale West", "Ancient night elf forest, silver rivers and moonwells; the Sentinels hold the road.",
                             "Kalimdor - Western Forest", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.seal_unreachable(L, (181, 106))
    dress(L)
    E.build_free_mask(L, NPC_POSITIONS.values())
    for lm in L.z.landmarks:
        ax, ay, w, h = lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]
        L.free_mask[max(0, ay):ay + h + 1, max(0, ax - 1):ax + w + 1] = False
    E.scatter_trees(L, TREES, seed=2101, spacing=4.0)
    sprinkle(L)
    E.seal_unreachable(L, (181, 106))
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def sprinkle(L):
    """Ground clutter on free forest floor: ferns, logs, rock outcrops - a little, not a lot."""
    import random
    rnd = random.Random(77)
    spec = L.spec
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    ferns = logs = rocks = 0
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        if ferns < 160 and r < 0.040:
            if L.prop("fern_cluster", x, y, 3, path_dir=E.AP, solid=False, nudge=0):
                ferns += 1
        elif logs < 28 and r < 0.046:
            if L.prop("fallen_log", x, y, 3, path_dir=E.AP, solid=False, nudge=0):
                logs += 1
        elif rocks < 26 and r < 0.052:
            if L.prop("rock_outcrop_small", x, y, 4, path_dir=E.AP, solid=False, nudge=0):
                rocks += 1
    L.clutter = (ferns, logs, rocks)


CHEST_SPOTS = [
    (12, 40), (34, 27), (47, 102), (60, 124), (90, 108), (90, 150), (117, 86), (151, 14), (141, 60),
    (167, 40), (198, 64), (183, 101), (177, 127), (189, 153), (152, 170), (72, 177), (198, 128),
]


def chests(L):
    import math
    for (x, y) in CHEST_SPOTS:
        if L.chest(x, y):
            continue
        # fallback (groves can swallow a spot): walk outwards in a ring until a clear tile takes it
        L.skipped.pop()
        done = False
        for r in range(6, 16, 2):
            for k in range(16):
                a = k * math.pi / 8
                if L.chest(int(x + r * math.cos(a)), int(y + r * math.sin(a))):
                    done = True
                    break
                L.skipped.pop()
            if done:
                break
        if not done:
            L.skipped.append(("chest", x, y, "no free tile"))


def dress(L):
    P = L.prop
    A = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=E.AP, **kw)
    X = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=E.XP, **kw)

    # ---- Greenwood Gate: the ruined elven arch the road passes under, the east seam ------------------------
    P("ent_elven_ruin_arch", 210, 103, 8, path_dir=ENT, solid=False, road_ok=True)
    A("large_canopy_tree", 204, 94, 11)
    A("large_canopy_tree", 205, 112, 11)
    P("br_signpost", 200, 106, 5)
    A("fern_cluster", 207, 98, 3, solid=False)
    A("fern_cluster", 208, 108, 3, solid=False)

    # ---- Zoram Strand cove (NW): a fishing landing on the sand ---------------------------------------------
    L.cp("rowboat_wreck", 9, 27, 3, shore_ok=True)
    L.cp("fish_drying_rack", 20, 35, 4)
    L.cp("mooring_posts", 11, 33, 3, shore_ok=True)
    L.cp("driftwood_pile", 10, 40, 3, shore_ok=True)
    L.cp("outrigger_canoe", 8, 36, 3, shore_ok=True)
    L.cp("fish_crates_traps", 20, 29, 3)
    A("ash_canoe_jetty", 11, 35, 4, shore_ok=True, solid=False)
    P("br_signpost", 19, 28, 5)

    # ---- Blackfathom headland: the sea cave and its warning stones -----------------------------------------
    A("rock_outcrop_large", 38, 26, 5)
    A("rock_outcrop_large", 22, 25, 5)
    P("br_signpost", 27, 27, 5)
    L.cp("driftwood_pile", 34, 29, 2)

    # ---- the Moonwell: a surface pool in a clearing, the cave under its north rim ---------------------------
    L.deco("moonwell_altar", 110, 94, 7, path_dir=E.AP)
    A("large_canopy_tree", 92, 86, 12)
    A("large_canopy_tree", 127, 88, 12)
    A("rock_outcrop_small", 100, 94, 4)
    A("rock_outcrop_small", 121, 96, 4)
    for (fx, fy) in ((103, 96), (117, 97), (98, 89), (123, 90), (110, 99)):
        A("fern_cluster", fx, fy, 3, solid=False)
    P("br_signpost", 114, 86, 5)
    A("ash_elune_statue", 105, 88, 7)
    A("ash_moon_lantern", 103, 93, 6, solid="core")
    A("ash_moon_lantern", 117, 93, 6, solid="core")
    A("ash_moon_sigil_stone", 121, 102, 5, solid="core")

    # ---- Maestra's Post: a Sentinel watch-camp on the lake shore ---------------------------------------------
    L.bld("moon_guard_tower", 90, 47, 11)
    L.bld("nightelf_house_small", 96, 61, 7)
    L.dp("vot_training_dummy", 92, 57, 3)
    L.dp("weapon_rack", 91, 50, 3)
    L.dp("vot_crate_stack", 99, 55, 3)
    L.dp("vot_fire_pit", 89, 59, 2, solid=False)
    P("br_signpost", 90, 65, 5)
    A("fallen_log", 68, 41, 3, solid=False)
    A("ash_sentinel_tent", 87, 53, 6)
    A("ash_sentinel_banner", 93, 54, 6, solid="core")
    A("ash_glaive_thrower", 101, 63, 4)
    A("ash_hippogryph_perch", 100, 51, 4)
    A("ash_archery_butts", 83, 59, 4)
    A("ash_herbalist_table", 96, 49, 4)
    A("ash_glaive_barricade", 84, 64, 4)

    # ---- the fork at the bluff: where the coast road splits to Zoram and Blackfathom ----------------------------
    P("br_signpost", 28, 52, 5)
    L.bld("generic_tent_a", 38, 48, 4)
    L.dp("vot_fire_pit", 34, 50, 2, solid=False)

    # ---- bluff camp on the coast road (a ranger waystation) -------------------------------------------------
    L.bld("generic_tent_a", 48, 98, 4)
    L.dp("vot_fire_pit", 44, 100, 2, solid=False)
    L.dp("vot_crate_stack", 51, 100, 3)
    L.cp("driftwood_pile", 30, 128, 3, shore_ok=True)
    L.cp("rowboat_wreck", 38, 150, 3, shore_ok=True)

    # ---- Ragged Highlands: furbolg country ---------------------------------------------------------------
    A("furbolg_den_entrance", 165, 46, 7)
    for (tx, ty) in ((158, 41), (171, 53)):
        A("furbolg_totem", tx, ty, 6, solid="core")
    for (tx, ty) in ((146, 36), (173, 38)):
        X("ashx_corrupt_furbolg_totem", tx, ty, 6, solid="core")
    L.dp("vot_hide_rack", 161, 52, 4)
    L.dp("vot_hide_rack", 168, 50, 4)
    L.dp("vot_fire_pit", 164, 52, 3, solid=False)
    A("ash_furbolg_lodge", 155, 50, 6)
    A("ash_furbolg_bonfire", 171, 58, 4)
    for (tx, ty) in ((151, 41), (176, 46), (156, 57)):
        A("dead_corrupted_tree", tx, ty, 7)
    # a second, lesser camp up the Mystral valley
    A("furbolg_totem", 134, 66, 6, solid="core")
    L.dp("vot_hide_rack", 137, 70, 4)
    A("ash_furbolg_lodge", 142, 71, 5)
    L.dp("vot_fire_pit", 135, 69, 2, solid=False)
    A("rock_outcrop_large", 150, 76, 5)
    A("ash_waterfall_pool", 154, 58, 7)

    # ---- Moonwhisper Grove: a ring of ancient trees round the moon pond ---------------------------------------
    import math
    for k in range(9):
        ang = k * 2 * math.pi / 9 + 0.35
        gx_, gy_ = 178 + 13.5 * math.cos(ang), 111 + 10.5 * math.sin(ang)
        A("large_canopy_tree", int(round(gx_)), int(round(gy_)), 12 if k % 2 == 0 else 11)
    for (fx, fy) in ((170, 114), (186, 116), (174, 120), (184, 105), (170, 104), (190, 110)):
        A("fern_cluster", fx, fy, 3, solid=False)
    A("fallen_log", 166, 118, 3, solid=False)
    A("ash_giant_ash_tree", 178, 99, 15)
    A("ash_moon_rune_stone", 169, 107, 6)
    A("ash_moon_rune_stone", 187, 107, 6)
    A("ash_nightbloom_bush", 168, 113, 3, solid=False)
    A("ash_nightbloom_bush", 188, 113, 3, solid=False)
    A("ash_glow_mushroom_ring", 178, 118, 3, solid=False)

    # ---- the ruined arch (Starfall ruins) -----------------------------------------------------------------------
    A("stone_archway", 176, 128, 7, solid="core")
    L.dp("broken_column", 170, 130, 4)
    L.dp("broken_column", 183, 131, 3)
    L.dp("broken_column", 173, 123, 3)
    A("ash_elven_ruin_wall", 172, 126, 6)
    A("ash_ivy_pillar", 182, 126, 6)
    A("ash_elf_statue_head", 168, 129, 3)
    A("ash_overgrown_steps", 177, 121, 4)
    A("fallen_log", 180, 124, 3, solid=False)

    # ---- Lake Elune'ara: the island shrine ---------------------------------------------------------------------
    L.deco("stone_archway", 106, 133, 5, path_dir=E.AP)

    # ---- Astranaar's gate (the town itself is its own zone south of here) ---------------------------------------
    L.bld("moon_guard_tower", 101, 157, 11)
    L.bld("moon_guard_tower", 123, 155, 11)
    P("br_signpost", 113, 165, 5)
    A("large_canopy_tree", 95, 150, 11)
    A("large_canopy_tree", 130, 149, 11)

    # ---- the Night Run: a nightsaber lair and a scout hide ------------------------------------------------------
    A("dead_corrupted_tree", 182, 172, 7)
    L.dp("skull_pile", 180, 174, 2)
    L.dp("vot_beast_ribcage", 186, 170, 3)
    L.bld("generic_tent_b", 152, 166, 4)
    L.dp("vot_fire_pit", 148, 168, 2, solid=False)
    A("rock_outcrop_large", 190, 160, 5)
    P("br_signpost", 134, 158, 5)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_ashenvale_west():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/aw_shape.png"
    if len(sys.argv) > 2 and sys.argv[2] == "build":
        import time
        t = time.time()
        L = build_layout()
        seen, walk, _ = E.reachable_report(L, (181, 106))
        print(f"built {time.time()-t:.1f}s  placed={L.placed} trees={L.trees} scattered={L.scattered} "
              f"woods_deco={L.woods_deco} landmarks={len(L.z.landmarks)} sealed={L.sealed} "
              f"clutter={L.clutter} walkable={walk} reachable={seen} skipped={len(L.skipped)}")
        for sk in L.skipped:
            if sk[0] not in ("fallen_log", "rock_outcrop_small", "fern_cluster"):
                print("  skipped", sk)
        SPEC.shape_preview(out, 4, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()), layout=L)
    else:
        SPEC.shape_preview(out, 4, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
    print("wrote", out)
