"""
Hand-built Celestial Expanse (300x260), levels 49-51: the open sky between the World Tree's crown and Aurelion
(docs/worldtree_brief.md: "Floating islands, sky rivers that fall from island to island, and ancient aerial ruins older
than anyone up here remembers"; threats: "The old sky ruins wake (Kharad-age machinery, sky-golems); Ascendancy patrols;
sky beasts"). Clear blue sky, the sun high.

THE SHAPE (Kyle, 20 Nov 2026: "Stop reusing the same shape"): beads on a falling river. Aurelion's water pours out of a
broken aqueduct at the north edge and becomes the Great Sky River, which runs south-west across one island, falls off its
edge onto the next, runs across that one and falls again, six islands in a string from the Spillway at the top to the
Last Falls, where it goes over the edge of the map into nothing. The Kharad's old stone spans cross each gap beside the
falls. Off the string: a ring of eight ruin islets orbiting a broken Kharad citadel (the Orbiting Ruins), the Silent
Forge on its own island to the west, the Ascendancy's Lancer's Perch chained above the hub to the east, Tethertown's
rocks tied together with planks, and the Whale Shallows, a bank of walkable cloud to the south-east where the sky
whales feed.

THE ROAD runs upriver. The council's skiff, sent down to fetch the ground's champions to Aurelion at the end of the
Sunward Crown, was brought down by the old Kharad wards that woke when the seal cracked: its wreck is on Crashfall, at
the bottom of the string, where the skiff from Lenswatch lands now. From there everything leads up the river to the
sky-bridge at the top, the way into Aurelion (built with the city). The map doesn't change with quests: the wreck, the
waking golems and the Ascendancy's perch are there from the start.

    Crashfall ............. the bottom island: the wreck of the council's skiff, and the skiff landing from Lenswatch
    The Last Falls ........ the river's end, an outcrop where it goes over into the void
    The Golem Fields ...... Kharad war-golems lying where they fell, getting up again
    The Silent Forge ...... the Kharad forge that made them, on its own island, west
    The Broad Isle ........ the biggest island, meadows and silver trees, the river across the middle
    Tethertown ............ the Earthborn's hamlet on the Broad Isle's east lobe, with two rocks tied on (safe)
    The Orbiting Ruins .... eight ruin islets round a broken citadel, north-west, reached by an old causeway
    The Whale Shallows .... walkable cloud south-east of the Broad Isle, where the sky whales feed
    Halcyon Rest .......... the Aetherian waystation on the river, the zone's hub, with its skiff flight (safe)
    The Lancer's Perch .... the Ascendancy's outpost, chained to the east of Halcyon Rest
    The Spillway .......... the top island, where Aurelion's water comes down
    The Aurelion Approach . the sky-bridge's foot at the north edge (Aurelion, when it's built)

A SKY MAP: the baker cuts the drop out and hangs rock under the islands and soft cloud under the Shallows
(tools/bake_ashenvale.sky_cut); the renderer paints the day-blue cloud sea below (ui/tilemap_renderer._draw_sky).

HARD CONTRACTS (world/portal_manager.py)
  portals  Lenswatch (103,206) <-> the Skiff Roost; the Golem Vault (90,156); the Anchorfields (295,30), east along
           the aqueduct arm; Aurelion (226,2), up the sky-bridge
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_worldtree_sunward_crown import _fbm, _puff, _poly, _seg_dist, _ell, smoothstep_np

BAKED_DIR = "assets/tiles/sky/baked_celestial_expanse"
NAME = "The Celestial Expanse"
W, H = 300, 260
SKP = "assets/tiles/sky/props/"
BLD = "assets/buildings/"

PORTALS = {(103, 206): "Lenswatch", (90, 156): "The Golem Vault", (295, 30): "The Anchorfields", (226, 2): "Aurelion",
           (196, 74): "Halcyon Rest"}
ARRIVALS = [(96, 206), (90, 159), (290, 30), (226, 7), (196, 77)]
LATER_PORTALS = {}
START = (96, 206)        # the skiff landing on Crashfall: everything must be reachable from here

# ---------------------------------------------------------------- the river and its beads
#: the Great Sky River, from the broken aqueduct at the north edge to the Last Falls
RIVER = [(246, 4), (246, 22), (236, 40), (220, 58), (206, 78), (190, 96), (170, 112), (150, 126), (132, 144),
         (114, 162), (94, 178), (74, 194), (54, 210), (36, 228), (20, 244), (10, 258)]
#: the six islands the river runs across, top to bottom
SPILLWAY = [(214, 4), (268, 3), (282, 22), (276, 44), (258, 54), (236, 56), (220, 46), (210, 26)]
HALCYON = [(184, 62), (214, 60), (234, 70), (236, 90), (222, 102), (196, 104), (178, 92), (176, 74)]
BROAD = [(150, 96), (178, 102), (198, 114), (208, 134), (198, 154), (174, 160), (150, 154), (128, 142), (120, 124),
         (132, 106)]
GOLEM = [(96, 144), (124, 148), (134, 164), (122, 182), (100, 186), (82, 176), (84, 156)]
CRASH = [(48, 186), (80, 186), (94, 200), (86, 222), (62, 230), (40, 222), (34, 204)]
LASTFALLS = [(16, 226), (34, 226), (38, 240), (24, 250), (12, 240)]
#: off the river
FORGE = [(12, 124), (44, 118), (60, 132), (54, 154), (30, 162), (10, 148)]
PERCH = [(264, 86), (282, 82), (292, 108), (288, 140), (272, 148), (260, 120)]
TETHERS = []     # Tethertown's two rocks are tied on below Halcyon Rest now, on the town's own map (22 Nov 2026)
ORBIT_C = (72, 58)                                                 # the broken citadel at the ring's heart
ORBIT_R = 32
ORBIT_N = 6
#: the Whale Shallows: walkable cloud off the Broad Isle's south-east
SHALLOWS = [(194, 142), (230, 150), (262, 166), (278, 196), (264, 224), (226, 238), (190, 230), (176, 206), (184, 172)]
SHALLOW_RIFTS = [([(214, 182), (230, 196), (250, 200)], 3.2), ([(200, 214), (214, 226)], 2.6)]

#: the Kharad's stone spans beside the falls, the causeway to the ruins, the chains to the perch, Tethertown's planks,
#: the skiff gangway and the sky-bridge's stub
SPANS = [
    ([(250, 46), (228, 70)], 4.0),                 # the Spillway to Halcyon Rest
    ([(216, 96), (196, 118)], 4.0),                # Halcyon Rest to the Broad Isle
    ([(148, 148), (120, 158)], 4.0),               # the Broad Isle to the Golem Fields
    ([(104, 180), (80, 194)], 4.0),                # the Golem Fields to Crashfall
    ([(50, 220), (28, 236)], 4.0),                 # Crashfall to the Last Falls
    ([(98, 62), (118, 84), (140, 110)], 4.0),      # the old causeway, the ring to the Broad Isle
    ([(46, 148), (92, 162)], 4.0),                 # the Silent Forge to the Golem Fields
    ([(228, 82), (248, 88), (272, 98)], 4.0),      # the Ascendancy's chains, Halcyon Rest to the perch
    ([(218, 119), (223, 113)], 4.0),               # ... and the second
    ([(90, 206), (104, 206)], 4.0),                # the skiff gangway on Crashfall
    ([(226, 12), (226, 0)], 4.0),                  # the sky-bridge's foot (Aurelion, later)
    ([(268, 30), (299, 30)], 4.0),                 # the old aqueduct's arm, east to the Anchorfields
]


def _orbit_islets():
    import math
    cx, cy = ORBIT_C
    out = []
    for i in range(ORBIT_N):
        a = 2 * math.pi * i / ORBIT_N + 0.2
        out.append((cx + ORBIT_R * math.cos(a), cy + ORBIT_R * 0.8 * math.sin(a), 11.5 - (i % 3), 9.0 - 0.5 * (i % 2), a))
    return out


ORBIT_ISLETS = _orbit_islets()


def _orbit_spans():
    """The short spans round the ring, one spoke into the citadel, and the gap left where a span fell."""
    out = []
    n = len(ORBIT_ISLETS)
    for i in range(n):
        if i == 5:
            continue                    # one span of the ring has fallen: you go round the long way
        a, b = ORBIT_ISLETS[i], ORBIT_ISLETS[(i + 1) % n]
        out.append(([(a[0], a[1]), (b[0], b[1])], 4.2))
    for k in (0, 3):                    # two spokes straight through the citadel, so the gap is never a long walk
        s = ORBIT_ISLETS[k]
        out.append(([(s[0], s[1]), ORBIT_C], 4.2))
    return out


ORBIT_SPANS = _orbit_spans()


def _warp(gx, gy, amp):
    return (gx + amp * _fbm(gx, gy, 0.7) + 0.55 * amp * _puff(gx, gy, 0.9),
            gy + amp * _fbm(gx, gy, 2.3) + 0.55 * amp * _puff(gx, gy, 3.3))


def _rock_raw(gx, gy):
    """Negative on the rock islands (every bead, the forge, the perch, the ring, the tethered rocks), before smoothing."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    wx, wy = _warp(gx, gy, 6.0)
    edge = 1.8 * _puff(gx, gy, 1.7) + 0.6 * np.sin(0.53 * gx + 0.37 * gy) + 0.4 * np.sin(0.81 * gy - 0.4 * gx)
    c = np.minimum.reduce([_poly(wx, wy, P) for P in (SPILLWAY, HALCYON, BROAD, GOLEM, CRASH, LASTFALLS, FORGE, PERCH)])
    c = c + edge
    for (x, y, rx, ry, rot) in TETHERS:
        c = np.minimum(c, _ell(gx, gy, x, y, rx, ry, rot) + 0.5 * edge)
    for (x, y, rx, ry, rot) in ORBIT_ISLETS:
        c = np.minimum(c, _ell(gx, gy, x, y, rx, ry, rot) + 0.4 * edge)
    c = np.minimum(c, _ell(gx, gy, ORBIT_C[0], ORBIT_C[1], 13, 10, 0.4) + 0.5 * edge)
    return c


