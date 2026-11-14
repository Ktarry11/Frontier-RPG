"""The hidden open-world maps (world/hidden_zones.py, kind "skull").

SPOILERS. Kyle, 14 Nov 2026: "I don't want to see as I want these to be secrets." Nothing here
says how to find them; the doors that lead here are picked by tools/build_secrets.py.

The brief, in Kyle's words: "For hidden zones, they can be new NEW transition zones too. These new
zones will still have the level range but maybe a skull next to them", "when I say new zones. I
mean actually new maps", "Open world will be 2.5x hp and 2.5x damage", "Quests can be in the zone,
but max of like 3 or 4....they're not quest hubs but they CAN have elite quests. I want the wonder
of exploring....and for good measure....I WANT to be rewarded for exploring."

Each is one painted map (playbook section 3), built from a SPEC below by the same recipe as Echo
Isles: analytic landforms -> tile grid AND painting from the same functions, so they can't drift.

  The Saltgrave        grey sandbars and drowned barrows in a cold sea
  The Glasswaste       a sealed red canyon where the sand has been fired to glass
  The Weeping Pines    a dead pine wood round a black mere, in a fog that never lifts

Every map's way out is its one portal; arriving puts you two tiles north of it.
"""
import math
import os

import numpy as np
from PIL import Image

from world.tilemap import Tilemap

DP = "assets/tiles/dungeon_props/"
BAKED = "assets/tiles/hidden/{}/baked"
HF = "assets/tiles/haunted_forest/props/"
ASHX = "assets/tiles/ashenvale_corruption/props/"
STV = "assets/tiles/stranglethorn/props/"
CP = "assets/tiles/coastal_props/"
VEG = "assets/tiles/vegetation/"
NG = "assets/tiles/naga_dungeon/"


def wob(gx, gy, ph=0.0):
    return (0.55 * np.sin(gx * 0.21 + gy * 0.13 + ph) + 0.35 * np.sin(gx * 0.47 - gy * 0.31 + 1.7 * ph)
            + 0.22 * np.sin(-gx * 0.83 + gy * 0.71 + 0.6 * ph))


def ell(gx, gy, cx, cy, rx, ry, rot=0.0):
    dx, dy = gx - cx, gy - cy
    if rot:
        r = math.radians(rot)
        c, s = math.cos(r), math.sin(r)
        dx, dy = c * dx + s * dy, -s * dx + c * dy
    return (1.0 - np.sqrt((dx / rx) ** 2 + (dy / ry) ** 2)) * min(rx, ry)


def seg_dist(gx, gy, pts):
    best = np.full(np.shape(gx), 99.0)
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        dx, dy = bx - ax, by - ay
        t = np.clip(((gx - ax) * dx + (gy - ay) * dy) / (dx * dx + dy * dy or 1), 0.0, 1.0)
        best = np.minimum(best, np.hypot(gx - ax - t * dx, gy - ay - t * dy))
    return best


# ===================================================================================== SPECS
SPECS = {}

