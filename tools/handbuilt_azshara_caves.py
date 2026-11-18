"""
Hand-built Azshara's two caves (docs/azshara_brief.md). Caves, not dungeons: one or two bosses pinned by the map, trash
rolled from the cave's own table (zone.fixed_spawns = False), no set packs.

Kyle, 18 Nov 2026, picked both names and both rosters. Neither shape is a string of round rooms (Kyle: "You default
to blobs"), and neither repeats a shape already in the game (the Plaguelands' web, ladder, grid and switchback):

  HALDARR DEN        off West Azshara (166,154), 54-56. THE ROOTS. The satyrs dug in under the great cursed tree
                     the way its roots grew: you come in at the tip of the taproot and climb it, winding, up to the
                     hollow under the tree's base where Haldarr the Hornlord keeps his fire. Side roots branch off the
                     taproot and fork again, and every fork ends in a pocket where the satyrs keep the Highborne they
                     bound. The Bound Magister (optional) is chained in the farthest of them.
  HETAERA'S GROTTO   off Central Azshara (186,58), 56-58. THE SHELL. A sea cave grown like a nautilus: you come in at
                     the widest chamber, the sea mouth, and every chamber after it along the spiral is smaller and
                     turns further in, each with the sea standing in it, until the spiral opens into the drowned
                     Highborne hall at its core. Tide-Priestess Sel'thira holds the hall; Hetaera, the hydra mother
                     (optional), lies in a deep pool off the spiral's second turn.

Every cave's way in and out is its one portal; you arrive two tiles inside it.
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked, _apply_pools  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

DP = "assets/tiles/dungeon_props/"
AZP = "assets/tiles/azshara/props/"
XP = "assets/tiles/ashenvale_corruption/props/"

DEN, GROTTO = "Haldarr Den", "Hetaera's Grotto"
CAVES = (DEN, GROTTO)
SLUG = {DEN: "haldarr_den", GROTTO: "hetaeras_grotto"}
BAKED = {n: f"assets/tiles/azshara/baked_{SLUG[n]}" for n in CAVES}
PARENT = {DEN: "West Azshara", GROTTO: "Central Azshara"}
DESC = {
    DEN: "The satyrs' warren under the great cursed tree of Haldarr, dug the way its roots grew. The Highborne they "
         "bound are kept at the ends of the roots.",
    GROTTO: "A sea cave on Hetaera's Clutch that grows inward like a shell, every chamber smaller than the last, down "
            "to a Highborne hall the sea brought up with it. The naga come up through here.",
}
SIZE = {DEN: (96, 100), GROTTO: (100, 100)}
PORTAL = {DEN: (48, 97), GROTTO: (50, 97)}
#: the way in from the open map: cave -> (parent tile, the mouth's sprite, w, h), drawn by the parent map
MOUTHS = {DEN: ((166, 154), "furbolg_den_entrance", 7, 7), GROTTO: ((186, 58), "ent_sea_cave", 9, 7)}
BOSSES = {n: {} for n in CAVES}
CHESTS = {n: [] for n in CAVES}
ROOM_NAMES = {n: {} for n in CAVES}
POOLS = {n: [] for n in CAVES}


def _near_walkable(zone, x, y, rad=5, dry=True):
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            xx, yy = int(x) + dx, int(y) + dy
            if not zone.is_walkable(xx, yy):
                continue
            if dry and zone.base_layer[yy][xx] in ("shallow_water", "deep_water"):
                continue
            d = dx * dx + dy * dy
            if best is None or d < best[0]:
                best = (d, xx, yy)
    return None if best is None else (best[1], best[2])


def _snapped(zone, L):
    """L.prop, but standing on the nearest dry floor: the tunnels wind, so a spot named on the plan can sit a tile or
    two off the floor that was actually cut."""
    def P(name, x, y, h, **kw):
        p = _near_walkable(zone, x, y, rad=3)
        return L.prop(name, p[0], p[1], h, **kw) if p else L.skipped.append((name, x, y, "no floor near"))
    return P


def _new(name):
    W, H = SIZE[name]
    zone = Tilemap(name, W, H, DESC[name])
    zone.is_cave = True
    zone.region = PARENT[name]
    zone.fixed_spawns = False
    px, py = PORTAL[name]
    return zone, CaveLayout(zone, (px, py - 2))


def _place(zone, L, name, bosses, chests, rooms):
    px, py = PORTAL[name]
    zone.collision_layer[py][px] = None
    L.mark("portal", px, py)
    fixed = []
    for (x, y, n) in bosses:
        p = _near_walkable(zone, x, y)
        assert p, (name, n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    BOSSES[name].clear()
    BOSSES[name].update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (fixed[0][0], fixed[0][1])
    zone.boss_positions = list(fixed)
    CHESTS[name][:] = []
    for (x, y) in chests:
        p = _near_walkable(zone, x, y)
        assert p, (name, x, y)
        CHESTS[name].append(p)
        L.mark("chest", *p)
    W, H = SIZE[name]
    zone.add_subzone(name, 0, 0, W, H)
    ROOM_NAMES[name].clear()
    for rname, (x, y, w, h) in rooms.items():
        zone.add_subzone(rname, x, y, w, h)
        ROOM_NAMES[name][rname] = (x, y, w, h)


# ============================================================================================ HALDARR DEN
#: the taproot, from the way in at the bottom up to Haldarr's hollow at the top
#: a gentle sweep, not a zig-zag (Kyle, 18 Nov 2026: "dont make it too zig-zag as its hard to walk")
TAPROOT = [(48, 97), (48, 86), (49, 74), (48, 62), (49, 50), (48, 38), (48, 22)]
#: side roots: (where on the taproot they leave it, the root's line out, and its two forks' pockets)
SIDE_ROOTS = [
    ((48, 86), [(36, 83), (25, 79)], [(14, 72), (16, 90)]),
    ((49, 74), [(61, 71), (73, 68)], [(85, 60), (84, 80)]),
    ((48, 62), [(35, 58), (24, 52)], [(12, 46), (24, 38)]),
    ((49, 50), [(61, 46), (72, 40)], [(84, 30), (82, 48)]),
]
HOLLOW = (48, 14, 12, 8)
MAGISTER_POCKET = (84, 30)      # the farthest pocket, up the east side


def build_den():
    name = DEN
    zone, L = _new(name)
    b = L.b
    tube(b, TAPROOT, 5.0, 6.4, ph=0.4)
    cavern(b, *HOLLOW, 0, 0.8)
    for i, (start, line, forks) in enumerate(SIDE_ROOTS):
        pts = [start] + line
        tube(b, pts, 3.8, 3.4, ph=1.1 + i)
        for j, tip in enumerate(forks):
            tube(b, [line[-1], tip], 3.2, 3.0, ph=2.0 + i + j)
            big = tip == MAGISTER_POCKET
            cavern(b, tip[0], tip[1], 6.5 if big else 4.6, 5.5 if big else 3.8, 15 * (i - j), 0.6 + i + j)
    _place(zone, L, name, [(48, 13, "Haldarr the Hornlord"), (MAGISTER_POCKET[0], MAGISTER_POCKET[1],
                                                                 "The Bound Magister")],
           [(16, 90), (85, 60), (12, 46)],
           {"The Taproot": (38, 20, 20, 80), "Haldarr's Hollow": (34, 4, 28, 20),
            "The West Roots": (4, 32, 40, 64), "The East Roots": (54, 32, 40, 56),
            "The Magister's Chains": (76, 22, 18, 16)})
    return zone, L


def dress_den(zone, L):
    P = _snapped(zone, L)
    hx, hy = 48, 14
    P("satyr_throne", hx, hy - 4, 4, where=XP, solid="core")
    P("az_fel_bonfire", hx - 6, hy + 2, 3, where=AZP, solid="core")
    P("az_fel_bonfire", hx + 6, hy + 2, 3, where=AZP, solid="core")
    P("az_satyr_totem", hx - 9, hy - 3, 4, where=AZP, solid="core")
    P("az_satyr_totem", hx + 9, hy - 3, 4, where=AZP, solid="core")
    P("ashx_satyr_weapon_rack", 46, 46, 3, where=XP, solid="core")
    P("fel_fire_brazier", 50, 70, 3, where=XP, solid="core")
    P("fel_fire_brazier", 46, 30, 3, where=XP, solid="core")
    # the Highborne they bound, a frame in every pocket
    for (_s, _l, forks) in SIDE_ROOTS:
        for tip in forks:
            if tip != MAGISTER_POCKET:
                P("rf_shackle_frame", tip[0], tip[1] - 1, 3, solid="core")
    P("bbc_chains", MAGISTER_POCKET[0] - 3, MAGISTER_POCKET[1] - 2, 3, solid="core")
    P("bbc_chains", MAGISTER_POCKET[0] + 3, MAGISTER_POCKET[1] - 2, 3, solid="core")
    P("ashx_skull_fence", 44, 82, 3, where=XP, solid="core")
    return zone, L


# ============================================================================================ HETAERA'S GROTTO
SPIRAL_C = (50, 50)


def _spiral(t):
    """A point on the shell's spiral: t = 0 at the sea mouth (bottom), 1 at the core; turns 1.5 times inward."""
    ang = math.radians(90 - t * 540)
    r = 38 * (0.30 ** t)
    return SPIRAL_C[0] + r * math.cos(ang), SPIRAL_C[1] + 0.96 * r * math.sin(ang)


