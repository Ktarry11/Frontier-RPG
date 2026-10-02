"""
Professions screen - shows the player's gathering profession skill levels
(Herbalism, Mining, ...) with a real progress bar toward the current tier
cap, plus a placeholder recipe section for each profession.

Separate screen from Skills/Talents (SkillsScreen - abilities/hotbar) and
from the Inventory screen's Materials tab (what you're HOLDING) - this is
specifically "how good am I at gathering", which didn't have anywhere to
live before except a buried one-line readout at the top of the Materials
tab. Kyle's ask: its own screen, reachable from the overworld tab column,
not squeezed into an existing screen.

Recipes are placeholder-only in Phase 1 (empty list, "Recipes - unlocks
with crafting professions" label) - there is no crafting system yet, so
listing anything real here would be lying about what the game can
currently do. The section exists now so the layout doesn't need to be
rebuilt when crafting arrives; it just gets populated.
"""
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_GOLD, COLOR_LIGHT_GRAY
from core.game_states import GameState
from ui.screens.base_screen import BaseScreen
from ui.sprite_loader import get_tile_sprite
from world.gathering_manager import TIER_SKILL_CAPS, MATERIAL_TYPE_FOLDERS, get_gathering_node_manager
from world.smelting_manager import get_smelting_manager
from world.blacksmithing_manager import get_blacksmithing_manager
from world.upgrade_manager import get_kit_for_item, can_upgrade, upgrade_item, next_rarity_for, MAX_UPGRADE_COUNT


#: Display order and label for each known gathering profession. A
#: profession not in this list still shows if the character has it in
#: profession_skills (falls back to its raw dict key, title-cased) - this
#: list only controls ordering/labeling for the ones Phase 1 knows about,
#: it's not a hard whitelist that could hide a real profession.
PROFESSION_DISPLAY_ORDER = [
    ("herbalism", "Herbalism"),
    ("mining", "Mining"),
]

PANEL_X = 20
PANEL_Y = 70
PANEL_WIDTH = SCREEN_WIDTH - 260  # leaves room for the tab column on the right, same margin style as overworld screens
BAR_HEIGHT = 28
BAR_GAP = 70


