"""
Hand-built THE GRAVITY FOUNDRY, levels 56-58: the first of the two dungeons in the Citadel of Ascent, the Ascendancy's
fortress on the Ascendant Bastions. Its door is the citadel's south gate, the bronze foundry gate off the parade ground
(tools/handbuilt_worldtree_ascendant_bastions.PORTALS (160,124)). The Ascendant Spire (60) is the north gate.

Kyle, 21 Nov 2026: "For the Bastion, let's have a 'Hellfire Citadel' like style. We can have a lvl 56-58 and a lvl
60 dungeon. Both into one mega structure but different entrances. Each dungeon will have around 8-9 bosss over two
floors." And from before: "hallway simulators are boring and uninspired", and "aurelion is ancient, we are new". The
citadel was a scholar house's college before the Ascendancy took it, and the foundry under it was the college's
workshop. The Ascendancy kept the halls and changed what's made in them: every construct on the Bastions was poured
here, and below, in the Keelworks, they're building the engine for the first warship.

THE FOUNDRY HALLS (180x140), 56-57. In from the south gate, out by the lift behind the Foundry-Master.
    the Intake (the crystal carts come in; Brannoc Teal holds the hall) -> west to the Casting Floor (the pour, and
    the Slag Colossus that climbs out of it) or east to the Quench Halls (the Pourmasters) -> either way up into the
    Assembly Ring round the assembly pit -> the Overseer's Gallery, where Cassor Vane watches it all -> the lift down.
    The Testing Hall (Prototype Nine) is off the Quench Halls, and optional. The Casting Floor's back stair runs
    straight up to the Gallery, so the floor is two loops.
        1 Intake-Warden Brannoc Teal   the officer at the door: a construct hound, and he calls the guard
        2 The Slag Colossus            cooling slag that climbs out of the pour: burns, and slows as it cools
        3 Pourmasters Ilka and Dov     twins, one fight: she pours molten crystal, he quenches it ice-cold
        4 Prototype Nine (optional)    the construct nobody's ever switched off: throws back what's cast at it
        5 Foundry-Master Cassor Vane   the master engineer: gravity stones, and he drops the ceiling on you

THE KEELWORKS (180x150), 57-58. Down the lift into the dry-dock where the first warship's engine is being built.
    the Lift Landing -> west over the Gantry Walks (Dessa Marn on the platform over the drop) or east through the
    Gravity Chamber (Iselle Varr among the pits) -> either way down into the Core Vault (the Coreless) -> the Great
    Slip, where the warship sits on its keel and the Warheart wakes -> the fast exit out to the parade ground
        6 Gantry-Chief Dessa Marn      the bomb-crystals, and the little bomber at her shoulder
        7 Gravity-Wright Iselle Varr   lifts the floor out from under you and drops it again
        8 The Coreless                 an engine core with no ship: unstable, and it overloads
        9 The Warheart                 the first warship's heart, awake: cannons, and the engine burns hotter

HARD CONTRACTS (world/portal_manager.py)
  DOOR (90,138) <-> the Bastions' south gate (160,124)
  STAIR_DOWN (90,3) on the Foundry Halls <-> STAIR_UP (90,2) on the Keelworks
  FAST_EXIT (176,136) on the Keelworks -> the Bastions, past the Warheart
"""
from tools import citadel_dungeon_kit as K

NAME = "The Gravity Foundry"
HALLS, KEEL = NAME, "The Gravity Foundry: The Keelworks"
FLOORS = (HALLS, KEEL)
BAKED = {HALLS: "assets/tiles/sky/baked_gravity_foundry", KEEL: "assets/tiles/sky/baked_keelworks"}
REGION = "The Ascendant Bastions"
DESC = {
    HALLS: "The foundry under the Citadel of Ascent: a scholar house's old workshops, where the Ascendancy pours its "
           "constructs.",
    KEEL: "The dry-dock under the foundry, where the Ascendancy is building the engine for its first warship.",
}
BLD = "assets/buildings/"
SKP = "assets/tiles/sky/props/"
ENT = "assets/tiles/cave_entrances/"
COLUMN = BLD + "ae_avenue_column.png"

