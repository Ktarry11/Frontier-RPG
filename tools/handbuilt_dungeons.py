"""Hand-placed dungeon layouts (Kyle: "lets hand build some of them").

Replaces the generator-driven versions of Blackfathom Deeps, Widow's Lair
and Shadowfang Keep. Every room, corridor and prop below is placed at an
explicit coordinate - no random scatter decides the shape. Hard contracts
kept exactly (world/portal_manager.py _links):
    Blackfathom Deeps  portal (120, 205) <-> Ashenvale West (30, 20)
    Widow's Lair       portal ( 70, 108) <-> Silverpine North (170, 100)
    Shadowfang Keep    portal ( 85, 152) <-> Silverpine South (100, 155)
Each generator ends with Builder.verify(): a 4-way flood fill from the
portal must reach every boss and chest or the zone fails to build.
"""
from world.tilemap import Tilemap
from tools.dungeon_builder import Builder

NAGA = "assets/tiles/naga_dungeon/"
SEABED = "assets/tiles/seabed/"
RUINS = "assets/tiles/ruins/"
CORR = "assets/tiles/ashenvale_corruption/props/"
DEN = "assets/tiles/the_den/props/"
CAVE_LM = "assets/tiles/cave_landmarks/"
TIRA = "assets/tiles/tiragarde_keep/props/"
HAUNT = "assets/tiles/haunted_forest/props/"
SKULL = "assets/tiles/skull_rock/props/"


