"""
Hand-built Fourth Peg (96x72): the survey town on the northeast flat of the Abyssal Sands. Standalone zone.

Kyle, 16 Nov 2026: "Lets make Fourth Peg an ACTUAL town. i feel that'd solve a lot of whats ugly in Abyssal Sands."
It was eight goblins and two tents standing on the open sand, which is how the zone's one safe place came to be a
patch of the zone with a "safe" flag on it. Now it's a map of its own, the way every town is.

THE STAKE HELD, SO THEY BUILT ROUND IT. The fourth survey peg has stood longer than anything else on the Sands, so
the camp stopped being a camp. Steamwheedle's money (Rullo's) finally paid for the things a camp does without:
walls, an inn with real beds, a forge under a roof, and a wyvern, so the next crew doesn't walk in from the port.
It is still the same eight people and their job is still the same: find out whether a road across the Sands is
possible. They're just doing it from somewhere that won't blow away.

    the south gate ..... (48, 69): the way in off the sands, and the only way
    Peg Street ......... north from the gate to the square
    the square ......... the fourth peg itself, the surveyor's tripod and the chief surveyor
    the west side ...... the Fourth Stake inn (Marda's pot, and real beds now), the teamsters' yard and carts
    the east side ...... the forge, the quartermaster's depot, the brewer's shed, Vizzi's winch yard
    the north rise ..... the survey office, the instrument shed, and the wyvern roost on the high ground

The flight point is new, and it is the point: the sync used to assert there would never be one ("it is a ten-person
camp on a rock and it does not get a wyvern"). It's a town now, and Kyle asked for one inn and one flight point.

HARD CONTRACT (world/portal_manager.py): Fourth Peg (48, 70) <-> The Abyssal Sands (140, 24).
NPC ids ab_*, written by tools/sync_abyssal_npcs.py from NPC_POSITIONS.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked  # noqa: F401
from tools.tint_goblin_buildings import path_for as tint_path

BAKED = "assets/tiles/fourth_peg/baked"
BLD = "assets/buildings/"
SFP = "assets/tiles/shimmering_flats/props/"
SNP = "assets/tiles/southern_needles/props/"
UDP = "assets/tiles/underdark/props/"
EKP = "assets/tiles/eastern_kingdoms/props/"

NAME = "Fourth Peg"
W, H = 96, 72
BAKED_DIR = BAKED
#: the south gate: the way in off the Abyssal Sands
PORTAL = (48, 70)

#: the town's ground, a walled flat with its corners cut
TOWN = dict(x0=6, y0=6, x1=90, y1=67, chamfer=9)
#: Peg Street, gate to square, and the cross street through the square
STREET = dict(x0=46, y0=40, x1=50, y1=70)
CROSS = dict(x0=10, y0=37, x1=86, y1=41)
SQUARE = dict(x0=38, y0=29, x1=58, y1=44)
#: the lanes off the cross street, up to the north rise and down to the yards
LANES = [((24, 37), (24, 22)), ((70, 37), (70, 22)), ((48, 29), (48, 14)), ((24, 41), (24, 58)),
         ((70, 41), (70, 60)), ((48, 14), (76, 14))]

NPC_POSITIONS = {
    # ---- the square: the peg and the woman who drove it
    "ab_surveyor":      (52, 33),
    # ---- the west side: the inn and the carts
    "ab_cook":          (24, 33),      # Marda Pell, at the Fourth Stake's door: the town's inn
    "ab_teamster":      (18, 52),
    # ---- the east side: the forge, the depot, the brewer, the winch yard
    "ab_smith":         (66, 33),
    "ab_quartermaster": (76, 46),
    "ab_reagents":      (64, 52),
    "ab_digger":        (82, 34),
    # ---- the north rise: the office, the instruments, the wyvern
    "ab_rodman":        (36, 18),
    "ab_flight_master": (72, 18),
    # ---- the gate
    "ab_gate_warden":   (44, 64),
}

#: (sprite, cx, base_y, height): the goblin set tinted for Tanaris (the same tint as Steamwheedle Port, where
#: the money comes from), and a few Barrens and plain buildings for what the survey put up itself
G = lambda sprite: tint_path("steamwheedle_port", sprite)      # noqa: E731
BUILDINGS = [
    # ---- the west side
    (G("gob_inn"), 24, 30, 12),
    ("crossroads_stable", 17, 49, 9),
    (G("gob_house_medium"), 33, 58, 8),
    # ---- the east side
    ("gg_forge", 66, 30, 9),
    ("supply_depot", 77, 43, 9),
    (G("gob_alchemy_lab"), 64, 49, 9),
    # ---- the north rise
    (G("gob_post_office"), 48, 11, 10),        # the survey office
    (G("gob_house_small"), 35, 15, 7),          # Hask's instrument shed
    ("orc_wyvern_roost", 76, 13, 11),
    (G("gob_water_tower"), 14, 20, 11),
    # ---- the gate
    (G("gob_town_gate"), 48, 66, 9),
]


def build_fourth_peg():
    zone = Tilemap(NAME, W, H,
                   "The survey town on the Abyssal Sands, built round the one stake that held. Walls, an inn with "
                   "real beds, a forge under a roof, and the only wyvern on the Sands.")
    zone.is_cave = False
    zone.region = "Kalimdor - Tanaris"
    zone.fixed_spawns = True
    zone.is_town = True

    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 3))
    b = L.b
    b.wall_id = "rock"
    b.floor_id = "sand"
    for y in range(H):
        for x in range(W):
            zone.collision_layer[y][x] = "rock"
            zone.set_tile(x, y, "rock", "base")

    b.rect(TOWN["x0"], TOWN["y0"], TOWN["x1"], TOWN["y1"], chamfer=TOWN["chamfer"], base="sand")
    b.rect(STREET["x0"], STREET["y0"], STREET["x1"], STREET["y1"], base="path")
    b.rect(CROSS["x0"], CROSS["y0"], CROSS["x1"], CROSS["y1"], base="path")
    b.rect(SQUARE["x0"], SQUARE["y0"], SQUARE["x1"], SQUARE["y1"], base="path")
    for (p, q) in LANES:
        b.corridor([p, q], width=3, base="path")

    import numpy as np
    zone._fp_ground = np.array([[zone.is_walkable(x, y) for x in range(W)] for y in range(H)])

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.set_tile(px, py, "path", "base")
    L.mark("portal", px, py)

    for npc_id, (x, y) in NPC_POSITIONS.items():
        if not zone.is_walkable(x, y):
            raise AssertionError(f"{zone.name}: {npc_id} at ({x},{y}) is not on walkable ground")
        zone.set_tile(x, y, "npc", "interaction")

    zone.add_subzone(NAME, 0, 0, W, H)
    zone.add_subzone("The Square", SQUARE["x0"], SQUARE["y0"], SQUARE["x1"] - SQUARE["x0"],
                     SQUARE["y1"] - SQUARE["y0"])
    zone.add_subzone("The North Rise", 28, 4, 56, 22)
    return zone, L


def dress(zone, L):
    P = L.prop
    F = dict(where=SFP)
    N = dict(where=SNP)
    U = dict(where=UDP)
    E = dict(where=EKP)
    for (sprite, cx, by, ht) in BUILDINGS:
        if not P(sprite, cx, by, ht, solid="core", where=BLD, near_ok=True):
            raise AssertionError(f"{zone.name}: {sprite} at ({cx},{by}) refused: {L.skipped[-1]}")
    # ---- THE PEG ITSELF, in the middle of the square, with the tripod still on it
    P("sn_anchor_post", 48, 35, 3, near_ok=True, **N)
    P("ud_survey_tripod", 45, 33, 4, near_ok=True, **U)
    P("sf_signboard", 55, 41, 4, near_ok=True, **F)
    # the first three pegs' story, on the board by the gate
    P("sf_signboard", 52, 63, 4, near_ok=True, **F)
    # ---- the inn yard and the carts
    P("sn_cook_fire", 30, 34, 2, near_ok=True, **N)
    P("ek_farm_cart", 12, 56, 4, near_ok=True, **E)
    P("ek_farm_cart", 25, 60, 4, near_ok=True, **E)
    P("sf_crate_stack", 12, 44, 3, near_ok=True, **F)
    P("sf_wheel_stack", 28, 49, 3, near_ok=True, **F)
    # ---- the forge and the depot
    P("sf_fuel_drums", 72, 33, 4, near_ok=True, **F)
    P("sf_crate_stack", 82, 49, 3, near_ok=True, **F)
    P("sf_crate_stack", 70, 55, 3, near_ok=True, **F)
    # ---- Vizzi's winch yard: the ropes she's lowered into every hole on the Sands
    P("sf_hand_winch", 85, 31, 3, near_ok=True, **F)
    P("sn_rope_coil", 79, 30, 2, near_ok=True, **N)
    P("sn_pulley_hoist", 86, 42, 5, near_ok=True, **N)
    # ---- the north rise: the instruments, and the old camp's tents kept as a bunkhouse
    P("ud_codex_tent", 58, 20, 5, near_ok=True, **U)
    P("ud_codex_tent", 22, 12, 5, near_ok=True, **U)
    P("sf_condenser", 84, 22, 6, near_ok=True, **F)
    # ---- lamps down Peg Street and round the square
    for (x, y) in [(44, 46), (52, 46), (44, 56), (52, 56), (37, 36), (59, 36), (16, 36), (80, 36)]:
        P("sf_lamp_post", x, y, 5, near_ok=True, **F)
    # ---- the desert getting in at the edges
    P("tan_dead_palm", 10, 30, 5, near_ok=True, **F)
    P("tan_dead_palm", 86, 58, 5, near_ok=True, **F)
    P("tan_thorn_scrub", 58, 62, 3, near_ok=True, **F)
    P("tan_dune_grass", 36, 64, 3, near_ok=True, **F)
    P("tan_dune_grass", 76, 64, 3, near_ok=True, **F)
    P("sn_rib_bones", 88, 26, 3, near_ok=True, **N)
    return zone, L


def finish(zone, L):
    return L.finish([PORTAL] + list(NPC_POSITIONS.values()))


def verify(zone):
    """A town, not a camp: every service a town has, inside walls, and one way in."""
    ground = getattr(zone, "_fp_ground", None)
    assert ground is not None, "verify needs the ground mask from build_fourth_peg()"
    for x in range(W):
        assert not zone.is_walkable(x, 0) and not zone.is_walkable(x, H - 1) or (x, H - 1) == PORTAL, \
            f"the town's edge is open at column {x}"
    return dict(walkable=int(ground.sum()), people=len(NPC_POSITIONS))


def build_fourth_peg_baked():
    zone, L = build_fourth_peg()
    dress(zone, L)
    finish(zone, L)
    return zone, L


def generate_fourth_peg():
    zone, L = build_fourth_peg_baked()
    register_baked(zone, BAKED)
    return zone


if __name__ == "__main__":
    import sys
    z, L = build_fourth_peg_baked()
    print(verify(z), "props", L.placed, "skipped", L.skipped)
    if "--preview" in sys.argv:
        from PIL import Image
        im = Image.new("RGB", (W * 6, H * 6))
        px = im.load()
        for y in range(H):
            for x in range(W):
                c = (210, 180, 110) if z.is_walkable(x, y) else (90, 70, 50)
                if z.base_layer[y][x] == "path":
                    c = (170, 150, 120)
                for dy in range(6):
                    for dx in range(6):
                        px[x * 6 + dx, y * 6 + dy] = c
        for (x, y) in NPC_POSITIONS.values():
            for dy in range(6):
                for dx in range(6):
                    px[x * 6 + dx, y * 6 + dy] = (220, 40, 40)
        im.save(sys.argv[sys.argv.index("--preview") + 1])
