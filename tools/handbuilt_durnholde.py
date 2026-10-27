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
                        ->  east or west BREACH, each knocked through a southern tower  ->  the courtyard
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
RING_W = 6                          # the bailey walk is a wall-walk, not a parade ground

#: EVERY shape in this file is an exact axis-aligned rect - no chamfer, no carved paths.
#:
#: Kyle, on Dun Garok: "it's a dwarf stronghold not a cave... I'm talking design." The same applies here and
#: harder, because Durnholde is a CASTLE. The first version used chamfered rooms and Builder.corridor(), and
#: corridor() runs ZoneGenerator._carve_path, which smears a soft diagonal line - so the keep baked with
#: rounded corners and feathered walls and read as caverns with a tidy floor. Masons do not round a corner
#: they did not mean to round. Rooms are rects, halls are rects, and rooms are joined by narrow punched
#: DOORWAYS, which is also what makes the breaches load-bearing instead of decorative.
#:
#: The keep's chambers sit WELL clear of the bailey walk, with three tiles of wall between each. An earlier
#: version let the Lord's Hall touch the north walk, which quietly connected the "sealed" keep straight to
#: the ring and made both breaches ornamental; sealing them and re-running the flood fill is what caught it.
ROOMS = {
    "gatehouse":  (60, 103, 80, 114, "The Gatehouse"),
    "armoury":    (26, 26, 46, 46, "The Armoury"),
    "watch":      (94, 26, 114, 46, "The Watch Tower"),
    "magister":   (26, 70, 46, 90, "The Magister's Tower"),
    "kennel":     (94, 70, 114, 90, "The Kennels"),
    "undercroft": (58, 24, 82, 36, "The Undercroft"),
    "hall":       (52, 40, 88, 58, "The Lord's Hall"),
    "keep":       (48, 62, 92, 88, "The Inner Keep"),
}

#: The bailey walk: four rects forming a closed ring just inside the curtain wall.
OUTER = (16, 14, 124, 102)
RING = [
    (16, 14, 124, 20),        # north walk
    (16, 96, 124, 102),       # south walk
    (16, 14, 22, 102),        # west walk
    (118, 14, 124, 102),      # east walk
]

#: Doorways and the two breaches - all rects. Each tower gets exactly ONE door, so it is a chamber you
#: clear rather than a stretch of corridor you pass through.
DOORS = {
    "gate_in":    (68, 102, 72, 103),    # gatehouse -> south walk
    "armoury_d":  (34, 20, 38, 26),      # armoury -> north walk
    "watch_d":    (102, 20, 106, 26),    # watch tower -> north walk
    "magister_d": (22, 78, 26, 82),      # magister's tower -> west walk
    "kennel_d":   (114, 78, 118, 82),    # kennels -> east walk
    "hall_down":  (68, 36, 72, 40),      # Lord's Hall -> the Undercroft stair
    "court_up":   (66, 58, 74, 62),      # courtyard -> the Lord's Hall
}
#: The only two ways through the curtain into the keep courtyard - and both of them run THROUGH a southern
#: tower (the breach bands overlap the Magister's Tower and the Kennels). That was not the original plan, but
#: it is a better castle: it makes those two bosses gates rather than optional side rooms, so getting into the
#: keep costs you a fight either way round the ring. Verified: seal one breach and the keep is still reachable
#: the other way; seal both and the courtyard, Perenolde and the Keepkeeper are all cut off.
BREACHES = {
    # Narrow. At 7 tiles tall these were bands, not holes: the courtyard, both southern towers and the
    # breaches merged into one open lower half, so the "sealed keep" had no visible edge at all even though
    # the flood fill still said it was sealed. A breach is a hole you squeeze through.
    "breach_e": (92, 72, 94, 74),
    "breach_w": (46, 72, 48, 74),
}

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

    # The bailey walk, then every room, then the doorways and breaches. All rects, no chamfer.
    for (x0, y0, x1, y1) in RING:
        b.rect(x0, y0, x1, y1)
    for key, (x0, y0, x1, y1, _n) in ROOMS.items():
        b.rect(x0, y0, x1, y1)
    for key, (x0, y0, x1, y1) in list(DOORS.items()) + list(BREACHES.items()):
        b.rect(x0, y0, x1, y1)

    # Pillars down the Lord's Hall - it should read as a hall, not a box.
    b.pillars([58, 82], [44, 52], size=2)

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.set_tile(px, py, "dirt", "base")
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    bosses = [(70, 108, "Sergeant-at-Arms Varth"),
              (104, 80, "Houndmaster Sable"),
              (36, 80, "Magister Yvaine"),
              (70, 30, "The Keepkeeper"),
              (70, 49, "Baron Aliden Perenolde")]
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
    for (x, y) in ((36, 36), (104, 36), (70, 80), (64, 30), (104, 86)):
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
