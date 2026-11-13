"""
Hand-built The Shimmering Flats (200x180). Levels 35-40.

ARCHETYPE: THE OPEN GROUND.

Every zone in this region so far is sorted by something with a direction in it - the Aspen Wilderness by
ALTITUDE, Southern Needles by DISTANCE FROM THE PASS, Rocky Pass by THE CLIMB. A salt pan is dead flat and
has none of those, and that is the design problem rather than an accident of the terrain. A zone with no
gradient and no walls has nothing to sort itself by.

So the axis is DISTANCE OUT ONTO THE PAN. The rim is where you walk; the pan is where you don't. The
silithids have the pan, and the ladder is how far out you are willing to go - 35 on the shore, 40 at the
far side. West to east and nothing else.

That also gives this zone the one thing none of the others have: NO COVER AND NO LINE. Everywhere else in
the game funnels you down something. Out here you can see what is coming from a very long way off, and it
can see you, and there is nothing in between.

THE HIVES ARE THE LANDMARKS, because a salt pan has none. Mounds erupting through the crust, visible
across the whole map, and the only navigation the zone offers. They are also the only steep ground out
there, which means SLOPE-DERIVED ROCK WORKS HERE for the second time in this region and for a different
reason: Southern Needles earns it because a mesa is a flat top and a sheer rim; the Flats earns it because
a hive mound is a cone standing on a table. Everything else on this map is level.

THE SILITHIDS WRECKED IT, AND THE INTEGRATION DID NOT. Three earlier docs call this zone "largely
untouched" - the region's best contrast, the one place that proves what the rest used to be. Kyle:
"lets do a mixture. We can have the silithids fuuuuucked the place up. So salt flats are still there but
its infested with silithids more."

That reconciles the idea rather than breaking it. Nothing from Earth is here, no mountain came down on it,
and the standing region rule holds. What ruined it is AZEROTH'S OWN. The zone still proves what the region
used to be; it also proves Azeroth could ruin things without any help.

THE MIRAGE RACEWAY is the mixture made visible. The track is still legible as a ring on the pan, the
stands are down, the pit camps are overrun. It is the best landmark on a map that has none, and the
clearest statement of what this place was for. Goblins and gnomes are Azeroth - the no-Earth rule is not
strained by a racetrack.

HARD CONTRACT (world/portal_manager.py):
    (6, 40)   <-> The Aspen Wilderness      - the high way in, where the range bleeds east
    (6, 132)  <-> Southern Thousand Needles - the road, which that zone already carved and left hanging
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob

KEY = "shimmering_flats"
#: Must match the name registered in create_all_zones - portal_manager keys on zone.name.
NAME = "The Shimmering Flats"
DESC = ("A salt pan the size of a sea, and the only thing that ever came out of it on purpose was a "
        "racetrack. Something underneath it has been busy.")
REGION = "Kalimdor - Thousand Needles"
W, H = 200, 180
BAKED_DIR = "assets/tiles/shimmering_flats/baked"
IS_TOWN = False
BASE_TILE = "sand"
SEED = 3540

TAU = 2.0 * np.pi

PORTALS = {(6, 40): "The Aspen Wilderness",
           (6, 132): "Southern Thousand Needles"}
ARRIVALS = [(12, 40), (12, 132)]
START = (12, 132)

# =========================================================================================================
# THE SHORE. Mesa remnants dying into the pan along the western rim - the tail of Southern Needles, not a
# feature of its own. They are small and low on purpose: the moment they get interesting they start
# competing with the hives, and the hives have to own the skyline.
# =========================================================================================================
STACKS = [
    ("North Head", 20, 28, 16, 12, 9.0),
    ("The Landing", 26, 74, 13, 11, 7.0),
    ("Saltwatch Head", 18, 118, 15, 13, 8.5),
    ("South Head", 30, 162, 14, 11, 7.5),
    ("The Last Stack", 58, 96, 9, 8, 6.0),      # one alone, well out. The shore's last word.
]

# =========================================================================================================
# THE HIVES. (name, cx, cy, radius, height, tunnel turn) - cones standing on a table.
#
# THEY GET BIGGER AND OLDER GOING EAST, which is the level ladder made into terrain: the first one you can
# see from the shore, the last one you have to cross the whole pan to reach. The tunnel turn is which
# flank the way in is on, as a fraction of a turn - the cut crosses the mound's flank in exactly one
# place, the same trick the mesa ramps use in Southern Needles.
# =========================================================================================================
HIVES = [
    ("The First Mound",  86,  62, 11,  7.0, 0.52),
    ("Crustbreak",       92, 140, 13,  8.5, 0.08),
    ("The Pit Mound",   132, 104, 15, 10.0, 0.60),
    ("Highcast",        152,  46, 16, 11.5, 0.30),
    ("The Deep Mound",  160, 118, 18, 14.0, 0.55),    # the oldest, and the far side of the pan
]

#: THE RIM. Mountains all the way round, which Kyle asked for to stop the zone being a box - "We can
#: put mountains around the edge of the flat to give it shape, so it's not a box."
#:
#: It is also why the salt is here. A pan forms in a CLOSED BASIN: water runs in, cannot run out, and
#: leaves its load behind when it evaporates. A salt flat with an open horizon on four sides is a salt
#: flat that should have drained. So the rim is not decoration bolted onto the edge - it is the reason
#: the zone exists, and the first version not having it was a hole in the premise as well as in the
#: shape.
RIM_H = 24.0
RIM_W = 23.0

#: The only ways through it. (edge point, inward point, width) - each cuts a notch in the rim, the same
#: trick the hive tunnels and the Southern Needles mesa ramps use.
#:
#: THE SOUTH PASS GOES NOWHERE YET, deliberately. Kyle: "we need a mountain pass in the south where
#: it'll go towards tanaris eventually." It is carved, it is walkable, and it has no portal registered
#: on it until Tanaris exists - which is exactly what Southern Needles did with the road named "flats"
#: that pointed at this zone for two zones before there was anything on the far side of it.
GATES = [
    ((0, 40), (36, 46), 4.5),       # the Aspen Wilderness, high and north
    ((0, 132), (38, 128), 5.0),     # the Southern Needles road
    ((120, 180), (116, 148), 5.0),  # THE SOUTH PASS, toward Tanaris
]
#: Where that pass meets the map edge. Unregistered on purpose - see above.
TANARIS_PASS = (120, 176)

#: The Mirage Raceway. A closed ring, still legible as a track because salt keeps a surface for years.
RACEWAY = [(104, 34), (124, 26), (144, 30), (152, 44), (148, 62), (130, 72), (110, 70), (100, 56),
           (104, 34)]


def smoothstep(a, b, x):
    t = np.clip((np.asarray(x, float) - a) / (b - a + 1e-9), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def _poly_dist(gx, gy, pts):
    d = None
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg = T.seg_dist(gx, gy, x0, y0, x1, y1)
        d = seg if d is None else np.minimum(d, seg)
    return d


def _stack_r(gx, gy, cx, cy, rx, ry):
    """Normalised radius inside a stack's footprint - wobbled, because erosion leaves no ellipses."""
    dx, dy = (np.asarray(gx, float) - cx) / rx, (np.asarray(gy, float) - cy) / ry
    a = np.arctan2(dy, dx)
    f = 1.0 + 0.12 * np.sin(2 * a + cx) + 0.07 * np.sin(3 * a + cy * 0.3) + 0.05 * np.sin(5 * a)
    return np.hypot(dx, dy) / f


