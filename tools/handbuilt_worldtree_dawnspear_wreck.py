"""
Hand-built Dawnspear Wreck (120x96): the Ascendant Bastions' town, 54-57 (Kyle's town rule: one town per open map, on
its own map, as the hub). Kyle, 22 Nov 2026: "Lets build the towns, move the NPCs", and "Caelora cities will have a
style to them as theyre all the same race".

The Dawnspear was an Ascendancy war-skiff until Captain Isolde Marrane brought her down rather than fire on Tethertown.
She broke in two on the islet south-west of the fort, and the deserters, the free skiffs and anyone else who'd walked
away from the Ascendancy built a camp in and round her. It's still Aetherian work (white marble, gold, crystal) with
the Ascendancy's bronze plate and blue cloth on everything, because that's what the ship was made of. Its own touch is
the wreck itself: the bow and the stern lying apart with the town between them, sails strung up as awnings, the mess in
the stern, the captain's cabin in the bow.

ORIENTATION FOLLOWS THE OVERWORLD. On the Bastions the camp's gate stands on the south side of the wreck's islet, so the
gate comes in on the town's NORTH edge.

    the gate (60,3), north <- Dawnspear Wreck's gate on the Bastions (40,209)
    the Gangway: where you come in, down from the islet
    the Bow: the captain's cabin and the lookout's perch, the broken bow section to the east
    the Stern Mess: the inn in the stern section, west, and the mail
    the Sail Market: the provisioner and the trader under the sails, in the middle
    the Sickbay: the surgeon's tents, south-west
    the Lance Yard: the deserters' rack and dummies, south-east
    the Skiff Moorings: the free skiffs (the flight path), on the islet's south tip

A SKY MAP (SKY): the baker cuts the drop out (tools/bake_ashenvale.sky_cut) and hangs the island's rock under it.

HARD CONTRACTS (world/portal_manager.py)
  portal   (60,3) <-> The Ascendant Bastions (40,209): arrive (60,8) coming in, (40,205) going out
  NPC ids  ab_* and dw_*: written by tools/build_ascendant_bastions_people.py from NPC_POSITIONS
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_worldtree_lenswatch import _poly, _seg_dist, _wob

BAKED_DIR = "assets/tiles/sky/baked_dawnspear_wreck"
NAME = "Dawnspear Wreck"
W, H = 120, 96
SKP = "assets/tiles/sky/props/"
BLD = "assets/buildings/"

PORTALS = {(60, 3): "The Ascendant Bastions"}
ARRIVALS = [(60, 8)]
LATER_PORTALS = {}
START = (60, 8)

#: the wreck's islet, long east to west, the moorings on its south tip
ISLAND = [(14, 30), (26, 16), (48, 10), (72, 10), (96, 16), (108, 30), (110, 48), (100, 62), (82, 70), (70, 84),
          (56, 88), (46, 80), (34, 70), (18, 60), (10, 46)]
BRIDGES = [
    ([(60, 0), (60, 14)], 2.6),             # the gangway down from the islet
]

SKY = {"far": "sky_far_storm", "parallax": 0.35, "drift": 6.0, "wisps": 0.55, "sun": 0.25, "far_tiles": 10,
       "underside": 5.0}


def bridge_mask(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    out = np.full(np.shape(gx), 99.0)
    for pts, hw in BRIDGES:
        out = np.minimum(out, _seg_dist(gx, gy, pts) - hw)
    return out


def sea(gx, gy):
    """The drop all round the islet. Extent > 0 is a fall into the sky."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    land = np.minimum.reduce([_poly(gx, gy, ISLAND) + _wob(gx, gy), bridge_mask(gx, gy)])
    edge = np.maximum.reduce([-1.0 - gx, gx - (W - 1.0), -1.0 - gy, gy - (H - 2.0)])
    return np.maximum(land, edge * 3.0)


def plaza_field(P, wp):
    """The gangway (the "plaza" layer, painted as the Ascendancy's bronze deck plates)."""
    from tools.bake_ashenvale import smoothstep
    return 1.9 * (1.0 - smoothstep(-0.4, 1.2, bridge_mask(P.gx, P.gy)))


ISLETS = []
#: rainwater caught in the bow's broken plates
LAKES = {"pools": [(94, 30, 3, 2, 0, 0.2)]}
DEEP_SHRINK = {"pools": 9.0}
RIVERS = []
FORDS = []
MESAS = []
RIDGES = []
WOODS = []
BELTS = []
CLEARINGS = [(60, 40, 50, 30), (60, 78, 14, 8)]
CORRUPT_PATCHES = []
BURNED_PATCHES = [(30, 26, 8, 5), (90, 24, 8, 5)]       # scorched where the two halves hit
BLUEBELL_PATCHES = []
#: the camp's deck: plates salvaged off the hull, laid as floors under the sails, in the mess and in the yard
PAVED_PATCHES = [(60, 40, 18, 8), (28, 30, 10, 6), (90, 30, 10, 6), (36, 56, 8, 5), (84, 56, 9, 5),
                 (60, 78, 9, 5)]
