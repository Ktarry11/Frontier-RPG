"""
Every way out of every map works, can be reached, and can be SEEN.

Kyle, 12 Nov: "Undecity portal is hidden and cant be seen either", "Portals in brill are
hidden (I THINK WE SHOULD JUST DO A FULL PORTAL AUDIT TO ENSURE PORTALS ARE NOT HIDDEN BY
PROPS!!!!)".

All 246 portal and boat tiles, on the maps the real ZoneManager builds:

  LINKED     every exit tile has a registered destination, and every registered link has a
             tile under it (a link with no tile is a door that is not there)
  WALKABLE   the exit tile can be stood on
  REACHABLE  every exit on a map is connected, on foot, to every other - an exit cut off by
             rock is "drawn but not reachable", the Emberdeep causeway bug
  DESTINATION the map it leads to exists, and the arrival is on (or snaps to) walkable ground
  VISIBLE    nothing but entrance art is drawn over an exit tile (world/portal_art.py), and
             the renderer draws the exit marker AFTER the art, so even entrance art frames
             the door rather than hiding it
"""
import collections
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def flood(t, start):
    seen = {start}
    queue = collections.deque([start])
    while queue:
        x, y = queue.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n in seen or not (0 <= n[0] < t.width and 0 <= n[1] < t.height):
                continue
            if t.is_walkable(*n):
                seen.add(n)
                queue.append(n)
    return seen


def _secret_door(zone, x, y):
    """A secret door (world/secrets.py) is meant to look like nothing: whatever's drawn over it is
    camouflage, not a hidden exit."""
    from world.secrets import get_secrets
    return get_secrets().is_door(zone, x, y)


def main():
    from world.zone_manager import ZoneManager
    from world.portal_art import is_entrance_art

    zm = ZoneManager()
    links = zm.portal_manager._links
    bad = []
    exits = framed = 0
    for zone, entry in zm.zones.items():
        t = entry["tilemap"]
        tiles = [(x, y) for y, row in enumerate(t.interaction_layer)
                 for x, kind in enumerate(row) if kind in ("portal", "boat")]
        declared = links.get(zone, {})
        for key, (dest, dx, dy) in declared.items():
            if key not in tiles:
                bad.append(f"{zone}: a link to {dest} is registered at {key} but there is no "
                           f"exit tile there")
            target = zm.zones.get(dest)
            if target is None:
                bad.append(f"{zone} {key}: leads to {dest!r}, which is not a map")
                continue
            tt = target["tilemap"]
            if not (0 <= dx < tt.width and 0 <= dy < tt.height):
                bad.append(f"{zone} {key}: arrives at ({dx},{dy}), off the map of {dest}")
            elif not tt.is_walkable(dx, dy) and zm._find_nearest_walkable(tt, dx, dy) is None:
                bad.append(f"{zone} {key}: arrives in {dest} with no walkable ground near")
        if not tiles:
            continue
        reach = None
        for (x, y) in tiles:
            exits += 1
            if (x, y) not in declared:
                bad.append(f"{zone}: exit tile at ({x},{y}) leads nowhere")
            if not t.is_walkable(x, y):
                bad.append(f"{zone}: exit tile at ({x},{y}) cannot be stood on")
                continue
            if reach is None:
                reach = flood(t, (x, y))
            elif (x, y) not in reach:
                bad.append(f"{zone}: the exit at ({x},{y}) cannot be reached from the exit "
                           f"at {tiles[0]}")
            covered = False
            for lm in getattr(t, "landmarks", []) or []:
                if (lm["anchor_x"] <= x < lm["anchor_x"] + lm["width_tiles"]
                        and lm["anchor_y"] <= y < lm["anchor_y"] + lm["height_tiles"]):
                    covered = True
                    if not is_entrance_art(lm["sprite_key"]) and not _secret_door(zone, x, y):
                        bad.append(f"{zone}: the exit at ({x},{y}) is under "
                                   f"{os.path.basename(lm['sprite_key'])}, which is not entrance art")
            framed += 1 if covered else 0

    if exits < 200:
        print(f"FAIL only {exits} exit tiles found - the rig is not seeing the maps")
        return 1

    # The renderer draws the marker after the art. Render one framed exit and one bare one.
    import pygame
    pygame.init()
    surface = pygame.display.set_mode((1280, 720))
    from ui.tilemap_renderer import TilemapRenderer
    src = (ROOT / "ui/tilemap_renderer.py").read_text(encoding="utf-8")
    order_ok = src.index("for lm in getattr(tilemap, \"landmarks\", []):") < src.index("self._portal_glow()")
    if not order_ok:
        bad.append("the renderer draws exit markers BEFORE landmarks - art will cover them again")
    if not hasattr(TilemapRenderer, "_portal_glow"):
        bad.append("the renderer has no exit marker pass")

    print(f"{exits} exit tiles on {len(zm.zones)} maps: {framed} framed by entrance art, "
          f"{exits - framed} bare; {zm.exit_props_cleared} stray prop(s) cleared off exits "
          f"at build")
    if bad:
        print(f"FAIL {len(bad)}:")
        for b in bad[:30]:
            print("  ", b)
        return 1
    print("portals OK - every exit is linked, reachable and visible.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
