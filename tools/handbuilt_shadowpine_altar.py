"""
Hand-built Shadowpine Altar (150x130): the curse-ritual caverns under Fenris Isle's western ridge.  A CAVE (random trash, pinned bosses).

ARCHETYPE: THE SERPENTINE PROCESSION.  The way up is one long S: from the mouth in the south the processional goes WEST to the Bone Circle,
doubles back EAST to the Moon Circle, then climbs NORTH-WEST to the Altar Ring at the top - and every circle can be skipped by one of two
loop-roads (an east shore road from the mouth to the Moon Circle, a long west road from the Bone Circle to the Ring), so the three circles
are a procession you may take whole or in part.  (Widow's Lair = a many-lobed comb, Ambermill = stacked towers, Shadowfang = stepped
castle; this is a snaking pilgrim's road with a ring at the top.)

  Bonewarden Aldric   L21  the Bone Circle  (west)     optional
  Curse Keeper Tael   L22  the Moon Circle  (east)     optional
  Alpha Fenris        L24  the Altar Ring   (north)    final boss; every route ends here
  chests: the bone nook (W), the shore nook (E), the Ring's gallery

TRASH IS RANDOM (hand-placed mobs only in full dungeons).  `zone.fixed_spawns = False`; bosses pinned.

HARD CONTRACTS (world/portal_manager.py): portal (75,115) <-> Fenris Isle (30,55); leaving a cave adds +3 to the destination, arrival into
the cave is 2 tiles north of the registered tile.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube, disc

CORR = "assets/tiles/ashenvale_corruption/props/"
SKULL = "assets/tiles/skull_rock/props/"
BAKED = "assets/tiles/shadowpine_altar/baked"
W, H = 150, 130
PORTAL = (75, 115)

ROOMS = {                         # key: (cx, cy, rx, ry, rot, phase, name)
    "mouth":  (75, 111, 11, 6, 0, 0.3, "The Altar Stair"),
    "bone":   (36, 88, 17, 12, 0.2, 1.1, "The Bone Circle"),
    "moon":   (112, 62, 18, 13, -0.2, 0.7, "The Moon Circle"),
    "ring":   (75, 18, 28, 13, 0, 1.9, "The Altar Ring"),
}
PATHS = {                         # name: (points, w0, w1)
    "stair":     ([(75, 108), (71, 101), (60, 96), (50, 93)], 5.0, 4.4),
    "first_turn": ([(38, 78), (46, 72), (66, 70), (90, 68), (98, 66)], 4.4, 4.4),
    "second_turn": ([(114, 49), (108, 41), (92, 34), (82, 29)], 4.4, 4.6),
    "east_shore": ([(81, 108), (98, 104), (116, 94), (124, 80), (122, 74)], 4.0, 4.0),
    "west_road":  ([(24, 82), (18, 64), (24, 46), (40, 34), (58, 26), (66, 24)], 4.0, 4.2),
}
NOOKS = {                         # (cx, cy, rx, ry, rot, phase, name)
    "bone_nook": (18, 56, 7, 6, 0, 0.5, "The Bone Nook"),
    "shore_nook": (124, 98, 7, 6, 0, 1.4, "The Shore Nook"),
    "gallery": (104, 20, 8, 6, 0, 2.3, "The Ring Gallery"),
}
BOSSES = {}
CHESTS = []


def build_altar():
    zone = Tilemap("Shadowpine Altar", W, H,
                   "Moonlit ritual caverns: a snaking road of bone circles climbs to the altar where Fenris was cursed.")
    zone.is_cave = True
    zone.region = "Fenris Isle"
    zone.fixed_spawns = False
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b
    for i, (key, (pts, w0, w1)) in enumerate(PATHS.items()):
        tube(b, pts, w0, w1, ph=0.5 + i * 0.9)
    for key, (cx, cy, rx, ry, rot, ph, _n) in ROOMS.items():
        cavern(b, cx, cy, rx, ry, rot, ph)
    for (cx, cy, rx, ry, rot, ph) in ((26, 98, 7, 5, 0, 0.4), (46, 82, 6, 5, 0, 1.3), (126, 70, 6, 5, 0, 2.0),
                                      (98, 52, 7, 5, 0, 0.8), (50, 20, 7, 5, 0, 1.6), (102, 14, 7, 4, 0, 0.2)):
        cavern(b, cx, cy, rx, ry, rot, ph)                      # lobes that make the circles read as caverns, not ovals
    for key, (cx, cy, rx, ry, rot, ph, _n) in NOOKS.items():
        cavern(b, cx, cy, rx, ry, rot, ph)
    # the Altar Ring: four short stubs of standing stone around the great altar, the walkway left open
    b.pillars((59, 91), (14, 22))
    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    bosses = [(32, 86, "Bonewarden Aldric"), (112, 58, "Curse Keeper Tael"), (75, 12, "Alpha Fenris")]
    for (x, y, n) in bosses:
        if not zone.is_walkable(x, y):
            raise AssertionError((n, x, y))
        L.mark("boss_marker", x, y)
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in bosses})
    zone.boss_position = (75, 12)
    zone.boss_positions = list(bosses)
    chests = [(18, 57), (124, 99), (104, 21)]
    for c in chests:
        if not zone.is_walkable(*c):
            raise AssertionError(("chest", c))
        L.mark("chest", *c)
    CHESTS[:] = chests

    zone.add_subzone("Shadowpine Altar", 0, 0, W, H)
    for key, (cx, cy, rx, ry, rot, ph, name) in ROOMS.items():
        zone.add_subzone(name, int(cx - rx - 2), int(cy - ry - 2), int(2 * rx + 4), int(2 * ry + 4))
    return zone, L


def finish(zone, L):
    return L.finish([PORTAL] + list(BOSSES.values()) + list(CHESTS))


def dress(zone, L):
    p = L.prop
    R = ROOMS
    # ---- the Altar Stair: a bone-altar either side of the climb
    mx, my = R["mouth"][:2]
    p("bbc_candelabra", mx - 8, my - 2, 4, solid="core")
    p("bbc_candelabra", mx + 8, my - 2, 4, solid="core")
    p("skull_pile", mx + 6, my + 3, 3, solid="core")
    # ---- the Bone Circle: a ritual circle at the centre, a bone heap, two sarcophagi against the rim
    bx, by = R["bone"][:2]
    p("ritual_circle", bx, by + 1, 9, near_ok=True)
    p("bone_pile", bx - 11, by - 5, 4, where=SKULL, solid="core")
    p("sarcophagus", bx + 11, by - 6, 3, solid="core")
    p("sarcophagus", bx - 12, by + 6, 3, solid="core")
    p("rf_skull_spears", bx + 12, by + 5, 4, solid="core")
    # ---- the Moon Circle: the moonstone ring and its keepers' altars
    qx, qy = R["moon"][:2]
    p("ritual_circle", qx, qy + 1, 9, near_ok=True)
    p("bbc_rune_pillar", qx - 12, qy - 5, 6, solid="core")
    p("bbc_rune_pillar", qx + 12, qy - 5, 6, solid="core")
    p("void_crystal_formation", qx + 13, qy + 6, 3, where=CORR, solid="core")
    p("bbc_candelabra", qx - 11, qy + 6, 4, solid="core")
    # ---- the Altar Ring: the great altar, candles at the compass points
    rx_, ry_ = R["ring"][:2]
    p("bbc_altar", rx_, ry_ + 3, 8, solid="core", avoid=2)
    p("bbc_banner", rx_ - 18, ry_ - 1, 6, solid="core")
    p("bbc_banner", rx_ + 18, ry_ - 1, 6, solid="core")
    p("bbc_candelabra", rx_ - 12, ry_ + 8, 4, solid="core")
    p("bbc_candelabra", rx_ + 12, ry_ + 8, 4, solid="core")
    # ---- the nooks: one piece each
    p("skull_pile", 17, 58, 3, solid="core")
    p("bone_pile", 122, 100, 4, where=SKULL, solid="core")
    p("bbc_candelabra", 102, 22, 4, solid="core")
    return zone, L


def generate_shadowpine_altar():
    zone, L = build_altar()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_altar_baked():
    zone, L = build_altar()
    dress(zone, L)
    finish(zone, L)
    return zone, L


if __name__ == "__main__":
    import sys
    from PIL import Image
    zone, L = build_altar_baked()
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
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/altar_shape.png"
    im.resize((W * 6, H * 6), Image.NEAREST).save(out)
    print(out, "skipped", [s for s in L.skipped][:20])
