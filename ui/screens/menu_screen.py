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
        slot_height = 56
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
            if self.slot_close_button.collidepoint(mouse_pos):
                self.slot_mode = None
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
            if self.state_manager.save_game(filename):
                self._notify(f"Saved to slot {slot_number}.", (140, 230, 160))
                self.slot_mode = None
            else:
                self._notify("Save failed.", (230, 140, 140))
    
    def update(self, dt):
        """Tick down the transient save/load message, and drive the vista."""
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

        pygame.draw.rect(screen, (70, 60, 40), self.slot_close_button)
        pygame.draw.rect(screen, (200, 180, 120), self.slot_close_button, 2)
        close_text = self.renderer.font_normal.render("Close", True, (255, 240, 200))
        screen.blit(close_text, close_text.get_rect(center=self.slot_close_button.center))

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
                screen, label, (rect.x + 14, rect.y + 8),
                color=(220, 200, 140), font_size=16)

            body = summary if occupied else "Empty"
            body_color = (210, 210, 215) if occupied else (120, 120, 128)
            self.renderer.draw_text(
                screen, body, (rect.x + 14, rect.y + 30),
                color=body_color, font_size=14)

        if self.message:
            self.renderer.draw_text(
                screen, self.message, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60),
                color=self.message_color, center=True)
