#!/usr/bin/env python3
"""Every multi-tiered dungeon has a fast way out past its last boss.

    PYTHONPATH=. python3 tools/qa_dungeon_fast_exits.py

Kyle, 16 Nov 2026: "for the crown in stonetalon, and this is true for ANY multiple-tiered dungeon. At the very end
of the dungeon (after the final boss) - can you please make a fast exit from the dungeon to outside in the open
world. prevents people from running back".

A DUNGEON CHAIN is two or more boss maps joined by doors (the Mother Vein and the Cistern, the Eldest's trunk and
crown, the Bloodsail ships, and every dungeon with a hidden level under it). For each one:
  * its LAST BOSS is the highest-level boss on any of its maps;
  * on that boss's map there is a door out of the chain that can be walked to from the boss;
  * that door is ONE WAY: nothing outside leads back in through it (Kyle on the Cistern: "the portal outside is
    one way").
Hidden chains are counted, never named.
"""
import collections
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from world.dungeon_packs import ALSO_DUNGEONS  # noqa: E402  (boss maps that are dungeons in all but name)


def main():
    from tools.build_fast_exits import flood, last_boss, load_world
    from world.hidden_zones import is_hidden, registry
    from world.portal_manager import PortalManager
    from world.zone_classification import is_dungeon
    tiles = load_world()
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    reg = registry()
    links = PortalManager()._links

    def dungeonish(n):
        if n not in tiles or not getattr(tiles[n], "boss_positions", None):
            return False
        if reg.get(n, {}).get("kind") == "skull" or reg.get(n, {}).get("frontier_type") == "open":
            return False
        return is_dungeon(n) or n in ALSO_DUNGEONS or reg.get(n, {}).get("kind") in ("layer", "frontier")

    maps = {n for n in tiles if dungeonish(n)}
    adj = collections.defaultdict(set)
    for z, ps in links.items():
        for (_p, (d, _x, _y)) in ps.items():
            if z in maps and d in maps:
                adj[z].add(d)
                adj[d].add(z)
    chains, seen = [], set()
    for n in sorted(maps):
        if n in seen:
            continue
        comp, q = {n}, [n]
        while q:
            a = q.pop()
            for b in adj[a] - comp:
                comp.add(b)
                q.append(b)
        seen |= comp
        if len(comp) > 1:
            chains.append(comp)

    bad, named, hidden = [], [], 0
    for comp in chains:
        best = None
        for m in comp:
            b = last_boss(tiles[m], creatures)
            if b is None:
                continue
            lv = max((creatures.get(x[2], {}).get("level_range", [0, 0])[1]
                      for x in tiles[m].boss_positions if len(x) > 2), default=0)
            if best is None or lv > best[0]:
                best = (lv, m, b)
        _lv, fm, boss = best
        t = tiles[fm]
        start = next(((boss[0] + dx, boss[1] + dy) for r in range(5) for dx in range(-r, r + 1)
                      for dy in range(-r, r + 1) if 0 <= boss[0] + dx < t.width and 0 <= boss[1] + dy < t.height
                      and t.is_walkable(boss[0] + dx, boss[1] + dy)), None)
        reach = flood(t, start) if start else set()
        outs = [(p, d) for p, d in links.get(fm, {}).items() if d[0] not in comp]
        good = [(p, d) for p, d in outs if any((p[0] + a, p[1] + b) in reach for a in (-1, 0, 1) for b in (-1, 0, 1))]
        secret = any(is_hidden(m) for m in comp)
        label = "a hidden dungeon level" if secret else " -> ".join(sorted(comp))
        if not good:
            bad.append(f"{label}: no way out past its last boss")
        for (p, (dz, _x, _y)) in good:
            back = [q for q, (z2, x2, y2) in links.get(dz, {}).items() if z2 == fm and (x2, y2) == p]
            if back:
                bad.append(f"{label}: its fast exit can be walked into from outside")
        if secret:
            hidden += 1
        else:
            named.append(f"{fm} (after {next(x[2] for x in t.boss_positions if tuple(x[:2]) == boss)})")
    print(f"{len(chains)} multi-tiered dungeons: {len(named)} visible, {hidden} with a hidden level")
    for n in named:
        print("  fast exit:", n)
    if bad:
        print(f"FAIL ({len(bad)})")
        for b in bad:
            print("  -", b)
        return 1
    print("PASS - every multi-tiered dungeon has a one-way fast exit past its last boss")
    return 0


if __name__ == "__main__":
    sys.exit(main())
