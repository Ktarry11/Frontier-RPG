"""
Hand-built layouts for Durotar's six caves (2026-10-21):

  Dustwind Cave            80x65  scorpid burrow            (portal 40,61 / boss Gorge 40,12)
  Tiragarde Keep           90x80  stranded Kul Tiras keep   (portal 45,76 / boss Thalenvorde 45,9)
  Skull Rock              110x90  Burning Blade fel fort    (portal 55,86 / Neru 18,54 / Gazz'uz 55,12)
  Drygulch Ravine          95x75  open-air harpy canyon     (portal 47,71 / boss Vess'ra 47,12)
  Thunder Ridge            90x90  storm-lizard crag         (portal 45,86 / boss Broodmother 45,10)
  Sunken Grotto of the Deep 110x95 naga sea cave            (portal 55,92 / 3 bosses)

Same recipe as tools/handbuilt_vot_caves.py (CaveLayout: guarded props, flood-fill
QA, loops instead of dead ends) and the same painted-chunk registration, baked
by tools/bake_durotar_caves.py.

Prop rule (Kyle): less is more; props must be logical for the room; a few
centrepieces.  Every prop goes through CaveLayout.prop.
"""
import os

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import (CaveLayout, DP, _apply_pools,  # noqa: F401
                                       register_baked, pool_fields)

TK = "assets/tiles/tiragarde_keep/props/"
SR = "assets/tiles/skull_rock/props/"
BAKED = "assets/tiles/durotar_caves/{}/baked"


def _cave(name, w, h, desc, portal):
    zone = Tilemap(name, w, h, desc)
    zone.is_cave = True
    zone.region = "Durotar"
    zone.fixed_spawns = False
    return zone, CaveLayout(zone, portal)


def _finish(L, zone, portal, bosses, chests, extra_targets=()):
    """Mark portal / bosses / chests, pin bosses, run flood-fill QA."""
    L.mark("portal", *portal)
    for (x, y, _) in bosses:
        L.mark("boss_marker", x, y)
    for c in chests:
        L.mark("chest", *c)
    zone.boss_position = (bosses[0][0], bosses[0][1])
    zone.boss_positions = [(x, y, n) for (x, y, n) in bosses]


# =================================================================== DUSTWIND
DW_PORTAL = (40, 61)
DW_BOSS = (40, 12)
DW_CHESTS = [(40, 9), (8, 60), (74, 30), (69, 55)]
DW_POOLS = [(40, 41, 4.2, 3.0, 0.9)]


def build_dustwind():
    zone, L = _cave("Dustwind Cave", 80, 65,
                    "A sandy scorpid hive burrowed beneath Durotar's red hills.", DW_PORTAL)
    b = L.b
    # entrance in the south, boss in the north, three rings of loops between
    b.lobes([(40, 59, 9, 3), (33, 58, 3, 2), (47, 58, 3, 2)])                    # Burrow Mouth
    b.corridor([(40, 56), (40, 49)], width=3)
    b.lobes([(40, 41, 14, 7), (28, 39, 5, 4), (52, 39, 5, 4), (40, 33, 6, 3)])    # Sandstone Hall
    b.corridor([(28, 42), (21, 46), (16, 50), (14, 53)], width=2)                 # west route
    b.lobes([(14, 57, 9, 5), (8, 59, 3, 3), (20, 60, 3, 2)])                      # The Husk Den
    b.corridor([(27, 36), (21, 31), (17, 27)], width=2)                           # north-west route
    b.lobes([(15, 23, 10, 6), (8, 26, 3, 3)])                                     # Bone Gallery
    b.corridor([(19, 19), (25, 15), (31, 13)], width=2)                           # gallery -> lair (loop)
    b.corridor([(53, 38), (59, 34), (63, 31)], width=2)                           # east route
    b.lobes([(66, 26, 9, 6), (73, 29, 3, 3)])                                     # Egg Chamber
    b.corridor([(63, 21), (58, 17), (53, 14)], width=2)                           # eggs -> lair (loop)
    b.corridor([(47, 58), (54, 56), (59, 54)], width=2)                           # east larder branch
    b.lobes([(63, 52, 7, 4), (69, 55, 3, 2)])                                     # The Larder
    b.corridor([(64, 48), (65, 40), (66, 33)], width=2)                           # larder -> eggs (loop)
    b.corridor([(40, 31), (40, 20)], width=3)                                     # lair approach
    b.lobes([(40, 12, 13, 7), (30, 11, 5, 4), (50, 11, 5, 4), (40, 5, 6, 3)])     # Gorge's Lair
    _apply_pools(zone, DW_POOLS)

    for n, x, y, w, h in [("The Burrow Mouth", 28, 54, 24, 10), ("The Sandstone Hall", 22, 30, 36, 20),
                          ("The Husk Den", 4, 50, 22, 13), ("The Bone Gallery", 3, 16, 24, 15),
                          ("The Egg Chamber", 56, 20, 22, 15), ("The Larder", 56, 46, 18, 12),
                          ("Gorge's Lair", 24, 2, 34, 20)]:
        zone.add_subzone(n, x, y, w, h)
    zone.add_subzone("Dustwind Cave", 0, 0, zone.width, zone.height)

    _finish(L, zone, DW_PORTAL, [(DW_BOSS[0], DW_BOSS[1], "Gorge the Corpsegrinder")], DW_CHESTS)

    p = L.prop
    # burrow mouth: the hole you came in by, a torch left by the last recruit
    p("den_torch", 35, 59, 4)
    p("den_burrow_hole", 46, 58, 3)
    # sandstone hall: clay pillars hold the roof; a seep of water at the centre
    p("den_clay_pillar", 30, 38, 5, solid="core")
    p("den_clay_pillar", 50, 38, 5, solid="core")
    p("den_stalagmite_pair", 40, 34, 4, solid="core")
    p("vot_scorpid_burrow", 33, 45, 3)
    # husk den: shed carapaces and what the scorpids ate
    p("den_chitin_husk", 12, 56, 3)
    p("den_chitin_husk", 18, 59, 3)
    p("den_leg_bones", 10, 62, 2)
    p("den_dead_recruit", 15, 61, 3)
    p("den_backpack", 11, 61, 2)
    # bone gallery
    p("vot_beast_ribcage", 14, 24, 3)
    p("den_leg_bones", 10, 22, 2)
    p("den_rock_rubble", 20, 26, 2)
    p("bone_pile", 17, 21, 3, where=SR)
    # egg chamber
    p("den_egg_cluster", 66, 24, 4, solid="core")
    p("den_egg_cluster", 71, 28, 4, solid="core")
    p("den_eggshell_pile", 62, 27, 2)
    p("den_web_boulder", 69, 22, 3)
    # larder
    p("den_buried_crate", 61, 54, 3)
    p("den_chest_sack", 66, 55, 3)
    p("cocoon_victim", 65, 50, 4)
    # gorge's lair: the nest mound is the centrepiece
    p("den_nest_mound", 40, 7, 6, solid="core", avoid=1)
    p("den_egg_cluster", 31, 10, 4, solid="core")
    p("den_egg_cluster", 49, 10, 4, solid="core")
    p("den_stalagmites", 34, 15, 4, solid="core")
    p("den_stalagmites", 46, 15, 4, solid="core")

    L.finish([DW_PORTAL, DW_BOSS] + DW_CHESTS)
    return zone, L


