"""
Hand-built Emerald Sanctuary (104x88): the Emerald Reclamation's town in South Felwood (claude/felwood_brief.md).

Kyle, 14 Nov 2026: "Town in central south near Emerald Sanctuary", "emerald sanctuary is not ashenvale",
and "its a group thing, whole new faction!" So this is NOT a night elf town with guests. It's the first
glade the druids cleansed, and four peoples live in it, each in its own quarter round the moonwell shrine
that started it:

    the shrine ........ centre: the moonwell shrine on a paved ring, the Arch Druid at its steps
    the Sentinels ..... north, facing the Fel Line: hall, watchtower, tents, the barricade
    the Timbermaw ..... east: honey-wood lodges, bear totems, the Timbermaw elder
    the grove ......... south: the druids' treehouse, the purified pool, treants standing among the trees
    the volunteers .... west, by the gate: the transplants' corner - the inn, the roost, the supply house,
                        the camp kitchen and the forge they built. Nothing from Earth is in it; the
                        people are from Earth and everything they've built is from Felwood.

The town engine (tools/ashenvale_town_kit.py) only paints the ground and walls; every building is Kyle's
Felwood sheet. The ground is graded greener and brighter than Ashenvale's (LUSH/GRADE, read by
tools/bake_ashenvale.py), the cleansed heart of the forest.

HARD CONTRACTS (world/portal_manager.py)
  portal   (3,44) -> South Felwood (100,118);  arrival (5,44)
  NPC ids  es_*, written by tools/sync_emerald_sanctuary_npcs.py from NPC_POSITIONS
"""
import sys

from tools import ashenvale_town_kit as AK

KEY = "emerald_sanctuary"
NAME = "Emerald Sanctuary"
DESC = "The Emerald Reclamation's town: night elves, Timbermaw, treants and transplants in the first glade the druids cleansed."
REGION = "Kalimdor - Felwood"
W, H = 104, 88
BAKED_DIR = "assets/tiles/felwood/baked_sanctuary"
PORTALS = {(3, 44): "South Felwood"}
ARRIVALS = [(5, 44)]
START = (8, 44)

ROADS = {
    "gate":   ([(2, 44), (12, 44), (24, 44), (38, 44)], 4.0),
    "north":  ([(52, 34), (52, 28), (52, 24)], 3.4),
    "east":   ([(64, 44), (74, 45), (84, 47), (92, 50)], 3.2),
    "south":  ([(52, 54), (52, 62), (52, 70)], 3.4),
    "nw":     ([(24, 44), (24, 34), (26, 26)], 2.6),
    "sw":     ([(24, 44), (24, 54), (26, 62)], 2.6),
    "ne":     ([(60, 38), (68, 30), (76, 26)], 2.4),
    "se":     ([(60, 50), (66, 60), (72, 68)], 2.4),
}
STREAMS = {"brook": ([(96, 10), (90, 20), (88, 32), (94, 40), (100, 46)], 3.0)}
STREAM_SHRINK = 1.3
POOLS = [(40, 72, 5.5, 4.0, 2.0)]            # the grove's purified pool
MOON_POOLS = [(40, 72, 6.0)]
PLAZA = (52, 44, 12.5, 9.0)
PAVED_PATCHES = [(52, 24, 7, 4), (6, 44, 4, 3.5), (52, 70, 5, 3)]
CLEARINGS = [(52, 44, 36, 30), (52, 20, 24, 12), (84, 48, 16, 16), (50, 72, 22, 12), (20, 44, 16, 22),
             (30, 64, 12, 9), (74, 70, 10, 8), (6, 44, 8, 8)]
DECKS = []
CLEARING_GRASS = True
DECK_PAINT = False
BLUEBELL_PATCHES = [(50, 74, 12, 6), (84, 60, 6, 4), (20, 58, 6, 4), (70, 26, 6, 4)]
LUSH = 1.0
GRADE = (1.40, 1.14)

