"""
Bake a hand-built Silverpine outdoor zone painting (Silverpine North, Silverpine South) from the seamless Silverpine materials in
assets/tiles/silverpine/materials (sp_*.png).

    python3 tools/bake_silverpine.py silverpine_north|silverpine_south|all [--preview out.png] [--scale 6]

Each zone module (tools/handbuilt_<zone>.py) supplies fields() (cliff / shallow / deep / deck - the SAME functions the tile grid is
built from), BASE (material -> weight of the noise patches), PAINT (material -> [(cx, cy, rx, ry, strength)]), optionally paved(),
COBBLE blobs, sea_field() (water that is sea, not spring/lake).  Writes assets/tiles/<zone>/baked/ground_<cx>_<cy>.jpg.
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

from tools.terrain_painter import Painter, smoothstep, TILE_PX         # noqa: E402

TEX_DIR = ROOT / "assets/tiles/silverpine/materials"
ZONES = {"silverpine_north": "tools.handbuilt_silverpine_north", "silverpine_south": "tools.handbuilt_silverpine_south",
         "sepulcher": "tools.handbuilt_sepulcher"}

MATERIALS = {
    "pine":    ("sp_pine_floor", None, 1.0),
    "fern":    ("sp_fern_floor", None, 1.0),
    "mulch":   ("sp_needle_mulch", None, 1.0),
    "grass":   ("sp_cold_grass", None, 1.0),
    "meadow":  ("sp_highland_meadow", None, 1.0),
    "rocky":   ("sp_rocky_ground", "sp_moss_rock", 1.0),
    "earth":   ("sp_cemetery_earth", None, 1.0),
    "field":   ("sp_farm_field", None, 1.0),
    "cursed":  ("sp_cursed_ground", None, 1.0),
    "bog":     ("sp_bog_mud", "sp_peat", 1.0),
    "web":     ("sp_web_ground", None, 1.0),
    "den":     ("sp_worgen_den", None, 1.0),
    "cobble":  ("sp_old_cobble", "sp_flagstone", 1.0),
    "gravel":  ("sp_gravel", None, 1.0),
    "road":    ("sp_road_centre", None, 1.0),
    "verge":   ("sp_road_edge", None, 1.0),
    "planks":  ("sp_wood_planks", "sp_pier_planks", 1.0),
    "shore":   ("sp_shingle", "sp_wet_shingle", 1.0),
    "marsh":   ("sp_marsh_water", None, 1.0),
    "pool_s":  ("sp_pool_shallow_flat", None, 1.0),
    "pool_d":  ("sp_pool_deep_flat", None, 1.0),
    "sea_s":   ("sp_sea_shallow_flat", None, 1.0),
    "sea_d":   ("sp_sea_deep_flat", None, 1.0),
    "river_s": ("sp_river_shallow_flat", None, 1.0),
    "cliff_a": ("sp_cliff_a", "sp_cliff_b", 1.0),
    "cliff_d": ("sp_rock_wall", None, 1.0),
}
LAND = ("pine", "fern", "mulch", "grass", "meadow", "rocky", "earth", "field", "cursed", "bog", "web", "den", "cobble", "gravel",
        "road", "verge", "planks", "shore", "marsh")


def build_scores(P, M):
    S = {}
    gx, gy = P.gx, P.gy
    wp = P.warp("regions", amp_tiles=1.8, scale=10.0)
    n_big = P.noise(9.0, "big", octaves=3)
    n_mid = P.noise(4.5, "mid", octaves=3)
    n_fine = P.noise(2.0, "fine", octaves=2)

    f = M.fields(gx, gy)
    cliff = f["cliff"].astype(np.float32)
    water = f["shallow"].astype(np.float32)                         # tile distance inside water (>0 in water)
    deep = f["deep"].astype(np.float32)
    deck = f["deck"].astype(np.float32)
    cliff_f = np.clip(cliff * 0.5, -0.4, 0.6).astype(np.float32)
    d_co = ndi.gaussian_filter(np.maximum(-cliff, 0), 1.2)
    d_ci = ndi.gaussian_filter(np.maximum(cliff, 0), 1.2)
    sea = M.sea_field(gx, gy).astype(np.float32) if hasattr(M, "sea_field") else np.full_like(cliff, -99.0)
    P.fields = dict(cliff=cliff, d_co=d_co, d_ci=d_ci, cf=cliff_f, water=water, deep=deep, sea=sea)

    # base: cold pine-needle floor with fern, mulch and rocky patches
    base = getattr(M, "BASE", {"pine": 0.55, "fern": 0.3, "mulch": 0.3, "rocky": 0.12})
    S["pine"] = np.full_like(n_big, 0.55)
    S["fern"] = 0.10 + 0.85 * base.get("fern", 0.3) / 0.3 * smoothstep(0.52, 0.78, n_big) * 0.9
    S["mulch"] = 0.05 + 0.60 * base.get("mulch", 0.3) / 0.3 * smoothstep(0.66, 0.88, n_mid) * (0.6 + 0.4 * n_fine)
    S["rocky"] = 0.05 + 0.40 * base.get("rocky", 0.12) / 0.12 * smoothstep(0.66, 0.85, n_mid)
    near_rim = smoothstep(-6.0, -1.0, cliff)
    S["rocky"] = np.maximum(S["rocky"], 0.2 + 0.95 * near_rim)
    S["mulch"] = np.maximum(S["mulch"], 0.2 + 0.6 * near_rim * smoothstep(0.45, 0.7, n_mid))
    for k in LAND:
        S.setdefault(k, np.full_like(n_big, -9.0))

    # hand-placed districts
    for mat, blobs in getattr(M, "PAINT", {}).items():
        cur = np.maximum(S[mat], 0.05)
        for (cx, cy, rx, ry, st) in blobs:
            b = P.blob(cx, cy, rx, ry, 0.6, wp)
            if mat in ("web", "field", "bog", "cursed", "earth"):
                b = b * (0.6 + 0.4 * smoothstep(0.3, 0.6, n_mid))
            cur = np.maximum(cur, 0.10 + 1.25 * b * st)
        S[mat] = cur.astype(np.float32)
        if mat in ("web", "cursed", "den"):
            S["rocky"] = np.maximum(S["rocky"], 0.15)
    if hasattr(M, "paved"):
        pv = smoothstep(-0.3, 1.2, M.paved(gx, gy).astype(np.float32))
        S["cobble"] = np.maximum(np.maximum(S["cobble"], 0.05), 0.12 + 1.35 * pv).astype(np.float32)
    for (cx, cy, rx, ry, st) in getattr(M, "COBBLE", []):
        S["cobble"] = np.maximum(np.maximum(S["cobble"], 0.05), 0.12 + 1.35 * P.blob(cx, cy, rx, ry, 0.6, wp) * st)

    # roads
    core, verge, _ = P.road_field(list(M.ROADS.values()))
    S["road"] = (0.05 + 1.3 * core).astype(np.float32)
    S["verge"] = np.maximum(0.05, 0.25 + 0.9 * verge * (1 - core)).astype(np.float32)

    # water: crisp, driven by the same field as the tile grid; shingle / mud bank around it
    wet = (water > 0.0).astype(np.float32)
    is_sea = (sea >= water - 0.6).astype(np.float32)
    bank = smoothstep(-1.4, 0.0, water)
    S["shore"] = np.maximum(S["shore"], 0.05 + 1.35 * smoothstep(-1.0, 0.05, water) * (0.35 + 0.65 * is_sea)).astype(np.float32)
    S["bog"] = np.maximum(S["bog"], 0.05 + 0.7 * bank * (1 - is_sea) * (0.5 + 0.5 * n_mid)).astype(np.float32)
    sh = np.clip(1.6 * water, -9.0, 9.0).astype(np.float32)
    S["pool_s"] = np.where(is_sea > 0.5, -9.0, sh).astype(np.float32)
    S["sea_s"] = np.where(is_sea > 0.5, sh, -9.0).astype(np.float32)
    dp = np.clip(1.8 * deep, -9.0, 9.0).astype(np.float32)
    S["pool_d"] = np.where(is_sea > 0.5, -9.0, dp - 0.4).astype(np.float32)
    S["sea_d"] = np.where(is_sea > 0.5, dp - 0.4, -9.0).astype(np.float32)
    for k in LAND:
        S[k] = (S[k] - 12.0 * wet).astype(np.float32)

    # decks (bridges) over water
    if deck.max() > 0:
        on = smoothstep(-0.30, 0.10, deck)
        S["planks"] = np.maximum(S["planks"], -2.0 + 14 * np.clip(deck + 0.15, 0, 0.6)).astype(np.float32)
        for k in ("pool_s", "pool_d", "sea_s", "sea_d"):
            S[k] = (S[k] - 60.0 * on).astype(np.float32)

    # cliffs
    depth_dark = smoothstep(2.0, 9.0, d_ci)
    cs = 1.6 + 12 * cliff_f
    S["cliff_a"] = (cs - 1.0 * depth_dark).astype(np.float32)
    S["cliff_d"] = (cs - 2.4 + 2.8 * depth_dark).astype(np.float32)
    cl_k = smoothstep(0.0, 0.30, cliff_f)
    for k in list(S):
        if not k.startswith("cliff_"):
            S[k] = (S[k] - 14.0 * cl_k).astype(np.float32)
    for k in MATERIALS:
        S.setdefault(k, np.full_like(S["pine"], -9.0))
    return S


def post(rgb, X, Y, P):
    f = P.fields
    sf = lambda a: P.sample_field(a.astype(np.float32), X, Y)
    d_co, d_ci = sf(f["d_co"]), sf(f["d_ci"])
    lum_n = P.sample_field(P.noise(14.0, "lumlow", octaves=2), X, Y)
    shade = 0.92 + 0.12 * lum_n
    shade *= 1 - 0.30 * (1 - smoothstep(0.0, 1.8, d_co))
    shade *= 1 - 0.32 * smoothstep(1.5, 9.0, d_ci)
    cf = sf(f["cf"])
    lip = smoothstep(0.0, 0.03, cf) * (1 - smoothstep(0.03, 0.14, cf))
    wd = sf(f["water"])
    depth = smoothstep(0.4, 5.5, wd)
    rgb = rgb * (1 - 0.55 * depth[..., None]) + np.array([6.0, 20.0, 30.0], np.float32) * 0.55 * depth[..., None]
    out = rgb * shade[..., None] + 20 * lip[..., None]
    out = out * np.array([0.95, 0.99, 1.03], np.float32)               # Silverpine's cold pine shade
    return out


def bake(key, preview=None, sc=6):
    M = importlib.import_module(ZONES[key])
    P = Painter(M.W, M.H, TEX_DIR, seed=getattr(M, "SEED", 71))
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
    which = [a for a in sys.argv[1:] if a in ZONES or a == "all"]
    keys = list(ZONES) if (not which or which[0] == "all") else which
    preview = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    sc = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 6
    for k in keys:
        if k == "silverpine_south" and not Path(ROOT / "tools/handbuilt_silverpine_south.py").exists():
            continue
        bake(k, preview.replace(".png", f"_{k}.png") if preview else None, sc)


if __name__ == "__main__":
    main()
