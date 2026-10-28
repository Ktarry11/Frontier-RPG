"""
Bake Southern Thousand Needles.

    PYTHONPATH=. python3 tools/bake_southern_needles.py [--preview OUT.png]

Paints from the real sliced set (assets/tiles/southern_needles/materials, 47 tiles) rather than the
recoloured Valley-of-Trials stand-ins the other Barrens zones still run on.

PAINTED BY ELEVATION, BECAUSE THE ZONE IS ONLY TWO HEIGHTS.

The Aspen Wilderness needed a whole thaw-and-drainage model to decide its ground. This zone does not,
and pretending otherwise would be dishonest about the landform. Thousand Needles is a floor and a set of
tops with a hard edge between them, so the palette is three bands and a few overlays:

    THE TOPS    wind-scoured hardpan, pale sandstone, orange lichen on bare stone. Dry and thin, because
                nothing holds soil up there.
    THE RIM     layered and iron-banded sandstone, crumbling edges, scree and rubble at the foot. This is
                the only band with any vertical information in it and it does all the work of saying
                "cliff" from directly above.
    THE FLOOR   red sand, cracked mud, dust drift, hoof-churned ground. Wash gravel and salt crust where
                the dry channels run.

Two bands sit across that:
    THE ASPEN TAIL in the north - row 5 of the sheet, which is aspen litter lying ON red soil. It is the
                last of the overlay and it stops at a hard line.
    THE SEAM itself, painted as a one-tile band and not a gradient, same as the Aspen Wilderness's.

sn_undercut is deliberately NOT used as a field material. It is a shadowed overhang and reads as a scene;
at field weights it tiles as a repeating cave mouth. It earns its place only directly under a rim.

LIGHTING. The hillshade reads the gradient of the TILE-grid elevation, precomputed in build_scores and
sampled in post(). Differencing elevation across PIXELS is the bug that quietly halved the brightness of
the entire Aspen Wilderness - at 32 px to a tile the gradient came out near zero and the shade term
pinned flat. A mesa zone would show it even worse, because here the gradient is the whole picture.
"""
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools.terrain_painter import Painter, smoothstep, TILE_PX         # noqa: E402

TEX_DIR = ROOT / "assets/tiles/southern_needles/materials"
ZONES = {"southern_needles": "tools.handbuilt_southern_needles"}

MATERIALS = {
    # --- mesa tops
    "hardpan":   ("sn_hardpan", "sn_dust_pebbles", 1.0),
    "pale":      ("sn_sandstone_pale", "sn_polished_shelf", 1.0),
    "lichen":    ("sn_lichen_orange", "sn_gravel_scatter", 1.0),
    "topgrass":  ("sn_dry_grass", "sn_cracked_clay", 1.0),
    # --- the rim
    "layered":   ("sn_layered_stone", "sn_iron_banded", 1.0),
    "crumble":   ("sn_crumbling_rim", "sn_stone_cracks", 1.0),
    "scree":     ("sn_scree", "sn_rubble_base", 1.0),
    "undercut":  ("sn_undercut", None, 1.0),
    # --- the floor
    "redsand":   ("sn_red_sand", "sn_rippled_sand", 1.0),
    "drymud":    ("sn_dry_mud", "sn_cracked_clay", 1.0),
    "drift":     ("sn_dust_drift", "sn_hoof_churned", 1.0),
    "scrub":     ("sn_desert_scrub", "sn_dry_grass", 1.0),
    # --- the dry channels
    "washgrav":  ("sn_wash_gravel", "sn_gravel_scatter", 1.0),
    "salt":      ("sn_salt_crust", "sn_salt_rime", 1.0),
    # --- the aspen tail and the seam
    "duff":      ("sn_duff_on_red", "sn_leaves_sandstone", 1.0),
    "needle":    ("sn_needle_sand", "sn_pine_duff", 1.0),
    "mixgrass":  ("sn_grass_dirt_mix", "sn_root_cracked", 1.0),
    "shaded":    ("sn_shaded_red", None, 1.0),
    "seam":      ("sn_seam_line", None, 1.0),
    # --- roads
    "road":      ("sn_packed_path", None, 1.0),
    "verge":     ("sn_hoof_churned", None, 1.0),
    # --- water
    "pool_s":    ("sn_pool_shallow", "sn_wet_sand", 1.0),
    "pool_d":    ("sn_pool_deep", None, 1.0),
    "reeds":     ("sn_reed_bed", "sn_damp_soil", 1.0),
    "spring":    ("sn_spring_grass", "sn_mossy_stone", 1.0),
    # --- cliff faces
    "cliff_a":   ("sn_iron_banded", "sn_layered_stone", 1.0),
    "cliff_d":   ("sn_crumbling_rim", "sn_stone_cracks", 1.0),
}
LAND = ("hardpan", "pale", "lichen", "topgrass", "layered", "crumble", "scree", "undercut",
        "redsand", "drymud", "drift", "scrub", "washgrav", "salt",
        "duff", "needle", "mixgrass", "shaded", "seam", "road", "verge")


