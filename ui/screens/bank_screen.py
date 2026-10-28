"""
Bank Screen - MerchantTusk's vault.

Two grids facing each other: the bank's current tab on the left, the player's backpack on the right.
Click a slot on either side to move that item to the other. That is the whole interaction, and it is
deliberately the whole interaction - a bank is a place you dump things quickly on the way past, and any
design that needs a confirm dialog per item is a design you stop using by level 30.

TAB STRIP along the top: owned tabs are buttons, the next unowned one is a price. Beyond that, nothing -
a row of six greyed-out padlocks tells the player nothing except that they are poor.

WHY THE GRID IS 8x6. SLOTS_PER_TAB is 48 and is owned by entities/bank.py, not by this file; the columns
here are chosen so 48 divides evenly and the two grids plus the strip between them fit 1280x720 with the
tab row above. If SLOTS_PER_TAB ever changes, _build_rects derives the row count from it rather than
assuming - a UI that believes in a different grid size than its storage is how slots go missing.
"""
import pygame

from config import (SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_GOLD, COLOR_GREEN,
                    COLOR_RED, COLOR_DARK_GRAY)
from core.game_states import GameState
from entities.bank import SLOTS_PER_TAB, TAB_NAMES, MAX_TABS, gold_str
from ui.renderer import Renderer
from ui.screens.base_screen import BaseScreen

GRID_COLS = 8
CELL = 56
GAP = 5
BANK_X, BANK_Y = 40, 190
PLAYER_X, PLAYER_Y = 760, 190
TAB_Y = 120
TAB_W, TAB_H = 128, 34


