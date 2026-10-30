"""
Hand-built layout for the Gurbashi Arena (104x104): an OCTAGONAL ARENA with a WALLED-OFF CENTRE.

Kyle, 30 Oct 2026, after looking at the first build (five chambers stacked in a vertical line):
"the center is walled off and you go through bosses counter clockwise until the 4th boss is slain,
then you go in the middle to the final boss.  So a boss at 10 o'clock.  Then 7 o'clock, then 5, then
3 then middle."

THE SHAPE.  A thick outer wall, a faceted eight-sided corridor cut inside it, and a round inner hall
ringed with columns sitting in the middle of all of it.  You come down the stair at twelve o'clock,
step through the gate onto the sand, and the ring takes you round.

    (52,12) stair head and EXIT portal ....... you arrive at (52,10)
    the ring .... centreline radius 30 from (52,56), corridor about 12 wide, cut as STRAIGHT
                  segments between the octagon's vertices so the walls read as faces, not as a curve
    the wall .... everything between radius 15 and radius 24 is left uncut.  That band is the
                  inner hall's wall, and it is why you cannot see or reach the last fight from the ring
    the hall .... radius 15 at (52,56).  Carved stone, eight columns, one gate

WHY THE UPPER-RIGHT FACE IS SOLID.  The ring is NOT a loop.  The two faces that would run from twelve
o'clock clockwise round to three o'clock - 270 to 315 and 315 to 0 - were never cut.  They are still
rock.  Standing at the gate you have exactly one direction to walk, anticlockwise, and the boss at
three o'clock is a dead end jammed up against the back of that uncut rock.  Nothing about the walk is
a suggestion: there is no second route, so the order the four are fought in is the order they are
built in, and the only reason you ever reach the centre gate is that you walked past all four to get
to it.  Take that face out and the arena becomes a racetrack where a party can skip to the easiest
pull and work backwards, which is a different dungeon.

    order  clock  angle   tile        who
      1     10     210    (26, 41)    Vek'tar the Unbeaten
      2      7     120    (37, 82)    Grateward Mok'tal
      3      5      60    (67, 82)    Rakjan the Ribcracker (+ Jin'sha the Bloodcaller)
      4      3       0    (75, 56)    Zul'gar Hammerfall          <- dead end against the solid face
      5    centre   -     (52, 56)    Jen'shala, the House Favourite

    the gate ..... one radial passage at angle 0, tube (76,56) -> (66,56), five wide.  It is the only
                   cut through the wall band, and it opens off the four's dead end.  THE FOUR STANDS
                   IN ITS MOUTH, at (75,56), not out at the vertex at (82,56): the dead end is twelve
                   wide and the face runs into it at a slant, so a boss parked out in the middle of
                   that sand had the gate hanging off his flank - a party could walk round him and
                   into the hall with him still alive.  (75,56) is the last tile going inward that
                   the sand does not reach: stand him there and he IS the doorway.  The sequence
                   check below is what found that, and it found it by failing.

WHAT A GAUNTLET IS, AND WHAT IT IS NOT.  Five bosses and NOTHING between them.  The moment you pad
the walk with pulls it stops being a gauntlet and becomes a short dungeon with thin trash, which is
the worst version of both.  So there is no trash list in this module and no trash table in the
encounter block: zone.fixed_spawns stays True (so the per-tile random roll in OverworldScreen never
fires here) and the encounter table contains bosses only, which leaves world/cave_spawns.populate()
with an empty `trash` dict and nothing to scatter.

THE CROWD.  Four alcoves bulge outward through the back of the outer wall, one behind each ring boss,
at radius 40.  Tiered benches, a rack of spare weapons, the cage the pair are kept in, the stoker's
fire - that is the rim, and it is the only part of this place not trying to kill you.  It is where
the chests are, because the Gurbashi keep the stakes where the people who bet them can see them.

WHY YOU ARE DOWN HERE.  You did not break in.  The Gurbashi still run the pits, they still take
entries, and somebody in Booty Bay has already written your name on a board and taken money on it.
Every station is somebody's livelihood: the drum crew at the first, the grate stoker at the second,
the pair-handlers at the third.  Nobody here is trying to stop you reaching the middle - they are
trying to make sure the rim gets its money's worth on the way.

HARD CONTRACTS (world/portal_manager.py: Central Stranglethorn (150,100) -> Gurbashi Arena (52,12);
the return side is wired elsewhere and is deliberately NOT added here).
    zone.is_cave = True, region "Eastern Kingdoms - Stranglethorn", size 104x104, band 36-38.
    Exit portal (52,12) and arrival (52,10) are both walkable and both inside the stair head.

ART.  Nothing here waits on new art.  Floors and walls are baked by tools/bake_gurbashi_arena.py out
of Stranglethorn's own material set (NOT the Durotar desert set - that lit the whole arena orange),
and every prop below is an existing sprite from assets/tiles/stranglethorn/props/ or the shared
dungeon props: the arena benches, gate, standards and weapon rack, the troll columns, the idol the
house bets under, the stoker's brazier, the pair's cage.

Prop rule (Kyle): less is more.  Two or three centrepieces per station, each one logical for that
station.  The eight columns in the hall are the exception and they are structure, not decoration.
Every placement goes through CaveLayout.prop, which refuses anything sitting on a marker or anything
that would wall a tile off.

VERIFICATION.  tools/verify_gurbashi_arena.py flood-fills from the arrival tile and proves (1) every
boss, the portal and every chest is reachable, (2) reachable == walkable, so there are no pockets,
(3) walling station N drops bosses N+1..5 off the map, which is the gauntlet property, and (4) you
cannot reach three o'clock by walking clockwise out of the stair.
"""
import math
import os

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import tube

