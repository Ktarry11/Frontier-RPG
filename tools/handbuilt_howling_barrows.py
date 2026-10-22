"""
Hand-built Howling Barrows (95x80): the frozen long barrow of the Kaldorei Wild Hunt, under the East's hills.

ARCHETYPE: THE LONG BARROW (a cross).  One straight, slightly bowed NAVE runs from the Frost Gate in the south to the Hall
of the Hunt-King in the north, with a wide CAIRN HEART where it is crossed by two TRANSEPTS: the Houndkeepers' Crypt (west,
where an old rare hound is chained) and the Hunters' Ossuary (east, bone-heaped chest room).  Past the Heart the nave narrows
into the Howling Gallery (a row of kneeling frozen hunters) and opens into the boss hall.  Burial alcoves bud off the nave.
(Broodspiral = spiral, RFK = warren wheel, Wailing = river ring, Moonwell = twin-bowl hourglass; this is the only cruciform.)

  Frost Gate (47,76) -> NAVE -> CAIRN HEART (47,50) -+- W: Houndkeepers' Crypt (rare Wintermaw)
                                                     '- E: Hunters' Ossuary (chests)
                          -> HOWLING GALLERY (47,34) -> HALL OF THE HUNT-KING (47,17): boss Hunt-King Valorin

Single-boss cave => TRASH IS RANDOM (zone.fixed_spawns = False; encounters.json Ashenvale East caves["Howling Barrows"]).
Boss: Hunt-King Valorin (L24).  Pinned rare: Wintermaw the Howling (L23, Houndkeepers' Crypt).  Zone: Ashenvale East 20-25.

HARD CONTRACTS (world/portal_manager.py): portal (47,76) <-> Ashenvale East (200,40); arrival = 2 north.
Prop rule (Kyle): less is more; logical for the room; a few centrepieces.
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

BAKED = "assets/tiles/howling_barrows/baked"
W, H = 95, 80
PORTAL = (47, 76)

PATHS = {
    "mouth":  ([(47, 78), (47, 73), (47, 67)], 5.0, 6.0),
    "nave_s": ([(47, 67), (45, 60), (48, 54)], 7.0, 7.5),
    "nave_n": ([(47, 46), (46, 40), (47, 34), (47, 28), (47, 22)], 6.0, 6.0),
    "west":   ([(42, 50), (34, 49), (26, 48), (20, 47)], 4.6, 4.6),
    "east":   ([(52, 50), (60, 49), (68, 48), (74, 47)], 4.6, 4.6),
    "alcove_w": ([(41, 62), (35, 63), (31, 63)], 3.0, 3.0),
    "alcove_e": ([(53, 38), (60, 38), (64, 37)], 3.0, 3.0),
    "bay_w":  ([(40, 17), (33, 15), (28, 14)], 3.2, 3.2),
    "bay_e":  ([(54, 17), (61, 15), (66, 14)], 3.2, 3.2),
}
ROOMS = {
    "gate":    (47, 70, 9, 4, 0, 0.4, "The Frost Gate"),
    "heart":   (47, 50, 13, 9, 0, 1.0, "The Cairn Heart"),
    "west":    (17, 47, 10, 8, 0, 2.0, "The Houndkeepers' Crypt"),
    "east":    (77, 47, 10, 8, 0, 0.7, "The Hunters' Ossuary"),
    "gallery": (47, 33, 11, 6, 0, 1.5, "The Howling Gallery"),
    "hall":    (47, 16, 22, 11, 0, 2.4, "Hall of the Hunt-King"),
    "alcove_w": (30, 63, 5, 4, 0, 0.9, "The Winter Niche"),
    "alcove_e": (65, 37, 5, 4, 0, 1.8, "The Rimed Niche"),
}

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


def walk(key, t):
    pts = PATHS[key][0]
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    d = t * sum(seg)
    for i, s in enumerate(seg):
        if d <= s or i == len(seg) - 1:
            u = min(1.0, d / s) if s else 0.0
            return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * u, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * u)
        d -= s


def build_barrows():
    zone = Tilemap("Howling Barrows", W, H,
                   "A frozen long barrow where the wind never stops howling; the Wild Hunt is buried here, and has not "
                   "finished hunting.")
    zone.is_cave = True
    zone.region = "Ashenvale East"
    zone.fixed_spawns = False
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b

    for i, (key, (pts, w0, w1)) in enumerate(PATHS.items()):
        tube(b, pts, w0, w1, ph=0.5 + i * 0.9)
    for key, (cx, cy, rx, ry, rot, ph, _n) in ROOMS.items():
        cavern(b, cx, cy, rx, ry, rot, ph)
    # join the nave halves through the Heart and the tunnel ends into their rooms
    for pts in (((48, 54), (47, 46)), ((47, 22), (47, 24)), ((24, 47), (22, 47)), ((70, 47), (72, 47)),
                ((31, 63), (33, 63)), ((64, 37), (62, 37)), ((28, 14), (31, 14)), ((66, 14), (63, 14))):
        tube(b, list(pts), 4.0, 4.0)

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    bosses = [(47, 12, "Hunt-King Valorin"), (15, 47, "Wintermaw the Howling")]
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
    for (x, y) in ((82, 47), (66, 37), (29, 63), (27, 13), (68, 13)):
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        chests.append(p)
    CHESTS[:] = chests
    for c in chests:
        L.mark("chest", *c)

    def sub(name, x, y, rx, ry):
        zone.add_subzone(name, int(x - rx), int(y - ry), int(2 * rx), int(2 * ry))
    zone.add_subzone("Howling Barrows", 0, 0, W, H)      # whole-map cave-table key first; named rooms re-register after
    for key, (cx, cy, rx, ry, rot, ph, name) in ROOMS.items():
        sub(name, cx, cy, rx + 2, ry + 2)
    return zone, L


def finish(zone, L):
    targets = [PORTAL] + [(x, y) for (x, y) in BOSSES.values()] + list(CHESTS)
    return L.finish(targets)


def dress(zone, L):
    from tools.ashenvale_town_kit import INDEX

    def P(name, cx, by, h, **kw):
        kw.setdefault("where", INDEX.get(name, DP))
        return L.prop(name, cx, by, h, **kw)
    R = ROOMS
    # ---- the Frost Gate: icicle pillars flank the door, a howling standard marks the dead's road
    P("ashx_icicle_pillar", 40, 72, 6, solid="core")
    P("ashx_icicle_pillar", 54, 72, 6, solid="core")
    P("ashx_howling_standard", 51, 67, 6, solid="core")
    # ---- nave (south): a black-ice sheet underfoot (the burial niches line the Cairn Heart)
    P("ashx_burial_niche_wall", 40, 44, 6, solid="core")
    P("ashx_burial_niche_wall", 54, 44, 6, solid="core")
    P("ashx_black_ice_patch", 47, 62, 3, solid=False)
    # ---- the Cairn Heart: two spirit braziers and a frozen warrior at the crossing
    hx, hy = R["heart"][:2]
    P("ashx_spirit_brazier", hx - 7, hy - 3, 4, solid="core")
    P("ashx_spirit_brazier", hx + 7, hy - 3, 4, solid="core")
    P("ashx_black_ice_patch", hx, hy + 2, 3, solid=False)
    P("ashx_ice_stalagmites", hx - 9, hy + 5, 4, solid="core")
    # ---- Houndkeepers' Crypt (rare's lair): kennel bones and a standard
    wx, wy = R["west"][:2]
    P("ashx_frost_sarcophagus", wx - 5, wy - 2, 5, solid="core")
    P("skull_pile", wx + 4, wy + 2, 3)
    P("ashx_howling_standard", wx + 1, wy - 5, 6, solid="core")
    P("ashx_ice_stalagmites", wx - 6, wy + 4, 4, solid="core")
    # ---- Hunters' Ossuary: sarcophagi and a wall of niches, a candelabra
    ex, ey = R["east"][:2]
    P("ashx_frost_sarcophagus", ex - 4, ey - 2, 5, solid="core")
    P("ashx_frost_sarcophagus", ex + 1, ey - 3, 5, solid="core")
    P("ashx_burial_niche_wall", ex, ey - 6, 6, solid="core")
    P("candelabra", ex - 6, ey + 3, 3)
    P("skull_pile", ex + 5, ey + 3, 3)
    # ---- niches: one small centrepiece each
    P("ashx_ice_stalagmites", R["alcove_w"][0] - 1, R["alcove_w"][1] + 3, 4, solid="core")
    P("ashx_black_ice_patch", R["alcove_e"][0], R["alcove_e"][1] + 1, 3, solid=False, near_ok=True)
    # ---- Howling Gallery: the frozen hunters kneel either side of the path
    gx, gy = R["gallery"][:2]
    P("ashx_frozen_warrior", gx - 5, gy - 1, 6, solid="core")
    P("ashx_frozen_warrior", gx + 5, gy - 1, 6, solid="core")
    P("ashx_icicle_pillar", gx - 8, gy + 3, 6, solid="core")
    P("ashx_icicle_pillar", gx + 8, gy + 3, 6, solid="core")
    # ---- Hall of the Hunt-King: the tomb itself, four columns, standards and braziers
    sx, sy = R["hall"][:2]
    P("ashx_frost_sarcophagus", sx, sy - 9, 6, solid="core", avoid=1)
    P("ashx_icicle_pillar", sx - 9, sy - 4, 7, solid="core")
    P("ashx_icicle_pillar", sx + 9, sy - 4, 7, solid="core")
    P("ashx_icicle_pillar", sx - 9, sy + 4, 7, solid="core")
    P("ashx_icicle_pillar", sx + 9, sy + 4, 7, solid="core")
    P("ashx_howling_standard", sx - 5, sy - 3, 6, solid="core")
    P("ashx_howling_standard", sx + 5, sy - 3, 6, solid="core")
    P("ashx_spirit_brazier", sx - 13, sy + 1, 4, solid="core")
    P("ashx_spirit_brazier", sx + 13, sy + 1, 4, solid="core")
    P("ashx_frozen_warrior", sx - 14, sy - 4, 6, solid="core")
    P("ashx_black_ice_patch", sx, sy + 1, 3, solid=False)
    return zone, L


def generate_howling_barrows():
    zone, L = build_barrows()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_barrows_baked():
    """(zone, layout) with props + QA done - what the baker paints from."""
    zone, L = build_barrows()
    dress(zone, L)
    finish(zone, L)
    return zone, L
