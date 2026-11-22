"""
Hand-built Halcyon Rest (120x100): the Celestial Expanse's town, 49-51 (Kyle's town rule: one town per open map, on
its own map, as the hub). Kyle, 22 Nov 2026: "Lets build the towns, move the NPCs", and "Keep in mind Caelora cities
will have a style to them as theyre all the same race".

Halcyon Rest is the Aetherian waystation halfway up the Great Sky River. It has fed travellers on the river for three
hundred years, and since the Eighth Ring fell it has taken in the ring's refugees too. It's built the Aetherian way
(white marble trimmed with gold, crystal lamps, blue cloth) like Lenswatch and Aurelion, and its own touch is the
garden: a pool in a ring of silver trees, pavilions round it, bells on the arches. Tethertown, the Earthborn's two
rocks, is tied on below its south-west edge with planks and rope, so the town's two peoples live a plank apart.

ORIENTATION FOLLOWS THE OVERWORLD. On the Expanse the Rest's gate stands on the west side of Halcyon Rest's island, so
the gate comes in on the town's WEST edge. The Lancer's Perch is east of the Rest, and the skiff dock looks that way.

    the gate (2,48), west <- the Rest's gate on the Expanse (196,74)
    the Rest Gate: where you come in, off the gangway from the island
    the Guest Hall: the inn, north-west, and the mail
    the Pool Garden: the pool in the middle, the keeper's pavilion and the silver grove
    the Pavilions: the Eighth Ring's refugees, north-east, round the soup table
    the Market Steps: the provisioner, the trader and the kiosks, south
    the Skiff Dock: the flight path, an islet up a light bridge to the east
    Tethertown: the Earthborn's two rocks, tied on below the south-west edge

A SKY MAP (SKY): the baker cuts the drop out (tools/bake_ashenvale.sky_cut) and hangs the island's rock under it.

HARD CONTRACTS (world/portal_manager.py)
  portal   (2,48) <-> The Celestial Expanse (196,74): arrive (7,48) coming in, (196,77) going out
  NPC ids  ce_* and hr_*: written by tools/build_celestial_expanse_people.py from NPC_POSITIONS
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_worldtree_lenswatch import _poly, _seg_dist, _wob

BAKED_DIR = "assets/tiles/sky/baked_halcyon_rest"
NAME = "Halcyon Rest"
W, H = 120, 100
SKP = "assets/tiles/sky/props/"
BLD = "assets/buildings/"

PORTALS = {(2, 48): "The Celestial Expanse"}
ARRIVALS = [(7, 48)]
LATER_PORTALS = {}
START = (7, 48)

#: the Rest's island, the garden on top of it
ISLAND = [(14, 40), (20, 22), (36, 12), (58, 10), (80, 12), (96, 22), (100, 40), (98, 58), (88, 72), (70, 82),
          (50, 82), (34, 76), (18, 64)]
#: the skiff dock's islet, east, up a light bridge
DOCK = [(104, 36), (116, 38), (118, 52), (114, 62), (104, 60)]
#: Tethertown's two rocks, tied on below the south-west edge
ROCK_A = [(12, 82), (24, 78), (36, 84), (32, 94), (16, 94)]
ROCK_B = [(42, 88), (54, 86), (62, 92), (56, 98), (44, 97)]
#: plank, rope and light across the drop
BRIDGES = [
    ([(0, 48), (16, 48)], 2.6),             # the gangway from the island's gate
    ([(98, 48), (106, 48)], 2.4),           # the light bridge to the skiff dock
    ([(30, 74), (26, 82)], 2.2),            # Tethertown's planks down to the first rock
    ([(34, 89), (44, 91)], 2.0),            # the planks from the first rock to the second
]

SKY = {"far": "sky_far_day", "parallax": 0.35, "drift": 5.0, "wisps": 0.6, "sun": 0.35, "far_tiles": 10,
       "underside": 5.0}


def bridge_mask(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    out = np.full(np.shape(gx), 99.0)
    for pts, hw in BRIDGES:
        out = np.minimum(out, _seg_dist(gx, gy, pts) - hw)
    return out


def sea(gx, gy):
    """The drop all round the islands. Extent > 0 is a fall into the sky."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    land = np.minimum.reduce([_poly(gx, gy, ISLAND) + _wob(gx, gy), _poly(gx, gy, DOCK) + 0.5 * _wob(gx, gy),
                              _poly(gx, gy, ROCK_A) + 0.5 * _wob(gx, gy), _poly(gx, gy, ROCK_B) + 0.5 * _wob(gx, gy),
                              bridge_mask(gx, gy)])
    edge = np.maximum.reduce([-1.0 - gx, gx - (W - 1.0), 2.0 - gy, gy - (H - 2.0)])
    return np.maximum(land, edge * 3.0)


