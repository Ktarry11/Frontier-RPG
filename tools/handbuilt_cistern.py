"""
Hand-built The Cistern (120x130): the lower half of the Glittervein's dungeon. Levels 50-52, four
bosses.

ARCHETYPE: THE SEAM, continued. See tools/handbuilt_mother_vein.py for what that means and
tools/seam_kit.py for the geometry both halves share.

Kyle: "you enter, go through some bosses, at the other end is another way further down into the
dungeon into another map with more bosses. at the very end (after the last boss) brings you back
out to Lastwater."

SO THIS MAP HAS TWO DOORS AND THEY ARE NOT THE SAME DOOR. You arrive down the shaft at the bottom
of the Mother Vein and you leave through THE OUTFLOW at the top - and the outflow is not a
convenience, it is the answer. The water in the pool at Lastwater did not gather there. It was
pulled down here, and then it was pushed back up, and the channel it takes is the one the player
walks out through. A party that has fought from the dig head to the heart surfaces beside the camp
they started at, having physically followed the water home.

That is the end of five zones of argument. The Aspen melt came early. The Southern Needles went
dry. The Shimmering Flats went to salt. Gadgetzan died of thirst with a well in the middle of it.
The floor of the Abyssal Sands fell in. At every one of them somebody said it was a local problem
with a local cause, and at the top of this map is the thing that has been drinking since the
Integration.

    THE DROWNED STAIR   where the shaft lets out. Wet, and already wrong.
    THE CHOIR           the seam in exact repeating lattice, and it is making a noise. [Resonance]
    THE SIPHON WORKS    where the water is moved, which is the first proof it IS moved. [The Siphon]
    THE STANDING WATER  water held upright by lattice, which water does not do. [The Standing Wave]
    THE CISTERN         the heart.                                              [The Thirst]
    THE OUTFLOW         the way home, and the way the water goes.

DEEPER MEANS MORE, NOT BIGGER. Four bosses here against three above, and the roster loses the last
goblin on the way in - by the Cistern there is nothing left down here that was ever anybody.

DUNGEON, not cave: fixed spawns, hand-authored packs, on world/zone_classification.DUNGEONS so it
carries no gathering.

HARD CONTRACT (world/portal_manager.py):
    (46, 122) <-> The Mother Vein (46, 10)     the shaft down
    (60,   7) <-> Glittervein (82, 101)        the outflow, out beside the camp
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401
from tools import seam_kit

BAKED = "assets/tiles/cistern/baked"
UDP = "assets/tiles/underdark/props/"
SFP = "assets/tiles/shimmering_flats/props/"
W, H = 120, 130
ENTRANCE = (46, 122)        # down from The Mother Vein
OUTFLOW = (60, 7)           # up and out, to the isle at Lastwater

NODES = [
    (46, 118),      # 0 - the drowned stair, where the shaft lets out
    (66,  96),      # 1 - the choir
    (44,  72),      # 2 - the siphon works
    (64,  48),      # 3 - the standing water
    (60,  18),      # 4 - the cistern
]

#: (node index, rx, ry). The cistern is the only big room on either map, and it has earned it.
VUGS = [
    (0, 12,  8),
    (1, 10,  7),
    (2, 11,  7),
    (3, 10,  7),
    (4, 22, 10),
]

BOWS = [
    (-15, 18),
    (-20, 12),
    (-14, 21),
    (-18, 15),
]

GALLERY_W = 3

BOSSES = {}
CHESTS = []
GROUPS = []
TRASH = []

WEAVE, HOUND = "Glass Weaver", "Lattice Hound"
BRINE = "Brinewrought Hulk"
SINGER, LURKER = "Seam Singer", "Cistern Lurker"

#: Three to four groups between each boss (Kyle). Every centre is a node or a gallery waypoint from
#: gallery_paths(), never a coordinate picked by eye - a centre that lands just inside a wall finds
#: a walkable tile six away and quietly stacks a pull somewhere nobody fights.
PACKS = [
    # --- the Drowned Stair and the first segment, before Resonance (4)
    (46, 114, [(WEAVE, 50), (HOUND, 50), (BRINE, 50)]),
    (31, 111, [(HOUND, 50), (WEAVE, 50), (SINGER, 50)]),
    (64, 111, [(WEAVE, 50), (SINGER, 50), (HOUND, 50), (WEAVE, 50)]),
    (51, 104, [(SINGER, 50), (BRINE, 50), (HOUND, 50)]),
    # --- the Choir into the Siphon Works, before The Siphon (4)
    (46,  88, [(SINGER, 51), (SINGER, 51), (WEAVE, 50)]),
    (78,  88, [(BRINE, 51), (HOUND, 51), (SINGER, 50)]),
    (24,  80, [(HOUND, 51), (WEAVE, 51), (SINGER, 51)]),
    (56,  80, [(BRINE, 51), (SINGER, 51), (HOUND, 51), (WEAVE, 51)]),
    # --- the Standing Water, before The Standing Wave (4). The lurkers start here.
    (30,  64, [(LURKER, 51), (BRINE, 51), (WEAVE, 51)]),
    (65,  64, [(LURKER, 51), (LURKER, 51), (HOUND, 51)]),
    (50,  56, [(BRINE, 51), (SINGER, 51), (LURKER, 51)]),
    (85,  56, [(LURKER, 51), (HOUND, 51), (BRINE, 52)]),
    # --- the long throat into the Cistern, before The Thirst (4)
    (46,  38, [(LURKER, 52), (BRINE, 52), (SINGER, 52)]),
    (79,  38, [(LURKER, 52), (LURKER, 52), (BRINE, 52)]),
    (42,  28, [(BRINE, 52), (SINGER, 52), (LURKER, 52)]),
    (75,  28, [(LURKER, 52), (BRINE, 52)]),
]


def gallery_paths():
    """The pairs of galleries. tools/seam_kit.py owns the shape."""
    return seam_kit.bow_paths(NODES, BOWS)


def _near_walkable(zone, x, y, rad=8):
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            if zone.is_walkable(int(x) + dx, int(y) + dy):
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, int(x) + dx, int(y) + dy)
    return None if best is None else (best[1], best[2])


def build_cistern(omit=()):
    zone = Tilemap("The Cistern", W, H,
                   "Where the water has been going for three years, and the thing that has been "
                   "taking it.")
    zone.is_cave = True
    # THE PARENT ZONE, NOT THE GEOGRAPHIC REGION. zone_manager.trigger_encounter looks a cave or
    # dungeon's encounter table up under `region` as a ZONE NAME
    # (encounters["zones"][region]["caves"][map name]), so "Kalimdor - Tanaris" - which is what the
    # open zones carry and what this said first - matches nothing and the map spawns nothing.
    zone.region = "Glittervein"
    zone.fixed_spawns = True
    L = CaveLayout(zone, (ENTRANCE[0], ENTRANCE[1] - 2))
    b = L.b

    b.lobes([(NODES[i][0], NODES[i][1], rx, ry) for (i, rx, ry) in VUGS])

    # `omit` is how tools/verify_mother_vein.py severs a gallery: it rebuilds this map without
    # carving that one, so the test measures THIS map rather than a reconstruction of it.
    for (_i, _bow, pts) in gallery_paths():
        if (_i, _bow) in omit:
            continue
        b.corridor(pts, width=GALLERY_W)

    # THE OUTFLOW. Up out of the cistern and off the top of the map - the channel the water takes
    # to the pool, and the way the party gets home.
    # Run it past the portal in both directions. A portal needs walkable ground on the ARRIVAL
    # tile as well as its own, and the arrival tile is the one nothing in the data writes down -
    # with the mouth at the very end of the channel the engine had to snap the landing a tile.
    b.corridor([(60, 14), (60, 3)], width=4)

    # Standing water: the stair is wet, and the cistern is most of the way to being a lake. The
    # island is what The Thirst stands on, so it is not optional.
    b.water([(46, 118, 9, 4), (60, 18, 17, 7)], island=[(60, 18, 6, 4)])

    for (px, py) in (ENTRANCE, OUTFLOW):
        zone.collision_layer[py][px] = None
        zone.set_tile(px, py, "dirt", "base")
        if py + 1 < H:
            zone.collision_layer[py + 1][px] = None
        if py - 1 >= 0:
            zone.collision_layer[py - 1][px] = None
        L.mark("portal", px, py)

    bosses = [(66, 96, "Resonance"),
              (44, 72, "The Siphon"),
              (64, 48, "The Standing Wave"),
              (60, 18, "The Thirst")]
    fixed = []
    for (x, y, n) in bosses:
        p = _near_walkable(zone, x, y)
        assert p, (n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    zone.boss_position = (fixed[0][0], fixed[0][1])
    zone.boss_positions = list(fixed)

    # A test build is geometry only - the packs standing on a severed gallery have nowhere to be,
    # and a test build must not overwrite the real map's module-level BOSSES/CHESTS/TRASH.
    if omit:
        zone.trash_packs, zone.trash_spawns = [], []
        return zone, L

    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})

    chests = []
    for (x, y) in ((84, 104), (24, 80), (85, 56), (42, 28)):
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        chests.append(p)
    CHESTS[:] = chests
    for c in chests:
        L.mark("chest", *c)

    TRASH.clear()
    GROUPS.clear()
    occupied = [(x, y) for (x, y) in BOSSES.values()] + [tuple(c) for c in CHESTS] \
        + [ENTRANCE, OUTFLOW]
    for (cx, cy, members) in PACKS:
        group = []
        k = len(members)
        for i, (nm, lvl) in enumerate(members):
            ang = 0.4 + 2 * math.pi * i / k
            spot = _near_walkable(zone, cx + 2.4 * math.cos(ang), cy + 2.0 * math.sin(ang), rad=6)
            assert spot, (nm, cx, cy)
            if any(max(abs(spot[0] - o[0]), abs(spot[1] - o[1])) < 2 for o in occupied):
                alt = _near_walkable(zone, cx + 3.4 * math.cos(ang), cy + 2.8 * math.sin(ang), rad=6)
                if alt and all(max(abs(alt[0] - o[0]), abs(alt[1] - o[1])) >= 2 for o in occupied):
                    spot = alt
            occupied.append(spot)
            group.append((spot[0], spot[1], nm, lvl))
            TRASH.append((spot[0], spot[1], nm, lvl))
        GROUPS.append(group)
    zone.trash_packs = [list(g) for g in GROUPS]
    zone.trash_spawns = list(TRASH)

    zone.add_subzone("The Cistern", 0, 0, W, H)          # the encounter-table key covers the map
    zone.add_subzone("The Drowned Stair", 28, 106, 40, 24)
    zone.add_subzone("The Choir", 24, 84, 72, 22)
    zone.add_subzone("The Siphon Works", 20, 60, 76, 24)
    zone.add_subzone("The Standing Water", 24, 36, 72, 24)
    zone.add_subzone("The Outflow", 36, 2, 48, 34)
    return zone, L


def finish(zone, L):
    targets = [ENTRANCE, OUTFLOW] + [(x, y) for (x, y) in BOSSES.values()] + list(CHESTS) \
        + [(x, y) for (x, y, _n, _l) in TRASH]
    return L.finish(targets)


def dress(zone, L):
    P = L.prop
    U = dict(where=UDP)
    S = dict(where=SFP)
    # ---- the Drowned Stair: the last goblin tackle anybody got this far down
    P("ud_dig_scaffold", 38, 120, 7, **U)
    P("sf_hand_winch", 54, 120, 4, **S)
    P("ud_glow_pool", 46, 116, 3, **U)
    P("ud_stalagmites", 34, 112, 4, **U)
    # ---- the Choir: lattice in exact repeating geometry, and it is making a noise
    P("ud_lattice_growth", 60, 96, 6, **U)
    P("ud_lattice_growth", 72, 96, 6, **U)
    P("ud_crystal_spire", 62, 91, 9, **U)
    P("ud_crystal_spire", 70, 91, 9, **U)
    P("ud_rune_stone", 31, 111, 4, **U)
    P("ud_arcane_brazier", 64, 111, 4, **U)
    # ---- the Siphon Works: where the water is moved
    P("sf_condenser", 38, 72, 5, **S)
    P("sf_condenser", 50, 72, 5, **S)
    P("ud_glow_pool", 44, 68, 3, **U)
    P("ud_crystal_float", 44, 77, 6, **U)
    P("ud_masonry_rubble", 24, 80, 4, **U)
    P("ud_masonry_rubble", 78, 88, 4, **U)
    # ---- the Standing Water: water held upright, which water does not do
    P("ud_crystal_float", 58, 48, 7, **U)
    P("ud_crystal_float", 70, 48, 7, **U)
    P("ud_floating_stone", 64, 43, 6, **U)
    P("ud_geode_open", 30, 64, 5, **U)
    P("ud_geode_open", 85, 56, 5, **U)
    P("ud_lattice_growth", 50, 56, 5, **U)
    # ---- the Cistern and the Outflow: the water, and the way home
    P("ud_crystal_spire", 42, 18, 11, **U)
    P("ud_crystal_spire", 78, 18, 11, **U)
    P("ud_crystal_float", 50, 11, 7, **U)
    P("ud_crystal_float", 70, 11, 7, **U)
    P("ud_lattice_growth", 60, 26, 6, **U)
    P("ud_moss_curtain", 56, 5, 5, **U)
    P("ud_moss_curtain", 64, 5, 5, **U)
    return zone, L


def generate_cistern():
    zone, L = build_cistern()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_cistern_baked():
    """(zone, layout) with props + QA done - what the baker paints from."""
    zone, L = build_cistern()
    dress(zone, L)
    finish(zone, L)
    return zone, L
