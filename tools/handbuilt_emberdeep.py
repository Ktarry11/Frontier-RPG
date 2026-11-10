"""
Hand-built The Emberdeep (170x180): inside the volcano. SEVEN BOSSES, island hopping.

Kyle, 10 Nov: the volcano dungeon is "almost like 'island hopping' style", and the islands are
"platforms in a lava lake".

ARCHETYPE: A LAKE WITH STEPPING STONES. Khaz Varun is a city - squared halls and a street. This is
its opposite in every way: one enormous lava lake filling the caldera, seven islands of cooled
crust standing in it, and a thread of basalt causeways between them. The lava is REAL collision
(base="lava" blocks movement, the same as Taragaman's lake in Ragefire Chasm), so the causeways
are not decoration - they are the only floor there is.

THE CHAIN IS THE POINT. Each island connects only to the NEXT one, so the run is a thread rather
than a room with exits: you commit to an island as you land on it, and the way on is the only way
that is not lava. That is what makes it hopping instead of a corridor with gaps.

    gate -> 1 Cinderhound -> 2 Thrass -> 3 Vok -> 4 Serpent -> 5 Ysmel -> 7 The Caldera
                                                                    \\
                                                                     -> 6 The Mountain's Heart
                                                                        (optional, off-chain)

SIX OF SEVEN ARE ON THE CHAIN and one hangs off it, because bosses are allowed to be skippable but
a thread with holes in it stops being a thread.

EVERY BOSS TEACHES SOMETHING, and after Khaz Varun taught the stats separately this is where they
get asked for together:
    1 Pack-Alpha Cinderhound  stacks a buff every hit  -> a long fight is a lost fight
    2 Thrass                  all_enemies on a cycle   -> a healing check with a clock
    3 Basalt Guardian Vok     armour AND dodge         -> expertise AND armour penetration
    4 The Molten Serpent      damage becomes its shield while submerged -> stop attacking
    5 Flame Oracle Ysmel      flattens resistances to your weakest, rolls maximum
    7 The Caldera             the volcano itself gets up

HARD CONTRACTS (world/portal_manager.py)
  (85, 174) <-> The Ashen Reach (115, 132)   the door in the volcano's north face

Multi-boss, so trash is HAND-PLACED. Roughly 3-4 pulls between bosses, and on this map a "pull" is
usually a causeway, which is deliberate: fighting on a two-tile bridge over lava is the dungeon's
whole personality.
"""
from world.tilemap import Tilemap
from tools.dungeon_builder import Builder

BAKED = "assets/tiles/emberdeep/baked"
W, H = 170, 180
PORTAL = (85, 174)

#: (x, y, rx, ry, name, required). The seven crust islands. Sizes vary on purpose - the first
#: island is small enough to feel exposed and the last is a floor you can actually fight a giant on.
ISLANDS = [
    (85, 150, 13, 10, "The Landing Shelf", True),
    (42, 128, 12, 10, "Thrass's Steam", True),
    (124, 116, 13, 11, "The Basalt Shelf", True),
    (56, 90, 13, 10, "The Serpent's Coil", True),
    (116, 66, 13, 11, "The Oracle's Ring", True),
    (34, 52, 11, 9, "The Mountain's Heart", False),
    (88, 26, 18, 14, "The Caldera Floor", True),
]

#: The causeways, in chain order. WIDTH 3, not 2. At 2 the corridor spline's own breathing pinched
#: four of the seven shut somewhere mid-span - the same failure Drywhisker's ventilation shaft hit -
#: and five of the seven bosses came back unreachable while every bridge still LOOKED drawn. A
#: bridge you can be knocked off is the idea; a bridge with a hole in it is a broken dungeon.
CAUSEWAYS = [
    [(85, 168), (85, 160)],                    # the gate onto the first shelf
    [(74, 146), (66, 142), (58, 138), (50, 132)],              # 1 -> 2
    [(54, 122), (84, 120), (112, 118)],        # 2 -> 3
    [(114, 108), (100, 104), (88, 100), (76, 97), (66, 94)],   # 3 -> 4
    [(64, 80), (78, 77), (90, 74), (99, 72), (106, 70)],       # 4 -> 5
    [(106, 58), (88, 56), (72, 54), (58, 53), (44, 52)],       # 5 -> 6, optional spur
    [(112, 56), (100, 42), (90, 34)],          # 5 -> 7, the way on
]

BOSSES = {}
CHESTS = []
TRASH = []

#: (x, y, name, required)
BOSS_LIST = [
    (85, 150, "Pack-Alpha Cinderhound", True),
    (42, 128, "Thrass, the Geyser Spirit", True),
    (124, 116, "Basalt Guardian Vok", True),
    (56, 90, "The Molten Serpent", True),
    (116, 66, "Flame Oracle Ysmel", True),
    (34, 52, "The Mountain's Heart", False),
    (88, 26, "The Caldera", True),
]


