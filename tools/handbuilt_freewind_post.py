"""
Hand-built Freewind Post (204x172): the tauren capital-in-exile, spread across THREE MESA TOPS joined by
rope bridges, seen from above as three decks floating over a canyon floor a very long way down.

ARCHETYPE: THE THREE DECKS.

Kyle: "Freewind post can be mildly expanded as its the 'tauren city' now. But not too big. Lets make it
spread over '3 mesas' so its very iconicly 1000 needles." And then: "let's do the 'high in the air' style
that you did with the zeppelin towers. That fuzzy ground texture with 'clouds' over it."

Those two instructions solve each other. A settlement on three mesa tops has one hard problem in a
top-down game - NOTHING ABOUT A FLAT TOP SAYS "HIGH" when you are looking straight down at it - and the
zeppelin tower already solved it: paint everything off the deck as the ground far below, under drifting
cloud, with the deck's own shadow falling across it. Here the decks are mesa tops instead of a timber
cross, and the arms between them are rope bridges instead of gangways.

    THE LANDING      the north top, and the only one with a ramp down to the canyon floor. Where you
                     arrive from Southern Thousand Needles, and the only ground route in or out.
    THE LONG MESA    the big one. Lodges, the trainers, the market, the cook fires. The actual town.
    WINDWARD         the small high one to the east. The elder, the great totem, and the lookout, which
                     is the highest point anybody in Thousand Needles can stand on.

THREE BRIDGES, NOT TWO. A chain would make Windward a dead end and the Long Mesa a corridor. A triangle
means every top has two ways off it, which is what a place people actually live in looks like, and it
means the long north-east span exists - the single-rope one nobody crosses with a full pack.

EVERYTHING BUILT UP HERE IS ASPEN. That is the whole reason the region talks about this place. The tauren
came south when Thunder Bluff fell, stopped in a mountain that had arrived from somewhere else, learned
to log it, and carried the timber down to build on mesas their grandparents could not have built on. The
stone is Azeroth's and the wood is not, and the bridges are what the wood was for.

HARD CONTRACT (world/portal_manager.py): portal (56, 14) <-> Southern Thousand Needles (168, 88).
Prop rule (Kyle): less is more; logical for the spot; a few centrepieces.
"""
import os

import numpy as np

from world.tilemap import Tilemap

BAKED_DIR = "assets/tiles/freewind_post/baked"
W, H = 204, 172

SNP = "assets/tiles/southern_needles/props/"
ASP = "assets/tiles/aspen/props/"
TAU = "assets/buildings/"

#: (name, cx, cy, rx, ry). The three tops, deliberately unequal - one to arrive on, one to live on, one to
#: look out from.
DECKS = {
    "landing":  (96, 40, 35, 27),
    "long":     (64, 114, 54, 40),
    "windward": (162, 112, 28, 22),
}

#: (from, to, half-width). The main span is wide enough for a kodo; the others are not, and the long
#: north-east one is a single rope with planks on it.
BRIDGES = [
    ("landing", "long", 3.6),
    ("long", "windward", 2.8),
    ("landing", "windward", 1.8),
]

PORTAL = (96, 20)          # on the Landing, at the head of the ramp down to the canyon floor
ARRIVAL = (96, 26)
START = (96, 27)

