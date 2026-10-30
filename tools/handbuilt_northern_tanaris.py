"""
Hand-built Northern Tanaris (240x110): the first zone of Tanaris. 41-44.

Kyle, 2026-10-30, drawing on the region map: "Top part is first entrance to tanaris... So it'll be 3
zones." Northern Tanaris is the top strip. The Abyssal Sands are the southwest and Glittervein - the
cenote, "similar stuff to the underdark" - is the southeast. Neither of those is built yet.

THE REGION IS THE GAME'S FIRST CONTENT ABOVE 40, and the ladder Kyle set is 41-44 here, 44-47 in the
Abyssal Sands, 46-49 in Glittervein. Before this, tools/audit_quests.py reported "NOTHING TO DO at
level(s): 43-60" - the game simply stopped. Two consequences that do not apply anywhere else yet:
magic resistance gear becomes legal at 45, so it belongs to the Sands and Glittervein and NOT to this
zone; and the upper ore and wood tiers have been sitting unused waiting for exactly these zones.

THE SHAPE IS A WIDE SHALLOW STRIP AND THAT IS THE POINT. Every zone in this region so far has been
taller than it is wide and has read as a journey north to south. This one reads EAST TO WEST, because
everything in it is strung along one road: you drop out of the mountains in the middle, the dead city
is west of you, the live port is east of you, and the whole zone is the walk between those two.

GADGETZAN IS RUINS AND ZUL'FARRAK IS RUBBLE. Kyle: "Gadetzan sucks. Let's trash it. Actually let's
trash ZF because fuck that place." Both are landmarks you walk through rather than content:

  GADGETZAN RUINS   where you arrive, which is a deliberate first impression. The first thing a player
                    sees of Tanaris is a goblin city that did not make it, and the second thing is a
                    road leading away from it toward one that did. That contrast IS the zone.
  ZUL'FARRAK        a troll step pyramid broken open down one side. NOT ENTERABLE - no instance, no
                    interior, no dungeon. It is skyline and it is a warning, and the fact that you can
                    walk right up to it and find nothing to do there is the statement.

ONE ROAD, AND IT IS THE ONLY STRUCTURE IN THE MIDDLE. The first draft of this zone put the cenote in
the centre to give the desert something to be about; Kyle moved the cenote to Glittervein, which left
the middle empty. A flat desert with nothing between two landmarks is a long boring walk, so the road
has to carry it alone - which means the things strung along it have to be worth stopping at. Hence
Kyle: "We can have some ruins as well, troll ruins, animal bones etc. A road is fine too."

THE SOUTH EDGE IS TWO DIFFERENT THINGS, which is the most interesting line in Kyle's drawing: a solid
mountain range on the east half and a dotted open border on the west. So there is exactly ONE way
south out of this zone and it is on the west, and the east half is sealed - which is what makes the
Abyssal Sands feel like somewhere you choose to go rather than somewhere you fall into.

HARD CONTRACT (world/portal_manager.py):
    (92, 2)    <-> The Shimmering Flats  - down out of the north range
    (216, 56)  <-> Steamwheedle Port     - the main town, its own map. ON THE QUAY: the shelf
                                           is deep water from x=226 east, so a portal any
                                           further out is a portal in the sea.
    (200, 88)  <-> The Drownbell         - the pirate cove, south of the port. A CAVE, not a dungeon.
    (60, 108)  <-> The Abyssal Sands     - the one way south. UNREGISTERED until that zone exists.
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob

KEY = "northern_tanaris"
#: Must match the name registered in create_all_zones - portal_manager keys on zone.name.
NAME = "Northern Tanaris"
DESC = ("Desert between a city that died and a port that did not, with one road running the length of "
        "it and a great deal of bone either side.")
REGION = "Kalimdor - Tanaris"
W, H = 240, 110
BAKED_DIR = "assets/tiles/northern_tanaris/baked"
IS_TOWN = False
BASE_TILE = "sand"
SEED = 4190

TAU = 2.0 * np.pi

#: The Abyssal Sands gate is carved and walkable and NOT registered, exactly as the Flats' Tanaris pass
#: was for two zones before this file existed. Southern Needles did the same thing with the road it
#: left pointing east. A pass that goes nowhere is better than a wall you have to re-cut later.
PORTALS = {(92, 2): "The Shimmering Flats",
           (216, 56): "Steamwheedle Port",
           (200, 88): "The Drownbell"}
ARRIVALS = [(92, 8), (216, 54), (200, 86), (60, 102)]
START = (92, 8)

# =========================================================================================================
# THE TWO RANGES.
#
# NORTH is a full-width wall with one notch in it - the Shimmering Flats are on the far side, and the
# notch is the only way between the two zones. SOUTHEAST is the bottom-right block Kyle drew, and it
# does two jobs: it seals the east half of the south edge, and it is what the pirate cove is cut into.
# =========================================================================================================
NORTH_H = 22.0          # how far down the north wall reaches
SE_H = 26.0             # the southeast block's height

#: Notches. (edge point, inward point, width) - each cuts through a range in exactly one place.
GATES = [
    ((92, 0), (92, 34), 5.0),        # down out of the Flats, into Gadgetzan
    ((60, 110), (64, 92), 5.5),      # THE ONE WAY SOUTH, west half. Unregistered until Abyssal Sands.
    # THE COVE IS APPROACHED FROM INSIDE THE ZONE, walking south out of the port - Kyle: "Pirate cove
    # entrance is bottom right of zone 1. So south of steamwheedle." The first cut ran UP from the
    # south map edge, which made the approach a cul-de-sac whose only opening was off the side of the
    # world: seal_unreachable found a pocket connected to nothing and walled it, and the zone's only
    # cave quietly stopped existing. Nothing threw, and tile_kind still said the tiles were walkable.
    ((200, 78), (200, 90), 3.0),     # a SHORT, NARROW mouth into the southeast block - Kyle: "a
                                     # small entrance in the south east, it doesn't need to take up
                                     # that much space". The cave itself is a separate map.
]

# =========================================================================================================
# THE LANDMARKS. (name, cx, cy, rx, ry, height) - low broken ground, not mountains. These are RUINS:
# they want to read as something that fell over, which means wide and low rather than tall and sharp.
# =========================================================================================================
#: GADGETZAN'S WALL. Kyle: "We also need to ensure the ruins of gadgetzan are there. So walls and
#: destroyed buildings with the goblins moved to steamwheedle."
#:
#: THE WALL IS TERRAIN, NOT PROPS, and that is the whole reason this reads. Gadgetzan was a WALLED
#: town and a walled town is recognisable from above in one glance - a ring, and a gap where the ring
#: has failed. Scattering wall sprites across a flat patch gives you rubble on sand; a real ring that
#: really blocks gives you a town that fell over, and the player understands it before reading a word.
#:
#: It is a RECTANGLE because goblins build square, and it is BROKEN IN FOUR PLACES: the two gates
#: that were always there (the pass road in from the north, the caravan road out to the east) and two
#: breaches that were not. A player can tell the difference between a gate and a hole, and the two
#: holes are the only thing in this zone that says what actually happened here.
# NOTE thick IS A HALF-WIDTH - the ring runs from -thick to +thick either side of the perimeter
# line, so the wall on the ground is twice this. Set to 2.8 it came out five to six tiles through,
# which is a rampart, not a town wall, and the corners rendered as solid blocks.
GAD = dict(x0=76, y0=30, x1=118, y1=58, thick=1.3, height=9.0)

#: (x, y, radius) - where the ring is down. The two road gaps carve themselves, because the road
#: flattens whatever it crosses; these are the two that are damage.
#: NOTE the damage reaches about TWICE the radius - the wall is killed outright inside it and fades
#: back in over the same distance again, which is what a collapse looks like and is easy to
#: under-count. At 6.0 the west breach took nineteen tiles of wall out, not twelve.
BREACHES = [(76, 46, 4.5),      # west wall, stove in
            (104, 58, 5.0)]     # south wall, the long collapse

RUINS = [
    # HEIGHT 24, NOT 9. At 9 the flanks sloped under WALK_SLOPE and the whole pyramid was walkable
    # ground - it rendered as nothing at all in the shape preview, which is what a landmark that is
    # not actually there looks like. A step pyramid is steep; that is the only reason it reads.
    ("Zul'Farrak", 36, 58, 22, 24, 24.0),         # the step pyramid, broken open down one side
    # The ground inside the walls only - low, because you walk THROUGH the city, not over it. The
    # walls themselves are a separate term below.
    # HEIGHT 1.2, NOT 3.0. At 3.0 the mound's own falloff put a slope over WALK_SLOPE around its
    # rim, which planted a ring of cliff INSIDE the walls - 37 tiles of unexplained rock in the
    # middle of a town square. The ground inside a ruined city is just ground; the walls do the work.
    ("Gadgetzan", 97, 44, 19, 13, 1.2),
]

#: Where the pyramid is broken open, as a fraction of a turn. The cut crosses the ruin's flank in one
#: place, same trick the Flats' hive tunnels use - without it the mound is a sealed cone and scenery.
ZF_BREACH = 0.62

# =========================================================================================================
# THE ROAD. Gadgetzan to the port, with one spur going south.
#
# It is the zone's only structure and so it is routed to be worth walking: out of the ruins, east along
# the open sand, and into the port - with the spur peeling off south-west toward the sands. The spur
# DIES at the border rather than arriving anywhere, which is honest about what is built.
# =========================================================================================================
ROADS = {
    "caravan": ([(97, 52), (120, 58), (150, 56), (178, 54), (202, 56), (216, 56)], 3.6),
    "south_spur": ([(120, 58), (104, 74), (84, 88), (66, 98), (60, 106)], 3.0),
    "zf_track": ([(97, 48), (78, 46), (62, 50), (50, 54)], 2.6),   # the old way out to the pyramid
}


def _poly_dist(gx, gy, pts):
    d = np.full(np.shape(gx), 1e9)
    for a, b in zip(pts, pts[1:]):
        d = np.minimum(d, T.seg_dist(gx, gy, a[0], a[1], b[0], b[1]))
    return d


def road_dist(gx, gy):
    out = np.full(np.shape(gx), -9.0)
    for (pts, wide) in ROADS.values():
        out = np.maximum(out, wide * 0.5 - _poly_dist(gx, gy, pts))
    return out


def paved(gx, gy):
    return road_dist(gx, gy) > 0.0


def _gate_cut(gx, gy):
    """>0 inside a gate - a notch cut through a range."""
    out = np.full(np.shape(gx), -9.0)
    for ((ex, ey), (ix, iy), wide) in GATES:
        d = T.seg_dist(gx, gy, ex, ey, ix, iy)
        out = np.maximum(out, (wide - d) + 0.8 * wob(gx * 0.6, gy * 0.6))
    return out


def _breach_cut(gx, gy):
    """>0 inside Zul'Farrak's broken face - the one way into the pyramid's footprint."""
    _n, cx, cy, rx, ry, _h = RUINS[0]
    a = ZF_BREACH * TAU
    ex, ey = cx + np.cos(a) * (rx + 7), cy + np.sin(a) * (ry + 7)
    d = T.seg_dist(gx, gy, cx, cy, ex, ey)
    return (4.2 - d) + 0.7 * wob(gx * 0.8, gy * 0.8)


