"""
Bake the Echo Isles painting (jungle islands, white-sand beaches, turquoise
fords over deep sea, sea-stack rock, timber piers) from the seamless tropical
materials in assets/tiles/echo_isles/materials.

    python3 tools/bake_echo_isles.py [--preview out.png] [--scale 6]

Landforms come from tools/handbuilt_echo_isles.fields() - the same functions the
tile grid is built from, so painting and collision cannot drift.
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

from tools import handbuilt_echo_isles as E              # noqa: E402
from tools.terrain_painter import Painter, smoothstep, TILE_PX  # noqa: E402

TEX_DIR = ROOT / "assets/tiles/echo_isles/materials"

MATERIALS = {
    "jungle":  ("echo_jungle_a", "echo_jungle_b", 1.0),
    "sand":    ("echo_sand", None, 1.0),
    "wet":     ("echo_wetsand", None, 1.0),
    "clay":    ("vot_mudshore", None, 1.0),
    "hard":    ("echo_wetsand", None, 1.0),
    "mud":     ("vot_mudshore", None, 1.0),
    "planks":  ("vot_planks", None, 1.0),
    "water_s": ("vot_water_shallow", None, 1.0),
    "water_d": ("vot_water_deep", None, 1.0),
    "rock_a":  ("echo_rock_a", "echo_rock_b", 1.0),
    "rock_d":  ("echo_rock_b", None, 1.0),
}

LAND_KEYS = ("jungle", "sand", "wet", "clay", "hard", "mud")


def build_scores(P):
    S = {}
    gx, gy = P.gx, P.gy
    wp = P.warp("regions", amp_tiles=2.2, scale=11.0)
    n_big = P.noise(10.0, "big", octaves=3)
    n_mid = P.noise(4.5, "mid", octaves=3)
    n_fine = P.noise(2.0, "fine", octaves=2)

    F = E.fields(gx, gy)
    land = F["land"].astype(np.float32)             # >0 dry land
    wet = F["wet"].astype(np.float32)               # >0 water
    deep = F["deep"].astype(np.float32)             # >0 deep sea
    deck = F["deck"].astype(np.float32)
    rock = F["rock_vis"].astype(np.float32)
    rock_f = np.clip(rock * 0.5, -0.4, 0.6).astype(np.float32)
    d_wo = np.maximum(land, 0) * 0 + np.maximum(wet * -1, 0)          # inland distance from waterline (land side)
    d_wi = np.maximum(wet, 0)                                         # offshore distance (water side)
    d_co = ndi.gaussian_filter(np.maximum(-rock, 0), 1.2)
    d_ci = ndi.gaussian_filter(np.maximum(rock, 0), 1.2)
    P.fields = dict(deck=deck, d_wo=d_wo, d_wi=d_wi, d_co=d_co, d_ci=d_ci, cf=rock_f, deep=deep)

    # ---- land: jungle floor; sand beach on the rim; wet sand at the waterline
    S["jungle"] = 0.55 + 0.35 * (n_big - 0.5) + 0.0 * n_fine
    S["clay"] = np.full_like(n_big, 0.10)
    S["hard"] = np.full_like(n_big, 0.05)
    beach = 1 - smoothstep(0.9, 2.3 + 0.8 * n_mid, land)             # 1 at the waterline
    S["sand"] = (0.10 + 1.15 * beach).astype(np.float32)
    S["wet"] = (0.05 + 1.3 * (1 - smoothstep(0.0, 1.1, land))).astype(np.float32)
    S["mud"] = np.full_like(n_big, -2.0)

    # camps / hand-authored clearings (trampled clay)
    camps = [(124, 56, 8, 6),      # troll camp
             (80, 52, 9, 7),       # darkspear village
             (30, 92, 6, 4),       # grotto landing
             (136, 106, 5, 4),     # hollow landing
             (24, 49, 5, 4)]       # naga ruins plaza (hardpan)
    c = np.zeros_like(n_big)
    for (cx, cy, rx, ry) in camps:
        c = np.maximum(c, P.blob(cx, cy, rx, ry, 0.6, wp))
    S["hard"] = np.maximum(S["hard"], 0.2 + 1.1 * c * (0.7 + 0.3 * smoothstep(0.3, 0.6, n_mid)))
    ruins = P.blob(24, 49, 8, 6, 0.6, wp)
    S["hard"] = np.maximum(S["hard"], 0.2 + 1.0 * ruins)

    # trails
    core, verge, _ = P.road_field([r for r in E.ROADS.values()])
    S["sand"] = np.maximum(S["sand"], 0.25 + 1.45 * core)
    S["wet"] = (S["wet"] - 1.0 * core).astype(np.float32)
    S["hard"] = np.maximum(S["hard"], 0.2 + 0.7 * verge * (1 - core) * 0.5)

    # ---- water (continuous scores -> anti-aliased shorelines)
    w_s = np.clip(wet, -4, 6)
    w_d = np.clip(deep, -6, 6)
    S["water_s"] = (1.6 + 10 * w_s).astype(np.float32)
    S["water_d"] = (1.6 + 10 * w_s + 3.0 * w_d - 0.0).astype(np.float32)
    knock = smoothstep(0.0, 0.7, wet)
    knock = np.maximum(knock, smoothstep(-0.30, 0.10, deck))
    S["planks"] = (-2.0 + 14 * np.clip(deck + 0.15, 0, 0.6)).astype(np.float32)
    for k in LAND_KEYS:
        S[k] = (S[k] - 14.0 * knock).astype(np.float32)
    on_deck = smoothstep(-0.30, 0.10, deck)
    S["water_s"] = (S["water_s"] - 120.0 * on_deck).astype(np.float32)
    S["water_d"] = (S["water_d"] - 120.0 * on_deck).astype(np.float32)

    # ---- rock (sea stacks + inland massifs), continuous
    depth_dark = smoothstep(2.0, 6.0, d_ci)
    cs = 1.6 + 12 * rock_f
    S["rock_a"] = (cs - 1.0 * depth_dark).astype(np.float32)
    S["rock_d"] = (cs - 2.2 + 2.2 * depth_dark - 3.0 * (1 - smoothstep(0.6, 0.85, n_big))).astype(np.float32)
    cl_k = smoothstep(0.0, 0.30, rock_f)
    wk = smoothstep(0.0, 1.2, rock)
    for k in list(S):
        if not k.startswith("rock_"):
            S[k] = (S[k] - 14.0 * cl_k - (120.0 * wk if k.startswith("water_") else 0.0)).astype(np.float32)
    return S


def post(rgb, X, Y, P):
    f = P.fields
    sf = lambda a: P.sample_field(a.astype(np.float32), X, Y)
    d_co, d_ci = sf(f["d_co"]), sf(f["d_ci"])
    d_wo, d_wi = sf(f["d_wo"]), sf(f["d_wi"])
    cf = sf(f["cf"])
    lum_n = P.sample_field(P.noise(16.0, "lumlow", octaves=2), X, Y)
    shade = 0.95 + 0.10 * lum_n
    shade *= 1 - 0.25 * (1 - smoothstep(0.0, 1.5, d_co))
    shade *= 1 - 0.25 * smoothstep(1.2, 7.0, d_ci)
    lip = smoothstep(0.0, 0.03, cf) * (1 - smoothstep(0.03, 0.14, cf))
    rgb = rgb * shade[..., None] + 22 * lip[..., None]
    # surf: soft white foam line right at the waterline, on the sea side
    foam = (1 - smoothstep(0.0, 0.34, d_wi)) * smoothstep(-0.05, 0.05, d_wi) * 0.38
    foam += (1 - smoothstep(0.0, 0.22, d_wo)) * 0.14
    foam = foam * (1 - smoothstep(-0.05, 0.12, cf))
    rgb = rgb * (1 - foam[..., None]) + np.array([232, 244, 242], np.float32) * foam[..., None]
    # wet darkening just inland of the foam
    wet = (1 - smoothstep(0.0, 0.9, d_wo)) * smoothstep(0.0, 0.2, d_wo)
    rgb *= (1 - 0.10 * wet)[..., None]
    # decks: dark rails + soft shadow on the water
    dk = sf(f["deck"])
    rail = smoothstep(-0.03, 0.03, dk) * (1 - smoothstep(0.10, 0.34, dk))
    rgb *= (1 - 0.45 * rail)[..., None]
    shadow = (1 - smoothstep(-0.03, 0.03, dk)) * (1 - smoothstep(0.0, 0.55, -dk)) * 0.35
    rgb *= (1 - shadow)[..., None]
    return rgb


def main():
    preview = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    P = Painter(E.W, E.H, TEX_DIR, seed=47)
    scores = build_scores(P)
    out = ROOT / E.BAKED_DIR
    written = P.bake(MATERIALS, scores, out, chunk_tiles=20, post=post)
    print(f"baked {len(written)} chunks -> {out}")
    if preview:
        sc = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 6
        full = Image.new("RGB", (E.W * TILE_PX, E.H * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        full.resize((E.W * sc, E.H * sc), Image.LANCZOS).save(preview)
        print("preview", preview)


if __name__ == "__main__":
    main()
