"""The Bloodsail galleon: four zones, levels 47-52. The end of the Return Voyage.

THE GALLEON IS A SIEGE FROM THE BEACH, and it is built that way to avoid being the raider again.

    The Bloodsail Anchorage      47-48, 2 bosses.  A cove. Not a ship at all.
    The Galleon's Weather Deck   49,    1 boss.    Boarded amidships, runs FORWARD.
    The Galleon's Hold           50,    2 bosses.  Forward to aft, six compartments.
    The Captain's Cabin          52,    2 at once. One room, one fight, no trash.

The raider is a lap - board aft, fight forward, drop down, run back aft. Doing that twice would
make the second ship the first ship with more health. So this one does not start on a ship: you
come ashore on the sand bar, and the galleon is in front of you the whole way down the cove, which
is a different kind of approach to a boss than a corridor. Then one direction per deck, and never
the direction you went last - forward along the weather deck, forward again below (which feels
wrong, and is the point: you are going deeper, not back), then aft into the cabin.

THE ISLAND EXPANDS. Kyle: "It's a small island it docks on... It expands when you enter it." From
our rail in The Crossing it is a sand bar with a galleon tied to it. Through the portal it is a
cove with a beach, a headland and two bosses on it. The player cannot see that coming, which is
worth more than the extra tiles cost.

THE DOUBLE BOSS IS ONE ENCOUNTER. Kyle: "a double boss fight of BOTH bloodsail leaders at once
(they can drop 3 pieces of loot at once from a pool of 10)." zone.boss_pack folds Dace into Crane's
SpawnPoint rather than giving him a chamber he does not have - he is standing in her cabin. Two
boss_positions entries would be two fights and two loot rolls.

HARD ON PURPOSE. Asked whether to soften it, since two bosses at once is about 5x a normal boss's
health, Kyle: "No, boss fight should be hard." Both carry the full 2.5x multiplier. For whoever
tunes it next: health makes a fight LONG. What makes this one HARD is that Crane is frost and Dace
is physical, so no single resistance or armour answer covers both, and both carry an AoE on a
5-turn cooldown, so the party is under spread damage while the tank can only face one of them. If
it plays as a slog rather than a scare, cut the health and leave those two facts alone.

THE CABIN HAS NO TRASH, AND THAT TAKES WORK. A fixed-spawn zone with no trash_packs entry falls
past CaveSpawnManager.populate's packs and authored-list branches and SCATTERS SINGLES off its
encounter table. Three weighted entries that looked like harmless flavour once put fifteen one-mob
fights in front of this double boss. An empty zone.trash_spawns does NOT help, because an empty
list is falsy and the roll is the elif after it. The table has to hold nothing but the two leaders
at weight 0.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout  # noqa: F401
import tools.ship_builder as sb

CP = "assets/tiles/coastal_props/"
SP = "assets/tiles/ship_props/"

# ---------------------------------------------------------------- the cove
AW, AH = 110, 124
A_IN = (54, 112)          # ashore at the landing, from The Crossing's sand bar
A_OUT = (48, 30)         # on the ramp, out over the water. She is afloat beyond it.

#: THE SHAPE KYLE PICKED. I had replaced this with a C of beach around a carved bay, on the
#: argument that a cove is the sea reaching into the land. He looked at both and chose this one:
#: "is the better option bro." So it is lobes of sand with water lying in them, and the route is
#: the weave BETWEEN the pools.
#:
#: THAT ONLY WORKS IF THE POOLS ARE NOT CROSSABLE - Kyle again: "that route will only work if the
#: light blue water is not crossable so we dont skip bosses." A walkable pool turns every weave
#: into a straight line and both bosses into optional scenery. So the shallows are PAINTED on
#: tiles whose collision stays water: the base layer is only what you see, and Tilemap.is_walkable
#: reads collision first. Turquoise you cannot wade.
COVE_LAND = [
    (54, 106, 20, 10),    # the landing, where you come ashore
    (42, 90, 16, 12),     # the west shore
    (62, 78, 16, 12),     # the east shore
    (44, 64, 16, 12),     # the middle
    (62, 50, 16, 11),     # the east headland
    (48, 40, 16, 10),     # the head, under her side
]
#: The pools the route weaves between. Blocking, per above.
#:
#: EACH LOBE OVERLAPS THE NEXT, which was not true of the first version and only did not matter
#: because the pools were WALKABLE there - they were quietly acting as bridges between lobes that
#: never touched. Making them block, which is the thing Kyle asked for, took the island apart:
#: the entire east shore came back stranded. So the sand is a connected chain FIRST and the pools
#: are dropped into the middle of it second, each pinching a wide stretch into a way round rather
#: than cutting a link. Checked by flood fill: 2755 walkable, 2755 reachable, 0 stranded.
COVE_POOLS = [(56, 94, 7, 5), (54, 78, 7, 5), (52, 58, 7, 5), (60, 44, 6, 4)]

#: (y0, y1, gap_lo, gap_hi) - bands the tide closes except for one gap, so the route has a neck
#: a boss can hold. The first sits between pools 1 and 2 and opens to the west; the second between
#: pools 3 and 4 and opens to the east, so the walk crosses the cove rather than running up one
#: side of it.
NECKS = [(85, 87, 34, 40), (50, 52, 68, 74)]

# -------------------------------------------------------------- the galleon
GW, GH = 130, 80
#: 107 long on a 37 beam, about 2.9:1 - bigger than the raider in every dimension, which is what
#: makes her read as the flagship rather than as the same ship twice.
GHULL = dict(x0=12, x1=118, ycen=40, beam=18, bow="w")
GHOLD = dict(x0=14, x1=116, ycen=40, beam=15, bow="w")

D_IN = (52, 56)          # boarded amidships, over her starboard rail from the ramp
D_HATCH = (24, 40)       # the forward hatch, down
H_IN = (24, 40)
H_OUT = (110, 40)        # the cabin door, aft

# --------------------------------------------------------------- the cabin
CW, CH = 60, 48
C_IN = (30, 42)
C_OUT = (30, 12)         # the stern gallery, straight back to our own deck

#: THE ROSTER. Declared here; the creature data is written from this list.
TRASH_LOW = ["Bloodsail Marine", "Bloodsail Gunner", "Bloodsail Deckmaster"]
TRASH_HIGH = ["Bloodsail Reaver", "Bloodsail Stormcaller", "Bloodsail Deckmaster"]
ANCHORAGE_CHESTS = []
ANCHORAGE_BOSSES = ["Shorebreaker Teska Vohl", "Quartermaster Ilsa Renn"]
DECK_BOSS = "Mastmaster Corbin Ake"
HOLD_BOSSES = ["Powdermaster Juno Felk", "Keelwarden Orso Brann"]
CABIN_LEAD = "Admiral Hedessa Crane"
CABIN_SECOND = "Fleet-Captain Orin Dace"

#: One encounter, two bosses. {lead: [(x, y, name), ...]} - world/cave_spawns folds the members
#: into the lead's SpawnPoint.
CABIN_PACK = {CABIN_LEAD: [(34, 22, CABIN_SECOND)]}

ANCHORAGE_PACKS = [
    (52, 104, 47, ["Bloodsail Marine", "Bloodsail Marine", "Bloodsail Gunner"]),
    (44, 98, 47, ["Bloodsail Gunner", "Bloodsail Marine", "Bloodsail Deckmaster"]),
    (36, 96, 47, ["Bloodsail Marine", "Bloodsail Marine", "Bloodsail Gunner"]),
    # ---- past Vohl, round the second and third pools toward the head.
    (70, 64, 48, ["Bloodsail Deckmaster", "Bloodsail Gunner", "Bloodsail Marine"]),
    (64, 60, 48, ["Bloodsail Marine", "Bloodsail Deckmaster", "Bloodsail Gunner"]),
    (66, 56, 48, ["Bloodsail Gunner", "Bloodsail Marine", "Bloodsail Marine"]),
]
ANCHORAGE_BOSS_AT = {"Shorebreaker Teska Vohl": (37, 82), "Quartermaster Ilsa Renn": (71, 46)}

GDECK_PACKS = [
    (46, 32, 49, ["Bloodsail Reaver", "Bloodsail Deckmaster", "Bloodsail Stormcaller"]),
    (56, 47, 49, ["Bloodsail Deckmaster", "Bloodsail Reaver", "Bloodsail Reaver"]),
    (44, 48, 49, ["Bloodsail Stormcaller", "Bloodsail Reaver", "Bloodsail Deckmaster"]),
    (34, 31, 49, ["Bloodsail Reaver", "Bloodsail Reaver", "Bloodsail Stormcaller"]),
]
#: AFT OF THE BOARDING POINT IS BEHIND THE PLAYER. The first barricade here was at station 76,
#: which is a fine chokepoint and entirely useless: you board amidships at x=52 and run FORWARD to
#: the hatch at x=24, so 76 is over your shoulder the whole time and Ake came back skippable while
#: every other boss in the dungeon had been fixed. A neck only counts if it is between the way in
#: and the way out.
GDECK_BOSS_AT = {DECK_BOSS: (34, 40)}
#: (station x, gap y_lo, y_hi) - the barricade Ake holds. An open deck gives a boss nothing.
GDECK_BARRICADES = [(44, 38, 42)]

GHOLD_PACKS = [
    (32, 35, 50, ["Bloodsail Reaver", "Bloodsail Deckmaster", "Bloodsail Reaver"]),
    (40, 45, 50, ["Bloodsail Stormcaller", "Bloodsail Reaver", "Bloodsail Deckmaster"]),
    (50, 35, 50, ["Bloodsail Reaver", "Bloodsail Reaver", "Bloodsail Stormcaller"]),
    # ---- past Felk
    (88, 45, 51, ["Bloodsail Deckmaster", "Bloodsail Reaver", "Bloodsail Stormcaller"]),
    (94, 35, 51, ["Bloodsail Reaver", "Bloodsail Stormcaller", "Bloodsail Reaver"]),
    (100, 45, 51, ["Bloodsail Deckmaster", "Bloodsail Reaver", "Bloodsail Reaver"]),
]
#: In their compartments - see the note in handbuilt_bloodsail_raider on why they came back out
#: of the doorways.
GHOLD_BOSS_AT = {"Powdermaster Juno Felk": (66, 40), "Keelwarden Orso Brann": (96, 40)}

#: Six compartments, which is what makes the hold a dungeon rather than a long room.
GBULKHEADS = [
    (28, 32, 36),
    (44, 44, 48),
    (58, 32, 36),
    (74, 44, 48),
    (90, 32, 36),
    (102, 44, 48),   # the cabin lobby door
]


def _sea(zone, w, h):
    for y in range(h):
        for x in range(w):
            zone.collision_layer[y][x] = "tropical_water"
            zone.set_tile(x, y, "tropical_water", "base")


# ============================================================== THE ANCHORAGE
def build_anchorage():
    zone = Tilemap("The Bloodsail Anchorage", AW, AH,
                   "A cove on the lee side of the island, deep enough to lie a galleon in. The "
                   "beach is a working one and everything on it belongs to her.")
    zone.is_cave = False
    zone.region = "The Crossing"
    zone.fixed_spawns = True
    L = CaveLayout(zone, A_IN)
    b = L.b
    b.wall_id = "tropical_water"
    b.floor_id = "sand"
    _sea(zone, AW, AH)

    b.lobes(COVE_LAND, base="sand")

    # THE POOLS BLOCK. Painted, not carved - see the COVE_POOLS note above. b.lobes would open
    # them, which is the one thing they must not be.
    for (cx, cy, rx, ry) in COVE_POOLS:
        for dy in range(-ry, ry + 1):
            for dx in range(-rx, rx + 1):
                if (dx / max(rx, 1)) ** 2 + (dy / max(ry, 1)) ** 2 <= 1.0:
                    x, y = cx + dx, cy + dy
                    if 0 <= x < AW and 0 <= y < AH:
                        zone.collision_layer[y][x] = "tropical_water"
                        zone.set_tile(x, y, "tropical_shallow", "base")

    # THE RAMP UP HER SIDE, out over the water from the head of the beach. She lies afloat beyond
    # it; the portal is on the ramp, not on the sand, so boarding her is a thing you walk up.
    sb.gangplank(b, 48, 36, 24, base="path", width=3)

    # TWO NECKS, AND A BOSS STANDING IN EACH. Kyle: "No fuckers are skipping bosses in this
    # game!" A scan of the map as first built found zero tiles anywhere that a boss could not be
    # walked round - every passage was wider than the three-tile band a boss covers. So the
    # geometry has to provide the chokepoint: the tide closes the beach at two bands and leaves
    # one gap in each, which is where Vohl and Renn stand. Verified, not assumed - see
    # tools/verify_return_voyage.py, which seals the trigger radius round each boss and checks the
    # exit goes unreachable.
    for (y0, y1, lo, hi) in NECKS:
        closed = sb.tidal_cut(b, y0, y1, lo, hi)
        if closed < 10:
            raise AssertionError(f"{zone.name}: neck at y{y0}-{y1} closed only {closed} tiles - "
                                 f"that band was already water, so it is not a neck")

    # Headland rock, for the look of the shore rather than for the route.
    b.pillar(76, 82, size=4)
    b.pillar(28, 96, size=4)
    b.pillar(32, 66, size=3)
    b.pillar(72, 40, size=3)

    for (px, py) in (A_IN, A_OUT):
        zone.collision_layer[py][px] = None
        L.mark("portal", px, py)

    zone.boss_positions = [(x, y, n) for n, (x, y) in ANCHORAGE_BOSS_AT.items()]
    zone.boss_position = zone.boss_positions[0][:2]
    for (x, y, n) in zone.boss_positions:
        L.mark("boss_marker", x, y)
    zone.trash_packs = sb.place_packs(zone, ANCHORAGE_PACKS)
    zone.trash_spawns = [m for pack in zone.trash_packs for m in pack]

    # THE WEST HORN IS A LONG WALK TO NOTHING otherwise. The cove is a U and the route up the east
    # side is the dungeon; the west side is scenery you can walk the whole length of, which is the
    # kind of thing a player explores once and resents. A chest at the far end of it is the
    # cheapest honest reason for it to be there.
    ANCHORAGE_CHESTS[:] = [(34, 96), (40, 38)]
    for (cx, cy) in ANCHORAGE_CHESTS:
        L.mark("chest", cx, cy)

    zone.add_subzone("The Bloodsail Anchorage", 0, 0, AW, AH)
    zone.add_subzone("The Landing", 32, 96, 46, 26)
    zone.add_subzone("The Cove", 24, 60, 60, 36)
    zone.add_subzone("The Head of the Cove", 30, 28, 50, 32)
    return zone, L


def dress_anchorage(zone, L):
    """Mooring gear at the water's edge, and the island everywhere else.

    NO SHIPS' GEAR UP THE BEACH. Kyle: "No ships gear on the beach." An earlier pass had cargo
    nets, powder, sail bundles and rope strewn across the sand, which is what CAREENING looks like -
    a ship hauled out for hull work with her whole inventory dumped on the shore. She is moored.
    What a moored ship puts on a beach is lines, a lamp, and the people watching them.
    """
    P = L.prop
    S = dict(where=SP)
    C = dict(where=CP)

    # SHE IS AFLOAT, not beached - her anchor tile is open water beyond the ramp head.
    sb.afloat(L, CP + "bloodsail_galleon.png", 48, 22, 20)
    # mooring gear at the ramp head, and NO LAMPS ON THE BEACH (Kyle: "dont put lamps on the
    # beach") - a working anchorage lights its ship, not its sand.
    P("mooring_posts", 42, 36, 3, near_ok=True, **C)
    P("bs_rope_coil", 54, 37, 2, near_ok=True, **S)
    # ... and the island itself.
    P("mangrove_thicket", 42, 108, 5, **C)
    P("banana_plant", 64, 106, 4, **C)
    P("jungle_banyan", 34, 88, 8, **C)
    P("sea_stack_spire", 72, 80, 8, **C)
    P("mossy_jungle_boulder", 40, 84, 4, **C)
    P("coral_reef_outcrop", 38, 68, 3, near_ok=True, **C)
    P("hibiscus_bush", 68, 67, 3, near_ok=True, **C)
    P("bamboo_grove", 64, 56, 6, **C)
    P("driftwood_pile", 62, 102, 3, near_ok=True, **C)
    P("tiki_totem", 36, 74, 5, **C)
    P("crab_claw_arch", 38, 56, 5, **C)
    P("sea_stack_spire", 30, 94, 8, **C)
    P("buried_treasure_chest", 34, 64, 3, near_ok=True, **C)
    return zone, L


def finish_anchorage(zone, L):
    return L.finish([A_IN, A_OUT] + [(x, y) for (x, y, _n) in zone.boss_positions]
                    + list(ANCHORAGE_CHESTS)
                    + [(s[0], s[1]) for s in zone.trash_spawns])


def generate_anchorage():
    zone, L = build_anchorage()
    dress_anchorage(zone, L)
    finish_anchorage(zone, L)
    return zone


# ============================================================ THE WEATHER DECK
def _galleon_zone(name, desc, start, hull, floor):
    zone = Tilemap(name, GW, GH, desc)
    zone.is_cave = True
    zone.region = "The Crossing"
    zone.fixed_spawns = True
    L = CaveLayout(zone, start)
    b = L.b
    b.wall_id = "tropical_water"
    b.floor_id = floor
    _sea(zone, GW, GH)
    stations = sb.carve_hull(b, base=floor, **hull)
    return zone, L, stations


def build_galleon_deck():
    zone, L, stations = _galleon_zone(
        "The Galleon's Weather Deck",
        "Four hundred tons of her, and the boarding ramp comes up amidships where the rail is "
        "lowest. Everything worth defending is forward.",
        D_IN, GHULL, "path")
    b = L.b

    sb.platform(b, 16, 32, 36, 48, base="sand")      # forecastle
    sb.platform(b, 96, 30, 116, 50, base="sand")     # quarterdeck, over the cabin
    sb.platform(b, 58, 35, 68, 45, base="stone")     # the main hatch
    sb.platform(b, 20, 36, 30, 44, base="stone")     # the forward hatch, where you go down
    sb.bulwark(b, base="dirt")

    # Deck houses and gun tackle, staggered so the run forward weaves.
    b.pillar(84, 30, size=4)
    b.pillar(70, 50, size=4)
    b.pillar(64, 28, size=3)
    b.pillar(48, 50, size=3)
    b.pillar(42, 28, size=3)

    for (station, lo, hi) in GDECK_BARRICADES:
        closed = sb.choke(b, "x", station, lo, hi, base="dirt")
        if closed < 8:
            raise AssertionError(f"{zone.name}: barricade at x={station} closed only {closed}")

    for (px, py) in (D_IN, D_HATCH):
        zone.collision_layer[py][px] = None
        L.mark("portal", px, py)

    zone.boss_positions = [(x, y, n) for n, (x, y) in GDECK_BOSS_AT.items()]
    zone.boss_position = zone.boss_positions[0][:2]
    for (x, y, n) in zone.boss_positions:
        L.mark("boss_marker", x, y)
    zone.trash_packs = sb.place_packs(zone, GDECK_PACKS)
    zone.trash_spawns = [m for pack in zone.trash_packs for m in pack]

    zone.add_subzone("The Galleon's Weather Deck", 0, 0, GW, GH)
    zone.add_subzone("The Boarding", 40, 44, 28, 24)
    zone.add_subzone("The Waist", 36, 24, 48, 32)
    zone.add_subzone("The Forecastle", 12, 28, 28, 24)
    return zone, L, stations


def dress_galleon_deck(zone, L):
    P = L.prop
    S = dict(where=SP)
    P("bs_bloodsail_flag", 108, 36, 7, **S)
    P("bs_ships_bell", 100, 46, 4, **S)
    P("bs_cannon_deck", 88, 36, 3, **S)
    P("bs_cannon_deck", 78, 46, 3, **S)
    P("bs_powder_barrels", 82, 34, 3, **S)
    P("bs_cargo_net", 70, 34, 3, **S)
    P("bs_crate_stack", 54, 50, 4, **S)
    P("bs_sail_bundle", 50, 32, 3, **S)
    P("bs_cannon_deck", 50, 46, 3, **S)
    P("bs_weapon_rack", 32, 34, 4, **S)
    P("bs_barrel_cluster", 28, 47, 3, **S)
    P("bs_lamp_post", 18, 42, 5, **S)
    return zone, L


def finish_galleon_deck(zone, L):
    return L.finish([D_IN, D_HATCH] + [(x, y) for (x, y, _n) in zone.boss_positions]
                    + [(s[0], s[1]) for s in zone.trash_spawns])


def generate_galleon_deck():
    zone, L, _s = build_galleon_deck()
    dress_galleon_deck(zone, L)
    finish_galleon_deck(zone, L)
    return zone


# ================================================================ THE HOLD
def build_galleon_hold():
    zone, L, stations = _galleon_zone(
        "The Galleon's Hold",
        "Six compartments between the forward hatch and the cabin door, and every one of them is "
        "somebody's job.",
        H_IN, GHOLD, "dirt")
    b = L.b

    sb.platform(b, 104, 32, 114, 48, base="path")    # the lobby outside the cabin

    cuts = [(x, sb.bulkhead(b, stations, x, lo, hi)) for (x, lo, hi) in GBULKHEADS]
    bad = [(x, n) for (x, n) in cuts if n < 4]
    if bad:
        raise AssertionError(f"{zone.name}: bulkheads that barely cut anything: {bad}")

    for (px, py) in (H_IN, H_OUT):
        zone.collision_layer[py][px] = None
        L.mark("portal", px, py)

    zone.boss_positions = [(x, y, n) for n, (x, y) in GHOLD_BOSS_AT.items()]
    zone.boss_position = zone.boss_positions[0][:2]
    for (x, y, n) in zone.boss_positions:
        L.mark("boss_marker", x, y)
    zone.trash_packs = sb.place_packs(zone, GHOLD_PACKS)
    zone.trash_spawns = [m for pack in zone.trash_packs for m in pack]

    zone.add_subzone("The Galleon's Hold", 0, 0, GW, GH)
    zone.add_subzone("The Cable Tier", 14, 28, 30, 26)
    zone.add_subzone("The Magazine", 44, 28, 30, 26)
    zone.add_subzone("The Orlop", 74, 28, 28, 26)
    zone.add_subzone("The Cabin Lobby", 102, 30, 24, 22)
    return zone, L, stations


def dress_galleon_hold(zone, L):
    P = L.prop
    S = dict(where=SP)
    P("bs_hanging_lantern", 22, 36, 3, **S)
    P("bs_hammock", 34, 46, 3, **S)
    P("bs_rope_coil", 38, 36, 2, near_ok=True, **S)
    P("bs_powder_barrels", 48, 36, 3, **S)
    P("bs_gunport_cannon", 54, 46, 4, **S)
    P("bs_bilge_pump", 68, 36, 4, **S)
    P("bs_crate_stack", 78, 46, 4, **S)
    P("bs_cargo_net", 86, 36, 3, **S)
    P("bs_manacles", 94, 46, 2, near_ok=True, **S)
    P("bs_sea_chest", 98, 36, 2, near_ok=True, **S)
    P("bs_loot_crate", 108, 36, 3, **S)
    P("bs_lamp_post", 112, 46, 5, **S)
    return zone, L


def finish_galleon_hold(zone, L):
    return L.finish([H_IN, H_OUT] + [(x, y) for (x, y, _n) in zone.boss_positions]
                    + [(s[0], s[1]) for s in zone.trash_spawns])


def generate_galleon_hold():
    zone, L, _s = build_galleon_hold()
    dress_galleon_hold(zone, L)
    finish_galleon_hold(zone, L)
    return zone


# ============================================================== THE CABIN
def build_cabin():
    zone = Tilemap("The Captain's Cabin", CW, CH,
                   "The great cabin, right aft, with the stern windows behind her. Both of them "
                   "are in here, and neither of them is going anywhere.")
    zone.is_cave = True
    zone.region = "The Crossing"
    zone.fixed_spawns = True
    L = CaveLayout(zone, C_IN)
    b = L.b
    b.wall_id = "tropical_water"
    b.floor_id = "path"
    _sea(zone, CW, CH)

    # ONE ROOM. The cabin is the stern of the ship, so it is wider aft than forward - the transom
    # is the widest part of a galleon and the great cabin runs the full width of it.
    b.rect(12, 10, 48, 44, chamfer=6, base="path")
    sb.platform(b, 16, 12, 44, 20, base="sand")      # the stern gallery, under the windows

    # THE BULKHEAD ACROSS THE CABIN, with the pair standing in its one doorway. A great cabin is
    # a single room and a single room lets you walk round anybody in it - the skippability scan
    # had both leaders optional, in the fight the whole dungeon is built around. This is the
    # screen bulkhead a ship of this size really has between the cabin and the stern gallery,
    # and the two of them are standing in the door of it.
    sb.choke(b, "y", 28, 27, 33, base="dirt")
    sb.bulwark(b, base="dirt")

    for (px, py) in (C_IN, C_OUT):
        zone.collision_layer[py][px] = None
        L.mark("portal", px, py)

    # The pair, as ONE SpawnPoint. boss_positions carries only the lead.
    zone.boss_positions = [(30, 22, CABIN_LEAD)]
    zone.boss_position = (30, 22)
    zone.boss_pack = CABIN_PACK
    L.mark("boss_marker", 30, 22)

    # NOT an empty list - see the module docstring. The zone simply has no trash attribute set to
    # anything falsy that populate() could fall past, and its encounter table holds only the two
    # leaders at weight 0 so the scatter branch has nothing to scatter.
    zone.trash_spawns = []
    zone.no_trash = True

    zone.add_subzone("The Captain's Cabin", 0, 0, CW, CH)
    return zone, L


def dress_cabin(zone, L):
    P = L.prop
    S = dict(where=SP)
    P("bs_captains_desk", 20, 30, 5, **S)
    P("bs_chart_table", 40, 30, 5, **S)
    P("bs_globe_stand", 44, 38, 4, **S)
    P("bs_bookshelf", 16, 22, 5, **S)
    P("bs_wine_rack", 44, 22, 5, **S)
    P("bs_armchair", 24, 38, 4, **S)
    P("bs_captains_bunk", 36, 42, 4, **S)
    P("bs_treasure_open", 18, 40, 3, **S)
    P("bs_sword_plaque", 30, 14, 3, near_ok=True, **S)
    P("bs_candelabra", 26, 20, 4, **S)
    P("bs_hanging_lantern", 38, 20, 3, **S)
    P("bs_bloodsail_flag", 14, 34, 6, **S)
    P("bs_mess_table", 34, 34, 4, **S)
    return zone, L


def finish_cabin(zone, L):
    members = [(m[0], m[1]) for v in CABIN_PACK.values() for m in v]
    return L.finish([C_IN, C_OUT, (30, 22)] + members)


def generate_cabin():
    zone, L = build_cabin()
    dress_cabin(zone, L)
    finish_cabin(zone, L)
    return zone
