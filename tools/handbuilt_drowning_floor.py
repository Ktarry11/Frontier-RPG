"""
Hand-built The Drowning Floor (132x112): the cave under the mesas where the year's flood goes.
Levels 33-35.

ARCHETYPE: THE PILLARED HALL NOBODY BUILT.

Every cave in this game so far is a space you move ALONG - the Weeping Ice braids, the Hollow Geode
closes inward in shells, the Broodspiral spirals, Dun Garok is a line of gates. This one is a space you
move ACROSS, and the difference is the landform.

A mesa is layered rock. Water does not bore a tube through layered rock; it dissolves out one soft bed
between two hard ones and leaves a single enormous cavity that is WIDE AND LOW - a few feet of headroom
over acres of floor - held up by whatever columns of the soft layer happened not to go. So the cave is
one room the size of the mesa above it, and you navigate it by PILLARS, not by corridors.

That would be an empty hall, which the standing rule forbids ("no massive open trash" - even an enormous
cave wants carved sections). It is not empty, because roofs fall in. COLLAPSE RIDGES of breakdown divide
the floor into bays, and the gaps between the fallen blocks are the only ways from one bay to the next.
Structure without a single corridor.

    THE SOAK          the way in. A hole at the foot of a mesa that swallows a wash and gives nothing back.
    THE OUTER BAYS    three of them round the rim of the hall, lowest ceiling, most pillars.
    THE DROWNED AISLE the long bay through the middle, where the flood runs hardest and the pillars have
                      been cut to stumps by three years of it.
    THE SUMP          the lowest point, and the only water that is here all year. Everything else in this
                      cave is dry for eleven months and then is not.

THE WHOLE PLACE DROWNS ONCE A YEAR, and that is the idea the zone above already set up: Thousand Needles
floods once, hard, and then is dry for a year. tools/handbuilt_southern_needles.WASHES are the channels
that water cut on the surface. This is where it goes. There is a high-water mark on every pillar in here,
well above your head, and nothing living in this cave is surprised by it.

CAVE, not dungeon (claude/dungeon_authoring_rules.md): random trash from its own table, one pinned boss
and two named rares, short main path, the far bays optional.

HARD CONTRACT (world/portal_manager.py): portal (66, 104) <-> Southern Thousand Needles (104, 112).
"""
import os

import numpy as np

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, _apply_pools, register_baked  # noqa: F401

BAKED = "assets/tiles/drowning_floor/baked"
SNP = "assets/tiles/southern_needles/props/"
UDP = "assets/tiles/underdark/props/"
W, H = 132, 112
PORTAL = (66, 104)

#: THE BAYS. Wide and shallow, because the cavity is a bedding plane and a bedding plane has no depth.
#: Deliberately unequal: the aisle is the obvious route and the outer bays are where you go if you want
#: something.
#: NOTHING HERE MIRRORS ANYTHING ELSE, and that is deliberate rather than fussy. The first cut of this map
#: had the west and east bays at matching offsets off a centred aisle, and the bake came out a Rorschach
#: blot - a butterfly, not a cave. A dissolved bedding plane is the record of where the water happened to
#: run, and water is not symmetrical about anything. So: the aisle leans, the west side is one big deep bay
#: and the east side is two small high ones, and the sump hangs off the west like a dead end that fills.
BAYS = {
    "soak":       (62, 94, 13, 9),       # the hole you come in by
    "aisle_s":    (72, 73, 33, 11),      # the Drowned Aisle, south half - running NW, not straight up
    "aisle_n":    (60, 47, 27, 14),      # and north half, swung back west
    "west_bay":   (24, 67, 17, 21),      # the big one. Deepest, most pillars, furthest from the flood
    "west_spur":  (15, 43, 10, 10),      # a dead end off it
    "east_bay":   (107, 57, 12, 15),     # east side is smaller and sits higher
    "north_bay":  (74, 21, 25, 9),
    "sump":       (32, 30, 15, 12),      # the lowest point, and the only year-round water
    "far_east":   (108, 27, 11, 9),
    "south_shelf": (95, 88, 12, 8),      # a shelf off the soak nobody needs to visit
}

