"""
Hand-built Onyxhollow (100x84): the Dark Iron town under the Abyssal Sands. Standalone town map.

Kyle, 13 Nov 2026: "Entire zone with a small 'town' - (seperate map) of dark iron dwarfs. There wont
be a flight master but this can have an inn." The name is his - "Town can be Onyxhollow" - and so is
the brief: "innkeeper for hearth, level appropriate shops, this can be more of a mining town and
Blacksmithing."

A MINING TOWN THAT MAKES WHAT IT DIGS. Everything here is on one of two streets. The Anvil Road runs
from the gate straight up to the Thane's Hall; Forge Row crosses it, and that is where the work is -
the smithy at the west end, the smeltery at the east, and the inn and the stores where the two
streets meet because that is where everybody passes. The mine head is in the north-west corner and
the vault in the north-east, as far from the gate as the hall can keep them.

AN INN AND NO FLIGHT MASTER. You walk here - down a sinkhole, through the Dry Deep, across the Black
Strand - and the inn is the reason that is bearable: bind here and the walk is done once.
tools/sync_onyxhollow_npcs.py registers the inn and fails if the town ever acquires a flight point.

ONE TRAINER, AND HE TEACHES THE TOWN'S TWO TRADES. Mining and blacksmithing, at the smeltery, with a
working forge beside the smithy (data/npcs/forges.json). Nothing else is taught here on purpose.

THE PEOPLE ARE DRAWN AS THEMSELVES. Each of the eighteen has a figure from the Dark Iron sheet
(tools/slice_dark_iron_dwarves.py), filed per NPC.

HARD CONTRACT (world/portal_manager.py): Onyxhollow (50, 80) <-> The Black Strand (84, 52), the gate
in the middle of the zone, between the two watchtowers.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked  # noqa: F401

NAME = "Onyxhollow"
BAKED = "assets/tiles/onyxhollow/baked"
BAKED_DIR = BAKED
BLD = "assets/buildings/"

W, H = 100, 84
PORTAL = (50, 80)
ARRIVAL = (50, 76)

TOWN = dict(x0=8, y0=10, x1=92, y1=76, chamfer=12)
#: The Anvil Road (gate to hall) and Forge Row (smithy to smeltery). (x0, y0, x1, y1)
ANVIL_ROAD = (47, 26, 53, 78)
FORGE_ROW = (14, 46, 86, 50)

#: (sprite, centre x, base y, height in tiles)
BUILDINGS = [
    ("di_great_hall", 50, 24, 16),
    ("di_mine_head", 20, 28, 13),
    ("di_vault", 80, 27, 11),
    ("di_inn", 32, 43, 15),
    ("di_shop", 68, 43, 13),
    ("di_blast_furnace", 86, 43, 13),
    ("di_boiler_works", 14, 43, 11),
    ("di_smithy", 22, 66, 13),
    ("di_smeltery", 77, 66, 14),
    ("di_crane_warehouse", 62, 69, 10),
    ("di_barracks", 37, 70, 10),
    ("di_shrine", 64, 58, 8),
]

FORGE = (32, 58)      # the working anvil, beside the smithy (forges.json)

NPC_POSITIONS = {
    # the hall
    "oh_thane": (50, 27),
    "oh_loremaster": (42, 28),
    "oh_geomancer": (58, 28),
    # the north corners
    "oh_mining_supplier": (22, 31),
    "oh_vault_keeper": (80, 30),
    # where the streets meet
    "oh_innkeeper": (34, 45),
    "oh_quartermaster": (68, 45),
    "oh_reagents": (60, 45),
    # Forge Row and south of it
    "oh_smith": (24, 68),
    "oh_armorer": (28, 69),
    "oh_forgemaster": (74, 68),
    "oh_stoker": (82, 67),
    "oh_powder": (62, 70),
    "oh_shrine_keeper": (64, 60),
    # the gate
    "oh_gate_captain": (54, 67),
    "oh_gate_guard_w": (46, 76),
    "oh_gate_guard_e": (54, 76),
    "oh_wall_sentry": (36, 73),
}


def _box(gx, gy, x0, y0, x1, y1):
    import numpy as np
    return np.minimum(np.minimum(gx - x0, x1 - gx), np.minimum(gy - y0, y1 - gy))


def street_field(gx, gy):
    """Positive on the two paved streets. Shared with the baker."""
    import numpy as np
    return np.maximum(_box(gx, gy, *ANVIL_ROAD), _box(gx, gy, *FORGE_ROW))


def build_onyxhollow():
    zone = Tilemap(NAME, W, H,
                   "A Dark Iron town cut into the rock under the desert. One road up to the hall, "
                   "one row of forges across it, and a gate that is shut more often than not.")
    zone.is_cave = False
    zone.region = "Kalimdor - Tanaris"
    zone.fixed_spawns = True
    zone.is_town = True

    L = CaveLayout(zone, ARRIVAL)
    b = L.b
    b.wall_id = "rock"
    b.floor_id = "dirt"
    for y in range(H):
        for x in range(W):
            zone.collision_layer[y][x] = "rock"
            zone.set_tile(x, y, "rock", "base")

    b.rect(TOWN["x0"], TOWN["y0"], TOWN["x1"], TOWN["y1"], chamfer=TOWN["chamfer"], base="dirt")
    b.rect(ANVIL_ROAD[0], ANVIL_ROAD[1], ANVIL_ROAD[2], ANVIL_ROAD[3], base="path")
    b.rect(FORGE_ROW[0], FORGE_ROW[1], FORGE_ROW[2], FORGE_ROW[3], base="path")
    b.corridor([(50, 81), (50, 74)], width=3, base="path")      # the gate passage

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.set_tile(px, py, "path", "base")
    L.mark("portal", px, py)

    for npc_id, (x, y) in NPC_POSITIONS.items():
        if not zone.is_walkable(x, y):
            raise AssertionError(f"{NAME}: {npc_id} at ({x},{y}) is not on walkable ground")
        zone.set_tile(x, y, "npc", "interaction")

    zone.add_subzone(NAME, 0, 0, W, H)
    zone.add_subzone("The Thane's Hall", 34, 10, 32, 22)
    zone.add_subzone("Forge Row", 10, 52, 80, 20)
    zone.add_subzone("The Anvil Road", 44, 32, 12, 46)
    zone.arrivals = [ARRIVAL]
    return zone, L


def dress(zone, L):
    """Twelve buildings and the gear of two trades. Less is more: the buildings are the town."""
    D = dict(where=BLD)
    for (sprite, cx, by, ht) in BUILDINGS:
        L.b.prop(f"{BLD}{sprite}.png", cx, by, ht, solid="core")
        L.placed += 1
    P = L.prop
    # the gate, from inside: a tower either side of the passage
    P("di_watchtower", 42, 76, 8, solid="base", fraction=0.4, near_ok=True, **D)
    P("di_watchtower", 58, 76, 8, solid="base", fraction=0.4, near_ok=True, **D)
    # braziers up the Anvil Road, in pairs
    for y in (38, 56, 62):
        P("di_brazier", 45, y, 3, solid="base", fraction=0.3, **D)
        P("di_brazier", 55, y, 3, solid="base", fraction=0.3, **D)
    # the hall's forecourt
    P("di_dwarf_statue", 44, 34, 5, solid="base", fraction=0.4, **D)
    P("di_dwarf_statue", 56, 34, 5, solid="base", fraction=0.4, **D)
    P("di_rune_obelisk", 38, 26, 4, solid="base", fraction=0.3, **D)
    P("di_rune_obelisk", 62, 26, 4, solid="base", fraction=0.3, **D)
    # the smithy's yard: the working anvil, and what feeds it
    P("di_forge_anvil", FORGE[0], FORGE[1] - 1, 4, solid="base", fraction=0.4, near_ok=True, **D)
    P("di_bellows", 36, 58, 4, solid="base", fraction=0.4, **D)
    # the smeltery's yard
    P("di_crucible", 84, 70, 4, solid="base", fraction=0.4, **D)
    P("di_slag_heap", 88, 62, 3, **D)
    P("di_steam_pipes", 68, 66, 4, solid="base", fraction=0.4, **D)
    # the mine head: carts in, carts out
    P("di_ore_cart", 27, 24, 3, **D)
    P("di_ore_cart", 14, 30, 3, **D)
    P("di_crane_hook", 30, 22, 5, solid="base", fraction=0.3, **D)
    # the cage outside the barracks is empty. It is still there.
    P("di_cage", 29, 73, 4, solid="base", fraction=0.4, **D)
    return zone, L


def finish(zone, L):
    return L.finish([PORTAL] + list(NPC_POSITIONS.values()) + [(FORGE[0], FORGE[1] + 1)])


def verify(zone):
    """What could quietly stop being true about this town."""
    assert zone.is_town and not zone.is_cave
    names = {b[0] for b in BUILDINGS}
    for must in ("di_inn", "di_smithy", "di_smeltery", "di_mine_head", "di_great_hall"):
        assert must in names, f"the town has lost its {must}"
    drawn = {lm["sprite_key"].split("/")[-1][:-4] for lm in zone.landmarks}
    lost = names - drawn
    assert not lost, f"buildings in the list and not on the map: {sorted(lost)}"
    # nobody stands inside a building
    for npc_id, (x, y) in NPC_POSITIONS.items():
        assert zone.is_walkable(x, y) or zone.interaction_layer[y][x] == "npc", f"{npc_id} is walled in"
    return dict(buildings=len(BUILDINGS), people=len(NPC_POSITIONS))


def build_onyxhollow_baked():
    zone, L = build_onyxhollow()
    dress(zone, L)
    finish(zone, L)
    return zone, L


def generate_onyxhollow():
    zone, _L = build_onyxhollow_baked()
    register_baked(zone, BAKED)
    return zone


if __name__ == "__main__":
    z, L = build_onyxhollow_baked()
    print(verify(z), "props placed", L.placed, "skipped", L.skipped)
