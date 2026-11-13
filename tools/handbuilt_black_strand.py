"""
Hand-built The Black Strand (150x120): the layer under The Dry Deep. 50-53.

Kyle, 13 Nov 2026: "in the cave, i want an even deeper layer going down to a zone that will be level
50-53. Entire zone with a small 'town' - (seperate map) of dark iron dwarfs. There wont be a flight
master but this can have an inn. The deeper layer can be mix of black sand and silithid and some
glowing mushrooms." And the same afternoon: "make deeper layer kind of like a gorgeous mix of dark
sand, fungi, and silithid". The town is Onyxhollow (his name) and the way down is "at the end of the
descent" - the last room of the Dry Deep, past The Weight of the Floor.

WHAT IT IS. The Dry Deep is the bed of a sea that drained. This is where that sea's SHORE went: the
sand it left, a long way down, black because nothing has bleached it in an age. Three things live on
it and the zone is the three of them meeting -

    THE SAND   is the ground everywhere. One texture, dark and quiet, so the two colours on top of
               it can be loud.
    FUNGI      came for what the sea left behind. Blue-green light, thickest in the south-west
               (the Lantern Wood) and thinning to single caps everywhere else.
    SILITHID   came for the fungi. Amber resin, thickest in the south-east (the Chitin Reach) and
               reaching back toward the wood in fingers, because that is what they are eating.

    and THE DARK IRON, who came for neither and dug a town into the middle of it. Onyxhollow's
    gate is in the one chamber both of the others have been kept out of.

THREE COLOURS ON BLACK is the whole art direction: teal light, amber light, and the red of a Dark
Iron brazier where the road is. Less is more (Kyle, 13 Nov, of the Flats: "Its just TOO many tiles")
- there is one ground texture per thing and the mixing is done by PLACE, not by blending.

AN OPEN ZONE, UNDERGROUND. is_cave False: per-subzone tables, rares on the subzone roll, its own
gathering pool, like the Abyssal Sands above it. The walls are cave rock and it is built with the
cave tools, but it is somewhere you quest across, not a hole with a boss at the end.

HARD CONTRACT (world/portal_manager.py):
    (20, 11)  <-> The Dry Deep (97, 40)   - up the last descent
    (84, 52)  <-> Onyxhollow              - the town gate. NOT YET A DOOR: see PORTALS.
"""
import numpy as np

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked, pool_fields, _apply_pools
from tools.tirisfal_kit import wob, seg_dist

KEY = "black_strand"
NAME = "The Black Strand"
DESC = ("The shore of a sea that drained, a long way under the desert. Black sand, the light of "
        "things that grow without any, and something that eats them.")
REGION = "Kalimdor - Tanaris"
W, H = 150, 120
BAKED = "assets/tiles/black_strand/baked"
BAKED_DIR = BAKED

UDP = "assets/tiles/underdark/props/"
BSP = "assets/tiles/broodspiral/props/"
SFP = "assets/tiles/shimmering_flats/props/"
BLD = "assets/buildings/"

UP = (20, 11)                 # to the Dry Deep
START = (20, 14)
TOWN_GATE = (84, 52)          # to Onyxhollow
TOWN_ARRIVAL = (84, 55)
#: The town gate becomes a door when Onyxhollow's map exists; until then it is NOT a portal tile,
#: because a portal that leads nowhere is a bug (tools/qa_portals.py) and not a placeholder.
PORTALS = {UP: "The Dry Deep"}
ARRIVALS = [START, TOWN_ARRIVAL]

#: (name, cx, cy, rx, ry). West is the way in; fungi south-west, hive south-east, the dwarves'
#: castoffs north-east, and the gate in the middle of all of it.
#: Kyle, 13 Nov, on the first pass: "we need to increase playing area massively....maybe 30% more?
#: I do like the cave zone, but i still want it 'open zone' as well." So the rooms are a fifth
#: wider each way and the passages between them are three times the width - they are not passages
#: any more, the rooms run into each other, and what is left of the rock between them stands in
#: the floor as islands you walk round. One cavern with a shape, not eight rooms with corridors.
GROW = 1.2
_ROOMS = [
    ("The Bottom Step",       20, 20, 12, 10),
    ("The Ash Dunes",         52, 34, 25, 17),
    ("The Lantern Wood",      34, 82, 24, 20),
    ("Onyxhollow Gate",       84, 63, 15, 11),
    ("The Castout Diggings", 114, 26, 22, 14),
    ("The Last Water",        77, 101, 17, 11),
    ("The Chitin Reach",     121, 80, 19, 20),
    ("The Royal Cell",       136, 108, 9, 7),
]
CHAMBERS = [(n, cx, cy, round(rx * GROW, 1), round(ry * GROW, 1)) for (n, cx, cy, rx, ry) in _ROOMS]
IDX = {c[0]: i for i, c in enumerate(CHAMBERS)}

