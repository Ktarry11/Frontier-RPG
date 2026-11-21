"""
Hand-built Anchorfields (300x250), levels 51-54: the engine country of the Aetherian continent (docs/worldtree_brief.md:
"islands held up by crystal anchors and gravity engines the size of towers, the scholar houses' estates and
observatories among them, and the first anchors failing, islands tilting and dropping"; threats: "the engines wake
wrong (constructs, arcane overload, gravity gone strange); the Ascendancy seizing the anchors; the sky's own storms").
A dawn sky, low gold light.

ANCIENT, NOT NEW (Kyle, 20 Nov 2026: "aurelion is ancient, we are new. we are learning lore not having it being new to
the world"). The anchors have held this shelf up for a thousand years and the Anchor-Wardens have tended them for as
long. The failing is a long decline that's lately got faster. The Dropfield is where an anchor gave out centuries ago
and its island fell. The player walks into the middle of all of it.

THE SHAPE (Kyle: "Stop reusing the same shape"; "dont make them too hard to travel on with tiny paths and snag points"):
a shattered plate. One great shelf of stone, cracked by gravity going wrong into five big shards with open sky in the
cracks between them, wide stone bridges over every crack. Three anchor towers stand on it, each in its own chain-field.
Off the shelf: the House of Measures' observatory on its own rock to the north-east, the Listing Isle tipped off the
east edge with the Earthborn camped on it, the old aqueduct arm you come in on from the west, and the Dropfield to the
south-west, a bank of walkable cloud strewn with what's left of the island that fell.

    The Aqueduct Arm ....... the old aqueduct's arm west to the Spillway (the way in from the Celestial Expanse)
    The Estates ............ the north-west shard: an old house's estate, half shut up since the shelf began to lean
    The First Anchor ....... the north-east shard: the oldest anchor tower, still holding, in its chain-field
    Keelstone .............. the Anchor-Wardens' hold at the First Anchor's foot, the zone's hub and flight path (safe)
    The Gearwork ........... the south-west shard: the engines that feed the anchors, waking wrong
    The Seized Anchor ...... the east shard: the second anchor, taken by the Ascendancy
    The Slipping Anchor .... the south-east shard: the third anchor, failing, and the way down into its keel
    The Listing Isle ....... off the east edge, tipped and still tipping
    Tiltside ............... the Earthborn's camp on the Listing Isle (safe)
    The Observatory ........ the House of Measures' rock, north-east (safe)
    The Dropfield .......... walkable cloud south-west, and the wreck of the island that fell

A SKY MAP: the baker cuts the drop out and hangs rock under the shards and soft cloud under the Dropfield.

HARD CONTRACTS (world/portal_manager.py)
  portals  The Celestial Expanse (3,74) <-> the Spillway; The Keel (its door at the Slipping Anchor)
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_worldtree_sunward_crown import _fbm, _puff, _poly, _seg_dist, _ell, smoothstep_np  # noqa: F401

BAKED_DIR = "assets/tiles/sky/baked_anchorfields"
NAME = "The Anchorfields"
W, H = 300, 250
SKP = "assets/tiles/sky/props/"
BLD = "assets/buildings/"

PORTALS = {(3, 74): "The Celestial Expanse", (188, 206): "The Keel"}
ARRIVALS = [(10, 74), (188, 210)]
START = (10, 74)          # the end of the aqueduct arm: everything must be reachable from here

# ---------------------------------------------------------------- the shelf and its cracks
#: the great shelf of stone, before it cracked
SHELF = [(40, 36), (108, 20), (190, 24), (246, 48), (264, 108), (252, 172), (208, 222), (132, 234), (72, 216),
         (34, 168), (26, 104)]
#: the cracks (polyline, half-width): open sky between the shards
CRACKS = [
    ([(18, 116), (60, 110), (96, 104), (150, 122), (210, 108), (272, 96)], 4.8),     # west to east, the long crack
    ([(150, 122), (142, 168), (136, 240)], 4.6),                                     # down from the long crack
    ([(112, 14), (118, 62), (96, 104)], 4.4),                                        # up between the Estates and the First Anchor
    ([(272, 152), (206, 150), (142, 168)], 4.4),                                     # between the Seized and Slipping Anchors
]
#: off the shelf
OBSERVATORY = (282, 42, 13, 11, 0.3)        # the House of Measures' rock
LISTING = [(268, 128), (292, 124), (298, 160), (290, 198), (272, 202), (266, 166)]   # the Listing Isle
CHAIN_ISLETS = [(224, 12, 17, 8, 0.25)]                         # held up in the First Anchor's chains
#: the Dropfield: walkable cloud south-west, where the island fell
DROPFIELD = [(4, 190), (44, 182), (84, 204), (92, 232), (56, 248), (10, 244)]

#: the bridges over the cracks and the gaps, wide (Kyle: no tiny paths)
SPANS = [
    ([(0, 74), (40, 74)], 4.0),                    # the Aqueduct Arm, from the west edge onto the Estates
    ([(56, 98), (56, 128)], 4.5),                  # the Estates to the Gearwork
    ([(100, 66), (136, 62)], 4.5),                 # the Estates to the First Anchor
    ([(132, 98), (128, 136)], 4.5),                # the First Anchor to the Gearwork, at the cracks' meeting
    ([(198, 96), (206, 128)], 4.5),                # the First Anchor to the Seized Anchor
    ([(124, 192), (158, 190)], 4.5),               # the Gearwork to the Slipping Anchor
    ([(214, 136), (214, 166)], 4.5),               # the Seized Anchor to the Slipping Anchor
    ([(240, 60), (276, 46)], 4.0),                 # the First Anchor to the Observatory
    ([(254, 138), (276, 144)], 4.0),               # the Seized Anchor to the Listing Isle
    ([(200, 30), (216, 12)], 4.6),                 # the chain-islet, held up on its own chains
]


def _warp(gx, gy, amp):
    return (gx + amp * _fbm(gx, gy, 1.3) + 0.55 * amp * _puff(gx, gy, 1.9),
            gy + amp * _fbm(gx, gy, 3.1) + 0.55 * amp * _puff(gx, gy, 4.1))


def _rock_raw(gx, gy):
    """Negative on the shards, the observatory rock, the Listing Isle and the chain-islets, before smoothing."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    wx, wy = _warp(gx, gy, 5.0)
    edge = 1.8 * _puff(gx, gy, 2.3) + 0.6 * np.sin(0.47 * gx + 0.29 * gy) + 0.4 * np.sin(0.73 * gy - 0.35 * gx)
    c = _poly(wx, wy, SHELF) + edge
    for pts, hw in CRACKS:                          # the cracks cut the shelf into shards
        jag = 0.6 * _puff(1.4 * gx, 1.4 * gy, 6.2)
        c = np.maximum(c, -(_seg_dist(wx, wy, pts) - hw - jag))
    c = np.minimum(c, _poly(wx, wy, LISTING) + 0.7 * edge)
    c = np.minimum(c, _ell(gx, gy, *OBSERVATORY) + 0.5 * edge)
    for isl in CHAIN_ISLETS:
        c = np.minimum(c, _ell(gx, gy, *isl) + 0.4 * edge)
    return c