# ================================================================== TIRAGARDE
TG_PORTAL = (45, 76)
TG_BOSS = (45, 9)
TG_CHESTS = [(38, 6), (9, 52), (81, 52), (9, 28), (82, 28)]


def build_tiragarde():
    zone, L = _cave("Tiragarde Keep", 90, 80,
                    "A storm-wrecked Kul Tiras garrison keep on Durotar's south coast.", TG_PORTAL)
    b = L.b
    b.rect(36, 70, 54, 77, chamfer=2)                                              # Gatehouse Yard
    b.corridor([(45, 71), (45, 62)], width=4)                                      # gate passage
    b.rect(27, 48, 63, 63, chamfer=3)                                              # Outer Courtyard
    b.rect(7, 50, 21, 65, chamfer=2)                                               # West Barracks
    b.corridor([(20, 57), (28, 57)], width=3)
    b.rect(69, 50, 83, 65, chamfer=2)                                              # East Barracks
    b.corridor([(62, 57), (70, 57)], width=3)
    b.corridor([(14, 51), (14, 41)], width=3)                                      # barracks -> armory
    b.rect(7, 26, 22, 42, chamfer=2)                                               # The Armory
    b.corridor([(76, 51), (76, 41)], width=3)                                      # barracks -> ruined wing
    b.rect(68, 26, 83, 42, chamfer=3)                                              # The Ruined Wing
    b.corridor([(45, 49), (45, 38)], width=4)                                      # keep gate
    b.rect(28, 25, 62, 39, chamfer=3)                                              # Hall of Banners
    b.corridor([(21, 34), (29, 33)], width=3)                                      # armory -> banner hall (loop)
    b.corridor([(69, 34), (61, 33)], width=3)                                      # ruined wing -> banner hall (loop)
    b.corridor([(45, 27), (45, 15)], width=4)                                      # grand stair
    b.rect(24, 4, 66, 17, chamfer=3)                                               # The Great Hall
    b.corridor([(15, 28), (15, 11), (26, 11)], width=2)                            # armory -> great hall (west stair)
    b.corridor([(75, 28), (75, 11), (64, 11)], width=2)                            # ruined wing -> great hall (east stair)

    for n, x, y, w, h in [("The Gatehouse Yard", 34, 68, 24, 11), ("The Outer Courtyard", 26, 46, 40, 19),
                          ("The West Barracks", 5, 48, 19, 19), ("The East Barracks", 67, 48, 19, 19),
                          ("The Armory", 5, 24, 19, 20), ("The Ruined Wing", 66, 24, 19, 20),
                          ("The Hall of Banners", 26, 23, 40, 18), ("The Great Hall", 22, 2, 46, 17)]:
        zone.add_subzone(n, x, y, w, h)
    zone.add_subzone("Tiragarde Keep", 0, 0, zone.width, zone.height)

    _finish(L, zone, TG_PORTAL, [(TG_BOSS[0], TG_BOSS[1], "Captain Thalenvorde")], TG_CHESTS)

    p = L.prop
    # gatehouse: the drawbridge IS the way in; banners flank it, barrels left by the garrison
    p("tiragarde_drawbridge", 45, 77, 4, where=TK, near_ok=True)
    p("tiragarde_banner_pole", 38, 73, 5, where=TK)
    p("tiragarde_banner_pole", 52, 73, 5, where=TK)
    p("tiragarde_barrel_crate_cluster", 40, 76, 3, where=TK)
    # outer courtyard: a fallen tower, a war table, rubble, banners of a lost fleet
    p("tiragarde_tower_collapsed", 33, 53, 7, where=TK, solid="core")
    p("tiragarde_tower_intact", 57, 53, 7, where=TK, solid="core")
    p("tiragarde_war_table", 45, 58, 3, where=TK, avoid=1)
    p("tiragarde_rubble_pile", 31, 61, 2, where=TK)
    p("tiragarde_rubble_beam", 59, 61, 2, where=TK)
    # west barracks: bunks (weapon racks), supplies, a caged hound
    p("weapon_rack", 14, 55, 4)
    p("weapon_rack", 18, 55, 4)
    p("tiragarde_barrel_crate_cluster", 9, 63, 3, where=TK)
    p("kennel_cage_worg", 18, 62, 4, solid="core")
    # east barracks
    p("weapon_rack", 73, 55, 4)
    p("weapon_rack", 77, 55, 4)
    p("tiragarde_barrel_crate_cluster", 81, 63, 3, where=TK)
    p("kennel_cage_empty", 72, 62, 4, solid="core")
    # armory: scaffolding, racks, crates
    p("tiragarde_scaffold", 12, 33, 6, where=TK, solid="core")
    p("weapon_rack", 18, 30, 4)
    p("tiragarde_barrel_crate_cluster", 10, 40, 3, where=TK)
    p("grotto_ship_cannon", 19, 39, 3)
    # ruined wing: a collapsed section, scorched rubble
    p("tiragarde_ruined_wall_section", 74, 31, 6, where=TK, solid="core")
    p("tiragarde_rubble_pile", 80, 38, 3, where=TK)
    p("tiragarde_rubble_beam", 72, 39, 2, where=TK)
    p("broken_column", 79, 32, 4)
    # hall of banners: ranks of banner poles, columns
    p("tiragarde_banner_pole", 33, 30, 5, where=TK)
    p("tiragarde_banner_pole", 57, 30, 5, where=TK)
    p("tiragarde_banner_pole", 38, 37, 5, where=TK)
    p("tiragarde_banner_pole", 52, 37, 5, where=TK)
    p("broken_column", 36, 31, 4, solid="core")
    p("broken_column", 54, 31, 4, solid="core")
    p("broken_column", 36, 36, 4, solid="core")
    p("broken_column", 54, 36, 4, solid="core")
    # great hall: the captain's table, banners, ship's wheel mounted as a trophy
    p("banquet_table", 45, 14, 4, solid="core", avoid=2)
    p("broken_column", 32, 7, 4, solid="core")
    p("broken_column", 58, 7, 4, solid="core")
    p("candelabra", 34, 11, 4)
    p("candelabra", 56, 11, 4)
    p("tiragarde_banner_pole", 29, 14, 5, where=TK)
    p("tiragarde_banner_pole", 61, 14, 5, where=TK)
    p("grotto_ship_wheel", 45, 5, 3, avoid=1)

    L.finish([TG_PORTAL, TG_BOSS] + TG_CHESTS)
    return zone, L


