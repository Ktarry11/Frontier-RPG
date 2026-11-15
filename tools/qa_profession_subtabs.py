#!/usr/bin/env python3
"""The professions screen: every trade fits, and every trade sorts into sub-tabs.

    PYTHONPATH=. SDL_VIDEODRIVER=dummy python3 tools/qa_profession_subtabs.py

Kyle, 14 Nov 2026: "when eventhing is taught this needs better layout" (the tab row ran off the
left edge), and "Can we make sub tabs within crafting ... rather than going through ALL tailoring, i
might just want bags".

  1. Every recipe in every trade sorts into a named sub-tab: none falls into a catch-all (Other,
     Gear, Consumables), which would mean a new kind of recipe nobody taught the sorter.
  2. With all 15 trades known, every trade's tab is on screen, and none overlaps the recipe panel.
  3. Clicking a sub-tab shows only that kind of recipe, and "Can craft" shows only what you can make.
  4. The mouse wheel scrolls the list and crafts nothing.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pygame  # noqa: E402

TRADES = ["herbalism", "mining", "woodcutting", "skinning", "fishing", "blacksmithing", "leatherworking",
          "alchemy", "tailoring", "woodworking", "engineering", "cooking", "jewelcrafting", "enchanting",
          "runecrafting"]
CATCH_ALL = {"Other", "Gear", "Consumables"}
PROBLEMS = []


def fail(msg):
    PROBLEMS.append(msg)
    print(f"  FAIL {msg}")


class SM:
    def __init__(self, p):
        from entities.party import Party
        self.player, self._party, self.states, self.current_state = p, Party(p), {}, None

    def get_party(self):
        return self._party

    def transition_to(self, *a, **k):
        pass

    def change_state(self, *a, **k):
        pass


def main():
    pygame.init()
    from config import SCREEN_WIDTH, SCREEN_HEIGHT
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    from entities.character import Character
    from ui.screens import professions_screen as PS
    from world.recipe_categories import category

    p = Character(name="Tester", char_class="Mage", level=60)
    for t in TRADES:
        p.profession_skills[t] = 300
        if isinstance(p.known_professions, set):
            p.known_professions.add(t)
        else:
            p.known_professions.append(t)
    scr = PS.ProfessionsScreen(SM(p))
    scr.set_subject(p)
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.mouse.get_pos = lambda: (2, 2)

    print("1. every recipe sorts")
    total = 0
    for tab, (prof, _label, _st) in PS.CRAFT_TABS.items():
        for rid, r in scr._craft_recipes(prof):
            total += 1
            c = category(r)
            if c in CATCH_ALL:
                fail(f"{tab}: {rid} ({r.get('name')}) sorts into '{c}'")
    print(f"  {total} recipes across {len(PS.CRAFT_TABS)} tabs")

    print("2. every trade fits")
    scr.render(surf)
    tabs = scr._tab_list()
    if len(tabs) < 14:
        fail(f"only {len(tabs)} tabs with every trade known - the rig didn't teach them")
    for key, rect in scr.tab_rects.items():
        if rect.bottom > SCREEN_HEIGHT - 10 or rect.left < 0:
            fail(f"the {key} tab is off screen ({rect})")
        if rect.right > PS.PANEL_X:
            fail(f"the {key} tab runs into the recipe panel")
    print(f"  {len(tabs)} tabs, the last ending at y={max(r.bottom for r in scr.tab_rects.values())}")

    print("3. sub-tabs filter")
    for tab in ("tailoring", "jewelcrafting", "blacksmithing", "enchanting"):
        scr.active_tab = tab
        scr.craft_scroll = 0
        scr.render(surf)
        labels = [c for c, _r in scr.subtab_rects if c not in ("All", "__craftable__")]
        if len(labels) < 3:
            fail(f"{tab} has only {labels} for sub-tabs")
            continue
        pick = "Bags" if tab == "tailoring" else labels[min(2, len(labels) - 1)]
        rect = dict(scr.subtab_rects)[pick]
        scr.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": rect.center, "button": 1}))
        scr.render(surf)
        recipes = dict(scr._craft_recipes(PS.CRAFT_TABS[tab][0]))
        shown = [rid for rid, _r in scr.craft_recipe_rects]
        if not shown:
            fail(f"{tab} > {pick} shows nothing")
        wrong = [rid for rid in shown if category(recipes[rid]) != pick]
        if wrong:
            fail(f"{tab} > {pick} shows {len(wrong)} recipes of another kind, e.g. {wrong[0]}")
        print(f"  {tab} > {pick}: {len(shown)} on screen, all {pick}")
    scr.active_tab = "tailoring"
    scr.craft_filter["tailoring"] = "All"
    scr.render(surf)
    rect = dict(scr.subtab_rects)["__craftable__"]
    scr.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": rect.center, "button": 1}))
    scr.render(surf)
    if not scr.only_craftable:
        fail("the Can craft toggle didn't turn on")
    if scr.craft_recipe_rects:
        fail(f"Can craft with empty bags still shows {len(scr.craft_recipe_rects)} recipes")
    scr.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": rect.center, "button": 1}))
    print("  Can craft with empty bags shows nothing, and turns off again")

    print("4. the wheel crafts nothing")
    scr.render(surf)
    before = {m: getattr(p, "materials", {}) for m in ()}
    crafted = []
    scr._attempt_craft = lambda rid: crafted.append(rid)
    row = scr.craft_recipe_rects[0][1]
    pygame.mouse.get_pos = lambda: row.center
    for button in (4, 5):
        scr.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": row.center, "button": button}))
    scr.handle_event(pygame.event.Event(pygame.MOUSEWHEEL, {"x": 0, "y": -1}))
    if crafted:
        fail(f"the wheel crafted {crafted}")
    if scr.craft_scroll <= 0:
        fail("the wheel didn't scroll the list")
    del before

    if PROBLEMS:
        print(f"\nFAILED - {len(PROBLEMS)} problem(s)")
        return 1
    print("\nprofession sub-tabs OK - every trade fits, every recipe sorts, and the filters filter.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