#: Where the people stand. Everything is on a deck; sync_freewind_npcs asserts it.
NPC_POSITIONS = {
    # ===== THE LANDING - the caravan quarter =====
    "fw_gate_warden": (90, 30),
    "fw_ramp_guard": (102, 30),
    "fw_bridge_keeper": (112, 60),
    "fw_caravan_master": (96, 48),
    "fw_stablemaster": (118, 48),
    "fw_kodo_wrangler": (78, 54),
    "fw_warehouse_keeper": (78, 44),
    "fw_tally_clerk": (108, 52),

    # ===== THE LONG MESA - the city =====
    "fw_high_elder": (64, 100),
    "fw_innkeeper": (76, 104),
    "fw_flight_master": (30, 94),
    "fw_banker": (52, 106),
    "fw_auctioneer": (44, 108),
    "fw_healer": (86, 102),
    "fw_rememberer": (64, 120),
    # market row, down the west side
    "fw_quartermaster": (30, 108),
    "fw_market_herbs": (30, 118),
    "fw_market_hides": (30, 126),
    "fw_market_spices": (30, 134),
    "fw_market_relics": (20, 122),
    "fw_cook": (22, 114),
    # craft row, east
    "fw_smith": (100, 116),
    "fw_weaponsmith": (100, 124),
    "fw_tanner": (106, 130),
    "fw_timberwright": (96, 136),
    "fw_bowyer": (82, 142),
    "fw_carver": (92, 140),
    "fw_potter": (110, 118),
    "fw_reagents": (104, 100),

    # ===== WINDWARD - the high seat =====
    "fw_skywatcher": (150, 100),
    "fw_totem_keeper": (162, 116),
    "fw_spirit_walker": (168, 106),
    "fw_council_1": (154, 122),
    "fw_council_2": (170, 124),
    "fw_lookout": (178, 102),
}


def _deck_r(gx, gy, cx, cy, rx, ry):
    """Normalised radius in a mesa top. Wobbled so the edge is eroded stone, not a drawn ellipse."""
    dx, dy = (np.asarray(gx, float) - cx) / rx, (np.asarray(gy, float) - cy) / ry
    a = np.arctan2(dy, dx)
    f = 1.0 + 0.10 * np.sin(2 * a + cx) + 0.06 * np.sin(3 * a + cy * 0.4) + 0.04 * np.sin(5 * a)
    return np.hypot(dx, dy) / f


def _seg_dist(gx, gy, x0, y0, x1, y1):
    px, py = x1 - x0, y1 - y0
    L2 = px * px + py * py + 1e-9
    t = np.clip(((np.asarray(gx, float) - x0) * px + (np.asarray(gy, float) - y0) * py) / L2, 0.0, 1.0)
    return np.hypot(np.asarray(gx, float) - (x0 + t * px), np.asarray(gy, float) - (y0 + t * py))


def deck_field(gx, gy):
    """>0 on standable ground: the three mesa tops and the bridges between them.

    Everything else is a drop. This single field decides collision, what the baker paints as deck, and
    what it paints as the canyon floor far below - so the hole in the world and the picture of the hole
    can never disagree.
    """
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    out = np.full(np.shape(gx), -99.0)
    for (cx, cy, rx, ry) in DECKS.values():
        out = np.maximum(out, (1.0 - _deck_r(gx, gy, cx, cy, rx, ry)) * min(rx, ry))
    for (a, b, half) in BRIDGES:
        ax, ay = DECKS[a][0], DECKS[a][1]
        bx, by = DECKS[b][0], DECKS[b][1]
        out = np.maximum(out, half - _seg_dist(gx, gy, ax, ay, bx, by))
    return out


def bridge_field(gx, gy):
    """>0 only on a bridge - the baker planks these and leaves the tops as stone."""
    gx = np.asarray(gx, float)
    gy = np.asarray(gy, float)
    out = np.full(np.shape(gx), -99.0)
    for (a, b, half) in BRIDGES:
        ax, ay = DECKS[a][0], DECKS[a][1]
        bx, by = DECKS[b][0], DECKS[b][1]
        out = np.maximum(out, half - _seg_dist(gx, gy, ax, ay, bx, by))
    # A bridge stops being a bridge once it is over a mesa top - otherwise the planking runs across the
    # middle of the town, which is where the spans cross but not where anybody laid boards.
    on_top = np.full(np.shape(gx), -99.0)
    for (cx, cy, rx, ry) in DECKS.values():
        on_top = np.maximum(on_top, (0.92 - _deck_r(gx, gy, cx, cy, rx, ry)) * min(rx, ry))
    return np.minimum(out, -on_top)


