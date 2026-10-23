"""
Hand-built Shadowfang Keep (200x180): Arugal's castle above the Pyrewood road.  FIVE BOSSES, hand-placed trash.

ARCHETYPE: THE STEPPED CASTLE.  The keep climbs in three tiers, south to north, and you choose your wings:

    tier 1  LOWER WARD    Gatehouse -> the Outer Bailey; Kennels (west, Rethilgore) and the Butcher's Yard (east, Razorclaw) off it
    tier 2  MIDDLE WARD   The Great Hall (Baron Silverlaine) - the one mandatory boss before the top.  Two cloisters leave it:
                          WEST  the Haunted Cloister -> Fenrus' Crypt (Fenrus the Devourer) -> crypt stair -> the Upper Landing
                          EAST  the Armoury Passage -> the Armoury (chests, the keep's rare) -> armoury stair -> the Upper Landing
    tier 3  UPPER KEEP    The Upper Landing -> Arugal's Sanctum (Archmage Arugal), a round tower room with two bay windows

So Fenrus is a real option, not a gate: the Armoury route skips him for loot instead.  Four nooks (hound pens, the chapel of
sorrows, the cellar, the yard store) hold chests.  (Plague Depths = ladder, Broodspiral = spiral, RFK = warren wheel, Wailing = river
ring, Moonwell = twin bowl, Barrows = cross, Grom's Rest = hub + spine; this is the only stepped castle.)

Levels: trash 19-25 ramping with the tiers.  Rethilgore L21, Razorclaw L22, Silverlaine L23, Fenrus L24, Arugal L25.
TRASH IS HAND-PLACED (multi-boss rule): `TRASH` -> zone.trash_spawns, packs of 2-4.

HARD CONTRACTS (world/portal_manager.py): portal (100,172) <-> Silverpine South (48,144); cave exit adds +3 to the destination.
Prop rule (Kyle): less is more; logical for the room; a few centrepieces.
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube, disc

UP = "assets/tiles/undercity/props/"
EKP = "assets/tiles/eastern_kingdoms/props/"
RUINS = "assets/tiles/ruins/"
TIRA = "assets/tiles/tiragarde_keep/props/"
SKULL = "assets/tiles/skull_rock/props/"
CORR = "assets/tiles/ashenvale_corruption/props/"
BAKED = "assets/tiles/shadowfang_keep/baked"
W, H = 200, 180
PORTAL = (100, 172)

# name: (x0, y0, x1, y1, chamfer, display name)
ROOMS = {
    "gate":    (90, 164, 110, 176, 2, "The Gatehouse"),
    "bailey":  (60, 128, 140, 156, 7, "The Outer Bailey"),
    "kennel":  (12, 124, 48, 154, 5, "The Kennels"),
    "yard":    (152, 124, 188, 154, 5, "The Butcher's Yard"),
    "hall":    (54, 78, 146, 112, 6, "The Great Hall"),
    "crypt":   (10, 34, 56, 72, 6, "Fenrus' Crypt"),
    "armory":  (150, 48, 190, 84, 5, "The Armoury"),
    "landing": (62, 32, 142, 50, 4, "The Upper Landing"),
}
PATHS = {
    "gate_pass":   ([(100, 164), (100, 160), (100, 156)], 5.0, 5.0),
    "kennel_door": ([(60, 140), (54, 139), (47, 138)], 4.2, 4.2),
    "yard_door":   ([(140, 140), (146, 139), (153, 138)], 4.2, 4.2),
    "bailey_n":    ([(100, 130), (100, 120), (100, 111)], 5.2, 5.2),
    "w_cloister":  ([(55, 92), (42, 92), (32, 86), (31, 68)], 4.2, 4.2),
    "e_cloister":  ([(145, 92), (160, 93), (170, 90), (171, 83)], 4.2, 4.2),
    "crypt_stair": ([(54, 44), (58, 44), (63, 44)], 4.2, 4.2),
    "arm_stair":   ([(151, 54), (146, 50), (141, 46)], 4.2, 4.2),
    "to_sanctum":  ([(100, 36), (100, 32), (100, 28)], 5.0, 5.0),
    "pens":        ([(22, 125), (19, 114), (17, 106)], 3.4, 3.4),
    "yard_store":  ([(178, 125), (181, 114), (183, 106)], 3.4, 3.4),
    "chapel":      ([(55, 104), (47, 106), (41, 108)], 3.4, 3.4),
    "cellar":      ([(145, 104), (152, 108), (158, 111)], 3.4, 3.4),
}
NOOKS = {                 # (cx, cy, rx, ry, rot, phase, name)
    "pens":    (16, 100, 7, 6, 0, 0.6, "The Hound Pens"),
    "store":   (184, 100, 7, 6, 0, 1.5, "The Yard Store"),
    "chapel":  (35, 109, 8, 7, 0, 2.1, "The Chapel of Sorrows"),
    "cellar":  (165, 113, 8, 7, 0, 0.9, "The Wine Cellar"),
}
SANCTUM = (100, 16, 17, 13, 0, 0.5, "Arugal's Sanctum")
SANCTUM_BAYS = ((76, 15, 8, 7, 0, 1.3), (124, 15, 8, 7, 0, 2.4), (100, 5, 9, 4, 0, 0.8))
BOSSES = {}
CHESTS = []
TRASH = []
LVL = {}


def build_keep():
    zone = Tilemap("Shadowfang Keep", W, H,
                   "Arugal's castle above the Pyrewood road: kennels, a butcher's yard, a hall of the damned and a tower of shadow.")
    zone.is_cave = True
    zone.region = "Silverpine South"
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b
    for key, (x0, y0, x1, y1, ch, _n) in ROOMS.items():
        if key not in ("crypt", "landing", "armory"):
            b.rect(x0, y0, x1, y1, chamfer=ch)
    cavern(b, 33, 53, 24, 19, 12, 0.7)                                   # Fenrus' Crypt: a vaulted undercroft
    cavern(b, 33, 40, 12, 5, 0, 1.9)
    b.rect(150, 48, 190, 68, chamfer=5)                                  # the Armoury is an L: the long rack hall...
    b.rect(168, 68, 190, 92, chamfer=5)                                  # ...and the stores
    disc(b, 100, 76, 14, 0.4)                                            # the Great Hall's apse (the Baron's dais)
    tube(b, [(62, 46), (80, 40), (100, 38), (120, 40), (142, 46)], 9.5, 9.5, ph=1.1)     # the Upper Landing: a bowed gallery
    for (tx, ty) in ((64, 131), (136, 131), (64, 153), (136, 153)):      # corner towers of the bailey
        disc(b, tx, ty, 6, 0.5)
    for i, (key, (pts, w0, w1)) in enumerate(PATHS.items()):
        tube(b, pts, w0, w1, ph=0.3 + i * 0.7)
    for key, (cx, cy, rx, ry, rot, ph, _n) in NOOKS.items():
        cavern(b, cx, cy, rx, ry, rot, ph)
    cx, cy, rx, ry, rot, ph, _n = SANCTUM
    cavern(b, cx, cy, rx, ry, rot, ph)
    for (bx, by, brx, bry, brot, bph) in SANCTUM_BAYS:
        cavern(b, bx, by, brx, bry, brot, bph)
    # the Great Hall's colonnade: two rows of 2x2 columns down both sides, the middle left open
    b.pillars((64, 76, 124, 136), (80, 92, 104))
    px, py = PORTAL
    zone.collision_layer[py][px] = None
    L.mark("portal", px, py)

    bosses = [(28, 136, "Rethilgore"), (170, 136, "Razorclaw the Butcher"), (100, 84, "Baron Silverlaine"),
              (33, 50, "Fenrus the Devourer"), (100, 12, "Archmage Arugal")]
    for (x, y, n) in bosses:
        if not zone.is_walkable(x, y):
            raise AssertionError((n, x, y))
        L.mark("boss_marker", x, y)
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in bosses})
    zone.boss_position = (100, 12)
    zone.boss_positions = list(bosses)
    chests = [(16, 99), (185, 99), (35, 110), (165, 114), (182, 62), (112, 16)]
    for c in chests:
        if not zone.is_walkable(*c):
            raise AssertionError(("chest", c))
        L.mark("chest", *c)
    CHESTS[:] = chests

    zone.add_subzone("Shadowfang Keep", 0, 0, W, H)
    for key, (x0, y0, x1, y1, ch, name) in ROOMS.items():
        zone.add_subzone(name, x0 - 1, y0 - 1, x1 - x0 + 2, y1 - y0 + 2)
    for key, (cx_, cy_, rx_, ry_, rot_, ph_, name) in NOOKS.items():
        zone.add_subzone(name, int(cx_ - rx_ - 2), int(cy_ - ry_ - 2), int(2 * rx_ + 4), int(2 * ry_ + 4))
    zone.add_subzone(SANCTUM[6], 74, 0, 54, 32)
    return zone, L


def finish(zone, L):
    return L.finish([PORTAL] + list(BOSSES.values()) + list(CHESTS))


def dress(zone, L):
    p = L.prop

    def U(name, cx, by, h, **kw):
        return p(name, cx, by, h, where=UP, **kw)

    def E(name, cx, by, h, **kw):
        return p(name, cx, by, h, where=EKP, **kw)

    def R(name, cx, by, h, **kw):
        return p(name, cx, by, h, where=RUINS, **kw)

    def T(name, cx, by, h, **kw):
        return p(name, cx, by, h, where=TIRA, **kw)
    # ---- the Gatehouse and its passage
    R("ruin_tower_skulls", 94, 172, 5, solid="core")
    R("ruin_tower_skulls", 106, 172, 5, solid="core")
    U("uc_portcullis", 100, 161, 6, solid=False, near_ok=True)
    # ---- the Outer Bailey: a dry fountain at the heart, racks and crates against the walls
    E("ek_dry_fountain", 100, 142, 6, solid="core", avoid=1)
    p("weapon_rack", 70, 134, 4, solid="core")
    p("weapon_rack", 130, 134, 4, solid="core")
    T("tiragarde_barrel_crate_cluster", 68, 150, 3, solid="core")
    T("tiragarde_barrel_crate_cluster", 132, 150, 3, solid="core")
    T("tiragarde_rubble_pile", 84, 148, 3)
    T("tiragarde_rubble_pile", 118, 136, 3)
    p("worgen_gargoyle", 93, 131, 5, solid="core")
    p("worgen_gargoyle", 107, 131, 5, solid="core")
    E("ek_forsaken_banner", 80, 132, 5, solid="core")
    E("ek_forsaken_banner", 120, 132, 5, solid="core")
    # ---- the Kennels: cages, a bone heap, the keeper's stool
    p("kennel_cage_empty", 20, 130, 4, solid="core")
    p("kennel_cage_worg", 20, 142, 4, solid="core")
    p("kennel_cage_empty", 40, 148, 4, solid="core")
    p("kennel_cage_worg", 42, 130, 4, solid="core")
    p("bone_pile", 30, 148, 4, where=SKULL, solid="core")
    p("rf_prison_cage", 15, 150, 4, solid="core")
    # ---- the Butcher's Yard: racks, a block, spears, chains
    p("weapon_rack", 160, 130, 4, solid="core")
    p("weapon_rack", 182, 148, 4, solid="core")
    U("uc_operating_table", 170, 144, 4, solid="core")
    p("rf_skull_spears", 158, 148, 4, solid="core")
    p("bbc_chains", 180, 130, 4)
    p("skull_pile", 164, 126, 3, solid="core")
    # ---- the Great Hall: a long banquet table, candelabras, the Baron's chair on the dais
    p("banquet_table", 100, 98, 5, solid="core", avoid=1)
    p("bbc_throne", 100, 74, 8, solid="core", avoid=2)
    p("bbc_banner", 90, 79, 6, solid="core")
    p("bbc_banner", 110, 79, 6, solid="core")
    p("candelabra", 63, 86, 4, solid="core")
    p("candelabra", 137, 86, 4, solid="core")
    p("worgen_gargoyle", 90, 108, 5, solid="core")
    p("worgen_gargoyle", 110, 108, 5, solid="core")
    R("ruin_archway", 100, 112, 4, solid=False, near_ok=True)
    # ---- the West cloister, Fenrus' crypt
    for (px_, py_) in [(22, 46), (44, 46), (20, 62), (46, 62)]:
        p("sarcophagus", px_, py_, 3, solid="core")
    p("skull_pile", 38, 64, 3, solid="core")
    p("bbc_candelabra", 28, 38, 4, solid="core")
    p("bbc_candelabra", 40, 38, 4, solid="core")
    p("ritual_circle", 33, 56, 8, near_ok=True)
    # ---- the Armoury
    for (px_, py_) in [(160, 56), (180, 56), (173, 86), (186, 86)]:
        p("weapon_rack", px_, py_, 4, solid="core")
    p("rf_supply_crates", 181, 76, 3, solid="core")
    T("tiragarde_rubble_pile", 156, 62, 3)
    # ---- the Upper Landing
    p("bbc_banner", 76, 40, 6, solid="core")
    p("bbc_banner", 124, 40, 6, solid="core")
    p("worgen_gargoyle", 94, 38, 5, solid="core")
    p("worgen_gargoyle", 106, 38, 5, solid="core")
    R("ruin_archway", 100, 34, 4, solid=False, near_ok=True)
    # ---- Arugal's Sanctum
    p("ritual_circle", 100, 18, 10, near_ok=True)
    p("bbc_rune_pillar", 86, 22, 6, solid="core")
    p("bbc_rune_pillar", 114, 22, 6, solid="core")
    p("wizard_desk", 76, 18, 4, solid="core")
    p("bbc_candelabra", 90, 6, 4, solid="core")
    p("void_crystal_formation", 124, 18, 3, where=CORR, solid="core")
    p("gothic_gate", 100, 6, 6, solid="core", avoid=3)
    # ---- the nooks: one piece each
    p("kennel_cage_worg", 16, 104, 4, solid="core")
    p("weapon_rack", 184, 104, 4, solid="core")
    p("bbc_altar", 35, 105, 5, solid="core")
    p("bbc_candelabra", 28, 112, 4, solid="core")
    T("tiragarde_barrel_crate_cluster", 165, 118, 3, solid="core")
    place_trash(zone)
    return zone, L


def _near_walkable(zone, x, y, rad=3):
    x, y = int(round(x)), int(round(y))
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            if zone.is_walkable(x + dx, y + dy):
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, x + dx, y + dy)
    return None if best is None else (best[1], best[2])


def place_trash(zone):
    """Hand-placed packs (multi-boss rule).  Levels ramp with the tiers: bailey 19-20 -> wings 21-23 -> crypt/landing 24-25."""
    TRASH.clear()
    occupied = []
    boss_pts = list(BOSSES.values())

    def put(x, y, name, lvl):
        p = _near_walkable(zone, x, y, rad=4)
        if p is None:
            raise AssertionError(f"no floor near ({x},{y}) for {name}")
        for q in occupied:
            if max(abs(p[0] - q[0]), abs(p[1] - q[1])) < 2:
                alt = _near_walkable(zone, p[0] + 2, p[1] + 1, rad=3)
                if alt and all(max(abs(alt[0] - o[0]), abs(alt[1] - o[1])) >= 2 for o in occupied):
                    p = alt
                break
        for (bx, by) in boss_pts:
            if abs(p[0] - bx) <= 5 and abs(p[1] - by) <= 5:
                raise AssertionError(f"{name} too near a boss at {p}")
        occupied.append(p)
        TRASH.append((p[0], p[1], name, lvl))

    def at(cx_, cy_, members, spread=3.0, start=0.0):
        k = len(members)
        for i, (name, lvl) in enumerate(members):
            a = start + 2 * math.pi * i / k
            put(cx_ + spread * math.cos(a), cy_ + spread * 0.8 * math.sin(a), name, lvl)

    Fw_, Fk, Wwar = "Forsaken Warrior", "Forsaken Knight", "Worgen Warrior"
    Kw, Sw, Ww = "Keep Worg", "Slavering Worg", "Wolfguard Worg"
    Mw, Ds, Vw = "Shadowfang Moonwalker", "Shadowfang Darksoul", "Arugal's Voidwalker"
    Hs, To, Wg = "Haunted Servitor", "Tormented Officer", "Wailing Guardsman"
    Dc, Sa, Lh = "Deathsworn Captain", "Son of Arugal", "Lupine Horror"

    # ---- the Gatehouse passage + Outer Bailey (19-20)
    at(100, 158, [(Kw, 19), (Kw, 19), (Wg, 20)], 2.6, 0.3)
    at(78, 142, [(Kw, 19), (Kw, 19), (Wg, 19), (Fw_, 19)], 3.4, 0.3)
    at(122, 142, [(Kw, 20), (Wg, 20), (Wg, 20), (Fw_, 20)], 3.4, 0.8)
    at(88, 134, [(Kw, 20), (Mw, 21), (Wg, 20)], 3.0, 0.5)
    at(113, 152, [(Kw, 20), (Kw, 20), (Mw, 21)], 3.0, 0.2)
    # ---- the Kennels (west, Rethilgore 21): hounds and their keepers (20-21)
    at(40, 140, [(Sw, 20), (Sw, 20), (Kw, 20), (Mw, 21)], 3.4, 0.4)
    at(24, 148, [(Sw, 21), (Kw, 20), (Sw, 21)], 3.0, 0.9)
    at(38, 128, [(Sw, 21), (Sw, 21), (Ds, 21)], 3.0, 0.2)
    at(16, 104, [(Sw, 21), (Kw, 21)], 2.4, 0.6)                     # the hound pens
    # ---- the Butcher's Yard (east, Razorclaw 22): armsmen and guard-hounds (21-22)
    at(159, 142, [(Ww, 21), (Wwar, 21), (Fk, 21), (Sw, 21)], 3.4, 0.3)
    at(182, 142, [(Wwar, 22), (Ww, 22), (Fk, 22), (Wwar, 22)], 3.4, 0.9)
    at(176, 128, [(Wwar, 22), (Ds, 22), (Ww, 21)], 3.0, 0.5)
    at(184, 104, [(Fk, 22), (Wwar, 22)], 2.4, 0.4)                  # the yard store
    # ---- the pass up to the Great Hall
    at(100, 120, [(Wg, 22), (To, 22), (Wg, 22)], 2.8, 0.5)
    # ---- the Great Hall (Silverlaine 23): the damned at their banquet (22-23)
    at(72, 96, [(To, 22), (Hs, 22), (Hs, 22), (Wg, 22)], 3.6, 0.3)
    at(128, 96, [(To, 23), (Hs, 22), (Hs, 23), (Wg, 22)], 3.6, 0.8)
    at(80, 106, [(Hs, 22), (Hs, 22), (To, 22)], 3.0, 0.2)
    at(120, 106, [(Hs, 23), (To, 23), (Hs, 23)], 3.0, 0.7)
    at(70, 84, [(Ds, 22), (To, 22), (Hs, 23)], 3.0, 0.4)
    at(130, 84, [(Mw, 22), (To, 23), (Hs, 23)], 3.0, 0.9)
    at(35, 108, [(Hs, 22), (Wg, 22)], 2.4, 0.5)                     # the chapel of sorrows
    at(165, 112, [(Hs, 23), (To, 23)], 2.4, 0.2)                    # the wine cellar
    # ---- the haunted west cloister and Fenrus' crypt (22-24)
    at(44, 92, [(Wg, 22), (Hs, 22), (Wg, 22)], 2.8, 0.4)
    at(33, 80, [(To, 23), (Hs, 23), (Ds, 23)], 2.8, 0.9)
    at(19, 58, [(Sa, 23), (Sa, 23), (Ds, 23), (Sa, 23)], 3.4, 0.3)
    at(47, 58, [(Sa, 24), (Lh, 24), (Sa, 24)], 3.2, 0.8)
    at(26, 66, [(Sa, 23), (Ds, 24), (Sa, 24)], 3.0, 0.5)
    at(33, 40, [(Lh, 24), (Sa, 24), (Ds, 24)], 3.0, 0.2)
    # ---- the armoury passage and the Armoury (22-24)
    at(158, 93, [(Dc, 23), (Fk, 22), (Fk, 22)], 2.8, 0.5)
    at(171, 86, [(Wwar, 23), (Dc, 23), (Wwar, 23)], 2.8, 0.2)
    at(160, 58, [(Dc, 23), (Fk, 23), (Fk, 23), (Wwar, 23)], 3.4, 0.4)
    at(181, 58, [(Dc, 24), (Fk, 23), (Fk, 24), (Dc, 24)], 3.4, 0.9)
    at(178, 78, [(Dc, 23), (Wwar, 24), (Fk, 23)], 3.0, 0.6)
    # ---- the Upper Landing (24-25)
    at(76, 42, [(Vw, 24), (Ds, 24), (Mw, 24), (To, 24)], 3.4, 0.3)
    at(124, 42, [(Vw, 24), (Dc, 24), (Ds, 24), (To, 24)], 3.4, 0.8)
    at(100, 40, [(Vw, 24), (Vw, 24), (Hs, 24)], 3.0, 0.5)
    # ---- Arugal's Sanctum (25): his servants
    at(82, 20, [(Vw, 25), (Ds, 25)], 2.6, 0.4)
    at(118, 21, [(Vw, 25), (Ds, 25)], 2.6, 0.9)
    zone.trash_spawns = list(TRASH)


def generate_shadowfang_keep():
    zone, L = build_keep()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_keep_baked():
    zone, L = build_keep()
    dress(zone, L)
    finish(zone, L)
    return zone, L


if __name__ == "__main__":
    import sys
    from PIL import Image
    zone, L = build_keep_baked()
    im = Image.new("RGB", (W, H), (30, 28, 34))
    for y in range(H):
        for x in range(W):
            if zone.is_walkable(x, y):
                im.putpixel((x, y), (120, 150, 110))
    for (x, y) in BOSSES.values():
        im.putpixel((x, y), (255, 60, 60))
    for (x, y) in CHESTS:
        im.putpixel((x, y), (255, 220, 60))
    im.putpixel(PORTAL, (255, 0, 255))
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/sfk_shape.png"
    im.resize((W * 4, H * 4), Image.NEAREST).save(out)
    print(out, "skipped", list(L.skipped))
