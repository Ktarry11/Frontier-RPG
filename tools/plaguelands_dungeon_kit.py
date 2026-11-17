"""
The floor builder the Plaguelands' city dungeons share (Stratholme's two halves and Hearthglen; Scholomance keeps its
own in tools/handbuilt_scholomance.py, which this one grew out of).

A floor is a dict (see tools/handbuilt_stratholme.py for three of them):

    size      (W, H)
    desc      the map's one-line description
    rooms     {name: ("rect", x0, y0, x1, y1, chamfer) | ("lobes", [(cx, cy, rx, ry), ...])}; each is a subzone
    links     [(points, width)]: streets, passages, stairs (dungeon_builder.Builder.corridor; width 2 cuts about
              five tiles across, 4 about nine)
    solids    [(x0, y0, x1, y1)]: put back as wall after carving: a fountain, a monument, a house in a square
    pillars   [(x, y)]: 2x2 columns
    doors     {"in"|"up"|"down"|"exit": (x, y)}. Every door but "exit" is somewhere a player ARRIVES, and the game
              puts an arriving player two tiles north of the door (world/portal_manager._offset_spawn), so those
              two tiles have to be floor. "exit" is the one-way fast exit past the last boss (Kyle: every
              multi-layer dungeon gets one, and it's ONE WAY): nobody arrives on it.
    bosses    [(x, y, name)]; `final` names the floor's last boss; `pack` {boss: [(x, y, name)]} for a shared fight
    chests    [(x, y)]
    trash     [[(x, y, name, level), ...], ...]: each list is one pack's seed, padded to four or five when the
              floor is wired (world/dungeon_packs.attach_packs)

build_floor() carves it, checks every door, boss, chest and trash seed can be walked to from the way in, and raises
if not. preview() draws it.
"""
from world.tilemap import Tilemap
from tools.dungeon_builder import Builder


def _box(r):
    if r[0] == "rect":
        _k, x0, y0, x1, y1, _c = r
        return x0, y0, x1 - x0 + 1, y1 - y0 + 1
    xs = [cx - rx for (cx, _cy, rx, _ry) in r[1]] + [cx + rx for (cx, _cy, rx, _ry) in r[1]]
    ys = [cy - ry for (_cx, cy, _rx, ry) in r[1]] + [cy + ry for (_cx, cy, _rx, ry) in r[1]]
    return min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1


def snap(zone, x, y, rad=6):
    if zone.is_walkable(x, y):
        return x, y
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < zone.width and 0 <= ny < zone.height and zone.is_walkable(nx, ny):
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, nx, ny)
    if best is None:
        raise AssertionError((zone.name, "nothing walkable near", x, y))
    return best[1], best[2]


COLUMN = "assets/tiles/scarlet_monastery/props/sm_stone_column.png"
PROPS = "assets/tiles/plaguelands/dungeon_props/"


