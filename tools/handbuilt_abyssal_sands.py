"""
Hand-built The Abyssal Sands (180x160): Tanaris zone 2. 44-47.

Kyle drew the region as three zones and named this one: "We can call them abyssal sands and the
cenote can be called Glittervein". It is the southwest block, below Northern Tanaris and west of
the divider, running down toward Uldum.

THE NAME DECIDED THE ZONE, AND SO DID THE WATER CHAIN THAT WAS ALREADY WRITTEN.

Four zones have each put down a piece of the same story without any of them planning to. The Aspen
has somebody watching the melt get bigger every spring. Southern Thousand Needles asks where that
water goes and gets no answer. The Shimmering Flats has the answer - it goes under, and east. And
Northern Tanaris has a walled city that died of thirst when the table tipped.

A DROPPING WATER TABLE DOES ONE MORE THING, and it is the obvious next sentence that nobody in those
four zones is in a position to say: when the water that was holding up a limestone floor leaves, THE
FLOOR FALLS IN. Not slowly. A sinkhole opens in an afternoon.

So this zone is the ground that gave way. Eleven collapse pits across a hundred and eighty tiles of
desert, none of them there four years ago, and the walking between them is the zone. That is also
why it is the one Tanaris zone with no town and no road: there was a road, it is in a hole, and
nobody has surveyed a new line because nobody is confident the ground they would survey will still
be there next season.

THE PITS ARE IMPASSABLE AND THE NAVIGATION IS THE CONTENT. A desert with nothing in it is a long
walk; a desert you have to think about crossing is a map. Every pit is a wall you can see over,
which is the opposite of a mountain and reads completely differently from above - the player can
see exactly where they want to be and has to work out how to get there.

HARD CONTRACT (world/portal_manager.py):
    (60, 2)    <-> Northern Tanaris  - down out of zone 1, the one way in from the north
    (176, 96)  <-> Glittervein       - east through the divider. UNREGISTERED until that zone exists.
    (46, 158)  <-> Uldum             - south. UNREGISTERED; there is no Uldum.
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob

KEY = "abyssal_sands"
NAME = "The Abyssal Sands"
DESC = ("Desert that has started falling into itself. Eleven holes that were not here four years "
        "ago, and no road left between them.")
REGION = "Kalimdor - Tanaris"
W, H = 180, 160
BAKED_DIR = "assets/tiles/abyssal_sands/baked"
IS_TOWN = False
BASE_TILE = "sand"
SEED = 4471

TAU = 2.0 * np.pi

#: Only the north gate is registered. The other two are carved and walkable and point at zones that
#: do not exist - exactly what the Flats did with the pass that now goes to Tanaris, and what
#: Southern Needles did with the road that pointed at the Flats.
#: The east gate to Glittervein was carved and walkable and deliberately unregistered for two
#: passes, exactly as the Flats' south pass was before Tanaris existed. Glittervein exists now.
PORTALS = {(60, 2): "Northern Tanaris", (176, 96): "Glittervein"}
ARRIVALS = [(60, 8), (170, 96), (46, 152)]
START = (60, 8)

#: THE PITS. (name, cx, cy, rx, ry, rim) - rim is how far the raised lip extends past the hole.
#:
#: SPREAD, NOT CLUSTERED, and deliberately sized up toward the east. A field of identical holes is
#: a texture; eleven holes of different sizes with the big ones where the limestone was deepest is
#: a place that something happened TO. The two biggest sit either side of the east divider, which
#: is the direction Glittervein lies in - the ground is worst where the water went.
PITS = [
    ("The First Hole", 44, 34, 11, 9, 4.0),
    ("Cartfall", 78, 28, 9, 8, 3.5),
    ("The Wide Sink", 62, 66, 15, 13, 5.0),
    ("Nineteen Mile Pit", 104, 48, 10, 9, 4.0),
    ("The Throat", 36, 92, 9, 12, 4.5),
    ("Glasswall", 120, 84, 13, 11, 4.5),
    ("The Long Collapse", 84, 112, 19, 10, 5.0),
    ("Deadfall", 142, 58, 11, 9, 4.0),
    ("The Second Throat", 52, 130, 10, 9, 4.0),
    ("Underlight", 148, 116, 16, 14, 5.5),
    ("The Last Hole", 116, 142, 12, 10, 4.5),
]

#: THE ONE DESCENDABLE PIT. Every other hole is a wall; this one has a ramp of its own collapse
#: debris down one side, and it is the zone's only interior. A field of eleven sealed holes with no
#: way into any of them is a field of eleven pieces of scenery.
DESCENT = ("The Wide Sink", 0.28)

#: The rim mountains. North is the wall against zone 1, east is Kyle's divider, and west and south
#: run toward Uldum.
# MEASURED, NOT GUESSED. At 26/20 with the wobble below, the rim alone was 56% of the map
# against the pits' 21% - a zone whose defining feature is eleven holes came out as a thin ring of
# desert inside a very thick mountain. The rim's job here is only to close the edge; the pits are
# what the player is supposed to be navigating.
RIM_H, RIM_W = 12.0, 9.0

GATES = [
    ((60, 0), (60, 26), 5.0),        # down out of Northern Tanaris
    ((180, 96), (156, 96), 5.0),     # east to Glittervein. Unregistered.
    ((46, 160), (48, 136), 5.0),     # south toward Uldum. Unregistered.
]


def _pit_field(gx, gy):
    """>0 inside a hole. The pits are the zone's walls, so this is most of its shape."""
    out = np.full(np.shape(gx), -9.0)
    for (_n, cx, cy, rx, ry, _rim) in PITS:
        dxp, dyp = (gx - cx) / rx, (gy - cy) / ry
        # AN ANGULAR TERM, NOT JUST A WOBBLED EDGE. Adding noise to the distance field gives a
        # crinkled ellipse, which from above still reads as an ellipse - the first render came out
        # as eleven neat ovals and looked like a pattern rather than like damage. Varying the RADIUS
        # with angle makes the hole genuinely lopsided: wider on one side, bitten in on another,
        # which is what a collapse actually does.
        ang = np.arctan2(dyp, dxp)
        # NOTE this term can only ADD radius, never subtract - at 0.22/0.13/0.08 it inflated every
        # pit by up to 43% and took the zone from 37% walkable to 21%, sealing the east gate. Kept
        # modest, and the base radii in PITS are scaled to match.
        lobe = (1.0 + 0.15 * np.sin(ang * 3.0 + cx * 0.7)
                + 0.09 * np.sin(ang * 5.0 - cy * 0.9)
                + 0.05 * np.sin(ang * 8.0 + cx * 0.3))
        r = np.hypot(dxp, dyp) / lobe
        out = np.maximum(out, (1.0 - r) * 6.0 + 0.9 * wob(gx * 0.22, gy * 0.20))
    return out


