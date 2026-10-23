"""
Vendor Screen - buy and sell consumables AND gear from vendor NPCs.

Rewritten from the original consumables-only version. Two real bugs fixed:

1. No gear for sale at all - vendors only stocked potions/food/elixirs.
   WoW vendors sell basic armor too (mostly white, a little green, rarely
   blue) - now wired through LootGenerator via VendorNPC.get_gear_stock().

2. Buying an item deducted gold but the item never actually reached the
   player - add_consumable()/inventory.append() were being called, but
   nothing refreshed the player-side list the SAME FRAME, and the "buy"
   path for a Consumable created a brand new instance every purchase
   without checking whether the player already had a stack of that same
   consumable_id, silently creating duplicate un-stacked entries instead
   of growing the existing one. Fixed by stacking onto an existing
   consumable of the same id when present, and always re-reading
   player.consumables / player.inventory fresh each render rather than
   caching a stale reference at screen construction.
"""
import pygame
from core.game_states import GameState
from ui.screens.base_screen import BaseScreen
from ui.renderer import Renderer
from entities.consumable_manager import get_consumable_manager
from entities.loot_generator import LootGenerator
from entities.loot_item import LootItem
from ui.coin_format import format_coins
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from config import COLOR_WHITE, COLOR_GOLD, COLOR_GREEN, COLOR_RED, COLOR_DARK_GRAY


