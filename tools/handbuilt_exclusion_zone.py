"""
Hand-built THE EXCLUSION ZONE, levels 57-60: the dungeon under the wheel in Deadwind East, the last T0 token dungeon
(docs/deadwind_brief.md, docs/deadwind_quest_plan.md). Three floors, three maps, one dungeon.

Kyle, 17-18 Nov 2026: "ONLY pripyat as the entrance to the fallout zone dungeon (We need one more dungeon with our last
T0 token - this is it)"; on the 18th he named it the Exclusion Zone, and then: "make the exclusion zone multiple layers
and kind of nuclear reactor mixed with the wheel...make the wheel massive and iconic!"

It's the rupture itself. The tear keeps a copy of everything that dies near it, and it has been reading the people
who came through it too. Under the wheel it grew a copy of the wheel. Under that, it grew the thing the transplants
carry in their heads whenever they look at the wheel: the building behind it, the reactor. Nothing from Earth is down
here, only the shapes, and the deeper you go the better the copy gets.

THE WHEEL'S SHADOW (200x200), 57-59: the wheel, laid flat underground.
    You climb down into the bottom of the rim and walk it the long way round, three quarters of the circle. Each
    chamber hangs off the rim where a car would hang, and the small alcoves between them are cars too. The last
    quarter has fallen in. From the east chamber the one open spoke runs in to the hub, and the hub is the axle: a
    shaft straight down, ringed with the seep, a stair cut into its island.
        the Crater Floor    the rim's bottom, Deadwind rock: Gristlemaw, a heap of the pass's ogres moving as one
        the Brood           the west chamber, flesh and silk: Broodmother Vexis
        the Stacks          the north chamber, black-glass shelving, every moment the tear kept filed on it:
                            Archivist Nine, Karazhan's librarian at nine ages at once
        the Hanging Cars    the east chamber: the wheel's cars hang from the roof as cages, and the volunteers who
                            went down before the camp knew better made their last camp under them
        the Open Spoke      in from the east chamber to the axle; the other three spokes end against stopped time
        the Axle            the hub: the shaft down, and the stair

THE REACTOR HALL (180x160), 58-60: the building behind the wheel, copied from memory and copied wrong way up.
    The shaft comes down at the north end. The core is a sealed block in the middle, and the only way into it is
    the long way round: west down the turbine hall, east across the flooded basement, north up the roof gallery,
    and in through the breach.
        the Axle's Foot     where the shaft comes down
        the Turbine Hall    a long hall down the west side, its turbines standing in a row like dead engines
        the Bubbler Pools   the flooded basement along the south side, two pools of the seep, and the Glow-Eater,
                            which eats it
        the Ninety Seconds  the east gallery, the reactor's roof copied inside out, graphite where it fell and
                            every blast and scream stopped where it was: the Stopped Man
        the Lid             the core, through the breach. The great round lid stands on its edge, the way it
                            landed, and the stair goes down beside it

THE FOOT (150x150), 59-60: where it all ran down to.
        the Sandfall        the bottom of the shaft, heaped with everything ever dropped down it
        the Steam Corridor  the long way down, three sides round the basement, the melt running beside you in
                            channels toward the middle
        the Elephant's Foot the basement: a lake of the melt, four channels pouring in, and the Wound's Heart on the
                            island in the middle. The fast exit is a ledge on the far side, over a second bridge.

THE NAMES ARE THE LIQUIDATORS'. The Forsaken call the place the Wound and its rooms by what's in them; the transplants
named the rooms after home, the way their parents' generation talked about Reactor Four:
  * the Bubbler Pools: under the reactor were the bubbler pools, and in May 1986 three men waded into the flooded
    basement in the dark to open the valves that drained them, so the core couldn't melt into the water and blow the
    rest of it apart. Halyna's father knew one of them.
  * the Ninety Seconds: the soldiers who cleared the graphite off the reactor roof by hand were given ninety seconds
    each, because that was all the dose a body could take. The liquidators work the gallery the same way, in timed
    shifts, and the Stopped Man is the one who stayed too long.
  * the Lid: the reactor's upper shield, a disc of steel and concrete heavier than a ship, was thrown up by the
    explosion and came down on its edge across the open core.
  * the Sandfall: helicopters dropped thousands of tonnes of sand, clay, lead and boron into the open reactor.
  * the Steam Corridor and the Elephant's Foot: the melted fuel, concrete and sand ran down through the steam
    corridors into the basement and set there, so hot that a few minutes beside it was enough. Kenji gave the
    Wound's Heart the name the first time he saw it.
Nothing from Earth is down here: the names are only words, the way people carry home with them.

The way out is the way you came in, or the fast exit past the Wound's Heart (Kyle, 16 Nov: "make a fast exit from the
dungeon to outside in the open world. prevents people from running back").

Trash comes in packs of four or five (world/dungeon_packs). The creatures, kits and loot are tools/build_deadwind_content.py.

HARD CONTRACTS (world/portal_manager.py)
  (100, 196) on the Wheel's Shadow <-> Deadwind East's wheel (152, 93)
  STAIR_DOWN[SHADOW] (100, 100) <-> STAIR_UP[HALL] (90, 4)
  STAIR_DOWN[HALL] (92, 72) <-> STAIR_UP[FOOT] (75, 2)
  FAST_EXIT (30, 84) on the Foot -> Deadwind East (152, 93), one way
"""
import math
import os
from collections import deque

