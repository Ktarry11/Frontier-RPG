"""
Hand-built Ascendant Bastions (300x260), levels 54-57: the Ascendancy's own ground (docs/worldtree_brief.md: "suspended
fortresses and storm-artillery platforms chained between islands, lancer barracks, the shipyards where the ships that
will take the tree are being built"; threat: "the Ascendancy at home: sky lancers, storm artillery, arcane bombardiers,
mechanical flying constructs"). A storm-lit sky.

ANCIENT, NOT NEW (Kyle, 20 Nov 2026). The Bastion of Ascent was a scholar house's college before it was a fortress; the
Ascendancy took it over two hundred years ago, walled it, and has been arming it ever since. The slipways are older
than the Ascendancy too: the long-haulers were built here before the warships were.

THE SHAPE (Kyle: "Stop reusing the same shape"; "dont make them too hard to travel on with tiny paths and snag
points"): a star fort. The Bastion of Ascent is one great island cut to the plan of a fortress, five arrowhead
bastions round a curtain, and on it the citadel: one solid mega-structure of walls, towers and halls (Kyle, 21 Nov
2026: a "Hellfire Citadel" like style, two dungeons "into one mega structure but different entrances"). You walk the
apron round its walls. The south gate, at the head of the causeway, is the Gravity Foundry (56-58); the north gate,
high on the northern bastion, is the Ascendant Spire (60). South of it, down the Ascent
Causeway, the Slipways: a long quay with five finger piers reaching south over the drop like a comb, the warships
hanging in the berths between them. East, the Gunline: four artillery platforms in a straight row on chain bridges.
West, the Proving Grounds' island, and north-west of that the Censor-Archive on its own rock. North-east, the Storm
Harvest. South-west, where the free skiffs dare to land, the wreck of the Dawnspear on its islet, with the Ashwake's
walkable cloud round it. The Firmament Road runs north off the fort's northern bastion, and waits.

    Dawnspear Wreck ........ a fallen war-skiff on an islet, the deserters' camp: the zone's hub and flight path (safe)
    The Ashwake ............ walkable cloud round the wreck, grey with the forges' smoke
    The Proving Grounds .... the lancers' training island: arenas, hangars, the mounted lancers
    The Censor-Archive ..... the Inquisitors' rock, where old records are read and burned
    The Bastion of Ascent .. the star fort: the citadel's walls, the apron round them, and its two gates
    The Ascent Causeway .... the fort's gate down to the quay
    The Slipways ........... the quay and its finger piers, warships building in the berths
    The Yard Pens .......... the Earthborn conscripts' compound at the quay's east end (safe)
    The Gunline ............ four storm-artillery platforms on chains, east of the fort
    The Storm Harvest ...... storm collectors on the north-east rock, drinking the sky's lightning
    The Firmament Road ..... the road north off the fort, toward the Fading Firmament (later)

A SKY MAP: the baker cuts the drop out and hangs rock under the islands and soft cloud under the Ashwake.

HARD CONTRACTS (world/portal_manager.py)
  portals  Aurelion (4,206) <-> the Skydocks; The Gravity Foundry (the citadel's south gate);
           The Ascendant Spire (the citadel's north gate); the Fading Firmament (160,4)
"""
import math

import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_worldtree_sunward_crown import _fbm, _puff, _poly, _seg_dist, _ell, smoothstep_np  # noqa: F401

BAKED_DIR = "assets/tiles/sky/baked_ascendant_bastions"
NAME = "The Ascendant Bastions"
W, H = 300, 260
SKP = "assets/tiles/sky/props/"
BLD = "assets/buildings/"

FORT_C = (160, 92)            # the citadel
CURTAIN_R = 42                # the pentagon of the curtain walls, corner radius
TIP_R = 64                    # how far each arrowhead bastion reaches past its corner
TIPS = (-90, -18, 54, 126, 198)          # one bastion due north, the gate in the south curtain (90)

