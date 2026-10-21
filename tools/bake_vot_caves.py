"""
Bake The Den and Burning Blade Coven paintings.

    python3 tools/bake_vot_caves.py [den|bbc] [--preview DIR]

Same pipeline as tools/bake_vot_terrain.py (continuous painting from seamless
materials, registered as ground+water+obstacle chunks), but caves get hard
cave lighting: walls fall to near-black a few tiles in, floors darken against
walls, lava / fel pools cast coloured glow.
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

from tools import handbuilt_vot_caves as C                       # noqa: E402
from tools.terrain_painter import Painter, smoothstep, MASK_PX, TILE_PX  # noqa: E402

TEX = ROOT / "assets/tiles/vot_cluster"

DEN_MATERIALS = {
    "floor":  ("den_floor_a", "den_floor_pebble", 1.0),
    "sand":   ("den_floor_sand", None, 1.0),
    "damp":   ("den_floor_damp", None, 1.0),
    "web":    ("den_floor_web", None, 1.0),
    "nest":   ("den_floor_nest", None, 1.0),
    "water_s": ("den_water_shallow", None, 1.0),
    "water_d": ("den_water_deep", None, 1.0),
    "wall":   ("den_wall_a", "den_wall_b", 1.0),
    "roots":  ("den_wall_roots", None, 1.0),
    "bones":  ("den_wall_bones", None, 1.0),
}

BBC_MATERIALS = {
    "floor":  ("bbc_floor_a", "bbc_floor_cracks", 1.0),
    "obs":    ("bbc_floor_obsidian", None, 1.0),
    "bones":  ("bbc_floor_bones", None, 1.0),
    "grate":  ("bbc_floor_grate", None, 1.0),
    "rune_r": ("bbc_rune_red", None, 1.0),
    "rune_g": ("bbc_rune_green", None, 1.0),
    "lava":   ("bbc_floor_lava", None, 1.0),
    "fel":    ("bbc_puddle_fel", None, 1.0),
    "water_s": ("bbc_water_shallow", None, 1.0),
    "water_d": ("bbc_water_shallow", None, 1.0),
    "wall":   ("bbc_wall_a", None, 1.0),
    "crys_r": ("bbc_wall_crystal_red", None, 1.0),
    "crys_p": ("bbc_wall_crystal_purple", None, 1.0),
    "runed":  ("bbc_wall_runed", None, 1.0),
}


# ------------------------------------------------------------------ helpers
def wall_fields(P, zone):
    wall_b = np.array([[c == "rock" for c in row] for row in zone.collision_layer])
    wall_f = P.tile_mask(wall_b, 0.5, 0.22, "wallm", sigma=1.0, soft=True)    # >0 inside
    wall = wall_f > 0
    d_in = ndi.gaussian_filter(P.edt(wall) / MASK_PX, 1.0)
    d_out = ndi.gaussian_filter(P.edt(~wall) / MASK_PX, 1.0)
    return wall_f, wall, d_in, d_out


def finish_scores(S, floor_keys, wall_keys, wall_f, d_in, n_big):
    """Wall materials win inside rock; floor materials lose there. Continuous edge."""
    cs = 1.6 + 12 * np.clip(wall_f, -0.4, 0.6)
    for k in wall_keys:
        S[k] = (cs + S[k]).astype(np.float32)
    deep_in = wall_f > 0.12
    for k in floor_keys:
        S[k] = np.where(deep_in, -2.0, S[k]).astype(np.float32)
    return S


def pool_water_scores(P, S, pools, keys=("water_s", "water_d")):
    sh, dp = C.pool_fields(pools, P.gx, P.gy)
    wob = (P.noise(3.0, "poolwob" + str(len(pools)), octaves=3) - 0.5) * 0.7
    s = np.clip(sh + wob, -4, 6)
    d = np.clip(dp + wob, -6, 6)
    S[keys[0]] = (1.6 + 10 * s).astype(np.float32)
    S[keys[1]] = (1.6 + 10 * s + 10 * d).astype(np.float32)
    return s, d


def make_post(cfg):
    def post(rgb, X, Y, P):
        f = P.fields
        sf = lambda a: P.sample_field(a, X, Y)
        d_ci, d_co, cf = sf(f["d_in"]), sf(f["d_out"]), sf(f["wall_f"])
        n = sf(P.noise(14.0, "cavelum", octaves=2))
        shade = 0.88 + 0.22 * n
        # floor: occlusion against walls; wall: falls to dark inside the rock
        shade *= 1 - cfg["ao"] * (1 - smoothstep(0.0, 2.6, d_co)) * (d_co < 4)
        shade *= 1 - cfg["depth"] * smoothstep(0.25, 4.2, d_ci)
        rgb = rgb * shade[..., None]
        lip = smoothstep(0.0, 0.03, cf) * (1 - smoothstep(0.03, 0.16, cf))
        rgb = rgb + cfg["lip"] * lip[..., None] * np.array(cfg["lip_col"], np.float32)
        # water: darker toward the deep core, soft shoreline foam
        if "pool_s" in f:
            ps, pd = sf(f["pool_s"]), sf(f["pool_d"])
            rgb = rgb * (1 - cfg["deep_dark"] * smoothstep(0.0, 2.2, pd))[..., None] if pd.max() > 0 else rgb
            foam = ((ps > 0) * (1 - smoothstep(0.0, 0.30, ps))) + ((ps < 0) * (1 - smoothstep(0.0, 0.25, -ps)))
            rgb = rgb * (1 - 0.22 * foam)[..., None] + cfg["foam_col"] * (0.22 * foam)[..., None]
        for key, col, rad, amt in cfg.get("glows", []):
            g = sf(f[key])
            gl = np.exp(-np.maximum(g, 0) / rad) * (g >= 0) * amt
            rgb = rgb + gl[..., None] * np.array(col, np.float32)
        return rgb
    return post


def bake(zone, out_dir, materials, scores, fields, cfg, preview=None):
    P = scores["_P"]
    P.fields = fields
    del scores["_P"]
    out = ROOT / out_dir
    written = P.bake(materials, scores, out, chunk_tiles=20, post=make_post(cfg), hscale=0.20)
    print(f"{zone.name}: baked {len(written)} chunks -> {out}")
    if preview:
        full = Image.new("RGB", (zone.width * TILE_PX, zone.height * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        Path(preview).mkdir(parents=True, exist_ok=True)
        pth = Path(preview) / f"{zone.name.replace(' ', '_')}_full.png"
        full.resize((zone.width * 10, zone.height * 10), Image.LANCZOS).save(pth)
        print("preview", pth)


# ======================================================================= DEN
def bake_den(preview=None):
    zone, L = C.build_den()
    P = Painter(zone.width, zone.height, TEX, seed=21)
    wall_f, wall, d_in, d_out = wall_fields(P, zone)
    n_big = P.noise(9.0, "den_big", octaves=3)
    n_mid = P.noise(4.0, "den_mid", octaves=3)
    n_fine = P.noise(2.0, "den_fine", octaves=2)
    wp = P.warp("den_regions", amp_tiles=1.6, scale=9.0)
    S = {}
    # ---- floors
    S["floor"] = np.full_like(n_big, 0.50)
    S["sand"] = 0.10 + 0.95 * np.maximum(P.blob(42, 64, 9, 4.5, 0.7, wp), P.blob(42, 59, 4, 3, 0.8, wp)) * (0.6 + 0.4 * smoothstep(0.3, 0.6, n_mid))
    s_ext, d_ext = C.pool_fields(C.DEN_POOLS, P.gx, P.gy)
    shore = np.maximum(-s_ext, 0)
    S["damp"] = 0.08 + 0.95 * np.maximum(1 - smoothstep(0.5, 4.5, shore), P.blob(14, 22, 8, 6, 0.8, wp)) * (0.55 + 0.45 * smoothstep(0.2, 0.55, n_mid))
    web_zones = np.maximum.reduce([P.blob(34, 61, 4.5, 3.5, 0.9, wp), P.blob(62, 52, 8, 5, 0.8, wp),
                                   P.blob(42, 10, 12, 7, 0.8, wp), P.blob(50, 61, 4, 3, 0.9, wp)])
    S["web"] = 0.10 + 0.95 * web_zones * smoothstep(0.30, 0.52, n_mid)
    nest_zones = np.maximum.reduce([P.blob(69, 24, 8, 6, 0.8, wp), P.blob(16, 54, 7, 5, 0.8, wp),
                                    P.blob(42, 8, 7, 4.5, 0.8, wp)])
    S["nest"] = 0.12 + 0.95 * nest_zones * smoothstep(0.35, 0.58, n_fine + 0.15 * n_mid)
    # ---- walls: rock base + roots in the green north-west, bones near the husk warren / larder
    S["wall"] = np.full_like(n_big, 0.0)
    S["roots"] = -0.8 + 2.4 * np.maximum(P.blob(12, 16, 14, 12, 0.8, wp), P.blob(42, 2, 16, 6, 0.9, wp)) * smoothstep(0.35, 0.6, n_mid)
    S["bones"] = -0.9 + 2.8 * np.maximum(P.blob(8, 62, 9, 6, 0.9, wp), P.blob(70, 57, 8, 5, 0.9, wp)) * smoothstep(0.45, 0.65, n_fine)
    fs = [k for k in ("floor", "sand", "damp", "web", "nest")]
    S = finish_scores(S, fs, ["wall", "roots", "bones"], wall_f, d_in, n_big)
    # ---- water
    s, d = pool_water_scores(P, S, C.DEN_POOLS)
    inw = s > 0.45
    for k in fs:
        S[k] = np.where(inw, -2.0, S[k]).astype(np.float32)
    S["_P"] = P
    fields = dict(wall_f=wall_f.astype(np.float32), d_in=d_in.astype(np.float32), d_out=d_out.astype(np.float32),
                  pool_s=s.astype(np.float32), pool_d=d.astype(np.float32))
    cfg = dict(ao=0.42, depth=0.88, lip=26, lip_col=(1.0, 0.82, 0.62), deep_dark=0.35,
               foam_col=np.array([200, 235, 235], np.float32), glows=[])
    bake(zone, C.BAKED_DEN, DEN_MATERIALS, S, fields, cfg, preview)


# ======================================================================= BBC
def bake_bbc(preview=None):
    zone, L = C.build_bbc()
    P = Painter(zone.width, zone.height, TEX, seed=33)
    wall_f, wall, d_in, d_out = wall_fields(P, zone)
    n_big = P.noise(9.0, "bbc_big", octaves=3)
    n_mid = P.noise(4.0, "bbc_mid", octaves=3)
    n_fine = P.noise(2.0, "bbc_fine", octaves=2)
    wp = P.warp("bbc_regions", amp_tiles=1.4, scale=8.0)
    S = {}
    lava_b = np.array([[b == "lava" for b in row] for row in zone.base_layer])
    lava_f = P.tile_mask(lava_b, 0.5, 0.18, "lavam", sigma=0.9, soft=True)
    lava = lava_f > 0
    d_lava = ndi.gaussian_filter(P.edt(~lava) / MASK_PX, 1.0)
    # ---- floors
    S["floor"] = np.full_like(n_big, 0.50)
    S["floor"] = S["floor"] + 0.0
    S["obs"] = 0.05 + 1.0 * np.maximum.reduce([P.blob(50, 60, 11, 7.5, 0.6, wp), P.blob(79, 63, 10, 7, 0.6, wp),
                                               P.blob(78, 47, 13, 9, 0.6, wp), P.blob(50, 16, 8, 5, 0.6, wp),
                                               P.blob(50, 78, 10, 4, 0.7, wp)]) * (0.7 + 0.3 * n_mid)
    S["bones"] = 0.02 + 1.0 * np.maximum(P.blob(20, 63, 7, 5, 0.9, wp), P.blob(50, 17, 5, 3, 0.9, wp)) * smoothstep(0.38, 0.55, n_fine + 0.2 * n_mid)
    S["grate"] = -0.5 + 2.2 * P.blob(50, 76.5, 4.5, 1.8, 0.7, wp)
    S["rune_r"] = -0.3 + 2.4 * P.blob(78, 48, 5.4, 4.2, 0.5, wp)
    S["rune_g"] = -0.3 + 2.4 * P.blob(50, 33.5, 4.6, 3.2, 0.5, wp)
    # lava + glow handled by score (continuous) and post glow
    S["lava"] = (1.4 + 10 * np.clip(lava_f, -0.4, 0.6)).astype(np.float32)
    # ---- walls
    S["wall"] = np.full_like(n_big, 0.0)
    red = np.maximum(P.blob(78, 46, 17, 13, 0.8, wp), P.blob(50, 58, 20, 12, 0.8, wp))
    pur = np.maximum(P.blob(22, 26, 16, 12, 0.8, wp), P.blob(50, 36, 18, 11, 0.8, wp))
    rud = np.maximum.reduce([P.blob(50, 78, 14, 8, 0.8, wp), P.blob(21, 63, 13, 9, 0.8, wp), P.blob(79, 64, 13, 9, 0.8, wp)])
    S["crys_r"] = -0.6 + 2.4 * red * smoothstep(0.30, 0.55, n_mid)
    S["crys_p"] = -0.6 + 2.4 * pur * smoothstep(0.30, 0.55, n_fine + 0.2 * n_mid)
    S["runed"] = -0.6 + 2.6 * rud * smoothstep(0.35, 0.6, n_big)
    fs = ["floor", "obs", "bones", "grate", "rune_r", "rune_g"]
    S = finish_scores(S, fs, ["wall", "crys_r", "crys_p", "runed"], wall_f, d_in, n_big)
    # lava wins only on lava tiles; floors lose there
    for k in fs:
        S[k] = np.where(lava_f > 0.05, -2.0, S[k]).astype(np.float32)
    S["lava"] = np.where(wall_f > 0.1, -2.0, S["lava"]).astype(np.float32)
    # ---- pools: fel puddle (shallow) + dark pool (deep)
    fs_ext, _ = C.pool_fields(C.BBC_FEL_POOLS, P.gx, P.gy)
    wob = (P.noise(3.0, "felwob", octaves=3) - 0.5) * 0.6
    fel = np.clip(fs_ext + wob, -4, 6)
    S["fel"] = (1.6 + 10 * fel).astype(np.float32)
    for k in fs:
        S[k] = np.where(fel > 0.45, -2.0, S[k]).astype(np.float32)
    ds, dd = pool_water_scores(P, S, C.BBC_DARK_POOLS)
    for k in fs:
        S[k] = np.where(ds > 0.45, -2.0, S[k]).astype(np.float32)
    S["fel"] = np.where(ds > -1, -2.0, S["fel"]).astype(np.float32)
    S["_P"] = P
    fields = dict(wall_f=wall_f.astype(np.float32), d_in=d_in.astype(np.float32), d_out=d_out.astype(np.float32),
                  pool_s=ds.astype(np.float32), pool_d=dd.astype(np.float32),
                  d_lava=d_lava.astype(np.float32), d_fel=np.maximum(-fs_ext, 0).astype(np.float32))
    cfg = dict(ao=0.50, depth=0.90, lip=34, lip_col=(1.0, 0.45, 0.30), deep_dark=0.55,
               foam_col=np.array([140, 170, 190], np.float32),
               glows=[("d_lava", (150, 52, 10), 2.4, 0.9), ("d_fel", (14, 100, 18), 2.8, 0.8)])
    bake(zone, C.BAKED_BBC, BBC_MATERIALS, S, fields, cfg, preview)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    if pv and pv in args:
        args.remove(pv)
    which = args or ["den", "bbc"]
    if "den" in which:
        bake_den(pv)
    if "bbc" in which:
        bake_bbc(pv)
