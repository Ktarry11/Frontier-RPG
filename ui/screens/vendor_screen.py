"""
Vendor Screen - buy and sell items from vendor NPCs.

Overhauled from the tabs-based version:

1. No more "consumables" / "gear" tabs.  Each vendor shows a single unified
   item list that reflects their role — an alchemist's supplier sells vials
   and parchment, a blacksmith's supplier sells flux and coal, an innkeeper
   sells food and drink.  The tab machinery is gone; only one list renders.

2. Vendors now sell Materials (crafting reagents: thread, vials, flux, …) as
   first-class buyable items alongside consumables and gear.  The buy path
   dispatches on the item type:
     • gear      → player.add_to_inventory()
     • consumable → player.add_consumable()   (stacks onto existing)
     • material   → player.add_material()     (stacks onto existing)

3. The sell-side ("Your Items") panel now includes player.materials so reagents
   the player picked up or bought can be sold back.

4. Tooltip for materials shows description + price; no level requirement
   since reagents aren't level-gated.
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
    """UI screen for buying/selling consumables, gear, and crafting reagents."""

    ITEM_ROW_HEIGHT = 44
    VISIBLE_ROWS = 9

    def __init__(self, state_manager, vendor):
        super().__init__(state_manager)
        self.vendor = vendor
        self.renderer = Renderer()
        self.consumable_manager = get_consumable_manager()
        self.loot_generator = LootGenerator()

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

        # Unified vendor stock: consumables + materials from vendor.sells,
        # plus gear from vendor.get_gear_stock() when sells_gear is True.
        self.vendor_inventory = self._build_vendor_stock()

        self.on_open()

    def on_open(self):
        """Called every time the screen is shown."""
        self.selected_vendor_item = None
        self.selected_player_item = None
        player = self.state_manager.player
        if getattr(player, "auto_sell_junk", False) and self.vendor.buys_from_player:
            self._sell_all_junk(auto=True)

    # ------------------------------------------------------------------ build

    def _build_vendor_stock(self):
        """Resolve all items this vendor sells into a unified list.

        Ordering: consumables and materials (sorted by vendor_price) first,
        then gear (sorted by required_level so lower-level stuff is at top).
        This matches the WoW vendor convention where gear is after supplies.
        """
        from world.gathering_manager import GatheringNodeManager
        gathering_mgr = GatheringNodeManager()

        items = []
        for item_id in self.vendor.sells:
            # Membership test BEFORE get_consumable, not a get-and-check:
            # get_consumable logs a WARNING for an unknown id, and an id that
            # is a crafting reagent rather than a consumable is the normal
            # case here, not an error. Probing with get_consumable printed
            # one false warning per reagent (~190 per vendor open).
            if self.consumable_manager.has_consumable(item_id):
                items.append(self.consumable_manager.get_consumable(item_id, quantity=1))
                continue
            # Crafting reagent or gathered material
            mat = gathering_mgr.make_material_instance(item_id)
            if mat:
                items.append(mat)
                continue
            # RECIPE SCROLLS. A vendor's sells list may name a recipe id directly, and 57 recipes
            # carry source "vendor" expecting exactly that. Until now this resolver only knew about
            # consumables and materials, so every one of those ids fell through to the warning below
            # and was silently dropped from the stock list - which is why none of them were buyable.
            # The buy path needs nothing extra: a scroll Item has both slot and armor_value, so
            # _is_gear already routes it to add_to_inventory.
            from world.recipe_manager import make_recipe_scroll
            scroll = make_recipe_scroll(item_id)
            if scroll is not None:
                items.append(scroll)
                continue
            # Genuinely unknown ID — warn and skip rather than crash
            print(f"[VendorScreen] WARNING: unknown sell ID '{item_id}' on vendor '{self.vendor.vendor_id}'")

        items.sort(key=lambda x: getattr(x, "vendor_price", 0))

        # Gear appended after supplies when the vendor has a gear stock
        if getattr(self.vendor, "sells_gear", False):
            gear = self.vendor.get_gear_stock(self.loot_generator)
            gear.sort(key=lambda g: getattr(g, "required_level", 0))
            items.extend(gear)

        return items

    # ------------------------------------------------------------------ queries

    def _is_gear(self, thing):
        return hasattr(thing, "slot") and hasattr(thing, "armor_value")

    def _is_material(self, thing):
        from entities.material import Material
        return isinstance(thing, Material)

    def _player_stock(self):
        """Player's consumables + materials + inventory gear, read fresh every
        call so newly bought items appear immediately."""
        player = self.state_manager.player
        return list(player.consumables) + list(getattr(player, "materials", [])) + list(player.inventory)

    # ------------------------------------------------------------------ actions

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
            if not player.add_to_inventory(item):
                party.add_currency(price)
                self._show_message("Your bags are full - purchase refunded.", COLOR_RED)
                self.selected_vendor_item = None
                return
            self._show_message(f"Bought {item.name} for {format_coins(price)}.", COLOR_GOLD)

        elif self._is_material(item):
            # Create a fresh instance from the gathering manager so we don't
            # mutate the vendor's display copy.
            from world.gathering_manager import GatheringNodeManager
            mat = GatheringNodeManager().make_material_instance(item.material_id)
            if mat is None:
                party.add_currency(price)
                self._show_message("Couldn't resolve that item — refunded.", COLOR_RED)
                self.selected_vendor_item = None
                return
            player.add_material(mat)
            self._show_message(f"Bought {item.name} for {format_coins(price)}.", COLOR_GOLD)

        else:
            # Consumable — stack onto existing entry with the same id
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

        elif self._is_material(item):
            party.add_currency(price)
            item.quantity -= 1
            if item.quantity <= 0:
                mats = getattr(player, "materials", [])
                if item in mats:
                    mats.remove(item)
            self._show_message(f"Sold {item.name} for {format_coins(price)}.", COLOR_GREEN)

        else:
            # Consumable
            party.add_currency(price)
            item.quantity -= 1
            if item.quantity <= 0:
                if isinstance(item, LootItem):
                    if item in player.inventory:
                        player.inventory.remove(item)
                else:
                    player.remove_consumable(item)
            self._show_message(f"Sold {item.name} for {format_coins(price)}.", COLOR_GREEN)

        if getattr(item, "quantity", 0) > 0 and not self._is_gear(item):
            return  # keep selected so repeated presses sell through the stack
        self.selected_player_item = None

    def _junk_stacks(self):
        player = self.state_manager.player
        return [i for i in player.inventory
                if isinstance(i, LootItem) and i.category == "trash" and i.is_sellable]

    def _sell_all_junk(self, auto=False):
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
        self._show_message(
            f"{'Auto-sold' if auto else 'Sold'} {count} junk item{'s' if count != 1 else ''} for {format_coins(total)}.",
            COLOR_GREEN)

    def _show_message(self, text, color):
        self.message = text
        self.message_color = color
        self.message_timer = 3.0

    # ------------------------------------------------------------------ update

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state_manager.transition_to(GameState.OVERWORLD)
                return
            if event.key == pygame.K_s:
                self._sell_item()
                return

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            # Vendor item list
            for i, item in enumerate(self.vendor_inventory[self.scroll_vendor:self.scroll_vendor + self.VISIBLE_ROWS]):
                if self._row_rect(self.VENDOR_PANEL_X, i).collidepoint(pos):
                    self.selected_vendor_item = item
                    self.selected_player_item = None
                    return

            # Player item list
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

    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = None

    # ------------------------------------------------------------------ render

    def render(self, screen):
        screen.fill((18, 18, 26))

        self.renderer.draw_text(screen, self.vendor.name, (SCREEN_WIDTH // 2 - 100, 20),
                                size="large", color=COLOR_GOLD)
        if hasattr(self.vendor, "greeting") and self.vendor.greeting:
            self.renderer.draw_text(screen, f'"{self.vendor.greeting}"',
                                    (SCREEN_WIDTH // 2 - 300, 58), size="small", color=(180, 180, 160))
        currency_str = self.state_manager.get_party().get_currency_string()
        self.renderer.draw_text(screen, f"Party gold: {currency_str}",
                                (SCREEN_WIDTH // 2 - 100, 100), color=COLOR_WHITE)

        self._draw_panel_header(screen, self.VENDOR_PANEL_X, "Vendor Stock")
        for i, item in enumerate(self.vendor_inventory[self.scroll_vendor:self.scroll_vendor + self.VISIBLE_ROWS]):
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

    # ------------------------------------------------------------------ helpers

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
        is_mat = self._is_material(item)

        if selected:
            pygame.draw.rect(screen, (60, 55, 30), rect)
            pygame.draw.rect(screen, COLOR_GOLD, rect, 2)
        else:
            pygame.draw.rect(screen, (24, 24, 30), rect)

        is_trash = getattr(item, "category", None) == "trash"
        if is_gear or is_trash or not getattr(item, "is_sellable", True):
            name_color = item.get_rarity_color()
        elif is_mat:
            name_color = (180, 210, 180)  # soft green for reagents — distinguishable from white consumables
        else:
            name_color = COLOR_WHITE

        self.renderer.draw_text(screen, item.name, (rect.x + 10, rect.y + 6),
                                size="small", color=name_color)

        if mode == "buy":
            price = getattr(item, "vendor_price", None)
            if price is None:
                price = max(1, int(item.sell_price * 4))
            price_text = format_coins(price)
        elif not getattr(item, "is_sellable", True):
            qty = getattr(item, "quantity", None)
            price_text = f"x{qty}  Quest" if qty is not None else "Quest"
        else:
            qty = getattr(item, "quantity", None)
            price_text = (f"x{qty}  ->{format_coins(item.sell_price)}" if qty is not None
                          else f"->{format_coins(item.sell_price)}")

        self.renderer.draw_text(screen, price_text, (rect.right - 140, rect.y + 6),
                                size="small", color=COLOR_GOLD)

        if is_gear:
            from world.upgrade_manager import upgrade_tag
            slot_label = item.slot.replace("_", " ").title()
            tag = upgrade_tag(item)
            if tag:
                slot_label = f"{slot_label}  ·  {tag}"
            self.renderer.draw_text(screen, slot_label, (rect.x + 10, rect.y + 24),
                                    size="small", color=(160, 160, 170))
        elif is_mat:
            # Show the profession tag as a sub-label (e.g. "Alchemy · Reagent")
            prof = item.profession.replace("_", " ").title()
            self.renderer.draw_text(screen, prof, (rect.x + 10, rect.y + 24),
                                    size="small", color=(120, 160, 120))

    def _render_tooltip(self, screen, item, mode):
        is_gear = self._is_gear(item)
        is_mat = self._is_material(item)
        lines = [item.name]

        if is_gear:
            # Refined/Superior shown as a badge, never folded into the name.
            from world.upgrade_manager import upgrade_tag
            tag = upgrade_tag(item)
            head = f"{item.rarity.title()} — {item.slot.replace('_', ' ').title()}"
            if tag:
                head += f" — {tag}"
            lines.append(head)
            if item.armor_value:
                lines.append(f"Armor: {item.armor_value}")
            for stat, val in item.primary_stats.items():
                lines.append(f"+{val} {stat.replace('_', ' ').title()}")
            for stat, val in item.secondary_stats.items():
                lines.append(f"+{val} {stat.replace('_', ' ').title()}")
            if item.weapon_damage_max:
                lines.append(f"Damage: {item.weapon_damage_min}–{item.weapon_damage_max}")
            lines.append(f"Requires level {item.required_level}")

        elif is_mat:
            lines.append(f"{item.profession.replace('_', ' ').title()} Reagent")
            if item.description:
                lines.append(item.description)

        elif not getattr(item, "is_sellable", True):
            if getattr(item, "description", ""):
                lines.append(item.description)
            lines.append("Quest Item — cannot be sold")

        elif getattr(item, "category", None) == "trash":
            # Vendor trash is a LootItem, not a Consumable. This branch used
            # to be the bare `else` below, which reads consumable_type and
            # required_level - neither of which a LootItem has - so hovering
            # a piece of trash in the sell list crashed the render loop
            # outright (Kyle: "crashed when going to sell shit").
            lines.append("Junk")
            if getattr(item, "description", ""):
                lines.append(item.description)

        else:
            # Defensive: this is the consumable branch, but it is also the
            # catch-all for any item class that is not gear/material/quest/
            # trash. A missing attribute here takes the whole game down with
            # it, since tooltips render inside the main loop, so every field
            # is optional rather than assumed.
            ctype = getattr(item, "consumable_type", None)
            if ctype:
                lines.append(f"Type: {str(ctype).replace('_', ' ').title()}")
            req = getattr(item, "required_level", 0)
            if req:
                lines.append(f"Requires level {req}")
            if getattr(item, "description", ""):
                lines.append(item.description)

        if mode == "buy":
            price = getattr(item, "vendor_price", None)
            if price is None:
                price = max(1, int(item.sell_price * 4))
            lines.append(f"Price: {format_coins(price)}")
        elif getattr(item, "is_sellable", True):
            lines.append(f"Sells for: {format_coins(item.sell_price)}")

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

    def _get_buy_button_rect(self):
        return pygame.Rect(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT - 70, 140, 44)

    def _get_sell_button_rect(self):
        return pygame.Rect(SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT - 70, 140, 44)

    def _get_close_button_rect(self):
        return pygame.Rect(SCREEN_WIDTH // 2 + 80, SCREEN_HEIGHT - 70, 140, 44)

    def _get_junk_button_rect(self):
        return pygame.Rect(SCREEN_WIDTH // 2 + 230, SCREEN_HEIGHT - 70, 140, 44)

    def _auto_box_rect(self):
        return pygame.Rect(self.PLAYER_PANEL_X, self.PANEL_Y + self.PANEL_HEIGHT + 12, 20, 20)
