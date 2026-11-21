"""
Hand-built The Keel (96x96): the root of the Anchorfields' third anchor, inside the shelf, 53-54.

Kyle, 20 Nov 2026: "Also hallway simulators are boring and uninspired", "remember that this is high level zone", and
"aurelion is ancient, we are new". Every anchor has a keel: the crystal it's grown round, set into the shelf's stone a
thousand years ago with the anchor chain dropping through a shaft beside it to whatever holds the other end. The third
anchor is slipping because its keel is cracking, and the Anchor-Wardens who went down to tend it a long time ago never
came back up.

Rooms, each with its own thing, joined by short wide ways, and two ways round:
    the way in (42,2) <- the Slipping Anchor's door on the Anchorfields
    THE ROOT STAIR: down from the door into the first hall
    THE CHAINWELL: a round hall round the shaft, the anchor chain going down into open sky; walk the rim either way
    THE BALLAST HALLS: west, the great stone weights the wardens hung to keep the shelf level, and what lives in them
    THE WARDENS' LAST POST: east, the post the lost wardens held, and the captain who still holds it (optional)
    THE CRYSTAL KEEL: the bottom, the keel itself, cracked, and the thing grown out of the crack

You arrive two tiles inside.
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked, _apply_pools  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

NAME = "The Keel"
W, H = 96, 96
BAKED = "assets/tiles/sky/baked_keel"
BAKED_DIR = BAKED
PARENT = "The Anchorfields"
DESC = ("The root of the third anchor, inside the shelf: the crystal keel it was grown round a thousand years ago, "
        "cracking, and the chain going down past it into the open sky.")
SKP = "assets/tiles/sky/props/"
BLD = "assets/buildings/"
ENT = "assets/tiles/cave_entrances/"

PORTAL = (42, 2)
PORTALS = {PORTAL: "The Anchorfields"}
ARRIVALS = {PORTAL: (42, 4)}

STAIR = [(42, 2), (43, 22)]
CHAINWELL = (44, 32, 22, 14)        # the round hall
SHAFT = (44, 33, 11.0, 8.0, 0.6)    # the shaft in its middle: the pool's deep core is open sky
BALLAST = (14, 58, 11, 13)          # the Ballast Halls, west
POST = (78, 56, 11, 11)             # the Wardens' Last Post, east
KEEL = (46, 80, 21, 12)             # the Crystal Keel, the bottom
WAYS = [[(26, 40), (16, 48)], [(64, 40), (74, 48)], [(20, 70), (32, 78)], [(72, 66), (62, 76)],
        [(44, 46), (44, 68)]]

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


def build_keel_baked():
    zone = Tilemap(NAME, W, H, DESC)
    zone.is_cave = True
    zone.region = PARENT
    zone.fixed_spawns = False
    L = CaveLayout(zone, ARRIVALS[PORTAL])
    b = L.b
    tube(b, STAIR, 10.0, 11.0, ph=0.4)
    cavern(b, *CHAINWELL, 0, 0.9)
    cavern(b, *BALLAST, 6, 1.7)
    cavern(b, *POST, -6, 2.3)
    cavern(b, *KEEL, 0, 3.0)
    for i, way in enumerate(WAYS):
        tube(b, way, 10.0, 10.0, ph=0.5 + 0.6 * i)
    # the shaft: the deep core is open sky (not walkable), the shallow edge a walkable lip
    _apply_pools(zone, [SHAFT])
    for (px, py) in PORTALS:
        zone.collision_layer[py][px] = None
        L.mark("portal", px, py)
    fixed = []
    for (x, y, n) in [(KEEL[0], KEEL[1] + 2, "The Keel-Heart"), (POST[0] + 2, POST[1], "Warden-Captain Oris Hale")]:
        p = _near_walkable(zone, x, y)
        assert p, (n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (fixed[0][0], fixed[0][1])
    zone.boss_positions = list(fixed)
    CHESTS[:] = []
    for (x, y) in [(6, 64), (86, 52), (24, 30), (70, 86)]:
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        CHESTS.append(p)
        L.mark("chest", *p)
    zone.add_subzone(NAME, 0, 0, W, H)
    rooms = {"The Root Stair": (32, 0, 22, 16), "The Chainwell": (18, 16, 54, 32), "The Ballast Halls": (0, 44, 32, 30),
             "The Wardens' Last Post": (60, 42, 36, 28), "The Crystal Keel": (20, 66, 54, 30)}
    ROOM_NAMES.clear()
    for rname, (x, y, w, h) in rooms.items():
        zone.add_subzone(rname, x, y, w, h)
        ROOM_NAMES[rname] = (x, y, w, h)
    dress(zone, L)
    L.finish(list(PORTALS) + list(BOSSES.values()) + CHESTS)
    return zone, L


def dress(zone, L):
    """The anchor chain's hoists round the shaft, the ballast stones, the lost wardens' post, the keel's crystal."""
    def P(name, x, y, h, where=SKP, **kw):
        p = _near_walkable(zone, x, y, rad=2)
        return L.prop(name, p[0], p[1], h, where=where, **kw) if p else L.skipped.append((name, x, y, "no floor"))
    P("ent_exit_crypt_stairs", PORTAL[0], PORTAL[1] + 2, 5, where=ENT, near_ok=True)
    sx, sy = SHAFT[0], SHAFT[1]
    for a in (210, 330):                                  # the chain's hoists either side of the shaft
        P("ae_chain_hoist", int(sx + 17 * math.cos(math.radians(a))), int(sy + 12 * math.sin(math.radians(a))) + 2, 5,
          where=BLD, solid="core")
    P("kh_chain_anchor", sx - 16, sy + 6, 4, where=BLD, solid="core")
    P("kh_chain_anchor", sx + 16, sy + 6, 4, where=BLD, solid="core")
    # the Ballast Halls: the great weights in rows, the aisle between them clear
    for (x, y) in [(8, 52), (20, 52), (8, 64), (20, 64)]:
        P("kh_quarry_blocks", x, y, 4, where=BLD, solid="core")
    # the Wardens' Last Post: their tents and crates, a standard still up
    P("ae_soldier_tent", POST[0] - 5, POST[1] - 4, 5, where=BLD, solid="core")
    P("ae_supply_crates", POST[0] + 6, POST[1] + 5, 3, where=BLD, solid="core")
    P("ae_banner", POST[0] - 6, POST[1] + 5, 5, where=BLD, solid="core")
    # the Crystal Keel: the keel itself behind the boss, cracked, and the light coming out of the crack
    P("kh_lightning_core", KEEL[0], KEEL[1] - 6, 7, where=BLD, solid="core")
    P("sk_crystal_blue", KEEL[0] - 14, KEEL[1] + 2, 4, solid="core")
    P("sk_crystal_blue", KEEL[0] + 14, KEEL[1] + 2, 4, solid="core")
    P("ae_failing_pylon", KEEL[0] + 16, KEEL[1] - 6, 7, where=BLD, solid="core")


def generate_keel():
    zone, _L = build_keel_baked()
    import os
    if os.path.isdir(BAKED) and any(os.path.exists(f"{BAKED}/ground_0_0.{e}") for e in ("jpg", "png", "webp")):
        register_baked(zone, BAKED)
    return zone


if __name__ == "__main__":
    z, L = build_keel_baked()
    walk = sum(1 for y in range(z.height) for x in range(z.width) if z.is_walkable(x, y))
    print(NAME, z.width, "x", z.height, "| walkable", walk, "| bosses", BOSSES, "| skipped", L.skipped)
