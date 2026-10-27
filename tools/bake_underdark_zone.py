"""
Bake the Crystalline Underdark's open zone.

    PYTHONPATH=. python3 tools/bake_underdark_zone.py [--preview OUT.png]

Structurally the same machinery as tools/bake_hillsbrad.py - a Painter, per-material score fields, hand-painted
districts from the layout module's PAINT, then a post-process - but the semantics are inverted at two points and
those two are the whole reason this is its own file rather than another entry in the Hillsbrad baker.

  LIGHT COMES FROM THE GROUND. Every surface baker in the game shades downward: ambient occlusion into the
  cliffs, a sun tint on top. Here the crystal, the fungus and the water are all emissive art, so the post-process
  ADDS light near the glowing materials and near water instead of darkening into them. Hillsbrad's warm
  sun multiply (1.03, 1.02, 0.93) becomes a cool cast, and the water tint lightens rather than deepens.

  THERE IS NO SKY, SO THE RIM IS NOT A HORIZON. The cliff darkening is heavier and reaches further than an
  outdoor zone's, because what the player is looking at past the galleries is a cavern wall, not distance. That
  darkness at the edges is what sells a ceiling the art never has to draw.
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

TEX_DIR = ROOT / "assets/tiles/underdark/materials"
ZONES = {"underdark": "tools.handbuilt_underdark",
         # The Bastion paints from the same material set: it is a town inside the same cavern, and giving
         # it a palette of its own would make the walk through its gate a change of world.
         "kaels_bastion": "tools.handbuilt_kaels_bastion"}

MATERIALS = {
    "cavern":  ("ud_cavern_dark", "ud_cavern_floor", 1.0),
    "fungal":  ("ud_fungal_mat", "ud_cap_litter", 1.0),
    "moss":    ("ud_spore_moss", None, 1.0),
    "glow":    ("ud_glow_lichen", None, 1.0),
    "myc":     ("ud_myc_threads", None, 1.0),
    "shard":   ("ud_shard_gravel", None, 1.0),
    "crystal": ("ud_crystal_floor_v", "ud_crystal_floor_c", 1.0),
    "lattice": ("ud_lattice_floor", None, 1.0),
    "dalaran": ("ud_dalaran_floor", "ud_dalaran_cracked", 1.0),
    "dim":     ("ud_dim_ground", None, 1.0),
    "rift":    ("ud_rift_ground", None, 1.0),
    "road":    ("ud_shard_gravel", None, 1.0),
    "verge":   ("ud_cavern_dark", None, 1.0),
    "cobble":  ("ud_bastion_floor", "ud_camp_boards", 1.0),
    "pool_s":  ("ud_lumen_shallow", None, 1.0),
    "pool_d":  ("ud_lumen_deep", None, 1.0),
    "cliff_a": ("ud_rock_wall", "ud_vein_wall", 1.0),
    "cliff_d": ("ud_crystal_wall_v", "ud_crystal_wall_c", 1.0),
}
LAND = ("cavern", "fungal", "moss", "glow", "myc", "shard", "crystal", "lattice",
        "dalaran", "dim", "rift", "road", "verge", "cobble")
#: Materials that are emissive art. The post-process lifts light out of these rather than shading into them.
EMISSIVE = ("crystal", "lattice", "rift")


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
    cliff_f = np.clip(cliff * 0.5, -0.4, 0.6).astype(np.float32)
    d_co = ndi.gaussian_filter(np.maximum(-cliff, 0), 1.2)
    d_ci = ndi.gaussian_filter(np.maximum(cliff, 0), 1.2)
    P.fields = dict(cliff=cliff, d_co=d_co, d_ci=d_ci, cf=cliff_f, water=water, deep=deep)

    base = getattr(M, "BASE", {"cavern": 0.58, "fungal": 0.20, "moss": 0.12, "shard": 0.14})
    S["cavern"] = np.full_like(n_big, 0.60)
    S["fungal"] = 0.06 + 0.80 * base.get("fungal", 0.20) / 0.20 * smoothstep(0.55, 0.80, n_big) * 0.9
    S["moss"] = 0.04 + 0.60 * base.get("moss", 0.12) / 0.12 * smoothstep(0.66, 0.88, n_mid) * (0.6 + 0.4 * n_fine)
    S["shard"] = 0.05 + 0.40 * base.get("shard", 0.14) / 0.14 * smoothstep(0.68, 0.86, n_mid)
    # Bare rock and shard gravel crowd the cavern wall; fungus does not grow hard against stone.
    near_rim = smoothstep(-3.0, -0.5, cliff)
    S["shard"] = np.maximum(S["shard"], 0.12 + 0.70 * near_rim)
    for k in LAND:
        S.setdefault(k, np.full_like(n_big, -9.0))

    for mat, blobs in getattr(M, "PAINT", {}).items():
        cur = np.maximum(S[mat], 0.05)
        for (cx, cy, rx, ry, st) in blobs:
            b = P.blob(cx, cy, rx, ry, 0.6, wp)
            # Fungal and mycelial spread gets a noisier edge than crystal, which grows to a face.
            if mat in ("fungal", "myc", "moss"):
                b = b * (0.6 + 0.4 * smoothstep(0.3, 0.6, n_mid))
            cur = np.maximum(cur, 0.10 + 1.25 * b * st)
        S[mat] = cur.astype(np.float32)

    if hasattr(M, "paved"):
        pv = smoothstep(-0.3, 1.2, M.paved(gx, gy).astype(np.float32))
        S["cobble"] = np.maximum(np.maximum(S["cobble"], 0.05), 0.12 + 1.35 * pv).astype(np.float32)
    for (cx, cy, rx, ry, st) in getattr(M, "COBBLE", []):
        S["cobble"] = np.maximum(np.maximum(S["cobble"], 0.05), 0.12 + 1.35 * P.blob(cx, cy, rx, ry, 0.6, wp) * st)

    core, verge, _ = P.road_field(list(M.ROADS.values()))
    S["road"] = (0.05 + 1.3 * core).astype(np.float32)
    S["verge"] = np.maximum(0.05, 0.25 + 0.9 * verge * (1 - core)).astype(np.float32)

    # water: glowing, so the bank gets lichen rather than mud
    wet = (water > 0.0).astype(np.float32)
    bank = smoothstep(-1.4, 0.0, water)
    S["glow"] = np.maximum(S["glow"], 0.05 + 1.20 * bank * (0.5 + 0.5 * n_mid)).astype(np.float32)
    S["pool_s"] = np.clip(1.6 * water, -9.0, 9.0).astype(np.float32)
    S["pool_d"] = np.clip(1.8 * deep, -9.0, 9.0).astype(np.float32) - 0.4
    for k in LAND:
        S[k] = (S[k] - 12.0 * wet).astype(np.float32)

    # cliffs: the cavern wall. Crystal shows through it where the zone is crystalline.
    depth_dark = smoothstep(2.0, 9.0, d_ci)
    cs = 1.6 + 12 * cliff_f
    S["cliff_a"] = (cs - 1.0 * depth_dark).astype(np.float32)
    S["cliff_d"] = (cs - 2.6 + 2.8 * depth_dark).astype(np.float32)
    cl_k = smoothstep(0.0, 0.30, cliff_f)
    for k in list(S):
        if not k.startswith("cliff_"):
            S[k] = (S[k] - 14.0 * cl_k).astype(np.float32)
    for k in MATERIALS:
        S.setdefault(k, np.full_like(S["cavern"], -9.0))
    P.scores = S
    return S


def post(rgb, X, Y, P):
    f = P.fields
    sf = lambda a: P.sample_field(a.astype(np.float32), X, Y)          # noqa: E731
    d_co, d_ci = sf(f["d_co"]), sf(f["d_ci"])
    lum_n = P.sample_field(P.noise(14.0, "lumlow", octaves=2), X, Y)

    shade = 0.84 + 0.16 * lum_n
    # Heavier and longer-reaching than an outdoor zone: what is past the galleries is a cavern wall, not
    # distance, and this darkness is what sells a ceiling the art never draws.
    shade *= 1 - 0.34 * (1 - smoothstep(0.0, 2.2, d_co))
    shade *= 1 - 0.42 * smoothstep(1.5, 11.0, d_ci)

    cf = sf(f["cf"])
    lip = smoothstep(0.0, 0.03, cf) * (1 - smoothstep(0.03, 0.14, cf))
    out = rgb * shade[..., None] + 16 * lip[..., None] * np.array([0.72, 0.78, 1.0], np.float32)

    # The water is lit from underneath, so it LIGHTENS toward the deep instead of going black.
    wd = sf(f["water"])
    depth = smoothstep(0.4, 5.5, wd)
    out = out * (1 - 0.26 * depth[..., None]) + np.array([22.0, 78.0, 104.0], np.float32) * 0.34 * depth[..., None]

    # Emissive ground pushes a little light back out, so crystal does not go grey next to a wall.
    em = None
    for k in EMISSIVE:
        if k in P.scores:
            s = sf(P.scores[k])
            em = s if em is None else np.maximum(em, s)
    if em is not None:
        glow = smoothstep(0.2, 1.1, em)
        out = out + glow[..., None] * np.array([18.0, 14.0, 40.0], np.float32)

    # Cool cast - the exact inverse of Hillsbrad's warm sun, because there is no sun.
    out = out * np.array([0.95, 0.97, 1.06], np.float32)
    return np.clip(out, 0, 255)


def bake(key, preview=None, sc=5):
    M = importlib.import_module(ZONES[key])
    P = Painter(M.W, M.H, TEX_DIR, seed=getattr(M, "SEED", 907))
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
