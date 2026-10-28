"""
Hand-built Southern Thousand Needles (220x200). Levels 29-34.

ARCHETYPE: THE FLOOR AND THE TOPS.

The Aspen Wilderness is a descent - you arrive at the summit and the whole zone is the problem of getting
down. This is its exact inverse. You arrive on the canyon FLOOR, you can walk anywhere on it, and almost
everything worth reaching is standing on top of a mesa you cannot climb.

That makes the map two separate networks laid over each other:

    THE FLOOR    continuous, safe-ish, and where all the travel happens. You can get anywhere down here.
    THE TOPS     disconnected islands in the sky. Each one is flat, each one is walkable once you are on
                 it, and most of them have no way up at all.

They touch at a handful of RAMPS - old switchback ledges cut into a rim, the only places the two networks
join. Finding the ramp that serves the mesa you want is the zone's navigation, the way finding the chutes
was the Aspen Wilderness's.

TERRAIN IS HAND-PLACED, AND SLOPE-DERIVED ROCK IS CORRECT HERE.

The Aspen Wilderness had to abandon slope as the source of its cliffs: in dissected mountain country the
steepest ground is the WALLS OF THE DRAINAGES, so reading rock off slope drew a grey dead tree across the
map. Rock there became crest-ness instead.

A mesa is the opposite landform and it rehabilitates the rule completely. A mesa IS a flat top, a sheer
rim and a flat floor - so "rock is wherever the ground is too steep to stand on" describes it exactly, and
describes nothing else. The rim is the only steep ground that exists. Nothing else on this map has a
gradient worth mentioning.

So the elevation model here is not a landscape, it is a set of PLATEAUX: each mesa is an ellipse with a
flat top, a hard shoulder and a floor, placed by hand because where a mesa stands is a design decision in
a way that a drainage network is not. Twelve of them, deliberately unequal.

THE TOP FIFTH IS STILL ASPEN. Kyle: "the top 20% of the map will still be aspen, the bottom 80% will be
mesas and traditional." That band is the tail of the overlay, not a blend. You come down out of the
timber, and the rest of the map is Azeroth exactly as it always was - which is the point. The Aspen
Wilderness is a zone where everything is the Integration. This is a zone where the Integration is a thing
at your back, getting smaller.

HARD CONTRACT (world/portal_manager.py):
    (110, 4)   <-> The Aspen Wilderness (the pass, once it opens)
    (176, 100) <-> Freewind Post      (the three-mesa settlement, its own zone)
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob

KEY = "southern_needles"
#: Must match the name this zone is registered as in create_all_zones - portal_manager keys on zone.name.
NAME = "Southern Thousand Needles"
DESC = ("Mesa country, and the last of the aspen dying out along its northern edge. The floor goes "
        "everywhere. Almost nothing else does.")
REGION = "Kalimdor - Thousand Needles"
W, H = 220, 200
BAKED_DIR = "assets/tiles/southern_needles/baked"
IS_TOWN = False
BASE_TILE = "dirt"
SEED = 733

TAU = 2.0 * np.pi

#: The aspen band. Everything north of this is the tail of the Rockies overlay; everything south is
#: Azeroth. ASPEN_Y is where the seam sits - a hard line, not a gradient, same as the Aspen Wilderness's
#: northern seam but running the other way round (there, red dust meets leaf mould; here, leaf mould
#: meets red stone).
ASPEN_Y = 40.0

PORTALS = {(110, 4): "The Aspen Wilderness",
           #: ON TOP of Freewind North, at the head of its ramp. The settlement is up there, so the climb
           #: has to be the way in - a portal at the mesa's foot would make the only ground route into
           #: Freewind a thing you walk past.
           (168, 88): "Freewind Post"}
ARRIVALS = [(110, 10), (164, 90)]
START = (110, 11)


# =========================================================================================================
# THE MESAS. (cx, cy, rx, ry, height, name) - height is in elevation units; a taller mesa has a longer
# drop and a bigger shadow, nothing more.
#
# DELIBERATELY UNEQUAL, and the inequality is the content. Three big ones carry Freewind's neighbours and
# have ramps. Several middle ones are reachable and hold camps. Four are SHEER - no ramp, no way up, and
# whatever is on top of them stays there. A zone where every mesa is climbable is a zone with no skyline.
# =========================================================================================================
MESAS = [
    # --- the western group
    ("Redhoof Mesa",      42,  74, 26, 18, 13.5),
    ("The Anvil",         26, 126, 19, 15, 15.0),
    ("Lowshelf",          62, 150, 22, 13,  9.0),      # low and broad, the easiest top in the zone
    # --- the central spine, which is what you look down when you walk the floor
    ("Needle's Eye",     108,  86, 12, 11, 17.5),      # tall and thin, the zone's landmark
    ("Broadback",        104, 134, 28, 19, 12.0),
    ("The Sisters",      142,  60, 15, 12, 14.0),
    ("Lesser Sister",    164,  48, 10,  9, 13.0),
    # --- the eastern group, nearest Shimmering Flats
    ("Saltwatch",        188, 146, 20, 16, 11.5),
    ("The Thumb",        204,  52,  9,  8, 16.0),      # sheer on every side
    ("Dryhollow",        150, 172, 24, 15, 10.5),
    # --- FREEWIND'S THREE, as seen from THIS zone. The settlement itself is its own map; from down here
    #     they are a cluster of three tops close enough to span, which is the whole reason the tauren
    #     built where they did. ONLY FREEWIND NORTH HAS A RAMP. The other two are reached from inside the
    #     settlement by bridge, so the only ground route into Freewind is the one ramp - and that falls
    #     straight out of the terrain rather than being enforced anywhere.
    ("Freewind North",   168,  88, 14, 11, 14.5),
    ("Freewind South",   184, 116, 15, 12, 14.0),
    ("Freewind East",    196,  92, 10,  8, 15.0),
]

#: WHICH MESAS CAN BE CLIMBED. A ramp is an old switchback ledge cut into the rim, and it is the only
#: place the floor network and the top network touch. Everything not listed here is sheer: you can see
#: what is up there and you are not getting to it from the ground.
#: (mesa name, approach angle in turns clockwise from east, width)
RAMPS = [
    ("Redhoof Mesa",   0.62, 4.2),      # from the south-west, the long easy one
    ("Lowshelf",       0.10, 5.0),      # barely a ramp; the mesa is low enough to walk up
    ("Broadback",      0.80, 3.8),
    ("Saltwatch",      0.35, 3.6),
    ("The Anvil",      0.55, 3.2),      # steep and narrow
    ("Dryhollow",      0.95, 4.0),
    ("Freewind North", 0.45, 3.4),      # the only ground route into the settlement
]

#: THE DRY WASHES. Thousand Needles floods, once, hard, and then is dry for a year. These are the channels
#: that water cut and left - shallow, braided, and the only thing on the floor with any shape to it.
WASHES = [
    ([(6, 58), (40, 64), (76, 60), (112, 68), (150, 62), (188, 70), (216, 66)], 2.2, 6.0),
    ([(20, 104), (56, 112), (96, 106), (134, 116), (172, 108), (214, 114)], 2.0, 5.5),
    ([(10, 162), (48, 170), (88, 164), (126, 174), (168, 166), (212, 172)], 1.8, 5.0),
    ([(92, 56), (96, 96), (90, 130), (98, 164), (94, 196)], 1.6, 4.4),      # one running north-south
]


def smoothstep(a, b, x):
    t = np.clip((np.asarray(x, float) - a) / (b - a + 1e-9), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def _poly_dist(gx, gy, pts):
    d = None
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg = T.seg_dist(gx, gy, x0, y0, x1, y1)
        d = seg if d is None else np.minimum(d, seg)
    return d


def _mesa_r(gx, gy, cx, cy, rx, ry):
    """Normalised radius inside a mesa's footprint: <1 on top, 1 at the rim, >1 off it.

    Wobbled, because a mesa is an erosion remnant and erosion does not leave ellipses. The wobble is
    low-frequency and keyed to the angle, so the outline bulges and bays instead of going lumpy.
    """
    dx, dy = (np.asarray(gx, float) - cx) / rx, (np.asarray(gy, float) - cy) / ry
    a = np.arctan2(dy, dx)
    f = 1.0 + 0.11 * np.sin(2 * a + cx) + 0.07 * np.sin(3 * a + cy * 0.3) + 0.045 * np.sin(5 * a)
    return np.hypot(dx, dy) / f


def _ramp_cut(gx, gy):
    """>0 inside a ramp - a wedge running up one flank of a climbable mesa.

    The ramp is cut as a line from well outside the rim to the centre, so it crosses the rim ring at one
    place and nowhere else. That single crossing IS the join between the floor network and the top
    network, and there are only seven of them on the whole map.
    """
    out = np.full(np.shape(gx), -9.0)
    by_name = {m[0]: m for m in MESAS}
    for (name, turn, wide) in RAMPS:
        _, cx, cy, rx, ry, _ = by_name[name]
        ang = turn * TAU
        ex, ey = cx + np.cos(ang) * rx * 1.45, cy + np.sin(ang) * ry * 1.45
        d = T.seg_dist(gx, gy, ex, ey, cx, cy)
        out = np.maximum(out, (wide - d) + 0.5 * wob(gx * 0.8, gy * 0.8))
    return out


def elevation(gx, gy):
    """Floor at roughly zero; each mesa a flat plateau with a hard shoulder.

    NOT a landscape function. There is no regional gradient here and there should not be - Thousand
    Needles is a floor with towers standing on it, and inventing a slope across the whole map would put a
    tilt on the one terrain that is famously level.
    """
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    e = np.zeros(np.shape(gx), float)

    # THE DEEPEST MESA WINS, IT DOES NOT ADD.
    #
    # Four pairs of these footprints touch or overlap, and summing their heights put a spike at every
    # junction - two 14-high plateaux meeting produced a 28-high tower that is not a landform. Taking the
    # maximum is also what is physically true: where two mesas have not finished eroding apart you get one
    # plateau at the higher level with a saddle in it, which is a thing Thousand Needles is full of.
    plateau = np.zeros(np.shape(gx), float)
    for (_, cx, cy, rx, ry, h) in MESAS:
        r = _mesa_r(gx, gy, cx, cy, rx, ry)
        # flat top out to 0.86, then the whole drop happens in the last 0.14 of the radius. That narrow
        # band is what makes a mesa read as a mesa rather than a hill.
        plateau = np.maximum(plateau, h * smoothstep(1.0, 0.86, r))
    e = e + plateau

    # the floor: shallow dry washes, and a little dune relief so it is not a table
    e = e - 1.6 * np.clip(_wash(gx, gy), 0, None)
    e = e + 0.55 * wob(gx * 0.07, gy * 0.08) + 0.22 * wob(gx * 0.19, gy * 0.21)

    # the aspen band in the north sits a little higher - it is the toe of the range coming down
    e = e + 3.2 * smoothstep(ASPEN_Y + 14.0, 0.0, gy)
    return e


def _wash(gx, gy):
    out = np.full(np.shape(gx), -9.0)
    for (pts, depth, width) in WASHES:
        d = _poly_dist(gx, gy, pts) + 1.2 * wob(gx * 0.25, gy * 0.25)
        out = np.maximum(out, depth * np.exp(-np.clip(d, 0, None) ** 2 / (2.0 * width ** 2)))
    return out


def _slope(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    dx = (elevation(gx + 1.0, gy) - elevation(gx - 1.0, gy)) * 0.5
    dy = (elevation(gx, gy + 1.0) - elevation(gx, gy - 1.0)) * 0.5
    return np.hypot(dx, dy)


WALK_SLOPE = 0.95


ROADS = {
    # THE FLOOR ROADS, AND THEY GO AROUND THE MESAS.
    #
    # cliff_field forces any tile under a road to be walkable, which means a road routed across a mesa
    # footprint does not climb it - it punches a walkable SLOT straight through the rim and out the other
    # side. The first draft did exactly that to Needle's Eye and Broadback, and the shape preview showed
    # two mesas with a corridor cut through them. Every line here is checked against every mesa footprint
    # by tools/verify_southern_needles.py, because this is not the kind of mistake you see in a diff.
    "main":   ([(110, 12), (110, 44), (122, 66), (128, 92), (140, 130), (120, 158), (112, 182),
                (110, 196)], 3.0),
    "west":   ([(128, 92), (100, 102), (70, 104), (44, 100), (24, 104)], 2.4),
    "south":  ([(120, 158), (92, 168), (64, 172), (40, 176)], 2.2),
    "east":   ([(128, 92), (148, 98), (158, 108), (159, 128), (160, 150)], 2.4),
    "flats":  ([(160, 150), (182, 160), (206, 154), (216, 150)], 2.2),   # off toward Shimmering Flats
}


def road_dist(gx, gy):
    out = np.full(np.shape(gx), -9.0)
    for (pts, wide) in ROADS.values():
        d = _poly_dist(gx, gy, pts)
        out = np.maximum(out, wide * 0.5 - d)
    return out


def paved(gx, gy):
    return road_dist(gx, gy) > 0.0


def water_field(gx, gy):
    """Thousand Needles is dry. A few spring pools at mesa bases and nothing else."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    out = np.full(np.shape(gx), -9.0)
    for (cx, cy, r) in [(66, 92, 5.0), (150, 118, 4.2), (36, 148, 3.8), (196, 160, 4.0)]:
        d = np.hypot(gx - cx, gy - cy) + 0.8 * wob(gx * 0.7, gy * 0.7)
        out = np.maximum(out, r - d)
    return np.minimum(out, 1.2)


