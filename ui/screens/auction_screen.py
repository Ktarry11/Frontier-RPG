"""The auction house: Classic's Browse, Bids and Auctions tabs, with the modern one's category tree, favourites and
sell panel (docs/auction_house_design.md, section 12).

Kyle, 15 Nov 2026: "we need to have all the tabs, the rariety, search function, level function....I WANT THIS
DETAILED AS FUCK BRO", with screenshots of Classic's Browse Auctions window and the modern category tree.

The market itself is world/market/market.py; this screen only asks it things and tells it what you clicked. Kyle's
two painted halls (assets/ui/auction/) sit behind the window: the Horde hall for the Horde book, the goblin one for
Steamwheedle.
"""
import math

import pygame

from config import SCREEN_HEIGHT, SCREEN_WIDTH
from core.game_states import GameState
from ui import theme
from ui.market_widgets import (RARITY_COLOUR, Button, CheckBox, Dropdown, MoneyBox, TextBox, draw_coins,
                               draw_icon, draw_tooltip, good_lines, ui_icon)
from ui.screens.base_screen import BaseScreen
from world.market import catalog as C
from world.market import goods as G
from world.market.market import (DURATIONS, MARKETS, PLAYER, TIME_ICON, market_of, min_next_bid)

WIN = pygame.Rect(30, 18, SCREEN_WIDTH - 60, 640)
ROW_H = 31
ROWS = 12
TREE_W = 186
RARITY_OPTIONS = [("All", None, None), ("Poor", "poor", RARITY_COLOUR["poor"]),
                  ("Common", "common", RARITY_COLOUR["common"]), ("Uncommon", "uncommon", RARITY_COLOUR["uncommon"]),
                  ("Rare", "rare", RARITY_COLOUR["rare"]), ("Epic", "epic", RARITY_COLOUR["epic"])]
GREETING = {
    "horde": "Welcome to the auction house. Everything here belongs to somebody, until it belongs to you.",
    "goblin": "Steamwheedle trades with anybody whose coin is real. The house takes its cut. The house always does.",
}


def _qty(r, screen, n, rect):
    """A stack count in the bottom right of an icon, with a dark edge so it reads on any art."""
    font = r._get_font("small")
    txt = str(n)
    w, h = font.size(txt)
    x, y = rect.right - w - 2, rect.bottom - h + 1
    shadow = font.render(txt, True, (0, 0, 0))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        screen.blit(shadow, (x + dx, y + dy))
    screen.blit(font.render(txt, True, (255, 255, 255)), (x, y))


