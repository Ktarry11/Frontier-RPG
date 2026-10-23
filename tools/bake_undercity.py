"""
Bake the Undercity painting: teal brick plaza, flagstone avenues and promenade, per-quarter floors (royal crypt + marble
hall, magic teal + ritual hall, war cobble + gravel arena, apothecarium sewer-moss + plague hall), the sewer canal, plank
bridges, brick quarter walls and the skull-wall cavern rim, from the Tirisfal seamless materials
(assets/tiles/tirisfal/materials/tf_*.png).

    PYTHONPATH=. python3 tools/bake_undercity.py [--preview out.png] [--scale 6]

Landforms come from tools/handbuilt_undercity.fields() and the QUARTERS / HALLS / ROADS tables - the SAME data the tile
grid is built from.  Writes assets/tiles/undercity/baked/ground_<cx>_<cy>.jpg (10x10 chunks of 20x20 tiles).
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

from tools import handbuilt_undercity as U                 # noqa: E402
from tools.terrain_painter import Painter, smoothstep, TILE_PX  # noqa: E402

TEX_DIR = ROOT / "assets/tiles/tirisfal/materials"

MATERIALS = {
    "plaza":    ("tf_undercity_floor", None, 1.0),
    "avenue":   ("tf_flagstone", "tf_old_cobble", 1.0),
    "marble":   ("tf_mausoleum_marble", None, 1.0),
    "crypt":    ("tf_crypt_floor", None, 1.0),
    "cobble":   ("tf_stone_wall", None, 1.0),
    "sewer":    ("tf_sewer_floor", None, 1.0),
    "gravel":   ("tf_grave_gravel", None, 1.0),
    "ritual":   ("tf_ritual_floor", None, 1.0),
    "plague":   ("tf_plague_ground", None, 1.0),
    "deck":     ("tf_rotten_planks", None, 1.0),
    "water":    ("uc_sewer_water", None, 1.0),      # tf_sewer_water with its brown top-edge stripe cleaned out
    "wall":     ("tf_undercity_wall", None, 1.0),
    "rim_skull": ("tf_ossuary_wall", None, 1.0),
    "rim_rock": ("tf_cliff_b", "tf_rock_wall", 1.0),
}

# quarter -> (ground material, hall material)
QUARTER_MAT = {"royal": ("crypt", "marble"), "magic": ("plaza", "crypt"),
               "war": ("cobble", "gravel"), "apoth": ("sewer", "sewer")}


def build_scores(P):
    S = {}
    gx, gy = P.gx, P.gy
    n_big = P.noise(11.0, "big", octaves=3)
    n_mid = P.noise(5.0, "mid", octaves=3)
    n_fine = P.noise(2.0, "fine", octaves=2)

    F = U.fields(gx, gy)
    cliff = F["cliff"].astype(np.float32)
    wall = F["wall"].astype(np.float32)
    canal = F["canal"].astype(np.float32)
    bridge = F["bridge"].astype(np.float32)
    cliff_f = np.clip(cliff * 0.5, -0.4, 0.6).astype(np.float32)
    wall_f = np.clip(wall * 0.8, -0.4, 0.6).astype(np.float32)
    canal_f = np.clip(canal * 0.5, -0.5, 0.8).astype(np.float32)
    d_co = ndi.gaussian_filter(np.maximum(-cliff, 0), 1.2)
    d_ci = ndi.gaussian_filter(np.maximum(cliff, 0), 1.2)
    d_canal = ndi.gaussian_filter(np.maximum(canal, 0), 1.0)
    P.fields = dict(cliff=cliff, wall=wall, d_co=d_co, d_ci=d_ci, cf=cliff_f, wf=wall_f, cn=canal_f, dcn=d_canal)

    r = U.radius(gx, gy).astype(np.float32)

    # default ground everywhere = the teal plaza brick; patches of darker / mossier brick break it up
    S["plaza"] = np.full_like(n_big, 0.50) + 0.10 * smoothstep(0.6, 0.8, n_big)
    S["cobble"] = np.full_like(n_big, -1.0)
    S["crypt"] = np.full_like(n_big, -1.0)
    S["marble"] = np.full_like(n_big, -1.0)
    S["sewer"] = np.full_like(n_big, -1.0)
    S["gravel"] = np.full_like(n_big, -1.0)
    S["plague"] = np.full_like(n_big, -1.0)
    S["ritual"] = np.full_like(n_big, -1.0)

    for qn, (gm, hm) in QUARTER_MAT.items():
        inside = smoothstep(0.0, 1.6, U.quarter_sd(gx, gy, qn).astype(np.float32))
        S[gm] = np.maximum(S[gm], -1.0 + 3.4 * inside).astype(np.float32)
        hin = smoothstep(0.0, 1.6, U.hall_sd(gx, gy, qn).astype(np.float32))
        S[hm] = np.maximum(S[hm], -1.0 + 3.8 * hin).astype(np.float32)
    # moss-plague patches in the apothecarium hall, ritual sigil under the Violet Spire, the Seal in the plaza
    ax, ay, _ = U.HALLS["apoth"]
    dap = np.hypot(gx - ax, gy - ay)
    S["plague"] = np.maximum(S["plague"], (-1.0 + 3.0 * smoothstep(0.0, 1.0, 0.55 * n_mid + 0.45 * n_fine)
                                           * smoothstep(0.0, 1.5, U.hall_sd(gx, gy, "apoth") - 2.0))).astype(np.float32)
    mx, my, _ = U.HALLS["magic"]
    dmg = np.hypot(gx - mx, gy - my)
    S["ritual"] = np.maximum(S["ritual"], (-1.0 + 3.8 * smoothstep(0.0, 1.2, 7.6 - dmg))).astype(np.float32)
    S["ritual"] = np.maximum(S["ritual"], (-1.0 + 3.8 * smoothstep(0.0, 1.2, 8.6 - r))).astype(np.float32)
    # ritual floor ring around the Seal is the same material; keep the Seal itself clear of roads
    pr = np.clip(1.0 - np.abs(r - 53.25) / 9.0, 0, 1)
    S["avenue"] = np.full_like(n_big, 0.0)

    core, verge, _ = P.road_field(list(U.ROADS.values()))
    S["avenue"] = (0.10 + 4.0 * core).astype(np.float32)
    S["avenue"] = np.where(r < 9.5, -1.0, S["avenue"]).astype(np.float32)          # the Seal stays bare
    # canal banks: worn pavement hugging the water
    bank = smoothstep(0.0, 1.6, 1.8 - np.maximum(-canal, 0.0))        # within ~1.8 tiles of the canal
    S["avenue"] = np.maximum(S["avenue"], (0.2 + 1.6 * bank * (canal <= 0))).astype(np.float32)

    # canal water + plank bridges
    S["water"] = (-2.0 + 12 * np.clip(canal_f + 0.12, 0, 0.8)).astype(np.float32)
    br_k = smoothstep(0.0, 0.5, np.clip(bridge * 0.5, -0.4, 0.8))
    S["deck"] = (-2.0 + 6.0 * br_k).astype(np.float32)
    S["water"] = (S["water"] - 14.0 * br_k).astype(np.float32)

    # brick quarter / hall walls
    S["wall"] = (-2.0 + 14 * np.clip(wall_f + 0.1, 0, 0.7)).astype(np.float32)

    # cavern rim: skull wall at the edge, dark rock behind it
    depth_dark = smoothstep(2.0, 9.0, d_ci)
    cs = 1.6 + 12 * cliff_f
    S["rim_skull"] = (cs - 0.2 - 2.4 * depth_dark).astype(np.float32)
    S["rim_rock"] = (cs - 2.2 + 2.6 * depth_dark).astype(np.float32)
    cl_k = smoothstep(0.0, 0.30, cliff_f)
    w_k = smoothstep(0.0, 0.25, wall_f)
    for k in list(S):
        if k in ("rim_skull", "rim_rock"):
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
    shade = 0.98 + 0.12 * lum_n
    shade *= 1 - 0.30 * (1 - smoothstep(0.0, 1.8, d_co))
    shade *= 1 - 0.34 * smoothstep(1.5, 9.0, d_ci)
    # a cavern is darker the further you are from the plaza lights: gentle radial vignette
    gx = X / TILE_PX
    gy = Y / TILE_PX
    r = np.hypot(gx - U.CX, gy - U.CY)
    shade *= 1.08 - 0.16 * smoothstep(48.0, 92.0, r)
    cf = sf(f["cf"])
    lip = smoothstep(0.0, 0.03, cf) * (1 - smoothstep(0.03, 0.14, cf))
    wf = sf(f["wf"])
    wcap = smoothstep(0.0, 0.05, wf) * (1 - smoothstep(0.05, 0.28, wf))
    near_wall = (1 - smoothstep(-0.4, 0.0, wf)) * smoothstep(-0.9, -0.05, wf)
    shade *= 1 - 0.22 * near_wall
    out = rgb * shade[..., None] + 26 * lip[..., None] + 22 * wcap[..., None]
    # canal: darker toward the middle of the channel, with a faint green glow rising off it
    cn = sf(f["cn"])
    in_canal = smoothstep(0.0, 0.12, cn)
    out = out * (1 - 0.22 * in_canal[..., None] * smoothstep(0.1, 0.8, cn)[..., None])
    glow = np.exp(-np.maximum(-cn, 0) * 3.0) * (cn < 0.02)
    out[..., 1] += 7.0 * glow
    return out


def main():
    preview = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    P = Painter(U.W, U.H, TEX_DIR, seed=59)
    scores = build_scores(P)
    out = ROOT / U.BAKED_DIR
    written = P.bake(MATERIALS, scores, out, chunk_tiles=20, post=post)
    print(f"baked {len(written)} chunks -> {out}")
    if preview:
        sc = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 6
        full = Image.new("RGB", (U.W * TILE_PX, U.H * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        full.resize((U.W * sc, U.H * sc), Image.LANCZOS).save(preview)
        print("preview", preview)


if __name__ == "__main__":
    main()