def deck_field(gx, gy):
    return np.full(np.shape(gx), -9.0)


def cliff_field(gx, gy):
    """ROCK IS SLOPE, and here that is simply true - see the module docstring.

    A mesa is a flat top, a sheer rim and a flat floor, so the only steep ground on this map IS the rim.
    Nothing else needs saying and nothing else should be added: every extra rock term would be a lie
    about a landform that is famously plain.
    """
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    rock = (_slope(gx, gy) - WALK_SLOPE) * 4.0

    # THE RAMPS CUT THROUGH THE RIM. Seven places on the whole map.
    #
    # The cut has to beat the rim it is cutting, and a rim's rock value scales with the MESA'S HEIGHT -
    # the whole drop happens inside 0.14 of the radius, so a tall mesa has a savage local slope. At a cut
    # strength of 6 the four shallow mesas opened and the three tall ones did not, which silently sealed
    # Freewind North: the settlement's only ground route, with the portal sitting on top of it. The cut is
    # now strong enough to beat any rim on the map, and the ramp's WIDTH is what controls how big the
    # opening is, which is the knob that should control it.
    rock = rock - 40.0 * np.clip(_ramp_cut(gx, gy), 0, None)

    edge = np.minimum.reduce([gx, W - gx, gy, H - gy])
    rock = np.maximum(rock, (4.0 - edge) * 2.0 + 0.3 * wob(gx * 1.3, gy * 1.3))
    # the arrival shelf in the north must stay open
    rock = np.where(gy < 14, np.minimum(rock, -0.6), rock)
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    rock = np.where(water_field(gx, gy) > -1.0, np.minimum(rock, -0.5), rock)
    return rock


def fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    w = water_field(gx, gy)
    return dict(cliff=cliff_field(gx, gy), shallow=w, deep=w - 3.0, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


SUBZONES = [
    ("The Last Stand", 0, 0, 220, 38),          # the aspen tail, and the name is the joke
    ("The Seam", 0, 34, 220, 12),
    ("Redhoof Mesa", 16, 56, 54, 38),
    ("The Anvil", 6, 110, 42, 34),
    ("Lowshelf", 40, 136, 46, 30),
    ("Needle's Eye", 94, 72, 30, 30),
    ("Broadback", 74, 114, 60, 42),
    ("The Sisters", 126, 38, 54, 34),
    ("Saltwatch", 164, 118, 44, 36),
    ("Dryhollow", 124, 156, 52, 32),
    ("The Windward Road", 150, 86, 56, 38),     # the floor under Freewind's mesas
]

BASE = {"hard": 0.40, "sand": 0.28, "clay": 0.20, "rock": 0.12}
PAINT = {}
COBBLE = []
NPC_POSITIONS = {}
CHESTS = []
FOREST = None


def _vegetate(L):
    """Placed by BAND, not scattered, and the bands do the zone's talking.

    North of the seam it is still aspen. Across the seam the aspen thins out over about ten tiles and
    stops - that thinning is the tail of the overlay and it should look deliberate rather than faded.
    The floor is desert scrub and red rock. The MESA TOPS ARE ALMOST BARE, and that is not an oversight:
    wind-scoured emptiness is what makes a top read as high, and a top with a forest on it reads as a
    hill.
    """
    z = L.z
    rng = np.random.default_rng(SEED)
    ASP = "assets/tiles/aspen/props/"
    SN = "assets/tiles/southern_needles/props/"
    A = lambda d, s: d + s + ".png"        # noqa: E731
    n = 0
    for _ in range(2600):
        x = int(rng.integers(3, W - 3))
        y = int(rng.integers(3, H - 3))
        if not z.is_walkable(x, y):
            continue
        e = float(np.asarray(elevation(np.array([[float(x)]]), np.array([[float(y)]]))).ravel()[0])
        on_top = e > 6.0
        r = rng.random()
        if y < ASPEN_Y - 6:                                  # the aspen tail
            if r < 0.50:
                nm = rng.choice(["asp_aspen_tall", "asp_aspen_clump", "asp_pine_tall", "asp_aspen_young"])
                if L.prop(A(ASP, nm), x, y, 6):
                    n += 1
        elif y < ASPEN_Y + 10:                               # the seam: thinning, and it looks chosen
            if r < 0.16:
                nm = rng.choice(["asp_aspen_young", "asp_snag_standing", "asp_dead_scrub"])
                if L.prop(A(ASP, nm), x, y, 4):
                    n += 1
        elif on_top:
            if r < 0.045:                                    # the tops are bare. That IS the design.
                nm = rng.choice(["sn_boulder_red", "sn_grass_tuft", "sn_cairn"])
                if L.prop(A(SN, nm), x, y, 3):
                    n += 1
        else:                                                # the floor
            if r < 0.20:
                nm = rng.choice(["sn_barrel_cactus", "sn_saguaro", "sn_thornbush", "sn_desert_sage",
                                 "sn_dead_shrub", "sn_grass_tuft", "sn_boulder_red", "sn_rock_spire",
                                 "sn_layered_stack", "sn_split_stone", "sn_stone_pile"])
                if L.prop(A(SN, nm), x, y, 4):
                    n += 1
    return n


def dress(L):
    return _vegetate(L)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_southern_needles():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/sn_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
