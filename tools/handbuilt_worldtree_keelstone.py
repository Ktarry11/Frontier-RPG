"""
Hand-built Keelstone (120x100): the Anchorfields' town, 51-54 (Kyle's town rule: one town per open map, on its own map,
as the hub). Kyle, 22 Nov 2026: "Lets build the towns, move the NPCs", and "Caelora cities will have a style to them as
theyre all the same race".

Keelstone is the Anchor-Wardens' hold at the foot of the First Anchor, the oldest anchor on the shelf. The wardens have
kept it for a thousand years, and it's built the Aetherian way (white marble trimmed with gold, crystal lamps, blue
cloth) like Lenswatch, Aurelion and Halcyon Rest. Its own touch is the chains: the anchor tower's foot stands at the
north end, its great bronze chains running down into the yard and off the edge, and everything in the town is built
round keeping them. The House of Measures keeps a reading room here to be near the wardens' gauges, and Tiltside's
Earthborn moved in below the market when the Listing Isle got too steep to sleep on.

ORIENTATION FOLLOWS THE OVERWORLD. On the Anchorfields the town's gate stands on the south side of the Keelstone plaza,
where the roads meet, and the First Anchor rises to the north, so the gate comes in on the town's SOUTH edge and the
anchor's foot is at the top.

    the gate (60,97), south <- Keelstone's gate on the Anchorfields (168,88)
    the Gate Stair: where you come in, up the gangway from the plaza
    the Anchor Market: the inn, the mail, the provisioner and the trader
    the Wardens' Hall: the Warden-Prime and the hold's oldest wardens
    the Chain Yard: the First Anchor's foot and its chains, the chainwright and the engineer
    the Measures' Annex: the House of Measures' reading room, east
    the Skiff Roost: the flight path, an islet up a light bridge to the west
    the Tilt Quarter: Tiltside's Earthborn, south-west of the market

A SKY MAP (SKY): the baker cuts the drop out (tools/bake_ashenvale.sky_cut) and hangs the island's rock under it.

HARD CONTRACTS (world/portal_manager.py)
  portal   (60,97) <-> The Anchorfields (168,88): arrive (60,92) coming in, (168,84) going out
  NPC ids  af_* and kl_*: written by tools/build_anchorfields_people.py from NPC_POSITIONS
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_worldtree_lenswatch import _poly, _seg_dist, _wob

BAKED_DIR = "assets/tiles/sky/baked_keelstone"
NAME = "Keelstone"
W, H = 120, 100
SKP = "assets/tiles/sky/props/"
BLD = "assets/buildings/"

PORTALS = {(60, 97): "The Anchorfields"}
ARRIVALS = [(60, 92)]
LATER_PORTALS = {}
START = (60, 92)

#: the hold's shelf of stone at the anchor's foot
ISLAND = [(22, 40), (30, 18), (50, 10), (74, 10), (94, 18), (106, 34), (110, 54), (104, 72), (90, 86), (70, 90),
          (50, 90), (30, 92), (14, 82), (14, 60)]
#: the skiff roost's islet, west, across a light bridge
ROOST = [(2, 36), (10, 34), (12, 46), (9, 56), (2, 56)]
#: plank and light across the drop
BRIDGES = [
    ([(60, 99), (60, 86)], 2.6),            # the gangway up from the plaza
    ([(8, 46), (20, 46)], 2.4),             # the light bridge to the roost
]

SKY = {"far": "sky_far_dawn", "parallax": 0.35, "drift": 4.0, "wisps": 0.5, "sun": 0.45, "far_tiles": 10,
       "underside": 5.0}


def bridge_mask(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    out = np.full(np.shape(gx), 99.0)
    for pts, hw in BRIDGES:
        out = np.minimum(out, _seg_dist(gx, gy, pts) - hw)
    return out


def sea(gx, gy):
    """The drop all round the shelf. Extent > 0 is a fall into the sky."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    land = np.minimum.reduce([_poly(gx, gy, ISLAND) + _wob(gx, gy), _poly(gx, gy, ROOST) + 0.5 * _wob(gx, gy),
                              bridge_mask(gx, gy)])
    edge = np.maximum.reduce([-1.0 - gx, gx - (W - 1.0), 2.0 - gy, gy - (H - 2.0)])
    return np.maximum(land, edge * 3.0)


