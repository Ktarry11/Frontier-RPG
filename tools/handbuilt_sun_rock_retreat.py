"""
Hand-built Sun Rock Retreat (100x84): Stonetalon's town, on top of its rock (docs/stonetalon_brief.md).

Kyle, 15 Nov 2026: Sun Rock is the town, "Sun Rock tauren", and its quest givers pay "Thunder bluff, steamwheedle,
and orgrimmar. Maybe one or two forsaken" (all of them in Sun Rock, with one small camp out in the West).

Thunder Bluff fell in the Integration and the tauren were taken in elsewhere. Sun Rock was always a small hold;
it's bigger now, because it's the closest high ground to Mulgore that isn't in Mulgore. So the town is two
things at once, and the layout shows it:

    the gate ............ west (3,46): the path up from the junction below
    the bonfire ......... centre: the plaza, red stone, the bonfire pavilion
    the elders .......... north: the great lodge and the spirit lodge, Sun Rock as it always was
    the refugees ........ north-east: tents, a food cache, what people carried out of Mulgore
    the inn and roost ... west, by the gate
    the work row ........ south: smithy, tannery, herb hut, carver: the trainers in their themed pairs
    the envoys .......... east: Orgrimmar's war tent, the Steamwheedle agent's shop, the Forsaken field tent
    the two watches ..... north-east over the Blowdown, and south-east over the Mulgore Rim

The town engine (tools/ashenvale_town_kit.py) paints the ground from the Stonetalon sheet (SHEET, the Aspen
materials until Kyle's tiles land): red earth and red stone on the top, and past the edge of the top the ground
falls away as ROCK (EDGE), not woods. Every building is the tauren set.

HARD CONTRACTS (world/portal_manager.py)
  portal   (3,46) -> Stonetalon East (144,93);  arrival (5,46)
  NPC ids  sr_*, ct_sun_rock, pt_sun_rock_*, written by tools/sync_sun_rock_npcs.py from NPC_POSITIONS
"""
import sys

from tools import ashenvale_town_kit as AK

KEY = "sun_rock_retreat"
NAME = "Sun Rock Retreat"
DESC = "A tauren hold on its rock above the Blowdown, bigger since Thunder Bluff fell. The closest high ground to Mulgore."
REGION = "Kalimdor - Stonetalon"
W, H = 100, 84
BAKED_DIR = "assets/tiles/stonetalon/baked_sun_rock"
SHEET = "stonetalon_east"
EDGE = "rock"
PORTALS = {(3, 46): "Stonetalon East"}
ARRIVALS = [(5, 46)]
START = (8, 46)

ROADS = {
    "gate":   ([(2, 46), (14, 46), (28, 45), (40, 44)], 4.0),
    "north":  ([(50, 36), (50, 31)], 3.4),
    "south":  ([(50, 52), (50, 60), (50, 66)], 3.4),
    "east":   ([(60, 44), (72, 46), (84, 48)], 3.2),
    "ne":     ([(58, 38), (66, 32), (74, 28), (84, 26)], 2.6),
    "se":     ([(58, 50), (68, 58), (80, 66), (86, 70)], 2.6),
    "inn":    ([(20, 46), (20, 40)], 2.6),
    "roost":  ([(20, 46), (20, 54)], 2.6),
    "work":   ([(36, 62), (50, 62), (64, 62), (76, 60)], 2.6),
}
STREAMS = {}
POOLS = [(30, 26, 3.5, 2.6, 1.6)]            # the spring the hold was built on
PLAZA = (50, 44, 11.0, 8.0)
PAVED_PATCHES = [(50, 29, 6, 3), (6, 46, 4, 3.5)]
CLEARINGS = [(50, 44, 44, 34), (24, 46, 16, 22), (78, 34, 16, 14), (78, 66, 18, 13), (6, 46, 8, 8),
             (50, 20, 22, 10), (30, 26, 9, 7)]
