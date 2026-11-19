"""
Hand-built The Dry Deep (108x96): the void under the Abyssal Sands. 45-47.

Kyle, 13 Nov 2026, of the Sands: "if we cant go into places in abyssal sands theyre wasted space
too", and then: "lets actually build an underground that is fully linked by 6 entrances? That'd be
super cool. Like another underground layer entered by each sinkhole that links up underground."

THIS IS THE VOID THE FLOOR FELL INTO. The Sands' own notes say what happened up there - a limestone
floor collapsed into a cavern that had drained. Nobody had built the cavern. It is one connected
space, and the six sinkholes that can be climbed down are six holes in its roof: go down any one
of them and you can walk to the foot of any other, under the desert, and come up somewhere else.

THE MAP IS THE SURFACE AT SIX TENTHS. Each chamber sits where its sinkhole is on the map above
(pit centre x 0.6), so the underground has the same shape as the ground over it and a player who
knows the Sands already knows roughly where they are. Light comes down each shaft, and the
chambers between them have none.

A CAVE, NOT A DUNGEON (claude/dungeon_authoring_rules): fixed_spawns False, trash rolled per step,
the boss and the rare pinned by zone.boss_positions and present in the table at weight 0.

THE SIX WAYS DOWN, as (surface pit, surface tile) -> tile here. world/portal_manager.py holds the
same pairs and tools/handbuilt_abyssal_sands.DESCENTS names the six pits.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked  # noqa: F401

BAKED = "assets/tiles/dry_deep/baked"
#: Kyle, 19 Nov 2026: "We can also have the writhing deep in Feralas connect to the map under Abyssal Sands. Since the
#: silithids are digging....". The Zukk'ash tunnel comes out in the Brine Seep's west wall: Feralas lies west.
FERALAS = (3, 37)
FERALAS_ARRIVAL = (6, 37)
SFP = "assets/tiles/shimmering_flats/props/"
SNP = "assets/tiles/southern_needles/props/"

NAME = "The Dry Deep"
W, H = 108, 96
BAKED_DIR = BAKED
SCALE = 0.6

#: (chamber name, surface pit it hangs under, surface pit centre). The chamber centre is the pit
#: centre at SCALE, and the portal is the chamber centre.
SHAFTS = [
    ("Under the First Hole",   "The First Hole",    (44, 34)),
    ("Under Nineteen Mile",    "Nineteen Mile Pit", (104, 48)),
    ("Under the Wide Sink",    "The Wide Sink",     (62, 66)),
    ("Under the Throat",       "The Throat",        (36, 92)),
    ("Under the Long Collapse", "The Long Collapse", (84, 112)),
    ("Under the Underlight",   "Underlight",        (148, 116)),
]


def _under(pt):
    return int(round(pt[0] * SCALE)), int(round(pt[1] * SCALE))


#: tile here -> (surface pit name, surface tile)
PORTALS = {_under(c): (pit, c) for (_n, pit, c) in SHAFTS}
PORTAL = _under(SHAFTS[2][2])           # the Wide Sink: the first one anybody could climb down

#: (name, cx, cy, rx, ry). The six under the shafts, then the dark between them.
CHAMBERS = [(n, _under(c)[0], _under(c)[1], 8, 7) for (n, _p, c) in SHAFTS] + [
    ("The Drained Sea",   60, 48, 13, 10),      # the middle of it, and the biggest room in Tanaris
    ("The Glass Roots",   78, 54, 8, 7),        # under the Glasswall: what the glass grew down into
    ("The Old Shoreline", 38, 78, 9, 6),        # a beach, at the bottom of a desert
    # Kyle, 13 Nov 2026, of the way down to the layer below: "I want it at the end of the descent."
    # The furthest room from every shaft: east of the Drained Sea, a dead end with a stair in it.
    ("The Last Descent",  95, 40, 7, 6),
    # ---- THE OUTSIDE RING (Kyle, 16 Nov 2026: "more tunnels, more places, optional bosses round the edge").
    # It was a hub with spokes: every room led to the Drained Sea. These are the rooms past the shafts, at the
    # edges of where the sea was, and the tunnels between them make loops that never touch the middle.
    ("The Salt Galleries",   10, 9, 7, 5),       # 10: where the sea left its salt, in layers you can walk along
    ("The Brine Seep",        8, 37, 5, 6),      # 11: the last of the water, still coming out of the wall
    ("The Whispering Fault", 46, 7, 9, 4),       # 12: a crack along the top of the cave; the wind comes down it
    ("The Fossil Shelf",     92, 15, 8, 6),      # 13: the old sea's floor, standing on its edge
    ("The Brood Shelf",      12, 85, 8, 6),      # 14: where the crawlers come from
    ("The Black Pool",       74, 86, 8, 5),      # 15: water nobody has found the bottom of
    ("The Glass Seam",      102, 55, 4, 4),      # 16: a vein of glass, at the end of a crawl
]

#: Down to The Black Strand (tools/handbuilt_black_strand.py), and where you arrive coming up.
DOWN = (98, 40)
DOWN_ARRIVAL = (95, 40)

#: (chamber a, chamber b, width). A ring round the outside, spokes into the Drained Sea, so every
#: shaft reaches every other at least two ways.
TUNNELS = [
    (0, 1, 4), (0, 2, 4), (2, 3, 4), (3, 8, 3), (8, 4, 4), (4, 5, 4), (5, 7, 4), (7, 1, 3),
    (2, 6, 4), (1, 6, 4), (4, 6, 4), (7, 6, 3),
    # the outside ring: four loops that go round the edge without touching the Drained Sea...
    (0, 10, 3), (10, 11, 3), (11, 3, 3),         # First Hole -> Salt Galleries -> Brine Seep -> Throat
    (0, 12, 3), (12, 1, 3),                      # First Hole -> Whispering Fault -> Nineteen Mile
    (3, 14, 3), (14, 8, 3),                      # Throat -> Brood Shelf -> Old Shoreline
    (4, 15, 3), (15, 5, 3),                      # Long Collapse -> Black Pool -> Underlight
    # ...and two rooms at the end of one way in
    (1, 13, 3),                                  # Nineteen Mile -> the Fossil Shelf
    (7, 16, 2),                                  # the Glass Roots -> the Glass Seam, a crawl
]

#: Dead-end side passages: a crawl off a room that ends in a pocket and goes nowhere. (path, pocket rx, ry)
SPURS = [
    ([(38, 82), (41, 88), (46, 91)], 3, 2),      # off the Old Shoreline, down to where the beach ends
    ([(15, 58), (9, 61), (4, 63)], 2, 3),        # off the Throat, west, under the dunes
    ([(95, 74), (101, 79), (104, 84)], 3, 3),    # off the Underlight, east, toward nothing
]

#: rooms at the end of one way in, by design (verify() lets these have a single tunnel)
DEAD_ENDS = {9, 13, 16}

BOSSES = {"The Weight of the Floor": (60, 48), "Old Dry-Eye": (38, 78),
          # the optional three, round the edge and off every route a quest walks you along
          "The Salt Widow": (8, 8), "Coil of the Old Sea": (95, 14), "Mother of Crawlers": (10, 87)}
# NOT the Glasswall Elemental: a quest on the surface sends you to the Glasswall for nine of them,
# and with them down here too the quest's own directions stopped pointing at the Glasswall.
#: Off the ring, in the corners of rooms a quest does not send you to the middle of.
CHESTS = [(30, 22), (80, 58), (24, 56),
          (77, 88), (103, 56), (40, 6), (45, 91)]
TRASH = ["Limestone Crawler", "Hollowing Ooze", "Sinkhole Lurker", "Saltbone Revenant"]


def build_dry_deep():
    zone = Tilemap(NAME, W, H,
                   "The cavern the desert fell into. Six shafts of daylight, a long way apart, and "
                   "between them the bed of a sea that drained before anything was written down.")
    zone.is_cave = True
    zone.region = "The Abyssal Sands"
    zone.fixed_spawns = False
    zone.boss_positions = [(x, y, n) for n, (x, y) in BOSSES.items()]

    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] + 2))
    b = L.b
    for (_n, cx, cy, rx, ry) in CHAMBERS:
        b.lobes([(cx, cy, rx, ry),
                 (cx + rx // 3, cy - ry // 3, int(rx * 0.7), int(ry * 0.7)),
                 (cx - rx // 3, cy + ry // 4, int(rx * 0.6), int(ry * 0.8))])
    for (a, c, wdt) in TUNNELS:
        _n1, ax, ay, _rx, _ry = CHAMBERS[a]
        _n2, bx, by, _rx2, _ry2 = CHAMBERS[c]
        # a dog-leg rather than a ruled line: caves do not run straight between rooms
        mx, my = (ax + bx) // 2 + (by - ay) // 6, (ay + by) // 2 - (bx - ax) // 6
        b.corridor([(ax, ay), (mx, my), (bx, by)], width=wdt)

    # THE LAST DESCENT opens off the east side of the Drained Sea. It is NOT sealed behind the
    # boss - the Sea's rim is where every spoke of this cave meets, and a passage that left it
    # anywhere joined a neighbour (tried twice). You pass the Weight's room to get here; you do
    # not have to kill it.
    b.corridor([(70, 44), (82, 40), (95, 40)], width=3)

    for (path, rx, ry) in SPURS:
        b.corridor(path, width=2)
        ex, ey = path[-1]
        b.lobes([(ex, ey, rx, ry)])

    for (px, py) in PORTALS:
        zone.collision_layer[py][px] = None
        zone.set_tile(px, py, "portal", "interaction")
        L.mark("portal", px, py)
    zone.collision_layer[DOWN[1]][DOWN[0]] = None
    L.mark("portal", *DOWN)
    # the Zukk'ash tunnel from Feralas comes out in the Brine Seep's west wall (19 Nov 2026)
    zone.collision_layer[FERALAS[1]][FERALAS[0]] = None
    zone.set_tile(FERALAS[0], FERALAS[1], "portal", "interaction")
    L.mark("portal", *FERALAS)
    for n, (x, y) in BOSSES.items():
        L.mark("boss_marker", x, y)        # the tile the other caves use; "boss" is not a tile at all
    for c in CHESTS:
        L.mark("chest", *c)

    for (name, cx, cy, rx, ry) in CHAMBERS:
        zone.add_subzone(name, max(0, cx - rx), max(0, cy - ry), rx * 2, ry * 2)
    zone.arrivals = [(px, py + 2) for (px, py) in PORTALS] + [DOWN_ARRIVAL, FERALAS_ARRIVAL]
    return zone, L


def dress(zone, L):
    P = L.prop
    F = dict(where=SFP)
    N = dict(where=SNP)
    # under each shaft: what fell in when the roof went
    for i, (px, py) in enumerate(PORTALS):
        P("sn_stone_pile", px - 4, py + 3, 3, near_ok=True, **N)
        P("sn_toppled_column" if i % 2 else "sn_split_stone", px + 4, py - 2, 4, near_ok=True, **N)
        P("sn_rope_coil", px + 2, py + 3, 2, near_ok=True, **N)
    # the Drained Sea: bones of things that swam
    for (x, y) in [(52, 44), (66, 52), (58, 54), (68, 44), (54, 50)]:
        P("sn_rib_bones", x, y, 4, near_ok=True, **N)
    P("sn_kodo_skull", 62, 42, 4, near_ok=True, **N)
    # the Glass Roots
    for (x, y) in [(74, 52), (80, 56), (78, 50)]:
        P("sf_resin_growth", x, y, 4, near_ok=True, **F)
    # the Old Shoreline: driftwood, at the bottom of a desert
    for (x, y) in [(34, 76), (42, 80), (36, 80)]:
        P("sn_driftwood_salt", x, y, 3, near_ok=True, **N)
    # the wreck of whoever came down the Wide Sink first with a winch
    P("sf_hand_winch", PORTAL[0] - 5, PORTAL[1] - 2, 4, **F)
    P("sf_crate_stack", PORTAL[0] + 5, PORTAL[1] + 2, 4, **F)
    # ---- the outside ring
    for (x, y) in [(6, 11), (14, 7), (16, 11)]:                 # the Salt Galleries: salt, and the dead it kept
        P("sn_split_stone", x, y, 3, near_ok=True, **N)
    P("sn_rib_bones", 12, 12, 3, near_ok=True, **N)
    for (x, y) in [(6, 34), (10, 41)]:                          # the Brine Seep
        P("sn_driftwood_salt", x, y, 3, near_ok=True, **N)
    # the Zukk'ash tunnel's mouth in the Seep's west wall, dug through from Feralas (the Zukk'ash Hive)
    P("ent_exit_kobold_tunnel", FERALAS[0] + 1, FERALAS[1] - 1, 4, near_ok=True, where="assets/tiles/cave_entrances/")
    for (x, y) in [(40, 8), (52, 7)]:                           # the Whispering Fault
        P("sn_split_stone", x, y, 3, near_ok=True, **N)
    for (x, y) in [(88, 14), (98, 17), (92, 19)]:               # the Fossil Shelf: things that swam, in the wall
        P("sn_kodo_skull" if x == 88 else "sn_rib_bones", x, y, 4, near_ok=True, **N)
    for (x, y) in [(8, 82), (16, 88), (14, 82)]:                # the Brood Shelf
        P("sn_stone_pile", x, y, 3, near_ok=True, **N)
    for (x, y) in [(70, 84), (80, 87)]:                         # the Black Pool's edge
        P("sn_driftwood_salt", x, y, 3, near_ok=True, **N)
    P("sf_resin_growth", 101, 53, 4, near_ok=True, **F)         # the Glass Seam
    return zone, L


def verify(zone):
    """Fully linked: every shaft reaches every other, the boss and the rare."""
    import collections
    assert zone.is_cave is True and zone.fixed_spawns is False
    start = (PORTAL[0], PORTAL[1] + 2)
    seen = {start}
    q = collections.deque([start])
    while q:
        x, y = q.popleft()
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + d[0], y + d[1])
            if 0 <= n[0] < W and 0 <= n[1] < H and n not in seen and zone.is_walkable(*n):
                seen.add(n)
                q.append(n)
    cut = [p for p in PORTALS if not any((p[0] + dx, p[1] + dy) in seen
                                         for dx in (-1, 0, 1) for dy in (-1, 0, 1))]
    assert not cut, f"these shafts are not linked to the rest: {cut}"
    lost = [n for n, p in BOSSES.items() if not any((p[0] + dx, p[1] + dy) in seen
                                                     for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2))]
    assert not lost, f"cannot be reached: {lost}"
    gone = [c for c in CHESTS if c not in seen]
    assert not gone, f"chests that cannot be reached: {gone}"
    # NOT A HUB WITH SPOKES: every room but the dead ends has two ways out, and the outside ring still joins up
    # with the Drained Sea taken out of it.
    deg = collections.Counter()
    for (a, c, _w) in TUNNELS:
        deg[a] += 1
        deg[c] += 1
    thin = [CHAMBERS[i][0] for i in range(len(CHAMBERS)) if i not in DEAD_ENDS and i != 9 and deg[i] < 2]
    assert not thin, f"rooms with one way out that are not meant to be dead ends: {thin}"
    ring = collections.defaultdict(set)
    for (a, c, _w) in TUNNELS:
        if 6 not in (a, c):
            ring[a].add(c)
            ring[c].add(a)
    reach, todo = {0}, [0]
    while todo:
        for n in ring[todo.pop()] - reach:
            reach.add(n)
            todo.append(n)
    outer = [i for i in range(len(CHAMBERS)) if i not in (6, 9)]
    cut_off = [CHAMBERS[i][0] for i in outer if i not in reach]
    assert not cut_off, f"without the Drained Sea these rooms are cut off: {cut_off}"
    return dict(chambers=len(CHAMBERS), shafts=len(PORTALS), tunnels=len(TUNNELS), spurs=len(SPURS),
                bosses=len(BOSSES), chests=len(CHESTS), reachable=len(seen))


def finish(zone, L):
    return L.finish(list(PORTALS) + list(BOSSES.values()) + list(CHESTS) + [DOWN, FERALAS])


def build_dry_deep_baked():
    zone, L = build_dry_deep()
    dress(zone, L)
    finish(zone, L)
    return zone, L


def generate_dry_deep():
    zone, L = build_dry_deep_baked()
    # The painted ground. Without this the cave draws in the fallback tiles - plain dirt and a grey
    # grid for rock - which is what the first screenshot of this zone showed.
    register_baked(zone, BAKED)
    return zone


if __name__ == "__main__":
    import sys
    z, _L = build_dry_deep_baked()
    print(verify(z), "props", _L.placed, "skipped", _L.skipped)
    if "--preview" in sys.argv:
        from PIL import Image
        im = Image.new("RGB", (W * 6, H * 6))
        px = im.load()
        marks = {p: (60, 160, 255) for p in PORTALS}
        marks.update({p: (220, 40, 40) for p in BOSSES.values()})
        marks.update({p: (250, 210, 40) for p in CHESTS})
        for y in range(H):
            for x in range(W):
                c = marks.get((x, y), (200, 175, 120) if z.is_walkable(x, y) else (60, 45, 35))
                for dy in range(6):
                    for dx in range(6):
                        px[x * 6 + dx, y * 6 + dy] = c
        im.save(sys.argv[sys.argv.index("--preview") + 1])