#: (a, b, half-width). Two ways to everywhere except the Royal Cell, which has one door.
TUNNELS = [
    (0, 1, 7.0), (1, 2, 7.5), (1, 3, 8.0), (1, 4, 6.5), (3, 4, 6.5), (3, 6, 7.5),
    (2, 5, 7.0), (5, 6, 6.5), (3, 5, 6.5), (2, 3, 7.0), (6, 7, 4.0),
]

#: Rock left standing in the big rooms (cx, cy, rx, ry) - a cavern this wide has pillars, and a
#: floor with nothing to walk round is a car park.
PILLARS = [
    (44, 30, 3.2, 2.6), (60, 40, 2.8, 3.4), (56, 26, 2.4, 2.0), (38, 40, 2.2, 2.4),
    (28, 76, 3.0, 2.6), (40, 90, 2.6, 3.2), (26, 92, 2.2, 2.0), (44, 74, 2.0, 2.2),
    (108, 22, 2.8, 2.4), (122, 30, 2.6, 2.6), (116, 72, 3.0, 2.8), (126, 88, 2.8, 3.2),
    (114, 90, 2.2, 2.2),
    (68, 52, 3.4, 2.6), (40, 58, 3.0, 2.4), (58, 70, 2.8, 3.0), (98, 44, 3.2, 2.6), (100, 78, 2.6, 3.0),
    (60, 90, 2.6, 2.4), (96, 96, 3.0, 2.4), (74, 80, 2.4, 2.2), (30, 34, 2.4, 2.0), (132, 60, 2.6, 2.4),
]

#: The Last Water: what did not drain. (cx, cy, rx, ry, phase) - shallow rim, deep middle.
POOLS = [(77, 102, 10.5, 6.0, 0.9)]
#: Small lit pools in the wood. Shallow only, you walk through them.
GLOW_POOLS = [(27, 84, 3.2, 2.4, 2.0), (41, 80, 2.6, 2.2, 0.4), (33, 95, 2.8, 2.0, 1.3)]

#: The slag road: the Bottom Step to the gate, and the gate to the Diggings. (points, half-width)
ROADS = [
    ([(20, 16), (24, 24), (34, 30), (50, 36), (66, 46), (78, 58), (84, 58), (84, 54)], 1.3),
    ([(86, 58), (96, 48), (104, 36), (112, 28)], 1.1),
]

SUBZONES = [(n, int(cx - rx - 2), int(cy - ry - 2), int(2 * rx + 4), int(2 * ry + 4)) for (n, cx, cy, rx, ry) in CHAMBERS]
CHESTS = [(62, 22), (16, 84), (132, 16), (90, 108), (108, 96), (141, 110)]
NPC_POSITIONS = {}


def _tunnel_pts(a, b):
    _n, ax, ay, _rx, _ry = CHAMBERS[a]
    _n2, bx, by, _rx2, _ry2 = CHAMBERS[b]
    mx, my = (ax + bx) / 2 + (by - ay) / 7.0, (ay + by) / 2 - (bx - ax) / 7.0
    return [(ax, ay), (mx, my), (bx, by)]


