"""
Hand-built Sunward Crown (300x240), levels 48-49: the top of the World Tree, above the cloud sea (docs/worldtree_brief.md,
"Twenty questions"). The first sky map, and the biggest map in the game (Kyle, 20 Nov 2026: "So these places can be
large! Don't hold back right bro", and for the Crown, "Even bigger").

THE SHAPE (Kyle, 20 Nov 2026: "Stop reusing the same shape....clouds can be walked on too"). Not limbs off a hub. The
crown is a horseshoe of golden canopy curled round the Hollow, the open heart of the tree's top, where you look straight
down past the trunk to the ground. The horseshoe's mouth opens east, and the cloud pours into it: from there to the far
edge of the map is the Cloud Shelf, cloud thick enough to walk on, rolling and torn open by long rifts where it's thin.
Things stand on the cloud (the Parley Stones, the Sunken Seal in its moat of open sky, the Annex, the survey's dock) and
things float off it (the Chainhold, the Ascendancy's islet; the Driftlets, where the sky beasts graze). The south-east of
the shelf is the Stormbank, cloud gone dark and heavy with lightning.

You come up out of the Cloudbreak through the broken mural (docs/crown_cutscene.md) on the Hollow's south rim. It's the
first place the ground, the sky and the Earth people all stand together, and it's gone wrong already (Kyle, 20 Nov 2026:
"the first zone players get into is where tension is super fucking high"). The survey came to talk, the trolls came to
tell them to get off their tree, and in the middle of the parley the Ascendancy landed. Now the trolls hold Spearhold at
the back of the horseshoe and want war, the survey's guests from Earth sit in the Annex out on the cloud, the Ascendancy
holds the horseshoe's north tip and the islet off it, and the old seal in the cloud is straining under all of it.

    The Mural Gate ........ the Hollow's south rim (100,164): where the Cloudbreak comes out
    The Lookdown .......... a branch out over the Hollow: where you look down at Stranglethorn
    Spearhold ............. the Highbough war camp at the back of the horseshoe (safe)
    The Goldenwood ........ the north arm, the golden forest
    The Taken Crown ....... the north arm's tip, fortified by the Ascendancy
    The Falls of Light .... the south arm, a river of dew running off the crown's edge
    The Parley Stones ..... old stone on the cloud just past the mouth, where the parley was
    The Sunken Seal ....... a ring of Kharad stone sunk in the cloud, ringed by a moat of open sky
    The Chainhold ......... the Ascendancy's islet, chained off the shelf's north edge
    The Cloud Shelf ....... the walkable cloud between them all
    The Annex ............. the survey's guests from Earth, on the cloud (safe)
    The Survey Dock ....... the shelf's east edge: the gangway to Lenswatch, the survey's camp (a town, its own map)
    The Stormbank ......... the shelf's south-east, dark cloud and lightning
    The Driftlets ......... islets chained off the shelf's south-west, over the open sky

THE DROP is the module's sea field. This is a sky map (SKY): the baker cuts the drop out of the ground
(tools/bake_ashenvale.sky_cut), hanging rock under the crown and the islets and soft cloud under the shelf, and the
renderer paints the cloud sea far below (ui/tilemap_renderer._draw_sky). It's collision, never water. No map changes
with quests: the Ascendancy's lines, the wreck at the stones and the cracked seal are there from the start.

HARD CONTRACTS (world/portal_manager.py)
  portals  The Cloudbreak (100,164) <-> its broken mural (32,9); Lenswatch (295,130) <-> its gangway
"""
import numpy as np

from tools import ashenvale_engine as E
from world.chunk_paths import exists as _chunk_exists  # noqa: E402  (.webp, .jpg or .png)

BAKED_DIR = "assets/tiles/sky/baked_sunward_crown"
NAME = "The Sunward Crown"
W, H = 300, 240
SKP = "assets/tiles/sky/props/"
WTP = "assets/tiles/worldtree/props/"
BLD = "assets/buildings/"

PORTALS = {(100, 164): "The Cloudbreak", (295, 130): "Lenswatch", (36, 121): "Spearhold"}
ARRIVALS = [(100, 169), (289, 130), (38, 126)]
LATER_PORTALS = {}
START = (100, 169)      # the Mural Gate: everything must be reachable from here

# ---------------------------------------------------------------- the outlines
#: the crown: the horseshoe's outside edge (the Hollow and the mouth are cut out of it below)
CROWN = [(52, 16), (90, 8), (124, 14), (146, 26), (170, 34), (154, 44), (172, 58), (152, 64), (162, 80),
         (140, 90), (150, 102), (152, 140), (172, 146), (150, 156), (174, 170), (152, 178), (162, 194), (142, 206),
         (112, 224), (76, 228), (44, 216), (20, 192), (10, 160), (16, 126), (8, 94), (16, 60), (30, 32)]
