"""Rocky Pass (120x190): an alpine dungeon above the treeline, levels 33-36.

Kyle: "lets make an alpine dungeon from 33-36 in northern 1000 needles." Then: "It will be an
outdoor dungeon going back and forth through canyons."

ARCHETYPE: THE EXPOSED TRAVERSE. Every other dungeon in this game is a roof over your head - caves,
a keep, a crypt, two ships. This one is outside, and what makes it a dungeon rather than open world
is not walls but that the ground gives you exactly one line and will not let you leave it.

IT IS A SWITCHBACK, NOT A CHAIN OF ROOMS, and that is a correction rather than a preference. The
first version was rooms joined by short gullies, and Kyle looked at the render and said: "Looks
like anal beads bro." He was right - a route built by unioning circles reads as a string of
circles no matter where the circles go. So the geometry here is LEGS: long canyon runs that cross
the map, joined at alternating ends by short climbs. You walk east, you climb, you walk west, you
climb. The bowls that bosses stand in hang off the legs rather than being the route.

THE CLIMB IS THE GRADIENT. South (high y) is the mouth, north (low y) is the summit, and three
things change the whole way up:

    floor     dirt and stone low, stone through the middle, ice near the top
    trees     tall aspen and pine at the mouth, then young, then bent, then krummholz, then
              nothing much - and FEWER of them the higher you go
    bake      tools/bake_rocky_pass.py carries rock -> frost -> snow over the same axis

TREES GROW ON THE WALLS. Kyle: "dont forget to put trees 'on the wall' so its not barren, we want
to see trees too bro" - and then, when I asked: "its a forest :)". So forest() plants on tiles that
are NOT walkable, with solid=False, which is the only way a canyon reads as cut through a forest
rather than through bare rock. A tree on a wall costs nothing and blocks nothing; the wall is
already solid.

HARPIES AND QUILBOAR, and the fight here answers a loose end in the zone below. The Aspen
Wilderness's own design doc flags that its harpies are "nesting in aspen crowns, which is not where
harpies nest." They are refugees. This is the roost they were driven out of, and what drove them
out is quilboar - the ones who climbed highest when the mountain pushed them out of the Barrens and
who took the only defensible ground on the range. The harpies are trying to take it back. The
player arrives in the middle of that and neither side cares which one they are.

THE SEAM GETS ONE DETAIL AND NO MORE: Barrens red dust, drifted into the lee of the summit, four
thousand feet above where any of it belongs. The props say it; nothing explains it. Whatever stands
at the Seam is the zone's own mystery and a side dungeon is the wrong place to spend it.

HARD CONTRACT (world/portal_manager.py): The Aspen Wilderness (48, 35) <-> Rocky Pass (52, 186).
"""
import random

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked  # noqa: F401
from tools.dungeon_builder import _aspect  # noqa: F401

BAKED = "assets/tiles/rocky_pass/baked"
AP = "assets/tiles/aspen/props/"

W, H = 120, 190
PORTAL = (52, 186)

#: THE LEGS. Each is [(polyline, width), ...]; corridor(width=N) clears about 2N+1 tiles. They run
#: across the map and alternate direction, so the route is a switchback rather than a tube.
#:
#: A LEG IS SPECIFIED BY WHERE IT HAS TO ARRIVE, not by how far it has to go. An earlier pass gave
#: the joins a distance to cover and put their endpoints on the EDGE of what they were joining;
#: four of them carved a band that touched neither end, and everything above the couloir was
#: unreachable. Every polyline here starts and ends well INSIDE the thing it connects to.
LEGS = {
    "mouth":       [([(52, 184), (38, 180), (24, 176)], 3)],
    "long_run":    [([(22, 168), (40, 160), (70, 156), (100, 150)], 3)],
    "wind_gap":    [([(102, 136), (80, 130), (50, 126), (26, 120)], 3)],
    "narrows":     [([(22, 108), (44, 102), (70, 98), (94, 92)], 2)],
    "last_canyon": [([(96, 80), (78, 74), (58, 70), (42, 66)], 3)],
}

#: The climbs that join one leg to the next, at the FAR end of the leg you just walked. These are
#: the constrictions - short, narrow, and the only way up.
TURNS = [
    ([(24, 176), (20, 170), (22, 168)], 2),      # mouth -> long_run, at the west end
    ([(100, 150), (104, 142), (102, 136)], 2),   # long_run -> wind_gap, at the east end
    ([(26, 120), (20, 114), (22, 108)], 2),      # wind_gap -> narrows, at the west end
    ([(94, 92), (98, 86), (96, 80)], 2),         # narrows -> last_canyon, at the east end
    ([(42, 66), (46, 56), (56, 44), (62, 36)], 2),  # last_canyon -> the summit basin
]

