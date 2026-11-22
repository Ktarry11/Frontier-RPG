"""
Hand-built Timbermaw Hold (220x200): the Timbermaw furbolgs' capital, a caldera city in the mountains above West
Azshara (docs/azshara_brief.md).

Kyle, 17 Nov 2026: Azshara's second hub is "timbermaw hold", "a massive Timbermaw Hold (this will be larger)"; it's a
caldera city with an inn and no flight point, and the Felwood Timbermaw Tunnel gets a long east passage that comes out
here. Then: "we know that timbermaw rep vendor and the leader will be in timbermaw hold and not in the tunnel", and
"Dont forget timbermaw hold is going to look like an actual capital city and it will have the dungeon under it. This is
similar to how org is." So it's built as a CAPITAL, Orgrimmar's way: quarters each with their own trade, homes packed
in round the work, the services a capital has (inn, mail, bank, auction house, a class trainer for every class and the
trades in their pairs), and the dungeon's door in the middle of the city, the way Ragefire Chasm opens in Orgrimmar's
Cleft.

THE SHAPE: A LOBED HOLLOW, NOT A RING. The first draft was two perfect rings and eight spokes, a dartboard (Kyle on
earlier maps: "Still doing a lot of circular blobs", and the Dry Deep's hub-and-spokes). So the caldera is a basin in
the middle with seven QUARTERS cut into the wall round it, strung round the rim. Four ramps come down to the basin
(from the Elders, the carvers, the tunnel and the gate); every other quarter is reached along the caldera wall from
its neighbours, so the rim is a path that loops:
    THE ELDERS' TERRACE (north): the Elders' Great Lodge, the ancestor shrine, the Elders' own lodges, the class trainer
    THE LONG HALL (north-west): the long hall, where the Hold's stores are kept, and the homes round it
    THE HONEY TERRACES (north-east): the hive-tree, the skeps, the honey stores and the press
    THE CARVERS' QUARTER (east): the carvers' hall, the unfinished totem, woodworking
    THE MARKET (south-east, by the gate): the inn, the bank and the auction house with the mail between them (Kyle:
      "an auction house, a bank, and a mailbox close together"), the stalls, the provisioner
    THE WORKSHOPS (south-west): the smithy, the tannery, the herb racks and their trainers
    THE TUNNEL MOUTH (west): the cave lodge, the terrace over it, the way through to Felwood
    THE BASIN: the great totem and the bonfire on the honey-clay square, the sacred spring, the quartermaster, and THE
      DEEP GATE in the floor, chained and warded, with wardens on it. Whatever turned the Deadwood came up from below
      the Hold; the fel rot dungeon (docs/azshara_brief.md) is under the city, and that gate is its door (later).

ORIENTATION FOLLOWS THE OVERWORLD (Kyle, 17 Nov: "ensure the orientation is accurate"):
    the south gate (120,198) <- West Azshara (62,4), the top of the Ursolan pass: you climb in from the south
    the west door (1,108)    <- the Timbermaw Tunnel's east passage (177,152): Felwood is west of Azshara

Buildings and props are Kyle's Timbermaw Hold sheet (docs/azshara_art_prompts.md sheet 4, the tm_ set) with the
Timbermaw pieces from Felwood and Ashenvale; trees are the Azshara autumn set. The ground is the Azshara sheet
(tools/bake_ashenvale.py TIMBERMAW_HOLD_SHEET).

HARD CONTRACTS (world/portal_manager.py)
  portal   (120,198) <-> West Azshara (62,4): you arrive at (120,194) coming in and (62,7) going out
  portal   (1,108) <-> Timbermaw Tunnel (177,152): you arrive at (4,108) coming in and (174,152) going out
  portal   (129,96) <-> The Rotroot Deeps (22,3), in front of the deep gate's doors: you arrive at (129,98) coming
           out and (22,6) going down
  NPC ids  th_*, ct_timbermaw_hold, pt_th_* (the Hold's own) and the two who moved up from the tunnel, tm_elder and
           tm_quartermaster; all written by tools/build_timbermaw_hold.py, which holds every Timbermaw
"""
import sys

