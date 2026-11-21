"""
Hand-built Deadwind West (200x180), levels 55-57: the tunnel in from Stranglethorn, the dead forest, Deadman's Crossing,
the ogres' ravine and Morgan's Plot (docs/deadwind_brief.md, docs/deadwind_quest_plan.md).

Kyle, 18 Nov 2026: two maps for the pass, the west and the east, with the liquidators' camp (Ariden's Watch) its own
map, and "keep somewhat authentic wow shape. Slightly modified though." So it keeps Classic's bones: the road crosses
the north of the pass at Deadman's Crossing, the ogres hold the ravine in the north-west, Morgan's Plot lies in the
south-east toward Karazhan (which is on the other map, just across the seam), and the way on east runs through the
Sleeping Gorge. What's changed is the way in (a tunnel from Stranglethorn, not Duskwood's road) and what's leaking
out of the middle.

The west is the part of Deadwind that still looks like Deadwind: a forest that died standing up, the old graves, the
ogres. The fallout is here, but it's thin. It runs down the Sickwater and pools in the Black Tarn, it's in the rock of
the tunnel, and it gets thicker the further east you go.

    The Cracked Tunnel ... south-west: the way in from Northern Stranglethorn (34,177), a crack through the mountain
                           that opened when the worlds came together, glowing more the further north you walk
    Delgado's Fence ...... the tunnel's mouth (50,130): the liquidators' quarantine line and the first sight of the pass
    Deadman's Crossing ... the north (96,66), where the roads meet; Ariden's Watch's gate is just south (96,74)
    Deadwind Ravine ...... north-west: the ogres' ravine, and Grosh'gok Compound in it
    The Widows' Wood ..... north-east: the spiders' wood, and the Widows' Nest in the crag (150,24)
    The Sickwater ........ the stream off the north mountains, carrying the seep south-west to the Black Tarn
    Baba Hanna's ......... west of the crossing: a homestead in the dead forest, and the old woman who won't leave it
    Coachman's Bend ...... on the road south to the Plot, where a wagon crashes every few minutes and has for months
    Morgan's Plot ........ south-east: the old graveyard under the cliff, the great crypt, the dead who don't stay down
    East road ............ east edge (196,62): on into Deadwind East

THE ART is Kyle's Deadwind sheets (docs/deadwind_art_prompts.md): tools/bake_ashenvale.py deadwind_west paints the
ground from sheet 1 (DEADWIND_SHEET), and the trees, graves, ogres and fallout are sheets 2 and 3.

HARD CONTRACTS (world/portal_manager.py)
  portals  Northern Stranglethorn (34,177) <-> its tunnel mouth (182,115); Ariden's Watch (96,74) <-> its gate;
           Deadwind East (196,62) <-> its west road (4,62); The Widows' Nest (150,24) <-> its way out
"""
import numpy as np

from tools import ashenvale_engine as E
from world.chunk_paths import exists as _chunk_exists  # noqa: E402  (.webp, .jpg or .png)

BAKED_DIR = "assets/tiles/deadwind/baked_west"
DWP = "assets/tiles/deadwind/props/"      # Kyle's Deadwind props sheets (docs/deadwind_art_prompts.md sheets 2 and 3)
BLD = "assets/buildings/"
W, H = 200, 180
NAME = "Deadwind West"

PORTALS = {(34, 177): "Northern Stranglethorn", (96, 74): "Ariden's Watch", (196, 62): "Deadwind East",
           (150, 24): "The Widows' Nest"}
ARRIVALS = [(34, 175), (96, 72), (194, 62), (150, 25)]
START = (96, 64)     # Deadman's Crossing: everything must be reachable from here

