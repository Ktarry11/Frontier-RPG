"""
Which material actually wins each tile of the Aspen Wilderness, and where.

    PYTHONPATH=. python3 tools/aspen_palette_report.py

A bake takes six minutes and produces one picture. When that picture comes out the wrong COLOUR - too
brown, too grey, no green - the picture itself does not say which score field is responsible, and guessing
at the weights and re-baking is a six-minute round trip per guess.

This runs the baker's own build_scores on the tile grid and prints the argmax histogram, overall and by
latitude band. It is seconds, not minutes, and it answers the only question that matters when a palette
is wrong: what is winning, and what is it beating.
"""
import os
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools import handbuilt_aspen_wilderness as M          # noqa: E402
from tools import bake_aspen_zone as B                      # noqa: E402
from tools.tirisfal_kit import wob                          # noqa: E402

W, H = M.W, M.H


class P:
    """Stand-in for Painter: build_scores only needs gx/gy, noise, blob, warp, road_field."""

    def __init__(self, seed):
        self.gx, self.gy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
        self._c = {}

    def noise(self, scale, key, octaves=1):
        if key in self._c:
            return self._c[key]
        a = np.zeros_like(self.gx)
        amp, f, tot = 1.0, 1.0 / max(scale, 1e-3), 0.0
        h = abs(hash(key)) % 977
        for _ in range(max(octaves, 1)):
            a = a + amp * wob(self.gx * f + h, self.gy * f + h * 0.37)
            tot += amp
            amp *= 0.5
            f *= 2.0
        a = a / max(tot, 1e-6)
        a = (a - a.min()) / max(a.max() - a.min(), 1e-6)
        self._c[key] = a.astype(np.float32)
        return self._c[key]

    def warp(self, key, amp_tiles=2.0, scale=8.0):
        return ((self.noise(scale, key + "wx") - 0.5) * 2 * amp_tiles,
                (self.noise(scale, key + "wy") - 0.5) * 2 * amp_tiles)

    def blob(self, cx, cy, rx, ry, soft, warp=None):
        gx, gy = self.gx, self.gy
        if warp is not None:
            gx, gy = gx + warp[0], gy + warp[1]
        d = np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2)
        return B.smoothstep(1.0 + soft, 1.0 - soft, d).astype(np.float32)

    def road_field(self, roads):
        """Mirrors terrain_painter.Painter.road_field closely enough to score with.

        NOT M.road_dist - that is an INVERSE distance (positive means ON the road, like _chute), and
        reading it as a plain distance made every tile in the zone a road and this whole report useless.
        """
        core = np.zeros_like(self.gx)
        verge = np.zeros_like(self.gx)
        for pts, width in roads:
            d = M._poly_dist(self.gx, self.gy, pts)
            core = np.maximum(core, 1 - B.smoothstep(width * 0.5 - 0.35, width * 0.5 + 0.35, d))
            verge = np.maximum(verge, 1 - B.smoothstep(width * 0.5, width * 0.5 + 1.8, d))
        return core.astype(np.float32), verge.astype(np.float32), None

    def sample_field(self, a, X, Y):
        return a


def main():
    p = P(M.SEED)
    S = B.build_scores(p, M)
    names = list(B.MATERIALS)
    stack = np.stack([S[k] for k in names])
    win = np.array(names, dtype=object)[np.argmax(stack, axis=0)]

    gx, gy = p.gx, p.gy
    kinds = np.asarray(M.tile_kind(gx, gy)).reshape(H, W)
    dry = kinds == 0

    print(f"{'material':<12} {'all':>7}   " + "  ".join(f"y{a}-{b}".rjust(9) for a, b in BANDS))
    counts = Counter(win[dry].tolist())
    tot = max(int(dry.sum()), 1)
    band_counts = []
    for a, b in BANDS:
        m = dry[a:b]
        band_counts.append((Counter(win[a:b][m].tolist()), max(int(m.sum()), 1)))
    for k, n in counts.most_common():
        row = f"{k:<12} {100.0 * n / tot:6.2f}%   "
        row += "  ".join(f"{100.0 * bc.get(k, 0) / bt:8.2f}%" for bc, bt in band_counts)
        print(row)
    print()
    print(f"rock (cliff tiles)   {100.0 * (kinds == 3).mean():.1f}% of map")
    print(f"water                {100.0 * ((kinds == 1) | (kinds == 2)).mean():.1f}% of map")
    snow = 100.0 * ((win == "snow") & dry).sum() / tot
    print(f"snow                 {snow:.2f}% of dry land  (budget {100 * B.SNOW_BUDGET:.1f}%)")


BANDS = [(0, 28), (28, 52), (52, 105), (105, 150), (150, 180)]

if __name__ == "__main__":
    main()
