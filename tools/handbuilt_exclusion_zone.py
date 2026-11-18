"""
Hand-built THE EXCLUSION ZONE (200x200), levels 57-60: the dungeon under the wheel in Deadwind East, the last T0 token
dungeon (docs/deadwind_brief.md, docs/deadwind_quest_plan.md).

Kyle, 17-18 Nov 2026: "ONLY pripyat as the entrance to the fallout zone dungeon (We need one more dungeon with our last
T0 token - this is it)", and on the 18th he named it the Exclusion Zone. It's the rupture itself: Deadwind rock giving
way to fused flesh, glowing slag and stopped time, down to the wound. Six bosses; the Wound's Heart drops the T0
bracers token.

THE SHAPE: THE WHEEL'S SHADOW. The tear keeps a copy of everything that dies near it, and it kept a copy of the wheel.
Under the real one, the cavern has grown in the same shape: a rim, spokes and a hub. Nothing from Earth is down here,
only the shape. You climb down into the bottom of the rim and walk it the long way round, three quarters of the
circle, through the chambers where the gondolas would hang. The last quarter has fallen in. From the east chamber the
one open spoke runs straight in to the hub, and the Wound's Heart is in the hub.

    1 THE CRATER FLOOR     the rim's bottom, where you climb in: Deadwind rock, and Gristlemaw, a heap of the pass's
                           ogres moving as one body
    2 THE BROOD            the rim's west chamber: flesh and silk, egg pods bulging off it, Broodmother Vexis
    3 THE BUBBLER POOLS    the rim's north chamber: a hall of slag with the seep standing in two pools either side of
                           the way through, and the Glow-Eater, which is eating it and getting bigger
    4 THE STACKS           the rim's east chamber: black-glass shelving in rows, every moment the tear has kept filed
                           on them, and Archivist Nine, Karazhan's librarian at nine ages at once
    5 THE NINETY SECONDS   the east spoke, straight in toward the hub, every blast and scream along it stopped where
                           it was, and the Stopped Man in the middle of it
    6 THE ELEPHANT'S FOOT  the hub: a ring of the wound's own fluid round an island, and the Wound's Heart on it
    the dead spokes        the west, north and south spokes run in from their chambers and stop dead against stopped
                           time, where the volunteers who went down before you left their kits

THE NAMES ARE THE LIQUIDATORS'. The Forsaken call the place the Wound and its rooms by what's in them; the transplants
named the rooms after home, the way their parents' generation talked about Reactor Four:
  * the Bubbler Pools: under the reactor were the bubbler pools, and in May 1986 three men waded into the flooded
    basement in the dark to open the valves that drained them, so the core couldn't melt into the water and blow the
    rest of it apart. Halyna's father knew one of them.
  * the Ninety Seconds: the soldiers who cleared the graphite off the reactor roof by hand were given ninety seconds
    each, because that was all the dose a body could take. The liquidators work the stopped hall the same way, in
    timed shifts, and the Stopped Man is the one who stayed too long.
  * the Elephant's Foot: the mass of melted fuel, concrete and sand that ran down into the reactor's basement and
    set there, so hot that standing beside it for a few minutes was enough. Kenji gave the Wound's Heart the name the
    first time he saw it.
Nothing from Earth is down here: the names are only words, the way people carry home with them.

The way out is the door you came in by, or the fast exit in the hub's west side once the Heart is dead (Kyle, 16 Nov:
"make a fast exit from the dungeon to outside in the open world. prevents people from running back").

Trash comes in packs of four or five (world/dungeon_packs). The creatures, kits and loot are tools/build_deadwind_content.py.

HARD CONTRACTS (world/portal_manager.py)
  (100, 196) <-> Deadwind East's wheel (152, 93); (84, 100) -> Deadwind East (152, 93), one way
"""
import math

from world.tilemap import Tilemap
from tools.dungeon_builder import Builder

