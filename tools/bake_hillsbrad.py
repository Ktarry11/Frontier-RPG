"""
Bake the Hillsbrad Foothills paintings (eastern and western halves) from the green materials in assets/tiles/hillsbrad/materials (hb_*.png).

    python3 tools/bake_hillsbrad.py hillsbrad_east|hillsbrad_west|all [--preview out.png] [--scale 6]

Same contract as tools/bake_silverpine.py - the zone module supplies fields() (the SAME functions the tile grid is built
from), BASE, PAINT, paved(), COBBLE, sea_field() - but with two deliberate differences, both from Kyle's "hillsbrand is
still kind of green. This is classic wow":

  1. The BASE is GRASS, not forest floor. Silverpine's base is a pine-needle mat with grass painted on top, which is why
     that zone reads brown-olive from the air. Hillsbrad inverts it: green grass everywhere, with the oak stands and
     ferns painted ON, so the default state of any unpainted tile is healthy pasture.
  2. The post() grade is WARM. Silverpine ends on `rgb * [0.95, 0.99, 1.03]`, a cold blue cast that sells the plague.
     Applying that here would undo the palette, so Hillsbrad uses a warm, slightly green-biased grade instead - the
     same trick pointed the other way.

The dry khaki meadow (`hb_dry`) is the one Silverpine material kept for ground cover, and PAINT only ever places it on
the high northern foothills, so elevation reads without the zone reading as blighted.
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

TEX_DIR = ROOT / "assets/tiles/hillsbrad/materials"
ZONES = {"hillsbrad_east": "tools.handbuilt_hillsbrad_east",
         "hillsbrad_west": "tools.handbuilt_hillsbrad_west",
         # The town baker is the same baker: Tarren Mill is Hillsbrad country, so it paints from the same green
         # material set rather than getting a palette of its own that would drift out of step with the zone
         # the player walks in from.
         "tarren_mill": "tools.handbuilt_tarren_mill",
         # ARATHI shares this baker on purpose. It is the zone next door and the same country - the
         # hb_* materials ARE the Lordaeron set - and giving Arathi a palette of its own would let the
         # two drift apart at a border the player walks across. The difference between them is carried
         # entirely by each module's own BASE weights: Hillsbrad is 62% grass, Arathi West is 46% dry
         # and 20% rocky. The green stops at the wall because the mix changes, not because the
         # materials do.
         "arathi_west": "tools.handbuilt_arathi_west",
         "arathi_central": "tools.handbuilt_arathi_central",
         "arathi_east": "tools.handbuilt_arathi_east"}

MATERIALS = {
    "grass":   ("hb_grass", "hb_grass2", 1.0),
    "meadow":  ("hb_meadow", "hb_meadow2", 1.0),
    "forest":  ("hb_forest", "hb_forest2", 1.0),
    "fern":    ("hb_fern", None, 1.0),
    "dry":     ("hb_dry", None, 1.0),
    "rocky":   ("hb_rocky", "hb_moss_rock", 1.0),
    "earth":   ("hb_earth", None, 1.0),
    "field":   ("hb_field", None, 1.0),
    "cobble":  ("hb_cobble", "hb_flagstone", 1.0),
    "gravel":  ("hb_gravel", None, 1.0),
    "road":    ("hb_road", None, 1.0),
    "verge":   ("hb_verge", None, 1.0),
    "planks":  ("hb_planks", "hb_pier", 1.0),
    "shore":   ("hb_shore", "hb_wet_sand", 1.0),
    "marsh":   ("hb_marsh", None, 1.0),
    "pool_s":  ("hb_pool_shallow", None, 1.0),
    "pool_d":  ("hb_pool_deep", None, 1.0),
    "sea_s":   ("hb_sea_shallow", None, 1.0),
    "sea_d":   ("hb_sea_deep", None, 1.0),
    "cliff_a": ("hb_cliff_a", "hb_cliff_b", 1.0),
    "cliff_d": ("hb_rock_wall", None, 1.0),
}
LAND = ("grass", "meadow", "forest", "fern", "dry", "rocky", "earth", "field", "cobble", "gravel",
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
    water = f["shallow"].astype(np.float32)
    deep = f["deep"].astype(np.float32)
    deck = f["deck"].astype(np.float32)
    cliff_f = np.clip(cliff * 0.5, -0.4, 0.6).astype(np.float32)
    d_co = ndi.gaussian_filter(np.maximum(-cliff, 0), 1.2)
    d_ci = ndi.gaussian_filter(np.maximum(cliff, 0), 1.2)
    # Arathi East names its open water water_field rather than sea_field (it has no inland pools
    # to distinguish it from), so fall back to that - without it the whole archipelago paints as
    # grass with a blue tile grid on top.
    _sea = getattr(M, "sea_field", None) or (getattr(M, "water_field", None)
                                             if getattr(M, "KEY", "") == "arathi_east" else None)
    sea = _sea(gx, gy).astype(np.float32) if _sea else np.full_like(cliff, -99.0)
    P.fields = dict(cliff=cliff, d_co=d_co, d_ci=d_ci, cf=cliff_f, water=water, deep=deep, sea=sea)

    # Base: GREEN PASTURE, with oak-stand floor and fern painted on top of it.
    base = getattr(M, "BASE", {"grass": 0.62, "forest": 0.22, "fern": 0.16, "rocky": 0.12})
    S["grass"] = np.full_like(n_big, 0.60)
    S["forest"] = 0.08 + 0.80 * base.get("forest", 0.22) / 0.22 * smoothstep(0.55, 0.80, n_big) * 0.9
    S["fern"] = 0.05 + 0.60 * base.get("fern", 0.16) / 0.16 * smoothstep(0.66, 0.88, n_mid) * (0.6 + 0.4 * n_fine)
    S["rocky"] = 0.05 + 0.40 * base.get("rocky", 0.12) / 0.12 * smoothstep(0.68, 0.86, n_mid)
    near_rim = smoothstep(-6.0, -1.0, cliff)
    S["rocky"] = np.maximum(S["rocky"], 0.2 + 0.95 * near_rim)
    # Scree at the mountain foot is rock and dry grass, never the lush stuff.
    S["dry"] = np.maximum(np.full_like(n_big, -9.0), 0.1 + 0.5 * near_rim * smoothstep(0.45, 0.75, n_mid))
    for k in LAND:
        S.setdefault(k, np.full_like(n_big, -9.0))

    # hand-placed districts
    for mat, blobs in getattr(M, "PAINT", {}).items():
        cur = np.maximum(S[mat], 0.05)
        for (cx, cy, rx, ry, st) in blobs:
            b = P.blob(cx, cy, rx, ry, 0.6, wp)
            # Worked/broken ground gets a noisier edge than pasture, so farm
            # plots look ploughed rather than airbrushed on.
            if mat in ("field", "earth", "dry"):
                b = b * (0.6 + 0.4 * smoothstep(0.3, 0.6, n_mid))
            cur = np.maximum(cur, 0.10 + 1.25 * b * st)
        S[mat] = cur.astype(np.float32)
    if hasattr(M, "paved"):
        pv = smoothstep(-0.3, 1.2, M.paved(gx, gy).astype(np.float32))
        S["cobble"] = np.maximum(np.maximum(S["cobble"], 0.05), 0.12 + 1.35 * pv).astype(np.float32)
    for (cx, cy, rx, ry, st) in getattr(M, "COBBLE", []):
        S["cobble"] = np.maximum(np.maximum(S["cobble"], 0.05), 0.12 + 1.35 * P.blob(cx, cy, rx, ry, 0.6, wp) * st)

    # roads
    core, verge, _ = P.road_field(list(M.ROADS.values()))
    S["road"] = (0.05 + 1.3 * core).astype(np.float32)
    S["verge"] = np.maximum(0.05, 0.25 + 0.9 * verge * (1 - core)).astype(np.float32)

    # water: driven by the same field as the tile grid. Sand at the sea, a
    # little marsh only at the inland ponds.
    wet = (water > 0.0).astype(np.float32)
    is_sea = (sea >= water - 0.6).astype(np.float32)
    bank = smoothstep(-1.4, 0.0, water)
    S["shore"] = np.maximum(S["shore"], 0.05 + 1.40 * smoothstep(-1.2, 0.05, water) * (0.30 + 0.70 * is_sea)).astype(np.float32)
    S["marsh"] = np.maximum(S["marsh"], 0.05 + 0.55 * bank * (1 - is_sea) * (0.5 + 0.5 * n_mid)).astype(np.float32)
    sh = np.clip(1.6 * water, -9.0, 9.0).astype(np.float32)
    S["pool_s"] = np.where(is_sea > 0.5, -9.0, sh).astype(np.float32)
    S["sea_s"] = np.where(is_sea > 0.5, sh, -9.0).astype(np.float32)
    dp = np.clip(1.8 * deep, -9.0, 9.0).astype(np.float32)
    S["pool_d"] = np.where(is_sea > 0.5, -9.0, dp - 0.4).astype(np.float32)
    S["sea_d"] = np.where(is_sea > 0.5, dp - 0.4, -9.0).astype(np.float32)
    for k in LAND:
        S[k] = (S[k] - 12.0 * wet).astype(np.float32)

    # decks (Southshore's quay) over water
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
        S.setdefault(k, np.full_like(S["grass"], -9.0))
    return S


def post(rgb, X, Y, P):
    f = P.fields
    sf = lambda a: P.sample_field(a.astype(np.float32), X, Y)
    d_co, d_ci = sf(f["d_co"]), sf(f["d_ci"])
    lum_n = P.sample_field(P.noise(14.0, "lumlow", octaves=2), X, Y)
    shade = 0.93 + 0.11 * lum_n
    shade *= 1 - 0.28 * (1 - smoothstep(0.0, 1.8, d_co))
    shade *= 1 - 0.30 * smoothstep(1.5, 9.0, d_ci)
    cf = sf(f["cf"])
    lip = smoothstep(0.0, 0.03, cf) * (1 - smoothstep(0.03, 0.14, cf))
    wd = sf(f["water"])
    depth = smoothstep(0.4, 5.5, wd)
    # Shallow sea over sand reads green-blue here rather than Silverpine's
    # near-black lake, because this coast is a beach, not a drowned bog.
    rgb = rgb * (1 - 0.50 * depth[..., None]) + np.array([10.0, 34.0, 42.0], np.float32) * 0.50 * depth[..., None]
    out = rgb * shade[..., None] + 20 * lip[..., None]
    # Warm, faintly green-biased sun - the opposite of Silverpine's cold cast.
    out = out * np.array([1.03, 1.02, 0.93], np.float32)
    return np.clip(out, 0, 255)


def bake(key, preview=None, sc=6):
    M = importlib.import_module(ZONES[key])
    P = Painter(M.W, M.H, TEX_DIR, seed=getattr(M, "SEED", 112))
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
        bake(k, preview.replace(".png", f"_{k}.png") if preview else None, sc)


if __name__ == "__main__":
    main()
