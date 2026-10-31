"""
RecruitDialogScreen - the conversation UI when the player walks up to a
recruitable companion NPC, BEFORE they join the party.

Previously (see overworld_screen.py's old _recruit_companion) pressing
Space on a recruit's tile silently added them to the party with zero
dialog - RecruitNPC.greeting existed in data/npcs/recruits.json and on
the RecruitNPC object, but nothing ever displayed it (dead data, same
class of bug flagged elsewhere in this codebase's known patterns). This
screen is the fix: it shows the recruit's greeting line and requires an
explicit Join/Leave choice, mirroring QuestDialogScreen's greeting +
accept/decline shape without dragging in any quest-turn-in machinery
that a recruitment conversation doesn't need.

A returning (previously dismissed) companion gets a distinct welcome-back
line instead of their first-meeting greeting, since "hello, stranger" text
reads wrong for someone who already traveled with you.
"""
import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_GOLD
from core.game_states import GameState
from ui.screens.base_screen import BaseScreen
from ui.recruit_portrait import get_recruit_portrait


class RecruitDialogScreen(BaseScreen):
    def __init__(self, state_manager, recruit):
        super().__init__(state_manager)
        self.recruit = recruit

        self.close_button = pygame.Rect(SCREEN_WIDTH - 140, SCREEN_HEIGHT - 70, 110, 40)
        self.join_button = pygame.Rect(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT - 90, 200, 50)
        self.leave_button = pygame.Rect(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT - 90, 200, 50)

        self.joined = False  # True once Join is clicked, swaps to a confirmation view
        self.result_message = None

    @property
    def _player_level(self):
        party = self.state_manager.get_party()
        player = getattr(party, "player", None)
        return getattr(player, "level", None)

    @property
    def block_reason(self):
        """Why this companion will not come, or None. Live, like is_returning:
        level up and walk back without leaving the screen and the Join button
        has to work."""
        return self.recruit.recruit_block_reason(self._player_level)

    @property
    def shown_level(self):
        """The level they will actually join at.

        The same catch-up level whether this is a first meeting or a return:
        somebody the player dismissed has been living their own life, not
        waiting in a doorway, so they come back having kept pace. If they left
        ABOVE the catch-up level they keep their own, which is why this is a
        max rather than a straight substitution.
        """
        lvl = self.recruit.effective_level(self._player_level)
        if self.is_returning:
            from world.recruit_manager import get_recruit_manager
            snap = get_recruit_manager().dismissed_characters.get(self.recruit.recruit_id)
            if snap and snap.get("level"):
                lvl = max(lvl, snap["level"])
        return lvl

    @property
    def is_returning(self):
        """True if this recruit was previously hired-then-dismissed, i.e.
        already knows the player. Read live rather than cached at
        __init__, matching the quest_mgr live-property pattern elsewhere
        in this codebase - dismissing someone mid-session and walking
        straight back up to them should show the welcome-back line
        immediately, not the stale first-meeting one."""
        from world.recruit_manager import get_recruit_manager
        return get_recruit_manager().is_dismissed(self.recruit.recruit_id)

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        mouse_pos = event.pos

        if self.close_button.collidepoint(mouse_pos):
            self.state_manager.transition_to(GameState.OVERWORLD)
            return

        if self.joined:
            return  # already resolved, only Close does anything now

        if self.join_button.collidepoint(mouse_pos):
            if self.block_reason:
                return          # too far above the player; the reason is on screen
            self._do_recruit()
            return

        if self.leave_button.collidepoint(mouse_pos):
            self.state_manager.transition_to(GameState.OVERWORLD)
            return

    def _do_recruit(self):
        """The actual recruitment - moved here from overworld_screen's old
        _recruit_companion so the join action only fires after the player
        has seen the greeting and chosen Join, not on first Space press."""
        from world.recruit_manager import get_recruit_manager

        manager = get_recruit_manager()
        returning = manager.is_dismissed(self.recruit.recruit_id)

        party = self.state_manager.get_party()
        # Checked again here rather than trusting the button: _do_recruit is the
        # only place a companion actually joins, so it is the only place the
        # rule is guaranteed to hold however the screen is driven.
        if self.recruit.recruit_block_reason(self._player_level):
            return
        character = manager.build_or_restore(self.recruit, self._player_level)
        placement = party.add_member(character)
        manager.mark_recruited(self.recruit.recruit_id)

        where = "joins your party" if placement == "active" else "waits on standby"
        verb = "rejoins you and" if returning else ""
        self.result_message = (
            f"{self.recruit.name} ({self.recruit.char_class}) "
            f"{verb} {where}!").replace("  ", " ")
        self.joined = True

    def render(self, screen):
        screen.fill((10, 10, 15))

        self.renderer.draw_text(screen, self.recruit.name, (40, 30), size="large", color=COLOR_GOLD)
        self.renderer.draw_text(
            screen, f"Level {self.shown_level} {self.recruit.char_class}", (40, 68),
            color=(180, 180, 190))

        if self.joined:
            self._render_joined(screen)
        else:
            self._render_greeting(screen)

        self.renderer.draw_button(screen, self.close_button, "Close")

    def _render_greeting(self, screen):
        if self.is_returning:
            line = (self.recruit.greeting
                     or f"{self.recruit.name} looks glad to see you again.")
            # A returning companion greets you as someone who already
            # knows you, not a stranger - prefixed distinctly from their
            # first-meeting line rather than repeating it verbatim.
            line = f"\"Back again? Good. Let's move.\" {line}".strip()
        else:
            line = self.recruit.greeting or f"{self.recruit.name} looks you over."

        portrait = get_recruit_portrait(self.recruit.recruit_id, 200)
        text_w = SCREEN_WIDTH - 80
        if portrait is not None:
            screen.blit(portrait, (SCREEN_WIDTH - 40 - portrait.get_width(), 20))
            text_w -= portrait.get_width() + 20

        self._draw_wrapped_text(screen, line, (40, 100), max_width=text_w)

        if self.recruit.backstory:
            self._draw_wrapped_text(screen, self.recruit.backstory, (40, 220),
                                     max_width=SCREEN_WIDTH - 80, color=(170, 170, 170))

        # Somebody too far above the player is shown WHY and at what level they
        # will come, rather than a Recruit button that silently does nothing.
        reason = self.block_reason
        if reason:
            self._draw_wrapped_text(screen, reason, (40, SCREEN_HEIGHT - 150),
                                     max_width=SCREEN_WIDTH - 80, color=(230, 140, 120))
            self.renderer.draw_button(screen, self.join_button, "Too Low", color=(70, 60, 60))
        else:
            self.renderer.draw_button(screen, self.join_button, "Recruit")
        self.renderer.draw_button(screen, self.leave_button, "Not Now")

    def _render_joined(self, screen):
        self._draw_wrapped_text(screen, self.result_message or "", (40, 100),
                                 max_width=SCREEN_WIDTH - 80, color=(120, 240, 140))

    def _draw_wrapped_text(self, screen, text, pos, max_width, color=COLOR_WHITE, line_height=26):
        """Simple word-wrap for dialog text - copied from
        QuestDialogScreen rather than sharing via inheritance, since the
        two screens have otherwise-unrelated conversation flows and this
        helper is small and self-contained."""
        if not text:
            return
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            width = self.renderer.font_normal.size(test)[0]
            if width > max_width and current:
                lines.append(current)
                current = word
            else:
                current = test
        if current:
            lines.append(current)

        x, y = pos
        for line in lines:
            self.renderer.draw_text(screen, line, (x, y), color=color)
            y += line_height
