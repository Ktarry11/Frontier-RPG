"""
Hand-built Spearhold (80x64): the Highbough Tribes' war camp at the back of the Sunward Crown, 48-49, as its own small
map. Kyle, 22 Nov 2026, on the Crown's hubs: "Tiny camp, no hearth or flight. But seperate map". The trolls won't sleep
in the survey's town while they're still deciding whether the sky people are an enemy, so they camp on their own bough
with their spears facing the cloud. It's a camp, not a town: no inn, no flight path (those are at Lenswatch).

It's the tree's own style, not Caelora's: bark lean-tos, loa totems, sap barrels, the wyverns' nest and a lookout lashed
to the highest branch, on the gold canopy.

ORIENTATION FOLLOWS THE OVERWORLD. On the Crown the camp's way in is where the road from the Mural Gate ends, so the way
in is on the camp's SOUTH edge.

    the way in (40,61), south <- Spearhold on the Sunward Crown (36,121)
    the War Fire: the war-leader's fire in the middle, and Orgrimmar's envoy beside it
    the Lean-tos: the provisioner and the trader under the bark
    the Witch Doctor's Hut: the witch doctor, reading the seal's light
    the Wyvern Roost: the rider and the wyverns' nest, east
    the Lookout: the scout's branch, north

HARD CONTRACTS (world/portal_manager.py)
  portal   (40,61) <-> The Sunward Crown (36,121): arrive (40,56) coming in, (38,126) going out
  NPC ids  sc_*: written by tools/build_sunward_crown_people.py from NPC_POSITIONS
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_worldtree_lenswatch import _poly, _seg_dist, _wob

BAKED_DIR = "assets/tiles/sky/baked_spearhold"
NAME = "Spearhold"
W, H = 80, 64
SKP = "assets/tiles/sky/props/"
WTP = "assets/tiles/worldtree/props/"
BLD = "assets/buildings/"

PORTALS = {(40, 61): "The Sunward Crown"}
ARRIVALS = [(40, 56)]
LATER_PORTALS = {}
START = (40, 56)

#: the bough the camp sits on, broad and flat, the gold canopy all round it
BOUGH = [(10, 26), (18, 10), (36, 5), (56, 7), (70, 16), (74, 32), (68, 46), (54, 54), (44, 58), (36, 58),
         (24, 54), (12, 44)]
BRIDGES = [
    ([(40, 63), (40, 52)], 2.6),            # the way in, off the road from the Mural Gate
]

SKY = {"far": "sky_far_gold", "parallax": 0.35, "drift": 6.0, "wisps": 0.55, "sun": 0.5, "far_tiles": 10,
       "underside": 5.0}


def bridge_mask(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    out = np.full(np.shape(gx), 99.0)
    for pts, hw in BRIDGES:
        out = np.minimum(out, _seg_dist(gx, gy, pts) - hw)
    return out


def sea(gx, gy):
    """The drop off the bough. Extent > 0 is a fall into the sky."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    land = np.minimum.reduce([_poly(gx, gy, BOUGH) + _wob(gx, gy), bridge_mask(gx, gy)])
    edge = np.maximum.reduce([-1.0 - gx, gx - (W - 1.0), 2.0 - gy, gy - (H - 2.0)])
    return np.maximum(land, edge * 3.0)


def plaza_field(P, wp):
    """The way in (the "plaza" layer, painted as the tree's deck planks)."""
    from tools.bake_ashenvale import smoothstep
    return 1.9 * (1.0 - smoothstep(-0.4, 1.2, bridge_mask(P.gx, P.gy)))


ISLETS = []
#: dew caught in a hollow of the bough
LAKES = {"pools": [(56, 22, 3, 2, 0, 0.3)]}
DEEP_SHRINK = {"pools": 9.0}
RIVERS = []
FORDS = []
MESAS = []
RIDGES = []
WOODS = []
BELTS = []
CLEARINGS = [(40, 32, 30, 22)]
CORRUPT_PATCHES = []
BURNED_PATCHES = [(40, 32, 4, 3)]          # round the war fire
BLUEBELL_PATCHES = [(22, 20, 5, 3)]
PAVED_PATCHES = []
LUSH = 0.0
GRADE = None
DROP = None
GAPS = [("ell", 40, 56, 4, 3), ("ell", 40, 34, 7, 4)]

