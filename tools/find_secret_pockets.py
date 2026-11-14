#!/usr/bin/env python3
"""Find places a secret could go, in every map.

    PYTHONPATH=. python3 tools/find_secret_pockets.py

Kyle, 14 Nov 2026: "pathways on maps that look like they can't be walked through, but they can"
and "look at echo isles map....then there's a shallow water you can walk to an island that doesn't
even appear. Is this possible?? That's how grim dawn does it."

The maps have almost no sealed ground of their own (the world builders flood-fill and clear what
nobody can reach), so a secret has to be MADE. Two kinds:

  GLADE   a hollow cut into the middle of a mass of rock, cliff or trees, with a ring of the mass
          left standing round it. The way in is one to four tiles of that same mass made walkable
          (Tilemap.secret_walkable) and nothing about how they look changes, so it reads as solid.
          On a cave map this is a secret room in the wall.
  ISLAND  a small patch of ground out in deep water, and a ford of shallow water to it from the
          shore. In the world you can see the ford if you look. On the map, until you have stood on
          it, both are drawn as deep water.

Picks are spread out (no two within 25 tiles in one map) and never touch a portal, an NPC, a chest,
a road or the map's edge. Writes data/world/secret_candidates.json for tools/build_secrets.py.
"""
import contextlib
import io
import json
import os
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

MASS = {"rock", "cliff", "tree"}            # what a glade can be cut from
DEEP = {"deep_water", "tropical_water"}
GROUND_FOR = {"tropical_water": "sand", "deep_water": "sand"}
EDGE = 4
SPREAD = 25


def walk_dist(tm, sources, passable, limit=None):
    """Multi-source BFS distance over tiles where passable(x, y), out to `limit` steps."""
    dist = {}
    q = deque()
    for s in sources:
        dist[s] = 0
        q.append(s)
    while q:
        x, y = q.popleft()
        if limit is not None and dist[(x, y)] >= limit:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n in dist or not (0 <= n[0] < tm.width and 0 <= n[1] < tm.height):
                continue
            if not passable(*n):
                continue
            dist[n] = dist[(x, y)] + 1
            q.append(n)
    return dist


def main_region(tm):
    best = set()
    seen = set()
    for y in range(tm.height):
        for x in range(tm.width):
            if (x, y) in seen or not tm.is_walkable(x, y):
                continue
            comp = set(walk_dist(tm, [(x, y)], tm.is_walkable))
            seen |= comp
            if len(comp) > len(best):
                best = comp
    return best


def ground_near(tm, x, y, main):
    for r in range(1, 8):
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                p = (x + dx, y + dy)
                if p in main:
                    b = tm.base_layer[p[1]][p[0]]
                    if b and b not in DEEP and b != "shallow_water":
                        return b
    return "grass"


