"""
Hand-built Kael's Bastion (96x84): the Crimson Codex's holdfast in the Crystalline Underdark.

TOWN ARCHETYPE: THE STACKS.  The Codex are cataloguers, and their worst instinct is that a thing properly
written down is a thing controlled - so when they built a town they built an INDEX. One spine runs the length of
it, and parallel galleries come off that spine in ranks, like shelves off the spine of a book. Nothing here grew;
every line of it was decided in advance by people who find disorder personally offensive.

(Brill is a high street, Crossroads a plus-shaped avenue, Camp Taurajo a ring camp, Razor Hill a walled hilltop,
Astranaar a moon-pool terrace, Splintertree a lumber stockade, Ratchet a crescent harbour, the Sepulcher a
terraced crypt-keep that climbs, Tarren Mill two banks of a millrace. None of them is a town whose plan is an
ORGANISING SYSTEM imposed on rock, and that is the one a library full of blood elves would build.)

The galleries are NUMBERED, not named - the Codex ran out of names in the first year and refused to invent more
on principle. Everyone who actually lives here has given them nicknames anyway, which the archivists have twice
tried to stamp out by memorandum.

THE BUILDINGS ARE HUE-SHIFTED. The sprites here are the `bud_*` set: the generic crimson-and-gold blood elf
architecture recoloured to arcane violet by tools/hue_shift_buildings.py, because the Bastion is the same
architecture under crystal light rather than sunlight. The `be_*` originals stay untouched for Silvermoon.

HARD CONTRACT (world/portal_manager.py): portal (48, 78) <-> The Crystalline Underdark (72, 80).
Prop rule (Kyle): less is more; logical for the room; a few centrepieces.
"""
import sys

import numpy as np

from tools import town_kit as K
from tools import tirisfal_kit as T
from tools.tirisfal_kit import wob, superlobe

KEY = "kaels_bastion"
#: Must match the registry name in create_all_zones - portal_manager keys on zone.name.
NAME = "Kael's Bastion"
DESC = ("The Crimson Codex's holdfast: one spine, four numbered galleries, and Dalaran stone reassembled by "
        "people who are excellent at magic and indifferent at masonry.")
REGION = "Eastern Kingdoms - Alterac"
W, H = 96, 92
BAKED_DIR = "assets/tiles/kaels_bastion/baked"
IS_TOWN = True
BASE_TILE = "dirt"
SEED = 1041

UDP = "assets/tiles/underdark/props/"

PORTALS = {(48, 86): "The Crystalline Underdark"}
ARRIVALS = [(48, 82)]
START = (48, 81)

#: The spine, and four galleries off it. Straight lines on purpose - a town laid out as an index does not
#: meander, and the contrast with the Underdark's wandering open country outside is the point.
ROADS = {
    "spine": ([(48, 88), (48, 70), (48, 54), (48, 38), (48, 24)], 3.6),
    "g1":    ([(16, 72), (48, 72), (80, 72)], 2.6),     # Gallery One - "the Mudroom"
    "g2":    ([(14, 58), (48, 58), (82, 58)], 2.6),     # Gallery Two - "the Long Shelf"
    "g3":    ([(14, 44), (48, 44), (82, 44)], 2.6),     # Gallery Three
    "g4":    ([(18, 30), (48, 30), (78, 30)], 2.4),     # Gallery Four - the magisters'
}
PLAZA = (48, 58, 9.0, 5.5)        # the crossing of spine and Long Shelf: the only open ground in the town
HALL = (48, 20, 12.0, 6.5)        # the Codex Hall's forecourt, closing the spine

_RS = K.RoadSet(ROADS)
road_dist = _RS.dist


def paved(gx, gy):
    out = np.full(np.shape(gx), -9.0)
    for cx, cy, rx, ry in (PLAZA, HALL):
        r = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
        out = np.maximum(out, (1 - r) * min(rx, ry))
    return out