def _gate_cut(gx, gy):
    """>0 inside a gate - a notch cut through the mountain rim."""
    out = np.full(np.shape(gx), -9.0)
    for ((ex, ey), (ix, iy), wide) in GATES:
        d = T.seg_dist(gx, gy, ex, ey, ix, iy)
        out = np.maximum(out, (wide - d) + 0.8 * wob(gx * 0.6, gy * 0.6))
    return out


def _tunnel_cut(gx, gy):
    """>0 inside a hive's tunnel mouth - a wedge up one flank, crossing the cone in one place.

    Without this every mound is a sealed cone and the hives are scenery. With it each one has exactly one
    way in, which is the encounter.
    """
    out = np.full(np.shape(gx), -9.0)
    for (_n, cx, cy, r, _h, turn) in HIVES:
        ang = turn * TAU
        ex, ey = cx + np.cos(ang) * r * 1.6, cy + np.sin(ang) * r * 1.6
        d = T.seg_dist(gx, gy, ex, ey, cx, cy)
        out = np.maximum(out, (2.6 - d) + 0.5 * wob(gx * 0.8, gy * 0.8))
    return out


def elevation(gx, gy):
    """The pan is zero. The shore stands above it; the hives stand on it; the middle sags.

    THERE IS A REGIONAL GRADIENT HERE and that is the opposite of the call made in Southern Needles,
    where inventing a slope across a famously level floor would have been a lie. A pan is not level in the
    same way: it is the bottom of a basin, which is WHY the salt is there - water ran in, could not run
    out, and evaporated. The slope is the reason the zone exists, so it belongs in the model.
    """
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)

    # THE RIM, all the way round, with notches cut for the three gates. Wobbled so the mountains have
    # an outline rather than a rectangle's corners.
    # A SOFT-MIN, NOT A MIN. min(dx, dy) is a rectangle's distance field and no amount of wobble
    # hides that - the first version came back with a band of mountains and four square corners,
    # which is precisely the box Kyle asked to get rid of. A soft minimum rounds the corners, so
    # the rim thickens into them the way a real basin's does.
    dx = np.minimum(gx, W - gx)
    dy = np.minimum(gy, H - gy)
    k = 9.0
    edge = -k * np.log(np.exp(-dx / k) + np.exp(-dy / k))

    # AND THE WOBBLE HAS TO BE BIG. At an amplitude of 4.5 against a 23-tile rim it moved the inner
    # edge by a fifth of its width and the eye still read a rectangle. At 16 the rim swings between
    # about seven and forty tiles deep, which is bays and headlands rather than a border.
    edge = (edge + 11.0 * wob(gx * 0.034, gy * 0.037)
            + 5.0 * wob(gx * 0.088, gy * 0.081)
            + 2.0 * wob(gx * 0.21, gy * 0.19))
    rim = RIM_H * smoothstep(RIM_W, 2.0, edge)
    rim = rim - 60.0 * np.clip(_gate_cut(gx, gy), 0, None)
    e = np.clip(rim, 0.0, None)

    # the stacks: erosion remnants standing on the pan inside the rim. DEEPEST WINS rather than adding - two overlapping footprints summing their
    # heights makes a spike at the junction, which is not a landform. Same rule as the mesas.
    plateau = np.zeros(np.shape(gx), float)
    for (_n, cx, cy, rx, ry, h) in STACKS:
        r = _stack_r(gx, gy, cx, cy, rx, ry)
        plateau = np.maximum(plateau, h * smoothstep(1.0, 0.84, r))
    e = np.maximum(e, plateau)

    # THE BASIN. Lowest east of centre. It is dry - see water_field - but it is still what sorts the
    # map, because the crust gets thinner and dirtier the lower you go and the hives like it best.
    d = np.hypot((gx - 146.0) / 62.0, (gy - 104.0) / 54.0)
    e = e - 2.1 * smoothstep(1.15, 0.1, d)

    # the hives: cones, flat-ish at the crown where the shaft is
    for (_n, cx, cy, r, h, _t) in HIVES:
        rr = np.hypot(gx - cx, gy - cy) / r
        e = e + h * smoothstep(1.05, 0.18, rr)

    # salt polygons and a little drift relief, so the pan is textured without being bumpy
    e = e + 0.16 * wob(gx * 0.11, gy * 0.12) + 0.07 * wob(gx * 0.33, gy * 0.31)
    return e


