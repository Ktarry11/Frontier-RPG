"""
Hand-built Cloudbreak (64x124), level 48: the top of the World Tree, where the last branches climb into the cloud
(docs/worldtree_brief.md, "The ascent"; the cutscene is docs/crown_cutscene.md).

"The one map in the game built only to be walked through, and that's the point: the moment the ground ends." One way
up from the Cloud Way on the Upper Boughs: the last branches, too thin for anything to live on, rising nearly straight through cloud
so thick you can't see the drop, with two gaps where somebody hung a rope ladder before you. No monsters and no quests.
The trolls who climbed this far left their marks, and the places are named for them. At the top the branches meet in a
platform of living wood, closed on its far side by an old stone wall much older than the tree, and on the wall is a
mural of three peoples under a golden sun. Walk up to it, and the game's first cutscene plays (world/cutscenes.py).

    The Cloud Way's top .. the bottom of the map (32,120): back down to the Upper Boughs
    The Mural ............ the stone wall at the top (32,9); the cutscene's trigger is the ground in front of it
    the way through ...... in front of the broken mural (32,13): the Sunward Crown. The cutscene takes you through
                           the first time (the portal stands in the cutscene's trigger, so both land you at the gate)

THE CLOUD. The drop is the module's sea field, painted as cloud, and the ground is painted foggy at the bottom and
gold-lit at the top, so the climb goes from white to light.

HARD CONTRACTS (world/portal_manager.py)
  portals  The Upper Boughs (32,120) <-> the Cloud Way (90,52)
           The Sunward Crown (32,13) <-> the Mural Gate (100,164), through the broken mural
"""
import numpy as np

from tools import ashenvale_engine as E

BAKED_DIR = "assets/tiles/worldtree/baked_cloudbreak"
NAME = "The Cloudbreak"
W, H = 64, 124
WTP = "assets/tiles/worldtree/props/"
BLD = "assets/buildings/"

PORTALS = {(32, 120): "The Upper Boughs", (32, 13): "The Sunward Crown"}
ARRIVALS = [(32, 116), (32, 16)]
LATER_PORTALS = {}
START = (32, 116)

#: the stone wall the mural is painted on, along the top
WALL_DEPTH = 7
#: the chamber at the top: a platform where the last branches meet
CHAMBER = (32, 17, 15, 8)
#: the cutscene's trigger: the ground right in front of the mural (world/cutscenes.TRIGGERS)
TRIGGER = [(x, y) for x in range(27, 38) for y in (12, 13)]

#: the last branches, rising nearly straight through the cloud (Kyle, 20 Nov 2026: "less zig zag"). (points, half-width)
BRANCHES = [
    ([(32, 120), (32, 104), (35, 92)], 4.4),
    ([(31, 80), (29, 68), (31, 56)], 4.2),
    ([(32, 44), (32, 34), (32, 26)], 4.2),
]
#: the rope ladders somebody hung across the gaps between them
LADDERS = [
    ([(35, 92), (33, 86), (31, 80)], 2.2),
    ([(31, 56), (32, 50), (32, 44)], 2.2),
]


def _seg_dist(gx, gy, pts):
    out = np.full(np.shape(gx), 1e9)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        vx, vy = x1 - x0, y1 - y0
        t = np.clip(((gx - x0) * vx + (gy - y0) * vy) / float(vx * vx + vy * vy), 0, 1)
        out = np.minimum(out, np.hypot(gx - (x0 + t * vx), gy - (y0 + t * vy)))
    return out


def sea(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    wob = 0.8 * np.sin(0.31 * gy + 0.4) + 0.6 * np.sin(0.23 * gx + 1.2)
    land = np.full(np.shape(gx), 99.0)
    for pts, hw in BRANCHES:
        land = np.minimum(land, _seg_dist(gx, gy, pts) - hw + wob)
    for pts, hw in LADDERS:
        land = np.minimum(land, _seg_dist(gx, gy, pts) - hw + 0.1 * wob)
    cx, cy, rx, ry = CHAMBER
    land = np.minimum(land, (np.hypot((gx - cx) / rx, (gy - cy) / ry) - 1.0) * min(rx, ry) + 0.4 * wob)
    # the platform runs right up to the wall, as wide as the chamber (a smooth box, so the cloud shades evenly round it)
    land = np.minimum(land, np.maximum(np.abs(gx - cx) - (rx + 1.0), gy - (WALL_DEPTH + 5.0)) + 0.3 * wob)
    edge = np.maximum.reduce([2.0 - gx, gx - (W - 3.0), gy - (H - 2.0)])
    return np.maximum(land, edge * 3.0)


def ladder_mask(gx, gy):
    out = np.full(np.shape(gx), 99.0)
    for pts, hw in LADDERS:
        out = np.minimum(out, _seg_dist(np.asarray(gx, float), np.asarray(gy, float), pts) - hw)
    return out


def plaza_field(P, wp):
    """The rope ladders' rungs (the "plaza" layer)."""
    from tools.bake_ashenvale import smoothstep
    return 1.7 * (1.0 - smoothstep(-0.4, 1.0, ladder_mask(P.gx, P.gy)))


ISLETS = []
LAKES = {}
DEEP_SHRINK = {}
RIVERS = []
FORDS = []
#: the old stone wall the mural is painted on, standing only behind the chamber
MESAS = [(32, 3, 17, 7, 0)]
RIDGES = []
WOODS = []
BELTS = []
CLEARINGS = [(32, 17, 14, 7), (32, 116, 5, 4)]
#: the climb from white to light: fog-hung bark below ("corrupt"), gold-lit bark at the top ("bluebell"), and the
#: chamber's floor of living heartwood ("paved")
CORRUPT_PATCHES = [(32, 106, 16, 22), (30, 80, 14, 16)]
BURNED_PATCHES = []
BLUEBELL_PATCHES = [(32, 36, 10, 12), (32, 24, 16, 6)]
PAVED_PATCHES = [(32, 16, 15, 8)]
LUSH = 0.0
GRADE = None
DROP = {"haze": (244, 244, 248), "fade": 0.18, "sat": 0.9, "shadow": (2.0, 3.5)}


def LIGHT(rgb, tx, ty):
    """From white to light (the brief): thick fog over everything at the foot of the climb, thinning as you go up, and
    the gold of the sun above the cloud coming through at the top. Applied last by the baker (tools/bake_ashenvale)."""
    t = np.clip((ty - 20.0) / 96.0, 0.0, 1.0)[..., None]          # 0 at the chamber, 1 at the foot
    fog = np.array([236, 239, 244], np.float32)
    gold = np.array([255, 214, 130], np.float32)
    rgb = rgb * (1 - 0.42 * t) + fog * (0.42 * t)
    warm = np.clip((44.0 - ty) / 34.0, 0.0, 1.0)[..., None]       # the last stretch and the chamber
    rgb = rgb * (1 - 0.16 * warm) + gold * (0.16 * warm)
    return rgb * (1 + 0.10 * warm)
GAPS = [("ell", 32, 116, 4, 3), ("ell", 32, 15, 10, 5)]
#: the way up: worn into the bark by everyone who climbed before you, stopping at each ladder
ROADS = {
    "low":  ([(32, 118), (32, 104), (34, 93)], 1.8),
    "mid":  ([(31, 79), (29, 68), (31, 57)], 1.8),
    "high": ([(32, 43), (32, 34), (32, 24)], 1.8),
}


class _Spec(E.Spec):
    def woods_raw(self, gx, gy):
        out = super().woods_raw(gx, gy)
        return np.minimum(out, -(np.asarray(sea(gx, gy)) + 3.0))


SPEC = _Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
             mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
             rim={}, rock_rim={}, gaps=GAPS, fords=FORDS, thicket=(0.99, 10.0, 2.0))

