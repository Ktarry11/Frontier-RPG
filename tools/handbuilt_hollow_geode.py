"""
Hand-built The Hollow Geode (110x110): a crystal cavity in the Underdark's eastern wall. Levels 34-37.

ARCHETYPE: THE CLOSING BUBBLE.  Kyle, on the first draft of this: "even if it's enormous let's make it still
look good, no massive open trash - a true geode isn't just open space." He is right, and the correction is the
design. A geode is not a hollow ball. It is a cavity that crystal has been filling for a very long time and has
very nearly finished, so the space you walk is THE GAP THAT IS LEFT.

That gives the map its shape without a single empty room:

    THE DRUSE GALLERY   an outer ring just inside the shell, broken into six bays by crystal masses that have
                        grown inward from the wall. You work around it, and the ring winds rather than runs.
    THREE THROATS       where crystal from the wall has nearly met crystal from within. The only ways inward.
    THE INNER CAVITY    four lobes around the core, smaller and tighter than the gallery
    ONE LAST THROAT     the narrowest
    THE CORE            still open, still growing, and the only chamber here that has any room in it

Concentric shells with narrow throats, which is both how a geode actually forms in layers and a shape nothing
else in the game uses - Durnholde is a curtain wall around a courtyard, the Broodspiral is a spiral, Dun Garok a
sequence of gates in a line. This one closes inward.

Nothing is wider than it has to be. The core is the ONLY generous space on the map, and it is generous because
it is the one part the crystal has not finished eating.

CAVE, not dungeon: random spawns, and it inherits the Underdark's gathering.

HARD CONTRACT (world/portal_manager.py): portal (55, 104) <-> The Crystalline Underdark (150, 62).
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401

BAKED = "assets/tiles/hollow_geode/baked"
UDP = "assets/tiles/underdark/props/"
W, H = 110, 110
PORTAL = (55, 104)
CX, CY = 55, 54                 # the cavity's centre

#: Outer ring: six bays, deliberately unequal. A geode's cavity is not a circle and the bays should not be
#: interchangeable - two of them are cramped, one is nearly a dead end, and that unevenness is what stops a
#: ring from reading as a racetrack.
BAYS = {
    "south_bay":  (57, 92, 15, 8),
    "southwest":  (26, 80, 11, 10),
    "west_bay":   (16, 50, 9, 13),
    "north_bay":  (50, 14, 16, 8),
    "northeast":  (86, 28, 12, 9),
    "east_bay":   (94, 62, 9, 12),
}
#: Inner cavity: four lobes, tighter than the bays.
INNER = {
    "inner_n": (55, 30, 13, 7),
    "inner_e": (80, 54, 7, 11),
    "inner_s": (55, 76, 13, 7),
    "inner_w": (30, 54, 7, 11),
}
CORE = (CX, CY, 12, 11)

#: Dead-end pockets off the gallery - a geode has blind vugs, and they are where the chests go.
VUGS = {
    "vug_a": (14, 76, 6, 5),
    "vug_b": (98, 90, 6, 5),
    "vug_c": (90, 12, 6, 5),
}

#: (points, width). The ring links are narrow on purpose: crystal has grown nearly across them.
#: corridor(width=N) clears about 2N+1 tiles, so 1 means a genuine squeeze.
GALLERY = [
    ([(50, 92), (34, 86), (28, 80)], 1),          # south bay -> southwest
    ([(24, 74), (18, 62), (16, 56)], 1),          # southwest -> west
    ([(18, 44), (28, 26), (44, 16)], 1),          # west -> north
    ([(62, 15), (78, 20), (86, 26)], 1),          # north -> northeast
    ([(90, 36), (94, 50), (94, 58)], 1),          # northeast -> east
    ([(94, 70), (80, 86), (66, 92)], 1),          # east -> south bay (closes the ring)
    ([(22, 80), (16, 78)], 1),                    # the vugs
    ([(96, 72), (99, 80), (98, 86)], 1),
    ([(88, 24), (90, 18), (90, 14)], 1),
]
#: The inner cavity is a ring too. Without this the four inner lobes each hang off their own throat and never
#: meet, which left the core and inner_s as an isolated island - caught by the kit's reachability assert.
#: Concentric rings is also the truer shape: a geode forms in layers, not in spokes.
INNER_RING = [
    ([(66, 34), (76, 44), (79, 50)], 1),
    ([(79, 60), (70, 72), (62, 76)], 1),
    ([(48, 76), (36, 68), (31, 60)], 1),
    ([(31, 48), (38, 36), (46, 31)], 1),
]
#: THE THREE THROATS. Each is a pinch where the wall's crystal has nearly met the cavity's, and each is where
#: a fight happens whether the player wants one or not.
THROATS = [
    ([(50, 20), (54, 26), (55, 30)], 1),          # north bay -> inner_n
    ([(90, 60), (85, 56), (82, 55)], 1),          # east bay -> inner_e
    ([(22, 56), (26, 55), (30, 55)], 1),          # west bay -> inner_w
]
#: The last throat, and the tightest thing on the map.
CORE_THROAT = ([(55, 72), (55, 66), (55, 62)], 1)

BOSSES = {}
CHESTS = []


def _near_walkable(zone, x, y, rad=8):
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            if zone.is_walkable(int(x) + dx, int(y) + dy):
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, int(x) + dx, int(y) + dy)
    return None if best is None else (best[1], best[2])


def build_hollow_geode():
    zone = Tilemap("The Hollow Geode", W, H,
                   "A cavity in the Underdark's eastern wall that crystal has spent an age filling, and has "
                   "nearly finished.")
    zone.is_cave = True
    #: .region declares the PARENT ZONE (world/zone_manager.py:55) - the encounter lookup keys off it.
    zone.region = "The Crystalline Underdark"
    zone.fixed_spawns = False
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b

    b.lobes(list(BAYS.values()) + list(INNER.values()) + list(VUGS.values()) + [CORE])
    for pts, w in GALLERY + THROATS + INNER_RING + [CORE_THROAT]:
        b.corridor(pts, width=w)
    # the way in, through a crack in the shell
    b.corridor([(55, 106), (55, 98), (56, 94)], width=1)

    # Crystal masses standing IN the cavity, so even the bays are not open floor. These are pillars rather
    # than walls - you see past them, you just cannot walk through them.
    b.pillars([44, 68], [88, 94], size=2)
    b.pillars([50, 60], [18, 22], size=2)
    b.pillars([48, 62], [30, 34], size=2)
    b.pillars([48, 62], [74, 78], size=2)

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.set_tile(px, py, "dirt", "base")
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    # One boss per shell: the gallery, the inner cavity, and the core.
    bosses = [(94, 62, "Shardmaw"),
              (55, 30, "The Prism Warden"),
              (CX, CY, "Heartgrown")]
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
    for (x, y) in ((14, 76), (98, 90), (90, 12), (30, 54)):
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        chests.append(p)
    CHESTS[:] = chests
    for c in chests:
        L.mark("chest", *c)

    zone.add_subzone("The Hollow Geode", 0, 0, W, H)      # the encounter-table key covers the whole map
    zone.add_subzone("The Druse Gallery", 6, 6, 98, 98)
    zone.add_subzone("The Inner Cavity", 22, 22, 66, 66)
    zone.add_subzone("The Core", 42, 42, 26, 24)
    return zone, L


def finish(zone, L):
    targets = [PORTAL] + [(x, y) for (x, y) in BOSSES.values()] + list(CHESTS)
    return L.finish(targets)


def dress(zone, L):
    P = L.prop
    U = dict(where=UDP)
    # ---- the crack in the shell, and the south bay
    P("ud_crystal_spire", 51, 96, 7, **U)
    P("ud_crystal_violet", 60, 96, 5, **U)
    P("ud_geode_open", 64, 92, 5, **U)
    P("ud_crystal_cyan", 50, 90, 5, **U)
    # ---- round the gallery: every bay gets its own crystal, none of them the same
    P("ud_crystal_cyan", 26, 84, 6, **U)
    P("ud_crystal_float", 30, 76, 4, **U)
    P("ud_crystal_violet", 16, 54, 6, **U)
    P("ud_lichen_boulder", 18, 46, 4, **U)
    P("ud_crystal_spire", 46, 16, 8, **U)
    P("ud_crystal_violet", 60, 12, 5, **U)
    P("ud_crystal_cyan", 86, 30, 6, **U)
    P("ud_geode_open", 90, 24, 5, **U)
    P("ud_crystal_spire", 96, 66, 8, **U)
    P("ud_crystal_float", 92, 58, 4, **U)
    # ---- the throats: the crystal that nearly closed them
    P("ud_lattice_growth", 54, 24, 6, **U)
    P("ud_lattice_growth", 86, 56, 6, **U)
    P("ud_lattice_growth", 26, 54, 6, **U)
    # ---- the inner cavity
    P("ud_crystal_violet", 52, 32, 5, **U)
    P("ud_crystal_cyan", 78, 50, 5, **U)
    P("ud_crystal_violet", 58, 78, 5, **U)
    P("ud_crystal_cyan", 32, 50, 5, **U)
    P("ud_glow_pool", 55, 36, 3, **U)
    # ---- the core: the only room with any space, because it is the part the crystal has not finished
    P("ud_crystal_spire", 48, 50, 9, **U)
    P("ud_crystal_spire", 62, 50, 9, **U)
    P("ud_geode_open", 55, 60, 6, **U)
    P("ud_crystal_float", 50, 58, 4, **U)
    P("ud_crystal_float", 60, 58, 4, **U)
    # ---- the vugs: blind pockets, and somebody got in before you
    P("ud_codex_crates", 15, 74, 3, near_ok=True, **U)
    P("ud_frozen_crate", 97, 88, 3, near_ok=True, **U)
    P("ud_masonry_rubble", 89, 11, 3, near_ok=True, **U)
    return zone, L


def generate_hollow_geode():
    zone, L = build_hollow_geode()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_hollow_geode_baked():
    """(zone, layout) with props + QA done - what the baker paints from."""
    zone, L = build_hollow_geode()
    dress(zone, L)
    finish(zone, L)
    return zone, L
