"""
The shared floor machinery for the two dungeons in the Citadel of Ascent on the Ascendant Bastions: the Gravity
Foundry (tools/handbuilt_gravity_foundry.py, 56-58) and the Ascendant Spire (tools/handbuilt_ascendant_spire.py, 60).

Kyle, 21 Nov 2026: "For the Bastion, let's have a 'Hellfire Citadel' like style. We can have a lvl 56-58 and a lvl
60 dungeon. Both into one mega structure but different entrances. Each dungeon will have around 8-9 bosss over two
floors." So each dungeon is two floors of fortress interior: big built halls joined by wide ways, with loops, and a
fast exit at the end of the second floor.

A floor is a dict (each map module has a FLOOR of two):
    size        (W, H)
    start       where you arrive, two tiles in from the way you came
    rooms       name -> ("rect", x0, y0, x1, y1, chamfer) | ("lobes", [(cx, cy, rx, ry), ...])
    deep        shapes laid over the floor that you can't walk into: the pour, the pits, the open sky. They're lava
                tiles under the hood, so the bake paints them (molten crystal on the Foundry, the sky on the Spire)
    land        shapes laid back over the deep: catwalks, islands, bridges
    passages    [(points, width)], tools/dungeon_builder corridors (about 2w + 1 tiles across)
    cells       side rooms with a chest each, and cell_links into them
    pillars     [(x, y)] 2x2 columns, drawn with the floor's COLUMN art
    bosses      [(x, y, name)], final, and pack {boss: [(x, y, name)]} for a fight with two bosses in it
    doors       the tiles the portals sit on
    dressing    [(path, x, y, height, solid)]
"""
from collections import deque

from world.tilemap import Tilemap
from tools.dungeon_builder import Builder


def _shape(b, spec, base=None):
    if spec[0] == "rect":
        _k, x0, y0, x1, y1 = spec[:5]
        b.rect(x0, y0, x1, y1, chamfer=(spec[5] if len(spec) > 5 else 0), base=base)
    elif spec[0] == "lobes":
        b.lobes(spec[1], base=base)
    else:
        b.lobes([spec], base=base)


def reach(zone, start):
    seen, q = {start}, deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and 0 <= n[0] < zone.width and 0 <= n[1] < zone.height and zone.is_walkable(*n):
                seen.add(n)
                q.append(n)
    return seen


def _seal(zone, start, wall):
    seen = reach(zone, start)
    for y in range(zone.height):
        for x in range(zone.width):
            if (x, y) not in seen and zone.is_walkable(x, y):
                zone.collision_layer[y][x] = wall


def _dress(b, spec, keep):
    z = b.zone
    for (path, x, y, h, solid) in spec["dressing"]:
        spot = min(((dx * dx + dy * dy, x + dx, y + dy) for dy in range(-3, 4) for dx in range(-3, 4)
                    if z.is_walkable(x + dx, y + dy) and (x + dx, y + dy) not in keep), default=None)
        if spot is None:
            raise AssertionError((z.name, "prop with no floor within reach", path, x, y))
        b.prop(path, spot[1], spot[2], h, solid=solid, fraction=0.3)


def room_box(r):
    if r[0] == "rect":
        return r[1], r[2], r[3] - r[1] + 1, r[4] - r[2] + 1
    lb = r[1]
    x0 = min(cx - rx for (cx, cy, rx, ry) in lb)
    y0 = min(cy - ry for (cx, cy, rx, ry) in lb)
    x1 = max(cx + rx for (cx, cy, rx, ry) in lb)
    y1 = max(cy + ry for (cx, cy, rx, ry) in lb)
    return int(x0), int(y0), int(x1 - x0 + 1), int(y1 - y0 + 1)


