"""
Main menu screen.
"""
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_PADDING
from config import (COLOR_WHITE, COLOR_DARK_GRAY, SAVE_SLOT_COUNT, SAVE_SLOT_COLUMNS,
                    save_slot_filename)
from core.game_states import GameState
from ui.screens.base_screen import BaseScreen


class MenuScreen(BaseScreen):
    """Main menu."""
    
    def __init__(self, state_manager):
        super().__init__(state_manager)
        
        # Button positions
        button_y_start = SCREEN_HEIGHT // 2 - (BUTTON_HEIGHT * 1.5)
        self.buttons = {
            "new_game": pygame.Rect(
                SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
                button_y_start,
                BUTTON_WIDTH,
                BUTTON_HEIGHT
            ),
            "load_game": pygame.Rect(
                SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
                button_y_start + BUTTON_HEIGHT + BUTTON_PADDING,
                BUTTON_WIDTH,
                BUTTON_HEIGHT
            ),
            "quit": pygame.Rect(
                SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
                button_y_start + (BUTTON_HEIGHT + BUTTON_PADDING) * 2,
                BUTTON_WIDTH,
                BUTTON_HEIGHT
            ),
        }
        
        # Save Game sits below Quit and only appears once there's a character
        # to save. It shares the column so the menu stays a single stack.
        self.buttons["save_game"] = pygame.Rect(
            SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
            button_y_start + (BUTTON_HEIGHT + BUTTON_PADDING) * 3,
            BUTTON_WIDTH,
            BUTTON_HEIGHT
        )

        # Back button (only show if not on main menu from start)
        self.back_button = pygame.Rect(20, 20, 100, 50)

        # Transient feedback for save/load results.
        self.message = None
        self.message_color = COLOR_WHITE
        self.message_timer = 0.0

        # Slot picker sub-view. "load_game"/"save_game" no longer act
        # immediately on click - they open this picker instead, so
        # Kyle's playtesters can run multiple characters/saves side by
        # side without one overwriting another (Kyle, 2026-09-06:
        # "improve save slots from 1 to 5"). slot_mode is None (normal
        # menu), "load", or "save"; slot_rects/slot_close_button are
        # only built (see _build_slot_rects) when the picker opens, not
        # up front, since SAVE_SLOT_COUNT-driven layout only matters
        # while the picker is actually on screen.
        self.slot_mode = None
        self.slot_rects = []
        self.slot_close_button = pygame.Rect(SCREEN_WIDTH - 140, 20, 110, 40)

        #: Overwrite confirmation. Kyle, 7 Nov: "If the player is trying to
        #: override a current save there needs to be a notice and
        #: conformation." Clicking an OCCUPIED slot in save mode arms this
        #: with (slot_number, summary) and writes nothing until the player
        #: confirms; an empty slot is still a single click, because there is
        #: nothing to lose and a confirm on every save is just friction.
        self.pending_overwrite = None

        #: Delete confirmation, armed by the small X on an occupied slot.
        #: Kyle, 7 Nov: "ability to delete a character. Obviously delete will
        #: require confirmation." Held separately from pending_overwrite so
        #: the two prompts can never be confused for one another - they ask
        #: different questions and one of them is not undoable.
        self.pending_delete = None
        #: Per-slot delete hitboxes, rebuilt with the grid.
        self.slot_delete_rects = {}

        self.confirm_yes_button = pygame.Rect(
            SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT // 2 + 40, 140, 46)
        self.confirm_no_button = pygame.Rect(
            SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT // 2 + 40, 140, 46)

        #: True while the picker is open for a character that has never been
        #: saved. Close is hidden in this mode - backing out would leave a
        #: character alive with nowhere to save, which is how progress gets
        #: lost quietly rather than loudly.
        self.slot_required = False

        #: Parallax Valley of Trials vista behind the menu, and the New Game
        #: push-in (ui/parallax.py). Built here rather than as a replacement
        #: TitleScreen deliberately: all the save-slot handling above is real,
        #: load-bearing and already debugged once this week, and a new screen
        #: would have had to grow its own copy of it.
        from ui.parallax import ParallaxBackdrop
        self.backdrop = ParallaxBackdrop()


    def _build_slot_rects(self):
        """One clickable Rect per save slot, stacked in a column centered
        on screen. Rebuilt each time the picker opens rather than cached
        in __init__ - SAVE_SLOT_COUNT is expected to stay constant at
        runtime, but rebuilding is cheap and keeps this robust if that
        ever changes."""
        cols = max(1, SAVE_SLOT_COLUMNS)
        rows = -(-SAVE_SLOT_COUNT // cols)          # ceil, so a partial last row still fits
        slot_height = 60
        gap = 12
        # Width comes from the column count rather than a fixed number, so the
        # picker stays on screen if the slot count or the columns ever change.
        margin = 50
        slot_width = (SCREEN_WIDTH - 2 * margin - (cols - 1) * gap) // cols
        grid_w = cols * slot_width + (cols - 1) * gap
        grid_h = rows * slot_height + (rows - 1) * gap
        start_x = SCREEN_WIDTH // 2 - grid_w // 2
        start_y = SCREEN_HEIGHT // 2 - grid_h // 2 + 20   # clear of the title
        rects = []
        for i in range(SAVE_SLOT_COUNT):
            c, r = i % cols, i // cols
            rects.append(pygame.Rect(
                start_x + c * (slot_width + gap),
                start_y + r * (slot_height + gap),
                slot_width,
                slot_height,
            ))
        return rects

    def _notify(self, text, color=COLOR_WHITE):
        self.message = text
        self.message_color = color
        self.message_timer = 3.0
    
    def handle_event(self, event):
        """Handle menu button clicks."""
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        mouse_pos = event.pos

        # Slot picker takes over input entirely while open - closing it
        # (via its own Close button) is the only way out other than
        # picking a slot, same modal convention every other overlay
        # screen in this game uses (quest dialog, journal, etc).
        if self.slot_mode is not None:
            # The confirmation is modal on top of the picker: while it is up
            # the slots underneath must not be clickable, or a stray click
            # lands on a different slot than the one being confirmed.
            if self.pending_overwrite is not None:
                if self.confirm_yes_button.collidepoint(mouse_pos):
                    slot_number = self.pending_overwrite[0]
                    self.pending_overwrite = None
                    self._write_slot(slot_number)
                elif self.confirm_no_button.collidepoint(mouse_pos):
                    self.pending_overwrite = None
                return
            if self.pending_delete is not None:
                if self.confirm_yes_button.collidepoint(mouse_pos):
                    slot_number, _summary = self.pending_delete
                    self.pending_delete = None
                    if self.state_manager.delete_save(save_slot_filename(slot_number)):
                        self._notify(f"Slot {slot_number} deleted.", (230, 180, 150))
                    else:
                        self._notify(f"Slot {slot_number} could not be deleted.",
                                     (230, 140, 140))
                elif self.confirm_no_button.collidepoint(mouse_pos):
                    self.pending_delete = None
                return
            if not self.slot_required and self.slot_close_button.collidepoint(mouse_pos):
                self.slot_mode = None
                return
            # The delete X is checked BEFORE the slot body it sits inside,
            # or the slot's own click would always win and the X would be
            # dead - and in load mode it would load the save instead.
            for slot_number, del_rect in self.slot_delete_rects.items():
                if del_rect.collidepoint(mouse_pos):
                    summary = self.state_manager.describe_save(
                        save_slot_filename(slot_number))
                    if summary:
                        self.pending_delete = (slot_number, summary)
                    return
            for i, rect in enumerate(self.slot_rects):
                if rect.collidepoint(mouse_pos):
                    self._handle_slot_click(i + 1)
                    return
            return

        # Back button - only active if there's a player to return to
        if self.state_manager.player and self.back_button.collidepoint(mouse_pos):
            self.state_manager.transition_to(GameState.OVERWORLD)
            return

        if self.buttons["new_game"].collidepoint(mouse_pos):
            # Forget the slot we were playing BEFORE creation starts, so the
            # new character cannot inherit it and cannot write to it. See
            # GameStateManager.begin_new_character.
            self.state_manager.begin_new_character()
            # Straight through. Kyle, 5 Nov: "no zoom in with white flash on
            # new game either" - the dolly came apart in motion, so it is gone
            # along with the bloom that handed off from it.
            self.state_manager.transition_to(GameState.CHARACTER_CREATION)
        elif self.buttons["load_game"].collidepoint(mouse_pos):
            self.slot_mode = "load"
            self.slot_rects = self._build_slot_rects()
        elif (self.state_manager.player
              and self.buttons["save_game"].collidepoint(mouse_pos)):
            self.slot_mode = "save"
            self.slot_rects = self._build_slot_rects()
        elif self.buttons["quit"].collidepoint(mouse_pos):
            self.state_manager.transition_to(GameState.QUIT)

    def _render_title_text(self, screen, alpha):
        """The logo, with a drop shadow so it survives a bright sunset.

        Rendered to its own surface and blitted with alpha rather than drawn
        with a faded colour: fading the colour toward the background only
        works on a background that holds still, and this one is moving and
        changing brightness underneath the text the whole time.
        """
        if alpha <= 0:
            return
        title = "FRONTIER RPG"
        font = self.renderer.font_large
        shadow = font.render(title, True, (20, 8, 4))
        body = font.render(title, True, (255, 232, 196))

        layer = pygame.Surface(
            (body.get_width() + 6, body.get_height() + 6), pygame.SRCALPHA)
        layer.blit(shadow, (4, 4))
        layer.blit(body, (0, 0))
        layer.set_alpha(max(0, min(255, int(alpha))))
        screen.blit(layer, (SCREEN_WIDTH // 2 - layer.get_width() // 2, 86))

    def _handle_slot_click(self, slot_number):
        """Save into or load from the clicked slot number (1-indexed),
        per whichever mode (self.slot_mode) opened the picker."""
        filename = save_slot_filename(slot_number)
        if self.slot_mode == "load":
            if not self.state_manager.has_save(filename):
                self._notify(f"Slot {slot_number} is empty.", (230, 140, 140))
                return
            if self.state_manager.load_game(filename):
                self.slot_mode = None
                self.state_manager.transition_to(GameState.OVERWORLD)
            else:
                self._notify(f"Slot {slot_number} could not be loaded.", (230, 140, 140))
        elif self.slot_mode == "save":
            # An occupied slot asks first. Reading the summary here rather
            # than trusting has_save means the prompt can NAME what is about
            # to be destroyed - "Slot 8 already has Stone Hoof - Level 13
            # Druid" is a warning; "Overwrite?" is a dialog box.
            summary = self.state_manager.describe_save(filename)
            if summary:
                self.pending_overwrite = (slot_number, summary)
                return
            self._write_slot(slot_number)

    def _write_slot(self, slot_number):
        """Actually commit to a slot. Only reached past any confirmation."""
        filename = save_slot_filename(slot_number)
        if self.state_manager.save_game(filename):
            self._notify(f"Saved to slot {slot_number}.", (140, 230, 160))
            self.slot_mode = None
            # A brand-new character has just been given a home, so the world
            # can be entered. This is the only path into OVERWORLD from
            # creation now - see character_screen's note.
            if self.slot_required:
                self.slot_required = False
                self.state_manager.pending_new_character = False
                self.state_manager.transition_to(GameState.OVERWORLD)
        else:
            self._notify("Save failed.", (230, 140, 140))
    
    def update(self, dt):
        """Tick down the transient save/load message, and drive the vista."""
        # A character that has just been created arrives here with no slot.
        # Open the picker on its behalf and keep it open until they choose.
        if getattr(self.state_manager, "pending_new_character", False) \
                and self.slot_mode is None:
            self.slot_mode = "save"
            self.slot_required = True
            self.slot_rects = self._build_slot_rects()
            self._notify("Choose a slot for your new character.", (230, 220, 150))

        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = None

        self.backdrop.update(dt)
    
    def render(self, screen):
        """Draw menu."""
        # Vista first, under everything, including the slot picker - the
        # picker used to sit on a flat fill and would look like a different
        # application next to the title.
        self.backdrop.draw(screen)

        if self.slot_mode is not None:
            # Darken behind the picker so slot text stays readable over a
            # bright sunset.
            scrim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            scrim.fill((6, 4, 10, 200))
            screen.blit(scrim, (0, 0))
            self._render_slot_picker(screen)
            return

        self._render_title_text(screen, 255)
        
        # Back button - only show if there's an active character to return to
        if self.state_manager.player:
            self.renderer.draw_button(screen, self.back_button, "Back")
        
        # Buttons
        self.renderer.draw_button(screen, self.buttons["new_game"], "New Game")

        # Load is greyed out only when EVERY slot is empty, so it reads as
        # unavailable rather than broken - with 5 slots, has_save() on the
        # single default filename is no longer the right check (Kyle,
        # 2026-09-06: multi-slot playtesting).
        has_save = any(
            self.state_manager.has_save(save_slot_filename(i + 1))
            for i in range(SAVE_SLOT_COUNT)
        )
        self.renderer.draw_button(
            screen, self.buttons["load_game"], "Load Game",
            color=COLOR_DARK_GRAY if has_save else (30, 30, 34),
            text_color=COLOR_WHITE if has_save else (110, 110, 118))

        self.renderer.draw_button(screen, self.buttons["quit"], "Quit")

        if self.state_manager.player:
            self.renderer.draw_button(screen, self.buttons["save_game"], "Save Game")

        if self.message:
            self.renderer.draw_text(
                screen, self.message, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60),
                color=self.message_color, center=True)

    def _render_slot_picker(self, screen):
        """5-slot list, each row showing that slot's summary (or 'Empty')
        - lets a player see what they're about to overwrite/load before
        clicking, same "don't make Load a blind click" principle the old
        single-slot summary line had."""
        screen.fill((10, 10, 15))
        title = "Load Game" if self.slot_mode == "load" else "Save Game"
        self.renderer.draw_text(
            screen, title, (SCREEN_WIDTH // 2 - 80, 40),
            color=COLOR_WHITE, size="large")

        # No way out while a new character still needs a home - backing out
        # would leave them alive with nowhere to save.
        if not self.slot_required:
            pygame.draw.rect(screen, (70, 60, 40), self.slot_close_button)
            pygame.draw.rect(screen, (200, 180, 120), self.slot_close_button, 2)
            close_text = self.renderer.font_normal.render("Close", True, (255, 240, 200))
            screen.blit(close_text, close_text.get_rect(center=self.slot_close_button.center))

        # Rebuilt every frame from what is actually on disk. Keeping the old
        # map would leave a clickable X floating over a slot that has just
        # been emptied, and deleting an already-deleted save reads as the
        # button being broken.
        self.slot_delete_rects = {}

        for i, rect in enumerate(self.slot_rects):
            slot_number = i + 1
            filename = save_slot_filename(slot_number)
            summary = self.state_manager.describe_save(filename)
            occupied = summary is not None

            pygame.draw.rect(screen, (30, 30, 38), rect)
            pygame.draw.rect(screen,
                             (140, 120, 70) if occupied else (70, 70, 78),
                             rect, 2)

            label = f"Slot {slot_number}"
            self.renderer.draw_text(
                screen, label, (rect.x + 12, rect.y + 7),
                color=(220, 200, 140), font_size=15)

            # DELETE, on occupied slots only. Top-right of the slot, well
            # clear of the row's centre so a click meant for "load this" does
            # not erase it - and it only ARMS a confirmation, never deletes.
            if occupied:
                del_rect = pygame.Rect(rect.right - 26, rect.y + 6, 20, 20)
                self.slot_delete_rects[slot_number] = del_rect
                pygame.draw.rect(screen, (60, 30, 32), del_rect)
                pygame.draw.rect(screen, (190, 110, 105), del_rect, 1)
                x_text = self.renderer._get_font(font_size=13).render(
                    "X", True, (240, 190, 185))
                screen.blit(x_text, x_text.get_rect(center=del_rect.center))

            body = summary if occupied else "Empty"
            body_color = (210, 210, 215) if occupied else (120, 120, 128)
            # Five columns puts a slot at 226px, so a long summary has to be
            # cut rather than allowed to run into the slot beside it.
            self.renderer.draw_text(
                screen, self._fit(body, rect.width - 24, 13),
                (rect.x + 12, rect.y + 32),
                color=body_color, font_size=13)

        # Drawn last so it sits on top of the grid it is asking about.
        if self.pending_overwrite is not None:
            self._render_confirm(
                screen, self.pending_overwrite,
                f"Overwrite slot {self.pending_overwrite[0]}?",
                "This slot already holds", "Overwrite")
        elif self.pending_delete is not None:
            self._render_confirm(
                screen, self.pending_delete,
                f"Delete slot {self.pending_delete[0]}?",
                "This will permanently erase", "Delete")

    def _fit(self, text, max_px, font_size):
        """Trim `text` with an ellipsis until it fits `max_px`."""
        font = self.renderer._get_font(font_size=font_size)
        if font.size(text)[0] <= max_px:
            return text
        cut = text
        while cut and font.size(cut + "...")[0] > max_px:
            cut = cut[:-1]
        return (cut.rstrip() + "...") if cut else ""

    def _render_confirm(self, screen, pending, heading, lead, verb):
        """Name what is about to be destroyed, and make them say yes.

        Kyle, 7 Nov: "If the player is trying to override a current save
        there needs to be a notice and conformation." And: "ability to
        delete a character. Obviously delete will require confirmation."

        One panel serves both, because they ask the same shape of question
        and the dangerous part is identical: the panel NAMES the save
        rather than asking a generic "Are you sure?". The whole failure
        being fixed here was a character disappearing without anybody being
        told which one.
        """
        slot_number, summary = pending
        panel = pygame.Rect(SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2 - 110, 600, 190)
        scrim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        scrim.fill((4, 3, 6, 215))
        screen.blit(scrim, (0, 0))
        pygame.draw.rect(screen, (26, 22, 28), panel)
        pygame.draw.rect(screen, (210, 150, 90), panel, 3)

        self.renderer.draw_text(
            screen, heading,
            (SCREEN_WIDTH // 2, panel.y + 26),
            color=(255, 210, 150), center=True, size="large")
        self.renderer.draw_text(
            screen, f"{lead}  {summary}",
            (SCREEN_WIDTH // 2, panel.y + 78),
            color=(235, 225, 230), center=True, font_size=16)
        self.renderer.draw_text(
            screen, "This cannot be undone.",
            (SCREEN_WIDTH // 2, panel.y + 104),
            color=(220, 130, 130), center=True, font_size=14)

        for rect, label, fill, edge in (
                (self.confirm_yes_button, verb, (90, 40, 40), (220, 120, 110)),
                (self.confirm_no_button, "Cancel", (40, 44, 52), (170, 180, 200))):
            pygame.draw.rect(screen, fill, rect)
            pygame.draw.rect(screen, edge, rect, 2)
            text = self.renderer.font_normal.render(label, True, (248, 240, 240))
            screen.blit(text, text.get_rect(center=rect.center))

        if self.message:
            self.renderer.draw_text(
                screen, self.message, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60),
                color=self.message_color, center=True)
