"""
Hand-built THE ROTROOT DEEPS (200x180), levels 55-58: the dungeon under Timbermaw Hold (docs/azshara_brief.md).

Kyle, 17 Nov 2026: "timbermaw hold is going to look like an actual capital city and it will have the dungeon under
it. This is similar to how org is." The brief: whatever turned the Deadwood came up from below the Hold itself, so
it's a satyr-and-demon dungeon under the furbolgs' feet, and every boss pays Timbermaw. Kyle named it and kept the
art sheet's five bosses on 18 Nov 2026 ("The Rotroot Deeps", "Keep all five"), then: "feel free to make the dungeons
more exciting than....that". So the first draft (five rooms on a line of passages) was thrown out for this.

THE SHAPE: A DESCENT INTO A ROTTING LAKE. You come down through the Hold's sealed deep gate into the furbolgs' own
burial halls, and every level after that the fel ooze has eaten more of the floor, until the last hall is an island
in it. The ooze is real collision (lava under the hood, painted as fel water), so the floor is roots and islands.

    1 THE BURIAL HALLS     built by the Timbermaw: a pillared nave with burial niches down both sides and Old Mossjaw,
                           the chieftain the rot took first, on his bier at the far end
    2 THE SPOREGARDEN      the first of the ooze: a cavern whose floor has gone to fel pools, fungus islands joined by
                           spore-crusted spits, Mother Sporeheart on the biggest island
    3 THE WARDEN'S GAUNTLET the satyrs' long cage hall: cage alcoves down both sides, a run past every one of them to
                           Rotwarden Kaz'thul at the end
    4 THE ROOT CATHEDRAL   a vast cavern over a fel lake, the Hold's own roots come down through the roof as bridges
                           between three root knots; Thornblight on the middle knot, the lake on every side
    5 THE GLOOMHOLLOW      the bottom: a fel lake in a ring of ledge, ritual platforms round it, and one long root
                           causeway out to Xavras the Gloomtender's throne island in the middle
    THE ROTTING STAIR      a ledge down the west wall beside a fel fall, from the Sporegarden to the Gloomhollow's ring:
                           the way back up after Xavras, and a way past the middle for a party that wants it (Kyle:
                           "if people want to skip bosses they can")

Trash comes in packs: four or five from level 30 up (world/dungeon_packs).

HARD CONTRACTS (world/portal_manager.py)
  (22, 3) <-> Timbermaw Hold's deep gate (130, 92)
"""
from world.tilemap import Tilemap
from tools.dungeon_builder import Builder

NAME = "The Rotroot Deeps"
BAKED = "assets/tiles/azshara/baked_rotroot_deeps"
W, H = 200, 180
PORTAL = (22, 3)

