"""Unit frames: a character's portrait, name, level and bars, the way the play screen shows its party.

Kyle, 27 Nov 2026: "the general UI isn't nice with character names, levels, resources", and of the play screen,
"There's a lot of wasted space on the right." The side panel showed the hero alone, with "HP: 559/559" written over a
bar that said 559/559 again, and an empty column below it. These frames show the hero and every party member, one
style for both: a framed portrait, the name in bold, a dim "Lv 22 Warrior" line, health with its numbers inside,
and the class's resource as a slim bar under it.
"""
import pygame

from ui import theme

RESOURCE_COLOURS = {"mana": (70, 120, 230), "rage": (200, 60, 55), "energy": (225, 200, 60)}


def _resource(char):
    """(current, max, colour) for the character's main resource, or None."""
    try:
        from combat.abilities import get_class_resource, ResourceType
        rtype = get_class_resource(char.char_class, char)
    except Exception:                                          # noqa: BLE001
        return None
    pools = {
        "mana": (getattr(char, "current_mana", 0), getattr(char, "mana", 0)),
        "rage": (getattr(char, "current_rage", 0), getattr(char, "max_rage", 0)),
        "energy": (getattr(char, "current_energy", 0), getattr(char, "max_energy", 0)),
    }
    key = getattr(rtype, "value", rtype)
    if key in pools:
        cur, mx = pools[key]
        return (cur, mx, RESOURCE_COLOURS[key]) if mx else None
    if hasattr(char, "get_resource_max"):
        mx = char.get_resource_max(rtype)
        if mx:
            return char.get_resource(rtype), mx, (170, 150, 220)
    return None


def _portrait(char, size):
    rid = getattr(char, "recruit_id", None)
    if rid:
        try:
            from ui.recruit_portrait import get_recruit_face
            face = get_recruit_face(rid, size)
            if face is not None:
                return face
        except Exception:                                      # noqa: BLE001
            pass
    try:
        from ui.class_portrait import get_class_icon
        return get_class_icon(char.char_class, size=size)
    except Exception:                                          # noqa: BLE001
        return None


def draw_unit_frame(renderer, screen, char, x, y, width, big=False, highlight=False, subtitle=None):
    """Draw one frame with its top-left at (x, y). Returns the frame's rect.

    big is the hero's: a larger portrait and name, and numbers on both bars. A party member's is compact.
    subtitle replaces the "Lv N Class" line (a title, say)."""
    pad = 8
    pic = 54 if big else 44
    hp_h = 16 if big else 14
    res_h = 12 if big else 7
    name_font = renderer.bold(19 if big else 15)
    sub_font = renderer._get_font(None, 12 if big else 11)
    height = pad * 2 + max(pic, name_font.get_height() + sub_font.get_height() + hp_h + res_h + 8)
    rect = pygame.Rect(x, y, width, height)

    # body: the theme's inset gradient, with a keyline; the hero's frame and a selected one are gold-edged
    body = pygame.Surface(rect.size)
    for row in range(height):
        t = row / max(1, height - 1)
        col = tuple(int(theme.PANEL_TOP[i] + (theme.PANEL_BOTTOM[i] - theme.PANEL_TOP[i]) * t) for i in range(3))
        pygame.draw.line(body, col, (0, row), (width, row))
    screen.blit(body, rect.topleft)
    edge = theme.FRAME_SELECTED if highlight else (theme.FRAME if big else theme.FRAME_INNER)
    pygame.draw.rect(screen, edge, rect, 1, border_radius=4)

    # portrait, framed; greyed when down
    alive = char.is_alive() if hasattr(char, "is_alive") else True
    prect = pygame.Rect(x + pad, y + pad, pic, pic)
    pygame.draw.rect(screen, (12, 11, 15), prect, border_radius=3)
    img = _portrait(char, pic - 4)
    if img is not None:
        if img.get_size() != (pic - 4, pic - 4):
            img = pygame.transform.smoothscale(img, (pic - 4, pic - 4))
        if not alive:
            img = img.copy()
            img.fill((90, 90, 95, 255), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(img, (prect.x + 2, prect.y + 2))
    pygame.draw.rect(screen, theme.FRAME if big else theme.FRAME_INNER, prect, 1, border_radius=3)

    # name and the level line
    tx = prect.right + 9
    tw = rect.right - pad - tx
    name = renderer.truncate(char.name, tw, font_size=None) if hasattr(renderer, "truncate") else char.name
    while name_font.size(name)[0] > tw and len(name) > 3:
        name = name[:-2].rstrip() + "."
    renderer.draw_text_shadow(screen, name, (tx, y + pad - 2), name_font,
                              color=theme.TEXT if alive else theme.TEXT_DISABLED)
    ty = y + pad - 2 + name_font.get_height() - 2
    if subtitle is None:
        subtitle = f"Lv {getattr(char, 'level', 1)} {getattr(char, 'char_class', '')}"
        if big and getattr(char, "prestige_level", 0):
            subtitle += f"  -  Prestige {char.prestige_level}"
    line = subtitle if alive else "Down"
    renderer.draw_text(screen, line, (tx, ty), font_size=12 if big else 11,
                       color=theme.TEXT_DIM if alive else theme.BAD)
    ty += sub_font.get_height() + 3

    # health, then the resource under it
    renderer.draw_health_bar(screen, (tx, ty), max(0, getattr(char, "current_health", 0)),
                             getattr(char, "health", 0) or 1, width=tw, height=hp_h,
                             bar_color=(70, 185, 80) if alive else (70, 70, 70), show_text=True)
    ty += hp_h + 3
    res = _resource(char)
    if res:
        cur, mx, colour = res
        renderer.draw_health_bar(screen, (tx, ty), cur, mx, width=tw, height=res_h, bar_color=colour,
                                 show_text=big)
    return rect
