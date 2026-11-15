"""
Hand-built South Felwood (150x200), level 51-53: the contested half of Felwood (claude/felwood_brief.md).

Kyle, 14 Nov 2026: "a modified Felwood where the elves are working with the furbolgs to take it back...
the southern part will look like a high level Ashenvale, the north is demon wastes. We can keep shape
similar to actual WoW." So this is WoW's Felwood valley read north-up: a long north-south forest walled
by mountains (Hyjal's slopes on the east), the road running up its spine from Ashenvale.

THE SOUTH IS RECLAIMED. Kyle: "southern felwood will NOT get fel stuff bro, it is reclaimed", and "bottom
85% of the zone is ashenvale, top 10-15% STARTS to get some fel... so it's not jarring when they go
north". So everything below the Fel Line (y ~30) is living, high-level Ashenvale forest with wild
animals and territorial treants in it; Shatter Scar Vale's craters are healed scars grown over with moss
and flowers. Only the northern band bleeds: dying trees, a few demons, the first fel.

Structure (tile coords, y down):

    Ashenvale road ...... south edge (74,196): the road up from Ashenvale East
    Morlos'Aren ......... a night elf watch on the road (80,176), half lost and half retaken
    Iris Lake ........... a purified lake east of the road (106,158): the druids' first cleansed water
    Hollowbark Glade .... an old-growth glade in the south-west (36,148): treants, sabers, wisps
    Emerald Sanctuary ... the town, its own map; its gate (100,118) is east of the road at the fork
    The river ........... north -> south down the west of the valley, fords at the two west roads
    Ruins of Constellas . old Highborne ruins in the west (34,98), retaken by the forest
    Shatter Scar Vale ... healed craters on the road north (70,52): the Legion's scars, grown over
    The Fel Line ........ the northern band (y < 30): where North Felwood's corruption bleeds through
    North gate .......... north edge (70,4): on into North Felwood (53-55)

HARD CONTRACTS (world/portal_manager.py):
    portals  Ashenvale road (74,196); later Emerald Sanctuary (100,118) and North Felwood (70,4),
    which go in LATER_PORTALS until those maps exist.
"""
import math

import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_central_barrens import ENT

BAKED_DIR = "assets/tiles/felwood/baked_south"
FP = "assets/tiles/felwood/props/"      # Kyle's Felwood sheet (tools/file_felwood_art.py)
W, H = 150, 200

PORTALS = {(74, 196): "Ashenvale East", (100, 118): "Emerald Sanctuary", (70, 4): "North Felwood"}
ARRIVALS = [(74, 194), (98, 119), (70, 6)]
#: Laid as soon as the maps behind them exist (qa_portals fails a door that leads nowhere). The
#: clearings, roads and gaps for both are already cut.
LATER_PORTALS = {}
START = (76, 186)      # a road tile: everything must be reachable from here

# ------------------------------------------------------------------ the plan
ROADS = {
    # the spine: Ashenvale -> Morlos'Aren -> the Sanctuary fork -> Shatter Scar -> the north gate
    "spine":      ([(74, 197), (76, 186), (80, 176), (84, 162), (89, 146), (92, 130), (91, 120), (86, 108),
                    (79, 92), (73, 74), (70, 58), (67, 40), (66, 24), (68, 12), (70, 4)], 3.4),
    "sanctuary":  ([(91, 121), (96, 119), (100, 118)], 3.0),
    # west: Hollowbark Glade, over the lower ford
    "deadwood":   ([(84, 160), (72, 158), (60, 156), (49, 153), (38, 149)], 2.8),
    # west: the Ruins of Constellas, over the upper ford
    "constellas": ([(80, 94), (68, 93), (55, 94), (44, 97), (35, 99)], 2.8),
    # east: the trail round Iris Lake
    "iris":       ([(85, 158), (96, 160), (106, 165)], 2.4),
}

