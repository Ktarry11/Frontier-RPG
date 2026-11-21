"""
Hand-built THE ASCENDANT SPIRE, level 60: the second of the two dungeons in the Citadel of Ascent on the Ascendant
Bastions, and the Ascendancy's command. Its door is the citadel's north gate, the tall white gate under the keep
(tools/handbuilt_worldtree_ascendant_bastions.PORTALS (160,54)). The Gravity Foundry (56-58) is the south gate.

Kyle, 21 Nov 2026: "For the Bastion, let's have a 'Hellfire Citadel' like style. We can have a lvl 56-58 and a lvl
60 dungeon. Both into one mega structure but different entrances. Each dungeon will have around 8-9 bosss over two
floors." The Foundry is where the Ascendancy builds; the Spire is where it gives orders. Ascendant-General Maelis Ardane
isn't here (she's the Fading Firmament's): her right hand is, and he's the last fight.

THE HALLS OF ASCENT (180x150), 60. In at the top from the north gate, out by the great stair at the bottom.
    the Muster Yard (Kaine Vorr drills his recruits) -> west down the Lancer Halls (Aris Thane rides the length of
    them) or east along the Storm Gallery, open to the sky (the Storm Choir) -> either way round into the Inquisitorium
    (Seren Vash) -> the great stair up. The Burning Archive sits between, off the Inquisitorium's north door, and its
    Censor is optional.
        1 Drillmaster Kaine Vorr          the drill: shield wall, and he calls his recruits in
        2 Lance-Commander Aris Thane      mounted: the charge down the hall, and the lance through the front line
        3 The Storm Choir                 three callers, one voice: the storm builds while they sing
        4 Archivist-Censor Mallen Roe     (optional) burns what he's told to, and you with it
        5 High Inquisitor Seren Vash      the censer, the question, and the cell for whoever won't answer

THE COMMAND SPIRE (180x150), 60. Up the stair into the top of the keep.
    the Stair Head -> the Aegis Hall (the Aegis Engine) -> west to the War Room (Dravin Kell at the map table) or east
    along the Guard's Walk (Corvo and Lysse, the Exarch's own guard) -> either way up into the Exarch's Sanctum, under
    the open sky -> the fast exit down to the parade ground
        6 The Aegis Engine                the shield over the whole keep: drones, and a dome you fight inside
        7 Warmarshal Dravin Kell          calls the guns: bombardment, and orders for whoever's left standing
        8 The Ascendant Guard             Corvo and Lysse, one fight: shield and blade
        9 Exarch Lucan Thessaly           the general's right hand: crystal, light, and the sky itself

HARD CONTRACTS (world/portal_manager.py)
  DOOR (90,1) <-> the Bastions' north gate (160,54)
  STAIR_DOWN (90,147) on the Halls of Ascent <-> STAIR_UP (90,147) on the Command Spire (it's a stair up, but it's
  the same kind of door)
  FAST_EXIT (90,2) on the Command Spire -> the Bastions, past the Exarch
"""
from tools import citadel_dungeon_kit as K

NAME = "The Ascendant Spire"
HALLS, COMMAND = NAME, "The Ascendant Spire: The Command Spire"
FLOORS = (HALLS, COMMAND)
BAKED = {HALLS: "assets/tiles/sky/baked_ascendant_spire", COMMAND: "assets/tiles/sky/baked_command_spire"}
REGION = "The Ascendant Bastions"
DESC = {
    HALLS: "The halls inside the Citadel of Ascent's keep, where the Ascendancy drills its lancers, sings up its "
           "storms and questions whoever it's caught.",
    COMMAND: "The top of the keep, the Ascendancy's command, where the general's right hand gives her orders.",
}
BLD = "assets/buildings/"
SKP = "assets/tiles/sky/props/"
ENT = "assets/tiles/cave_entrances/"
COLUMN = BLD + "ae_winged_column.png"

DOOR = (90, 1)
STAIR_DOWN = (90, 147)
STAIR_UP = (90, 147)
FAST_EXIT = (90, 2)

