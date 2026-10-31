"""
Hand-built The Lashings (136x120): the Southsea cove on the Tanaris coast. Levels 44-48, five
bosses.

Kyle asked for "a new Southsea cove in Tanaris" - their proper home, as against the Drownbell,
which is a small sea cave under a headland with a different crew in it.

ARCHETYPE: THE LASHED FLEET, and it is the exact inverse of the Mother Vein.

The Southsea stopped sailing. Nine hulls came into this cove over about twenty years and none of
them left, and rather than beach them the crews lashed them together where they floated - plank to
plank, cable to cable - until the fleet stopped being ships and became a town that happens to be
made of ships. The water between the hulls is the wall. The planks are the only doors.

So the shape of this map is A TREE:

  - every ROOM is a HULL, which means it is LONG. A room here has a bow and a stern and a
    centreline, and you fight down it rather than across it.
  - every connection is a SINGLE PLANK. There is no second way round, anywhere, because a fleet
    lashed together is assembled outward from whatever was moored first and nobody ever built a
    redundant gangway over open water for the pleasure of it.

That second property is the whole design and it is the opposite of the Glittervein dungeon, where
every gallery is doubled and the seam always rejoins. Here, cutting any plank strands everything
beyond it - which means every plank is a chokepoint, every boss stands on one, and nobody skips
anything. Kyle, on the Anchorage: "No fuckers are skipping bosses in this game!" A tree gives that
for free where a cove had to have the tide cut into it to get the same effect.

It also means BACKTRACKING IS THE EXPLORATION. Three hulls are dead ends with a chest at the far
side, and you only get there by walking out along a plank and back. That is a real cost, and it is
the correct one for a place whose whole premise is that you cannot go round.

DUNGEON, not cave: fixed spawns, hand-authored packs, on world/zone_classification.DUNGEONS.

tools/verify_lashings.py measures both claims - every hull's aspect ratio, and the tree property,
by rebuilding the map with each plank missing and requiring something to be stranded every time.

HARD CONTRACT (world/portal_manager.py): portal (68, 112) <-> Northern Tanaris (222, 26).
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401
from tools import ship_builder as sb

BAKED = "assets/tiles/lashings/baked"
SFP = "assets/tiles/shimmering_flats/props/"
SNP = "assets/tiles/southern_needles/props/"
W, H = 136, 120
PORTAL = (68, 112)

#: THE FLEET. (key, name, x0, x1, ycen, beam, bow). beam is the HALF-beam at the widest station,
#: so a hull of beam 6 is thirteen tiles across amidships and tapers to nothing at bow and stern.
#:
#: THE x RANGES OVERLAP GENEROUSLY ON PURPOSE. A plank lands at the middle of the overlap between
#: two hulls, so a short overlap puts it on a taper where the deck is two tiles wide - which is a
#: gangway nobody can stand on and a boss who cannot hold it.
#:
#: EVERY ONE OF THESE IS LONG, and the verifier measures it. A hull that comes out square is a
#: room, and a map of rooms connected by corridors is every other dungeon in the game.
HULLS = [
    ("h0", "The Grounded Hulk", 48,  88, 106, 6, "e"),   # you board here off the shingle
    ("h1", "The Careenage",     34,  74,  86, 6, "w"),
    ("h2", "The Cookpot",       56, 104,  66, 6, "e"),
    ("h3", "The Powder Hulk",   30,  76,  46, 5, "w"),
    ("h4", "The Prize Court",   52, 102,  28, 6, "e"),
    ("h5", "The Flagship",      38,  96,  10, 7, "w"),
    # --- dead ends. Each one is a plank out and a plank back, and a chest at the end of it.
    ("l1", "The Netting",       82, 110,  86, 4, "e"),
    ("l2", "The Cable Tier",     4,  26,  46, 4, "w"),
    ("l3", "The Spoil Deck",   108, 130,  28, 4, "e"),
]
HULL_BY_KEY = {h[0]: h for h in HULLS}

#: Planks carve as "path", like the hulls. "deck" is not a tile the game has - carving with it
#: produced eight planks that rendered and were not walkable, and the only symptom was that every
#: hull past the first was stranded, which looks exactly like a geometry bug and is not one.
#:
#: A boss is triggered within CaveSpawnManager.TRIGGER_RADIUS tiles, covering a band of
#: ship_builder.TRIGGER_BAND. Every plank is exactly that wide, so a boss standing at the end of
#: one cannot be walked past - which on the Anchorage took tidal cuts to achieve and here is just
#: what a gangplank is.
PLANK_W = sb.TRIGGER_BAND

#: THE PLANKS, as a list of (kind, hull a, hull b) - and there are exactly len(HULLS) - 1 of them,
#: because this is a tree.
#:
#: THE GEOMETRY IS DERIVED, NOT WRITTEN DOWN. The first version of this file carried hand-written
#: spans and every one of them missed: a hull tapers to nothing at bow and stern, so a plank
#: pinned to a column that looked reasonable on paper attached to a station two tiles tall or to
#: no hull at all, and the whole map past the first hull was stranded. plank_spans() reads the
#: station maps carve_hull returns and lands each plank amidships, where the hull is widest, which
#: is also where a crew would actually sling one.
PLANKS = [
    ("v", "h0", "h1"),      # up out of the grounded hulk
    ("v", "h1", "h2"),
    ("v", "h2", "h3"),
    ("v", "h3", "h4"),
    ("v", "h4", "h5"),
    ("h", "h1", "l1"),      # out to the netting and back
    ("h", "l2", "h3"),
    ("h", "h4", "l3"),
]


def _extent(key):
    (_k, _nm, x0, x1, ycen, beam, _bow) = HULL_BY_KEY[key]
    return x0, x1, ycen, beam


def plank_spans(stations):
    """[(kind, line, lo, hi)] - where each plank actually runs, off the built hulls.

    ONE IMPLEMENTATION, read by the map and by tools/verify_lashings.py, for the same reason
    seam_kit owns the Glittervein galleries: a verifier with its own copy of this arithmetic is a
    verifier that can pass while the map is broken.
    """
    out = []
    for (kind, a, bkey) in PLANKS:
        sa, sb_ = stations[a], stations[bkey]
        if kind == "v":
            # a is the LOWER hull (larger ycen). Cross at a column both hulls carry, as close to
            # amidships of the shorter overlap as possible.
            lo_x = max(min(sa), min(sb_))
            hi_x = min(max(sa), max(sb_))
            col = (lo_x + hi_x) // 2
            a_top = sa[col][0]
            b_bot = sb_[col][1]
            if a_top < b_bot:                      # a is actually the upper hull; swap
                a_top, b_bot = sb_[col][0], sa[col][1]
            out.append(("v", col, b_bot, a_top))
        else:
            # side by side: cross on the shared centreline, between the nearer ends
            _ax0, ax1, aycen, _ab = _extent(a)
            bx0, _bx1, bycen, _bb = _extent(bkey)
            row = (aycen + bycen) // 2
            left, right = (ax1, bx0) if ax1 < bx0 else (_bx1, _ax0)
            out.append(("h", row, min(left, right), max(left, right)))
    return out


BOSSES = {}
CHESTS = []
GROUPS = []
TRASH = []

SWAB, RIG = "Southsea Swabbie", "Southsea Rigger"
POWDER, NET = "Southsea Powdermonkey", "Southsea Netcaster"
RAT = "Hulk Rat"

#: Three to four groups between each boss (Kyle). Every centre is on a hull's centreline, so no
#: pack can land in the water that is this map's wall.
PACKS = [
    # --- the grounded hulk, before Bosun Grell Tarpot (4)
    (62, 106, [(SWAB, 44), (SWAB, 44), (RAT, 44)]),
    (74, 106, [(SWAB, 44), (RIG, 44), (SWAB, 44)]),
    (54, 104, [(RAT, 44), (RAT, 44), (SWAB, 45)]),
    (82, 108, [(RIG, 45), (SWAB, 44), (RAT, 44)]),
    # --- the careenage and the netting, before Sailmaker Oona Flay (4)
    (46,  86, [(RIG, 45), (SWAB, 45), (NET, 45)]),
    (60,  88, [(NET, 45), (RIG, 45), (SWAB, 45)]),
    (92,  86, [(NET, 45), (NET, 45), (RIG, 45)]),
    (104, 86, [(NET, 46), (RIG, 45), (SWAB, 45)]),
    # --- the cookpot, before Powder-Master Juss Wick (3)
    (70,  66, [(SWAB, 46), (RAT, 45), (RIG, 46)]),
    (84,  66, [(RIG, 46), (NET, 46), (SWAB, 46)]),
    (96,  68, [(RAT, 46), (RIG, 46), (POWDER, 46)]),
    # --- the powder hulk and the cable tier, before Quartermaster Nadd Kell (4)
    (42,  46, [(POWDER, 46), (POWDER, 46), (RIG, 46)]),
    (58,  46, [(POWDER, 47), (SWAB, 46), (NET, 46)]),
    (14,  46, [(RAT, 46), (POWDER, 46), (RIG, 46)]),
    (22,  46, [(NET, 47), (POWDER, 47)]),
    # --- the prize court and the spoil deck, before Captain Ardessa Rake (4)
    (72,  28, [(RIG, 47), (NET, 47), (POWDER, 47)]),
    (88,  28, [(NET, 47), (RIG, 47), (SWAB, 47)]),
    (118, 28, [(POWDER, 47), (RIG, 47), (NET, 48)]),
    (82,  24, [(RIG, 48), (POWDER, 48)]),
]


def _sea(zone):
    for y in range(H):
        for x in range(W):
            zone.collision_layer[y][x] = "tropical_water"
            zone.set_tile(x, y, "tropical_water", "base")


def _near_walkable(zone, x, y, rad=8):
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            if zone.is_walkable(int(x) + dx, int(y) + dy):
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, int(x) + dx, int(y) + dy)
    return None if best is None else (best[1], best[2])


def build_lashings(omit=()):
    zone = Tilemap("The Lashings", W, H,
                   "Nine hulls that came into this cove over twenty years and never left, lashed "
                   "together until the fleet stopped being ships and became a town.")
    zone.is_cave = True
    zone.region = "Northern Tanaris"
    zone.fixed_spawns = True
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b
    b.wall_id = "tropical_water"
    b.floor_id = "path"
    _sea(zone)

    stations = {}
    for (key, _nm, x0, x1, ycen, beam, bow) in HULLS:
        stations[key] = sb.carve_hull(b, x0, x1, ycen, beam, bow=bow, base="path")

    # `omit` is how tools/verify_lashings.py strands a hull: it rebuilds this map without carving
    # that plank, so the test measures THIS map rather than a reconstruction of which tiles the
    # plank probably occupies. That reconstruction was the bug in the Mother Vein's first verifier.
    for i, (kind, line, lo, hi) in enumerate(plank_spans(stations)):
        if i in omit:
            continue
        if kind == "v":
            sb.gangplank(b, line, lo, hi, base="path", width=PLANK_W)
        else:
            sb.gangplank_x(b, line, lo, hi, base="path", width=PLANK_W)

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.set_tile(px, py, "path", "base")
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    # EVERY BOSS STANDS AT THE INBOARD END OF THE PLANK IT HOLDS. The plank is three tiles wide,
    # which is exactly a boss's trigger band, so there is no way past - and unlike the Anchorage,
    # which needed tidal cuts carved into a beach to produce a chokepoint, that is simply what a
    # gangplank between two hulls IS.
    # EVERY BOSS STANDS AT THE INBOARD END OF THE PLANK SHE HOLDS, and that position is DERIVED
    # from the plank, not written down beside it. Hand-written boss coordinates went stale the
    # moment the planks were derived from the hulls instead, and the symptom was not a crash - it
    # was four bosses standing a few tiles off the gangway they were meant to be holding, which
    # looks completely fine and means every one of them can be walked past.
    #
    # The plank is three tiles wide, which is exactly a boss's trigger band, so standing at its
    # mouth there is no way round. The Anchorage needed tidal cuts carved into a beach to get the
    # same guarantee; here it is what a gangplank already is. Kyle: "No fuckers are skipping
    # bosses in this game!"
    spans = plank_spans(stations)
    names = ["Bosun Grell Tarpot", "Sailmaker Oona Flay", "Powder-Master Juss Wick",
             "Quartermaster Nadd Kell", "Captain Ardessa Rake"]
    bosses = []
    for i, nm in enumerate(names):
        kind, line, lo, hi = spans[i]
        # ON the plank, at its deeper end - not one tile inside the hull. Hulls taper to nothing
        # at bow and stern, and a plank lands where two hulls OVERLAP, which for a short overlap
        # is near a taper: the tile just inboard was unwalkable, _near_walkable quietly moved the
        # boss somewhere roomier, and she stopped holding the gangway at all. The plank itself is
        # always walkable and always exactly a trigger band wide.
        bosses.append((line, lo, nm) if kind == "v" else (lo, line, nm))
    fixed = []
    for (x, y, n) in bosses:
        p = _near_walkable(zone, x, y)
        assert p, (n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    zone.boss_position = (fixed[0][0], fixed[0][1])
    zone.boss_positions = list(fixed)

    if omit:
        zone.trash_packs, zone.trash_spawns = [], []
        return zone, L

    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})

    # THE CHESTS ARE WHY THE DEAD ENDS EXIST. A leaf hull with nothing at the end of it is a long
    # walk the player does once and resents - the same note the Anchorage's west horn got.
    chests = []
    for (x, y) in ((96, 86), (12, 46), (122, 28), (56, 10), (80, 106)):
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        chests.append(p)
    CHESTS[:] = chests
    for c in chests:
        L.mark("chest", *c)

    TRASH.clear()
    GROUPS.clear()
    occupied = [(x, y) for (x, y) in BOSSES.values()] + [tuple(c) for c in CHESTS] + [PORTAL]
    for (cx, cy, members) in PACKS:
        group = []
        k = len(members)
        for i, (nm, lvl) in enumerate(members):
            ang = 0.4 + 2 * math.pi * i / k
            spot = _near_walkable(zone, cx + 2.4 * math.cos(ang), cy + 1.8 * math.sin(ang), rad=6)
            assert spot, (nm, cx, cy)
            if any(max(abs(spot[0] - o[0]), abs(spot[1] - o[1])) < 2 for o in occupied):
                alt = _near_walkable(zone, cx + 3.4 * math.cos(ang), cy + 2.6 * math.sin(ang), rad=6)
                if alt and all(max(abs(alt[0] - o[0]), abs(alt[1] - o[1])) >= 2 for o in occupied):
                    spot = alt
            occupied.append(spot)
            group.append((spot[0], spot[1], nm, lvl))
            TRASH.append((spot[0], spot[1], nm, lvl))
        GROUPS.append(group)
    zone.trash_packs = [list(g) for g in GROUPS]
    zone.trash_spawns = list(TRASH)

    zone.add_subzone("The Lashings", 0, 0, W, H)
    for (key, nm, x0, x1, ycen, beam, _bow) in HULLS:
        zone.add_subzone(nm, x0, ycen - beam - 1, (x1 - x0) + 1, 2 * beam + 3)
    return zone, L


def finish(zone, L):
    targets = [PORTAL] + [(x, y) for (x, y) in BOSSES.values()] + list(CHESTS) \
        + [(x, y) for (x, y, _n, _l) in TRASH]
    return L.finish(targets)


def dress(zone, L):
    P = L.prop
    S = dict(where=SFP)
    N = dict(where=SNP)
    # ---- the grounded hulk: the one that is actually aground, and the reason there is a door
    P("sw_bollard", 54, 104, 3, **S)
    P("sw_bollard", 82, 104, 3, **S)
    P("sw_nets", 62, 108, 4, **S)
    P("sw_fish_crates", 76, 108, 3, **S)
    # ---- the careenage: a hull laid over to have its bottom scraped, and nobody ever righted it
    P("sw_cargo_winch", 44, 86, 5, **S)
    P("sn_pulley_hoist", 58, 84, 5, **N)
    P("sw_harbour_lamp", 50, 90, 5, **S)
    # ---- the netting
    P("sw_nets", 90, 86, 4, **S)
    P("sw_nets", 102, 86, 4, **S)
    P("sn_rope_coil", 96, 88, 3, **N)
    # ---- the cookpot: they live in this one
    P("sn_cook_fire", 72, 66, 3, **N)
    P("sn_drying_rack", 84, 64, 4, **N)
    P("sw_fish_crates", 92, 68, 3, **S)
    P("sn_hide_tent", 62, 68, 4, **N)
    # ---- the powder hulk and the cable tier
    P("sf_fuel_drums", 40, 46, 3, **S)
    P("sf_fuel_drums", 56, 46, 3, **S)
    P("sn_rope_coil", 16, 46, 3, **N)
    P("sn_rope_coil", 22, 48, 3, **N)
    P("sw_cargo_winch", 34, 44, 5, **S)
    # ---- the prize court and the spoil deck: everything they have taken, sorted
    P("sf_crate_stack", 70, 28, 4, **S)
    P("sf_crate_stack", 90, 28, 4, **S)
    P("sn_clay_vessel", 80, 30, 3, **N)
    P("sf_crate_stack", 116, 28, 4, **S)
    P("sw_dock_crane", 100, 26, 7, **S)
    # ---- the flagship
    P("sw_harbour_lamp", 52, 10, 5, **S)
    P("sw_harbour_lamp", 88, 10, 5, **S)
    P("sn_hide_banner", 60, 8, 5, **N)
    P("sn_hide_banner", 80, 8, 5, **N)
    P("sw_cargo_winch", 70, 6, 5, **S)
    return zone, L


def generate_lashings():
    zone, L = build_lashings()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_lashings_baked():
    """(zone, layout) with props + QA done - what the baker paints from."""
    zone, L = build_lashings()
    dress(zone, L)
    finish(zone, L)
    return zone, L