def _cloud_raw(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    wx, wy = _warp(gx, gy, 6.0)
    billow = 2.8 * _puff(gx, gy, 5.4) + 2.0 * _puff(1.7 * gx, 1.7 * gy, 9.2)
    return _poly(wx, wy, DROPFIELD) + billow


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
_SMOOTH_TILES = {"rock": 1.8, "cloudraw": 1.4}


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
    """The drop: everything that isn't shard, cloud or bridge. Extent > 0 is a fall into the sky."""
    return _sample(_cached("sea", _sea_exact), gx, gy)


def cloudness(gx, gy):
    return _sample(_cached("cloud", _cloudness_exact), gx, gy)


def ground_suppress(gx, gy):
    c = cloudness(gx, gy)
    t = np.clip((c - 0.2) / 0.4, 0, 1)
    return t * t * (3 - 2 * t)


#: the renderer's sky and the baker's cut: a dawn sky, the sun low and gold
SKY = {"far": "sky_far_dawn", "parallax": 0.35, "drift": 4.0, "wisps": 0.5, "sun": 0.45, "far_tiles": 10,
       "underside": 5.0, "cloud": cloudness, "cloud_lift": 0.14}


def satyr_field(P, wp):
    """The Dropfield's cloud (the "satyr" layer, painted as cloud)."""
    return 1.75 * cloudness(P.gx, P.gy)


def plaza_field(P, wp):
    """The bridges, painted over the gaps only (on the shards you walk on the shard's own ground)."""
    from tools.bake_ashenvale import smoothstep
    over_the_gap = smoothstep(-1.5, 0.5, rock_field(P.gx, P.gy))
    return 1.9 * (1.0 - smoothstep(-0.4, 1.2, span_mask(P.gx, P.gy))) * over_the_gap


ISLETS = []
#: the Estates' reflecting pool, the Gearwork's coolant pond, Tiltside's spring
LAKES = {"pools": [(54, 62, 7, 4, 0.2, 0.7), (78, 176, 6, 4, 0.5, 1.4), (282, 176, 4, 3, 0.0, 2.2)]}
DEEP_SHRINK = {"pools": 5.0}
RIVERS = []
FORDS = []

MESAS = []
RIDGES = []
#: silver groves in the Estates, a few wind-bent stands out on the shards
WOODS = [(70, 40, 7, 4, 0.4, 1.0), (88, 84, 5, 3, 0.2, 2.0), (236, 88, 5, 3, 0.6, 0.6), (98, 210, 5, 3, 0.1, 1.7)]
BELTS = []
CLEARINGS = [
    (10, 74, 6, 4),             # the end of the aqueduct arm
    (74, 64, 14, 9),            # the Estates' house and lawn
    (168, 80, 14, 9),           # Keelstone
    (190, 52, 12, 9),           # the First Anchor's foot
    (80, 160, 14, 10),          # the Gearwork's engines
    (226, 122, 12, 9),          # the Seized Anchor
    (186, 192, 13, 9),          # the Slipping Anchor
    (188, 210, 5, 3),           # before the Keel's door
    (283, 168, 8, 9),           # Tiltside
    (282, 42, 9, 7),            # the Observatory
]
#: crystal ash where the Slipping Anchor bleeds ("corrupt"), cracked engine paving round the Gearwork ("burned"),
#: sky-flowers on the Estates' lawns ("bluebell"), the estate's and the hold's paving ("paved")
CORRUPT_PATCHES = [(186, 192, 30, 22)]
BURNED_PATCHES = [(80, 160, 30, 22), (226, 122, 20, 14)]
BLUEBELL_PATCHES = [(60, 48, 10, 6), (92, 80, 6, 4), (240, 92, 6, 4)]
PAVED_PATCHES = [(76, 64, 13, 8), (168, 80, 17, 12), (282, 42, 8, 6), (190, 54, 10, 7)]
LUSH = 0.3
GRADE = None
DROP = None

GAPS = [("ell", 10, 74, 4, 3), ("ell", 168, 80, 9, 6), ("ell", 283, 168, 6, 6), ("ell", 282, 42, 6, 5)]

#: the roads: from the arm through the Estates to Keelstone, and out from Keelstone over every bridge
ROADS = {
    "arm":        ([(12, 74), (40, 74), (62, 66), (74, 64)], 2.4),
    "estates":    ([(74, 64), (100, 66), (136, 62), (156, 72), (168, 80)], 2.6),
    "south_arm":  ([(62, 70), (56, 98), (56, 128), (70, 148), (80, 160)], 2.4),
    "gearwork":   ([(168, 80), (150, 92), (132, 98), (128, 136), (104, 150), (80, 160)], 2.4),
    "anchor":     ([(168, 80), (182, 64), (190, 56)], 2.2),
    "seized":     ([(168, 80), (194, 90), (198, 96), (206, 128), (222, 126)], 2.4),
    "slipping":   ([(214, 136), (214, 166), (198, 186), (188, 196)], 2.4),
    "slip_west":  ([(104, 170), (124, 192), (158, 190), (176, 192)], 2.2),
    "observe":    ([(206, 62), (240, 60), (276, 46)], 2.2),
    "listing":    ([(232, 130), (254, 138), (276, 144), (283, 160)], 2.2),
}


class _Spec(E.Spec):
    """Groves only on the rock, never on the cloud or out over the drop."""

    def woods_raw(self, gx, gy):
        out = super().woods_raw(gx, gy)
        return np.minimum(out, -(np.asarray(rock_field(gx, gy)) + 3.0))


SPEC = _Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
             mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
             rim={}, rock_rim={}, gaps=GAPS, fords=FORDS, thicket=(0.99, 10.0, 2.0))

