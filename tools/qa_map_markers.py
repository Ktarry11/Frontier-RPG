#!/usr/bin/env python3
"""The map's last three painted markers: banks, faction leaders and dungeon doors (22 Nov 2026).

    PYTHONPATH=. python3 tools/qa_map_markers.py

Kyle, 22 Nov 2026: "Can you deal with map icons". Sheet MI1 had three medallions the map didn't use yet. The map screen
(ui/screens/map_screen.py) now draws the strongbox on every banker, the crown on every faction leader data/factions/
factions.json names, and the skull door on any portal into a dungeon. This checks:
  1  the three medallion files exist
  2  every named leader stands somewhere (an ambient NPC or a vendor with a zone), and no secret faction names one
  3  no portal into a hidden zone, and no door on secret ground, ever gets the dungeon marker
  4  at least one real dungeon door does (Ragefire Chasm's, in Orgrimmar)
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def main():
    bad = []
    for name in ("bank", "leader", "dungeon"):
        if not Path(f"assets/icons/map/{name}.png").exists():
            bad.append(f"assets/icons/map/{name}.png is missing")

    from ui.screens.map_screen import MapScreen
    facs = json.loads(Path("data/factions/factions.json").read_text(encoding="utf-8"))["factions"]
    placed = {n["npc_id"] for n in json.loads(Path("data/npcs/ambient_npcs.json").read_text(encoding="utf-8"))["npcs"]
              if n.get("zone")}
    placed |= {v["vendor_id"] for v in json.loads(Path("data/npcs/vendors.json").read_text(encoding="utf-8"))["vendors"]
               if v.get("zone")}
    leaders = MapScreen._leader_ids()
    for fid, f in facs.items():
        lid = (f.get("leader") or {}).get("npc_id")
        if f.get("secret") and lid in leaders:
            bad.append(f"secret faction {fid} would get a crown on the map")
    for lid in sorted(leaders - placed):
        bad.append(f"faction leader {lid} isn't placed anywhere, so the crown never shows")

    from world.hidden_zones import is_hidden
    from world.portal_manager import PortalManager
    from world.secrets import get_secrets

    class _ZM:
        portal_manager = PortalManager()

    zm = _ZM()
    secrets = get_secrets()
    marked = 0
    for (zone, x, y), dest in zm.portal_manager._lookup.items():
        if not MapScreen._leads_to_dungeon(zm, zone, x, y):
            continue
        marked += 1
        if is_hidden(dest[0]):
            bad.append(f"{zone} ({x},{y}) leads into a hidden zone and would show as a dungeon")
        if secrets.is_hidden_tile(zone, x, y):
            bad.append(f"{zone} ({x},{y}) stands on secret ground and would show as a dungeon")
    if not any(MapScreen._leads_to_dungeon(zm, z, x, y) and d[0] == "Ragefire Chasm"
               for (z, x, y), d in zm.portal_manager._lookup.items()):
        bad.append("Ragefire Chasm's door doesn't get the dungeon marker")

    for b in bad:
        print("  FAIL", b)
    print(f"{len(leaders)} leaders crowned, {marked} dungeon doors marked; {'FAILED' if bad else 'ok'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
