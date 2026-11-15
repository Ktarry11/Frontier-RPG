#!/usr/bin/env python3
"""The bag's sub-tabs filter, and a click on a filtered grid means the item you clicked.

    PYTHONPATH=. SDL_VIDEODRIVER=dummy python3 tools/qa_bag_subtabs.py

Kyle, 14 Nov 2026: "Lets make sorting tabs for almost everything bro". The gear grid is matched to the
bag by position, so a filter that drew the right items but clicked by the old positions would equip
or discard the wrong thing. This checks both, on the Gear and Consumables tabs.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import pygame  # noqa: E402

BAD = []


def main():
    pygame.init()
    from config import SCREEN_WIDTH, SCREEN_HEIGHT
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    from entities.character import Character
    from entities.consumable_manager import get_consumable_manager
    from ui.screens import inventory_screen as IS
    from world import crafted_items
    sys.path.insert(0, str(ROOT / "tools"))
    from qa_profession_subtabs import SM

    p = Character(name="Tester", char_class="Warrior", level=60)
    B = json.loads((ROOT / "data/blacksmithing/recipes.json").read_text(encoding="utf-8"))["recipes"]
    J = json.loads((ROOT / "data/jewelcrafting/recipes.json").read_text(encoding="utf-8"))["recipes"]
    armour = [r for r in B.values() if r["output"].get("kind") == "armor"][:4]
    rings = [r for r in J.values() if r["output"].get("kind") == "armor"][:3]
    for r in armour + rings:
        p.inventory.append(crafted_items.build(r))
    cm = get_consumable_manager()
    for cid in ("healing_potion_minor", "elixir_of_agility", "bread_and_cheese"):
        c = cm.get_consumable(cid, 3)
        if c is not None:
            p.add_consumable(c)

    scr = IS.InventoryScreen(SM(p))
    scr.set_subject(p)
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.mouse.get_pos = lambda: (2, 2)

    # gear: the Jewellery tab shows only jewellery, and its first cell is the first ring in the bag
    scr.active_tab = "gear"
    scr.render(surf)
    rect = scr.gear_subtab_rects.get("jewellery")
    if rect is None:
        BAD.append("no Jewellery sub-tab on the gear tab")
    else:
        scr.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": rect.center, "button": 1}))
        scr.render(surf)
        shown = scr._shown_inventory(p)
        kinds = {IS.gear_subtab(p.inventory[i]) for i in shown}
        if kinds != {"jewellery"}:
            BAD.append(f"the Jewellery tab shows {kinds}")
        first_ring = p.inventory[shown[0]]
        cell = scr.inventory_rects[0]
        if scr._get_hovered_item(cell.center, p) is not first_ring:
            BAD.append("hovering the first Jewellery cell shows a different item")
        scr.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": cell.center, "button": 1}))
        worn = [s for s, it in p.equipment.slots.items() if it is first_ring]
        if not worn:
            BAD.append("clicking the first Jewellery cell didn't equip that ring "
                       "(the click went to another bag position)")
        else:
            print(f"  Jewellery tab: {len(shown)} shown, clicking the first equipped {first_ring.name} in {worn[0]}")

    # consumables: the Potions tab shows only potions, and the cell is that potion
    scr.active_tab = "consumables"
    scr.render(surf)
    rect = scr.consumable_subtab_rects.get("potions")
    if rect is None:
        BAD.append("no Potions sub-tab on the consumables tab")
    else:
        scr.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": rect.center, "button": 1}))
        scr.render(surf)
        shown = scr._shown_consumables(p)
        if not shown or {IS.consumable_subtab(c) for c in shown} != {"potions"}:
            BAD.append(f"the Potions tab shows {[c.consumable_id for c in shown]}")
        else:
            print(f"  Potions tab: {[c.name for c in shown]}")

    if BAD:
        print("\nFAILED:")
        for b in BAD:
            print("  -", b)
        return 1
    print("bag sub-tabs OK - each shows only its kind, and a click means the item clicked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
