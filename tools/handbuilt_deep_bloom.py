"""
Hand-built The Deep Bloom (130x150): the Underdark's dungeon. Levels 36-39, five bosses.

ARCHETYPE: THE MISREMEMBERED LIBRARY.

The mycelium under the Sporefall is a network, and a network that has spent four years in a mana-saturated
cavern beneath a library has started to do something with that. The Deep Bloom is where it has grown into the
shape of what it absorbed - and the horror is not that it built a library. It is that it built one WRONG, from
the inside, having never seen a building.

So the map is a gradient, and the gradient is FROM ARCHITECTURE INTO TISSUE:

    THE PORTICO         almost convincing. Square, columned, a hall you could believe in.
    THE STACKS          long parallel shelf-galleries. Still exact rectangles.          [The Index]
    THE REPEATED WING   the same gallery, grown twice, with a seam where the copies meet.
                        The player notices they have been here before. They have.        [The Second Copy]
    THE SCRIPTORIUM     proportions drifting, corners softening, walls thickening.       [The Scriptor]
    THE LOWER STACKS    rooms remembering they were rooms, and failing.                  [Errata]
    THE HEART           no architecture left at all.                                     [The Deep Bloom]

That is built into the GEOMETRY, not just the art: the upper sections are carved with exact rects, the middle
with chamfered rects, the lower with ellipse lobes. tools/verify_deep_bloom.py measures it - the straight-run
fraction of each section's floor/wall boundary - because a claim like this one is worth nothing if it only
exists in a docstring.

AND MEASURING IT CORRECTED IT. The first test demanded a smooth fall band by band and the map failed twice, in
both cases because the test was wrong. What the map actually does is better: it holds at 0.56-0.67 for three
sections and then drops off a cliff to 0.27, 0.06, 0.11. The Bloom copies a library competently, and then STOPS
BEING ABLE TO. A gradual slide would have been the Bloom getting tired; a collapse is the Bloom running out of
whatever it was using to remember, which is the more frightening of the two and the one the art already paints.

DUNGEON, not cave: fixed spawns, hand-authored packs, and on world/zone_classification.DUNGEONS so it carries
no gathering. Trash is authored here rather than rolled, for the reason Durnholde taught - a generic router
hands bosses zero pulls when a layout is not a simple chain.

HARD CONTRACT (world/portal_manager.py): portal (65, 144) <-> The Crystalline Underdark (34, 142).
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401

BAKED = "assets/tiles/deep_bloom/baked"
UDP = "assets/tiles/underdark/props/"
W, H = 130, 150
PORTAL = (65, 144)

#: EXACT rects - the sections where the Bloom still remembers what a wall is. (x0, y0, x1, y1)
RECTS = {
    "portico":      (46, 128, 84, 142),
    "stack_hall":   (56, 104, 74, 128),       # the spine of the Stacks
    "stack_w1":     (24, 118, 54, 124),       # shelf-galleries, parallel and identical
    "stack_w2":     (24, 106, 54, 112),
    "stack_e1":     (76, 118, 106, 124),
    "stack_e2":     (76, 106, 106, 112),
    # THE REPEATED WING: these two are the SAME rect, grown twice, 18 tiles apart. The duplication is the
    # point - the mycelium copied a shelf-rank it liked and did not notice it had already made one.
    "repeat_a":     (30, 86, 100, 96),
    "repeat_b":     (30, 68, 100, 78),
    "repeat_seam":  (62, 78, 68, 86),         # the join, where the two copies meet and do not quite line up
}
#: CHAMFERED rects - the Scriptorium, where the proportions have started to drift.
CHAMFERED = {
    "scriptorium":  (42, 46, 86, 65, 5),
    "scrip_w":      (18, 51, 42, 61, 4),
    "scrip_e":      (88, 48, 112, 62, 5),       # the east wing is bigger and sits higher: the mirror is going
}
#: LOBES - below here it is tissue. (cx, cy, rx, ry)
#: AND THE SYMMETRY GOES WITH THE GEOMETRY. The upper half of this map is mirrored on x=65 because a building
#: is mirrored - a library has matching stacks either side of its spine, and the Repeated Wing is symmetric
#: twice over, which is its whole joke. Below the Scriptorium nothing is mirrored, because nothing down there
#: was built. The first draft kept the mirror all the way to the Heart and the bottom of the map read as
#: architecture no matter what it was carved with; losing the axis is as much of the collapse as losing
#: the corners.
LOBES = {
    "lower_w":      (31, 35, 15, 9),
    "lower_c":      (67, 31, 16, 12),
    "lower_e":      (98, 29, 12, 11),
    "heart_throat": (61, 20, 9, 6),             # off the spine - the way in is no longer on the axis
    "heart":        (68, 11, 24, 9),            # and the Heart has drifted east of everything above it
}

#: Connections. Narrow where the Bloom grew a doorway because it had seen one, wide where it forgot.
PASSAGES = [
    ([(65, 140), (65, 132), (65, 126)], 2),       # portico -> stack hall
    ([(56, 121), (50, 121)], 1), ([(74, 121), (80, 121)], 1),
    ([(56, 109), (50, 109)], 1), ([(74, 109), (80, 109)], 1),
    ([(65, 106), (65, 98), (65, 94)], 2),         # stack hall -> repeat_a
    ([(65, 92), (65, 86)], 1),                    # through the seam
    ([(65, 78), (65, 72)], 1),
    ([(65, 68), (65, 62)], 2),                    # repeat_b -> scriptorium
    ([(46, 56), (40, 56)], 1), ([(84, 56), (90, 56)], 1),
    ([(65, 46), (65, 40), (65, 36)], 2),          # scriptorium -> lower stacks
    # lower_c moved east, so the west link has to start deeper inside it - at x=50 the corridor stopped one
    # tile short of the lobe's new edge and orphaned the whole west chamber. The kit's flood-fill caught it.
    ([(58, 34), (46, 34)], 1), ([(80, 33), (90, 31)], 1),
    ([(65, 26), (65, 22)], 1),                    # lower -> throat
    ([(65, 15), (65, 13)], 2),                    # throat -> heart
]

BOSSES = {}
CHESTS = []
GROUPS = []                      # packs as placed, mirrored onto zone.trash_packs
TRASH = []

#: Hand-authored, for the reason Durnholde taught: a generic router gave two of its five bosses ZERO pulls
#: because a layout that is not a simple chain defeats "assign mobs to the boss they lead to". Three to four
#: groups between each boss (Kyle), and the roster thins toward the Heart as architecture gives way - by the
#: Lower Stacks there is nothing left that was ever shaped like a librarian.
THRALL, SHELF, SCRIBE = "Bloom Thrall", "Shelf-Grown", "Spore Scribe"
BINDER, PULP = "Mycelial Binder", "Pulpwright"
PACKS = [
    # --- the Portico and the first rank of galleries, before The Index (4)
    (65, 134, [(THRALL, 36), (THRALL, 36), (SHELF, 36)]),
    (65, 126, [(SHELF, 36), (THRALL, 36), (SCRIBE, 36)]),
    (40, 121, [(SHELF, 36), (SHELF, 36), (THRALL, 37), (SCRIBE, 36)]),
    (90, 121, [(SHELF, 37), (THRALL, 37), (SCRIBE, 37)]),
    # --- the lower galleries and the first copy, before The Second Copy (4)
    (40, 109, [(THRALL, 37), (SHELF, 37), (BINDER, 37)]),
    (90, 109, [(SHELF, 37), (SCRIBE, 37), (THRALL, 37), (SHELF, 37)]),
    # the same pack, twice, because everything in this wing is twice
    (44, 91, [(SHELF, 37), (SCRIBE, 37), (BINDER, 37), (THRALL, 38)]),
    (86, 91, [(SHELF, 37), (SCRIBE, 37), (BINDER, 37), (THRALL, 38)]),
    # --- the second copy's floor and the scriptorium wings, before The Scriptor (4)
    (44, 73, [(SCRIBE, 38), (BINDER, 38), (SHELF, 38), (THRALL, 38)]),   # and again
    (86, 73, [(SCRIBE, 38), (BINDER, 38), (SHELF, 38), (THRALL, 38)]),   # and again
    (30, 56, [(SCRIBE, 38), (SCRIBE, 38), (BINDER, 38)]),
    (99, 56, [(SCRIBE, 38), (BINDER, 38), (PULP, 39)]),
    # --- the Lower Stacks, before Errata. No scribes left down here, only the heavy grown things (3)
    (36, 33, [(PULP, 39), (PULP, 39), (THRALL, 39)]),
    (94, 33, [(PULP, 39), (THRALL, 39), (BINDER, 39)]),
    (65, 38, [(PULP, 39), (PULP, 39), (BINDER, 39), (THRALL, 39)]),
    # --- the throat, before The Deep Bloom. A threshold, not a gauntlet (3)
    (65, 22, [(PULP, 39), (BINDER, 39), (PULP, 39)]),
    (58, 18, [(PULP, 39), (PULP, 39)]),
    (72, 18, [(BINDER, 39), (PULP, 39)]),
]


def _near_walkable(zone, x, y, rad=8):
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            if zone.is_walkable(int(x) + dx, int(y) + dy):
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, int(x) + dx, int(y) + dy)
    return None if best is None else (best[1], best[2])


def build_deep_bloom():
    zone = Tilemap("The Deep Bloom", W, H,
                   "A library grown from the inside by something that had never seen one, and got it almost "
                   "right for the first few halls.")
    zone.is_cave = True
    zone.region = "The Crystalline Underdark"
    zone.fixed_spawns = True
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b

    # THE GRADIENT IS IN THE CARVING, not only in the art: exact rects where the Bloom still remembers walls,
    # chamfered rects where it is losing them, lobes where it never had them.
    for (x0, y0, x1, y1) in RECTS.values():
        b.rect(x0, y0, x1, y1)
    for (x0, y0, x1, y1, ch) in CHAMFERED.values():
        b.rect(x0, y0, x1, y1, chamfer=ch)
    b.lobes(list(LOBES.values()))
    for pts, w in PASSAGES:
        b.corridor(pts, width=w)

    # Shelf-ranks standing in the galleries: the Bloom grew furniture too, because a library has furniture.
    b.pillars([30, 38, 46], [119, 123], size=1)
    b.pillars([84, 92, 100], [119, 123], size=1)
    b.pillars([30, 38, 46], [107, 111], size=1)
    b.pillars([84, 92, 100], [107, 111], size=1)
    b.pillars([40, 56, 74, 90], [88, 94], size=1)
    b.pillars([40, 56, 74, 90], [70, 76], size=1)

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.set_tile(px, py, "dirt", "base")
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    # EACH BOSS SITS AT THE FAR END OF ITS SECTION, i.e. the lowest y the player reaches in it. Placed mid-room
    # (the first draft) the packs straddle them, so a player meets half a boss's trash after killing it and the
    # three-to-four rule becomes meaningless - tools/verify_deep_bloom.py counts this and caught it.
    bosses = [(65, 114, "The Index"),              # the stack hall, above the first rank of galleries
              (65, 82, "The Second Copy"),         # THE SEAM, where the two copies meet and do not line up.
                                                   # The boss IS the duplication, so it lives at the join.
              (65, 50, "The Scriptor"),            # the scriptorium's north end
              (65, 26, "Errata"),                  # the lower stacks, where the rooms stop being rooms
              (65, 11, "The Deep Bloom")]          # the heart
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
    for (x, y) in ((26, 121), (104, 121), (22, 56), (108, 56), (34, 32)):
        p = _near_walkable(zone, x, y)
        assert p, (x, y)
        chests.append(p)
    CHESTS[:] = chests
    for c in chests:
        L.mark("chest", *c)

    # ---- hand-placed packs, rung around their centre
    TRASH.clear()
    GROUPS.clear()
    occupied = [(x, y) for (x, y) in BOSSES.values()] + [tuple(c) for c in CHESTS] + [PORTAL]
    for (cx, cy, members) in PACKS:
        group = []
        k = len(members)
        for i, (nm, lvl) in enumerate(members):
            ang = 0.4 + 2 * math.pi * i / k
            spot = _near_walkable(zone, cx + 2.4 * math.cos(ang), cy + 2.0 * math.sin(ang), rad=6)
            assert spot, (nm, cx, cy)
            if any(max(abs(spot[0] - o[0]), abs(spot[1] - o[1])) < 2 for o in occupied):
                alt = _near_walkable(zone, cx + 3.4 * math.cos(ang), cy + 2.8 * math.sin(ang), rad=6)
                if alt and all(max(abs(alt[0] - o[0]), abs(alt[1] - o[1])) >= 2 for o in occupied):
                    spot = alt
            occupied.append(spot)
            group.append((spot[0], spot[1], nm, lvl))
            TRASH.append((spot[0], spot[1], nm, lvl))
        GROUPS.append(group)
    # world/cave_spawns.py reads zone.trash_packs directly, so authoring the groups here makes this map
    # self-sufficient: it does NOT need tools/build_dungeon_pulls.py, whose job is regrouping the older
    # dungeons' flat solo-fight chains into packs. These are already packs, placed by hand, and running the
    # regrouper over them would re-cluster and re-place them for no gain.
    zone.trash_packs = [list(g) for g in GROUPS]
    zone.trash_spawns = list(TRASH)

    zone.add_subzone("The Deep Bloom", 0, 0, W, H)        # the encounter-table key covers the whole map
    zone.add_subzone("The Portico", 42, 124, 46, 24)
    zone.add_subzone("The Stacks", 20, 100, 90, 30)
    zone.add_subzone("The Repeated Wing", 26, 64, 78, 36)
    zone.add_subzone("The Scriptorium", 16, 42, 98, 26)
    zone.add_subzone("The Lower Stacks", 18, 20, 94, 24)
    zone.add_subzone("The Heart", 40, 2, 50, 20)
    return zone, L


def finish(zone, L):
    #: The trash goes in as targets as well. L.mark() only treats portal/boss/chest tiles as critical, so a
    #: prop with a solid footprint can be placed on top of a mob and bury it inside a wall - which renders
    #: fine and spawns an unreachable pack. Handing the packs to the flood-fill makes the kit catch it.
    targets = [PORTAL] + [(x, y) for (x, y) in BOSSES.values()] + list(CHESTS) \
        + [(x, y) for (x, y, _n, _l) in TRASH]
    return L.finish(targets)


def dress(zone, L):
    P = L.prop
    U = dict(where=UDP)
    # ---- the Portico: almost convincing, and the columns are the giveaway - they are grown, not cut
    P("ud_broken_column", 52, 138, 7, **U)
    P("ud_broken_column", 78, 138, 7, **U)
    P("ud_fungal_shelf", 50, 130, 5, **U)
    P("ud_fungal_shelf", 80, 130, 5, **U)
    P("ud_spore_vent", 65, 136, 4, **U)
    # ---- the Stacks: shelves of fruiting bodies in the exact ranks of a library
    for x in (30, 44, 86, 100):
        P("ud_fungal_shelf", x, 122, 5, **U)
        P("ud_fungal_shelf", x, 110, 5, **U)
    P("ud_fungal_node", 58, 110, 6, **U)
    P("ud_shelf_fungus", 60, 126, 4, **U)
    P("ud_shelf_fungus", 70, 126, 4, **U)
    # ---- the Repeated Wing: the same dressing, twice, 18 tiles apart. Deliberate.
    for y in (94, 76):
        P("ud_fungal_shelf", 38, y, 5, **U)
        P("ud_fungal_shelf", 92, y, 5, **U)
        P("ud_cocooned_shape", 50, y, 5, **U)
        P("ud_cocooned_shape", 80, y, 5, **U)
    P("ud_fungal_node", 50, 89, 6, **U)
    # ---- the Scriptorium: it was trying to make desks
    P("ud_field_desk", 52, 58, 3, **U)
    P("ud_field_desk", 78, 58, 3, **U)
    P("ud_fungal_shelf", 26, 58, 5, **U)
    P("ud_fungal_shelf", 104, 58, 5, **U)
    P("ud_spore_vent", 65, 60, 4, **U)
    P("ud_cocooned_shape", 44, 52, 5, **U)
    P("ud_cocooned_shape", 86, 52, 5, **U)
    # ---- the Lower Stacks: rooms remembering they were rooms
    P("ud_fungal_node", 28, 36, 6, **U)
    P("ud_fungal_node", 96, 34, 6, **U)
    P("ud_shroom_cluster_blue", 50, 30, 7, **U)
    P("ud_shroom_cluster_blue", 80, 30, 7, **U)
    P("ud_cocooned_shape", 54, 40, 5, **U)
    P("ud_spore_vent", 42, 28, 4, **U)
    # ---- the Heart: no architecture left
    P("ud_fungal_node", 54, 12, 8, **U)
    P("ud_fungal_node", 76, 12, 8, **U)
    P("ud_shroom_canopy", 48, 8, 10, **U)
    P("ud_shroom_canopy", 82, 8, 10, **U)
    P("ud_cocooned_shape", 58, 16, 5, **U)
    P("ud_cocooned_shape", 72, 16, 5, **U)
    P("ud_glow_pool", 65, 14, 3, **U)
    return zone, L


def generate_deep_bloom():
    zone, L = build_deep_bloom()
    dress(zone, L)
    finish(zone, L)
    register_baked(zone, BAKED)
    return zone


def build_deep_bloom_baked():
    """(zone, layout) with props + QA done - what the baker paints from."""
    zone, L = build_deep_bloom()
    dress(zone, L)
    finish(zone, L)
    return zone, L
