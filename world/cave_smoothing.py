"""Cave floors without snags (backlog O [86]).

Kyle, on the Drowned Barrow: "a jagged, blocky floor full of single-tile notches and pillars-of-wall,
so movement snags constantly... Apply the same smoothing check to every dungeon/cave: no 1-tile
jags on walkable edges, minimum corridor width."

ONE RULE, TWO PLACES. A cave's look is a baked painting made from its floor plan, and the game walks
the floor plan. If only the game smoothed, the player would walk through painted rock; if only the
baker did, the painting would show floor the player can't stand on. So the same function runs in
both: tools/bake_durotar_caves.bake_spec smooths a cave before painting it and records EXACTLY
which tiles it opened in data/world/smoothed_caves.json, and world/zone_generator.create_all_zones
opens those same tiles and no others. The game never re-derives them, so it cannot drift from the
painting; a cave painted by some other baker is not on the list and is never changed.

OPENING ONLY. A pass never turns floor into rock, so every NPC, chest, spawn, pack and quest spot
that stood on floor still does. Each pass:
  - a passage one tile wide (rock both sides) is opened to two, toward the side with more floor;
  - a rock tile with floor on three or four sides (a notch, a pillar stub) becomes floor.
Only plain rock ("rock", "wall") is ever opened. Water, cliffs, props and the map's border are left
alone, and so is everything within two tiles of a secret (data/world/secrets.json): a hidden way in
has to keep looking like the solid rock around it.
"""
import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
LIST_PATH = _ROOT / "data" / "world" / "smoothed_caves.json"
SECRETS_PATH = _ROOT / "data" / "world" / "secrets.json"
WALL_IDS = ("rock", "wall")
MARGIN = 2


def secret_guard(zone_name):
    """Tiles of every secret in this map, two tiles out."""
    try:
        doc = json.loads(SECRETS_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    core = set()
    for s in doc.get("secrets") or []:
        if s.get("zone") != zone_name:
            continue
        core |= {tuple(t) for t in (s.get("passage") or []) + (s.get("area") or [])}
        for k in ("cache", "door"):
            if s.get(k):
                core.add((s[k]["x"], s[k]["y"]))
    return {(x + dx, y + dy) for (x, y) in core
            for dx in range(-MARGIN, MARGIN + 1) for dy in range(-MARGIN, MARGIN + 1)}


def smooth(zone, guard=frozenset(), passes=4):
    """Open the snags in place. Returns the tiles opened, in order."""
    W, H = zone.width, zone.height
    col = zone.collision_layer
    opened = []

    def floor(x, y):
        return 0 <= x < W and 0 <= y < H and col[y][x] is None

    def openable(x, y):
        return 1 <= x < W - 1 and 1 <= y < H - 1 and col[y][x] in WALL_IDS and (x, y) not in guard

    def base_from_neighbour(x, y):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if floor(x + dx, y + dy):
                return zone.base_layer[y + dy][x + dx]
        return zone.base_layer[y][x]

    def open_(x, y):
        zone.base_layer[y][x] = base_from_neighbour(x, y)
        col[y][x] = None

    def room(x, y):
        return sum(floor(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1))

    for _ in range(passes):
        todo = set()
        for y in range(1, H - 1):
            for x in range(1, W - 1):
                if col[y][x] is None:
                    for a, b in (((x - 1, y), (x + 1, y)), ((x, y - 1), (x, y + 1))):
                        if not floor(*a) and not floor(*b):
                            cands = [t for t in (a, b) if openable(*t)]
                            if cands:
                                todo.add(max(cands, key=lambda t: room(*t)))
                elif openable(x, y):
                    if sum(floor(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) >= 3:
                        todo.add((x, y))
        if not todo:
            break
        for t in sorted(todo):
            open_(*t)
        opened += sorted(todo)
    return opened


def listed():
    """{cave name: [[x, y], ...]} - the tiles its baker opened."""
    try:
        return json.loads(LIST_PATH.read_text(encoding="utf-8")).get("caves") or {}
    except (OSError, ValueError):
        return {}


def record(zone_name, tiles):
    caves = listed()
    caves[zone_name] = [list(t) for t in tiles]
    LIST_PATH.write_text(json.dumps({"caves": dict(sorted(caves.items()))}, separators=(",", ":"),
                                    ensure_ascii=False) + "\n", encoding="utf-8")


def apply(zones):
    """create_all_zones: open the tiles each cave's baker opened, where they are still plain rock."""
    caves = listed()
    for name, tiles in caves.items():
        z = zones.get(name)
        if z is None:
            continue
        for x, y in tiles:
            # "cliff" too: some bakers paint a cave's cliff walls as rock (bake_small_caves,
            # bake_ashenvale_dungeons), so their smoothing saw rock where the game has cliff.
            if z.collision_layer[y][x] in WALL_IDS + ("cliff",):
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if z.collision_layer[ny][nx] is None:
                        z.base_layer[y][x] = z.base_layer[ny][nx]
                        break
                z.collision_layer[y][x] = None
