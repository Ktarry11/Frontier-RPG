#!/usr/bin/env python3
"""Hidden sellers rotate their gear every twelve market hours, and sell it at three quarters of the old price.

    PYTHONPATH=. SDL_VIDEODRIVER=dummy python3 tools/qa_secret_rotation.py

Kyle, 17 Nov 2026: "make like 25% cheaper for weapon and armor from these vendors" and "they have 6 or 7 blue items
but only 3 to 4 are at once. They can follow 12 hour rotations with the time passing like how the AH passes."
Counts only, never where (Kyle's rule for secrets).
  1. every hidden seller that sells gear for gold has a pool of six or seven, and every piece in it can be made
  2. every piece costs 75% of its full price
  3. the shelf shows four, the same four all through a window, and a different draw in the next
  4. over a few days every piece in a pool comes round
  5. reputation quartermasters never rotate
  6. the real vendor screen, with a real market clock, shows the window's four and says when new stock comes;
     moving the market clock twelve hours changes the shelf when the shop is opened again
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

fails = []


def check(ok, msg):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}")
    if not ok:
        fails.append(msg)


def main():
    from world.vendor_manager import VendorManager
    from world.vendor_rotation import shelf, SHOWN, ROTATION_HOURS
    from world.vendor_stock import make_unique
    items = json.loads(Path("data/items/secret_uniques.json").read_text(encoding="utf-8"))["items"]
    vm = VendorManager()
    # Easter eggs (tools/build_easter_eggs.py, Kyle 20 Nov 2026) are hidden, but they're a joke with one piece, not a
    # rotating shelf: they keep their own stock
    hidden = [v for v in vm.vendors.values() if getattr(v, "hidden", False) and not getattr(v, "barter", None)
              and not v.vendor_id.startswith("egg_")]
    pools = {v.vendor_id: [s for s in v.sells if s.startswith("unique:")] for v in hidden}
    gear = {k: p for k, p in pools.items() if p}
    # 1
    small = [k for k, p in gear.items() if len(p) < 6]
    check(not small, f"{len(gear)} hidden sellers carry gear, every one a pool of six or seven ({len(small)} short)")
    broken = [s for p in gear.values() for s in p if make_unique(s[len('unique:'):]) is None]
    check(not broken, f"every piece in every pool can be made ({len(broken)} can't)")
    # 2
    off = [k for k, d in items.items() if d.get("price") != int(round(d.get("price_full", 0) * 0.75))]
    check(not off, f"every one-of-a-kind piece is at 75% of its full price ({len(off)} aren't)")
    # 3 and 4
    same, differ, all_seen, shown_ok = 0, 0, 0, 0
    for v in hidden:
        if not gear.get(v.vendor_id):
            continue
        a = [s for s in shelf(v, v.sells, 1.0) if s.startswith("unique:")]
        b = [s for s in shelf(v, v.sells, ROTATION_HOURS - 0.5) if s.startswith("unique:")]
        c = [s for s in shelf(v, v.sells, ROTATION_HOURS + 0.5) if s.startswith("unique:")]
        shown_ok += len(a) == SHOWN
        same += a == b
        differ += set(a) != set(c)
        seen = set()
        for w in range(14):                       # a week of windows
            seen |= {s for s in shelf(v, v.sells, w * ROTATION_HOURS + 1) if s.startswith("unique:")}
        all_seen += seen == set(gear[v.vendor_id])
        rest = [s for s in v.sells if not s.startswith("unique:")]
        if any(s not in shelf(v, v.sells, 5.0) for s in rest):
            fails.append(f"{v.vendor_id}: a recipe or supply left the shelf")
    n = len(gear)
    check(shown_ok == n, f"the shelf shows {SHOWN} pieces ({shown_ok}/{n})")
    check(same == n, f"the same four all through a window ({same}/{n})")
    check(differ >= n * 0.9, f"the next window draws again ({differ}/{n} changed)")
    check(all_seen >= n * 0.9, f"within a week every piece comes round ({all_seen}/{n})")
    # 5
    quarter = [v for v in vm.vendors.values() if not getattr(v, "hidden", False)
               and sum(1 for s in v.sells if str(s).startswith("unique:")) > SHOWN]
    check(all(shelf(v, v.sells, 7.0) == list(v.sells) for v in quarter),
          f"reputation quartermasters never rotate ({len(quarter)} with more than {SHOWN})")
    # 6
    import pygame
    pygame.init()
    surf = pygame.display.set_mode((1280, 720))
    from core.game_state import GameStateManager
    from entities.character import Character
    from world.market.market import market_of
    from ui.screens.vendor_screen import VendorScreen
    sm = GameStateManager(surf)
    sm.player = Character(name="Hero", char_class="Warrior", level=40)
    party = sm.get_party()
    m = market_of(party)
    v = next(v for v in hidden if gear.get(v.vendor_id))
    try:
        scr = VendorScreen(sm, v)
    except TypeError:
        scr = VendorScreen(sm, vendor=v)
    names = lambda: sorted(getattr(i, "name", "") for i in scr.vendor_inventory if hasattr(i, "slot"))  # noqa: E731
    first = names()
    check(len(first) == SHOWN, f"the screen shows {len(first)} pieces")
    scr.render(surf)
    m.advance(ROTATION_HOURS)
    scr.on_open()
    second = names()
    check(first != second, "twelve market hours later the shelf has turned over")
    print("secret rotation OK" if not fails else f"FAILED: {len(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
