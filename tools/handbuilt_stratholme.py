"""
Hand-built Stratholme, both halves, levels 57-60 (docs/plaguelands_design.md). STRUCTURE ONLY: the maps, rooms, doors,
bosses' marks and trash seeds. Nothing here is wired into the game until Kyle's dungeon tiles and creatures land
("The Dungeons can wait as we don't have the tiles"); then it takes the Scarlet Monastery's path (a content builder,
a baker, the doors in portal_manager, the fast exit in tools/build_fast_exits.py).

Kyle, 16 Nov 2026: "Ensure that scholomance and Stratholme live up to their wow parts. Multiple bosses." And: "Dead is
two layers as it's massive. Live is one layer as its smaller." So classic's whole roster, in classic's order, seven a
side, through classic's streets (warcraft.wiki.gg's subzones; the classic guides for who stands where). The chest
token of the T0 set drops on both sides (20% a boss, always from the last). The Scarlet side pays the Order of the
Pale Flame, the Scourge side the Argent Dawn.

THE MAIN GATE: STRATHOLME (150x112), the living side, one map. The city's streets, then the Scarlet Bastion.
    the Main Gate (in, from East EPL's road) -> King's Square -> Market Row -> Crusaders' Square -> the Bastion:
    the Hall of the Crimson Legion, the Hoard west, the Archives east, the Hall of High Command north
        the Main Gate                 1 Skul                      a skeleton the gate guard never buried
        King's Square                 2 Hearthsinger Forresten    a bard's ghost: his song takes the party's nerve
        Market Row                    3 The Unforgiven            a death knight's shade with his court around him
        Crusaders' Square             4 Timmy the Cruel           the ghoul that runs out of the side street
        the Hoard                     5 Cannon Master Willey      the Bastion's cannons and the riflemen who load them
        the Archives                  6 Archivist Galford         burns the archive rather than let you read it
        the Hall of High Command      7 Grand Crusader Dathrohan  at 40% he is Balnazzar (the boss phases)

THE SERVICE ENTRANCE (150x100), the dead side's first floor: the streets the Scourge holds, and its three ziggurats.
    the Service Entrance (in) -> Elders' Square and the Alonsus Chapel -> the Gauntlet Gate -> the Gauntlet -> the
    three ziggurats off it -> the Portcullis -> down to Slaughter Square
        Elders' Square                8 Magistrate Barthilas      the city's magistrate, still keeping the key
        the Gauntlet                  9 Stonespine                a gargoyle that walks the street between ziggurats
        Nerub'enkan's Ziggurat       10 Nerub'enkan               crypt lord: scarabs and webs
        Anastari's Ziggurat          11 Baroness Anastari         banshee: she possesses one of you
        Maleki's Ziggurat            12 Maleki the Pallid         lich: frost, and drains your mana

SLAUGHTER SQUARE (110x96), the dead side's second floor: the square and the Slaughterhouse.
    the Portcullis Yard (up) -> Slaughter Square, its houses and its abomination pens -> the Slaughterhouse ->
    the fast exit, one way out to East EPL past the Baron
        Slaughter Square             13 Ramstein the Gorger       the abomination the square is kept for
        the Slaughterhouse           14 Baron Rivendare           the Baron, and his deathcharger
"""
from tools.plaguelands_dungeon_kit import build_floor, generate_floor, preview

LIVE = "Stratholme"
DEAD_1 = "Stratholme: Service Entrance"
DEAD_2 = "Stratholme: Slaughter Square"
FLOORS = (LIVE, DEAD_1, DEAD_2)
REGION = "Eastern Plaguelands West"
BAKED = {LIVE: "assets/tiles/stratholme/baked_live", DEAD_1: "assets/tiles/stratholme/baked_service_entrance",
         DEAD_2: "assets/tiles/stratholme/baked_slaughter_square"}
LEVELS = {LIVE: [57, 59], DEAD_1: [58, 59], DEAD_2: [59, 60]}
#: where each half's door is in East EPL's west map (tools/handbuilt_epl_west.LATER_PORTALS)
OUTSIDE = {LIVE: (40, 5), DEAD_1: (88, 5)}