# THE SALTGRAVE. Sandbars in a grey sea, three barrows the sea came over, and a fourth, the King's,
# out on its own to the north. Shallows join them; everywhere else is cold deep water.
SPECS["The Saltgrave"] = dict(
    slug="saltgrave", W=100, H=86, region="Arathi East", seed=931,
    desc="A drowned barrow-field out past the last island: grey sand, grey water, and the old dead "
         "of the highlands, who never stopped guarding what was buried with them.",
    mode="islands", shore_w=3.0,
    land=[(50, 74, 15, 6, 0), (24, 54, 12, 8, 15), (78, 50, 12, 8, -20), (49, 42, 9, 5, 0),
          (51, 16, 14, 9, 5), (14, 26, 5, 4, 0), (86, 24, 6, 4, 0)],
    flats=[(50, 60, 4.5, 9), (36, 48, 9, 4.5), (64, 46, 9, 4.5), (50, 30, 4.5, 9),
           (19, 38, 4, 9), (82, 36, 4, 9)],
    rocks=[(22, 50, 3.4, 2.6), (80, 46, 3.2, 2.6), (51, 12, 4.2, 3.0), (60, 20, 1.8, 1.6),
           (40, 18, 1.8, 1.6)],
    roads=[],
    portal=(50, 78),
    giver=("hz_saltgrave_maud", (43, 73)),
    subzones=[("The Landing Bar", 34, 66, 32, 16), ("The West Barrow", 10, 44, 28, 20),
              ("The East Barrow", 64, 40, 28, 20), ("The Middle Bar", 38, 36, 22, 12),
              ("The King's Barrow", 34, 4, 34, 24)],
    materials={"land": ("echo_isles/materials/echo_wetsand", None),
               "grass": ("hillsbrad/materials/hb_dry", None),
               "barrow": ("hillsbrad/materials/hb_rocky", "hillsbrad/materials/hb_moss_rock"),
               "water_s": ("hillsbrad/materials/hb_sea_shallow", None),
               "water_d": ("hillsbrad/materials/hb_sea_deep", None),
               "rock": ("hillsbrad/materials/hb_cliff_a", "hillsbrad/materials/hb_cliff_b")},
    regions={"grass": [(24, 56, 8, 5), (78, 52, 8, 5), (51, 19, 10, 6)],
             "barrow": [(22, 51, 6, 4), (80, 47, 6, 4), (51, 13, 7, 5)]},
    tint=(0.86, 0.90, 0.95), dark=0.10,
    props=[
        ("stv_bleached_log", STV, 44, 76, 2, False), ("stv_fish_bones", STV, 57, 75, 2, False),
        ("stv_driftwood", STV, 38, 73, 2, False), ("skull_pile", DP, 26, 57, 3, False),
        ("sarcophagus", DP, 17, 55, 3, "core"), ("bbc_skull_pile", DP, 75, 54, 3, False),
        ("sarcophagus", DP, 84, 52, 3, "core"), ("stv_broken_mast", STV, 70, 48, 4, "core"),
        ("grotto_pirate_skeletons", DP, 46, 43, 3, False), ("stv_chain_heap", STV, 53, 43, 2, False),
        ("crypt_mausoleum", HF, 51, 22, 5, "core"), ("skull_pile", DP, 44, 21, 3, False),
        ("skull_pile", DP, 58, 21, 3, False), ("stv_shells", STV, 14, 27, 2, False),
        ("stv_boat_wreck", STV, 86, 25, 3, "core"),
    ],
)

