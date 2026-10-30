"""
Hand-built layout for the Gurbashi Arena (80x140), a FIVE-ROOM GAUNTLET in Central Stranglethorn.

Kyle, 29 Oct 2026: "we can make the Gurbashi arena a gauntlet style dungeon where it's just 5 rooms
with hard bosses."

WHAT A GAUNTLET IS, AND WHAT IT IS NOT.  Five rooms, five bosses, and NOTHING between them.  The
moment you pad the walk with pulls it stops being a gauntlet and becomes a short dungeon with thin
trash, which is the worst version of both.  So there is no trash list in this module and no trash
table in the encounter block: zone.fixed_spawns stays True (so the per-tile random roll in
OverworldScreen never fires here) and the encounter table contains bosses only, which leaves
world/cave_spawns.populate() with an empty `trash` dict and nothing to scatter.

ONE ENTRANCE, ONE LINE.  The map is 80 wide and 140 tall because a gauntlet should read as a line,
not a square: you come in at the top, the five pits run south, and each chamber's only southern gate
is on the far side of its own floor.  There is no branch, no loop and no shortcut anywhere in the
build - which is the whole point, and tests/verification asserts it by flood-filling with chamber N
walled off and confirming chamber N+1 goes dark.

    The Sand Gate ......... vestibule.  EXIT portal (40,12); you arrive at (40,10)
    The Opening Bout ...... room 1, boss (40,34)    Vek'tar the Unbeaten
    The Hot Grate ......... room 2, boss (40,59)    Grateward Mok'tal
    The Pairing ........... room 3, boss (40,84)    Rakjan the Ribcracker (+ Jin'sha the Bloodcaller)
    The Hard Round ........ room 4, boss (40,109)   Zul'gar Hammerfall
    The House Floor ....... room 5, boss (40,130)   Jen'shala, the House Favourite

WHY YOU ARE DOWN HERE.  You did not break in.  The Gurbashi still run the pits, they still take
entries, and somebody in Booty Bay has already written your name on a board and taken money on it.
Every room is somebody's livelihood: the drum crew in the first pit, the grate stoker in the second,
the pair-handlers in the third.  Nobody here is trying to stop you reaching the floor - they are
trying to make sure the crowd gets its money's worth on the way.

HARD CONTRACTS (world/portal_manager.py: Central Stranglethorn (150,100) -> Gurbashi Arena (40,12);
the return side is wired elsewhere and is deliberately NOT added here).
    zone.is_cave = True, region "Eastern Kingdoms - Stranglethorn", size 80x140, band 36-38.
    Exit portal (40,12) and arrival (40,10) are both walkable and both inside the vestibule.

ART.  Nothing here waits on new art.  The floors and walls are baked by tools/bake_gurbashi_arena.py
out of materials that already ship (the Durotar/VoT desert set plus the Burning Blade grate), and
every prop below is an existing sprite: troll banners, totems and a cookfire from the coastal set,
the Gurbashi idol and a ruin from Echo Isles, and pillars, cages, braziers and vents from the shared
dungeon props.

Prop rule (Kyle): less is more.  A few centrepieces per room, each one logical for that room - the
drum that starts a bout, the vents in the grate pit, the pair's cage, the idol the house bets under.
Every placement goes through CaveLayout.prop, which refuses anything sitting on a marker or anything
that would wall a tile off.
"""
import os

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401

CP = "assets/tiles/coastal_props/"
JP = "assets/tiles/echo_isles/props/"
SR = "assets/tiles/skull_rock/props/"

NAME = "Gurbashi Arena"
DESC = ("A Gurbashi fighting pit sunk under Stranglethorn: five floors in a line, a crowd on every "
        "rim, and bookmakers who already know your name.")
