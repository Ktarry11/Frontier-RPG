#!/usr/bin/env python3
"""The bank's filter row and Sort button.

    PYTHONPATH=. SDL_VIDEODRIVER=dummy python3 tools/qa_bank_sorting.py

Kyle, 14 Nov 2026: "Lets make sorting tabs for almost everything bro". A bank tab is 48 fixed cells, so
the filter dims rather than hides, and a click on a cell must still mean the item in that cell.

  1. The filter row fits under the bank grid and never reaches the backpack column.
  2. A filter dims what doesn't match, and clicking a lit cell takes out exactly that item.
  3. Sort packs the strongbox by kind (armour before weapons before jewellery), best first, and keeps
     every item: nothing lost, nothing doubled.
  4. Sort on the guild bank goes through its transaction and keeps every item too.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
import pygame  # noqa: E402

BAD = []


def check(label, cond, detail=""):
    print(f"  {'ok  ' if cond else 'FAIL'} {label}" + (f"  {detail}" if not cond and detail else ""))
    if not cond:
        BAD.append(label)


class _SM:
    def __init__(self, player, party):
        self.player, self.party = player, party
        self.icon_ui_helper = None

    def get_party(self):
        return self.party

    def transition_to(self, _s):
        pass


def click(scr, pos):
    scr.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": pos, "button": 1}))


def main():
    pygame.init()
    from config import SCREEN_WIDTH, SCREEN_HEIGHT
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    from entities.character import Character
    from entities.party import Party
    from entities import guild_bank as GB
    from ui.screens import bank_screen as BS
    from ui.screens.inventory_screen import gear_subtab
    from world import crafted_items

    p = Character(name="Tester", char_class="Warrior", level=60)
    party = Party(p)
    B = json.loads((ROOT / "data/blacksmithing/recipes.json").read_text(encoding="utf-8"))["recipes"]
    J = json.loads((ROOT / "data/jewelcrafting/recipes.json").read_text(encoding="utf-8"))["recipes"]
    armour = [crafted_items.build(r) for r in B.values()
              if r["output"].get("kind") == "armor" and not r["output"].get("weapon_type")][:5]
    weapons = [crafted_items.build(r) for r in B.values() if r["output"].get("weapon_type")][:4]
    rings = [crafted_items.build(r) for r in J.values() if r["output"].get("kind") == "armor"][:3]
    # a jumbled strongbox, with gaps
    jumble = [weapons[0], rings[0], None, armour[0], weapons[1], None, rings[1], armour[1],
              armour[2], weapons[2], rings[2], armour[3], weapons[3], armour[4]]
    for i, it in enumerate(jumble):
        party.bank.tabs[0][i] = it
    everything = sorted(id(x) for x in jumble if x is not None)

    scr = BS.BankScreen(_SM(p, party))
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    scr.render(surf)

    print("1. layout")
    right = max(r.right for r in list(scr.filter_rects.values()) + [scr.sort_rect])
    grid_bottom = max(r.bottom for r in scr.bank_rects)
    check("the filter row and Sort sit under the bank grid", scr.sort_rect.top > grid_bottom,
          f"row {scr.sort_rect.top}, grid {grid_bottom}")
    check("and stop before the backpack column", right < BS.PLAYER_X, f"right edge {right}")
    check("and above the message line", scr.sort_rect.bottom < SCREEN_HEIGHT - 44)
    check("seven filters", len(scr.filter_rects) == 7, str(list(scr.filter_rects)))

    print("2. the Weapons filter dims, and a click means the cell clicked")
    click(scr, scr.filter_rects["weapons"].center)
    scr.render(surf)
    check("the filter took", scr.filter == "weapons")
    lit = [i for i, it in enumerate(party.bank.tabs[0]) if it is not None and scr._lit(it)]
    check("only weapons are lit", lit and all(gear_subtab(party.bank.tabs[0][i]) == "weapons" for i in lit),
          str(lit))
    target_i = lit[1]
    target = party.bank.tabs[0][target_i]
    click(scr, scr.bank_rects[target_i].center)
    check("clicking a lit weapon took out that weapon", target in p.inventory and
          party.bank.tabs[0][target_i] is None, scr.message)
    party.bank.tabs[0][target_i] = p.inventory.pop(p.inventory.index(target))

    print("3. Sort")
    click(scr, scr.filter_rects["all"].center)
    click(scr, scr.sort_rect.center)
    tab = party.bank.tabs[0]
    kinds = [gear_subtab(x) for x in tab if x is not None]
    n = len(kinds)
    check("packed to the front, no gaps", all(x is not None for x in tab[:n]) and all(x is None for x in tab[n:]))
    order = ["armour", "weapons", "jewellery"]
    check("armour, then weapons, then jewellery", kinds == sorted(kinds, key=order.index), str(kinds))
    check("every item kept, none doubled", sorted(id(x) for x in tab if x is not None) == everything)
    check("says so", scr.message == "Sorted.", scr.message)
    click(scr, scr.sort_rect.center)
    check("a second Sort changes nothing", scr.message == "Already tidy.", scr.message)

    print("4. the guild bank")
    g = GB.GuildBank()
    g.save = lambda: True
    saved = GB._host_saver
    GB.set_host_saver(lambda: True)
    BS.get_guild_bank = lambda: g
    for i, it in enumerate([rings[0], None, weapons[0], armour[0], None, rings[1]]):
        g.slots[i] = it
    before = sorted(id(x) for x in g.slots if x is not None)
    click(scr, scr.tab_rects[BS.GUILD_TAB].center)
    scr.render(surf)
    click(scr, scr.sort_rect.center)
    gk = [gear_subtab(x) for x in g.slots if x is not None]
    check("the guild bank sorts", gk == sorted(gk, key=order.index) and g.slots[len(gk)] is None, str(gk))
    check("and keeps every item", sorted(id(x) for x in g.slots if x is not None) == before)
    GB.set_host_saver(saved)

    if BAD:
        print(f"\nFAILED - {len(BAD)}")
        return 1
    print("\nbank sorting OK - the filter dims without moving anything, and Sort tidies without losing a thing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