ROCKS = [(92, 12, 5, 4), (8, 10, 6, 5), (92, 80, 6, 4)]
DECKS = []
CLEARING_GRASS = False
DECK_PAINT = False
GRADE = (1.0, 1.05)

NPC_POSITIONS = {
    # the hold's own
    "sr_elder":             (50, 32),    # Elder Muhana Windhoof - the great lodge's door
    "sr_spirit_walker":     (34, 30),    # by the spirit lodge
    "sr_watch_captain":     (84, 34),    # the north-east watch, over the Blowdown
    "sr_rim_watcher":       (82, 74),    # the south-east watch, over the Mulgore Rim
    # the refugees
    "sr_refugee_mother":    (66, 26),
    "sr_refugee_hunter":    (74, 34),
    # the envoys
    "sr_orgrimmar_envoy":   (82, 52),
    "sr_steamwheedle_agent": (68, 54),
    "sr_forsaken_apothecary": (90, 62),
    # a transplant who came for the mountain
    "sr_transplant_geologist": (60, 34),
    # services
    "sr_innkeeper":         (22, 40),
    "sr_flight_master":     (24, 58),
    "sr_trader":            (34, 52),    # general goods
    "sr_armsmith":          (38, 66),    # tauren arms and armour
    "sr_provisioner":       (62, 50),    # food and drink
    # trainers: one class trainer for every class, and the trades in their themed pairs
    "ct_sun_rock":          (44, 52),
    "pt_sun_rock_forge":    (32, 66),
    "pt_sun_rock_hide":     (46, 70),
    "pt_sun_rock_herbs":    (62, 68),
    "pt_sun_rock_wood":     (76, 64),
}
CHESTS = [(92, 22), (10, 22)]


def dress(L):
    A, B, F, V = L.p, L.b, L.f, L.v
    # ---- the gate: the path up from below
    B("tau_gate_arch", 10, 50, 8, road_ok=True, solid=False)
    A("tau_totem_carved", 12, 40, 5)
    # ---- the bonfire
    B("tau_bonfire_pavilion", 50, 48, 9, road_ok=True, nudge=1)
    # ---- north: the elders
    B("tau_great_lodge", 50, 24, 13, nudge=1)
    B("tau_spirit_lodge", 36, 26, 11)
    A("tau_totem_pole", 42, 34, 7)
    A("tau_totem_pole", 58, 34, 7)
    A("tau_water_trough", 30, 32, 3)
    # ---- north-east: the refugees from Mulgore
    B("tau_tent_large", 68, 22, 9)
    B("tau_tent_medium", 78, 26, 8)
    B("tau_tent_small", 62, 30, 6)
    A("tau_food_cache", 72, 30, 4)
    A("tau_cook_fire", 70, 36, 3)
    A("tau_drying_rack", 80, 36, 3)
    # ---- west: the inn and the roost
    B("tau_hearth_lodge", 18, 36, 11)
    B("orc_wyvern_roost", 16, 62, 12)
    A("tau_hitching_post", 26, 50, 3)
    # ---- general goods by the plaza
    B("tau_trading_post", 32, 48, 9)
    # ---- south: the work row
    B("tau_smithy", 30, 72, 10)
    B("tau_tannery", 46, 76, 10)
    B("tau_herb_hut", 62, 76, 9)
    B("tau_carver_shop", 76, 72, 9)
    A("tau_timber_stack", 84, 62, 3)
    A("tau_kiln", 22, 70, 4)
    # ---- east: the envoys
    B("command_war_tent", 84, 46, 8)              # Orgrimmar
    B("sw_trade_shop", 70, 50, 8)                 # the Steamwheedle agent
    B("ek_forsaken_field_tent", 92, 58, 7)        # the Forsaken
    B("tau_storehouse", 60, 56, 7)                # the provisioner
    # ---- the two watches
    B("tau_watchtower", 90, 30, 13)               # over the Blowdown
    B("tau_watchtower", 92, 70, 13)               # over the Mulgore Rim
    A("tau_totem_carved", 82, 78, 5)


AK.install(sys.modules[__name__])
