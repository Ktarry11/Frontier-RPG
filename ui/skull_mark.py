"""A small skull, drawn rather than loaded: the mark beside a hidden zone's name.

Kyle, 14 Nov 2026: "These new zones will still have the level range but maybe a skull next to them.
The hidden open world zones that link to a new zone need this skull to indicate they're harder."
The game's font (Lora) has no skull glyph, and the mark has to read at banner size on any
background, so it is a few shapes with a dark outline.
"""
import pygame

_cache = {}


def skull(size=26, color=(225, 215, 190), outline=(25, 18, 12)):
    key = (size, color, outline)
    if key in _cache:
        return _cache[key]
    s = size
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    for col, grow in ((outline, 2), (color, 0)):
        cr = int(s * 0.36) + grow
        pygame.draw.circle(surf, col, (s // 2, int(s * 0.42)), cr)
        jaw = pygame.Rect(int(s * 0.28) - grow, int(s * 0.56) - grow, int(s * 0.44) + 2 * grow, int(s * 0.30) + 2 * grow)
        pygame.draw.rect(surf, col, jaw, border_radius=max(1, s // 10))
    eye = max(2, int(s * 0.12))
    for ex in (int(s * 0.35), int(s * 0.65)):
        pygame.draw.circle(surf, outline, (ex, int(s * 0.45)), eye)
    nose = [(s // 2, int(s * 0.56)), (int(s * 0.45), int(s * 0.66)), (int(s * 0.55), int(s * 0.66))]
    pygame.draw.polygon(surf, outline, nose)
    for tx in (0.38, 0.5, 0.62):
        x = int(s * tx)
        pygame.draw.line(surf, outline, (x, int(s * 0.72)), (x, int(s * 0.84)), max(1, s // 18))
    _cache[key] = surf
    return surf