# ================================================================ SKULL ROCK
SK_PORTAL = (55, 86)
SK_NERU = (18, 54)
SK_GAZZUZ = (55, 12)
SK_CHESTS = [(13, 61), (97, 62), (22, 27), (97, 31), (49, 8)]


def build_skull_rock():
    zone, L = _cave("Skull Rock", 110, 90,
                    "The Burning Blade's cliff-side fel fortress above Durotar's northeast coast.", SK_PORTAL)
    b = L.b
    b.lobes([(55, 83, 10, 4), (46, 81, 4, 3), (64, 81, 4, 3)])                      # Cliff Mouth
    b.corridor([(55, 78), (55, 71)], width=3)
    b.lobes([(55, 64, 15, 7), (41, 62, 5, 4), (69, 62, 5, 4)])                      # Guard Hall
    b.corridor([(40, 62), (33, 60), (27, 58)], width=3)                             # to the forge
    b.lobes([(20, 55, 11, 8), (11, 52, 4, 3), (14, 62, 5, 3), (28, 49, 4, 3)])      # Neru's Forge
    b.corridor([(70, 62), (78, 60), (85, 58)], width=3)                             # to the kennels
    b.lobes([(92, 56, 11, 8), (101, 52, 4, 3), (99, 63, 5, 3)])                     # The Kennels
    b.corridor([(55, 57), (55, 51)], width=3)                                       # north to the terrace
    b.lobes([(55, 43, 19, 8), (39, 41, 6, 5), (71, 41, 6, 5)])                      # Lava Terrace
    b.lobes([(55, 40, 7, 3)], base="lava")                                          # the lava pool in its middle
    b.corridor([(25, 48), (31, 44), (37, 41)], width=2)                             # forge -> terrace (loop)
    b.corridor([(87, 50), (81, 45), (75, 41)], width=2)                             # kennels -> terrace (loop)
    b.corridor([(55, 35), (55, 27)], width=3)                                       # sanctum approach
    b.lobes([(55, 17, 17, 9), (41, 15, 5, 5), (69, 15, 5, 5), (55, 8, 8, 3)])       # Gazz'uz's Sanctum
    b.lobes([(46, 17, 2, 3), (64, 17, 2, 3)], base="lava")                          # braziers' basins
    b.corridor([(18, 46), (18, 38), (21, 33)], width=2)                             # forge -> library
    b.lobes([(22, 28, 10, 6), (13, 30, 3, 3)])                                      # Warlock Library
    b.corridor([(30, 25), (38, 21), (42, 18)], width=2)                             # library -> sanctum (loop)
    b.corridor([(95, 48), (92, 40), (90, 34)], width=2)                             # kennels -> bone pit
    b.lobes([(89, 28, 10, 6), (97, 31, 3, 3)])                                      # The Bone Pit
    b.corridor([(80, 24), (74, 20), (70, 17)], width=2)                             # pit -> sanctum (loop)

    for n, x, y, w, h in [("The Cliff Mouth", 42, 78, 28, 11), ("The Guard Hall", 34, 56, 44, 16),
                          ("Neru's Forge", 6, 44, 28, 24), ("The Kennels", 80, 46, 28, 22),
                          ("The Lava Terrace", 32, 33, 48, 20), ("The Warlock Library", 8, 22, 28, 14),
                          ("The Bone Pit", 76, 22, 28, 14), ("Gazz'uz's Sanctum", 34, 3, 44, 24)]:
        zone.add_subzone(n, x, y, w, h)
    zone.add_subzone("Skull Rock", 0, 0, zone.width, zone.height)

    _finish(L, zone, SK_PORTAL,
            [(SK_NERU[0], SK_NERU[1], "Neru Fireblade"), (SK_GAZZUZ[0], SK_GAZZUZ[1], "Gazz'uz")], SK_CHESTS)

    p = L.prop
    # cliff mouth: banners and a skull-pile warning
    p("bbc_banner", 47, 80, 5)
    p("bbc_banner", 63, 80, 5)
    p("skull_pile", 52, 82, 3)
    # guard hall: braziers and weapon racks, the guards' own table
    p("ritual_brazier", 46, 60, 4, where=SR, solid="core")
    p("ritual_brazier", 64, 60, 4, where=SR, solid="core")
    p("weapon_rack", 43, 66, 4)
    p("weapon_rack", 67, 66, 4)
    p("bbc_tent", 69, 64, 5)
    # neru's forge: anvil-and-tools, molten leakage, the idol
    p("rf_tool_rack", 14, 51, 4)
    p("rf_ore_cart", 9, 54, 3)
    p("rf_lava_fissure", 17, 61, 3)
    p("bbc_idol", 24, 51, 4, solid="core", avoid=1)
    p("rf_supply_crates", 25, 59, 3)
    p("cracked_pillar", 28, 50, 4, where=SR, solid="core")
    # kennels: cages with worgs, bones, a feeding trough of skulls
    p("kennel_cage_worg", 88, 53, 4, solid="core")
    p("kennel_cage_empty", 96, 53, 4, solid="core")
    p("kennel_cage_worg", 93, 62, 4, solid="core")
    p("bone_pile", 100, 60, 3, where=SR)
    p("bbc_chains", 86, 62, 4)
    # lava terrace: spikes in the lava, rune pillar pair framing the road north
    p("lava_spikes", 47, 44, 4, where=SR, solid="core")
    p("bbc_rune_pillar", 49, 36, 5, solid="core")
    p("bbc_rune_pillar", 61, 36, 5, solid="core")
    p("rf_steam_vent", 42, 44, 3)
    p("bbc_obsidian_spikes", 70, 45, 4, solid="core")
    # warlock library: shelves, desk, summoning scribbles
    p("bbc_bookshelf", 18, 25, 5, solid="core")
    p("bbc_bookshelf", 26, 25, 5, solid="core")
    p("bbc_warlock_desk", 22, 31, 3, solid="core")
    p("bbc_candelabra", 14, 29, 4)
    # bone pit: a heap of skulls and spears (the Blade's tithe)
    p("rf_skull_spears", 87, 27, 4)
    p("skull_pile", 93, 31, 3)
    p("bone_pile", 84, 31, 3, where=SR)
    p("rf_sacrificial_altar", 90, 25, 5, solid="core", fraction=0.3)
    # gazz'uz's sanctum: the summoning circle at the centre, a throne, two braziers, banners
    p("bbc_summon_circle", 55, 18, 5, avoid=0)
    p("bbc_throne", 55, 7, 6, solid="core", avoid=2)
    p("bbc_fel_brazier", 44, 20, 4, solid="core")
    p("bbc_fel_brazier", 66, 20, 4, solid="core")
    p("bbc_banner", 41, 12, 5)
    p("bbc_banner", 69, 12, 5)
    p("rf_obsidian_spikes", 38, 18, 4, solid="core")
    p("rf_obsidian_spikes", 72, 18, 4, solid="core")

    L.finish([SK_PORTAL, SK_NERU, SK_GAZZUZ] + SK_CHESTS)
    return zone, L


