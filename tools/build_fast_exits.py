#!/usr/bin/env python3
"""A one-way exit past the last boss of every multi-tiered dungeon, out to the open world.

    PYTHONPATH=. python3 tools/build_fast_exits.py [--apply]

Kyle, 16 Nov 2026: "for the crown in stonetalon, and this is true for ANY multiple-tiered dungeon. At the very end
of the dungeon (after the final boss) - can you please make a fast exit from the dungeon to outside in the open
world. prevents people from running back".

THE VISIBLE DUNGEONS already have theirs in world/portal_manager.py (the Cistern, the Eldest's Crown, the Raider's
Hold, the Captain's Cabin), and tools/qa_dungeon_fast_exits.py holds every one of them to it. This tool does the
hidden levels: a hidden layer under a dungeon makes that dungeon multi-tiered, so its last boss gets an exit too.

For each hidden layer and deep frontier:
  * the EXIT TILE is open ground a few steps from its last boss, on the far side from the way in, that nothing is
    standing on;
  * the DESTINATION is the open-world tile in front of the door the whole dungeon is entered by (walking up the
    parents until a map that the open world leads into).
Written into data/world/hidden_zones.json as "fast_exit". It prints counts only: Kyle wants to find these places
himself, so nothing here says where they are.
"""
import argparse
import collections
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
PATH = ROOT / "data/world/hidden_zones.json"


def load_world():
    import pygame
    pygame.init()
    pygame.display.set_mode((1280, 720))
    from core.game_state import GameStateManager
    from entities.character import Character
    sm = GameStateManager(pygame.display.get_surface())
    sm.player = Character(name="H", char_class="Warrior", level=60)
    zm = sm._live_zone_manager()
    return {n: (e["tilemap"] if isinstance(e, dict) else e) for n, e in zm.zones.items()}


def flood(t, start):
    seen, q = {start}, collections.deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and 0 <= n[0] < t.width and 0 <= n[1] < t.height and t.is_walkable(*n):
                seen.add(n)
                q.append(n)
    return seen


def last_boss(t, creatures):
    """The highest-level boss on a map; on a tie, the one the map names as its boss (zone.boss_position)."""
    best = None
    named = tuple(getattr(t, "boss_position", None) or ())[:2]
    for b in getattr(t, "boss_positions", None) or []:
        lv = creatures.get(b[2] if len(b) > 2 else None, {}).get("level_range", [0, 0])[1]
        key = (lv, tuple(b[:2]) == named)
        if best is None or key > best[0]:
            best = (key, tuple(b[:2]))
    return best[1] if best else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--debug", action="store_true")
    a = ap.parse_args()
    from world.portal_manager import PortalManager
    from world.zone_classification import is_dungeon
    tiles = load_world()
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    doc = json.loads(PATH.read_text(encoding="utf-8"))
    reg = doc["zones"]
    links = PortalManager()._links

    def front_door(zone):
        """(open-world zone, x, y) in front of the door the dungeon `zone` sits in is entered by. A level under a
        hidden open-world map (a skull zone) comes out in that map, at its own secret door."""
        par = reg.get(zone, {}).get("parent")
        if par and (reg.get(par, {}).get("kind") == "skull" or reg.get(par, {}).get("frontier_type") == "open"):
            for (x, y), (d, _dx, _dy) in links.get(par, {}).items():
                if d == zone:
                    return par, x, y
        seen, todo = set(), [zone]
        while todo:                      # every dungeon map joined to this one, up through the parents
            z = todo.pop()
            if z in seen:
                continue
            seen.add(z)
            if reg.get(z, {}).get("parent"):
                todo.append(reg[z]["parent"])
            for (_p, (d, _x, _y)) in links.get(z, {}).items():
                if d not in seen and (is_dungeon(d) or d in reg) and reg.get(d, {}).get("kind") != "skull":
                    todo.append(d)
        for src, ps in links.items():
            if src in seen or src in reg or is_dungeon(src):
                continue
            for (x, y), (d, _dx, _dy) in ps.items():
                if d in seen and not reg.get(d):
                    return src, x, y
        return None

    made = skipped = 0
    for name, info in sorted(reg.items()):
        deep = info.get("kind") == "layer" or (info.get("kind") == "frontier"
                                              and info.get("frontier_type", "deep") == "deep")
        if not deep or name not in tiles:
            continue
        t = tiles[name]
        boss = last_boss(t, creatures)
        door = front_door(name)
        entry = next(iter(links.get(name, {})), None)      # the way back up, inside this map
        if boss is None or door is None:
            skipped += 1
            continue
        start = next(((boss[0] + dx, boss[1] + dy) for r in range(4) for dx in range(-r, r + 1)
                      for dy in range(-r, r + 1) if 0 <= boss[0] + dx < t.width and 0 <= boss[1] + dy < t.height
                      and t.is_walkable(boss[0] + dx, boss[1] + dy)), None)
        reach = flood(t, start) if start else set()
        cands = []
        for (x, y) in reach:
            d = abs(x - boss[0]) + abs(y - boss[1])
            if not 3 <= d <= 7 or t.get_tile(x, y, "interaction") is not None:
                continue
            if not all(t.is_walkable(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                continue
            far = abs(x - entry[0]) + abs(y - entry[1]) if entry else 0
            cands.append((-far, d, x, y))
        if not cands:
            skipped += 1
            continue
        _f, _d, x, y = min(cands)
        info["fast_exit"] = [x, y, door[0], door[1], door[2]]
        made += 1
    print(f"fast exits: {made} hidden levels given one, {skipped} could not be placed")
    if "--debug" in sys.argv:
        for n, i in reg.items():
            if i.get("fast_exit"):
                print("  ", n, i.get("kind"), i.get("parent"), "->", i["fast_exit"])
    if a.apply and made:
        PATH.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {PATH.relative_to(ROOT)}")
    return 0 if not skipped else 1


if __name__ == "__main__":
    sys.exit(main())
