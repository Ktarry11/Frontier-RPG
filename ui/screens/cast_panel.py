"""
Cast Panel - collapsible out-of-combat buff/heal widget for the overworld.

REPLACES the old full-screen CastScreen as the primary way to cast buffs
and heals outside combat. That screen worked correctly (verified directly -
casting Fortitude, Renew, Heal etc all functioned), but it was only
reachable via the "B" key, which nothing in the UI explained and which
collides with WoW's real convention (B opens Bags/inventory there, not a
spellbook). A binding nobody would ever discover by accident is the same
as a missing feature, so per Kyle: rework this as an always-present,
collapsed tab on the right-side info panel that expands into a clickable
list - no hidden keybind required, though N still toggles it for a fast
keyboard path.

This does NOT reimplement the caster -> ability -> target logic; it wraps
the exact same selection state machine CastScreen already used (proven
correct in isolation), just rendered as a panel instead of taking over the
whole screen, so the map and party stay visible underneath it.

Layout: sits in the ~460px strip right of the viewport (SCREEN_WIDTH=1280,
VIEWPORT_X+VIEWPORT_WIDTH=820), below OverworldScreen's existing HP/resource
block, above the tilemap legend it already draws there.
"""
import pygame
from ui.renderer import Renderer
from config import SCREEN_WIDTH, COLOR_WHITE, COLOR_GOLD, COLOR_GREEN, COLOR_RED, COLOR_DARK_GRAY


