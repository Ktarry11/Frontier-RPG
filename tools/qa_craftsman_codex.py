#!/usr/bin/env python3
"""MerchantTusk's Craftsman Codex: one more primary profession slot, 100/200/300/400 gold, then 500 each.

    PYTHONPATH=. SDL_VIDEODRIVER=dummy python3 tools/qa_craftsman_codex.py

Kyle, 16 Nov 2026: "I want merchant Tusk to sell a 'Craftsman Codex' Which unlocks additional Crafting Slots. First
Codex is 100g, then 200g, then 300g, then 400g, then each additional one is 500g and won't go past that point!"

  1. The prices run 100, 200, 300, 400, then 500 for every one after, and never more.
  2. A codex lets the character learn one more primary trade, and the trainer's count says so.
  3. Without the gold nothing changes; the purse pays exactly the price.
  4. Once every primary trade has a slot, Tusk stops selling them.
  5. The slots survive a save and load.
  6. The button is on Tusk's screen, inside it, and clicking it buys one.
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


def main():
    pygame.init()
    from config import SCREEN_WIDTH, SCREEN_HEIGHT
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    from entities.character import Character
    from entities.party import Party
    from world import craftsman_codex as CC
    from world import profession_manager as PM

    p = Character(name="Tester", char_class="Warrior", level=60)
    party = Party(p)
    primaries = [k for k, d in PM.professions().items() if d.get("kind") != "secondary"]

    # 1. prices
    seen = []
    party.copper = 10 ** 9
    while CC.price(p) is not None and len(seen) < 30:
        cost = CC.price(p)
        before = party.copper
        ok, _msg = CC.buy(p, party)
        seen.append(cost // CC.GOLD)
        if before - party.copper != cost:
            BAD.append(f"codex {len(seen)} cost {before - party.copper}, priced {cost}")
    want = [100, 200, 300, 400] + [500] * (len(primaries) - 3 - 4)
    check(f"prices run {want}", seen == want, f"got {seen}")
    check("never more than 500 gold", max(seen) <= 500)
    # 4. stops at every trade
    check("Tusk stops selling once every primary trade has a slot",
          CC.price(p) is None and PM.max_primary(p) == len(primaries), f"{PM.max_primary(p)} slots")
    ok, _msg = CC.buy(p, party)
    check("buying past that does nothing", not ok and PM.max_primary(p) == len(primaries))

    # 2. a fourth trade
    q = Character(name="Q", char_class="Warrior", level=20)
    for prof in primaries[:3]:
        q.learn_profession(prof)
    check("three trades fill the base slots", not q.learn_profession(primaries[3]))
    party_q = Party(q)
    party_q.copper = 99 * CC.GOLD
    ok, _msg = CC.buy(q, party_q)
    check("99 gold doesn't buy a 100 gold codex", not ok and party_q.copper == 99 * CC.GOLD and q.codices == 0)
    party_q.copper = 100 * CC.GOLD
    ok, msg = CC.buy(q, party_q)
    check("100 gold buys the first codex", ok and party_q.copper == 0, msg)
    check("a codex lets you learn a fourth trade", q.learn_profession(primaries[3]))
    rows = PM.offers(q, primaries[4])
    check("the trainer counts four slots", any("4 professions" in str(r.get("reason", "")) for r in rows),
          str([r.get("reason") for r in rows]))

    # 5. save and load
    again = Character.from_dict(q.to_dict()) if hasattr(Character, "from_dict") else None
    check("the codex survives a save", again is not None and again.codices == 1 and PM.max_primary(again) == 4)

    # 6. Tusk's screen
    from ui.screens import bank_screen as BS
    r = Character(name="R", char_class="Warrior", level=20)
    party_r = Party(r)
    party_r.copper = 150 * CC.GOLD
    scr = BS.BankScreen(_SM(r, party_r))
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    scr.render(surf)
    check("the codex button sits on the screen", surf.get_rect().contains(scr.codex_rect))
    check("it doesn't cover the backpack or the deposit button",
          not scr.codex_rect.colliderect(scr.deposit_all_rect)
          and not any(scr.codex_rect.colliderect(c) for c in scr.player_rects[:16]))
    scr.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": scr.codex_rect.center, "button": 1}))
    check("clicking it buys one", r.codices == 1 and party_r.copper == 50 * CC.GOLD, scr.message)
    scr.render(surf)
    if len(sys.argv) > 1:
        pygame.image.save(surf, sys.argv[1])

    if BAD:
        print(f"\nFAIL ({len(BAD)})")
        return 1
    print("\nPASS - the Craftsman Codex: 100, 200, 300, 400, then 500 gold, one more trade each")
    return 0


if __name__ == "__main__":
    sys.exit(main())
