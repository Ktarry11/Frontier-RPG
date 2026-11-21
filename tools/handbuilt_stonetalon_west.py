"""
Hand-built Stonetalon West (200x180), level 29-32: the giants the blast didn't reach (docs/stonetalon_brief.md).

Kyle, 15 Nov 2026: Stonetalon is SCARRED vs UNTOUCHED, and the Earth that landed on it is "all of it": redwood fog
in the low valleys, giant sequoias higher up, the volcano at the top. The East is what the blast knocked flat.
This is what stood behind the ridge and kept standing, and what the Venture Co. are cutting into now.

    Stonetalon Peak ...... north: the volcano. A ring of rim you can walk, the crater lake inside it, steam vents,
                           and the elementals the mountain woke. The Ashvent (a lava tube cave) opens on its
                           east flank (150,40)
    The Sequoia Slopes ... the middle band: the giant sequoias, and the greatest of them, the dungeon (96,70)
    Greatwood Vale ....... south and south-west: coastal redwoods in the fog, ferns and creeks
    Mistwalker Camp ...... the far side's quest camp (60,140): quest givers only, no inn, no flight master
    The Venture Cutline .. east (150-196, 100-140): where the goblins are cutting into the standing forest. The
                           way back to Stonetalon East (196,118)
    The way west ......... (4,150): toward Desolace, cut and shut until Desolace exists

THE FOREST IS THE WALL. Like Ashenvale, the dense redwood canopy is impassable and the paths are what's been cut or
walked through it; the giants stand in groves in the open ground, trunks you walk round with the crown overhead.

ART. Until Kyle's tree sheet lands (docs/stonetalon_art_prompts.md sheet 2) the giants are stand-ins from the
Ashenvale canopy trees and the Aspen pines; st() asks for each Stonetalon sprite by name and falls back, so filing
the sheet upgrades the map with no code change.

HARD CONTRACTS (world/portal_manager.py)
    (196,118) Stonetalon East   (96,70) the sequoia dungeon   (150,40) the Ashvent   (4,150) Desolace (later)
"""
import math
import os

import numpy as np

from tools import ashenvale_engine as E
from world.chunk_paths import exists as _chunk_exists  # noqa: E402  (.webp, .jpg or .png)

BAKED_DIR = "assets/tiles/stonetalon/baked_west"
ASP = "assets/tiles/aspen/props/"
STP = "assets/tiles/stonetalon/props/"
W, H = 200, 180

DOORS = {(196, 118): ("Stonetalon East", (194, 118)), (96, 70): ("The Eldest Sequoia", (96, 72)),
         (150, 40): ("The Ashvent", (150, 42)), (4, 150): ("Desolace", (6, 150))}
#: The doors whose maps exist; the rest are carved and framed but shut (qa_portals fails a door that leads nowhere).
BUILT = {"Stonetalon East", "The Ashvent", "The Eldest Sequoia"}
PORTALS = {xy: dest for xy, (dest, _a) in DOORS.items() if dest in BUILT}
ARRIVALS = [a for xy, (dest, a) in DOORS.items() if dest in BUILT]
LATER_PORTALS = {xy: dest for xy, (dest, _a) in DOORS.items() if dest not in BUILT}
START = (186, 118)

# ------------------------------------------------------------------ the plan
ROADS = {
    # the Cutline: in from the East, the goblins' haul road
    "cutline":  ([(197, 118), (184, 118), (170, 116), (156, 114), (142, 112)], 3.2),
    # the old trail up through the giants to the dungeon's tree
    "slopes":   ([(142, 112), (130, 104), (118, 92), (106, 80), (98, 72)], 2.8),
    # on up to the volcano's rim, switching back
    "peak":     ([(118, 92), (128, 80), (124, 66), (134, 54), (130, 42), (118, 34), (104, 30)], 2.4),
    # the rim path round the crater (the crater lake is inside it)
    "rim":      ([(104, 30), (88, 26), (78, 16), (86, 8), (104, 6), (120, 10), (124, 22), (118, 34)], 2.2),
    # the Ashvent spur, off the peak road
    "ashvent":  ([(134, 54), (142, 46), (150, 42)], 2.2),
    # down into Greatwood Vale and Mistwalker Camp
    "vale":     ([(142, 112), (126, 124), (106, 132), (86, 136), (68, 140), (60, 140)], 2.8),
    # west out of the camp toward Desolace
    "west":     ([(60, 140), (42, 146), (24, 150), (3, 150)], 2.6),
    # a fern trail south-east into the deep vale
    "fern":     ([(86, 136), (92, 152), (104, 164)], 2.0),
}

