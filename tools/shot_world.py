#!/usr/bin/env python3
"""Screenshot the real overworld, anywhere, without launching the game.

    PYTHONPATH=. python3 tools/shot_world.py "Arathi Central" 120 110 out.png
    PYTHONPATH=. python3 tools/shot_world.py "Stromgarde Keep" --tour 6 --out-dir /tmp/strom

WHY. Kyle, 7 Nov: "we need to visually look at the Dungeons and caves in
arathi. Some of them look off. I suggest you look at some screenshots of the
walls, floor, and props."

There was no way to do that. tools/zone_dressed_preview.py only knows the
handbuilt modules listed in its ZONES dict and paints its own composite;
tools/dungeon_preview.py draws a schematic of three specific caves. Neither
shows Arathi, and neither shows what the PLAYER sees - they draw the whole map
from above at their own scale, which is the view that made Arathi's dungeons
measure fine and play wrong.

This drives the actual OverworldScreen: the real tilemap renderer, the real
camera, the real sprites, at the real viewport size. If it looks wrong here it
looks wrong in the game, because it is the same code path.

--tour N walks a grid of N viewpoints spread over the zone's walkable tiles
and shoots each one, which is how you review a dungeon you have never seen
without guessing coordinates.
"""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402


def _state(surface, char_class="Warrior", level=40):
    """A GameStateManager far enough along to render. Not a stub of the world -
    the real ZoneManager, so chunks, props and collision are the shipped ones."""
    from core.game_state import GameStateManager, GameState
    from entities.character import Character
    from entities.party import Party

    sm = GameStateManager(surface)
    sm.player = Character("Camera", char_class, level)
    sm.party = Party(sm.player)
    sm.current_state = GameState.OVERWORLD
    return sm


def _place(screen_obj, zone_name, x, y):
    zm = screen_obj.zone_manager
    zone = zm.get_zone_by_name(zone_name)
    if zone is None:
        names = sorted(zm.zones)
        raise SystemExit(f"no zone named {zone_name!r}.\n  known: " +
                         ", ".join(names[:40]) + (" ..." if len(names) > 40 else ""))
    zm.current_zone = zone
    zm.player_x, zm.player_y = int(x), int(y)
    # Chunk sprites are prewarmed on zone entry in the game; do the same here or
    # the first frame renders the ground as flat colour and the screenshot lies.
    try:
        from ui.tilemap_renderer import prewarm_chunk_sprites
        from world.tile_textures import TILE_SIZE
        prewarm_chunk_sprites(zone, TILE_SIZE)
    except Exception:
        pass
    try:
        zm.gathering_manager.populate(zone, zone.name)
    except Exception:
        pass
    return zone


def _walkable_tour(zone, count):
    """`count` viewpoints spread over the zone, each on a walkable tile.

    A plain grid would put half the shots inside rock. Each grid point walks
    outward to the nearest walkable tile instead, so a tour of a cave follows
    the cave rather than the bounding box.
    """
    import math
    cols = max(1, int(math.ceil(math.sqrt(count))))
    rows = max(1, int(math.ceil(count / cols)))
    picks = []
    for r in range(rows):
        for c in range(cols):
            if len(picks) >= count:
                break
            gx = int(zone.width * (c + 0.5) / cols)
            gy = int(zone.height * (r + 0.5) / rows)
            best = None
            for radius in range(0, max(zone.width, zone.height)):
                for dx in range(-radius, radius + 1):
                    for dy in (-radius, radius) if radius else (0,):
                        px, py = gx + dx, gy + dy
                        if 0 <= px < zone.width and 0 <= py < zone.height and zone.is_walkable(px, py):
                            best = (px, py)
                            break
                    if best:
                        break
                if best:
                    break
            picks.append(best or (gx, gy))
    return picks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("zone")
    ap.add_argument("x", nargs="?", type=int, default=None)
    ap.add_argument("y", nargs="?", type=int, default=None)
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--tour", type=int, default=0, help="shoot N spread viewpoints instead")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--class", dest="char_class", default="Warrior")
    ap.add_argument("--level", type=int, default=40)
    args = ap.parse_args()

    pygame.init()
    from config import SCREEN_WIDTH, SCREEN_HEIGHT
    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    from ui.screens.overworld_screen import OverworldScreen
    sm = _state(surface, args.char_class, args.level)
    screen_obj = OverworldScreen(sm)
    sm.zone_manager = screen_obj.zone_manager

    zone = _place(screen_obj, args.zone, args.x or 0, args.y or 0)

    if args.tour:
        out_dir = Path(args.out_dir or f"/tmp/{args.zone.lower().replace(' ', '_')}")
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"  {zone.name}  {zone.width}x{zone.height}"
              f"{'  (cave)' if getattr(zone, 'is_cave', False) else ''}")
        for i, (px, py) in enumerate(_walkable_tour(zone, args.tour), 1):
            screen_obj.zone_manager.player_x, screen_obj.zone_manager.player_y = px, py
            # update() BEFORE render(): the camera is centred in update(), and
            # without it every shot is the zone's top-left corner no matter
            # where the player stands - which looks exactly like an unlit,
            # untextured dungeon and nearly had me report one.
            screen_obj.update(0.016)
            surface.fill((0, 0, 0))
            screen_obj.render(surface)
            path = out_dir / f"{i:02d}_{px}_{py}.png"
            pygame.image.save(surface, str(path))
            sub = zone.get_subzone_at(px, py) if hasattr(zone, "get_subzone_at") else None
            label = (sub.get("name") if isinstance(sub, dict) else getattr(sub, "name", None)) or "-"
            print(f"   {path}   ({px},{py})  {label}")
        return 0

    if args.x is None or args.y is None:
        raise SystemExit("give x and y, or use --tour N")
    screen_obj.update(0.016)
    surface.fill((0, 0, 0))
    screen_obj.render(surface)
    out = args.out or f"/tmp/{args.zone.lower().replace(' ', '_')}_{args.x}_{args.y}.png"
    pygame.image.save(surface, out)
    print(f"  wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