#: the Hollow: the open heart of the tree's top
HOLLOW = [(74, 90), (98, 84), (118, 92), (130, 106), (128, 128), (116, 146), (96, 154), (76, 148), (64, 130),
          (64, 106)]
#: the mouth: where the horseshoe opens east and the cloud comes in
MOUTH = [(116, 96), (162, 98), (162, 140), (116, 142)]
#: the Cloud Shelf: walkable cloud, from the mouth to the far edge
CLOUD = [(150, 26), (190, 16), (202, 32), (196, 60), (214, 80), (252, 90), (296, 94), (296, 162), (290, 200),
         (272, 228), (226, 232), (200, 224), (194, 200), (176, 192), (158, 188), (152, 170), (158, 152), (124, 146),
         (112, 136), (119, 126), (106, 116), (114, 106), (110, 100), (150, 94), (160, 70)]
#: the Stormbank: the shelf's south-east, dark and heavy (painted, not cut)
STORM = [(196, 190), (246, 186), (296, 182), (296, 232), (200, 232)]
#: the islets in the open sky: the Chainhold (a crescent of rock), the three Driftlets
CHAINHOLD = [(212, 32), (236, 20), (260, 26), (270, 42), (256, 58), (236, 54), (224, 46)]
DRIFTLETS = [[(162, 202), (174, 198), (180, 208), (170, 214), (160, 210)],
             [(180, 218), (192, 216), (196, 226), (186, 232), (178, 226)],
             [(152, 222), (162, 220), (166, 230), (156, 234)]]
#: the Sunken Seal: a ring of old stone in the cloud, with a moat of open sky round it, crossed at two necks
SEAL = (178, 62)
SEAL_MOAT = (13.0, 17.5)                 # inner and outer radius of the moat
SEAL_NECKS = [(-1.6, 0.30), (3.0, 0.32)]   # (angle in radians, half-width in radians): south-west and west

#: the rifts: long tears in the shelf where the cloud is too thin to hold you. (points, half-width)
RIFTS = [
    ([(202, 34), (208, 52), (226, 70), (252, 80), (298, 82)], 5.0),          # the north rift, under the Chainhold
    ([(150, 178), (166, 184), (180, 182)], 5.0),                              # the south rift, west reach
    ([(194, 180), (214, 176), (232, 184), (243, 182)], 5.5),                  # ... middle reach (necks either side)
    ([(256, 180), (276, 178), (298, 184)], 5.5),                              # ... east reach
    ([(222, 106), (234, 114), (248, 112)], 3.0),                              # a tear north of the Annex
    ([(258, 150), (268, 160), (274, 172)], 2.6),                              # a tear south of the dock
    ([(196, 140), (206, 152)], 2.6),                                          # a tear west of the Annex
]
#: bays bitten into the crown's outside edge, where the canopy has broken away
BAYS = [(16, 84, 15, 7, 0.3), (64, 228, 16, 8, 0.0), (120, 14, 14, 7, 0.5), (16, 198, 12, 9, 0.6), (146, 206, 11, 6, 0.8)]
#: the crown's own sky wells: holes in the canopy
WELLS = [(40, 168, 5, 4, 0.4), (58, 76, 5, 3, 1.1), (126, 54, 4, 6, 0.3), (30, 112, 3, 5, 0.0)]
#: the Lookdown: a branch out over the Hollow from its south rim
PIER = ([(92, 156), (90, 140), (88, 126)], 3.6)
PIER_END = (88, 124, 5.0, 3.6)
#: chains and planks across the open sky
BRIDGES = [
    ([(198, 38), (206, 37), (214, 36)], 2.4),           # the shelf to the Chainhold
    ([(170, 192), (170, 199)], 2.2),                    # the shelf to the first Driftlet
    ([(176, 210), (183, 218)], 2.0),                    # first Driftlet to the second
    ([(164, 211), (160, 221)], 2.0),                    # first Driftlet to the third
    ([(288, 130), (299, 130)], 2.6),                    # the survey's gangway to Lenswatch
]


# ---------------------------------------------------------------- the field helpers
def _fbm(gx, gy, k=0.0):
    """A cheap, smooth, non-repeating wobble in about -1..1 (sums of sines at odd angles and scales)."""
    out = 0.0
    for i, (f, a, th) in enumerate([(0.041, 1.0, 0.3), (0.073, 0.6, 1.9), (0.13, 0.35, 2.7), (0.23, 0.2, 4.1),
                                    (0.41, 0.1, 5.3)]):
        c, s = np.cos(th + k), np.sin(th + k)
        out = out + a * np.sin(f * (gx * c + gy * s) + 1.7 * i + k * 3.1)
    return out / 2.25