CHAMBER_T = (0.0, 0.15, 0.30, 0.45, 0.60, 0.74)
HYDRA_POOL = None     # set in build_grotto: the alcove off the spiral's second turn


def build_grotto():
    global HYDRA_POOL
    name = GROTTO
    zone, L = _new(name)
    b = L.b
    line = [_spiral(i / 40) for i in range(0, 37)]
    tube(b, line, 4.6, 3.6, ph=0.7)
    pools = []
    for k, t in enumerate(CHAMBER_T):
        cx, cy = _spiral(t)
        rad = 11.0 * (0.62 ** (t * 1.4))
        cavern(b, cx, cy, rad, rad * 0.84, 30 * k, 0.5 + k)
        # the sea standing in every chamber, on its outer side
        ox, oy = cx - SPIRAL_C[0], cy - SPIRAL_C[1]
        n = math.hypot(ox, oy) or 1
        pools.append((cx + ox / n * rad * 0.48, cy + oy / n * rad * 0.48, rad * 0.42, rad * 0.32, 0.4 + k))
    # the core: the drowned Highborne hall
    cavern(b, SPIRAL_C[0], SPIRAL_C[1], 10, 9, 0, 1.9)
    tube(b, [_spiral(0.86), _spiral(0.95), SPIRAL_C], 4.0, 4.4, ph=2.6)
    # Hetaera's alcove: off the spiral's second turn, outward, a deep pool with a ledge on the near side
    hx, hy = _spiral(0.52)
    ox, oy = hx - SPIRAL_C[0], hy - SPIRAL_C[1]
    n = math.hypot(ox, oy) or 1
    ax, ay = hx + ox / n * 13, hy + oy / n * 13
    tube(b, [(hx, hy), (ax, ay)], 3.6, 3.6, ph=3.3)
    cavern(b, ax + ox / n * 4, ay + oy / n * 4, 8, 6.5, 0, 3.1)
    HYDRA_POOL = (ax + ox / n * 7, ay + oy / n * 7)
    pools.append((HYDRA_POOL[0], HYDRA_POOL[1], 5.5, 4.2, 1.2))
    # a ring of shallows round the hall's middle
    pools.append((SPIRAL_C[0], SPIRAL_C[1] + 3, 4.5, 2.6, 2.2))
    POOLS[name][:] = pools
    _apply_pools(zone, pools)
    # the way in at the bottom
    tube(b, [PORTAL[name], _spiral(0.0)], 4.6, 5.0, ph=0.2)
    hb = _near_walkable(zone, ax, ay, rad=6)
    _place(zone, L, name, [(SPIRAL_C[0], SPIRAL_C[1] - 5, "Tide-Priestess Sel'thira"),
                           (hb[0], hb[1], "Hetaera")],
           [_spiral(0.15), _spiral(0.45), _spiral(0.74)],
           {"The Sea Mouth": (30, 74, 40, 24), "The Chambers": (6, 8, 88, 88),
            "Hetaera's Pool": (int(HYDRA_POOL[0]) - 10, int(HYDRA_POOL[1]) - 9, 20, 18),
            "The Drowned Hall": (39, 40, 22, 20)})
    return zone, L


