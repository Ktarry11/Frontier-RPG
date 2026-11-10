"""
Hand-built The Emberdeep (170x180): inside the volcano. SEVEN BOSSES, island hopping.

Kyle, 10 Nov: the volcano dungeon is "almost like 'island hopping' style", the islands are
"platforms in a lava lake", and - after two wrong turns - "can we keep it volcano shaped? ...
I still want islands. Don't forget you enter from the NORTH and go south."

=========================================================================================
THE THREE THINGS THIS MAP IS, AND THE TWO WAYS I GOT THEM WRONG
=========================================================================================

1. IT IS VOLCANO SHAPED. The playable space is a ROUND CALDERA - one circular lava lake with
   solid rock outside it. An earlier build made it a rectangle cut by a grid of lava rivers,
   which gave plenty of land and looked like a circuit board. A volcano's inside is a bowl.

2. IT IS ISLANDS, and they are BIG. Kyle on the first attempt: "There is not enough landmass
   and too much lava!" The islands here are 24-44 tiles across, which is room to actually fight
   a 55-58 boss on rather than the rafts the first build had. The lava between them is what
   makes each one a commitment; the lava is not the floor.

3. YOU ENTER FROM THE NORTH AND GO SOUTH. The door is cut into the volcano's north face (see
   handbuilt_ashen_reach), so the entrance platform is at the TOP of this map and the Caldera
   Floor - the last fight, and the biggest island - is at the BOTTOM.

THE CHAIN, north to south:

    north door -> 1 Cinderhound -> 2 Thrass -> 4 The Serpent -> 5 Ysmel -> 7 The Caldera
                               \\-> 3 Vok    ->/        \\-> 6 The Mountain's Heart (optional)

Island 1 forks west and east, and the two sides rejoin at the Coil - so the first half can be
run in either order, and both halves have to be cleared to get south.

The lava is REAL collision - b.lobes(base="lava"), the same call Taragaman's lake in Ragefire
Chasm uses - so the causeways are the only floor between islands. NOTE that
b.corridor(base="lava") does NOT block: it carves walkable floor and merely tags it, which is
how an earlier build ended up with lava rivers that painted perfectly and stopped nothing.

EVERY BOSS TEACHES SOMETHING, and after Khaz Varun taught the stats separately this is where
they get asked for together:
    1 Pack-Alpha Cinderhound  stacks a buff every hit  -> a long fight is a lost fight
    2 Thrass                  all_enemies on a cycle   -> a healing check with a clock
    3 Basalt Guardian Vok     armour AND dodge         -> expertise AND armour penetration
    4 The Molten Serpent      damage becomes its shield while submerged -> stop attacking
    5 Flame Oracle Ysmel      flattens resistances to your weakest, rolls maximum
    7 The Caldera             the volcano itself gets up

HARD CONTRACTS (world/portal_manager.py)
  (85, 6) <-> The Ashen Reach (115, 132)   the door in the volcano's NORTH face
"""
from world.tilemap import Tilemap
from tools.dungeon_builder import Builder

BAKED = "assets/tiles/emberdeep/baked"
W, H = 170, 180
#: NORTH. The door is on the volcano's north face, so the run starts at the top and descends.
PORTAL = (85, 6)

#: The caldera: one round bowl of lava with solid rock outside it. This is the "volcano shaped"
#: requirement, and it is a single ellipse on purpose - no rivers, no grid, no cleverness.
CALDERA = (85, 96, 80, 82)

#: (name, [lobes], required). BIG islands. Shapes vary so no two fights feel the same, but every
#: one is a readable blob or ridge rather than a pattern.
ISLANDS = {
    "The Landing Shelf":    [(85, 36, 22, 16), (68, 30, 10, 8), (102, 30, 10, 8)],
    "Thrass's Steam":       [(42, 64, 20, 16), (58, 54, 11, 9)],        # west
    "The Basalt Shelf":     [(128, 66, 21, 17), (112, 56, 11, 9)],      # east
    "The Serpent's Coil":   [(72, 100, 26, 14), (48, 96, 13, 11),
                             (96, 104, 13, 11)],                        # a long ridge, mid-map
    "The Oracle's Ring":    [(128, 126, 22, 18)],                       # south-east, lava heart
    "The Mountain's Heart": [(34, 128, 17, 14)],                        # south-west, optional
    "The Caldera Floor":    [(85, 156, 28, 18), (60, 144, 13, 11),
                             (110, 144, 13, 11)],                       # the arena, at the bottom
}
#: The hole in the Oracle's Ring, painted back to lava AFTER its island. You cannot cross it,
#: only go round, and Ysmel stands on the near arc.
RING_HOLE = (128, 130, 10, 8)

