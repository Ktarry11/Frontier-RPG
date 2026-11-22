"""
Hand-built MOONGLADE (200x170): the druids' valley round Lake Elune'ara, a town and a hub at the end of Kalimdor's 55-60
road (docs/moonglade_brief.md).

Kyle, 18 Nov 2026: "moonglade can be quite a decent size but is still a town and hub. there will be an inn and a
flight path. no monsters", "We do need the giant water in the middle that can have something later too", and "Get
that mystical druid look for moonglade, we should have the lush tiles, trees, and brillian beautiful water!" Three
dungeons come later (a corrupted druid one in the Barrow Dens, an Emerald Dream one through the Dreaming Arch, and one
under the lake); their doors are on the map from the start and lead nowhere yet.

ORIENTATION FOLLOWS THE OVERWORLD. Moonglade is north-west of the Timbermaw Tunnel and Felwood, with Winterspring to
the east: you come up the Moonglade passage and in at the south-east, and the pass to Winterspring leaves from the
north-east (shut by snow and rockfall until Winterspring exists).

    LAKE ELUNE'ARA fills the middle. The island in its centre (a ring of moonstones round a still pool that reflects
      nothing, a broken stair going down into it) is the third dungeon's door, out of reach: no bridge, no boat.
    NIGHTHAVEN, the east shore: the town proper. The great moonwell in the middle, the flight roost (hippogryphs and
      wind riders, the valley's one flight path) and the tauren quarter north of it, the Cenarion Circle's hall and
      the night elf houses south, the inn by the way in, the pier out into the lake, the trades.
    THE SHRINE OF REMULOS on the north-west point, and THE DREAMING ARCH behind it in the north woods.
    THE FALLS OF ELUNE'ARA, coming down into the lake's north shore.
    THE WAKENED'S SETTLEMENT, the west shore: the longhouse, the cabins, the infirmary, the gardens, and the wall of
      last memories, with the reed beds below it.
    THE STORMRAGE BARROW DENS in the south-west hills, behind a living thorn ward with the Circle's wardens on it.

The art is Kyle's Moonglade sheets (docs/moonglade_art_prompts.md, the mg_ set in assets/tiles/moonglade and
assets/buildings), the ground his Moonglade ground sheet (tools/bake_ashenvale.py MOONGLADE_SHEET).

HARD CONTRACTS (world/portal_manager.py)
  portal   (156,169) <-> the Timbermaw Tunnel's Moonglade passage (12,34): you arrive at (156,165) coming in and
           (12,36) going out
  later    THE DOORS: the Barrow Dens (DOORS["barrows"]), the Dreaming Arch (DOORS["arch"]), the island (DOORS["island"])
  NPC ids  mg_*, ct_moonglade, pt_mg_*: written by tools/build_moonglade.py from NPC_POSITIONS
"""
import math
import sys

import numpy as np  # noqa: F401

from tools import ashenvale_town_kit as AK

KEY = "moonglade"
NAME = "Moonglade"
DESC = ("The druids' valley: Lake Elune'ara under a moon that never sets, Nighthaven on its shore, and a quiet "
        "everybody who lives here can feel. Something else is waking up.")
REGION = "Kalimdor - Moonglade"
W, H = 200, 170
BAKED_DIR = "assets/tiles/moonglade/baked"
SHEET = "moonglade"
PORTALS = {(156, 169): "Timbermaw Tunnel"}
ARRIVALS = [(156, 165)]
START = (156, 158)
#: the three dungeons' doors (later): where each one's portal will stand
DOORS = {"barrows": (30, 150), "arch": (100, 21), "island": (100, 90)}

LAKE = (100, 86)


def _ring(rx, ry, a0=0, a1=360, step=15):
    return [(round(LAKE[0] + rx * math.cos(math.radians(a))), round(LAKE[1] + ry * math.sin(math.radians(a))))
            for a in range(a0, a1 + 1, step)]


