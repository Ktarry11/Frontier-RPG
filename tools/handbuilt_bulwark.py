"""
Hand-built The Bulwark (104x80): the Forsaken's wall between Tirisfal and the Plaguelands, and the Order of the
Pale Flame's camp inside it (docs/plaguelands_towns_plan.md).

Kyle, 16 Nov 2026: "The Bulwark, The Pale Watch need to be seperate zones and stand alone towns. Remove Sorrow Hill and
Move these people into the Bulwark. We don't need 2 flight paths in one zone wtf." So the Bulwark is its own map,
and the road from Tirisfal runs straight through it: in at the west gate, out at the east gate onto South WPL. You
can't reach the Plaguelands from Tirisfal without walking down its street.

Two quarters, because the two sides don't love each other:

    the west gate ....... (3,40): the road from Eastern Tirisfal
    the street .......... the King's Road, west to east through the middle
    the Forsaken ........ north of the street: the inn and the bats by the west gate, the store, the barracks
                          and the High Executor, the apothecary's vats and the wagon shed by the east gate
    the Order ........... south of the street, behind its own banners: the hall, the keep and the chapel on
                          a lane of their own, the training yard in front of them, the stable at the east end.
                          They came down from Sorrow Hill when the hill went back to the dead.
    the east gate ....... (100,40): out onto South WPL

One inn (the Forsaken's) and one flight master (the bats). The Order brought its cook and its hawks: Priya feeds the
Order's quarter and Anders's hawks carry its letters, but the beds and the flights are the Forsaken's.

HARD CONTRACTS (world/portal_manager.py)
  portals  (3,40) -> Eastern Tirisfal (84,126);  (100,40) -> Western Plaguelands South (7,84)
  arrivals (6,40), (97,40)
  NPC ids  wpl_bulwark_*, wpl_pf_*, written by tools/sync_wpl_south_npcs.py from NPC_POSITIONS
"""
import sys

from tools import ashenvale_town_kit as AK

KEY = "bulwark"
NAME = "The Bulwark"
DESC = ("The Forsaken's wall where Tirisfal ends and the Plaguelands begin, with the Order of the Pale Flame camped "
        "inside it. Neither side loves the other; both of them love the wall.")
REGION = "Eastern Kingdoms - Lordaeron"
W, H = 104, 80
BAKED_DIR = "assets/tiles/plaguelands/baked_bulwark"
SHEET = "wpl_south"
PORTALS = {(3, 40): "Eastern Tirisfal", (100, 40): "Western Plaguelands South"}
ARRIVALS = [(6, 40), (97, 40)]
START = (8, 40)

SUBZONES = [   # 22 Nov 2026, for the townsfolk
    ("The West Gate", 6, 26, 26, 20),
    ("The Forsaken Row", 32, 14, 36, 22),
    ("The Apothecary's Yard", 68, 14, 30, 24),
    ("The King's Road", 32, 36, 36, 12),
    ("The Order's Lane", 30, 50, 64, 24),
]

ROADS = {
    "street":  ([(2, 40), (14, 40), (30, 40), (52, 40), (74, 40), (88, 40), (101, 40)], 4.0),
    # the Forsaken's lanes, north to their doors
    "inn":     ([(20, 40), (20, 33)], 2.8),
    "store":   ([(36, 40), (36, 33)], 2.6),
    "hall":    ([(58, 40), (58, 31)], 2.8),
    "vats":    ([(80, 40), (80, 33)], 2.6),
    # the Order's lane: down from the street at both ends and along the fronts of its three houses
    "pf_west": ([(30, 40), (30, 50), (30, 66)], 2.8),
    "pf_lane": ([(30, 66), (44, 67), (56, 67), (70, 67), (82, 66)], 3.0),
    "pf_east": ([(82, 40), (82, 52), (82, 66)], 2.8),
}
STREAMS = {}
POOLS = []
PLAZA = (52, 40, 9.0, 4.5)
PAVED_PATCHES = [(20, 34, 5, 3), (58, 32, 6, 3), (56, 67, 12, 3)]
CLEARINGS = [(52, 40, 46, 30), (52, 66, 34, 10), (52, 18, 36, 10), (5, 40, 7, 7), (99, 40, 7, 7)]
DECKS = []
CLEARING_GRASS = False
DECK_PAINT = False
#: the baker's names are Ashenvale's: "corrupt" paints the blight round the vats, "burned" the scorched yard
CORRUPT_PATCHES = [(86, 30, 6, 3)]
BURNED_PATCHES = [(46, 52, 6, 3)]
GRADE = (1.0, 1.05)