def _cloud_raw(gx, gy):
    """Negative on the Whale Shallows' walkable cloud, before smoothing."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    wx, wy = _warp(gx, gy, 6.0)
    billow = 3.0 * _puff(gx, gy, 4.4) + 2.2 * _puff(1.7 * gx, 1.7 * gy, 8.1)
    c = _poly(wx, wy, SHALLOWS) + billow
    for pts, hw in SHALLOW_RIFTS:
        c = np.maximum(c, -(_seg_dist(wx, wy, pts) - hw + 0.5 * billow))
    return c


def span_mask(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    out = np.full(np.shape(gx), 99.0)
    for pts, hw in SPANS + ORBIT_SPANS:
        out = np.minimum(out, _seg_dist(gx, gy, pts) - hw)
    return out


def _sea_exact(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    land = np.minimum.reduce([rock_field(gx, gy), cloud_field(gx, gy), span_mask(gx, gy) + 0.1 * _fbm(gx, gy, 1.0)])
    edge = np.maximum.reduce([2.0 - gx, gx - (W - 3.0), -1.0 - gy, gy - (H - 1.0)])
    return np.maximum(land, edge * 3.0)


def _cloudness_exact(gx, gy):
    from tools.bake_ashenvale import smoothstep
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    other = np.minimum(rock_field(gx, gy), span_mask(gx, gy))
    return (1 - smoothstep(-1.2, 0.8, cloud_field(gx, gy))) * smoothstep(-1.5, 1.5, other)


# ---------------------------------------------------------------- cached fields (see the Sunward Crown's module)
_GRID_R = 4
_CACHE = {}


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


#: Kyle, 20 Nov 2026: "dont make them too hard to travel on with tiny paths and snag points....looks good - sucks to
#: play". The island and cloud fields are blurred on the cached grid before anything reads them: a blur rounds the
#: coast, fills the one-tile notches you catch on and melts the thin spits, so every rim is a smooth curve to walk along.
#: The spans aren't blurred (they'd thin out); they're wide instead.
_SMOOTH_TILES = {"rock": 1.8, "cloudraw": 1.4}


def _smoothed(name, raw):
    def fn(GX, GY):
        from scipy.ndimage import gaussian_filter
        return gaussian_filter(np.asarray(raw(GX, GY), np.float32), _SMOOTH_TILES[name] * _GRID_R, mode="nearest")
    return _cached(name, fn)


def rock_field(gx, gy):
    """Negative on the rock islands (smoothed: see _SMOOTH_TILES)."""
    return _sample(_smoothed("rock", _rock_raw), gx, gy)


def cloud_field(gx, gy):
    """Negative on the Whale Shallows' walkable cloud (smoothed)."""
    return _sample(_smoothed("cloudraw", _cloud_raw), gx, gy)


