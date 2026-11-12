"""
A quest giver's Shop / Bank / service buttons never sit on the quest's text.

Kyle's screenshot, 10 Nov: on Quartermaster Horg's quest offer the Shop button was drawn over
the Rewards line.

For EVERY quest in the game, offered by an NPC who is a vendor, a banker and an innkeeper at
once (the most buttons there can be), with the real screen:
  1. no text is drawn inside or across a service button
  2. the buttons do not overlap each other, Accept or Not Now, and are on screen
  3. clicking Shop opens the shop
"""
import json
import os
import sys
import types
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
    from world.quest import Quest
    from ui.screens.quest_dialog_screen import QuestDialogScreen

    player, party = build("Warrior", 60)
    sm = StubSM(player, party)
    npc = types.SimpleNamespace(name="Quartermaster Horg of the Long Supply Line", npc_id="x", greeting="")
    scr = QuestDialogScreen(sm, npc)
    scr._refresh = lambda *a, **k: None
    scr.is_vendor, scr.is_banker, scr.services = True, True, ["inn"]

    drawn = []
    real = scr.renderer.draw_text

    def spy(screen, text, pos, *a, **k):
        try:
            font = scr.renderer._get_font(font_size=k.get("font_size")) if k.get("font_size") else scr.renderer._get_font(size=k.get("size", "normal"))
            w, h = font.size(str(text))
        except Exception:
            w, h = 8 * len(str(text)), 18
        if screen is surf and screen.get_clip().colliderect(pygame.Rect(pos[0], pos[1], w, h)):   # not text scrolled out of its clip
            drawn.append((str(text), pygame.Rect(pos[0], pos[1], w, h)))
        return real(screen, text, pos, *a, **k)
    scr.renderer.draw_text = spy

    quests = []
    for f in sorted((ROOT / "data/quests").glob("*.json")):
        raw = json.loads(f.read_text())
        block = raw if isinstance(raw, list) else raw.get("quests", raw)
        for it in (block if isinstance(block, list) else list(block.values())):
            if isinstance(it, dict) and it.get("quest_id"):
                quests.append(it)
    check(len(quests) > 500, f"rig: only {len(quests)} quests")

    n = 0
    for q in quests:
        try:
            quest = Quest(**{k: v for k, v in q.items() if k in Quest.__init__.__code__.co_varnames})
        except Exception:
            continue
        scr.mode, scr.active_quest = "offer", quest
        drawn.clear()
        surf.fill((0, 0, 0))
        try:
            scr.render(surf)
        except Exception as exc:
            check(False, f"rig: {q['quest_id']} would not render ({type(exc).__name__}: {exc})")
            continue
        n += 1
        buttons = scr._side_service_buttons()
        labels = {b[0] for b in buttons}
        if not check(len(buttons) == 3, f"rig: {len(buttons)} service buttons, wanted Shop, Bind and Bank"):
            break
        for label, _action, rect in buttons:
            check(surf.get_rect().contains(rect), f"{label} button {tuple(rect)} is off screen")
            for other in (scr.accept_button, scr.decline_button):
                check(not rect.colliderect(other), f"{label} button overlaps Accept / Not Now")
            for text, trect in drawn:
                if text in labels:
                    continue                         # the button's own caption
                if trect.colliderect(rect):
                    check(False, f"{q['quest_id']}: the {label} button {tuple(rect)} sits on {text[:60]!r} at {tuple(trect)}")
                    break
        for i, a in enumerate(buttons):
            for b in buttons[i + 1:]:
                check(not a[2].colliderect(b[2]), f"{a[0]} overlaps {b[0]}")
        if len(fails) > 30:
            break

    went = []
    sm.transition_to = lambda state, **kw: went.append((state, kw))
    shop = next(r for l, a, r in scr._side_service_buttons() if a == "shop")
    scr.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=shop.center, button=1))
    check(went and "VENDOR" in str(went[-1][0]).upper(), f"clicking Shop went to {went[-1:] }")

    if "--shot" in sys.argv:
        pygame.image.save(surf, sys.argv[sys.argv.index("--shot") + 1])
    print(f"{n} quest offers rendered with Shop, Bind Hearthstone and Bank showing")
    if fails:
        print(f"FAIL {len(fails)}:")
        for f in fails[:20]:
            print("  ", f)
        return 1
    print("quest screen service buttons OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