def _rim_lip(gx, gy):
    """The raised ring of spoil round each hole - what came up when the floor went down."""
    out = np.zeros(np.shape(gx))
    for (_n, cx, cy, rx, ry, rim) in PITS:
        dxp, dyp = (gx - cx) / rx, (gy - cy) / ry
        ang = np.arctan2(dyp, dxp)
        # NOTE this term can only ADD radius, never subtract - at 0.22/0.13/0.08 it inflated every
        # pit by up to 43% and took the zone from 37% walkable to 21%, sealing the east gate. Kept
        # modest, and the base radii in PITS are scaled to match.
        lobe = (1.0 + 0.15 * np.sin(ang * 3.0 + cx * 0.7)
                + 0.09 * np.sin(ang * 5.0 - cy * 0.9)
                + 0.05 * np.sin(ang * 8.0 + cx * 0.3))
        r = np.hypot(dxp, dyp) / lobe
        band = np.clip(1.0 - np.abs(r - 1.06) / (rim / max(rx, ry)), 0.0, 1.0)
        out = np.maximum(out, band)
    return out


def _descent_cut(gx, gy):
    """>0 on the one ramp down into the Wide Sink - its own debris, fallen in a slope."""
    name, turn = DESCENT
    for (n, cx, cy, rx, ry, _rim) in PITS:
        if n != name:
            continue
        a = turn * TAU
        ex, ey = cx + np.cos(a) * (rx + 8), cy + np.sin(a) * (ry + 8)
        d = T.seg_dist(gx, gy, cx, cy, ex, ey)
        return (5.0 - d) + 0.8 * wob(gx * 0.7, gy * 0.7)
    return np.full(np.shape(gx), -9.0)


def _gate_cut(gx, gy):
    out = np.full(np.shape(gx), -9.0)
    for ((ex, ey), (ix, iy), wide) in GATES:
        d = T.seg_dist(gx, gy, ex, ey, ix, iy)
        out = np.maximum(out, (wide - d) + 0.8 * wob(gx * 0.6, gy * 0.6))
    return out


def water_field(gx, gy):
    """NO WATER. That is the entire point of the zone and of the region's whole water story - the
    water left, which is why the floor fell in. Glittervein, east of here, is where it comes back."""
    return np.full(np.shape(gx), -9.0)


def deck_field(gx, gy):
    return np.full(np.shape(gx), -9.0)