def sea(gx, gy):
    """The drop: everything that isn't island, cloud or span. Extent > 0 is a fall into the sky."""
    return _sample(_cached("sea", _sea_exact), gx, gy)


def cloudness(gx, gy):
    return _sample(_cached("cloud", _cloudness_exact), gx, gy)


def ground_suppress(gx, gy):
    c = cloudness(gx, gy)
    t = np.clip((c - 0.2) / 0.4, 0, 1)
    return t * t * (3 - 2 * t)


#: the renderer's sky (tilemap.sky) and the baker's cut: the clear day sky, more wisps, the sun higher and softer
SKY = {"far": "sky_far_day", "parallax": 0.35, "drift": 5.0, "wisps": 0.6, "sun": 0.35, "far_tiles": 10,
       "underside": 5.0, "cloud": cloudness, "cloud_lift": 0.16}


def satyr_field(P, wp):
    """The Whale Shallows' cloud (the "satyr" layer, painted as cloud)."""
    return 1.75 * cloudness(P.gx, P.gy)


def plaza_field(P, wp):
    """The old stone spans, the planks and the gangway (the "plaza" layer), painted over the gaps only: the spans run
    well into the islands either end so they always land, but on the rock you walk on the island's own ground."""
    from tools.bake_ashenvale import smoothstep
    over_the_gap = smoothstep(-1.5, 0.5, rock_field(P.gx, P.gy))
    return 1.9 * (1.0 - smoothstep(-0.4, 1.2, span_mask(P.gx, P.gy))) * over_the_gap


