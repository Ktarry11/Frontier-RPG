"""
Hand-built Scholomance, the Cult of the Damned's school of necromancy in the crypts under Caer Darrow
(docs/plaguelands_design.md: "Scholomance, classic and full"). Two floors, two maps, one dungeon, levels 56-60.

Kyle, 16 Nov 2026: "Ensure that scholomance and Stratholme live up to their wow parts. Multiple bosses". So this one
breaks the four-to-six rule the way Hearthglen does: it has CLASSIC'S WHOLE ROSTER, thirteen bosses in twelve
fights, in classic's rooms and classic's order (warcraft.wiki.gg's subzone list; the classic guides for who stands
where). Trash is fixed, in packs of four or five. The head token of the T0 set drops here (20% a boss, always from
Gandling). Scourge kills pay the Argent Dawn.

The door is on Caer Darrow in South WPL (tools/handbuilt_wpl_south.LATER_PORTALS, (156,128)).

UPPER SCHOLOMANCE (120x100), 56-58: the school's working floor.
    stair down from Caer Darrow (south) -> the Reliquary -> the Herald's Balcony (east, Kirtonos) -> the Hall of
    Secrets (west, Jandice) -> the Chamber of Summoning -> the Great Ossuary (Rattlegore in the bone pit) -> the
    Viewing Room over it (Marduk and Vectus) -> the Laboratory (Ras Frostwhisper) -> the stair down
        the Herald's Balcony           1 Kirtonos the Herald         a gargoyle on the wing: dives, silences
        the Hall of Secrets            2 Jandice Barov               splits into illusions: find the real one
        the Great Ossuary              3 Rattlegore                  a bone giant: knocks the tank flat
        the Viewing Room               4 Marduk Blackpool            a death knight: shadow and fear
                                       5 Vectus                      a student with a flamethrower: fire on the floor
        the Laboratory                 6 Ras Frostwhisper            a lich: freezes, then shatters

LOWER SCHOLOMANCE (120x100), 58-60: the faculty. A great hall with the masters' rooms round it, classic's six.
    stair from the Laboratory (north) -> the Great Hall -> the Coven, the Shadow Vault, the Hall of the Damned
    (west), the Vault of the Ravenian, the Barov Family Vault (east) -> the Headmaster's Study (south)
        the Coven                      7 Instructor Malicia          calls her students in waves
        the Shadow Vault               8 Doctor Theolen Krastinov    the butcher: bleeds and rends
        the Hall of the Damned         9 Lorekeeper Polkelt          plague and corrosive bile: cleanse
        the Vault of the Ravenian     10 The Ravenian                cleaves the whole front line
        the Barov Family Vault        11 Lord Alexei Barov and Lady Illucia Barov, one fight: he rots, she charms
        the Headmaster's Study        12 Darkmaster Gandling         sends you to a cell and fights you alone
"""
from world.tilemap import Tilemap
from tools.dungeon_builder import Builder

UPPER, LOWER = "Scholomance", "Scholomance: Lower Halls"
FLOORS = (UPPER, LOWER)
BAKED = {UPPER: "assets/tiles/scholomance/baked_upper", LOWER: "assets/tiles/scholomance/baked_lower"}
REGION = "Western Plaguelands South"

DP = "assets/tiles/dungeon_props/"
EK = "assets/tiles/eastern_kingdoms/props/"
UF = "assets/tiles/undead_farmland/props/"
PL = "assets/tiles/plaguelands/props/"
COLUMN = "assets/tiles/scarlet_monastery/props/sm_stone_column.png"   # grey stone; Kyle's Scholomance art replaces it

#: the way in from Caer Darrow, and the stair between the floors
DOOR = (60, 97)                       # Upper's south edge; Caer Darrow (156,128) lands here
STAIR_DOWN = (100, 8)                 # Upper's Laboratory -> Lower's stair (60,6)
STAIR_UP = (60, 4)                    # Lower's stair -> back up to the Laboratory
#: past Gandling, one way out to Caer Darrow (Kyle: a fast exit at the end of every multi-tiered dungeon)
FAST_EXIT = (60, 97)

