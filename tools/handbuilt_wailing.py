"""
Hand-built Wailing Caverns (240x220): Naralex's dream-warren under Lushwater, drowned in green.

ARCHETYPE: THE RIVER LOOP (flooded ring gallery).  The old layout was a river and rectangular rooms; here the water is the
spine.  A great SERPENTBLOOM CAVERN with a wadeable river across it opens onto a RING that circles the whole map:
west to Cobrahn's Den, up through Kresh's flooded pool, across Skum's gallery, round to the Chamber of the Fang
(Lord Serpentis + Verdan), down the east side to Pythas's Hollow and back into the main cavern.  Either way round works
(the loop is the point, like the river guides keep describing); the ring's deepest point is the Fang chamber, and from
it a spur runs into the dead-end NARALEX'S DREAM, the sealed heart of the ring where Mutanus the Devourer waits.

  Lushwater Maw -> Serpentbloom Cavern (Lady Anacondra) -+- W arm -> Cobrahn's Den -> Kresh's Pool -> Skum's Gallery -+
                                                          |                                                          v
                                                          +- E arm <- Pythas's Hollow <------------------ Chamber of the Fang (Serpentis+Verdan)
                                                                                                             '-> Naralex's Dream (Mutanus)
  rares: Old Hissfang (SW nook), Drowsyroot the Dreamer (W nook), Sporeback the Bloated (SE nook)

Boss ladder (Kyle's table): Anacondra 19, Cobrahn 20, Kresh 20, Pythas 21, Skum 21, Serpentis 21, Verdan 22, Mutanus 24;
trash 16-22.  TRASH IS HAND-PLACED (multi-boss rule, claude/dungeon_authoring_rules.md): `TRASH` -> zone.trash_spawns.

HARD CONTRACTS (world/portal_manager.py): portal (120,210) <-> Central Barrens (75,223); arrival = 2 north.
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked, _apply_pools  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

BP = "assets/tiles/barrens/props/"
BAKED = "assets/tiles/wailing_caverns/baked"
W, H = 240, 220
PORTAL = (120, 210)

PATHS = {
    "entry":    ([(120, 202), (120, 190), (121, 181)], 5.0, 5.0),
    "sw_nook":  ([(96, 170), (82, 177), (68, 184)], 3.0, 3.0),
    "w_arm_a":  ([(88, 152), (68, 151), (50, 145)], 4.6, 4.6),
    "w_arm_b":  ([(36, 128), (30, 110), (36, 93), (46, 80)], 4.6, 4.6),
    "nook_w":   ([(31, 108), (22, 103), (15, 100)], 3.0, 3.0),
    "nw_arm":   ([(66, 66), (88, 51), (110, 44)], 4.6, 4.6),
    "n_arm":    ([(138, 40), (158, 47), (172, 54)], 4.6, 4.6),
    "dream":    ([(172, 66), (152, 77), (136, 90)], 4.2, 4.2),
    "e_arm_a":  ([(206, 74), (211, 92), (206, 110)], 4.6, 4.6),
    "e_arm_b":  ([(186, 133), (172, 141), (156, 149)], 4.6, 4.6),
    "nook_se":  ([(170, 145), (180, 157), (188, 165)], 3.0, 3.0),
}
ROOMS = {
    "gate":    (120, 203, 12, 6, 0, 0.4, "Lushwater Maw"),
    "main":    (120, 160, 36, 24, 0, 0.7, "Serpentbloom Cavern"),
    "den":     (40, 136, 16, 12, 0, 1.9, "Cobrahn's Den"),
    "kresh":   (52, 72, 19, 13, 0, 2.6, "Kresh's Pool"),
    "skum":    (126, 40, 15, 10, 0, 3.2, "Skum's Gallery"),
    "fang":    (192, 60, 24, 15, 0, 0.9, "Chamber of the Fang"),
    "dream":   (120, 98, 20, 14, 0, 1.5, "Naralex's Dream"),
    "pythas":  (196, 122, 17, 13, 0, 2.2, "Pythas's Hollow"),
    "nook_sw": (60, 187, 8, 6, 0, 0.8, "The Hissing Hollow"),
    "nook_w":  (12, 99, 8, 6, 0, 1.4, "The Dreamers' Nook"),
    "nook_se": (193, 169, 8, 6, 0, 2.4, "The Spore Pit"),
}
# analytic shallow pools (walkable, painted as river): (cx, cy, rx, ry, phase)
WC_POOLS = [
    # the river across the Serpentbloom Cavern (overlapping, so it reads as one flowing band)
    (84, 157, 8.0, 4.0, 0.3), (92, 159, 8.0, 4.0, 1.1), (100, 161, 8.0, 4.2, 2.0), (108, 162, 8.0, 4.2, 0.7),
    (116, 162, 8.0, 4.2, 1.6), (124, 162, 8.0, 4.2, 2.3), (132, 162, 8.0, 4.2, 0.9), (140, 161, 8.0, 4.0, 1.4),
    (148, 159, 8.0, 3.8, 2.6), (156, 157, 7.0, 3.6, 0.5),
    # the river runs into both arms
    (74, 152, 5.5, 2.8, 0.4), (61, 150, 5.0, 2.7, 1.3), (171, 141, 5.5, 2.8, 2.5), (181, 135, 5.0, 2.7, 0.2),
    # standing pools
    (52, 72, 11, 7, 0.7),          # Kresh's pool
    (120, 100, 9, 6, 1.2),         # the Dream pool
    (30, 141, 4.8, 3.4, 2.1),      # Cobrahn's spring
    (196, 129, 4.5, 3.2, 0.5),     # Pythas's basin
    (192, 67, 6.0, 3.5, 2.2),      # the Fang basin
]

BOSSES = {}
CHESTS = []
TRASH = []


def _near_walkable(zone, x, y, rad=4):
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            if zone.is_walkable(int(x) + dx, int(y) + dy):
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, int(x) + dx, int(y) + dy)
    return None if best is None else (best[1], best[2])


def walk(key, t):
    pts = PATHS[key][0]
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    d = t * sum(seg)
    for i, s in enumerate(seg):
        if d <= s or i == len(seg) - 1:
            u = min(1.0, d / s) if s else 0.0
            return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * u, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * u)
        d -= s


def build_wailing():
    zone = Tilemap("Wailing Caverns", W, H,
                   "A sprawling cave system, waterlogged and overgrown, home to the Fang Lords and the corrupted druid "
                   "Naralex's nightmare.")
    zone.is_cave = True
    zone.region = "Central Barrens"
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b

    for i, (key, (pts, w0, w1)) in enumerate(PATHS.items()):
        tube(b, pts, w0, w1, ph=0.4 + i * 0.8)
    for key, (cx, cy, rx, ry, rot, ph, _n) in ROOMS.items():
        cavern(b, cx, cy, rx, ry, rot, ph)
    # join the ends of arms into their rooms
    for pts in (((48, 145), (44, 140)), ((36, 128), (38, 134)), ((46, 80), (50, 74)), ((64, 67), (70, 64)),
                ((108, 44), (116, 42)), ((136, 40), (130, 40)), ((172, 54), (178, 56)), ((172, 66), (178, 64)),
                ((136, 90), (130, 94)), ((206, 72), (203, 68)), ((206, 110), (203, 114)), ((188, 132), (192, 130)),
                ((156, 149), (150, 152)), ((88, 152), (96, 153)), ((120, 181), (120, 176)), ((120, 203), (120, 198)),
                ((68, 184), (64, 185)), ((96, 170), (102, 166)), ((15, 100), (14, 100)), ((188, 165), (190, 167))):
        tube(b, list(pts), 4.0, 4.0)

    _apply_pools(zone, WC_POOLS, shallow_only=True)

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    bosses = [
        (120, 141, "Lady Anacondra"), (36, 132, "Lord Cobrahn"), (52, 72, "Kresh"), (200, 117, "Lord Pythas"),
        (126, 38, "Skum"), (181, 57, "Lord Serpentis"), (203, 57, "Verdan the Everliving"),
        (120, 94, "Mutanus the Devourer"),
        (60, 187, "Old Hissfang"), (12, 99, "Drowsyroot the Dreamer"), (193, 169, "Sporeback the Bloated"),
    ]
    fixed = []
    for (x, y, n) in bosses:
        p = _near_walkable(zone, x, y)
        assert p, (n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (fixed[7][0], fixed[7][1])          # Mutanus is the final boss
    zone.boss_positions = list(fixed)

    chests = []
    for (x, y) in ((30, 143), (66, 78), (136, 43), (208, 66), (206, 128), (131, 104), (66, 191)):
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        chests.append(p)
    CHESTS[:] = chests
    for c in chests:
        L.mark("chest", *c)

    def sub(name, x, y, rx, ry):
        zone.add_subzone(name, int(x - rx), int(y - ry), int(2 * rx), int(2 * ry))
    for key, (cx, cy, rx, ry, rot, ph, name) in ROOMS.items():
        sub(name, cx, cy, rx + 2, ry + 2)
    return zone, L


def finish(zone, L):
    targets = [PORTAL] + [(x, y) for (x, y) in BOSSES.values()] + list(CHESTS)
    return L.finish(targets)


def dress_and_trash(zone, L):
    P = L.prop
    R = ROOMS
    gx, gy = R["main"][:2]
    ax, ay = BOSSES["Lady Anacondra"]
    # ---- the Maw: a serpent shrine at the mouth, then the cave begins
    P("br_wc_serpent_shrine", 120, 199, 8, where=BP, solid=False, near_ok=True, avoid=0)
    P("den_glow_mushrooms", 111, 204, 3)
    P("den_leg_bones", 130, 203, 2)
    # ---- Serpentbloom Cavern: blooms on the south bank, ruined shrine stones on the north
    P("den_glow_mushrooms", 98, 172, 3)
    P("den_glow_mushrooms", 143, 170, 3)
    P("den_stalagmites", 90, 165, 4)
    P("den_stalagmites", 150, 168, 4)
    P("vot_reeds", 106, 156, 3)
    P("vot_reeds", 134, 157, 3)
    P("grotto_naga_rune_stone", ax - 9, ay + 3, 4)
    P("grotto_naga_rune_stone", ax + 9, ay + 3, 4)
    P("den_egg_cluster", ax - 4, ay - 4, 2)
    P("grotto_serpent_skeleton", 105, 143, 3)
    P("vot_fallen_log", 138, 147, 3)
    # ---- west arm / Cobrahn's Den
    cx, cy = BOSSES["Lord Cobrahn"]
    P("den_nest_mound", cx + 6, cy + 4, 4)
    P("den_egg_cluster", cx - 6, cy + 5, 2)
    P("den_stalagmites", cx + 11, cy - 6, 4)
    P("vot_dead_tree", cx - 11, cy - 5, 6)
    P("skull_pile", cx + 9, cy + 9, 2)
    # ---- Kresh's pool: reeds + fallen log at the shoreline
    kx, ky = R["kresh"][:2]
    P("vot_reeds", kx - 15, ky + 5, 3)
    P("vot_reeds", kx + 14, ky + 6, 3)
    P("vot_fallen_log", kx + 12, ky - 8, 3)
    P("den_stalactites", kx - 5, ky - 11, 4)
    P("grotto_tide_pool", kx + 8, ky + 9, 2, solid=False)
    # ---- Skum's gallery
    sx, sy = R["skum"][:2]
    P("den_stalagmite_pair", sx - 11, sy + 4, 4)
    P("den_stalagmites", sx + 11, sy + 5, 4)
    P("den_rock_rubble", sx + 3, sy - 6, 2)
    P("den_leg_bones", sx - 4, sy + 6, 2)
    # ---- the Chamber of the Fang: the serpent wall's shrine, banners, braziers
    fx, fy = R["fang"][:2]
    P("br_wc_serpent_shrine", fx, fy - 12, 9, where=BP, solid="core", near_ok=True, avoid=1)
    P("spirit_brazier", fx - 17, fy + 2, 4, solid="core")
    P("spirit_brazier", fx + 17, fy + 2, 4, solid="core")
    P("rf_cult_banner", fx - 8, fy - 9, 5)
    P("rf_cult_banner", fx + 8, fy - 9, 5)
    P("ritual_circle", fx, fy - 1, 6, solid=False, near_ok=True, avoid=0)
    P("skull_pile", fx + 15, fy + 8, 2)
    P("grotto_naga_rune_stone", fx - 15, fy + 8, 4)
    # ---- Pythas's Hollow
    px_, py_ = R["pythas"][:2]
    P("den_glow_mushrooms", px_ - 9, py_ + 6, 3)
    P("den_nest_mound", px_ + 8, py_ + 6, 4)
    P("den_stalagmites", px_ - 10, py_ - 7, 4)
    P("den_leg_bones", px_ + 6, py_ - 8, 2)
    # ---- Naralex's Dream: the sleeping druid's circle, glowing and strange
    dx, dy = R["dream"][:2]
    P("den_glow_mushrooms", dx - 13, dy + 4, 3)
    P("den_glow_mushrooms", dx + 13, dy + 4, 3)
    P("den_glow_mushrooms", dx - 6, dy - 9, 3)
    P("den_glow_mushrooms", dx + 7, dy - 9, 3)
    P("den_spring_pool", dx - 4, dy + 9, 3, solid=False)
    P("den_egg_cluster", dx + 9, dy + 8, 2)
    # ---- nooks
    for key, name, n in (("nook_sw", "grotto_serpent_skeleton", 3), ("nook_w", "den_glow_mushrooms", 3),
                         ("nook_se", "den_glow_mushrooms", 3)):
        nx, ny = R[key][:2]
        P(name, nx + 3, ny + 3, n)
        P("den_leg_bones", nx - 3, ny + 2, 2)
    # ---- sparse corridor dressing
    for key, t, name, h in (("entry", 0.5, "den_stalagmites", 3), ("w_arm_a", 0.5, "vot_reeds", 3),
                            ("w_arm_b", 0.4, "den_stalagmites", 4), ("w_arm_b", 0.8, "den_leg_bones", 2),
                            ("nw_arm", 0.45, "vot_fallen_log", 3), ("n_arm", 0.5, "den_stalagmites", 3),
                            ("dream", 0.5, "den_rock_rubble", 2), ("e_arm_a", 0.5, "vot_reeds", 3),
                            ("e_arm_b", 0.5, "den_stalagmites", 4)):
        x, y = walk(key, t)
        P(name, round(x) + 2, round(y) + 1, h)

    # ============================================================ HAND-PLACED TRASH
    TRASH.clear()
    occupied = []

    def put(x, y, name, lvl):
        p = _near_walkable(zone, x, y, rad=3)
        if p is None:
            raise AssertionError(f"no floor near ({x},{y}) for {name}")
        for q in occupied:
            if max(abs(p[0] - q[0]), abs(p[1] - q[1])) < 2:
                alt = _near_walkable(zone, p[0] + 2, p[1] + 1, rad=3)
                if alt and all(max(abs(alt[0] - o[0]), abs(alt[1] - o[1])) >= 2 for o in occupied):
                    p = alt
                break
        occupied.append(p)
        TRASH.append((p[0], p[1], name, lvl))

    def pack(key, t, members, lateral=1.9):
        x0, y0 = walk(key, t)
        x1, y1 = walk(key, min(1.0, t + 0.02))
        dx_, dy_ = x1 - x0, y1 - y0
        n = math.hypot(dx_, dy_) or 1.0
        nx_, ny_ = -dy_ / n, dx_ / n
        for i, (name, lvl) in enumerate(members):
            lat = (i - (len(members) - 1) / 2.0) * lateral
            put(x0 + nx_ * lat + (dx_ / n) * ((i % 2) * 1.4 - 0.7), y0 + ny_ * lat + (dy_ / n) * ((i % 2) * 1.4 - 0.7),
                name, lvl)

    def around(cx_, cy_, members, spread=5.0, start=0.0, sq=1.0):
        k = len(members)
        for i, (name, lvl) in enumerate(members):
            a = start + 2 * math.pi * i / k
            put(cx_ + spread * math.cos(a), cy_ + spread * sq * math.sin(a), name, lvl)

    Py, Oz, Rp, Cr = "Deviate Python", "Deviate Ooze", "Deviate Raptor", "Deviate Crocolisk"
    Ad, La, Rv, Vp, Sh = "Deviate Adder", "Deviate Lasher", "Deviate Ravager", "Deviate Viper", "Deviate Shambler"
    Fd, Dn, Df_ = "Deviate Faerie Dragon", "Druid of the Fang", "Dreadfang"
    In, Wp, Br = "Fang Initiate", "Nightmare Wisp", "Deviate Broodling"

    # ---- the Maw + entry tube (16-17)
    pack("entry", 0.25, [(Br, 16), (Br, 16)], lateral=1.2)
    pack("entry", 0.7, [(Py, 16), (Rp, 16)], lateral=1.2)
    # ---- Serpentbloom Cavern: south bank (17-18), river crossing (18), north platform guard (19)
    around(gx, gy + 8, [(Rp, 17), (Cr, 17), (Py, 17), (Oz, 17), (Br, 17)], spread=21.0, start=0.2, sq=0.35)
    around(gx - 18, gy + 4, [(Cr, 18), (Cr, 18), (Rp, 18)], spread=5.5, start=0.8)
    around(gx + 18, gy + 4, [(Cr, 18), (Oz, 18), (Rp, 18)], spread=5.5, start=0.3)
    around(gx, gy + 2, [(Ad, 18), (Vp, 18), (Ad, 18), (Py, 18)], spread=6.0, start=1.0, sq=0.6)
    around(ax, ay, [(Dn, 19), (Dn, 19), (In, 19), (Rp, 19)], spread=10.0, start=0.5, sq=0.55)
    pack("sw_nook", 0.5, [(Py, 18), (Br, 18)], lateral=1.2)
    # ---- west arm: lashers + druids toward Cobrahn (18-19)
    pack("w_arm_a", 0.25, [(La, 18), (Rp, 18)])
    pack("w_arm_a", 0.7, [(Dn, 19), (Df_, 19), (Dn, 19)])
    around(cx, cy, [(Dn, 20), (In, 19), (In, 20), (Df_, 19), (Rv, 20)], spread=9.5, start=0.6, sq=0.8)
    pack("w_arm_b", 0.15, [(La, 19), (Sh, 19)])
    pack("w_arm_b", 0.45, [(Rv, 20), (Vp, 19), (Ad, 19)])
    pack("w_arm_b", 0.8, [(Dn, 20), (In, 20)])
    pack("nook_w", 0.5, [(Sh, 20), (Wp, 20)], lateral=1.2)
    # ---- Kresh's pool (19-20)
    around(kx, ky, [(Cr, 19), (Cr, 20), (Oz, 19), (Oz, 20), (Fd, 20)], spread=13.0, start=0.3, sq=0.65)
    pack("nw_arm", 0.2, [(Dn, 20), (La, 20)])
    pack("nw_arm", 0.5, [(Rv, 20), (Wp, 20), (Rv, 20)])
    pack("nw_arm", 0.82, [(In, 20), (Dn, 20)])
    # ---- Skum's gallery (20-21)
    around(sx, sy, [(Rp, 20), (Rp, 20), (Rv, 21), (Sh, 20), (Rp, 21)], spread=10.0, start=0.9, sq=0.55)
    pack("n_arm", 0.2, [(Dn, 20), (In, 20), (Fd, 21)])
    pack("n_arm", 0.55, [(Wp, 21), (La, 21), (Wp, 21)])
    pack("n_arm", 0.85, [(In, 21), (Dn, 21)])
    # ---- the Chamber of the Fang (21-22): Serpentis + Verdan with their acolytes
    around(fx, fy, [(Dn, 21), (Dn, 21), (In, 21), (In, 22), (Df_, 21), (Wp, 21), (Dn, 22), (In, 21)],
           spread=14.0, start=0.3, sq=0.55)
    around(fx - 10, fy, [(In, 22), (Dn, 22)], spread=3.5, start=0.4)
    around(fx + 11, fy, [(Rv, 22), (Sh, 22)], spread=3.5, start=1.1)
    # ---- the Dream spur + Naralex's Dream (21-23)
    pack("dream", 0.2, [(Wp, 21), (Wp, 21)], lateral=1.4)
    pack("dream", 0.55, [(Wp, 22), (Sh, 22), (Wp, 22)])
    pack("dream", 0.85, [(Wp, 22), (Fd, 22)], lateral=1.4)
    around(dx, dy, [(Wp, 22), (Wp, 22), (Wp, 22), (Wp, 22), (Sh, 22), (Fd, 22)], spread=9.5, start=0.5, sq=0.65)
    # ---- east arm to Pythas (20-21)
    pack("e_arm_a", 0.25, [(La, 20), (Sh, 20)])
    pack("e_arm_a", 0.6, [(Rv, 21), (Dn, 21), (Rv, 21)])
    around(px_, py_, [(Dn, 21), (In, 21), (Dn, 21), (Df_, 21), (Rp, 21)], spread=9.5, start=0.7, sq=0.7)
    pack("e_arm_b", 0.25, [(Cr, 20), (Oz, 20)])
    pack("e_arm_b", 0.65, [(Rp, 20), (Rp, 20), (Df_, 20)])
    pack("nook_se", 0.5, [(Oz, 21), (Oz, 21)], lateral=1.2)
    zone.trash_spawns = list(TRASH)
    return zone, L


def generate_wailing_caverns():
    zone, L = build_wailing()
    dress_and_trash(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_wailing_baked():
    """(zone, layout) with props + QA done - what the baker paints from."""
    zone, L = build_wailing()
    dress_and_trash(zone, L)
    finish(zone, L)
    return zone, L
