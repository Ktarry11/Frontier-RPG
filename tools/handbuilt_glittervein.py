"""
Hand-built Glittervein (170x170): Tanaris zone 3. 46-49.

Kyle: "the cenote can be called Glittervein and it'll have similar stuff to the underdark."

THIS IS WHERE THE WATER COMES BACK, AND IT IS THE END OF A FIVE-ZONE ARGUMENT NOBODY PLANNED.

  The Aspen Wilderness      the melt is higher every spring
  Southern Thousand Needles where does all that water go
  The Shimmering Flats      it arrives, it goes under, it goes east
  Northern Tanaris          a walled city died of thirst when the table tipped
  The Abyssal Sands         and then the floor fell in

Five zones, four of them written before anybody noticed they were one story. This is the sixth
sentence and the only good one: THE WATER IS NOT GONE. It is here, at the bottom of a hole in the
limestone, and it is the only standing water for a hundred miles in any direction.

A CENOTE IS A SINKHOLE WITH THE WATER TABLE AT THE BOTTOM OF IT. The Abyssal Sands are what happens
when a limestone floor collapses into a void that has drained. This is what one looks like when the
void has NOT drained - the same geology, the same event, the opposite result. A player who has
crossed the Sands and then stands on this rim should recognise the shape instantly and find green in
the bottom of it.

SO THE ZONE IS A DESCENT AND THAT IS THE WHOLE DESIGN. Dead desert on the rim, three terraces
stepping down, and at the bottom a lake with trees round it. The terraces are concentric walkable
rings with impassable risers between them, joined by three ramps cut at different angles - so going
down is a spiral, not a staircase, and the player circles the hole getting lower. The depth IS the
level curve: the rim is 46 and the waterline is 49.

MAGIC RESISTANCE BELONGS HERE AND NOWHERE EARLIER. The rule is 45+. Northern Tanaris (41-44) could
not have it and the Abyssal Sands (44-47) deliberately did not take it even though two of its levels
qualify, because a zone that hands out resistance gear on a third of its drops has decided
resistance is its theme. This zone is the first one where it can be the theme, and the crystal
veins in these walls are the reason for it.

ONE WAY IN. Kyle's drawing puts a solid mountain range between Northern Tanaris and this zone, so
there is no direct route from zone 1 - you come through the Abyssal Sands or not at all. That suits
the end of a chain.

HARD CONTRACT (world/portal_manager.py):
    (6, 96) <-> The Abyssal Sands (176, 96)
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob

KEY = "glittervein"
NAME = "Glittervein"
DESC = ("A hole in the limestone with the water table at the bottom of it, and the only standing "
        "water for a hundred miles in any direction.")
REGION = "Kalimdor - Tanaris"
W, H = 170, 170
BAKED_DIR = "assets/tiles/glittervein/baked"
IS_TOWN = False
BASE_TILE = "sand"
SEED = 4912

TAU = 2.0 * np.pi

#: (86, 100) is the dig mouth on the isle - see THE MOTHER VEIN below.
PORTALS = {(6, 96): "The Abyssal Sands", (86, 100): "The Mother Vein"}
ARRIVALS = [(12, 96)]
START = (12, 96)

#: THE CENOTE. Centre, and the radii of the four levels.
#:
#: R_LIP is where the ground starts to go and R_WATER is the waterline, but the DESCENT runs from
#: R_LIP to R_FLOOR - the spiral ends where the ground levels out, not at the water's edge, and the
#: shore between R_FLOOR and R_WATER is flat. That leaves ONE turn of ramp over twenty-eight tiles
#: of radius: twenty-eight tiles of pitch, fifteen of ramp, thirteen of riser. The ramp has to be
#: wide enough to stand and turn round on or the descent is a corridor rather than a road.
CX, CY = 86, 94
R_LIP, R_WATER = 62.0, 23.0
DEPTH = 46.0
TERRACES = 3

#: THE SPIRAL. One continuous ramp from the rim to the waterline, two and a half turns of it.
#:
#: THE FIRST VERSION WAS THREE SHORT RAMPS CUT STRAIGHT DOWN THE WALL AND THEY WERE NOT WALKABLE.
#: The cone from rim to waterline drops 46 over 39 tiles of radius - a slope of 1.18 against a walk
#: threshold of 0.70 - so a ramp that simply restores the un-terraced profile is a 50-degree face.
#: It came out as rock, terrace 1 was reachable on 66 tiles, and the descent broke at the second
#: step. That is what a real cenote wall is like, which is why real ones need ropes.
#:
#: A QUARRY SPIRAL SOLVES IT THE WAY QUARRIES DO: descend TANGENTIALLY. Two and a half turns at an
#: average radius of forty tiles is about six hundred and sixty tiles of path for a forty-six tile
#: drop, which is a gradient of 0.07.
#:
#: AND THE RAMP'S HEIGHT MUST BE CONSTANT ACROSS ITS WIDTH, which is the part that is easy to get
#: wrong: rock here is the MAGNITUDE of the gradient, not the gradient along the path. If the ramp
#: just exposed the smooth cone, its sideways slope would still be 1.18 and the whole ramp would be
#: rock however gently it descended. So depth on the ramp is a function of how far ALONG the spiral
#: a point is, and does not vary across it at all.
# ONE LAP. Kyle: "so lets not make it too annoying of a spiral, not too tight as that'd be
# annoying. Maybe one layer only." He is right and the earlier number was the designer enjoying the
# mechanism rather than the player walking it - two and a half laps of a hundred-and-seventy-tile
# hole is four hundred tiles of descent every single time you come down here, and there is a camp
# and a dungeon at the bottom that people will visit repeatedly.
#
# One turn over the twenty-eight tiles of radius between the lip and the floor gives a pitch of
# twenty-eight tiles. The ramp band takes fifteen of those and the remaining thirteen are the cliff
# it is cut into. THE PITCH MUST STILL EXCEED THE BAND WIDTH - if it does not, the single pass wraps
# into itself, no riser is left anywhere, and the "spiral" is the bare cone again under another
# name: walkable nowhere, and looking perfectly correct from above the whole time.
SPIRAL_TURNS = 1.0
# A PLATEAU, NOT A TRIANGLE. A mask that falls off linearly from the spiral's centreline makes
# the ramp flat only along one line and sloped everywhere else, because the blend between the ramp
# depth and the cone behind it IS a gradient. The band needs a flat CORE with a short shoulder:
# six tiles either side at full strength, then a tile and a half of transition into the cliff.
RAMP_CORE, RAMP_SHOULDER = 6.0, 1.5

#: Half-width of the clear lane down the ramp's middle. See _ramp_lane.
#:
#: Measured, not guessed. The ramp band is fifteen tiles but only its flat core walks, so the
#: WALKABLE road is about ten tiles wide - and a lane of 3.5 was taking 4009 of the wall's 4323
#: walkable tiles, leaving a 93%-clear road with twenty-six props on it. Two gives a four-tile
#: guaranteed lane and hands the shoulders back to the dressing pass, which is the whole point of
#: having a lane rather than banning scenery from the road outright.
RAMP_LANE = 2.0

#: THE DUNGEON ISLE. (cx, cy, r) - dead centre of the pool, and what the whole descent is for.
#: Kyle: "i want the center of the cenote to be a dungeon." So the middle of the lake is not
#: scenery, it is the destination, and the zone's job is to put the player on it.
#: Widened from seven to eleven because it now has to hold a camp as well as a doorway. Kyle: "I'd
#: like an outpost with quest givers outside of the cenote dungeon too."
DUNGEON_ISLE = (86, 94, 11.0)

#: Rock stacks standing in the water. These are NOT meant to be stood on - they are the bits of the
#: collapsed roof that landed too far out to walk to. Because they are walkable ground with no route
#: to them, seal_unreachable turns them into cliff of its own accord, which is precisely what a
#: limestone stack in a flooded sinkhole is. The sealing pass is doing the modelling here.
STACKS = [(73, 89, 2.5), (98, 101, 2.5)]

ISLES = [DUNGEON_ISLE] + STACKS

#: THE SPIT. A tongue of fallen limestone from the north shore out to the dungeon isle. Without it
#: the centre of the lake is ringed by deep water and the mouth of the dungeon is somewhere the
#: player can see and never reach. It comes in from the NORTH because the spiral lands the player on
#: the EAST shore - so the last thing the descent asks is that they walk the waterline to get to it.
#: It starts INSIDE the shore, not at the floor's edge. Beginning it at r=34 put its landward end
#: exactly on the riser ring, and a spit whose first tile is cliff is a spit nobody can set foot on
#: - one tile, and the dungeon was unreachable.
CAUSEWAY = ((86, 68), (86, 86), 3.2)

#: THE VEINS. (angle, width) - crystal seams running up the inside wall of the hole, which is what
#: the zone is named for and where its resistance gear comes from.
VEINS = [(0.12, 3.0), (0.29, 2.2), (0.55, 3.4), (0.80, 2.6), (0.93, 3.0)]

#: THE FLOOR. Inside this radius the hole has a flat bottom, and that is not a convenience - it is
#: what a cenote is. A sinkhole fills with its own roof: the limestone that fell in is lying down
#: there, graded flat by the water that is still arriving. A cone all the way to the waterline is a
#: funnel, which is a shape water makes going OUT, not a shape it makes standing still.
#:
#: It is also the fix for the last thing wrong with the descent. A 2.5-turn spiral ends where it
#: ends: inward of its final pass the bare cone resumed, at a gradient of 1.18 against a walk limit
#: of 0.70, so the bottom third of the hole was rock with thirty-eight reachable tiles in it. The
#: floor replaces that cone with level ground, the spiral's last pass already ends inside this
#: radius at every bearing, and the two-tile step at the edge becomes one more riser the ramp
#: breaches where it crosses - the same mechanism as every other terrace here.
R_FLOOR = 34.0

RIM_H, RIM_W = 11.0, 11.0

GATES = [((0, 96), (24, 96), 5.5)]


def _wr(gx, gy):
    """Wobbled radius from the centre. A cenote is round-ish, not round."""
    dx, dy = gx - CX, gy - CY
    r = np.hypot(dx, dy)
    ang = np.arctan2(dy, dx)
    lobe = 1.0 + 0.07 * np.sin(ang * 3.0 + 1.1) + 0.04 * np.sin(ang * 5.0 - 0.6)
    # THE WOBBLE HAS TO BE SLOWER THAN THE SPIRAL'S PITCH. This radius is what picks which turn of
    # the descent a tile belongs to - k = round(want - ang) - so a two-tile ripple at frequency 0.05
    # flips that choice back and forth INSIDE the ramp band, and every flip is a full turn's worth of
    # depth, twenty-three units, in one tile. That speckled a quarter of the ramp with rock at every
    # radius, which reads as a ramp with holes in it and measures as a ramp that is mostly cliff.
    # A long, lazy wobble still stops the hole being a circle and never reorders the turns.
    return r / lobe + 1.5 * wob(gx * 0.02, gy * 0.018)


def _spit(gx, gy):
    """>0 on the causeway out to the dungeon isle. Used by water_field to cut it out of the lake,
    and by dress to keep scenery off it - a six-tile spit with a fern in the middle is a wall."""
    (ax, ay), (bx, by), wide = CAUSEWAY
    vx, vy = bx - ax, by - ay
    L2 = float(vx * vx + vy * vy) or 1.0
    tt = np.clip(((gx - ax) * vx + (gy - ay) * vy) / L2, 0.0, 1.0)
    d = np.hypot(gx - (ax + tt * vx), gy - (ay + tt * vy))
    return wide - d + 0.5 * wob(gx * 0.22, gy * 0.2)


def _spiral_geom(gx, gy):
    """(r, r_center, t) for the descending spiral - the ONE place the ramp's position is worked out.
    The ramp mask and the clear lane both need it, and two copies of this arithmetic is exactly how
    a lane ends up running down somewhere the ramp is not."""
    dx, dy = gx - CX, gy - CY
    r = np.maximum(_wr(gx, gy), 0.5)
    ang = (np.arctan2(dy, dx) / TAU) % 1.0            # 0..1 round the hole

    # How many whole turns in is this point? The spiral passes every bearing SPIRAL_TURNS times at
    # different radii, so pick the pass whose radius is nearest to r.
    #
    # THE SPIRAL ENDS AT THE FLOOR, NOT AT THE WATER. Mapping it onto R_LIP..R_WATER while the
    # bottom was flat from R_FLOOR inward left the ramp arriving at a depth of 33 onto a floor at
    # 46 - a thirteen-deep step round the entire shore, which read as rock, which sealed the bottom
    # of the hole. Ending the descent where the ground levels out makes the join exact.
    want = SPIRAL_TURNS * (R_LIP - r) / (R_LIP - R_FLOOR)
    k = np.round(want - ang)
    t = np.clip((ang + k) / SPIRAL_TURNS, 0.0, 1.0)   # 0 at the rim, 1 at the floor
    return r, R_LIP - (R_LIP - R_FLOOR) * t, t


def _spiral(gx, gy):
    """(mask, depth) for the descending spiral.

    mask is 1 on the ramp and falls to 0 off it. depth is how far down the ramp is AT THAT POINT
    ALONG ITS LENGTH - constant across the ramp's width, which is what keeps it walkable.
    """
    r, r_center, t = _spiral_geom(gx, gy)
    mask = np.clip((RAMP_CORE + RAMP_SHOULDER - np.abs(r - r_center)) / RAMP_SHOULDER, 0.0, 1.0)
    # only between the rim and the floor
    mask = np.where((r < R_LIP) & (r > R_FLOOR - 1.0), mask, 0.0)
    return mask, DEPTH * t


def _ramp_lane(gx, gy):
    """True down the middle of the ramp - the lane that stays clear of scenery.

    Banning props from the WHOLE ramp band was the first attempt and it is wrong on this map,
    because on a one-turn spiral the ramp IS the walkable wall: the descent came out as bare rock
    with a hundred and fifty props piled on the rim and the shore. What the road needs is a clear
    middle, not a clear everything - so seven tiles down the centreline take nothing and the
    shoulders either side are dressed like any other ground.
    """
    r, r_center, _t = _spiral_geom(gx, gy)
    return np.abs(r - r_center) < RAMP_LANE


def vein_field(gx, gy):
    """>0 on a crystal seam. Decoration and loot flavour; it does not change the walking."""
    dx, dy = gx - CX, gy - CY
    ang = np.arctan2(dy, dx) / TAU
    r = np.hypot(dx, dy)
    out = np.full(np.shape(gx), -9.0)
    inwall = (r > R_WATER - 2) & (r < R_LIP + 2)
    for (turn, wdt) in VEINS:
        d = np.abs(((ang - turn + 0.5) % 1.0) - 0.5) * TAU * np.maximum(r, 1.0)
        out = np.maximum(out, np.where(inwall, wdt - d, -9.0))
    return out


def _raw_depth(gx, gy):
    """How far down the ground is, before terracing. 0 on the rim, DEPTH at the waterline."""
    r = _wr(gx, gy)
    t = np.clip((R_LIP - r) / (R_LIP - R_FLOOR), 0.0, 1.0)
    return DEPTH * t


def elevation(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)

    # ---- the map's own rim, so the zone is not a square of desert
    dx = np.minimum(gx - RIM_W, (W - 1 - RIM_W) - gx)
    dy = np.minimum(gy - RIM_H, (H - 1 - RIM_H) - gy)
    k = 8.0
    d = -k * np.log(np.exp(-dx / k) + np.exp(-dy / k)) + 6.0 * wob(gx * 0.04, gy * 0.035) \
        + 2.5 * wob(gx * 0.12, gy * 0.1)
    e = 22.0 * np.clip(-d / 11.0, 0.0, None)

    # ---- THE HOLE. Terraced, which is what makes it climbable at all.
    #
    # Quantising the depth into steps gives FLAT TREADS with VERTICAL RISERS between them. The
    # treads come out walkable because they have no slope; the risers come out as rock because they
    # have nothing but slope. That is the entire mechanism, and it is the same fact - rock is
    # derived from gradient - that made a plateau's top walkable in Northern Tanaris and a pit's
    # floor walkable in the Abyssal Sands. Here it is used on purpose instead of being fought.
    # THE WALL IS THE SPIRAL. There is no separate terracing any more and the attempt to have both
    # is what broke this zone twice.
    #
    # The quarry spiral descends one turn every 15.6 tiles of radius, and a ramp wide enough to
    # stand and fight on covers 12 of those - so "the spiral" and "the wall" were already almost the
    # same surface, and what was left between passes was a three-tile strip where the old terraced
    # profile still applied. Those strips became sharp risers against the ramp either side of them,
    # which is how terrace 1 ended up with ONE reachable tile while the ramp itself measured a
    # perfectly walkable 0.07 gradient.
    #
    # So the whole inside of the hole takes the spiral's own depth. That is what a worked quarry
    # looks like from above: not treads with ramps cut into them, but one continuous descending
    # floor that happens to pass under itself, with a single high wall along the seam where the top
    # of one turn meets the bottom of the last.
    ramp, ramp_depth = _spiral(gx, gy)
    r = _wr(gx, gy)
    raw = _raw_depth(gx, gy)

    # ON the band, the spiral's own depth, which is flat across the band's width and so walkable.
    # OFF it, the bare cone - a 50-degree face, which comes out as rock and is the cliff the ramp is
    # cut into. Applying the spiral depth to the WHOLE wall instead was the second failure: the
    # depth then had no radial variation anywhere, so the hole became concentric flat rings with one
    # radial cliff and no ramp at all, and every ring below the first was sealed as unreachable.
    down = ramp_depth * ramp + raw * (1.0 - ramp)

    # The flat bottom, taken over two tiles so the edge is a riser rather than a long shallow
    # gradient. A gradual blend here would be a slope everywhere it was partial, which is exactly
    # the mistake the ramp band made with a triangular mask.
    floorward = np.clip((R_FLOOR - r) / 2.0, 0.0, 1.0)
    down = down * (1.0 - floorward) + DEPTH * floorward

    return e - down


def _slope(gx, gy):
    h = 0.6
    ex = (elevation(gx + h, gy) - elevation(gx - h, gy)) / (2 * h)
    ey = (elevation(gx, gy + h) - elevation(gx, gy - h)) / (2 * h)
    return np.hypot(ex, ey)


WALK_SLOPE = 0.70


def water_field(gx, gy):
    """THE POOL. The whole point of the zone, and the only standing water in the region.

    It sits at the bottom of the hole, inside R_WATER, minus the islands - a lake with nothing to
    stand on in it is a floor you look at.
    """
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    r = _wr(gx, gy)
    w = (R_WATER - r) + 1.5 * wob(gx * 0.09, gy * 0.08)
    for (ix, iy, ir) in ISLES:
        isle = ir - np.hypot(gx - ix, gy - iy) + 0.8 * wob(gx * 0.3, gy * 0.28)
        w = np.where(isle > 0, -9.0, w)

    # THE SPIT, cut out of the water last so nothing can put the water back over it.
    w = np.where(_spit(gx, gy) > 0, -9.0, w)
    return w


def deck_field(gx, gy):
    return np.full(np.shape(gx), -9.0)


def _gate_cut(gx, gy):
    out = np.full(np.shape(gx), -9.0)
    for ((ex, ey), (ix, iy), wide) in GATES:
        d = T.seg_dist(gx, gy, ex, ey, ix, iy)
        out = np.maximum(out, (wide - d) + 0.8 * wob(gx * 0.6, gy * 0.6))
    return out


def cliff_field(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    rock = (_slope(gx, gy) - WALK_SLOPE) * 4.0
    rock = rock - 40.0 * np.clip(_gate_cut(gx, gy), 0, None)
    rock = np.where(water_field(gx, gy) > 0.0, np.minimum(rock, -0.5), rock)
    edge_row = (gy < 1.0) | (gy > H - 2.0) | (gx < 1.0) | (gx > W - 2.0)
    rock = np.where(edge_row & (_gate_cut(gx, gy) <= 0.0), np.maximum(rock, 6.0), rock)
    return rock


def fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    w = water_field(gx, gy)
    return dict(cliff=cliff_field(gx, gy), shallow=w, deep=w - 5.0, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


def road_dist(gx, gy):
    return np.full(np.shape(gx), -9.0)


def paved(gx, gy):
    return road_dist(gx, gy) > 0.0


#: THE DEPTH IS THE LEVEL CURVE. Rim 46, waterline 49 - you get lower and it gets worse, which is
#: the one thing a hole can do that a flat map cannot.
SUBZONES = [
    ("The Dry Rim", 8, 8, 154, 154),
    ("The First Terrace", 30, 38, 112, 112),
    ("The Vein Galleries", 44, 52, 84, 84),
    ("The Green Shelf", 56, 64, 60, 60),
    ("The Waterline", 64, 72, 44, 44),
    # The camp on the isle. It sits INSIDE the Waterline box on purpose - the more specific box
    # wins when a tile is in both, so the player reads "Lastwater" standing in the camp and
    # "The Waterline" standing on the shore twenty tiles away.
    ("Lastwater", 74, 82, 24, 24),
]

BASE = {"sand": 0.40, "hard": 0.26, "clay": 0.20, "rock": 0.14}
PAINT = {}
COBBLE = []
#: LASTWATER. Ten people on the isle, arranged between the spit (which lands at the top) and the
#: dig mouth (which is at the bottom), so a player walks the length of the camp to reach the door.
#: Nobody stands on the line between those two points - an NPC tile is an interaction tile and a
#: person standing in a doorway is a person blocking it.
NPC_POSITIONS = {
    # the north end, where the spit lands
    "gv_surveyor":       (84, 88),
    "gv_tally_clerk":    (89, 87),
    "gv_diver":          (78, 92),
    # the camp proper
    "gv_innkeeper":      (80, 95),
    "gv_quartermaster":  (82, 92),
    "gv_crystal_cutter": (91, 93),
    "gv_reagents":       (93, 96),
    "gv_smith":          (90, 90),
    # the south end, either side of the dig mouth at (86, 100)
    "gv_dig_boss":       (89, 100),
    "gv_pump_chief":     (83, 100),
}
#: One per level of the descent, and every one of them checked in verify(). Two of the first four
#: were sitting inside cliff - a chest in rock is loot the player can never see and nothing in the
#: build complains, because placing a chest on an unwalkable tile is not an error, it is just a
#: waste. They are re-sited whenever the wall changes, which going from two turns to one did to all
#: four of them: a coordinate on a ramp is a coordinate that belongs to that ramp's geometry.
#: They now sit IN THE CLEAR LANE, which is the only ground on the wall that nothing can ever be
#: dropped on - chests are placed after the dressing pass, so a chest on the ramp's shoulder is a
#: chest a fern can bury, and that is a silent loss rather than a crash.
CHESTS = [(46, 132), (67, 51), (119, 112), (58, 94)]
#: What a stalled dig camp has lying around. The underdark set has the survey and excavation props
#: already - they were made for the Codex's dig in the Sunken Archive, and a goblin works stoppage
#: looks much the same from the outside. Placed by hand and checked, never rolled.
CAMP_PROPS = [
    (87, 90, "ud_dig_scaffold"),      # over the shaft head, north of the mouth
    (85, 103, "ud_dig_scaffold"),
    (81, 89, "ud_survey_tripod"),     # Ulla's instruments, at the north end where she stands
    (87, 86, "ud_survey_tripod"),
    (79, 97, "ud_codex_tent"),
    (92, 98, "ud_codex_tent"),
    (84, 94, "ud_field_desk"),        # the tally clerk's book, in the middle of the argument
    (92, 90, "ud_codex_crates"),
    (78, 94, "ud_codex_crates"),
    (94, 93, "ud_specimen_rack"),     # the cutter's stock
    (82, 86, "ud_arcane_brazier"),
    (90, 103, "ud_arcane_brazier"),
]

FOREST = None


def dress(L):
    """Dead on the rim, green at the bottom, and the whole zone is that gradient.

    NOTHING GROWS ON THE RIM AND EVERYTHING GROWS AT THE WATERLINE, with the terraces in between
    getting steadily less dead. That is a cenote: the only reason there is anything alive in this
    part of the world is that the hole is deep enough to reach the water, and the proof of it should
    be visible as a ring that thickens as the player descends.
    """
    z = L.z
    rng = np.random.default_rng(SEED)
    SF = "assets/tiles/shimmering_flats/props/"
    SN = "assets/tiles/southern_needles/props/"
    UD = "assets/tiles/underdark/props/"
    BR = "assets/tiles/barrens/props/"
    A = lambda d, s: d + s + ".png"        # noqa: E731
    n = 0
    for _ in range(9000):
        x = int(rng.integers(3, W - 3))
        y = int(rng.integers(3, H - 3))
        if not z.is_walkable(x, y):
            continue
        # THE ROAD KEEPS ITS LANE. Two hundred and fifty-eight props sealed two thousand six
        # hundred tiles of shore the first time this ran, because the spiral's mouth onto the floor
        # is a seam a few tiles wide and a single boulder in it is a wall. A worked quarry keeps a
        # clear haul road for exactly that reason - but only the MIDDLE of it, or the descent is
        # bare rock the whole way down.
        xa = np.array([[float(x)]])
        ya = np.array([[float(y)]])
        if bool(_ramp_lane(xa, ya)[0, 0]):
            continue
        if abs(float(_wr(xa, ya)[0, 0]) - R_FLOOR) < 4.0:
            continue
        if float(_spit(xa, ya)[0, 0]) > -2.0:        # and off the causeway, for the same reason
            continue
        # AND OFF THE ISLE ENTIRELY. There is a camp and a dungeon mouth on it. Three boulders
        # landed on the middle of it and buried the doorway the descent exists to reach.
        _ix, _iy, _ir = DUNGEON_ISLE
        if np.hypot(x - _ix, y - _iy) < _ir + 1.5:
            continue
        r = float(np.hypot(x - CX, y - CY))
        depth = float(np.clip((R_LIP - r) / (R_LIP - R_WATER), 0.0, 1.0))
        on_vein = float(vein_field(xa, ya)[0, 0]) > 0.0
        roll = rng.random()

        # THE ARCANE FOLLOWS THE SEAMS. Kyle wants "a mixture of tropical / arcane / mystic...so
        # underdark mixed with barrens oasis style", and the cheap way to do that is to shake
        # crystal over the whole map like glitter. The zone already has five crystal seams defined
        # by vein_field - the things it is NAMED for, and where its magic resistance gear comes
        # from - so the crystal goes ON THEM. Then the glow has a geography: a player can see a
        # seam from the rim, follow it down, and find the loot and the ore where the light was.
        if on_vein and roll < 0.34 and depth > 0.10:
            nm = rng.choice(["ud_crystal_cyan", "ud_crystal_violet", "ud_crystal_spire",
                             "ud_lattice_growth", "ud_geode_open", "ud_crystal_float"])
            if L.prop(A(UD, nm), x, y, 5):
                n += 1
            continue

        if depth < 0.15:
            # THE DRY RIM. Desert, and barely that. Nothing glows up here and nothing is green -
            # the whole zone is the argument that the hole is the only reason anything lives, so
            # the top of it has to be dead or the argument is never made.
            if roll < 0.05:
                nm, d = rng.choice([("tan_thorn_scrub", SF), ("tan_dead_palm", SF),
                                    ("sn_boulder_red", SN), ("tan_dune_grass", SF),
                                    ("br_tumbleweed_bones", BR), ("br_dead_tree_vulture", BR)])
                if L.prop(A(d, nm), x, y, 3):
                    n += 1
        elif depth < 0.50:
            # THE TERRACES. Stone, ruin and the first lichen, with the seams starting to show.
            if roll < 0.20:
                nm, d = rng.choice([("cen_mossy_boulder", SF), ("sn_layered_stack", SN),
                                    ("tan_ruin_block", SF), ("cen_roots_shaft", SF),
                                    ("sn_stone_pile", SN), ("ud_lichen_boulder", UD),
                                    ("ud_rune_stone", UD), ("br_sandstone_boulders", BR)])
                if L.prop(A(d, nm), x, y, 4):
                    n += 1
        elif depth < 0.80:
            # THE GREEN SHELF. Where the damp reaches. Fern, vine, moss and the first fungus - the
            # handover band, and the one place both palettes are present in equal measure.
            if roll < 0.30:
                nm, d = rng.choice([("cen_ferns", SF), ("cen_vines", SF), ("cen_roots_shaft", SF),
                                    ("ud_moss_curtain", UD), ("ud_shroom_squat_ochre", UD),
                                    ("ud_shroom_cluster_blue", UD), ("ud_fungal_node", UD),
                                    ("br_mossy_boulder", BR), ("br_golden_grass_tuft", BR)])
                if L.prop(A(d, nm), x, y, 5):
                    n += 1
        else:
            # THE WATERLINE. A Barrens oasis that has been left alone underground for three years
            # with a magic seam running through it: acacia and lilies and standing water, and then
            # a violet mushroom the height of a man and a stone that has not come down yet.
            if roll < 0.34:
                nm, d = rng.choice([("br_umbrella_acacia", BR), ("br_green_oak", BR),
                                    ("acacia_tree", BR), ("nb_lily_cattails", BR),
                                    ("nb_fen_willow", BR), ("cen_fallen_palm", SF),
                                    ("cen_arch", SF), ("cen_ferns", SF),
                                    ("ud_shroom_tall_violet", UD), ("ud_glow_pool", UD),
                                    ("ud_floating_stone", UD), ("ud_shroom_canopy", UD)])
                if L.prop(A(d, nm), x, y, 6):
                    n += 1

    # ===== LASTWATER'S OWN CLUTTER =====
    # Hand-placed, because this is the one part of the map where a prop in the wrong tile closes a
    # camp. Every one of these is checked by verify(), which requires all ten people AND the dig
    # mouth to stay reachable - so a scaffold dropped across the only line to the door fails the
    # build rather than shipping.
    for (px, py, nm) in CAMP_PROPS:
        if L.prop(A(UD, nm), px, py, 5):
            n += 1
    return n


def verify(zone):
    """The descent has to work, and it has to be a spiral rather than a staircase."""
    import collections
    start = START
    seen = {start}
    q = collections.deque([start])
    while q:
        x, y = q.popleft()
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nn = (x + d[0], y + d[1])
            if 0 <= nn[0] < W and 0 <= nn[1] < H and nn not in seen and zone.is_walkable(*nn):
                seen.add(nn)
                q.append(nn)

    # 1) EVERY RING HAS TO BE REACHED. A terrace you cannot get onto is a wall with a view, and the
    #    failure is silent - the zone still looks right from above.
    rings = {}
    for (x, y) in seen:
        r = float(np.hypot(x - CX, y - CY))
        if r > R_LIP:
            rings.setdefault("rim", 0)
            rings["rim"] += 1
        elif r > R_FLOOR:
            tier = int((R_LIP - r) / ((R_LIP - R_FLOOR) / TERRACES))
            rings.setdefault(f"terrace{min(tier, TERRACES - 1)}", 0)
            rings[f"terrace{min(tier, TERRACES - 1)}"] += 1
        else:
            rings.setdefault("floor", 0)
            rings["floor"] += 1
    for t in range(TERRACES):
        assert rings.get(f"terrace{t}", 0) > 200, \
            f"terrace {t} has only {rings.get(f'terrace{t}', 0)} reachable tiles - the descent breaks there"

    # 1b) AND SO HAS THE BOTTOM. The terraces are the journey; the floor is the destination, and it
    #     is where the dungeon mouth is. A descent that stops one riser short is the exact failure
    #     this zone shipped twice, and both times every terrace above it measured fine.
    assert rings.get("floor", 0) > 400, \
        f"the cenote floor has only {rings.get('floor', 0)} reachable tiles - the shore is cut off"

    # 1c) EVERY CHEST AND EVERY PERSON HAS TO BE SOMEWHERE THE PLAYER CAN STAND. Neither of these
    #     is an error at build time - a chest on a cliff tile places perfectly happily and is then
    #     invisible forever, and an NPC spot that fell in rock is a quest giver nobody can reach.
    for (cx_, cy_) in CHESTS:
        assert (cx_, cy_) in seen, f"chest at ({cx_},{cy_}) is not reachable - it is loot in a wall"
    for who, (nx_, ny_) in NPC_POSITIONS.items():
        assert (nx_, ny_) in seen, f"{who} stands at ({nx_},{ny_}), which the player cannot reach"

    # 2) THE DUNGEON ISLE HAS TO BE REACHED, not merely walkable. It is the one tile in this zone
    #    that the entire descent exists to deliver the player to, and it sits in the middle of a
    #    lake - so "there is ground there" is worth nothing on its own. The stacks are deliberately
    #    NOT checked: they are supposed to be cut off, and the sealing pass turns them to cliff.
    ix, iy, _ir = DUNGEON_ISLE
    assert (ix, iy) in seen, \
        f"the dungeon isle at ({ix},{iy}) cannot be reached - the spit is broken"

    # 3) THE SPIRAL HAS TO BE USABLE ALONG ITS WHOLE LENGTH. Two things make this check easy to get
    #    wrong, and this zone hit both.
    #
    #    It must find the band where the band ACTUALLY IS. The ramp is positioned in _wr space - the
    #    lobed, wobbled radius - so stepping out a plain cos/sin radius drifts off it by up to four
    #    tiles and then reports the cliff beside the ramp as the ramp.
    #
    #    And it must test REACHABLE, not walkable. A ramp can be perfectly flat and perfectly
    #    disconnected; walkability is a property of one tile and the thing that matters is whether
    #    the player can get to it. This is the same distinction that let a sealed quay pass in
    #    Steamwheedle and a sealed terrace pass here twice.
    #    And it asks whether the band is passable ACROSS ITS WIDTH, not whether one chosen tile in
    #    it is. The ramp's core is flat for eight tiles, so "the highest-mask tile" is an arbitrary
    #    pick among equals and lands on the tile against the riser about half the time. Picking that
    #    tile reported thirteen breaks in a ramp that every station could in fact be walked.
    blocked = []
    for i in range(int(SPIRAL_TURNS * 12) + 1):
        t = i / (SPIRAL_TURNS * 12)
        a = (t * SPIRAL_TURNS) % 1.0 * TAU
        rr = R_LIP - (R_LIP - R_FLOOR) * t           # the SAME mapping _spiral uses, or this
        passable = False                             # looks eleven tiles from where the ramp is
        for off in np.arange(-8.0, 8.01, 0.5):       # hunt the band across _wr's disagreement
            px = int(round(CX + np.cos(a) * (rr + off)))
            py = int(round(CY + np.sin(a) * (rr + off)))
            if not (0 <= px < W and 0 <= py < H):
                continue
            m = float(_spiral(np.array([[float(px)]]), np.array([[float(py)]]))[0][0, 0])
            if m > 0.5 and (px, py) in seen:
                passable = True
                break
        if not passable:
            blocked.append((int(round(CX + np.cos(a) * rr)), int(round(CY + np.sin(a) * rr))))
    assert len(blocked) <= 1, \
        f"the spiral is impassable at {len(blocked)} of its stations: {blocked[:5]}"

    return dict(reachable=len(seen), rings={k: v for k, v in sorted(rings.items())})


def build_layout():
    return T.build(sys.modules[__name__])


def generate_glittervein():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/glitter_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