def auto_dress(zone, b, spec, avoid, seed):
    """Kyle's dungeon prop sheet (sheet 8), set into each room by `spec["decor"]` = {room: [(stem, height, kind,
    count)]}. kind "wall" stands against the room's north wall with a solid base (shelves, organs, cages); "floor"
    is walk-through clutter (rubble, a cart, a brazier); "free" is a solid piece in the open (a fountain, a table).
    Nothing goes within three tiles of a door, a boss, a chest or a pack, and pieces keep four tiles apart, so the
    rooms read furnished without a prop ever standing in the way. Deterministic (seeded by the floor's name)."""
    import random
    rnd = random.Random(seed)
    placed = []

    def clear(x, y, r=3):
        return all(abs(x - ax) > r or abs(y - ay) > r for (ax, ay) in avoid + placed)
    for room, items in (spec.get("decor") or {}).items():
        r = spec["rooms"][room]
        x0, y0, w, h = _box(r)
        tiles = [(x, y) for y in range(y0, y0 + h) for x in range(x0, x0 + w)
                 if 0 < x < zone.width - 1 and 0 < y < zone.height - 1 and zone.is_walkable(x, y)
                 and zone.interaction_layer[y][x] is None]
        rnd.shuffle(tiles)
        for (stem, hgt, kind, count) in items:
            path = PROPS + stem + ".png"
            from tools.dungeon_builder import _aspect
            wt = max(1, round(hgt * _aspect(path)))
            n = 0
            for (x, y) in tiles:
                if n >= count:
                    break
                if not clear(x, y, 4 if kind != "floor" else 3):
                    continue
                span = range(x - wt // 2, x - wt // 2 + wt)
                if kind == "wall":
                    # against the north wall: the row above is rock, the row below is open floor
                    if zone.is_walkable(x, y - 1) or not zone.is_walkable(x, y + 1):
                        continue
                    if not all(zone.is_walkable(xx, y) and zone.interaction_layer[y][xx] is None for xx in span):
                        continue
                    b.prop(path, x, y, hgt, solid="core", fraction=0.35)
                elif kind == "free":
                    if not all(zone.is_walkable(xx, yy) for xx in range(x - wt // 2 - 1, x + wt // 2 + 2)
                               for yy in (y - 1, y, y + 1)):
                        continue
                    b.prop(path, x, y, hgt, solid="core", fraction=0.35)
                else:
                    b.prop(path, x, y, hgt, solid=False)
                placed.append((x, y))
                n += 1
    return len(placed)


def build_floor(name, spec, region, pillar_sprite=COLUMN):
    W, H = spec["size"]
    zone = Tilemap(name, W, H, spec["desc"])
    zone.is_cave = True
    zone.region = region
    b = Builder(zone, wall_id="wall", floor_id="stone")
    for r in spec["rooms"].values():
        if r[0] == "rect":
            b.rect(r[1], r[2], r[3], r[4], chamfer=r[5])
        else:
            b.lobes(r[1])
    for pts, wdt in spec.get("links", []):
        b.corridor(pts, width=wdt)
    for (x0, y0, x1, y1) in spec.get("solids", []):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                zone.set_tile(x, y, "wall", "collision")
    for (x, y) in spec.get("pillars", []):
        b.pillars([x], [y], size=2, sprite=pillar_sprite, height=4)

    doors = spec["doors"]
    for kind, (dx, dy) in doors.items():
        zone.collision_layer[dy][dx] = None
        if kind != "exit":
            for yy in (dy - 1, dy - 2):
                if not zone.is_walkable(dx, yy):
                    raise AssertionError((name, f"the {kind} door at {(dx, dy)} has rock where you arrive", dx, yy))
    fixed = []
    for (x, y, n) in spec["bosses"]:
        if not zone.is_walkable(x, y):
            raise AssertionError((name, "boss standing in rock", n, x, y))
        fixed.append((x, y, n))
    for mates in spec.get("pack", {}).values():
        for (x, y, n) in mates:
            if not zone.is_walkable(x, y):
                raise AssertionError((name, "boss standing in rock", n, x, y))
    final = next(f for f in fixed if f[2] == spec["final"])
    zone.boss_position = final[:2]
    zone.boss_positions = list(fixed)
    zone.boss_pack = dict(spec.get("pack", {}))
    zone.chest_spots = [snap(zone, x, y) for (x, y) in spec.get("chests", [])]
    zone.door_tiles = dict(doors)
    way_in = doors.get("in") or doors.get("up")
    start = (way_in[0], way_in[1] - 2)
    targets = [f for f in fixed] + [(x, y, "chest") for (x, y) in zone.chest_spots]
    targets += [(x, y, kind) for kind, (x, y) in doors.items()]
    for pack in spec.get("trash", []):
        for (x, y, n, _l) in pack:
            sx, sy = snap(zone, x, y)
            targets.append((sx, sy, n))
    avoid = [(t[0], t[1]) for t in targets] + [start]
    zone.dressed = auto_dress(zone, b, spec, avoid, sum(map(ord, name)))
    b.verify(start, targets)
    zone.add_subzone(name, 0, 0, W, H)
    for rname, r in spec["rooms"].items():
        zone.add_subzone(rname, *_box(r))
    return zone, b


def generate_floor(name, spec, region, baked, pillar_sprite=COLUMN):
    """The floor as the game uses it: carved, its trash seeds filled to packs of four or five
    (world/dungeon_packs.attach_packs, Kyle: "in dungeons enemies are in packs of 4 to 5"), its painting registered
    and its chests set down."""
    zone, _b = build_floor(name, spec, region, pillar_sprite)
    from world.dungeon_packs import attach_packs
    avoid = list(spec["doors"].values()) + [tuple(b[:2]) for b in zone.boss_positions]
    seeds = [[(*snap(zone, x, y), n, lvl) for (x, y, n, lvl) in pack] for pack in spec.get("trash", [])]
    attach_packs(zone, seeds, avoid=avoid)
    from tools.handbuilt_vot_caves import register_baked
    register_baked(zone, baked)
    for (x, y) in zone.chest_spots:
        if zone.get_tile(x, y, "interaction") is None:
            zone.set_tile(x, y, "chest", "interaction")
    return zone


def preview(zone, spec, path, scale=6):
    """A plain picture of the floor: rock, floor, rooms named, doors, bosses (red), chests (gold), trash (grey)."""
    from PIL import Image, ImageDraw
    W, H = zone.width, zone.height
    im = Image.new("RGB", (W * scale, H * scale), (18, 16, 20))
    d = ImageDraw.Draw(im)
    for y in range(H):
        for x in range(W):
            if zone.is_walkable(x, y):
                d.rectangle([x * scale, y * scale, x * scale + scale - 1, y * scale + scale - 1], fill=(120, 116, 108))

    def dot(x, y, col, r=1.6):
        cx, cy = x * scale + scale / 2, y * scale + scale / 2
        d.ellipse([cx - r * scale, cy - r * scale, cx + r * scale, cy + r * scale], fill=col)
    for pack in spec.get("trash", []):
        for (x, y, _n, _l) in pack:
            dot(*snap(zone, x, y), (70, 70, 80), 0.8)
    for (x, y) in zone.chest_spots:
        dot(x, y, (220, 180, 60), 0.9)
    for kind, (x, y) in spec["doors"].items():
        dot(x, y, (80, 160, 230) if kind != "exit" else (150, 90, 230), 1.4)
        d.text((x * scale + 8, y * scale - 6), kind, fill=(170, 210, 255))
    for (x, y, n) in spec["bosses"]:
        dot(x, y, (210, 50, 50), 1.5)
        d.text((x * scale + 10, y * scale + 4), n, fill=(255, 200, 200))
    for rname, r in spec["rooms"].items():
        x, y, _w, _h = _box(r)
        d.text((x * scale + 3, y * scale + 2), rname, fill=(235, 235, 210))
    im.save(path)
    return path