RIVERS = [   # Mistfall Creek: down from the peak through the vale to the south edge
    ([(70, 40), (66, 62), (58, 84), (52, 108), (58, 128), (76, 150), (84, 180)], 2.6, 1.0),
]
FORDS = [(53, 106, 5), (64, 140, 5)]
LAKES = {
    # the crater lake, inside the rim
    "crater": [(102, 18, 15, 9, 0, 0.4)],
    "tarns": [(32, 128, 4, 3, 0, 1.2), (128, 156, 5, 3.5, 0, 2.1)],
}
DEEP_SHRINK = {"crater": 3.4, "tarns": 1.8}

# ---- rock (impassable): the volcano's cone round the rim, its flanks, and granite through the slopes
MESAS = [
    # the cone: rock all round the rim, outside it
    (70, 18, 10, 14, 0), (134, 18, 10, 14, 0), (102, 40, 14, 5, 0),
    # the flanks
    (40, 30, 16, 12, 10), (168, 30, 16, 12, -10), (20, 60, 10, 12, 0), (180, 70, 10, 10, 0),
    # granite outcrops among the sequoias
    (78, 78, 5, 4, 0), (140, 84, 6, 4, 20), (110, 100, 4, 3, 0),
]
RIDGES = [
    ([(150, 140), (162, 150), (176, 152)], 2.4),     # south of the Cutline
    ([(20, 100), (30, 110), (36, 120)], 2.2),        # west of the vale
]

# ---- woods (impassable redwood forest): the vale is thick with it
WOODS = [
    (30, 168, 22, 10, 0, 1.2), (130, 172, 22, 8, 0, 0.6), (100, 148, 10, 8, 0, 2.0), (16, 128, 8, 14, 0, 1.0),
    (88, 112, 8, 7, 0, 2.5), (156, 160, 14, 8, 0, 0.9), (40, 90, 10, 9, 0, 0.3), (176, 96, 10, 8, 0, 1.6),
    (160, 66, 8, 8, 0, 2.2),
]
BELTS = []
CLEARINGS = [
    (60, 140, 12, 9),          # Mistwalker Camp
    (96, 74, 12, 9),           # the great sequoia's clearing
    (190, 118, 8, 7),          # the Cutline gate
    (8, 150, 8, 7),            # the way west
]

# painting-only patches for the baker
#: the volcano's ash and cinder, on the cone and the rim
BURNED_PATCHES = [(102, 20, 40, 22), (150, 40, 10, 8)]
#: sorrel and fern carpets in the vale
BLUEBELL_PATCHES = [(70, 150, 18, 10), (110, 140, 14, 8), (40, 136, 10, 8)]
CORRUPT_PATCHES = []
PAVED_PATCHES = []
GRADE = (1.10, 1.10)
BURN_SUPPRESS = 1.3

GAPS = [
    ("ell", 196, 118, 8, 7),
    ("ell", 96, 70, 7, 5),
    ("ell", 150, 41, 6, 5),
    ("ell", 4, 150, 8, 7),
    ("ell", 60, 140, 10, 8),
    ("ell", 104, 30, 6, 4),
]

SPEC = E.Spec("Stonetalon West", W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK,
              mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={"south": 6, "west": 6}, rock_rim={"north": 5, "east": 6}, gaps=GAPS, fords=FORDS,
              thicket=(0.70, 10.0, 1.3))

#: Mistwalker Camp's quest givers stand here (tools/sync_stonetalon_npcs.py, with the quests).
NPC_POSITIONS = {
    "mw_camp_leader":    (56, 138),   # Mistwalker Iyana Rainsong, by the fire
    "mw_arborist":       (52, 141),   # Tamsin Reyes, by her climbing gear
    "mw_ex_venture":     (64, 146),   # Nozzle Quickspan, as far from the totem as he can get
    "mw_forsaken_chem":  (48, 144),   # Alchemist Rennick Toll, downwind
}

CAVES = {   # portal tile -> (sprite, w, h): the mouth faces the way you come
    (150, 40): ("ent_volcanic_fissure", 9, 7),
}

SUBZONES = [   # (table_key, x, y, w, h, display_name)
    ("Greatwood Vale", 8, 112, 140, 64, None),
    ("The Sequoia Slopes", 50, 52, 120, 60, None),
    ("Stonetalon Peak", 60, 0, 90, 46, None),
    ("The Venture Cutline", 146, 100, 52, 44, None),
    ("Mistwalker Camp", 48, 130, 24, 20, None),
]