from tools import ashenvale_town_kit as AK

KEY = "timbermaw_hold"
NAME = "Timbermaw Hold"
DESC = ("The Timbermaw's home: a city in the hollow of the mountain, open to the sky, with lodges up the walls, a "
        "great totem in the middle and a gate in the floor that nobody opens.")
REGION = "Kalimdor - Azshara"
W, H = 220, 200
BAKED_DIR = "assets/tiles/azshara/baked_timbermaw_hold"
SHEET = "timbermaw_hold"
EDGE = "rock"
PORTALS = {(120, 198): "West Azshara", (1, 108): "Timbermaw Tunnel", (129, 96): "The Rotroot Deeps"}
ARRIVALS = [(120, 194), (4, 108), (129, 98)]
START = (120, 188)
#: the deep gate in the basin floor opened on 18 Nov 2026: its door is the tile in front of the gate's doors, in PORTALS
LATER_DOORS = {}

ROADS = {
    # the climb in from the south gate, through the market, down into the basin
    "gate":     ([(120, 200), (120, 186), (126, 172), (122, 152), (116, 134)], 3.4),
    # round the basin, following its lobes
    "basin":    ([(90, 116), (98, 96), (116, 86), (136, 88), (150, 104), (146, 122), (128, 134), (106, 136),
                  (92, 128), (90, 116)], 3.0),
    # four ramps down to the basin
    "elders":   ([(112, 86), (112, 64), (110, 46), (110, 36)], 3.2),
    "carvers":  ([(150, 108), (168, 112), (186, 112)], 2.8),
    "tunnel":   ([(90, 114), (66, 110), (44, 108), (20, 108), (0, 108)], 3.0),
    # the rim, quarter to quarter along the caldera wall
    "wall_ne":  ([(140, 34), (154, 40), (164, 48), (168, 58)], 2.4),
    "wall_e":   ([(180, 70), (188, 86), (190, 100)], 2.4),
    "wall_n":   ([(82, 34), (70, 42), (60, 52)], 2.4),
    "wall_nw":  ([(32, 94), (38, 78), (48, 66)], 2.4),
    "wall_sw":  ([(30, 124), (40, 140), (52, 154)], 2.4),
    "wall_s":   ([(84, 166), (102, 172), (122, 172)], 2.4),
    # the quarters' own streets
    "elders_st": ([(82, 34), (110, 36), (140, 34)], 2.8),
    "market_st": ([(124, 168), (148, 166), (172, 164)], 2.8),
    "works_st":  ([(36, 160), (60, 162), (84, 166)], 2.8),
    "honey_st":  ([(160, 62), (172, 62), (186, 66)], 2.4),
}
STREAMS = {}
#: the sacred spring, a real pool in the basin's west lobe
POOLS = [(98, 112, 6.5, 4.5, 2.6)]
PLAZA = (120, 112, 12.0, 8.5)               # the honey-clay square round the great totem
PAVED_PATCHES = [(110, 36, 10, 4)]          # the flagstones before the Great Lodge
CLEARINGS = [
    # the basin: three lobes, not one ellipse
    (120, 110, 30, 24), (98, 120, 18, 14), (136, 94, 18, 12),
    # the quarters
    (110, 30, 38, 14),      # the Elders' Terrace
    (52, 56, 26, 18),       # the Long Hall
    (170, 60, 26, 20),      # the Honey Terraces
    (190, 112, 18, 26),     # the Carvers' Quarter
    (148, 166, 34, 18),     # the Market
    (60, 160, 32, 18),      # the Workshops
    (28, 108, 20, 24),      # the Tunnel Mouth
    # the gate gorge
    (120, 192, 10, 9),
]
ROCKS = [(126, 142, 5, 3), (78, 132, 4, 5), (160, 140, 5, 4), (86, 80, 4, 4)]    # knuckles on the slopes
DECKS = []
CLEARING_GRASS = False
DECK_PAINT = False
GRADE = (1.15, 1.08)
EXTRA_PATCHES = {"corrupt": [(130, 88, 6, 4, 1.3)],        # the green creeping up round the deep gate
                 "sawdust": [(190, 120, 6, 4, 1.0)],       # the carvers' yard
                 "scorch": [(46, 160, 4, 3, 1.0)]}         # the smithy's yard

