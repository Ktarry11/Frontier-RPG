"""
Hand-built Deadwind East (200x180), levels 56-58: the Sleeping Gorge, the Vice, Karazhan, the places where time stopped,
and the rupture under the wheel (docs/deadwind_brief.md, docs/deadwind_quest_plan.md).

Kyle, 18 Nov 2026: the east is "the rupture, the wheel, Karazhan's crag, the stopped avalanche", and "keep somewhat
authentic wow shape. Slightly modified though." So it keeps Classic's bones: the way south to Karazhan runs down the
Sleeping Gorge, a chasm in the east of the pass, and turns east at the bottom into the Vice, which brings you out under
the tower in the south. The old road to the Swamp of Sorrows still leaves to the south-east, but the liquidators have
shut it. What's new is the middle: this is where the leylines tore. The ground is ash and old dust, and the further
in you go the less time behaves.

    West road ............ west edge (4,62): from Deadwind West, to the rim of the gorge
    The Sleeping Gorge ... the chasm down the west of the map. The road goes down into it at (58,60) and follows the
                           floor south. A black stream runs along it, and in one stretch it has stopped. The old high
                           road crossed it on a bridge (66,44) that broke in the tear; a liquidator's echo is stuck at
                           its west end mid-stride.
    Ariden's Camp ........ the gorge's west rim, south (42,118), looking out over the Vice at the tower
    The Drowned Hollow ... south-west: a mere of seep water, and the Drowned Seep's mouth in the hill above it (30,145)
    The Vice ............. the narrow valley east from the gorge's foot to Karazhan
    Karazhan ............. south-east: the tower on its crag, sealed in stopped time, and the ground at its foot where
                           its servants wandered out
    The Stopped Places ... the plateau east of the gorge, up the ramp from its floor (112,70): floating rock, a crow in a
                           shard of stopped air, the elder tree that aged ten thousand years in a second
    The Hanging Slide .... north of the Stopped Places: a rockslide stopped halfway down the cliff
    The Rupture .......... east of the middle: the glow crater, the wheel standing over it, the liquidators'
                           containment spire, and the Exclusion Zone's door at the wheel's foot (152,93)
    The swamp road ....... south-east edge (194,118): the road to the Swamp of Sorrows, closed at the liquidators'
                           barricade

HARD CONTRACTS (world/portal_manager.py)
  portals  Deadwind West (4,62) <-> its east road (196,62); The Exclusion Zone (152,93) <-> its way out;
           The Drowned Seep (30,145) <-> its way out
"""
import numpy as np

from tools import ashenvale_engine as E

BAKED_DIR = "assets/tiles/deadwind/baked_east"
DWP = "assets/tiles/deadwind/props/"
BLD = "assets/buildings/"
W, H = 200, 180
NAME = "Deadwind East"

PORTALS = {(4, 62): "Deadwind West", (152, 93): "The Exclusion Zone", (30, 145): "The Drowned Seep"}
ARRIVALS = [(6, 62), (152, 94), (30, 146)]
START = (112, 72)     # the Stopped Places: everything must be reachable from here

# ------------------------------------------------------------------ the plan
ROADS = {
    # in from the west to the gorge's rim
    "west":     ([(3, 62), (20, 62), (34, 62), (46, 62)], 3.0),
    # down into the Sleeping Gorge and south along its floor
    "gorge":    ([(46, 62), (58, 61), (64, 72), (66, 88), (68, 104), (70, 120), (74, 132)], 2.8),
    # east at the gorge's foot, through the Vice to Karazhan
    "vice":     ([(74, 132), (88, 136), (104, 137), (122, 138), (140, 139), (148, 139)], 2.6),
    # up the ramp out of the gorge onto the plateau and the Stopped Places
    "ramp":     ([(66, 86), (80, 86), (94, 80), (106, 74), (112, 72)], 3.0),
    # north to the Hanging Slide
    "slide":    ([(106, 74), (102, 60), (96, 48)], 2.4),
    # east to the rupture and the wheel
    "rupture":  ([(112, 72), (126, 76), (140, 84), (150, 92)], 3.0),
    # south from the rupture to the tower's foot
    "tower":    ([(152, 96), (158, 112), (154, 128), (148, 139)], 2.6),
    # the old road to the Swamp of Sorrows, south-east, closed at the barricade
    "swamp":    ([(158, 112), (176, 117), (190, 118)], 2.6),
    # north along the west rim to the broken bridge
    "bridge":   ([(46, 62), (44, 52), (46, 44)], 2.2),
    # south along the west rim to Ariden's Camp and the Drowned Hollow
    "rim":      ([(46, 62), (42, 80), (38, 100), (40, 116), (36, 132), (30, 144)], 2.4),
}