# ================================================================== DRYGULCH
DG_PORTAL = (47, 71)
DG_BOSS = (47, 12)
DG_CHESTS = [(42, 6), (13, 36), (81, 37), (28, 18), (77, 25)]
DG_POOLS = [(47, 43, 4.2, 3.0, 1.1)]


def build_drygulch():
    zone, L = _cave("Drygulch Ravine", 95, 75,
                    "A twisting red-rock canyon where the Dustwind harpies keep their roosts.", DG_PORTAL)
    b = L.b
    b.lobes([(47, 68, 10, 4), (38, 66, 4, 3), (56, 66, 4, 3)])                      # Canyon Mouth
    b.corridor([(47, 64), (46, 58), (41, 53), (34, 49)], width=5)                   # Dry Wash (west leg)
    b.corridor([(46, 58), (53, 53), (60, 49), (65, 46)], width=4)                   # Dry Wash (east leg)
    b.lobes([(22, 42, 11, 8), (14, 37, 4, 4), (21, 50, 5, 3)])                      # The Harpy Roost
    b.lobes([(70, 43, 12, 8), (79, 39, 4, 4), (68, 52, 6, 3)])                      # Savage Camp
    b.lobes([(47, 42, 14, 8), (47, 36, 6, 3)])                                      # The Gulch Heart
    _apply_pools(zone, DG_POOLS, deep_ok=False, shallow_only=True)
    b.corridor([(47, 34), (47, 26)], width=5)                                       # north to the aerie
    b.corridor([(18, 33), (22, 30), (26, 27)], width=3)                             # roost -> witches
    b.lobes([(28, 22, 9, 7), (22, 27, 3, 3)])                                       # Storm-Witch Circle
    b.corridor([(35, 20), (40, 17)], width=3)                                       # witches -> aerie (loop)
    b.corridor([(74, 36), (72, 30)], width=3)                                       # camp -> bone wash
    b.lobes([(70, 24, 8, 6)])                                                       # The Bone Wash
    b.corridor([(64, 22), (58, 17)], width=3)                                       # bone wash -> aerie (loop)
    b.lobes([(47, 13, 15, 8), (35, 11, 5, 4), (59, 11, 5, 4), (47, 6, 8, 3)])       # Vess'ra's Aerie

    for n, x, y, w, h in [("The Canyon Mouth", 34, 62, 26, 12), ("The Dry Wash", 30, 46, 40, 17),
                          ("The Harpy Roost", 6, 32, 30, 22), ("The Savage Camp", 56, 34, 28, 22),
                          ("The Gulch Heart", 32, 32, 30, 16), ("The Storm-Witch Circle", 16, 14, 24, 18),
                          ("The Bone Wash", 60, 16, 22, 14), ("Vess'ra's Aerie", 30, 3, 36, 20)]:
        zone.add_subzone(n, x, y, w, h)
    zone.add_subzone("Drygulch Ravine", 0, 0, zone.width, zone.height)

    _finish(L, zone, DG_PORTAL, [(DG_BOSS[0], DG_BOSS[1], "Matriarch Vess'ra")], DG_CHESTS)

    p = L.prop
    # canyon mouth: a natural rock arch frames the way in, trail cairn marks the path
    p("vot_rock_arch", 47, 66, 6, avoid=1)
    p("vot_trail_cairn", 40, 69, 3)
    p("vot_mesa_pillar", 36, 65, 5, solid="core")
    p("vot_mesa_pillar", 57, 67, 5, solid="core")
    # dry wash: a dead tree, bleached bones where the wash floods
    p("vot_dead_tree", 41, 56, 4)
    p("vot_beast_ribcage", 52, 57, 3)
    p("vot_thornbush", 36, 52, 2)
    # harpy roost: nests on the ledge, bones of what they carried up
    p("rf_trogg_nest", 18, 39, 3)
    p("rf_trogg_nest", 25, 44, 3)
    p("bone_pile", 16, 47, 3, where=SR)
    p("vot_dead_tree", 12, 41, 4)
    p("vot_mesa_pillar", 28, 37, 5, solid="core")
    # savage camp: tents, a totem, drum, hide rack - the Dustwind savages
    p("rf_trogg_tent", 66, 42, 5, solid="core")
    p("rf_trogg_tent", 75, 46, 5, solid="core")
    p("vot_totem_pole", 71, 40, 5, solid="core", avoid=1)
    p("vot_war_drum", 64, 48, 3)
    p("vot_hide_rack", 78, 44, 3)
    p("vot_fire_pit", 70, 47, 3)
    # gulch heart: the seep is the centrepiece; reeds, boulder, cairn
    p("vot_spring_boulder", 41, 40, 4, solid="core")
    p("vot_reeds", 53, 46, 3)
    p("vot_reeds", 42, 46, 3)
    p("vot_thornbush", 54, 38, 2)
    # storm-witch circle: a ritual ring and a brazier, bones for the offering
    p("ritual_circle", 28, 22, 4, avoid=0)
    p("spirit_brazier", 22, 19, 4, solid="core")
    p("spirit_brazier", 34, 25, 4, solid="core")
    p("vot_trail_cairn", 33, 19, 3)
    # bone wash
    p("vot_beast_ribcage", 68, 25, 3)
    p("skull_pile", 74, 22, 3)
    p("vot_dead_tree", 66, 20, 4)
    # aerie: nests all around, the matriarch's pillars frame the throne ledge
    p("rf_trogg_nest", 38, 15, 3)
    p("rf_trogg_nest", 56, 15, 3)
    p("rf_trogg_nest", 47, 7, 4, solid="core", avoid=2)
    p("vot_mesa_pillar", 36, 15, 5, solid="core")
    p("vot_mesa_pillar", 58, 15, 5, solid="core")
    p("bone_pile", 42, 9, 3, where=SR)
    p("vot_beast_ribcage", 53, 10, 3)

    L.finish([DG_PORTAL, DG_BOSS] + DG_CHESTS)
    return zone, L


