"""
Hand-built THE DROWNED PALACE, levels 59-60: Azshara's second dungeon, Queen Azshara's palace in Zin-Azshari, its door
at the head of the Drowned Court off East Azshara's shore (docs/azshara_brief.md). Two floors, two maps, one dungeon.

Kyle, 18 Nov 2026, picking it: the name "The Drowned Palace"; "Naga up, ghosts down" (the naga hold the flooded halls,
the Highborne dead keep the vault under them); and the set piece "Sunken palace, dry vault": the first floor is the
palace half fallen into the sea, its halls cut by deep channels you cross on fallen columns, and the second is a dry
air pocket under the sea, gold and violet and untouched, held up by the queen's wards, with Azshara's empty throne at
the end. On the second floor the walls ARE the sea: beyond the wards there's nothing but deep water.

THE FLOODED HALLS (180x150), 59-60: the naga's. In at the bottom from the Drowned Court, out by the flooded stair.
    the Sunken Gate -> the Siren's Court (Lady Ssiriss on her coral dais in the pool, one fallen column out to her)
    -> the Collapsed Gallery (a long hall gone into the sea: three ledges and two fallen columns, back and forth across
    the channel) -> the Drowned Archive (the Drowned Chamberlain among the swollen shelves) -> the Throne of Tides
    (Tidelord Vashj'ren on the coral throne, a moat round it) -> the flooded stair down
        1 Lady Ssiriss             a four-armed siren queen: charms and drowns
        2 The Drowned Chamberlain  the palace steward, still keeping the ledger: locks you in, collects
        3 Tidelord Vashj'ren       the naga warlord: the tide comes in with him

THE QUEEN'S VAULT (170x140), 59-60: the Highborne dead's.
    the Air Pocket -> the Moonguard Processional (the Moonguard Revenant at its end) -> the Arcanum (Magistrix Elaria
    the Undying at the cracked well) -> the Hall of Mirrors and the treasuries -> the Queen's Throne Room (the Echo of
    the Queen before Azshara's empty throne) -> the fast exit up to the Drowned Court
        4 The Moonguard Revenant   the queen's knight, drowned in its armour: shield wall, then the charge
        5 Magistrix Elaria         the sorceress at the well: blue fire, and she drinks the well to heal
        6 Echo of the Queen        moonlight and water in the queen's shape: calls her court, then the sea

HARD CONTRACTS (world/portal_manager.py)
  (90,148) <-> East Azshara (178,92), the Vault door in the Drowned Court
  STAIR_DOWN (162,12) on the Flooded Halls <-> STAIR_UP (20,2) on the Queen's Vault
  FAST_EXIT (164,117) on the Queen's Vault -> East Azshara, past the Echo of the Queen
"""
from collections import deque

from world.tilemap import Tilemap
from tools.dungeon_builder import Builder

NAME = "The Drowned Palace"
HALLS, VAULT = NAME, "The Drowned Palace: The Queen's Vault"
FLOORS = (HALLS, VAULT)
BAKED = {HALLS: "assets/tiles/azshara/baked_drowned_halls", VAULT: "assets/tiles/azshara/baked_queens_vault"}
REGION = "East Azshara"

DOOR = (90, 148)
STAIR_DOWN = (162, 12)
STAIR_UP = (20, 2)
FAST_EXIT = (164, 117)
VZ = "assets/tiles/dungeon_props/vz_"