def plaza_field(P, wp):
    """The gangway and the light bridge (the "plaza" layer)."""
    from tools.bake_ashenvale import smoothstep
    return 1.9 * (1.0 - smoothstep(-0.4, 1.2, bridge_mask(P.gx, P.gy)))


ISLETS = []
#: the cistern under the anchor's foot, and the wardens' well in the market
LAKES = {"pools": [(84, 28, 4, 2, 0, 0.3), (60, 74, 2, 2, 0, 0.0)]}
DEEP_SHRINK = {"pools": 9.0}
RIVERS = []
FORDS = []
MESAS = []
RIDGES = []
WOODS = []
BELTS = []
CLEARINGS = [(60, 50, 44, 36), (8, 46, 8, 10)]
CORRUPT_PATCHES = []
BURNED_PATCHES = []
BLUEBELL_PATCHES = [(96, 66, 4, 3), (24, 56, 4, 3)]
#: the hold is paved nearly end to end: the market, the hall's court, the yard, the annex steps
PAVED_PATCHES = [(60, 68, 30, 9), (60, 52, 22, 6), (60, 30, 24, 8), (94, 54, 8, 6), (6, 46, 5, 6),
                 (60, 86, 8, 5)]
LUSH = 0.0
GRADE = None
DROP = None
GAPS = [("ell", 60, 92, 4, 3), ("ell", 60, 66, 10, 5)]

ROADS = {
    "gate":     ([(60, 97), (60, 78), (60, 62)], 2.8),
    "market":   ([(28, 68), (60, 64), (94, 66)], 2.6),
    "hall":     ([(60, 62), (60, 54)], 2.4),
    "court":    ([(36, 54), (60, 56), (84, 54)], 2.4),
    "yard_w":   ([(40, 54), (44, 34)], 2.2),
    "yard_e":   ([(80, 54), (76, 34)], 2.2),
    "annex":    ([(84, 54), (94, 58)], 2.2),
    "roost":    ([(36, 54), (24, 48), (8, 46)], 2.4),
    "tilt":     ([(28, 68), (24, 78)], 2.2),
}

SPEC = E.Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
              mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={}, rock_rim={}, gaps=GAPS, fords=FORDS, thicket=(0.99, 10.0, 2.0))

