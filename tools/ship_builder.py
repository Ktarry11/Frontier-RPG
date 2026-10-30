"""Ships in plan view, for the Return Voyage's two Bloodsail hulls.

WHY THIS EXISTS. tools/dungeon_builder.Builder draws rooms as unions of
ellipse lobes or chamfered rectangles, and neither is a ship. A hull in plan
view is one continuous fair curve whose bow taper runs about twice the length
of its stern taper, and which is widest somewhat aft of amidships. Two
mirrored chamfers on a rectangle give a lozenge; a union of ellipses gives a
caterpillar. Both read as "a room shaped a bit like a boat", which is worse
than a room, because the player can tell what it was trying to be.

carve_hull walks the hull station by station the way a lines plan does, and
RETURNS THE STATION MAP - {x: (y_top, y_bot)} - so anything that has to sit
on the hull is looked up rather than guessed. Guessing a y near the bow is
how a hatch ends up in the sea, and the sea is not walkable, so the bug
presents as "the dungeon has no second deck" rather than as an error.

THE SEA IS THE WALL. These zones are built with wall_id="tropical_water",
which is flagged walkable: False, so an uncarved tile blocks exactly like
rock and the ship needs no railing tiles to keep the player aboard. This
matters more than it sounds: water is otherwise WALKABLE in this engine (only
tile kind 3 sets collision), so the obvious way to paint a sea zone lets the
player walk off the quarterdeck and keep going to Ratchet.
"""
import math

#: Beam fraction at the very tip of each taper. Not zero: a ship has a stem
#: of some width and a transom of a lot, and tapering either to a point gives
#: a canoe you cannot walk to the end of. The transom is much the wider.
BOW_FILL, STERN_FILL = 0.18, 0.42
#: Where the hull is widest, as a fraction of LOA from the bow. Aft of
#: amidships, which is what makes the shape read as having a direction rather
#: than as a symmetrical blob. It also makes the entry run longer than the
#: run aft, which is how a real hull is proportioned.
MAX_BEAM_AT = 0.58
#: Shape of the run aft. Below 1 holds the hull near full beam for a while
#: before letting go toward the transom.
STERN_POWER = 0.45


def _half_beam(t, beam, bow_first=True):
    """Half-beam at longitudinal position t (0 at the bow end, 1 at the stern).

    TWO TAPERS MEETING AT THE WIDEST STATION, which is the fix for a
    three-piece version that had an entry curve, a flat middle and a run aft.
    Those pieces did not agree at their joins: the entry reached full beam at
    the end of its run while the middle's formula gave 0.94 of it there, so
    the hull stepped IN by a tile just aft of the bow and the station profile
    came out 23, 27, 25, 27 - a hull with a dent in it. Printing the profile
    is the only reason I saw it; it is two tiles on a 27-tile beam and would
    have passed any look at the render.

    Each side is monotonic and both reach exactly 1.0 at MAX_BEAM_AT, so
    there is no join to disagree at. The entry is a sine - leaves the stem at
    an angle, flattens into the widest station. The run aft is a gentler
    power curve, so the ship holds its beam and then lets go.
    """
    if not bow_first:
        t = 1.0 - t
    if t <= MAX_BEAM_AT:
        u = t / MAX_BEAM_AT if MAX_BEAM_AT else 1.0
        frac = BOW_FILL + (1.0 - BOW_FILL) * math.sin(u * math.pi / 2.0)
    else:
        u = (1.0 - t) / (1.0 - MAX_BEAM_AT)
        frac = STERN_FILL + (1.0 - STERN_FILL) * (u ** STERN_POWER)
    return max(1, int(round(beam * frac)))


def carve_hull(b, x0, x1, ycen, beam, bow="w", base="path"):
    """Carve a hull into Builder `b` and return its station map.

    x0..x1 inclusive is the length overall, ycen the centreline, `beam` the
    HALF-beam at the widest station. bow="w" puts the bow at low x (pointing
    west), bow="e" at high x.

    Returns {x: (y_top, y_bot)} - the inclusive deck extent at every station,
    for looking up where a hatch, a portal or a gangplank can actually go.
    """
    assert x1 > x0, "a hull needs length"
    loa = x1 - x0
    stations = {}
    for x in range(x0, x1 + 1):
        t = (x - x0) / loa
        half = _half_beam(t, beam, bow_first=(bow == "w"))
        y_top, y_bot = ycen - half, ycen + half
        stations[x] = (y_top, y_bot)
        for y in range(y_top, y_bot + 1):
            b._open(x, y, base)
    return stations


def bulwark(b, base="dirt"):
    """Paint the outermost walkable tile of a deck in a darker tile.

    A FAIR HULL IS NOT ENOUGH TO READ AS A SHIP. The first render of The
    Crossing had a mathematically correct 3:1 hull in one flat colour and it
    looked like a brown island - the two Bloodsail ships beside it read as
    ships only because they are sprites. What the eye wants is the gunwale:
    the dark line round the edge that says "this is a vessel with sides",
    which a one-colour deck does not have.

    Defined as "any walkable tile with a blocked 8-neighbour" rather than as
    the top and bottom station of each column, because the station map steps
    in and out by a tile or two along the taper and the shoulder tiles that
    exposes would be missed - leaving the gunwale with gaps in it exactly
    where the hull curves, which is where it most needs to be seen.
    """
    z = b.zone
    edge = []
    for y in range(b.h):
        for x in range(b.w):
            if not z.is_walkable(x, y):
                continue
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if not (0 <= nx < b.w and 0 <= ny < b.h) or not z.is_walkable(nx, ny):
                        edge.append((x, y))
                        break
                else:
                    continue
                break
    for (x, y) in edge:
        z.set_tile(x, y, base, "base")
    return len(edge)


