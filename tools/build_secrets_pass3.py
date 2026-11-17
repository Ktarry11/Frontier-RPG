#!/usr/bin/env python3
"""Secrets, pass three: real hidden ground for most behind-a-building sellers, secrets for the maps that had none,
and long hidden runs across whole maps. Idempotent; ADDS to data/world/secrets.json and never re-runs the first
builder (tools/build_secrets.py must not be re-run: it would rebuild every seller's stock).

    PYTHONPATH=. python3 tools/build_secrets_pass3.py [--check]

Kyle, 17 Nov 2026, on the secrets backlog (docs/plaguelands_quests_towns_BACKLOG.md, "Secrets"):
  * 38 of the 52 hidden sellers were "behind a building" and nothing else. Most of them move into real hidden ground:
    a hollow cut into the rock, cliff or trees the map is walled with, reached through a way in that still looks
    solid (world/secrets.py: a glade). A few stay behind their buildings, Razor Hill's among them (Kyle asked for
    that one by name, to test with).
  * The Scarlet Monastery Grounds, The Lashings and Jaedenar had no secrets. They get some.
  * "dont be afraid to have LONGER secrets....like walking into a hidden thing in the bottom left of a map and ending
    up in top right". A few maps get a long run through the rock from one side to the other, with a cache in a room
    partway along it.
And the standing rules: hidden is truly hidden (the way in and the ground behind it keep their rock or trees, the map
keeps lying, nothing is drawn until you're in there), and Kyle is never told where. This script prints counts only.

Glades come from tools/find_secret_pockets.candidates() on the live maps, filtered so a new one never touches an
existing secret, a portal, an NPC or a road.
"""
import contextlib
import io
import json
import os
import random
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

SECRETS = ROOT / "data/world/secrets.json"
VENDORS = ROOT / "data/npcs/vendors.json"
LEVELS = ROOT / "data/zones/zone_levels.json"
TAG = "pass3"

#: Kyle asked for Razor Hill's by name; the rest of the keepers are whoever has no hollow to move to
KEEP_BEHIND = {"secret_razorhill_fence"}
TARGET_MOVED = 30
EMPTY_MAPS = ["Scarlet Monastery Grounds", "The Lashings", "Jaedenar"]
PER_EMPTY_MAP = 2
LONG_RUNS = 6
CLEAR = 8                  # a new secret keeps this far from any older one's tiles

FOUND = ["This wall isn't a wall.", "You've found a way nobody marked.", "Somebody cut a room into the rock here.",
         "The trees part, if you know where to push.", "There's a hollow back here nobody's walked in years.",
         "Whoever made this didn't want company."]
LONG_FOUND = ["The rock goes on, and so does the path through it.", "This passage runs a long way. Somebody dug it "
              "for a reason.", "A way through the mountain that isn't on any map."]


def load_world():
    with contextlib.redirect_stdout(io.StringIO()):
        import pygame
        pygame.init()
        pygame.display.set_mode((64, 64))
        from world.zone_manager import ZoneManager
        zm = ZoneManager()
    return {n: e["tilemap"] for n, e in zm.zones.items()}


def taken_tiles(secrets, zone):
    out = set()
    for s in secrets:
        if s["zone"] != zone:
            continue
        for x, y in list(s.get("passage") or []) + list(s.get("area") or []):
            out.add((x, y))
        c = s.get("cache")
        if c:
            out.add((c["x"], c["y"]))
        d = s.get("door")
        if d:
            out.add((d["x"], d["y"]))
    return out


def near(tiles, taken, r=CLEAR):
    if not taken:
        return False
    for x, y in tiles:
        for tx, ty in taken:
            if abs(tx - x) <= r and abs(ty - y) <= r:
                return True
    return False


#: what a hollow may be cut from, per map, past the finder's own rock, cliff and trees, for maps that aren't walled
#: with either (a glade's tiles keep their collision and their art, so it still looks like what it's cut from)
EXTRA_MASS = {"Scarlet Monastery Grounds": {"wall"}, "The Lashings": {"tropical_water"}}


def glades(tm, taken):
    """Fresh glade candidates on this map, clear of every older secret."""
    import find_secret_pockets as F
    out = []
    base_mass = set(F.MASS)
    F.MASS = base_mass | EXTRA_MASS.get(tm.name, set())
    try:
        found = F.candidates(tm)
    finally:
        F.MASS = base_mass
    for c in found:
        if c["kind"] != "glade":
            continue
        tiles = [tuple(p) for p in c["area"] + c["passage"]]
        if near(tiles, taken):
            continue
        out.append(c)
    return out


