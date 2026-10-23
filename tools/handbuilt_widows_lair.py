"""
Hand-built Widow's Lair (130x116): the spider hive under the Skittering Dark in Silverpine North.  A CAVE (random trash, pinned bosses).

ARCHETYPE: THE HIVE CLUSTER.  A round Web Heart sits in the middle of the map and the rest of the warren buds off it like cells
of a comb: two big lair-buds either side of the hub, two small larder-buds behind them, two nursery-buds at the back and the
Matriarch's Spire at the top.  The short path is straight up the hub's north neck; the two side lairs are optional bosses, and the
nurseries link them to the Spire the long way round, so every bud has a second way out.  (VoT's Den = a lake loop, Skull Rock = a
single gorge; this is a many-lobed comb.)

  Broodmother Silka    L17   west lair   (Silka's Egg Chamber)    reached from the hub's west neck
  Weaver Skitter       L18   east lair   (Skitter's Lair)         reached from the hub's east neck
  Matriarch Velaxis    L19   north spire (Matriarch's Spire)      the final boss; short path = hub -> north neck
  chests: the Larder (W), the Husk Pit (E), the Spire

TRASH IS RANDOM (Kyle 2026-10-22: "hand-placed mobs only in full dungeons").  `zone.fixed_spawns = False`; bosses pinned.

HARD CONTRACTS (world/portal_manager.py): portal (65,106) <-> Silverpine North (150,84); leaving a cave adds +3 to the
destination, arrival into the cave is 2 tiles north of the registered tile.
"""
import os

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

DEN = "assets/tiles/the_den/props/"
BAKED = "assets/tiles/widows_lair/baked"
W, H = 130, 116
PORTAL = (65, 106)

ROOMS = {
    "mouth":   (65, 100, 15, 8, 0, 0.3, "The Silk Mouth"),
    "hub":     (65, 68, 19, 15, 0, 1.1, "The Web Heart"),
    "silka":   (28, 74, 16, 12, 12, 2.0, "Silka's Egg Chamber"),
    "skitter": (102, 74, 16, 12, -12, 0.6, "Skitter's Lair"),
    "larder":  (19, 47, 9, 7, 0, 1.4, "The Larder"),
    "pit":     (111, 47, 9, 7, 0, 2.3, "The Husk Pit"),
    "nurs_w":  (31, 24, 11, 8, 0, 0.9, "The West Nursery"),
    "nurs_e":  (99, 24, 11, 8, 0, 1.8, "The East Nursery"),
    "spire":   (65, 20, 24, 13, 0, 0.5, "Matriarch's Spire"),
}
PATHS = {
    "neck_mouth": ([(65, 96), (65, 90), (64, 83)], 6.0, 6.0),
    "neck_w":     ([(48, 70), (42, 72), (38, 73)], 5.0, 5.0),
    "neck_e":     ([(82, 70), (88, 72), (92, 73)], 5.0, 5.0),
    "neck_n":     ([(65, 54), (61, 47), (68, 40), (65, 33)], 5.0, 5.0),
    "w_up":       ([(24, 63), (21, 57), (19, 53)], 3.6, 3.6),
    "e_up":       ([(106, 63), (109, 57), (111, 53)], 3.6, 3.6),
    "w_nurs":     ([(19, 41), (23, 34), (29, 31)], 3.6, 3.6),
    "e_nurs":     ([(111, 41), (107, 34), (101, 31)], 3.6, 3.6),
    "w_spire":    ([(38, 24), (46, 22), (52, 21)], 3.6, 3.6),
    "e_spire":    ([(92, 24), (84, 22), (78, 21)], 3.6, 3.6),
}
BOSSES = {}
CHESTS = []


def build_widows():
    zone = Tilemap("Widow's Lair", W, H,
                   "A hive of silk and broken ribs: spiders bud off one great web-heart, and a matriarch waits at the top.")
    zone.is_cave = True
    zone.region = "Silverpine North"
    zone.fixed_spawns = False
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b
    for i, (key, (pts, w0, w1)) in enumerate(PATHS.items()):
        tube(b, pts, w0, w1, ph=0.4 + i * 0.8)
    for key, (cx, cy, rx, ry, rot, ph, _n) in ROOMS.items():
        cavern(b, cx, cy, rx, ry, rot, ph)
    # side lobes that make the hub and spire read as many-celled
    for (cx, cy, rx, ry, rot, ph) in ((52, 78, 7, 6, 0, 0.2), (78, 78, 7, 6, 0, 1.0), (65, 56, 8, 5, 0, 2.2),
                                      (46, 18, 8, 6, 0, 1.4), (84, 18, 8, 6, 0, 2.6), (65, 9, 11, 4, 0, 0.9)):
        cavern(b, cx, cy, rx, ry, rot, ph)
    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    bosses = [(28, 70, "Broodmother Silka"), (102, 70, "Weaver Skitter"), (65, 16, "Matriarch Velaxis")]
    for (x, y, n) in bosses:
        if not zone.is_walkable(x, y):
            raise AssertionError((n, x, y))
        L.mark("boss_marker", x, y)
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in bosses})
    zone.boss_position = (65, 16)
    zone.boss_positions = list(bosses)
    chests = [(17, 47), (113, 47), (79, 13)]
    for c in chests:
        if not zone.is_walkable(*c):
            raise AssertionError(("chest", c))
        L.mark("chest", *c)
    CHESTS[:] = chests

    zone.add_subzone("Widow's Lair", 0, 0, W, H)
    for key, (cx, cy, rx, ry, rot, ph, name) in ROOMS.items():
        zone.add_subzone(name, int(cx - rx - 2), int(cy - ry - 2), int(2 * rx + 4), int(2 * ry + 4))
    return zone, L


