"""
Hand-built Heartwatch (92x72): the Highbough shadow hunters' stone hold on the first climbers' terraces, 45-47, as its
own small map. Kyle, 22 Nov 2026: "Actually, no we do need hubs in the boughs". The shadow hunters hold the oldest stone
on the tree because of what's at their back, the split in the trunk that goes down into the heartwood, and the people
who've come up to fight the rot live inside its walls with them. It's the Middle Boughs' hub now: the inn, the mail, the
bats, and most of the tier's quests. The sealed split itself stays out on the terraces, where the braziers guard it.

It's the tree's own style, the Middle Boughs' grey lichen bark and the first climbers' carved stone (sheet W1), colder
and older than Mossroof: stone towers and cairns, braziers, and mist where the canopy used to be.

ORIENTATION FOLLOWS THE OVERWORLD. On the Middle Boughs the trunk is the west wall, and the hold's door is on the
outpost platform off the terraces, so you walk north into it and arrive here on the hold's SOUTH edge. The trunk is this
map's west wall too.

    the way in (46,69), south <- the outpost platform on the Middle Boughs (44,42)
    the Watch Gate: the way in, under the gate tower
    the Shadow Court: the shadow hunter and the huntmaster in the middle of the hold
    the Loa Steps: the loa-speaker's shrine against the trunk, north-west
    the Climbers' Stair: the stonekeeper's terrace, the first climbers' carved steps up the trunk
    the Rot Ward: the bark-doctor and the pathologist, south-west, as far from the court as they can keep the rot
    the Bronze Shed: the scholar and the pieces she's dragged in off the Lichen Reach, north-east
    the Outpost Market: the provisioner and the trader
    the Lichen Hearth: the inn and the mail
    the Bat Perch: the bats, on a stone spur out over the mist, east

HARD CONTRACTS (world/portal_manager.py)
  portal   (46,69) <-> The Middle Boughs (44,42): arrive (46,64) coming in, (44,46) going out
  NPC ids  mb_* and hw_*: written by tools/build_middle_boughs_people.py from NPC_POSITIONS
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_worldtree_lenswatch import _poly, _seg_dist, _wob
from world.chunk_paths import exists as _chunk_exists  # noqa: E402  (.webp, .jpg or .png)

BAKED_DIR = "assets/tiles/worldtree/baked_heartwatch"
NAME = "Heartwatch"
W, H = 92, 72
WTP = "assets/tiles/worldtree/props/"
BLD = "assets/buildings/"

PORTALS = {(46, 69): "The Middle Boughs"}
ARRIVALS = [(46, 64)]
LATER_PORTALS = {}
START = (46, 64)

#: the trunk: a wall of bark along the west edge
TRUNK_DEPTH = 10
#: the first climbers' terraces along the trunk's foot run out this far
TERRACE_OUT = 30.0
#: the hold's stone platform, built out from the terraces over the mist
HOLD = [(28, 8), (64, 6), (70, 20), (68, 46), (58, 55), (34, 55), (28, 46)]
#: the bats' spur
PERCH = [(76, 20), (88, 19), (90, 33), (81, 40), (74, 32)]
#: the way in, up from the outpost platform below
WAY_IN = ([(46, 71), (46, 54)], 5.0)
BRIDGES = [([(68, 30), (76, 30)], 2.2)]
#: mist below, cool and grey, the same as the tier's (the Middle Boughs' DROP)
DROP = {"haze": (164, 174, 178), "fade": 0.42, "sat": 0.8, "shadow": (3.0, 5.0)}


def bridge_mask(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    out = np.full(np.shape(gx), 99.0)
    for pts, hw in BRIDGES:
        out = np.minimum(out, _seg_dist(gx, gy, pts) - hw)
    return out


def sea(gx, gy):
    """The drop: everything that isn't terrace, hold, spur or bridge. Extent > 0 is a fall into the mist."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    wob = _wob(gx, gy)
    terraces = np.maximum.reduce([gx - TERRACE_OUT + 0.6 * wob, 3.0 - gy, gy - (H - 5.0)])
    land = np.minimum.reduce([
        terraces,
        _poly(gx, gy, HOLD) + 0.6 * wob,
        _poly(gx, gy, PERCH) + wob,
        _seg_dist(gx, gy, WAY_IN[0]) - WAY_IN[1] + 0.4 * wob,
        bridge_mask(gx, gy),
    ])
    edge = np.maximum.reduce([gx - W, -1.0 - gy, gy - (H - 2.0)])
    return np.maximum(land, edge * 3.0)


def plaza_field(P, wp):
    """The bridge's lashed planks (the "plaza" layer)."""
    from tools.bake_ashenvale import smoothstep
    return 1.7 * (1.0 - smoothstep(-0.4, 1.2, bridge_mask(P.gx, P.gy)))


ISLETS = []
#: rain held in a basin the first climbers cut in the court's stone
LAKES = {"pools": [(38, 30, 2, 2, 0, 0.5)]}
DEEP_SHRINK = {"pools": 9.0}
RIVERS = []
FORDS = []
MESAS = []
RIDGES = []
WOODS = []
BELTS = []
CLEARINGS = [(46, 30, 16, 14), (20, 34, 8, 26), (82, 29, 6, 7), (46, 62, 4, 8)]
#: the rot the bark-doctor keeps out of the hold ("corrupt"), her burned cuttings ("burned"), the climbers' stone ("paved")
CORRUPT_PATCHES = [(18, 58, 4, 3)]
BURNED_PATCHES = [(14, 52, 3, 2)]
BLUEBELL_PATCHES = []
PAVED_PATCHES = [(46, 30, 18, 20), (20, 30, 8, 24), (46, 60, 4, 8), (82, 29, 5, 6)]
LUSH = 0.35
GRADE = None
GAPS = [("ell", 46, 64, 4, 3), ("ell", 46, 30, 8, 6)]

