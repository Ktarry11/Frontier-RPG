"""
Hand-built Mossroof (100x72): the trolls' first village on the World Tree, at the foot of the Great Bough, 44-45, as its
own small map. Kyle, 22 Nov 2026, on the towns: "Actually, no we do need hubs in the boughs". The village climbs off the
Trunk Ledge onto its own decks in the crotch where the Great Bough leaves the trunk: moss-roofed treehouses on
platforms, ladders and lanterns, the spring the Greenwater river is born from, and the drop into the jungle canopy on
three sides. It's the Lower Boughs' hub now: the inn, the mail, the bats, and most of the tier's quests.

It's the tree's own style (sheet W1's bark and planks, the Settlement's gs_* buildings), the oldest and plainest of the
tree's villages, so it's small houses and lean-tos, not the city's halls.

ORIENTATION FOLLOWS THE OVERWORLD. On the Lower Boughs the way up is on the trunk's face above the ledge, so you walk
north into it and arrive here on the village's SOUTH edge, at the foot of the ladders.

    the way in (50,69), south <- the Trunk Ledge on the Lower Boughs (80,16)
    the Ladderfoot: the foot of the ladders, where the Great Bough's root comes up into the village
    the Elder's Deck: Elder Tal'vani's deck in the middle, and Vel'jani with the sky-bones beside it
    the Greenwater Spring: the pool at the trunk's foot where the river's born, and its rivercaller
    the Moss Market: the cook and the trader under the moss roofs
    the Ropewalk: the bridgekeeper's coils and posts, west along the trunk
    the Hunters' Rack: the bough-hunter's platform out over the drop, west
    the Hanging Hammocks: the inn and the mail, east along the trunk
    the Bat Roost: the bats, in the trunk's corner, north-east
    the Viewing Ledge: the platform out over the canopy, east, where the transplant sits

HARD CONTRACTS (world/portal_manager.py)
  portal   (50,69) <-> The Lower Boughs (80,16): arrive (50,64) coming in, (80,20) going out
  NPC ids  lb_* and mr_*: written by tools/build_lower_boughs_people.py from NPC_POSITIONS
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_worldtree_lenswatch import _poly, _seg_dist, _wob
from world.chunk_paths import exists as _chunk_exists  # noqa: E402  (.webp, .jpg or .png)

BAKED_DIR = "assets/tiles/worldtree/baked_mossroof"
NAME = "Mossroof"
W, H = 100, 72
WTP = "assets/tiles/worldtree/props/"
BLD = "assets/buildings/"

PORTALS = {(50, 69): "The Lower Boughs"}
ARRIVALS = [(50, 64)]
LATER_PORTALS = {}
START = (50, 64)

#: the trunk: a wall of bark along the north edge
TRUNK_DEPTH = 10
#: the decks along the trunk's foot: (y of the lip) - everything north of it is village, south of it the drop
LEDGE_LIP = 27
#: the platforms out over the drop
ELDERS_DECK = [(38, 26), (62, 26), (64, 36), (58, 46), (42, 46), (36, 36)]
HUNTERS_RACK = [(8, 38), (22, 36), (28, 44), (24, 54), (12, 56), (6, 48)]
VIEWING_LEDGE = [(74, 40), (90, 38), (96, 46), (92, 56), (78, 56), (72, 48)]
#: the Great Bough's root, up from the ladders into the middle of the village
ROOT = ([(50, 70), (50, 58), (50, 44)], 6.0)
#: rope-and-plank walkways across the drop
BRIDGES = [
    ([(30, 42), (38, 40)], 2.2),             # the Elder's Deck to the Hunters' Rack
    ([(62, 42), (72, 45)], 2.2),             # the Elder's Deck to the Viewing Ledge
]
#: the canopy far below in a green-gold haze, the same as the tier's (the Lower Boughs' DROP)
DROP = {"haze": (104, 138, 104), "fade": 0.34, "shadow": (3.0, 5.0)}


def bridge_mask(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    out = np.full(np.shape(gx), 99.0)
    for pts, hw in BRIDGES:
        out = np.minimum(out, _seg_dist(gx, gy, pts) - hw)
    return out


def sea(gx, gy):
    """The drop: everything that isn't deck, platform, root or bridge. Extent > 0 is a fall into the canopy."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    wob = _wob(gx, gy)
    ledge = np.maximum.reduce([gy - LEDGE_LIP + 0.8 * wob, 3.0 - gx, gx - (W - 4.0)])
    land = np.minimum.reduce([
        ledge,
        _poly(gx, gy, ELDERS_DECK) + wob,
        _poly(gx, gy, HUNTERS_RACK) + wob,
        _poly(gx, gy, VIEWING_LEDGE) + wob,
        _seg_dist(gx, gy, ROOT[0]) - ROOT[1] + 0.5 * wob,
        bridge_mask(gx, gy),
    ])
    land = np.minimum(land, gy - (TRUNK_DEPTH + 6.0))        # the decks run right up to the trunk
    edge = np.maximum.reduce([-1.0 - gx, gx - W, gy - (H - 2.0)])
    return np.maximum(land, edge * 3.0)


