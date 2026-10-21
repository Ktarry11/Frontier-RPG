"""
Hand-built layouts for Echo Isles' two caves (2026-10-21):

  Sunken Temple Grotto   100x90  drowned naga temple   (portal 50,81 / boss Gharesh 50,9)
  Zalazane's Hollow      100x92  troll voodoo hollow   (portal 52,86 / boss Zalazane 52,9)

Same recipe as tools/handbuilt_durotar_caves.py (CaveLayout: guarded props, flood-fill
QA, loops instead of dead ends) and the same painted-chunk registration, baked by
tools/bake_echo_caves.py.  Both are drawn as a spine to the boss with side wings that
loop back, so a player can detour for extra fights but never has to backtrack a dead end.

Portal contracts (world/portal_manager.py): Echo (24,98) <-> Grotto (50,81);
Echo (141,117) <-> Hollow (52,86).

Prop rule (Kyle): less is more; props logical for the room; a few centrepieces.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import (CaveLayout, DP, _apply_pools,  # noqa: F401
                                       register_baked, pool_fields)

SR = "assets/tiles/skull_rock/props/"
BAKED = "assets/tiles/echo_caves/{}/baked"


def _cave(name, w, h, desc, portal):
    zone = Tilemap(name, w, h, desc)
    zone.is_cave = True
    zone.region = "Echo Isles"
    zone.fixed_spawns = False
    return zone, CaveLayout(zone, portal)


def _finish(L, zone, portal, bosses, chests):
    L.mark("portal", *portal)
    for (x, y, _) in bosses:
        L.mark("boss_marker", x, y)
    for c in chests:
        L.mark("chest", *c)
    zone.boss_position = (bosses[0][0], bosses[0][1])
    zone.boss_positions = [(x, y, n) for (x, y, n) in bosses]


# ============================================================ SUNKEN TEMPLE GROTTO
STG_PORTAL = (50, 81)
STG_BOSS = (50, 10)
STG_ROAR = (16, 42)                  # Drowned Troll's sulk (named rare)
STG_CHESTS = [(40, 7), (9, 38), (91, 38), (10, 63)]
STG_POOLS = [(50, 66, 6.5, 3.0, 0.9), (84, 69, 4.2, 2.6, 1.7), (50, 45, 5.0, 2.6, 0.4)]


def build_temple_grotto():
    zone, L = _cave("Sunken Temple Grotto", 100, 90,
                    "A naga temple sunk beneath the Echo Isles, its halls half drowned by the tide.",
                    STG_PORTAL)
    b = L.b
    b.lobes([(50, 80, 10, 4), (42, 79, 4, 3), (58, 79, 4, 3)])                     # Tidewash Landing
    b.corridor([(50, 77), (50, 72)], width=4)
    b.lobes([(50, 65, 17, 7), (36, 63, 5, 4), (64, 63, 5, 4)])                     # The Flooded Atrium
    b.corridor([(35, 64), (28, 64), (23, 66)], width=3)                            # west
    b.lobes([(16, 68, 9, 6), (10, 63, 4, 3), (18, 74, 5, 3)])                      # Murloc Warrens
    b.corridor([(65, 64), (72, 64), (77, 66)], width=3)                            # east
    b.lobes([(84, 69, 9, 6), (90, 63, 3, 3), (82, 75, 5, 3)])                      # Elemental Springs
    b.corridor([(50, 59), (50, 51)], width=3)                                      # north
    b.lobes([(50, 45, 10, 5), (41, 44, 4, 3), (59, 44, 4, 3)])                     # The Sunken Cistern
    b.corridor([(50, 40), (50, 36)], width=3)
    b.rect(38, 26, 62, 35, chamfer=3)                                              # Hall of Tides
    b.corridor([(12, 60), (12, 54), (14, 48)], width=2)                            # warrens -> crypt
    b.lobes([(16, 42, 9, 6), (9, 38, 3, 3), (22, 46, 3, 2)])                       # The Drowned Crypt
    b.corridor([(23, 40), (29, 35), (37, 31)], width=3)                            # crypt -> hall (loop)
    b.corridor([(88, 62), (88, 55), (86, 48)], width=2)                            # springs -> reliquary
    b.lobes([(84, 42, 9, 6), (91, 38, 3, 3), (78, 46, 3, 2)])                      # Pearl Reliquary
    b.corridor([(77, 40), (71, 35), (63, 31)], width=3)                            # reliquary -> hall (loop)
    b.corridor([(24, 43), (31, 44), (38, 44)], width=2)                            # crypt -> cistern
    b.corridor([(78, 44), (70, 44), (62, 44)], width=2)                            # reliquary -> cistern
    b.corridor([(50, 25), (50, 14)], width=4)                                      # sanctum approach
    b.rect(36, 4, 64, 15, chamfer=3)                                               # Tidelord's Sanctum
    _apply_pools(zone, STG_POOLS, shallow_only=True)

    for n, x, y, w, h in [("Tidewash Landing", 38, 74, 24, 12), ("The Flooded Atrium", 30, 57, 42, 17),
                          ("The Murloc Warrens", 3, 58, 24, 22), ("The Elemental Springs", 74, 61, 24, 20),
                          ("The Sunken Cistern", 36, 39, 28, 13), ("The Drowned Crypt", 4, 34, 24, 16),
                          ("The Pearl Reliquary", 74, 34, 24, 16), ("The Hall of Tides", 37, 25, 26, 11),
                          ("The Tidelord's Sanctum", 35, 3, 30, 13)]:
        zone.add_subzone(n, x, y, w, h)
    zone.add_subzone("Sunken Temple Grotto", 0, 0, zone.width, zone.height)

    _finish(L, zone, STG_PORTAL,
            [(STG_BOSS[0], STG_BOSS[1], "Tidelord Gharesh"),
             (STG_ROAR[0], STG_ROAR[1], "Drowned Troll")], STG_CHESTS)

    p = L.prop
    # landing: a drowned anchor and a fisher's net strung from the arch
    p("grotto_anchor", 43, 80, 4)
    p("grotto_glow_coral", 58, 80, 3)
    p("temple_archway", 50, 75, 6, avoid=1)
    # atrium: columns frame the pool, braziers burn blue
    p("temple_column", 40, 61, 5, solid="core")
    p("temple_column", 60, 61, 5, solid="core")
    p("grotto_blue_brazier", 45, 70, 4, solid="core")
    p("grotto_blue_brazier", 55, 70, 4, solid="core")
    p("grotto_tide_pool", 34, 66, 3)
    # murloc warrens: nets, barrels, a fish-stink pile
    p("grotto_fishing_net", 14, 66, 3)
    p("grotto_barrel_stack", 20, 72, 3)
    p("grotto_crab_molt", 11, 72, 3)
    p("grotto_kelp_stalks", 9, 66, 4)
    p("den_campfire_ashes", 17, 70, 2)
    # elemental springs: glow coral and clams round the springs
    p("grotto_giant_clam", 80, 72, 3)
    p("grotto_glow_coral", 90, 70, 3)
    p("glow_coral_cluster", 78, 66, 3)
    p("grotto_barnacle_pillar", 87, 73, 4, solid="core")
    # cistern: a drowned obelisk
    p("grotto_naga_rune_stone", 50, 48, 4, solid="core", avoid=1)
    p("grotto_shell_altar", 41, 46, 3, solid="core")
    # crypt: troll dead (the Drowned Troll's lair)
    p("sarcophagus", 12, 44, 4, solid="core")
    p("skull_pile", 20, 40, 3)
    p("grotto_shackle_frame", 21, 45, 4, solid="core")
    p("grotto_pirate_skeletons", 13, 39, 3)
    p("grotto_kelp_stalks", 8, 42, 4)
    # reliquary: pearls and a shell altar
    p("grotto_shell_altar", 84, 40, 3, solid="core", avoid=1)
    p("grotto_glow_coral", 81, 44, 3)
    p("grotto_giant_clam", 88, 44, 3)
    p("priestess_statue", 79, 38, 5, solid="core")
    # hall of tides
    p("grotto_naga_column", 42, 28, 5, solid="core")
    p("grotto_naga_column", 58, 28, 5, solid="core")
    p("grotto_naga_priestess_statue", 41, 33, 5, solid="core")
    p("grotto_naga_warrior_statue", 59, 33, 5, solid="core")
    p("grotto_blue_brazier", 47, 31, 4, solid="core")
    p("grotto_blue_brazier", 53, 31, 4, solid="core")
    # sanctum: the throne, flanked
    p("grotto_naga_throne", 50, 7, 6, solid="core", avoid=2)
    p("naga_statue", 39, 10, 5, solid="core")
    p("naga_statue", 61, 10, 5, solid="core")
    p("grotto_shell_altar", 44, 12, 3, solid="core")
    p("grotto_shell_altar", 56, 12, 3, solid="core")
    p("grotto_naga_rune_stone", 50, 13, 4, solid="core", avoid=1)

    L.finish([STG_PORTAL, STG_BOSS, STG_ROAR] + STG_CHESTS)
    return zone, L


# ============================================================== ZALAZANE'S HOLLOW
ZH_PORTAL = (52, 86)
ZH_BOSS = (52, 9)
ZH_HOUNDMASTER = (52, 46)            # named rare, the kennel master
ZH_WITCH = (18, 42)                  # named rare, the Den's witch-doctor
ZH_CHESTS = [(40, 7), (11, 38), (89, 38), (90, 62)]
ZH_POOLS = []


def build_hollow():
    zone, L = _cave("Zalazane's Hollow", 100, 92,
                    "Zalazane's voodoo warren beneath the Echo Isles, thick with hex-smoke and bone.",
                    ZH_PORTAL)
    b = L.b
    b.lobes([(52, 84, 10, 4), (44, 83, 4, 3), (60, 83, 4, 3)])                     # Hexed Threshold
    b.corridor([(52, 80), (52, 72)], width=4)
    b.rect(40, 60, 64, 73, chamfer=2)                                              # The Thrall Pens
    b.corridor([(52, 59), (52, 53)], width=4)
    b.rect(40, 40, 64, 52, chamfer=2)                                              # The Hound Kennels
    b.corridor([(52, 39), (52, 33)], width=4)
    b.rect(36, 22, 68, 32, chamfer=3)                                              # The Ritual Hall
    b.corridor([(52, 21), (52, 15)], width=4)
    b.lobes([(52, 9, 14, 6), (40, 8, 5, 4), (64, 8, 5, 4)])                        # Zalazane's Sanctum
    # west wing
    b.corridor([(39, 66), (31, 66), (26, 66)], width=3)
    b.lobes([(18, 66, 9, 6), (12, 62, 3, 3), (20, 72, 4, 3)])                      # The Fetish Workshop
    b.corridor([(16, 60), (16, 52), (18, 47)], width=2)
    b.lobes([(18, 42, 9, 6), (11, 38, 3, 3)])                                      # The Witch-Doctor's Den
    b.corridor([(26, 40), (33, 36), (37, 30)], width=2)                            # den -> ritual hall (loop)
    b.corridor([(39, 45), (32, 44), (27, 43)], width=2)                            # den -> kennels
    # east wing
    b.corridor([(65, 66), (73, 66), (78, 66)], width=3)
    b.lobes([(84, 66, 9, 6), (90, 62, 3, 3), (82, 72, 4, 3)])                      # The Bone Pit
    b.corridor([(86, 60), (86, 52), (84, 47)], width=2)
    b.lobes([(82, 42, 9, 6), (89, 38, 3, 3)])                                      # The Hexed Larder
    b.corridor([(74, 40), (68, 34), (66, 29)], width=2)                            # larder -> ritual hall (loop)
    b.corridor([(65, 45), (73, 44), (77, 43)], width=2)                            # larder -> kennels

    for n, x, y, w, h in [("The Hexed Threshold", 38, 78, 28, 12), ("The Thrall Pens", 38, 58, 28, 17),
                          ("The Hound Kennels", 38, 38, 28, 16), ("The Ritual Hall", 34, 20, 36, 14),
                          ("Zalazane's Sanctum", 36, 2, 34, 15),
                          ("The Fetish Workshop", 4, 57, 24, 20), ("The Witch-Doctor's Den", 4, 33, 24, 16),
                          ("The Bone Pit", 74, 57, 24, 20), ("The Hexed Larder", 72, 33, 24, 16)]:
        zone.add_subzone(n, x, y, w, h)
    zone.add_subzone("Zalazane's Hollow", 0, 0, zone.width, zone.height)

    _finish(L, zone, ZH_PORTAL,
            [(ZH_BOSS[0], ZH_BOSS[1], "Zalazane"),
             (ZH_HOUNDMASTER[0], ZH_HOUNDMASTER[1], "Houndmaster Gor'tek"),
             (ZH_WITCH[0], ZH_WITCH[1], "Mam'toth the Hexweaver")], ZH_CHESTS)

    p = L.prop
    # threshold: the first totems, a torch and the last recruit
    p("den_torch", 45, 84, 4)
    p("den_torch", 59, 84, 4)
    p("vot_totem_pole", 46, 82, 6, solid="core", avoid=1)
    p("vot_totem_pole", 58, 82, 6, solid="core", avoid=1)
    # thrall pens: cages of villagers, shackles, a hide rack
    p("rf_prison_cage", 44, 64, 4, solid="core")
    p("rf_prison_cage", 60, 64, 4, solid="core")
    p("rf_shackle_frame", 44, 70, 4, solid="core")
    p("rf_shackle_frame", 60, 70, 4, solid="core")
    p("vot_hide_rack", 52, 66, 4, solid="core", avoid=1)
    p("den_leg_bones", 49, 71, 2)
    # hound kennels
    p("kennel_cage_worg", 44, 44, 4, solid="core")
    p("kennel_cage_worg", 60, 44, 4, solid="core")
    p("kennel_cage_empty", 44, 50, 4, solid="core")
    p("vot_beast_ribcage", 58, 50, 3)
    p("bone_pile", 49, 49, 3, where=SR)
    # ritual hall: summoning circle centrepiece, braziers and the idol
    p("ritual_circle", 52, 28, 5, avoid=1)
    p("spirit_brazier", 42, 26, 4, solid="core")
    p("spirit_brazier", 62, 26, 4, solid="core")
    p("bbc_idol", 40, 31, 5, solid="core")
    p("bbc_idol", 64, 31, 5, solid="core")
    p("vot_war_drum", 47, 24, 3, solid="core")
    # sanctum
    p("rf_sacrificial_altar", 52, 13, 4, solid="core", avoid=1)
    p("vot_totem_pole", 42, 11, 6, solid="core")
    p("vot_totem_pole", 62, 11, 6, solid="core")
    p("bbc_skull_pile", 46, 6, 3)
    p("bbc_skull_pile", 58, 6, 3)
    p("spirit_brazier", 37, 10, 4, solid="core")
    p("spirit_brazier", 67, 10, 4, solid="core")
    # fetish workshop
    p("bbc_warlock_desk", 18, 64, 4, solid="core")
    p("bbc_bookshelf", 14, 70, 4, solid="core")
    p("den_chest_sack", 22, 70, 3)
    p("vot_hide_rack", 12, 66, 4)
    p("candelabra", 22, 63, 3)
    # witch-doctor's den
    p("bbc_cage", 13, 44, 4, solid="core")
    p("bone_pile", 23, 44, 3, where=SR)
    p("den_glow_mushrooms", 20, 38, 3)
    p("spirit_brazier", 16, 38, 4, solid="core")
    # bone pit
    p("skull_pile", 84, 64, 3)
    p("vot_beast_ribcage", 80, 68, 3)
    p("den_leg_bones", 90, 68, 2)
    p("bbc_skull_pile", 86, 72, 3)
    p("bone_pile", 79, 62, 3, where=SR)
    # hexed larder
    p("den_buried_crate", 78, 40, 3)
    p("den_chest_sack", 86, 46, 3)
    p("vot_hide_rack", 80, 44, 4)
    p("cocoon_victim", 88, 42, 4)

    L.finish([ZH_PORTAL, ZH_BOSS, ZH_HOUNDMASTER, ZH_WITCH] + ZH_CHESTS)
    return zone, L


# ======================================================== generate_* wrappers
def _gen(build, slug):
    zone, _ = build()
    register_baked(zone, BAKED.format(slug))
    return zone


def generate_sunken_temple_grotto():
    return _gen(build_temple_grotto, "temple_grotto")


def generate_zalazane_hollow():
    return _gen(build_hollow, "hollow")
