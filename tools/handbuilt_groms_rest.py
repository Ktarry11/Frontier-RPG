"""
Hand-built Grom's Rest (240x220): the felled-forest throne of the demons beneath Ashenvale East.  SIX BOSSES (Kyle's first
home-brew dungeon idea, kept as he drew it).

ARCHETYPE: THE THRONE ASCENT (hub + two wings + a gated spine).  One DEMON TOTEM HALL (the hub) sits behind the Ashen Gate.
Two OPTIONAL wings bud off it east and west (no gates, genuinely skippable):
    W  Satyr's Ritual Hall  - Satyr Warlord          E  Void Gathering - Void Handmaiden
A single corridor leaves the hub's north edge and climbs a MANDATORY CHAIN where every chamber's only way on is the next one
(no shortcuts, nothing connects back to the hub; the tubes are single-width on purpose):
    Doomguard's Approach (fel pools)   - Doomguard Sentinel
 -> The Corrupted Grove                - Corrupted Ancient
 -> The Bone Hall                      - Felguard Overseer
 -> The Inner Sanctum                  - Lord Nightmare (the eldritch horror, final boss)
Dead-end nooks off the hub hold chests.  (Broodspiral = spiral, RFK = warren wheel, Wailing = river ring, Moonwell = twin
bowl, Barrows = cross; this is the only hub-and-spine.)

Levels: trash 26-30 ramping with depth; bosses Warlord 28, Handmaiden 29, Sentinel 29, Ancient 30, Overseer 31, Nightmare 32.
TRASH IS HAND-PLACED (multi-boss rule, claude/dungeon_authoring_rules.md): `TRASH` -> zone.trash_spawns, packs of 3-4.

HARD CONTRACTS (world/portal_manager.py): portal (120,205) <-> Ashenvale East (165,175); arrival = 2 north.
Prop rule (Kyle): less is more; logical for the room; a few centrepieces.
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked, _apply_pools  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

BAKED = "assets/tiles/groms_rest/baked"
W, H = 240, 220
PORTAL = (120, 205)

PATHS = {
    "approach": ([(120, 199), (116, 190), (122, 180), (120, 172)], 6.0, 6.5),
    "west":     ([(90, 150), (76, 152), (64, 148)], 4.8, 4.8),
    "east":     ([(150, 150), (164, 152), (176, 148)], 4.8, 4.8),
    "spine_a":  ([(120, 133), (123, 126), (120, 119)], 4.6, 4.6),        # hub -> Doomguard (the only way on)
    "spine_b":  ([(120, 94), (116, 86), (120, 78)], 4.6, 4.6),           # Doomguard -> Grove
    "spine_c":  ([(120, 54), (123, 51), (120, 48)], 4.6, 4.6),           # Grove -> Bone Hall
    "spine_d":  ([(120, 28), (118, 25), (120, 22)], 4.6, 4.6),           # Bone Hall -> Sanctum
    "nook_sw":  ([(96, 164), (86, 172), (80, 178)], 3.2, 3.2),
    "nook_se":  ([(144, 164), (154, 172), (160, 178)], 3.2, 3.2),
    "nook_w":   ([(30, 138), (24, 128), (22, 122)], 3.0, 3.0),           # off the Satyr hall
    "nook_e":   ([(210, 138), (216, 128), (218, 122)], 3.0, 3.0),        # off the Void Gathering
}
ROOMS = {
    "gate":     (120, 206, 14, 6, 0, 0.4, "The Ashen Gate"),
    "hub":      (120, 152, 33, 20, 0, 1.0, "The Demon Totem Hall"),
    "satyr":    (40, 146, 22, 16, 0, 2.0, "Satyr's Ritual Hall"),
    "void":     (200, 146, 22, 16, 0, 0.6, "Void Gathering"),
    "doom":     (120, 106, 21, 13, 0, 1.7, "Doomguard's Approach"),
    "grove":    (120, 66, 19, 12, 0, 2.6, "The Corrupted Grove"),
    "bone":     (120, 38, 19, 10, 0, 0.9, "The Bone Hall"),
    "sanctum":  (120, 14, 30, 9, 0, 1.4, "The Inner Sanctum"),
    "nook_sw":  (77, 181, 7, 5, 0, 0.8, "The Imp Larder"),
    "nook_se":  (163, 181, 7, 5, 0, 2.3, "The Felhound Kennel"),
    "nook_w":   (20, 118, 6, 5, 0, 1.2, "The Satyr Cache"),
    "nook_e":   (220, 118, 6, 5, 0, 2.0, "The Void Cache"),
}
# shallow fel pools (walkable, painted as fel water): (cx, cy, rx, ry, phase) - Doomguard's Approach
GR_POOLS = [
    (107, 106, 5.5, 3.8, 0.4), (133, 107, 5.5, 3.8, 1.3), (120, 98, 4.0, 2.6, 2.2),
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


def build_groms():
    zone = Tilemap("Grom's Rest", W, H,
                   "Where the forest fell, the demons found a home. And Grom's Rest became their throne.")
    zone.is_cave = True
    zone.region = "Ashenvale East"
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b

    for i, (key, (pts, w0, w1)) in enumerate(PATHS.items()):
        tube(b, pts, w0, w1, ph=0.5 + i * 0.9)
    for key, (cx, cy, rx, ry, rot, ph, _n) in ROOMS.items():
        cavern(b, cx, cy, rx, ry, rot, ph)
    # join each tube end into its room (short plugs; the spine ones are single-width on purpose)
    for pts in (((120, 199), (120, 202)), ((120, 172), (120, 168)), ((92, 150), (96, 150)), ((64, 148), (60, 147)),
                ((148, 150), (144, 150)), ((176, 148), (180, 147)), ((120, 133), (120, 137)), ((120, 119), (120, 117)),
                ((120, 94), (120, 96)), ((120, 78), (120, 76)), ((120, 54), (120, 56)), ((120, 48), (120, 46)),
                ((120, 28), (120, 30)), ((120, 22), (120, 20)), ((96, 164), (98, 163)), ((80, 178), (78, 180)),
                ((144, 164), (142, 163)), ((160, 178), (162, 180)), ((30, 138), (32, 140)), ((22, 122), (21, 121)),
                ((210, 138), (208, 140)), ((218, 122), (219, 121))):
        tube(b, list(pts), 4.0, 4.0)

    _apply_pools(zone, GR_POOLS, shallow_only=True)

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    bosses = [
        (40, 142, "Satyr Warlord"), (200, 142, "Void Handmaiden"), (120, 100, "Doomguard Sentinel"),
        (120, 62, "Corrupted Ancient"), (120, 35, "Felguard Overseer"), (120, 11, "Lord Nightmare"),
    ]
    fixed = []
    for (x, y, n) in bosses:
        p = _near_walkable(zone, x, y)
        assert p, (n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (fixed[5][0], fixed[5][1])          # Lord Nightmare is the final boss
    zone.boss_positions = list(fixed)

    chests = []
    for (x, y) in ((74, 183), (166, 183), (19, 118), (221, 118), (60, 140), (140, 140), (131, 58), (131, 40), (108, 12)):
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        chests.append(p)
    CHESTS[:] = chests
    for c in chests:
        L.mark("chest", *c)

    def sub(name, x, y, rx, ry):
        zone.add_subzone(name, int(x - rx), int(y - ry), int(2 * rx), int(2 * ry))
    zone.add_subzone("Grom's Rest", 0, 0, W, H)           # whole-map cave-table key first; named rooms re-register after
    for key, (cx, cy, rx, ry, rot, ph, name) in ROOMS.items():
        sub(name, cx, cy, rx + 2, ry + 2)
    return zone, L


def finish(zone, L):
    targets = [PORTAL] + [(x, y) for (x, y) in BOSSES.values()] + list(CHESTS)
    return L.finish(targets)


def dress(zone, L):
    from tools.ashenvale_town_kit import INDEX

    def P(name, cx, by, h, **kw):
        kw.setdefault("where", INDEX.get(name, DP))
        return L.prop(name, cx, by, h, **kw)
    R = ROOMS
    # ---- the Ashen Gate: obsidian spires and fel braziers flank the way in
    P("ashx_obsidian_spires", 108, 205, 6, solid="core")
    P("ashx_obsidian_spires", 131, 207, 6, solid="core")
    P("bbc_fel_brazier", 113, 200, 4, solid="core")
    P("bbc_fel_brazier", 128, 202, 4, solid="core")
    # ---- the Demon Totem Hall (hub): the skull altar is the centrepiece
    hx, hy = R["hub"][:2]
    P("ritual_circle", hx, hy + 2, 8, solid=False, near_ok=True, avoid=0)
    P("ashx_demon_skull_altar", hx, hy - 2, 8, solid="core", avoid=1)
    P("bbc_fel_brazier", hx - 18, hy - 8, 4, solid="core")
    P("bbc_fel_brazier", hx + 18, hy - 8, 4, solid="core")
    P("bbc_fel_brazier", hx - 18, hy + 9, 4, solid="core")
    P("bbc_fel_brazier", hx + 18, hy + 9, 4, solid="core")
    P("bbc_banner", hx - 10, hy - 14, 6, solid="core")
    P("bbc_banner", hx + 10, hy - 14, 6, solid="core")
    P("skull_pile", hx - 24, hy + 3, 3)
    P("bbc_chains", hx + 25, hy + 2, 5, solid="core")
    # ---- nooks: one small centrepiece each
    P("ashx_demon_egg", R["nook_sw"][0] + 1, R["nook_sw"][1] + 2, 3)
    P("kennel_cage_worg", R["nook_se"][0] - 3, R["nook_se"][1] + 2, 4, solid="core")
    P("ashx_satyr_weapon_rack", R["nook_w"][0] + 3, R["nook_w"][1], 4, solid="core")
    P("void_crystal_formation", R["nook_e"][0] - 3, R["nook_e"][1], 4, solid="core")
    # ---- Satyr's Ritual Hall: a throne, weapon racks, a ritual ring
    sx, sy = R["satyr"][:2]
    P("ritual_circle", sx, sy + 3, 7, solid=False, near_ok=True, avoid=0)
    P("satyr_throne", sx, sy - 10, 7, solid="core", avoid=1)
    P("ashx_satyr_weapon_rack", sx - 12, sy - 4, 4, solid="core")
    P("ashx_satyr_weapon_rack", sx + 12, sy - 4, 4, solid="core")
    P("fel_fire_brazier", sx - 14, sy + 6, 4, solid="core")
    P("fel_fire_brazier", sx + 14, sy + 6, 4, solid="core")
    P("skull_pile", sx + 8, sy + 9, 3)
    # ---- Void Gathering: crystals and a twilight altar
    vx, vy = R["void"][:2]
    P("twilight_altar", vx, vy - 9, 6, solid="core", avoid=1)
    P("void_crystal_formation", vx - 13, vy - 3, 5, solid="core")
    P("void_crystal_formation", vx + 13, vy - 3, 5, solid="core")
    P("rf_void_crystals", vx - 10, vy + 8, 4, solid="core")
    P("rf_void_crystals", vx + 10, vy + 8, 4, solid="core")
    P("ritual_circle", vx, vy + 2, 7, solid=False, near_ok=True, avoid=0)
    # ---- Doomguard's Approach: fel pools, a ribcage, pylons, chains
    dx, dy = R["doom"][:2]
    P("bbc_fel_pylon", dx - 15, dy - 6, 5, solid="core")
    P("bbc_fel_pylon", dx + 15, dy - 6, 5, solid="core")
    P("ashx_demon_ribcage", dx - 14, dy + 7, 4, solid="core")
    P("bbc_obsidian_spikes", dx + 14, dy + 7, 4, solid="core")
    P("bbc_chains", dx + 6, dy - 9, 5, solid="core")
    # ---- the Corrupted Grove: the great corrupted tree and its root pillars
    gx, gy = R["grove"][:2]
    P("ashx_corrupt_ancient_tree", gx, gy - 8, 11, solid="core", avoid=1)
    P("ashx_nightmare_root_pillar", gx - 13, gy - 3, 6, solid="core")
    P("ashx_nightmare_root_pillar", gx + 13, gy - 3, 6, solid="core")
    P("dead_corrupted_tree", gx - 10, gy + 7, 6, solid="core")
    P("dead_corrupted_tree", gx + 10, gy + 7, 6, solid="core")
    P("ashx_demon_egg", gx + 4, gy + 8, 3)
    # ---- the Bone Hall: ribcages, skull heaps, rune pillars
    bx, by = R["bone"][:2]
    P("ashx_demon_ribcage", bx - 12, by - 4, 5, solid="core")
    P("ashx_demon_ribcage", bx + 12, by - 4, 5, solid="core")
    P("bbc_rune_pillar", bx - 8, by + 5, 6, solid="core")
    P("bbc_rune_pillar", bx + 8, by + 5, 6, solid="core")
    P("skull_pile", bx - 5, by - 7, 3)
    P("skull_pile", bx + 14, by + 6, 3)
    P("ashx_skull_fence", bx, by - 8, 5, solid="core")
    # ---- the Inner Sanctum: a throne under the void, rune pillars, braziers
    nx, ny = R["sanctum"][:2]
    P("bbc_throne", nx, ny - 6, 8, solid="core", avoid=1)
    P("ritual_circle", nx, ny + 2, 10, solid=False, near_ok=True, avoid=0)
    for ox in (-18, -9, 9, 18):
        P("bbc_rune_pillar", nx + ox, ny + (3 if abs(ox) > 10 else 5), 7, solid="core")
    P("void_crystal_formation", nx - 24, ny - 2, 5, solid="core")
    P("void_crystal_formation", nx + 24, ny - 2, 5, solid="core")
    P("bbc_fel_brazier", nx - 6, ny - 3, 4, solid="core")
    P("bbc_fel_brazier", nx + 6, ny - 3, 4, solid="core")

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

    def at(cx_, cy_, members, spread=3.2, start=0.0):
        k = len(members)
        for i, (name, lvl) in enumerate(members):
            a = start + 2 * math.pi * i / k
            put(cx_ + spread * math.cos(a), cy_ + spread * 0.8 * math.sin(a), name, lvl)

    Sc, Di, Fh, Vc = "Satyr Cultist", "Dread Imp", "Corrupted Felhound", "Corrupted Void Construct"
    Fl, Dw, Tr, Rv = "Felguard Legionnaire", "Doomguard Warden", "Corrupted Treant", "Buried Revenant"

    # ---- the Ashen Gate + approach (26)
    pack("approach", 0.28, [(Fh, 26), (Fh, 26), (Di, 26)], lateral=1.6)
    pack("approach", 0.72, [(Sc, 26), (Di, 26), (Sc, 26)], lateral=1.8)
    # ---- the Demon Totem Hall (26-27): four packs around the altar
    at(hx - 17, hy - 2, [(Sc, 26), (Sc, 26), (Di, 26), (Fh, 26)], spread=3.4, start=0.4)
    at(hx + 17, hy - 2, [(Vc, 27), (Vc, 27), (Di, 26)], spread=3.2, start=1.0)
    at(hx - 9, hy + 11, [(Fh, 26), (Fh, 27), (Sc, 27), (Di, 27)], spread=3.4, start=0.2)
    at(hx + 9, hy + 11, [(Fl, 27), (Sc, 27), (Sc, 27)], spread=3.2, start=0.9)
    # ---- optional west wing: Satyr's Ritual Hall (27-28)
    pack("west", 0.5, [(Sc, 27), (Di, 27), (Sc, 27)], lateral=1.6)
    at(sx - 9, sy + 1, [(Sc, 28), (Sc, 28), (Sc, 28), (Di, 28)], spread=3.4, start=0.3)
    at(sx + 9, sy + 1, [(Fh, 28), (Fh, 28), (Sc, 28), (Sc, 28)], spread=3.4, start=0.8)
    at(sx, sy + 8, [(Sc, 28), (Di, 28), (Di, 28)], spread=3.0, start=0.5)
    pack("nook_sw", 0.5, [(Di, 27), (Di, 27), (Fh, 27)], lateral=1.4)
    pack("nook_w", 0.55, [(Sc, 28), (Sc, 28)], lateral=1.4)
    # ---- optional east wing: Void Gathering (27-28)
    pack("east", 0.5, [(Vc, 27), (Di, 27), (Vc, 27)], lateral=1.6)
    at(vx - 9, vy + 1, [(Vc, 28), (Vc, 28), (Sc, 28), (Di, 28)], spread=3.4, start=0.3)
    at(vx + 9, vy + 1, [(Vc, 28), (Vc, 28), (Di, 28), (Di, 28)], spread=3.4, start=0.8)
    at(vx, vy + 9, [(Fh, 28), (Vc, 28), (Vc, 28)], spread=3.0, start=0.5)
    pack("nook_se", 0.5, [(Fh, 27), (Fh, 27), (Fh, 27)], lateral=1.4)
    pack("nook_e", 0.55, [(Vc, 28), (Vc, 28)], lateral=1.4)
    # ---- the spine (28-30): single-width tubes, a pack in each
    pack("spine_a", 0.5, [(Fl, 28), (Dw, 28), (Fl, 28)], lateral=1.3)
    at(dx - 10, dy + 2, [(Dw, 28), (Dw, 28), (Fl, 28), (Fh, 28)], spread=3.2, start=0.2)
    at(dx + 10, dy + 2, [(Fl, 29), (Fl, 29), (Dw, 29)], spread=3.0, start=0.7)
    at(dx, dy + 8, [(Fh, 29), (Fh, 29), (Di, 29), (Di, 29)], spread=3.4, start=0.4)
    pack("spine_b", 0.5, [(Dw, 29), (Di, 29), (Dw, 29)], lateral=1.3)
    at(gx - 9, gy + 3, [(Tr, 29), (Tr, 29), (Tr, 29), (Sc, 29)], spread=3.4, start=0.3)
    at(gx + 9, gy + 3, [(Tr, 30), (Tr, 30), (Di, 30), (Di, 30)], spread=3.4, start=0.9)
    at(gx, gy + 8, [(Tr, 30), (Sc, 30), (Sc, 30)], spread=3.0, start=0.6)
    pack("spine_c", 0.5, [(Tr, 30), (Fh, 30), (Tr, 30)], lateral=1.3)
    at(bx - 9, by + 2, [(Rv, 30), (Rv, 30), (Rv, 30), (Fl, 30)], spread=3.4, start=0.3)
    at(bx + 9, by + 2, [(Rv, 30), (Fl, 30), (Fl, 30), (Rv, 30)], spread=3.4, start=0.8)
    at(bx, by + 7, [(Rv, 30), (Rv, 30), (Dw, 30)], spread=3.0, start=0.5)
    pack("spine_d", 0.5, [(Fl, 30), (Rv, 30), (Fl, 30)], lateral=1.3)
    at(nx - 14, ny + 2, [(Vc, 30), (Vc, 30), (Sc, 30), (Sc, 30)], spread=3.4, start=0.2)
    at(nx + 14, ny + 2, [(Vc, 30), (Vc, 30), (Sc, 30), (Sc, 30)], spread=3.4, start=0.9)
    at(nx, ny + 6, [(Fl, 30), (Fl, 30), (Fl, 30)], spread=3.0, start=0.5)
    zone.trash_spawns = list(TRASH)
    return zone, L


def generate_groms_rest():
    zone, L = build_groms()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_groms_baked():
    """(zone, layout) with props + QA done - what the baker paints from."""
    zone, L = build_groms()
    dress(zone, L)
    finish(zone, L)
    return zone, L
