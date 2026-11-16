"""
Hand-built the Scarlet Monastery: its grounds and FOUR WINGS, each its own dungeon (docs/plaguelands_design.md).

Kyle, 16 Nov 2026: "So can you also make SM with the 4 different dungeons? The layout etc." The levels are his
(Plan A): Graveyard 28-32, Library 32-36, Armory 35-39, Cathedral 38-42. Scarlet kills inside pay the Order of the
Pale Flame, capped at Honored ("YES" to the cap). No keys: every wing is open.

THE GROUNDS (64x52) is the walled close inside the barred gate in Eastern Tirisfal. No monsters: four doors and the
way back out. The Graveyard is down through the crypt chapel in the cemetery on the west side; the Library, the
Armory and the Cathedral are three houses against the north wall, left to right: a chapel, a gatehouse and the
Cathedral's own front.

    gate (32,50) <-> Eastern Tirisfal (70,32)
    Graveyard door (12,34) . Library door (14,13) . Armory door (32,13) . Cathedral door (50,13)

THE WINGS FOLLOW WOW'S (Kyle, 16 Nov 2026: "cathedral has a courtyard THEN cathedral!" and "Look up authentic-style
WoW dungeons for this bro"). Each wing walks in the same order as the classic one and its rooms carry the classic
names (warcraft.wiki.gg's subzone lists; the classic guides for who stands where). One wing in each has an OPEN-AIR
part, painted as ground rather than floor (`open_air`): the Graveyard's burial ground, the Library's kennel cloister,
the Armory's training yard and the Cathedral's gardens. Every boss asks one thing of the party (kits in
tools/build_scarlet_monastery_content.py). FIVE ENCOUNTERS A WING (Kyle: "Lets aim for about 4-6 bosses per
dungeon"), classic's own where it has them and new ones where it doesn't; trash is fixed, in packs of four or five.

THE GRAVEYARD (100x84), 28-32: the halls, the torture room, the burial ground, the tomb.
    door (south) -> the Penitents' Hall -> the Chamber of Atonement (west) -> the Forlorn Cloister (open air, north)
    -> Honor's Tomb (east)
        the Chamber of Atonement             1 Interrogator Maelis           burns and breaks: cleanse, heal through
        the Forlorn Cloister, west (opt.)    2 Ironspine                     a giant of bone: poison, armour of bone
        the Forlorn Cloister                 3 Azshir the Sleepless          a wraith among the graves: spread out
        behind the mausoleum (opt.)          4 the Fallen Champion           hits harder as it falls
        Honor's Tomb                         5 Bloodmage Thalnos             spells feed his ward: hit him with steel

THE LIBRARY (110x96), 32-36: long halls that keep turning, the kennels, the gallery, the Athenaeum.
    door -> the Scriptorium -> the west hall -> the north hall -> Huntsman's Cloister (open air) -> the Gallery of
    Treasures -> the Athenaeum
        the Hall of Judgement                1 Inquisitor Vellan Rook        marks a heretic: heal the mark
        Huntsman's Cloister                  2 Houndmaster Loksey            his hounds first, or they mend him
        the Closed Stacks, off the north hall (opt.)
                                             3 Archivist Dana Mercer         a transplant who catalogued the Crusade's
                                                                             sins and kept them: silences casters
        the Gallery of Treasures             4 Curator Halbrecht             calls the gallery's monks: kill them first
        the Athenaeum                        5 Arcanist Doan                 detonates: get away from him at the brink

THE ARMORY (110x90), 35-39: the yard, the two armouries, the hall the Crusade keeps for its champions.
    door -> the Gate Hall -> the Training Grounds (open air) -> the Footman's Armory -> the Crusader's Armory -> the
    Hall of Champions
        the Training Grounds                 1 Sergeant Major Cole Brennan   a transplant drill instructor: his recruits
                                                                             come in waves
        the Footman's Armory                 2 Quartermaster Bram Ellison    armour you have to cut through
        the Crusader's Armory                3 Master-at-Arms Dorran Pike    parries steel back: casters carry it
        the Armory Forge, north (opt.)       4 Smithmaster Corra Bellweather burns that spread, plate she tempers
        the Hall of Champions                5 Herod                         whirlwinds and enrages: the party moves

THE CATHEDRAL (120x110), 38-42: the gardens first, then the chapel.
    door -> the Chapel Gardens (open air, a fountain at the centre) -> up the steps -> the Crusader's Chapel -> the
    Chancel
        the Chapel Gardens, by the fountain  1 Brother Garrick Thorne        the gardener: thorns and roots
        the top of the steps                 2 Captain Elric Stane           the chapel's doors: his guard first
        the Inquisitor's Cell, off the chapel (opt.)
                                             3 High Inquisitor Aldric        a corpse that will not stay dead
        the Crusader's Chapel                4 Brother Corwin Ashe           a transplant who preaches: his sermon
                                                                             shields the faithful
        the Chancel                          5 High Inquisitor Whitemane and Scarlet Commander Mograine, one fight:
                                               he holds the front and gets back up once; she mends herself. Three drops.
"""
from world.tilemap import Tilemap
from tools.dungeon_builder import Builder

