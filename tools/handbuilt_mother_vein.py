"""
Hand-built The Mother Vein (120x150): the Glittervein's dungeon. Levels 48-51, five bosses.

ARCHETYPE: THE SEAM. The player walks INSIDE the ore shoot.

TWO MAPS, AND THE SECOND ONE IS HOW YOU GET OUT. Kyle: "basically means you enter, go through some
bosses, at the other end is another way further down into the dungeon into another map with more
bosses. at the very end (after the last boss) brings you back out to Lastwater." So this map is the
upper half - three bosses and a shaft at the far end - and tools/handbuilt_cistern.py is the lower
half. The way out of the lower half is THE OUTFLOW: the channel the water itself takes to reach the
pool, which is why following it surfaces at Lastwater. The exit is the answer to the question the
whole five-zone chain has been asking.

Every interior Frontier has built is a shape a person or a creature would make: a gauntlet of
gates, a broken ring, drowned workings, switchback terraces, a spiral, stacked octagons, a throne
ascent, a warren that trends down, a roofed country, a stack of shelves, a closing bubble, a
library grown wrong. This one is a shape ROCK makes. A vein is not a corridor system and it is not
a warren - it is a sheet of mineral filling a fracture, and the fractures it fills do a thing
neither of those does.

THEY BRANCH AND THEY REJOIN. A warren branches and dead-ends; a corridor does not branch at all. A
fracture network ANASTOMOSES - it splits around whatever would not break and comes back together on
the far side - so the seam is full of cycles and has almost no dead ends. That makes a navigational
feel nothing else in the game has: you cannot be permanently lost, because everything rejoins, and
you can also never see the whole of it, because nothing runs straight for more than a few tiles.

So the map is NARROW GALLERIES BETWEEN WIDE VUGS, and the galleries always come in pairs:

    THE DIG HEAD        the only part of this map a person cut. Square, timbered, exact rects -
                        and it is the only square thing here, which is what makes the rest read
                        as rock rather than as architecture.
    THE DROWNED GALLERY the works below the water table, where the dig stopped being a dig.
                                                                     [Pitboss Grebble Vask]
    THE SHOOT           the vein proper. Narrow, angular, doubled.             [The Sump]
    THE GLASS ROOMS     vugs - crystal-lined pockets where the seam swelled.   [Glassmaw]
    THE DOWNSHAFT       where the seam drops out from under the workings, and the goblins stopped.

AND THE PAYOFF IS A FIVE-ZONE PAYOFF. The Aspen melt came early; the Southern Needles went dry; the
Shimmering Flats went to salt; Gadgetzan died of thirst with a well in the middle of it; the floor
of the Abyssal Sands fell in. At every one of those somebody explained it as a local problem with a
local cause. It is one problem, it has been drinking since the Integration, and it is at the top of
this map.

DUNGEON, not cave: fixed spawns, hand-authored packs, and on world/zone_classification.DUNGEONS so
it carries no gathering. Trash is authored here rather than rolled, for the reason Durnholde
taught - a generic router hands bosses zero pulls when a layout is not a simple chain, and this
layout is the least chain-like one yet.

THE CLAIM IS MEASURED, NOT ASSERTED. tools/verify_mother_vein.py blocks each branch gallery in turn
and requires the heart to stay reachable through every one of them, and separately measures the
width of the galleries against the width of the vugs. A docstring that says "it branches and
rejoins" is worth nothing; a test that severs each branch is worth something.

HARD CONTRACT (world/portal_manager.py):
    (60, 104) <-> Glittervein (86, 100)        the way in
    (46,  10) <-> The Cistern (46, 122)        the way down
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401
from tools import seam_kit

BAKED = "assets/tiles/mother_vein/baked"
UDP = "assets/tiles/underdark/props/"
SFP = "assets/tiles/shimmering_flats/props/"
W, H = 120, 110
PORTAL = (60, 104)          # up and out, to the isle at Lastwater
DOWNSHAFT = (46, 10)        # down, into The Cistern

#: THE DIG HEAD. Exact rects, and the only exact rects on the map. Goblins cut this part, so it is
#: square and timbered, and the moment the player leaves it nothing is square again.
DIG = {
    "head":     (50,  90, 70, 106),       # the shaft foot, where the lift came down
    "drift_w":  (28,  95, 50, 101),       # two drifts chasing the seam sideways, abandoned
    "drift_e":  (70,  95, 92, 101),
}

#: THE VERTICAL BUDGET, which is the thing that actually has to be laid out and was twice patched
#: instead. The drowned gallery is a ROOM, fifteen tiles tall, and the cistern is a room twenty-two
#: tall; between them sit three vugs fourteen tall each. Every one of those has to clear its
#: neighbour by enough tiles that the galleries between them are the only way across - the first
#: build had the gallery room overlapping the first vug by two tiles, and those two tiles were a
#: door around the entire first segment. Clearances as built, top of one chamber to bottom of the
#: next: 11, 8, 6.

#: THE DROWNED GALLERY. Chamfered - it was cut, then it fell in. Half-building, half-rock, which is
#: the handover between the two halves of the map.
GALLERY = (34, 76, 86, 90, 6)

#: THE NODES. Where the seam swells into a vug. The galleries run BETWEEN these, in pairs.
#: x wanders deliberately: a fracture does not run down the middle of anything.
#:
#: SPACING IS THE WHOLE DESIGN AND THE FIRST ATTEMPT GOT IT WRONG. Eight nodes sixteen tiles apart
#: with vugs eight tiles tall meant consecutive vugs very nearly touched, so the chambers merged
#: into one continuous blob and the galleries between them carried nothing. The map still LOOKED
#: like a seam and the single-branch severing test still passed fourteen times out of fourteen -
#: because with the branches gone the player simply walked from vug to vug. It was the negative
#: control that caught it: blocking BOTH branches of a segment left the heart reachable every
#: time. Five nodes twenty-two apart with vugs seven tall leaves six clear tiles of gallery
#: between each pair of chambers, which is where the galleries become load-bearing.
NODES = [
    (60, 76),       # 0 - the top of the drowned gallery, where the natural seam takes over
    (54, 58),       # 1
    (68, 36),       # 2
    (46, 14),       # 3 - the downshaft chamber
]

#: (node index, rx, ry) - the vugs themselves. Wide, because they are the only wide places, and no
#: taller than seven or they eat the galleries either side of them. The downshaft chamber is larger
#: because it has to hold a hole in its floor and a fight around it.
VUGS = [
    (1, 10, 7),
    (2,  9, 7),
    (3, 13, 9),
]

#: The bow of each pair of galleries, left and right, between node i and node i+1. Asymmetric on
#: purpose - a matched pair of arcs reads as a ladder, and a ladder is a building.
BOWS = [
    (-17, 14),
    (-13, 19),
    (-20, 12),
]

#: Galleries are THREE wide. That number is the archetype. Everything else about this map follows
#: from the fact that the walking space is a crack.
GALLERY_W = 3

BOSSES = {}
CHESTS = []
GROUPS = []                      # packs as placed, mirrored onto zone.trash_packs
TRASH = []

SODDEN, CRAWL = "Sodden Digger", "Vein Crawler"
WEAVE, HOUND = "Glass Weaver", "Lattice Hound"
BRINE = "Brinewrought Hulk"

#: Three to four groups between each boss (Kyle), hand-authored. The roster changes as the player
#: goes up: goblins who did not come out near the bottom, then the things that grew in the seam,
#: and by the Cistern there is nothing left that was ever anybody.
#: EVERY CENTRE HERE IS A REAL POINT ON THE SEAM - a node, a gallery waypoint, or a room in the dig
#: head - and not a coordinate chosen by eye off the docstring. Four of the first eighteen were
#: nowhere near the map and the build asserted on the first of them, which is the good outcome; the
#: bad one is a pack centre that lands JUST inside a wall, finds a walkable tile six away, and
#: quietly stacks a pull somewhere nobody fights. gallery_paths() prints the anchors.
#: EVERY CENTRE HERE IS A REAL POINT ON THE SEAM - a node, a gallery waypoint, or a room in the dig
#: head - and not a coordinate chosen by eye off the docstring. Four of the first eighteen were
#: nowhere near the map and the build asserted on the first of them, which is the good outcome; the
#: bad one is a pack centre that lands JUST inside a wall, finds a walkable tile six away, and
#: quietly stacks a pull somewhere nobody fights. gallery_paths() prints the anchors.
PACKS = [
    # --- the Dig Head and the Drowned Gallery, before Pitboss Grebble Vask (4)
    (60, 100, [(SODDEN, 48), (SODDEN, 48), (CRAWL, 48)]),
    (38,  98, [(SODDEN, 48), (CRAWL, 48), (SODDEN, 48)]),
    (82,  98, [(SODDEN, 48), (SODDEN, 48), (CRAWL, 48), (CRAWL, 48)]),
    (60,  84, [(SODDEN, 48), (CRAWL, 49), (WEAVE, 48)]),
    # --- both galleries of the first segment, before The Sump (3)
    (43,  70, [(CRAWL, 49), (CRAWL, 49), (HOUND, 49)]),
    (74,  70, [(SODDEN, 49), (WEAVE, 49), (CRAWL, 49)]),
    (68,  64, [(CRAWL, 49), (WEAVE, 49), (SODDEN, 49)]),
    # --- the Shoot, before Glassmaw (4)
    (41,  51, [(CRAWL, 49), (WEAVE, 49), (HOUND, 49)]),
    (73,  51, [(WEAVE, 49), (HOUND, 49), (CRAWL, 49), (SODDEN, 49)]),
    (55,  44, [(HOUND, 50), (WEAVE, 50), (CRAWL, 50)]),
    (87,  44, [(WEAVE, 50), (HOUND, 50), (BRINE, 50)]),
    # --- the run to the downshaft. No boss after these: the fight at the end of this map is the
    # --- decision to go further down, and a gauntlet is the wrong way to ask that question (3)
    (48,  29, [(WEAVE, 50), (HOUND, 50), (BRINE, 50)]),
    (80,  29, [(HOUND, 50), (WEAVE, 50), (CRAWL, 50)]),
    (26,  22, [(BRINE, 50), (WEAVE, 50)]),
]


def gallery_paths():
    """The pairs of galleries. tools/seam_kit.py owns the shape; this just names the inputs, so
    the map, the other half of the dungeon and the verifier cannot drift apart."""
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


def build_mother_vein(omit=()):
    zone = Tilemap("The Mother Vein", W, H,
                   "A crack in the limestone that filled with crystal, and then with water, and "
                   "then with something that drinks it.")
    zone.is_cave = True
    zone.region = "Kalimdor - Tanaris"
    zone.fixed_spawns = True
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b

    # ---- the only square thing on the map
    for (x0, y0, x1, y1) in DIG.values():
        b.rect(x0, y0, x1, y1)
    gx0, gy0, gx1, gy1, gch = GALLERY
    b.rect(gx0, gy0, gx1, gy1, chamfer=gch)

    # ---- the vugs
    b.lobes([(NODES[i][0], NODES[i][1], rx, ry) for (i, rx, ry) in VUGS])

    # ---- the seam: every gallery doubled, so every one of them can be severed
    #
    # `omit` is how tools/verify_mother_vein.py severs one. It takes (segment, bow) keys and simply
    # does not carve those galleries, so the verifier tests THIS map with a gallery missing rather
    # than a reconstruction of which tiles the gallery probably occupies. The reconstruction was
    # the first approach and it was wrong in the usual way: a second implementation of
    # Builder.corridor that walked the same points to slightly different tiles, so the severing
    # left slivers of the real gallery open and every negative control passed through them.
    for (_i, _bow, pts) in gallery_paths():
        if (_i, _bow) in omit:
            continue
        b.corridor(pts, width=GALLERY_W)

    # ---- standing water. The drowned gallery and the cistern are the two places it has pooled.
    b.water([(60, 120, 20, 5), (60, 14, 15, 7)], island=[(60, 14, 6, 4)])

    for (px, py) in (PORTAL, DOWNSHAFT):
        zone.collision_layer[py][px] = None
        zone.set_tile(px, py, "dirt", "base")
        zone.collision_layer[py - 1][px] = None
        L.mark("portal", px, py)

    # EACH BOSS SITS AT THE FAR END OF ITS SECTION - the lowest y the player reaches in it. Placed
    # mid-section the packs straddle them, so a player meets half a boss's trash after killing it
    # and the three-to-four rule stops meaning anything.
    bosses = [(60, 82, "Pitboss Grebble Vask"),     # in the drowned gallery itself
              (54, 58, "The Sump"),                 # the vug where the pumps gave out
              (68, 36, "Glassmaw")]                 # the glass rooms
    fixed = []
    for (x, y, n) in bosses:
        p = _near_walkable(zone, x, y)
        assert p, (n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    zone.boss_position = (fixed[0][0], fixed[0][1])
    zone.boss_positions = list(fixed)

    # A TEST BUILD IS GEOMETRY ONLY. verify_mother_vein severs a gallery by rebuilding without it,
    # and the packs standing on that gallery then have nowhere to be - which asserted, and would
    # also have let a test build quietly overwrite the real map's module-level BOSSES/CHESTS/TRASH
    # if it had not. So a build with `omit` carves the rock, places nothing, and touches no global.
    if omit:
        zone.trash_packs, zone.trash_spawns = [], []
        return zone, L

    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})

    chests = []
    for (x, y) in ((32, 98), (88, 98), (74, 70), (87, 44)):
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        chests.append(p)
    CHESTS[:] = chests
    for c in chests:
        L.mark("chest", *c)

    # ---- hand-placed packs, rung around their centre
    TRASH.clear()
    GROUPS.clear()
    occupied = [(x, y) for (x, y) in BOSSES.values()] + [tuple(c) for c in CHESTS] + [PORTAL]
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
    # world/cave_spawns.py reads zone.trash_packs directly, so authoring the groups here makes the
    # map self-sufficient: it does NOT need tools/build_dungeon_pulls.py, whose job is regrouping
    # the older dungeons' flat solo-fight chains into packs.
    zone.trash_packs = [list(g) for g in GROUPS]
    zone.trash_spawns = list(TRASH)

    zone.add_subzone("The Mother Vein", 0, 0, W, H)       # the encounter-table key covers the map
    zone.add_subzone("The Dig Head", 26, 128, 68, 22)
    zone.add_subzone("The Drowned Gallery", 30, 114, 60, 18)
    zone.add_subzone("The Shoot", 24, 90, 72, 26)
    zone.add_subzone("The Glass Rooms", 20, 58, 76, 32)
    zone.add_subzone("The Choir", 20, 26, 76, 32)
    zone.add_subzone("The Cistern", 32, 2, 58, 26)
    return zone, L


def finish(zone, L):
    #: The trash goes in as targets too. L.mark() only treats portal/boss/chest tiles as critical,
    #: so a prop with a solid footprint can be placed on top of a mob and bury it inside a wall -
    #: which renders fine and spawns an unreachable pack.
    targets = [PORTAL, DOWNSHAFT] + [(x, y) for (x, y) in BOSSES.values()] + list(CHESTS) \
        + [(x, y) for (x, y, _n, _l) in TRASH]
    return L.finish(targets)


def dress(zone, L):
    P = L.prop
    U = dict(where=UDP)
    S = dict(where=SFP)
    # ---- the Dig Head: goblin work, and all of it stopped mid-shift
    P("ud_dig_scaffold", 60, 102, 7, **U)
    P("ud_frozen_crate", 54, 100, 3, **U)
    P("ud_frozen_crate", 66, 100, 3, **U)
    P("sf_hand_winch", 34, 98, 4, **S)
    P("sf_hand_winch", 86, 98, 4, **S)
    P("sf_fuel_drums", 44, 99, 3, **S)
    P("sf_scrap_heap", 76, 99, 3, **S)
    # ---- the Drowned Gallery: the pumps, and what they could not keep up with
    P("ud_dig_scaffold", 42, 88, 7, **U)
    P("sf_condenser", 76, 88, 5, **S)
    P("ud_glow_pool", 60, 84, 3, **U)
    P("ud_masonry_rubble", 46, 78, 4, **U)
    P("ud_masonry_rubble", 74, 78, 4, **U)
    # ---- the Shoot: the seam itself, and the first crystal worth the walk
    for (x, y) in ((54, 58), (68, 36)):
        P("ud_crystal_cyan", x - 6, y, 6, **U)
        P("ud_crystal_violet", x + 6, y, 6, **U)
    P("ud_lattice_growth", 54, 53, 5, **U)
    P("ud_stalagmites", 43, 70, 4, **U)
    P("ud_stalagmites", 73, 51, 4, **U)
    P("ud_lichen_boulder", 68, 41, 4, **U)
    # ---- the Glass Rooms: vugs, so the walls are the loot
    P("ud_crystal_spire", 62, 36, 9, **U)
    P("ud_crystal_spire", 74, 36, 9, **U)
    P("ud_geode_open", 68, 31, 5, **U)
    P("ud_geode_open", 87, 44, 5, **U)
    P("ud_crystal_float", 55, 44, 6, **U)
    # ---- the Downshaft: a hole in a floor, and goblin tackle abandoned round the lip of it
    P("ud_dig_scaffold", 40, 16, 7, **U)
    P("ud_survey_tripod", 52, 16, 4, **U)
    P("ud_crystal_spire", 36, 10, 9, **U)
    P("ud_crystal_spire", 56, 10, 9, **U)
    P("ud_glow_pool", 46, 20, 3, **U)
    return zone, L


def generate_mother_vein():
    zone, L = build_mother_vein()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_mother_vein_baked():
    """(zone, layout) with props + QA done - what the baker paints from."""
    zone, L = build_mother_vein()
    dress(zone, L)
    finish(zone, L)
    return zone, L
