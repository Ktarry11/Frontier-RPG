"""
Hand-built Highrest (96x66): the Windwardens' camp on the last shelf of wood below the cloud, 47-49, as its own small
map. Kyle, 22 Nov 2026: "Actually, no we do need hubs in the boughs". Highrest is lashed out from the trunk ring's south
side over the cloud tops, plank and rope and the last branches, and everybody who's climbed this high and stopped lives
on it. It's the Upper Boughs' hub now: the inn, the mail, the flight path, and most of the tier's quests.

There are no bats this high: the wind would take a bat off the tree (docs/worldtree_brief.md). The flight path is the
wyverns, who ride the wind instead of fighting it, from the tamer's ledge.

It's the tree's own style at its barest (sheets W1 and SK): pale wind-scoured bark, lashed planks, charms hung on the
windward rim, the cloud close underneath, and gold where the light first comes down from above.

ORIENTATION FOLLOWS THE OVERWORLD. On the Upper Boughs Highrest's gate is on the far side of its platform, south of the
ring, so you walk south into it and arrive here on the camp's NORTH edge, on the plank bridge from the ring.

    the way in (48,2), north <- Highrest's platform on the Upper Boughs (90,105)
    the Windgate: the plank bridge in from the ring
    the Warden's Fire: the windwarden and the oldest climber round the fire in the middle
    the Last Market: the provisioner and the trader, the last stalls before the cloud
    the Storm Circle: the storm shaman's charms and the lightning stump, west
    the Cloudside Rest: the inn and the mail, south-west
    the Wyvern Ledge: the tamer, the wyverns' handler (the flight path) and the nests, east
    the Weather Post: the meteorologist's rail, south-east, facing the wind
    the Skywatch: the skywatcher's lookout on the southern tip, over the cloud

HARD CONTRACTS (world/portal_manager.py)
  portal   (48,2) <-> The Upper Boughs (90,105): arrive (48,6) coming in, (90,101) going out
  NPC ids  ub_* and hr_*: written by tools/build_upper_boughs_people.py from NPC_POSITIONS
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_worldtree_lenswatch import _poly, _seg_dist, _wob
from world.chunk_paths import exists as _chunk_exists  # noqa: E402  (.webp, .jpg or .png)

BAKED_DIR = "assets/tiles/worldtree/baked_highrest"
NAME = "Highrest"
W, H = 96, 66
WTP = "assets/tiles/worldtree/props/"
BLD = "assets/buildings/"

PORTALS = {(48, 2): "The Upper Boughs"}
ARRIVALS = [(48, 6)]
LATER_PORTALS = {}
START = (48, 6)

#: the camp's great lashed platform
CAMP = [(20, 12), (76, 12), (86, 22), (84, 44), (64, 52), (32, 52), (12, 44), (8, 26)]
#: the wyverns' ledge, a branch stub out to the east
LEDGE = [(84, 18), (95, 21), (95, 38), (85, 43)]
#: the skywatch on the southern tip
TIP = [(40, 49), (58, 49), (54, 63), (44, 63)]
#: the plank bridge in from the ring
BRIDGES = [([(48, -1), (48, 13)], 3.2)]
#: the cloud tops close below, bright and white, the same as the tier's (the Upper Boughs' DROP)
DROP = {"haze": (236, 240, 246), "fade": 0.22, "sat": 0.95, "shadow": (3.0, 5.0)}


def bridge_mask(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    out = np.full(np.shape(gx), 99.0)
    for pts, hw in BRIDGES:
        out = np.minimum(out, _seg_dist(gx, gy, pts) - hw)
    return out


def sea(gx, gy):
    """The drop: everything that isn't platform, ledge, tip or bridge. Extent > 0 is a fall into the cloud."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    wob = _wob(gx, gy)
    land = np.minimum.reduce([
        _poly(gx, gy, CAMP) + 0.6 * wob,
        _poly(gx, gy, LEDGE) + 0.6 * wob,
        _poly(gx, gy, TIP) + 0.5 * wob,
        bridge_mask(gx, gy),
    ])
    edge = np.maximum.reduce([-1.0 - gx, gx - W, -2.0 - gy, gy - (H - 2.0)])
    return np.maximum(land, edge * 3.0)


def plaza_field(P, wp):
    """The bridge's planks (the "plaza" layer)."""
    from tools.bake_ashenvale import smoothstep
    return 1.9 * (1.0 - smoothstep(-0.4, 1.2, bridge_mask(P.gx, P.gy)))


ISLETS = []
#: rain caught in a fork of the platform's branches
LAKES = {"pools": [(64, 24, 2, 2, 0, 0.8)]}
DEEP_SHRINK = {"pools": 9.0}
RIVERS = []
FORDS = []
MESAS = []
RIDGES = []
WOODS = []
BELTS = []
CLEARINGS = [(48, 30, 18, 14), (89, 30, 4, 8), (48, 56, 5, 5)]
#: the storm-black bark round the lightning stump ("burned"), gold where the light comes down ("bluebell"), the camp's
#: planks ("paved")
CORRUPT_PATCHES = []
BURNED_PATCHES = [(22, 24, 4, 3)]
BLUEBELL_PATCHES = [(50, 58, 4, 3), (90, 34, 3, 3)]
PAVED_PATCHES = [(48, 30, 14, 10), (34, 19, 8, 3), (22, 46, 6, 3)]
LUSH = 0.0
GRADE = None
GAPS = [("ell", 48, 6, 4, 3), ("ell", 48, 30, 8, 6)]