PORTALS = {(4, 206): "Aurelion", (40, 209): "Dawnspear Wreck", (160, 124): "The Gravity Foundry", (160, 54): "The Ascendant Spire",
           (160, 4): "The Fading Firmament"}
ARRIVALS = [(10, 206), (160, 128), (160, 48), (160, 8), (40, 205)]
#: the citadel stands this many tiles in from the fort's edge; the band outside it is the apron you walk
CITADEL_INSET = 7
LATER_PORTALS = {}
START = (10, 206)          # the skiff landing at the wreck: everything must be reachable from here


def _pt(r, deg, c=FORT_C):
    a = math.radians(deg)
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


#: the curtain: a pentagon with a corner under each bastion
CURTAIN = [_pt(CURTAIN_R, t) for t in TIPS]
#: the bastions: an arrowhead on every corner, its point out past the curtain and its flanks swept back
BASTIONS = [[_pt(TIP_R, t), _pt(46, t + 15), _pt(32, t + 12), _pt(32, t - 12), _pt(46, t - 15)] for t in TIPS]


def _fort(bx, by):
    out = _poly(bx, by, CURTAIN)
    for b in BASTIONS:
        out = np.minimum(out, _poly(bx, by, b))
    return out

# ---------------------------------------------------------------- the other islands
#: the Slipways: the quay, and five finger piers south over the drop
QUAY = [(70, 160), (246, 160), (250, 176), (66, 176)]
FINGERS = [[(x - 6, 172), (x + 6, 172), (x + 6, 220), (x - 6, 220)] for x in (92, 124, 156, 188, 220)]
WRECK = (40, 204, 24, 16, 0.25)               # Dawnspear Wreck's islet
PROVING = (52, 104, 28, 22, 0.15)             # the Proving Grounds
ARCHIVE = (38, 34, 17, 12, 0.3)               # the Censor-Archive
HARVEST = (264, 30, 26, 15, -0.2)             # the Storm Harvest
YARD = (262, 196, 22, 15, 0.1)                # the Yard Pens, off the quay's east end
#: the Gunline: four square platforms in a straight row east of the fort
GUNS = [(234, 110), (260, 128), (284, 148)]
GUN_HALF = 8
#: the Ashwake: walkable cloud round the wreck, south-west
ASHWAKE = [(0, 212), (34, 216), (70, 230), (84, 258), (0, 258)]

#: the bridges, wide (Kyle: no tiny paths). The chain bridges of the Gunline are as wide as the rest.
SPANS = [
    ([(0, 206), (20, 206)], 4.5),                  # the skiff landing onto the wreck's islet
    ([(52, 190), (72, 172)], 4.5),                 # the wreck to the quay's west end
    ([(46, 188), (50, 124)], 4.5),                 # the wreck to the Proving Grounds
    ([(44, 84), (40, 44)], 4.5),                   # the Proving Grounds to the Censor-Archive
    ([(78, 100), (122, 90)], 4.6),                 # the Proving Grounds to the fort's west curtain
    ([(160, 126), (160, 164)], 5.5),               # the Ascent Causeway: the south gate down to the quay
    ([(210, 92), (230, 106)], 4.5),                # the fort's east bastion to the first gun platform
    ([(240, 114), (254, 124)], 4.5),               # gun platform to gun platform, on chains
    ([(266, 132), (278, 142)], 4.5),
    ([(282, 156), (268, 186)], 4.5),               # the last platform down to the Yard Pens
    ([(246, 172), (256, 186)], 4.5),               # the quay's east end to the Yard Pens
    ([(234, 102), (254, 42)], 4.5),                # the first gun platform up to the Storm Harvest
    ([(160, 36), (160, 2)], 4.6),                  # the Firmament Road, north off the northern bastion
    ([(118, 66), (82, 50), (54, 40)], 4.5),        # the fort's north-west bastion to the Censor-Archive
]