#: name -> ("rect", x0, y0, x1, y1, chamfer) or ("lobes", [(cx, cy, rx, ry)]): the floor, cut first
ROOMS = {
    "The Burial Halls":      ("rect", 14, 10, 52, 50, 4),
    "The Sporegarden":       ("lobes", [(86, 66, 22, 16), (104, 56, 10, 8), (70, 76, 9, 7)]),
    "The Warden's Gauntlet": ("rect", 120, 70, 176, 84, 2),
    "The Root Cathedral":    ("lobes", [(150, 124, 30, 22)]),
    "The Gloomhollow":       ("lobes", [(78, 150, 30, 20), (46, 144, 9, 8)]),
}
#: the fel ooze, laid back over the floor (impassable): (cx, cy, rx, ry)
OOZE = [
    (84, 68, 17, 11), (100, 60, 6, 5),                      # the Sporegarden's pools
    (150, 124, 31, 23),                                     # the Root Cathedral's lake, wall to wall: roots or nothing
    (78, 152, 24, 15),                                      # the Gloomhollow's lake
    (62, 104, 2, 20),                                       # the fel fall beside the Rotting Stair
]
#: islands and knots standing in the ooze: (cx, cy, rx, ry)
ISLANDS = [
    (86, 68, 7, 5),                                         # Sporeheart's island
    (74, 62, 4, 3), (98, 72, 4, 3),                         # fungus islands
    (150, 126, 8, 6), (132, 118, 5, 4), (168, 132, 5, 4),   # the cathedral's three root knots
    (172, 104, 5, 4), (122, 140, 5, 4),                     # the cathedral's two landings, in and out
    (78, 152, 7, 5),                                        # Xavras's throne island
    (58, 142, 3, 3), (98, 142, 3, 3), (78, 164, 3, 3),      # ritual platforms on the Gloomhollow's rim
]
#: (points, width): passages, spits, root bridges and the causeway, every end on floor
PASSAGES = [
    ([(22, 4), (22, 12)], 5),                                   # the gate stair down into the halls
    ([(48, 46), (58, 54), (66, 60)], 5),                        # 1 -> 2, the first slope
    # the Sporegarden's spits: the way round the pools to its far side, and out to the islands
    ([(66, 62), (74, 62), (86, 68), (98, 72), (110, 66)], 3),
    ([(104, 56), (114, 62), (122, 70)], 5),                     # 2 -> 3, into the gauntlet
    ([(174, 84), (176, 94), (172, 102)], 5),                    # 3 -> 4, down into the cathedral
    # the root bridges: the cathedral's south rim to the knots, knot to knot
    ([(172, 104), (168, 118), (168, 132)], 3),
    ([(168, 132), (160, 129), (150, 126)], 3),
    ([(150, 126), (140, 122), (132, 118)], 3),
    ([(132, 118), (124, 128), (122, 140)], 3),
    ([(122, 140), (112, 144), (104, 146)], 5),                  # 4 -> 5, down to the Gloomhollow's rim
    ([(104, 146), (92, 150), (78, 152)], 3),                    # the causeway out to the throne
    # the Rotting Stair: from the Sporegarden down the west wall beside the fel fall, to the rim
    ([(66, 80), (66, 92), (66, 116), (60, 132), (50, 140)], 3),
]
#: rock left standing: the halls' pillars, and the gauntlet's cage walls
PILLARS = [(24, 20, 1), (24, 30, 1), (24, 40, 1), (42, 20, 1), (42, 30, 1), (42, 40, 1)]
#: the gauntlet's cage alcoves: (x0, y0, x1, y1), cut out of the rock either side of the hall
ALCOVES = ([(x, 64, x + 4, 69) for x in range(124, 172, 8)]
           + [(x, 85, x + 4, 90) for x in range(124, 172, 8)])
#: the halls' burial niches, cut into the side walls
NICHES = ([(9, y, 13, y + 4) for y in range(14, 46, 8)] + [(53, y, 57, y + 4) for y in range(14, 42, 8)])

BOSS_LIST = [
    (33, 46, "Old Mossjaw"),                 # on his bier at the far (south) end of the nave, before the slope down
    (86, 67, "Mother Sporeheart"),
    (172, 77, "Rotwarden Kaz'thul"),
    (150, 126, "Thornblight"),
    (78, 151, "Xavras the Gloomtender"),
]
BOSSES = {}
CHESTS = []
TRASH = []


def _seal_strays(zone):
    """Any floor the gate can't walk to (a corner the ooze cut off) goes back to rock."""
    from collections import deque
    start = (PORTAL[0], PORTAL[1] + 1)
    seen, q = {start}, deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and 0 <= n[0] < W and 0 <= n[1] < H and zone.is_walkable(*n):
                seen.add(n)
                q.append(n)
    for y in range(H):
        for x in range(W):
            if (x, y) not in seen and zone.is_walkable(x, y):
                zone.collision_layer[y][x] = "rock"


