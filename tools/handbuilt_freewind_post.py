"""
Hand-built Freewind Post (150x140): the tauren capital-in-exile, spread across THREE MESA TOPS joined by
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
W, H = 150, 140

SNP = "assets/tiles/southern_needles/props/"
ASP = "assets/tiles/aspen/props/"
TAU = "assets/buildings/"

#: (name, cx, cy, rx, ry). The three tops, deliberately unequal - one to arrive on, one to live on, one to
#: look out from.
DECKS = {
    "landing":  (76, 34, 25, 19),
    "long":     (52, 92, 37, 27),
    "windward": (118, 89, 21, 17),
}

#: (from, to, half-width). The main span is wide enough for a kodo; the others are not, and the long
#: north-east one is a single rope with planks on it.
BRIDGES = [
    ("landing", "long", 3.0),
    ("long", "windward", 2.4),
    ("landing", "windward", 1.5),
]

PORTAL = (76, 18)          # on the Landing, at the head of the ramp down to the canyon floor
ARRIVAL = (76, 24)
START = (76, 25)

#: Where the people stand. Everything is on a deck; sync_freewind_npcs asserts it.
NPC_POSITIONS = {
    # --- the Landing: the gate
    "fw_gate_warden": (66, 30),
    "fw_bridge_keeper": (88, 42),
    # --- the Long Mesa: the town proper
    "fw_elder": (48, 84),
    "fw_quartermaster": (32, 90),
    "fw_cook": (62, 100),
    "fw_tanner": (26, 102),
    "fw_timberwright": (46, 110),
    "fw_innkeeper": (62, 86),
    "fw_flight_master": (22, 84),
    # --- Windward: the high place
    "fw_skywatcher": (116, 78),
    "fw_totem_keeper": (126, 96),
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


def _dress(L):
    """Less is more (Kyle's standing rule), and logical for the spot.

    Bigger now, and the extra room goes into the LONG MESA - that is the town, and a capital needs a
    smith, a bowyer, a carver and somewhere to put the food, not just lodges. The Landing gains the kodo
    pen and the stable, because the ramp is the only way anything four-legged gets up here and it would
    be penned at the top of it. Windward gains almost nothing on purpose: it is the high place, and an
    empty top is what makes it read as the top.

    No palisade and no gate across anything. There is nothing to wall out up here. The drop does that.
    """
    p = L.prop
    A = lambda d, s: d + s + ".png"        # noqa: E731

    # ---- THE LANDING. Everything that reaches this town comes up the ramp and across this top, so it is
    # hoists, rope, pens and a watchtower, and nowhere to sleep.
    p(A(TAU, "tau_watchtower"), 64, 28, 11)
    p(A(TAU, "tau_gate_arch"), 90, 40, 8)
    p(A(TAU, "tau_kodo_pen"), 60, 44, 9)
    p(A(TAU, "tau_stable"), 88, 28, 8)
    p(A(TAU, "tau_storehouse"), 74, 46, 8)
    p(A(SNP, "sn_pulley_hoist"), 70, 34, 6)
    p(A(SNP, "sn_plank_stack"), 56, 34, 3)
    p(A(SNP, "sn_rope_coil"), 58, 24, 2, solid=False)
    p(A(SNP, "sn_windsock"), 82, 26, 7)
    p(A(SNP, "sn_hide_banner"), 68, 22, 6)

    # ---- THE LONG MESA. The town. The great lodge faces the bridge you arrive by, so the first thing
    # anybody coming up here sees is that these people built something permanent.
    p(A(TAU, "tau_great_lodge"), 50, 80, 13)
    p(A(TAU, "tau_elder_lodge"), 32, 86, 10)
    p(A(TAU, "tau_longhouse"), 66, 90, 10)
    p(A(TAU, "tau_hearth_lodge"), 36, 102, 9)
    p(A(TAU, "tau_trading_post"), 58, 108, 9)
    p(A(TAU, "tau_smithy"), 74, 100, 8)
    p(A(TAU, "tau_tannery"), 24, 96, 8)
    p(A(TAU, "tau_carver_shop"), 20, 108, 8)
    p(A(TAU, "tau_bowyer"), 46, 114, 8)
    p(A(TAU, "tau_herb_hut"), 70, 80, 7)
    p(A(TAU, "tau_food_cache"), 30, 76, 6)
    p(A(TAU, "tau_bonfire_pavilion"), 50, 96, 7)
    p(A(TAU, "tau_meeting_shelter"), 62, 76, 7)
    p(A(TAU, "tau_yurt"), 78, 90, 7)
    p(A(TAU, "tau_tent_medium"), 40, 110, 6)
    p(A(TAU, "tau_water_trough"), 18, 88, 4)
    p(A(SNP, "sn_drying_rack"), 26, 110, 5)
    p(A(SNP, "sn_streamers"), 42, 90, 5, solid=False)
    p(A(SNP, "sn_anchor_post"), 76, 108, 5)
    p(A(SNP, "sn_anchor_post"), 58, 72, 5)

    # ---- WINDWARD. The high place: a spirit lodge, the great totem and the lookout, and very little
    # else. The emptiness is the point.
    p(A(TAU, "tau_spirit_lodge"), 122, 86, 10)
    p(A(TAU, "tau_totem_pole"), 112, 94, 11)
    p(A(SNP, "sn_lookout_platform"), 126, 84, 11)
    p(A(SNP, "sn_cairn"), 106, 98, 4)
    p(A(SNP, "sn_streamers"), 114, 80, 5, solid=False)
    p(A(SNP, "sn_anchor_post"), 102, 92, 5)


def build_layout():
    L = Layout()
    _terrain(L)
    _dress(L)
    # subzones: one per top, so a quest or an encounter table can name a mesa
    L.z.add_subzone("Freewind Post", 0, 0, W, H)
    L.z.add_subzone("The Landing", 50, 14, 52, 40)
    L.z.add_subzone("The Long Mesa", 14, 64, 76, 56)
    L.z.add_subzone("Windward", 96, 71, 44, 36)
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