def _puff(gx, gy, k=0.0):
    """Billows: a tighter, lumpier wobble than _fbm, for cloud edges and leafy scallops (about -1..1)."""
    out = 0.0
    for i, (f, a, th) in enumerate([(0.16, 1.0, 0.5), (0.27, 0.6, 2.2), (0.45, 0.3, 3.6)]):
        c, s = np.cos(th + k), np.sin(th + k)
        out = out + a * np.sin(f * (gx * c + gy * s) + 2.1 * i + k * 1.7) * np.sin(f * 0.8 * (gy * c - gx * s) + k)
    return out / 1.2


def smoothstep_np(a, b, x):
    t = np.clip((np.asarray(x, float) - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def _poly(gx, gy, pts):
    """Signed distance to a polygon: negative inside."""
    d = np.full(np.shape(gx), 1e9)
    inside = np.zeros(np.shape(gx), bool)
    n = len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        vx, vy = x1 - x0, y1 - y0
        t = np.clip(((gx - x0) * vx + (gy - y0) * vy) / float(vx * vx + vy * vy), 0, 1)
        d = np.minimum(d, np.hypot(gx - (x0 + t * vx), gy - (y0 + t * vy)))
        cross = ((y0 > gy) != (y1 > gy)) & (gx < (x1 - x0) * (gy - y0) / ((y1 - y0) if y1 != y0 else 1e-9) + x0)
        inside ^= cross
    return np.where(inside, -d, d)


def _seg_dist(gx, gy, pts):
    out = np.full(np.shape(gx), 1e9)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        vx, vy = x1 - x0, y1 - y0
        t = np.clip(((gx - x0) * vx + (gy - y0) * vy) / float(vx * vx + vy * vy), 0, 1)
        out = np.minimum(out, np.hypot(gx - (x0 + t * vx), gy - (y0 + t * vy)))
    return out


def _ell(gx, gy, cx, cy, rx, ry, rot=0.0):
    c, s = np.cos(rot), np.sin(rot)
    dx, dy = gx - cx, gy - cy
    u, v = dx * c + dy * s, -dx * s + dy * c
    return (np.hypot(u / rx, v / ry) - 1.0) * min(rx, ry)


def _warp(gx, gy, amp):
    return (gx + amp * _fbm(gx, gy, 0.7) + 0.55 * amp * _puff(gx, gy, 0.9),
            gy + amp * _fbm(gx, gy, 2.3) + 0.55 * amp * _puff(gx, gy, 3.3))


def crown_field(gx, gy):
    """Negative on the crown's canopy (the horseshoe, the Hollow and the mouth cut out, the wells too)."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    wx, wy = _warp(gx, gy, 8.0)
    leafy = (2.2 * _puff(gx, gy, 1.1) + 0.6 * np.sin(0.47 * gx + 0.31 * gy)
             + 0.4 * np.sin(0.61 * gy - 0.22 * gx + 1.3))                                 # scalloped leaf edge
    # where the canopy meets the cloud it frays: tongues of gold leaf reaching out into the cloud, cloud reaching back
    fray = smoothstep_np(118.0, 150.0, gx) * 4.5 * _puff(1.6 * gx, 1.6 * gy, 7.7)
    c = _poly(wx, wy, CROWN) + leafy + fray
    c = np.maximum(c, -(_poly(wx, wy, HOLLOW) + 0.6 * leafy))
    c = np.maximum(c, -_poly(wx, wy, MOUTH))
    for (hx, hy, rx, ry, rot) in WELLS + BAYS:
        c = np.maximum(c, -(_ell(gx, gy, hx, hy, rx, ry, rot) + 0.4 * leafy))
    pier = _seg_dist(gx, gy, PIER[0]) - PIER[1] + 0.2 * leafy
    pier = np.minimum(pier, _ell(gx, gy, *PIER_END))
    return np.minimum(c, pier)


def cloud_field(gx, gy):
    """Negative on the walkable cloud of the shelf (the rifts and the seal's moat cut out)."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    wx, wy = _warp(gx, gy, 7.0)
    billow = (3.2 * _puff(gx, gy, 4.4) + 1.0 * _fbm(gx * 1.9, gy * 1.9, 4.4)
              + 2.5 * _puff(1.7 * gx, 1.7 * gy, 8.1))                            # soft, rolling, lumpy edges
    c = _poly(wx, wy, CLOUD) + billow
    for pts, hw in RIFTS:
        r = _seg_dist(wx, wy, pts) - hw * (0.75 + 0.45 * _fbm(gx, gy, 5.5)) + 0.6 * billow
        c = np.maximum(c, -r)
    sx, sy = SEAL
    rr = np.hypot(gx - sx, gy - sy)
    ang = np.arctan2(gy - sy, gx - sx)
    moat = np.maximum(SEAL_MOAT[0] - rr, rr - SEAL_MOAT[1]) + 0.5 * billow
    for a0, hw in SEAL_NECKS:
        da = np.abs(np.angle(np.exp(1j * (ang - a0))))
        moat = np.maximum(moat, (hw - da) * rr)                            # the necks: cloud left standing
    return np.maximum(c, -moat)


def isle_field(gx, gy):
    """Negative on the islets in the open sky: rock, so they hang rock below them."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    wx, wy = _warp(gx, gy, 2.0)
    c = _poly(wx, wy, CHAINHOLD)
    for d in DRIFTLETS:
        c = np.minimum(c, _poly(wx, wy, d))
    return c


def bridge_mask(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    out = np.full(np.shape(gx), 99.0)
    for pts, hw in BRIDGES:
        out = np.minimum(out, _seg_dist(gx, gy, pts) - hw)
    return out


def _sea_exact(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    land = np.minimum.reduce([crown_field(gx, gy), cloud_field(gx, gy), isle_field(gx, gy),
                              bridge_mask(gx, gy) + 0.1 * _fbm(gx, gy, 1.0)])
    edge = np.maximum.reduce([2.0 - gx, gx - (W - 1.0), 2.0 - gy, gy - (H - 3.0)])
    return np.maximum(land, edge * 3.0)


def _cloudness_exact(gx, gy):
    from tools.bake_ashenvale import smoothstep
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    other = np.minimum.reduce([crown_field(gx, gy), isle_field(gx, gy), bridge_mask(gx, gy)])
    return (1 - smoothstep(-1.2, 0.8, cloud_field(gx, gy))) * smoothstep(-1.5, 1.5, other)


def _storminess_exact(gx, gy):
    from tools.bake_ashenvale import smoothstep
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    wx, wy = _warp(gx, gy, 6.0)
    return 1 - smoothstep(-5.0, 3.0, _poly(wx, wy, STORM) + 4.0 * _puff(gx, gy, 6.1))


# ---------------------------------------------------------------- the fields, cached
# The exact fields are polygons and sums of sines, and the baker asks for them at every pixel a dozen times a chunk
# (tools/bake_ashenvale.sky_cut). So each is worked out once on a grid four to a tile and read back with bilinear
# sampling: smooth to well under a pixel's worth of tile, and the bake goes from over an hour to minutes.
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
    out = map_coordinates(arr, [np.ravel(fy), np.ravel(fx)], order=1, mode="nearest")
    return out.reshape(shp)


def sea(gx, gy):
    """The drop: everything that isn't crown, cloud, islet or bridge. Extent > 0 is a fall into the sky."""
    return _sample(_cached("sea", _sea_exact), gx, gy)


def cloudness(gx, gy):
    """0..1: how much this spot is the shelf's cloud rather than canopy, rock or plank (the baker's cloud material, and
    the soft underside sky_cut hangs under the cloud's edge instead of rock)."""
    return _sample(_cached("cloud", _cloudness_exact), gx, gy)


def storminess(gx, gy):
    """0..1: the Stormbank's dark cloud."""
    return _sample(_cached("storm", _storminess_exact), gx, gy)


def ground_suppress(gx, gy):
    """Where the canopy's own materials (gold grass, roots, the worn trails) mustn't show: out on the cloud, which
    doesn't grow grass or hold a footprint (tools/bake_ashenvale.build_scores)."""
    c = cloudness(gx, gy)
    t = np.clip((c - 0.2) / 0.4, 0, 1)
    return t * t * (3 - 2 * t)



#: the renderer's sky (tilemap.sky) and the baker's cut: the gold cloud sea far below, wisps, full sun
SKY = {"far": "sky_far_gold", "parallax": 0.35, "drift": 6.0, "wisps": 0.55, "sun": 0.5, "far_tiles": 10,
       "underside": 5.0, "cloud": cloudness, "cloud_lift": 0.16}


def satyr_field(P, wp):
    """The walkable cloud (the "satyr" layer, painted as cloud): strong enough to win over the canopy's materials
    everywhere on the shelf, except where the Stormbank darkens it, the old stone shows through, or a plank runs."""
    from tools.bake_ashenvale import smoothstep
    cl = cloudness(P.gx, P.gy)
    pav = [P.blob(*b, 0.55, wp) for b in PAVED_PATCHES]
    pv = np.maximum.reduce(pav) if pav else 0
    return 1.75 * cl * (1 - storminess(P.gx, P.gy)) * (1 - smoothstep(0.35, 0.7, pv))


def burned_field(P, wp):
    """The Stormbank's dark cloud (the "burned" layer): wherever the shelf's cloud is stormy."""
    return storminess(P.gx, P.gy) * cloudness(P.gx, P.gy)


def plaza_field(P, wp):
    """The chain bridges' planks and the gangway (the "plaza" layer), strong enough to win near the drop."""
    from tools.bake_ashenvale import smoothstep
    return 1.9 * (1.0 - smoothstep(-0.4, 1.2, bridge_mask(P.gx, P.gy)))


ISLETS = []
#: dew caught in the canopy: the Goldenwood's pools, the spring the Falls of Light run from, a pool at Spearhold
LAKES = {"pools": [(64, 46, 7, 4, 0.4, 0.6), (92, 30, 4, 3, 0, 1.4), (88, 186, 5, 3, 0.2, 2.1),
                   (28, 140, 4, 3, 0, 0.9)]}
DEEP_SHRINK = {"pools": 6.0}
#: the Falls of Light: the dew runs from the spring south-west across the south arm and off the crown's edge
RIVERS = [([(86, 190), (74, 196), (60, 202), (46, 210), (32, 222)], 2.2, -4.0)]
FORDS = [(66, 200, 6)]

MESAS = []
RIDGES = []
#: thickets of golden canopy you walk round, not through
WOODS = [
    (52, 60, 6, 4, 0.7, 1.0), (88, 22, 5, 3, 0.2, 2.0), (24, 148, 5, 3, 0.0, 1.4), (70, 214, 5, 3, 0.8, 0.8),
    (122, 190, 5, 3, 0.4, 2.2), (40, 92, 4, 3, 1.2, 0.6), (112, 40, 4, 3, 0.3, 1.7),
]
BELTS = []
CLEARINGS = [
    (100, 166, 10, 6),          # the Mural Gate
    (88, 124, 5, 3),            # the Lookdown
    (36, 122, 14, 10),          # Spearhold
    (66, 52, 10, 7),            # the Goldenwood's glade
    (138, 40, 12, 9),           # the Taken Crown's fort
    (60, 198, 9, 5),            # the Falls of Light
    (176, 118, 13, 9),          # the Parley Stones
    (178, 62, 11, 11),          # the Sunken Seal
    (240, 38, 12, 8),           # the Chainhold
    (238, 140, 14, 9),          # the Annex
    (280, 130, 8, 5),           # the Survey Dock
    (246, 210, 10, 7),          # the Stormbank's heart
]
#: gold flowers on the crown ("bluebell"). The Stormbank's dark cloud is "burned", painted from storminess (burned_field)
CORRUPT_PATCHES = []
BURNED_PATCHES = []
BURN_SUPPRESS = 2.5
BLUEBELL_PATCHES = [(48, 176, 8, 5), (80, 40, 7, 4), (22, 100, 5, 6), (124, 172, 6, 4), (36, 60, 5, 4),
                    (106, 206, 7, 4)]
#: no paved ground: the stones, the seal and the Ascendancy's camps are things standing on the canopy and the cloud
PAVED_PATCHES = []
LUSH = 0.0
GRADE = None
DROP = None

GAPS = [("ell", 100, 169, 6, 3), ("ell", 289, 130, 4, 3), ("ell", 176, 118, 8, 5), ("ell", 36, 122, 9, 6),
        ("ell", 238, 140, 8, 5)]

#: the trails. On the canopy they're worn bark; out on the cloud they don't show (cloud doesn't hold a footprint),
#: but they keep the way clear between the places people walk.
ROADS = {
    "gate_west":  ([(100, 170), (84, 176), (66, 172), (50, 158), (40, 140), (37, 128)], 2.6),
    "falls":      ([(78, 176), (70, 188), (62, 198)], 2.2),
    "back":       ([(34, 112), (30, 92), (36, 72), (52, 56), (64, 50)], 2.4),
    "north_arm":  ([(70, 48), (92, 38), (114, 32), (132, 38)], 2.4),
    "lookdown":   ([(94, 160), (91, 144), (88, 128)], 1.8),
    "gate_east":  ([(108, 168), (126, 166), (142, 156), (150, 140), (164, 126), (172, 120)], 2.6),
    "stones_seal": ([(178, 112), (174, 96), (170, 80), (172, 70)], 2.2),
    "seal_crown": ([(166, 60), (152, 52), (142, 46)], 2.2),
    "stones_annex": ([(186, 120), (206, 126), (226, 136)], 2.4),
    "annex_dock": ([(250, 138), (266, 132), (282, 130)], 2.4),
    "chain":      ([(184, 50), (192, 42), (198, 38)], 2.0),
    "storm":      ([(240, 150), (246, 168), (250, 182), (248, 200)], 2.2),
    "drift":      ([(186, 128), (176, 150), (168, 172), (170, 190)], 2.2),
}


class _Spec(E.Spec):
    """The golden thickets stay on the crown: nothing grows out over the drop or on the cloud."""

    def woods_raw(self, gx, gy):
        out = super().woods_raw(gx, gy)
        return np.minimum(out, -(np.asarray(crown_field(gx, gy)) + 3.0))


SPEC = _Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
             mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
             rim={}, rock_rim={}, gaps=GAPS, fords=FORDS, thicket=(0.99, 10.0, 2.0))

#: everyone on the crown (tools/build_sunward_crown_people.py writes their records); the survey's own people are in
#: Lenswatch, its town
NPC_POSITIONS = {
    # the Mural Gate and the Lookdown
    "sc_gatewatch":      (106, 167),   # a troll who sits by the broken mural and counts who comes up
    "sc_mural_piece":    (94, 168),    # a fallen piece of the mural: walk up to it to watch the cutscene again
    "sc_lookdown":       (90, 127),    # an old troll at the end of the Lookdown, showing the climbers the ground
    # Spearhold is its own small map now (tools/handbuilt_worldtree_spearhold.py); the Annex and the survey's two
    # scholars moved into Lenswatch (22 Nov 2026, Kyle's town rule)
    # the Parley Stones
    "sc_parley_troll":   (182, 121),   # the troll who stood for the Highbough at the parley
    # the Sunken Seal
    # the Falls of Light
    "sc_falls_hunter":   (56, 194),    # a troll hunter after the sky beasts at the falls
    # the Survey Dock
    "sc_dockhand":       (282, 127),   # the survey's dockmaster at the gangway
    # the Taken Crown's edge
    "sc_line_scout":     (118, 36),    # a scout at the edge of the Ascendancy's lines
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("The Cloud Shelf", 110, 20, 190, 220, None),
    ("The Goldenwood", 10, 6, 110, 84, None),
    ("The Falls of Light", 10, 172, 140, 62, None),
    ("The Taken Crown", 104, 10, 60, 62, None),
    ("The Sunken Seal", 158, 42, 40, 40, None),
    ("The Chainhold", 204, 14, 70, 48, None),
    ("The Parley Stones", 158, 104, 36, 28, None),
    ("The Survey Dock", 262, 118, 38, 24, None),
    ("The Stormbank", 194, 184, 106, 56, None),
    ("The Driftlets", 150, 192, 50, 46, None),
    ("Spearhold", 14, 104, 46, 34, None),
    ("The Mural Gate", 84, 156, 34, 20, None),
    ("The Lookdown", 80, 118, 18, 38, None),
]

#: the golden forest: gold trees and weeping gold, silver and blossom where the light is softest
#: (the weeping gold is placed by hand over the Hollow's rim: its drooping canopy reads as ground, so groves of it
#: stack on each other)
TREES = {
    "big":   [(SKP + "sk_gold_tree.png", 8), (SKP + "sk_ruin_tree.png", 7)],
    "mid":   [(SKP + "sk_blossom_tree.png", 6), (SKP + "sk_silver_tree.png", 6), (SKP + "sk_sky_birch.png", 6)],
    "small": [(SKP + "sk_wind_tuft.png", 3), (SKP + "sk_heather_clump.png", 3), (SKP + "sk_sun_lilies.png", 2)],
    "woods": [(SKP + "sk_gold_tree.png", 8)],
}


def _grid():
    ys, xs = np.mgrid[0:H, 0:W]
    return xs + 0.5, ys + 0.5


def drop_mask(L=None):
    return sea(*_grid()) > 0


def on_the_cloud():
    """Tiles of the shelf (not canopy, rock or plank): trees don't grow on cloud."""
    gx, gy = _grid()
    return (cloud_field(gx, gy) < 0) & (crown_field(gx, gy) > 0.5) & (isle_field(gx, gy) > 0.5)


def on_a_bridge(pad=1.5):
    """Tiles on or beside the planks: nothing grows or stands there, or a bridge gets plugged."""
    return bridge_mask(*_grid()) < pad


def in_a_camp():
    """The camps and the stones are laid out by hand; no greenery scattered into them."""
    gx, gy = _grid()
    m = np.zeros((H, W), bool)
    for (cx, cy, rx, ry) in [(36, 122, 16, 11), (238, 140, 14, 9), (280, 130, 10, 5), (100, 166, 11, 6),
                             (176, 118, 14, 9), (178, 62, 12, 12), (138, 40, 13, 9), (240, 38, 13, 9)]:
        m |= (np.abs(gx - cx) < rx) & (np.abs(gy - cy) < ry)
    return m


def open_the_drop(L):
    """The drop is collision, not water: nothing to swim, fish or wade."""
    z = L.z
    for y, x in zip(*np.nonzero(drop_mask(L))):
        z.set_tile(int(x), int(y), "grass", "base")
        z.set_tile(int(x), int(y), "cliff", "collision")


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "The World Tree's golden crown above the cloud: a horseshoe of canopy round the Hollow, "
                             "and the cloud shelf beyond it, where the ground, the sky and the Earth people meet.",
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
    L.free_mask[on_a_bridge()] = False
    L.free_mask[in_a_camp()] = False
    cloud = on_the_cloud()
    keep = L.free_mask.copy()
    L.free_mask[cloud] = False
    # greenery may be scattered; objects may not (Kyle, 20 Nov 2026): every brazier, crate and pylon is placed in dress()
    E.scatter_trees(L, TREES, seed=4901, spacing=8.0, grove_keep=0.5)
    sprinkle(L)
    L.free_mask = keep & L.free_mask | (keep & cloud)
    cloud_dress(L, cloud)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def sprinkle(L):
    """Gold flowers, lilies and clover on the canopy; nothing on the roads, the cloud or over the drop."""
    import random
    rnd = random.Random(4903)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    kinds = [("sk_bellflowers", 0.010, 34), ("sk_clover_patch", 0.016, 26), ("sk_sky_lilies", 0.019, 14),
             ("sk_rubble_flowers", 0.021, 10)]
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
                    L.free_mask[max(0, y - 2):y + 3, max(0, x - 2):x + 3] = False     # one flower per patch
                break
    L.clutter = tuple(n.values())


def cloud_dress(L, cloud):
    """What lies on the cloud: wisps and cloud banks drifting on it, nothing rooted (greenery doesn't grow on cloud)."""
    import random
    rnd = random.Random(4907)
    free = L.free_mask & cloud
    ys, xs = np.nonzero(free)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = {"sk_cloud_wisp": 0, "sk_cloud_bank": 0}
    cap = {"sk_cloud_wisp": 30, "sk_cloud_bank": 10}
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        name = "sk_cloud_wisp" if r < 0.006 else "sk_cloud_bank" if r < 0.008 else None
        if name and n[name] < cap[name]:
            if L.prop(name, x, y, 3 if name == "sk_cloud_wisp" else 5, path_dir=SKP, solid=False, nudge=0):
                n[name] += 1
                L.free_mask[max(0, y - 4):y + 5, max(0, x - 4):x + 5] = False     # wisps drift apart
    L.cloud_clutter = tuple(n.values())


CHEST_SPOTS = [(28, 64), (58, 30), (104, 22), (80, 218), (126, 182), (172, 206), (190, 226), (262, 44),
               (210, 104), (30, 178), (150, 70), (284, 104), (226, 220), (288, 196)]


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

    def T(n, x, y, h, **kw):
        kw.setdefault("solid", "core")
        kw.setdefault("nudge", 3)
        return L.prop(n, x, y, h, path_dir=WTP, **kw)

    # ---- the Mural Gate: the way back down, the broken wall either side of it, the trolls' marker
    B("wt_cloud_way", 100, 162, 12, road_ok=True, allow_overlap=True)
    S("sk_ruin_gate", 90, 166, 7)
    S("sk_broken_column", 112, 165, 5)
    B("gs_loa_totem", 110, 170, 6)
    # ---- the Lookdown: lanterns at the end of the branch, over the Hollow
    S("sk_stone_lantern", 85, 124, 4)
    S("sk_stone_lantern", 92, 124, 4)
    # ---- Spearhold: the way into the war camp at the back of the horseshoe (the camp is its own small map); the
    #      trolls' totems either side of it, wind charms on the branch above
    B("gs_loa_totem", 30, 118, 6)
    B("gs_loa_totem", 42, 118, 6)
    T("wt_wind_charms", 36, 112, 5)
    # ---- the Goldenwood: the pools under the gold, an old shrine the roots have swallowed, a fallen gold log
    S("sk_flower_log", 76, 58, 4)
    S("sk_vine_column", 54, 42, 6)
    S("sk_ivy_wall", 40, 50, 5)
    S("sk_mist_fountain", 70, 46, 5)
    # ---- the Taken Crown: the Ascendancy's line across the north arm, the fort behind it, artillery aimed south-west
    #      down the arm at Spearhold
    B("ae_shield_pylon", 122, 46, 6)
    B("ae_shield_pylon", 124, 30, 6)
    B("ae_storm_artillery", 132, 50, 6)
    B("ae_soldier_tent", 142, 34, 5)
    B("ae_soldier_tent", 148, 42, 5)
    B("ae_war_standard", 138, 44, 6)
    B("ae_guard_post", 150, 30, 6)
    B("ae_ammo_rack", 132, 36, 3)
    B("ae_supply_crates", 144, 50, 3)
    S("ff_trench", 116, 40, 3, solid=False)
    # ---- the Falls of Light: the spring, and the falls where the river goes over the edge
    pass  # the cascade prop is gone too (Kyle, 21 Nov 2026: "these waterfall sprites are terrible here")
    pass  # the edge falls prop is gone (Kyle, 21 Nov 2026: "lets remove this prop... it doesnt work")
    S("sk_boulder", 54, 204, 4)
    # ---- the Parley Stones: old stone on the cloud. The Aetherians' dais on one side, the trolls' spears planted on
    #      the other, the table overturned between them, and the Ascendancy skiff that came down on it, burnt out
    S("sk_mosaic_fragment", 176, 116, 3, solid=False)
    S("sk_rune_plate", 182, 120, 2, solid=False)
    B("ae_dais", 168, 112, 5)
    B("ae_banner", 164, 110, 6)
    B("gs_loa_totem", 186, 124, 6)
    B("ae_council_table", 176, 120, 3)
    B("ae_war_skiff", 186, 110, 9, allow_overlap=True)
    S("ff_burnt_pavilion", 168, 126, 5)
    S("sk_broken_column", 164, 120, 5)
    S("sk_broken_column", 188, 116, 5)
    # ---- the Sunken Seal: a ring of Kharad stone in the cloud, its columns standing round the seal, the seal cracked
    #      with the light coming through, and a kneeling giant at its head
    S("sk_rune_circle_gold", 178, 64, 6, solid=False)
    S("sk_mosaic_fragment", 172, 66, 3, solid=False)
    S("sk_rune_ring", 184, 64, 3, solid=False)
    S("sk_lightning_breach", 178, 62, 5, allow_overlap=True)
    for (x, y) in [(169, 56), (187, 56), (168, 68), (188, 68)]:
        S("sk_broken_column", x, y, 6)
    S("sk_ancestor_pillar", 178, 52, 8)
    B("kh_kneeling_statue", 171, 53, 8)
    S("sk_giant_head", 168, 74, 7)
    # ---- the Chainhold: the Ascendancy's landing, a gate onto the chains and the war skiffs moored on it
    B("ae_fortress_gate", 216, 40, 8, allow_overlap=True)
    B("ae_war_skiff", 250, 30, 9, allow_overlap=True)
    B("ae_lancer_hangar", 240, 28, 7)
    B("ae_bombard_tower", 258, 46, 7)
    B("ae_war_standard", 236, 44, 6)
    B("ae_ammo_rack", 228, 40, 3)
    # ---- where the Annex stood on the cloud: the survey moved its guests into Lenswatch; two lamps left on the path
    B("ae_lamp_post", 226, 138, 4)
    B("ae_lamp_post", 252, 146, 4)
    # ---- the Survey Dock: the dock's pylons and the survey skiff moored off the cloud's edge
    B("ae_skiff_dock", 280, 135, 6)
    B("ae_survey_skiff", 288, 142, 9, allow_overlap=True)
    B("ae_lamp_post", 276, 126, 4)
    B("ae_crystal_crates", 284, 125, 3)
    # ---- the Stormbank: lightning standing on the cloud, and what it's struck
    S("vy_lightning_spire", 246, 206, 9)
    S("sk_rune_circle_storm", 236, 212, 5, solid=False)
    S("sk_lightning_breach", 270, 214, 5)
    S("sk_crag", 222, 220, 5)
    # ---- the Driftlets: grass islets over the open sky, and the chains that hold them
    S("sk_float_rock", 186, 224, 4)
    B("sk_wellspring", 170, 206, 5)
    # ---- the light: gold trees lean in over the Hollow's rim
    for (x, y) in [(70, 96), (124, 112), (72, 150), (118, 148)]:
        S("sk_weeping_gold", x, y, 7)


def register_baked(zone):
    import os
    zone.sky = {k: v for k, v in SKY.items() if not callable(v)}
    if os.path.isdir(BAKED_DIR) and (os.path.exists(f"{BAKED_DIR}/ground_0_0.webp")
                                     or _chunk_exists(f"{BAKED_DIR}/ground_0_0.jpg")):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_sunward_crown():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS) + list(LATER_PORTALS),
                              npc=list(NPC_POSITIONS.values()))
