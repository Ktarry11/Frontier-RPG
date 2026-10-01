"""
Earthen Guardian toggle screen (Shaman Tank). Same shared-screen pattern as
PetScreen/TotemScreen/FormScreen - character is set by whatever transitions
here (overworld_screen.py), and the real logic lives entirely in
Character.toggle_guardian_stance() / combat/guardian_stance.py. This screen
is just a thin visual wrapper around that one call, since Earthen Guardian
is a single on/off toggle rather than a multi-form picker like FormScreen.

PERSISTENT per the same rule as shapeshift forms: toggling here stays in
effect across multiple fights until the player explicitly toggles it off.
"""
import pygame
from ui.screens.base_screen import BaseScreen
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_GOLD, COLOR_GREEN, COLOR_RED, COLOR_DARK_GRAY


class GuardianScreen(BaseScreen):
    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.character = None
        self._toggle_rect = None
        self._message = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._back()
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._toggle_rect and self._toggle_rect.collidepoint(event.pos):
                self._toggle()
                return

    def _back(self):
        from core.game_states import GameState
        self.state_manager.transition_to(GameState.OVERWORLD)

    def _toggle(self):
        if self.character is None:
            return
        success, msg = self.character.toggle_guardian_stance()
        self._message = (msg, COLOR_GREEN if success else COLOR_RED)

    def render(self, screen):
        screen.fill((15, 15, 20))
        char = self.character or getattr(self.state_manager, "player", None)

        self.renderer.draw_text(screen, "Earthen Guardian", (40, 30), size="large", color=COLOR_GOLD)
        self.renderer.draw_text(
            screen, "ESC to go back - this stance is persistent and stays active across fights",
            (40, 65), font_size=14, color=COLOR_DARK_GRAY)

        if char is None:
            self.renderer.draw_text(screen, "No character selected.", (40, 100), color=COLOR_RED)
            return

        if char.char_class != "Shaman":
            self.renderer.draw_text(
                screen, f"{char.char_class}s cannot use Earthen Guardian.", (40, 100), color=COLOR_RED)
            return

        from combat.guardian_stance import get_guardian_stance
        stance = get_guardian_stance()

        active = getattr(char, "guardian_stance_active", False)
        unlocked = char.level >= stance["level_req"]

        y = 110
        rect = pygame.Rect(40, y, SCREEN_WIDTH - 80, 90)

        if active:
            bg, border = (60, 50, 20), COLOR_GOLD
        elif unlocked:
            bg, border = (28, 28, 36), COLOR_WHITE
        else:
            bg, border = (18, 18, 18), (50, 50, 50)

        pygame.draw.rect(screen, bg, rect)
        pygame.draw.rect(screen, border, rect, 2 if active else 1)

        name_color = COLOR_WHITE if unlocked else (100, 100, 100)
        self.renderer.draw_text(screen, stance["name"], (rect.x + 15, rect.y + 10),
                                color=name_color, font_size=18)
        self.renderer.draw_text(screen, stance["description"], (rect.x + 15, rect.y + 38),
                                color=COLOR_DARK_GRAY, font_size=13)

        if not unlocked:
            self.renderer.draw_text(screen, f"Requires level {stance['level_req']}",
                                    (rect.right - 190, rect.y + 10), color=COLOR_RED, font_size=14)
            self._toggle_rect = None
        elif active:
            self.renderer.draw_text(screen, "Drop Stance", (rect.right - 150, rect.y + 10),
                                    color=COLOR_RED, font_size=14)
            self._toggle_rect = rect
        else:
            cost = stance["activation_cost"]
            self.renderer.draw_text(screen, f"Activate ({cost} Mana)", (rect.right - 180, rect.y + 10),
                                    color=COLOR_GREEN, font_size=14)
            self._toggle_rect = rect

        y += 100
        self.renderer.draw_text(screen, "Status: Active" if active else "Status: Inactive",
                                (40, y), color=COLOR_GOLD if active else COLOR_DARK_GRAY, font_size=14)

        if self._message:
            msg, color = self._message
            self.renderer.draw_text(screen, msg, (40, y + 30), color=color, font_size=14)
