"""
Hand-built Broodspiral (240x240): the silithid hive that spirals down into the earth under the Southern Barrens.

ARCHETYPE: THE SPIRAL (Kyle: "keep the spiral look").  The original design is kept exactly - an Archimedean
corridor r = 15 + 6.5*theta winding 2.2 turns inward from the entrance (152,220) to the Queen's Hollow at the
centre (120,120), same boss stations, same room names, same hive/resin/larval/queen art - but drawn as living
tunnel: breathing width, a wobbling centreline, organic rotated chambers instead of rectangles, and radial
NURSERIES (dead-end side chambers in the rock between the arms) that hold the named rares and the chests.

  Carapace Warden     L19  outer ring   (1.5 turns out, west side)         Outer Ring
  The Broodkeeper     L21  mid ring     (0.8 turns out, north side)        Brood Chamber
  Larval Broodguard   L22  the screen   (0.35 turns out, south-west)      Larval Screen
  Broodspiral Queen   L24  dead centre                                     Queen's Hollow
  rares (pinned in nurseries): Mother Amberwing L20, Gnash the Hollow-Maw L22, Chitterlord Skrix L23

TRASH IS HAND-PLACED (Kyle: multi-boss dungeons place their trash room by room; caves/keeps use random rolls).
`TRASH` below becomes zone.trash_spawns (world/cave_spawns.py) - no respawns until you leave and re-enter, levels
ramp with depth.  `fixed_spawns` stays True (a real dungeon).

HARD CONTRACTS (world/portal_manager.py): portal (152,220) <-> Southern Barrens (225,220); arrival = 2 north.
Prop rule (Kyle): less is more; props logical for the room; a few centrepieces.
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

BP = "assets/tiles/broodspiral/props/"
BAKED = "assets/tiles/broodspiral/baked"
W = H = 240
CX, CY = 120, 120
A, B = 15.0, 6.5
TURNS = 2.2
TH_MAX = TURNS * 2 * math.pi
PORTAL = (152, 220)


def sp(theta, wob=True):
    """Spiral centreline point, with a slow radial wobble so the arms breathe."""
    r = A + B * theta
    off = (1.3 * math.sin(2.7 * theta + 0.4) + 0.7 * math.sin(6.1 * theta + 1.3)) if wob else 0.0
    r += off
    return (CX + r * math.cos(theta), CY + r * math.sin(theta))


def rot_deg(theta):
    return math.degrees(theta) + 90.0           # tangent direction


def radial(theta, dist):
    """Point `dist` tiles outward (+) / inward (-) of the arm at theta."""
    x, y = sp(theta)
    return (x + dist * math.cos(theta), y + dist * math.sin(theta))


# ---- stations (theta, same radii as the original dungeon) ----------------------------------------------
TH_WARDEN = 1.5 * 2 * math.pi
TH_KEEPER = 0.8 * 2 * math.pi
TH_GUARD = 0.35 * 2 * math.pi

# ---- nurseries: (key, theta on the arm, side +1 out/-1 in, distance, tangential r, radial r, phase, rot offset)
NOOKS = {
    "amberwing": dict(theta=11.2, side=-1, dist=20, rt=10, rr=6.5, ph=0.7, name="Amberwing's Nursery"),
    "gnash":     dict(theta=7.1, side=-1, dist=20, rt=11, rr=7.0, ph=1.9, name="The Hollow-Maw Pit"),
    "skrix":     dict(theta=3.4, side=+1, dist=20, rt=10, rr=6.5, ph=2.6, name="Skrix's Roost"),
    "eggs":      dict(theta=12.9, side=-1, dist=20, rt=9, rr=6.0, ph=3.3, name="The Egg Chamber"),
}

BOSSES = {}          # filled by build
CHESTS = []
TRASH = []           # filled by build (hand-placed packs)


def _near_walkable(zone, x, y, rad=4):
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            if zone.is_walkable(int(x) + dx, int(y) + dy):
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, int(x) + dx, int(y) + dy)
    return None if best is None else (best[1], best[2])


def build_broodspiral():
    zone = Tilemap("The Broodspiral", W, H,
                   "A silithid hive spiraling down into the earth south of the quilboar lands. "
                   "Something ancient wakes at its center.")
    zone.is_cave = True
    zone.region = "Southern Barrens"
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b

    # ------------------------------------------------------------ the spiral tunnel
    pts, th = [], TH_MAX
    while th > 0.05:
        pts.append(sp(th))
        th -= 0.14
    pts.append(sp(0.05))
    pts = [(round(x, 1), round(y, 1)) for (x, y) in pts]
    tube(b, pts, 5.6, 4.6, ph=0.6)

    # entrance chamber: the hive mouth
    cavern(b, 152, 215, 11, 7.5, -12, 0.4)

    # ------------------------------------------------------------ boss chambers (organic, rotated along the arm)
    wx, wy = sp(TH_WARDEN)
    cavern(b, wx, wy, 15, 11.5, rot_deg(TH_WARDEN), 0.9)                  # Carapace Warden's hall
    kx, ky = sp(TH_KEEPER)
    cavern(b, kx, ky, 15.5, 12, rot_deg(TH_KEEPER), 1.6)                  # The Broodkeeper's brood chamber
    gx, gy = sp(TH_GUARD)
    cavern(b, gx, gy, 14, 10.5, rot_deg(TH_GUARD), 2.3)                   # the Larval Screen
    cavern(b, CX, CY, 17.5, 16, 0, 0.5)                                   # the Queen's Hollow

    # ------------------------------------------------------------ nurseries (radial side chambers)
    nook_pos = {}
    for key, n in NOOKS.items():
        ax, ay = sp(n["theta"])
        nx, ny = radial(n["theta"], n["side"] * n["dist"])
        cavern(b, nx, ny, n["rt"], n["rr"], rot_deg(n["theta"]), n["ph"])
        tube(b, [(ax, ay), ((ax + nx) / 2 + 0.8, (ay + ny) / 2 - 0.8), (nx, ny)], 3.6, 3.6, ph=n["ph"])
        nook_pos[key] = (round(nx), round(ny))

    # ------------------------------------------------------------ markers
    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    bosses = [
        (round(wx), round(wy) - 2, "Carapace Warden"),
        (round(kx), round(ky) - 2, "The Broodkeeper"),
        (round(gx), round(gy) - 2, "Larval Broodguard"),
        (CX, CY - 3, "Broodspiral Queen"),
        (nook_pos["amberwing"][0], nook_pos["amberwing"][1], "Mother Amberwing"),
        (nook_pos["gnash"][0], nook_pos["gnash"][1], "Gnash the Hollow-Maw"),
        (nook_pos["skrix"][0], nook_pos["skrix"][1], "Chitterlord Skrix"),
    ]
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
    for key, dx, dy in (("amberwing", 4, 2), ("gnash", -5, 3), ("skrix", 4, 2), ("eggs", 0, 1)):
        x, y = nook_pos[key]
        p = _near_walkable(zone, x + dx, y + dy)
        assert p, key
        chests.append(p)
    p = _near_walkable(zone, CX + 10, CY + 8)
    chests.append(p)
    CHESTS[:] = chests
    for c in chests:
        L.mark("chest", *c)

    # ------------------------------------------------------------ subzones (display names, original ones kept)
    def sub(name, x, y, rx, ry):
        zone.add_subzone(name, int(x - rx), int(y - ry), int(2 * rx), int(2 * ry))
    sub("The Outer Ring", wx, wy, 16, 13)
    sub("The Brood Chamber", kx, ky, 17, 14)
    sub("The Larval Screen", gx, gy, 15, 12)
    sub("The Queen's Hollow", CX, CY, 19, 17)
    for key, n in NOOKS.items():
        x, y = nook_pos[key]
        sub(n["name"], x, y, n["rt"] + 2, n["rr"] + 2)

    # ------------------------------------------------------------ props: eggs where eggs belong, a few centrepieces
    P = L.prop
    # outer ring: the Warden's hall is an egg-guard post
    P("egg_sac_cluster", int(wx) - 5, int(wy) + 6, 5, where=BP)
    P("carapace_pile", int(wx) + 6, int(wy) - 5, 4, where=BP)
    P("den_chitin_husk", int(wx) - 9, int(wy) - 3, 3)
    P("den_eggshell_pile", int(wx) + 3, int(wy) + 8, 2)
    # mid ring: the Broodkeeper's brood chamber - resin pillars flank its dais
    P("resin_pillar", int(kx) - 7, int(ky) - 5, 6, where=BP, solid="core")
    P("resin_pillar", int(kx) + 7, int(ky) - 5, 6, where=BP, solid="core")
    P("den_nest_mound", int(kx) - 5, int(ky) + 6, 4)
    P("den_nest_mound", int(kx) + 6, int(ky) + 6, 4)
    P("den_egg_cluster", int(kx), int(ky) + 8, 3)
    # larval screen: husks and a carapace heap
    P("carapace_pile", int(gx) - 6, int(gy) + 4, 4, where=BP)
    P("den_chitin_husk", int(gx) + 6, int(gy) + 3, 3)
    P("den_eggshell_pile", int(gx) + 1, int(gy) + 8, 2)
    P("den_leg_bones", int(gx) - 2, int(gy) - 7, 2)
    # queen's hollow: the throne and a ring of pillars
    P("queens_throne", CX, CY - 8, 8, where=BP, solid="core", avoid=1)
    for a in (35, 85, 145, 215, 275, 325):
        P("resin_pillar", round(CX + 13 * math.cos(math.radians(a))), round(CY + 11 * math.sin(math.radians(a))) + 3, 6,
          where=BP, solid="core")
    P("den_nest_mound", CX - 4, CY + 11, 4)
    P("den_nest_mound", CX + 9, CY + 5, 4)
    P("den_egg_cluster", CX + 2, CY + 9, 3)
    # nurseries
    ax, ay = nook_pos["amberwing"]
    P("egg_sac_cluster", ax - 3, ay + 3, 5, where=BP)
    P("den_egg_cluster", ax + 6, ay - 2, 3)
    P("den_web_cocoon", ax - 6, ay - 2, 3)
    gx2, gy2 = nook_pos["gnash"]
    P("den_burrow_hole", gx2 + 4, gy2 + 3, 3)
    P("den_leg_bones", gx2 - 5, gy2 - 2, 2)
    P("carapace_pile", gx2 - 6, gy2 + 4, 4, where=BP)
    P("den_stalagmites", gx2 + 8, gy2 - 3, 3)
    sx, sy = nook_pos["skrix"]
    P("resin_pillar", sx - 5, sy - 3, 6, where=BP, solid="core")
    P("den_web_boulder", sx + 6, sy + 3, 3)
    P("den_glow_mushrooms", sx - 3, sy + 4, 2)
    ex, ey = nook_pos["eggs"]
    P("egg_sac_cluster", ex - 3, ey + 2, 5, where=BP)
    P("den_egg_cluster", ex + 4, ey + 3, 3)
    P("den_egg_cluster", ex - 6, ey - 1, 3)
    P("den_eggshell_pile", ex + 2, ey - 3, 2)
    # entrance: a few husks of the unlucky
    P("den_dead_recruit", 146, 213, 3)
    P("den_chitin_husk", 158, 211, 3)
    P("den_torch", 143, 218, 4)
    # sparse corridor dressing (logical: glow-mushrooms and husks on the arms)
    for th_, k in ((12.4, 0), (10.9, 1), (9.0, 2), (7.7, 0), (6.4, 1), (4.7, 2), (3.7, 0), (2.9, 1), (1.4, 2), (0.9, 0)):
        x, y = sp(th_)
        name = ("den_glow_mushrooms", "den_chitin_husk", "den_leg_bones")[k]
        P(name, round(x) + 2, round(y) + 2, 2 if name != "den_chitin_husk" else 3)

    # ------------------------------------------------------------ HAND-PLACED TRASH (room by room, depth ramps level)
    def pack(theta, members, lateral=1.4):
        """Members stand side by side across the tunnel at `theta` (name, level)."""
        x0, y0 = sp(theta, wob=True)
        tx, ty = -math.sin(theta), math.cos(theta)          # tangent
        nx_, ny_ = math.cos(theta), math.sin(theta)         # radial
        for i, (name, lvl) in enumerate(members):
            lat = (i - (len(members) - 1) / 2.0) * lateral * 1.7
            along = (i % 2) * 1.6 - 0.8
            p = _near_walkable(zone, x0 + nx_ * lat + tx * along, y0 + ny_ * lat + ty * along, rad=3)
            if p is None:
                raise AssertionError(f"pack at theta={theta}: no floor for {name}")
            if any(max(abs(p[0] - q[0]), abs(p[1] - q[1])) < 2 for q in [(t[0], t[1]) for t in TRASH]):
                p = _near_walkable(zone, p[0] + 2, p[1] + 2, rad=3) or p
            TRASH.append((p[0], p[1], name, lvl))

    def room_pack(cx_, cy_, members, spread=5.0, start=0.0):
        n = len(members)
        for i, (name, lvl) in enumerate(members):
            a = start + 2 * math.pi * i / n
            p = _near_walkable(zone, cx_ + spread * math.cos(a), cy_ + spread * math.sin(a), rad=3)
            if p is None:
                raise AssertionError(f"room pack at {cx_},{cy_}: no floor for {name}")
            TRASH.append((p[0], p[1], name, lvl))

    TRASH.clear()
    G, D, K, Sk, St = "Silithid Guardian", "Hive Drone", "Brood Tender", "Hive Skulker", "Silithid Stinger"
    Sp, Cr, Lv, Wv, Se = "Resin Spitter", "Carapace Crusher", "Gorged Larva", "Hive Weaver", "Amber Sentinel"
    # ---- outer ring (18-19): drones and guardians, the hive's rank and file
    pack(13.1, [(D, 18), (D, 18)])
    pack(12.3, [(G, 18), (D, 18)])
    pack(11.5, [(Sk, 19), (Sk, 19)])
    pack(10.8, [(St, 19), (D, 19)])
    pack(10.1, [(G, 19), (G, 19)])
    room_pack(wx, wy, [(D, 19), (D, 19), (St, 19)], spread=8.0, start=0.3)             # the Warden's egg-guards
    # ---- mid ring (20-21): spitters, skulkers and the first tenders
    pack(8.8, [(Sk, 20), (Sp, 20)])
    pack(8.1, [(St, 20), (St, 20)])
    pack(7.5, [(K, 20), (G, 20), (G, 20)])
    pack(6.7, [(Sp, 20), (D, 20), (D, 20)])
    pack(6.1, [(Cr, 21), (G, 21)])
    pack(5.6, [(Wv, 21), (G, 21)])
    room_pack(kx, ky, [(K, 21), (K, 21), (D, 21), (D, 21)], spread=8.5, start=0.6)        # the Broodkeeper's attendants
    # ---- the screen (22): larvae, weavers, sentinels
    pack(4.5, [(Lv, 21), (Lv, 21)])
    pack(3.9, [(Wv, 22), (Sp, 22)])
    pack(3.4, [(Cr, 22), (Sk, 22)])
    pack(2.95, [(Se, 22), (K, 22)])
    room_pack(gx, gy, [(Lv, 22), (Lv, 22), (Lv, 22)], spread=7.5, start=0.9)              # larvae in their nursery
    # ---- the last approach (23): queen's own guard
    pack(1.7, [(Se, 22), (Se, 23)])
    pack(1.2, [(Wv, 23), (Cr, 23)])
    pack(0.7, [(Se, 23), (Lv, 23), (Lv, 23)])
    room_pack(CX, CY, [(Se, 23), (Se, 23)], spread=11.0, start=2.4)                       # sentinels at the throne
    # ---- nurseries
    for key, members in (("amberwing", [(D, 20), (D, 20)]), ("gnash", [(Lv, 22), (Lv, 22)]),
                         ("skrix", [(Wv, 23), (Wv, 23)]), ("eggs", [(D, 20), (D, 20), (K, 21)])):
        x, y = nook_pos[key]
        room_pack(x, y, members, spread=3.8, start=1.1)
    zone.trash_spawns = list(TRASH)
    return zone, L


def finish(zone, L):
    targets = [PORTAL] + [(x, y) for (x, y) in BOSSES.values()] + list(CHESTS)
    return L.finish(targets)


def generate_the_broodspiral():
    zone, L = build_broodspiral()
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


BAKED_FMT = BAKED                      # bake_durotar_caves.bake_spec does C.BAKED.format(slug); no placeholder = fixed dir


def build_broodspiral_baked():
    """(zone, layout) with flood-fill QA done - what the baker paints from."""
    zone, L = build_broodspiral()
    finish(zone, L)
    return zone, L
