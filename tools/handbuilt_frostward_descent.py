"""
Hand-built The Frostward Descent (120x140): the cave system under the Alterac range that carries you from
Hillsbrad's frozen north down into the Crystalline Underdark. Levels 31-33.

ARCHETYPE: THE LONG WAY DOWN.  Not Dun Garok's gauntlet of gates, not Durnholde's broken ring, not Azurelode's
drowned workings, not Boulder Lode's switchback benches, not a spiral, wheel, rotunda or C-warren.  This is a real
WARREN - branching chambers, winding passage and dead ends worth walking - with exactly one rule holding it
together: every route trends DOWNWARD.  There is no corridor to follow, so the player is never on rails, and there
is never a wrong way, so the player is never lost.

ITS JOB IS A CHANGE, NOT A SHAPE.  The map crosses from Alterac ice to arcane crystal, and the crossing happens
ACROSS THE WARREN rather than along a line. The player is busy navigating and loses the frost gradually; the
intended moment is looking back and being unable to remember where it stopped.

    ICE      y 100-140  glacier, frozen watercourse, blue-white
    THE SEAM y  56-100  wet black rock, the first crystal veins, light in the walls
    ARCANE   y   8- 56  crystal, lattice growth, the stone making its own light

THE SET PIECE sits at the seam: a frozen expedition camp, iced over, decades old, a hundred paces from the first
lattice growth. Somebody was down here long before the Crimson Codex, and did not come back up.

CAVE, NOT DUNGEON - and that is a deliberate departure from the design doc, which called for fixed spawns.
This map is the ONLY route in or out of the Underdark, so the player will walk it many times. Hand-placed packs
would make their commute a corridor of corpses forever after the first clear. Random spawns keep it alive, and
keeping it off world/zone_classification.DUNGEONS also lets the ice chambers carry Frostpine the way the design
intended.

HARD CONTRACTS (world/portal_manager.py)
  (60, 134) <-> Eastern Hillsbrad, north of Gavin's Naze
  (58, 8)   <-> The Crystalline Underdark. The tile is carved and marked here; the LINK is registered only once
              that zone exists. An unregistered portal tile fails safe (zone_manager.try_use_portal returns
              False rather than teleporting somewhere undefined), so this is harmless until then.
Prop rule (Kyle): less is more; logical for the room; a few centrepieces.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401

BAKED = "assets/tiles/frostward_descent/baked"
UDP = "assets/tiles/underdark/props/"
W, H = 120, 140
PORTAL = (60, 134)            # up to Eastern Hillsbrad
EXIT = (58, 8)                # down into the Crystalline Underdark

#: Chambers as ellipse lobes - this is a natural cave, so nothing here is square. (Dun Garok is square
#: BECAUSE dwarves cut it; water and time cut this one.) Each entry is (cx, cy, rx, ry).
CHAMBERS = {
    # ---- ICE: the way in, and the last of Alterac
    "entry_hall":      (60, 127, 13, 8),
    "icefall":         (36, 114, 15, 10),
    "glacier_gallery": (86, 112, 14, 10),
    "ice_vault":       (20, 100, 9, 7),        # dead end
    "meltwater":       (62, 104, 11, 7),
    # ---- THE SEAM: where it stops being Azeroth
    "drip_hall":       (28, 84, 13, 9),
    "the_seam":        (62, 78, 19, 12),       # set piece + the named boss
    "vein_gallery":    (96, 76, 13, 9),
    "cold_cache":      (14, 64, 8, 6),         # dead end
    # ---- ARCANE: the Underdark reaching up to meet you
    "lattice_hall":    (56, 44, 17, 11),
    "crystal_vault":   (24, 38, 13, 9),
    "shardway":        (94, 40, 13, 9),
    "deep_cache":      (102, 16, 8, 6),        # dead end
    "threshold":       (58, 17, 14, 9),        # the door out
}

#: Winding passages. Deliberately more connections than a tree needs - a warren has loops, and a loop is what
#: stops a dead end from feeling like a mistake. corridor(width=N) clears ~2N+1 tiles, so these stay narrow.
PASSAGES = [
    # ice
    ([(60, 120), (50, 118), (44, 114)], 2),
    ([(60, 120), (72, 118), (80, 114)], 2),
    ([(36, 105), (28, 102), (22, 100)], 2),
    ([(44, 110), (54, 107), (60, 104)], 2),
    ([(74, 108), (68, 105), (62, 104)], 2),
    # ice -> seam
    ([(36, 105), (34, 96), (30, 88)], 2),
    ([(62, 98), (62, 90), (62, 86)], 2),
    ([(86, 103), (92, 92), (95, 84)], 2),
    # seam
    ([(40, 82), (50, 80), (48, 78)], 2),
    ([(80, 78), (88, 77), (86, 76)], 2),
    ([(22, 78), (16, 71), (14, 66)], 2),
    # seam -> arcane
    ([(28, 76), (26, 60), (24, 46)], 2),
    ([(62, 67), (60, 58), (57, 54)], 2),
    ([(96, 68), (95, 56), (94, 48)], 2),
    # arcane
    ([(40, 44), (33, 41), (36, 39)], 2),
    ([(72, 44), (82, 42), (82, 40)], 2),
    ([(56, 34), (57, 27), (58, 25)], 2),
    ([(94, 32), (100, 24), (102, 18)], 2),
    ([(94, 32), (76, 24), (68, 19)], 2),
]

BOSSES = {}
CHESTS = []


def _near_walkable(zone, x, y, rad=7):
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            if zone.is_walkable(int(x) + dx, int(y) + dy):
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, int(x) + dx, int(y) + dy)
    return None if best is None else (best[1], best[2])


def build_frostward_descent():
    zone = Tilemap("The Frostward Descent", W, H,
                   "A cave system under the Alterac range. It begins as glacier ice and ends as something that "
                   "makes its own light.")
    zone.is_cave = True
    # .region declares the PARENT ZONE (world/zone_manager.py:55) - the encounter lookup and the pull builder
    # key off it. Not a flavour label.
    zone.region = "Eastern Hillsbrad"
    zone.fixed_spawns = False
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b

    b.lobes([e for e in CHAMBERS.values()])
    for pts, w in PASSAGES:
        b.corridor(pts, width=w)

    for (px, py) in (PORTAL, EXIT):
        zone.collision_layer[py][px] = None
        zone.set_tile(px, py, "dirt", "base")
        zone.collision_layer[py - 1][px] = None
        L.mark("portal", px, py)

    # One beat per band rather than the single boss the design doc called for: 120x140 of warren with one
    # named thing in it is thin, and each band needs a reason to be walked rather than crossed.
    bosses = [(38, 114, "Hoarfang"),                       # ice
              (62, 78, "The Frozen Cartographer"),         # the seam, with the camp
              (56, 44, "Latticeborn")]                     # arcane
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
    for (x, y) in ((20, 100), (14, 64), (102, 16), (96, 76)):   # the three dead ends, plus one off the route
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        chests.append(p)
    CHESTS[:] = chests
    for c in chests:
        L.mark("chest", *c)

    zone.add_subzone("The Frostward Descent", 0, 0, W, H)   # the encounter-table key covers the whole map
    zone.add_subzone("The Frozen Course", 8, 92, 104, 48)
    zone.add_subzone("The Seam", 6, 52, 108, 42)
    zone.add_subzone("The Lattice Deeps", 8, 6, 104, 48)
    return zone, L


def finish(zone, L):
    targets = [PORTAL, EXIT] + [(x, y) for (x, y) in BOSSES.values()] + list(CHESTS)
    return L.finish(targets)


def dress(zone, L):
    P = L.prop
    U = dict(where=UDP)
    # ================= ICE: Alterac, and the last of it ======================================================
    P("ud_ice_stalagmites", 54, 124, 4, **U)
    P("ud_ice_stalagmites", 68, 122, 4, **U)
    P("den_torch", 60, 130, 4)
    P("ud_ice_stalagmites", 30, 118, 5, **U)
    P("ud_ice_stalagmites", 44, 108, 4, **U)
    P("bbc_rubble", 24, 112, 3, solid="core")
    P("ud_ice_stalagmites", 92, 116, 5, **U)
    P("ud_ice_stalagmites", 80, 106, 4, **U)
    P("den_rock_rubble", 88, 104, 3)
    # the dead-end ice vault: somebody cached supplies here and never came back for them
    P("ud_frozen_crate", 16, 103, 3, **U)
    P("ud_frozen_crate", 23, 101, 3, **U)

    # ================= THE SEAM: the set piece ===============================================================
    # A frozen expedition camp, iced over, decades old - and the first lattice a hundred paces away. The whole
    # argument of the map is these two things being visible from the same spot.
    P("ud_frozen_crate", 54, 82, 3, **U)
    P("ud_frozen_crate", 58, 85, 3, **U)
    P("den_campfire_ashes", 57, 80, 2)
    P("den_backpack", 52, 78, 2)
    P("ud_ice_stalagmites", 48, 84, 4, **U)
    P("bbc_skull_pile", 55, 74, 3)
    P("ud_lattice_growth", 70, 76, 5, **U)          # <- the first lattice, in the same chamber
    P("ud_crystal_violet", 74, 80, 4, **U)
    P("ud_glow_pool", 62, 72, 3, **U)
    # the rest of the seam
    P("den_rock_rubble", 30, 88, 3)
    P("ud_glow_pool", 26, 82, 3, **U)
    P("den_torch", 20, 80, 4)
    P("ud_crystal_violet", 98, 80, 4, **U)
    P("ud_lichen_boulder", 92, 74, 3, **U)
    P("ud_frozen_crate", 17, 67, 3, **U)

    # ================= ARCANE: the Underdark reaching up ======================================================
    P("ud_lattice_growth", 50, 48, 6, **U)
    P("ud_lattice_growth", 64, 46, 6, **U)
    P("ud_crystal_spire", 56, 40, 7, **U)
    P("ud_crystal_float", 60, 50, 4, **U)
    P("ud_glow_pool", 48, 41, 3, **U)
    P("ud_crystal_violet", 20, 42, 5, **U)
    P("ud_crystal_cyan", 28, 35, 5, **U)
    P("ud_geode_open", 24, 44, 4, **U)
    P("ud_crystal_cyan", 90, 44, 5, **U)
    P("ud_crystal_violet", 98, 37, 5, **U)
    P("ud_lichen_boulder", 88, 36, 3, **U)
    P("ud_crystal_float", 105, 21, 4, **U)
    # the threshold: you can already see the Underdark's light from here
    P("ud_crystal_spire", 50, 20, 7, **U)
    P("ud_crystal_spire", 66, 20, 7, **U)
    P("ud_moss_curtain", 58, 13, 5, **U)
    P("ud_glow_pool", 58, 22, 3, **U)
    return zone, L


def generate_frostward_descent():
    zone, L = build_frostward_descent()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_frostward_descent_baked():
    """(zone, layout) with props + QA done - what the baker paints from."""
    zone, L = build_frostward_descent()
    dress(zone, L)
    finish(zone, L)
    return zone, L
