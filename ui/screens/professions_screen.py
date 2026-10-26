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
from world.crafting_manager import get_crafting_manager
from world.sawmill_manager import get_sawmill_manager
from world import profession_manager
from world.upgrade_manager import get_kit_for_item, can_upgrade, upgrade_item, next_rarity_for, MAX_UPGRADE_COUNT
from world.attachment_manager import (ATTACHMENTS, is_attachable, attachments_for_item,
                                      attach, attachment_label)


#: Display order and label for each known gathering profession. A
#: profession not in this list still shows if the character has it in
#: profession_skills (falls back to its raw dict key, title-cased) - this
#: list only controls ordering/labeling for the ones Phase 1 knows about,
#: it's not a hard whitelist that could hide a real profession.
PROFESSION_DISPLAY_ORDER = [
    ("herbalism", "Herbalism"),
    ("mining", "Mining"),
    ("woodcutting", "Woodcutting"),
    ("blacksmithing", "Blacksmithing"),
    ("alchemy", "Alchemy"),
    ("tailoring", "Tailoring"),
    ("woodworking", "Woodworking"),
]

#: Crafting tabs that share one generic recipe-list renderer: tab key -> (profession, label, needs station).
CRAFT_TABS = {
    "sawmill": ("woodcutting", "Sawmill", "sawmill"),
    "blacksmithing": ("blacksmithing", "Blacksmithing", None),
    "alchemy": ("alchemy", "Alchemy", None),
    "tailoring": ("tailoring", "Tailoring", None),
    "woodworking": ("woodworking", "Woodworking", None),
}

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
        #: tab key -> Rect; rebuilt every render from what the character has learned (see _tab_list)
        self.tab_rects = {}
        # Upgrade tab is deliberately NOT tied to one profession (Kyle, Oct 2026: "This will be for every crafting thing
        # too") - it scans the whole bag for crafted, kit-eligible items.
        self.craft_scroll = 0
        self.crafting_manager = get_crafting_manager()
        self.sawmill_manager = get_sawmill_manager()

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
        #: One rect per weapon ATTACHMENT that fits the selected item (scopes,
        #: limbs). Separate list from the kit rects because the two are
        #: different systems with different rules - see
        #: world/attachment_manager.py's header - and a weapon can legitimately
        #: offer both at once.
        self.attachment_button_rects = []
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
        if event.type == pygame.MOUSEWHEEL and self.active_tab in CRAFT_TABS:
            self.craft_scroll = max(0, self.craft_scroll - event.y * 2)
            return
        if event.type == pygame.KEYDOWN and self.active_tab in CRAFT_TABS:
            if event.key == pygame.K_DOWN:
                self.craft_scroll += 1
            elif event.key == pygame.K_UP:
                self.craft_scroll = max(0, self.craft_scroll - 1)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.close_button.collidepoint(event.pos):
                self._close()
                return
            for key, rect in self.tab_rects.items():
                if rect.collidepoint(event.pos):
                    self.active_tab = key
                    self.craft_scroll = 0
                    if key == "upgrade":
                        self.selected_upgrade_item = None
                    return
            if self.active_tab == "smelting":
                for i, rect in enumerate(self.recipe_rects):
                    if rect.collidepoint(event.pos):
                        self._attempt_smelt(i)
                        return
            if self.active_tab in CRAFT_TABS:
                for recipe_id, rect in self.craft_recipe_rects:
                    if rect.collidepoint(event.pos):
                        self._attempt_craft(recipe_id)
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
                for attach_id, rect in self.attachment_button_rects:
                    if rect.collidepoint(event.pos):
                        self._attempt_attach(attach_id)
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

    def _at_sawmill(self):
        zone_manager = getattr(self.state_manager.states.get(GameState.OVERWORLD), "zone_manager", None)
        return zone_manager is not None and zone_manager.get_sawmill_at_location() is not None

    def _attempt_craft(self, recipe_id):
        """Craft one recipe on the active generic crafting tab. Always the PLAYER's own materials and skill (same
        reasoning as _attempt_smelt). Blacksmithing keeps its own manager; everything else goes through CraftingManager."""
        player = self.state_manager.player
        profession, _, station = CRAFT_TABS[self.active_tab]
        if profession == "blacksmithing":
            if not player.knows_profession("blacksmithing"):
                ok, msg = False, "You haven't learned Blacksmithing."
            else:
                result = self.blacksmithing_manager.craft(player, recipe_id)
                if result is not None:
                    ok, msg = True, f"Crafted {result.name}."
                elif len(player.inventory) >= player.inventory_capacity:
                    ok, msg = False, "Your bags are full."
                else:
                    ok, msg = False, "Missing materials for that recipe."
        else:
            ok, msg, _ = self.crafting_manager.craft(player, profession, recipe_id,
                                                     at_station=(station != "sawmill" or self._at_sawmill()))
        self.craft_message = msg
        self.craft_message_color = (140, 220, 160) if ok else (240, 140, 140)
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
                self.upgrade_message = f"{result.name} is now {result.rarity.title()}!"
            else:
                self.upgrade_message = f"{result.name}: stats boosted again."
            self.upgrade_message_color = (140, 220, 160)
            self.upgrade_message_timer = 3.0
            # The item may no longer be eligible for ANY kit (if it just
            # hit upgrade_count == 2, it's permanently done) - clear the
            # selection rather than leaving a stale reference pointing at
            # an item that might not even still list a kit button under
            # it next render.
            self.selected_upgrade_item = None

    def _attempt_attach(self, attachment_id):
        """Fit a weapon attachment to the selected item.

        Same division of responsibility as _attempt_upgrade: attach() re-runs
        its own eligibility checks, so this only turns the result into a
        message. The selection is cleared on success because an attachment is
        permanent and single - the weapon has nothing left to offer, and a
        stale selection would keep rendering buttons attach() would refuse.
        """
        player = self.state_manager.player
        item = self.selected_upgrade_item
        if item is None:
            return
        result = attach(player, item, attachment_id)
        if result is None:
            self.upgrade_message = "That doesn't fit this weapon."
            self.upgrade_message_color = (240, 140, 140)
        else:
            self.upgrade_message = f"{attachment_label(result)} fitted to {result.name}."
            self.upgrade_message_color = (140, 220, 160)
            self.selected_upgrade_item = None
        self.upgrade_message_timer = 3.0

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

    def _tab_list(self):
        """[(key, label)] - Overview, then one tab per learned crafting profession (plus Smelting / Sawmill for the
        gathering professions that have a station), then Upgrade."""
        player = self.state_manager.player
        tabs = [("overview", "Overview")]
        if player.knows_profession("mining") or self.active_tab == "smelting":
            tabs.append(("smelting", "Smelting"))
        if player.knows_profession("woodcutting") or self.active_tab == "sawmill":
            tabs.append(("sawmill", "Sawmill"))
        for key in ("blacksmithing", "alchemy", "tailoring", "woodworking"):
            if player.knows_profession(key):
                tabs.append((key, CRAFT_TABS[key][1]))
        tabs.append(("upgrade", "Upgrade"))
        return tabs

    def render(self, screen):
        subject = self._get_subject()

        player = self.state_manager.player
        tabs = self._tab_list()
        if self.active_tab not in {k for k, _ in tabs}:
            self.active_tab = "overview"
        base_title = {"overview": "PROFESSIONS", "smelting": "SMELTING", "upgrade": "UPGRADE GEAR"}.get(
            self.active_tab, (CRAFT_TABS.get(self.active_tab, ("", "PROFESSIONS"))[1]).upper())
        if subject is player:
            title = base_title
        else:
            title = f"{subject.name.upper()}'S {base_title}"
        self.renderer.draw_text(screen, title, (20, 20), size="large", color=COLOR_GOLD)

        # ---- Sub-tab buttons - right-aligned left of the Close button, sized to their label ----
        self.tab_rects = {}
        x = SCREEN_WIDTH - 140
        for key, label in reversed(tabs):
            w = max(80, 22 + 9 * len(label))
            x -= w + 6
            self.tab_rects[key] = pygame.Rect(x, 20, w, 36)
        for key, label in tabs:
            rect = self.tab_rects[key]
            color = COLOR_GOLD if self.active_tab == key else (90, 90, 95)
            self.renderer.draw_rect(screen, rect, (35, 35, 40))
            self.renderer.draw_rect(screen, rect, color, fill=False)
            self.renderer.draw_text(screen, label, (rect.x + 11, rect.y + 9), color=color)

        if self.active_tab == "smelting":
            self._render_smelting_tab(screen)
        elif self.active_tab in CRAFT_TABS:
            self._render_craft_tab(screen)
        elif self.active_tab == "upgrade":
            self._render_upgrade_tab(screen)
        else:
            self._render_overview_tab(screen, subject)
        self.renderer.draw_button(screen, self.close_button, "Close")

    def _render_overview_tab(self, screen, subject):
        skills = subject.profession_skills or {}
        known = list(getattr(subject, "known_professions", []))
        slots = getattr(subject, "MAX_PRIMARY_PROFESSIONS", 3)
        self.renderer.draw_text(screen, f"Professions known: {len(known)} / {slots}", (PANEL_X, 54), color=(180, 180, 190))

        if not known:
            self.renderer.draw_text(screen, "No professions learned yet. Every town has trainers - look for the profession icon on the map.",
                                    (PANEL_X, PANEL_Y + 10), color=(150, 150, 150))
            return

        labels = dict(PROFESSION_DISPLAY_ORDER)
        ordered = [(k, labels[k]) for k, _ in PROFESSION_DISPLAY_ORDER if k in known]
        ordered += [(k, k.title()) for k in known if k not in labels]
        y = PANEL_Y + 10
        for prof_key, label in ordered:
            self._render_profession_bar(screen, prof_key, label, skills.get(prof_key, 0), y, subject)
            y += BAR_GAP
        y += 10
        self.renderer.draw_text(screen, "Recipes are in the tabs above. Smelting needs a Forge, Sawmill recipes need a Sawmill.",
                                (PANEL_X, y), size="small", color=(150, 150, 150))

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

        if not player.knows_profession("mining"):
            self.renderer.draw_text(screen, "You haven't learned Mining. Find a Mining trainer in any town.",
                                    (PANEL_X, PANEL_Y + 40), color=(220, 160, 120))
            self._draw_smelt_message(screen)
            return
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

    def _craft_recipes(self, profession):
        if profession == "blacksmithing":
            recipes = self.blacksmithing_manager.recipes
        else:
            recipes = self.crafting_manager.all_recipes(profession)
        return sorted(recipes.items(), key=lambda kv: kv[1].get("skill_required", 0))

    def _material_icon(self, material_id):
        mat_def = self.gathering_manager.get_material_def(material_id)
        if not mat_def or not mat_def.get("icon_id"):
            return None
        folder = MATERIAL_TYPE_FOLDERS.get(mat_def["material_type"], mat_def["material_type"])
        return get_tile_sprite(f"assets/gathering_nodes/{folder}/{mat_def['icon_id']}.png", (0, 0, 32, 32), 40)

    @staticmethod
    def _difficulty_color(skill, recipe):
        """WoW's recipe colours: orange = always skills up, yellow = usually, green = sometimes, grey = never."""
        req = recipe.get("skill_required", 0)
        orange, yellow, green, grey = recipe.get("skill_range") or (req + 5, req + 15, req + 25, req + 35)
        if skill < orange:
            return (255, 150, 40)
        if skill < yellow:
            return (235, 215, 70)
        if skill < green:
            return (110, 205, 110)
        return (130, 130, 135)

    def _render_craft_tab(self, screen):
        """One scrolling recipe list for Blacksmithing / Alchemy / Tailoring / Woodworking / the Sawmill. Every recipe is
        listed (locked ones greyed with the skill they need) so the player can see what they are working toward."""
        player = self.state_manager.player
        profession, label, station = CRAFT_TABS[self.active_tab]
        self.craft_recipe_rects = []

        if not player.knows_profession(profession):
            self.renderer.draw_text(screen, f"You haven't learned {label}. Find a {label} trainer in any town.",
                                    (PANEL_X, PANEL_Y), color=(220, 160, 120))
            self._draw_craft_message(screen)
            return

        skill = player.profession_skills.get(profession, 0)
        cap = player.profession_cap(profession)
        tier = profession_manager.tier_name(player.profession_tiers.get(profession, 0))
        self.renderer.draw_text(screen, f"{tier} {label if profession != 'woodcutting' else 'Woodcutting'}:  skill {skill} / {cap}",
                                (PANEL_X, PANEL_Y), color=COLOR_WHITE)
        y = PANEL_Y + 30
        if station == "sawmill":
            if self._at_sawmill():
                self.renderer.draw_text(screen, "At a Sawmill - ready to saw.", (PANEL_X, y), color=(140, 220, 160))
            else:
                self.renderer.draw_text(screen, "You are not at a Sawmill. Find one to saw planks.", (PANEL_X, y), color=(220, 160, 120))
            y += 30
        elif skill >= cap and cap < 300:
            self.renderer.draw_text(screen, f"Skill cap reached - visit a {label} trainer to advance.", (PANEL_X, y), color=(220, 190, 120))
            y += 30

        recipes = self._craft_recipes(profession)
        row_h = 52
        visible = max(1, (SCREEN_HEIGHT - 80 - y) // row_h)
        self.craft_scroll = max(0, min(self.craft_scroll, max(0, len(recipes) - visible)))
        if len(recipes) > visible:
            self.renderer.draw_text(screen, f"Scroll for more ({self.craft_scroll + 1}-{min(len(recipes), self.craft_scroll + visible)} of {len(recipes)})",
                                    (SCREEN_WIDTH - 520, PANEL_Y), size="small", color=(150, 150, 150))

        for recipe_id, recipe in recipes[self.craft_scroll:self.craft_scroll + visible]:
            rect = pygame.Rect(PANEL_X, y, PANEL_WIDTH, row_h - 6)
            req = recipe.get("skill_required", 0)
            unlocked = skill >= req
            if profession == "blacksmithing":
                can_craft = self.blacksmithing_manager.can_craft(player, recipe_id)
                name = recipe["name"]
            else:
                can_craft = self.crafting_manager.can_craft(player, profession, recipe_id)
                name = self.crafting_manager.output_name(recipe)
            border = (140, 220, 160) if can_craft else ((100, 100, 100) if unlocked else (60, 60, 65))
            self.renderer.draw_rect(screen, rect, (30, 30, 35) if unlocked else (22, 22, 26))
            self.renderer.draw_rect(screen, rect, border, fill=False)

            out = recipe.get("output", {})
            sprite = self._material_icon(out.get("material_id")) if out.get("kind") == "material" else None
            if sprite is None:
                first_input = next(iter(recipe["inputs"]), None)
                sprite = self._material_icon(first_input) if first_input else None
            if sprite is not None:
                screen.blit(sprite, (rect.x + 6, rect.y + 2))
            text_x = rect.x + (54 if sprite is not None else 12)

            parts = []
            for input_id, qty in recipe["inputs"].items():
                mat_def = self.gathering_manager.get_material_def(input_id)
                parts.append(f"{mat_def['name'] if mat_def else input_id} {player.get_material_quantity(input_id)}/{qty}")
            self.renderer.draw_text(screen, name, (text_x, rect.y + 4), color=COLOR_WHITE if unlocked else (120, 120, 125))
            self.renderer.draw_text(screen, "   ".join(parts), (text_x, rect.y + 25), size="small", color=COLOR_LIGHT_GRAY if unlocked else (100, 100, 105))
            if unlocked:
                self.renderer.draw_text(screen, f"Skill {req}", (rect.right - 110, rect.y + 12), color=self._difficulty_color(skill, recipe))
            else:
                self.renderer.draw_text(screen, f"Requires {req}", (rect.right - 130, rect.y + 12), color=(200, 110, 110))
            self.craft_recipe_rects.append((recipe_id, rect))
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
        self.attachment_button_rects = []

        # Two independent reasons an item can appear here, so the tab is one
        # place for "permanently improve this item" rather than two:
        #   - a crafted piece with an upgrade kit still available, or
        #   - a ranged weapon that can still take an attachment (which does
        #     NOT require is_crafted - a scope goes on a dropped rifle too).
        eligible = [item for item in player.inventory
                    if (getattr(item, "is_crafted", False) and get_kit_for_item(item) is not None)
                    or (is_attachable(item) and attachments_for_item(item))]

        if not eligible:
            self.renderer.draw_text(
                screen,
                "Nothing in your bags can be improved right now.",
                (PANEL_X, PANEL_Y), color=(150, 150, 150))
            self.renderer.draw_text(
                screen,
                "Crafted gear takes upgrade kits; guns, bows and crossbows take scopes and limbs.",
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
            status = f"{item.rarity.title()}"
            if getattr(item, "is_crafted", False):
                status += f"   ({item.upgrade_count}/{MAX_UPGRADE_COUNT} upgrades used)"
            if is_attachable(item):
                fitted = attachment_label(item)
                status += f"   [{fitted}]" if fitted else "   [no attachment]"
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
        kit_id = get_kit_for_item(item) if getattr(item, "is_crafted", False) else None
        fits = attachments_for_item(item)
        next_y = PANEL_Y + 32

        if kit_id is None and fits:
            # Attachment-only item (a dropped rifle, or a crafted one whose
            # kits are spent). Skip the kit panel entirely rather than showing
            # the "fully upgraded" dead end, which would be misleading when
            # there IS still something to fit.
            self._draw_attachment_buttons(screen, player, item, panel_x, next_y, fits)
            self._draw_upgrade_message(screen)
            return

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
            effect_line = f"{item.rarity.title()} -> {to_rarity.title()}, +10% stats, Refined   (have {have_qty})"
        else:
            effect_line = f"+20% stats, Superior, stays {item.rarity.title()}   (have {have_qty})"

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

        # A crafted gun can take BOTH a kit and a scope, so the attachments
        # render under the kit rather than instead of it.
        if fits:
            self._draw_attachment_buttons(screen, player, item, panel_x, rect.bottom + 16, fits)

        self._draw_upgrade_message(screen)

    def _draw_attachment_buttons(self, screen, player, item, panel_x, y, fits):
        """One button per attachment that fits this weapon.

        Unlike upgrade kits - where get_kit_for_item returns at most one match,
        so there is never a choice - several attachments fit a given weapon
        type at once (a rifle accepts any of the four scopes). They are listed
        strongest-first so the obvious pick is at the top, with the ones the
        player does not hold greyed rather than hidden, so the line is visible
        as something to work toward.
        """
        self.renderer.draw_text(screen, "FIT ATTACHMENT", (panel_x, y), color=COLOR_GOLD)
        y += 30
        for aid in sorted(fits, key=lambda a: -ATTACHMENTS[a]["damage"]):
            spec = ATTACHMENTS[aid]
            have = player.get_material_quantity(aid)
            rect = pygame.Rect(panel_x, y, 360, 44)
            can = have >= 1
            self.renderer.draw_rect(screen, rect, (30, 30, 35))
            self.renderer.draw_rect(screen, rect, (140, 220, 160) if can else (100, 100, 100), fill=False)
            self.renderer.draw_text(screen, spec["name"], (rect.x + 10, rect.y + 5),
                                    color=COLOR_WHITE if can else (130, 130, 130))
            self.renderer.draw_text(
                screen, f"+{spec['damage']} weapon damage, permanent   (have {have})",
                (rect.x + 10, rect.y + 24), size="small", color=COLOR_LIGHT_GRAY)
            if can:
                self.attachment_button_rects.append((aid, rect))
            y += 50

    def _draw_upgrade_message(self, screen):
        if self.upgrade_message:
            self.renderer.draw_text(screen, self.upgrade_message, (PANEL_X, SCREEN_HEIGHT - 60), color=self.upgrade_message_color)

    def _render_profession_bar(self, screen, prof_key, label, current_skill, y, subject=None):
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
        # The bar fills toward the TRAINED tier's cap (Apprentice 75, Journeyman 150, ...), so a capped bar means
        # "visit your trainer", not "done".
        cap = subject.profession_cap(prof_key) if subject is not None else sum(TIER_SKILL_CAPS.values())
        tier = profession_manager.tier_name(subject.profession_tiers.get(prof_key, 0)) if subject is not None else ""
        display_current = min(current_skill, cap)

        self.renderer.draw_text(screen, f"{label}  -  {tier}  ({display_current} / {cap})",
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
