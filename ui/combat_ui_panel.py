"""
Combat UI panel. Shows hotbar, resources, combat info.
"""
import pygame
from config import (
    COLOR_WHITE, COLOR_DARK_GRAY, COLOR_RED, COLOR_GREEN, COLOR_BLUE,
    BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_PADDING, FONT_SIZE_NORMAL, FONT_SIZE_SMALL
)


class CombatUIPanel:
    """UI panel for combat information and hotbar."""
    
    def __init__(self, renderer):
        self.renderer = renderer
    
    def render_player_panel(self, screen, character, x, y, width=300, height=200):
        """Render player info panel."""
        # Background
        panel_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, COLOR_DARK_GRAY, panel_rect)
        pygame.draw.rect(screen, COLOR_WHITE, panel_rect, 2)
        
        # Name and class
        self.renderer.draw_text(screen, f"{character.name} ({character.char_class})", (x + 10, y + 10))
        y_offset = y + 35
        
        # Health bar
        self.renderer.draw_text(screen, "HP", (x + 10, y_offset))
        self.renderer.draw_health_bar(screen, (x + 50, y_offset), character.current_health, character.health, width=240)
        y_offset += 30
        
        # Mana bar (if applicable)
        if character.char_class in ["Shaman", "Priest"]:
            self.renderer.draw_text(screen, "Mana", (x + 10, y_offset))
            self.renderer.draw_health_bar(screen, (x + 50, y_offset), character.current_mana, character.mana, width=240, height=15)
            y_offset += 30
        
        # Rage bar (if Warrior)
        if character.char_class == "Warrior":
            self.renderer.draw_text(screen, "Rage", (x + 10, y_offset))
            self.renderer.draw_health_bar(screen, (x + 50, y_offset), character.rage, character.max_rage, width=240, height=15)
            y_offset += 30
        
        # Energy bar (if Rogue)
        if character.char_class == "Rogue":
            self.renderer.draw_text(screen, "Energy", (x + 10, y_offset))
            self.renderer.draw_health_bar(screen, (x + 50, y_offset), character.energy, character.max_energy, width=240, height=15)
    
    def render_target_panel(self, screen, character, x, y, width=300, height=150):
        """Render target info panel."""
        # Background
        panel_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, COLOR_DARK_GRAY, panel_rect)
        pygame.draw.rect(screen, COLOR_RED, panel_rect, 2)
        
        # Name and level
        self.renderer.draw_text(screen, f"{character.name} (Lvl {character.level})", (x + 10, y + 10))
        y_offset = y + 35
        
        # Health bar
        self.renderer.draw_text(screen, "HP", (x + 10, y_offset))
        self.renderer.draw_health_bar(screen, (x + 50, y_offset), character.current_health, character.health, width=240)
    
    def render_hotbar(self, screen, character, x, y, button_width=70, button_height=70):
        """Render hotbar with ability buttons."""
        # Background
        bar_width = (button_width + BUTTON_PADDING) * 4
        bar_rect = pygame.Rect(x, y, bar_width, button_height + 20)
        pygame.draw.rect(screen, COLOR_DARK_GRAY, bar_rect)
        pygame.draw.rect(screen, COLOR_WHITE, bar_rect, 2)
        
        # Draw slots
        for i, ability_id in enumerate(character.hotbar):
            slot_x = x + 5 + i * (button_width + BUTTON_PADDING)
            slot_y = y + 5
            slot_rect = pygame.Rect(slot_x, slot_y, button_width, button_height)
            
            # Get ability
            ability = character.get_ability(ability_id) if ability_id else None
            
            # Background color based on availability
            if ability and ability.is_available(character):
                bg_color = (50, 100, 50)  # Green - available
            elif ability:
                bg_color = (100, 50, 50)  # Red - unavailable
            else:
                bg_color = (50, 50, 50)  # Gray - empty
            
            pygame.draw.rect(screen, bg_color, slot_rect)
            pygame.draw.rect(screen, COLOR_WHITE, slot_rect, 2)
            
            # Ability name
            if ability:
                # Truncate name to fit
                name = ability.name[:10]
                text = self.renderer.font_normal.render(name, True, COLOR_WHITE)
                text_rect = text.get_rect(center=(slot_x + button_width // 2, slot_y + 20))
                screen.blit(text, text_rect)
                
                # Cost
                # Talented cost - see combat_screen; the action bar must
                # agree with what the cast will actually charge.
                _caster = getattr(self, "character", None) or getattr(self, "player", None)
                cost_text = f"{ability.talented_cost(_caster) if _caster is not None else ability.cost}"
                cost_surface = self.renderer.font_normal.render(cost_text, True, COLOR_WHITE)
                cost_rect = cost_surface.get_rect(center=(slot_x + button_width // 2, slot_y + 45))
                screen.blit(cost_surface, cost_rect)
                
                # Cooldown indicator
                if ability.current_cooldown > 0:
                    cd_text = f"{ability.current_cooldown:.1f}s"
                    cd_surface = self.renderer.font_normal.render(cd_text, True, COLOR_RED)
                    cd_rect = cd_surface.get_rect(center=(slot_x + button_width // 2, slot_y + 60))
                    screen.blit(cd_surface, cd_rect)
            
            # Key number
            key_text = self.renderer.font_normal.render(str(i + 1), True, COLOR_BLUE)
            screen.blit(key_text, (slot_x + 5, slot_y + 5))
    
    def render_combat_log(self, screen, combat_log, x, y, width=400, height=150, max_lines=6):
        """Render combat log."""
        # Background
        log_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, COLOR_DARK_GRAY, log_rect)
        pygame.draw.rect(screen, COLOR_WHITE, log_rect, 2)
        
        # Title
        self.renderer.draw_text(screen, "Combat Log", (x + 10, y + 5))
        
        # Show last N lines
        start_idx = max(0, len(combat_log) - max_lines)
        y_offset = y + 25
        for msg in combat_log[start_idx:]:
            self.renderer.draw_text(screen, msg, (x + 10, y_offset), size="small")
            y_offset += 20
    
    def get_hotbar_rect(self, slot, x, y, button_width=70, button_height=70):
        """Get screen rect for a hotbar slot."""
        slot_x = x + 5 + slot * (button_width + BUTTON_PADDING)
        slot_y = y + 5
        return pygame.Rect(slot_x, slot_y, button_width, button_height)