#: Bowls hang OFF the legs - they are where a boss stands, not part of the walk. (cx, cy, rx, ry)
BOWLS = {
    "vekka_bowl": (28, 122, 10, 8),      # Thornmother Vekka, at the west end of the wind gap
    "hagra_bowl": (38, 64, 10, 8),       # Hagra Stormcrown, at the west end of the last canyon
    "basin": (62, 30, 22, 12),           # the summit. Gorrek Passkeeper.
}

#: Dead ends: a short draw off a leg, ending in a pocket. (polyline+width list, pocket ellipse)
#:
#: A DEAD END HAS TO BE CHECKED FOR BEING ONE. An earlier hanging draw grew north until it touched
#: the leg above it, which short-circuited two whole legs of the switchback - and nothing failed,
#: because a short circuit is perfectly connected. verify_turns catches it now.
SPURS = {
    "hanging_draw": ([([(62, 103), (62, 85)], 2)], (62, 84, 8, 5)),   # The Windsnapped, a rare
    "wind_scour":   ([([(74, 155), (77, 169)], 2)], (78, 170, 8, 5)),  # optional, one chest
}

#: (label, x0, x1, y0, y1) - a SMALL box round each turn. verify_turns seals the box and checks
#: the route above is cut off, then measures how wide the turn actually is.
#:
#: SMALL IS THE WHOLE POINT. The check this replaced sealed a full-width band and asserted that
#: something got stranded - which sounds right and is vacuous, because this map is one line, so a
#: band across it cuts the map wherever you put it, merged geometry or not. It only came to light
#: by deliberately widening a room until it swallowed two joins and watching the check pass. A
#: negative control is part of a check's design, not a nicety.
TURN_BOXES = [
    ("mouth|long_run", 14, 30, 166, 180),
    ("long_run|wind_gap", 94, 110, 134, 152),
    ("wind_gap|narrows", 14, 32, 106, 122),
    ("narrows|last_canyon", 88, 104, 78, 94),
    ("last_canyon|basin", 36, 60, 44, 70),
]
#: THE PINCH, not the widest row. A box round a turn necessarily contains the ends of the two legs
#: it joins, so measuring the widest row in it measures a leg and reports 13-25 tiles for turns
#: that are perfectly fine. What distinguishes a turn from two legs that have run into each other
#: is that a turn has a NARROW row somewhere in it. Healthy turns come out 3-5 against 15-17 for a
#: merged pair.
MAX_TURN_PINCH = 7

#: FLOOR BY ALTITUDE. (y at or above which this applies, base tile). South is low, north is high.
FLOOR_BANDS = [(150, "dirt"), (96, "stone"), (52, "stone"), (0, "ice")]

#: THE FOREST. (y at or above which this applies, [(prop, height)], density)
#:
#: Kyle: "So like a true mountain, trees are bigger at the start and gradually get smaller as
#: well". Then: "Ok reduce the starting number of trees by about 25% if possible. We still want
#: some at the peak - and a bit more of a gradient". So the mouth bands are ~0.28 rather than the
#: 0.38 they started at, there is still something standing at the summit, and the steps between
#: bands are smaller so the thinning reads as gradual rather than as four distinct forests.
FOREST_BANDS = [
    (166, [("asp_aspen_tall", 8), ("asp_pine_tall", 9), ("asp_aspen_clump", 7)], 0.28),
    (150, [("asp_pine_tall", 8), ("asp_aspen_tall", 7), ("asp_aspen_clump", 6)], 0.25),
    (132, [("asp_pine_tall", 7), ("asp_aspen_young", 5), ("asp_pine_young", 6)], 0.21),
    (114, [("asp_pine_young", 5), ("asp_aspen_young", 4), ("asp_pine_bent", 5)], 0.17),
    (96,  [("asp_pine_young", 4), ("asp_pine_bent", 4), ("asp_dead_scrub", 3)], 0.13),
    (78,  [("asp_pine_bent", 4), ("asp_pine_krummholz", 3), ("asp_dead_scrub", 3)], 0.095),
    (58,  [("asp_pine_krummholz", 3), ("asp_pine_bent", 3), ("asp_dead_scrub", 2)], 0.065),
    (34,  [("asp_pine_krummholz", 2), ("asp_dead_scrub", 2)], 0.055),
    (0,   [("asp_pine_krummholz", 2), ("asp_dead_scrub", 2)], 0.038),
]
#: Plant on every Nth wall tile rather than testing all of them - a canyon has a lot of wall, and
#: at step 1 the density figures above would put a tree on top of a tree.
FOREST_STEP = 4

