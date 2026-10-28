"""
Hand-built The Aspen Wilderness (210x180): the north face of the range that came down on Thousand Needles.
Levels 25-30. Frontier's second home-brew zone.

ARCHETYPE: THE WALL AND THE WAY THROUGH. The range runs EAST TO WEST, across the player's path. Every other
open zone in the game is country you move around in; this is country you have to get OVER. You come in at the
Barrens floor along the north edge and everything trends up and south toward one pass.

THE TERRAIN IS A REAL MOUNTAIN, NOT A FIELD WITH ROCKS ON IT.

Kyle lives in the Rockies and asked for them to be done justice, so this map is not built the way the others
are. Every other zone in Frontier hand-places its rock: a list of spurs and outcrops, dropped where the author
wants a wall. That approach cannot produce a mountain, because a mountain's shape is not a decision about where
walls go - it is a consequence of elevation, and the walls are wherever the ground got too steep to stand on.

So this zone has an ELEVATION MODEL, and everything else is derived from it:

  elevation()   the long ramp up the north face, the divide rising at the south edge, spur ridges running
                north off that divide, drainages incised between them, and a terracing pass that produces
                benches - the flat glacial shelves you actually walk on in this country.
  _slope()      the gradient of elevation, evaluated analytically so it works on any sub-grid.
  cliff_field() IS THE SLOPE. Rock is wherever the ground is steeper than a person can walk. Nothing is
                placed; the cliffs are what is left over.

That one inversion is the whole zone. It gives you, for free and correctly related to each other: valley
bottoms you can follow, benches that connect, headwalls you cannot climb, and ridgelines that actually read
as the tops of things rather than as fences.

WHAT THE ROCKIES ACTUALLY LOOK LIKE, and where each of these is in the code:

  * Spur ridges are DERIVED, never drawn. They are whatever the drainage network has not cut away, which
    is why they branch and taper the way real ones do. The first build described ridges directly, with a
    sinusoid, and got parallel stripes - see the note above DRAINAGE.
  * Benches. Glaciated country steps: flat shelf, short steep riser, flat shelf. That is the terracing term
    in elevation(), and it is what makes the map walkable at all.
  * AVALANCHE CHUTES are the ways up (CHUTES). A path is swept clear of timber every few winters, so it is
    the one break in otherwise impassable slope - which means in this zone the dangerous ground and the only
    route are the same ground. That is true of the real range and it is the best thing about the map.
  * Treeline is a HARD boundary, not a fade. Below it, forest; above it, krummholz for a short band and then
    nothing but rock and snow (TREELINE, used by the vegetation pass).
  * Aspen marks DISTURBANCE. It is a pioneer: it colonises burns, slide paths and benches, and conifer shades
    it out everywhere else. So the gold stands in this zone are not decoration, they are a map of what has
    happened here - and the dark lodgepole holds the wet drainage walls.

THE VEGETATION PASS IS CUSTOM for that last reason. tirisfal_kit.forest() scatters uniformly and picks a
random name per tree, which would mix aspen and pine evenly across the whole map and throw the ecology away.
_vegetate() below places by terrain instead: conifer in the drainages, aspen on benches and in the slide
paths and the burn, krummholz at treeline, bare rock above it.

HARD CONTRACTS (world/portal_manager.py)
  (105, 5)   <-> Southern Barrens          the Broken Lift, at the seam
  (104, 173) -> the Pass, south            carved and marked, NOT registered until Southern Needles exists.
                                           An unregistered portal tile fails safe.
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob, water_body

KEY = "aspen_wilderness"
#: Must match the name this zone is registered as in create_all_zones - portal_manager keys on zone.name.
NAME = "The Aspen Wilderness"
DESC = ("The north face of a mountain range that was not here three years ago. Aspen and lodgepole, avalanche "
        "paths, and one pass over the top.")
REGION = "Kalimdor - Thousand Needles"
W, H = 210, 180
BAKED_DIR = "assets/tiles/aspen/baked"
IS_TOWN = False
BASE_TILE = "dirt"
SEED = 541

ASP = "assets/tiles/aspen/props/"
TAU = 2.0 * np.pi

PORTALS = {(105, 5): "Southern Barrens",
           #: The cave mouth, high on the Rim's east side and well off the main trail - a glacier
           #: remnant belongs up near the ice, and this one should be found rather than tripped over.
           (145, 48): "The Weeping Ice"}
ARRIVALS = [(105, 11), (145, 51)]
START = (105, 12)

#: Where the forest stops. In elevation units, not tiles - see elevation().
TREELINE = 12.4
KRUMMHOLZ = 9.6           # the stunted band just below it


def smoothstep(a, b, x):
    t = np.clip((np.asarray(x, float) - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


# =================================================================================================== TERRAIN
#
# THE DRAINAGE NETWORK IS THE MOUNTAIN, AND THE RIDGES ARE WHAT IS LEFT BETWEEN IT.
#
# The first build of this terrain used a sinusoidal ridge field - a function of x alone - and it produced
# exactly what a function of x alone has to produce: parallel vertical stripes, with two creeks running the
# full height of the map like canals. Regular corrugation is the giveaway of a generated mountain, and that
# one was giving itself away in the first screenshot.
#
# Real topography is the other way round. Water carves a BRANCHING network - a main stem with tributaries
# joining at angles, each with its own headwaters - and the high ground is simply whatever the water has not
# taken yet. Ridges branch because drainages branch. So this model authors the drainage tree and subtracts
# it from a smooth ramp, and never describes a ridge at all: every spur, shoulder and saddle on this map is
# a consequence of where the water goes.
#
# Stream order sets depth and width. The main stem is deep and broad; a headwater is a shallow crease. That
# is why the country opens out as you descend and closes in as you climb toward the headwalls.

#: (points north-to-south, depth, width). Order 1 is the main stem; the rest join it.
#: THE DRAINAGE NETWORK IS A COMB, NOT A TREE.
#:
#: This was hand-drawn twice as a dendritic network - one big trunk running north-south up the middle with
#: tributaries joining it at angles - and both bakes came out looking like a dead tree lying on the map.
#: The reason is geometric, not cosmetic. A single trunk with branches radiating off it IS a tree: it is
#: what a whole WATERSHED looks like from above, the drainage of a basin collected to one outlet. That is
#: the right picture for a river delta and the wrong picture for what this zone is.
#:
#: This zone is the NORTH FACE OF AN EAST-WEST RANGE. Kyle: "Run it east to west." On the flank of a range
#: the water has nowhere to collect - it falls off the divide and runs straight down the slope - so what
#: you get is twenty-odd SHORT, ROUGHLY PARALLEL creeks hanging off the crest like the teeth of a comb,
#: separated by the spurs between them, all of it emptying into one valley running along the foot. Stand
#: anywhere on the north side of the Rockies and that is what is in front of you.
#:
#: That shape also does the zone's job for free: the spurs run north-south, across the player's line of
#: travel, so climbing means crossing them one after another, and the range reads as a wall of parallel
#: ribs rather than as an object sitting on a field.
#:
#: Generated rather than typed, because twenty-two creeks is too many to hand-place and the spacing and
#: sinuosity matter more than any individual line. Seeded, so it is reproducible.
#: THE COMB NEEDS A HIERARCHY, OR IT IS WALLPAPER.
#:
#: First comb attempt was 22 creeks at an even spacing, all hanging the same distance off the divide, all
#: roughly the same depth. Kyle, looking at the bake: "It looks like copy paste paste paste." He is right,
#: and it is the same failure as the dead tree one level up - a rule applied uniformly reads as a texture,
#: not as terrain.
#:
#: Real range flanks are hierarchical. A handful of MAJOR valleys cut most of the way to the crest and are
#: what you actually navigate by. Between them sit medium draws that peter out halfway down the face. In
#: the gaps between THOSE are short gullies that only exist in the bottom third. The spurs left over are
#: therefore wildly different widths - some are thin ribs you step over, one or two are broad shoulders
#: with their own small drainage - and that irregularity is the whole difference between a mountain and a
#: comb. Spacing is drawn irregularly for the same reason: evenly spaced anything reads as manufactured.
DRAIN_MAJOR = 4
DRAIN_MID = 7
DRAIN_MINOR = 12


def _creek(rng, x0, y_top, y_bot, sway_amp, n=5):
    pts = []
    for j in range(n):
        t = j / (n - 1.0)
        y = y_top + (y_bot - y_top) * t
        sway = np.sin(np.pi * t) * rng.uniform(-sway_amp, sway_amp) + rng.uniform(-1.6, 1.6)
        pts.append((round(float(x0 + sway), 1), round(float(y), 1)))
    return pts


def _spread(rng, n, lo, hi, jitter):
    """n positions across [lo, hi] that are NOT evenly spaced - each slot is nudged by up to `jitter` of
    its own width, so gaps and clusters both happen."""
    step = (hi - lo) / n
    return [lo + step * (i + 0.5 + rng.uniform(-jitter, jitter)) for i in range(n)]


def _build_drainage():
    """(polyline, depth, width) per watercourse. See the note above for why this is tiered."""
    rng = np.random.default_rng(SEED)
    out = []

    # THE COLLECTOR. One valley running east-west along the foot of the range, which everything empties
    # into. The only continuous east-west walking in the zone, so it carries the lower trail.
    out.append(([(4, 152), (34, 156), (66, 151), (96, 157), (128, 151), (160, 157), (190, 152), (206, 156)],
                9.4, 8.2))

    # TIER 1 - the major valleys. Deep, wide, and they reach almost to the divide. These are the four
    # features a player will actually learn the zone by.
    majors = _spread(rng, DRAIN_MAJOR, 16.0, 196.0, 0.42)
    for x0 in majors:
        top = rng.uniform(46.0, 56.0)
        pts = _creek(rng, x0, top, 154.0 + rng.uniform(-3.0, 2.0), 9.5, n=6)
        out.append((pts, round(float(rng.uniform(9.6, 11.4)), 2), round(float(rng.uniform(7.0, 8.4)), 2)))
        # Two real tributaries each, on alternating sides, which is what gives the big spurs their own
        # internal shape instead of leaving them as smooth ribs.
        for k, side in enumerate((1.0, -1.0) if rng.random() < 0.5 else (-1.0, 1.0)):
            jy = top + rng.uniform(28.0, 62.0) + 22.0 * k
            jx = x0 + rng.uniform(-4.0, 4.0)
            out.append(([(round(float(jx + side * rng.uniform(22.0, 32.0)), 1), round(float(jy - 26.0), 1)),
                         (round(float(jx + side * rng.uniform(10.0, 16.0)), 1), round(float(jy - 11.0), 1)),
                         (round(float(jx), 1), round(float(jy), 1))],
                        round(float(rng.uniform(5.6, 7.4)), 2), round(float(rng.uniform(4.4, 5.6)), 2)))

    # TIER 2 - medium draws. They start partway up and die out before the crest, so the upper face is
    # noticeably less dissected than the lower face, the way a real one is.
    for x0 in _spread(rng, DRAIN_MID, 10.0, 200.0, 0.46):
        if min(abs(x0 - m) for m in majors) < 11.0:       # don't crowd a major
            x0 += 15.0 * (1.0 if x0 < 105 else -1.0)
        top = rng.uniform(62.0, 92.0)
        pts = _creek(rng, x0, top, 153.0 + rng.uniform(-4.0, 2.0), 7.0, n=5)
        out.append((pts, round(float(rng.uniform(6.4, 8.2)), 2), round(float(rng.uniform(5.2, 6.4)), 2)))

    # TIER 3 - short gullies in the bottom third only. They break up the lower spurs without adding
    # anything the player has to climb around.
    for x0 in _spread(rng, DRAIN_MINOR, 8.0, 202.0, 0.50):
        top = rng.uniform(102.0, 128.0)
        pts = _creek(rng, x0 + rng.uniform(-5.0, 5.0), top, 152.0 + rng.uniform(-3.0, 2.0), 4.6, n=4)
        out.append((pts, round(float(rng.uniform(4.0, 5.8)), 2), round(float(rng.uniform(3.6, 4.8)), 2)))

    return out


DRAINAGE = _build_drainage()


def _poly_dist(gx, gy, pts):
    """Distance to a polyline."""
    d = None
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg = T.seg_dist(gx, gy, x0, y0, x1, y1)
        d = seg if d is None else np.minimum(d, seg)
    return d


#: DRAINAGES ARE V-VALLEYS, NOT SLOTS. The first build cut them at their declared depth and width and the
#: result baked as a grey dead tree across a brown field: a 14-deep channel with a 5-wide falloff has walls
#: pitched past 1.5, which is three times WALK_SLOPE, so every creek in the zone grew rock sides and the
#: drainage network - the one thing that was supposed to be invisible structure - became the most visible
#: object on the map. Shallower and wider turns each slot into a valley you can walk down with timber on
#: both sides, which is what a drainage in this country actually looks like.
INC_DEPTH = 0.95
INC_WIDE = 1.55


def _incision(gx, gy):
    """How deep the water has cut here. The deepest channel wins rather than the sum, so a junction is
    as deep as its main stem instead of adding into a pit."""
    inc = np.zeros(np.shape(gx))
    wander = 1.6 * wob(gx * 0.30, gy * 0.30)
    for (pts, depth, width) in DRAINAGE:
        d = _poly_dist(gx, gy, pts) + wander
        w = width * INC_WIDE
        inc = np.maximum(inc, depth * INC_DEPTH * np.exp(-np.clip(d, 0, None) ** 2 / (2.0 * w ** 2)))
    return inc


def _channel(gx, gy):
    """>0 in the actual watercourse - the narrow bottom of the big drainages, not the whole valley."""
    out = np.full(np.shape(gx), -9.0)
    wander = 1.1 * wob(gx * 0.9, gy * 0.9)
    for (pts, depth, width) in DRAINAGE:
        if depth < 7.6:                      # headwaters run dry; only the majors carry water
            continue
        d = _poly_dist(gx, gy, pts) + wander
        out = np.maximum(out, (width * 0.26) - d)
    return out


def elevation(gx, gy):
    """Height of the ground. South (larger y) is uphill; the divide is the south edge."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)

    # YOU ENTER AT THE TOP AND GO DOWN. Kyle: "even though it runs east to west, we go DOWN the mountain
    # as we go south. We start at the highest point when we enter the northern part of the zone."
    #
    # The first three builds had this backwards - entering on the Barrens floor and climbing south to a
    # pass. Inverted, it is both better and lore-correct: in Azeroth the Great Lift carried you DOWN off
    # the Barrens plateau into Thousand Needles, so with the Lift destroyed the zone's problem is not
    # getting over a range, it is getting down off one. Everything below follows from that.
    e = 25.6 - 0.049 * gy                            # the long descent, north to south

    # THE ESCARPMENT. The drop the Great Lift used to span, now a line of cliff near the top of the map.
    # It is the zone's gate: high bare country above it, the whole forested descent below, and only a few
    # gullies through. Its line wanders north and south along its length so it reads as a broken rim
    # rather than a fence, and the chutes that breach it are the ways down.
    rim_y = 40.0 + 7.0 * wob(gx * 0.023, np.zeros_like(gy)) + 3.0 * wob(gx * 0.061, np.zeros_like(gy))
    e = e - 13.5 * smoothstep(rim_y - 7.0, rim_y + 13.0, gy)

    # A SECOND STEP, lower down. Real descents go in stages - rim, a long bench, another riser - and this
    # one is pierced by saddles so it breaks into separate benches instead of running as one terrace.
    step_y = 108.0 + 9.0 * wob(gx * 0.034, np.zeros_like(gy))
    saddle = 0.60 + 0.40 * wob(gx * 0.047 + 11.0, np.zeros_like(gy))
    e = e - 4.4 * saddle * smoothstep(step_y - 8.0, step_y + 9.0, gy)

    # THE HIGH BASIN behind the rim, where the Lift platform and the Seam sit. A flat place to arrive in,
    # which matters because the player lands here and should not land on a slope.
    bowl = 1.0 - np.sqrt(((gx - 104) / 46.0) ** 2 + ((gy - 18) / 15.0) ** 2)
    e = e - 2.2 * np.clip(bowl, 0, None)

    # Broad relief - the mass of the range. NOT structure: the structure comes from the water below.
    # Low frequencies only. A high-frequency term here crosses the walkable-slope threshold at
    # random and litters the map with one-tile rocks that read as gravel rather than terrain.
    e = e + 2.6 * wob(gx * 0.13, gy * 0.16) + 1.1 * wob(gx * 0.31, gy * 0.33)

    # The water takes its share - BUT NOT ABOVE THE RIM. A drainage divide is by definition where drainage
    # starts; nothing has cut across it, which is exactly why it is still there. Letting the big valleys
    # run at full depth through the escarpment punched gaps in it and turned the rim into a fence with
    # holes. The incision fades out as it nears the rim from below instead.
    e = e - _incision(gx, gy) * smoothstep(rim_y - 10.0, rim_y + 14.0, gy)

    # BENCHES. Glaciated country steps - flat shelf, short riser, flat shelf - and the flats are most of
    # what is walkable at all.
    e = e + 0.62 * np.sin(e * 1.85)
    return e


