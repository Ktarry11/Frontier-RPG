"""
Hand-built North Western Plaguelands (180x140), level 53-56. docs/plaguelands_design.md.

The top half of WoW's Western Plaguelands, read north-up: the Scarlet Crusade's country. Hearthglen sits on its hill
at the top of the map behind its walls (the new dungeon, its own map), the Crusade works Northridge for timber, the
fourth cauldron poisons Gahrron's Withering, and the Thondroril runs down the east side to the Eastern Plaguelands.

Structure (tile coords, y down):

    South gate ......... (96,137): back to South WPL
    The Pale Watch ..... the Order of the Pale Flame's forward camp (92,112): a few of Rory's people watching the road
    Northridge ......... the Scarlet lumber camp in the west (40,60)
    Gahrron's Withering  the fourth cauldron, east of centre (128,82)
    Hearthglen Fields .. Scarlet patrols and pyres on the slope below the walls (100,34)
    Hearthglen ......... the gate at the top (100,6): the dungeon, its own map
    The Thondroril ..... the river on the east side; the crossing (176,70) leads to West EPL

LATER PORTALS (their ground is cut; they go live with their maps): Hearthglen (100,6), West EPL (176,70).
"""
import numpy as np

from tools import ashenvale_engine as E

BAKED_DIR = "assets/tiles/plaguelands/baked_wpl_north"
EK = "assets/tiles/eastern_kingdoms/props/"
UF = "assets/tiles/undead_farmland/props/"
HF = "assets/tiles/haunted_forest/props/"
CI = "assets/tiles/cursed_isle/props/"
PL = "assets/tiles/plaguelands/props/"
W, H = 180, 140
NAME = "Western Plaguelands North"

PORTALS = {(96, 137): "Western Plaguelands South", (176, 70): "Eastern Plaguelands West", (146, 28): "The Weeping Cave"}
ARRIVALS = [(96, 133), (172, 70), (146, 26)]
LATER_PORTALS = {
    (100, 6): ("Hearthglen", None),
}
START = (96, 128)

ROADS = {
    # the King's Road north to Hearthglen
    "kings":      ([(96, 138), (96, 124), (92, 110), (90, 94), (94, 76), (98, 60), (100, 44), (100, 26), (100, 14),
                    (100, 5)], 3.4),
    # west to Northridge
    "northridge": ([(92, 98), (76, 90), (60, 78), (46, 66), (40, 60)], 2.8),
    # east to Gahrron's and on to the river crossing
    "gahrron":    ([(94, 80), (110, 82), (126, 82)], 2.6),
    "crossing":   ([(126, 82), (142, 78), (160, 72), (176, 70)], 2.8),
}

RIVERS = [   # the Thondroril, out of the north down the east side
    ([(164, 0), (166, 24), (162, 48), (166, 70), (164, 96), (168, 120), (166, 140)], 3.6, 1.6),
]
FORDS = [(165, 71, 7)]

LAKES = {"ponds": [(60, 110, 5, 3.5, 0, 0.7), (140, 30, 4, 3, 0, 1.9)]}
DEEP_SHRINK = {"ponds": 1.8}

MESAS = [
    (70, 30, 7, 6, 10), (130, 50, 6, 8, 0), (24, 100, 6, 7, 0), (120, 118, 5, 5, 0), (56, 40, 4, 5, 0),
    (144, 104, 4, 6, 0),
]
RIDGES = [
    ([(76, 20), (86, 14), (90, 22)], 2.4),        # the shoulder of Hearthglen's hill, west
    ([(112, 22), (120, 14), (128, 20)], 2.4),     # ... and east
]
WOODS = [
    (28, 30, 10, 9, 0, 1.1), (54, 120, 8, 6, 0, 0.3), (150, 124, 8, 7, 0, 2.2), (136, 98, 5, 6, 0, 1.4),
    (20, 76, 6, 9, 0, 0.6), (112, 64, 5, 6, 0, 2.6),
]
BELTS = []
CLEARINGS = [
    (96, 132, 9, 6),            # the south gate
    (92, 112, 10, 7),           # the Pale Watch
    (40, 60, 15, 12),           # Northridge
    (128, 82, 13, 10),          # Gahrron's Withering
    (100, 34, 18, 12),          # Hearthglen Fields
    (100, 10, 10, 7),           # Hearthglen's gate
    (168, 70, 9, 7),            # the crossing
]
GAPS = [
    ("ell", 96, 137, 8, 6), ("ell", 100, 6, 9, 6), ("ell", 176, 70, 7, 6),
    ("ell", 92, 112, 8, 6), ("ell", 40, 60, 12, 9), ("ell", 128, 82, 10, 8), ("ell", 100, 34, 15, 10),
]