FLOOR = {
    HALLS: dict(
        size=(180, 150), start=(90, 5),
        rooms={
            "The Muster Yard":    ("rect", 60, 4, 120, 34, 3),
            "The Lancer Halls":   ("rect", 10, 20, 44, 104, 3),
            "The Storm Gallery":  ("rect", 136, 14, 174, 104, 3),
            "The Burning Archive": ("rect", 64, 46, 116, 84, 2),
            "The Inquisitorium":  ("rect", 62, 100, 118, 140, 3),
        },
        # the Storm Gallery is open to the sky down its east side
        deep=[("rect", 162, 18, 174, 100)],
        land=[],
        passages=[([(90, 0), (90, 7)], 2),                       # in from the north gate
                  ([(62, 20), (42, 20)], 3),                     # the Muster Yard -> the Lancer Halls
                  ([(118, 20), (138, 20)], 3),                   # the Muster Yard -> the Storm Gallery
                  ([(27, 102), (27, 120), (64, 120)], 3),        # the Lancer Halls -> the Inquisitorium
                  ([(150, 102), (150, 120), (116, 120)], 3),     # the Storm Gallery -> the Inquisitorium
                  ([(90, 102), (90, 82)], 2),                    # the Inquisitorium -> the Burning Archive
                  ([(90, 138), (90, 148)], 2)],                  # the great stair up, past the Inquisitor
        cells=[(48, 40, 58, 50), (124, 40, 132, 50), (124, 124, 134, 134)],
        cell_links=[([(42, 45), (50, 45)], 1), ([(138, 45), (130, 45)], 1), ([(116, 129), (126, 129)], 1)],
        pillars=[(18, 32), (34, 32), (18, 52), (34, 52), (18, 72), (34, 72),
                 (70, 108), (108, 108), (70, 130), (108, 130)],
        bosses=[(90, 26, "Drillmaster Kaine Vorr"), (27, 92, "Lance-Commander Aris Thane"),
                (150, 60, "The Storm Choir"), (90, 56, "Archivist-Censor Mallen Roe"),
                (90, 130, "High Inquisitor Seren Vash")],
        pack={},
        final="High Inquisitor Seren Vash",
        doors=[DOOR, STAIR_DOWN],
        dressing=[(ENT + "ent_exit_crypt_stairs.png", 90, 4, 5, False),
                  # the Muster Yard: the dummies, the standards, the armour racks
                  (SKP + "ab_training_dummy.png", 74, 14, 3, "core"), (SKP + "ab_training_dummy.png", 82, 14, 3, "core"),
                  (SKP + "ab_training_dummy.png", 98, 14, 3, "core"), (SKP + "ab_training_dummy.png", 106, 14, 3, "core"),
                  (SKP + "ab_armour_rack.png", 66, 30, 3, "core"), (SKP + "ab_armour_rack.png", 114, 30, 3, "core"),
                  (SKP + "ab_standard.png", 66, 10, 4, "core"), (SKP + "ab_standard.png", 114, 10, 4, "core"),
                  # the Lancer Halls: lance racks down both walls
                  (SKP + "ab_lance_rack.png", 14, 42, 3, "core"), (SKP + "ab_lance_rack.png", 40, 42, 3, "core"),
                  (SKP + "ab_lance_rack.png", 14, 62, 3, "core"), (SKP + "ab_lance_rack.png", 40, 62, 3, "core"),
                  (SKP + "ab_lance_rack.png", 14, 82, 3, "core"), (SKP + "ab_lance_rack.png", 40, 82, 3, "core"),
                  # the Storm Gallery: the storm pillars along the open edge
                  (SKP + "ab_storm_pillar.png", 158, 30, 5, "core"), (SKP + "ab_storm_pillar.png", 158, 60, 5, "core"),
                  (SKP + "ab_storm_pillar.png", 158, 90, 5, "core"), (SKP + "ab_sky_window.png", 142, 20, 5, "core"),
                  # the Burning Archive
                  (SKP + "ab_plate_shelves.png", 70, 50, 4, "core"), (SKP + "ab_plate_shelves.png", 80, 50, 4, "core"),
                  (SKP + "ab_plate_shelves.png", 100, 50, 4, "core"), (SKP + "ab_plate_shelves.png", 110, 50, 4, "core"),
                  (SKP + "ab_scroll_brazier.png", 76, 66, 3, "core"), (SKP + "ab_scroll_brazier.png", 104, 66, 3, "core"),
                  (SKP + "ab_lectern.png", 90, 64, 3, "core"),
                  # the Inquisitorium: the chair, the cages, the braziers
                  (SKP + "ab_interrogation_chair.png", 90, 136, 3, "core"),
                  (SKP + "ab_cage.png", 68, 118, 3, "core"), (SKP + "ab_cage.png", 112, 118, 3, "core"),
                  (SKP + "ab_cage.png", 68, 124, 3, "core"), (SKP + "ab_cage.png", 112, 124, 3, "core"),
                  (SKP + "ab_scroll_brazier.png", 80, 130, 3, "core"), (SKP + "ab_scroll_brazier.png", 100, 130, 3, "core")],
    ),
    COMMAND: dict(
        size=(180, 150), start=(90, 143),
        rooms={
            "The Stair Head":       ("rect", 70, 124, 110, 144, 2),
            "The Aegis Hall":       ("lobes", [(90, 100, 24, 16)]),
            "The War Room":         ("rect", 10, 60, 56, 104, 3),
            "The Guard's Walk":     ("rect", 124, 40, 170, 104, 3),
            "The Exarch's Sanctum": ("rect", 40, 6, 140, 36, 4),
        },
        # the Sanctum is open to the sky at either end
        deep=[("rect", 40, 6, 52, 36), ("rect", 128, 6, 140, 36)],
        land=[],
        passages=[([(90, 148), (90, 142)], 2),                   # up the great stair from the Halls of Ascent
                  ([(90, 126), (90, 114)], 3),                   # the Stair Head -> the Aegis Hall
                  ([(68, 98), (54, 98)], 3),                     # the Aegis Hall -> the War Room
                  ([(112, 98), (126, 98)], 3),                   # the Aegis Hall -> the Guard's Walk
                  ([(30, 62), (30, 24), (56, 24)], 3),           # the War Room -> the Sanctum
                  ([(147, 42), (147, 24), (124, 24)], 3),        # the Guard's Walk -> the Sanctum
                  ([(90, 8), (90, 1)], 2)],                      # past the Exarch: the fast exit
        cells=[(2, 112, 12, 122), (172, 108, 178, 118), (150, 8, 160, 16)],
        cell_links=[([(14, 102), (7, 114)], 1), ([(166, 102), (175, 110)], 1), ([(146, 24), (155, 14)], 1)],
        pillars=[(132, 50), (160, 50), (132, 66), (160, 66), (132, 82), (160, 82),
                 (62, 12), (118, 12), (62, 28), (118, 28)],
        bosses=[(90, 92, "The Aegis Engine"), (30, 72, "Warmarshal Dravin Kell"),
                (140, 58, "Ascendant Guard Corvo"), (90, 16, "Exarch Lucan Thessaly")],
        pack={"Ascendant Guard Corvo": [(152, 58, "Ascendant Guard Lysse")]},
        final="Exarch Lucan Thessaly",
        doors=[STAIR_UP, FAST_EXIT],
        dressing=[(SKP + "ab_knight_statue.png", 76, 128, 4, "core"), (SKP + "ab_knight_statue.png", 104, 128, 4, "core"),
                  # the Aegis Hall: the shield domes round the engine
                  (SKP + "ab_shield_dome.png", 72, 96, 3, "core"), (SKP + "ab_shield_dome.png", 108, 96, 3, "core"),
                  (SKP + "ab_shield_dome.png", 78, 110, 3, "core"), (SKP + "ab_shield_dome.png", 102, 110, 3, "core"),
                  # the War Room: the table, the chairs, the officers' dinner nobody's eaten
                  (SKP + "ab_war_table.png", 30, 80, 4, "core"), (SKP + "ab_officer_chair.png", 22, 80, 3, "core"),
                  (SKP + "ab_officer_chair.png", 38, 80, 3, "core"), (SKP + "ab_banquet_table.png", 40, 98, 3, "core"),
                  (SKP + "ab_standard.png", 14, 64, 4, "core"), (SKP + "ab_standard.png", 52, 64, 4, "core"),
                  # the Guard's Walk: statues between the columns
                  (SKP + "ab_knight_statue.png", 146, 50, 4, "core"), (SKP + "ab_knight_statue.png", 146, 82, 4, "core"),
                  (SKP + "ab_armour_rack.png", 166, 96, 3, "core"),
                  # the Exarch's Sanctum: the command seat, the vault, the windows on the sky
                  (SKP + "ab_command_seat.png", 90, 11, 5, "core"), (SKP + "ab_vault_door.png", 110, 10, 5, "core"),
                  (SKP + "ab_sky_window.png", 70, 9, 5, "core"), (SKP + "ab_storm_pillar.png", 58, 20, 5, "core"),
                  (SKP + "ab_storm_pillar.png", 122, 20, 5, "core")],
    ),
}