from world.tilemap import Tilemap
from tools.dungeon_builder import Builder

NAME = "The Exclusion Zone"
SHADOW, HALL, FOOT = NAME, f"{NAME}: The Reactor Hall", f"{NAME}: The Foot"
FLOORS = (SHADOW, HALL, FOOT)
TITLE = {SHADOW: "The Wheel's Shadow", HALL: "The Reactor Hall", FOOT: "The Foot"}
LEVELS = {SHADOW: (57, 59), HALL: (58, 60), FOOT: (59, 60)}
BAKED = {SHADOW: "assets/tiles/fallout_zone/baked_exclusion_zone",
         HALL: "assets/tiles/fallout_zone/baked_reactor_hall",
         FOOT: "assets/tiles/fallout_zone/baked_the_foot"}
REGION = "Deadwind East"

PORTAL = (100, 196)
STAIR_DOWN = {SHADOW: (100, 100), HALL: (92, 72)}
STAIR_UP = {HALL: (90, 4), FOOT: (75, 2)}
FAST_EXIT = (30, 84)
C = (100, 100)
RIM_R = 72
FZ = "assets/tiles/dungeon_props/fz_"


def _rim_point(deg, r=None):
    """A point on the rim: 90 degrees is the bottom (screen y grows down), 180 the west, 270 the north, 360 the east.
    The rim breathes a little so it never reads as a compass circle."""
    a = math.radians(deg)
    r = (RIM_R if r is None else r) + 3.0 * math.sin(3 * a + 0.7) + 1.5 * math.sin(7 * a)
    return (C[0] + r * math.cos(a), C[1] + r * math.sin(a))


def _ip(p):
    return (int(round(p[0])), int(round(p[1])))


#: the rim, the long way round from the bottom to the east; the south-east quarter has fallen in
RIM = [_ip(_rim_point(d)) for d in range(90, 361, 10)]
#: the small cars between the chambers, hung off the outside of the rim
CARS = {d: _ip(_rim_point(d, RIM_R + 11)) for d in (135, 225, 315)}

