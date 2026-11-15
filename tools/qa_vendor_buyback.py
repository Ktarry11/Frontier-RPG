#!/usr/bin/env python3
"""Buyback at vendors, and the shop's own sorting tabs.

    PYTHONPATH=. python3 tools/qa_vendor_buyback.py

Playtest, 14 Nov 2026 (a friend's notes): no buyback at vendors. And Kyle: "Lets make sorting tabs for
almost everything bro".

  1. Selling gear, part of a stack, and a material puts each on the Buyback tab; selling more of the
     same stack grows its row instead of adding one.
  2. Buying back costs what you were paid, and gives back exactly what was sold.
  3. The list keeps the last twelve, newest first.
  4. The shop's tabs show only their kind.
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


class _Stub:
    pass


def main():
    pygame.init()
    from config import SCREEN_WIDTH, SCREEN_HEIGHT
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    from entities.character import Character
    from entities.party import Party
    from entities.consumable_manager import get_consumable_manager
    from entities.loot_generator import LootGenerator
    from world.gathering_manager import GatheringNodeManager
    from ui.screens.vendor_screen import VendorScreen

    p = Character(name="Tester", char_class="Warrior", level=30)
    party = Party(p)
    party.add_currency(100000)
    gear = LootGenerator().generate_item_for_class("Warrior", 30, rarity="rare", player_level=30)
    p.inventory.append(gear)
    pots = get_consumable_manager().get_consumable("healing_potion_minor", quantity=5)
    p.add_consumable(pots)
    ore = GatheringNodeManager().make_material_instance("ore_copper")
    ore.quantity = 4
    p.add_material(ore)

    sm = _Stub()
    sm.player = p
    sm.get_party = lambda: party
    sm.transition_to = lambda s: None
    vendor = _Stub()
    vendor.name, vendor.vendor_id, vendor.greeting = "Test Vendor", "test", ""
    vendor.sells = ["healing_potion_minor", "ore_copper", "thread_coarse"]
    vendor.sells_gear = False
    vendor.buys_from_player = True
    scr = VendorScreen(sm, vendor)
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    print("1. selling puts things on the Buyback tab")
    for thing in (gear,):
        scr.selected_player_item = thing
        scr._sell_item()
    potion = next(c for c in p.consumables if c.consumable_id == "healing_potion_minor")
    scr.selected_player_item = potion
    scr._sell_item()
    scr._sell_item()
    mat = next(m for m in p.materials if m.material_id == "ore_copper")
    scr.selected_player_item = mat
    scr._sell_item()
    bb = scr._buyback()
    names = [(e["item"].name, getattr(e["item"], "quantity", None)) for e in bb]
    check("three rows: the ore, the potions (2), the gear, newest first",
          len(bb) == 3 and bb[0]["item"].name == mat.name and bb[1]["item"].quantity == 2
          and bb[2]["item"] is gear, str(names))

    print("2. buying back")
    scr.buy_filter = "buyback"
    scr.render(surf)
    before = party.copper
    scr.selected_vendor_item = bb[1]["item"]
    scr._buy_back()
    paid = before - party.copper
    left = next(c for c in p.consumables if c.consumable_id == "healing_potion_minor").quantity
    check("two potions came back for what they sold for", left == 5 and paid == 2 * potion.sell_price,
          f"have {left}, paid {paid}")
    before = party.copper
    scr.selected_vendor_item = next(e["item"] for e in scr._buyback() if e["item"] is gear)
    scr._buy_back()
    check("the gear came back, the same item", gear in p.inventory and before - party.copper == gear.sell_price)
    check("bought-back rows leave the list", len(scr._buyback()) == 1)

    print("3. twelve at most")
    for i in range(15):
        g = LootGenerator().generate_item_for_class("Warrior", 20, rarity="uncommon", player_level=20)
        p.inventory.append(g)
        scr.selected_player_item = g
        scr._sell_item()
    check("twelve kept", len(scr._buyback()) == VendorScreen.BUYBACK_MAX, str(len(scr._buyback())))

    print("4. the shop's tabs")
    for key in ("supplies", "mats"):
        scr.buy_filter = key
        shown = scr._vendor_list()
        check(f"{key} shows only {key}", shown and all(scr._vendor_category(i) == key for i in shown),
              str([i.name for i in shown]))
    scr.buy_filter = "all"
    scr.render(surf)

    if BAD:
        print(f"\nFAILED - {len(BAD)}")
        return 1
    print("\nvendor buyback OK - what you sell can be bought back for what you got, and the shop sorts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
