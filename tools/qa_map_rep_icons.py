#!/usr/bin/env python3
"""Every reputation quartermaster gets the map's banner icon, and the secret faction's seller never does.

    PYTHONPATH=. python3 tools/qa_map_rep_icons.py

Kyle, 17 Nov 2026: "Let's have a map icon for Rep Vendors? So they're easy to find." The map screen
(ui/screens/map_screen.py) draws a lime banner instead of the shop's coin on anyone world.faction_manager.
quartermaster_ids() names. This checks the list against the data:
  1  every non-secret faction with a shelf has its quartermaster listed, and that vendor exists in a zone
  2  no secret faction's vendor is listed (nothing may point at the ???? seller)
  3  the glyph draws (a lime pixel lands on a blank surface), and the legend names it
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


def main():
    from world.faction_manager import quartermaster_ids
    bad = []
    qms = quartermaster_ids()
    facs = json.loads(Path("data/factions/factions.json").read_text(encoding="utf-8"))["factions"]
    vendors = {v["vendor_id"]: v for v in json.loads(Path("data/npcs/vendors.json").read_text(encoding="utf-8"))["vendors"]}
    for fid, f in facs.items():
        shelf = (f.get("rewards") or {}).get("vendor_stock") or {}
        for vid in shelf:
            if f.get("secret"):
                if vid in qms:
                    bad.append(f"secret faction {fid}'s seller {vid} would get a map icon")
                continue
            if vid not in qms:
                bad.append(f"{fid}: quartermaster {vid} has no map icon")
            if vid not in vendors or not vendors[vid].get("zone"):
                bad.append(f"{fid}: quartermaster {vid} isn't a placed vendor")
    import pygame
    pygame.init()
    pygame.display.set_mode((64, 64))
    from ui.screens import map_screen as MS
    surf = pygame.Surface((40, 40))
    scr = MS.MapScreen.__new__(MS.MapScreen)
    MS.MapScreen._draw_service_icon(scr, surf, "rep", 20, 20)
    if not any(tuple(surf.get_at((x, y)))[:3] == MS.REP_LIME for x in range(40) for y in range(40)):
        bad.append("the rep glyph drew nothing")
    if '("rep", "Reputation quartermaster")' not in Path("ui/screens/map_screen.py").read_text(encoding="utf-8"):
        bad.append("the map legend doesn't name the rep glyph")
    for b in bad:
        print("  FAIL", b)
    print(f"{len(qms)} quartermasters carry the banner; {'FAILED' if bad else 'ok'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