FLOOR = {
    # ================================================================================================ THE WHEEL'S SHADOW
    SHADOW: dict(
        size=(200, 200), start=(PORTAL[0], PORTAL[1] - 2),
        rooms={
            "The Crater Floor": ("lobes", [(100, 172, 20, 12), (85, 178, 8, 6), (115, 177, 8, 6), (100, 184, 7, 6)]),
            "The Brood":        ("lobes", [(28, 100, 15, 19), (17, 85, 7, 6), (17, 116, 7, 6), (39, 89, 6, 5),
                                           (39, 112, 6, 5)]),
            "The Stacks":       ("rect", 70, 10, 130, 42, 4),
            "The Hanging Cars": ("rect", 158, 78, 188, 122, 3),
            "The Open Spoke":   ("rect", 116, 97, 158, 103, 0),
            "The Axle":         ("lobes", [(100, 100, 16, 14)]),
        },
        cells=[(cx - 5, cy - 4, cx + 5, cy + 4) for (cx, cy) in CARS.values()],
        cell_links=[([_ip(_rim_point(d)), CARS[d]], 1) for d in CARS],
        # the seep, pooled: the axle's ring, and the Brood's birthing pool behind Vexis
        deep=[(100, 100, 10, 8), (24, 100, 4, 6)],
        land=[(100, 100, 5, 4)],
        channels=[],
        passages=[([PORTAL, (100, 184)], 2),                     # the climb down into the crater
                  (RIM, 2),                                      # the rim, the long way round
                  # the dead spokes: in from their chambers, ending against stopped time
                  ([(40, 100), (66, 100)], 1), ([(100, 42), (100, 66)], 1), ([(100, 160), (100, 136)], 1)],
        bridges=[([(116, 100), (104, 100)], 1)],                 # the open spoke's end, over the ring to the island
        #: the Stacks' shelving: rows of black glass, north of the rim's line through the room, an aisle down the middle
        blocks=[(x, y, 2, 5) for x in (76, 82, 88, 110, 116, 122) for y in (13, 20)],
        bosses=[(100, 168, "Gristlemaw"), (24, 108, "Broodmother Vexis"), (100, 17, "Archivist Nine")],
        final="Archivist Nine",
        doors=[PORTAL, STAIR_DOWN[SHADOW]],
        chests=[(115, 180), (17, 116)] + list(CARS.values()) + [(184, 118)],
        dressing=[
            # the crater floor: the collapsed supports you climb down past, the ogres' carcass heaps
            ("collapsed_support", 92, 186, 4, "core"), ("collapsed_support", 108, 186, 4, "core"),
            ("carcass_heap", 86, 176, 3, "core"), ("carcass_heap", 116, 174, 3, "core"),
            ("bone_altar", 100, 162, 3, "core"),
            # the rim: barricades, a vent, the cars between the chambers hanging over their alcoves
            ("barricade", 34, 132, 3, "core"), ("fume_vent", 44, 142, 3, "core"), ("rib_arch", 44, 52, 4, False),
            ("glass_shard", 140, 36, 4, "core"),
            *[("hanging_cage", x, y - 1, 5, "core") for (x, y) in CARS.values()],
            # the brood: pods and sacs off every lobe
            ("flesh_sac", 17, 84, 3, "core"), ("open_pod", 17, 115, 3, "core"), ("flesh_sac", 39, 88, 3, "core"),
            ("open_pod", 39, 111, 3, "core"), ("flesh_pillar", 34, 100, 4, "core"), ("eye_cluster", 20, 92, 3, False),
            # the stacks: the archive's stones at the ends of the aisles, the air torn over the librarian's desk
            ("rune_stone", 74, 38, 3, "core"), ("rune_stone", 126, 38, 3, "core"), ("air_tear", 100, 13, 4, False),
            ("crystal_pillar", 92, 40, 4, "core"), ("crystal_pillar", 108, 40, 4, "core"),
            # the hanging cars: cages from the roof, and the volunteers' camp under them
            ("hanging_cage", 164, 86, 6, "core"), ("hanging_cage", 182, 86, 6, "core"),
            ("hanging_cage", 164, 114, 6, "core"), ("hanging_cage", 182, 114, 6, "core"),
            ("dead_kit", 172, 96, 3, False), ("dead_kit", 176, 106, 3, False), ("barricade", 186, 100, 3, "core"),
            # the dead spokes, ended against stopped time
            ("stopped_blast", 66, 101, 4, False), ("stopped_blast", 100, 67, 4, False),
            ("stopped_blast", 100, 137, 4, False),
            ("dead_kit", 60, 100, 3, False), ("dead_kit", 100, 62, 3, False), ("dead_kit", 100, 142, 3, False),
            # the open spoke, and the axle: the seep pouring into the shaft, the stair down on the island
            ("floating_ring", 140, 98, 5, False), ("ooze_fall", 92, 90, 5, False), ("ooze_fall", 108, 90, 5, False),
            ("down_stair", 100, 101, 4, False),
        ],
    ),
    # ================================================================================================ THE REACTOR HALL
    HALL: dict(
        size=(180, 160), start=(STAIR_UP[HALL][0], STAIR_UP[HALL][1] + 4),
        rooms={
            "The Axle's Foot":    ("rect", 76, 4, 104, 20, 2),
            "The Turbine Hall":   ("rect", 10, 14, 50, 146, 3),
            "The Bubbler Pools":  ("rect", 56, 116, 126, 152, 4),
            "The Ninety Seconds": ("rect", 132, 18, 170, 150, 3),
            "The Lid":            ("lobes", [(92, 68, 18, 16)]),
        },
        cells=[(150, 152 - 8, 160, 152)],
        cell_links=[],
        deep=[(72, 134, 8, 11), (110, 134, 8, 11)],              # the two pools of the seep
        land=[],
        channels=[],
        passages=[([(77, 12), (56, 12), (46, 20)], 2),            # the axle's foot -> the turbine hall
                  ([(46, 134), (60, 134)], 2),                     # the turbine hall -> the bubbler pools
                  ([(122, 134), (136, 134)], 2),                   # the bubbler pools -> the roof gallery
                  ([(134, 28), (92, 28), (92, 54)], 1)],           # the breach, into the core
        bridges=[],
        #: the turbines, a row of them down the middle of the hall
        blocks=[(26, y, 9, 11) for y in (26, 50, 74, 98, 122)],
        bosses=[(91, 134, "The Glow-Eater"), (143, 30, "The Stopped Man")],
        final="The Stopped Man",
        doors=[STAIR_UP[HALL], STAIR_DOWN[HALL]],
        chests=[(14, 142), (122, 150), (166, 22), (155, 148)],
        dressing=[
            ("collapsed_support", 82, 8, 4, "core"), ("collapsed_support", 98, 8, 4, "core"),
            ("ooze_fall", 90, 16, 5, False),
            # the turbine hall: vents and fallen beams between the turbines
            ("fume_vent", 30, 40, 3, "core"), ("fume_vent", 30, 88, 3, "core"), ("fume_vent", 30, 136, 3, "core"),
            ("collapsed_support", 14, 62, 4, "core"), ("collapsed_support", 46, 110, 4, "core"),
            ("slag_cluster", 44, 30, 3, "core"), ("dead_kit", 16, 96, 3, False),
            # the bubbler pools: the seep pouring in, slag on the walkway between
            ("ooze_fall", 72, 120, 5, False), ("ooze_fall", 110, 120, 5, False), ("slag_pool", 91, 148, 3, False),
            ("slag_cluster", 62, 150, 3, "core"), ("slag_cluster", 120, 150, 3, "core"),
            # the ninety seconds: graphite where it fell (black glass), and every blast stopped where it was
            ("glass_shard", 138, 120, 4, "core"), ("glass_shard", 164, 104, 4, "core"), ("glass_shard", 140, 80, 4, "core"),
            ("glass_shard", 162, 60, 4, "core"), ("glass_shard", 160, 26, 4, "core"),
            ("stopped_blast", 150, 128, 4, False), ("stopped_blast", 146, 94, 4, False),
            ("stopped_blast", 156, 70, 4, False), ("stopped_blast", 150, 44, 4, False),
            ("dead_kit", 158, 112, 3, False), ("dead_kit", 140, 56, 3, False),
            # the lid, standing on its edge, and the stair down beside it
            ("floating_ring", 92, 64, 9, False), ("crystal_pillar", 80, 60, 4, "core"),
            ("crystal_pillar", 104, 60, 4, "core"), ("down_stair", 92, 73, 4, False),
        ],
    ),
    # ================================================================================================ THE FOOT
    FOOT: dict(
        size=(150, 150), start=(STAIR_UP[FOOT][0], STAIR_UP[FOOT][1] + 4),
        rooms={
            "The Sandfall":        ("rect", 52, 2, 98, 24, 3),
            "The Steam Corridor":  ("rects", [(8, 28, 60, 38), (8, 28, 20, 140), (8, 128, 138, 140),
                                              (126, 40, 138, 140)]),
            "The Elephant's Foot": ("lobes", [(75, 84, 32, 26)]),
        },
        cells=[(26, 78, 38, 90)],                                # the ledge on the far side: the fast exit
        cell_links=[],
        deep=[(75, 84, 33, 27)],                                 # the lake of the melt, wall to wall
        land=[("rect", 100, 78, 108, 90), (75, 84, 7, 5)],       # the landing where you come in, the Heart's island
        #: the melt, running down to the lake in four channels (impassable): from the Sandfall, and in from beside the
        #: corridor on the west, south and east
        channels=[[(75, 23), (75, 60)], [(19, 100), (44, 96)], [(75, 129), (75, 108)], [(127, 104), (106, 96)]],
        passages=[([(56, 22), (56, 30)], 2),                     # the sandfall -> the corridor
                  ([(128, 84), (106, 84)], 2)],                  # the corridor -> the landing
        bridges=[([(101, 84), (81, 84)], 1),                     # the landing -> the island
                 ([(69, 84), (36, 84)], 1)],                     # the island -> the far ledge
        blocks=[],
        bosses=[(75, 84, "The Wound's Heart")],
        final="The Wound's Heart",
        doors=[STAIR_UP[FOOT], FAST_EXIT],
        chests=[(94, 6), (12, 136), (134, 136)],
        dressing=[
            # the sandfall: what was dropped down the shaft, heaped where it landed
            ("slag_cluster", 60, 10, 3, "core"), ("collapsed_support", 66, 18, 4, "core"),
            ("slag_cluster", 90, 12, 3, "core"), ("collapsed_support", 88, 20, 4, "core"),
            ("ooze_fall", 75, 22, 5, False),
            # the steam corridor: the volunteers who got furthest, and the vents
            ("dead_kit", 30, 33, 3, False), ("fume_vent", 12, 60, 3, "core"), ("dead_kit", 14, 120, 3, False),
            ("fume_vent", 40, 136, 3, "core"), ("dead_kit", 110, 134, 3, False), ("fume_vent", 134, 120, 3, "core"),
            ("stopped_blast", 132, 60, 4, False),
            # the foot
            ("heart_mass", 75, 82, 5, False), ("wound_pit", 69, 80, 3, False), ("eye_cluster", 81, 88, 3, False),
            ("slag_pool", 104, 88, 3, False), ("rune_stone", 30, 80, 3, "core"),
        ],
    ),
}