FLOOR = {
    LIVE: dict(
        size=(150, 112),
        desc="Stratholme's streets from the Main Gate to the Scarlet Bastion, where the Crusade still holds the east "
             "of the city against the dead in the west of it.",
        rooms={"The Main Gate": ("rect", 14, 92, 36, 108, 2),
               "King's Square": ("rect", 8, 46, 62, 84, 4),
               "Market Row": ("rect", 62, 59, 100, 69, 0),
               # the Row's shops, two a side, each open to the street
               "The Baker's": ("rect", 65, 49, 75, 58, 1), "The Smithy": ("rect", 83, 49, 93, 58, 1),
               "The Apothecary": ("rect", 70, 70, 80, 79, 1), "The Postmaster's": ("rect", 86, 70, 96, 79, 1),
               "Crusaders' Square": ("rect", 100, 44, 140, 82, 4),
               "Hall of the Crimson Legion": ("rect", 96, 20, 128, 34, 2),
               "The Hoard": ("rect", 70, 18, 90, 32, 2),
               "The Archives": ("rect", 132, 16, 147, 34, 2),
               "Hall of High Command": ("rect", 98, 3, 130, 13, 2)},
        links=[([(25, 92), (25, 84)], 3),
               ([(112, 44), (112, 34)], 3), ([(96, 26), (90, 26)], 2), ([(128, 26), (132, 26)], 2),
               ([(112, 20), (112, 13)], 3),
               ],
        solids=[(32, 61, 38, 68),          # King's Square's fountain
                (117, 59, 123, 66),        # the Crusaders' monument
                (8, 46, 16, 52), (54, 46, 62, 52)],   # the square's corner houses
        pillars=[(102, 23), (108, 23), (116, 23), (122, 23), (102, 30), (108, 30), (116, 30), (122, 30),
                 (104, 6), (122, 6)],
        doors={"in": (25, 108)},
        bosses=[(25, 98, "Skul"), (22, 58, "Hearthsinger Forresten"), (82, 64, "The Unforgiven"),
                (106, 62, "Timmy the Cruel"), (80, 24, "Cannon Master Willey"), (140, 24, "Archivist Galford"),
                (114, 8, "Grand Crusader Dathrohan")],
        final="Grand Crusader Dathrohan",
        chests=[(70, 51), (91, 77), (74, 30), (144, 32)],
        trash=[[(22, 100, "Skeletal Guardian", 57), (28, 102, "Plague Ghoul", 57)],
               [(18, 72, "Ghostly Citizen", 57), (24, 76, "Spectral Citizen", 57)],
               [(44, 56, "Skeletal Berserker", 57), (50, 60, "Plague Ghoul", 57)],
               [(44, 76, "Wailing Banshee", 58), (50, 74, "Ghostly Citizen", 58)],
               [(68, 64, "Fleshflayer Ghoul", 58), (72, 62, "Patchwork Horror", 58)],
               [(92, 64, "Vengeful Phantom", 58), (96, 66, "Rockwing Gargoyle", 58)],
               [(106, 50, "Crimson Guardsman", 58), (112, 52, "Crimson Conjuror", 58)],
               [(130, 52, "Crimson Initiate", 58), (134, 56, "Crimson Gallant", 58)],
               [(128, 74, "Crimson Defender", 58), (132, 70, "Crimson Priest", 58)],
               [(110, 76, "Crimson Rifleman", 58), (114, 72, "Crimson Monk", 58)],
               [(104, 26, "Crimson Battle Mage", 59), (110, 28, "Crimson Gallant", 59)],
               [(120, 26, "Crimson Sorcerer", 59), (124, 28, "Crimson Guardsman", 59)],
               [(84, 28, "Crimson Rifleman", 59), (76, 22, "Crimson Defender", 59)],
               [(138, 30, "Crimson Inquisitor", 59), (142, 20, "Crimson Monk", 59)],
               [(106, 10, "Crimson Inquisitor", 59), (124, 10, "Crimson Battle Mage", 59)]],
    ),
    DEAD_1: dict(
        size=(150, 100),
        desc="The Scourge's half of Stratholme, in at the service gate: Elders' Square, the Gauntlet and its three "
             "ziggurats, and the portcullis down to Slaughter Square.",
        rooms={"The Service Entrance": ("rect", 120, 84, 140, 97, 2),
               "Elders' Square": ("rect", 96, 50, 144, 80, 4),
               "The Alonsus Chapel": ("rect", 108, 34, 132, 50, 2),
               "The Gauntlet": ("rect", 20, 58, 96, 70, 0),
               "Nerub'enkan's Ziggurat": ("rect", 56, 26, 74, 44, 3),
               "Anastari's Ziggurat": ("rect", 36, 80, 56, 94, 3),
               "Maleki's Ziggurat": ("rect", 18, 26, 38, 44, 3),
               "The Portcullis": ("rect", 4, 54, 18, 74, 2)},
        links=[([(130, 84), (130, 80)], 3),
               ([(64, 44), (64, 58)], 2), ([(46, 70), (46, 80)], 2), ([(28, 44), (28, 58)], 2),
               ([(18, 64), (20, 64)], 2)],
        solids=[(96, 50, 96, 56), (96, 72, 96, 80),     # the Gauntlet Gate: a narrow way through the square's wall
                (126, 58, 134, 66),                      # the square's well-house
                (62, 32, 68, 38), (42, 84, 50, 90), (24, 32, 32, 38),   # each ziggurat's stepped core
                (32, 58, 36, 61), (58, 67, 62, 70), (80, 58, 84, 61)],  # rubble in the Gauntlet
        pillars=[(112, 38), (126, 38), (112, 44), (126, 44)],
        doors={"in": (130, 97), "down": (10, 72)},
        bosses=[(106, 62, "Magistrate Barthilas"), (46, 64, "Stonespine"), (65, 29, "Nerub'enkan"),
                (46, 92, "Baroness Anastari"), (28, 29, "Maleki the Pallid")],
        final="Maleki the Pallid",
        chests=[(110, 36), (140, 76), (72, 42), (38, 92)],
        trash=[[(124, 90, "Ghoul Ravener", 58), (134, 92, "Rockwing Gargoyle", 58)],
               [(104, 74, "Mangled Cadaver", 58), (110, 70, "Broken Cadaver", 58)],
               [(138, 56, "Ghoul Ravener", 58), (134, 72, "Plagued Crypt Crawler", 58)],
               [(118, 46, "Thuzadin Shadowcaster", 58), (122, 40, "Thuzadin Acolyte", 58)],
               [(86, 64, "Crypt Beast", 58), (90, 66, "Undead Scarab", 58)],
               [(72, 62, "Thuzadin Necromancer", 59), (76, 66, "Rockwing Screecher", 59)],
               [(58, 40, "Thuzadin Acolyte", 59), (70, 40, "Plagued Crypt Crawler", 59)],
               [(40, 88, "Thuzadin Acolyte", 59), (52, 88, "Thuzadin Shadowcaster", 59)],
               [(22, 40, "Thuzadin Acolyte", 59), (34, 40, "Thuzadin Necromancer", 59)],
               [(26, 66, "Eye of Naxxramas", 59), (30, 62, "Broken Cadaver", 59)],
               [(10, 60, "Rockwing Gargoyle", 59), (12, 66, "Mangled Cadaver", 59)]],
    ),
    DEAD_2: dict(
        size=(110, 96),
        desc="Slaughter Square, where the Scourge stitches its abominations, and the Slaughterhouse where the Baron "
             "waits.",
        rooms={"The Portcullis Yard": ("rect", 44, 80, 66, 93, 2),
               "Slaughter Square": ("rect", 16, 30, 94, 80, 4),
               "The West Houses": ("rect", 2, 40, 11, 70, 1),
               "The East Houses": ("rect", 99, 40, 108, 70, 1),
               "The Slaughterhouse": ("rect", 34, 4, 76, 24, 3)},
        links=[([(55, 30), (55, 24)], 3), ([(11, 46), (16, 46)], 1), ([(11, 64), (16, 64)], 1),
               ([(99, 46), (94, 46)], 1), ([(99, 64), (94, 64)], 1)],
        solids=[(28, 38, 36, 46), (74, 38, 82, 46), (28, 64, 36, 72), (74, 64, 82, 72),   # the abomination pens
                (2, 54, 11, 56), (99, 54, 108, 56)],                                    # each row of houses split
        pillars=[(40, 8), (68, 8), (40, 18), (68, 18)],
        doors={"up": (55, 93), "exit": (72, 12)},
        bosses=[(55, 52, "Ramstein the Gorger"), (55, 10, "Baron Rivendare")],
        final="Baron Rivendare",
        chests=[(6, 42), (104, 68), (36, 20)],
        trash=[[(50, 84, "Venom Belcher", 59), (60, 84, "Bile Spewer", 59)],
               [(24, 52, "Bile Spewer", 59), (22, 60, "Bile Slime", 59)],
               [(86, 52, "Venom Belcher", 59), (88, 60, "Bile Slime", 59)],
               [(6, 48, "Thuzadin Acolyte", 59), (6, 64, "Thuzadin Acolyte", 59)],
               [(104, 48, "Thuzadin Acolyte", 59), (104, 62, "Thuzadin Acolyte", 59)],
               [(44, 34, "Mindless Undead", 60), (66, 34, "Mindless Undead", 60)],
               [(46, 22, "Black Guard Sentry", 60), (64, 22, "Black Guard Sentry", 60)]],
    ),
}