# ------------------------------------------------------------------ the plan
ROADS = {
    # up the tunnel from Stranglethorn, out at Delgado's Fence
    "tunnel": ([(34, 178), (34, 168), (38, 158), (36, 148), (42, 138), (50, 130)], 2.6),
    # the old pass road north-east from the fence to Deadman's Crossing
    "pass":   ([(50, 130), (58, 116), (68, 100), (80, 84), (90, 72), (96, 66)], 3.2),
    # the Watch's gate, just off the crossing
    "watch":  ([(96, 66), (96, 73)], 3.0),
    # west up Deadwind Ravine to Grosh'gok's gate
    "ravine": ([(96, 66), (82, 58), (68, 50), (56, 44), (46, 40)], 2.8),
    # east over the Sickwater ford and out to Deadwind East
    "east":   ([(96, 66), (114, 64), (132, 62), (154, 60), (176, 62), (197, 62)], 3.2),
    # south past Coachman's Bend to Morgan's Plot
    "plot":   ([(132, 62), (136, 80), (140, 98), (146, 114), (150, 128)], 2.8),
    # north through the Widows' Wood to the nest
    "nest":   ([(154, 60), (154, 46), (152, 34), (150, 25)], 2.4),
}

RIVERS = [   # the Sickwater, off the north mountains into the Black Tarn
    ([(118, 0), (116, 22), (114, 44), (116, 62), (112, 84), (104, 104), (96, 124), (92, 142)], 3.0, 1.3),
]
FORDS = [(116, 63, 6)]

LAKES = {"tarn": [(88, 152, 13, 8, 0, 0.8)]}
DEEP_SHRINK = {"tarn": 3.2}

# ---- rock: the mountain the tunnel goes through, the ravine's walls, the cliff over the Plot, the nest's crag
MESAS = [
    (28, 162, 24, 18, 0), (12, 128, 12, 16, 0), (62, 168, 12, 8, 0), (54, 154, 9, 13, 0),
    (22, 140, 10, 8, 0),                                                    # the mountain round the tunnel
    (58, 24, 9, 9, 0), (18, 62, 11, 7, 0), (52, 62, 6, 5, 0),             # Deadwind Ravine's walls
    (178, 138, 9, 15, 0), (160, 162, 16, 7, 0),                             # the cliff over Morgan's Plot
    (150, 14, 12, 8, 0),                                                    # the crag the Widows' Nest is in
    (72, 140, 7, 5, 0), (128, 40, 5, 5, 0), (180, 30, 9, 7, 0), (86, 26, 6, 5, 0), (120, 120, 5, 4, 0),
]
RIDGES = [
    ([(54, 150), (48, 140), (56, 136)], 2.2),       # the tunnel's east wall where it opens out
]

# ---- the dead forest (impassable): (cx, cy, rx, ry, rot, phase)
WOODS = [
    (24, 96, 12, 18, 0, 1.0), (82, 30, 12, 9, 0, 2.0), (178, 92, 10, 12, 0, 0.6), (84, 110, 9, 8, 0, 2.3),
    (118, 142, 8, 10, 0, 1.1), (176, 42, 8, 8, 0, 0.2), (62, 156, 8, 6, 0, 2.6), (104, 30, 8, 10, 0, 1.7),
    (158, 96, 7, 8, 0, 0.9), (126, 104, 6, 7, 0, 2.2), (44, 100, 7, 9, 0, 1.3), (70, 74, 7, 6, 0, 0.5),
]
BELTS = []
CLEARINGS = [   # carved back out of the forest
    (50, 130, 10, 8),           # Delgado's Fence, the tunnel's mouth
    (96, 66, 12, 9),            # Deadman's Crossing
    (36, 38, 16, 12),           # Grosh'gok Compound
    (152, 136, 18, 12),         # Morgan's Plot
    (138, 90, 9, 6),            # Coachman's Bend
    (150, 30, 10, 7),           # the nest's mouth
    (186, 62, 10, 8),           # the east road out
    (116, 63, 8, 7),            # the Sickwater ford
    (88, 150, 18, 12),          # the Black Tarn's shore
]
#: the seep, glowing roots in the dead forest: where the Sickwater and the tunnel have carried it
BLUEBELL_PATCHES = [(130, 72, 7, 5), (64, 92, 7, 5), (160, 46, 6, 5), (40, 146, 4, 6)]
#: the fallout proper, pustule ground and glowing cracks: along the Sickwater, round the tarn, and thicker to the east
CORRUPT_PATCHES = [(38, 150, 5, 8), (114, 40, 7, 12), (102, 112, 9, 10), (88, 152, 16, 11), (184, 60, 14, 14)]
#: the green ash where the dead forest burned (it burns green), round the Watch's gate and the ogres' fires
BURNED_PATCHES = [(100, 76, 5, 3), (36, 38, 9, 6)]
PAVED_PATCHES = [(154, 134, 9, 6), (96, 66, 4, 3)]
LUSH = 0.0
LIFT = (1.10, 1.32)     # the sheet is dark at source: lift it so the roads and the graves read

