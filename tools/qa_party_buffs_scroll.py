#!/usr/bin/env python3
"""The Party Buffs tab never draws under the action buttons; it scrolls.

    PYTHONPATH=. SDL_VIDEODRIVER=dummy python3 tools/qa_party_buffs_scroll.py [--shot out.png]

Kyle, 16 Nov 2026 (screenshot): the Party Buffs list was drawn under the action buttons. A full party of five plus a
benched two, each with a dozen buffs, so the list is far taller than its box:
  1. no hoverable buff row overlaps an action button, and every row sits inside the panel
  2. the list has somewhere to scroll to, and the mouse wheel moves it
  3. scrolled to the bottom, the last member's buffs are reachable (hoverable)
  4. scrolling back up past the top stops at the top
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

fails = []


def check(ok, msg):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}")
    if not ok:
        fails.append(msg)


def main():
    shot = sys.argv[sys.argv.index("--shot") + 1] if "--shot" in sys.argv else None
    pygame.init()
    pygame.display.set_mode((1280, 720))
    surf = pygame.Surface((1280, 720))
    from combat.status_effects import StatusEffect, EffectType
    from entities.character import Character
    from entities.party import Party
    from ui.screens.party_screen import PartyScreen

    hero = Character(name="Hero", char_class="Priest", level=40)
    party = Party(hero)
    names = ["Mira", "Rook", "Pell", "Dane", "Oona", "Bram"]
    classes = ["Mage", "Rogue", "Warrior", "Druid", "Shaman", "Paladin"]
    folks = [Character(name=n, char_class=c, level=40) for n, c in zip(names, classes)]
    for m in folks:
        party.add_member(m)               # four join the party, the last two go to the bench
    everyone = [m for m in party.members] + [m for m in party.bench if m not in party.members]
    check(len(everyone) == 7, f"rig: {len(everyone)} people, wanted the party of five and a bench of two")
    for m in everyone:
        for i in range(12):
            m.apply_status_effect(StatusEffect(f"qa_buff_{i}", f"Test Buff {i}", EffectType.BUFF, 5,
                                               stat_mods={"stamina": 1}, source_name="QA"))

    class SM:
        def get_party(self_inner):
            return party
        player = hero

        def transition_to(self_inner, *a, **k):
            pass

    screen = PartyScreen(SM())
    screen.selected = hero
    screen.tab = "buffs"
    screen.render(surf)
    buttons = [r for _a, r in screen.action_rects]
    rows = [r for r, _e, _m in screen._effect_hits]
    check(bool(buttons), "the action buttons are drawn")
    check(bool(rows), "some buff rows are drawn")
    check(all(not r.colliderect(b) for r in rows for b in buttons), "no buff row overlaps an action button")
    box = screen._buffs_box
    check(all(b.top >= box.bottom for b in buttons), "the list's box ends above the buttons")
    # 2
    check(screen._buffs_max_scroll > 0, f"the list overflows its box and can scroll ({screen._buffs_max_scroll}px)")
    screen.handle_event(pygame.event.Event(pygame.MOUSEWHEEL, x=0, y=-3, flipped=False))
    check(screen.buffs_scroll == 120, f"the wheel scrolls it ({screen.buffs_scroll})")
    # 3
    screen.buffs_scroll = 10 ** 6
    screen.render(surf)
    last = everyone[-1]
    check(any(m is last for _r, _e, m in screen._effect_hits), f"scrolled down, {last.name}'s buffs (the last benched) are reachable")
    rows = [r for r, _e, _m in screen._effect_hits]
    check(all(not r.colliderect(b) for r in rows for b in buttons), "scrolled, still nothing over the buttons")
    if shot:
        screen.buffs_scroll = 200
        screen.render(surf)
        pygame.image.save(surf, shot)
    # 4
    screen.buffs_scroll = 40
    screen.handle_event(pygame.event.Event(pygame.MOUSEWHEEL, x=0, y=5, flipped=False))
    check(screen.buffs_scroll == 0, f"scrolling up stops at the top ({screen.buffs_scroll})")
    print("party buffs scroll OK" if not fails else f"FAILED: {len(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