def _softmin(a, b, k=9.0):
    return -k * np.log(np.exp(-a / k) + np.exp(-b / k))


def elevation(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    e = np.zeros(np.shape(gx), float)

    # THE RIM, all the way round, soft-min so the corners are shoulders rather than right angles -
    # the Flats had to be rebuilt once for using a plain min() here. NO UPPER CLIP: clipped it makes
    # a plateau, a plateau's top is flat, and a flat top is walkable right off the edge of the map.
    dx = _softmin(gx - RIM_W, (W - 1 - RIM_W) - gx)
    dy = _softmin(gy - RIM_H, (H - 1 - RIM_H) - gy)
    d = _softmin(dx, dy) + 6.0 * wob(gx * 0.035, gy * 0.03) + 3.0 * wob(gx * 0.1, gy * 0.09) \
        + 1.5 * wob(gx * 0.28, gy * 0.25)
    e = np.maximum(e, 24.0 * np.clip(-d / 13.0, 0.0, None))

    # the spoil rings. Low, but enough to read as a lip you climb over to look in.
    e = np.maximum(e, 4.5 * _rim_lip(gx, gy))

    # THE HOLES. Negative elevation, steeply, which is what makes them walls - rock here is slope,
    # and the inside wall of a pit is the steepest ground on the map.
    pit = _pit_field(gx, gy)
    e = e - 26.0 * np.clip(pit, 0.0, None)
    return e


def _slope(gx, gy):
    h = 0.6
    ex = (elevation(gx + h, gy) - elevation(gx - h, gy)) / (2 * h)
    ey = (elevation(gx, gy + h) - elevation(gx, gy - h)) / (2 * h)
    return np.hypot(ex, ey)


WALK_SLOPE = 0.60


def cliff_field(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    rock = (_slope(gx, gy) - WALK_SLOPE) * 4.0

    # THE FLOOR OF A PIT IS NOT WALKABLE EITHER, and slope alone will not say so: the middle of a
    # big hole is FLAT, exactly like the top of a plateau, so it comes out as perfectly good ground
    # at the bottom of a cliff you cannot climb. Every pit except the one with a ramp is blocked
    # outright, which is also what makes them read as holes rather than as craters with floors.
    pit = _pit_field(gx, gy)
    rock = np.maximum(rock, 8.0 * np.clip(pit + 0.6, 0.0, 1.0))

    rock = rock - 40.0 * np.clip(_descent_cut(gx, gy), 0, None)
    rock = rock - 40.0 * np.clip(_gate_cut(gx, gy), 0, None)

    # the outer row, as headland/wall, after everything else - ordering matters, see Northern Tanaris
    edge_row = (gy < 1.0) | (gy > H - 2.0) | (gx < 1.0) | (gx > W - 2.0)
    rock = np.where(edge_row & (_gate_cut(gx, gy) <= 0.0), np.maximum(rock, 6.0), rock)
    return rock


def fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    w = water_field(gx, gy)
    return dict(cliff=cliff_field(gx, gy), shallow=w, deep=w - 3.0, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


def road_dist(gx, gy):
    """NO ROAD. There was one and it is in a hole, and there is still not a new one - Fourth Peg
    is eight people trying to find out whether one is POSSIBLE, which is a different job with a
    different answer and only one of those has ever been funded. Nobody has surveyed a line because
    confident the ground they would survey will still be there next season."""
    return np.full(np.shape(gx), -9.0)


def paved(gx, gy):
    return road_dist(gx, gy) > 0.0


#: North to south is the walk and the difficulty curve - the ground gets worse the further you go
#: from the one gate you came in by.
SUBZONES = [
    ("The First Hole", 22, 16, 56, 48),
    ("Cartfall", 60, 14, 48, 34),
    ("The Wide Sink", 30, 46, 62, 48),
    ("The Glasswall", 96, 60, 56, 52),
    ("The Throats", 18, 76, 54, 70),
    ("The Long Collapse", 54, 96, 72, 56),
    ("Underlight", 118, 96, 58, 58),
    # The camp. Flagged "safe" in encounters.json - a subzone with no roster of its own falls
    # through to the parent zone's table AND rolls at 5% a step against the open zone's 2%, so
    # without the flag the quietest place on the map is the most dangerous one.
    ("Fourth Peg", 128, 16, 26, 22),
]

BASE = {"sand": 0.50, "hard": 0.26, "clay": 0.14, "rock": 0.10}
PAINT = {}
COBBLE = []
#: FOURTH PEG. A road survey camp, pitched around the fourth stake because the first three are all
#: in holes. Up on the northeast flat, which is the furthest any ground on this map sits from a
#: pit - thirty-five tiles from the nearest one, measured rather than eyeballed.
#:
#: THIS DOES NOT GIVE THE ZONE A TOWN OR A ROAD. There is still no road; there are eight people
#: trying to find out whether one is possible, in tents, on four carts they can strike in a day.
#: The docstring's claim stands: nobody has surveyed a new LINE, because every line they have
#: pegged so far has been overtaken by the ground before it could be finished.
NPC_POSITIONS = {
    "ab_surveyor":     (140, 25),      # the peg itself is here, and so is she
    "ab_rodman":       (145, 23),
    "ab_teamster":     (134, 24),
    "ab_digger":       (147, 28),
    "ab_quartermaster": (136, 29),
    "ab_cook":         (140, 30),
    "ab_smith":        (144, 30),
    "ab_reagents":     (132, 27),
}
CHESTS = [(34, 22), (96, 36), (28, 110), (134, 100)]
FOREST = None


def dress(L):
    """A desert with holes in it, and what the holes took.

    THE PROPS CLUSTER ON THE RIMS, which is both true and useful. True because a collapse throws its
    own spoil up in a ring and everything that was standing nearby ends up in that ring. Useful
    because the rim is where the player walks - they are following the edge of a hole trying to get
    round it, so that is where the detail should be. The open sand between pits is nearly bare and
    should feel like it.
    """
    z = L.z
    rng = np.random.default_rng(SEED)
    SF = "assets/tiles/shimmering_flats/props/"
    SN = "assets/tiles/southern_needles/props/"
    A = lambda d, s: d + s + ".png"        # noqa: E731
    n = 0
    gy_, gx_ = np.mgrid[0:H, 0:W]
    lip = _rim_lip(gx_ + 0.5, gy_ + 0.5)
    for _ in range(3600):
        x = int(rng.integers(3, W - 3))
        y = int(rng.integers(3, H - 3))
        if not z.is_walkable(x, y):
            continue
        r = rng.random()
        on_rim = lip[y, x] > 0.25
        if on_rim:
            if r < 0.22:
                nm = rng.choice(["tan_ruin_block", "tan_skeleton", "sn_rib_bones", "sn_stone_pile",
                                 "sn_layered_stack", "sf_scrap_heap", "sn_cairn", "tan_obelisk"])
                if L.prop(A(SF if nm.startswith("tan_") or nm.startswith("sf_") else SN, nm),
                          x, y, 4):
                    n += 1
        elif r < 0.035:
            nm = rng.choice(["tan_thorn_scrub", "tan_dune_grass", "tan_dead_palm", "sn_boulder_red"])
            if L.prop(A(SF if nm.startswith("tan_") else SN, nm), x, y, 3):
                n += 1
    return n


def verify(zone):
    """The things about this zone that could quietly stop being true."""
    import collections
    # 1) every pit must actually be a hole - blocked in the middle, not a crater with a floor
    open_floors = []
    for (name, cx, cy, _rx, _ry, _rim) in PITS:
        if name == DESCENT[0]:
            continue
        if zone.is_walkable(cx, cy):
            open_floors.append(name)
    assert not open_floors, f"these pits have walkable floors and are craters, not holes: {open_floors}"

    # 2) the one descendable pit must actually be descendable FROM OUTSIDE
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
    # RESOLVED BY NAME UP FRONT, NOT INSIDE A LOOP THAT CAN SKIP ITSELF.
    #
    # This check used to be `for pit in PITS: if pit.name == DESCENT[0]: assert reachable`. A
    # negative control that broke the ramp by renaming DESCENT made the loop body never run at all,
    # so the assertion was never evaluated and verify() reported everything fine - a check that
    # silently disables itself in exactly the circumstance it exists to catch. The control found it;
    # nothing else would have.
    target = [p for p in PITS if p[0] == DESCENT[0]]
    assert len(target) == 1, (f"DESCENT names {DESCENT[0]!r}, which is not one of the pits - the "
                              f"zone has no descendable hole at all")
    _n, dcx, dcy, _rx, _ry, _rim = target[0]
    assert (dcx, dcy) in seen, (f"{DESCENT[0]}'s ramp does not reach its floor - the zone's only "
                                f"interior is sealed")
    # 3) every gate's arrival has to be reachable, or a pass leads nowhere
    for a in ARRIVALS:
        assert a in seen, f"arrival {a} is not reachable from the start"
    return dict(pits=len(PITS), sealed=len(PITS) - 1, reachable=len(seen))


def build_layout():
    return T.build(sys.modules[__name__])


def generate_abyssal_sands():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/sands_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
