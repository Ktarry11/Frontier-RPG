"""
Hand-built The Royal Hive (140x160): the silithid hive under the Black Strand. FIVE BOSSES, 54-56.

Kyle, 13 Nov 2026: "Lets make a lvl 54-56 dungeon with the final boss dropping shoulders under the
abyssal sands. Silithid dungeon", "'The royal hive'". And on 14 Nov, before the shops: "Let's
quickly flesh out the Royal Hive as it'll drop another token."

WHERE IT IS. Hive Queen Zil'kesh in the Black Strand's Royal Cell was a daughter. The floor at the
back of her cell goes down, and the hive she was raised in is underneath: the chambers that dug
toward Onyxhollow's wall were its outer galleries, not the whole of it. You go in through the
narrow end of the Royal Cell and descend south.

THE SHAPE IS A HIVE, NOT A CAVE: round chambers of different sizes, joined by narrow bored
tunnels, descending. Every chamber is a lobe set, every tunnel a corridor whose ends sit on lobe
centres (the rule the Emberdeep learned: an end on a rim strands whoever stands there).

    door -> The Breach -> 1 Drone Galleries -> 3 Resin Halls -> 4 Deep Burrows -> 5 Royal Chamber
                                       \\-> 2 Brood Chambers (optional, west)

EVERY BOSS ASKS ONE THING (kits in tools/build_isle_dungeon_kits.py):
    1 Hive-Warden Kasz'ar      a carapace that shields itself the first time it drops low
    2 The Brood Nurse          larvae on a cap, and she mends them: kill the nursery first
    3 Resin-Mother Vex'ith     seals a player in resin and coats the party in acid: cleanse
    4 Tunnel-King Ruzzak       burrows, and while under, damage feeds its shell: stop hitting
    5 Hive-Mother Ahn'thera    the queen AND her Consort, Zhir'ak, in one fight (Kyle, 14 Nov: "another
      and Royal Consort Zhir'ak  2 for 1 boss fight. Drops 3 pieces of loot"). She calls guards and holds
                               at the brink once; he stands in front of her, armoured, and hits back.

HARD CONTRACTS (world/portal_manager.py)
  (70, 6) <-> The Black Strand (138, 115)   the floor of the Royal Cell
"""
from world.tilemap import Tilemap
from tools.dungeon_builder import Builder

NAME = "The Royal Hive"
BAKED = "assets/tiles/royal_hive/baked"
W, H = 140, 160
PORTAL = (70, 6)

#: name -> lobes (cx, cy, rx, ry). Hive chambers are round; the big ones get satellite lobes so
#: the walls bulge like cells rather than reading as ellipses.
CHAMBERS = {
    "The Breach":          [(70, 20, 9, 7)],
    "The Drone Galleries": [(70, 46, 20, 12), (52, 40, 8, 7), (88, 52, 8, 7)],
    "The Brood Chambers":  [(28, 76, 15, 12), (18, 66, 7, 6), (38, 88, 7, 6)],         # optional
    "The Resin Halls":     [(98, 82, 19, 13), (116, 74, 7, 7), (84, 92, 7, 6)],
    "The Deep Burrows":    [(52, 112, 20, 12), (34, 106, 7, 6), (70, 120, 7, 6)],
    "The Royal Chamber":   [(72, 142, 26, 13), (48, 138, 8, 7), (96, 138, 8, 7)],
}
#: (points, width) in chain order. Narrow, because they were bored by the things that live here.
TUNNELS = [
    ([(70, 6), (70, 14), (70, 20)], 4),
    ([(70, 20), (70, 34), (70, 46)], 3),
    ([(52, 40), (36, 56), (28, 76)], 3),                    # the brood spur, west
    ([(88, 52), (96, 66), (98, 82)], 3),
    ([(84, 92), (68, 102), (52, 112)], 3),
    ([(70, 120), (72, 132), (72, 142)], 4),
]
#: Side cells, each with a chest. Reached by a short bore off a chamber.
CELLS = [(16, 40, 5, 4), (124, 50, 5, 4), (120, 108, 5, 4), (20, 132, 5, 4)]
CELL_LINKS = [
    ([(52, 40), (32, 40), (16, 40)], 2),
    ([(88, 52), (108, 50), (124, 50)], 2),
    ([(116, 74), (122, 92), (120, 108)], 2),
    ([(34, 106), (24, 120), (20, 132)], 2),
]
#: Resin columns left standing in the big chambers.
COLUMNS = [(62, 44, 2, 2), (80, 48, 2, 2), (94, 78, 2, 2), (104, 88, 2, 2), (46, 110, 2, 2),
           (60, 116, 2, 2), (62, 140, 2, 2), (84, 144, 2, 2)]

