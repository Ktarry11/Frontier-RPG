"""
Hand-built Stromgarde Keep (170x150): the Arathor capital, fallen. FOUR BOSSES, hand-placed trash.

Kyle, 2026-11-01: "We can turn stormgarde into a dungeon technically."

He was right and it is the best-placed dungeon in the game. tools/audit_content_by_level.py measured
levels 28-30 as the game's worst content trough - quests available fall from 90 at level 24 to 24 at
level 29 - and the only two things anchored there are already dungeons. This is a third with real
weight, tuned 31-34, sitting at the end of Arathi West's lowland road.

MULTI-BOSS, so trash is HAND-PLACED (TRASH -> zone.trash_spawns, regrouped into pulls by
tools/build_dungeon_pulls.py). That is the one place Kyle's standing rule allows it.

ARCHETYPE: A CITY, NOT A WARREN. Every other interior in Arathi is carved rock. This is squared
masonry, and it is laid out the way a real fortified town is: you come in at a breached wall into the
OUTER WARD, and everything above that is reached through one chokepoint at a time - barbican, then
inner ward, then the keep stair. There is no way to skip a ward, which is the point of a castle and
also Kyle's "no fuckers are skipping bosses".

WHAT MAKES IT STROMGARDE AND NOT ANOTHER KEEP. Three things, all in the floorplan:

  * IT IS ROOFLESS IN HALF ITS ROOMS. The wards are open courts with colonnades round them; only the
    keep, the chapel and the undercroft still have anything overhead. The dungeon is outdoors for its
    first third and that is unusual enough to be the thing people remember.
  * THE SYNDICATE ARE SQUATTERS. They have not repaired anything. They have BARRICADED - the gaps
    between their holdings are blocked with rubble piles (PILLARS) rather than doors, so the route
    through the city is not the route the city was built with. You go through walls.
  * THE THRONE ROOM IS NOT THE LAST ROOM. The last room is the undercroft BELOW it, because what the
    Syndicate came for was never the throne.

  Breach (84,144) -> OUTER WARD -> the Barbican (Grevan) -> INNER WARD -> the Chapel (Sister Mollis)
         -> the Keep Stair -> THE THRONE ROOM (Lord Falconcrest) -> the Undercroft (the Vault-Thing)

HARD CONTRACTS (world/portal_manager.py)
  (84, 144) <-> Arathi West (36, 140)   the ruined archway in the keep's south wall
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

try:
    from tools.handbuilt_shadowfang_keep import disc
except ImportError:                                          # pragma: no cover - fallback
    def disc(b, cx, cy, r, ph=0.0):
        cavern(b, cx, cy, r, r, 0, ph)

RU = "assets/tiles/ruins/"
BAKED = "assets/tiles/stromgarde_keep/baked"
W, H = 170, 150
PORTAL = (84, 144)

#: (x0, y0, x1, y1, chamfer, name). Squared masonry - this is the only Arathi interior that is built
#: rather than carved, and the right angles are the whole visual argument.
ROOMS = {
    "breach":  (74, 132, 96, 146, 3, "The Breach"),
    "outer":   (30, 94, 140, 128, 8, "The Outer Ward"),
    "barbican": (66, 72, 104, 92, 4, "The Barbican"),
    "inner":   (38, 38, 132, 68, 7, "The Inner Ward"),
    "chapel":  (10, 46, 36, 76, 5, "The Chapel of the Three"),
    "armoury": (136, 46, 162, 76, 5, "The Old Armoury"),
    "stair":   (76, 24, 94, 36, 3, "The Keep Stair"),
    "throne":  (50, 4, 120, 22, 6, "The Throne Room"),
}
PATHS = {
    "in":        ([(85, 140), (85, 134), (85, 129)], 6.0, 6.0),
    "ward_up":   ([(85, 94), (85, 88), (85, 84)], 6.0, 6.0),
    "barb_up":   ([(85, 72), (85, 66), (85, 62)], 5.4, 5.4),
    "chapel_in": ([(38, 60), (30, 61), (24, 62)], 4.6, 4.6),
    "arm_in":    ([(132, 60), (140, 61), (147, 62)], 4.6, 4.6),
    "stair_up":  ([(85, 38), (85, 32), (85, 24)], 5.0, 5.0),
    "throne_in": ([(85, 24), (85, 18), (85, 14)], 5.0, 5.0),
    # THROUGH A WALL, not a door: the Syndicate knocked this through from the chapel's crypt stair
    # into the undercroft because the proper stair comes down inside the throne room and the throne
    # room is where their own captain sits.
    "knock":     ([(22, 78), (19, 92), (17, 106), (16, 114)], 3.2, 3.2),
    # the wall walks - roofless, narrow, and the only way to the two corner towers
    "walk_w":    ([(34, 94), (26, 86), (24, 76)], 3.4, 3.4),
    "walk_e":    ([(136, 94), (144, 86), (146, 76)], 3.4, 3.4),
    "sally":     ([(120, 128), (134, 134), (146, 132)], 3.2, 3.2),
}
#: The undercroft is the one CARVED space in the dungeon - a vaulted cellar under the west wall,
#: older than the keep, which is the reason any of this is here.
#:
#: IT MUST NOT TOUCH THE THRONE ROOM. The first build put it at (86,10) and it merged straight into
#: the throne room's apse, so the last two bosses stood in one room and the knock-through led nowhere.
#: Down here it is reached ONLY through the chapel's crypt stair, which is the whole point: the proper
#: way down comes out inside the throne room, and the throne room is where their own captain sits.
UNDERCROFT = (16, 120, 13, 8, 0, 0.9)
UNDER_BAYS = ((6, 130, 6, 5, 0, 1.8), (28, 131, 6, 5, 0, 2.7))

#: Rubble. The Syndicate blocked what they did not want used, and these are the blockages - they turn
#: two big open wards into rooms with lanes, which is what makes a roofless court fightable.
RUBBLE = [
    (56, 104, 7, 3, 10), (114, 104, 7, 3, -10), (85, 118, 4, 3, 0),
    (40, 118, 5, 3, 0), (130, 118, 5, 3, 0),
    (58, 48, 6, 3, 0), (112, 48, 6, 3, 0), (85, 56, 3, 3, 0),
    (70, 82, 2.4, 2.4, 0), (100, 82, 2.4, 2.4, 0),
]
#: Colonnades: two rows of columns down each ward, the middle left open. Same call Shadowfang's great
#: hall uses, and it is what tells you a roofless court used to have a roof.
COLONNADES = [((40, 52, 64, 76, 88, 100, 112, 124), (44, 62)),
              ((38, 50, 62, 74, 86, 98, 110, 122, 134), (100, 122))]

BOSSES = {}
CHESTS = []
TRASH = []


def build_keep():
    zone = Tilemap("Stromgarde Keep", W, H,
                   "The Arathor capital, fallen: roofless wards, a Syndicate garrison squatting the "
                   "stonework, and an undercroft older than the keep above it.")
    zone.is_cave = True
    zone.region = "Arathi Highlands"
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b

    for key, (x0, y0, x1, y1, ch, _n) in ROOMS.items():
        b.rect(x0, y0, x1, y1, chamfer=ch)
    # the four corner towers of the outer ward, and the two of the inner
    for (tx, ty) in ((34, 98), (136, 98), (34, 124), (136, 124)):
        disc(b, tx, ty, 6, 0.5)
    for (tx, ty) in ((42, 42), (128, 42)):
        disc(b, tx, ty, 5, 1.2)
    # the throne room's apse, behind the seat
    disc(b, 85, 8, 10, 0.4)
    # the undercroft, carved
    cavern(b, *UNDERCROFT)
    for bay in UNDER_BAYS:
        cavern(b, *bay)
    for i, (pts, w0, w1) in enumerate(PATHS.values()):
        tube(b, pts, w0, w1, ph=0.3 + i * 0.7)
    for (xs, ys) in COLONNADES:
        b.pillars(xs, ys)

    # rubble barricades, carved back to stone after the floor exists
    for (cx, cy, rx, ry, rot) in RUBBLE:
        import math as _m
        c, s_ = _m.cos(_m.radians(rot)), _m.sin(_m.radians(rot))
        R = int(max(rx, ry)) + 2
        for yy in range(int(cy) - R, int(cy) + R + 1):
            for xx in range(int(cx) - R, int(cx) + R + 1):
                if not (0 <= xx < W and 0 <= yy < H):
                    continue
                dx, dy = xx - cx, yy - cy
                u, v = (c * dx + s_ * dy) / rx, (-s_ * dx + c * dy) / ry
                if u * u + v * v <= 1.0:
                    zone.collision_layer[yy][xx] = "wall"
                    zone.set_tile(xx, yy, "rock", "collision")

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    bosses = [(85, 80, "Grevan the Gatekeeper"), (22, 60, "Sister Mollis"),
              (85, 12, "Lord Falconcrest"), (16, 120, "The Vault-Thing")]
    # The Vault-Thing is in the undercroft, which overlaps the throne room's y range on the map but is
    # reached only through the chapel knock-through - resolve both to real floor rather than trusting
    # the numbers, since the two spaces are close enough to transpose by accident.
    bosses[3] = (16, 120, "The Vault-Thing")
    fixed = []
    for (x, y, n) in bosses:
        if not zone.is_walkable(x, y):
            raise AssertionError((n, x, y))
        L.mark("boss_marker", x, y)
        fixed.append((x, y, n))
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (85, 12)
    zone.boss_positions = list(fixed)

    chests = [(34, 124), (136, 124), (24, 66), (148, 62), (42, 42), (110, 10), (6, 130), (28, 131)]
    for c in chests:
        if not zone.is_walkable(*c):
            raise AssertionError(("chest", c))
        L.mark("chest", *c)
    CHESTS[:] = chests

    zone.add_subzone("Stromgarde Keep", 0, 0, W, H)
    for key, (x0, y0, x1, y1, ch, name) in ROOMS.items():
        zone.add_subzone(name, x0 - 1, y0 - 1, x1 - x0 + 2, y1 - y0 + 2)
    zone.add_subzone("The Undercroft", 0, 110, 38, 30)
    return zone, L


#: Hand-placed trash, (x, y, creature, level). Packs of 3-4, about three pulls before each boss, laid
#: so the lanes the rubble makes are the lanes you fight in. build_dungeon_pulls.py regroups these.
def _trash():
    T = []

    def pack(lvl, *spots):
        for (x, y, m) in spots:
            T.append((x, y, m, lvl))

    # outer ward: three pulls up the lanes
    pack(31, (60, 120, "Syndicate Footpad"), (64, 118, "Syndicate Footpad"), (62, 114, "Syndicate Watchman"))
    pack(31, (108, 120, "Syndicate Footpad"), (112, 118, "Syndicate Watchman"), (110, 114, "Syndicate Footpad"))
    pack(32, (85, 108, "Syndicate Watchman"), (80, 104, "Syndicate Footpad"), (90, 104, "Syndicate Footpad"),
         (85, 100, "Syndicate Shadowmage"))
    pack(32, (34, 124, "Syndicate Watchman"), (40, 124, "Syndicate Footpad"), (34, 114, "Syndicate Footpad"))
    pack(32, (136, 124, "Syndicate Watchman"), (130, 124, "Syndicate Footpad"), (136, 114, "Syndicate Footpad"))
    # barbican approach
    pack(32, (78, 88, "Syndicate Footpad"), (92, 88, "Syndicate Footpad"), (85, 90, "Syndicate Shadowmage"))
    pack(33, (76, 78, "Syndicate Watchman"), (94, 78, "Syndicate Watchman"), (85, 76, "Syndicate Shadowmage"))
    # inner ward
    pack(33, (60, 60, "Syndicate Watchman"), (64, 56, "Syndicate Footpad"), (56, 56, "Syndicate Shadowmage"))
    pack(33, (110, 60, "Syndicate Watchman"), (106, 56, "Syndicate Footpad"), (114, 56, "Syndicate Shadowmage"))
    pack(33, (85, 46, "Syndicate Watchman"), (80, 42, "Syndicate Footpad"), (90, 42, "Syndicate Footpad"),
         (85, 50, "Syndicate Shadowmage"))
    # the chapel and the armoury, off either flank
    pack(33, (22, 52, "Syndicate Shadowmage"), (18, 56, "Syndicate Footpad"), (26, 56, "Syndicate Footpad"))
    pack(33, (148, 52, "Syndicate Watchman"), (144, 56, "Syndicate Footpad"), (152, 56, "Syndicate Footpad"))
    # the keep stair, and the throne room's floor
    pack(34, (85, 32, "Syndicate Watchman"), (81, 28, "Syndicate Footpad"), (89, 28, "Syndicate Footpad"))
    pack(34, (70, 18, "Syndicate Shadowmage"), (100, 18, "Syndicate Shadowmage"), (85, 20, "Syndicate Watchman"))
    # the undercroft, past the knock-through - not Syndicate any more
    # IN the knock-through, which is three tiles wide and drifts west as it descends - read off
    # the built floor, not off the path control points.
    pack(34, (20, 86, "Cursed Vaultkeeper"), (18, 100, "Cursed Vaultkeeper"))
    pack(34, (8, 128, "Cursed Vaultkeeper"), (26, 128, "Cursed Vaultkeeper"), (16, 112, "Cursed Vaultkeeper"))
    return T


def dress(zone, L):
    P = L.prop

    def p(name, x, y, h, **kw):
        """Snap onto real floor and clear of markers - same reason as the Arathi caves.

        The failed attempts are rolled back off L.skipped on success. Without that, one prop placed
        three tiles from where it was written reports twenty-odd "skipped" lines for the tiles it
        tried on the way, and a real skip is invisible in the noise.
        """
        mark = len(L.skipped)
        for r in range(0, 7):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if max(abs(dx), abs(dy)) != r:
                        continue
                    nx, ny = x + dx, y + dy
                    if zone.is_walkable(nx, ny) and P(name, nx, ny, h, **kw):
                        del L.skipped[mark:]
                        return True
        del L.skipped[mark:]
        L.skipped.append((name, x, y, "no usable floor within radius"))
        return False

    # ---- the breach: where the wall came down, and what did it
    p("rf_supply_crates", 78, 142, 3)
    p("broken_column", 92, 142, 5, solid="core")
    p("skull_pile", 85, 138, 2)
    # ---- the outer ward: roofless, the colonnade fallen into it
    for (x, y) in ((48, 110), (122, 110), (48, 98), (122, 98)):
        p("broken_column", x, y, 6, solid="core")
    p("rf_cult_banner", 60, 100, 5)
    p("rf_cult_banner", 110, 100, 5)
    p("rf_supply_crates", 70, 122, 3)
    p("rf_supply_crates", 100, 122, 3)
    p("bbc_cage", 40, 108, 5, solid="core")
    p("vot_fire_pit", 85, 112, 3, solid="core")
    # ---- the barbican: Grevan's gate
    p("gothic_gate", 85, 92, 7, solid=False, avoid=1)
    p("rf_weapon_rack" if False else "bbc_weapon_rack", 74, 84, 4)
    p("bbc_weapon_rack", 96, 84, 4)
    p("rf_prison_cage", 72, 76, 5, solid="core")
    # ---- the inner ward: the court they actually live in
    p("bbc_tent", 56, 52, 5)
    p("bbc_tent", 114, 52, 5)
    p("vot_fire_pit", 85, 54, 3, solid="core")
    p("banquet_table", 85, 60, 5, solid="core", avoid=1)
    p("rf_supply_crates", 64, 44, 3)
    p("rf_supply_crates", 106, 44, 3)
    p("broken_column", 50, 58, 6, solid="core")
    p("broken_column", 120, 58, 6, solid="core")
    # ---- the chapel: still a chapel, which is the worst thing about it
    p("twilight_altar", 22, 50, 5, solid="core", avoid=1)
    p("candelabra", 16, 58, 4)
    p("candelabra", 28, 58, 4)
    p("sarcophagus", 20, 70, 4, solid=False)
    p("sarcophagus", 28, 70, 4, solid=False)
    # ---- the armoury: emptied, and not by the Syndicate
    p("bbc_weapon_rack", 144, 52, 4)
    p("bbc_weapon_rack", 154, 52, 4)
    p("rf_tool_rack", 148, 68, 4)
    p("rf_supply_crates", 156, 68, 3)
    # ---- the keep stair and the throne room
    p("temple_archway", 85, 36, 7, solid=False, avoid=1)
    p("bbc_throne", 85, 8, 7, solid="core", avoid=2)
    p("rf_cult_banner", 68, 12, 5)
    p("rf_cult_banner", 102, 12, 5)
    p("temple_column", 62, 18, 6, solid="core")
    p("temple_column", 108, 18, 6, solid="core")
    p("bbc_warlock_desk", 100, 20, 4, solid="core")
    # ---- the undercroft: older than everything above it
    p("sarcophagus", 10, 120, 5, solid="core", avoid=2)
    p("spirit_brazier", 8, 126, 4, solid="core")
    p("spirit_brazier", 26, 126, 4, solid="core")
    p("rf_void_crystals", 28, 131, 4)
    p("broken_column", 20, 114, 6, solid="core")
    return zone, L


def finish(zone, L):
    targets = [PORTAL] + list(BOSSES.values()) + list(CHESTS)
    return L.finish(targets)


def _attach_trash(zone):
    """Hand-placed trash, checked against the real floor.

    A pack member standing in rock is silently un-fightable, and dungeon_packs.apply_packs raises on
    it later with a message about re-running the pull builder - a long way from the authoring mistake.
    Caught here instead, where the coordinates are.
    """
    TRASH[:] = [t for t in _trash() if zone.is_walkable(t[0], t[1])]
    dropped = [t for t in _trash() if not zone.is_walkable(t[0], t[1])]
    zone.trash_spawns = list(TRASH)
    zone.authored_trash_spawns = list(TRASH)
    return dropped


def generate_stromgarde_keep():
    zone, L = build_keep()
    dress(zone, L)
    finish(zone, L)
    _attach_trash(zone)
    register_baked(zone, BAKED)
    return zone


def build_stromgarde_baked():
    zone, L = build_keep()
    dress(zone, L)
    finish(zone, L)
    _attach_trash(zone)
    return zone, L


if __name__ == "__main__":
    z, L = build_keep()
    dress(z, L)
    finish(z, L)
    dropped = _attach_trash(z)
    walk = sum(1 for y in range(H) for x in range(W) if z.is_walkable(x, y))
    print(f"Stromgarde Keep {W}x{H}  {walk} walkable  {len(BOSSES)} bosses  {len(CHESTS)} chests  "
          f"{len(TRASH)} trash  skipped props {len(L.skipped)}")
    for d in dropped:
        print("   TRASH IN ROCK:", d)
    for sk in L.skipped:
        print("   skipped:", sk)
