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
    # ROOMS are a LIST OF LOBES each, not one ellipse. Kyle, 2026-11-01: "These caves are very boring.
    # Put more effort into them if you can bro" - and he was right: the first build had five distinct
    # OUTLINES and five identical insides, because every room was one smooth oval joined to the next by
    # one smooth tube. Nothing to walk round, nothing to find, no rhythm. Unioned lobes give a room
    # corners, bays and a long axis; ALCOVES below give it pockets; PILLARS give it something to fight
    # around.
    for lobes in spec["ROOMS"].values():
        for (cx, cy, rx, ry, rot, ph) in lobes[0]:
            cavern(b, cx, cy, rx, ry, rot, ph)
    for (cx, cy, rx, ry, rot, ph) in spec.get("ALCOVES", ()):
        cavern(b, cx, cy, rx, ry, rot, ph)

    # PILLARS are carved back to rock AFTER the floor exists - roof supports, rock islands and spines
    # that split a room into routes. A hall you cross in a straight line is a corridor with a big name.
    for (cx, cy, rx, ry, rot) in spec.get("PILLARS", ()):
        import math as _m
        c, s_ = _m.cos(_m.radians(rot)), _m.sin(_m.radians(rot))
        R = int(max(rx, ry)) + 2
        for yy in range(int(cy) - R, int(cy) + R + 1):
            for xx in range(int(cx) - R, int(cx) + R + 1):
                if not (0 <= xx < spec["W"] and 0 <= yy < spec["H"]):
                    continue
                dx, dy = xx - cx, yy - cy
                u, v = (c * dx + s_ * dy) / rx, (-s_ * dx + c * dy) / ry
                if u * u + v * v <= 1.0:
                    zone.collision_layer[yy][xx] = "wall"
                    zone.set_tile(xx, yy, "rock", "collision")

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
    for (lobes, name) in spec["ROOMS"].values():
        x0 = min(cx - rx for (cx, cy, rx, ry, _r, _p) in lobes)
        x1 = max(cx + rx for (cx, cy, rx, ry, _r, _p) in lobes)
        y0 = min(cy - ry for (cx, cy, rx, ry, _r, _p) in lobes)
        y1 = max(cy + ry for (cx, cy, rx, ry, _r, _p) in lobes)
        zone.add_subzone(name, int(x0 - 2), int(y0 - 2), int(x1 - x0 + 4), int(y1 - y0 + 4))
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
    cands = []
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            nx, ny = int(x) + dx, int(y) + dy
            if not z.is_walkable(nx, ny):
                continue
            if z.base_layer[ny][nx] in ("shallow_water", "deep_water", "lava"):
                continue
            if any(max(abs(qx - nx), abs(qy - ny)) <= avoid for (qx, qy) in L.critical):
                continue
            cands.append((dx * dx + dy * dy, nx, ny))
    # EVERY candidate in distance order, not just the nearest. L.prop has its own refusals - chiefly
    # "would isolate N tiles", which a solid prop in a doorway earns - and giving up on the first one
    # leaves a room bare for a reason that the next tile over does not have.
    for (_d, nx, ny) in sorted(cands):
        if L.prop(name, nx, ny, height, **kw):
            return True
    L.skipped.append((name, x, y, "no usable floor within radius"))
    return False


