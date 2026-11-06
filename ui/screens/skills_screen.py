"""
Skills screen - browse and slot abilities to hotbar.
UPDATED WITH ICON SYSTEM INTEGRATION

Has a **subject** - the character whose ability list/hotbar is shown -
same pattern as InventoryScreen.set_subject()/TalentTreeScreen.character:
defaults to the player, but PartyScreen's "Skills" button can point it at
a companion. Every companion Character already has its own independent
ability_book and hotbar (see entities/character.py __init__), so unlike
InventoryScreen there's no shared-bag complication here - a companion's
loadout is entirely their own, nothing routes back through the player.
"""
import pygame
from core.game_states import GameState
from ui.screens.base_screen import BaseScreen
from ui.renderer import Renderer
from entities.consumable import Consumable
from config import SCREEN_WIDTH, SCREEN_HEIGHT


class SkillsScreen(BaseScreen):
    """Screen for managing abilities and consumables in hotbar."""
    
    def __init__(self, state_manager, icon_ui_helper=None):
        super().__init__(state_manager)
        # BaseScreen stores this as self.state_manager. This class referenced
        # self.game_state_manager throughout, which never existed - opening
        # the Skills tab raised AttributeError on the first render. Aliased
        # rather than renamed everywhere so both spellings keep working.
        self.game_state_manager = state_manager
        self.renderer = Renderer()
        
        # Icon system integration
        self.icon_ui_helper = icon_ui_helper
        
        # UI state
        self.selected_ability = None
        self.selected_slot = None
        self.scroll_offset = 0

        # Real hover-tooltip state (same shared Ability.get_tooltip_lines
        # backend cast_screen.py/combat_screen.py use). Consumables don't
        # have get_tooltip_lines, so hover only tracks real Abilities.
        self.hovered_ability = None
        self.mouse_pos = (0, 0)

        # Whose abilities/hotbar we're editing, and where ESC/close returns
        # to. Set via set_subject(); reset to the player whenever opened
        # from the overworld or CharacterSheetScreen so you never land on a
        # companion's hotbar by accident.
        self.subject = None
        self.return_state = GameState.CHARACTER_SHEET

        # Real spellbook tabs (Kyle's ask: replace the flat list with real
        # Core + per-tree tabs, matching real WoW's General/Fire/Frost/
        # Arcane split). "core" is always the first tab (baseline
        # abilities, no requires_talent flag); one additional tab per
        # talent tree the subject actually has, built from the real
        # ability<->tree link talent data already carries (each tree
        # node's "unlock_ability" key - see _build_tabs). active_tab is a
        # tree_id string, or the literal "core".
        self.active_tab = "core"
        self._tab_rects = []
        
        # Layout
        self.ABILITY_LIST_X = 20
        self.ABILITY_LIST_Y = 80
        self.ABILITY_LIST_WIDTH = 420  # Wider to accommodate icons
        self.ABILITY_LIST_HEIGHT = 500
        
        self.HOTBAR_PANEL_X = 470
        self.HOTBAR_PANEL_Y = 80
        self.HOTBAR_PANEL_WIDTH = 750
        self.HOTBAR_PANEL_HEIGHT = 560  # grown to fit the extra-slots block below the main 20-slot grid
        
        self.SLOT_HEIGHT = 50  # Taller to show icons
        self.VISIBLE_ABILITIES = 10
        self.ABILITY_ICON_SIZE = 36
        self.HOTBAR_ICON_SIZE = 64

    def set_subject(self, character, return_state=None):
        """Point the screen at a character (party screen uses this)."""
        self.subject = character
        self.selected_ability = None
        self.selected_slot = None
        self.scroll_offset = 0
        self.active_tab = "core"
        if return_state is not None:
            self.return_state = return_state

    def _get_subject(self):
        """The character whose abilities/hotbar are being edited - the
        player unless PartyScreen pointed this at a companion."""
        return self.subject or self.game_state_manager.player
    
    def _learned_abilities(self, player):
        """Only abilities the character has actually reached the level
        requirement for.

        This screen previously listed ability_book.get_all_abilities(), which
        includes every ability in the class kit regardless of level - so a
        level 1 character saw (and could slot) their level 30 and level 38
        abilities. Character.get_learned_abilities() is the same filter the
        hotbar autofill uses, so the two can't disagree.
        """
        if hasattr(player, "get_learned_abilities"):
            return player.get_learned_abilities()
        return player.ability_book.get_all_abilities()

    def _resolve_ability_tab(self, player, ability, unlock_map):
        """Real tab this ability belongs in for the spellbook - per Kyle:
        every combat spell belongs to its real tree identity, not a
        generic bucket. Resolution order, all from real data:
          1. requires_talent abilities: unlock_map (built once per
             render from the subject's actual talent_trees - each tree
             node's real "unlock_ability" key, the same field the talent
             screen itself uses to grant the ability) tells us exactly
             which tree unlocked this ability_id.
          2. spellbook_tree_map.get_owning_tree(): the real per-class
             school-to-tree table for baseline schooled spells (Frostbolt
             -> Frost even though every Mage starts with it).
          3. "core": no tree owns it - a genuine passive/profession/
             racial (Kyle's real definition of Core), or a physical
             ability with no single confirmed tree owner (e.g. Rupture -
             see spellbook_tree_map.PHYSICAL_TREE_OVERRIDES' comment).
        Returns a tree_id string, or "core".
        """
        if getattr(ability, "requires_talent", False):
            tree_id = unlock_map.get(ability.ability_id)
            if tree_id:
                return tree_id

        from ui.spellbook_tree_map import get_owning_tree
        tree_id = get_owning_tree(player.char_class, ability)
        return tree_id or "core"

    def _build_tabs(self, player):
        """Real {tab_key: [abilities]} grouping for the subject's whole
        learned kit, plus an ordered list of (tab_key, display_label)
        pairs for the tab bar itself. "core" is always first; remaining
        tabs are the subject's real talent trees, in the order
        talent_trees.values() naturally gives (insertion order from
        TalentManager - matches the same order the talent screen itself
        lists a class's trees in, so tab order and talent-tree order
        stay consistent for the player).
        """
        # unlock_map: ability_id -> tree_id, built from every tree's
        # real node data. A node's "unlock_ability" field IS the
        # authoritative link (same field Character._sync_talent_unlocked_
        # abilities already reads to grant the ability in the first
        # place) - not inferred, not guessed.
        unlock_map = {}
        for tree_id, tree in getattr(player, "talent_trees", {}).items():
            for node in tree.nodes.values():
                unlock_id = node.effects.get("unlock_ability") if node.effects else None
                if unlock_id:
                    unlock_map[unlock_id] = tree_id

        groups = {"core": []}
        tab_order = [("core", "Core")]
        seen_trees = set()

        for ability in self._learned_abilities(player):
            tab_key = self._resolve_ability_tab(player, ability, unlock_map)
            if tab_key not in groups:
                groups[tab_key] = []
                tree = player.talent_trees.get(tab_key)
                label = tree.spec_name if tree else tab_key
                # Trim the redundant class-name prefix real spec_name
                # values carry ("Mage Fire" -> "Fire") since the tab bar
                # already lives inside this specific character's
                # spellbook - repeating "Mage" on every tab is noise a
                # real WoW spellbook doesn't have either (its tabs just
                # say "Fire", "Frost", "Arcane").
                from core.class_names import strip_class_prefix
                label = strip_class_prefix(label, player.char_class)
                tab_order.append((tab_key, label))
                seen_trees.add(tab_key)
            groups[tab_key].append(ability)

        return groups, tab_order

    def _visible_abilities(self, player):
        """Real tab-filtered ability list for the active tab - the single
        source both render() and handle_event()'s click logic read, so
        clicking a row always slots the ability actually shown there, not
        a stale unfiltered index (see _build_tabs' docstring for why a
        flat list can't be used any more now that every real spell has a
        real tree home)."""
        groups, _ = self._build_tabs(player)
        return groups.get(self.active_tab, [])

    def _centered(self, text, center_x, y, size="normal"):
        """Approximate horizontal centring.

        Renderer.draw_text() takes a top-left position and has no center
        flag, but this screen was written as though it did (it passed
        center=True and a font_size kwarg, neither of which exist). Rather
        than change the shared Renderer API used by every other screen, this
        measures the string with the right font and returns a shifted
        top-left position.
        """
        font = (self.renderer.font_large if size == "large"
                else self.renderer.font_normal)
        return (center_x - font.size(text)[0] // 2, y)

    def _close(self):
        """Return where we came from, and always release the subject -
        same reasoning as InventoryScreen._close(): otherwise opening
        Skills from the overworld could still be pointed at whatever
        companion PartyScreen last sent it to."""
        destination = self.return_state or GameState.CHARACTER_SHEET
        self.subject = None
        self.return_state = GameState.CHARACTER_SHEET
        self.game_state_manager.transition_to(destination)

    #: Hotbar grid geometry, in one place. These used to be open-coded at
    #: three call sites and two of them disagreed: render() drew slots at
    #: PANEL_Y + 50 + row*85 while both hit-tests looked for them at
    #: PANEL_Y + 60 + row*85. Every slot therefore had a 10px dead strip
    #: along its top and a 10px phantom strip under it, which reads as
    #: "the hotbar sometimes ignores me" rather than as an off-by-ten.
    #:
    #: ROW_PITCH is 90, not 85, because a 64px slot at an 85px pitch
    #: leaves 21px between rows and the "Row 2 (Press Shift+1-0):" label
    #: needs ~18 of them - it was being drawn at PANEL_Y + 110, four
    #: pixels INSIDE row 1's slots, which is the text overlap.
    SLOT_PX = 64
    COL_PITCH = 70
    ROW_PITCH = 95
    ROW0_TOP = 50          # first slot row, relative to HOTBAR_PANEL_Y
    LABEL_GAP = 24         # label sits this far above its row of slots

    def _hotbar_slot_rect(self, index):
        """Rect for hotbar slot `index` (0-19). The single source of truth
        for both drawing and hit-testing - see the note above."""
        row, col = divmod(index, 10)
        return pygame.Rect(
            self.HOTBAR_PANEL_X + 20 + col * self.COL_PITCH,
            self.HOTBAR_PANEL_Y + self.ROW0_TOP + row * self.ROW_PITCH,
            self.SLOT_PX, self.SLOT_PX)

    def _hotbar_label_y(self, row):
        """Baseline for a row's keybind caption, clear of the slots above."""
        return (self.HOTBAR_PANEL_Y + self.ROW0_TOP
                + row * self.ROW_PITCH - self.LABEL_GAP)

    def _extra_slot_rects(self):
        """Rects for the 8 click-only extra ability slots, laid out as 2
        rows x 4 cols below the real 20-slot hotbar grid - same panel,
        same slot size, just a visually separated block since these have
        no keybind (see Character.extra_slots)."""
        rects = []
        base_y = (self.HOTBAR_PANEL_Y + self.ROW0_TOP
                  + 2 * self.ROW_PITCH + 40)  # below both hotbar rows + gap
        for i in range(8):
            row = i // 4
            col = i % 4
            slot_x = self.HOTBAR_PANEL_X + 20 + col * self.COL_PITCH
            slot_y = base_y + row * self.ROW_PITCH
            rects.append(pygame.Rect(slot_x, slot_y, self.SLOT_PX, self.SLOT_PX))
        return rects

    def handle_event(self, event):
        """Handle input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._close()
                return
        
        elif event.type == pygame.MOUSEWHEEL:
            # scroll_offset existed but nothing ever modified it, so with kits
            # now 8-9 abilities long the list could exceed VISIBLE_ABILITIES
            # with no way to reach the rest. Clamped so you can't scroll past
            # the end or above the start. Uses the real tab-filtered count,
            # not the whole class's kit, since scrolling only ever moves
            # through what's actually visible under the active tab.
            player = self._get_subject()
            max_offset = max(0, len(self._visible_abilities(player)) - self.VISIBLE_ABILITIES)
            self.scroll_offset = max(0, min(max_offset, self.scroll_offset - event.y))
            return

        elif event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            self.mouse_pos = event.pos
            self.hovered_ability = None
            player = self._get_subject()

            # Check the ability list rows first - real tab-filtered list,
            # not the whole kit (see _visible_abilities' docstring).
            visible_abilities = self._visible_abilities(player)[
                self.scroll_offset:self.scroll_offset + self.VISIBLE_ABILITIES]
            for i, ability in enumerate(visible_abilities):
                slot_y = self.ABILITY_LIST_Y + i * self.SLOT_HEIGHT
                slot_rect = pygame.Rect(self.ABILITY_LIST_X, slot_y, self.ABILITY_LIST_WIDTH, self.SLOT_HEIGHT)
                if slot_rect.collidepoint(mouse_x, mouse_y):
                    self.hovered_ability = ability
                    return

            # Then the hotbar slots - real Ability lookup by id, skipping
            # Consumable entries (no get_tooltip_lines to show).
            for i in range(20):
                slot_rect = self._hotbar_slot_rect(i)
                if slot_rect.collidepoint(mouse_x, mouse_y):
                    content = player.hotbar[i]
                    if content and not isinstance(content, Consumable):
                        self.hovered_ability = player.ability_book.get_ability(content)
                    return

            # Then the extra (click-only) slots, same tooltip treatment.
            for i, slot_rect in enumerate(self._extra_slot_rects()):
                if slot_rect.collidepoint(mouse_x, mouse_y):
                    content = player.extra_slots[i] if i < len(player.extra_slots) else None
                    if content and not isinstance(content, Consumable):
                        self.hovered_ability = player.ability_book.get_ability(content)
                    return
            return

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Only left (1) and right (3) clicks act.  pygame also reports the scroll wheel as buttons
            # 4/5; those used to fall through and wipe whichever hotbar slot the cursor was resting on.
            if event.button not in (1, 3):
                return
            mouse_x, mouse_y = pygame.mouse.get_pos()
            player = self._get_subject()
            right_click = event.button == 3

            # Click a tab - switches active_tab and resets scroll, since a
            # scroll position from a longer tab's list could otherwise land
            # you scrolled past the end of a shorter one.
            for tab_key, rect in self._tab_rects:
                if rect.collidepoint(mouse_x, mouse_y):
                    self.active_tab = tab_key
                    self.scroll_offset = 0
                    self.selected_ability = None
                    return

            # Click ability in list - real tab-filtered list, not the
            # whole kit (see _visible_abilities' docstring).
            for i, ability in enumerate(self._visible_abilities(player)[self.scroll_offset:self.scroll_offset + self.VISIBLE_ABILITIES]):
                slot_y = self.ABILITY_LIST_Y + i * self.SLOT_HEIGHT
                slot_rect = pygame.Rect(self.ABILITY_LIST_X, slot_y, self.ABILITY_LIST_WIDTH, self.SLOT_HEIGHT)
                if slot_rect.collidepoint(mouse_x, mouse_y):
                    self.selected_ability = ability
                    self.selected_slot = None
                    return
            
            # Click consumable in list. Consumables are per-character now
            # (each Character has always had their own self.consumables -
            # this screen just needed to stop hardcoding it to the real
            # player's list). A companion's own potions/food show and slot
            # here, same as their abilities. Consumables only appear under
            # the Core tab (they're not spec content any real spell tab
            # should repeat) - see the matching render-side rule in
            # render().
            if self.active_tab == "core":
                consumables_start_y = self.ABILITY_LIST_Y + len(self._visible_abilities(player)) * self.SLOT_HEIGHT
                for i, consumable in enumerate(player.consumables):
                    slot_y = consumables_start_y + i * self.SLOT_HEIGHT
                    if slot_y > self.ABILITY_LIST_Y + self.ABILITY_LIST_HEIGHT - self.SLOT_HEIGHT:
                        break
                    slot_rect = pygame.Rect(self.ABILITY_LIST_X, slot_y, self.ABILITY_LIST_WIDTH, self.SLOT_HEIGHT)
                    if slot_rect.collidepoint(mouse_x, mouse_y):
                        self.selected_ability = consumable
                        self.selected_slot = None
                        return
            
            # Click hotbar slot
            for i in range(20):
                slot_rect = self._hotbar_slot_rect(i)
                
                if slot_rect.collidepoint(mouse_x, mouse_y):
                    if right_click:
                        player.hotbar[i] = None       # right-click always clears
                        self.selected_ability = None
                    elif self.selected_ability:
                        # Slot the ability/consumable
                        if isinstance(self.selected_ability, Consumable):
                            player.hotbar[i] = self.selected_ability
                        else:
                            player.hotbar[i] = self.selected_ability.ability_id
                        self.selected_ability = None
                    else:
                        # Clear the slot
                        player.hotbar[i] = None
                    return

            # Click extra (click-only) slot - same assign/clear flow as the
            # real hotbar, writes to player.extra_slots instead.
            for i, slot_rect in enumerate(self._extra_slot_rects()):
                if slot_rect.collidepoint(mouse_x, mouse_y):
                    if right_click:
                        player.extra_slots[i] = None
                        self.selected_ability = None
                    elif self.selected_ability:
                        if isinstance(self.selected_ability, Consumable):
                            player.extra_slots[i] = self.selected_ability
                        else:
                            player.extra_slots[i] = self.selected_ability.ability_id
                        self.selected_ability = None
                    else:
                        player.extra_slots[i] = None
                    return
    
    def update(self, dt):
        """Update logic."""
        pass
    
    def render(self, screen):
        """Render skills screen."""
        screen.fill((20, 20, 30))
        player = self._get_subject()
        groups, tab_order = self._build_tabs(player)
        abilities = groups.get(self.active_tab, [])
        real_player = self.game_state_manager.player

        # Title
        title = "Skills & Abilities" if player is real_player \
            else f"{player.name}'s Skills & Abilities"
        self.renderer.draw_text(
            screen, title,
            self._centered(title, 640, 24, size="large"),
            color=(200, 200, 100), size="large")

        # Real spellbook tabs (Kyle's ask: every real spell belongs to its
        # real school/tree, never a generic bucket - see spellbook_tree_map.
        # py and _build_tabs' docstring). Drawn above the ability list,
        # left-aligned to it so the tab row reads as owning that panel.
        self._tab_rects = []
        tab_x = self.ABILITY_LIST_X
        tab_y = self.ABILITY_LIST_Y - 60
        for tab_key, label in tab_order:
            tab_w = max(70, self.renderer.font_normal.size(label)[0] + 24)
            rect = pygame.Rect(tab_x, tab_y, tab_w, 28)
            is_active = tab_key == self.active_tab
            color = (70, 90, 130) if is_active else (40, 40, 50)
            text_color = (255, 230, 150) if is_active else (170, 170, 180)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (100, 100, 115), rect, 1)
            self.renderer.draw_text(screen, label,
                                    (rect.x + 12, rect.y + 6),
                                    font_size=14, color=text_color)
            self._tab_rects.append((tab_key, rect))
            tab_x += tab_w + 4

        # Left panel: available abilities & consumables
        pygame.draw.rect(screen, (50, 50, 60),
                         (self.ABILITY_LIST_X, self.ABILITY_LIST_Y,
                          self.ABILITY_LIST_WIDTH, self.ABILITY_LIST_HEIGHT), 2)

        # Show the scroll position so it is obvious when the list continues
        # past the visible window. Consumables only ever appear under Core
        # (see the render-side gate below and its click-handling twin), so
        # the header's total only includes them there too.
        consumable_count = len(player.consumables) if self.active_tab == "core" else 0
        total = len(abilities) + consumable_count
        header = f"Available ({total})"
        if len(abilities) > self.VISIBLE_ABILITIES:
            header += f"  [{self.scroll_offset + 1}-" \
                      f"{min(self.scroll_offset + self.VISIBLE_ABILITIES, len(abilities))}]"
        self.renderer.draw_text(
            screen, header,
            (self.ABILITY_LIST_X + 10, self.ABILITY_LIST_Y - 25),
            color=(200, 200, 100), size="large")

        visible = abilities[self.scroll_offset:self.scroll_offset + self.VISIBLE_ABILITIES]
        row = 0
        for ability in visible:
            slot_y = self.ABILITY_LIST_Y + row * self.SLOT_HEIGHT
            slot_rect = pygame.Rect(self.ABILITY_LIST_X, slot_y,
                                    self.ABILITY_LIST_WIDTH, self.SLOT_HEIGHT)
            
            # Highlight selected ability
            if self.selected_ability == ability:
                pygame.draw.rect(screen, (100, 150, 255), slot_rect, 2)
            else:
                pygame.draw.rect(screen, (50, 50, 60), slot_rect, 1)

            # Draw ability icon if icon system is available
            icon_x = self.ABILITY_LIST_X + 6
            icon_y = slot_y + 7
            
            if self.icon_ui_helper:
                try:
                    # Build ability data dict for icon lookup
                    ability_data = {
                        "ability_id": ability.ability_id,
                        "name": ability.name,
                        "icon_id": getattr(ability, "icon_id", None),
                        "effect_type": getattr(ability, "effect_type", "damage")
                    }
                    icon_surface = self.icon_ui_helper.get_ability_icon_surface(
                        ability_data, 
                        size=self.ABILITY_ICON_SIZE
                    )
                    if icon_surface:
                        screen.blit(icon_surface, (icon_x, icon_y))
                except Exception as e:
                    # Silently fail - game keeps running
                    pass
            
            # Draw ability name and rank info
            text_x = icon_x + self.ABILITY_ICON_SIZE + 12
            text_y = slot_y + 8
            
            self.renderer.draw_text(
                screen, f"{ability.name}",
                (text_x, text_y),
                color=(200, 200, 200))

            # Rank readout - useful now that abilities have up to 5 ranks.
            rank_label = f"Rank {ability.current_rank['rank']}/{ability.max_rank_number}"
            self.renderer.draw_text(
                screen, rank_label,
                (text_x, text_y + 18),
                color=(140, 140, 160))
            
            row += 1

        # List consumables below the abilities. Per-character now - the
        # subject's own consumables, same as their abilities/hotbar.
        # Only shown under Core (not real spec content - repeating them
        # under every school tab would be redundant/confusing, see the
        # matching click-handling gate in handle_event()).
        consumables_start_row = row
        for consumable in (player.consumables if self.active_tab == "core" else []):
            slot_y = self.ABILITY_LIST_Y + row * self.SLOT_HEIGHT
            if slot_y > self.ABILITY_LIST_Y + self.ABILITY_LIST_HEIGHT - self.SLOT_HEIGHT:
                break
            slot_rect = pygame.Rect(self.ABILITY_LIST_X, slot_y,
                                    self.ABILITY_LIST_WIDTH, self.SLOT_HEIGHT)
            
            # Highlight selected consumable
            if self.selected_ability == consumable:
                pygame.draw.rect(screen, (100, 150, 255), slot_rect, 2)
            else:
                pygame.draw.rect(screen, (50, 50, 60), slot_rect, 1)
            
            # Draw consumable icon if icon system is available
            icon_x = self.ABILITY_LIST_X + 6
            icon_y = slot_y + 7
            
            if self.icon_ui_helper:
                try:
                    consumable_data = {
                        "name": consumable.name,
                        "icon_id": getattr(consumable, "icon_id", None),
                    }
                    icon_surface = self.icon_ui_helper.get_item_icon_surface(
                        consumable_data,
                        size=self.ABILITY_ICON_SIZE
                    )
                    if icon_surface:
                        screen.blit(icon_surface, (icon_x, icon_y))
                except Exception as e:
                    # Silently fail - game keeps running
                    pass
            
            # Draw consumable name
            text_x = icon_x + self.ABILITY_ICON_SIZE + 12
            text_y = slot_y + 12
            
            self.renderer.draw_text(
                screen, f"{consumable.name} x{consumable.quantity}",
                (text_x, text_y),
                color=(200, 200, 200))
            
            row += 1

        # Right panel: hotbar grid
        pygame.draw.rect(screen, (50, 50, 60),
                         (self.HOTBAR_PANEL_X, self.HOTBAR_PANEL_Y,
                          self.HOTBAR_PANEL_WIDTH, self.HOTBAR_PANEL_HEIGHT), 2)
        self.renderer.draw_text(
            screen, "Hotbar (1-9,0 / Shift+1-9,0)",
            (self.HOTBAR_PANEL_X + 10, self.HOTBAR_PANEL_Y - 25),
            color=(200, 200, 100), size="large")
        self.renderer.draw_text(
            screen, "Row 1 (Press 1-0):",
            (self.HOTBAR_PANEL_X + 20, self._hotbar_label_y(0)),
            color=(150, 150, 150))
        self.renderer.draw_text(
            screen, "Row 2 (Press Shift+1-0):",
            (self.HOTBAR_PANEL_X + 20, self._hotbar_label_y(1)),
            color=(150, 150, 150))

        # Render hotbar slots with icons
        for i in range(20):
            slot_rect = self._hotbar_slot_rect(i)
            slot_x, slot_y = slot_rect.x, slot_rect.y

            hotbar_content = player.hotbar[i]
            
            if hotbar_content:
                if isinstance(hotbar_content, Consumable):
                    btn_color = (40, 60, 40)
                    label = hotbar_content.name
                    qty = f"x{hotbar_content.quantity}"
                    
                    # Draw consumable
                    pygame.draw.rect(screen, btn_color, slot_rect)
                    pygame.draw.rect(screen, (150, 200, 150), slot_rect, 2)
                    
                    # Draw icon if available
                    if self.icon_ui_helper:
                        try:
                            consumable_data = {
                                "name": hotbar_content.name,
                                "icon_id": getattr(hotbar_content, "icon_id", None),
                            }
                            icon_surface = self.icon_ui_helper.get_item_icon_surface(
                                consumable_data,
                                size=self.HOTBAR_ICON_SIZE
                            )
                            if icon_surface:
                                screen.blit(icon_surface, (slot_x, slot_y))
                        except Exception:
                            pass
                    
                    # Draw quantity
                    self.renderer.draw_text(screen, qty, (slot_x + 5, slot_y + 48),
                                            color=(200, 200, 100))
                else:
                    btn_color = (60, 40, 80)
                    ability = player.ability_book.get_ability(hotbar_content)
                    label = ability.name if ability else "?"
                    qty = ""
                    
                    # Draw ability
                    pygame.draw.rect(screen, btn_color, slot_rect)
                    pygame.draw.rect(screen, (200, 150, 200), slot_rect, 2)
                    
                    # Draw icon if available
                    if self.icon_ui_helper and ability:
                        try:
                            ability_data = {
                                "ability_id": ability.ability_id,
                                "name": ability.name,
                                "icon_id": getattr(ability, "icon_id", None),
                                "effect_type": getattr(ability, "effect_type", "damage")
                            }
                            icon_surface = self.icon_ui_helper.get_ability_icon_surface(
                                ability_data,
                                size=self.HOTBAR_ICON_SIZE
                            )
                            if icon_surface:
                                screen.blit(icon_surface, (slot_x, slot_y))
                        except Exception:
                            pass
            else:
                pygame.draw.rect(screen, (40, 40, 50), slot_rect)
                pygame.draw.rect(screen, (80, 80, 100), slot_rect, 1)

            # Slot number (1-0). Derived from the index rather than a loop
            # variable so it cannot drift from _hotbar_slot_rect's own
            # divmod - the whole point of routing geometry through one place.
            col = i % 10
            slot_num = (col + 1) if col < 9 else 0
            self.renderer.draw_text(screen, str(slot_num), (slot_x + 50, slot_y + 50),
                                    color=(100, 150, 200))

        # Extra (click-only) slots - same visuals as the main grid, no
        # keybind number since these are mouse-only (see Character.extra_slots
        # / combat_screen.py's matching render block).
        extra_rects = self._extra_slot_rects()
        self.renderer.draw_text(
            screen, "Extra Slots (click only, no keybind):",
            (self.HOTBAR_PANEL_X + 20, extra_rects[0].y - 30),
            color=(150, 150, 150))

        for i, slot_rect in enumerate(extra_rects):
            slot_x, slot_y = slot_rect.x, slot_rect.y
            extra_content = player.extra_slots[i] if i < len(player.extra_slots) else None

            if extra_content:
                if isinstance(extra_content, Consumable):
                    pygame.draw.rect(screen, (40, 60, 40), slot_rect)
                    pygame.draw.rect(screen, (150, 200, 150), slot_rect, 2)
                    if self.icon_ui_helper:
                        try:
                            consumable_data = {
                                "name": extra_content.name,
                                "icon_id": getattr(extra_content, "icon_id", None),
                            }
                            icon_surface = self.icon_ui_helper.get_item_icon_surface(
                                consumable_data, size=self.HOTBAR_ICON_SIZE)
                            if icon_surface:
                                screen.blit(icon_surface, (slot_x, slot_y))
                        except Exception:
                            pass
                    self.renderer.draw_text(screen, f"x{extra_content.quantity}",
                                            (slot_x + 5, slot_y + 48), color=(200, 200, 100))
                else:
                    ability = player.ability_book.get_ability(extra_content)
                    pygame.draw.rect(screen, (60, 40, 80), slot_rect)
                    pygame.draw.rect(screen, (200, 150, 200), slot_rect, 2)
                    if self.icon_ui_helper and ability:
                        try:
                            ability_data = {
                                "ability_id": ability.ability_id,
                                "name": ability.name,
                                "icon_id": getattr(ability, "icon_id", None),
                                "effect_type": getattr(ability, "effect_type", "damage")
                            }
                            icon_surface = self.icon_ui_helper.get_ability_icon_surface(
                                ability_data, size=self.HOTBAR_ICON_SIZE)
                            if icon_surface:
                                screen.blit(icon_surface, (slot_x, slot_y))
                        except Exception:
                            pass
            else:
                # Slightly different border tint than an empty hotbar slot,
                # matching combat_screen.py's convention for "this slot has
                # no keybind fallback".
                pygame.draw.rect(screen, (40, 40, 50), slot_rect)
                pygame.draw.rect(screen, (90, 80, 60), slot_rect, 1)

        # Instructions
        line1 = "Click ability/consumable on left, then a hotbar or extra slot to assign. Click a slot again to clear."
        line2 = "Mouse wheel: scroll list  |  ESC: return"
        self.renderer.draw_text(screen, line1, self._centered(line1, 640, 660),
                                color=(150, 150, 150))
        self.renderer.draw_text(screen, line2, self._centered(line2, 640, 685),
                                color=(150, 150, 150))

        # Real hover tooltip - per Kyle's ask, same shared
        # Ability.get_tooltip_lines() cast_screen.py/combat_screen.py use.
        if self.hovered_ability is not None:
            self._render_ability_tooltip(screen, self.hovered_ability, self.mouse_pos)

    def _render_ability_tooltip(self, screen, ability, pos):
        """Hover tooltip for an ability. ONE implementation, in ui/ability_tooltip.py -
        this used to be a 40-line copy of the same box drawn in two other screens.
        """
        from ui.ability_tooltip import draw_ability_tooltip
        draw_ability_tooltip(self.renderer, screen, ability, pos,
                             getattr(self.state_manager, "player", None))
