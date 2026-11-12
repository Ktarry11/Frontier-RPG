"""
Stackable goods can be bought more than one at a time.

Kyle, 12 Nov: "When buying stuff from shop (like crafting reagents/food/drink) - should be
able to buy more than one at a time."

A real Character, a real Party purse and real vendors from the vendor manager; every purchase
driven through the screen's own event handler with clicks on its own button rects.

  - +, +5, +20, - set the quantity; Buy takes exactly that many and charges exactly n x price
  - the selection and quantity survive the purchase, so the order can be repeated
  - not enough gold buys NOTHING and charges nothing
  - picking a different item resets the quantity to 1
  - gear is always one, and shows no quantity controls
  - the screen renders with the controls up
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PROBLEMS = []


def fail(msg):
    PROBLEMS.append(msg)
    print(f"  FAIL {msg}")


def ok(msg):
    print(f"  ok   {msg}")


def main():
    import pygame
    pygame.init()
    surface = pygame.display.set_mode((1280, 720))
    from entities.character import Character
    from entities.party import Party
    from ui.screens.vendor_screen import VendorScreen
    from world.vendor_manager import get_vendor_manager

    class SM:
        def __init__(self):
            self.player = Character(name="Buyer", char_class="Warrior", level=30)
            self._party = Party(self.player)

        def get_party(self):
            return self._party

        def transition_to(self, *a, **k):
            pass

    def click(scr, rect):
        scr.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=rect.center, button=1))

    def pick(scr, item):
        idx = scr.vendor_inventory.index(item)
        scr.scroll_vendor = max(0, min(idx, len(scr.vendor_inventory) - 1))
        click(scr, scr._row_rect(scr.VENDOR_PANEL_X, idx - scr.scroll_vendor))
        return scr.selected_vendor_item is item

    def held(player, item):
        if hasattr(item, "material_id"):
            return sum(m.quantity for m in player.materials if m.material_id == item.material_id)
        return sum(c.quantity for c in player.consumables
                   if c.consumable_id == item.consumable_id)

    # Find a vendor with a consumable, one with a material, and one with gear.
    found = {}
    for vendor in get_vendor_manager().vendors.values():
        sm = SM()
        try:
            scr = VendorScreen(sm, vendor)
        except Exception:
            continue
        for item in scr.vendor_inventory:
            kind = ("gear" if scr._is_gear(item) else
                    "material" if scr._is_material(item) else "consumable")
            found.setdefault(kind, (vendor, item.name))
        if len(found) == 3:
            break
    if len(found) < 3:
        fail(f"rig: could not find vendors selling all three kinds, only {sorted(found)}")
        return 1

    for kind in ("consumable", "material"):
        vendor, name = found[kind]
        sm = SM()
        scr = VendorScreen(sm, vendor)
        item = next(i for i in scr.vendor_inventory if i.name == name)
        unit = scr._unit_price(item)
        party, player = sm.get_party(), sm.player
        party.copper = unit * 1000
        if not pick(scr, item):
            fail(f"{kind}: rig could not select {name}")
            continue
        q = scr._qty_rects()

        click(scr, q["plus20"])
        click(scr, q["plus5"])
        click(scr, q["plus"])
        click(scr, q["minus"])
        if scr.buy_qty != 25:
            fail(f"{kind}: +20, +5, +, - gave a quantity of {scr.buy_qty}, expected 25")
            continue
        before_gold, before_have = party.copper, held(player, item)
        scr.render(surface)
        click(scr, scr._get_buy_button_rect())
        got, paid = held(player, item) - before_have, before_gold - party.copper
        if got != 25 or paid != unit * 25:
            fail(f"{kind} ({name}): bought {got} for {paid}c, expected 25 for {unit * 25}c")
            continue
        if scr.selected_vendor_item is not item or scr.buy_qty != 25:
            fail(f"{kind}: the selection or quantity was lost after buying")
            continue
        click(scr, scr._get_buy_button_rect())
        if held(player, item) - before_have != 50:
            fail(f"{kind}: repeating the order did not buy another 25")
            continue
        ok(f"{kind} ({name}): 25 for {unit * 25}c in one press, and again on a second")

        # Not enough gold: nothing bought, nothing charged.
        party.copper = unit * 3
        have = held(player, item)
        click(scr, scr._get_buy_button_rect())
        if held(player, item) != have or party.copper != unit * 3:
            fail(f"{kind}: with gold for 3, an order of 25 bought "
                 f"{held(player, item) - have} and left {party.copper}c")
        else:
            ok(f"{kind}: an order it cannot afford buys nothing ({scr.message!r})")

        # A different item resets the count.
        other = next((i for i in scr.vendor_inventory if i is not item), None)
        if other is not None:
            pick(scr, other)
            if scr.buy_qty != 1:
                fail(f"{kind}: picking a different item kept the quantity at {scr.buy_qty}")

    # Gear: always one.
    vendor, name = found["gear"]
    sm = SM()
    scr = VendorScreen(sm, vendor)
    item = next(i for i in scr.vendor_inventory if i.name == name)
    sm.get_party().copper = scr._unit_price(item) * 50
    pick(scr, item)
    scr.buy_qty = 9                                   # as if left over from a reagent
    scr.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_PLUS, mod=0, unicode="+"))
    bag = len(sm.player.inventory)
    gold = sm.get_party().copper
    scr.render(surface)
    click(scr, scr._get_buy_button_rect())
    if len(sm.player.inventory) - bag != 1 or gold - sm.get_party().copper != scr._unit_price(item):
        fail(f"gear ({name}): bought {len(sm.player.inventory) - bag} for "
             f"{gold - sm.get_party().copper}c - gear must be exactly one")
    else:
        ok(f"gear ({name}): one, at one price, whatever the quantity was left at")

    if PROBLEMS:
        print(f"\nFAILED - {len(PROBLEMS)} problem(s)")
        return 1
    print("\nbulk buying OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