class BankScreen(BaseScreen):
    """The bank's current tab beside the player's backpack. Click to move."""

    def __init__(self, state_manager, banker=None, icon_ui_helper=None):
        super().__init__(state_manager)
        self.banker = banker
        self.renderer = Renderer()
        self.icon_ui_helper = icon_ui_helper or getattr(state_manager, "icon_ui_helper", None)
        self.active_tab = 0
        self.message = ""
        self.hover = None          # ("bank"|"player", index) for the tooltip
        self._build_rects()

    # ------------------------------------------------------------------ data
    def _bank(self):
        party = self.state_manager.get_party() if hasattr(self.state_manager, "get_party") \
            else getattr(self.state_manager, "party", None)
        return (getattr(party, "bank", None), party)

    def _build_rects(self):
        rows = (SLOTS_PER_TAB + GRID_COLS - 1) // GRID_COLS
        self.bank_rects, self.player_rects = [], []
        for i in range(SLOTS_PER_TAB):
            c, r = i % GRID_COLS, i // GRID_COLS
            self.bank_rects.append(pygame.Rect(BANK_X + c * (CELL + GAP),
                                               BANK_Y + r * (CELL + GAP), CELL, CELL))
        # The backpack side is sized to the player's real capacity, not to SLOTS_PER_TAB - drawing 48
        # backpack cells when the player has 16 would invite clicks on slots that cannot exist.
        for i in range(SLOTS_PER_TAB):
            c, r = i % GRID_COLS, i // GRID_COLS
            self.player_rects.append(pygame.Rect(PLAYER_X + c * (CELL + GAP),
                                                 PLAYER_Y + r * (CELL + GAP), CELL, CELL))
        self.tab_rects = [pygame.Rect(40 + i * (TAB_W + 6), TAB_Y, TAB_W, TAB_H)
                          for i in range(MAX_TABS)]
        self.close_rect = pygame.Rect(SCREEN_WIDTH - 150, 20, 120, 40)
        self.deposit_all_rect = pygame.Rect(PLAYER_X, PLAYER_Y - 44, 190, 34)

    # ------------------------------------------------------------------ input
    def handle_event(self, event):
        bank, party = self._bank()
        player = self.state_manager.player
        if bank is None or player is None:
            return

        if event.type == pygame.MOUSEMOTION:
            self.hover = None
            for i, r in enumerate(self.bank_rects):
                if r.collidepoint(event.pos) and bank.get(self.active_tab, i):
                    self.hover = ("bank", i)
            for i, r in enumerate(self.player_rects):
                if r.collidepoint(event.pos) and i < len(player.inventory):
                    self.hover = ("player", i)
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state_manager.transition_to(GameState.OVERWORLD)
            return

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        pos = event.pos

        if self.close_rect.collidepoint(pos):
            self.state_manager.transition_to(GameState.OVERWORLD)
            return

        # --- tabs: owned ones switch, the next one is for sale
        for i, r in enumerate(self.tab_rects):
            if not r.collidepoint(pos):
                continue
            if i < bank.tabs_owned:
                self.active_tab = i
                self.message = ""
            elif i == bank.tabs_owned:
                ok, msg = bank.buy_tab(party)
                self.message = msg
                if ok:
                    self.active_tab = i
            return

        # --- deposit everything that fits, which is what the button is for
        if self.deposit_all_rect.collidepoint(pos):
            moved = 0
            for item in list(player.inventory):
                if bank.deposit(item) is None:
                    break
                player.inventory.remove(item)
                moved += 1
            self.message = (f"Stored {moved} item{'s' if moved != 1 else ''}."
                            if moved else "Nothing fit - the vault is full.")
            return

        # --- bank slot -> backpack
        for i, r in enumerate(self.bank_rects):
            if not r.collidepoint(pos):
                continue
            item = bank.get(self.active_tab, i)
            if item is None:
                return
            if len(player.inventory) >= getattr(player, "inventory_capacity", 16):
                self.message = "Your bags are full."
                return
            player.inventory.append(bank.withdraw(self.active_tab, i))
            self.message = f"Took {getattr(item, 'name', 'it')}."
            return

        # --- backpack -> bank. Prefer the tab being looked at, then anywhere.
        for i, r in enumerate(self.player_rects):
            if not r.collidepoint(pos) or i >= len(player.inventory):
                continue
            item = player.inventory[i]
            spot = bank.deposit(item, self.active_tab)
            if spot is None:
                spot = bank.deposit(item)
            if spot is None:
                self.message = "The vault is full. Buy another tab."
                return
            player.inventory.remove(item)
            self.message = f"Stored {getattr(item, 'name', 'it')}."
            return

    # ------------------------------------------------------------------ draw
    def _icon(self, screen, item, rect):
        if not self.icon_ui_helper or not getattr(item, "icon_id", None):
            return False
        size = min(rect.width, rect.height) - 6
        try:
            surf = self.icon_ui_helper.get_item_icon_surface(
                {"name": item.name, "icon_id": item.icon_id,
                 "rarity": getattr(item, "rarity", "common")}, size=size)
            if surf:
                screen.blit(surf, (rect.x + (rect.width - size) // 2,
                                   rect.y + (rect.height - size) // 2))
                return True
        except Exception:
            pass
        return False

    def _cell(self, screen, rect, item):
        pygame.draw.rect(screen, (28, 28, 34), rect)
        pygame.draw.rect(screen, (70, 70, 82), rect, 1)
        if item is None:
            return
        colour = item.get_rarity_color() if hasattr(item, "get_rarity_color") else COLOR_WHITE
        pygame.draw.rect(screen, colour, rect, 2)
        if not self._icon(screen, item, rect):
            # No art for this item - the first letters of its name beat an empty box.
            self.renderer.draw_text(screen, getattr(item, "name", "?")[:6],
                                    (rect.x + 4, rect.centery - 8), color=colour, size="small")

    def render(self, screen):
        screen.fill((16, 16, 20))
        bank, party = self._bank()
        player = self.state_manager.player
        if bank is None or player is None:
            self.renderer.draw_text(screen, "No vault here.", (40, 40), color=COLOR_RED)
            return

        name = getattr(self.banker, "name", None) or "MerchantTusk"
        self.renderer.draw_text(screen, name, (40, 22), color=COLOR_GOLD, size="large")
        greet = getattr(self.banker, "greeting", "")
        if greet:
            self.renderer.draw_text(screen, f'"{greet}"', (40, 62), color=(170, 170, 180),
                                    size="small")
        purse = party.get_currency_string() if party and hasattr(party, "get_currency_string") else ""
        self.renderer.draw_text(screen, f"Party gold: {purse}", (SCREEN_WIDTH - 420, 62),
                                color=COLOR_GOLD)

        # --- tab strip
        for i, r in enumerate(self.tab_rects):
            if i < bank.tabs_owned:
                col = (70, 110, 70) if i == self.active_tab else COLOR_DARK_GRAY
                self.renderer.draw_button(screen, r, TAB_NAMES[i], color=col)
            elif i == bank.tabs_owned:
                price = bank.next_tab_price()
                self.renderer.draw_button(screen, r, f"Buy {gold_str(price)}", color=(110, 90, 40))
            else:
                # Locked tabs beyond the next one are drawn flat and unlabelled on purpose: a row of
                # padlocks with prices on them is a shop window, and this is a vault.
                pygame.draw.rect(screen, (26, 26, 30), r)
                pygame.draw.rect(screen, (46, 46, 52), r, 1)

        # --- the two grids
        used = sum(1 for s in bank.tabs[self.active_tab] if s is not None)
        self.renderer.draw_text(screen, f"{TAB_NAMES[self.active_tab]}  {used}/{SLOTS_PER_TAB}",
                                (BANK_X, BANK_Y - 30), color=COLOR_GOLD)
        for i, r in enumerate(self.bank_rects):
            self._cell(screen, r, bank.get(self.active_tab, i))

        cap = getattr(player, "inventory_capacity", 16)
        self.renderer.draw_text(screen, f"Backpack  {len(player.inventory)}/{cap}",
                                (PLAYER_X, PLAYER_Y - 76), color=COLOR_GOLD)
        self.renderer.draw_button(screen, self.deposit_all_rect, "Deposit everything",
                                  color=COLOR_DARK_GRAY)
        for i, r in enumerate(self.player_rects):
            if i >= cap:
                break
            self._cell(screen, r, player.inventory[i] if i < len(player.inventory) else None)

        self.renderer.draw_button(screen, self.close_rect, "Close (Esc)", color=COLOR_DARK_GRAY)
        if self.message:
            self.renderer.draw_text(screen, self.message, (40, SCREEN_HEIGHT - 40),
                                    color=COLOR_GREEN)

        self._tooltip(screen, bank, player)

    def _tooltip(self, screen, bank, player):
        if not self.hover:
            return
        side, i = self.hover
        item = bank.get(self.active_tab, i) if side == "bank" else (
            player.inventory[i] if i < len(player.inventory) else None)
        if item is None:
            return
        rect = (self.bank_rects if side == "bank" else self.player_rects)[i]
        lines = [getattr(item, "name", "?")]
        if getattr(item, "item_level", None):
            lines.append(f"Item level {item.item_level}")
        if getattr(item, "required_level", None):
            lines.append(f"Requires level {item.required_level}")
        w = max(160, 9 * max(len(x) for x in lines))
        box = pygame.Rect(min(rect.right + 8, SCREEN_WIDTH - w - 8), rect.y, w, 20 * len(lines) + 12)
        pygame.draw.rect(screen, (20, 20, 26), box)
        colour = item.get_rarity_color() if hasattr(item, "get_rarity_color") else COLOR_WHITE
        pygame.draw.rect(screen, colour, box, 2)
        for n, line in enumerate(lines):
            self.renderer.draw_text(screen, line, (box.x + 8, box.y + 6 + n * 20),
                                    color=colour if n == 0 else COLOR_WHITE, size="small")

    def update(self, dt):
        pass