ROADS = {
    # the lakeshore road, all the way round
    "ring":     (_ring(66, 50), 2.6),
    # up from the Moonglade passage to Nighthaven
    "in":       ([(156, 170), (156, 154), (150, 136), (146, 122)], 3.2),
    # Nighthaven's street, north to south behind the shore
    "main":     ([(162, 44), (172, 56), (174, 72), (172, 92), (170, 112), (162, 132), (154, 148)], 3.0),
    # the old pass to Winterspring, shut
    "pass":     ([(172, 56), (180, 46), (186, 40)], 2.4),
    # the pier walk
    "pier":     ([(166, 88), (151, 88)], 2.4),
    # the Shrine of Remulos, the Dreaming Arch, the Barrow Dens
    "shrine":   ([(54, 52), (46, 46)], 2.6),
    "arch":     ([(100, 36), (100, 30), (100, 24)], 2.2),
    "barrows":  ([(52, 122), (40, 140), (32, 152)], 2.4),
    # the Wakened's lanes
    "wakened":  ([(34, 92), (20, 92), (10, 100)], 2.4),
    "w_north":  ([(34, 92), (42, 80), (40, 62)], 2.2),
    "w_south":  ([(22, 92), (22, 106), (28, 122)], 2.2),
}
STREAMS = {}
#: the lake: a big body with a west lobe and a north-east lobe so it never reads as an ellipse (cx, cy, rx, ry, shrink)
POOLS = [(100, 86, 50, 34, 3.6), (60, 98, 16, 13, 3.0), (136, 68, 16, 10, 3.0), (106, 116, 20, 8, 2.6)]
#: Nighthaven's square round the great moonwell
PLAZA = (174, 80, 11, 8)
PAVED_PATCHES = [(42, 40, 9, 6),       # the shrine's old flagstones
                 (176, 110, 8, 5)]     # before the Circle's hall
CLEARINGS = [
    (100, 86, 84, 66),      # the valley floor
    (40, 34, 22, 16),       # the Shrine of Remulos
    (100, 20, 16, 10),      # the Dreaming Arch's glade
    (176, 60, 22, 26),      # Nighthaven north (the roost, the tauren)
    (172, 120, 24, 34),     # Nighthaven south
    (24, 92, 20, 34),       # the Wakened
    (34, 146, 20, 14),      # the Barrow Dens
    (156, 158, 12, 12),     # the way in
    (188, 38, 12, 10),      # the end of the Winterspring pass
]
GAPS = []
#: knuckles of mountain rock: the cliff behind the falls, and the barrow hill over the dens' door
ROCKS = [(124, 50, 7, 4), (24, 140, 8, 5), (194, 32, 6, 8)]
DECKS = [(134, 152, 86, 90)]                # the pier, out over the shallows
DECK_MAT = "pl_elf"
#: the pier's planks are the sheet's own silver-grey boardwalk (tools/bake_ashenvale_towns.py EXTRA_TILES)
EXTRA_TILES = {"av_elf_planks": "assets/tiles/moonglade/ground/mg_boardwalk.png"}
CLEARING_GRASS = True
#: the island's still pool and Nighthaven's great moonwell are sprites; the moon water layer is the falls' pool
MOON_POOLS = []
EXTRA_PATCHES = {
    "fel":     [(100, 20, 10, 6, 1.2)],                               # the Dream's grass round the arch
    "corrupt": [(30, 148, 7, 4, 1.1)],                                # the bramble earth before the barrow door
    "satyr":   [(30, 152, 10, 6, 1.0)],                               # the barrow hill's old earth
    "scorch":  [(16, 66, 6, 4, 1.2), (38, 108, 5, 3, 1.0)],           # the Wakened's gardens
    "burned":  [(166, 98, 6, 4, 0.9), (44, 30, 6, 4, 0.9)],           # fallen petals by the hall and the shrine
    "bell":    [(60, 60, 8, 6, 0.9), (140, 120, 8, 6, 0.9), (120, 150, 10, 5, 0.9), (70, 136, 9, 5, 0.9)],
}

NPC_POSITIONS = {
    # ---- the Cenarion Circle, Nighthaven
    "mg_rabine":          (172, 118),    # Rabine Saturna, who keeps Nighthaven, at the Circle's hall
    "mg_hamuul":          (160, 52),     # Archdruid Hamuul Runetotem, in the tauren quarter
    "mg_bunthen":         (184, 72),     # Bunthen Plainswind, the roost: the valley's one flight path
    "mg_circle_qm":       (182, 118),    # the Cenarion Circle's quartermaster
    "mg_innkeeper":       (164, 142),    # the inn, by the way in
    "ct_moonglade":       (162, 104),    # the class trainer
    "pt_mg_herbs":        (186, 100),    # herbalism and alchemy
    "pt_mg_hide":         (186, 140),    # skinning and leatherworking
    "pt_mg_fish":         (150, 92),     # cooking and fishing, at the pier
    "mg_provisioner":     (176, 148),    # food and drink
    "mg_moonwell_keeper": (164, 82),     # the great moonwell
    "mg_tauren_elder":    (168, 46),     # the tauren survivors
    # ---- the Shrine of Remulos and the north woods
    "mg_remulos":         (42, 46),      # Keeper Remulos, under his tree
    "mg_arch_watcher":    (108, 26),     # a druid who sits with the Dreaming Arch
    # ---- the Wakened, west shore
    "mg_sandvik":         (26, 94),      # Dr. Ingrid Sandvik, at the longhouse
    "mg_wakened_qm":      (20, 80),      # the Wakened's quartermaster
    "mg_infirmary":       (18, 112),     # the infirmary's keeper
    "mg_carver":          (40, 72),      # who started the wall of last memories
    "mg_gardener":        (14, 66),
    "mg_dreamer":         (10, 98),      # who never stopped trying to go back to sleep
    # ---- the Barrow Dens
    "mg_barrow_warden":   (40, 146),
    "mg_barrow_warden_b": (20, 154),
}
#: the sheet-5 recruits (tools/build_sheet5_recruits.py PINNED): Valentina on the north shore at night, Faris in the
#: reed beds below the Wakened
RECRUITS = {"valentina": (84, 44), "faris": (44, 112)}
CHESTS = []