def plaza_field(P, wp):
    """The bridges' planks (the "plaza" layer, sheet W1's lashed planks)."""
    from tools.bake_ashenvale import smoothstep
    return 1.9 * (1.0 - smoothstep(-0.4, 1.2, bridge_mask(P.gx, P.gy)))


ISLETS = []
#: the Greenwater Spring, where the river's born at the trunk's foot, and a rain pool on the hunters' platform
LAKES = {"pools": [(51, 17, 4, 2, 0, 0.4), (16, 46, 2, 2, 0, 1.1)]}
DEEP_SHRINK = {"pools": 9.0}
RIVERS = []
FORDS = []
MESAS = []
RIDGES = []
WOODS = []
BELTS = []
CLEARINGS = [(50, 20, 40, 7), (50, 36, 11, 8), (16, 46, 8, 7), (84, 47, 9, 7), (50, 58, 5, 9)]
#: sunlit bark round the spring ("corrupt" -> dappled light), the village's lashed decks ("paved")
CORRUPT_PATCHES = [(51, 18, 7, 3)]
BURNED_PATCHES = []
BLUEBELL_PATCHES = [(88, 50, 4, 3)]
PAVED_PATCHES = [(50, 36, 9, 6), (32, 21, 9, 3), (69, 21, 9, 3), (50, 62, 3, 5)]
LUSH = 0.9
GRADE = None
GAPS = [("ell", 50, 64, 4, 3), ("ell", 50, 34, 7, 5)]

ROADS = {
    "in":    ([(50, 69), (50, 52), (50, 40)], 2.6),
    "ledge": ([(8, 22), (30, 23), (50, 24), (70, 23), (92, 22)], 2.6),
    "up":    ([(50, 40), (50, 24)], 2.4),
}

SPEC = E.Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
              mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={}, rock_rim={"north": TRUNK_DEPTH}, gaps=GAPS, fords=FORDS, thicket=(0.99, 10.0, 2.0))

