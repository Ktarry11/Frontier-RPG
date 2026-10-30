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
AW, AH = 110, 96
A_IN = (66, 84)          # ashore on the east horn of the cove, from The Crossing's sand bar
A_OUT = (48, 18)         # up the boarding ramp at the head of the cove

#: THE COVE IS CUT OUT OF THE LAND, NOT ASSEMBLED FROM PONDS.
#:
#: The first version of this map was a chain of overlapping sand lobes with shallow pools dropped
#: on top, and it rendered as an island with puddles. That is the same mistake Kyle rejected on
#: Rocky Pass - "Looks like anal beads bro" - a route built by unioning circles reads as a string
#: of circles however the circles are placed.
#:
#: A cove is the sea reaching INTO the land. So: lay down one headland, then carve the bay back out
#: of it from the south, narrowing as it goes north. What is left is a C of beach that you walk
#: around, with water on one side of you the whole way and the galleon visible at the head of it
#: from the moment you land.
HEADLAND = [(52, 52, 33, 38), (74, 44, 16, 22), (30, 40, 14, 20)]
#: Carved back OUT as blocking water. Wide at the mouth, narrow at the head, which is both what a
#: drowned valley looks like and what makes the walk round it get tighter as you go.
BAY = [(50, 96, 19, 16), (50, 78, 15, 13), (52, 62, 12, 11), (54, 48, 9, 9), (54, 36, 6, 6)]
#: Waded shelf along the bay's edge - the shallows you can actually stand in.
COVE_SHALLOWS = [(66, 72, 7, 6), (34, 66, 6, 6), (68, 44, 5, 5)]

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
CABIN_PACK = {CABIN_LEAD: [(34, 24, CABIN_SECOND)]}

ANCHORAGE_PACKS = [
    (68, 80, 47, ["Bloodsail Marine", "Bloodsail Marine", "Bloodsail Gunner"]),
    (70, 74, 47, ["Bloodsail Gunner", "Bloodsail Marine", "Bloodsail Deckmaster"]),
    (74, 68, 47, ["Bloodsail Marine", "Bloodsail Marine", "Bloodsail Gunner"]),
    # ---- past Vohl at the neck. North of the midpoint between the two, or path distance gives
    # them all to her and Renn is approached across open sand.
    (76, 38, 48, ["Bloodsail Deckmaster", "Bloodsail Gunner", "Bloodsail Marine"]),
    (68, 32, 48, ["Bloodsail Marine", "Bloodsail Deckmaster", "Bloodsail Gunner"]),
    (64, 27, 48, ["Bloodsail Gunner", "Bloodsail Marine", "Bloodsail Marine"]),
]
ANCHORAGE_BOSS_AT = {"Shorebreaker Teska Vohl": (80, 58), "Quartermaster Ilsa Renn": (60, 24)}

GDECK_PACKS = [
    (46, 32, 49, ["Bloodsail Reaver", "Bloodsail Deckmaster", "Bloodsail Stormcaller"]),
    (56, 47, 49, ["Bloodsail Deckmaster", "Bloodsail Reaver", "Bloodsail Reaver"]),
    (38, 48, 49, ["Bloodsail Stormcaller", "Bloodsail Reaver", "Bloodsail Deckmaster"]),
    (34, 31, 49, ["Bloodsail Reaver", "Bloodsail Reaver", "Bloodsail Stormcaller"]),
]
GDECK_BOSS_AT = {DECK_BOSS: (76, 40)}

GHOLD_PACKS = [
    (32, 35, 50, ["Bloodsail Reaver", "Bloodsail Deckmaster", "Bloodsail Reaver"]),
    (40, 45, 50, ["Bloodsail Stormcaller", "Bloodsail Reaver", "Bloodsail Deckmaster"]),
    (50, 35, 50, ["Bloodsail Reaver", "Bloodsail Reaver", "Bloodsail Stormcaller"]),
    # ---- past Felk
    (84, 45, 51, ["Bloodsail Deckmaster", "Bloodsail Reaver", "Bloodsail Stormcaller"]),
    (94, 35, 51, ["Bloodsail Reaver", "Bloodsail Stormcaller", "Bloodsail Reaver"]),
    (100, 45, 51, ["Bloodsail Deckmaster", "Bloodsail Reaver", "Bloodsail Reaver"]),
]
GHOLD_BOSS_AT = {"Powdermaster Juno Felk": (62, 40), "Keelwarden Orso Brann": (106, 40)}