def _warp(gx, gy, amp):
    return (gx + amp * _fbm(gx, gy, 1.3) + 0.55 * amp * _puff(gx, gy, 1.9),
            gy + amp * _fbm(gx, gy, 3.1) + 0.55 * amp * _puff(gx, gy, 4.1))


def _square(gx, gy, c, half):
    return np.maximum(np.abs(gx - c[0]), np.abs(gy - c[1])) - half


def _rock_raw(gx, gy):
    """Negative on the fort, the quay and its piers, the gun platforms and the islands, before smoothing. The built
    places keep their straight edges; the natural rocks get a ragged coast."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    bx, by = _warp(gx, gy, 0.9)                 # built: almost straight
    nx, ny = _warp(gx, gy, 4.5)                 # natural: ragged
    edge = 1.6 * _puff(gx, gy, 2.3) + 0.5 * np.sin(0.47 * gx + 0.29 * gy) + 0.4 * np.sin(0.73 * gy - 0.35 * gx)
    built = np.minimum(_fort(bx, by), _poly(bx, by, QUAY))
    for f in FINGERS:
        built = np.minimum(built, _poly(bx, by, f))
    for g in GUNS:
        built = np.minimum(built, _square(bx, by, g, GUN_HALF))
    nat = _ell(nx, ny, *WRECK) + edge
    nat = np.minimum(nat, _ell(nx, ny, *PROVING) + 0.8 * edge)
    nat = np.minimum(nat, _ell(nx, ny, *ARCHIVE) + 0.6 * edge)
    nat = np.minimum(nat, _ell(nx, ny, *HARVEST) + 0.8 * edge)
    nat = np.minimum(nat, _ell(nx, ny, *YARD) + 0.5 * edge)
    return np.minimum(built, nat)


def _cloud_raw(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    wx, wy = _warp(gx, gy, 6.0)
    billow = 2.8 * _puff(gx, gy, 5.4) + 2.0 * _puff(1.7 * gx, 1.7 * gy, 9.2)
    return _poly(wx, wy, ASHWAKE) + billow


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
_SMOOTH_TILES = {"rock": 1.2, "cloudraw": 1.4}      # less than the Anchorfields: a fort keeps its corners


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
    return _sample(_smoothed("cloudraw", _cloud_raw), gx, gy)


def _sea_exact(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    land = np.minimum.reduce([rock_field(gx, gy), cloud_field(gx, gy), span_mask(gx, gy) + 0.1 * _fbm(gx, gy, 1.0)])
    edge = np.maximum.reduce([-1.0 - gx, gx - (W - 1.0), -1.0 - gy, gy - (H - 1.0)])
    return np.maximum(land, edge * 3.0)


def _cloudness_exact(gx, gy):
    from tools.bake_ashenvale import smoothstep
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    other = np.minimum(rock_field(gx, gy), span_mask(gx, gy))
    return (1 - smoothstep(-1.2, 0.8, cloud_field(gx, gy))) * smoothstep(-1.5, 1.5, other)


def sea(gx, gy):
    """The drop: everything that isn't island, cloud or bridge. Extent > 0 is a fall into the sky."""
    return _sample(_cached("sea", _sea_exact), gx, gy)


def cloudness(gx, gy):
    return _sample(_cached("cloud", _cloudness_exact), gx, gy)


