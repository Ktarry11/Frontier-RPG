"""
Hand-built Lenswatch (130x96): the survey's camp off the Sunward Crown's cloud shelf, 48-49 (docs/worldtree_brief.md,
"Twenty questions"). A town, so its own map (Kyle's town rule), with an inn and the Crown's one flight path.

Kyle, 20 Nov 2026, on where players rest at the Crown: "Aetherian survey camp". You sleep in the camp of the people who
are studying you. The House of the Patient Lens (the scholar house that respects the ground) sent the survey down to
the tree; it towed a small island along behind its ship and anchored it off the cloud's edge, and that island is
Lenswatch: white stone and crystal lamps on bare rock, a guesthouse for the ground folk the survey wants to talk to, a
court in the middle with the house's great lens pointed down at the world, and the survey ship moored off the far side.

ORIENTATION FOLLOWS THE OVERWORLD. Lenswatch lies east of the Crown's Survey Dock, so the gangway comes in on its WEST
side and the open sky is all round; the ship rides off its east side, away from the crown.

    the gangway (2,46), west <- the Survey Dock (The Sunward Crown, 295,130)
    the Landing: the west deck where the gangway comes in, the cargo and the survey's guards
    the Guesthouse: the inn, north-west, built for guests from the ground
    the Survey Court: the plaza in the middle, the observatory and the great lens on its north side
    the Skiff Roost: the flight path, an islet up a light bridge to the north-east, skiffs hung off it
    the Lens Hall: the scholars' laboratory and archive, on their own rock down a stair to the south
    the Mooring: the survey ship off the east edge

A SKY MAP (SKY): the baker cuts the drop out (tools/bake_ashenvale.sky_cut) and hangs the island's rock under it; the
renderer paints the cloud sea under that.

HARD CONTRACTS (world/portal_manager.py)
  portal   (2,46) <-> The Sunward Crown (295,130): you arrive at (7,46) coming in and (289,130) going out
           (119,13), the skiff off the Roost <-> The Celestial Expanse's landing on Crashfall (103,206)
  NPC ids  lw_*: written by tools/build_sunward_crown_people.py from NPC_POSITIONS
"""
import numpy as np

from tools import ashenvale_engine as E

BAKED_DIR = "assets/tiles/sky/baked_lenswatch"
NAME = "Lenswatch"
W, H = 130, 96
SKP = "assets/tiles/sky/props/"
BLD = "assets/buildings/"

PORTALS = {(2, 46): "The Sunward Crown", (119, 13): "The Celestial Expanse"}
ARRIVALS = [(7, 46), (114, 14)]
LATER_PORTALS = {}
START = (7, 46)

#: the island: bare rock the survey towed here and anchored, its top paved where the camp stands
ISLAND = [(14, 34), (24, 22), (40, 24), (50, 14), (66, 18), (80, 26), (92, 34), (112, 40), (118, 52), (110, 62),
          (94, 64), (84, 72), (70, 70), (58, 76), (40, 72), (26, 64), (12, 56)]
#: the two islets anchored off it: the Skiff Roost to the north-east, the Lens Hall's rock to the south
ROOST = [(96, 12), (110, 6), (122, 14), (118, 28), (102, 28)]
HALL = [(38, 82), (58, 79), (78, 84), (72, 93), (46, 93)]
#: plank and light across the drop: the gangway in from the west, the ship's gangway out east
BRIDGES = [
    ([(0, 46), (16, 46)], 2.6),             # the gangway from the Crown's dock
    ([(114, 50), (124, 50)], 2.2),          # the ship's gangway
    ([(88, 34), (100, 24)], 2.2),           # the light bridge up to the Skiff Roost
    ([(60, 72), (60, 82)], 2.4),            # the stair down to the Lens Hall
]
#: the ship's deck: a long hull moored off the east edge (walkable: its deck is the "plaza" layer)
SHIP = ([(118, 42), (126, 44), (126, 58), (118, 60)])

SKY = {"far": "sky_far_gold", "parallax": 0.35, "drift": 6.0, "wisps": 0.5, "sun": 0.5, "far_tiles": 10,
       "underside": 5.0}


def _poly(gx, gy, pts):
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


def _wob(gx, gy):
    return (1.3 * np.sin(0.21 * gx + 0.4) * np.sin(0.17 * gy + 1.1) + 0.8 * np.sin(0.37 * gx - 0.29 * gy)
            + 0.4 * np.sin(0.61 * gy + 0.2 * gx))