FLOOR = {
    UPPER: dict(
        size=(120, 100), door=DOOR,
        rooms={"The Reliquary": (44, 70, 76, 94, 3), "The Herald's Balcony": (82, 72, 104, 90, 2),
               "Hall of Secrets": (8, 64, 38, 92, 2), "Chamber of Summoning": (10, 30, 40, 56, 3),
               "The Great Ossuary": (46, 30, 80, 60, 4), "The Viewing Room": (86, 30, 112, 52, 2),
               "The Laboratory": (48, 4, 108, 22, 3)},
        corridors=[([(60, 97), (60, 94)], 4), ([(76, 82), (82, 82)], 4), ([(44, 80), (38, 80)], 4),
                   ([(22, 64), (22, 56)], 4), ([(40, 44), (46, 44)], 4), ([(80, 42), (86, 42)], 4),
                   ([(64, 30), (64, 22)], 4)],
        cells=[(2, 40, 8, 48), (112, 74, 118, 82), (24, 14, 32, 22)],
        cell_links=[([(10, 44), (8, 44)], 2), ([(104, 78), (112, 78)], 2), ([(28, 22), (28, 30)], 2)],
        pillars=[(50, 74), (70, 74), (50, 88), (70, 88), (52, 34), (74, 34), (52, 56), (74, 56)],
        bosses=[(94, 80, "Kirtonos the Herald", True), (22, 76, "Jandice Barov", True),
                (63, 46, "Rattlegore", True), (94, 40, "Marduk Blackpool", True), (104, 40, "Vectus", True),
                (78, 12, "Ras Frostwhisper", True)],
        final="Ras Frostwhisper", pack={},
        dressing=[(DP + "skull_pile", 48, 92, 2, False), (DP + "skull_pile", 72, 92, 2, False),
                  (DP + "candelabra", 54, 72, 3, False), (DP + "candelabra", 66, 72, 3, False),
                  (DP + "twilight_altar", 60, 72, 3, "core"),                   # the Reliquary's reliquary
                  (DP + "rf_sacrificial_altar", 99, 76, 3, "core"),             # the herald's brazier
                  (DP + "bbc_bookshelf", 12, 67, 4, "core"), (DP + "bbc_bookshelf", 20, 67, 4, "core"),
                  (DP + "bbc_bookshelf", 28, 67, 4, "core"), (DP + "bbc_bookshelf", 12, 89, 4, "core"),
                  (DP + "bbc_bookshelf", 28, 89, 4, "core"), (DP + "wizard_desk", 30, 78, 3, "core"),
                  (DP + "twilight_altar", 25, 33, 3, "core"), (DP + "candelabra", 16, 34, 3, False),
                  (DP + "candelabra", 34, 34, 3, False), (DP + "skull_pile", 14, 52, 2, False),
                  (DP + "skull_pile", 50, 36, 2, False), (DP + "skull_pile", 76, 38, 2, False),
                  (DP + "skull_pile", 52, 54, 2, False), (DP + "skull_pile", 72, 56, 2, False),
                  (DP + "sarcophagus", 90, 48, 3, "core"), (DP + "sarcophagus", 108, 48, 3, "core"),
                  (DP + "wizard_desk", 56, 8, 3, "core"), (DP + "wizard_desk", 90, 8, 3, "core"),
                  (DP + "rf_prison_cage", 54, 18, 3, "core"), (DP + "bbc_bookshelf", 70, 6, 4, "core"),
                  (DP + "candelabra", 64, 18, 3, False), (DP + "candelabra", 92, 18, 3, False)],
        trash=[[(56, 90, "Scholomance Student", 56), (64, 90, "Scholomance Neophyte", 56),
                (60, 86, "Scholomance Student", 56)],
               [(52, 80, "Plagued Hatchling", 56), (56, 78, "Plagued Hatchling", 56)],
               [(68, 80, "Plagued Hatchling", 56), (64, 78, "Plagued Hatchling", 56)],
               [(88, 84, "Scholomance Necrolyte", 57), (92, 86, "Scholomance Student", 57)],
               [(30, 84, "Scholomance Neophyte", 57), (34, 74, "Scholomance Necrolyte", 57)],
               [(14, 78, "Scholomance Student", 57), (14, 84, "Scholomance Neophyte", 57)],
               [(20, 46, "Scholomance Dark Summoner", 57), (26, 42, "Risen Guard", 57),
                (30, 48, "Scholomance Necrolyte", 57)],
               [(54, 40, "Reanimated Corpse", 57), (58, 52, "Risen Guard", 57)],
               [(72, 48, "Reanimated Corpse", 57), (70, 40, "Necrofiend", 57)],
               [(98, 46, "Scholomance Dark Summoner", 58), (92, 34, "Risen Guard", 58)],
               [(58, 14, "Necrofiend", 58), (66, 12, "Scholomance Dark Summoner", 58)],
               [(92, 14, "Risen Guard", 58), (98, 18, "Scholomance Necrolyte", 58)]],
    ),
    LOWER: dict(
        size=(120, 100), door=STAIR_UP,
        rooms={"The Stairwell": (52, 2, 68, 14, 2), "The Great Hall": (40, 30, 80, 66, 4),
               "The Coven": (6, 22, 30, 40, 2), "The Shadow Vault": (6, 48, 30, 64, 2),
               "Hall of the Damned": (6, 72, 32, 92, 2), "Vault of the Ravenian": (90, 22, 114, 40, 2),
               "Barov Family Vault": (88, 50, 114, 70, 2), "The Headmaster's Study": (46, 76, 74, 96, 3)},
        corridors=[([(60, 14), (60, 30)], 4), ([(40, 34), (30, 34)], 4), ([(40, 56), (30, 56)], 4),
                   ([(44, 66), (44, 82), (32, 82)], 4), ([(80, 34), (90, 34)], 4), ([(80, 60), (88, 60)], 4),
                   ([(60, 66), (60, 76)], 4)],
        cells=[(108, 82, 116, 90), (2, 2, 10, 10), (84, 6, 92, 14)],
        cell_links=[([(100, 70), (100, 78), (108, 86)], 2), ([(6, 22), (6, 10)], 2), ([(94, 24), (88, 20), (88, 14)], 2)],
        pillars=[(46, 36), (74, 36), (46, 60), (74, 60), (52, 80), (68, 80)],
        bosses=[(18, 30, "Instructor Malicia", True), (18, 56, "Doctor Theolen Krastinov", True),
                (19, 84, "Lorekeeper Polkelt", True), (102, 30, "The Ravenian", True),
                (100, 58, "Lord Alexei Barov", True), (60, 88, "Darkmaster Gandling", True)],
        final="Darkmaster Gandling",
        pack={"Lord Alexei Barov": [(105, 58, "Lady Illucia Barov")]},
        dressing=[(DP + "candelabra", 54, 6, 3, False), (DP + "candelabra", 66, 6, 3, False),
                  (DP + "twilight_altar", 60, 48, 3, "core"),                   # the hall's centre
                  (DP + "skull_pile", 44, 44, 2, False), (DP + "skull_pile", 76, 52, 2, False),
                  (DP + "bbc_bookshelf", 10, 25, 4, "core"), (DP + "bbc_bookshelf", 26, 25, 4, "core"),
                  (DP + "wizard_desk", 18, 36, 3, "core"),
                  (DP + "rf_tool_rack", 10, 51, 3, "core"), (DP + "rf_sacrificial_altar", 24, 60, 3, "core"),
                  (DP + "rf_shackle_frame", 10, 60, 4, "core"),
                  (DP + "sarcophagus", 10, 76, 3, "core"), (DP + "sarcophagus", 28, 76, 3, "core"),
                  (DP + "skull_pile", 12, 90, 2, False), (DP + "skull_pile", 26, 90, 2, False),
                  (DP + "skull_pile", 94, 26, 2, False), (DP + "skull_pile", 110, 36, 2, False),
                  (DP + "bbc_throne", 100, 52, 3, "core"), (DP + "banquet_table", 96, 66, 3, "core"),
                  (DP + "bbc_candelabra", 92, 54, 3, False), (DP + "bbc_candelabra", 110, 54, 3, False),
                  (DP + "wizard_desk", 60, 92, 3, "core"), (DP + "bbc_bookshelf", 50, 79, 4, "core"),
                  (DP + "bbc_bookshelf", 70, 79, 4, "core"), (DP + "bbc_candelabra", 52, 92, 3, False),
                  (DP + "bbc_candelabra", 68, 92, 3, False)],
        trash=[[(56, 10, "Spectral Tutor", 58), (64, 10, "Spectral Researcher", 58)],
               [(56, 22, "Risen Construct", 58), (64, 22, "Bone Minion", 58)],
               [(48, 40, "Scholomance Necromancer", 58), (52, 44, "Risen Aberration", 58)],
               [(72, 40, "Spectral Researcher", 58), (68, 44, "Scholomance Necromancer", 58)],
               [(48, 58, "Risen Construct", 59), (54, 62, "Spectral Tutor", 59)],
               [(72, 58, "Risen Aberration", 59), (66, 62, "Bone Minion", 59)],
               [(24, 32, "Scholomance Necromancer", 59), (12, 36, "Spectral Tutor", 59)],
               [(24, 58, "Risen Aberration", 59), (12, 52, "Bone Minion", 59)],
               [(26, 82, "Unstable Corpse", 59), (12, 86, "Unstable Corpse", 59)],
               [(96, 34, "Risen Construct", 59), (108, 26, "Spectral Researcher", 59)],
               [(94, 62, "Spectral Tutor", 60), (108, 64, "Scholomance Necromancer", 60)],
               [(52, 84, "Risen Construct", 60), (68, 84, "Scholomance Necromancer", 60)]],
    ),
}