def dress_grotto(zone, L):
    P = _snapped(zone, L)
    cx, cy = SPIRAL_C
    P("vz_coral_throne", cx, cy - 9, 4, solid="core")
    P("grotto_naga_priestess_statue", cx - 7, cy - 4, 4, solid="core")
    P("grotto_naga_warrior_statue", cx + 7, cy - 4, 4, solid="core")
    P("az_barnacle_statue", cx - 6, cy + 6, 5, where=AZP, solid="core")
    P("az_drowned_obelisk", cx + 6, cy + 6, 4, where=AZP, solid="core")
    P("grotto_blue_brazier", cx - 3, cy - 7, 3, solid="core")
    P("grotto_blue_brazier", cx + 3, cy - 7, 3, solid="core")
    for k, t in enumerate(CHAMBER_T[1:], 1):
        x, y = _spiral(t)
        P(("grotto_glow_coral", "grotto_naga_column", "az_coral_cluster", "grotto_kelp_stalks",
           "grotto_shell_altar")[k % 5], int(x), int(y), 3,
          where=(AZP if k % 5 == 2 else DP), solid="core")
    mx, my = _spiral(0.0)
    P("az_wreck_prow", int(mx) + 5, int(my) - 1, 4, where=AZP, solid="core")
    P("grotto_crab_nest", int(mx) - 5, int(my) + 1, 3, solid="core")
    P("grotto_serpent_skeleton", int(HYDRA_POOL[0]) - 4, int(HYDRA_POOL[1]) - 6, 3, solid="core")
    P("grotto_giant_clam", int(HYDRA_POOL[0]) + 5, int(HYDRA_POOL[1]) - 5, 3, solid="core")
    return zone, L


BUILD = {DEN: (build_den, dress_den), GROTTO: (build_grotto, dress_grotto)}


def build(name):
    zone, L = BUILD[name][0]()
    BUILD[name][1](zone, L)
    L.finish([PORTAL[name]] + list(BOSSES[name].values()) + CHESTS[name])
    return zone, L


def generate(name):
    zone, _L = build(name)
    register_baked(zone, BAKED[name])
    return zone


def build_den_baked():
    return build(DEN)


def build_grotto_baked():
    return build(GROTTO)


if __name__ == "__main__":
    for n in CAVES:
        z, L = build(n)
        walk = sum(1 for y in range(z.height) for x in range(z.width) if z.is_walkable(x, y))
        print(n, z.width, "x", z.height, "| walkable", walk, "| bosses", BOSSES[n], "| skipped", L.skipped)