ROADS = {
    "in":       ([(40, 61), (40, 46), (40, 36)], 2.6),
    "camp":     ([(20, 34), (40, 30), (62, 32)], 2.2),
    "lookout":  ([(40, 30), (40, 14)], 2.0),
}

SPEC = E.Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
              mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={}, rock_rim={}, gaps=GAPS, fords=FORDS, thicket=(0.99, 10.0, 2.0))

#: Spearhold's people (tools/build_sunward_crown_people.py writes their records)
NPC_POSITIONS = {
    # the War Fire
    "sc_warleader":         (36, 38),    # Zan'kaji's war-leader on the crown
    "sc_envoy":             (46, 38),    # Orgrimmar's envoy, trying to keep it from becoming a war
    # the Lean-tos
    "sc_spear_provisioner": (18, 40),    # food and drink
    "sc_spear_trader":      (24, 44),    # the camp's trader
    # the Witch Doctor's Hut
    "sc_witchdoctor":       (22, 24),    # reads the seal's light
    # the Wyvern Roost
    "sc_wyvern_rider":      (62, 38),    # a rider whose wyverns hate the sky beasts
    # the Lookout
    "sc_spear_scout":       (44, 14),    # scout of the Taken Crown
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}
SUBZONES = [
    ("Spearhold", 0, 0, W, H, None),
    ("The War Fire", 28, 28, 26, 18, None),
    ("The Lean-tos", 8, 36, 22, 20, None),
    ("The Witch Doctor's Hut", 10, 12, 22, 20, None),
    ("The Wyvern Roost", 54, 26, 24, 24, None),
    ("The Lookout", 32, 2, 26, 22, None),
]


def drop_mask(L=None):
    ys, xs = np.mgrid[0:H, 0:W]
    return sea(xs + 0.5, ys + 0.5) > 0


def open_the_drop(L):
    z = L.z
    for y, x in zip(*np.nonzero(drop_mask(L))):
        z.set_tile(int(x), int(y), "grass", "base")
        z.set_tile(int(x), int(y), "cliff", "collision")


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "The Highbough war camp at the back of the crown: bark lean-tos round the war-leader's "
                             "fire, loa totems, the wyverns' nest, and every spear facing the cloud.",
                             "Eastern Kingdoms - The World Tree", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    open_the_drop(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.seal_unreachable(L, START)
    dress(L)
    E.seal_unreachable(L, START)
    E.register_subzones(L, SUBZONES)
    L.z.is_town = True          # a camp: safe, no gathering (but no inn and no flight path, Kyle's call)
    return L


def dress(L):
    def B(n, x, y, h, **kw):
        kw.setdefault("solid", "core")
        kw.setdefault("nudge", 2)
        return L.prop(n, x, y, h, path_dir=BLD, **kw)

    def T(n, x, y, h, **kw):
        kw.setdefault("solid", "core")
        kw.setdefault("nudge", 2)
        return L.prop(n, x, y, h, path_dir=WTP, **kw)

    # ---- the War Fire
    B("gs_brazier", 40, 34, 4)
    B("gs_loa_totem", 32, 30, 6)
    B("gs_loa_totem", 50, 30, 6)
    # ---- the Lean-tos
    T("wt_bark_leanto", 14, 36, 5)
    T("wt_bark_leanto", 22, 50, 5)
    T("wt_sap_barrels", 30, 46, 4)
    # ---- the Witch Doctor's Hut
    T("wt_bark_leanto", 18, 20, 5)
    T("wt_wind_charms", 28, 18, 5)
    # ---- the Wyvern Roost
    T("wt_wyvern_nest", 66, 30, 5)
    T("wt_wyvern_nest", 60, 46, 4)
    # ---- the Lookout
    T("wt_high_lookout", 50, 12, 9)


def register_baked(zone):
    import os
    zone.sky = dict(SKY)
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.webp"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_spearhold():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