#: Kyle's dungeon props (sheet 8), set into the rooms by tools/plaguelands_dungeon_kit.auto_dress:
#: room -> [(prop, height in tiles, "wall" | "free" | "floor", how many)]
DECOR = {
    UPPER: {
        "The Reliquary": [("hg_reliquary", 4, "wall", 2), ("sm_sarcophagus", 3, "free", 1)],
        "The Herald's Balcony": [("dg_wall_torch", 3, "wall", 2), ("scholo_iron_cage", 4, "wall", 1)],
        "Hall of Secrets": [("sm_bookshelf", 4, "wall", 4), ("scholo_desk", 3, "free", 2)],
        "Chamber of Summoning": [("scholo_ritual_stone", 3, "free", 1), ("sm_candelabra", 4, "floor", 3)],
        "The Great Ossuary": [("scourge_bone_chest", 3, "free", 1), ("scholo_iron_cage", 4, "wall", 2)],
        "The Viewing Room": [("scholo_desk", 3, "free", 2), ("sm_bookshelf", 4, "wall", 2)],
        "The Laboratory": [("scholo_alchemy_table", 3, "free", 2), ("scholo_specimen_jars", 4, "wall", 3),
                           ("scholo_golem_table", 3, "free", 1)],
    },
    LOWER: {
        "The Great Hall": [("dg_wall_torch", 3, "wall", 4), ("sm_candelabra", 4, "floor", 4)],
        "The Coven": [("scholo_desk", 3, "free", 3), ("sm_lectern", 4, "wall", 1)],
        "The Shadow Vault": [("scholo_golem_table", 3, "free", 1), ("scholo_iron_cage", 4, "wall", 2)],
        "Hall of the Damned": [("sm_bookshelf", 4, "wall", 4), ("scholo_specimen_jars", 4, "wall", 1)],
        "Vault of the Ravenian": [("scourge_bone_chest", 3, "free", 1), ("dg_wall_torch", 3, "wall", 2)],
        "Barov Family Vault": [("sm_sarcophagus", 3, "free", 2), ("hg_reliquary", 4, "wall", 1)],
        "The Headmaster's Study": [("scholo_desk", 3, "free", 1), ("sm_bookshelf", 4, "wall", 3),
                                   ("hg_throne", 4, "wall", 1)],
    },
}