def build_emberdeep():
    zone = Tilemap("The Emberdeep", W, H,
                   "Inside the volcano: a lava lake filling the caldera, islands of cooled crust "
                   "standing in it, and a thread of basalt causeways between them.")
    zone.is_cave = True
    #: The PARENT OPEN ZONE, which is also the encounter-table key. "Tempest Isle" is prose and
    #: names no zone, so a dungeon keyed to it would resolve no table at all.
    zone.region = "The Ashen Reach"
    b = Builder(zone, wall_id="wall", floor_id="stone")

    # THE LAKE FIRST, then the islands cut out of it. Done the other way round the lava paints
    # over the platforms and the whole dungeon is a solid block of collision.
    b.rect(8, 8, 162, 172, chamfer=10, base="sand")
    # THE LAKE HAS TO FILL THE CALDERA. At radius 74x78 a walkable ring of shore survived around
    # the outside of it, so the whole dungeon could be walked round the edge without ever using a
    # causeway - which deletes the only idea the map has. It reaches the rim now, and the only
    # floor in the lake is the islands and the thread between them.
    b.lobes([(84, 92, 84, 88)], base="lava")

    # the entrance hall, outside the lake
    b.rect(72, 162, 98, 176, chamfer=2, base="stone")

    for (cx, cy, rx, ry, _n, _req) in ISLANDS:
        b.lobes([(cx, cy, rx, ry)], base="stone")
    for pts in CAUSEWAYS:
        b.corridor(pts, width=3)
    b.restyle(6, 6, 164, 174, wall="cliff")

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.collision_layer[py - 1][px] = None

    fixed = []
    for (x, y, n, _req) in BOSS_LIST:
        if not zone.is_walkable(x, y):
            raise AssertionError(("boss standing in lava or rock", n, x, y))
        fixed.append((x, y, n))
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (88, 26)
    zone.boss_positions = list(fixed)

    chests = [(78, 152), (36, 124), (130, 112), (50, 86), (122, 62), (30, 48), (78, 22), (98, 22)]
    chests = [c for c in chests if zone.is_walkable(*c)]
    CHESTS[:] = chests

    zone.add_subzone("The Emberdeep", 0, 0, W, H)
    for (cx, cy, rx, ry, name, _req) in ISLANDS:
        zone.add_subzone(name, int(cx - rx - 3), int(cy - ry - 3),
                         int(rx * 2 + 6), int(ry * 2 + 6))
    zone.add_subzone("The Ember Gate", 70, 160, 30, 18)
    return zone, b


def _trash():
    """Hand-placed. On this map a pull is usually a CAUSEWAY, which is the point."""
    T = []

    def pack(lvl, *spots):
        for (x, y, m) in spots:
            T.append((x, y, m, lvl))

    pack(55, (85, 164, "Fire Sprite"), (80, 162, "Fire Sprite"), (90, 162, "Cinder Hound"))
    pack(55, (85, 156, "Cinder Hound"), (78, 152, "Fire Sprite"))
    # 1 -> 2, the first causeway
    pack(55, (74, 146, "Flame Elemental"), (62, 140, "Fire Sprite"), (52, 134, "Flame Elemental"))
    pack(55, (38, 132, "Steam Elemental"), (46, 124, "Geyser Spirit"))
    # 2 -> 3
    pack(56, (62, 121, "Ash Wraith"), (84, 120, "Ash Wraith"), (104, 119, "Flame Elemental"))
    pack(56, (128, 122, "Obsidian Shardling"), (118, 110, "Basalt Guardian"),
         (132, 110, "Obsidian Shardling"))
    # 3 -> 4
    pack(56, (104, 104, "Magma Elemental"), (84, 99, "Magma Elemental"), (70, 95, "Earth Elemental"))
    pack(56, (50, 94, "Molten Serpent"), (60, 84, "Sulphur Crawler"))
    # 4 -> 5
    pack(57, (70, 78, "Ember Swarm"), (90, 74, "Ember Swarm"), (102, 71, "Flame Elemental"))
    pack(57, (120, 72, "Flame Oracle"), (110, 60, "Ash Wraith"), (124, 60, "Ash Wraith"))
    # the optional spur, 5 -> 6
    pack(57, (88, 54, "Earth Elemental"), (62, 53, "Basalt Guardian"), (44, 52, "Earth Elemental"))
    # 5 -> 7, the way on
    pack(58, (108, 50, "Smoke Drake"), (98, 40, "Smoke Drake"), (90, 34, "Lava Lord"))
    pack(58, (76, 28, "Magma Elemental"), (100, 28, "Magma Elemental"), (88, 18, "Lava Lord"))
    return T


def _snap(zone, spots, rad=6):
    """Pull any trash spot that landed in lava or rock out to the nearest walkable tile.

    Bosses are asserted walkable and must be fixed by hand - they are placed deliberately. Trash
    is a scatter, and on a map that is three-quarters lava a pack member landing a tile off a
    causeway is expected rather than a defect; what matters is that every mob can be fought.
    """
    out = []
    for (x, y, m, lvl) in spots:
        if zone.is_walkable(x, y):
            out.append((x, y, m, lvl)); continue
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
            raise AssertionError(("trash with no walkable tile within reach", m, x, y))
        out.append((best[1], best[2], m, lvl))
    return out


def build_emberdeep_baked():
    """The map for the baker to paint from. See handbuilt_khaz_varun for why this is separate."""
    return build_emberdeep()


def generate_emberdeep():
    zone, _b = build_emberdeep()
    TRASH[:] = _snap(zone, _trash())
    zone.trash_spawns = list(TRASH)
    from tools.handbuilt_vot_caves import register_baked
    register_baked(zone, BAKED)
    return zone


if __name__ == "__main__":
    z, _ = build_emberdeep()
    print(z.name, z.width, "x", z.height, "| bosses", len(z.boss_positions))