BOSSES = {
    "Thornmother Vekka": (28, 122),
    "Hagra Stormcrown": (38, 64),
    "Gorrek Passkeeper": (62, 30),
    "The Windsnapped": (62, 84),      # the rare, in the hanging draw
}
CHESTS = [(78, 170), (62, 84), (62, 30)]

TRASH = ["Pass-Climber Quilboar", "Thornweald Geomancer", "Ridge-Wind Harpy",
         "Snowcrest Windcaller", "Cliff-Backed Ram"]

#: (cx, cy, level, [names]). Three to four pulls before each main boss, per Kyle: "For a dungeon
#: we want roughly 3-4 trash packs before each boss, for smaller dungeons this can be reduced to
#: like 2 or so." Mixed-role on purpose - a pull of three identical mobs is one mob three times.
PACKS = [
    # ---- up to Vekka, who holds the wind gap
    (40, 178, 33, ["Pass-Climber Quilboar", "Pass-Climber Quilboar", "Cliff-Backed Ram"]),
    (46, 159, 33, ["Pass-Climber Quilboar", "Thornweald Geomancer", "Pass-Climber Quilboar"]),
    (82, 153, 33, ["Pass-Climber Quilboar", "Cliff-Backed Ram", "Thornweald Geomancer"]),
    (68, 128, 34, ["Thornweald Geomancer", "Pass-Climber Quilboar", "Pass-Climber Quilboar"]),
    # ---- the narrows and the hanging draw off it. ALL THREE OF THESE BELONG TO THE RARE, and
    # that is geometry rather than choice: the draw hangs directly off the narrows, while the
    # route to Hagra runs the whole length of the narrows east, up the turn, and back west again.
    # Anything standing on the narrows is nearer the thing in the draw than the thing two legs
    # away, so putting "Hagra's approach" here just gave the rare a bodyguard of five.
    (40, 103, 34, ["Ridge-Wind Harpy", "Ridge-Wind Harpy", "Snowcrest Windcaller"]),
    (62, 96, 35, ["Ridge-Wind Harpy", "Snowcrest Windcaller", "Ridge-Wind Harpy"]),
    (62, 89, 35, ["Snowcrest Windcaller", "Ridge-Wind Harpy", "Ridge-Wind Harpy"]),
    # ---- Hagra's approach is the last canyon, which is the leg she actually sits at the end of.
    (86, 78, 35, ["Ridge-Wind Harpy", "Snowcrest Windcaller", "Ridge-Wind Harpy"]),
    (72, 74, 35, ["Snowcrest Windcaller", "Ridge-Wind Harpy", "Pass-Climber Quilboar"]),
    (58, 72, 35, ["Ridge-Wind Harpy", "Ridge-Wind Harpy", "Snowcrest Windcaller"]),
    # ---- the climb to the summit. ABOVE the midpoint of the last turn, or they belong to Hagra:
    # that turn is thirty tiles long, so a pack in the bottom half of it is nearer the boss below.
    (54, 48, 36, ["Pass-Climber Quilboar", "Pass-Climber Quilboar", "Thornweald Geomancer"]),
    (60, 40, 36, ["Thornweald Geomancer", "Pass-Climber Quilboar", "Cliff-Backed Ram"]),
    (46, 34, 36, ["Pass-Climber Quilboar", "Thornweald Geomancer", "Pass-Climber Quilboar"]),
]


def _floor_for(y):
    for (lo, tile) in FLOOR_BANDS:
        if y >= lo:
            return tile
    return "ice"


