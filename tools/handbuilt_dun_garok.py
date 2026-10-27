"""
Hand-built Dun Garok (110x100): the Stormpike dwarves' fort cut into Hillsbrad's southern ridge, levels 25-28.

ARCHETYPE: THE GAUNTLET OF GATES.  Not Azurelode's drowned islands, not Durnholde's ring, not Boulder Lode's
switchback benches, not a wheel, spiral, ladder, hive, rotunda or C-warren.  Dun Garok is a FORT, and a fort
built into a mountainside is a sequence of things you have to get through: the approach narrows into the Outer
Gate, opens into the Muster Yard, narrows again at the Inner Gate, opens into the Great Hall, and narrows a
third time at the Vault Door before the Crypt.  Wide, narrow, wide, narrow - the rhythm IS the layout, and it
reads nothing like a cave because the dwarves cut it square.

The one mercy is the SALLY PORT: a cramped side tunnel running up the east wall from the Muster Yard into the
Barracks, built so the garrison could get out behind an attacker.  It bypasses the Inner Gate - and only the
Inner Gate - so the fort has exactly one flank and the other two chokepoints are mandatory. That asymmetry is
deliberate; a gauntlet with no way round is a corridor, and a gauntlet you can skip entirely is not a gauntlet.

    Approach (55,96) -> THE OUTER GATE (Gatewarden Brannic) -> THE MUSTER YARD
                     -> THE INNER GATE -> THE GREAT HALL -> THE VAULT DOOR (Shrine-Keeper Morgrin)
                     -> THE CRYPT OF DUN GAROK (Thane Korrin Stonewatch)
    and the sally port: Muster Yard --east wall--> THE BARRACKS (Rifle-Sergeant Dunmar), skipping the Inner Gate.

A fort, not a Dungeon: it stays OFF world/zone_classification.DUNGEONS, so it inherits Eastern Hillsbrad's ore
the way a mountain hold should (Kyle: "caves (and keeps) are fine, just not dungeons").

Four bosses, pinned; trash is random from the table (zone.fixed_spawns = False).

HARD CONTRACTS (world/portal_manager.py): portal (55,96) <-> Eastern Hillsbrad (95,139); arrival = 2 north.
Prop rule (Kyle): less is more; logical for the room; a few centrepieces.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401

BAKED = "assets/tiles/dun_garok/baked"
W, H = 110, 100
PORTAL = (55, 96)

#: Rooms: (x0, y0, x1, y1, display name). EXACT rectangles - no chamfer anywhere.
#:
#: Kyle: "Dun garok is a dwarf stronghold not a cave... I'm talking design." The first version carved these
#: with chamfered corners and Builder.corridor(), and corridor() runs ZoneGenerator._carve_path, which smears
#: a diagonal-ish line and leaves soft organic edges. The result read as a set of caverns someone had tidied
#: up. Dwarves do not tidy up a cavern - they cut the hold square. So every room and every hallway here is a
#: plain axis-aligned rect, the walls between rooms are deliberate thickness, and the rooms are joined by
#: narrow DOORWAYS rather than by touching.
ROOMS = {
    "outer_gate": (44, 78, 66, 87, "The Outer Gate"),
    "muster":     (26, 56, 84, 75, "The Muster Yard"),
    "inner_gate": (48, 46, 62, 54, "The Inner Gate"),
    "great_hall": (26, 26, 64, 44, "The Great Hall"),
    "barracks":   (68, 28, 96, 47, "The Barracks"),
    "vault_door": (40, 16, 56, 24, "The Vault Door"),
    "crypt":      (24, 4, 70, 14, "The Crypt of Dun Garok"),
}

#: Hallways and doorways, also exact rects. A doorway is a gap of solid wall with a narrow rect punched
#: through it, which is what makes the three gates real chokepoints instead of two rooms that happen to abut.
HALLS = {
    "approach":   (53, 88, 57, 97),      # the cut in from the ridge face
    "gate1_door": (53, 76, 57, 77),      # Outer Gate -> Muster Yard
    "gate2_door": (53, 55, 57, 55),      # Muster Yard -> Inner Gate
    "gate2_out":  (53, 45, 57, 45),      # Inner Gate -> Great Hall
    "hall_barr":  (65, 34, 67, 38),      # Great Hall -> Barracks
    "vault_in":   (46, 25, 50, 25),      # Great Hall -> Vault Door
    "vault_out":  (46, 15, 50, 15),      # Vault Door -> the Crypt
    # The sally port: a cramped service passage up the east wall into the Barracks, skipping the Inner Gate.
    "sally_h1":   (84, 62, 91, 64),
    "sally_v":    (88, 44, 91, 64),
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


def build_dun_garok():
    zone = Tilemap("Dun Garok", W, H,
                   "A dwarven hold cut square into the ridge: three gates, a muster yard, and a crypt the "
                   "Stormpike do not talk about.")
    zone.is_cave = True
    zone.region = "Hillsbrad Foothills"
    zone.fixed_spawns = False
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b

    # Dwarves cut square. Rooms and halls are both plain rects, no chamfer, no carved paths.
    for key, (x0, y0, x1, y1, _n) in ROOMS.items():
        b.rect(x0, y0, x1, y1)
    for key, (x0, y0, x1, y1) in HALLS.items():
        b.rect(x0, y0, x1, y1)

    # Pillars down the Great Hall and the Muster Yard - these are halls, not boxes.
    b.pillars([34, 56], [31, 39], size=2)
    b.pillars([36, 54, 72], [61, 69], size=2)

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.set_tile(px, py, "dirt", "base")
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    bosses = [(55, 83, "Gatewarden Brannic"),
              (82, 37, "Rifle-Sergeant Dunmar"),
              (48, 20, "Shrine-Keeper Morgrin"),
              (47, 9, "Thane Korrin Stonewatch")]
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
    for (x, y) in ((30, 60), (90, 34), (30, 30), (64, 8), (80, 70)):
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        chests.append(p)
    CHESTS[:] = chests
    for c in chests:
        L.mark("chest", *c)

    zone.add_subzone("Dun Garok", 0, 0, W, H)              # the encounter-table key covers the whole map
    for key, (x0, y0, x1, y1, name) in ROOMS.items():
        zone.add_subzone(name, x0, y0, x1 - x0, y1 - y0)   # later registration wins, so rooms are display names
    return zone, L


def finish(zone, L):
    targets = [PORTAL] + [(x, y) for (x, y) in BOSSES.values()] + list(CHESTS)
    return L.finish(targets)


def dress(zone, L):
    P = L.prop
    # ---- the approach and the Outer Gate: the first thing that says turn back
    P("rf_brazier", 50, 86, 3)
    P("rf_brazier", 60, 86, 3)
    P("bbc_weapon_rack", 46, 81, 3)
    P("bbc_weapon_rack", 64, 81, 3)
    P("den_torch", 55, 90, 4)
    P("bbc_rubble", 48, 87, 3, solid="core")
    # ---- the Muster Yard: where the garrison formed up
    P("rf_supply_crates", 30, 60, 3)
    P("rf_supply_crates", 78, 60, 3)
    P("bbc_weapon_rack", 44, 59, 3)
    P("bbc_weapon_rack", 62, 59, 3)
    P("den_campfire_ashes", 55, 66, 2)
    P("vot_crate_stack", 32, 72, 3)
    P("den_torch", 28, 58, 4)
    P("den_torch", 82, 58, 4)
    P("bbc_banner", 48, 57, 5)
    P("bbc_banner", 62, 57, 5)
    # ---- the Inner Gate: a throat, held
    P("rf_brazier", 50, 54, 3)
    P("rf_brazier", 60, 54, 3)
    P("bbc_chains", 52, 48, 5)
    # ---- the sally port: cramped, and nobody has swept it in years
    P("den_rock_rubble", 92, 56, 2)
    P("den_torch", 92, 50, 4)
    P("den_backpack", 92, 60, 2)
    # ---- the Barracks: bunks, a rifle rack, cold stove
    P("bbc_weapon_rack", 72, 32, 3)
    P("bbc_weapon_rack", 92, 32, 3)
    P("rf_supply_crates", 74, 44, 3)
    P("den_campfire_ashes", 82, 40, 2)
    P("banquet_table", 82, 34, 4)
    P("den_torch", 70, 30, 4)
    P("den_torch", 94, 30, 4)
    # ---- the Great Hall: the hold proper
    P("bbc_throne", 45, 30, 6)
    P("bbc_banner", 38, 29, 5)
    P("bbc_banner", 52, 29, 5)
    P("rf_brazier", 32, 42, 3)
    P("rf_brazier", 58, 42, 3)
    P("broken_column", 30, 36, 5)
    P("broken_column", 60, 36, 5)
    # ---- the Vault Door: the shrine-keeper's post
    P("bbc_candelabra", 44, 22, 4)
    P("bbc_candelabra", 52, 22, 4)
    P("bbc_rune_pillar", 48, 18, 6, solid="core")
    P("bbc_idol", 48, 25, 5)
    # ---- the Crypt: the thing the Stormpike do not talk about
    P("bbc_skull_pile", 32, 10, 3)
    P("bbc_skull_pile", 62, 10, 3)
    P("bbc_chains", 28, 7, 5)
    P("bbc_chains", 66, 7, 5)
    P("den_torch", 47, 6, 4)
    P("cocoon_victim", 38, 14, 4)
    P("bbc_rubble", 56, 14, 3, solid="core")
    return zone, L


def generate_dun_garok():
    zone, L = build_dun_garok()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_dun_garok_baked():
    """(zone, layout) with props + QA done - what the baker paints from."""
    zone, L = build_dun_garok()
    dress(zone, L)
    finish(zone, L)
    return zone, L
