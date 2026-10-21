"""
Bake the Valley of Trials painting (ground + water + cliffs) from the
seamless materials in assets/tiles/vot_cluster.

    python3 tools/bake_vot_terrain.py [--preview out.png]

Reads the tile layout from tools/handbuilt_vot.py (so water/cliff/road shapes
here are always the ones the game uses), writes assets/tiles/valley_of_trials/
baked/ground_<cx>_<cy>.jpg (6x6 chunks of 20x20 tiles).
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

from tools import handbuilt_vot as V                      # noqa: E402
from tools.terrain_painter import Painter, smoothstep, MASK_PX, TILE_PX  # noqa: E402

TEX_DIR = ROOT / "assets/tiles/vot_cluster"

MATERIALS = {
    "clay":    ("vot_clay_a", "vot_clay_pebbles", 1.0),
    "hard":    ("vot_hardpan", None, 1.0),
    "cinder":  ("vot_cinder", None, 1.0),
    "dune":    ("vot_dune", None, 1.0),
    "bone":    ("vot_bonesand", None, 1.0),
    "gravel":  ("vot_gravel", "vot_gravel_flat", 1.0),
    "sage":    ("vot_sagegrass", None, 1.0),
    "green":   ("vot_greengrass", None, 1.0),
    "mud":     ("vot_mudshore", None, 1.0),
    "burrow":  ("vot_burrow", "vot_clay_pebbles", 1.0),
    "camp":    ("vot_camp_prints", "vot_clay_pebbles", 1.0),
    "flag":    ("vot_flag_red", None, 1.0),
    "road":    ("vot_road_ruts_a", "vot_road_ruts_b", 1.0),
    "water_s": ("vot_water_shallow", None, 1.0),
    "water_d": ("vot_water_deep", None, 1.0),
    "cliff_a": ("vot_cliff_a", "vot_cliff_b", 1.0),
    "cliff_d": ("vot_rock_dark", None, 1.0),
    "cliff_l": ("vot_limestone", None, 1.0),
}


def build_scores(P, L):
    z = L.zone
    S = {}
    wp = P.warp("regions", amp_tiles=2.6, scale=13.0)
    n_big = P.noise(11.0, "big", octaves=3)
    n_mid = P.noise(5.0, "mid", octaves=3)
    n_fine = P.noise(2.0, "fine", octaves=2)

    # -------- tile-derived masks (organic edges)
    cliff_b = np.array([[c == "cliff" for c in row] for row in z.collision_layer])
    deep_b = np.array([[b == "deep_water" for b in row] for row in z.base_layer])
    shal_b = np.array([[b == "shallow_water" for b in row] for row in z.base_layer])
    cliff_f = P.tile_mask(cliff_b, 0.5, 0.20, "cliffm", soft=True)   # >0 inside cliff
    cliff = cliff_f > 0
    # the lake is an analytic smooth shape shared with the layout, so the
    # painted shoreline is pixel-smooth while tiles match to within ~half a tile
    sh_ext, dp_ext = V.lake_fields(P.gx, P.gy)
    wob = (P.noise(3.0, "shorewob", octaves=3) - 0.5) * 0.9
    water = (sh_ext + wob) > 0
    deepw = ((dp_ext + wob) > 0) & water
    sw = (sh_ext + wob).astype(np.float32)            # signed, ~tiles, continuous
    d_water_out = np.maximum(-sw, 0)                  # tiles from water, on land
    d_water_in = np.maximum(sw, 0)                    # tiles inside water from shore
    d_cliff_out = P.edt(~cliff) / MASK_PX            # tiles from cliff, on land
    d_cliff_in = ndi.gaussian_filter(P.edt(cliff) / MASK_PX, 1.2)   # tiles inside cliff from its edge
    d_cliff_out = ndi.gaussian_filter(d_cliff_out, 1.2)
    P.fields = dict(cliff=cliff, water=water, deep=deepw, d_wo=d_water_out,
                    d_wi=d_water_in, d_co=d_cliff_out, d_ci=d_cliff_in, cf=cliff_f.astype(np.float32))

    land = ~cliff & ~water

    # -------- base country: clay with hardpan / gravel patches
    S["clay"] = np.full_like(n_big, 0.50)
    S["hard"] = 0.30 + 0.60 * smoothstep(0.55, 0.78, n_big)
    S["gravel"] = 0.25 + 0.70 * smoothstep(0.62, 0.82, n_mid) * (0.6 + 0.4 * n_fine)

    # -------- regions (hand-authored)
    camp_plaza = P.blob(60, 23, 12, 9, 0.6, wp)
    camp_yard = P.blob(58, 44, 10, 9, 0.6, wp)
    camp_mid = P.blob(60, 33, 8, 7, 0.7, wp)
    S["camp"] = 0.15 + 0.95 * np.maximum.reduce([camp_plaza, camp_yard, camp_mid * 0.8])
    S["flag"] = 0.10 + 0.95 * P.blob(59, 23, 5.5, 4.2, 0.55, wp)

    flat = P.blob(28, 29, 13, 12, 0.7, wp)                   # Sagebrush Flat
    S["sage"] = 0.12 + 0.95 * flat * (0.55 + 0.45 * smoothstep(0.30, 0.55, n_mid))
    lush_flat = P.blob(23, 24, 6, 5, 0.8, wp) * smoothstep(0.35, 0.60, n_fine)
    grove = P.blob(80, 36, 10, 11, 0.7, wp)                  # Sagewood Grove
    S["green"] = 0.08 + 0.95 * np.maximum(grove * smoothstep(0.25, 0.5, n_mid), lush_flat)
    S["sage"] = np.maximum(S["sage"], 0.12 + 0.9 * grove * (1 - smoothstep(0.25, 0.5, n_mid)))

    nest = P.blob(94, 21, 15, 13, 0.7, wp)                   # Scorpid Nest
    S["burrow"] = 0.10 + 0.95 * nest
    S["bone"] = 0.12 + 0.85 * smoothstep(0.6, 0.8, n_fine) * np.maximum(nest, P.blob(94, 52, 10, 10, 0.8, wp))
    dunes = P.blob(95, 52, 11, 22, 0.7, wp)                  # Windrift Dunes
    S["dune"] = 0.10 + 0.95 * dunes
    cinder = P.blob(38, 93, 21, 11, 0.7, wp)                 # Cinderjaw Wastes
    S["cinder"] = 0.10 + 0.95 * cinder
    S["gravel"] = np.maximum(S["gravel"], 0.2 + 0.8 * P.blob(38, 93, 24, 13, 0.9, wp) * smoothstep(0.45, 0.65, n_mid))

    # -------- lake: mud rim then a green fringe, noise-broken
    S["mud"] = 0.10 + 1.0 * (1 - smoothstep(0.5, 2.4, d_water_out)) * (0.75 + 0.25 * n_fine)
    fringe = (1 - smoothstep(2.0, 6.5, d_water_out)) * smoothstep(0.30, 0.55, n_mid)
    S["green"] = np.maximum(S["green"], 0.08 + 0.9 * fringe)

    # -------- roads
    core, verge, _ = P.road_field(list(V.ROADS.values()))
    S["road"] = 0.05 + 1.25 * core
    # worn verge: hardpan/gravel creeps in around the road
    S["hard"] = np.maximum(S["hard"], 0.3 + 0.8 * verge * (1 - core))

    # -------- water (continuous scores -> anti-aliased shoreline)
    w_s = np.clip(sh_ext + wob, -4, 6)
    w_d = np.clip(dp_ext + wob, -6, 6)
    S["water_s"] = (1.6 + 10 * w_s).astype(np.float32)
    S["water_d"] = (1.6 + 10 * w_s + 10 * w_d).astype(np.float32)
    inw = (sh_ext + wob) > 0.45
    for k in ("clay", "hard", "gravel", "camp", "flag", "sage", "green", "burrow", "bone",
              "dune", "cinder", "mud", "road"):
        S[k] = np.where(inw, -2.0, S[k]).astype(np.float32)

    # -------- cliffs (continuous)
    depth_dark = smoothstep(2.0, 9.0, d_cliff_in)
    cs = 1.6 + 12 * np.clip(cliff_f, -0.4, 0.6)
    S["cliff_a"] = (cs - 1.0 * depth_dark).astype(np.float32)
    S["cliff_l"] = (cs - 1.0 - 4.0 * (1 - smoothstep(0.70, 0.85, n_big)) - 2 * depth_dark).astype(np.float32)
    S["cliff_d"] = (cs - 0.6 + 3.0 * depth_dark - 1.0 * (1 - depth_dark)).astype(np.float32)
    deep_in = cliff_f > 0.12
    for k in list(S):
        if not k.startswith("cliff_") and not k.startswith("water_"):
            S[k] = np.where(deep_in, -2.0, S[k]).astype(np.float32)
    return S


def post(rgb, X, Y, P):
    f = P.fields
    sf = lambda a: P.sample_field(a.astype(np.float32), X, Y)
    d_co, d_ci = sf(f["d_co"]), sf(f["d_ci"])
    d_wo, d_wi = sf(f["d_wo"]), sf(f["d_wi"])
    lum_n = P.sample_field(P.noise(18.0, "lumlow", octaves=2), X, Y)
    shade = 0.93 + 0.14 * lum_n
    # ambient occlusion where land meets cliff, and depth into the mountain
    shade *= 1 - 0.28 * (1 - smoothstep(0.0, 1.7, d_co)) * (d_co < 3)
    shade *= 1 - 0.40 * smoothstep(1.5, 11.0, d_ci)
    # lit lip on the cliff edge
    cf = sf(f["cf"])
    lip = smoothstep(0.0, 0.03, cf) * (1 - smoothstep(0.03, 0.14, cf))
    rgb = rgb * shade[..., None] + 26 * lip[..., None]
    # wet-sand darkening and a soft foam line at the waterline
    wet = (1 - smoothstep(0.0, 1.0, d_wo)) * (d_wo > 0)
    rgb *= (1 - 0.14 * wet)[..., None]
    foam = np.maximum((d_wo > 0) * (1 - smoothstep(0.0, 0.28, d_wo)),
                      (d_wi > 0) * (1 - smoothstep(0.0, 0.30, d_wi))) * 0.30
    rgb = rgb * (1 - foam[..., None]) + np.array([225, 240, 240], np.float32) * foam[..., None]
    return rgb


def main():
    preview = None
    if "--preview" in sys.argv:
        preview = sys.argv[sys.argv.index("--preview") + 1]
    L = V.build_layout()
    P = Painter(V.W, V.H, TEX_DIR, seed=11)
    scores = build_scores(P, L)
    out = ROOT / V.BAKED_DIR
    written = P.bake(MATERIALS, scores, out, chunk_tiles=20, post=post)
    print(f"baked {len(written)} chunks -> {out}")
    if preview:
        full = Image.new("RGB", (V.W * TILE_PX, V.H * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        full.resize((V.W * 8, V.H * 8), Image.LANCZOS).save(preview)
        print("preview", preview)
    if L.skipped:
        print("props skipped:", len(L.skipped))
        for s in L.skipped:
            print("  ", s)


if __name__ == "__main__":
    main()