def generate_blackfathom_deeps():
    """Blackfathom Deeps (240x220): entry cave -> Pool of Ask'ar junction ->
    three branches (NW swim to Sarevess, S cross-tunnels to Gelihast, NE
    gauntlet to Lorgus) -> Serra'kis' grotto -> Drowned Sacellum (Kelris,
    4 braziers) -> Aku'mai's chamber. Boss coordinates are pinned and
    unchanged from the previous layout."""
    zone = Tilemap("Blackfathom Deeps", 240, 220,
                   "Sunken night elf temple. Naga and twilight corruption "
                   "have claimed these ruins; the sea is reclaiming the rest.")
    zone.is_cave = True
    zone.region = "Ashenvale West"
    b = Builder(zone, wall_id="wall", floor_id="dirt")

    entrance = (120, 205)
    ghamoora = (130, 150)
    sarevess = (45, 98)
    gelihast = (200, 205)
    lorgus = (168, 90)
    serrakis = (128, 62)
    kelris = (120, 8)
    akumai = (40, 12)

    # --- Entrance cavern + winding tunnel up to the pool ---
    b.lobes([(120, 198, 10, 7), (111, 195, 5, 4), (130, 196, 5, 4)])
    b.corridor([(120, 205), (120, 192)], width=2)
    b.corridor([(120, 192), (120, 186), (127, 181), (130, 172)], width=2)
    zone.add_subzone("Entrance Caverns", 106, 188, 30, 20)

    # --- Pool of Ask'ar: the first junction, Ghamoo-ra on an island ---
    b.lobes([(130, 155, 25, 17), (108, 150, 9, 9), (152, 160, 9, 9),
             (130, 139, 13, 6), (130, 170, 8, 5)])
    b.water([(130, 154, 17, 12)], island=[(130, 150, 5, 4)])
    zone.add_subzone("Pool of Ask'ar", 103, 135, 55, 40)

    # --- NW branch: a flooded channel to Lady Sarevess ---
    b.corridor([(111, 148), (98, 140), (84, 128), (70, 118), (58, 111)],
               width=3, base="shallow_water")
    b.lobes([(50, 105, 13, 10), (41, 98, 7, 6), (58, 113, 6, 5), (48, 114, 7, 4)])
    b.water([(53, 109, 6, 3)])
    zone.add_subzone("Sarevess's Grotto", 34, 90, 32, 28)

    # --- South branch: cross-tunnels to Gelihast's pool ---
    b.corridor([(132, 198), (150, 203), (165, 206), (186, 205)], width=2)
    b.corridor([(150, 203), (150, 188), (150, 168)], width=1)
    b.lobes([(196, 200, 13, 9), (206, 194, 6, 5), (187, 207, 5, 4), (198, 211, 7, 4)])
    b.water([(194, 197, 6, 4)])
    zone.add_subzone("Gelihast's Pool", 181, 189, 32, 26)

    # --- NE branch: the Twilight Gauntlet to Lorgus Jett ---
    b.corridor([(140, 138), (150, 128), (158, 116), (164, 100)], width=2)
    b.lobes([(165, 95, 12, 9), (174, 88, 6, 5), (157, 98, 6, 5)])
    zone.add_subzone("Twilight Gauntlet", 151, 82, 32, 24)

    # --- Old Serra'kis: flooded side grotto off the gauntlet ---
    b.corridor([(154, 100), (146, 90), (138, 80), (134, 70)],
               width=2, base="shallow_water")
    b.lobes([(130, 65, 10, 8), (121, 60, 5, 4), (139, 70, 5, 4)])
    b.water([(128, 68, 6, 3)])
    zone.add_subzone("The Sunken Grotto", 116, 55, 30, 24)

    # --- Drowned Sacellum: approach, walled antechamber, Kelris' hall ---
    b.corridor([(165, 90), (160, 72), (148, 60), (134, 50), (121, 43)], width=2)
    b.rect(111, 35, 129, 45, chamfer=2)          # the walled choke-point
    b.corridor([(120, 40), (120, 20)], width=1)
    b.rect(102, 3, 138, 23, chamfer=3)           # Kelris' summoning hall
    zone.add_subzone("Drowned Sacellum", 100, 0, 40, 26)

    # --- Aku'mai's chamber, west of the Sacellum ---
    b.corridor([(106, 12), (80, 12), (56, 12)], width=1)
    b.lobes([(45, 12, 14, 9), (36, 7, 6, 5), (36, 17, 6, 4)])
    zone.add_subzone("Aku'mai's Chamber", 28, 0, 34, 24)

    # --- Temple styling: Twilight-stone walls + flagstone floor from the
    # antechamber's choke-point through Kelris' hall (the Drowned Sacellum).
    b.restyle(96, 0, 144, 52, floor="stone", wall="cliff")

    # --- Markers ---
    zone.set_tile(*entrance, "portal", "interaction")
    for pos in (ghamoora, sarevess, gelihast, lorgus, serrakis, kelris, akumai):
        zone.set_tile(pos[0], pos[1], "boss_marker", "interaction")
    braziers = [(108, 4), (132, 4), (108, 16), (132, 16)]
    for bx, by in braziers:
        zone.set_tile(bx, by, "quest_marker", "interaction")
    chests = [(akumai[0] + 4, akumai[1] + 1), (kelris[0], kelris[1] + 6)]
    for cx, cy in chests:
        zone.set_tile(cx, cy, "chest", "interaction")

    # --- Props (hand placed; bottom-center anchors) ---
    b.prop(NAGA + "shipwreck.png", 191, 198, 4, solid="core")        # sunken wreck
    b.prop(NAGA + "giant_crab.png", 137, 74, 3)                       # Serra'kis' kin
    b.prop(NAGA + "serpent_skeleton.png", 172, 100, 4)                # gauntlet remains
    b.prop(RUINS + "ruin_archway.png", 120, 47, 4)                    # Kelris' walled gate
    b.prop(RUINS + "ruin_bone_pillars.png", 109, 14, 6, solid="core")
    b.prop(RUINS + "ruin_bone_pillars.png", 131, 14, 6, solid="core")
    b.prop(CORR + "void_crystal_formation.png", 105, 22, 3, solid="core")
    b.prop(CORR + "void_crystal_formation.png", 135, 22, 3, solid="core")
    b.prop(CORR + "void_crystal_formation.png", 177, 92, 3, solid="core")
    b.prop(CORR + "void_crystal_formation.png", 50, 17, 3, solid="core")
    for bx, by in braziers:
        b.prop(CORR + "fel_fire_brazier.png", bx, by, 3)
    for (px, py, nm) in [(116, 149, "shell_pearl"), (144, 147, "shell_brown"),
                         (119, 160, "coral_blue"), (143, 163, "coral_pink"),
                         (126, 161, "coral_red"), (136, 143, "shell_pearl"),
                         (48, 112, "coral_blue"), (55, 108, "shell_brown"),
                         (197, 202, "coral_pink"), (192, 196, "shell_pearl"),
                         (126, 70, "coral_red"), (132, 67, "shell_brown")]:
        b.prop(SEABED + nm + ".png", px, py, 1)

    # Entrance-side landing stays clear (cheap guarantee, portal already open).
    n = b.verify(entrance, [ghamoora, sarevess, gelihast, lorgus, serrakis,
                            kelris, akumai] + [(x, y, "chest") for x, y in chests]
                 + [(x, y, "brazier") for x, y in braziers])

    zone.boss_positions = [
        (ghamoora[0], ghamoora[1], "Ghamoo-ra"),
        (sarevess[0], sarevess[1], "Lady Sarevess"),
        (gelihast[0], gelihast[1], "Gelihast"),
        (lorgus[0], lorgus[1], "Lorgus Jett"),
        (serrakis[0], serrakis[1], "Old Serra'kis"),
        (kelris[0], kelris[1], "Twilight Lord Kelris"),
        (akumai[0], akumai[1], "Aku'mai"),
    ]
    zone.boss_position = akumai
    zone.add_subzone("Blackfathom Deeps", 0, 0, zone.width, zone.height)
    return zone


