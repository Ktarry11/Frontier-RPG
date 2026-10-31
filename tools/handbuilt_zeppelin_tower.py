"""
Hand-built Zeppelin Tower (64x64): a goblin-engineered, orc-garrisoned mooring tower, seen from above as a timber
CROSS floating over the ground far below.

ARCHETYPE: THE CROSS (hub + four arms).  Kyle's call: it is the continent's transport node, so every arm is a gate.
    N arm  - airship berth 1  -> the other tower's north berth (Orgrimmar <-> Undercity shuttle)
    S arm  - the stair head   -> down to the ground (Durotar / Eastern Tirisfal)
    E arm  - airship berth 2  - RESERVED (Grom'gol / Stranglethorn route), empty berth for now
    W arm  - airship berth 3  - RESERVED (Thunder Bluff route), empty berth for now
One octagonal hub in the middle holds the engine works and four searchlight towers; each arm is a 9-wide gangway ending in a
15-wide docking apron.  Everything outside the deck is a sheer drop (collision "cliff", painted as haze over the far ground).

The SAME layout serves both towers; the Tirisfal twin gets its own skin (see below):
    SITES["Zeppelin Tower"]           the Durotar tower outside Orgrimmar (N berth -> Undercity)
    SITES["Undercity Zeppelin Tower"] its Tirisfal twin (N berth -> Orgrimmar)
Painting: tools/bake_zeppelin_tower.py [--skin orc|forsaken] -> assets/tiles/zeppelin_tower/baked / baked_forsaken (same deck, re-skinned:
weathered grey planks, blighted ground, purple landing pads and Forsaken banners on the Tirisfal twin).

HARD CONTRACTS (world/portal_manager.py): portal tiles N (32,6)  S (32,58); reserved E (58,32)  W (6,32).
You land 3 tiles inside the arm from each portal: N (32,9)  S (32,55); reserved E (55,32)  W (9,32).
portal_manager registers N (32,11) / S (32,57) because the transition lands 2 tiles north of the registered tile.
Prop rule (Kyle): less is more; logical for the spot; a few centrepieces.
"""
import os

import numpy as np
from PIL import Image

from world.tilemap import Tilemap

BAKED_DIR = "assets/tiles/zeppelin_tower/baked"
W, H = 64, 64
CX = CY = 32.5                 # centre of tile (32,32)
HALF_ARM = 4.5                 # arms are 9 tiles wide
HALF_APRON = 7.5               # aprons are 15 tiles wide
HUB_R = 10.0
TIP0, TIP1 = 4.0, 61.0         # deck spans tiles 4..60
APRON_DEPTH = 6.0

PORTALS = {"N": (32, 6), "S": (32, 58), "E": (58, 32), "W": (6, 32)}
ARRIVALS = {"N": (32, 9), "S": (32, 55), "E": (55, 32), "W": (9, 32)}
#: Which arms are cut as real gates, PER SITE. It used to be one global tuple, which was fine while
#: both towers were the same four-arm hub - but Grom'gol's tower is the far end of one route and has
#: no third berth to offer, so a live E arm there would be a portal tile standing over a drop.
LIVE_PORTALS = ("N", "S", "E")

SITES = {
    "Zeppelin Tower": dict(region="Durotar", slug="zeppelin_tower", skin="orc", baked=BAKED_DIR,
                           live=("N", "S", "E"),
                           desc="A creaking tower of lashed timber outside Orgrimmar's gates. "
                                "Its airships run to the Undercity, and the berths to either side are waiting for more routes."),
    "Undercity Zeppelin Tower": dict(region="Eastern Kingdoms - Lordaeron", slug="undercity_zeppelin_tower",
                                     skin="forsaken", baked=BAKED_DIR + "_forsaken", live=("N", "S"),
                                     desc="The Horde's mooring tower above the Tirisfal glades, bolted together by goblin hands. "
                                          "Airships from Orgrimmar dock at the north berth."),
    # The far end of the Stranglethorn run. Same deck, same orc skin, and only two live arms: the
    # berth the airship comes in on and the stair down into the camp. Kyle, 29 Oct: "zepplin tower
    # outside grom'gol" - it was inside the palisade and it had no business being there. A mooring
    # tower is a thing you walk out to.
    "Grom'gol Zeppelin Tower": dict(region="Eastern Kingdoms - Stranglethorn",
                                    slug="gromgol_zeppelin_tower", skin="jungle",
                                    baked=BAKED_DIR + "_jungle",
                                    live=("N", "S"),
                                    desc="A goblin mooring tower bolted to the jungle canopy above Grom'gol. "
                                         "The airship from Durotar comes in on the north berth; the stair "
                                         "goes down into the camp."),
}

