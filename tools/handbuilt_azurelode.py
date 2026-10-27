"""
Hand-built Azurelode Mine (110x90): the silver mine in Western Hillsbrad's western rock, levels 23-26.

ARCHETYPE: THE DROWNED WORKINGS.  Not a switchback bench mine (Boulder Lode), not a round drowned rotunda
(Sunken Temple Grotto), not a wheel, spiral, ladder, hive or C-warren.  Azurelode cut too deep and struck the
water table: the whole lower half of the mine is one great SUMP of standing water, and the workings that are
left are ISLANDS of spoil in it.  You do not walk a corridor through this cave - you pick your way across it,
wading the shallows and crossing the causeways the kobolds have piled from mine waste, with deep water (not
walkable) in between.  The route is a loop around the sump rather than a line through it, so the Pump House
and the Silver Face can be taken in either order.

    The Adit (55,83) -> the Haulage Drift descends north -> THE SUMP:
        Spoil Island (centre)  --causeway W-->  The Pump House (Grimewick the Drowned)
        Spoil Island           --causeway N-->  The Silver Face (Overseer Ashlan Silvervein, the boss)
        east shallows          ------------->  The Kobold Warren (dry side gallery)
        west shallows          ------------->  The Drowned Stope (Deepmuck)

Water rules this layout, so it is built in four explicit passes rather than carved and left: carve the rock,
flood the sump, put the islands BACK as dry floor, then lay the wadeable causeways. Deep water is not
walkable and shallow water is (world/tiles.py), which is what makes the islands gate movement at all.

Three bosses => TRASH IS RANDOM (zone.fixed_spawns = False; encounters.json caves["Azurelode Mine"]).

HARD CONTRACTS (world/portal_manager.py): portal (55,86) <-> Western Hillsbrad (33,60); arrival = 2 north.
Prop rule (Kyle): less is more; logical for the room; a few centrepieces.
"""
import numpy as np

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, _apply_pools, register_baked, pool_fields  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

GP = "assets/tiles/goblin_shared/props/"
BAKED = "assets/tiles/azurelode_mine/baked"
W, H = 110, 90
PORTAL = (55, 86)

# ---- carved rock: drifts and chambers ------------------------------------------------------------------
PATHS = {
    "adit":     ([(55, 86), (55, 81), (55, 77)], 5.0, 6.0),
    "drift":    ([(55, 77), (54, 71), (52, 65)], 6.0, 7.0),          # the haulage drift down to the water
    "sump_rim": ([(20, 58), (34, 63), (52, 65), (72, 62), (88, 56)], 7.0, 7.0),   # the dry shelf round the south rim
    "east_gal": ([(88, 56), (95, 50), (97, 42)], 5.0, 5.0),
    "west_gal": ([(20, 58), (14, 52), (13, 44)], 5.0, 5.0),
}
# ---- chambers: (cx, cy, rx, ry, rot, phase, display name) ------------------------------------------------
ROOMS = {
    "adit":    (55, 83, 10, 4.0, 0, 0.4, "The Adit"),
    "drift":   (53, 70, 9, 5.0, 0, 1.1, "The Haulage Drift"),
    "sump":    (55, 40, 36, 22, 0, 2.2, "The Sump"),                 # the flooded hall - most of this is water
    "warren":  (97, 36, 11, 8.0, 0, 1.4, "The Kobold Warren"),
    "stope":   (13, 38, 10, 7.0, 0, 0.8, "The Drowned Stope"),
}

