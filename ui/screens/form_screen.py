"""
Shapeshift form screen. Druid (Bear/Dire Bear/Cat/Moonkin/Tree of Life) and
Priest (Shadowform) both use this - real WOTLK class differs but the
underlying mechanic (Character.shift_form) is identical either way, same
shared-screen pattern as PetScreen/TotemScreen.

PERSISTENT per Kyle's direction: shifting here stays in effect across
multiple fights until the player explicitly reverts or shifts again -
nothing elsewhere in the engine calls revert_form() automatically.
"""
import pygame
from ui.screens.base_screen import BaseScreen
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_GOLD, COLOR_GREEN, COLOR_RED, COLOR_DARK_GRAY


class FormScreen(BaseScreen):
    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.character = None
        self._row_rects = []

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._back()
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            for rect, callback in self._row_rects:
                if rect.collidepoint(event.pos):
                    callback()
                    return

    def _back(self):
        from core.game_states import GameState
        self.state_manager.transition_to(GameState.OVERWORLD)

    def _pick(self, form_id):
        if self.character is None:
            return
        success, msg = self.character.shift_form(form_id)

    def _revert(self):
        if self.character is None:
            return
        self.character.revert_form()

    def render(self, screen):
        screen.fill((15, 15, 20))
        char = self.character or getattr(self.state_manager, "player", None)

        self.renderer.draw_text(screen, "Shapeshift Forms", (40, 30), size="large", color=COLOR_GOLD)
        self.renderer.draw_text(
            screen, "ESC to go back - forms are persistent and stay active across fights",
            (40, 65), font_size=14, color=COLOR_DARK_GRAY)

        if char is None:
            self.renderer.draw_text(screen, "No character selected.", (40, 100), color=COLOR_RED)
            return

        from combat.forms import FORMS

        class_forms = [(fid, f) for fid, f in FORMS.items() if f["class"] == char.char_class]
        if not class_forms:
            self.renderer.draw_text(
                screen, f"{char.char_class}s have no shapeshift forms.", (40, 100), color=COLOR_RED)
            return

        class_forms.sort(key=lambda pair: pair[1]["level_req"])

        self._row_rects = []
        y = 110

        # Base/Humanoid form row - always available, reverts
        base_rect = pygame.Rect(40, y, SCREEN_WIDTH - 80, 50)
        is_base = char.current_form is None
        bg, border = ((60, 50, 20), COLOR_GOLD) if is_base else ((28, 28, 36), COLOR_WHITE)
        pygame.draw.rect(screen, bg, base_rect)
        pygame.draw.rect(screen, border, base_rect, 2 if is_base else 1)
        self.renderer.draw_text(screen, "Normal Form (Mana)", (base_rect.x + 15, base_rect.y + 8),
                                color=COLOR_WHITE, font_size=16)
        if is_base:
            self.renderer.draw_text(screen, "Active", (base_rect.right - 100, base_rect.y + 8),
                                    color=COLOR_GOLD, font_size=14)
        else:
            self.renderer.draw_text(screen, "Revert", (base_rect.right - 100, base_rect.y + 8),
                                    color=COLOR_GREEN, font_size=14)
            self._row_rects.append((base_rect, self._revert))
        y += 58

        for fid, form in class_forms:
            unlocked = char.can_use_form(fid)
            is_current = char.current_form == fid
            rect = pygame.Rect(40, y, SCREEN_WIDTH - 80, 60)

            if is_current:
                bg, border = (60, 50, 20), COLOR_GOLD
            elif unlocked:
                bg, border = (28, 28, 36), COLOR_WHITE
            else:
                bg, border = (18, 18, 18), (50, 50, 50)

            pygame.draw.rect(screen, bg, rect)
            pygame.draw.rect(screen, border, rect, 2 if is_current else 1)

            name_color = COLOR_WHITE if unlocked else (100, 100, 100)
            self.renderer.draw_text(screen, form["name"], (rect.x + 15, rect.y + 8),
                                    color=name_color, font_size=16)
            self.renderer.draw_text(screen, form["description"], (rect.x + 15, rect.y + 32),
                                    color=COLOR_DARK_GRAY, font_size=12)

            if not unlocked:
                self.renderer.draw_text(screen, f"Requires level {form['level_req']}",
                                        (rect.right - 180, rect.y + 8), color=COLOR_RED, font_size=14)
            elif is_current:
                self.renderer.draw_text(screen, "Active", (rect.right - 100, rect.y + 8),
                                        color=COLOR_GOLD, font_size=14)
            else:
                self.renderer.draw_text(screen, "Shift", (rect.right - 100, rect.y + 8),
                                        color=COLOR_GREEN, font_size=14)
                self._row_rects.append((rect, lambda f=fid: self._pick(f)))

            y += 68
