"""
Hand-built Serena's Hollow (60x55): a harpy roost in a winding cliff gorge, Dry Hills, Northern Barrens.

ARCHETYPE: THE CLIFF GORGE (a climb, not a hall-chain).  Not a spiral, wheel, river loop, rotunda, C-warren
or switchback.  One long narrow gorge twists north in an S-curve from the cave mouth up to the roost; ledge
NESTS hang off its walls as side alcoves.  Halfway up the gorge BRAIDS round a standing pillar of rock
(a west arm and the main bed, rejoining above it), so the middle of the climb can be run two ways; a high
east ledge hides the pinned rare.  The roost is a wide nest bowl at the top - the one place the cliff opens
out.

  Mouth (30,48) -> gorge S-bend -> NEST LEDGES (east alcove) -> the braid (W arm | main) ->
  gorge N-bend -> Skreeva's high ledge (E) | -> THE ROOST (Harpy Matriarch)

Single-boss cave => TRASH IS RANDOM (zone.fixed_spawns = False; encounters.json caves["Serena's Hollow"]).
Boss: Harpy Matriarch (roost).  Pinned rare: Windcaller Skreeva (high ledge).

HARD CONTRACTS (world/portal_manager.py): portal (30,48) <-> Northern Barrens (60,150); arrival = 2 north.
Prop rule (Kyle): less is more; logical for the room; a few centrepieces.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

BP = "assets/tiles/barrens/props/"
BAKED = "assets/tiles/serenas_hollow/baked"
W, H = 60, 55
PORTAL = (30, 48)

PATHS = {
    "mouth":    ([(30, 48), (30, 45), (29, 42)], 5.0, 5.0),
    "gorge_s":  ([(29, 42), (24, 38), (20, 33)], 4.6, 4.6),
    "braid_w":  ([(20, 33), (12, 30), (10, 24), (15, 19), (24, 18)], 3.8, 3.8),       # west arm
    "braid_m":  ([(20, 33), (22, 28), (26, 23), (30, 19)], 4.4, 4.4),                  # main bed
    "gorge_n":  ([(28, 18), (36, 16), (41, 12), (38, 9)], 4.8, 5.4),
    "ledge_a":  ([(26, 40), (32, 39), (37, 38)], 3.0, 3.0),                            # east nest alcove tube
    "ledge_b":  ([(37, 15), (43, 19), (48, 23)], 3.0, 3.0),                            # climb to Skreeva's ledge
    "w_nest":   ([(11, 27), (7, 27)], 3.0, 3.0),
}
ROOMS = {
    "mouth":   (30, 47, 8, 4.5, 0, 0.4, "The Hollow Mouth"),
    "nest_a":  (40, 38, 5.5, 3.8, 0, 1.1, "The Lower Nests"),
    "nest_w":  (7, 25, 4.5, 4.0, 0, 2.0, "The Feather Ledge"),
    "ledge":   (49, 25, 6, 4.2, 0, 0.7, "Skreeva's Perch"),
    "roost":   (31, 8, 17, 6.5, 0, 2.6, "The Roost"),
}
PILLAR = (18, 25, 3.0, 4.2)         # the rock pillar the gorge braids round (cx, cy, rx, ry)

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


def build_serenas_hollow():
    zone = Tilemap("Serena's Hollow", W, H,
                   "A harpy roost at the head of a winding cliff gorge, thick with old nests.")
    zone.is_cave = True
    zone.region = "Northern Barrens"
    zone.fixed_spawns = False
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b

    for i, (key, (pts, w0, w1)) in enumerate(PATHS.items()):
        tube(b, pts, w0, w1, ph=0.5 + i * 0.9)
    for key, (cx, cy, rx, ry, rot, ph, _n) in ROOMS.items():
        cavern(b, cx, cy, rx, ry, rot, ph)
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

    bosses = [(31, 7, "Harpy Matriarch"), (49, 25, "Windcaller Skreeva")]
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
    for (x, y) in ((42, 38), (6, 24), (22, 10), (44, 8)):
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        chests.append(p)
    CHESTS[:] = chests
    for c in chests:
        L.mark("chest", *c)

    zone.add_subzone("Serena's Hollow", 0, 0, W, H)       # cave table key first; named rooms re-registered on top
    for key, (cx, cy, rx, ry, rot, ph, name) in ROOMS.items():
        zone.add_subzone(name, int(cx - rx - 2), int(cy - ry - 2), int(2 * rx + 4), int(2 * ry + 4))
    return zone, L


def finish(zone, L):
    targets = [PORTAL] + [(x, y) for (x, y) in BOSSES.values()] + list(CHESTS)
    return L.finish(targets)


def dress(zone, L):
    P = L.prop
    R = ROOMS
    # ---- mouth: bones at the threshold, a vulture-pecked kill
    P("vot_beast_ribcage", 26, 49, 3)
    P("den_leg_bones", 35, 49, 2)
    P("skull_pile", 34, 45, 2)
    # ---- lower nests (east alcove)
    nx, ny = R["nest_a"][:2]
    P("nb_harpy_eyrie", nx - 1, ny + 1, 4, where=BP)
    P("den_leg_bones", nx - 3, ny + 2, 2)
    P("den_eggshell_pile", nx + 4, ny - 1, 2)
    # ---- the gorge: a nest on a shelf, a stalagmite spur
    P("nb_harpy_eyrie", 23, 39, 4, where=BP)
    P("nb_guano_needle", 25, 36, 7, where=BP, solid="core")
    # ---- west arm + feather ledge
    P("nb_feather_charms", 11, 21, 5, where=BP)
    P("den_leg_bones", 8, 27, 2)
    P("skull_pile", 5, 23, 2)
    # ---- the braid: bones where prey was dropped
    P("den_leg_bones", 24, 28, 2)
    P("den_stalagmites", 14, 18, 4, solid="core")
    # ---- Skreeva's perch: a windcaller's totem
    sx, sy = R["ledge"][:2]
    P("nb_harpy_totem", sx - 5, sy - 2, 8, where=BP, solid="core", avoid=1)
    P("nb_harpy_eyrie", sx + 3, sy + 2, 4, where=BP)
    P("den_leg_bones", sx - 2, sy + 3, 2)
    # ---- north bend
    P("nb_guano_ledge", 34, 13, 4, where=BP)
    P("den_rock_rubble", 40, 14, 2)
    # ---- the roost: nest mounds round the matriarch's perch
    rx_, ry_ = R["roost"][:2]
    P("den_nest_mound", rx_, ry_ - 3, 6, solid="core", avoid=1)
    P("nb_harpy_eyrie", rx_ - 12, ry_ + 2, 4, where=BP)
    P("nb_harpy_eyrie", rx_ + 10, ry_ + 3, 4, where=BP)
    P("vot_beast_ribcage", rx_ + 5, ry_ + 4, 3)
    P("skull_pile", rx_ - 13, ry_ - 2, 2)
    P("den_eggshell_pile", rx_ + 12, ry_ - 1, 2)
    P("den_leg_bones", rx_ + 1, ry_ + 5, 2)
    return zone, L


def generate_serenas_hollow():
    zone, L = build_serenas_hollow()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_serenas_hollow_baked():
    """(zone, layout) with props + QA done - what the baker paints from."""
    zone, L = build_serenas_hollow()
    dress(zone, L)
    finish(zone, L)
    return zone, L