class AuctionScreen(BaseScreen):
    def __init__(self, state_manager, icon_ui_helper=None):
        super().__init__(state_manager)
        self._icons = icon_ui_helper
        self.market_id = "horde"
        self.auctioneer = None
        self.tab = "browse"
        self.message, self.message_col, self.message_t = "", theme.TEXT, 0.0
        self._bg = {}
        # ---- browse controls
        x, y = WIN.x + 16, WIN.y + 86
        self.name_box = TextBox((x, y, 196, 24), placeholder="Search", on_enter=self._search)
        self.exact = CheckBox((x + 206, y + 4, 16, 16), "Exact")
        self.lo_box = TextBox((x + 290, y, 36, 24), digits=True, max_len=2, on_enter=self._search)
        self.hi_box = TextBox((x + 342, y, 36, 24), digits=True, max_len=2, on_enter=self._search)
        self.rarity = Dropdown((x + 392, y, 110, 24), RARITY_OPTIONS)
        self.usable = CheckBox((x + 516, y + 4, 16, 16), "Usable items")
        self.favs = CheckBox((x + 628, y + 4, 16, 16), "Favourites")
        self.search_btn = Button((WIN.right - 214, y - 3, 96, 30), "Search")
        self.reset_btn = Button((WIN.right - 110, y - 3, 94, 30), "Reset")
        self.per_unit = CheckBox((WIN.x + 16 + TREE_W + 14, WIN.bottom - 92, 16, 16), "Price per unit", True)
        self.bid_box = MoneyBox(WIN.right - 560, WIN.bottom - 42)
        self.bid_btn = Button((WIN.right - 330, WIN.bottom - 46, 100, 32), "Bid")
        self.buy_btn = Button((WIN.right - 222, WIN.bottom - 46, 100, 32), "Buyout")
        self.close_btn = Button((WIN.right - 114, WIN.bottom - 46, 98, 32), "Close")
        self.prev_btn = Button((WIN.right - 196, WIN.bottom - 96, 84, 28), "Prev")
        self.next_btn = Button((WIN.right - 104, WIN.bottom - 96, 84, 28), "Next")
        self.cat, self.sub = None, None
        self.expanded = set()
        self.tree_scroll = 0
        self.results = []
        self.page = 0
        self.sort = ("buyout", 1)
        self.selected = None
        self.searched = False
        # ---- auctions (sell) controls
        sx, sy = WIN.x + 16, WIN.y + 70
        self.bag_scroll = 0
        self.sell_obj = None
        self.stack_box = TextBox((sx + 96, sy + 296, 46, 24), digits=True, max_len=3)
        self.count_box = TextBox((sx + 262, sy + 296, 40, 24), digits=True, max_len=2)
        self.start_box = MoneyBox(sx + 96, sy + 330)
        self.buyout_box = MoneyBox(sx + 96, sy + 364)
        self.duration = 24
        self.create_btn = Button((sx, sy + 454, 340, 34), "Create Auction")
        self.cancel_btn = Button((WIN.right - 196, WIN.bottom - 46, 180, 32), "Cancel Auction")
        self.mine_selected = None
        self._hover = None

    # ------------------------------------------------------------ open
    def open(self, market_id, auctioneer, encoding="utf-8"):
        self.market_id = market_id if market_id in MARKETS else "horde"
        self.auctioneer = auctioneer
        m = self.market
        m.ensure_started()
        m.advance(0)
        self.selected = None
        self._search(keep_page=True)

    @property
    def icons(self):
        return self._icons or getattr(self.state_manager, "icon_ui_helper", None)

    @property
    def party(self):
        return self.state_manager.get_party()

    @property
    def player(self):
        return self.state_manager.player

    @property
    def market(self):
        return market_of(self.party)

    def _say(self, text, col=None):
        self.message, self.message_col, self.message_t = text, col or theme.TEXT, 5.0

    # ------------------------------------------------------------ search
    def _search(self, keep_page=False):
        lo = self.lo_box.value if self.lo_box.text else None
        hi = self.hi_box.value if self.hi_box.text else None
        self.results = self.market.search(
            self.market_id, text=self.name_box.text, exact=self.exact.checked, lo=lo, hi=hi,
            rarity=self.rarity.value, usable_by=self.player if self.usable.checked else None, cat=self.cat,
            sub=self.sub, favourites=self.favs.checked)
        self._sort()
        if not keep_page:
            self.page = 0
        self.page = min(self.page, max(0, self._pages() - 1))
        self.searched = True

    def _reset(self):
        self.name_box.set("")
        self.exact.checked = False
        self.lo_box.set("")
        self.hi_box.set("")
        self.rarity.index = 0
        self.usable.checked = False
        self.favs.checked = False
        self.cat = self.sub = None
        self._search()

    def _price_key(self, a, which):
        v = (a.bid or a.min_bid) if which == "bid" else (a.buyout or 10 ** 12)
        return v / a.qty if self.per_unit.checked else v

    def _sort(self):
        col, d = self.sort
        rank = {r: i for i, r in enumerate(C.RARITY_ORDER)}
        keys = {
            "name": lambda a: (-rank.get(a.rarity, 1), a.name),
            "lvl": lambda a: (a.level or 0, a.name),
            "time": lambda a: a.ends_at,
            "seller": lambda a: str(a.seller),
            "bid": lambda a: self._price_key(a, "bid"),
            "buyout": lambda a: (self._price_key(a, "buyout"), a.name),
        }
        self.results.sort(key=keys[col], reverse=d < 0)

    def _pages(self):
        return max(1, math.ceil(len(self.results) / ROWS))

    # ------------------------------------------------------------ geometry
    def _cols(self, x0, x1, tab="browse"):
        """[(key, label, x, w)] across the results table."""
        if tab == "auctions":
            spec = [("name", "Item", None), ("lvl", "Lvl", 44), ("time", "Time Left", 104), ("bidder", "High Bidder", 150),
                    ("bid", "Current Bid", 136), ("buyout", "Buyout", 136)]
        elif tab == "bids":
            spec = [("name", "Item", None), ("lvl", "Lvl", 44), ("time", "Time Left", 104), ("seller", "Seller", 150),
                    ("status", "Status", 96), ("bid", "Current Bid", 136), ("buyout", "Buyout", 136)]
        else:
            spec = [("name", "Item", None), ("lvl", "Lvl", 44), ("time", "Time Left", 104), ("seller", "Seller", 150),
                    ("bid", "Current Bid", 140), ("buyout", "Buyout", 140)]
        fixed = sum(w for _k, _l, w in spec if w)
        out, x = [], x0
        for k, label, w in spec:
            w = w or (x1 - x0 - fixed)
            out.append((k, label, x, w))
            x += w
        return out

    def _table_rect(self):
        if self.tab == "browse":
            return pygame.Rect(WIN.x + 16 + TREE_W + 14, WIN.y + 122, WIN.right - 16 - (WIN.x + 16 + TREE_W + 14),
                               24 + ROWS * ROW_H)
        if self.tab == "bids":
            return pygame.Rect(WIN.x + 16, WIN.y + 70, WIN.width - 32, 24 + ROWS * ROW_H)
        return pygame.Rect(WIN.x + 392, WIN.y + 286, WIN.right - 16 - (WIN.x + 392), 24 + 8 * ROW_H)

    def _rows(self):
        if self.tab == "browse":
            return self.results[self.page * ROWS:(self.page + 1) * ROWS]
        if self.tab == "bids":
            return self.market.bids(self.market_id)[:ROWS]
        return self.market.my_auctions(self.market_id)[:8]

    def _row_rect(self, i):
        t = self._table_rect()
        return pygame.Rect(t.x, t.y + 24 + i * ROW_H, t.width, ROW_H - 2)

    def _tree_rows(self):
        """[(label, cat, sub, depth)] of the category tree, as it is expanded now."""
        out = [("Favourites", "__fav__", None, 0)]
        for cat, subs in C.TREE:
            out.append((cat, cat, None, 0))
            if cat in self.expanded:
                for s in subs:
                    out.append((s, cat, s, 1))
        return out

    def _tree_rect(self):
        return pygame.Rect(WIN.x + 16, WIN.y + 122, TREE_W, 24 + ROWS * ROW_H)

    def _tab_rects(self):
        out = []
        x = WIN.x + 20
        for key, label in (("browse", "Browse"), ("bids", "Bids"), ("auctions", "Auctions")):
            out.append((key, label, pygame.Rect(x, WIN.bottom + 2, 120, 32)))
            x += 126
        return out

    # ------------------------------------------------------------ the sell side
    def _bag_goods(self):
        return G.tradeable_goods(self.player)

    def _bag_rect(self, i):
        sx, sy = WIN.x + 16, WIN.y + 96
        c, r = i % 7, i // 7
        return pygame.Rect(sx + c * 49, sy + r * 49, 45, 45)

    def _pick_sell(self, obj):
        self.sell_obj = obj
        if obj is None:
            return
        have = 1 if G.kind_of(obj) == G.GEAR else int(getattr(obj, "quantity", 1) or 1)
        stack = have if G.kind_of(obj) == G.GEAR else min(have, int(getattr(obj, "stack_limit", 20) or 20))
        self.stack_box.set(stack)
        self.count_box.set(1)
        start, buy = self.market.suggest(self.market_id, obj, stack)
        self.start_box.set(start)
        self.buyout_box.set(buy)

    def _sell_numbers(self):
        obj = self.sell_obj
        if obj is None:
            return None
        have = 1 if G.kind_of(obj) == G.GEAR else int(getattr(obj, "quantity", 1) or 1)
        stack = max(1, min(have, self.stack_box.value or 1))
        count = max(1, min(have // stack, self.count_box.value or 1))
        probe = G.pack(obj, stack)
        dep = self.market.deposit_for(probe, self.duration, self.market_id) * count
        return have, stack, count, dep

    def _create(self):
        nums = self._sell_numbers()
        if not nums:
            self._say("Pick something from your bags first.", theme.WARN)
            return
        have, stack, count, dep = nums
        start, buy = self.start_box.value, self.buyout_box.value
        made = 0
        last = ""
        for _ in range(count):
            obj = self.sell_obj
            if obj is None:
                break
            ok, msg = self.market.post(self.party, self.player, obj, stack, start, buy, self.duration,
                                       self.market_id)
            last = msg
            if not ok:
                break
            made += 1
            still = [o for o in self._bag_goods() if o is obj]
            if not still:
                self.sell_obj = None
        if made:
            self._say(last if made == 1 else f"Listed {made} stacks. Deposits {self._fmt(dep)}.", theme.OK)
            if self.sell_obj is None:
                self.stack_box.set("")
        else:
            self._say(last, theme.BAD)

    @staticmethod
    def _fmt(c):
        from entities.coins import coins
        return coins(c)

    # ------------------------------------------------------------ events
    def handle_event(self, event):
        if self.rarity.open:
            if self.rarity.handle(event):
                return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and not self._any_focus():
            self.state_manager.transition_to(GameState.OVERWORLD)
            return
        for key, _label, r in self._tab_rects():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and r.collidepoint(event.pos):
                self.tab = key
                self.selected = None
                self.mine_selected = None
                return
        if self.close_btn.clicked(event) and self.tab != "auctions":
            self.state_manager.transition_to(GameState.OVERWORLD)
            return
        if self.tab == "browse":
            self._browse_event(event)
        elif self.tab == "bids":
            self._bids_event(event)
        else:
            self._auctions_event(event)

    def _any_focus(self):
        return any(b.focus for b in (self.name_box, self.lo_box, self.hi_box, self.stack_box, self.count_box)) or \
            self.bid_box.focus or self.start_box.focus or self.buyout_box.focus

    def _browse_event(self, event):
        for w in (self.name_box, self.lo_box, self.hi_box):
            if w.handle(event):
                return
        self.bid_box.handle(event)
        if self.exact.handle(event, self.renderer) or self.usable.handle(event, self.renderer):
            self._search()
            return
        if self.favs.handle(event, self.renderer):
            self._search()
            return
        if self.per_unit.handle(event, self.renderer):
            self._sort()
            return
        if self.rarity.handle(event):
            if not self.rarity.open:
                self._search()
            return
        if self.search_btn.clicked(event):
            self._search()
            return
        if self.reset_btn.clicked(event):
            self._reset()
            return
        if self.prev_btn.clicked(event):
            self.page = max(0, self.page - 1)
            return
        if self.next_btn.clicked(event):
            self.page = min(self._pages() - 1, self.page + 1)
            return
        if self.bid_btn.clicked(event):
            self._bid()
            return
        if self.buy_btn.clicked(event):
            self._buyout()
            return
        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if self._tree_rect().collidepoint((mx, my)):
                self.tree_scroll = max(0, min(len(self._tree_rows()) - ROWS - 1, self.tree_scroll - event.y))
            elif self._table_rect().collidepoint((mx, my)):
                self.page = max(0, min(self._pages() - 1, self.page - event.y))
            return
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        # the tree
        tr = self._tree_rect()
        if tr.collidepoint(event.pos):
            i = (event.pos[1] - tr.y - 4) // 24 + self.tree_scroll
            rows = self._tree_rows()
            if 0 <= i < len(rows):
                label, cat, sub, depth = rows[i]
                if cat == "__fav__":
                    self.favs.checked = not self.favs.checked
                    self.cat = self.sub = None
                elif sub is None:
                    if self.cat == cat and self.sub is None:
                        self.cat = None
                        self.expanded.discard(cat)
                    else:
                        self.cat, self.sub = cat, None
                        self.expanded.add(cat)
                else:
                    self.cat, self.sub = cat, sub
                self._search()
            return
        self._table_click(event)

    def _table_click(self, event):
        t = self._table_rect()
        cols = self._cols(t.x, t.right, self.tab)
        # header: sort
        if pygame.Rect(t.x, t.y, t.width, 24).collidepoint(event.pos) and self.tab == "browse":
            for k, _l, x, w in cols:
                if x <= event.pos[0] < x + w and k in ("name", "lvl", "time", "seller", "bid", "buyout"):
                    col, d = self.sort
                    self.sort = (k, -d if col == k else 1)
                    self._sort()
            return
        for i, a in enumerate(self._rows()):
            r = self._row_rect(i)
            if r.collidepoint(event.pos):
                star = pygame.Rect(r.x + 2, r.y + 6, 18, 18)
                if star.collidepoint(event.pos):
                    on = self.market.toggle_favourite(a.name)
                    self._say(f"{a.name} {'added to' if on else 'removed from'} your favourites.", theme.ACCENT)
                    return
                if self.tab == "auctions":
                    self.mine_selected = a.id
                else:
                    self.selected = a.id
                    nxt = min_next_bid(a) if a.bidder != PLAYER else a.bid + max(1, math.ceil(a.bid * 0.05))
                    self.bid_box.set(nxt)
                return

    def _sel(self):
        if self.selected is None:
            return None
        return self.market.books[self.market_id].get(self.selected)

    def _bid(self):
        a = self._sel()
        if a is None:
            self._say("Pick an auction first.", theme.WARN)
            return
        ok, msg = self.market.place_bid(self.party, a.id, self.bid_box.value, self.market_id)
        self._say(msg, theme.OK if ok else theme.BAD)

    def _buyout(self):
        a = self._sel()
        if a is None:
            self._say("Pick an auction first.", theme.WARN)
            return
        ok, msg = self.market.buyout(self.party, a.id, self.market_id)
        self._say(msg, theme.OK if ok else theme.BAD)
        if ok:
            self.selected = None
            self._search(keep_page=True)

    def _bids_event(self, event):
        self.bid_box.handle(event)
        if self.bid_btn.clicked(event):
            self._bid()
            return
        if self.buy_btn.clicked(event):
            self._buyout()
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._table_click(event)

    def _auctions_event(self, event):
        for w in (self.stack_box, self.count_box):
            if w.handle(event):
                if w is self.stack_box and self.sell_obj is not None and event.type == pygame.KEYDOWN:
                    start, buy = self.market.suggest(self.market_id, self.sell_obj, max(1, self.stack_box.value))
                    self.start_box.set(start)
                    self.buyout_box.set(buy)
                return
        if self.start_box.handle(event) or self.buyout_box.handle(event):
            return
        if self.create_btn.clicked(event):
            self._create()
            return
        if self.cancel_btn.clicked(event):
            if self.mine_selected is None:
                self._say("Pick one of your auctions first.", theme.WARN)
                return
            ok, msg = self.market.cancel(self.party, self.mine_selected, self.market_id)
            self._say(msg, theme.OK if ok else theme.BAD)
            self.mine_selected = None
            return
        if event.type == pygame.MOUSEWHEEL:
            if pygame.Rect(WIN.x + 16, WIN.y + 96, 345, 196).collidepoint(pygame.mouse.get_pos()):
                n = len(self._bag_goods())
                self.bag_scroll = max(0, min(max(0, (n - 1) // 7 - 3), self.bag_scroll - event.y))
            return
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        goods = self._bag_goods()
        for i in range(28):
            j = i + self.bag_scroll * 7
            if j < len(goods) and self._bag_rect(i).collidepoint(event.pos):
                self._pick_sell(goods[j])
                return
        for d, r in self._duration_rects():
            if r.collidepoint(event.pos):
                self.duration = d
                return
        self._table_click(event)

    def _duration_rects(self):
        sx, sy = WIN.x + 16, WIN.y + 70
        return [(d, pygame.Rect(sx + 96 + i * 80, sy + 396, 74, 26)) for i, d in enumerate(DURATIONS)]

    def update(self, dt):
        if self.message_t > 0:
            self.message_t -= dt

    # ------------------------------------------------------------ drawing
    def _background(self, screen):
        key = self.market_id
        bg = self._bg.get(key)
        if bg is None:
            path = "assets/ui/auction/goblin_hall.jpg" if key == "goblin" else "assets/ui/auction/horde_hall.jpg"
            try:
                img = pygame.image.load(path).convert()
                bg = pygame.transform.smoothscale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except Exception:
                bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                bg.fill(theme.SCREEN_BG)
            self._bg[key] = bg
        screen.blit(bg, (0, 0))
        veil = pygame.Surface((WIN.width, WIN.height), pygame.SRCALPHA)
        veil.fill((14, 12, 18, 218))
        screen.blit(veil, WIN.topleft)
        pygame.draw.rect(screen, theme.FRAME, WIN, 2)
        pygame.draw.rect(screen, theme.FRAME_INNER, WIN.inflate(-6, -6), 1)

    def render(self, screen):
        self._hover = None
        self._background(screen)
        m = self.market
        title = MARKETS[self.market_id]["name"]
        self.renderer.draw_text(screen, title, (WIN.centerx, WIN.y + 8), size="large", color=theme.TEXT_HEADING,
                                center=True)
        screen.blit(ui_icon("gavel", 34), (WIN.x + 14, WIN.y + 8))
        news = [n for n in m.news if n["market"] == self.market_id]
        who = getattr(self.auctioneer, "name", None)
        line = news[-1]["text"] if news and m.clock - news[-1]["at"] < 72 else GREETING[self.market_id]
        if who:
            line = f"{who}: \"{line}\""
        self.renderer.draw_text(screen, self.renderer.truncate(line, WIN.width - 40, size="small"),
                                (WIN.centerx, WIN.y + 44), size="small", color=theme.TEXT_DIM, center=True)
        for key, label, r in self._tab_rects():
            on = key == self.tab
            self.renderer.draw_vgradient(screen, r, (60, 52, 40) if on else theme.BTN_TOP, theme.BTN_BOTTOM)
            pygame.draw.rect(screen, theme.FRAME_SELECTED if on else theme.FRAME, r, 2)
            n = ""
            if key == "bids":
                n = f" ({len(m.bids(self.market_id))})" if m.bids(self.market_id) else ""
            if key == "auctions":
                k = len(m.my_auctions(self.market_id))
                n = f" ({k})" if k else ""
            self.renderer.draw_text(screen, label + n, (r.centerx, r.y + 7), color=theme.TEXT if on else
                                    theme.TEXT_DIM, center=True)
        if self.tab == "browse":
            self._render_browse(screen)
        elif self.tab == "bids":
            self._render_bids(screen)
        else:
            self._render_auctions(screen)
        # money, bottom left, always
        mx = WIN.x + 18
        my = WIN.bottom - 38
        self.renderer.draw_text(screen, "Your money", (mx, my - 16), size="small", color=theme.TEXT_DIM)
        draw_coins(self.renderer, screen, self.party.copper, (mx, my + 2), size="normal", icon=16)
        if self.message_t > 0 and self.message:
            self.renderer.draw_text(screen, self.message, (WIN.centerx, WIN.bottom - 70), size="small",
                                    color=self.message_col, center=True)
        self.rarity.draw_open(self.renderer, screen)
        self._draw_hover(screen)

    def _render_browse(self, screen):
        r = self.renderer
        for w in (self.name_box, self.lo_box, self.hi_box):
            w.draw(r, screen)
        r.draw_text(screen, "Name", (self.name_box.rect.x, self.name_box.rect.y - 17), size="small",
                    color=theme.TEXT_DIM)
        r.draw_text(screen, "Level Range", (self.lo_box.rect.x, self.lo_box.rect.y - 17), size="small",
                    color=theme.TEXT_DIM)
        r.draw_text(screen, "-", (self.lo_box.rect.right + 5, self.lo_box.rect.y + 3), color=theme.TEXT_DIM)
        r.draw_text(screen, "Rarity", (self.rarity.rect.x, self.rarity.rect.y - 17), size="small",
                    color=theme.TEXT_DIM)
        screen.blit(ui_icon("magnifier", 18), (self.name_box.rect.right - 22, self.name_box.rect.y + 3))
        self.exact.draw(r, screen)
        self.usable.draw(r, screen)
        self.favs.draw(r, screen)
        self.rarity.draw(r, screen)
        self.search_btn.draw(r, screen)
        self.reset_btn.draw(r, screen)
        self._render_tree(screen)
        self._render_table(screen, self._rows())
        # pages
        t = self._table_rect()
        if self.results:
            a, b = self.page * ROWS + 1, min(len(self.results), (self.page + 1) * ROWS)
            r.draw_text(screen, f"Items {a} - {b} of {len(self.results)}    Page {self.page + 1} of {self._pages()}",
                        (t.x + 160, t.bottom + 10), size="small", color=theme.TEXT_DIM)
        elif self.searched:
            r.draw_text(screen, "No items found.", (t.centerx, t.y + 80), color=theme.TEXT_DIM, center=True)
        self.prev_btn.enabled = self.page > 0
        self.next_btn.enabled = self.page < self._pages() - 1
        self.prev_btn.draw(r, screen)
        self.next_btn.draw(r, screen)
        self.per_unit.draw(r, screen)
        self._render_buy_bar(screen)

    def _render_buy_bar(self, screen):
        r = self.renderer
        a = self._sel()
        self.bid_btn.enabled = a is not None and not a.mine
        self.buy_btn.enabled = a is not None and not a.mine and bool(a.buyout) and \
            self.party.copper + (a.bid if a.bidder == PLAYER else 0) >= a.buyout
        self.bid_box.draw(r, screen, label="Your bid")
        self.bid_btn.draw(r, screen)
        self.buy_btn.draw(r, screen)
        self.close_btn.draw(r, screen)

    def _render_tree(self, screen):
        r = self.renderer
        tr = self._tree_rect()
        r.draw_panel(screen, tr, inset=True, studs=False)
        rows = self._tree_rows()
        clip = screen.get_clip()
        screen.set_clip(tr.inflate(-4, -4))
        for i, (label, cat, sub, depth) in enumerate(rows[self.tree_scroll:]):
            y = tr.y + 4 + i * 24
            if y > tr.bottom - 24:
                break
            rr = pygame.Rect(tr.x + 3, y, tr.width - 6, 22)
            on = (cat == "__fav__" and self.favs.checked) or (cat == self.cat and sub == self.sub)
            hover = rr.collidepoint(pygame.mouse.get_pos())
            if on or hover:
                pygame.draw.rect(screen, (70, 58, 34) if on else (40, 37, 46), rr)
            x = tr.x + 10 + depth * 16
            if cat == "__fav__":
                screen.blit(ui_icon("star", 16), (x, y + 3))
                x += 20
            elif depth == 0:
                sign = "-" if cat in self.expanded else "+"
                if C.TREE and dict(C.TREE).get(cat):
                    r.draw_text(screen, sign, (x, y + 2), size="small", color=theme.ACCENT)
                x += 14
            r.draw_text(screen, label, (x, y + 3), size="small",
                        color=theme.TEXT_HEADING if depth == 0 else theme.TEXT)
        screen.set_clip(clip)

    def _render_table(self, screen, rows):
        r = self.renderer
        t = self._table_rect()
        r.draw_panel(screen, t, inset=True, studs=False)
        cols = self._cols(t.x, t.right, self.tab)
        col, d = self.sort
        for k, label, x, w in cols:
            txt = label
            if self.tab == "browse" and k == col:
                txt += " ^" if d > 0 else " v"
            if k in ("bid", "buyout") and self.per_unit.checked and self.tab == "browse":
                txt += " (each)"
            r.draw_text(screen, txt, (x + (30 if k == "name" else 6), t.y + 4), size="small", color=theme.TEXT_HEADING)
        pygame.draw.line(screen, theme.FRAME_INNER, (t.x + 4, t.y + 23), (t.right - 4, t.y + 23))
        mouse = pygame.mouse.get_pos()
        m = self.market
        for i, a in enumerate(rows):
            rr = self._row_rect(i)
            sel = (a.id == self.selected) if self.tab != "auctions" else (a.id == self.mine_selected)
            if sel:
                pygame.draw.rect(screen, (74, 60, 30), rr)
                pygame.draw.rect(screen, theme.FRAME_SELECTED, rr, 1)
            elif rr.collidepoint(mouse):
                pygame.draw.rect(screen, (36, 33, 42), rr)
            if a.fat or a.mine or (a.seller_id or "").startswith("recruit:"):
                pass
            for k, _l, x, w in cols:
                cy = rr.y + 7
                if k == "name":
                    star_on = a.name in m.favourites
                    st = ui_icon("star", 16).copy()
                    if not star_on:
                        st.set_alpha(55)
                    screen.blit(st, (x + 4, rr.y + 7))
                    draw_icon(screen, self.icons, a.icon, pygame.Rect(x + 24, rr.y + 1, 28, 28), a.rarity)
                    name = r.truncate(a.name, w - 72, size="small")
                    r.draw_text(screen, name, (x + 58, cy), size="small", color=RARITY_COLOUR.get(a.rarity, theme.TEXT))
                    if a.qty > 1:
                        _qty(r, screen, a.qty, pygame.Rect(x + 24, rr.y + 1, 28, 28))
                    if rr.collidepoint(mouse) and x <= mouse[0] < x + w:
                        self._hover = ("item", a)
                elif k == "lvl":
                    r.draw_text(screen, str(a.level or ""), (x + w // 2, cy), size="small", color=theme.TEXT,
                                center=True)
                elif k == "time":
                    band = m.time_left(a)
                    screen.blit(ui_icon(TIME_ICON[band], 20), (x + 4, rr.y + 5))
                    r.draw_text(screen, band, (x + 26, cy), size="small",
                                color=theme.BAD if band == "Short" else theme.TEXT)
                elif k == "seller":
                    name, _detail = m.seller_info(a)
                    col_ = theme.OK if (a.seller_id or "").startswith("recruit:") else (
                        theme.ACCENT if a.mine else theme.TEXT)
                    r.draw_text(screen, r.truncate(name, w - 10, size="small"), (x + 6, cy), size="small", color=col_)
                    if rr.collidepoint(mouse) and x <= mouse[0] < x + w:
                        self._hover = ("seller", a)
                elif k == "bidder":
                    if a.bidder:
                        r.draw_text(screen, r.truncate(str(a.bidder), w - 10, size="small"), (x + 6, cy), size="small")
                    else:
                        r.draw_text(screen, "No bids", (x + 6, cy), size="small", color=theme.TEXT_DIM)
                elif k == "status":
                    win = a.bidder == PLAYER
                    r.draw_text(screen, "Winning" if win else "Outbid", (x + 6, cy), size="small",
                                color=theme.OK if win else theme.BAD)
                elif k == "bid":
                    unit = self.per_unit.checked and self.tab == "browse"
                    v = a.bid or a.min_bid
                    v = int(math.ceil(v / a.qty)) if unit else v
                    colr = theme.OK if a.bidder == PLAYER else (theme.TEXT if a.bid else theme.TEXT_DIM)
                    draw_coins(r, screen, v, (x + w - 8, cy), right=True, colour=colr)
                elif k == "buyout":
                    if a.buyout:
                        unit = self.per_unit.checked and self.tab == "browse"
                        v = int(math.ceil(a.buyout / a.qty)) if unit else a.buyout
                        draw_coins(r, screen, v, (x + w - 8, cy), right=True)
                    else:
                        r.draw_text(screen, "Bid only", (x + w - 64, cy), size="small", color=theme.TEXT_DIM)
            if self.tab == "bids" and rr.collidepoint(mouse):
                self._hover = self._hover or ("item", a)
        if not rows and self.tab != "browse":
            r.draw_text(screen, "Nothing here yet." if self.tab == "bids" else "You have no auctions running.",
                        (t.centerx, t.y + 60), color=theme.TEXT_DIM, center=True)

    def _render_bids(self, screen):
        self.renderer.draw_text(screen, "Auctions you've bid on. Outbid ones stay until they end, so you can bid again.",
                                (WIN.x + 18, WIN.y + 64 - 14), size="small", color=theme.TEXT_DIM)
        self._render_table(screen, self._rows())
        self._render_buy_bar(screen)

    def _render_auctions(self, screen):
        r = self.renderer
        m = self.market
        sx, sy = WIN.x + 16, WIN.y + 70
        r.draw_text(screen, "Create Auction", (sx, sy - 6), color=theme.TEXT_HEADING)
        r.draw_text(screen, "Pick something from your bags", (sx + 150, sy - 3), size="small", color=theme.TEXT_DIM)
        goods = self._bag_goods()
        mouse = pygame.mouse.get_pos()
        for i in range(28):
            j = i + self.bag_scroll * 7
            rr = self._bag_rect(i)
            pygame.draw.rect(screen, (16, 15, 20), rr)
            pygame.draw.rect(screen, theme.FRAME_INNER, rr, 1)
            if j < len(goods):
                obj = goods[j]
                rar = C.rarity_of(G.pack(obj))
                draw_icon(screen, self.icons, obj, rr, rar)
                q = 1 if G.kind_of(obj) == G.GEAR else int(getattr(obj, "quantity", 1) or 1)
                if q > 1:
                    _qty(r, screen, q, rr)
                if obj is self.sell_obj:
                    pygame.draw.rect(screen, theme.FRAME_SELECTED, rr, 2)
                if rr.collidepoint(mouse):
                    self._hover = ("bag", obj)
        if len(goods) > 28:
            r.draw_text(screen, "Scroll for more", (sx + 250, sy + 228), size="small", color=theme.TEXT_DIM)
        # the chosen thing
        y = sy + 238
        pygame.draw.line(screen, theme.FRAME_INNER, (sx, y), (sx + 345, y))
        obj = self.sell_obj
        if obj is not None and obj not in goods:
            self.sell_obj = obj = None
        if obj is None:
            r.draw_text(screen, "Nothing chosen yet.", (sx, y + 14), color=theme.TEXT_DIM)
        else:
            good = G.pack(obj)
            draw_icon(screen, self.icons, obj, pygame.Rect(sx, y + 8, 40, 40), C.rarity_of(good))
            r.draw_text(screen, r.truncate(obj.name, 290, size="normal"), (sx + 48, y + 8),
                        color=RARITY_COLOUR.get(C.rarity_of(good), theme.TEXT))
            going, value, idx = m.going_for(obj, self.market_id)
            r.draw_text(screen, "Going price each", (sx + 48, y + 30), size="small", color=theme.TEXT_DIM)
            draw_coins(r, screen, int(going), (sx + 345, y + 30), right=True)
            trend = "rising" if idx > 1.15 else "falling" if idx < 0.87 else ""
            if trend:
                r.draw_text(screen, trend, (sx + 160, y + 30), size="small", color=theme.OK if trend == "rising"
                            else theme.BAD)
        r.draw_text(screen, "Stack size", (sx, sy + 300), size="small", color=theme.TEXT_DIM)
        self.stack_box.draw(r, screen)
        nums = self._sell_numbers()
        if nums:
            have, stack, count, dep = nums
            r.draw_text(screen, f"of {have}", (self.stack_box.rect.right + 6, sy + 300), size="small",
                        color=theme.TEXT_DIM)
        r.draw_text(screen, "Stacks", (sx + 210, sy + 300), size="small", color=theme.TEXT_DIM)
        self.count_box.draw(r, screen)
        r.draw_text(screen, "Starting bid", (sx, sy + 334), size="small", color=theme.TEXT_DIM)
        self.start_box.draw(r, screen)
        r.draw_text(screen, "Buyout", (sx, sy + 368), size="small", color=theme.TEXT_DIM)
        self.buyout_box.draw(r, screen)
        r.draw_text(screen, "Duration", (sx, sy + 401), size="small", color=theme.TEXT_DIM)
        for d, rr in self._duration_rects():
            on = d == self.duration
            pygame.draw.rect(screen, (70, 58, 34) if on else (20, 19, 24), rr)
            pygame.draw.rect(screen, theme.FRAME_SELECTED if on else theme.FRAME_INNER, rr, 1)
            r.draw_text(screen, f"{d} hours", (rr.centerx, rr.y + 5), size="small", center=True,
                        color=theme.TEXT if on else theme.TEXT_DIM)
        r.draw_text(screen, "Deposit", (sx, sy + 430), size="small", color=theme.TEXT_DIM)
        if nums:
            draw_coins(r, screen, nums[3], (sx + 96, sy + 430))
            if nums[2] > 1:
                r.draw_text(screen, f"for {nums[2]} stacks", (sx + 170, sy + 430), size="small", color=theme.TEXT_DIM)
        cut = int(MARKETS[self.market_id]["cut"] * 100)
        r.draw_text(screen, f"House cut {cut}%", (sx + 262, sy + 430), size="small", color=theme.TEXT_DIM)
        self.create_btn.enabled = obj is not None
        self.create_btn.draw(r, screen)
        # the competition
        cx, cy = WIN.x + 392, WIN.y + 70
        r.draw_text(screen, "Others selling it" if obj is not None else "Your auctions", (cx, cy - 6),
                    color=theme.TEXT_HEADING)
        if obj is not None:
            comp = m.competition(self.market_id, obj)[:6]
            box = pygame.Rect(cx, cy + 22, WIN.right - 16 - cx, 6 * 28 + 8)
            r.draw_panel(screen, box, inset=True, studs=False)
            if not comp:
                r.draw_text(screen, "Nobody else has one up. Name your price.", (box.x + 12, box.y + 12),
                            size="small", color=theme.TEXT_DIM)
            for i, a in enumerate(comp):
                y = box.y + 6 + i * 28
                name, _d = m.seller_info(a)
                r.draw_text(screen, f"{a.qty} x", (box.x + 10, y + 5), size="small")
                r.draw_text(screen, r.truncate(name, 200, size="small"), (box.x + 60, y + 5), size="small",
                            color=theme.ACCENT if a.mine else theme.TEXT)
                r.draw_text(screen, m.time_left(a), (box.x + 280, y + 5), size="small", color=theme.TEXT_DIM)
                r.draw_text(screen, "each", (box.right - 200, y + 5), size="small", color=theme.TEXT_DIM)
                draw_coins(r, screen, int(math.ceil(a.buyout / a.qty)), (box.right - 210, y + 5), right=True)
                draw_coins(r, screen, a.buyout, (box.right - 10, y + 5), right=True)
        r.draw_text(screen, "Your auctions", (cx, self._table_rect().y - 22), color=theme.TEXT_HEADING)
        self._render_table(screen, self._rows())
        self.cancel_btn.enabled = self.mine_selected is not None
        self.cancel_btn.draw(r, screen)

    def _draw_hover(self, screen):
        if not self._hover or self.rarity.open:
            return
        kind, x = self._hover
        m = self.market
        pos = pygame.mouse.get_pos()
        if kind == "seller":
            name, detail = m.seller_info(x)
            lines = [(name, theme.TEXT_HEADING)]
            if detail:
                lines.append((detail, theme.TEXT_DIM))
            draw_tooltip(self.renderer, screen, lines, pos, width=260)
            return
        if kind == "bag":
            good = G.pack(x)
            going, _v, _i = m.going_for(x, self.market_id)
            extra = [(f"__price__Going price each|{int(going)}", theme.ACCENT)]
            draw_tooltip(self.renderer, screen, good_lines(good), pos, extra=extra)
            return
        good = m.good_of(x)
        if good is None:
            return
        extra = []
        if x.buyout:
            extra.append((f"__price__Buyout|{x.buyout}", theme.ACCENT))
            if x.qty > 1:
                extra.append((f"__price__Buyout each|{int(math.ceil(x.buyout / x.qty))}", theme.TEXT_DIM))
        extra.append((f"__price__{'Current bid' if x.bid else 'Starting bid'}|{x.bid or x.min_bid}", theme.TEXT))
        if x.bidder == PLAYER:
            extra.append(("You're the high bidder.", theme.OK))
        if (x.seller_id or "").startswith("recruit:"):
            extra.append((f"{x.seller} is selling this. They're in your party.", theme.OK))
        draw_tooltip(self.renderer, screen, good_lines(good), pos, extra=extra)