RIVERS = [   # (pts, half-width shallow, half-width deep): the river, out of the north
    ([(50, 0), (49, 26), (47, 52), (52, 76), (55, 96), (55, 116), (51, 136), (47, 156), (43, 178), (40, 200)],
     3.4, 1.5),
]
FORDS = [(55, 94, 6), (47, 155, 6)]

LAKES = {
    "iris": [(108, 156, 9, 6.5, 0, 0.6)],
    "tarns": [(24, 112, 4.5, 3.5, 0, 1.1), (118, 92, 4, 3, 0, 2.2), (60, 128, 3.5, 2.6, 0, 0.4)],
}
DEEP_SHRINK = {"iris": 3.0, "tarns": 1.8}
MOON_POOLS = [(108, 156, 11)]       # Iris Lake is purified water: it paints silver, not brown

# ---- rock (impassable): Hyjal's foothills on the east, crags on the west, the scar's crater rims
MESAS = [
    # Shatter Scar Vale: broken crater rims
    (58, 44, 4, 3, 10), (84, 48, 5, 3, -10), (76, 34, 3, 2.5, 0), (60, 62, 3, 2.5, 0),
    # east foothills pushing into the valley
    (126, 64, 8, 14, 0), (130, 120, 7, 12, 0), (124, 182, 8, 8, 0), (118, 34, 6, 8, 0),
    # west crags
    (18, 64, 7, 12, 0), (14, 176, 6, 10, 0), (22, 132, 5, 6, 0),
    # the narrows below the north gate
    (52, 18, 6, 6, 0), (86, 18, 7, 6, 0),
]
RIDGES = [
    ([(100, 70), (108, 84), (104, 100)], 2.4),      # a spur east of the spine
    ([(30, 74), (40, 80), (44, 70)], 2.2),          # behind Constellas
    ([(96, 186), (104, 178), (110, 184)], 2.0),     # east of Morlos'Aren
]

# ---- woods (impassable dense forest): (cx, cy, rx, ry, rot, phase)
WOODS = [
    # the living south: Ashenvale-deep forest
    (54, 184, 9, 8, 0, 1.2), (100, 196, 10, 5, 0, 0.6), (112, 140, 7, 10, 0, 2.0), (66, 140, 6, 9, 0, 0.9),
    (100, 100, 6, 7, 0, 1.6), (30, 170, 7, 6, 0, 2.4), (114, 172, 6, 6, 0, 0.3),
    # the corrupting north
    (34, 40, 8, 10, 0, 1.4), (98, 44, 7, 9, 0, 0.7), (96, 140, 4, 6, 0, 2.7), (62, 108, 4, 6, 0, 1.0),
    (40, 120, 5, 6, 0, 2.1), (110, 116, 5, 5, 0, 0.5),
]
BELTS = []
CLEARINGS = [   # carved back out of the woods
    (74, 191, 10, 7),           # the Ashenvale road in
    (80, 176, 14, 10),          # Morlos'Aren
    (104, 160, 12, 9),          # Iris Lake's shore
    (36, 148, 15, 12),          # Hollowbark Glade
    (96, 120, 10, 7),           # the Sanctuary gate
    (34, 99, 15, 12),           # the Ruins of Constellas
    (70, 50, 20, 14),           # Shatter Scar Vale
    (70, 8, 10, 7),             # the north gate
]
# painting-only patches for the baker (cx, cy, rx, ry)
BLUEBELL_PATCHES = [(104, 160, 12, 8), (80, 178, 10, 6), (96, 122, 8, 5), (86, 140, 8, 6), (36, 148, 12, 8),
                    (70, 50, 14, 9), (34, 99, 10, 6)]
