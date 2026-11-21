"""
Hand-built The Storm-Well (84x100): the Golem Vault's second floor, under the Celestial Expanse's Golem Fields, 51.

Kyle, 20 Nov 2026: "remember that this is high level zone - so multiple floors are okay" and "Also hallway simulators
are boring and uninspired". Down the Deep Stair from the vault, the floor opens into the place the whole cave was built
round: where the Kharad wrights bound a storm and fed it into every golem's core and every ward on the islands, the same
storm that brought the council's skiff down on Crashfall.

You come down into the Binding Hall, a ring of chained binding stones. The Core Racks open off its west side, where the
spare cores hang charging. Two broad ramps go down from the hall either side, and the third way is straight down the
middle, and all three open onto the Well: one great round cavern with the storm itself in the middle, a pool of bound
storm-cloud you can't walk into. Four short bridges cross it to the binding dais in the centre, where Stormwright Yrvald
keeps the storm. Walk round the rim, cross on any bridge.
A cave, not a dungeon: trash rolled from the cave's own table, the boss pinned by the map.

    the way up (42,2) -> the Golem Vault's Deep Stair
    THE BINDING HALL: the ring of binding stones
    THE CORE RACKS: west off the hall, the spare cores
    THE WELL: the great round cavern, the storm in the middle, four bridges to the dais, Stormwright Yrvald

You arrive two tiles inside.
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked, _apply_pools  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

NAME = "The Storm-Well"
W, H = 84, 100
BAKED = "assets/tiles/sky/baked_storm_well"
BAKED_DIR = BAKED
PARENT = "The Celestial Expanse"
DESC = ("The Golem Vault's lowest floor, where the Kharad bound a storm and fed it into every golem's core and every "
        "ward on the islands. It's still bound, and its keeper is still keeping it.")
SKP = "assets/tiles/sky/props/"
BLD = "assets/buildings/"
ENT = "assets/tiles/cave_entrances/"

PORTAL = (42, 2)
PORTALS = {PORTAL: "The Golem Vault"}
ARRIVALS = {PORTAL: (42, 4)}

STAIR = [(42, 2), (42, 11)]
BINDING = (42, 21, 21, 10)         # the Binding Hall
RACKS = (11, 22, 9, 10)            # the Core Racks
RACKS_WAY = [(26, 22), (16, 22)]
WAYS = [[(28, 28), (22, 44)], [(42, 30), (42, 42)], [(56, 28), (62, 44)]]
WELL = (42, 66, 33, 28)            # the Well: the great round cavern
STORM = (42, 66, 23.0, 18.0, 0.4)  # the storm in the middle (cx, cy, rx, ry, phase); the pool's deep is its core
DAIS = (42, 66, 4.6, 3.8)          # the binding dais in the centre
BRIDGE_W = 5                       # four bridges, N S E W, wide enough to cross without thinking about it

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


def _floor(zone, x, y):
    if zone.base_layer[y][x] in ("shallow_water", "deep_water"):
        zone.set_tile(x, y, "dirt", "base")
        zone.collision_layer[y][x] = None


def build_storm_well_baked():
    zone = Tilemap(NAME, W, H, DESC)
    zone.is_cave = True
    zone.region = PARENT
    zone.fixed_spawns = False
    L = CaveLayout(zone, ARRIVALS[PORTAL])
    b = L.b
    tube(b, STAIR, 9.0, 10.0, ph=0.5)
    cavern(b, *BINDING, 0, 1.1)
    tube(b, RACKS_WAY, 10.0, 10.0, ph=1.5)
    cavern(b, *RACKS, 10, 2.1)
    for i, way in enumerate(WAYS):
        tube(b, way, 10.0, 11.0, ph=2.0 + 0.6 * i)
    cavern(b, *WELL, 0, 2.9)
    # the storm: a pool of bound storm-cloud (shallow edge walkable, deep core not), the dais and the bridges kept dry
    _apply_pools(zone, [STORM])
    cx, cy, rx, ry = DAIS
    for y in range(H):
        for x in range(W):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0:
                _floor(zone, x, y)
    half = BRIDGE_W // 2
    sx, sy = int(STORM[0]), int(STORM[1])
    reach_x, reach_y = int(STORM[2] + 2), int(STORM[3] + 2)
    for d in range(-reach_y, reach_y + 1):              # north and south bridges
        for o in range(-half, half + 1):
            _floor(zone, sx + o, sy + d)
    for d in range(-reach_x, reach_x + 1):              # east and west bridges
        for o in range(-half, half + 1):
            _floor(zone, sx + d, sy + o)
    for (px, py) in PORTALS:
        zone.collision_layer[py][px] = None
        L.mark("portal", px, py)
    fixed = []
    for (x, y, n) in [(DAIS[0], DAIS[1] + 1, "Stormwright Yrvald")]:
        p = _near_walkable(zone, x, y)
        assert p, (n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (fixed[0][0], fixed[0][1])
    zone.boss_positions = list(fixed)
    CHESTS[:] = []
    for (x, y) in [(6, 24), (16, 84), (70, 84), (66, 18)]:
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        CHESTS.append(p)
        L.mark("chest", *p)
    zone.add_subzone(NAME, 0, 0, W, H)
    rooms = {"The Binding Hall": (22, 0, 44, 34), "The Core Racks": (0, 8, 22, 28), "The Well": (0, 34, 84, 66)}
    ROOM_NAMES.clear()
    for rname, (x, y, w, h) in rooms.items():
        zone.add_subzone(rname, x, y, w, h)
        ROOM_NAMES[rname] = (x, y, w, h)
    dress(zone, L)
    L.finish(list(PORTALS) + list(BOSSES.values()) + CHESTS)
    return zone, L


def dress(zone, L):
    """The binding stones in a ring with the middle clear, the spare cores on the racks, thunder towers round the
    Well's rim between the ways in, and the gravity engine on the dais."""
    def P(name, x, y, h, where=SKP, **kw):
        p = _near_walkable(zone, x, y, rad=2)
        return L.prop(name, p[0], p[1], h, where=where, **kw) if p else L.skipped.append((name, x, y, "no floor"))
    P("ent_exit_crypt_stairs", PORTAL[0], PORTAL[1] + 2, 5, where=ENT, near_ok=True)
    bx, by, _rx, _ry = BINDING
    for k in range(6):                                   # the ring, skipping the stair at the top and the ways below
        a = math.radians(200 + k * 28)
        P("kh_chained_stone", int(bx + 16 * math.cos(a)), int(by + 7 * math.sin(a)) + 3, 5, where=BLD, solid="core")
    P("kh_lightning_core", RACKS[0] - 3, RACKS[1] - 2, 5, where=BLD, solid="core")
    P("kh_wind_core", RACKS[0] + 4, RACKS[1] + 5, 4, where=BLD, solid="core")
    P("kh_water_core", RACKS[0] - 5, RACKS[1] + 6, 4, where=BLD, solid="core")
    for (x, y) in [(16, 56), (68, 56), (14, 78), (70, 78), (42, 92)]:
        P("kh_thunder_tower", x, y, 7, where=BLD, solid="core")
    P("kh_gravity_engine", DAIS[0] + 5, DAIS[1] - 3, 4, where=BLD, solid="core")


def generate_storm_well():
    zone, _L = build_storm_well_baked()
    import os
    if os.path.isdir(BAKED) and any(os.path.exists(f"{BAKED}/ground_0_0.{e}") for e in ("jpg", "png", "webp")):
        register_baked(zone, BAKED)
    return zone


if __name__ == "__main__":
    z, L = build_storm_well_baked()
    walk = sum(1 for y in range(z.height) for x in range(z.width) if z.is_walkable(x, y))
    print(NAME, z.width, "x", z.height, "| walkable", walk, "| bosses", BOSSES, "| skipped", L.skipped)