def plaza_field(P, wp):
    """The gangway, the planks and the light bridge (the "plaza" layer)."""
    from tools.bake_ashenvale import smoothstep
    return 1.9 * (1.0 - smoothstep(-0.4, 1.2, bridge_mask(P.gx, P.gy)))


ISLETS = []
#: the garden's pool, and the little pool by the guest hall
LAKES = {"pools": [(60, 48, 6, 3, 0, 0.4), (24, 30, 3, 2, 0, 1.0)]}
DEEP_SHRINK = {"pools": 9.0}
RIVERS = []
FORDS = []
MESAS = []
RIDGES = []
WOODS = []
BELTS = []
CLEARINGS = [(58, 46, 40, 30), (110, 48, 10, 10), (24, 88, 10, 6), (52, 92, 8, 4)]
CORRUPT_PATCHES = []
BURNED_PATCHES = []
#: sky-flowers in the garden beds
BLUEBELL_PATCHES = [(46, 60, 6, 3), (74, 60, 6, 3), (52, 34, 5, 3), (86, 46, 4, 6)]
#: the Rest's white stone: the gate court, the guest hall's steps, the ring round the pool, the market steps
PAVED_PATCHES = [(16, 48, 10, 6), (34, 36, 8, 4), (60, 48, 14, 9), (60, 68, 16, 5), (78, 28, 10, 4),
                 (108, 48, 7, 6)]
LUSH = 0.0
GRADE = None
DROP = None
GAPS = [("ell", 7, 48, 4, 3), ("ell", 60, 48, 9, 5)]

ROADS = {
    "gate":      ([(6, 48), (26, 48), (42, 46)], 2.8),
    "garden_n":  ([(42, 46), (52, 40), (68, 40), (80, 46)], 2.4),
    "garden_s":  ([(42, 46), (50, 56), (70, 57), (80, 46)], 2.4),
    "dock":      ([(80, 46), (96, 48), (110, 48)], 2.6),
    "inn":       ([(34, 47), (34, 37)], 2.2),
    "pavilions": ([(70, 40), (78, 31)], 2.2),
    "market":    ([(60, 57), (60, 70)], 2.4),
    "tether":    ([(42, 52), (32, 66), (28, 78), (24, 86)], 2.0),
}

SPEC = E.Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
              mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={}, rock_rim={}, gaps=GAPS, fords=FORDS, thicket=(0.99, 10.0, 2.0))

