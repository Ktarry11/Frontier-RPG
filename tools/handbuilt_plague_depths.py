"""
Hand-built Plague Depths (240x220): the Royal Apothecary Society's old plague vaults beneath Undercity, where a cabal of
Forsaken alchemists is breeding a plague to overthrow Sylvanas and crown one of their own.  FIVE BOSSES.

ARCHETYPE: THE LADDER (twin aqueducts + rungs).  Two long galleries (the rails) run north from the Outer Cistern, joined by
three cross-passages (the rungs):

    rung 1  The Outer Cistern   (y 176)  - the entry hall; both rails start here
    rung 2  The Mid Conduit     (y 124)  - a cross-over half way up (skip a boss room? no: it only joins the corridors)
    rung 3  The Antechamber     (y  66)  - both rails end here; one stair north to the Plague Heart
    W rail  THE COURT   : The Weaving Hall (Plagueweaver Vex 31)  ->  The Throne of Rot (The Infected Noble 32, the cabal's pretender)
    E rail  THE LAB     : The Blight Archive (Plague Keeper Voss 32) -> The Vault of Flesh (Vile Plague Abomination 33)
    N       The Plague Heart (Dark Sorcerer Zul'keth 34, final boss) - only reachable through the Antechamber

You choose a rail first (the Lab hits harder), and either rail is a full gauntlet of two boss rooms: you cannot reach the
Antechamber without clearing one of them.  Six dead-end nooks (quarantine ward, specimen cellar, sump, chute, closets)
hold the chests.  (Broodspiral = spiral, RFK = warren wheel, Wailing = river ring, Moonwell = twin bowl, Barrows = cross,
Grom's Rest = hub + spine; this is the only ladder.)

Levels (Kyle: about 32): trash 30-32 ramping with depth; bosses Vex 31, Noble 32, Voss 32, Abomination 33, Zul'keth 34.
TRASH IS HAND-PLACED (multi-boss rule, claude/dungeon_authoring_rules.md): `TRASH` -> zone.trash_spawns, packs of 3-4.

HARD CONTRACTS (world/portal_manager.py): portal (120,205) <-> Undercity Deeps Gate (100,185); arrival = 2 north.
Prop rule (Kyle): less is more; logical for the room; a few centrepieces.
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked, _apply_pools  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

UP = "assets/tiles/undercity/props/"
EKP = "assets/tiles/eastern_kingdoms/props/"
BAKED = "assets/tiles/plague_depths/baked"
W, H = 240, 220
PORTAL = (120, 205)

PATHS = {
    "approach": ([(120, 200), (118, 193), (120, 187)], 6.0, 6.5),
    "w_a":      ([(82, 174), (70, 166), (62, 158)], 5.2, 5.2),         # cistern -> Weaving Hall
    "w_b":      ([(60, 138), (56, 126), (58, 114)], 4.6, 4.6),         # Weaving Hall -> Throne of Rot (rung 2 crosses it)
    "w_c":      ([(60, 84), (66, 74), (84, 68)], 5.0, 5.0),            # Throne -> Antechamber
    "e_a":      ([(158, 174), (170, 166), (178, 158)], 5.2, 5.2),
    "e_b":      ([(180, 138), (184, 126), (182, 114)], 4.6, 4.6),
    "e_c":      ([(180, 84), (176, 74), (156, 68)], 5.0, 5.0),
    "mid_w":    ([(54, 126), (80, 121), (104, 125)], 4.4, 4.4),        # rung 2, west half
    "mid_e":    ([(186, 126), (160, 121), (136, 125)], 4.4, 4.4),      # rung 2, east half
    "to_heart": ([(120, 57), (123, 49), (120, 40)], 4.6, 4.6),         # the only way to the Heart
    "nook_w":   ([(52, 134), (40, 137), (31, 136)], 3.0, 3.0),
    "nook_e":   ([(188, 134), (200, 137), (209, 136)], 3.0, 3.0),
    "nook_sw":  ([(84, 180), (64, 187), (48, 192)], 3.2, 3.2),
    "nook_se":  ([(156, 180), (176, 187), (192, 192)], 3.2, 3.2),
    "nook_nw":  ([(90, 28), (80, 30), (73, 30)], 3.2, 3.2),
    "nook_ne":  ([(150, 28), (160, 30), (167, 30)], 3.2, 3.2),
}
ROOMS = {
    "gate":     (120, 206, 14, 6, 0, 0.4, "The Deeps Gate"),
    "cistern":  (120, 176, 40, 11, 0, 1.0, "The Outer Cistern"),
    "loom":     (58, 148, 22, 15, 0, 2.0, "The Weaving Hall"),
    "throne":   (58, 98, 25, 16, 0, 0.7, "The Throne of Rot"),
    "archive":  (182, 148, 23, 15, 0, 1.6, "The Blight Archive"),
    "vault":    (182, 98, 24, 16, 0, 2.5, "The Vault of Flesh"),
    "mid":      (120, 124, 17, 10, 0, 1.3, "The Mid Conduit"),
    "ante":     (120, 66, 24, 11, 0, 0.9, "The Antechamber"),
    "heart":    (120, 26, 32, 15, 0, 1.7, "The Plague Heart"),
    "nook_w":   (25, 136, 7, 5, 0, 1.2, "The Quarantine Ward"),
    "nook_e":   (215, 136, 7, 5, 0, 2.0, "The Specimen Cellar"),
    "nook_sw":  (40, 193, 8, 6, 0, 0.8, "The Overflow Sump"),
    "nook_se":  (200, 193, 8, 6, 0, 2.3, "The Cadaver Chute"),
    "nook_nw":  (66, 30, 7, 5, 0, 1.5, "The Alchemist's Closet"),
    "nook_ne":  (174, 30, 7, 5, 0, 0.3, "The Reagent Stores"),
}
# shallow plague-sludge pools (walkable, painted as sewer water): (cx, cy, rx, ry, phase)
PD_POOLS = [
    (95, 178, 7.0, 3.6, 0.5), (145, 178, 7.0, 3.6, 1.4),       # the cistern
    (176, 106, 5.0, 3.6, 2.0),                                 # beside the vault tables
    (98, 24, 4.5, 3.0, 0.9), (142, 24, 4.5, 3.0, 2.2),         # the Heart's sumps
]

LVL = {28: 30, 29: 30, 30: 31, 31: 31, 32: 32, 33: 32}      # pack tables below were drafted on a 28-33 ramp; fitted to 30-32
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


def build_plague():
    zone = Tilemap("Plague Depths", W, H,
                   "Beneath the Undercity the Apothecary Society's vaults still run. So does what they let out.")
    zone.is_cave = True
    zone.region = "Undercity"
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b

    for i, (key, (pts, w0, w1)) in enumerate(PATHS.items()):
        tube(b, pts, w0, w1, ph=0.5 + i * 0.9)
    for key, (cx, cy, rx, ry, rot, ph, _n) in ROOMS.items():
        cavern(b, cx, cy, rx, ry, rot, ph)
    # join each tube end into its room (short plugs)
    for pts in (((120, 199), (120, 202)), ((120, 187), (120, 184)), ((84, 174), (88, 175)), ((62, 158), (60, 156)),
                ((156, 174), (152, 175)), ((178, 158), (180, 156)), ((60, 138), (60, 141)), ((58, 114), (58, 112)),
                ((60, 84), (60, 86)), ((84, 68), (92, 67)), ((180, 138), (180, 141)), ((182, 114), (182, 112)),
                ((180, 84), (180, 86)), ((156, 68), (148, 67)), ((104, 125), (108, 125)), ((136, 125), (132, 125)),
                ((120, 57), (120, 60)), ((120, 40), (120, 38)), ((31, 136), (29, 136)), ((209, 136), (211, 136)),
                ((48, 192), (46, 192)), ((192, 192), (194, 192)), ((73, 30), (71, 30)), ((167, 30), (169, 30)),
                ((90, 28), (86, 28)), ((150, 28), (154, 28))):
        tube(b, list(pts), 4.0, 4.0)

    _apply_pools(zone, PD_POOLS, shallow_only=True)

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    bosses = [(58, 143, "Plagueweaver Vex"), (58, 93, "The Infected Noble"), (182, 143, "Plague Keeper Voss"),
              (182, 93, "Vile Plague Abomination"), (120, 21, "Dark Sorcerer Zul'keth")]
    fixed = []
    for (x, y, n) in bosses:
        p = _near_walkable(zone, x, y)
        assert p, (n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (fixed[4][0], fixed[4][1])          # Zul'keth is the final boss
    zone.boss_positions = list(fixed)

    chests = []
    for (x, y) in ((22, 136), (218, 136), (36, 195), (204, 195), (63, 31), (177, 31), (101, 64), (139, 64)):
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        chests.append(p)
    CHESTS[:] = chests
    for c in chests:
        L.mark("chest", *c)

    def sub(name, x, y, rx, ry):
        zone.add_subzone(name, int(x - rx), int(y - ry), int(2 * rx), int(2 * ry))
    zone.add_subzone("Plague Depths", 0, 0, W, H)           # whole-map cave-table key first; named rooms re-register after
    for key, (cx, cy, rx, ry, rot, ph, name) in ROOMS.items():
        sub(name, cx, cy, rx + 2, ry + 2)
    return zone, L


def finish(zone, L):
    targets = [PORTAL] + [(x, y) for (x, y) in BOSSES.values()] + list(CHESTS)
    return L.finish(targets)


def dress(zone, L):
    def P(name, cx, by, h, **kw):
        kw.setdefault("where", DP)
        return L.prop(name, cx, by, h, **kw)

    def U(name, cx, by, h, **kw):
        return P(name, cx, by, h, where=UP, **kw)

    def E(name, cx, by, h, **kw):
        return P(name, cx, by, h, where=EKP, **kw)
    R = ROOMS
    # ---- the Deeps Gate: outfalls and skull pillars flank the way in
    gx0, gy0 = R["gate"][:2]
    U("uc_skull_pillar", gx0 - 9, gy0 + 1, 7, solid="core")
    U("uc_skull_pillar", gx0 + 9, gy0 + 1, 7, solid="core")
    P("spirit_brazier", gx0 - 5, gy0 - 3, 4, solid="core")
    P("spirit_brazier", gx0 + 5, gy0 - 3, 4, solid="core")
    U("uc_bone_heap", gx0 + 3, gy0 + 3, 3)
    # ---- the Outer Cistern: vats and pipes against the long walls, a cauldron in the middle
    cx, cy = R["cistern"][:2]
    U("uc_sewer_outlet", cx - 34, cy - 4, 6, solid="core")
    U("uc_sewer_outlet", cx + 34, cy - 4, 6, solid="core")
    U("uc_plague_vat", cx - 22, cy - 7, 5, solid="core")
    U("uc_plague_vat", cx + 22, cy - 7, 5, solid="core")
    U("uc_pipe_cluster", cx - 12, cy - 8, 5, solid="core")
    U("uc_pipe_cluster", cx + 12, cy - 8, 5, solid="core")
    E("ek_plague_cauldron", cx, cy - 1, 5, solid="core", avoid=1)
    U("uc_bone_heap", cx - 14, cy + 6, 3)
    U("uc_floor_grate", cx + 14, cy + 6, 2, near_ok=True)
    # ---- the Weaving Hall (Vex): cocoons and webbing, a worktable of threads
    lx, ly = R["loom"][:2]
    P("web_tangle", lx - 12, ly - 4, 4, solid="core")
    P("web_tangle", lx + 12, ly - 4, 4, solid="core")
    P("cocoon_victim", lx - 8, ly + 7, 5, solid="core")
    P("cocoon_victim", lx + 9, ly + 7, 5, solid="core")
    P("den_web_cocoon", lx, ly - 9, 5, solid="core", avoid=1)
    U("uc_alchemy_table", lx - 15, ly + 4, 4, solid="core")
    P("bbc_candelabra", lx + 15, ly + 3, 4, solid="core")
    E("ek_egg_sacs", lx + 3, ly + 9, 3)
    # ---- the Throne of Rot (the Noble): a rotting throne under banners, a spoiled banquet
    tx, ty = R["throne"][:2]
    U("uc_throne", tx, ty - 10, 8, solid="core", avoid=1)
    U("uc_royal_banner", tx - 9, ty - 11, 7, solid="core")
    U("uc_royal_banner", tx + 9, ty - 11, 7, solid="core")
    P("banquet_table", tx, ty + 6, 5, solid="core", avoid=1)
    P("bbc_candelabra", tx - 14, ty - 3, 4, solid="core")
    P("bbc_candelabra", tx + 14, ty - 3, 4, solid="core")
    P("sarcophagus", tx - 17, ty + 7, 4, solid="core")
    P("sarcophagus", tx + 17, ty + 7, 4, solid="core")
    P("skull_pile", tx + 11, ty + 10, 3)
    # ---- the Blight Archive (Voss): shelves, a desk, jars of the unmentionable
    ax, ay = R["archive"][:2]
    for ox in (-15, -8, 8, 15):
        P("bbc_bookshelf", ax + ox, ay - 11, 5, solid="core")
    U("uc_jar_shelf", ax - 17, ay + 2, 4, solid="core")
    U("uc_jar_shelf", ax + 17, ay + 2, 4, solid="core")
    P("wizard_desk", ax, ay - 2, 4, solid="core", avoid=1)
    U("uc_lectern", ax - 9, ay + 7, 4, solid="core")
    U("uc_lectern", ax + 9, ay + 7, 4, solid="core")
    P("bbc_candelabra", ax - 4, ay + 9, 4, solid="core")
    # ---- the Vault of Flesh (the Abomination): operating tables, vats, cages
    vx, vy = R["vault"][:2]
    U("uc_operating_table", vx - 9, vy - 3, 4, solid="core")
    U("uc_operating_table", vx + 9, vy - 3, 4, solid="core")
    U("uc_plague_vat", vx - 17, vy + 4, 5, solid="core")
    U("uc_plague_vat", vx + 17, vy + 4, 5, solid="core")
    U("uc_plague_vat", vx, vy - 11, 5, solid="core", avoid=1)
    U("uc_cage_cell", vx - 14, vy - 9, 5, solid="core")
    U("uc_cage_cell", vx + 13, vy + 11, 5, solid="core")
    U("uc_copper_still", vx + 18, vy - 9, 5, solid="core")
    E("ek_plague_cart", vx - 18, vy - 8, 5, solid="core")
    # ---- the Mid Conduit: sluices at each end, pipework, a grate
    mx, my = R["mid"][:2]
    U("uc_sluice_gate", mx - 13, my - 4, 7, solid="core")
    U("uc_sluice_gate", mx + 13, my - 4, 7, solid="core")
    U("uc_pipe_cluster", mx - 5, my - 8, 5, solid="core")
    U("uc_pipe_cluster", mx + 5, my - 8, 5, solid="core")
    U("uc_floor_grate", mx, my + 3, 2, near_ok=True)
    U("uc_bone_heap", mx + 3, my + 7, 3)
    # ---- the Antechamber: the gate to the Heart
    nx, ny = R["ante"][:2]
    U("uc_skull_arch", 120, 58, 9, solid=False, near_ok=True, avoid=0)
    for ox in (-8, 8):
        U("uc_skull_pillar", nx + ox, ny - 5, 7, solid="core")
    P("spirit_brazier", nx - 15, ny + 2, 4, solid="core")
    P("spirit_brazier", nx + 15, ny + 2, 4, solid="core")
    U("uc_coffin_stack", nx - 17, ny - 5, 4, solid="core")
    U("uc_coffin_stack", nx + 17, ny - 5, 4, solid="core")
    P("skull_pile", nx - 4, ny + 7, 3)
    # ---- the Plague Heart (Zul'keth): the altar of the blight and its great vats
    hx, hy = R["heart"][:2]
    P("ritual_circle", hx, hy + 1, 10, solid=False, near_ok=True, avoid=0)
    P("rf_sacrificial_altar", hx, hy + 5, 7, solid="core", avoid=1)
    for ox in (-22, 22):
        U("uc_plague_vat", hx + ox, hy + 4, 5, solid="core")
    for ox in (-14, 14):
        P("bbc_rune_pillar", hx + ox, hy + 9, 6, solid="core")
    U("uc_pipe_cluster", hx - 27, hy - 1, 5, solid="core")
    U("uc_pipe_cluster", hx + 26, hy - 4, 5, solid="core")
    P("bbc_fel_brazier", hx - 8, hy - 4, 4, solid="core")
    P("bbc_fel_brazier", hx + 8, hy - 4, 4, solid="core")
    # ---- nooks: one small centrepiece each
    U("uc_cage_cell", R["nook_w"][0] + 1, R["nook_w"][1] + 2, 4, solid="core")
    U("uc_jar_shelf", R["nook_e"][0] - 2, R["nook_e"][1] + 1, 4, solid="core")
    U("uc_sewer_outlet", R["nook_sw"][0] - 1, R["nook_sw"][1] - 1, 5, solid="core")
    U("uc_coffin_stack", R["nook_se"][0] + 1, R["nook_se"][1] + 1, 4, solid="core")
    U("uc_alchemy_table", R["nook_nw"][0], R["nook_nw"][1] + 1, 4, solid="core")
    U("uc_crate_stack", R["nook_ne"][0], R["nook_ne"][1] + 1, 3, solid="core")

    # ============================================================ HAND-PLACED TRASH (packs of 3-4)
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
        TRASH.append((p[0], p[1], name, LVL.get(lvl, lvl)))

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

    def at(cx_, cy_, members, spread=3.2, start=0.0):
        k = len(members)
        for i, (name, lvl) in enumerate(members):
            a = start + 2 * math.pi * i / k
            put(cx_ + spread * math.cos(a), cy_ + spread * 0.8 * math.sin(a), name, lvl)

    Pr, Rw, Ph, Ps, Pz = "Plagued Rat", "Rot Worm", "Plagued Hound", "Plague Spore", "Plague Zombie"
    Ft, Fw, Ir, Bc = "Forsaken Traitor", "Forsaken Witch", "Infected Retainer", "Blighted Courtier"
    Su, Bl, Pa, Fe = "Plague Surgeon", "Blight Cultist", "Plague Abomination", "Failed Experiment"

    # ---- the gate + approach + Outer Cistern (28-29)
    pack("approach", 0.45, [(Pr, 28), (Rw, 28), (Pr, 28)], lateral=1.6)
    at(cx - 24, cy + 1, [(Pr, 28), (Pr, 28), (Rw, 28), (Ps, 28)], spread=3.4, start=0.3)
    at(cx + 24, cy + 1, [(Ph, 28), (Ph, 28), (Rw, 28)], spread=3.2, start=0.9)
    at(cx - 8, cy + 6, [(Pz, 29), (Pz, 29), (Ps, 28), (Rw, 29)], spread=3.2, start=0.5)
    at(cx + 9, cy + 6, [(Ph, 29), (Pz, 29), (Pz, 29)], spread=3.0, start=0.2)
    pack("nook_sw", 0.5, [(Rw, 29), (Pr, 29), (Pr, 29)], lateral=1.4)
    pack("nook_se", 0.5, [(Ps, 29), (Ps, 29), (Rw, 29)], lateral=1.4)
    # ---- the Court (west rail): 29-32
    pack("w_a", 0.5, [(Ft, 29), (Ir, 29), (Ft, 29)], lateral=1.6)
    at(lx - 10, ly + 1, [(Ft, 30), (Ir, 30), (Bc, 30), (Pz, 30)], spread=3.4, start=0.3)
    at(lx + 10, ly + 1, [(Fw, 30), (Ft, 30), (Ir, 30), (Pz, 30)], spread=3.4, start=0.8)
    at(lx, ly + 9, [(Bc, 30), (Pz, 30), (Pz, 30)], spread=3.0, start=0.5)
    pack("w_b", 0.5, [(Ir, 30), (Bc, 30), (Ir, 30)], lateral=1.3)
    pack("nook_w", 0.55, [(Pz, 30), (Pz, 30)], lateral=1.4)
    at(tx - 12, ty + 2, [(Ir, 31), (Ft, 31), (Bc, 31), (Fw, 31)], spread=3.4, start=0.2)
    at(tx + 12, ty + 2, [(Ir, 31), (Ir, 31), (Fw, 31), (Pz, 31)], spread=3.4, start=0.9)
    at(tx, ty + 10, [(Ft, 31), (Bc, 32), (Pz, 31)], spread=3.0, start=0.6)
    pack("w_c", 0.5, [(Ir, 32), (Fw, 32), (Ir, 32)], lateral=1.5)
    # ---- the Lab (east rail): 30-33
    pack("e_a", 0.5, [(Bl, 30), (Su, 30), (Bl, 30)], lateral=1.6)
    at(ax - 10, ay + 1, [(Bl, 31), (Su, 31), (Bl, 31), (Fe, 31)], spread=3.4, start=0.3)
    at(ax + 10, ay + 1, [(Su, 31), (Bl, 31), (Fe, 31), (Fe, 31)], spread=3.4, start=0.8)
    at(ax, ay + 9, [(Bl, 31), (Su, 31), (Ph, 31)], spread=3.0, start=0.5)
    pack("e_b", 0.5, [(Fe, 31), (Su, 31), (Fe, 31)], lateral=1.3)
    pack("nook_e", 0.55, [(Fe, 31), (Fe, 31)], lateral=1.4)
    at(vx - 12, vy + 1, [(Pa, 32), (Fe, 32), (Su, 32), (Bl, 32)], spread=3.4, start=0.2)
    at(vx + 12, vy + 1, [(Pa, 32), (Fe, 32), (Fe, 32), (Su, 32)], spread=3.4, start=0.9)
    at(vx, vy + 10, [(Pa, 32), (Bl, 32), (Fe, 33)], spread=3.0, start=0.6)
    pack("e_c", 0.5, [(Pa, 33), (Su, 33), (Fe, 33)], lateral=1.5)
    # ---- the Mid Conduit (30-31): the only trash that is not on a rail
    at(mx - 6, my + 1, [(Ph, 30), (Rw, 30), (Ps, 30)], spread=3.0, start=0.4)
    at(mx + 6, my + 1, [(Ph, 31), (Ph, 31), (Rw, 31)], spread=3.0, start=0.9)
    # ---- the Antechamber + Heart (32-33)
    at(nx - 10, ny + 1, [(Pa, 32), (Ir, 32), (Fw, 32), (Su, 32)], spread=3.4, start=0.3)
    at(nx + 10, ny + 1, [(Pa, 32), (Fe, 32), (Bl, 33), (Bc, 32)], spread=3.4, start=0.8)
    pack("to_heart", 0.45, [(Pa, 33), (Bl, 33), (Pa, 33)], lateral=1.3)
    at(hx - 17, hy + 3, [(Pa, 33), (Su, 33), (Bl, 33), (Fe, 33)], spread=3.4, start=0.2)
    at(hx + 17, hy + 3, [(Pa, 33), (Su, 33), (Bl, 33), (Fe, 33)], spread=3.4, start=0.9)
    at(hx, hy + 9, [(Fw, 33), (Fw, 33), (Pa, 33)], spread=3.0, start=0.5)
    pack("nook_nw", 0.5, [(Su, 32), (Bl, 32)], lateral=1.4)
    pack("nook_ne", 0.5, [(Fe, 32), (Bl, 32)], lateral=1.4)
    zone.trash_spawns = list(TRASH)
    return zone, L


def generate_plague_depths():
    zone, L = build_plague()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_plague_baked():
    """(zone, layout) with props + QA done - what the baker paints from."""
    zone, L = build_plague()
    dress(zone, L)
    finish(zone, L)
    return zone, L
