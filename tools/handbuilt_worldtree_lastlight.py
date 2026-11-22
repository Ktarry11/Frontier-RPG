"""
Hand-built Lastlight (120x96): the Fading Firmament's town, 57-60 (Kyle's town rule: one town per open map, on its own
map, as the hub). Kyle, 22 Nov 2026: "Lets build the towns, move the NPCs", and "Caelora cities will have a style to
them as theyre all the same race".

The Firmament's people left in stages as its crystal went dark, and the last of them live round the one shrine still
lit. Lastlight is Aetherian to the bone (white marble gone grey, gold worn thin, crystal everywhere and nearly all of it
dead) like every Caelora town, and its own touch is the light: the shrine burning gold in the middle of a grey town, the
lamps round it relit one by one from its crystals, and the edges of the town already dark. The House of Long Memory
moved its rooms in from Forgewatch so its scholars sleep somewhere lit, and the scholars' Earthborn smith keeps a forge
here for them.

ORIENTATION FOLLOWS THE OVERWORLD. On the Firmament the town's gate stands just north of where the road from the
Bastions ends, so the gate comes in on the town's SOUTH edge, with the Emptied Quarter beyond its north side.

    the gate (60,93), south <- Lastlight's gate on the Fading Firmament (100,190)
    the Lamp Walk: where you come in, between the last lamps
    the Shrine Court: the last lit shrine, its keeper and its crystal-cutter, in the middle
    the Magistrate's Steps: the last magistrate's hall, east
    the Shelter: the pavilions where the families live, the inn and the mail, west
    the Long Memory's Rooms: the House of Long Memory's scholars, north-west
    the Forge Shed: the Earthborn smith's forge, north-east
    the Skiff Ledge: the last skiff that still flies out, on a ledge off the east side

A SKY MAP (SKY): the baker cuts the drop out (tools/bake_ashenvale.sky_cut) and hangs the island's rock under it.

HARD CONTRACTS (world/portal_manager.py)
  portal   (60,93) <-> The Fading Firmament (100,190): arrive (60,88) coming in, (100,194) going out
  NPC ids  ff_* and ll_*: written by tools/build_fading_firmament_people.py from NPC_POSITIONS
"""
import numpy as np

from tools import ashenvale_engine as E
from tools.handbuilt_worldtree_lenswatch import _poly, _seg_dist, _wob

BAKED_DIR = "assets/tiles/sky/baked_lastlight"
NAME = "Lastlight"
W, H = 120, 96
SKP = "assets/tiles/sky/props/"
BLD = "assets/buildings/"

PORTALS = {(60, 93): "The Fading Firmament"}
ARRIVALS = [(60, 88)]
LATER_PORTALS = {}
START = (60, 88)

#: the town's island, cracked round its edges
ISLAND = [(18, 34), (28, 16), (50, 10), (76, 10), (94, 18), (104, 34), (104, 54), (94, 70), (78, 80), (62, 84),
          (44, 80), (26, 72), (14, 56)]
#: the skiff ledge, off the east side
LEDGE = [(108, 40), (116, 42), (117, 56), (108, 58)]
BRIDGES = [
    ([(60, 96), (60, 80)], 2.6),            # the steps up from the road's end
    ([(100, 48), (110, 48)], 2.2),          # the plank out to the skiff ledge
]

SKY = {"far": "sky_far_dusk", "parallax": 0.35, "drift": 2.5, "wisps": 0.35, "sun": 0.2, "far_tiles": 10,
       "underside": 5.0}


