"""
Hand-built Stonetalon East (200x180), level 26-29: the half the volcano knocked flat (docs/stonetalon_brief.md).

Kyle, 15 Nov 2026: "lets start to build some new zones. Maybe stonetalon but with a frontier twist?" Then, in
four rounds of questions: 26-32 over two zones, SCARRED vs UNTOUCHED; Earth's redwoods, sequoias and a Cascades
volcano landed on it; in from the Barrens and from Ashenvale through the Talondeep Path; Sun Rock Retreat is the
town; Venture Co., Grimtotem, Windshear harpies, Earth beasts and elementals; a glimpse of Mulgore at the
south-east edge.

THE BLAST CAME FROM THE NORTH-WEST. Stonetalon Peak is a volcano now, and it's in Stonetalon West. When it
landed, its side blew out toward the south-east, the way St. Helens blew north. So this map is laid out along
that line:

    The north-west .......... the volcano's flank: rock, the way the blast came from
    The Blowdown ............ north and middle: the blast zone. Ash ground, the forest laid flat in rows, every
                              trunk pointing away from the peak. The Venture Co. salvage it
    Venture Salvage Yard .... in the Blowdown (64,44): their works
    Windshear Crag .......... north-east: rock spires and harpy nests
    Talondeep Path .......... north-east edge (172,4): the tunnel north to Ashenvale West
    Windshear Mine .......... the Venture Co.'s dig under the crag (188,44): the zone's cave
    The Barrens road ........ east edge (196,96): out to Northern Barrens
    Sun Rock Retreat ........ the town, its own map, up on its rock north of the junction; gate (144,93)
    The Standing Grove ...... south-west: the forest the blast missed, behind the ground's fold
    Grimtotem Compound ...... south (80,150): the hardline clan, pressing on Sun Rock
    The Mulgore Rim ......... south-east: where Mulgore's dark starts. A closed border. You look; you don't cross
    The Cutline ............. west edge (4,118): the Venture Co.'s road into the standing giants, Stonetalon West

ART. Kyle's Stonetalon sheets (docs/stonetalon_art_prompts.md) aren't generated yet, so the ground is painted
from the Aspen materials (ash, char, fireweed, duff, granite) by tools/bake_ashenvale.py stonetalon_east, and the
dressing uses Aspen's burned props. Every place that wants a Stonetalon sprite asks for it by name through st()
and falls back to the Aspen stand-in, so dropping the sheets into assets/tiles/stonetalon/props/ upgrades the
map with no code change.

HARD CONTRACTS (world/portal_manager.py)
    (196,96) Northern Barrens   (172,4) Ashenvale West   (144,93) Sun Rock Retreat
    (188,44) Windshear Mine     (4,118) Stonetalon West
    Doors to maps that don't exist yet wait in LATER_PORTALS (qa_portals fails a door that leads nowhere).
"""
import math
import os

import numpy as np

from tools import ashenvale_engine as E

BAKED_DIR = "assets/tiles/stonetalon/baked_east"
ASP = "assets/tiles/aspen/props/"
STP = "assets/tiles/stonetalon/props/"
W, H = 200, 180

DOORS = {(196, 96): ("Northern Barrens", (194, 96)), (172, 4): ("Ashenvale West", (172, 6)),
         (144, 93): ("Sun Rock Retreat", (144, 95)), (188, 44): ("Windshear Mine", (186, 45)),
         (4, 118): ("Stonetalon West", (6, 118))}
#: The doors whose maps exist. The rest are carved and framed but stay shut (qa_portals fails a door that leads
#: nowhere); each one is added here when its map is built.
BUILT = {"Northern Barrens", "Ashenvale West", "Sun Rock Retreat", "Windshear Mine"}
PORTALS = {xy: dest for xy, (dest, _a) in DOORS.items() if dest in BUILT}
ARRIVALS = [a for xy, (dest, a) in DOORS.items() if dest in BUILT]
LATER_PORTALS = {xy: dest for xy, (dest, _a) in DOORS.items() if dest not in BUILT}
START = (180, 97)      # a road tile on the Barrens road: everything must be reachable from here