GAPS = [
    ("ell", 34, 177, 6, 6), ("ell", 96, 74, 7, 5), ("ell", 196, 62, 8, 7), ("ell", 150, 26, 6, 5),
    ("ell", 50, 130, 8, 6), ("ell", 96, 66, 9, 7), ("ell", 36, 38, 12, 9), ("ell", 152, 136, 12, 8),
    ("ell", 138, 90, 7, 5),
]

SPEC = E.Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK,
              mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={}, rock_rim={"north": 9, "east": 6, "south": 7, "west": 6}, gaps=GAPS, fords=FORDS,
              thicket=(0.66, 10.0, 1.1))


def plaza_field(P, wp):
    """Grave earth over Morgan's Plot."""
    return P.blob(152, 138, 15, 10, 0.6, wp)


def satyr_field(P, wp):
    """Trodden camp mud: the ogres' yard and the liquidators' fence line."""
    return np.maximum(P.blob(36, 38, 13, 10, 0.6, wp), P.blob(50, 131, 6, 4, 0.6, wp))


#: the pass's own people (tools/build_deadwind.py writes them; docs/deadwind_quest_plan.md)
NPC_POSITIONS = {
    "dw_delgado":     (54, 127),     # Corporal Ray Delgado, on his fence at the tunnel's mouth
    "dw_mourner":     (144, 130),    # the Forsaken at Morgan's Plot who wants a name read
    "dw_grull":       (60, 48),      # Grull the Younger, on the ravine road outside the compound
    "dw_hanna":       (44, 75),      # Baba Hanna, at the homestead she won't leave
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {(150, 24): ("ent_spider_lair", 8, 6)}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("The Dead Forest", 0, 0, 200, 180, None),
    ("The Sickwater", 104, 0, 22, 140, None),
    ("The Widows' Wood", 130, 6, 56, 46, None),
    ("Deadwind Ravine", 8, 10, 62, 52, None),
    ("Grosh'gok Compound", 18, 24, 38, 30, None),
    ("Deadman's Crossing", 82, 54, 30, 26, None),
    ("Coachman's Bend", 128, 82, 22, 16, None),
    ("Morgan's Plot", 132, 120, 52, 34, None),
    ("The Black Tarn", 70, 136, 40, 30, None),
    ("The Cracked Tunnel", 6, 136, 48, 44, None),
    ("Delgado's Fence", 40, 120, 22, 16, None),
]

TREES = {
    "big":   [(DWP + "dw_dead_tree.png", 10), (DWP + "dw_split_tree.png", 9), (DWP + "dw_dead_tree.png", 11)],
    "mid":   [(DWP + "dw_dead_birches.png", 8), (DWP + "dw_dead_tree.png", 9), (DWP + "dw_tumour_tree.png", 8)],
    "small": [(DWP + "dw_dead_birches.png", 7), (DWP + "dw_split_tree.png", 7)],
    "woods": [(DWP + "dw_dead_tree.png", 10), (DWP + "dw_dead_birches.png", 9), (DWP + "dw_split_tree.png", 10)],
}


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "A forest that died standing, the old graves under the cliff, and the ogres in their "
                             "ravine. The glow comes down the Sickwater from the east, and it's getting closer.",
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
    E.scatter_trees(L, TREES, seed=5501, spacing=5.6, grove_keep=0.6)
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


