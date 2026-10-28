"""
Hand-built The Weeping Ice (96x132): a dying glacier's plumbing, inside the Aspen Wilderness. Levels 29-31.

ARCHETYPE: THE BRAIDED CONDUIT.

A cave in rock is carved by one river and comes out as rooms on a corridor. A cave in ICE is carved by
MELTWATER, which does not behave like a river at all - it splits around every hard mass it meets and
rejoins below it, over and over, all the way down. The result is not rooms-and-corridors. It is one
descending passage that keeps dividing into strands and knitting back together, and the "rooms" are only
the places where several strands happen to meet at once.

Nothing else in the game is shaped like that. The Hollow Geode closes inward in concentric shells, the
Broodspiral spirals, Dun Garok is a line of gates, Durnholde a wall around a courtyard, the Deep Bloom a
library that repeats itself. This one BRAIDS DOWNWARD, and it means there is never a single correct route
and never a dead corridor either - every strand goes somewhere, most of them go to the same place, and a
player who takes the left fork twice has still descended.

    THE MOULIN        the way in. A shaft where meltwater pours in from the snowfield above, and the one
                      place in here with daylight in it.
    THE UPPER BRAID   three strands around two ice masses. Widest part of the cave and still not open.
    THE CISTERN       where the three strands pool. Standing water that never drains fast enough.
    THE LOWER BRAID   two strands, tighter, because there is less water down here to keep them open.
    THE SINK          the bottom. Where the water goes and does not come back.

THE LORE IS THE ZONE'S LORE, UNDERGROUND. The Aspen Wilderness is a piece of the Rockies dropped onto
Kalimdor by the Integration. This is the piece of GLACIER that came with it - ice that has no business
existing at this latitude, melting out a little more every year. The cave gets BIGGER annually, which is
why nothing in here is old and settled.

And the yetis came across inside it. They are not native to Thousand Needles and they never will be; they
are refugees of the same accident as the mountain, and their home is draining away under them. The bears
are local - they denned here when it was just a cave, and they are sharing it with something that arrived
from another world and is in a worse mood than they are.

CAVE, not dungeon (Kyle 2026-10-22: "Hand placed mobs are only in full dungeons!"): random trash from the
cave encounter table, one pinned boss and two named rares, short main path, side strands optional.

HARD CONTRACT (world/portal_manager.py): portal (48, 126) <-> The Aspen Wilderness (76, 63).
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401
from tools.handbuilt_vot_caves import _apply_pools

BAKED = "assets/tiles/weeping_ice/baked"
UDP = "assets/tiles/underdark/props/"
W, H = 96, 132
PORTAL = (48, 126)

#: THE MOULIN. The shaft the meltwater comes down, and the way in.
MOULIN = (48, 114, 15, 13)

#: THE UPPER BRAID. Three strands around two ice masses. They are NOT equal - the centre strand is the
#: obvious one and the shortest, the west strand is the longest and passes the bear den, the east strand
#: is a squeeze that most players will only find on the way back. Equal strands would make the braid a
#: decision with no content in it.
UPPER = {
    "up_west":   (18, 92, 11, 15),
    "up_centre": (48, 94, 12, 12),
    "up_east":   (76, 90, 9, 13),
    "up_knot":   (48, 74, 16, 9),      # where the three come back together
}

#: THE CISTERN. Standing meltwater. The only generous space in the cave, and it is generous because it is
#: half pool - the walkable margin around it is no wider than anything else.
CISTERN = (48, 58, 24, 13)

#: THE LOWER BRAID. Two strands, tighter than the upper three. Less water gets this far.
LOWER = {
    "lo_west": (28, 40, 10, 13),
    "lo_east": (68, 40, 10, 13),
    "lo_knot": (48, 24, 14, 9),
}

#: THE SINK. The bottom of the system.
SINK = (48, 11, 20, 11)

#: CREVASSE POCKETS. Blind side-pockets off the strands, which is where the chests are. In a glacier these
#: are where meltwater found a crack, filled it, and then the route moved on and left it.
POCKETS = {
    "pocket_a": (8, 76, 7, 6),
    "pocket_b": (88, 70, 6, 6),
    "pocket_c": (14, 22, 7, 6),
    "pocket_d": (82, 20, 7, 6),
}

#: (points, width). corridor(width=N) clears roughly 2N+1 tiles. Width 1 is a genuine squeeze; the braid
#: uses 1 almost everywhere, because a meltwater conduit is the size the water needed and no larger.
STRANDS = [
    # moulin -> the three upper strands
    ([(44, 110), (32, 104), (24, 98)], 1),
    ([(48, 108), (48, 100)], 2),                    # the obvious one, and the widest thing here
    ([(53, 110), (68, 104), (78, 96)], 1),
    # the three upper strands -> the knot
    ([(20, 86), (30, 80), (42, 76)], 1),
    ([(48, 88), (48, 79)], 1),
    ([(78, 84), (66, 79), (55, 76)], 1),
    # knot -> cistern
    ([(44, 70), (44, 64)], 1),
    ([(53, 70), (53, 64)], 1),                      # two ways down into the cistern, not one
    # cistern -> the two lower strands
    ([(38, 54), (32, 48), (29, 46)], 1),
    ([(58, 54), (64, 48), (67, 46)], 1),
    # lower strands -> lower knot
    ([(29, 34), (38, 28), (44, 25)], 1),
    ([(67, 34), (58, 28), (53, 25)], 1),
    # a cross-link between the two lower strands. Without it each is a spur off the cistern and the braid
    # stops braiding exactly where it should be tightest.
    ([(36, 40), (48, 38), (60, 40)], 1),
    # lower knot -> the sink
    ([(48, 20), (48, 16)], 1),
    # the crevasse pockets
    ([(17, 92), (12, 84), (10, 79)], 1),
    ([(84, 88), (88, 78), (88, 73)], 1),
    ([(26, 42), (19, 32), (16, 25)], 1),
    ([(72, 42), (79, 30), (82, 23)], 1),
]

#: THE CISTERN'S WATER. (cx, cy, rx, ry, phase). Shallow only - this is standing meltwater a few inches
#: deep that never drains fast enough, not a lake, and a player should wade it rather than swim it.
#: Declared HERE and shared with the baker (tools/bake_weeping_ice.py passes this exact list), because a
#: pool painted in the bake but absent from the tilemap is water you cannot see yourself standing in.
WI_POOLS = [(48, 58, 8.5, 4.0, 0.7)]

BOSSES = {}
CHESTS = []


def _near_walkable(zone, x, y, rad=8):
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            if zone.is_walkable(int(x) + dx, int(y) + dy):
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, int(x) + dx, int(y) + dy)
    return None if best is None else (best[1], best[2])


def build_weeping_ice():
    zone = Tilemap("The Weeping Ice", W, H,
                   "A piece of glacier that came across with the mountains and has been melting ever "
                   "since. Its meltwater carved the passages, and they get wider every year.")
    zone.is_cave = True
    #: .region declares the PARENT ZONE (world/zone_manager.py:55) - the encounter lookup keys off it.
    zone.region = "The Aspen Wilderness"
    zone.fixed_spawns = False
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b

    b.lobes([MOULIN] + list(UPPER.values()) + [CISTERN] + list(LOWER.values()) + [SINK]
            + list(POCKETS.values()))
    for pts, w in STRANDS:
        b.corridor(pts, width=w)

    # the way in, down the moulin shaft
    b.corridor([(48, 130), (48, 124), (48, 120)], width=1)

    # ICE MASSES STANDING IN THE PASSAGES. These are what the water split AROUND, so they are the reason
    # the braid exists at all - without them the strands have nothing to be strands on either side of, and
    # the upper braid reads as one wide room with pillars in it rather than three routes.
    b.pillars([34, 62], [96, 108], size=3)          # the two masses the upper braid divides around
    b.pillars([40, 56], [76, 92], size=2)
    b.pillars([42, 54], [40, 52], size=2)           # and the one the lower braid divides around
    b.pillars([44, 52], [60, 66], size=2)           # islands in the cistern

    _apply_pools(zone, WI_POOLS, shallow_only=True)

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.set_tile(px, py, "dirt", "base")
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    # ONE BOSS, TWO NAMED RARES - a cave, not a dungeon. Rimehowl sits at the Sink because the bottom of
    # the system is the last place in here that is still properly frozen, and he is the reason the bears
    # stay upstairs. Snowmaw dens off the long west strand; the Last Drift is in a crevasse pocket that
    # most players will never open.
    bosses = [(48, 11, "Rimehowl"),
              (20, 94, "Snowmaw"),
              (88, 70, "The Last Drift")]
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
    for (x, y) in ((8, 76), (14, 22), (82, 20), (48, 58)):
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        chests.append(p)
    CHESTS[:] = chests
    for c in chests:
        L.mark("chest", *c)

    zone.add_subzone("The Weeping Ice", 0, 0, W, H)       # the encounter-table key covers the whole map
    zone.add_subzone("The Moulin", 38, 106, 22, 24)
    zone.add_subzone("The Upper Braid", 8, 66, 82, 44)
    zone.add_subzone("The Cistern", 32, 50, 34, 20)
    zone.add_subzone("The Lower Braid", 18, 18, 62, 34)
    zone.add_subzone("The Sink", 36, 4, 26, 16)
    return zone, L


def finish(zone, L):
    targets = [PORTAL] + [(x, y) for (x, y) in BOSSES.values()] + list(CHESTS)
    return L.finish(targets)


def dress(zone, L):
    P = L.prop
    U = dict(where=UDP)
    # ---- THE MOULIN: the shaft, and the only daylight in the cave
    P("ud_ice_stalagmites", 42, 120, 8, **U)
    P("ud_ice_stalagmites", 55, 120, 7, **U)
    P("ud_frozen_crate", 53, 116, 3, near_ok=True, **U)
    P("ud_stalagmites", 45, 112, 5, **U)

    # ---- THE UPPER BRAID: the masses the water split around, seen from the passages beside them
    P("ud_ice_stalagmites", 30, 100, 9, **U)
    P("ud_ice_stalagmites", 22, 90, 5, **U)
    P("ud_stalagmites", 16, 96, 4, **U)
    P("ud_stalagmites", 58, 102, 9, **U)
    P("ud_ice_stalagmites", 50, 92, 5, **U)
    P("ud_stalagmites", 80, 94, 4, **U)
    P("ud_ice_stalagmites", 82, 86, 5, **U)
    P("ud_stalagmites", 44, 76, 4, **U)

    # ---- THE CISTERN: standing water, and what is frozen into the edges of it
    P("ud_stalagmites", 36, 62, 5, **U)
    P("ud_stalagmites", 62, 62, 5, **U)
    P("ud_stalagmites", 48, 52, 6, **U)
    P("ud_ice_stalagmites", 40, 56, 7, **U)

    # ---- THE LOWER BRAID: tighter, colder, less of it melted out
    P("ud_ice_stalagmites", 26, 44, 8, **U)
    P("ud_stalagmites", 32, 34, 5, **U)
    P("ud_ice_stalagmites", 70, 44, 8, **U)
    P("ud_ice_stalagmites", 64, 34, 5, **U)
    P("ud_stalagmites", 48, 36, 4, **U)

    # ---- THE SINK: still properly frozen, which is the whole reason anything lives down here
    P("ud_stalagmites", 40, 14, 10, **U)
    P("ud_ice_stalagmites", 57, 14, 10, **U)
    P("ud_ice_stalagmites", 48, 7, 7, **U)
    P("ud_frozen_crate", 44, 18, 3, near_ok=True, **U)

    # ---- the crevasse pockets: somebody or something got in here before you
    P("ud_frozen_crate", 9, 74, 3, near_ok=True, **U)
    P("ud_masonry_rubble", 87, 68, 3, near_ok=True, **U)
    P("ud_frozen_crate", 15, 20, 3, near_ok=True, **U)
    P("ud_masonry_rubble", 81, 18, 3, near_ok=True, **U)
    return zone, L


def generate_weeping_ice():
    zone, L = build_weeping_ice()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_weeping_ice_baked():
    """(zone, layout) with props + QA done - what the baker paints from."""
    zone, L = build_weeping_ice()
    dress(zone, L)
    finish(zone, L)
    return zone, L
