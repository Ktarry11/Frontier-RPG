#!/usr/bin/env python3
"""The combat hotbar shows each ability's icon, and hovering it says what it does.

    PYTHONPATH=. python3 tools/qa_hotbar_icons.py

Kyle, 15 Nov 2026: "ability icons on the combat hotbar instead of labelled boxes. Hovering one shows the name, the
damage, healing or potency range, cast speed, cost and cooldown." Built 18 Nov. Through the real CombatScreen, in a
real fight, for a caster, a melee class and a healer at level 60, it checks:
  1. every ability on the bar that has art on disk is drawn as that art (the slot isn't the old flat box), and one
     with no art still has its labelled box
  2. an ability on cooldown shows the turns left on its icon (the slot is darkened and differs from the ready one)
  3. hovering a slot gives a tooltip whose second line is its reach ("Ranged, any one enemy", "Melee, ...",
     "One ally", ...), and an area spell's shape line agrees with it (one row, not "all enemies")
  4. a potion on the bar draws its icon and hovering it names it, since an icon carries no name
  5. every player ability's reach line is one of the known phrasings (nothing falls through)
"""
import contextlib
import io
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)
    return ok


def fight(sm, cls):
    from core.game_states import GameState
    from entities.character import Character
    from entities.monster import Monster
    with contextlib.redirect_stdout(io.StringIO()):
        sm.player = Character(name="QA", char_class=cls, level=60)
        foes = [Monster(name="Dummy", monster_type="beast_basic", level=60),
                Monster(name="Dummy Caster", monster_type="humanoid_caster", level=60)]
        sm.current_enemy, sm.current_enemies = foes[0], foes
        cs = sm.states[GameState.COMBAT]
        cs._init_combat()
    return cs


def slot_pixels(screen, rect):
    inner = rect.inflate(-8, -8)
    sub = screen.subsurface(inner)
    return [tuple(sub.get_at((x, y))[:3]) for y in range(0, inner.h, 6) for x in range(0, inner.w, 6)]


def main():
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    from core.game_state import GameStateManager
    from ui.screens.combat_screen import CombatScreen
    from entities.consumable_manager import get_consumable_manager
    with contextlib.redirect_stdout(io.StringIO()):
        sm = GameStateManager(screen)
    pygame.mouse.get_pos = lambda: (0, 0)

    known = ("Yourself", "Your pet", "One ally", "Your whole party", "The ", "Ranged, ", "Melee, ")
    drawn = 0
    for cls in ("Mage", "Warrior", "Priest"):
        cs = fight(sm, cls)
        p = sm.player
        abilities = [(i, p.ability_book.get_ability(x)) for i, x in enumerate(p.hotbar) if isinstance(x, str)]
        abilities = [(i, a) for i, a in abilities if a is not None]
        check(len(abilities) >= 6, f"{cls}: only {len(abilities)} abilities on the bar, the rig is wrong")
        iconed = set()
        real = cs._draw_icon_slot

        def spy(screen_, rect_, surf, **kw):
            ok = real(screen_, rect_, surf, **kw)
            if ok:
                iconed.add(tuple(rect_))
            return ok
        cs._draw_icon_slot = spy
        screen.fill((0, 0, 0))
        cs.render(screen)
        del cs._draw_icon_slot
        for i, a in abilities:
            rect = cs.hotbar_positions[i]
            art = cs._ability_icon(a, rect.w - 4) is not None
            check(art == (tuple(rect) in iconed),
                  f"{cls}: {a.name} {'has art but was drawn as a label' if art else 'has no art but drew an icon'}")
            if art:
                drawn += 1
                if a.is_usable_by(p):       # a ready icon shows its art; a dimmed one is dark on purpose
                    colours = len(set(slot_pixels(screen, rect)))
                    check(colours > 25, f"{cls}: {a.name} is ready but its slot is flat ({colours} colours)")

        # 2. cooldown
        i, a = next(((i, a) for i, a in abilities if cs._ability_icon(a, 76) is not None), (None, None))
        if a is not None:
            before = slot_pixels(screen, cs.hotbar_positions[i])
            a.turns_remaining = 3
            screen.fill((0, 0, 0))
            cs.render(screen)
            after = slot_pixels(screen, cs.hotbar_positions[i])
            dark = sum(sum(c) for c in after) < sum(sum(c) for c in before) * 0.8
            check(dark, f"{cls}: {a.name} on cooldown isn't darkened")
            a.turns_remaining = 0

        # 3. hover
        for i, a in abilities[:6]:
            r = cs.hotbar_positions[i]
            cs.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=r.center, rel=(0, 0), buttons=(0, 0, 0)))
            check(cs.hovered_ability is a, f"{cls}: hovering slot {i} doesn't pick {a.name}")
            lines = a.get_tooltip_lines(p)
            check(len(lines) > 1 and lines[1] == a.reach_text(), f"{cls}: {a.name}'s tooltip has no reach line")
            if a.target_type == "enemy_aoe":
                check(not any("all enemies" in l for l in lines),
                      f"{cls}: {a.name} says a row and then 'all enemies'")

    # 4. a potion on the bar
    cs = fight(sm, "Warrior")
    p = sm.player
    potion = None
    for cid in ("healing_potion_major", "healing_potion_superior", "healing_potion_greater", "healing_potion_standard"):
        potion = get_consumable_manager().get_consumable(cid, quantity=5)
        if potion is not None:
            break
    if check(potion is not None, "rig: no healing potion to put on the bar"):
        p.hotbar[9] = potion
        r = cs.hotbar_positions[9]
        has_art = cs._consumable_icon(potion, r.w - 4) is not None
        screen.fill((0, 0, 0))
        cs.render(screen)
        if has_art:
            check(len(set(slot_pixels(screen, r))) > 25, f"{potion.name} has art but its slot is flat")
        cs.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=r.center, rel=(0, 0), buttons=(0, 0, 0)))
        tip = cs.hovered_ability
        check(tip is not None and tip.get_tooltip_lines(p)[0] == potion.name,
              f"hovering {potion.name} doesn't name it")

    # 5. every reach line is a known phrasing
    import json
    from entities.character import Character
    specs = json.loads((ROOT / "data/items/spec_gear.json").read_text(encoding="utf-8"))
    classes = sorted({v["class"] for v in specs.values() if isinstance(v, dict) and "class" in v})
    n = 0
    for cls in classes:
        with contextlib.redirect_stdout(io.StringIO()):
            c = Character(name="QA", char_class=cls, level=60)
        for a in c.ability_book.get_all_abilities():
            n += 1
            t = a.reach_text()
            check(bool(t) and t.startswith(known), f"{cls}: {a.name} reach line {t!r}")

    print(f"{drawn} hotbar icons drawn across 3 classes; {n} abilities' reach lines read")
    if fails:
        print(f"FAIL {len(fails)}:")
        for f in fails[:20]:
            print("  ", f)
        return 1
    print("hotbar icons OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