NPC_POSITIONS = {
    # the Elders' Terrace
    "tm_elder":           (110, 40),     # Elder Haldor Mossmane, at the Great Lodge's door (moved up from the tunnel)
    "ct_timbermaw_hold":  (132, 40),     # the class trainer, on the terrace
    "th_orc_envoy":       (88, 40),      # Orgrimmar's envoy, waiting on the Elders
    # the basin
    "tm_quartermaster":   (134, 116),    # Quartermaster Bruna Honeyhide, the square (moved up from the tunnel)
    "th_totemkeeper":     (126, 104),    # at the great totem
    "th_spring_keeper":   (106, 108),    # the sacred spring
    "th_deep_warden":     (110, 94),     # on the deep gate
    "th_deep_warden_b":   (140, 94),
    # the Long Hall
    "th_auctioneer":      (171, 160),    # a goblin, at the auction house's door in the Market
    "th_volunteer":       (36, 56),      # an Earth volunteer, keeping the long hall's stores
    # the Honey Terraces
    "th_banker":          (153, 160),    # MerchantTusk, at the bank's door in the Market
    "th_honeymother":     (178, 74),
    # the Carvers' Quarter
    "th_carver":          (184, 118),
    "pt_th_wood":         (194, 102),    # woodcutting and woodworking
    # the Market
    "th_innkeeper":       (134, 160),    # the inn
    "th_provisioner":     (158, 172),
    # the Workshops
    "th_smith":           (44, 166),
    "pt_th_forge":        (52, 166),     # mining, blacksmithing, jewelcrafting
    "pt_th_hide":         (68, 168),     # skinning, leatherworking, tailoring, cooking, fishing
    "pt_th_herbs":        (80, 158),     # herbalism and alchemy
    # the doors
    "th_gate_warden":     (117, 182),    # the south gate
    "th_gate_warden_b":   (125, 180),
    "th_tunnel_warden":   (14, 104),     # the tunnel's mouth
}
CHESTS = []