#: (points, width). These are not corridors - they are the GAPS BETWEEN FALLEN BLOCKS, which is why they
#: are short and wide rather than long and narrow. corridor(width=N) clears about 2N+1 tiles.
GAPS = [
    ([(64, 86), (68, 80)], 3),                       # soak -> aisle
    ([(66, 62), (62, 56)], 3),                       # aisle south -> north, and it kinks
    ([(46, 70), (38, 67)], 2),                       # aisle -> west bay
    ([(90, 66), (99, 60)], 2),                       # aisle -> east bay
    ([(64, 36), (70, 27)], 2),                       # aisle -> north bay
    ([(24, 54), (18, 48)], 2),                       # west bay -> the spur
    ([(16, 36), (26, 32)], 2),                       # the spur -> the sump
    ([(54, 24), (44, 29)], 2),                       # north bay -> the sump, the long way round
    ([(110, 48), (109, 34)], 2),                     # east bay -> far east
    ([(88, 20), (101, 25)], 2),                      # north bay -> far east
    ([(72, 92), (88, 89)], 2),                       # soak -> the south shelf
]

#: THE SUMP'S WATER. (cx, cy, rx, ry, phase). Shallow only - this is the last of last year's flood, not a
#: lake, and a player should wade it. Declared HERE and handed to the baker, because a pool painted in the
#: bake but absent from the tilemap is water you cannot see yourself standing in.
DF_POOLS = [(32, 30, 8.5, 6.0, 0.6), (70, 75, 5.5, 3.0, 1.9)]

BOSSES = {}
CHESTS = []


def _near_walkable(zone, x, y, rad=9):
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            if zone.is_walkable(int(x) + dx, int(y) + dy):
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, int(x) + dx, int(y) + dy)
    return None if best is None else (best[1], best[2])


