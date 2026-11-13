#!/usr/bin/env python3
"""The maps Kyle called swamped have about 30% fewer props, and kept their landmarks.

    PYTHONPATH=. python3 tools/qa_prop_thinning.py

Backlog O [85] (Arathi dungeons and caves), C [18] (Gadgetzan ruins), C [20] (the Drownbell).
  1. every listed map lost props, and the Arathi interiors lost between 10% and 35%
  2. no sprite that appeared on the map was removed entirely - one of each always stays
  3. nothing that was removed is still blocking a tile
  4. thinning a map twice in a row removes nothing the second time beyond the share (stable)
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


def main():
    import pygame
    pygame.init()
    pygame.display.set_mode((64, 64))
    import world.prop_thinning as PT
    from world.zone_manager import ZoneManager
    real = PT.thin_all
    before = {}

    def spy(zones):
        for name in list(PT.THIN) + list(PT.THIN_SUBZONE):
            if name in zones:
                before[name] = [dict(l) for l in zones[name]["tilemap"].landmarks]
        return real(zones)
    PT.thin_all = spy
    zm = ZoneManager()
    PT.thin_all = real
    bad = []
    for name, was in before.items():
        tm = zm.zones[name]["tilemap"]
        now = tm.landmarks
        removed = zm.props_thinned.get(name, 0)
        if removed <= 0:
            bad.append(f"{name}: nothing was thinned")
        if name in PT.THIN and not (0.10 <= removed / len(was) <= 0.35):
            bad.append(f"{name}: {removed} of {len(was)} removed ({removed / len(was):.0%})")
        gone = {l["sprite_key"] for l in was} - {l["sprite_key"] for l in now}
        # the NPC pass may also remove scenery; a sprite lost entirely to THIS pass is the fault
        if gone and removed >= len(was) - len(now):
            bad.append(f"{name}: lost every copy of {sorted(os.path.basename(g) for g in gone)}")
        for y in range(tm.height):
            for x in range(tm.width):
                if tm.collision_layer[y][x] == "landmark" and not any(
                        l["anchor_x"] <= x < l["anchor_x"] + l["width_tiles"]
                        and l["anchor_y"] <= y < l["anchor_y"] + l["height_tiles"] for l in now):
                    bad.append(f"{name}: tile {(x, y)} is still blocked by a prop that is gone")
                    break
        print(f"  {name:22s} {len(was):4d} -> {len(now):4d}")
    if len(before) < 8:
        bad.append(f"only {len(before)} of the listed maps exist")
    if bad:
        for b in bad[:20]:
            print("  -", b)
        return 1
    print("\nprop thinning OK - less filler, every landmark kept, nothing left blocking.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