REGION = "Eastern Kingdoms - Stranglethorn"
SP = "assets/tiles/stranglethorn/props/"
#: a couple of shared sprites that Sheet C and E did not replace - the signal
#: beacon and the hulls - still live with the other coastal art.
CPD = "assets/tiles/coastal_props/"
W, H = 80, 140
BAKED = "assets/tiles/gurbashi_arena/{}/baked"
SLUG = "arena"

LEVEL_BAND = (36, 38)

# ---------------------------------------------------------------- the line
PORTAL = (40, 12)                 # EXIT portal (hard contract)
ARRIVAL = (40, 10)                # where the player lands coming in (hard contract)

#: Each chamber: (table_key, x0, y0, x1, y1, chamfer).  Drawn top to bottom; the gate between
#: consecutive chambers is the ONLY join, so chamber order IS progression order.
CHAMBERS = [
    ("The Sand Gate",      28,   5, 52,  19, 4),
    ("The Opening Bout",   16,  24, 64,  43, 6),
    ("The Hot Grate",      16,  48, 64,  67, 6),
    ("The Pairing",        16,  72, 64,  91, 6),
    ("The Hard Round",     16,  96, 64, 115, 6),
    ("The House Floor",    13, 120, 67, 137, 5),
]

#: Boss chamber centres, in order.  Room N's boss stands on room N's floor; the gate south of it is
#: on the other side of that floor, so you cannot walk past a boss without crossing its pit.
BOSSES = [
    (40,  34, "Vek'tar the Unbeaten"),
    (40,  59, "Grateward Mok'tal"),
    (40,  84, "Rakjan the Ribcracker"),
    (40, 109, "Zul'gar Hammerfall"),
    (40, 130, "Jen'shala, the House Favourite"),
]

#: The add in room 3.  It is NOT a pinned boss chamber - it is the second member of a PACK, so
#: stepping onto Rakjan's floor pulls both at once and the fight is a target-priority problem rather
#: than two tidy duels.  See world/cave_spawns.populate(): pinned chambers and zone.trash_packs are
#: laid out by separate passes, so the pack places Rakjan and the pinned list leaves him out.
ADD = (34, 84, "Jin'sha the Bloodcaller")

#: One chest per pit, off to the side of the floor so it never shares a tile with a boss marker.
CHESTS = [(24, 39), (56, 63), (24, 87), (56, 111), (40, 135)]


def _gate(b, y_from, y_to):
    """The single corridor joining one pit to the next."""
    b.corridor([(40, y_from), (40, y_to)], width=3)


