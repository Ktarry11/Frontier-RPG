#!/usr/bin/env python3
"""Render a UI screen headlessly to a PNG, for before/after layout review.

Real pygame rendering against a real Character and Party - the point is to see
what the player sees, not an approximation of it. Stubs only the
GameStateManager, since the screens reach into it for the party and player and
nothing else during a render.

    python3 tools/shot_screen.py cast  /tmp/cast.png  [--class Primalist] [--level 1]
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402


def build(char_class="Primalist", level=1):
    from entities.character import Character
    from entities.party import Party
    player = Character("Hero", char_class, level)
    party = Party(player)
    return player, party


class StubSM:
    def __init__(self, player, party):
        self.player = player
        self._party = party
        self.states = {}
        self.current_state = None

    def get_party(self):
        return self._party

    def change_state(self, *a, **k):
        pass


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "cast"
    out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/screen.png"
    cls = "Primalist"
    lvl = 1
    if "--class" in sys.argv:
        cls = sys.argv[sys.argv.index("--class") + 1]
    if "--level" in sys.argv:
        lvl = int(sys.argv[sys.argv.index("--level") + 1])

    pygame.init()
    from config import SCREEN_WIDTH, SCREEN_HEIGHT
    surf = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    player, party = build(cls, lvl)
    sm = StubSM(player, party)

    if which == "cast":
        from ui.screens.cast_screen import CastScreen
        scr = CastScreen(sm)
        scr.selected_caster = player
    elif which == "party":
        from ui.screens.party_screen import PartyScreen
        scr = PartyScreen(sm)
        scr.selected = player
        if hasattr(scr, "selected_member"):
            scr.selected_member = player
    else:
        raise SystemExit(f"unknown screen {which!r}")

    scr.render(surf)
    pygame.image.save(surf, out)
    print(f"wrote {out}  ({cls} lvl {lvl}, {SCREEN_WIDTH}x{SCREEN_HEIGHT})")
    pygame.quit()


if __name__ == "__main__":
    main()
