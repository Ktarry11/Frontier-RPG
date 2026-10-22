"""
Bake the Deathknell painting (valley floor, roads, square, graves, yard, claim, farm, pond, cliff ring) from the seamless
Tirisfal materials in assets/tiles/tirisfal/materials.

    python3 tools/bake_deathknell.py [--preview out.png] [--scale 12]

Landforms come from tools/handbuilt_deathknell.fields() - the same functions the tile grid is built from.
Writes assets/tiles/deathknell/baked/ground_<cx>_<cy>.jpg.
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

from tools import handbuilt_deathknell as D                    # noqa: E402
from tools.terrain_painter import Painter, smoothstep, TILE_PX  # noqa: E402

TEX_DIR = ROOT / "assets/tiles/tirisfal/materials"

MATERIALS = {
    "meadow":  ("tf_withered_meadow", "tf_dead_grass", 1.0),
    "mist":    ("tf_mist_grass", None, 1.0),
    "litter":  ("tf_leaf_litter", None, 1.0),
    "rocky":   ("tf_rocky_ground", None, 1.0),
    "earth":   ("tf_graveyard_earth", "tf_bone_dirt", 1.0),
    "gravel":  ("tf_grave_gravel", None, 1.0),
    "cobble":  ("tf_old_cobble", "tf_flagstone", 1.0),
    "road":    ("tf_road_centre", None, 1.0),
    "verge":   ("tf_road_edge", None, 1.0),
    "web":     ("tf_cobweb_floor", "tf_rocky_ground", 1.0),
    "field":   ("tf_farm_field", None, 1.0),
    "burned":  ("tf_burned_village", "tf_ash_ground", 1.0),
    "marsh":   ("tf_marsh_moss", "tf_mud_puddles", 1.0),
    "shore":   ("tf_shore_mud", None, 1.0),
    "shallow": ("tf_pond_shallow", None, 1.0),
    "deep":    ("tf_pond_deep", None, 1.0),
    "cliff_a": ("tf_cliff_a", "tf_cliff_b", 1.0),
    "cliff_d": ("tf_rock_wall", None, 1.0),
}


def build_scores(P):
    S = {}
    gx, gy = P.gx, P.gy
    wp = P.warp("regions", amp_tiles=1.8, scale=10.0)
    n_big = P.noise(9.0, "big", octaves=3)
    n_mid = P.noise(4.5, "mid", octaves=3)
    n_fine = P.noise(2.0, "fine", octaves=2)

    f = D.fields(gx, gy)
    cliff = f["cliff"].astype(np.float32)
    pond = f["pond"].astype(np.float32)
    cliff_f = np.clip(cliff * 0.5, -0.4, 0.6).astype(np.float32)
    d_co = ndi.gaussian_filter(np.maximum(-cliff, 0), 1.2)
    d_ci = ndi.gaussian_filter(np.maximum(cliff, 0), 1.2)
    P.fields = dict(cliff=cliff, d_co=d_co, d_ci=d_ci, cf=cliff_f, pond=pond)

    blob = lambda c, grow=0.0: P.blob(c[0], c[1], c[2] + grow, c[3] + grow * 0.8, 0.6, wp)
    plaza = blob(D.PLAZA, 1.0)
    graves = blob(D.GRAVES, 0.5)
    yard = blob(D.YARD, -1.0)
    claim = blob(D.CLAIM)
    crypt = blob(D.CRYPT, -1.0)
    farm = blob(D.FARM)
    pond_edge = smoothstep(-0.28, 0.0, pond)                        # the muddy bank around the water

    # base: sallow meadow with mist-grass, leaf-litter and rocky patches
    S["meadow"] = np.full_like(n_big, 0.55)
    S["mist"] = 0.20 + 0.70 * smoothstep(0.58, 0.82, n_big)
    S["litter"] = 0.10 + 0.75 * smoothstep(0.62, 0.84, n_mid) * (0.6 + 0.4 * n_fine)
    S["rocky"] = 0.05 + 0.40 * smoothstep(0.66, 0.85, n_mid)
    near_rim = smoothstep(-6.0, -1.0, cliff)
    S["rocky"] = np.maximum(S["rocky"], 0.2 + 0.95 * near_rim)
    S["litter"] = np.maximum(S["litter"], 0.2 + 0.6 * near_rim * smoothstep(0.45, 0.7, n_mid))

    # districts
    S["cobble"] = 0.10 + 1.3 * plaza
    S["earth"] = 0.10 + 1.25 * graves
    S["gravel"] = 0.10 + 1.25 * yard
    S["web"] = 0.10 + 1.2 * claim * (0.5 + 0.5 * smoothstep(0.3, 0.6, n_mid))
    S["rocky"] = np.maximum(S["rocky"], 0.2 + 0.9 * claim * 0.6)
    S["cobble"] = np.maximum(S["cobble"], 0.15 + 1.1 * crypt)
    S["field"] = 0.05 + 1.2 * farm * smoothstep(0.35, 0.6, n_big)
    S["burned"] = 0.05 + 1.25 * P.blob(79, 66, 4.5, 3.6, 0.6, wp)
    S["marsh"] = 0.05 + 1.1 * pond_edge * (0.5 + 0.5 * n_mid) + 0.3 * smoothstep(0.7, 0.9, n_big)
    S["shore"] = 0.05 + 1.35 * smoothstep(-0.16, 0.02, pond)

    # roads
    core, verge, _ = P.road_field(list(D.ROADS.values()))
    S["road"] = 0.05 + 1.3 * core
    S["verge"] = np.maximum(0.05, 0.25 + 0.9 * verge * (1 - core))

    # water: crisp, driven by the same pond field as the tile grid
    in_pond = np.clip(14.0 * (pond - 0.0), -9.0, 9.0)
    deep_k = np.clip(7.0 * (pond - 0.45), -9.0, 9.0)
    S["shallow"] = in_pond.astype(np.float32)
    S["deep"] = np.where(pond > 0.30, np.clip(5.0 * (pond - 0.30), 0.0, 1.0) * 0.0 - 0.5 + 6.0 * (pond - 0.30), -9.0).astype(np.float32)
    wet = (pond > 0.0).astype(np.float32)
    for k in ("meadow", "mist", "litter", "rocky", "earth", "gravel", "cobble", "web", "field", "burned", "marsh", "shore",
              "road", "verge"):
        S[k] = (S[k] - 12.0 * wet).astype(np.float32)

    # cliffs
    depth_dark = smoothstep(2.0, 9.0, d_ci)
    cs = 1.6 + 12 * cliff_f
    S["cliff_a"] = (cs - 1.0 * depth_dark).astype(np.float32)
    S["cliff_d"] = (cs - 2.4 + 2.8 * depth_dark).astype(np.float32)
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
    shade *= 1 - 0.30 * (1 - smoothstep(0.0, 1.8, d_co))       # floor edge darkens into the rim
    shade *= 1 - 0.30 * smoothstep(1.5, 9.0, d_ci)             # rock deepens away from the edge
    cf = sf(f["cf"])
    lip = smoothstep(0.0, 0.03, cf) * (1 - smoothstep(0.03, 0.14, cf))
    pd = sf(f["pond"])
    depth = smoothstep(0.15, 0.62, pd)                         # open water darkens smoothly towards the middle
    rgb = rgb * (1 - 0.55 * depth[..., None]) + np.array([6.0, 22.0, 30.0], np.float32) * 0.55 * depth[..., None]
    out = rgb * shade[..., None] + 22 * lip[..., None]
    # Tirisfal's permanent overcast: cool the whole valley slightly
    out = out * np.array([0.96, 0.98, 1.02], np.float32)
    return out


def main():
    preview = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    P = Painter(D.W, D.H, TEX_DIR, seed=44)
    scores = build_scores(P)
    out = ROOT / D.BAKED_DIR
    written = P.bake(MATERIALS, scores, out, chunk_tiles=20, post=post)
    print(f"baked {len(written)} chunks -> {out}")
    if preview:
        sc = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 12
        full = Image.new("RGB", (D.W * TILE_PX, D.H * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        full.resize((D.W * sc, D.H * sc), Image.LANCZOS).save(preview)
        print("preview", preview)


if __name__ == "__main__":
    main()
