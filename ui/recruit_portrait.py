"""Recruit portrait loader: assets/ui/portraits/<recruit_id>.png (RGBA bust, transparent background).

Returns None for anyone without a portrait (the player, missing files) so callers simply skip drawing it."""
import os
import pygame

_PORTRAIT_DIR = "assets/ui/portraits"
_cache = {}


def get_recruit_portrait(recruit_id, height=None):
    if not recruit_id:
        return None
    key = (recruit_id, height)
    if key in _cache:
        return _cache[key]
    surf = None
    path = os.path.join(_PORTRAIT_DIR, f"{recruit_id}.png")
    if os.path.isfile(path):
        try:
            surf = pygame.image.load(path)
            if pygame.display.get_surface() is not None:
                surf = surf.convert_alpha()
            if height:
                w = round(surf.get_width() * height / surf.get_height())
                surf = pygame.transform.smoothscale(surf, (w, height))
        except pygame.error:
            surf = None
    _cache[key] = surf
    return surf
