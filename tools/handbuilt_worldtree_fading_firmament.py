"""
Hand-built Fading Firmament (300x260), levels 57-60: the dying heart of Caelora, the last of the sky (docs/worldtree_brief.md:
"the dying heart of the Aetherian world: sky-forges going dark, crystal engines failing, islands breaking apart and
falling into the void below the clouds"; threat: "the Ascendancy's last push to seize the tree; the sky itself coming
apart"). A failing violet dusk.

ANCIENT, NOT NEW (Kyle, 20 Nov 2026). The Firmament was the oldest ground in the sky, one great plate round the
Threefold Forge, where the wellstones were made. It's been coming apart for centuries, slowly, the way a dying fire goes
out, and lately much faster. Its people left in stages. The last of them are at Lastlight, round the one shrine still lit.

THE SHAPE (Kyle: "Stop reusing the same shape"; "dont make them too hard to travel on with tiny paths and snag
points"; and, for a map of links, "we don't want like 10 small islands, maybe 2 or 3 large ones with a few small ones.
Don't make it a chore to island hop"). Three big landmasses round a hole in the sky, the Wound, and a few small rocks.
The Old Plate is a great crescent wrapping the Wound's west side, what's left of the Firmament's own ground: the road
comes up onto its southern tip, and Lastlight, the Emptied Quarter, the Greyfall Gardens and the Coldforges run north
along it. The Ascendancy holds the big eastern mass: the Dead Engines to the north, the Siege Line down its middle. In
the middle, the Rim, one horseshoe of ground round the Wound, open to the north-east, with the Wound's Edge on its west
side and the Moorage on its east, where Ascendant-General Maelis Ardane's fleet hangs over the hole. The small ones:
the Threefold Forge on its own rock at the top, the Breaking coming apart at the bottom, and one islet with the last
green tree. Short wide bridges join the Old Plate to the Forge and to the Breaking, and the Breaking to the east. The
four gaps too wide to bridge are crossed by links (world/links.py): a skip-stone onto the Rim from each big mass, a
dusk current from the Forge across to the Dead Engines, and another out to the islet.

    The Road's End ......... the Firmament Road's last span, from the Ascendant Bastions (the way in)
    Lastlight .............. the last people, round the last lit shrine: the zone's hub and flight path (safe)
    The Emptied Quarter .... a town everyone left, its doors still open
    The Greyfall Gardens ... the gardens gone grey, the crystal trees turned to glass
    The Coldforges ......... the sky-forges, gone dark one by one, and the Ascendancy stripping them
    The Last Green ......... an islet off the Gardens with one tree still alive on it
    The Threefold Forge .... the oldest forge, with three hearths, and the way down into the Hearthdeep
    Forgewatch ............. the House of Long Memory's scholars at the forge's west end (safe)
    The Dead Engines ....... the great crystal engines gone black, and the way into the Hollow Engine
    The Siege Line ......... the Ascendancy's trenches and guns, and the camp the fleet is fed from
    The Breaking ........... an island coming apart as you stand on it
    The Wound's Edge ....... the Rim's west side, over the hole in the sky
    The Moorage ............ the Rim's east side, and the general's fleet moored over the Wound

A SKY MAP: the baker cuts the drop out (the gaps and the Wound) and hangs rock under the islands.

HARD CONTRACTS (world/portal_manager.py)
  portals  The Ascendant Bastions (122,257) <-> the Road's End; The Hearthdeep (the Threefold Forge);
           The Hollow Engine (the Dead Engines)
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_worldtree_sunward_crown import _fbm, _puff, _poly, _seg_dist, _ell, smoothstep_np  # noqa: F401

BAKED_DIR = "assets/tiles/sky/baked_fading_firmament"
NAME = "The Fading Firmament"
W, H = 300, 260
SKP = "assets/tiles/sky/props/"
BLD = "assets/buildings/"
ENT = "assets/tiles/cave_entrances/"

PORTALS = {(122, 257): "The Ascendant Bastions", (178, 14): "The Hearthdeep", (244, 50): "The Hollow Engine"}
ARRIVALS = [(122, 251), (178, 18), (244, 54)]
START = (122, 251)          # the top of the Firmament Road: everything must be reachable from here

WOUND_C = (156, 122)        # the hole in the sky
#: (cx, cy, rx, ry, rot). THE OLD PLATE: a crescent of lobes round the Wound's west side, the road's tip at its south
OLD_PLATE = [(122, 236, 16, 12, 0.0), (114, 206, 30, 27, 0.3), (87, 188, 30, 27, 0.5), (67, 161, 30, 27, 0.2),
             (58, 130, 30, 27, 0.0), (61, 98, 30, 27, -0.2), (76, 69, 30, 26, -0.5), (96, 49, 28, 22, -0.3)]
#: THE ASCENDANCY'S SIDE: the big eastern mass
EAST = [(231, 62, 30, 26, 0.5), (248, 90, 30, 27, 0.2), (254, 122, 30, 27, 0.0), (248, 154, 30, 27, -0.2),
        (231, 182, 30, 26, -0.5)]
#: the small ones
FORGE = (166, 22, 28, 17, 0.0)
BREAKING = (178, 218, 22, 17, 0.2)
LAST_GREEN = (24, 30, 12, 9, 0.3)
LOBES = OLD_PLATE + EAST + [FORGE, BREAKING, LAST_GREEN]
#: THE RIM: one horseshoe round the Wound, open to the north-east (angle, half-width in degrees)
RIM_OUT = (52, 44)
RIM_IN = (27, 23)
RIM_CRACKS = [(-50, 22)]
#: the Moorage's pier, out over the Wound from the Rim's east side (built: straight-sided)
PIER = [(164, 117), (188, 117), (188, 127), (164, 127)]

#: the bridges, wide (Kyle: no tiny paths). The gaps too wide to bridge are crossed by links instead (LINKS, below).
SPANS = [
    ([(122, 259), (122, 246)], 4.6),               # the Firmament Road's last span
    ([(136, 232), (160, 222)], 4.6),               # the Road's End to the Breaking
    ([(196, 210), (214, 196)], 4.6),               # the Breaking to the Siege Line
    ([(116, 40), (142, 26)], 4.6),                 # the Coldforges to the Threefold Forge
]


def _reach_in(spans, d=6.0, keep=1):
    """Run each bridge a few tiles on into the ground at both ends, so the warped coasts can't leave it short. The first
    `keep` spans (the road's, which ends at the map's edge) are left alone at their outer end."""
    out = []
    for i, (pts, hw) in enumerate(spans):
        (x0, y0), (x1, y1) = pts[0], pts[1]
        n = max(1e-6, ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5)
        a = pts[0] if i < keep else (x0 - d * (x1 - x0) / n, y0 - d * (y1 - y0) / n)
        (xa, ya), (xb, yb) = pts[-2], pts[-1]
        m = max(1e-6, ((xb - xa) ** 2 + (yb - ya) ** 2) ** 0.5)
        b = (xb + d * (xb - xa) / m, yb + d * (yb - ya) / m)
        out.append(([a] + list(pts[1:-1]) + [b] if len(pts) > 2 else [a, b], hw))
    return out


SPANS = _reach_in(SPANS)

#: LINKS (world/links.py; Kyle, 21 Nov 2026: "little short range portals that link islands instead of bridges", "you use
#: wind currents to move between them", "they are more heavily found later", "Don't make it a chore to island hop").
#: The Aetherians' old skip-stones still reach the Rim from both big masses (the Ascendancy refitted its own), and two
#: failing dusk currents cross the gaps the ground drifted too far apart to bridge. (kind, pad, pad); you land two
#: tiles south of the pad you arrive at.
LINKS = [
    ("skipstone", (80, 128), (112, 122)),       # the Old Plate (by the Emptied Quarter) to the Wound's Edge
    ("skipstone", (230, 122), (200, 128)),      # the Siege Line to the Moorage
    ("dusk_wind", (186, 22), (220, 52)),        # the Threefold Forge to the Dead Engines
    ("dusk_wind", (62, 62), (28, 30)),          # the Greyfall Gardens out to the Last Green
]


def _warp(gx, gy, amp):
    return (gx + amp * _fbm(gx, gy, 1.7) + 0.55 * amp * _puff(gx, gy, 2.3),
            gy + amp * _fbm(gx, gy, 3.7) + 0.55 * amp * _puff(gx, gy, 4.9))


def _rim(gx, gy):
    """Negative on the rim band: inside the outer ellipse, outside the Wound, and not in a crack."""
    cx, cy = WOUND_C
    dx, dy = gx - cx, gy - cy
    outer = (np.hypot(dx / RIM_OUT[0], dy / RIM_OUT[1]) - 1.0) * min(RIM_OUT)
    inner = (1.0 - np.hypot(dx / RIM_IN[0], dy / RIM_IN[1])) * min(RIM_IN)
    band = np.maximum(outer, inner)
    ang = np.degrees(np.arctan2(dy, dx))
    r = np.hypot(dx, dy)
    for (a, hw) in RIM_CRACKS:
        d = np.abs((ang - a + 180) % 360 - 180)
        crack = (hw - d) * np.maximum(r, 1) * np.pi / 180      # tiles inside the crack's wedge
        band = np.maximum(band, crack)
    return band


#: fissures opening in the ground (polyline, half-width): the Breaking splitting as you stand on it, and the Emptied
#: Quarter's old crack. They run in from the edge and stop, so they never cut the ground in two.
FISSURES = [([(200, 226), (186, 220)], 1.4), ([(160, 210), (170, 214)], 1.2), ([(28, 146), (42, 142)], 1.3)]


def _rock_raw(gx, gy):
    """Negative on the landmasses, the small rocks, the Rim and the pier, before smoothing. The edges crumble."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    nx, ny = _warp(gx, gy, 5.0)
    edge = 1.8 * _puff(gx, gy, 2.9) + 0.6 * np.sin(0.43 * gx + 0.31 * gy) + 0.45 * np.sin(0.69 * gy - 0.37 * gx)
    out = np.full(np.shape(gx), 99.0)
    for isl in LOBES:
        out = np.minimum(out, _ell(nx, ny, *isl) + edge)
    rx, ry = _warp(gx, gy, 3.0)
    out = np.minimum(out, _rim(rx, ry) + 0.7 * edge)
    for pts, hw in FISSURES:
        out = np.maximum(out, hw - _seg_dist(nx, ny, pts))
    bx, by = _warp(gx, gy, 0.8)
    return np.minimum(out, _poly(bx, by, PIER))


