#!/usr/bin/env python3
"""Paint the hidden open-world maps (tools/handbuilt_skull_zones.py).

    PYTHONPATH=. python3 tools/bake_skull_zones.py [slug ...] [--preview DIR]

Same recipe as tools/bake_echo_isles.py: the landforms come from the zone module's fields(), the
same functions the tile grid is built from, so painting and collision can't drift. Each map names
its own materials (borrowed from its parent region, so it looks like it belongs to that part of
the world) and a tint and a darkening, because these are places that feel wrong.
"""
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools import handbuilt_skull_zones as Z               # noqa: E402
from tools.terrain_painter import Painter, smoothstep, TILE_PX  # noqa: E402

TEX = ROOT / "assets/tiles"


def build_scores(P, spec):
    S = {}
    wp = P.warp("regions", amp_tiles=2.2, scale=11.0)
    n_big = P.noise(10.0, "big", octaves=3)
    n_mid = P.noise(4.5, "mid", octaves=3)
    F = Z.fields(spec, P.gx, P.gy)
    land = F["land"].astype(np.float32)
    wet = F["wet"].astype(np.float32)
    deep = F["deep"].astype(np.float32)
    rock = F["rock"].astype(np.float32)
    road = F["road"].astype(np.float32)
    rock_f = np.clip(rock * 0.5, -0.4, 0.6).astype(np.float32)
    d_wo = np.maximum(-wet, 0)
    d_wi = np.maximum(wet, 0)
    d_co = ndi.gaussian_filter(np.maximum(-rock, 0), 1.2)
    d_ci = ndi.gaussian_filter(np.maximum(rock, 0), 1.2)
    P.fields = dict(d_wo=d_wo, d_wi=d_wi, d_co=d_co, d_ci=d_ci, cf=rock_f)

    mats = spec["materials"]
    S["land"] = (0.55 + 0.35 * (n_big - 0.5)).astype(np.float32)
    for k, ells in spec.get("regions", {}).items():
        if k not in mats:
            continue
        r = np.zeros_like(n_big)
        for (cx, cy, rx, ry) in ells:
            r = np.maximum(r, P.blob(cx, cy, rx, ry, 0.6, wp))
        S[k] = (0.1 + 1.1 * r * (0.65 + 0.35 * smoothstep(0.3, 0.6, n_mid))).astype(np.float32)
    for k in mats:
        if k not in S and k not in ("water_s", "water_d", "rock", "road"):
            S[k] = np.full_like(n_big, -2.0)
    if "road" in mats:
        core = smoothstep(-0.6, 0.4, road)
        S["road"] = (-2.0 + 3.2 * core).astype(np.float32)
    land_keys = [k for k in S if k not in ("water_s", "water_d", "rock")]
    w_s = np.clip(wet, -4, 6)
    w_d = np.clip(deep, -6, 6)
    S["water_s"] = (1.6 + 10 * w_s).astype(np.float32)
    S["water_d"] = (1.6 + 10 * w_s + 3.0 * w_d).astype(np.float32)
    knock = smoothstep(0.0, 0.7, wet)
    for k in land_keys:
        S[k] = (S[k] - 14.0 * knock).astype(np.float32)
    depth_dark = smoothstep(2.0, 6.0, d_ci)
    S["rock"] = (1.6 + 12 * rock_f - 1.0 * depth_dark).astype(np.float32)
    cl_k = smoothstep(0.0, 0.30, rock_f)
    wk = smoothstep(0.0, 1.2, rock)
    for k in list(S):
        if k != "rock":
            S[k] = (S[k] - 14.0 * cl_k - (120.0 * wk if k.startswith("water_") else 0.0)).astype(np.float32)
    return S


def make_post(spec):
    tint = np.array(spec.get("tint", (1, 1, 1)), np.float32)
    dark = float(spec.get("dark", 0.0))

    def post(rgb, X, Y, P):
        f = P.fields
        sf = lambda a: P.sample_field(a.astype(np.float32), X, Y)  # noqa: E731
        d_co, d_ci = sf(f["d_co"]), sf(f["d_ci"])
        d_wo, d_wi = sf(f["d_wo"]), sf(f["d_wi"])
        cf = sf(f["cf"])
        lum_n = P.sample_field(P.noise(16.0, "lumlow", octaves=2), X, Y)
        shade = 0.95 + 0.10 * lum_n
        shade *= 1 - 0.25 * (1 - smoothstep(0.0, 1.5, d_co))
        shade *= 1 - 0.28 * smoothstep(1.2, 7.0, d_ci)
        lip = smoothstep(0.0, 0.03, cf) * (1 - smoothstep(0.03, 0.14, cf))
        rgb = rgb * shade[..., None] + 18 * lip[..., None]
        foam = (1 - smoothstep(0.0, 0.34, d_wi)) * smoothstep(-0.05, 0.05, d_wi) * 0.30
        foam = foam * (1 - smoothstep(-0.05, 0.12, cf))
        rgb = rgb * (1 - foam[..., None]) + np.array([210, 220, 220], np.float32) * foam[..., None]
        # the mood: a cast over everything and a drift of murk, low and patchy, like weather
        murk = P.sample_field(P.noise(12.0, "murk", octaves=2), X, Y)
        rgb = rgb * tint[None, None, :] * (1 - dark * (0.6 + 0.8 * murk))[..., None]
        return rgb
    return post


def bake(name, preview=None):
    spec = Z.SPECS[name]
    P = Painter(spec["W"], spec["H"], TEX, seed=spec["seed"])
    scores = build_scores(P, spec)
    mats = {k: (a, b, 1.0) for k, (a, b) in spec["materials"].items() if k in scores}
    out = ROOT / Z.BAKED.format(spec["slug"])
    written = P.bake(mats, scores, out, chunk_tiles=20, post=make_post(spec))
    print(f"{name}: baked {len(written)} chunks -> {out}")
    if preview:
        full = Image.new("RGB", (spec["W"] * TILE_PX, spec["H"] * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        Path(preview).mkdir(parents=True, exist_ok=True)
        full.resize((spec["W"] * 8, spec["H"] * 8), Image.LANCZOS).save(Path(preview) / f"{spec['slug']}_full.png")


def main():
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    slugs = {s["slug"]: n for n, s in Z.SPECS.items()}
    keys = [slugs[a] for a in sys.argv[1:] if a in slugs] or list(Z.SPECS)
    for k in keys:
        bake(k, pv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