def fields(gx, gy):
    return dict(deck=deck_field(gx, gy), bridge=bridge_field(gx, gy))


class Layout:
    def __init__(self):
        self.zone = Tilemap("Freewind Post", W, H,
                            "Three mesa tops, roped together with aspen hauled down out of a mountain "
                            "that was not here three years ago. The tauren live on top of it.")
        self.z = self.zone
        self.z.region = "Kalimdor - Thousand Needles"
        self.skipped = []
        self.placed = 0
        ys, xs = np.mgrid[0:H, 0:W]
        self.deck = deck_field(xs + 0.5, ys + 0.5) > 0
        self.bridge = bridge_field(xs + 0.5, ys + 0.5) > 0
        self.keep = {PORTAL, ARRIVAL, START} | set(NPC_POSITIONS.values())

    def free(self, x, y):
        return (0 <= x < W and 0 <= y < H and self.deck[y, x]
                and self.z.collision_layer[y][x] is None)

    def prop(self, path, cx, base_y, height, solid=True, fraction=0.4, nudge=1):
        """Stand a prop with its base-centre on (cx, base_y). Footprint must be ON A DECK and clear of
        keep-outs - a prop hanging over the drop is the one mistake this zone can make that looks like a
        bug rather than a choice."""
        from tools.dungeon_builder import _aspect
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
            # nothing stands on a bridge. They are two tiles wide and people have to pass.
            if any(self.bridge[y][x] for x, y in foot):
                continue
            # THE WHOLE SPRITE HAS TO BE OVER THE DECK, not just its base.
            #
            # Everywhere else in the game a tall prop may overhang its footprint - that is just a tree
            # whose crown reaches past the trunk. Over a four-hundred-foot drop it is a building
            # HOVERING IN MID-AIR, and the first dressed preview of this zone had the great lodge doing
            # exactly that off the north-west rim. The base rule passed it; the eye did not.
            box = [(x, y) for y in range(max(ay, 0), min(ay + height, H))
                   for x in range(max(ax, 0), min(ax + wt, W))]
            # 0.96, not 0.8: at 80% on-deck the great lodge still read as hovering off the north-west
            # rim. Over a drop there is no such thing as a slight overhang.
            if not box or sum(self.deck[y][x] for x, y in box) < 0.96 * len(box):
                continue
            z.add_landmark(path, ax, ay, wt, height, solid=False)
            for x, y in core:
                z.collision_layer[y][x] = "landmark"
            self.placed += 1
            return True
        self.skipped.append((os.path.basename(path), cx, base_y))
        return False


def _terrain(L):
    z = L.z
    z.fill("sand", "base")
    for y in range(H):
        for x in range(W):
            if L.deck[y, x]:
                z.set_tile(x, y, "path", "base")
            else:
                z.set_tile(x, y, "cliff", "collision")
    px, py = PORTAL
    z.set_tile(px, py, "portal", "interaction")


def _row(L, path, x0, y0, x1, y1, n, height, **kw):
    """Place n copies evenly along a line. A market ROW has to read as a row.

    Capitals are not camps with more tents in them - they are STREETS, and a street is a line of things.
    Orgrimmar's market is twelve stalls in a row; Camp Taurajo is a ring of tipis round a fire. Freewind
    needs the former, and hand-typing sixty coordinates to get it would be sixty chances to typo one.
    """
    placed = 0
    for i in range(n):
        t = i / max(n - 1, 1)
        x = int(round(x0 + (x1 - x0) * t))
        y = int(round(y0 + (y1 - y0) * t))
        placed += bool(L.prop(path, x, y, height, **kw))
    return placed


