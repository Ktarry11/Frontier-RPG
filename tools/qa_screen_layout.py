#!/usr/bin/env python3
"""No button may sit on top of another, or outside the screen, or in a panel.

    PYTHONPATH=. python3 tools/qa_screen_layout.py

Kyle sent a screenshot of the character sheet with the PRESTIGE button and its
label drawn straight through the COMBAT STATS column, over "Hit (Off Hand)"
and "Hit (Ranged)", while the entire right-hand side sat empty.

The cause is worth writing down because it will recur: the button was placed at
pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, ...). Screen-centre is
not a position in a multi-column layout - it is whichever column happens to be
there. The column maths lived in render() as locals, so __init__ could not see
it and worked out its own answer. One rule, two implementations, again.

WHY A SUITE RATHER THAN JUST THE FIX. Every screen in this game places its
buttons by hand against SCREEN_WIDTH and SCREEN_HEIGHT, so every screen can
make the same mistake, and the only detector until now was Kyle playing the
game and taking a photo. This checks what can be checked without a human eye:

  * no interactive rect leaves the screen
  * no two interactive rects overlap each other
  * on screens that declare panel regions, no button lands inside one

It cannot see text overflowing a panel - draw_text does not report where it
drew - so tools/shot_screen.py exists for the eye half of the job.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402


#: Screens whose buttons are placed by hand and so can collide. Keyed the same
#: way tools/shot_screen.py names them.
SCREENS = {
    "character_sheet": ("ui.screens.character_sheet_screen", "CharacterSheetScreen"),
    "inventory": ("ui.screens.inventory_screen", "InventoryScreen"),
    "quest_journal": ("ui.screens.quest_journal_screen", "QuestJournalScreen"),
    "cast": ("ui.screens.cast_screen", "CastScreen"),
    "party": ("ui.screens.party_screen", "PartyScreen"),
}


#: Buttons that SHARE a rect on purpose because they are never on screen at
#: the same time - a two-step confirm where "Yes" replaces the first button in
#: place. Overlap between these is the design, not a bug.
#:
#: Declared rather than guessed: the suite cannot tell a state-swapped button
#: from a misplaced one, and silently ignoring same-rect pairs would have let
#: the real prestige bug through if it had happened to land exactly on another
#: button.
EXCLUSIVE = {
    "quest_journal": [{"abandon_button", "abandon_yes_button"}],
}


#: screen key -> panel rects that buttons must stay out of. Only declared
#: where a screen has a column layout worth protecting.
def _sheet_panels():
    from ui.screens.character_sheet_screen import COL_W, COL_LEFT_X, COL_MID_X
    from config import SCREEN_HEIGHT
    return [("left column", pygame.Rect(COL_LEFT_X, 20, COL_W, SCREEN_HEIGHT - 40)),
            ("middle column", pygame.Rect(COL_MID_X, 20, COL_W, SCREEN_HEIGHT - 40))]


PANELS = {"character_sheet": _sheet_panels}


def main():
    from config import SCREEN_WIDTH, SCREEN_HEIGHT
    pygame.init()
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    sys.path.insert(0, str(ROOT / "tools"))
    # Reuses tools/shot_screen.py's own stub rather than a second one. That
    # file is the screenshot tool for these same screens; two different stubs
    # would drift and one of them would stop matching what the game does.
    from shot_screen import build, StubSM
    from config import PRESTIGE_LEVEL

    findings = []
    checked = 0

    for name, (mod_name, cls_name) in sorted(SCREENS.items()):
        try:
            player, party = build("Druid", PRESTIGE_LEVEL)
            __import__(mod_name)
            cls = getattr(sys.modules[mod_name], cls_name)
            scr = cls(StubSM(player, party))
        except Exception as e:
            findings.append((name, f"could not build: {type(e).__name__}: {e}"))
            continue

        rects = {n: r for n, r in vars(scr).items()
                 if isinstance(r, pygame.Rect) and n.endswith("button")}
        checked += len(rects)

        for n, r in sorted(rects.items()):
            if not (0 <= r.left and r.right <= SCREEN_WIDTH
                    and 0 <= r.top and r.bottom <= SCREEN_HEIGHT):
                findings.append((name, f"{n} {tuple(r)} leaves the {SCREEN_WIDTH}x"
                                       f"{SCREEN_HEIGHT} screen"))

        names = sorted(rects)
        groups = EXCLUSIVE.get(name, [])
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                pair = {names[i], names[j]}
                if any(pair <= g for g in groups):
                    continue
                if rects[names[i]].colliderect(rects[names[j]]):
                    findings.append((name, f"{names[i]} overlaps {names[j]}"))

        if name in PANELS:
            try:
                panels = PANELS[name]()
            except Exception as e:
                findings.append((name, f"panel probe failed: {e}"))
                panels = []
            for n, r in sorted(rects.items()):
                for pname, p in panels:
                    if r.colliderect(p):
                        findings.append(
                            (name, f"{n} {tuple(r)} is drawn inside the {pname} "
                                   f"{tuple(p)}"))

    print(f"  {checked} interactive rects across {len(SCREENS)} screens")
    print(f"  checked: on-screen, no mutual overlap, clear of declared panels\n")

    if findings:
        print(f"  {len(findings)} finding(s):\n")
        for scr, msg in findings:
            print(f"    {scr:18}{msg}")
        print("\nFAIL")
        return 1

    print("  every button is on-screen, clear of its neighbours, and outside "
          "the stat panels")
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
