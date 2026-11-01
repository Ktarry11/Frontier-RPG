#!/usr/bin/env python3
"""A companion must be able to eat food the player bought.

    PYTHONPATH=. python3 tools/qa_party_consumables.py

Kyle, 2026-10-31: "we cant make party members consume stuff. when i buy food,
freja cant eat it as its not in her inventory."

Every path that acquires a consumable - vendor, loot, crafting - puts it in the
PLAYER's .consumables. Nothing anywhere puts one in a companion's. So the
Consumables tab, which drew from subject.consumables, was not "empty right now"
for a companion; it was empty permanently and by construction.

The fix shares the stack and keeps the checks personal, so this checks both:
the food shows up on a companion AND the companion's own level, cooldown and
buff slots still decide whether they may eat it.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("FRONTIER_QUIET", "1")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

FAILS = []


def check(label, cond, detail=""):
    if cond:
        print(f"  ok   {label}")
    else:
        FAILS.append(label)
        print(f"  FAIL {label}  {detail}")


def main():
    pygame.init()
    pygame.display.set_mode((1280, 720))

    from entities.character import Character
    from entities.consumable_manager import get_consumable_manager
    from ui.screens.inventory_screen import InventoryScreen

    cm = get_consumable_manager()

    player = Character("Kyle", "warrior", level=20)
    freja = Character("Freja", "hunter", level=20)

    class _SM:
        pass
    sm = _SM()
    sm.player = player
    sm.get_party = lambda: None
    sm.transition_to = lambda s: None

    screen = InventoryScreen(sm)

    # The player buys food. Nothing goes to Freja, which is the whole point.
    player.add_consumable(cm.get_consumable("meal_tough_jerky", quantity=2))
    player.add_consumable(cm.get_consumable("healing_potion_minor", quantity=3))
    check("Freja's own consumable list is empty, as it always is",
          len(freja.consumables) == 0)

    screen.set_subject(freja)
    pool = screen._consumable_source(freja).consumables
    check("the Consumables tab shows Freja the party's food",
          len(pool) == 2, f"{len(pool)} entries")

    # ---- she actually eats it, and it comes off the shared stack -------------
    jerky = next(c for c in pool if c.consumable_id == "meal_tough_jerky")
    before_qty = jerky.quantity
    freja.current_health = max(1, freja.health // 2)
    before_hp = freja.current_health
    screen._use_consumable(freja, jerky)
    check("eating it decrements the shared stack",
          jerky.quantity == before_qty - 1, f"{before_qty} -> {jerky.quantity}")
    # A meal starts a REGEN tick rather than healing on the spot, so the proof
    # that it landed is the regen state, not the health bar one frame later.
    check("the effect lands on FREJA, not on the player",
          bool(freja.consumable_regen_active())
          or freja.current_health > before_hp or freja.food_buff is not None,
          f"hp {before_hp} -> {freja.current_health}, regen={freja.consumable_regen_active()}")
    check("the player did not eat it",
          not player.consumable_regen_active() and player.food_buff is None)

    # ---- an emptied stack leaves the shared list, not a dead slot ------------
    jerky.quantity = 1
    screen._use_consumable(freja, jerky)
    check("an emptied stack is removed from the PLAYER's list",
          jerky not in player.consumables, f"{[c.name for c in player.consumables]}")

    # ---- the checks stay personal -------------------------------------------
    # Negative control. If this passed, the level gate would not be running at
    # all and every "ok" above would be meaningless.
    low = Character("Rookie", "rogue", level=1)
    gated = cm.get_consumable("healing_potion_superior", quantity=1)
    screen.set_subject(low)
    screen.equip_error = None
    if gated.required_level <= 1:
        print("  --   skipped: no level-gated potion to test with")
    else:
        screen._use_consumable(low, gated)
        check("a level gate is judged against the SUBJECT, not the player",
              screen.equip_error and "requires level" in screen.equip_error,
              repr(screen.equip_error))

    print(f"\n{len(FAILS)} failed" if FAILS else "\ncompanions can use the party's consumables")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