#: The sump itself: (cx, cy, rx, ry). EVERYTHING carved inside this ellipse floods unless it is an island or
#: the southern shelf. Hand-placed water blobs were tried first and the archetype did not survive the test -
#: they left a dry band along the north of the sump, so the player could simply walk AROUND the water and
#: reach every island without wading. Deriving the water from the room instead of painting it in means the
#: gating is structural and cannot quietly spring a leak when a blob is nudged.
SUMP = (55, 40, 36, 22)
#: The dry shelf along the south rim, where the miners stopped: polyline + half-width.
SHELF = ([(18, 58), (34, 63), (52, 65), (72, 62), (90, 56)], 5.0)
#: Dry ground inside the sump: (cx, cy, rx, ry). Put back AFTER flooding.
ISLANDS = [
    (55, 47, 9.0, 5.5),      # Spoil Island - the hub you arrive at
    (33, 40, 7.5, 5.0),      # The Pump House
    (56, 22, 12.0, 7.0),     # The Silver Face - the vein, and the boss
    (76, 30, 5.0, 3.5),      # a stepping heap on the east side
]
#: Wadeable routes between the islands: (points, half-width in tiles).
CAUSEWAYS = [
    ([(53, 62), (54, 57), (55, 53)], 2.0),          # drift shelf -> Spoil Island
    ([(47, 46), (40, 43), (36, 41)], 1.8),          # Spoil Island -> Pump House
    ([(55, 41), (55, 34), (56, 29)], 2.0),          # Spoil Island -> Silver Face
    ([(63, 45), (71, 38), (75, 33)], 1.8),          # Spoil Island -> east stepping heap
    ([(80, 29), (88, 33), (92, 38)], 1.8),          # east heap -> Kobold Warren
    ([(26, 42), (20, 40), (16, 39)], 1.8),          # Pump House -> Drowned Stope
]

BOSSES = {}
CHESTS = []


def _near_walkable(zone, x, y, rad=5):
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            if zone.is_walkable(int(x) + dx, int(y) + dy):
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, int(x) + dx, int(y) + dy)
    return None if best is None else (best[1], best[2])


def _dist_to_polyline(pts, x, y):
    best = 1e9
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / L2))
        px, py = x0 + t * dx, y0 + t * dy
        best = min(best, ((x - px) ** 2 + (y - py) ** 2) ** 0.5)
    return best


def _flood_sump(zone):
    """Deep-water every carved tile inside SUMP that is not an island or the southern shelf.

    Derived from the room, not painted on: an earlier version placed three water blobs by hand and left a dry
    band across the north of the sump, so every island was reachable on foot and the whole drowned-workings
    idea was decoration. Checking that is what caught it - see the test in the module docstring's contract.
    """
    cx, cy, rx, ry = SUMP
    shelf_pts, shelf_half = SHELF
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if not (0 <= x < zone.width and 0 <= y < zone.height):
                continue
            if zone.collision_layer[y][x] == "rock":
                continue
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 > 1.0:
                continue
            if any(((x - ix) / irx) ** 2 + ((y - iy) / iry) ** 2 <= 1.0 for (ix, iy, irx, iry) in ISLANDS):
                continue
            if _dist_to_polyline(shelf_pts, x, y) <= shelf_half:
                continue
            zone.set_tile(x, y, "deep_water", "base")
            zone.collision_layer[y][x] = None


def _dry(zone, cx, cy, rx, ry):
    """Put rock-free DRY floor back inside an ellipse (an island in the sump)."""
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if not (0 <= x < zone.width and 0 <= y < zone.height):
                continue
            if zone.collision_layer[y][x] == "rock":
                continue
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None


def _wade(zone, pts, half):
    """Lay a wadeable shallow-water causeway along a polyline (never over rock)."""
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        steps = max(abs(x1 - x0), abs(y1 - y0)) * 3 + 1
        for s in range(steps + 1):
            t = s / steps
            cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            r = int(half) + 1
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    x, y = int(round(cx)) + dx, int(round(cy)) + dy
                    if not (0 <= x < zone.width and 0 <= y < zone.height):
                        continue
                    if zone.collision_layer[y][x] == "rock":
                        continue
                    if dx * dx + dy * dy > half * half:
                        continue
                    if zone.base_layer[y][x] == "deep_water":
                        zone.set_tile(x, y, "shallow_water", "base")
                        zone.collision_layer[y][x] = None