BOSSES = {}
#: every boss, in the order the T0 token rotation reads them (tools/build_deadwind_content.tokens)
BOSS_LIST = [(x, y, n) for f in FLOORS for (x, y, n) in FLOOR[f]["bosses"]]
_ORDER = ["Gristlemaw", "Broodmother Vexis", "The Glow-Eater", "Archivist Nine", "The Stopped Man", "The Wound's Heart"]
BOSS_LIST.sort(key=lambda b: _ORDER.index(b[2]))
FLOOR_OF = {n: f for f in FLOORS for (_x, _y, n) in FLOOR[f]["bosses"]}
TRASH = {}


def _rect_ellipses(x0, y0, x1, y1):
    """A long rect as a chain of overlapping round blobs (the bakers paint regions as ellipses), spaced about half
    a blob apart so the chain has no waist."""
    w, h = x1 - x0, y1 - y0
    side = max(1, min(w, h))
    n = max(1, math.ceil(2 * max(w, h) / side) - 1)
    out = []
    for i in range(n):
        along = side / 2 + ((max(w, h) - side) * i / (n - 1) if n > 1 else (max(w, h) - side) / 2)
        if w >= h:
            out.append((x0 + along, (y0 + y1) / 2, side * 0.62, h * 0.62))
        else:
            out.append(((x0 + x1) / 2, y0 + along, w * 0.62, side * 0.62))
    return out