def build_rocky_pass():
    zone = Tilemap("Rocky Pass", W, H,
                   "A pass over the northern range, switching back and forth up the canyons above "
                   "the treeline. The quilboar hold the only flat ground on it and the harpies "
                   "want it back.")
    zone.is_cave = True
    #: .region declares the PARENT ZONE - the encounter lookup keys off it.
    zone.region = "The Aspen Wilderness"
    zone.fixed_spawns = True

    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b
    b.wall_id = "rock"
    b.floor_id = "stone"
    for y in range(H):
        for x in range(W):
            zone.collision_layer[y][x] = "rock"
            zone.set_tile(x, y, "rock", "base")

    for parts in LEGS.values():
        for (pts, wdt) in parts:
            b.corridor(pts, width=wdt)
    for (pts, wdt) in TURNS:
        b.corridor(pts, width=wdt)
    b.lobes(list(BOWLS.values()))
    for (paths, pocket) in SPURS.values():
        for (pts, wdt) in paths:
            b.corridor(pts, width=wdt)
        b.lobes([pocket])
    # the cleft down to the Aspen Wilderness
    b.corridor([(52, 188), (52, 182)], width=1)

    # ---- the altitude gradient in the floor itself, so the climb reads even unbaked
    for y in range(H):
        tile = _floor_for(y)
        for x in range(W):
            if zone.is_walkable(x, y) and zone.base_layer[y][x] != "rock":
                zone.set_tile(x, y, tile, "base")

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.set_tile(px, py, "stone", "base")
    L.mark("portal", px, py)

    fixed = []
    for name, (bx, by) in BOSSES.items():
        if not zone.is_walkable(bx, by):
            raise AssertionError(f"{zone.name}: {name} at ({bx},{by}) is not on walkable ground")
        fixed.append((bx, by, name))
        L.mark("boss_marker", bx, by)
    zone.boss_positions = fixed
    zone.boss_position = fixed[0][:2]

    for (cx, cy) in CHESTS:
        if zone.is_walkable(cx, cy):
            L.mark("chest", cx, cy)

    import tools.ship_builder as sb
    zone.trash_packs = sb.place_packs(zone, PACKS, rad=8)
    zone.trash_spawns = [m for pack in zone.trash_packs for m in pack]

    zone.add_subzone("Rocky Pass", 0, 0, W, H)
    zone.add_subzone("The Mouth", 10, 160, 60, 30)
    zone.add_subzone("The Long Run", 14, 140, 96, 34)
    zone.add_subzone("The Wind Gap", 14, 108, 96, 34)
    zone.add_subzone("The Narrows", 14, 76, 92, 34)
    zone.add_subzone("The Summit Basin", 30, 14, 70, 44)
    return zone, L