# =====================================================================================================
# BOULDER'GOR - DUMBBELL. Ogres, Arathi West's moor.
# Two halls and one crawl, and that is the whole cave. The crawl is deliberately long and narrow: an
# ogre hold where the two mobs cannot see each other is a place you can actually fight through, and the
# shape says "these two bands barely tolerate each other" without a line of dialogue.
# =====================================================================================================
BOULDERGOR = dict(
    W=66, H=52, PORTAL=(30, 46),
    PATHS={
        "mouth":   ([(30, 46), (30, 42), (29, 39)], 5.0, 5.2),
        # the crawl, with two PASSING PLACES where it bellies out - the rhythm is squeeze, breathe,
        # squeeze, and an ogre band can only come at you one at a time in the narrow parts
        "crawl_a": ([(26, 33), (21, 31), (18, 28)], 3.0, 3.0),
        "crawl_b": ([(18, 28), (15, 24), (18, 21)], 3.0, 3.0),
        "crawl_c": ([(18, 21), (22, 18), (27, 17)], 3.0, 3.2),
        "stash":   ([(16, 26), (10, 25)], 2.6, 3.4),          # a dead-end pocket off the crawl
        "upper":   ([(30, 17), (36, 15), (42, 14)], 4.4, 4.6),
        # a crack above the lower hall: a loop round the spine, so the hall can be fought two ways
        "crack":   ([(24, 26), (31, 23), (39, 26)], 2.8, 2.8),
    },
    ROOMS={
        "mouth": ([(30, 44, 8.0, 4.5, 0, 0.4)], "The Boulder Gate"),
        # the lower hall: two overlapping lobes, so it has a waist rather than being one oval
        "lower": ([(24, 33, 10.0, 6.5, 10, 1.2), (38, 31, 11.0, 6.0, -8, 2.6)], "The Lower Hall"),
        # the chief's hall: a long main bay with a raised back bay behind the pillars
        "upper": ([(46, 15, 11.0, 5.5, 0, 2.3), (56, 11, 7.0, 4.5, 20, 0.9)], "The Chief's Hall"),
    },
    #: sleeping dens off the lower hall's north wall, and the chief's larder
    ALCOVES=[(19, 26, 3.4, 2.8, 0, 1.1), (29, 25, 3.0, 2.6, 0, 2.2), (41, 25, 3.4, 2.8, 0, 0.6),
             (52, 20, 3.6, 3.0, 0, 1.8)],
    #: the spine that splits the lower hall into two aisles, and the chief's roof supports
    PILLARS=[(31, 33, 5.0, 1.8, -12), (44, 13, 1.8, 1.8, 0), (50, 16, 1.8, 1.8, 0),
             (14, 25, 1.4, 1.4, 0)],
    BOSSES=[(57, 11, "Gor'mok the Pit Chief"), (24, 34, "Gruln Stonejaw")],
    CHESTS=[(10, 25), (41, 25), (19, 26), (52, 20)],
    BAKED=f"{BAKED_ROOT}/bouldergor/baked",
    DESC="A two-hall ogre hold on the high moor, joined by a crawl neither band likes using.",
    REGION="Arathi West",  # THE PARENT OPEN ZONE'S NAME, which is also its encounter-table key
    # (data/creatures/encounters.json). "Arathi Highlands" is the region in
    # prose and the name of nothing in the game: the three open maps are
    # Arathi West/Central/East, and CreatureManager.get_encounter_table looks
    # a cave up at zones[region]["caves"][name]. All seven Arathi caves were
    # set to the prose name, so all seven resolved NO table - their pinned
    # bosses never spawned and the player met the open zone's own mobs
    # instead (qa_encounter_tables).
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
        "mouth":   ([(32, 50), (33, 46), (34, 43)], 5.0, 5.2),
        "spoke_n": ([(36, 32), (39, 25), (36, 18)], 3.6, 4.2),          # kinked
        "spoke_w": ([(26, 36), (18, 34), (11, 29)], 3.4, 4.0),          # straight-ish
        "spoke_e": ([(46, 37), (55, 34), (63, 30)], 3.6, 4.2),
        "spoke_s": ([(40, 45), (47, 51), (54, 56)], 3.4, 3.8),
        # THE BACK PASSAGE. A pure star is five dead ends; this one link turns the north and east dens
        # into a loop, so a pull in the hall can be run away from in more than one direction.
        "back":    ([(37, 17), (50, 16), (62, 22), (66, 27)], 2.8, 2.8),
        # and a servants' crack from the west den down to the larder, long and mean
        "crack":   ([(10, 32), (14, 44), (26, 54), (42, 58), (52, 58)], 2.4, 2.4),
    },
    ROOMS={
        "mouth": ([(33, 48, 7.5, 4.2, 0, 0.5)], "The Fist Gate"),
        # the feast hall: three lobes, so it is a long room with a bulge rather than a circle
        "hall":  ([(28, 39, 10.0, 6.5, 8, 1.0), (40, 38, 10.0, 7.0, -6, 2.4),
                   (34, 45, 7.0, 4.0, 0, 3.0)], "The Feast Hall"),
        "north": ([(35, 15, 7.0, 5.0, 0, 1.9), (41, 12, 4.5, 3.6, 0, 0.3)], "The Bone Den"),
        "west":  ([(8, 28, 6.5, 5.0, 0, 2.4), (10, 21, 4.5, 3.6, 15, 1.2)], "The Scrap Den"),
        "east":  ([(67, 29, 7.0, 5.5, 0, 0.8), (62, 35, 5.0, 4.0, 0, 2.7)], "The Chief's Den"),
        "south": ([(57, 58, 7.0, 4.5, 0, 3.1), (49, 60, 5.0, 3.4, 0, 1.5)], "The Deep Larder"),
    },
    ALCOVES=[(21, 33, 3.2, 2.6, 0, 0.9), (30, 31, 3.0, 2.4, 0, 2.1), (45, 31, 3.2, 2.6, 0, 1.4),
             (52, 40, 3.4, 2.8, 0, 2.9), (28, 18, 3.0, 2.6, 0, 0.4), (56, 20, 3.2, 2.6, 0, 3.4)],
    #: four roof supports in a rough square, plus a rock island the fire pit sits against
    PILLARS=[(26, 34, 2.0, 2.0, 0), (44, 33, 2.0, 2.0, 0), (26, 44, 2.0, 2.0, 0), (44, 44, 2.0, 2.0, 0),
             (35, 41, 3.0, 1.6, 20), (66, 32, 1.6, 1.6, 0), (6, 25, 1.6, 1.6, 0)],
    BOSSES=[(69, 27, "Boulderfist Hal'dun"), (41, 11, "Mauler Krakk")],
    CHESTS=[(21, 33), (8, 21), (28, 18), (52, 40), (49, 60)],
    BAKED=f"{BAKED_ROOT}/boulderfist/baked",
    DESC="The larger ogre hold: a feast hall with four dens off it, grown rather than planned.",
    REGION="Arathi Central",  # parent open zone, see BOULDERGOR
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
        "mouth":  ([(30, 52), (30, 48), (29, 45)], 4.6, 4.6),
        # the spine BREATHES: it is cut as four segments whose width swells between rib junctions and
        # pinches at them, so walking it has a pulse instead of being one corridor
        "spine_a": ([(29, 45), (29, 41)], 5.6, 3.6),
        "spine_b": ([(29, 41), (29, 36), (28, 31)], 3.6, 5.8),
        "spine_c": ([(28, 31), (28, 26), (28, 21)], 5.8, 3.4),
        "spine_d": ([(28, 21), (28, 16), (28, 11)], 3.4, 6.0),
        "rib_a": ([(29, 41), (22, 40)], 3.0, 3.4), "rib_b": ([(29, 41), (36, 40)], 3.0, 3.4),
        "rib_c": ([(29, 31), (20, 30)], 3.0, 3.4), "rib_d": ([(29, 31), (38, 30)], 3.0, 3.4),
        "rib_e": ([(28, 21), (19, 20)], 3.0, 3.4), "rib_f": ([(28, 21), (37, 20)], 3.0, 3.4),
        # THE ROBBERS' TUNNEL. Someone dug in from the side and cut across two ribs rather than walk
        # the spine - it is crooked, too narrow, and it is the reason this barrow is already empty.
        "robbers": ([(14, 44), (13, 36), (16, 30), (15, 24), (18, 19)], 2.4, 2.4),
        "rob_in":  ([(14, 44), (20, 42)], 2.4, 2.4),
    },
    ROOMS={
        "mouth": ([(30, 50, 6.5, 4.0, 0, 0.6)], "The Barrow Mouth"),
        "n_a":   ([(19, 40, 4.5, 3.6, 0, 1.4)], "The First Niches"),
        "n_b":   ([(39, 40, 4.5, 3.6, 0, 2.2)], "The Second Niches"),
        "n_c":   ([(17, 30, 4.5, 3.6, 0, 0.9)], "The Flooded Niches"),
        "n_d":   ([(41, 30, 4.5, 3.6, 0, 2.8)], "The Silted Niches"),
        "n_e":   ([(16, 20, 4.5, 3.6, 0, 1.7)], "The Drowned Niches"),
        "n_f":   ([(40, 20, 4.5, 3.6, 0, 3.3)], "The Last Niches"),
        # the head: a wide chamber with a deep apse behind the thane
        "head":  ([(28, 9, 12.0, 6.0, 0, 2.0), (28, 4, 6.0, 3.0, 0, 0.7)], "The Barrow Head"),
    },
    #: burial shelves - small pockets off the ribs and the spine, the actual graves
    ALCOVES=[(23, 44, 2.6, 2.2, 0, 0.5), (34, 44, 2.6, 2.2, 0, 1.6), (23, 34, 2.6, 2.2, 0, 2.7),
             (34, 34, 2.6, 2.2, 0, 0.8), (22, 24, 2.6, 2.2, 0, 1.9), (34, 24, 2.6, 2.2, 0, 3.0),
             (21, 15, 3.0, 2.4, 0, 1.1), (35, 15, 3.0, 2.4, 0, 2.3)],
    #: a plinth in each niche chamber, and a ring of columns round the thane
    PILLARS=[(19, 40, 1.4, 1.4, 0), (39, 40, 1.4, 1.4, 0), (17, 30, 1.4, 1.4, 0), (41, 30, 1.4, 1.4, 0),
             (16, 20, 1.4, 1.4, 0), (40, 20, 1.4, 1.4, 0),
             (22, 10, 1.6, 1.6, 0), (34, 10, 1.6, 1.6, 0), (22, 6, 1.6, 1.6, 0), (34, 6, 1.6, 1.6, 0),
             (28, 38, 1.5, 3.0, 0), (28, 28, 1.5, 3.0, 0)],
    BOSSES=[(28, 4, "The Barrow Warden"), (18, 19, "Thane Aldric's Shade")],
    CHESTS=[(23, 44), (34, 34), (21, 15), (35, 15), (13, 36)],
    BAKED=f"{BAKED_ROOT}/barrow/baked",
    DESC="An Arathor barrow dug into a hill that is now below the waterline. The far end is water.",
    REGION="Arathi East",  # parent open zone, see BOULDERGOR
)