def room_ellipses(floor, name, pad=2):
    """A room as (cx, cy, rx, ry) blobs, for the baker."""
    r = FLOOR[floor]["rooms"][name]
    if r[0] == "rect":
        return [(cx, cy, rx + pad, ry + pad) for (cx, cy, rx, ry) in _rect_ellipses(*r[1:5])]
    if r[0] == "rects":
        return [(cx, cy, rx + pad, ry + pad) for rc in r[1] for (cx, cy, rx, ry) in _rect_ellipses(*rc)]
    return [(cx, cy, rx + pad, ry + pad) for (cx, cy, rx, ry) in r[1]]


def _shape(b, spec, base=None):
    if spec[0] == "rect":
        _k, x0, y0, x1, y1 = spec[:5]
        b.rect(x0, y0, x1, y1, chamfer=(spec[5] if len(spec) > 5 else 0), base=base)
    elif spec[0] == "rects":
        for (x0, y0, x1, y1) in spec[1]:
            b.rect(x0, y0, x1, y1, chamfer=1, base=base)
    elif spec[0] == "lobes":
        b.lobes(spec[1], base=base)
    else:
        b.lobes([spec], base=base)


def _channel(zone, pts, half=1):
    """A channel of the melt along a polyline, 2 * half + 1 tiles across (the corridor carver only lays its base
    over floor that isn't walkable, so it can't pour lava over stone)."""
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = max(abs(bx - ax), abs(by - ay))
        for i in range(n + 1):
            x, y = round(ax + (bx - ax) * i / n), round(ay + (by - ay) * i / n)
            for dy in range(-half, half + 1):
                for dx in range(-half, half + 1):
                    if 1 <= x + dx < zone.width - 1 and 1 <= y + dy < zone.height - 1:
                        zone.collision_layer[y + dy][x + dx] = None
                        zone.set_tile(x + dx, y + dy, "lava", "base")


def _reach(zone, start):
    seen, q = {start}, deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and 0 <= n[0] < zone.width and 0 <= n[1] < zone.height and zone.is_walkable(*n):
                seen.add(n)
                q.append(n)
    return seen


def _seal(zone, start):
    """Any floor the way in can't walk to goes back to rock."""
    seen = _reach(zone, start)
    for y in range(zone.height):
        for x in range(zone.width):
            if (x, y) not in seen and zone.is_walkable(x, y):
                zone.collision_layer[y][x] = "rock"