#: everyone on the Anchorfields (tools/build_anchorfields_people.py writes their records)
NPC_POSITIONS = {
    # the end of the aqueduct arm
    "af_armwarden":        (16, 70),    # the warden at the arm's end
    # the Estates: House Vaelith's old estate, half shut up
    "af_steward":          (80, 70),    # the estate's last steward
    "af_house_heir":       (68, 70),    # the young heir who stayed
    # Keelstone: the Anchor-Wardens' hold
    "af_warden_prime":     (166, 78),   # the Warden-Prime
    "af_chainwright":      (172, 82),   # keeps the chains
    "af_keel_engineer":    (162, 84),   # the engineer who reads the anchors
    "af_warden_scout":     (176, 76),   # watches the Ascendancy
    "af_old_warden":       (170, 74),   # the oldest warden, who remembers the last fall
    "af_skiffmaster":      (164, 80),   # the flight path
    "af_provisioner":      (164, 86),   # food
    "af_trader":           (174, 86),   # goods
    # the Observatory: the House of Measures
    "af_measurer":         (280, 40),   # the house's master of measures
    "af_star_reader":      (286, 44),   # reads the drift of the islands against the stars
    "af_obs_archivist":    (278, 46),   # keeps the house's thousand-year records
    # Tiltside: the Earthborn on the Listing Isle
    "af_tilt_lead":        (282, 166),  # the camp's leader
    "af_tilt_surveyor":    (288, 170),  # an Earthborn surveyor measuring the tilt
    "af_tilt_medic":       (278, 172),  # the camp's medic
    "af_tilt_trader":      (284, 174),  # odds and ends
    # out on the shards
    "af_gear_tender":      (90, 156),   # an engine-tender in the Gearwork
    "af_slip_watcher":     (196, 186),  # a warden posted at the Slipping Anchor
    "af_drop_scavenger":   (40, 214),   # a scavenger on the Dropfield
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}