def candidates(tm):
    main = main_region(tm)
    if not main:
        return []
    busy = set()
    for y in range(tm.height):
        for x in range(tm.width):
            if tm.interaction_layer[y][x]:
                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        busy.add((x + dx, y + dy))
    road = getattr(tm, "road_tiles", None) or set()
    inside = lambda x, y: EDGE <= x < tm.width - EDGE and EDGE <= y < tm.height - EDGE  # noqa: E731
    coll = lambda x, y: tm.collision_layer[y][x]  # noqa: E731
    base = lambda x, y: tm.base_layer[y][x]  # noqa: E731
    out = []

    # ---------------- glades: distance from walkable ground, through solid mass only
    def mass(x, y):
        return inside(x, y) and coll(x, y) in MASS and not tm.is_walkable(x, y)
    border = [p for p in main if any(mass(p[0] + dx, p[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    d = walk_dist(tm, border, lambda x, y: mass(x, y) or (x, y) in main)
    for (x, y), dv in sorted(d.items(), key=lambda kv: -kv[1]):
        if dv < 4 or (x, y) in busy or x % 3 or y % 3:
            continue
        if any(abs(x - p["spot"][0]) + abs(y - p["spot"][1]) < SPREAD for p in out):
            continue
        glade = [(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
        glade += [(x + dx, y + dy) for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)
                  if abs(dx) == 2 or abs(dy) == 2 if d.get((x + dx, y + dy), 0) >= 3]
        if not all(mass(*p) and p not in busy for p in glade):
            continue
        # the way in: shortest run of mass from the glade's edge to walkable ground
        way = walk_dist(tm, glade, mass, limit=5)
        best = None
        for p, dd in way.items():
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (p[0] + dx, p[1] + dy)
                if n in main and n not in busy and n not in road and (best is None or dd < best[0]):
                    best = (dd, p)
        if best is None or not 1 <= best[0] <= 4:
            continue
        # walk back to the glade
        path, cur = [best[1]], best[1]
        while way[cur] > 1:
            cur = next(n for n in ((cur[0] + 1, cur[1]), (cur[0] - 1, cur[1]), (cur[0], cur[1] + 1),
                                   (cur[0], cur[1] - 1)) if way.get(n) == way[cur] - 1)
            path.append(cur)
        kinds = {}
        for p in path + glade:
            kinds[coll(*p)] = kinds.get(coll(*p), 0) + 1
        out.append({"kind": "glade", "spot": [x, y], "area": [list(p) for p in glade],
                    "passage": [list(p) for p in path], "mask": max(kinds, key=kinds.get),
                    "ground": ground_near(tm, x, y, main), "depth": dv})

    # ---------------- islands: deep water far from any land, a ford back to the shore
    def deep(x, y):
        return inside(x, y) and base(x, y) in DEEP and not coll(x, y)
    painted = any(c.get("exact") for c in getattr(tm, "ground_chunks", []) or [])
    shore = [] if painted else [p for p in main if any(deep(p[0] + dx, p[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    wd = walk_dist(tm, shore, lambda x, y: deep(x, y) or (x, y) in main)
    for (x, y), dv in sorted(wd.items(), key=lambda kv: -kv[1]):
        if not 6 <= dv <= 12 or (x, y) in busy or x % 2 or y % 2:
            continue
        if any(abs(x - p["spot"][0]) + abs(y - p["spot"][1]) < SPREAD for p in out):
            continue
        isle = [(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
        isle += [(x + dx, y + dy) for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2))]
        if not all(deep(*p) and wd.get(p, 0) >= 4 for p in isle):
            continue
        cur, ford = (x, y), []
        while wd.get(cur, 0) > 1:
            cur = next(n for n in ((cur[0] + 1, cur[1]), (cur[0] - 1, cur[1]), (cur[0], cur[1] + 1),
                                   (cur[0], cur[1] - 1)) if wd.get(n) == wd[cur] - 1)
            if cur not in isle:
                ford.append(cur)
        if any(p in busy or p in road for p in ford):
            continue
        out.append({"kind": "island", "spot": [x, y], "area": [list(p) for p in isle],
                    "passage": [list(p) for p in ford], "mask": base(x, y),
                    "ground": GROUND_FOR.get(base(x, y), "sand"),
                    "shallow": "tropical_shallow" if base(x, y) == "tropical_water" else "shallow_water",
                    "depth": dv})

    # ---------------- behind: open ground a building's picture hides completely. Nothing is
    # carved; Kyle, 14 Nov: "Best thing about vendors or paths behind buildings....they don't
    # need sprites or entrance art."
    from world import npc_clearance as NC
    for lm in tm.landmarks:
        if not NC.is_building(lm) or lm["width_tiles"] < 5 or lm.get("rotation"):
            continue
        ax, ay, w, h = lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]
        hid = [(x, y) for y in range(ay, ay + h) for x in range(ax, ax + w)
               if (x, y) in main and (x, y) not in busy and (x, y) not in road and inside(x, y)
               and NC.covered(lm, x, y) >= 0.95]
        hid = [p for p in hid if sum((p[0] + dx, p[1] + dy) in main for dx in (-1, 0, 1)
                                     for dy in (-1, 0, 1) if dx or dy) >= 4]
        if len(hid) < 3:
            continue
        cx = sum(p[0] for p in hid) / len(hid)
        spot = min(hid, key=lambda p: (p[0] - cx) ** 2 + p[1])     # middle of the back, highest row
        out.append({"kind": "behind", "spot": list(spot), "area": [list(spot)], "passage": [],
                    "mask": None, "ground": None, "building": os.path.basename(lm["sprite_key"])[:-4],
                    "depth": 10 + len(hid) / 10})

    # spread out: the deepest first, then nothing within SPREAD of a pick
    out.sort(key=lambda c: -c["depth"])
    picked = []
    for c in out:
        if all(abs(c["spot"][0] - p["spot"][0]) + abs(c["spot"][1] - p["spot"][1]) >= SPREAD for p in picked):
            picked.append(c)
    return picked


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        import pygame
        pygame.init()
        pygame.display.set_mode((64, 64))
        from world.zone_manager import ZoneManager
        zm = ZoneManager()
    from collections import Counter
    result, totals = {}, Counter()
    for name, entry in sorted(zm.zones.items()):
        tm = entry["tilemap"]
        c = candidates(tm)
        for x in c:
            x["map_area"] = tm.width * tm.height
        if c:
            result[name] = c
            for x in c:
                totals[x["kind"]] += 1
    out = ROOT / "data/world/secret_candidates.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result) + "\n", encoding="utf-8")
    print(f"{dict(totals)} possible across {len(result)} maps")


if __name__ == "__main__":
    main()