# zeppelin master per site (vendors.json carries the stock; position lives here)
MASTER_XY = (36, 10)


def deck_field(gx, gy):
    """>0 on the planked deck (tiles).  Pure rectangles + one octagon, so it follows the tile grid exactly."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    dx, dy = np.abs(gx - CX), np.abs(gy - CY)
    bar_v = np.minimum(HALF_ARM - dx, np.minimum(gy - TIP0, TIP1 - gy))
    bar_h = np.minimum(HALF_ARM - dy, np.minimum(gx - TIP0, TIP1 - gx))
    hub = np.minimum(np.minimum(HUB_R - dx, HUB_R - dy), (HUB_R * 1.4 - dx - dy) / 1.4142)
    n_ap = np.minimum(HALF_APRON - dx, np.minimum(gy - TIP0, TIP0 + APRON_DEPTH - gy))
    s_ap = np.minimum(HALF_APRON - dx, np.minimum(gy - (TIP1 - APRON_DEPTH), TIP1 - gy))
    w_ap = np.minimum(HALF_APRON - dy, np.minimum(gx - TIP0, TIP0 + APRON_DEPTH - gx))
    e_ap = np.minimum(HALF_APRON - dy, np.minimum(gx - (TIP1 - APRON_DEPTH), TIP1 - gx))
    return np.maximum.reduce([bar_v, bar_h, hub, n_ap, s_ap, w_ap, e_ap])


def fields(gx, gy):
    return dict(deck=deck_field(gx, gy))


def arm_of(x, y):
    """Which arm a deck tile belongs to ('H' hub) - used by the baker for plank direction."""
    dx, dy = abs(x + 0.5 - CX), abs(y + 0.5 - CY)
    if max(dx, dy) <= HUB_R - 1.0 or (dx + dy) <= HUB_R * 1.4 - 1.0:
        return "H"
    return "V" if dy > dx else "Hz"


_ASPECT = {}


def _aspect(path):
    if path not in _ASPECT:
        with Image.open(path) as im:
            _ASPECT[path] = im.size[0] / im.size[1]
    return _ASPECT[path]


class Layout:
    def __init__(self, site):
        cfg = SITES[site]
        self.site = site
        self.zone = Tilemap(site, W, H, cfg["desc"])
        self.z = self.zone
        self.z.region = cfg["region"]
        self.skipped = []
        self.placed = 0
        ys, xs = np.mgrid[0:H, 0:W]
        self.deck = deck_field(xs + 0.5, ys + 0.5) > 0
        # keep-out tiles: portals, arrivals, the master, and the centre lane of every arm
        self.keep = set(PORTALS.values()) | set(ARRIVALS.values()) | {MASTER_XY}

    def free(self, x, y):
        return (0 <= x < W and 0 <= y < H and self.deck[y, x]
                and self.z.collision_layer[y][x] is None)

    def prop(self, path, cx, base_y, height, solid=True, fraction=0.4, nudge=1, lane_ok=False):
        """Stand a prop with its base-centre on (cx, base_y).  Footprint must lie on the deck and clear of keep-outs."""
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        z = self.z
        wt = max(1, round(height * _aspect(path)))
        offs = sorted(((dx, dy) for dx in range(-nudge, nudge + 1) for dy in range(-nudge, nudge + 1)),
                      key=lambda d: (d[0] ** 2 + d[1] ** 2, abs(d[0])))
        for dx, dy in offs:
            ax, ay = cx + dx - wt // 2, base_y + dy - height + 1
            rows = max(1, round(height * fraction))
            core = [(x, y) for y in range(ay + height - rows, ay + height)
                    for x in range(ax + int(wt * 0.2), max(ax + int(wt * 0.8), ax + int(wt * 0.2) + 1))]
            if not solid:
                core = []
            foot = core or [(cx + dx, base_y + dy)]
            if not all(self.free(x, y) for x, y in foot):
                continue
            if any(abs(x - kx) <= 1 and abs(y - ky) <= 1 for x, y in foot for kx, ky in self.keep):
                continue
            if not lane_ok and any(abs(x - 32) <= 1 or abs(y - 32) <= 1 for x, y in foot):
                continue
            z.add_landmark(path, ax, ay, wt, height, solid=False)
            for x, y in core:
                z.collision_layer[y][x] = "landmark"
            self.placed += 1
            return True
        self.skipped.append((os.path.basename(path), cx, base_y))
        return False


GP = "assets/tiles/goblin_shared/props/"
OP = "assets/tiles/orgrimmar/props/"
CP = "assets/tiles/coastal_props/"
DP = "assets/tiles/dungeon_props/"


def _terrain(L):
    z = L.z
    z.fill("sand", "base")
    for y in range(H):
        for x in range(W):
            if L.deck[y, x]:
                z.set_tile(x, y, "path", "base")
            else:
                z.set_tile(x, y, "cliff", "collision")
    for key in SITES[L.site]["live"]:
        px, py = PORTALS[key]
        z.set_tile(px, py, "portal", "interaction")
    mx, my = MASTER_XY
    z.set_tile(mx, my, "npc", "interaction")


UP = "assets/tiles/undercity/props/"
SP = "assets/tiles/stranglethorn/props/"
KITS = {
    "orc": dict(banner=OP + "war_banner.png", stair_lamp=OP + "orc_brazier.png", berth_lamp=CP + "dock_lantern_post.png",
                crates=DP + "vot_crate_stack.png", cargo=GP + "gob_oil_drums.png",
                east=GP + "gob_rocket_crates.png", west=GP + "gob_cannon.png"),
    # Forsaken tower: same goblin engine, but Royal Apothecary banners, bone-and-iron lanterns, and coffins shipped as cargo
    "forsaken": dict(banner=UP + "uc_royal_banner.png", stair_lamp=UP + "uc_skull_pillar.png", berth_lamp=UP + "uc_lantern_post.png",
                     crates=UP + "uc_crate_stack.png", cargo=UP + "uc_coffin_stack.png",
                     east=UP + "uc_crate_stack.png", west=UP + "uc_tool_rack.png"),
    # Grom'gol: the same goblin engine under a jungle canopy. Troll braziers and war banners
    # rather than Orgrimmar's, and cargo that reads as a jungle outpost's - the camp it serves
    # ships hides and timber, not oil drums.
    "jungle": dict(banner=SP + "stv_war_banner.png", stair_lamp=SP + "stv_troll_brazier.png",
                   berth_lamp=SP + "stv_dock_lantern.png", crates=SP + "stv_crate_stack.png",
                   cargo=SP + "stv_cargo_net.png",
                   east=SP + "stv_crate_tarp.png", west=SP + "stv_fish_crates.png"),
}


def _dress(L, kit):
    p = L.prop
    # ---- hub: a searchlight tower on each diagonal, the engine works to the north-east, cargo to the south-west
    for (x, y) in [(27, 27), (37, 27), (27, 37), (37, 37)]:
        p(GP + "gob_searchlight_tower.png", x, y, 5, nudge=0)
    p(GP + "gob_boiler_tank.png", 40, 30, 4, nudge=1)      # the engine works, east of the capstan ring
    p(GP + "gob_pipe_tangle.png", 24, 35, 4, nudge=1)
    # ---- north berth (live: Undercity): mooring bollards, lanterns, banners at the gate
    p(CP + "mooring_posts.png", 27, 8, 3)
    p(CP + "mooring_posts.png", 38, 8, 3)
    p(kit["banner"], 29, 14, 5)
    p(kit["banner"], 36, 14, 5)
    # ---- south stair head (live: the ground): braziers either side of the steps, cargo waiting to be hoisted
    p(kit["stair_lamp"], 28, 58, 3)
    p(kit["stair_lamp"], 37, 58, 3)
    p(kit["crates"], 26, 55, 3)
    p(kit["cargo"], 38, 55, 3)
    p(kit["banner"], 29, 50, 5)
    p(kit["banner"], 36, 50, 5)
    # ---- east berth (reserved): an empty berth - bollards, a rail of track, a crate or two for a route that is coming
    p(CP + "mooring_posts.png", 58, 27, 3)
    p(CP + "mooring_posts.png", 58, 38, 3)
    p(kit["east"], 52, 27, 3)
    p(kit["banner"], 50, 29, 5)
    p(kit["banner"], 50, 36, 5)
    # ---- west berth (reserved)
    p(CP + "mooring_posts.png", 6, 27, 3)
    p(CP + "mooring_posts.png", 6, 38, 3)
    p(kit["west"], 11, 37, 3)
    p(kit["banner"], 14, 29, 5)
    p(kit["banner"], 14, 36, 5)


#: The Grom'gol run flies the same class of Horde airship in a jungle livery, so the two routes
#: out of Durotar are told apart at a glance from the deck. Kyle, 2026-10-31: "the east one goes
#: to grom'gol. Can we recolour a horde zepplin and put it there?"
SHIPS = {"orc": CP + "zeppelin_orc.png", "forsaken": CP + "zeppelin_undead.png",
         "jungle": CP + "zeppelin_orc_jungle.png"}


def _ship(L, skin, height=8, cx=32, base_y=8):
    """An airship moored over a berth apron, with the berth's portal tile under its gondola.
    Visual only (the lane stays walkable); side view, nose to the right, like every other sprite
    in the game."""
    path = SHIPS[skin]
    wt = max(1, round(height * _aspect(path)))
    L.z.add_landmark(path, cx - wt // 2, base_y - height + 1, wt, height, solid=False)


def build_layout(site="Zeppelin Tower"):
    L = Layout(site)
    _terrain(L)
    _dress(L, KITS[SITES[site]["skin"]])
    _ship(L, SITES[site]["skin"])
    # A SHIP AT EVERY LIVE BERTH, not just the north one. Durotar's east arm has been a real
    # portal to Grom'gol since that route opened and was still dressed as "a route that is
    # coming" - bollards, a crate and nothing moored. An empty berth over a live portal is why
    # the run was invisible from the deck. The east ship flies the jungle livery because that is
    # where it goes; the north one stays Horde red for the Undercity shuttle.
    if "E" in SITES[site].get("live", ()):
        _ship(L, "jungle", cx=54, base_y=32)
    return L


def shape_preview(path, scale=10):
    ys, xs = np.mgrid[0:H, 0:W]
    d = deck_field(xs + 0.5, ys + 0.5)
    img = np.zeros((H, W, 3), np.uint8)
    img[:] = (30, 40, 60)
    img[d > 0] = (140, 100, 60)
    for k, (x, y) in PORTALS.items():
        img[y, x] = (255, 0, 255) if k in LIVE_PORTALS else (120, 120, 120)
    for (x, y) in ARRIVALS.values():
        img[y, x] = (80, 255, 120)
    img[MASTER_XY[1], MASTER_XY[0]] = (30, 200, 255)
    Image.fromarray(img).resize((W * scale, H * scale), Image.NEAREST).save(path)


def register_baked(zone, baked_dir=BAKED_DIR, chunk=20):
    for cy in range(0, H, chunk):
        for cx in range(0, W, chunk):
            fn = f"{baked_dir}/ground_{cx}_{cy}.jpg"
            if not os.path.exists(fn):
                raise FileNotFoundError(f"{fn} - run python3 tools/bake_zeppelin_tower.py")
            w, h = min(chunk, W - cx), min(chunk, H - cy)
            zone.add_ground_chunk(fn, cx, cy, w, h)
            zone.ground_chunks[-1]["exact"] = True
            zone.add_water_chunk(fn, cx, cy, w, h)
            zone.add_obstacle_chunk(fn, cx, cy, w, h)


def generate(site="Zeppelin Tower"):
    L = build_layout(site)
    register_baked(L.zone, SITES[site]["baked"])
    return L.zone