NAME = "Gurbashi Arena"
DESC = ("A Gurbashi fighting pit sunk under Stranglethorn: an eight-sided sand ring, a crowd in every "
        "alcove, and a walled hall in the middle that nobody opens until the ring is empty.")
REGION = "Eastern Kingdoms - Stranglethorn"
SP = "assets/tiles/stranglethorn/props/"
W, H = 104, 104
BAKED = "assets/tiles/gurbashi_arena/{}/baked"
SLUG = "arena"

LEVEL_BAND = (36, 38)

# ------------------------------------------------------------------ the octagon
PORTAL = (52, 12)                 # EXIT portal (hard contract)
ARRIVAL = (52, 10)                # where the player lands coming in (hard contract)
CENTRE = (52, 56)

RING_R = 30                       # centreline radius of the eight-sided corridor
RING_W = 12                       # corridor width
HALL_R = 15                       # inner hall radius; the band 15..24 is left as rock
ALCOVE_R = 40                     # how far out behind a boss the crowd sits


def pol(r, deg, cx=CENTRE[0], cy=CENTRE[1]):
    """Screen-convention polar: 0 = right, 90 = down, 270 = up."""
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


#: The octagon's vertices, in ORDER OF TRAVEL out of the stair.  270 is the gate at twelve o'clock;
#: the chain ENDS at 0 (three o'clock).  There is deliberately no 315 vertex and no 0 -> 270 closing
#: segment: the upper-right pair of faces is the uncut rock that makes this a gauntlet.
RING_DEG = [270, 225, 180, 135, 90, 45, 0]
RING_VERTS = [pol(RING_R, d) for d in RING_DEG]

#: Each boss: (x, y, name, travel-direction unit vector along the ring at that tile).  The direction
#: is what the sequence check walls across - a two-tile slab cut square through the corridor at the
#: boss's feet, which is what "you cannot get past this fight" means geometrically.
BOSSES = [
    (26, 41, "Vek'tar the Unbeaten", (-9, 21)),              # 10 o'clock, on the 225->180 face
    (37, 82, "Grateward Mok'tal", (21.2, 8.8)),              #  7 o'clock, on the 135->90 face
    (67, 82, "Rakjan the Ribcracker", (21.2, -8.8)),         #  5 o'clock, on the 90->45 face
    (75, 56, "Zul'gar Hammerfall", (-1, 0)),                 #  3 o'clock, IN the gate mouth
    (52, 56, "Jen'shala, the House Favourite", (0, 0)),      #  the hall
]

