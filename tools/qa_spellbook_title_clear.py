"""
The spellbook's title never sits on its tab row.

Kyle, 10 Nov: "when a character has 4 talent trees, it overlaps their name." Bashir Khalidi's
seven tabs ran under "Bashir Khalidi's Skills & Abilities".

The title used to be drawn at a fixed centre. For every class in the game, as the player AND
as a companion with a long name, render the real screen and read back the rects it drew: the
title must exist, must not intersect any tab, and must be on screen.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main():
    import pygame
    pygame.init()
    surface = pygame.display.set_mode((1280, 720))
    from entities.character import Character
    from ui.screens.skills_screen import SkillsScreen

    class SM:
        pass

    classes = sorted(" ".join(w.capitalize() for w in p.stem.split("_"))
                     for p in (ROOT / "data/abilities").glob("*.json"))
    bad, checked, most_tabs = [], 0, (0, "")
    for cls in classes:
        try:
            hero = Character(name="Hero", char_class=cls, level=60)
            mate = Character(name="Maximiliano Fernandez-Castillo", char_class=cls, level=60)
        except Exception:
            continue                       # not a playable class file (shared, racial, ...)
        sm = SM()
        sm.player = hero
        scr = SkillsScreen(sm)
        for who, subject in (("player", None), ("companion", mate)):
            scr.subject = subject
            scr.render(surface)
            tabs = [r for _, r in scr._tab_rects]
            title = getattr(scr, "_title_rect", None)
            checked += 1
            if len(tabs) > most_tabs[0]:
                most_tabs = (len(tabs), cls)
            if title is None:
                bad.append(f"{cls} ({who}): no title could be placed beside {len(tabs)} tabs")
            elif any(title.colliderect(t) for t in tabs):
                bad.append(f"{cls} ({who}): title {tuple(title)} overlaps a tab "
                           f"(tabs end at x={max(t.right for t in tabs)})")
            elif title.right > 1280 or title.left < 0:
                bad.append(f"{cls} ({who}): title runs off the screen {tuple(title)}")
            if tabs and max(t.right for t in tabs) > 1280:
                bad.append(f"{cls} ({who}): the tab row itself runs off the screen")
    if checked < 20:
        print(f"FAIL only {checked} screens rendered - the rig is not reaching the classes")
        return 1
    print(f"{checked} spellbooks rendered; the widest tab row is {most_tabs[0]} tabs ({most_tabs[1]})")
    if bad:
        print(f"FAIL {len(bad)}:")
        for b in bad:
            print("  ", b)
        return 1
    print("spellbook titles OK - clear of the tabs for every class, as player and companion.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