# ------------------------------------------------------------------ the plan
ROADS = {
    # the Barrens road: in from the east to the junction under Sun Rock
    "barrens":   ([(197, 96), (184, 97), (168, 99), (152, 101), (140, 104)], 3.2),
    # the spine: the junction west through the Blowdown to the Cutline
    "spine":     ([(140, 104), (126, 100), (110, 92), (94, 84), (78, 86), (62, 96), (44, 106), (26, 114),
                   (12, 118), (3, 118)], 3.2),
    # north to the Talondeep Path, past the crag
    "talondeep": ([(164, 99), (166, 86), (166, 70), (165, 54), (166, 38), (168, 22), (172, 8), (172, 3)], 2.8),
    # the climb up to Sun Rock's gate, off the junction
    "sunrock":   ([(146, 101), (145, 97), (144, 94)], 2.6),
    # the mine spur under the crag
    "mine":      ([(165, 52), (174, 48), (182, 46), (188, 45)], 2.4),
    # the salvage yard, up into the Blowdown
    "salvage":   ([(88, 84), (80, 70), (72, 56), (66, 46)], 2.6),
    # south to the Grimtotem
    "grimtotem": ([(100, 89), (98, 106), (94, 124), (86, 140), (80, 148)], 2.4),
    # south-east from the junction toward the Rim, ending at the overlook
    "rim":       ([(132, 103), (130, 118), (136, 132), (148, 144), (160, 154), (170, 162)], 2.4),
    # a hunters' trail into the Standing Grove
    "grove":     ([(44, 106), (40, 122), (36, 138), (34, 150)], 2.2),
}

RIVERS = [   # Ashfall Creek: off the volcano, grey with silt, down through the Blowdown to the south
    ([(52, 0), (56, 22), (64, 40), (82, 62), (104, 74), (116, 96), (114, 120), (106, 146), (100, 180)], 2.8, 1.1),
]
FORDS = [(108, 86, 6), (113, 98, 5)]
LAKES = {
    # a small pond below Sun Rock, and a mud pool in the Blowdown where the creek backed up behind the logs
    "pond": [(118, 128, 5.5, 4, 0, 0.6)],
    "mudpool": [(78, 58, 4.5, 3.2, 0, 1.4)],
}
DEEP_SHRINK = {"pond": 2.2, "mudpool": 2.0}

# ---- rock (impassable)
MESAS = [
    # Sun Rock: the town's mesa, north of the junction (the town is its own map; its gate is on the south face)
    (144, 80, 13, 10, 0),
    # the volcano's flank pushing in from the north-west
    (14, 26, 14, 18, 20), (32, 12, 16, 8, 0), (8, 62, 7, 12, 0),
    # Windshear Crag: a loose field of spires round the harpies' bowl
    (176, 24, 4.4, 3.8, 0), (186, 34, 4.0, 3.4, 0), (150, 30, 4.6, 4.0, 0), (144, 46, 4.0, 3.4, 0),
    (184, 60, 4.2, 3.6, 0), (190, 44, 5.5, 8, 0),
    # the mine's cliff face (the cave sprite stands against it)
    (194, 40, 6, 10, 0),
    # the fold of ground that sheltered the Standing Grove
    (60, 126, 9, 5, 25), (70, 118, 6, 4, 10),
    # the Grimtotem's back wall
    (70, 166, 12, 5, 0), (96, 168, 9, 4, 0),
    # broken country near the Rim
    (178, 132, 6, 5, 0), (190, 150, 5, 8, 0),
]
RIDGES = [
    ([(120, 40), (128, 54), (126, 70)], 2.6),        # a spur between the Blowdown and the crag
    # the blast's hummocks: long low ribs of debris, all lying along the line the blast travelled (NW -> SE),
    # so the Blowdown reads as one event and walks as lanes rather than one open field
    ([(28, 34), (40, 44), (50, 52)], 2.4),
    ([(76, 18), (88, 28), (96, 36)], 2.2),
    ([(38, 60), (50, 70), (58, 76)], 2.2),
    ([(96, 50), (106, 58)], 2.0),
    ([(24, 80), (34, 88)], 2.0),
    ([(120, 150), (128, 162), (140, 168)], 2.4),     # between the Grimtotem and the Rim
]

# ---- woods (impassable standing forest): only where the blast didn't reach
WOODS = [
    (22, 150, 14, 16, 0, 1.2), (48, 166, 12, 8, 0, 0.5), (12, 98, 6, 8, 0, 2.2),
    (110, 170, 10, 6, 0, 1.7), (196, 120, 5, 10, 0, 0.9),
]
BELTS = []
CLEARINGS = [   # carved back out of the woods
    (34, 146, 9, 8),            # the hunters' clearing in the Standing Grove
    (8, 118, 8, 7),             # the Cutline gate
]