def _slope(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    dx = (elevation(gx + 1.0, gy) - elevation(gx - 1.0, gy)) * 0.5
    dy = (elevation(gx, gy + 1.0) - elevation(gx, gy - 1.0)) * 0.5
    return np.hypot(dx, dy)


WALK_SLOPE = 0.80

ROADS = {
    # The road in from Southern Needles, straight out onto the pan because that is what a road across a
    # salt flat does - there is nothing to go around until the hives.
    "road":  ([(4, 132), (32, 128), (66, 120), (100, 112), (128, 110), (152, 112), (180, 116)], 3.0),
    # The high track down from the Aspen side, joining it.
    "track": ([(4, 40), (28, 48), (48, 66), (62, 92), (72, 110), (92, 116)], 2.4),
    # And the spur north to the Raceway, which is how anybody ever got to a race.
    "spur":  ([(100, 112), (102, 90), (104, 72), (104, 56)], 2.2),
}


def road_dist(gx, gy):
    out = np.full(np.shape(gx), -9.0)
    for (pts, wide) in ROADS.values():
        d = _poly_dist(gx, gy, pts)
        out = np.maximum(out, wide * 0.5 - d)
    return out


def track_dist(gx, gy):
    """The Raceway ring itself - a surface, not a road, and wider than one."""
    d = _poly_dist(gx, gy, RACEWAY)
    return 3.4 - d


def paved(gx, gy):
    return (road_dist(gx, gy) > 0.0) | (track_dist(gx, gy) > 0.0)


def water_field(gx, gy):
    """THERE IS NO WATER ON THE FLATS. Kyle: "the flats does not have water."

    An earlier pass had the basin holding a sheet of standing brine, on the reasoning that water runs to
    the lowest ground and stays there. That reasoning is right about how the salt GOT here and wrong
    about what is here now: a pan is what a lake leaves BEHIND. The water is the one thing that is
    finished. The basin is still the lowest ground and still the thing that sorts the map - it is just
    dry, and what fills it is crust, mud and what the hives have brought up.
    """
    return np.full(np.shape(gx), -9.0)


def deck_field(gx, gy):
    return np.full(np.shape(gx), -9.0)


def cliff_field(gx, gy):
    """Rock is slope, and out here the only slope is a hive's flank or a stack's rim.

    See the module docstring: this rule has been wrong once in this region (the Aspen Wilderness, where
    the steepest ground is the drainage walls) and right twice, for two different reasons.
    """
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    rock = (_slope(gx, gy) - WALK_SLOPE) * 4.0

    # the tunnel mouths cut through the flanks. Strong enough to beat the biggest mound on the map -
    # Southern Needles learned this the hard way, where a cut tuned against the shallow mesas silently
    # sealed the three tall ones and with them the only ground route into Freewind.
    rock = rock - 40.0 * np.clip(_tunnel_cut(gx, gy), 0, None)

    # The rim does the edge sealing now, so the old four-tile border term is gone - it would have
    # drawn a hard rectangle inside the mountains it is standing in.
    # The three gates stay open.
    rock = rock - 40.0 * np.clip(_gate_cut(gx, gy), 0, None)
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    rock = np.where(track_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    rock = np.where(water_field(gx, gy) > -1.0, np.minimum(rock, -0.5), rock)
    return rock


def fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    w = water_field(gx, gy)
    return dict(cliff=cliff_field(gx, gy), shallow=w, deep=w - 3.0, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


#: West to east, which is the level ladder. See the module docstring.
SUBZONES = [
    ("The Shore", 18, 18, 56, 148),               # 35-36, the ground inside the west rim
    ("The Crust", 48, 18, 54, 144),               # 36-37
    ("The Mirage Raceway", 90, 16, 72, 66),       # 37-38
    ("The Brine", 86, 92, 72, 80),                # 37-38
    ("The Mounds", 134, 26, 48, 128),             # 38-39
    ("The Deep Pan", 158, 60, 42, 92),            # 39-40
]

BASE = {"salt": 0.46, "hard": 0.26, "clay": 0.18, "rock": 0.10}
PAINT = {}
COBBLE = []
NPC_POSITIONS = {}
CHESTS = [(24, 74), (104, 44), (132, 104), (172, 118)]
FOREST = None


def dress(L):
    """Salt country, and what is coming up through it.

    THE PAN IS NEARLY BARE AND THAT IS THE DESIGN. Nothing grows on salt. Props cluster on the shore,
    thin out to almost nothing across the crust, and are replaced further east by the hives' own
    leavings - carapace, egg sacs, resin. The emptiest stretch of this map should be the middle, which is
    also where you are most exposed, which is the zone's whole idea.
    """
    z = L.z
    rng = np.random.default_rng(SEED)
    SN = "assets/tiles/southern_needles/props/"
    BS = "assets/tiles/broodspiral/props/"
    A = lambda d, s: d + s + ".png"        # noqa: E731
    n = 0
    for _ in range(2400):
        x = int(rng.integers(3, W - 3))
        y = int(rng.integers(3, H - 3))
        if not z.is_walkable(x, y):
            continue
        r = rng.random()
        if x < 72:                                            # the shore: the last of the desert
            if r < 0.22:
                nm = rng.choice(["sn_barrel_cactus", "sn_desert_sage", "sn_dead_shrub", "sn_grass_tuft",
                                 "sn_boulder_red", "sn_rock_spire", "sn_layered_stack", "sn_cairn"])
                if L.prop(A(SN, nm), x, y, 4):
                    n += 1
        elif x < 118:                                         # the crust: salt, bone and driftwood
            if r < 0.055:
                nm = rng.choice(["sn_driftwood_salt", "sn_rib_bones", "sn_kodo_skull", "sn_dead_shrub",
                                 "sn_stone_pile"])
                if L.prop(A(SN, nm), x, y, 3):
                    n += 1
        else:                                                 # hive country
            if r < 0.085:
                nm = rng.choice(["carapace_pile", "egg_sac_cluster", "resin_pillar"])
                if L.prop(A(BS, nm), x, y, 4):
                    n += 1
            elif r < 0.105:
                nm = rng.choice(["sn_rib_bones", "sn_driftwood_salt"])
                if L.prop(A(SN, nm), x, y, 3):
                    n += 1
    return n


def _landmarks(L):
    """THE ZONE'S OWN PROPS, WHICH IT NEVER USED. Found 13 Nov 2026, looking for something to see.

    assets/tiles/shimmering_flats/props holds a grandstand, a start gantry, pit awnings, wrecked
    racers, fuel drums and wheel stacks - a whole raceway - and hive mounds, tunnel mouths, chitin
    spires, egg clusters and resin growths. dress() above reached for Southern Needles' cactus and
    the Broodspiral's leavings and placed none of them. The Mirage Raceway was a ring painted on
    the salt with nothing standing at it, and a hive was a dark disc.

    A SECOND pass with its own dice, after dress(), so nothing already placed moves. Everything
    goes through L.prop (never on a road, never on top of something), and nothing is put in a gate
    through the rim or in a tunnel into a mound.
    """
    rng = np.random.default_rng(SEED + 9173)
    SF = "assets/tiles/shimmering_flats/props/"
    n = 0

    def one(fn, x, y):
        return float(np.asarray(fn(np.array([[float(x)]]), np.array([[float(y)]]))).ravel()[0])

    def put(name, x, y, h):
        nonlocal n
        x, y = int(round(x)), int(round(y))
        if not (6 <= x < W - 6 and 6 <= y < H - 6):
            return False
        if one(_gate_cut, x, y) > -4.0 or one(_tunnel_cut, x, y) > -2.5:
            return False
        if any(abs(x - ax) + abs(y - ay) < 8 for (ax, ay) in list(ARRIVALS) + list(PORTALS) + list(CHESTS)):
            return False
        ok = L.prop(SF + name + ".png", x, y, h)
        n += bool(ok)
        return ok

    # ---- THE MIRAGE RACEWAY. The crowd watches the north straight; the pits are inside the ring.
    put("sf_start_gantry", 104, 31, 7)
    # inside the north straight: outside it is the foot of the rim, where nothing can stand
    for (x, y) in [(116, 38), (128, 36), (140, 40)]:
        put("sf_grandstand", x, y, 6)
    for (x, y) in [(112, 44), (119, 47), (127, 45)]:
        put("sf_pit_awning", x, y, 5)
    for (name, x, y, h) in [("sf_fuel_drums", 115, 51, 3), ("sf_wheel_stack", 122, 53, 3),
                            ("sf_crate_stack", 130, 51, 3), ("sf_scrap_heap", 136, 47, 4),
                            ("sf_condenser", 124, 58, 4), ("sf_hand_winch", 110, 56, 3),
                            ("sf_wheel_stack", 133, 57, 3), ("sf_fuel_drums", 140, 55, 3),
                            ("sf_signboard", 98, 30, 3), ("sf_signboard", 97, 108, 3),
                            ("sf_signboard", 44, 124, 3)]:
        put(name, x, y, h)
    # the ones that did not make the corner, and the ones that left the track altogether
    for (x, y) in [(158, 40), (96, 62), (146, 70), (70, 150), (118, 162), (62, 32), (176, 152),
                   (142, 86), (84, 100)]:
        put("sf_wrecked_racer", x, y, 4)
    # lamps down the spur, which is how anybody found the place at night
    for y in range(62, 110, 9):
        put("sf_lamp_post", 108, y, 5)

    # ---- THE HIVES. A ring of spires round each mound, its leavings, and a mouth where the way in is.
    for (_nm, cx, cy, r, _h, turn) in HIVES:
        ang = turn * TAU
        put("sf_tunnel_mouth", cx + np.cos(ang) * r * 1.75 + np.sin(ang) * 5,
            cy + np.sin(ang) * r * 1.75 - np.cos(ang) * 5, 6)
        for _ in range(int(r * 0.9)):
            a, d = rng.random() * TAU, r * (1.18 + 0.5 * rng.random())
            put("sf_chitin_spire", cx + np.cos(a) * d, cy + np.sin(a) * d, int(rng.integers(5, 9)))
        for _ in range(int(r * 0.7)):
            a, d = rng.random() * TAU, r * (1.2 + 0.9 * rng.random())
            put(str(rng.choice(["sf_egg_cluster", "sf_resin_growth", "sf_carapace_heap"])),
                cx + np.cos(a) * d, cy + np.sin(a) * d, int(rng.integers(3, 5)))
        for _ in range(2):          # and the young ones starting beside it
            a, d = rng.random() * TAU, r * (2.0 + 0.5 * rng.random())
            put("sf_hive_mound", cx + np.cos(a) * d, cy + np.sin(a) * d, 5)

    # ---- THE SHORE: what the sand had already half taken before the salt came
    for (x, y) in [(40, 60), (34, 104), (46, 146)]:
        put("tan_obelisk", x, y, 6)
    for (x, y) in [(44, 64), (38, 58), (30, 108), (50, 150), (42, 142)]:
        put("tan_ruin_block", x, y, 4)
    for _ in range(40):
        x, y = int(rng.integers(22, 70)), int(rng.integers(20, 162))
        put(str(rng.choice(["tan_dead_palm", "tan_dune_grass", "tan_thorn_scrub", "tan_skeleton"])), x, y,
            int(rng.integers(3, 6)))
    return n


_dress_scatter = dress


def dress(L):          # noqa: F811 - the scatter, then the landmarks
    return _dress_scatter(L) + _landmarks(L)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_shimmering_flats():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/flats_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