#: How far across the corridor the sequence check's slab runs, per station.  Three o'clock is the one
#: exception and it has to be: the other three have their crowd alcove bulging RADIALLY OUTWARD from
#: the ring, which is sideways to the direction of travel, so the slab has to run out through the
#: alcove or a party walks boss -> benches -> back onto the sand behind it.  At three o'clock travel
#: has already turned inward along the gate, so the alcove is behind the boss rather than beside him
#: and a 10-tile slab is the whole cross-section.  Running it to the map edge there would clip the
#: tail of the five o'clock face twenty tiles away and pass the check for the wrong reason.
BLOCK_LEN = {3: 10}

#: The add at five o'clock.  It is NOT a pinned boss station - it is the second member of a PACK, so
#: stepping onto Rakjan's stretch of sand pulls both at once and the fight is a target-priority
#: problem rather than two tidy duels.  See world/cave_spawns.populate(): pinned chambers and
#: zone.trash_packs are laid out by separate passes, so the pack places Rakjan and the pinned list
#: leaves him out.
ADD = (62, 82, "Jin'sha the Bloodcaller")

#: The crowd alcoves, one behind each ring boss, bulging outward through the back of the outer wall.
ALCOVES = [(17, 36), (32, 90), (72, 90), (92, 56)]

#: One chest per boss.  The four ring chests sit in the alcove behind their fight (the Gurbashi keep
#: the stakes where the rim can see them); the fifth is on the hall floor.
CHESTS = [(13, 36), (32, 94), (72, 94), (96, 56), (52, 66)]

#: The one cut through the wall band, at angle 0, opening off three o'clock's dead end.
GATE = [(76, 56), (66, 56)]
GATE_W = 5

#: Eight columns round the hall, set on the half-facets so the gate at 0 and the idol at 270 each
#: stand in a gap rather than behind a column.
COLUMN_R = 12
COLUMN_DEG = [22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.5, 337.5]

#: Station name -> the rectangle it owns, for the subzone pass.  Names kept from the first build
#: because they are the fights, not the floorplan: the grate stoker is still the grate stoker.
STATIONS = [
    ("The Sand Gate",    43,   5, 22, 24),
    ("The Opening Bout",  7,  26, 28, 24),
    ("The Hot Grate",    22,  72, 28, 28),
    ("The Pairing",      56,  72, 28, 28),
    ("The Hard Round",   74,  42, 28, 28),
    ("The House Floor",  36,  40, 33, 33),
]


def boss_block_tiles(zone, index, half_thick=1.5, inner_r=20):
    """Tiles to wall off to stand boss `index` in the way.  Used by the sequence check only.

    A slab cut square across the ring at the boss's feet: `half_thick` deep along the direction of
    travel and running the full width of the map across it, minus everything inside `inner_r` of the
    arena's centre.

    THE SLAB HAS TO REACH THE BACK OF THE ALCOVE.  First attempt capped it at 10 tiles either side,
    which covers the 12-wide corridor and nothing else - and the check passed while the layout was
    broken, because the crowd alcove bulges outward right behind the boss and a party could walk
    boss -> alcove -> back onto the ring on the far side of the slab.  So it runs outward to the map
    edge instead.  The inner cap is the other half of that: the ring's inner lip never comes closer
    than 21 to the centre, so stopping at 20 spans the whole corridor while leaving the wall band and
    the inner hall untouched - a slab that clipped the hall would disconnect the last fight for a
    reason that has nothing to do with the gauntlet.
    """
    bx, by, _n, (ux, uy) = BOSSES[index]
    L = math.hypot(ux, uy) or 1.0
    ux, uy = ux / L, uy / L
    half_len = BLOCK_LEN.get(index)
    out = set()
    for y in range(zone.height):
        for x in range(zone.width):
            dx, dy = x - bx, y - by
            if abs(dx * ux + dy * uy) > half_thick:
                continue
            if half_len is not None and abs(dx * -uy + dy * ux) > half_len:
                continue
            if math.hypot(x - CENTRE[0], y - CENTRE[1]) < inner_r:
                continue
            out.add((x, y))
    return out