#: (points, width) in chain order, north to south. Width varies because the crossing IS the
#: fight: a five-tile basalt road and a three-tile rib are different experiences.
#:
#: EVERY END SITS ON A LOBE CENTRE, never on a rim. Ends on the rim stranded five of seven bosses
#: in an earlier build - the same mistake Drywhisker shipped with - and the map looked fine.
#: WIDTH 3 IS THE FLOOR for anything long or curved: at 2 the corridor spline's own breathing
#: pinches a causeway shut mid-span while still drawing it.
CAUSEWAYS = [
    ([(85, 8), (85, 22), (85, 36)], 5),                     # the door onto the landing shelf
    ([(85, 36), (68, 44), (56, 54), (42, 64)], 3),          # 1 -> 2, south-west
    ([(85, 36), (104, 44), (114, 56), (128, 66)], 3),       # 1 -> 3, south-east
    ([(42, 64), (46, 80), (50, 96), (72, 100)], 3),         # 2 -> 4
    ([(128, 66), (120, 84), (104, 96), (94, 104)], 3),      # 3 -> 4
    ([(94, 104), (110, 114), (128, 126)], 4),               # 4 -> 5
    ([(50, 96), (42, 112), (34, 128)], 3),                  # 4 -> 6, the optional spur
    ([(128, 126), (108, 142), (85, 156)], 4),               # 5 -> 7, into the arena
]

#: Stepping stones: single rocks off the thread, each one a chest. Reachable, but only by
#: standing somewhere with lava on three sides.
STEPPING = [(28, 38, 6, 5), (144, 36, 6, 5), (22, 92, 6, 5), (152, 98, 6, 5), (85, 128, 7, 6)]
STEP_LINKS = [
    ([(85, 36), (56, 36), (28, 38)], 2),
    ([(85, 36), (116, 36), (144, 36)], 2),
    ([(42, 64), (30, 78), (22, 92)], 2),
    ([(128, 66), (142, 82), (152, 98)], 2),
    ([(72, 100), (78, 114), (85, 128)], 2),
]

BOSSES = {}
CHESTS = []
TRASH = []

#: (x, y, name, required). On a ring the boss is NOT at the centre, so each is asserted walkable.
BOSS_LIST = [
    (85, 36, "Pack-Alpha Cinderhound", True),
    (42, 64, "Thrass, the Geyser Spirit", True),
    (128, 66, "Basalt Guardian Vok", True),
    (72, 100, "The Molten Serpent", True),
    (128, 114, "Flame Oracle Ysmel", True),      # the ring's north arc, outside the lava heart
    (34, 128, "The Mountain's Heart", False),
    (85, 156, "The Caldera", True),
]


