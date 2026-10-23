"""
Hand-built Boulder Lode Mine (100x80): the Venture Co. claim cut into the Northern Barrens' east cliffs.

ARCHETYPE: THE SWITCHBACK TERRACES.  Not a spiral, wheel, river loop, rotunda or C-warren.  The mine is cut
into the hillside as three long E-W benches stacked like stair treads; a haulage ramp joins each pair of
benches at ALTERNATING ENDS (east, west, east), so the way up is a zig-zag you walk the full length of every
tread to reach.  A crystal vein chamber caps the climb.  Two short side adits hang off the middle benches
(the rare's claim and a collapsed gallery); the bottom tread has a pillar of rock left standing mid-hall, so
the lower gallery loops round it instead of being one corridor.

  Adit mouth (50,76) -> LOWER GALLERY (y~66, W<->E, pillar island) -> haulage ramp E ->
  TIMBERED GALLERY (y~51, E->W; side adit N: Delvik's Claim) -> ramp W ->
  UPPER GALLERY (y~35, W->E; side adit N: collapsed gallery) -> ramp E -> VEIN CHAMBER (y~14, Foreman Grills)

Single-boss cave => TRASH IS RANDOM (zone.fixed_spawns = False; encounters.json caves["Boulder Lode Mine"]).
Boss: Foreman Grills (vein chamber).  Pinned rare: Prospector Delvik (Delvik's Claim).

HARD CONTRACTS (world/portal_manager.py): portal (50,76) <-> Northern Barrens (255,45); arrival = 2 north.
Prop rule (Kyle): less is more; logical for the room; a few centrepieces.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

GP = "assets/tiles/goblin_shared/props/"          # gob_* Venture Co. props
BAKED = "assets/tiles/boulder_lode_mine/baked"
W, H = 100, 80
PORTAL = (50, 76)

# ---- the galleries (control points; ramps join benches at alternating ends) --------------------------------
PATHS = {
    "adit":     ([(50, 76), (50, 72), (50, 68)], 5.0, 6.0),
    "lower":    ([(12, 66), (26, 68), (40, 66), (56, 68), (72, 66), (88, 67)], 6.0, 6.0),
    "ramp_e1":  ([(88, 67), (92, 59), (89, 52)], 5.0, 5.0),
    "timber":   ([(88, 51), (74, 53), (58, 50), (42, 52), (26, 50), (12, 51)], 6.0, 6.0),
    "ramp_w2":  ([(12, 51), (8, 43), (11, 36)], 5.0, 5.0),
    "upper":    ([(12, 35), (28, 37), (44, 34), (60, 36), (76, 34), (88, 35)], 6.0, 6.0),
    "ramp_e3":  ([(88, 35), (92, 28), (86, 22)], 5.0, 5.0),
    "to_vein":  ([(86, 22), (76, 17), (66, 14)], 5.0, 6.0),
    "claim":    ([(31, 49), (30, 46), (29, 44)], 3.0, 3.0),          # adit N of the timbered gallery
    "collapse": ([(62, 33), (62, 30), (62, 28)], 3.0, 3.0),          # adit N of the upper gallery
}
# ---- chambers: (cx, cy, rx, ry, rot, phase, display name) ---------------------------------------------------
ROOMS = {
    "mouth":    (50, 73, 11, 4, 0, 0.4, "The Adit"),
    "lower":    (46, 66, 14, 6.5, 0, 1.1, "The Lower Gallery"),
    "timber":   (50, 51, 40, 3.6, 0, 2.0, "The Timbered Gallery"),
    "upper":    (50, 35, 40, 3.6, 0, 2.7, "The Upper Gallery"),
    "claim":    (29, 43, 7, 2.5, 0, 0.8, "Delvik's Claim"),
    "collapse": (62, 26, 8, 2.6, 0, 1.4, "The Collapsed Gallery"),
    "vein":     (52, 13, 19, 9, 0, 0.9, "The Crystal Vein"),
}
PILLAR = (46, 66, 5.0, 2.2)        # the rock island left standing in the lower gallery (cx, cy, rx, ry)

BOSSES = {}
CHESTS = []


def _near_walkable(zone, x, y, rad=4):
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            if zone.is_walkable(int(x) + dx, int(y) + dy):
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, int(x) + dx, int(y) + dy)
    return None if best is None else (best[1], best[2])


def build_boulder_lode():
    zone = Tilemap("Boulder Lode Mine", W, H,
                   "A Venture Co. claim cut into the hillside in stepped galleries, climbing toward a rich crystal vein.")
    zone.is_cave = True
    zone.region = "Northern Barrens"
    zone.fixed_spawns = False
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b

    for i, (key, (pts, w0, w1)) in enumerate(PATHS.items()):
        tube(b, pts, w0, w1, ph=0.5 + i * 0.9)
    for key, (cx, cy, rx, ry, rot, ph, _n) in ROOMS.items():
        cavern(b, cx, cy, rx, ry, rot, ph)
    # the pillar: put the rock back (a wall island the lower gallery loops round)
    px_, py_, prx, pry = PILLAR
    for y in range(int(py_ - pry) - 1, int(py_ + pry) + 2):
        for x in range(int(px_ - prx) - 1, int(px_ + prx) + 2):
            if ((x - px_) / prx) ** 2 + ((y - py_) / pry) ** 2 <= 1.0:
                zone.collision_layer[y][x] = "wall"
                zone.set_tile(x, y, "rock", "collision")

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    bosses = [(52, 12, "Foreman Grills"), (29, 43, "Prospector Delvik")]
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
    for (x, y) in ((66, 26), (14, 66), (88, 35), (36, 14)):
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        chests.append(p)
    CHESTS[:] = chests
    for c in chests:
        L.mark("chest", *c)

    def sub(name, x, y, rx, ry):
        zone.add_subzone(name, int(x - rx), int(y - ry), int(2 * rx), int(2 * ry))
    for key, (cx, cy, rx, ry, rot, ph, name) in ROOMS.items():
        sub(name, cx, cy, rx + 2, ry + 2)
    zone.add_subzone("Boulder Lode Mine", 0, 0, W, H)      # the cave table key covers the whole map (registered first,
    # named rooms above stay for display only; later registration wins, so re-register rooms after)
    for key, (cx, cy, rx, ry, rot, ph, name) in ROOMS.items():
        sub(name, cx, cy, rx + 2, ry + 2)
    return zone, L


def finish(zone, L):
    targets = [PORTAL] + [(x, y) for (x, y) in BOSSES.values()] + list(CHESTS)
    return L.finish(targets)


def dress(zone, L):
    P = L.prop
    R = ROOMS
    # ---- adit mouth: braziers frame the door, one cart left where the shift stopped
    P("rf_brazier", 44, 73, 3)
    P("rf_brazier", 56, 73, 3)
    P("gob_ore_cart", 41, 71, 4, where=GP)
    P("vot_crate_stack", 59, 71, 3)
    P("gob_mine_frame", 50, 73, 8, where=GP, solid=False)          # the adit's timber frame over the door
    # ---- lower gallery: the tool-and-haulage hall
    P("gob_ore_cart", 20, 66, 4, where=GP)
    P("rf_tool_rack", 30, 69, 3)
    P("rf_supply_crates", 66, 69, 3)
    P("gob_rail_stack", 33, 63, 3, where=GP, solid=False)
    P("gob_ore_cart", 80, 67, 4, where=GP)
    P("den_rock_rubble", 56, 63, 2)
    P("den_torch", 14, 63, 4)
    P("den_torch", 86, 64, 4)
    # ---- haulage ramp east: a spilled cart
    P("gob_ore_cart", 91, 57, 4, where=GP)
    # ---- timbered gallery: crew quarters
    P("rf_supply_crates", 78, 52, 3)
    P("vot_crate_stack", 64, 52, 3)
    P("rf_tool_rack", 52, 52, 3)
    P("rf_brazier", 40, 50, 3)
    P("den_rock_rubble", 24, 52, 2)
    P("den_torch", 80, 50, 4)
    P("den_torch", 16, 49, 4)
    # ---- Delvik's claim: a prospector's lone camp
    cx, cy = R["claim"][:2]
    P("rf_supply_crates", cx + 4, cy + 1, 3)
    P("rf_tool_rack", cx - 4, cy + 1, 3)
    P("den_rock_rubble", cx - 5, cy - 1, 2)
    P("den_backpack", cx + 2, cy - 1, 2)
    P("gob_claim_marker", cx, cy + 3, 6, where=GP)
    P("gob_dynamite_crate", cx + 6, cy + 1, 3, where=GP)
    # ---- ramp west
    P("gob_ore_cart", 10, 45, 4, where=GP)
    # ---- upper gallery: the face being worked
    P("rf_tool_rack", 20, 36, 3)
    P("gob_ore_cart", 50, 36, 4, where=GP)
    P("rf_supply_crates", 82, 36, 3)
    P("rf_brazier", 36, 33, 3)
    P("rf_brazier", 72, 33, 3)
    P("den_stalagmites", 56, 33, 4, solid="core")
    # ---- collapsed gallery: the cave-in
    qx, qy = R["collapse"][:2]
    P("den_rock_rubble", qx - 5, qy, 3, solid="core")
    P("den_rock_rubble", qx + 3, qy + 1, 3, solid="core")
    P("gob_ore_cart", qx - 1, qy + 2, 4, where=GP)
    P("den_stalagmite_pair", qx + 6, qy, 4, solid="core")
    P("gob_ore_pile", qx - 8, qy, 3, where=GP)
    # ---- ramp east to the vein
    P("rf_brazier", 80, 18, 3)
    # ---- crystal vein chamber: the foreman's workshop round the vein
    vx, vy = R["vein"][:2]
    P("rf_void_crystals", vx - 9, vy - 2, 5, solid="core")
    P("rf_void_crystals", vx + 10, vy - 3, 5, solid="core")
    P("rf_void_crystals", vx, vy - 6, 6, solid="core", avoid=1)
    P("rf_brazier", vx - 5, vy + 5, 3)
    P("rf_brazier", vx + 6, vy + 5, 3)
    P("gob_ore_cart", vx - 12, vy + 4, 4, where=GP)
    P("rf_supply_crates", vx + 13, vy + 3, 3)
    P("rf_tool_rack", vx + 3, vy + 6, 3)
    return zone, L


def generate_boulder_lode_mine():
    zone, L = build_boulder_lode()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_boulder_lode_baked():
    """(zone, layout) with props + QA done - what the baker paints from."""
    zone, L = build_boulder_lode()
    dress(zone, L)
    finish(zone, L)
    return zone, L