NAME = "The Exclusion Zone"
BAKED = "assets/tiles/fallout_zone/baked_exclusion_zone"
W, H = 200, 200
PORTAL = (100, 196)
FAST_EXIT = (84, 100)
C = (100, 100)
RIM_R = 72


def _rim_point(deg):
    """A point on the rim: 90 degrees is the bottom (screen y grows down), 180 the west, 270 the north, 360 the east.
    The rim breathes a little so it never reads as a compass circle."""
    a = math.radians(deg)
    r = RIM_R + 3.0 * math.sin(3 * a + 0.7) + 1.5 * math.sin(7 * a)
    return (C[0] + r * math.cos(a), C[1] + r * math.sin(a))


#: the rim, the long way round from the bottom to the east; the south-east quarter has fallen in
RIM = [_rim_point(d) for d in range(90, 361, 10)]

#: name -> ("rect", x0, y0, x1, y1, chamfer) or ("lobes", [(cx, cy, rx, ry)]): the floor, cut first
ROOMS = {
    "The Crater Floor": ("lobes", [(100, 172, 20, 12), (85, 178, 8, 6), (115, 177, 8, 6), (100, 184, 7, 6)]),
    "The Brood":        ("lobes", [(28, 100, 15, 19), (17, 85, 7, 6), (17, 116, 7, 6), (39, 89, 6, 5),
                                   (39, 112, 6, 5)]),
    "The Bubbler Pools":    ("rect", 76, 14, 124, 42, 5),
    "The Stacks":       ("rect", 158, 78, 188, 122, 3),
    "The Ninety Seconds": ("rect", 120, 96, 158, 104, 0),
    "The Elephant's Foot":        ("lobes", [(100, 100, 18, 16)]),
}
#: the seep, pooled (impassable, lava under the hood, painted as toxic water): (cx, cy, rx, ry)
POOLS = [
    (86, 28, 7, 9), (114, 28, 7, 9),            # the Bubbler Pools, either side of the way through
    (100, 100, 12, 10),                          # the ring round the Heart's island
    (24, 100, 4, 6),                             # the Brood's birthing pool behind Vexis
]
#: islands back over the seep: (cx, cy, rx, ry)
ISLANDS = [(100, 100, 6, 5)]
#: (points, width): the rim, the spokes, the bridge onto the Heart's island. _carve_path's width is about 2w + 1
PASSAGES = [
    ([PORTAL, (100, 184)], 2),                                  # the climb down into the crater
    (RIM, 2),                                                   # the rim, the long way round
    ([(122, 100), (105, 100)], 1),                              # the bridge onto the island, from the Ninety Seconds
    ([(83, 100), (95, 100)], 1),                                  # the island's back: the fast exit's ledge
    # the dead spokes: in from their chambers, ending against stopped time
    ([(40, 100), (66, 100)], 1),
    ([(100, 40), (100, 66)], 1),
    ([(100, 164), (100, 136)], 1),
]
#: the Stacks' shelving: rows of black glass, two tiles thick, with aisles between
SHELVES = [(x, y) for x in (164, 172, 180) for y in (84, 94, 106, 116)]

BOSS_LIST = [
    (100, 168, "Gristlemaw"),
    (24, 108, "Broodmother Vexis"),
    (100, 26, "The Glow-Eater"),
    (180, 100, "Archivist Nine"),
    (138, 100, "The Stopped Man"),
    (100, 100, "The Wound's Heart"),
]
BOSSES = {}
CHESTS = []
TRASH = []

