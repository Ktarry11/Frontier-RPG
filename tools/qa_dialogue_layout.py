#!/usr/bin/env python3
"""A talk quest's questions sit under what the person said, and fit on the screen.

    PYTHONPATH=. SDL_VIDEODRIVER=dummy python3 tools/qa_dialogue_layout.py

Kyle, 16 Nov 2026, on Brannoc at the Black Strand: "This is overlapping? The option to talk to people is good and i
like this. just fix UI". The question buttons sat at a fixed height, so an opening longer than two paragraphs ran
under them. For every quest with a dialogue objective, rendered in the talk screen:
  1. the first question starts below the last line of the opening;
  2. every question and the hint under them fit above the Close button.
"""
import os
import sys
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
import pygame  # noqa: E402


def main():
    pygame.init()
    from config import SCREEN_WIDTH, SCREEN_HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    from core.game_state import GameStateManager
    from entities.character import Character
    from ui.screens.quest_dialog_screen import QuestDialogScreen
    from world.quest_manager import get_quest_manager
    sm = GameStateManager(screen)
    sm.player = Character(name="H", char_class="Warrior", level=40)
    qm = get_quest_manager()
    bad, n = [], 0
    for qid, q in qm.quests.items():
        if not any(o.objective_type.value == "dialogue" for o in q.objectives):
            continue
        scr = QuestDialogScreen(sm, SimpleNamespace(npc_id="qa", name="Someone", greeting=""))
        scr.mode, scr.active_quest, scr.selected_topic = "dialogue", q, None
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        scr.render(surf)
        end = scr._draw_wrapped_text(pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)), q.accept_text, (40, 130),
                                     max_width=SCREEN_WIDTH - 80, line_height=22)
        rects = [r for _t, r in scr.topic_button_rects]
        n += 1
        if rects and rects[0].y < end:
            bad.append(f"{qid}: the first question (y {rects[0].y}) starts above the end of the text (y {end})")
        if rects and rects[-1].bottom + 40 > SCREEN_HEIGHT - 90:
            bad.append(f"{qid}: the questions run to y {rects[-1].bottom}, into the Close button")
    print(f"{n} talk quests laid out")
    if bad:
        print(f"FAIL ({len(bad)})")
        for b in bad[:20]:
            print("  -", b)
        return 1
    print("PASS - every talk quest's questions sit under its text and above the Close button")
    return 0


if __name__ == "__main__":
    sys.exit(main())
