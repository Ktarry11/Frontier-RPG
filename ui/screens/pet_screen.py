"""
Pet summon screen. Shared by Hunter (taming) and Warlock (summoning) - both
just show a different filtered list from combat/pet_templates.py, per
entities/pet.py's design note that acquisition flavor differs but the
underlying mechanic (Character.summon_pet) is identical either way.

Real WoW treats pet summon/tame as an out-of-combat action, so this is a
standalone screen (like Talents or the Character Sheet) rather than a
combat-panel widget - there's no need to fight for hotbar/combat-screen
space for something you do between fights, not mid-turn.
"""
import pygame
from ui.renderer import Renderer
from ui.screens.base_screen import BaseScreen
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_GOLD, COLOR_GREEN, COLOR_RED, COLOR_DARK_GRAY


class PetScreen(BaseScreen):
    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.character = None  # set by whatever transitions here (party screen, overworld)
        self._row_rects = []

    def _pet_type_for_class(self, char_class):
        if char_class == "Hunter":
            return "hunter"
        if char_class == "Warlock":
            return "warlock"
        return None

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

    def _pick(self, template_id):
        if self.character is None:
            return
        success, result = self.character.summon_pet(template_id)
        if success:
            self._back()
        # On failure, result is an error string - stay on this screen so
        # the (should-be-impossible-via-UI, but now actually enforced)
        # rejection is visible rather than silently doing nothing.

    def render(self, screen):
        screen.fill((15, 15, 20))
        char = self.character or getattr(self.state_manager, "player", None)

        self.renderer.draw_text(screen, "Summon a Pet", (40, 30), size="large", color=COLOR_GOLD)
        self.renderer.draw_text(screen, "ESC to go back", (40, 65), font_size=14, color=COLOR_DARK_GRAY)

        if char is None:
            self.renderer.draw_text(screen, "No character selected.", (40, 100), color=COLOR_RED)
            return

        pet_type = self._pet_type_for_class(char.char_class)
        if pet_type is None:
            self.renderer.draw_text(
                screen, f"{char.char_class}s cannot summon pets.", (40, 100), color=COLOR_RED)
            return

        from combat.pet_templates import pets_for_class, PET_TEMPLATES
        available = pets_for_class(pet_type, char.level)
        available_ids = {tid for tid, _ in available}

        if char.active_pet is not None:
            self.renderer.draw_text(
                screen, f"Current pet: {char.active_pet.name}", (40, 95),
                color=COLOR_GREEN, font_size=16)

        self._row_rects = []
        y = 140
        row_h = 60
        all_for_class = [(tid, t) for tid, t in PET_TEMPLATES.items() if t["pet_type"] == pet_type]
        all_for_class.sort(key=lambda pair: pair[1].get("level_req", 1))

        for tid, template in all_for_class:
            unlocked = tid in available_ids
            rect = pygame.Rect(40, y, SCREEN_WIDTH - 80, row_h - 8)
            is_current = char.active_pet is not None and char.active_pet.template_id == tid

            if is_current:
                bg, border = (60, 50, 20), COLOR_GOLD
            elif unlocked:
                bg, border = (28, 28, 36), COLOR_WHITE
            else:
                bg, border = (18, 18, 18), (50, 50, 50)

            pygame.draw.rect(screen, bg, rect)
            pygame.draw.rect(screen, border, rect, 2 if is_current else 1)

            name_color = COLOR_WHITE if unlocked else (100, 100, 100)
            self.renderer.draw_text(screen, template["display_name"],
                                    (rect.x + 15, rect.y + 8), color=name_color, font_size=18)

            ability_names = ", ".join(a["name"] for a in template.get("abilities", []))
            self.renderer.draw_text(screen, ability_names,
                                    (rect.x + 15, rect.y + 32), color=COLOR_DARK_GRAY, font_size=13)

            if not unlocked:
                lvl = template.get("level_req", 1)
                self.renderer.draw_text(screen, f"Requires level {lvl}",
                                        (rect.right - 180, rect.y + 8), color=COLOR_RED, font_size=14)
            elif is_current:
                self.renderer.draw_text(screen, "Active", (rect.right - 100, rect.y + 8),
                                        color=COLOR_GOLD, font_size=14)
            else:
                self.renderer.draw_text(screen, "Summon", (rect.right - 110, rect.y + 8),
                                        color=COLOR_GREEN, font_size=14)
                self._row_rects.append((rect, lambda t=tid: self._pick(t)))

            y += row_h
