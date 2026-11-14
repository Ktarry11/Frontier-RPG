"""
Hand-built Brill (96x78): the Forsaken village on the hill, hub of Tirisfal Glades.

TOWN ARCHETYPE: HIGH STREET.  One crooked street climbs from the west gate (the road from Deathknell and Western Tirisfal) through
the square to the east gate (the road on to the Undercity, the zeppelin landing and Eastern Tirisfal); the Town Hall closes the
square's north lane, the graveyard terrace sits behind the inn, the apothecary and chapel line the east lane, and the village's
last farm plots straggle off the south lane.  (Crossroads is a plus-shaped avenue town and Razor Hill a walled hilltop; this is a
long street with terraces and back-lanes - the shape Brill has on the real map: a village strung along the road.)

Same recipe as Crossroads (tools/town_kit.py + tools/tirisfal_kit.py): this module owns the tile data + landform fields; the baker
(tools/bake_tirisfal.py brill) paints from the same fields.

HARD CONTRACTS (world/portal_manager.py)
  portals  Western Tirisfal(5,44)  Eastern Tirisfal(91,44)
  NPC ids  referenced by data/quests/*.json; positions below are written back by tools/sync_tirisfal_npcs.py
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob, superlobe

KEY = "brill"
NAME = "Brill"
DESC = "Brill. A village of the Forsaken, built over the bones of a human town."
REGION = "Eastern Kingdoms - Lordaeron"
W, H = 96, 78
BAKED_DIR = "assets/tiles/brill/baked"
IS_TOWN = True
BASE_TILE = "grass"

PORTALS = {(5, 44): "Western Tirisfal", (91, 44): "Eastern Tirisfal"}
ARRIVALS = [(9, 44), (87, 44)]
START = (20, 44)

ROADS = {
    "high":      ([(5, 44), (16, 45), (28, 43), (39, 41), (48, 40), (58, 40), (68, 42), (80, 44), (91, 44)], 3.6),
    "hall":      ([(48, 40), (48, 34), (49, 29)], 3.0),
    "graveyard": ([(36, 41), (30, 35), (25, 30), (24, 27)], 2.4),
    "east":      ([(58, 40), (62, 35), (64, 31)], 2.2),
    "south":     ([(44, 41), (42, 48), (41, 55), (41, 62)], 2.4),
    "market":    ([(68, 42), (71, 49), (73, 55)], 2.2),
}
PLAZA = (48, 40, 9.0, 6.0)          # the square (paved)

_RS = K.RoadSet(ROADS)
road_dist = _RS.dist


def paved(gx, gy):
    cx, cy, rx, ry = PLAZA
    r = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
    return (1 - r) * min(rx, ry)


def cliff_field(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    floor = np.maximum.reduce([
        superlobe(gx, gy, 48.0, 42.0, 43.0, 18.0, 2.8),          # the long street
        superlobe(gx, gy, 49.0, 24.0, 14.0, 12.0, 2.6),          # the Town Hall terrace
        superlobe(gx, gy, 24.0, 24.0, 13.0, 11.0, 2.6),          # the graveyard terrace
        superlobe(gx, gy, 65.0, 31.0, 11.0, 9.0, 2.6),           # apothecary + chapel
        superlobe(gx, gy, 41.0, 61.0, 15.0, 12.0, 2.6),          # the south farm plots
        superlobe(gx, gy, 72.0, 52.0, 12.0, 11.0, 2.6),          # the east market yard
    ])
    floor = floor + 1.8 * wob(gx * 0.5, gy * 0.5) + 0.9 * wob(gx, gy)
    floor = np.maximum(floor, road_dist(gx, gy) + 2.4)
    rock = -floor
    edge = np.minimum.reduce([gx, W - gx, gy, H - gy])
    rock = np.maximum(rock, (3.5 - edge) * 1.2 + 0.3 * wob(gx * 1.3, gy * 1.3))
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    return rock


def fields(gx, gy):
    gx = np.asarray(gx, float)
    return dict(cliff=cliff_field(gx, gy), shallow=np.full(gx.shape, -99.0), deep=np.full(gx.shape, -99.0),
                deck=np.full(gx.shape, -9.0))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


SUBZONES = [
    ("Gallows' End Tavern", 28, 42, 18, 14),
    ("Brill Town Hall", 38, 14, 22, 24),
    ("Brill Graveyard", 8, 10, 32, 24),
]

# ---- baker config (read by tools/bake_tirisfal.py) -------------------------------------------------
BASE = {"meadow": 0.45, "mist": 0.25, "litter": 0.25, "rocky": 0.10}
PAINT = {
    "earth":  [(24, 22, 11, 8, 1.0)],                                     # the graveyard
    "gravel": [(24, 20, 6, 4, 0.5)],
    "field":  [(41, 66, 11, 7, 1.0)],                                     # the south plots
    "cobble": [(49, 29, 8, 5, 1.0), (65, 33, 6, 4, 0.9), (36, 46, 7, 5, 0.9), (73, 50, 6, 4, 0.8)],
}
COBBLE = []

# ---- NPC spots -------------------------------------------------------------------------------------
NPC_POSITIONS = {
    "et_balnir_edric": (46, 33),              # quest hub: Stablehand Edric, Balnir
    "et_gravekeeper_morvyn": (44, 53),        # quest hub: Gravekeeper Morvyn, Faol's Rest
    "wt_solliden_farmer": (55, 43),           # quest hub: Widow Marren, Solliden Farm
    "wt_garren_warden": (50, 46),             # quest hub: Warden Brask, Garren's Haunt
    "wt_coldhearth_watcher": (40, 44),        # quest hub: Watcher Pell, Cold Hearth Manor
    "wt_agamand_envoy": (46, 47),             # quest hub: Envoy Sorren, the Agamand mill
    "brill_deathguard": (46, 44),            # Deathguard Rennick, at the square (quest giver)
    "brill_town_crier": (52, 43),
    "brill_guard": (10, 46),                 # west gate
    "brill_innkeeper": (39, 46),             # Gallows' End Tavern
    "brill_general_goods": (71, 47),         # east market
    "brill_beltelf_trader": (75, 47),
    "brill_butcher": (74, 54),
    "brill_tailor": (30, 47),
    "brill_reagent_dealer": (63, 33),        # beside the apothecary
    "brill_apothecary_asst": (60, 31),
    "brill_bell_ringer": (69, 35),           # at the chapel
    "brill_gravedigger": (25, 27),           # graveyard gate
    "brill_human_sympathizer": (23, 49),
    "brill_farmer": (42, 58),
    "brill_scarecrow_tender": (38, 63),
    "brill_newly_risen_farmhand": (45, 61),
    "brill_forge": (67, 60),                 # the village forge (smelting + blacksmithing) beside the east market
}
CHESTS = [(14, 18), (84, 38), (30, 66), (50, 14)]

FOREST = dict(seed=41, count=30, rim=8, thorn=10, names=[
    ("ek_dead_oak", 6, 0.34), (T.HFP + "dead_pine_cluster.png", 5, 0.40), (T.CIP + "cursed_dead_tree_cluster.png", 4, 0.40)])


def dress(L):
    p, b = L.prop, L.bld
    UF, HF, CI, UC = T.UFP, T.HFP, T.CIP, T.UCP
    # ---- gates
    # No gatehouses here: they were the ORC palisade gatehouse, in a Forsaken town. The exit
    # pass (world/exit_frames.py TOWN) stands Brill's own iron gate over each road out.
    p("ek_forsaken_banner", 11, 41, 5)
    p("ek_forsaken_banner", 85, 41, 5)
    p("ek_signpost", 14, 47, 4)
    p("ek_signpost", 82, 47, 4)
    # ---- the square
    p("ek_dry_fountain", 52, 37, 5, nudge=1)
    p("ek_pillory", 44, 38, 4)
    p("ek_forsaken_banner", 41, 38, 5)
    p("ek_forsaken_banner", 56, 38, 5)
    p("ek_farm_well", 53, 46, 4)
    p("ek_plague_cart", 58, 45, 4)
    for x in (22, 32, 44, 54, 64, 76):
        p(UC + "uc_lantern_post.png", x, 46 if x % 2 == 0 else 39, 5, solid=False)
    # ---- the Town Hall closes the north lane
    b("forsaken_town_hall", 49, 26, 11, solid="core", fraction=0.5, nudge=0)
    p("ek_forsaken_banner", 42, 28, 5)
    p("ek_forsaken_banner", 56, 28, 5)
    p("ek_cross_crows", 41, 22, 4)
    p("ek_gibbet", 58, 22, 6)
    # ---- Gallows' End Tavern: the inn, its gallows, the barrel yard
    b("forsaken_house_medium", 34, 49, 10, nudge=1)
    b("gallows_post", 37, 53, 6, nudge=1)
    p("ek_plague_cauldron", 36, 52, 3)
    p("ek_signpost", 31, 44, 4)
    # ---- the tailor's and the back lane
    b("forsaken_house_small", 24, 56, 8, nudge=1)
    b("forsaken_house_small", 16, 52, 8, nudge=1)
    p("ek_haystack", 29, 54, 4)
    # ---- the graveyard terrace: gate, fence, rows of stones, a mausoleum
    p("ek_cemetery_gate", 24, 31, 5, road_ok=True, allow_overlap=True, nudge=0)
    for x in (18, 30):
        p("ek_cemetery_fence", x, 32, 3, solid=True)
    p(HF + "crypt_mausoleum.png", 24, 15, 9, fraction=0.5)
    for (x, y) in [(15, 20), (20, 24), (30, 20), (33, 25), (16, 27), (28, 28)]:
        p(CI + "worn_tombstone_row.png", x, y, 3)
    p("ek_open_grave", 21, 28, 3)
    p("ek_open_grave", 31, 17, 3)
    p("ek_angel_statue", 26, 21, 6)
    p("ek_cross_crows", 18, 17, 4)
    p("ek_willow", 12, 24, 7)
    # ---- the east lane: apothecary and chapel
    b("forsaken_house_small", 62, 29, 8, nudge=1)
    p(UC + "uc_alchemy_table.png", 59, 34, 3)
    p(UC + "uc_plague_vat.png", 66, 29, 4)
    b("crypt_chapel", 71, 31, 10, nudge=1)
    p(CI + "worn_tombstone_row.png", 76, 36, 3)
    p("ek_scarecrow", 56, 33, 4)
    # ---- the east market yard
    p(UC + "uc_stall_goods.png", 70, 51, 4)
    p(UC + "uc_stall_bottles.png", 76, 50, 4)
    b("forsaken_house_small", 78, 54, 8, nudge=1)
    b("forsaken_house_medium", 62, 54, 9, nudge=1)
    # The smithy was authored at (67,57) with a one-tile nudge, on top of the crates and the
    # medium house, so it was refused and BRILL HAD NO FORGE BUILDING - only the forge tile.
    # It goes in first now, south of the houses and over its tile; the cart moved along.
    b("ek_smithy_forge", 69, 60, 7, nudge=2)                                       # Brill's forge (tile at 67,60)
    p("ek_plague_cart", 76, 59, 4)
    p("ek_signpost", 72, 46, 4)
    # ---- the south plots
    for (x, y) in [(36, 60), (46, 64), (40, 68)]:
        p("ek_haystack", x, y, 4)
    for (x, y) in [(37, 62), (44, 66)]:
        p("ek_scarecrow", x, y, 4)
    p(UF + "scarecrow.png", 34, 66, 4)
    for x in (34, 38, 42, 46, 50):
        p("ek_farm_fence", x, 71, 3, solid=True)
    p("ek_farm_cart", 48, 58, 4)
    p(HF + "burned_house_ruin.png", 33, 58, 7)
    p("ek_signpost", 43, 52, 4)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_brill():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/brill_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