def build_arena():
    zone = Tilemap(NAME, W, H, DESC)
    zone.is_cave = True
    #: .region declares the PARENT ZONE for the encounter lookup (world/zone_manager.py) - pinned by
    #: the hard contract, and tools/build_gurbashi_content.py writes the cave table under this key.
    zone.region = REGION
    #: TRUE, unlike every single-boss cave in the game: a gauntlet must not have the open world's
    #: random per-tile roll firing between pits.  With a boss-only encounter table this also means
    #: populate() has no trash to scatter, which is exactly the shape Kyle asked for.
    zone.fixed_spawns = True

    L = CaveLayout(zone, ARRIVAL)
    b = L.b

    # --- the five pits and the vestibule above them, plus the five gates that join them
    for (_key, x0, y0, x1, y1, ch) in CHAMBERS:
        b.rect(x0, y0, x1, y1, chamfer=ch)
    for (a, _b) in zip(CHAMBERS, CHAMBERS[1:]):
        _gate(b, a[4], _b[2])

    # --- subzones: whole map first so each pit's own name overrides it
    zone.add_subzone(NAME, 0, 0, W, H)
    for (key, x0, y0, x1, y1, _ch) in CHAMBERS:
        zone.add_subzone(key, x0 - 2, y0 - 1, (x1 - x0) + 5, (y1 - y0) + 3)

    # --- markers
    L.mark("portal", *PORTAL)
    for (x, y, _n) in BOSSES:
        L.mark("boss_marker", x, y)
    for c in CHESTS:
        L.mark("chest", *c)

    #: Four PINNED chambers.  Rakjan is missing on purpose: he arrives with his handler as a pack
    #: (zone.trash_packs below).  With no unpinned chambers in this list nothing ever draws from the
    #: shared boss pool, so he cannot also be spawned a second time somewhere else.
    zone.boss_positions = [(x, y, n) for (x, y, n) in BOSSES if n != "Rakjan the Ribcracker"]
    zone.boss_position = (BOSSES[0][0], BOSSES[0][1])
    zone.trash_packs = [[
        (BOSSES[2][0], BOSSES[2][1], BOSSES[2][2], 37),
        (ADD[0], ADD[1], ADD[2], 36),
    ]]

    # --- props.  A few per pit, each one somebody's job.
    p = L.prop
    # The Sand Gate: the way out, a banner either side of it, and the totem entries are marked at.
    p("stv_arena_standard", 33, 8, 6, where=SP, solid="core")
    p("stv_arena_standard", 47, 8, 6, where=SP, solid="core")
    p("stv_troll_totem", 31, 17, 5, where=SP, solid="core")
    p("stv_troll_totem", 49, 17, 5, where=SP, solid="core")
    # The Opening Bout: the drum crew start every bout, and the sand keeps what the last one left.
    p("vot_war_drum", 22, 28, 4, solid="core")
    p("vot_war_drum", 58, 28, 4, solid="core")
    p("vot_totem_pole", 19, 36, 6, solid="core")
    p("vot_totem_pole", 61, 36, 6, solid="core")
    p("skull_pile", 50, 41, 3)
    # The Hot Grate: the stoker's vents and the fire he keeps under the floor.
    p("rf_steam_vent", 24, 53, 4)
    p("rf_steam_vent", 56, 53, 4)
    p("rf_brazier", 20, 62, 5, solid="core")
    p("rf_brazier", 60, 62, 5, solid="core")
    p("lava_spikes", 48, 66, 4, where=SR)
    # The Pairing: the cage the pair are kept in, and the handlers' fire.
    p("rf_prison_cage", 21, 78, 5, solid="core")
    p("rf_prison_cage", 59, 78, 5, solid="core")
    p("stv_troll_cookfire", 29, 90, 4, where=SP)
    p("bone_pile", 52, 89, 3, where=SR)
    # The Hard Round: the pit they do not sweep, and two pillars that have been hit a lot.
    p("broken_column", 23, 102, 6, solid="core")
    p("broken_column", 57, 102, 6, solid="core")
    p("rf_fallen_pillar", 30, 114, 4)
    p("cracked_pillar", 50, 114, 6, where=SR, solid="core")
    # The House Floor: the idol the house bets under, the ruin it was built into, the banners.
    p("stv_troll_idol_head", 40, 124, 7, where=SP, solid="core", avoid=3)
    p("stv_troll_ziggurat_block", 18, 128, 6, where=SP, solid="core")
    p("stv_troll_totem", 62, 128, 5, where=SP, solid="core")
    p("stv_arena_standard", 26, 135, 6, where=SP, solid="core")
    p("stv_arena_standard", 54, 135, 6, where=SP, solid="core")

    L.finish([ARRIVAL, PORTAL] + [(x, y) for (x, y, _n) in BOSSES] + [ADD[:2]] + CHESTS)
    return zone, L


def chamber_tiles(zone, index):
    """Every walkable tile of chamber `index` (0 = the vestibule).  Used by the sequence check."""
    _key, x0, y0, x1, y1, _ch = CHAMBERS[index]
    return {(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)
            if zone.is_walkable(x, y)}


def generate_gurbashi_arena():
    zone, _ = build_arena()
    if os.path.exists(f"{BAKED.format(SLUG)}/ground_0_0.jpg"):
        register_baked(zone, BAKED.format(SLUG))
    return zone