GROUNDS, GRAVEYARD, LIBRARY, ARMORY, CATHEDRAL = (
    "Scarlet Monastery Grounds", "Scarlet Monastery: Graveyard", "Scarlet Monastery: Library",
    "Scarlet Monastery: Armory", "Scarlet Monastery: Cathedral")
WINGS = (GRAVEYARD, LIBRARY, ARMORY, CATHEDRAL)
BAKED = {GROUNDS: "assets/tiles/scarlet_monastery/baked_grounds",
         GRAVEYARD: "assets/tiles/scarlet_monastery/baked_graveyard",
         LIBRARY: "assets/tiles/scarlet_monastery/baked_library",
         ARMORY: "assets/tiles/scarlet_monastery/baked_armory",
         CATHEDRAL: "assets/tiles/scarlet_monastery/baked_cathedral"}

DP = "assets/tiles/dungeon_props/"
EK = "assets/tiles/eastern_kingdoms/props/"
UF = "assets/tiles/undead_farmland/props/"
PL = "assets/tiles/plaguelands/props/"
BLD = "assets/buildings/"
BLD_ = BLD                 # (dressing entries take a path without ".png")

#: the door in from each wing's grounds side, and where it lands in the grounds
GROUNDS_DOORS = {GRAVEYARD: (12, 34), LIBRARY: (14, 13), ARMORY: (32, 13), CATHEDRAL: (50, 13)}
GROUNDS_GATE = (32, 50)