#: Six compartments, which is what makes the hold a dungeon rather than a long room.
GBULKHEADS = [
    (28, 32, 36),
    (44, 44, 48),
    (58, 32, 36),
    (74, 44, 48),
    (90, 32, 36),
    (102, 44, 48),
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

    b.lobes(HEADLAND, base="sand")
    # ... and now take the sea back. _open carves; this is the opposite, so it is written out
    # rather than borrowed - Builder has no "close" because no other zone has ever needed one.
    for (cx, cy, rx, ry) in BAY:
        for dy in range(-ry, ry + 1):
            for dx in range(-rx, rx + 1):
                if (dx / max(rx, 1)) ** 2 + (dy / max(ry, 1)) ** 2 <= 1.0:
                    x, y = cx + dx, cy + dy
                    if 0 <= x < AW and 0 <= y < AH:
                        zone.collision_layer[y][x] = "tropical_water"
                        zone.set_tile(x, y, "tropical_water", "base")
    # The shelf: painted on blocked tiles at the bay's edge, so it reads as wadeable water without
    # letting the player swim the cove and skip both bosses.
    for (cx, cy, rx, ry) in COVE_SHALLOWS:
        for dy in range(-ry, ry + 1):
            for dx in range(-rx, rx + 1):
                if (dx / max(rx, 1)) ** 2 + (dy / max(ry, 1)) ** 2 <= 1.0:
                    x, y = cx + dx, cy + dy
                    if 0 <= x < AW and 0 <= y < AH and not zone.is_walkable(x, y):
                        zone.set_tile(x, y, "tropical_shallow", "base")

    # The ramp up her side, at the head of the cove, out over the water.
    sb.gangplank(b, A_OUT[0], 24, 14, base="path", width=3)

    # Headland rock. Placed to PINCH the walk round the bay, so the east shore has a neck in it
    # rather than being an open promenade.
    b.pillar(84, 58, size=5)
    b.pillar(78, 30, size=4)
    b.pillar(24, 54, size=4)
    b.pillar(34, 28, size=3)

    for (px, py) in (A_IN, A_OUT):
        zone.collision_layer[py][px] = None
        L.mark("portal", px, py)

    zone.boss_positions = [(x, y, n) for n, (x, y) in ANCHORAGE_BOSS_AT.items()]
    zone.boss_position = zone.boss_positions[0][:2]
    for (x, y, n) in zone.boss_positions:
        L.mark("boss_marker", x, y)
    zone.trash_spawns = sb.place_packs(zone, ANCHORAGE_PACKS)

    # THE WEST HORN IS A LONG WALK TO NOTHING otherwise. The cove is a U and the route up the east
    # side is the dungeon; the west side is scenery you can walk the whole length of, which is the
    # kind of thing a player explores once and resents. A chest at the far end of it is the
    # cheapest honest reason for it to be there.
    ANCHORAGE_CHESTS[:] = [(28, 40), (56, 26)]
    for (cx, cy) in ANCHORAGE_CHESTS:
        L.mark("chest", cx, cy)

    zone.add_subzone("The Bloodsail Anchorage", 0, 0, AW, AH)
    zone.add_subzone("The Landing", 32, 70, 46, 24)
    zone.add_subzone("The Cove", 24, 36, 58, 34)
    zone.add_subzone("The Head of the Cove", 28, 14, 48, 24)
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

    P("bloodsail_galleon", 52, 22, 20, near_ok=True, **C)
    # the water's edge, at the head of the cove
    P("mooring_posts", 44, 24, 3, near_ok=True, **C)
    P("bs_rope_coil", 56, 25, 2, near_ok=True, **S)
    P("bs_lamp_post", 62, 28, 5, **S)
    # ... and the island itself, thickest on the east horn you walk up
    P("mangrove_thicket", 72, 80, 5, **C)
    P("banana_plant", 66, 76, 4, **C)
    P("jungle_banyan", 78, 70, 8, **C)
    P("sea_stack_spire", 84, 52, 8, **C)
    P("mossy_jungle_boulder", 76, 62, 4, **C)
    P("coral_reef_outcrop", 70, 70, 3, near_ok=True, **C)
    P("hibiscus_bush", 80, 44, 3, near_ok=True, **C)
    P("bamboo_grove", 78, 34, 6, **C)
    P("driftwood_pile", 68, 82, 3, near_ok=True, **C)
    P("tiki_totem", 30, 46, 5, **C)
    P("crab_claw_arch", 32, 34, 5, **C)
    P("sea_stack_spire", 26, 60, 8, **C)
    P("mangrove_thicket", 24, 72, 5, **C)
    P("jungle_banyan", 34, 54, 8, **C)
    P("mossy_jungle_boulder", 24, 36, 4, **C)
    P("buried_treasure_chest", 32, 44, 3, near_ok=True, **C)
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
    b.pillar(74, 48, size=4)
    b.pillar(64, 28, size=3)
    b.pillar(48, 50, size=3)
    b.pillar(42, 28, size=3)

    for (px, py) in (D_IN, D_HATCH):
        zone.collision_layer[py][px] = None
        L.mark("portal", px, py)

    zone.boss_positions = [(x, y, n) for n, (x, y) in GDECK_BOSS_AT.items()]
    zone.boss_position = zone.boss_positions[0][:2]
    for (x, y, n) in zone.boss_positions:
        L.mark("boss_marker", x, y)
    zone.trash_spawns = sb.place_packs(zone, GDECK_PACKS)

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
    P("bs_cannon_deck", 44, 46, 3, **S)
    P("bs_weapon_rack", 34, 34, 4, **S)
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
    zone.trash_spawns = sb.place_packs(zone, GHOLD_PACKS)

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
    sb.bulwark(b, base="dirt")

    for (px, py) in (C_IN, C_OUT):
        zone.collision_layer[py][px] = None
        L.mark("portal", px, py)

    # The pair, as ONE SpawnPoint. boss_positions carries only the lead.
    zone.boss_positions = [(30, 24, CABIN_LEAD)]
    zone.boss_position = (30, 24)
    zone.boss_pack = CABIN_PACK
    L.mark("boss_marker", 30, 24)

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
    return L.finish([C_IN, C_OUT, (30, 24)] + members)


def generate_cabin():
    zone, L = build_cabin()
    dress_cabin(zone, L)
    finish_cabin(zone, L)
    return zone
