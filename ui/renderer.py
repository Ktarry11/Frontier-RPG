"""
Placeholder renderer. Uses rectangles and text for UI.
"""
import pygame
from config import (
    COLOR_WHITE, COLOR_BLACK, COLOR_DARK_GRAY, COLOR_LIGHT_GRAY,
    COLOR_RED, COLOR_GREEN, COLOR_BLUE, FONT_SIZE_NORMAL, FONT_SIZE_LARGE
)

#: "small" was accepted as a `size=` value in 24+ call sites across the UI
#: (item quantity corners, tooltips, ...) but _get_font's size branch only
#: ever recognized "normal" vs falling back to "large" for anything else -
#: so every one of those call sites was silently rendering at 40px (large)
#: instead of something actually smaller than normal. Found via a real
#: rendered screenshot of the materials tooltip showing overlapping text
#: lines, not a code-inspection guess. Every existing size="small" caller
#: gets a genuinely smaller font for free the moment this constant exists
#: and _get_font checks for it - no caller code needs to change.
FONT_SIZE_SMALL = 16


class Renderer:
    """Simple placeholder rendering utilities."""
    
    def __init__(self):
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_normal = pygame.font.Font(None, FONT_SIZE_NORMAL)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        self._font_cache = {}
    
    def draw_rect(self, screen, rect, color, fill=True):
        """Draw a rectangle."""
        if fill:
            pygame.draw.rect(screen, color, rect)
        else:
            pygame.draw.rect(screen, color, rect, 2)
    
    def _get_font(self, size="normal", font_size=None):
        """
        Resolve a font. `font_size` (an int pixel size) wins if given and is
        cached, otherwise fall back to the named 'small'/'normal'/'large'
        fonts - anything unrecognized still falls back to 'normal' (not
        'large'), so a typo'd size name degrades to a readable default
        instead of unexpectedly blowing up to the biggest font.
        """
        if font_size is not None:
            font_size = int(font_size)
            font = self._font_cache.get(font_size)
            if font is None:
                font = pygame.font.Font(None, font_size)
                self._font_cache[font_size] = font
            return font
        if size == "large":
            return self.font_large
        if size == "small":
            return self.font_small
        return self.font_normal

    def draw_text(self, screen, text, pos, y=None, color=COLOR_WHITE,
                  size="normal", font_size=None, center=False):
        """
        Draw text.

        Position may be given either as a tuple `(x, y)` or as two separate
        positional args `x, y`. `center` treats the position as the text's
        horizontal centre rather than its top-left. `font_size` requests an
        explicit pixel size instead of the named 'normal'/'large' fonts.
        """
        if y is not None and not isinstance(pos, (tuple, list)):
            x, y_pos = pos, y
        else:
            x, y_pos = pos

        font = self._get_font(size, font_size)
        surface = font.render(str(text), True, color)
        if center:
            screen.blit(surface, surface.get_rect(center=(x, y_pos + surface.get_height() // 2)))
        else:
            screen.blit(surface, (x, y_pos))
    
    def wrap_text(self, text, max_width, size="normal"):
        """
        Word-wrap text to fit within max_width pixels, measuring actual
        rendered text width rather than guessing by character count (which
        breaks for variable-width fonts and cuts messages off mid-word).
        Returns a list of line strings.
        """
        font = self.font_normal if size == "normal" else self.font_large
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        return lines if lines else [""]

    def draw_button(self, screen, rect, text, color=COLOR_DARK_GRAY, text_color=COLOR_WHITE):
        """Draw a button."""
        self.draw_rect(screen, rect, color)
        self.draw_rect(screen, rect, COLOR_LIGHT_GRAY, fill=False)
        
        # Center text in button
        text_surface = self.font_normal.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)
    
    def draw_character_box(self, screen, char, pos):
        """Draw a character representation (placeholder)."""
        box_width, box_height = 150, 200
        box_rect = pygame.Rect(pos[0], pos[1], box_width, box_height)
        
        # Draw background
        self.draw_rect(screen, box_rect, COLOR_DARK_GRAY)
        self.draw_rect(screen, box_rect, COLOR_LIGHT_GRAY, fill=False)
        
        # Draw character info
        y_offset = pos[1] + 10
        self.draw_text(screen, f"{char.name}", (pos[0] + 10, y_offset))
        y_offset += 30
        self.draw_text(screen, f"Lvl {char.level} {char.char_class}", (pos[0] + 10, y_offset))
        y_offset += 30
        self.draw_text(screen, f"HP: {char.display_health}/{round(char.health)}", (pos[0] + 10, y_offset))
        y_offset += 25
        self.draw_text(screen, f"Mana: {char.display_mana}/{round(char.mana)}", (pos[0] + 10, y_offset))
    
    def draw_health_bar(self, screen, pos, current, max_val, width=100, height=20, bar_color=None, show_text=True):
        """
        Draw a health/resource bar with the current/max numbers overlaid by
        default. bar_color lets callers use the right color per resource
        (green=HP, blue=mana, red=rage, yellow=energy); falls back to green
        if not specified, matching prior behavior.
        """
        bar_rect = pygame.Rect(pos[0], pos[1], width, height)
        
        # Background
        self.draw_rect(screen, bar_rect, COLOR_DARK_GRAY)
        
        # Filled portion
        fill_color = bar_color if bar_color is not None else COLOR_GREEN
        if max_val > 0:
            fill_width = int(width * (current / max_val))
            fill_rect = pygame.Rect(pos[0], pos[1], fill_width, height)
            self.draw_rect(screen, fill_rect, fill_color)
        
        # Border
        self.draw_rect(screen, bar_rect, COLOR_LIGHT_GRAY, fill=False)

        # Numeric overlay (e.g. "196/196"), centered on the bar. round()
        # not int() - current can be a real float (out-of-combat regen
        # ticks fractional HP every frame), and truncating would visibly
        # undercount by up to ~1 point vs. the character sheet's own
        # display_health, which rounds (see StatusEffectMixin.display_health).
        if show_text:
            text = f"{round(current)}/{round(max_val)}"
            text_surface = self.font_normal.render(text, True, COLOR_WHITE)
            text_rect = text_surface.get_rect(center=bar_rect.center)
            screen.blit(text_surface, text_rect)

    def draw_class_portrait(self, screen, center, radius, icon_surface,
                            border_color=None, border_width=3,
                            bg_color=(20, 20, 25)):
        """
        Round unit-frame portrait: a filled background disc, the class icon
        clipped to a circle on top, and a ring border - the "nicer bars"
        request's portrait half, WoW-unit-frame style. icon_surface may be
        None (custom CoA classes with no sourced icon, or a load failure);
        in that case only the empty ring + background disc draw, same
        "WIP" treatment as the character sheet's blank portrait box rather
        than guessing at a substitute face.
        """
        from config import COLOR_GOLD
        border_color = border_color if border_color is not None else COLOR_GOLD

        pygame.draw.circle(screen, bg_color, center, radius)

        if icon_surface is not None:
            # Clip the (square) icon to a circle via a mask surface, so a
            # square PNG reads as a round portrait instead of a square peg
            # sitting inside a circular border.
            diameter = radius * 2
            icon_scaled = pygame.transform.smoothscale(icon_surface, (diameter, diameter))
            mask = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
            pygame.draw.circle(mask, (255, 255, 255, 255), (radius, radius), radius)
            clipped = icon_scaled.copy()
            clipped.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            screen.blit(clipped, (center[0] - radius, center[1] - radius))

        pygame.draw.circle(screen, border_color, center, radius, border_width)