#: no trees in the tunnel: it's a crack through a mountain
NO_TREES = [(40, 158, 22, 24), (44, 74, 7, 5)]


def open_ground(L):
    """No trees in the clearings: the places the quests send you to are dressed by hand and stay open."""
    ys, xs = np.mgrid[0:H, 0:W]
    for (cx, cy, rx, ry) in CLEARINGS + NO_TREES:
        L.free_mask[np.hypot((xs - cx) / rx, (ys - cy) / ry) < 0.9] = False


def sprinkle(L):
    """Ground clutter, a little: thorns and rotten logs in the forest, the odd growth that shouldn't be there."""
    import random
    rnd = random.Random(5503)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = {"thorn": 0, "log": 0, "stones": 0, "wrong": 0}
    wrong = ("dw_eye_mushrooms", "dw_hand_roots", "dw_teeth_flower", "dw_tumour_growth")
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        if n["thorn"] < 18 and r < 0.012:
            n["thorn"] += bool(L.prop("dw_thornbush", x, y, 3, path_dir=DWP, solid=False, nudge=0))
        elif n["log"] < 16 and r < 0.030:
            n["log"] += bool(L.prop("dw_fungus_log", x, y, 3, path_dir=DWP, solid=False, nudge=0))
        elif n["stones"] < 14 and r < 0.040:
            n["stones"] += bool(L.prop("dw_broken_stones", x, y, 3, path_dir=DWP, solid=False, nudge=0))
        elif n["wrong"] < 14 and r < 0.046:
            n["wrong"] += bool(L.prop(wrong[rnd.randrange(len(wrong))], x, y, 3, path_dir=DWP, solid=False, nudge=0))
    L.clutter = tuple(n.values())