# ============================================================= THUNDER RIDGE
TR_PORTAL = (45, 86)
TR_BOSS = (45, 10)
TR_CHESTS = [(40, 6), (9, 54), (79, 54), (14, 28), (76, 28)]
TR_POOLS = [(19, 58, 5.2, 3.4, 0.6), (72, 58, 4.0, 3.0, 1.9)]


def build_thunder_ridge():
    zone, L = _cave("Thunder Ridge", 90, 90,
                    "A storm-wracked crag where the thunder lizards nest above Durotar.", TR_PORTAL)
    b = L.b
    b.lobes([(45, 83, 11, 4), (36, 81, 4, 3), (54, 81, 4, 3)])                      # Ridge Foot
    b.corridor([(45, 79), (45, 72)], width=4)
    b.lobes([(45, 64, 15, 8), (32, 62, 5, 4), (58, 62, 5, 4)])                      # Gravel Basin
    b.corridor([(31, 62), (25, 60)], width=3)
    b.lobes([(19, 58, 10, 7), (12, 54, 4, 3), (15, 64, 4, 3)])                      # Thunder Pools
    b.corridor([(59, 62), (65, 60)], width=3)
    b.lobes([(72, 58, 10, 7), (79, 54, 4, 3), (70, 65, 4, 2)])                      # Hatchling Terraces
    _apply_pools(zone, TR_POOLS, shallow_only=True)
    b.corridor([(45, 57), (45, 47)], width=4)                                       # the climb
    b.lobes([(45, 40, 17, 7), (30, 38, 5, 4), (60, 38, 5, 4)])                      # Storm Ledge
    b.corridor([(20, 52), (26, 46), (31, 41)], width=3)                             # pools -> ledge (loop)
    b.corridor([(73, 52), (66, 46), (61, 41)], width=3)                             # terraces -> ledge (loop)
    b.corridor([(45, 33), (45, 19)], width=4)                                       # mesa walk
    b.corridor([(29, 36), (25, 32), (23, 29)], width=3)
    b.lobes([(22, 25, 10, 7), (14, 28, 3, 3)])                                      # Stormbinder Altar
    b.corridor([(30, 22), (36, 18)], width=3)                                       # altar -> eyrie (loop)
    b.corridor([(61, 36), (65, 31), (67, 28)], width=3)
    b.lobes([(68, 25, 10, 7), (76, 28, 3, 3)])                                      # Broodnest Crown
    b.corridor([(60, 21), (55, 17)], width=3)                                       # crown -> eyrie (loop)
    b.lobes([(45, 12, 16, 8), (33, 11, 5, 4), (57, 11, 5, 4), (45, 5, 7, 3)])       # Broodmother's Eyrie

    for n, x, y, w, h in [("The Ridge Foot", 32, 78, 26, 11), ("The Gravel Basin", 28, 56, 36, 16),
                          ("The Thunder Pools", 3, 46, 28, 24), ("The Hatchling Terraces", 60, 48, 30, 22),
                          ("The Storm Ledge", 24, 32, 44, 16), ("The Stormbinder Altar", 8, 16, 28, 20),
                          ("The Broodnest Crown", 56, 16, 28, 20), ("The Broodmother's Eyrie", 28, 2, 36, 20)]:
        zone.add_subzone(n, x, y, w, h)
    zone.add_subzone("Thunder Ridge", 0, 0, zone.width, zone.height)

    _finish(L, zone, TR_PORTAL, [(TR_BOSS[0], TR_BOSS[1], "Thunder Broodmother")], TR_CHESTS)

    p = L.prop
    # ridge foot: the ridge stones frame the way up
    p("vot_mesa_pillar", 36, 83, 5, solid="core")
    p("vot_mesa_pillar", 54, 83, 5, solid="core")
    p("vot_trail_cairn", 45, 80, 3)
    # gravel basin: scree, a dead tree struck by lightning, a scorched log
    p("vot_dead_tree", 38, 66, 4)
    p("vot_fallen_log", 52, 68, 3)
    p("den_rock_rubble", 45, 60, 2)
    p("vot_beast_ribcage", 57, 65, 3)
    # thunder pools: a waterfall boulder, reeds, spring
    p("vot_spring_boulder", 12, 56, 4)
    p("vot_reeds", 24, 62, 3)
    p("vot_reeds", 14, 52, 3)
    p("den_stalagmite_pair", 25, 54, 4, solid="core")
    # hatchling terraces: egg clutches where the hatchlings spill out
    p("den_egg_cluster", 76, 56, 4, solid="core")
    p("den_egg_cluster", 69, 62, 4, solid="core")
    p("den_eggshell_pile", 74, 53, 2)
    p("vot_reeds", 66, 56, 3)
    # storm ledge: lightning-rod crystals, a vent, bones
    p("rf_void_crystals", 36, 36, 4, solid="core")
    p("rf_void_crystals", 54, 36, 4, solid="core")
    p("rf_steam_vent", 45, 42, 3, avoid=1)
    p("vot_beast_ribcage", 38, 43, 3)
    p("den_stalagmites", 28, 43, 4, solid="core")
    p("den_stalagmites", 62, 43, 4, solid="core")
    # stormbinder altar: ritual circle and braziers
    p("ritual_circle", 22, 26, 4, avoid=0)
    p("twilight_altar", 22, 21, 4, solid="core")
    p("spirit_brazier", 16, 25, 4, solid="core")
    p("spirit_brazier", 28, 29, 4, solid="core")
    # broodnest crown: the broodmother's guard clutches
    p("den_egg_cluster", 66, 24, 4, solid="core")
    p("den_egg_cluster", 72, 28, 4, solid="core")
    p("den_nest_mound", 72, 21, 5, solid="core")
    # eyrie: the nest, crystals, scattered bones
    p("den_nest_mound", 45, 6, 6, solid="core", avoid=1)
    p("den_egg_cluster", 34, 10, 4, solid="core")
    p("den_egg_cluster", 56, 10, 4, solid="core")
    p("rf_void_crystals", 38, 16, 4, solid="core")
    p("rf_void_crystals", 52, 16, 4, solid="core")
    p("bone_pile", 45, 15, 3, where=SR)

    L.finish([TR_PORTAL, TR_BOSS] + TR_CHESTS)
    return zone, L