#: Halcyon Rest's people (tools/build_celestial_expanse_people.py writes their records)
NPC_POSITIONS = {
    # the Rest Gate
    "hr_gatewarden":      (14, 44),    # the Rest's gatewarden
    # the Guest Hall: the inn and the mail
    "hr_innkeeper":       (37, 38),    # the guest hall's keeper (the inn)
    # the Pool Garden
    "ce_keeper":          (64, 43),    # Keeper Ithren Lorrow, at his pavilion over the pool
    "ce_ilaren":          (50, 50),    # Ilaren Vey, up the river from the wreck
    "ce_leandro":         (48, 44),    # Leandro Arrieta, likewise
    "ce_golem_scholar":   (72, 52),    # Scholar Idris Marrowell, her notes spread on the dais
    # the Pavilions: the Eighth Ring's refugees
    "ce_refugee":         (74, 33),    # Teodric Ashlane
    "ce_herald":          (84, 34),    # Herald Cassian Orel, lodged with the refugees
    # the Market Steps
    "ce_provisioner":     (54, 70),    # food and drink
    "ce_trader":          (66, 70),    # goods, and buys salvage
    # the Skiff Dock
    "ce_skiffmaster":     (108, 44),   # the flight path: the skiffs
    "ce_deserter":        (112, 54),   # Dace Morrow, looking east at the Perch
    # Tethertown: the Earthborn
    "ce_tether_lead":     (22, 86),    # Kaisa Lehtonen
    "ce_tether_rigger":   (30, 88),    # Gustavo Pires, by the planks
    "ce_tether_farmer":   (18, 90),    # Annelies de Vries, at her rows
    "ce_tether_trader":   (50, 92),    # Yasmin Darwish, at her oven on the second rock
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}
#: the districts (later registrations win on overlap). The townsfolk live in these (tools/townsfolk/halcyon_rest.py).
SUBZONES = [
    ("Halcyon Rest", 0, 0, W, H, None),
    ("The Rest Gate", 0, 38, 30, 20, None),
    ("The Guest Hall", 14, 12, 34, 26, None),
    ("The Pavilions", 66, 12, 34, 24, None),
    ("The Pool Garden", 40, 36, 44, 26, None),
    ("The Market Steps", 40, 62, 46, 22, None),
    ("The Skiff Dock", 98, 34, 22, 30, None),
    ("Tethertown", 8, 76, 58, 24, None),
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
                             "The Aetherian waystation halfway up the Great Sky River: a garden round a pool, "
                             "pavilions full of the Eighth Ring's refugees, and Tethertown's two rocks tied on below.",
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

    # ---- the Rest Gate: lamps either side of the way in, the travellers' crates stacked off the path
    B("ae_lamp_post", 12, 42, 4)
    B("ae_lamp_post", 14, 54, 4)
    B("ae_supply_crates", 22, 56, 3)
    B("ae_banner", 22, 42, 5)
    # ---- the Guest Hall (the inn), with its little pool and a bench
    B("ae_guesthouse", 34, 33, 10)
    B("ae_planter", 26, 36, 3)
    B("ae_bench", 44, 30, 2)
    S("sk_silver_tree", 20, 26, 7)
    # ---- the Pool Garden: the keeper's pavilion over the pool, the garden pavilion, the silver grove, the dais
    B("ae_pool_pavilion", 62, 36, 7)
    B("ae_garden_pavilion", 48, 40, 6)
    B("ae_silver_grove", 78, 60, 6)
    B("ae_meditation_dais", 72, 55, 3)
    for (x, y) in [(52, 54), (70, 44), (46, 58), (76, 52)]:
        B("ae_lamp_post", x, y, 4)
    S("sk_silver_tree", 44, 62, 7)
    S("sk_blossom_tree", 84, 40, 6)
    S("sk_temple_bell", 56, 60, 4)
    # ---- the Pavilions: the Eighth Ring's refugees round the soup table, their belongings piled by the beds
    B("ae_refugee_pavilion", 70, 29, 6)
    B("ae_refugee_pavilion", 88, 30, 6)
    B("ae_soup_table", 79, 34, 3)
    B("ae_belongings", 92, 34, 2)
    S("sk_ancient_bell", 82, 20, 4)
    # ---- the Market Steps: three kiosks and the stores
    B("ae_kiosk_cloth", 48, 68, 4)
    B("ae_kiosk_crystal", 60, 76, 4)
    B("ae_kiosk_scrolls", 72, 68, 4)
    B("ae_crystal_crates", 78, 74, 3)
    # ---- the Skiff Dock: its own islet, the skiffs hung off the edge, the beacon
    B("ae_skiff_dock", 112, 42, 6)
    B("ae_skiff_small", 116, 58, 5, allow_overlap=True)
    B("ae_crystal_beacon", 104, 58, 4)
    # ---- Tethertown: houses out of what the Aetherians threw away, round one fire, the ropes on their posts
    S("ff_camp_fire", 26, 90, 3, solid=False)
    B("ae_damaged_house", 18, 84, 6)
    S("ff_patched_tent", 32, 93, 4)
    S("ff_salvage", 58, 95, 3)
    S("ff_patched_tent", 46, 95, 4)
    S("lk_tether_post", 28, 80, 3)
    S("lk_tether_post", 40, 91, 3)
    S("sk_clover_patch", 14, 92, 2, solid=False)
    # ---- the island's own: crystal out of the rock where nothing's built
    S("sk_crystal_blue", 92, 62, 4)
    S("sk_crystal_gold", 30, 18, 4)


def register_baked(zone):
    import os
    zone.sky = dict(SKY)
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.webp"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_halcyon_rest():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
