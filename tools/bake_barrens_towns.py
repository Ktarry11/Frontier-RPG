"""
Bake a Barrens town painting (Crossroads, Camp Taurajo, Ratchet) from the shared Barrens materials.

    python3 tools/bake_barrens_towns.py crossroads|camp_taurajo|ratchet|all [--preview out.png] [--scale 10]

Each town module (tools/handbuilt_<town>.py) supplies fields() (cliff/water/deck - the SAME functions
the tile grid is built from), BASE / PAINT (ground patches) and WATER ("sea" | "lake" | None).  Materials
are the cb_* set in assets/tiles/central_barrens/materials/ with the provisional-recolour fallback of
tools/bake_central_barrens.py, so real tiles dropped there improve every Barrens zone on the next bake.
Writes assets/tiles/<town>/baked/ground_<cx>_<cy>.jpg.
"""
import importlib
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

from tools.bake_central_barrens import build_material_dir, MATERIALS, post   # noqa: E402
from tools.terrain_painter import Painter, smoothstep, TILE_PX              # noqa: E402

TOWNS = {"crossroads": "tools.handbuilt_crossroads", "camp_taurajo": "tools.handbuilt_camp_taurajo",
         "ratchet": "tools.handbuilt_ratchet"}


def build_scores(P, M):
    gx, gy = P.gx, P.gy
    wp = P.warp("regions", amp_tiles=1.8, scale=10.0)
    n_big = P.noise(9.0, "big", octaves=3)
    n_big2 = P.noise(12.0, "big2", octaves=3)
    n_mid = P.noise(4.5, "mid", octaves=3)
    n_fine = P.noise(2.0, "fine", octaves=2)
    F = M.fields(gx, gy)
    wob = (P.noise(3.0, "shorewob", octaves=3) - 0.5) * 0.9
    cliff = F["cliff"].astype(np.float32)
    deck = F["deck"].astype(np.float32)
    cliff_f = np.clip(cliff * 0.5, -0.4, 0.6).astype(np.float32)
    sw = (F["shallow"] + wob).astype(np.float32)
    d_water_out = np.maximum(-sw, 0)
    d_water_in = np.maximum(sw, 0)
    d_cliff_out = ndi.gaussian_filter(np.maximum(-cliff, 0), 1.2)
    d_cliff_in = ndi.gaussian_filter(np.maximum(cliff, 0), 1.2)
    P.fields = dict(cliff=cliff, deck=deck, d_wo=d_water_out, d_wi=d_water_in,
                    d_co=d_cliff_out, d_ci=d_cliff_in, cf=cliff_f)

    off = np.float32(-9.0)
    S = {k: np.full_like(n_big, off, dtype=np.float32) for k in MATERIALS}

    # ---- base country: the town's own mix of earths / grasses
    for i, (mat, w) in enumerate(M.BASE.items()):
        n = P.noise(8.0 + 3 * i, f"base_{mat}", octaves=3)
        S[mat] = (0.12 + w * (0.45 + 0.9 * smoothstep(0.38, 0.72, n))).astype(np.float32)
    # ---- hand-placed patches
    for mat, blobs in M.PAINT.items():
        cur = np.maximum(S[mat], 0.05)
        for (cx, cy, rx, ry, st) in blobs:
            cur = np.maximum(cur, 0.10 + 1.15 * P.blob(cx, cy, rx, ry, 0.6, wp) * st)
        S[mat] = cur.astype(np.float32)
    # ---- paved plaza
    if hasattr(M, "paved"):
        pv = smoothstep(-0.3, 1.2, M.paved(gx, gy).astype(np.float32))
        S["hard"] = np.maximum(np.maximum(S["hard"], 0.05), 0.2 + 1.3 * pv).astype(np.float32)
        S["camp"] = np.maximum(S["camp"], 0.05).astype(np.float32)
    # ---- roads
    core, verge, _ = P.road_field(list(M.ROADS.values()))
    S["road"] = (0.05 + 1.3 * core).astype(np.float32)
    S["verge"] = (0.08 + 0.95 * verge * (1 - core)).astype(np.float32)
    S["hard"] = np.maximum(np.maximum(S["hard"], 0.05), 0.18 + 0.55 * verge * (1 - core)).astype(np.float32)

    # ---- water
    w_s = np.clip(sw, -4, 6)
    w_d = np.clip(F["deep"] + wob, -6, 6)
    base_s = (1.6 + 10 * w_s).astype(np.float32)
    base_d = (1.6 + 10 * w_s + 2.5 * w_d).astype(np.float32)
    if M.WATER == "sea":
        S["sea_s"], S["sea_d"] = base_s, base_d
        S["beach"] = (0.06 + 1.0 * (1 - smoothstep(1.0, 7.0, d_water_out)) * (0.6 + 0.4 * smoothstep(0.25, 0.6, n_fine))).astype(np.float32)
        S["wet"] = (0.06 + 1.1 * (1 - smoothstep(0.3, 1.7, d_water_out))).astype(np.float32)
    elif M.WATER == "lake":
        S["lake_s"], S["lake_d"] = base_s, base_d
        halo = (1 - smoothstep(2.0, 8.0, d_water_out)) * (0.55 + 0.45 * smoothstep(0.3, 0.6, n_mid))
        S["lush"] = (0.06 + 1.0 * halo).astype(np.float32)
        S["o_mud"] = (0.08 + 1.1 * (1 - smoothstep(0.4, 2.2, d_water_out)) * (0.75 + 0.25 * n_fine)).astype(np.float32)
    knock = np.maximum(smoothstep(0.0, 0.7, sw), smoothstep(-0.30, 0.10, deck))
    S["planks"] = (-2.0 + 14 * np.clip(deck + 0.15, 0, 0.6)).astype(np.float32)
    land = ("gold", "tall", "sparse", "cracked", "hard", "clay", "wash_g", "wash_m", "dust", "bone", "thorn",
            "camp", "lush", "o_mud", "beach", "wet", "salt", "road", "verge")
    for k in land:
        if S[k].max() > -8:
            S[k] = (S[k] - 14.0 * knock).astype(np.float32)
    on_deck = smoothstep(-0.30, 0.10, deck)
    for k in ("sea_s", "sea_d", "lake_s", "lake_d"):
        S[k] = (S[k] - 160.0 * on_deck).astype(np.float32)

    # ---- cliffs
    depth_dark = smoothstep(2.0, 9.0, d_cliff_in)
    cs = 1.6 + 12 * cliff_f
    S["cliff_a"] = (cs - 1.0 * depth_dark).astype(np.float32)
    S["cliff_c"] = (cs - 1.0 - 5.0 * (1 - smoothstep(0.72, 0.86, n_big2)) - 2 * depth_dark).astype(np.float32)
    S["cliff_d"] = (cs - 2.6 + 2.6 * depth_dark).astype(np.float32)
    cl_k = smoothstep(0.0, 0.30, cliff_f)
    wk = smoothstep(0.0, 1.2, cliff)
    for k in list(S):
        if not k.startswith("cliff_") and S[k].max() > -8:
            S[k] = (S[k] - 14.0 * cl_k - (40.0 * wk if k.endswith(("_s", "_d")) else 0.0)).astype(np.float32)
    return S


def bake(key, mat_dir, preview=None, sc=10):
    M = importlib.import_module(TOWNS[key])
    P = Painter(M.W, M.H, mat_dir, seed=53)
    scores = build_scores(P, M)
    out = ROOT / M.BAKED_DIR
    written = P.bake(MATERIALS, scores, out, chunk_tiles=20, post=post)
    print(f"{key}: baked {len(written)} chunks -> {out}")
    if preview:
        full = Image.new("RGB", (M.W * TILE_PX, M.H * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        full.resize((M.W * sc, M.H * sc), Image.LANCZOS).save(preview)
        print("preview", preview)


def main():
    which = [a for a in sys.argv[1:] if a in TOWNS or a == "all"]
    keys = list(TOWNS) if (not which or which[0] == "all") else which
    preview = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    sc = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 10
    mat_dir, provisional = build_material_dir()
    if provisional:
        print(f"PROVISIONAL textures for {len(provisional)} materials")
    for k in keys:
        bake(k, mat_dir, preview.replace(".png", f"_{k}.png") if preview else None, sc)


if __name__ == "__main__":
    main()
