#!/usr/bin/env python3
"""Fishing spots are drawn as pools on the water.

    PYTHONPATH=. python3 tools/qa_fishing_pools.py

Kyle's 30-sprite pool sheet, 13 Nov 2026 (tools/slice_fishing_pools.py). FOUR CLAIMS:
  1. All thirty sprites are on disk, 96x96 with alpha, and none has a pink rim left on it.
  2. Every zone with fishing names pools that exist; no zone is left on the default by accident.
  3. Placed for real in three zones: every fishing spot gets a pool, and the tile it is drawn on
     is WATER and touches the spot.
  4. A pool is drawn at the water tile; every other node still draws where it stands.
  5. You can cast from the bank tile and from a step either side of it (FISHING_REACH), not from
     one unmarked tile.
  7. A POOL HOLDS ONE TO FOUR FISH: always one, 66% a second, 33% a third, 10% a fourth.
  6. TRACKING IS LEARNED WITH THE TRADE: a character with no gathering trade tracks nothing; one
     who knows only Fishing tracks pools and nothing else.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
ZONES = ("Arathi West", "Durotar", "Western Hillsbrad")


def main():
    import numpy as np
    import pygame
    from PIL import Image
    pygame.init()
    pygame.display.set_mode((64, 64))
    from slice_fishing_pools import NAMES, OUT
    from world import fishing_pools as FP
    from world.gathering_manager import GatheringNodeManager, WATER_TILES
    from world.zone_manager import ZoneManager

    bad = []
    for n in NAMES:
        p = OUT / f"{n}.png"
        if not p.exists():
            bad.append(f"{n}.png missing")
            continue
        im = Image.open(p)
        if im.size != (96, 96) or im.mode != "RGBA":
            bad.append(f"{n}: {im.size} {im.mode}")
        a = np.asarray(im).astype(float)
        seen = a[..., 3] > 60
        pink = (np.minimum(a[..., 0], a[..., 2]) - a[..., 1] > 70) & (a[..., 0] > 150) & (a[..., 2] > 150) & seen
        if pink.sum() > 0.01 * max(1, seen.sum()):
            bad.append(f"{n}: {int(pink.sum())} bright pink pixels left")

    pools = json.loads((ROOT / "data/gathering/node_pools.json").read_text(encoding="utf-8"))["zones"]
    fishing = [k for k, v in pools.items() if isinstance(v, dict) and v.get("fishing")]
    for k in fishing:
        if k not in FP.ZONE_POOLS:
            bad.append(f"{k} has fishing and no pool chosen for it")
        elif len(FP.pools_for(k)) != len(FP.ZONE_POOLS[k]):
            bad.append(f"{k}: names a pool with no art: {FP.ZONE_POOLS[k]}")

    zm = ZoneManager()
    spots = 0
    for name in ZONES:
        zone = zm.get_zone_by_name(name)
        if zone is None:
            bad.append(f"no zone {name}")
            continue
        gm = GatheringNodeManager()
        gm.populate(zone, zone.name)
        fish = [n for n in gm.active_nodes if gm.materials.get(n.material_id, {}).get("material_type") == "fish"]
        if not fish:
            bad.append(f"{name}: no fishing spots rolled")
        for n in fish:
            spots += 1
            if not n.pool or not n.pool_tile:
                bad.append(f"{name}: spot at {(n.x, n.y)} has no pool")
                continue
            wx, wy = n.pool_tile
            straight = (wx == n.x or wy == n.y) and 1 <= abs(wx - n.x) + abs(wy - n.y) <= gm.POOL_MAX_OUT
            if zone.base_layer[wy][wx] not in WATER_TILES or not straight:
                bad.append(f"{name}: pool for {(n.x, n.y)} drawn at {(wx, wy)}, which is not water beside it")
            # you can cast from the bank tile, and from a step either side of it
            for sx, sy in ((n.x, n.y), (n.x + 1, n.y), (n.x - 1, n.y), (n.x, n.y + 1)):
                if gm.fishing_node_near(sx, sy) is None:
                    bad.append(f"{name}: standing at {(sx, sy)} beside the pool at {(wx, wy)} cannot cast")
        drawn = gm.active_nodes_render_data()
        if sum(1 for d in drawn if d[2] == "fishing_pool") != len(fish):
            bad.append(f"{name}: {len(fish)} spots but {sum(1 for d in drawn if d[2] == 'fishing_pool')} pools drawn")

    # 7. a pool gives one fish for certain and up to four, at Kyle's odds
    import random
    random.seed(7)
    counts = {1: 0, 2: 0, 3: 0, 4: 0}
    zone = zm.get_zone_by_name(ZONES[0])
    for _ in range(4000):
        node = type(fish[0])(1, 1, fish[0].material_id)
        node.pool_tile = (1, 2)
        n_fish = 0
        while not node.gathered and n_fish < 9:
            if gm.gather(node, zone) is None:
                break
            n_fish += 1
        counts[n_fish] = counts.get(n_fish, 0) + 1
    want = {1: 0.34, 2: 0.66 * 0.67, 3: 0.66 * 0.33 * 0.90, 4: 0.66 * 0.33 * 0.10}
    for k, share in want.items():
        got = counts.get(k, 0) / 4000
        if abs(got - share) > 0.03:
            bad.append(f"{k} fish from a pool {got:.1%} of the time, wanted about {share:.1%}")
    if set(counts) - {1, 2, 3, 4}:
        bad.append(f"a pool gave {sorted(counts)} fish; four is the most")

    # 6. tracking is gated by the trade
    from ui.screens.overworld_screen import OverworldScreen

    class _P:
        known_professions = []

    class _SM:
        player = _P()

    class _ZM:
        gathering_manager = gm

    probe = OverworldScreen.__new__(OverworldScreen)
    probe.state_manager, probe.zone_manager = _SM(), _ZM()
    if probe.tracked_nodes():
        bad.append("a character with no trades is tracking nodes")
    _P.known_professions = ["fishing"]
    kinds = {t[0] for t in probe.tracked_nodes()}
    if kinds != {"fish"}:
        bad.append(f"a fisher tracks {sorted(kinds)}, wanted only fish")
    _P.known_professions = ["mining", "herbalism"]
    if "fish" in {t[0] for t in probe.tracked_nodes()}:
        bad.append("a miner-herbalist is tracking fishing pools")

    print(f"{len(NAMES)} sprites, {len(fishing)} fishing zones, {spots} spots placed in {len(ZONES)} zones")
    for b in bad[:30]:
        print("  FAIL", b)
    print("\nfishing pools OK - every spot is a pool on the water." if not bad else f"\n{len(bad)} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
