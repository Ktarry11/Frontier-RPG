"""The Crossing (120x100): the boat home from Booty Bay, with two Bloodsail ships on it.

THE ASYMMETRY IS THE WHOLE IDEA.

    Ratchet -> Booty Bay    direct. Unchanged. A boat ride.
    Booty Bay -> Ratchet    you arrive ON THE BOAT, mid-crossing, under attack.

Going south is travel; coming north is an event, and a player who has only ever sailed one way
never learns this exists. tools/verify_return_voyage.py asserts both directions, so a later tidy-up
cannot quietly make them symmetrical.

This module owns the hub. The two ships alongside are separate modules, because each is a dungeon:

    tools/handbuilt_bloodsail_raider.py     2 zones, levels 38-42
    tools/handbuilt_bloodsail_galleon.py    4 zones, levels 47-52

WHAT IS ON THIS MAP. Our own deck, with four ways off it and no combat on it - the hub has to stay
safe or a player who zones out of a dungeon at 10% health dies to the hub. North, a plank across to
the raider that has grappled us. South, a plank down to a sand bar the galleon is moored against.

THE ISLAND IS SMALL AND THAT IS DELIBERATE. Kyle: "It's a small island it docks on. The island will
be smaller In the travel (BB to ratchet) section and that's where the dungeon portal is. It expands
when you enter it." So what you see from our rail is a sand bar with a galleon tied to it; the cove
you fight down is behind the portal. The player crossing that plank cannot tell how much island is
on the other side, which is the point.

NO SHIPS' GEAR ON THE BEACH. An earlier pass scattered cargo nets, powder, sail bundles and rope
across the sand, which is what CAREENING looks like - a ship hauled out for hull work with her
inventory dumped on the shore. She is moored, not careened. The only made things on the sand are at
the water's edge where a ship ties up.

THE SEA IS THE WALL. wall_id="tropical_water", which is flagged walkable: False, so an uncarved tile
blocks like rock and the rail costs no tiles. Water is otherwise WALKABLE in this engine (only tile
kind 3 sets collision), so the obvious way to paint a sea zone lets the player walk off the
quarterdeck to Ratchet. Kyle, on the colour: "i assume we are throwing in tropical water colour lol"
- hence tropical_water/tropical_shallow rather than deep_water, which is a North Atlantic blue and
right for Tirisfal and wrong for this crossing.

HARD CONTRACT (world/portal_manager.py): Booty Bay (64, 34) -> The Crossing. Four portals out.
"""
import os

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked  # noqa: F401
import tools.ship_builder as sb

CP = "assets/tiles/coastal_props/"
SP = "assets/tiles/ship_props/"

W, H = 120, 100

#: Our ship. 85 long on a 27 beam is about 3:1, which reads as a ship rather than as a room.
HULL = dict(x0=18, x1=102, ycen=50, beam=13, bow="w")

#: The four ways off this deck. Every one of them is a portal_manager entry as well; the two have
#: to agree or you get a tile that looks like a door and is not one.
P_RATCHET = (24, 50)        # forward, the way we are going
P_BOOTY = (98, 50)          # aft, the way we came
P_RAIDER = (58, 32)         # the north plank - Kyle: "lets have the northern portal on the gangplank"
P_ANCHORAGE = (60, 80)      # on the sand bar, where the galleon is tied up

#: North plank, out to the raider that grappled us. The portal sits ON it, which is the thing Kyle
#: asked for: a portal on a bare stretch of rail is a hole in the air, and a plank is a reason.
#: It has to run two tiles PAST the portal, because PortalManager._offset_spawn drops an arriving
#: player two tiles north of the destination tile, and two north of (58, 32) must be plank and not
#: open water.
PLANK_N = dict(x=58, y_from=37, y_to=28, width=3)
#: South plank, down to the sand bar.
PLANK_S = dict(x=56, y_from=62, y_to=74, width=3)

#: The sand bar. Two lobes that OVERLAP - an earlier shrink left the mooring lobe just touching the
#: main one, the gap closed when a prop went down, and 73 tiles of island stranded themselves. The
#: flood fill caught it; looking at the render did not.
ISLET = [(58, 78, 8, 6), (70, 80, 6, 4)]