DOOR = (90, 138)
STAIR_DOWN = (90, 3)
STAIR_UP = (90, 2)
FAST_EXIT = (176, 136)

FLOOR = {
    HALLS: dict(
        size=(180, 140), start=(90, 134),
        rooms={
            "The Intake":             ("rect", 64, 106, 116, 134, 3),
            "The Casting Floor":      ("rect", 10, 68, 54, 122, 3),
            "The Quench Halls":       ("rect", 124, 68, 156, 122, 3),
            "The Testing Hall":       ("rect", 162, 60, 176, 104, 2),
            "The Assembly Ring":      ("lobes", [(90, 58, 22, 17)]),
            "The Overseer's Gallery": ("rect", 52, 6, 128, 30, 3),
        },
        # molten crystal: the pour on the Casting Floor, and the assembly pit in the Ring
        deep=[(32, 99, 8, 9), (90, 58, 7, 5)],
        land=[],
        passages=[([(90, 139), (90, 132)], 2),                  # in from the south gate
                  ([(66, 120), (52, 120)], 3),                  # the Intake -> the Casting Floor
                  ([(114, 120), (126, 120)], 3),                # the Intake -> the Quench Halls
                  ([(154, 96), (164, 96)], 2),                  # the Quench Halls -> the Testing Hall
                  ([(32, 70), (32, 58), (70, 58)], 3),          # the Casting Floor -> the Ring
                  ([(140, 70), (140, 58), (110, 58)], 3),       # the Quench Halls -> the Ring
                  ([(90, 43), (90, 28)], 3),                    # the Ring -> the Gallery
                  ([(16, 70), (16, 18), (54, 18)], 2),          # the Casting Floor's back stair up to the Gallery
                  ([(90, 8), (90, 2)], 2)],                     # the lift down, behind the Foundry-Master
        cells=[(2, 36, 10, 46), (136, 10, 146, 18), (2, 126, 12, 134)],
        cell_links=[([(16, 41), (8, 41)], 1), ([(126, 14), (138, 14)], 1), ([(14, 120), (7, 128)], 1)],
        pillars=[(72, 114), (106, 114), (62, 20), (116, 20)],
        bosses=[(90, 112, "Intake-Warden Brannoc Teal"), (32, 80, "The Slag Colossus"),
                (134, 82, "Pourmaster Ilka"), (169, 70, "Prototype Nine"),
                (90, 14, "Foundry-Master Cassor Vane")],
        pack={"Pourmaster Ilka": [(146, 82, "Pourmaster Dov")]},
        final="Foundry-Master Cassor Vane",
        doors=[DOOR, STAIR_DOWN],
        dressing=[(ENT + "ent_exit_crypt_stairs.png", 90, 137, 5, False),
                  # the Intake: the ore carts come in on their rails, and the rivets and chain go out
                  (SKP + "ab_ore_cart.png", 72, 128, 3, "core"), (SKP + "ab_ore_cart.png", 108, 128, 3, "core"),
                  (SKP + "ab_rivet_bin.png", 70, 110, 3, "core"), (BLD + "ae_crystal_crates.png", 110, 110, 3, "core"),
                  (SKP + "ab_chain_coil.png", 100, 132, 2, False),
                  # the Casting Floor: the crucible over the pour, the furnace that heats it, the moulds it fills
                  (SKP + "ab_crucible.png", 22, 98, 5, "core"), (SKP + "ab_furnace.png", 18, 76, 6, "core"),
                  (SKP + "ab_casting_mould.png", 46, 90, 3, False), (SKP + "ab_casting_mould.png", 46, 106, 3, False),
                  (SKP + "ab_slag_heap.png", 44, 76, 3, "core"), (SKP + "ab_slag_heap.png", 20, 116, 3, "core"),
                  (SKP + "ab_crane.png", 46, 118, 5, "core"),
                  # the Quench Halls: the tanks the castings cool in
                  (SKP + "ab_quench_tank.png", 130, 76, 3, "core"), (SKP + "ab_quench_tank.png", 150, 76, 3, "core"),
                  (SKP + "ab_quench_tank.png", 130, 104, 3, "core"), (SKP + "ab_quench_tank.png", 150, 104, 3, "core"),
                  (SKP + "ab_crystal_lathe.png", 140, 118, 3, "core"),
                  # the Testing Hall: the shield pylons, and what's left of the prototypes before Nine
                  (BLD + "ae_shield_pylon.png", 165, 100, 6, "core"), (BLD + "ae_shield_pylon.png", 174, 100, 6, "core"),
                  (SKP + "ab_broken_construct.png", 165, 86, 3, "core"), (SKP + "ab_broken_construct.png", 174, 80, 3, "core"),
                  # the Assembly Ring: a cradle at each quarter, the conveyor and the limb racks between
                  (SKP + "ab_assembly_cradle.png", 76, 50, 5, "core"), (SKP + "ab_assembly_cradle.png", 104, 50, 5, "core"),
                  (SKP + "ab_assembly_cradle.png", 76, 70, 5, "core"), (SKP + "ab_assembly_cradle.png", 104, 70, 5, "core"),
                  (SKP + "ab_limb_rack.png", 90, 46, 3, "core"), (SKP + "ab_conveyor.png", 90, 72, 2, False),
                  # the Overseer's Gallery: the engine the Foundry-Master runs it all from, his bench and his standards
                  (BLD + "ae_crystal_engine.png", 68, 14, 7, "core"), (SKP + "ab_workbench.png", 112, 14, 3, "core"),
                  (SKP + "ab_standard.png", 80, 10, 4, "core"), (SKP + "ab_standard.png", 100, 10, 4, "core"),
                  (SKP + "ab_test_core.png", 74, 26, 3, "core")],
    ),
    KEEL: dict(
        size=(180, 150), start=(90, 6),
        rooms={
            "The Lift Landing":    ("rect", 72, 4, 108, 24, 2),
            "The Gantry Walks":    ("rect", 8, 20, 62, 82, 2),
            "The Gravity Chamber": ("rect", 118, 20, 172, 82, 3),
            "The Core Vault":      ("lobes", [(90, 102, 24, 16)]),
            "The Great Slip":      ("rect", 14, 126, 166, 146, 4),
        },
        # the drop under the gantries, the gravity pits, the core's well and the slip under the warship's hull
        deep=[("rect", 16, 32, 54, 70),
              (132, 38, 6, 5), (158, 38, 6, 5), (132, 64, 6, 5), (158, 64, 6, 5),
              (90, 107, 6, 4),
              ("rect", 50, 135, 130, 146)],
        # the gantry across the drop, and the platform Dessa Marn works from
        land=[("rect", 32, 32, 38, 70), ("lobes", [(35, 51, 7, 6)])],
        passages=[([(90, 1), (90, 8)], 2),                       # up the lift to the Foundry Halls
                  ([(74, 14), (36, 14), (36, 24)], 2),           # the Landing -> the Gantry Walks
                  ([(106, 14), (145, 14), (145, 24)], 2),        # the Landing -> the Gravity Chamber
                  ([(35, 78), (35, 100), (70, 100)], 3),         # the Gantry Walks -> the Core Vault
                  ([(145, 78), (145, 100), (110, 100)], 3),      # the Gravity Chamber -> the Core Vault
                  ([(90, 116), (90, 128)], 3),                   # the Core Vault -> the Great Slip
                  ([(162, 136), (178, 136)], 2)],                # past the Warheart: the fast exit
        cells=[(2, 92, 12, 102), (168, 92, 178, 102), (2, 128, 10, 136)],
        cell_links=[([(10, 80), (7, 94)], 1), ([(168, 79), (173, 94)], 1), ([(16, 132), (8, 132)], 1)],
        pillars=[(40, 130), (138, 130), (40, 142), (138, 142)],
        bosses=[(35, 51, "Gantry-Chief Dessa Marn"), (145, 51, "Gravity-Wright Iselle Varr"),
                (90, 94, "The Coreless"), (90, 130, "The Warheart")],
        pack={},
        final="The Warheart",
        doors=[STAIR_UP, FAST_EXIT],
        dressing=[(BLD + "ae_gravity_lift.png", 100, 12, 6, "core"), (SKP + "ab_crane.png", 80, 12, 5, "core"),
                  # the Gantry Walks: the gantry pillars at the drop's corners, and the bomb-crystal stores
                  (SKP + "ab_gantry_pillar.png", 14, 26, 5, "core"), (SKP + "ab_gantry_pillar.png", 56, 26, 5, "core"),
                  (SKP + "ab_gantry_pillar.png", 14, 78, 5, "core"), (SKP + "ab_gantry_pillar.png", 56, 78, 5, "core"),
                  (BLD + "ae_ammo_rack.png", 24, 24, 3, "core"), (BLD + "ae_crystal_crates.png", 46, 24, 3, "core"),
                  # the Gravity Chamber
                  (BLD + "ae_gravity_anchor.png", 124, 28, 6, "core"), (BLD + "ae_gravity_anchor.png", 166, 28, 6, "core"),
                  (SKP + "ab_chain_coil.png", 124, 76, 2, False), (BLD + "ae_gear_bank.png", 166, 78, 5, "core"),
                  # the Core Vault: the engine cores on their test stands round the well
                  (SKP + "ab_test_core.png", 72, 98, 4, "core"), (SKP + "ab_test_core.png", 108, 98, 4, "core"),
                  (BLD + "ae_engine_pylon.png", 76, 112, 6, "core"), (BLD + "ae_engine_pylon.png", 104, 112, 6, "core"),
                  # the Great Slip: the ship's ribs waiting their turn, the cranes, the cradles
                  (SKP + "ab_ship_ribs.png", 26, 140, 4, "core"), (SKP + "ab_ship_ribs.png", 154, 140, 4, "core"),
                  (SKP + "ab_crane.png", 30, 130, 6, "core"), (SKP + "ab_crane.png", 150, 130, 6, "core"),
                  (BLD + "ae_dock_cradle.png", 46, 132, 4, "core"), (BLD + "ae_dock_cradle.png", 134, 132, 4, "core"),
                  (SKP + "ab_rivet_bin.png", 62, 130, 3, "core"), (SKP + "ab_workbench.png", 118, 130, 3, "core")],
        # drawn over the slip without a floor under them: the warship on its keel
        over=[(BLD + "ae_airship_war.png", 90, 147, 13)],
    ),
}

