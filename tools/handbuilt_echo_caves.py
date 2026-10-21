"""
Hand-built layouts for Echo Isles' two caves (2026-10-21):

  Sunken Temple Grotto   120x100 drowned naga ROTUNDA  (portal 60,92 / boss Gharesh 60,48)
  Zalazane's Hollow      130x84  winding troll warren   (portal 14,74 / boss Zalazane 22,12)

Same recipe as tools/handbuilt_durotar_caves.py (CaveLayout: guarded props, flood-fill
QA, loops instead of dead ends) and the same painted-chunk registration, baked by
tools/bake_echo_caves.py.  Both are drawn as a spine to the boss with side wings that
loop back, so a player can detour for extra fights but never has to backtrack a dead end.

Portal contracts (world/portal_manager.py): Echo (24,98) <-> Grotto (60,92);
Echo (141,117) <-> Hollow (14,74).

LAYOUT VARIETY (Kyle: "a lot of these are hand crafted but they're starting to look
similar"): the earlier caves were all a central spine with symmetric wings.  These two
are deliberately different shapes - a CIRCULAR temple (ring hall, gated inner wall,
moat and an island sanctum, chambers hanging off at odd angles) and a long organic
C-shaped warren that spirals back toward its own entrance.  Organic carving helpers
(tube / cavern / disc) live here so future caves can pick a shape instead of a rect.

Prop rule (Kyle): less is more; props logical for the room; a few centrepieces.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import (CaveLayout, DP, _apply_pools,  # noqa: F401
                                       register_baked, pool_fields)

SR = "assets/tiles/skull_rock/props/"
BAKED = "assets/tiles/echo_caves/{}/baked"


def _cave(name, w, h, desc, portal):
    zone = Tilemap(name, w, h, desc)
    zone.is_cave = True
    zone.region = "Echo Isles"
    zone.fixed_spawns = False
    return zone, CaveLayout(zone, portal)


def _finish(L, zone, portal, bosses, chests):
    L.mark("portal", *portal)
    for (x, y, _) in bosses:
        L.mark("boss_marker", x, y)
    for c in chests:
        L.mark("chest", *c)
    zone.boss_position = (bosses[0][0], bosses[0][1])
    zone.boss_positions = [(x, y, n) for (x, y, n) in bosses]



# ------------------------------------------------------------------ organic carving
import math


def _wob(a, ph, k=(0.10, 0.07, 0.04)):
    return 1 + k[0] * math.sin(2 * a + ph) + k[1] * math.sin(3 * a + ph * 1.7) + k[2] * math.sin(5 * a + ph * 0.3)


def cavern(b, cx, cy, rx, ry, rot=0.0, ph=0.0, base=None):
    """Irregular rotated cavern (integer-harmonic edge, so it never seams)."""
    c, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    R = int(max(rx, ry) * 1.3) + 2
    for y in range(int(cy) - R, int(cy) + R + 1):
        for x in range(int(cx) - R, int(cx) + R + 1):
            dx, dy = x - cx, y - cy
            u, v = (c * dx + s_ * dy) / rx, (-s_ * dx + c * dy) / ry
            if math.hypot(u, v) <= _wob(math.atan2(v, u), ph):
                b._open(x, y, base)


def _catmull(pts, n=10):
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t
                                    + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
    out.append(tuple(pts[-1]))
    return out


def tube(b, pts, w0=4, w1=None, ph=0.0, base=None):
    """Smooth spline tunnel whose width eases from w0 to w1 and breathes a little."""
    w1 = w0 if w1 is None else w1
    line = _catmull(pts) if len(pts) > 2 else [(pts[0][0] + (pts[1][0] - pts[0][0]) * i / 30,
                                                pts[0][1] + (pts[1][1] - pts[0][1]) * i / 30) for i in range(31)]
    n = len(line)
    for i, (x, y) in enumerate(line):
        w = (w0 + (w1 - w0) * i / max(n - 1, 1)) * (1 + 0.12 * math.sin(i * 0.37 + ph))
        r = max(w / 2, 1.2)
        for yy in range(int(y - r) - 1, int(y + r) + 2):
            for xx in range(int(x - r) - 1, int(x + r) + 2):
                if (xx - x) ** 2 + (yy - y) ** 2 <= r * r:
                    b._open(xx, yy, base)


def disc(b, cx, cy, r, ph=0.0, base=None):
    cavern(b, cx, cy, r, r, 0.0, ph, base)


def pol(cx, cy, r, deg):
    a = math.radians(deg)
    return (round(cx + r * math.cos(a)), round(cy + r * math.sin(a)))


def wall_annulus(zone, cx, cy, r0, r1, gates, gate_half_deg=11):
    """Rock ring r0..r1 with gaps ('gates') at the given angles (degrees, y down)."""
    for y in range(zone.height):
        for x in range(zone.width):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            r = math.hypot(dx, dy)
            if r0 <= r <= r1:
                a = math.degrees(math.atan2(dy, dx)) % 360
                if any(min(abs(a - g) % 360, 360 - abs(a - g) % 360) <= gate_half_deg for g in gates):
                    continue
                zone.set_tile(x, y, "rock", "collision")


# ============================================================ SUNKEN TEMPLE GROTTO
STG_PORTAL = (60, 92)
STG_C = (60, 48)                     # rotunda centre
STG_BOSS = (60, 48)
STG_ROAR = (12, 58)                  # Drowned Troll's crypt (named rare)
STG_CHESTS = [(7, 61), (18, 10), (105, 12), (112, 64)]
STG_GATES = (90, 300, 180)           # south, north-east, west gates in the inner wall
_moat = [(STG_C[0] + 14.5 * math.cos(math.radians(a)), STG_C[1] + 14.5 * math.sin(math.radians(a)), 5.4, 5.4, a * 0.05)
         for a in (0, 30, 60, 120, 150, 210, 240, 270, 330)]
STG_POOLS = [(round(x, 2), round(y, 2), rx, ry, ph) for (x, y, rx, ry, ph) in _moat] + [
    (108, 60, 4.2, 3.0, 1.7)]


def build_temple_grotto():
    zone, L = _cave("Sunken Temple Grotto", 120, 100,
                    "A naga temple sunk beneath the Echo Isles: a round hall around a moat, half drowned by the tide.",
                    STG_PORTAL)
    b = L.b
    cx, cy = STG_C
    disc(b, cx, cy, 36, ph=0.6)                                        # the Rotunda
    cavern(b, 60, 92, 10, 4, 0, 0.4)                                   # Tidewash Landing
    tube(b, [(60, 89), (60, 80)], 5)
    # chambers hanging off the rotunda at odd angles
    cavern(b, 12, 58, 9, 7, 10, 1.1)                                   # The Drowned Crypt
    tube(b, [(30, 51), (20, 55), (15, 57)], 3)
    tube(b, [(32, 63), (21, 62), (16, 61)], 3)
    cavern(b, 22, 13, 11, 7, -25, 2.0)                                 # The Murloc Warrens
    tube(b, [(38, 26), (30, 18), (26, 15)], 3)
    tube(b, [(44, 22), (35, 12), (31, 10)], 3)
    cavern(b, 100, 14, 9, 7, 20, 0.2)                                  # The Pearl Reliquary
    tube(b, [(80, 26), (91, 18), (96, 15)], 3)
    tube(b, [(72, 18), (82, 9), (92, 10)], 3)
    cavern(b, 108, 60, 9, 8, 0, 1.5)                                   # The Elemental Springs
    tube(b, [(90, 54), (101, 57), (104, 59)], 3)
    tube(b, [(86, 64), (99, 66), (103, 64)], 3)
    # inner wall with three gates, then the moat
    wall_annulus(zone, cx, cy, 22, 25, STG_GATES)
    _apply_pools(zone, STG_POOLS, shallow_only=True)

    sg = [("Tidewash Landing", 48, 86, 24, 12), ("The Rotunda", 24, 12, 72, 73),
          ("The Tidelord's Sanctum", 42, 30, 36, 36),
          ("The Drowned Crypt", 2, 49, 22, 18), ("The Murloc Warrens", 6, 3, 34, 20),
          ("The Pearl Reliquary", 86, 4, 30, 20), ("The Elemental Springs", 96, 50, 22, 20)]
    for n, x, y, w, h in sg:
        zone.add_subzone(n, x, y, w, h)
    zone.add_subzone("Sunken Temple Grotto", 0, 0, zone.width, zone.height)
    zone.subzones.insert(0, zone.subzones.pop())      # whole-map name first, so rooms override it

    _finish(L, zone, STG_PORTAL,
            [(STG_BOSS[0], STG_BOSS[1], "Tidelord Gharesh"),
             (STG_ROAR[0], STG_ROAR[1], "Drowned Troll")], STG_CHESTS)

    p = L.prop
    g = lambda r, a: pol(cx, cy, r, a)
    # landing
    p("grotto_anchor", 53, 92, 4)
    p("grotto_glow_coral", 67, 92, 3)
    p("temple_archway", 60, 82, 6, avoid=1)
    # rotunda outer hall: statues and braziers at uneven intervals, columns at the three gates
    for a, name in ((35, "grotto_naga_priestess_statue"), (215, "grotto_naga_warrior_statue"),
                    (255, "naga_statue"), (330, "grotto_naga_priestess_statue")):
        p(name, *g(30, a), 5, solid="core")
    for a in (10, 70, 160, 200, 285):
        p("grotto_blue_brazier", *g(29, a), 4, solid="core")
    for a in STG_GATES:
        for da in (-13, 13):
            p("temple_column", *g(26.8, a + da), 5, solid="core")
    p("grotto_tide_pool", *g(32, 120), 3)
    p("grotto_glow_coral", *g(33, 150), 3)
    p("glow_coral_cluster", *g(32, 60), 3)
    # sanctum island
    p("grotto_naga_throne", cx, cy - 5, 6, solid="core", avoid=2)
    p("grotto_shell_altar", cx - 7, cy + 2, 3, solid="core")
    p("grotto_shell_altar", cx + 7, cy + 2, 3, solid="core")
    p("naga_statue", cx - 5, cy + 6, 5, solid="core")
    p("naga_statue", cx + 5, cy + 6, 5, solid="core")
    p("grotto_naga_rune_stone", cx, cy + 8, 4, solid="core", avoid=1)
    # crypt: troll dead
    p("sarcophagus", 9, 55, 4, solid="core")
    p("skull_pile", 17, 62, 3)
    p("grotto_shackle_frame", 14, 53, 4, solid="core")
    p("grotto_pirate_skeletons", 10, 64, 3)
    p("grotto_kelp_stalks", 18, 58, 4)
    # murloc warrens
    p("grotto_fishing_net", 14, 12, 3)
    p("grotto_barrel_stack", 27, 17, 3)
    p("grotto_crab_molt", 14, 16, 3)
    p("grotto_kelp_stalks", 22, 8, 4)
    p("den_campfire_ashes", 22, 14, 2)
    # reliquary
    p("grotto_shell_altar", 100, 12, 3, solid="core", avoid=1)
    p("grotto_glow_coral", 96, 16, 3)
    p("grotto_giant_clam", 106, 16, 3)
    p("priestess_statue", 94, 9, 5, solid="core")
    # springs
    p("grotto_giant_clam", 104, 63, 3)
    p("grotto_glow_coral", 112, 57, 3)
    p("glow_coral_cluster", 106, 66, 3)
    p("grotto_barnacle_pillar", 113, 58, 4, solid="core")

    L.finish([STG_PORTAL, STG_BOSS, STG_ROAR] + STG_CHESTS)
    return zone, L


# ============================================================== ZALAZANE'S HOLLOW
ZH_PORTAL = (14, 74)
ZH_BOSS = (22, 12)
ZH_HOUNDMASTER = (76, 48)            # named rare, the kennel master
ZH_WITCH = (22, 36)                  # named rare, the Den's witch-doctor
ZH_CHESTS = [(38, 9), (112, 28), (107, 76), (16, 35)]
ZH_POOLS = []


def build_hollow():
    zone, L = _cave("Zalazane's Hollow", 130, 84,
                    "Zalazane's voodoo warren beneath the Echo Isles: one long hexed tunnel that coils back on itself.",
                    ZH_PORTAL)
    b = L.b
    # the long way round: entrance (SW) -> east along the bottom -> up the east side -> west along the top -> boss (NW)
    cavern(b, 16, 72, 10, 6, -10, 0.3)                                 # Hexed Threshold
    tube(b, [(24, 70), (33, 66), (39, 61)], 5, 4, ph=0.5)
    cavern(b, 44, 54, 12, 9, -25, 1.2)                                 # The Thrall Pens
    tube(b, [(52, 49), (60, 46), (67, 48)], 4, ph=1.1)
    cavern(b, 76, 48, 11, 8, 15, 2.1)                                  # The Hound Kennels
    tube(b, [(84, 52), (91, 58), (95, 65)], 4, 5, ph=2.0)
    cavern(b, 100, 70, 12, 9, -10, 0.8)                                # The Bone Pit
    tube(b, [(105, 62), (112, 52), (112, 41)], 4, ph=0.3)
    cavern(b, 110, 32, 10, 8, 20, 1.9)                                 # The Hexed Larder
    tube(b, [(105, 27), (95, 22), (88, 21)], 4, ph=0.9)
    cavern(b, 74, 20, 15, 10, 5, 2.4)                                  # The Ritual Hall
    tube(b, [(60, 18), (50, 14), (42, 12)], 5, 6, ph=1.5)
    cavern(b, 28, 14, 16, 9, -5, 0.6)                                  # Zalazane's Sanctum
    # side wings and shortcuts that make loops
    cavern(b, 50, 75, 8, 5, 8, 1.7)                                    # The Fetish Workshop
    tube(b, [(36, 66), (43, 71), (46, 73)], 3)
    tube(b, [(54, 70), (52, 63), (49, 61)], 3)                         # workshop -> pens (loop)
    cavern(b, 22, 36, 9, 7, -30, 2.7)                                  # The Witch-Doctor's Den
    tube(b, [(36, 49), (29, 43), (25, 40)], 3)                         # pens -> den
    tube(b, [(20, 29), (21, 25), (23, 22)], 3)                         # den -> sanctum (loop with the long way)
    tube(b, [(74, 40), (72, 33), (74, 29)], 3)                         # kennels -> ritual hall (loop)
    tube(b, [(90, 68), (84, 61), (80, 55)], 3)                         # bone pit -> kennels (loop)

    for n, x, y, w, h in [("The Hexed Threshold", 4, 65, 26, 16), ("The Fetish Workshop", 40, 69, 22, 12),
                          ("The Thrall Pens", 30, 44, 30, 20), ("The Witch-Doctor's Den", 10, 28, 24, 18),
                          ("The Hound Kennels", 64, 38, 26, 20), ("The Bone Pit", 86, 60, 28, 20),
                          ("The Hexed Larder", 98, 22, 26, 20), ("The Ritual Hall", 58, 8, 32, 24),
                          ("Zalazane's Sanctum", 10, 3, 38, 22)]:
        zone.add_subzone(n, x, y, w, h)
    zone.add_subzone("Zalazane's Hollow", 0, 0, zone.width, zone.height)
    zone.subzones.insert(0, zone.subzones.pop())

    _finish(L, zone, ZH_PORTAL,
            [(ZH_BOSS[0], ZH_BOSS[1], "Zalazane"),
             (ZH_HOUNDMASTER[0], ZH_HOUNDMASTER[1], "Houndmaster Gor'tek"),
             (ZH_WITCH[0], ZH_WITCH[1], "Mam'toth the Hexweaver")], ZH_CHESTS)

    p = L.prop
    # threshold
    p("den_torch", 10, 75, 4)
    p("vot_totem_pole", 21, 75, 6, solid="core", avoid=1)
    p("den_dead_recruit", 22, 69, 3)
    # fetish workshop
    p("bbc_warlock_desk", 50, 73, 4, solid="core")
    p("bbc_bookshelf", 45, 77, 4, solid="core")
    p("den_chest_sack", 55, 77, 3)
    p("candelabra", 55, 72, 3)
    # thrall pens: cages of villagers and shackles
    p("rf_prison_cage", 40, 56, 4, solid="core")
    p("rf_prison_cage", 49, 57, 4, solid="core")
    p("rf_shackle_frame", 44, 49, 4, solid="core")
    p("vot_hide_rack", 38, 61, 4, solid="core")
    p("den_leg_bones", 47, 61, 2)
    # witch-doctor's den
    p("bbc_cage", 17, 38, 4, solid="core")
    p("bone_pile", 27, 38, 3, where=SR)
    p("den_glow_mushrooms", 25, 40, 3)
    p("spirit_brazier", 19, 32, 4, solid="core")
    # hound kennels
    p("kennel_cage_worg", 70, 45, 4, solid="core")
    p("kennel_cage_worg", 83, 46, 4, solid="core")
    p("kennel_cage_empty", 72, 53, 4, solid="core")
    p("vot_beast_ribcage", 82, 53, 3)
    p("bone_pile", 78, 44, 3, where=SR)
    # bone pit
    p("skull_pile", 96, 66, 3)
    p("vot_beast_ribcage", 104, 72, 3)
    p("den_leg_bones", 93, 72, 2)
    p("bbc_skull_pile", 106, 66, 3)
    p("bone_pile", 100, 75, 3, where=SR)
    # hexed larder
    p("den_buried_crate", 105, 34, 3)
    p("den_chest_sack", 116, 33, 3)
    p("vot_hide_rack", 108, 28, 4)
    p("cocoon_victim", 111, 36, 4)
    # ritual hall
    p("ritual_circle", 72, 20, 5, avoid=1)
    p("spirit_brazier", 62, 17, 4, solid="core")
    p("spirit_brazier", 84, 18, 4, solid="core")
    p("bbc_idol", 66, 26, 5, solid="core")
    p("bbc_idol", 80, 25, 5, solid="core")
    p("vot_war_drum", 72, 12, 3, solid="core")
    # sanctum
    p("rf_sacrificial_altar", 28, 12, 4, solid="core", avoid=1)
    p("vot_totem_pole", 17, 10, 6, solid="core")
    p("vot_totem_pole", 38, 16, 6, solid="core")
    p("bbc_skull_pile", 32, 7, 3)
    p("bbc_skull_pile", 14, 16, 3)
    p("spirit_brazier", 14, 9, 4, solid="core")
    p("spirit_brazier", 42, 10, 4, solid="core")

    L.finish([ZH_PORTAL, ZH_BOSS, ZH_HOUNDMASTER, ZH_WITCH] + ZH_CHESTS)
    return zone, L


# ======================================================== generate_* wrappers
def _gen(build, slug):
    zone, _ = build()
    register_baked(zone, BAKED.format(slug))
    return zone


def generate_sunken_temple_grotto():
    return _gen(build_temple_grotto, "temple_grotto")


def generate_zalazane_hollow():
    return _gen(build_hollow, "hollow")
