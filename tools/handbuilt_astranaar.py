"""
Hand-built Astranaar (110x90): the night elf forward base in Ashenvale.

TOWN ARCHETYPE: MOON-POOL TERRACE TOWN.  A bowl of clear forest inside dense woods.  The living-tree gate stands at
the south; the road climbs to a paved plaza built around a still moon pool; a second road keeps climbing to the
Sentinel hall on the north terrace.  A stream runs down the west side (two footbridges) into a pond; the Sentinels'
tower, camp and drill pavilion sit on the far bank.  East: the inn, houses, the hippogryph perch; south-east: the
druid grove and the forge.  (Razor Hill = hill fort, Crossroads = avenue cross, Taurajo = tipi ring, Ratchet =
harbour; Astranaar is the only town built around water and trees.)

HARD CONTRACTS (world/portal_manager.py)
  portal   (55,85) -> Ashenvale West (110,160);  arrival (55,83)
  NPC ids  referenced by data/quests/ashenvale.json; positions are written back by tools/sync_ashenvale_town_npcs.py
"""
import sys

from tools import ashenvale_town_kit as AK

KEY = "astranaar"
NAME = "Astranaar"
DESC = "Ancient night elf settlement, Alliance's forward base in Ashenvale."
REGION = "Kalimdor - Western Forest"
W, H = 110, 90
BAKED_DIR = "assets/tiles/astranaar/baked"
PORTALS = {(55, 85): "Ashenvale West"}
ARRIVALS = [(55, 83)]
START = (55, 80)

ROADS = {
    "south": ([(55, 86), (55, 78), (54, 70), (55, 63)], 4.0),
    "north": ([(55, 46), (55, 41), (55, 37), (55, 33)], 3.8),
    "west":  ([(44, 56), (36, 56), (28, 57), (18, 56)], 3.2),
    "east":  ([(66, 55), (76, 54), (86, 53), (96, 51)], 3.2),
    "nw":    ([(51, 42), (44, 37), (36, 32), (27, 31)], 2.6),
    "ne":    ([(59, 42), (66, 36), (72, 33)], 2.6),
    "se":    ([(61, 61), (68, 66), (76, 71), (84, 74)], 2.6),
    "sw":    ([(49, 61), (42, 66), (35, 70), (30, 72)], 2.6),
}
STREAMS = {"brook": ([(38, 17), (36, 24), (34, 32), (34, 42), (30, 50), (27, 60), (28, 69)], 3.6)}
STREAM_SHRINK = 1.4
POOLS = [(28, 76, 6.5, 4.8, 2.4),            # the pond the brook runs into
         (55, 54, 3.8, 2.8, 1.6)]            # the moon pool in the plaza
MOON_POOLS = [(55, 54, 4.4)]
PLAZA = (55, 54, 12.5, 8.5)
PAVED_PATCHES = [(55, 36, 8, 5), (55, 79, 4.5, 3.5), (82, 78, 7, 4.5)]   # hall steps, gate, druid grove
CLEARINGS = [(55, 52, 34, 28), (55, 26, 22, 13), (86, 50, 13, 15), (28, 30, 13, 13), (24, 56, 14, 14),
             (80, 74, 14, 10), (55, 81, 10, 8), (24, 74, 12, 9), (92, 28, 10, 10)]
DECKS = [(24.0, 33.0, 54.7, 58.9),           # west footbridge over the brook
         (30.0, 38.5, 28.8, 33.2)]           # north footbridge
CLEARING_GRASS = True
DECK_PAINT = False                           # the footbridges are sprites (ash_footbridge); the brook stays painted under them

BLUEBELL_PATCHES = [(92, 30, 6, 4), (70, 78, 5, 3), (20, 62, 5, 3)]

NPC_POSITIONS = {
    "astranaar_sentinel_commander": (55, 31),   # Sentinel Eltharaen - hall door
    "astranaar_moon_guard": (25, 30),           # Talonar Swiftmoon - tower foot
    "astranaar_innkeeper": (82, 52),            # Innkeeper Rimble - inn door
    "astranaar_weapon_vendor": (40, 53),        # Sentinel Weaponsmith
    "astranaar_armor_vendor": (40, 60),         # Astranaar Outfitter
    "astranaar_druid_trainer": (90, 77),        # Kerlonian Evershade - druid grove
    "astranaar_sentinel_trainer": (22, 54),     # Drill Instructor - pavilion
    "astranaar_flight_master": (73, 31),        # beside the hippogryph perch
    "astranaar_sentinel_liaison": (47, 64),     # Sentinel Shalasyr
    "astranaar_grove_warden": (84, 76),         # Grove Warden Pennarin
    "astranaar_refugee": (51, 76),              # Thessaly Windrunner, just inside the gate
}
FORGE = (72, 73)
EXTRA_NPC_XY = [FORGE]
CHESTS = [(96, 36), (16, 70), (66, 28)]


