"""
Bake the Southern Barrens painting (ground + water + cliffs) from seamless materials.

    python3 tools/bake_southern_barrens.py [--preview out.png] [--scale 4]

Shares the Barrens material set (assets/tiles/central_barrens/materials/cb_*.png, see
claude/barrens_tile_prompts.md) and the provisional-recolour fallback with the Central baker, so
real tiles dropped there improve BOTH zones.  Landforms come from
tools/handbuilt_southern_barrens.fields() - the SAME analytic functions the tile grid is built
from - so painting and collision agree.  Writes assets/tiles/southern_barrens/baked/.
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

from tools import handbuilt_southern_barrens as SB                      # noqa: E402
from tools.bake_central_barrens import build_material_dir, MATERIALS, post  # noqa: E402
from tools.terrain_painter import Painter, smoothstep, TILE_PX           # noqa: E402


def build_scores(P):
    S = {}
    gx, gy = P.gx, P.gy
    wp = P.warp("regions", amp_tiles=2.6, scale=13.0)
    n_big = P.noise(11.0, "big", octaves=3)
    n_big2 = P.noise(14.0, "big2", octaves=3)
    n_mid = P.noise(5.0, "mid", octaves=3)
    n_fine = P.noise(2.0, "fine", octaves=2)

    F = SB.fields(gx, gy)
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
    P.fields = dict(cliff=cliff, deck=deck, d_wo=d_water_out, d_wi=d_water_in,
                    d_co=d_cliff_out, d_ci=d_cliff_in, cf=cliff_f)

    # -------- base country: drier than Central - sparse + cracked earth dominate
    S["gold"] = np.full_like(n_big, 0.40)
    S["tall"] = 0.10 + 0.70 * smoothstep(0.62, 0.82, n_big)
    S["sparse"] = 0.30 + 0.70 * smoothstep(0.50, 0.78, n_mid) * (0.55 + 0.45 * smoothstep(0.3, 0.6, n_big2))
    giants = P.blob(140, 188, 62, 34, 0.8, wp)
    south_dry = np.maximum(giants, P.blob(60, 205, 50, 24, 0.8, wp))
    S["cracked"] = 0.20 + 0.80 * np.maximum(smoothstep(0.55, 0.75, n_big2) * 0.9 * (0.35 + 0.65 * south_dry),
                                             south_dry * 0.6 * smoothstep(0.40, 0.62, n_mid))
    S["clay"] = 0.05 + 0.95 * np.maximum.reduce([
        P.blob(60, 130, 10, 6, 0.7, wp) * smoothstep(0.35, 0.6, n_mid),
        P.blob(190, 136, 12, 5, 0.7, wp) * smoothstep(0.35, 0.6, n_mid),
        P.blob(34, 64, 20, 16, 0.7, wp) * 0.55 * smoothstep(0.35, 0.6, n_mid),
        P.blob(222, 212, 18, 14, 0.7, wp) * 0.8])
    mesa_skirt = 1 - smoothstep(0.8, 6.0, d_cliff_out)
    keep_floor = P.blob(88, 33, 24, 14, 0.8, wp)
    S["hard"] = 0.10 + 0.90 * np.maximum.reduce([mesa_skirt * (0.35 + 0.65 * smoothstep(0.35, 0.6, n_mid)),
                                                  keep_floor * 0.95, P.blob(34, 64, 22, 18, 0.8, wp) * 0.55])
    S["dust"] = 0.08 + 0.90 * np.maximum.reduce([
        P.blob(215, 150, 24, 20, 0.8, wp) * smoothstep(0.35, 0.6, n_mid),
        P.blob(20, 215, 18, 12, 0.8, wp) * smoothstep(0.35, 0.6, n_mid),
        P.blob(180, 50, 22, 14, 0.8, wp) * smoothstep(0.35, 0.6, n_mid),
        smoothstep(0.78, 0.9, n_fine) * south_dry * 0.6])
    S["bone"] = 0.08 + 0.92 * np.maximum.reduce([
        P.blob(140, 190, 40, 18, 0.8, wp) * (0.55 + 0.45 * smoothstep(0.3, 0.6, n_fine)),
        P.blob(110, 130, 16, 6, 0.7, wp) * 0.7,
        P.blob(222, 212, 12, 9, 0.7, wp) * 0.7, P.blob(172, 64, 8, 5, 0.7, wp)])
    S["thorn"] = 0.08 + 0.92 * np.maximum.reduce([
        P.blob(58, 168, 24, 20, 0.8, wp), P.blob(52, 104, 26, 14, 0.8, wp) * smoothstep(0.4, 0.6, n_mid),
        P.blob(46, 106, 10, 8, 0.8, wp)])
    camp_fields = [P.blob(cx, cy, rx, ry, 0.7, wp) for (cx, cy, rx, ry) in SB.CAMP_PATCHES.values()]
    S["camp"] = 0.08 + 0.95 * np.maximum.reduce(camp_fields)
    S["salt"] = 0.05 + 0.95 * np.maximum.reduce(
        [P.blob(cx, cy, rx, ry, 0.7, wp) * smoothstep(0.30, 0.55, n_mid) for (cx, cy, rx, ry) in SB.SALT_PANS])

    # -------- dry riverbeds (painted only): the Rift floor is a long gravel bed
    wd = SB.wash_dist(gx, gy).astype(np.float32)
    wd_in = np.clip(wd, -2, 2.5)
    S["wash_g"] = 0.05 + 1.3 * smoothstep(-0.4, 0.6, wd_in)
    S["wash_m"] = 0.04 + 1.3 * smoothstep(0.8, 1.7, wd_in) * (0.6 + 0.4 * smoothstep(0.3, 0.6, n_fine))

    # -------- ponds: lush grass halo + dark wet mud rim
    halo = (1 - smoothstep(2.0, 9.0, d_water_out)) * (0.55 + 0.45 * smoothstep(0.3, 0.6, n_mid))
    S["lush"] = 0.06 + 1.0 * halo
    S["tall"] = np.maximum(S["tall"], 0.2 + 0.8 * halo * smoothstep(0.2, 0.5, n_fine))
    S["o_mud"] = 0.08 + 1.1 * (1 - smoothstep(0.4, 2.2, d_water_out)) * (0.75 + 0.25 * n_fine)
    S["beach"] = np.full_like(n_big, -9.0)
    S["wet"] = np.full_like(n_big, -9.0)

    # -------- roads
    core, verge, _ = P.road_field(list(SB.ROADS.values()))
    S["road"] = 0.05 + 1.3 * core
    S["verge"] = 0.08 + 0.95 * verge * (1 - core)
    S["hard"] = np.maximum(S["hard"], 0.18 + 0.55 * verge * (1 - core))

    # -------- water (continuous scores -> anti-aliased shorelines); lake materials only
    w_s = np.clip(sh_ext + wob, -4, 6)
    w_d = np.clip(dp_ext + wob, -6, 6)
    base_s = (1.6 + 10 * w_s).astype(np.float32)
    base_d = (1.6 + 10 * w_s + 2.5 * w_d).astype(np.float32)
    off = np.float32(-40.0)
    S["sea_s"] = np.full_like(n_big, off, dtype=np.float32)
    S["sea_d"] = np.full_like(n_big, off, dtype=np.float32)
    S["lake_s"] = base_s
    S["lake_d"] = base_d
    S["planks"] = np.full_like(n_big, -9.0, dtype=np.float32)
    knock = smoothstep(0.0, 0.7, sw)
    for k in ("gold", "tall", "sparse", "cracked", "hard", "clay", "wash_g", "wash_m", "dust", "bone", "thorn",
              "camp", "lush", "o_mud", "salt", "road", "verge"):
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


def main():
    preview = None
    if "--preview" in sys.argv:
        preview = sys.argv[sys.argv.index("--preview") + 1]
    mat_dir, provisional = build_material_dir()
    if provisional:
        print(f"PROVISIONAL textures for {len(provisional)} materials")
    P = Painter(SB.W, SB.H, mat_dir, seed=47)
    scores = build_scores(P)
    out = ROOT / SB.BAKED_DIR
    written = P.bake(MATERIALS, scores, out, chunk_tiles=20, post=post)
    print(f"baked {len(written)} chunks -> {out}")
    if preview:
        sc = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 4
        full = Image.new("RGB", (SB.W * TILE_PX, SB.H * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        full.resize((SB.W * sc, SB.H * sc), Image.LANCZOS).save(preview)
        print("preview", preview)


if __name__ == "__main__":
    main()