def build_rotroot():
    zone = Tilemap(NAME, W, H,
                   "Under Timbermaw Hold, where the rot that took the Deadwood came from. The furbolgs' burial halls "
                   "first, then a floor the fel ooze has eaten, until the last hall is an island in it.")
    zone.is_cave = True
    #: the parent open zone, which is also the encounter-table key
    zone.region = "Timbermaw Hold"
    b = Builder(zone, wall_id="rock", floor_id="stone")
    for name, spec in ROOMS.items():
        if spec[0] == "rect":
            _k, x0, y0, x1, y1, ch = spec
            b.rect(x0, y0, x1, y1, chamfer=ch)
        else:
            b.lobes(spec[1])
    for (x0, y0, x1, y1) in ALCOVES + NICHES:
        b.rect(x0, y0, x1, y1)
    # THE OOZE OVER THE FLOOR, then the islands and bridges back over the ooze (the Emberdeep's order)
    b.lobes(OOZE, base="lava")
    b.lobes(ISLANDS)
    for pts, wdt in PASSAGES:
        b.corridor(pts, width=wdt)
    for (px, py, r) in PILLARS:
        for y in range(py - r, py + r + 1):
            for x in range(px - r, px + r + 1):
                if (x - px) ** 2 + (y - py) ** 2 <= r * r + 1:
                    zone.collision_layer[y][x] = "rock"

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.collision_layer[py + 1][px] = None
    _seal_strays(zone)

    fixed = []
    for (x, y, n) in BOSS_LIST:
        if not zone.is_walkable(x, y):
            raise AssertionError(("boss standing in rock or ooze", n, x, y))
        fixed.append((x, y, n))
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = BOSS_LIST[-1][:2]
    zone.boss_positions = list(fixed)

    chests = [(11, 16), (55, 32), (74, 62), (126, 66), (166, 88), (132, 118), (98, 142), (46, 144)]
    CHESTS[:] = [c for c in chests if zone.is_walkable(*c)]

    zone.add_subzone(NAME, 0, 0, W, H)
    for name, spec in ROOMS.items():
        if spec[0] == "rect":
            _k, x0, y0, x1, y1, _c = spec
            zone.add_subzone(name, x0 - 5, y0 - 6, x1 - x0 + 11, y1 - y0 + 13)
        else:
            lobes = spec[1]
            x0 = min(cx - rx for (cx, cy, rx, ry) in lobes)
            x1 = max(cx + rx for (cx, cy, rx, ry) in lobes)
            y0 = min(cy - ry for (cx, cy, rx, ry) in lobes)
            y1 = max(cy + ry for (cx, cy, rx, ry) in lobes)
            zone.add_subzone(name, x0 - 2, y0 - 2, x1 - x0 + 4, y1 - y0 + 4)
    zone.add_subzone("The Rotting Stair", 56, 80, 16, 56)
    return zone, b