def st(name, fallback, fallback_dir):
    """A Stonetalon sheet sprite when it's been filed, else the stand-in: full path."""
    if os.path.exists(f"{STP}{name}.png"):
        return f"{STP}{name}.png"
    return f"{fallback_dir}{fallback}.png"


AP = E.AP
TREES = {
    "big": [(st("st_redwood_giant", "large_canopy_tree", AP), 13), (st("st_redwood_twin", "canopy_tree_cluster", AP), 12)],
    "mid": [(st("st_redwood_giant", "large_canopy_tree", AP), 12), (st("st_redwood_young", "medium_canopy_tree", AP), 9)],
    "small": [(st("st_redwood_young", "medium_canopy_tree", AP), 8), (st("st_redwood_young", "medium_canopy_tree", AP), 9)],
    "woods": [(st("st_redwood_giant", "large_canopy_tree", AP), 13), (st("st_redwood_twin", "canopy_tree_cluster", AP), 12)],
}
#: the sequoia slopes: a different tree, warmer and wider
SEQUOIAS = [(st("st_sequoia_mature", "large_canopy_tree", AP), 14), (st("st_sequoia_young", "medium_canopy_tree", AP), 10),
            (st("st_sequoia_scarred", "canopy_tree_cluster", AP), 13)]


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


def build_layout():
    AL = E.make_layout_class(SPEC, "Stonetalon West",
                             "The side of Stonetalon the blast never reached. Redwoods in the fog, sequoias on the "
                             "slopes, a volcano at the top, and the Venture Co. cutting their way in.",
                             "Kalimdor - Stonetalon", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.seal_unreachable(L, START)
    dress(L)
    E.build_free_mask(L, NPC_POSITIONS.values())
    for lm in L.z.landmarks:
        ax, ay, w, h = lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]
        L.free_mask[max(0, ay):ay + h + 1, max(0, ax - 1):ax + w + 1] = False
    ys, xs = np.mgrid[0:H, 0:W]
    peak = np.zeros((H, W), bool)
    for (cx, cy, rx, ry) in BURNED_PATCHES:
        peak |= np.hypot((xs - cx) / rx, (ys - cy) / ry) < 1.0
    slopes = (ys > 46) & (ys < 112) & (xs > 50) & (xs < 170)
    cut = (xs > 146) & (ys > 100) & (ys < 144)
    saved = L.free_mask.copy()
    # the vale's redwoods
    L.free_mask = saved & ~peak & ~slopes & ~cut
    E.scatter_trees(L, TREES, seed=6201, spacing=4.6)
    # the sequoias on the slopes, fewer and bigger
    L.free_mask = saved & slopes & ~peak
    E.scatter_trees(L, {"big": SEQUOIAS, "mid": SEQUOIAS, "small": SEQUOIAS[1:2], "woods": TREES["woods"]},
                    seed=6202, spacing=6.0, woods_deco=False)
    L.free_mask = saved & cut
    cutline(L)
    L.free_mask = saved & peak
    volcano(L)
    L.free_mask = saved
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def cutline(L):
    """The Venture Co.'s cut: stumps where the giants stood, a few logs not hauled yet."""
    import random
    rnd = random.Random(6203)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = 0
    stump = st("st_logged_stump", "asp_aspen_stump", ASP)
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if n >= 30:
            break
        if L.free_mask[y, x] and rnd.random() < 0.05:
            d, nm = os.path.split(stump)
            if L.prop(nm[:-4], x, y, 4, path_dir=d + "/", solid="core", nudge=0):
                L.free_mask[max(0, y - 2):y + 3, max(0, x - 2):x + 3] = False
                n += 1
    L.stumps = n


def volcano(L):
    """The cone: talus, boulders, the odd dead snag. No trees grow on fresh cinder."""
    import random
    rnd = random.Random(6204)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = 0
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if n >= 26:
            break
        if L.free_mask[y, x] and rnd.random() < 0.04:
            name = rnd.choice(("asp_talus_pile", "asp_boulder", "asp_snag_charred"))
            if L.prop(name, x, y, 3 if name != "asp_snag_charred" else 6, path_dir=ASP, solid="core", nudge=0):
                L.free_mask[max(0, y - 2):y + 3, max(0, x - 2):x + 3] = False
                n += 1
    L.cone = n