FZ = "assets/tiles/dungeon_props/fz_"
#: Kyle's Exclusion Zone props (docs/deadwind_art_prompts.md sheet 7): (prop, x, base y, height, solid)
DRESSING = [
    # the crater floor: the collapsed supports you climb down past, the ogres' carcass heaps
    ("collapsed_support", 92, 186, 4, "core"), ("collapsed_support", 108, 186, 4, "core"),
    ("carcass_heap", 86, 176, 3, "core"), ("carcass_heap", 116, 174, 3, "core"), ("bone_altar", 100, 162, 3, "core"),
    # the rim west: the volunteers' things
    ("dead_kit", 52, 150, 3, False), ("barricade", 34, 132, 3, "core"), ("fume_vent", 44, 142, 3, "core"),
    # the brood: pods and sacs off every lobe
    ("flesh_sac", 17, 84, 3, "core"), ("open_pod", 17, 115, 3, "core"), ("flesh_sac", 39, 88, 3, "core"),
    ("open_pod", 39, 111, 3, "core"), ("flesh_pillar", 34, 100, 4, "core"), ("eye_cluster", 20, 92, 3, False),
    # the rim north-west
    ("rib_arch", 44, 52, 4, False), ("hanging_cage", 62, 34, 4, "core"),
    # the glow pits: slag heaped between the pools, crystals at the hall's corners
    ("slag_cluster", 84, 18, 3, "core"), ("slag_cluster", 116, 18, 3, "core"), ("crystal_pillar", 80, 40, 4, "core"),
    ("crystal_pillar", 120, 40, 4, "core"), ("slag_pool", 100, 38, 3, False),
    # the rim north-east
    ("glass_shard", 140, 36, 4, "core"), ("floating_ring", 156, 52, 4, False),
    # the stacks: the archive's stones at the ends of the aisles
    ("rune_stone", 162, 80, 3, "core"), ("rune_stone", 186, 120, 3, "core"), ("glass_shard", 186, 80, 3, "core"),
    ("air_tear", 162, 120, 4, False),
    # the stopped hall: every blast stopped where it was
    ("stopped_blast", 128, 98, 4, False), ("stopped_blast", 150, 103, 4, False), ("dead_kit", 146, 98, 3, False),
    # the dead spokes, ended against stopped time
    ("stopped_blast", 66, 101, 4, False), ("stopped_blast", 100, 67, 4, False), ("stopped_blast", 100, 137, 4, False),
    ("dead_kit", 60, 100, 3, False), ("dead_kit", 100, 62, 3, False), ("dead_kit", 100, 142, 3, False),
    # the heart
    ("heart_mass", 100, 98, 4, False), ("wound_pit", 92, 92, 3, False), ("sinew", 108, 108, 3, False),
]


def _dress(b):
    """Each prop's base pulled onto the nearest floor within three tiles (the seep's edge wanders)."""
    import os
    z = b.zone
    for (name, x, y, h, solid) in DRESSING:
        path = f"{FZ}{name}.png"
        if not os.path.exists(path):
            continue                          # a piece the sheet didn't have: the room reads without it
        spot = min(((dx * dx + dy * dy, x + dx, y + dy) for dy in range(-3, 4) for dx in range(-3, 4)
                    if z.is_walkable(x + dx, y + dy)), default=None)
        if spot is None:
            raise AssertionError(("prop with no floor within reach", name, x, y))
        b.prop(path, spot[1], spot[2], h, solid=solid, fraction=0.3)


def _seal_strays(zone):
    """Any floor the door can't walk to goes back to rock."""
    from collections import deque
    start = (PORTAL[0], PORTAL[1] - 1)
    seen, q = {start}, deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and 0 <= n[0] < W and 0 <= n[1] < H and zone.is_walkable(*n):
                seen.add(n)
                q.append(n)
    for y in range(H):
        for x in range(W):
            if (x, y) not in seen and zone.is_walkable(x, y):
                zone.collision_layer[y][x] = "rock"