def _trash():
    """Hand-placed, from the gate down. Each pack(...) is one pull, filled to four or five beside itself."""
    T = []

    def pack(lvl, *spots):
        T.append([(x, y, m, lvl) for (x, y, m) in spots])

    # THE BURIAL HALLS: the Timbermaw dead the rot got up, down both aisles and out of the niches
    pack(55, (20, 22, "Rotroot Furbolg"), (26, 24, "Rotroot Furbolg"), (22, 28, "Rotroot Mystic"))
    pack(55, (46, 22, "Rotroot Furbolg"), (40, 24, "Rotroot Furbolg"), (44, 28, "Rotroot Mystic"))
    pack(55, (30, 34, "Rotroot Mauler"), (36, 34, "Rotroot Furbolg"), (33, 30, "Drifting Sporecloud"))
    pack(55, (11, 32, "Rotroot Furbolg"), (16, 36, "Rotroot Mystic"), (18, 40, "Rotroot Furbolg"))
    pack(55, (54, 36, "Rotroot Furbolg"), (50, 38, "Drifting Sporecloud"), (48, 34, "Rotroot Mauler"))
    # the first slope
    pack(56, (56, 52, "Rotroot Furbolg"), (60, 56, "Rotroot Mystic"), (54, 50, "Drifting Sporecloud"))
    # THE SPOREGARDEN: round the rim, and out on the fungus
    pack(56, (68, 70, "Drifting Sporecloud"), (70, 74, "Drifting Sporecloud"), (72, 78, "Rotroot Mauler"))
    pack(56, (90, 54, "Rotroot Mystic"), (96, 52, "Rotroot Furbolg"), (86, 54, "Drifting Sporecloud"))
    pack(56, (74, 62, "Drifting Sporecloud"), (76, 63, "Rotroot Furbolg"))
    pack(56, (98, 72, "Rotroot Mauler"), (100, 72, "Drifting Sporecloud"))
    pack(56, (108, 64, "Rotroot Mauler"), (110, 60, "Drifting Sporecloud"), (106, 52, "Rotroot Mystic"))
    # THE WARDEN'S GAUNTLET: the run past the cages
    pack(57, (130, 74, "Satyr Rot-Tender"), (134, 78, "Gloomhollow Satyr"), (130, 80, "Gloomhollow Satyr"))
    pack(57, (148, 74, "Gloomhollow Satyr"), (152, 78, "Rotroot Bodyguard"), (148, 80, "Satyr Rot-Tender"))
    pack(57, (162, 74, "Satyr Rot-Tender"), (160, 80, "Gloomhollow Satyr"), (138, 66, "Rootbound Horror"))
    pack(57, (154, 88, "Rootbound Horror"), (142, 88, "Rotroot Bodyguard"))
    pack(57, (176, 92, "Rotroot Bodyguard"), (174, 96, "Satyr Rot-Tender"))
    # THE ROOT CATHEDRAL: the landings and the knots, nothing but ooze between
    pack(58, (170, 106, "Rotroot Bodyguard"), (173, 104, "Satyr Rot-Tender"), (171, 102, "Gloomhollow Satyr"))
    pack(58, (168, 130, "Rootbound Horror"), (166, 134, "Gloomhollow Satyr"), (170, 132, "Drifting Sporecloud"))
    pack(58, (132, 118, "Rootbound Horror"), (130, 120, "Drifting Sporecloud"), (134, 116, "Satyr Rot-Tender"))
    pack(58, (122, 140, "Gloomhollow Satyr"), (120, 142, "Rotroot Bodyguard"), (124, 139, "Satyr Rot-Tender"))
    # THE GLOOMHOLLOW: round the ring, and at the causeway's foot
    pack(58, (102, 140, "Gloomhollow Satyr"), (98, 142, "Satyr Rot-Tender"), (100, 144, "Rotroot Bodyguard"))
    pack(58, (104, 152, "Rotroot Bodyguard"), (102, 156, "Gloomhollow Satyr"), (100, 158, "Satyr Rot-Tender"))
    pack(58, (46, 144, "Rootbound Horror"), (50, 148, "Rotroot Mystic"), (44, 140, "Gloomhollow Satyr"))
    pack(58, (70, 166, "Gloomhollow Satyr"), (80, 168, "Satyr Rot-Tender"), (86, 167, "Rotroot Bodyguard"))
    pack(58, (70, 134, "Gloomhollow Satyr"), (80, 132, "Rotroot Bodyguard"), (88, 133, "Satyr Rot-Tender"))
    # THE ROTTING STAIR
    pack(57, (66, 90, "Rotroot Mauler"), (66, 96, "Rotroot Furbolg"))
    pack(57, (64, 122, "Rootbound Horror"), (62, 126, "Rotroot Mystic"))
    return T


def _snap(zone, spots, rad=8):
    out = []
    for (x, y, m, lvl) in spots:
        if zone.is_walkable(x, y):
            out.append((x, y, m, lvl)); continue
        best = None
        for r in range(1, rad + 1):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < zone.width and 0 <= ny < zone.height and zone.is_walkable(nx, ny):
                        d = dx * dx + dy * dy
                        if best is None or d < best[0]:
                            best = (d, nx, ny)
            if best:
                break
        if best is None:
            raise AssertionError(("trash with no floor within reach", m, x, y))
        out.append((best[1], best[2], m, lvl))
    return out


def build_rotroot_baked():
    return build_rotroot()


def generate_rotroot_deeps():
    zone, _b = build_rotroot()
    from world.dungeon_packs import attach_packs
    avoid = [PORTAL] + [tuple(b[:2]) for b in zone.boss_positions]
    packs = attach_packs(zone, [_snap(zone, p) for p in _trash()], avoid=avoid)
    TRASH[:] = [m for p in packs for m in p]
    from tools.handbuilt_vot_caves import register_baked
    register_baked(zone, BAKED)
    return zone


if __name__ == "__main__":
    from collections import deque
    z, _ = build_rotroot()
    start = (PORTAL[0], PORTAL[1] + 2)
    seen, q = {start}, deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and z.is_walkable(*n):
                seen.add(n)
                q.append(n)
    walk = sum(z.is_walkable(x, y) for y in range(H) for x in range(W))
    print(z.name, W, "x", H, "| walkable", walk, "| reached", len(seen),
          "| bosses reached", all(tuple(b[:2]) in seen for b in z.boss_positions))
