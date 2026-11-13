"""
Hand-built Tarren Mill (96x88): the Forsaken-held mill village in the Hillsbrad lowlands, levels 20-26.

TOWN ARCHETYPE: THE MILLRACE, TWO BANKS.  A diverted channel runs the length of the town from the weir in the north
down to the wheel that drives the mill, and it cuts the place in half.  The WEST BANK is the human village the
Forsaken took - inn, cottages, barn, smithy, stable, chapel, the mill and its granary, all still doing the work they
were built for.  The EAST BANK is what the Royal Apothecary Society put up on the floodplain afterwards: the
apothecarium, the vat platform, the tents and the watchtower.  Three footbridges join them and nothing else does.
The water IS the layout, and both halves want you to use the bridge rather than live on the other side.

(Brill is a high street, Crossroads a plus-shaped avenue, the Sepulcher a terraced crypt-keep, Ratchet a crescent
harbour, Camp Taurajo a ring camp, Splintertree a stockade, Razor Hill a walled hilltop.  Astranaar is the only other
town built around water, and that is a POOL the town sits around - a still centrepiece you walk past.  This is a
CHANNEL that runs through and divides, and the difference is the point: Astranaar's water is scenery, this water is
a wall.  Hence the hard contract below.)

HARD CONTRACT - THE RACE IS A BARRIER.  The channel is DEEP water end to end (deep_water is walkable=False;
shallow would let you wade and the archetype would be decoration).  The three bridges are `deck` tiles, which
kind_from_fields resolves LAST and so paints plank over deep.  tools/verify_tarren_mill.py removes the bridges and
asserts the banks fall apart - a layout whose idea is "X is the only way across" has to fail when X is taken away,
which is the lesson Azurelode and Durnholde both taught the hard way.

    south gate (44,83) <- Eastern Hillsbrad's mill square
      |
    WEST BANK (the village)   ||| race |||   EAST BANK (the apothecarium)
      inn, cottages, smithy,   bridges at    apothecarium, vat platform,
      stable, barn, chapel,    y=70, 48, 24  tents, watchtower, boarded
      the mill + granary                     houses

HARD CONTRACTS (world/portal_manager.py): portal (44,83) <-> Eastern Hillsbrad (62,32); arrival 4 tiles inside.
Prop rule (Kyle): less is more; logical for the room; a few centrepieces.
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob, superlobe, seg_dist

KEY = "tarren_mill"
NAME = "Tarren Mill"
DESC = "Tarren Mill. A Lordaeron mill village held by the Forsaken: the old town on one bank, the apothecaries on the other."
REGION = "Eastern Kingdoms - Lordaeron"
W, H = 96, 88
BAKED_DIR = "assets/tiles/tarren_mill/baked"
IS_TOWN = True
BASE_TILE = "grass"
SEED = 733

PORTALS = {(34, 84): "Eastern Hillsbrad"}
ARRIVALS = [(34, 80)]
START = (34, 79)

#: The race, north weir to southern outfall. A millrace is a CUT channel, not a river, so it is near-straight with
#: one slow bend around the wheel rather than a meander.
RACE = [(49.0, 4.0), (49.0, 20.0), (48.0, 36.0), (47.0, 52.0), (47.0, 68.0), (46.0, 88.0)]
RACE_HALF = 3.1                       # ~6 tiles bank to bank: too wide to be a ditch, narrow enough to bridge

#: Bridges: (x0, x1, y0, y1) plank decks laid over the race. These are the ONLY crossings.
BRIDGES = [(42.0, 56.0, 23.0, 25.4),      # the weir walk, by the sluice
           (41.0, 55.0, 47.0, 49.4),      # the market bridge, off the mill square
           (40.0, 54.0, 69.0, 71.4)]      # the gate bridge, first thing you meet coming in

ROADS = {
    # the west bank's street: the gate, up past the square and the mill, on to the north cottages
    "high":   ([(34, 85), (33, 74), (33, 64), (34, 50), (32, 36), (33, 20), (35, 10)], 3.2),
    # the east bank's track, shorter and meaner - the Society only ever needed to get between its own sheds
    "east":   ([(60, 76), (62, 62), (61, 48), (63, 34), (62, 20)], 2.6),
    # the three bridge approaches
    "br_s":   ([(38, 70), (58, 70)], 2.4),
    "br_m":   ([(37, 48), (57, 48)], 2.4),
    "br_n":   ([(39, 24), (57, 24)], 2.2),
}
PLAZA = (34, 50, 9.0, 6.0)            # the mill square, west bank
YARD = (62, 58, 7.0, 5.0)             # the apothecary's working yard, east bank

_RS = K.RoadSet(ROADS)
road_dist = _RS.dist


def paved(gx, gy):
    out = -9.0
    for cx, cy, rx, ry in (PLAZA, YARD):
        r = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
        out = np.maximum(out, (1 - r) * min(rx, ry))
    return out


def _race(gx, gy):
    """Tile distance INSIDE the race (>0 is water)."""
    d = np.full(np.shape(gx), 1e9)
    for i in range(len(RACE) - 1):
        (x0, y0), (x1, y1) = RACE[i], RACE[i + 1]
        d = np.minimum(d, seg_dist(gx, gy, x0, y0, x1, y1))
    # A cut channel has straight banks; only a whisper of wobble so it does not read as ruled with a pen.
    return (RACE_HALF - d) + 0.22 * wob(gx * 1.6, gy * 1.6)


def deck_field(gx, gy):
    out = np.full(np.shape(gx), -9.0)
    for (x0, x1, y0, y1) in BRIDGES:
        inside = np.minimum(np.minimum(gx - x0, x1 - gx), np.minimum(gy - y0, y1 - gy))
        out = np.maximum(out, inside)
    return out


def cliff_field(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    # The valley floor the town sits on; everything outside it is the rising ground that seals the map.
    floor = np.maximum.reduce([
        superlobe(gx, gy, 32.0, 48.0, 30.0, 40.0, 2.8),        # the west bank
        superlobe(gx, gy, 64.0, 48.0, 28.0, 38.0, 2.8),        # the east bank
        superlobe(gx, gy, 48.0, 44.0, 16.0, 44.0, 3.0),        # the channel's own corridor
    ])
    floor = floor + 1.4 * wob(gx * 0.5, gy * 0.5) + 0.7 * wob(gx, gy)
    floor = np.maximum(floor, road_dist(gx, gy) + 2.4)
    rock = -floor
    edge = np.minimum.reduce([gx, W - gx, gy, H - gy])
    rock = np.maximum(rock, (3.5 - edge) * 1.2 + 0.3 * wob(gx * 1.3, gy * 1.3))
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    # Rock never eats the race or a bridge: a channel blocked by a boulder is a channel with a ford in it.
    rock = np.where(_race(gx, gy) > -1.0, np.minimum(rock, -0.5), rock)
    return rock


def fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    race = _race(gx, gy)
    return dict(cliff=cliff_field(gx, gy),
                # The whole channel is DEEP. There is no shallow margin, deliberately: a wadeable edge would let
                # the player cross anywhere and the two banks would stop being two banks.
                shallow=np.full(gx.shape, -99.0),
                deep=race,
                deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


SUBZONES = [
    ("The Mill Yard", 22, 38, 30, 24),
    ("The Apothecarium", 52, 36, 36, 30),
    ("The Weir", 36, 6, 28, 20),
    ("Mill Row", 16, 62, 32, 22),
]

# ---- baker config (read by tools/bake_hillsbrad.py) -----------------------------------------------------------
BASE = {"grass": 0.66, "forest": 0.14, "fern": 0.12, "rocky": 0.14}
PAINT = {
    "field":  [(20, 24, 11, 8, 0.9), (22, 72, 10, 7, 0.9)],          # the village's own plots
    "earth":  [(34, 50, 7, 5, 0.8), (62, 58, 6, 4, 0.9), (64, 40, 7, 5, 0.8)],
    "meadow": [(26, 58, 10, 7, 0.8), (76, 70, 10, 7, 0.7)],
    "marsh":  [(47, 80, 6, 7, 0.8), (49, 12, 5, 6, 0.7)],            # where the race leaks into its banks
    "rocky":  [(8, 44, 7, 14, 0.7), (88, 44, 7, 14, 0.7)],
    "gravel": [(44, 80, 6, 4, 0.7), (62, 24, 5, 4, 0.6)],
    "forest": [(14, 16, 10, 8, 0.7), (82, 18, 9, 7, 0.7), (80, 80, 9, 6, 0.6)],
}
COBBLE = [(34, 50, 9, 6, 0.95), (62, 58, 7, 5, 0.8)]

# ---- NPC spots ------------------------------------------------------------------------------------------------
#: West bank = the living town (innkeeper, smith, trader, stablemaster). East bank = the Society (apothecaries,
#: the commander). Written into data/npcs/*.json by tools/sync_hillsbrad_npcs.py.
NPC_POSITIONS = {
    # --- the gate and Mill Row (west bank, south)
    "tarren_mill_gate_guard": (42, 77),
    "tarren_mill_innkeeper": (26, 68),
    "tarren_mill_stablemaster": (20, 74),
    "tarren_mill_farrier": (31, 72),
    # --- the mill square (west bank, middle)
    "tarren_mill_miller": (37, 60),
    "tarren_mill_trader": (30, 47),
    "tarren_mill_smith": (24, 52),
    "tarren_mill_reagent_seller": (37, 45),
    "tarren_mill_bowyer": (27, 40),
    # --- the north cottages and the weir (west bank, north)
    "tarren_mill_chaplain": (30, 26),
    "tarren_mill_sluice_keeper": (40, 18),
    "tarren_mill_farmhand": (22, 30),
    # --- the apothecarium (east bank)
    "tarren_mill_apothecary": (64, 55),
    "tarren_mill_apprentice": (68, 60),
    "tarren_mill_vat_tender": (72, 46),
    "tarren_mill_commander": (62, 36),
    "tarren_mill_scout": (70, 30),
    "tarren_mill_watchman": (58, 71),
}
CHESTS = [(12, 36), (86, 36), (18, 82), (84, 76)]

FOREST = dict(seed=73, count=26, rim=7, thorn=12, names=[
    ("ek_willow", 6, 0.34), ("ek_pine_trio", 7, 0.40), ("ek_pine_tall", 8, 0.34)])


def dress(L):
    p, b = L.prop, L.bld
    # ================= THE RACE ITSELF: the one thing the town is built around ==============================
    # The mill straddles the west bank at the wheel - its own art carries the wheel and the water splash, so it
    # is placed hard against the channel rather than set back with the rest of the street.
    # The mill is the one building the town is NAMED for, and at 7 tiles it came out the same size as a
    # watchtower and read as just another shed. It is the landmark, so it gets the height and the elbow room,
    # with the wheel sitting out over the channel where the art already puts its own water.
    b("ek_watermill", 41, 57, 10, nudge=1)
    b("ek_granary", 28, 65, 6, nudge=1)
    b("ek_millstone_shelter", 31, 59, 5, nudge=1)
    b("ek_mill_sluice", 44, 15, 6, nudge=0)                        # the weir that feeds the race
    p("ek_signpost", 36, 81, 4)

    # ================= WEST BANK: the village the Forsaken took ==============================================
    # ---- Mill Row (south): the inn, the stable, the plots
    b("ek_village_inn", 26, 65, 7, nudge=1)
    b("ek_stable_block", 19, 71, 5, nudge=1)
    b("ek_barn", 16, 62, 6, nudge=1)
    b("ek_cottage_small", 28, 76, 5, nudge=1)
    b("ek_cottage_medium", 24, 80, 5, nudge=1)
    p("ek_haystack", 21, 78, 3)
    p("ek_farm_cart", 30, 69, 3)
    p("ek_farm_fence", 17, 80, 2, solid=False)
    p("ek_farm_fence", 27, 83, 2, solid=False)
    # ---- the mill square (middle): the trading floor of the place
    b("ek_trading_post", 29, 45, 6, nudge=1)
    b("ek_smithy_forge", 22, 50, 6, nudge=1)
    p("ek_farm_well", 34, 51, 4, road_ok=True)
    p("ek_signpost", 37, 48, 4, road_ok=True)
    p("ek_forsaken_banner", 31, 54, 5)
    p("ek_forsaken_banner", 39, 49, 5)
    # ---- the north cottages and the chapel
    b("ek_townhouse", 27, 38, 6, nudge=1)
    b("ek_village_chapel", 29, 23, 6, nudge=1)
    b("ek_cottage_small", 20, 34, 5, nudge=1)
    b("ek_cottage_medium", 23, 18, 5, nudge=1)
    p("ek_scarecrow", 18, 26, 4)
    p("ek_haystack", 36, 32, 3)
    p("ek_farm_fence", 15, 22, 2, solid=False)

    # ================= EAST BANK: what the Royal Apothecary Society built ====================================
    # ---- the apothecarium and its working yard
    b("ek_apothecarium", 66, 52, 7, nudge=1)
    b("ek_plague_vat_platform", 74, 44, 6, nudge=1)
    p("ek_plague_cauldron", 61, 56, 3)
    p("ek_plague_cauldron", 66, 61, 3)
    p("ek_plague_cart", 70, 63, 3)
    p("ek_forsaken_banner", 58, 54, 5)
    # ---- the camp: the Society travels with its own guard and does not use the village's beds
    b("ek_forsaken_field_tent", 60, 38, 5, nudge=1)
    b("ek_forsaken_field_tent", 69, 34, 5, nudge=1)
    b("ek_forsaken_watchtower", 55, 65, 7, nudge=1)
    b("ek_forsaken_watchtower", 66, 22, 7, nudge=1)
    p("ek_forsaken_banner", 66, 31, 5)
    p("ek_cross_crows", 75, 36, 4)
    # ---- the boarded end: the townsfolk who lived this side were moved on
    b("ek_syndicate_house", 78, 60, 6, nudge=1)
    b("ek_burnt_cottage", 76, 72, 5, nudge=1)
    p("ek_open_grave", 80, 66, 3)
    p("ek_pillory", 72, 68, 4)
    p("ek_gibbet", 82, 54, 6)
    # ---- the wayshrine at the far track, the last human thing on this bank
    b("ek_wayshrine", 72, 24, 5, nudge=1)
    p("ek_thorn_bush", 76, 28, 2, solid=False)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_tarren_mill():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/tarren_mill_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