# ============================================================================================ data per wing
#: name -> dict(size, door, rooms {name: (x0, y0, x1, y1, chamfer)}, corridors [(points, width)],
#:              cells [(x0, y0, x1, y1)], cell_links, pillars [(x, y)], bosses [(x, y, name, required)],
#:              final, pack (2-for-1 members), dressing [(sprite, x, y, h, solid)], trash [[(x, y, name, lvl)]])
WING = {
    # THE GRAVEYARD: the halls, Vishas's old torture room, the open-air graveyard with its mausoleum, the tomb.
    GRAVEYARD: dict(
        size=(100, 84), door=(50, 81),
        rooms={"The Penitents' Hall": (42, 62, 58, 80, 2), "The Chamber of Atonement": (6, 54, 30, 74, 2),
               "The Forlorn Cloister": (10, 8, 74, 46, 4), "Honor's Tomb": (78, 6, 97, 40, 3)},
        corridors=[([(50, 81), (50, 80)], 4), ([(44, 67), (30, 67)], 3), ([(18, 54), (18, 46)], 3),
                   ([(74, 24), (78, 24)], 3)],
        cells=[(34, 50, 40, 56), (84, 46, 92, 52), (2, 76, 10, 82)],
        cell_links=[([(30, 58), (36, 53)], 2), ([(88, 40), (88, 46)], 2), ([(10, 74), (6, 77)], 2)],
        pillars=[(82, 12), (92, 12), (82, 22), (92, 22), (82, 32), (92, 32)],
        open_air=["The Forlorn Cloister"],
        bosses=[(18, 64, "Interrogator Maelis", True), (24, 30, "Ironspine", False),
                (64, 22, "Azshir the Sleepless", True), (42, 14, "The Fallen Champion", False),
                (87, 10, "Bloodmage Thalnos", True)],
        final="Bloodmage Thalnos", pack={},
        dressing=[(DP + "rf_shackle_frame", 10, 58, 4, "core"), (DP + "rf_prison_cage", 27, 58, 4, "core"),
                  (DP + "rf_sacrificial_altar", 18, 71, 3, "core"), (DP + "rf_tool_rack", 27, 72, 3, "core"),
                  (EK + "ek_scarlet_banner", 44, 64, 4, False), (EK + "ek_scarlet_banner", 56, 64, 4, False),
                  (DP + "candelabra", 45, 76, 3, False), (DP + "candelabra", 55, 76, 3, False),
                  # the cloister: graves around the mausoleum, the Fallen Champion behind it
                  (BLD_ + "crypt_chapel", 42, 31, 10, True),
                  (UF + "gravestone_cluster", 18, 16, 3, False), (UF + "gravestone_cluster", 26, 24, 3, False),
                  (UF + "gravestone_cluster", 16, 34, 3, False), (UF + "gravestone_cluster", 56, 14, 3, False),
                  (UF + "gravestone_cluster", 58, 34, 3, False), (UF + "gravestone_cluster", 68, 40, 3, False),
                  (EK + "ek_open_grave", 30, 40, 2, False), (EK + "ek_grave_hand", 50, 40, 2, False),
                  (EK + "ek_dead_oak", 14, 42, 6, "core"), (EK + "ek_dead_oak", 70, 12, 6, "core"),
                  (UF + "dead_tree_bare", 34, 12, 5, "core"), (EK + "ek_angel_statue", 52, 26, 5, "core"),
                  # the tomb
                  (DP + "sarcophagus", 81, 36, 3, "core"), (DP + "sarcophagus", 94, 36, 3, "core"),
                  (DP + "twilight_altar", 87, 7, 3, "core"), (DP + "candelabra", 82, 8, 3, False),
                  (DP + "candelabra", 93, 8, 3, False), (DP + "skull_pile", 80, 28, 2, False)],
        trash=[[(48, 74, "Scarlet Torturer", 28), (52, 74, "Scarlet Scryer", 28), (50, 70, "Scarlet Torturer", 28)],
               [(46, 65, "Scarlet Scryer", 28), (54, 65, "Scarlet Torturer", 28)],
               [(26, 66, "Scarlet Torturer", 29), (26, 62, "Scarlet Scryer", 29)],
               [(12, 64, "Scarlet Scryer", 29), (14, 68, "Scarlet Torturer", 29)],
               [(20, 40, "Anguished Dead", 30), (24, 36, "Haunting Phantasm", 30)],
               [(16, 22, "Unfettered Spirit", 30), (22, 18, "Anguished Dead", 30)],
               [(58, 40, "Haunting Phantasm", 30), (64, 38, "Anguished Dead", 30)],
               [(68, 30, "Unfettered Spirit", 31), (60, 30, "Haunting Phantasm", 31)],
               [(84, 28, "Haunting Phantasm", 31), (90, 28, "Unfettered Spirit", 31), (87, 32, "Anguished Dead", 31)]],
    ),
    # THE LIBRARY: long halls that turn and turn, the kennels' cloister, the gallery, the Athenaeum.
    LIBRARY: dict(
        size=(110, 96), door=(55, 93),
        rooms={"The Scriptorium": (48, 80, 62, 92, 2), "The Hall of Judgement": (6, 80, 24, 92, 2),
               "Huntsman's Cloister": (4, 34, 34, 62, 3),
               "The Closed Stacks": (26, 66, 44, 80, 2), "Gallery of Treasures": (38, 38, 100, 50, 2),
               "The Athenaeum": (50, 4, 106, 30, 4)},
        corridors=[([(55, 93), (55, 92)], 4), ([(48, 86), (16, 86)], 4), ([(16, 88), (16, 62)], 4),
                   ([(18, 72), (26, 72)], 3), ([(34, 44), (38, 44)], 4), ([(92, 38), (92, 30)], 4)],
        cells=[(46, 53, 54, 59), (78, 53, 86, 59), (60, 32, 68, 36)],
        cell_links=[([(50, 50), (50, 53)], 2), ([(82, 50), (82, 53)], 2), ([(64, 30), (64, 32)], 2)],
        pillars=[(10, 40), (27, 40), (10, 55), (27, 55), (60, 12), (60, 22), (96, 12), (96, 22)],
        open_air=["Huntsman's Cloister"],
        bosses=[(14, 86, "Inquisitor Vellan Rook", True), (19, 48, "Houndmaster Loksey", True),
                (36, 73, "Archivist Dana Mercer", False), (80, 44, "Curator Halbrecht", True),
                (78, 10, "Arcanist Doan", True)],
        final="Arcanist Doan", pack={},
        dressing=[(DP + "kennel_cage_worg", 8, 61, 3, "core"), (DP + "kennel_cage_empty", 30, 61, 3, "core"),
                  (DP + "kennel_cage_empty", 8, 37, 3, "core"), (DP + "kennel_cage_worg", 30, 37, 3, "core"),
                  (EK + "ek_thorn_bush", 14, 46, 2, False), (EK + "ek_thorn_bush", 24, 52, 2, False),
                  (DP + "bbc_bookshelf", 30, 69, 4, "core"), (DP + "bbc_bookshelf", 36, 69, 4, "core"),
                  (DP + "bbc_bookshelf", 42, 69, 4, "core"), (DP + "wizard_desk", 34, 78, 3, "core"),
                  (EK + "ek_scarlet_banner", 44, 40, 4, False), (EK + "ek_scarlet_banner", 60, 40, 4, False),
                  (EK + "ek_scarlet_banner", 76, 40, 4, False), (DP + "priestess_statue", 92, 48, 4, "core"),
                  (DP + "bbc_candelabra", 52, 48, 3, False), (DP + "bbc_candelabra", 70, 48, 3, False),
                  (DP + "bbc_bookshelf", 56, 7, 4, "core"), (DP + "bbc_bookshelf", 66, 7, 4, "core"),
                  (DP + "bbc_bookshelf", 90, 7, 4, "core"), (DP + "bbc_bookshelf", 100, 7, 4, "core"),
                  (DP + "bbc_bookshelf", 70, 27, 4, "core"), (DP + "bbc_bookshelf", 80, 27, 4, "core"),
                  (DP + "bbc_altar", 78, 6, 3, "core"), (DP + "wizard_desk", 102, 26, 3, "core"),
                  (DP + "banquet_table", 55, 86, 3, "core"), (DP + "bbc_throne", 15, 82, 3, "core"),
                  (EK + "ek_scarlet_banner", 9, 83, 4, False), (EK + "ek_scarlet_banner", 21, 83, 4, False), (DP + "bbc_candelabra", 50, 82, 3, False),
                  (DP + "bbc_candelabra", 60, 82, 3, False)],
        trash=[[(52, 89, "Scarlet Adept", 32), (58, 89, "Scarlet Gallant", 32), (55, 84, "Scarlet Adept", 32)],
               [(36, 86, "Scarlet Gallant", 33), (30, 86, "Scarlet Monk", 33)],
               [(16, 76, "Scarlet Adept", 33), (16, 70, "Scarlet Gallant", 33)],
               [(8, 48, "Scarlet Beastmaster", 33), (10, 44, "Scarlet Tracking Hound", 33),
                (8, 52, "Scarlet Tracking Hound", 33)],
               [(30, 46, "Scarlet Gallant", 34), (30, 52, "Scarlet Monk", 34)],
               [(28, 77, "Scarlet Adept", 34), (42, 77, "Scarlet Monk", 34)],
               [(46, 44, "Scarlet Monk", 34), (50, 46, "Scarlet Adept", 34), (46, 47, "Scarlet Gallant", 34)],
               [(66, 44, "Scarlet Gallant", 35), (70, 46, "Scarlet Monk", 35), (66, 47, "Scarlet Adept", 35)],
               [(88, 44, "Scarlet Beastmaster", 35), (92, 45, "Scarlet Tracking Hound", 35)],
               [(92, 26, "Scarlet Adept", 35), (86, 24, "Scarlet Gallant", 35)],
               [(70, 18, "Scarlet Monk", 35), (88, 16, "Scarlet Adept", 35)]],
    ),
    # THE ARMORY: the open training yard, the two armouries, the Hall of Champions.
    ARMORY: dict(
        size=(110, 90), door=(55, 87),
        rooms={"The Gate Hall": (50, 76, 60, 88, 2), "Training Grounds": (20, 50, 90, 76, 4),
               "Footman's Armory": (4, 20, 34, 46, 2), "Crusader's Armory": (40, 18, 70, 40, 2),
               "The Armory Forge": (44, 4, 66, 14, 2),
               "Hall of Champions": (74, 4, 106, 44, 3)},
        corridors=[([(55, 87), (55, 86)], 4), ([(26, 52), (20, 44)], 4), ([(34, 30), (40, 30)], 4),
                   ([(70, 30), (74, 30)], 4), ([(55, 18), (55, 14)], 3)],
        cells=[(96, 52, 106, 60), (4, 52, 12, 60), (40, 43, 48, 48)],
        cell_links=[([(90, 60), (96, 56)], 2), ([(20, 58), (12, 56)], 2), ([(44, 40), (44, 43)], 2)],
        pillars=[(79, 12), (99, 12), (79, 22), (99, 22), (79, 32), (99, 32)],
        open_air=["Training Grounds"],
        bosses=[(55, 63, "Sergeant Major Cole Brennan", True), (19, 31, "Quartermaster Bram Ellison", True),
                (56, 25, "Master-at-Arms Dorran Pike", True), (55, 8, "Smithmaster Corra Bellweather", False),
                (89, 9, "Herod", True)],
        final="Herod", pack={},
        dressing=[(DP + "vot_training_dummy", 30, 58, 3, "core"), (DP + "vot_training_dummy", 36, 58, 3, "core"),
                  (DP + "vot_training_dummy", 30, 68, 3, "core"), (DP + "vot_training_dummy", 36, 68, 3, "core"),
                  (DP + "vot_archery_target", 78, 56, 3, "core"), (DP + "vot_archery_target", 84, 56, 3, "core"),
                  (DP + "vot_archery_target", 84, 66, 3, "core"), (PL + "pf_weapon_rack", 60, 52, 3, "core"),
                  (EK + "ek_scarlet_banner", 46, 54, 4, False), (EK + "ek_scarlet_banner", 64, 54, 4, False),
                  (EK + "ek_haystack", 76, 72, 3, "core"), (DP + "vot_crate_stack", 24, 72, 3, "core"),
                  (DP + "weapon_rack", 8, 24, 3, "core"), (DP + "weapon_rack", 16, 24, 3, "core"),
                  (DP + "bbc_weapon_rack", 28, 24, 3, "core"), (EK + "ek_scarlet_crates", 8, 43, 3, "core"),
                  (EK + "ek_scarlet_crates", 30, 43, 3, "core"), (DP + "bbc_weapon_rack", 46, 21, 3, "core"),
                  (DP + "bbc_weapon_rack", 56, 21, 3, "core"), (DP + "weapon_rack", 66, 21, 3, "core"),
                  (EK + "ek_scarlet_crates", 66, 37, 3, "core"),
                  (PL + "pl_knight_statue", 77, 8, 4, "core"), (PL + "pl_knight_statue", 102, 8, 4, "core"),
                  (EK + "ek_scarlet_banner", 84, 6, 4, False), (EK + "ek_scarlet_banner", 94, 6, 4, False),
                  (DP + "bbc_throne", 89, 6, 3, "core"),
                  (DP + "vot_fire_pit", 48, 8, 2, "core"), (DP + "rf_tool_rack", 62, 6, 3, "core"),
                  (DP + "rf_ore_cart", 63, 12, 3, "core"), (DP + "weapon_rack", 47, 13, 3, "core")],
        trash=[[(53, 82, "Scarlet Trainee", 35), (57, 82, "Scarlet Trainee", 35)],
               [(70, 70, "Scarlet Trainee", 35), (74, 66, "Scarlet Soldier", 35), (66, 66, "Scarlet Trainee", 35)],
               [(42, 70, "Scarlet Soldier", 35), (46, 66, "Scarlet Trainee", 35)],
               [(40, 56, "Scarlet Soldier", 36), (44, 58, "Scarlet Trainee", 36)],
               [(12, 40, "Scarlet Defender", 36), (24, 40, "Scarlet Soldier", 36), (18, 44, "Scarlet Evoker", 36)],
               [(8, 30, "Scarlet Myrmidon", 37), (30, 30, "Scarlet Defender", 37)],
               [(44, 34, "Scarlet Myrmidon", 37), (48, 37, "Scarlet Defender", 37), (44, 30, "Scarlet Evoker", 37)],
               [(64, 34, "Scarlet Myrmidon", 37), (67, 30, "Scarlet Evoker", 37)],
               [(48, 11, "Scarlet Soldier", 37), (62, 9, "Scarlet Evoker", 37)],
               [(84, 38, "Scarlet Defender", 38), (94, 38, "Scarlet Myrmidon", 38), (89, 34, "Scarlet Evoker", 38)],
               [(84, 24, "Scarlet Myrmidon", 38), (94, 24, "Scarlet Defender", 38)]],
    ),
    # THE CATHEDRAL: the Chapel Gardens first, out in the open, then up the steps into the Crusader's Chapel.
    CATHEDRAL: dict(
        size=(120, 110), door=(60, 107),
        rooms={"Chapel Gardens": (14, 58, 106, 104, 5), "Crusader's Chapel": (40, 14, 80, 52, 2),
               "The Chancel": (34, 3, 86, 16, 3), "The Inquisitor's Cell": (90, 18, 110, 38, 2)},
        corridors=[([(60, 107), (60, 104)], 4), ([(60, 58), (60, 52)], 8), ([(80, 28), (90, 28)], 2)],
        cells=[(4, 62, 12, 70), (108, 62, 116, 70), (88, 42, 96, 48)],
        cell_links=[([(14, 66), (12, 66)], 2), ([(106, 66), (108, 66)], 2), ([(80, 45), (88, 45)], 2)],
        pillars=[(47, 20), (72, 20), (47, 29), (72, 29), (47, 38), (72, 38), (47, 46), (72, 46)],
        open_air=["Chapel Gardens"],
        bosses=[(60, 71, "Brother Garrick Thorne", True), (60, 50, "Captain Elric Stane", True),
                (100, 28, "High Inquisitor Aldric", False), (60, 34, "Brother Corwin Ashe", True),
                (60, 9, "High Inquisitor Whitemane", True)],
        final="High Inquisitor Whitemane",
        pack={"High Inquisitor Whitemane": [(64, 11, "Scarlet Commander Mograine")]},
        dressing=[(EK + "ek_dry_fountain", 60, 85, 8, "core"),         # the gardens' centre
                  (EK + "ek_angel_statue", 40, 70, 5, "core"), (EK + "ek_angel_statue", 80, 70, 5, "core"),
                  (EK + "ek_pine_tall", 22, 66, 6, "core"), (EK + "ek_pine_tall", 98, 66, 6, "core"),
                  (EK + "ek_pine_tall", 24, 98, 6, "core"), (EK + "ek_pine_tall", 96, 98, 6, "core"),
                  (EK + "ek_willow", 34, 94, 6, "core"), (EK + "ek_willow", 86, 94, 6, "core"),
                  (EK + "ek_thorn_bush", 44, 76, 2, False), (EK + "ek_thorn_bush", 76, 76, 2, False),
                  (EK + "ek_thorn_bush", 44, 90, 2, False), (EK + "ek_thorn_bush", 76, 90, 2, False),
                  (PL + "ql_lantern_post", 54, 98, 3, "core"), (PL + "ql_lantern_post", 66, 98, 3, "core"),
                  (PL + "ql_lantern_post", 54, 64, 3, "core"), (PL + "ql_lantern_post", 66, 64, 3, "core"),
                  (EK + "ek_scarlet_banner", 52, 61, 4, False), (EK + "ek_scarlet_banner", 68, 61, 4, False),
                  # the chapel
                  (DP + "candelabra", 44, 17, 3, False), (DP + "candelabra", 76, 17, 3, False),
                  (EK + "ek_scarlet_banner", 42, 26, 4, False), (EK + "ek_scarlet_banner", 78, 26, 4, False),
                  (EK + "ek_scarlet_banner", 42, 42, 4, False), (EK + "ek_scarlet_banner", 78, 42, 4, False),
                  (DP + "wizard_desk", 60, 31, 2, "core"),
                  (DP + "bbc_altar", 60, 5, 3, "core"), (DP + "bbc_candelabra", 52, 6, 3, False),
                  (DP + "bbc_candelabra", 68, 6, 3, False), (EK + "ek_scarlet_banner", 38, 8, 5, False),
                  (EK + "ek_scarlet_banner", 82, 8, 5, False),
                  (DP + "sarcophagus", 106, 22, 3, "core"), (DP + "rf_prison_cage", 94, 36, 3, "core")],
        trash=[[(56, 98, "Scarlet Centurion", 38), (64, 98, "Scarlet Sorcerer", 38), (60, 94, "Scarlet Centurion", 38)],
               [(28, 84, "Scarlet Champion", 38), (32, 78, "Scarlet Monk", 38), (24, 76, "Scarlet Wizard", 38)],
               [(92, 84, "Scarlet Centurion", 39), (88, 78, "Scarlet Abbot", 39), (96, 76, "Scarlet Sorcerer", 39)],
               [(46, 64, "Scarlet Champion", 39), (50, 68, "Scarlet Wizard", 39)],
               [(74, 64, "Scarlet Monk", 39), (70, 68, "Scarlet Centurion", 39)],
               [(50, 43, "Scarlet Champion", 40), (70, 43, "Scarlet Abbot", 40), (60, 42, "Scarlet Monk", 40)],
               [(52, 25, "Scarlet Sorcerer", 40), (68, 25, "Scarlet Wizard", 40)],
               [(93, 34, "Scarlet Centurion", 40), (94, 22, "Scarlet Wizard", 40)],
               [(48, 15, "Scarlet Champion", 41), (72, 15, "Scarlet Champion", 41), (60, 18, "Scarlet Abbot", 41)],
               [(40, 9, "Scarlet Wizard", 41), (80, 9, "Scarlet Sorcerer", 41)]],
    ),
}
#: The Forlorn Cloister is a burial ground first: rows of graves either side of the walk to the mausoleum.
WING[GRAVEYARD]["dressing"] += [(UF + "gravestone_cluster", x, y, 3, False)
                                for y in (16, 21, 34, 39) for x in (20, 25, 31, 53, 59, 65)
                                if (x, y) not in ((25, 21), (59, 34))]


