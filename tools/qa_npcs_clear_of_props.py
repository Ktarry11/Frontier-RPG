#!/usr/bin/env python3
"""No NPC stands with scenery drawn over them.

    PYTHONPATH=. python3 tools/qa_npcs_clear_of_props.py

Kyle, 10 Nov 2026: "NPCs on props." 105 of 777 NPCs had a prop's solid pixels over their tile -
a guard in a tree's canopy, a vendor wearing a banner. world/npc_clearance.py now removes the
PROP, on every finished map.

THREE CLAIMS:

  1. NO NPC IS UNDER SCENERY. Trees, banners, crates, signposts: none covers more than half of
     any NPC's tile.
  2. NO NPC IS UNDER ENTRANCE ART THE FRAMING PASS PLACED. A gate dropped on a gate guard would
     be this pass undoing the other.
  3. THE BUILDINGS LIST ONLY SHRINKS. An NPC drawn on a roof is a mis-placed NPC, and moving
     one is a per-town job; there were 39 on 12 Nov. A new one is a failure, and when the
     number drops the ceiling below should drop with it.
"""
import contextlib
import io
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

#: NPCs still drawn on a building. Lower it as towns are fixed; never raise it.
ON_BUILDINGS_CEILING = 0


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        import pygame
        pygame.init()
        pygame.display.set_mode((64, 64))
        from world.zone_manager import ZoneManager
        from world import npc_clearance as NC
        from world.portal_art import is_entrance_art
        zm = ZoneManager()
    bad, on_buildings, npcs = [], [], 0
    # A HIDDEN SELLER (world/secrets.py) stands behind a building on purpose. Kyle, 14 Nov: "people
    # behind buildings and exploration is rewarded."
    hidden = {(v.zone, v.x, v.y) for v in zm.vendor_manager.vendors.values() if getattr(v, "hidden", False)}
    for name, entry in zm.zones.items():
        tm = entry["tilemap"]
        for y, row in enumerate(tm.interaction_layer):
            for x, kind in enumerate(row):
                if kind != "npc":
                    continue
                if any((z, x, y) in hidden for z in (name, name.lower().replace(" ", "_"))):
                    continue
                npcs += 1
                for lm in tm.landmarks:
                    if NC.covered(lm, x, y) <= NC.COVER:
                        continue
                    art = os.path.basename(lm["sprite_key"])[:-4]
                    if NC.is_building(lm):
                        on_buildings.append(f"{name} {(x, y)} on {art}")
                    elif lm.get("exit_frame"):
                        bad.append(f"{name}: the NPC at {(x, y)} is under {art}, which the "
                                   f"framing pass put there")
                    elif not is_entrance_art(lm["sprite_key"]):
                        bad.append(f"{name}: the NPC at {(x, y)} is under {art}")
                    break
    if len(on_buildings) > ON_BUILDINGS_CEILING:
        bad.append(f"{len(on_buildings)} NPCs are drawn on a building, over the ceiling of "
                   f"{ON_BUILDINGS_CEILING}: {on_buildings[:6]}")
    # the check must be able to fail: a tile in the middle of a solid prop reads as covered
    solid = next((lm for e in zm.zones.values() for lm in e["tilemap"].landmarks
                  if NC.is_building(lm) and lm["width_tiles"] >= 3 and lm["height_tiles"] >= 3
                  and not lm.get("rotation")), None)
    if solid is None or NC.covered(solid, solid["anchor_x"] + solid["width_tiles"] // 2,
                                   solid["anchor_y"] + solid["height_tiles"] // 2) <= NC.COVER:
        bad.append("negative control: the middle of a building does not read as covered, so "
                   "this check cannot see anything")

    print(f"{npcs} NPCs; {zm.props_cleared_off_npcs} props moved out from over them; "
          f"{len(on_buildings)} still drawn on a building (ceiling {ON_BUILDINGS_CEILING})")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for line in bad[:20]:
            print("  -", line)
        return 1
    print("\nNPCs OK - nobody stands under scenery or under a gate the framing pass placed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
