"""Sockets: put cut gems into gear, or have a jeweller take them out.

world/jewelcrafting.py has the rules. This screen has two modes:

  socket   opened from the inventory ("Sockets" button). Pick a piece of gear with sockets, pick
           a cut gem from your bags, click a socket. A socket that already holds a gem asks once
           before the old gem is destroyed (Kyle's call, 14 Nov: gems are permanent unless a
           jeweller takes them out).
  remove   opened from a jeweller (a forge trainer who teaches jewelcrafting, "Remove Gems").
           Click a socket with a gem in it; the jeweller hands it back for a fee.

Gear is listed from the player's bags and from everything anyone in the party is wearing, so a
companion's helm can be gemmed without taking it off.
"""
import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_GOLD
from core.game_states import GameState
from ui.screens.base_screen import BaseScreen

LIST_X, LIST_Y, LIST_W, ROW_H = 20, 90, 430, 40
PANEL_X = LIST_X + LIST_W + 30


class SocketScreen(BaseScreen):
    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.mode = "socket"
        self.return_state = GameState.INVENTORY
        self.close_button = pygame.Rect(SCREEN_WIDTH - 120, 20, 100, 50)
        self.selected_item = None
        self.selected_gem = None
        self.armed_socket = None        # a filled socket clicked once: the next click replaces it
        self.message = ""
        self.message_ok = True
        self.item_rects, self.socket_rects, self.gem_rects = [], [], []
        self.scroll = 0

    def open(self, mode="socket", return_state=None):
        self.mode = mode
        self.return_state = return_state or (GameState.INVENTORY if mode == "socket" else GameState.OVERWORLD)
        self.selected_item = self.selected_gem = self.armed_socket = None
        self.message = ""
        self.scroll = 0

    # ------------------------------------------------------------ data
    def _gear(self):
        """[(owner, item, where)] for every socketed item in reach."""
        from world.jewelcrafting import sockets
        sm = self.state_manager
        player = sm.player
        out = []
        for it in getattr(player, "inventory", []):
            if getattr(it, "is_gear", True) and getattr(it, "sockets", None) and sockets(it):
                out.append((player, it, "in your bags"))
        party = sm.get_party()
        members = list(getattr(party, "members", []) or [player]) + list(getattr(party, "bench", []) or [])
        for m in members:
            for it in m.equipment.get_all_equipped():
                if getattr(it, "sockets", None) and sockets(it):
                    out.append((m, it, f"worn by {m.name}" if m is not player else "worn"))
        return out

    def _gems(self):
        from world.jewelcrafting import cut
        p = self.state_manager.player
        seen = {}
        for m in p.materials:
            g = cut(m.material_id)
            if g:
                seen[m.material_id] = seen.get(m.material_id, 0) + m.quantity
        return sorted(((cid, n, cut(cid)) for cid, n in seen.items()), key=lambda t: (t[2]["color"], t[2]["name"]))

    def _owner_of(self, item):
        for owner, it, _w in self._gear():
            if it is item:
                return owner
        return self.state_manager.player

    # ------------------------------------------------------------ input
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state_manager.transition_to(self.return_state)
            return
        if event.type == pygame.MOUSEWHEEL:
            self.scroll = max(0, self.scroll - event.y)
            return
        if event.type != pygame.MOUSEBUTTONDOWN or getattr(event, "button", 1) != 1:
            return
        pos = event.pos
        if self.close_button.collidepoint(pos):
            self.state_manager.transition_to(self.return_state)
            return
        for item, rect in self.item_rects:
            if rect.collidepoint(pos):
                self.selected_item = item
                self.armed_socket = None
                self.message = ""
                return
        for cid, rect in self.gem_rects:
            if rect.collidepoint(pos):
                self.selected_gem = cid
                self.armed_socket = None
                return
        for index, rect in self.socket_rects:
            if rect.collidepoint(pos):
                self._socket_clicked(index)
                return

    def _socket_clicked(self, index):
        from world import jewelcrafting as J
        item = self.selected_item
        if item is None:
            return
        s = J.sockets(item)[index]
        if self.mode == "remove":
            ok, msg = J.remove(self.state_manager.player, item, index, party=self.state_manager.get_party())
            if ok:
                J._refresh(self._owner_of(item))
            self._say(ok, msg)
            return
        if not self.selected_gem:
            self._say(False, "Pick a gem from your bags first.")
            return
        if s.get("gem") and self.armed_socket != index:
            self.armed_socket = index
            g = J.cut(s["gem"])
            self._say(False, f"That socket holds a {g['name'] if g else 'gem'}. Click again to "
                             f"replace it and destroy it, or take it to a jeweller first.")
            return
        self.armed_socket = None
        ok, msg = J.place(self.state_manager.player, item, index, self.selected_gem)
        if ok:
            J._refresh(self._owner_of(item))
            if self.state_manager.player.get_material_quantity(self.selected_gem) < 1:
                self.selected_gem = None
        self._say(ok, msg)

    def _say(self, ok, msg):
        self.message, self.message_ok = msg, ok

    # ------------------------------------------------------------ drawing
    def render(self, screen):
        from world import jewelcrafting as J
        screen.fill((12, 12, 18))
        title = "SOCKET GEMS" if self.mode == "socket" else "REMOVE GEMS"
        self.renderer.draw_text(screen, title, (20, 20), size="large", color=COLOR_GOLD)
        hint = ("Pick an item, pick a gem, then click a socket." if self.mode == "socket" else
                "Pick an item, then click a gem to have it taken out. The jeweller charges for each one.")
        self.renderer.draw_text(screen, hint, (20, 58), color=(170, 170, 180))
        self.renderer.draw_button(screen, self.close_button, "Close")

        gear = self._gear()
        self.item_rects = []
        y = LIST_Y
        if not gear:
            self.renderer.draw_text(screen, "Nothing in reach has a socket. Gear from level 30 up can have them.",
                                    (LIST_X, y), color=(200, 160, 120))
        for owner, it, where in gear[self.scroll:self.scroll + 16]:
            rect = pygame.Rect(LIST_X, y, LIST_W, ROW_H - 4)
            chosen = it is self.selected_item
            self.renderer.draw_rect(screen, rect, (40, 40, 52) if chosen else (26, 26, 32))
            self.renderer.draw_rect(screen, rect, it.get_rarity_color() if chosen else (70, 70, 80), fill=False)
            filled = sum(1 for s in J.sockets(it) if s.get("gem"))
            self.renderer.draw_text(screen, it.name, (rect.x + 8, rect.y + 3), color=it.get_rarity_color())
            self.renderer.draw_text(screen, f"{where}, {filled} of {len(J.sockets(it))} sockets filled",
                                    (rect.x + 8, rect.y + 20), font_size=13, color=(160, 160, 170))
            self.item_rects.append((it, rect))
            y += ROW_H

        self.socket_rects = []
        item = self.selected_item
        py = LIST_Y
        if item is not None:
            self.renderer.draw_text(screen, item.name, (PANEL_X, py), color=item.get_rarity_color())
            py += 30
            for i, s in enumerate(J.sockets(item)):
                rect = pygame.Rect(PANEL_X, py, 520, 40)
                colour = J.SOCKET_COLOURS.get(s["color"], (150, 150, 150))
                armed = self.armed_socket == i
                self.renderer.draw_rect(screen, rect, (34, 30, 30) if armed else (26, 26, 32))
                self.renderer.draw_rect(screen, rect, colour, fill=False)
                pygame.draw.circle(screen, colour, (rect.x + 20, rect.centery), 11)
                name, stats, fits = J.describe_socket(s)
                if stats:
                    label = f"{name}: {stats}" + ("" if fits else "  (doesn't match)")
                    if self.mode == "remove":
                        from ui.coin_format import format_coins
                        g = J.cut(s["gem"]) or {}
                        label += f"   take out for {format_coins(max(1, g.get('level', 1)) * J.REMOVAL_FEE_PER_LEVEL)}"
                else:
                    label = f"Empty {s['color']} socket"
                self.renderer.draw_text(screen, label, (rect.x + 42, rect.y + 11),
                                        color=COLOR_WHITE if stats else (160, 160, 170))
                self.socket_rects.append((i, rect))
                py += 46
            bonus = getattr(item, "socket_bonus", None) or {}
            if bonus:
                text = ", ".join(f"+{v} {k.replace('_', ' ').title()}" for k, v in bonus.items())
                on = J.bonus_active(item)
                self.renderer.draw_text(screen, f"Socket Bonus: {text}" + ("" if on else "  (fill every socket with a matching gem)"),
                                        (PANEL_X, py + 4), color=(30, 255, 0) if on else (130, 130, 130))
                py += 34

        self.gem_rects = []
        if self.mode == "socket":
            gy = max(py + 20, LIST_Y + 260)
            self.renderer.draw_text(screen, "Your gems", (PANEL_X, gy), color=COLOR_GOLD)
            gy += 26
            gems = self._gems()
            if not gems:
                self.renderer.draw_text(screen, "You don't have any cut gems. A jewelcrafter cuts them from raw stones.",
                                        (PANEL_X, gy), color=(160, 160, 170))
            for cid, n, g in gems[:12]:
                rect = pygame.Rect(PANEL_X, gy, 520, 30)
                chosen = cid == self.selected_gem
                colour = J.SOCKET_COLOURS.get(g["color"], (200, 200, 200))
                self.renderer.draw_rect(screen, rect, (40, 40, 52) if chosen else (24, 24, 30))
                self.renderer.draw_rect(screen, rect, colour if chosen else (60, 60, 70), fill=False)
                fits = "any" if g["color"] == "prismatic" else " or ".join(sorted(J.FITS[g["color"]]))
                stats = ", ".join(f"+{v} {k.replace('_', ' ')}" for k, v in g["stats"].items())
                self.renderer.draw_text(screen, f"{g['name']} x{n}   {stats}   fits {fits}",
                                        (rect.x + 10, rect.y + 7), color=COLOR_WHITE)
                self.gem_rects.append((cid, rect))
                gy += 34

        if self.message:
            self.renderer.draw_text(screen, self.message, (20, SCREEN_HEIGHT - 40),
                                    color=(140, 220, 160) if self.message_ok else (240, 180, 120))