# ------------------------------------------------------------------ straight-edged carving
# The organic helpers (cavern / tube / lobes) spline and wobble their edges, which is right for a cave
# and wrong for this: the Gurbashi BUILT the ring, and a splined corridor makes laid stone read as a
# worm hole.  These three cut clean - a regular polygon, a polygon annulus, and a square-sided
# corridor - so the arena comes out faceted the way masonry is.

def _ngon(px, py, r, n=8, phi=-math.pi / 2, cx=CENTRE[0], cy=CENTRE[1]):
    """Inside a regular n-gon of circumradius r, vertices starting at angle phi."""
    a = r * math.cos(math.pi / n)
    vx, vy = px - cx, py - cy
    for k in range(n):
        th = phi + (k + 0.5) * 2 * math.pi / n
        if vx * math.cos(th) + vy * math.sin(th) > a:
            return False
    return True


def poly_fill(b, r, base=None):
    """Open every tile inside a regular octagon centred on CENTRE."""
    for y in range(max(0, int(CENTRE[1] - r - 2)), min(H, int(CENTRE[1] + r + 3))):
        for x in range(max(0, int(CENTRE[0] - r - 2)), min(W, int(CENTRE[0] + r + 3))):
            if _ngon(x, y, r):
                b._open(x, y, base)


def poly_band(b, r_in, r_out, deg_lo, deg_hi, base=None):
    """Open the octagonal annulus between two radii, but only over an arc.  The arc is what leaves
    the upper-right pair of faces as solid rock."""
    for y in range(max(0, int(CENTRE[1] - r_out - 2)), min(H, int(CENTRE[1] + r_out + 3))):
        for x in range(max(0, int(CENTRE[0] - r_out - 2)), min(W, int(CENTRE[0] + r_out + 3))):
            if not _ngon(x, y, r_out) or _ngon(x, y, r_in):
                continue
            ang = math.degrees(math.atan2(y - CENTRE[1], x - CENTRE[0])) % 360
            if deg_lo <= ang <= deg_hi:
                b._open(x, y, base)


def seg(b, a, c, w, base=None):
    """A square-sided corridor from a to c."""
    (x0, y0), (x1, y1) = a, c
    half, dx, dy = w / 2.0, c[0] - a[0], c[1] - a[1]
    dd = dx * dx + dy * dy or 1.0
    for y in range(max(0, int(min(y0, y1) - half - 2)), min(H, int(max(y0, y1) + half + 3))):
        for x in range(max(0, int(min(x0, x1) - half - 2)), min(W, int(max(x0, x1) + half + 3))):
            t = max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / dd))
            if math.hypot(x - (x0 + t * dx), y - (y0 + t * dy)) <= half:
                b._open(x, y, base)