CHEST_SPOTS = [
    (30, 80), (70, 120), (88, 96), (124, 84), (170, 76), (166, 40), (118, 30), (60, 34), (40, 112),
    (60, 150), (128, 150), (184, 160), (16, 40),
]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    D = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=DWP, **kw)        # noqa: E731
    B = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=BLD, **kw)        # noqa: E731

    # ---- the Cracked Tunnel: the runner's handcart halfway up, and the glow getting into the rock further on
    B("dw_body_cart", 38, 159, 4, solid="core")
    D("dw_sample_crate", 34, 155, 3, solid="core")
    D("dw_seep_boulder", 41, 147, 4, solid="core")
    D("dw_slag_crystals", 31, 143, 4, solid="core")
    D("dw_fume_vent", 46, 141, 4, solid="core")
    D("dw_warning_cairn", 30, 170, 4, solid="core")
    # ---- Delgado's Fence: the quarantine line across the tunnel's mouth
    B("dw_fence_gate", 50, 132, 5, solid=False, road_ok=True)
    B("dw_quarantine_fence", 43, 133, 4, solid="core")
    B("dw_quarantine_fence", 57, 131, 4, solid="core")
    D("dw_quarantine_stake", 40, 126, 4, solid="core")
    D("dw_rope_barrier", 58, 125, 3, solid="core")
    B("dw_signpost", 60, 122, 5)
    B("dw_burn_bin", 46, 125, 3, solid="core")
    B("dw_supply_stack", 59, 136, 4, solid="core")
    # ---- Deadman's Crossing, and the Watch's gate
    B("dw_signpost", 102, 60, 5)
    D("dw_rotted_signpost", 88, 63, 4, solid="core")
    D("dw_iron_lamp", 91, 75, 4, solid="core")
    D("dw_iron_lamp", 101, 75, 4, solid="core")
    B("dw_gatehouse", 96, 76, 8, solid=False, road_ok=True)
    D("dw_quarantine_stake", 86, 78, 4, solid="core")
    D("dw_quarantine_stake", 106, 78, 4, solid="core")
    # ---- Deadwind Ravine: Grosh'gok's gate across the ravine road, and the yard behind it
    B("dw_ogre_gate", 48, 42, 10, solid=False, road_ok=True)
    D("dw_ogre_palisade", 44, 30, 5, solid="core")
    D("dw_bone_rock", 50, 30, 4, solid="core")
    D("dw_ogre_hut", 28, 32, 6, solid="core")
    D("dw_ogre_hut", 22, 44, 6, solid="core")
    D("dw_ogre_hut", 34, 48, 6, solid="core")
    D("dw_ogre_cookpot", 36, 38, 4, solid="core")
    D("dw_ogre_banner", 40, 34, 5, solid="core")
    D("dw_ogre_banner", 40, 46, 5, solid="core")
    D("dw_bone_heap", 22, 34, 4, solid="core")
    D("dw_bone_heap", 28, 50, 4, solid="core")
    D("dw_ogre_cocoon", 30, 40, 5, solid="core")
    D("dw_carcass_heap", 38, 30, 4, solid="core")
    D("dw_skull_totem", 52, 36, 5, solid="core")
    D("dw_fused_ogre_tree", 64, 44, 7, solid="core")
    # ---- the Widows' Wood and the nest's mouth
    D("dw_web_mass", 142, 30, 5, solid="core")
    D("dw_web_cocoon", 158, 32, 5, solid="core")
    D("dw_egg_sacs", 156, 27, 3, solid="core")
    D("dw_bone_nest", 144, 26, 3, solid="core")
    D("dw_web_cocoon", 160, 46, 5, solid="core")
    # ---- Baba Hanna's homestead in the dead forest: a lean-to, a cold fire, a scarecrow of crow perches
    B("dw_lean_to", 40, 72, 5, solid="core")
    D("dw_pyre_burned", 48, 73, 3, solid="core")
    D("dw_crow_perch", 50, 78, 5, solid="core")
    B("dw_salt_barrel", 38, 77, 3, solid="core")
    # ---- the Sickwater and the Black Tarn
    D("dw_seep_pool", 122, 40, 3, solid="core")
    D("dw_dissolved_deer", 80, 146, 4, solid="core")
    D("dw_black_well", 100, 144, 4, solid="core")
    D("dw_tumour_growth", 76, 156, 5, solid="core")
    D("dw_crow_perch", 104, 156, 5, solid="core")
    # ---- Coachman's Bend: the wreck that keeps happening
    D("dw_wagon_wreck", 136, 92, 4, solid="core")
    D("dw_horse_skeleton", 144, 94, 4, solid="core")
    D("dw_echo_wagon", 146, 87, 4, solid=False)
    D("dw_echo_fence", 132, 96, 3, solid=False)
    # ---- Morgan's Plot: the great crypt against the cliff, the graves, the fence
    B("dw_great_crypt", 166, 134, 12, solid="core")
    D("dw_crypt", 146, 126, 6, solid="core")
    D("dw_crypt", 170, 150, 6, solid="core")
    D("dw_graves", 146, 140, 4, solid="core")
    D("dw_graves", 156, 144, 4, solid="core")
    D("dw_open_grave", 150, 146, 3, solid="core")
    D("dw_gravestone", 140, 138, 4, solid="core")
    D("dw_gravestone", 158, 128, 4, solid="core")
    D("dw_rotted_angel", 152, 130, 5, solid="core")
    D("dw_iron_fence", 138, 132, 4, solid="core")
    D("dw_iron_fence", 140, 146, 4, solid="core")
    D("dw_iron_lamp", 150, 136, 4, solid="core")
    # ---- out along the east road, the seep showing through
    D("dw_seep_boulder", 180, 54, 4, solid="core")
    D("dw_fume_vent", 188, 70, 4, solid="core")
    D("dw_slag_crystals", 172, 56, 4, solid="core")


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and _chunk_exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_deadwind_west():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