# painting-only patches for the baker (cx, cy, rx, ry)
#: the blast zone: grey ash over everything the blast flattened (bake: "burned" ash, "scorch" char)
BURNED_PATCHES = [(72, 58, 58, 42), (112, 44, 22, 22), (40, 92, 22, 16), (104, 92, 20, 14)]
#: fireweed is the first thing back after a burn, coming up pink through the ash (bake: the "bell" layer)
BLUEBELL_PATCHES = [(58, 76, 10, 6), (96, 52, 8, 5), (40, 46, 8, 6), (84, 98, 7, 4)]
#: the Mulgore Rim: the dark creeping in from the south-east (bake: "corrupt" and "fel")
CORRUPT_PATCHES = [(182, 162, 24, 16), (192, 140, 10, 16), (160, 172, 16, 8)]
#: Sun Rock's packed red earth at the foot of the gate, and the Grimtotem's trampled ground
PAVED_PATCHES = [(138, 104, 5, 3)]
GRADE = (1.0, 1.04)
#: inside the blast, ash covers the living ground completely (tools/bake_ashenvale.py)
BURN_SUPPRESS = 1.3
#: and at the Rim the dark covers it too
DARK_SUPPRESS = 1.2


def satyr_field(P, wp):
    """The Grimtotem compound's trampled earth (the baker's "satyr" layer)."""
    return P.blob(80, 150, 16, 11, 0.8, wp)


GAPS = [
    ("ell", 196, 96, 8, 7),
    ("ell", 172, 4, 7, 6),
    ("ell", 4, 118, 8, 7),
    ("ell", 144, 95, 6, 4),
    ("ell", 188, 45, 6, 5),
    ("ell", 64, 46, 12, 9),          # the salvage yard
    ("ell", 80, 150, 12, 9),         # the Grimtotem compound
    ("ell", 168, 160, 8, 6),         # the overlook
]

SPEC = E.Spec("Stonetalon East", W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK,
              mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={"south": 5}, rock_rim={"north": 8, "west": 7, "east": 6}, gaps=GAPS, fords=FORDS,
              thicket=None)

#: Quests are given in Sun Rock Retreat (its own map). Two of Sun Rock's people stand at the Rim overlook: it's
#: where the town watches the dark from. Written by tools/sync_stonetalon_npcs.py.
NPC_POSITIONS = {}

CAVES = {   # portal tile -> (sprite, w, h)
    (188, 44): ("ent_collapsed_mine", 9, 7),
    (172, 4): ("ent_cliff_road_tunnel", 9, 7),
    (144, 93): ("ent_town_tauren_totems", 9, 7),
}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("The Blowdown", 18, 18, 112, 92, None),
    ("Venture Salvage Yard", 48, 30, 34, 28, None),
    ("Windshear Crag", 136, 12, 60, 60, None),
    ("The Standing Grove", 6, 124, 56, 52, None),
    ("Grimtotem Compound", 58, 132, 46, 32, None),
    ("The Mulgore Rim", 146, 140, 54, 40, None),
]

# the few standing conifers the blast missed: the Standing Grove and the sheltered edges
TREES = {
    "big": [(f"{ASP}asp_pine_tall.png", 10), (f"{ASP}asp_pine_tall.png", 11)],
    "mid": [(f"{ASP}asp_pine_tall.png", 9), (f"{ASP}asp_pine_young.png", 7)],
    "small": [(f"{ASP}asp_pine_young.png", 6), (f"{ASP}asp_pine_young.png", 7)],
    "woods": [(f"{ASP}asp_pine_tall.png", 10), (f"{ASP}asp_pine_tall.png", 11), (f"{ASP}asp_pine_bent.png", 9)],
}

#: the blast's line: from the peak in the north-west, out to the south-east. Fallen trunks point along it.
BLAST_FROM = (-20.0, -30.0)


def st(name, fallback):
    """A Stonetalon sheet sprite when it's been filed, else the Aspen stand-in: (name, dir)."""
    if os.path.exists(f"{STP}{name}.png"):
        return name, STP
    return fallback, ASP


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


def blast(x, y):
    """0..1: how hard the blast hit this spot (the baker's ash and the dressing both read it)."""
    best = 0.0
    for (cx, cy, rx, ry) in BURNED_PATCHES:
        d = math.hypot((x - cx) / rx, (y - cy) / ry)
        best = max(best, min(1.0, max(0.0, 1.3 - d)))
    return best