BOSSES = {}


def build_floor(name):
    zone, b = K.build_floor(name, FLOOR[name], DESC[name], REGION, COLUMN)
    BOSSES[name] = {n: (x, y) for (x, y, n) in FLOOR[name]["bosses"]}
    return zone, b


def build_halls_baked():
    return build_floor(HALLS)[0], None


def build_command_baked():
    return build_floor(COMMAND)[0], None


def trash(name):
    T, pack = K.pack_builder()
    if name == HALLS:
        # the Muster Yard
        pack(60, (72, 22, "Spire Recruit"), (76, 24, "Spire Recruit"), (74, 18, "Spire Drill Sergeant"))
        pack(60, (108, 22, "Spire Recruit"), (104, 24, "Spire Recruit"), (106, 18, "Spire Drill Sergeant"))
        # the Lancer Halls
        pack(60, (27, 30, "Spire Lancer"), (22, 34, "Spire Lancer"), (32, 34, "Mounted Spire Lancer"))
        pack(60, (27, 50, "Mounted Spire Lancer"), (22, 56, "Spire Lancer"))
        pack(60, (27, 70, "Spire Lancer"), (32, 74, "Mounted Spire Lancer"), (22, 74, "Spire Drill Sergeant"))
        # the Storm Gallery
        pack(60, (148, 28, "Storm Chorister"), (144, 32, "Spire Warden"), (152, 32, "Storm Chorister"))
        pack(60, (146, 46, "Bound Storm"), (152, 46, "Bound Storm"))
        pack(60, (148, 78, "Storm Chorister"), (144, 84, "Bound Storm"), (152, 84, "Spire Warden"))
        # the Burning Archive
        pack(60, (74, 76, "Ash-Page Wisp"), (78, 80, "Ash-Page Wisp"), (72, 72, "Spire Inquisitor"))
        pack(60, (106, 76, "Ash-Page Wisp"), (102, 80, "Spire Warden"), (108, 72, "Spire Inquisitor"))
        # the Inquisitorium
        pack(60, (76, 108, "Spire Inquisitor"), (80, 112, "Spire Warden"), (72, 112, "Spire Inquisitor"))
        pack(60, (104, 108, "Spire Inquisitor"), (100, 112, "Spire Warden"), (108, 112, "Spire Warden"))
        pack(60, (40, 120, "Spire Lancer"), (46, 120, "Spire Warden"))
        pack(60, (134, 120, "Storm Chorister"), (128, 120, "Spire Warden"))
    else:
        # the Stair Head
        pack(60, (80, 134, "Ascendant Honour Guard"), (84, 136, "Aegis Drone"), (78, 138, "Ascendant Honour Guard"))
        pack(60, (100, 134, "Ascendant Honour Guard"), (96, 136, "Aegis Drone"), (102, 138, "Ascendant Battle-Mage"))
        # the Aegis Hall
        pack(60, (74, 102, "Aegis Drone"), (78, 104, "Aegis Drone"), (72, 106, "Ascendant Battle-Mage"))
        pack(60, (106, 102, "Aegis Drone"), (102, 104, "Aegis Drone"), (108, 106, "Ascendant Honour Guard"))
        # the War Room
        pack(60, (20, 92, "War-Room Strategist"), (26, 94, "Ascendant Honour Guard"), (16, 96, "War-Room Strategist"))
        pack(60, (46, 70, "War-Room Strategist"), (48, 76, "Ascendant Honour Guard"))
        pack(60, (30, 40, "Ascendant Honour Guard"), (30, 48, "Ascendant Battle-Mage"))
        # the Guard's Walk
        pack(60, (140, 94, "Ascendant Honour Guard"), (146, 94, "Exarch's Sentinel"), (152, 94, "Ascendant Honour Guard"))
        pack(60, (140, 74, "Ascendant Battle-Mage"), (152, 74, "Exarch's Sentinel"))
        pack(60, (147, 34, "Exarch's Sentinel"), (147, 28, "Ascendant Battle-Mage"))
        # the Exarch's Sanctum
        pack(60, (64, 20, "Ascendant Battle-Mage"), (68, 24, "Exarch's Sentinel"), (70, 18, "Ascendant Battle-Mage"))
        pack(60, (116, 20, "Ascendant Battle-Mage"), (112, 24, "Exarch's Sentinel"), (110, 18, "Ascendant Honour Guard"))
    return T


def generate(name):
    zone, _b = build_floor(name)
    return K.generate(zone, FLOOR[name], trash(name), BAKED[name])


def generate_halls():
    return generate(HALLS)


def generate_command():
    return generate(COMMAND)


if __name__ == "__main__":
    for n in FLOORS:
        z, _b = build_floor(n)
        walk = sum(z.is_walkable(x, y) for y in range(z.height) for x in range(z.width))
        print(n, z.width, "x", z.height, "| walkable", walk, "| bosses", len(z.boss_positions))