def build_scores(P, M):
    S = {}
    gx, gy = P.gx, P.gy
    n_big = P.noise(11.0, "big", octaves=3)
    n_mid = P.noise(4.5, "mid", octaves=3)
    n_fine = P.noise(1.9, "fine", octaves=2)

    f = M.fields(gx, gy)
    cliff = f["cliff"].astype(np.float32)
    water = f["shallow"].astype(np.float32)
    deep = f["deep"].astype(np.float32)

    elev = M.elevation(gx, gy).astype(np.float32)
    slope = M._slope(gx, gy).astype(np.float32)
    wash = np.clip(M._wash(gx, gy), 0, None).astype(np.float32)

    # The three bands. A mesa's drop happens inside 0.14 of its radius, so `rim` is narrow by construction
    # and does not need a tuned threshold - it is wherever the ground is doing anything at all.
    top = smoothstep(5.0, 9.0, elev)
    rim = smoothstep(0.9, 2.4, slope)
    floor = (1.0 - top) * (1.0 - rim)
    aspen = smoothstep(M.ASPEN_Y + 8.0, M.ASPEN_Y - 10.0, gy)      # 1 in the aspen tail, 0 south of it

    cliff_f = np.clip(cliff * 0.5, -0.4, 0.6).astype(np.float32)
    dzdx = (M.elevation(gx + 1.0, gy) - M.elevation(gx - 1.0, gy)).astype(np.float32) * 0.5
    dzdy = (M.elevation(gx, gy + 1.0) - M.elevation(gx, gy - 1.0)).astype(np.float32) * 0.5
    P.fields = dict(cliff=cliff, cf=cliff_f, water=water, deep=deep, elev=elev, slope=slope,
                    top=top, rim=rim, dzdx=dzdx, dzdy=dzdy)

    # ---- THE TOPS: thin, dry and bare. Nothing holds soil up there and the palette should say so.
    S["hardpan"] = 0.30 + 1.25 * top * (0.55 + 0.45 * n_big)
    S["pale"] = 0.10 + 1.38 * top * smoothstep(0.40, 0.70, n_mid)
    S["lichen"] = 0.05 + 1.30 * top * smoothstep(0.54, 0.80, n_fine)
    S["topgrass"] = 0.05 + 1.20 * top * smoothstep(0.50, 0.78, n_big)

    # ---- THE RIM: the only band with vertical information in it, and it does all the work of saying
    # "this is a cliff" to a player looking straight down.
    S["layered"] = 0.10 + 1.60 * rim * (0.6 + 0.4 * n_mid)
    S["crumble"] = 0.05 + 1.35 * rim * smoothstep(0.45, 0.78, n_fine)
    S["scree"] = 0.05 + 1.30 * smoothstep(0.55, 0.95, slope) * (1 - top) * (0.5 + 0.5 * n_mid)
    # sn_undercut is a SCENE, not a field - see the module docstring. It only wins in a thin band right
    # under a rim, where a shadowed overhang is exactly what is there.
    S["undercut"] = -0.6 + 2.2 * rim * (1 - top) * smoothstep(0.86, 0.97, n_fine)

    # ---- THE FLOOR
    S["redsand"] = 0.25 + 1.05 * floor * (0.5 + 0.5 * n_big)
    S["drymud"] = 0.08 + 1.32 * floor * smoothstep(0.40, 0.70, n_mid)
    S["drift"] = 0.05 + 1.28 * floor * smoothstep(0.44, 0.74, n_fine)
    S["scrub"] = 0.05 + 1.22 * floor * smoothstep(0.48, 0.78, n_big)

    # ---- THE DRY CHANNELS. Thousand Needles floods once, hard, then is dry for a year; the washes are
    # what the water left and they are the only lines on the floor with any shape.
    # MEASURED, not guessed: at smoothstep(0.6, 1.5) the gravel won 14.9% of all dry land and the bake
    # came out as broad grey bands that read like rivers. The wash field peaks around 2.2, so the
    # channel BOTTOM is the top quarter of it and nothing else is.
    S["washgrav"] = 0.05 + 1.10 * smoothstep(1.30, 2.05, wash) * (1 - top)
    S["salt"] = 0.02 + 1.20 * smoothstep(1.70, 2.15, wash) * smoothstep(0.50, 0.80, n_mid) * (1 - top)

    # ---- THE ASPEN TAIL. Row 5 of the sheet is aspen litter lying ON red soil, which is the whole idea
    # of the band: the overlay is thinning out and the ground underneath is already Azeroth's.
    S["duff"] = -0.3 + 2.30 * aspen * (0.55 + 0.45 * n_big)
    S["needle"] = -0.3 + 2.00 * aspen * smoothstep(0.48, 0.80, n_mid)
    S["mixgrass"] = -0.3 + 1.85 * aspen * smoothstep(0.55, 0.84, n_fine)
    S["shaded"] = -0.3 + 1.70 * aspen * smoothstep(0.70, 0.92, n_mid)
    for k in ("redsand", "drymud", "drift", "scrub"):
        S[k] = S[k] - 2.6 * aspen

    # ---- THE SEAM: a one-tile band, not a gradient. The Integration did not blend.
    band = smoothstep(2.6, 0.0, np.abs(gy - M.ASPEN_Y))
    S["seam"] = -0.5 + 3.0 * band

    for k in LAND:
        S.setdefault(k, np.full_like(n_big, -9.0))

    core, verge, _ = P.road_field(list(M.ROADS.values()))
    S["road"] = (0.05 + 1.5 * core).astype(np.float32)
    S["verge"] = np.maximum(0.05, 0.25 + 0.9 * verge * (1 - core)).astype(np.float32)

    wetmask = (water > 0.0).astype(np.float32)
    S["pool_s"] = np.clip(1.6 * water, -9.0, 9.0).astype(np.float32)
    S["pool_d"] = np.clip(1.8 * deep, -9.0, 9.0).astype(np.float32) - 0.4
    S["reeds"] = (1.5 * water - 0.3 + 0.9 * smoothstep(0.55, 0.85, n_mid)
                  - 14.0 * (1 - wetmask)).astype(np.float32)
    # the spring margin: the only green on the floor, and it is three tiles wide
    S["spring"] = (1.2 * smoothstep(-2.5, 0.2, water) - 0.45 - 9.0 * wetmask).astype(np.float32)
    for k in LAND:
        S[k] = (S[k] - 12.0 * wetmask).astype(np.float32)

    depth_dark = smoothstep(2.0, 9.0, np.maximum(cliff, 0))
    cs = 1.6 + 12 * cliff_f
    S["cliff_a"] = (cs - 1.0 * depth_dark).astype(np.float32)
    S["cliff_d"] = (cs - 2.2 + 2.6 * depth_dark).astype(np.float32)
    cl_k = smoothstep(0.0, 0.30, cliff_f)
    for k in list(S):
        if not k.startswith("cliff_"):
            S[k] = (S[k] - 14.0 * cl_k).astype(np.float32)
    for k in MATERIALS:
        S.setdefault(k, np.full_like(S["hardpan"], -9.0))
    P.scores = S
    return S