ISLETS = []
#: the plunge pool under Aurelion's water, Halcyon Rest's pool, a pond on the Broad Isle, the forge's quench pool
LAKES = {"pools": [(244, 24, 9, 6, 0.3, 0.6), (218, 74, 4, 3, 0, 1.2), (160, 140, 5, 3, 0.5, 2.1),
                   (28, 140, 4, 3, 0, 0.9)]}
DEEP_SHRINK = {"pools": 6.0}
#: the Great Sky River: (points, shallow half-width, deep half-width) as the engine takes them
RIVERS = [(RIVER, 3.0, -2.0)]
FORDS = [(206, 80, 6), (160, 120, 6), (106, 168, 6), (62, 206, 6)]

MESAS = []
RIDGES = []
#: silver groves on the Broad Isle and Halcyon Rest's garden, a stand of blossom trees on the Spillway
WOODS = [(150, 108, 6, 4, 0.5, 1.0), (186, 146, 4, 3, 0.2, 2.0), (136, 132, 4, 3, 0.9, 0.6),
         (262, 30, 5, 3, 0.3, 1.4), (190, 74, 3, 2, 0.0, 2.2)]
BELTS = []
CLEARINGS = [
    (96, 206, 7, 4),            # the skiff landing
    (64, 204, 10, 7),           # Crashfall's camp by the wreck
    (24, 238, 6, 5),            # the Last Falls
    (108, 168, 10, 7),          # the Golem Fields
    (90, 158, 5, 4),            # before the Golem Vault's door
    (32, 140, 10, 8),           # the Silent Forge
    (186, 134, 11, 8),          # the Broad Isle's east lobe, where Tethertown stood before it moved up to the Rest
    (160, 124, 12, 8),          # the Broad Isle's meadow
    (205, 82, 12, 8),           # Halcyon Rest
    (275, 112, 8, 12),          # the Lancer's Perch
    (242, 30, 12, 9),           # the Spillway
    (290, 30, 5, 4),            # the aqueduct arm's landing
    (226, 16, 6, 4),            # the Aurelion Approach
    (72, 58, 8, 6),             # the broken citadel
]
#: ruin-moss on the ring's islets ("corrupt"), rubble and broken stone at the forge and the golems ("burned"),
#: sky-flowers on the meadows ("bluebell")
CORRUPT_PATCHES = [(72, 58, 30, 26)]
BURNED_PATCHES = [(32, 140, 18, 14), (108, 166, 16, 12)]
BLUEBELL_PATCHES = [(158, 112, 10, 6), (176, 148, 6, 4), (252, 40, 8, 5), (198, 92, 6, 4), (70, 192, 6, 4)]
PAVED_PATCHES = []
LUSH = 0.3
GRADE = None
DROP = None

