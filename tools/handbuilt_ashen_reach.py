"""
Hand-built The Ashen Reach (190x170): the north half of Tempest Isle, levels 55-58.

Kyle, 7 Nov 2026: "the north map is bigger than the south map". It is - 190x170 against the
Shallows' 170x150 - and that size difference is load-bearing: it is why the Shallows needed the
islets to make up its area, and it is why the Reach can carry a town, a dungeon door and the works
without any of them crowding.

ARCHETYPE: THE WORKING SIDE. The Shallows is where you land; this is where the Ashclaim actually
operates. Same island, same sea, but the jungle thins into cooled lava, scoria and steam fissures
as the ground climbs, and the only green left is in the lee of things.

=========================================================================================
THE SAME TWO RULES AS THE SHALLOWS, BECAUSE IT IS THE SAME ISLAND
=========================================================================================

  1. IT IS AN ISLAND. No rim rock, no mountain ring. The sea closes every edge but the SOUTH,
     which is not an edge at all - it is the border with the Shallows, and the island runs across
     it. Kyle, 10 Nov: "the ENTIRE thing should be surrounded by water bro? No mountains, this is
     an ISLAND".
  2. THE VOLCANO IS ONE ROUND MASSIF ON THE BORDER, not a wall. Its centre sits just BELOW this
     map's bottom edge - the mirror of the Shallows, where it sits just above the top edge - so
     the two halves of the mountain line up across the seam and the player walks round the same
     rock from either side.

WHAT THIS ZONE HAS THAT THE SHALLOWS DOES NOT:

    THE EMBERDEEP'S DOOR, on the volcano's NORTH face. This is the whole reason the dungeon is
    55-58 and not 52-55: you need the high zone to reach it, exactly as the brief specifies.
    CINDERWHARF, north-east, its own zone off a gate tile. Goblin wharf welded to a Dark Iron hold.
    THE WORKS - a smelter, a pump house and a mine head the Ashclaim has got running again, each
    a small hub under constant elemental attack. "The underwriter wants the foundry" as content.

PLACES (north is up; Tempest Shallows lies south across the border):
    S      THE TWO PASSES: round the volcano's west and east flanks, back down to the Shallows.
    SC     THE VOLCANO, northern half, with THE EMBERDEEP'S DOOR on its north face.
    NE     CINDERWHARF'S GATE: the town, its own zone.
    C      THE WORKS: smelter, pump house, mine head, strung along the trunk road.
    NW     THE SCOURED COAST: ash fields running to a black-sand shore.

HARD CONTRACTS (world/portal_manager.py) - filled in after the coast is measured, never guessed.
Prop rule (Kyle): less is more; logical for the room; a few centrepieces.
Earth references scale with zone level - this is the HIGH half of the isle, so it carries
noticeably more of them than the Shallows, and still only in what people say.
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools import tempest_isle_coast as C
from tools.tirisfal_kit import wob, lobe

KEY = "ashen_reach"
NAME = "The Ashen Reach"
DESC = ("The north half of Tempest Isle: ash fields and steam under the volcano's far face, "
        "with the Ashclaim's works strung across them and a goblin wharf on the north-east coast.")
REGION = "Tempest Isle"
W, H = C.W, C.REACH_H
BAKED_DIR = "assets/tiles/ashen_reach/baked"
IS_TOWN = False
BASE_TILE = "grass"
SEED = 557

RU = "assets/tiles/ruins/"

#: Filled in below from measured land. Declared here so the module reads top-down.
PORTALS = {(58, 156): "Tempest Shallows",
           (176, 156): "Tempest Shallows",
           (176, 98): "Cinderwharf",
           (115, 132): "The Emberdeep"}
ARRIVALS = [(58, 153), (176, 153), (173, 98), (115, 129)]
START = (58, 150)

# ---- the coast: NOT DEFINED HERE ------------------------------------------------------------------
# tools/tempest_isle_coast.py owns the island, and this zone reads its northern half. That is the
# whole point: the Shallows reads the southern half of the SAME curve, so the land either side of
# the border is one row of one coastline rather than two modules' guesses. See that file's header
# for what went wrong when each zone had its own.
#
# The volcano sits exactly ON the seam, so it is defined there too - a mountain half-owned by two
# modules drifts the moment one of them is edited.
VOLCANO_R = C.VOLCANO_R
#: The Emberdeep's door, in ISLAND space: a bite out of the skirt's north face so the forecourt in
#: front of it is walkable. A portal tile inside solid rock is a player who cannot reach their
#: own dungeon.
DOOR_ISLAND = (C.VOLCANO[0], C.SEAM_Y - 30.0, 11.0)


def land_field(gx, gy):
    return C.land(KEY, gx, gy)


def sea_field(gx, gy):
    return -land_field(gx, gy)


def deck_field(gx, gy):
    """No jetty in this zone - the wharf is inside Cinderwharf, which is its own map."""
    return np.full(np.shape(gx), -99.0)


# ---- roads ------------------------------------------------------------------------------------------
# The trunk runs from the WEST pass, north past the works, and east to Cinderwharf's gate. The
# volcano road branches off it to the Emberdeep's door. The east pass hangs off the trunk's far end.
ROADS = {
    "trunk":   ([(58, 158), (54, 134), (62, 112), (82, 94), (112, 82), (146, 82), (172, 90),
                 (176, 98)], 3.2),
    "east":    ([(146, 82), (168, 112), (176, 158)], 2.6),        # round the volcano's east flank
    "volcano": ([(112, 82), (114, 106), (115, 128)], 2.6),        # in to the Emberdeep's door
    "works":   ([(62, 112), (80, 122), (96, 128)], 2.4),          # the smelter and the mine head
    "coast":   ([(54, 134), (42, 110), (44, 82), (56, 58)], 2.2),  # out to the scoured coast
}
_RS = K.RoadSet(ROADS)
road_dist = _RS.dist


def paved(gx, gy):
    """Worn stone: the Emberdeep's forecourt, and the smelter yard."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    door = lobe(gx, gy, 115.0, 130.0, 10.0, 7.0) + 0.5 * wob(gx, gy)
    yard = lobe(gx, gy, 80.0, 122.0, 8.0, 6.0) + 0.5 * wob(gx, gy)
    gate = lobe(gx, gy, 184.0, 96.0, 7.0, 6.0) + 0.5 * wob(gx, gy)
    return np.maximum.reduce([door, yard, gate]) - 1.2




