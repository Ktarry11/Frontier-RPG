"""
Hand-built The Golem Vault (84x100): the Kharad's vault under the Golem Fields on the Celestial Expanse, 50-51, the
first of its two floors (the second is the Storm-Well, tools/handbuilt_storm_well.py).

Kyle, 20 Nov 2026: "And we will have dungeons and caves too i hope", "remember that this is high level zone - so
multiple floors are okay", and "Also hallway simulators are boring and uninspired". So this is rooms, not corridors:
every space is a place with something in it, the ways between them are short and wide, and there's more than one way
through ("dont make them too hard to travel on with tiny paths and snag points").

The golems on the fields above were made here. You come down the stair into the Muster Hall, where the golems that were
never sent out still stand in their ranks, an army in rows with an aisle down the middle. Three ways lead down out of
it: west to the Wrights' Hall, the workshop, where Vault-Thane Brask keeps the list of every golem made; straight down to
the Assembly Floor, where the last golem stands half-built in its scaffold; and east to the Sleepers' Hall, where the
crews lay down on stone biers beside their work and are getting up. All three come together in the Deep Hall, and the
Deep Stair goes down from there to the storm.
A cave, not a dungeon: trash rolled from the cave's own table, the boss pinned by the map.

    the way in (42,2) <- the Golem Fields (on the map: tools/handbuilt_worldtree_celestial_expanse.py PORTALS)
    THE MUSTER HALL: the golems in their ranks
    THE WRIGHTS' HALL: west, the forge and the crane, Vault-Thane Brask (optional)
    THE ASSEMBLY FLOOR: the middle, the last golem in its scaffold
    THE SLEEPERS' HALL: east, the crews on their biers
    THE DEEP HALL: where the three ways meet, and the Deep Stair (42,97) -> the Storm-Well

You arrive two tiles inside either door.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

NAME = "The Golem Vault"
W, H = 84, 100
BAKED = "assets/tiles/sky/baked_golem_vault"
BAKED_DIR = BAKED
PARENT = "The Celestial Expanse"
DESC = ("The Kharad's vault under the Golem Fields, where the golems that were never sent out still stand in their "
        "ranks. The crews who built them lay down in the stone beside them, and they're getting up.")
SKP = "assets/tiles/sky/props/"
BLD = "assets/buildings/"
ENT = "assets/tiles/cave_entrances/"

PORTAL = (42, 2)
DOWN = (42, 97)
PORTALS = {PORTAL: "The Celestial Expanse", DOWN: "The Storm-Well"}
ARRIVALS = {PORTAL: (42, 4), DOWN: (42, 94)}

STAIR = [(42, 2), (42, 10)]
MUSTER = (42, 21, 31, 11)          # the Muster Hall
WRIGHTS = (17, 52, 13, 11)         # the Wrights' Hall: Vault-Thane Brask
ASSEMBLY = (42, 52, 10, 9)         # the Assembly Floor
SLEEPERS = (67, 52, 13, 11)        # the Sleepers' Hall
DEEP_HALL = (42, 81, 25, 9)        # where the three ways meet
WAYS = [[(24, 28), (18, 42)], [(42, 31), (42, 44)], [(60, 28), (66, 42)],          # down out of the Muster Hall
        [(19, 62), (28, 76)], [(42, 60), (42, 73)], [(65, 62), (56, 76)]]          # down into the Deep Hall
DEEP_STAIR = [(42, 88), (42, 97)]

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


def build_golem_vault_baked():
    zone = Tilemap(NAME, W, H, DESC)
    zone.is_cave = True
    zone.region = PARENT
    zone.fixed_spawns = False
    L = CaveLayout(zone, ARRIVALS[PORTAL])
    b = L.b
    tube(b, STAIR, 9.0, 10.0, ph=0.3)
    cavern(b, *MUSTER, 0, 0.6)
    cavern(b, *WRIGHTS, 8, 1.4)
    cavern(b, *ASSEMBLY, 0, 2.0)
    cavern(b, *SLEEPERS, -8, 2.6)
    cavern(b, *DEEP_HALL, 0, 3.1)
    for i, way in enumerate(WAYS):
        tube(b, way, 10.0, 10.0, ph=0.7 * i)
    tube(b, DEEP_STAIR, 9.0, 9.0, ph=3.6)
    for (px, py) in PORTALS:
        zone.collision_layer[py][px] = None
        L.mark("portal", px, py)
    fixed = []
    for (x, y, n) in [(WRIGHTS[0] + 2, WRIGHTS[1] + 2, "Vault-Thane Brask")]:
        p = _near_walkable(zone, x, y)
        assert p, (n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (fixed[0][0], fixed[0][1])
    zone.boss_positions = list(fixed)
    CHESTS[:] = []
    for (x, y) in [(8, 56), (76, 48), (42, 58), (62, 84)]:
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        CHESTS.append(p)
        L.mark("chest", *p)
    zone.add_subzone(NAME, 0, 0, W, H)
    rooms = {"The Muster Hall": (8, 0, 68, 36), "The Wrights' Hall": (0, 36, 30, 32),
             "The Assembly Floor": (30, 36, 24, 32), "The Sleepers' Hall": (54, 36, 30, 32),
             "The Deep Hall": (8, 68, 68, 32)}
    ROOM_NAMES.clear()
    for rname, (x, y, w, h) in rooms.items():
        zone.add_subzone(rname, x, y, w, h)
        ROOM_NAMES[rname] = (x, y, w, h)
    dress(zone, L)
    L.finish(list(PORTALS) + list(BOSSES.values()) + CHESTS)
    return zone, L


def dress(zone, L):
    """Each room has its own thing: the golems in ranks, the workshop, the half-built golem, the biers, the stair."""
    def P(name, x, y, h, where=SKP, **kw):
        p = _near_walkable(zone, x, y, rad=2)
        return L.prop(name, p[0], p[1], h, where=where, **kw) if p else L.skipped.append((name, x, y, "no floor"))
    P("ent_exit_crypt_stairs", PORTAL[0], PORTAL[1] + 2, 5, where=ENT, near_ok=True)
    # the Muster Hall: two ranks either side of the aisle, the standard at the head of it
    for x in (22, 30, 54, 62):
        for y in (15, 23):
            P("sk_dormant_golem", x, y, 5, solid="core")
    P("kh_standard", 42, 13, 5, where=BLD, solid="core")
    P("kh_lantern", 34, 12, 3, where=BLD, solid="core")
    P("kh_lantern", 50, 12, 3, where=BLD, solid="core")
    # the Wrights' Hall: the forge, the crane over the anvil, ore and a work table
    P("kh_forge", 10, 47, 8, where=BLD, solid="core")
    P("kh_crane", 25, 47, 7, where=BLD, solid="core")
    P("di_forge_anvil", 22, 57, 3, where=BLD, solid="core")
    P("kh_ore_pile", 9, 60, 3, where=BLD, solid="core")
    P("kh_table", 26, 61, 3, where=BLD, solid="core")
    # the Assembly Floor: the last golem, half-built in its scaffold
    P("kh_scaffold", 42, 53, 8, where=BLD, solid="core")
    P("sk_golem_core", 36, 57, 3, solid="core")
    # the Sleepers' Hall: the biers in two rows, urns at their heads
    for (x, y) in [(60, 47), (71, 47), (60, 59), (71, 59)]:
        P("kh_bench", x, y, 3, where=BLD, solid="core")
        P("kh_urn", x + 3, y - 1, 2, where=BLD, solid=False)
    P("kh_ancestor_statue", 79, 53, 6, where=BLD, solid="core")
    # the Deep Hall: braziers either side of the Deep Stair, obelisks where the ways come in
    P("sk_obelisk", 24, 80, 5, solid="core")
    P("sk_obelisk", 60, 80, 5, solid="core")
    P("kh_brazier", 36, 88, 4, where=BLD, solid="core")
    P("kh_brazier", 48, 88, 4, where=BLD, solid="core")
    P("ent_door_stairs_down", DOWN[0], DOWN[1] - 1, 5, where=ENT, near_ok=True)


def generate_golem_vault():
    zone, _L = build_golem_vault_baked()
    import os
    if os.path.isdir(BAKED) and any(os.path.exists(f"{BAKED}/ground_0_0.{e}") for e in ("jpg", "png", "webp")):
        register_baked(zone, BAKED)
    return zone


if __name__ == "__main__":
    z, L = build_golem_vault_baked()
    walk = sum(1 for y in range(z.height) for x in range(z.width) if z.is_walkable(x, y))
    print(NAME, z.width, "x", z.height, "| walkable", walk, "| bosses", BOSSES, "| skipped", L.skipped)