# THE GLASSWASTE. A canyon the Kolkar never went into: whatever burned here burned hot enough to
# turn the sand to glass. Red walls all round, mesas inside, and fire still walking about.
SPECS["The Glasswaste"] = dict(
    slug="glasswaste", W=96, H=80, region="Durotar", seed=932,
    desc="A sealed red canyon behind Durotar's cliffs, where something burned so hot the sand "
         "turned to glass. It hasn't finished burning.",
    mode="canyon", shore_w=1.5,
    lakes=[], flats=[],
    open=[(48, 70, 9, 6, 0), (30, 50, 16, 11, 20), (64, 46, 15, 10, -15), (50, 30, 7, 5, 0),
          (58, 14, 20, 8, 5), (18, 27, 8, 7, 0), (82, 26, 7, 9, 10)],
    passes=[([(48, 70), (40, 60), (32, 52)], 6), ([(48, 70), (58, 58), (64, 48)], 5),
            ([(30, 50), (28, 36), (20, 28)], 5), ([(64, 46), (56, 34), (52, 26), (56, 16)], 6),
            ([(64, 46), (78, 36), (82, 26), (74, 14)], 5)],
    rocks=[(30, 48, 4, 3), (66, 44, 3, 4), (58, 14, 3, 2), (24, 56, 2, 2)],
    roads=[([(48, 74), (44, 62), (36, 52), (30, 40), (40, 32), (52, 26), (58, 16)], 2.2)],
    portal=(48, 76),
    giver=("hz_glasswaste_durek", (53, 70)),
    subzones=[("The Scorched Mouth", 34, 62, 28, 16), ("The Shard Fields", 8, 30, 36, 30),
              ("The Kiln Rise", 52, 30, 38, 30), ("Blister's Hollow", 40, 4, 40, 22)],
    materials={"land": ("vot_cluster/vot_clay_a", "vot_cluster/vot_clay_pebbles"),
               "glass": ("vot_cluster/vot_cinder", None),
               "dune": ("vot_cluster/vot_dune", None),
               "bone": ("vot_cluster/vot_bonesand", None),
               "road": ("vot_cluster/vot_hardpan", None),
               "water_s": ("vot_cluster/vot_water_shallow", None),
               "water_d": ("vot_cluster/vot_water_deep", None),
               "rock": ("vot_cluster/vot_cliff_a", None)},
    regions={"glass": [(24, 44, 14, 12), (60, 12, 14, 8), (76, 44, 10, 9)],
             "dune": [(44, 56, 12, 8)], "bone": [(60, 12, 6, 4)]},
    tint=(1.04, 0.92, 0.86), dark=0.06,
    props=[
        ("vot_dead_tree", DP, 40, 70, 4, "core"), ("vot_beast_ribcage", DP, 58, 66, 3, False),
        ("rf_lava_fissure", DP, 22, 40, 3, False), ("rf_obsidian_spikes", DP, 16, 52, 3, "core"),
        ("rf_lava_fissure", DP, 30, 50, 3, False), ("bbc_obsidian_spikes", DP, 66, 36, 3, "core"),
        ("rf_steam_vent", DP, 78, 46, 3, False), ("vot_mesa_pillar", DP, 58, 44, 5, "core"),
        ("rf_golem_husk", DP, 74, 28, 4, "core"), ("vot_beast_ribcage", DP, 56, 10, 3, False),
        ("rf_lava_pool", DP, 66, 12, 4, False), ("vot_scorpid_burrow", DP, 46, 18, 3, False),
        ("bbc_red_stalagmites", DP, 36, 22, 4, "core"),
    ],
)