ROADS = {
    "in":       ([(46, 69), (46, 50), (46, 36)], 2.6),
    "terraces": ([(20, 8), (20, 36), (20, 62)], 2.4),
    "cross":    ([(20, 30), (46, 32), (68, 30)], 2.4),
}

SPEC = E.Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
              mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={}, rock_rim={"west": TRUNK_DEPTH}, gaps=GAPS, fords=FORDS, thicket=(0.99, 10.0, 2.0))

#: Heartwatch's people (tools/build_middle_boughs_people.py writes their records)
NPC_POSITIONS = {
    # the Shadow Court
    "mb_shadowhunter":   (44, 26),    # Shadow Hunter Vokra
    "mb_huntmaster":     (52, 34),    # Huntmaster Raz'gul
    # the Loa Steps
    "mb_loa_speaker":    (24, 13),    # Loa-Speaker Ganjo
    # the Climbers' Stair
    "mb_stonekeeper":    (24, 30),    # Stonekeeper Jo'than
    # the Rot Ward
    "mb_bark_doctor":    (23, 48),    # Bark-Doctor Ezzi
    "mb_transplant":     (25, 58),    # Dr. Priya Raman
    # the Bronze Shed
    "mb_scholar":        (57, 15),    # Scholar Nyara
    # the Outpost Market
    "mb_provisioner":    (35, 46),    # food and drink
    "mb_trader":         (42, 48),    # the hold's trader
    # the Lichen Hearth
    "hw_innkeeper":      (59, 47),    # the inn
    # the Bat Perch
    "hw_bat_handler":    (81, 32),    # the bats (the tier's flight path)
}
MAILBOX = (53, 49)


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}
SUBZONES = [
    ("Heartwatch", 0, 0, W, H, None),
    ("The Watch Gate", 36, 55, 20, 17, None),
    ("The Shadow Court", 32, 20, 26, 20, None),
    ("The Loa Steps", 10, 2, 22, 20, None),
    ("The Climbers' Stair", 10, 22, 20, 18, None),
    ("The Rot Ward", 10, 40, 20, 28, None),
    ("The Bronze Shed", 46, 4, 24, 16, None),
    ("The Outpost Market", 30, 40, 18, 15, None),
    ("The Lichen Hearth", 48, 38, 22, 17, None),
    ("The Bat Perch", 70, 14, 22, 30, None),
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
                             "The shadow hunters' hold on the first climbers' stone: carved towers against the trunk, "
                             "braziers against the cold, and nothing below the walls but mist.",
                             "Eastern Kingdoms - The World Tree", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    open_the_drop(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.seal_unreachable(L, START)
    dress(L)
    E.seal_unreachable(L, START)
    E.register_subzones(L, SUBZONES)
    L.z.is_town = True          # the Middle Boughs' hub: safe, no gathering, the inn and the bats
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

    # ---- the Watch Gate
    T("wt_stone_tower_squat", 37, 53, 6)
    B("gs_brazier", 52, 60, 3)
    # ---- the Shadow Court
    B("gs_brazier", 40, 22, 3)
    B("gs_brazier", 50, 22, 3)
    B("gs_loa_totem", 56, 28, 5)
    T("wt_war_totem", 36, 36, 4)
    # ---- the Loa Steps
    T("wt_old_shrine", 18, 12, 6)
    B("gs_prayer_streamers", 28, 8, 4)
    # ---- the Climbers' Stair
    T("wt_stone_tower", 16, 30, 9)
    T("wt_stone_cairn", 26, 36, 3)
    # ---- the Rot Ward
    B("gs_herbalist", 17, 46, 6)
    T("wt_rot_sac", 16, 60, 3)
    # ---- the Bronze Shed
    T("wt_bronze_wing", 64, 12, 4)
    T("wt_bronze_scrap", 52, 12, 3)
    # ---- the Outpost Market
    B("gs_stall_teal", 36, 42, 4)
    T("wt_sap_barrels", 43, 43, 3)
    # ---- the Lichen Hearth
    B("gs_inn", 60, 43, 7)
    B("gs_lantern_post", 66, 49, 4)
    # ---- the Bat Perch
    B("gs_bat_roost", 83, 28, 7)
    B("gs_brazier", 87, 37, 3)
    # ---- the hold's houses: the first climbers' stone towers and the round huts built against them
    T("wt_stone_tower_squat", 64, 24, 6)
    T("wt_stone_tower", 34, 24, 7)
    B("gs_hut_round", 14, 38, 5)
    B("gs_hut_round", 38, 16, 5)
    T("wt_stone_cairn", 30, 52, 3)
    T("wt_bronze_scrap", 66, 16, 3)
    B("gs_lantern_post", 40, 40, 4)
    B("gs_lantern_post", 52, 40, 4)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and _chunk_exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_heartwatch():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
