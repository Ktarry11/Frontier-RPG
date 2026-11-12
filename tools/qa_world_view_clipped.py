"""
The world is drawn inside its frame and nowhere else.

Seen 12 Nov in screenshots: an NPC standing on the health bar, a building running under the
Mount and Hearth buttons, figures in the black margin. Nothing clipped the world view, so
anything tall or near the edge of the view was painted across the interface.

In ten zones, standing at several spots (town centres included):
  1. the margin right of the view and above the side panel's blank area holds no world pixels
  2. the strip below the travel buttons holds none
  3. the view itself is still drawn (it is not blank)
The interface regions tested are ones the HUD leaves empty, so any colour there is spill.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)
    return ok


def main():
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    from core.game_state import GameStateManager, GameState
    from entities.character import Character
    from ui.screens.overworld_screen import OverworldScreen

    sm = GameStateManager(screen)
    sm.player = Character(name="Hero", char_class="Warrior", level=60)
    ow = sm.states.get(GameState.OVERWORLD) or OverworldScreen(sm)
    if hasattr(ow, "on_enter"):
        ow.on_enter()
    zm = sm._live_zone_manager()
    vp = ow.viewport_rect
    # Empty parts of the interface: between the view and the button column, below the bars;
    # and the strip under the travel buttons.
    empties = [pygame.Rect(vp.right + 6, 240, 1080 - vp.right - 12, vp.bottom - 250),
               pygame.Rect(20, 668, 1040, 46)]
    zones = [z for z in ("Razor Hill", "Orgrimmar", "Booty Bay", "Crossroads", "Brill", "Astranaar",
                         "Central Stranglethorn", "Undercity", "Durotar", "Grom'gol") if z in zm.zones]
    check(len(zones) >= 8, f"rig: only {len(zones)} of the test zones exist")
    shots = 0
    for zone in zones:
        t = zm.zones[zone]["tilemap"]
        npcs = [(x, y) for y in range(t.height) for x in range(t.width) if t.interaction_layer[y][x] == "npc"]
        spots = (npcs[:: max(1, len(npcs) // 5)][:5] or [(t.width // 2, t.height // 2)])
        for (x, y) in spots:
            if not zm.transition_to_zone(zone, x, y, via_portal=False):
                continue
            screen.fill((0, 0, 0))
            ow.render(screen)
            shots += 1
            for r in empties:
                sub = screen.subsurface(r)
                spill = 0
                for py in range(0, r.h, 3):
                    for px in range(0, r.w, 3):
                        c = sub.get_at((px, py))
                        if c[0] > 24 or c[1] > 24 or c[2] > 24:
                            spill += 1
                check(spill == 0, f"{zone} at ({x},{y}): {spill} world pixels drawn outside the view, in {tuple(r)}")
            inner = screen.subsurface(vp.inflate(-40, -40))
            lit = sum(1 for py in range(0, inner.get_height(), 20) for px in range(0, inner.get_width(), 20)
                      if sum(inner.get_at((px, py))[:3]) > 40)
            check(lit > 200, f"{zone} at ({x},{y}): the world view is blank")
    print(f"{shots} views rendered across {len(zones)} zones")
    if fails:
        print(f"FAIL {len(fails)}:")
        for f in fails[:15]:
            print("  ", f)
        return 1
    print("world view clipped OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