# THE WEEPING PINES. A pine wood that died standing up, round a mere so still it shows the trees
# that aren't there any more. Fog, and something in the water that weeps.
SPECS["The Weeping Pines"] = dict(
    slug="weeping_pines", W=96, H=86, region="Silverpine North", seed=933,
    desc="A dead pine wood round a black mere, hidden in the folds of Silverpine. The fog never "
         "lifts, and on still nights something in the water weeps.",
    mode="canyon", shore_w=2.2,
    lakes=[(50, 40, 12, 8, 10), (72, 58, 4.5, 3, 0)],
    flats=[],
    open=[(48, 74, 12, 8, 0), (28, 52, 13, 16, 10), (50, 40, 21, 15, 10), (72, 58, 11, 9, -10),
          (28, 18, 12, 8, -15), (58, 14, 17, 8, 5), (82, 32, 7, 10, 0), (14, 34, 6, 7, 0)],
    passes=[([(48, 74), (36, 64), (30, 56)], 6), ([(48, 74), (62, 66), (70, 60)], 5),
            ([(28, 40), (26, 28)], 6), ([(38, 18), (48, 14)], 6), ([(70, 18), (80, 26)], 5),
            ([(82, 40), (78, 50)], 5), ([(20, 38), (16, 36)], 4)],
    rocks=[(22, 22, 3, 2), (86, 30, 2, 3)],
    roads=[([(48, 80), (46, 70), (34, 60), (28, 44), (28, 28), (40, 16), (58, 14), (74, 20), (82, 32)], 2.0)],
    portal=(48, 82),
    giver=("hz_pines_ilsabet", (55, 76)),
    subzones=[("The Fogbound Track", 30, 64, 36, 20), ("The Weeping Mere", 32, 26, 38, 30),
              ("The Hanging Wood", 8, 28, 24, 36), ("The Stillwater Shrine", 40, 6, 40, 20),
              ("The Drowned Copse", 60, 46, 26, 20)],
    materials={"land": ("silverpine/materials/sp_needle_mulch", "silverpine/materials/sp_pine_floor"),
               "moss": ("silverpine/materials/sp_cursed_ground", None),
               "bog": ("silverpine/materials/sp_bog_mud", "silverpine/materials/sp_peat"),
               "road": ("silverpine/materials/sp_gravel", None),
               "water_s": ("silverpine/materials/sp_pool_shallow", None),
               "water_d": ("silverpine/materials/sp_pool_deep", None),
               "rock": ("silverpine/materials/sp_cliff_a", "silverpine/materials/sp_rock_wall")},
    regions={"moss": [(20, 44, 12, 18), (60, 14, 14, 7)], "bog": [(52, 40, 20, 14), (70, 56, 10, 7)]},
    tint=(0.84, 0.90, 0.92), dark=0.14,
    props=[
        ("dead_pine_cluster", HF, 30, 74, 6, "core"), ("dead_pine_cluster", HF, 64, 72, 6, "core"),
        ("dead_pine_cluster", HF, 14, 36, 6, "core"), ("dead_pine_cluster", HF, 22, 54, 6, "core"),
        ("dead_pine_cluster", HF, 82, 46, 6, "core"), ("dead_pine_cluster", HF, 30, 14, 6, "core"),
        ("dead_pine_cluster", HF, 74, 10, 6, "core"), ("dead_pine_cluster", HF, 86, 60, 6, "core"),
        ("twisted_root_arch", HF, 26, 32, 5, "core"), ("bog_reeds_cluster", HF, 38, 44, 3, False),
        ("bog_reeds_cluster", HF, 62, 34, 3, False), ("bog_reeds_cluster", HF, 66, 60, 3, False),
        ("ashx_spirit_brazier", ASHX, 44, 14, 4, "core"), ("ashx_spirit_brazier", ASHX, 58, 14, 4, "core"),
        ("burned_house_ruin", HF, 74, 64, 6, "core"), ("crypt_mausoleum", HF, 51, 11, 5, "core"),
        ("vot_fallen_log", DP, 40, 62, 2, False),
        # the wood itself: dead pines standing in clumps all round the mere
        ("dead_pine_cluster", HF, 20, 46, 6, "core"), ("dead_pine_cluster", HF, 36, 50, 5, "core"),
        ("dead_pine_cluster", HF, 18, 62, 5, "core"), ("dead_pine_cluster", HF, 40, 30, 5, "core"),
        ("dead_pine_cluster", HF, 62, 28, 5, "core"), ("dead_pine_cluster", HF, 66, 48, 5, "core"),
        ("dead_pine_cluster", HF, 78, 62, 5, "core"), ("dead_pine_cluster", HF, 56, 76, 5, "core"),
        ("dead_pine_cluster", HF, 38, 78, 5, "core"), ("dead_pine_cluster", HF, 22, 22, 5, "core"),
        ("dead_pine_cluster", HF, 66, 14, 5, "core"), ("dead_pine_cluster", HF, 84, 38, 5, "core"),
        ("dead_pine_cluster", HF, 12, 34, 5, "core"), ("dead_pine_cluster", HF, 34, 18, 5, "core"),
    ],
)


