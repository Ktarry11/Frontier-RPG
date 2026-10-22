"""
Terrain painter - bakes a whole outdoor zone into ONE continuous painting
from seamless material textures + hand-authored region/road/water/cliff maps.

WHY
---
The old per-zone pipeline tiled a handful of 20-tile "ground chunk" images
with a feather pass.  Result: flat fields, right-angle road stripes, blocky
tile-edge shorelines, no visible sub-areas.  The painter instead treats every
256px seamless tile (see assets/tiles/vot_cluster) as a MATERIAL and blends
them per pixel by smooth, domain-warped weight fields, so clay melts into
grass, grass into mud, mud into water; roads are curved splines; cliffs are
shaded with depth.

HOW THE RENDERER USES IT
------------------------
The output is a grid of CHUNK x CHUNK-tile JPEGs.  The SAME image rect is
registered as a ground chunk, a water chunk AND an obstacle chunk; the
renderer already clips each of those to its own tile kind (non-water /
water / cliff), and because all three are the same pixels the union is the
complete painting - so the visible shoreline / cliff edge is the smooth
baked one, while walkability stays on the tile grid.

All fields are evaluated by map_coordinates on a global mask grid, so
neighbouring chunks are continuous by construction (no seams).
"""
import os
import zlib
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

TILE_PX = 32
MASK_PX = 4           # mask-grid pixels per tile (field resolution)
TEX = 256


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


