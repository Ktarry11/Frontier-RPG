"""
Hand-built Arathi caves - five of them, one per zone plus the two sea caves.

Kyle, 2026-11-01: "We can have 1 cave in each zone... we have an archipelago there as well full of
pirates and two sea caves."

ALL FIVE ARE SINGLE-BOSS, so trash is RANDOM (zone.fixed_spawns = False) with the boss and one rare
pinned. Hand-placed mobs are a full-dungeon thing only, per Kyle's standing rule; Stromgarde Keep and
Drywhisker Deeps are the dungeons and they live in their own modules.

LAYOUT VARIETY IS THE POINT (playbook section 4: "hand-crafted caves must not look similar"). Five caves
shipping together is the worst case for that, so each one gets a topology archetype nobody else in the
game is using, and they are listed here so the next person can see the set at a glance rather than
discovering the repetition on a minimap:

    Boulder'gor         DUMBBELL      two big halls, one long low crawl between them. Nothing else.
    Boulderfist Hall    HUB & SPOKES  a feast hall with four dens radiating off it at uneven angles.
    The Drowned Barrow  RIB-CAGE      one straight spine with burial niches ribbing off both sides,
                                      flooding as it descends - the far end is water.
    Wrackline Hold      TERRACES      a sea-level dock climbing in three shelves to the crew's quarters.
    The Tidewrack       ROTUNDA       one flooded round sump with an island in the middle of it.

None of those is a spiral, a C-warren, a gorge, a switchback or a ring, which is what the existing caves
already are.

HARD CONTRACTS (world/portal_manager.py) - arrival leaving a cave is the destination tile +3:
    Boulder'gor        (30, 46) <-> Arathi West    (44, 34)
    Boulderfist Hall   (32, 50) <-> Arathi Central (38, 40)
    The Drowned Barrow (30, 52) <-> Arathi East    (34, 38)
    Wrackline Hold     (28, 48) <-> Arathi East    (150, 60)
    The Tidewrack      (34, 50) <-> Arathi East    (160, 132)
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

GR = DP            # grotto_/den_/rf_/vot_ all live in dungeon_props
BAKED_ROOT = "assets/tiles/arathi_caves"


def _near_walkable(zone, x, y, rad=5):
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            if zone.is_walkable(int(x) + dx, int(y) + dy):
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, int(x) + dx, int(y) + dy)
    return None if best is None else (best[1], best[2])


def _carve(zone, spec):
    """Build the floor from a spec's PATHS and ROOMS, open the portal, pin bosses and chests."""
    L = CaveLayout(zone, (spec["PORTAL"][0], spec["PORTAL"][1] - 2))
    b = L.b
    for i, (pts, w0, w1) in enumerate(spec["PATHS"].values()):
        tube(b, pts, w0, w1, ph=0.5 + i * 0.9)
    for (cx, cy, rx, ry, rot, ph, _n) in spec["ROOMS"].values():
        cavern(b, cx, cy, rx, ry, rot, ph)

    px, py = spec["PORTAL"]
    zone.collision_layer[py][px] = None
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    fixed = []
    for (x, y, n) in spec["BOSSES"]:
        p = _near_walkable(zone, x, y)
        assert p, (zone.name, n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    zone.boss_position = (fixed[0][0], fixed[0][1])
    zone.boss_positions = list(fixed)
    spec["_bosses"] = {n: (x, y) for (x, y, n) in fixed}

    chests = []
    for (x, y) in spec["CHESTS"]:
        p = _near_walkable(zone, x, y)
        assert p, (zone.name, x, y)
        chests.append(p)
        L.mark("chest", *p)
    spec["_chests"] = chests

    zone.add_subzone(zone.name, 0, 0, spec["W"], spec["H"])   # cave table key first
    for (cx, cy, rx, ry, _rot, _ph, name) in spec["ROOMS"].values():
        zone.add_subzone(name, int(cx - rx - 2), int(cy - ry - 2), int(2 * rx + 4), int(2 * ry + 4))
    return L



def _place(L, name, x, y, height, rad=6, **kw):
    """Put a prop on the nearest tile that is actually floor AND clear of the pinned markers.

    Hand-written cave props are placed against a mental picture of the floorplan, and the floorplan is
    generated - a spine tube four tiles wide does not reach the x the author imagined, and a sarcophagus
    written at the same spot as a chest is refused for crowding it. The first build of these five caves
    skipped 22 props between them for exactly those two reasons, silently, leaving rooms bare.

    So: search outward for a tile that is walkable, is dry, and is further than `avoid` from every
    critical marker, and place there. Returns False only if nothing within `rad` qualifies, which is a
    real authoring error rather than a near miss.
    """
    z = L.z
    avoid = kw.get("avoid", 2)
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            nx, ny = int(x) + dx, int(y) + dy
            if not z.is_walkable(nx, ny):
                continue
            if z.base_layer[ny][nx] in ("shallow_water", "deep_water", "lava"):
                continue
            if any(max(abs(qx - nx), abs(qy - ny)) <= avoid for (qx, qy) in L.critical):
                continue
            d = dx * dx + dy * dy
            if best is None or d < best[0]:
                best = (d, nx, ny)
    if best is None:
        L.skipped.append((name, x, y, "no floor within radius"))
        return False
    return L.prop(name, best[1], best[2], height, **kw)


# =====================================================================================================
# BOULDER'GOR - DUMBBELL. Ogres, Arathi West's moor.
# Two halls and one crawl, and that is the whole cave. The crawl is deliberately long and narrow: an
# ogre hold where the two mobs cannot see each other is a place you can actually fight through, and the
# shape says "these two bands barely tolerate each other" without a line of dialogue.
# =====================================================================================================
BOULDERGOR = dict(
    W=66, H=52, PORTAL=(30, 46),
    PATHS={
        "mouth": ([(30, 46), (30, 42), (29, 39)], 5.0, 5.2),
        "crawl": ([(26, 33), (20, 30), (16, 25), (20, 20), (26, 17)], 3.4, 3.4),   # the long low squeeze
        "upper": ([(30, 17), (36, 15), (42, 14)], 4.4, 4.6),
    },
    ROOMS={
        "mouth":  (30, 44, 8.0, 4.5, 0, 0.4, "The Boulder Gate"),
        "lower":  (31, 32, 15.0, 7.0, 0, 1.2, "The Lower Hall"),
        "upper":  (46, 14, 14.0, 6.5, 0, 2.3, "The Chief's Hall"),
    },
    BOSSES=[(50, 13, "Gor'mok the Pit Chief"), (24, 34, "Gruln Stonejaw")],
    CHESTS=[(20, 35), (40, 30), (54, 17), (34, 11)],
    BAKED=f"{BAKED_ROOT}/bouldergor/baked",
    DESC="A two-hall ogre hold on the high moor, joined by a crawl neither band likes using.",
    REGION="Arathi Highlands",
)


def _dress_bouldergor(zone, L):
    P = lambda *a, **k: _place(L, *a, **k)   # noqa: E731 - snaps onto real floor
    # mouth: the toll they take off the Go'Shek road
    P("vot_broken_cart", 25, 45, 4)
    P("vot_crate_stack", 35, 45, 3)
    P("skull_pile", 33, 41, 2)
    # lower hall: Gruln's band, living rough
    P("vot_fire_pit", 31, 34, 3, solid="core")
    P("den_nest_mound", 22, 30, 5, solid="core", avoid=1)
    P("vot_hide_rack", 38, 29, 4)
    P("vot_beast_ribcage", 36, 35, 3)
    P("den_leg_bones", 27, 36, 2)
    P("den_stalagmites", 40, 33, 4, solid="core")
    # the crawl: low, wet, nothing in it but what has been dragged through
    P("den_stalactites", 18, 27, 3)
    P("den_leg_bones", 21, 21, 2)
    # the chief's hall: a seat, a hoard, and the banner of whoever they last killed
    P("bbc_throne", 50, 12, 6, solid="core", avoid=1)
    P("grotto_barrel_stack", 44, 17, 4)
    P("vot_crate_stack", 55, 15, 3)
    P("skull_pile", 46, 11, 2)
    P("den_stalagmite_pair", 58, 13, 4, solid="core")
    return zone, L


# =====================================================================================================
# BOULDERFIST HALL - HUB AND SPOKES. Ogres, Arathi Central's north ridge.
# The bigger hold, and a different shape on purpose: one feast hall with four dens off it at UNEVEN
# angles, so it reads as a warren that grew rather than a plan. You can clear the spokes in any order,
# which is the opposite of Boulder'gor's one-way squeeze.
# =====================================================================================================
BOULDERFIST = dict(
    W=74, H=64, PORTAL=(32, 50),
    PATHS={
        "mouth":  ([(32, 50), (33, 46), (34, 43)], 5.0, 5.2),
        "spoke_n": ([(36, 34), (38, 25), (36, 18)], 3.8, 4.2),
        "spoke_w": ([(28, 36), (18, 33), (11, 29)], 3.6, 4.0),
        "spoke_e": ([(45, 37), (55, 35), (63, 31)], 3.8, 4.2),
        "spoke_s": ([(40, 44), (48, 50), (54, 56)], 3.6, 3.8),
    },
    ROOMS={
        "mouth": (33, 48, 7.5, 4.2, 0, 0.5, "The Fist Gate"),
        "hall":  (36, 38, 16.0, 8.0, 0, 1.0, "The Feast Hall"),
        "north": (35, 15, 9.0, 6.0, 0, 1.9, "The Bone Den"),
        "west":  (8, 28, 8.5, 6.0, 0, 2.4, "The Scrap Den"),
        "east":  (67, 29, 9.0, 6.5, 0, 0.8, "The Chief's Den"),
        "south": (57, 58, 8.0, 5.0, 0, 3.1, "The Deep Larder"),
    },
    BOSSES=[(67, 28, "Boulderfist Hal'dun"), (35, 14, "Mauler Krakk")],
    CHESTS=[(28, 40), (8, 27), (34, 12), (58, 58), (62, 32)],
    BAKED=f"{BAKED_ROOT}/boulderfist/baked",
    DESC="The larger ogre hold: a feast hall with four dens off it, grown rather than planned.",
    REGION="Arathi Highlands",
)


def _dress_boulderfist(zone, L):
    P = lambda *a, **k: _place(L, *a, **k)   # noqa: E731 - snaps onto real floor
    P("vot_palisade", 28, 49, 4)
    P("skull_pile", 37, 48, 2)
    # the feast hall - the one room the whole hold shares
    P("banquet_table", 36, 39, 5, solid="core", avoid=1)
    P("vot_fire_pit", 30, 41, 3, solid="core")
    P("vot_beast_ribcage", 44, 40, 3)
    P("den_leg_bones", 25, 37, 2)
    P("vot_hide_rack", 46, 34, 4)
    P("den_clay_pillar", 22, 42, 6, solid="core")
    P("den_clay_pillar", 50, 42, 6, solid="core")
    # north: bones, because this is where they put what is left
    P("den_nest_mound", 33, 16, 5, solid="core", avoid=1)
    P("skull_pile", 38, 17, 2)
    P("vot_beast_ribcage", 31, 12, 3)
    # west: scrap robbed off the ring road
    P("vot_broken_cart", 10, 30, 4)
    P("grotto_barrel_stack", 5, 26, 4)
    P("vot_crate_stack", 12, 25, 3)
    # east: the chief
    P("bbc_throne", 67, 27, 6, solid="core", avoid=1)
    P("vot_crate_stack", 61, 31, 3)
    P("den_stalagmites", 71, 32, 4, solid="core")
    # south: the larder, which is not a nice room
    P("vot_hide_rack", 54, 57, 4)
    P("den_leg_bones", 59, 60, 2)
    P("grotto_shackle_frame", 60, 55, 5, solid="core")
    return zone, L


# =====================================================================================================
# THE DROWNED BARROW - RIB-CAGE SPINE. Arathi East's last highland.
# One straight passage with burial niches ribbing off both sides, and it DESCENDS: the niches get wetter
# the further in you go and the last third of the spine is standing water. An Arathor barrow dug into a
# hill that is now below the waterline, which is the zone's whole idea expressed as a floorplan.
# =====================================================================================================
BARROW = dict(
    W=58, H=70, PORTAL=(30, 52),
    PATHS={
        "mouth": ([(30, 52), (30, 48), (29, 45)], 4.6, 4.6),
        "spine": ([(29, 45), (29, 36), (28, 26), (28, 16), (28, 9)], 4.4, 5.6),
        "rib_a": ([(29, 41), (22, 40)], 3.0, 3.4),
        "rib_b": ([(29, 41), (36, 40)], 3.0, 3.4),
        "rib_c": ([(29, 31), (20, 30)], 3.0, 3.4),
        "rib_d": ([(29, 31), (38, 30)], 3.0, 3.4),
        "rib_e": ([(28, 21), (19, 20)], 3.0, 3.4),
        "rib_f": ([(28, 21), (37, 20)], 3.0, 3.4),
    },
    ROOMS={
        "mouth": (30, 50, 6.5, 4.0, 0, 0.6, "The Barrow Mouth"),
        "n_a":   (19, 40, 4.5, 3.6, 0, 1.4, "The First Niches"),
        "n_b":   (39, 40, 4.5, 3.6, 0, 2.2, "The Second Niches"),
        "n_c":   (17, 30, 4.5, 3.6, 0, 0.9, "The Flooded Niches"),
        "n_d":   (41, 30, 4.5, 3.6, 0, 2.8, "The Silted Niches"),
        "n_e":   (16, 20, 4.5, 3.6, 0, 1.7, "The Drowned Niches"),
        "n_f":   (40, 20, 4.5, 3.6, 0, 3.3, "The Last Niches"),
        "head":  (28, 8, 13.0, 7.0, 0, 2.0, "The Barrow Head"),
    },
    BOSSES=[(28, 7, "The Barrow Warden"), (16, 20, "Thane Aldric's Shade")],
    CHESTS=[(19, 40), (41, 30), (40, 20), (33, 6), (22, 9)],
    BAKED=f"{BAKED_ROOT}/barrow/baked",
    DESC="An Arathor barrow dug into a hill that is now below the waterline. The far end is water.",
    REGION="Arathi Highlands",
)


def _dress_barrow(zone, L):
    P = lambda *a, **k: _place(L, *a, **k)   # noqa: E731 - snaps onto real floor
    P("gothic_gate", 30, 49, 6, solid="core", avoid=1)
    P("broken_column", 25, 51, 5, solid="core")
    # the ribs: a sarcophagus in each, getting worse as you go in
    for (x, y) in ((19, 40), (39, 40), (17, 30), (41, 30), (16, 21), (40, 21)):
        P("sarcophagus", x, y, 4, solid="core", avoid=1)
    P("temple_column", 24, 36, 6, solid="core")
    P("temple_column", 34, 36, 6, solid="core")
    P("skull_pile", 31, 34, 2)
    P("den_stalactites", 27, 28, 3)
    # the wet end
    P("grotto_kelp_stalks", 25, 18, 3)
    P("grotto_tide_pool", 32, 17, 3)
    P("grotto_barnacle_pillar", 22, 14, 6, solid="core")
    # the head: the thane's own chamber
    P("sarcophagus", 28, 7, 5, solid="core", avoid=1)
    P("spirit_brazier", 22, 10, 4, solid="core")
    P("spirit_brazier", 34, 10, 4, solid="core")
    P("broken_column", 19, 7, 5, solid="core")
    P("broken_column", 37, 7, 5, solid="core")
    return zone, L


# =====================================================================================================
# WRACKLINE HOLD - TERRACES. The crew's sea cave, under Gallowmast Isle.
# Three shelves rising from a water-level dock to the quarters at the top, joined by ramps at ALTERNATING
# ends so you switch back on yourself each time. A smuggler's cave is organised by what the tide can
# reach: boats at the bottom, cargo on the middle shelf, people above the high-water mark.
# =====================================================================================================
WRACKLINE = dict(
    W=70, H=56, PORTAL=(28, 48),
    PATHS={
        "mouth": ([(28, 48), (28, 45), (28, 42)], 5.2, 5.4),
        "ramp1": ([(44, 40), (52, 36), (56, 31)], 4.0, 4.2),     # east end, up to the cargo shelf
        "ramp2": ([(22, 29), (14, 25), (12, 19)], 4.0, 4.2),     # west end, up to the quarters
    },
    ROOMS={
        "dock":   (28, 41, 18.0, 6.0, 0, 0.7, "The Boat Floor"),
        "cargo":  (36, 28, 20.0, 6.5, 0, 1.6, "The Cargo Shelf"),
        "crew":   (30, 14, 17.0, 6.5, 0, 2.5, "The Crew's Shelf"),
    },
    BOSSES=[(30, 13, "Captain Mory Vane"), (56, 29, "Ledger-Keeper Ashkin")],
    CHESTS=[(16, 42), (44, 40), (20, 27), (50, 27), (38, 13)],
    BAKED=f"{BAKED_ROOT}/wrackline/baked",
    DESC="A sea cave in three shelves: boats at the tideline, cargo above it, the crew above that.",
    REGION="Arathi Highlands",
)


def _dress_wrackline(zone, L):
    P = lambda *a, **k: _place(L, *a, **k)   # noqa: E731 - snaps onto real floor
    # the boat floor - what the tide reaches
    P("grotto_ship_bow", 18, 43, 7, solid="core", avoid=1)
    P("grotto_anchor", 36, 43, 4)
    P("grotto_fishing_net", 24, 44, 4)
    P("grotto_tide_pool", 32, 44, 3)
    P("grotto_barnacle_pillar", 14, 39, 6, solid="core")
    P("grotto_crab_nest", 40, 44, 3)
    # the cargo shelf - the whole reason the hold exists
    P("grotto_barrel_stack", 26, 29, 4)
    P("grotto_barrel_stack", 46, 29, 4)
    P("vot_crate_stack", 34, 30, 3)
    P("vot_crate_stack", 40, 26, 3)
    P("grotto_ship_cannon", 52, 29, 5, solid="core")
    P("grotto_shackle_frame", 20, 25, 5, solid="core")
    # the crew's shelf - above the high-water mark, and the only dry room
    P("grotto_ship_wheel", 30, 12, 5, solid="core", avoid=1)
    P("grotto_treasure_chest", 22, 15, 4)
    P("bbc_warlock_desk", 38, 15, 4, solid="core")
    P("grotto_pirate_skeletons", 26, 17, 3)
    P("den_torch", 18, 13, 4)
    P("den_torch", 42, 13, 4)
    return zone, L


# =====================================================================================================
# THE TIDEWRACK - ROTUNDA. The second sea cave, on the southern rocks.
# One round flooded sump with an ISLAND in the middle of it and a shelf running most of the way round
# the wall. Nothing else - no side rooms, no branches. You can see the boss from the doorway and the
# whole fight is the walk round to it, which no other cave in the game does.
# =====================================================================================================
TIDEWRACK = dict(
    W=62, H=58, PORTAL=(34, 50),
    PATHS={
        "mouth": ([(34, 50), (33, 47), (32, 44)], 5.0, 5.0),
        "ring_w": ([(28, 42), (16, 36), (12, 26), (18, 16), (28, 11)], 4.2, 4.2),
        "ring_e": ([(36, 42), (48, 36), (52, 26), (46, 16), (36, 11)], 4.2, 4.2),
        # MUST overlap the sump disc, not stop at its rim. At (32,18) it ended one row short and
        # the island was a sealed pocket of floor with the boss standing on it.
        "causeway": ([(32, 10), (32, 22)], 3.4, 3.4),         # the only way onto the island
    },
    ROOMS={
        "mouth":  (33, 48, 6.5, 3.8, 0, 0.5, "The Tide Gate"),
        "sump":   (32, 27, 9.0, 8.0, 0, 1.3, "The Sump"),
        "north":  (32, 10, 11.0, 4.5, 0, 2.1, "The North Shelf"),
    },
    BOSSES=[(32, 24, "The Wrack-Drowned"), (12, 26, "Brinemaw")],
    CHESTS=[(32, 25), (12, 25), (52, 26), (28, 9)],
    BAKED=f"{BAKED_ROOT}/tidewrack/baked",
    DESC="A round flooded sump with an island in the middle and a shelf round the wall.",
    REGION="Arathi Highlands",
)


def _dress_tidewrack(zone, L):
    P = lambda *a, **k: _place(L, *a, **k)   # noqa: E731 - snaps onto real floor
    P("grotto_barnacle_pillar", 29, 49, 6, solid="core")
    P("grotto_crab_molt", 37, 49, 3)
    # the island in the sump - everything the tide has brought in, piled on the one dry spot
    P("grotto_serpent_skeleton", 32, 23, 6, solid="core", avoid=1)
    P("grotto_shell_altar", 28, 26, 4, solid="core")
    P("grotto_pirate_skeletons", 36, 27, 3)
    # the shelf, round the wall
    P("grotto_kelp_stalks", 16, 34, 3)
    P("grotto_kelp_stalks", 48, 34, 3)
    P("grotto_giant_clam", 14, 28, 4)
    P("grotto_tide_pool", 50, 28, 3)
    P("grotto_glow_coral", 18, 18, 3)
    P("grotto_glow_coral", 46, 18, 3)
    P("grotto_crab_nest", 52, 24, 3)
    # the north shelf
    P("grotto_treasure_chest", 28, 9, 4)
    P("grotto_anchor", 38, 10, 4)
    P("glow_coral_cluster", 32, 8, 3)
    return zone, L


# =====================================================================================================
SPECS = [
    ("Boulder'gor", BOULDERGOR, _dress_bouldergor),
    ("Boulderfist Hall", BOULDERFIST, _dress_boulderfist),
    ("The Drowned Barrow", BARROW, _dress_barrow),
    ("Wrackline Hold", WRACKLINE, _dress_wrackline),
    ("The Tidewrack", TIDEWRACK, _dress_tidewrack),
]


def _build(name, spec, dresser, baked=True):
    zone = Tilemap(name, spec["W"], spec["H"], spec["DESC"])
    zone.is_cave = True
    zone.region = spec["REGION"]
    zone.fixed_spawns = False           # single boss => random trash, boss and rare pinned
    L = _carve(zone, spec)
    dresser(zone, L)
    targets = [spec["PORTAL"]] + list(spec["_bosses"].values()) + list(spec["_chests"])
    L.finish(targets)
    if baked:
        register_baked(zone, spec["BAKED"])
    return zone, L


def generate_bouldergor():
    return _build("Boulder'gor", BOULDERGOR, _dress_bouldergor)[0]


def generate_boulderfist_hall():
    return _build("Boulderfist Hall", BOULDERFIST, _dress_boulderfist)[0]


def generate_drowned_barrow():
    return _build("The Drowned Barrow", BARROW, _dress_barrow)[0]


def generate_wrackline_hold():
    return _build("Wrackline Hold", WRACKLINE, _dress_wrackline)[0]


def generate_tidewrack():
    return _build("The Tidewrack", TIDEWRACK, _dress_tidewrack)[0]


def build_all_baked():
    """[(zone, layout, spec)] with props + QA done - what the baker paints from."""
    return [(*_build(n, s, d, baked=False), s) for (n, s, d) in SPECS]


if __name__ == "__main__":
    for (n, s, d) in SPECS:
        z, L = _build(n, s, d, baked=False)
        walk = sum(1 for y in range(s["H"]) for x in range(s["W"]) if z.is_walkable(x, y))
        print(f"{n:22s} {s['W']}x{s['H']}  {walk:5d} walkable  "
              f"{len(s['_bosses'])} pinned  {len(s['_chests'])} chests  skipped props: {len(L.skipped)}")
        for sk in L.skipped:
            print("     skipped:", sk)
