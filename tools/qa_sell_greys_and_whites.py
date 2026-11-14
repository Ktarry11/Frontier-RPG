#!/usr/bin/env python3
"""The shop's Sell Greys & Whites button.

    PYTHONPATH=. python3 tools/qa_sell_greys_and_whites.py

Playtest, 14 Nov 2026: "a way to sell all grey and white non junk items at once". Checks that one
click only warns, the second sells every grey and white piece of gear plus the vendor trash, and
that nothing worn, nothing green or better, no set piece and no quest item goes with it.
"""
import contextlib
import io
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def main():
    import pygame
    pygame.init()
    pygame.display.set_mode((1280, 720))
    with contextlib.redirect_stdout(io.StringIO()):
        from entities.character import Character
        from entities.party import Party
        from entities.loot_generator import LootGenerator
        from entities.loot_item import LootItem
        from ui.screens.vendor_screen import VendorScreen
        from world.vendor_manager import get_vendor_manager

    class SM:
        def __init__(self):
            self.player = Character(name="Seller", char_class="Warrior", level=20)
            self._party = Party(self.player)

        def get_party(self):
            return self._party

        def transition_to(self, *a, **k):
            pass

    with contextlib.redirect_stdout(io.StringIO()):
        sm = SM()
        lg = LootGenerator()
        p = sm.player
        made = {}
        for r in ("poor", "common", "uncommon", "rare"):
            made[r] = lg.generate_armor_piece("chest", "plate", "str_physical", 20, r) if r in lg.rarity_tiers else None
        vendor = next(v for v in get_vendor_manager().vendors.values() if v.buys_from_player)
        scr = VendorScreen(sm, vendor)
    bad = []
    if any(v is None for v in made.values()):
        print("could not make test gear", made)
        return 1
    setpiece = lg.generate_armor_piece("legs", "plate", "str_physical", 20, "common")
    setpiece.set_id = "t0_test"
    trash = LootItem("trash_test", "Broken Tooth", category="trash", description="A tooth.", sell_price=7)
    quest = LootItem("quest_test", "Letter", category="quest", description="A letter.")
    p.inventory.extend(list(made.values()) + [setpiece, trash, quest])
    worn = next((i for i in p.equipment.to_dict().values() if i is not None), None)
    before = scr.state_manager.get_party().copper
    scr._sell_all_plain()
    if made["poor"] not in p.inventory:
        bad.append("the first click sold without asking")
    scr._sell_all_plain()
    for r in ("poor", "common"):
        if made[r] in p.inventory:
            bad.append(f"a {r} piece was not sold")
    for r in ("uncommon", "rare"):
        if made[r] not in p.inventory:
            bad.append(f"an {r} piece was sold")
    if trash in p.inventory:
        bad.append("vendor trash was not sold")
    if setpiece not in p.inventory:
        bad.append("a set piece was sold")
    if quest not in p.inventory:
        bad.append("a quest item was sold")
    if worn is not None and worn not in p.equipment.to_dict().values():
        bad.append("something worn was sold")
    if scr.state_manager.get_party().copper <= before:
        bad.append("no money changed hands")
    if scr._get_plain_button_rect().right > 1280:
        bad.append("the button runs off the screen")
    if bad:
        print("\n".join("  - " + b for b in bad))
        return 1
    print("Sell Greys & Whites OK - warns once, sells greys, whites and trash, keeps everything else.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
