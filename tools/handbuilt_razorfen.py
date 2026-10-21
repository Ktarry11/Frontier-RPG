"""
Hand-built Razorfen Kraul (240x220): the quilboar thorn-warren under the Southern Barrens.

ARCHETYPE: THE WARREN WHEEL (hub-and-radial with rim loops).  Not a spiral (Broodspiral), not a rotunda/C-warren
(Echo), not a gorge.  One central TRUNK of thorn-tunnel runs south->north through the dungeon's four great
chambers; two RIM LOOPS peel off the Thorn Court to the flanking boss pens and rejoin the Boar Pens hub from the
side, so the middle of the dungeon is a wheel you can run either way round.  Three spokes leave the hub:
the sealed NW neck to the Beast Pit, the N ramp to Charlga's Platform, and (from the first fork) the long vine
bridge west to Roogug's detour.

  Thorn Gate (entrance) -> Bramble Fork -+-> vine bridge W -> Roogug's Platform (optional dead end)
                                          |
                                          +-> trunk N -> THORN COURT -+-> W rim -> Aggem's Pen   -> W gallery -+
                                                                      +-> E rim -> Jargba's Chamber -> E gallery -+
                                                                      +-> trunk N ----------------------------+--> THE BOAR PENS (hub, Ramtusk)
                                                                                                                  |-> NW neck (Ward-Keepers) -> Agathelos's Pit
                                                                                                                  '-> N ramp -> Charlga's Platform
  rares: Blind Hunter (W gallery nook), Earthcaller Halmgar (E gallery nook), Thornjaw the Gorger (N-ramp nook)

Boss levels (Kyle's ladder): Roogug 28, Aggem 30, Jargba 30, Ramtusk 32, Agathelos 32, Charlga 34; trash 25-31.
TRASH IS HAND-PLACED (multi-boss dungeon rule, claude/dungeon_authoring_rules.md): `TRASH` -> zone.trash_spawns.

HARD CONTRACTS (world/portal_manager.py): portal (120,208) <-> Southern Barrens (55,175); arrival = 2 north.
Prop rule (Kyle): less is more; logical for the room; a few centrepieces.
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube, wall_annulus

BP = "assets/tiles/barrens/props/"
BAKED = "assets/tiles/razorfen_kraul/baked"
W, H = 240, 220
PORTAL = (120, 208)

# ---- the tunnel network (control points; also what trash is walked along) -------------------------------
PATHS = {
    "approach":  ([(120, 198), (121, 190), (119, 182)], 5.0, 5.0),
    "bridge":    ([(105, 177), (88, 181), (68, 184)], 2.8, 2.8),
    "trunk_s":   ([(120, 168), (118, 158), (121, 150)], 5.0, 5.0),
    "w_rim_a":   ([(104, 142), (86, 138), (66, 140)], 4.4, 4.4),
    "w_rim_b":   ([(40, 121), (36, 108), (45, 97), (62, 91), (82, 92)], 4.4, 4.4),
    "e_rim_a":   ([(136, 141), (158, 137), (178, 134)], 4.4, 4.4),
    "e_rim_b":   ([(204, 114), (206, 102), (196, 93), (176, 89), (156, 91)], 4.4, 4.4),
    "trunk_n":   ([(121, 130), (119, 122), (121, 112)], 5.0, 5.0),
    "n_ramp":    ([(121, 74), (123, 62), (118, 50), (121, 38)], 4.6, 4.6),
    "nw_neck":   ([(102, 78), (88, 68), (74, 59)], 3.4, 3.2),
    "nook_w":    ([(40, 106), (30, 103), (21, 101)], 3.0, 3.0),
    "nook_e":    ([(206, 103), (214, 100), (222, 98)], 3.0, 3.0),
    "nook_n":    ([(122, 56), (136, 54), (150, 51)], 3.0, 3.0),
}
# ---- chambers: (key, cx, cy, rx, ry, rot, phase, display name) ------------------------------------------
ROOMS = {
    "gate":     (120, 202, 13, 7, 0, 0.4, "The Thorn Gate"),
    "fork":     (119, 175, 16, 9, 0, 1.1, "The Bramble Fork"),
    "roogug":   (45, 183, 17, 11, 8, 0.6, "Roogug's Platform"),
    "court":    (120, 141, 19, 12, 0, 2.0, "The Thorn Court"),
    "aggem":    (46, 133, 18, 13, -10, 2.7, "Aggem's Pen"),
    "jargba":   (193, 128, 17, 12, 12, 3.3, "Jargba's Chamber"),
    "hub":      (120, 92, 25, 19, 0, 0.9, "The Boar Pens"),
    "pit":      (46, 47, 20, 15, 15, 1.7, "Agathelos's Pit"),
    "charlga":  (120, 25, 23, 13, 0, 2.4, "Charlga's Platform"),
    "nook_w":   (19, 100, 8, 6, 0, 0.8, "The Hunter's Blind"),
    "nook_e":   (224, 97, 8, 6, 0, 1.4, "Halmgar's Hollow"),
    "nook_n":   (153, 50, 8, 6, 0, 2.2, "The Gorger's Wallow"),
}
# boar-pen stalls around the hub rim (angle deg from hub centre, radius multiplier of rx/ry, stall rx, ry)
STALLS = [(28, 0, 7.4, 5.4), (62, 0, 7.4, 5.4), (118, 0, 7.4, 5.4), (152, 0, 7.4, 5.4), (330, 0, 7.4, 5.4)]
CORRAL = (8.2, 11.8, (90, 215, 322))      # Ramtusk's pen: ring wall r0..r1 with gaps S / NW / NE

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
    """Point at fraction t (0..1) along a path's control polyline."""
    pts = PATHS[key][0]
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    d = t * sum(seg)
    for i, s in enumerate(seg):
        if d <= s or i == len(seg) - 1:
            u = min(1.0, d / s) if s else 0.0
            return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * u, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * u)
        d -= s