SPEC = E.Spec(NAME, W, H, ROADS, rivers=RIVERS, lakes=LAKES, deep_shrink=DEEP_SHRINK,
              mesas=MESAS, ridges=RIDGES, woods=WOODS, belts=BELTS, clearings=CLEARINGS,
              rim={"north": 4, "south": 4}, rock_rim={"west": 7, "east": 4}, gaps=GAPS, fords=FORDS,
              thicket=(0.78, 9.0, 0.4))

#: the Pale Watch: the Order's forward camp under Hearthglen. Quests come from Sorrow Hill; these watch the road.
NPC_POSITIONS = {
    "wpln_pf_watch_captain": (90, 108),
    "wpln_pf_scout": (98, 110),
    "wpln_pf_field_medic": (88, 116),
    "wpln_pf_sister": (84, 104),
    "wpln_pf_woodwright": (94, 100),
    "wpln_pf_angler": (98, 116),
    "wpln_pf_clerk": (82, 112),
}

SUBZONES = [
    ("Northridge Lumber Camp", 22, 44, 38, 32, None),
    ("Gahrron's Withering", 112, 68, 32, 28, None),
    ("Hearthglen Fields", 76, 18, 48, 30, None),
    ("The Thondroril", 152, 4, 28, 132, None),
    ("The Pale Watch", 80, 102, 24, 20, None),
]


def fields(gx, gy):
    return SPEC.fields(gx, gy)


def tile_kind(gx, gy):
    return SPEC.tile_kind(gx, gy)


def road_dist(gx, gy, names=None):
    return SPEC.road_dist(gx, gy, names)


#: the cave mouths (tools/handbuilt_plaguelands_caves.py MOUTHS): portal tile -> (sprite, w, h)
CAVES = {(146, 28): ("ent_wailing_maw", 8, 6)}

TREES = {   # Kyle's dead oaks lead; Northridge keeps its tall pines (it's a lumber camp); blight pines in the woods
    "big": [(PL + "pl_dead_oak.png", 9), (EK + "ek_pine_tall.png", 9), (EK + "ek_dead_oak.png", 9)],
    "mid": [(PL + "pl_dead_oak.png", 8), (UF + "dead_tree_bare.png", 7), (EK + "ek_pine_tall.png", 8)],
    "small": [(UF + "dead_tree_bare.png", 6), (PL + "pl_dead_oak.png", 6)],
    "woods": [(EK + "ek_pine_trio.png", 9), (PL + "pl_dead_oak.png", 9), (PL + "pl_blight_pine.png", 9)],
}

BLUEBELL_PATCHES = [(40, 60, 10, 7), (100, 36, 14, 8)]          # cut timber and trampled fields
CORRUPT_PATCHES = [(128, 84, 7, 5)]                               # the cauldron's blight
BURNED_PATCHES = [(100, 30, 6, 4), (40, 58, 6, 4)]                # the pyres and the burned stumps
PAVED_PATCHES = [(100, 12, 7, 4), (92, 112, 5, 4)]
GRADE = (1.0, 1.05)        # (saturation, value): Kyle's ground sheet is lit already; a touch of lift


def build_layout():
    AL = E.make_layout_class(SPEC, NAME,
                             "The Scarlet Crusade's half of the Western Plaguelands, from Northridge's saws to "
                             "Hearthglen's walls, with the fourth cauldron burning at Gahrron's Withering.",
                             "Eastern Kingdoms - Lordaeron", PORTALS, ARRIVALS, NPC_POSITIONS)
    L = AL()
    E.terrain(L)
    E.place_portals(L, PORTALS, ARRIVALS, CAVES)
    for (px, py) in LATER_PORTALS:
        L.z.collision_layer[py][px] = None
    E.seal_unreachable(L, START)
    dress(L)
    E.build_free_mask(L, NPC_POSITIONS.values())
    for lm in L.z.landmarks:
        ax, ay, w, h = lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]
        L.free_mask[max(0, ay):ay + h + 1, max(0, ax - 1):ax + w + 1] = False
    E.scatter_trees(L, TREES, seed=6201, spacing=7.6, scale=1.0)
    sprinkle(L)
    E.seal_unreachable(L, START)
    chests(L)
    E.register_subzones(L, SUBZONES)
    return L


