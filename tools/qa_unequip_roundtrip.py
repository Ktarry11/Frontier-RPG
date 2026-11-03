#!/usr/bin/env python3
"""
Gear taken off a party member must come back to a bag you can see.

    PYTHONPATH=. python3 tools/qa_unequip_roundtrip.py

Kyle, 2 Nov 2026: "when i unequip party gear its lost in the void."

It was not destroyed - it was parked somewhere with no UI. The inventory
screen's _bag_source always draws the PLAYER's bag when gearing a companion,
but Character.unequip_item appended to the COMPANION's own inventory. Equip out
of one bag, unequip into another: a one-way trip, and the item falls out of the
world while still existing in memory.

What this asserts is the ROUND TRIP, which is the property that was broken:
equip a companion from the player's bag, take it off again, and it must be back
in the bag it came from - not merely "somewhere".

Also covers the second half of the fix. The old code appended straight to the
list and bypassed inventory_capacity, so unequipping into a full bag silently
overflowed it. It now refuses and puts the item back, which must leave the item
EQUIPPED rather than dropped - a refusal that loses the item is the original bug
with extra steps.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


def main():
    from entities.character import Character
    from entities.loot_generator import LootGenerator

    fails = []
    gen = LootGenerator()
    player = Character(name="Hero", char_class="Warrior", level=30)
    mate = Character(name="Mate", char_class="Warrior", level=30)

    def fresh_item():
        # `is_gear` is not an attribute on Item - the screens read it with
        # getattr(..., True), i.e. gear is the default and only LootItem opts
        # out. Testing for it directly skipped every real piece of gear.
        it = gen.generate_item_for_class("Warrior", 30, slot="chest")
        return it if getattr(it, "slot", None) == "chest" else None

    item = fresh_item()
    if item is None:
        print("  SKIP  could not generate a chest item to test with")
        return 0

    # ---- the round trip, exactly as the screen does it. equip_item requires
    # the item to be in the subject's OWN inventory, so the screen hands it
    # across first (_equip_on_subject); mirror that here or we are testing a
    # flow the game does not have.
    player.inventory.append(item)
    player.inventory.remove(item)
    mate.inventory.append(item)
    if not mate.equip_item(item):
        fails.append("could not equip the item onto the companion")
    else:
        ok = mate.unequip_item("chest", into=player)
        if not ok:
            fails.append("unequip returned False with room in the bag")
        if item in mate.inventory:
            fails.append("item went into the COMPANION's bag - the void bug")
        if item not in player.inventory:
            fails.append("item is in NOBODY's bag after unequip - lost")
        if mate.equipment.get_equipped("chest") is not None:
            fails.append("slot still occupied after a successful unequip")

    # ---- a full destination bag must refuse, not drop
    item2 = fresh_item()
    if item2 is not None:
        hoarder = Character(name="Full", char_class="Warrior", level=30)
        wearer = Character(name="Wearer", char_class="Warrior", level=30)
        wearer.inventory.append(item2)
        wearer.equip_item(item2)
        hoarder.inventory = [object()] * hoarder.inventory_capacity
        before = len(hoarder.inventory)
        ok = wearer.unequip_item("chest", into=hoarder)
        if ok:
            fails.append("unequip into a FULL bag reported success")
        if len(hoarder.inventory) != before:
            fails.append(f"full bag grew to {len(hoarder.inventory)} (capacity "
                         f"{hoarder.inventory_capacity}) - overflowed")
        if wearer.equipment.get_equipped("chest") is not item2:
            fails.append("refused unequip did not leave the item equipped - LOST")

    # ---- default destination is still the character's own bag
    solo = Character(name="Solo", char_class="Warrior", level=30)
    item3 = fresh_item()
    if item3 is not None:
        solo.inventory.append(item3)
    if item3 is not None and solo.equip_item(item3):
        solo.unequip_item("chest")
        if item3 not in solo.inventory:
            fails.append("unequipping yourself no longer lands in your own bag")

    if fails:
        for f in fails:
            print(f"  FAIL  {f}")
        return 1
    print("round trip: player bag -> companion -> player bag")
    print("full bag: refused, item stays equipped, no overflow")
    print("solo unequip: lands in own bag")
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