def generate_widows_lair():
    """Widow's Lair (140x120): a spider warren drawn by hand.

    Entrance web chamber -> Central Nest hub, then two narrow tunnels:
    WEST to Broodmother Silka's egg chamber, EAST down a serpentine silk
    tunnel to Weaver Skitter's lair. Neither lair is a dead end: each exits
    into the Web Gallery, and ONLY the gallery leads north to Matriarch
    Velaxis, so you must fight through at least one lair to reach her.
    (Previously this dungeon used "stone" as its wall tile - not a blocker -
    so it had no walls at all.)"""
    zone = Tilemap("Widow's Lair", 140, 120,
                   "Spider-infested cavern: egg chambers, silk-choked tunnels, "
                   "and a matriarch at the heart of the web.")
    zone.is_cave = True
    zone.region = "Silverpine North"
    b = Builder(zone, wall_id="rock", floor_id="dirt")

    entrance = (70, 108)
    silka = (35, 55)
    skitter = (106, 46)
    velaxis = (70, 12)

    # Entrance web chamber + Central Nest
    b.lobes([(70, 100, 18, 9), (57, 96, 8, 6), (83, 97, 8, 6)])
    b.corridor([(70, 96), (70, 78)], width=2)
    b.lobes([(70, 76, 13, 9), (60, 70, 6, 5), (80, 70, 6, 5)])
    zone.add_subzone("Web Entrance", 50, 90, 40, 20)
    zone.add_subzone("The Central Nest", 54, 64, 32, 24)

    # WEST: tunnel to Silka's egg chamber
    b.corridor([(58, 76), (46, 78), (38, 72), (34, 64)], width=1)
    b.lobes([(34, 56, 14, 11), (25, 49, 7, 6), (43, 48, 7, 6), (30, 66, 8, 5)])
    zone.add_subzone("Silka's Egg Chamber", 18, 42, 36, 30)

    # EAST: serpentine silk tunnel to Skitter's lair
    b.corridor([(82, 76), (96, 78), (106, 74), (108, 66), (98, 62), (102, 54)], width=1)
    b.lobes([(106, 46, 12, 9), (115, 41, 6, 5), (97, 42, 6, 5)])
    zone.add_subzone("The Silk Tunnels", 90, 56, 26, 26)
    zone.add_subzone("Skitter's Lair", 92, 34, 32, 22)

    # Web Gallery - both lairs exit here; north is the only way on
    b.lobes([(70, 48, 10, 6), (62, 44, 5, 4), (78, 44, 5, 4)])
    b.corridor([(43, 48), (58, 46)], width=1)       # Silka's chamber -> gallery
    b.corridor([(97, 42), (82, 45)], width=1)       # Skitter's lair -> gallery
    zone.add_subzone("The Web Gallery", 56, 38, 28, 18)

    # NORTH: Matriarch's chamber
    b.corridor([(70, 43), (70, 28)], width=1)
    b.lobes([(70, 20, 26, 13), (52, 26, 9, 7), (88, 26, 9, 7), (70, 9, 12, 5)])
    zone.add_subzone("Matriarch's Chamber", 42, 4, 56, 34)

    # Markers
    zone.set_tile(*entrance, "portal", "interaction")
    for pos in (silka, skitter, velaxis):
        zone.set_tile(pos[0], pos[1], "boss_marker", "interaction")
    chests = [(silka[0] + 5, silka[1] + 3), (skitter[0] + 4, skitter[1] + 2),
              (velaxis[0] + 6, velaxis[1] + 3)]
    for cx, cy in chests:
        zone.set_tile(cx, cy, "chest", "interaction")

    # Props
    b.prop(HAUNT + "twisted_root_arch.png", 70, 94, 4)                    # mouth of the warren
    b.prop(DEN + "web_tent_peak.png", 70, 9, 7)                          # Velaxis' web-nest
    b.prop(DEN + "egg_cluster_a.png", 27, 53, 5, solid="core")
    b.prop(DEN + "egg_cluster_b.png", 42, 59, 5, solid="core")
    b.prop(DEN + "egg_cocoon_hanging.png", 33, 48, 5)
    b.prop(DEN + "egg_cluster_b.png", 111, 51, 5, solid="core")
    b.prop(DEN + "egg_cocoon_hanging.png", 100, 46, 5)
    b.prop(DEN + "egg_cluster_a.png", 56, 28, 5, solid="core")
    b.prop(DEN + "egg_cluster_a.png", 86, 29, 5, solid="core")
    b.prop(DEN + "web_bridge_a.png", 103, 70, 4)
    b.prop(DEN + "web_bridge_b.png", 70, 51, 4)
    b.prop(CAVE_LM + "cocoon_web.png", 62, 47, 2)
    b.prop(CAVE_LM + "cocoon_web.png", 78, 47, 2)
    b.prop(CAVE_LM + "cocoon_web.png", 60, 74, 2)
    b.prop(CAVE_LM + "cocoon_web.png", 80, 74, 2)
    b.prop(CAVE_LM + "cocoon_web.png", 64, 99, 2)
    b.prop(CAVE_LM + "cocoon_web.png", 77, 98, 2)

    b.verify(entrance, [silka, skitter, velaxis] + [(x, y, "chest") for x, y in chests])

    zone.boss_positions = [
        (silka[0], silka[1], "Broodmother Silka"),
        (skitter[0], skitter[1], "Weaver Skitter"),
        (velaxis[0], velaxis[1], "Matriarch Velaxis"),
    ]
    zone.boss_position = velaxis
    zone.add_subzone("Widow's Lair", 0, 0, zone.width, zone.height)
    return zone