def build_exclusion():
    zone = Tilemap(NAME, W, H,
                   "Under the wheel. The tear kept a copy of everything that died near it, the wheel too, and the "
                   "cavern has grown in its shape: a rim, spokes, and the wound at the hub.")
    zone.is_cave = True
    #: the parent open zone, which is also the encounter-table key
    zone.region = "Deadwind East"
    b = Builder(zone, wall_id="rock", floor_id="stone")
    for name, spec in ROOMS.items():
        if spec[0] == "rect":
            _k, x0, y0, x1, y1, ch = spec
            b.rect(x0, y0, x1, y1, chamfer=ch)
        else:
            b.lobes(spec[1])
    for pts, wdt in PASSAGES:
        b.corridor([(int(round(x)), int(round(y))) for (x, y) in pts], width=wdt)
    # THE SEEP OVER THE FLOOR, then the island and its bridges back over it
    b.lobes(POOLS, base="lava")
    b.lobes(ISLANDS)
    for pts, wdt in PASSAGES[2:4]:
        b.corridor(pts, width=wdt)
    for (x, y) in SHELVES:
        for yy in range(y, y + 4):
            for xx in range(x, x + 2):
                zone.collision_layer[yy][xx] = "rock"

    for (px, py) in (PORTAL, FAST_EXIT):
        zone.collision_layer[py][px] = None
    zone.collision_layer[PORTAL[1] - 1][PORTAL[0]] = None
    _seal_strays(zone)
    _dress(b)
    _seal_strays(zone)

    fixed = []
    for (x, y, n) in BOSS_LIST:
        if not zone.is_walkable(x, y):
            raise AssertionError(("boss standing in rock or seep", n, x, y))
        fixed.append((x, y, n))
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = BOSS_LIST[-1][:2]
    zone.boss_positions = list(fixed)

    chests = [(115, 180), (17, 116), (64, 100), (100, 64), (186, 116), (100, 140), (40, 60)]
    CHESTS[:] = [c for c in chests if zone.is_walkable(*c)]

    zone.add_subzone(NAME, 0, 0, W, H)
    for name, spec in ROOMS.items():
        if spec[0] == "rect":
            _k, x0, y0, x1, y1, _c = spec
            zone.add_subzone(name, x0 - 3, y0 - 3, x1 - x0 + 7, y1 - y0 + 7)
        else:
            lobes = spec[1]
            x0 = min(cx - rx for (cx, cy, rx, ry) in lobes)
            x1 = max(cx + rx for (cx, cy, rx, ry) in lobes)
            y0 = min(cy - ry for (cx, cy, rx, ry) in lobes)
            y1 = max(cy + ry for (cx, cy, rx, ry) in lobes)
            zone.add_subzone(name, x0 - 2, y0 - 2, x1 - x0 + 4, y1 - y0 + 4)
    return zone, b