def _slope(gx, gy):
    """|grad elevation|, evaluated analytically so it is valid on any sub-grid the baker hands us."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    dx = (elevation(gx + 1.0, gy) - elevation(gx - 1.0, gy)) * 0.5
    dy = (elevation(gx, gy + 1.0) - elevation(gx, gy - 1.0)) * 0.5
    return np.hypot(dx, dy)


#: AVALANCHE CHUTES: (x_top, y_top, x_bottom, y_bottom, half-width). A slide path is swept clear every few
#: winters, so it is the one break in slope that would otherwise be unclimbable - which makes the dangerous
#: ground and the only route up the same ground. These are the ways through the map.
CHUTES = [
    # (x_top, y_top, x_bottom, y_bottom, half-width)
    # THE WAYS DOWN. A chute is a gully swept clear by slides every few winters, so it is the one break in
    # ground that is otherwise too steep to descend. The first four breach the Lift escarpment and are the
    # only ways off the high basin; the rest step down the benches below it. That makes the dangerous
    # ground and the only route the SAME ground, which is the zone's best single idea and falls straight
    # out of the terrain rather than being written on top of it.
    (104, 30, 102, 58, 4.6),      # the main breach, below the Broken Lift itself
    (48, 34, 54, 60, 4.0),
    (156, 32, 148, 60, 4.0),
    (82, 36, 76, 62, 3.4),
    (96, 74, 90, 104, 4.2),       # down off the upper benches
    (132, 72, 140, 102, 3.8),
    (42, 78, 52, 106, 3.8),
    (168, 82, 160, 110, 3.4),
    (88, 116, 94, 146, 3.6),      # the last step, onto the valley floor
    (140, 118, 132, 148, 3.4),
]


def _chute(gx, gy):
    """How strongly a slide path has cleared the ground here (>0 inside a chute)."""
    out = np.full(np.shape(gx), -9.0)
    for (x0, y0, x1, y1, t) in CHUTES:
        d = T.seg_dist(gx, gy, x0, y0, x1, y1)
        out = np.maximum(out, (t - d) + 0.6 * wob(gx * 1.1, gy * 1.1))
    return out


#: Trails. In this country a road is a game trail that people widened - they follow the valley bottoms and
#: the benches, because that is where the walking is, and they are NOT the only way across.
ROADS = {
    # Trails follow the descent, because that is where the walking is. "main" drops off the high basin
    # through the Lift breach and works south down the benches to the valley floor; the rest are side
    # routes along the benches. They are NOT the only way down - the chutes are open ground too.
    "main":  ([(105, 8), (104, 24), (103, 44), (101, 66), (95, 90), (97, 114), (103, 138), (104, 176)], 2.8),
    "west":  ([(101, 66), (76, 72), (56, 84), (44, 102), (48, 122), (56, 142)], 2.2),
    "east":  ([(104, 56), (134, 62), (158, 76), (168, 98), (154, 120)], 2.2),
    "bench": ([(95, 90), (68, 96), (50, 104)], 2.0),
    "burn":  ([(100, 112), (128, 112), (152, 120)], 2.0),
}
_RS = K.RoadSet(ROADS)
road_dist = _RS.dist


def paved(gx, gy):
    return np.full(np.shape(gx), -9.0)


# ---- water: creeks in the drainages, beaver ponds on the benches ------------------------------------------
#: Stepped beaver ponds on the gentle ground. (cx, cy, rx, ry, k)
PONDS = [(146, 40, 9.0, 5.5, 0.5), (138, 52, 6.5, 4.0, 0.2), (155, 32, 5.5, 3.5, 0.0),
         (60, 104, 7.0, 4.5, 0.3), (50, 112, 5.0, 3.2, 0.0),
         (104, 150, 8.0, 5.0, 0.2)]


def water_field(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    # Creeks run the bottoms of the real drainages and dry up as they climb toward the headwalls.
    # Dry up with altitude by SUBTRACTING, never by multiplying. _channel returns a large negative value
    # for "no water here", and a multiplier that reaches zero turns that sentinel into 0.0 - which reads
    # as water surface level rather than as no water. cliff_field forces anything above -1.0 walkable, so
    # that one sign error made the entire headwall walkable while its slope said otherwise.
    dry = smoothstep(TREELINE - 7.0, TREELINE + 1.0, elevation(gx, gy))
    creek = _channel(gx, gy) * 2.4 - 40.0 * dry
    w = np.minimum(creek, 1.1)
    for (cx, cy, rx, ry, k) in PONDS:
        w = np.maximum(w, water_body(gx, gy, cx, cy, rx, ry, k=0.7) + k)
    return w


def deck_field(gx, gy):
    return np.full(np.shape(gx), -9.0)


#: Slope at which the ground stops being walkable. Everything about how open or closed this map feels is
#: this number; tools/verify_aspen_wilderness.py measures the result rather than trusting it.
WALK_SLOPE = 0.48


#: Ring radius for _relief, in tiles. THIS IS THE SENSITIVE NUMBER IN THE ZONE. It has to span about
#: half a valley so the ring sits on the ridges while the centre sits on the floor; at 3.4 it was inside
#: a single valley and measured surface wobble instead of valley-versus-ridge, and the rock threshold
#: barely responded to being moved at all - every setting gave the same 70% open map.
RELIEF_R = 8.0


def _relief(gx, gy, r=RELIEF_R):
    """How far this point stands above its own neighbourhood. Positive on crests, ridgelines and spur
    noses; negative in valley bottoms and on benches. Sampled on a ring rather than blurred, so it stays
    analytic and works on whatever sub-grid the baker hands us."""
    e = elevation(gx, gy)
    k = r * 0.7071
    acc = (elevation(gx + r, gy) + elevation(gx - r, gy)
           + elevation(gx, gy + r) + elevation(gx, gy - r)
           + elevation(gx + k, gy + k) + elevation(gx - k, gy + k)
           + elevation(gx + k, gy - k) + elevation(gx - k, gy - k))
    return e - acc / 8.0


def cliff_field(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    e = elevation(gx, gy)

    # ROCK IS CREST-NESS, NOT STEEPNESS.
    #
    # The first version of this read rock straight off the slope, on the reasoning that rock is wherever
    # the ground is too steep to stand on. That is true of a hillside and false of a range, and the bake
    # showed why: the steepest ground in a dissected mountain is the WALLS OF THE DRAINAGES, so the whole
    # map came out as grey canyon ribbons branching across a brown field - a dead tree, not a mountain.
    #
    # What the eye actually reads as rock from above is the high ground between the valleys: ridgelines,
    # spur noses, and everything above treeline. So rock is relief - how far a point stands above its own
    # surroundings - with the bar dropping as you climb. Down in the timber only a sharp crest breaks out
    # of the trees; up near the divide almost everything does. The valleys stay walkable and green for
    # their whole length, which is both truer and the thing worth looking at.
    alt = smoothstep(KRUMMHOLZ - 1.5, TREELINE + 3.0, e)
    bar = 0.34 - 0.52 * alt
    rock = (_relief(gx, gy) - bar) * 3.6

    # A genuinely sheer face is still rock whatever its relief says, but the threshold sits well above a
    # valley wall so this adds headwalls and cliff bands without re-growing the canyon sides.
    rock = np.maximum(rock, (_slope(gx, gy) - (WALK_SLOPE + 0.66)) * 7.0)

    # NO BLANKET "ABOVE TREELINE IS SOLID" RULE ANY MORE. That existed when the high ground was the
    # headwall at the far edge of the map and the player never stood on it. Now the high ground is where
    # the player ARRIVES - the basin above the rim, with the Lift and the Seam in it - and turning it to
    # rock walled off the entrance. Above treeline this country is bare and stony to look at, which the
    # baker handles, but it is ground you walk on. The rim below it does the blocking, by being steep.

    # The slide paths cut through it. This is what makes the map climbable.
    rock = rock - 3.2 * np.clip(_chute(gx, gy), 0, None)

    edge = np.minimum.reduce([gx, W - gx, gy, H - gy])
    rock = np.maximum(rock, (4.0 - edge) * 2.0 + 0.3 * wob(gx * 1.3, gy * 1.3))
    # The seam and the gate: the first stretch inside the map is Barrens floor and must stay open.
    rock = np.where(gy < 22, np.minimum(rock, -0.6), rock)

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


# ---- subzones (x, y, w, h), laid out by elevation band ----------------------------------------------------
SUBZONES = [
    # Ordered by ALTITUDE, which now means north-to-south: you arrive at the top and work down.
    ("The Broken Lift", 84, 0, 44, 18),      # the platform, cables going over the rim into nothing
    ("The Seam", 0, 10, 210, 14),            # the line itself, running east-west across the high basin
    ("The Rim", 0, 30, 210, 22),             # the escarpment the Lift used to span. Four ways down.
    ("The Gold Stands", 12, 56, 88, 44),     # aspen proper, the first real timber below the rim
    ("Blackneedle Rise", 106, 56, 94, 44),   # lodgepole, dark and close
    ("The Slide", 8, 102, 52, 46),
    ("The Burn", 94, 100, 104, 44),
    ("Elkhorn Meadow", 60, 104, 90, 34),
    ("Beaverdam Benches", 16, 142, 180, 34),  # the valley floor, stepped ponds, the only flat walking
]

# ---- baker config (read by tools/bake_aspen_zone.py) ------------------------------------------------------
BASE = {"duff": 0.42, "needle": 0.26, "grass": 0.20, "rock": 0.12}
PAINT = {}
COBBLE = []

#: WHERE THE PEOPLE STAND. Who they ARE lives in tools/aspen_npc_roster.py; this is the only place a
#: coordinate is decided, and tools/sync_aspen_npcs.py asserts the two name exactly the same people.
#:
#: Placed along the main trail rather than scattered, because this zone is a DESCENT - the player moves
#: through it in one direction and anybody standing off the route is somebody they never meet.
NPC_POSITIONS = {
    # the high basin: the gate, the Lift, the Seam
    "asp_gate_scout": (108, 12),
    "asp_lift_keeper": (100, 16),
    "asp_seam_watcher": (110, 21),
    # the rim: the people whose whole trade is the drop
    "asp_rope_master": (100, 38),
    "asp_rim_runner": (105, 45),
    "asp_cave_watch": (142, 52),          # near the cave mouth at (145, 48)
    # Longstand Camp, in the Gold Stands
    "asp_camp_elder": (92, 78),
    "asp_logger": (96, 80),
    "asp_camp_hunter": (85, 79),
    "asp_camp_cook": (90, 82),
    "asp_camp_smith": (94, 84),
    # downslope
    "asp_meadow_scout": (100, 118),
    "asp_bench_warden": (104, 152),
}
CHESTS = [(36, 46), (176, 44), (24, 120), (168, 96), (104, 158), (90, 82)]
#: The Pass tile, carved and marked but NOT registered - Southern Needles does not exist yet and an
#: unregistered portal fails safe. The main trail is extended to y=176 so the tile is reachable;
#: without that the marker sits behind the headwall and nobody can ever stand on it.
PASS_TILE = (104, 176)

#: The generic scatter is switched OFF - see the module docstring. _vegetate() places by terrain instead.
FOREST = None


# =============================================================================================== VEGETATION
def _vegetate(L):
    """Place trees the way the range places them, not uniformly.

    Conifer holds the wet drainage walls; aspen takes the benches, the burn and the slide paths, because
    aspen is a pioneer that colonises disturbance and gets shaded out everywhere else; krummholz marks the
    last stunted band under treeline; nothing grows above it.
    """
    rng = np.random.default_rng(SEED)
    ys, xs = np.mgrid[0:H, 0:W]
    gx, gy = xs + 0.5, ys + 0.5
    f = fields(gx, gy)
    floor = (f["cliff"] <= 0) & (f["shallow"] <= 0)
    e = elevation(gx, gy)
    inc = _incision(gx, gy)        # how deep the water has cut here: high = valley bottom
    slope = _slope(gx, gy)
    chute = _chute(gx, gy)
    burn = (gx > 104) & (gx < 198) & (gy > 64) & (gy < 104)

    placed = 0
    for _ in range(9000):
        if placed >= 620:
            break
        x, y = int(rng.integers(3, W - 3)), int(rng.integers(3, H - 3))
        if not floor[y, x]:
            continue
        ev, rv, sv, cv = e[y, x], inc[y, x], slope[y, x], chute[y, x]

        if ev > TREELINE:                      # above the trees: nothing but rock and snow
            continue
        if ev > KRUMMHOLZ:                     # the stunted band
            if rng.random() < 0.55:
                continue
            nm, hh, fr = "asp_pine_krummholz.png", 3, 0.30
        elif cv > 0:                           # a slide path: swept, and aspen comes back first
            if rng.random() < 0.45:
                continue
            nm, hh, fr = ("asp_aspen_young.png", 5, 0.30) if rng.random() < 0.6 \
                else ("asp_trunk_snapped.png", 3, 0.26)
        elif burn[y, x]:                       # the burn: snags standing, aspen coming up through them
            r = rng.random()
            nm, hh, fr = (("asp_snag_charred.png", 6, 0.26) if r < 0.34 else
                          ("asp_stump_burned.png", 3, 0.26) if r < 0.5 else
                          ("asp_aspen_young.png", 5, 0.30))
        elif rv > 2.2 and sv > 0.20:           # in a drainage, wet and shaded: lodgepole
            r = rng.random()
            nm, hh, fr = (("asp_pine_tall.png", 8, 0.26) if r < 0.6 else
                          ("asp_pine_young.png", 5, 0.28) if r < 0.85 else
                          ("asp_snag_standing.png", 6, 0.24))
        elif sv < 0.20:                        # a bench: open, dry, aspen parkland
            r = rng.random()
            nm, hh, fr = (("asp_aspen_tall.png", 8, 0.28) if r < 0.45 else
                          ("asp_aspen_clump.png", 8, 0.30) if r < 0.7 else
                          ("asp_aspen_bare.png", 7, 0.26) if r < 0.85 else
                          ("asp_aspen_fallen.png", 3, 0.26))
        else:                                  # everything between: mixed
            r = rng.random()
            nm, hh, fr = (("asp_aspen_tall.png", 8, 0.28) if r < 0.4 else
                          ("asp_pine_tall.png", 8, 0.26) if r < 0.75 else
                          ("asp_pine_bent.png", 7, 0.26))
        if L.prop(ASP + nm, x, y, hh, fraction=fr, nudge=0):
            placed += 1

    # Ground cover, thinner and lower down, same terrain logic
    for _ in range(3000):
        x, y = int(rng.integers(4, W - 4)), int(rng.integers(4, H - 4))
        if not floor[y, x] or e[y, x] > KRUMMHOLZ:
            continue
        r = rng.random()
        if inc[y, x] > 2.6:
            nm = "asp_willow_thicket.png" if r < 0.6 else "asp_ferns.png"
        elif burn[y, x]:
            nm = "asp_fireweed.png"
        else:
            nm = ("asp_huckleberry.png" if r < 0.35 else
                  "asp_grass_tussock.png" if r < 0.7 else "asp_wildflowers.png")
        L.prop(ASP + nm, x, y, 2, solid=False, nudge=0)
    return placed


def dress(L):
    p = L.prop
    n = _vegetate(L)
    A = lambda s: ASP + s + ".png"        # noqa: E731

    # ---- the Broken Lift: the top half of the machinery, and the cables going into rock ------------------
    # The Lift is Azerothian, not an Earth leaving - it was built to drop a thousand feet to Thousand
    # Needles, and the range is now standing where the drop used to be.
    p(A("asp_boulder"), 96, 9, 4)
    p(A("asp_boulder_split"), 114, 9, 4)
    p(A("asp_dead_scrub"), 100, 14, 2, solid=False)
    p(A("asp_red_drift"), 110, 15, 2, solid=False)

    # ---- the Seam: Barrens scrub standing dead in forest shade, and red dust in the lee of the trunks ----
    for (x, y) in ((28, 20), (54, 22), (82, 19), (132, 21), (164, 20), (188, 22)):
        p(A("asp_dead_scrub"), x, y, 3, solid=False)
    for (x, y) in ((40, 24), (96, 25), (150, 24), (176, 26)):
        p(A("asp_red_drift"), x, y, 2, solid=False)

    # ---- beaver works on the benches ---------------------------------------------------------------------
    p(A("asp_beaver_lodge"), 146, 42, 4)
    p(A("asp_beaver_dam"), 141, 47, 3)
    p(A("asp_beaver_dam"), 152, 36, 3)
    p(A("asp_beaver_lodge"), 60, 106, 4)
    p(A("asp_beaver_dam"), 55, 110, 3)

    # ---- the tauren push south: a working camp, not a settlement ----------------------------------------
    p(A("tau_hide_tent_small"), 88, 70, 5)
    p(A("tau_hide_tent_small"), 96, 72, 5)
    p(A("tau_cook_fire"), 92, 74, 3)
    p(A("tau_timber_stack"), 84, 76, 3)
    p(A("tau_drying_rack"), 100, 76, 4)
    p(A("tau_totem_carved"), 92, 66, 6)
    p(A("tau_hitching_post"), 82, 70, 3)

    # ---- the high country ---------------------------------------------------------------------------------
    p(A("asp_elk_skull"), 104, 134, 2, solid=False)
    p(A("asp_elk_skull"), 72, 120, 2, solid=False)
    p(A("asp_talus_pile"), 90, 160, 5)
    p(A("asp_talus_pile"), 120, 158, 5)
    p(A("asp_boulder_lichen"), 104, 146, 4)
    return n


def build_layout():
    return T.build(sys.modules[__name__])


def generate_aspen_wilderness():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/aspen_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