RIVERS = [   # the gorge's stream, black and shallow, along the floor (never deep: it's walkable everywhere)
    ([(66, 8), (66, 40), (68, 66), (70, 96), (72, 120), (76, 134)], 1.7, -2.0),
]
FORDS = []
#: a stretch of the stream that stopped when the leylines tore: painted as stopped water
MOON_POOLS = [(69, 78, 7)]

LAKES = {"mere": [(46, 156, 12, 7, 0, 0.9)]}
DEEP_SHRINK = {"mere": 3.2}

# ---- rock: the gorge's walls, the Vice's walls, Karazhan's crag, the slide's cliff, the seep's hill
MESAS = [
    (52, 36, 6, 26, 0), (55, 94, 6, 28, 0), (62, 130, 6, 10, 0),                # the gorge's west wall
    (80, 38, 6, 32, 0), (82, 72, 6, 14, 0), (86, 114, 6, 22, 0),                # and its east wall
    (70, 151, 12, 6, 0),                                                          # the gorge's foot
    (110, 118, 26, 8, 0), (106, 155, 28, 8, 0),                                   # the Vice
    (172, 146, 16, 12, 0),                                                        # Karazhan's crag
    (98, 20, 12, 7, 0),                                                           # the cliff the slide hangs on
    (28, 134, 8, 6, 0),                                                           # the hill over the Drowned Seep
    (130, 52, 6, 5, 0), (182, 80, 7, 9, 0), (24, 84, 6, 5, 0), (130, 108, 6, 4, 0),
]
RIDGES = []

# ---- what's left of the forest: (cx, cy, rx, ry, rot, phase)
WOODS = [
    (120, 38, 8, 6, 0, 1.0), (182, 50, 8, 12, 0, 0.4), (126, 100, 6, 6, 0, 2.0), (186, 98, 6, 8, 0, 1.4),
    (28, 32, 10, 8, 0, 0.6), (18, 104, 6, 10, 0, 2.3), (150, 30, 10, 7, 0, 1.1),
]
BELTS = []
CLEARINGS = [
    (8, 62, 8, 6),              # the west road in
    (46, 62, 8, 6),             # the gorge's rim, where the road goes down
    (46, 44, 6, 4),             # the broken bridge's west end
    (42, 118, 9, 7),            # Ariden's Camp
    (32, 148, 8, 5),            # the Drowned Hollow
    (112, 70, 16, 11),          # the Stopped Places
    (96, 44, 8, 6),             # under the Hanging Slide
    (152, 90, 20, 14),          # the rupture
    (148, 138, 10, 8),          # Karazhan's foot
    (186, 118, 8, 6),           # the barricade on the swamp road
]
#: shattered time: the Stopped Places, the Hanging Slide, the bridge, the tower's foot
BLUEBELL_PATCHES = [(112, 70, 12, 9), (96, 44, 7, 5), (48, 44, 5, 4), (150, 136, 7, 4)]
#: slag and black glass: the rupture, thickest at the crater, the seep's mere, and down the gorge's floor
CORRUPT_PATCHES = [(152, 92, 30, 22), (46, 154, 14, 10), (100, 138, 10, 6), (68, 100, 6, 14)]
#: the glowing ash at the crater's lip
BURNED_PATCHES = [(152, 92, 15, 11)]
PAVED_PATCHES = [(148, 138, 6, 4), (42, 118, 3, 2)]
LUSH = 0.0
LIFT = (1.10, 1.32)     # the sheet is dark at source: lift it so the roads and the graves read