FLOOR = {
    HALLS: dict(
        size=(180, 150), start=(90, 144),
        rooms={
            "The Sunken Gate":      ("rect", 70, 122, 110, 144, 3),
            "The Siren's Court":    ("lobes", [(90, 96, 26, 15)]),
            "The Collapsed Gallery": ("rect", 14, 40, 46, 110, 2),
            "The Drowned Archive":  ("rect", 10, 8, 60, 30, 2),
            "The Throne of Tides":  ("lobes", [(118, 30, 34, 19)]),
        },
        # the sea, over the floor (impassable)
        deep=[(76, 132, 3, 6), (104, 132, 3, 6),              # the gate's two drowned basins
              (90, 96, 20, 10),                               # the court's pool
              ("rect", 13, 41, 47, 109),                      # the gallery: all of it gone into the sea...
              (118, 30, 35, 20)],                             # the Tidelord's sea, wall to wall
        # ...and the floor laid back over it: ledges, islands, fallen columns
        land=[("rect", 38, 74, 46, 110), ("rect", 14, 50, 22, 86), ("rect", 38, 40, 46, 64),   # the gallery's ledges
              ("rect", 14, 40, 46, 46),                       # its north landing
              (90, 92, 6, 4),                                 # Ssiriss's coral dais
              (118, 27, 10, 7),                               # the Tidelord's island
              (90, 25, 6, 5), (148, 22, 5, 4)],               # the landings either side of it
        # widths are _carve_path's: about 2w + 1 tiles across, so a fallen column (w 1) is three tiles wide
        passages=[([(90, 149), (90, 140)], 2),                # the door, up the sunken steps
                  ([(90, 124), (90, 108)], 2),                # gate -> court
                  ([(90, 109), (90, 94)], 1),                 # the fallen column out to the dais
                  ([(68, 100), (42, 100)], 2),                # court -> gallery (onto the east ledge)
                  ([(42, 80), (18, 80)], 1),                  # fallen column, east ledge -> west
                  ([(18, 56), (42, 56)], 1),                  # fallen column, west ledge -> east
                  ([(26, 44), (26, 26)], 2),                  # gallery -> archive
                  ([(58, 18), (86, 24)], 2),                  # archive -> throne of tides
                  ([(84, 30), (112, 27)], 1),                 # the column bridge out to the throne island
                  ([(124, 27), (150, 22), (158, 15), (162, 12)], 1)],   # island -> the flooded stair
        cells=[(62, 8, 72, 16), (2, 62, 10, 72), (156, 28, 166, 36)],
        cell_links=[([(58, 12), (64, 12)], 1), ([(8, 67), (16, 67)], 1), ([(151, 24), (158, 31)], 1)],
        bosses=[(90, 91, "Lady Ssiriss"), (35, 14, "The Drowned Chamberlain"), (118, 25, "Tidelord Vashj'ren")],
        final="Tidelord Vashj'ren",
        doors=[DOOR, STAIR_DOWN],
        dressing=[("flooded_stair", 90, 141, 6, False), ("drowned_colonnade", 78, 126, 5, False),
                  ("drowned_colonnade", 102, 126, 5, False), ("coral_throne", 90, 89, 5, False),
                  ("fallen_chandelier", 72, 108, 4, False), ("naga_shrine", 108, 86, 5, False),
                  ("drowned_shelf", 14, 11, 5, False), ("drowned_shelf", 22, 11, 5, False),
                  ("drowned_shelf", 48, 11, 5, False), ("drowned_shelf", 56, 11, 5, False),
                  ("drowned_shelf", 14, 29, 5, False), ("drowned_shelf", 56, 29, 5, False),
                  ("naga_shrine", 90, 22, 5, False), ("naga_shrine", 148, 20, 4, False),
                  ("flooded_stair", 162, 15, 5, False)],
    ),
    VAULT: dict(
        size=(170, 140), start=(20, 6),
        rooms={
            "The Air Pocket":             ("rect", 6, 4, 34, 26, 2),
            "The Moonguard Processional": ("rect", 40, 9, 132, 25, 2),
            "The Arcanum":                ("lobes", [(120, 64, 26, 18)]),
            "The Hall of Mirrors":        ("rect", 30, 52, 84, 74, 2),
            "The Queen's Throne Room":    ("rect", 20, 100, 154, 134, 4),
        },
        deep=[(122, 66, 8, 6)],                               # the ancient well's arcane water
        land=[],
        passages=[([(20, 2), (20, 8)], 2),                    # down from the flooded stair
                  ([(32, 16), (42, 16)], 2),
                  ([(126, 22), (126, 52)], 2),                # processional -> arcanum
                  ([(97, 64), (82, 64)], 2),                  # arcanum -> hall of mirrors
                  ([(56, 72), (56, 102)], 3),                 # mirrors -> throne room
                  ([(152, 117), (165, 117)], 2)],             # past the throne: the fast exit
        cells=[(30, 80, 44, 92), (66, 80, 80, 92), (140, 44, 150, 54)],
        cell_links=[([(37, 72), (37, 82)], 1), ([(73, 72), (73, 82)], 1), ([(142, 52), (134, 60)], 1)],
        pillars=[(56, 12), (56, 21), (74, 12), (74, 21), (92, 12), (92, 21), (110, 12), (110, 21),
                 (44, 104), (44, 129), (70, 104), (70, 129), (96, 104), (96, 129), (122, 104), (122, 129)],
        bosses=[(126, 17, "The Moonguard Revenant"), (122, 55, "Magistrix Elaria the Undying"),
                (146, 117, "Echo of the Queen")],
        final="Echo of the Queen",
        doors=[STAIR_UP, FAST_EXIT],
        dressing=[("vault_door", 20, 10, 5, False), ("ancient_well", 122, 74, 7, False),
                  ("artifact_pedestal", 104, 56, 4, False), ("artifact_pedestal", 140, 72, 4, False),
                  ("water_mirror", 38, 55, 5, False), ("water_mirror", 50, 55, 5, False),
                  ("water_mirror", 64, 55, 5, False), ("water_mirror", 76, 55, 5, False),
                  ("treasure_pile", 37, 90, 4, False), ("treasure_pile", 73, 90, 4, False),
                  ("treasure_pile", 145, 52, 3, False),
                  ("queens_throne", 150, 116, 8, False), ("artifact_pedestal", 134, 106, 4, False),
                  ("artifact_pedestal", 134, 128, 4, False)],
    ),
}

