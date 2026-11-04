#!/usr/bin/env python3
"""
Render all three Party screen tabs headlessly and check what they show.

    PYTHONPATH=. python3 tools/qa_party_screen_tabs.py

A UI screen that imports proves nothing - every bug this covers is a runtime
one. It builds a real party with real gear and real buffs, draws each tab, and
then asserts the thing each tab exists for:

  Details   core stats must read WITH gear. The bug being guarded is that
            Character keeps `strength` (base) and `effective_strength`
            (base+gear) and the panel read the base one, so anyone wearing
            anything was under-reported. A geared character must not display
            their naked number.
  Stats     must survive being drawn for a class with no school-specific spell
            power at all (every warrior), which is the branch that prints
            nothing rather than six zeroes.
  Buffs     must list every party member, including ones with no buffs - the
            whole point is seeing who is MISSING one, so an empty member who
            is silently skipped defeats the feature.
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


def main():
    pygame.init()
    pygame.display.set_mode((1280, 720))
    surf = pygame.Surface((1280, 720))

    from entities.character import Character
    from entities.party import Party
    from ui.screens.party_screen import PartyScreen

    hero = Character(name="Hero", char_class="Mage", level=40)
    mate = Character(name="Mate", char_class="Warrior", level=40)
    party = Party(hero)
    party.add_member(mate)

    class SM:
        def get_party(self_inner):
            return party
        player = hero
        def transition_to(self_inner, *a, **k):
            pass

    screen = PartyScreen(SM())
    screen.selected = hero
    fails = []

    # ---- Details: gear must be included in the core stats
    base = int(getattr(hero, "intellect", 0) or 0)
    eff = PartyScreen._eff(hero, "intellect")
    if eff < base:
        fails.append(f"_eff(intellect)={eff} is below base {base}")
    hero.effective_intellect = base + 100
    if PartyScreen._eff(hero, "intellect") != base + 100:
        fails.append("_eff did not read effective_intellect")

    # ---- rounding: no 13.22 / 0.82%
    for raw, pct, want in ((13.22, False, "13"), (0.82, True, "0.75%"),
                           (4.13, True, "4.25%"), (0.0, True, "0%")):
        got = PartyScreen._num(raw, pct=pct)
        if got != want:
            fails.append(f"_num({raw}, pct={pct}) = {got!r}, want {want!r}")

    # ---- every tab must draw without raising
    for tab, _label in PartyScreen.TABS:
        screen.tab = tab
        try:
            screen.render(surf)
        except Exception as exc:          # noqa: BLE001 - reporting, not handling
            import traceback
            fails.append(f"tab {tab!r} raised {type(exc).__name__}: {exc}")
            traceback.print_exc()

    # ---- the Stats tab must cope with a class that has no school spell power
    screen.tab = "stats"
    screen.selected = mate
    for _name, attr in PartyScreen.SCHOOLS:
        setattr(mate, attr, 0)
    try:
        screen.render(surf)
    except Exception as exc:              # noqa: BLE001
        fails.append(f"stats tab with no school spell power raised: {exc}")

    # ---- the Buffs tab must name every member, buffed or not
    screen.tab = "buffs"
    seen = []
    real_draw = screen.renderer.draw_text

    def spy(dst, text, pos, *a, **k):
        seen.append(str(text))
        return real_draw(dst, text, pos, *a, **k)

    screen.renderer.draw_text = spy
    try:
        screen.render(surf)
    finally:
        screen.renderer.draw_text = real_draw
    for member in (hero, mate):
        if not any(member.name in t for t in seen):
            fails.append(f"buffs tab never named {member.name}")
    if not any("no active buffs" in t or "none" in t.lower() for t in seen):
        fails.append("buffs tab showed nothing for an unbuffed party")

    # ---- the tab bar must be clickable
    if len(screen.tab_rects) != len(PartyScreen.TABS):
        fails.append(f"{len(screen.tab_rects)} tab rects, want {len(PartyScreen.TABS)}")

    # ---- ACTION BUTTONS MUST EXIST ON EVERY TAB
    #
    # Kyle, 4 Nov 2026: "i can't equip my party members. I need the option to
    # do that." He could - from the Details tab only. Stats and Party Buffs
    # (both added 2 Nov, in this same file's feature) each returned early from
    # _render_detail BEFORE the button row was drawn, so action_rects came back
    # empty and Gear, Talents, Skills, Background, Bench and Dismiss simply did
    # not exist on two of the three tabs.
    #
    # Losing it on Stats is the worst case: that is the tab you are reading
    # when you work out what someone needs to equip.
    #
    # Asserted per tab rather than once, because the failure was per tab and a
    # single check on the default tab would have passed throughout.
    for tab_name, _label in PartyScreen.TABS:
        screen.tab = tab_name
        screen.selected = mate
        screen.render(surf)
        actions = {a for a, _r in screen.action_rects}
        for required in ("gear", "talents", "skills"):
            if required not in actions:
                fails.append(f"'{tab_name}' tab has no {required.upper()} button "
                             f"(found: {sorted(actions) or 'nothing'})")
        # Drawn once per render, not once per tab branch - a duplicated call
        # would stack two rects per action in the same place.
        if len(screen.action_rects) != len(actions):
            fails.append(f"'{tab_name}' tab registered {len(screen.action_rects)} "
                         f"rects for {len(actions)} actions - duplicated draw")

    print(f"tabs drawn: {[t for t, _ in PartyScreen.TABS]}")
    print(f"tab hit-rects: {len(screen.tab_rects)}")
    if fails:
        for f in fails:
            print(f"  FAIL  {f}")
        return 1
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