GAPS = [
    ("ell", 4, 62, 8, 7), ("ell", 152, 93, 8, 6), ("ell", 30, 146, 5, 3), ("ell", 46, 62, 7, 6),
    ("ell", 112, 70, 11, 8), ("ell", 152, 88, 14, 10), ("ell", 42, 118, 7, 5), ("ell", 148, 138, 8, 6),
    ("ell", 96, 44, 6, 4),
]

SPEC = E.Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK,
              mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={}, rock_rim={"north": 9, "east": 7, "south": 7, "west": 5}, gaps=GAPS, fords=FORDS,
              thicket=(0.74, 9.0, 0.6))


def plaza_field(P, wp):
    """Stained rings of old seep round the rupture."""
    return P.blob(152, 92, 19, 13, 0.6, wp)


def satyr_field(P, wp):
    """Rift rock, purple-cracked, at the crater's lip and under the tower."""
    return np.maximum(P.blob(152, 88, 10, 7, 0.6, wp), P.blob(162, 140, 8, 4, 0.6, wp))


NPC_POSITIONS = {
    "dw_ariden":      (44, 116),     # Ariden, at his camp on the gorge's rim, watching the tower
    "dw_bridge_echo": (48, 44),      # Mykola's echo, stuck mid-stride at the bridge's west end
    "dw_vessa":       (104, 86),     # Deathstalker Vessa Morrow, the Forsaken's eyes on the Stopped Places
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {(30, 145): ("ent_plague_cave", 8, 6)}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("The Ashen Rise", 0, 0, 200, 180, None),
    ("The Sleeping Gorge", 52, 8, 34, 136, None),
    ("The Broken Bridge", 40, 34, 40, 16, None),
    ("Ariden's Camp", 28, 106, 26, 24, None),
    ("The Drowned Hollow", 14, 128, 46, 46, None),
    ("The Vice", 78, 126, 70, 22, None),
    ("Karazhan", 140, 122, 56, 50, None),
    ("The Stopped Places", 88, 54, 44, 32, None),
    ("The Hanging Slide", 84, 10, 30, 42, None),
    ("The Rupture", 128, 70, 48, 40, None),
]

TREES = {
    "big":   [(DWP + "dw_dead_tree.png", 10), (DWP + "dw_aged_tree.png", 9)],
    "mid":   [(DWP + "dw_dead_birches.png", 8), (DWP + "dw_split_tree.png", 8)],
    "small": [(DWP + "dw_dead_birches.png", 7), (DWP + "dw_split_tree.png", 7)],
    "woods": [(DWP + "dw_dead_tree.png", 10), (DWP + "dw_aged_tree.png", 9), (DWP + "dw_split_tree.png", 10)],
}


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "Where the leylines tore. Ash and old dust, a gorge running black, a rockslide that "
                             "never landed, and in the middle of it all a wheel that came from another world.",
                             "Eastern Kingdoms - Deadwind Pass", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.seal_unreachable(L, START)
    dress(L)
    E.build_free_mask(L, NPC_POSITIONS.values())
    for lm in L.z.landmarks:
        ax, ay, w, h = lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]
        L.free_mask[max(0, ay):ay + h + 1, max(0, ax - 1):ax + w + 1] = False
    open_ground(L)
    E.scatter_trees(L, TREES, seed=5601, spacing=6.4, grove_keep=0.6)
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


#: no trees round the rupture: nothing grows within a long stone's throw of the wheel
NO_TREES = [(152, 92, 26, 20)]


def open_ground(L):
    """No trees in the clearings: the places the quests send you to are dressed by hand and stay open."""
    ys, xs = np.mgrid[0:H, 0:W]
    for (cx, cy, rx, ry) in CLEARINGS + NO_TREES:
        L.free_mask[np.hypot((xs - cx) / rx, (ys - cy) / ry) < 0.9] = False


