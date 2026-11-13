#!/usr/bin/env python3
"""Every chest a zone module lists is on its map, where a player can get to it.

    PYTHONPATH=. python3 tools/qa_flats_chests.py

Found on the Shimmering Flats, 13 Nov 2026: the layout listed four chests and the map had three.
One was aimed at a cliff tile and the chest helper skipped it without saying so. Checked here for
every zone built on tools/tirisfal_kit.py that declares CHESTS, not only the Flats, because the
helper is shared and so is the way it fails.
"""
import contextlib
import importlib
import io
import os
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

ZONES = ["handbuilt_shimmering_flats", "handbuilt_southern_needles", "handbuilt_aspen_wilderness",
         "handbuilt_northern_tanaris", "handbuilt_abyssal_sands", "handbuilt_glittervein"]


def main():
    bad, total = [], 0
    with contextlib.redirect_stdout(io.StringIO()):
        from tools import tirisfal_kit as T
    for name in ZONES:
        with contextlib.redirect_stdout(io.StringIO()):
            M = importlib.import_module(f"tools.{name}")
            zone = T.build(M).zone
        want = list(getattr(M, "CHESTS", []))
        live = [(x, y) for y, row in enumerate(zone.interaction_layer)
                for x, k in enumerate(row) if k == "chest"]
        seen, q = {M.START}, deque([M.START])
        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if 0 <= n[0] < M.W and 0 <= n[1] < M.H and n not in seen and zone.is_walkable(*n):
                    seen.add(n)
                    q.append(n)
        total += len(live)
        if len(live) != len(want):
            bad.append(f"{M.NAME}: lists {len(want)} chests, the map has {len(live)}")
        for c in live:
            if not any((c[0] + dx, c[1] + dy) in seen for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                bad.append(f"{M.NAME}: the chest at {c} cannot be reached")
    print(f"{total} chests on {len(ZONES)} zones")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for line in bad:
            print("  -", line)
        return 1
    print("\nchests OK - every one listed is on its map and can be walked to.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