NPC_POSITIONS = {
    # ---- the Forsaken
    "wpl_bulwark_commander":     (58, 33),    # High Executor Marla Venn, at the barracks door
    "wpl_bulwark_captain":       (62, 33),    # Deathguard Captain Ludo Vance
    "wpl_bulwark_innkeeper":     (20, 34),    # the inn
    "wpl_bulwark_bat_handler":   (15, 35),    # the bats, by the west gate
    "wpl_bulwark_quartermaster": (36, 34),    # the store
    "wpl_bulwark_apothecary":    (80, 34),    # Apothecary Dorian Vesk, at the vats
    "wpl_bulwark_surgeon":       (72, 35),    # Surgeon Halbert Grey
    "wpl_bulwark_sewer_agent":   (94, 45),    # Deathstalker Ilsa Rook, in the shadow of the east gate
    # ---- the Order of the Pale Flame
    "wpl_pf_flamekeeper":        (56, 68),    # Flamekeeper Rory Callahan, at the keep's door
    "wpl_pf_knight":             (60, 68),    # Ser Aldren Holt
    "wpl_pf_chaplain":           (70, 68),    # Chaplain Odile Marchand, at the chapel
    "wpl_pf_quartermaster":      (42, 68),    # Quartermaster Hollis Burke, at the hall
    "wpl_pf_drillmaster":        (46, 50),    # Drillmaster Kofi Mensah, in the training yard
    "wpl_pf_scout":              (84, 55),    # Scout Agata Wrobel, by the stable
    "wpl_pf_innkeeper":          (25, 63),    # Priya Raman, who cooks for the Order now, at the tents
    "wpl_pf_bat_keeper":         (80, 60),    # Anders Holm and the Order's hawks, by the stable
}
CHESTS = [(96, 22), (24, 63)]


def dress(L):
    A, B, F, V = L.p, L.b, L.f, L.v
    # ---- the gates: the wall's two doors, with the palisade either side of each
    for gx in (8, 96):
        V("pl_bulwark_gate", gx, 36, 8)
        V("pl_bulwark_palisade", gx, 50, 8)
    A("ek_signpost", 14, 45, 4)
    A("ek_signpost", 90, 45, 4)
    # ---- the Forsaken: north of the street
    B("forsaken_inn", 20, 31, 11)
    B("pl_bulwark_bat_roost", 12, 30, 10)
    B("forsaken_general_store", 36, 31, 9)
    B("pl_bulwark_barracks", 58, 30, 9)
    B("forsaken_watch_tower", 46, 30, 12)
    B("pl_bulwark_apothecary", 80, 31, 9)
    B("pl_bulwark_wagon_shed", 88, 26, 7)
    A("pl_cauldron_live", 87, 34, 4)
    A("ek_plague_cauldron", 73, 31, 3)
    A("pl_corpse_sacks", 68, 34, 3)
    A("ek_plague_cart", 28, 34, 3)
    for x in (26, 50, 66, 88):
        A("ek_forsaken_banner", x, 37, 5)
    # the back of the Forsaken quarter: the crypt they keep their own dead in, and graves
    B("forsaken_mausoleum", 30, 18, 9)
    A("gravestone_cluster", 40, 16, 3)
    A("gravestone_cluster", 22, 20, 3)
    B("forsaken_storehouse", 72, 18, 8)
    # ---- the Order of the Pale Flame: south of the street, behind its banners
    for x in (38, 50, 62, 74):
        A("pf_banner", x, 46, 5)
    B("pf_hall", 42, 65, 9)
    B("pf_keep", 56, 65, 11)
    B("pf_chapel", 70, 65, 10)
    B("pf_training_yard", 46, 57, 6)
    B("pf_stable", 90, 60, 7)
    A("pf_weapon_rack", 38, 52, 3)
    A("pf_weapon_rack", 54, 52, 3)
    A("pf_field_tent", 20, 58, 5)
    A("pf_field_tent", 20, 68, 5)
    A("ek_haystack", 84, 60, 3)
    L.edge_canopy(seed=81, names=(("pl_dead_oak", 9), ("pl_blight_pine", 9), ("dead_pine_cluster", 8)))


AK.install(sys.modules[__name__])