NPC_POSITIONS = {
    # the four who lead it
    "es_arch_druid":        (52, 54),    # Arch Druid Aelyra Moonbough - the shrine steps
    "es_sentinel_captain":  (55, 25),    # Captain Saranis Duskwhisper - the hall door
    "es_timbermaw_elder":   (80, 50),    # Elder Grumhall Oakpelt - the lodge door
    "es_treant_elder":      (62, 72),    # Old Thornbark - among the grove trees
    # services
    "es_innkeeper":         (18, 39),    # Innkeeper Nelanthe Softbough
    "es_flight_master":     (16, 58),    # Windrider of the roost, Faelin Skybough
    "es_quartermaster":     (40, 24),    # Sentinel Quartermaster Ilyssa - arms and armour
    "es_timbermaw_trader":  (88, 44),    # Trader Burlrock - Timbermaw goods
    "es_herbalist":         (44, 64),    # Druid Mirelle Fernsong - herbs and reagents
    "es_camp_cook":         (30, 52),    # Luis Ortega - the volunteers' kitchen
    # the transplants: people, not recruits
    "es_volunteer_medic":   (34, 36),    # Dr. Nkechi Adeyemi
    "es_volunteer_carpenter": (60, 22),  # Tomasz Wolny - the barricade
    "es_volunteer_botanist": (66, 64),   # Yuki Hashimoto - cataloguing the regrowth
    "es_volunteer_runner":  (12, 48),    # Ana Lucia Ferreira - just inside the gate
    # treants who stand where the Sentinels stand
    "es_treant_warden":     (74, 26),
    # Kyle, 14 Nov: "Only a herbalist and alchemy trainer in sanctuary." By the druids' herb table.
    "pt_emerald_sanctuary_herbs": (38, 66),
}
FORGE = (36, 58)
EXTRA_NPC_XY = [FORGE]
CHESTS = [(94, 30), (14, 30), (82, 72)]


def dress(L):
    A, B, F, V = L.p, L.b, L.f, L.v
    # ---- the gate: two old trees and the road in
    A("fw_ashenvale_tree", 8, 38, 10)
    A("fw_ashenvale_tree", 8, 52, 10)
    A("ash_signpost", 12, 40, 5)
    # ---- the shrine: the moonwell that started it
    B("fw_moonwell_shrine", 52, 50, 11, road_ok=True, nudge=1)
    for (x, y) in [(42, 38), (62, 38), (42, 50), (62, 50)]:
        V("ash_moon_lantern", x, y, 5)
    F("fw_moonflowers", 46, 40, 3)
    F("fw_moonflowers", 58, 40, 3)
    # ---- north: the Sentinels, facing the Fel Line
    B("fw_sentinel_hall", 52, 21, 13, nudge=1)
    B("fw_sentinel_tower", 34, 22, 13)
    B("fw_sentinel_tent", 66, 22, 7)
    B("fw_stake_barricade", 44, 12, 6)
    B("fw_stake_barricade", 60, 12, 6)
    A("ash_sentinel_weapon_rack", 40, 27, 5)
    A("ash_glaive_thrower", 72, 30, 6)
    # ---- east: the Timbermaw
    B("fw_timbermaw_lodge", 82, 46, 11)
    B("fw_timbermaw_lodge", 90, 60, 11)
    A("fw_timbermaw_totem", 76, 52, 8)
    A("fw_timbermaw_totem", 94, 40, 8)
    A("ash_hay_pile", 86, 52, 3)
    # ---- south: the grove, the pool, the treehouse
    B("fw_druid_treehouse", 54, 76, 14)
    A("fw_purified_moonwell", 30, 76, 6)
    A("fw_ashenvale_tree", 66, 78, 11)
    A("fw_ashenvale_tree", 42, 80, 11)
    A("fw_half_cleansed_tree", 72, 64, 10)       # the one the druids are still working on
    F("fw_moonflowers", 48, 66, 3)
    A("ash_glow_mushroom_ring", 60, 66, 3)
    # ---- west: the volunteers' corner by the gate
    B("fw_inn", 15, 35, 11)
    B("fw_hippogryph_roost", 16, 56, 10)
    B("fw_supply_house", 34, 48, 8)
    B("fw_sentinel_tent", 28, 56, 7)                 # the kitchen tent
    A("ash_elf_forge", 36, 56, 6)
    A("ash_travel_trunks", 30, 46, 3)
    A("ash_herbalist_table", 40, 62, 4)
    L.edge_canopy(seed=73, names=(("fw_ashenvale_tree", 11), ("large_canopy_tree", 11), ("canopy_tree_cluster", 10)))


AK.install(sys.modules[__name__])
