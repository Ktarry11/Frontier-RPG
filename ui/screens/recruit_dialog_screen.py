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

        # FRIENDSHIP (world/bond_manager.py). Only recruits with a record in data/npcs/bonds.json
        # get the stage text, reply moments and the talk view; everyone else is unchanged.
        from world.bond_manager import get_bond_manager
        self.bonds = get_bond_manager()
        self.bond = self.bonds.get(recruit.recruit_id)
        self.reply = None               # what they said back to your last choice
        self.option_rects = []          # [(moment_id, index, rect)]
        self.stay_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 90, 200, 50)

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
        from world.recruit_manager import get_recruit_manager
        return get_recruit_manager().block_reason(self.recruit, self._player_level)

    @property
    def shown_level(self):
        """The level they will actually join at.

        The same catch-up level whether this is a first meeting or a return:
        somebody the player dismissed has been living their own life, not
        waiting in a doorway, so they come back having kept pace. If they left
        ABOVE the catch-up level they keep their own, which is why this is a
        max rather than a straight substitution.
        """
        from world.recruit_manager import get_recruit_manager
        return get_recruit_manager().join_level(self.recruit, self._player_level)

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

    @property
    def in_party(self):
        from world.recruit_manager import get_recruit_manager
        return get_recruit_manager().is_recruited(self.recruit.recruit_id)

    def _moment(self):
        """The reply moment on screen now, if any."""
        if self.bond is None or self.reply is not None:
            return None
        if self.in_party:
            return self.bonds.talk_moment(self.recruit.recruit_id)
        return self.bonds.hire_moment(self.recruit.recruit_id)

    def _bond_click(self, pos):
        """Clicks that belong to the friendship view. True if one was handled."""
        rid = self.recruit.recruit_id
        for moment_id, index, rect in self.option_rects:
            if rect.collidepoint(pos):
                reply, joins, _stays = self.bonds.answer(rid, moment_id, index)
                self.reply = reply
                moment = next((m for m in self.bond.data.get("moments", []) if m["id"] == moment_id), {})
                if moment.get("when") == "hire" and joins:
                    self._do_recruit()
                    self.result_message = f"\"{reply}\"  {self.result_message or ''}".strip()
                return True
        if self.in_party and self.stay_button.collidepoint(pos) and self._can_ask_to_stay():
            self.bonds.ask_to_stay(rid)
            self.reply = self.bonds.line(rid, "asked_to_stay")
            return True
        return False

    def _can_ask_to_stay(self):
        b = self.bond
        return bool(b and b.in_party and not b.asked_this_stint and not b.angry
                    and (b.warned or b.leave_cause))

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        mouse_pos = event.pos

        if self.bond is not None and not self.joined and self._bond_click(mouse_pos):
            return
        if self.bond is not None and (self.in_party or self._moment() is not None):
            # talking to a party member, or a question waiting for an answer: no Recruit button
            if self.close_button.collidepoint(mouse_pos):
                self.state_manager.transition_to(GameState.OVERWORLD if not self.in_party
                                                 else GameState.PARTY)
            return

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
        if manager.block_reason(self.recruit, self._player_level):
            return
        if self.bond is not None:
            ok, _why = self.bonds.can_hire(self.recruit.recruit_id)
            if not ok:
                return
            self.bonds.heard_walkout_talk(self.recruit.recruit_id)
        character = manager.build_or_restore(self.recruit, self._player_level)
        placement = party.add_member(character)
        manager.mark_recruited(self.recruit.recruit_id)
        if self.bond is not None:
            self.bonds.on_joined(self.recruit.recruit_id)

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
        elif self.bond is not None:
            self._render_bond(screen)
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

    def _render_bond(self, screen):
        """The friendship view: what they've told you so far, and any reply waiting to be made."""
        from world.bond_manager import STAGE_NAMES
        rid = self.recruit.recruit_id
        b = self.bond
        self.option_rects = []
        portrait = get_recruit_portrait(rid, 200)
        text_w = SCREEN_WIDTH - 80
        if portrait is not None:
            screen.blit(portrait, (SCREEN_WIDTH - 40 - portrait.get_width(), 20))
            text_w -= portrait.get_width() + 20

        stage = STAGE_NAMES[b.stage_key]
        status = stage if not self.in_party else f"{stage}. {self.bonds.mood_line(rid)}"
        self.renderer.draw_text(screen, status, (40, 96), color=(150, 200, 160))
        y = 130

        ok, why = self.bonds.can_hire(rid)
        talk = None if self.in_party else self.bonds.walkout_talk(rid)
        if not self.in_party and not ok:
            y = self._draw_wrapped_text(screen, why or f"{self.recruit.name} isn't ready to talk "
                                        "to you again yet. Come back after you've been out and "
                                        "done something.", (40, y), max_width=text_w)
        elif talk:
            y = self._draw_wrapped_text(screen, f"\"{talk}\"", (40, y), max_width=text_w)
        else:
            learned = self.bonds.learned(rid)
            # earlier stages in grey, the newest in white: you learn more as you go
            for name, text in learned[:-1][-2:]:
                y = self._draw_wrapped_text(screen, f"\"{text}\"", (40, y), max_width=text_w,
                                            color=(150, 150, 160), line_height=22)
                y += 8
            if learned:
                y = self._draw_wrapped_text(screen, f"\"{learned[-1][1]}\"", (40, y),
                                            max_width=text_w)
        y += 16

        moment = self._moment() if ok or self.in_party else None
        if self.reply is not None:
            y = self._draw_wrapped_text(screen, f"\"{self.reply}\"", (40, y),
                                        max_width=text_w, color=(240, 220, 140))
        elif moment is not None:
            if moment.get("line"):
                y = self._draw_wrapped_text(screen, f"\"{moment['line']}\"", (40, y),
                                            max_width=text_w, color=(240, 220, 140))
            y = self._draw_wrapped_text(screen, moment.get("prompt", ""), (40, y + 4),
                                        max_width=text_w, color=(170, 170, 180))
            y += 8
            for i, o in enumerate(moment["options"]):
                rect = pygame.Rect(60, y, min(text_w, 900), 34)
                self.renderer.draw_button(screen, rect, o["text"])
                self.option_rects.append((moment["id"], i, rect))
                y += 42

        if self.in_party:
            if self._can_ask_to_stay() and self.reply is None:
                self.renderer.draw_button(screen, self.stay_button, "Ask them to stay")
            return
        if moment is None and ok:
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
            return pos[1]
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
        return y
