"""
Hand-built Jaedenar (160x190): the Shadow Council's hold in North Felwood. EIGHT BOSSES, 52-55.

claude/felwood_brief.md. Kyle, 14 Nov 2026: "likely something 51-55 with a dungeon thats 52-55 to drop
the hands", "Jaedenar", and "dungeon should be about 8 bosses." Every boss has a 20% chance at the T0
hands token and the last always drops one (tools/build_tempest_loot.py); one fight is two bosses at
once and drops three.

TWO LEVELS ON ONE MAP, the Khaz Varun shape:

    THE SHADOW HOLD (south). Built: squared halls of dressed stone the Council took from the
    Highborne and made its own. You come in at the Black Gate, cross the Bloodied Yard and go up
    through the Hall of Whispers to the Summoner's Sanctum. The Barracks, the Kennels, the Black
    Library and the Shadow Chapel hang off the way.
    THE SUMMONING PIT (north). Carved: under the Sanctum the floor goes down into the caves the
    Council has been opening to the Nether. Round chambers, fel underfoot, and the thing they
    summoned sitting on a throne at the bottom.

    gate -> 1 Hold-Warden Gorvash (yard) -> 2 Inquisitor Xel'thas (hall) -> 4 Master Summoner Kaz'reth
                                               \\-> 3 the Duskwhisper Sisters and Zeth'rak (library, west)
         -> the stair down -> 6 Doomlord Kazrak (the pit) -> 8 Zar'gothrax the Unbound (the throne)
                                 \\-> 5 the Entropic Horror (the Maw, east, optional)
                                 \\-> 7 Grimbark the Chained (the Chained Grove, west, optional)

EVERY BOSS ASKS ONE THING (kits in tools/build_isle_dungeon_kits.py, JAEDENAR):
    1 Hold-Warden Gorvash        plants his banner: his guards fight harder near it. Kill the guards.
    2 Inquisitor Xel'thas        reflects spells he's hit with: casters ease off while it's up
    3 the Duskwhisper Sisters    two warlock sisters and the eredar they made their pact with, one
      and Zeth'rak the Pactbound fight: the Sisters drain life to heal, Zeth'rak hits back. Kill the
                                 Sisters first. Drops three.
    4 Master Summoner Kaz'reth   opens portals: imps keep coming until he falls
    5 the Entropic Horror        its hits make you take more from everything: a tank swap, or heal through
    6 Doomlord Kazrak            armour that grows each turn he isn't stunned or slowed: bring armour pen
    7 Grimbark the Chained       a corrupted ancient: heals off the fel in the grove. Burst it.
    8 Zar'gothrax the Unbound    everything at once, and holds at the brink once

Packs of four or five between bosses (Kyle: "in dungeons enemies are in packs of 4 to 5"), through
world/dungeon_packs.attach_packs.

HARD CONTRACTS (world/portal_manager.py)
  (80, 186) <-> North Felwood (19, 106)   the Black Gate, cut into North Felwood's west wall
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

NAME = "Jaedenar"
BAKED = "assets/tiles/jaedenar/baked"
W, H = 160, 190
PORTAL = (80, 186)

#: (x0, y0, x1, y1, chamfer, name). The hold is cut stone and right angles.
ROOMS = {
    "gate":     (66, 172, 94, 188, 1, "The Black Gate"),
    "yard":     (24, 146, 136, 168, 2, "The Bloodied Yard"),
    "barracks": (6, 116, 40, 140, 1, "The Felguard Barracks"),
    "kennels":  (120, 116, 154, 140, 1, "The Kennels"),
    "hall":     (52, 114, 108, 138, 2, "The Hall of Whispers"),
    "library":  (8, 82, 46, 106, 1, "The Black Library"),
    "chapel":   (114, 82, 152, 106, 1, "The Shadow Chapel"),
    "sanctum":  (54, 82, 106, 106, 2, "The Summoner's Sanctum"),
}
#: (cx, cy, rx, ry, rot, phase, name). The pit is carved, round and uneven.
CAVERNS = {
    "descent": (80, 70, 12, 6, 0, 0.4, "The Descent"),
    "cells":   (34, 58, 14, 9, 0, 1.2, "The Binding Cells"),
    "maw":     (128, 56, 13, 9, 0, 2.1, "The Maw"),
    "pit":     (80, 42, 22, 11, 0, 0.8, "The Summoning Pit"),
    "grove":   (30, 24, 14, 9, 0, 1.7, "The Chained Grove"),
    "throne":  (80, 14, 18, 8, 0, 2.6, "The Burning Throne"),
}
#: EVERY END OF EVERY LINK SITS INSIDE THE SPACE IT JOINS (the Drywhisker lesson).
PATHS = {
    "in":       ([(80, 186), (80, 178), (80, 170)], 6.0, 6.0),
    "gate_up":  ([(80, 176), (80, 166), (80, 158)], 6.0, 6.0),
    "barracks": ([(30, 152), (26, 144), (22, 132)], 4.4, 4.4),
    "kennels":  ([(130, 152), (134, 144), (138, 132)], 4.4, 4.4),
    "hall_up":  ([(80, 152), (80, 142), (80, 130)], 5.4, 5.4),
    "library":  ([(60, 126), (44, 114), (28, 98)], 4.6, 4.6),
    "chapel":   ([(100, 126), (116, 114), (132, 98)], 4.6, 4.6),
    "sanctum":  ([(80, 120), (80, 110), (80, 98)], 5.4, 5.4),
    # THE STAIR DOWN: from behind the Summoner's dais into the pit
    "stair":    ([(80, 88), (80, 80), (80, 70)], 5.0, 4.6),
    "cells":    ([(72, 68), (54, 62), (36, 58)], 4.2, 4.2),
    "maw":      ([(88, 68), (108, 62), (126, 56)], 4.2, 4.2),
    "pit":      ([(80, 68), (80, 58), (80, 46)], 5.0, 5.0),
    "grove":    ([(34, 54), (32, 40), (30, 26)], 4.0, 4.0),
    "throne":   ([(80, 38), (80, 28), (80, 16)], 5.2, 5.2),
}
#: Pillars down the hold's halls, so they read as vaulted rooms, not boxes.
COLONNADES = [((32, 48, 64, 96, 112, 128), (150, 164)),
              ((58, 70, 90, 102), (118, 134)),
              ((60, 72, 88, 100), (86, 102))]

#: (x, y, name, required)
BOSS_LIST = [
    (80, 154, "Hold-Warden Gorvash", True),
    (80, 122, "Inquisitor Xel'thas", True),
    (24, 92, "The Duskwhisper Sisters", True),
    (80, 90, "Master Summoner Kaz'reth", True),
    (130, 54, "The Entropic Horror", False),
    (80, 40, "Doomlord Kazrak", True),
    (30, 22, "Grimbark the Chained", False),
    (80, 10, "Zar'gothrax the Unbound", True),
]
#: One encounter, two bosses: Zeth'rak folds into the Sisters' spawn (world/cave_spawns, zone.boss_pack).
SISTERS_PACK = {"The Duskwhisper Sisters": [(28, 92, "Zeth'rak the Pactbound")]}
BOSSES = {}
CHESTS = []
TRASH = []
CHEST_SPOTS = [(12, 122), (148, 122), (146, 88), (12, 102), (24, 64), (138, 62), (40, 18)]


def build_jaedenar():
    zone = Tilemap(NAME, W, H,
                   "The Shadow Council's hold in North Felwood: Highborne halls they made their own, "
                   "and under them the pit where they open the way for the Legion.")
    zone.is_cave = True
    #: the PARENT OPEN ZONE, which is also the encounter-table key
    zone.region = "North Felwood"
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b

    for (x0, y0, x1, y1, ch, _n) in ROOMS.values():
        b.rect(x0, y0, x1, y1, chamfer=ch)
    for (cx, cy, rx, ry, rot, ph, _n) in CAVERNS.values():
        cavern(b, cx, cy, rx, ry, rot, ph)
    for i, (pts, w0, w1) in enumerate(PATHS.values()):
        tube(b, pts, w0, w1, ph=0.3 + i * 0.6)
    for (xs, ys) in COLONNADES:
        for x in xs:
            for y in ys:
                zone.collision_layer[y][x] = "wall"
                zone.set_tile(x, y, "rock", "collision")
    dress(zone, L)

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    fixed = []
    for (x, y, n, _req) in BOSS_LIST:
        if not zone.is_walkable(x, y):
            raise AssertionError(("boss in solid rock", n, x, y))
        L.mark("boss_marker", x, y)
        fixed.append((x, y, n))
    for lead, members in SISTERS_PACK.items():
        for (x, y, n) in members:
            if not zone.is_walkable(x, y):
                raise AssertionError(("pack boss in solid rock", n, x, y))
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (80, 10)
    zone.boss_positions = list(fixed)
    zone.boss_pack = SISTERS_PACK

    chests = []
    for c in CHEST_SPOTS:
        # a carved chamber's edge is uneven: a chest takes the nearest floor within four tiles
        x, y = _snap(zone, [(c[0], c[1], "chest", 0)], rad=4)[0][:2]
        L.mark("chest", x, y)
        chests.append((x, y))
    CHESTS[:] = chests

    zone.add_subzone(NAME, 0, 0, W, H)
    for (x0, y0, x1, y1, _ch, name) in ROOMS.values():
        zone.add_subzone(name, x0 - 2, y0 - 2, (x1 - x0) + 4, (y1 - y0) + 4)
    for (cx, cy, rx, ry, _r, _p, name) in CAVERNS.values():
        zone.add_subzone(name, int(cx - rx - 2), int(cy - ry - 2), int(2 * rx + 4), int(2 * ry + 4))
    return zone, L


_DP = "assets/tiles/dungeon_props/"
_FP = "assets/tiles/felwood/props/"
#: (sprite, x, base_y, height, solid). Less is more: a few centrepieces, logical for the room.
DRESSING = [
    # the gate and the yard: the Council's banners over what was a Highborne court
    (_DP + "bbc_banner.png", 70, 175, 5, "core"), (_DP + "bbc_banner.png", 90, 175, 5, "core"),
    (_FP + "fw_fel_brazier.png", 60, 158, 4, "core"), (_FP + "fw_fel_brazier.png", 100, 158, 4, "core"),
    (_DP + "bbc_weapon_rack.png", 40, 150, 3, False), (_DP + "rf_prison_cage.png", 120, 150, 4, "core"),
    # the barracks and the kennels
    (_DP + "bbc_weapon_rack.png", 14, 120, 3, False), (_DP + "bbc_tent.png", 30, 124, 5, "core"),
    (_DP + "kennel_cage_empty.png", 128, 122, 4, "core"), (_DP + "kennel_cage_worg.png", 144, 132, 4, "core"),
    # the Hall of Whispers
    (_DP + "bbc_candelabra.png", 62, 128, 4, False), (_DP + "bbc_candelabra.png", 98, 128, 4, False),
    (_DP + "bbc_rune_pillar.png", 80, 116, 5, "core"),
    # the Black Library and the Shadow Chapel
    (_DP + "bbc_bookshelf.png", 14, 86, 4, "core"), (_DP + "bbc_bookshelf.png", 38, 86, 4, "core"),
    (_DP + "bbc_warlock_desk.png", 32, 98, 3, "core"),
    (_DP + "bbc_altar.png", 134, 86, 4, "core"), (_DP + "bbc_chains.png", 122, 96, 3, False),
    # the Summoner's Sanctum
    (_FP + "fw_summoning_dais.png", 80, 94, 4, False),
    (_FP + "fw_fel_obelisk.png", 62, 88, 6, "core"), (_FP + "fw_fel_obelisk.png", 98, 88, 6, "core"),
    # the pit: fel and what came through it
    (_FP + "fw_fel_crystals.png", 70, 72, 3, False), (_FP + "fw_fel_crystals.png", 92, 72, 3, False),
    (_DP + "rf_prison_cage.png", 26, 54, 4, "core"), (_DP + "bbc_chains.png", 42, 60, 3, False),
    (_FP + "fw_fel_pool.png", 138, 52, 4, False), (_FP + "fw_demon_bones.png", 120, 60, 2, False),
    (_DP + "bbc_summon_circle.png", 80, 46, 3, False),
    (_FP + "fw_demon_portal.png", 66, 36, 7, "core"), (_FP + "fw_demon_portal.png", 94, 36, 7, "core"),
    (_FP + "fw_corrupted_tree.png", 20, 20, 8, "core"), (_FP + "fw_dead_ironwood.png", 42, 28, 8, "core"),
    (_FP + "fw_fel_mushrooms.png", 34, 30, 3, False),
    (_DP + "bbc_throne.png", 80, 8, 5, "core"),
    (_DP + "bbc_fel_pylon.png", 66, 12, 5, "core"), (_DP + "bbc_fel_pylon.png", 94, 12, 5, "core"),
]


def dress(zone, L):
    for (path, x, y, h, solid) in DRESSING:
        if not zone.is_walkable(x, y):
            raise AssertionError(("prop base not on the floor", path, x, y))
        L.b.prop(path, x, y, h, solid=solid, fraction=0.4)


def _trash():
    """Hand-placed pulls, door to throne: each pack(...) is one pull, filled to four or five."""
    T = []

    def pack(lvl, *spots):
        T.append([(x, y, m, lvl) for (x, y, m) in spots])

    # ---- the gate and the yard
    pack(52, (80, 180, "Shadow Council Acolyte"), (76, 176, "Jaedenar Felguard"), (84, 176, "Shadow Council Acolyte"))
    pack(52, (44, 160, "Jaedenar Hound Handler"), (48, 156, "Jaedenar Felhound"), (40, 156, "Jaedenar Felhound"))
    pack(52, (116, 160, "Jaedenar Felguard"), (112, 156, "Shadow Council Acolyte"), (120, 156, "Jaedenar Imp"))
    # ---- the barracks and the kennels (off the yard)
    pack(53, (22, 128, "Jaedenar Felguard"), (16, 132, "Jaedenar Felguard"), (28, 132, "Shadow Council Warlock"))
    pack(53, (136, 128, "Jaedenar Hound Handler"), (130, 132, "Jaedenar Felhound"), (142, 124, "Jaedenar Felhound"))
    # ---- the Hall of Whispers
    pack(53, (80, 136, "Shadow Council Warlock"), (74, 132, "Bound Voidwalker"), (86, 132, "Shadow Council Acolyte"))
    pack(53, (64, 120, "Jaedenar Felguard"), (60, 126, "Shadow Council Warlock"))
    pack(53, (96, 120, "Jaedenar Felguard"), (100, 126, "Shadow Council Warlock"))
    # ---- the Black Library and the Shadow Chapel
    pack(54, (36, 102, "Shadow Council High Warlock"), (40, 96, "Bound Voidwalker"), (30, 104, "Shadow Council Acolyte"))
    pack(54, (126, 100, "Shadow Council High Warlock"), (132, 104, "Bound Voidwalker"), (140, 98, "Jaedenar Imp"))
    pack(54, (140, 90, "Shadow Council Summoner"), (130, 92, "Jaedenar Felguard"))
    # ---- the Summoner's Sanctum
    pack(54, (80, 104, "Shadow Council Summoner"), (72, 100, "Jaedenar Imp"), (88, 100, "Jaedenar Imp"))
    pack(54, (64, 96, "Shadow Council High Warlock"), (96, 96, "Shadow Council High Warlock"))
    # ---- down into the pit
    pack(54, (80, 74, "Jaedenar Doomguard"), (74, 70, "Jaedenar Felhound"), (86, 70, "Jaedenar Felhound"))
    pack(54, (44, 60, "Bound Voidwalker"), (36, 62, "Shadow Council Summoner"), (28, 56, "Bound Voidwalker"))
    pack(55, (116, 58, "Jaedenar Infernal"), (124, 62, "Jaedenar Imp"), (122, 50, "Jaedenar Imp"))
    pack(55, (80, 52, "Jaedenar Doomguard"), (72, 48, "Jaedenar Felguard"), (88, 48, "Jaedenar Felguard"))
    pack(55, (64, 42, "Jaedenar Infernal"), (96, 42, "Jaedenar Infernal"))
    # ---- the Chained Grove
    pack(55, (32, 32, "Jaedenar Felhound"), (26, 28, "Bound Voidwalker"), (38, 26, "Jaedenar Felhound"))
    # ---- the Burning Throne
    pack(55, (80, 26, "Jaedenar Doomguard"), (72, 20, "Jaedenar Doomguard"), (88, 20, "Shadow Council High Warlock"))
    return T


def _snap(zone, spots, rad=5):
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


def build_jaedenar_baked():
    """The map for the baker to paint from (no register_baked: the art doesn't exist yet)."""
    return build_jaedenar()


def generate_jaedenar():
    zone, L = build_jaedenar()
    from world.dungeon_packs import attach_packs
    avoid = [PORTAL] + [tuple(b[:2]) for b in zone.boss_positions]
    packs = attach_packs(zone, [_snap(zone, p) for p in _trash()], avoid=avoid)
    TRASH[:] = [m for p in packs for m in p]
    register_baked(zone, BAKED)
    return zone


if __name__ == "__main__":
    z, L = build_jaedenar()
    seen = L._reach()
    crit = [c for c in L.critical if c not in seen]
    print(z.name, z.width, "x", z.height, "| bosses", len(z.boss_positions), "| reachable", len(seen),
          "| critical unreachable", crit, "| skipped props", L.skipped)