def build_layout():
    AL = E.make_layout_class(SPEC, "Stonetalon East",
                             "The side of Stonetalon the volcano knocked flat. Grey ash, the forest laid down in "
                             "rows, and the Venture Co. hauling it away. Sun Rock still stands.",
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
    flat = np.zeros((H, W), bool)
    for (cx, cy, rx, ry) in BURNED_PATCHES:
        flat |= np.hypot((xs - cx) / rx, (ys - cy) / ry) < 1.0
    dark = np.zeros((H, W), bool)
    for (cx, cy, rx, ry) in CORRUPT_PATCHES:
        dark |= np.hypot((xs - cx) / rx, (ys - cy) / ry) < 1.0
    L.flat_mask, L.dark_mask = flat, dark
    saved = L.free_mask.copy()
    # living trees only where the blast didn't reach
    L.free_mask = saved & ~flat & ~dark
    E.scatter_trees(L, TREES, seed=6101, spacing=5.0)
    L.free_mask = saved & flat
    blowdown(L)
    L.free_mask = saved & dark
    rim(L)
    L.free_mask = saved
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def blowdown(L):
    """The forest laid flat. Fallen trunks everywhere the blast hit, a few charred snags still standing, burned
    stumps. Heavier near the peak, thinning to the south-east."""
    import random
    rnd = random.Random(6102)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    logs = snags = stumps = 0
    log_a = st("st_log_redwood", "asp_trunk_snapped")
    log_b = st("st_giant_snag", "asp_aspen_fallen")
    snag = st("st_giant_snag", "asp_snag_charred")
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        hit = blast(x, y)
        r = rnd.random()
        if logs < 110 and r < 0.030 * hit:
            name, d = log_a if rnd.random() < 0.6 else log_b
            if L.prop(name, x, y, rnd.choice((3, 4)), path_dir=d, solid="core", nudge=0):
                L.free_mask[max(0, y - 2):y + 3, max(0, x - 3):x + 4] = False
                logs += 1
        elif snags < 45 and r < 0.040 * hit:
            name, d = snag
            if L.prop(name, x, y, rnd.choice((6, 7)), path_dir=d, solid="core", nudge=0):
                L.free_mask[max(0, y - 2):y + 3, max(0, x - 2):x + 3] = False
                snags += 1
        elif stumps < 40 and r < 0.050 * hit:
            if L.prop("asp_stump_burned", x, y, 3, path_dir=ASP, solid="core", nudge=0):
                L.free_mask[max(0, y - 1):y + 2, max(0, x - 1):x + 2] = False
                stumps += 1
    L.blowdown = (logs, snags, stumps)


def rim(L):
    """The Mulgore Rim: dead grass and nothing growing, the odd charred snag, the thorn fence."""
    import random
    rnd = random.Random(6103)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = 0
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if n >= 14:
            break
        if L.free_mask[y, x] and rnd.random() < 0.02:
            if L.prop("asp_snag_standing", x, y, 6, path_dir=ASP, solid="core", nudge=0):
                L.free_mask[max(0, y - 2):y + 3, max(0, x - 2):x + 3] = False
                n += 1
    L.rim_snags = n


def sprinkle(L):
    """Ground clutter, a little: fireweed and deadfall in the Blowdown, ferns in the Grove, rocks everywhere."""
    import random
    rnd = random.Random(6104)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    weed = ferns = rocks = 0
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        flat = L.flat_mask[y, x]
        if L.dark_mask[y, x]:
            continue
        if flat and weed < 50 and r < 0.030:
            if L.prop("asp_fireweed", x, y, 2, path_dir=ASP, solid=False, nudge=0):
                weed += 1
        elif not flat and ferns < 40 and r < 0.030:
            if L.prop("asp_ferns", x, y, 2, path_dir=ASP, solid=False, nudge=0):
                ferns += 1
        elif rocks < 30 and r < 0.040:
            if L.prop("asp_boulder_lichen" if not flat else "asp_boulder", x, y, 3, path_dir=ASP,
                      solid="core", nudge=0):
                rocks += 1
    L.clutter = (weed, ferns, rocks)


CHEST_SPOTS = [
    (30, 40), (96, 30), (110, 60), (48, 84), (88, 110), (150, 64), (178, 74), (20, 140), (48, 150),
    (70, 140), (124, 140), (158, 170), (186, 110),
]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    P = L.prop
    A = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=ASP, **kw)

    def S(name, fallback, x, y, h, **kw):
        n, d = st(name, fallback)
        return L.prop(n, x, y, h, path_dir=d, **kw)

    # ---- the Barrens road in -----------------------------------------------------------------------------------
    P("br_signpost", 184, 92, 5)
    A("asp_boulder_split", 190, 102, 4)

    # ---- the junction under Sun Rock: the town's front door ------------------------------------------------------
    P("br_signpost", 156, 104, 5)
    A("tau_totem_carved", 136, 98, 5, solid="core")
    A("tau_totem_carved", 152, 98, 5, solid="core")
    A("tau_hitching_post", 128, 106, 3)

    # ---- the Venture Salvage Yard: the goblins working the fallen giants ------------------------------------------
    L.bld("bd_warehouse", 56, 42, 7)
    S("st_venture_bunkhouse", "tau_timber_stack", 74, 40, 4)
    S("st_log_deck", "asp_deadfall_pile", 58, 52, 4)
    S("st_log_deck", "asp_deadfall_pile", 72, 52, 4)
    S("st_saw_rig", "tau_timber_stack", 66, 36, 4)
    S("st_sawdust_burner", "asp_stump_burned", 50, 50, 4)
    P("br_signpost", 82, 62, 5)
    L.dp("vot_crate_stack", 62, 46, 3)
    L.dp("vot_crate_stack", 70, 46, 3)

    # ---- the Blowdown's landmarks: the biggest of the fallen ------------------------------------------------------
    S("st_sequoia_rootplate", "asp_deadfall_pile", 44, 64, 6)
    S("st_log_redwood", "asp_trunk_snapped", 92, 46, 5)
    S("st_giant_snag", "asp_snag_charred", 100, 66, 8)
    A("asp_elk_skull", 84, 74, 2, solid=False)

    # ---- Windshear Crag: the harpies' nests in the spires --------------------------------------------------------
    S("st_harpy_nest", "asp_deadfall_pile", 168, 36, 3)
    S("st_harpy_nest", "asp_deadfall_pile", 158, 24, 3)
    S("st_wind_spire", "asp_talus_pile", 178, 50, 5)
    A("asp_talus_pile", 152, 58, 3)
    A("asp_boulder_lichen", 172, 66, 3)

    # ---- the mine: the Venture Co.'s dig under the crag ----------------------------------------------------------
    S("st_ore_cart", "asp_boulder", 182, 50, 3)
    L.dp("vot_crate_stack", 180, 40, 3)

    # ---- the Talondeep Path: north to Ashenvale -----------------------------------------------------------------
    P("br_signpost", 166, 14, 5)

    # ---- the Standing Grove: the forest the blast missed ---------------------------------------------------------
    A("asp_ferns", 30, 142, 2, solid=False)
    A("asp_huckleberry", 38, 150, 2, solid=False)
    A("tau_drying_rack", 36, 142, 3)                # a tauren hunters' camp

    # ---- the Grimtotem Compound -------------------------------------------------------------------------------
    S("st_grim_tent", "tau_hide_tent_small", 72, 146, 5)
    S("st_grim_tent", "tau_hide_tent_small", 88, 144, 5)
    S("st_grim_war_totem", "tau_totem_carved", 80, 140, 6)
    S("st_grim_drum", "tau_cook_fire", 80, 154, 3)
    S("st_grim_hide_rack", "tau_drying_rack", 92, 154, 3)
    S("st_grim_palisade", "tau_timber_stack", 66, 156, 3)

    # ---- the Mulgore Rim: where the dark starts ---------------------------------------------------------------
    S("st_rim_thorn_fence", "asp_deadfall_pile", 162, 166, 3)
    S("st_rim_thorn_fence", "asp_deadfall_pile", 176, 166, 3)
    S("st_burial_platform", "tau_drying_rack", 180, 156, 5)
    S("st_rim_cairn", "asp_talus_pile", 168, 156, 3)
    A("asp_elk_skull", 156, 160, 2, solid=False)

    # ---- the Cutline: west into the standing giants -------------------------------------------------------------
    S("st_logged_stump", "asp_aspen_stump", 16, 110, 3)
    S("st_logged_stump", "asp_aspen_stump", 18, 126, 3)
    P("br_signpost", 16, 114, 5)


def register_baked(zone):
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_stonetalon_east():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(DOORS), npc=list(NPC_POSITIONS.values()))


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/ste_shape.png"
    if len(sys.argv) > 2 and sys.argv[2] == "build":
        import time
        t = time.time()
        L = build_layout()
        seen, walk, _ = E.reachable_report(L, START)
        print(f"built {time.time()-t:.1f}s  placed={L.placed} trees={L.trees} scattered={L.scattered} "
              f"landmarks={len(L.z.landmarks)} sealed={L.sealed} blowdown={L.blowdown} rim={L.rim_snags} "
              f"clutter={L.clutter} walkable={walk} reachable={seen} skipped={len(L.skipped)}")
        for sk in L.skipped:
            if sk[0] not in ("asp_fireweed", "asp_ferns", "asp_boulder", "asp_boulder_lichen"):
                print("  skipped", sk)
        SPEC.shape_preview(out, 4, portals=list(DOORS), npc=list(NPC_POSITIONS.values()), layout=L)
    else:
        SPEC.shape_preview(out, 4, portals=list(DOORS), npc=list(NPC_POSITIONS.values()))
    print("wrote", out)
