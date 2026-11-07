"""
Hand-built Orgrimmar (200x200): the Horde capital carved into Durotar's red
canyon.  A cliff rim all round, the great south gate, a gate avenue running
north to the central market plaza, and eight walled districts - Valley of
Wisdom, Magic Quarter, Valley of Honor (north); Valley of Strength, Warlock
Quarter (middle); Cleft of Shadow, Craft Row, Stables (south) - each with its
own ground, brick wall, gates and character.

Same recipe as Valley of Trials / Durotar / Razor Hill
(see claude/zone_perfection_playbook.md): this module owns the TILE data and the
analytic landform fields the baker (tools/bake_orgrimmar.py) paints from, so
collision and painting can't drift apart.  Every object is placed at an explicit
coordinate (no random scatter).

HARD CONTRACTS
  portal   (100,197) -> Durotar (65,26)        (world/portal_manager.py)
  portal   Ragefire Chasm entrance in the Cleft of Shadow (RAGEFIRE below)
  NPC ids  are referenced by data/quests/*.json - positions are written back to
           data/npcs/*.json by tools/sync_orgrimmar_npcs.py
"""
import os

import numpy as np
from PIL import Image

from world.tilemap import Tilemap

DP = "assets/tiles/dungeon_props/"
BLD = "assets/buildings/"
ENT = "assets/tiles/cave_entrances/"
OP = "assets/tiles/orgrimmar/props/"
BAKED_DIR = "assets/tiles/orgrimmar_city/baked"
W, H = 200, 200
GATE_PORTAL = (100, 197)

# ------------------------------------------------------------------ districts
# name: (x0, y0, x1, y1, corner radius)  - walled platforms
DISTRICTS = {
    "wisdom":   (12, 12, 56, 60, 5),      # Grommash Hold, shaman trainers, Elder Torgun
    "magic":    (76, 16, 124, 56, 5),     # mage / enchanting / engineering, flight roost
    "honor":    (144, 12, 188, 60, 5),    # hunters, beast masters
    "strength": (12, 76, 56, 122, 5),     # forge, bank, main auction house, warriors
    "warlock":  (144, 76, 188, 122, 5),   # warlocks, demon masters
    "cleft":    (12, 142, 56, 188, 5),    # rogues, Ragefire Chasm
    "craft_w":  (62, 146, 88, 186, 4),    # Craft Row west  (alchemy, leather)
    "craft_e":  (112, 146, 138, 186, 4),  # Craft Row east  (tailoring, supplies)
    "stables":  (144, 142, 188, 188, 5),  # mounts, stable masters
}
PLAZA = (62, 66, 138, 134, 14)            # the central market (open, no wall)

# gates punched through district walls: (cx, cy, axis, width) - axis "x" = the
# gate is in a vertical wall (walk east-west), "y" = in a horizontal wall.
GATES = [
    (56, 36, "x", 7), (34, 60, "y", 7),                          # wisdom
    (100, 56, "y", 9), (76, 36, "x", 6), (124, 36, "x", 6),      # magic
    (144, 36, "x", 7), (166, 60, "y", 7),                        # honor
    (56, 99, "x", 9), (34, 76, "y", 7), (34, 122, "y", 7),       # strength
    (144, 99, "x", 9), (166, 76, "y", 7), (166, 122, "y", 7),    # warlock
    (34, 142, "y", 7), (56, 165, "x", 9),                        # cleft
    (88, 165, "x", 10), (112, 165, "x", 10),                     # craft row, avenue side
    (62, 165, "x", 7), (138, 165, "x", 7),                       # craft row, outer sides
    (75, 146, "y", 7), (125, 146, "y", 7),                       # craft row, plaza side
    (166, 142, "y", 7), (144, 165, "x", 9),                      # stables
]

