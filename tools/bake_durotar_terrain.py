"""
Bake the Durotar painting (ground + water + cliffs + decks) from the seamless
materials in assets/tiles/vot_cluster (Durotar reuses the Valley of Trials
tileset - same red-clay country).

    python3 tools/bake_durotar_terrain.py [--preview out.png] [--scale 6]

Landforms come from tools/handbuilt_durotar.fields() - the SAME analytic
functions the tile grid is built from - so painting and collision agree.
Writes assets/tiles/durotar/baked/ground_<cx>_<cy>.jpg (7x11 chunks of 20x20).
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

from tools import handbuilt_durotar as D                  # noqa: E402
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
    "planks":  ("vot_planks", None, 1.0),
    "water_s": ("vot_water_shallow", None, 1.0),
    "water_d": ("vot_water_deep", None, 1.0),
    "cliff_a": ("vot_cliff_a", "vot_cliff_b", 1.0),
    "cliff_d": ("vot_rock_dark", None, 1.0),
    "cliff_l": ("vot_limestone", None, 1.0),
}


def build_scores(P):
    S = {}
    gx, gy = P.gx, P.gy
    wp = P.warp("regions", amp_tiles=2.6, scale=13.0)
    n_big = P.noise(11.0, "big", octaves=3)
    n_mid = P.noise(5.0, "mid", octaves=3)
    n_fine = P.noise(2.0, "fine", octaves=2)

    F = D.fields(gx, gy)
    wob = (P.noise(3.0, "shorewob", octaves=3) - 0.5) * 0.9
    sh_ext = F["shallow"]
    dp_ext = F["deep"]
    cliff = F["cliff"].astype(np.float32)
    deck = F["deck"].astype(np.float32)
    water = (sh_ext + wob) > 0
    cliff_f = np.clip(cliff * 0.5, -0.4, 0.6).astype(np.float32)
    sw = (sh_ext + wob).astype(np.float32)
    d_water_out = np.maximum(-sw, 0)
    d_water_in = np.maximum(sw, 0)
    d_cliff_out = ndi.gaussian_filter(np.maximum(-cliff, 0), 1.2)
    d_cliff_in = ndi.gaussian_filter(np.maximum(cliff, 0), 1.2)
    # distance from the SEA only (for dune beaches) - river gets mud instead
    sea_ext = np.maximum(gx - D.coast_east(gy), gy - D.coast_south(gx))
    P.fields = dict(cliff=cliff, deck=deck, d_wo=d_water_out, d_wi=d_water_in,
                    d_co=d_cliff_out, d_ci=d_cliff_in, cf=cliff_f)

    # -------- base country: clay with hardpan / gravel patches
    S["clay"] = np.full_like(n_big, 0.50)
    S["hard"] = 0.30 + 0.60 * smoothstep(0.55, 0.78, n_big)
    S["gravel"] = 0.25 + 0.70 * smoothstep(0.62, 0.82, n_mid) * (0.6 + 0.4 * n_fine)

    # -------- regions (hand-authored), by name
    gate_plaza = P.blob(65, 28, 13, 7, 0.6, wp)
    gate_flag = P.blob(65, 27, 7, 4.2, 0.55, wp)
    thunder = P.blob(50, 56, 16, 13, 0.7, wp)
    drygulch = P.blob(88, 30, 12, 6, 0.7, wp)
    skull = P.blob(111, 54, 17, 15, 0.8, wp)
    skull_bone = P.blob(115, 60, 11, 8, 0.8, wp)
    pan = P.blob(80, 142, 10, 9, 0.8, wp)
    highway = P.blob(76, 60, 9, 30, 0.8, wp)
    kolkar = P.blob(26, 124, 17, 14, 0.7, wp)
    kolkar_camp = P.blob(23, 124, 8, 6.5, 0.7, wp)
    farm = P.blob(33, 173, 17, 15, 0.7, wp)
    razor = P.blob(65, 106, 13, 9, 0.6, wp)
    tira = P.blob(92, 176, 15, 11, 0.7, wp)
    flats = P.blob(78, 132, 16, 18, 0.8, wp)          # the Sun-Cracked Flats (hardpan pan)
    dunes_n = P.blob(98, 128, 12, 14, 0.7, wp)
    barrens = P.blob(36, 90, 20, 8, 0.8, wp)

    S["camp"] = 0.15 + 0.95 * np.maximum.reduce([gate_plaza * 0.9, razor * 0.9,
                                                 kolkar_camp, P.blob(100, 55, 5, 4, .6, wp) * 0.7])
    S["flag"] = 0.10 + 0.95 * gate_flag
    S["hard"] = np.maximum(S["hard"], 0.2 + 0.95 * np.maximum(flats, thunder * smoothstep(0.35, 0.55, n_mid)))
    S["gravel"] = np.maximum.reduce([S["gravel"],
                                     0.2 + 0.9 * thunder * smoothstep(0.45, 0.65, n_fine),
                                     0.2 + 0.9 * drygulch,
                                     0.2 + 0.9 * tira * smoothstep(0.35, 0.6, n_mid),
                                     0.2 + 0.9 * barrens * smoothstep(0.5, 0.7, n_mid)])
    S["sage"] = 0.12 + 0.95 * np.maximum.reduce([kolkar * (0.5 + 0.5 * smoothstep(0.3, 0.55, n_mid)),
                                                 farm * 0.9, highway * smoothstep(0.58, 0.72, n_mid)])
    # crop furrows at Rocktusk Farm: rows of green between rows of tilled earth
    fields_rects = [(20, 160, 30, 168), (32, 160, 42, 168), (20, 172, 30, 181), (33, 172, 43, 181)]
    plots = np.zeros_like(n_big)
    for (x0, y0, x1, y1) in fields_rects:
        plots = np.maximum(plots, P.rect(x0, y0, x1, y1, soft_tiles=1.1, warp=wp))
    rows = 0.5 + 0.5 * np.sin((gy + 1.4 * (n_fine - 0.5)) * np.pi * 0.62)   # furrow rows, hand-wobbled
    S["green"] = np.full_like(n_big, 0.08)
    S["green"] = np.maximum(S["green"], 0.12 + 0.95 * plots * smoothstep(0.3, 0.7, rows))
    S["burrow"] = 0.10 + 0.95 * np.maximum(plots * (1 - smoothstep(0.3, 0.7, rows)),
                                           P.blob(30, 175, 4, 3, 0.6, wp) * 0.0)
    S["cinder"] = 0.10 + 0.95 * np.maximum(skull * (0.4 + 0.6 * smoothstep(0.35, 0.6, n_mid)),
                                           thunder * 0.55 * smoothstep(0.55, 0.75, n_fine))
    S["bone"] = 0.12 + 0.85 * np.maximum.reduce([skull_bone, smoothstep(0.7, 0.85, n_fine) * skull,
                                                 pan * smoothstep(0.42, 0.62, n_mid)])
    beach_w = (1 - smoothstep(0.8, 8.0, -np.minimum(sea_ext, 0))) * (0.55 + 0.45 * smoothstep(0.25, 0.6, n_mid))      # 1 at the waterline, fading inland
    beach_w = np.where(gx > 70, beach_w, np.where(gy > 150, beach_w, 0))
    S["dune"] = 0.10 + 0.95 * np.maximum.reduce([beach_w * (0.55 + 0.45 * smoothstep(0.3, 0.55, n_fine)),
                                                 dunes_n * 0.9])

    # -------- shores: mud rim, then a green fringe (river and sea)
    S["mud"] = 0.10 + 1.0 * (1 - smoothstep(0.5, 2.4, d_water_out)) * (0.75 + 0.25 * n_fine)
    fringe = (1 - smoothstep(2.0, 6.5, d_water_out)) * smoothstep(0.30, 0.55, n_mid) * (gx < 30)
    S["green"] = np.maximum(S["green"], 0.08 + 0.9 * fringe)
    # sea shore stays sandy: mud only along the river, dune sand along the sea
    sea_side = (sea_ext > -4)
    S["mud"] = np.where(sea_side, 0.05 + 0.4 * (1 - smoothstep(0.3, 1.2, d_water_out)), S["mud"]).astype(np.float32)

    # -------- roads
    core, verge, _ = P.road_field(list(r for r in D.ROADS.values()))
    S["road"] = 0.05 + 1.25 * core
    S["hard"] = np.maximum(S["hard"], 0.3 + 0.8 * verge * (1 - core))

    # -------- water (continuous scores -> anti-aliased shoreline)
    w_s = np.clip(sh_ext + wob, -4, 6)
    w_d = np.clip(dp_ext + wob, -6, 6)
    S["water_s"] = (1.6 + 10 * w_s).astype(np.float32)
    S["water_d"] = (1.6 + 10 * w_s + 2.5 * w_d).astype(np.float32)
    # land scores fade out under water/decks continuously (no boolean knock-outs ->
    # no 4px stair-steps on shorelines)
    knock = np.maximum(smoothstep(0.0, 0.7, sw), smoothstep(-0.30, 0.10, deck))
    # decks: planks win over water and land
    S["planks"] = (-2.0 + 14 * np.clip(deck + 0.15, 0, 0.6)).astype(np.float32)
    for k in ("clay", "hard", "gravel", "camp", "flag", "sage", "green", "burrow", "bone",
              "dune", "cinder", "mud", "road"):
        S[k] = (S[k] - 14.0 * knock).astype(np.float32)
    on_deck = smoothstep(-0.30, 0.10, deck)
    S["water_s"] = (S["water_s"] - 40.0 * on_deck).astype(np.float32)
    S["water_d"] = (S["water_d"] - 40.0 * on_deck).astype(np.float32)

    # -------- cliffs (continuous); cliffs win over water on the west rim
    depth_dark = smoothstep(2.0, 9.0, d_cliff_in)
    cs = 1.6 + 12 * cliff_f
    S["cliff_a"] = (cs - 1.0 * depth_dark).astype(np.float32)
    S["cliff_l"] = (cs - 1.0 - 4.0 * (1 - smoothstep(0.70, 0.85, n_big)) - 2 * depth_dark).astype(np.float32)
    S["cliff_d"] = (cs - 2.6 + 2.6 * depth_dark).astype(np.float32)
    cl_k = smoothstep(0.0, 0.30, cliff_f)          # cliffs hide everything under them, softly
    wk = smoothstep(0.0, 1.2, cliff)                # ...including the river on its far bank
    for k in list(S):
        if not k.startswith("cliff_"):
            S[k] = (S[k] - 14.0 * cl_k - (40.0 * wk if k.startswith("water_") else 0.0)).astype(np.float32)
    return S


def post(rgb, X, Y, P):
    f = P.fields
    sf = lambda a: P.sample_field(a.astype(np.float32), X, Y)
    d_co, d_ci = sf(f["d_co"]), sf(f["d_ci"])
    d_wo, d_wi = sf(f["d_wo"]), sf(f["d_wi"])
    lum_n = P.sample_field(P.noise(18.0, "lumlow", octaves=2), X, Y)
    shade = 0.93 + 0.14 * lum_n
    shade *= 1 - 0.28 * (1 - smoothstep(0.0, 1.7, d_co))
    shade *= 1 - 0.26 * smoothstep(1.5, 11.0, d_ci)
    cf = sf(f["cf"])
    lip = smoothstep(0.0, 0.03, cf) * (1 - smoothstep(0.03, 0.14, cf))
    rgb = rgb * shade[..., None] + 26 * lip[..., None]
    wet = (1 - smoothstep(0.0, 1.0, d_wo)) * smoothstep(0.0, 0.25, d_wo)
    rgb *= (1 - 0.14 * wet)[..., None]
    foam = (1 - smoothstep(0.0, 0.30, d_wo + d_wi)) * 0.30      # |signed distance| - no boolean steps
    foam = foam * (1 - smoothstep(-0.05, 0.12, cf))        # no foam under cliffs
    rgb = rgb * (1 - foam[..., None]) + np.array([225, 240, 240], np.float32) * foam[..., None]
    # decks: dark rails along the edges + a soft shadow cast on the water
    dk = sf(f["deck"])
    rail = smoothstep(-0.03, 0.03, dk) * (1 - smoothstep(0.10, 0.34, dk))
    rgb *= (1 - 0.45 * rail)[..., None]
    shadow = (1 - smoothstep(-0.03, 0.03, dk)) * (1 - smoothstep(0.0, 0.55, -dk)) * 0.35
    rgb *= (1 - shadow)[..., None]
    return rgb


def main():
    preview = None
    if "--preview" in sys.argv:
        preview = sys.argv[sys.argv.index("--preview") + 1]
    P = Painter(D.W, D.H, TEX_DIR, seed=23)
    scores = build_scores(P)
    out = ROOT / D.BAKED_DIR
    written = P.bake(MATERIALS, scores, out, chunk_tiles=20, post=post)
    print(f"baked {len(written)} chunks -> {out}")
    if preview:
        sc = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 6
        full = Image.new("RGB", (D.W * TILE_PX, D.H * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        full.resize((D.W * sc, D.H * sc), Image.LANCZOS).save(preview)
        print("preview", preview)


if __name__ == "__main__":
    main()