BOSSES = {}


def build_floor(name):
    zone, b = K.build_floor(name, FLOOR[name], DESC[name], REGION, COLUMN)
    for (path, x, y, h) in FLOOR[name].get("over", []):
        b.prop(path, x, y, h, solid=False)
    BOSSES[name] = {n: (x, y) for (x, y, n) in FLOOR[name]["bosses"]}
    return zone, b


def build_halls_baked():
    return build_floor(HALLS)[0], None


def build_keel_baked():
    return build_floor(KEEL)[0], None


def trash(name):
    T, pack = K.pack_builder()
    if name == HALLS:
        # the Intake
        pack(56, (80, 128, "Foundry Guard"), (100, 128, "Foundry Guard"), (90, 124, "Crucible Tender"))
        pack(56, (76, 118, "Intake Hound"), (80, 120, "Intake Hound"), (72, 122, "Foundry Guard"))
        pack(56, (104, 118, "Foundry Smith"), (108, 122, "Crucible Tender"))
        # the Casting Floor
        pack(56, (44, 104, "Foundry Smith"), (46, 98, "Slag Elemental"), (42, 110, "Foundry Smith"))
        pack(57, (18, 104, "Slag Elemental"), (20, 96, "Slag Elemental"), (18, 110, "Crucible Tender"))
        pack(57, (40, 88, "Crucible Tender"), (24, 88, "Foundry Smith"))
        # the Quench Halls
        pack(56, (134, 112, "Quench Hand"), (146, 112, "Quench Hand"), (140, 106, "Foundry Smith"))
        pack(57, (132, 96, "Quench Hand"), (148, 96, "Foundry Guard"), (140, 92, "Crucible Tender"))
        # the Testing Hall
        pack(57, (169, 94, "Proving Frame"), (166, 86, "Proving Frame"))
        # the Assembly Ring, round the pit
        pack(57, (74, 58, "Assembly Construct"), (78, 62, "Foundry Gravity-Binder"), (76, 54, "Assembly Construct"))
        pack(57, (106, 58, "Assembly Construct"), (102, 62, "Foundry Gravity-Binder"), (104, 54, "Foundry Guard"))
        pack(57, (90, 70, "Foundry Overseer"), (84, 72, "Assembly Construct"), (96, 72, "Assembly Construct"))
        # the Overseer's Gallery
        pack(57, (66, 24, "Foundry Overseer"), (60, 26, "Foundry Guard"), (70, 26, "Foundry Gravity-Binder"))
        pack(57, (114, 24, "Foundry Overseer"), (120, 26, "Foundry Guard"), (110, 26, "Foundry Gravity-Binder"))
        pack(57, (30, 20, "Intake Hound"), (36, 20, "Intake Hound"), (42, 20, "Foundry Guard"))   # the back stair
    else:
        # the Lift Landing
        pack(57, (80, 18, "Keelworks Rigger"), (86, 20, "Keelworks Rigger"), (82, 16, "Hull Welder"))
        pack(57, (100, 18, "Keelworks Marine"), (96, 20, "Hull Welder"))
        # the Gantry Walks, on the ring round the drop and the gantry across it
        pack(57, (14, 40, "Gantry Bomber"), (12, 48, "Keelworks Rigger"), (14, 56, "Gantry Bomber"))
        pack(58, (58, 44, "Keelworks Marine"), (58, 52, "Hull Welder"), (58, 60, "Keelworks Rigger"))
        pack(58, (35, 36, "Gantry Bomber"), (35, 66, "Gantry Bomber"))
        pack(58, (24, 76, "Keelworks Marine"), (46, 76, "Keelworks Marine"), (35, 78, "Hull Welder"))
        # the Gravity Chamber, between the pits
        pack(57, (145, 32, "Gravity Adept"), (138, 30, "Keel Sentinel"), (152, 30, "Gravity Adept"))
        pack(58, (124, 51, "Keel Sentinel"), (126, 46, "Gravity Adept"))
        pack(58, (166, 51, "Keel Sentinel"), (164, 46, "Gravity Adept"))
        pack(58, (145, 72, "Keelworks Marine"), (138, 74, "Gravity Adept"), (152, 74, "Keel Sentinel"))
        # the Core Vault
        pack(58, (74, 106, "Repair Swarm"), (78, 112, "Repair Swarm"), (72, 100, "Hull Welder"))
        pack(58, (106, 106, "Repair Swarm"), (102, 112, "Keel Sentinel"), (108, 100, "Hull Welder"))
        # the Great Slip
        pack(58, (30, 134, "Keelworks Marine"), (34, 138, "Keelworks Marine"), (26, 138, "Hull Welder"))
        pack(58, (60, 132, "Keel Sentinel"), (66, 130, "Keelworks Rigger"))
        pack(58, (150, 134, "Keelworks Marine"), (146, 138, "Keel Sentinel"), (154, 138, "Hull Welder"))
    return T


def generate(name):
    zone, _b = build_floor(name)
    return K.generate(zone, FLOOR[name], trash(name), BAKED[name])


def generate_halls():
    return generate(HALLS)


def generate_keel():
    return generate(KEEL)


if __name__ == "__main__":
    for n in FLOORS:
        z, _b = build_floor(n)
        walk = sum(z.is_walkable(x, y) for y in range(z.height) for x in range(z.width))
        print(n, z.width, "x", z.height, "| walkable", walk, "| bosses", len(z.boss_positions))
