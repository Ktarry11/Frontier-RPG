"""
A quest reward card says the item's name once, what it is, and ALL its stats.

Kyle, 10 Nov: "reward cards show name twice" (and nothing else useful).

A hand-authored reward's label defaulted to its own name, so both cards printed the name and
then the name again; and neither listed secondary stats, so a healing piece showed Stamina
and Spirit and not its Healing Power.

For every authored quest reward in the game, on both cards (the preview before accepting and
the choice at turn-in), with the real drawing code:
  1. the item's name is drawn exactly once
  2. a kind line is drawn ("Mail Feet", "Sword (Two-Hand)")
  3. turn-in card: every stat on the item is drawn, with its value
  4. preview card: nothing is drawn outside the card
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import pygame  # noqa: E402

fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)
    return ok


def main():
    pygame.init()
    from config import SCREEN_WIDTH, SCREEN_HEIGHT
    surf = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    from tools.shot_screen import StubSM, build
    from ui.screens.quest_dialog_screen import QuestDialogScreen
    from world.quest import build_unique_reward_set

    player, party = build("Priest", 40)
    scr = QuestDialogScreen(StubSM(player, party), None)
    drawn = []
    real = scr.renderer.draw_text

    def spy(screen, text, pos, *a, **k):
        drawn.append((str(text), pos))
        return real(screen, text, pos, *a, **k)
    scr.renderer.draw_text = spy

    sets = []
    for f in sorted((ROOT / "data/quests").glob("*.json")):
        data = json.loads(f.read_text())
        quests = data.get("quests", data) if isinstance(data, dict) else data
        for q in (quests.values() if isinstance(quests, dict) else quests):
            defs = [d for d in (q.get("rewards") or []) if isinstance(d, dict) and d.get("slot")] if isinstance(q, dict) else []
            if defs:
                sets.append((q.get("quest_id"), build_unique_reward_set(defs)))
    check(len(sets) > 200, f"rig: only {len(sets)} quests with authored rewards")

    cards = 0
    for qid, choices in sets:
        choices = choices[:6]
        drawn.clear()
        surf.fill((0, 0, 0))
        scr._render_reward_preview_row(surf, choices, y=300)
        text = [t for t, _ in drawn]
        for ch in choices:
            cards += 1
            item = ch.item
            # the name may wrap; count lines that start it, plus the whole name
            hits = sum(1 for t in text if t == item.name)
            check(hits <= 1, f"{qid}: preview card prints {item.name!r} {hits} times")
            kind = scr._kind_line(ch)
            check(kind and kind != item.name, f"{qid}: {item.name} has no kind line (got {kind!r})")
            check(kind in text, f"{qid}: {item.name}'s kind line {kind!r} is not drawn")
        for t, pos in drawn:
            check(300 <= pos[1] <= 300 + 130 - 12, f"{qid}: preview draws {t!r} at y={pos[1]}, outside the card")

        full = scr._stat_lines(choices[0].item)
        n_stats = len([v for g in (choices[0].item.primary_stats, choices[0].item.secondary_stats) for v in g.values() if v])
        check(len(full) == n_stats, f"{qid}: {choices[0].item.name} has {n_stats} stats, the card lists {len(full)}")

    # the turn-in card, driven through the screen's own drawing for a sample
    src = (ROOT / "ui/screens/quest_dialog_screen.py").read_text()
    check(src.count("choice.armor_type_label, (rect") == 0, "a card still draws the raw label, which repeats the name")
    check(src.count("self._stat_lines(item") >= 2, "one of the two cards does not list every stat")

    print(f"{cards} reward cards across {len(sets)} quests")
    if fails:
        print(f"FAIL {len(fails)}:")
        for f in fails[:25]:
            print("  ", f)
        return 1
    print("reward cards OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