def bridge_mask(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    out = np.full(np.shape(gx), 99.0)
    for pts, hw in BRIDGES:
        out = np.minimum(out, _seg_dist(gx, gy, pts) - hw)
    return out


def sea(gx, gy):
    """The drop all round the island. Extent > 0 is a fall into the sky."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    land = np.minimum.reduce([_poly(gx, gy, ISLAND) + _wob(gx, gy), _poly(gx, gy, LEDGE) + 0.5 * _wob(gx, gy),
                              bridge_mask(gx, gy)])
    edge = np.maximum.reduce([-1.0 - gx, gx - (W - 1.0), 2.0 - gy, gy - (H - 2.0)])
    return np.maximum(land, edge * 3.0)


def plaza_field(P, wp):
    """The steps and the plank (the "plaza" layer)."""
    from tools.bake_ashenvale import smoothstep
    return 1.9 * (1.0 - smoothstep(-0.4, 1.2, bridge_mask(P.gx, P.gy)))


ISLETS = []
#: the shrine's wellstone pool, the one in the Firmament that still runs clear
LAKES = {"pools": [(60, 50, 4, 2, 0, 0.0)]}
DEEP_SHRINK = {"pools": 9.0}
RIVERS = []
FORDS = []
MESAS = []
RIDGES = []
WOODS = []
BELTS = []
CLEARINGS = [(60, 46, 40, 30), (112, 48, 6, 8)]
CORRUPT_PATCHES = [(22, 26, 8, 6), (96, 22, 8, 6), (30, 72, 6, 4)]     # where the town has already gone dark
BURNED_PATCHES = [(90, 30, 5, 4)]                                       # round the smith's forge
BLUEBELL_PATCHES = []
#: the old marble: the shrine court, the magistrate's steps, the lamp walk
PAVED_PATCHES = [(60, 46, 14, 9), (86, 48, 8, 6), (60, 72, 6, 8), (34, 48, 8, 5)]
LUSH = 0.0
GRADE = None
DROP = None
GAPS = [("ell", 60, 88, 4, 3), ("ell", 60, 46, 9, 5)]

ROADS = {
    "lamps":    ([(60, 93), (60, 72), (60, 58)], 2.8),
    "court":    ([(36, 48), (60, 42), (86, 48)], 2.6),
    "court_s":  ([(36, 48), (60, 58), (86, 48)], 2.6),
    "rooms":    ([(40, 46), (34, 30)], 2.2),
    "forge":    ([(80, 44), (88, 30)], 2.2),
    "ledge":    ([(86, 48), (110, 48)], 2.2),
}

SPEC = E.Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK, sea=sea, islets=ISLETS,
              mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={}, rock_rim={}, gaps=GAPS, fords=FORDS, thicket=(0.99, 10.0, 2.0))

#: Lastlight's people (tools/build_fading_firmament_people.py writes their records)
NPC_POSITIONS = {
    # the Lamp Walk
    "ll_gatewarden":       (54, 80),    # keeps the gate and lights the walk's lamps
    # the Shelter: the families, the inn and the mail
    "ll_innkeeper":        (28, 54),    # keeps the last beds
    "ff_provisioner":      (34, 62),    # food
    "ff_trader":           (44, 62),    # goods
    "ff_salvager":         (20, 56),    # an Earthborn who salvages what the islands drop
    "ff_child_minder":     (40, 70),    # an Earthborn teacher with the town's children
    # the Shrine Court
    "ff_shrine_keeper":    (60, 38),    # keeps the shrine lit
    "ff_lamp_cutter":      (68, 54),    # the last crystal-cutter
    # the Magistrate's Steps
    "ff_last_magistrate":  (86, 44),    # the Firmament's last magistrate
    "ff_orla":             (90, 54),    # Magister Orla Thessan, come north after her student
    # the Long Memory's Rooms
    "ff_long_memory":      (30, 26),    # Archivist of the House of Long Memory
    "ff_forge_scholar":    (40, 22),    # her student, who reads Kharad runes
    "ff_forgewatch_guard": (46, 30),    # a Lens warden, still guarding the scholars
    # the Forge Shed
    "ff_earthborn_smith":  (84, 24),    # the scholars' Earthborn smith
    # the Skiff Ledge
    "ff_skiffmaster":      (113, 52),   # the flight path: the last skiff that still flies out
}


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


CAVES = {}
#: the districts (later registrations win on overlap). The townsfolk live in these (tools/townsfolk/lastlight.py).
SUBZONES = [
    ("Lastlight", 0, 0, W, H, None),
    ("The Shrine Court", 46, 30, 30, 30, None),
    ("The Shelter", 14, 40, 32, 36, None),
    ("The Magistrate's Steps", 76, 34, 28, 30, None),
    ("The Long Memory's Rooms", 18, 12, 34, 28, None),
    ("The Forge Shed", 74, 12, 30, 22, None),
    ("The Skiff Ledge", 104, 38, 16, 22, None),
    ("The Lamp Walk", 48, 62, 24, 34, None),
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
                             "The last people of the Firmament, round the one shrine still lit: a grey town with a gold "
                             "light in the middle of it, its edges already dark.",
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

    # ---- the Shrine Court: the last lit shrine over its pool, its last crystals, the lamps relit from it
    S("ff_lit_shrine", 60, 36, 6)
    S("ff_last_crystal", 52, 38, 3)
    S("ff_last_crystal", 68, 38, 3)
    B("ae_orb_lantern", 50, 54, 4)
    B("ae_orb_lantern", 70, 46, 4)
    # ---- the Shelter: the families' pavilions, the inn, the soup table
    B("ae_guesthouse", 24, 50, 8)
    B("ae_refugee_pavilion", 38, 58, 6)
    B("ae_refugee_pavilion", 22, 68, 5)
    B("ae_soup_table", 30, 66, 3)
    # ---- the Magistrate's Steps: the magistrate's hall, its marble cracked, a fallen statue left where it fell
    B("ae_magister_hall", 92, 40, 9)
    S("ff_toppled_magister", 98, 60, 4)
    # ---- the Long Memory's Rooms: the house's archive and its shelves, moved in from Forgewatch
    B("ae_archive", 26, 22, 8)
    B("ae_instrument_shelf", 44, 26, 3)
    B("ae_chart_desk", 36, 30, 2)
    # ---- the Forge Shed: the Earthborn smith's forge, relit
    B("ae_forge", 92, 28, 6)
    S("ff_salvage", 80, 30, 3)
    # ---- the Skiff Ledge: the last skiff
    B("ae_skiff_small", 114, 46, 5, allow_overlap=True)
    # ---- the Lamp Walk: the lamps on the way in
    for (x, y) in [(55, 66), (65, 66), (55, 76), (65, 76)]:
        B("ae_lamp_post", x, y, 4)
    # ---- the edges, already dark
    S("ff_dead_crystal_tree", 22, 32, 6)
    S("ff_dead_crystal_tree", 100, 24, 6)
    S("ff_dim_shards", 32, 74, 3, solid=False)
    S("ff_broken_pylon", 96, 66, 5)


def register_baked(zone):
    import os
    zone.sky = dict(SKY)
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.webp"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_lastlight():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


def shape_preview(path, scale=4):
    return SPEC.shape_preview(path, scale, portals=list(PORTALS), npc=list(NPC_POSITIONS.values()))
