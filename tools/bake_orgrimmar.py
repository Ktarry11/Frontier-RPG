"""
Bake the Orgrimmar painting: district floors, brick walls, streets, plaza and the
red cliff rim, from seamless materials in assets/tiles/orgrimmar_city/materials
(the old per-district floor art made seamless + the VoT clay/road/cliff set).

    python3 tools/bake_orgrimmar.py [--preview out.png] [--scale 6]

Landforms come from tools/handbuilt_orgrimmar.fields() and the DISTRICTS / ROADS
tables - the SAME data the tile grid is built from.
Writes assets/tiles/orgrimmar_city/baked/ground_<cx>_<cy>.jpg (10x10 chunks of 20x20).
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

from tools import handbuilt_orgrimmar as O               # noqa: E402
from tools.terrain_painter import Painter, smoothstep, TILE_PX  # noqa: E402

TEX_DIR = ROOT / "assets/tiles/orgrimmar_city/materials"

MATERIALS = {
    "clay":     ("vot_clay_a", "vot_clay_pebbles", 1.0),
    "hard":     ("vot_hardpan", None, 1.0),
    "gravel":   ("vot_gravel", "vot_gravel_flat", 1.0),
    "road":     ("vot_road_ruts_a", "vot_road_ruts_b", 1.0),
    "plaza":    ("org_plaza", None, 1.0),
    "wisdom":   ("org_wisdom", None, 1.0),
    "honor":    ("org_honor", None, 1.0),
    "magic":    ("org_magic", None, 1.0),
    "strength": ("org_strength", None, 1.0),
    "warlock":  ("org_warlock", None, 1.0),
    "cleft":    ("org_cleft", None, 1.0),
    "craft":    ("org_craft", None, 1.0),
    "stables":  ("org_stables", None, 1.0),
    "wall":     ("org_wall", None, 1.0),
    "cliff_a":  ("vot_cliff_a", "vot_cliff_b", 1.0),
    "cliff_d":  ("vot_rock_dark", None, 1.0),
}

DISTRICT_MAT = {"wisdom": "wisdom", "magic": "magic", "honor": "honor", "strength": "strength",
                "warlock": "warlock", "cleft": "cleft", "craft_w": "craft", "craft_e": "craft",
                "stables": "stables"}


def build_scores(P):
    S = {}
    gx, gy = P.gx, P.gy
    n_big = P.noise(11.0, "big", octaves=3)
    n_mid = P.noise(5.0, "mid", octaves=3)
    n_fine = P.noise(2.0, "fine", octaves=2)

    F = O.fields(gx, gy)
    cliff = F["cliff"].astype(np.float32)
    wall = F["wall"].astype(np.float32)
    cliff_f = np.clip(cliff * 0.5, -0.4, 0.6).astype(np.float32)
    wall_f = np.clip(wall * 0.8, -0.4, 0.6).astype(np.float32)
    d_co = ndi.gaussian_filter(np.maximum(-cliff, 0), 1.2)
    d_ci = ndi.gaussian_filter(np.maximum(cliff, 0), 1.2)
    P.fields = dict(cliff=cliff, wall=wall, d_co=d_co, d_ci=d_ci, cf=cliff_f, wf=wall_f)

    # open ground between districts: clay with hardpan / gravel patches
    S["clay"] = np.full_like(n_big, 0.50)
    S["hard"] = 0.30 + 0.55 * smoothstep(0.55, 0.78, n_big)
    S["gravel"] = 0.22 + 0.60 * smoothstep(0.64, 0.84, n_mid) * (0.6 + 0.4 * n_fine)

    # district floors: each wins inside its own walls
    for dname, mat in DISTRICT_MAT.items():
        sd = O.district_sd(gx, gy, dname).astype(np.float32)
        inside = smoothstep(0.0, 1.6, sd)
        key = mat
        S[key] = np.maximum(S.get(key, np.full_like(n_big, -1.0)), -1.0 + 3.6 * inside).astype(np.float32)
    for k in ("wisdom", "magic", "honor", "strength", "warlock", "cleft", "craft", "stables"):
        S.setdefault(k, np.full_like(n_big, -1.0))
    # the central market
    px0, py0, px1, py1, pr = O.PLAZA
    sdp = O.rrect(gx, gy, px0, py0, px1, py1, pr).astype(np.float32)
    S["plaza"] = (-1.0 + 3.0 * smoothstep(0.0, 2.5, sdp)).astype(np.float32)

    core, verge, _ = P.road_field(list(O.ROADS.values()))
    S["road"] = 0.05 + 4.2 * core
    S["hard"] = np.maximum(S["hard"], 0.3 + 0.8 * verge * (1 - core))

    # brick walls
    S["wall"] = (-2.0 + 14 * np.clip(wall_f + 0.1, 0, 0.7)).astype(np.float32)

    # cliff rim
    depth_dark = smoothstep(2.0, 9.0, d_ci)
    cs = 1.6 + 12 * cliff_f
    S["cliff_a"] = (cs - 1.0 * depth_dark).astype(np.float32)
    S["cliff_d"] = (cs - 2.6 + 2.6 * depth_dark).astype(np.float32)
    cl_k = smoothstep(0.0, 0.30, cliff_f)
    w_k = smoothstep(0.0, 0.25, wall_f)
    for k in list(S):
        if k.startswith("cliff_"):
            continue
        if k == "wall":
            S[k] = (S[k] - 14.0 * cl_k).astype(np.float32)
        else:
            S[k] = (S[k] - 14.0 * cl_k - 14.0 * w_k).astype(np.float32)
    return S


def post(rgb, X, Y, P):
    f = P.fields
    sf = lambda a: P.sample_field(a.astype(np.float32), X, Y)
    d_co, d_ci = sf(f["d_co"]), sf(f["d_ci"])
    lum_n = P.sample_field(P.noise(16.0, "lumlow", octaves=2), X, Y)
    shade = 0.94 + 0.12 * lum_n
    shade *= 1 - 0.30 * (1 - smoothstep(0.0, 1.8, d_co))
    shade *= 1 - 0.30 * smoothstep(1.5, 9.0, d_ci)
    cf = sf(f["cf"])
    lip = smoothstep(0.0, 0.03, cf) * (1 - smoothstep(0.03, 0.14, cf))
    # walls: cast a soft shadow on the ground just outside them, bright cap on top
    wf = sf(f["wf"])
    wcap = smoothstep(0.0, 0.05, wf) * (1 - smoothstep(0.05, 0.28, wf))
    near_wall = (1 - smoothstep(-0.4, 0.0, wf)) * smoothstep(-0.9, -0.05, wf)
    shade *= 1 - 0.22 * near_wall
    return rgb * shade[..., None] + 26 * lip[..., None] + 22 * wcap[..., None]


def main():
    preview = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    P = Painter(O.W, O.H, TEX_DIR, seed=47)
    scores = build_scores(P)
    out = ROOT / O.BAKED_DIR
    written = P.bake(MATERIALS, scores, out, chunk_tiles=20, post=post)
    print(f"baked {len(written)} chunks -> {out}")
    if preview:
        sc = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 6
        full = Image.new("RGB", (O.W * TILE_PX, O.H * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        full.resize((O.W * sc, O.H * sc), Image.LANCZOS).save(preview)
        print("preview", preview)


if __name__ == "__main__":
    main()
