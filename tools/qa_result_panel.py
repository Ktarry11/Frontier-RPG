#!/usr/bin/env python3
"""The victory screen: nothing on it sits on anything else, however much a fight gives.

    PYTHONPATH=. SDL_VIDEODRIVER=dummy python3 tools/qa_result_panel.py [out_dir]

Kyle, 16 Nov 2026, with "YOUR BAGS ARE FULL" drawn over the item it was about: "We should expand out the victory
screen". For a quiet win, a big haul (twelve drops, coin, trash), a full-bag win and a defeat:
  1. every line of text on the panel lies inside the panel;
  2. no two lines of text overlap;
  3. the bags-full plate holds every line it draws.
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
    from entities.loot_generator import LootGenerator
    from ui.screens.combat_screen import CombatScreen
    out = sys.argv[1] if len(sys.argv) > 1 else None
    player = Character("Hero", "Warrior", 40)
    sm = StubSM(player, Party(player))
    foe = Monster("Mangy Wolf", "beast_basic", level=40)
    sm.current_enemy, sm.current_enemies = foe, [foe]
    scr = CombatScreen(sm)
    scr._init_combat()
    gen = LootGenerator()
    items = [gen.generate_item_for_class("Warrior", 40 + i % 5) for i in range(12)]
    items = [i for i in items if i is not None]
    cases = {
        "quiet": dict(victory=True, exp_earned=420, copper_earned=0, trash_gained=0, loot_gained=items[:1],
                      loot_missed=[]),
        "haul": dict(victory=True, exp_earned=1790, copper_earned=23456, trash_gained=3, loot_gained=items[:12],
                     loot_missed=[]),
        "bags_full": dict(victory=True, exp_earned=1790, copper_earned=0, trash_gained=3, loot_gained=items[:4],
                          loot_missed=["Barbed Stinger", "Hive Resin", "Sturdy Cloak", "Chitin Plate",
                                       "Stinger Gland"]),
        "defeat": dict(victory=False, exp_earned=0, copper_earned=0, trash_gained=0, loot_gained=[], loot_missed=[]),
    }
    bad = []
    real = scr.renderer.draw_text
    for name, fields in cases.items():
        eng = scr.combat_engine
        eng.is_active = False
        eng.fled = False
        eng.loot_dropped = None
        for k, v in fields.items():
            setattr(eng, k, v)
        drawn = []

        def spy(surface, text, pos, *a, **kw):
            size = kw.get("size", "normal")
            font = scr.renderer.font_large if size == "large" else scr.renderer.font_normal
            w, h = font.size(str(text))
            drawn.append((str(text), pygame.Rect(int(pos[0]), int(pos[1]), w, h - 4)))
            return real(surface, text, pos, *a, **kw)
        scr.renderer.draw_text = spy
        surf.fill((0, 0, 0))
        scr._render_result_panel(surf, "Victory!" if fields["victory"] else "Defeat!", (80, 200, 80))
        scr.renderer.draw_text = real
        panel = scr._result_panel_rect
        if out:
            pygame.image.save(surf, os.path.join(out, f"result_{name}.png"))
        for t, r in drawn:
            if not panel.contains(r):
                bad.append(f"{name}: '{t}' runs outside the panel")
        for i, (t1, r1) in enumerate(drawn):
            for t2, r2 in drawn[i + 1:]:
                if r1.colliderect(r2):
                    bad.append(f"{name}: '{t1}' and '{t2}' overlap")
        if not panel.height < SCREEN_HEIGHT:
            bad.append(f"{name}: the panel is taller than the screen")
    print(f"{len(cases)} results laid out")
    if bad:
        print(f"FAIL ({len(bad)})")
        for b in bad[:20]:
            print("  -", b)
        return 1
    print("PASS - the victory screen never draws one thing over another")
    return 0


if __name__ == "__main__":
    sys.exit(main())