#: Mossroof's people (tools/build_lower_boughs_people.py writes their records)
NPC_POSITIONS = {
    # the Elder's Deck
    "lb_elder":          (50, 31),    # Elder Tal'vani
    "lb_scholar":        (43, 37),    # Vel'jani, buying sky-bones
    # the Greenwater Spring
    "lb_shaman":         (57, 20),    # Rivercaller Jinda, at the spring
    # the Moss Market
    "lb_provisioner":    (28, 24),    # food and drink
    "lb_trader":         (38, 24),    # the village's trader
    # the Ropewalk
    "lb_ropemaster":     (13, 24),    # Bridgekeeper Ozzu
    # the Hunters' Rack
    "lb_hunter":         (19, 42),    # Bough-Hunter Rakaz
    # the Hanging Hammocks
    "mr_innkeeper":      (69, 24),    # the inn
    # the Bat Roost
    "mr_bat_handler":    (87, 24),    # the bats (the tier's flight path)
    # the Viewing Ledge
    "lb_transplant":     (86, 46),    # Aroha Tane, who climbed for the view
}
MAILBOX = (64, 24)


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}
SUBZONES = [
    ("Mossroof", 0, 0, W, H, None),
    ("The Ladderfoot", 40, 50, 20, 22, None),
    ("The Elder's Deck", 34, 27, 32, 23, None),
    ("The Ropewalk", 0, 10, 22, 18, None),
    ("The Moss Market", 22, 10, 22, 18, None),
    ("The Greenwater Spring", 44, 10, 16, 17, None),
    ("The Hanging Hammocks", 60, 10, 19, 18, None),
    ("The Bat Roost", 79, 10, 21, 18, None),
    ("The Hunters' Rack", 0, 32, 32, 28, None),
    ("The Viewing Ledge", 68, 34, 32, 26, None),
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
                             "The trolls' first village on the tree: moss-roofed treehouses on decks at the foot of the "
                             "Great Bough, the spring the river's born from, and the canopy a long way below.",
                             "Eastern Kingdoms - The World Tree", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    open_the_drop(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.seal_unreachable(L, START)
    dress(L)
    E.seal_unreachable(L, START)
    E.register_subzones(L, SUBZONES)
    L.z.is_town = True          # the Lower Boughs' hub: safe, no gathering, the inn and the bats
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

    # ---- the trunk: the loa's face in the bark over the village
    B("wt_loa_face", 50, 9, 9, allow_overlap=True)
    # ---- the Ladderfoot: lanterns either side of the root coming up from the ladders
    B("gs_lantern_post", 45, 60, 4)
    B("gs_lantern_post", 55, 60, 4)
    T("wt_rope_post", 45, 52, 3)
    # ---- the Elder's Deck
    T("wt_treehouse", 40, 32, 7)
    B("gs_loa_totem", 57, 33, 5)
    B("gs_prayer_streamers", 59, 40, 4)
    # ---- the Greenwater Spring
    T("wt_pool_reeds", 46, 18, 3, solid=False)
    B("gs_waterfall_shrine", 56, 15, 5)
    # ---- the Moss Market
    T("wt_cook_shelter", 27, 19, 5)
    B("gs_stall_spice", 38, 19, 4)
    T("wt_sap_barrels", 33, 25, 3)
    # ---- the Ropewalk
    T("wt_treehouse_small", 7, 18, 6)
    T("wt_rope_hooks", 17, 18, 4)
    T("wt_rope_post", 20, 25, 3)
    # ---- the Hunters' Rack
    T("wt_skull_rack", 12, 40, 4)
    T("wt_bark_leanto", 22, 50, 5)
    # ---- the Hanging Hammocks
    B("gs_inn", 69, 19, 7)
    T("wt_hammock", 76, 25, 3)
    # ---- the Bat Roost
    B("gs_bat_roost", 89, 19, 7)
    # ---- the Viewing Ledge
    T("wt_treehouse_small", 78, 50, 5)
    T("wt_wind_charms", 92, 44, 4)
    T("wt_hammock", 92, 52, 3)
    # ---- the village's homes: treehouses and round huts on every deck
    B("gs_hut_round", 24, 15, 5)
    B("gs_hut_round", 43, 16, 5)
    T("wt_treehouse_small", 79, 16, 5)
    T("wt_treehouse", 61, 41, 6)
    T("wt_treehouse_small", 10, 52, 5)
    T("wt_treehouse_small", 84, 54, 5)
    B("gs_lantern_post", 37, 29, 4)
    B("gs_lantern_post", 63, 29, 4)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and _chunk_exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_mossroof():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
