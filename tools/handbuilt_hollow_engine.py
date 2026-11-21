"""
Hand-built The Hollow Engine (92x92): inside the greatest of the Dead Engines on the Fading Firmament, 58-59.

The engine is bigger than most towns, and it's been dead longer than anyone at Lastlight has been alive. Its core burned
out black, and something has been growing in the dark crystal ever since. Its last governor, a construct built to keep it
running, is still trying to start it.

Rooms round a dead heart, two ways round:
    the way in (46,2) <- the hatch at the engine's foot, on the Dead Engines
    THE INTAKE: a round hall where the engine drew the sky in
    THE GEAR GALLERIES: west and east, the great gears stopped mid-turn, the last governor in the east (optional)
    THE COOLANT VAULT: the bottom west, the coolant still standing dark in its basin
    THE GOVERNOR'S WORKS: the bottom east, where the engine's wardens kept their tools
    THE BLACK CORE: the heart, burned black, and what's grown in it

You arrive two tiles inside.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked, _apply_pools  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

NAME = "The Hollow Engine"
W, H = 92, 92
BAKED = "assets/tiles/sky/baked_hollow_engine"
BAKED_DIR = BAKED
PARENT = "The Fading Firmament"
DESC = ("Inside the greatest of the dead engines: the gears stopped mid-turn, the core burned black, and something "
        "grown in the dark crystal. The engine's last governor is still trying to start it.")
SKP = "assets/tiles/sky/props/"
BLD = "assets/buildings/"
ENT = "assets/tiles/cave_entrances/"

PORTAL = (46, 2)
PORTALS = {PORTAL: "The Fading Firmament"}
ARRIVALS = {PORTAL: (46, 4)}

STAIR = [(46, 2), (46, 12)]
INTAKE = (46, 20, 18, 9)            # the Intake
GEARS_W = (16, 44, 11, 13)          # the west gear gallery
GEARS_E = (76, 44, 11, 13)          # the east gear gallery: the last governor
COOLANT = (20, 76, 13, 10)          # the Coolant Vault
COOLANT_POOL = (20, 77, 7.0, 4.5, 0.2)
WORKS = (72, 76, 13, 10)            # the Governor's Works
CORE = (46, 54, 14, 12)             # the Black Core
WAYS = [[(32, 24), (20, 34)], [(60, 24), (72, 34)],                    # the Intake out to each gallery
        [(18, 56), (20, 68)], [(74, 56), (72, 68)],                    # each gallery down to the vault and the works
        [(32, 78), (60, 78)],                                          # along the bottom, vault to works
        [(26, 46), (34, 50)], [(66, 46), (58, 50)],                    # each gallery in to the core
        [(46, 66), (46, 74)]]                                          # the core down to the bottom way

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


def build_hollow_engine_baked():
    zone = Tilemap(NAME, W, H, DESC)
    zone.is_cave = True
    zone.region = PARENT
    zone.fixed_spawns = False
    L = CaveLayout(zone, ARRIVALS[PORTAL])
    b = L.b
    tube(b, STAIR, 9.0, 10.0, ph=0.3)
    cavern(b, *INTAKE, 0, 0.7)
    cavern(b, *GEARS_W, 5, 1.2)
    cavern(b, *GEARS_E, -5, 1.8)
    cavern(b, *COOLANT, 0, 2.4)
    cavern(b, *WORKS, 0, 3.0)
    cavern(b, *CORE, 0, 3.6)
    for i, way in enumerate(WAYS):
        tube(b, way, 10.0, 10.0, ph=0.4 + 0.6 * i)
    _apply_pools(zone, [COOLANT_POOL])
    for (px, py) in PORTALS:
        zone.collision_layer[py][px] = None
        L.mark("portal", px, py)
    fixed = []
    for (x, y, n) in [(CORE[0], CORE[1] + 2, "The Black Lattice"), (GEARS_E[0], GEARS_E[1] + 3, "The Last Governor")]:
        p = _near_walkable(zone, x, y)
        assert p, (n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (fixed[0][0], fixed[0][1])
    zone.boss_positions = list(fixed)
    CHESTS[:] = []
    for (x, y) in [(8, 44), (84, 48), (10, 82), (82, 80)]:
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        CHESTS.append(p)
        L.mark("chest", *p)
    zone.add_subzone(NAME, 0, 0, W, H)
    rooms = {"The Intake": (26, 0, 40, 30), "The West Gear Gallery": (0, 30, 30, 32),
             "The East Gear Gallery": (62, 30, 30, 32), "The Black Core": (30, 38, 32, 30),
             "The Coolant Vault": (0, 62, 40, 30), "The Governor's Works": (52, 62, 40, 30)}
    ROOM_NAMES.clear()
    for rname, (x, y, w, h) in rooms.items():
        zone.add_subzone(rname, x, y, w, h)
        ROOM_NAMES[rname] = (x, y, w, h)
    dress(zone, L)
    L.finish(list(PORTALS) + list(BOSSES.values()) + CHESTS)
    return zone, L


def dress(zone, L):
    """The intake's vents, the stopped gears, the coolant's pipes, the wardens' benches, the black heart."""
    def P(name, x, y, h, where=SKP, **kw):
        p = _near_walkable(zone, x, y, rad=2)
        return L.prop(name, p[0], p[1], h, where=where, **kw) if p else L.skipped.append((name, x, y, "no floor"))
    P("ent_exit_crypt_stairs", PORTAL[0], PORTAL[1] + 2, 5, where=ENT, near_ok=True)
    P("ae_light_vents", 36, 18, 4, where=BLD, solid="core")
    P("ae_light_vents", 56, 18, 4, where=BLD, solid="core")
    for (x, y) in ((12, 38), (20, 52), (80, 38), (72, 52)):
        P("sk_giant_gear", x, y, 5, solid="core")
    P("ae_gear_bank", 8, 48, 4, where=BLD, solid="core")
    P("ae_cooling_tower", 30, 72, 6, where=BLD, solid="core")
    P("ae_engine_bench", 66, 72, 3, where=BLD, solid="core")
    P("ae_gauge_panel", 80, 72, 4, where=BLD, solid="core")
    P("ff_dead_engine", CORE[0], CORE[1] - 8, 7, solid="core")
    P("ff_dim_shards", CORE[0] - 9, CORE[1] + 4, 2, solid=False)
    P("ff_dim_shards", CORE[0] + 9, CORE[1] + 4, 2, solid=False)


def generate_hollow_engine():
    zone, _L = build_hollow_engine_baked()
    import os
    if os.path.isdir(BAKED) and any(os.path.exists(f"{BAKED}/ground_0_0.{e}") for e in ("jpg", "png", "webp")):
        register_baked(zone, BAKED)
    return zone


if __name__ == "__main__":
    z, L = build_hollow_engine_baked()
    walk = sum(1 for y in range(z.height) for x in range(z.width) if z.is_walkable(x, y))
    print(NAME, z.width, "x", z.height, "| walkable", walk, "| bosses", BOSSES, "| skipped", L.skipped)
