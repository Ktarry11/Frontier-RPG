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
DP = "assets/tiles/dungeon_props/"


BAKED_BFD = "assets/tiles/blackfathom_deeps/baked"


def generate_blackfathom_deeps():
    """The runtime zone: the built layout under its painted ground (tools/bake_ashenvale_dungeons.py blackfathom_deeps)."""
    import os
    zone = build_blackfathom_deeps()
    if os.path.exists(f"{BAKED_BFD}/ground_0_0.jpg"):
        from tools.handbuilt_vot_caves import register_baked
        register_baked(zone, BAKED_BFD)
    return zone


def build_blackfathom_deeps():
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
    # Entrance + pool: naga guardians flank the way in
    b.prop(DP + "naga_statue.png", 112, 195, 5, solid="core")
    b.prop(DP + "naga_statue.png", 128, 195, 5, solid="core")
    b.prop(DP + "naga_statue.png", 106, 156, 5, solid="core")
    b.prop(DP + "glow_coral_cluster.png", 148, 170, 3)
    b.prop(DP + "glow_coral_cluster.png", 112, 162, 3)
    # Sarevess' grotto
    b.prop(DP + "naga_statue.png", 56, 104, 5, solid="core")
    b.prop(DP + "glow_coral_cluster.png", 38, 108, 3)
    # Gelihast's pool
    b.prop(DP + "grotto_ship_bow.png", 191, 200, 8, solid="core")
    b.prop(DP + "glow_coral_cluster.png", 205, 208, 3)
    # Twilight Gauntlet
    b.prop(DP + "grotto_serpent_skeleton.png", 172, 100, 5)
    b.prop(CORR + "void_crystal_formation.png", 177, 92, 3, solid="core")
    b.prop(DP + "broken_column.png", 160, 98, 4, solid="core")
    # Old Serra'kis' grotto
    b.prop(DP + "grotto_crab_molt.png", 137, 74, 3)
    b.prop(DP + "glow_coral_cluster.png", 122, 64, 3)
    # Drowned Sacellum: walled gate, priestess guardians, columns, altar, braziers
    b.prop(DP + "temple_archway.png", 120, 47, 5)
    b.prop(DP + "priestess_statue.png", 112, 44, 5, solid="core")
    b.prop(DP + "priestess_statue.png", 128, 44, 5, solid="core")
    b.prop(DP + "twilight_altar.png", 120, 6, 4, solid="core")
    for (px, py) in [(111, 11), (129, 11), (111, 21), (129, 21)]:
        b.prop(DP + "temple_column.png", px, py, 6, solid="core")
    b.prop(DP + "broken_column.png", 104, 12, 4, solid="core")
    b.prop(DP + "broken_column.png", 136, 20, 4, solid="core")
    for bx, by in braziers:
        b.prop(DP + "spirit_brazier.png", bx, by + 1, 4, solid="core")
    # Aku'mai's chamber
    b.prop(CORR + "void_crystal_formation.png", 50, 17, 3, solid="core")
    b.prop(DP + "glow_coral_cluster.png", 30, 12, 3)
    b.prop(DP + "priestess_statue.png", 52, 8, 5, solid="core")
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

    # Themed floors: silk-matted nests in the three lairs, heavy web in the
    # silk tunnel and gallery, plain silk-veined earth elsewhere.
    b.restyle(16, 40, 56, 74, floor="stone")        # Silka's egg chamber
    b.restyle(90, 32, 126, 56, floor="stone")       # Skitter's lair
    b.restyle(40, 3, 100, 36, floor="stone")        # Matriarch's chamber
    b.restyle(88, 58, 112, 82, floor="sand")        # silk tunnel
    b.restyle(54, 38, 88, 54, floor="sand")         # web gallery

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
    b.prop(DP + "spider_nest.png", 70, 9, 8, solid="core")                # Velaxis' nest
    b.prop(DP + "web_curtain.png", 70, 41, 5)                              # gallery -> matriarch
    b.prop(DP + "web_curtain.png", 52, 79, 4)                              # tunnel to Silka
    b.prop(DP + "web_curtain.png", 92, 80, 4)                              # mouth of the silk tunnel
    b.prop(DEN + "egg_cluster_a.png", 27, 53, 5, solid="core")
    b.prop(DEN + "egg_cluster_b.png", 42, 59, 5, solid="core")
    b.prop(DEN + "egg_cluster_b.png", 111, 51, 5, solid="core")
    b.prop(DEN + "egg_cluster_a.png", 56, 28, 5, solid="core")
    b.prop(DEN + "egg_cluster_a.png", 86, 29, 5, solid="core")
    b.prop(DP + "cocoon_victim.png", 33, 49, 5)
    b.prop(DP + "cocoon_victim.png", 100, 46, 5)
    b.prop(DP + "cocoon_victim.png", 62, 24, 5)
    b.prop(DP + "cocoon_victim.png", 80, 70, 4)
    b.prop(DP + "spider_husk.png", 30, 62, 4)
    b.prop(DP + "spider_husk.png", 112, 40, 4)
    b.prop(DP + "skull_pile.png", 44, 52, 3, solid="core")
    b.prop(DP + "skull_pile.png", 64, 28, 3, solid="core")
    b.prop(DP + "web_tangle.png", 60, 74, 3)
    b.prop(DP + "web_tangle.png", 76, 99, 3)
    b.prop(DP + "web_tangle.png", 62, 98, 3)
    b.prop(DEN + "web_bridge_a.png", 103, 70, 4)
    b.prop(DEN + "web_bridge_b.png", 70, 51, 4)

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
    b.pillars((68, 78, 92, 102), (82, 90, 98), sprite=DP + "candelabra.png", height=5)
    zone.add_subzone("The Great Hall", 58, 74, 54, 34)

    # WEST door: Fenrus' crypt, then the Upper Landing
    b.corridor([(62, 91), (40, 91), (40, 76)], width=1)
    b.rect(26, 50, 54, 78, chamfer=3)
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
    b.pillars((66, 104), (10, 18, 24), sprite=DP + "candelabra.png", height=5)
    zone.add_subzone("Arugal's Sanctum", 56, 2, 58, 30)

    # Markers
    zone.set_tile(*entrance, "portal", "interaction")
    for pos in (rethilgore, razorclaw, silverlaine, fenrus, arugal):
        zone.set_tile(pos[0], pos[1], "boss_marker", "interaction")
    chests = [(134, 62), (arugal[0] + 8, arugal[1] + 4), (28, 126)]
    for cx, cy in chests:
        zone.set_tile(cx, cy, "chest", "interaction")

    # Arugal's Sanctum gets its own arcane floor
    b.restyle(58, 4, 112, 30, floor="path")

    # Props
    b.prop(RUINS + "ruin_archway.png", 85, 143, 4)                       # gate to the ward
    b.prop(RUINS + "ruin_archway.png", 85, 121, 4)                       # ward -> great hall
    b.prop(RUINS + "ruin_archway.png", 85, 41, 4)                        # landing -> sanctum
    b.prop(RUINS + "ruin_tower_skulls.png", 74, 151, 5, solid="core")
    b.prop(RUINS + "ruin_tower_skulls.png", 97, 151, 5, solid="core")
    b.prop(DP + "gothic_gate.png", 95, 80, 5, solid="core")              # sealed door, Great Hall
    b.prop(DP + "gothic_gate.png", 85, 8, 5, solid="core")               # Arugal's great doors
    b.prop(TIRA + "tiragarde_barrel_crate_cluster.png", 66, 134, 3, solid="core")
    b.prop(TIRA + "tiragarde_barrel_crate_cluster.png", 106, 121, 3, solid="core")
    b.prop(TIRA + "tiragarde_rubble_pile.png", 76, 129, 3)
    b.prop(TIRA + "tiragarde_rubble_pile.png", 96, 132, 3)
    # Kennel
    b.prop(DP + "kennel_cage_empty.png", 27, 124, 4, solid="core")
    b.prop(DP + "kennel_cage_worg.png", 27, 134, 4, solid="core")
    b.prop(DP + "kennel_cage_empty.png", 41, 135, 4, solid="core")
    b.prop(SKULL + "bone_pile.png", 40, 121, 4, solid="core")
    # Barracks
    b.prop(DP + "weapon_rack.png", 130, 122, 4, solid="core")
    b.prop(DP + "weapon_rack.png", 143, 134, 4, solid="core")
    b.prop(TIRA + "tiragarde_barrel_crate_cluster.png", 130, 135, 3, solid="core")
    b.prop(TIRA + "tiragarde_rubble_beam.png", 142, 124, 3)
    # Great Hall
    b.prop(DP + "banquet_table.png", 73, 96, 4, solid="core")
    b.prop(DP + "candelabra.png", 64, 80, 4, solid="core")
    b.prop(DP + "candelabra.png", 106, 104, 4, solid="core")
    b.prop(TIRA + "tiragarde_rubble_pile.png", 102, 90, 3)
    b.prop(DP + "worgen_gargoyle.png", 82, 106, 5, solid="core")
    # Fenrus' crypt
    for (px, py) in [(30, 55), (50, 55), (30, 72), (50, 72)]:
        b.prop(DP + "sarcophagus.png", px, py, 3, solid="core")
    b.prop(TIRA + "tiragarde_rubble_pile.png", 48, 66, 3)
    # Armory
    b.prop(DP + "weapon_rack.png", 122, 56, 4, solid="core")
    b.prop(DP + "weapon_rack.png", 140, 74, 4, solid="core")
    b.prop(TIRA + "tiragarde_barrel_crate_cluster.png", 122, 72, 3, solid="core")
    # Arugal's Sanctum
    b.prop(DP + "ritual_circle.png", 85, 17, 10)
    b.prop(DP + "worgen_gargoyle.png", 78, 29, 5, solid="core")
    b.prop(DP + "worgen_gargoyle.png", 92, 29, 5, solid="core")
    b.prop(DP + "wizard_desk.png", 66, 20, 4, solid="core")
    for (px, py) in [(64, 8), (106, 8), (62, 24), (108, 24)]:
        b.prop(DP + "candelabra.png", px, py, 4, solid="core")
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


