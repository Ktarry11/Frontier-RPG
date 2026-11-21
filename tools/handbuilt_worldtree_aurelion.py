"""
Hand-built Aurelion (260x250): the Aetherian capital, the sky's first city (docs/worldtree_brief.md).

Kyle, 20 Nov 2026: "Aurelion must look PERFECT and grand", and "aurelion is ancient, we are new". His two pictures
(docs/zone_refs/aurelion_ref_spires.png, aurelion_ref_domes.png): a white-and-gold Spire Palace with blue crystal
windows, domed basilicas, circular gold-inlaid plazas with winged guardian statues, a grand avenue with a glowing blue
channel, arched bridges, districts on floating rock pouring waterfalls, airships.

THE SHAPE: rings round the Spire Palace, the way the Aetherians have always said it, seen from above. The palace stands
on its own isle in the middle. Around it the Inner Ring, broken into four great arcs, and around that the Outer Ring,
broken into six, with open sky between every ring and every arc, and broad white bridges across every gap. Out past
the north-west arc, what's left of the Eighth Ring: broken stubs of an arc that fell, a long time ago. Down the middle
from the south, the Grand Avenue runs straight from the sky-bridge to the palace stair, with the glowing channel down
its centre falling off each ring's edge into the sky. Every pool and channel spills off an edge (the wellstones).

    THE PALACE ISLE ....... the Spire Palace (the council meets in its hall, not here: the palace is the city's oldest
                            stone, and its keepers')
    THE COUNCIL RING ...... inner north: the Council Hall of the High Houses, and the houses' towers
    THE ACADEMIES ......... inner east: the academy, the spiral library, the magisters' hall, the amphitheatre
    THE GARDENS ........... inner west: the great conservatory's lawns, silver groves and gold orchards
    THE GRAND PLAZA ....... inner south: the round plaza on the avenue, the light fountain, the winged guardians
    THE BRIDGEFOOT ........ outer south: where the sky-bridge lands; the inn, the bank, the auction house and the mail
                            together, and the skiffs (Kyle, 17 Nov: "an auction house, a bank, and a mailbox close
                            together"; the brief: inn and flight path with them)
    THE GROUND EMBASSY .... outer south-east: the hall the council opened for the ground, and the guest quarter
    THE SKYDOCKS .......... outer north-east: the airship docks and the sky-forge
    THE NORTH GATE ........ outer north: the great ring-gate, the road north to the low country (later)
    THE EIGHTH'S REST ..... outer north-west: the survivors of the Eighth Ring, and the memorial
    THE TRAINERS' RING .... outer south-west: the trainers' halls, every class and the trades
    THE EIGHTH RING ....... the fallen ring's stubs, past the north-west arc

A SKY MAP and a TOWN: safe everywhere, no gathering. The baker cuts the drop out and hangs rock under every ring.

HARD CONTRACTS (world/portal_manager.py)
  portals  The Celestial Expanse (130,246) <-> the sky-bridge's foot (226,2); later: the north road (130,4)
"""
import math

import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_worldtree_sunward_crown import _fbm, _puff, _poly, _seg_dist, _ell, smoothstep_np  # noqa: F401

BAKED_DIR = "assets/tiles/sky/baked_aurelion"
NAME = "Aurelion"
W, H = 260, 250
SKP = "assets/tiles/sky/props/"
BLD = "assets/buildings/"

C = (130.0, 120.0)
PORTALS = {(130, 246): "The Celestial Expanse"}
ARRIVALS = [(130, 241)]
LATER_PORTALS = {(130, 4): "The North Road"}
START = (130, 241)        # the sky-bridge's landing: everything must be reachable from here

# ---------------------------------------------------------------- the rings
PALACE_R = 24.0
INNER = (36.0, 62.0)                       # the Inner Ring's radii
OUTER = (77.0, 108.0)                      # the Outer Ring's radii
INNER_GAPS = (45, 135, 225, 315)           # sky between the Inner Ring's four arcs (degrees, screen: 0 east, 90 south)
OUTER_GAPS = (0, 60, 120, 180, 240, 300)   # sky between the Outer Ring's six arcs
GAP_HW = (5.0, 6.0)                        # half-width of the sky in each ring's gaps
#: the fallen Eighth Ring: two broken stubs past the north-west arc, one reachable by its old span
EIGHTH_STUBS = [(118.0, 126.0, 205.0, 222.0), (118.0, 126.0, 231.0, 242.0)]
#: round terraces built out from the Outer Ring's rim, the way the pictures show them: a plaza on each, pouring falls
BASTIONS = [(30, 111.0, 12.0), (150, 111.0, 12.0), (210, 111.0, 11.0), (330, 111.0, 12.0)]