def nooks(tm, taken):
    """For a map whose walls are too thin for a full glade: a 3x3 room inside the wall,
    reached through one to three tiles of it. Same rules otherwise: clear of busy tiles, roads and older secrets."""
    import find_secret_pockets as F
    main = F.main_region(tm)
    W, H, E = tm.width, tm.height, 2
    kinds = set(F.MASS) | EXTRA_MASS.get(tm.name, set())
    busy = set()
    for y in range(H):
        for x in range(W):
            if tm.interaction_layer[y][x]:
                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        busy.add((x + dx, y + dy))
    road = getattr(tm, "road_tiles", None) or set()

    def mass(x, y):
        return E <= x < W - E and E <= y < H - E and tm.collision_layer[y][x] in kinds and not tm.is_walkable(x, y)
    out = []
    for y in range(E + 1, H - E - 1):
        for x in range(E + 1, W - E - 1):
            room = [(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
            if not all(mass(*p) and p not in busy for p in room) or near(room, taken, 4):
                continue
            # the way in: up to three tiles of wall to walkable ground
            way = F.walk_dist(tm, room, mass, limit=3)
            best = None
            for q, dd in way.items():
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    n = (q[0] + dx, q[1] + dy)
                    if n in main and n not in busy and n not in road and (best is None or dd < best[0]):
                        best = (dd, q)
            if best is None or best[0] < 1:
                continue
            path, cur = [best[1]], best[1]
            while way[cur] > 1:
                cur = next(n for n in ((cur[0] + 1, cur[1]), (cur[0] - 1, cur[1]), (cur[0], cur[1] + 1),
                                       (cur[0], cur[1] - 1)) if way.get(n) == way[cur] - 1)
                path.append(cur)
            k = {}
            for q in path + room:
                k[tm.collision_layer[q[1]][q[0]]] = k.get(tm.collision_layer[q[1]][q[0]], 0) + 1
            out.append({"kind": "glade", "spot": [x, y], "area": [list(q) for q in room],
                        "passage": [list(q) for q in path], "mask": max(k, key=k.get),
                        "ground": F.ground_near(tm, x, y, main), "depth": 3 + len(path)})
    picked = []
    for c in sorted(out, key=lambda c: -c["depth"]):
        if all(abs(c["spot"][0] - p["spot"][0]) + abs(c["spot"][1] - p["spot"][1]) >= 16 for p in picked):
            picked.append(c)
    return picked


def long_run(tm, taken, rnd):
    """The longest run through solid mass between two far-apart points of the map's walkable ground, or None."""
    import find_secret_pockets as F
    main = F.main_region(tm)
    if not main:
        return None
    E = F.EDGE
    W, H = tm.width, tm.height
    busy = set()
    for y in range(H):
        for x in range(W):
            if tm.interaction_layer[y][x]:
                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        busy.add((x + dx, y + dy))
    road = getattr(tm, "road_tiles", None) or set()

    def mass(x, y):
        return (E <= x < W - E and E <= y < H - E and tm.collision_layer[y][x] in F.MASS
                and not tm.is_walkable(x, y) and (x, y) not in taken)
    border = [(x, y) for y in range(H) for x in range(W) if mass(x, y)
              and any((x + dx, y + dy) in main and (x + dx, y + dy) not in busy and (x + dx, y + dy) not in road
                      for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    if len(border) < 2:
        return None
    border_set = set(border)
    want = 0.45 * max(W, H)
    best = None
    for start in rnd.sample(border, min(30, len(border))):
        dist, prev = {start: 0}, {start: None}
        q = deque([start])
        while q:
            cur = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (cur[0] + dx, cur[1] + dy)
                if n not in dist and mass(*n):
                    dist[n] = dist[cur] + 1
                    prev[n] = cur
                    q.append(n)
        for end, dv in dist.items():
            if end not in border_set:
                continue
            straight = ((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2) ** 0.5
            if straight < want or dv > 2.2 * straight:
                continue
            if best is None or dv > best[0]:
                best = (dv, start, end, prev)
    if best is None:
        return None
    dv, start, end, prev = best
    path, cur = [], end
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    if near(path, taken):
        return None
    # the room partway along: a 3x3 of mass round the middle, or failing that the middle tile itself
    mid = path[len(path) // 2]
    room = [(mid[0] + dx, mid[1] + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not all(mass(*p) or p in path for p in room):
        room = [mid]
    kinds = {}
    for p in path:
        kinds[tm.collision_layer[p[1]][p[0]]] = kinds.get(tm.collision_layer[p[1]][p[0]], 0) + 1
    return {"passage": [list(p) for p in path if p not in room], "area": [list(p) for p in room],
            "mask": max(kinds, key=kinds.get), "length": dv, "spot": list(mid),
            "ground": F.ground_near(tm, mid[0], mid[1], main)}


def zone_level(levels, zone):
    r = levels.get(zone) or [10]
    return int(max(r))


def main():
    check = "--check" in sys.argv
    rnd = random.Random(3)
    doc = json.loads(SECRETS.read_text(encoding="utf-8"))
    secrets = doc["secrets"]
    levels = json.loads(LEVELS.read_text(encoding="utf-8"))["zones"]
    vdoc = json.loads(VENDORS.read_text(encoding="utf-8"))
    vby = {v["vendor_id"]: v for v in vdoc["vendors"]}
    zones = load_world()
    counts = {"moved": 0, "kept": 0, "empty_map": 0, "long": 0}

    # ---- 1. behind-a-building sellers into real hidden ground
    behind = [s for s in secrets if s.get("kind") == "behind" and s.get("vendor")]
    already = sum(1 for s in secrets if s.get(TAG) == "moved")
    for s in sorted(behind, key=lambda s: s["id"]):
        if s["id"] in KEEP_BEHIND or already + counts["moved"] >= TARGET_MOVED:
            counts["kept"] += 1
            continue
        tm = zones.get(s["zone"])
        if tm is None:
            counts["kept"] += 1
            continue
        taken = taken_tiles([o for o in secrets if o is not s], s["zone"])
        cands = glades(tm, taken)
        if not cands:
            counts["kept"] += 1
            continue
        c = max(cands, key=lambda c: c["depth"])
        s.update(kind="glade", passage=c["passage"], area=c["area"], mask=c["mask"], ground=c["ground"],
                 found_text=rnd.choice(FOUND))
        s[TAG] = "moved"
        v = vby.get(s["vendor"])
        if v is not None:
            v["x"], v["y"] = c["spot"]
        counts["moved"] += 1
    counts["moved_total"] = already + counts["moved"]

    have = {s["id"] for s in secrets}

    # ---- 2. the maps that had none
    for zone in EMPTY_MAPS:
        tm = zones.get(zone)
        if tm is None:
            print(f"  WARNING: {zone} isn't a map")
            continue
        n_have = sum(1 for s in secrets if s["zone"] == zone)
        for i in range(n_have, PER_EMPTY_MAP):
            taken = taken_tiles(secrets, zone)
            cands = glades(tm, taken) or nooks(tm, taken)
            if not cands:
                break
            c = max(cands, key=lambda c: c["depth"])
            sid = f"secret3_{zone.lower().replace(' ', '_').replace(chr(39), '')}_{i + 1}"
            if sid in have:
                continue
            spot = c["spot"]
            secrets.append({"id": sid, "zone": zone, "kind": "glade", "passage": c["passage"], "area": c["area"],
                            "mask": c["mask"], "ground": c["ground"], "vendor": None, "door": None,
                            "cache": {"x": spot[0], "y": spot[1], "level": zone_level(levels, zone)},
                            "found_text": rnd.choice(FOUND), TAG: "empty_map"})
            have.add(sid)
            counts["empty_map"] += 1

    # ---- 3. long runs across whole maps: the open world's biggest masses of rock and forest
    done_long = [s for s in secrets if s.get(TAG) == "long"]
    if len(done_long) < LONG_RUNS:
        from world.zone_generator import create_all_zones  # noqa: F401  (zones already built above)
        pool = []
        for name, tm in zones.items():
            if getattr(tm, "is_cave", False) or getattr(tm, "is_town", False) or name in {s["zone"] for s in done_long}:
                continue
            if tm.width * tm.height < 120 * 120:
                continue
            run = long_run(tm, taken_tiles(secrets, name), rnd)
            if run and run["length"] >= 50:
                pool.append((name, run))
        pool.sort(key=lambda r: -r[1]["length"])
        for name, run in pool[:LONG_RUNS - len(done_long)]:
            sid = f"secret3_long_{name.lower().replace(' ', '_').replace(chr(39), '')}"
            if sid in have:
                continue
            spot = run["spot"]
            secrets.append({"id": sid, "zone": name, "kind": "glade", "passage": run["passage"], "area": run["area"],
                            "mask": run["mask"], "ground": run["ground"], "vendor": None, "door": None,
                            "cache": {"x": spot[0], "y": spot[1], "level": zone_level(levels, name)},
                            "found_text": rnd.choice(LONG_FOUND), TAG: "long"})
            have.add(sid)
            counts["long"] += 1

    if not check:
        SECRETS.write_text(json.dumps(doc, ensure_ascii=False) + "\n", encoding="utf-8")
        VENDORS.write_text(json.dumps(vdoc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    behind_left = sum(1 for s in secrets if s.get("kind") == "behind" and s.get("vendor"))
    print(f"pass three{' (check only)' if check else ''}: {counts['moved']} sellers moved into hidden ground this run "
          f"({counts['moved_total']} in all, {behind_left} still behind buildings), {counts['empty_map']} secrets "
          f"for the maps that had none, {counts['long']} long runs; {len(secrets)} secrets in all")
    return 0


if __name__ == "__main__":
    sys.exit(main())
