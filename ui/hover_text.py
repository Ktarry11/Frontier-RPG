"""A hover box with the whole text of something a list had to cut short.

Kyle, 14 Nov 2026: "for rune descriptions that run off, we need to be able to have a way to see
them fully. this is also how enchanting works." Lists keep one line per row and truncate it; hover
the row and this draws the full name and description, wrapped, beside the mouse and kept on the
screen. Draw it last so nothing covers it.
"""
import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT

WIDTH = 420


def draw_hover(screen, renderer, title, lines, pos=None, title_colour=(255, 215, 120),
               text_colour=(200, 220, 200)):
    pos = pos or pygame.mouse.get_pos()
    inner = WIDTH - 24
    body = []
    for line in lines:
        if not line:
            continue
        for w in renderer.wrap_text(line, inner, font_size=15):
            body.append(w)
    titles = renderer.wrap_text(title, inner) if title else []
    h = 14 + len(titles) * 24 + (6 if titles and body else 0) + len(body) * 20 + 10
    x = pos[0] + 18
    y = pos[1] + 14
    if x + WIDTH > SCREEN_WIDTH - 8:
        x = pos[0] - WIDTH - 12
    if y + h > SCREEN_HEIGHT - 8:
        y = max(8, SCREEN_HEIGHT - 8 - h)
    box = pygame.Rect(x, y, WIDTH, h)
    pygame.draw.rect(screen, (16, 16, 22), box)
    pygame.draw.rect(screen, (150, 130, 90), box, 1)
    ty = y + 10
    for t in titles:
        renderer.draw_text(screen, t, (x + 12, ty), color=title_colour)
        ty += 24
    if titles and body:
        ty += 6
    for b in body:
        renderer.draw_text(screen, b, (x + 12, ty), font_size=15, color=text_colour)
        ty += 20
    return box