def build_the_crossing():
    zone = Tilemap("The Crossing", W, H,
                   "The deck of the Ratchet boat, somewhere north of Booty Bay. There is a raider "
                   "grappled to your port side and a galleon moored off the sand bar to starboard, "
                   "and the crew are not going to be the ones to deal with either.")
    zone.is_cave = False
    #: .region declares the PARENT ZONE - the encounter lookup keys off it (world/zone_manager.py).
    zone.region = "The Crossing"
    zone.fixed_spawns = True

    L = CaveLayout(zone, (P_RATCHET[0], P_RATCHET[1]))
    b = L.b
    b.wall_id = "tropical_water"
    b.floor_id = "path"
    # CaveLayout hands Builder rock/dirt; this is a sea, so repaint the whole map before carving.
    for y in range(H):
        for x in range(W):
            zone.collision_layer[y][x] = "tropical_water"
            zone.set_tile(x, y, "tropical_water", "base")

    stations = sb.carve_hull(b, base="path", **HULL)

    # DECK STRUCTURE, because a fair hull in one flat colour reads as an island. A raised
    # forecastle forward, the waist amidships where the work happens, the quarterdeck aft over
    # the cabin, and a cargo hatch in the middle of the waist.
    # Pale tiles for the raised decks: a scrubbed deck IS paler than the working waist, and grey
    # stone on a wooden ship reads as a slab somebody left on the planking.
    sb.platform(b, 22, 44, 36, 56, base="sand")        # forecastle
    sb.platform(b, 86, 42, 100, 58, base="sand")       # quarterdeck, over the cabin
    sb.platform(b, 56, 47, 62, 53, base="stone")       # the main hatch - a hole, so dark
    sb.bulwark(b, base="dirt")                         # the gunwale, last so it wins the edge

    sb.gangplank(b, PLANK_N["x"], PLANK_N["y_from"], PLANK_N["y_to"],
                 base="path", width=PLANK_N["width"])
    sb.gangplank(b, PLANK_S["x"], PLANK_S["y_from"], PLANK_S["y_to"],
                 base="path", width=PLANK_S["width"])
    b.lobes(ISLET, base="sand")

    # A SHOAL ROUND THE SAND BAR, painted on tiles that are still blocked. The base layer is only
    # what you see; is_walkable reads the collision layer first, so this is turquoise shallows you
    # cannot wade into - which is what keeps the player on the island without a fence.
    for (cx, cy, rx, ry) in ISLET:
        for dy in range(-ry - 4, ry + 5):
            for dx in range(-rx - 5, rx + 6):
                x, y = cx + dx, cy + dy
                if not (0 <= x < W and 0 <= y < H):
                    continue
                d = (dx / (rx + 5.0)) ** 2 + (dy / (ry + 4.0)) ** 2
                if d <= 1.0 and not zone.is_walkable(x, y):
                    zone.set_tile(x, y, "tropical_shallow", "base")

    for (px, py) in (P_RATCHET, P_BOOTY, P_RAIDER, P_ANCHORAGE):
        zone.collision_layer[py][px] = None
        L.mark("portal", px, py)

    zone.add_subzone("The Crossing", 0, 0, W, H)
    zone.add_subzone("The Weather Deck", 18, 36, 85, 28)
    zone.add_subzone("The Boarding Plank", 52, 26, 13, 14)
    zone.add_subzone("The Sand Bar", 46, 70, 36, 18)
    return zone, L, stations


def dress(zone, L):
    """Our own deck, the two ships alongside, and the sand bar.

    The ships are landmark sprites rather than carved hulls, because from our rail that is all they
    are - you can see them, you cannot walk onto them without crossing a plank, and what is on the
    other side of the plank is a dungeon with its own map.
    """
    P = L.prop
    S = dict(where=SP)
    C = dict(where=CP)

    # ---- THE TWO SHIPS. Bottom-centre anchors sit on the plank ends, so each sprite stands off our
    # beam with its boarding plank running to it.
    P("bloodsail_raider", 58, 28, 22, near_ok=True, **C)
    P("bloodsail_galleon", 72, 83, 18, near_ok=True, **C)

    # ---- OUR DECK. A working merchantman that has just been boarded: her own gear, and the first
    # evidence of the people who came over the rail.
    P("bs_water_barrel", 34, 46, 3, **S)
    P("bs_crate_stack", 38, 55, 4, **S)
    P("bs_cargo_net", 44, 58, 3, **S)
    P("bs_rope_coil", 48, 43, 2, near_ok=True, **S)
    P("bs_ships_bell", 30, 52, 4, **S)
    P("bs_sail_bundle", 68, 57, 3, **S)
    P("bs_barrel_cluster", 76, 45, 3, **S)
    P("bs_crate_stack", 84, 54, 4, **S)
    P("bs_lamp_post", 90, 47, 5, **S)
    P("bs_rope_coil", 94, 52, 2, near_ok=True, **S)
    # What came aboard with the boarders.
    P("bs_bloodsail_flag", 64, 40, 6, **S)
    P("bs_weapon_rack", 52, 59, 4, **S)
    P("bs_manacles", 62, 61, 2, near_ok=True, **S)

    # ---- THE SAND BAR. Mooring gear at the water's edge and nothing else made by anybody - see the
    # careening note in the module docstring.
    P("bs_rope_coil", 54, 76, 2, near_ok=True, **S)
    P("bs_lamp_post", 65, 77, 5, **S)
    P("mooring_posts", 68, 82, 3, near_ok=True, **C)
    # ... and the island itself.
    P("mangrove_thicket", 53, 81, 5, **C)
    P("coral_reef_outcrop", 74, 81, 3, near_ok=True, **C)
    P("sea_stack_spire", 53, 74, 7, **C)
    return zone, L


def finish(zone, L):
    targets = [P_RATCHET, P_BOOTY, P_RAIDER, P_ANCHORAGE]
    return L.finish(targets)


def generate_the_crossing():
    zone, L, _stations = build_the_crossing()
    dress(zone, L)
    finish(zone, L)
    return zone
