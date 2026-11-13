#!/usr/bin/env python3
"""No two props stand on the same ground in the game the player sees.

    PYTHONPATH=. python3 tools/qa_prop_overlap.py

Kyle, 10 Nov 2026 ([83]): "Randomly dropped overlapping props. [...] Add a check that fails the
build when two props' footprints overlap, and fix every hit."

world/prop_clearance.py is the fix - one pass over each finished map that removes the lesser prop
of any pair sharing a footprint. This is the check.

FOUR CLAIMS:
  1. THE LIVE MAPS HAVE NO SUCH PAIR - read from the zone manager, after every clearance pass.
  2. THE PASS NEVER REMOVES A BUILDING.
  3. IT LEAVES THE THINGS IT IS MEANT TO LEAVE: a crate in FRONT of a tent (drawn over it, standing
     on different ground) stays, and so does rock against rock.
  4. IT IS DOING REAL WORK, and not much of it: between 1 and 120 props removed across the world.
     Zero would mean it has stopped running; hundreds would mean it has started eating scenery.
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
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


class _Map:
    """Just enough of a tilemap for the pass to work on."""
    def __init__(self, landmarks, w=40, h=40):
        self.landmarks = landmarks
        self.width, self.height = w, h
        self.collision_layer = [[None] * w for _ in range(h)]
        self.interaction_layer = [[None] * w for _ in range(h)]


def _lm(sprite, x, y, w, h):
    return {"sprite_key": sprite, "anchor_x": x, "anchor_y": y, "width_tiles": w, "height_tiles": h}


def main():
    bad = []
    with contextlib.redirect_stdout(io.StringIO()):
        import pygame
        pygame.init()
        screen = pygame.display.set_mode((64, 64))
        from core.game_state import GameStateManager
        from entities.character import Character
        from world import prop_clearance as PC
        from world.npc_clearance import is_building
        sm = GameStateManager(screen)
        sm.player = Character(name="Audit", char_class="Warrior", level=60)
        zm = sm._live_zone_manager()

    # 1
    left = 0
    for name, entry in zm.zones.items():
        for (f, a, b) in PC.shared_ground(entry["tilemap"]):
            left += 1
            if left <= 8:
                bad.append(f"{name}: {PC._name(a)} and {PC._name(b)} share ground ({f:.0%})")
    removed = getattr(zm, "props_cleared_off_props", None)

    # 4
    if removed is None or not 1 <= removed <= 120:
        bad.append(f"the pass removed {removed} props across the world")

    # 2, 3 - on a made-up map
    TENT = "assets/tiles/underdark/props/ud_codex_tent.png"
    CRATE = "assets/tiles/shimmering_flats/props/sf_crate_stack.png"
    INN = "assets/buildings/bb_harbour_inn.png"
    ROCK = "assets/tiles/southern_needles/props/sn_boulder_red.png"
    same = _Map([_lm(TENT, 10, 10, 5, 5), _lm(CRATE, 11, 12, 3, 3)])          # crate inside the tent
    if PC.clear_props_through_props(same) != 1 or PC._name(same.landmarks[0]) != "ud_codex_tent.png":
        bad.append("a crate standing inside a tent was not the one removed")
    front = _Map([_lm(TENT, 10, 10, 5, 5), _lm(CRATE, 11, 14, 3, 3)])         # crate in front of it
    if PC.clear_props_through_props(front) != 0:
        bad.append("a crate standing in front of a tent was removed")
    with_inn = _Map([_lm(INN, 10, 10, 9, 9), _lm(CRATE, 13, 16, 3, 3)])
    PC.clear_props_through_props(with_inn)
    if not any(is_building(lm) for lm in with_inn.landmarks):
        bad.append("the pass removed a building")
    rocks = _Map([_lm(ROCK, 10, 10, 3, 3), _lm(ROCK, 11, 10, 3, 3)])
    if PC.clear_props_through_props(rocks) != 0:
        bad.append("two boulders together were treated as a fault")

    print(f"{len(zm.zones)} live maps, {left} pairs sharing ground, {removed} props removed by the pass")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for line in bad:
            print("  -", line)
        return 1
    print("\nprops OK - nothing stands on the same ground as something else.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