GAPS = [("ell", 96, 206, 4, 3), ("ell", 64, 204, 7, 5), ("ell", 205, 82, 8, 5), ("ell", 186, 134, 8, 5)]

#: the trails: upriver along the banks from the landing to the sky-bridge, across at the fords, out to the side islands
ROADS = {
    "landing":   ([(94, 206), (80, 206), (64, 204)], 2.4),
    "crash_up":  ([(64, 204), (78, 194), (88, 188)], 2.2),
    "lastfalls": ([(56, 214), (44, 222), (34, 230)], 2.0),
    "golem":     ([(92, 182), (104, 170), (120, 160), (128, 154)], 2.4),
    "forge":     ([(86, 162), (60, 152), (40, 144)], 2.2),
    "broad":     ([(140, 150), (152, 138), (162, 124), (176, 116), (198, 114)], 2.6),
    "causeway":  ([(136, 106), (150, 112), (158, 120)], 2.2),
    "halcyon":   ([(204, 110), (210, 96), (206, 82), (220, 72), (232, 66)], 2.6),
    "rest_gate": ([(206, 82), (198, 77)], 2.2),
    "perch":     ([(228, 84), (234, 82)], 2.0),
    "spillway":  ([(240, 56), (250, 44), (248, 30), (236, 20), (226, 14)], 2.4),
    "shallows":  ([(196, 148), (210, 166), (222, 186)], 2.0),
}


class _Spec(E.Spec):
    """Groves only on the rock, never on the cloud or out over the drop."""

    def woods_raw(self, gx, gy):
        out = super().woods_raw(gx, gy)
        return np.minimum(out, -(np.asarray(rock_field(gx, gy)) + 3.0))


SPEC = _Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
             mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
             rim={}, rock_rim={}, gaps=GAPS, fords=FORDS, thicket=(0.99, 10.0, 2.0))