#: bridges (points, half-width): palace to the Inner Ring at the four quarters, the Inner Ring to every Outer arc,
#: the sky-bridge in from the south edge, the north gate's stub, the span out to the Eighth Ring's stub
def _pt(r, deg):
    a = math.radians(deg)
    return (C[0] + r * math.cos(a), C[1] + r * math.sin(a))


SPANS = [(([_pt(PALACE_R - 4, d), _pt(INNER[0] + 4, d)]), 5.0) for d in (0, 90, 180, 270)]
#: the north arc's two bridges flank the Council Hall rather than running into its doors
SPANS += [(([_pt(INNER[1] - 4, d), _pt(OUTER[0] + 4, d)]), 5.0 if d == 90 else 4.6)
          for d in (30, 90, 150, 210, 256, 284, 330)]
SPANS += [
    ([(130, 249), (130, OUTER[1] + C[1] - 4)], 5.0),            # the sky-bridge's last stretch, onto the Bridgefoot
    ([(130, 0), (130, C[1] - OUTER[1] + 4)], 4.6),              # the north road's stub, past the ring-gate
    ([_pt(OUTER[1] - 4, 214), _pt(120, 214)], 4.0),             # the old span out to the Eighth Ring's stub
]


def _ring(gx, gy, r0, r1, gaps, gap_hw, wob):
    dx, dy = gx - C[0], gy - C[1]
    r = np.hypot(dx, dy) + wob
    d = np.maximum(r0 - r, r - r1)
    for g in gaps:
        a = math.radians(g)
        # distance from the gap's radial line, inside the ring's radii
        along = dx * math.cos(a) + dy * math.sin(a)
        perp = np.abs(-dx * math.sin(a) + dy * math.cos(a))
        cut = gap_hw - perp
        d = np.where((along > 0) & (cut > 0), np.maximum(d, cut), d)
    return d


def _arc(gx, gy, r0, r1, a0, a1, wob):
    dx, dy = gx - C[0], gy - C[1]
    r = np.hypot(dx, dy) + wob
    ang = (np.degrees(np.arctan2(dy, dx)) + 360) % 360
    mid, half = (a0 + a1) / 2, (a1 - a0) / 2
    da = np.abs((ang - mid + 180) % 360 - 180) - half
    return np.maximum.reduce([r0 - r, r - r1, da * np.radians(1) * r])