def _dress(b, spec):
    """Each prop's base pulled onto the nearest floor within three tiles (the seep's edge wanders)."""
    z = b.zone
    for (name, x, y, h, solid) in spec["dressing"]:
        path = f"{FZ}{name}.png"
        if not os.path.exists(path):
            raise AssertionError((z.name, "no such prop", path))
        spot = min(((dx * dx + dy * dy, x + dx, y + dy) for dy in range(-3, 4) for dx in range(-3, 4)
                    if z.is_walkable(x + dx, y + dy)), default=None)
        if spot is None:
            raise AssertionError((z.name, "prop with no floor within reach", name, x, y))
        b.prop(path, spot[1], spot[2], h, solid=solid, fraction=0.3)


DESCRIPTION = {
    SHADOW: "Under the wheel. The tear kept a copy of everything that died near it, the wheel too, and the cavern has "
            "grown in its shape: a rim, spokes, and a shaft going down at the hub.",
    HALL: "Under the wheel's shadow, the tear has grown the building the transplants see whenever they look at the "
          "wheel. It remembers it wrong way up, and the core is sealed in the middle.",
    FOOT: "The bottom of everything. The melt ran down here through the steam corridors and set in the basement, and "
          "the wound's heart sits on it.",
}


def build_floor(name):
    spec = FLOOR[name]
    W, H = spec["size"]
    zone = Tilemap(name, W, H, DESCRIPTION[name])
    zone.is_cave = True
    #: the parent open zone, which is also the encounter-table key
    zone.region = REGION
    b = Builder(zone, wall_id="rock", floor_id="stone")
    for r in spec["rooms"].values():
        _shape(b, r)
    for (x0, y0, x1, y1) in spec["cells"]:
        b.rect(x0, y0, x1, y1, chamfer=1)
    for pts, wdt in spec["passages"] + spec["cell_links"]:
        b.corridor(pts, width=wdt)
    # THE SEEP AND THE MELT over the floor (impassable: lava under the hood), then the land laid back over it, then
    # the bridges across
    for pts in spec["channels"]:
        _channel(zone, pts)
    for d in spec["deep"]:
        _shape(b, d, base="lava")
    for d in spec["land"]:
        _shape(b, d)
    for pts, wdt in spec["bridges"]:
        b.corridor(pts, width=wdt)
    for (x, y, w, h) in spec["blocks"]:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                zone.collision_layer[yy][xx] = "rock"
    for (dx, dy) in spec["doors"]:
        for yy in (dy - 1, dy, dy + 1):
            if 0 <= yy < H and zone.base_layer[yy][dx] != "lava":
                zone.collision_layer[yy][dx] = None
    _seal(zone, spec["start"])
    _dress(b, spec)
    _seal(zone, spec["start"])

    fixed = []
    for (x, y, n) in spec["bosses"]:
        if not zone.is_walkable(x, y):
            raise AssertionError((name, "boss standing in rock or seep", n, x, y))
        fixed.append((x, y, n))
    BOSSES[name] = {n: (x, y) for (x, y, n) in fixed}
    final = next(f for f in fixed if f[2] == spec["final"])
    zone.boss_position = final[:2]
    zone.boss_positions = list(fixed)
    zone.chest_spots = list(spec["chests"])
    seen = _reach(zone, spec["start"])
    missing = [t for t in fixed + [(x, y, "chest") for (x, y) in zone.chest_spots]
               + [(d[0], d[1], "door") for d in spec["doors"]] if (t[0], t[1]) not in seen]
    if missing:
        raise AssertionError((name, "unreachable", missing))
    zone.add_subzone(name, 0, 0, W, H)
    for rname, r in spec["rooms"].items():
        if r[0] == "rect":
            zone.add_subzone(rname, r[1], r[2], r[3] - r[1] + 1, r[4] - r[2] + 1)
            continue
        rects = r[1] if r[0] == "rects" else [(cx - rx, cy - ry, cx + rx, cy + ry) for (cx, cy, rx, ry) in r[1]]
        x0, y0 = min(q[0] for q in rects), min(q[1] for q in rects)
        x1, y1 = max(q[2] for q in rects), max(q[3] for q in rects)
        zone.add_subzone(rname, x0, y0, x1 - x0 + 1, y1 - y0 + 1)
    return zone, b


def build_shadow_baked():
    return build_floor(SHADOW)[0], None


def build_hall_baked():
    return build_floor(HALL)[0], None


def build_foot_baked():
    return build_floor(FOOT)[0], None