# ========================================================= SUNKEN GROTTO
SG_PORTAL = (55, 92)
SG_CRAB = (88, 50)
SG_PIRATE = (22, 50)
SG_GUARDIAN = (55, 10)
SG_CHESTS = [(44, 6), (96, 44), (13, 46), (14, 82), (96, 75)]
SG_POOLS = [(55, 70, 7.0, 3.4, 0.8), (88, 54, 5.0, 3.0, 1.4)]


def build_grotto():
    zone, L = _cave("Sunken Grotto of the Deep", 110, 95,
                    "A drowned sea-cave beneath Durotar's northeast coast, claimed by naga.", SG_PORTAL)
    b = L.b
    b.lobes([(55, 89, 11, 4), (46, 87, 4, 3), (64, 87, 4, 3)])                      # Tideway Mouth
    b.corridor([(55, 86), (55, 77)], width=4)
    b.lobes([(55, 70, 18, 8), (41, 68, 5, 4), (69, 68, 5, 4)])                      # The Flooded Hall
    b.corridor([(40, 66), (32, 62), (27, 58)], width=3)                             # to the cove
    b.lobes([(25, 50, 14, 9), (14, 46, 4, 4), (18, 57, 5, 3)])                      # Shipwreck Cove
    b.corridor([(70, 66), (78, 62), (83, 58)], width=3)                             # to the crab den
    b.lobes([(88, 50, 13, 10), (97, 45, 4, 4), (95, 57, 4, 3)])                     # The Crab Den
    b.corridor([(42, 72), (34, 75), (27, 77)], width=3)                             # to the pearl grotto
    b.lobes([(19, 79, 9, 6), (12, 75, 3, 3)])                                       # The Pearl Grotto
    b.corridor([(18, 73), (20, 66), (22, 59)], width=2)                             # pearl -> cove (loop)
    b.corridor([(68, 72), (76, 74), (82, 75)], width=3)                             # to the kelp garden
    b.lobes([(92, 76, 10, 6), (98, 71, 3, 3)])                                      # The Kelp Garden
    b.corridor([(94, 69), (95, 64), (95, 59)], width=2)                             # kelp -> den (loop)
    _apply_pools(zone, SG_POOLS, shallow_only=True)
    b.corridor([(26, 41), (30, 35), (40, 29), (46, 26)], width=3)                   # cove -> shrine
    b.corridor([(88, 40), (82, 34), (70, 29), (64, 26)], width=3)                   # den -> shrine
    b.rect(40, 19, 70, 30, chamfer=3)                                               # The Naga Shrine
    b.corridor([(55, 22), (55, 10)], width=4)                                       # throne approach
    b.rect(38, 3, 72, 12, chamfer=2)                                                # The Tidelord's Throne

    for n, x, y, w, h in [("The Tideway Mouth", 42, 84, 28, 10), ("The Flooded Hall", 34, 60, 42, 20),
                          ("Shipwreck Cove", 8, 40, 34, 22), ("The Crab Den", 74, 38, 34, 26),
                          ("The Pearl Grotto", 6, 70, 28, 14), ("The Kelp Garden", 80, 68, 28, 14),
                          ("The Naga Shrine", 38, 17, 36, 15), ("The Tidelord's Throne", 36, 2, 38, 12)]:
        zone.add_subzone(n, x, y, w, h)
    zone.add_subzone("Sunken Grotto of the Deep", 0, 0, zone.width, zone.height)

    _finish(L, zone, SG_PORTAL,
            [(SG_CRAB[0], SG_CRAB[1], "Giant Crab"), (SG_PIRATE[0], SG_PIRATE[1], "Undead Pirate Captain"),
             (SG_GUARDIAN[0], SG_GUARDIAN[1], "Naga Shrine Guardian")], SG_CHESTS)

    p = L.prop
    # mouth: the tide-washed entrance, a drowned anchor
    p("grotto_anchor", 47, 90, 4)
    p("grotto_glow_coral", 63, 89, 3)
    # flooded hall: the serpent that died here is the centrepiece; pillars frame the pool
    p("grotto_serpent_skeleton", 55, 76, 5, avoid=1)
    p("grotto_barnacle_pillar", 46, 66, 5, solid="core")
    p("grotto_barnacle_pillar", 64, 66, 5, solid="core")
    p("grotto_tide_pool", 41, 71, 3)
    p("grotto_glow_coral", 69, 72, 3)
    # shipwreck cove: the pirate captain's wreck
    p("grotto_ship_bow", 17, 49, 8, solid="core")
    p("grotto_ship_cannon", 28, 45, 3)
    p("grotto_ship_wheel", 31, 53, 3)
    p("grotto_barrel_stack", 23, 56, 3)
    p("grotto_pirate_skeletons", 20, 53, 3)
    p("grotto_fishing_net", 30, 49, 3)
    # crab den: nests, molts, a giant clam in the shallows
    p("grotto_crab_nest", 82, 45, 4, solid="core")
    p("grotto_crab_nest", 95, 52, 4, solid="core")
    p("grotto_crab_molt", 80, 55, 3)
    p("grotto_giant_clam", 90, 58, 3)
    p("grotto_barnacle_pillar", 79, 48, 4, solid="core")
    # pearl grotto: glow coral and clams
    p("grotto_giant_clam", 18, 78, 3)
    p("grotto_glow_coral", 13, 76, 3)
    p("glow_coral_cluster", 23, 82, 3)
    p("grotto_shell_altar", 20, 74, 3, solid="core")
    # kelp garden
    p("grotto_kelp_stalks", 92, 74, 4)
    p("grotto_kelp_stalks", 98, 78, 4)
    p("grotto_kelp_stalks", 87, 79, 4)
    p("grotto_glow_coral", 96, 72, 3)
    # naga shrine: columns, rune stones, statues
    p("grotto_naga_column", 44, 24, 5, solid="core")
    p("grotto_naga_column", 66, 24, 5, solid="core")
    p("grotto_naga_rune_stone", 55, 28, 4, solid="core", avoid=1)
    p("grotto_blue_brazier", 49, 22, 4, solid="core")
    p("grotto_blue_brazier", 61, 22, 4, solid="core")
    p("grotto_naga_priestess_statue", 42, 29, 5, solid="core")
    p("grotto_naga_warrior_statue", 68, 29, 5, solid="core")
    # throne hall
    p("grotto_naga_throne", 55, 6, 6, solid="core", avoid=2)
    p("naga_statue", 41, 9, 5, solid="core")
    p("naga_statue", 69, 9, 5, solid="core")
    p("grotto_shell_altar", 48, 8, 3, solid="core")
    p("grotto_shell_altar", 62, 8, 3, solid="core")

    L.finish([SG_PORTAL, SG_CRAB, SG_PIRATE, SG_GUARDIAN] + SG_CHESTS)
    return zone, L