class ProfessionsScreen(BaseScreen):
    """Profession skill overview PLUS a real Smelting sub-tab (Kyle,
    2026-09-12: "professions tab to have sub tabs for each thing").
    Overview is read-only (skill bars); Smelting is interactive
    (craft bars from ore) but only near a Forge, matching real WoW
    ("Smelting can only be done at a Forge" - confirmed via web search).
    Future profession sub-tabs (Alchemy, etc.) follow the same
    self.active_tab pattern once they exist."""

    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.close_button = pygame.Rect(SCREEN_WIDTH - 120, 20, 100, 50)
        self.subject = None
        self.return_state = GameState.OVERWORLD

        self.active_tab = "overview"
        self.overview_tab_button = pygame.Rect(SCREEN_WIDTH - 720, 20, 120, 36)
        self.smelting_tab_button = pygame.Rect(SCREEN_WIDTH - 590, 20, 120, 36)
        self.blacksmithing_tab_button = pygame.Rect(SCREEN_WIDTH - 460, 20, 150, 36)
        #: Upgrade Kit tab - deliberately NOT tied to Blacksmithing, even
        #: though Blacksmithing is the only profession that exists today.
        #: Kyle, Oct 2026: "This will be for every crafting thing too.
        #: Leather worker, tailor, etc." - every future crafting
        #: profession will craft its OWN kits the same way (Kyle's
        #: earlier "all crafters will craft their upgrade kits" rule),
        #: and a crafted Leatherworked/Tailored item is just as eligible
        #: as a crafted Blacksmithed one (upgrade_manager.py's own
        #: can_upgrade/get_kit_for_item never check which profession made
        #: the item, only item.is_crafted + its current rarity) - so this
        #: lives as its own tab, scanning the ENTIRE inventory for any
        #: crafted+eligible item, rather than being folded into
        #: Blacksmithing's tab where it would need rebuilding the moment
        #: a second crafting profession ships.
        self.upgrade_tab_button = pygame.Rect(SCREEN_WIDTH - 300, 20, 130, 36)

        self.smelting_manager = get_smelting_manager()
        self.blacksmithing_manager = get_blacksmithing_manager()
        self.gathering_manager = get_gathering_node_manager()
        self.smelt_message = None
        self.smelt_message_color = (140, 220, 160)
        self.smelt_message_timer = 0.0
        self.recipe_rects = []  # index-aligned to the recipe list currently rendered
        self.craft_message = None
        self.craft_message_color = (140, 220, 160)
        self.craft_message_timer = 0.0
        self.craft_recipe_rects = []  # index-aligned to blacksmithing's own recipe list

        #: Upgrade tab state. selected_upgrade_item is the inventory Item
        #: currently chosen to upgrade (None = no selection yet); clicking
        #: a kit button while an eligible item is selected applies it.
        #: Index-aligned rect lists rebuilt every render, same convention
        #: as recipe_rects/craft_recipe_rects above.
        self.selected_upgrade_item = None
        self.upgrade_item_rects = []  # eligible crafted items in the bag
        self.upgrade_kit_button_rects = []  # one rect per kit the player holds that fits the selected item
        self.upgrade_message = None
        self.upgrade_message_color = (140, 220, 160)
        self.upgrade_message_timer = 0.0

    def set_subject(self, character, return_state=None):
        """Point the screen at a character (party screen uses this) -
        same pattern as InventoryScreen/SkillsScreen's set_subject."""
        self.subject = character
        self.active_tab = "overview"
        if return_state is not None:
            self.return_state = return_state

    def _get_subject(self):
        return self.subject or self.state_manager.player

    def _close(self):
        destination = self.return_state or GameState.OVERWORLD
        self.subject = None
        self.return_state = GameState.OVERWORLD
        self.state_manager.transition_to(destination)

    def _at_forge(self):
        """True if the player character (not necessarily the screen's
        subject - smelting is always the PLAYER's own action, same as
        gathering, even when viewing a companion's overview tab) is
        currently standing on a Forge tile. Reads the real ZoneManager
        state rather than trusting anything cached, since forge
        proximity can change every time the player moves before this
        screen is reopened."""
        zone_manager = getattr(self.state_manager.states.get(GameState.OVERWORLD), "zone_manager", None)
        if zone_manager is None:
            return False
        return zone_manager.get_forge_at_location() is not None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._close()
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.close_button.collidepoint(event.pos):
                self._close()
                return
            if self.overview_tab_button.collidepoint(event.pos):
                self.active_tab = "overview"
                return
            if self.smelting_tab_button.collidepoint(event.pos):
                self.active_tab = "smelting"
                return
            if self.blacksmithing_tab_button.collidepoint(event.pos):
                self.active_tab = "blacksmithing"
                return
            if self.upgrade_tab_button.collidepoint(event.pos):
                self.active_tab = "upgrade"
                self.selected_upgrade_item = None
                return
            if self.active_tab == "smelting":
                for i, rect in enumerate(self.recipe_rects):
                    if rect.collidepoint(event.pos):
                        self._attempt_smelt(i)
                        return
            if self.active_tab == "blacksmithing":
                for i, rect in enumerate(self.craft_recipe_rects):
                    if rect.collidepoint(event.pos):
                        self._attempt_craft(i)
                        return
            if self.active_tab == "upgrade":
                for item, rect in self.upgrade_item_rects:
                    if rect.collidepoint(event.pos):
                        # Re-clicking the already-selected item deselects
                        # it - a cheap toggle so there's always a way back
                        # to the "pick an item" state without a separate
                        # Cancel button.
                        self.selected_upgrade_item = None if self.selected_upgrade_item is item else item
                        return
                for kit_id, rect in self.upgrade_kit_button_rects:
                    if rect.collidepoint(event.pos):
                        self._attempt_upgrade(kit_id)
                        return

    def _attempt_smelt(self, recipe_index):
        """Craft the recipe at recipe_index in the currently-displayed
        list. Always the PLAYER's own materials/skill, same "smelting is
        a player action, not a viewed-subject action" reasoning as
        _at_forge above - viewing a companion's Overview tab should never
        let you smelt using the companion's inventory."""
        player = self.state_manager.player
        if not self._at_forge():
            self.smelt_message = "You must be at a Forge to smelt."
            self.smelt_message_color = (240, 140, 140)
            self.smelt_message_timer = 3.0
            return

        available = self.smelting_manager.available_recipes(player)
        output_ids = list(available.keys())
        if recipe_index >= len(output_ids):
            return
        output_id = output_ids[recipe_index]

        result = self.smelting_manager.smelt(player, output_id, self.gathering_manager)
        if result is None:
            self.smelt_message = "Missing materials for that recipe."
            self.smelt_message_color = (240, 140, 140)
            self.smelt_message_timer = 3.0
        else:
            self.smelt_message = f"Smelted {result.name}."
            self.smelt_message_color = (140, 220, 160)
            self.smelt_message_timer = 3.0

    def _attempt_craft(self, recipe_index):
        """Craft the Blacksmithing recipe at recipe_index. Real WoW
        Blacksmithing has no location requirement (unlike Smelting's
        real "only at a Forge" rule) - no _at_forge()-equivalent check
        here, matching this project's "what did WoW do?" north star.
        Always the PLAYER's own materials/skill, same reasoning as
        _attempt_smelt."""
        player = self.state_manager.player
        available = self.blacksmithing_manager.available_recipes(player)
        recipe_ids = list(available.keys())
        if recipe_index >= len(recipe_ids):
            return
        recipe_id = recipe_ids[recipe_index]

        result = self.blacksmithing_manager.craft(player, recipe_id)
        if result is None:
            # can_craft already distinguishes "missing bars" from "bag
            # full" internally, but craft() itself only returns None for
            # either - re-check here just for the message, same
            # "friendlier message, same underlying gate" pattern as
            # _attempt_smelt's single generic failure string.
            if len(player.inventory) >= player.inventory_capacity:
                self.craft_message = "Your bags are full."
            else:
                self.craft_message = "Missing materials for that recipe."
            self.craft_message_color = (240, 140, 140)
            self.craft_message_timer = 3.0
        else:
            self.craft_message = f"Crafted {result.name}."
            self.craft_message_color = (140, 220, 160)
            self.craft_message_timer = 3.0

    def _attempt_upgrade(self, kit_material_id):
        """Apply kit_material_id to self.selected_upgrade_item. Always the
        PLAYER's own bag/materials, same "it's always the player acting"
        reasoning as _attempt_smelt/_attempt_craft - this tab is never
        shown for a companion subject in the first place (see
        _render_upgrade_tab), so there's no viewed-subject ambiguity to
        guard against here the way _at_forge has to.

        upgrade_item() re-checks can_upgrade() itself and guarantees the
        kit is never consumed on failure, so this method doesn't need to
        duplicate that check - it only needs to turn the result into a
        message, same division of responsibility as _attempt_craft."""
        player = self.state_manager.player
        item = self.selected_upgrade_item
        if item is None:
            return

        result = upgrade_item(player, item, kit_material_id)
        if result is None:
            self.upgrade_message = "That kit doesn't fit this item."
            self.upgrade_message_color = (240, 140, 140)
            self.upgrade_message_timer = 3.0
        else:
            # upgrade_count is 1 right after the FIRST application (the
            # one that moved the rarity) and 2 right after the SECOND
            # (stats-only, rarity frozen - Kyle: "green stays green") -
            # the message needs to say which one just happened rather
            # than always claiming a rarity change.
            if result.upgrade_count == 1:
                self.upgrade_message = f"{result.name} upgraded to {result.rarity.title()}!"
            else:
                self.upgrade_message = f"{result.name} refined further (stats boosted again)."
            self.upgrade_message_color = (140, 220, 160)
            self.upgrade_message_timer = 3.0
            # The item may no longer be eligible for ANY kit (if it just
            # hit upgrade_count == 2, it's permanently done) - clear the
            # selection rather than leaving a stale reference pointing at
            # an item that might not even still list a kit button under
            # it next render.
            self.selected_upgrade_item = None

    def update(self, dt):
        if self.smelt_message_timer > 0:
            self.smelt_message_timer -= dt
            if self.smelt_message_timer <= 0:
                self.smelt_message = None
        if self.craft_message_timer > 0:
            self.craft_message_timer -= dt
            if self.craft_message_timer <= 0:
                self.craft_message = None
        if self.upgrade_message_timer > 0:
            self.upgrade_message_timer -= dt
            if self.upgrade_message_timer <= 0:
                self.upgrade_message = None

    def render(self, screen):
        subject = self._get_subject()

        player = self.state_manager.player
        base_title = {
            "overview": "PROFESSIONS",
            "smelting": "SMELTING",
            "blacksmithing": "BLACKSMITHING",
            "upgrade": "UPGRADE GEAR",
        }.get(self.active_tab, "PROFESSIONS")
        if subject is player:
            title = base_title
        else:
            title = f"{subject.name.upper()}'S {base_title}"
        self.renderer.draw_text(screen, title, (20, 20), size="large", color=COLOR_GOLD)

        # ---- Sub-tab buttons - always visible ----
        overview_color = COLOR_GOLD if self.active_tab == "overview" else (90, 90, 95)
        smelting_color = COLOR_GOLD if self.active_tab == "smelting" else (90, 90, 95)
        self.renderer.draw_rect(screen, self.overview_tab_button, (35, 35, 40))
        self.renderer.draw_rect(screen, self.overview_tab_button, overview_color, fill=False)
        self.renderer.draw_text(screen, "Overview", (self.overview_tab_button.x + 20, self.overview_tab_button.y + 9), color=overview_color)
        self.renderer.draw_rect(screen, self.smelting_tab_button, (35, 35, 40))
        self.renderer.draw_rect(screen, self.smelting_tab_button, smelting_color, fill=False)
        self.renderer.draw_text(screen, "Smelting", (self.smelting_tab_button.x + 22, self.smelting_tab_button.y + 9), color=smelting_color)
        blacksmithing_color = COLOR_GOLD if self.active_tab == "blacksmithing" else (90, 90, 95)
        self.renderer.draw_rect(screen, self.blacksmithing_tab_button, (35, 35, 40))
        self.renderer.draw_rect(screen, self.blacksmithing_tab_button, blacksmithing_color, fill=False)
        self.renderer.draw_text(screen, "Blacksmithing", (self.blacksmithing_tab_button.x + 12, self.blacksmithing_tab_button.y + 9), color=blacksmithing_color)
        upgrade_color = COLOR_GOLD if self.active_tab == "upgrade" else (90, 90, 95)
        self.renderer.draw_rect(screen, self.upgrade_tab_button, (35, 35, 40))
        self.renderer.draw_rect(screen, self.upgrade_tab_button, upgrade_color, fill=False)
        self.renderer.draw_text(screen, "Upgrade", (self.upgrade_tab_button.x + 24, self.upgrade_tab_button.y + 9), color=upgrade_color)

        if self.active_tab == "smelting":
            self._render_smelting_tab(screen)
            self.renderer.draw_button(screen, self.close_button, "Close")
            return

        if self.active_tab == "blacksmithing":
            self._render_blacksmithing_tab(screen)
            self.renderer.draw_button(screen, self.close_button, "Close")
            return

        if self.active_tab == "upgrade":
            self._render_upgrade_tab(screen)
            self.renderer.draw_button(screen, self.close_button, "Close")
            return

        self._render_overview_tab(screen, subject)
        self.renderer.draw_button(screen, self.close_button, "Close")

    def _render_overview_tab(self, screen, subject):
        skills = subject.profession_skills or {}

        if not skills:
            self.renderer.draw_text(screen, "No professions learned yet.",
                                    (PANEL_X, PANEL_Y), color=(150, 150, 150))
            return

        # Known professions first in a stable, sensible order; anything
        # else the character has (a future profession not yet added to
        # PROFESSION_DISPLAY_ORDER) still shows, appended after - so this
        # screen can never silently hide a real profession just because
        # the display-order list hasn't been updated yet.
        known_keys = {key for key, _ in PROFESSION_DISPLAY_ORDER}
        ordered = list(PROFESSION_DISPLAY_ORDER)
        for key in skills:
            if key not in known_keys:
                ordered.append((key, key.title()))

        y = PANEL_Y
        for prof_key, label in ordered:
            if prof_key not in skills:
                continue
            self._render_profession_bar(screen, prof_key, label, skills[prof_key], y)
            y += BAR_GAP

        # ---- Recipes placeholder section (non-Mining professions only -
        # Mining's real recipes now live in the Smelting sub-tab instead
        # of this placeholder, see _render_smelting_tab) ----
        y += 20
        self.renderer.draw_text(screen, "RECIPES", (PANEL_X, y), color=COLOR_GOLD)
        y += 30
        self.renderer.draw_text(
            screen,
            "Herbalism recipes unlock once Alchemy is added. Mining recipes are under the Smelting tab above.",
            (PANEL_X, y), color=(150, 150, 150))

    def _render_smelting_tab(self, screen):
        """Recipe list: known recipes (skill-gated) each show their
        inputs, whether the player currently has them, and a Smelt
        button - disabled-looking (but still clickable, to surface the
        "you need a Forge" / "missing materials" message rather than
        silently doing nothing) when out of range of a Forge or short on
        materials."""
        player = self.state_manager.player
        at_forge = self._at_forge()

        if not at_forge:
            self.renderer.draw_text(screen, "You are not at a Forge. Find one to smelt.",
                                    (PANEL_X, PANEL_Y), color=(220, 160, 120))
        else:
            self.renderer.draw_text(screen, "At a Forge - ready to smelt.",
                                    (PANEL_X, PANEL_Y), color=(140, 220, 160))

        available = self.smelting_manager.available_recipes(player)
        self.recipe_rects = []

        if not available:
            self.renderer.draw_text(screen, "No smelting recipes known yet - raise your Mining skill by gathering ore.",
                                    (PANEL_X, PANEL_Y + 40), color=(150, 150, 150))
            self._draw_smelt_message(screen)
            return

        y = PANEL_Y + 40
        row_h = 56
        for output_id, recipe in available.items():
            mat_def = self.gathering_manager.get_material_def(output_id)
            name = mat_def["name"] if mat_def else output_id

            rect = pygame.Rect(PANEL_X, y, PANEL_WIDTH, row_h - 8)
            can_craft = self.smelting_manager.can_craft(player, output_id)
            border_color = (140, 220, 160) if (can_craft and at_forge) else (100, 100, 100)
            self.renderer.draw_rect(screen, rect, (30, 30, 35))
            self.renderer.draw_rect(screen, rect, border_color, fill=False)

            icon_drawn = False
            if mat_def and mat_def.get("icon_id"):
                folder = MATERIAL_TYPE_FOLDERS.get(mat_def["material_type"], mat_def["material_type"])
                sprite = get_tile_sprite(f"assets/gathering_nodes/{folder}/{mat_def['icon_id']}.png", (0, 0, 32, 32), 40)
                if sprite is not None:
                    screen.blit(sprite, (rect.x + 8, rect.y + 8))
                    icon_drawn = True

            text_x = rect.x + (56 if icon_drawn else 12)
            input_parts = []
            for input_id, qty in recipe["inputs"].items():
                input_def = self.gathering_manager.get_material_def(input_id)
                input_name = input_def["name"] if input_def else input_id
                have = player.get_material_quantity(input_id)
                input_parts.append(f"{input_name} {have}/{qty}")
            input_line = "   ".join(input_parts)

            self.renderer.draw_text(screen, name, (text_x, rect.y + 6), color=COLOR_WHITE)
            self.renderer.draw_text(screen, input_line, (text_x, rect.y + 26), size="small", color=COLOR_LIGHT_GRAY)

            self.recipe_rects.append(rect)
            y += row_h

        self._draw_smelt_message(screen)

    def _draw_smelt_message(self, screen):
        if self.smelt_message:
            self.renderer.draw_text(screen, self.smelt_message, (PANEL_X, SCREEN_HEIGHT - 60), color=self.smelt_message_color)

    def _render_blacksmithing_tab(self, screen):
        """Recipe list for Blacksmithing - same row shape as
        _render_smelting_tab, with two real differences: no Forge
        requirement (real WoW Blacksmithing can be crafted anywhere,
        unlike Smelting - see _attempt_craft's own docstring), and a
        recipe's display name/inputs come from the recipe dict itself
        (recipe["name"], e.g. "Copper Bracers") rather than looking up an
        output material's name - a Blacksmithing recipe's OUTPUT is
        either a freshly-generated Item (no material def exists for it)
        or an upgrade-kit Material (whose def does exist, but the
        recipe's own authored name is used for consistency with the item
        recipes rather than branching the label lookup by output kind)."""
        player = self.state_manager.player
        available = self.blacksmithing_manager.available_recipes(player)
        self.craft_recipe_rects = []

        if not available:
            self.renderer.draw_text(screen, "No Blacksmithing recipes known yet.",
                                    (PANEL_X, PANEL_Y), color=(150, 150, 150))
            self._draw_craft_message(screen)
            return

        y = PANEL_Y
        row_h = 56
        for recipe_id, recipe in available.items():
            name = recipe["name"]

            rect = pygame.Rect(PANEL_X, y, PANEL_WIDTH, row_h - 8)
            can_craft = self.blacksmithing_manager.can_craft(player, recipe_id)
            border_color = (140, 220, 160) if can_craft else (100, 100, 100)
            self.renderer.draw_rect(screen, rect, (30, 30, 35))
            self.renderer.draw_rect(screen, rect, border_color, fill=False)

            # Real bar icons (same MATERIAL_TYPE_FOLDERS/gathering_manager
            # lookup smelting uses) - every current recipe's FIRST input
            # is always a bar, so this draws that bar's icon as a stand-in
            # for the recipe itself (there's no icon art for the output
            # gear/kit yet - procedural items render as rarity-colored
            # boxes elsewhere in the UI, not real sprites).
            icon_drawn = False
            first_input_id = next(iter(recipe["inputs"]), None)
            input_def = self.gathering_manager.get_material_def(first_input_id) if first_input_id else None
            if input_def and input_def.get("icon_id"):
                folder = MATERIAL_TYPE_FOLDERS.get(input_def["material_type"], input_def["material_type"])
                sprite = get_tile_sprite(f"assets/gathering_nodes/{folder}/{input_def['icon_id']}.png", (0, 0, 32, 32), 40)
                if sprite is not None:
                    screen.blit(sprite, (rect.x + 8, rect.y + 8))
                    icon_drawn = True

            text_x = rect.x + (56 if icon_drawn else 12)
            input_parts = []
            for input_id, qty in recipe["inputs"].items():
                mat_def = self.gathering_manager.get_material_def(input_id)
                input_name = mat_def["name"] if mat_def else input_id
                have = player.get_material_quantity(input_id)
                input_parts.append(f"{input_name} {have}/{qty}")
            input_line = "   ".join(input_parts)

            self.renderer.draw_text(screen, name, (text_x, rect.y + 6), color=COLOR_WHITE)
            self.renderer.draw_text(screen, input_line, (text_x, rect.y + 26), size="small", color=COLOR_LIGHT_GRAY)

            self.craft_recipe_rects.append(rect)
            y += row_h

        self._draw_craft_message(screen)

    def _draw_craft_message(self, screen):
        if self.craft_message:
            self.renderer.draw_text(screen, self.craft_message, (PANEL_X, SCREEN_HEIGHT - 60), color=self.craft_message_color)

    def _render_upgrade_tab(self, screen):
        """Profession-agnostic Upgrade Kit screen (Kyle, Oct 2026: "This
        will be for every crafting thing too. Leather worker, tailor,
        etc.") - scans the PLAYER's entire bag for crafted+eligible
        items rather than anything Blacksmithing-specific, so it needs no
        rework when a second crafting profession ships. Always the
        player's own bag (never a viewed companion's - this tab's
        button/content ignores self.subject entirely, same "upgrading is
        a player action" reasoning _attempt_smelt/_attempt_craft already
        use for crafting itself).

        Two-step flow: click an eligible item on the left to select it
        (stored in self.selected_upgrade_item), which reveals the one
        kit button that actually fits its current rarity on the right
        (get_kit_for_item already returns at most one match - there's
        never a choice to make between competing kits, so this never
        needs to show kits that don't apply)."""
        player = self.state_manager.player
        self.upgrade_item_rects = []
        self.upgrade_kit_button_rects = []

        eligible = [item for item in player.inventory if getattr(item, "is_crafted", False) and get_kit_for_item(item) is not None]

        if not eligible:
            self.renderer.draw_text(
                screen,
                "No crafted gear is eligible for an upgrade right now.",
                (PANEL_X, PANEL_Y), color=(150, 150, 150))
            self.renderer.draw_text(
                screen,
                "Craft gear from a profession (e.g. Blacksmithing) first - only crafted items can be upgraded.",
                (PANEL_X, PANEL_Y + 28), size="small", color=(120, 120, 120))
            self._draw_upgrade_message(screen)
            return

        list_width = 420
        self.renderer.draw_text(screen, "ELIGIBLE ITEMS", (PANEL_X, PANEL_Y), color=COLOR_GOLD)
        y = PANEL_Y + 32
        row_h = 48
        for item in eligible:
            rect = pygame.Rect(PANEL_X, y, list_width, row_h - 8)
            selected = item is self.selected_upgrade_item
            border_color = COLOR_GOLD if selected else (100, 100, 100)
            self.renderer.draw_rect(screen, rect, (30, 30, 35))
            self.renderer.draw_rect(screen, rect, border_color, fill=False)
            self.renderer.draw_text(screen, item.name, (rect.x + 10, rect.y + 6), color=COLOR_WHITE)
            status = f"{item.rarity.title()}   ({item.upgrade_count}/{MAX_UPGRADE_COUNT} upgrades used)"
            self.renderer.draw_text(screen, status, (rect.x + 10, rect.y + 24), size="small", color=COLOR_LIGHT_GRAY)
            self.upgrade_item_rects.append((item, rect))
            y += row_h

        # ---- Right-hand panel: the kit (singular) that fits the
        # currently-selected item, or a prompt to pick one ----
        panel_x = PANEL_X + list_width + 40
        self.renderer.draw_text(screen, "APPLY KIT", (panel_x, PANEL_Y), color=COLOR_GOLD)

        if self.selected_upgrade_item is None:
            self.renderer.draw_text(screen, "Select an item on the left.",
                                    (panel_x, PANEL_Y + 32), color=(150, 150, 150))
            self._draw_upgrade_message(screen)
            return

        item = self.selected_upgrade_item
        kit_id = get_kit_for_item(item)
        if kit_id is None:
            # item.upgrade_count has hit MAX_UPGRADE_COUNT (2) - both
            # applications (rank+stats, then stats-only) are already
            # used up and this item can never be upgraded again.
            # Defensive rather than expected in practice, since
            # selection is cleared on every successful upgrade
            # (_attempt_upgrade), so this item shouldn't normally still
            # be selected once it's maxed.
            self.renderer.draw_text(screen, f"{item.name} is already fully upgraded.",
                                    (panel_x, PANEL_Y + 32), color=(150, 150, 150))
            self._draw_upgrade_message(screen)
            return

        have_qty = player.get_material_quantity(kit_id)
        kit_name = kit_id.replace("upgrade_kit_", "").title() + " Upgrade Kit"

        # Application 1 moves the rarity up one rank; application 2
        # (item.upgrade_count == 1 at this point - get_kit_for_item above
        # already excludes upgrade_count >= 2) is stats-only and the
        # rarity is frozen at whatever application 1 left it at (Kyle:
        # "green stays green") - the label needs to say which is about
        # to happen, not always claim a rarity change.
        if item.upgrade_count == 0:
            to_rarity = next_rarity_for(item.rarity)
            effect_line = f"{item.rarity.title()} -> {to_rarity.title()}   (have {have_qty})"
        else:
            effect_line = f"Refine further (1.5x stat bump, stays {item.rarity.title()})   (have {have_qty})"

        rect = pygame.Rect(panel_x, PANEL_Y + 32, 360, 64)
        can_apply = have_qty >= 1
        border_color = (140, 220, 160) if can_apply else (100, 100, 100)
        self.renderer.draw_rect(screen, rect, (30, 30, 35))
        self.renderer.draw_rect(screen, rect, border_color, fill=False)
        self.renderer.draw_text(screen, kit_name, (rect.x + 10, rect.y + 8), color=COLOR_WHITE)
        self.renderer.draw_text(
            screen,
            effect_line,
            (rect.x + 10, rect.y + 32), size="small", color=COLOR_LIGHT_GRAY)
        self.upgrade_kit_button_rects.append((kit_id, rect))

        self._draw_upgrade_message(screen)

    def _draw_upgrade_message(self, screen):
        if self.upgrade_message:
            self.renderer.draw_text(screen, self.upgrade_message, (PANEL_X, SCREEN_HEIGHT - 60), color=self.upgrade_message_color)

    def _render_profession_bar(self, screen, prof_key, label, current_skill, y):
        """One profession's row: label, current/cap numbers, and a real
        filled progress bar. Cap is the CUMULATIVE sum of every tier cap
        (see TIER_SKILL_CAPS - currently early=75 + mid=150 = 225 total),
        matching WoW's real staircase (75 -> 150 -> 225 -> 300) where
        each tier adds its own range on top of the last rather than
        replacing it. A flat 'always cap at 75' was correct back when
        only Early tier existed, but silently broke the moment Mid-tier
        materials (Silver, Iron, Briarthorn) started letting skill climb
        past 75 - without this fix the bar would show 150/75, overflowing
        past its own border. No per-character tier-unlock tracking exists
        yet, so this assumes every tier whose materials exist is
        available to fill toward - accurate today (nothing gates a
        player from smelting Silver once they hit the skill), revisit if
        tier access ever becomes a real gate."""
        cap = sum(TIER_SKILL_CAPS.values())
        display_current = min(current_skill, cap)

        self.renderer.draw_text(screen, f"{label}  ({display_current} / {cap})",
                                (PANEL_X, y), color=COLOR_WHITE)

        bar_y = y + 26
        bar_rect = pygame.Rect(PANEL_X, bar_y, PANEL_WIDTH, BAR_HEIGHT)
        self.renderer.draw_rect(screen, bar_rect, (35, 35, 40))

        if cap > 0:
            fill_ratio = min(1.0, display_current / cap)
            fill_width = int(PANEL_WIDTH * fill_ratio)
            if fill_width > 0:
                fill_rect = pygame.Rect(PANEL_X, bar_y, fill_width, BAR_HEIGHT)
                # Maxed-out professions read as gold (matches the rest of
                # the UI's "gold = complete/important" convention -
                # COLOR_GOLD is used for titles/headers throughout), still-
                # progressing ones as the same teal the overworld tab
                # column already uses, so this bar reads as consistent
                # with the rest of the game's palette rather than
                # inventing a new color language just for this screen.
                fill_color = COLOR_GOLD if display_current >= cap else (30, 130, 150)
                self.renderer.draw_rect(screen, fill_rect, fill_color)

        self.renderer.draw_rect(screen, bar_rect, (100, 100, 100), fill=False)