def sprinkle(L):
    """Ground clutter: stones and ash, and the little stopped things you only notice when you're standing on them."""
    import random
    rnd = random.Random(5603)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = {"stones": 0, "ash": 0, "stopped": 0, "glass": 0}
    stopped = ("dw_frozen_leaves", "dw_air_tear", "dw_floating_rock")
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        if n["stones"] < 18 and r < 0.014:
            n["stones"] += bool(L.prop("dw_broken_stones", x, y, 3, path_dir=DWP, solid=False, nudge=0))
        elif n["ash"] < 10 and r < 0.024:
            n["ash"] += bool(L.prop("dw_ember_ash", x, y, 3, path_dir=DWP, solid=False, nudge=0))
        elif n["stopped"] < 14 and r < 0.034:
            n["stopped"] += bool(L.prop(stopped[rnd.randrange(3)], x, y, 3, path_dir=DWP, solid=False, nudge=0))
        elif n["glass"] < 10 and r < 0.040:
            n["glass"] += bool(L.prop("dw_glass_spire", x, y, 4, path_dir=DWP, solid=False, nudge=0))
    L.clutter = tuple(n.values())


CHEST_SPOTS = [
    (20, 50), (36, 90), (16, 150), (104, 52), (126, 86), (168, 74), (176, 104), (138, 128), (66, 100),
    (114, 30), (186, 160), (92, 140), (36, 24),
]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def landmark(L, path, cx, base_y, h, core=()):
    """A great piece of the map drawn as it is (the wheel, the tower, the bridge): the sprite, plus the few tiles of
    its feet that block, so nothing walks through a leg."""
    from tools import handbuilt_central_barrens as CB
    wt = max(1, round(h * CB._aspect(path)))
    L.z.add_landmark(path, cx - wt // 2, base_y - h + 1, wt, h, solid=False)
    for (x, y) in core:
        if L.z.interaction_layer[y][x] is None:
            L.z.collision_layer[y][x] = "landmark"


def dress(L):
    D = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=DWP, **kw)        # noqa: E731
    B = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=BLD, **kw)        # noqa: E731

    # ---- the west road in, and the rim where it goes down into the gorge
    B("dw_signpost", 14, 58, 5)
    D("dw_warning_cairn", 30, 68, 4, solid="core")
    D("dw_quarantine_stake", 50, 56, 4, solid="core")
    D("dw_rope_barrier", 40, 68, 3, solid="core")
    # ---- the broken bridge over the gorge, and Mykola's echo stuck at its west end
    landmark(L, BLD + "dw_broken_bridge.png", 65, 47, 14)
    D("dw_rotted_signpost", 42, 40, 4, solid="core")
    # ---- the Sleeping Gorge's floor: the stopped stretch of the stream, and what washed down
    D("dw_stopped_waterfall", 74, 76, 6, solid="core")
    D("dw_frozen_leaves", 64, 80, 4, solid=False)
    D("dw_carcass_heap", 66, 110, 4, solid="core")
    D("dw_bone_rock", 72, 96, 4, solid="core")
    # ---- Ariden's Camp on the rim, looking out at the tower
    B("dw_lean_to", 38, 114, 5, solid="core")
    D("dw_pyre_burned", 46, 122, 3, solid="core")
    D("dw_sundial", 36, 122, 4, solid="core")
    B("dw_map_table", 48, 114, 4, solid="core")
    D("dw_crow_perch", 34, 110, 5, solid="core")
    # ---- the Drowned Hollow
    D("dw_seep_pool", 38, 148, 3, solid="core")
    D("dw_crow_perch", 22, 148, 5, solid="core")
    D("dw_dissolved_deer", 40, 144, 4, solid="core")
    D("dw_tumour_tree", 18, 140, 7, solid="core")
    # ---- the Vice: the narrow way to the tower
    D("dw_echo_cottage", 96, 132, 5, solid="core")
    D("dw_broken_stones", 116, 134, 4, solid="core")
    D("dw_horse_skeleton", 128, 143, 4, solid="core")
    # ---- Karazhan: the tower on its crag, and the ground its servants wandered out onto
    landmark(L, BLD + "dw_dark_tower.png", 172, 150, 24)
    D("dw_stable_ruin", 140, 132, 6, solid="core")
    D("dw_iron_lamp", 144, 144, 4, solid="core")
    D("dw_iron_lamp", 154, 144, 4, solid="core")
    D("dw_air_tear", 156, 134, 5, solid="core")
    D("dw_rotted_angel", 138, 142, 5, solid="core")
    # ---- the Stopped Places: the elder tree and its sapling, the stopped crow, the floating rock
    landmark(L, BLD + "dw_elder_tree.png", 106, 66, 15, core=[(105, 66), (106, 66), (107, 66), (106, 65)])
    D("dw_aged_tree", 116, 64, 6, solid="core")
    D("dw_stopped_crow", 122, 72, 5, solid="core")
    D("dw_floating_rock", 100, 76, 4, solid="core")
    D("dw_stopped_fire", 118, 80, 4, solid="core")
    D("dw_time_doorway", 126, 66, 6, solid="core")
    D("dw_false_reflection", 108, 80, 3, solid=False)
    D("dw_sundial", 112, 76, 4, solid="core")
    # ---- the Hanging Slide
    landmark(L, BLD + "dw_stopped_avalanche.png", 98, 34, 12)
    D("dw_stopped_rockslide", 90, 42, 5, solid="core")
    D("dw_floating_rock", 102, 44, 4, solid="core")
    # ---- the rupture: the crater, the wheel over it, the spire, and the door at the wheel's foot
    # the wheel stands over everything: the tallest thing in the pass after the tower
    landmark(L, BLD + "dw_ferris_wheel.png", 152, 89, 24,
             core=[(145, 89), (146, 89), (158, 89), (159, 89)])
    D("dw_glow_crater", 152, 96, 5, solid=False, road_ok=True, allow_overlap=True)
    landmark(L, BLD + "dw_containment_spire.png", 136, 98, 18, core=[(135, 98), (136, 98), (137, 98)])
    # the ground round it, where the fallout comes up thickest
    D("dw_seep_pool", 168, 92, 3, solid="core")
    D("dw_seep_pool", 140, 112, 3, solid="core")
    D("dw_glow_crater", 170, 106, 3, solid="core")
    D("dw_tumour_growth", 158, 110, 5, solid="core")
    D("dw_flesh_pods", 166, 80, 4, solid="core")
    D("dw_slag_crystals", 134, 86, 4, solid="core")
    D("dw_fume_vent", 150, 108, 4, solid="core")
    D("dw_hand_roots", 172, 96, 3, solid="core")
    D("dw_eye_mushrooms", 144, 116, 3, solid="core")
    D("dw_rift_crack", 164, 96, 4, solid="core")
    D("dw_rift_crack", 142, 104, 4, solid="core")
    D("dw_slag_crystals", 166, 86, 4, solid="core")
    D("dw_fume_vent", 160, 104, 4, solid="core")
    D("dw_flesh_mass", 138, 84, 5, solid="core")
    D("dw_many_ribs", 168, 100, 4, solid="core")
    D("dw_quarantine_stake", 130, 80, 4, solid="core")
    D("dw_quarantine_stake", 144, 76, 4, solid="core")
    B("dw_sample_coffer", 130, 92, 3, solid="core")
    # ---- the swamp road, shut at the liquidators' barricade
    B("dw_quarantine_fence", 190, 116, 5, solid="core", road_ok=True)
    B("dw_quarantine_fence", 190, 121, 5, solid="core", road_ok=True)
    D("dw_rope_barrier", 184, 113, 3, solid="core")
    D("dw_quarantine_stake", 182, 122, 4, solid="core")
    B("dw_signpost", 178, 112, 5)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_deadwind_east():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