# ======================================================== generate_* wrappers
def _gen(build, slug):
    zone, _ = build()
    register_baked(zone, BAKED.format(slug))
    return zone


def generate_dustwind_cave():
    return _gen(build_dustwind, "dustwind")


def generate_tiragarde_keep():
    return _gen(build_tiragarde, "tiragarde")


def generate_skull_rock():
    return _gen(build_skull_rock, "skull_rock")


def generate_drygulch_ravine():
    return _gen(build_drygulch, "drygulch")


def generate_thunder_ridge():
    return _gen(build_thunder_ridge, "thunder_ridge")


def generate_sunken_grotto_of_the_deep():
    return _gen(build_grotto, "grotto")


def ascii_preview(zone, step=2):
    rows = []
    for y in range(0, zone.height, step):
        r = ""
        for x in range(0, zone.width, step):
            if zone.interaction_layer[y][x] == "portal":
                r += "P"
            elif zone.interaction_layer[y][x] == "boss_marker":
                r += "B"
            elif zone.interaction_layer[y][x] == "chest":
                r += "c"
            elif zone.base_layer[y][x] == "lava":
                r += "~"
            elif zone.base_layer[y][x] in ("shallow_water", "deep_water"):
                r += "w"
            elif zone.is_walkable(x, y):
                r += "."
            else:
                r += "#"
        rows.append(r)
    return "\n".join(rows)
