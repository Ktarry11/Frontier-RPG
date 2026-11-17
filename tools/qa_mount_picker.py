#!/usr/bin/env python3
"""Every mount you buy stays yours, and a picker chooses which one you ride.

    PYTHONPATH=. SDL_VIDEODRIVER=dummy python3 tools/qa_mount_picker.py [--shot out.png]

Kyle, 16 Nov 2026: "for mounts we need a way to select the mount - as when we buy them it just replaces the old mount
with the new ones". With a rider who owns three mounts:
  1. buying keeps the old ones; all three are owned
  2. clicking the Mount button opens the picker (with one mount it just rides); every owned mount is a row, inside
     the screen
  3. picking a mount rides it and makes it the one R summons; R afterwards toggles that one
  4. in a cave the pick is remembered but you stay on foot, and say why
  5. the choice survives a save and load
  6. Esc closes the picker without changing anything
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

fails = []


def check(ok, msg):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}")
    if not ok:
        fails.append(msg)


def main():
    shot = sys.argv[sys.argv.index("--shot") + 1] if "--shot" in sys.argv else None
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    from core.game_state import GameStateManager, GameState
    from entities.character import Character
    from ui.screens.overworld_screen import OverworldScreen
    from world.travel_manager import get_travel_manager, travel_data
    sm = GameStateManager(screen)
    sm.player = Character(name="Hero", char_class="Warrior", level=45)
    ow = sm.states.get(GameState.OVERWORLD) or OverworldScreen(sm)
    if hasattr(ow, "on_enter"):
        ow.on_enter()
    t = get_travel_manager()
    t.riding_rank, t.owned_mounts, t.active_mount, t.mounted = 3, [], None, False
    mounts = travel_data()["mounts"]
    picks = [next(m for m in mounts if m["tier"] == k) for k in (1, 2)] + [
        next(m for m in mounts if m["tier"] == 1 and m["id"] != next(x for x in mounts if x["tier"] == 1)["id"])]
    # 1
    for m in picks:
        t.buy_mount(m)
    check(len(t.owned()) == 3, f"all three bought mounts are kept ({[m['name'] for m in t.owned()]})")
    ow.zone_manager.is_in_cave = lambda: False
    # 2
    ow.render(screen)
    ow.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=ow.mount_button_rect.center, button=1))
    check(ow.mount_picker, "clicking Mount opens the picker")
    ow.render(screen)
    ids = [mid for _r, mid in ow.mount_picker_rects]
    check(set(ids) == {m["id"] for m in picks}, "every owned mount is a row")
    check(all(screen.get_rect().contains(r) for r, _ in ow.mount_picker_rects), "every row is inside the screen")
    if shot:
        pygame.image.save(screen, shot)
    # 3
    want = picks[2]["id"]
    r = next(r for r, mid in ow.mount_picker_rects if mid == want)
    ow.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=r.center, button=1))
    check(not ow.mount_picker and t.mounted and t.active_mount == want,
          f"picking rides it ({t.active_mount}, mounted {t.mounted})")
    ow.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r, mod=0, unicode="r"))
    check(not t.mounted, "R dismounts")
    ow.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r, mod=0, unicode="r"))
    check(t.mounted and t.active_mount == want, "R rides the picked one again")
    # 4
    t.mounted = False
    mounted, msg = t.choose_mount(picks[1]["id"], True)
    check(not mounted and t.active_mount == picks[1]["id"] and "cave" in msg.lower(),
          f"in a cave the pick is kept and you stay on foot ({msg})")
    # 5
    data = t.to_dict()
    t.active_mount = None
    t.load_from_dict(data)
    check(t.active_mount == picks[1]["id"] and len(t.owned_mounts) == 3, "the choice survives a save and load")
    # 6
    before = t.active_mount
    ow.render(screen)
    ow.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=ow.mount_button_rect.center, button=1))
    ow.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, mod=0, unicode=""))
    check(not ow.mount_picker and t.active_mount == before, "Esc closes the picker without changing anything")
    print("mount picker OK" if not fails else f"FAILED: {len(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
