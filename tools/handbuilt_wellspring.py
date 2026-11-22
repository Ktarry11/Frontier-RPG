"""
Hand-built The Wellspring (88x92): under the Hearthdeep, the second floor of the Threefold Forge's roots on the Fading
Firmament, 59.

THE SKY'S ONE MYSTERY, THE FIRMAMENT'S PIECE (docs/worldtree_brief.md: "a thing only the three together could have
made"). The wellstones were grown here, in the dark under the forge. The seedbeds are giants' work, long troughs of
quarried stone; the seeds in them are Aetherian-cut crystal; and the channels cut round the beds are wind-ways, for the
Veyr's songs to run through and wake the water out of the stone. Nobody in Aurelion knows where the wellstones came from.
This is where, and it took all three. The beds have been dry longer than any house has kept records. It says nothing
about why the three stopped, or what's killing the sky now.

    the way in (44,2) <- the Deep Stair, from the Hearthdeep
    THE SINGING STAIR: down, the first wind-ways cut into its walls
    THE SEEDBEDS: two long halls of stone troughs, west and east, the seeds still in them, and the seedbed warden
      (optional) in the west
    THE SINGING CHANNEL: the wind-way round the Motherstone's hall, walked either way
    THE MOTHERSTONE: the oldest wellstone, still pouring, and what the Ascendancy woke trying to cut it out

You arrive two tiles inside.
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked, _apply_pools  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

NAME = "The Wellspring"
W, H = 88, 92
BAKED = "assets/tiles/sky/baked_wellspring"
BAKED_DIR = BAKED
PARENT = "The Fading Firmament"
DESC = ("Under the forge, where the wellstones were grown: giants' stone beds, Aetherian-cut seeds and the Veyr's "
        "wind-ways, and the oldest wellstone still pouring.")
SKP = "assets/tiles/sky/props/"
BLD = "assets/buildings/"
ENT = "assets/tiles/cave_entrances/"

PORTAL = (44, 2)
PORTALS = {PORTAL: "The Hearthdeep"}
ARRIVALS = {PORTAL: (44, 4)}

STAIR = [(44, 2), (44, 14)]
LANDING = (44, 20, 14, 7)
BEDS_W = (16, 42, 11, 17)           # the west seedbeds: the seedbed warden
BEDS_E = (72, 42, 11, 17)           # the east seedbeds
MOTHER = (44, 70, 18, 13)           # the Motherstone's hall
MOTHER_POOL = (44, 66, 7.0, 4.5, 0.0)          # the Motherstone's pool: it pours
WAYS = [[(34, 22), (20, 28)], [(54, 22), (68, 28)],                                # the landing down to each bed hall
        [(20, 58), (30, 70)], [(68, 58), (58, 70)],                                # the beds down to the Motherstone
        [(44, 26), (44, 52)]]                                                      # straight down the middle
CHANNEL = [(26, 74), (34, 86), (44, 88), (54, 86), (62, 74)]                     # the wind-way round the hall's foot

BOSSES = {}
CHESTS = []
ROOM_NAMES = {}


def _near_walkable(zone, x, y, rad=5):
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            xx, yy = int(x) + dx, int(y) + dy
            if not zone.is_walkable(xx, yy):
                continue
            if zone.base_layer[yy][xx] in ("shallow_water", "deep_water"):
                continue
            d = dx * dx + dy * dy
            if best is None or d < best[0]:
                best = (d, xx, yy)
    return None if best is None else (best[1], best[2])


def build_wellspring_baked():
    zone = Tilemap(NAME, W, H, DESC)
    zone.is_cave = True
    zone.region = PARENT
    zone.fixed_spawns = False
    L = CaveLayout(zone, ARRIVALS[PORTAL])
    b = L.b
    tube(b, STAIR, 9.0, 10.0, ph=0.4)
    cavern(b, *LANDING, 0, 0.8)
    cavern(b, *BEDS_W, 4, 1.4)
    cavern(b, *BEDS_E, -4, 2.1)
    cavern(b, *MOTHER, 0, 2.9)
    for i, way in enumerate(WAYS):
        tube(b, way, 10.0, 10.0, ph=0.5 + 0.7 * i)
    tube(b, CHANNEL, 9.0, 9.0, ph=3.3)
    _apply_pools(zone, [MOTHER_POOL])
    for (px, py) in PORTALS:
        zone.collision_layer[py][px] = None
        L.mark("portal", px, py)
    fixed = []
    for (x, y, n) in [(MOTHER[0], MOTHER[1] + 6, "The Unsung"), (BEDS_W[0], BEDS_W[1] + 4, "The Seedbed Warden")]:
        p = _near_walkable(zone, x, y)
        assert p, (n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (fixed[0][0], fixed[0][1])
    zone.boss_positions = list(fixed)
    CHESTS[:] = []
    for (x, y) in [(8, 34), (80, 52), (44, 86), (60, 20)]:
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        CHESTS.append(p)
        L.mark("chest", *p)
    zone.add_subzone(NAME, 0, 0, W, H)
    rooms = {"The Singing Stair": (32, 0, 24, 28), "The West Seedbeds": (0, 24, 32, 38),
             "The East Seedbeds": (56, 24, 32, 38), "The Motherstone": (24, 56, 40, 28),
             "The Singing Channel": (20, 78, 48, 14)}
    ROOM_NAMES.clear()
    for rname, (x, y, w, h) in rooms.items():
        zone.add_subzone(rname, x, y, w, h)
        ROOM_NAMES[rname] = (x, y, w, h)
    dress(zone, L)
    L.finish(list(PORTALS) + list(BOSSES.values()) + CHESTS)
    return zone, L


def dress(zone, L):
    """The giants' troughs in rows with the cut seeds in them, the wind-ways' chimes, the Motherstone and its falls."""
    def P(name, x, y, h, where=SKP, **kw):
        p = _near_walkable(zone, x, y, rad=2)
        return L.prop(name, p[0], p[1], h, where=where, **kw) if p else L.skipped.append((name, x, y, "no floor"))
    P("ent_exit_crypt_stairs", PORTAL[0], PORTAL[1] + 2, 5, where=ENT, near_ok=True)
    P("vy_wind_chimes", 36, 18, 4, where=BLD, solid="core")
    P("vy_wind_chimes", 52, 18, 4, where=BLD, solid="core")
    # the seedbeds: the giants' troughs, a cut seed of crystal in each
    for (cx, side) in ((BEDS_W[0], -1), (BEDS_E[0], 1)):
        for y in (32, 42, 52):
            P("kh_quarry_blocks", cx - 4, y, 3, where=BLD, solid="core")
            P("sk_crystal_dim", cx + 4, y, 3, solid="core")
    P("vy_prayer_stone", 8, 44, 3, where=BLD, solid="core")
    P("vy_prayer_stone", 80, 44, 3, where=BLD, solid="core")
    # the Motherstone: the oldest wellstone over its pool, still pouring
    P("sk_crystal_spire", MOTHER[0], MOTHER[1] - 10, 7, solid="core")
    pass  # the edge falls prop is gone (Kyle, 21 Nov 2026: "lets remove this prop... it doesnt work")
    for a in (200, 340):
        P("kh_lantern", int(MOTHER[0] + 15 * math.cos(math.radians(a))), int(MOTHER[1] + 9 * math.sin(math.radians(a))),
          3, where=BLD, solid="core")
    P("ae_crystal_crates", MOTHER[0] + 12, MOTHER[1] + 6, 3, where=BLD, solid="core")    # the salvage crews' cutting kit


def generate_wellspring():
    zone, _L = build_wellspring_baked()
    import os
    if os.path.isdir(BAKED) and any(os.path.exists(f"{BAKED}/ground_0_0.{e}") for e in ("jpg", "png", "webp")):
        register_baked(zone, BAKED)
    return zone


if __name__ == "__main__":
    z, L = build_wellspring_baked()
    walk = sum(1 for y in range(z.height) for x in range(z.width) if z.is_walkable(x, y))
    print(NAME, z.width, "x", z.height, "| walkable", walk, "| bosses", BOSSES, "| skipped", L.skipped)