# painted routes (waypoints, width in tiles)
ROADS = {
    "gate":      ([(100, 199), (100, 186), (100, 150), (100, 134)], 11.0),
    "north":     ([(100, 66), (100, 56)], 8.0),
    "west":      ([(62, 99), (56, 99)], 8.0),
    "east":      ([(138, 99), (144, 99)], 8.0),
    "street_n":  ([(56, 36), (76, 36)], 5.0),
    "street_n2": ([(124, 36), (144, 36)], 5.0),
    "street_w1": ([(34, 60), (34, 76)], 5.0),
    "street_w2": ([(34, 122), (34, 142)], 5.0),
    "street_e1": ([(166, 60), (166, 76)], 5.0),
    "street_e2": ([(166, 122), (166, 142)], 5.0),
    "cleft":     ([(56, 165), (62, 165)], 6.0),
    "stables":   ([(138, 165), (144, 165)], 6.0),
    "ring_w":    ([(75, 134), (75, 146)], 5.0),
    "ring_e":    ([(125, 134), (125, 146)], 5.0),
    # the market's two main lanes
    "plaza_ns":  ([(100, 134), (100, 98), (100, 66)], 8.0),
    "plaza_ew":  ([(62, 99), (100, 99), (138, 99)], 6.0),
    # inside each district: gate -> heart
    "in_wis":    ([(56, 36), (34, 36), (34, 60)], 5.0),
    "in_wis_c":  ([(34, 36), (34, 32)], 10.0),
    "in_mag":    ([(100, 56), (100, 36)], 5.0),
    "in_mag_x":  ([(76, 36), (124, 36)], 5.0),
    "in_hon":    ([(144, 36), (166, 36), (166, 60)], 5.0),
    "in_hon_c":  ([(166, 36), (166, 32)], 9.0),
    "in_str":    ([(34, 76), (34, 122)], 5.0),
    "in_str_x":  ([(56, 99), (34, 99)], 5.0),
    "in_war":    ([(144, 99), (166, 99)], 5.0),
    "in_war_s":  ([(166, 76), (166, 122)], 5.0),
    "in_cle":    ([(34, 142), (34, 184)], 5.0),
    "in_cle_x":  ([(56, 165), (34, 165)], 5.0),
    "in_crw":    ([(75, 146), (75, 165)], 5.0),
    "in_crw_x":  ([(62, 165), (88, 165)], 5.0),
    "in_crw_s":  ([(75, 165), (75, 184)], 4.0),
    "in_cre":    ([(125, 146), (125, 165)], 5.0),
    "in_cre_x":  ([(112, 165), (138, 165)], 5.0),
    "in_cre_s":  ([(125, 165), (125, 184)], 4.0),
    "in_sta":    ([(166, 142), (166, 165), (144, 165)], 5.0),
    "in_sta_s":  ([(166, 165), (166, 186)], 5.0),
}

BUILDING_SCALE = 1.3   # a capital's buildings are bigger than a hamlet's
RIM = 8.0           # cliff band thickness at the map edge
WALL_HALF = 1.0     # district wall half-thickness (tiles)


# ORGRIMMAR WAS BUILT OUT OF STARTER ARCHITECTURE. Kyle, 7 Nov: "you can also
# replace some buildings in org with better Horde buildings if you want. Not
# all, just some..logically."
#
# The capital of the Horde had four generic_tent_a, six generic_hut_*, two
# shamans_hut, an elders_tent and a hide_tanners_hut in it - exactly the set
# claude/orc_building_prompts.md was commissioned to replace, in its own words:
# "Valley-of-Trials starter architecture... a clan that has just landed and is
# living rough, which was right for Durotar and is wrong everywhere else."
# Thirty proper orc buildings have existed since 1 Nov; Orgrimmar got none.
#
# SOME, LOGICALLY - 24 of 61, matched by FUNCTION: the quartermaster gets the
# quartermaster's post, the leatherworker the tannery hall, the stablemaster the
# warbeast stable, the clan hall becomes a war hall. DELIBERATELY LEFT: the
# bazaar's tents and stall rows, because a market of awnings is right; and the
# smugglers' quarter shacks, because a den that looks like a proper building is
# not a den. Rough is the point in both.

def _wob(gx, gy):
    return (0.45 * np.sin(0.37 * gx + 1.3) * np.sin(0.29 * gy + 0.7)
            + 0.30 * np.sin(0.83 * gx + 0.21 * gy + 2.0)
            + 0.25 * np.sin(0.19 * gx - 0.57 * gy + 4.1))