def bridge_mask(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    out = np.full(np.shape(gx), 99.0)
    for pts, hw in BRIDGES:
        out = np.minimum(out, _seg_dist(gx, gy, pts) - hw)
    return np.minimum(out, _poly(gx, gy, SHIP))


def sea(gx, gy):
    """The drop all round the island. Extent > 0 is a fall into the sky."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    land = np.minimum.reduce([_poly(gx, gy, ISLAND) + _wob(gx, gy), _poly(gx, gy, ROOST) + 0.5 * _wob(gx, gy),
                              _poly(gx, gy, HALL) + 0.5 * _wob(gx, gy), bridge_mask(gx, gy)])
    edge = np.maximum.reduce([-1.0 - gx, gx - (W - 1.0), 2.0 - gy, gy - (H - 3.0)])
    return np.maximum(land, edge * 3.0)


def plaza_field(P, wp):
    """The gangways and the ship's deck (the "plaza" layer)."""
    from tools.bake_ashenvale import smoothstep
    return 1.9 * (1.0 - smoothstep(-0.4, 1.2, bridge_mask(P.gx, P.gy)))


ISLETS = []
#: the court's reflecting pool, and the little garden pool by the guesthouse
LAKES = {"pools": [(44, 58, 5, 3, 0, 0.5), (26, 38, 3, 2, 0, 1.2)]}
DEEP_SHRINK = {"pools": 9.0}
RIVERS = []
FORDS = []
MESAS = []
RIDGES = []
WOODS = []
BELTS = []
CLEARINGS = [(62, 46, 52, 30), (110, 18, 10, 8), (58, 86, 18, 6)]
CORRUPT_PATCHES = []
BURNED_PATCHES = []
BLUEBELL_PATCHES = [(40, 66, 6, 4), (84, 62, 6, 4), (24, 58, 4, 3)]
#: the camp's white stone: the court, the landing, the paths between the buildings
PAVED_PATCHES = [(62, 46, 16, 9), (20, 46, 8, 6), (36, 30, 8, 5), (108, 18, 7, 5), (58, 88, 12, 4),
                 (106, 50, 8, 5)]
LUSH = 0.0
GRADE = None
DROP = None
GAPS = [("ell", 7, 46, 4, 3), ("ell", 60, 48, 10, 6)]

ROADS = {
    "landing":  ([(8, 46), (30, 46), (50, 46)], 2.8),
    "court":    ([(50, 46), (70, 47), (96, 50), (114, 50)], 2.8),
    "guests":   ([(30, 46), (34, 36)], 2.2),
    "roost":    ([(76, 46), (86, 36), (100, 24), (106, 20)], 2.2),
    "hall":     ([(60, 48), (60, 70), (60, 84)], 2.4),
    "lens":     ([(62, 46), (62, 38)], 2.2),
}

SPEC = E.Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
              mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={}, rock_rim={}, gaps=GAPS, fords=FORDS, thicket=(0.99, 10.0, 2.0))

#: Lenswatch's people (tools/build_sunward_crown_people.py writes their records)
NPC_POSITIONS = {
    "lw_gangway_guard":  (14, 43),     # the survey guard at the gangway
    "lw_innkeeper":      (38, 36),     # the Guesthouse's keeper
    "lw_skiffmaster":    (104, 18),    # the flight path: the skiffs to the Great Settlement and on
    "lw_surveyor":       (64, 44),     # the survey's leader, in the court
    "lw_lensmaster":     (54, 40),     # the keeper of the great lens
    "lw_warden":         (48, 52),     # the Aetherian who keeps the survey's guests from Earth
    "lw_provisioner":    (24, 52),     # food and drink at the Landing
    "lw_supplier":       (70, 54),     # the survey's stores: reagents, ammunition, salvage bought
    "lw_smith":          (78, 44),     # a crystalsmith who repairs
    "lw_archivist":      (64, 86),     # the Lens Hall's archivist
    "lw_shipwright":     (108, 54),    # the survey ship's master
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}
SUBZONES = [("Lenswatch", 0, 0, W, H, None)]


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
                             "The survey's camp: an island the House of the Patient Lens towed down to the tree and "
                             "anchored off the cloud, white stone, crystal lamps and a great lens pointed at the ground.",
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
        kw.setdefault("nudge", 2)
        return L.prop(n, x, y, h, path_dir=BLD, **kw)

    def S(n, x, y, h, **kw):
        kw.setdefault("solid", "core")
        kw.setdefault("nudge", 2)
        return L.prop(n, x, y, h, path_dir=SKP, **kw)

    # ---- the Landing: the survey's guard post where the gangway comes in, the cargo stacked off the path
    B("ae_guard_post", 18, 40, 6)
    B("ae_crystal_crates", 20, 52, 3)
    B("ae_supply_crates", 26, 54, 3)
    B("ae_lamp_post", 12, 50, 4)
    # ---- the Guesthouse (the inn), with a garden pool in front of it
    B("ae_guesthouse", 36, 32, 10)
    B("ae_planter", 26, 36, 3)
    B("ae_bench", 30, 42, 2)
    # ---- the Survey Court: the observatory and the great lens on its north side, the pool in the middle, lamps at
    #      the corners
    B("ae_observatory", 60, 32, 12)
    B("ae_great_telescope", 74, 34, 9)
    B("ae_armillary", 48, 40, 4)
    for (x, y) in [(52, 42), (72, 42), (52, 52), (72, 52)]:
        B("ae_orb_lantern", x, y, 4)
    B("ae_banner", 68, 40, 6)
    # ---- the Skiff Roost: the flight path, its own islet up a light bridge, skiffs hung off its edge
    B("ae_skiff_dock", 112, 22, 6)
    B("ae_skiff_small", 120, 20, 5, allow_overlap=True)
    B("ae_lamp_post", 100, 16, 4)
    # ---- the Lens Hall: the laboratory and the archive on their own rock, down the stair south of the court
    B("ae_laboratory", 48, 90, 9)
    B("ae_archive", 70, 90, 9)
    B("ae_lens_bench", 56, 84, 3)
    B("ae_instrument_shelf", 61, 84, 3)
    # ---- the stores and the smith on the court's east side
    B("ae_field_pavilion", 76, 60, 6)
    B("ae_engine_bench", 82, 44, 3)
    B("ae_crystal_heater", 84, 52, 3)
    # ---- the Mooring: the survey ship off the east edge, its anchor and chain on the island
    B("ae_survey_skiff", 122, 58, 10, allow_overlap=True, road_ok=True)
    B("ae_gravity_anchor", 104, 60, 6)
    B("ae_chain_hoist", 106, 40, 5)
    # ---- the island's own: crystal growing out of the rock where nothing's been built
    S("sk_crystal_gold", 28, 60, 4)
    S("sk_crystal_blue", 90, 62, 4)
    S("sk_crystal_spire", 116, 12, 6)


def register_baked(zone):
    import os
    zone.sky = dict(SKY)
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.webp"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_lenswatch():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
