#!/usr/bin/env python3
"""The sell panel must be able to reach gear that sits past row nine.

    PYTHONPATH=. python3 tools/qa_vendor_sell_panel.py

Kyle, 2026-10-31: "I also need a way to scroll down or sell stuff by tabs - since
this forces me to sell crafting materials before my trash gear."

The scroll offsets had existed since this screen was written and were threaded
through every list slice and every hit test. Nothing ever assigned to them. The
panel was frozen on its first nine rows, and since _player_stock concatenates
consumables + materials + inventory in that order, gear is precisely what fell
off the bottom.

This drives the real screen with a stocked player and checks the two ways out:
the wheel, and the tabs. The clamp cases matter as much as the scroll - the list
SHRINKS as you sell, so an unclamped offset strands the player on a blank page.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

from ui.screens.vendor_screen import VendorScreen  # noqa: E402

FAILS = []


def check(label, cond, detail=""):
    if cond:
        print(f"  ok   {label}")
    else:
        FAILS.append(label)
        print(f"  FAIL {label}  {detail}")


class _Stub:
    pass


def build():
    """A player carrying more than one page, with the gear deliberately last."""
    from entities.loot_generator import LootGenerator
    from entities.consumable_manager import get_consumable_manager
    from world.gathering_manager import GatheringNodeManager

    lg = LootGenerator()
    gm = GatheringNodeManager()
    cm = get_consumable_manager()

    player = _Stub()
    player.consumables = [cm.get_consumable("healing_potion_minor", quantity=3)]
    player.materials = [m for m in (gm.make_material_instance(mid) for mid in
                                    ("ore_copper", "ore_tin", "crystal_azure",
                                     "vial_empty", "flux_weak", "thread_coarse",
                                     "bar_copper", "herb_peacebloom", "wood_ashwood",
                                     "ore_weakstone"))
                        if m]
    player.inventory = [g for g in (lg.generate_item_for_class("warrior", 10)
                                    for _ in range(4)) if g]
    player.auto_sell_junk = False
    player.equipment = _Stub()
    player.equipment.to_dict = lambda: {}

    party = _Stub()
    party.add_currency = lambda n: None
    party.remove_currency = lambda n: True
    party.get_currency_string = lambda: "0c"

    sm = _Stub()
    sm.player = player
    sm.get_party = lambda: party
    sm.transition_to = lambda s: None

    vendor = _Stub()
    vendor.name = "Test Vendor"
    vendor.vendor_id = "test"
    vendor.greeting = ""
    vendor.sells = []
    vendor.sells_gear = False
    vendor.buys_from_player = True

    return VendorScreen(sm, vendor), player


def main():
    pygame.init()
    pygame.display.set_mode((1280, 720))
    screen, player = build()

    total = len(screen._player_stock(filtered=False))
    check("the test player overflows one page",
          total > screen.VISIBLE_ROWS, f"only {total} items")

    # ---- 1. gear is off the first page, which is the bug being fixed ----------
    first_page = screen._player_stock()[:screen.VISIBLE_ROWS]
    check("gear is NOT reachable without scrolling (the reported symptom)",
          not any(screen._category_of(i) == "gear" for i in first_page))

    # ---- 2. the wheel moves the sell list ------------------------------------
    PLAYER_POS = (screen.PLAYER_PANEL_X + 20, screen.PANEL_Y + 20)
    VENDOR_POS = (screen.VENDOR_PANEL_X + 20, screen.PANEL_Y + 20)

    def wheel(pos, y):
        screen.handle_event(pygame.event.Event(pygame.MOUSEWHEEL, {"x": 0, "y": y, "pos": pos}))

    wheel(PLAYER_POS, -1)
    check("wheel down scrolls the sell list", screen.scroll_player == 1,
          f"scroll_player={screen.scroll_player}")

    for _ in range(200):
        wheel(PLAYER_POS, -1)
    check("scroll clamps at the end, never past it",
          screen.scroll_player == max(0, total - screen.VISIBLE_ROWS),
          f"scroll_player={screen.scroll_player}, expected {total - screen.VISIBLE_ROWS}")
    check("gear IS visible once scrolled to the end",
          any(screen._category_of(i) == "gear" for i in
              screen._player_stock()[screen.scroll_player:screen.scroll_player + screen.VISIBLE_ROWS]))

    for _ in range(200):
        wheel(PLAYER_POS, 1)
    check("scroll clamps at zero", screen.scroll_player == 0)

    # ---- 3. the wheel over the VENDOR panel must not move the sell list ------
    before = screen.scroll_player
    wheel(VENDOR_POS, -1)
    check("wheel over the vendor panel leaves the sell list alone",
          screen.scroll_player == before)

    # ---- 4. tabs filter, and reach gear with no scrolling at all -------------
    for key, _label in screen.SELL_FILTERS:
        screen.sell_filter = key
        got = screen._player_stock()
        if key == "all":
            check("tab 'all' shows everything", len(got) == total)
        else:
            check(f"tab {key!r} shows only {key}",
                  all(screen._category_of(i) == key for i in got),
                  f"{[screen._category_of(i) for i in got]}")

    screen.sell_filter = "gear"
    check("gear tab puts gear on the first page with no scrolling",
          len(screen._player_stock()) > 0
          and all(screen._category_of(i) == "gear"
                  for i in screen._player_stock()[:screen.VISIBLE_ROWS]))

    # ---- 5. trash is Junk, not Gear ------------------------------------------
    # Vendor trash is a LootItem WITH a slot and an armor_value, so _is_gear says
    # yes to it. If _category_of tested gear first, the Junk tab would be empty
    # and the Gear tab full of grey rubbish.
    from entities.loot_item import LootItem
    trash = LootItem(item_id="qa_trash", name="Chipped Tusk", rarity="poor",
                     sell_price=3, category="trash")
    player.inventory.append(trash)
    check("vendor trash files under Junk, not Gear",
          screen._category_of(trash) == "junk")

    # ---- 6. the shrink case: sell down and the offset must follow ------------
    screen.sell_filter = "all"
    screen.scroll_player = screen._max_scroll(len(screen._player_stock()))
    player.inventory.clear()
    player.materials.clear()
    screen._clamp_scrolls()
    check("selling the tail pulls the scroll back in range",
          screen.scroll_player <= screen._max_scroll(len(screen._player_stock())))
    check("and the remaining page is not blank",
          len(screen._player_stock()[screen.scroll_player:]) > 0)

    print(f"\n{len(FAILS)} failed" if FAILS else "\nsell panel scrolls and filters")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