def build_drowning_floor():
    zone = Tilemap("The Drowning Floor", W, H,
                   "A bedding plane under the mesas, hollowed out by water and held up by what the water "
                   "did not take. It fills to the roof once a year.")
    zone.is_cave = True
    #: .region declares the PARENT ZONE (world/zone_manager.py:55) - the encounter lookup keys off it.
    zone.region = "Southern Thousand Needles"
    zone.fixed_spawns = False
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b

    b.lobes(list(BAYS.values()))
    for pts, w in GAPS:
        b.corridor(pts, width=w)
    # the soak-away itself, down from the surface
    b.corridor([(66, 110), (66, 103), (63, 97)], width=1)

    # THE PILLARS ARE THE POINT. Columns of the soft bed that happened not to dissolve, holding up the
    # roof. Dense in the outer bays where the flood runs slowest; cut back to stumps down the aisle, where
    # three years of annual flood has been working on them.
    # A GRID OF EQUAL PILLARS READS AS POCKMARKS, not as columns - the first bake made that very plain.
    # Breakdown does not sort itself by size: a bedding plane leaves a few fat columns that the water went
    # round and a lot of thin ones it very nearly took, scattered with no spacing worth the name. So these
    # are short irregular calls at three different sizes rather than one tidy cross-product per bay.
    b.pillars([19, 30], [60, 73], size=3)                      # west bay: the fat ones that held
    b.pillars([24, 33], [66], size=2)
    b.pillars([17, 26, 34], [55, 78], size=1)
    b.pillars([13, 19], [41, 47], size=2)                      # the spur
    b.pillars([104, 112], [54, 66], size=3)                    # east bay: fewer, fatter
    b.pillars([108], [60], size=1)
    # THE AISLE IS STUMPS. Three years of annual flood has been working on them and it shows.
    b.pillars([58, 69, 80, 88], [70, 78], size=1)
    b.pillars([52, 63, 72], [44, 52], size=1)
    b.pillars([66, 84], [48], size=2)                          # two the water has not got to yet
    b.pillars([68, 80, 90], [19, 24], size=2)                  # north bay
    b.pillars([76], [22], size=3)
    b.pillars([105, 113], [25, 30], size=2)                    # far east
    b.pillars([29, 38], [27, 34], size=1)                      # the sump, mostly eaten
    b.pillars([92, 100], [87, 91], size=1)                     # the south shelf

    _apply_pools(zone, DF_POOLS, shallow_only=True)

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.set_tile(px, py, "dirt", "base")
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    # ONE BOSS, TWO NAMED RARES - a cave, not a dungeon. The boss is in the Sump because the Sump is the
    # only water that is here all year, and the only thing in this cave that never has to leave.
    bosses = [(32, 30, "Yearmaw"),
              (108, 59, "The Leavings"),
              (76, 21, "Old Saltbed")]
    fixed = []
    for (x, y, n) in bosses:
        p = _near_walkable(zone, x, y)
        assert p, (n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (fixed[0][0], fixed[0][1])
    zone.boss_positions = list(fixed)

    chests = []
    for (x, y) in ((24, 70), (108, 27), (82, 19), (38, 34), (15, 43)):
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        chests.append(p)
    CHESTS[:] = chests
    for c in chests:
        L.mark("chest", *c)

    zone.add_subzone("The Drowning Floor", 0, 0, W, H)   # the encounter-table key covers the whole map
    zone.add_subzone("The Soak", 48, 80, 58, 30)
    zone.add_subzone("The Drowned Aisle", 42, 36, 56, 48)
    zone.add_subzone("The Sump", 6, 18, 42, 40)
    zone.add_subzone("The Far Bays", 96, 16, 34, 62)
    return zone, L


def finish(zone, L):
    targets = [PORTAL] + [(x, y) for (x, y) in BOSSES.values()] + list(CHESTS)
    return L.finish(targets)


def dress(zone, L):
    P = L.prop
    S = dict(where=SNP)
    U = dict(where=UDP)
    # ---- THE SOAK: what the last flood carried in and left at the top of the hole
    P("sn_driftwood_salt", 58, 96, 3, near_ok=True, **S)
    P("sn_rib_bones", 66, 95, 3, near_ok=True, **S)
    P("sn_stone_pile", 57, 91, 4, **S)

    # ---- THE DROWNED AISLE: stumps, and the wrack line the water leaves every year
    P("sn_layered_stack", 58, 75, 5, **S)
    P("sn_layered_stack", 85, 72, 5, **S)
    P("sn_driftwood_salt", 76, 70, 3, near_ok=True, **S)
    P("sn_split_stone", 55, 49, 5, **S)
    P("sn_split_stone", 70, 44, 5, **S)
    P("sn_kodo_skull", 64, 58, 3, near_ok=True, **S)

    # ---- THE OUTER BAYS: densest pillars, least disturbed, so this is where things are still whole
    P("sn_rock_spire", 22, 59, 7, **S)
    P("sn_boulder_red", 30, 76, 4, **S)
    P("sn_clay_vessel", 27, 70, 2, near_ok=True, **S)
    P("sn_rock_spire", 110, 52, 7, **S)
    P("sn_boulder_red", 104, 65, 4, **S)
    P("sn_rib_bones", 110, 63, 3, near_ok=True, **S)

    # ---- THE NORTH BAY AND THE FAR EAST
    P("sn_layered_stack", 65, 24, 5, **S)
    P("sn_cairn", 84, 22, 4, **S)
    P("sn_boulder_red", 110, 22, 4, **S)
    P("sn_driftwood_salt", 112, 30, 3, near_ok=True, **S)

    # ---- THE SUMP: standing water that has been standing a long time
    P("sn_rock_spire", 24, 25, 7, **S)
    P("ud_frozen_crate", 40, 33, 3, near_ok=True, **U)
    P("sn_rib_bones", 28, 35, 3, near_ok=True, **S)
    P("sn_boulder_red", 21, 49, 4, **S)          # the spur
    P("sn_clay_vessel", 94, 89, 2, near_ok=True, **S)   # the south shelf
    return zone, L


def generate_drowning_floor():
    zone, L = build_drowning_floor()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_drowning_floor_baked():
    """(zone, layout) with props + QA done - what the baker paints from."""
    zone, L = build_drowning_floor()
    dress(zone, L)
    finish(zone, L)
    return zone, L