def sprinkle(L):
    """Ferns everywhere in the vale, a few mossy boulders and fallen logs."""
    import random
    rnd = random.Random(6205)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    ferns = logs = rocks = 0
    fern = st("st_ferns_big", "asp_ferns", ASP)
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x] or y < 46:
            continue
        r = rnd.random()
        if ferns < 120 and r < 0.05:
            d, nm = os.path.split(fern)
            if L.prop(nm[:-4], x, y, 2, path_dir=d + "/", solid=False, nudge=0):
                ferns += 1
        elif logs < 16 and r < 0.056:
            if L.prop("asp_aspen_fallen", x, y, 3, path_dir=ASP, solid="core", nudge=0):
                logs += 1
        elif rocks < 24 and r < 0.064:
            if L.prop("asp_boulder_lichen", x, y, 3, path_dir=ASP, solid="core", nudge=0):
                rocks += 1
    L.clutter = (ferns, logs, rocks)


CHEST_SPOTS = [(30, 150), (120, 150), (80, 90), (150, 70), (90, 20), (176, 130), (40, 112), (130, 100)]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    P = L.prop
    A = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=ASP, **kw)

    def S(name, fallback, fdir, x, y, h, **kw):
        path = st(name, fallback, fdir)
        d, nm = os.path.split(path)
        return L.prop(nm[:-4], x, y, h, path_dir=d + "/", **kw)

    # ---- the Cutline gate and the goblins' camp in the cut
    P("br_signpost", 186, 112, 5)
    S("st_log_deck", "asp_deadfall_pile", ASP, 170, 108, 4)
    S("st_steam_winch", "tau_timber_stack", ASP, 160, 122, 4)
    S("st_climbing_rig", "asp_trunk_snapped", ASP, 152, 106, 5)
    L.bld("bd_warehouse", 176, 128, 7)
    L.dp("vot_crate_stack", 166, 124, 3)
    # ---- the great sequoia: the dungeon's tree (the door at its foot opens when the dungeon is built)
    # drawn without the prop checks (it's bigger than any footprint test likes), then its trunk made solid by hand:
    # a wall of bark either side of the split in its base, which is the door
    path = st("st_sequoia_great", "ash_giant_ash_tree", E.AP)
    import tools.handbuilt_central_barrens as CB
    hgt = 24
    wt = max(1, round(hgt * CB._aspect(path)))
    L.z.add_landmark(path, 96 - wt // 2, 69 - hgt + 1, wt, hgt, solid=False)
    for y in range(64, 69):
        for x in range(91, 102):
            if (x, y) != (96, 68) and L.z.interaction_layer[y][x] is None:
                L.z.collision_layer[y][x] = "landmark"
    # ---- Mistwalker Camp: a scouts' camp in the vale
    S("st_scout_camp", "tau_hide_tent_small", ASP, 54, 136, 5)
    A("tau_cook_fire", 62, 142, 3)
    A("tau_drying_rack", 66, 136, 3)
    A("tau_totem_carved", 52, 144, 5)
    # ---- the volcano: vents and the rim
    S("st_fumarole", "asp_talus_pile", ASP, 88, 30, 4)
    S("st_steam_vents", "asp_boulder", ASP, 120, 30, 3)
    S("st_obsidian_boulder", "asp_boulder_split", ASP, 112, 8, 3)
    # ---- the way west
    P("br_signpost", 14, 144, 5)


def register_baked(zone):
    if os.path.isdir(BAKED_DIR) and _chunk_exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_stonetalon_west():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/stw_shape.png"
    if len(sys.argv) > 2 and sys.argv[2] == "build":
        L = build_layout()
        seen, walk, _ = E.reachable_report(L, START)
        print(f"placed={L.placed} trees={L.trees} landmarks={len(L.z.landmarks)} sealed={L.sealed} "
              f"stumps={L.stumps} cone={L.cone} clutter={L.clutter} walkable={walk} reachable={seen} "
              f"skipped={len(L.skipped)}")
        for sk in L.skipped:
            if sk[0] not in ("asp_ferns", "asp_boulder_lichen", "asp_aspen_fallen", "st_ferns_big"):
                print("  skipped", sk)
        SPEC.shape_preview(out, 4, portals=list(DOORS), npc=list(NPC_POSITIONS.values()), layout=L)
    else:
        SPEC.shape_preview(out, 4, portals=list(DOORS), npc=list(NPC_POSITIONS.values()))
    print("wrote", out)