def generate_shadowfang_keep():
    """Shadowfang Keep (170x160): Arugal's castle, laid out room by room.

    Gate Hall -> Outer Ward, with the Kennel (Rethilgore, west) and Barracks
    (Razorclaw the Butcher, east) as side halls. North of the ward is the
    Great Hall (Baron Silverlaine). From the hall the WEST door leads to
    Fenrus the Devourer's crypt and, past it, the Upper Landing and Arugal's
    Sanctum; the EAST door leads to an optional dead-end Armory. So Fenrus
    is mandatory, the Armory is not. (Previously "stone" walls = no walls.)"""
    zone = Tilemap("Shadowfang Keep", 170, 160,
                   "Gothic castle, worgen-infested, Arugal's mad lair.")
    zone.is_cave = True
    zone.region = "Silverpine South"
    b = Builder(zone, wall_id="wall", floor_id="stone")

    entrance = (85, 152)
    rethilgore = (34, 128)
    razorclaw = (136, 128)
    silverlaine = (85, 82)
    fenrus = (40, 60)
    arugal = (85, 10)

    # Gate Hall + Outer Ward
    b.rect(70, 141, 100, 153, chamfer=2)
    b.corridor([(85, 142), (85, 132)], width=2)
    b.rect(55, 116, 115, 136, chamfer=3)
    b.pillars((62, 70, 100, 108), (122, 130))
    zone.add_subzone("Gate Hall", 68, 139, 34, 16)
    zone.add_subzone("The Outer Ward", 53, 114, 64, 24)

    # Kennel (west) and Barracks (east)
    b.rect(22, 118, 46, 138, chamfer=2)
    b.corridor([(44, 127), (58, 127)], width=1)
    b.rect(124, 118, 148, 138, chamfer=2)
    b.corridor([(112, 127), (126, 127)], width=1)
    b.restyle(22, 118, 46, 138, floor="dirt")
    zone.add_subzone("The Kennel", 20, 116, 28, 24)
    zone.add_subzone("The Barracks", 122, 116, 28, 24)

    # Great Hall
    b.corridor([(85, 120), (85, 104)], width=2)
    b.rect(60, 76, 110, 106, chamfer=3)
    b.pillars((68, 78, 92, 102), (82, 90, 98))
    zone.add_subzone("The Great Hall", 58, 74, 54, 34)

    # WEST door: Fenrus' crypt, then the Upper Landing
    b.corridor([(62, 91), (40, 91), (40, 76)], width=1)
    b.rect(26, 50, 54, 78, chamfer=3)
    b.restyle(26, 50, 54, 78, floor="dirt")
    b.pillars((32, 48), (58, 66, 74))
    zone.add_subzone("Fenrus' Crypt", 24, 48, 34, 32)
    b.corridor([(40, 52), (40, 44), (68, 44)], width=1)
    b.rect(66, 38, 104, 50, chamfer=2)
    zone.add_subzone("The Upper Landing", 64, 36, 42, 16)

    # EAST door: optional dead-end Armory
    b.corridor([(108, 91), (130, 91), (130, 76)], width=1)
    b.rect(116, 52, 144, 78, chamfer=3)
    b.pillars((122, 138), (58, 66, 74))
    zone.add_subzone("The Armory", 114, 50, 34, 30)

    # Arugal's Sanctum
    b.corridor([(85, 40), (85, 26)], width=2)
    b.rect(58, 4, 112, 30, chamfer=4)
    b.pillars((66, 104), (10, 18, 24))
    zone.add_subzone("Arugal's Sanctum", 56, 2, 58, 30)

    # Markers
    zone.set_tile(*entrance, "portal", "interaction")
    for pos in (rethilgore, razorclaw, silverlaine, fenrus, arugal):
        zone.set_tile(pos[0], pos[1], "boss_marker", "interaction")
    chests = [(134, 62), (arugal[0] + 8, arugal[1] + 4), (28, 126)]
    for cx, cy in chests:
        zone.set_tile(cx, cy, "chest", "interaction")

    # Props
    b.prop(RUINS + "ruin_archway.png", 85, 143, 4)                       # gate to the ward
    b.prop(RUINS + "ruin_archway.png", 85, 121, 4)                       # ward -> great hall
    b.prop(RUINS + "ruin_archway.png", 85, 41, 4)                        # landing -> sanctum
    b.prop(RUINS + "ruin_tower_skulls.png", 74, 151, 5, solid="core")
    b.prop(RUINS + "ruin_tower_skulls.png", 97, 151, 5, solid="core")
    b.prop(TIRA + "tiragarde_barrel_crate_cluster.png", 66, 134, 3, solid="core")
    b.prop(TIRA + "tiragarde_barrel_crate_cluster.png", 106, 121, 3, solid="core")
    b.prop(TIRA + "tiragarde_rubble_pile.png", 76, 129, 3)
    b.prop(TIRA + "tiragarde_rubble_pile.png", 96, 132, 3)
    b.prop(SKULL + "bone_pile.png", 28, 134, 4, solid="core")
    b.prop(SKULL + "bone_pile.png", 40, 122, 4, solid="core")
    b.prop(TIRA + "tiragarde_barrel_crate_cluster.png", 130, 135, 3, solid="core")
    b.prop(TIRA + "tiragarde_rubble_beam.png", 142, 124, 3)
    b.prop(TIRA + "tiragarde_rubble_pile.png", 70, 102, 3)
    b.prop(TIRA + "tiragarde_rubble_pile.png", 102, 86, 3)
    b.prop(RUINS + "ruin_wall_arch.png", 85, 100, 4)
    b.prop(TIRA + "tiragarde_ruined_wall_section.png", 40, 55, 5, solid="core")
    b.prop(TIRA + "tiragarde_rubble_pile.png", 48, 72, 3)
    b.prop(TIRA + "tiragarde_barrel_crate_cluster.png", 122, 72, 3, solid="core")
    b.prop(TIRA + "tiragarde_rubble_beam.png", 138, 56, 3)
    for bx, by in [(68, 12), (102, 12), (68, 26), (102, 26)]:
        b.prop(CORR + "fel_fire_brazier.png", bx, by, 3)
    b.prop(CORR + "void_crystal_formation.png", 76, 8, 3, solid="core")
    b.prop(CORR + "void_crystal_formation.png", 94, 8, 3, solid="core")

    b.verify(entrance, [rethilgore, razorclaw, silverlaine, fenrus, arugal]
             + [(x, y, "chest") for x, y in chests])

    zone.boss_positions = [
        (rethilgore[0], rethilgore[1], "Rethilgore"),
        (razorclaw[0], razorclaw[1], "Razorclaw the Butcher"),
        (silverlaine[0], silverlaine[1], "Baron Silverlaine"),
        (fenrus[0], fenrus[1], "Fenrus the Devourer"),
        (arugal[0], arugal[1], "Archmage Arugal"),
    ]
    zone.boss_position = arugal
    zone.add_subzone("Shadowfang Keep", 0, 0, zone.width, zone.height)
    return zone