def dress(L):
    A, B = L.p, L.b
    # ---- the south gate, and the climb in
    B("tm_totem_gate", 120, 194, 9, solid=False, road_ok=True)
    A("tm_war_banner", 112, 186, 6)
    A("tm_war_banner", 128, 186, 6)
    # ---- THE ELDERS' TERRACE: the Great Lodge at the head of the city, and the Elders' own lodges either side
    B("tm_elders_great_lodge", 110, 32, 19)
    B("fw_timbermaw_lodge", 88, 30, 10)
    B("tm_cliff_lodge", 132, 30, 11)
    A("tm_ancestor_shrine", 78, 28, 7)
    A("tm_candle_stand", 102, 40, 3)
    A("tm_candle_stand", 118, 40, 3)
    A("fw_timbermaw_totem", 146, 30, 7)
    A("tm_war_banner", 98, 42, 6)
    A("tm_war_banner", 122, 42, 6)
    # ---- THE LONG HALL: the trade hall and the homes round it
    B("tm_long_hall", 54, 54, 14)
    B("tm_round_den", 34, 50, 8)
    B("tm_round_den", 70, 62, 8)
    B("tm_round_den", 40, 68, 8)
    A("tm_supply_cache", 62, 46, 4)
    A("tm_stair_ramp", 74, 46, 7)
    A("az_autumn_tree", 28, 62, 9)
    # ---- THE HONEY TERRACES: the hive-tree, the skeps, the stores and the press
    A("tm_hive_tree", 172, 54, 12)
    B("tm_honey_store", 160, 66, 9)
    A("tm_skep_row", 186, 58, 6)
    A("tm_skep_row", 154, 50, 6)
    A("tm_honey_press", 184, 72, 5)
    A("tm_smoke_pot", 192, 64, 4)
    B("tm_round_den", 174, 76, 8)
    A("tm_candle_stand", 166, 72, 3)
    # ---- THE CARVERS' QUARTER: the hall, the yard and the totem that's waiting for its last face
    B("tm_carvers_hall", 194, 98, 13)
    A("tm_great_totem", 182, 108, 9)
    B("tm_round_den", 196, 128, 8)
    A("tm_woodpile", 186, 126, 5)
    A("tm_lookout", 176, 96, 9)
    A("tm_paw_stone", 202, 114, 5)
    # ---- THE MARKET, by the gate: the inn, then the bank and the auction house side by side with the mail between
    # them (Kyle, 17 Nov 2026: "an auction house, a bank, and a mailbox close together"; the bank and AH sheet's
    # tauren pair, docs/bank_auction_art_prompts.md), and the stalls in front
    B("tm_inn", 134, 156, 13)
    B("bank_tauren", 153, 156, 13)
    B("ah_tauren", 172, 156, 13)
    B("tm_market_stall", 150, 178, 6)
    B("tm_market_stall", 166, 180, 6)
    A("tm_supply_cache", 182, 172, 5)
    A("tm_drum_circle", 136, 176, 5)
    # ---- THE WORKSHOPS: the smithy, the tannery, the herb racks
    B("tm_smithy", 46, 158, 12)
    B("tm_tannery", 66, 160, 9)
    A("tm_herb_rack", 82, 152, 5)
    A("tm_herb_rack", 88, 160, 5)
    A("tm_woodpile", 34, 168, 5)
    A("tm_supply_cache", 58, 172, 5)
    B("tm_round_den", 76, 176, 8)
    B("tm_round_den", 50, 144, 8)
    # ---- THE TUNNEL MOUTH: the cave lodge, the terrace over it
    B("tm_cave_lodge", 26, 96, 11)
    B("tm_cliff_terrace", 34, 122, 9)
    B("tm_round_den", 18, 124, 8)
    A("furbolg_totem", 10, 100, 5)
    A("furbolg_totem", 10, 116, 5)
    # ---- THE BASIN: the square, the spring, and the deep gate in the floor
    A("tm_great_totem", 120, 108, 16)
    A("tm_bonfire_pit", 120, 122, 5)
    A("tm_drum_circle", 132, 108, 5)
    B("tm_market_stall", 110, 128, 6)
    B("tm_deep_gate", 130, 92, 14)
    A("tm_gate_guard_post", 146, 92, 7)
    A("tm_warning_totem", 116, 90, 6)
    A("tm_fel_crack", 138, 100, 4, solid=False)

    _homes(L)


#: the quarters' homes: every quarter is filled with the Timbermaw's dens and lodges wherever they fit, clear of the
#: streets, the doors and the people, so a quarter reads as a neighbourhood and not a clearing with a building in it
QUARTERS = [(110, 30, 38, 14), (52, 56, 26, 18), (170, 60, 26, 20), (190, 112, 18, 26), (148, 166, 34, 18),
            (60, 160, 32, 18), (28, 108, 20, 24)]
#: the Timbermaw set only (Ashenvale's blue-purple domes clashed with the honey wood)
HOMES = [("tm_round_den", 8), ("fw_timbermaw_lodge", 8), ("tm_cliff_lodge", 9), ("tm_round_den", 7),
         ("fw_timbermaw_lodge", 7), ("tm_cliff_lodge", 8)]
YARD = [("tm_woodpile", 4), ("tm_supply_cache", 4), ("tm_herb_rack", 4), ("furbolg_totem", 5), ("tm_war_banner", 5),
        ("tm_candle_stand", 3)]


#: homes the filler leaves out because they boxed in a strip of ground (see build_layout below)
_SKIP = set()