def open_field(gx, gy):
    """> 0 where there is floor, in tiles from the wall. Shared with the baker's regions."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    o = np.full(np.shape(gx), -99.0)
    rough = 1.6 * wob(gx * 0.9, gy * 0.9) + 0.9 * wob(gx * 2.3 + 5.0, gy * 2.1)
    for (_n, cx, cy, rx, ry) in CHAMBERS:
        d = (1.0 - np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)) * min(rx, ry)
        o = np.maximum(o, d + rough)
    for (a, b, hw) in TUNNELS:
        pts = _tunnel_pts(a, b)
        for (p, q) in zip(pts, pts[1:]):
            o = np.maximum(o, hw - seg_dist(gx, gy, p[0], p[1], q[0], q[1]) + 0.45 * rough)
    for (cx, cy, rx, ry) in PILLARS:
        d = (1.0 - np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)) * min(rx, ry)
        o = np.minimum(o, -(d + 0.5 * wob(gx * 2.0, gy * 2.0)))
    # the doors are always open, whatever the noise did
    for (px, py) in list(PORTALS) + ARRIVALS + [TOWN_GATE]:
        o = np.maximum(o, 2.2 - np.hypot(gx - px, gy - py))
    edge = np.minimum(np.minimum(gx, W - gx), np.minimum(gy, H - gy))
    return np.minimum(o, edge - 2.0)


def road_dist(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    r = np.full(np.shape(gx), -99.0)
    for (pts, hw) in ROADS:
        for (p, q) in zip(pts, pts[1:]):
            r = np.maximum(r, hw - seg_dist(gx, gy, p[0], p[1], q[0], q[1]))
    return r


def region_field(name, gx, gy, grow=1.25):
    """~1 in the middle of a chamber, 0 at `grow` radii, for the baker and the scatter."""
    _n, cx, cy, rx, ry = CHAMBERS[IDX[name]]
    return np.clip(grow - np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2), 0.0, 1.0)


def fungus_field(gx, gy):
    """How much this ground belongs to the fungi, 0..1: the wood, the lake shore, and a thin
    scatter of it everywhere that is not hive or forge."""
    f = np.maximum(region_field("The Lantern Wood", gx, gy, 1.35),
                   0.75 * region_field("The Last Water", gx, gy, 1.3))
    return np.clip(f * 1.6, 0.0, 1.0)


def hive_field(gx, gy):
    """How much it belongs to the hive: the Reach, the Cell, and two fingers reaching west along
    the tunnels toward the wood and the water - toward the food."""
    h = np.maximum(region_field("The Chitin Reach", gx, gy, 1.3),
                   region_field("The Royal Cell", gx, gy, 1.5))
    for (a, b) in ((5, 6), (3, 6)):
        pts = _tunnel_pts(a, b)
        for (p, q) in zip(pts, pts[1:]):
            h = np.maximum(h, 0.8 * np.clip(1.0 - seg_dist(gx, gy, p[0], p[1], q[0], q[1]) / 5.0, 0, 1)
                           * np.clip((gx - 84.0) / 14.0, 0.0, 1.0))
    return np.clip(h * 1.6, 0.0, 1.0)


def forge_field(gx, gy):
    return np.clip(1.6 * np.maximum(region_field("The Castout Diggings", gx, gy, 1.25),
                                    0.9 * region_field("Onyxhollow Gate", gx, gy, 1.05)), 0.0, 1.0)


def build_black_strand():
    zone = Tilemap(NAME, W, H, DESC)
    zone.is_cave = False
    zone.region = REGION
    zone.fixed_spawns = False
    L = CaveLayout(zone, START)
    b = L.b
    ys, xs = np.mgrid[0:H, 0:W]
    o = open_field(xs + 0.5, ys + 0.5)
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if o[y, x] > 0:
                b._open(x, y)
    rd = road_dist(xs + 0.5, ys + 0.5)
    for y in range(H):
        for x in range(W):
            if rd[y, x] > 0 and zone.collision_layer[y][x] is None:
                zone.set_tile(x, y, "path", "base")
    _apply_pools(zone, POOLS)
    _apply_pools(zone, GLOW_POOLS, shallow_only=True)

    # seal anything the noise cut off, so nothing walkable is unreachable
    seen = L._reach()
    for y in range(H):
        for x in range(W):
            if (x, y) not in seen and zone.is_walkable(x, y):
                zone.set_tile(x, y, "rock", "collision")

    for (px, py) in PORTALS:
        zone.collision_layer[py][px] = None
        L.mark("portal", px, py)
    # A chest goes on the nearest floor to where it was aimed. The walls are noise, and a chest
    # aimed at a tile the noise closed would otherwise be a chest in solid rock.
    seen = L._reach()
    L.chests = []
    for (cx, cy) in CHESTS:
        best = min((t for t in seen if zone.base_layer[t[1]][t[0]] not in ("shallow_water", "deep_water")
                    and zone.interaction_layer[t[1]][t[0]] is None),
                   key=lambda t: (t[0] - cx) ** 2 + (t[1] - cy) ** 2)
        L.chests.append(best)
        L.mark("chest", *best)
    for (name, x, y, w, h) in SUBZONES:
        zone.add_subzone(name, max(0, x), max(0, y), w, h)
    zone.arrivals = list(ARRIVALS)
    return zone, L


def dress(zone, L):
    """Mushrooms, resin and iron - each thick at home and thin everywhere else."""
    rng = np.random.default_rng(5053)
    ys, xs = np.mgrid[0:H, 0:W]
    gx, gy = xs + 0.5, ys + 0.5
    fung, hive, forge = fungus_field(gx, gy), hive_field(gx, gy), forge_field(gx, gy)
    rd = road_dist(gx, gy)
    o = open_field(gx, gy)

    U = dict(where=UDP)
    S = dict(where=SFP)
    B = dict(where=BSP)
    D = dict(where=BLD)

    # the tall ones are the wood's trees: solid, on the rim, so the middle stays walkable
    tall = [("ud_shroom_tall_violet", 6), ("ud_shroom_canopy", 6), ("ud_shroom_squat_ochre", 4),
            ("ud_shroom_cluster_blue", 4)]
    small = [("ud_shroom_small", 2), ("ud_shroom_cluster_blue", 3), ("ud_fungal_node", 2),
             ("ud_shelf_fungus", 2), ("ud_fungal_shelf", 3)]
    # NOT sf_hive_mound: it was drawn for the salt flats and stands on a white salt apron, which on
    # black sand is a white patch under every mound.
    hive_big = [("sf_chitin_spire", 6, S), ("resin_pillar", 5, B), ("sf_chitin_spire", 4, S)]
    hive_small = [("sf_resin_growth", 3, S), ("sf_egg_cluster", 2, S), ("egg_sac_cluster", 3, B),
                  ("sf_carapace_heap", 3, S), ("carapace_pile", 2, B)]
    iron = [("di_slag_heap", 3), ("di_ore_cart", 3), ("di_rubble", 3), ("di_crane_hook", 4),
            ("di_cage", 4)]

    # LESS IS MORE (Kyle, 13 Nov, looking at the first dressed pass: "dont forget, sometimes less
    # is more with props!"). The first pass put 300 props down and the wood and the hive were
    # carpets. The ground already says which place this is - the light does - so the props only
    # have to punctuate it: under half as many, and the floor shows between them.
    n = dict(fungi=0, hive=0, iron=0, stone=0)
    # ---- set pieces
    # the foot of the descent: what the first people down left
    L.prop("ud_survey_tripod", 25, 20, 3, near_ok=True, **U)
    L.prop("sf_crate_stack", 15, 22, 3, **S)
    # braziers along the slag road, every so often, so the road is a line of red in the dark
    for (pts, _hw) in ROADS:
        for (p, q) in zip(pts, pts[1:]):
            steps = max(1, int(np.hypot(q[0] - p[0], q[1] - p[1]) // 9))
            for i in range(1, steps + 1):
                t = i / (steps + 1)
                bx, by = int(p[0] + (q[0] - p[0]) * t) + 2, int(p[1] + (q[1] - p[1]) * t) - 1
                L.prop("di_brazier", bx, by, 3, solid="base", fraction=0.3, **D)
    # ONYXHOLLOW GATE: the gatehouse stands over the portal, a tower either side, wall between
    L.prop("di_watchtower", TOWN_GATE[0] - 7, TOWN_GATE[1] + 4, 7, solid="base", fraction=0.4, near_ok=True, **D)
    L.prop("di_watchtower", TOWN_GATE[0] + 7, TOWN_GATE[1] + 4, 7, solid="base", fraction=0.4, near_ok=True, **D)
    L.prop("di_rune_obelisk", TOWN_GATE[0] - 3, TOWN_GATE[1] + 6, 4, solid="base", fraction=0.3, near_ok=True, **D)
    L.prop("di_rune_obelisk", TOWN_GATE[0] + 3, TOWN_GATE[1] + 6, 4, solid="base", fraction=0.3, near_ok=True, **D)
    L.prop("di_dwarf_statue", 84, 68, 5, solid="base", fraction=0.4, **D)
    # THE CASTOUT DIGGINGS: a working that was shut and has people in it who were not let back
    L.prop("di_mine_head", 118, 20, 8, solid="base", fraction=0.4, **D)
    L.prop("di_ruined_hall", 106, 30, 7, solid="base", fraction=0.4, **D)
    L.prop("di_ruined_tower", 128, 24, 7, solid="base", fraction=0.4, **D)
    L.prop("di_ruined_gate", 100, 24, 6, solid="base", fraction=0.3, **D)
    # THE ROYAL CELL
    L.prop("queens_throne", 138, 106, 6, solid="base", fraction=0.4, near_ok=True, **B)
    # the Last Water's shore
    for (x, y) in [(64, 98), (90, 100), (76, 93)]:
        L.prop("ud_glow_pool", x, y, 3, **U)

    def taken(x, y, pad=1):
        """Inside (or within `pad` of) something already placed. The set pieces go down first and
        the scatter keeps off them: the first build scattered an ore cart through the statue at
        the gate and a cage through a watchtower (tools/qa_building_overlap.py)."""
        for lm in zone.landmarks:
            if (lm["anchor_x"] - pad <= x < lm["anchor_x"] + lm["width_tiles"] + pad
                    and lm["anchor_y"] - pad <= y < lm["anchor_y"] + lm["height_tiles"] + pad + 2):
                return True
        return False

    for _ in range(5200):
        x, y = int(rng.integers(3, W - 3)), int(rng.integers(3, H - 3))
        if not zone.is_walkable(x, y) or rd[y, x] > -1.2 or taken(x, y):
            continue
        r = rng.random()
        f, h, g = fung[y, x], hive[y, x], forge[y, x]
        near_wall = o[y, x] < 3.0
        if h > 0.25 and r < 0.11 * h:
            if near_wall and rng.random() < 0.5:
                nm, ht, kw = hive_big[int(rng.integers(len(hive_big)))]
                ok = L.prop(nm, x, y, ht, solid="base", fraction=0.4, **kw)
            else:
                nm, ht, kw = hive_small[int(rng.integers(len(hive_small)))]
                ok = L.prop(nm, x, y, ht, **kw)
            n["hive"] += bool(ok)
        elif f > 0.25 and r < 0.13 * f:
            if near_wall or rng.random() < 0.22:
                nm, ht = tall[int(rng.integers(len(tall)))]
                ok = L.prop(nm, x, y, ht, solid="base", fraction=0.3, **U)
            else:
                nm, ht = small[int(rng.integers(len(small)))]
                ok = L.prop(nm, x, y, ht, **U)
            n["fungi"] += bool(ok)
        elif g > 0.3 and r < 0.035 * g:
            nm, ht = iron[int(rng.integers(len(iron)))]
            n["iron"] += bool(L.prop(nm, x, y, ht, **D))
        elif r < 0.014:
            # the thin scatter: a lone cap or a stalagmite on open black sand
            nm, ht = [("ud_shroom_small", 2), ("ud_stalagmites", 3), ("ud_lichen_boulder", 3),
                      ("ud_fungal_node", 2)][int(rng.integers(4))]
            n["stone"] += bool(L.prop(nm, x, y, ht, **U))

    L.dress_counts = n
    return zone, L


def verify(zone):
    import collections
    assert zone.is_cave is False
    seen = {START}
    q = collections.deque([START])
    while q:
        x, y = q.popleft()
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nn = (x + d[0], y + d[1])
            if 0 <= nn[0] < W and 0 <= nn[1] < H and nn not in seen and zone.is_walkable(*nn):
                seen.add(nn)
                q.append(nn)
    lost = [n for (n, cx, cy, _rx, _ry) in CHAMBERS
            if not any((cx + dx, cy + dy) in seen for dx in range(-3, 4) for dy in range(-3, 4))]
    assert not lost, f"chambers cut off from the way in: {lost}"
    for p in list(PORTALS) + ARRIVALS:
        assert any((p[0] + dx, p[1] + dy) in seen for dx in (-1, 0, 1) for dy in (-1, 0, 1)), \
            f"{p} cannot be reached"
    return dict(chambers=len(CHAMBERS), reachable=len(seen))


def finish(zone, L):
    return L.finish(list(PORTALS) + list(L.chests))


def build_black_strand_baked():
    zone, L = build_black_strand()
    dress(zone, L)
    finish(zone, L)
    return zone, L


def generate_black_strand():
    zone, _L = build_black_strand_baked()
    register_baked(zone, BAKED)
    return zone


if __name__ == "__main__":
    z, L = build_black_strand_baked()
    print(verify(z), L.dress_counts, "skipped", len(L.skipped))