def _works_raw(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    bx, by = _warp(gx, gy, 0.9)
    built = np.minimum(_fort(bx, by), _poly(bx, by, QUAY))
    for f in FINGERS:
        built = np.minimum(built, _poly(bx, by, f))
    for g in GUNS:
        built = np.minimum(built, _square(bx, by, g, GUN_HALF))
    return built


def paving_field(P, wp):
    """The fort, the quay and its piers and the gun platforms are paved whole (tools/bake_ashenvale.py's hook)."""
    from tools.bake_ashenvale import smoothstep
    w = _sample(_cached("works", _works_raw), P.gx, P.gy)
    return 1.0 - smoothstep(-2.0, 0.5, w)


def ground_suppress(gx, gy):
    c = cloudness(gx, gy)
    t = np.clip((c - 0.2) / 0.4, 0, 1)
    return t * t * (3 - 2 * t)


#: the renderer's sky and the baker's cut: a storm-lit sky, the sun behind cloud
SKY = {"far": "sky_far_storm", "parallax": 0.35, "drift": 6.0, "wisps": 0.55, "sun": 0.25, "far_tiles": 10,
       "underside": 5.0, "cloud": cloudness, "cloud_lift": 0.14}


def satyr_field(P, wp):
    """The Ashwake's cloud (the "satyr" layer, painted as cloud)."""
    return 1.75 * cloudness(P.gx, P.gy)


def plaza_field(P, wp):
    """The bridges, painted over the gaps only."""
    from tools.bake_ashenvale import smoothstep
    over_the_gap = smoothstep(-1.5, 0.5, rock_field(P.gx, P.gy))
    return 1.9 * (1.0 - smoothstep(-0.4, 1.2, span_mask(P.gx, P.gy))) * over_the_gap


ISLETS = []
#: the Proving Grounds' horse-trough pool and the Storm Harvest's rain basin
LAKES = {"pools": [(40, 112, 5, 3, 0.5, 1.4), (272, 30, 5, 3, 0.0, 2.2)]}
DEEP_SHRINK = {"pools": 5.0}
RIVERS = []
FORDS = []

MESAS = []
RIDGES = []
#: a few wind-bent stands on the natural rocks only
WOODS = [(30, 96, 5, 3, 0.4, 1.0), (276, 22, 4, 3, 0.2, 2.0), (30, 210, 4, 3, 0.6, 0.6)]
BELTS = []
CLEARINGS = [
    (10, 206, 6, 4),            # the skiff landing
    (40, 204, 14, 9),           # Dawnspear Wreck
    (52, 104, 16, 12),          # the Proving Grounds' arenas
    (38, 34, 9, 6),             # the Censor-Archive's yard
    (160, 126, 6, 3),           # before the Foundry's gate
    (160, 50, 5, 3),            # before the Spire's gate
    (160, 166, 18, 5),          # the quay's head
    (262, 196, 12, 8),          # the Yard Pens
    (264, 30, 12, 7),           # the Storm Harvest's collectors
]
#: scorched paving round the guns and the forges ("burned"), the fort's and the quay's paving ("paved"),
#: grey ash on the Ashwake's rocks ("corrupt")
CORRUPT_PATCHES = [(30, 212, 10, 6)]
BURNED_PATCHES = [(254, 116, 40, 24), (264, 30, 16, 10)]
BLUEBELL_PATCHES = [(52, 96, 6, 4)]
PAVED_PATCHES = [(160, 92, 40, 30), (158, 168, 90, 7), (38, 34, 9, 6), (262, 196, 12, 8)]
LUSH = 0.05
GRADE = None
DROP = None

GAPS = [("ell", 10, 206, 4, 3), ("ell", 40, 204, 9, 6), ("ell", 262, 196, 8, 6), ("ell", 160, 126, 4, 2),
        ("ell", 160, 50, 4, 2)]

#: the roads: from the landing through the wreck, and out over every bridge to the fort, the quay and the guns
ROADS = {
    "landing":   ([(12, 206), (24, 206), (40, 204)], 2.4),
    "quay_west": ([(40, 204), (52, 190), (72, 172), (90, 168)], 2.4),
    "proving":   ([(44, 194), (46, 160), (50, 124), (52, 108)], 2.4),
    "archive":   ([(48, 96), (44, 84), (40, 44)], 2.2),
    "fort_west": ([(60, 102), (78, 100), (122, 90)], 2.6),
    "quay":      ([(90, 168), (160, 168), (240, 168)], 2.8),
    "causeway":  ([(160, 168), (160, 126)], 3.0),
    "fort_east": ([(212, 84), (230, 106)], 2.6),
    "gunline":   ([(234, 110), (260, 128), (284, 148), (282, 156), (268, 186)], 2.4),
    "pens":      ([(240, 168), (256, 186), (262, 194)], 2.4),
    "wreck_gate": ([(40, 204), (40, 208)], 2.4),
    "harvest":   ([(234, 102), (254, 42), (264, 34)], 2.2),
    "north":     ([(160, 52), (160, 36), (160, 6)], 2.4),
    "fort_nw":   ([(118, 66), (82, 50), (54, 40)], 2.2),
}


class _Spec(E.Spec):
    """Groves only on the natural rocks, never on the fort, the cloud or out over the drop."""

    def woods_raw(self, gx, gy):
        out = super().woods_raw(gx, gy)
        return np.minimum(out, -(np.asarray(rock_field(gx, gy)) + 3.0))


SPEC = _Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
             mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
             rim={}, rock_rim={}, gaps=GAPS, fords=FORDS, thicket=(0.99, 10.0, 2.0))

