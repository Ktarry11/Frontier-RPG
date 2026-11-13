"""
Hand-built Hammerfall (104x88): the orc-and-Forsaken garrison holding the Arathi basin, levels 33-37.

TOWN ARCHETYPE: THE STOCKADE, FOUR QUARTERS ROUND A MUSTER.  One gate in the south wall, one road straight up
from it to the war hall on the high end, and a muster yard halfway where that road crosses the cross-lane.  The
four quarters hang off that crossing and each one is a different trade: WAR YARD west (forge, armoury, siege
work), MARKET ROW east (quartermaster, store, reagents, the roost beyond it), the FORSAKEN QUARTER north-west
(apothecary, deathguard post - orcs took the ground, the Forsaken moved in beside them), and the YARDS
south-east and south-west (inn and mess, then tannery, smokehouse, timber).

(Brill is a high street, Crossroads a plus-shaped avenue, Tarren Mill two banks of a millrace, Razor Hill a
walled hilltop, Splintertree a palisade war yard.  This is the only STOCKADE WITH QUARTERS: a square hold whose
inside is divided by what gets done where, not by terrain.  Razor Hill is the near miss and the difference is
that its wall follows a hill - this wall is built on flat basin floor and encloses because somebody built it.)

WHY IT IS ITS OWN ZONE.  Kyle, 7 Nov: "the towns are just open and not stand alone towns. We need to fix this."
Hammerfall was nine-odd props scattered on the open moor inside Arathi Central, with nineteen NPCs standing in
a 34x31 box of it - no wall, no gate, nothing that made it a place you enter.  The design record already called
it "full town - inn, war forge, wind rider roost, apothecary, shops, stables"; it just was not built as one.

HARD CONTRACT - THE WALL IS THE EDGE.  Everything outside the stockade floor is cliff (walkable=False), so the
only way in or out is the south gate portal.  tools/verify_hammerfall.py asserts that: it removes the gate tile
and checks the town has no route to the map edge.  A hold whose idea is "one way in" has to fail when the one
way is taken away - the lesson Tarren Mill's bridges and Azurelode both taught.

    north:  WAR HALL (Gath'rok) + totem court
             |
    FORSAKEN QUARTER  --  MUSTER YARD  --  STABLES / ROOST
    (apothecary,          (sergeant,        (Rukka, Dreka)
     deathguard)           trainer)
             |                  |
    WAR YARD west  ----  MAIN ROAD  ----  MARKET ROW east
    (forge, armoury)          |           (quartermaster, store, reagents)
             |                |                   |
    TANNERY / SMOKEHOUSE   SOUTH GATE          INN / MESS
                           -> Arathi Central

HARD CONTRACTS (world/portal_manager.py): portal (52,85) <-> Arathi Central (138,62); arrival 3 tiles inside.
Prop rule (Kyle): less is more; logical for the room; a few centrepieces.
NPC ids are the ones already in data/npcs/*.json - this module MOVES them, it does not invent any.
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob, superlobe

KEY = "hammerfall"
NAME = "Hammerfall"
DESC = "Hammerfall. An orc garrison in a stolen human hold, with the Forsaken camped in beside it."
REGION = "Eastern Kingdoms - Arathi Highlands"
W, H = 104, 88
BAKED_DIR = "assets/tiles/hammerfall/baked"
IS_TOWN = True
BASE_TILE = "grass"

PORTALS = {(52, 85): "Arathi Central"}
ARRIVALS = [(52, 82)]
START = (52, 80)

ROADS = {
    # The spine: gate -> muster -> war hall. Every other lane hangs off it.
    "spine":   ([(52, 86), (52, 74), (52, 62), (52, 48), (52, 34), (52, 26)], 3.8),
    # The cross-lane through the muster yard, west into the war yard and east into the market.
    "cross":   ([(18, 54), (32, 55), (44, 55), (52, 55), (62, 55), (76, 56), (88, 57)], 3.4),
    # Up the north-west into the Forsaken quarter.
    "forsaken": ([(44, 48), (36, 40), (30, 33), (26, 28)], 2.6),
    # Up the north-east to the stables and the wind rider roost.
    "roost":   ([(60, 47), (70, 40), (80, 34), (88, 31)], 2.6),
    # Down the south-east to the inn and mess hall.
    "inn":     ([(60, 62), (68, 68), (74, 73)], 2.6),
    # Down the south-west to the tannery and smokehouse yards.
    "yards":   ([(44, 62), (36, 68), (28, 73)], 2.6),
}
PLAZA = (52, 55, 11.0, 7.5)          # the muster yard (packed earth, reads as paving)

_RS = K.RoadSet(ROADS)
road_dist = _RS.dist


def paved(gx, gy):
    cx, cy, rx, ry = PLAZA
    r = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
    return (1 - r) * min(rx, ry)


def cliff_field(gx, gy):
    """Rock everywhere the hold is not.

    The enclosure IS this function - not the stockade sprites, which are only the
    picture of it. Everything outside the quarter lobes and the roads is cliff, and
    the map rim is forced to cliff hard, so there is no walking out the back of the
    town past a gap between two wall sprites. That gap is how Refuge Pointe reads as
    open moor today.
    """
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    floor = np.maximum.reduce([
        superlobe(gx, gy, 52.0, 55.0, 17.0, 12.0, 2.8),          # the muster yard
        superlobe(gx, gy, 52.0, 30.0, 16.0, 11.0, 2.6),          # war hall terrace + totem court
        superlobe(gx, gy, 27.0, 31.0, 13.0, 11.0, 2.6),          # the Forsaken quarter
        superlobe(gx, gy, 26.0, 56.0, 13.0, 10.0, 2.6),          # the war yard
        superlobe(gx, gy, 81.0, 57.0, 14.0, 10.0, 2.6),          # market row
        superlobe(gx, gy, 85.0, 31.0, 12.0, 10.0, 2.6),          # stables and the roost
        superlobe(gx, gy, 73.0, 73.0, 12.0, 10.0, 2.6),          # inn and mess yard
        superlobe(gx, gy, 28.0, 73.0, 12.0, 10.0, 2.6),          # tannery and smokehouse yard
        superlobe(gx, gy, 52.0, 78.0, 10.0, 8.0, 2.6),           # inside the gate
    ])
    floor = floor + 1.8 * wob(gx * 0.5, gy * 0.5) + 0.9 * wob(gx, gy)
    floor = np.maximum(floor, road_dist(gx, gy) + 2.4)
    rock = -floor
    edge = np.minimum.reduce([gx, W - gx, gy, H - gy])
    rock = np.maximum(rock, (4.0 - edge) * 1.4 + 0.3 * wob(gx * 1.3, gy * 1.3))
    # The gate column is the ONE hole in the rim, and it is cut after the rim is
    # forced, so the ordering cannot be got wrong by a later edit.
    gate = (np.abs(gx - 52.0) < 3.0) & (gy > H - 8)
    rock = np.where(gate, -1.0, rock)
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    return rock


def fields(gx, gy):
    gx = np.asarray(gx, float)
    return dict(cliff=cliff_field(gx, gy), shallow=np.full(gx.shape, -99.0),
                deep=np.full(gx.shape, -99.0), deck=np.full(gx.shape, -9.0))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


SUBZONES = [
    ("The Muster Yard", 40, 46, 26, 19),
    ("The War Hall", 40, 20, 26, 20),
    ("The Forsaken Quarter", 14, 20, 28, 22),
    ("Hammerfall War Yard", 12, 46, 28, 20),
    ("Hammerfall Market Row", 66, 46, 32, 22),
    ("The Wind Rider Roost", 72, 20, 28, 22),
]

# ---- baker config (read by tools/bake_hillsbrad.py) ------------------------------------------------
# Drier and rockier than Arathi Central's open basin: this is a trampled garrison floor, not moor.
BASE = {"dry": 0.46, "grass": 0.22, "rocky": 0.24, "earth": 0.08}
PAINT = {
    "earth":  [(52, 55, 14, 9, 1.0), (52, 30, 11, 7, 0.9), (26, 56, 9, 6, 0.85), (85, 31, 8, 6, 0.8)],
    "gravel": [(52, 78, 8, 5, 0.8), (52, 44, 6, 4, 0.6), (81, 57, 8, 5, 0.6)],
    "field":  [(28, 73, 9, 6, 0.8), (73, 73, 9, 6, 0.7)],
    "rocky":  [(16, 34, 9, 7, 0.8), (92, 44, 8, 6, 0.8), (16, 68, 7, 5, 0.7), (92, 70, 7, 5, 0.7)],
    "cobble": [(52, 55, 7, 5, 0.9)],
}
COBBLE = []

# ---- NPC spots ---------------------------------------------------------------------------------
# NINETEEN NPCs OVER 104x88, one per quarter's business, instead of nineteen in a 34x31 box.
# Kyle, 7 Nov: "Ensure NPCs, vendors, trainers are spaced out. Don't cram everything to a tiny
# corner." The rule used below: nobody stands more than a few tiles off a road (so they are found
# by walking, not by sweeping the grass), and no two share a quarter's doorway.
NPC_POSITIONS = {
    # the spine, north to south
    "hammerfall_commander":        (52, 29),   # Overlord Gath'rok, outside the war hall
    "hammerfall_tauren_envoy":     (45, 24),   # High Envoy Tamka Stillwater, at the totem court
    "hammerfall_tauren_herbalist": (58, 25),   # Herbalist Nahto Greenhoof, the other side of it
    "ct_hammerfall":               (46, 50),   # Trainer Naruk - class trainer, on the muster yard
    "hammerfall_sergeant":         (57, 59),   # Sergeant Mok Blackstone, drilling on the yard
    # the Forsaken quarter, north-west
    "hammerfall_apothecary":       (25, 29),   # Apothecary Dellwyn Voss
    "hammerfall_deathguard":       (31, 35),   # Deathguard Olen, on the lane in
    "pt_hammerfall_herbs":         (20, 34),   # Apothecary Vashka - herbalism
    # the war yard, west
    "hammerfall_weaponsmith":      (27, 53),   # Weaponsmith Krol Anvilbrand, at the war forge
    "pt_hammerfall_forge":         (21, 58),   # Forge Grokk - blacksmithing
    "pt_hammerfall_essence":       (33, 60),   # Tinker Grokk - enchanting, by the armoury
    # market row, east
    "hammerfall_quartermaster":    (72, 54),   # Quartermaster Urga Ironhand
    "hammerfall_general_goods":    (82, 58),   # Trader Molg
    "hammerfall_reagent_vendor":   (89, 54),   # Reagent-Keeper Shelna
    # stables and roost, north-east
    "hammerfall_stablemaster":     (80, 34),   # Stablemaster Rukka
    "hammerfall_windrider_master": (89, 28),   # Wind Rider Master Dreka, at the roost
    # the yards, south
    "hammerfall_innkeeper":        (74, 71),   # Innkeeper Grettha
    "pt_hammerfall_hide":          (25, 72),   # Tanner Rokan - leatherworking
    "pt_hammerfall_wood":          (33, 76),   # Woodwright Naruk - the timber yard
}
CHESTS = [(16, 24), (94, 24), (18, 78), (96, 74)]

# Sparse: this is a stockade on basin floor, so the only greenery is what grows against the wall.
FOREST = dict(seed=51, count=22, rim=6, thorn=11, names=[
    ("ek_thorn_bush", 4, 0.42), ("ek_dead_oak", 6, 0.30), ("ek_pine_trio", 7, 0.26)])


def dress(L):
    p, b = L.prop, L.bld

    # ---- THE WALL. Stockade sections right round the rim, broken only at the gate. These are the
    # picture of the enclosure; cliff_field is the enclosure itself.
    for x in range(10, 96, 6):
        if abs(x - 52) > 6:
            b("orc_stockade_section", x, 84, 6, solid=True, nudge=0)
            b("orc_stockade_section", x, 12, 6, solid=True, nudge=0)
    for y in range(18, 82, 6):
        b("orc_stockade_section", 10, y, 6, solid=True, nudge=0)
        b("orc_stockade_section", 96, y, 6, solid=True, nudge=0)
    b("orc_great_gatehouse", 52, 83, 12, solid=False, road_ok=True, nudge=0)
    b("orc_watch_tower", 40, 82, 11)
    b("orc_watch_tower", 64, 82, 11)
    b("orc_watch_tower", 12, 18, 11)
    b("orc_watch_tower", 94, 18, 11)
    b("orc_signal_beacon", 52, 16, 7, nudge=2)

    # ---- the spine and the muster yard
    b("orc_war_hall", 52, 26, 16, nudge=2)
    b("orc_warchief_lodge", 64, 30, 12, nudge=2)
    b("orc_totem_court", 44, 22, 10, nudge=2)
    b("orc_great_totem", 52, 40, 8, nudge=2)
    p("ek_signpost", 52, 66, 4)
    p("ek_forsaken_banner", 46, 60, 6)
    p("ek_forsaken_banner", 58, 60, 6)

    # ---- the Forsaken quarter: orc timber, Forsaken tenants
    b("orc_forsaken_apothecary", 24, 27, 11, nudge=2)
    b("orc_deathguard_post", 32, 32, 10, nudge=2)
    b("orc_spirit_lodge", 18, 36, 10, nudge=2)
    p("ek_plague_cart", 29, 24, 4)

    # ---- the war yard
    b("orc_war_forge", 26, 50, 12, nudge=2)
    b("orc_armoury", 34, 58, 10, nudge=2)
    b("orc_siege_workshop", 17, 56, 11, nudge=2)
    p("ek_scarlet_crates", 31, 52, 4)
    p("ek_farm_cart", 22, 61, 4)

    # ---- market row
    b("orc_quartermaster_post", 71, 51, 10, nudge=2)
    b("orc_supply_store", 83, 55, 10, nudge=2)
    b("orc_brew_house", 91, 60, 10, nudge=2)
    p("ek_scarlet_crates", 77, 57, 4)
    p("ek_scarlet_crates", 87, 50, 4)

    # ---- stables and the roost
    b("orc_warbeast_stable", 79, 31, 11, nudge=2)
    b("orc_kennel_block", 90, 36, 9, nudge=2)
    b("orc_great_totem", 90, 25, 7, nudge=2)

    # ---- the inn and mess yard
    b("orc_mess_hall", 72, 70, 11, nudge=2)
    b("orc_officers_house", 82, 74, 9, nudge=2)
    p("ek_farm_well", 66, 72, 4)

    # ---- the tannery and smokehouse yard
    b("orc_tannery_hall", 24, 70, 11, nudge=2)
    b("orc_smokehouse", 34, 75, 9, nudge=2)
    b("orc_bone_yard_shed", 16, 76, 9, nudge=2)
    p("ek_haystack", 29, 67, 4)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_hammerfall():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/hammerfall_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