NPC_POSITIONS = {}

#: the voices of the trolls who climbed before you: each place is named for what they left there
SUBZONES = [
    ("The Last Branches", 0, 0, W, H, None),
    ("Where Ruk'tan Turned Back", 16, 92, 34, 30, None),
    ("Zel'ji's Rope", 14, 76, 34, 18, None),
    ("The Charm-Tree", 14, 52, 34, 26, None),
    ("Old Vosh's Ladder", 18, 38, 30, 16, None),
    ("The Mural", 12, 0, 40, 28, None),
]


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}


def drop_mask(L):
    ys, xs = np.mgrid[0:H, 0:W]
    return sea(xs + 0.5, ys + 0.5) > 0


def open_the_drop(L):
    z = L.z
    for y, x in zip(*np.nonzero(drop_mask(L))):
        z.set_tile(int(x), int(y), "grass", "base")
        z.set_tile(int(x), int(y), "cliff", "collision")


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "The last branches of the World Tree, climbing into the cloud, and an old stone wall at "
                             "the top with three peoples painted on it.",
                             "Eastern Kingdoms - The World Tree", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    open_the_drop(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.seal_unreachable(L, START)
    dress(L)
    E.seal_unreachable(L, START)
    E.register_subzones(L, SUBZONES)
    return L


def dress(L):
    def B(n, x, y, h, **kw):
        kw.setdefault("solid", "core")
        kw.setdefault("nudge", 1)
        return L.prop(n, x, y, h, path_dir=BLD, **kw)

    def G(n, x, y, h, **kw):
        # nothing on these thin branches is solid: a charm or a cairn nudged into a neck would close the climb
        kw.setdefault("solid", False)
        kw.setdefault("nudge", 2)
        return L.prop(n, x, y, h, path_dir=WTP, **kw)

    # ---- the mural on the old stone wall: whole until you've seen it break, then broken open (world/cutscenes.py)
    n0 = len(L.z.landmarks)
    if B("cb_mural_intact", 32, 10, 11, allow_overlap=True, road_ok=True):
        L.z.landmarks[-1]["cutscene_hide"] = "crown"
    if B("cb_mural_broken", 32, 10, 11, allow_overlap=True, road_ok=True):
        L.z.landmarks[-1]["cutscene_show"] = "crown"
    assert len(L.z.landmarks) == n0 + 2, "the mural must stand in both its states"
    # ---- what the climbers left on the way up
    G("wt_stone_cairn", 28, 104, 4)              # where Ruk'tan turned back
    G("wt_wind_charms", 36, 100, 5)
    G("wt_rope_post", 38, 92, 4)                 # Zel'ji's rope
    G("wt_rope_post", 28, 80, 4)
    G("wt_wind_branch", 25, 68, 5)               # the charm-tree: one bent branch, and the charms tied to it
    G("wt_wind_charms", 25, 65, 5)
    G("wt_wind_charms", 26, 71, 5)
    G("wt_rope_post", 34, 56, 4)                 # old Vosh's ladder
    G("wt_rope_post", 35, 44, 4)
    G("wt_gold_branch_tip", 36, 32, 5)           # the first gold, near the top
    G("wt_gold_branch_tip", 28, 26, 5)
    G("wt_stone_cairn", 42, 19, 4)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_cloudbreak():
    L = build_layout()
    register_baked(L.zone)
    from world.cutscenes import register_trigger
    register_trigger(NAME, "crown", TRIGGER)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS) + list(LATER_PORTALS), npc=[])