#: everyone on the Bastions who isn't trying to kill you (tools/build_ascendant_bastions_people.py writes them)
NPC_POSITIONS = {
    # Dawnspear Wreck's people live on the town's own map now (tools/handbuilt_worldtree_dawnspear_wreck.py)
    # the Yard Pens: the Earthborn conscripts
    "ab_pens_foreman":     (258, 194),  # an Earthborn welder the yard can't do without
    "ab_pens_medic":       (266, 198),  # a nurse among the conscripts
    "ab_pens_rigger":      (262, 202),  # rigs the warships' sails, and remembers every one
    "ab_pens_cook":        (270, 192),  # feeds the pens on what the yard throws away
    # out on the islands
    "ab_archive_clerk":    (32, 38),    # a clerk at the Censor-Archive who copies before he burns
    "ab_harvest_keeper":   (258, 34),   # an old storm-keeper the Ascendancy kept on
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("The Bastion of Ascent", 98, 30, 124, 104, None),
    ("The Ascent Causeway", 148, 126, 24, 36, None),
    ("The Slipways", 62, 156, 192, 68, None),
    ("The Proving Grounds", 20, 78, 66, 52, None),
    ("The Censor-Archive", 14, 18, 50, 34, None),
    ("The Gunline", 222, 92, 78, 74, None),
    ("The Storm Harvest", 234, 10, 64, 40, None),
    ("The Firmament Road", 148, 0, 24, 34, None),
    ("The Ashwake", 0, 220, 90, 40, None),
    ("Dawnspear Wreck", 0, 186, 66, 36, None),
    ("The Yard Pens", 238, 180, 50, 32, None),
]