BOSSES = {}


def _shape(b, spec, base=None):
    if spec[0] == "rect":
        _k, x0, y0, x1, y1 = spec[:5]
        b.rect(x0, y0, x1, y1, chamfer=(spec[5] if len(spec) > 5 else 0), base=base)
    elif spec[0] == "lobes":
        b.lobes(spec[1], base=base)
    else:
        b.lobes([spec], base=base)


def _reach(zone, start):
    seen, q = {start}, deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and 0 <= n[0] < zone.width and 0 <= n[1] < zone.height and zone.is_walkable(*n):
                seen.add(n)
                q.append(n)
    return seen


def _seal(zone, start):
    seen = _reach(zone, start)
    for y in range(zone.height):
        for x in range(zone.width):
            if (x, y) not in seen and zone.is_walkable(x, y):
                zone.collision_layer[y][x] = "rock"


def _dress(b, spec):
    z = b.zone
    for (name, x, y, h, solid) in spec["dressing"]:
        spot = min(((dx * dx + dy * dy, x + dx, y + dy) for dy in range(-3, 4) for dx in range(-3, 4)
                    if z.is_walkable(x + dx, y + dy)), default=None)
        if spot is None:
            raise AssertionError((z.name, "prop with no floor within reach", name, x, y))
        b.prop(f"{VZ}{name}.png", spot[1], spot[2], h, solid=solid, fraction=0.3)


