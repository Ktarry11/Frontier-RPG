"""Small helper for HAND-PLACED dungeon layouts.

Every dungeon rebuilt with this is drawn room by room at explicit
coordinates (no random scatter deciding the shape): rooms are unions of
ellipse lobes or chamfered rectangles, corridors are polylines, and props
are placed with a bottom-center anchor and an aspect-correct footprint.

WHY this exists: the generic generate_cave()/carve() layouts produced
identical circular blobs joined by straight tubes, and two of the Silverpine
dungeons (Widow's Lair, Shadowfang Keep) used "stone" as their wall tile.
"stone" is a walkable FLOOR tile_id, so placing it on the collision layer is
a no-op - those two dungeons had no walls at all. Builder.wall_id defaults
to a real blocker ("wall"/"rock") and verify() fails loudly if a boss,
portal or chest can't be reached.
"""
import os
from collections import deque

from PIL import Image

from world.zone_generator import ZoneGenerator

_ASPECT_CACHE = {}


def _aspect(path):
    if path not in _ASPECT_CACHE:
        with Image.open(path) as im:
            _ASPECT_CACHE[path] = im.size[0] / im.size[1]
    return _ASPECT_CACHE[path]


class Builder:
    def __init__(self, zone, wall_id="wall", floor_id="dirt"):
        self.zone = zone
        self.wall_id = wall_id
        self.floor_id = floor_id
        self.w, self.h = zone.width, zone.height
        zone.fill(floor_id, "base")
        for y in range(self.h):
            for x in range(self.w):
                zone.set_tile(x, y, wall_id, "collision")

    # ------------------------------------------------------------------
    # carving
    # ------------------------------------------------------------------
    def _open(self, x, y, base=None):
        if 1 <= x < self.w - 1 and 1 <= y < self.h - 1:
            self.zone.collision_layer[y][x] = None
            self.zone.set_tile(x, y, base or self.floor_id, "base")

    def lobes(self, ellipses, base=None):
        """Union of (cx, cy, rx, ry) ellipses - an organic cave room."""
        for (cx, cy, rx, ry) in ellipses:
            for dy in range(-ry, ry + 1):
                for dx in range(-rx, rx + 1):
                    if (dx / max(rx, 1)) ** 2 + (dy / max(ry, 1)) ** 2 <= 1.0:
                        self._open(cx + dx, cy + dy, base)

    def rect(self, x0, y0, x1, y1, chamfer=0, base=None):
        """Inclusive rectangle, optionally with chamfered (45-degree) corners."""
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                ix = min(x - x0, x1 - x)
                iy = min(y - y0, y1 - y)
                if ix + iy < chamfer:
                    continue
                self._open(x, y, base)

    def corridor(self, points, width=3, base=None):
        """Polyline corridor through (x, y) waypoints."""
        for (a, b) in zip(points, points[1:]):
            ZoneGenerator._carve_path(self.zone, a[0], a[1], b[0], b[1],
                                      width=width, base=base or self.floor_id)

    def restyle(self, x0, y0, x1, y1, floor=None, wall=None):
        """Re-tag tiles inside an inclusive rect so a themed wing gets its
        own texture: open floor -> `floor` base tile_id, blocking wall ->
        `wall` collision tile_id. Water and props are left alone."""
        for y in range(max(0, y0), min(self.h, y1 + 1)):
            for x in range(max(0, x0), min(self.w, x1 + 1)):
                if self.zone.collision_layer[y][x] == self.wall_id:
                    if wall:
                        self.zone.collision_layer[y][x] = wall
                elif self.zone.collision_layer[y][x] is None and floor:
                    if self.zone.base_layer[y][x] == self.floor_id:
                        self.zone.set_tile(x, y, floor, "base")

    def pillar(self, x, y, size=2):
        """size x size block of wall (a lone 32px wall tile is nearly
        invisible against flagstone; 2x2 reads as a real column base)."""
        for dy in range(size):
            for dx in range(size):
                self.zone.set_tile(x + dx, y + dy, self.wall_id, "collision")

    def pillars(self, xs, ys, size=2):
        for y in ys:
            for x in xs:
                self.pillar(x, y, size)

    def water(self, ellipses, island=None):
        """Shallow (walkable) water lobes; `island` ellipses stay dry."""
        self.lobes(ellipses, base="shallow_water")
        if island:
            self.lobes(island, base=self.floor_id)

    # ------------------------------------------------------------------
    # props
    # ------------------------------------------------------------------
    def prop(self, path, cx, base_y, height, solid=False, fraction=0.5, rotation=0):
        """Place a sprite with its bottom-center on tile (cx, base_y).

        height: footprint height in tiles; width follows the sprite's real
        aspect so nothing is squashed. solid: False = decorative only;
        True = whole footprint blocks; "core" = only the bottom `fraction`
        of rows and the central 60% of columns block (a tree/statue base,
        not its canopy). Tiles holding a portal/boss/chest are never made
        solid.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        wt = max(1, round(height * _aspect(path)))
        ax = cx - wt // 2
        ay = base_y - height + 1
        self.zone.add_landmark(path, ax, ay, wt, height, solid=(solid is True))
        if solid == "core":
            rows = max(1, round(height * fraction))
            c0 = ax + int(wt * 0.2)
            c1 = ax + max(int(wt * 0.8), int(wt * 0.2) + 1)
            for y in range(ay + height - rows, ay + height):
                for x in range(c0, c1):
                    if (0 <= x < self.w and 0 <= y < self.h
                            and self.zone.interaction_layer[y][x] is None):
                        self.zone.collision_layer[y][x] = "landmark"
        if solid is True:
            # Re-open any interaction tile swallowed by a full-footprint prop.
            for y in range(ay, ay + height):
                for x in range(ax, ax + wt):
                    if (0 <= x < self.w and 0 <= y < self.h
                            and self.zone.interaction_layer[y][x] is not None):
                        self.zone.collision_layer[y][x] = None
        return ax, ay, wt, height

    # ------------------------------------------------------------------
    # verification
    # ------------------------------------------------------------------
    def reachable(self, start):
        seen = {start}
        q = deque([start])
        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if (0 <= n[0] < self.w and 0 <= n[1] < self.h and n not in seen
                        and self.zone.is_walkable(*n)):
                    seen.add(n)
                    q.append(n)
        return seen

    def verify(self, start, targets):
        """Raise if `start` isn't walkable or any (x, y, label) target is
        unreachable from it by 4-way flood fill."""
        if not self.zone.is_walkable(*start):
            raise AssertionError(f"{self.zone.name}: start {start} not walkable")
        seen = self.reachable(start)
        missing = [(t[0], t[1], t[2] if len(t) > 2 else "") for t in targets
                   if (t[0], t[1]) not in seen]
        if missing:
            raise AssertionError(f"{self.zone.name}: unreachable from {start}: {missing}")
        return len(seen)
