"""
Hand-built Windshear Mine (90x80), level 27-30: the Venture Co.'s dig under Windshear Crag (docs/stonetalon_brief.md).

ARCHETYPE: THE BREAKTHROUGH. Boulder Lode is switchback benches; this one is a ring. The goblins drove a straight
drift north into the crag, worked a ring of galleries round a pillar of bad rock they daren't touch, and then
blasted north once too often and broke into the bottom of a natural chimney that runs right up through the crag
to the sky. The wind comes down it, ash from the Blowdown comes down it, and so does anything that lives up top.

  Adit (45,76) -> THE DRIFT (north) -> THE RING (round the bad-rock pillar):
      west  THE SORTING CUT (ore sorted and carted)
      east  THE BLASTING GALLERY (powder, fuses, the charges that did it)  -> side adit NE: OLD PUMICE'S HOLLOW
  -> THE BREAKTHROUGH (north): the bottom of the chimney, ash on the floor, daylight from above. The driller.

Two bosses: Driller Mozzik in his drilling rig at the Breakthrough (the end) and Old Pumice, a pumice elemental
the blasting woke, pinned in its hollow (optional). Trash is random from the cave's table.

HARD CONTRACTS (world/portal_manager.py): portal (45,76) <-> Stonetalon East (188,44); arrival = 2 north.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

GP = "assets/tiles/goblin_shared/props/"
ASP = "assets/tiles/aspen/props/"
BAKED = "assets/tiles/stonetalon/baked_windshear_mine"
W, H = 90, 80
PORTAL = (45, 76)

PATHS = {
    "drift":    ([(45, 76), (45, 68), (44, 60), (45, 54)], 5.0, 5.5),
    "ring_w":   ([(45, 54), (32, 52), (24, 44), (26, 34), (36, 28), (45, 27)], 5.0, 5.0),
    "ring_e":   ([(45, 54), (58, 52), (66, 44), (64, 34), (54, 28), (45, 27)], 5.0, 5.0),
    "sorting":  ([(24, 44), (16, 44), (10, 46)], 4.0, 4.5),
    "blasting": ([(66, 44), (74, 42), (80, 40)], 4.0, 4.5),
    "pumice":   ([(78, 38), (80, 30), (78, 22)], 3.0, 3.5),
    "breach":   ([(45, 27), (45, 20), (44, 14)], 5.0, 6.0),
}
ROOMS = {
    "mouth":     (45, 72, 9, 4, 0, 0.4, "The Adit"),
    "sorting":   (12, 45, 8, 6, 0, 1.2, "The Sorting Cut"),
    "blasting":  (78, 42, 8, 5, 0, 2.1, "The Blasting Gallery"),
    "pumice":    (76, 18, 7, 5, 0, 0.7, "Old Pumice's Hollow"),
    "breach":    (44, 12, 16, 8, 0, 1.6, "The Breakthrough"),
}
PILLAR = (45, 40, 9.0, 6.5)        # the bad rock the ring goes round (cx, cy, rx, ry)

BOSSES = {}
CHESTS = []


def _near_walkable(zone, x, y, rad=4):
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            if zone.is_walkable(int(x) + dx, int(y) + dy):
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, int(x) + dx, int(y) + dy)
    return None if best is None else (best[1], best[2])


def build_windshear_mine():
    zone = Tilemap("Windshear Mine", W, H,
                   "The Venture Co.'s dig under Windshear Crag. They blasted once too often and broke into the bottom "
                   "of a chimney that runs up to the sky.")
    zone.is_cave = True
    zone.region = "Stonetalon East"
    zone.fixed_spawns = False
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b
    for i, (key, (pts, w0, w1)) in enumerate(PATHS.items()):
        tube(b, pts, w0, w1, ph=0.3 + i * 0.8)
    for key, (cx, cy, rx, ry, rot, ph, _n) in ROOMS.items():
        cavern(b, cx, cy, rx, ry, rot, ph)
    # the pillar of bad rock the ring goes round
    px_, py_, prx, pry = PILLAR
    for y in range(int(py_ - pry) - 1, int(py_ + pry) + 2):
        for x in range(int(px_ - prx) - 1, int(px_ + prx) + 2):
            if ((x - px_) / prx) ** 2 + ((y - py_) / pry) ** 2 <= 1.0:
                zone.collision_layer[y][x] = "wall"
                zone.set_tile(x, y, "rock", "collision")

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    bosses = [(44, 10, "Driller Mozzik"), (76, 17, "Old Pumice")]
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
    for (x, y) in ((10, 48), (82, 44), (56, 12)):
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        chests.append(p)
    CHESTS[:] = chests
    for c in chests:
        L.mark("chest", *c)

    def sub(name, x, y, rx, ry):
        zone.add_subzone(name, int(x - rx), int(y - ry), int(2 * rx), int(2 * ry))
    zone.add_subzone("Windshear Mine", 0, 0, W, H)      # the cave table key covers the whole map
    for key, (cx, cy, rx, ry, rot, ph, name) in ROOMS.items():
        sub(name, cx, cy, rx + 2, ry + 2)
    return zone, L


def finish(zone, L):
    targets = [PORTAL] + [(x, y) for (x, y) in BOSSES.values()] + list(CHESTS)
    return L.finish(targets)


def dress(zone, L):
    P = L.prop
    R = ROOMS
    # ---- the adit: the timber frame over the door, a cart left at the mouth
    P("gob_mine_frame", 45, 73, 8, where=GP, solid=False)
    P("rf_brazier", 39, 72, 3)
    P("rf_brazier", 51, 72, 3)
    P("gob_ore_cart", 40, 69, 4, where=GP)
    # ---- the drift: rails and a lamp
    P("gob_rail_stack", 48, 62, 3, where=GP, solid=False)
    P("den_torch", 41, 60, 4)
    # ---- the ring: the long way round the bad rock
    P("den_torch", 28, 48, 4)
    P("den_torch", 62, 48, 4)
    P("rf_supply_crates", 30, 32, 3)
    P("gob_ore_cart", 60, 32, 4, where=GP)
    P("den_rock_rubble", 52, 50, 2)
    # ---- the sorting cut
    sx, sy = R["sorting"][:2]
    P("gob_ore_pile", sx - 3, sy - 2, 3, where=GP)
    P("gob_ore_cart", sx + 2, sy + 2, 4, where=GP)
    P("rf_tool_rack", sx - 4, sy + 3, 3)
    # ---- the blasting gallery: what did it
    bx, by = R["blasting"][:2]
    P("gob_dynamite_crate", bx - 3, by - 1, 3, where=GP)
    P("gob_dynamite_crate", bx + 3, by + 2, 3, where=GP)
    P("rf_supply_crates", bx + 4, by - 2, 3)
    P("den_rock_rubble", bx - 4, by + 3, 2)
    # ---- Old Pumice's hollow: the rock the blasting cracked open
    qx, qy = R["pumice"][:2]
    P("den_rock_rubble", qx - 4, qy + 2, 3, solid="core")
    P("den_stalagmite_pair", qx + 4, qy, 4, solid="core")
    # ---- the breakthrough: the chimney's floor, ash and wind and daylight
    vx, vy = R["breach"][:2]
    P("asp_snag_charred", vx - 10, vy - 2, 6, where=ASP, solid="core")      # a dead tree that fell down the chimney
    P("asp_deadfall_pile", vx + 10, vy + 2, 4, where=ASP, solid="core")
    P("den_rock_rubble", vx - 6, vy + 5, 3)
    P("gob_dynamite_crate", vx + 5, vy + 6, 3, where=GP)
    P("rf_tool_rack", vx - 2, vy + 6, 3)
    return zone, L


def generate_windshear_mine():
    zone, L = build_windshear_mine()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_windshear_mine_baked():
    """(zone, layout) with props + QA done - what the baker paints from."""
    zone, L = build_windshear_mine()
    dress(zone, L)
    finish(zone, L)
    return zone, L