#: Keelstone's people (tools/build_anchorfields_people.py writes their records)
NPC_POSITIONS = {
    # the Gate Stair
    "kl_gatewarden":       (54, 86),    # the wardens' gate-keeper
    # the Anchor Market
    "kl_innkeeper":        (36, 71),    # the Warden's Rest (the inn)
    "af_provisioner":      (50, 70),    # food
    "af_trader":           (74, 70),    # goods
    # the Wardens' Hall
    "af_warden_prime":     (60, 50),    # the Warden-Prime, at the hall's door
    "af_old_warden":       (65, 58),    # the oldest warden, on the bench in the court
    "af_warden_scout":     (50, 58),    # watches the Ascendancy
    # the Chain Yard
    "af_chainwright":      (72, 32),    # keeps the chains
    "af_keel_engineer":    (48, 32),    # reads the anchors' gauges
    # the Measures' Annex
    "af_star_reader":      (92, 60),    # the House of Measures' star-reader
    "af_obs_archivist":    (100, 60),   # the house's archivist, with the copies of its records
    # the Skiff Roost
    "af_skiffmaster":      (6, 42),     # the flight path
    # the Tilt Quarter: Tiltside's Earthborn
    "af_tilt_lead":        (22, 76),    # Margit Halvorsen
    "af_tilt_surveyor":    (32, 82),    # Bartosz Wierzbicki, his instruments on a crate
    "af_tilt_medic":       (18, 84),    # Dr. Ngozi Eze
    "af_tilt_trader":      (28, 74),    # Daisuke Moriyama
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}
#: the districts (later registrations win on overlap). The townsfolk live in these (tools/townsfolk/keelstone.py).
SUBZONES = [
    ("Keelstone", 0, 0, W, H, None),
    ("The Chain Yard", 28, 8, 70, 30, None),
    ("The Wardens' Hall", 30, 38, 54, 24, None),
    ("The Measures' Annex", 84, 34, 30, 40, None),
    ("The Anchor Market", 30, 62, 64, 18, None),
    ("The Tilt Quarter", 10, 64, 26, 30, None),
    ("The Gate Stair", 40, 80, 40, 20, None),
    ("The Skiff Roost", 0, 32, 18, 26, None),
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
                             "The Anchor-Wardens' hold at the foot of the First Anchor: the anchor's chains in the "
                             "yard, the wardens' hall, the House of Measures' reading room, and Tiltside's Earthborn "
                             "below the market.",
                             "Eastern Kingdoms - The World Tree", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    open_the_drop(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    E.seal_unreachable(L, START)
    dress(L)
    E.seal_unreachable(L, START)
    E.register_subzones(L, SUBZONES)
    L.z.is_town = True          # a town: safe, no gathering
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

    # ---- the Chain Yard: the First Anchor's foot, its chains coming down into the yard and off the north edge
    B("ae_anchor_column", 60, 26, 12)
    B("ae_chain_hoist", 40, 24, 6)
    B("ae_chain_hoist", 84, 22, 6)
    B("kh_chain_anchor", 50, 20, 4)
    B("kh_chain_anchor", 72, 18, 4)
    S("sk_sky_chain", 32, 28, 6)
    S("sk_sky_chain", 96, 30, 6)
    B("ae_gauge_panel", 66, 34, 3)
    B("ae_engine_bench", 54, 34, 3)
    # ---- the Wardens' Hall, its court and banners
    B("ae_barracks", 60, 46, 9)
    B("ae_banner", 46, 46, 5)
    B("ae_banner", 74, 46, 5)
    B("ae_bench", 76, 60, 2)
    B("ae_orb_lantern", 40, 58, 4)
    B("ae_orb_lantern", 80, 58, 4)
    # ---- the Anchor Market: the Warden's Rest (the inn), the stalls, the well
    B("ae_guesthouse", 34, 66, 9)
    B("ae_kiosk_crystal", 46, 76, 4)
    B("ae_kiosk_cloth", 74, 76, 4)
    B("ae_supply_crates", 84, 72, 3)
    B("ae_lamp_post", 54, 62, 4)
    B("ae_lamp_post", 68, 62, 4)
    # ---- the Measures' Annex: the house's reading room, an armillary and its globe
    B("ae_archive", 96, 50, 8)
    B("ae_armillary", 104, 62, 4)
    B("ae_star_globe", 88, 64, 3)
    # ---- the Skiff Roost: the skiff dock on its islet
    B("ae_skiff_dock", 6, 52, 5)
    B("ae_crystal_beacon", 10, 38, 4)
    # ---- the Tilt Quarter: what Tiltside carried off the Listing Isle, and a house the wardens gave them
    B("ae_house_small", 18, 70, 6)
    S("ff_patched_tent", 30, 88, 4)
    S("ff_camp_fire", 24, 84, 3, solid=False)
    # ---- the Gate Stair
    B("ae_lamp_post", 54, 82, 4)
    B("ae_lamp_post", 66, 82, 4)
    B("ae_guard_post", 70, 86, 5)


def register_baked(zone):
    import os
    zone.sky = dict(SKY)
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.webp"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_keelstone():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