def rrect(gx, gy, x0, y0, x1, y1, r):
    """Signed distance INSIDE a rounded rectangle (tiles; >0 inside)."""
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    hx, hy = (x1 - x0) / 2.0 - r, (y1 - y0) / 2.0 - r
    qx = np.abs(gx - cx) - hx
    qy = np.abs(gy - cy) - hy
    out = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r
    return -out


_TREES = {}


def road_dist(gx, gy, names=None):
    from scipy.spatial import cKDTree
    from tools.terrain_painter import Painter
    q = np.stack([np.ravel(gx), np.ravel(gy)], 1)
    best = None
    for n in (names or ROADS):
        if n not in _TREES:
            pts, w = ROADS[n]
            _TREES[n] = (cKDTree(Painter.spline(pts)), w)
        tree, w = _TREES[n]
        d, _ = tree.query(q)
        e = (w * 0.5) - d
        best = e if best is None else np.maximum(best, e)
    return best.reshape(np.shape(gx))


def gate_extent(gx, gy):
    """>0 inside any gate opening (a clear box through the wall)."""
    best = np.full(np.shape(gx), -99.0)
    for (cx, cy, axis, w) in GATES:
        if axis == "x":      # gate in a vertical wall: opening is w tall, 4 deep
            e = np.minimum(w / 2.0 - np.abs(gy - cy), 3.2 - np.abs(gx - cx))
        else:
            e = np.minimum(w / 2.0 - np.abs(gx - cx), 3.2 - np.abs(gy - cy))
        best = np.maximum(best, e)
    return best


def district_sd(gx, gy, name):
    x0, y0, x1, y1, r = DISTRICTS[name]
    return rrect(gx, gy, x0, y0, x1, y1, r)


def wall_extent(gx, gy):
    """>0 inside a district wall band (gates already cut out)."""
    best = np.full(np.shape(gx), -99.0)
    for n in DISTRICTS:
        sd = district_sd(gx, gy, n)
        best = np.maximum(best, WALL_HALF - np.abs(sd))
    return np.minimum(best, -gate_extent(gx, gy) + 0.0)