def build_arena():
    zone = Tilemap(NAME, W, H, DESC)
    zone.is_cave = True
    #: .region declares the PARENT ZONE for the encounter lookup (world/zone_manager.py) - pinned by
    #: the hard contract, and tools/build_gurbashi_content.py writes the cave table under this key.
    zone.region = REGION
    #: TRUE, unlike every single-boss cave in the game: a gauntlet must not have the open world's
    #: random per-tile roll firing between stations.  With a boss-only encounter table this also
    #: means populate() has no trash to scatter, which is exactly the shape Kyle asked for.
    zone.fixed_spawns = True

    L = CaveLayout(zone, ARRIVAL)
    b = L.b

    # --- the stair head at twelve o'clock, and the hall down to the sand
    seg(b, (PORTAL[0], PORTAL[1] - 3), (PORTAL[0], PORTAL[1] + 2), 9)
    seg(b, PORTAL, RING_VERTS[0], 10)

    # --- THE RING, cut as a true octagonal annulus over the arc 0..270.  Six faces, hard corners,
    #     and the two faces between 270 and 360 - the upper right - never cut at all.  That uncut
    #     pair is the whole gauntlet: out of the stair the only way is anticlockwise.
    poly_band(b, RING_R - RING_W / 2, RING_R + RING_W / 2, 0, 270)

    # --- the crowd's alcoves.  These ARE organic: the Gurbashi laid the ring, the crowd dug itself
    #     pits through the back of it, and the two should not look like the same hands did them.
    for (ax, ay) in ALCOVES:
        b.lobes([(ax, ay, 9, 7)])

    # --- the inner hall, and the single radial gate that reaches it
    poly_fill(b, HALL_R)
    seg(b, GATE[0], GATE[1], GATE_W)

    # --- subzones: whole map first so each station's own name overrides it
    zone.add_subzone(NAME, 0, 0, W, H)
    for (key, x, y, w, h) in STATIONS:
        zone.add_subzone(key, x, y, w, h)

    # --- markers
    L.mark("portal", *PORTAL)
    for (x, y, _n, _d) in BOSSES:
        L.mark("boss_marker", x, y)
    for c in CHESTS:
        L.mark("chest", *c)

    #: Four PINNED stations.  Rakjan is missing on purpose: he arrives with his handler as a pack
    #: (zone.trash_packs below).  With no unpinned chambers in this list nothing ever draws from the
    #: shared boss pool, so he cannot also be spawned a second time somewhere else.
    zone.boss_positions = [(x, y, n) for (x, y, n, _d) in BOSSES if n != "Rakjan the Ribcracker"]
    zone.boss_position = (BOSSES[0][0], BOSSES[0][1])
    zone.trash_packs = [[
        (BOSSES[2][0], BOSSES[2][1], BOSSES[2][2], 37),
        (ADD[0], ADD[1], ADD[2], 36),
    ]]

    # --- props.  Two or three per station, each one somebody's job.
    p = L.prop
    # The Sand Gate: the stair you came down, the gate onto the sand, a standard either side of it.
    p("stv_troll_steps", 52, 8, 5, where=SP)
    p("stv_arena_standard", 48, 18, 6, where=SP, solid="core")
    p("stv_arena_standard", 56, 18, 6, where=SP, solid="core")
    p("stv_arena_gate", 52, 24, 7, where=SP)
    # The Opening Bout, ten o'clock: the drum crew start every bout, the rim watches from the benches.
    p("stv_troll_war_drum", 22, 34, 4, where=SP, solid="core")
    p("stv_arena_benches", 18, 40, 5, where=SP, solid="core")
    # The Hot Grate, seven o'clock: the stoker's fire, and the vents he opens by hand.
    p("rf_brazier", 30, 86, 5, solid="core")
    p("rf_steam_vent", 43, 86, 4)
    p("stv_arena_benches", 36, 93, 5, where=SP, solid="core")
    # The Pairing, five o'clock: the cage the pair are kept in, and the handlers' fire.
    p("stv_troll_cage", 74, 87, 6, where=SP, solid="core")
    p("stv_troll_cookfire", 61, 87, 4, where=SP)
    p("stv_arena_benches", 68, 93, 5, where=SP, solid="core")
    # The Hard Round, three o'clock: the dead end.  Spare weapons on the rack and nowhere left to go.
    p("stv_arena_weapon_rack", 89, 51, 5, where=SP, solid="core")
    p("stv_troll_skull_pile", 88, 62, 3, where=SP)
    p("stv_arena_benches", 92, 60, 5, where=SP, solid="core")
    # The House Floor: eight columns round the hall, the idol the house bets under, and its braziers.
    #: The 2x2 block is the collision; the sprite stands on the open tile just south of it, which is
    #: where a bottom-centre anchor has to go for the column to read as standing on its own base.
    for d in COLUMN_DEG:
        cx, cy = pol(COLUMN_R, d)
        b.pillar(round(cx), round(cy), 2)
        p("stv_troll_column", round(cx), round(cy) + 2, 7, where=SP)
    p("stv_troll_idol_head", 52, 46, 7, where=SP, solid="core", avoid=3)
    p("stv_troll_brazier", 43, 62, 5, where=SP, solid="core")
    p("stv_troll_brazier", 61, 62, 5, where=SP, solid="core")

    L.finish([ARRIVAL, PORTAL] + [(x, y) for (x, y, _n, _d) in BOSSES] + [ADD[:2]] + CHESTS)
    return zone, L


def generate_gurbashi_arena():
    zone, _ = build_arena()
    if os.path.exists(f"{BAKED.format(SLUG)}/ground_0_0.jpg"):
        register_baked(zone, BAKED.format(SLUG))
    return zone