def span_mask(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    out = np.full(np.shape(gx), 99.0)
    for pts, hw in SPANS:
        out = np.minimum(out, _seg_dist(gx, gy, pts) - hw)
    return out


# ---------------------------------------------------------------- cached, smoothed fields (see the Expanse's module)
_GRID_R = 4
_CACHE = {}
_SMOOTH_TILES = {"rock": 1.5}


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


def cloud_field(gx, gy):
    """No walkable cloud on the Firmament: the cloud's thinning here, which is half of what's wrong."""
    return np.full(np.shape(np.asarray(gx, float)), 99.0)


def _sea_exact(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    land = np.minimum(rock_field(gx, gy), span_mask(gx, gy) + 0.1 * _fbm(gx, gy, 1.0))
    edge = np.maximum.reduce([-1.0 - gx, gx - (W - 1.0), -1.0 - gy, gy - (H - 1.0)])
    return np.maximum(land, edge * 3.0)


def sea(gx, gy):
    """The drop: everything that isn't island or bridge, the Wound among it. Extent > 0 is a fall into the sky."""
    return _sample(_cached("sea", _sea_exact), gx, gy)


def cloudness(gx, gy):
    return np.zeros(np.shape(np.asarray(gx, float)))


def _works_raw(gx, gy):
    """The Siege Line's earthworks and the Moorage's pier: paved, built ground."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    bx, by = _warp(gx, gy, 0.8)
    return np.minimum(_poly(bx, by, PIER), _ell(bx, by, 252, 150, 16, 20, -0.2))


def paving_field(P, wp):
    from tools.bake_ashenvale import smoothstep
    w = _sample(_cached("works", _works_raw), P.gx, P.gy)
    return 1.0 - smoothstep(-2.0, 0.5, w)


def ground_suppress(gx, gy):
    return np.zeros(np.shape(np.asarray(gx, float)))


#: the renderer's sky and the baker's cut: a failing violet dusk, the sun low and weak
SKY = {"far": "sky_far_dusk", "parallax": 0.35, "drift": 2.5, "wisps": 0.35, "sun": 0.2, "far_tiles": 10,
       "underside": 5.0, "cloud": cloudness, "cloud_lift": 0.0}


def satyr_field(P, wp):
    return np.zeros(np.shape(P.gx))


def plaza_field(P, wp):
    """The bridges, painted over the gaps only."""
    from tools.bake_ashenvale import smoothstep
    over_the_gap = smoothstep(-1.5, 0.5, rock_field(P.gx, P.gy))
    return 1.9 * (1.0 - smoothstep(-0.4, 1.2, span_mask(P.gx, P.gy))) * over_the_gap


ISLETS = []
#: the wellstone pools that still run: Lastlight's, the Gardens' dry fountain basin, the Forge's quench pool, the
#: Breaking's spring (Kyle: every pool falls off the nearest edge)
LAKES = {"pools": [(104, 202, 5, 3, 0.3, 1.1), (54, 104, 5, 3, 0.4, 1.6), (154, 26, 4, 3, 0.0, 2.1),
                   (184, 224, 4, 3, 0.2, 2.6)]}
DEEP_SHRINK = {"pools": 5.0}
RIVERS = []
FORDS = []
MESAS = []
RIDGES = []
#: the last stands of trees, dead most of them, on the natural ground
WOODS = [(40, 172, 9, 6, 0.3, 1.0), (74, 92, 7, 5, 0.5, 1.8), (268, 100, 8, 6, -0.3, 2.4), (24, 30, 3, 2, 0.2, 0.6),
         (226, 166, 6, 4, 0.2, 3.1)]
BELTS = []
CLEARINGS = [
    (122, 246, 7, 4),           # the top of the road
    (100, 198, 16, 10),         # Lastlight
    (62, 150, 16, 14),          # the Emptied Quarter's streets
    (60, 102, 14, 10),          # the Gardens' walks
    (90, 52, 20, 10),           # the Coldforges' yards
    (166, 22, 16, 9),           # the Threefold Forge and Forgewatch
    (178, 18, 5, 3),            # before the Hearthdeep's door
    (240, 68, 14, 10),          # among the dead engines
    (244, 54, 5, 3),            # before the Hollow Engine's door
    (250, 150, 16, 18),         # the Siege Line's camp
    (178, 218, 12, 8),          # the Breaking
    (176, 122, 10, 4),          # the Moorage's pier
]
#: dead grey grass over most of it, grey crystal ash worn through; violet crystal rubble where the ground's breaking
#: ("corrupt"), burnt bronze round the forges and the guns ("burned"), the old plate's ruined marble where it was paved
CORRUPT_PATCHES = [(60, 100, 26, 18), (178, 218, 22, 14), (156, 122, 44, 36)]
BURNED_PATCHES = [(90, 52, 26, 14), (250, 150, 26, 30), (238, 72, 22, 18)]
BLUEBELL_PATCHES = [(30, 30, 8, 6)]
PAVED_PATCHES = [(62, 150, 22, 18), (100, 198, 14, 8), (166, 22, 18, 10)]
LUSH = 0.02
GRADE = None
DROP = None

GAPS = [("ell", 122, 246, 5, 3), ("ell", 100, 198, 10, 6), ("ell", 166, 22, 9, 5), ("ell", 178, 18, 3, 2),
        ("ell", 244, 54, 3, 2), ("ell", 250, 150, 8, 8)]

#: the roads: up the Old Plate from the road's tip, out over the bridges to the Forge and round by the Breaking to the
#: east, round the Rim, and short spurs to every link's pad
ROADS = {
    "road":      ([(122, 250), (122, 236), (112, 218), (100, 198)], 2.4),
    "quarter":   ([(100, 198), (80, 180), (66, 156), (60, 130)], 2.4),
    "gardens":   ([(60, 130), (60, 100), (72, 74)], 2.4),
    "forges":    ([(72, 74), (86, 56), (110, 44), (142, 26), (166, 22)], 2.4),
    "breaking":  ([(122, 236), (136, 232), (160, 222), (178, 218), (196, 210), (214, 196), (234, 178)], 2.4),
    "siege":     ([(234, 178), (250, 150), (254, 122), (246, 92), (236, 66)], 2.4),
    "rim":       ([(194, 110), (194, 134), (176, 151), (149, 156), (125, 144), (116, 122), (125, 100),
                   (149, 88)], 2.2),
    "pier":      ([(194, 120), (184, 122), (170, 122)], 2.0),
    "pad_w":     ([(60, 130), (78, 128)], 2.0),
    "pad_e":     ([(254, 122), (232, 122)], 2.0),
    "pad_forge": ([(166, 22), (184, 22)], 2.0),
    "pad_eng":   ([(236, 66), (222, 54)], 2.0),
    "pad_green": ([(72, 74), (64, 64)], 2.0),
}


class _Spec(E.Spec):
    """Groves only on the natural ground, never on the works or out over the drop."""

    def woods_raw(self, gx, gy):
        out = super().woods_raw(gx, gy)
        return np.minimum(out, -(np.asarray(rock_field(gx, gy)) + 3.0))


SPEC = _Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
             mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
             rim={}, rock_rim={}, gaps=GAPS, fords=FORDS, thicket=(0.99, 10.0, 2.0))

#: everyone on the Firmament who isn't trying to kill you (tools/build_fading_firmament_people.py writes them)
NPC_POSITIONS = {
    # the Road's End
    "ff_road_warden":      (116, 240),  # the Aetherian who keeps count of who comes up the road
    # Lastlight: the last people, round the last lit shrine
    "ff_shrine_keeper":    (100, 192),  # keeps the shrine lit; the camp's heart
    "ff_last_magistrate":  (92, 196),   # the Firmament's last magistrate, who stayed with her people
    "ff_orla":             (106, 196),  # Magister Orla Thessan, come north after her student
    "ff_skiffmaster":      (106, 202),  # the flight path: the last skiff that still flies out
    "ff_provisioner":      (90, 204),   # food
    "ff_trader":           (108, 206),  # goods
    "ff_salvager":         (84, 198),   # an Earthborn who salvages what the islands drop
    "ff_child_minder":     (98, 208),   # an Earthborn teacher with the camp's children
    "ff_lamp_cutter":      (104, 212),  # cuts the shrine's crystals, the last crystal-cutter left
    # Forgewatch: the House of Long Memory's scholars at the Threefold Forge
    "ff_long_memory":      (152, 18),   # Archivist of the House of Long Memory, laughed at for a thousand years
    "ff_forge_scholar":    (148, 26),   # her student, who reads Kharad runes
    "ff_earthborn_smith":  (160, 30),   # an Earthborn blacksmith the scholars brought for the forge
    "ff_forgewatch_guard": (144, 20),   # a Lens warden on the camp's edge
    # out on the islands
    "ff_last_resident":    (52, 146),   # the one man in the Emptied Quarter who won't go
    "ff_gardener":         (22, 34),    # tends the one tree still green, on the Last Green
    "ff_turncoat":         (262, 172),  # an Ascendancy quartermaster who's had enough, behind the Siege Line
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("The Wound's Edge", 100, 74, 56, 96, None),
    ("The Moorage", 156, 74, 56, 96, None),
    ("The Road's End", 104, 222, 40, 38, None),
    ("Lastlight", 70, 178, 58, 42, None),
    ("The Emptied Quarter", 24, 120, 62, 58, None),
    ("The Greyfall Gardens", 26, 76, 62, 44, None),
    ("The Coldforges", 52, 26, 74, 50, None),
    ("The Last Green", 6, 14, 36, 32, None),
    ("The Threefold Forge", 136, 0, 62, 40, None),
    ("Forgewatch", 138, 10, 26, 24, None),
    ("The Dead Engines", 198, 30, 92, 76, None),
    ("The Siege Line", 204, 106, 88, 100, None),
    ("The Breaking", 152, 196, 52, 42, None),
]

#: the last trees: dead crystal trees and grey ones, and one or two still green
TREES = {
    "big":   [(SKP + "ff_dead_crystal_tree.png", 7)],
    "mid":   [(SKP + "ff_dead_crystal_tree.png", 6), (SKP + "sk_wind_tree.png", 6)],
    "small": [(SKP + "ff_dead_flowers.png", 3), (SKP + "sk_wind_tuft.png", 3)],
    "woods": [(SKP + "ff_dead_crystal_tree.png", 7)],
}


def _grid():
    ys, xs = np.mgrid[0:H, 0:W]
    return xs + 0.5, ys + 0.5


def drop_mask(L=None):
    return sea(*_grid()) > 0


def on_a_span(pad=1.5):
    return span_mask(*_grid()) < pad


def on_the_works():
    gx, gy = _grid()
    return _works_raw(gx, gy) < 1.0


def in_a_camp():
    gx, gy = _grid()
    m = np.zeros((H, W), bool)
    for (cx, cy, rx, ry) in [(122, 244, 8, 6), (100, 200, 18, 13), (152, 24, 14, 9), (52, 146, 6, 5),
                             (22, 34, 6, 5), (262, 172, 6, 5)]:
        m |= (np.abs(gx - cx) < rx) & (np.abs(gy - cy) < ry)
    return m


def open_the_drop(L):
    z = L.z
    for y, x in zip(*np.nonzero(drop_mask(L))):
        z.set_tile(int(x), int(y), "grass", "base")
        z.set_tile(int(x), int(y), "cliff", "collision")


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "The dying heart of the sky: a ring of broken islands round a hole in it, the forges "
                             "gone cold, and the last people round the last lit shrine.",
                             "Eastern Kingdoms - The World Tree", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    open_the_drop(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.place_links(L, LINKS)
    E.seal_unreachable(L, START)
    dress(L)
    E.build_free_mask(L, NPC_POSITIONS.values())
    for lm in L.z.landmarks:
        ax, ay, w, h = lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]
        L.free_mask[max(0, ay):ay + h + 1, max(0, ax - 1):ax + w + 1] = False
    L.free_mask[drop_mask(L)] = False
    L.free_mask[on_a_span()] = False
    L.free_mask[in_a_camp()] = False
    L.free_mask[on_the_works()] = False
    for _k, a, b in LINKS:                      # keep the pads and their landings clear
        for (x, y) in (a, b):
            L.free_mask[max(0, y - 3):y + 5, max(0, x - 3):x + 4] = False
    E.scatter_trees(L, TREES, seed=5901, spacing=11.0, grove_keep=0.45)
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    hanging(L)
    link_pads(L)
    return L


def sprinkle(L):
    """Dead flowers, dim shards and wind tufts on the natural ground; nothing on the works, the roads or the bridges."""
    import random
    rnd = random.Random(5903)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    kinds = [("ff_dim_shards", 0.015, 16), ("ff_dead_flowers", 0.035, 18), ("sk_wind_tuft", 0.05, 12)]
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


CHEST_SPOTS = [(128, 244), (76, 206), (36, 140), (72, 168), (40, 96), (82, 92), (66, 50), (108, 54), (16, 28),
               (190, 28), (218, 60), (268, 80), (276, 132), (228, 160), (172, 230), (120, 150), (150, 160),
               (188, 140)]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def hanging(L):
    """What hangs over the drop, drawn and not walked (added last): the general's fleet moored over the Wound, a falling
    island going down past the Breaking, and the tears in the sky over the Wound's middle."""
    from PIL import Image
    for (name, x, y, h) in [("ae_airship_great", 152, 142, 18), ("ae_airship_war", 150, 112, 13),
                            ("ff_void_rift", 136, 128, 10), ("ff_falling_island", 262, 236, 14),
                            ("ff_falling_island", 20, 236, 12), ("ff_falling_island", 282, 24, 9),
                            ("ff_falling_island", 206, 234, 8)]:
        path = f"{BLD}{name}.png"
        iw, ih = Image.open(path).size
        w = max(1, round(h * iw / ih))
        L.z.add_landmark(path, x - w // 2, y - h + 1, w, h, solid=False)


def link_pads(L):
    """Kyle's LK1 art (tools/link_art.py): the Firmament's skip-stones are failing, cracked and flickering violet, and the
    Ascendancy has refitted the one at its own Siege Line; the dusk currents rise out of old updraft rings."""
    from tools.link_art import dress_links
    dress_links(L.z, [lk for lk in LINKS if lk[1] != (230, 122)], pads={"skipstone": "lk_skipstone_failing"})
    dress_links(L.z, [lk for lk in LINKS if lk[1] == (230, 122)], pads={"skipstone": "lk_skipstone_ascendancy"})


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
        while 0 < x + dx < W - 1 and 0 < y + dy < H - 1 and float(sea(x + dx, y + dy)) < -0.5:
            x, y = x + dx, y + dy
        return x, y

    # ---- the wellstones' falls: every pool still running spills off the nearest edge
    for (px, py, dx, dy) in [(104, 202, 1, 0), (54, 104, -1, 0), (154, 26, 0, -1), (184, 224, 0, 1)]:
        S("sk_edge_falls", *rim(px, py, dx, dy), 5, solid=False, allow_overlap=True)
    # ---- the Road's End: the road's last marker, and the warden's post
    B("ae_crystal_beacon", 130, 240, 5)
    B("ae_guard_post", 110, 234, 6)
    # ---- Lastlight: the shrine still lit, the camp round it
    S("ff_lit_shrine", 100, 188, 5)
    S("ff_last_crystal", 95, 186, 3)
    B("ae_refugee_pavilion", 86, 190, 7)
    B("ae_refugee_pavilion", 114, 192, 7)
    S("ff_patched_tent", 82, 210, 5)
    S("ff_patched_tent", 116, 214, 5)
    S("ff_camp_fire", 100, 200, 3, solid=False)
    S("ff_salvage", 78, 202, 3)
    B("ae_skiff_dock", 122, 204, 6)
    B("ae_soup_table", 92, 210, 3)
    # ---- the Emptied Quarter: the houses left open, the kiosks, the toy on the step
    for (x, y) in [(46, 136), (70, 140), (78, 160), (46, 162), (62, 172), (30, 130)]:
        S("ff_abandoned_home", x, y, 7)
    S("ff_empty_kiosk", 58, 146, 4)
    S("ff_empty_kiosk", 66, 160, 4)
    S("ff_toy_bird", 56, 158, 2, solid=False)
    S("ff_fallen_lantern", 72, 150, 2, solid=False)
    S("ff_toppled_magister", 50, 126, 5)
    # ---- the Greyfall Gardens: the grey gardens, the dry fountain
    S("ff_grey_garden", 46, 92, 4)
    S("ff_grey_garden", 70, 110, 4)
    S("sk_dry_fountain", 60, 100, 5)
    B("ae_garden_pavilion", 42, 110, 7)
    # ---- the Last Green: the one tree still alive
    S("ff_last_tree", 26, 28, 5)
    # ---- the Coldforges: the forges gone dark, the Ascendancy's salvage crews
    S("ff_cold_forge", 78, 56, 6)
    S("ff_cold_forge", 104, 40, 6)
    B("ae_sky_forge", 92, 38, 10)
    S("ff_burnt_crystal", 84, 66, 3)
    S("ff_burnt_crystal", 112, 54, 3)
    B("ae_supply_crates", 98, 60, 3)
    B("ae_chain_hoist", 116, 46, 5)
    # ---- the Threefold Forge: three hearths round the old anvil-stone, and the way down
    B("kh_forge", 166, 12, 7)                       # the giant's hearth
    B("vy_storm_forge", 184, 30, 6)                 # the singer's hearth, on its perch
    B("ae_great_forge", 166, 34, 7)                 # the cutter's hearth
    S("sk_rune_circle_broken", 172, 22, 6, solid=False)
    L.prop("ent_door_stairs_down", 178, 11, 5, path_dir=ENT, solid="core", nudge=0, allow_overlap=True)
    # ---- Forgewatch: the House of Long Memory's tents
    B("ae_field_pavilion", 150, 14, 6)
    S("ff_patched_tent", 144, 28, 5)
    B("ae_chart_desk", 158, 16, 3)
    # ---- the Dead Engines: the great engines gone black, the snapped anchors, the way inside
    B("ae_dead_engine", 244, 44, 12)                # the Hollow Engine itself, its hatch at its foot
    L.prop("ent_door_bronze_pipe", 244, 47, 5, path_dir=ENT, solid="core", nudge=0, allow_overlap=True)
    S("ff_dead_engine", 228, 76, 8)
    S("ff_dead_engine", 262, 84, 8)
    S("ff_snapped_anchor", 246, 100, 5)
    S("ff_broken_pylon", 258, 62, 5)
    # ---- the Siege Line: the trenches, the guns, the command table
    S("ff_trench", 236, 140, 4)
    S("ff_trench", 236, 160, 4)
    S("ff_artillery_post", 232, 150, 5)
    S("ff_barricade", 240, 132, 3)
    S("ff_barricade", 240, 170, 3)
    S("ff_command_table", 258, 150, 3)
    S("ff_lance_rack", 266, 156, 3)
    B("ae_soldier_tent", 262, 136, 5)
    B("ae_soldier_tent", 268, 166, 5)
    B("ae_war_standard", 254, 140, 6)
    B("ae_storm_artillery", 244, 112, 7)
    # ---- the Breaking: the ground going, what's left of the Veyr's totem and the Kharad's hand
    S("ff_crumbling_edge", 172, 230, 4)
    S("ff_sinking_rock", 190, 228, 5)
    S("ff_sky_rift", 194, 216, 5, solid=False)
    S("ff_fallen_totem", 170, 210, 5)
    S("ff_giant_hand", 186, 212, 6)
    # ---- the Wound's Edge and the Moorage
    S("ff_crystal_crater", 120, 108, 5)
    S("ff_shattered_pylon", 122, 140, 5)
    S("ff_dead_construct", 140, 158, 4)
    B("ae_dock_cradle", 186, 121, 6, road_ok=True)
    B("ae_crystal_beacon", 198, 114, 5)
    B("ae_war_standard", 196, 144, 6)
    S("ff_burnt_pavilion", 176, 156, 5)


def register_baked(zone):
    import os
    zone.sky = {k: v for k, v in SKY.items() if not callable(v)}
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.webp"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_fading_firmament():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