#: everyone on the Expanse (tools/build_celestial_expanse_people.py writes their records)
NPC_POSITIONS = {
    # Crashfall: the council's skiff came down here, and the skiff from Lenswatch lands here now
    "ce_pilot":           (56, 200),   # the council skiff's pilot, hurt
    "ce_landing_hand":    (92, 203),   # the survey's hand at the skiff landing
    # the Last Falls and the Golem Fields
    "ce_falls_watcher":   (26, 236),   # an old Aetherian who watches the islands fall
    # Tethertown, Halcyon Rest and the people who came up the river to them live on the town's own map now
    # (tools/handbuilt_worldtree_halcyon_rest.py)
    # the Whale Shallows
    "ce_whale_watcher":   (200, 160),  # an Earthborn marine biologist, watching the whales
    # the Spillway and the Aurelion Approach
    "ce_spill_tender":    (240, 40),   # keeps what's left of the aqueduct
    "ce_bridgewarden":    (228, 18),   # holds the sky-bridge, closed until the council sends word
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("The Broad Isle", 116, 94, 96, 70, None),
    ("The Golem Fields", 80, 142, 58, 46, None),
    ("The Silent Forge", 6, 114, 58, 52, None),
    ("The Orbiting Ruins", 36, 28, 76, 60, None),
    ("The Whale Shallows", 174, 150, 110, 92, None),
    ("The Lancer's Perch", 244, 80, 54, 72, None),
    ("The Spillway", 206, 22, 82, 36, None),
    ("Crashfall", 32, 184, 66, 48, None),
    ("The Last Falls", 8, 222, 36, 34, None),
    ("Halcyon Rest", 176, 60, 62, 46, None),
    ("The Aurelion Approach", 212, 0, 30, 22, None),
]

#: silver and blossom trees on the meadows, wind trees out on the edges
TREES = {
    "big":   [(SKP + "sk_silver_tree.png", 8), (SKP + "sk_sky_birch.png", 7)],
    "mid":   [(SKP + "sk_blossom_tree.png", 6), (SKP + "sk_wind_tree.png", 6), (SKP + "sk_fruit_tree.png", 6)],
    "small": [(SKP + "sk_wind_tuft.png", 3), (SKP + "sk_heather_clump.png", 3), (SKP + "sk_bellflowers.png", 2)],
    "woods": [(SKP + "sk_silver_tree.png", 8)],
}


def _grid():
    ys, xs = np.mgrid[0:H, 0:W]
    return xs + 0.5, ys + 0.5


def drop_mask(L=None):
    return sea(*_grid()) > 0


def on_the_cloud():
    gx, gy = _grid()
    return (cloud_field(gx, gy) < 0) & (rock_field(gx, gy) > 0.5)


def on_a_span(pad=1.5):
    return span_mask(*_grid()) < pad


def in_a_camp():
    gx, gy = _grid()
    m = np.zeros((H, W), bool)
    for (cx, cy, rx, ry) in [(64, 204, 12, 8), (96, 206, 6, 4), (186, 134, 12, 8), (205, 82, 13, 9),
                             (275, 112, 10, 14), (226, 16, 7, 5), (72, 58, 10, 8), (32, 140, 12, 10),
                             (108, 168, 10, 8), (242, 30, 6, 5)]:
        m |= (np.abs(gx - cx) < rx) & (np.abs(gy - cy) < ry)
    return m


def open_the_drop(L):
    z = L.z
    for y, x in zip(*np.nonzero(drop_mask(L))):
        z.set_tile(int(x), int(y), "grass", "base")
        z.set_tile(int(x), int(y), "cliff", "collision")


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "The open sky between the World Tree and Aurelion: islands strung down a great river that "
                             "falls from one to the next, old Kharad ruins waking, and sky whales in the cloud.",
                             "Eastern Kingdoms - The World Tree", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
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
    L.free_mask[in_a_camp()] = False
    cloud = on_the_cloud()
    keep = L.free_mask.copy()
    L.free_mask[cloud] = False
    E.scatter_trees(L, TREES, seed=5101, spacing=8.0, grove_keep=0.5)
    sprinkle(L)
    L.free_mask = L.free_mask | (keep & cloud)
    cloud_dress(L, cloud)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def sprinkle(L):
    """Sky-lilies, clover and wind tufts on the meadows; nothing on the trails, the cloud or the spans."""
    import random
    rnd = random.Random(5103)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    kinds = [("sk_sky_lilies", 0.008, 26), ("sk_clover_patch", 0.016, 30), ("sk_rubble_flowers", 0.020, 16)]
    n = {k: 0 for k, _, _ in kinds}
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        for name, upto, cap in kinds:
            if r < upto:
                if n[name] < cap and L.prop(name, x, y, 2, path_dir=SKP, solid=False, nudge=0):
                    n[name] += 1
                    L.free_mask[max(0, y - 2):y + 3, max(0, x - 2):x + 3] = False
                break
    L.clutter = tuple(n.values())


