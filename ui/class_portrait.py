"""
Class portrait loader for the overworld unit frame.

Sourced from Gethe/wow-ui-textures (real WoW class icons, not generated
art) - see assets/ui/class_icons/. Kyle was explicit these should be the
authentic class icons, not a generic/anime-style face.

Custom CoA classes (Stormbringer, and the 21 data-modeled-but-not-yet-
selectable ones) have no official WoW icon, so this degrades gracefully
to None rather than guessing at a substitute - callers draw the existing
"Portrait WIP" placeholder treatment in that case, same as the character
sheet already does for the animated-character slot.
"""
import os
import pygame

_ICON_DIR = "assets/ui/class_icons"

# class name -> loaded pygame.Surface (raw, unscaled)
_icon_cache = {}


def _icon_key(char_class):
    """Maps whatever spelling of a class a caller has to the icon filename.

    Classes are spelled TWO ways in this codebase and both reach here. The player's
    char_class and the ability/talent data use the file-safe id ("sun_cleric"); every
    recruit in data/npcs/recruits.json stores the display name ("Sun Cleric"). Only the
    first spelling used to resolve, so Elias and the other 7 recruits in the four
    two-word classes - Sun Cleric, Witch Doctor, Witch Hunter, Knight of Xoroth - fell
    through to "no icon" even though their icon file was sitting right there.

    One-word classes hid this for months because "Paladin".lower() already matched.
    """
    from core.class_names import class_key
    return class_key(char_class)


def get_class_icon(char_class, size=None):
    """Returns a pygame.Surface for the class's icon, optionally scaled to
    (size, size), or None if no icon exists for this class (custom CoA
    classes) or the file is missing.

    A missing char_class returns None rather than raising. Callers use this as a
    FALLBACK for a character with no portrait, so it is reached precisely when
    something is already absent, and a crash there would be the worst possible
    response to "this person has no picture".
    """
    if not char_class:
        return None
    key = _icon_key(char_class)
    if key not in _icon_cache:
        path = os.path.join(_ICON_DIR, f"{key}.png")
        surf = None
        if os.path.isfile(path):
            try:
                surf = pygame.image.load(path)
                if pygame.display.get_surface() is not None:
                    surf = surf.convert_alpha()
            except pygame.error:
                surf = None
        _icon_cache[key] = surf

    surf = _icon_cache[key]
    if surf is None or size is None:
        return surf
    return pygame.transform.smoothscale(surf, (size, size))