def _hides(L, name, gx, gy, h):
    """Would this home's PICTURE stand over or behind a building already up? The kit only checks footprints, and
    qa_building_overlap caught 23 dens drawn through their neighbours. Same rectangle rule as that check."""
    from tools.handbuilt_central_barrens import _aspect
    w = max(1, round(h * _aspect(f"{AK.INDEX[name]}{name}.png")))
    x0, y0, x1, y1 = gx - w / 2 - 0.5, gy - h, gx + w / 2 + 0.5, gy + 1
    for lm in L.z.landmarks:
        if "assets/buildings/" not in str(lm.get("sprite_key", "")):
            continue
        ax, ay = float(lm["anchor_x"]), float(lm["anchor_y"])
        bx1, by1 = ax + float(lm["width_tiles"]), ay + float(lm["height_tiles"])
        ox, oy = min(x1, bx1) - max(x0, ax), min(y1, by1) - max(y0, ay)
        if ox > 0 and oy > 0:
            smaller = min((x1 - x0) * (y1 - y0), (bx1 - ax) * (by1 - ay))
            if ox * oy / smaller > 0.25:          # qa_building_overlap allows a third; keep well inside it
                return True
    return False


def _homes(L):
    n = k = 0
    L.home_spots = []
    for qi, (cx, cy, rx, ry) in enumerate(QUARTERS):
        for gy in range(int(cy - ry) + 6, int(cy + ry), 9):     # +6: off the wall, or a den boxes in a strip
            for gx in range(int(cx - rx) + 4, int(cx + rx), 10):
                if ((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2 > 0.85:
                    continue
                if (gx, gy) in _SKIP:
                    continue
                name, h = HOMES[(n + qi) % len(HOMES)]
                if _hides(L, name, gx, gy, h):
                    continue
                if L.b(name, gx, gy, h, nudge=0):
                    n += 1
                    L.home_spots.append((gx, gy, h))
                else:
                    yname, yh = YARD[(k + qi) % len(YARD)]
                    if not _hides(L, yname, gx, gy, yh) and L.p(yname, gx, gy, yh, nudge=0):
                        k += 1
    L.homes = (n, k)

AK.install(sys.modules[__name__])
_kit_build_layout = build_layout  # noqa: F821  (defined by AK.install)


def build_layout():
    """The kit's build, made to keep its ground whole. A den that boxes in a strip of ground leaves sealed tiles, and
    the painter (tools/bake_ashenvale.build_scores) treats any sealed tile as a reason to shade the WHOLE map as
    deep forest: the Hold baked dark brown instead of gold. So any home next to a sealed tile is left out and the
    city is built again, until nothing is sealed."""
    for _ in range(6):
        L = _kit_build_layout()
        sealed = getattr(L, "sealed_land", [])
        if not sealed:
            return L
        bad = {(x, y) for (x, y, h) in getattr(L, "home_spots", [])
               if any(abs(sx - x) <= h + 2 and -h - 2 <= sy - y <= 3 for (sx, sy) in sealed)}
        if not bad:
            return L
        _SKIP.update(bad)
    return L


#: The quarters as named places on the map, so the map labels them and the townsfolk (tools/townsfolk/timbermaw_hold.py)
#: can live in each one. Kyle, 21 Nov 2026: "Also timbermaw hold is dead...for a capital city".
DISTRICTS = [   # (name, x, y, w, h); the Basin is registered last so it wins where the rim's boxes touch it
    ("The Elders' Terrace", 78, 22, 74, 32),
    ("The Long Hall", 14, 38, 58, 50),
    ("The Honey Terraces", 156, 48, 52, 46),
    ("The Carvers' Quarter", 166, 96, 50, 44),
    ("The Market", 124, 144, 72, 40),
    ("The Workshops", 24, 144, 72, 40),
    ("The Tunnel Mouth", 4, 90, 38, 36),
    ("The Basin", 88, 84, 74, 52),
]


def generate_timbermaw_hold():
    L = build_layout()
    for name, x, y, w, h in DISTRICTS:
        L.zone.add_subzone(name, x, y, w, h)
    AK.K.register_baked(L.zone, sys.modules[__name__])
    return L.zone