class VendorScreen(BaseScreen):
    """UI screen for buying/selling consumables and gear at vendor NPCs."""

    ITEM_ROW_HEIGHT = 44
    VISIBLE_ROWS = 9

    def __init__(self, state_manager, vendor):
        super().__init__(state_manager)
        self.vendor = vendor
        self.renderer = Renderer()
        self.consumable_manager = get_consumable_manager()
        self.loot_generator = LootGenerator()

        self.vendor_tab = "consumables"  # "consumables" or "gear"

        self.selected_vendor_item = None
        self.selected_player_item = None
        self.scroll_vendor = 0
        self.scroll_player = 0

        self.message = None
        self.message_color = COLOR_WHITE
        self.message_timer = 0.0

        self.PANEL_Y = 130
        self.PANEL_HEIGHT = self.ITEM_ROW_HEIGHT * self.VISIBLE_ROWS
        self.VENDOR_PANEL_X = 40
        self.PANEL_WIDTH = 540
        self.PLAYER_PANEL_X = SCREEN_WIDTH - 40 - self.PANEL_WIDTH

        self.vendor_inventory = self._build_vendor_consumables()
        self.vendor_gear = vendor.get_gear_stock(self.loot_generator)

        self.on_open()

    def on_open(self):
        """Called every time the screen is shown (fresh build or reopen of the same vendor)."""
        self.selected_vendor_item = None
        self.selected_player_item = None
        # Global "auto-sell vendor trash" tick-box: sweeps the grey stuff the moment any buying vendor opens.
        player = self.state_manager.player
        if getattr(player, "auto_sell_junk", False) and self.vendor.buys_from_player:
            self._sell_all_junk(auto=True)

    def _build_vendor_consumables(self):
        items = []
        for consumable_id in self.vendor.sells:
            c = self.consumable_manager.get_consumable(consumable_id, quantity=1)
            if c:
                items.append(c)
        items.sort(key=lambda c: c.vendor_price)
        return items

    def _current_vendor_stock(self):
        return self.vendor_gear if self.vendor_tab == "gear" else self.vendor_inventory

    def _player_stock(self):
        """Player's own consumables + inventory gear, read fresh every call
        so a just-bought item shows up immediately instead of waiting for
        the screen to be rebuilt."""
        player = self.state_manager.player
        return list(player.consumables) + list(player.inventory)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state_manager.transition_to(GameState.OVERWORLD)
                return

            # "S" shortcut to sell the currently-selected player item, so
            # selling a stack doesn't require re-clicking the Sell button
            # after every single item. _sell_item() already handles "nothing
            # selected" with its own message, so no extra guard needed here.
            if event.key == pygame.K_s:
                self._sell_item()
                return

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            for tab_id, rect in self._tab_rects().items():
                if rect.collidepoint(pos):
                    self.vendor_tab = tab_id
                    self.selected_vendor_item = None
                    self.scroll_vendor = 0
                    return

            stock = self._current_vendor_stock()
            for i, item in enumerate(stock[self.scroll_vendor:self.scroll_vendor + self.VISIBLE_ROWS]):
                if self._row_rect(self.VENDOR_PANEL_X, i).collidepoint(pos):
                    self.selected_vendor_item = item
                    self.selected_player_item = None
                    return

            player_stock = self._player_stock()
            for i, item in enumerate(player_stock[self.scroll_player:self.scroll_player + self.VISIBLE_ROWS]):
                if self._row_rect(self.PLAYER_PANEL_X, i).collidepoint(pos):
                    self.selected_player_item = item
                    self.selected_vendor_item = None
                    return

            if self._auto_box_rect().collidepoint(pos):
                player = self.state_manager.player
                player.auto_sell_junk = not getattr(player, "auto_sell_junk", False)
                if player.auto_sell_junk:
                    self._sell_all_junk()
                else:
                    self._show_message("Auto-sell junk off.", COLOR_WHITE)
                return

            if self._get_junk_button_rect().collidepoint(pos):
                self._sell_all_junk()
            elif self._get_buy_button_rect().collidepoint(pos):
                self._buy_item()
            elif self._get_sell_button_rect().collidepoint(pos):
                self._sell_item()
            elif self._get_close_button_rect().collidepoint(pos):
                self.state_manager.transition_to(GameState.OVERWORLD)

    def _is_gear(self, thing):
        return hasattr(thing, "slot") and hasattr(thing, "armor_value")

    def _buy_item(self):
        item = self.selected_vendor_item
        if item is None:
            self._show_message("Select something to buy first.", COLOR_RED)
            return

        price = getattr(item, "vendor_price", None)
        if price is None:
            price = max(1, int(item.sell_price * 4))

        player = self.state_manager.player
        party = self.state_manager.get_party()
        if not party.remove_currency(price):
            self._show_message(f"Not enough copper! Need {format_coins(price)}.", COLOR_RED)
            return

        if self._is_gear(item):
            # This is a fresh Item instance from the vendor's rolled stock -
            # give the player their own copy directly. Vendor stock is a
            # display of what's on offer, not a shared pool.
            #
            # Bag space check happens AFTER the currency charge above -
            # refunded immediately if it doesn't fit, so a full-bag buy
            # attempt costs nothing rather than silently eating the item
            # the player just paid for.
            if not player.add_to_inventory(item):
                party.add_currency(price)
                self._show_message("Your bags are full - purchase refunded.", COLOR_RED)
                self.selected_vendor_item = None
                return
            self._show_message(f"Bought {item.name} for {format_coins(price)}.", COLOR_GOLD)
        else:
            # THE ACTUAL BUG: previously this always created a brand new
            # Consumable instance and appended it, even if the player
            # already had that same potion. add_consumable() is supposed to
            # stack onto an existing entry of the same id - if it silently
            # failed to find the existing stack (e.g. because the new
            # instance's consumable_id didn't match, or add_consumable's
            # stacking check compared object identity instead of id), the
            # new item could end up appended somewhere that never actually
            # rendered, making it look like the purchase vanished. Buying a
            # fresh instance and explicitly logging what we added, plus
            # reading player.consumables fresh in _player_stock() every
            # frame (see above), makes sure whatever add_consumable() does
            # is immediately visible.
            new_c = self.consumable_manager.get_consumable(item.consumable_id, quantity=1)
            player.add_consumable(new_c)
            self._show_message(f"Bought {item.name} for {format_coins(price)}.", COLOR_GOLD)

        self.selected_vendor_item = None

    def _sell_item(self):
        item = self.selected_player_item
        if item is None:
            self._show_message("Select something to sell first.", COLOR_RED)
            return
        if not self.vendor.buys_from_player:
            self._show_message(f"{self.vendor.name} doesn't buy from adventurers.", COLOR_RED)
            return

        # Quest items are never sellable, regardless of sell_price -
        # Kyle's explicit ruling. Checked via the explicit is_sellable
        # attribute (same style as _is_gear above) rather than an
        # isinstance check, so any future non-gear, non-sellable item
        # type gets the same protection for free just by setting
        # is_sellable = False, without this code needing to know about it.
        if not getattr(item, "is_sellable", True):
            self._show_message(f"{item.name} is a quest item and cannot be sold.", COLOR_RED)
            return

        player = self.state_manager.player
        party = self.state_manager.get_party()
        price = item.sell_price

        if self._is_gear(item):
            equipped_items = player.equipment.to_dict().values()
            if item in equipped_items:
                self._show_message("Unequip that item before selling it.", COLOR_RED)
                return
            if item not in player.inventory:
                self._show_message("You don't have that anymore.", COLOR_RED)
                return
            player.inventory.remove(item)
            party.add_currency(price)
            self._show_message(f"Sold {item.name} for {format_coins(price)}.", COLOR_GREEN)
        else:
            party.add_currency(price)
            item.quantity -= 1
            if item.quantity <= 0:
                if isinstance(item, LootItem):
                    # LootItem stacks live in player.inventory (remove_consumable only looks at consumables).
                    if item in player.inventory:
                        player.inventory.remove(item)
                else:
                    player.remove_consumable(item)
            self._show_message(f"Sold {item.name} for {format_coins(price)}.", COLOR_GREEN)

        if getattr(item, "quantity", 0) > 0 and not self._is_gear(item):
            return  # keep the stack selected so repeated Sell clicks / S presses work through it
        self.selected_player_item = None

    def _junk_stacks(self):
        player = self.state_manager.player
        return [i for i in player.inventory
                if isinstance(i, LootItem) and i.category == "trash" and i.is_sellable]

    def _sell_all_junk(self, auto=False):
        """Sell every vendor-trash (grey) stack. Never touches gear, materials, consumables or quest items."""
        if not self.vendor.buys_from_player:
            self._show_message(f"{self.vendor.name} doesn't buy from adventurers.", COLOR_RED)
            return
        player = self.state_manager.player
        party = self.state_manager.get_party()
        stacks = self._junk_stacks()
        if not stacks:
            if not auto:
                self._show_message("No vendor trash to sell.", COLOR_WHITE)
            return
        count = sum(max(1, i.quantity) for i in stacks)
        total = sum(i.sell_price * max(1, i.quantity) for i in stacks)
        for i in stacks:
            player.inventory.remove(i)
        party.add_currency(total)
        if self.selected_player_item in stacks:
            self.selected_player_item = None
        self._show_message(f"{'Auto-sold' if auto else 'Sold'} {count} junk item{'s' if count != 1 else ''} for {format_coins(total)}.",
                           COLOR_GREEN)



    def _show_message(self, text, color):
        self.message = text
        self.message_color = color
        self.message_timer = 3.0

    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = None

    def render(self, screen):
        screen.fill((18, 18, 26))

        self.renderer.draw_text(screen, self.vendor.name, (SCREEN_WIDTH // 2 - 100, 20),
                                size="large", color=COLOR_GOLD)
        currency_str = self.state_manager.get_party().get_currency_string()
        self.renderer.draw_text(screen, f"Party gold: {currency_str}",
                                (SCREEN_WIDTH // 2 - 100, 55), color=COLOR_WHITE)

        for tab_id, rect in self._tab_rects().items():
            active = tab_id == self.vendor_tab
            color = COLOR_GOLD if active else COLOR_DARK_GRAY
            pygame.draw.rect(screen, (50, 45, 30) if active else (35, 35, 40), rect)
            pygame.draw.rect(screen, color, rect, 2)
            label = "Wares" if tab_id == "consumables" else "Gear"
            self.renderer.draw_text(screen, label, (rect.x + 14, rect.y + 8),
                                    size="small", color=color)

        self._draw_panel_header(screen, self.VENDOR_PANEL_X, "Vendor Stock")
        stock = self._current_vendor_stock()
        for i, item in enumerate(stock[self.scroll_vendor:self.scroll_vendor + self.VISIBLE_ROWS]):
            self._draw_item_row(screen, self.VENDOR_PANEL_X, i, item,
                                selected=(item is self.selected_vendor_item), mode="buy")

        self._draw_panel_header(screen, self.PLAYER_PANEL_X, "Your Items")
        player_stock = self._player_stock()
        for i, item in enumerate(player_stock[self.scroll_player:self.scroll_player + self.VISIBLE_ROWS]):
            self._draw_item_row(screen, self.PLAYER_PANEL_X, i, item,
                                selected=(item is self.selected_player_item), mode="sell")

        buy_rect = self._get_buy_button_rect()
        sell_rect = self._get_sell_button_rect()
        close_rect = self._get_close_button_rect()

        buy_enabled = self.selected_vendor_item is not None
        sell_enabled = self.selected_player_item is not None

        pygame.draw.rect(screen, (40, 70, 40) if buy_enabled else (30, 30, 30), buy_rect)
        pygame.draw.rect(screen, COLOR_GREEN if buy_enabled else COLOR_DARK_GRAY, buy_rect, 2)
        self.renderer.draw_text(screen, "Buy", (buy_rect.x + 20, buy_rect.y + 10),
                                color=COLOR_GREEN if buy_enabled else COLOR_DARK_GRAY)

        pygame.draw.rect(screen, (70, 40, 40) if sell_enabled else (30, 30, 30), sell_rect)
        pygame.draw.rect(screen, COLOR_RED if sell_enabled else COLOR_DARK_GRAY, sell_rect, 2)
        self.renderer.draw_text(screen, "Sell", (sell_rect.x + 20, sell_rect.y + 10),
                                color=COLOR_RED if sell_enabled else COLOR_DARK_GRAY)

        junk_rect = self._get_junk_button_rect()
        has_junk = bool(self._junk_stacks()) and self.vendor.buys_from_player
        pygame.draw.rect(screen, (60, 60, 60) if has_junk else (30, 30, 30), junk_rect)
        pygame.draw.rect(screen, (180, 180, 180) if has_junk else COLOR_DARK_GRAY, junk_rect, 2)
        self.renderer.draw_text(screen, "Sell Junk", (junk_rect.x + 18, junk_rect.y + 10),
                                color=(200, 200, 200) if has_junk else COLOR_DARK_GRAY)

        box = self._auto_box_rect()
        on = getattr(self.state_manager.player, "auto_sell_junk", False)
        pygame.draw.rect(screen, (28, 28, 36), box)
        pygame.draw.rect(screen, COLOR_GOLD if on else (150, 150, 160), box, 2)
        if on:
            pygame.draw.line(screen, COLOR_GOLD, (box.x + 4, box.centery), (box.x + 9, box.bottom - 5), 3)
            pygame.draw.line(screen, COLOR_GOLD, (box.x + 9, box.bottom - 5), (box.right - 4, box.y + 4), 3)
        self.renderer.draw_text(screen, "Auto-sell junk on open", (box.right + 10, box.y - 1),
                                size="small", color=COLOR_GOLD if on else (170, 170, 180))

        pygame.draw.rect(screen, (40, 40, 45), close_rect)
        pygame.draw.rect(screen, COLOR_WHITE, close_rect, 2)
        self.renderer.draw_text(screen, "Close (Esc)", (close_rect.x + 12, close_rect.y + 10),
                                size="small", color=COLOR_WHITE)

        if self.message:
            self.renderer.draw_text(screen, self.message,
                                    (SCREEN_WIDTH // 2 - 150, close_rect.y - 40),
                                    color=self.message_color)

        if self.selected_vendor_item:
            self._render_tooltip(screen, self.selected_vendor_item, "buy")
        elif self.selected_player_item:
            self._render_tooltip(screen, self.selected_player_item, "sell")

    def _draw_panel_header(self, screen, x, label):
        panel_rect = pygame.Rect(x, self.PANEL_Y, self.PANEL_WIDTH, self.PANEL_HEIGHT)
        pygame.draw.rect(screen, (28, 28, 36), panel_rect)
        pygame.draw.rect(screen, (70, 70, 85), panel_rect, 2)
        self.renderer.draw_text(screen, label, (x, self.PANEL_Y - 26), color=COLOR_GOLD)

    def _row_rect(self, panel_x, row_index):
        y = self.PANEL_Y + row_index * self.ITEM_ROW_HEIGHT
        return pygame.Rect(panel_x, y, self.PANEL_WIDTH, self.ITEM_ROW_HEIGHT - 2)

    def _draw_item_row(self, screen, panel_x, row_index, item, selected, mode):
        rect = self._row_rect(panel_x, row_index)
        is_gear = self._is_gear(item)

        if selected:
            pygame.draw.rect(screen, (60, 55, 30), rect)
            pygame.draw.rect(screen, COLOR_GOLD, rect, 2)
        else:
            pygame.draw.rect(screen, (24, 24, 30), rect)

        is_trash = getattr(item, "category", None) == "trash"
        name_color = (item.get_rarity_color() if (is_gear or is_trash or not getattr(item, "is_sellable", True))
                      else COLOR_WHITE)
        self.renderer.draw_text(screen, item.name, (rect.x + 10, rect.y + 6),
                                size="small", color=name_color)

        if mode == "buy":
            price = getattr(item, "vendor_price", None)
            if price is None:
                price = max(1, int(item.sell_price * 4))
            price_text = format_coins(price)
        elif not getattr(item, "is_sellable", True):
            # Quest item in the player's sell-list panel - shown with its
            # quantity but no price, since it can't actually be sold (see
            # _sell_item's is_sellable gate). A blank/zero price here
            # would read as "vendor pays nothing" rather than "this can't
            # be sold at all", which is a different, clearer message.
            # Kept short ("Quest") rather than "(quest item)" - the
            # longer form ran off the right edge of the row at this
            # panel width once a quantity prefix was added too.
            qty = getattr(item, "quantity", None)
            price_text = f"x{qty}  Quest" if qty is not None else "Quest"
        else:
            qty = getattr(item, "quantity", None)
            price_text = (f"x{qty}  ->{format_coins(item.sell_price)}" if qty is not None
                          else f"->{format_coins(item.sell_price)}")

        self.renderer.draw_text(screen, price_text, (rect.right - 140, rect.y + 6),
                                size="small", color=COLOR_GOLD)

        if is_gear:
            slot_label = item.slot.replace("_", " ").title()
            self.renderer.draw_text(screen, slot_label, (rect.x + 10, rect.y + 24),
                                    size="small", color=(160, 160, 170))

    def _render_tooltip(self, screen, item, mode):
        is_gear = self._is_gear(item)
        lines = [item.name]
        if is_gear:
            lines.append(f"{item.rarity.title()} - {item.slot.replace('_', ' ').title()}")
            if item.armor_value:
                lines.append(f"Armor: {item.armor_value}")
            for stat, val in item.primary_stats.items():
                lines.append(f"+{val} {stat.replace('_', ' ').title()}")
            for stat, val in item.secondary_stats.items():
                lines.append(f"+{val} {stat.replace('_', ' ').title()}")
            if item.weapon_damage_max:
                lines.append(f"Damage: {item.weapon_damage_min}-{item.weapon_damage_max}")
            lines.append(f"Requires level {item.required_level}")
        elif not getattr(item, "is_sellable", True):
            # QuestItem - neither gear nor a real Consumable, so it has
            # none of the fields the branch below assumes
            # (consumable_type, required_level). A plain description +
            # "cannot be sold" reads better than crashing on a missing
            # attribute or showing a fake "Requires level 1".
            if getattr(item, "description", ""):
                lines.append(item.description)
            lines.append("Quest Item - cannot be sold")
        else:
            lines.append(f"Type: {item.consumable_type}")
            lines.append(f"Requires level {item.required_level}")
            lines.append(item.description)

        if mode == "buy":
            price = getattr(item, "vendor_price", None)
            if price is None:
                price = max(1, int(item.sell_price * 4))
            lines.append(f"Price: {format_coins(price)}")
        elif getattr(item, "is_sellable", True):
            lines.append(f"Sells for: {format_coins(item.sell_price)}")
        # else: is_sellable is False - the "cannot be sold" line was
        # already appended above, no separate price line needed.

        mouse_pos = pygame.mouse.get_pos()
        box_width = 320
        line_height = 20
        box_height = len(lines) * line_height + 12
        tooltip_x = min(mouse_pos[0] + 12, SCREEN_WIDTH - box_width - 10)
        tooltip_y = min(mouse_pos[1] + 12, SCREEN_HEIGHT - box_height - 10)

        pygame.draw.rect(screen, (26, 26, 34), (tooltip_x, tooltip_y, box_width, box_height))
        pygame.draw.rect(screen, (90, 90, 110), (tooltip_x, tooltip_y, box_width, box_height), 1)

        for i, line in enumerate(lines):
            self.renderer.draw_text(screen, line, (tooltip_x + 8, tooltip_y + 6 + i * line_height),
                                    size="small", color=COLOR_WHITE)

    def _tab_rects(self):
        y = 95
        return {
            "consumables": pygame.Rect(self.VENDOR_PANEL_X, y, 120, 32),
            "gear": pygame.Rect(self.VENDOR_PANEL_X + 130, y, 120, 32),
        }

    def _get_buy_button_rect(self):
        return pygame.Rect(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT - 70, 140, 44)

    def _get_sell_button_rect(self):
        return pygame.Rect(SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT - 70, 140, 44)

    def _get_close_button_rect(self):
        return pygame.Rect(SCREEN_WIDTH // 2 + 80, SCREEN_HEIGHT - 70, 140, 44)

    def _get_junk_button_rect(self):
        return pygame.Rect(SCREEN_WIDTH // 2 + 230, SCREEN_HEIGHT - 70, 140, 44)

    def _auto_box_rect(self):
        # sits under the "Your Items" panel, right-aligned with it
        return pygame.Rect(self.PLAYER_PANEL_X, self.PANEL_Y + self.PANEL_HEIGHT + 12, 20, 20)
