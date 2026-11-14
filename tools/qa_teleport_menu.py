#!/usr/bin/env python3
"""The Teleport menu lists every town and lands you in each one.

    PYTHONPATH=. python3 tools/qa_teleport_menu.py

Kyle, 13 Nov 2026: "change that 'stuck' option into a fast teleport ... teleport to any town ...
a separate menu that replaces the stuck. Remove the hotkey from it." FOUR CLAIMS:
  1. Every innkeeper's town is on the list, once, with a name (world/fast_travel.py).
  2. Teleporting to each one puts you in that zone, on a walkable tile, within three tiles of
     the innkeeper.
  3. The overworld has a Teleport button and no Unstuck button, and U does nothing.
  4. No town's label is a bare zone slug.
"""
import json
import os
import re
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
    pygame.display.set_mode((64, 64))
    from world.zone_manager import ZoneManager
    from world.fast_travel import destinations

    zm = ZoneManager()
    dests = destinations(zm)
    bad = []
    travel = json.loads((ROOT / "data/travel/travel_data.json").read_text(encoding="utf-8"))
    inns = sum(1 for v in travel["services"].values() if "inn" in v)
    if len(dests) != inns:
        bad.append(f"{inns} innkeepers but {len(dests)} towns on the list")
    labels = [d["label"] for d in dests]
    if len(set(labels)) != len(labels):
        bad.append(f"a town is listed twice: {sorted(l for l in set(labels) if labels.count(l) > 1)}")
    for d in dests:
        if "_" in d["label"] or d["label"] != d["label"].strip() or not d["label"][0].isupper():
            bad.append(f"label {d['label']!r} is not a name")
        zm.transition_to_zone(d["zone"], d["x"], d["y"], via_portal=False)
        z = zm.current_zone
        off = max(abs(zm.player_x - d["x"]), abs(zm.player_y - d["y"]))
        if z.name != d["zone"] or not z.is_walkable(zm.player_x, zm.player_y) or off > 3:
            bad.append(f"{d['label']}: landed in {z.name} at {(zm.player_x, zm.player_y)}, "
                       f"{off} tiles from the inn at {(d['x'], d['y'])}")

    src = (ROOT / "ui/screens/overworld_screen.py").read_text(encoding="utf-8")
    if '"Teleport"' not in src or 'self.tab_rects["teleport"]' not in src:
        bad.append("no Teleport button in the tab column")
    if re.search(r'"Unstuck', src) or "K_u:" in src or "K_u)" in src:
        bad.append("the Unstuck button or its U hotkey is still there")

    print(f"{len(dests)} towns: " + ", ".join(labels))
    for b in bad:
        print("  FAIL", b)
    print("\nteleport menu OK - every town is listed and reachable." if not bad else f"\n{len(bad)} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