def sprinkle(L):
    import random
    rnd = random.Random(6203)
    ys, xs = np.nonzero(L.free_mask)
    idx = list(range(len(xs)))
    rnd.shuffle(idx)
    n = {"thorn": 0, "rock": 0}
    for i in idx:
        x, y = int(xs[i]), int(ys[i])
        if not L.free_mask[y, x]:
            continue
        r = rnd.random()
        if n["thorn"] < 34 and r < 0.020:
            n["thorn"] += bool(L.prop("ek_thorn_bush", x, y, 3, path_dir=EK, solid=False, nudge=0))
        elif n["rock"] < 18 and r < 0.030:
            n["rock"] += bool(L.prop("rock_outcrop_small", x, y, 4, path_dir=E.AP, solid=False, nudge=0))
    L.clutter = n


CHEST_SPOTS = [(30, 50), (52, 70), (118, 76), (140, 88), (84, 30), (116, 36), (70, 110), (140, 116), (26, 120),
               (150, 60)]


def chests(L):
    for (x, y) in CHEST_SPOTS:
        L.chest(x, y)


def dress(L):
    P = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=EK, **kw)
    Q = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=PL, **kw)      # Kyle's Plaguelands props
    BQ = lambda n, x, y, h, **kw: L.prop(n, x, y, h, path_dir=PL, fraction=0.5, **kw)
    B = L.bld

    # ---- the Pale Watch: the Order's forward camp
    Q("pf_field_tent", 86, 108, 5)
    Q("pf_field_tent", 84, 116, 5)
    B("ek_border_watchtower", 98, 105, 8)
    Q("pf_banner", 94, 106, 5)
    Q("pf_weapon_rack", 100, 114, 3)
    P("ek_signpost", 100, 118, 4)

    # ---- Northridge Lumber Camp: the Crusade's saws
    B("ek_sawmill_shed", 36, 54, 7)
    B("sc_barracks", 50, 56, 7)
    Q("sc_war_tent", 30, 64, 5)
    Q("sc_supply_cart", 52, 66, 4)
    P("ek_scarlet_banner", 44, 52, 5)
    P("ek_scarlet_crates", 42, 66, 3)
    P("ek_farm_cart", 34, 68, 3)

    # ---- Gahrron's Withering: the fourth cauldron
    BQ("pl_farmhouse_burned", 122, 76, 7)
    BQ("pl_barn_plagued", 138, 78, 7)
    Q("pl_cauldron_platform", 128, 86, 6)
    Q("pl_runoff_pool", 134, 88, 3, solid=False)
    Q("pl_corpse_sacks", 120, 88, 3)
    Q("pl_fence_broken", 116, 82, 3, solid=False)

    # ---- Hearthglen Fields: patrols and pyres below the walls
    for (x, y) in [(88, 32), (112, 32), (100, 42)]:
        Q("sc_war_tent", x, y, 5)
    for (x, y) in [(94, 24), (106, 24), (84, 40), (116, 40)]:
        P("ek_scarlet_banner", x, y, 5)
    Q("sc_pyre", 92, 44, 4)
    Q("sc_pyre", 110, 44, 4)
    B("mardenholde_tower", 124, 26, 9)           # a Scarlet watchtower on the eastern shoulder
    Q("sc_supply_cart", 120, 36, 4)

    # ---- Hearthglen's gate (the dungeon is its own map)
    B("hearthglen_gatehouse", 100, 14, 9, road_ok=True, nudge=0)

    # ---- the crossing
    P("ek_signpost", 158, 66, 4)


def register_baked(zone):
    import os
    if os.path.isdir(BAKED_DIR) and os.path.exists(f"{BAKED_DIR}/ground_0_0.jpg"):
        E.register_baked(zone, BAKED_DIR, W, H)
        return True
    return False


def generate_wpl_north():
    L = build_layout()
    register_baked(L.zone)
    return L.zone


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/wpl_north_shape.png"
    L = build_layout()
    seen, walk, _ = E.reachable_report(L, START)
    print(f"placed={L.placed} trees={L.trees} sealed={L.sealed} walkable={walk} reachable={seen} skipped={len(L.skipped)}")
    for sk in L.skipped:
        if sk[0] not in ("ek_thorn_bush", "rock_outcrop_small"):
            print("  skipped", sk)
    SPEC.shape_preview(out, 4, portals=list(PORTALS) + list(LATER_PORTALS), npc=list(NPC_POSITIONS.values()), layout=L)
    print("wrote", out)