GRO = DP + "grotto_"


def generate_sunken_grotto_of_the_deep():
    """Sunken Grotto of the Deep (110x95): the Durotar naga sea-cave, drawn by hand.

    Landing -> Flooded Hall (tidepool, coiled serpent skeleton) with two side
    wings (west: Pearl Nook treasure alcove, east: Kelp Garden) and a fork:
      WEST  Shipwreck Cove   - Undead Pirate Captain (wrecked bow, cannons, skeletons)
      EAST  Crab Den         - Giant Crab (nest, molted shells, tide pools)
    Both forks rejoin at the Naga Shrine (statues, shell altars), which leads
    north into the Naga Sanctum - Naga Shrine Guardian before a coral throne.
    Hard contract kept: portal (55, 92) <-> Durotar (120, 40).
    """
    zone = Tilemap("Sunken Grotto of the Deep", 110, 95,
                   "A drowned sea-cave beneath Durotar's northeast coast, "
                   "claimed by naga.")
    zone.is_cave = True
    zone.region = "Durotar"
    b = Builder(zone, wall_id="wall", floor_id="dirt")

    entrance = (55, 92)
    pirate = (22, 50)
    crab = (88, 50)
    guardian = (55, 10)

    # --- Landing + Flooded Hall ---
    b.lobes([(55, 87, 10, 6), (46, 86, 4, 3), (64, 86, 4, 3)])
    b.corridor([(55, 81), (55, 75)], width=1)
    b.lobes([(55, 66, 15, 9), (42, 64, 6, 5), (68, 64, 6, 5), (55, 74, 6, 3)])
    b.water([(55, 65, 8, 4)], island=[(55, 65, 2, 1)])
    zone.add_subzone("The Landing", 43, 80, 25, 14)
    zone.add_subzone("The Flooded Hall", 38, 56, 36, 22)

    # --- West wing: Pearl Nook (optional treasure alcove) ---
    b.corridor([(40, 66), (28, 68)], width=1)
    b.lobes([(20, 68, 9, 6), (14, 64, 4, 3)], base="sand")
    zone.add_subzone("The Pearl Nook", 9, 60, 24, 16)

    # --- East wing: Kelp Garden (dead end, flavour + trash) ---
    b.corridor([(70, 66), (82, 68)], width=1)
    b.lobes([(91, 68, 10, 7), (98, 63, 4, 3)], base="grass")
    zone.add_subzone("The Kelp Garden", 79, 59, 26, 18)

    # --- West fork: Shipwreck Cove ---
    b.corridor([(46, 58), (34, 54), (28, 50)], width=1)
    b.lobes([(22, 46, 14, 10), (12, 40, 6, 5), (31, 38, 6, 5), (20, 55, 7, 3)])
    b.restyle(12, 38, 34, 58, floor="path")           # deck planks around the wreck
    b.water([(26, 50, 6, 3)])
    zone.add_subzone("Shipwreck Cove", 6, 33, 34, 26)

    # --- East fork: Crab Den ---
    b.corridor([(64, 58), (76, 54), (82, 50)], width=1)
    b.lobes([(88, 46, 14, 10), (98, 40, 6, 5), (79, 38, 6, 5), (90, 55, 7, 3)])
    b.restyle(76, 36, 102, 58, floor="sand")
    b.water([(84, 49, 5, 3)])
    zone.add_subzone("The Crab Den", 74, 33, 34, 26)

    # --- Both forks rejoin at the Naga Shrine ---
    b.corridor([(22, 36), (24, 29), (42, 27)], width=1)
    b.corridor([(88, 36), (86, 29), (68, 27)], width=1)
    b.lobes([(55, 26, 16, 8), (42, 25, 5, 4), (68, 25, 5, 4)])
    b.restyle(38, 18, 72, 34, floor="stone", wall="cliff")
    zone.add_subzone("The Naga Shrine", 37, 17, 36, 18)

    # --- Naga Sanctum (boss) ---
    b.corridor([(55, 18), (55, 15)], width=2)
    b.rect(36, 2, 74, 15, chamfer=3)
    b.restyle(36, 1, 74, 16, floor="stone", wall="cliff")
    zone.add_subzone("The Naga Sanctum", 34, 0, 42, 18)

    # --- Markers ---
    zone.set_tile(*entrance, "portal", "interaction")
    for pos in (pirate, crab, guardian):
        zone.set_tile(pos[0], pos[1], "boss_marker", "interaction")
    chests = [(44, 5), (14, 68)]
    for cx, cy in chests:
        zone.set_tile(cx, cy, "chest", "interaction")
    zone.boss_position = guardian
    zone.boss_positions = [
        (crab[0], crab[1], "Giant Crab"),
        (pirate[0], pirate[1], "Undead Pirate Captain"),
        (guardian[0], guardian[1], "Naga Shrine Guardian"),
    ]

    # --- Props ---
    # Landing + Flooded Hall
    b.prop(GRO + "naga_column.png", 47, 83, 5, solid="core")
    b.prop(GRO + "naga_column.png", 63, 83, 5, solid="core")
    b.prop(GRO + "glow_coral.png", 50, 90, 3)
    b.prop(GRO + "barnacle_pillar.png", 45, 62, 5, solid="core")
    b.prop(GRO + "barnacle_pillar.png", 66, 62, 5, solid="core")
    b.prop(GRO + "serpent_skeleton.png", 47, 72, 6)
    b.prop(GRO + "glow_coral.png", 68, 72, 3)
    b.prop(GRO + "tide_pool.png", 58, 59, 3)
    # Pearl Nook
    b.prop(GRO + "giant_clam.png", 20, 66, 3)
    b.prop(GRO + "treasure_chest.png", 25, 72, 2)
    b.prop(GRO + "anchor.png", 15, 72, 3)
    b.prop(GRO + "glow_coral.png", 12, 66, 3)
    # Kelp Garden
    b.prop(GRO + "kelp_stalks.png", 88, 66, 4)
    b.prop(GRO + "kelp_stalks.png", 96, 70, 4)
    b.prop(GRO + "kelp_stalks.png", 90, 73, 4)
    b.prop(GRO + "tide_pool.png", 95, 64, 3)
    # Shipwreck Cove
    b.prop(GRO + "ship_bow.png", 16, 47, 11, solid="core")
    b.prop(GRO + "ship_cannon.png", 29, 44, 3, solid="core")
    b.prop(GRO + "pirate_skeletons.png", 27, 54, 3)
    b.prop(GRO + "ship_wheel.png", 14, 55, 3)
    b.prop(GRO + "barrel_stack.png", 30, 40, 3, solid="core")
    b.prop(GRO + "fishing_net.png", 12, 43, 3)
    b.prop(GRO + "anchor.png", 19, 56, 3)
    # Crab Den
    b.prop(GRO + "crab_nest.png", 94, 45, 4)
    b.prop(GRO + "crab_molt.png", 82, 44, 3)
    b.prop(GRO + "tide_pool.png", 82, 55, 4)
    b.prop(GRO + "barnacle_pillar.png", 98, 52, 5, solid="core")
    b.prop(GRO + "glow_coral.png", 79, 40, 3)
    b.prop(GRO + "crab_nest.png", 98, 40, 3)
    # Naga Shrine
    b.prop(GRO + "shell_altar.png", 47, 23, 5, solid="core")
    b.prop(GRO + "shell_altar.png", 63, 23, 5, solid="core")
    b.prop(GRO + "naga_priestess_statue.png", 41, 29, 6, solid="core")
    b.prop(GRO + "naga_priestess_statue.png", 69, 29, 6, solid="core")
    b.prop(GRO + "naga_rune_stone.png", 55, 21, 4)
    b.prop(GRO + "blue_brazier.png", 49, 31, 4, solid="core")
    b.prop(GRO + "blue_brazier.png", 61, 31, 4, solid="core")
    # Naga Sanctum
    b.prop(GRO + "naga_throne.png", 55, 7, 9, solid="core")
    for x in (41, 69):
        b.prop(GRO + "naga_warrior_statue.png", x, 10, 6, solid="core")
        b.prop(GRO + "naga_column.png", x, 5, 5, solid="core")
    b.prop(GRO + "blue_brazier.png", 46, 13, 4, solid="core")
    b.prop(GRO + "blue_brazier.png", 64, 13, 4, solid="core")
    b.prop(GRO + "shackle_frame.png", 48, 6, 4)
    b.prop(GRO + "naga_rune_stone.png", 62, 6, 4)

    b.verify(entrance, [(*pirate, "pirate"), (*crab, "crab"), (*guardian, "guardian")]
             + [(cx, cy, "chest") for cx, cy in chests])
    return zone


