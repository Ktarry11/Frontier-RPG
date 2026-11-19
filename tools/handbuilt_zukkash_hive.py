"""
Hand-built The Zukk'ash Hive (104x124): the Zukk'ash hive under the High Wilderness, Feralas, 47-49
(docs/feralas_brief.md).

THE NAME: Kyle asked for "the writhing deep in Feralas", but the Plaguelands already have a cave called The Writhing
Deep (the spiders under South Western Plaguelands), and two maps can't share a name. So Feralas's is the Zukk'ash Hive
(the classic hive's own name) until Kyle says otherwise.

Kyle, 19 Nov 2026: "We can also have the writhing deep in Feralas connect to the map under Abyssal Sands. Since the
silithids are digging....", and of what it is in play: "A hive cave, tunnel at the back". A cave, not a dungeon: trash
rolled from the cave's own table (fixed_spawns False), the bosses pinned by the map.

THE SHAPE IS A DIG, NOT A STRING OF BLOBS. Silithids don't hollow rooms out, they follow a line and brood off it:

    the way in (52,2) <- the High Wilderness's Hive Fields (176,142), where the mound broke the forest floor
    THE GALLERY: the main shaft, winding down from the mouth through the wet forest earth, roots in the walls
    THE BROOD CELLS: short blind galleries off the shaft, each ending in a cell of eggs (three, west, east, west)
    THE DEEP MOTHER'S CHAMBER: where the shaft levels out, the queen's chamber, wide and low, resin all through it
    THE DIG: past the chamber the line carries on, narrower and still being dug, the wet earth drying to dark sand
             as it goes, down to the dig's head where Tunnelmaster Zix'tal drives the workers
    the way through (52,121) -> The Dry Deep (3,37): the tunnel comes out in the Brine Seep, under the Abyssal Sands

Both ways are portals; you arrive two tiles inside each.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

NAME = "The Zukk'ash Hive"
W, H = 104, 124
BAKED = "assets/tiles/feralas/baked_zukkash_hive"
BAKED_DIR = BAKED
PARENT = "The High Wilderness"
DESC = ("The Zukk'ash hive under Feralas, dug down from the forest floor along one long line. Past the queen's "
        "chamber the silithids are still digging, and the tunnel doesn't stop.")
STP = "assets/tiles/stonetalon/props/"
DP = "assets/tiles/dungeon_props/"
ENT = "assets/tiles/cave_entrances/"

PORTAL = (52, 2)                  # up to the High Wilderness
THROUGH = (52, 121)               # on through the tunnel to the Dry Deep
PORTALS = {PORTAL: "The High Wilderness", THROUGH: "The Dry Deep"}
ARRIVALS = {PORTAL: (52, 4), THROUGH: (52, 119)}

#: the main shaft, winding down (Kyle, 18 Nov 2026: "dont make it too zig-zag as its hard to walk")
GALLERY = [(52, 2), (50, 12), (56, 22), (50, 32), (56, 42), (52, 52), (56, 60)]
#: the brood cells: (where the cell gallery leaves the shaft, its line, the cell)
BROOD = [((50, 12), [(38, 14)], (26, 18)), ((51, 32), [(66, 30)], (80, 26)), ((54, 46), [(40, 48)], (26, 52))]
CHAMBER = (60, 70, 17, 9)          # the Deep Mother's chamber: cx, cy, rx, ry (wide and low)
DIG = [(74, 74), (82, 84), (76, 96), (64, 104), (56, 112), (52, 121)]
DIG_HEAD = (58, 110)

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


def build_zukkash_hive_baked():
    zone = Tilemap(NAME, W, H, DESC)
    zone.is_cave = True
    zone.region = PARENT
    zone.fixed_spawns = False
    L = CaveLayout(zone, ARRIVALS[PORTAL])
    b = L.b
    tube(b, GALLERY, 6.0, 7.0, ph=0.3)
    cavern(b, 52, 6, 6, 4, 0, 0.4)                      # the mouth's landing
    for i, (start, line, cell) in enumerate(BROOD):
        tube(b, [start] + line + [cell], 3.6, 3.2, ph=1.2 + i)
        cavern(b, cell[0], cell[1], 6.0, 4.6, 20 * (i - 1), 0.7 + i)
    cavern(b, *CHAMBER, 6, 0.9)
    tube(b, [(56, 60), (58, 66)], 6.0, 7.0, ph=0.5)
    tube(b, [(70, 72)] + DIG, 6.0, 4.6, ph=1.9)
    cavern(b, DIG_HEAD[0], DIG_HEAD[1], 6, 4, -20, 1.3)
    cavern(b, 52, 117, 5, 4, 0, 2.1)                     # the tunnel's far end, where it opens
    for (px, py) in PORTALS:
        zone.collision_layer[py][px] = None
        L.mark("portal", px, py)
    fixed = []
    for (x, y, n) in [(CHAMBER[0], CHAMBER[1] - 2, "The Deep Mother"), (DIG_HEAD[0], DIG_HEAD[1], "Tunnelmaster Zix'tal")]:
        p = _near_walkable(zone, x, y)
        assert p, (n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (fixed[0][0], fixed[0][1])
    zone.boss_positions = list(fixed)
    CHESTS[:] = []
    for (x, y) in [(26, 18), (80, 26), (26, 52), (72, 66)]:
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        CHESTS.append(p)
        L.mark("chest", *p)
    zone.add_subzone(NAME, 0, 0, W, H)
    rooms = {"The Gallery": (40, 0, 26, 62), "The Brood Cells": (14, 8, 80, 52),
             "The Deep Mother's Chamber": (42, 58, 38, 22), "The Dig": (48, 78, 44, 46)}
    ROOM_NAMES.clear()
    for rname, (x, y, w, h) in rooms.items():
        zone.add_subzone(rname, x, y, w, h)
        ROOM_NAMES[rname] = (x, y, w, h)
    dress(zone, L)
    L.finish(list(PORTALS) + list(BOSSES.values()) + CHESTS)
    return zone, L


def dress(zone, L):
    def P(name, x, y, h, where=STP, **kw):
        p = _near_walkable(zone, x, y, rad=3)
        return L.prop(name, p[0], p[1], h, where=where, **kw) if p else L.skipped.append((name, x, y, "no floor"))
    # the way in, and the way through, both with their own mouths
    P("ent_exit_cave_daylight", PORTAL[0], PORTAL[1] + 2, 5, where=ENT, near_ok=True)
    P("ent_exit_kobold_tunnel", THROUGH[0], THROUGH[1] - 1, 5, where=ENT, near_ok=True)
    # the gallery: roots through the walls near the top, where the forest is still overhead
    P("st_nurse_log", 46, 16, 3, solid="core")
    P("st_moss_boulder", 58, 28, 3, solid="core")
    P("st_redwood_burl", 46, 38, 3, solid="core")
    # the brood cells' eggs, and the queen's chamber
    for (_s, _l, cell) in BROOD:
        P("st_pumice_pile", cell[0] + 4, cell[1] - 1, 3, solid="core")
    P("st_sequoia_rootplate", CHAMBER[0], CHAMBER[1] - 7, 5, solid="core")
    P("st_pumice_pile", CHAMBER[0] - 10, CHAMBER[1] + 2, 3, solid="core")
    P("st_pumice_pile", CHAMBER[0] + 10, CHAMBER[1] + 2, 3, solid="core")
    # the dig: spoil heaps and the diggers' leavings, drying to sand
    P("st_sawdust_pile", 80, 86, 3, solid="core")
    P("st_obsidian_boulder", 70, 100, 3, solid="core")
    P("st_pumice_pile", 62, 106, 3, solid="core")


def generate_zukkash_hive():
    zone, _L = build_zukkash_hive_baked()
    import os
    if os.path.isdir(BAKED) and os.path.exists(f"{BAKED}/ground_0_0.jpg"):
        register_baked(zone, BAKED)
    return zone


if __name__ == "__main__":
    z, L = build_zukkash_hive_baked()
    walk = sum(1 for y in range(z.height) for x in range(z.width) if z.is_walkable(x, y))
    print(NAME, z.width, "x", z.height, "| walkable", walk, "| bosses", BOSSES, "| skipped", L.skipped)
