"""
Hand-built The Knothollow (84x100): the cave into the World Tree's trunk off the Lower Boughs' ledge, 44-45
(docs/worldtree_brief.md, "Into the tree").

Kyle, 19 Nov 2026: "We likely will need a 'Dungeon' and some 'caves' where these are just going deeper into the world
tree a bit". This is the first of them. A great knot in the trunk has rotted hollow behind its face, and the bark-borers
found it: they've eaten their way in and down through the wood toward the sap. A cave, not a dungeon: trash rolled from
the cave's own table (fixed_spawns False), the two bosses pinned by the map.

THE SHAPE IS EATEN, NOT DUG. Borers chew along the grain and turn back on themselves, so the galleries wind and
leave short dead-end bores off every bend:

    the way in (40,2) <- the Lower Boughs' ledge (62,16), through the knot's face
    THE KNOT: the round hollow just inside, where the wood rotted out first; daylight through the knot's mouth
    THE BORER GALLERIES: the galleries winding down from it along the grain, the bores branching off them
    THE SAPWELL: where the borers broke into a vein of sap; a chamber of gold, and Gnawmother Ixx, who laid them
    THE HEARTWARD BORE: past the Sapwell one bore carries on, down to where the bark turns to heartwood and the sap
                        has pooled and swollen into the Amber Glut (optional: you can turn back at the Sapwell)

One way in and out; you arrive two tiles inside.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube
from world.chunk_paths import exists as _chunk_exists  # noqa: E402  (.webp, .jpg or .png)

NAME = "The Knothollow"
W, H = 84, 100
BAKED = "assets/tiles/worldtree/baked_knothollow"
BAKED_DIR = BAKED
PARENT = "The Lower Boughs"
DESC = ("A great knot in the World Tree's trunk, rotted hollow behind its face. The bark-borers have eaten their way in "
        "and down through the wood toward the sap.")
WTP = "assets/tiles/worldtree/props/"
ENT = "assets/tiles/cave_entrances/"

PORTAL = (40, 2)                  # out to the Lower Boughs' ledge
PORTALS = {PORTAL: "The Lower Boughs"}
ARRIVALS = {PORTAL: (40, 4)}

KNOT = (40, 11, 10, 7)            # the hollow behind the knot: cx, cy, rx, ry
#: the galleries winding down along the grain (Kyle, 18 Nov 2026: "dont make it too zig-zag as its hard to walk")
GALLERY = [(40, 16), (32, 26), (42, 36), (34, 46), (44, 56)]
#: the dead-end bores off the bends: (where it leaves, its line)
BORES = [((32, 26), [(18, 24), (12, 30)]), ((42, 36), [(58, 32), (66, 38)]), ((34, 46), [(20, 50), (16, 58)])]
SAPWELL = (52, 66, 15, 9)         # the vein of sap the borers broke into
HEARTWARD = [(60, 74), (64, 82), (56, 90)]
HEART = (48, 92, 9, 5)            # where the bark turns to heartwood

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


def build_knothollow_baked():
    zone = Tilemap(NAME, W, H, DESC)
    zone.is_cave = True
    zone.region = PARENT
    zone.fixed_spawns = False
    L = CaveLayout(zone, ARRIVALS[PORTAL])
    b = L.b
    tube(b, [(40, 2), (40, 6)], 6.0, 7.0, ph=0.2)        # through the knot's mouth
    cavern(b, *KNOT, 0, 0.4)
    tube(b, GALLERY, 6.0, 6.5, ph=0.3)
    for i, (start, line) in enumerate(BORES):
        tube(b, [start] + line, 4.0, 3.2, ph=1.1 + i)
        end = line[-1]
        cavern(b, end[0], end[1], 4.6, 3.8, 25 * (i - 1), 0.6 + i)
    tube(b, [(44, 56), (48, 60)], 6.0, 6.5, ph=0.5)
    cavern(b, *SAPWELL, 10, 0.9)
    tube(b, [(60, 70)] + HEARTWARD, 5.0, 4.4, ph=1.7)
    cavern(b, *HEART, -10, 1.4)
    for (px, py) in PORTALS:
        zone.collision_layer[py][px] = None
        L.mark("portal", px, py)
    fixed = []
    for (x, y, n) in [(SAPWELL[0], SAPWELL[1] - 2, "Gnawmother Ixx"), (HEART[0], HEART[1], "The Amber Glut")]:
        p = _near_walkable(zone, x, y)
        assert p, (n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (fixed[0][0], fixed[0][1])
    zone.boss_positions = list(fixed)
    CHESTS[:] = []
    for (x, y) in [(12, 30), (66, 38), (16, 58), (64, 66)]:
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        CHESTS.append(p)
        L.mark("chest", *p)
    zone.add_subzone(NAME, 0, 0, W, H)
    rooms = {"The Knot": (28, 0, 26, 20), "The Borer Galleries": (6, 18, 70, 44),
             "The Sapwell": (34, 56, 38, 20), "The Heartward Bore": (36, 72, 36, 28)}
    ROOM_NAMES.clear()
    for rname, (x, y, w, h) in rooms.items():
        zone.add_subzone(rname, x, y, w, h)
        ROOM_NAMES[rname] = (x, y, w, h)
    dress(zone, L)
    L.finish(list(PORTALS) + list(BOSSES.values()) + CHESTS)
    return zone, L


def dress(zone, L):
    """Kyle's World Tree props (sheet W2): fungus and sap on the walls, the borers' leavings, the heart's glow."""
    def P(name, x, y, h, where=WTP, **kw):
        p = _near_walkable(zone, x, y, rad=3)
        return L.prop(name, p[0], p[1], h, where=where, **kw) if p else L.skipped.append((name, x, y, "no floor"))
    # the way in: daylight through the knot's mouth
    P("ent_exit_cave_daylight", PORTAL[0], PORTAL[1] + 2, 5, where=ENT, near_ok=True)
    # the knot: rot and fungus where the wood went soft first
    P("wt_shelf_fungus", 32, 10, 4, solid="core")
    P("wt_pale_mushrooms", 48, 14, 3, solid=False)
    P("wt_rot_fungus", 46, 8, 4, solid="core")
    # the galleries and their bores: the borers' leavings, sap weeping from the cut wood
    P("wt_sap_drip", 36, 30, 4, solid="core")
    P("wt_root_knuckle", 22, 26, 3, solid="core")
    P("wt_dark_sap_split", 60, 34, 4, solid="core")
    P("wt_rot_sac", 13, 60, 4, solid="core")
    P("wt_pale_mushrooms", 40, 48, 3, solid=False)
    # the Sapwell: the vein of sap, and what the mother's laid round it
    P("wt_sap_blister", SAPWELL[0] - 10, SAPWELL[1] + 3, 5, solid="core")
    P("wt_sap_blister", SAPWELL[0] + 11, SAPWELL[1] + 2, 5, solid="core")
    P("wt_seed_pod", SAPWELL[0] - 4, SAPWELL[1] + 5, 3, solid="core")
    P("wt_rot_pit", SAPWELL[0] + 6, SAPWELL[1] - 6, 4, solid="core")
    # the heartward bore: the heartwood showing gold through the bark
    P("wt_sap_drip", 62, 80, 4, solid="core")
    P("wt_bark_pool", HEART[0] - 6, HEART[1] + 2, 4, solid="core")


def generate_knothollow():
    zone, _L = build_knothollow_baked()
    import os
    if os.path.isdir(BAKED) and _chunk_exists(f"{BAKED}/ground_0_0.jpg"):
        register_baked(zone, BAKED)
    return zone


if __name__ == "__main__":
    z, L = build_knothollow_baked()
    walk = sum(1 for y in range(z.height) for x in range(z.width) if z.is_walkable(x, y))
    print(NAME, z.width, "x", z.height, "| walkable", walk, "| bosses", BOSSES, "| skipped", L.skipped)