#: (x, y, name, required)
BOSS_LIST = [
    (70, 48, "Hive-Warden Kasz'ar", True),
    (26, 78, "The Brood Nurse", False),
    (100, 84, "Resin-Mother Vex'ith", True),
    (50, 114, "Tunnel-King Ruzzak", True),
    (72, 146, "Hive-Mother Ahn'thera", True),
]
#: One encounter, two bosses (world/cave_spawns folds the members into the lead's SpawnPoint).
FINAL_PACK = {"Hive-Mother Ahn'thera": [(76, 144, "Royal Consort Zhir'ak")]}
BOSSES = {}
CHESTS = []
TRASH = []


def build_royal_hive():
    zone = Tilemap(NAME, W, H,
                   "The hive the Black Strand's queen was raised in: resin chambers bored "
                   "through the rock under the Abyssal Sands, going down.")
    zone.is_cave = True
    #: The PARENT OPEN ZONE, which is also the encounter-table key.
    zone.region = "The Black Strand"
    b = Builder(zone, wall_id="wall", floor_id="dirt")

    for lobes in CHAMBERS.values():
        b.lobes(lobes)
    for (cx, cy, rx, ry) in CELLS:
        b.lobes([(cx, cy, rx, ry)])
    for pts, wdt in TUNNELS + CELL_LINKS:
        b.corridor(pts, width=wdt)
    for (cx, cy, rx, ry) in COLUMNS:
        b.pillar(cx, cy, size=rx)
    dress(zone, b)

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.collision_layer[py + 1][px] = None

    fixed = []
    for (x, y, n, _req) in BOSS_LIST:
        if not zone.is_walkable(x, y):
            raise AssertionError(("boss standing in rock", n, x, y))
        fixed.append((x, y, n))
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (72, 146)
    zone.boss_positions = list(fixed)
    zone.boss_pack = FINAL_PACK

    CHESTS[:] = [(cx, cy) for (cx, cy, _rx, _ry) in CELLS if zone.is_walkable(cx, cy)]
    # every boss and every chest reachable from the door, or the build fails here
    b.verify((px, py + 2), [(x, y, n) for (x, y, n) in fixed] + [(x, y, "chest") for (x, y) in CHESTS])

    zone.add_subzone(NAME, 0, 0, W, H)
    for name, lobes in CHAMBERS.items():
        x0 = min(cx - rx for (cx, cy, rx, ry) in lobes)
        x1 = max(cx + rx for (cx, cy, rx, ry) in lobes)
        y0 = min(cy - ry for (cx, cy, rx, ry) in lobes)
        y1 = max(cy + ry for (cx, cy, rx, ry) in lobes)
        zone.add_subzone(name, int(x0 - 2), int(y0 - 2), int(x1 - x0 + 4), int(y1 - y0 + 4))
    return zone, b