def _trash(name=None):
    """Hand-placed, in the order you walk it. Each pack(...) is one pull, filled to four or five beside itself.
    With no floor named, every floor's."""
    if name is None:
        return [p for f in FLOORS for p in _trash(f)]
    T = []

    def pack(lvl, *spots):
        T.append([(x, y, m, lvl) for (x, y, m) in spots])

    rp = lambda d: _ip(_rim_point(d))     # noqa: E731
    if name == SHADOW:
        # THE CRATER FLOOR: what's left of Grosh'gok's ogres, and what they turned into
        pack(57, (88, 176, "Exclusion Ogre"), (92, 178, "Exclusion Ogre"), (90, 172, "Bursting Walker"))
        pack(57, (112, 176, "Heaped Abomination"), (116, 172, "Exclusion Ogre"))
        pack(57, (100, 182, "Bursting Walker"), (104, 180, "Exclusion Ogre"))
        pack(57, (100, 146, "Heaped Abomination"), (100, 150, "Exclusion Ogre"))          # the south spoke
        # THE RIM, south-west
        pack(57, (*rp(120), "Heaped Abomination"), (*rp(122), "Bursting Walker"))
        pack(58, (*rp(150), "Exclusion Ogre"), (*rp(152), "Heaped Abomination"))
        # THE BROOD
        pack(58, (36, 118, "Brood Seepwidow"), (40, 112, "Brood Hatchling Swarm"), (34, 114, "Brood Seepwidow"))
        pack(58, (36, 86, "Brood Seepwidow"), (40, 90, "Brood Burrower"), (32, 84, "Brood Hatchling Swarm"))
        pack(58, (18, 116, "Brood Hatchling Swarm"), (20, 112, "Brood Seepwidow"))
        pack(58, (60, 100, "Brood Burrower"), (56, 100, "Brood Seepwidow"))                # the west spoke
        # THE RIM, north-west
        pack(58, (*rp(205), "Brood Burrower"), (*rp(207), "Brood Seepwidow"))
        pack(58, (*rp(240), "Hollow Guardian"), (*rp(242), "Brood Burrower"))
        # THE STACKS: along the rim's line and down the aisles
        pack(59, (78, 30, "Archive Wraith"), (82, 32, "Swarming Pages"), (76, 34, "Hollow Guardian"))
        pack(59, (122, 30, "Archive Anomaly"), (118, 32, "Swarming Pages"), (124, 34, "Archive Wraith"))
        pack(59, (100, 30, "Hollow Guardian"), (96, 26, "Archive Wraith"), (104, 26, "Archive Anomaly"))
        pack(59, (100, 60, "Swarming Pages"), (100, 56, "Archive Wraith"))                 # the north spoke
        # THE RIM, north-east
        pack(59, (*rp(300), "Archive Wraith"), (*rp(302), "Archive Anomaly"))
        pack(59, (*rp(330), "Hollow Guardian"), (*rp(332), "Swarming Pages"))
        # THE HANGING CARS: things roost in the cages, and the archive's strays drift under them
        pack(59, (166, 92, "Brood Hatchling Swarm"), (170, 88, "Brood Seepwidow"), (164, 96, "Archive Anomaly"))
        pack(59, (180, 110, "Hollow Guardian"), (176, 114, "Brood Hatchling Swarm"), (184, 108, "Archive Wraith"))
        pack(59, (174, 100, "Archive Anomaly"), (170, 104, "Swarming Pages"))
        # THE OPEN SPOKE, and the axle's ring
        pack(59, (140, 100, "Hollow Guardian"), (136, 100, "Archive Wraith"))
        pack(59, (124, 100, "Archive Anomaly"), (120, 100, "Hollow Guardian"))
    elif name == HALL:
        # THE AXLE'S FOOT
        pack(59, (84, 12, "Bubbler Slagcrawler"), (96, 12, "Aged Volunteer"), (90, 16, "Bubbler Wyrm"))
        # THE TURBINE HALL: down both sides of the row of turbines
        pack(59, (18, 24, "Aged Volunteer"), (16, 30, "Bubbler Slagcrawler"), (20, 34, "Aged Volunteer"))
        pack(59, (42, 52, "Moment Without End"), (44, 58, "Aged Volunteer"), (40, 62, "Bubbler Slagcrawler"))
        pack(59, (18, 80, "Bubbler Wyrm"), (16, 86, "Bubbler Slagcrawler"), (20, 90, "Aged Volunteer"))
        pack(59, (42, 104, "Aged Volunteer"), (44, 110, "Moment Without End"), (40, 114, "Bubbler Wyrm"))
        pack(59, (30, 142, "Bubbler Slagcrawler"), (24, 140, "Aged Volunteer"), (36, 140, "Bubbler Wyrm"))
        # THE BUBBLER POOLS: round the pools and on the walkway between
        pack(59, (64, 120, "Bubbler Ooze"), (60, 126, "Bubbler Wyrm"), (62, 148, "Bubbler Ooze"))
        pack(59, (91, 122, "Bubbler Ooze"), (86, 126, "Bubbler Slagcrawler"), (96, 126, "Bubbler Ooze"))
        pack(59, (118, 120, "Bubbler Wyrm"), (122, 126, "Bubbler Ooze"), (120, 148, "Bubbler Slagcrawler"))
        # THE NINETY SECONDS: up the roof gallery, frozen where they stood
        pack(60, (150, 134, "Stopped Volunteer"), (146, 130, "Moment Without End"), (154, 130, "Aged Volunteer"))
        pack(60, (140, 108, "Stopped Volunteer"), (144, 104, "Stopped Volunteer"), (160, 110, "Moment Without End"))
        pack(60, (152, 84, "Moment Without End"), (148, 80, "Aged Volunteer"), (156, 80, "Stopped Volunteer"))
        pack(60, (160, 56, "Stopped Volunteer"), (156, 52, "Moment Without End"), (164, 52, "Aged Volunteer"))
        # THE BREACH, and the Lid
        pack(60, (112, 28, "Stopped Volunteer"), (116, 28, "Moment Without End"))
        pack(60, (82, 74, "Moment Without End"), (102, 74, "Stopped Volunteer"), (92, 80, "Aged Volunteer"))
    else:
        # THE SANDFALL
        pack(59, (62, 14, "Aged Volunteer"), (68, 10, "Bubbler Slagcrawler"), (84, 16, "Aged Volunteer"))
        # THE STEAM CORRIDOR: west, down, east, up
        pack(59, (40, 33, "Bubbler Slagcrawler"), (36, 30, "Moment Without End"), (44, 36, "Aged Volunteer"))
        pack(59, (14, 54, "Stopped Volunteer"), (12, 50, "Aged Volunteer"), (16, 58, "Bubbler Slagcrawler"))
        pack(60, (14, 90, "Moment Without End"), (12, 86, "Stopped Volunteer"), (16, 94, "Aged Volunteer"))
        pack(60, (40, 134, "Bubbler Slagcrawler"), (44, 136, "Moment Without End"), (36, 132, "Stopped Volunteer"))
        pack(60, (100, 134, "Aged Volunteer"), (104, 136, "Bubbler Slagcrawler"), (96, 132, "Moment Without End"))
        pack(60, (132, 112, "Stopped Volunteer"), (130, 116, "Moment Without End"), (134, 108, "Aged Volunteer"))
        pack(60, (132, 70, "Bubbler Slagcrawler"), (130, 66, "Stopped Volunteer"), (134, 74, "Moment Without End"))
        # THE LANDING
        pack(60, (104, 80, "Moment Without End"), (104, 88, "Stopped Volunteer"))
    return T


