"""
Hand-built Hearthglen, levels 58-60 (docs/plaguelands_design.md: "Town and citadel: fight up through the occupied
streets of Hearthglen, then Mardenholde Keep. Ten or more bosses."). STRUCTURE ONLY, like tools/handbuilt_stratholme.py:
nothing is wired in until Kyle's dungeon tiles land.

Kyle, 16 Nov 2026: "Hearthglen can be 2 layers as well". Two maps: the town, climbing the hill in terraces, and the
keep at the top. The feet token of the T0 set drops here (20% a boss, always from the last). Scarlet kills pay the
Order of the Pale Flame with no cap. The last boss is the Earth-born Grand Crusader, Victor Hale, and he can take a
second form with the boss phases (entities/monster.py) when Kyle decides what it is.

HEARTHGLEN (140x112), 58-59: the town. In at the gate at the bottom of the hill (from North WPL's road), along the
lower street to the kennels and the infirmary, up to the square and the chapel, and across to the barbican.
        the Hearthglen Gate           1 High Protector Tarsen         holds the gate behind a shield wall
        the Kennels                   2 Huntsman Radley               his hounds come first, and keep coming
        the Infirmary                 3 Chirurgeon Maeve Ostrowski    an Earth-born field surgeon; her saws bleed
        the Chapel of the Flame       4 High Clerist Hendrick         burns the floor and heals himself through it
        the Barbican                  5 High Protector Lorik          the keep's gate: a hammer and a stun

MARDENHOLDE KEEP (120x100), 59-60: the citadel. Through the keep gate into the muster yard, the armoury and the
barracks off it, the great hall, and the stair up the tower.
        the Muster Yard               6 Scarlet Commander Marjhan     drills the yard's soldiers on you
        the Armoury                   7 Armsmaster Grell              changes weapons as the fight goes
        the Barracks                  8 Drillmaster Osric Pell        a whistle, and the barracks empties
        the Great Hall                9 High General Abbendis         the general who let Hale take her keep
        the Tower Top                10 Grand Crusader Victor Hale    the last boss; past him, the fast exit (one way)
"""
from tools.plaguelands_dungeon_kit import build_floor, generate_floor, preview

TOWN = "Hearthglen"
KEEP = "Hearthglen: Mardenholde Keep"
FLOORS = (TOWN, KEEP)
REGION = "Western Plaguelands North"
BAKED = {TOWN: "assets/tiles/hearthglen/baked_town", KEEP: "assets/tiles/hearthglen/baked_keep"}
LEVELS = {TOWN: [58, 59], KEEP: [59, 60]}
#: the door in North WPL (tools/handbuilt_wpl_north.LATER_PORTALS)
OUTSIDE = {TOWN: (100, 6)}

