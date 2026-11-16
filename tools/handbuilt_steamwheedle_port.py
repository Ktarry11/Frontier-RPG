"""
Hand-built Steamwheedle Port (120x92): the main town of Tanaris. Standalone zone.

Kyle: "To the east will be steamwheedle which is the main town here", and - about Gadgetzan - "walls
and destroyed buildings with the goblins moved to steamwheedle." Then, 16 Nov 2026: "Can we redesign
steamwheedle....it's very ugly and needs water in the east".

THE TOWN THAT WON, AND IT IS THE SAME PEOPLE. This is not a rival city that outlasted Gadgetzan; it
is where everybody from Gadgetzan went. Half this town has been here four generations and half of it
arrived three years ago with what it could carry, and the difference between those two halves is the
only social fact the place has.

THE REDESIGN (16 Nov 2026). The first build put the sea along the north edge and the ground bake never
painted it (the spec had no tile_water), so the port drew as one flat slab of sand with buildings on
it and no water anywhere. It is turned to face east now, the way the desert road runs:

  THE WEST GATE, where the road comes in off the dunes from Northern Tanaris.
  THE UPPER YARD, west and inland - Gadgetzan's trade rebuilt in a hurry on a goat field: the forge,
    the scrapyard, salvage and sheds, unpaved. Uglier, and where the money is now.
  GADGET ROW, the one street, straight from the gate to the water. Everything happens on it.
  THE QUAY, east, paved and old, built for ships: the harbourmaster's tower, the inn, the bank, the
    fish market, the dock office, the shipwright. Three piers run out into the sea from it.
  THE SEA, the whole east side. Deep water past the piers, a shallow lip along the stones.

THE WIND RIDER IS THE POINT OF CONTRAST WITH SALTWHEEL. Saltwheel has an inn and no bird. This town has
both, and it is the nearest flight point to that pan.

HARD CONTRACT (world/portal_manager.py): Steamwheedle Port (5, 47) <-> Northern Tanaris (216, 56).
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked  # noqa: F401
from tools.tint_goblin_buildings import path_for as tint_path

BAKED = "assets/tiles/steamwheedle_port/baked"
BLD = "assets/buildings/"
SFP = "assets/tiles/shimmering_flats/props/"
SNP = "assets/tiles/southern_needles/props/"
BOATS = "assets/tiles/coastal_props/"

W, H = 120, 92
BAKED_DIR = BAKED
#: the west gate: the desert road comes in here from Northern Tanaris
PORTAL = (5, 47)


def coast(y):
    """The shoreline's x at row y: everything east of it is sea. It wanders a little so it reads as a
    coast and not a ruler line."""
    return int(round(89 + 2.4 * math.sin(y * 0.19) + 1.3 * math.sin(y * 0.47 + 1.0)))


#: The town's ground: a pan from the gate to the water, chamfered at the inland corners.
TOWN = dict(x0=7, y0=12, x1=100, y1=82, chamfer=11)
#: Gadget Row, gate to quay, and the paved quay itself
ROW = dict(y0=45, y1=49)
QUAY = dict(x0=74, y0=14, x1=100, y1=80)
#: the market square halfway down the Row, where the two towns meet
SQUARE = dict(x0=40, y0=41, x1=56, y1=55)
#: the yard's hardstanding and the old-town lanes off the Row
LANES = [((46, 18), (46, 41)), ((48, 55), (48, 78)), ((24, 49), (24, 72)), ((24, 45), (24, 22))]
#: three piers out into the sea: (row of the pier's top edge, how far east it runs)
PIERS = [(22, 110), (46, 113), (70, 109)]
PIER_W = 3
#: what the subzones and verify() call the two halves
YARD = dict(x0=8, y0=14, x1=56, y1=80)

NPC_POSITIONS = {
    "stw_enchanter": (31, 52),          # enchanter (tools/build_enchanters.py, 14 Nov 2026)
    "stw_gem_trader": (28, 52),          # gem seller (tools/build_gem_sellers.py)
    # ===== THE QUAY - old harbour families, stone buildings, four generations =====
    "stw_harbourmaster": (82, 26),
    "stw_innkeeper": (62, 44),
    "stw_barkeep": (68, 44),
    "stw_shipwright": (85, 69),
    "stw_banker": (64, 63),
    "stw_fishmonger": (70, 32),
    "stw_chandler": (79, 58),
    "stw_flight_master": (86, 37),       # the bird stands on the stones by the north pier, out of the yard's smoke

    # ===== THE UPPER YARD - Gadgetzan, rebuilt in a hurry on a goat field =====
    "stw_yard_boss": (34, 44),
    "stw_smith": (21, 44),
    "stw_engineer": (33, 64),
    "stw_reagents": (52, 68),
    "stw_general_goods": (16, 64),
    "stw_salvage_broker": (28, 77),
    "stw_caravan_agent": (11, 51),       # by the gate: the caravans go out the way you came in

    # ===== BETWEEN THE TWO, on the square, which is where the arguments happen =====
    "stw_tally_clerk": (52, 51),
    "stw_doctor": (44, 58),
    "stw_old_gadgetzan": (38, 74),
}

#: (sprite, cx, base_y, height). The goblin town sheet, tinted for Tanaris, plus Booty Bay's harbour set
#: for the old quay, which is older than any of it.
G = lambda sprite: tint_path("steamwheedle_port", sprite)      # the goblin set, lightly tinted for this port
BUILDINGS = [
    # ---- THE QUAY: old stone, facing the water, leaving the stones in front of it open
    ("bb_harbourmaster_tower", 80, 23, 14),
    (G("gob_fish_market"), 66, 30, 10),
    ("bb_harbour_inn", 65, 42, 14),
    ("bb_counting_house", 64, 61, 10),
    (G("gob_dock_office"), 79, 56, 9),
    (G("gob_shipwright"), 79, 68, 10),
    (G("gob_lighthouse"), 84, 81, 13),
    (G("gob_customs_house"), 64, 78, 10),
    # ---- THE SQUARE: where both halves come to shout at each other
    (G("gob_auction_house"), 50, 40, 11),
    (G("gob_emporium"), 57, 30, 9),
    # ---- THE UPPER YARD: hot metal and salvage, unpaved
    ("gg_forge", 22, 41, 9),
    (G("gob_engineering_workshop"), 35, 39, 10),
    ("scrapyard_workshop", 33, 61, 11),
    ("supply_depot", 15, 61, 10),
    (G("gob_salvage_yard"), 22, 75, 9),
    (G("gob_water_tower"), 13, 30, 12),
    ("bb_warehouse", 31, 27, 9),
    (G("gob_shredder_hangar"), 41, 70, 10),
    (G("gob_fireworks_shop"), 55, 66, 9),
    (G("gob_boarding_house"), 56, 77, 10),
    (G("gob_stacked_houses"), 39, 22, 10),
    (G("gob_house_medium"), 18, 22, 7),
]


def _sea(zone):
    """East of the coast is sea: a shallow lip two tiles wide, then deep water. Neither is walkable,
    which is what makes the coast an edge and not a decoration."""
    for y in range(H):
        cx = coast(y)
        for x in range(cx, W):
            deep = x >= cx + 2
            zone.set_tile(x, y, "deep_water" if deep else "shallow_water", "base")
            zone.collision_layer[y][x] = "water"


def _piers(zone):
    """Planked piers on posts, out over the water from the quay."""
    for (py, x_end) in PIERS:
        for y in range(py, py + PIER_W):
            for x in range(coast(y) - 2, x_end + 1):
                zone.collision_layer[y][x] = None
                zone.set_tile(x, y, "path", "base")
        # a landing at the head, where the boats tie up
        for y in range(py - 1, py + PIER_W + 1):
            for x in range(x_end - 3, x_end + 1):
                zone.collision_layer[y][x] = None
                zone.set_tile(x, y, "path", "base")


def build_steamwheedle():
    zone = Tilemap("Steamwheedle Port", W, H,
                   "The port that got Gadgetzan's people. Old harbour families on the quay, the "
                   "Gadgetzan crowd up the yard, and the only wind rider for a very long way.")
    zone.is_cave = False
    zone.region = "Kalimdor - Tanaris"
    zone.fixed_spawns = True
    zone.is_town = True

    L = CaveLayout(zone, (PORTAL[0] + 3, PORTAL[1]))
    b = L.b
    b.wall_id = "rock"
    b.floor_id = "sand"
    for y in range(H):
        for x in range(W):
            zone.collision_layer[y][x] = "rock"
            zone.set_tile(x, y, "rock", "base")

    b.rect(TOWN["x0"], TOWN["y0"], TOWN["x1"], TOWN["y1"], chamfer=TOWN["chamfer"], base="sand")
    # Gadget Row, gate to water, and the gate road out to the portal
    b.rect(2, ROW["y0"], TOWN["x0"] + 2, ROW["y1"], base="path")      # wide enough that you land on road, two up from the door
    b.rect(TOWN["x0"], ROW["y0"], QUAY["x0"], ROW["y1"], base="path")
    b.rect(QUAY["x0"], QUAY["y0"], QUAY["x1"], QUAY["y1"], base="path")
    b.rect(SQUARE["x0"], SQUARE["y0"], SQUARE["x1"], SQUARE["y1"], base="path")
    for (p, q) in LANES:
        b.corridor([p, q], width=3, base="path")

    _sea(zone)
    _piers(zone)

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
    zone.add_subzone("The Quay", QUAY["x0"] - 16, QUAY["y0"], W - QUAY["x0"] + 16, QUAY["y1"] - QUAY["y0"])
    zone.add_subzone("The Upper Yard", YARD["x0"], YARD["y0"],
                     YARD["x1"] - YARD["x0"], YARD["y1"] - YARD["y0"])
    return zone, L


def dress(zone, L):
    P = L.prop
    F = dict(where=SFP)
    N = dict(where=SNP)
    for (sprite, cx, by, ht) in BUILDINGS:
        if not P(sprite, cx, by, ht, solid="core", where=BLD, near_ok=True):
            raise AssertionError(f"{zone.name}: {sprite} at ({cx},{by}) refused: {L.skipped[-1]}")
    # ---- the piers: cranes, winches, bollards and lamps, and the boats tied to them
    for (py, x_end) in PIERS:
        P("sw_harbour_lamp", coast(py) + 2, py, 5, near_ok=True, **F)
        P("sw_harbour_lamp", x_end - 1, py, 5, near_ok=True, **F)
        P("sw_bollard", x_end - 3, py + PIER_W - 1, 2, near_ok=True, **F)
        L.b.prop(f"{SFP}sw_bollard.png", (coast(py) + x_end) // 2, py + PIER_W - 1, 2)
    P("sw_dock_crane", 107, 22, 9, near_ok=True, **F)
    P("sw_cargo_winch", 110, 47, 5, near_ok=True, **F)
    P("sw_nets", 104, 71, 3, near_ok=True, **F)
    for (bx, by, bh, art) in [(115, 30, 8, "boat_orc"), (112, 58, 7, "boat_troll"), (114, 78, 6, "boat_troll")]:
        L.b.prop(f"{BOATS}{art}.png", bx, by, bh)          # over water: drawn, never solid
    # ---- the quay stones
    P("sw_fish_crates", 74, 33, 3, near_ok=True, **F)
    P("sw_fish_crates", 84, 62, 3, near_ok=True, **F)
    P("sw_nets", 84, 31, 3, near_ok=True, **F)
    P("sf_crate_stack", 72, 74, 4, near_ok=True, **F)
    for (x, y) in [(76, 18), (76, 40), (76, 52), (76, 72), (59, 44), (40, 44), (20, 50)]:
        P("sw_harbour_lamp", x, y, 5, near_ok=True, **F)
    # ---- the square
    P("sf_signboard", 44, 51, 4, near_ok=True, **F)
    P("sf_lamp_post", 41, 55, 5, near_ok=True, **F)
    P("sf_lamp_post", 55, 55, 5, near_ok=True, **F)
    # ---- the upper yard: hot metal and salvage
    P("sf_fuel_drums", 28, 42, 4, near_ok=True, **F)
    P("sf_scrap_heap", 27, 67, 4, near_ok=True, **F)
    P("sf_wheel_stack", 38, 64, 4, near_ok=True, **F)
    P("sf_crate_stack", 20, 66, 4, near_ok=True, **F)
    P("sf_condenser", 10, 38, 6, near_ok=True, **F)
    P("sf_hand_winch", 30, 74, 4, near_ok=True, **F)
    P("sf_wrecked_racer", 14, 74, 5, near_ok=True, **F)
    # ---- old Gadgetzan: what Mazzic carried out, and what he could not
    P("tan_ruin_block", 34, 77, 4, near_ok=True, **F)
    P("tan_ruin_block", 43, 78, 3, near_ok=True, **F)
    # ---- the desert getting in at the edges
    P("tan_dead_palm", 12, 42, 5, near_ok=True, **F)
    P("tan_dead_palm", 10, 55, 5, near_ok=True, **F)
    P("tan_thorn_scrub", 60, 16, 3, near_ok=True, **F)
    P("tan_dune_grass", 30, 16, 3, near_ok=True, **F)
    P("tan_dune_grass", 70, 80, 3, near_ok=True, **F)
    P("sn_rib_bones", 9, 70, 3, near_ok=True, **N)
    return zone, L


def verify(zone):
    """The two halves have to be real, the sea has to be east, and the quay has to be on it."""
    import numpy as np
    ground = getattr(zone, "_stw_ground", None)
    assert ground is not None, "verify needs the ground mask from build_steamwheedle()"
    quay = [p for p in NPC_POSITIONS.values() if p[0] >= 58]
    yard = [p for p in NPC_POSITIONS.values() if p[0] < 40]
    assert len(quay) >= 7 and len(yard) >= 6, \
        f"the two halves are lopsided: {len(quay)} on the quay, {len(yard)} up the yard"
    # the sea is the east: every row's last tiles are water, and none of the west is
    for y in range(H):
        assert zone.base_layer[y][W - 1] == "deep_water", f"row {y} does not reach the sea"
    west_water = sum(zone.base_layer[y][x] in ("deep_water", "shallow_water") for y in range(H) for x in range(60))
    assert west_water == 0, f"{west_water} water tiles in the west half"
    # the quay must actually front onto the water, or it is a square with a view
    front = sum(1 for y in range(QUAY["y0"], QUAY["y1"]) if zone.is_walkable(coast(y) - 1, y))
    assert front > 50, f"only {front} rows of quay front onto the sea"
    return dict(quay=len(quay), yard=len(yard), quay_front=front,
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
