"""
Hand-built layouts for Stranglethorn's three caves - one per zone (2026-10-29):

  Rotvine Hollow      110x90   flooded root cavern, Northern Stranglethorn   (portal 32,10 / boss 88,70)
  Veilfall Cave       120x95   terraces around a plunge pool, Central        (portal 32,10 / boss 66,63)
  The Drowned Shrine  115x100  flooded colonnade, Southern Stranglethorn     (portal 32,10 / boss 85,83)

Same recipe as tools/handbuilt_echo_caves.py: CaveLayout (guarded props, flood-fill QA), the organic
carving helpers (cavern / tube / disc), loops instead of dead ends, and painted-chunk registration,
baked by tools/bake_stranglethorn_caves.py.  Region voice and the standing flavour rules come from
tools/handbuilt_stranglethorn_north.py: troll stonework rotting in the vine, concrete detail, no new art.

Portal contracts (world/portal_manager.py - already wired on the overworld side, do not touch it):
    Northern Stranglethorn (150,40) -> Rotvine Hollow (32,10)
    Central Stranglethorn  (40,58)  -> Veilfall Cave (32,10)
    Southern Stranglethorn (170,116)-> The Drowned Shrine (32,10)
Every cave's mouth tile is (32,10) and the player stands on (32,8) on arrival; leaving a cave lands one
tile SOUTH of the overworld mouth.

LAYOUT VARIETY (Kyle: "a lot of these are hand crafted but they're starting to look similar").  Three
caves written in one sitting is exactly how three caves end up being the same cave, so none of these is
a spine with wings and no two of them share a topology:

  Rotvine Hollow      ONE ROOM, NO CORRIDORS.  A single drowned chamber the size of the whole map with
                      the root boles of the crag above punched back through it as rock pillars.  You
                      navigate between obstacles in open water instead of along a route, so there is no
                      such thing as a wrong turn down here - only a longer wade.  Shape chosen because
                      the fiction is a root mass, and a root mass is a field, not a tunnel.
  Veilfall Cave       A DESCENDING SPIRAL OF RING TERRACES.  Four concentric ring galleries around a
                      central plunge pool, each one lower than the last, joined by short ramps at
                      staggered angles, with three collapsed stairs cutting between rings as shortcuts.
                      You always walk around the water and you can always see where you are going next,
                      one terrace down across the pool.  Shape chosen because the cave IS the lip of a
                      waterfall: the only honest way to build it is as height.
  The Drowned Shrine  A RECTILINEAR GRID OF CAUSEWAYS.  Not carved rock at all - the lowest terrace of
                      Zul'Kundaraz, so the geometry is cut stone on a survey grid.  The ruin's halls are
                      under deep water and the route is the dry high ground between them: the tops of
                      the hall walls, four by four, every junction a loop.  Shape chosen because it is
                      the only one of the three that was built by somebody.

Prop rule (Kyle): less is more; a few centrepieces per room; every prop logical for its room.
Art: nothing new.  Dungeon props, the coastal troll kit, the Echo Isles ruin set, the Ashenvale canopy
and root pieces, and the Skull Rock bone pieces - all already on disk.
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import (CaveLayout, DP, _apply_pools,  # noqa: F401
                                       register_baked, pool_fields)
from tools.handbuilt_echo_caves import cavern, tube, disc, pol, _wob  # noqa: F401

SP = "assets/tiles/stranglethorn/props/"
CP = "assets/tiles/coastal_props/"
JP = "assets/tiles/echo_isles/props/"
AP = "assets/tiles/ashenvale/props/"
SR = "assets/tiles/skull_rock/props/"
BAKED = "assets/tiles/stranglethorn_caves/{}/baked"

REGION = "Eastern Kingdoms - Stranglethorn"


def _cave(name, w, h, desc, portal, arrival):
    zone = Tilemap(name, w, h, desc)
    zone.is_cave = True
    zone.region = REGION
    zone.fixed_spawns = False
    return zone, CaveLayout(zone, arrival)


def _finish(L, zone, portal, bosses, chests):
    L.mark("portal", *portal)
    for (x, y, _) in bosses:
        L.mark("boss_marker", x, y)
    for c in chests:
        L.mark("chest", *c)
    zone.boss_position = (bosses[0][0], bosses[0][1])
    zone.boss_positions = [(x, y, n) for (x, y, n) in bosses]


def _subzones(zone, rooms):
    for n, x, y, w, h in rooms:
        zone.add_subzone(n, x, y, w, h)
    zone.add_subzone(zone.name, 0, 0, zone.width, zone.height)
    zone.subzones.insert(0, zone.subzones.pop())      # whole-map name first, so rooms override it


def ring(b, cx, cy, r, w, a0=0, a1=360, step=10, ph=0.0, base=None):
    """A ring gallery: an arc of `tube` at radius r.  a1 > 360 wraps."""
    pts = [pol(cx, cy, r, a) for a in range(a0, a1 + 1, step)]
    tube(b, pts, w, ph=ph, base=base)


def radial(b, cx, cy, r0, r1, deg, w=3, base=None):
    """A ramp or a collapsed stair: straight in or out between two radii."""
    tube(b, [pol(cx, cy, r0, deg), pol(cx, cy, r1, deg)], w, base=base)


def guarded_pillar(L, cx, cy, r, ph=0.0):
    """Punch a rock bole back through already-carved floor, and take it out again if it would
    strand anything.  The pillar field in Rotvine Hollow is placed blind on a jittered lattice,
    so this is what keeps a field of thirty obstacles honest without hand-checking each one."""
    z = L.z
    R = int(r * 1.4) + 2
    touched = []
    for y in range(int(cy) - R, int(cy) + R + 1):
        for x in range(int(cx) - R, int(cx) + R + 1):
            if not (0 <= x < z.width and 0 <= y < z.height):
                continue
            dx, dy = x - cx, y - cy
            if math.hypot(dx / r, dy / r) > _wob(math.atan2(dy, dx), ph):
                continue
            if any(max(abs(qx - x), abs(qy - y)) <= 2 for (qx, qy) in L.critical):
                return False
            touched.append((x, y, z.base_layer[y][x], z.collision_layer[y][x]))
    for (x, y, _b, _c) in touched:
        z.set_tile(x, y, "rock", "collision")
    reached = len(L._reach())
    total = sum(z.is_walkable(x, y) for y in range(z.height) for x in range(z.width))
    if reached != total:
        for (x, y, b, c) in touched:
            z.collision_layer[y][x] = c
            if b:
                z.set_tile(x, y, b, "base")
        return False
    return True


def water_rect(zone, x0, y0, x1, y1, tile):
    """Flood a rect of already-open floor (the Drowned Shrine's halls are tile water, not pools:
    the baker reads them back with tile_water so the painting and the collision agree)."""
    for y in range(max(0, y0), min(zone.height, y1 + 1)):
        for x in range(max(0, x0), min(zone.width, x1 + 1)):
            if zone.collision_layer[y][x] == "rock":
                continue
            zone.set_tile(x, y, tile, "base")
            zone.collision_layer[y][x] = None


# ================================================================== ROTVINE HOLLOW
RH_PORTAL = (32, 10)
RH_ARRIVE = (32, 8)
RH_BOSS = (90, 64)                     # Rootmaw, on the lip of the sink where the outflow starts
RH_RARE = (18, 30)                     # Hap'ka the Drowned, in the shelf of troll dead (named rare)
RH_CHESTS = [(16, 66), (92, 26), (58, 30), (70, 56)]
# Standing water between the boles: medium ponds, deep in their middles, shallow at the edges.
RH_POOLS = [(26, 48, 7.5, 5.5, 0.4), (46, 58, 8.0, 5.0, 1.6), (64, 42, 7.0, 5.5, 2.4),
            (82, 56, 7.5, 5.0, 0.9), (40, 32, 6.5, 4.5, 1.2), (86, 74, 8.0, 5.5, 2.0),
            (62, 70, 6.5, 4.5, 0.2)]
# Jittered lattice of root boles.  Deterministic, and every one of them is checked by guarded_pillar.
RH_PILLARS = []
for _iy, _y in enumerate(range(26, 79, 9)):
    for _ix, _x in enumerate(range(14, 101, 10)):
        _jx = _x + round(3.0 * math.sin(_ix * 2.3 + _iy * 1.1))
        _jy = _y + round(2.5 * math.sin(_ix * 1.7 + _iy * 2.9))
        _r = 2.6 + 1.6 * (0.5 + 0.5 * math.sin(_ix * 0.9 + _iy * 1.3))
        RH_PILLARS.append((_jx, _jy, round(_r, 2), round((_ix + _iy) * 0.7, 2)))


def build_rotvine_hollow():
    zone, L = _cave("Rotvine Hollow", 110, 90,
                    "A flooded root cavern under the Zul'Marosh crag: standing water, hanging roots and "
                    "the start of the river that rots the fen downhill.",
                    RH_PORTAL, RH_ARRIVE)
    b = L.b
    # the mouth, and the only tunnel in the place
    cavern(b, 32, 9, 8, 4, 0, 0.3)
    tube(b, [(32, 12), (32, 18), (31, 23)], 5, 6, ph=0.6)
    # ONE ROOM.  Four overlapping caverns make the chamber read as rock-cut rather than as an ellipse.
    cavern(b, 54, 50, 44, 27, 0, 0.5)
    cavern(b, 24, 60, 17, 13, -15, 1.4)
    cavern(b, 84, 32, 16, 12, 20, 2.2)
    cavern(b, 88, 70, 15, 11, -10, 0.8)
    cavern(b, 18, 30, 11, 8, 10, 1.9)                              # the shelf of troll dead
    tube(b, [(28, 36), (22, 33)], 4)
    _apply_pools(zone, RH_POOLS)

    _subzones(zone, [("The Rotvine Mouth", 22, 3, 22, 14),
                     ("The Root Floor", 8, 20, 94, 60),
                     ("The Drowned Shelf", 6, 20, 26, 20),
                     ("The Outflow Sink", 72, 56, 36, 28)])

    _finish(L, zone, RH_PORTAL,
            [(RH_BOSS[0], RH_BOSS[1], "Rootmaw"),
             (RH_RARE[0], RH_RARE[1], "Hap'ka the Drowned")], RH_CHESTS)

    placed = sum(guarded_pillar(L, x, y, r, ph) for (x, y, r, ph) in RH_PILLARS)
    L.pillars = placed

    p = L.prop
    # mouth: you come in under the roots and they are the first thing you touch
    p("stv_liana_arch", 32, 13, 6, where=SP, solid="core", avoid=1)
    p("stv_mushroom_ring", 30, 15, 3, where=SP)
    p("den_glow_mushrooms", 34, 16, 3)
    # the drowned shelf: trolls the crag's stair dropped in here, and nobody came down for them
    p("stv_troll_totem", 15, 28, 5, where=SP, solid="core")
    p("bone_pile", 21, 32, 3, where=SR)
    p("stv_troll_ziggurat_block", 13, 34, 5, where=SP, solid="core")
    # the root floor: roots, fungus, mangrove at the water's edge.  Spread thin - it is one big room
    p("stv_moss_curtain", 43, 40, 6, where=SP)
    p("stv_moss_curtain", 71, 64, 6, where=SP)
    p("stv_mangrove", 36, 59, 6, where=SP, solid="core")
    p("stv_mangrove", 68, 36, 6, where=SP, solid="core")
    p("stv_mushroom_ring", 49, 34, 3, where=SP)
    p("den_glow_mushrooms", 53, 62, 3)
    p("den_glow_mushrooms", 30, 44, 3)
    p("stv_stone_pile", 60, 50, 5, where=SP, solid="core")
    p("stv_tide_pool", 46, 46, 3, where=SP)
    # the outflow sink: where the water leaves, and what waits at the drain
    p("stv_tide_pool", 96, 74, 4, where=SP)
    p("grotto_serpent_skeleton", 80, 77, 4)
    p("vot_beast_ribcage", 96, 64, 3)
    p("den_stalagmites", 100, 70, 4, solid="core")

    L.finish([RH_ARRIVE, RH_PORTAL, RH_BOSS, RH_RARE] + RH_CHESTS)
    return zone, L


# =================================================================== VEILFALL CAVE
VF_PORTAL = (32, 10)
VF_ARRIVE = (32, 8)
VF_C = (66, 52)                        # the plunge pool, and the centre of every terrace
VF_BOSS = (66, 63)                     # Veilspeaker Zul'Rath, lowest terrace, facing the water
VF_RARE = (85, 83)                     # Sheetfall, in the font chamber (named rare)
VF_CHESTS = [(30, 69), (73, 11), (48, 52), (97, 34)]
VF_RINGS = (36, 27, 18, 10)
VF_POOLS = [(66, 52, 7.2, 6.6, 0.5),                               # the plunge pool
            (30, 73, 5.0, 3.8, 1.3),                               # the mist shrine's basin
            (85, 87, 4.6, 3.4, 2.1),                               # the font
            (79, 15, 3.4, 2.6, 0.8)]                               # a dripstone catch basin


def build_veilfall_cave():
    zone, L = _cave("Veilfall Cave", 120, 95,
                    "Wet limestone behind the Veilfall: four terraces of carved troll shrine stepping "
                    "down around the plunge pool, and a wall of falling water across the mouth.",
                    VF_PORTAL, VF_ARRIVE)
    b = L.b
    cx, cy = VF_C
    r0, r1, r2, r3 = VF_RINGS
    # the mouth, behind the sheet of water, then straight down the west wall onto the rim
    cavern(b, 32, 9, 9, 5, 0, 0.7)
    tube(b, [(32, 13), (32, 24), (32, 33), (32, 40)], 5, ph=0.4)
    # the plunge pool's own basin, cut out first so the water has somewhere to sit and a shore to sit on
    disc(b, cx, cy, 8.5, ph=0.5)
    # four ring galleries, each lower than the one outside it
    for i, r in enumerate(VF_RINGS):
        ring(b, cx, cy, r, 5, ph=0.3 + 0.6 * i)
    # the ramps down, at staggered angles, so the descent circles the pool instead of dropping straight
    radial(b, cx, cy, r0, r1, 330, 4)
    radial(b, cx, cy, r1, r2, 120, 4)
    radial(b, cx, cy, r2, r3, 250, 4)
    # three collapsed stairs: shortcuts between neighbouring terraces, so every terrace is a loop
    radial(b, cx, cy, r0, r1, 70, 3)
    radial(b, cx, cy, r1, r2, 300, 3)
    radial(b, cx, cy, r2, r3, 30, 3)
    # shrine chambers cut OUTWARD off the rim, which is the only direction with rock to spare
    for (deg, rr, rx, ry, rot, ph) in ((150, 42, 9, 7, 10, 1.1), (280, 42, 9, 7, -20, 0.2),
                                       (60, 41, 9, 6, 15, 2.4)):
        ax, ay = pol(cx, cy, rr, deg)
        cavern(b, ax, ay, rx, ry, rot, ph)
        radial(b, cx, cy, r0, rr, deg, 3)
    _apply_pools(zone, VF_POOLS)

    _subzones(zone, [("The Veil", 22, 3, 22, 14),
                     ("The Rim Gallery", 24, 10, 84, 80),
                     ("The Second Terrace", 34, 20, 64, 64),
                     ("The Dripstone Gallery", 60, 3, 28, 20),
                     ("Shrine of the Mist", 18, 62, 26, 22),
                     ("The Font", 72, 76, 28, 19),
                     ("The Plunge", 50, 36, 32, 32)])

    _finish(L, zone, VF_PORTAL,
            [(VF_BOSS[0], VF_BOSS[1], "Veilspeaker Zul'Rath"),
             (VF_RARE[0], VF_RARE[1], "Sheetfall")], VF_CHESTS)

    p = L.prop
    g = lambda r, a: pol(cx, cy, r, a)
    # the mouth: the water comes down across the opening and the trolls lit the inside of it
    p("stv_tide_pool", 32, 14, 6, where=SP, avoid=1)
    p("stv_troll_cookfire", 27, 12, 3, where=SP)
    p("stv_troll_totem", 36, 13, 5, where=SP, solid="core")
    # the rim gallery: a long curved walk, so almost nothing on it - lamps and a banner at the head
    p("stv_arena_standard", *g(36, 185), 6, where=SP, solid="core")
    p("vot_totem_pole", *g(36, 15), 6, solid="core")
    p("den_stalactites", *g(36, 255), 4)
    # second terrace: where the carving starts being deliberate
    p("stv_troll_idol_head", *g(27, 95), 5, where=SP, solid="core")
    p("spirit_brazier", *g(27, 200), 4, solid="core")
    p("cracked_pillar", *g(27, 340), 5, where=SR, solid="core")
    # third terrace: the shrine proper
    p("temple_column", *g(18, 150), 5, solid="core")
    p("temple_column", *g(18, 215), 5, solid="core")
    p("vot_war_drum", *g(18, 75), 3, solid="core")
    # the lowest terrace, at the water
    p("ritual_circle", *g(10, 135), 4, avoid=1)
    p("skull_pile", *g(11, 45), 3)
    p("stv_troll_totem", *g(11, 185), 5, where=SP, solid="core")
    # dripstone gallery
    p("den_stalactites", 69, 9, 4)
    p("den_stalagmite_pair", 76, 11, 4, solid="core")
    p("stv_mushroom_ring", 66, 15, 3, where=SP)
    # shrine of the mist
    p("grotto_shell_altar", 25, 70, 3, solid="core")
    p("stv_troll_obelisk", 35, 76, 5, where=SP, solid="core")
    p("den_glow_mushrooms", 24, 77, 3)
    # the font
    p("grotto_blue_brazier", 80, 84, 4, solid="core")
    p("grotto_kelp_stalks", 90, 90, 4)
    p("stv_mushroom_ring", 90, 82, 3, where=SP)

    L.finish([VF_ARRIVE, VF_PORTAL, VF_BOSS, VF_RARE] + VF_CHESTS)
    return zone, L


# =============================================================== THE DROWNED SHRINE
DS_PORTAL = (32, 10)
DS_ARRIVE = (32, 8)
DS_BOSS = (85, 83)                     # Tide-Priestess Myzrai, on the sanctum terrace
DS_RARE = (56, 32)                     # Saltgorge, in the pillar court (named rare)
DS_CHESTS = [(20, 48), (98, 22), (62, 40), (94, 78)]
DS_XS = (20, 46, 72, 98)               # the causeway grid: the tops of the hall walls
DS_YS = (22, 48, 74, 92)
DS_IN = (18, 20, 100, 94)              # the terrace that is still above water at all
DS_DRY = [(46, 72, 22, 48), (72, 98, 74, 92)]      # the pillar court, and the sanctum
# collapsed hall walls standing out of the flooded halls - silhouette, not obstacles on the route
DS_STUBS = [(28, 30, 31, 42), (54, 56, 56, 68), (80, 86, 30, 33), (84, 90, 56, 62),
            (28, 34, 80, 83)]


def build_drowned_shrine():
    zone, L = _cave("The Drowned Shrine", 115, 100,
                    "The lowest terrace of Zul'Kundaraz, taken by the tide: cut stone halls under salt "
                    "water and a grid of wall-tops to walk on.",
                    DS_PORTAL, DS_ARRIVE)
    b = L.b
    x0, y0, x1, y1 = DS_IN
    # the sea cave mouth, and the gullet down onto the terrace
    cavern(b, 32, 9, 9, 5, 0, 0.9)
    b.rect(30, 12, 34, y0 + 4)
    # the whole terrace is open stone first; the halls are then flooded back out of it
    b.rect(x0, y0, x1, y1)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            on_road = (any(abs(x - c) <= 2 for c in DS_XS) or any(abs(y - c) <= 2 for c in DS_YS)
                       or any(ax <= x <= bx and ay <= y <= by for (ax, bx, ay, by) in DS_DRY))
            if on_road:
                continue
            # 2-tile shallow lip against the dry stone, deep water over the halls themselves
            near = (min(abs(x - c) for c in DS_XS) <= 4 or min(abs(y - c) for c in DS_YS) <= 4
                    or x < x0 + 3 or x > x1 - 3 or y < y0 + 3 or y > y1 - 3
                    or any(ax - 2 <= x <= bx + 2 and ay - 2 <= y <= by + 2
                           for (ax, bx, ay, by) in DS_DRY))
            zone.set_tile(x, y, "shallow_water" if near else "deep_water", "base")
            zone.collision_layer[y][x] = None
    # plazas where the wall-tops cross: the only places wide enough for the colonnade to still stand
    for jx in DS_XS:
        for jy in DS_YS:
            b.rect(jx - 3, jy - 3, jx + 3, jy + 3)
    for (ax, bx, ay, by) in DS_STUBS:
        for y in range(ay, by + 1):
            for x in range(ax, bx + 1):
                zone.set_tile(x, y, "rock", "collision")

    _subzones(zone, [("The Sea Mouth", 22, 3, 22, 14),
                     ("The Flooded Halls", 16, 18, 86, 78),
                     ("The Pillar Court", 44, 20, 30, 30),
                     ("The Sunken Sanctum", 70, 72, 32, 22)])

    _finish(L, zone, DS_PORTAL,
            [(DS_BOSS[0], DS_BOSS[1], "Tide-Priestess Myzrai"),
             (DS_RARE[0], DS_RARE[1], "Saltgorge")], DS_CHESTS)

    p = L.prop
    # the sea mouth
    p("stv_coral_outcrop", 27, 12, 4, where=SP)
    p("grotto_anchor", 36, 13, 4)
    # the wall-top grid: a surviving column at the junctions, and nothing else on the route
    for (jx, jy) in ((20, 22), (72, 22), (46, 74), (98, 92)):
        p("temple_column", jx, jy + 2, 5, solid="core")
    p("broken_column", 46, 50, 5, solid="core")
    p("broken_column", 98, 50, 5, solid="core")
    p("grotto_barnacle_pillar", 20, 76, 4, solid="core")
    p("grotto_kelp_stalks", 72, 50, 4)
    p("stv_coral_outcrop", 46, 24, 4, where=SP)
    # the pillar court: the one hall on this terrace whose floor is still above the water
    p("stv_troll_idol_head", 52, 28, 5, where=SP, solid="core")
    p("stv_troll_totem", 66, 30, 5, where=SP, solid="core")
    p("stv_troll_ziggurat_block", 50, 44, 5, where=SP, solid="core")
    p("grotto_giant_clam", 68, 44, 3)
    p("cracked_pillar", 60, 26, 5, where=SR, solid="core")
    # the sanctum: naga moved in, and they did not change much
    p("grotto_naga_throne", 85, 78, 6, solid="core", avoid=2)
    p("naga_statue", 78, 86, 5, solid="core")
    p("naga_statue", 92, 86, 5, solid="core")
    p("grotto_shell_altar", 76, 79, 3, solid="core")
    p("grotto_naga_rune_stone", 90, 80, 4, solid="core")
    p("grotto_serpent_skeleton", 80, 91, 4)

    L.finish([DS_ARRIVE, DS_PORTAL, DS_BOSS, DS_RARE] + DS_CHESTS)
    return zone, L


# ========================================================= generate_* wrappers
def _gen(build, slug):
    zone, _ = build()
    register_baked(zone, BAKED.format(slug))
    return zone


def generate_rotvine_hollow():
    return _gen(build_rotvine_hollow, "rotvine_hollow")


def generate_veilfall_cave():
    return _gen(build_veilfall_cave, "veilfall_cave")


def generate_drowned_shrine():
    return _gen(build_drowned_shrine, "drowned_shrine")
