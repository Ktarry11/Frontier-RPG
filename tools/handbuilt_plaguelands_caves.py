"""
Hand-built the Plaguelands' four caves, one off each map (docs/plaguelands_design.md). Caves, not dungeons: one or
two bosses pinned by the map, trash rolled from the cave's own table (zone.fixed_spawns = False), no set packs.

Kyle, 16 Nov 2026: "let's add the caves, which needs boss and loot", "we can use existing art most likely", and
about the secret maps the same afternoon: "Don't make all the shapes the same. You default to blobs." So no two of
these share a shape, and none of them is a string of round rooms:

  THE WRITHING DEEP     South WPL, 53-55. THE WEB. The crypt fiends dug it the way a spider spins: a brood chamber
                        in the middle, six burrows running out from it like spokes, and two rings crossing every
                        spoke, so every junction is a choice and every way round comes back to the middle.
                        Broodlord Szarak in the brood chamber; the Silken Bride (optional) in a pocket off the rim.
  THE WEEPING CAVE      North WPL, 55-57. THE LADDER. Two long galleries one above the other, the length of the
                        hill, joined by short rungs where the water runs down between them, and at the far end the
                        pool they both drain into. The Weeper at the pool; the Drowned Hermit (optional) in a cell
                        above the upper gallery.
  THE MARRIS CRYPT      West EPL, 56-58. THE GRID. Built, not dug: the Marris family's crypt under the stead, a
                        lattice of straight passages on a mason's plan, burial niches off every one, a hall at the
                        crossing and a chapel at the head. Sexton Hollowell in the hall; the Bone Choir in the chapel.
  THE BONE MINES        East EPL, 58-60. THE SWITCHBACK. The Scourge mines bone under the Pestilent Scar: five
                        galleries stacked down the hillside, each turning back on the one above at a ramp, down to
                        the marrow pit at the bottom. Overseer Marrowgrim at the pit; the Ossifier (optional) in his
                        workshop off the middle gallery.

Every cave's way in and out is its one portal; you arrive two tiles inside it.
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

DP = "assets/tiles/dungeon_props/"
UF = "assets/tiles/undead_farmland/props/"
PL = "assets/tiles/plaguelands/props/"
EK = "assets/tiles/eastern_kingdoms/props/"
SR = "assets/tiles/skull_rock/props/"

WRITHING, WEEPING, MARRIS, BONE = "The Writhing Deep", "The Weeping Cave", "The Marris Crypt", "The Bone Mines"
CAVES = (WRITHING, WEEPING, MARRIS, BONE)
SLUG = {WRITHING: "writhing_deep", WEEPING: "weeping_cave", MARRIS: "marris_crypt", BONE: "bone_mines"}
BAKED = {n: f"assets/tiles/plaguelands/baked_{SLUG[n]}" for n in CAVES}
PARENT = {WRITHING: "Western Plaguelands South", WEEPING: "Western Plaguelands North",
          MARRIS: "Eastern Plaguelands West", BONE: "Eastern Plaguelands East"}
DESC = {
    WRITHING: "Burrows under the Writhing Haunt, dug by crypt fiends in the shape of a web. Everything down here "
              "leads back to the brood chamber in the middle.",
    WEEPING: "A long cave in the hill above the Thondroril where the water never stops running down the walls. Two "
             "galleries, one over the other, and a pool at the end that everything drains into.",
    MARRIS: "The Marris family's crypt under the stead, laid out on a mason's grid. The family's dead don't stay in "
            "their niches any more.",
    BONE: "Galleries cut into the hill under the Pestilent Scar, where the Scourge mines the bones of the east for "
          "its constructs. Every level goes deeper than the last.",
}
SIZE = {WRITHING: (96, 88), WEEPING: (104, 64), MARRIS: (90, 80), BONE: (100, 96)}
PORTAL = {WRITHING: (48, 84), WEEPING: (10, 60), MARRIS: (45, 76), BONE: (10, 90)}
#: the way in from the open map: cave -> (parent tile, the mouth's sprite, w, h). Open ground, so that coming back
#: out (two tiles north of the mouth, world/portal_manager._offset_spawn) puts you on your feet.
MOUTHS = {WRITHING: ((150, 53), "ent_spider_lair", 8, 6), WEEPING: ((146, 28), "ent_wailing_maw", 8, 6),
          MARRIS: ((66, 122), "ent_crypt_mausoleum", 8, 6), BONE: ((106, 60), "ent_collapsed_mine", 8, 6)}
BOSSES = {n: {} for n in CAVES}
CHESTS = {n: [] for n in CAVES}
ROOM_NAMES = {n: {} for n in CAVES}


def _near_walkable(zone, x, y, rad=5):
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            if zone.is_walkable(int(x) + dx, int(y) + dy):
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, int(x) + dx, int(y) + dy)
    return None if best is None else (best[1], best[2])


def _arc(cx, cy, rx, ry, a0, a1, step=12):
    """Points along an ellipse from angle a0 to a1 (degrees, clockwise on screen)."""
    n = max(2, int(abs(a1 - a0) / step) + 1)
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / (n - 1))),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / (n - 1)))) for i in range(n)]


def _new(name):
    W, H = SIZE[name]
    zone = Tilemap(name, W, H, DESC[name])
    zone.is_cave = True
    zone.region = PARENT[name]
    zone.fixed_spawns = False
    px, py = PORTAL[name]
    start = (px, py - 2)
    return zone, CaveLayout(zone, start)


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


# ============================================================================================ THE WRITHING DEEP
def build_writhing():
    name = WRITHING
    zone, L = _new(name)
    b = L.b
    cx, cy = 48, 40
    # the brood chamber
    cavern(b, cx, cy, 9, 8, 0, 0.3)
    # six spokes out from the middle, to the outer rim
    for i, ang in enumerate((-90, -30, 30, 90, 150, 210)):
        tube(b, [(cx + 6 * math.cos(math.radians(ang)), cy + 6 * math.sin(math.radians(ang))),
                 (cx + 20 * math.cos(math.radians(ang)), cy + 17 * math.sin(math.radians(ang))),
                 (cx + 36 * math.cos(math.radians(ang)), cy + 31 * math.sin(math.radians(ang)))], 3.2, 3.6,
             ph=0.4 + i)
    # two rings crossing every spoke: the inner one whole, the outer one broken in two places
    tube(b, _arc(cx, cy, 20, 17, 0, 360), 3.0, 3.0, ph=2.2)
    tube(b, _arc(cx, cy, 36, 31, -60, 100), 3.4, 3.4, ph=3.1)
    tube(b, _arc(cx, cy, 36, 31, 130, 280), 3.4, 3.4, ph=3.7)
    # the way in from the south, and the Silken Bride's pocket off the north-east rim
    tube(b, [(48, 84), (48, 78), (48, 71)], 4.5, 4.0, ph=0.9)
    cavern(b, 82, 10, 6, 5, 20, 1.1)
    tube(b, [(cx + 36 * math.cos(math.radians(-50)), cy + 31 * math.sin(math.radians(-50))), (80, 13)], 3.0, 3.0)
    _place(zone, L, name, [(cx, cy, "Broodlord Szarak"), (82, 9, "The Silken Bride")],
           [(cx + 20, cy), (cx - 36, cy - 4), (cx, cy - 31)],
           {"The Brood Chamber": (38, 31, 20, 18), "The Inner Ring": (26, 21, 44, 38),
            "The Outer Burrows": (10, 8, 76, 66), "The Bride's Pocket": (74, 3, 16, 14)})
    return zone, L


def dress_writhing(zone, L):
    P = L.prop
    cx, cy = 48, 40
    P("skull_pile", cx - 5, cy + 4, 2)
    P("skull_pile", cx + 6, cy - 3, 2)
    for (x, y) in ((cx - 18, cy - 6), (cx + 18, cy + 8), (cx - 8, cy + 18), (cx + 30, cy - 18)):
        P("skull_pile", x, y, 2)
    P("pl_corpse_sacks", 84, 12, 3, where=PL, solid="core")
    P("pl_skull_pile", 46, 76, 2, where=PL)
    return zone, L


# ============================================================================================ THE WEEPING CAVE
def build_weeping():
    name = WEEPING
    zone, L = _new(name)
    b = L.b
    # two galleries the length of the hill
    tube(b, [(14, 18), (32, 14), (52, 19), (72, 15), (92, 18), (96, 24)], 4.6, 4.6, ph=0.5)
    tube(b, [(14, 46), (34, 50), (54, 45), (74, 50), (92, 46), (96, 40)], 4.8, 4.8, ph=1.3)
    # the rungs, where the water runs down from the upper gallery to the lower
    for i, x in enumerate((24, 42, 62, 82)):
        tube(b, [(x, 18), (x + 2, 32), (x, 46)], 2.8, 2.8, ph=2.0 + i)
    # the way in, at the west end of the lower gallery, and the pool both galleries drain into, at the east end
    cavern(b, 12, 52, 6, 6, 0, 0.7)
    tube(b, [(10, 60), (11, 56)], 4.0, 4.0)
    cavern(b, 96, 32, 7, 12, 0, 1.6)
    # the hermit's cell, up through the roof of the upper gallery
    cavern(b, 52, 6, 5, 3.5, 0, 2.4)
    tube(b, [(52, 17), (52, 8)], 2.6, 2.6)
    _place(zone, L, name, [(96, 32, "The Weeper"), (52, 6, "The Drowned Hermit")],
           [(14, 18), (74, 50), (90, 18)],
           {"The Lower Gallery": (8, 38, 90, 18), "The Upper Gallery": (8, 9, 90, 16),
            "The Weeping Pool": (88, 18, 16, 28), "The Hermit's Cell": (46, 1, 12, 9)})
    return zone, L


def dress_weeping(zone, L):
    P = L.prop
    for (x, y) in ((20, 47), (48, 46), (70, 49), (88, 46)):
        P("skull_pile", x, y, 2)
    P("rf_ore_cart", 30, 14, 3, solid="core")
    P("pl_skull_pile", 96, 40, 2, where=PL)
    P("rf_prison_cage", 55, 5, 3, solid="core")
    return zone, L


# ============================================================================================ THE MARRIS CRYPT
def build_marris():
    name = MARRIS
    zone, L = _new(name)
    b = L.b
    xs, ys = (16, 30, 60, 74), (14, 30, 48, 62)
    for x in xs:
        b.corridor([(x, 10), (x, 66)], width=2)
    for y in ys:
        b.corridor([(12, y), (78, y)], width=2)
    # the hall at the crossing, the chapel at the head, and the stair down from the stead
    b.rect(36, 30, 54, 48, chamfer=2)
    b.corridor([(45, 30), (45, 14)], width=3)
    b.rect(36, 3, 54, 12, chamfer=2)
    b.corridor([(45, 76), (45, 48)], width=3)
    # burial niches off the passages, on the mason's plan
    for x in xs:
        for y in (22, 40, 56):
            side = -1 if x < 45 else 1
            b.rect(x + 2 if side > 0 else x - 4, y - 1, x + 4 if side > 0 else x - 2, y + 1, chamfer=0)
    _place(zone, L, name, [(45, 39, "Sexton Hollowell"), (45, 7, "The Bone Choir")],
           [(10, 30), (80, 62), (20, 66)],
           {"The Sexton's Hall": (36, 30, 19, 19), "The Choir Chapel": (36, 3, 19, 10),
            "The West Niches": (8, 10, 26, 58), "The East Niches": (56, 10, 26, 58)})
    return zone, L


def dress_marris(zone, L):
    P = L.prop
    P("sarcophagus", 40, 34, 3, solid="core")
    P("sarcophagus", 50, 34, 3, solid="core")
    P("candelabra", 39, 45, 3)
    P("candelabra", 51, 45, 3)
    P("twilight_altar", 45, 4, 3, solid="core")
    P("candelabra", 39, 9, 3)
    P("candelabra", 51, 9, 3)
    for (x, y) in ((16, 22), (74, 40), (30, 56), (60, 22)):
        P("skull_pile", x, y, 2)
    return zone, L


# ============================================================================================ THE BONE MINES
def build_bone():
    name = BONE
    zone, L = _new(name)
    b = L.b
    # five galleries stacked into the hill, each turning back on the one before at a ramp; you come in at the
    # bottom of the map and every gallery is a level deeper (the portal sits at the south edge so you arrive
    # two tiles inside it, like every cave)
    rows = (84, 66, 48, 30, 12)
    for i, y in enumerate(rows):
        x0, x1 = (12, 88) if i % 2 == 0 else (88, 12)
        if i == len(rows) - 1:
            x1 = 70
        n = max(3, int(abs(x1 - x0) / 8) + 1)
        pts = [(x0 + (x1 - x0) * k / (n - 1), y + (1.5 if (k + i) % 2 else -1.5) * (0 < k < n - 1))
               for k in range(n)]
        tube(b, pts, 4.6, 4.6, ph=0.6 + i)
        if i < len(rows) - 1:
            # the ramp to the next gallery, at the far end
            tube(b, [(x1, y), (x1 + (3 if x1 > 50 else -3), y - 9), (x1, rows[i + 1])], 4.0, 4.0, ph=1.7 + i)
    tube(b, [(10, 90), (12, 84)], 4.0, 4.0)
    # the marrow pit at the end of the deepest gallery, and the Ossifier's workshop off the middle one
    cavern(b, 82, 12, 9, 7, 0, 2.3)
    cavern(b, 50, 57, 7, 4, 0, 1.4)
    tube(b, [(50, 48), (50, 54)], 3.0, 3.0)
    _place(zone, L, name, [(82, 12, "Overseer Marrowgrim"), (50, 58, "The Ossifier")],
           [(86, 84), (14, 48), (20, 12)],
           {"The First Workings": (6, 60, 88, 32), "The Middle Workings": (6, 42, 88, 18),
            "The Ossifier's Workshop": (42, 53, 16, 10), "The Deep Workings": (6, 4, 70, 34),
            "The Marrow Pit": (72, 4, 20, 16)})
    return zone, L


def dress_bone(zone, L):
    P = L.prop
    P("rf_ore_cart", 40, 84, 3, solid="core")
    P("rf_ore_cart", 60, 48, 3, solid="core")
    P("rf_tool_rack", 30, 66, 3, solid="core")
    P("skull_pile", 70, 66, 2)
    P("skull_pile", 24, 30, 2)
    P("pl_bone_barricade", 74, 14, 3, where=PL, solid="core")
    P("pl_skull_pile", 86, 16, 2, where=PL)
    P("rf_sacrificial_altar", 46, 58, 3, solid="core")
    return zone, L


BUILD = {WRITHING: (build_writhing, dress_writhing), WEEPING: (build_weeping, dress_weeping),
         MARRIS: (build_marris, dress_marris), BONE: (build_bone, dress_bone)}


def build(name):
    zone, L = BUILD[name][0]()
    BUILD[name][1](zone, L)
    L.finish([PORTAL[name]] + list(BOSSES[name].values()) + CHESTS[name])
    return zone, L


def generate(name):
    zone, _L = build(name)
    register_baked(zone, BAKED[name])
    return zone


def build_writhing_baked():
    return build(WRITHING)


def build_weeping_baked():
    return build(WEEPING)


def build_marris_baked():
    return build(MARRIS)


def build_bone_baked():
    return build(BONE)


if __name__ == "__main__":
    for n in CAVES:
        z, L = build(n)
        walk = sum(1 for y in range(z.height) for x in range(z.width) if z.is_walkable(x, y))
        print(n, z.width, "x", z.height, "| walkable", walk, "| bosses", list(BOSSES[n]), "| skipped", L.skipped)