# Only the Fel Line bleeds (y < ~30). Everything south of it is reclaimed forest.
CORRUPT_PATCHES = [(70, 12, 46, 12), (44, 24, 12, 6), (98, 22, 12, 6)]
BURNED_PATCHES = [(66, 10, 6, 4)]
# Kyle, 14 Nov: "make southern more vibrant." The baker (tools/bake_ashenvale.py) lays more sunlit
# grass, ferns and bluebells on the living ground and grades it brighter and more saturated; the
# corrupt patches keep the sick, dim cast, so the colour itself shows where the Reclamation holds.
LUSH = 1.0
GRADE = (1.35, 1.12)        # (saturation, value) on living ground
PAVED_PATCHES = [(80, 176, 5, 4), (34, 99, 7, 5), (98, 119, 4, 3)]


GAPS = [
    ("ell", 74, 196, 8, 7),
    ("ell", 70, 4, 8, 7),
    ("ell", 100, 118, 6, 5),
    ("ell", 80, 176, 8, 7),
    ("ell", 36, 148, 9, 7),
    ("ell", 34, 99, 9, 7),
    ("ell", 70, 50, 10, 8),
    ("ell", 104, 160, 8, 6),
]

SPEC = E.Spec("South Felwood", W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK,
              mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={"north": 5, "south": 6}, rock_rim={"west": 9, "east": 11}, gaps=GAPS, fords=FORDS,
              thicket=(0.70, 10.0, 3.1))

#: Quests are given in Emerald Sanctuary (its own map). Morlos'Aren is a "safe" settlement in the encounter
#: tables, and "The Watch at Morlos'Aren" ends with Captain Saranis saying "I'll send two of my people down
#: there with a lantern", yet nobody stood in it (Felwood audit, 15 Nov 2026). These are those two, written
#: by tools/sync_felwood_south_npcs.py. They don't give quests: Kyle keeps the givers in the hubs.
NPC_POSITIONS = {
    "fs_morlosaren_sentinel": (77, 174),      # by the tent
    "fs_morlosaren_lookout": (84, 175),       # under the tower
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("Morlos'Aren", 62, 164, 36, 26, None),
    ("Iris Lake", 92, 144, 32, 30, None),
    ("Hollowbark Glade", 14, 130, 44, 36, None),
    ("Ruins of Constellas", 14, 80, 46, 36, None),
    ("Shatter Scar Vale", 44, 32, 56, 42, None),
    ("The Fel Line", 9, 3, 130, 29, None),
]

TREES = {
    "big": [("large_canopy_tree", 10), ("canopy_tree_cluster", 9), ("large_canopy_tree", 11)],
    "mid": [("medium_canopy_tree", 8), ("large_canopy_tree", 9), ("canopy_tree_cluster", 8)],
    "small": [("medium_canopy_tree", 7), ("medium_canopy_tree", 7)],
    "woods": [("large_canopy_tree", 10), ("canopy_tree_cluster", 9), ("large_canopy_tree", 11)],
}


def corruption(x, y):
    """0 = clean forest .. 1 = fully corrupt, from the same patches the baker paints."""
    best = 0.0
    for (cx, cy, rx, ry) in CORRUPT_PATCHES:
        d = np.hypot((x - cx) / rx, (y - cy) / ry)
        best = max(best, float(np.clip(1.4 - d, 0, 1)))
    return best