def _room_box(r):
    x0, y0, x1, y1, _c = r
    return x0, y0, x1 - x0 + 1, y1 - y0 + 1


def build_wing(name):
    spec = WING[name]
    W, H = spec["size"]
    zone = Tilemap(name, W, H, {
        GRAVEYARD: "The crypts under the Scarlet Monastery's burial ground, where the Crusade questions its "
                   "prisoners and its dead won't stay down.",
        LIBRARY: "The Crusade's archive: every book it has ever burned a copy of, and the kennels of the hounds it "
                 "hunts heretics with.",
        ARMORY: "The Crusade's training yard and armouries, and the hall it keeps for its champions.",
        CATHEDRAL: "The Scarlet Cathedral: the courtyard, the nave, and the chancel where the Crusade's "
                   "leaders keep court.",
    }[name])
    zone.is_cave = True
    zone.region = "Eastern Tirisfal"
    b = Builder(zone, wall_id="wall", floor_id="stone")
    for r in spec["rooms"].values():
        b.rect(r[0], r[1], r[2], r[3], chamfer=r[4])
    for (x0, y0, x1, y1) in spec["cells"]:
        b.rect(x0, y0, x1, y1, chamfer=1)
    for pts, wdt in spec["corridors"] + spec["cell_links"]:
        b.corridor(pts, width=wdt)
    for (x, y) in spec["pillars"]:
        b.pillars([x], [y], size=2, sprite="assets/tiles/scarlet_monastery/props/sm_stone_column.png", height=4)
    for (path, x, y, h, solid) in spec["dressing"]:
        if not zone.is_walkable(x, y):
            raise AssertionError((name, "prop base not on the floor", path, x, y))
        b.prop(path + ".png", x, y, h, solid=solid, fraction=0.4)

    dx, dy = spec["door"]
    zone.collision_layer[dy][dx] = None
    zone.collision_layer[dy - 1][dx] = None
    fixed = []
    for (x, y, n, _req) in spec["bosses"]:
        if not zone.is_walkable(x, y):
            raise AssertionError((name, "boss standing in rock", n, x, y))
        fixed.append((x, y, n))
    final = next(f for f in fixed if f[2] == spec["final"])
    zone.boss_position = final[:2]
    zone.boss_positions = list(fixed)
    zone.boss_pack = dict(spec["pack"])
    chests = [((x0 + x1) // 2, (y0 + y1) // 2) for (x0, y0, x1, y1) in spec["cells"]]
    zone.chest_spots = chests
    b.verify((dx, dy - 2), list(fixed) + [(x, y, "chest") for (x, y) in chests])
    zone.add_subzone(name, 0, 0, W, H)
    for rname, r in spec["rooms"].items():
        zone.add_subzone(rname, *_room_box(r))
    return zone, b


def build_grounds():
    W, H = 64, 52
    zone = Tilemap(GROUNDS, W, H, "The walled close inside the Scarlet Monastery's gate: the burial ground to the "
                                  "west and the monastery's three doors to the north.")
    zone.is_cave = False
    zone.region = "Eastern Tirisfal"
    b = Builder(zone, wall_id="wall", floor_id="stone")
    b.rect(3, 9, 60, 50, chamfer=3)                       # the close
    gx, gy = GROUNDS_GATE
    zone.collision_layer[gy][gx] = None
    zone.collision_layer[gy - 1][gx] = None
    # THE THREE HOUSES stand against the north wall, each over its own door: the Library's chapel, the Armory's
    # gatehouse and the Cathedral's front. The Graveyard's way down is the crypt chapel in the cemetery.
    for path, wing, h in ((BLD + "bd_seized_chapel.png", LIBRARY, 10), (BLD + "hearthglen_keep_gate.png", ARMORY, 10),
                          (BLD + "sm_facade.png", CATHEDRAL, 12), (BLD + "crypt_chapel.png", GRAVEYARD, 8)):
        x, y = GROUNDS_DOORS[wing]
        b.prop(path, x, y - 1, h, solid=True)
    for (x, y) in GROUNDS_DOORS.values():
        zone.collision_layer[y][x] = None
    for (x, y) in [(6, 22), (18, 22), (6, 40), (18, 40), (22, 31)]:
        b.prop(UF + "gravestone_cluster.png", x, y, 3, solid=False)
    b.prop(EK + "ek_cemetery_fence.png", 12, 19, 3, solid=False)
    b.prop(EK + "ek_cemetery_fence.png", 12, 44, 3, solid=False)
    b.prop(EK + "ek_angel_statue.png", 23, 17, 5, solid="core")
    b.prop(EK + "ek_angel_statue.png", 41, 17, 5, solid="core")
    b.prop(EK + "ek_dry_fountain.png", 32, 32, 7, solid="core")            # the close's centre
    for (x, y) in [(46, 22), (54, 22), (46, 40), (54, 40)]:
        b.prop(EK + "ek_scarlet_banner.png", x, y, 4, solid=False)
    b.prop(PL + "sc_war_tent.png", 52, 31, 5, solid="core")
    b.prop(EK + "ek_scarlet_crates.png", 44, 46, 3, solid="core")
    b.verify((gx, gy - 2), [(x, y, n) for n, (x, y) in GROUNDS_DOORS.items()])
    zone.add_subzone(GROUNDS, 0, 0, W, H)
    return zone, b


def build_grounds_baked():
    return build_grounds()


def build_graveyard_baked():
    return build_wing(GRAVEYARD)


def build_library_baked():
    return build_wing(LIBRARY)


def build_armory_baked():
    return build_wing(ARMORY)


def build_cathedral_baked():
    return build_wing(CATHEDRAL)


def _snap(zone, spots, rad=6):
    out = []
    for (x, y, m, lvl) in spots:
        if zone.is_walkable(x, y):
            out.append((x, y, m, lvl))
            continue
        best = None
        for dy in range(-rad, rad + 1):
            for dx in range(-rad, rad + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < zone.width and 0 <= ny < zone.height and zone.is_walkable(nx, ny):
                    d = dx * dx + dy * dy
                    if best is None or d < best[0]:
                        best = (d, nx, ny)
        if best is None:
            raise AssertionError(("trash with no walkable tile within reach", zone.name, m, x, y))
        out.append((best[1], best[2], m, lvl))
    return out


def generate_wing(name):
    zone, _b = build_wing(name)
    # PACKS, not lone mobs (Kyle, 14 Nov: "in dungeons enemies are in packs of 4 to 5"): each list is one pull,
    # filled to four or five beside itself.
    from world.dungeon_packs import attach_packs
    door = WING[name]["door"]
    avoid = [door] + [tuple(b[:2]) for b in zone.boss_positions]
    attach_packs(zone, [_snap(zone, p) for p in WING[name]["trash"]], avoid=avoid)
    from tools.handbuilt_vot_caves import register_baked
    register_baked(zone, BAKED[name])
    for (x, y) in zone.chest_spots:
        if zone.get_tile(x, y, "interaction") is None:
            zone.set_tile(x, y, "chest", "interaction")
    return zone


def generate_grounds():
    zone, _b = build_grounds()
    from tools.handbuilt_vot_caves import register_baked
    register_baked(zone, BAKED[GROUNDS])
    return zone


if __name__ == "__main__":
    for n in WING:
        z, b = build_wing(n)
        print(n, z.width, "x", z.height, "| bosses", len(z.boss_positions), "| reachable",
              len(b.reachable(tuple((WING[n]["door"][0], WING[n]["door"][1] - 2)))))
    z, b = build_grounds()
    print(GROUNDS, z.width, "x", z.height, "| reachable", len(b.reachable((GROUNDS_GATE[0], GROUNDS_GATE[1] - 2))))
