"""
Hand-built the Eldest Sequoia, Stonetalon's dungeon (30-33): TWO MAPS, and you climb (docs/stonetalon_brief.md).

Kyle, 15 Nov 2026: the dungeon is inside a standing sequoia, and it climbs UP - "Standing, climb UP". The
World-Root Hollow goes down under a tree's roots; this is its opposite. Map 1 is the trunk, map 2 the crown, and
after the last boss the way out drops you back at the foot of the tree, one way, like Glittervein's Cistern.

MAP 1: THE ELDEST SEQUOIA (100x124), the trunk. Read north = up the tree.
    The Burned Door (south) ..... in through the fire-split at the base
    The Rigging Hall ............ the Venture Co.'s ropes and winches, hauling up the trunk.   1 Rigboss Gazzle
    The Galleries (west) ........ bark beetles have bored the heartwood into a warren.         2 the Heartrot Queen
    The Sap Well (east) ......... the tree's sap pooled in a hollow ring. Optional.            3 Ambermaw
    The Heartwood Stair ......... up through the ring rooms, the growth rings as walls
    The Upper Trunk (north) ..... the way out onto the branches

MAP 2: THE ELDEST'S CROWN (112x100), branch walkways over open sky.
    The Great Bough (south) ..... out of the trunk onto the biggest branch
    The Nest (west) ............. a storm-roc's nest of whole trees.                           4 Old Talonwing
    The Topper's Rig (east) ..... the goblins' climbing shredder, come to top the tree.       5 Topper Kezzik
    The Crown (north) ........... the top of the tree, and the tree's own spirit.            6 The Eldest

THE SKY IS THE WALL on map 2: off a branch is down. The crown's "rock" is open air, painted by its own baker
(tools/bake_eldest_crown.py): the loop the branches ring in is the tree's foliage, everything else is the ground a
long way below, and every branch has a lush fringe of leaves. No walls anywhere (Kyle, 15 Nov 2026).

HARD CONTRACTS (world/portal_manager.py)
    trunk (50,120) <-> Stonetalon West (96,70)       the burned door
    trunk (50,3)   <-> crown (56,96)                 the top of the trunk onto the Great Bough
    crown (56,3)   ->  Stonetalon West (96,70)       ONE WAY: after the Eldest, back down to the foot of the tree
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

STP = "assets/tiles/stonetalon/props/"
TRUNK, CROWN = "The Eldest Sequoia", "The Eldest's Crown"
BAKED = {"trunk": "assets/tiles/stonetalon/baked_eldest_trunk", "crown": "assets/tiles/stonetalon/baked_eldest_crown"}

# ------------------------------------------------------------------------------------------------ the trunk
TW, TH = 100, 124
T_PORTAL, T_UP = (50, 120), (50, 3)
T_CAVERNS = {   # (cx, cy, rx, ry, rot, phase, name)
    "door":      (50, 114, 9, 6, 0, 0.4, "The Burned Door"),
    "rigging":   (50, 94, 18, 10, 0, 1.1, "The Rigging Hall"),
    "gal_a":     (24, 80, 8, 5, 20, 0.7, "The Galleries"),
    "gal_b":     (14, 64, 7, 6, 0, 1.9, "The Galleries"),
    "gal_c":     (30, 58, 6, 5, -15, 2.6, "The Galleries"),
    "queen":     (18, 42, 11, 8, 0, 1.3, "The Queen's Gallery"),
    "sapwell":   (80, 62, 12, 9, 0, 0.9, "The Sap Well"),
    "ring_a":    (50, 66, 12, 7, 0, 2.2, "The Heartwood Stair"),
    "ring_b":    (54, 42, 11, 7, 0, 0.6, "The Heartwood Stair"),
    "upper":     (50, 14, 16, 8, 0, 1.6, "The Upper Trunk"),
}
T_PATHS = {
    "in":        ([(50, 120), (50, 112), (50, 104)], 5.5, 6.0),
    "gal_1":     ([(36, 92), (28, 86), (24, 80)], 4.0, 4.0),
    "gal_2":     ([(22, 76), (16, 70), (14, 64)], 3.5, 3.5),
    "gal_3":     ([(16, 62), (24, 60), (30, 58)], 3.5, 3.5),
    "gal_4":     ([(14, 60), (14, 52), (18, 46)], 3.5, 3.5),
    "gal_back":  ([(28, 46), (38, 46), (46, 44)], 3.5, 3.5),       # the warren comes out on the stair
    "sap":       ([(64, 90), (74, 80), (80, 70)], 4.0, 4.0),
    "stair_1":   ([(50, 84), (50, 76), (50, 70)], 5.0, 5.0),
    "stair_2":   ([(52, 60), (54, 52), (54, 46)], 5.0, 5.0),
    "stair_3":   ([(54, 36), (52, 28), (50, 20)], 5.0, 5.0),
    "out":       ([(50, 10), (50, 6), (50, 3)], 4.0, 4.0),
}
T_SPINE = [(50, 30, 3.0, 4.0)]         # a knot in the heartwood the stair winds past
#: (x, y, name, required)
T_BOSSES = [(50, 92, "Rigboss Gazzle", True), (18, 40, "The Heartrot Queen", True), (82, 60, "Ambermaw", False)]
T_CHESTS = [(10, 66), (90, 64), (62, 12)]

# ------------------------------------------------------------------------------------------------ the crown
CW, CH = 112, 100
C_IN, C_OUT = (56, 96), (56, 3)
C_CAVERNS = {
    "bough":     (56, 86, 14, 6, 0, 0.5, "The Great Bough"),
    "fork":      (56, 62, 9, 6, 0, 1.4, "The Fork"),
    "nest":      (22, 34, 15, 11, 0, 0.9, "The Nest"),
    "rig":       (92, 32, 13, 9, 0, 2.1, "The Topper's Rig"),
    "crown":     (56, 14, 16, 9, 0, 1.7, "The Crown"),
}
C_PATHS = {   # the branches themselves: narrow, and over nothing
    "trunk":     ([(56, 96), (56, 90)], 4.5, 4.5),
    "up":        ([(56, 82), (56, 72), (56, 66)], 4.0, 4.0),
    "west_limb": ([(50, 60), (40, 52), (30, 44), (24, 40)], 3.2, 3.6),
    "east_limb": ([(62, 60), (74, 50), (84, 42), (90, 36)], 3.2, 3.6),
    "nest_up":   ([(26, 26), (36, 18), (44, 14)], 3.2, 3.2),
    "rig_up":    ([(88, 24), (76, 16), (68, 14)], 3.2, 3.2),
    "top":       ([(56, 8), (56, 5), (56, 3)], 3.5, 3.5),
    "spur_w":    ([(42, 86), (30, 82), (20, 78)], 2.8, 2.8),       # a dead-end branch with a chest on it
}
C_BOSSES = [(20, 32, "Old Talonwing", True), (94, 30, "Topper Kezzik", True), (56, 12, "The Eldest", True)]
C_CHESTS = [(18, 78), (96, 40)]

BOSSES = {"trunk": {}, "crown": {}}
CHESTS = {"trunk": [], "crown": []}


def _near(zone, x, y, rad=4):
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            if zone.is_walkable(int(x) + dx, int(y) + dy):
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, int(x) + dx, int(y) + dy)
    return None if best is None else (best[1], best[2])


def _carve(zone, L, caverns, paths, spines=()):
    b = L.b
    for i, (pts, w0, w1) in enumerate(paths.values()):
        tube(b, pts, w0, w1, ph=0.4 + i * 0.7)
    for (cx, cy, rx, ry, rot, ph, _n) in caverns.values():
        cavern(b, cx, cy, rx, ry, rot, ph)
    for (px_, py_, prx, pry) in spines:
        for y in range(int(py_ - pry) - 1, int(py_ + pry) + 2):
            for x in range(int(px_ - prx) - 1, int(px_ + prx) + 2):
                if ((x - px_) / prx) ** 2 + ((y - py_) / pry) ** 2 <= 1.0:
                    zone.collision_layer[y][x] = "wall"
                    zone.set_tile(x, y, "rock", "collision")


def _finish_common(zone, L, key, portals, bosses, chests, caverns, name):
    for (px, py) in portals:
        zone.collision_layer[py][px] = None
        L.mark("portal", px, py)
    fixed = []
    for (x, y, n, _req) in bosses:
        p = _near(zone, x, y)
        assert p, (n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    BOSSES[key].clear()
    BOSSES[key].update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = fixed[-1][:2] if key == "crown" else fixed[0][:2]
    zone.boss_positions = list(fixed)
    got = []
    for (x, y) in chests:
        p = _near(zone, x, y)
        assert p, (x, y)
        got.append(p)
        L.mark("chest", *p)
    CHESTS[key][:] = got
    zone.add_subzone(name, 0, 0, zone.width, zone.height)
    seen = set()
    for (cx, cy, rx, ry, _r, _p, sub) in caverns.values():
        zone.add_subzone(sub, int(cx - rx - 2), int(cy - ry - 2), int(2 * rx + 4), int(2 * ry + 4))
        seen.add(sub)


def build_trunk():
    zone = Tilemap(TRUNK, TW, TH, "Inside the greatest of Stonetalon's sequoias: hollowed by fire, bored by beetles, "
                                  "and the Venture Co. climbing it on ropes.")
    zone.is_cave = True
    zone.region = "Stonetalon West"
    L = CaveLayout(zone, (T_PORTAL[0], T_PORTAL[1] - 2))
    _carve(zone, L, T_CAVERNS, T_PATHS, T_SPINE)
    _finish_common(zone, L, "trunk", (T_PORTAL, T_UP), T_BOSSES, T_CHESTS, T_CAVERNS, TRUNK)
    return zone, L


def build_crown():
    zone = Tilemap(CROWN, CW, CH, "The crown of the Eldest Sequoia: branches as wide as roads, a sea of cloud below, "
                                  "and the tree's own spirit at the top.")
    zone.is_cave = True
    zone.region = "Stonetalon West"
    L = CaveLayout(zone, (C_IN[0], C_IN[1] - 2))
    _carve(zone, L, C_CAVERNS, C_PATHS)
    _finish_common(zone, L, "crown", (C_IN, C_OUT), C_BOSSES, C_CHESTS, C_CAVERNS, CROWN)
    return zone, L


def dress_trunk(zone, L):
    P = L.prop
    # the burned door: char and the first of the goblins' gear
    P("st_climbing_rig", 44, 112, 5, where=STP)
    P("st_powder_kegs", 57, 112, 3, where=STP, solid="core")
    # the Rigging Hall: winches and log sleds hauling up the trunk
    P("st_steam_winch", 38, 96, 4, where=STP, solid="core")
    P("st_steam_winch", 62, 96, 4, where=STP, solid="core")
    P("st_climbing_rig", 50, 86, 5, where=STP)
    P("st_log_sled", 36, 88, 3, where=STP, solid="core")
    # the galleries: beetle-bored heartwood and dead wood
    P("st_nurse_log", 20, 82, 3, where=STP, solid="core")
    P("st_log_redwood", 26, 56, 3, where=STP, solid="core")
    # the sap well
    P("st_moss_boulder", 72, 66, 3, where=STP, solid="core")
    # the upper trunk: light coming in
    P("st_climbing_rig", 40, 12, 5, where=STP)
    return zone, L


def dress_crown(zone, L):
    P = L.prop
    P("st_harpy_nest", 22, 38, 4, where=STP, solid="core")       # the roc's nest
    P("st_harpy_nest", 12, 30, 3, where=STP, solid="core")
    P("st_shredder_wreck", 98, 36, 4, where=STP, solid="core")   # a shredder that fell short
    P("st_climbing_rig", 86, 28, 5, where=STP)
    P("st_steam_winch", 100, 28, 4, where=STP, solid="core")
    P("st_ferns_big", 48, 16, 3, where=STP)
    P("st_ferns_big", 64, 16, 3, where=STP)
    return zone, L


def _trash_trunk():
    T = []

    def pack(lvl, *spots):
        T.append([(x, y, m, lvl) for (x, y, m) in spots])
    pack(30, (50, 108, "Venture Co. Hauler"), (46, 104, "Venture Co. Trunk Rigger"), (54, 104, "Venture Co. Hauler"))
    pack(31, (36, 100, "Venture Co. Trunk Rigger"), (32, 96, "Venture Co. Hauler"), (40, 100, "Venture Co. Sap Tapper"))
    pack(31, (64, 100, "Venture Co. Hauler"), (68, 96, "Venture Co. Trunk Rigger"), (60, 100, "Venture Co. Sap Tapper"))
    pack(31, (24, 80, "Heartrot Borer"), (20, 78, "Heartrot Borer"), (28, 82, "Heartrot Drone"))
    pack(31, (14, 64, "Heartrot Borer"), (10, 62, "Heartrot Drone"), (18, 66, "Heartrot Borer"))
    pack(32, (30, 58, "Heartrot Drone"), (26, 56, "Heartrot Borer"), (32, 56, "Heartrot Drone"))
    pack(31, (78, 72, "Living Sap"), (74, 70, "Venture Co. Sap Tapper"), (84, 70, "Living Sap"))
    pack(31, (50, 66, "Venture Co. Trunk Rigger"), (46, 64, "Heartrot Borer"), (54, 64, "Venture Co. Hauler"))
    pack(32, (54, 44, "Living Sap"), (50, 40, "Heartrot Drone"), (58, 40, "Venture Co. Sap Tapper"))
    pack(32, (50, 18, "Venture Co. Trunk Rigger"), (44, 14, "Venture Co. Hauler"), (56, 14, "Venture Co. Sap Tapper"))
    return T


def _trash_crown():
    T = []

    def pack(lvl, *spots):
        T.append([(x, y, m, lvl) for (x, y, m) in spots])
    pack(32, (56, 84, "Crown Owl"), (50, 86, "Crown Owl"), (62, 86, "Eldest's Warden"))
    pack(32, (56, 62, "Crown Sky Serpent"), (52, 60, "Crown Owl"), (60, 64, "Crown Sky Serpent"))
    pack(32, (32, 46, "Crown Sky Serpent"), (28, 42, "Crown Owl"), (36, 48, "Crown Owl"))
    pack(33, (22, 40, "Crown Sky Serpent"), (14, 36, "Crown Owl"), (30, 36, "Crown Sky Serpent"))
    pack(32, (80, 46, "Venture Co. Topper"), (76, 50, "Venture Co. Topper"), (84, 44, "Venture Co. Crown Shredder"))
    pack(33, (92, 36, "Venture Co. Crown Shredder"), (86, 32, "Venture Co. Topper"), (98, 32, "Venture Co. Topper"))
    pack(33, (44, 14, "Eldest's Warden"), (40, 16, "Crown Owl"), (48, 16, "Eldest's Warden"))
    pack(33, (68, 14, "Eldest's Warden"), (72, 16, "Venture Co. Topper"), (64, 16, "Eldest's Warden"))
    return T


def _snap(zone, spots, rad=5):
    out = []
    for (x, y, m, lvl) in spots:
        p = (x, y) if zone.is_walkable(x, y) else _near(zone, x, y, rad)
        if p is None:
            raise AssertionError(("trash with no floor near", m, x, y))
        out.append((p[0], p[1], m, lvl))
    return out


def _packs(zone, trash, portals):
    from world.dungeon_packs import attach_packs
    avoid = list(portals) + [tuple(b[:2]) for b in zone.boss_positions]
    return attach_packs(zone, [_snap(zone, p) for p in trash], avoid=avoid)


def build_trunk_baked():
    zone, L = build_trunk()
    dress_trunk(zone, L)
    L.finish([T_PORTAL, T_UP] + list(BOSSES["trunk"].values()) + CHESTS["trunk"])
    return zone, L


def build_crown_baked():
    zone, L = build_crown()
    dress_crown(zone, L)
    L.finish([C_IN, C_OUT] + list(BOSSES["crown"].values()) + CHESTS["crown"])
    return zone, L


def generate_eldest_trunk():
    zone, L = build_trunk_baked()
    _packs(zone, _trash_trunk(), (T_PORTAL, T_UP))
    register_baked(zone, BAKED["trunk"])
    return zone


def generate_eldest_crown():
    zone, L = build_crown_baked()
    _packs(zone, _trash_crown(), (C_IN, C_OUT))
    register_baked(zone, BAKED["crown"])
    return zone


if __name__ == "__main__":
    for f in (build_trunk_baked, build_crown_baked):
        z, L = f()
        seen = L._reach()
        crit = [c for c in L.critical if c not in seen]
        print(z.name, z.width, "x", z.height, "| bosses", z.boss_positions, "| critical unreachable", crit,
              "| skipped", L.skipped)