LUSH = 0.0
GRADE = None
DROP = None
GAPS = [("ell", 60, 8, 4, 3), ("ell", 60, 40, 9, 5)]

ROADS = {
    "gangway":  ([(60, 3), (60, 20), (60, 36)], 2.8),
    "deck":     ([(26, 38), (60, 40), (94, 38)], 2.6),
    "sickbay":  ([(44, 42), (36, 54)], 2.2),
    "yard":     ([(76, 42), (84, 54)], 2.2),
    "moorings": ([(60, 40), (60, 60), (60, 76)], 2.4),
}

SPEC = E.Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
              mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={}, rock_rim={}, gaps=GAPS, fords=FORDS, thicket=(0.99, 10.0, 2.0))

#: Dawnspear Wreck's people (tools/build_ascendant_bastions_people.py writes their records)
NPC_POSITIONS = {
    # the Gangway
    "dw_gatewarden":       (54, 14),    # a deserter who keeps the gangway
    # the Stern Mess: the inn
    "dw_steward":          (30, 37),    # the Dawnspear's old mess steward, who keeps the inn
    # the Bow
    "ab_wreck_captain":    (88, 36),    # Captain Isolde Marrane
    "ab_lookout":          (100, 30),   # on the bow, watching the fort
    # the Sail Market
    "ab_provisioner":      (52, 46),    # food
    "ab_trader":           (68, 46),    # goods
    "ab_unsworn_scholar":  (60, 30),    # Magister Orla Thessan, at her chart desk under the main sail
    # the Sickbay
    "ab_wreck_surgeon":    (30, 56),    # the camp's surgeon
    # the Lance Yard
    "ab_lancer_deserter":  (90, 56),    # Lancer Tavin Roake
    # the Skiff Moorings
    "ab_skiffmaster":      (66, 78),    # the flight path: the free skiffs
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}
#: the districts (later registrations win on overlap). The townsfolk live in these (tools/townsfolk/dawnspear_wreck.py).
SUBZONES = [
    ("Dawnspear Wreck", 0, 0, W, H, None),
    ("The Sail Market", 42, 24, 36, 26, None),
    ("The Stern Mess", 10, 18, 32, 26, None),
    ("The Bow", 78, 14, 36, 30, None),
    ("The Sickbay", 16, 46, 32, 22, None),
    ("The Lance Yard", 74, 44, 32, 22, None),
    ("The Skiff Moorings", 44, 66, 32, 26, None),
    ("The Gangway", 48, 0, 24, 22, None),
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
                             "The deserters' town in the wreck of the Dawnspear: the bow and the stern lying apart on "
                             "their islet, sails strung between them, and the free skiffs moored at the south tip.",
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

    # ---- the Stern Mess: the stern section lying on its side, the inn inside it
    B("ae_war_skiff", 26, 32, 10, allow_overlap=True)
    B("ae_deck_cargo", 38, 30, 3)
    B("ae_mast", 16, 40, 8)
    # ---- the Bow: the broken bow section, the captain's cabin, the lookout's perch at the prow
    B("ae_war_skiff", 94, 28, 10, allow_overlap=True)
    B("ae_captain_chair", 84, 32, 2)
    B("ae_ship_wheel", 92, 36, 3)
    B("ae_deck_cannon", 104, 38, 3)
    # ---- the Sail Market: the main sail strung as an awning, the scholar's desk under it, the stalls
    B("ae_field_pavilion", 69, 28, 6)
    B("ae_chart_desk", 56, 30, 2)
    B("ae_kiosk_cloth", 48, 52, 4)
    B("ae_supply_crates", 74, 52, 3)
    B("ae_war_standard", 77, 30, 5)
    S("ab_ship_ribs", 46, 22, 6)
    # ---- the Sickbay: the surgeon's tents under a sail
    B("ae_soldier_tent", 24, 52, 5)
    B("ae_soldier_tent", 38, 62, 5)
    B("ae_belongings", 22, 60, 2)
    # ---- the Lance Yard: the deserters' rack of laid-down lances, and the dummies they train the camp on
    S("ab_lance_rack", 96, 52, 4)
    S("ab_training_dummy", 84, 60, 3)
    S("ab_training_dummy", 98, 60, 3)
    B("ae_banner", 80, 48, 5)
    # ---- the Skiff Moorings: the free skiffs tied off the south tip
    B("ae_skiff_dock", 56, 84, 5)
    B("ae_skiff_small", 72, 84, 5, allow_overlap=True)
    B("ae_crystal_beacon", 50, 76, 4)
    # ---- the Gangway
    B("ae_lamp_post", 54, 10, 4)
    B("ae_lamp_post", 66, 10, 4)


def register_baked(zone):
    import os
    zone.sky = dict(SKY)
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.webp"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_dawnspear_wreck():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
