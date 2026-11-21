"""
Hand-built The Stormsplit (84x100): the cave into the World Tree's trunk off the Upper Boughs' ring, 47-48
(docs/worldtree_brief.md, "Into the tree": one cave a tier).

Lightning split the trunk here, a long crack running down the grain, and the storm got in and couldn't get out. The
cave is the shape of the bolt that made it (the Knothollow was eaten and Shriekhollow grew round a shaft; this one was
struck): two long straight legs with one kink between them where it first struck, wide enough to run (Kyle, 18 Nov
2026: "dont make it too zig-zag as its hard to walk"; 20 Nov: "less zig zag for the tunnel, thatd be annoying to run
up"), and at the bottom the hall where the storm is trapped inside the tree. Off the kink a side split runs down to
where an old wyvern nested in the crack and was struck with it.
A cave, not a dungeon: trash rolled from the cave's own table, the two bosses pinned by the map.

    the way in (40,2) <- the Upper Boughs' ring (68,66), through the lightning-split stump
    THE SPLIT: the long straight crack down from the mouth
    THE FIRST STRIKE: the kink where the bolt struck, burned black
    THE SIDE SPLIT: the narrower crack off the kink
    THE SCORCHED NEST: the old wyvern's nest at the end of the side split, Old Charwing (optional)
    THUNDER HALL: the storm trapped at the bottom of the split, the Caught Storm

One way in and out; you arrive two tiles inside.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube
from world.chunk_paths import exists as _chunk_exists  # noqa: E402  (.webp, .jpg or .png)

NAME = "The Stormsplit"
W, H = 84, 100
BAKED = "assets/tiles/worldtree/baked_stormsplit"
BAKED_DIR = BAKED
PARENT = "The Upper Boughs"
DESC = ("A lightning split in the World Tree's trunk, running down the grain the way the bolt went. The storm got in "
        "and couldn't get out, and it's still down there.")
WTP = "assets/tiles/worldtree/props/"
ENT = "assets/tiles/cave_entrances/"

PORTAL = (40, 2)
PORTALS = {PORTAL: "The Upper Boughs"}
ARRIVALS = {PORTAL: (40, 4)}

#: the bolt: two long straight legs, one kink between them
LEG1 = [(40, 8), (46, 24), (52, 38)]
BEND1 = (53, 43, 10, 6)           # the kink: the first strike
LEG2 = [(52, 48), (51, 62), (50, 77)]
HALL = (50, 87, 17, 9)            # Thunder Hall
SIDE = [(45, 46), (30, 54), (18, 64), (13, 75)]
NEST = (12, 82, 8, 6)             # the Scorched Nest

BOSSES = {}
CHESTS = []
ROOM_NAMES = {}


def _near_walkable(zone, x, y, rad=5):
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            xx, yy = int(x) + dx, int(y) + dy
            if not zone.is_walkable(xx, yy):
                continue
            if zone.base_layer[yy][xx] in ("shallow_water", "deep_water"):
                continue
            d = dx * dx + dy * dy
            if best is None or d < best[0]:
                best = (d, xx, yy)
    return None if best is None else (best[1], best[2])


def build_stormsplit_baked():
    zone = Tilemap(NAME, W, H, DESC)
    zone.is_cave = True
    zone.region = PARENT
    zone.fixed_spawns = False
    L = CaveLayout(zone, ARRIVALS[PORTAL])
    b = L.b
    tube(b, [(40, 2), (40, 9)], 6.0, 7.0, ph=0.2)
    tube(b, LEG1, 7.5, 7.0, ph=0.4)
    cavern(b, *BEND1, 15, 0.7)
    tube(b, LEG2, 7.5, 7.5, ph=1.0)
    cavern(b, *HALL, 0, 2.1)
    tube(b, SIDE, 4.6, 4.0, ph=2.4)
    cavern(b, *NEST, 10, 2.7)
    for (px, py) in PORTALS:
        zone.collision_layer[py][px] = None
        L.mark("portal", px, py)
    fixed = []
    for (x, y, n) in [(HALL[0], HALL[1], "The Caught Storm"), (NEST[0], NEST[1], "Old Charwing")]:
        p = _near_walkable(zone, x, y)
        assert p, (n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (fixed[0][0], fixed[0][1])
    zone.boss_positions = list(fixed)
    CHESTS[:] = []
    for (x, y) in [(60, 40), (30, 55), (62, 90), (6, 84)]:
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        CHESTS.append(p)
        L.mark("chest", *p)
    zone.add_subzone(NAME, 0, 0, W, H)
    rooms = {"The Split": (30, 0, 36, 36), "The First Strike": (38, 36, 30, 16), "The Side Split": (10, 44, 38, 28),
             "The Scorched Nest": (0, 72, 24, 26), "Thunder Hall": (30, 70, 54, 30)}
    ROOM_NAMES.clear()
    for rname, (x, y, w, h) in rooms.items():
        zone.add_subzone(rname, x, y, w, h)
        ROOM_NAMES[rname] = (x, y, w, h)
    dress(zone, L)
    L.finish(list(PORTALS) + list(BOSSES.values()) + CHESTS)
    return zone, L


def dress(zone, L):
    """Kyle's World Tree props: lightning-struck wood, the old wyvern's nest, and the storm's leavings."""
    def P(name, x, y, h, where=WTP, **kw):
        p = _near_walkable(zone, x, y, rad=3)
        return L.prop(name, p[0], p[1], h, where=where, **kw) if p else L.skipped.append((name, x, y, "no floor"))
    P("ent_exit_cave_daylight", PORTAL[0], PORTAL[1] + 2, 5, where=ENT, near_ok=True)
    P("wt_dark_sap_split", 43, 14, 4, solid="core")
    P("wt_lightning_stump", 60, 44, 5, solid="core")      # where the bolt kinked
    P("wt_dead_stub", 24, 58, 4, solid="core")
    P("wt_wyvern_nest", NEST[0] + 2, NEST[1] - 3, 5, solid="core")
    P("wt_skull_rack", NEST[0] + 5, NEST[1] + 2, 4, solid="core")
    P("wt_lightning_stump", HALL[0] - 11, HALL[1] - 2, 5, solid="core")
    P("wt_lightning_stump", HALL[0] + 12, HALL[1] - 4, 5, solid="core")
    P("wt_crystal_shard", HALL[0] + 4, HALL[1] - 5, 4, solid="core")


def generate_stormsplit():
    zone, _L = build_stormsplit_baked()
    import os
    if os.path.isdir(BAKED) and _chunk_exists(f"{BAKED}/ground_0_0.jpg"):
        register_baked(zone, BAKED)
    return zone


if __name__ == "__main__":
    z, L = build_stormsplit_baked()
    walk = sum(1 for y in range(z.height) for x in range(z.width) if z.is_walkable(x, y))
    print(NAME, z.width, "x", z.height, "| walkable", walk, "| bosses", BOSSES, "| skipped", L.skipped)