ROADS = {
    "in":    ([(48, 2), (48, 20), (48, 28)], 2.6),
    "round": ([(20, 30), (48, 34), (76, 30), (88, 30)], 2.4),
    "tip":   ([(48, 34), (48, 56)], 2.2),
}

SPEC = E.Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
              mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={}, rock_rim={}, gaps=GAPS, fords=FORDS, thicket=(0.99, 10.0, 2.0))

#: Highrest's people (tools/build_upper_boughs_people.py writes their records)
NPC_POSITIONS = {
    # the Warden's Fire
    "ub_windwarden":     (44, 29),    # Windwarden Kaz
    "ub_old_climber":    (53, 32),    # Old Muzzi
    # the Last Market
    "ub_provisioner":    (30, 20),    # food and drink
    "ub_trader":         (39, 20),    # the camp's trader
    # the Storm Circle
    "ub_storm_shaman":   (19, 30),    # Storm-Shaman Ixi
    # the Cloudside Rest
    "hr_innkeeper":      (25, 45),    # the inn
    # the Wyvern Ledge
    "ub_wyvern_tamer":   (78, 30),    # Gulok, who wants a wyvern of his own
    "hr_wyvern_handler": (89, 33),    # the wyverns (the tier's flight path)
    # the Weather Post
    "ub_transplant":     (68, 43),    # Ingrid, reading the weather
    # the Skywatch
    "ub_skywatcher":     (45, 57),    # Talmae, after the skiff
}
MAILBOX = (30, 45)


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}
SUBZONES = [
    ("Highrest", 0, 0, W, H, None),
    ("The Windgate", 40, 0, 16, 14, None),
    ("The Warden's Fire", 36, 22, 24, 18, None),
    ("The Last Market", 24, 12, 22, 10, None),
    ("The Storm Circle", 6, 16, 22, 22, None),
    ("The Cloudside Rest", 10, 38, 26, 16, None),
    ("The Wyvern Ledge", 72, 14, 24, 32, None),
    ("The Weather Post", 58, 36, 22, 16, None),
    ("The Skywatch", 38, 48, 22, 18, None),
]


def drop_mask(L=None):
    ys, xs = np.mgrid[0:H, 0:W]
    return sea(xs + 0.5, ys + 0.5) > 0


def open_the_drop(L):
    """The drop is collision, not water: nothing to swim, fish or wade."""
    z = L.z
    for y, x in zip(*np.nonzero(drop_mask(L))):
        z.set_tile(int(x), int(y), "grass", "base")
        z.set_tile(int(x), int(y), "cliff", "collision")


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "The Windwardens' camp on the last wood below the cloud: lashed planks, charms on the "
                             "windward rim, the wyverns' ledge, and the cloud tops close enough to touch.",
                             "Eastern Kingdoms - The World Tree", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    open_the_drop(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.seal_unreachable(L, START)
    dress(L)
    E.seal_unreachable(L, START)
    E.register_subzones(L, SUBZONES)
    L.z.is_town = True          # the Upper Boughs' hub: safe, no gathering, the inn and the wyverns
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

    # ---- the Windgate
    T("wt_rope_post", 44, 10, 3)
    T("wt_rope_post", 52, 10, 3)
    # ---- the Warden's Fire
    B("gs_brazier", 48, 31, 3)
    B("gs_loa_totem", 56, 26, 5)
    # ---- the Last Market
    B("gs_stall_red", 34, 16, 4)
    T("wt_sap_barrels", 43, 17, 3)
    # ---- the Storm Circle
    T("wt_lightning_stump", 22, 24, 5)
    T("wt_wind_charms", 14, 30, 4)
    # ---- the Cloudside Rest
    B("gs_inn", 22, 41, 7)
    T("wt_hammock", 34, 48, 3)
    # ---- the Wyvern Ledge
    T("wt_wyvern_nest", 90, 27, 4)
    T("wt_wyvern_nest", 91, 40, 4)
    # ---- the Weather Post
    T("wt_wind_charms", 73, 40, 4)
    T("wt_wind_branch", 62, 46, 4)
    # ---- the Skywatch
    T("wt_high_lookout", 51, 61, 8)
    # ---- the camp's homes: lean-tos and round huts lashed down against the wind, all across the platform
    B("gs_hut_round", 30, 28, 5)
    B("gs_hut_round", 62, 22, 5)
    T("wt_bark_leanto", 70, 20, 4)
    T("wt_treehouse_small", 60, 40, 5)
    T("wt_bark_leanto", 40, 44, 4)
    T("wt_treehouse_small", 14, 39, 5)
    B("gs_house_medium", 77, 41, 5)
    T("wt_sap_barrels", 82, 23, 3)
    T("wt_rope_hooks", 56, 52, 3)
    B("gs_lantern_post", 44, 24, 4)
    B("gs_lantern_post", 52, 24, 4)
    B("gs_lantern_post", 40, 52, 4)
    B("gs_lantern_post", 57, 45, 4)
    T("wt_wind_charms", 24, 16, 4)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and _chunk_exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_highrest():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
