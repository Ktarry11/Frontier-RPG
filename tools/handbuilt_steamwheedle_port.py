"""
Hand-built Steamwheedle Port (120x92): the main town of Tanaris. Standalone zone.

Kyle: "To the east will be steamwheedle which is the main town here", and - about Gadgetzan - "walls
and destroyed buildings with the goblins moved to steamwheedle."

THE TOWN THAT WON, AND IT IS THE SAME PEOPLE.

That second half is the whole design. This is not a rival city that outlasted Gadgetzan; it is where
everybody from Gadgetzan went. Half this town has been here four generations and half of it arrived
three years ago with what it could carry, and the difference between those two halves is the only
social fact the place has. The old harbour families run the quay. The Gadgetzan crowd run the upper
yard, because the upper yard is where there was room.

So the layout is TWO TOWNS THAT HAVE GROWN INTO EACH OTHER:

  THE QUAY, west and on the water - stone, old, built for ships. The harbourmaster, the shipwright,
  the inn, the bank. Everything here predates the Integration and looks it.
  THE UPPER YARD, east and inland - sheds, scaffolding, a smell of hot metal. Gadgetzan's trade,
  rebuilt in a hurry on ground that was a goat field. It is uglier and it is where the money is now,
  and both halves know it.

THE WIND RIDER IS THE POINT OF CONTRAST WITH SALTWHEEL. Kyle gave Saltwheel an inn and no bird, and
that absence says how far out it is. This town has both, and it is the nearest flight point to that
pan - so the Saltwheel goblins' complaint about having to walk is a complaint about THIS post,
sitting a day east with a bird on it that will not come to them.

HARD CONTRACT (world/portal_manager.py): Steamwheedle Port (40, 58) <-> Northern Tanaris (216, 56).
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked  # noqa: F401

BAKED = "assets/tiles/steamwheedle_port/baked"
BLD = "assets/buildings/"
SFP = "assets/tiles/shimmering_flats/props/"
SNP = "assets/tiles/southern_needles/props/"

W, H = 120, 92
BAKED_DIR = BAKED
PORTAL = (40, 58)

#: THE WATER. The whole north edge is sea and the town faces it. A port with the water at the side
#: would be a town with a lake; the quay has to be the town's front.
SEA = dict(y1=22)

#: The town's ground: the strip between the water and the desert, chamfered at the inland corners.
TOWN = dict(x0=8, y0=20, x1=112, y1=80, chamfer=12)

#: THE QUAY AND THE UPPER YARD. Two rectangles that overlap by a few tiles, which is the point -
#: nobody drew a line, the two halves just met somewhere around x=56 and stopped.
QUAY = dict(x0=10, y0=22, x1=60, y1=62)
YARD = dict(x0=52, y0=30, x1=110, y1=78)

NPC_POSITIONS = {
    "stw_gem_trader": (71, 45),          # gem seller (tools/build_gem_sellers.py)
    # ===== THE QUAY - old harbour families, stone buildings, four generations =====
    "stw_harbourmaster": (24, 30),
    "stw_innkeeper": (34, 36),
    "stw_barkeep": (38, 36),
    "stw_shipwright": (18, 34),
    "stw_banker": (44, 32),
    # Back on the waterfront now the warehouse has moved inland. The first attempt put him here
    # when it was walkable but UNREACHABLE - sealed behind that warehouse - which is the whole
    # lesson: walkable is not the property that matters, reachable is, and a free-tile search that
    # only checks the first one finds exactly the tiles you cannot use.
    "stw_fishmonger": (13, 26),
    "stw_chandler": (28, 42),
    # Right on the waterfront, clear of the counting house's footprint - the first two spots I
    # picked for these two were inside building cores, which L.finish() caught as unreachable.
    "stw_flight_master": (41, 26),

    # ===== THE UPPER YARD - Gadgetzan, rebuilt in a hurry on a goat field =====
    "stw_yard_boss": (66, 46),
    "stw_smith": (74, 44),
    "stw_engineer": (82, 48),
    "stw_reagents": (90, 44),
    "stw_general_goods": (70, 58),
    "stw_salvage_broker": (80, 60),
    "stw_caravan_agent": (96, 56),

    # ===== BETWEEN THE TWO, which is where the arguments happen =====
    "stw_tally_clerk": (56, 50),
    "stw_doctor": (58, 66),
    "stw_old_gadgetzan": (62, 70),
}

#: (sprite, cx, base_y, height). Booty Bay's goblin harbour set on the quay; workshops up the yard.
BUILDINGS = [
    # the quay
    ("bb_harbourmaster_tower", 24, 28, 18),
    ("bb_harbour_inn", 35, 34, 15),
    ("bb_counting_house", 49, 32, 13),
    # INLAND, not against the water. At base_y 32 its core reached from y20 to y32 and sealed the
    # western waterfront strip against the sea - a 44-tile pocket you could see and never stand in.
    # A building on a quay has to leave the quay walkable in front of it.
    ("bb_warehouse", 15, 44, 12),
    ("bb_trade_shop", 29, 40, 11),
    ("bb_lean_shack", 25, 50, 7),      # out from under the warehouse
    # the upper yard - newer, scrappier, and a scrapyard workshop is exactly right for it
    ("scrapyard_workshop", 56, 44, 13),
    ("gg_forge", 75, 42, 12),
    ("ratchet_docks_warehouse", 90, 42, 12),
    ("generic_shack_a", 71, 56, 9),
    ("generic_shack_b", 81, 58, 9),
    ("supply_depot", 97, 54, 11),
]


def build_steamwheedle():
    zone = Tilemap("Steamwheedle Port", W, H,
                   "The port that got Gadgetzan's people. Old harbour families on the quay, the "
                   "Gadgetzan crowd up the yard, and the only wind rider for a very long way.")
    zone.is_cave = False
    zone.region = "Kalimdor - Tanaris"
    zone.fixed_spawns = True
    zone.is_town = True

    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b
    b.wall_id = "rock"
    b.floor_id = "sand"
    for y in range(H):
        for x in range(W):
            zone.collision_layer[y][x] = "rock"
            zone.set_tile(x, y, "rock", "base")

    b.rect(TOWN["x0"], TOWN["y0"], TOWN["x1"], TOWN["y1"], chamfer=TOWN["chamfer"], base="sand")
    # the quay itself and the yard's hardstanding are the only paved ground
    b.rect(QUAY["x0"], QUAY["y0"], QUAY["x1"], QUAY["y1"], base="path")
    b.rect(YARD["x0"] + 6, YARD["y0"] + 8, YARD["x1"] - 6, YARD["y1"] - 10, base="path")
    # the road in from the desert, on the south edge
    b.corridor([(PORTAL[0], 86), (PORTAL[0], 74), (52, 62)], width=3, base="path")

    # THE SEA, along the whole north edge. deep_water is not walkable, which is what makes it an
    # edge rather than a decoration.
    for y in range(0, SEA["y1"]):
        for x in range(W):
            zone.collision_layer[y][x] = "water"
            zone.set_tile(x, y, "deep_water", "base")
    for x in range(W):
        zone.set_tile(x, SEA["y1"], "shallow_water", "base")
        zone.collision_layer[SEA["y1"]][x] = "water"

    import numpy as np
    zone._stw_ground = np.array([[zone.is_walkable(x, y) for x in range(W)] for y in range(H)])

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.set_tile(px, py, "path", "base")
    L.mark("portal", px, py)

    for npc_id, (x, y) in NPC_POSITIONS.items():
        if not zone.is_walkable(x, y):
            raise AssertionError(f"{zone.name}: {npc_id} at ({x},{y}) is not on walkable ground")
        zone.set_tile(x, y, "npc", "interaction")

    zone.add_subzone("Steamwheedle Port", 0, 0, W, H)
    zone.add_subzone("The Quay", QUAY["x0"], QUAY["y0"],
                     QUAY["x1"] - QUAY["x0"], QUAY["y1"] - QUAY["y0"])
    zone.add_subzone("The Upper Yard", YARD["x0"], YARD["y0"],
                     YARD["x1"] - YARD["x0"], YARD["y1"] - YARD["y0"])
    return zone, L


def dress(zone, L):
    P = L.prop
    F = dict(where=SFP)
    N = dict(where=SNP)
    for (sprite, cx, by, ht) in BUILDINGS:
        L.b.prop(f"{BLD}{sprite}.png", cx, by, ht, solid="core")
        L.placed += 1
    # the quay: everything a working harbour has on it
    P("sw_dock_crane", 20, 24, 9, near_ok=True, **F)
    P("sw_cargo_winch", 40, 24, 6, near_ok=True, **F)
    P("sw_bollard", 16, 23, 2, near_ok=True, **F)
    P("sw_bollard", 32, 23, 2, near_ok=True, **F)
    P("sw_bollard", 48, 23, 2, near_ok=True, **F)
    P("sw_fish_crates", 12, 26, 3, **F)
    P("sw_nets", 26, 25, 3, **F)
    P("sw_harbour_lamp", 30, 28, 5, **F)
    P("sw_harbour_lamp", 50, 28, 5, **F)
    # the upper yard: hot metal and salvage
    P("sf_fuel_drums", 78, 52, 4, **F)
    P("sf_scrap_heap", 86, 56, 4, **F)
    P("sf_crate_stack", 94, 62, 4, **F)
    P("sf_wheel_stack", 72, 64, 4, **F)
    P("sf_condenser", 100, 46, 6, **F)
    P("sf_hand_winch", 88, 66, 4, **F)
    # the desert edge, where the yard runs out
    P("tan_thorn_scrub", 104, 70, 3, **F)
    P("tan_dead_palm", 22, 70, 5, **F)
    P("tan_dune_grass", 64, 76, 3, **F)
    P("sn_rib_bones", 108, 60, 3, near_ok=True, **N)
    return zone, L


def verify(zone):
    """The two halves have to be real, and the quay has to be on the water."""
    import numpy as np
    ground = getattr(zone, "_stw_ground", None)
    assert ground is not None, "verify needs the ground mask from build_steamwheedle()"
    quay = [p for p in NPC_POSITIONS.values() if p[0] < 52]
    yard = [p for p in NPC_POSITIONS.values() if p[0] > 60]
    assert len(quay) >= 7 and len(yard) >= 6, \
        f"the two halves are lopsided: {len(quay)} on the quay, {len(yard)} up the yard"
    # the quay must actually touch the water, or it is a square with a view
    touching = sum(1 for x in range(QUAY["x0"], QUAY["x1"])
                   if zone.is_walkable(x, SEA["y1"] + 1))
    assert touching > 30, f"only {touching} tiles of quay front onto the sea"
    return dict(quay=len(quay), yard=len(yard), quay_front=touching,
                walkable=int(np.asarray(ground).sum()))


def finish(zone, L):
    return L.finish([PORTAL] + list(NPC_POSITIONS.values()))


def build_steamwheedle_baked():
    zone, L = build_steamwheedle()
    dress(zone, L)
    finish(zone, L)
    return zone, L


def generate_steamwheedle_port():
    zone, L = build_steamwheedle_baked()
    # THE PAINTED GROUND, WHICH WAS BAKED AND NEVER ATTACHED. Found 13 Nov 2026: this zone drew in
    # the fallback tiles - plain dirt and a grey grid for rock - while a full set of baked chunks
    # sat in its folder. It is what Kyle's backlog called "has no tiles".
    register_baked(zone, BAKED)
    return zone
