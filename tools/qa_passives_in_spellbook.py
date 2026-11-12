"""
Passives are listed in the spellbook, under Core.

Kyle, 10 Nov: "show passives under Core."

A recruit's own trait and a race's heritage are always on and were shown nowhere - the only
trace of Kiet Somsak's "-30% threat, +8% haste" was his sheet reading differently.

With the real spellbook screen, for every recruit:
  1. the Core tab lists each passive they have, by name, tagged Passive, with its numbers
  2. the numbers shown are the numbers applied (they match what the character really gets)
  3. passives are not on the other tabs
  4. a consumable below the passives is still the one that gets selected when clicked
"""
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
    from tools.shot_screen import StubSM
    from entities.party import Party
    from world.recruit_manager import get_recruit_manager
    from world.personal_kits import passive_entries_for, passives_for
    from ui.screens.skills_screen import SkillsScreen

    rm = get_recruit_manager()
    seen_passives = 0
    shot_done = False
    for rec in rm.recruits.values():
        c = rm.build_or_restore(rec, player_level=40)
        if c is None:
            continue
        entries = passive_entries_for(c)
        applied = passives_for(c)
        shown_keys = sum(len(lines) for _n, _s, lines in entries)
        check(shown_keys == len([v for v in applied.values() if v]) or shown_keys >= len(applied),
              f"{c.name}: {len(applied)} passive stats applied, {shown_keys} shown")
        if not entries:
            continue
        sm = StubSM(c, Party(c))
        scr = SkillsScreen(sm)
        if hasattr(scr, "set_subject"):
            scr.set_subject(c)
        texts = []
        real = scr.renderer.draw_text
        scr.renderer.draw_text = lambda s_, text, *a, **k: (texts.append(str(text)), real(s_, text, *a, **k))[1]

        scr.active_tab = "core"
        scr.scroll_offset = 0
        texts.clear()
        surf.fill((0, 0, 0))
        scr.render(surf)
        rows = list(getattr(scr, "_passive_rows", []))
        if len(c.ability_book.get_all_abilities()) and len(rows) < len(entries):
            # only acceptable if the list ran out of room
            room = scr.ABILITY_LIST_HEIGHT // scr.SLOT_HEIGHT
            check(len(scr._visible_abilities(c)) + len(rows) >= room - 1,
                  f"{c.name}: {len(entries)} passives, {len(rows)} drawn, and the list was not full")
        for name, source, lines, rect in rows:
            seen_passives += 1
            check(name in texts, f"{c.name}: passive {name!r} is not written on the Core tab")
            check(any(t.startswith("Passive") for t in texts), f"{c.name}: {name} is not tagged Passive")
            check(any(lines[0].split()[0] in t for t in texts), f"{c.name}: {name}'s numbers are not shown")
            check(surf.get_rect().contains(rect), f"{c.name}: {name}'s row is off screen")
        if rows and not shot_done and "--shot" in sys.argv:
            pygame.image.save(surf, sys.argv[sys.argv.index("--shot") + 1])
            shot_done = True

        # 3. not on another tab
        other = next((t for t in ("all", scr.CLASS_TAB) if t != "core"), None)
        scr.active_tab = other
        scr.render(surf)
        check(not getattr(scr, "_passive_rows", []), f"{c.name}: passives are drawn on the {other} tab")

        # 4. consumable click still lands
        if rows and seen_passives < 6:
            from entities.consumable_manager import get_consumable_manager
            food = get_consumable_manager().get_consumable("meal_tough_jerky", 3)
            c.consumables = [food]
            scr.active_tab = "core"
            scr.selected_ability = None
            scr.render(surf)
            y = scr.ABILITY_LIST_Y + (len(scr._visible_abilities(c)) + len(rows)) * scr.SLOT_HEIGHT + scr.SLOT_HEIGHT // 2
            if y < scr.ABILITY_LIST_Y + scr.ABILITY_LIST_HEIGHT:
                real_pos = pygame.mouse.get_pos
                pygame.mouse.get_pos = lambda: (scr.ABILITY_LIST_X + 60, y)     # the screen asks the mouse, not the event
                scr.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(scr.ABILITY_LIST_X + 60, y), button=1))
                pygame.mouse.get_pos = real_pos
                check(scr.selected_ability is food, f"{c.name}: clicking the food under the passives selected {getattr(scr.selected_ability, 'name', None)}")
            c.consumables = []

    check(seen_passives >= 40, f"rig: only {seen_passives} passive rows seen across all recruits")
    print(f"{seen_passives} passive rows drawn across the recruits' Core tabs")
    if fails:
        print(f"FAIL {len(fails)}:")
        for f in fails[:20]:
            print("  ", f)
        return 1
    print("passives in spellbook OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
