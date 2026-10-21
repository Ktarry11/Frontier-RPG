"""
Bake the Northern Barrens painting (ground + water + cliffs) from seamless materials.

    python3 tools/bake_northern_barrens.py [--preview out.png] [--scale 4]

Shares the Barrens material set (assets/tiles/central_barrens/materials/cb_*.png, see
claude/barrens_tile_prompts.md) and the provisional-recolour fallback with the Central baker, so
real tiles dropped there improve ALL the Barrens zones.  Landforms come from
tools/handbuilt_northern_barrens.fields() - the SAME analytic functions the tile grid is built
from - so painting and collision agree.  Writes assets/tiles/northern_barrens/baked/.

Painted character (no collision): braided fen = lush grass + black mud islets; Sludge Fen = oil-black
water and stained ground; harpy nest bowl = bone earth; Dry Hills = cracked clay; sea coast = beach.
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

from tools import handbuilt_northern_barrens as NB                      # noqa: E402
from tools.bake_central_barrens import build_material_dir, MATERIALS, post as _post  # noqa: E402
from tools.terrain_painter import Painter, smoothstep, TILE_PX           # noqa: E402

OIL_TINT = np.array([16, 18, 10], np.float32)


def build_scores(P):
    S = {}
    gx, gy = P.gx, P.gy
    wp = P.warp("regions", amp_tiles=2.6, scale=13.0)
    n_big = P.noise(11.0, "big", octaves=3)
    n_big2 = P.noise(14.0, "big2", octaves=3)
    n_mid = P.noise(5.0, "mid", octaves=3)
    n_fine = P.noise(2.0, "fine", octaves=2)

    F = NB.fields(gx, gy)
    wob = (P.noise(3.0, "shorewob", octaves=3) - 0.5) * 0.9
    sh_ext, dp_ext = F["shallow"], F["deep"]
    cliff = F["cliff"].astype(np.float32)
    deck = F["deck"].astype(np.float32)
    cliff_f = np.clip(cliff * 0.5, -0.4, 0.6).astype(np.float32)
    sw = (sh_ext + wob).astype(np.float32)
    d_water_out = np.maximum(-sw, 0)
    d_water_in = np.maximum(sw, 0)
    d_cliff_out = ndi.gaussian_filter(np.maximum(-cliff, 0), 1.2)
    d_cliff_in = ndi.gaussian_filter(np.maximum(cliff, 0), 1.2)
    # oil-stain field for the Sludge Fen (painted tint applied in post)
    oil = np.maximum.reduce([P.blob(cx, cy, rx, ry, 0.8, wp) for (cx, cy, rx, ry) in NB.OIL_STAIN])
    oil_ext = np.maximum.reduce([NB.blob(gx, gy, cx, cy, rx, ry, rot, ph)
                                 for (cx, cy, rx, ry, rot, ph) in NB.LAKES["sludge"]]) + wob
    oil_w = smoothstep(-0.5, 0.9, oil_ext)                 # the oil pools themselves (water + wet shore)
    P.fields = dict(cliff=cliff, deck=deck, d_wo=d_water_out, d_wi=d_water_in,
                    d_co=d_cliff_out, d_ci=d_cliff_in, cf=cliff_f, oil=oil.astype(np.float32),
                    oil_w=oil_w.astype(np.float32))
    sea_ext = np.minimum(gx - NB.coast_x(gy), (gy - 78.0) * 2.0)
    sea_side = sea_ext > -14.0                    # within reach of the east sea; every other water is a fen / oasis / oil pool

    # -------- base country: greener and wetter than Central, with sparse patches
    S["gold"] = np.full_like(n_big, 0.50)
    S["tall"] = 0.20 + 0.75 * smoothstep(0.58, 0.80, n_big)
    S["sparse"] = 0.26 + 0.70 * smoothstep(0.55, 0.80, n_mid) * (0.55 + 0.45 * smoothstep(0.3, 0.6, n_big2))
    dry_hills = P.blob(38, 98, 36, 74, 0.8, wp)
    dry_south = np.maximum(P.blob(70, 215, 50, 30, 0.8, wp), P.blob(205, 112, 30, 24, 0.8, wp))
    S["cracked"] = 0.18 + 0.80 * np.maximum(smoothstep(0.58, 0.78, n_big2) * 0.9 * (0.3 + 0.7 * dry_hills),
                                             dry_hills * 0.65 * smoothstep(0.42, 0.62, n_mid))
    S["clay"] = 0.05 + 0.95 * np.maximum.reduce([
        P.blob(26, 120, 14, 22, 0.7, wp) * smoothstep(0.35, 0.6, n_mid),
        P.blob(50, 60, 14, 12, 0.7, wp) * 0.7 * smoothstep(0.35, 0.6, n_mid),
        P.blob(236, 158, 12, 10, 0.7, wp) * smoothstep(0.4, 0.6, n_mid),
        P.blob(170, 232, 10, 8, 0.7, wp) * smoothstep(0.4, 0.6, n_mid)])
    mesa_skirt = 1 - smoothstep(0.8, 6.0, d_cliff_out)
    S["hard"] = 0.10 + 0.90 * np.maximum.reduce([
        mesa_skirt * (0.35 + 0.65 * smoothstep(0.35, 0.6, n_mid)),
        P.blob(150, 31, 24, 7, 0.8, wp) * 0.7, P.blob(145, 65, 16, 12, 0.8, wp) * 0.6])
    S["dust"] = 0.08 + 0.90 * np.maximum.reduce([
        dry_south * smoothstep(0.35, 0.6, n_mid) * 0.8,
        P.blob(256, 130, 16, 12, 0.8, wp) * smoothstep(0.3, 0.6, n_mid),
        smoothstep(0.78, 0.9, n_fine) * dry_hills * 0.6])
    nest = NB.NEST_BOWL
    S["bone"] = 0.08 + 0.92 * np.maximum.reduce([
        P.blob(nest[0], nest[1], nest[2], nest[3], 0.8, wp) * (0.6 + 0.4 * smoothstep(0.3, 0.6, n_fine)),
        P.blob(50, 76, 6, 5, 0.7, wp) * 0.7, P.blob(126, 214, 8, 5, 0.7, wp) * 0.6])
    S["thorn"] = 0.08 + 0.92 * np.maximum.reduce([
        P.blob(cx, cy, rx, ry, 0.8, wp) * 0.9 for (cx, cy, rx, ry) in NB.OIL_STAIN] +
        [P.blob(30, 52, 14, 8, 0.8, wp) * smoothstep(0.4, 0.6, n_mid)])
    camp_fields = [P.blob(cx, cy, rx, ry, 0.7, wp) for (cx, cy, rx, ry) in NB.CAMP_PATCHES.values()]
    S["camp"] = 0.08 + 0.95 * np.maximum.reduce(camp_fields)
    S["salt"] = 0.05 + 0.95 * np.maximum.reduce(
        [P.blob(cx, cy, rx, ry, 0.7, wp) * smoothstep(0.30, 0.55, n_mid) for (cx, cy, rx, ry) in NB.SALT_PANS])

    # -------- dry washes (painted only)
    wd = NB.wash_dist(gx, gy).astype(np.float32)
    wd_in = np.clip(wd, -2, 2.5)
    S["wash_g"] = 0.05 + 1.3 * smoothstep(-0.4, 0.6, wd_in)
    S["wash_m"] = 0.04 + 1.3 * smoothstep(0.8, 1.7, wd_in) * (0.6 + 0.4 * smoothstep(0.3, 0.6, n_fine))

    # -------- fen + oasis: lush halos, black mud islets round the waterways
    lake_out = np.where(sea_side, 99.0, d_water_out)
    halo = (1 - smoothstep(2.0, 10.0, lake_out)) * (0.55 + 0.45 * smoothstep(0.3, 0.6, n_mid))
    fen = P.blob(104, 132, 46, 42, 0.8, wp)
    fen_lush = np.clip(fen, 0, 1) * (0.6 + 0.4 * smoothstep(0.35, 0.65, n_big2))
    S["lush"] = 0.06 + 1.0 * np.maximum(halo, 0.85 * fen_lush)
    S["tall"] = np.maximum(S["tall"], 0.2 + 0.8 * halo * smoothstep(0.2, 0.5, n_fine))
    # no lush grass round the oil: the basin is stained, bare and black
    S["lush"] = 0.06 + (S["lush"] - 0.06) * (1 - 0.92 * np.clip(1.8 * oil, 0, 1))
    S["tall"] = 0.18 + (S["tall"] - 0.18) * (1 - 0.8 * np.clip(1.8 * oil, 0, 1))
    islet_mud = np.clip(fen, 0, 1) * smoothstep(0.46, 0.66, n_mid) * 0.9
    S["o_mud"] = 0.08 + 1.1 * np.maximum((1 - smoothstep(0.4, 2.2, lake_out)) * (0.75 + 0.25 * n_fine), islet_mud)
    # the Stagnant Oasis shore is scummy: more mud, less grass
    S["o_mud"] = np.maximum(S["o_mud"], 0.08 + 0.9 * P.blob(204, 172, 14, 10, 0.8, wp) * smoothstep(0.3, 0.55, n_mid))

    # -------- coast: pale beach sand, wet sand at the surf
    sea_out = np.where(sea_side, d_water_out, 99.0)
    S["beach"] = 0.06 + 1.0 * (1 - smoothstep(1.0, 9.0, sea_out)) * (0.6 + 0.4 * smoothstep(0.25, 0.6, n_fine))
    S["wet"] = 0.06 + 1.1 * (1 - smoothstep(0.3, 1.7, sea_out))

    # -------- roads
    core, verge, _ = P.road_field(list(NB.ROADS.values()))
    S["road"] = 0.05 + 1.3 * core
    S["verge"] = 0.08 + 0.95 * verge * (1 - core)
    S["hard"] = np.maximum(S["hard"], 0.18 + 0.55 * verge * (1 - core))

    # -------- water (continuous scores -> anti-aliased shorelines)
    w_s = np.clip(sh_ext + wob, -4, 6)
    w_d = np.clip(dp_ext + wob, -6, 6)
    base_s = (1.6 + 10 * w_s).astype(np.float32)
    base_d = (1.6 + 10 * w_s + 2.5 * w_d).astype(np.float32)
    off = np.float32(-40.0)
    S["sea_s"] = np.where(sea_side, base_s, off).astype(np.float32)
    S["sea_d"] = np.where(sea_side, base_d, off).astype(np.float32)
    S["lake_s"] = np.where(sea_side, off, base_s).astype(np.float32)
    S["lake_d"] = np.where(sea_side, off, base_d).astype(np.float32)
    knock = smoothstep(0.0, 0.7, sw)
    S["planks"] = np.full_like(n_big, -9.0, dtype=np.float32)
    for k in ("gold", "tall", "sparse", "cracked", "hard", "clay", "wash_g", "wash_m", "dust", "bone", "thorn",
              "camp", "lush", "o_mud", "beach", "wet", "salt", "road", "verge"):
        S[k] = (S[k] - 14.0 * knock).astype(np.float32)

    # -------- cliffs (continuous): sandstone bands, dark depths, chalk streaks
    depth_dark = smoothstep(2.0, 9.0, d_cliff_in)
    cs = 1.6 + 12 * cliff_f
    S["cliff_a"] = (cs - 1.0 * depth_dark).astype(np.float32)
    S["cliff_c"] = (cs - 1.0 - 5.0 * (1 - smoothstep(0.72, 0.86, n_big2)) - 2 * depth_dark).astype(np.float32)
    S["cliff_d"] = (cs - 2.6 + 2.6 * depth_dark).astype(np.float32)
    cl_k = smoothstep(0.0, 0.30, cliff_f)
    wk = smoothstep(0.0, 1.2, cliff)
    for k in list(S):
        if not k.startswith("cliff_"):
            S[k] = (S[k] - 14.0 * cl_k - (40.0 * wk if k.endswith(("_s", "_d")) else 0.0)).astype(np.float32)
    return S


def post(rgb, X, Y, P):
    rgb = _post(rgb, X, Y, P)
    oil = P.sample_field(P.fields["oil"], X, Y)
    oil_w = P.sample_field(P.fields["oil_w"], X, Y)
    # oil pools: black, glossy; the stained ground round them: darkened
    m = np.maximum(oil_w, 0.30 * np.clip(oil, 0, 1))
    rgb = rgb * (1 - 0.93 * m[..., None]) + OIL_TINT * (0.93 * m[..., None])
    return rgb


def main():
    preview = None
    if "--preview" in sys.argv:
        preview = sys.argv[sys.argv.index("--preview") + 1]
    mat_dir, provisional = build_material_dir()
    if provisional:
        print(f"PROVISIONAL textures for {len(provisional)} materials")
    P = Painter(NB.W, NB.H, mat_dir, seed=53)
    scores = build_scores(P)
    out = ROOT / NB.BAKED_DIR
    written = P.bake(MATERIALS, scores, out, chunk_tiles=20, post=post)
    print(f"baked {len(written)} chunks -> {out}")
    if preview:
        sc = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 4
        full = Image.new("RGB", (NB.W * TILE_PX, NB.H * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        full.resize((NB.W * sc, NB.H * sc), Image.LANCZOS).save(preview)
        print("preview", preview)


if __name__ == "__main__":
    main()