#: Kyle's dungeon props (sheet 8), set into the rooms by tools/plaguelands_dungeon_kit.auto_dress:
#: room -> [(prop, height in tiles, "wall" | "free" | "floor", how many)]
FLOOR[LIVE]["decor"] = {
    "The Main Gate": [("strat_rubble", 3, "floor", 2), ("dg_wall_torch", 3, "wall", 2)],
    "King's Square": [("strat_stall_burned", 4, "free", 2), ("strat_grain_cart", 3, "free", 2),
                      ("strat_rubble", 3, "floor", 4), ("silver_hand_symbol", 4, "wall", 1)],
    "Market Row": [("strat_stall_burned", 4, "floor", 2), ("strat_rubble", 3, "floor", 2)],
    "The Baker's": [("sm_supply_crates", 3, "wall", 1)], "The Smithy": [("sm_weapon_rack", 4, "wall", 1)],
    "The Apothecary": [("scholo_specimen_jars", 4, "wall", 1)],
    "The Postmaster's": [("sm_supply_crates", 3, "wall", 1)],
    "Crusaders' Square": [("hg_banner", 4, "wall", 3), ("sm_weapon_rack", 4, "wall", 2),
                          ("strat_grain_cart", 3, "free", 2), ("strat_rubble", 3, "floor", 3)],
    "Hall of the Crimson Legion": [("hg_banner", 4, "wall", 4), ("dg_wall_torch", 3, "wall", 3)],
    "The Hoard": [("sm_supply_crates", 3, "wall", 3), ("sc_treasure_chest", 3, "free", 1)],
    "The Archives": [("sm_bookshelf", 4, "wall", 4), ("sm_lectern", 4, "free", 1)],
    "Hall of High Command": [("hg_war_table", 3, "free", 1), ("hg_banner", 4, "wall", 3),
                             ("hg_throne", 4, "wall", 1)],
}
FLOOR[DEAD_1]["decor"] = {
    "The Service Entrance": [("strat_rubble", 3, "floor", 2), ("dg_wall_torch", 3, "wall", 2)],
    "Elders' Square": [("strat_rubble", 3, "floor", 5), ("strat_grain_cart", 3, "free", 1),
                       ("strat_wall", 3, "floor", 2)],
    "The Alonsus Chapel": [("sm_pew", 3, "free", 3), ("sm_altar", 4, "wall", 1), ("sm_saint_statue", 4, "wall", 2)],
    "The Gauntlet": [("strat_rubble", 3, "floor", 4), ("strat_ziggurat_brazier", 4, "floor", 3)],
    "Nerub'enkan's Ziggurat": [("strat_ziggurat_brazier", 4, "floor", 2), ("scourge_bone_chest", 3, "free", 1)],
    "Anastari's Ziggurat": [("strat_ziggurat_brazier", 4, "floor", 2), ("sm_sarcophagus", 3, "free", 1)],
    "Maleki's Ziggurat": [("strat_ziggurat_brazier", 4, "floor", 2), ("scholo_ritual_stone", 3, "free", 1)],
    "The Portcullis": [("dg_wall_torch", 3, "wall", 2)],
}
FLOOR[DEAD_2]["decor"] = {
    "The Portcullis Yard": [("strat_rubble", 3, "floor", 2), ("dg_wall_torch", 3, "wall", 2)],
    "Slaughter Square": [("scholo_golem_table", 3, "free", 2), ("scholo_iron_cage", 4, "floor", 3),
                         ("strat_rubble", 3, "floor", 4), ("strat_ziggurat_brazier", 4, "floor", 2)],
    "The West Houses": [("strat_rubble", 3, "floor", 2)], "The East Houses": [("strat_rubble", 3, "floor", 2)],
    "The Slaughterhouse": [("scholo_golem_table", 3, "free", 1), ("hg_throne", 4, "wall", 1),
                           ("dg_wall_torch", 3, "wall", 3)],
}


def build(name):
    return build_floor(name, FLOOR[name], REGION)


def build_baked(name):
    """The bare floor the painter works from (tools/bake_plaguelands_dungeons.py)."""
    return build_floor(name, FLOOR[name], REGION)


def generate(name):
    """The floor as the game loads it (world/zone_generator.py)."""
    return generate_floor(name, FLOOR[name], REGION, BAKED[name])


if __name__ == "__main__":
    import sys
    out = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    for n in FLOORS:
        z, b = build(n)
        door = z.door_tiles.get("in") or z.door_tiles.get("up")
        print(f"{n}: {z.width}x{z.height} | bosses {len(z.boss_positions)} | reachable "
              f"{len(b.reachable((door[0], door[1] - 2)))}")
        if out:
            preview(z, FLOOR[n], f"{out}/{n.replace(':', '').replace(' ', '_').lower()}.png")
