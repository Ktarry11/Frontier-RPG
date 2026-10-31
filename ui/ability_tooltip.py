"""The one ability hover-tooltip, drawn the same way everywhere it appears.

There were three copies of this function - cast_screen.py, combat_screen.py and
skills_screen.py - each carrying a comment saying it matched the other two. They
did match, to the pixel, apart from one of them drawing a (200, 200, 100) border
where the others used COLOR_GOLD (200, 150, 50), which is exactly the kind of
drift three copies of one rule produce. Kyle, 2026-10-31, asked for a fourth:
"when we go to learn something, is there a way to hover over it and show what it
does? like we can do that in our cast bar already." A fourth copy was the wrong
answer, so there is now one.

The CONTENT comes from Ability.get_tooltip_lines, which has always been shared -
see its docstring for why the numbers it prints are deliberately pre-modifier
rather than the caster's computed damage. This module is only the box around it.
"""
import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_GOLD

FONT_SIZE = 14
LINE_HEIGHT = 18
PADDING = 10

#: A long flavour line would otherwise force the box absurdly wide, so the text
#: wraps at this width instead.
MAX_TEXT_WIDTH = 320


def draw_ability_tooltip(renderer, screen, ability, pos, player=None):
    """Draw `ability`'s tooltip near `pos`, clamped inside the screen.

    Returns True if something was drawn. An object with no get_tooltip_lines (a
    Consumable, say) or an empty line list draws nothing, so callers can hand
    this whatever they are hovering without checking first.
    """
    getter = getattr(ability, "get_tooltip_lines", None)
    if getter is None:
        return False
    lines = getter(player)
    if not lines:
        return False

    font = renderer._get_font(font_size=FONT_SIZE)
    wrapped = []
    for line in lines:
        if font.size(line)[0] <= MAX_TEXT_WIDTH:
            wrapped.append(line)
            continue
        cur = ""
        for word in line.split():
            candidate = f"{cur} {word}".strip()
            if font.size(candidate)[0] > MAX_TEXT_WIDTH and cur:
                wrapped.append(cur)
                cur = word
            else:
                cur = candidate
        if cur:
            wrapped.append(cur)

    box_w = max(font.size(l)[0] for l in wrapped) + PADDING * 2
    box_h = len(wrapped) * LINE_HEIGHT + PADDING * 2

    # Offset off the cursor so the pointer never sits on top of the text, then
    # clamped so the box cannot draw off the right or bottom edge.
    x, y = pos[0] + 16, pos[1] + 16
    if x + box_w > SCREEN_WIDTH:
        x = SCREEN_WIDTH - box_w - 4
    if y + box_h > SCREEN_HEIGHT:
        y = SCREEN_HEIGHT - box_h - 4

    pygame.draw.rect(screen, (15, 15, 20), (x, y, box_w, box_h))
    pygame.draw.rect(screen, COLOR_GOLD, (x, y, box_w, box_h), 2)

    text_y = y + PADDING
    for i, line in enumerate(wrapped):
        # Name and rank in gold, body in white - the convention the real game
        # uses, and what Kyle's reference screenshot shows.
        renderer.draw_text(screen, line, (x + PADDING, text_y),
                           font_size=FONT_SIZE, color=COLOR_GOLD if i == 0 else COLOR_WHITE)
        text_y += LINE_HEIGHT
    return True
