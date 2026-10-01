"""
Totem loadout screen. Lets a Shaman pick one totem per element (Earth,
Fire, Water, Air) to save into Character.totem_loadout - that saved
loadout is what Call of the Ancestors (see combat/abilities.py's
totem_loadout effect_type) casts in a single action.

Standalone screen like PetScreen, reachable from the overworld - matches
real WoW where setting up a totem preset is something you do at rest, not
mid-fight.
"""
import pygame
from ui.screens.base_screen import BaseScreen
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_GOLD, COLOR_GREEN, COLOR_RED, COLOR_DARK_GRAY

ELEMENT_LABELS = {"earth": "Earth", "fire": "Fire", "water": "Water", "air": "Air"}
ELEMENT_COLORS = {
    "earth": (120, 90, 50),
    "fire": (150, 60, 30),
    "water": (40, 90, 140),
    "air": (140, 140, 160),
}


class TotemScreen(BaseScreen):
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

    def _pick(self, totem_ability_id):
        if self.character is None:
            return
        self.character.set_totem(totem_ability_id)

    def render(self, screen):
        screen.fill((15, 15, 20))
        char = self.character or getattr(self.state_manager, "player", None)

        self.renderer.draw_text(screen, "Totem Loadout", (40, 30), size="large", color=COLOR_GOLD)
        self.renderer.draw_text(screen, "ESC to go back - select one totem per element",
                                (40, 65), font_size=14, color=COLOR_DARK_GRAY)

        if char is None or char.char_class != "Shaman":
            self.renderer.draw_text(screen, "Only Shaman have totems.", (40, 100), color=COLOR_RED)
            return

        from combat.totems import ELEMENTS, totems_for_element

        self._row_rects = []
        col_w = (SCREEN_WIDTH - 80) // 4
        for col, element in enumerate(ELEMENTS):
            x = 40 + col * col_w
            y = 110
            color = ELEMENT_COLORS[element]
            pygame.draw.rect(screen, color, (x, y, col_w - 15, 34))
            self.renderer.draw_text(screen, ELEMENT_LABELS[element],
                                    (x + 10, y + 8), color=COLOR_WHITE, font_size=16)
            y += 50

            options = totems_for_element(element)
            for totem_id in options:
                ability = char.ability_book.get_ability(totem_id) if hasattr(char, "ability_book") else None
                if ability is None:
                    continue
                rect = pygame.Rect(x, y, col_w - 15, 50)
                is_learned = getattr(ability, "is_learned", True)
                is_selected = char.totem_loadout.get(element) == totem_id

                if not is_learned:
                    bg, border = (18, 18, 18), (50, 50, 50)
                elif is_selected:
                    bg, border = (60, 50, 20), COLOR_GOLD
                else:
                    bg, border = (28, 28, 36), COLOR_WHITE

                pygame.draw.rect(screen, bg, rect)
                pygame.draw.rect(screen, border, rect, 2 if is_selected else 1)

                name_color = COLOR_WHITE if is_learned else (100, 100, 100)
                self.renderer.draw_text(screen, ability.name, (rect.x + 8, rect.y + 6),
                                        color=name_color, font_size=13)

                if is_learned:
                    lvl_text = "Selected" if is_selected else "Select"
                    lvl_color = COLOR_GOLD if is_selected else COLOR_GREEN
                    self.renderer.draw_text(screen, lvl_text, (rect.x + 8, rect.y + 28),
                                            color=lvl_color, font_size=12)
                    self._row_rects.append((rect, lambda t=totem_id: self._pick(t)))
                else:
                    lvl = ability.ranks[0]["level_req"] if ability.ranks else "?"
                    self.renderer.draw_text(screen, f"Req. level {lvl}", (rect.x + 8, rect.y + 28),
                                            color=COLOR_RED, font_size=12)

                y += 58

        # Show the Call ability's readiness at the bottom
        call_ability = char.ability_book.get_ability("shaman_call_of_ancestors") if hasattr(char, "ability_book") else None
        if call_ability and getattr(call_ability, "is_learned", False):
            slotted = len(char.totem_loadout)
            self.renderer.draw_text(
                screen, f"Call of the Ancestors ready - {slotted}/4 totems slotted",
                (40, SCREEN_HEIGHT - 50), color=COLOR_GREEN, font_size=16)
        else:
            self.renderer.draw_text(
                screen, "Call of the Ancestors not yet learned - totems must be cast individually.",
                (40, SCREEN_HEIGHT - 50), color=COLOR_DARK_GRAY, font_size=14)