def platform(b, x0, y0, x1, y1, base="stone"):
    """Re-tile a rectangle of existing deck - a forecastle, a quarterdeck, a
    hatch surround. Only repaints tiles that are already walkable, so a
    platform specified a little too wide spills into the sea as nothing at
    all rather than as deck hanging over the water."""
    n = 0
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if 0 <= x < b.w and 0 <= y < b.h and b.zone.is_walkable(x, y):
                b.zone.set_tile(x, y, base, "base")
                n += 1
    return n


def afloat(L, path, cx, base_y, height):
    """Place a ship sprite over WATER, bypassing the dry-floor guard.

    Kyle: "ensure the boat is not on the land and its in the water - we enter
    it through a ramp (portal)." He is right, and the reason every moored ship
    on these maps had been sitting on the sand is CaveLayout.prop, which
    refuses any prop whose base tile is not dry walkable floor. That guard is
    correct for a barrel and exactly wrong for a ship: a ship's base tile
    SHOULD be water.

    So this goes to Builder.prop underneath it. Nothing is lost by skipping
    the guard here - the sprite is decorative (solid=False), it cannot block
    anything, and the tile it anchors to is sea the player could never stand
    on anyway. The way aboard is a carved ramp with the portal on it.
    """
    L.b.prop(path, cx, base_y, height, solid=False)
    L.placed += 1
    return True


def gangplank(b, x, y_from, y_to, base="path", width=1):
    """A walkway running north or south at column x, inclusive of both ends.

    Carved AFTER the hull, so it reaches out over water that is otherwise the
    zone's wall. width>1 spreads either side of x.
    """
    lo, hi = (y_from, y_to) if y_from <= y_to else (y_to, y_from)
    half = (width - 1) // 2
    for y in range(lo, hi + 1):
        for dx in range(-half, width - half):
            b._open(x + dx, y, base)
    return [(x, y) for y in range(lo, hi + 1)]


def bulkhead(b, stations, x, gap_lo, gap_hi):
    """Seal station x except for a doorway from gap_lo to gap_hi inclusive.

    THIS IS WHAT MAKES A HULL A DUNGEON. A ship below decks is one long open
    space, and one long open space has no pull structure - every fight is the
    same fight at a different x. Bulkheads cut it into compartments, and the
    doorway is the pull point.

    Returns the number of tiles sealed, which the caller should check is
    non-zero: a bulkhead whose doorway is wider than the hull at that station
    is a wall with nothing either side of it, and connectivity tests pass on
    it happily.
    """
    if x not in stations:
        raise ValueError(f"station {x} is not on this hull "
                         f"({min(stations)}..{max(stations)})")
    y_top, y_bot = stations[x]
    sealed = 0
    for y in range(y_top, y_bot + 1):
        if gap_lo <= y <= gap_hi:
            continue
        b.zone.set_tile(x, y, b.wall_id, "collision")
        sealed += 1
    return sealed


#: Offsets a pack's members take around its lead, in placement order. Not a
#: block or a ring: a boarding party or a watch below decks stands in a loose
#: clump, and a tidy formation is the tell that a generator placed it. The
#: first entry is the lead's own tile.
FAN = [(0, 0), (2, -1), (-2, 1), (0, -3), (0, 3), (2, 2), (-2, -2)]


def place_packs(zone, specs, rad=6, spacing=2):
    """Flatten pack specs into the (x, y, name, level) list a zone wants.

    specs = [(cx, cy, level, [name, ...]), ...]

    Each member is nudged to the nearest walkable tile within `rad` and kept
    at least `spacing` tiles from any member already placed, so two members
    never share a tile and a pack never collapses into a line when the clump
    lands half over water. Raises if a member cannot be placed at all, rather
    than dropping it - a pack quietly coming out one mob short is the kind of
    thing nobody notices until the dungeon feels easy.
    """
    out = []
    taken = set()

    def free(x, y):
        return (zone.is_walkable(x, y)
                and all(max(abs(x - px), abs(y - py)) >= spacing
                        for (px, py) in taken))

    for (cx, cy, level, names) in specs:
        for i, name in enumerate(names):
            ox, oy = FAN[i % len(FAN)]
            tx, ty = cx + ox, cy + oy
            spot = None
            if free(tx, ty):
                spot = (tx, ty)
            else:
                best = None
                for dy in range(-rad, rad + 1):
                    for dx in range(-rad, rad + 1):
                        nx, ny = tx + dx, ty + dy
                        if free(nx, ny):
                            d = dx * dx + dy * dy
                            if best is None or d < best[0]:
                                best = (d, nx, ny)
                if best:
                    spot = (best[1], best[2])
            if spot is None:
                raise AssertionError(
                    f"{zone.name}: no free tile for '{name}' near "
                    f"({tx}, {ty}) within {rad} - the pack at ({cx}, {cy}) "
                    f"would have come out short")
            taken.add(spot)
            out.append((spot[0], spot[1], name, level))
    return out
