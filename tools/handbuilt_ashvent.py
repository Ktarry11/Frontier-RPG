"""
Hand-built The Ashvent (96x84), level 30-32: a lava tube in the flank of Stonetalon Peak (docs/stonetalon_brief.md).

ARCHETYPE: THE BRAIDED TUBE. Windshear Mine is a ring round a pillar; this is a river of rock that set. A lava
tube is one long sinuous tunnel, and where the flow split round something harder and came back together it left
a braid: two channels side by side with a wall of rock between them. You go in at the top, follow the tube down
into the mountain, choose a channel at each braid, and come out at the bottom where the last of the heat still
pools under the crust.

  Mouth (48,80) -> THE UPPER TUBE (winding north-west) -> THE FIRST BRAID (two channels round a rock spine)
  -> THE SKYLIGHT (a roof collapse; daylight and ash fall onto the floor; side lobe: THE ASH MOTHER'S HOLLOW)
  -> THE SECOND BRAID -> THE CRUST (the bottom: a cooling lava pool under a skin of rock). Magmacore.

Two bosses: Magmacore at the Crust (the end) and the Ash Mother in her hollow off the Skylight (optional).
Trash is random from the cave's table.

HARD CONTRACTS (world/portal_manager.py): portal (48,80) <-> Stonetalon West (150,40); arrival = 2 north.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

ASP = "assets/tiles/aspen/props/"
STP = "assets/tiles/stonetalon/props/"
BAKED = "assets/tiles/stonetalon/baked_ashvent"
W, H = 96, 84
PORTAL = (48, 80)

PATHS = {
    "upper":    ([(48, 80), (46, 72), (38, 66), (28, 64), (20, 58)], 5.0, 5.5),
    # the first braid: two channels round a spine of rock
    "braid1_n": ([(20, 58), (18, 48), (24, 40), (34, 36)], 4.0, 4.0),
    "braid1_s": ([(20, 58), (30, 52), (36, 44), (34, 36)], 4.0, 4.0),
    "to_sky":   ([(34, 36), (44, 32), (52, 30)], 5.0, 5.5),
    "mother":   ([(52, 30), (50, 20), (44, 12)], 3.5, 3.5),
    # the second braid
    "braid2_n": ([(58, 30), (66, 22), (76, 24), (82, 32)], 4.0, 4.0),
    "braid2_s": ([(58, 30), (66, 38), (76, 38), (82, 32)], 4.0, 4.0),
    "to_crust": ([(82, 32), (84, 44), (80, 56), (72, 62)], 5.0, 6.0),
}
ROOMS = {
    "mouth":    (48, 77, 8, 4, 0, 0.4, "The Mouth"),
    "skylight": (54, 30, 9, 7, 0, 1.4, "The Skylight"),
    "mother":   (42, 11, 8, 6, 0, 2.2, "The Ash Mother's Hollow"),
    "crust":    (66, 66, 16, 9, 10, 0.9, "The Crust"),
}
SPINES = [(28, 46, 4.0, 5.0), (70, 30, 6.0, 3.0)]   # the rock the flow split round, one per braid

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


def build_ashvent():
    zone = Tilemap("The Ashvent", W, H,
                   "A lava tube in the flank of Stonetalon Peak. The flow set into stone years ago; the heat at the "
                   "bottom hasn't left.")
    zone.is_cave = True
    zone.region = "Stonetalon West"
    zone.fixed_spawns = False
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b
    for i, (key, (pts, w0, w1)) in enumerate(PATHS.items()):
        tube(b, pts, w0, w1, ph=0.6 + i * 0.7)
    for key, (cx, cy, rx, ry, rot, ph, _n) in ROOMS.items():
        cavern(b, cx, cy, rx, ry, rot, ph)
    for (px_, py_, prx, pry) in SPINES:
        for y in range(int(py_ - pry) - 1, int(py_ + pry) + 2):
            for x in range(int(px_ - prx) - 1, int(px_ + prx) + 2):
                if ((x - px_) / prx) ** 2 + ((y - py_) / pry) ** 2 <= 1.0:
                    zone.collision_layer[y][x] = "wall"
                    zone.set_tile(x, y, "rock", "collision")
    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    bosses = [(68, 66, "Magmacore"), (42, 10, "The Ash Mother")]
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
    for (x, y) in ((18, 50), (78, 22), (56, 68)):
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        chests.append(p)
    CHESTS[:] = chests
    for c in chests:
        L.mark("chest", *c)

    def sub(name, x, y, rx, ry):
        zone.add_subzone(name, int(x - rx), int(y - ry), int(2 * rx), int(2 * ry))
    zone.add_subzone("The Ashvent", 0, 0, W, H)
    for key, (cx, cy, rx, ry, rot, ph, name) in ROOMS.items():
        sub(name, cx, cy, rx + 2, ry + 2)
    return zone, L


def finish(zone, L):
    targets = [PORTAL] + [(x, y) for (x, y) in BOSSES.values()] + list(CHESTS)
    return L.finish(targets)


def dress(zone, L):
    P = L.prop
    R = ROOMS
    # ---- the mouth
    P("st_obsidian_boulder", 42, 76, 3, where=STP, solid="core")
    P("st_pumice_pile", 54, 76, 3, where=STP, solid="core")
    # ---- the upper tube: steam where the floor is thin
    P("st_steam_vents", 32, 64, 3, where=STP)
    P("den_rock_rubble", 24, 60, 2)
    # ---- the skylight: ash and a dead tree that came down through the roof
    sx, sy = R["skylight"][:2]
    P("asp_snag_charred", sx - 6, sy - 2, 6, where=ASP, solid="core")
    P("st_pumice_pile", sx + 6, sy + 3, 3, where=STP, solid="core")
    # ---- the Ash Mother's hollow
    mx, my = R["mother"][:2]
    P("st_fumarole", mx - 4, my + 2, 4, where=STP, solid="core")
    P("st_steam_vents", mx + 5, my + 2, 3, where=STP)
    # ---- the second braid
    P("st_obsidian_boulder", 64, 22, 3, where=STP, solid="core")
    P("st_steam_vents", 74, 40, 3, where=STP)
    # ---- the crust: the last heat in the mountain
    cx, cy = R["crust"][:2]
    P("st_cinder_cone", cx - 10, cy - 3, 5, where=STP, solid="core")
    P("st_fumarole", cx + 11, cy - 2, 4, where=STP, solid="core")
    P("st_obsidian_boulder", cx + 8, cy + 6, 3, where=STP, solid="core")
    P("st_steam_vents", cx - 6, cy + 6, 3, where=STP)
    return zone, L


def generate_ashvent():
    zone, L = build_ashvent()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_ashvent_baked():
    zone, L = build_ashvent()
    dress(zone, L)
    finish(zone, L)
    return zone, L