FLOOR = {
    TOWN: dict(
        size=(140, 112),
        desc="Hearthglen, the Scarlet Crusade's town on the hill: the lower street, the kennels and the infirmary, "
             "the square and the chapel, and the barbican under the keep.",
        rooms={"The Hearthglen Gate": ("rect", 58, 94, 82, 109, 2),
               "The Kennels": ("rect", 4, 66, 30, 84, 2),
               "The Infirmary": ("rect", 110, 64, 136, 84, 2),
               "The Town Square": ("rect", 50, 40, 90, 60, 3),
               "The Chapel of the Flame": ("rect", 56, 16, 84, 34, 2),
               "The Barbican": ("rect", 98, 10, 126, 28, 2)},
        links=[# the lower street, out from the gate to either end of the hill
               ([(58, 98), (40, 94), (24, 90), (16, 84)], 3), ([(82, 98), (100, 94), (116, 90), (124, 84)], 3),
               # the upper street, back across the hill above it
               ([(16, 66), (28, 58), (50, 52)], 3), ([(124, 64), (110, 58), (90, 52)], 3),
               ([(70, 40), (70, 34)], 2),
               ([(90, 44), (102, 36), (110, 28)], 2)],
        solids=[(67, 47, 73, 53),                               # the square's fountain
                (10, 70, 14, 74), (20, 70, 24, 74),             # the kennel runs
                (116, 68, 120, 72), (126, 68, 130, 72),         # the infirmary's wards
                (64, 98, 66, 100), (74, 98, 76, 100)],          # the gatehouse's towers
        pillars=[(61, 20), (77, 20), (61, 28), (77, 28)],
        doors={"in": (70, 109), "down": (112, 12)},
        bosses=[(70, 98, "High Protector Tarsen"), (17, 78, "Huntsman Radley"),
                (124, 76, "Chirurgeon Maeve Ostrowski"), (70, 22, "High Clerist Hendrick"),
                (112, 18, "High Protector Lorik")],
        final="High Protector Lorik",
        chests=[(6, 82), (134, 82), (82, 18)],
        trash=[[(62, 104, "Hearthglen Templar", 58), (78, 104, "Hearthglen Arbalest", 58)],
               [(44, 94, "Hearthglen Zealot", 58), (36, 92, "Hearthglen Templar", 58)],
               [(96, 94, "Hearthglen Cleric", 58), (104, 92, "Hearthglen Arbalest", 58)],
               [(8, 80, "Hearthglen Mastiff", 58), (26, 80, "Hearthglen Mastiff", 58)],
               [(114, 80, "Hearthglen Field Medic", 58), (132, 78, "Hearthglen Templar", 58)],
               [(30, 58, "Hearthglen Zealot", 59), (40, 54, "Hearthglen Arbalest", 59)],
               [(108, 58, "Hearthglen Cleric", 59), (100, 54, "Hearthglen Zealot", 59)],
               [(56, 44, "Hearthglen Templar", 59), (84, 56, "Hearthglen Cleric", 59)],
               [(60, 30, "Hearthglen Zealot", 59), (80, 30, "Hearthglen Cleric", 59)],
               [(104, 22, "Hearthglen Templar", 59), (120, 22, "Hearthglen Arbalest", 59)]],
    ),
    KEEP: dict(
        size=(120, 100),
        desc="Mardenholde Keep, the citadel at the top of Hearthglen: the muster yard, the armoury and the barracks, "
             "the great hall, and the tower where the Grand Crusader keeps his rooms.",
        rooms={"The Keep Gate": ("rect", 50, 86, 70, 97, 2),
               "The Muster Yard": ("rect", 20, 52, 100, 86, 4),
               "The Armoury": ("rect", 3, 54, 15, 80, 2),
               "The Barracks": ("rect", 105, 54, 117, 80, 2),
               "The Great Hall": ("rect", 30, 20, 90, 44, 3),
               "The Tower Top": ("lobes", [(100, 10, 9, 7)])},
        links=[([(16, 66), (20, 66)], 2), ([(104, 66), (100, 66)], 2), ([(60, 52), (60, 44)], 3),
               # the tower stair, narrow and climbing out of the hall's east end
               ([(90, 32), (98, 28), (100, 17)], 2)],
        solids=[(56, 66, 64, 72),                         # the yard's statue
                (3, 66, 9, 68), (111, 66, 117, 68)],     # each side room's racks and bunks across its middle
        pillars=[(38, 26), (50, 26), (68, 26), (80, 26), (38, 36), (50, 36), (68, 36), (80, 36)],
        doors={"up": (60, 97), "exit": (108, 10)},
        bosses=[(60, 78, "Scarlet Commander Marjhan"), (9, 60, "Armsmaster Grell"),
                (111, 74, "Drillmaster Osric Pell"), (60, 30, "High General Abbendis"),
                (100, 9, "Grand Crusader Victor Hale")],
        final="Grand Crusader Victor Hale",
        chests=[(6, 78), (114, 56), (34, 40)],
        trash=[[(54, 90, "Mardenholde Halberdier", 59), (66, 90, "Mardenholde Halberdier", 59)],
               [(30, 60, "Mardenholde Knight", 59), (36, 78, "Mardenholde Crossbowman", 59)],
               [(90, 60, "Mardenholde Knight", 59), (84, 78, "Mardenholde Battle Priest", 59)],
               [(46, 58, "Mardenholde Crossbowman", 59), (74, 58, "Mardenholde Halberdier", 59)],
               [(6, 72, "Mardenholde Knight", 60), (12, 56, "Mardenholde Halberdier", 60)],
               [(114, 62, "Mardenholde Crossbowman", 60), (108, 78, "Mardenholde Knight", 60)],
               [(36, 30, "Mardenholde Battle Priest", 60), (44, 40, "Mardenholde Knight", 60)],
               [(84, 30, "Mardenholde Halberdier", 60), (76, 40, "Mardenholde Battle Priest", 60)],
               [(96, 22, "Mardenholde Knight", 60), (104, 16, "Mardenholde Crossbowman", 60)]],
    ),
}


#: Kyle's dungeon props (sheet 8), set into the rooms by tools/plaguelands_dungeon_kit.auto_dress:
#: room -> [(prop, height in tiles, "wall" | "free" | "floor", how many)]
FLOOR[TOWN]["decor"] = {
    "The Hearthglen Gate": [("hg_banner", 4, "wall", 2), ("dg_wall_torch", 3, "wall", 2)],
    "The Kennels": [("hg_kennel", 3, "wall", 3), ("hg_kennel", 3, "free", 1)],
    "The Infirmary": [("scholo_alchemy_table", 3, "free", 1), ("scholo_specimen_jars", 4, "wall", 2),
                      ("sm_supply_crates", 3, "wall", 1)],
    "The Town Square": [("strat_fountain", 4, "free", 1), ("hg_banner", 4, "wall", 3),
                        ("strat_grain_cart", 3, "free", 1)],
    "The Chapel of the Flame": [("sm_pew", 3, "free", 4), ("hg_organ", 4, "wall", 1), ("hg_choir_stall", 3, "wall", 2),
                                ("sm_altar", 4, "wall", 1), ("hg_reliquary", 4, "wall", 1)],
    "The Barbican": [("sm_weapon_rack", 4, "wall", 2), ("hg_banner", 4, "wall", 2)],
}
FLOOR[KEEP]["decor"] = {
    "The Keep Gate": [("hg_banner", 4, "wall", 2), ("dg_wall_torch", 3, "wall", 2)],
    "The Muster Yard": [("sm_training_dummy", 4, "free", 3), ("sm_weapon_rack", 4, "wall", 2)],
    "The Armoury": [("sm_weapon_rack", 4, "wall", 4), ("sm_supply_crates", 3, "wall", 2)],
    "The Barracks": [("sm_supply_crates", 3, "wall", 2), ("sm_training_dummy", 4, "free", 1)],
    "The Great Hall": [("hg_throne", 4, "wall", 1), ("hg_banner", 4, "wall", 4), ("hg_war_table", 3, "free", 1),
                       ("dg_wall_torch", 3, "wall", 2)],
    "The Tower Top": [("hg_banner", 4, "wall", 2), ("sm_candelabra", 4, "floor", 2)],
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
