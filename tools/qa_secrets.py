#!/usr/bin/env python3
"""Secrets work: hidden paths, hidden sellers, one-time caches, and a map that lies.

    PYTHONPATH=. python3 tools/qa_secrets.py

Kyle, 14 Nov 2026: "pathways on maps that look like they can't be walked through, but they can",
"don't tell me where they are", "is it possible to have the map LIE to you?", "Don't have map
redraw. It can stay blank." See world/secrets.py.

Prints counts only, never places: Kyle wants to find them himself.

CLAIMS
  1. Every secret's map exists, and its seller or cache can be walked to from the map's main ground.
  2. A path that shouldn't exist is walkable, and still drawn as what it pretends to be: its tiles
     keep their collision (the rock is still rock to look at) and the map's mask covers them.
  3. Hidden sellers have no map icon or dot, and every item on their shelves can be made, including
     every one-of-a-kind item.
  4. A cache gives rare or better, and never comes back after it is opened.
  5. A secret recipe is sold by its hidden seller and by nobody else.
  6. The map keeps lying after a secret is found.
  7. An island can never be seen from ordinary ground. Kyle, 14 Nov: "They should not be visible
     from the main land" and "Ensure islands or caves can't EVER be seen from main path". With the
     real camera (800x600 viewport, 32px tiles, clamped at the map's edges), no walkable tile that
     isn't part of a secret puts any of an island, or the three tiles round it, on screen.
  8. A secret's cache or seller is not drawn until you're in its secret ground and close (or, behind
     a building, just close). Kyle: "Hidden should be HIIIIIIIIDEN". world/secrets.Secrets.shows.
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

RANK = {"poor": 0, "common": 1, "uncommon": 2, "rare": 3, "epic": 4, "legendary": 5}


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        import pygame
        pygame.init()
        pygame.display.set_mode((64, 64))
        from world.zone_manager import ZoneManager
        from world.secrets import get_secrets
        from world.vendor_stock import resolve_vendor_item
        zm = ZoneManager()
    S = get_secrets()
    bad = []
    zones = {n: e["tilemap"] for n, e in zm.zones.items()}
    if not S.secrets:
        bad.append("no secrets at all")

    def main_region(tm):
        best = set()
        seen = set()
        for y in range(0, tm.height):
            for x in range(0, tm.width):
                if (x, y) in seen or not tm.is_walkable(x, y) or (x, y) in tm.secret_walkable:
                    continue
                comp, q = {(x, y)}, deque([(x, y)])
                while q:
                    cx, cy = q.popleft()
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        n = (cx + dx, cy + dy)
                        if n not in comp and 0 <= n[0] < tm.width and 0 <= n[1] < tm.height \
                                and tm.is_walkable(*n) and n not in tm.secret_walkable:
                            comp.add(n)
                            q.append(n)
                seen |= comp
                if len(comp) > len(best):
                    best = comp
        return best

    def reach(tm, start_set, goal):
        q, seen = deque(start_set), set(start_set)
        while q:
            p = q.popleft()
            if p == goal:
                return True
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (p[0] + dx, p[1] + dy)
                if n not in seen and 0 <= n[0] < tm.width and 0 <= n[1] < tm.height and tm.is_walkable(*n):
                    seen.add(n)
                    q.append(n)
        return False

    mains = {}
    kinds = {}
    vendors = zm.vendor_manager.vendors
    for s in S.secrets:
        kinds[s.get("kind")] = kinds.get(s.get("kind"), 0) + 1
        tm = zones.get(s["zone"])
        if tm is None:
            bad.append(f"secret {s['id']}: map does not exist")
            continue
        if s["zone"] not in mains:
            mains[s["zone"]] = main_region(tm)
        m = mains[s["zone"]]
        goal = None
        if s.get("cache"):
            goal = (s["cache"]["x"], s["cache"]["y"])
            if tm.get_tile(goal[0], goal[1], "interaction") != "chest":
                bad.append(f"secret {s['id']}: its cache has no chest")
        if s.get("vendor"):
            v = vendors.get(s["vendor"])
            if v is None:
                bad.append(f"secret {s['id']}: seller {s['vendor']} does not exist")
            else:
                goal = (v.x, v.y)
                if not getattr(v, "hidden", False):
                    bad.append(f"secret {s['id']}: seller is not hidden")
        if goal and not tm.is_walkable(*goal):
            bad.append(f"secret {s['id']}: its seller or cache stands on ground nobody can walk")
        elif goal and goal not in m:
            near = [(goal[0] + dx, goal[1] + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
            start = [p for p in m if abs(p[0] - goal[0]) + abs(p[1] - goal[1]) < 12] or list(m)[:1]
            if not any(p in m for p in near) and not reach(tm, start, goal):
                bad.append(f"secret {s['id']}: cannot be walked to")
        for x, y in s.get("passage") or []:
            if s.get("kind") == "glade":
                if not tm.is_walkable(x, y):
                    bad.append(f"secret {s['id']}: its hidden path is not walkable")
                    break
                if tm.collision_layer[y][x] is None:
                    bad.append(f"secret {s['id']}: its hidden path lost its rock (it would show)")
                    break
        if s.get("mask"):
            mask = getattr(tm, "map_mask", {}) or {}
            if any((x, y) not in mask for x, y in s.get("area") or []):
                bad.append(f"secret {s['id']}: the map tells the truth about it")

    # 3. hidden sellers' shelves
    hidden = [v for v in vendors.values() if getattr(v, "hidden", False)]
    uniques = 0
    for v in hidden:
        for sid in v.sells:
            item = resolve_vendor_item(sid)
            if item is None:
                bad.append(f"hidden seller {v.vendor_id}: '{sid}' cannot be made")
            elif str(sid).startswith("unique:"):
                uniques += 1
    # map icons: the map screen skips them (checked by reading the same flags it reads)
    from world.travel_manager import services_for_npc
    for v in hidden:
        if services_for_npc(v):
            bad.append(f"hidden seller {v.vendor_id} offers a service, so the map would mark it")

    # 4. caches
    from world.chest_manager import ChestManager
    cm = ChestManager()
    caches = [s for s in S.secrets if s.get("cache")]
    for s in caches[:6]:
        tm = zones[s["zone"]]
        c = s["cache"]
        item = cm.open_secret_cache(tm, c["x"], c["y"], player_level=c.get("level", 20))
        if item is None or RANK.get(getattr(item, "rarity", "poor"), 0) < RANK["rare"]:
            bad.append(f"a cache gave {getattr(item, 'rarity', None)}")
        cm.RESPAWN_CHANCE_OVERWORLD = cm.RESPAWN_CHANCE_DUNGEON = 1.0
        cm._next_roll.clear()
        cm.on_enter_zone(tm)
        if tm.get_tile(c["x"], c["y"], "interaction") == "chest":
            bad.append("an opened cache came back")
        tm.set_tile(c["x"], c["y"], "chest", "interaction")      # put it back for later checks

    # 5. secret recipes
    from world.recipe_manager import _load_all_recipes
    secret = {rid for rid, (_p, r) in _load_all_recipes().items() if r.get("secret")}
    for rid in secret:
        sellers = [v for v in vendors.values() if rid in v.sells]
        if not sellers:
            bad.append(f"secret recipe {rid} is sold by nobody")
        elif any(not getattr(v, "hidden", False) for v in sellers):
            bad.append(f"secret recipe {rid} is sold in town")

    # 6. the map keeps lying after a find
    for s in S.secrets:
        if s.get("mask") and s.get("area"):
            tm = zones[s["zone"]]
            x, y = s["area"][0]
            S.on_step(tm, x, y)
            if (x, y) not in (getattr(tm, "map_mask", {}) or {}):
                bad.append("the map redrew a secret after it was found")
            break

    # 7. islands stay off screen from ordinary ground
    import numpy as np
    TS, VW, VH = 32, 800, 600
    secret_tiles = {}
    for s in S.secrets:
        for x, y in list(s.get("passage") or []) + list(s.get("area") or []):
            secret_tiles.setdefault(s["zone"], set()).add((x, y))
    unseen_ok = 0
    for s in S.secrets:
        if s.get("kind") not in ("island", "baked_island") or s["zone"] not in zones:
            continue
        tm = zones[s["zone"]]
        W, H = tm.width, tm.height
        mine = secret_tiles.get(s["zone"], set())
        walk = np.zeros((H, W), bool)
        for y in range(H):
            for x in range(W):
                walk[y, x] = tm.is_walkable(x, y) and (x, y) not in mine
        # the ground a player gets to without the secret: the biggest walkable piece
        lab = np.zeros((H, W), int)
        sizes, n = [0], 0
        for y in range(H):
            for x in range(W):
                if walk[y, x] and not lab[y, x]:
                    n += 1
                    lab[y, x] = n
                    q, c = deque([(x, y)]), 1
                    while q:
                        cx, cy = q.popleft()
                        for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                            if 0 <= nx < W and 0 <= ny < H and walk[ny, nx] and not lab[ny, nx]:
                                lab[ny, nx] = n
                                c += 1
                                q.append((nx, ny))
                    sizes.append(c)
        ground = lab == int(np.argmax(sizes))
        diff = np.zeros((H + 1, W + 1), int)
        ys, xs = np.nonzero(ground)
        camx = np.clip(xs * TS - VW // 2 + TS // 2, 0, max(0, W * TS - VW))
        camy = np.clip(ys * TS - VH // 2 + TS // 2, 0, max(0, H * TS - VH))
        for a, b, c, d in zip(camx // TS, np.minimum(W, (camx + VW - 1) // TS + 1),
                              camy // TS, np.minimum(H, (camy + VH - 1) // TS + 1)):
            diff[c, a] += 1
            diff[c, b] -= 1
            diff[d, a] -= 1
            diff[d, b] += 1
        seen = np.cumsum(np.cumsum(diff, 0), 1)[:H, :W] > 0
        shown = sum(1 for x, y in s.get("area") or [] for dx in range(-3, 4) for dy in range(-3, 4)
                    if 0 <= x + dx < W and 0 <= y + dy < H and seen[y + dy, x + dx])
        if shown:
            bad.append(f"secret {s['id']}: {shown} tiles of the island (or round it) can be seen from ordinary ground")
        else:
            unseen_ok += 1

    # 8. caches and hidden sellers aren't drawn from outside their secret
    shown_from_outside = 0
    for s in S.secrets:
        tm = zones.get(s["zone"])
        if tm is None:
            continue
        spot = (s["cache"]["x"], s["cache"]["y"]) if s.get("cache") else None
        if s.get("vendor") and s["vendor"] in vendors:
            spot = (vendors[s["vendor"]].x, vendors[s["vendor"]].y)
        if spot is None:
            continue
        inside = {(x, y) for x, y in list(s.get("passage") or []) + list(s.get("area") or [])}
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                p = (spot[0] + dx, spot[1] + dy)
                if p in inside or p == spot or not (0 <= p[0] < tm.width and 0 <= p[1] < tm.height):
                    continue
                if not tm.is_walkable(*p):
                    continue
                if s.get("kind") != "behind" and S.shows(s["zone"], spot[0], spot[1], p, vendor_id=s.get("vendor")):
                    shown_from_outside += 1
        far = (spot[0] + 12, spot[1])
        if S.shows(s["zone"], spot[0], spot[1], far, vendor_id=s.get("vendor")):
            shown_from_outside += 1
        if not S.shows(s["zone"], spot[0], spot[1], spot, vendor_id=s.get("vendor")):
            bad.append(f"secret {s['id']}: not drawn even when you're standing on it")
    if shown_from_outside:
        bad.append(f"{shown_from_outside} times a secret's cache or seller is drawn for someone outside it")

    print(f"{unseen_ok} islands out of sight of ordinary ground")
    print(f"{len(S.secrets)} secrets ({', '.join(f'{k} {n}' for k, n in sorted(kinds.items(), key=str))}); "
          f"{len(hidden)} hidden sellers, {uniques} one-of-a-kind items on their shelves, "
          f"{len(caches)} caches, {len(secret)} secret recipes")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad[:25]:
            print("  -", b)
        return 1
    print("\nSecrets OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