def _rock_raw(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    wob = 1.2 * _puff(gx, gy, 3.3) + 0.5 * np.sin(0.21 * gx + 0.17 * gy)
    c = np.hypot(gx - C[0], gy - C[1]) + wob - PALACE_R
    c = np.minimum(c, _ring(gx, gy, *INNER, INNER_GAPS, GAP_HW[0], wob))
    c = np.minimum(c, _ring(gx, gy, *OUTER, OUTER_GAPS, GAP_HW[1], wob))
    for (r0, r1, a0, a1) in EIGHTH_STUBS:
        c = np.minimum(c, _arc(gx, gy, r0, r1, a0, a1, 1.6 * wob))
    for (d, r, rad) in BASTIONS:
        x, y = _pt(r, d)
        c = np.minimum(c, np.hypot(gx - x, gy - y) + 0.6 * wob - rad)
    return c


def span_mask(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    out = np.full(np.shape(gx), 99.0)
    for pts, hw in SPANS:
        out = np.minimum(out, _seg_dist(gx, gy, pts) - hw)
    return out


# ---------------------------------------------------------------- cached, smoothed fields
_GRID_R = 4
_CACHE = {}
_SMOOTH_TILES = {"rock": 1.0}


def _cached(name, fn):
    if name not in _CACHE:
        xs = (np.arange((W + 4) * _GRID_R) + 0.5) / _GRID_R - 2.0
        ys = (np.arange((H + 4) * _GRID_R) + 0.5) / _GRID_R - 2.0
        GX, GY = np.meshgrid(xs, ys)
        _CACHE[name] = np.asarray(fn(GX, GY), np.float32)
    return _CACHE[name]


def _sample(arr, gx, gy):
    from scipy.ndimage import map_coordinates
    fx = (np.asarray(gx, float) + 2.0) * _GRID_R - 0.5
    fy = (np.asarray(gy, float) + 2.0) * _GRID_R - 0.5
    shp = np.shape(fx)
    return map_coordinates(arr, [np.ravel(fy), np.ravel(fx)], order=1, mode="nearest").reshape(shp)


def _smoothed(name, raw):
    def fn(GX, GY):
        from scipy.ndimage import gaussian_filter
        return gaussian_filter(np.asarray(raw(GX, GY), np.float32), _SMOOTH_TILES[name] * _GRID_R, mode="nearest")
    return _cached(name, fn)


def rock_field(gx, gy):
    return _sample(_smoothed("rock", _rock_raw), gx, gy)


def _sea_exact(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    land = np.minimum(rock_field(gx, gy), span_mask(gx, gy) + 0.1 * _fbm(gx, gy, 1.0))
    edge = np.maximum.reduce([-1.0 - gx, gx - (W - 1.0), -1.0 - gy, gy - (H - 1.0)])
    return np.maximum(land, edge * 3.0)


def sea(gx, gy):
    """The drop: everything that isn't ring, isle or bridge."""
    return _sample(_cached("sea", _sea_exact), gx, gy)


def cloudness(gx, gy):
    return np.zeros(np.shape(np.asarray(gx, float)))


#: the renderer's sky and the baker's cut: the golden sky, the sun strong
SKY = {"far": "sky_far_gold", "parallax": 0.35, "drift": 3.0, "wisps": 0.25, "sun": 0.3, "far_tiles": 10,
       "underside": 6.0, "cloud": cloudness, "cloud_lift": 0.0}


def plaza_field(P, wp):
    """The white bridges, painted over the gaps only."""
    from tools.bake_ashenvale import smoothstep
    over_the_gap = smoothstep(-1.5, 0.5, rock_field(P.gx, P.gy))
    return 1.9 * (1.0 - smoothstep(-0.4, 1.2, span_mask(P.gx, P.gy))) * over_the_gap


ISLETS = []
#: the Gardens' reflecting pool, the plaza's round basin, the embassy's fountain pool, the Eighth's Rest memorial pool
LAKES = {"pools": [(80, 120, 7, 5, 0.3, 0.7), (60, 74, 5, 4, 0.2, 2.1), (210, 168, 4, 3, 0.0, 1.3)]}
DEEP_SHRINK = {"pools": 4.0}
#: the Grand Avenue's glowing channel, in two lengths, each falling off its ring's edge into the sky
RIVERS = [([(130, 222), (130, OUTER[0] + C[1] - 2)], 1.6, -2.0),
          ([(130, 167), (130, INNER[0] + C[1] - 2)], 1.6, -2.0)]   # out of the light fountain, north off the edge
FORDS = []

MESAS = []
RIDGES = []
#: silver groves and gold orchards in the Gardens, a few trees in the courts
WOODS = [(72, 106, 6, 4, 0.3, 1.0), (88, 140, 5, 3, 0.6, 2.0), (70, 132, 4, 3, 0.1, 0.6)]
BELTS = []
CLEARINGS = [
    (130, 241, 6, 4),           # the sky-bridge's landing
    (130, 212, 22, 10),         # the Bridgefoot's square
    (130, 170, 14, 11),         # the Grand Plaza
    (130, 108, 14, 10),         # before the Spire Palace
    (130, 72, 14, 7),           # before the Council Hall
    (180, 120, 12, 14),         # the Academies' court
    (210, 168, 12, 9),          # the Ground Embassy
    (208, 72, 12, 9),           # the Skydocks
    (130, 26, 12, 7),           # the North Gate
    (52, 74, 12, 9),            # the Eighth's Rest
    (52, 166, 14, 10),          # the Trainers' Ring
]
#: the gardens' lawns ("bluebell"), the plazas' and the palace's marble ("paved"), the Eighth's Rest's worn stone
#: ("burned")
BLUEBELL_PATCHES = [(78, 120, 14, 18), (60, 96, 6, 5)]
#: whole lawns (tools/bake_ashenvale.py paints them solid): the Gardens' terraces round the reflecting pool, and a
#: lawn either side of the Council Hall's court
LAWN_PATCHES = [(81, 103, 10, 6), (78, 139, 10, 7), (91, 121, 4, 9), (69, 121, 3, 8), (111, 71, 6, 3), (149, 71, 6, 3)]
PAVED_PATCHES = [(130, 170, 13, 11), (130, 110, 16, 12), (130, 74, 16, 8), (130, 212, 20, 9), (180, 120, 12, 12)]
BURNED_PATCHES = [(52, 74, 14, 12), (44, 40, 10, 8)]
CORRUPT_PATCHES = []
LUSH = 0.2
GRADE = None
DROP = None

GAPS = [("ell", 130, 241, 5, 3)]

#: the roads: the Grand Avenue north from the sky-bridge to the palace, and a ring road round each ring
ROADS = {
    "avenue_out":  ([(130, 244), (130, 202)], 3.0),
    "avenue_in":   ([(130, 190), (130, 150)], 3.0),
    "palace_stair": ([(130, 140), (130, 126)], 2.6),
}


def _arc_road(r, a0, a1, step=10):
    pts = [_pt(r, a) for a in np.arange(a0, a1 + 0.1, step)]
    return [(round(x, 1), round(y, 1)) for x, y in pts]


#: the ring roads run along each ring's inner edge, so the great buildings stand on the outer side looking out
for i, (a0, a1) in enumerate([(-36, 36), (54, 126), (144, 216), (234, 306)]):
    ROADS[f"inner_{i}"] = (_arc_road(INNER[0] + 5.5, a0, a1), 2.2)
for i, (a0, a1) in enumerate([(9, 51), (69, 111), (129, 171), (189, 231), (249, 291), (309, 351)]):
    ROADS[f"outer_{i}"] = (_arc_road(OUTER[0] + 6.5, a0, a1, 8), 2.4)


class _Spec(E.Spec):
    """Groves only on the rings, never out over the drop; the avenue's water is a built channel."""
    canal = True

    def woods_raw(self, gx, gy):
        out = super().woods_raw(gx, gy)
        return np.minimum(out, -(np.asarray(rock_field(gx, gy)) + 3.0))


SPEC = _Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
             mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
             rim={}, rock_rim={}, gaps=GAPS, fords=FORDS, thicket=(0.99, 10.0, 2.0))

#: everyone in Aurelion (tools/build_aurelion.py writes their records)
NPC_POSITIONS = {
    # the Bridgefoot: the gate, and the inn, the bank, the auction house, the mail and the skiffs round one square
    "au_gate_warden":      (123, 227),
    "au_innkeeper":        (112, 220),
    "au_banker":           (150, 215),
    "au_auctioneer":       (147, 226),
    "au_flight_master":    (106, 224),
    "au_provisioner":      (118, 208),
    "au_trader":           (141, 207),
    "au_smith":            (158, 199),
    # the Grand Plaza: the herald, and the pair of allies, waiting
    "au_plaza_herald":     (121, 171),
    "au_ilaren":           (139, 175),
    "au_leandro":          (126, 177),
    # the Spire Palace
    "au_palace_keeper":    (123, 131),
    # the Council Ring
    "au_first_speaker":    (130, 73),
    "au_councillor_lens":  (119, 76),
    "au_councillor_memory": (141, 76),
    "au_quartermaster":    (112, 88),
    # the Academies and the Gardens
    "au_academy_master":   (175, 114),
    "au_gardener":         (85, 113),
    # the Ground Embassy
    "au_ambassador":       (210, 180),
    "au_embassy_aide":     (202, 182),
    # the Skydocks and the North Gate
    "au_dockmaster":       (214, 76),
    "au_north_warden":     (124, 31),
    # the Eighth's Rest
    "au_eighth_elder":     (52, 88),
    "au_soup_cook":        (44, 92),
    # the Trainers' Ring: every class, and the trades in their pairs
    "ct_aurelion":         (52, 168),
    "pt_au_forge":         (38, 158),
    "pt_au_gems":          (40, 180),
    "pt_au_hide":          (60, 156),
    "pt_au_herbs":         (64, 172),
    "pt_au_cloth":         (56, 182),
    "pt_au_wood":          (29, 178),
    "pt_au_cook":          (68, 194),
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("Aurelion", 0, 0, W, H, None),
    ("The Bridgefoot", 92, 192, 76, 58, None),
    ("The Ground Embassy", 176, 140, 70, 60, None),
    ("The Skydocks", 176, 40, 74, 60, None),
    ("The North Gate", 92, 0, 76, 46, None),
    ("The Eighth's Rest", 14, 40, 70, 60, None),
    ("The Trainers' Ring", 14, 140, 70, 60, None),
    ("The Eighth Ring", 0, 0, 56, 52, None),
    ("The Council Ring", 96, 54, 68, 34, None),
    ("The Academies", 164, 84, 32, 72, None),
    ("The Gardens", 64, 84, 32, 72, None),
    ("The Grand Plaza", 96, 152, 68, 34, None),
    ("The Spire Palace", 104, 94, 52, 52, None),
]

TREES = {
    "big":   [(SKP + "sk_silver_tree.png", 8)],
    "mid":   [(SKP + "sk_blossom_tree.png", 6), (SKP + "sk_fruit_tree.png", 6)],
    "small": [(SKP + "sk_bellflowers.png", 2), (SKP + "sk_heather_clump.png", 3)],
    "woods": [(SKP + "sk_silver_tree.png", 8), (SKP + "sk_blossom_tree.png", 6)],
}


def _grid():
    ys, xs = np.mgrid[0:H, 0:W]
    return xs + 0.5, ys + 0.5


def drop_mask(L=None):
    return sea(*_grid()) > 0


def on_a_span(pad=1.5):
    return span_mask(*_grid()) < pad


def open_the_drop(L):
    z = L.z
    for y, x in zip(*np.nonzero(drop_mask(L))):
        z.set_tile(int(x), int(y), "grass", "base")
        z.set_tile(int(x), int(y), "cliff", "collision")


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "Aurelion, the Aetherian capital: rings of white and gold stone round the Spire Palace, "
                             "older than anyone's memory, with the sky between them and the Eighth Ring long fallen.",
                             "Eastern Kingdoms - The World Tree", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    L.z.is_town = True          # a capital: safe, no gathering, the town's rules
    E.terrain(L)
    open_the_drop(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.seal_unreachable(L, START)
    dress(L)
    E.build_free_mask(L, NPC_POSITIONS.values())
    for lm in L.z.landmarks:
        ax, ay, w, h = lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]
        L.free_mask[max(0, ay):ay + h + 1, max(0, ax - 1):ax + w + 1] = False
    L.free_mask[drop_mask(L)] = False
    L.free_mask[on_a_span()] = False
    E.scatter_trees(L, TREES, seed=5501, spacing=13.0, grove_keep=0.6)
    E.seal_unreachable(L, START)
    E.register_subzones(L, SUBZONES)
    sky_islands(L)
    return L


def sky_islands(L):
    """The city's own islands out in the sky, past the rings: drawn, not walked (the landmark sprites carry their own
    rock and falls). Added after everything else so nothing is placed round them."""
    for (name, x, y, h) in [("ae_palace_crown", 226, 214, 30), ("ae_city_falls", 26, 214, 28),
                            ("ae_underspire", 232, 22, 28), ("ae_great_conservatory", 238, 120, 22)]:
        path = f"{BLD}{name}.png"
        from PIL import Image
        iw, ih = Image.open(path).size
        w = max(1, round(h * iw / ih))
        L.z.add_landmark(path, x - w // 2, y - h + 1, w, h, solid=False)


def dress(L):
    def B(n, x, y, h, **kw):
        kw.setdefault("solid", "core")
        kw.setdefault("nudge", 2)
        return L.prop(n, x, y, h, path_dir=BLD, **kw)

    def S(n, x, y, h, **kw):
        kw.setdefault("solid", "core")
        kw.setdefault("nudge", 2)
        return L.prop(n, x, y, h, path_dir=SKP, **kw)

    def rim(x, y, dx, dy):
        while 0 < x + dx < W - 1 and 0 < y + dy < H - 1 and float(sea(x + dx, y + dy)) < -0.5:
            x, y = x + dx, y + dy
        return x, y

    # ---- falls: the channel off both ring edges, the pools off theirs, and the rings' rims pouring into the sky
    S("sk_edge_falls", 130, int(OUTER[0] + C[1]) - 1, 6, solid=False, allow_overlap=True)
    S("sk_edge_falls", 130, int(INNER[0] + C[1]) - 1, 6, solid=False, allow_overlap=True)
    for (px, py, dx, dy) in [(80, 120, 1, 0), (60, 74, 0, -1), (210, 168, 1, 0)]:
        S("sk_edge_falls", *rim(px, py, dx, dy), 5, solid=False, allow_overlap=True)
    for d in (20, 100, 160, 200, 250, 290, 340):
        x, y = _pt(OUTER[1] - 1.5, d)
        S("sk_edge_falls", int(x), int(y), 6, solid=False, allow_overlap=True, nudge=1)

    # ---- the Spire Palace on its isle, the stair up from the avenue, winged columns flanking it
    B("ae_aurelion_spire", 130, 116, 26, allow_overlap=True)
    for dx in (-9, 9):
        B("ae_winged_column", 130 + dx, 132, 7)
    B("ae_guard_statue", 118, 124, 5)
    B("ae_guard_statue", 142, 124, 5)
    # ---- the Council Ring (inner north): the Council Hall of the High Houses, the houses' towers either side
    B("ae_council_hall", 130, 68, 18, allow_overlap=True)
    for (x, y) in [(104, 82), (156, 82)]:
        B("ae_residence_tower", x, y, 9)
    B("ae_magister_statue", 114, 86, 6)
    B("ae_magister_statue", 146, 86, 6)
    # ---- the Academies (inner east)
    B("ae_academy", 178, 104, 10)
    B("ae_spiral_library", 190, 122, 11)
    B("ae_magister_hall", 180, 140, 10)
    B("ae_amphitheatre", 186, 132, 7)
    B("ae_star_globe", 186, 108, 3)
    # ---- the Gardens (inner west)
    B("ae_conservatory", 82, 102, 9)
    B("ae_gold_orchard", 74, 146, 7)
    B("ae_garden_pavilion", 90, 134, 6)
    # ---- the Grand Plaza (inner south): the light fountain in the middle, winged guardians round it, colossi at the
    #      avenue's ends holding up their rings of stone
    B("ae_light_fountain", 130, 171, 8, allow_overlap=True, road_ok=True)
    for d in (30, 150, 210, 330):
        x, y = 130 + 12 * math.cos(math.radians(d)), 170 + 9 * math.sin(math.radians(d))
        B("ae_winged_column", int(x), int(y), 7)
    B("ae_colossus", 114, 180, 11)
    B("ae_colossus", 146, 180, 11)
    for y in (156, 162):
        B("ae_avenue_column", 124, y, 6)
        B("ae_avenue_column", 136, y, 6)
    # ---- the Bridgefoot (outer south): the inn, the bank, the auction house and the mail round one square; the skiffs
    B("ae_great_ring_gate", 130, 234, 13, road_ok=True, allow_overlap=True, solid=False)
    B("ae_guesthouse", 108, 214, 10)
    B("ae_vault", 154, 210, 10)
    B("ae_exchange", 152, 224, 10)
    B("ae_mail_pylon", 142, 214, 5)
    B("ae_skiff_dock", 100, 220, 6)
    B("ae_orb_lantern", 120, 204, 4)
    B("ae_orb_lantern", 140, 204, 4)
    B("ae_kiosk_crystal", 116, 222, 4)
    # ---- the Ground Embassy (outer south-east)
    B("ae_ground_embassy", 218, 174, 11)
    B("ae_townhouses", 228, 150, 9)
    B("ae_townhouses", 198, 194, 9)
    # ---- the Skydocks (outer north-east): the sky-forge, the airships moored at the rim
    B("ae_sky_forge", 206, 62, 10)
    B("ae_airship_dock", 222, 82, 10)
    B("ae_airship_great", 226, 58, 10, allow_overlap=True)
    B("ae_crystal_crates", 208, 88, 3)
    B("ae_supply_crates", 212, 62, 3)
    # ---- the North Gate (outer north)
    B("ae_ring_gate", 130, 20, 11, road_ok=True, allow_overlap=True, solid=False)
    B("ae_wall_tower", 112, 30, 9)
    B("ae_wall_tower", 148, 30, 9)
    B("ae_forge", 104, 22, 7)
    # ---- the Eighth's Rest (outer north-west): the survivors' pavilions, the memorial, soup tables
    B("ae_crystal_memorial", 54, 80, 7)
    B("ae_refugee_pavilion", 40, 66, 6)
    B("ae_refugee_pavilion", 66, 60, 6)
    B("ae_soup_table", 46, 86, 3)
    B("ae_damaged_house", 30, 90, 7)
    # ---- the Eighth Ring: the fallen ring's broken landmark out past its stubs
    B("ae_broken_ring", 44, 40, 7, allow_overlap=True)
    # ---- the Trainers' Ring (outer south-west)
    B("ae_trainers_hall", 50, 160, 10)
    B("ae_forge", 34, 150, 7)
    B("ae_laboratory", 64, 190, 8)
    B("ae_engineer_guildhall", 30, 168, 9)

    # ---- the city lived in (look-dev, 21 Nov 2026): lamps down the avenue, benches and planters round the plaza,
    #      braziers at the palace stair, and houses filling every outer arc behind its great buildings
    B("ae_lamp_post", 123, 222, 5)
    B("ae_lamp_post", 137, 222, 5)
    for (x, y) in [(111, 165), (149, 165)]:
        B("ae_planter", x, y, 3)
    for (x, y) in [(123, 160), (137, 160)]:
        B("ae_bench", x, y, 2)
    B("ae_ceremonial_brazier", 124, 141, 4)
    B("ae_ceremonial_brazier", 136, 141, 4)
    #: the people who stand here, and the two recruits (tools/build_sheet6_recruits.py PINNED): nothing is drawn over them
    people = list(NPC_POSITIONS.values()) + [(206, 190), (170, 126)]

    def clear_spot(x, y, r):
        """Nobody standing under where the sprite will be, and no building's base within r: fillers never crowd the
        set pieces or the people."""
        if any(abs(x - px) <= 4 and -9 <= py - y <= 2 for (px, py) in people):
            return False
        return all(math.dist((x, y), (lm["anchor_x"] + lm["width_tiles"] / 2, lm["anchor_y"] + lm["height_tiles"]))
                   >= r for lm in L.z.landmarks)

    def first_clear(name, h, r, angles, radius=54):
        for a in angles:
            x, y = _pt(radius, a)
            if clear_spot(x, y, r):
                return B(name, int(x), int(y), h)
        return False

    # the Council Ring: the houses' archive and the aurora tower at the arc's ends
    B("ae_archive", *map(int, _pt(54, 248)), 9)
    B("ae_aurora_tower", *map(int, _pt(54, 292)), 12)
    # the Academies: the observatory and the great telescope out on the arc's ends
    first_clear("ae_observatory", 10, 13, (-26, -30, -34, -22))
    first_clear("ae_great_telescope", 8, 11, (26, 30, 34, 22))
    first_clear("ae_armillary", 4, 6, (8, -8, 12, -12), radius=50)
    # the Gardens: silver groves and crystal trees round the reflecting pool, the pool pavilion on its bank
    B("ae_silver_grove", *map(int, _pt(54, 160)), 7)
    first_clear("ae_crystal_tree", 7, 9, (200, 205, 210, 195))
    B("ae_pool_pavilion", 88, 124, 6)
    B("ae_sun_dial", 96, 112, 3)
    # the outer arcs: houses on the far side of each ring road
    HOMES = ("ae_house_medium", "ae_residence_large", "ae_terrace_mansion", "ae_house_small")
    for i, (mid, skip) in enumerate([(30, ()), (90, (90,)), (150, ()), (210, ()), (270, (270,)), (330, ())]):
        for j, da in enumerate((-19, -8, 8, 19)):
            a = mid + da
            if any(abs(a - s) < 12 for s in skip):
                continue
            x, y = _pt(101, a)
            if clear_spot(x, y, 9):
                B(HOMES[(i + j) % len(HOMES)], int(x), int(y), 8, nudge=3)
        for da in ((-14, 14) if skip else (-14, 0, 14)):
            x, y = _pt(OUTER[0] + 10.5, mid + da)
            if clear_spot(x, y, 9):
                B("ae_lamp_post", int(x), int(y), 5, nudge=1)


def register_baked(zone):
    import os
    zone.sky = {k: v for k, v in SKY.items() if not callable(v)}
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.webp"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_aurelion():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS) + list(LATER_PORTALS),
                              npc=list(NPC_POSITIONS.values()))
