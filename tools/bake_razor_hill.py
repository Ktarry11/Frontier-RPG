"""
Bake the Razor Hill painting (plateau ground + roads + plaza + cliff rim) from
the seamless Valley-of-Trials materials.

    python3 tools/bake_razor_hill.py [--preview out.png] [--scale 14]

Landforms come from tools/handbuilt_razor_hill.fields() - the same functions the
tile grid is built from.  Writes assets/tiles/razor_hill/baked/ground_<cx>_<cy>.jpg.
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

from tools import handbuilt_razor_hill as R              # noqa: E402
from tools.terrain_painter import Painter, smoothstep, TILE_PX  # noqa: E402

TEX_DIR = ROOT / "assets/tiles/vot_cluster"

MATERIALS = {
    "clay":    ("vot_clay_a", "vot_clay_pebbles", 1.0),
    "hard":    ("vot_hardpan", None, 1.0),
    "cinder":  ("vot_cinder", None, 1.0),
    "gravel":  ("vot_gravel", "vot_gravel_flat", 1.0),
    "sage":    ("vot_sagegrass", None, 1.0),
    "camp":    ("vot_camp_prints", "vot_clay_pebbles", 1.0),
    "flag":    ("vot_flag_red", None, 1.0),
    "road":    ("vot_road_ruts_a", "vot_road_ruts_b", 1.0),
    "planks":  ("vot_planks", None, 1.0),
    "cliff_a": ("vot_cliff_a", "vot_cliff_b", 1.0),
    "cliff_d": ("vot_rock_dark", None, 1.0),
    "cliff_l": ("vot_limestone", None, 1.0),
}


def build_scores(P):
    S = {}
    gx, gy = P.gx, P.gy
    wp = P.warp("regions", amp_tiles=1.8, scale=10.0)
    n_big = P.noise(9.0, "big", octaves=3)
    n_mid = P.noise(4.5, "mid", octaves=3)
    n_fine = P.noise(2.0, "fine", octaves=2)

    cliff = R.fields(gx, gy)["cliff"].astype(np.float32)
    cliff_f = np.clip(cliff * 0.5, -0.4, 0.6).astype(np.float32)
    d_co = ndi.gaussian_filter(np.maximum(-cliff, 0), 1.2)
    d_ci = ndi.gaussian_filter(np.maximum(cliff, 0), 1.2)
    P.fields = dict(cliff=cliff, d_co=d_co, d_ci=d_ci, cf=cliff_f)

    # base: clay, with hardpan and gravel patches
    S["clay"] = np.full_like(n_big, 0.50)
    S["hard"] = 0.28 + 0.55 * smoothstep(0.58, 0.80, n_big)
    S["gravel"] = 0.22 + 0.60 * smoothstep(0.64, 0.84, n_mid) * (0.6 + 0.4 * n_fine)

    cx, cy, rx, ry = R.PLAZA
    plaza = P.blob(cx, cy, rx + 1.5, ry + 1.2, 0.6, wp)
    flag = P.blob(cx, cy, 3.6, 3.0, 0.55, wp)
    court = P.blob(30, 17, 12, 5, 0.6, wp)                   # barracks parade ground
    smithy = P.blob(13, 21, 6.5, 4.5, 0.6, wp)
    yard = P.blob(14, 45, 8, 4.5, 0.6, wp)                   # training yard
    market = P.blob(43, 34, 8, 5.5, 0.6, wp)
    refugee = P.blob(47, 45, 7, 4.5, 0.6, wp)
    garden = P.blob(10, 34, 5.5, 4.0, 0.6, wp)
    gate = P.blob(30, 48, 8, 4.0, 0.6, wp)

    S["camp"] = 0.12 + 1.15 * np.maximum.reduce([plaza * 1.0, court * 0.8, yard * 0.9,
                                                 refugee * 0.8, market * 0.55, gate * 0.5])
    S["flag"] = 0.10 + 1.25 * flag
    S["cinder"] = 0.10 + 0.95 * smithy * (0.55 + 0.45 * smoothstep(0.3, 0.6, n_mid))
    S["sage"] = 0.10 + 0.95 * garden * (0.55 + 0.45 * smoothstep(0.3, 0.55, n_mid))
    S["hard"] = np.maximum(S["hard"], 0.2 + 0.9 * np.maximum(market * 0.8, court * 0.5))
    S["gravel"] = np.maximum(S["gravel"], 0.2 + 0.8 * np.maximum(refugee * 0.6, gate * 0.6))
    S["planks"] = np.full_like(n_big, -2.0)

    core, verge, _ = P.road_field(list(R.ROADS.values()))
    S["road"] = 0.05 + 1.25 * core
    S["hard"] = np.maximum(S["hard"], 0.3 + 0.8 * verge * (1 - core))

    depth_dark = smoothstep(2.0, 9.0, d_ci)
    cs = 1.6 + 12 * cliff_f
    S["cliff_a"] = (cs - 1.0 * depth_dark).astype(np.float32)
    S["cliff_l"] = (cs - 1.0 - 4.0 * (1 - smoothstep(0.70, 0.85, n_big)) - 2 * depth_dark).astype(np.float32)
    S["cliff_d"] = (cs - 2.6 + 2.6 * depth_dark).astype(np.float32)
    cl_k = smoothstep(0.0, 0.30, cliff_f)
    for k in list(S):
        if not k.startswith("cliff_"):
            S[k] = (S[k] - 14.0 * cl_k).astype(np.float32)
    return S


def post(rgb, X, Y, P):
    f = P.fields
    sf = lambda a: P.sample_field(a.astype(np.float32), X, Y)
    d_co, d_ci = sf(f["d_co"]), sf(f["d_ci"])
    lum_n = P.sample_field(P.noise(14.0, "lumlow", octaves=2), X, Y)
    shade = 0.94 + 0.12 * lum_n
    shade *= 1 - 0.30 * (1 - smoothstep(0.0, 1.8, d_co))       # plateau edge darkens into the rim
    shade *= 1 - 0.30 * smoothstep(1.5, 9.0, d_ci)             # rock deepens away from the edge
    cf = sf(f["cf"])
    lip = smoothstep(0.0, 0.03, cf) * (1 - smoothstep(0.03, 0.14, cf))
    return rgb * shade[..., None] + 26 * lip[..., None]


def main():
    preview = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    P = Painter(R.W, R.H, TEX_DIR, seed=31)
    scores = build_scores(P)
    out = ROOT / R.BAKED_DIR
    written = P.bake(MATERIALS, scores, out, chunk_tiles=20, post=post)
    print(f"baked {len(written)} chunks -> {out}")
    if preview:
        sc = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 14
        full = Image.new("RGB", (R.W * TILE_PX, R.H * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        full.resize((R.W * sc, R.H * sc), Image.LANCZOS).save(preview)
        print("preview", preview)


if __name__ == "__main__":
    main()