SUBZONES = [   # (table_key, x, y, w, h, display_name) - later registrations win on overlap
    ("The Estates", 26, 24, 92, 84, None),
    ("The First Anchor", 120, 0, 150, 108, None),
    ("The Gearwork", 24, 112, 116, 106, None),
    ("The Seized Anchor", 150, 100, 116, 50, None),
    ("The Slipping Anchor", 140, 150, 116, 80, None),
    ("The Dropfield", 0, 182, 96, 68, None),
    ("The Listing Isle", 262, 120, 38, 86, None),
    ("The Aqueduct Arm", 0, 62, 34, 24, None),
    ("Keelstone", 152, 68, 34, 24, None),
    ("Tiltside", 272, 156, 24, 26, None),
    ("The Observatory", 266, 28, 32, 28, None),
]

#: silver and wind trees, the estate's gold orchard trees on the lawns
TREES = {
    "big":   [(SKP + "sk_silver_tree.png", 8), (SKP + "sk_sky_birch.png", 7)],
    "mid":   [(SKP + "sk_wind_tree.png", 6), (SKP + "sk_fruit_tree.png", 6)],
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
    for (cx, cy, rx, ry) in [(10, 74, 7, 5), (74, 66, 16, 10), (168, 80, 16, 10), (190, 52, 14, 10),
                             (80, 160, 16, 12), (226, 122, 14, 10), (186, 194, 15, 12), (283, 168, 10, 11),
                             (282, 42, 11, 9)]:
        m |= (np.abs(gx - cx) < rx) & (np.abs(gy - cy) < ry)
    return m


def open_the_drop(L):
    z = L.z
    for y, x in zip(*np.nonzero(drop_mask(L))):
        z.set_tile(int(x), int(y), "grass", "base")
        z.set_tile(int(x), int(y), "cliff", "collision")


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "The engine country: a great shelf of stone cracked into shards, held up by anchor towers "
                             "older than anyone's memory, and the third of them failing.",
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
    E.scatter_trees(L, TREES, seed=5301, spacing=9.0, grove_keep=0.5)
    sprinkle(L)
    L.free_mask = L.free_mask | (keep & cloud)
    cloud_dress(L, cloud)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    E.place_links(L, LINKS)
    from tools.link_art import dress_links
    dress_links(L.z, LINKS, pads={"skipstone": "lk_skipstone_overgrown"})
    return L


#: THE FIRST LINK in the sky (world/links.py; Kyle, 21 Nov 2026: "We can have 1 or 2 before the ff zone so people see
#: them a few times. But they are more heavily found later"). An old skip-stone, overgrown and forgotten, still joins
#: the House of Measures' rock to the Listing Isle; the house uses it to send its surveyors to Tiltside.
LINKS = [("skipstone", (282, 48), (280, 146))]


def sprinkle(L):
    """Clover, wind tufts and rubble flowers on the shards; nothing on the roads, the cloud or the bridges."""
    import random
    rnd = random.Random(5303)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    kinds = [("sk_clover_patch", 0.012, 26), ("sk_rubble_flowers", 0.022, 22), ("sk_sky_lilies", 0.026, 12)]
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
    """Wisps drifting over the Dropfield."""
    import random
    rnd = random.Random(5307)
    ys, xs = np.nonzero(L.free_mask & cloud)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = 0
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x] or rnd.random() > 0.01 or n >= 12:
            continue
        if L.prop("sk_cloud_wisp", x, y, 3, path_dir=SKP, solid=False, nudge=0):
            n += 1
            L.free_mask[max(0, y - 4):y + 5, max(0, x - 4):x + 5] = False
    L.cloud_clutter = (n,)


