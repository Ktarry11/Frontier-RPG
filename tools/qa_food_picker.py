#!/usr/bin/env python3
"""The food picker and the food-buff strip on the overworld.

    PYTHONPATH=. SDL_VIDEODRIVER=dummy python3 tools/qa_food_picker.py [--shot out.png]

Kyle, 16 Nov 2026: "we need to have a way to see our food buff. Also a way to select food. these should open menu to
select food options...." With the real overworld screen, a hurt Warrior and three meals in the bags (one cooked, with
Well Fed):
  1. clicking Eat opens the picker; it lists "Best you have" and all three meals, inside the screen
  2. picking the cooked meal eats THAT one (not the biggest), remembers it, and the picker closes
  3. F afterwards eats the remembered one first; "Best you have" clears the choice
  4. the Well Fed buff shows as a chip in the badge strip with its time left, inside the screen and clear of the
     Eat / Drink buttons and the encounter switch; hovering it says what it gives
  5. Esc closes the picker without eating
  6. the choice survives a save and load
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
    return ok


def main():
    shot = sys.argv[sys.argv.index("--shot") + 1] if "--shot" in sys.argv else None
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    from core.game_state import GameStateManager, GameState
    from entities.character import Character
    from entities.consumable import Consumable
    from ui.screens.overworld_screen import OverworldScreen

    sm = GameStateManager(screen)
    sm.player = Character(name="Hero", char_class="Warrior", level=40)
    ow = sm.states.get(GameState.OVERWORLD) or OverworldScreen(sm)
    if hasattr(ow, "on_enter"):
        ow.on_enter()
    hero = sm.player
    def meal(cid, name, value, qty, **kw):
        c = Consumable(cid, name, "meal", name, value, effect_duration=18, level_multiplier=0, required_level=1,
                       cooldown_seconds=0, stack_limit=20, vendor_price=1, sell_price=0, **kw)
        c.quantity = qty
        return c
    big = meal("qa_big_bread", "Big Bread", 900, 5)
    small = meal("qa_small_bread", "Small Bread", 300, 5)
    stew = meal("qa_stew", "Hunter's Stew", 500, 3, stat_bonuses={"stamina": 8}, buff_category="food")
    hero.consumables = [big, small, stew]

    def hurt():
        hero.current_health = hero.health // 3
        hero._meal_regen = None            # stop eating, so the next press is a fresh meal
        hero._drink_regen = None

    ow.render(screen)
    hurt()
    # 1
    ow.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=ow.eat_button_rect.center, button=1))
    check(ow.rest_picker == "meal", "clicking Eat opens the picker")
    ow.render(screen)
    ids = [cid for _r, cid in ow.rest_picker_rects]
    check(ids[0] is None and set(ids[1:]) == {"qa_big_bread", "qa_small_bread", "qa_stew"},
          f"the picker lists Best + all three meals ({ids})")
    screen_rect = screen.get_rect()
    check(all(screen_rect.contains(r) for r, _ in ow.rest_picker_rects), "every row is inside the screen")
    # 2
    stew_rect = next(r for r, cid in ow.rest_picker_rects if cid == "qa_stew")
    ow.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=stew_rect.center, button=1))
    check(ow.rest_picker is None, "picking closes the picker")
    check(stew.quantity == 2 and big.quantity == 5, f"the stew was eaten, not the biggest (stew {stew.quantity}, "
                                                    f"big {big.quantity})")
    check(hero.rest_choice.get("meal") == "qa_stew", "the pick is remembered")
    # 4
    check(hero.food_buff is not None, "Well Fed is running")
    ow.render(screen)
    chips = [r for r, slot, _c, _s in ow.buff_chip_rects if slot == "food_buff"]
    check(len(chips) == 1, "a Well Fed chip is drawn")
    if chips:
        chip = chips[0]
        check(screen_rect.contains(chip), "the chip is inside the screen")
        for name in ("eat_button_rect", "drink_button_rect", "mount_button_rect", "hearth_button_rect"):
            r = getattr(ow, name, None)
            check(r is None or not chip.colliderect(r), f"the chip is clear of {name}")
        check(not chip.colliderect(ow.ENCOUNTER_BADGE), "the chip is clear of the encounter switch")
        pygame.mouse.set_pos(chip.center)
        ow.render(screen)
    if shot:
        pygame.image.save(screen, shot)
    # 3
    hurt()
    ow.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_f, mod=0, unicode="f"))
    check(stew.quantity == 1, f"F eats the remembered stew first (stew {stew.quantity})")
    ow._pick_rest("meal", None)
    check(hero.rest_choice.get("meal") is None, "\"Best you have\" clears the choice")
    # 5
    hurt()
    before = sum(c.quantity for c in hero.consumables)
    ow.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=ow.eat_button_rect.center, button=1))
    ow.render(screen)
    ow.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, mod=0, unicode=""))
    check(ow.rest_picker is None and sum(c.quantity for c in hero.consumables) == before,
          "Esc closes the picker without eating")
    # 6
    hero.rest_choice = {"meal": "qa_stew", "drink": "x"}
    back = Character.from_dict(hero.to_dict())
    check(back.rest_choice == {"meal": "qa_stew", "drink": "x"}, f"the choice survives save and load "
                                                                 f"({back.rest_choice})")
    print("food picker OK" if not fails else f"FAILED: {len(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
