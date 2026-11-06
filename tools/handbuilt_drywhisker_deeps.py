"""
Hand-built Drywhisker Deeps (150x160): the kobold dig under Arathi Central. FOUR BOSSES, hand-placed trash.

Kyle, 2026-11-01: "a kobold dungeon from 37-40 in the central" - tuned ABOVE its zone (Central is
33-37) on purpose, so the entrance is somewhere you find at 34 and the dungeon is somewhere you come
back to at 38. It also lands on the game's SECOND content trough: levels 38-40 fall from 59 quests at
36 to 18 at 40 and never recover.

Multi-boss, so trash is HAND-PLACED (TRASH -> zone.trash_spawns, regrouped by
tools/build_dungeon_pulls.py). That is the one place the standing rule allows it.

ARCHETYPE: A WORKING MINE, DUG DOWNWARD. Stromgarde is a city laid out in wards; the five Arathi caves
are natural rock. This is neither - it is INDUSTRY, and its shape is the shape of an excavation:

  * FOUR LEVELS, each a long horizontal GALLERY, stacked top to bottom and joined by three INCLINES at
    alternating ends. You switch back on yourself every level, so depth is something you feel rather
    than read on a map. Each gallery is a little wider and a little wetter than the one above it.
  * STOPES hang off every gallery - the short dead-end side cuts where the ore actually was. They are
    where the kobolds live and where everything worth taking is.
  * THE SUMP at the bottom, because a mine fills with water from underneath, and the kobolds have been
    digging below the waterline for a while now. That is what woke the last boss.
  * ONE VENTILATION SHAFT running the full height off to the west, connecting level one to level four
    directly. It is narrow, it is a shortcut, and it is the only part of the mine nobody is guarding -
    which also means it drops you at the bottom with three levels of kobolds behind you.

  Adit (76,154) -> FIRST GALLERY (Grubbis Tallow) -> incline -> SECOND GALLERY (Overseer Ratch)
       -> incline -> THIRD GALLERY (the Pick-Mother) -> incline -> THE SUMP (What They Dug Into)

HARD CONTRACTS (world/portal_manager.py)
  (76, 154) <-> Arathi Central (170, 114)   the adit at the head of Drywhisker Gorge
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

BAKED = "assets/tiles/drywhisker_deeps/baked"
W, H = 150, 160
PORTAL = (76, 154)

#: Each gallery is a list of lobes, so a level has ends and a bulge rather than being one long bar.
#: They get wider and wetter with depth - 11, 12, 13, 15 - which is the one number that says "down".
GALLERIES = {
    "g1": ([(44, 136, 22.0, 5.5, 0, 0.6), (92, 134, 24.0, 6.0, 0, 2.1)], "The First Gallery"),
    "g2": ([(54, 100, 24.0, 6.0, 0, 1.4), (104, 102, 22.0, 6.5, 0, 2.9)], "The Second Gallery"),
    "g3": ([(42, 64, 22.0, 6.5, 0, 0.9), (90, 66, 25.0, 7.0, 0, 2.3)], "The Third Gallery"),
    "sump": ([(70, 24, 28.0, 9.0, 0, 1.7), (40, 30, 12.0, 6.0, 0, 0.4)], "The Sump"),
}
PATHS = {
    # EVERY END OF EVERY LINK SITS INSIDE THE SPACE IT JOINS, not on its rim. The first build put
    # all four on the edge and eleven of the thirteen markers - four bosses included - came back
    # unreachable. A gallery's real extent is its lobe centre plus or minus its radius; read that,
    # do not eyeball it.
    "adit":     ([(76, 154), (76, 146), (76, 137)], 5.4, 5.6),
    # the inclines, alternating ends: east, west, east
    "incline1": ([(112, 132), (128, 118), (118, 104)], 4.4, 4.6),
    "incline2": ([(36, 98), (22, 84), (32, 67)], 4.4, 4.6),
    "incline3": ([(108, 64), (122, 46), (94, 30)], 4.4, 4.6),
    # THE VENTILATION SHAFT: full height, narrow, unguarded, and it puts you at the bottom with three
    # levels of kobolds between you and the door.
    # 2.8, not 2.4: at the narrower width the spline's own breathing pinched the shaft shut
    # around y=80 and left a 9-tile pocket. A corridor meant to be tight still has to be open.
    "shaft":    ([(14, 134), (8, 112), (10, 88), (8, 74), (6, 62), (12, 40), (32, 30)], 2.8, 2.8),
    "shaft_in": ([(22, 136), (14, 134)], 2.6, 2.6),
    # the ore road: a rail run along the second gallery's back wall, bypassing its middle
    # 3.4: at 2.8 the spline's breathing left two 4-tile fragments of rail floating between
    # the stope stubs and the gallery below. A rail run has to be continuous to be a route.
    "orerail":  ([(36, 95), (64, 91), (96, 93), (120, 98)], 3.4, 3.4),
}
#: STOPES - the short dead-end side cuts where the ore was, and where the kobolds live.
STOPES = [
    (24, 128, 4.5, 3.6, 0, 0.5), (56, 128, 4.0, 3.2, 0, 1.6), (84, 126, 4.5, 3.6, 0, 2.7),
    (110, 142, 4.0, 3.2, 0, 0.8), (62, 144, 4.0, 3.2, 0, 2.0),
    (38, 92, 4.5, 3.6, 0, 1.2), (74, 92, 4.0, 3.2, 0, 2.4), (116, 92, 4.5, 3.6, 0, 0.3),
    (92, 110, 4.0, 3.2, 0, 1.9), (46, 110, 4.0, 3.2, 0, 3.1),
    (28, 56, 4.5, 3.6, 0, 0.7), (64, 56, 4.5, 3.6, 0, 2.2), (104, 56, 4.0, 3.2, 0, 1.5),
    (80, 76, 4.5, 3.6, 0, 2.8), (40, 76, 4.0, 3.2, 0, 0.9),
    (36, 14, 5.0, 3.6, 0, 1.1), (100, 12, 5.0, 3.6, 0, 2.5),
]
#: PILLARS are the mine's own: left standing because pulling them drops the roof. Rows of them down
#: each gallery turn a long hall into aisles, which is what a real stope-and-pillar working looks like.
PILLARS = [
    (30, 136, 2.2, 2.2, 0), (50, 136, 2.2, 2.2, 0), (70, 135, 2.2, 2.2, 0),
    (90, 134, 2.2, 2.2, 0), (110, 134, 2.2, 2.2, 0),
    (40, 100, 2.4, 2.4, 0), (62, 100, 2.4, 2.4, 0), (84, 101, 2.4, 2.4, 0), (108, 102, 2.4, 2.4, 0),
    (30, 64, 2.4, 2.4, 0), (52, 64, 2.4, 2.4, 0), (76, 65, 2.4, 2.4, 0), (100, 66, 2.4, 2.4, 0),
    # the sump's drowned supports, bigger because this level was never finished
    (56, 24, 3.2, 3.2, 0), (84, 24, 3.2, 3.2, 0), (70, 16, 3.0, 3.0, 0),
]

BOSSES = {}
CHESTS = []
TRASH = []


def build_deeps():
    zone = Tilemap("Drywhisker Deeps", W, H,
                   "A kobold working dug four levels into the gorge wall, the bottom one below the "
                   "waterline and filling.")
    zone.is_cave = True
    # The PARENT OPEN ZONE, which is also the encounter-table key - see
    # tools/handbuilt_arathi_caves.py. "Arathi Highlands" is prose and
    # names no zone, so this cave resolved no table at all.
    zone.region = "Arathi Central"
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b

    for (lobes, _n) in GALLERIES.values():
        for (cx, cy, rx, ry, rot, ph) in lobes:
            cavern(b, cx, cy, rx, ry, rot, ph)
    for st in STOPES:
        cavern(b, *st)
    # EVERY STOPE GETS A STUB back to its gallery. Written as bare caverns they all sat a tile or two
    # clear of the lobe they belonged to - seven markers, including a boss, came back unreachable and
    # the rest were one wobble away from it. A side cut is a cut INTO something; the stub is what
    # makes that true no matter how the lobe edge wobbles, and it reads correctly as the mouth of
    # the working. Each one runs to the nearest gallery lobe CENTRE, so it always lands in open floor.
    centres = [(cx, cy) for (lobes, _n) in GALLERIES.values() for (cx, cy, _rx, _ry, _r, _p) in lobes]
    for (sx, sy, _rx, _ry, _rot, _ph) in STOPES:
        gx, gy = min(centres, key=lambda c: (c[0] - sx) ** 2 + (c[1] - sy) ** 2)
        tube(b, [(sx, sy), (sx + (gx - sx) * 0.6, sy + (gy - sy) * 0.6)], 3.4, 3.8)
    for i, (pts, w0, w1) in enumerate(PATHS.values()):
        tube(b, pts, w0, w1, ph=0.4 + i * 0.8)

    for (cx, cy, rx, ry, rot) in PILLARS:
        import math as _m
        c, s_ = _m.cos(_m.radians(rot)), _m.sin(_m.radians(rot))
        R = int(max(rx, ry)) + 2
        for yy in range(int(cy) - R, int(cy) + R + 1):
            for xx in range(int(cx) - R, int(cx) + R + 1):
                if not (0 <= xx < W and 0 <= yy < H):
                    continue
                dx, dy = xx - cx, yy - cy
                u, v = (c * dx + s_ * dy) / rx, (-s_ * dx + c * dy) / ry
                if u * u + v * v <= 1.0:
                    zone.collision_layer[yy][xx] = "wall"
                    zone.set_tile(xx, yy, "rock", "collision")

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    bosses = [(110, 142, "Grubbis Tallow"), (116, 92, "Overseer Ratch"),
              (28, 56, "The Pick-Mother"), (70, 20, "What They Dug Into")]
    fixed = []
    for (x, y, n) in bosses:
        if not zone.is_walkable(x, y):
            raise AssertionError((n, x, y))
        L.mark("boss_marker", x, y)
        fixed.append((x, y, n))
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (70, 20)
    zone.boss_positions = list(fixed)

    chests = [(24, 128), (62, 144), (46, 110), (74, 92), (64, 56), (80, 76), (36, 14), (100, 12)]
    for c in chests:
        if not zone.is_walkable(*c):
            raise AssertionError(("chest", c))
        L.mark("chest", *c)
    CHESTS[:] = chests

    zone.add_subzone("Drywhisker Deeps", 0, 0, W, H)
    for (lobes, name) in GALLERIES.values():
        x0 = min(cx - rx for (cx, cy, rx, ry, _r, _p) in lobes)
        x1 = max(cx + rx for (cx, cy, rx, ry, _r, _p) in lobes)
        y0 = min(cy - ry for (cx, cy, rx, ry, _r, _p) in lobes)
        y1 = max(cy + ry for (cx, cy, rx, ry, _r, _p) in lobes)
        zone.add_subzone(name, int(x0 - 2), int(y0 - 3), int(x1 - x0 + 4), int(y1 - y0 + 6))
    zone.add_subzone("The Ventilation Shaft", 0, 24, 22, 118)
    return zone, L


def _trash():
    T = []

    def pack(lvl, *spots):
        for (x, y, m) in spots:
            T.append((x, y, m, lvl))

    # first gallery - tallow-lamp kobolds, the ones nearest the door
    pack(37, (70, 140, "Drywhisker Digger"), (74, 138, "Drywhisker Digger"), (66, 137, "Drywhisker Tunneler"))
    pack(37, (40, 134, "Drywhisker Digger"), (36, 132, "Drywhisker Tunneler"), (44, 131, "Drywhisker Digger"))
    pack(37, (24, 128, "Drywhisker Tunneler"), (28, 126, "Drywhisker Digger"), (22, 124, "Drywhisker Digger"))
    pack(38, (96, 134, "Drywhisker Tunneler"), (100, 132, "Drywhisker Digger"), (92, 131, "Drywhisker Digger"),
         (98, 138, "Drywhisker Geomancer"))
    # the first incline
    pack(38, (124, 122, "Drywhisker Tunneler"), (128, 118, "Drywhisker Digger"), (124, 114, "Drywhisker Geomancer"))
    # second gallery - the ore road and the stopes off it
    pack(38, (64, 102, "Drywhisker Tunneler"), (60, 99, "Drywhisker Digger"), (68, 99, "Drywhisker Digger"))
    pack(38, (38, 92, "Drywhisker Geomancer"), (34, 94, "Drywhisker Digger"), (42, 94, "Drywhisker Digger"))
    pack(39, (92, 110, "Drywhisker Tunneler"), (88, 108, "Drywhisker Digger"), (96, 108, "Drywhisker Digger"),
         (92, 104, "Drywhisker Geomancer"))
    pack(39, (46, 110, "Drywhisker Digger"), (42, 108, "Drywhisker Tunneler"), (50, 108, "Drywhisker Digger"))
    # the second incline, and the third gallery
    pack(39, (26, 90, "Drywhisker Tunneler"), (22, 84, "Drywhisker Geomancer"), (26, 76, "Drywhisker Digger"))
    pack(39, (46, 64, "Drywhisker Tunneler"), (42, 62, "Drywhisker Digger"), (50, 62, "Drywhisker Digger"))
    pack(39, (80, 76, "Drywhisker Geomancer"), (76, 78, "Drywhisker Digger"), (84, 78, "Drywhisker Tunneler"))
    pack(40, (86, 66, "Drywhisker Tunneler"), (90, 63, "Drywhisker Digger"), (82, 63, "Drywhisker Digger"),
         (96, 66, "Drywhisker Geomancer"))
    # the third incline, and the sump - what is down here is not kobold
    pack(40, (118, 54, "Drywhisker Tunneler"), (122, 46, "Drywhisker Geomancer"), (114, 38, "Drywhisker Digger"))
    pack(40, (96, 28, "Brine-Choked Digger"), (100, 24, "Brine-Choked Digger"), (92, 22, "Deep Seep"))
    pack(40, (44, 28, "Brine-Choked Digger"), (40, 24, "Deep Seep"), (48, 22, "Brine-Choked Digger"))
    return T


def dress(zone, L):
    P = L.prop

    def p(name, x, y, h, **kw):
        mark = len(L.skipped)
        for r in range(0, 7):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if max(abs(dx), abs(dy)) != r:
                        continue
                    nx, ny = x + dx, y + dy
                    if zone.is_walkable(nx, ny) and P(name, nx, ny, h, **kw):
                        del L.skipped[mark:]
                        return True
        del L.skipped[mark:]
        L.skipped.append((name, x, y, "no usable floor within radius"))
        return False

    # ---- the adit: the gear they took with the dig
    p("rf_ore_cart", 70, 150, 4)
    p("rf_tool_rack", 82, 150, 4)
    p("rf_supply_crates", 76, 146, 3)
    # ---- first gallery: working face, carts, tallow lamps
    for (x, y) in ((34, 136), (60, 135), (104, 133)):
        p("rf_ore_cart", x, y, 4)
    p("rf_tool_rack", 48, 139, 4)
    p("den_torch", 44, 131, 4)
    p("den_torch", 96, 130, 4)
    p("rf_trogg_nest", 24, 128, 4, solid="core")
    p("rf_trogg_tent", 56, 128, 5)
    p("rf_trogg_totem", 84, 126, 6, solid="core")
    p("den_stalactites", 72, 131, 3)
    # ---- second gallery: deeper, the ore road, the overseer's stope
    for (x, y) in ((50, 100), (96, 102)):
        p("rf_ore_cart", x, y, 4)
    p("rf_supply_crates", 64, 96, 3)
    p("rf_trogg_tent", 38, 92, 5)
    p("rf_trogg_nest", 92, 110, 4, solid="core")
    p("rf_trogg_totem", 46, 110, 6, solid="core")
    p("den_glow_mushrooms", 74, 92, 3)
    p("den_torch", 108, 99, 4)
    # ---- third gallery: wet, and the Pick-Mother's brood
    p("rf_trogg_nest", 28, 56, 5, solid="core", avoid=2)
    p("den_egg_cluster", 34, 60, 4)
    p("den_egg_cluster", 22, 60, 4)
    p("rf_ore_cart", 68, 65, 4)
    p("rf_trogg_tent", 64, 56, 5)
    p("rf_trogg_totem", 104, 56, 6, solid="core")
    p("den_spring_pool", 96, 70, 3)
    p("den_glow_mushrooms", 40, 76, 3)
    p("den_stalagmites", 88, 60, 4, solid="core")
    # ---- the sump: below the waterline, and the thing they dug into
    p("grotto_tide_pool", 56, 30, 3)
    p("grotto_tide_pool", 88, 30, 3)
    p("grotto_kelp_stalks", 46, 20, 3)
    p("grotto_barnacle_pillar", 100, 20, 6, solid="core")
    p("grotto_serpent_skeleton", 70, 14, 6, solid="core", avoid=2)
    p("rf_void_crystals", 36, 14, 4)
    p("rf_void_crystals", 100, 12, 4)
    p("den_stalactites", 70, 30, 3)
    return zone, L


def finish(zone, L):
    targets = [PORTAL] + list(BOSSES.values()) + list(CHESTS)
    return L.finish(targets)


def _snap_trash(zone, spots, rad=4):
    """Nudge each hand-placed mob onto real floor, and report any that cannot be.

    Trash is authored against a mental picture of the floorplan while the floorplan is generated, so a
    mob written beside a pillar or just past a gallery edge lands in rock. In rock it is silently
    un-fightable, and dungeon_packs.apply_packs only raises on it much later with a message about
    re-running the pull builder, a long way from the coordinates that are wrong.

    Snapping keeps the pack TOGETHER - a member moved two tiles is still in its pull - while a mob
    with no floor within `rad` is a real authoring error and is reported with its position.
    """
    out, lost = [], []
    for (x, y, mob, lvl) in spots:
        if zone.is_walkable(x, y):
            out.append((x, y, mob, lvl))
            continue
        best = None
        for dy in range(-rad, rad + 1):
            for dx in range(-rad, rad + 1):
                nx, ny = x + dx, y + dy
                if not zone.is_walkable(nx, ny):
                    continue
                if any(abs(px - nx) + abs(py - ny) < 1 for (px, py, _m, _l) in out):
                    continue
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, nx, ny)
        if best is None:
            lost.append((x, y, mob, lvl))
        else:
            out.append((best[1], best[2], mob, lvl))
    return out, lost


def _attach_trash(zone):
    """Hand-placed trash, checked against the real floor - see the note in handbuilt_stromgarde_keep."""
    snapped, dropped = _snap_trash(zone, _trash())
    TRASH[:] = snapped
    zone.trash_spawns = list(TRASH)
    zone.authored_trash_spawns = list(TRASH)
    return dropped


def generate_drywhisker_deeps():
    zone, L = build_deeps()
    dress(zone, L)
    finish(zone, L)
    _attach_trash(zone)
    register_baked(zone, BAKED)
    return zone


def build_drywhisker_baked():
    zone, L = build_deeps()
    dress(zone, L)
    finish(zone, L)
    _attach_trash(zone)
    return zone, L


if __name__ == "__main__":
    z, L = build_deeps()
    dress(z, L)
    finish(z, L)
    dropped = _attach_trash(z)
    walk = sum(1 for y in range(H) for x in range(W) if z.is_walkable(x, y))
    print(f"Drywhisker Deeps {W}x{H}  {walk} walkable  {len(BOSSES)} bosses  {len(CHESTS)} chests  "
          f"{len(TRASH)} trash  skipped props {len(L.skipped)}")
    for d in dropped:
        print("   TRASH IN ROCK:", d)
    for sk in L.skipped:
        print("   skipped:", sk)
