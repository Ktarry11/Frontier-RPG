"""
Bake a hand-built Tirisfal zone painting (Western Tirisfal, Eastern Tirisfal, Brill) from the seamless Tirisfal materials in
assets/tiles/tirisfal/materials.

    python3 tools/bake_tirisfal.py western_tirisfal|eastern_tirisfal|brill|all [--preview out.png] [--scale 8]

Each zone module (tools/handbuilt_<zone>.py) supplies fields() (cliff / shallow / deep / deck - the SAME functions the tile grid is
built from), BASE (material -> weight of the noise patches), PAINT (material -> [(cx, cy, rx, ry, strength)]) and optionally paved().
Writes assets/tiles/<zone>/baked/ground_<cx>_<cy>.jpg.
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

from tools.bake_deathknell import MATERIALS as _DK_MATERIALS          # noqa: E402
from tools.terrain_painter import Painter, smoothstep, TILE_PX         # noqa: E402

TEX_DIR = ROOT / "assets/tiles/tirisfal/materials"
ZONES = {"western_tirisfal": "tools.handbuilt_western_tirisfal", "eastern_tirisfal": "tools.handbuilt_eastern_tirisfal",
         "brill": "tools.handbuilt_brill"}

MATERIALS = dict(_DK_MATERIALS)
MATERIALS.update({
    "blight":   ("tf_blight_soil", "tf_plague_ground", 1.0),
    "scourge":  ("tf_scourge_earth", "tf_bone_dirt", 1.0),
    "flag":     ("tf_flagstone", "tf_old_cobble", 1.0),
    "planks":   ("tf_wood_planks", "tf_rotten_planks", 1.0),
    "ash":      ("tf_ash_ground", None, 1.0),
    "mud":      ("tf_mud_puddles", "tf_shore_mud", 1.0),
    "river_s":  ("tf_river_shallow", None, 1.0),
    "river_d":  ("tf_river_deep", None, 1.0),
})
LAND = ("meadow", "mist", "litter", "rocky", "earth", "gravel", "cobble", "web", "field", "burned", "marsh", "shore", "road",
        "verge", "blight", "scourge", "flag", "planks", "ash", "mud")


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
    deck = f["deck"].astype(np.float32)
    cliff_f = np.clip(cliff * 0.5, -0.4, 0.6).astype(np.float32)
    d_co = ndi.gaussian_filter(np.maximum(-cliff, 0), 1.2)
    d_ci = ndi.gaussian_filter(np.maximum(cliff, 0), 1.2)
    P.fields = dict(cliff=cliff, d_co=d_co, d_ci=d_ci, cf=cliff_f, water=water)

    # base: sallow meadow with mist-grass, leaf-litter and rocky patches
    S["meadow"] = np.full_like(n_big, 0.55)
    base = getattr(M, "BASE", {"meadow": 0.55, "mist": 0.30, "litter": 0.25, "rocky": 0.15})
    S["mist"] = 0.20 + 0.70 * base.get("mist", 0.3) / 0.3 * smoothstep(0.58, 0.82, n_big) * 0.9
    S["litter"] = 0.10 + 0.75 * base.get("litter", 0.25) / 0.25 * smoothstep(0.62, 0.84, n_mid) * (0.6 + 0.4 * n_fine)
    S["rocky"] = 0.05 + 0.40 * base.get("rocky", 0.15) / 0.15 * smoothstep(0.66, 0.85, n_mid)
    near_rim = smoothstep(-6.0, -1.0, cliff)
    S["rocky"] = np.maximum(S["rocky"], 0.2 + 0.95 * near_rim)
    S["litter"] = np.maximum(S["litter"], 0.2 + 0.6 * near_rim * smoothstep(0.45, 0.7, n_mid))
    for k in LAND:
        S.setdefault(k, np.full_like(n_big, -9.0))

    # hand-placed districts
    for mat, blobs in getattr(M, "PAINT", {}).items():
        cur = np.maximum(S[mat], 0.05)
        for (cx, cy, rx, ry, st) in blobs:
            b = P.blob(cx, cy, rx, ry, 0.6, wp)
            if mat in ("web", "field", "marsh", "mud"):
                b = b * (0.55 + 0.45 * smoothstep(0.3, 0.6, n_mid))
            cur = np.maximum(cur, 0.10 + 1.25 * b * st)
        S[mat] = cur.astype(np.float32)
        if mat in ("web", "burned", "blight", "scourge", "ash"):
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

    # water: crisp, driven by the same field as the tile grid; muddy bank around it
    wet = (water > 0.0).astype(np.float32)
    bank = smoothstep(-1.4, 0.0, water)
    S["shore"] = (0.05 + 1.35 * smoothstep(-1.0, 0.05, water)).astype(np.float32)
    S["marsh"] = np.maximum(S["marsh"], 0.05 + 0.6 * bank * (0.5 + 0.5 * n_mid)).astype(np.float32)
    S["shallow"] = np.clip(1.6 * water, -9.0, 9.0).astype(np.float32)
    S["deep"] = np.full_like(S["shallow"], -9.0)
    for k in LAND:
        S[k] = (S[k] - 12.0 * wet).astype(np.float32)

    # decks (bridges) over water
    if deck.max() > 0:
        on = smoothstep(-0.30, 0.10, deck)
        S["planks"] = np.maximum(S["planks"], -2.0 + 14 * np.clip(deck + 0.15, 0, 0.6)).astype(np.float32)
        S["shallow"] = (S["shallow"] - 60.0 * on).astype(np.float32)

    # cliffs
    depth_dark = smoothstep(2.0, 9.0, d_ci)
    cs = 1.6 + 12 * cliff_f
    S["cliff_a"] = (cs - 1.0 * depth_dark).astype(np.float32)
    S["cliff_d"] = (cs - 2.4 + 2.8 * depth_dark).astype(np.float32)
    cl_k = smoothstep(0.0, 0.30, cliff_f)
    for k in list(S):
        if not k.startswith("cliff_"):
            S[k] = (S[k] - 14.0 * cl_k).astype(np.float32)
    S["deep"] = np.full_like(S["shallow"], -9.0)
    for k in MATERIALS:
        S.setdefault(k, np.full_like(S["shallow"], -9.0))
    return S


def post(rgb, X, Y, P):
    f = P.fields
    sf = lambda a: P.sample_field(a.astype(np.float32), X, Y)
    d_co, d_ci = sf(f["d_co"]), sf(f["d_ci"])
    lum_n = P.sample_field(P.noise(14.0, "lumlow", octaves=2), X, Y)
    shade = 0.94 + 0.12 * lum_n
    shade *= 1 - 0.30 * (1 - smoothstep(0.0, 1.8, d_co))
    shade *= 1 - 0.30 * smoothstep(1.5, 9.0, d_ci)
    cf = sf(f["cf"])
    lip = smoothstep(0.0, 0.03, cf) * (1 - smoothstep(0.03, 0.14, cf))
    wd = sf(f["water"])
    depth = smoothstep(0.4, 5.0, wd)                                   # open water darkens smoothly towards the middle
    rgb = rgb * (1 - 0.6 * depth[..., None]) + np.array([6.0, 22.0, 30.0], np.float32) * 0.6 * depth[..., None]
    out = rgb * shade[..., None] + 22 * lip[..., None]
    out = out * np.array([0.96, 0.98, 1.02], np.float32)               # Tirisfal's permanent overcast
    return out


def bake(key, preview=None, sc=8):
    M = importlib.import_module(ZONES[key])
    P = Painter(M.W, M.H, TEX_DIR, seed=getattr(M, "SEED", 61))
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
    sc = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 8
    for k in keys:
        bake(k, preview.replace(".png", f"_{k}.png") if preview else None, sc)


if __name__ == "__main__":
    main()