def _trash():
    """Hand-placed, round the rim from the crater. Each pack(...) is one pull, filled to four or five beside itself."""
    T = []

    def pack(lvl, *spots):
        T.append([(x, y, m, lvl) for (x, y, m) in spots])

    rp = lambda d, off=0: tuple(int(round(v)) for v in _rim_point(d + off))     # noqa: E731
    # THE CRATER FLOOR: what's left of Grosh'gok's ogres, and what they turned into
    pack(57, (88, 176, "Exclusion Ogre"), (92, 178, "Exclusion Ogre"), (90, 172, "Bursting Walker"))
    pack(57, (112, 176, "Heaped Abomination"), (116, 172, "Exclusion Ogre"))
    pack(57, (100, 182, "Bursting Walker"), (104, 180, "Exclusion Ogre"))
    # THE RIM, south-west
    pack(57, (*rp(120), "Heaped Abomination"), (*rp(122), "Bursting Walker"))
    pack(58, (*rp(140), "Exclusion Ogre"), (*rp(142), "Heaped Abomination"))
    # THE BROOD
    pack(58, (36, 118, "Brood Seepwidow"), (40, 112, "Brood Hatchling Swarm"), (34, 114, "Brood Seepwidow"))
    pack(58, (36, 86, "Brood Seepwidow"), (40, 90, "Brood Burrower"), (32, 84, "Brood Hatchling Swarm"))
    pack(58, (18, 116, "Brood Hatchling Swarm"), (20, 112, "Brood Seepwidow"))
    pack(58, (60, 100, "Brood Burrower"), (56, 100, "Brood Seepwidow"))                # the west spoke
    # THE RIM, north-west
    pack(58, (*rp(210), "Bubbler Slagcrawler"), (*rp(212), "Brood Burrower"))
    pack(58, (*rp(232), "Bubbler Wyrm"), (*rp(234), "Bubbler Slagcrawler"))
    # THE GLOW PITS
    pack(59, (80, 20, "Bubbler Slagcrawler"), (80, 26, "Bubbler Ooze"), (82, 34, "Bubbler Wyrm"))
    pack(59, (120, 20, "Bubbler Wyrm"), (120, 26, "Bubbler Slagcrawler"), (118, 34, "Bubbler Ooze"))
    pack(59, (100, 40, "Bubbler Ooze"), (96, 38, "Bubbler Slagcrawler"))
    pack(59, (100, 60, "Bubbler Wyrm"), (100, 56, "Bubbler Ooze"))                     # the north spoke
    # THE RIM, north-east
    pack(59, (*rp(300), "Archive Wraith"), (*rp(302), "Archive Anomaly"))
    pack(59, (*rp(322), "Hollow Guardian"), (*rp(324), "Archive Wraith"))
    # THE STACKS: down the aisles
    pack(59, (168, 84, "Swarming Pages"), (168, 90, "Archive Wraith"), (176, 86, "Hollow Guardian"))
    pack(59, (168, 112, "Swarming Pages"), (176, 114, "Archive Anomaly"), (168, 118, "Hollow Guardian"))
    pack(59, (184, 88, "Swarming Pages"), (184, 112, "Archive Wraith"))
    # THE STOPPED HALL
    pack(60, (154, 99, "Stopped Volunteer"), (154, 102, "Moment Without End"), (156, 100, "Aged Volunteer"))
    pack(60, (126, 99, "Moment Without End"), (124, 102, "Stopped Volunteer"))
    # THE SOUTH SPOKE (from the crater)
    pack(57, (100, 146, "Heaped Abomination"), (100, 150, "Exclusion Ogre"))
    return T


def _snap(zone, spots, rad=8):
    out = []
    for (x, y, m, lvl) in spots:
        if zone.is_walkable(x, y):
            out.append((x, y, m, lvl))
            continue
        best = None
        for r in range(1, rad + 1):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < zone.width and 0 <= ny < zone.height and zone.is_walkable(nx, ny):
                        d = dx * dx + dy * dy
                        if best is None or d < best[0]:
                            best = (d, nx, ny)
            if best:
                break
        if best is None:
            raise AssertionError(("trash with no floor within reach", m, x, y))
        out.append((best[1], best[2], m, lvl))
    return out


def build_exclusion_baked():
    return build_exclusion()


def generate_exclusion_zone():
    zone, _b = build_exclusion()
    from world.dungeon_packs import attach_packs
    avoid = [PORTAL, FAST_EXIT] + [tuple(b[:2]) for b in zone.boss_positions]
    packs = attach_packs(zone, [_snap(zone, p) for p in _trash()], avoid=avoid)
    TRASH[:] = [m for p in packs for m in p]
    from tools.handbuilt_vot_caves import register_baked
    register_baked(zone, BAKED)
    return zone


if __name__ == "__main__":
    from collections import deque
    z, _ = build_exclusion()
    start = (PORTAL[0], PORTAL[1] - 2)
    seen, q = {start}, deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and z.is_walkable(*n):
                seen.add(n)
                q.append(n)
    walk = sum(z.is_walkable(x, y) for y in range(H) for x in range(W))
    print(z.name, W, "x", H, "| walkable", walk, "| reached", len(seen),
          "| bosses reached", all(tuple(b[:2]) in seen for b in z.boss_positions),
          "| fast exit reached", FAST_EXIT in seen)