def verify_turns(zone):
    """Each turn must be a real constriction, and each spur a real dead end.

    Seals a SMALL box round each turn and checks the route above goes unreachable, then measures
    the turn's widest walkable row. A turn that comes back 15 tiles across is two legs that have
    run into each other, which is perfectly connected and not a traverse.
    """
    from collections import deque

    def flood(start, blocked=frozenset()):
        seen = {start}
        q = deque([start])
        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if n not in seen and n not in blocked and zone.is_walkable(*n):
                    seen.add(n)
                    q.append(n)
        return seen

    start = (PORTAL[0], PORTAL[1] - 2)
    summit = BOSSES["Gorrek Passkeeper"]
    problems = []
    report = []

    # THE BASELINE FIRST, or every test below passes for the wrong reason. The first run of this
    # had the last turn stopping four tiles short of the summit basin, so the summit was
    # unreachable with NOTHING sealed - and every single turn duly reported "sealing this cuts the
    # route to the summit", because the route was already cut. A cut test needs to know the thing
    # was connected to begin with.
    reachable = flood(start)
    if summit not in reachable:
        problems.append("the summit is unreachable before anything is sealed - every turn test "
                        "below would pass for that reason alone")
        return report, problems
    total = sum(zone.is_walkable(x, y) for y in range(H) for x in range(W))
    if total != len(reachable):
        problems.append(f"{total - len(reachable)} walkable tiles are isolated")

    for (label, x0, x1, y0, y1) in TURN_BOXES:
        box = {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
        if summit in flood(start, frozenset(box)):
            problems.append(f"sealing the turn {label} does not cut the route to the summit - "
                            f"there is another way round, so it is not a constriction")
        rows = [sum(zone.is_walkable(x, y) for x in range(x0, x1 + 1))
                for y in range(y0, y1 + 1)]
        pinch = min((r for r in rows if r), default=0)
        if pinch > MAX_TURN_PINCH:
            problems.append(f"the turn {label} never narrows below {pinch} tiles, over the "
                            f"{MAX_TURN_PINCH} a turn may be - the two legs have merged")
        report.append((label, pinch))

    # A SPUR IS A DEAD END IF THE ROUTE DOES NOT NEED IT. Sealing its throat was the obvious test
    # and the wrong one: a leg is wide enough that a spur joins it over several tiles, so a box on
    # the throat leaves a way in round the side and the test fails on a perfectly good dead end.
    # Sealing the POCKET and checking the summit is still reachable asks the real question.
    for name, (paths, pocket) in SPURS.items():
        cx, cy, rx, ry = pocket
        blob = {(cx + dx, cy + dy) for dx in range(-rx, rx + 1) for dy in range(-ry, ry + 1)
                if (dx / max(rx, 1)) ** 2 + (dy / max(ry, 1)) ** 2 <= 1.0}
        if summit not in flood(start, frozenset(blob)):
            problems.append(f"the spur '{name}' is on the main route - sealing its pocket cuts "
                            f"the summit off, so it is a leg of the switchback, not a dead end")
    return report, problems


def forest(zone, L):
    """Trees on the canyon WALLS, thinning and shrinking with altitude.

    Kyle: "dont forget to put trees 'on the wall' so its not barren, we want to see trees too bro"
    ... "its a forest :)". Planted on tiles that are NOT walkable, solid=False, so they cost
    nothing and block nothing - the wall is already solid. Going through Builder.prop rather than
    CaveLayout.prop because the latter refuses any prop whose base is not dry walkable floor,
    which is the whole point here.

    NOTHING IS PLANTED WHERE IT WOULD RISE THROUGH A WALKABLE ROW. A sprite is drawn upward from
    its base, so a tree standing on the wall SOUTH of a canyon hangs over the canyon floor and
    hides the path. Every candidate is checked for walkable ground in the rows its canopy covers.
    """
    rng = random.Random(3416)
    planted = 0
    for y in range(0, H, 1):
        for (lo, choices, density) in FOREST_BANDS:
            if y >= lo:
                break
        for x in range(0, W, FOREST_STEP):
            if zone.is_walkable(x, y):
                continue
            if rng.random() > density:
                continue
            name, height = choices[rng.randrange(len(choices))]
            # would its canopy hang over the path?
            if any(zone.is_walkable(cx, cy)
                   for cy in range(max(0, y - height + 1), y + 1)
                   for cx in range(max(0, x - 2), min(W, x + 3))):
                continue
            L.b.prop(f"{AP}{name}.png", x, y, height, solid=False)
            planted += 1
    return planted


def dress(zone, L):
    """The ground itself: talus, boulders, the summit's red dust."""
    P = L.prop
    A = dict(where=AP)
    P("asp_talus_pile", 44, 181, 4, **A)
    P("asp_boulder", 52, 181, 4, **A)
    P("asp_deadfall_pile", 30, 171, 3, near_ok=True, **A)
    P("asp_boulder_lichen", 54, 158, 4, **A)
    P("asp_aspen_fallen", 86, 153, 3, near_ok=True, **A)
    P("asp_talus_pile", 60, 128, 4, **A)
    P("asp_boulder_split", 90, 133, 5, **A)
    P("asp_elk_skull", 34, 124, 2, near_ok=True, **A)
    P("asp_boulder", 54, 101, 4, **A)
    P("asp_talus_pile", 80, 96, 4, **A)
    P("asp_snag_standing", 68, 73, 6, **A)
    P("asp_boulder_lichen", 50, 69, 4, **A)
    P("asp_dead_scrub", 42, 60, 3, near_ok=True, **A)
    # THE SEAM, and nothing else about it: Barrens red dust, drifted into the lee of the summit,
    # four thousand feet above where any of it belongs.
    P("asp_red_drift", 70, 34, 3, near_ok=True, **A)
    P("asp_red_drift", 54, 28, 3, near_ok=True, **A)
    P("asp_talus_pile", 76, 26, 4, **A)
    P("asp_boulder_split", 48, 24, 5, **A)
    return zone, L


def finish(zone, L):
    targets = [PORTAL] + [(x, y) for (x, y, _n) in zone.boss_positions] \
        + [(s[0], s[1]) for s in zone.trash_spawns]
    return L.finish(targets)


def build_rocky_pass_baked():
    """(zone, layout) with props and QA done - what the baker paints from."""
    zone, L = build_rocky_pass()
    dress(zone, L)
    forest(zone, L)
    finish(zone, L)
    return zone, L


def generate_rocky_pass():
    zone, L = build_rocky_pass_baked()
    register_baked(zone, BAKED)
    return zone