def build_layout():
    AL = E.make_layout_class(SPEC, "South Felwood",
                             "Ashenvale's forest running north into the corruption. The Emerald Reclamation "
                             "holds the south; the Legion's scars begin at Shatter Scar Vale.",
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
    ys, xs = np.mgrid[0:H, 0:W]
    dead = np.zeros((H, W), bool)
    for (cx, cy, rx, ry) in CORRUPT_PATCHES:
        dead |= np.hypot((xs - cx) / rx, (ys - cy) / ry) < 0.85
    L.dead_mask = dead
    saved = L.free_mask.copy()
    L.free_mask = saved & ~dead
    E.scatter_trees(L, TREES, seed=5101, spacing=4.2)
    L.free_mask = saved & dead
    dead_trees(L)
    L.free_mask = saved
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def dead_trees(L):
    """Burned and twisted trunks across the corrupt ground - sparse, a forest dying rather than dead."""
    import random
    rnd = random.Random(5102)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = 0
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if n >= 60:
            break
        if not L.free_mask[y, x] or rnd.random() >= 0.06:
            continue
        name = rnd.choice(("fw_corrupted_tree", "fw_corrupted_tree", "fw_half_cleansed_tree",
                           "fw_dead_ironwood", "dead_corrupted_tree"))
        path = FP if name.startswith("fw_") else E.AP
        if L.prop(name, x, y, rnd.choice((7, 8, 9)), path_dir=path, solid="core", nudge=0):
            L.free_mask[max(0, y - 3):y + 4, max(0, x - 3):x + 4] = False
            n += 1
    L.dead_trees = n


def sprinkle(L):
    """Ground clutter, a little: ferns and logs in the living forest, rocks everywhere."""
    import random
    rnd = random.Random(5103)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    ferns = logs = rocks = 0
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        dead = L.dead_mask[y, x]
        if ferns < 90 and r < 0.040 and not dead:
            if L.prop("fern_cluster", x, y, 3, path_dir=E.AP, solid=False, nudge=0):
                ferns += 1
        elif logs < 18 and r < 0.046 and not dead:
            if L.prop("fallen_log", x, y, 3, path_dir=E.AP, solid=False, nudge=0):
                logs += 1
        elif rocks < 26 and r < 0.056:
            if L.prop("rock_outcrop_small", x, y, 4, path_dir=E.AP, solid=False, nudge=0):
                rocks += 1
    L.clutter = (ferns, logs, rocks)


CHEST_SPOTS = [
    (60, 186), (98, 182), (110, 150), (88, 132), (28, 156), (46, 140), (22, 104), (48, 104),
    (108, 104), (60, 76), (88, 56), (54, 40), (82, 28), (100, 64),
]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    P = L.prop
    A = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=E.AP, **kw)
    X = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=E.XP, **kw)
    F = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=FP, **kw)

    # ---- the road in from Ashenvale -------------------------------------------------------------------------
    P("br_signpost", 79, 188, 5)
    F("fw_ashenvale_tree", 66, 188, 10)
    F("fw_ashenvale_tree", 84, 192, 10)

    # ---- Morlos'Aren: a night elf watch on the road, half lost and half retaken -----------------------------
    L.bld("fw_sentinel_tower", 88, 172, 9)
    L.bld("fw_sentinel_tent", 72, 172, 6)
    L.bld("fw_stake_barricade", 80, 168, 5)
    F("fw_fallen_statue", 70, 181, 5)
    A("ash_moon_lantern", 75, 178, 6, solid="core")
    A("ash_moon_lantern", 86, 179, 6, solid="core")
    X("ashx_burned_treehouse", 92, 183, 9)            # the half that was lost
    F("fw_half_cleansed_tree", 64, 176, 9)
    L.dp("vot_crate_stack", 84, 170, 3)
    P("br_signpost", 85, 166, 5)

    # ---- Iris Lake: the first water the druids cleansed --------------------------------------------------------
    F("fw_purified_moonwell", 98, 152, 5)
    A("ash_moon_lantern", 98, 164, 6, solid="core")
    A("ash_moon_lantern", 114, 166, 6, solid="core")
    F("fw_moonflowers", 100, 166, 3, solid=False)
    F("fw_moonflowers", 117, 152, 3, solid=False)
    F("fw_ashenvale_tree", 96, 146, 10)
    F("fw_ashenvale_tree", 120, 162, 10)
    A("ash_living_gate_arch", 94, 160, 8, solid=False, road_ok=True)
    L.bld("fw_druid_treehouse", 102, 172, 9)

    # ---- the Sanctuary gate: the town is its own map -----------------------------------------------------------
    F("fw_ashenvale_tree", 104, 112, 10)
    F("fw_ashenvale_tree", 104, 126, 10)
    P("br_signpost", 92, 116, 5)

    # ---- Hollowbark Glade: old growth, the forest's own -------------------------------------------------------
    for k in range(6):
        ang = k * 2 * math.pi / 6 + 0.4
        F("fw_ashenvale_tree", int(round(36 + 12.0 * math.cos(ang))), int(round(148 + 8.5 * math.sin(ang))), 11)
    A("ash_glow_mushroom_ring", 34, 147, 3, solid=False)
    F("fw_moonflowers", 40, 151, 3, solid=False)
    A("fallen_log", 30, 152, 3, solid=False)
    A("rock_outcrop_large", 44, 142, 5)

    # ---- the Ruins of Constellas: Highborne stone, retaken by the forest ---------------------------------------
    for k in range(7):
        ang = k * 2 * math.pi / 7 + 0.3
        F("fw_highborne_column", int(round(34 + 11.0 * math.cos(ang))), int(round(99 + 7.5 * math.sin(ang))),
          5 if k % 2 == 0 else 4)
    F("fw_highborne_arch", 34, 92, 7, solid=False, road_ok=True)
    F("fw_purified_moonwell", 34, 100, 5)
    F("fw_fallen_statue", 46, 92, 5)
    F("fw_moonflowers", 26, 104, 3, solid=False)
    F("fw_ashenvale_tree", 22, 94, 10)

    # ---- Shatter Scar Vale: the Legion's craters, healed over ---------------------------------------------------
    A("rock_outcrop_large", 64, 48, 5)
    A("rock_outcrop_large", 79, 56, 5)
    A("rock_outcrop_small", 70, 40, 4, solid=False)
    F("fw_moonflowers", 62, 52, 3, solid=False)
    F("fw_moonflowers", 82, 52, 3, solid=False)
    F("fw_moonflowers", 72, 44, 3, solid=False)
    F("fw_ashenvale_tree", 58, 58, 10)
    F("fw_half_cleansed_tree", 86, 44, 9)          # the one the druids haven't finished
    A("ash_glow_mushroom_ring", 74, 58, 3, solid=False)
    A("fern_cluster", 66, 56, 3, solid=False)
    P("br_signpost", 74, 64, 5)

    # ---- the Fel Line: North Felwood bleeding through -----------------------------------------------------------
    F("fw_fel_crystals", 58, 20, 4)
    F("fw_fel_pool", 86, 22, 4, solid=False)
    F("fw_fel_mushrooms", 46, 24, 4)
    F("fw_demon_bones", 96, 14, 3, solid=False)
    L.bld("fw_stake_barricade", 64, 30, 5)          # the Sentinels' line across the road
    L.bld("fw_stake_barricade", 78, 30, 5)

    # ---- the north gate: on into North Felwood -----------------------------------------------------------------
    F("fw_corrupted_tree", 62, 12, 8)
    F("fw_dead_ironwood", 80, 12, 8)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_felwood_south():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/fws_shape.png"
    if len(sys.argv) > 2 and sys.argv[2] == "build":
        import time
        t = time.time()
        L = build_layout()
        seen, walk, _ = E.reachable_report(L, START)
        print(f"built {time.time()-t:.1f}s  placed={L.placed} trees={L.trees} scattered={L.scattered} "
              f"woods_deco={L.woods_deco} landmarks={len(L.z.landmarks)} sealed={L.sealed} "
              f"clutter={L.clutter} dead={L.dead_trees} walkable={walk} reachable={seen} skipped={len(L.skipped)}")
        for sk in L.skipped:
            if sk[0] not in ("fallen_log", "rock_outcrop_small", "fern_cluster"):
                print("  skipped", sk)
        SPEC.shape_preview(out, 4, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()), layout=L)
    else:
        SPEC.shape_preview(out, 4, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
    print("wrote", out)
