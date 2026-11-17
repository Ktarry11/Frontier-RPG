#!/usr/bin/env python3
"""Five enemies fit across the top of the combat screen, names and all.

    PYTHONPATH=. SDL_VIDEODRIVER=dummy python3 tools/qa_enemy_strip_fits.py [out_dir]

Kyle, 16 Nov 2026, with the fifth of a Jaedenar pack cut off at the right edge: "i like 5 enemies but we need to ensure
they fit!" For pulls of one to five, with the longest names in the game:
  1. every name plate and health bar lies inside the screen;
  2. no two name plates overlap.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
import pygame  # noqa: E402


def main():
    pygame.init()
    from config import SCREEN_WIDTH, SCREEN_HEIGHT
    surf = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    from tools.shot_screen import StubSM
    from entities.character import Character
    from entities.party import Party
    from entities.monster import Monster
    from ui.screens.combat_screen import CombatScreen
    out = sys.argv[1] if len(sys.argv) > 1 else None
    names = ["Jaedenar Doomguard", "Jaedenar Felhound", "Scarlet Woodsman Archer", "Restless Lodge Ranger",
             "Marris Ossuary Guard"]
    player = Character("Hero", "Warrior", 54)
    bad = []
    for n in range(1, 6):
        foes = [Monster(names[i], "beast_basic", level=54) for i in range(n)]
        sm = StubSM(player, Party(player))
        sm.current_enemy, sm.current_enemies = foes[0], foes
        scr = CombatScreen(sm)
        scr._init_combat()
        drawn = []
        real = scr.renderer.draw_text

        def spy(surface, text, pos, *a, **kw):
            size = kw.get("size", "normal")
            font = scr.renderer.font_small if size == "small" else (
                scr.renderer.font_large if size == "large" else scr.renderer.font_normal)
            w, h = font.size(str(text))
            x = int(pos[0]) - (w // 2 if kw.get("center") else 0)
            drawn.append((str(text), pygame.Rect(x, int(pos[1]), w, h - 4)))
            return real(surface, text, pos, *a, **kw)
        scr.renderer.draw_text = spy
        surf.fill((0, 0, 0))
        scr._draw_enemy_strip(surf)
        scr.renderer.draw_text = real
        if out:
            pygame.image.save(surf, os.path.join(out, f"enemy_strip_{n}.png"))
        plates = [(t, r) for t, r in drawn if "(Lvl" in t or t.endswith("...")]
        if len(plates) != n:
            bad.append(f"{n} enemies: {len(plates)} name plates drawn")
        screen = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        for t, r in plates:
            if not screen.contains(r):
                bad.append(f"{n} enemies: '{t}' runs off the screen ({r.left}..{r.right})")
        for i, (t1, r1) in enumerate(plates):
            for t2, r2 in plates[i + 1:]:
                if r1.colliderect(r2):
                    bad.append(f"{n} enemies: '{t1}' and '{t2}' overlap")
    if bad:
        print(f"FAIL ({len(bad)})")
        for b in bad:
            print("  -", b)
        return 1
    print("PASS - up to five enemies fit across the screen, and no two names touch")
    return 0


if __name__ == "__main__":
    sys.exit(main())
