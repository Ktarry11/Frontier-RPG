"""The mailbox: WoW's inbox and Send Mail (docs/auction_house_design.md, section 11).

Kyle, 15 Nov 2026: "MAILBOX and MAIL SERVICE". Everything the auction house pays, refunds, returns or hands over
arrives here, and so do the letters from the other traders (world/market/meme_mail.py) and their cash-on-delivery
offers. Send Mail posts things to your own recruits, in the party or on the bench. Friends writes to the ones who've
gone home and asks them to meet you at a town you pick (world/recruit_mail.py).
"""
import pygame

from config import SCREEN_HEIGHT, SCREEN_WIDTH
from core.game_states import GameState
from ui import theme
from ui.market_widgets import (RARITY_COLOUR, Button, Dropdown, TextBox, draw_coins, draw_icon, draw_tooltip,
                               good_lines, ui_icon)
from ui.screens.auction_screen import _qty
from ui.screens.base_screen import BaseScreen
from world.market import catalog as C
from world.market import goods as G
from world.market.market import market_of
from world.mail import MAX_ATTACH, Mailbox

WIN = pygame.Rect(60, 24, SCREEN_WIDTH - 120, 630)
PER_PAGE = 7
ROW = 70


class MailScreen(BaseScreen):
    def __init__(self, state_manager, icon_ui_helper=None):
        super().__init__(state_manager)
        self._icons = icon_ui_helper
        self.tab = "inbox"
        self.page = 0
        self.open_id = None
        self.message, self.message_col, self.message_t = "", theme.TEXT, 0.0
        lx = WIN.x + 470
        self.take_money_btn = Button((WIN.right - 136, WIN.y + 380, 116, 30), "Take")
        self.take_all_btn = Button((lx, WIN.bottom - 52, 130, 34), "Take All")
        self.cod_btn = Button((lx, WIN.bottom - 52, 210, 34), "Pay")
        self.delete_btn = Button((WIN.right - 276, WIN.bottom - 52, 126, 34), "Delete")
        self.return_btn = Button((WIN.right - 142, WIN.bottom - 52, 126, 34), "Return")
        self.prev_btn = Button((WIN.x + 16, WIN.bottom - 52, 90, 34), "Prev")
        self.next_btn = Button((WIN.x + 346, WIN.bottom - 52, 90, 34), "Next")
        self.close_btn = Button((WIN.right - 110, WIN.y + 10, 94, 30), "Close")
        # send
        sx, sy = WIN.x + 20, WIN.y + 90
        self.to = Dropdown((sx + 80, sy, 260, 26), [("Nobody to send to", None, None)])
        self.subject = TextBox((sx + 80, sy + 40, 420, 26), max_len=40, placeholder="Subject")
        self.body = TextBox((sx + 80, sy + 80, 520, 26), max_len=160, placeholder="A short note")
        self.attach = []
        self.send_btn = Button((sx, WIN.bottom - 52, 160, 34), "Send")
        self.bag_scroll = 0
        self._bg = None
        self._hover = None
        # friends
        self.friend_page = 0
        self.friend_id = None
        self.town_index = 0
        fx = WIN.x + 470
        self.town_prev = Button((fx + 96, WIN.y + 250, 34, 30), "<")
        self.town_next = Button((WIN.right - 50, WIN.y + 250, 34, 30), ">")
        self.write_btn = Button((fx, WIN.bottom - 52, 200, 34), "Write to them")

    @property
    def icons(self):
        return self._icons or getattr(self.state_manager, "icon_ui_helper", None)

    def open(self, encoding="utf-8"):
        self.page = 0
        self.open_id = None
        m = market_of(self.party)
        # you're standing at a mailbox, so this town is somewhere you can ask people to meet you
        try:
            from world import recruit_mail
            from world.bond_manager import get_bond_manager
            zm = getattr(self.state_manager, "zone_manager", None)
            if zm is not None and getattr(zm, "current_zone", None) is not None:
                recruit_mail.note_town(get_bond_manager(), zm.current_zone)
        except Exception:
            pass
        m.advance(0)
        self._refresh_to()

    @property
    def party(self):
        return self.state_manager.get_party()

    @property
    def player(self):
        return self.state_manager.player

    @property
    def box(self) -> Mailbox:
        return market_of(self.party).mail

    @property
    def now(self):
        return market_of(self.party).clock

    def _say(self, text, col=None):
        self.message, self.message_col, self.message_t = text, col or theme.TEXT, 5.0

    def _refresh_to(self):
        people = [m for m in list(getattr(self.party, "members", []))[1:] + list(getattr(self.party, "bench", []))]
        opts = [(p.name + ("" if p in self.party.members else " (bench)"), p.name, None) for p in people]
        self.to.options = opts or [("Nobody to send to", None, None)]
        self.to.index = min(self.to.index, len(self.to.options) - 1)

    def _letters(self):
        return self.box.visible(self.now)

    def _current(self):
        for x in self._letters():
            if x.id == self.open_id:
                return x
        return None

    # ------------------------------------------------------------ geometry
    def _row_rect(self, i):
        return pygame.Rect(WIN.x + 16, WIN.y + 64 + i * ROW, 420, ROW - 6)

    def _item_rect(self, i):
        c, r = i % 6, i // 6
        return pygame.Rect(WIN.x + 470 + c * 58, WIN.y + 430 + r * 58, 52, 52)

    def _tab_rects(self):
        return [("inbox", "Inbox", pygame.Rect(WIN.x + 20, WIN.bottom + 2, 120, 32)),
                ("send", "Send Mail", pygame.Rect(WIN.x + 146, WIN.bottom + 2, 120, 32)),
                ("friends", "Friends", pygame.Rect(WIN.x + 272, WIN.bottom + 2, 120, 32))]

    def _bag_rect(self, i):
        c, r = i % 8, i // 8
        return pygame.Rect(WIN.right - 16 - 8 * 50 + c * 50, WIN.y + 90 + r * 50, 46, 46)

    def _attach_rect(self, i):
        c, r = i % 6, i // 6
        return pygame.Rect(WIN.x + 100 + c * 56, WIN.y + 250 + r * 56, 50, 50)

    # ------------------------------------------------------------ events
    def handle_event(self, event):
        if self.to.open:
            self.to.handle(event)
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and not (self.subject.focus or self.body.focus):
            self._leave()
            return
        for key, _l, r in self._tab_rects():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and r.collidepoint(event.pos):
                self.tab = key
                self._refresh_to()
                return
        if self.close_btn.clicked(event):
            self._leave()
            return
        if self.tab == "inbox":
            self._inbox_event(event)
        elif self.tab == "friends":
            self._friends_event(event)
        else:
            self._send_event(event)

    def _leave(self):
        # anything still in the attach list goes back to the bags
        for g in self.attach:
            G.give(self.player, g)
        self.attach = []
        self.state_manager.transition_to(GameState.OVERWORLD)

    def _inbox_event(self, event):
        letters = self._letters()
        pages = max(1, (len(letters) + PER_PAGE - 1) // PER_PAGE)
        if self.prev_btn.clicked(event):
            self.page = max(0, self.page - 1)
            return
        if self.next_btn.clicked(event):
            self.page = min(pages - 1, self.page + 1)
            return
        cur = self._current()
        if cur is not None:
            if cur.cod and cur.goods:
                if self.cod_btn.clicked(event):
                    ok, msg = self.box.pay_cod(cur, self.party, self.player)
                    self._say(msg, theme.OK if ok else theme.BAD)
                    return
                if self.return_btn.clicked(event):
                    self.box.refuse_cod(cur)
                    self._say(f"Sent back to {cur.sender}.", theme.TEXT)
                    self.open_id = None
                    return
            else:
                if self.take_money_btn.clicked(event) and cur.copper:
                    n = self.box.take_money(cur, self.party)
                    from entities.coins import coins
                    self._say(f"Took {coins(n)}.", theme.OK)
                    return
                if self.take_all_btn.clicked(event):
                    got, n, left = self.box.take_all(cur, self.party, self.player)
                    if left:
                        self._say("Your bags are full. The rest stays in the letter.", theme.WARN)
                    elif got or n:
                        self._say("Took everything.", theme.OK)
                    return
                if self.delete_btn.clicked(event):
                    if self.box.delete(cur):
                        self.open_id = None
                        self._say("Deleted.", theme.TEXT_DIM)
                    else:
                        self._say("Take the money and items out first.", theme.WARN)
                    return
                if self.return_btn.clicked(event) and cur.can_return and not cur.empty:
                    if self.box.return_to_sender(cur, self.now):
                        self.open_id = None
                        self._say("Returned.", theme.TEXT)
                    return
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i in range(len(cur.goods)):
                        if self._item_rect(i).collidepoint(event.pos):
                            ok, msg = self.box.take_good(cur, i, self.player)
                            self._say(msg, theme.OK if ok else theme.BAD)
                            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            shown = letters[self.page * PER_PAGE:(self.page + 1) * PER_PAGE]
            for i, x in enumerate(shown):
                if self._row_rect(i).collidepoint(event.pos):
                    self.open_id = x.id
                    x.read = True
                    return
        if event.type == pygame.MOUSEWHEEL:
            self.page = max(0, min(pages - 1, self.page - event.y))

    def _send_event(self, event):
        if self.to.handle(event):
            return
        if self.subject.handle(event) or self.body.handle(event):
            return
        if self.send_btn.clicked(event):
            self._send()
            return
        if event.type == pygame.MOUSEWHEEL:
            n = len(G.tradeable_goods(self.player))
            self.bag_scroll = max(0, min(max(0, (n - 1) // 8 - 7), self.bag_scroll - event.y))
            return
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        for i, g in enumerate(list(self.attach)):
            if self._attach_rect(i).collidepoint(event.pos):
                if G.give(self.player, g):
                    self.attach.remove(g)
                return
        goods = G.tradeable_goods(self.player)
        for i in range(64):
            j = i + self.bag_scroll * 8
            if j < len(goods) and self._bag_rect(i).collidepoint(event.pos):
                if len(self.attach) >= MAX_ATTACH:
                    self._say(f"A letter holds {MAX_ATTACH} things at most.", theme.WARN)
                    return
                g = G.take(self.player, goods[j])
                if g is not None:
                    self.attach.append(g)
                return

    def _send(self):
        to = self.to.value
        if not to:
            self._say("You need a recruit to send it to.", theme.WARN)
            return
        if not self.attach and not self.body.text:
            self._say("Attach something or write a note.", theme.WARN)
            return
        cost = Mailbox.postage(len(self.attach))
        if not self.party.remove_currency(cost):
            self._say("You can't afford the postage.", theme.BAD)
            return
        self.box.send(to, self.subject.text or "A parcel", self.body.text, self.attach, self.now)
        self.attach = []
        self.subject.set("")
        self.body.set("")
        from entities.coins import coins
        self._say(f"Sent to {to}. It'll be with them in about an hour. Postage {coins(cost)}.", theme.OK)

    def update(self, dt):
        if self.message_t > 0:
            self.message_t -= dt

    # ------------------------------------------------------------ drawing
    def render(self, screen):
        self._hover = None
        if self._bg is None:
            try:
                img = pygame.image.load("assets/ui/auction/horde_hall.jpg").convert()
                self._bg = pygame.transform.smoothscale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except Exception:
                self._bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                self._bg.fill(theme.SCREEN_BG)
        screen.blit(self._bg, (0, 0))
        veil = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        veil.fill((10, 9, 13, 150))
        screen.blit(veil, (0, 0))
        panel = pygame.Surface(WIN.size, pygame.SRCALPHA)
        panel.fill((16, 14, 20, 232))
        screen.blit(panel, WIN.topleft)
        pygame.draw.rect(screen, theme.FRAME, WIN, 2)
        r = self.renderer
        screen.blit(ui_icon("mail_flag_up" if self.box.unread(self.now) else "mail_flag_down", 34),
                    (WIN.x + 14, WIN.y + 8))
        r.draw_text(screen, "Mailbox", (WIN.x + 56, WIN.y + 10), size="large", color=theme.TEXT_HEADING)
        self.close_btn.draw(r, screen)
        for key, label, rr in self._tab_rects():
            on = key == self.tab
            r.draw_vgradient(screen, rr, (60, 52, 40) if on else theme.BTN_TOP, theme.BTN_BOTTOM)
            pygame.draw.rect(screen, theme.FRAME_SELECTED if on else theme.FRAME, rr, 2)
            n = self.box.unread(self.now) if key == "inbox" else 0
            r.draw_text(screen, label + (f" ({n})" if n else ""), (rr.centerx, rr.y + 7), center=True,
                        color=theme.TEXT if on else theme.TEXT_DIM)
        if self.tab == "inbox":
            self._render_inbox(screen)
        elif self.tab == "friends":
            self._render_friends(screen)
        else:
            self._render_send(screen)
        if self.message_t > 0:
            r.draw_text(screen, self.message, (WIN.centerx, WIN.bottom - 86), size="small", color=self.message_col,
                        center=True)
        self.to.draw_open(r, screen) if self.tab == "send" else None
        if self._hover:
            draw_tooltip(r, screen, good_lines(self._hover, self.player), pygame.mouse.get_pos())

    def _render_inbox(self, screen):
        r = self.renderer
        letters = self._letters()
        pages = max(1, (len(letters) + PER_PAGE - 1) // PER_PAGE)
        self.page = min(self.page, pages - 1)
        shown = letters[self.page * PER_PAGE:(self.page + 1) * PER_PAGE]
        mouse = pygame.mouse.get_pos()
        if not letters:
            r.draw_text(screen, "No mail.", (WIN.x + 226, WIN.y + 200), color=theme.TEXT_DIM, center=True)
        for i, x in enumerate(shown):
            rr = self._row_rect(i)
            sel = x.id == self.open_id
            r.draw_panel(screen, rr, selected=sel, inset=not sel, studs=False)
            if rr.collidepoint(mouse) and not sel:
                pygame.draw.rect(screen, theme.FRAME_SELECTED, rr, 1)
            screen.blit(ui_icon(x.icon, 46), (rr.x + 8, rr.y + 9))
            col = theme.TEXT if not x.read else theme.TEXT_DIM
            r.draw_text(screen, r.truncate(str(x.sender), 230, size="normal"), (rr.x + 64, rr.y + 8),
                        color=theme.TEXT_HEADING if not x.read else theme.TEXT_DIM)
            r.draw_text(screen, r.truncate(x.subject, 270, size="small"), (rr.x + 64, rr.y + 32), size="small",
                        color=col)
            tag_x = rr.right - 10
            if x.cod and x.goods:
                r.draw_text(screen, "COD", (tag_x - 34, rr.y + 8), size="small", color=theme.WARN)
            elif x.copper:
                draw_coins(r, screen, x.copper, (tag_x, rr.y + 8), right=True)
            if x.goods and not x.cod:
                screen.blit(ui_icon("parcel", 20), (tag_x - 22, rr.y + 30))
            d = x.days_left(self.now)
            if d is not None:
                r.draw_text(screen, f"{d} days", (tag_x - 52, rr.y + 46), size="small", color=theme.TEXT_DIM)
        r.draw_text(screen, f"Page {self.page + 1} of {pages}", (WIN.x + 226, WIN.bottom - 44), size="small",
                    color=theme.TEXT_DIM, center=True)
        self.prev_btn.enabled = self.page > 0
        self.next_btn.enabled = self.page < pages - 1
        self.prev_btn.draw(r, screen)
        self.next_btn.draw(r, screen)
        cur = self._current()
        lx = WIN.x + 470
        if cur is None:
            r.draw_text(screen, "Pick a letter to read it.", (lx + 220, WIN.y + 200), color=theme.TEXT_DIM, center=True)
            return
        r.draw_text(screen, "From", (lx, WIN.y + 64), size="small", color=theme.TEXT_DIM)
        r.draw_text(screen, str(cur.sender), (lx + 64, WIN.y + 62), color=theme.TEXT_HEADING)
        r.draw_text(screen, "Subject", (lx, WIN.y + 90), size="small", color=theme.TEXT_DIM)
        r.draw_text(screen, r.truncate(cur.subject, WIN.right - lx - 90, size="normal"), (lx + 64, WIN.y + 88))
        page = pygame.Rect(lx, WIN.y + 120, WIN.right - 16 - lx, 240)
        r.draw_vgradient(screen, page, (64, 54, 38), (44, 37, 27))
        pygame.draw.rect(screen, theme.FRAME_INNER, page, 1)
        y = page.y + 12
        for para in str(cur.body or "").split("\n"):
            for line in r.wrap_text(para, page.width - 28):
                r.draw_text(screen, line, (page.x + 14, y), color=(236, 224, 196))
                y += 20
            y += 4
        # money
        if cur.cod and cur.goods:
            r.draw_text(screen, "Cash on delivery", (lx, WIN.y + 384), color=theme.WARN)
            draw_coins(r, screen, cur.cod, (lx + 170, WIN.y + 386), size="normal", icon=16)
            r.draw_text(screen, "Pay it to take the items, or send them back.", (lx, WIN.y + 406), size="small",
                        color=theme.TEXT_DIM)
        elif cur.copper:
            r.draw_text(screen, "Money", (lx, WIN.y + 386), color=theme.TEXT_DIM)
            draw_coins(r, screen, cur.copper, (lx + 70, WIN.y + 388), size="normal", icon=16)
            self.take_money_btn.draw(r, screen)
        for i, g in enumerate(cur.goods):
            rr = self._item_rect(i)
            draw_icon(screen, self.icons, (g["kind"], g["data"].get("icon_id") or "", g["data"].get("material_type") or "",
                                           g["data"].get("consumable_id") or ""), rr, C.rarity_of(g))
            q = G.quantity(g)
            if q > 1:
                _qty(r, screen, q, rr)
            if rr.collidepoint(pygame.mouse.get_pos()):
                self._hover = g
        if cur.cod and cur.goods:
            from entities.coins import coins
            self.cod_btn.label = f"Pay {coins(cur.cod)}"
            self.cod_btn.enabled = self.party.copper >= cur.cod
            self.cod_btn.draw(r, screen)
            self.return_btn.enabled = True
            self.return_btn.draw(r, screen)
        else:
            self.take_all_btn.enabled = not cur.empty
            self.take_all_btn.draw(r, screen)
            self.delete_btn.enabled = cur.empty
            self.delete_btn.draw(r, screen)
            if cur.can_return:
                self.return_btn.enabled = not cur.empty
                self.return_btn.draw(r, screen)

    def _render_send(self, screen):
        r = self.renderer
        sx, sy = WIN.x + 20, WIN.y + 90
        r.draw_text(screen, "To", (sx, sy + 4), color=theme.TEXT_DIM)
        r.draw_text(screen, "Subject", (sx, sy + 44), color=theme.TEXT_DIM)
        r.draw_text(screen, "Note", (sx, sy + 84), color=theme.TEXT_DIM)
        self.to.draw(r, screen)
        self.subject.draw(r, screen)
        self.body.draw(r, screen)
        r.draw_text(screen, "Attachments (click one to take it back)", (sx, WIN.y + 226), size="small",
                    color=theme.TEXT_DIM)
        for i in range(MAX_ATTACH):
            rr = self._attach_rect(i)
            pygame.draw.rect(screen, (16, 15, 20), rr)
            pygame.draw.rect(screen, theme.FRAME_INNER, rr, 1)
            if i < len(self.attach):
                g = self.attach[i]
                draw_icon(screen, self.icons, (g["kind"], g["data"].get("icon_id") or "",
                                               g["data"].get("material_type") or "", g["data"].get("consumable_id") or ""),
                          rr, C.rarity_of(g))
                q = G.quantity(g)
                if q > 1:
                    _qty(r, screen, q, rr)
                if rr.collidepoint(pygame.mouse.get_pos()):
                    self._hover = g
        r.draw_text(screen, "Postage", (sx, WIN.y + 380), color=theme.TEXT_DIM)
        draw_coins(r, screen, Mailbox.postage(len(self.attach)), (sx + 90, WIN.y + 382))
        r.draw_text(screen, "Your party shares one purse, so there's no money to send. Items arrive in about an hour.",
                    (sx, WIN.y + 410), size="small", color=theme.TEXT_DIM)
        self.send_btn.enabled = bool(self.to.value)
        self.send_btn.draw(r, screen)
        draw_coins(r, screen, self.party.copper, (sx + 190, WIN.bottom - 42), size="normal", icon=16)
        # the bags
        bx = WIN.right - 16 - 8 * 50
        r.draw_text(screen, "Your bags (click to attach)", (bx, WIN.y + 66), size="small", color=theme.TEXT_DIM)
        goods = G.tradeable_goods(self.player)
        for i in range(64):
            j = i + self.bag_scroll * 8
            rr = self._bag_rect(i)
            if rr.bottom > WIN.bottom - 60:
                break
            pygame.draw.rect(screen, (16, 15, 20), rr)
            pygame.draw.rect(screen, theme.FRAME_INNER, rr, 1)
            if j < len(goods):
                obj = goods[j]
                good = G.pack(obj)
                draw_icon(screen, self.icons, obj, rr, C.rarity_of(good))
                q = 1 if G.kind_of(obj) == G.GEAR else int(getattr(obj, "quantity", 1) or 1)
                if q > 1:
                    _qty(r, screen, q, rr)
                if rr.collidepoint(pygame.mouse.get_pos()):
                    self._hover = good

    # ------------------------------------------------------------ friends (world/recruit_mail.py)
    def _friends(self):
        from world import recruit_mail
        from world.bond_manager import get_bond_manager
        from world.recruit_manager import get_recruit_manager
        return recruit_mail.friends(get_bond_manager(), get_recruit_manager(), self.party)

    def _friend(self):
        for b, rec in self._friends():
            if b.rid == self.friend_id:
                return b, rec
        return None, None

    def _towns(self):
        from world import recruit_mail
        from world.bond_manager import get_bond_manager
        return recruit_mail.meeting_towns(get_bond_manager())

    def _friend_row(self, i):
        return pygame.Rect(WIN.x + 16, WIN.y + 64 + i * ROW, 420, ROW - 6)

    def _friends_event(self, event):
        people = self._friends()
        pages = max(1, (len(people) + PER_PAGE - 1) // PER_PAGE)
        if self.prev_btn.clicked(event):
            self.friend_page = max(0, self.friend_page - 1)
            return
        if self.next_btn.clicked(event):
            self.friend_page = min(pages - 1, self.friend_page + 1)
            return
        towns = self._towns()
        if towns and self.town_prev.clicked(event):
            self.town_index = (self.town_index - 1) % len(towns)
            return
        if towns and self.town_next.clicked(event):
            self.town_index = (self.town_index + 1) % len(towns)
            return
        if self.write_btn.clicked(event):
            self._write()
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            shown = people[self.friend_page * PER_PAGE:(self.friend_page + 1) * PER_PAGE]
            for i, (b, _rec) in enumerate(shown):
                if self._friend_row(i).collidepoint(event.pos):
                    self.friend_id = b.rid
                    return
        if event.type == pygame.MOUSEWHEEL:
            self.friend_page = max(0, min(pages - 1, self.friend_page - event.y))

    def _write(self):
        import random
        from world import recruit_mail
        from world.bond_manager import get_bond_manager
        from world.recruit_manager import get_recruit_manager
        b, rec = self._friend()
        towns = self._towns()
        if b is None:
            self._say("Pick somebody to write to.", theme.WARN)
            return
        if not towns:
            self._say("You haven't been to a town with a mailbox yet.", theme.WARN)
            return
        _line, can = recruit_mail.status(get_bond_manager(), get_recruit_manager(), b, rec, self.now,
                                         getattr(self.player, "level", None))
        if not can:
            self._say(_line, theme.WARN)
            return
        cost = Mailbox.postage(0)
        if not self.party.remove_currency(cost):
            self._say("You can't afford the postage.", theme.BAD)
            return
        key, _name = towns[self.town_index % len(towns)]
        ok, msg = recruit_mail.invite(get_bond_manager(), b, key, self.now, random)
        self._say(msg, theme.OK if ok else theme.WARN)

    def _render_friends(self, screen):
        from world import recruit_mail
        from world.bond_manager import STAGE_NAMES, get_bond_manager
        from world.recruit_manager import get_recruit_manager
        r = self.renderer
        bonds, rm = get_bond_manager(), get_recruit_manager()
        people = self._friends()
        pages = max(1, (len(people) + PER_PAGE - 1) // PER_PAGE)
        self.friend_page = min(self.friend_page, pages - 1)
        shown = people[self.friend_page * PER_PAGE:(self.friend_page + 1) * PER_PAGE]
        level = getattr(self.player, "level", None)
        mouse = pygame.mouse.get_pos()
        if not people:
            r.draw_text(screen, "Nobody's gone home yet.", (WIN.x + 226, WIN.y + 180), color=theme.TEXT_DIM, center=True)
            r.draw_text(screen, "Anyone who's been out with you shows up here once they leave.",
                        (WIN.x + 226, WIN.y + 206), size="small", color=theme.TEXT_DIM, center=True)
        for i, (b, rec) in enumerate(shown):
            rr = self._friend_row(i)
            sel = b.rid == self.friend_id
            r.draw_panel(screen, rr, selected=sel, inset=not sel, studs=False)
            if rr.collidepoint(mouse) and not sel:
                pygame.draw.rect(screen, theme.FRAME_SELECTED, rr, 1)
            try:
                from ui.recruit_portrait import get_recruit_portrait
                pic = get_recruit_portrait(rec.recruit_id, 52)
            except Exception:
                pic = None
            if pic is not None:
                screen.blit(pic, (rr.x + 6, rr.y + 6))
            line, _can = recruit_mail.status(bonds, rm, b, rec, self.now, level)
            r.draw_text(screen, r.truncate(rec.name, 200, size="normal"), (rr.x + 66, rr.y + 6), color=theme.TEXT_HEADING)
            stage = STAGE_NAMES.get(b.stage_key, "")
            sw = r._get_font("small").size(stage)[0]
            r.draw_text(screen, stage, (rr.right - 10 - sw, rr.y + 8), size="small", color=theme.TEXT_DIM)
            r.draw_text(screen, r.truncate(f"{rec.char_class}", 300, size="small"), (rr.x + 66, rr.y + 28), size="small",
                        color=theme.TEXT_DIM)
            r.draw_text(screen, r.truncate(line, 340, size="small"), (rr.x + 66, rr.y + 45), size="small",
                        color=theme.TEXT)
        r.draw_text(screen, f"Page {self.friend_page + 1} of {pages}", (WIN.x + 226, WIN.bottom - 44), size="small",
                    color=theme.TEXT_DIM, center=True)
        self.prev_btn.enabled = self.friend_page > 0
        self.next_btn.enabled = self.friend_page < pages - 1
        self.prev_btn.draw(r, screen)
        self.next_btn.draw(r, screen)
        lx = WIN.x + 470
        b, rec = self._friend()
        if b is None:
            r.draw_text(screen, "Pick somebody to write to.", (lx + 220, WIN.y + 160), color=theme.TEXT_DIM, center=True)
            r.draw_text(screen, "The better you know them, the likelier they are to answer, and the sooner.",
                        (lx + 220, WIN.y + 190), size="small", color=theme.TEXT_DIM, center=True)
            return
        r.draw_text(screen, rec.name, (lx, WIN.y + 64), size="large", color=theme.TEXT_HEADING)
        r.draw_text(screen, f"{STAGE_NAMES.get(b.stage_key, '')}, {rec.char_class}", (lx, WIN.y + 100),
                    color=theme.TEXT_DIM)
        line, can = recruit_mail.status(bonds, rm, b, rec, self.now, level)
        y = WIN.y + 132
        for part in r.wrap_text(line, WIN.right - 16 - lx):
            r.draw_text(screen, part, (lx, y))
            y += 20
        odds = recruit_mail.chance(b)
        pace = recruit_mail.reply_hours(b)
        word = ("always writes back" if odds >= 0.999 else "usually writes back" if odds >= 0.7
                else "often writes back" if odds >= 0.45 else "might not write back")
        r.draw_text(screen, f"{rec.name.split()[0]} {word}. An answer takes about {int(pace + 0.5)} hours.",
                    (lx, WIN.y + 196), size="small", color=theme.TEXT_DIM)
        towns = self._towns()
        r.draw_text(screen, "Meet at", (lx, WIN.y + 256), color=theme.TEXT_DIM)
        box = pygame.Rect(lx + 136, WIN.y + 250, WIN.right - 56 - (lx + 136), 30)
        pygame.draw.rect(screen, (16, 15, 20), box)
        pygame.draw.rect(screen, theme.FRAME_INNER, box, 1)
        if towns:
            self.town_index %= len(towns)
            r.draw_text(screen, r.truncate(f"The inn in {towns[self.town_index][1]}", box.width - 16, size="normal"),
                        (box.centerx, box.y + 6), center=True)
        else:
            r.draw_text(screen, "No town with a mailbox yet", (box.centerx, box.y + 6), center=True, color=theme.TEXT_DIM)
        self.town_prev.enabled = self.town_next.enabled = len(towns) > 1
        self.town_prev.draw(r, screen)
        self.town_next.draw(r, screen)
        r.draw_text(screen, "Any town with a mailbox you've been to. They wait at its inn and join when you get there.",
                    (lx, WIN.y + 290), size="small", color=theme.TEXT_DIM)
        r.draw_text(screen, "Postage", (lx, WIN.bottom - 92), color=theme.TEXT_DIM)
        draw_coins(r, screen, Mailbox.postage(0), (lx + 90, WIN.bottom - 90))
        self.write_btn.enabled = bool(can and towns)
        self.write_btn.draw(r, screen)