def _dress_barrow(zone, L):
    P = lambda *a, **k: _place(L, *a, **k)   # noqa: E731 - snaps onto real floor
    # THE DOOR IS BEHIND YOU. The gate stood solid at y=49, three tiles in front of where the
    # barrow sets you down, so the way in began with walking round its own front door. Kyle,
    # 12 Nov: "Entering Drowned Barrow and I just immediately hit a wall prop." It is the door
    # you came through now: against the south wall, round the arrival tile, not solid.
    # Placed directly rather than through _place: _place snaps a prop AWAY from the arrival
    # tile, which is the one place this has to be.
    zone.add_landmark("assets/tiles/dungeon_props/gothic_gate.png", 27, 49, 6, 6, solid=False)
    P("broken_column", 25, 51, 5, solid="core")
    # the ribs: a sarcophagus in each, getting worse as you go in
    # NOT solid: each niche already has a stone plinth carved as a PILLAR at its centre, so a solid
    # sarcophagus in the same small room leaves a ring of floor too thin to walk and L.prop refuses it
    # outright ("would isolate 3 tiles"). The lid lies flat beside the plinth instead.
    for (x, y) in ((21, 40), (37, 40), (19, 30), (43, 30), (18, 21), (38, 21)):
        P("sarcophagus", x, y, 4, solid=False, avoid=1)
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
        # Both ramps run INTO the shelf above, not up to its edge. Stopping at (12,19) left the
        # whole crew shelf and its three bunks sealed off - the boss with them.
        "ramp2": ([(22, 29), (14, 25), (13, 20), (17, 16)], 4.0, 4.2),
        # THE BACK STAIR. Narrow, hidden behind the cargo, and it skips a whole shelf. A smuggler's
        # cave with one route through it is a warehouse; this is the thing the crew uses when the
        # revenue men come in the front.
        "stair": ([(50, 41), (56, 44), (62, 38), (62, 28), (58, 20), (46, 15)], 2.4, 2.4),
        # and a tide channel along the back of the boat floor, cutting behind the rock islands
        "channel": ([(14, 38), (24, 36), (36, 37), (46, 39)], 2.8, 2.8),
    },
    ROOMS={
        # three long shelves, each two lobes so they have ends rather than being one bar
        "dock":  ([(22, 42, 11.0, 5.0, 0, 0.7), (36, 41, 10.0, 5.5, 0, 2.2)], "The Boat Floor"),
        "cargo": ([(28, 28, 11.0, 5.5, 0, 1.6), (44, 27, 11.0, 6.0, 0, 3.0)], "The Cargo Shelf"),
        "crew":  ([(24, 14, 10.0, 5.5, 0, 2.5), (38, 13, 9.0, 5.0, 0, 1.0)], "The Crew's Shelf"),
    },
    #: bunks off the crew shelf, a lamp room, and two cargo bays
    ALCOVES=[(18, 8, 3.2, 2.6, 0, 0.4), (28, 7, 3.2, 2.6, 0, 1.5), (40, 7, 3.2, 2.6, 0, 2.6),
             (34, 21, 3.4, 2.6, 0, 0.9), (52, 21, 3.4, 2.6, 0, 2.0), (16, 46, 3.4, 2.8, 0, 3.1)],
    #: rock islands standing in the boat floor, and a crate-row spine down the cargo shelf
    # NO ISLAND AT (28,43) ANY MORE. It stood three tiles north of the arrival at (28,48), dead
    # centre in the mouth of the entry nook - Kyle, 10 Nov: "Wrackline hold....zone in and hit
    # that wall again, not a good design." The boat floor keeps its other two.
    PILLARS=[(40, 44, 2.2, 1.8, -20), (17, 40, 2.0, 1.6, 0),
             (34, 29, 4.5, 1.5, 0), (48, 29, 3.0, 1.5, 0), (30, 15, 1.8, 3.0, 0)],
    BOSSES=[(44, 12, "Captain Mory Vane"), (58, 30, "Ledger-Keeper Ashkin")],
    CHESTS=[(16, 46), (34, 21), (52, 21), (18, 8), (40, 7)],
    BAKED=f"{BAKED_ROOT}/wrackline/baked",
    DESC="A sea cave in three shelves: boats at the tideline, cargo above it, the crew above that.",
    REGION="Arathi East",  # parent open zone, see BOULDERGOR
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
        "mouth":  ([(34, 50), (33, 47), (32, 44)], 5.0, 5.0),
        # the two arms of the ring, DIFFERENT WIDTHS: the west arm is broad and the east arm pinches
        # to almost nothing halfway round, so the two ways to the causeway are not the same walk
        "ring_w": ([(28, 42), (16, 36), (12, 26), (18, 16), (28, 11)], 5.0, 5.0),
        "ring_e": ([(36, 42), (48, 37), (52, 27), (46, 17), (36, 11)], 4.4, 2.6),
        "causeway": ([(32, 10), (32, 22)], 3.4, 3.4),         # the only way onto the island
        # the island is a RING ITSELF - a walkway round a pool in its middle
        "isle_w": ([(30, 23), (26, 27), (30, 32)], 3.0, 3.0),
        "isle_e": ([(34, 23), (38, 27), (34, 32)], 3.0, 3.0),
        "isle_s": ([(30, 32), (34, 32)], 3.0, 3.0),
        # a stub to the south-east pocket. As a bare ALCOVE it floated 27 tiles clear of the
        # ring - an alcove only works if it overlaps something, and this one did not.
        "pocket_e": ([(42, 42), (46, 45)], 2.4, 2.4),
    },
    ROOMS={
        "mouth": ([(33, 48, 6.5, 3.8, 0, 0.5)], "The Tide Gate"),
        "sump":  ([(32, 27, 8.0, 7.5, 0, 1.3)], "The Sump"),
        "north": ([(32, 10, 10.0, 4.0, 0, 2.1), (24, 12, 5.0, 3.4, 0, 0.6)], "The North Shelf"),
    },
    #: pockets off the outer ring - what the tide has pushed into the wall
    ALCOVES=[(9, 30, 3.4, 3.0, 0, 0.8), (14, 18, 3.2, 2.6, 0, 1.9), (55, 30, 3.4, 3.0, 0, 3.0),
             (50, 18, 3.0, 2.4, 0, 1.2), (20, 44, 3.2, 2.6, 0, 2.4), (46, 45, 3.2, 2.6, 0, 0.3)],
    #: the pool at the heart of the island, and two stacks pinching the east arm
    PILLARS=[(32, 27, 3.2, 3.2, 0), (49, 32, 2.2, 2.6, 0), (47, 22, 2.0, 2.2, 0),
             (15, 32, 1.8, 2.0, 0)],
    BOSSES=[(32, 22, "The Wrack-Drowned"), (9, 30, "Brinemaw")],
    CHESTS=[(32, 32), (20, 44), (55, 30), (24, 12)],
    BAKED=f"{BAKED_ROOT}/tidewrack/baked",
    DESC="A round flooded sump with a ringed island in the middle and a shelf round the wall.",
    REGION="Arathi East",  # parent open zone, see BOULDERGOR
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