_BS = "assets/tiles/broodspiral/props/"
_SF = "assets/tiles/shimmering_flats/props/"
_DP = "assets/tiles/dungeon_props/"
#: (sprite, x, base_y, height, solid). Less is more: a throne for the queen, resin on the
#: columns, eggs where the brood is kept, husks where the borers moult, and nothing in a tunnel.
DRESSING = [
    (_BS + "queens_throne.png", 72, 153, 6, "core"),        # behind her, at the back wall
    (_BS + "egg_sac_cluster.png", 20, 74, 3, False), (_BS + "egg_sac_cluster.png", 36, 84, 3, False),
    (_BS + "egg_sac_cluster.png", 30, 68, 3, False),
    (_SF + "sf_egg_cluster.png", 52, 141, 2, False), (_SF + "sf_egg_cluster.png", 92, 141, 2, False),
    (_SF + "sf_carapace_heap.png", 56, 45, 3, False), (_SF + "sf_carapace_heap.png", 86, 51, 3, False),
    (_DP + "den_chitin_husk.png", 40, 111, 3, False), (_DP + "den_chitin_husk.png", 64, 113, 3, False),
    (_SF + "sf_chitin_spire.png", 112, 73, 5, "core"), (_SF + "sf_chitin_spire.png", 88, 91, 5, "core"),
] + [(_BS + "resin_pillar.png", cx + 1, cy + 1, 4, False) for (cx, cy, _rx, _ry) in COLUMNS]


def dress(zone, b):
    for (path, x, y, h, solid) in DRESSING:
        if not zone.is_walkable(x, y) and not path.endswith("resin_pillar.png"):
            raise AssertionError(("prop base not on the floor", path, x, y))
        b.prop(path, x, y, h, solid=solid, fraction=0.4)


def _trash():
    """Hand-placed packs of two to three, door to queen. Larvae only near the nursery."""
    T = []

    def pack(lvl, *spots):
        for (x, y, m) in spots:
            T.append((x, y, m, lvl))

    pack(54, (70, 14, "Royal Hive Drone"), (67, 22, "Royal Hive Drone"), (74, 22, "Hive Tunneler"))
    pack(54, (70, 32, "Royal Hive Drone"), (66, 38, "Resin Weaver"))
    pack(54, (54, 40, "Royal Hive Guard"), (58, 50, "Royal Hive Drone"), (50, 46, "Resin Weaver"))
    pack(55, (86, 52, "Royal Hive Guard"), (84, 44, "Venomwing Wasp"), (90, 46, "Venomwing Wasp"))
    pack(54, (38, 58, "Brood Larva"), (34, 64, "Brood Larva"), (40, 66, "Royal Hive Drone"))
    pack(54, (20, 70, "Brood Larva"), (34, 86, "Resin Weaver"), (22, 86, "Brood Larva"))
    pack(55, (94, 66, "Hive Tunneler"), (98, 72, "Royal Hive Guard"))
    pack(55, (112, 76, "Resin Weaver"), (116, 80, "Venomwing Wasp"), (108, 90, "Royal Hive Drone"))
    pack(55, (86, 92, "Royal Hive Guard"), (80, 96, "Resin Weaver"))
    pack(55, (68, 104, "Hive Tunneler"), (62, 108, "Hive Tunneler"), (56, 104, "Venomwing Wasp"))
    pack(56, (36, 106, "Royal Hive Guard"), (40, 118, "Hive Tunneler"), (64, 118, "Resin Weaver"))
    pack(56, (72, 126, "Royal Hive Guard"), (70, 132, "Royal Hive Guard"))
    pack(56, (50, 138, "Venomwing Wasp"), (54, 144, "Royal Hive Guard"), (94, 138, "Venomwing Wasp"),
         (90, 144, "Royal Hive Guard"))
    return T


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
            raise AssertionError(("trash with no walkable tile within reach", m, x, y))
        out.append((best[1], best[2], m, lvl))
    return out


def build_royal_hive_baked():
    """The map for the baker to paint from."""
    return build_royal_hive()


def generate_royal_hive():
    zone, _b = build_royal_hive()
    TRASH[:] = _snap(zone, _trash())
    zone.trash_spawns = list(TRASH)
    from tools.handbuilt_vot_caves import register_baked
    register_baked(zone, BAKED)
    return zone


if __name__ == "__main__":
    z, b = build_royal_hive()
    seen = b.reachable(PORTAL) if hasattr(b, "reachable") else None
    print(z.name, z.width, "x", z.height, "| bosses", len(z.boss_positions),
          "| reachable", None if seen is None else len(seen))