def _snap(zone, spots, rad=8):
    out = []
    for (x, y, m, lvl) in spots:
        if zone.is_walkable(x, y):
            out.append((x, y, m, lvl))
            continue
        best = min(((dx * dx + dy * dy, x + dx, y + dy) for dy in range(-rad, rad + 1) for dx in range(-rad, rad + 1)
                    if 0 <= x + dx < zone.width and 0 <= y + dy < zone.height and zone.is_walkable(x + dx, y + dy)),
                   default=None)
        if best is None:
            raise AssertionError(("trash with no floor within reach", zone.name, m, x, y))
        out.append((best[1], best[2], m, lvl))
    return out


def generate_floor(name):
    zone, _b = build_floor(name)
    from world.dungeon_packs import attach_packs
    avoid = list(FLOOR[name]["doors"]) + [tuple(b[:2]) for b in zone.boss_positions]
    packs = attach_packs(zone, [_snap(zone, p) for p in _trash(name)], avoid=avoid)
    TRASH[name] = [m for p in packs for m in p]
    from tools.handbuilt_vot_caves import register_baked
    register_baked(zone, BAKED[name])
    for (x, y) in zone.chest_spots:
        if zone.get_tile(x, y, "interaction") is None:
            zone.set_tile(x, y, "chest", "interaction")
    return zone


if __name__ == "__main__":
    for n in FLOORS:
        z, _b = build_floor(n)
        walk = sum(z.is_walkable(x, y) for y in range(z.height) for x in range(z.width))
        print(n, z.width, "x", z.height, "| walkable", walk, "| bosses", [b[2] for b in z.boss_positions])
