#!/usr/bin/env python3
"""Every shop in the game opens.

    PYTHONPATH=. python3 tools/qa_every_shop_opens.py

Kyle, 13 Nov 2026, a crash on opening a vendor: "TypeError: '<' not supported between instances of
'NoneType' and 'int'" in VendorScreen._build_vendor_stock. A recipe scroll has vendor_price=None
and the stock was sorted on that field raw, so ANY shop selling a recipe beside a potion crashed -
39 of them. Nothing had ever opened every shop.

This builds the real VendorScreen for every vendor record, and fails on an exception, on a sell id
that resolves to nothing, or on a price that is not a positive whole number.
"""
import contextlib
import io
import json
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
    from ui.screens.vendor_screen import VendorScreen
    from world.vendor_manager import VendorManager
    from entities.character import Character
    from entities.party import Party

    class _SM:
        def __init__(self):
            self.player = Character(name="Shopper", char_class="Warrior", level=60)
            self._party = Party(self.player)

        def get_party(self):
            return self._party

        def transition_to(self, *a, **k):
            pass
    sm = _SM()
    vendors = list(VendorManager().vendors.values())
    want = len(json.loads((ROOT / "data/npcs/vendors.json").read_text(encoding="utf-8"))["vendors"])
    bad = []
    for v in vendors:
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                scr = VendorScreen(sm, v)
        except Exception as e:                       # noqa: BLE001 - the point is to catch any
            bad.append(f"{v.vendor_id}: {type(e).__name__}: {e}")
            continue
        if "unknown sell ID" in out.getvalue():
            bad.append(f"{v.vendor_id}: " + out.getvalue().strip().splitlines()[0])
        for it in scr.vendor_inventory:
            p = scr._unit_price(it)
            if not isinstance(p, int) or p <= 0:
                bad.append(f"{v.vendor_id}: {getattr(it, 'name', it)} costs {p!r}")
    print(f"{len(vendors)} shops opened (of {want} on record)")
    if len(vendors) != want:
        bad.append(f"only {len(vendors)} of {want} vendor records were loaded")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad[:40]:
            print("  -", b)
        return 1
    print("\nEvery shop opens OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