def dress(L):
    A, B, F, V = L.p, L.b, L.f, L.v
    # ---------------------------------------------------------------- the lake: the island, the falls, the edges
    V("mg_island", 100, 94, 13)
    V("mg_falls", 124, 60, 14)
    for (x, y, h) in [(60, 104, 3), (66, 114, 3), (84, 116, 3), (136, 104, 3), (128, 112, 3), (70, 72, 3)]:
        V("mg_lily_cluster", x, y, h)
    for (x, y, h) in [(56, 96, 5), (58, 84, 5), (62, 110, 4), (144, 76, 4)]:
        V("mg_reed_bed", x, y, h)
    V("mg_stepping_stones", 64, 62, 4)
    V("mg_sunken_stone", 140, 66, 5)
    # ---------------------------------------------------------------- NIGHTHAVEN
    B("mg_great_moonwell", 174, 80, 11, road_ok=True)
    A("mg_moon_lantern", 162, 76, 5)
    A("mg_moon_lantern", 186, 76, 5)
    B("mg_flight_roost", 186, 68, 15)
    # the tauren quarter, north
    B("mg_tauren_lodge", 158, 48, 9)
    B("mg_tauren_lodge", 176, 42, 9)
    B("mg_tauren_tent", 166, 38, 7)
    A("mg_tauren_totem", 170, 50, 7)
    A("mg_tauren_cookfire", 164, 56, 4)
    A("mg_hide_rack", 152, 58, 5)
    A("mg_tauren_memorial", 182, 52, 6)
    # the Circle's hall and the night elf houses, south
    B("mg_circle_hall", 178, 112, 13)
    A("mg_circle_banner", 168, 112, 6)
    A("mg_circle_banner", 188, 112, 6)
    B("mg_druid_treehouse", 190, 128, 12)
    B("mg_elf_house", 160, 94, 8)
    B("mg_elf_cottage", 154, 108, 7)
    B("mg_circle_house", 158, 120, 8)
    B("mg_elf_house", 180, 136, 8)
    B("mg_elf_inn", 166, 138, 10)
    A("mg_moon_lantern", 158, 140, 5)
    # the trades
    A("mg_herb_stall", 190, 102, 5)
    A("mg_alchemy_table", 182, 100, 4)
    A("mg_hide_frame", 192, 142, 5)
    A("mg_market_stall", 182, 152, 5)
    B("mg_stable_pen", 168, 156, 5)
    A("mg_druid_altar", 164, 66, 5)
    A("mg_warden_post", 150, 156, 6)
    # the pier
    A("mg_moon_lantern", 156, 85, 4)
    V("mg_pier", 136, 93, 5)
    # ---------------------------------------------------------------- THE SHRINE OF REMULOS
    B("mg_shrine_of_remulos", 40, 40, 20)
    A("mg_moonstone", 56, 34, 6)
    A("mg_moonstone_ring", 28, 48, 4)
    A("mg_moon_lilies", 54, 44, 3)
    A("mg_cup_boulder", 26, 36, 4)
    # ---------------------------------------------------------------- THE DREAMING ARCH
    B("mg_dreaming_arch", 100, 20, 12)
    A("mg_dream_motes", 92, 22, 3)
    A("mg_dream_motes", 108, 20, 3)
    A("mg_gold_flowers", 94, 26, 3)
    A("mg_gold_flowers", 108, 28, 3)
    # ---------------------------------------------------------------- THE WAKENED
    B("mg_wakened_longhouse", 24, 88, 13)
    B("mg_cabin", 8, 86, 7)
    B("mg_longhouse", 20, 72, 9)
    B("mg_cabin", 34, 64, 7)
    B("mg_infirmary", 16, 108, 8)
    A("mg_dream_cot", 26, 112, 4)
    A("mg_dream_cot", 26, 118, 4)
    B("mg_memory_wall", 42, 78, 5)
    A("mg_garden_beds", 14, 62, 4)
    B("mg_wash_house", 36, 104, 6)
    B("mg_meeting_house", 14, 124, 8)
    A("mg_wakened_banner", 36, 96, 6)
    A("mg_wakened_banner", 14, 96, 6)
    A("mg_woodpile", 8, 90, 4)
    A("mg_rain_barrel", 30, 124, 4)
    A("mg_bench_shelter", 44, 100, 4)
    # ---------------------------------------------------------------- THE BARROW DENS
    # the door's own art carries the living thorn ward that shuts it
    B("mg_barrow_door", 30, 150, 12, allow_overlap=True)
    A("mg_warden_post", 44, 142, 6)
    A("mg_moonstone", 14, 148, 5)
    # ---------------------------------------------------------------- the Winterspring pass, shut
    A("mg_rock_outcrop", 190, 40, 6, solid=True, road_ok=True, allow_overlap=True)
    A("mg_shore_boulders", 186, 36, 4, solid=True, road_ok=True, allow_overlap=True)
    # ---------------------------------------------------------------- the glade: trees, flowers, stones
    for (name, x, y, h) in [
            ("mg_ancient_oak", 66, 30, 13), ("mg_violet_tree", 132, 30, 12), ("mg_willow", 54, 70, 11),
            ("mg_willow", 146, 110, 11), ("mg_silver_birch", 120, 36, 10), ("mg_blossom_tree", 82, 132, 9),
            ("mg_ancient_oak", 120, 140, 13), ("mg_violet_tree", 60, 132, 12), ("mg_twisted_tree", 140, 140, 10),
            ("mg_pine", 30, 22, 12), ("mg_blossom_tree", 150, 32, 9),
            ("mg_violet_tree", 46, 124, 11), ("mg_willow", 152, 64, 10), ("mg_ancient_oak", 86, 34, 12),
            ("mg_silver_birch", 104, 146, 10)]:
        A(name, x, y, h)
    for (name, x, y, h) in [
            ("mg_star_flowers", 74, 50, 3), ("mg_lupins", 110, 44, 3), ("mg_glow_mushroom_ring", 92, 138, 3),
            ("mg_silver_mushrooms", 130, 132, 3), ("mg_moon_lilies", 150, 124, 3), ("mg_nightbloom", 58, 120, 3),
            ("mg_fern", 72, 140, 3), ("mg_berry_bush", 138, 46, 3), ("mg_flower_hedge", 186, 144, 3),
            ("mg_mossy_log", 112, 150, 3), ("mg_moon_crystals", 76, 128, 3), ("mg_elven_pillar", 136, 128, 5),
            ("mg_owl_stump", 62, 46, 4), ("mg_white_rabbits", 118, 132, 3), ("mg_antlers", 52, 140, 3),
            ("mg_sapling", 144, 52, 5), ("mg_star_flowers", 160, 128, 3), ("mg_nightbloom", 98, 40, 3)]:
        F(name, x, y, h)
    # the woods all round the valley: the Moonglade trees as the treeline
    L.edge_canopy(seed=5801, names=(("mg_ancient_oak", 13), ("mg_violet_tree", 12), ("mg_pine", 12),
                                    ("mg_willow", 11), ("mg_silver_birch", 11)), spacing=4.2, prob=0.55)


AK.install(sys.modules[__name__])


if __name__ == "__main__":
    L = build_layout()  # noqa: F821  (defined by AK.install)
    n, bad = AK.report(L)
    print(NAME, W, "x", H, "| reachable", n, "| unreachable", bad, "| skipped", getattr(L, "skipped", None))
    if "--preview" in sys.argv:
        AK.preview(L, sys.argv[sys.argv.index("--preview") + 1])

#: the districts, where the townsfolk live (Kyle, 22 Nov 2026: "ensure ALL towns are actually populated"; names made up to
#: fit). (key, x, y, w, h, display name)
SUBZONES = [
    ('Moonglade', 0, 0, 200, 170, None),
    ('The Tauren Camp', 144, 34, 48, 32, None),
    ('The Great Moonwell', 154, 66, 46, 24, None),
    ('The Pier', 124, 82, 30, 22, None),
    ('The Circle Hall', 148, 96, 52, 26, None),
    ('Nighthaven Lane', 144, 122, 56, 22, None),
    ('The Market Green', 150, 144, 50, 24, None),
]