def finish(zone, L):
    targets = [PORTAL] + list(BOSSES.values()) + list(CHESTS)
    return L.finish(targets)


def dress(zone, L):
    p = L.prop
    R = ROOMS

    def D(name, cx, by, h, **kw):
        kw.setdefault("where", DEN)
        return p(name, cx, by, h, **kw)
    # ---- the Silk Mouth: a curtain across the throat, a few husks of the unlucky
    mx, my = R["mouth"][:2]
    p("web_curtain", 65, 93, 5, near_ok=True)
    p("spider_husk", mx - 8, my + 2, 4)
    p("web_tangle", mx + 9, my - 2, 3)
    p("cocoon_victim", mx - 4, my - 4, 5, solid="core")
    # ---- the Web Heart: a great web boulder at the centre, cocoons around it
    hx, hy = R["hub"][:2]
    p("den_web_boulder", hx, hy - 2, 7, solid="core", avoid=1)
    p("den_web_cocoon", hx - 12, hy + 3, 5, solid="core")
    p("den_web_cocoon", hx + 12, hy + 4, 5, solid="core")
    p("cocoon_victim", hx - 7, hy - 9, 5, solid="core")
    p("web_tangle", hx + 8, hy + 9, 3)
    p("den_glow_mushrooms", hx - 15, hy - 3, 3)
    # ---- Silka's Egg Chamber: eggs and shell, a nest mound under her
    sx, sy = R["silka"][:2]
    p("den_egg_cluster", sx - 9, sy - 4, 5, solid="core")
    p("den_egg_cluster", sx + 9, sy + 3, 5, solid="core")
    p("den_eggshell_pile", sx - 3, sy + 8, 3)
    p("den_nest_mound", sx, sy - 1, 5, solid="core", avoid=1)
    p("spider_husk", sx + 10, sy - 7, 4)
    # ---- Skitter's Lair: the weaver's hanging larder
    kx, ky = R["skitter"][:2]
    p("den_web_wall", kx, ky - 9, 6, solid="core")
    p("cocoon_victim", kx - 10, ky + 4, 5, solid="core")
    p("cocoon_victim", kx + 8, ky - 5, 5, solid="core")
    p("web_tangle", kx + 11, ky + 7, 3)
    p("den_leg_bones", kx - 4, ky + 9, 3)
    # ---- the larder / husk pit: one centrepiece each
    p("skull_pile", R["larder"][0] + 2, R["larder"][1] + 3, 3, solid="core")
    p("cocoon_victim", R["larder"][0] + 4, R["larder"][1] + 2, 4, solid="core")
    p("den_chitin_husk", R["pit"][0] - 2, R["pit"][1] + 3, 3, solid="core")
    p("spider_husk", R["pit"][0] + 4, R["pit"][1] - 3, 4)
    # ---- nurseries: eggs only
    for key in ("nurs_w", "nurs_e"):
        nx, ny = R[key][:2]
        p("den_egg_cluster", nx - 3, ny + 1, 5, solid="core")
        p("den_eggshell_pile", nx + 4, ny + 3, 3)
    # ---- Matriarch's Spire: her nest, a ring of cocoons
    vx, vy = R["spire"][:2]
    p("spider_nest", vx, vy - 8, 9, solid="core", avoid=1)
    p("den_web_cocoon", vx - 15, vy + 3, 5, solid="core")
    p("den_web_cocoon", vx + 15, vy + 3, 5, solid="core")
    p("cocoon_victim", vx - 9, vy + 8, 5, solid="core")
    p("skull_pile", vx + 11, vy + 8, 3)
    p("web_curtain", 65, 35, 5, near_ok=True)
    return zone, L


def generate_widows_lair():
    zone, L = build_widows()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_widows_baked():
    zone, L = build_widows()
    dress(zone, L)
    finish(zone, L)
    return zone, L


if __name__ == "__main__":
    import sys
    from PIL import Image
    zone, L = build_widows_baked()
    im = Image.new("RGB", (W, H), (30, 28, 34))
    for y in range(H):
        for x in range(W):
            if zone.is_walkable(x, y):
                im.putpixel((x, y), (120, 150, 110))
    for (x, y) in BOSSES.values():
        im.putpixel((x, y), (255, 60, 60))
    for (x, y) in CHESTS:
        im.putpixel((x, y), (255, 220, 60))
    im.putpixel(PORTAL, (255, 0, 255))
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/widows_shape.png"
    im.resize((W * 6, H * 6), Image.NEAREST).save(out)
    print(out, "skipped", [s for s in L.skipped][:20])
