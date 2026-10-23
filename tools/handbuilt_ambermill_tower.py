"""
Hand-built Ambermill Tower (150x140): the Dalaran waygate-tower above Ambermill, where Kirin Tor remnants and Forsaken mages still
fight over the library and the lab.  A CAVE-class mini-dungeon (random trash, pinned bosses).

ARCHETYPE: THE STACKED OCTAGONS.  A tower climbed one floor at a time: every floor is its own chamfered octagon hall, and a curved stair
tube carries you from one corner of a floor to the opposite corner of the next, so the route zig-zags up the map (south to north)
instead of running straight.  Each floor has one side alcove for a chest.  (Plague Depths = ladder, Broodspiral = spiral, the
Widow's Lair = comb of buds; this is the only vertical stack.)

  vestibule (portal)  ->  F1 The Reading Hall  ->  S1 west stair  ->  F2 The Archivist's Gallery (Magister Hawren L22)
        -> S2 east stair  ->  F3 The Alchemy Lab (Apothecary Helbrim L23)  -> S3 west stair  ->  F4 The Observatory (Archmage Atiesh L23)

HARD CONTRACTS (world/portal_manager.py): portal (75,128) <-> Silverpine South (138,90).  Cave exit adds +3 to the destination.
Prop rule (Kyle): less is more; logical for the room; a few centrepieces.
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import tube

UP = "assets/tiles/undercity/props/"
BAKED = "assets/tiles/ambermill_tower/baked"
W, H = 150, 140
PORTAL = (75, 128)

# (x0, y0, x1, y1, chamfer, name)
ROOMS = {
    "vestibule": (64, 122, 86, 133, 3, "The Waygate Vestibule"),
    "reading":   (46, 98, 104, 120, 6, "The Reading Hall"),
    "gallery":   (12, 60, 64, 86, 7, "The Archivist's Gallery"),
    "lab":       (68, 34, 136, 58, 7, "The Alchemy Lab"),
    "observ":    (34, 4, 116, 28, 9, "The Observatory"),
    "map_room":  (22, 102, 38, 114, 3, "The Map Room"),
    "scripto":   (112, 102, 130, 114, 3, "The Scriptorium"),
    "store":     (130, 36, 144, 50, 3, "The Reagent Store"),
    "orrery":    (118, 8, 134, 22, 3, "The Orrery"),
}
PATHS = {
    "s0":  ([(75, 122), (75, 120), (75, 118)], 5.0, 5.0),                    # vestibule -> hall
    "s1":  ([(54, 100), (44, 94), (36, 89), (36, 84)], 4.6, 4.6),             # hall NW corner -> gallery
    "s2":  ([(62, 70), (78, 66), (92, 62), (96, 56)], 4.6, 4.6),              # gallery E -> lab
    "s3":  ([(72, 40), (60, 36), (52, 32), (50, 26)], 4.6, 4.6),              # lab W -> observatory
    "map": ([(46, 108), (38, 108)], 3.4, 3.4),
    "scr": ([(104, 108), (112, 108)], 3.4, 3.4),
    "sto": ([(130, 44), (126, 44)], 3.4, 3.4),
    "orr": ([(116, 16), (120, 16)], 3.4, 3.4),
}
BOSSES = {}
CHESTS = []


def build_tower():
    zone = Tilemap("Ambermill Tower", W, H,
                   "A Dalaran waygate-tower: a library, a laboratory and an observatory, stacked and still arguing.")
    zone.is_cave = True
    zone.region = "Silverpine South"
    zone.fixed_spawns = False
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b
    for key, (x0, y0, x1, y1, ch, _n) in ROOMS.items():
        b.rect(x0, y0, x1, y1, chamfer=ch)
    for i, (key, (pts, w0, w1)) in enumerate(PATHS.items()):
        tube(b, pts, w0, w1, ph=0.3 + i * 0.7)
    px, py = PORTAL
    zone.collision_layer[py][px] = None
    L.mark("portal", px, py)

    bosses = [(38, 68, "Magister Hawren"), (102, 44, "Apothecary Helbrim"), (75, 14, "Archmage Atiesh")]
    for (x, y, n) in bosses:
        if not zone.is_walkable(x, y):
            raise AssertionError((n, x, y))
        L.mark("boss_marker", x, y)
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in bosses})
    zone.boss_position = (75, 14)
    zone.boss_positions = list(bosses)
    chests = [(26, 108), (126, 108), (139, 43), (129, 15)]
    for c in chests:
        if not zone.is_walkable(*c):
            raise AssertionError(("chest", c))
        L.mark("chest", *c)
    CHESTS[:] = chests

    zone.add_subzone("Ambermill Tower", 0, 0, W, H)
    for key, (x0, y0, x1, y1, ch, name) in ROOMS.items():
        zone.add_subzone(name, x0 - 1, y0 - 1, x1 - x0 + 2, y1 - y0 + 2)
    return zone, L


def finish(zone, L):
    return L.finish([PORTAL] + list(BOSSES.values()) + list(CHESTS))


def dress(zone, L):
    p = L.prop

    def U(name, cx, by, h, **kw):
        return p(name, cx, by, h, where=UP, **kw)
    # ---- vestibule: the waygate's lamps
    p("candelabra", 68, 126, 4, solid="core")
    p("candelabra", 82, 126, 4, solid="core")
    # ---- F1 Reading Hall: bookshelves along the north wall, reading desks, a rune pillar pair
    for x in (54, 62, 88, 96):
        p("bbc_bookshelf", x, 101, 5, solid="core")
    p("wizard_desk", 66, 110, 4, solid="core")
    p("wizard_desk", 84, 110, 4, solid="core")
    p("bbc_rune_pillar", 75, 104, 6, solid="core", avoid=1)
    p("broken_column", 52, 116, 4)
    p("broken_column", 98, 117, 4)
    p("bbc_bookshelf", 26, 104, 5, solid="core")                              # map room
    p("bbc_bookshelf", 120, 104, 5, solid="core")                             # scriptorium
    # ---- F2 Archivist's Gallery (Hawren): shelf-lined walls, a lectern, his desk
    for x in (20, 28, 46, 54):
        p("bbc_bookshelf", x, 63, 5, solid="core")
    U("uc_lectern", 38, 76, 4, solid="core", avoid=1)
    p("wizard_desk", 22, 80, 4, solid="core")
    p("bbc_candelabra", 54, 80, 4, solid="core")
    p("bbc_rune_pillar", 18, 74, 6, solid="core")
    p("bbc_rune_pillar", 58, 74, 6, solid="core")
    # ---- F3 Alchemy Lab (Helbrim): benches, stills and a cauldron's worth of trouble
    U("uc_alchemy_table", 80, 44, 4, solid="core")
    U("uc_alchemy_table", 124, 52, 4, solid="core")
    U("uc_copper_still", 118, 40, 5, solid="core")
    U("uc_plague_vat", 76, 54, 5, solid="core")
    U("uc_jar_shelf", 90, 38, 4, solid="core")
    U("uc_jar_shelf", 112, 38, 4, solid="core")
    U("uc_lectern", 102, 52, 4, solid="core")
    U("uc_crate_stack", 138, 48, 3, solid="core")                            # reagent store
    # ---- F4 Observatory (Atiesh): an arcane circle, a ring of rune pillars, void crystals
    p("bbc_summon_circle", 75, 18, 11, near_ok=True)
    for ox in (-24, 24):
        p("bbc_rune_pillar", 75 + ox, 22, 6, solid="core")
    p("bbc_candelabra", 44, 24, 4, solid="core")
    p("bbc_candelabra", 106, 24, 4, solid="core")
    p("rf_void_crystals", 126, 18, 4, solid="core")                           # the orrery
    p("bbc_bookshelf", 44, 9, 5, solid="core")
    p("bbc_bookshelf", 106, 9, 5, solid="core")
    return zone, L


def generate_ambermill_tower():
    zone, L = build_tower()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_tower_baked():
    zone, L = build_tower()
    dress(zone, L)
    finish(zone, L)
    return zone, L


if __name__ == "__main__":
    import sys
    from PIL import Image
    zone, L = build_tower_baked()
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
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/tower_shape.png"
    im.resize((W * 5, H * 5), Image.NEAREST).save(out)
    print(out, "skipped", list(L.skipped))