class CastPanel:
    """Collapsed tab that expands into a caster -> ability -> target picker."""

    ROW_HEIGHT = 40
    PANEL_WIDTH = 260
    TAB_WIDTH = 28
    ICON_SIZE = 32

    def __init__(self, state_manager, x, y, height):
        self.state_manager = state_manager
        self.renderer = Renderer()

        # Panel's own top-left and available height, passed in by
        # OverworldScreen so this widget doesn't hardcode a layout that
        # would drift out of sync with the info panel above it.
        self.x = x
        self.y = y
        self.height = height

        self.expanded = False

        # Same 3-stage state machine as the old CastScreen.
        self.stage = "caster"
        self.selected_caster = None
        self.selected_ability = None
        self.target_candidates = []
        self.hovered_target = None
        self._target_rects = []
        self._row_rects = []  # (rect, callback) pairs rebuilt each render

        # Scroll offset for the ability list (index of the first VISIBLE
        # row) - mirrors skills_screen.py's real fix for the identical
        # overflow bug: a fixed-height panel drawing every castable
        # ability as a fixed-height row, with no regard for how many
        # actually fit, spilled rows past the panel border into raw
        # unclipped space and stranded the Back button mid-list once a
        # caster had more than a handful of out-of-combat-usable spells
        # (which is nearly every class past ~level 15). Reset to 0
        # whenever a new caster is picked (_pick_caster) or the panel
        # closes (_reset_selection), so scroll position never leaks
        # between different casters' lists.
        self.ability_scroll_offset = 0

        self.message = None
        self.message_color = COLOR_WHITE
        self.message_timer = 0.0

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def toggle(self):
        self.expanded = not self.expanded
        if not self.expanded:
            self._reset_selection()

    def _reset_selection(self):
        self.stage = "caster"
        self.selected_caster = None
        self.selected_ability = None
        self.target_candidates = []
        self.ability_scroll_offset = 0

    def _visible_rows(self):
        """How many ability rows actually fit in the panel's real height,
        computed from the SAME real geometry _list_row_rect and the Back
        button already use (rows start at y+40, Back sits at
        y+height-34) - not a separate guessed reservation, so this stays
        exactly in sync if either of those ever changes. This is the real
        fix for the overflow bug: rows are computed from actual available
        space instead of being drawn unconditionally for every castable
        ability regardless of whether the panel is tall enough.
        """
        rows_start_y = 40
        back_button_top = self.height - 34
        available = back_button_top - rows_start_y
        return max(1, available // self.ROW_HEIGHT)

    def handle_event(self, event):
        """Returns True if the event was consumed (caller should not also
        treat it as overworld movement/interaction input).

        NOTE: the panel's own edge tab (CAST label, click-to-expand) was
        removed when the right-side tab column replaced it - see
        overworld_screen.py's tab_rects["cast"]. This method no longer
        checks _tab_rect() for a click; opening/closing now only happens
        via the tab column button (OverworldScreen calls .toggle()
        directly) or the N key below.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.expanded:
                return False
            # Click outside the panel while expanded closes it, same as
            # clicking away from any dropdown - avoids a stuck-open panel
            # eating clicks meant for the map.
            if not self._panel_rect().collidepoint(event.pos):
                self.expanded = False
                self._reset_selection()
                return False
            for rect, callback in self._row_rects:
                if rect.collidepoint(event.pos):
                    callback()
                    return True
            return True  # swallow clicks inside the panel that hit nothing

        if not self.expanded:
            return False

        if event.type == pygame.MOUSEWHEEL and self.stage == "ability":
            # Real scroll fix - see _visible_rows' docstring for the
            # overflow bug this addresses. Clamped exactly like
            # skills_screen.py's identical fix: can't scroll above the
            # first row or past the point where the last row would be
            # the final visible one.
            castable = self._castable_abilities(self.selected_caster)
            max_offset = max(0, len(castable) - self._visible_rows())
            self.ability_scroll_offset = max(0, min(max_offset, self.ability_scroll_offset - event.y))
            return True

        if event.type == pygame.MOUSEMOTION and self.stage == "target":
            self.hovered_target = self._hit_test(event.pos)
            return True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.stage == "target":
                self.stage = "ability"
            elif self.stage == "ability":
                self.stage = "caster"
                self.selected_caster = None
            else:
                self.expanded = False
            return True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_n:
            # N re-toggles closed. The catch-all `return True` below would
            # otherwise swallow every KEYDOWN while expanded - including a
            # second N press - before it ever reached OverworldScreen's own
            # N handler, which can only fire while this method returns
            # False. Handling it here directly is what makes N a real
            # open/close toggle instead of "open-only".
            self.toggle()
            return True

        # While expanded, this widget owns input - WSAD etc shouldn't walk
        # the player around behind an open panel.
        return True

    def _hit_test(self, pos):
        for combatant, rect in self._target_rects:
            if rect.collidepoint(pos):
                return combatant
        return None

    # ------------------------------------------------------------------
    # Casting (identical logic to the old CastScreen)
    # ------------------------------------------------------------------

    def _castable_abilities(self, member):
        from combat.abilities import is_castable_out_of_combat
        out = []
        for ability in member.ability_book.abilities.values():
            if not getattr(ability, "is_learned", True):
                continue
            # Form-gated abilities (Mangle etc - see Ability.requires_form)
            # only appear here while the caster is actually in a form that
            # allows them, same reasoning as is_usable_by(): "known" and
            # "castable right now" are different questions, and this panel
            # cares about the second one.
            if hasattr(ability, "is_form_ready") and not ability.is_form_ready(member):
                continue
            # ONE RULE, in combat/abilities.py - and it is keyed on what the ability DOES,
            # not on who its target_type claims to point at. See is_castable_out_of_combat:
            # the old target_type test let every Cleave and every untyped damage spell in the
            # game through, aimed at the party.
            if not is_castable_out_of_combat(ability):
                continue
            out.append(ability)
        return out

    def _pick_caster(self, member):
        self.selected_caster = member
        self.stage = "ability"
        self.ability_scroll_offset = 0

    def _pick_ability(self, ability):
        actor = self.selected_caster
        target_type = getattr(ability, "target_type", "ally")

        if target_type == "self":
            self._cast(actor, ability, actor)
            return
        if target_type == "party":
            party = self.state_manager.get_party()
            self._cast(actor, ability, party.living_members())
            return

        party = self.state_manager.get_party()
        self.target_candidates = party.living_members()
        if len(self.target_candidates) == 1:
            self._cast(actor, ability, self.target_candidates[0])
            return
        self.selected_ability = ability
        self.hovered_target = self.target_candidates[0]
        self.stage = "target"

    def _cast(self, actor, ability, target):
        # in_combat=False: this panel is overworld-only (see module
        # docstring), so casts here never start a cooldown - see
        # Ability.use()'s in_combat docstring for why.
        success, message = actor.ability_book.get_ability(ability.ability_id).use(
            actor, target, in_combat=False)
        self._show_message(message, COLOR_GOLD if success else COLOR_RED)
        self.stage = "caster"
        self.selected_caster = None
        self.selected_ability = None

    def _show_message(self, text, color):
        self.message = text
        self.message_color = color
        self.message_timer = 3.0

    def _can_afford(self, actor, ability):
        from combat.abilities import get_class_resource, ResourceType
        resource = get_class_resource(actor.char_class)
        # THE ACTUAL BUG: get_current_cost() doesn't exist on Ability at
        # all (see combat/abilities.py - the real API is the `cost`
        # property, or talented_cost(caster) for the talent-reduced real
        # cost that use() and _has_resource() actually check against).
        # hasattr() silently swallowed the AttributeError and fell back to
        # 0 every time, so every ability in this panel has always read as
        # "affordable" regardless of actual mana/rage/energy cost.
        cost = ability.talented_cost(actor) if hasattr(ability, "talented_cost") else 0
        pools = {
            ResourceType.MANA: actor.current_mana,
            ResourceType.RAGE: actor.current_rage,
            ResourceType.ENERGY: actor.current_energy,
        }
        return pools.get(resource, 9999) >= cost

    def _icon_helper(self):
        """The icon UI helper, read lazily from state_manager rather than
        taken as a constructor arg.

        main.py builds icon_ui_helper AFTER GameStateManager.__init__ has
        already constructed every screen - screens that took it as a
        constructor argument got a permanent None because main.py only
        ever patched it back onto GameState.SKILLS afterward, never onto
        every other screen (see icon_system_core.py for the fuller story).
        Reading it fresh from state_manager at render time sidesteps the
        ordering problem entirely: by the time anything actually renders,
        main.py has long since finished setup.
        """
        return getattr(self.state_manager, "icon_ui_helper", None)

    def _draw_ability_icon(self, screen, ability, x, y):
        """Draw an ability's icon at (x,y), or nothing if the icon system
        isn't available (keeps this panel working even if icon_ui_helper
        never got set up)."""
        helper = self._icon_helper()
        if helper is None:
            return
        surface = helper.get_ability_icon_surface(ability, size=self.ICON_SIZE)
        if surface:
            screen.blit(surface, (x, y))

    def _resource_abbrev(self, actor):
        """Short label for the caster's resource pool - 'Mana', 'Rage',
        'Energy' - so a cost can read '40 Mana' instead of a bare number
        with no unit."""
        from combat.abilities import get_class_resource, ResourceType
        resource = get_class_resource(actor.char_class)
        return {
            ResourceType.MANA: "Mana",
            ResourceType.RAGE: "Rage",
            ResourceType.ENERGY: "Energy",
        }.get(resource, "")

    # ------------------------------------------------------------------
    # Update / render
    # ------------------------------------------------------------------

    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = None

    def _panel_rect(self):
        return pygame.Rect(self.x, self.y, self.PANEL_WIDTH, self.height)

    def render(self, screen):
        if not self.expanded:
            return

        self._row_rects = []
        panel_rect = self._panel_rect()
        pygame.draw.rect(screen, (18, 18, 26), panel_rect)
        pygame.draw.rect(screen, (90, 90, 110), panel_rect, 2)

        if self.stage == "caster":
            self._render_caster_list(screen)
        elif self.stage == "ability":
            self._render_ability_list(screen)
        elif self.stage == "target":
            self._render_target_picker(screen)

        if self.message:
            wrapped = self.renderer.wrap_text(self.message, self.PANEL_WIDTH - 20)
            msg_y = self.y + self.height - 20 * len(wrapped) - 10
            for line in wrapped:
                self.renderer.draw_text(screen, line, (self.x + 10, msg_y),
                                        font_size=14, color=self.message_color)
                msg_y += 18

    def _list_row_rect(self, index):
        return pygame.Rect(self.x + 10, self.y + 40 + index * self.ROW_HEIGHT,
                           self.PANEL_WIDTH - 20, self.ROW_HEIGHT - 4)

    def _render_caster_list(self, screen):
        self.renderer.draw_text(screen, "Cast", (self.x + 10, self.y + 8),
                                font_size=14, color=COLOR_GOLD)
        party = self.state_manager.get_party()
        helper = self._icon_helper()
        for i, member in enumerate(party.living_members()):
            rect = self._list_row_rect(i)
            pygame.draw.rect(screen, (28, 28, 36), rect)
            pygame.draw.rect(screen, (70, 70, 85), rect, 1)

            text_x = rect.x + 8
            if helper is not None:
                class_icon = helper.get_class_icon_surface(member.char_class, size=self.ICON_SIZE)
                if class_icon:
                    screen.blit(class_icon, (rect.x + 4, rect.y + 4))
                    text_x = rect.x + self.ICON_SIZE + 12

            self.renderer.draw_text(screen, member.name, (text_x, rect.y + 5),
                                    font_size=14, color=COLOR_WHITE)
            castable_count = len(self._castable_abilities(member))
            self.renderer.draw_text(screen, f"{castable_count}",
                                    (rect.right - 24, rect.y + 5),
                                    font_size=14, color=COLOR_GOLD)
            self._row_rects.append((rect, lambda m=member: self._pick_caster(m)))

    def _render_ability_list(self, screen):
        actor = self.selected_caster
        self.renderer.draw_text(screen, f"{actor.name}", (self.x + 10, self.y + 8),
                                font_size=14, color=COLOR_GOLD)

        # Caster's current resource pool, so "can I afford this" is
        # visible at a glance instead of having to infer it from which
        # rows are greyed out. Matches Kyle's "also the mana of the
        # character using it" ask.
        from combat.abilities import get_class_resource, ResourceType
        resource = get_class_resource(actor.char_class)
        pools = {
            ResourceType.MANA: actor.current_mana,
            ResourceType.RAGE: actor.current_rage,
            ResourceType.ENERGY: actor.current_energy,
        }
        current_resource = pools.get(resource)
        resource_label = self._resource_abbrev(actor)
        if current_resource is not None and resource_label:
            self.renderer.draw_text(
                screen, f"{round(current_resource)} {resource_label}",
                (self.x + self.PANEL_WIDTH - 90, self.y + 10),
                font_size=12, color=(150, 190, 255))

        castable = self._castable_abilities(actor)
        if not castable:
            self.renderer.draw_text(screen, "Nothing castable.",
                                    (self.x + 10, self.y + 40),
                                    font_size=14, color=COLOR_DARK_GRAY)

        # Real overflow fix: only draw as many rows as _visible_rows()
        # says actually fit above the Back button, sliced from
        # ability_scroll_offset - mirrors skills_screen.py's identical
        # fix for the same "list longer than panel" bug. Previously every
        # castable ability drew unconditionally regardless of the panel's
        # real height, so any caster with more than ~4 out-of-combat
        # spells (nearly every class past ~level 15) spilled rows past
        # the border into raw unclipped space and stranded the Back
        # button mid-list.
        visible_rows = self._visible_rows()
        # Clamp here too (not just in the MOUSEWHEEL handler) so a
        # scroll_offset left over from a caster with a longer list
        # doesn't leave a shorter-list caster's view scrolled past its
        # own end - e.g. switching from a caster with 9 spells (scrolled
        # to offset 5) to one with only 3.
        max_offset = max(0, len(castable) - visible_rows)
        self.ability_scroll_offset = max(0, min(max_offset, self.ability_scroll_offset))
        visible = castable[self.ability_scroll_offset:self.ability_scroll_offset + visible_rows]

        if len(castable) > visible_rows:
            # "[X-Y of Z]" range indicator, same convention as
            # skills_screen.py, so it's clear there's more to scroll to
            # rather than the list silently ending mid-class.
            lo = self.ability_scroll_offset + 1
            hi = min(self.ability_scroll_offset + visible_rows, len(castable))
            self.renderer.draw_text(
                screen, f"[{lo}-{hi} of {len(castable)}]",
                (self.x + 10, self.y + 24),
                font_size=11, color=(140, 140, 150))

        for i, ability in enumerate(visible):
            rect = self._list_row_rect(i)
            affordable = self._can_afford(actor, ability)
            color = COLOR_WHITE if affordable else COLOR_DARK_GRAY
            pygame.draw.rect(screen, (28, 28, 36), rect)
            pygame.draw.rect(screen, (70, 70, 85), rect, 1)

            icon_pad = 4
            self._draw_ability_icon(screen, ability, rect.x + icon_pad, rect.y + icon_pad)
            text_x = rect.x + self.ICON_SIZE + icon_pad * 2

            self.renderer.draw_text(screen, ability.name, (text_x, rect.y + 4),
                                    font_size=13, color=color)

            # Cost line under the name, e.g. "40 Mana" - per Kyle's "cost
            # of the spell" ask. talented_cost() is the same real API
            # _can_afford() uses above (accounts for talent-reduced
            # costs) - NOT the nonexistent get_current_cost() this used
            # to call, which silently always returned 0 via hasattr().
            cost = ability.talented_cost(actor) if hasattr(ability, "talented_cost") else 0
            if cost and resource_label:
                cost_color = (150, 150, 160) if affordable else (140, 90, 90)
                self.renderer.draw_text(screen, f"{int(cost)} {resource_label}",
                                        (text_x, rect.y + 20),
                                        font_size=11, color=cost_color)

            self._row_rects.append((rect, lambda a=ability: self._pick_ability(a)))

        back_rect = pygame.Rect(self.x + 10, self.y + self.height - 34,
                                self.PANEL_WIDTH - 20, 26)
        pygame.draw.rect(screen, (40, 40, 45), back_rect)
        pygame.draw.rect(screen, COLOR_WHITE, back_rect, 1)
        self.renderer.draw_text(screen, "< Back", (back_rect.x + 8, back_rect.y + 4),
                                font_size=14, color=COLOR_WHITE)
        self._row_rects.append((back_rect, self._back_to_caster))

    def _back_to_caster(self):
        self.stage = "caster"
        self.selected_caster = None

    def _render_target_picker(self, screen):
        self._target_rects = []
        self.renderer.draw_text(screen, f"{self.selected_ability.name}",
                                (self.x + 10, self.y + 8),
                                font_size=14, color=COLOR_GOLD)

        for i, member in enumerate(self.target_candidates):
            rect = self._list_row_rect(i)
            is_hovered = member is self.hovered_target
            color = COLOR_GOLD if is_hovered else COLOR_GREEN
            border = COLOR_GOLD if is_hovered else COLOR_GREEN
            pygame.draw.rect(screen, (28, 40, 28), rect)
            pygame.draw.rect(screen, border, rect, 1)
            self.renderer.draw_text(screen, member.name, (rect.x + 8, rect.y + 5),
                                    font_size=14, color=color)
            self._target_rects.append((member, rect))
            self._row_rects.append(
                (rect, lambda m=member: self._cast(self.selected_caster, self.selected_ability, m)))

        back_rect = pygame.Rect(self.x + 10, self.y + self.height - 34,
                                self.PANEL_WIDTH - 20, 26)
        pygame.draw.rect(screen, (40, 40, 45), back_rect)
        pygame.draw.rect(screen, COLOR_WHITE, back_rect, 1)
        self.renderer.draw_text(screen, "< Back", (back_rect.x + 8, back_rect.y + 4),
                                font_size=14, color=COLOR_WHITE)
        self._row_rects.append((back_rect, self._back_to_ability))

    def _back_to_ability(self):
        self.stage = "ability"