def cliff_field(gx, gy):
    """>0 inside the outer rock rim (tiles)."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    edge = np.minimum(np.minimum(gx, 200 - gx), np.minimum(gy, 200 - gy))
    rim = RIM + 2.2 * _wob(gx * 1.3, gy * 1.3) + 1.6 * np.sin(0.21 * gx + 0.17 * gy)
    cl = rim - edge
    # the great south gate cuts the rim
    gate_cut = np.minimum(13.0 - np.abs(gx - 100.0), gy - 176.0)
    return np.minimum(cl, -gate_cut + 0.0)


def fields(gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    return dict(cliff=cliff_field(gx, gy), wall=wall_extent(gx, gy))


_ASPECT = {}


def _aspect(path):
    if path not in _ASPECT:
        with Image.open(path) as im:
            _ASPECT[path] = im.size[0] / im.size[1]
    return _ASPECT[path]


def district_of(x, y):
    for n in DISTRICTS:
        x0, y0, x1, y1, _ = DISTRICTS[n]
        if x0 + 2 <= x <= x1 - 2 and y0 + 2 <= y <= y1 - 2:
            return n
    return None


# ----------------------------------------------------------------- NPC spots
NPC_POSITIONS = {
    # ---- Valley of Wisdom
    "org_thrall": (34, 30),
    "org_elder_2": (18, 28),
    "org_shaman_trainer": (18, 56),
    "org_shaman_trainer_2": (50, 56),
    "org_reagent_vendor": (49, 31),
    "orgrimmar_quartermaster": (21, 44),
    "orgrimmar_provisioner": (47, 45),
    "orgrimmar_elixir_trader": (27, 50),
    "org_scout": (24, 24),
    # ---- Magic Quarter
    "org_mage_trainer": (100, 31),
    "org_enchanter": (86, 32),
    "org_engineer": (114, 32),
    "org_flight_master": (88, 53),
    # ---- Valley of Honor
    "org_hunter": (154, 49),
    "org_stablemaster": (178, 49),
    "org_beast_vendor": (151, 27),
    # ---- Valley of Strength
    "org_smith": (24, 95),
    "org_warrior_trainer": (22, 104),
    "org_weaponsmith": (46, 93),
    # ---- Warlock Quarter
    "org_warlock_trainer": (156, 93),
    "org_summoning_master": (176, 111),
    "orgrimmar_alchemist": (178, 93),
    "org_demonic_vendor": (156, 115),
    # ---- Cleft of Shadow
    "org_rogue_trainer": (20, 159),
    "org_poison_vendor": (48, 159),
    # ---- Craft Row
    "org_alchemist_2": (68, 161),
    "org_leatherworker": (82, 179),
    "org_tailor": (130, 161),
    "org_supplies": (118, 179),
    # ---- Stables
    "org_mount_vendor": (154, 159),
    "org_stable_master_2": (178, 159),
    # ---- the market (four quarters of three stalls)
    "org_market_trader_1": (72, 81),
    "org_market_food": (86, 81),
    "org_market_herbs": (79, 95),
    "org_market_jewelcrafter": (114, 81),
    "org_market_fisher": (128, 81),
    "org_market_furrier": (121, 95),
    "org_market_scribe": (72, 113),
    "org_market_relics": (86, 113),
    "org_market_baker": (79, 127),
    "org_market_florist": (114, 113),
    "org_market_spices": (128, 113),
    "org_market_toys": (121, 127),
}
RECRUITS = {"dan_warrior": (100, 85)}
FORGE = (27, 95)
RAGEFIRE = (34, 184)          # portal tile in the Ragefire mouth (arrival = 2 tiles north)


class Layout:
    def __init__(self):
        self.zone = Tilemap("Orgrimmar", W, H,
                            "The great orcish capital. Towering walls, forges burning, "
                            "war banners flying. A true seat of Horde power.")
        self.z = self.zone
        self.z.region = "Durotar"
        self.skipped = []
        self.placed = 0
        self.npc_xy = []

    def road_clear(self, x, y, margin=0.9):
        return road_dist(np.array([x + 0.5]), np.array([y + 0.5]))[0] < -margin

    def _try(self, path, wt, height, cx, base_y, solid, fraction, road_ok, allow_overlap, portal_ok):
        z = self.z
        ax, ay = cx - wt // 2, base_y - height + 1
        core = []
        rows = max(1, round(height * fraction))
        for y in range(ay, ay + height):
            for x in range(ax, ax + wt):
                if solid is True or (solid == "core" and y >= ay + height - rows
                                     and ax + int(wt * 0.2) <= x < max(ax + int(wt * 0.8), ax + int(wt * 0.2) + 1)):
                    core.append((x, y))
        probe = core or [(cx, base_y)]
        for (x, y) in probe:
            if not (0 <= x < W and 0 <= y < H):
                return "off-map", core, ax, ay
            if z.collision_layer[y][x] is not None and not allow_overlap:
                return "overlaps solid", core, ax, ay
            if any(abs(x - nx) <= 1 and abs(y - ny) <= 1 for nx, ny in self.npc_xy):
                return "NPC", core, ax, ay
            if not portal_ok and abs(x - GATE_PORTAL[0]) <= 2 and abs(y - GATE_PORTAL[1]) <= 2:
                return "portal", core, ax, ay
            if not road_ok and not self.road_clear(x, y, 0.6):
                return "road", core, ax, ay
        return None, core, ax, ay

    def prop(self, name, cx, base_y, height, solid="core", fraction=0.4, road_ok=False,
             path_dir=DP, allow_overlap=False, nudge=2, portal_ok=False):
        path = f"{path_dir}{name}.png" if not name.endswith(".png") else f"{path_dir}{name}"
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        z = self.z
        wt = max(1, round(height * _aspect(path)))
        offs = sorted(((dx, dy) for dx in range(-nudge, nudge + 1) for dy in range(-nudge, nudge + 1)),
                      key=lambda d: (d[0] ** 2 + d[1] ** 2, abs(d[0])))
        first_bad = None
        for (dx, dy) in offs:
            bad, core, ax, ay = self._try(path, wt, height, cx + dx, base_y + dy, solid, fraction,
                                          road_ok, allow_overlap, portal_ok)
            if first_bad is None:
                first_bad = bad
            if bad is None:
                z.add_landmark(path, ax, ay, wt, height, solid=False)
                for (x, y) in core:
                    if z.interaction_layer[y][x] is None:
                        z.collision_layer[y][x] = "landmark"
                self.placed += 1
                return True
        self.skipped.append((name, cx, base_y, first_bad))
        return False

    def bld(self, name, cx, base_y, height, **kw):
        height = int(round(height * BUILDING_SCALE))
        kw.setdefault("path_dir", BLD)
        kw.setdefault("fraction", 0.5)
        return self.prop(name, cx, base_y, height, **kw)

    def row(self, name, xs, base_y, height, **kw):
        return sum(bool(self.prop(name, x, base_y, height, **kw)) for x in xs)


def _terrain(L):
    z = L.z
    z.fill("stone", "base")
    ys, xs = np.mgrid[0:H, 0:W]
    F = fields(xs + 0.5, ys + 0.5)
    rd = road_dist(xs + 0.5, ys + 0.5)
    for y in range(H):
        for x in range(W):
            if F["cliff"][y, x] > 0:
                z.set_tile(x, y, "cliff", "collision")
            elif F["wall"][y, x] > 0:
                z.set_tile(x, y, "wall", "collision")
            elif rd[y, x] > 0:
                z.set_tile(x, y, "path", "base")


def _portals(L):
    z = L.z
    px, py = GATE_PORTAL
    z.collision_layer[py][px] = None
    z.set_tile(px, py, "portal", "interaction")
    rx, ry = RAGEFIRE
    z.collision_layer[ry][rx] = None
    z.set_tile(rx, ry, "portal", "interaction")


def _dress(L):
    p, b, row = L.prop, L.bld, L.row
    z = L.z
    L.npc_xy = list(NPC_POSITIONS.values()) + list(RECRUITS.values()) + [FORGE]
    op = lambda name, cx, by, h, **kw: p(name, cx, by, h, path_dir=OP, **kw)

    # ================================================================ GREAT GATE
    b("orgrimmar_gate", 100, 184, 16, solid=False, road_ok=True, allow_overlap=True, nudge=0)
    for x in (95, 105):
        op("war_banner", x, 176, 7, road_ok=True, nudge=0)
    # the road out: rock arch over the portal
    p("vot_rock_arch", 100, 198, 7, solid=False, road_ok=True, portal_ok=True, allow_overlap=True, nudge=0)
    p("vot_war_banner", 96, 196, 5, portal_ok=True, road_ok=True)
    p("vot_war_banner", 104, 196, 5, portal_ok=True, road_ok=True)
    # gate avenue: banners and braziers between the gate and the market
    for y in (140, 152, 164):
        op("war_banner", 94, y, 7, road_ok=True, nudge=1)
        op("war_banner", 106, y, 7, road_ok=True, nudge=1)
    for y in (146, 158, 170):
        op("orc_brazier", 94, y, 5, road_ok=True, nudge=1)
        op("orc_brazier", 106, y, 5, road_ok=True, nudge=1)

    # ================================================================ VALLEY OF WISDOM
    b("warchiefs_hall", 34, 27, 16)                       # Grommash Hold
    op("orc_brazier", 25, 32, 6)
    op("orc_brazier", 43, 32, 6)
    op("war_banner", 29, 33, 7, road_ok=True)
    op("war_banner", 39, 33, 7, road_ok=True)
    op("skull_tusk_cluster", 22, 24, 6)
    op("skull_tusk_cluster", 46, 24, 6)
    b("orc_totem_court", 18, 25, 8)
    p("vot_hide_rack", 24, 28, 3)
    b("trading_post", 49, 28, 8)                          # reagents
    p("vot_crate_stack", 53, 30, 3)
    b("orc_quartermaster_post", 21, 41, 9)                      # quartermaster
    p("bbc_weapon_rack", 14, 44, 3)
    b("orc_supply_store", 47, 42, 10)                        # provisioner
    p("vot_crate_stack", 52, 45, 3)
    b("orc_healer_house", 27, 47, 9)                        # elixirs
    b("orc_spirit_lodge", 18, 54, 10)
    b("orc_spirit_lodge", 50, 54, 10)
    p("vot_totem_pole", 25, 52, 7)
    p("vot_totem_pole", 43, 52, 7)
    b("orc_watch_tower", 13, 21, 12, nudge=3)
    b("orc_watch_tower", 51, 21, 12, nudge=3)
    op("war_banner", 28, 56, 6, road_ok=True)
    op("war_banner", 40, 56, 6, road_ok=True)

    # ================================================================ MAGIC QUARTER
    b("training_pavilion", 100, 29, 13)
    b("orc_warlock_tower", 86, 36, 11)                         # enchanter
    b("scrapyard_workshop", 114, 29, 8)                   # engineering
    p("rf_tool_rack", 120, 32, 3)
    b("zep_tower_orc", 88, 51, 12)                       # the flight roost
    p("spirit_brazier", 95, 40, 6, road_ok=True)
    p("spirit_brazier", 105, 40, 6, road_ok=True)
    p("bbc_candelabra", 82, 41, 4)
    p("bbc_candelabra", 118, 41, 4)
    p("wizard_desk", 110, 46, 4)
    p("bbc_bookshelf", 116, 50, 5)
    b("orc_officers_house", 106, 52, 9)
    p("bbc_candelabra", 82, 24, 4)
    p("bbc_candelabra", 118, 24, 4)

    # ================================================================ VALLEY OF HONOR
    b("orc_war_hall", 168, 27, 14)
    op("skull_tusk_cluster", 153, 31, 7)
    op("skull_tusk_cluster", 179, 31, 7)
    op("war_banner", 161, 33, 6, road_ok=True)
    op("war_banner", 171, 33, 6, road_ok=True)
    b("orc_kennel_block", 151, 24, 9)                     # beast vendor
    b("orc_barracks_longhouse", 154, 46, 10)                       # hunters
    b("orc_warbeast_stable", 178, 46, 11)                    # stablemaster
    p("vot_archery_target", 150, 54, 4)
    p("vot_archery_target", 158, 56, 4)
    p("kennel_cage_worg", 174, 55, 5)
    p("kennel_cage_empty", 182, 54, 5)
    p("vot_hide_rack", 182, 24, 3)
    b("orc_officers_house", 189, 36, 9)
    b("plain_orc_house_c", 150, 47, 4)
    p("weapon_rack", 182, 38, 4)
    b("orc_watch_tower", 182, 21, 12, nudge=3)

    # ================================================================ VALLEY OF STRENGTH
    b("orc_war_forge", 22, 92, 14)
    p("rf_ore_cart", 16, 98, 4)
    p("rf_tool_rack", 30, 90, 4)
    p("rf_supply_crates", 15, 87, 4)
    b("weapon_rack_shelter", 46, 90, 8)
    b("auction_house", 46, 117, 11)
    b("valley_bank", 22, 117, 11)
    p("vot_training_dummy", 16, 108, 4)
    p("vot_training_dummy", 22, 111, 4)
    p("vot_training_dummy", 28, 108, 4)
    p("bbc_weapon_rack", 14, 103, 4)
    p("vot_archery_target", 46, 107, 4)
    op("orc_brazier", 38, 94, 5)
    op("orc_brazier", 38, 105, 5)

    # ================================================================ WARLOCK QUARTER
    p("bbc_summon_circle", 176, 108, 7)
    b("crypt_chapel", 156, 90, 12)
    b("forsaken_house_small", 178, 90, 8)
    b("orc_supply_store", 156, 112, 10)
    p("bbc_warlock_desk", 150, 108, 4)
    for (x, y) in [(162, 84), (170, 84), (162, 114), (170, 114)]:
        p("bbc_fel_brazier", x, y, 6)
    p("bbc_fel_pylon", 184, 100, 6)
    p("bbc_fel_pylon", 148, 100, 6)
    p("rf_skull_spears", 184, 82, 5)
    p("rf_skull_spears", 148, 82, 5)
    p("bbc_idol", 184, 118, 6)

    # ================================================================ CLEFT OF SHADOW
    b("forsaken_house_medium", 20, 156, 10)               # rogues
    b("orc_healer_house", 48, 156, 9)                        # poisons
    p("rf_prison_cage", 44, 150, 5)
    b("generic_shack_b", 46, 174, 5)                      # a smuggler's den
    p("rf_supply_crates", 40, 178, 4)
    p("rf_cult_banner", 14, 162, 6)
    p("rf_cult_banner", 54, 162, 6)
    p("bbc_idol", 15, 178, 5)
    b("generic_hut_a", 18, 170, 5)
    p("rf_skull_spears", 14, 152, 5)
    p("bbc_candelabra", 30, 150, 4)
    p("bbc_candelabra", 38, 150, 4)
    # Ragefire Chasm: the lava-mouth in the south wall

    rx, ry = RAGEFIRE
    p("cave_entrance_banners", 34, 187, 14, path_dir=ENT, solid=False, road_ok=True,
      allow_overlap=True, nudge=0, portal_ok=True)
    for x in list(range(29, 31)) + list(range(38, 40)):    # rock shoulders either side of the mouth
        for y in range(183, 187):
            if z.collision_layer[y][x] is None:
                z.collision_layer[y][x] = "landmark"
    p("rf_lava_fissure", 25, 181, 6)
    p("rf_lava_fissure", 43, 181, 6)
    p("rf_obsidian_spikes", 22, 175, 7)
    p("rf_obsidian_spikes", 46, 175, 7)
    p("rf_brazier", 30, 177, 6)
    p("rf_brazier", 38, 177, 6)
    p("rf_steam_vent", 16, 168, 5)
    p("rf_steam_vent", 52, 170, 5)
    p("rf_skull_spears", 28, 171, 5)
    p("rf_skull_spears", 40, 171, 5)

    # ================================================================ CRAFT ROW
    b("orc_healer_house", 68, 158, 9)                      # alchemist
    p("vot_crate_stack", 70, 164, 3)
    b("orc_tannery_hall", 82, 182, 11)                     # leatherworker
    p("vot_hide_rack", 81, 170, 3)
    p("vot_hide_rack", 85, 171, 3)
    p("rf_tool_rack", 68, 178, 4)
    b("bazaar_stall_row", 130, 158, 8)                    # tailor
    p("vot_hide_rack", 133, 152, 3)
    b("supply_cache_shed", 118, 176, 5)                   # supplies
    p("rf_supply_crates", 132, 176, 4)
    p("vot_broken_cart", 120, 152, 4)
    b("generic_shack_a", 68, 172, 5)
    b("generic_hut_a", 82, 147, 5)
    p("vot_crate_stack", 70, 183, 3)
    b("plain_orc_house_b", 132, 172, 4)
    b("orc_officers_house", 118, 154, 9)
    p("vot_crate_stack", 124, 184, 3)
    p("rf_ore_cart", 134, 183, 4)

    # ================================================================ STABLES
    b("taurajo_stables", 154, 156, 10)                    # mounts
    b("orc_warbeast_stable", 178, 156, 11)                  # stable master
    p("kennel_cage_worg", 150, 173, 5)
    p("kennel_cage_worg", 158, 176, 5)
    p("kennel_cage_empty", 180, 173, 5)
    p("kennel_cage_worg", 186, 177, 5)
    b("taurajo_stables", 154, 182, 9)
    b("orc_warbeast_stable", 176, 184, 11)
    b("generic_hut_a", 160, 172, 5)
    for x in (170, 174, 178, 182, 186):
        p("vot_palisade", x, 169, 3, nudge=1)
    op("skull_tusk_cluster", 150, 148, 6)
    op("skull_tusk_cluster", 184, 150, 6)
    p("vot_hide_rack", 172, 150, 3)
    p("rf_supply_crates", 160, 166, 4)
    p("vot_crate_stack", 174, 180, 3)

    # ================================================================ THE MARKET
    stalls = [("bazaar_stall_row", 68, 78, 8), ("trading_post", 88, 78, 8), ("mixed_trading_post", 79, 92, 8),
              ("generic_tent_a", 114, 78, 8), ("bazaar_stall_row", 128, 78, 8), ("trading_post", 121, 92, 8),
              ("generic_tent_b", 72, 110, 8), ("mixed_trading_post", 86, 110, 8), ("bazaar_stall_row", 79, 124, 8),
              ("trading_post", 114, 110, 8), ("generic_tent_a", 128, 110, 8), ("mixed_trading_post", 121, 124, 8)]
    for (n, x, y, h) in stalls:
        b(n, x, y, h)
    # the Warchief's trophy at the crossing of the two lanes
    op("skull_tusk_cluster", 100, 103, 14, road_ok=True, nudge=0)
    for (x, y) in [(93, 95), (107, 95), (93, 106), (107, 106)]:
        op("orc_brazier", x, y, 5, road_ok=True, nudge=0)
    for (x, y) in [(70, 86), (94, 86), (106, 86), (130, 86), (70, 118), (94, 118), (106, 118), (130, 118)]:
        p("vot_crate_stack", x, y, 3)
    op("war_banner", 96, 71, 7, road_ok=True)
    op("war_banner", 104, 71, 7, road_ok=True)
    op("war_banner", 96, 130, 7, road_ok=True)
    op("war_banner", 104, 130, 7, road_ok=True)
    p("vot_war_drum", 66, 99, 4, road_ok=True)
    p("vot_war_drum", 134, 99, 4, road_ok=True)
    b("well_house", 90, 99, 5, road_ok=True)
    # The second well is gone. It sat on the trading post and every move I gave
    # it was shoved back by the placer's nudge, which is the placer saying the
    # only free ground nearby IS the post. The Drag already has a well twenty
    # tiles west; a plaza with one well is not missing anything.

    # ================================================================ WALL GATES
    for (cx, cy, off, w) in [(56, 36, "e", 7), (144, 36, "w", 7), (100, 56, "s", 9),
                             (56, 99, "e", 9), (144, 99, "w", 9), (56, 165, "e", 9),
                             (144, 165, "w", 9), (88, 165, "e", 10), (112, 165, "w", 10)]:
        h = w // 2 + 1
        if off in "ew":
            xx = cx + (3 if off == "e" else -3)
            op("war_banner", xx, cy - h, 6, nudge=1)
            op("war_banner", xx, cy + h + 2, 6, nudge=1)
        else:
            op("war_banner", cx - h, cy + 4, 6, nudge=1)
            op("war_banner", cx + h, cy + 4, 6, nudge=1)

    # fixed interaction tile (smelting) beside the smith
    fx, fy = FORGE
    z.collision_layer[fy][fx] = None


def build_layout():
    L = Layout()
    _terrain(L)
    _portals(L)
    _dress(L)
    return L


def shape_preview(path, scale=5):
    ys, xs = np.mgrid[0:H, 0:W]
    F = fields(xs + 0.5, ys + 0.5)
    img = np.zeros((H, W, 3), np.uint8)
    img[:] = (200, 125, 80)
    for n, (x0, y0, x1, y1, r) in DISTRICTS.items():
        sd = district_sd(xs + 0.5, ys + 0.5, n)
        img[sd > 0] = (170, 110, 80)
    px0, py0, px1, py1, pr = PLAZA
    img[rrect(xs + 0.5, ys + 0.5, px0, py0, px1, py1, pr) > 0] = (225, 150, 90)
    rd = road_dist(xs + 0.5, ys + 0.5)
    img[(rd > 0)] = (235, 200, 120)
    img[F["wall"] > 0] = (110, 70, 60)
    img[F["cliff"] > 0] = (60, 40, 38)
    img[GATE_PORTAL[1], GATE_PORTAL[0]] = (255, 0, 255)
    Image.fromarray(img).resize((W * scale, H * scale), Image.NEAREST).save(path)


def register_baked(zone, baked_dir=BAKED_DIR, chunk=20):
    """Register the baked painting as ground + water + obstacle chunks."""
    for cy in range(0, H, chunk):
        for cx in range(0, W, chunk):
            fn = f"{baked_dir}/ground_{cx}_{cy}.jpg"
            if not os.path.exists(fn):
                raise FileNotFoundError(f"{fn} - run python3 tools/bake_orgrimmar.py")
            w, h = min(chunk, W - cx), min(chunk, H - cy)
            zone.add_ground_chunk(fn, cx, cy, w, h)
            zone.ground_chunks[-1]["exact"] = True
            zone.add_water_chunk(fn, cx, cy, w, h)
            zone.add_obstacle_chunk(fn, cx, cy, w, h)


def generate_orgrimmar():
    L = build_layout()
    register_baked(L.zone)
    return L.zone
