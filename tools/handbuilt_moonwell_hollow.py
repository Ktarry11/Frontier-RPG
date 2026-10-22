"""
Hand-built Moonwell Hollow (85x70): the root-cellar under Ashenvale's Moonwell, rotting from the roots up.

ARCHETYPE: THE HOURGLASS.  Two wide bowls joined by a pinched waist, with a CHOICE of crossing: the Dripping Grotto
(south, where you arrive) and the Moonwell Sanctum (north, the boss) are linked by TWO tunnels that run round a solid
heart of rock - the dry ROOT TUNNEL on the west (a side adit leads into the Druids' Alcove, where an old rare is
holed up) and the wadeable SILVERSEEP on the east (the Moonwell's runoff, glowing blue; a side adit leads to Lantern
Hollow and a chest).  Either way round is the same distance; the point is the loop and the two nooks.  (Broodspiral =
spiral, RFK = warren wheel, Wailing = river ring, Blackfathom = flooded halls; this is the only twin-bowl dungeon.)

  Mouth (42,66) -> DRIPPING GROTTO -+- W: Root Tunnel -> (adit E: Druids' Alcove, rare Mosshide) -+-> MOONWELL SANCTUM
                                    '- E: Silverseep   -> (adit W: Lantern Hollow, chest)       -'   (Maelwyn Blightbloom)

Single-boss cave => TRASH IS RANDOM (zone.fixed_spawns = False; encounters.json Ashenvale West caves["Moonwell Hollow"]).
Boss: Maelwyn Blightbloom (L25).  Pinned rare: Mosshide the Gloomcap Elder (L24, Druids' Alcove).  Zone: Ashenvale West 22-28.

HARD CONTRACTS (world/portal_manager.py): portal (42,66) <-> Ashenvale West (110,82); arrival = 2 north.
Prop rule (Kyle): less is more; logical for the room; a few centrepieces.
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked, _apply_pools  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

BAKED = "assets/tiles/moonwell_hollow/baked"
W, H = 85, 70
PORTAL = (42, 66)

PATHS = {
    "mouth":   ([(42, 67), (42, 63), (42, 59)], 5.0, 6.0),
    "west":    ([(26, 47), (16, 43), (11, 34), (14, 26), (24, 21)], 4.8, 4.8),
    "east":    ([(58, 47), (68, 43), (73, 34), (70, 26), (60, 21)], 5.2, 5.2),
    "alcove":  ([(12, 36), (20, 35), (27, 34)], 3.2, 3.2),
    "lantern": ([(72, 35), (64, 34), (57, 34)], 3.2, 3.2),
}
ROOMS = {
    "mouth":   (42, 63, 9, 4, 0, 0.4, "The Hollow Mouth"),
    "grotto":  (42, 51, 21, 9, 0, 0.9, "The Dripping Grotto"),
    "sanctum": (42, 17, 24, 11, 0, 1.7, "The Moonwell Sanctum"),
    "alcove":  (31, 34, 6, 4, 0, 2.2, "The Druids' Alcove"),
    "lantern": (53, 34, 6, 4, 0, 0.6, "Lantern Hollow"),
}
# analytic shallow pools (walkable, painted as moonwater): (cx, cy, rx, ry, phase)
MH_POOLS = [
    (42, 20, 9.0, 5.5, 1.2),                         # the Moonwell's own pool
    (60, 47, 4.6, 2.8, 0.3), (66, 45, 5.0, 3.0, 1.1), (71, 40, 4.0, 3.6, 2.0),    # the Silverseep running north
    (73, 34, 3.8, 3.6, 0.7), (72, 28, 4.0, 3.2, 1.6), (67, 24, 4.6, 2.8, 2.4), (61, 21, 4.0, 2.6, 0.9),
    (30, 54, 4.8, 3.0, 0.5),                         # the grotto's drip pond
]

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


def build_moonwell():
    zone = Tilemap("Moonwell Hollow", W, H,
                   "Roots as thick as houses hang over a flooded cellar of silver light, the Moonwell's drain, "
                   "going wrong from the bottom up.")
    zone.is_cave = True
    zone.region = "Ashenvale West"
    zone.fixed_spawns = False
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b

    for i, (key, (pts, w0, w1)) in enumerate(PATHS.items()):
        tube(b, pts, w0, w1, ph=0.5 + i * 0.9)
    for key, (cx, cy, rx, ry, rot, ph, _n) in ROOMS.items():
        cavern(b, cx, cy, rx, ry, rot, ph)
    # join tunnel ends into their bowls
    for pts in (((42, 59), (42, 57)), ((26, 47), (30, 49)), ((58, 47), (54, 49)),
                ((24, 21), (29, 20)), ((60, 21), (55, 20)), ((27, 34), (29, 34)), ((57, 34), (55, 34))):
        tube(b, list(pts), 4.0, 4.0)

    _apply_pools(zone, MH_POOLS, shallow_only=True)

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    bosses = [(42, 10, "Maelwyn Blightbloom"), (31, 34, "Mosshide the Gloomcap Elder")]
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
    for (x, y) in ((53, 35), (59, 13), (23, 56), (27, 15)):
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        chests.append(p)
    CHESTS[:] = chests
    for c in chests:
        L.mark("chest", *c)

    def sub(name, x, y, rx, ry):
        zone.add_subzone(name, int(x - rx), int(y - ry), int(2 * rx), int(2 * ry))
    zone.add_subzone("Moonwell Hollow", 0, 0, W, H)      # whole-map cave table key first; named rooms re-register after
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
    # ---- the mouth: a moon-sigil stone at the door, roots hanging
    P("ash_moon_rune_stone", 36, 65, 6)
    P("den_glow_mushrooms", 49, 64, 3)
    # ---- the Dripping Grotto: stalagmites, ferns round the drip pond, a fallen log
    P("den_stalagmites", 25, 50, 4, solid="core")
    P("den_stalagmites", 58, 54, 4, solid="core")
    P("fern_cluster", 34, 57, 3)
    P("fern_cluster", 27, 57, 3)
    P("vot_reeds", 33, 52, 3)
    P("fallen_log", 50, 48, 3)
    P("den_glow_mushrooms", 44, 56, 3)
    P("ash_silver_saplings", 47, 58, 5)
    # ---- the root tunnel: sparse
    for key, t, name, h in (("west", 0.2, "den_rock_rubble", 2), ("west", 0.55, "fern_cluster", 3),
                            ("west", 0.85, "den_stalagmites", 3)):
        x, y = walk(key, t)
        P(name, round(x) + 2, round(y) + 1, h)
    # ---- Druids' Alcove: a herb altar, an offering stone, a lamp of mushrooms
    ax, ay = R["alcove"][:2]
    P("moonwell_altar", ax - 4, ay - 1, 6, solid="core", avoid=1)
    P("ash_glow_mushroom_ring", ax - 4, ay + 2, 4)
    P("den_backpack", ax + 4, ay + 2, 2)
    # ---- Silverseep: reeds on the banks, one glowing growth
    for key, t, name, h in (("east", 0.18, "vot_reeds", 3), ("east", 0.5, "ash_nightbloom_bush", 4),
                            ("east", 0.85, "vot_reeds", 3)):
        x, y = walk(key, t)
        P(name, round(x) - 3, round(y) + 1, h)
    # ---- Lantern Hollow: a traveller's rest, lit by blue mushrooms
    lx, ly = R["lantern"][:2]
    P("den_glow_mushrooms", lx - 3, ly + 2, 3)
    P("den_glow_mushrooms", lx + 3, ly + 2, 3)
    P("ash_foxglove_patch", lx - 1, ly - 3, 3)
    # ---- the Moonwell Sanctum: the Moonwell's pool, the ruin round it, the boss's stage
    sx, sy = R["sanctum"][:2]
    P("ash_elune_statue", sx - 16, sy + 5, 8, solid="core")
    P("ash_elven_ruin_wall", sx + 14, sy - 4, 7, solid="core")
    P("ash_ivy_pillar", sx - 9, sy - 8, 6, solid="core")
    P("ash_ivy_pillar", sx + 9, sy - 8, 6, solid="core")
    P("ash_moon_rune_stone", sx - 18, sy + 2, 6)
    P("ash_glow_mushroom_ring", sx + 16, sy + 5, 4)
    P("ashx_corrupt_moonwell", sx, sy - 8, 6, solid=False, near_ok=True, avoid=0)   # the blight at the boss's feet
    P("dead_corrupted_tree", sx - 11, sy - 6, 7, solid="core")
    P("dead_corrupted_tree", sx + 11, sy - 5, 7, solid="core")
    return zone, L


def generate_moonwell_hollow():
    zone, L = build_moonwell()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_moonwell_baked():
    """(zone, layout) with props + QA done - what the baker paints from."""
    zone, L = build_moonwell()
    dress(zone, L)
    finish(zone, L)
    return zone, L
