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

    #: Sell-side tabs. Kyle, 2026-10-31: "I also need a way to scroll down or sell stuff by tabs -
    #: since this forces me to sell crafting materials before my trash gear."
    #:
    #: Both halves of that are real. scroll_vendor/scroll_player existed from the first version of
    #: this screen and were threaded through every slice and hit test, but NOTHING ever assigned to
    #: them - no wheel handler, no buttons, no keys. The list was permanently frozen on its first
    #: nine rows, and because consumables and materials are concatenated ahead of inventory, gear
    #: was always the part that fell off the bottom.
    SELL_FILTERS = [
        ("all", "All"),
        ("gear", "Gear"),
        ("mats", "Materials"),
        ("supplies", "Supplies"),
        ("junk", "Junk"),
    ]
    TAB_HEIGHT = 24

    def __init__(self, state_manager, vendor):
        super().__init__(state_manager)
        self.vendor = vendor
        self.renderer = Renderer()
        self.consumable_manager = get_consumable_manager()
        self.loot_generator = LootGenerator()

        self.selected_vendor_item = None
        self.selected_player_item = None
        #: How many of the selected vendor item one press of Buy takes. Always 1 for gear.
        self.buy_qty = 1
        self.scroll_vendor = 0
        self.scroll_player = 0
        self.sell_filter = "all"

        self.message = None
        self.message_color = COLOR_WHITE
        self.message_timer = 0.0
        self._plain_armed = False

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
        from world.vendor_stock import resolve_vendor_item
        gathering_mgr = GatheringNodeManager()

        items = []
        for item_id in self.vendor.sells:
            # ONE resolver, shared with every tool that needs the same
            # answer - see world/vendor_stock.py for why that matters. The
            # order (consumable, material/reagent, recipe scroll, bag) and
            # all the reasoning behind it moved there verbatim.
            thing = resolve_vendor_item(
                item_id, consumable_manager=self.consumable_manager,
                gathering_manager=gathering_mgr,
                loot_generator=self.loot_generator)
            if thing is not None:
                items.append(thing)
                continue
            # Genuinely unknown ID - warn and skip rather than crash
            print(f"[VendorScreen] WARNING: unknown sell ID '{item_id}' on vendor '{self.vendor.vendor_id}'")

        # A recipe scroll carries vendor_price=None (its price is worked out from sell_price),
        # and None cannot be sorted against a number: every shop that sold a recipe crashed.
        items.sort(key=self._unit_price)

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

    def _category_of(self, item):
        """Which sell tab an item belongs under. Trash is tested FIRST because a
        piece of vendor trash is a LootItem with a slot and an armor_value, so
        _is_gear says yes to it and it would otherwise file under Gear."""
        if getattr(item, "category", None) == "trash":
            return "junk"
        if self._is_material(item):
            return "mats"
        if self._is_gear(item):
            return "gear"
        return "supplies"

    def _player_stock(self, filtered=True):
        """Player's consumables + materials + inventory gear, read fresh every
        call so newly bought items appear immediately.

        Filtered by the active sell tab unless asked otherwise - the unfiltered
        list is what the tab counts are drawn from.
        """
        player = self.state_manager.player
        stock = (list(player.consumables) + list(getattr(player, "materials", []))
                 + list(player.inventory))
        if filtered and self.sell_filter != "all":
            stock = [i for i in stock if self._category_of(i) == self.sell_filter]
        return stock

    # ------------------------------------------------------------------ scrolling

    def _max_scroll(self, count):
        return max(0, count - self.VISIBLE_ROWS)

    def _clamp_scrolls(self):
        """Both scroll positions, pulled back into range.

        Called on every render as well as on every wheel event, because the
        lists SHRINK underneath the scroll position: sell the last four things
        on page two and page two stops existing. Clamping only on input would
        leave the panel showing nothing with no way to tell why.
        """
        self.scroll_vendor = max(0, min(self.scroll_vendor,
                                        self._max_scroll(len(self.vendor_inventory))))
        self.scroll_player = max(0, min(self.scroll_player,
                                        self._max_scroll(len(self._player_stock()))))

    def _panel_rect(self, x):
        return pygame.Rect(x, self.PANEL_Y, self.PANEL_WIDTH, self.PANEL_HEIGHT)

    def _filter_tab_rects(self):
        """tab key -> rect, laid out in a row above the player panel."""
        rects = {}
        x = self.PLAYER_PANEL_X + 112  # clear of the "Your Items" header on the same line
        for key, label in self.SELL_FILTERS:
            w = 10 + 8 * len(label) + 10
            rects[key] = pygame.Rect(x, self.PANEL_Y - self.TAB_HEIGHT - 4, w, self.TAB_HEIGHT)
            x += w + 4
        return rects

    # ------------------------------------------------------------------ actions

    #: The most one purchase can take. A full stack of anything in the game is 20 or 200;
    #: this is a ceiling on a typo, not a design limit.
    MAX_BUY_QTY = 200

    def _stackable(self, item):
        """Reagents, food, drink - anything that is not a single piece of gear."""
        return item is not None and not self._is_gear(item)

    def _unit_price(self, item):
        price = getattr(item, "vendor_price", None)
        if not price:
            # None (a recipe scroll) or 0: six planks and a feast were on sale for nothing.
            price = max(1, int((getattr(item, "sell_price", 0) or 0) * 4))
        return int(price)

    def _set_buy_qty(self, qty):
        item = self.selected_vendor_item
        if not self._stackable(item):
            self.buy_qty = 1
            return
        self.buy_qty = max(1, min(self.MAX_BUY_QTY, int(qty)))

    def _qty_rects(self):
        """The quantity controls, left of the Buy button: [-20] [-5] [-] [N] [+] [+5] [+20].

        Kyle, 14 Nov 2026: "with multiple buy option of +1 +5 +20.... there is only -1". The row
        is narrower per button so all seven and the total still fit left of Buy."""
        buy = self._get_buy_button_rect()
        x, y, h = self.VENDOR_PANEL_X, buy.y, buy.height
        out, widths = {}, (("minus20", 40), ("minus5", 34), ("minus", 28), ("count", 44),
                           ("plus", 28), ("plus5", 34), ("plus20", 40))
        for key, w in widths:
            out[key] = pygame.Rect(x, y, w, h)
            x += w + 4
        out["total_x"] = x + 4
        return out

    def _buy_item(self):
        """Buy buy_qty of the selected item, all or nothing.

        Kyle, 12 Nov: "When buying stuff from shop (like crafting reagents/food/drink) -
        should be able to buy more than one at a time." It was one per click, and the
        selection was cleared after each, so twenty of anything was forty clicks.

        The whole purchase is priced and paid for first, then delivered; if the gold is not
        there nothing is bought, and the message says how many WOULD fit the purse. The
        selection and the quantity are kept afterwards so the same order can be repeated.
        """
        item = self.selected_vendor_item
        if item is None:
            self._show_message("Select something to buy first.", COLOR_RED)
            return

        qty = self.buy_qty if self._stackable(item) else 1
        unit = self._unit_price(item)
        price = unit * qty

        player = self.state_manager.player
        party = self.state_manager.get_party()
        if not party.remove_currency(price):
            can = party.copper // unit if unit else 0
            if qty > 1 and can >= 1:
                self._show_message(
                    f"Not enough copper for {qty} - need {format_coins(price)}. "
                    f"You can afford {can}.", COLOR_RED)
            else:
                self._show_message(f"Not enough copper! Need {format_coins(price)}.", COLOR_RED)
            return

        label = f"{qty} x {item.name}" if qty > 1 else item.name

        if self._is_gear(item):
            if not player.add_to_inventory(item):
                party.add_currency(price)
                self._show_message("Your bags are full - purchase refunded.", COLOR_RED)
                self.selected_vendor_item = None
                return
            self._show_message(f"Bought {item.name} for {format_coins(price)}.", COLOR_GOLD)
            self.selected_vendor_item = None
            return

        if self._is_material(item):
            # A fresh instance each, from the gathering manager, so the vendor's display copy
            # is never mutated - and one at a time through add_material, which is what knows
            # how to fill a stack and start the next.
            from world.gathering_manager import GatheringNodeManager
            maker = GatheringNodeManager()
            if maker.make_material_instance(item.material_id) is None:
                party.add_currency(price)
                self._show_message("Couldn't resolve that item — refunded.", COLOR_RED)
                self.selected_vendor_item = None
                return
            for _ in range(qty):
                player.add_material(maker.make_material_instance(item.material_id))
        else:
            # Consumable - stacks onto an existing entry with the same id.
            for _ in range(qty):
                player.add_consumable(
                    self.consumable_manager.get_consumable(item.consumable_id, quantity=1))

        self._show_message(f"Bought {label} for {format_coins(price)}.", COLOR_GOLD)

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

    #: Playtest, 14 Nov 2026: "a way to sell all grey and white non junk items at once". Gear of
    #: these two rarities, in the bags (never what is worn), plus the vendor trash Sell Junk sells.
    PLAIN_RARITIES = ("poor", "common")

    def _plain_gear_stacks(self):
        player = self.state_manager.player
        worn = set(id(i) for i in player.equipment.to_dict().values() if i is not None)
        out = []
        for i in player.inventory:
            if id(i) in worn or not getattr(i, "is_sellable", True):
                continue
            if isinstance(i, LootItem) and i.category == "trash":
                out.append(i)
            elif (self._is_gear(i) and getattr(i, "rarity", None) in self.PLAIN_RARITIES
                    and not getattr(i, "set_id", None)):
                out.append(i)
        return out

    def _sell_all_plain(self):
        """First click names what will go and for how much; a second click within the message's
        life sells it. Whites can still be wanted early on, so it never sells on one click."""
        if not self.vendor.buys_from_player:
            self._show_message(f"{self.vendor.name} doesn't buy from adventurers.", COLOR_RED)
            return
        stacks = self._plain_gear_stacks()
        if not stacks:
            self._show_message("No grey or white items to sell.", COLOR_WHITE)
            return
        count = sum(max(1, getattr(i, "quantity", 1) or 1) for i in stacks)
        total = sum(i.sell_price * max(1, getattr(i, "quantity", 1) or 1) for i in stacks)
        if not (self._plain_armed and self.message_timer > 0):
            self._plain_armed = True
            self._show_message(f"Click again to sell {count} grey and white item"
                               f"{'s' if count != 1 else ''} for {format_coins(total)}.", COLOR_GOLD)
            return
        self._plain_armed = False
        player = self.state_manager.player
        for i in stacks:
            player.inventory.remove(i)
        self.state_manager.get_party().add_currency(total)
        if self.selected_player_item in stacks:
            self.selected_player_item = None
        self._show_message(f"Sold {count} grey and white item{'s' if count != 1 else ''} for "
                           f"{format_coins(total)}.", COLOR_GREEN)

    def _get_plain_button_rect(self):
        return pygame.Rect(SCREEN_WIDTH // 2 + 380, SCREEN_HEIGHT - 70, 230, 44)

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
            # Quantity from the keyboard: + and - (main row or numpad).
            if event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                self._set_buy_qty(self.buy_qty + 1)
                return
            if event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                self._set_buy_qty(self.buy_qty - 1)
                return
            # Keyboard scrolling for the sell list, which is the one that grows.
            if event.key in (pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                step = self.VISIBLE_ROWS if event.key == pygame.K_PAGEDOWN else -self.VISIBLE_ROWS
                self.scroll_player += step
                self._clamp_scrolls()
                return
            if event.key == pygame.K_TAB:
                keys = [k for k, _ in self.SELL_FILTERS]
                self.sell_filter = keys[(keys.index(self.sell_filter) + 1) % len(keys)]
                self.scroll_player = 0
                self.selected_player_item = None
                return

        elif event.type == pygame.MOUSEWHEEL:
            # Scroll whichever panel the cursor is over. event.y is +1 up / -1 down.
            # A real MOUSEWHEEL carries no position, so the cursor is queried. The
            # headless QA harness cannot move a cursor under the dummy video driver,
            # so an event that DOES carry a pos is honoured.
            mx, my = getattr(event, "pos", None) or pygame.mouse.get_pos()
            if self._panel_rect(self.PLAYER_PANEL_X).collidepoint(mx, my):
                self.scroll_player -= event.y
            elif self._panel_rect(self.VENDOR_PANEL_X).collidepoint(mx, my):
                self.scroll_vendor -= event.y
            self._clamp_scrolls()
            return

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            for key, rect in self._filter_tab_rects().items():
                if rect.collidepoint(pos):
                    self.sell_filter = key
                    self.scroll_player = 0
                    self.selected_player_item = None
                    return

            # Vendor item list
            for i, item in enumerate(self.vendor_inventory[self.scroll_vendor:self.scroll_vendor + self.VISIBLE_ROWS]):
                if self._row_rect(self.VENDOR_PANEL_X, i).collidepoint(pos):
                    if item is not self.selected_vendor_item:
                        self.buy_qty = 1          # a new item starts at one
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

            if self._stackable(self.selected_vendor_item):
                q = self._qty_rects()
                for key, delta in (("minus20", -20), ("minus5", -5), ("minus", -1), ("plus", 1),
                                   ("plus5", 5), ("plus20", 20)):
                    if q[key].collidepoint(pos):
                        # +5 and +20 from a fresh 1 give 5 and 20, not 6 and 21: the first
                        # press of a "stack" button means "that many".
                        if delta > 1 and self.buy_qty == 1:
                            self._set_buy_qty(delta)
                        else:
                            self._set_buy_qty(self.buy_qty + delta)
                        return

            if self._get_plain_button_rect().collidepoint(pos):
                self._sell_all_plain()
                return
            self._plain_armed = False
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
            # Wrapped, and the paragraph breaks joined. It was one draw_text call, so a greeting
            # with two paragraphs ran off the right of the screen with the newlines drawn as
            # boxes in the middle of it (seen 14 Nov 2026 on every shop rewritten in two parts).
            flat = " ".join(p.strip() for p in str(self.vendor.greeting).split("\n") if p.strip())
            lines = self.renderer.wrap_text(f'"{flat}"', SCREEN_WIDTH - 100, size="small")
            if len(lines) > 2:
                lines = lines[:2]
                lines[1] = lines[1].rstrip(' "') + '..."'
            for n, line in enumerate(lines):
                self.renderer.draw_text(screen, line, (50, 56 + n * 19), size="small",
                                        color=(180, 180, 160))
        currency_str = self.state_manager.get_party().get_currency_string()
        self.renderer.draw_text(screen, f"Party gold: {currency_str}",
                                (SCREEN_WIDTH // 2 - 100, 100), color=COLOR_WHITE)

        self._clamp_scrolls()

        self._draw_panel_header(screen, self.VENDOR_PANEL_X, "Vendor Stock")
        for i, item in enumerate(self.vendor_inventory[self.scroll_vendor:self.scroll_vendor + self.VISIBLE_ROWS]):
            self._draw_item_row(screen, self.VENDOR_PANEL_X, i, item,
                                selected=(item is self.selected_vendor_item), mode="buy")
        self._draw_scrollbar(screen, self.VENDOR_PANEL_X, len(self.vendor_inventory), self.scroll_vendor)

        self._draw_panel_header(screen, self.PLAYER_PANEL_X, "Your Items")
        self._draw_filter_tabs(screen)
        player_stock = self._player_stock()
        for i, item in enumerate(player_stock[self.scroll_player:self.scroll_player + self.VISIBLE_ROWS]):
            self._draw_item_row(screen, self.PLAYER_PANEL_X, i, item,
                                selected=(item is self.selected_player_item), mode="sell")
        if not player_stock:
            self.renderer.draw_text(screen, "Nothing here.",
                                    (self.PLAYER_PANEL_X + 14, self.PANEL_Y + 14),
                                    size="small", color=(120, 120, 130))
        self._draw_scrollbar(screen, self.PLAYER_PANEL_X, len(player_stock), self.scroll_player)

        buy_rect = self._get_buy_button_rect()
        sell_rect = self._get_sell_button_rect()
        close_rect = self._get_close_button_rect()

        buy_enabled = self.selected_vendor_item is not None
        sell_enabled = self.selected_player_item is not None

        pygame.draw.rect(screen, (40, 70, 40) if buy_enabled else (30, 30, 30), buy_rect)
        pygame.draw.rect(screen, COLOR_GREEN if buy_enabled else COLOR_DARK_GRAY, buy_rect, 2)
        stackable = self._stackable(self.selected_vendor_item)
        buy_label = f"Buy x{self.buy_qty}" if (stackable and self.buy_qty > 1) else "Buy"
        self.renderer.draw_text(screen, buy_label, (buy_rect.x + 20, buy_rect.y + 10),
                                color=COLOR_GREEN if buy_enabled else COLOR_DARK_GRAY)

        # Quantity controls - only for something that stacks. Gear is always one.
        if stackable:
            q = self._qty_rects()
            for key, text in (("minus20", "-20"), ("minus5", "-5"), ("minus", "-"), ("plus", "+"),
                              ("plus5", "+5"), ("plus20", "+20")):
                r = q[key]
                pygame.draw.rect(screen, (40, 50, 60), r)
                pygame.draw.rect(screen, (120, 140, 160), r, 2)
                tw = self.renderer.font_normal.size(text)[0]
                self.renderer.draw_text(screen, text, (r.centerx - tw // 2, r.y + 12),
                                        color=(210, 220, 230))
            r = q["count"]
            pygame.draw.rect(screen, (20, 20, 26), r)
            pygame.draw.rect(screen, COLOR_GOLD, r, 1)
            count = str(self.buy_qty)
            tw = self.renderer.font_normal.size(count)[0]
            self.renderer.draw_text(screen, count, (r.centerx - tw // 2, r.y + 12), color=COLOR_GOLD)
            total = self._unit_price(self.selected_vendor_item) * self.buy_qty
            afford = self.state_manager.get_party().copper >= total
            self.renderer.draw_text(screen, format_coins(total), (q["total_x"], r.y + 12),
                                    size="small", color=COLOR_GOLD if afford else COLOR_RED)

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

        plain_rect = self._get_plain_button_rect()
        has_plain = bool(self._plain_gear_stacks()) and self.vendor.buys_from_player
        pygame.draw.rect(screen, (60, 60, 60) if has_plain else (30, 30, 30), plain_rect)
        pygame.draw.rect(screen, (200, 200, 200) if has_plain else COLOR_DARK_GRAY, plain_rect, 2)
        self.renderer.draw_text(screen, "Sell Greys & Whites", (plain_rect.x + 14, plain_rect.y + 10),
                                color=(220, 220, 220) if has_plain else COLOR_DARK_GRAY)

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

    def _draw_filter_tabs(self, screen):
        counts = {}
        for item in self._player_stock(filtered=False):
            counts[self._category_of(item)] = counts.get(self._category_of(item), 0) + 1
        total = sum(counts.values())
        rects = self._filter_tab_rects()
        for key, label in self.SELL_FILTERS:
            rect = rects[key]
            active = key == self.sell_filter
            n = total if key == "all" else counts.get(key, 0)
            # An empty tab is drawn greyed rather than hidden, so the row does not
            # reflow under the cursor as the player sells their way through it.
            if active:
                pygame.draw.rect(screen, (60, 55, 30), rect)
                pygame.draw.rect(screen, COLOR_GOLD, rect, 2)
                color = COLOR_GOLD
            else:
                pygame.draw.rect(screen, (26, 26, 33), rect)
                pygame.draw.rect(screen, (70, 70, 85), rect, 1)
                color = (170, 170, 180) if n else (95, 95, 105)
            self.renderer.draw_text(screen, f"{label} {n}", (rect.x + 7, rect.y + 4),
                                    size="small", color=color)

    def _draw_scrollbar(self, screen, panel_x, total, scroll):
        """A track and thumb on the panel's right edge, drawn only when there is
        something off-screen. Without it the wheel works but nothing says so."""
        if total <= self.VISIBLE_ROWS:
            return
        track = pygame.Rect(panel_x + self.PANEL_WIDTH - 9, self.PANEL_Y + 3,
                            6, self.PANEL_HEIGHT - 6)
        pygame.draw.rect(screen, (20, 20, 26), track)
        thumb_h = max(24, int(track.height * self.VISIBLE_ROWS / total))
        span = track.height - thumb_h
        top = track.y + int(span * scroll / max(1, self._max_scroll(total)))
        pygame.draw.rect(screen, (110, 110, 130), pygame.Rect(track.x, top, track.width, thumb_h))

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
            price = self._unit_price(item)
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
            from ui.item_kind import item_kind
            slot_label = item_kind(item)                 # "Leather Chest", "Two-Hand Axe"
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
            from ui.item_kind import item_kind
            head = f"{item.rarity.title()} — {item_kind(item)}"
            if tag:
                head += f" — {tag}"
            lines.append(head)
            # Kyle, 5 Nov 2026: "We should also include a description of how
            # many slots each bag has when you hover over it." Capacity is the
            # ONLY thing that separates one bag from another - a shelf now
            # showing 6, 8 and 10-slot bags at three different prices is
            # unreadable without it, and the icon art does not say.
            #
            # Placed above armor/stats because for a bag it IS the stat line.
            if getattr(item, "bag_capacity", 0):
                slots = item.bag_capacity
                lines.append(f"{slots} Slot Bag")
            if item.armor_value:
                lines.append(f"Armor: {item.armor_value}")
            for stat, val in item.primary_stats.items():
                lines.append(f"+{val} {stat.replace('_', ' ').title()}")
            for stat, val in item.secondary_stats.items():
                lines.append(f"+{val} {stat.replace('_', ' ').title()}")
            if item.weapon_damage_max:
                lines.append(f"Damage: {item.weapon_damage_min}–{item.weapon_damage_max}")
            from world.jewelcrafting import tooltip_lines as _socket_lines
            lines.extend(text for text, _kind in _socket_lines(item))
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
            price = self._unit_price(item)
            lines.append(f"Price: {format_coins(price)}")
        elif getattr(item, "is_sellable", True):
            lines.append(f"Sells for: {format_coins(item.sell_price)}")

        mouse_pos = pygame.mouse.get_pos()
        box_width = 320
        line_height = 20

        # Kyle, 2026-10-31: "words are running off." The box is a fixed 320px
        # and four separate branches above append item.description as one
        # unbroken line, so any flavour text longer than the box drew through
        # its right-hand border. Wrapped HERE, once, after every branch has had
        # its say - doing it per-branch would be four copies of one rule, which
        # is exactly how this got four ways to overflow in the first place.
        # Wrapped at size="small" because that is what the draw loop below uses.
        wrapped = []
        for line in lines:
            wrapped.extend(self.renderer.wrap_text(str(line), box_width - 16, size="small"))
        lines = wrapped

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
