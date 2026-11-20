"""
Hand-built Shriekhollow (84x100): the cave into the World Tree's trunk off the Middle Boughs' terraces, 45-47
(docs/worldtree_brief.md, "Into the tree": one cave a tier).

The trunk rotted hollow round a shaft that drops away into the dark, and the blighted harpies moved in. They roost
on the ledges round the shaft, they've hung their nests up the hollow's throat, and their matron keeps the eyrie at the top of
it. Below the eyrie the rot goes on down, and in the dark at the bottom something grew that the harpies feed and
won't go near. A cave, not a dungeon: trash rolled from the cave's own table, the two bosses pinned by the map.

THE SHAPE IS GROWN, NOT EATEN (the Knothollow's borers chewed theirs). A hollow is round:

    the way in (40,2) <- the Middle Boughs' terraces (16,82), through a split in the bark
    THE ROOST: a ring of ledges round the Well, where the hollow's floor drops away into the trunk
    THE THROAT: the hollow climbing on from the Roost, with the nests hung in side hollows off it
    THE EYRIE: the matron's chamber at the top of the throat, Matron Vyssa
    THE ROTDARK: past the eyrie the rot goes down to where Old Splinterheart grew in the dark (optional)

One way in and out; you arrive two tiles inside.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube, wall_annulus

NAME = "Shriekhollow"
W, H = 84, 100
BAKED = "assets/tiles/worldtree/baked_shriekhollow"
BAKED_DIR = BAKED
PARENT = "The Middle Boughs"
DESC = ("A hollow in the World Tree's trunk, rotted out round a shaft that drops into the dark. The blighted harpies roost "
        "in it, and something at the bottom of it they feed and won't go near.")
WTP = "assets/tiles/worldtree/props/"
ENT = "assets/tiles/cave_entrances/"

PORTAL = (40, 2)                  # out to the Middle Boughs' terraces
PORTALS = {PORTAL: "The Middle Boughs"}
ARRIVALS = {PORTAL: (40, 4)}

ROOST = (40, 20, 15, 11)          # the hollow round the Heartpost: cx, cy, rx, ry
HEARTPOST = 5.0                   # the Well: the shaft in the Roost's middle (radius), walled so nobody falls
#: the throat climbing on from the Roost, gently (Kyle, 18 Nov 2026: "dont make it too zig-zag as its hard to walk")
THROAT = [(46, 31), (52, 40), (46, 50), (52, 58)]
#: the nests hung in side hollows off the throat: (where it leaves, its line)
NESTS = [((50, 37), [(64, 32), (70, 26)]), ((47, 48), [(32, 50), (22, 46)]), ((52, 57), [(66, 60), (72, 66)])]
EYRIE = (44, 68, 14, 8)           # the matron's chamber at the top of the throat
ROTDARK = [(34, 74), (30, 82), (38, 90)]
DARK = (48, 92, 9, 5)             # where Old Splinterheart grew

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


def build_shriekhollow_baked():
    zone = Tilemap(NAME, W, H, DESC)
    zone.is_cave = True
    zone.region = PARENT
    zone.fixed_spawns = False
    L = CaveLayout(zone, ARRIVALS[PORTAL])
    b = L.b
    tube(b, [(40, 2), (40, 9)], 6.0, 7.0, ph=0.4)         # through the split in the bark
    cavern(b, *ROOST, 0, 0.3)
    tube(b, [(48, 26)] + THROAT, 6.5, 6.0, ph=0.6)
    for i, (start, line) in enumerate(NESTS):
        tube(b, [start] + line, 4.2, 3.4, ph=1.3 + i)
        end = line[-1]
        cavern(b, end[0], end[1], 5.0, 4.0, 20 * (i - 1), 0.9 + i)
    tube(b, [(52, 58), (48, 63)], 6.0, 6.5, ph=0.5)
    cavern(b, *EYRIE, -8, 1.1)
    tube(b, [(38, 72)] + ROTDARK, 5.0, 4.4, ph=1.9)
    cavern(b, *DARK, 10, 1.6)
    # the Well: the shaft drops away in the Roost's middle, so the Roost is a ring of ledges round it
    wall_annulus(zone, ROOST[0], ROOST[1], 0.0, HEARTPOST, gates=())
    for (px, py) in PORTALS:
        zone.collision_layer[py][px] = None
        L.mark("portal", px, py)
    fixed = []
    for (x, y, n) in [(EYRIE[0] + 2, EYRIE[1], "Matron Vyssa"), (DARK[0], DARK[1], "Old Splinterheart")]:
        p = _near_walkable(zone, x, y)
        assert p, (n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (fixed[0][0], fixed[0][1])
    zone.boss_positions = list(fixed)
    CHESTS[:] = []
    for (x, y) in [(70, 26), (22, 46), (72, 66), (28, 22)]:
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        CHESTS.append(p)
        L.mark("chest", *p)
    zone.add_subzone(NAME, 0, 0, W, H)
    rooms = {"The Roost": (22, 6, 38, 28), "The Throat": (14, 30, 66, 32), "The Eyrie": (28, 58, 34, 18),
             "The Rotdark": (22, 74, 40, 26)}
    ROOM_NAMES.clear()
    for rname, (x, y, w, h) in rooms.items():
        zone.add_subzone(rname, x, y, w, h)
        ROOM_NAMES[rname] = (x, y, w, h)
    dress(zone, L)
    L.finish(list(PORTALS) + list(BOSSES.values()) + CHESTS)
    return zone, L


def dress(zone, L):
    """Kyle's World Tree props (sheet W2): the harpies' nests and litter, the rot below them."""
    def P(name, x, y, h, where=WTP, **kw):
        p = _near_walkable(zone, x, y, rad=3)
        return L.prop(name, p[0], p[1], h, where=where, **kw) if p else L.skipped.append((name, x, y, "no floor"))
    P("ent_exit_cave_daylight", PORTAL[0], PORTAL[1] + 2, 5, where=ENT, near_ok=True)
    # the Roost: nests on the ledges round the Heartpost
    P("wt_harpy_nest", 28, 16, 4, solid="core")
    P("wt_harpy_nest", 53, 24, 4, solid="core")
    P("wt_shelf_fungus", 30, 27, 3, solid="core")
    P("wt_knot_hole", 50, 13, 4, solid="core")
    # the throat and its nests
    P("wt_harpy_nest", 64, 31, 4, solid="core")
    P("wt_harpy_nest", 28, 50, 4, solid="core")
    P("wt_harpy_nest", 65, 60, 4, solid="core")
    P("wt_pale_mushrooms", 48, 44, 3, solid=False)
    P("wt_sap_drip", 56, 52, 4, solid="core")
    # the eyrie: the matron's nest, bigger than the rest
    P("wt_harpy_nest", EYRIE[0] - 6, EYRIE[1] - 3, 6, solid="core")
    P("wt_skull_rack", EYRIE[0] + 8, EYRIE[1] - 2, 4, solid="core")
    # the rotdark: the rot the harpies won't go into
    P("wt_rot_pit", 30, 80, 4, solid="core")
    P("wt_rot_sac", DARK[0] + 6, DARK[1] - 2, 4, solid="core")
    P("wt_rot_fungus", DARK[0] - 7, DARK[1] + 1, 4, solid="core")
    P("wt_dark_sap_split", 56, 90, 4, solid="core")


def generate_shriekhollow():
    zone, _L = build_shriekhollow_baked()
    import os
    if os.path.isdir(BAKED) and os.path.exists(f"{BAKED}/ground_0_0.jpg"):
        register_baked(zone, BAKED)
    return zone


if __name__ == "__main__":
    z, L = build_shriekhollow_baked()
    walk = sum(1 for y in range(z.height) for x in range(z.width) if z.is_walkable(x, y))
    print(NAME, z.width, "x", z.height, "| walkable", walk, "| bosses", BOSSES, "| skipped", L.skipped)