def cliff_field(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    # The town occupies a rectangular bay cut out of the cavern wall. Squarer than a natural chamber, because
    # the Codex squared it off - but the rock they could not be bothered to move is still rock.
    floor = np.maximum.reduce([
        superlobe(gx, gy, 48.0, 54.0, 40.0, 34.0, 3.2),
        superlobe(gx, gy, 48.0, 80.0, 22.0, 12.0, 2.8),      # the gate bay
        superlobe(gx, gy, 48.0, 20.0, 28.0, 14.0, 2.8),      # the Hall's forecourt
    ])
    floor = floor + 1.3 * wob(gx * 0.5, gy * 0.5) + 0.6 * wob(gx, gy)
    floor = np.maximum(floor, road_dist(gx, gy) + 2.4)
    rock = -floor
    edge = np.minimum.reduce([gx, W - gx, gy, H - gy])
    rock = np.maximum(rock, (4.0 - edge) * 1.3 + 0.3 * wob(gx * 1.3, gy * 1.3))
    rock = np.where(road_dist(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    rock = np.where(paved(gx, gy) > -0.4, np.minimum(rock, -0.5), rock)
    return rock


def fields(gx, gy):
    gx = np.asarray(gx, float)
    return dict(cliff=cliff_field(gx, gy), shallow=np.full(gx.shape, -99.0),
                deep=np.full(gx.shape, -99.0), deck=np.full(gx.shape, -9.0))


def tile_kind(gx, gy):
    return K.kind_from_fields(fields(gx, gy), np.shape(gx))


SUBZONES = [
    ("The Codex Hall", 22, 8, 52, 20),
    ("Gallery Four", 12, 24, 72, 14),
    ("Gallery Three", 10, 38, 76, 12),
    ("Gallery Two", 10, 52, 78, 12),
    ("Gallery One", 12, 66, 72, 12),
]

# ---- baker config (read by tools/bake_underdark_zone.py) --------------------------------------------------------
BASE = {"cavern": 0.62, "fungal": 0.10, "moss": 0.10, "shard": 0.18}
PAINT = {
    "dalaran": [(48, 54, 12, 8, 1.0), (48, 16, 13, 8, 1.0), (48, 40, 10, 5, 0.7)],
    "shard":   [(14, 48, 10, 20, 0.8), (84, 48, 10, 20, 0.8)],
    "moss":    [(20, 68, 8, 6, 0.7), (78, 68, 8, 6, 0.7)],
    "crystal": [(88, 30, 8, 7, 0.8), (10, 32, 7, 6, 0.7)],
    "glow":    [(48, 66, 8, 4, 0.5)],
}
COBBLE = [(48, 54, 12, 8, 0.95), (48, 16, 13, 8, 0.95),
          (48, 66, 26, 4, 0.7), (48, 40, 26, 4, 0.7), (48, 26, 24, 4, 0.6)]

# ---- NPC spots ---------------------------------------------------------------------------------------------------
#: The Codex, by function. Positions feed tools/sync_underdark_npcs.py in the NPC pass.
NPC_POSITIONS = {
    # the gate and Gallery One - the working end, closest to the door
    "kb_gate_warden": (44, 80),
    "kb_quartermaster": (30, 72),
    "kb_porter": (62, 72),
    "kb_stablemaster": (74, 70),
    # Gallery Two, the Long Shelf - trade and the inn
    "kb_innkeeper": (34, 58),
    "kb_trader": (60, 58),
    "kb_smith": (24, 58),
    "kb_reagent_seller": (70, 58),
    # Gallery Three - the practical disciplines
    "kb_alchemist": (30, 44),
    "kb_enchanter": (64, 44),
    "kb_cartographer": (40, 44),
    "kb_naturalist": (56, 44),
    # Gallery Four - the magisters
    "kb_magister": (34, 30),
    "kb_archivist": (62, 30),
    # the Codex Hall
    "kb_codex_master": (48, 24),
    "kb_hall_adjutant": (40, 26),
    "kb_hall_sentinel": (56, 26),
}
#: The last two were nominally in corner rock; the kit relocates a chest to the nearest walkable tile, so
#: these are the positions it actually used. Recorded rather than left to be re-derived every build.
CHESTS = [(14, 76), (84, 76), (16, 26), (82, 28)]

FOREST = dict(seed=113, count=18, rim=6, thorn=0, names=[
    (UDP + "ud_shroom_small.png", 4, 0.36),
    (UDP + "ud_shroom_cluster_blue.png", 6, 0.36),
])


def dress(L):
    p, b = L.prop, L.bld
    U = lambda n: UDP + n + ".png"   # noqa: E731

    # ================= THE GATE: the only way in, and the Codex check everyone ===============================
    b("bud_gatehouse", 58, 84, 8, nudge=1)
    p(U("ud_arcane_brazier"), 40, 84, 5)
    p(U("ud_codex_banner"), 42, 78, 6)
    p(U("ud_codex_banner"), 54, 78, 6)

    # ================= GALLERY ONE - "the Mudroom": stores, stable, everything that arrives dirty ===========
    b("bud_storehouse", 22, 77, 6, nudge=1)
    b("bud_house_small", 34, 77, 6, nudge=1)
    b("bud_guard_post", 60, 77, 6, nudge=1)
    b("bud_stable", 74, 77, 6, nudge=1)
    p(U("ud_codex_crates"), 28, 67, 3)
    p(U("ud_dig_scaffold"), 82, 68, 7)
    p(U("ud_specimen_rack"), 66, 67, 4)

    # ================= GALLERY TWO - "the Long Shelf": trade, and the town's one open square ================
    b("bud_inn", 28, 64, 8, nudge=1)
    b("bud_shop", 64, 64, 7, nudge=1)
    b("bud_smithy", 18, 54, 7, nudge=1)
    b("bud_townhouse", 78, 54, 7, nudge=1)
    b("bud_market_stall", 66, 53, 5, nudge=1)
    p(U("ud_arcane_brazier"), 42, 54, 5)
    p(U("ud_arcane_brazier"), 54, 54, 5)

    # ================= GALLERY THREE: the practical disciplines =============================================
    b("bud_alchemist", 24, 50, 7, nudge=1)
    b("bud_sanctum", 68, 50, 7, nudge=1)
    b("bud_house_medium", 34, 39, 6, nudge=1)
    b("bud_house_medium", 62, 39, 6, nudge=1)
    p(U("ud_survey_tripod"), 44, 40, 4)
    p(U("ud_specimen_rack"), 52, 40, 4)

    # ================= GALLERY FOUR: the magisters, and they chose the quiet end ============================
    b("bud_spire", 22, 36, 9, nudge=1)
    b("bud_library", 70, 36, 8, nudge=1)
    b("bud_observatory", 42, 26, 8, nudge=1)
    b("bud_arcane_well", 58, 26, 6, nudge=1)
    p(U("ud_rune_stone"), 30, 25, 6)
    p(U("ud_rune_stone"), 66, 25, 6)

    # ================= THE CODEX HALL: closing the spine, because an index has a last page ==================
    b("bud_great_hall", 48, 16, 11, solid="core", fraction=0.5, nudge=0)
    b("bud_grand_spire", 26, 18, 11, nudge=1)
    b("bud_temple", 70, 18, 9, nudge=1)
    p(U("ud_codex_banner"), 38, 22, 6)
    p(U("ud_codex_banner"), 58, 22, 6)

    # ================= the salvage they built it from, left where it was dragged =============================
    b("bud_ruined_tower", 14, 48, 8, nudge=1)
    b("bud_wall_arch", 84, 48, 7, nudge=1)
    b("bud_obelisk", 22, 22, 8, nudge=1)
    p(U("ud_broken_column"), 12, 64, 7)
    p(U("ud_fallen_arch"), 82, 32, 6)


def build_layout():
    return T.build(sys.modules[__name__])


def generate_kaels_bastion():
    return T.generate(sys.modules[__name__])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/kaels_bastion_shape.png"
    T.shape_preview(sys.modules[__name__], out)
    print(out)