CHEST_SPOTS = [(40, 60), (104, 40), (60, 96), (150, 40), (226, 70), (210, 10), (244, 98), (40, 150), (120, 168),
               (100, 204), (166, 132), (248, 128), (168, 218), (224, 188), (282, 190), (276, 50), (20, 238), (76, 236)]


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
        """The last walkable tile walking from (x, y) toward (dx, dy): where a pool's overflow goes over."""
        while 0 < x + dx < W - 1 and 0 < y + dy < H - 1 and float(sea(x + dx, y + dy)) < -0.5:
            x, y = x + dx, y + dy
        return x, y

    # ---- the wellstones' falls: every pool spills off the nearest edge (docs/worldtree_brief.md)
    for (px, py, dx, dy) in [(54, 62, -1, 0), (78, 176, -1, 0), (282, 176, 1, 0)]:
        S("sk_edge_falls", *rim(px, py, dx, dy), 5, solid=False, allow_overlap=True)
    # ---- the Aqueduct Arm: the old arm's end, where it lands on the Estates
    B("ae_aqueduct", 30, 72, 8, allow_overlap=True, road_ok=True)
    # ---- the Estates: House Vaelith's mansion over the lawn, the conservatory, the gravity fountain, the orchard
    B("ae_terrace_mansion", 80, 56, 12)
    B("ae_conservatory", 50, 76, 8)
    B("ae_gravity_fountain", 92, 72, 5)
    B("ae_gold_orchard", 96, 44, 7)
    B("ae_garden_pavilion", 50, 46, 6)
    # ---- the First Anchor: the anchor tower in its chain-field, the chain hoists, the islets held up on chains
    B("ae_gravity_anchor", 190, 46, 14)
    for (x, y) in [(176, 38), (206, 36), (178, 62), (204, 62)]:
        B("kh_chain_anchor", x, y, 4)
    B("ae_chain_hoist", 214, 50, 6)
    B("ae_anchor_column", 214, 8, 7)
    B("ae_anchor_column", 236, 12, 7)
    # ---- Keelstone: the wardens' hold
    B("ae_wall_tower", 150, 70, 10)
    B("ae_guard_post", 182, 72, 6)
    B("ae_engine_bench", 160, 90, 3)
    B("ae_supply_crates", 178, 90, 3)
    B("ae_skiff_dock", 150, 82, 6)
    B("ae_ceremonial_brazier", 168, 86, 3)
    B("ae_barracks", 186, 78, 8)
    B("ae_field_pavilion", 156, 64, 6)
    B("ae_orb_lantern", 158, 74, 4)
    B("ae_orb_lantern", 178, 70, 4)
    B("ae_banner", 164, 70, 5)
    B("ae_bench", 172, 92, 3)
    # ---- the Gearwork: the engines that feed the anchors, waking wrong
    B("ae_crystal_engine", 62, 152, 9)
    B("ae_cooling_tower", 96, 144, 10)
    B("ae_gear_bank", 62, 166, 5)
    B("ae_engine_pylon", 104, 168, 7)
    B("ae_construct_cradle", 86, 186, 6)
    B("ae_crystal_boiler", 46, 140, 6)
    # ---- the Seized Anchor: the second anchor, the Ascendancy's camp round it
    B("ae_anchor_column", 228, 112, 10)
    B("ae_soldier_tent", 214, 120, 5)
    B("ae_soldier_tent", 240, 128, 5)
    B("ae_storm_artillery", 236, 112, 6)
    B("ae_shield_pylon", 218, 134, 6)
    B("ae_war_standard", 244, 120, 6)
    # ---- the Slipping Anchor: the third anchor, failing, and the door down into its keel
    B("ae_failing_pylon", 182, 184, 12)
    B("ae_dead_engine", 166, 200, 6)
    S("ff_crystal_crater", 204, 196, 5, solid=False)
    L.prop("ent_door_stairs_down", 188, 203, 5, path_dir="assets/tiles/cave_entrances/", solid="core", nudge=0)
    # ---- the Listing Isle and Tiltside: the leaning tower, and the Earthborn camped under it
    B("ae_leaning_tower", 283, 140, 12)
    S("ff_camp_fire", 283, 168, 3, solid=False)
    S("ff_patched_tent", 276, 162, 5)
    S("ff_patched_tent", 290, 164, 5)
    S("ff_salvage", 288, 180, 4)
    # ---- the Observatory: the House of Measures
    B("ae_observatory", 284, 34, 10)
    B("ae_armillary", 274, 44, 4)
    B("ae_star_globe", 292, 46, 3)
    # ---- the Dropfield: what's left of the island that fell, strewn across the cloud
    S("sk_float_rock", 26, 204, 5)
    S("sk_float_rock", 64, 226, 5)
    B("ae_broken_ring", 48, 196, 7, allow_overlap=True)
    B("ae_rubble", 72, 210, 4)
    B("ae_rubble", 20, 230, 4)


def register_baked(zone):
    import os
    zone.sky = {k: v for k, v in SKY.items() if not callable(v)}
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.webp"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_anchorfields():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