def _room_box(r):
    x0, y0, x1, y1, _c = r
    return x0, y0, x1 - x0 + 1, y1 - y0 + 1


def build_floor(name):
    spec = FLOOR[name]
    W, H = spec["size"]
    zone = Tilemap(name, W, H, {
        UPPER: "The working floor of the Cult's school under Caer Darrow: the reliquary, the libraries, the bone pit "
               "and the laboratory where the dead are taught to stand.",
        LOWER: "Scholomance's lower halls, where the masters keep their rooms around the great hall and the "
               "Headmaster keeps his study.",
    }[name])
    zone.is_cave = True
    zone.region = REGION
    b = Builder(zone, wall_id="wall", floor_id="stone")
    for r in spec["rooms"].values():
        b.rect(r[0], r[1], r[2], r[3], chamfer=r[4])
    for (x0, y0, x1, y1) in spec["cells"]:
        b.rect(x0, y0, x1, y1, chamfer=1)
    for pts, wdt in spec["corridors"] + spec["cell_links"]:
        b.corridor(pts, width=wdt)
    for (x, y) in spec["pillars"]:
        b.pillars([x], [y], size=2, sprite=COLUMN, height=4)
    for (path, x, y, h, solid) in spec["dressing"]:
        if not zone.is_walkable(x, y):
            raise AssertionError((name, "prop base not on the floor", path, x, y))
        b.prop(path + ".png", x, y, h, solid=solid, fraction=0.4)

    doors = [spec["door"]] + ([STAIR_DOWN] if name == UPPER else [FAST_EXIT])
    for (dx, dy) in doors:
        for yy in (dy - 1, dy, dy + 1):
            if 0 <= yy < H:
                zone.collision_layer[yy][dx] = None
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
    start = (spec["door"][0], spec["door"][1] - 2) if name == UPPER else (STAIR_UP[0], STAIR_UP[1] + 2)
    targets = list(fixed) + [(x, y, "chest") for (x, y) in chests]
    if name == UPPER:
        targets.append((STAIR_DOWN[0], STAIR_DOWN[1], "stair"))
    else:
        targets.append((FAST_EXIT[0], FAST_EXIT[1], "the fast exit past Gandling"))
    # Kyle's Scholomance props (sheet 8), set into the rooms beside the older dressing above
    from tools.plaguelands_dungeon_kit import auto_dress
    kit_spec = {"rooms": {rn: ("rect",) + tuple(r) for rn, r in spec["rooms"].items()}, "decor": DECOR.get(name, {})}
    avoid = [(t[0], t[1]) for t in targets] + [start] + [(x, y) for p in spec["trash"] for (x, y, _m, _l) in p]
    zone.dressed = auto_dress(zone, b, kit_spec, avoid, sum(map(ord, name)))
    b.verify(start, targets)
    zone.add_subzone(name, 0, 0, W, H)
    for rname, r in spec["rooms"].items():
        zone.add_subzone(rname, *_room_box(r))
    return zone, b


def build_upper_baked():
    return build_floor(UPPER)


def build_lower_baked():
    return build_floor(LOWER)


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


def generate_floor(name):
    zone, _b = build_floor(name)
    from world.dungeon_packs import attach_packs
    avoid = [FLOOR[name]["door"]] + [tuple(b[:2]) for b in zone.boss_positions]
    if name == UPPER:
        avoid.append(STAIR_DOWN)
    attach_packs(zone, [_snap(zone, p) for p in FLOOR[name]["trash"]], avoid=avoid)
    from tools.handbuilt_vot_caves import register_baked
    register_baked(zone, BAKED[name])
    for (x, y) in zone.chest_spots:
        if zone.get_tile(x, y, "interaction") is None:
            zone.set_tile(x, y, "chest", "interaction")
    return zone


if __name__ == "__main__":
    for n in FLOOR:
        z, b = build_floor(n)
        d = FLOOR[n]["door"]
        print(n, z.width, "x", z.height, "| bosses", len(z.boss_positions), "| reachable",
              len(b.reachable((d[0], d[1] - 2) if n == UPPER else (d[0], d[1] + 2))))