def cloud_dress(L, cloud):
    """Wisps and cloud banks drifting on the Shallows."""
    import random
    rnd = random.Random(5107)
    ys, xs = np.nonzero(L.free_mask & cloud)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = {"sk_cloud_wisp": 0, "sk_cloud_bank": 0}
    cap = {"sk_cloud_wisp": 18, "sk_cloud_bank": 6}
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        name = "sk_cloud_wisp" if r < 0.008 else "sk_cloud_bank" if r < 0.011 else None
        if name and n[name] < cap[name]:
            if L.prop(name, x, y, 3 if name == "sk_cloud_wisp" else 5, path_dir=SKP, solid=False, nudge=0):
                n[name] += 1
                L.free_mask[max(0, y - 4):y + 5, max(0, x - 4):x + 5] = False
    L.cloud_clutter = tuple(n.values())


CHEST_SPOTS = [(20, 244), (16, 132), (50, 156), (90, 180), (128, 160), (122, 120), (172, 152), (216, 126), (228, 110),
               (236, 92), (284, 126), (268, 18), (60, 36), (92, 74), (48, 74), (240, 228), (268, 186)]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    def B(n, x, y, h, **kw):
        kw.setdefault("solid", "core")
        kw.setdefault("nudge", 2)
        return L.prop(n, x, y, h, path_dir=BLD, **kw)

    def S(n, x, y, h, **kw):
        kw.setdefault("solid", "core")
        kw.setdefault("nudge", 3)
        return L.prop(n, x, y, h, path_dir=SKP, **kw)

    def rim(x, y, dx, dy):
        """The last walkable-rock tile walking from (x, y) toward (dx, dy): where a pool's overflow goes over."""
        while 0 < x + dx < W - 1 and 0 < y + dy < H - 1 and float(sea(x + dx, y + dy)) < -0.5:
            x, y = x + dx, y + dy
        return x, y

    # ---- the wellstones' falls (Kyle, 20 Nov 2026: "island waterfalls where some-fucking-how we have unlimited water
    #      pouring off the island"): the side islands' pools spill over their nearest edge, as the river does
    for (px, py, dx, dy) in [(28, 140, -1, 0), (160, 140, 0, 1), (218, 74, 0, -1)]:
        pass  # the edge falls prop is gone (Kyle, 21 Nov 2026: "lets remove this prop... it doesnt work")

    # ---- Crashfall: the council's skiff where it came down, torn open, a fire by it, and the survey's landing
    S("ff_wrecked_skiff", 50, 196, 8, allow_overlap=True)
    S("ff_camp_fire", 64, 204, 3, solid=False)
    S("ff_patched_tent", 74, 200, 5)
    S("ff_salvage", 54, 210, 4)
    B("ae_skiff_dock", 92, 212, 6)
    B("ae_lamp_post", 88, 200, 4)
    # ---- the Last Falls: the river goes over, and the old watcher's lantern
    pass  # the edge falls prop is gone (Kyle, 21 Nov 2026: "lets remove this prop... it doesnt work")
    S("sk_stone_lantern", 28, 232, 4)
    # ---- the Golem Fields: war-golems lying where they fell, a sword the size of a tree, a core still humming
    for (x, y) in [(96, 160), (118, 176), (124, 156), (100, 176)]:
        S("sk_dormant_golem", x, y, 6)
    S("sk_giant_sword", 110, 152, 8)
    S("sk_golem_core", 116, 166, 4)
    S("ff_patched_tent", 106, 174, 5)
    # the vault, standing ON its door (Kyle, 21 Nov 2026: "golem vault has two art entrances?"). It sat three tiles north of
    # the portal, so world/exit_frames.py saw a bare door and framed it again underneath.
    L.z.add_landmark("assets/tiles/cave_entrances/ent_door_kharad_vault.png", 87, 151, 7, 6, solid=False)   # door tile in its arch
    B("kh_kneeling_statue", 90, 168, 8)
    # ---- the Silent Forge: the Kharad forge and its yard, cold for ages and warming again
    B("kh_forge", 32, 136, 10)
    B("kh_mason_yard", 20, 148, 6)
    B("kh_quarry_blocks", 46, 146, 4)
    B("kh_crane", 44, 130, 8)
    B("kh_earth_core", 24, 128, 6)
    # ---- the Broad Isle: an old observatory ruin on its rise, a fallen column across the meadow
    B("sk_observatory_ruin", 140, 118, 10)
    S("sk_fallen_column", 168, 112, 4)
    S("sk_ruin_tree", 132, 140, 7)
    # ---- the Broad Isle's east lobe: Tethertown moved up to the Rest; the chain they tied on with is still in the rock
    B("kh_chain_anchor", 212, 126, 4)
    # ---- the Whale Shallows: rock islets the whales rub on, standing out of the cloud
    S("sk_float_rock", 238, 206, 5)
    S("sk_cloud_bank", 220, 168, 5, solid=False)
    # ---- Halcyon Rest: the island outside the Rest's gate (the town is its own map, west of the river), the
    #      keeper's pool pavilion showing over the wall, lamps along the river road
    B("ae_pool_pavilion", 228, 76, 8)
    S("sk_silver_tree", 188, 70, 6)
    S("sk_silver_tree", 186, 82, 6)
    for (x, y) in [(202, 70), (216, 70), (200, 92), (224, 80)]:
        B("ae_lamp_post", x, y, 4)
    # ---- the Lancer's Perch: the Ascendancy's watch-spire over the river, tents, a gun on the rest
    B("ae_watch_spire", 276, 104, 12)
    B("ae_soldier_tent", 270, 118, 5)
    B("ae_soldier_tent", 280, 124, 5)
    B("ae_storm_artillery", 268, 98, 6)
    B("ae_shield_pylon", 266, 108, 6)
    B("ae_war_standard", 278, 132, 6)
    # ---- the Orbiting Ruins: the broken citadel in the middle, bells and pillars out on the ring
    B("kh_citadel_keep", 72, 60, 12, allow_overlap=True)
    for i, (x, y, *_r) in enumerate(ORBIT_ISLETS):
        S(("sk_broken_column", "sk_float_ruin", "sk_obelisk", "sk_ancient_bell")[i % 4],
          int(x), int(y), 5)
    # ---- the Spillway: Aurelion's broken aqueduct at the north edge, its water coming down into the pool
    B("ae_aqueduct", 246, 10, 10, allow_overlap=True, road_ok=True)
    S("sk_float_falls", 256, 28, 6)
    pass  # the cascade prop is gone too (Kyle, 21 Nov 2026: "these waterfall sprites are terrible here")
    # ---- the Aurelion Approach: the sky-bridge's pylons and the bridgewarden's post
    B("ae_bridge_pylon", 220, 14, 8)
    B("ae_bridge_pylon", 232, 14, 8)
    B("ae_guard_post", 236, 20, 6)
    # ---- the river's falls: where it goes over each island's edge onto the next
    for (x, y) in [(226, 56), (194, 104), (130, 148), (90, 186), (40, 226)]:
        pass  # the edge falls prop is gone (Kyle, 21 Nov 2026: "lets remove this prop... it doesnt work")


def register_baked(zone):
    import os
    zone.sky = {k: v for k, v in SKY.items() if not callable(v)}
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.webp"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_celestial_expanse():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS) + list(LATER_PORTALS),
                              npc=list(NPC_POSITIONS.values()))