def build_floor(name, spec, desc, region, column, wall="rock"):
    """-> (zone, builder), with every boss, chest and door checked reachable from the start."""
    W, H = spec["size"]
    zone = Tilemap(name, W, H, desc)
    zone.is_cave = True
    zone.region = region
    b = Builder(zone, wall_id=wall, floor_id="stone")
    for r in spec["rooms"].values():
        _shape(b, r)
    for (x0, y0, x1, y1) in spec["cells"]:
        b.rect(x0, y0, x1, y1, chamfer=1)
    for d in spec.get("deep", []):
        _shape(b, d, base="lava")
    for d in spec.get("land", []):
        _shape(b, d)
    # the ways go in last, so a way across the deep is a bridge
    for pts, wdt in spec["passages"] + spec["cell_links"]:
        b.corridor(pts, width=wdt)
    for (dx, dy) in spec["doors"]:
        for yy in (dy - 1, dy, dy + 1):
            if 0 <= yy < H:
                zone.collision_layer[yy][dx] = None
                if zone.base_layer[yy][dx] == "lava":
                    zone.base_layer[yy][dx] = "stone"
    _seal(zone, spec["start"], wall)
    keep = {spec["start"]} | {(x, y) for (x, y, _n) in spec["bosses"]} | set(spec["doors"])
    keep |= {(m[0], m[1]) for ms in spec.get("pack", {}).values() for m in ms}
    for (x, y) in spec.get("pillars", []):
        if any(zone.base_layer[yy][xx] == "lava" for yy in (y, y + 1) for xx in (x, x + 1)):
            raise AssertionError((name, "pillar in the deep", x, y))
        b.pillars([x], [y], size=2, sprite=column, height=5)
    _dress(b, spec, keep)
    _seal(zone, spec["start"], wall)

    fixed = []
    for (x, y, n) in spec["bosses"]:
        if not zone.is_walkable(x, y):
            raise AssertionError((name, "boss standing in rock or the deep", n, x, y))
        fixed.append((x, y, n))
    final = next(f for f in fixed if f[2] == spec["final"])
    zone.boss_position = final[:2]
    zone.boss_positions = list(fixed)
    zone.boss_pack = {k: list(v) for k, v in spec.get("pack", {}).items()}
    zone.chest_spots = [((x0 + x1) // 2, (y0 + y1) // 2) for (x0, y0, x1, y1) in spec["cells"]]
    seen = reach(zone, spec["start"])
    missing = [t for t in fixed + [(x, y, "chest") for (x, y) in zone.chest_spots]
               + [m for ms in spec.get("pack", {}).values() for m in ms]
               + [(d[0], d[1], "door") for d in spec["doors"]] if (t[0], t[1]) not in seen]
    if missing:
        raise AssertionError((name, "unreachable", missing))
    zone.add_subzone(name, 0, 0, W, H)
    for rname, r in spec["rooms"].items():
        zone.add_subzone(rname, *room_box(r))
    return zone, b


def snap(zone, spots, rad=8):
    out = []
    for (x, y, m, lvl) in spots:
        if zone.is_walkable(x, y):
            out.append((x, y, m, lvl))
            continue
        best = min(((dx * dx + dy * dy, x + dx, y + dy) for dy in range(-rad, rad + 1) for dx in range(-rad, rad + 1)
                    if 0 <= x + dx < zone.width and 0 <= y + dy < zone.height and zone.is_walkable(x + dx, y + dy)),
                   default=None)
        if best is None:
            raise AssertionError(("trash with no floor within reach", zone.name, m, x, y))
        out.append((best[1], best[2], m, lvl))
    return out


def generate(zone, spec, trash, baked):
    from world.dungeon_packs import attach_packs
    avoid = list(spec["doors"]) + [tuple(b[:2]) for b in zone.boss_positions]
    attach_packs(zone, [snap(zone, p) for p in trash], avoid=avoid)
    from tools.handbuilt_vot_caves import register_baked
    from world.chunk_paths import exists
    if exists(f"{baked}/ground_0_0.png"):
        register_baked(zone, baked)
    for (x, y) in zone.chest_spots:
        if zone.get_tile(x, y, "interaction") is None:
            zone.set_tile(x, y, "chest", "interaction")
    return zone


def pack_builder():
    T = []

    def pack(lvl, *spots):
        T.append([(x, y, m, lvl) for (x, y, m) in spots])
    return T, pack
