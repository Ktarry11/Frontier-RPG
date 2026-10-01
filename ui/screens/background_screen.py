"""
Background Screen - full-screen 4-tab companion lore view.

Per Kyle: a real "Background" button opening a sub-menu with tabs for a
companion's life Before the integration, their Adjustment immediately
after (how they got used to the world shifting), how they are Now, and
what they want moving Forward - since companions are meant to read as
real fleshed-out people, not flavor-text NPCs.

Data lives on Character.background_sections (see entities/character.py's
get_background_section - "now" falls back to the existing flat
self.backstory when not explicitly written, so every companion authored
before this screen existed already has real content under the "Now" tab
on day one).
"""
import pygame
from core.game_states import GameState
from ui.screens.base_screen import BaseScreen
from ui.renderer import Renderer
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_GOLD, COLOR_DARK_GRAY


class BackgroundScreen(BaseScreen):
    """Full-screen 4-tab lore reader for one companion at a time."""

    PANEL_X = 80
    PANEL_Y = 140
    PANEL_WIDTH = SCREEN_WIDTH - 160
    PANEL_HEIGHT = SCREEN_HEIGHT - 260

    TAB_WIDTH = 180
    TAB_HEIGHT = 44
    TAB_GAP = 8

    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.renderer = Renderer()
        self.character = None
        self.return_state = GameState.PARTY
        self.active_tab = "before"
        self._tab_rects = []

    def set_subject(self, character, return_state=None):
        self.character = character
        self.active_tab = "before"
        if return_state is not None:
            self.return_state = return_state

    def _close(self):
        self.state_manager.transition_to(self.return_state or GameState.PARTY)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._close()
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            close_rect = pygame.Rect(SCREEN_WIDTH - 120, 20, 100, 40)
            if close_rect.collidepoint(event.pos):
                self._close()
                return
            for key, rect in self._tab_rects:
                if rect.collidepoint(event.pos):
                    self.active_tab = key
                    return

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill((18, 18, 24))

        if self.character is None:
            msg = "No companion selected."
            self.renderer.draw_text(screen, msg,
                (SCREEN_WIDTH // 2 - self.renderer.font_normal.size(msg)[0] // 2, SCREEN_HEIGHT // 2),
                color=COLOR_DARK_GRAY)
            return

        title = f"{self.character.name}'s Background"
        self.renderer.draw_text(
            screen, title,
            (SCREEN_WIDTH // 2 - self.renderer.font_large.size(title)[0] // 2, 30),
            color=(200, 200, 100), size="large")

        close_rect = pygame.Rect(SCREEN_WIDTH - 120, 20, 100, 40)
        self.renderer.draw_button(screen, close_rect, "Close (Esc)")

        self._render_tabs(screen)
        self._render_content(screen)

    def _render_tabs(self, screen):
        self._tab_rects = []
        from entities.character import Character
        keys = Character.BACKGROUND_SECTION_KEYS
        labels = Character.BACKGROUND_SECTION_LABELS

        total_w = len(keys) * self.TAB_WIDTH + (len(keys) - 1) * self.TAB_GAP
        start_x = SCREEN_WIDTH // 2 - total_w // 2
        y = self.PANEL_Y - self.TAB_HEIGHT - 12

        for i, key in enumerate(keys):
            rect = pygame.Rect(start_x + i * (self.TAB_WIDTH + self.TAB_GAP), y,
                               self.TAB_WIDTH, self.TAB_HEIGHT)
            is_active = key == self.active_tab
            has_content = bool(self.character.get_background_section(key))
            color = (40, 60, 90) if is_active else (32, 32, 40)
            text_color = COLOR_GOLD if is_active else (COLOR_WHITE if has_content else COLOR_DARK_GRAY)
            self.renderer.draw_button(screen, rect, labels[key], color=color, text_color=text_color)
            self._tab_rects.append((key, rect))

    def _render_content(self, screen):
        panel = pygame.Rect(self.PANEL_X, self.PANEL_Y, self.PANEL_WIDTH, self.PANEL_HEIGHT)
        pygame.draw.rect(screen, (28, 28, 36), panel)
        pygame.draw.rect(screen, (70, 70, 85), panel, 2)

        text = self.character.get_background_section(self.active_tab)
        if not text:
            placeholder = "Not yet written."
            self.renderer.draw_text(screen, placeholder,
                                    (panel.x + 24, panel.y + 24),
                                    font_size=16, color=COLOR_DARK_GRAY)
            return

        self._draw_wrapped(screen, text, panel.x + 24, panel.y + 24, panel.width - 48)

    def _draw_wrapped(self, screen, text, x, y, max_width, font_size=17, line_height=26, color=COLOR_WHITE):
        """Real word wrap, measured and drawn with the SAME font (the
        exact bug this screen exists partly to avoid repeating - see
        party_screen.py's _draw_wrapped fix from this same session, where
        measuring against one font and drawing with another silently
        resolved to the wrong font entirely and ran text off the panel).
        Paragraphs (blank-line-separated in the source text) get extra
        vertical space between them so longer background pieces don't
        read as one dense wall of text.
        """
        font = self.renderer._get_font(font_size=font_size)
        paragraphs = text.split("\n\n") if "\n\n" in text else [text]
        for para in paragraphs:
            words = para.split()
            line = ""
            for word in words:
                candidate = f"{line} {word}".strip()
                if font.size(candidate)[0] > max_width and line:
                    self.renderer.draw_text(screen, line, (x, y), font_size=font_size, color=color)
                    y += line_height
                    line = word
                else:
                    line = candidate
            if line:
                self.renderer.draw_text(screen, line, (x, y), font_size=font_size, color=color)
                y += line_height
            y += 14  # paragraph gap
        return y