def dress(L):
    A, B, F, V = L.p, L.b, L.f, L.v
    # ---- gate: the living-tree arch, lanterns lining the south road
    V("ash_living_gate_arch", 55, 82, 8)
    for (x, y) in [(51, 77), (59, 77), (51, 70), (59, 70), (51, 64), (59, 64)]:
        V("ash_moon_lantern", x, y, 5)
    A("ash_signpost", 60, 80, 5)
    V("ash_footbridge", 28, 58, 5)               # west footbridge over the brook
    V("ash_footbridge", 34, 33, 5)               # north footbridge
    # ---- the plaza: moon pool, Elune, benches of light
    A("ash_elune_statue", 46, 47, 8)
    A("ash_elune_statue", 64, 47, 8)
    for (x, y) in [(44, 51), (66, 51), (44, 60), (66, 60)]:
        V("ash_moon_lantern", x, y, 5)
    A("ash_market_stall", 38, 51, 6)
    A("ash_market_stall", 38, 62, 6)
    A("ash_market_stall", 71, 60, 6)
    # ---- north terrace: the Sentinel hall, steps, banners, the hippogryph perch
    B("sentinel_outpost_hall", 55, 29, 15, road_ok=False, nudge=1)
    F("ash_overgrown_steps", 48, 35, 4)
    A("ash_sentinel_banner", 49, 33, 7)
    A("ash_sentinel_banner", 61, 33, 7)
    A("ash_hippogryph_perch", 72, 29, 8)
    B("nightelf_house_small", 38, 24, 11)
    B("nightelf_house_small", 68, 23, 11)
    A("ash_glow_mushroom_ring", 40, 36, 4)
    # ---- west bank: tower, Sentinel camp, drill pavilion
    B("moon_guard_tower", 24, 28, 15)
    B("ash_sentinel_tent", 21, 39, 8)
    A("ash_sentinel_weapon_rack", 27, 41, 5)
    A("ash_glaive_thrower", 18, 44, 6)
    A("ash_sentinel_banner", 28, 37, 7)
    B("training_pavilion", 21, 52, 11)
    A("ash_archery_butts", 13, 56, 4)
    A("ash_silver_saplings", 15, 62, 6)
    A("ash_nightbloom_bush", 18, 69, 4)
    # ---- east: the inn, houses, the waterfall pool
    B("nightelf_house_medium", 83, 49, 12)
    A("ash_inn_sign", 76, 51, 6)
    A("ash_travel_trunks", 80, 56, 3)
    B("nightelf_house_small", 94, 44, 11)
    B("nightelf_house_small", 92, 61, 11)
    A("ash_hollow_stump_door", 77, 41, 8)
    A("ash_waterfall_pool", 97, 33, 7)
    A("ash_giant_ash_tree", 89, 23, 16)
    # ---- south-east: druid grove + forge
    B("druid_priestess_hut", 90, 74, 13)
    A("ash_moon_rune_stone", 82, 69, 6)
    A("ash_herbalist_table", 85, 80, 4)
    A("ash_foxglove_patch", 78, 77, 3)
    B("ash_elf_forge", 72, 70, 8)
    A("ash_nightbloom_bush", 66, 74, 4)
    # ---- south-west: the nightsaber stable
    B("ash_nightsaber_stall", 40, 71, 7)
    A("ash_sleeping_nightsaber", 47, 69, 4, solid=False)
    A("ash_hay_pile", 34, 74, 3)
    A("ash_moon_well", 36, 63, 6)
    # ---- the pond: a jetty and the ruins above it
    A("ash_canoe_jetty", 21, 74, 5, shore_ok=True)
    A("ash_elven_ruin_wall", 14, 76, 7)
    A("ash_ivy_pillar", 39, 79, 6)
    # a few quiet fillers
    for (x, y) in [(60, 70), (48, 58), (37, 44), (88, 38), (14, 50), (66, 45)]:
        F("ash_foxglove_patch", x, y, 3)
    L.edge_canopy(seed=51)


AK.install(sys.modules[__name__])
