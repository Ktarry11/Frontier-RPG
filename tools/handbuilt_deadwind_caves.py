"""
Hand-built Deadwind's two caves (docs/deadwind_brief.md, docs/deadwind_quest_plan.md). Caves, not dungeons: one boss
pinned by the map, trash rolled from the cave's own table (zone.fixed_spawns = False), no set packs.

Neither shape is a string of round rooms (Kyle: "You default to blobs"), and neither repeats a shape already in the
game (the Plaguelands' web, ladder, grid and switchback, Azshara's roots and shell):

  THE WIDOWS' NEST   off Deadwind West (150,24), 56-58. THE FUNNEL. Built the way a funnel-web spider builds: you
                     come in onto the Sheet, a wide fan of silk-floored cave that narrows as you cross it, and it
                     funnels you into the Throat, one long winding tube with the widows' retreat holes bored off its
                     sides. At the top of the Throat is the brood chamber, where the Silk Mother has grown into her
                     own cocoon.
  THE DROWNED SEEP   off Deadwind East (30,145), 57-58. THE DRAIN. The fallout pools in the Drowned Hollow and drains
                     down through the hill, and the cave is the channel it cut: one long meander, the seep running
                     down the middle of it between two banks, deep in the bends and shallow where you can wade
                     across. The bends left oxbow pools behind them. It ends in the sump, a flooded round chamber
                     with a mud shelf, where the Drowned Thing has been growing for months.

Every cave's way in and out is its one portal; you arrive two tiles inside it.
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked, _apply_pools  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

DWP = "assets/tiles/deadwind/props/"
FZP = "assets/tiles/dungeon_props/"

NEST, SEEP = "The Widows' Nest", "The Drowned Seep"
CAVES = (NEST, SEEP)
SLUG = {NEST: "widows_nest", SEEP: "drowned_seep"}
BAKED = {n: f"assets/tiles/deadwind/baked_{SLUG[n]}" for n in CAVES}
PARENT = {NEST: "Deadwind West", SEEP: "Deadwind East"}
DESC = {
    NEST: "The Deadwind widows' nest, bored into the crag above their wood. The silk funnels everything that walks "
          "in toward the brood, and the eggs glow.",
    SEEP: "The channel the fallout cut draining down through the hill under the Drowned Hollow. It all ends up in "
          "the sump at the bottom, and so does everything it carried.",
}
SIZE = {NEST: (96, 100), SEEP: (100, 100)}
PORTAL = {NEST: (48, 97), SEEP: (50, 97)}
#: the way in from the open map: cave -> (parent tile, the mouth's sprite, w, h), drawn by the parent map
MOUTHS = {NEST: ((150, 24), "ent_spider_lair", 8, 6), SEEP: ((30, 145), "ent_plague_cave", 8, 6)}
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


# ============================================================================================ THE WIDOWS' NEST
#: the Sheet: a fan, widest at the way in (the bottom), narrowing to the Throat's mouth
SHEET_BOTTOM, SHEET_TOP = 86, 60
SHEET_HALF = (32, 6)          # the fan's half-width at the bottom, and at the top
#: the Throat: one long winding tube up from the Sheet to the brood chamber
THROAT = [(48, 62), (42, 52), (52, 42), (44, 32), (50, 22), (48, 16)]
#: the retreat holes bored off the Throat: (where they leave it, their line, the pocket at the end)
RETREATS = [
    ((42, 52), [(30, 50)], (20, 52)),
    ((52, 42), [(64, 40)], (74, 44)),
    ((44, 32), [(32, 28)], (22, 24)),
    ((50, 22), [(62, 20)], (72, 16)),
]
BROOD = (48, 10, 14, 7)
#: little egg alcoves bitten out of the Sheet's two edges
EGG_ALCOVES = [(19, 80), (29, 71), (36, 64), (77, 80), (67, 71), (60, 64)]


def _fan(b, ph=0.6):
    """Open the Sheet: a trapezoid whose two slanting sides breathe a little, so it reads as silk and not a ruler."""
    for y in range(SHEET_TOP, SHEET_BOTTOM + 1):
        t = (y - SHEET_TOP) / (SHEET_BOTTOM - SHEET_TOP)
        half = SHEET_HALF[1] + (SHEET_HALF[0] - SHEET_HALF[1]) * t ** 0.8
        half += 1.2 * math.sin(y * 0.55 + ph) + 0.6 * math.sin(y * 1.3)
        for x in range(int(48 - half), int(48 + half) + 1):
            b._open(x, y)
    # the bottom edge isn't straight either: a few bites out of it
    for (x, r) in ((22, 3.5), (36, 3.0), (60, 3.0), (74, 3.5)):
        cavern(b, x, SHEET_BOTTOM + 1, r, 2.2, 0, x * 0.1)


def build_nest():
    name = NEST
    zone, L = _new(name)
    b = L.b
    _fan(b)
    tube(b, [PORTAL[name], (48, 88)], 5.0, 6.0, ph=0.3)
    for i, (x, y) in enumerate(EGG_ALCOVES):
        cavern(b, x, y, 3.6, 2.8, 20 * i, 0.4 + i)
    tube(b, THROAT, 5.2, 4.4, ph=0.9)
    for i, (start, line, pocket) in enumerate(RETREATS):
        tube(b, [start] + line + [pocket], 3.2, 2.8, ph=1.4 + i)
        cavern(b, pocket[0], pocket[1], 4.2, 3.4, 25 * i, 0.8 + i)
    cavern(b, *BROOD, 0, 1.3)
    _place(zone, L, name, [(48, 8, "The Silk Mother")],
           [RETREATS[0][2], RETREATS[1][2], RETREATS[3][2]],
           {"The Sheet": (12, 58, 72, 34), "The Throat": (34, 14, 28, 50), "The Retreats": (14, 12, 68, 46),
            "The Brood": (32, 2, 32, 16)})
    return zone, L


def dress_nest(zone, L):
    P = _snapped(zone, L)
    # the brood: the Silk Mother's cocoon wall, and the egg sacs heaped round it
    P("dw_web_mass", 38, 9, 4, where=DWP, solid="core")
    P("dw_web_mass", 58, 9, 4, where=DWP, solid="core")
    P("dw_egg_sacs", 42, 14, 3, where=DWP, solid="core")
    P("dw_egg_sacs", 54, 14, 3, where=DWP, solid="core")
    P("dw_ogre_cocoon", 36, 13, 4, where=DWP, solid="core")
    # the Sheet: cocooned kills hung in the alcoves, eggs in the edges
    for i, (x, y) in enumerate(EGG_ALCOVES):
        P(("dw_egg_sacs", "dw_web_cocoon", "dw_bone_nest")[i % 3], x, y, 3, where=DWP, solid="core")
    P("dw_dissolved_deer", 40, 78, 3, where=DWP, solid="core")
    P("dw_shed_skin", 58, 76, 3, where=DWP, solid="core")
    # the retreats: something left behind in every hole
    for i, (_s, _l, (x, y)) in enumerate(RETREATS):
        P(("dw_shed_skin", "dw_web_cocoon", "dw_bone_nest", "dw_egg_sacs")[i], x + (3 if x < 48 else -3), y + 1, 3,
          where=DWP, solid="core")
    P("dw_web_cocoon", 46, 36, 4, where=DWP, solid="core")
    return zone, L


# ============================================================================================ THE DROWNED SEEP
#: the channel the seep cut: one long meander down from the way in to the sump
MEANDER = [(50, 92), (34, 86), (24, 74), (34, 62), (56, 60), (74, 52), (72, 38), (52, 32), (30, 28), (26, 16),
           (40, 10)]
SUMP = (62, 12, 13, 9)
#: the oxbow pools the bends left behind, each in its own pocket off the channel: (cx, cy, rx, ry)
OXBOWS = [(14, 82, 7, 5), (86, 58, 6, 6), (18, 36, 6, 5)]
#: where the seep is shallow enough to wade: the channel's deep core stops short of these
RIFFLES = [(26, 70), (66, 56), (40, 30)]


def _meander_pools():
    """The seep down the channel's middle: a chain of small pools along the meander, deep in the long stretches and
    left out at the riffles, so the deep water never closes the channel."""
    pools = []
    pts = MEANDER
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 2))
        for k in range(n):
            t = k / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            if min(math.hypot(x - rx, y - ry) for (rx, ry) in RIFFLES) < 5:
                continue
            pools.append((x, y, 3.2, 3.2, 0.3 * i + k))
    return pools


def build_seep():
    name = SEEP
    zone, L = _new(name)
    b = L.b
    tube(b, [PORTAL[name], MEANDER[0]], 5.0, 7.0, ph=0.2)
    tube(b, MEANDER, 11.0, 9.0, ph=0.7)
    for i, (cx, cy, rx, ry) in enumerate(OXBOWS):
        cavern(b, cx, cy, rx + 3, ry + 2.5, 15 * i, 1.1 + i)
        near = min(MEANDER, key=lambda p: math.hypot(p[0] - cx, p[1] - cy))
        tube(b, [(cx, cy), near], 6.0, 6.0, ph=0.4 + i)       # the old bend it was cut off from
    cavern(b, *SUMP, 0, 2.2)
    tube(b, [MEANDER[-1], (SUMP[0] - 8, SUMP[1])], 7.0, 7.0, ph=1.7)
    # the water: the seep down the channel, the oxbows, and the sump with its mud shelf on the near side
    pools = _meander_pools()
    pools += [(cx, cy, rx, ry, 0.5 + i) for i, (cx, cy, rx, ry) in enumerate(OXBOWS)]
    pools.append((SUMP[0] + 3, SUMP[1] - 1, 8.5, 5.5, 1.9))
    POOLS[name][:] = pools
    _apply_pools(zone, pools)
    _place(zone, L, name, [(SUMP[0] - 7, SUMP[1] + 3, "The Drowned Thing")],
           [(OXBOWS[0][0] + 2, OXBOWS[0][1] - 5), (OXBOWS[1][0] - 1, OXBOWS[1][1] + 6), (OXBOWS[2][0], OXBOWS[2][1] - 5)],
           {"The Drain": (14, 22, 70, 76), "The Oxbows": (4, 26, 92, 64), "The Sump": (44, 0, 40, 24)})
    return zone, L


def dress_seep(zone, L):
    P = _snapped(zone, L)
    sx, sy = SUMP[0], SUMP[1]
    P("dw_flesh_mass", sx - 12, sy - 3, 4, where=DWP, solid="core")
    P("dw_tumour_growth", sx + 8, sy + 6, 4, where=DWP, solid="core")
    P("dw_hand_roots", sx - 4, sy + 7, 3, where=DWP, solid="core")
    P("dw_dissolved_deer", 30, 80, 3, where=DWP, solid="core")
    P("dw_carcass_heap", 60, 58, 3, where=DWP, solid="core")
    P("dw_eye_mushrooms", 22, 60, 3, where=DWP, solid="core")
    P("dw_eye_mushrooms", 76, 44, 3, where=DWP, solid="core")
    P("dw_fume_vent", 46, 34, 3, where=DWP, solid="core")
    P("dw_tumour_growth", 32, 20, 3, where=DWP, solid="core")
    P("dw_horse_skeleton", 82, 66, 3, where=DWP, solid="core")
    return zone, L


BUILD = {NEST: (build_nest, dress_nest), SEEP: (build_seep, dress_seep)}


def build(name):
    zone, L = BUILD[name][0]()
    BUILD[name][1](zone, L)
    L.finish([PORTAL[name]] + list(BOSSES[name].values()) + CHESTS[name])
    return zone, L


def generate(name):
    zone, _L = build(name)
    register_baked(zone, BAKED[name])
    return zone


def build_nest_baked():
    return build(NEST)


def build_seep_baked():
    return build(SEEP)


if __name__ == "__main__":
    for n in CAVES:
        z, L = build(n)
        walk = sum(1 for y in range(z.height) for x in range(z.width) if z.is_walkable(x, y))
        print(n, z.width, "x", z.height, "| walkable", walk, "| bosses", BOSSES[n], "| skipped", L.skipped)