# ============================================================================== THE LANDFORMS
def fields(spec, gx, gy):
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    W, H = spec["W"], spec["H"]
    if spec["mode"] == "islands":
        land = np.full(np.shape(gx), -30.0)
        for n, (cx, cy, rx, ry, rot) in enumerate(spec["land"]):
            land = np.maximum(land, ell(gx, gy, cx, cy, rx, ry, rot) + 0.9 * wob(gx, gy, n * 1.3))
        flat = np.full(np.shape(gx), -30.0)
        for (cx, cy, rx, ry) in spec["flats"]:
            flat = np.maximum(flat, ell(gx, gy, cx, cy, rx, ry))
        wet = -land
        deep = np.minimum(wet - spec["shore_w"], -flat)
        edge = np.full(np.shape(gx), -9.0)
    if spec["mode"] == "canyon":
        # ground where the chambers and the passes between them are; rock everywhere else
        opn = np.full(np.shape(gx), -30.0)
        for n, (cx, cy, rx, ry, rot) in enumerate(spec["open"]):
            opn = np.maximum(opn, ell(gx, gy, cx, cy, rx, ry, rot) + 0.9 * wob(gx, gy, n * 1.7))
        for n, (pts, w) in enumerate(spec["passes"]):
            opn = np.maximum(opn, w / 2 - seg_dist(gx, gy, pts) + 0.5 * wob(gx * 1.3, gy * 1.3, n))
        e = np.minimum.reduce([gx, W - gx, gy, H - gy])
        opn = np.minimum(opn, e - 2.5)
    if spec["mode"] != "islands":
        lake = np.full(np.shape(gx), -30.0)
        for n, (cx, cy, rx, ry, rot) in enumerate(spec["lakes"]):
            lake = np.maximum(lake, ell(gx, gy, cx, cy, rx, ry, rot) + 0.7 * wob(gx, gy, n * 2.1))
        land = -lake
        wet = lake
        flat = np.full(np.shape(gx), -30.0)
        for (cx, cy, rx, ry) in spec["flats"]:
            flat = np.maximum(flat, ell(gx, gy, cx, cy, rx, ry))
        deep = np.minimum(wet - spec["shore_w"], -flat)
        edge = -opn
    rock = edge
    for n, (cx, cy, rx, ry) in enumerate(spec["rocks"]):
        rock = np.maximum(rock, ell(gx, gy, cx, cy, rx, ry) + 0.5 * wob(gx * 1.6, gy * 1.6, n))
    rd = np.full(np.shape(gx), 99.0)
    for pts, w in spec["roads"]:
        rd = np.minimum(rd, seg_dist(gx, gy, pts) - w / 2)
    rock = np.where(rd < 1.2, np.minimum(rock, -0.6), rock)
    # the way in and out is never rock, and neither is the column you arrive on
    px, py = spec["portal"]
    near_portal = np.maximum(np.abs(gx - (px + 0.5)) - 2.5, np.abs(gy - (py - 1.0)) - 4.0)
    rock = np.where(near_portal < 0, np.minimum(rock, -0.6), rock)
    return dict(land=land, wet=wet, deep=deep, rock=rock, road=-rd)


def tile_kind(spec, gx, gy):
    """0 land, 1 shallow, 2 deep, 3 rock."""
    f = fields(spec, gx, gy)
    kind = np.zeros(np.shape(gx), int)
    kind[f["wet"] > 0] = 1
    kind[f["deep"] > 0] = 2
    kind[f["rock"] > 0] = 3
    return kind


# =============================================================================== THE TILE MAP
_ASPECT = {}


def _aspect(path):
    if path not in _ASPECT:
        with Image.open(path) as im:
            _ASPECT[path] = im.size[0] / im.size[1]
    return _ASPECT[path]


