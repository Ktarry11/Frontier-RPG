"""The Bloodsail Raider: two zones, levels 38-42. The ship that grappled us.

THE RAIDER IS A LAP, and that is the whole shape of it.

    weather deck    board at the STERN, fight FORWARD
    bow hatch       down
    the hold        run AFT, back the way you came, one deck lower
    the cabin       under the quarterdeck you boarded over. The exit is the tile past the Captain.

Kyle's requirement was "another portal right after the last boss that returns us to our ship so we
don't back pedal". The cheap way to honour that is a teleport out of a dead end, which makes the
hold a cul-de-sac and the whole ship a there-and-back. A lap instead: the ship gets used twice, in
opposite directions, on two decks, and the exit is where it is because that is where the cabin
actually is on a ship of this kind. The player works that out on arriving in the cabin, which is
the moment the layout pays off.

BULKHEADS ARE WHAT MAKE A HULL A DUNGEON. Below decks a ship is one long open space, and one long
open space has no pull structure - every fight is the same fight at a different x. ship_builder
.bulkhead cuts the hold into compartments with one doorway each, and the doorways alternate port
and starboard so the run aft is a zigzag rather than a corridor.

EACH BOSS'S PACKS SIT IN ITS OWN COMPARTMENT, and that is not fussiness. world/dungeon_packs
assigns a pack to the boss it leads to by PATH DISTANCE, and a hull is one long line, so a pack
placed "on the way to" the second boss is still nearer the first. An earlier pass of this dungeon
came out with three pulls before the First Mate and ZERO before the Captain, which reads as the
final boss having no approach at all.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked  # noqa: F401
import tools.ship_builder as sb

BAKED = "assets/tiles/return_voyage/{}/baked"   # .format(slug); bake_durotar_caves formats it
CP = "assets/tiles/coastal_props/"
SP = "assets/tiles/ship_props/"

W, H = 110, 70
#: 89 long on a 29 beam. Smaller than the galleon, which is the point of her being a raider.
HULL = dict(x0=10, x1=98, ycen=35, beam=14, bow="w")
#: The hold is the same hull one deck down, so it is narrower - a ship's sides come in below the
#: waterline, and a hold as wide as the weather deck would give the lap away by feeling identical.
HOLD = dict(x0=12, x1=96, ycen=35, beam=11, bow="w")

# ---- weather deck
D_IN = (94, 35)         # boarded over the quarterdeck rail, from The Crossing
D_HATCH = (18, 35)      # the bow hatch, down to the hold
# ---- hold
H_IN = (18, 35)         # arrive at the bow, one deck down
H_OUT = (92, 35)        # the cabin door, back to The Crossing. Past the Captain.

#: THE ROSTER IS DECLARED HERE and the creature data is written from it, not the other way round.
#: An earlier pass had placeholder names in the trash tables and real names in creatures.json; they
#: did not match, and world/cave_spawns raises on zone entry for a spawn whose creature is unknown -
#: so the dungeon was broken from the first step into it, and nothing before that step said so.
TRASH = ["Bloodsail Swab", "Bloodsail Cannoneer", "Bloodsail Bosun"]
DECK_BOSSES = ["Bosun Harl Greave", "Topman Yanni Sear"]
HOLD_BOSSES = ["First Mate Oskar Vane", "Captain Ruel Scuttler"]

#: (cx, cy, level, [names]) - a pull. Levels rise forward on the deck and aft in the hold, which is
#: the direction of travel on each.
DECK_PACKS = [
    (88, 30, 38, ["Bloodsail Swab", "Bloodsail Swab", "Bloodsail Cannoneer"]),
    (80, 41, 38, ["Bloodsail Swab", "Bloodsail Bosun", "Bloodsail Swab"]),
    (72, 29, 39, ["Bloodsail Cannoneer", "Bloodsail Swab", "Bloodsail Swab"]),
    # ---- past Greave. These sit FORWARD of the midpoint between the two bosses, or path distance
    # assigns them to Greave and Sear gets no approach at all.
    (40, 40, 40, ["Bloodsail Bosun", "Bloodsail Swab", "Bloodsail Cannoneer"]),
    (36, 29, 40, ["Bloodsail Swab", "Bloodsail Cannoneer", "Bloodsail Swab"]),
    (30, 40, 41, ["Bloodsail Bosun", "Bloodsail Swab", "Bloodsail Swab"]),
]
DECK_BOSS_AT = {"Bosun Harl Greave": (68, 35), "Topman Yanni Sear": (20, 35)}
#: (station x, gap y_lo, y_hi) - the gaps the two deck bosses hold.
DECK_BARRICADES = [(60, 33, 37), (28, 33, 37)]

HOLD_PACKS = [
    (25, 31, 40, ["Bloodsail Swab", "Bloodsail Swab", "Bloodsail Bosun"]),
    (31, 39, 40, ["Bloodsail Cannoneer", "Bloodsail Swab", "Bloodsail Swab"]),
    (37, 31, 41, ["Bloodsail Swab", "Bloodsail Bosun", "Bloodsail Cannoneer"]),
    # ---- past Vane, and AFT of the midpoint between him and the Captain, for the same reason.
    (74, 39, 41, ["Bloodsail Cannoneer", "Bloodsail Swab", "Bloodsail Swab"]),
    (76, 31, 42, ["Bloodsail Bosun", "Bloodsail Cannoneer", "Bloodsail Swab"]),
    (80, 39, 42, ["Bloodsail Swab", "Bloodsail Swab", "Bloodsail Bosun"]),
]
#: IN THEIR OWN COMPARTMENTS, not jammed in the doorways. I had moved every boss into a doorway
#: and narrowed every doorway to the three tiles a boss covers, so that none of them could be run
#: past. Kyle, on seeing it: "in all honesty, if people want to skip bosses they can. just need to
#: make sure that we have trash mobs too. if people wanna miss loot chances thats fine. we have
#: optional bosses in dungeons already." Which is the right call and a better game - a boss you
#: cannot decline is a toll, not an encounter. The bulkheads stay, because compartments are what
#: give the hold its pulls, and the pulls are the part he does want.
HOLD_BOSS_AT = {"First Mate Oskar Vane": (44, 35), "Captain Ruel Scuttler": (88, 35)}

#: (station x, doorway y_lo, y_hi). Alternating sides, so the run aft zigzags. Each one is checked
#: for being a real cut - see build_hold.
BULKHEADS = [
    (26, 28, 31),
    (38, 39, 42),
    (50, 28, 31),
    (62, 39, 42),
    (72, 29, 32),
    (82, 38, 41),    # the cabin door
]


def _sea(zone):
    for y in range(zone.height):
        for x in range(zone.width):
            zone.collision_layer[y][x] = "tropical_water"
            zone.set_tile(x, y, "tropical_water", "base")


def _hull_zone(name, desc, start, hull, floor="path"):
    zone = Tilemap(name, W, H, desc)
    zone.is_cave = True
    zone.region = "The Crossing"
    zone.fixed_spawns = True
    L = CaveLayout(zone, start)
    b = L.b
    b.wall_id = "tropical_water"
    b.floor_id = floor
    _sea(zone)
    stations = sb.carve_hull(b, base=floor, **hull)
    return zone, L, stations


# ============================================================ THE WEATHER DECK
def build_raider_deck():
    zone, L, stations = _hull_zone(
        "The Bloodsail Raider",
        "Her weather deck, grappled to our starboard side. The boarding party went the other way; "
        "these are the ones who stayed with the ship.",
        D_IN, HULL)
    b = L.b

    sb.platform(b, 14, 29, 30, 41, base="sand")     # forecastle - Sear's
    sb.platform(b, 82, 27, 96, 43, base="sand")     # quarterdeck - where we came over
    sb.platform(b, 50, 30, 58, 40, base="stone")    # the main hatch surround

    # DECK HOUSES AND CARGO, placed as solid blocks. A weather deck has no bulkheads, so what gives
    # it structure is the stuff standing on it - and the gaps between the stuff are the pull points.
    # Staggered port and starboard so the run forward weaves instead of going straight up the middle.
    b.pillar(68, 27, size=3)
    b.pillar(60, 41, size=3)
    b.pillar(44, 26, size=3)
    b.pillar(36, 42, size=3)
    b.pillar(78, 40, size=2)
    b.pillar(72, 24, size=2)

    # TWO BARRICADES ACROSS HER, each with one gap. They went in to stop the deck bosses being
    # walked round and they stay now that that is no longer required, because what they really do
    # is give an open deck some pull structure - the gap is a pull point, and the stretch between
    # two of them is a room. Lashed cargo and gun tackle rather than a wall: a fighting deck
    # somebody has made defensible in a hurry.
    for (station, lo, hi) in DECK_BARRICADES:
        closed = sb.choke(b, "x", station, lo, hi, base="dirt")
        if closed < 8:
            raise AssertionError(f"{zone.name}: barricade at x={station} closed only {closed} "
                                 f"tiles - the gap is as wide as the deck there")

    for (px, py) in (D_IN, D_HATCH):
        zone.collision_layer[py][px] = None
        L.mark("portal", px, py)

    zone.boss_positions = [(x, y, n) for n, (x, y) in DECK_BOSS_AT.items()]
    zone.boss_position = zone.boss_positions[0][:2]
    for (x, y, n) in zone.boss_positions:
        L.mark("boss_marker", x, y)
    zone.trash_packs = sb.place_packs(zone, DECK_PACKS)
    zone.trash_spawns = [m for pack in zone.trash_packs for m in pack]

    zone.add_subzone("The Bloodsail Raider", 0, 0, W, H)
    zone.add_subzone("The Quarterdeck", 78, 24, 30, 24)
    zone.add_subzone("The Waist", 32, 22, 48, 28)
    zone.add_subzone("The Forecastle", 10, 26, 24, 20)
    return zone, L, stations


def dress_raider_deck(zone, L):
    P = L.prop
    S = dict(where=SP)
    P("bs_bloodsail_flag", 90, 31, 6, **S)
    P("bs_ships_bell", 86, 40, 4, **S)
    P("bs_cannon_deck", 70, 31, 3, **S)
    P("bs_cannon_deck", 62, 38, 3, **S)
    P("bs_powder_barrels", 66, 42, 3, **S)
    P("bs_cargo_net", 56, 28, 3, **S)
    P("bs_crate_stack", 48, 42, 4, **S)
    P("bs_rope_coil", 52, 33, 2, near_ok=True, **S)
    P("bs_cannon_deck", 40, 30, 3, **S)
    P("bs_water_barrel", 32, 38, 3, **S)
    P("bs_weapon_rack", 20, 30, 4, **S)
    P("bs_lamp_post", 16, 39, 5, **S)
    return zone, L


def finish_raider_deck(zone, L):
    return L.finish([D_IN, D_HATCH] + [(x, y) for (x, y, _n) in zone.boss_positions]
                    + [(s[0], s[1]) for s in zone.trash_spawns])


def build_raider_deck_baked():
    zone, L, _s = build_raider_deck()
    dress_raider_deck(zone, L)
    finish_raider_deck(zone, L)
    return zone, L


def generate_raider_deck():
    zone, L = build_raider_deck_baked()
    register_baked(zone, BAKED.format("raider_deck"))
    return zone


# ================================================================== THE HOLD
def build_raider_hold():
    zone, L, stations = _hull_zone(
        "The Raider's Hold",
        "Below her weather deck, bow to stern: cable tier, powder, cargo, and the Captain's cabin "
        "under the quarterdeck you came aboard over.",
        H_IN, HOLD, floor="dirt")
    b = L.b

    sb.platform(b, 84, 28, 94, 42, base="path")     # the cabin, aft - a made room, not a hold

    cuts = []
    for (x, lo, hi) in BULKHEADS:
        sealed = sb.bulkhead(b, stations, x, lo, hi)
        cuts.append((x, sealed))
    # A BULKHEAD WITH NOTHING EITHER SIDE OF IT IS A WALL WITH A HOLE IN IT, and connectivity tests
    # pass on one happily - the hold stays walkable end to end and has no compartments. So check
    # every one actually sealed something.
    bad = [(x, n) for (x, n) in cuts if n < 4]
    if bad:
        raise AssertionError(f"{zone.name}: bulkheads that barely cut anything: {bad} - "
                             f"the doorway is as wide as the hull at that station")

    for (px, py) in (H_IN, H_OUT):
        zone.collision_layer[py][px] = None
        L.mark("portal", px, py)

    zone.boss_positions = [(x, y, n) for n, (x, y) in HOLD_BOSS_AT.items()]
    zone.boss_position = zone.boss_positions[0][:2]
    for (x, y, n) in zone.boss_positions:
        L.mark("boss_marker", x, y)
    zone.trash_packs = sb.place_packs(zone, HOLD_PACKS)
    zone.trash_spawns = [m for pack in zone.trash_packs for m in pack]

    zone.add_subzone("The Raider's Hold", 0, 0, W, H)
    zone.add_subzone("The Cable Tier", 12, 24, 20, 22)
    zone.add_subzone("The Powder Room", 32, 24, 24, 22)
    zone.add_subzone("The Cargo Hold", 56, 24, 24, 22)
    zone.add_subzone("The Captain's Cabin", 82, 26, 24, 18)
    return zone, L, stations


def dress_raider_hold(zone, L):
    P = L.prop
    S = dict(where=SP)
    P("bs_hanging_lantern", 20, 31, 3, **S)
    P("bs_rope_coil", 16, 38, 2, near_ok=True, **S)
    P("bs_hammock", 24, 40, 3, **S)
    P("bs_powder_barrels", 36, 31, 3, **S)
    P("bs_barrel_cluster", 44, 39, 3, **S)
    P("bs_bilge_pump", 54, 33, 4, **S)
    P("bs_crate_stack", 60, 31, 4, **S)
    P("bs_cargo_net", 68, 40, 3, **S)
    P("bs_sea_chest", 74, 32, 2, near_ok=True, **S)
    # ---- the cabin
    P("bs_captains_desk", 84, 32, 4, **S)
    P("bs_wine_rack", 90, 39, 4, **S)
    P("bs_candelabra", 86, 38, 3, near_ok=True, **S)
    return zone, L


def finish_raider_hold(zone, L):
    return L.finish([H_IN, H_OUT] + [(x, y) for (x, y, _n) in zone.boss_positions]
                    + [(s[0], s[1]) for s in zone.trash_spawns])


def build_raider_hold_baked():
    zone, L, _s = build_raider_hold()
    dress_raider_hold(zone, L)
    finish_raider_hold(zone, L)
    return zone, L


def generate_raider_hold():
    zone, L = build_raider_hold_baked()
    register_baked(zone, BAKED.format("raider_hold"))
    return zone
