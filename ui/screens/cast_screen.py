"""
Cast Screen - full-screen, FF-style out-of-combat buff/heal menu.

REPLACES CastPanel (the collapsible right-edge sidebar widget). That panel's
underlying caster -> ability -> target logic was correct (verified: costs,
learned-gating, talented_cost all worked), but its 190px-tall strip could
only ever show 2-3 ability rows before hitting its own Back button, even
after adding real scrolling - the panel was just too short for any class
with more than a handful of out-of-combat spells (nearly everyone past
~level 15). Per Kyle: "let's make it a menu like final fantasy" - a real
full-screen two-column layout (party roster left, that member's ability
list right), modeled directly on SkillsScreen's proven real scrolling
list (same VISIBLE_ROWS/scroll_offset/"[X-Y of Z]" indicator pattern,
not a new invention), with a lightweight target picker overlay when an
ability needs one.

Opened via GameState.CAST (see core/game_state.py's registry and
overworld_screen.py's "Cast (N)" tab / N key, both updated to transition
here instead of toggling the old panel).
"""
import pygame
from core.game_states import GameState
from ui.screens.base_screen import BaseScreen
from ui.renderer import Renderer
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_GOLD, COLOR_GREEN, COLOR_RED, COLOR_DARK_GRAY


class CastScreen(BaseScreen):
    """Full-screen caster -> ability -> target picker for out-of-combat casts."""

    # Left column: party roster.
    ROSTER_X = 40
    ROSTER_Y = 100
    ROSTER_WIDTH = 320
    ROSTER_HEIGHT = 540
    ROSTER_ROW_HEIGHT = 92

    # Right column: selected member's ability list - same real proportions
    # as SkillsScreen's ABILITY_LIST/HOTBAR_PANEL split, so this reads as
    # the same family of screen rather than a one-off layout.
    ABILITY_X = 400
    ABILITY_Y = 100
    ABILITY_WIDTH = 480
    ABILITY_HEIGHT = 540
    ABILITY_ROW_HEIGHT = 56
    VISIBLE_ROWS = ABILITY_HEIGHT // ABILITY_ROW_HEIGHT  # real division, not guessed - 540/56 = 9

    ICON_SIZE = 40

    def __init__(self, state_manager, icon_ui_helper=None):
        super().__init__(state_manager)
        self.icon_ui_helper = icon_ui_helper
        self.renderer = Renderer()

        self.selected_caster = None
        self.selected_ability = None
        self.ability_scroll_offset = 0

        # Target picker overlay state - shown as a centered floating list
        # rather than a 4th screen/stage, since it's a short-lived choice
        # layered on top of the ability list, not a real navigation step.
        self.picking_target = False
        self.target_candidates = []
        self.hovered_target = None
        self._target_rects = []

        self._roster_rects = []
        self._ability_rects = []

        # Real hover-tooltip state (Kyle's ask: hover an ability to see
        # its real pre-modifier info, matching real WoW's tooltip
        # convention). hovered_ability is the Ability under the mouse
        # right now (or None); mouse_pos is tracked so the tooltip can be
        # drawn near the cursor rather than at a fixed screen position.
        self.hovered_ability = None
        self.mouse_pos = (0, 0)
        # Parallel to _ability_rects (which stores (rect, click_callback)
        # pairs) - this stores (rect, ability) pairs specifically for
        # hover-tooltip lookup, since extracting the real Ability back out
        # of a click lambda closure isn't reliable/clean. Rebuilt every
        # render alongside _ability_rects.
        self._ability_hover_rects = []

        self.message = None
        self.message_color = COLOR_WHITE
        self.message_timer = 0.0

        self.return_state = GameState.OVERWORLD

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def set_subject(self, member=None, return_state=None):
        """Reset to a clean state and optionally pre-select a caster.
        Called explicitly by whatever transitions here (overworld_screen's
        Cast tab / N key) - matches InventoryScreen/SkillsScreen's real
        set_subject convention (GameStateManager.transition_to is a pure
        state-flag swap with no lifecycle hooks, so nothing resets
        automatically on entry; every other screen in this codebase relies
        on the CALLER resetting it, not an on_enter() this project doesn't
        have). member=None (the default) means "pick the first living
        party member," matching this screen's normal open path from the
        overworld Cast tab, where there's no specific caster in mind yet.
        """
        party = self.state_manager.get_party()
        living = party.living_members() if party else []
        self.selected_caster = member or (living[0] if living else None)
        self.selected_ability = None
        self.ability_scroll_offset = 0
        self.picking_target = False
        self.message = None
        if return_state is not None:
            self.return_state = return_state

    def _close(self):
        self.state_manager.transition_to(self.return_state or GameState.OVERWORLD)

    # ------------------------------------------------------------------
    # Ability logic (identical to CastPanel's real, proven casting logic -
    # not reimplemented, just moved)
    # ------------------------------------------------------------------

    def _castable_abilities(self, member):
        out = []
        for ability in member.ability_book.abilities.values():
            if not getattr(ability, "is_learned", True):
                continue
            if hasattr(ability, "is_form_ready") and not ability.is_form_ready(member):
                continue
            target_type = getattr(ability, "target_type", "enemy")
            if target_type == "enemy":
                continue
            out.append(ability)
        return out

    def _can_afford(self, actor, ability):
        from combat.abilities import get_class_resource, ResourceType
        resource = get_class_resource(actor.char_class)
        cost = ability.talented_cost(actor) if hasattr(ability, "talented_cost") else 0
        pools = {
            ResourceType.MANA: actor.current_mana,
            ResourceType.RAGE: actor.current_rage,
            ResourceType.ENERGY: actor.current_energy,
        }
        return pools.get(resource, 9999) >= cost

    def _resource_abbrev(self, actor):
        from combat.abilities import get_class_resource, ResourceType
        resource = get_class_resource(actor.char_class)
        return {
            ResourceType.MANA: "Mana",
            ResourceType.RAGE: "Rage",
            ResourceType.ENERGY: "Energy",
        }.get(resource, "")

    def _pick_caster(self, member):
        if member is self.selected_caster:
            return
        self.selected_caster = member
        self.selected_ability = None
        self.ability_scroll_offset = 0
        self.picking_target = False

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
        self.picking_target = True

    def _cast(self, actor, ability, target):
        # in_combat=False: this screen is overworld-only, so casts here
        # never start a cooldown - see Ability.use()'s in_combat docstring.
        success, message = actor.ability_book.get_ability(ability.ability_id).use(
            actor, target, in_combat=False)
        self._show_message(message, COLOR_GOLD if success else COLOR_RED)
        self.picking_target = False
        self.selected_ability = None

    def _show_message(self, text, color):
        self.message = text
        self.message_color = color
        self.message_timer = 3.0

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.picking_target:
                self.picking_target = False
            else:
                self._close()
            return

        if event.type == pygame.MOUSEWHEEL and not self.picking_target:
            castable = self._castable_abilities(self.selected_caster) if self.selected_caster else []
            max_offset = max(0, len(castable) - self.VISIBLE_ROWS)
            self.ability_scroll_offset = max(0, min(max_offset, self.ability_scroll_offset - event.y))
            return

        if event.type == pygame.MOUSEMOTION and self.picking_target:
            self.hovered_target = self._hit_test_target(event.pos)
            return

        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
            self.hovered_ability = None
            for rect, ability in self._ability_hover_rects:
                if rect.collidepoint(event.pos):
                    self.hovered_ability = ability
                    break
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.picking_target:
                target = self._hit_test_target(event.pos)
                if target is not None:
                    self._cast(self.selected_caster, self.selected_ability, target)
                    return
                # Click outside the target list cancels back to the ability list.
                self.picking_target = False
                return

            for rect, callback in self._roster_rects:
                if rect.collidepoint(event.pos):
                    callback()
                    return
            for rect, callback in self._ability_rects:
                if rect.collidepoint(event.pos):
                    callback()
                    return

    def _hit_test_target(self, pos):
        for combatant, rect in self._target_rects:
            if rect.collidepoint(pos):
                return combatant
        return None

    # ------------------------------------------------------------------
    # Update / render
    # ------------------------------------------------------------------

    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = None

    def _centered(self, text, center_x, y, size="normal"):
        font = (self.renderer.font_large if size == "large"
                else self.renderer.font_normal)
        return (center_x - font.size(text)[0] // 2, y)

    def render(self, screen):
        screen.fill((22, 22, 30))

        title = "Cast"
        self.renderer.draw_text(
            screen, title, self._centered(title, SCREEN_WIDTH // 2, 30, size="large"),
            color=(200, 200, 100), size="large")

        self._render_roster(screen)
        self._render_abilities(screen)
        if self.picking_target:
            self._render_target_overlay(screen)

        if self.message:
            wrapped = self.renderer.wrap_text(self.message, self.ABILITY_WIDTH)
            msg_y = SCREEN_HEIGHT - 20 * len(wrapped) - 50
            for line in wrapped:
                self.renderer.draw_text(screen, line, (self.ABILITY_X, msg_y),
                                        font_size=18, color=self.message_color)
                msg_y += 22

        close_rect = pygame.Rect(SCREEN_WIDTH - 120, 20, 100, 40)
        self.renderer.draw_button(screen, close_rect, "Close (Esc)")
        self._roster_rects.append((close_rect, self._close))

        if self.hovered_ability is not None and not self.picking_target:
            self._render_tooltip(screen, self.hovered_ability, self.mouse_pos)

    def _render_tooltip(self, screen, ability, pos):
        """Real hover tooltip - per Kyle's ask, showing the ability's raw
        pre-modifier info (see Ability.get_tooltip_lines' docstring for
        why these numbers deliberately don't reflect the caster's actual
        computed damage). Positioned near the cursor, clamped so it can
        never draw off the right/bottom edge of the screen.
        """
        lines = ability.get_tooltip_lines(getattr(self.state_manager, "player", None))
        if not lines:
            return

        font_size = 14
        line_height = 18
        padding = 10
        font = self.renderer._get_font(font_size=font_size)

        # Wrap the description line (usually the longest) rather than
        # letting a long flavor-text line force the tooltip absurdly wide.
        max_text_width = 320
        wrapped_lines = []
        for line in lines:
            if font.size(line)[0] <= max_text_width:
                wrapped_lines.append(line)
                continue
            words = line.split()
            cur = ""
            for word in words:
                candidate = f"{cur} {word}".strip()
                if font.size(candidate)[0] > max_text_width and cur:
                    wrapped_lines.append(cur)
                    cur = word
                else:
                    cur = candidate
            if cur:
                wrapped_lines.append(cur)

        box_w = max(font.size(l)[0] for l in wrapped_lines) + padding * 2
        box_h = len(wrapped_lines) * line_height + padding * 2

        x, y = pos
        x += 16  # offset so the tooltip doesn't sit directly under the cursor
        y += 16
        if x + box_w > SCREEN_WIDTH:
            x = SCREEN_WIDTH - box_w - 4
        if y + box_h > SCREEN_HEIGHT:
            y = SCREEN_HEIGHT - box_h - 4

        pygame.draw.rect(screen, (15, 15, 20), (x, y, box_w, box_h))
        pygame.draw.rect(screen, COLOR_GOLD, (x, y, box_w, box_h), 2)

        text_y = y + padding
        for i, line in enumerate(wrapped_lines):
            # First line (name+rank) in gold, rest in white - matches the
            # real WoW convention Kyle's screenshot shows (title stands
            # out, body text is plain).
            color = COLOR_GOLD if i == 0 else COLOR_WHITE
            self.renderer.draw_text(screen, line, (x + padding, text_y),
                                    font_size=font_size, color=color)
            text_y += line_height

    def _render_roster(self, screen):
        self._roster_rects = []
        pygame.draw.rect(screen, (50, 50, 60),
                         (self.ROSTER_X, self.ROSTER_Y, self.ROSTER_WIDTH, self.ROSTER_HEIGHT), 2)
        self.renderer.draw_text(screen, "Party", (self.ROSTER_X + 10, self.ROSTER_Y - 25),
                                color=(200, 200, 100), size="large")

        party = self.state_manager.get_party()
        from combat.abilities import get_class_resource, ResourceType
        for i, member in enumerate(party.living_members()):
            row_y = self.ROSTER_Y + i * self.ROSTER_ROW_HEIGHT
            rect = pygame.Rect(self.ROSTER_X, row_y, self.ROSTER_WIDTH, self.ROSTER_ROW_HEIGHT - 6)

            is_selected = member is self.selected_caster
            pygame.draw.rect(screen, (40, 60, 90) if is_selected else (32, 32, 40), rect)
            pygame.draw.rect(screen, COLOR_GOLD if is_selected else (70, 70, 85), rect, 2 if is_selected else 1)

            text_x = rect.x + 10
            if self.icon_ui_helper:
                class_icon = self.icon_ui_helper.get_class_icon_surface(member.char_class, size=self.ICON_SIZE)
                if class_icon:
                    screen.blit(class_icon, (rect.x + 6, rect.y + 6))
                    text_x = rect.x + self.ICON_SIZE + 16

            self.renderer.draw_text(screen, member.name, (text_x, rect.y + 4),
                                    font_size=18, color=COLOR_WHITE)
            castable_count = len(self._castable_abilities(member))
            self.renderer.draw_text(screen, f"{castable_count} spells", (rect.right - 90, rect.y + 6),
                                    font_size=14, color=COLOR_GOLD)

            # Real HP bar - per Kyle's "see party members' HP" ask. Same
            # green/yellow/red thresholds as the combat screen's own
            # health bars, not a new invented color scheme, so this reads
            # consistently whether you're looking at it here or mid-fight.
            bar_x, bar_y = text_x, rect.y + 24
            bar_w, bar_h = rect.right - bar_x - 10, 10
            hp_pct = (member.current_health / member.health) if member.health else 0
            hp_pct = max(0.0, min(1.0, hp_pct))
            if hp_pct > 0.5:
                hp_color = (80, 200, 90)
            elif hp_pct > 0.25:
                hp_color = (220, 190, 60)
            else:
                hp_color = (210, 70, 70)
            pygame.draw.rect(screen, (20, 20, 24), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(screen, hp_color, (bar_x, bar_y, int(bar_w * hp_pct), bar_h))
            pygame.draw.rect(screen, (80, 80, 90), (bar_x, bar_y, bar_w, bar_h), 1)
            hp_text = f"{member.display_health}/{round(member.health)}"
            self.renderer.draw_text(screen, hp_text, (bar_x + bar_w + 6, bar_y - 2),
                                    font_size=13, color=(200, 200, 205))

            # Resource bar (Mana/Rage/Energy) - same "see the mana of the
            # character using it" ask this screen already honored in the
            # ability-cost display, now visible at a glance on the roster
            # too, not just after you've already picked them.
            resource = get_class_resource(member.char_class)
            pools = {
                ResourceType.MANA: (member.current_mana, getattr(member, "mana", 0), (90, 130, 230)),
                ResourceType.RAGE: (member.current_rage, 100, (200, 70, 70)),
                ResourceType.ENERGY: (member.current_energy, 100, (210, 200, 60)),
            }
            pool = pools.get(resource)
            res_y = bar_y + 14
            if pool is not None and pool[1]:
                cur, mx, res_color = pool
                res_pct = max(0.0, min(1.0, cur / mx)) if mx else 0
                pygame.draw.rect(screen, (20, 20, 24), (bar_x, res_y, bar_w, 6))
                pygame.draw.rect(screen, res_color, (bar_x, res_y, int(bar_w * res_pct), 6))
                pygame.draw.rect(screen, (80, 80, 90), (bar_x, res_y, bar_w, 6), 1)

            # Active buffs/debuffs - per Kyle's ask. Filtered to BUFF/
            # Active buffs/debuffs - per Kyle's ask. Filtered to BUFF/
            # DEBUFF only (StatusEffectMixin also tracks DOT/HOT ticks,
            # which aren't "buffs" a player is choosing to track here -
            # a DoT on a party member would be unusual/an edge case
            # anyway, but excluding it keeps this row reading as "status
            # effects", not internal combat bookkeeping). Uses the real
            # StatusEffect objects via _effects() (not get_effects_summary,
            # which strips down to (name, duration, effect_type) tuples
            # and loses icon_id) so real icons can render via
            # get_status_effect_icon_surface - falls back to that same
            # helper's own effect_type-based fallback icon for anything
            # without a real icon_id yet, so this never shows a blank gap.
            from combat.status_effects import EffectType
            buffs = [e for e in member._effects()
                    if e.effect_type in (EffectType.BUFF, EffectType.DEBUFF)]
            buff_y = res_y + 12
            BUFF_ICON_SIZE = 20
            if buffs and self.icon_ui_helper:
                icon_x = text_x
                for effect in buffs[:6]:
                    surface = self.icon_ui_helper.get_status_effect_icon_surface(effect, size=BUFF_ICON_SIZE)
                    if surface:
                        screen.blit(surface, (icon_x, buff_y))
                    icon_x += BUFF_ICON_SIZE + 4
                if len(buffs) > 6:
                    self.renderer.draw_text(screen, f"+{len(buffs) - 6}", (icon_x, buff_y + 2),
                                            font_size=12, color=(160, 210, 160))
            elif buffs:
                # No icon helper wired (e.g. a headless/test render) -
                # same text fallback as before, so this never renders
                # nothing at all just because icons aren't available.
                buff_text = "  ".join(e.name for e in buffs[:3])
                if len(buffs) > 3:
                    buff_text += f"  +{len(buffs) - 3}"
                self.renderer.draw_text(screen, buff_text, (text_x, buff_y),
                                        font_size=13, color=(160, 210, 160))
            else:
                self.renderer.draw_text(screen, "No active buffs", (text_x, buff_y),
                                        font_size=13, color=(90, 90, 95))

            self._roster_rects.append((rect, lambda m=member: self._pick_caster(m)))

    def _render_abilities(self, screen):
        self._ability_rects = []
        self._ability_hover_rects = []
        pygame.draw.rect(screen, (50, 50, 60),
                         (self.ABILITY_X, self.ABILITY_Y, self.ABILITY_WIDTH, self.ABILITY_HEIGHT), 2)

        actor = self.selected_caster
        if actor is None:
            self.renderer.draw_text(screen, "No party members available.",
                                    (self.ABILITY_X + 10, self.ABILITY_Y + 10),
                                    font_size=16, color=COLOR_DARK_GRAY)
            return

        castable = self._castable_abilities(actor)

        header = f"{actor.name}'s Spells ({len(castable)})"
        if len(castable) > self.VISIBLE_ROWS:
            lo = self.ability_scroll_offset + 1
            hi = min(self.ability_scroll_offset + self.VISIBLE_ROWS, len(castable))
            header += f"  [{lo}-{hi}]"
        self.renderer.draw_text(screen, header, (self.ABILITY_X + 10, self.ABILITY_Y - 25),
                                color=(200, 200, 100), size="large")

        resource_label = self._resource_abbrev(actor)
        from combat.abilities import get_class_resource, ResourceType
        resource = get_class_resource(actor.char_class)
        pools = {
            ResourceType.MANA: actor.current_mana,
            ResourceType.RAGE: actor.current_rage,
            ResourceType.ENERGY: actor.current_energy,
        }
        current_resource = pools.get(resource)
        if current_resource is not None and resource_label:
            pool_text = f"{round(current_resource)} {resource_label}"
            self.renderer.draw_text(
                screen, pool_text,
                (self.ABILITY_X + self.ABILITY_WIDTH - 10 - self.renderer.font_normal.size(pool_text)[0], self.ABILITY_Y - 25),
                font_size=16, color=(150, 190, 255))

        if not castable:
            self.renderer.draw_text(screen, "Nothing castable.",
                                    (self.ABILITY_X + 10, self.ABILITY_Y + 10),
                                    font_size=16, color=COLOR_DARK_GRAY)
            return

        max_offset = max(0, len(castable) - self.VISIBLE_ROWS)
        self.ability_scroll_offset = max(0, min(max_offset, self.ability_scroll_offset))
        visible = castable[self.ability_scroll_offset:self.ability_scroll_offset + self.VISIBLE_ROWS]

        for i, ability in enumerate(visible):
            row_y = self.ABILITY_Y + i * self.ABILITY_ROW_HEIGHT
            rect = pygame.Rect(self.ABILITY_X, row_y, self.ABILITY_WIDTH, self.ABILITY_ROW_HEIGHT - 4)

            affordable = self._can_afford(actor, ability)
            color = COLOR_WHITE if affordable else COLOR_DARK_GRAY
            pygame.draw.rect(screen, (32, 32, 40), rect)
            pygame.draw.rect(screen, (70, 70, 85), rect, 1)

            icon_pad = 8
            if self.icon_ui_helper:
                surface = self.icon_ui_helper.get_ability_icon_surface(ability, size=self.ICON_SIZE)
                if surface:
                    screen.blit(surface, (rect.x + icon_pad, rect.y + icon_pad))
            text_x = rect.x + self.ICON_SIZE + icon_pad * 2

            self.renderer.draw_text(screen, ability.name, (text_x, rect.y + 6),
                                    font_size=18, color=color)

            cost = ability.talented_cost(actor) if hasattr(ability, "talented_cost") else 0
            if cost and resource_label:
                cost_color = (150, 150, 160) if affordable else (140, 90, 90)
                self.renderer.draw_text(screen, f"{int(cost)} {resource_label}",
                                        (text_x, rect.y + 28),
                                        font_size=14, color=cost_color)

            self._ability_rects.append((rect, lambda a=ability: self._pick_ability(a)))
            self._ability_hover_rects.append((rect, ability))

    def _render_target_overlay(self, screen):
        """Small floating target list, centered over the ability panel -
        a short-lived overlay rather than a full 3rd screen, since picking
        a target is a quick follow-up choice, not real navigation."""
        self._target_rects = []
        overlay_w, overlay_h = 300, 60 + 44 * min(len(self.target_candidates), 8)
        overlay_x = self.ABILITY_X + (self.ABILITY_WIDTH - overlay_w) // 2
        overlay_y = self.ABILITY_Y + (self.ABILITY_HEIGHT - overlay_h) // 2

        pygame.draw.rect(screen, (18, 18, 26), (overlay_x, overlay_y, overlay_w, overlay_h))
        pygame.draw.rect(screen, COLOR_GOLD, (overlay_x, overlay_y, overlay_w, overlay_h), 2)

        title = f"Target for {self.selected_ability.name}"
        self.renderer.draw_text(screen, title, (overlay_x + 10, overlay_y + 10),
                                font_size=16, color=COLOR_GOLD)

        for i, member in enumerate(self.target_candidates):
            rect = pygame.Rect(overlay_x + 10, overlay_y + 44 + i * 44, overlay_w - 20, 38)
            is_hovered = member is self.hovered_target
            pygame.draw.rect(screen, (28, 40, 28), rect)
            pygame.draw.rect(screen, COLOR_GOLD if is_hovered else COLOR_GREEN, rect, 2 if is_hovered else 1)
            color = COLOR_GOLD if is_hovered else COLOR_GREEN
            self.renderer.draw_text(screen, member.name, (rect.x + 10, rect.y + 8),
                                    font_size=16, color=color)
            self._target_rects.append((member, rect))