def build_emberdeep():
    zone = Tilemap("The Emberdeep", W, H,
                   "Inside the volcano: a round caldera flooded with lava, islands of cooled "
                   "crust standing in it, and a thread of basalt causeways running south.")
    zone.is_cave = True
    #: The PARENT OPEN ZONE, which is also the encounter-table key. "Tempest Isle" is prose and
    #: names no zone, so a dungeon keyed to it would resolve no table at all.
    zone.region = "The Ashen Reach"
    b = Builder(zone, wall_id="wall", floor_id="stone")

    # THE LAKE FIRST, then everything laid back over it. Done the other way round the lava paints
    # over the platforms and the dungeon is one solid block of collision.
    b.lobes([CALDERA], base="lava")
    # the door platform, cut into the caldera's north rim
    b.rect(76, 2, 94, 14, chamfer=2, base="stone")

    for lobes in ISLANDS.values():
        b.lobes(lobes, base="stone")
    for (sx, sy, rx, ry) in STEPPING:
        b.lobes([(sx, sy, rx, ry)], base="stone")
    # the ring's lava heart, back over its island
    b.lobes([RING_HOLE], base="lava")
    for pts, wdt in CAUSEWAYS:
        b.corridor(pts, width=wdt)
    for pts, wdt in STEP_LINKS:
        b.corridor(pts, width=wdt)
    b.restyle(0, 0, W - 1, H - 1, wall="cliff")

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.collision_layer[py + 1][px] = None

    fixed = []
    for (x, y, n, _req) in BOSS_LIST:
        if not zone.is_walkable(x, y):
            raise AssertionError(("boss standing in lava or rock", n, x, y))
        fixed.append((x, y, n))
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (85, 156)
    zone.boss_positions = list(fixed)

    chests = [(28, 38), (144, 36), (22, 92), (152, 98), (85, 128), (64, 146), (106, 146)]
    CHESTS[:] = [c for c in chests if zone.is_walkable(*c)]

    zone.add_subzone("The Emberdeep", 0, 0, W, H)
    for name, lobes in ISLANDS.items():
        x0 = min(cx - rx for (cx, cy, rx, ry) in lobes)
        x1 = max(cx + rx for (cx, cy, rx, ry) in lobes)
        y0 = min(cy - ry for (cx, cy, rx, ry) in lobes)
        y1 = max(cy + ry for (cx, cy, rx, ry) in lobes)
        zone.add_subzone(name, int(x0 - 3), int(y0 - 3), int(x1 - x0 + 6), int(y1 - y0 + 6))
    zone.add_subzone("The Ember Gate", 74, 0, 22, 18)
    return zone, b


def _trash():
    """Hand-placed, north to south. A pull on a causeway over lava is the map's personality."""
    T = []

    def pack(lvl, *spots):
        for (x, y, m) in spots:
            T.append((x, y, m, lvl))

    pack(55, (85, 14, "Fire Sprite"), (80, 20, "Fire Sprite"), (90, 20, "Cinder Hound"))
    pack(55, (85, 28, "Cinder Hound"), (76, 32, "Fire Sprite"), (94, 32, "Cinder Hound"))
    pack(55, (68, 44, "Flame Elemental"), (60, 50, "Fire Sprite"), (52, 56, "Flame Elemental"))
    pack(55, (38, 58, "Steam Elemental"), (48, 68, "Geyser Spirit"), (40, 74, "Steam Elemental"))
    pack(56, (104, 44, "Ash Wraith"), (112, 52, "Ash Wraith"), (120, 60, "Obsidian Shardling"))
    pack(56, (134, 72, "Basalt Guardian"), (120, 76, "Obsidian Shardling"))
    pack(56, (46, 82, "Magma Elemental"), (50, 94, "Earth Elemental"))
    pack(56, (118, 86, "Magma Elemental"), (104, 96, "Earth Elemental"))
    pack(56, (62, 102, "Sulphur Crawler"), (82, 102, "Molten Serpent"), (94, 106, "Sulphur Crawler"))
    pack(57, (42, 112, "Earth Elemental"), (34, 120, "Basalt Guardian"))
    pack(57, (110, 114, "Ember Swarm"), (122, 120, "Flame Oracle"), (136, 120, "Ash Wraith"))
    pack(57, (128, 138, "Ember Swarm"), (116, 134, "Flame Oracle"))
    pack(58, (108, 142, "Smoke Drake"), (96, 150, "Smoke Drake"), (85, 142, "Lava Lord"))
    pack(58, (68, 154, "Magma Elemental"), (102, 154, "Magma Elemental"), (85, 168, "Lava Lord"))
    return T


def _snap(zone, spots, rad=8):
    """Pull any trash spot that landed in lava or rock out to the nearest walkable tile.

    Bosses are asserted walkable and fixed by hand - they are placed deliberately. Trash is a
    scatter, and on a map that is mostly lava a pack member landing a tile off a causeway is
    expected rather than a defect; what matters is that every mob can be fought.
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