def water_field(gx, gy):
    """THE SEA, on the east edge only, and it is the zone's one piece of water.

    Tanaris has no cenote in it any more - Kyle moved that to Glittervein in the southeast - so unlike
    every other desert zone in this region the only water here is the one that was always going to be
    here, which is the ocean the port is a port FOR. That is also why Steamwheedle survived and
    Gadgetzan did not: one of them was on a trade route that does not depend on the desert working.
    """
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    # THE SHORELINE WOBBLES, WITHIN LIMITS. Unclamped it wandered east past x=229 at the top and
    # bottom of the map, which left a strip of walkable beach at the north and south map borders -
    # four tiles a player could stand on at the edge of the world, in each corner.
    shore = np.clip(224.0 + 3.0 * wob(gy * 0.35, gx * 0.1), 218.0, 225.0)
    return gx - shore


def deck_field(gx, gy):
    return np.full(np.shape(gx), -9.0)


def _softmin(a, b, k=8.0):
    """A rectangle's distance field is min(dx, dy) and no amount of wobble hides the four square
    corners it produces - the Flats learned this and had to be rebuilt around a soft-min. Same here."""
    return -k * np.log(np.exp(-a / k) + np.exp(-b / k))


def elevation(gx, gy):
    """Flat desert at zero, two ranges standing on it, two ruins sagging into it."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    e = np.zeros(np.shape(gx), float)

    # ---- THE NORTH RANGE: full width, one notch. Wobbled hard so its southern face is a coastline
    # rather than a ruled line - it is the first thing a player sees and a straight edge would say
    # "box" before they have taken three steps.
    # NO UPPER CLIP, AND THAT IS THE WHOLE SEAL. Clipped at 1.0 this term makes a plateau, and a
    # plateau's TOP IS FLAT - rock here is derived from slope, so the flat top is walkable and the
    # map border runs straight along it. The first build of this zone had 435 open edge tiles for
    # exactly that reason, on three sides, and the shape preview looked completely correct because a
    # plateau and a wall are the same picture from above. Letting it climb without bound keeps the
    # gradient constant all the way off the edge, so the slope stays over WALK_SLOPE and it is rock.
    south_face = 26.0 + 7.0 * wob(gx * 0.055, gy * 0.05) + 3.0 * wob(gx * 0.17, gy * 0.14)
    e = np.maximum(e, NORTH_H * np.clip((south_face - gy) / 14.0, 0.0, None))

    # ---- THE SOUTHEAST BLOCK: Kyle's solid line. Seals the east half of the south edge and holds the
    # cove. Soft-min against the two edges it is built from so the inner corner is a shoulder.
    dx = gx - (146.0 + 6.0 * wob(gy * 0.08, gx * 0.06))
    dy = gy - (80.0 + 7.0 * wob(gx * 0.06, gy * 0.07))
    e = np.maximum(e, SE_H * np.clip(_softmin(dx, dy, 9.0) / 16.0, 0.0, None))

    # ---- THE WEST DUNE RIDGE: Kyle's dotted line. NOT mountains - a low ridge you cross at one place.
    # The asymmetry is the whole point of his drawing: the east half is a wall, the west half is a
    # border, and a player should be able to feel the difference without being told.
    ridge = 7.0 + 2.5 * wob(gx * 0.09, gy * 0.08)
    e = np.maximum(e, ridge * np.clip((gy - (96.0 + 5.0 * wob(gx * 0.07, gy * 0.05))) / 9.0, 0.0, None)
                   * np.clip((150.0 - gx) / 20.0, 0.0, 1.0))

    # ---- THE WEST EDGE: low broken ground so the map does not simply stop.
    e = np.maximum(e, 9.0 * np.clip((9.0 + 3.0 * wob(gy * 0.12, gx * 0.1) - gx) / 7.0, 0.0, None))

    # ---- GADGETZAN'S WALL RING. Distance to the rectangle's perimeter, raised into a thin wall,
    # with the breaches cut back out of it.
    G = GAD
    inside = np.minimum(np.minimum(gx - G["x0"], G["x1"] - gx),
                        np.minimum(gy - G["y0"], G["y1"] - gy))
    # A WALL IS BUILT, SO IT IS STRAIGHT. The first version wobbled it by +/-0.9 against a 2.2
    # thickness, which is most of the wall, and what came out wandered like a hedgerow - the one
    # shape that reads instantly from above was thrown away to avoid looking artificial. Artificial
    # is the point: a straight line in a desert is a thing somebody made. Ruin comes from the
    # BREACHES, not from making the whole run crooked.
    perim = np.abs(inside) + 0.3 * wob(gx * 0.5, gy * 0.5)
    wall = np.clip(1.0 - perim / G["thick"], 0.0, 1.0)
    for (bx, by, br) in BREACHES:
        wall = wall * np.clip(np.hypot(gx - bx, gy - by) / br - 1.0, 0.0, 1.0)
    e = np.maximum(e, G["height"] * wall)

    # ---- THE RUINS. Low and wide: these fell over, they were not pushed up.
    for (_n, cx, cy, rx, ry, h) in RUINS:
        r = np.hypot((gx - cx) / rx, (gy - cy) / ry)
        e = np.maximum(e, h * np.clip(1.25 - r, 0.0, 1.0) * (0.75 + 0.25 * wob(gx * 0.3, gy * 0.3)))

    # the road never climbs anything
    e = np.where(road_dist(gx, gy) > -0.6, np.minimum(e, 0.4), e)
    return e


def _slope(gx, gy):
    h = 0.6
    ex = (elevation(gx + h, gy) - elevation(gx - h, gy)) / (2 * h)
    ey = (elevation(gx, gy + h) - elevation(gx, gy - h)) / (2 * h)
    return np.hypot(ex, ey)


WALK_SLOPE = 0.62


def cliff_field(gx, gy):
    """Rock is slope. The gates and the pyramid's breach cut through it."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    rock = (_slope(gx, gy) - WALK_SLOPE) * 4.0
    # strong enough to beat the tallest thing on the map - Southern Needles sealed its own only route
    # with a cut tuned against the shallow mesas, and nothing caught it until a player could not walk.
    rock = rock - 40.0 * np.clip(_breach_cut(gx, gy), 0, None)
    # THE OUTER ROW, WHERE A RANGE MEETS THE SEA. Everything above seals the border by SLOPE, which
    # works everywhere except the two points where the north range and the southeast block run down
    # into the water: there the water term cancels the rock, and what is left is a couple of tiles of
    # dry land at the very corner of the map. Three tiles, in the one place the two sealing mechanisms
    # hand over to each other - which is exactly where this kind of hole always is.
    #
    # Chasing it by moving the coast west worked and cost the zone a column of map each time, so the
    # outer row is simply declared rock instead. Only dry land: the sea is already impassable and
    # painting stone into it would be a worse answer than the hole. Gates are cut back out below.
    # THE GATES ARE CUT LAST, AFTER THE BORDER SEAL, or the seal closes the north gate behind them.
    # Strong enough to beat the tallest thing on the map - Southern Needles sealed its own only route
    # with a cut tuned against the shallow mesas, and nothing caught it until a player could not walk.
    rock = rock - 40.0 * np.clip(_gate_cut(gx, gy), 0, None)
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    # ONLY ACTUAL WATER CANCELS ROCK. At > -1.0 this also cancelled it for the tile of dry land just
    # inshore, so where a range runs down to the sea the beach under it came out walkable and the map
    # border with it.
    rock = np.where(water_field(gx, gy) > 0.0, np.minimum(rock, -0.5), rock)

    # THE OUTER ROW GOES LAST, AFTER the water cancel, and that ordering is the whole fix.
    #
    # Everything above seals the border by SLOPE, which works everywhere except the two points where
    # the north range and the southeast block run down into the sea. Three tiles survived every
    # attempt, and the reason took a while: they are not dry land at all, they are SHALLOW WATER,
    # which is walkable. A seal that skipped water skipped exactly the tiles that were leaking, and
    # pulling the coastline west to escape them cost the zone a column of map each time and moved
    # the hole rather than closing it.
    #
    # So the ranges are allowed to run INTO the water at the top and bottom edges, as headlands.
    # Deep water is left alone - it is already impassable and stone painted across the open sea
    # would be a worse answer than the hole was.
    edge_row = (gy < 1.0) | (gy > H - 2.0)
    not_deep = np.maximum(water_field(gx, gy) - 3.0, gx - 226.0) <= 0.0
    headland = edge_row & not_deep & (_gate_cut(gx, gy) <= 0.0)
    rock = np.where(headland, np.maximum(rock, 6.0), rock)
    return rock


def fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    w = water_field(gx, gy)
    # DEEP WATER IS FORCED PAST x=234, whatever the shoreline wobble does. The wobble is what gives
    # the coast its shape, and at the top and bottom of the map it pushed the shore far enough east
    # to leave a walkable sliver of sand OUTSIDE the sea, in both corners - four tiles of beach a
    # player could stand on at the very edge of the world. The shoreline stays wobbled; the water
    # behind it does not get a vote.
    # DEEP PAST x=228, not merely "three tiles out from the wobbled shore". SHALLOW WATER IS
    # WALKABLE, so a shallow fringe reaching the north or south map border is a leak exactly like a
    # beach would be - the player stands in ankle-deep sea at the edge of the world. The visible
    # shallows are whatever the wobble leaves between the shoreline and here, which is nought to
    # seven tiles and still reads as a coast.
    deep = np.maximum(w - 3.0, gx - 226.0)
    return dict(cliff=cliff_field(gx, gy), shallow=w, deep=deep, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


#: West to east is the walk, not the level ladder - this zone is one band. The subzones exist so the
#: encounter tables can differ by where you are, and so the rares have somewhere to live (rares only
#: spawn in subzones; see tools/qa_rare_placement.py).
SUBZONES = [
    ("Zul'Farrak Ruins", 12, 32, 52, 54),
    ("Gadgetzan Ruins", 74, 28, 48, 34),
    ("The Caravan Road", 118, 44, 62, 28),
    ("The Bonefields", 70, 68, 76, 34),
    ("Steamwheedle Approach", 184, 34, 44, 44),
    ("The Drownbell Shore", 160, 76, 68, 30),
]

BASE = {"sand": 0.52, "hard": 0.24, "clay": 0.14, "rock": 0.10}
PAINT = {}
COBBLE = []
NPC_POSITIONS = {}
CHESTS = [(40, 62), (104, 46), (152, 58), (196, 84)]
FOREST = None


#: GADGETZAN'S DEAD BUILDINGS, hand-placed. (sprite, x, y, height, solid)
#:
#: PLACED, NOT SCATTERED, because a town has a LAYOUT and rubble does not. The street is the caravan
#: road running through at y~52; the trade buildings face it; the zeppelin tower is down across the
#: north end, which is the thing you see first coming out of the pass. Random placement here would
#: produce a field of broken houses, which reads as a disaster area rather than as a town that people
#: walked out of - and they walked out, they were not buried. Kyle: "the goblins moved to steamwheedle."
GADGETZAN_BUILDINGS = [
    # the zeppelin tower, down. First thing you see coming out of the pass.
    ("zep_tower_goblin", 92, 36, 16, "core"),
    # the trade row, facing the street from the north
    ("gazlowes_office", 84, 44, 11, "core"),
    ("bud_ruined_house", 97, 43, 9, "core"),
    ("scrapyard_workshop", 109, 44, 11, "core"),
    # the south side of the street
    ("bud_ruined_house", 88, 56, 9, "core"),
    ("ek_burnt_cottage", 101, 56, 8, "core"),
    ("bud_ruined_tower", 112, 55, 13, "core"),
    # the east gate, where the caravan road leaves for Steamwheedle
    ("ek_ruined_gatehouse", 118, 52, 12, "core"),
]


def _gadgetzan(L):
    """The walls are terrain; this is what is left standing inside them."""
    n = 0
    for (sprite, x, y, h, solid) in GADGETZAN_BUILDINGS:
        if L.prop(f"assets/buildings/{sprite}.png", x, y, h, solid=solid):
            n += 1
    return n


def dress(L):
    """Desert, and what is lying in it.

    THE DENSITY IS THE STORY. Nearly bare in the open sand, thick in three places - the pyramid, the
    dead city, and the bonefields either side of the road. Kyle: "We can have some ruins as well,
    troll ruins, animal bones etc." The bones cluster ON the road because that is where things walked
    until they stopped, and a player who notices the bone density rises as the road goes on has read
    the zone correctly without anybody telling them.
    """
    z = L.z
    n = _gadgetzan(L)
    rng = np.random.default_rng(SEED)
    # KEEP CLEAR OF THE WAYS IN AND OUT. dress() blocks the tile it decorates, and the Drownbell's
    # portal sat inside the bonefield band - a rib cage rolled onto it and sealed the only cave in
    # the zone. Nothing threw: a portal on a blocked tile is just a portal you cannot reach.
    KEEPOUT = list(PORTALS) + ARRIVALS
    SN = "assets/tiles/southern_needles/props/"
    SF = "assets/tiles/shimmering_flats/props/"
    A = lambda d, s: d + s + ".png"        # noqa: E731
    for _ in range(3000):
        x = int(rng.integers(3, W - 3))
        y = int(rng.integers(3, H - 3))
        if not z.is_walkable(x, y):
            continue
        if any(abs(x - px) <= 3 and abs(y - py) <= 3 for px, py in KEEPOUT):
            continue
        r = rng.random()
        near_zf = (x < 66) and (28 < y < 92)
        near_gad = (72 < x < 124) and (26 < y < 66)
        on_road = 40 < y < 96 and 60 < x < 210
        if near_zf:                                       # the pyramid: troll stone and old bone
            if r < 0.26:
                nm = rng.choice(["tan_ruin_block", "tan_obelisk", "tan_skeleton", "sn_cairn",
                                 "sn_layered_stack", "sn_stone_pile", "tan_dead_palm"])
                if L.prop(A(SF if nm.startswith("tan_") else SN, nm), x, y, 4):
                    n += 1
        elif near_gad:                                    # the dead city: goblin wreckage
            if r < 0.24:
                nm = rng.choice(["sf_scrap_heap", "sf_crate_stack", "sf_fuel_drums", "sf_wheel_stack",
                                 "sf_condenser", "tan_ruin_block", "sf_signboard"])
                if L.prop(A(SF, nm), x, y, 4):
                    n += 1
        elif on_road:                                     # the bonefields
            if r < 0.11:
                nm = rng.choice(["tan_skeleton", "sn_rib_bones", "sn_kodo_skull", "tan_ruin_block",
                                 "tan_thorn_scrub", "sn_dead_shrub"])
                if L.prop(A(SF if nm.startswith("tan_") else SN, nm), x, y, 3):
                    n += 1
        else:                                             # open sand: nearly bare
            if r < 0.045:
                nm = rng.choice(["tan_dune_grass", "tan_thorn_scrub", "tan_dead_palm", "sn_boulder_red",
                                 "sn_dead_shrub"])
                if L.prop(A(SF if nm.startswith("tan_") else SN, nm), x, y, 3):
                    n += 1
    return n


def build_layout():
    return T.build(sys.modules[__name__])


def generate_northern_tanaris():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/tanaris_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
