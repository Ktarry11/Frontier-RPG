"""
The sea round the ships is water, not a grid of flat teal squares.

Kyle, 10 Nov: "the crossing (and all the boat dungeons (blood sail raider AND anchorage) has
a water glitch."

Those zones use "tropical_water" as their WALL, stamped on the collision layer so nobody walks
off the deck. It has no sprite, so the renderer's fallback painted every sea tile as a flat
(18,118,134) square with a grey outline, over the baked water underneath.

For every map that puts a water id on its collision layer, render the real overworld screen
centred on such a tile and count pixels that are exactly the tile's flat fallback colour. A
painted sea has essentially none; the bug filled most of the view with them.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

WATER_IDS = ("water", "tropical_water", "tropical_shallow", "deep_water", "shallow_water")


def main():
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    from core.game_state import GameStateManager, GameState
    from entities.character import Character
    from ui.screens.overworld_screen import OverworldScreen
    from world.tiles import get_tile_color

    sm = GameStateManager(screen)
    sm.player = Character(name="Hero", char_class="Warrior", level=60)
    ow = sm.states.get(GameState.OVERWORLD) or OverworldScreen(sm)
    if hasattr(ow, "on_enter"):
        ow.on_enter()
    zm = sm._live_zone_manager()

    targets = []
    for zone, entry in zm.zones.items():
        t = entry["tilemap"]
        ids = {c for row in t.collision_layer for c in row if c in WATER_IDS}
        if not ids:
            continue
        # A walkable tile with the most wall-water round it: a view of open sea.
        best = None
        for y in range(4, t.height - 4, 3):
            for x in range(4, t.width - 4, 3):
                if not t.is_walkable(x, y):
                    continue
                wet = sum(1 for dy in range(-4, 5) for dx in range(-4, 5)
                          if t.collision_layer[y + dy][x + dx] in WATER_IDS)
                if best is None or wet > best[0]:
                    best = (wet, x, y)
        if best and best[0] >= 10:
            targets.append((zone, best[1], best[2], sorted(ids)))
    if not targets:
        print("FAIL no map uses a water id as a wall - the rig is not seeing the ship zones")
        return 1

    bad = []
    for zone, x, y, ids in targets:
        zm.transition_to_zone(zone, x, y, via_portal=False)
        zm.player_x, zm.player_y = x, y
        ow.update(0.016)
        ow.render(screen)
        view = pygame.surfarray.array3d(screen)[20:820, 20:620]
        total = view.shape[0] * view.shape[1]
        worst = 0.0
        for tid in ids:
            r, g, b = get_tile_color(tid)[:3]
            flat = ((view[:, :, 0] == r) & (view[:, :, 1] == g) & (view[:, :, 2] == b)).sum()
            worst = max(worst, flat / total)
        if worst > 0.03:
            bad.append(f"{zone} at ({x},{y}): {worst:.0%} of the view is the flat fallback "
                       f"colour of {ids}")
        else:
            print(f"  ok   {zone}: {worst:.1%} flat-colour pixels")
    if bad:
        print(f"FAIL {len(bad)}:")
        for b in bad:
            print("  ", b)
        return 1
    print(f"water OK on {len(targets)} map(s) that use the sea as a wall.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