#: wind-bent trees and tufts on the natural rocks
TREES = {
    "big":   [(SKP + "sk_wind_tree.png", 7)],
    "mid":   [(SKP + "sk_wind_tree.png", 6), (SKP + "sk_sky_birch.png", 6)],
    "small": [(SKP + "sk_wind_tuft.png", 3), (SKP + "sk_heather_clump.png", 3)],
    "woods": [(SKP + "sk_wind_tree.png", 7)],
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


def on_the_works():
    """The fort, the quay and the piers and the gun platforms: built stone, where nothing grows."""
    gx, gy = _grid()
    bx, by = gx, gy
    built = np.minimum(_fort(bx, by), _poly(bx, by, QUAY))
    for f in FINGERS:
        built = np.minimum(built, _poly(bx, by, f))
    for g in GUNS:
        built = np.minimum(built, _square(bx, by, g, GUN_HALF))
    return built < 1.0


def citadel_mask():
    """The citadel's footprint: the curtain's pentagon, CITADEL_INSET tiles in from its walls. Solid. The bastions are
    open platforms projecting from it (gun-platforms, as a star fort's are), and with the apron they're what you walk."""
    gx, gy = _grid()
    return _poly(gx, gy, CURTAIN) < -CITADEL_INSET


def seal_the_citadel(L):
    z = L.z
    for y, x in zip(*np.nonzero(citadel_mask())):
        z.set_tile(int(x), int(y), "cliff", "collision")


def citadel(L):
    """The mega-structure, drawn over its footprint (added last, like the berths). Kyle's sheets AB1 and AB5 (21 Nov
    2026): the curtain is laid in his angled wall pieces, one angle a side, so nothing on the slopes is stepped any more
    (his "Why don't I get angled wall art using the reference wall"), with a round tower on every corner, the Spire's
    gate on the north corner and the Foundry's in the south curtain. Inside it stands the Citadel of Ascent itself, his
    AB1 fortress-city, its own gate behind the Foundry's.

    The pieces as drawn: ab_wall_72r/72l run about 38 degrees, which is the slope of the two northern curtains;
    ab_wall_deep runs straight away from you, which is what the two steep side curtains are made of; ab_wall_flat is
    the south curtain. Every piece is scaled so its wall face matches the old SK6 wall's (11 tiles to 136 px)."""
    from PIL import Image

    S = 11 / 136                                   # tiles per pixel, the SK6 wall's scale
    FACE = 138                                     # the wall face's height in px on every AB5 piece
    pieces = []

    def size(name):
        return Image.open(f"{BLD}{name}.png").size

    def centred(name, cx, cy, h):
        iw, ih = size(name)
        w = max(1, round(h * iw / ih))
        h = max(1, round(h))
        pieces.append((cy + h / 2, name, int(round(cx - w / 2)), int(round(cy - h / 2)), w, h))

    def based(name, x, y, h, late=0.0):
        iw, ih = size(name)
        w = max(1, round(h * iw / ih))
        pieces.append((y + late, name, int(round(x - w / 2)), int(y - h + 1), w, h))

    def run(a, b, names, along_y, thick=0):
        """Lay `names` (cycled) end to end from corner a to corner b. along_y: the piece's run is measured down the
        screen (the end-on pieces) rather than across it; thick: px of the piece's width that's wall thickness, not
        run (a slanted piece's box is wider than its run by about that)."""
        iw, ih = size(names[0])
        span = abs(b[1] - a[1]) if along_y else abs(b[0] - a[0])
        per = ((ih - FACE) if along_y else (iw - thick) * (1.0 if thick else 0.92)) * S
        n = max(1, round(span / per))
        k = span / n / per                         # stretch a touch so they meet the corners exactly
        for i in range(n):
            t = (i + 0.5) / n
            mx, my = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            name = names[i % len(names)]
            jw, jh = size(name)
            h = jh * S * k
            centred(name, mx, my - FACE * S * k / 2, h)   # the box spans the run's top edge to its foot

    inner = CURTAIN_R - CITADEL_INSET + 1
    c = {t: _pt(inner, t) for t in TIPS}
    n_, ne, se, sw, nw = (c[-90], c[-18], c[54], c[126], c[198])
    run(n_, ne, ["ab_wall_72r_1", "ab_wall_72r_2"], False, 28)     # the north-east curtain, down to the right
    run(n_, nw, ["ab_wall_72l_1", "ab_wall_72l_2"], False, 28)     # the north-west curtain, down to the left
    run(ne, se, ["ab_wall_deep_2", "ab_wall_deep_1"], True)        # the steep east curtain
    run(nw, sw, ["ab_wall_deep_2", "ab_wall_deep_1"], True)        # the steep west curtain
    run(sw, se, ["ab_wall_flat_1", "ab_wall_flat_2"], False)       # the south curtain, the Foundry's gate in it
    for t, lit in ((-18, False), (54, True), (126, True), (198, False)):
        x, y = c[t]
        based("ab_corner_tower_lit" if lit else "ab_corner_tower", x, y + 3, 22, late=0.5)
    for (a_, b_) in ((ne, se), (nw, sw)):                          # a tower halfway down each steep curtain
        based("ab_corner_tower", (a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2 + 3, 20, late=0.5)
    based("ab_spire_gate", 160, 60, 20, late=0.5)                 # the Ascendant Spire's gate, on the north corner
    based("ab_foundry_gate", 160, (sw[1] + se[1]) / 2 + 1, 15, late=1.0)   # the Gravity Foundry's, in the south curtain
    based("ab_citadel", 160, 113, 36)                              # the Citadel of Ascent itself
    for (_k, name, ax, ay, w, h) in sorted(pieces, key=lambda p: p[0]):
        L.z.add_landmark(f"{BLD}{name}.png", ax, ay, w, h, solid=False)


def in_a_camp():
    gx, gy = _grid()
    m = np.zeros((H, W), bool)
    for (cx, cy, rx, ry) in [(10, 206, 7, 5), (40, 204, 16, 11), (262, 196, 14, 10), (38, 34, 10, 7),
                             (264, 30, 13, 8), (52, 104, 17, 13)]:
        m |= (np.abs(gx - cx) < rx) & (np.abs(gy - cy) < ry)
    return m


def open_the_drop(L):
    z = L.z
    for y, x in zip(*np.nonzero(drop_mask(L))):
        z.set_tile(int(x), int(y), "grass", "base")
        z.set_tile(int(x), int(y), "cliff", "collision")


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "The Ascendancy's own ground: a star fort cut from a floating island, the shipyards "
                             "where the warships for the tree are built, and storm guns on chains.",
                             "Eastern Kingdoms - The World Tree", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    open_the_drop(L)
    seal_the_citadel(L)
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
    L.free_mask[on_the_works()] = False
    L.free_mask[citadel_mask()] = False
    cloud = on_the_cloud()
    keep = L.free_mask.copy()
    L.free_mask[cloud] = False
    E.scatter_trees(L, TREES, seed=5701, spacing=10.0, grove_keep=0.5)
    sprinkle(L)
    L.free_mask = L.free_mask | (keep & cloud)
    cloud_dress(L, cloud)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    berths(L)
    citadel(L)
    return L


def sprinkle(L):
    """Wind tufts and rubble on the natural rocks; nothing on the works, the roads, the cloud or the bridges."""
    import random
    rnd = random.Random(5703)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    kinds = [("sk_rubble_flowers", 0.02, 18), ("sk_wind_tuft", 0.04, 16)]
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
    """Smoke-grey wisps drifting over the Ashwake."""
    import random
    rnd = random.Random(5707)
    ys, xs = np.nonzero(L.free_mask & cloud)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = 0
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x] or rnd.random() > 0.01 or n >= 10:
            continue
        if L.prop("sk_cloud_wisp", x, y, 3, path_dir=SKP, solid=False, nudge=0):
            n += 1
            L.free_mask[max(0, y - 4):y + 5, max(0, x - 4):x + 5] = False
    L.cloud_clutter = (n,)


CHEST_SPOTS = [(34, 26), (60, 120), (36, 120), (118, 74), (214, 70), (196, 140), (124, 140), (92, 214),
               (156, 214), (220, 214), (230, 166), (260, 132), (284, 152), (270, 36), (282, 200), (50, 244),
               (20, 226), (160, 20)]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def berths(L):
    """The warships building in the berths between the finger piers, and the war-skiffs moored off the quay: drawn,
    not walked, hanging over the drop (added last, so nothing is placed round them)."""
    from PIL import Image
    for (name, x, y, h) in [("ae_airship_war", 108, 212, 18), ("ae_airship_war", 172, 214, 18),
                            ("ae_airship_great", 140, 216, 20), ("ae_war_skiff", 204, 208, 10),
                            ("ae_war_skiff", 236, 214, 10), ("ae_airship_cargo", 76, 214, 12)]:
        path = f"{BLD}{name}.png"
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
        kw.setdefault("nudge", 3)
        return L.prop(n, x, y, h, path_dir=SKP, **kw)

    def rim(x, y, dx, dy):
        while 0 < x + dx < W - 1 and 0 < y + dy < H - 1 and float(sea(x + dx, y + dy)) < -0.5:
            x, y = x + dx, y + dy
        return x, y

    # ---- the wellstones' falls: every pool spills off the nearest edge
    for (px, py, dx, dy) in [(40, 112, -1, 0), (272, 30, 0, -1)]:
        pass  # the edge falls prop is gone (Kyle, 21 Nov 2026: "lets remove this prop... it doesnt work")
    # ---- the Bastion of Ascent: the two gates on the apron (the citadel itself is drawn by citadel(), last)
    B("ae_fortress_gate", 160, 121, 12, solid=False, allow_overlap=True, road_ok=True)
    B("ae_crystal_beacon", 152, 42, 5)
    B("ae_crystal_beacon", 168, 42, 5)
    for t in (-18, 198, 54, 126):                           # a storm gun on every bastion that isn't a road
        x, y = _pt(52, t)
        B("ae_storm_artillery", int(x), int(y), 7)
    # ---- the Slipways: cradles at the pier heads, cranes and crates along the quay
    for x in (92, 124, 156, 188, 220):
        B("ae_dock_cradle", x, 216, 6)            # at the pier's far end, where the next keel will be laid
    B("ae_construct_cradle", 108, 166, 6)
    B("ae_supply_crates", 200, 166, 3)
    B("ae_ammo_rack", 130, 166, 3)
    B("ae_crystal_beacon", 78, 168, 5)
    B("ae_crystal_beacon", 240, 168, 5)
    # ---- the Gunline: a gun on every platform
    for (gx, gy) in GUNS:
        B("ae_storm_artillery", gx + 3, gy - 2, 7)
    B("ae_bombard_tower", 228, 118, 9)
    # ---- the Proving Grounds: the arena rings, the hangar, the tents
    B("ae_lancer_hangar", 66, 92, 9)
    B("ae_soldier_tent", 40, 96, 5)
    B("ae_soldier_tent", 62, 118, 5)
    S("sk_rune_circle_gold", 50, 106, 6, solid=False)
    B("ae_war_standard", 72, 108, 6)
    # ---- the Censor-Archive: the tower, the braziers where the records go
    B("ae_archive", 42, 30, 10)
    B("ae_ceremonial_brazier", 30, 38, 4)
    B("ae_ceremonial_brazier", 50, 40, 4)
    # ---- the Storm Harvest: the collectors drinking the lightning
    B("ae_storm_collector", 256, 26, 10)
    B("ae_storm_collector", 276, 34, 10)
    B("ae_shield_pylon", 266, 22, 7)
    # ---- Dawnspear Wreck: the islet outside the camp's gate (the town is its own map), the war-skiff's mast and
    #      spar sticking up over the wall
    B("ae_war_skiff", 40, 196, 10, allow_overlap=True)
    B("ae_lamp_post", 34, 206, 4)
    B("ae_lamp_post", 46, 206, 4)
    # ---- the Yard Pens: the conscripts' compound
    S("ff_patched_tent", 254, 190, 5)
    S("ff_patched_tent", 272, 202, 5)
    S("ff_camp_fire", 262, 196, 3, solid=False)
    B("ae_soup_table", 268, 190, 3)
    B("ae_fortress_wall", 248, 204, 6)
    # ---- the Firmament Road: the road's first marker off the northern bastion
    B("ae_crystal_beacon", 166, 24, 5)


def register_baked(zone):
    import os
    zone.sky = {k: v for k, v in SKY.items() if not callable(v)}
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.webp"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_ascendant_bastions():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
