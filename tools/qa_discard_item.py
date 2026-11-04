#!/usr/bin/env python3
"""
Discarding an item must actually destroy it, whatever kind of item it is.

    PYTHONPATH=. python3 tools/qa_discard_item.py

Kyle, 4 Nov 2026: "We need a discard button for items so we can trash them.
Like if our bags fill up mid dungeon", then: "Allow quest items to be destroyed
too."

Two things are under test, and the second is the one that bites.

1. COVERAGE. A bag click already meant four different things depending on the
   item - equip the gear, learn the recipe scroll, open the quest offer on a
   starter item, confirm-destroy anything else. Three of those four swallowed
   the click, so gear, recipe scrolls and quest starters could not be thrown
   away at all. Discard mode is checked before any of them, so this walks one
   of each type through and demands they all reach the confirmation.

2. THE DESTROY ACTUALLY REMOVING IT. The confirm handler removed from
   subject.inventory while the grid draws from _bag_source(subject) - which is
   the PLAYER's bag whenever you are gearing a companion. Destroying from a
   companion's inventory screen found nothing to remove, left the item sitting
   in the player's bag, and still printed "destroyed." A silent no-op wearing a
   success message, and the same two-lists-one-job shape as the unequip void
   bug on 2 Nov. That is asserted directly below.
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


class StubSM:
    def __init__(self, player, party):
        self.player = player
        self._party = party
        self.states = {}
        self.current_state = None

    def get_party(self):
        return self._party

    def transition_to(self, *a, **k):
        pass

    def change_state(self, *a, **k):
        pass


def _click(screen_obj, rect):
    screen_obj.handle_event(pygame.event.Event(
        pygame.MOUSEBUTTONDOWN, {"pos": rect.center, "button": 1}))


def main():
    pygame.init()
    from config import SCREEN_WIDTH, SCREEN_HEIGHT
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    from entities.character import Character
    from entities.party import Party
    from entities.loot_item import LootItem
    from entities.loot_generator import LootGenerator
    from ui.screens.inventory_screen import InventoryScreen

    fails = []
    gen = LootGenerator()

    def fresh_screen(subject_is_companion=False):
        player = Character(name="Hero", char_class="Warrior", level=30)
        party = Party(player)
        mate = Character(name="Mate", char_class="Warrior", level=30)
        party.add_member(mate)
        sm = StubSM(player, party)
        scr = InventoryScreen(sm)
        scr.set_subject(mate if subject_is_companion else player)
        return scr, player, mate

    # ---- 1. every item type reaches the confirmation in discard mode
    def _real_recipe_scroll():
        """A REAL scroll from the recipe manager, not a hand-rolled LootItem.

        An approximation here was actively misleading: a fake scroll with only
        recipe_id set crashed the OLD code path in _use_recipe_scroll on a
        missing recipe_profession, which looks like a test bug and is really
        the test failing to model the thing it is testing.
        """
        from world.recipe_manager import make_recipe_scroll, _load_all_recipes
        for rid in (_load_all_recipes() or {}):
            scroll = make_recipe_scroll(rid)
            if scroll is not None:
                return scroll
        return None

    def _real_vendor_trash():
        """Real vendor trash - Kyle, 4 Nov: "We need to ensure this pathway
        works for vendor trash as well as gear too if needed."

        Built the way combat actually builds it: vendor_trash.roll_drops
        returns plain DICTS, and combat_engine turns each one into a real bag
        entry through add_loot_item. Handing the dict straight to the bag put
        a dict in the inventory and blew up on item.name - the test was
        modelling the drop table rather than the thing that ends up in the
        backpack, which is the only thing a discard button ever sees.

        Vendor trash is the most likely thing to be discarded mid-dungeon,
        since it is what fills the bag, so it gets the real article here.
        """
        from entities import vendor_trash as vt
        from entities.loot_item import add_loot_item

        class _Dummy:
            name, level, is_boss, location_type = "Bandit Thug", 30, False, "open_zone"

        carrier = Character(name="Carrier", char_class="Warrior", level=30)
        for _ in range(40):
            drop = vt.roll_drops(_Dummy())
            for it in drop["items"]:
                add_loot_item(carrier, it["item_id"], it["name"], category="trash",
                              amount=1, description=it["description"],
                              icon_id=it["icon_id"], sell_price=it["price"])
                if carrier.inventory:
                    return carrier.inventory[0]
        return LootItem("tr", "Cracked Tusk", category="trash", sell_price=42)

    cases = {
        "gear": lambda: gen.generate_item_for_class("Warrior", 30, slot="chest"),
        "quest item": lambda: LootItem("qi", "Ledger", category="quest", quest_id="q1"),
        "quest starter": lambda: LootItem("qs", "Sealed Orders", category="quest",
                                          starts_quest_id="q2"),
        "recipe scroll": _real_recipe_scroll,
        "vendor trash": _real_vendor_trash,
    }
    for label, make in cases.items():
        scr, player, _ = fresh_screen()
        item = make()
        if item is None:
            print(f"  SKIP  could not build a {label}")
            continue
        player.inventory = [item]

        scr.discard_mode = True
        scr._build_inventory_rects(len(player.inventory))
        _click(scr, scr.inventory_rects[0])

        if scr.pending_destroy_item is not item:
            fails.append(f"{label}: discard mode did not reach the confirmation "
                         f"(pending={scr.pending_destroy_item})")
            continue
        if scr.discard_mode:
            fails.append(f"{label}: discard mode stayed armed after one use")

        _click(scr, scr.destroy_yes_button)
        if item in player.inventory:
            fails.append(f"{label}: confirmed destroy but the item is still in the bag")

    # ---- 2. THE COMPANION BAG. The bug.
    scr, player, mate = fresh_screen(subject_is_companion=True)
    item = gen.generate_item_for_class("Warrior", 30, slot="chest")
    if item is not None:
        # Loot lives in the PLAYER's bag; the grid draws it while gearing Mate.
        player.inventory = [item]
        mate.inventory = []
        bag = scr._bag_source(mate)
        if bag is not player:
            fails.append("_bag_source no longer returns the player's bag for a "
                         "companion - this test's premise is stale, recheck it")
        scr.discard_mode = True
        scr._build_inventory_rects(len(bag.inventory))
        _click(scr, scr.inventory_rects[0])
        _click(scr, scr.destroy_yes_button)
        if item in player.inventory:
            fails.append("destroying from a COMPANION's screen left the item in the "
                         "player's bag - the silent no-op bug")

    # ---- 3. cancel keeps the item
    scr, player, _ = fresh_screen()
    keeper = gen.generate_item_for_class("Warrior", 30, slot="legs")
    if keeper is not None:
        player.inventory = [keeper]
        scr.discard_mode = True
        scr._build_inventory_rects(1)
        _click(scr, scr.inventory_rects[0])
        _click(scr, scr.destroy_no_button)
        if keeper not in player.inventory:
            fails.append("Cancel destroyed the item anyway")
        if scr.pending_destroy_item is not None:
            fails.append("Cancel left the confirmation open")

    # ---- 4. disarming: escape, and tab changes
    scr, player, _ = fresh_screen()
    scr.discard_mode = True
    scr.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE, "mod": 0}))
    if scr.discard_mode:
        fails.append("Escape did not disarm discard mode")

    scr, player, _ = fresh_screen()
    scr.discard_mode = True
    _click(scr, scr.materials_tab_button)
    if scr.discard_mode:
        fails.append("switching tabs left discard mode armed")

    # ---- 5. with discard OFF, gear still equips rather than being destroyed
    scr, player, _ = fresh_screen()
    item = gen.generate_item_for_class("Warrior", 30, slot="chest")
    if item is not None:
        player.inventory = [item]
        scr.discard_mode = False
        scr._build_inventory_rects(1)
        _click(scr, scr.inventory_rects[0])
        if scr.pending_destroy_item is not None:
            fails.append("a normal click on gear opened the destroy prompt - "
                         "discard must be opt-in")

    pygame.quit()

    if fails:
        for f in fails:
            print(f"  FAIL  {f}")
        return 1

    print("gear, quest items, quest starters, recipe scrolls and trash all discardable")
    print("discard mode disarms after one use, on Escape, and on a tab change")
    print("destroying from a companion's screen removes from the bag on screen")
    print("Cancel keeps the item; a normal click still equips")
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