def post(rgb, X, Y, P):
    """Light the mesas. In a zone that is two flat heights, the shading IS the elevation cue."""
    f = P.fields
    sf = lambda a: P.sample_field(a.astype(np.float32), X, Y)          # noqa: E731
    elev, top = sf(f["elev"]), sf(f["top"])
    lum = P.sample_field(P.noise(13.0, "lum", octaves=2), X, Y)

    out = rgb * (0.93 + 0.07 * lum)[..., None]

    # HILLSHADE from the TILE-grid gradient (see the module docstring on the pixel-vs-tile bug). On a mesa
    # this is nearly everything: top and floor are both flat, so without it the only thing separating a
    # plateau from the ground beside it is a slight hue change.
    gxs, gys = sf(f["dzdx"]), sf(f["dzdy"])
    shade = np.clip(1.0 + 0.55 * (-gxs * 0.70 - gys * 0.70), 0.55, 1.55)
    out = out * shade[..., None]

    # The tops catch more sun and more wind. Lifting them a little is what makes the skyline read.
    out = out * (0.97 + 0.16 * top)[..., None]

    # Warm the whole zone - this is red rock country and the sheet is already warm, so this is a nudge.
    out = out * np.array([1.04, 0.99, 0.94], np.float32)

    wd = sf(f["water"])
    depth = smoothstep(0.4, 4.0, wd)
    out = out * (1 - 0.28 * depth[..., None]) + np.array([40, 92, 96], np.float32) * 0.34 * depth[..., None]

    cf = sf(f["cf"])
    lip = smoothstep(0.0, 0.03, cf) * (1 - smoothstep(0.03, 0.14, cf))
    out = out + 16 * lip[..., None] * np.array([0.98, 0.88, 0.74], np.float32)
    return np.clip(out, 0, 255)


def bake(key, preview=None, sc=4):
    import importlib
    M = importlib.import_module(ZONES[key])
    P = Painter(M.W, M.H, TEX_DIR, seed=getattr(M, "SEED", 733))
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


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    for k in ([a for a in sys.argv[1:] if a in ZONES] or list(ZONES)):
        bake(k, pv)
