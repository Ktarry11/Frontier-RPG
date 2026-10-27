"""
Hand-built Durnholde Keep (140x120): the Syndicate's stronghold in Eastern Hillsbrad, levels 26-30.

ARCHETYPE: THE BROKEN RING.  Not Shadowfang's stepped castle (which climbs), not Ambermill's stacked
octagons, not a cave shape at all.  Durnholde is a CURTAIN WALL with a dead keep inside it: you come in
under the gatehouse and the only way forward is the BAILEY WALK, a ring corridor that runs the whole way
round the inner keep with a tower at each corner.  The keep itself is sealed - its gate fell in - so you
circle the ring looking for a way in, and there are two BREACHES in the inner wall, east and west, which
means the ring can be walked either direction and the two flanking bosses can be taken in either order.
Inside, the Lord's Hall sits over a collapsed UNDERCROFT reached by the stair behind the dais.

    Gatehouse (70,112)  ->  BAILEY WALK (the ring)  ->  corner towers: Kennel (SE), Magister's (SW),
                                                        Armoury (NW), Watch (NE)
                        ->  east or west BREACH  ->  THE INNER KEEP courtyard
                        ->  THE LORD'S HALL (Perenolde)  ->  stair  ->  THE UNDERCROFT (the Keepkeeper)

A real Dungeon, not a mining cave: registered in world/zone_classification.DUNGEONS, which is what keeps
gathering nodes out of it (Kyle: "caves (and keeps) are fine, just not dungeons").

Five bosses, pinned; trash is random from the table (zone.fixed_spawns = False).
  Sergeant-at-Arms Varth 27 (gatehouse) | Houndmaster Sable 28 (kennel) | Magister Yvaine 28 (magister's)
  The Keepkeeper 29 (undercroft)        | Baron Aliden Perenolde 30 (lord's hall)

HARD CONTRACTS (world/portal_manager.py): portal (70,112) <-> Eastern Hillsbrad (109,74); arrival = 2 north.
Prop rule (Kyle): less is more; logical for the room; a few centrepieces.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401

BAKED = "assets/tiles/durnholde_keep/baked"
W, H = 140, 120
PORTAL = (70, 112)

#: The curtain wall's inside face - the bailey walk runs just inside this.
OUTER = (16, 14, 124, 102)          # x0, y0, x1, y1
RING_W = 5                          # how wide the bailey walk is (a corridor, not a parade ground:
                                    # at 9 the ring and the corner towers merged into one open band)
#: Rooms: (x0, y0, x1, y1, display name). The keep's three chambers sit WELL clear of the bailey walk -
#: the first version let the Lord's Hall overlap the north walk, which quietly connected the "sealed" keep
#: straight to the ring and made both breaches decorative. Sealing them and re-running the flood fill is
#: what caught it; the gaps below (y22-25 above the undercroft, 28 tiles either side of the chambers) are
#: the seal, and the breach corridors are the only thing that crosses them.
ROOMS = {
    "gatehouse":  (60, 96, 80, 112, "The Gatehouse"),
    "kennel":     (98, 74, 122, 98, "The Kennels"),
    "magister":   (18, 74, 42, 98, "The Magister's Tower"),
    "armoury":    (18, 18, 42, 42, "The Armoury"),
    "watch":      (98, 18, 122, 42, "The Watch Tower"),
    "keep":       (48, 60, 92, 88, "The Inner Keep"),
    "hall":       (52, 36, 88, 56, "The Lord's Hall"),
    "undercroft": (58, 22, 82, 34, "The Undercroft"),
}
#: The two ways through the curtain into the keep courtyard: (points, width)
#: width=N in Builder.corridor carves roughly 2N+1 tiles (see ZoneGenerator._carve_path - it clears a
#: perpendicular line of the stated width either side of travel). A width of 7 made these 15 tiles tall,
#: which swallowed the kennel and stopped reading as "a hole knocked in a wall" entirely. 3 is a breach.
BREACHES = [
    ([(120, 73), (88, 73)], 3),      # east breach
    ([(20, 73), (52, 73)], 3),       # west breach
]

BOSSES = {}
CHESTS = []


def _near_walkable(zone, x, y, rad=6):
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            if zone.is_walkable(int(x) + dx, int(y) + dy):
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, int(x) + dx, int(y) + dy)
    return None if best is None else (best[1], best[2])


def build_durnholde():
    zone = Tilemap("Durnholde Keep", W, H,
                   "A curtain wall around a dead keep. The Syndicate hold the walls; something else holds "
                   "the undercroft.")
    zone.is_cave = True                 # interior zone - same renderer path as the keeps in Silverpine
    zone.region = "Hillsbrad Foothills"
    zone.fixed_spawns = False
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b

    x0, y0, x1, y1 = OUTER
    # The bailey walk: four corridors forming a closed ring just inside the curtain wall.
    b.rect(x0, y0, x1, y0 + RING_W)                      # north walk
    b.rect(x0, y1 - RING_W, x1, y1)                      # south walk
    b.rect(x0, y0, x0 + RING_W, y1)                      # west walk
    b.rect(x1 - RING_W, y0, x1, y1)                      # east walk

    # Corner towers and the gatehouse hang off the ring.
    for key in ("gatehouse", "kennel", "magister", "armoury", "watch"):
        rx0, ry0, rx1, ry1, _ = ROOMS[key]
        b.rect(rx0, ry0, rx1, ry1, chamfer=3)

    # The keep's three chambers, carved individually - NOT one big block, and nothing touching the ring.
    for key in ("keep", "hall", "undercroft"):
        rx0, ry0, rx1, ry1, _ = ROOMS[key]
        b.rect(rx0, ry0, rx1, ry1, chamfer=3)
    b.corridor([(70, 61), (70, 55)], width=3)            # courtyard -> the Lord's Hall
    b.corridor([(70, 37), (70, 33)], width=2)            # hall -> the stair down to the undercroft

    # The two breaches - the only ways through the inner wall.
    for pts, wdt in BREACHES:
        b.corridor(pts, width=wdt)

    # Short stubs joining the towers to the ring, so nothing relies on a room merely touching it.
    b.corridor([(70, 104), (70, 98)], width=3)           # gatehouse -> south walk
    b.corridor([(110, 74), (110, 68)], width=3)          # kennel -> east walk
    b.corridor([(30, 74), (30, 68)], width=3)            # magister -> west walk
    b.corridor([(30, 42), (30, 48)], width=3)            # armoury -> west walk
    b.corridor([(110, 42), (110, 48)], width=3)          # watch -> east walk

    # Pillars down the Lord's Hall - it should read as a hall, not a box.
    b.pillars([58, 82], [42, 50], size=2)

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.set_tile(px, py, "dirt", "base")
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    bosses = [(70, 104, "Sergeant-at-Arms Varth"),
              (110, 86, "Houndmaster Sable"),
              (30, 86, "Magister Yvaine"),
              (70, 28, "The Keepkeeper"),
              (70, 46, "Baron Aliden Perenolde")]
    fixed = []
    for (x, y, n) in bosses:
        p = _near_walkable(zone, x, y)
        assert p, (n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (fixed[0][0], fixed[0][1])
    zone.boss_positions = list(fixed)

    chests = []
    for (x, y) in ((30, 30), (110, 30), (70, 76), (70, 28), (110, 86)):
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        chests.append(p)
    CHESTS[:] = chests
    for c in chests:
        L.mark("chest", *c)

    zone.add_subzone("Durnholde Keep", 0, 0, W, H)       # the encounter-table key covers the whole map
    for key, (rx0, ry0, rx1, ry1, name) in ROOMS.items():
        zone.add_subzone(name, rx0, ry0, rx1 - rx0, ry1 - ry0)
    return zone, L


def finish(zone, L):
    targets = [PORTAL] + [(x, y) for (x, y) in BOSSES.values()] + list(CHESTS)
    return L.finish(targets)


def dress(zone, L):
    P = L.prop
    # ---- the gatehouse: the Syndicate's front door
    P("rf_brazier", 63, 106, 3)
    P("rf_brazier", 77, 106, 3)
    P("bbc_banner", 66, 99, 5)
    P("bbc_banner", 74, 99, 5)
    P("rf_supply_crates", 62, 101, 3)
    P("bbc_weapon_rack", 78, 101, 3)
    # ---- the bailey walk: a ring of wall-torches, rubble where the wall is failing
    for (x, y) in ((40, 20), (100, 20), (20, 58), (120, 58), (40, 96), (100, 96)):
        P("den_torch", x, y, 4)
    P("bbc_rubble", 46, 18, 3, solid="core")
    P("bbc_rubble", 94, 98, 3, solid="core")
    P("broken_column", 22, 46, 5)
    P("broken_column", 118, 70, 5)
    # ---- the kennels
    P("bbc_cage", 106, 84, 5)
    P("bbc_cage", 118, 84, 5)
    P("den_campfire_ashes", 112, 92, 2)
    P("bbc_skull_pile", 106, 94, 3)
    P("rf_supply_crates", 119, 94, 3)
    # ---- the magister's tower
    P("bbc_bookshelf", 20, 82, 6)
    P("bbc_bookshelf", 36, 82, 6)
    P("bbc_warlock_desk", 28, 94, 4)
    P("bbc_candelabra", 22, 92, 4)
    P("bbc_candelabra", 34, 92, 4)
    P("bbc_rune_pillar", 28, 80, 6, solid="core")
    # ---- the armoury
    P("bbc_weapon_rack", 20, 22, 3)
    P("bbc_weapon_rack", 36, 22, 3)
    P("rf_supply_crates", 22, 36, 3)
    P("vot_crate_stack", 34, 36, 3)
    P("rf_brazier", 28, 30, 3)
    # ---- the watch tower
    P("den_torch", 104, 22, 4)
    P("den_torch", 120, 22, 4)
    P("bbc_banner", 112, 20, 5)
    P("rf_supply_crates", 106, 36, 3)
    # ---- the inner keep: a courtyard open to the sky, long abandoned
    P("broken_column", 58, 68, 5)
    P("broken_column", 82, 68, 5)
    P("broken_column", 58, 80, 5)
    P("broken_column", 82, 80, 5)
    P("bbc_rubble", 70, 78, 3, solid="core")
    P("den_rock_rubble", 62, 70, 2)
    # ---- the Lord's Hall: the baron still holds court in a roofless room
    P("bbc_throne", 70, 46, 6)
    P("bbc_banner", 62, 45, 5)
    P("bbc_banner", 78, 45, 5)
    P("rf_brazier", 58, 56, 3)
    P("rf_brazier", 82, 56, 3)
    P("banquet_table", 70, 55, 4)
    # ---- the undercroft: what the Syndicate stopped going down to find
    P("bbc_skull_pile", 62, 30, 3)
    P("bbc_skull_pile", 78, 30, 3)
    P("bbc_chains", 60, 29, 5)
    P("bbc_chains", 80, 29, 5)
    P("den_torch", 70, 28, 4)
    P("cocoon_victim", 66, 36, 4)
    return zone, L


def generate_durnholde_keep():
    zone, L = build_durnholde()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_durnholde_baked():
    """(zone, layout) with props + QA done - what the baker paints from."""
    zone, L = build_durnholde()
    dress(zone, L)
    finish(zone, L)
    return zone, L