RF = DP + "rf_"


def generate_ragefire_chasm():
    """Ragefire Chasm (240x220): the volcanic cultist warren under Orgrimmar.

    Cleft Gate (portal, quest NPCs) -> Trogg Warrens (trash) -> Searing Blade
    Antechamber (cultists) which forks: WEST to Oggleflint's Den (optional
    boss + Maur's corpse), NORTH across Taragaman's lava lake (only the stone
    bridges are walkable; lava tiles block) -> Jergosh's Ritual Chamber ->
    Bazzalan's Walkway.  All boss/NPC/portal coordinates are unchanged from
    the generator-driven layout, so spawns, quests and the Orgrimmar link keep
    working (portal (120, 214) <-> Orgrimmar (22, 168)).
    """
    zone = Tilemap("Ragefire Chasm", 240, 220,
                   "A volcanic cavern beneath Orgrimmar. Troggs and the "
                   "Searing Blade cult have made this their territory.")
    zone.is_cave = True
    zone.region = "Orgrimmar"
    b = Builder(zone, wall_id="wall", floor_id="stone")

    entrance = (120, 214)
    oggleflint = (55, 100)
    taragaman = (90, 60)
    jergosh = (62, 12)
    bazzalan = (120, 12)

    # --- Cleft Gate: entrance hall, quest NPCs at (112,205) and (128,205) ---
    b.rect(102, 194, 138, 216, chamfer=4)
    zone.add_subzone("The Cleft Gate", 100, 192, 40, 26)

    # --- winding tunnel + Trogg Warrens ---
    b.corridor([(120, 194), (118, 186), (106, 181), (100, 175)], width=1)
    b.lobes([(95, 166, 17, 11), (82, 160, 7, 6), (107, 157, 7, 5), (86, 173, 7, 4)], base="dirt")
    zone.add_subzone("The Trogg Warrens", 76, 150, 44, 32)

    # optional mining spur west of the warrens (ore cart, tool racks)
    b.corridor([(80, 166), (64, 168)], width=1)
    b.lobes([(54, 168, 11, 7)], base="grass")
    b.restyle(44, 160, 66, 176, wall="rock")
    zone.add_subzone("The Ore Spur", 42, 160, 26, 18)

    # --- Searing Blade Antechamber (cultists) ---
    b.corridor([(100, 156), (110, 147), (118, 139)], width=1)
    b.rect(106, 118, 142, 138, chamfer=3, base="path")
    b.restyle(104, 116, 144, 140, wall="rock")
    zone.add_subzone("Searing Blade Antechamber", 104, 116, 40, 24)

    # --- WEST: Oggleflint's Den (optional) ---
    b.corridor([(108, 126), (92, 118), (78, 110)], width=1)
    b.lobes([(60, 105, 17, 12), (48, 98, 8, 6), (71, 112, 7, 5), (52, 112, 6, 4)], base="dirt")
    zone.add_subzone("Oggleflint's Den", 42, 92, 36, 28)

    # --- NORTH: Taragaman's lava lake ---
    b.corridor([(124, 118), (110, 102), (96, 86), (90, 80)], width=1)
    b.rect(67, 41, 113, 79, chamfer=6, base="sand")
    b.lobes([(90, 60, 21, 17)], base="lava")                 # the lake (blocks movement)
    b.rect(89, 41, 91, 80, base="stone")                     # N-S bridge
    b.rect(67, 59, 113, 61, base="stone")                    # E-W bridge
    b.lobes([(90, 60, 6, 5)], base="stone")                  # boss platform
    b.restyle(65, 39, 115, 81, wall="cliff")
    zone.add_subzone("Taragaman's Chamber", 66, 40, 50, 42)

    # --- Jergosh's Ritual Chamber ---
    b.corridor([(90, 42), (84, 33), (74, 26), (66, 21)], width=1)
    b.rect(46, 4, 84, 24, chamfer=3, base="path")
    b.restyle(44, 2, 86, 26, wall="rock")
    zone.add_subzone("Jergosh's Chamber", 44, 2, 44, 26)

    # --- Bazzalan's Walkway ---
    b.corridor([(80, 14), (104, 14)], width=1)
    b.rect(102, 4, 138, 22, chamfer=3, base="stone")
    b.restyle(100, 2, 140, 24, wall="cliff")
    zone.add_subzone("Bazzalan's Walkway", 100, 2, 40, 24)

    # --- Markers (coordinates are contracts) ---
    zone.set_tile(*entrance, "portal", "interaction")
    for pos in (oggleflint, taragaman, jergosh, bazzalan):
        zone.set_tile(pos[0], pos[1], "boss_marker", "interaction")
    for pos in ((65, 108), (112, 205), (128, 205)):
        zone.set_tile(pos[0], pos[1], "npc", "interaction")
    chests = [(126, 16), (50, 168), (48, 104)]
    for cx, cy in chests:
        zone.set_tile(cx, cy, "chest", "interaction")
    zone.boss_positions = [
        (oggleflint[0], oggleflint[1], "Oggleflint"),
        (taragaman[0], taragaman[1], "Taragaman the Hungerer"),
        (jergosh[0], jergosh[1], "Jergosh the Invoker"),
        (bazzalan[0], bazzalan[1], "Bazzalan"),
        # optional named rares (tools/build_ragefire_content.py)
        (56, 169, "Grulgash the Pitbreaker"),        # Ore Spur
        (124, 132, "Acolyte Zhurra Bloodhex"),       # Antechamber, behind the altar
        (110, 44, "Cinderfang"),                     # NE shore of Taragaman's lake
    ]
    zone.boss_position = taragaman

    # --- Props: Cleft Gate ---
    b.prop(RF + "cult_banner.png", 106, 200, 7, solid="core")
    b.prop(RF + "cult_banner.png", 134, 200, 7, solid="core")
    b.prop(RF + "brazier.png", 108, 210, 5, solid="core")
    b.prop(RF + "brazier.png", 132, 210, 5, solid="core")
    b.prop(RF + "supply_crates.png", 114, 200, 4, solid="core")
    b.prop(RF + "supply_crates.png", 126, 200, 4, solid="core")
    b.prop(RF + "skull_spears.png", 120, 198, 4)
    b.prop(RF + "lava_fissure.png", 106, 212, 3)
    # --- Trogg Warrens ---
    b.prop(RF + "trogg_tent.png", 86, 165, 6, solid="core")
    b.prop(RF + "trogg_tent.png", 102, 162, 6, solid="core")
    b.prop(RF + "trogg_nest.png", 92, 173, 4)
    b.prop(RF + "trogg_nest.png", 108, 169, 4)
    b.prop(RF + "trogg_totem.png", 80, 158, 6, solid="core")
    b.prop(RF + "trogg_totem.png", 110, 154, 6, solid="core")
    b.prop(RF + "skull_spears.png", 96, 159, 4)
    b.prop(RF + "lava_stalagmite.png", 82, 175, 6, solid="core")
    b.prop(RF + "lava_fissure.png", 100, 170, 3)
    # --- Ore Spur ---
    b.prop(RF + "ore_cart.png", 52, 166, 3, solid="core")
    b.prop(RF + "tool_rack.png", 60, 164, 4, solid="core")
    b.prop(RF + "tool_rack.png", 48, 172, 4, solid="core")
    b.prop(RF + "supply_crates.png", 58, 172, 3, solid="core")
    # --- Antechamber ---
    b.prop(RF + "cult_circle.png", 124, 128, 5)
    b.prop(RF + "sacrificial_altar.png", 124, 123, 6, solid="core")
    b.prop(RF + "prison_cage.png", 111, 125, 5, solid="core")
    b.prop(RF + "prison_cage.png", 137, 125, 5, solid="core")
    b.prop(RF + "cult_banner.png", 112, 135, 7, solid="core")
    b.prop(RF + "cult_banner.png", 136, 135, 7, solid="core")
    b.prop(RF + "brazier.png", 118, 137, 5, solid="core")
    b.prop(RF + "brazier.png", 130, 137, 5, solid="core")
    b.prop(RF + "shackle_frame.png", 140, 134, 5)
    # --- Oggleflint's Den ---
    b.prop(RF + "trogg_tent.png", 49, 104, 6, solid="core")
    b.prop(RF + "trogg_nest.png", 66, 100, 4)
    b.prop(RF + "skull_spears.png", 70, 112, 4)
    b.prop(RF + "trogg_totem.png", 62, 97, 6, solid="core")
    b.prop(RF + "trogg_nest.png", 53, 113, 4)
    b.prop(RF + "lava_fissure.png", 71, 105, 3)
    # --- Taragaman's lake (props sit on rim/lava, never on the bridges) ---
    b.prop(RF + "lava_pool.png", 78, 50, 5)
    b.prop(RF + "lava_pool.png", 102, 70, 5)
    b.prop(RF + "lava_pool.png", 102, 50, 4)
    b.prop(RF + "lava_pool.png", 78, 70, 4)
    b.prop(RF + "obsidian_spikes.png", 72, 46, 5, solid="core")
    b.prop(RF + "obsidian_spikes.png", 108, 46, 5, solid="core")
    b.prop(RF + "lava_stalagmite.png", 72, 74, 6, solid="core")
    b.prop(RF + "lava_stalagmite.png", 108, 74, 6, solid="core")
    b.prop(RF + "steam_vent.png", 84, 77, 5, solid="core")
    b.prop(RF + "steam_vent.png", 96, 45, 5, solid="core")
    b.prop(RF + "golem_husk.png", 98, 57, 4)
    b.prop(RF + "basalt_bridge.png", 90, 53, 3)
    # --- Jergosh ---
    b.prop(RF + "summoning_circle.png", 62, 15, 6)
    b.prop(RF + "void_crystals.png", 52, 9, 4, solid="core")
    b.prop(RF + "void_crystals.png", 76, 9, 4, solid="core")
    b.prop(RF + "cult_banner.png", 50, 22, 7, solid="core")
    b.prop(RF + "cult_banner.png", 80, 22, 7, solid="core")
    b.prop(RF + "brazier.png", 58, 20, 5, solid="core")
    b.prop(RF + "brazier.png", 70, 20, 5, solid="core")
    b.prop(RF + "prison_cage.png", 78, 16, 5, solid="core")
    b.prop(RF + "void_crystals.png", 66, 6, 4, solid="core")
    # --- Bazzalan ---
    b.prop(RF + "obsidian_throne.png", 120, 8, 9, solid="core")
    b.prop(RF + "cult_banner.png", 108, 10, 7, solid="core")
    b.prop(RF + "cult_banner.png", 132, 10, 7, solid="core")
    b.prop(RF + "brazier.png", 110, 20, 5, solid="core")
    b.prop(RF + "brazier.png", 130, 20, 5, solid="core")
    b.prop(RF + "cult_circle.png", 120, 17, 5)
    b.prop(RF + "fallen_pillar.png", 106, 16, 4)
    b.prop(RF + "supply_crates.png", 129, 15, 3, solid="core")

    b.verify(entrance, [(*oggleflint, "oggleflint"), (*taragaman, "taragaman"),
                        (*jergosh, "jergosh"), (*bazzalan, "bazzalan"),
                        (65, 108, "npc"), (112, 205, "npc"), (128, 205, "npc")]
             + [(cx, cy, "chest") for cx, cy in chests])
    return zone