def build_zone(name):
    spec = SPECS[name]
    W, H = spec["W"], spec["H"]
    z = Tilemap(name, W, H, spec["desc"])
    z.region = spec["region"]
    z.is_town = False
    z.hidden_skull = True
    z.fill("grass", "base")
    ys, xs = np.mgrid[0:H, 0:W]
    gx, gy = xs + 0.5, ys + 0.5
    f = fields(spec, gx, gy)
    kind = tile_kind(spec, gx, gy)
    for y in range(H):
        for x in range(W):
            k = kind[y, x]
            if k == 1:
                z.set_tile(x, y, "shallow_water", "base")
            elif k == 2:
                z.set_tile(x, y, "deep_water", "base")
            elif k == 3:
                z.set_tile(x, y, "dirt", "base")
                z.set_tile(x, y, "cliff", "collision")
            elif f["road"][y, x] > 0:
                z.set_tile(x, y, "path", "base")
            elif spec["mode"] == "islands" and f["land"][y, x] < 1.5:
                z.set_tile(x, y, "sand", "base")
    px, py = spec["portal"]
    z.collision_layer[py][px] = None
    z.set_tile(px, py, "portal", "interaction")
    gid, (gx0, gy0) = spec["giver"]
    npcs = [(gx0, gy0)]
    # props: guarded, never on water, a portal, the giver or the road
    placed, skipped = 0, []
    for (pname, pdir, cx, by, h, solid) in spec["props"]:
        path = f"{pdir}{pname}.png"
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        wt = max(1, round(h * _aspect(path)))
        ax, ay = cx - wt // 2, by - h + 1
        core = []
        if solid:
            rows = max(1, round(h * 0.4))
            for yy in range(ay + h - rows, ay + h):
                for xx in range(ax + int(wt * 0.2), max(ax + int(wt * 0.8), ax + int(wt * 0.2) + 1)):
                    core.append((xx, yy))
        bad = None
        for (xx, yy) in core or [(cx, by)]:
            if not (0 <= xx < W and 0 <= yy < H):
                bad = "off-map"
            elif kind[yy, xx] in (1, 2):
                bad = "water"
            elif abs(xx - px) <= 2 and abs(yy - py) <= 4:
                bad = "portal"
            elif any(abs(xx - nx) <= 1 and abs(yy - ny) <= 1 for nx, ny in npcs):
                bad = "npc"
            elif f["road"][yy, xx] > -0.6:
                bad = "road"
        if bad:
            skipped.append((pname, cx, by, bad))
            continue
        z.add_landmark(path, ax, ay, wt, h, solid=False)
        for (xx, yy) in core:
            if z.interaction_layer[yy][xx] is None:
                z.collision_layer[yy][xx] = "landmark"
        placed += 1
    z.add_subzone(name, 0, 0, W, H)
    for (sn, x, y, w, h) in spec["subzones"]:
        z.add_subzone(sn, x, y, w, h)
    _seal_unreachable(z, (px, py - 2))
    z.props_skipped = skipped
    return z


def _seal_unreachable(z, start):
    from collections import deque
    seen = {start}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < z.width and 0 <= n[1] < z.height and n not in seen and z.is_walkable(*n):
                seen.add(n)
                q.append(n)
    sealed = 0
    for y in range(z.height):
        for x in range(z.width):
            if (x, y) not in seen and z.is_walkable(x, y) and (x, y) != start:
                if z.base_layer[y][x] == "shallow_water":
                    z.set_tile(x, y, "deep_water", "base")
                else:
                    z.set_tile(x, y, "cliff", "collision")
                sealed += 1
    z.sealed = sealed


def register_baked(zone, baked_dir, chunk=20):
    for cy in range(0, zone.height, chunk):
        for cx in range(0, zone.width, chunk):
            fn = f"{baked_dir}/ground_{cx}_{cy}.jpg"
            if not os.path.exists(fn):
                return False
            w, h = min(chunk, zone.width - cx), min(chunk, zone.height - cy)
            zone.add_ground_chunk(fn, cx, cy, w, h)
            zone.ground_chunks[-1]["exact"] = True
            zone.add_water_chunk(fn, cx, cy, w, h)
            zone.add_obstacle_chunk(fn, cx, cy, w, h)
    return True


#: each map's portal tile (its way out, and where its secret door leads)
PORTALS = {n: s["portal"] for n, s in SPECS.items()}

#: hidden zones whose door is not a room in a wall but stands on a secret island
#: (tools/build_secrets.BAKED_ISLANDS), keyed to the island's map
ISLAND_DOORS = {"The Saltgrave": "Arathi East"}

#: quest givers: npc id -> (zone, x, y)
GIVERS = {s["giver"][0]: (n, *s["giver"][1]) for n, s in SPECS.items()}


def generate_all():
    out = {}
    for name, spec in SPECS.items():
        z = build_zone(name)
        register_baked(z, BAKED.format(spec["slug"]))
        out[name] = z
    return out