def _dress(L):
    """A CAPITAL, not a camp. Districts, streets and rows.

    Kyle: "This is supposed to be the defacto Tauren town. Should be like a capital city."

    He was right and the numbers said so: before this pass Freewind had 36 buildings to Camp Taurajo's
    83, and eleven people to Razor Hill's twenty-two. It was a big empty map. Orgrimmar is 208 landmarks
    and 51 people; a capital is not a bigger camp, it is a place with STREETS in it.

    So each mesa becomes a district, which is what the three-mesa idea was always for:

        THE LANDING    the caravan quarter. Everything that reaches this city comes up the one ramp, so
                       this top is pens, stables, warehouses and the people who count what arrives.
        THE LONG MESA  the city. A market row, a craft row, the lodges, the inn, and a square with the
                       great lodge at its head.
        WINDWARD       the high seat. The spirit lodge, the great totem, the elders - and deliberately
                       the most open of the three, because the seat of a people should have room to
                       gather and a view of what they lost.

    AND THEN IT GETS THINNED. Kyle, on the first dense pass: "Don't just flood it with buildings too.
    Sometimes less is more too." He is right and the first attempt went too far the other way - ranks
    of identical yurts and two lanes of identical tents, which is not a city, it is wallpaper with
    roofs on. A capital reads as a capital through STRUCTURE: a square you can see across, a market
    that is a line of DIFFERENT traders, a civic centre with room around it. The repeated housing is
    cut back hard and the open ground it was eating is the point of what is left.
    """
    p = L.prop
    A = lambda d, s: d + s + ".png"        # noqa: E731
    T = lambda s: TAU + s + ".png"         # noqa: E731
    S = lambda s: SNP + s + ".png"         # noqa: E731

    # =====================================================================================================
    # THE LANDING - the caravan quarter
    # =====================================================================================================
    p(T("tau_watchtower"), 78, 30, 11)
    p(T("tau_watchtower"), 118, 32, 11)
    p(T("tau_gate_arch"), 96, 32, 8)
    # the pens: the ramp is the only way anything four-legged gets up here, so the stock lives at its head
    _row(L, T("tau_kodo_pen"), 72, 52, 84, 56, 2, 9)
    p(T("tau_stable"), 112, 52, 8)
    p(T("tau_stable"), 124, 46, 8)
    # the warehouses - everything that arrives is stored before it crosses a bridge
    _row(L, T("tau_storehouse"), 72, 40, 72, 54, 2, 8)
    _row(L, T("tau_storehouse"), 120, 50, 112, 58, 2, 8)
    p(T("tau_trading_post"), 106, 58, 9)
    p(T("tau_food_cache"), 90, 58, 6)
    p(T("tau_meeting_shelter"), 104, 44, 7)
    p(T("tau_tent_small"), 84, 44, 5)
    _row(L, S("sn_pulley_hoist"), 88, 26, 104, 26, 2, 6)
    _row(L, S("sn_plank_stack"), 74, 34, 116, 38, 2, 3)
    _row(L, S("sn_rope_coil"), 94, 38, 108, 48, 2, 2, solid=False)
    _row(L, S("sn_windsock"), 80, 26, 114, 28, 2, 7)
    _row(L, S("sn_hide_banner"), 82, 24, 112, 24, 2, 6)
    _row(L, S("sn_anchor_post"), 86, 62, 106, 62, 2, 5)

    # =====================================================================================================
    # THE LONG MESA - the city. Rows, not scatter.
    # =====================================================================================================
    # --- the head of the square: the great lodge, with the elder's and the spirit house flanking it
    p(T("tau_great_lodge"), 64, 92, 14)
    p(T("tau_elder_lodge"), 44, 94, 10)
    p(T("tau_hearth_lodge"), 84, 94, 9)
    p(T("tau_bonfire_pavilion"), 64, 108, 7)

    # --- THE MARKET ROW. Ten stalls down the west side, which is what makes this a city.
    _row(L, T("tau_trading_post"), 24, 106, 24, 134, 4, 9)
    _row(L, T("tau_tent_medium"), 38, 108, 38, 134, 3, 6)
    _row(L, T("tau_tent_small"), 15, 114, 15, 128, 2, 5)
    _row(L, S("sn_hide_banner"), 31, 110, 31, 132, 2, 6, solid=False)

    # --- THE CRAFT ROW. The working side, east, where the smoke goes downwind of the lodges.
    _row(L, T("tau_smithy"), 96, 110, 96, 126, 2, 8)
    p(T("tau_kiln"), 106, 112, 7)
    p(T("tau_tannery"), 106, 126, 8)
    p(T("tau_carver_shop"), 88, 136, 8)
    p(T("tau_bowyer"), 76, 140, 8)
    p(T("tau_herb_hut"), 100, 96, 7)
    _row(L, S("sn_drying_rack"), 98, 134, 90, 142, 2, 5)

    # --- the living quarter, south-west: yurts in two ranks
    _row(L, T("tau_yurt"), 48, 144, 68, 144, 3, 7)

    _row(L, T("tau_longhouse"), 46, 118, 46, 134, 2, 10)
    _row(L, T("tau_tent_large"), 66, 128, 78, 128, 2, 7)

    # --- the square itself: troughs, totems, the things a gathering place has
    _row(L, T("tau_water_trough"), 54, 116, 74, 116, 2, 4)
    _row(L, T("tau_totem_pole"), 52, 100, 76, 100, 2, 11)
    _row(L, S("sn_streamers"), 54, 112, 76, 112, 2, 5, solid=False)
    _row(L, S("sn_anchor_post"), 96, 92, 106, 114, 2, 5)
    p(T("tau_food_cache"), 36, 88, 6)
    p(T("tau_storehouse"), 24, 92, 8)
    # --- a second market lane, east of the square, and the bunkhouses behind the craft row
    _row(L, T("tau_tent_medium"), 92, 110, 92, 130, 2, 6)

    _row(L, T("tau_longhouse"), 72, 140, 86, 142, 2, 10)
    _row(L, S("sn_hide_banner"), 88, 112, 88, 128, 2, 6, solid=False)
    _row(L, S("sn_water_trough"), 42, 110, 42, 132, 2, 4)
    _row(L, S("sn_clay_vessel"), 30, 120, 30, 128, 2, 2, solid=False)
    _row(L, S("sn_spear_bundle"), 56, 96, 72, 96, 2, 5)

    # =====================================================================================================
    # WINDWARD - the high seat. Open on purpose: a people's seat needs room to gather.
    # =====================================================================================================
    p(T("tau_spirit_lodge"), 162, 104, 11)
    p(T("tau_totem_pole"), 148, 112, 12)
    p(T("tau_totem_pole"), 176, 112, 12)
    p(T("tau_meeting_shelter"), 162, 124, 8)
    _row(L, S("sn_lookout_platform"), 150, 102, 176, 102, 2, 11)
    _row(L, S("sn_cairn"), 148, 124, 176, 126, 2, 4)
    _row(L, S("sn_streamers"), 152, 106, 174, 106, 2, 5, solid=False)
    _row(L, S("sn_anchor_post"), 142, 110, 142, 122, 2, 5)
    p(T("tau_hearth_lodge"), 178, 122, 9)
    _row(L, T("tau_tent_medium"), 144, 118, 144, 118, 1, 6)
    _row(L, T("tau_tent_small"), 182, 110, 182, 110, 1, 5)
    _row(L, S("sn_spear_bundle"), 154, 96, 170, 96, 2, 5)


def build_layout():
    L = Layout()
    _terrain(L)
    _dress(L)
    # subzones: one per top, so a quest or an encounter table can name a mesa
    L.z.add_subzone("Freewind Post", 0, 0, W, H)
    L.z.add_subzone("The Landing", 62, 14, 68, 52)
    L.z.add_subzone("The Long Mesa", 13, 76, 102, 76)
    L.z.add_subzone("Windward", 130, 88, 58, 46)
    return L


def generate_freewind_post():
    L = build_layout()
    from tools.handbuilt_vot_caves import register_baked
    register_baked(L.z, BAKED_DIR)
    return L.z


def build_freewind_baked():
    """(zone, layout) - what the baker paints from."""
    L = build_layout()
    return L.z, L