def room_xy(key):
    return ROOMS[key][0], ROOMS[key][1]


def build_razorfen():
    zone = Tilemap("Razorfen Kraul", W, H,
                   "Thorn tunnels choked with bramble. Quilboar ancestral home, ruled by Charlga Razorflank and the "
                   "spirits of Agamaggan.")
    zone.is_cave = True
    zone.region = "Southern Barrens"
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b

    for i, (key, (pts, w0, w1)) in enumerate(PATHS.items()):
        tube(b, pts, w0, w1, ph=0.5 + i * 0.9)
    for key, (cx, cy, rx, ry, rot, ph, _n) in ROOMS.items():
        cavern(b, cx, cy, rx, ry, rot, ph)
    hx, hy, hrx, hry = ROOMS["hub"][:4]
    stall_pos = []
    for k, (ang, rm, srx, sry) in enumerate(STALLS):
        a = math.radians(ang)
        sx, sy = hx + (hrx + 3) * math.cos(a), hy + (hry + 3) * math.sin(a)
        cavern(b, sx, sy, srx, sry, ang + 90, 0.7 + k * 1.3)
        stall_pos.append((round(sx), round(sy)))
    wall_annulus(zone, hx, hy, CORRAL[0], CORRAL[1], CORRAL[2], gate_half_deg=15)
    # tubes into the corner rooms that the path lists only imply
    tube(b, [(120, 196), (120, 202)], 5, 5)
    tube(b, [(70, 183), (62, 183)], 3, 3)
    tube(b, [(138, 141), (144, 141)], 4.4, 4.4)
    tube(b, [(60, 140), (56, 138)], 4.4, 4.4)
    tube(b, [(178, 134), (184, 132)], 4.4, 4.4)
    tube(b, [(124, 112), (121, 106)], 5, 5)
    tube(b, [(121, 132), (121, 128)], 5, 5)
    tube(b, [(121, 38), (121, 32)], 4.6, 4.6)
    tube(b, [(74, 59), (62, 54)], 3.2, 3.4)
    tube(b, [(82, 92), (95, 92)], 4.4, 4.4)
    tube(b, [(156, 91), (146, 91)], 4.4, 4.4)
    tube(b, [(40, 121), (42, 126)], 4.4, 4.4)
    tube(b, [(204, 114), (200, 120)], 4.4, 4.4)
    tube(b, [(121, 76), (121, 72)], 4.6, 4.6)
    tube(b, [(102, 78), (106, 82)], 3.6, 3.6)

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    bosses = [
        (45, 180, "Roogug"), (46, 131, "Aggem Thorncurse"), (193, 126, "Death Speaker Jargba"),
        (120, 88, "Overlord Ramtusk"), (42, 44, "Agathelos the Raging"), (120, 21, "Charlga Razorflank"),
        (19, 99, "Blind Hunter"), (224, 96, "Earthcaller Halmgar"), (153, 49, "Thornjaw the Gorger"),
    ]
    fixed = []
    for (x, y, n) in bosses:
        p = _near_walkable(zone, x, y)
        assert p, (n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (fixed[5][0], fixed[5][1])
    zone.boss_positions = list(fixed)

    chests = []
    for (x, y) in ((54, 188), (36, 136), (200, 133), (60, 58), (130, 24), (24, 98), (228, 100)):
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
    zone._stall_pos = stall_pos
    return zone, L


def finish(zone, L):
    targets = [PORTAL] + [(x, y) for (x, y) in BOSSES.values()] + list(CHESTS)
    return L.finish(targets)


def dress_and_trash(zone, L):
    P = L.prop
    hx, hy = ROOMS["hub"][:2]
    px, py = ROOMS["charlga"][:2]
    ax, ay = ROOMS["aggem"][:2]
    jx, jy = ROOMS["jargba"][:2]
    qx, qy = ROOMS["pit"][:2]
    rx_, ry_ = ROOMS["roogug"][:2]
    # ---- thorn gate: the bramble arch over the mouth
    P("br_razorfen_bramble_gate", 120, 199, 8, where=BP, solid=False, near_ok=True, avoid=0)
    P("br_thorn_scrub", 111, 203, 3, where=BP)
    P("den_leg_bones", 129, 204, 2)
    # ---- fork: a quilboar guard post
    P("vot_war_banner", 110, 172, 5)
    P("vot_war_banner", 128, 172, 5)
    P("vot_fire_pit", 119, 178, 2, solid=False)
    P("vot_hide_rack", 126, 179, 3)
    # ---- Roogug's platform: a warrior's yard at the end of the vine bridge
    P("weapon_rack", rx_ + 7, ry_ + 6, 4)
    P("vot_training_dummy", rx_ - 7, ry_ - 5, 3)
    P("skull_pile", rx_ - 6, ry_ + 6, 2)
    P("vot_hide_rack", rx_ + 9, ry_ - 3, 3)
    # ---- thorn court: the last crossroads before the pens
    P("vot_totem_pole", 108, 135, 6, solid="core")
    P("vot_totem_pole", 132, 135, 6, solid="core")
    P("vot_crate_stack", 126, 147, 3)
    P("vot_beast_ribcage", 112, 148, 3)
    # ---- Aggem's pen: beast-trainers' kennels
    P("kennel_cage_empty", ax + 8, ay + 3, 4)
    P("kennel_cage_empty", ax - 9, ay + 5, 4)
    P("vot_palisade", ax + 4, ay + 8, 3, solid=True)
    P("vot_palisade", ax - 4, ay + 9, 3, solid=True)
    P("den_leg_bones", ax + 1, ay - 8, 2)
    P("vot_hide_rack", ax - 3, ay - 9, 3)
    # ---- Jargba's chamber: Death's Head ritual ground
    P("ritual_circle", jx, jy + 1, 6, solid=False, near_ok=True, avoid=0)
    P("candelabra", jx - 8, jy - 3, 4, solid="core")
    P("candelabra", jx + 8, jy - 3, 4, solid="core")
    P("skull_pile", jx + 9, jy + 6, 2)
    P("vot_totem_pole", jx - 11, jy + 4, 6, solid="core")
    # ---- the boar pens
    P("vot_war_banner", hx - 6, hy + 13, 5)
    P("vot_war_banner", hx + 6, hy + 13, 5)
    P("vot_crate_stack", hx - 17, hy + 4, 3)
    P("vot_hide_rack", hx + 17, hy + 5, 3)
    P("vot_beast_ribcage", hx + 14, hy - 12, 3)
    P("den_nest_mound", hx - 13, hy - 8, 4)
    for sx, sy in zone._stall_pos[:4]:
        P("den_nest_mound", sx, sy + 1, 3)
    # corral fence: palisade posts standing ON the ring wall (the rock ring blocks; the fence is what you read)
    rmid = (CORRAL[0] + CORRAL[1]) / 2.0
    ang = 0.0
    while ang < 360:
        gap = min(min(abs(ang - g) % 360, 360 - abs(ang - g) % 360) for g in CORRAL[2])
        if gap > 19:
            a_ = math.radians(ang)
            L.b.prop(DP + "vot_palisade.png", round(hx + rmid * math.cos(a_)), round(hy + rmid * math.sin(a_)) + 1, 3,
                     solid=False)
        ang += 360.0 / (2 * math.pi * rmid / 2.1)

    # ---- n-ramp + gorger's wallow
    P("vot_war_drum", 125, 66, 3)
    P("vot_thornbush", 116, 56, 3)
    P("vot_thornbush", 128, 46, 3)
    ng = ROOMS["nook_n"][:2]
    P("den_nest_mound", ng[0] + 3, ng[1] + 3, 4)
    P("den_leg_bones", ng[0] - 4, ng[1] + 2, 2)
    # ---- Charlga's platform: the House of Razorflank
    P("br_quilboar_hut", px, py - 7, 11, where=BP, solid="core", near_ok=True, avoid=1)
    P("vot_totem_pole", px - 12, py - 2, 6, solid="core")
    P("vot_totem_pole", px + 12, py - 2, 6, solid="core")
    P("vot_war_banner", px - 6, py + 6, 5)
    P("vot_war_banner", px + 6, py + 6, 5)
    P("vot_fire_pit", px, py + 5, 2, solid=False)
    P("skull_pile", px + 16, py + 6, 2)
    P("vot_hide_rack", px - 16, py + 5, 3)
    # ---- the sealed neck + Agathelos's pit
    P("br_razorfen_bramble_gate", 70, 57, 7, where=BP, solid=False, near_ok=True, avoid=0)
    P("kennel_cage_worg", qx + 8, qy + 5, 4)
    P("kennel_cage_worg", qx - 10, qy + 4, 4)
    P("vot_beast_ribcage", qx + 2, qy + 8, 3)
    P("rf_shackle_frame", qx - 4, qy - 8, 4)
    P("den_leg_bones", qx + 10, qy - 6, 2)
    P("skull_pile", qx - 12, qy - 4, 2)
    # ---- nooks
    for key, name, n in (("nook_w", "vot_hide_rack", 3), ("nook_e", "skull_pile", 2)):
        nx, ny = ROOMS[key][:2]
        P(name, nx + 3, ny + 3, n)
        P("den_leg_bones", nx - 3, ny + 2, 2)
    # ---- sparse corridor dressing (thorns and bones where the quilboar dragged them)
    for key, t, name, h in (("approach", 0.5, "br_thorn_scrub", 3), ("trunk_s", 0.4, "vot_thornbush", 3),
                            ("w_rim_b", 0.5, "br_thorn_scrub", 3), ("e_rim_b", 0.5, "vot_thornbush", 3),
                            ("trunk_n", 0.5, "den_leg_bones", 2), ("bridge", 0.5, "br_tumbleweed_bones", 3),
                            ("w_rim_a", 0.6, "vot_thornbush", 3), ("e_rim_a", 0.4, "br_thorn_scrub", 3)):
        x, y = walk(key, t)
        P(name, round(x) + 2, round(y) + 1, h, where=BP if name.startswith("br_") else DP)

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
        dx, dy = x1 - x0, y1 - y0
        n = math.hypot(dx, dy) or 1.0
        nx_, ny_ = -dy / n, dx / n
        for i, (name, lvl) in enumerate(members):
            lat = (i - (len(members) - 1) / 2.0) * lateral
            put(x0 + nx_ * lat + (dx / n) * ((i % 2) * 1.4 - 0.7), y0 + ny_ * lat + (dy / n) * ((i % 2) * 1.4 - 0.7), name, lvl)

    def around(cx, cy, members, spread=5.0, start=0.0, sq=1.0):
        k = len(members)
        for i, (name, lvl) in enumerate(members):
            a = start + 2 * math.pi * i / k
            put(cx + spread * math.cos(a), cy + spread * sq * math.sin(a), name, lvl)

    Sp, Df, Bt, Hd = "Razorfen Spearhide", "Razorfen Defender", "Razorfen Beast Trainer", "Razorfen Handler"
    Gm, Tm, Wk = "Razorfen Geomancer", "Razorfen Totemic", "Razorfen Ward-Keeper"
    Ac, Cu = "Death's Head Acolyte", "Death's Head Cultist"
    Bb, Ag, So = "Kraul Bristleboar", "Raging Agam'ar", "Thornback Sow"

    # ---- approach + fork (25-26)
    pack("approach", 0.30, [(Bb, 25), (Bb, 25)])
    pack("approach", 0.75, [(Sp, 25), (Hd, 25)])
    around(119, 175, [(Sp, 26), (Df, 26), (Hd, 26)], spread=7.5, start=0.4)
    # ---- the vine bridge and Roogug's yard (26-28)
    pack("bridge", 0.25, [(Bb, 26), (Hd, 26)], lateral=1.2)
    pack("bridge", 0.7, [(Sp, 27), (Df, 27)], lateral=1.2)
    around(rx_, ry_, [(Sp, 27), (Sp, 28), (Df, 28), (Hd, 27)], spread=9.0, start=0.9)
    # ---- trunk to the court (26-27)
    pack("trunk_s", 0.35, [(Bb, 26), (Bb, 26), (Bt, 26)])
    pack("trunk_s", 0.85, [(Df, 27), (Hd, 27)])
    around(120, 141, [(Bt, 27), (Bb, 27), (Gm, 27), (Sp, 27), (Hd, 27)], spread=9.5, start=0.2, sq=0.65)
    # ---- west rim: Aggem (28-29)
    pack("w_rim_a", 0.30, [(Sp, 27), (Gm, 28)])
    pack("w_rim_a", 0.75, [(Bt, 28), (Bb, 28), (Bb, 28)])
    around(ax, ay, [(Bt, 29), (Bt, 29), (Ag, 29), (Gm, 29)], spread=8.0, start=0.5)
    pack("w_rim_b", 0.12, [(Df, 28), (Hd, 28)])
    pack("w_rim_b", 0.38, [(Sp, 29), (Gm, 29), (Sp, 29)])
    pack("w_rim_b", 0.62, [(Bb, 29), (Ag, 29)])
    pack("w_rim_b", 0.88, [(Df, 29), (Tm, 30)])
    pack("nook_w", 0.4, [(Hd, 29), (Hd, 29)], lateral=1.2)
    # ---- east rim: Jargba (28-30)
    pack("e_rim_a", 0.30, [(Ac, 27), (Sp, 27)])
    pack("e_rim_a", 0.75, [(Cu, 28), (Ac, 28), (Df, 28)])
    around(jx, jy, [(Cu, 29), (Ac, 29), (Ac, 29), (Cu, 30)], spread=8.0, start=1.3)
    pack("e_rim_b", 0.12, [(Sp, 29), (Hd, 29)])
    pack("e_rim_b", 0.38, [(Ac, 29), (Cu, 30), (Ac, 29)])
    pack("e_rim_b", 0.62, [(Df, 30), (Tm, 30)])
    pack("e_rim_b", 0.88, [(Bb, 29), (Ag, 29)])
    pack("nook_e", 0.4, [(Ac, 30), (Cu, 30)], lateral=1.2)
    # ---- trunk into the pens (28)
    pack("trunk_n", 0.4, [(Df, 28), (Sp, 28)])
    # ---- the boar pens (28-30): boars in stalls, handlers on the floor, Ramtusk's guard inside the corral
    for k, (sx, sy) in enumerate(zone._stall_pos):
        around(sx, sy, [(So if k % 2 else Bb, 29), (Bb, 28)], spread=2.6, start=0.8 + k)
    around(hx, hy, [(Bt, 29), (Hd, 29), (Gm, 29), (Tm, 30), (Sp, 29), (Df, 30)], spread=17.0, start=0.9, sq=0.72)
    around(hx, hy, [(Sp, 31), (Sp, 31)], spread=5.0, start=0.2)             # Ramtusk's two Spearhides
    # ---- the north ramp + the Gorger's wallow (30-31)
    pack("n_ramp", 0.15, [(Sp, 30), (Hd, 30)])
    pack("n_ramp", 0.45, [(Bt, 30), (Ag, 30), (Ag, 30)])
    pack("n_ramp", 0.78, [(Df, 31), (Tm, 31)])
    pack("nook_n", 0.4, [(So, 30), (Bb, 30)], lateral=1.2)
    around(px, py, [(Tm, 31), (Tm, 31), (Df, 31), (Df, 32), (Sp, 31), (Gm, 31)], spread=12.0, start=0.6, sq=0.6)
    # ---- the sealed neck: Ward-Keepers hold the door (29-30), the pit's own beasts inside (31)
    pack("nw_neck", 0.30, [(Wk, 29), (Sp, 29)])
    pack("nw_neck", 0.85, [(Wk, 30), (Wk, 30)], lateral=1.0)
    around(qx, qy, [(Ag, 31), (Ag, 31), (So, 31), (Bt, 31)], spread=9.0, start=0.3)
    zone.trash_spawns = list(TRASH)
    return zone, L


def generate_razorfen_kraul():
    zone, L = build_razorfen()
    dress_and_trash(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_razorfen_baked():
    """(zone, layout) with props + QA done - what the baker paints from."""
    zone, L = build_razorfen()
    dress_and_trash(zone, L)
    finish(zone, L)
    return zone, L
