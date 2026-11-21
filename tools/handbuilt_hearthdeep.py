"""
Hand-built The Hearthdeep (96x100): the roots of the Threefold Forge on the Fading Firmament, 58-59, the first of its two
floors (the second is the Wellspring, tools/handbuilt_wellspring.py).

Kyle, 21 Nov 2026: "No Dungeons but some caves are fine", and, from the Expanse, "remember that this is high level zone
- so multiple floors are okay" and "hallway simulators are boring and uninspired". So: rooms, each with its own thing,
short wide ways between them, and more than one way through.

The Threefold Forge has three hearths on the surface, and each has its own flue going down into the stone, cut for the
people who worked it: the giants' flue is a stair of steps a man has to climb, the singers' gallery is cut with
wind-ways and perches, and the cutters' works are benches and racks at an Aetherian's height. The three come together
over the Confluence, where the deep anvil sits, and the Deep Stair goes on down to the Wellspring. The Ascendancy's
salvage crews are down here, cutting out what they can carry for the fleet.

    the way in (48,2) <- the Threefold Forge on the Firmament
    THE BELLOWS STAIR: down from the forge
    THE ASH HALL: a thousand years of the forge's ash, settled
    THE GIANTS' FLUE: west, the Kharad's hearth-shaft, steps cut for giants
    THE CUTTERS' WORKS: the middle, the Aetherians' benches, and the salvage crews' foreman (optional)
    THE SINGERS' GALLERY: east, the Veyr's wind-ways, cut into the walls
    THE CONFLUENCE: where the three flues meet over the deep anvil, and the Bellows-Warden that keeps the draught
    THE DEEP STAIR (48,97) -> the Wellspring

A cave, not a dungeon: trash rolled from the cave's own table, the bosses pinned by the map. You arrive two tiles inside
either door.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

NAME = "The Hearthdeep"
W, H = 96, 100
BAKED = "assets/tiles/sky/baked_hearthdeep"
BAKED_DIR = BAKED
PARENT = "The Fading Firmament"
DESC = ("The roots of the Threefold Forge: three flues cut down into the stone for three peoples, meeting over the deep "
        "anvil. The Ascendancy's salvage crews are cutting out whatever they can carry.")
SKP = "assets/tiles/sky/props/"
BLD = "assets/buildings/"
ENT = "assets/tiles/cave_entrances/"

PORTAL = (48, 2)
DOWN = (48, 97)
PORTALS = {PORTAL: "The Fading Firmament", DOWN: "The Wellspring"}
ARRIVALS = {PORTAL: (48, 4), DOWN: (48, 94)}

STAIR = [(48, 2), (48, 11)]
ASH_HALL = (48, 22, 30, 11)         # the Ash Hall
FLUE = (17, 52, 12, 14)             # the Giants' Flue, west
WORKS = (48, 50, 12, 9)             # the Cutters' Works, the middle
GALLERY = (79, 52, 12, 14)          # the Singers' Gallery, east
CONFLUENCE = (48, 80, 26, 10)       # the Confluence
WAYS = [[(26, 30), (19, 40)], [(48, 32), (48, 42)], [(70, 30), (77, 40)],          # down out of the Ash Hall
        [(20, 64), (30, 76)], [(48, 58), (48, 71)], [(76, 64), (66, 76)],          # down into the Confluence
        [(28, 50), (37, 50)], [(59, 50), (68, 50)]]                                 # across, works to each flue
DEEP_STAIR = [(48, 88), (48, 97)]

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


def build_hearthdeep_baked():
    zone = Tilemap(NAME, W, H, DESC)
    zone.is_cave = True
    zone.region = PARENT
    zone.fixed_spawns = False
    L = CaveLayout(zone, ARRIVALS[PORTAL])
    b = L.b
    tube(b, STAIR, 9.0, 10.0, ph=0.2)
    cavern(b, *ASH_HALL, 0, 0.5)
    cavern(b, *FLUE, 6, 1.3)
    cavern(b, *WORKS, 0, 1.9)
    cavern(b, *GALLERY, -6, 2.5)
    cavern(b, *CONFLUENCE, 0, 3.2)
    for i, way in enumerate(WAYS):
        tube(b, way, 10.0, 10.0, ph=0.6 * i)
    tube(b, DEEP_STAIR, 9.0, 9.0, ph=3.9)
    for (px, py) in PORTALS:
        zone.collision_layer[py][px] = None
        L.mark("portal", px, py)
    fixed = []
    for (x, y, n) in [(CONFLUENCE[0], CONFLUENCE[1] + 1, "The Bellows-Warden"),
                      (WORKS[0] + 3, WORKS[1] + 2, "Salvage-Master Corin Hask")]:
        p = _near_walkable(zone, x, y)
        assert p, (n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (fixed[0][0], fixed[0][1])
    zone.boss_positions = list(fixed)
    CHESTS[:] = []
    for (x, y) in [(8, 50), (88, 54), (26, 20), (70, 86)]:
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        CHESTS.append(p)
        L.mark("chest", *p)
    zone.add_subzone(NAME, 0, 0, W, H)
    rooms = {"The Bellows Stair": (36, 0, 24, 12), "The Ash Hall": (12, 12, 72, 24), "The Giants' Flue": (0, 36, 32, 32),
             "The Cutters' Works": (32, 36, 32, 32), "The Singers' Gallery": (64, 36, 32, 32),
             "The Confluence": (14, 68, 68, 32)}
    ROOM_NAMES.clear()
    for rname, (x, y, w, h) in rooms.items():
        zone.add_subzone(rname, x, y, w, h)
        ROOM_NAMES[rname] = (x, y, w, h)
    dress(zone, L)
    L.finish(list(PORTALS) + list(BOSSES.values()) + CHESTS)
    return zone, L


def dress(zone, L):
    """Each flue its own people's: the giants' steps and quarried blocks, the cutters' benches and the salvage crates,
    the singers' perches and wind-chimes; the ash in the hall; the deep anvil at the Confluence."""
    def P(name, x, y, h, where=SKP, **kw):
        p = _near_walkable(zone, x, y, rad=2)
        return L.prop(name, p[0], p[1], h, where=where, **kw) if p else L.skipped.append((name, x, y, "no floor"))
    P("ent_exit_crypt_stairs", PORTAL[0], PORTAL[1] + 2, 5, where=ENT, near_ok=True)
    # the Ash Hall: the cold hearth-mouths in the ceiling's shadow, ash heaped round them
    P("ff_burnt_crystal", 30, 20, 3, solid="core")
    P("ff_burnt_crystal", 66, 24, 3, solid="core")
    P("sk_cold_brazier", 40, 16, 3, solid="core")
    P("sk_cold_brazier", 56, 16, 3, solid="core")
    # the Giants' Flue: the steps, the blocks, a giant's lantern
    P("sk_giant_stair", 14, 46, 6, solid="core")
    P("kh_quarry_blocks", 22, 58, 4, where=BLD, solid="core")
    P("kh_lantern", 10, 60, 4, where=BLD, solid="core")
    # the Cutters' Works: the benches, the racks, the salvage crews' crates
    P("ae_engine_bench", 42, 46, 3, where=BLD, solid="core")
    P("ae_instrument_shelf", 54, 46, 4, where=BLD, solid="core")
    P("ae_crystal_crates", 40, 55, 3, where=BLD, solid="core")
    P("ff_salvage", 57, 55, 3, solid="core")
    # the Singers' Gallery: the perches and the chimes the wind used to sing through
    P("vy_watch_perch", 84, 46, 6, where=BLD, solid="core")
    P("vy_wind_chimes", 74, 58, 4, where=BLD, solid="core")
    P("vy_prayer_stone", 86, 60, 3, where=BLD, solid="core")
    # the Confluence: the deep anvil under the three flues' mouths
    P("kh_forge", CONFLUENCE[0], CONFLUENCE[1] - 6, 7, where=BLD, solid="core")
    P("ae_crystal_heater", CONFLUENCE[0] - 16, CONFLUENCE[1] + 2, 4, where=BLD, solid="core")
    P("vy_storm_altar", CONFLUENCE[0] + 16, CONFLUENCE[1] + 2, 4, where=BLD, solid="core")


def generate_hearthdeep():
    zone, _L = build_hearthdeep_baked()
    import os
    if os.path.isdir(BAKED) and any(os.path.exists(f"{BAKED}/ground_0_0.{e}") for e in ("jpg", "png", "webp")):
        register_baked(zone, BAKED)
    return zone


if __name__ == "__main__":
    z, L = build_hearthdeep_baked()
    walk = sum(1 for y in range(z.height) for x in range(z.width) if z.is_walkable(x, y))
    print(NAME, z.width, "x", z.height, "| walkable", walk, "| bosses", BOSSES, "| skipped", L.skipped)