#: A dry pocket this size or smaller at the water's edge is a rounding artifact of the flood mask and gets
#: drowned. Anything BIGGER is a real design break - a room nobody can reach - and must fail loudly instead.
MAX_SLIVER = 8


def _drown_slivers(zone, start):
    """Flood tiny unreachable dry pockets; raise on a big one.

    Deriving the sump from the room (rather than hand-placed blobs) leaves a handful of one- and two-tile dry
    slivers where the ellipse edge grazes the rock - six of them, the first time. They are invisible to the
    player but they trip the cave's own reachability assert, and nudging the geometry to chase them would just
    move them somewhere else. So they are drowned deterministically.

    The size cap is the point: it cleans up arithmetic noise without papering over an actual mistake. If a
    whole island or gallery ever ends up cut off, this raises instead of quietly flooding it.
    """
    from collections import deque as _dq
    wset = {(x, y) for y in range(zone.height) for x in range(zone.width) if zone.is_walkable(x, y)}
    seen = {start}
    q = _dq([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and n in wset:
                seen.add(n)
                q.append(n)
    rest = wset - seen
    while rest:
        seed = next(iter(rest))
        pocket = {seed}
        q = _dq([seed])
        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if n not in pocket and n in rest:
                    pocket.add(n)
                    q.append(n)
        if len(pocket) > MAX_SLIVER:
            raise AssertionError(
                f"Azurelode Mine: {len(pocket)} walkable tiles cut off at {sorted(pocket)[0]} - that is a "
                f"layout break, not an edge sliver; fix the causeways or the island, do not raise MAX_SLIVER")
        for (x, y) in pocket:
            zone.set_tile(x, y, "deep_water", "base")
            zone.collision_layer[y][x] = None
        rest -= pocket


def build_azurelode():
    zone = Tilemap("Azurelode Mine", W, H,
                   "A silver mine that cut too deep and struck water: the lower workings are islands of spoil "
                   "in a standing sump, worked now by kobolds.")
    zone.is_cave = True
    # .region is how a cave declares its PARENT ZONE (world/zone_manager.py:55), which is what the
    # encounter lookup and the pull builder key off - not a flavour label. "Hillsbrad Foothills" is
    # not a zone, so this read back empty everywhere it mattered.
    zone.region = "Western Hillsbrad"
    zone.fixed_spawns = False
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b

    # 1) carve the rock
    for i, (key, (pts, w0, w1)) in enumerate(PATHS.items()):
        tube(b, pts, w0, w1, ph=0.5 + i * 0.9)
    for key, (cx, cy, rx, ry, rot, ph, _n) in ROOMS.items():
        cavern(b, cx, cy, rx, ry, rot, ph)

    # 2) flood the sump - everything in it that is not island or shelf
    _flood_sump(zone)

    # 3) put the islands back as dry ground
    for (cx, cy, rx, ry) in ISLANDS:
        _dry(zone, cx, cy, rx, ry)

    # 4) lay the wadeable causeways between them
    for pts, half in CAUSEWAYS:
        _wade(zone, pts, half)

    # 5) drown the slivers the flood leaves at the sump's edge
    _drown_slivers(zone, (PORTAL[0], PORTAL[1] - 2))

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.set_tile(px, py, "dirt", "base")
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    bosses = [(56, 22, "Overseer Ashlan Silvervein"),      # the Silver Face
              (33, 40, "Grimewick the Drowned"),           # the Pump House
              (13, 38, "Deepmuck")]                        # the Drowned Stope
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
    for (x, y) in ((55, 47), (97, 36), (13, 38), (62, 20)):
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        chests.append(p)
    CHESTS[:] = chests
    for c in chests:
        L.mark("chest", *c)

    def sub(name, x, y, rx, ry):
        zone.add_subzone(name, int(x - rx), int(y - ry), int(2 * rx), int(2 * ry))
    zone.add_subzone("Azurelode Mine", 0, 0, W, H)          # the cave's encounter-table key covers the map
    for key, (cx, cy, rx, ry, rot, ph, name) in ROOMS.items():
        sub(name, cx, cy, rx + 2, ry + 2)                   # later registration wins, so rooms are display names
    zone.add_subzone("The Silver Face", 44, 15, 24, 14)
    zone.add_subzone("The Pump House", 26, 35, 15, 11)
    return zone, L


def finish(zone, L):
    targets = [PORTAL] + [(x, y) for (x, y) in BOSSES.values()] + list(CHESTS)
    return L.finish(targets)


def dress(zone, L):
    P = L.prop
    # ---- the adit: the shift that never came back up
    P("gob_mine_frame", 55, 83, 8, where=GP, solid=False)
    P("rf_brazier", 49, 83, 3)
    P("rf_brazier", 61, 83, 3)
    P("gob_ore_cart", 47, 82, 4, where=GP)
    P("vot_crate_stack", 63, 82, 3)
    # ---- the haulage drift down to the water
    P("den_torch", 48, 70, 4)
    P("den_torch", 59, 70, 4)
    P("gob_ore_cart", 56, 72, 4, where=GP)
    P("den_rock_rubble", 50, 67, 2)
    # ---- the south shelf: where the water stopped them
    P("gob_claim_marker", 40, 62, 6, where=GP)
    P("rf_tool_rack", 66, 62, 3)
    P("grotto_tide_pool", 30, 60, 3, solid=False)
    P("den_glow_mushrooms", 74, 60, 2, solid=False)
    # ---- Spoil Island: the kobolds' camp on the heap
    P("gob_ore_pile", 50, 47, 3, where=GP)
    P("gob_ore_pile", 60, 48, 3, where=GP)
    P("den_campfire_ashes", 55, 44, 2)
    P("rf_supply_crates", 58, 44, 3)
    P("den_backpack", 52, 44, 2)
    # ---- The Pump House: the machinery that lost the fight
    P("gob_boiler_tank", 33, 37, 6, where=GP)
    P("gob_pipe_tangle", 28, 41, 4, where=GP, solid=False)
    P("gob_oil_drums", 37, 42, 3, where=GP)
    P("den_torch", 30, 36, 4)
    P("grotto_barrel_stack", 36, 36, 3)
    # ---- The Silver Face: the vein they were chasing, and the overseer standing on it
    P("rf_void_crystals", 48, 23, 5, solid="core")
    P("rf_void_crystals", 65, 21, 5, solid="core")
    P("rf_void_crystals", 59, 21, 6, solid="core", avoid=1)
    P("rf_brazier", 50, 26, 3)
    P("rf_brazier", 62, 26, 3)
    P("gob_ore_cart", 46, 24, 4, where=GP)
    P("rf_tool_rack", 66, 25, 3)
    # ---- The Kobold Warren: the dry side gallery they actually live in
    P("den_glow_mushrooms", 92, 34, 2, solid=False)
    P("den_campfire_ashes", 96, 33, 2)
    P("gob_ore_pile", 101, 34, 3, where=GP)
    P("den_backpack", 94, 39, 2)
    P("den_stalagmites", 103, 40, 4, solid="core")
    # ---- The Drowned Stope: a collapsed working, half under
    P("den_rock_rubble", 10, 35, 3, solid="core")
    P("den_stalagmite_pair", 17, 34, 4, solid="core")
    P("grotto_tide_pool", 14, 41, 3, solid=False)
    P("gob_ore_cart", 9, 41, 4, where=GP)
    return zone, L


def generate_azurelode_mine():
    zone, L = build_azurelode()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_azurelode_baked():
    """(zone, layout) with props + QA done - what the baker paints from."""
    zone, L = build_azurelode()
    dress(zone, L)
    finish(zone, L)
    return zone, L
