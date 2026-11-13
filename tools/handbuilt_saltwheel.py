"""
Hand-built Saltwheel (120x100): the goblin town on the Shimmering Flats. Standalone zone.

Kyle: "We can put a goblin town in there, but we need to change the name to reflect the fucked up
enviornment." And: "We also need the standalone town. This can have an inn but no wind rider."

THE NAME IS THE PITCH. The wheel is the racetrack; the salt is what is eating it. Goblin naming is
mercantile and blunt - Ratchet, Booty Bay, Gadgetzan - and Saltwheel says the environment went wrong
without being a joke about it.

ARCHETYPE: THE TOWN ON THE START LINE.

Saltwheel is not a town that happens to have a racetrack near it. It is the pit lane, and everything
here faces the straight, because when the money was good that is where the money was. The buildings
stand in two rows looking at each other across the start line, which is also the only paved ground on
the pan and therefore the main street whether anybody meant it to be or not.

NO WIND RIDER, AND THE ABSENCE IS THE POINT. Kyle's instruction, and it does more for the place than
another vendor would. You walk out of here. Everywhere else in this game with an inn also has a way to
skip the journey, so a town that only has the first half of that pair says something about how far out
it is and how little anybody with a bird wants to land here - and a player who has walked the pan to
reach it finds out they are walking back. The inn is here precisely because the flight is not.

They have not left. They are not going to, and they will tell you why at length: the track is still
here, the salt is still worth something, and the hives have not actually come as far as the fence yet.
Every one of those is true and none of them is a reason.

SALT-WASHED, NOT REBUILT. Kyle: "We have goblin structures and what we can do is color tint them to
make them look salt washed." tools/asset_pipeline/salt_wash.py makes the sw_* set from the Booty Bay
goblin buildings - chroma gone, everything lifted toward the colour of the ground, and a rime gradient
up the bottom of every wall, which is the part that says where the building is standing.

HARD CONTRACT (world/portal_manager.py): Saltwheel (16, 50) <-> The Shimmering Flats (104, 56), which
is where the Raceway spur road meets the ring.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked  # noqa: F401

BAKED = "assets/tiles/saltwheel/baked"
BLD = "assets/buildings/"
SFP = "assets/tiles/shimmering_flats/props/"
SNP = "assets/tiles/southern_needles/props/"

W, H = 120, 100
BAKED_DIR = BAKED
PORTAL = (16, 50)

#: the town's ground: a chamfered rect of trodden pan, with the rim rock outside it
#: Widened from (8,24)-(114,78) after the first bake measured the off-town rim at 51% of the map -
#: more than half the picture being a frame nobody stands on. Growing the pan rather than shrinking
#: the map keeps every building and every NPC exactly where they are, and it gives the salt-creep
#: gradient the room it needs: the rime has to come in from somewhere, and at the old size it started
#: four tiles behind the back doors.
TOWN = dict(x0=6, y0=16, x1=116, y1=88, chamfer=12)

#: THE STRAIGHT. The start line, running the length of the town - paved, because it is the only
#: surface anybody out here ever bothered to lay, and the main street by default.
STRAIGHT = dict(y0=44, y1=56, x0=10, x1=112)

#: Where the people stand. The layout is the only place a position is decided -
#: tools/saltwheel_npc_roster.py says who they are, and the sync asserts the two agree.
NPC_POSITIONS = {
    # ===== THE TRADE ROW - the north side, facing the straight =====
    "sw_innkeeper": (34, 38),
    "sw_barkeep": (40, 38),
    "sw_general_goods": (52, 38),
    "sw_reagents": (60, 38),
    "sw_salt_buyer": (74, 38),
    "sw_road_agent": (80, 38),
    "sw_quartermaster": (92, 38),

    # ===== THE PIT ROW - the south side, which is what the town was for =====
    "sw_race_marshal": (29, 61),
    "sw_pit_boss": (44, 61),
    "sw_mechanic": (53, 62),
    "sw_salvager": (64, 62),
    "sw_fuel_trader": (72, 62),
    "sw_repair": (84, 62),

    # ===== THE FENCE - where the town stops pretending =====
    "sw_hive_watcher": (102, 50),
    "sw_doctor": (26, 50),
    "sw_tally_clerk": (96, 62),
    "sw_old_racer": (58, 50),
}

#: (sprite, cx, base_y, height). Salt-washed goblin buildings, two rows facing the straight.
BUILDINGS = [
    ("sw_inn", 36, 36, 16),
    ("sw_trade_shop", 56, 36, 12),
    ("sw_counting_house", 77, 36, 13),
    ("sw_warehouse", 94, 36, 12),
    ("sw_workshop", 48, 70, 13),
    ("sw_shack", 30, 68, 9),
    ("sw_shack_a", 66, 69, 9),
    ("sw_shack_b", 86, 69, 9),
]


def _box(gx, gy, x0, y0, x1, y1):
    """Signed tiles-from-the-edge of an axis-aligned box: positive inside, negative outside."""
    import numpy as np
    return np.minimum(np.minimum(gx - x0, x1 - gx), np.minimum(gy - y0, y1 - gy))


def town_field(gx, gy):
    """The chamfered pan the town stands on. Positive inside.

    THIS IS A SECOND DESCRIPTION OF GEOMETRY THAT ALREADY EXISTS, which is a thing worth being nervous
    about: the Builder carves the ground and this function tells the baker where the ground is, and if
    the two ever disagree the paint slides off the town by a tile or two and nothing anywhere throws.
    So verify_fields() below holds them against each other rather than trusting that they match.
    """
    import numpy as np
    T = TOWN
    rect = _box(gx, gy, T["x0"], T["y0"], T["x1"], T["y1"])
    # the 45-degree corner cuts: distance to the chamfer line, in the same units
    dx = np.minimum(gx - T["x0"], T["x1"] - gx)
    dy = np.minimum(gy - T["y0"], T["y1"] - gy)
    cham = (dx + dy - T["chamfer"]) / np.sqrt(2.0)
    d = np.minimum(rect, cham)

    # THE EDGE WOBBLE, WHICH IS THE DIFFERENCE BETWEEN A TOWN AND A STICKER.
    #
    # The first bake of this zone came out as a clean white octagon sitting on a dark pan - a shape,
    # not a place, and no amount of texture inside it was going to fix an outline that straight. A
    # salt pan does not have corners and neither does the ground a town has trodden flat.
    #
    # The wobble only ever eats INWARD (it is subtracted, and the term is non-negative), which is not
    # a stylistic choice: the Builder carved a hard rect, so a field that bulged outward anywhere
    # would be claiming ground the layout never cut, and verify_fields() would fail - correctly. Eating
    # inward leaves a ragged apron of walkable pan just outside the painted town, which is what the
    # outskirts of a place like this actually look like.
    w = (np.sin(gx * 0.085 + 1.7) * np.cos(gy * 0.071 - 0.4)
         + 0.55 * np.sin(gx * 0.21 - 2.2) * np.cos(gy * 0.185 + 1.1)
         + 0.30 * np.sin((gx + gy) * 0.33 + 0.6))
    return d - 5.0 * (0.5 + 0.5 * np.clip(w / 1.85, -1.0, 1.0))


def straight_field(gx, gy):
    """The paved start line, which is also the main street. Positive on the pavement."""
    import numpy as np
    S = STRAIGHT
    run = _box(gx, gy, S["x0"], S["y0"], S["x1"], S["y1"])
    approach = _box(gx, gy, 3, 49, 15, 51)      # the spur in from the Raceway
    return np.maximum(run, approach)


def verify_fields(zone, tol=1):
    """The analytic fields and the carved GROUND must describe the same town.

    A field that has drifted from the layout is invisible at build time and obvious in the picture, and
    only ever in one direction - the paint goes on the wrong tiles.

    THE COMPARISON IS AGAINST THE CARVED GROUND, NOT AGAINST WALKABILITY, and the first run of this
    check is why: it reported 396 stray tiles, every one of them under a building. A building core
    blocks the tile it stands on, so walkability stops being a description of the terrain the moment
    anything is dressed onto it - and the baker paints ground, including the ground beneath a building.
    build_saltwheel() stashes the mask at the instant the Builder finishes, which is the only moment
    the two descriptions are talking about the same thing.

    Both tests are deliberately one-sided: the edge is genuinely fuzzy to within a tile, so what is
    being caught is a field that is wrong by a LOT, not one that is wrong by half.
    """
    import numpy as np
    ground = getattr(zone, "_saltwheel_ground", None)
    if ground is None:
        raise AssertionError("verify_fields needs the ground mask from build_saltwheel()")
    gy, gx = np.mgrid[0:H, 0:W]
    gx = gx.astype(np.float32) + 0.5
    gy = gy.astype(np.float32) + 0.5

    inside = town_field(gx, gy) > tol
    stray = int((inside & ~ground).sum())
    if stray:
        ys, xs = np.nonzero(inside & ~ground)
        raise AssertionError(f"{zone.name}: town_field claims {stray} tiles the layout did not carve, "
                             f"e.g. ({xs[0]},{ys[0]})")

    paved = straight_field(gx, gy) > tol
    off = int((paved & ~ground).sum())
    if off:
        ys, xs = np.nonzero(paved & ~ground)
        raise AssertionError(f"{zone.name}: straight_field paves {off} uncarved tiles, "
                             f"e.g. ({xs[0]},{ys[0]})")
    return int(inside.sum()), int(paved.sum())


def build_saltwheel():
    zone = Tilemap("Saltwheel", W, H,
                   "A goblin town on the start line of a racetrack nobody races any more. The salt "
                   "has been at it for three years and the hives are closer than anyone admits.")
    zone.is_cave = False
    zone.region = "The Shimmering Flats"
    zone.fixed_spawns = True
    zone.is_town = True

    L = CaveLayout(zone, (PORTAL[0] + 2, PORTAL[1]))
    b = L.b
    b.wall_id = "rock"
    b.floor_id = "sand"
    for y in range(H):
        for x in range(W):
            zone.collision_layer[y][x] = "rock"
            zone.set_tile(x, y, "rock", "base")

    # the town's ground: salt pan, with the paved straight down the middle of it
    b.rect(TOWN["x0"], TOWN["y0"], TOWN["x1"], TOWN["y1"], chamfer=TOWN["chamfer"], base="sand")
    b.rect(STRAIGHT["x0"], STRAIGHT["y0"], STRAIGHT["x1"], STRAIGHT["y1"], base="path")
    # the way in, off the Raceway spur
    b.corridor([(4, 50), (14, 50)], width=2, base="path")

    # the ground, as carved, before anything is dressed onto it - see verify_fields()
    import numpy as np
    zone._saltwheel_ground = np.array(
        [[zone.is_walkable(x, y) for x in range(W)] for y in range(H)])

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.set_tile(px, py, "path", "base")
    L.mark("portal", px, py)

    for npc_id, (x, y) in NPC_POSITIONS.items():
        if not zone.is_walkable(x, y):
            raise AssertionError(f"{zone.name}: {npc_id} at ({x},{y}) is not on walkable ground")
        zone.set_tile(x, y, "npc", "interaction")

    zone.add_subzone("Saltwheel", 0, 0, W, H)
    zone.add_subzone("The Straight", 10, 42, 104, 16)
    zone.add_subzone("The Trade Row", 20, 26, 86, 18)
    zone.add_subzone("The Pit Row", 20, 58, 86, 20)
    return zone, L


def dress(zone, L):
    """Two rows facing the straight, and the leavings of a sport nobody plays."""
    P = L.prop
    F = dict(where=SFP)
    N = dict(where=SNP)
    for (sprite, cx, by, ht) in BUILDINGS:
        L.b.prop(f"{BLD}{sprite}.png", cx, by, ht, solid="core")
        L.placed += 1

    # the start line itself, and what is still standing on it
    P("sf_start_gantry", 20, 50, 8, near_ok=True, **F)
    P("sf_signboard", 28, 44, 4, **F)
    P("sf_lamp_post", 46, 43, 5, **F)
    P("sf_lamp_post", 88, 43, 5, **F)
    P("sf_grandstand", 68, 42, 7, **F)
    # the pit side
    P("sf_pit_awning", 40, 66, 6, **F)
    P("sf_wrecked_racer", 58, 66, 5, **F)
    P("sf_fuel_drums", 74, 65, 4, **F)
    P("sf_wheel_stack", 80, 66, 4, **F)
    P("sf_scrap_heap", 36, 72, 4, **F)
    P("sf_crate_stack", 90, 72, 4, **F)
    P("sf_hand_winch", 100, 66, 4, **F)
    P("sf_condenser", 104, 40, 6, **F)
    # the salt getting in at the edges
    P("sn_driftwood_salt", 14, 68, 3, near_ok=True, **N)
    P("sn_rib_bones", 108, 56, 3, near_ok=True, **N)
    P("sf_tunnel_mouth", 110, 74, 6, **F)      # the hives are closer than anyone admits
    return zone, L


def finish(zone, L):
    return L.finish([PORTAL] + list(NPC_POSITIONS.values()))


def verify(zone):
    """Everything about this town that could quietly stop being true."""
    inside, paved = verify_fields(zone)
    # the straight has to be the only paved ground and it has to run the length of the place, because
    # that is the whole layout: two rows looking at each other across it.
    span = STRAIGHT["x1"] - STRAIGHT["x0"]
    assert span >= 90, f"the straight is only {span} tiles long; it is supposed to be the town"
    north = [p for p in NPC_POSITIONS.values() if p[1] < STRAIGHT["y0"]]
    south = [p for p in NPC_POSITIONS.values() if p[1] > STRAIGHT["y1"]]
    assert len(north) >= 6 and len(south) >= 6, \
        f"the two rows are lopsided: {len(north)} north, {len(south)} south"
    return dict(inside=inside, paved=paved, north=len(north), south=len(south))


def build_saltwheel_baked():
    zone, L = build_saltwheel()
    dress(zone, L)
    finish(zone, L)
    return zone, L


def generate_saltwheel():
    zone, L = build_saltwheel_baked()
    # THE PAINTED GROUND, WHICH WAS BAKED AND NEVER ATTACHED. Found 13 Nov 2026: this zone drew in
    # the fallback tiles - plain dirt and a grey grid for rock - while a full set of baked chunks
    # sat in its folder. It is what Kyle's backlog called "has no tiles".
    register_baked(zone, BAKED)
    return zone