def volcano_field(gx, gy):
    """>0 inside the volcano's skirt, with the Emberdeep's door bitten out of its north face."""
    return C.volcano(KEY, gx, gy, DOOR_ISLAND)


def cliff_field(gx, gy):
    """NO RIM: the sea is the edge, so the only cliff here is the volcano."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    rock = volcano_field(gx, gy)
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    rock = np.where(sea_field(gx, gy) > -1.0, np.minimum(rock, -0.5), rock)
    return rock


def fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    sea = sea_field(gx, gy)
    cliff = cliff_field(gx, gy)
    # No archipelago on this side - the shelf is narrow and the ocean is deep, which is part of
    # why the Shallows got the islets and this zone got open ground instead.
    deep = sea - 3.0
    return dict(cliff=np.where(sea > 0, -99.0, cliff),
                shallow=sea, deep=deep, deck=deck_field(gx, gy))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


SUBZONES = [
    # NO TWO OF THESE OVERLAP (14 Nov 2026): the Works shared a 20x30 block with the Emberdeep
    # Approach, so the yard's own engine house spawned fire spirits, and the Coast, Flats and
    # Cinderwharf Gate each bled into a neighbour.
    ("The Scoured Coast", 34, 58, 40, 48),
    ("The Ashclaim Works", 62, 106, 36, 36),
    ("The Emberdeep Approach", 98, 112, 40, 40),
    ("The Cinder Flats", 100, 60, 60, 40),
    ("Cinderwharf Gate", 160, 80, 48, 36),
]

# ---- baker config (tools/bake_tempest.py) --------------------------------------------------------
# The mirror of the Shallows' mix: there, 40% jungle grass. Here, dry and rocky carry the map and
# green only survives in the lee of things. The green stops at the border because the MIX changes,
# not because the materials do - the same trick Arathi plays against Hillsbrad.
# ROCK CARRIES THIS ZONE, NOT ORANGE. At dry 0.36 the hardpan painted a desert across the middle
# of a volcanic island - the material is a Tanaris texture and it behaves like one at volume. It is
# scorch now: small, weak, and near the mountain. Cooled lava and scree do the heavy lifting.
# UN'GORO CRATER, not a cinder field. Kyle, 10 Nov: "Part of the reach should be jungle. THINK
# UNGORO CRATER - like jungle + volcano". That is the whole look: lush green everywhere, and a
# burnt ridge sitting in the middle of it. The ash is a RING at the volcano's foot, not the
# zone's ground cover - the contrast is the point, and ash everywhere destroys it.
#
# (The first pass went the other way and read as jungle with no volcano at all, because "rocky"
# pairs mossy stone with basalt and the painter mixes them - the moss wins. `ash` and `cinder`
# are unmixed basalt and scoria, which is why the ring can be black against green.)
BASE = {"grass": 0.30, "forest": 0.22, "rocky": 0.16, "shore": 0.14, "dry": 0.06}
PAINT = {
    # The volcano sits at (115,160) with a 36-tile skirt, so the ash ring is drawn around that
    # and fades outward. Strongest at the foot, gone by the time the coast is in sight.
    # A TIGHT RING at the volcano's foot (it sits at (115,160), skirt 36). Strong where the rock
    # meets the ground and gone within a dozen tiles, so the jungle runs right up to the burn.
    "ash":    [(115, 142, 46, 14, 1.0), (84, 140, 18, 10, 0.8), (146, 140, 18, 10, 0.8),
               (115, 124, 30, 8, 0.55)],
    "cinder": [(115, 132, 26, 8, 0.7), (94, 134, 14, 7, 0.5), (136, 134, 14, 7, 0.5)],
    "dry":    [(115, 116, 22, 8, 0.35), (88, 122, 14, 7, 0.3), (142, 122, 14, 7, 0.3)],
    "rocky":  [(115, 146, 42, 18, 1.0), (76, 146, 26, 13, 0.9), (156, 146, 26, 13, 0.9),
               (44, 104, 22, 14, 0.8), (184, 96, 12, 9, 0.7), (100, 110, 32, 16, 0.7),
               (140, 112, 26, 14, 0.7)],
    "grass":  [(60, 90, 32, 24, 1.0), (164, 102, 28, 20, 0.95), (86, 46, 26, 20, 0.95),
               (128, 70, 30, 20, 0.9), (44, 120, 20, 14, 0.8), (182, 78, 18, 12, 0.8)],
    "forest": [(58, 88, 22, 15, 0.95), (160, 100, 20, 14, 0.9), (88, 44, 20, 14, 0.9),
               (126, 66, 22, 14, 0.85), (46, 118, 14, 10, 0.75)],
    "shore":  [(38, 92, 10, 14, 0.6), (80, 22, 14, 7, 0.6), (196, 110, 10, 12, 0.55),
               (62, 46, 12, 7, 0.55), (186, 78, 10, 7, 0.5)],
    "earth":  [(80, 122, 8, 6, 0.9), (115, 130, 8, 6, 0.9), (184, 96, 7, 5, 0.8)],
    "gravel": [(58, 156, 7, 5, 0.7), (176, 156, 7, 5, 0.7), (96, 128, 7, 5, 0.6)],
    "marsh":  [(40, 104, 9, 7, 0.5)],
}
COBBLE = [(115, 130, 9, 6, 0.9), (80, 122, 7, 5, 0.85), (184, 96, 6, 5, 0.8)]

# ---- NPC spots --------------------------------------------------------------------------------------
# One per thing the zone does, spread across 190x170 rather than clustered at the road head.
NPC_POSITIONS = {
    "ar_works_foreman": (80, 120),         # the smelter yard
    "ar_works_enginewright": (96, 126),    # the mine head
    "ar_door_warden": (115, 126),          # outside the Emberdeep, where nobody wants to stand
    "ar_coast_surveyor": (44, 86),         # the scoured coast
    "ar_flats_scout": (134, 86),           # the cinder flats
    "ar_gate_factor": (170, 102),           # the goblin factor at Cinderwharf's gate
    "ar_works_assayer": (72, 116),         # the weigh shed
    "ar_works_powderman": (87, 130),       # the red shed, away from everything
    "ar_works_volcanologist": (78, 106),   # the instrument hut on the north edge
}

CHESTS = [(56, 60), (44, 100), (70, 140), (150, 120), (178, 118), (96, 48), (148, 72)]

PALMS = [("ek_dead_oak", 7, 0.30), ("ek_thorn_bush", 4, 0.42), ("assets/tiles/shimmering_flats/props/tan_dead_palm.png", 7, 0.24)]
FOREST = dict(seed=71, count=44, rim=12, thorn=12, names=[
    ("ek_dead_oak", 7, 0.34), ("ek_thorn_bush", 4, 0.44), ("assets/tiles/shimmering_flats/props/tan_dead_palm.png", 7, 0.22)])


def dress(L):
    p, b = L.prop, L.bld
    ENT = T.ENT

    # ---- the Emberdeep's door, cut into the volcano's north face -----------------------------------
    # The portal tile (95,120) and the column below it stay clear of solid props. A cave mouth
    # drawn ON the arrival tile is a player standing inside a boulder - Boulder'gor shipped that way.
    p(ENT + "cave_entrance_plain.png", 115, 136, 9, solid=False, nudge=0, road_ok=True,
      allow_overlap=True)
    for (x, y) in ((106, 136), (124, 136)):
        p("ek_web_boulder", x, y, 6)
    p("ek_signpost", 115, 122, 4)
    p("ek_forsaken_banner", 121, 126, 6)

    # ---- the works: the reason the underwriter is on this island ------------------------------------
    b("orc_supply_store", 78, 116, 10, nudge=2)
    b("orc_watch_tower", 88, 122, 11, nudge=2)
    p("ek_farm_cart", 74, 126, 4)
    p("ek_scarlet_crates", 86, 114, 3)
    b("orc_smokehouse", 100, 122, 9, nudge=2)
    p("ek_signpost", 66, 112, 4)

    # ---- the two passes, back down to the Shallows ---------------------------------------------------
    p("ek_signpost", 62, 148, 4)
    p("ek_signpost", 172, 148, 4)
    for (x, y) in ((68, 146), (74, 138), (170, 142), (164, 134)):
        p("ek_web_boulder", x, y, 6)

    # ---- Cinderwharf's gate, north-east ---------------------------------------------------------------
    # The gate to the town, moved inland to (176,98) on 14 Nov 2026. It was at (186,96) on the
    # waterline, and the only way to fit the gatehouse there put half of it in the sea (Kyle: "that
    # gate over the sea is bad"). Base three below the portal, which is the kit's minimum.
    b("orc_great_gatehouse", 176, 101, 12, solid=False, road_ok=True, nudge=0)
    # One tower on the shore side of the moved gate; the inland side is the road.
    b("orc_watch_tower", 186, 104, 11, nudge=2)
    p("ek_signpost", 166, 101, 4)

    # ---- the scoured coast, north-west ----------------------------------------------------------------
    p(RU + "ruin_stone_ring.png", 46, 90, 5, solid=False)
    p("ek_dead_oak", 48, 104, 6)
    p("ek_web_boulder", 44, 76, 5)

    # ---- the cinder flats -----------------------------------------------------------------------------
    T.grove(L, 52, 84, 6, 5, 6, PALMS, seed=7)
    T.grove(L, 164, 102, 6, 5, 5, PALMS, seed=8)
    for (x, y) in ((100, 56), (142, 100), (74, 70)):
        p("ek_web_boulder", x, y, 5)
    b("ek_wayshrine", 130, 94, 5, nudge=2)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_ashen_reach():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/ashen_reach_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