class Painter:
    def __init__(self, width_tiles, height_tiles, tex_dir, seed=7):
        self.W, self.H = width_tiles, height_tiles
        self.tex_dir = Path(tex_dir)
        self.rng = np.random.default_rng(seed)
        self.seed = seed
        self.mw, self.mh = width_tiles * MASK_PX, height_tiles * MASK_PX
        # tile-unit coordinates of every mask sample (cell centres)
        ys, xs = np.mgrid[0:self.mh, 0:self.mw]
        self.gx = (xs + 0.5) / MASK_PX
        self.gy = (ys + 0.5) / MASK_PX
        self._tex = {}
        self._noise_cache = {}

    # ---------------------------------------------------------------- textures
    def tex(self, name):
        if name not in self._tex:
            im = Image.open(self.tex_dir / f"{name}.png").convert("RGB")
            if im.size != (TEX, TEX):
                im = im.resize((TEX, TEX), Image.LANCZOS)
            self._tex[name] = np.asarray(im, dtype=np.float32)
        return self._tex[name]

    # ------------------------------------------------------------------ noise
    def noise(self, scale_tiles, key, octaves=3, persistence=0.5):
        """fbm value noise on the mask grid, ~[0,1]. Deterministic per key."""
        ck = (round(scale_tiles, 3), key, octaves)
        if ck in self._noise_cache:
            return self._noise_cache[ck]
        rng = np.random.default_rng(zlib.crc32(f'{self.seed}:{key}'.encode()))
        out = np.zeros((self.mh, self.mw), np.float32)
        amp, tot = 1.0, 0.0
        for o in range(octaves):
            sc = scale_tiles / (2 ** o)
            nx = int(self.W / sc) + 4
            ny = int(self.H / sc) + 4
            lat = rng.random((ny, nx)).astype(np.float32)
            zy = (self.gy / sc)
            zx = (self.gx / sc)
            layer = ndi.map_coordinates(lat, [zy, zx], order=3, mode="reflect")
            out += amp * layer
            tot += amp
            amp *= persistence
        out = out / tot
        out = (out - out.min()) / (out.max() - out.min() + 1e-6)
        self._noise_cache[ck] = out
        return out

    def warp(self, key="warp", amp_tiles=2.0, scale=14.0):
        """Return warped (gx, gy) for evaluating organic region shapes."""
        nx = (self.noise(scale, key + "x") - 0.5) * 2 * amp_tiles
        ny = (self.noise(scale, key + "y") - 0.5) * 2 * amp_tiles
        return self.gx + nx, self.gy + ny

    # ----------------------------------------------------------------- shapes
    def blob(self, cx, cy, rx, ry, soft=0.5, warp=None, rot=0.0):
        """1 inside the ellipse, smoothly fading to 0 over `soft` (fraction of radius)."""
        gx, gy = warp if warp is not None else (self.gx, self.gy)
        dx, dy = gx - cx, gy - cy
        if rot:
            c, s = np.cos(rot), np.sin(rot)
            dx, dy = c * dx + s * dy, -s * dx + c * dy
        d = np.sqrt((dx / rx) ** 2 + (dy / ry) ** 2)
        return 1.0 - smoothstep(1.0 - soft, 1.0 + 1e-3, d)

    def rect(self, x0, y0, x1, y1, soft_tiles=3.0, warp=None):
        gx, gy = warp if warp is not None else (self.gx, self.gy)
        ex = np.minimum(gx - x0, x1 - gx)
        ey = np.minimum(gy - y0, y1 - gy)
        return smoothstep(0, soft_tiles, np.minimum(ex, ey))

    # ------------------------------------------------------------------ roads
    @staticmethod
    def spline(points, step=0.35):
        """Catmull-Rom through points -> dense polyline (tile units)."""
        pts = [np.array(p, float) for p in points]
        pts = [pts[0] * 2 - pts[1]] + pts + [pts[-1] * 2 - pts[-2]]
        out = []
        for i in range(1, len(pts) - 2):
            p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
            seg = max(2, int(np.linalg.norm(p2 - p1) / step))
            for t in np.linspace(0, 1, seg, endpoint=False):
                t2, t3 = t * t, t * t * t
                out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                                  + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
        out.append(pts[-2])
        return np.array(out)

    def road_field(self, roads, jitter_key="road"):
        """roads: list of (points, width_tiles). Returns (core, verge) fields
        in [0,1]: core = the rutted road surface, verge = worn edge."""
        gx, gy = self.warp(jitter_key, amp_tiles=0.5, scale=5.0)
        core = np.zeros((self.mh, self.mw), np.float32)
        verge = np.zeros_like(core)
        q = np.stack([gx.ravel(), gy.ravel()], 1)
        for pts, width in roads:
            line = self.spline(pts)
            d, _ = cKDTree(line).query(q)
            d = d.reshape(self.mh, self.mw)
            core = np.maximum(core, 1 - smoothstep(width * 0.5 - 0.35, width * 0.5 + 0.35, d))
            verge = np.maximum(verge, 1 - smoothstep(width * 0.5, width * 0.5 + 1.8, d))
        return core, verge, None

    def road_dist(self, pts):
        line = self.spline(pts)
        q = np.stack([self.gx.ravel(), self.gy.ravel()], 1)
        d, _ = cKDTree(line).query(q)
        return d.reshape(self.mh, self.mw)

    # -------------------------------------------------------- tile-grid masks
    def tile_mask(self, tile_bool, threshold=0.5, noise_amp=0.18, key="m", sigma=1.15, soft=False):
        """Smooth, slightly noisy pixel-level mask from a tile boolean grid
        (so shorelines/cliff edges are organic but stay within ~half a tile
        of the real walkability grid)."""
        t = np.asarray(tile_bool, np.float32)
        f = ndi.gaussian_filter(np.pad(t, 4, mode="edge"), sigma)
        coords = [(self.gy - 0.5 + 4), (self.gx - 0.5 + 4)]
        v = ndi.map_coordinates(f, coords, order=3, mode="nearest")
        n = (self.noise(2.2, key, octaves=3) - 0.5) * 2 * noise_amp
        if soft:
            return (v + n) - threshold
        return (v + n) > threshold

    @staticmethod
    def edt(mask_bool):
        """distance (in mask px) from True pixels' complement..."""
        return ndi.distance_transform_edt(mask_bool)

    # ------------------------------------------------------------------ render
    def sample_field(self, field, X, Y):
        """Bilinear sample a mask-grid field at pixel coords X,Y (world px)."""
        cx = X / (TILE_PX / MASK_PX) - 0.5
        cy = Y / (TILE_PX / MASK_PX) - 0.5
        return ndi.map_coordinates(field, [cy, cx], order=1, mode="nearest")

    def bake(self, materials, scores, out_dir, chunk_tiles=20, tau=0.10, hscale=0.22,
             post=None, quality=90, prefix="ground", variant_mix=None, only=None):
        """
        materials: {name: (texA, texB_or_None, tile_scale)}  (texture file stems)
        scores:    {name: mask-grid float field (higher = wins)}
        post:      optional fn(rgb float (H,W,3), X, Y, painter) -> rgb  (cliff/water/AO/lighting)
        Writes <out_dir>/<prefix>_<cx>_<cy>.jpg for every chunk.
        """
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        names = list(materials)
        cp = chunk_tiles * TILE_PX
        mix_noise = self.noise(9.0, "variantmix", octaves=2)
        written = []
        for cy in range(0, self.H, chunk_tiles):
            for cx in range(0, self.W, chunk_tiles):
                if only is not None and (cx, cy) not in only:
                    continue
                wpx = min(chunk_tiles, self.W - cx) * TILE_PX
                hpx = min(chunk_tiles, self.H - cy) * TILE_PX
                ys, xs = np.mgrid[0:hpx, 0:wpx]
                X = (xs + cx * TILE_PX).astype(np.float32) + 0.5
                Y = (ys + cy * TILE_PX).astype(np.float32) + 0.5
                mix = self.sample_field(mix_noise, X, Y)
                cols, svals = [], []
                # skip materials that cannot reach a weight above ~1e-3 anywhere in this chunk (speed-up only)
                base = {n: self.sample_field(scores[n], X, Y) for n in names}
                bmax = np.max(np.stack(list(base.values())), axis=0)
                lum_b = hscale * 0.5
                active = [n for n in names if np.any(base[n] + lum_b > bmax - lum_b - 7.0 * tau)]
                for i, n in enumerate(names):
                    if n not in active:
                        continue
                    a, b, scale = materials[n]
                    ox, oy = (i * 83) % TEX, (i * 131) % TEX
                    sx = ((X / scale + ox) % TEX).astype(np.int32)
                    sy = ((Y / scale + oy) % TEX).astype(np.int32)
                    col = self.tex(a)[sy, sx]
                    if b:
                        sx2 = ((X / scale + ox + 97) % TEX).astype(np.int32)
                        sy2 = ((Y / scale + oy + 41) % TEX).astype(np.int32)
                        col2 = self.tex(b)[sy2, sx2]
                        m = smoothstep(0.42, 0.58, mix)[..., None]
                        col = col * (1 - m) + col2 * m
                    lum = col.mean(axis=2) / 255.0
                    s = base[n] + hscale * (lum - 0.5)
                    cols.append(col)
                    svals.append(s)
                S = np.stack(svals)
                S = (S - S.max(axis=0, keepdims=True)) / tau
                Wt = np.exp(S)
                Wt /= Wt.sum(axis=0, keepdims=True)
                rgb = np.zeros((hpx, wpx, 3), np.float32)
                for i in range(len(cols)):
                    rgb += Wt[i][..., None] * cols[i]
                if post:
                    rgb = post(rgb, X, Y, self)
                img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
                fn = out_dir / f"{prefix}_{cx}_{cy}.jpg"
                img.save(fn, quality=quality, optimize=True)
                written.append((fn, cx, cy, wpx // TILE_PX, hpx // TILE_PX))
        return written