def build_floor(name):
    spec = FLOOR[name]
    W, H = spec["size"]
    zone = Tilemap(name, W, H, {
        HALLS: "Queen Azshara's palace in Zin-Azshari, half fallen into the sea. The naga hold its flooded halls.",
        VAULT: "A dry vault under the sea, held up by the queen's wards, gold and violet and untouched. The "
               "Highborne dead still keep it for her.",
    }[name])
    zone.is_cave = True
    zone.region = REGION
    b = Builder(zone, wall_id="rock", floor_id="stone")
    for r in spec["rooms"].values():
        _shape(b, r)
    for (x0, y0, x1, y1) in spec["cells"]:
        b.rect(x0, y0, x1, y1, chamfer=1)
    for d in spec["deep"]:
        _shape(b, d, base="lava")
    for d in spec["land"]:
        _shape(b, d)
    for pts, wdt in spec["passages"] + spec["cell_links"]:
        b.corridor(pts, width=wdt)
    for (x, y) in spec.get("pillars", []):
        for yy in range(y, y + 2):
            for xx in range(x, x + 2):
                zone.collision_layer[yy][xx] = "rock"
    for (dx, dy) in spec["doors"]:
        for yy in (dy - 1, dy, dy + 1):
            if 0 <= yy < H:
                zone.collision_layer[yy][dx] = None
    _seal(zone, spec["start"])
    _dress(b, spec)
    _seal(zone, spec["start"])

    fixed = []
    for (x, y, n) in spec["bosses"]:
        if not zone.is_walkable(x, y):
            raise AssertionError((name, "boss standing in rock or sea", n, x, y))
        fixed.append((x, y, n))
    BOSSES[name] = {n: (x, y) for (x, y, n) in fixed}
    final = next(f for f in fixed if f[2] == spec["final"])
    zone.boss_position = final[:2]
    zone.boss_positions = list(fixed)
    zone.chest_spots = [((x0 + x1) // 2, (y0 + y1) // 2) for (x0, y0, x1, y1) in spec["cells"]]
    seen = _reach(zone, spec["start"])
    missing = [t for t in fixed + [(x, y, "chest") for (x, y) in zone.chest_spots]
               + [(d[0], d[1], "door") for d in spec["doors"]] if (t[0], t[1]) not in seen]
    if missing:
        raise AssertionError((name, "unreachable", missing))
    zone.add_subzone(name, 0, 0, W, H)
    for rname, r in spec["rooms"].items():
        if r[0] == "rect":
            zone.add_subzone(rname, r[1], r[2], r[3] - r[1] + 1, r[4] - r[2] + 1)
        else:
            lb = r[1]
            x0 = min(cx - rx for (cx, cy, rx, ry) in lb)
            y0 = min(cy - ry for (cx, cy, rx, ry) in lb)
            x1 = max(cx + rx for (cx, cy, rx, ry) in lb)
            y1 = max(cy + ry for (cx, cy, rx, ry) in lb)
            zone.add_subzone(rname, x0, y0, x1 - x0 + 1, y1 - y0 + 1)
    return zone, b


def build_halls_baked():
    return build_floor(HALLS)[0], None


def build_vault_baked():
    return build_floor(VAULT)[0], None


def _trash(name):
    T = []

    def pack(lvl, *spots):
        T.append([(x, y, m, lvl) for (x, y, m) in spots])

    if name == HALLS:
        # the Sunken Gate
        pack(59, (82, 136, "Zin-Azshari Myrmidon"), (98, 136, "Zin-Azshari Myrmidon"), (90, 130, "Zin-Azshari Siren"))
        pack(59, (80, 124, "Zin-Azshari Royal Guard"), (100, 124, "Zin-Azshari Tidecaller"))
        # the Siren's Court, round the rim
        pack(59, (70, 100, "Zin-Azshari Siren"), (72, 92, "Zin-Azshari Siren"), (68, 96, "Zin-Azshari Royal Guard"))
        pack(59, (110, 100, "Zin-Azshari Myrmidon"), (110, 92, "Drowned Highborne"), (112, 96, "Zin-Azshari Tidecaller"))
        pack(60, (90, 84, "Zin-Azshari Royal Guard"), (82, 84, "Zin-Azshari Siren"))
        # the Collapsed Gallery, on its ledges
        pack(59, (42, 100, "Hydra Spawn"), (42, 92, "Hydra Spawn"), (42, 86, "Zin-Azshari Tidecaller"))
        pack(60, (18, 74, "Zin-Azshari Myrmidon"), (18, 66, "Drowned Highborne"), (18, 60, "Zin-Azshari Siren"))
        pack(60, (42, 50, "Zin-Azshari Royal Guard"), (42, 44, "Hydra Spawn"))
        # the Drowned Archive
        pack(60, (20, 22, "Drowned Highborne"), (24, 18, "Drowned Highborne"), (16, 18, "Zin-Azshari Tidecaller"))
        pack(60, (48, 22, "Drowned Highborne"), (52, 16, "Zin-Azshari Siren"), (44, 18, "Drowned Highborne"))
        # the Throne of Tides
        pack(60, (88, 22, "Zin-Azshari Royal Guard"), (92, 26, "Zin-Azshari Royal Guard"), (86, 18, "Zin-Azshari Tidecaller"))
        pack(60, (114, 32, "Zin-Azshari Myrmidon"), (122, 32, "Hydra Spawn"), (118, 33, "Zin-Azshari Siren"))
        pack(60, (148, 22, "Zin-Azshari Royal Guard"), (150, 20, "Zin-Azshari Myrmidon"))
    else:
        # the Air Pocket
        pack(59, (14, 18, "Vault Hound"), (24, 20, "Vault Hound"), (20, 16, "Tormented Courtier"))
        # the Moonguard Processional
        pack(59, (50, 16, "Moonguard Sentinel"), (52, 20, "Moonguard Sentinel"), (48, 12, "Highborne Spellbinder"))
        pack(60, (82, 16, "Moonguard Sentinel"), (84, 20, "Queen's Handmaiden"), (80, 12, "Tormented Courtier"))
        pack(60, (102, 16, "Arcane Sentry"), (104, 20, "Moonguard Sentinel"))
        # the Arcanum, round the well
        pack(60, (104, 66, "Mana Wyrm"), (106, 72, "Mana Wyrm"), (100, 64, "Highborne Spellbinder"))
        pack(60, (138, 66, "Ley Beast"), (136, 74, "Arcane Sentry"), (140, 60, "Highborne Spellbinder"))
        pack(60, (122, 78, "Arcane Sentry"), (116, 80, "Mana Wyrm"))
        # the Hall of Mirrors and its treasuries
        pack(60, (70, 62, "Queen's Handmaiden"), (74, 66, "Tormented Courtier"), (66, 66, "Highborne Spellbinder"))
        pack(60, (40, 64, "Moonguard Sentinel"), (44, 68, "Vault Hound"), (36, 60, "Queen's Handmaiden"))
        # the Queen's Throne Room
        pack(60, (40, 112, "Moonguard Sentinel"), (40, 122, "Moonguard Sentinel"), (34, 117, "Highborne Spellbinder"))
        pack(60, (82, 110, "Queen's Handmaiden"), (82, 124, "Tormented Courtier"), (88, 117, "Arcane Sentry"))
        pack(60, (112, 112, "Moonguard Sentinel"), (112, 122, "Ley Beast"), (118, 117, "Queen's Handmaiden"))
    return T


def _snap(zone, spots, rad=8):
    out = []
    for (x, y, m, lvl) in spots:
        if zone.is_walkable(x, y):
            out.append((x, y, m, lvl))
            continue
        best = min(((dx * dx + dy * dy, x + dx, y + dy) for dy in range(-rad, rad + 1) for dx in range(-rad, rad + 1)
                    if 0 <= x + dx < zone.width and 0 <= y + dy < zone.height and zone.is_walkable(x + dx, y + dy)),
                   default=None)
        if best is None:
            raise AssertionError(("trash with no floor within reach", zone.name, m, x, y))
        out.append((best[1], best[2], m, lvl))
    return out


def generate_floor(name):
    zone, _b = build_floor(name)
    from world.dungeon_packs import attach_packs
    avoid = list(FLOOR[name]["doors"]) + [tuple(b[:2]) for b in zone.boss_positions]
    attach_packs(zone, [_snap(zone, p) for p in _trash(name)], avoid=avoid)
    from tools.handbuilt_vot_caves import register_baked
    register_baked(zone, BAKED[name])
    for (x, y) in zone.chest_spots:
        if zone.get_tile(x, y, "interaction") is None:
            zone.set_tile(x, y, "chest", "interaction")
    return zone


if __name__ == "__main__":
    for n in FLOORS:
        z, _b = build_floor(n)
        walk = sum(z.is_walkable(x, y) for y in range(z.height) for x in range(z.width))
        print(n, z.width, "x", z.height, "| walkable", walk, "| bosses", len(z.boss_positions))
