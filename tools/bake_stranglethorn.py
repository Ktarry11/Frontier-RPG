"""
Bake every Stranglethorn painting - the three wilderness zones and the two towns - from one jungle
material set.

    python3 tools/bake_stranglethorn.py north|central|south|gromgol|booty_bay|all
                                        [--preview out.png] [--scale 4] [--region x0,y0,x1,y1]

Landforms come from each zone module's own fields() - the SAME analytic functions the tile grid is built
from - so painting and collision cannot drift.  Wilderness zones go through the ashenvale_engine Spec
(cliff / woods / shallow / deep / deck); the two towns go through town_kit (cliff / shallow / deep /
deck plus BASE and PAINT patch lists).  Both land in this file because they share every texture.

TEXTURES ARE SYNTHESISED, and that is the point.  Kyle, 29 Oct 2026: "Start baking and building
everything without art."  Nothing here waits on a new asset: every stv_* material below is built at bake
time by cropping, recolouring and tiling an existing texture - the Echo Isles tropical set for the
jungle floor, sand, rock and water (right biome, built for the Darkspear isles), the Ashenvale forest
sheet for ferns, roots and the rocky skirt, and the Valley of Trials set for road ruts, limestone and
gravel.  Drop a real assets/tiles/stranglethorn/materials/stv_<name>.png in and it wins on the next
bake, one material at a time, with no code change.
"""
import colorsys
import importlib
import os
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools.terrain_painter import Painter, smoothstep, TILE_PX  # noqa: E402

REAL_DIR = ROOT / "assets/tiles/stranglethorn/materials"
T = ROOT / "assets/tiles"
EI, AV, VOT = T / "echo_isles/materials", T / "ashenvale", T / "vot_cluster"
SIZE = 256

WILD = {"north": "tools.handbuilt_stranglethorn_north",
        "central": "tools.handbuilt_stranglethorn_central",
        "south": "tools.handbuilt_stranglethorn_south"}
TOWN = {"gromgol": "tools.handbuilt_gromgol", "booty_bay": "tools.handbuilt_booty_bay"}

# stem -> (source file, vertical crop offset, (hue, sat, val) or None, extra)
SHEET = {
    "stv_jungle":    (EI / "echo_jungle_a.png", 0.5, None, None),
    "stv_jungle_b":  (EI / "echo_jungle_b.png", 0.5, (118, 0.72, 0.88), None),
    "stv_fern":      (AV / "forest_floor_light.png", 0.2, (104, 0.86, 0.80), None),
    "stv_root":      (AV / "forest_floor_roots.png", 0.5, (44, 0.52, 0.72), None),
    "stv_mulch":     (AV / "forest_floor_roots.png", 0.15, (26, 0.44, 0.70), None),
    "stv_rot":       (AV / "corrupted_ground.png", 0.5, (72, 0.40, 0.62), None),
    "stv_ruin":      (VOT / "vot_limestone.png", 0.3, (96, 0.26, 0.74), None),
    "stv_trampled":  (EI / "vot_hardpan.png", 0.5, (38, 0.30, 0.92), None),
    "stv_clay":      (EI / "vot_clay_a.png", 0.5, (26, 0.30, 0.78), None),
    "stv_camp":      (EI / "vot_hardpan.png", 0.2, (34, 0.38, 0.82), None),
    "stv_road":      (VOT / "vot_road_ruts_a.png", 0.5, (36, 0.36, 1.02), None),
    "stv_verge":     (VOT / "vot_road_ruts_b.png", 0.5, (44, 0.32, 0.88), None),
    "stv_rocky":     (AV / "rocky_forest_ground.png", 0.5, (84, 0.22, 0.86), None),
    "stv_stream":    (VOT / "vot_gravel.png", 0.5, (88, 0.14, 0.74), None),
    "stv_mud":       (EI / "vot_mudshore.png", 0.5, None, None),
    "stv_planks":    (EI / "vot_planks.png", 0.5, None, None),
    "stv_beach":     (EI / "echo_sand.png", 0.5, None, None),
    "stv_wet":       (EI / "echo_wetsand.png", 0.5, None, None),
    "stv_sea_s":     (EI / "vot_water_shallow.png", 0.5, None, None),
    "stv_sea_d":     (EI / "vot_water_deep.png", 0.5, None, None),
    "stv_lake_s":    (EI / "vot_water_shallow.png", 0.3, (150, 0.44, 0.88), None),
    "stv_lake_d":    (EI / "vot_water_deep.png", 0.3, (158, 0.58, 0.64), None),
    "stv_cliff_a":   (EI / "echo_rock_a.png", 0.5, None, None),
    "stv_cliff_b":   (EI / "echo_rock_b.png", 0.5, (96, 0.12, 0.84), None),
    "stv_canopy":    (EI / "echo_jungle_b.png", 0.35, (122, 0.84, 1.00), "canopy"),
}

MATERIALS = {
    "floor":   ("stv_jungle", "stv_jungle_b", 1.0),
    "fern":    ("stv_fern", None, 1.0),
    "root":    ("stv_root", None, 1.0),
    "mulch":   ("stv_mulch", None, 1.0),
    "rot":     ("stv_rot", None, 1.0),
    "ruin":    ("stv_ruin", None, 1.0),
    "hard":    ("stv_trampled", None, 1.0),
    "clay":    ("stv_clay", None, 1.0),
    "camp":    ("stv_camp", None, 1.0),
    "road":    ("stv_road", "stv_verge", 1.0),
    "verge":   ("stv_verge", None, 1.0),
    "rocky":   ("stv_rocky", None, 1.0),
    "stream":  ("stv_stream", None, 1.0),
    "mud":     ("stv_mud", None, 1.0),
    "planks":  ("stv_planks", None, 1.0),
    "beach":   ("stv_beach", None, 1.0),
    "wet":     ("stv_wet", None, 1.0),
    "sea_s":   ("stv_sea_s", None, 1.0),
    "sea_d":   ("stv_sea_d", None, 1.0),
    "lake_s":  ("stv_lake_s", None, 1.0),
    "lake_d":  ("stv_lake_d", None, 1.0),
    "cliff_a": ("stv_cliff_a", "stv_cliff_b", 1.0),
    "cliff_d": ("stv_cliff_b", None, 1.0),
    "canopy":  ("stv_canopy", None, 1.0),
    # the town modules name "jungle" in their BASE dicts; it is the same floor.
    "jungle":  ("stv_jungle", "stv_jungle_b", 1.0),
}

LAND = ("floor", "fern", "root", "mulch", "rot", "ruin", "hard", "clay", "camp", "road", "verge",
        "rocky", "mud", "beach", "wet", "jungle")


# --------------------------------------------------------------------------- material synthesis
def _recolour(a, hue, sat, val):
    lum = a.mean(2)
    v = np.clip(lum, 0, 1) * val
    r, g, b = colorsys.hsv_to_rgb(hue / 360.0, 1.0, 1.0)
    tint = v[..., None] * np.array([r, g, b], np.float32)[None, None, :]
    gray = np.repeat(v[..., None], 3, 2)
    return gray * (1 - sat) + tint * sat


def _seamless(a):
    n = a.shape[0]
    b = np.roll(a, (n // 2, n // 2), axis=(0, 1))
    t = (np.arange(n, dtype=np.float32) + 0.5) / n
    wx = 0.5 - 0.5 * np.cos(2 * np.pi * t)
    wgt = np.sqrt(np.outer(wx, wx))[..., None]
    return a * wgt + b * (1 - wgt)


def synth(stem, seed=11):
    path, off, rec, extra = SHEET[stem]
    im = Image.open(path).convert("RGB")
    w, h = im.size
    s = min(w, h) - 6
    x0 = (w - s) // 2
    y0 = int((h - s) * off)
    im = im.crop((x0, y0, x0 + s, y0 + s)).resize((SIZE, SIZE), Image.LANCZOS)
    a = np.asarray(im, np.float32) / 255.0
    if rec is not None:
        a = _recolour(a, *rec)
    a = _seamless(a)
    if extra == "canopy":
        rng = np.random.default_rng(seed + sum(map(ord, stem)))
        lobes = ndi.gaussian_filter(rng.random((SIZE, SIZE)).astype(np.float32), 5.0, mode="wrap")
        lobes = (lobes - lobes.min()) / (lobes.max() - lobes.min() + 1e-6)
        fine = ndi.gaussian_filter(rng.random((SIZE, SIZE)).astype(np.float32), 1.6, mode="wrap")
        fine = (fine - fine.min()) / (fine.max() - fine.min() + 1e-6)
        a = a * (0.55 + 0.80 * (lobes > 0.50) * (0.40 + 0.60 * fine))[..., None]
    return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))


def build_material_dir():
    tmp = Path(tempfile.mkdtemp(prefix="stv_mat_"))
    provisional = []
    for stem in SHEET:
        real = REAL_DIR / f"{stem}.png"
        if real.exists():
            Image.open(real).convert("RGB").resize((SIZE, SIZE), Image.LANCZOS).save(tmp / f"{stem}.png")
            continue
        synth(stem).save(tmp / f"{stem}.png")
        provisional.append(stem)
    return tmp, provisional


# --------------------------------------------------------------------------- shared helpers
def _patches(P, wp, blobs, soft=0.8):
    if not blobs:
        return None
    return np.maximum.reduce([P.blob(cx, cy, rx, ry, soft, wp) for (cx, cy, rx, ry) in blobs])


def _water_split(P, M, S, sh, dp, wob, n_fine, d_out, is_sea):
    w_s = np.clip(sh + wob, -4, 6)
    w_d = np.clip(dp + wob, -6, 6)
    base_s = (1.6 + 10 * w_s).astype(np.float32)
    base_d = (1.6 + 10 * w_s + 2.5 * w_d).astype(np.float32)
    off = np.float32(-40.0)
    S["sea_s"] = np.where(is_sea, base_s, off).astype(np.float32)
    S["sea_d"] = np.where(is_sea, base_d, off).astype(np.float32)
    S["lake_s"] = np.where(is_sea, off, base_s).astype(np.float32)
    S["lake_d"] = np.where(is_sea, off, base_d).astype(np.float32)
    sea_out = np.where(is_sea, d_out, 99.0)
    lake_out = np.where(is_sea, 99.0, d_out)
    S["beach"] = (0.06 + 1.0 * (1 - smoothstep(1.0, 8.0, sea_out))
                  * (0.6 + 0.4 * smoothstep(0.25, 0.6, n_fine))).astype(np.float32)
    S["wet"] = (0.06 + 1.1 * (1 - smoothstep(0.3, 1.7, sea_out))).astype(np.float32)
    S["mud"] = (0.08 + 1.1 * (1 - smoothstep(0.35, 2.2, lake_out))
                * (0.75 + 0.25 * n_fine)).astype(np.float32)


# --------------------------------------------------------------------------- wilderness zones
def build_scores_wild(P, M):
    S = {}
    gx, gy = P.gx, P.gy
    spec = M.SPEC
    wp = P.warp("regions", amp_tiles=2.4, scale=13.0)
    n_big = P.noise(11.0, "big", octaves=3)
    n_big2 = P.noise(14.0, "big2", octaves=3)
    n_mid = P.noise(5.0, "mid", octaves=3)
    n_fine = P.noise(2.0, "fine", octaves=2)

    F = spec.fields(gx, gy)
    wob = (P.noise(3.0, "shorewob", octaves=3) - 0.5) * 0.9
    sh, dp = F["shallow"].astype(np.float32), F["deep"].astype(np.float32)
    cliff = F["cliff"].astype(np.float32)
    woods = F["woods"].astype(np.float32)
    deck = F["deck"].astype(np.float32)

    # tiles sealed by seal_unreachable must LOOK like walls, not like a lawn you cannot step on
    sl, sw_t = getattr(P, "sealed_land", None), getattr(P, "sealed_water", None)
    if sl:
        g = np.zeros((P.H, P.W), np.float32)
        for (x, y) in sl:
            g[y, x] = 1.0
        m = P.tile_mask(g, threshold=0.5, noise_amp=0.10, key="sealland", sigma=0.9, soft=True).astype(np.float32)
        woods = np.where(m > 0.02, np.maximum(woods, 1.2), woods).astype(np.float32)
    if sw_t:
        g = np.zeros((P.H, P.W), np.float32)
        for (x, y) in sw_t:
            g[y, x] = 1.0
        m = P.tile_mask(g, threshold=0.5, noise_amp=0.10, key="sealwater", sigma=0.9, soft=True).astype(np.float32)
        dp = np.maximum(dp, 1.4 * m + 0.2).astype(np.float32)

    cliff_f = np.clip(cliff * 0.5, -0.4, 0.6).astype(np.float32)
    woods_f = np.clip(woods * 0.5, -0.4, 0.6).astype(np.float32)
    swv = (sh + wob).astype(np.float32)
    d_wo, d_wi = np.maximum(-swv, 0), np.maximum(swv, 0)
    d_co = ndi.gaussian_filter(np.maximum(-cliff, 0), 1.2)
    d_ci = ndi.gaussian_filter(np.maximum(cliff, 0), 1.2)
    d_fo = ndi.gaussian_filter(np.maximum(-woods, 0), 1.2)
    d_fi = ndi.gaussian_filter(np.maximum(woods, 0), 1.2)
    P.fields = dict(cliff=cliff, deck=deck, d_wo=d_wo, d_wi=d_wi, d_co=d_co, d_ci=d_ci,
                    cf=cliff_f, wf=woods_f, d_fo=d_fo, d_fi=d_fi)

    # ---- the jungle floor.  Dark and wet by default; it only opens up in the clearings.
    clear = _patches(P, wp, [(cx, cy, rx * 1.05, ry * 1.05) for (cx, cy, rx, ry) in M.CLEARINGS])
    open_land = smoothstep(2.0, 12.0, d_fo)
    S["floor"] = np.full_like(n_big, 0.66)
    S["fern"] = 0.18 + 0.85 * np.maximum(clear * (0.5 + 0.5 * smoothstep(0.3, 0.6, n_mid)),
                                         smoothstep(0.58, 0.78, n_big) * (0.35 + 0.65 * open_land))
    edge_w = 1 - smoothstep(0.2, 2.8, d_fo)
    S["root"] = 0.16 + 0.85 * np.maximum(edge_w * (0.55 + 0.45 * smoothstep(0.35, 0.6, n_fine)),
                                         smoothstep(0.72, 0.86, n_big2) * 0.6)
    S["mulch"] = 0.14 + 0.80 * smoothstep(0.64, 0.80, n_big2) * (0.4 + 0.6 * (1 - open_land))
    S["rocky"] = 0.08 + 0.9 * np.maximum((1 - smoothstep(0.6, 5.0, d_co))
                                         * (0.4 + 0.6 * smoothstep(0.3, 0.6, n_mid)),
                                         smoothstep(0.82, 0.93, n_big2) * 0.7)
    S["clay"] = np.full_like(n_big, 0.10)

    # ---- the hand-placed patches: camps, troll stonework, rot, mangrove
    tr = _patches(P, wp, getattr(M, "TRAMPLED", []), 0.6)
    ru = _patches(P, wp, getattr(M, "RUIN_STONE", []), 0.7)
    rt = _patches(P, wp, getattr(M, "ROT_PATCHES", []), 0.8)
    mg = _patches(P, wp, getattr(M, "MANGROVE", []), 0.8)
    z = np.zeros_like(n_big)
    S["hard"] = 0.05 + 1.15 * (tr if tr is not None else z)
    S["camp"] = 0.04 + 0.95 * (tr if tr is not None else z) * smoothstep(0.4, 0.7, n_mid)
    S["ruin"] = 0.04 + 1.10 * (ru if ru is not None else z) * (0.85 + 0.15 * n_fine)
    S["rot"] = 0.04 + 1.00 * (rt if rt is not None else z) * (0.6 + 0.4 * smoothstep(0.3, 0.6, n_mid))
    if mg is not None:
        S["mud"] = np.maximum(0.04 + 1.0 * mg, 0.04)
    S["planks"] = (-2.0 + 14 * np.clip(deck + 0.15, 0, 0.6)).astype(np.float32)

    # ---- roads
    core, verge, _ = P.road_field(list(M.ROADS.values()))
    S["road"] = 0.05 + 1.3 * core
    S["verge"] = 0.08 + 0.95 * verge * (1 - core)

    # ---- water: sea on the coast, lakes and rivers inland, pebble beds at the fords
    sea_ext = M.sea(gx, gy) if getattr(M, "sea", None) else np.full_like(n_big, -99.0)
    is_sea = sea_ext > -3.0
    _water_split(P, M, S, sh, dp, wob, n_fine, d_wo, is_sea)
    near_ford = np.zeros_like(n_big)
    for (fx, fy, fr) in spec.fords:
        near_ford = np.maximum(near_ford, np.clip(1 - np.hypot(gx - fx, gy - fy) / fr, 0, 1))
    S["stream"] = (-2.0 + 12 * np.clip(swv + 0.4, 0, 1) * near_ford + 0.6 * near_ford).astype(np.float32)
    S["lake_s"] = (S["lake_s"] - 6.0 * near_ford * np.clip(1 - d_wi * 1.5, 0, 1)).astype(np.float32)

    knock = np.maximum(smoothstep(0.0, 0.7, swv), smoothstep(-0.30, 0.10, deck))
    for k in LAND:
        S[k] = (np.maximum(S.get(k, np.full_like(n_big, -9.0)), -9.0) - 14.0 * knock).astype(np.float32)
    on_deck = smoothstep(-0.30, 0.10, deck)
    for k in ("sea_s", "sea_d", "lake_s", "lake_d"):
        S[k] = (S[k] - 160.0 * on_deck).astype(np.float32)

    # ---- rock and canopy, both impassable and drawn differently
    depth_dark = smoothstep(2.0, 9.0, d_ci)
    cs = 1.6 + 12 * cliff_f
    S["cliff_a"] = (cs - 1.0 * depth_dark).astype(np.float32)
    S["cliff_d"] = (cs - 2.6 + 2.6 * depth_dark).astype(np.float32)
    S["canopy"] = (1.6 + 12 * woods_f).astype(np.float32)
    cl_k = smoothstep(0.0, 0.30, cliff_f)
    wd_k = smoothstep(0.0, 0.30, woods_f)
    for k in list(S):
        if k.startswith("cliff_") or k == "canopy":
            continue
        S[k] = (S[k] - 14.0 * cl_k - 14.0 * wd_k
                - (40.0 * smoothstep(0.0, 1.2, cliff) if k.endswith(("_s", "_d")) else 0.0)).astype(np.float32)
    S["canopy"] = (S["canopy"] - 16.0 * cl_k).astype(np.float32)
    S["cliff_a"] = (S["cliff_a"] - 16.0 * wd_k * (1 - cl_k)).astype(np.float32)
    S["cliff_d"] = (S["cliff_d"] - 16.0 * wd_k * (1 - cl_k)).astype(np.float32)
    for k in MATERIALS:
        S.setdefault(k, np.full_like(n_big, -40.0, dtype=np.float32))
    S["jungle"] = S["floor"]
    return S


# --------------------------------------------------------------------------- towns
def build_scores_town(P, M):
    gx, gy = P.gx, P.gy
    wp = P.warp("regions", amp_tiles=1.8, scale=10.0)
    n_big = P.noise(9.0, "big", octaves=3)
    n_big2 = P.noise(12.0, "big2", octaves=3)
    n_mid = P.noise(4.5, "mid", octaves=3)
    n_fine = P.noise(2.0, "fine", octaves=2)
    F = M.fields(gx, gy)
    wob = (P.noise(3.0, "shorewob", octaves=3) - 0.5) * 0.9
    cliff = F["cliff"].astype(np.float32)
    deck = F["deck"].astype(np.float32)
    cliff_f = np.clip(cliff * 0.5, -0.4, 0.6).astype(np.float32)
    swv = (F["shallow"] + wob).astype(np.float32)
    d_wo, d_wi = np.maximum(-swv, 0), np.maximum(swv, 0)
    d_co = ndi.gaussian_filter(np.maximum(-cliff, 0), 1.2)
    d_ci = ndi.gaussian_filter(np.maximum(cliff, 0), 1.2)
    P.fields = dict(cliff=cliff, deck=deck, d_wo=d_wo, d_wi=d_wi, d_co=d_co, d_ci=d_ci,
                    cf=cliff_f, wf=np.zeros_like(cliff_f), d_fo=np.full_like(cliff, 99.0),
                    d_fi=np.zeros_like(cliff))

    off = np.float32(-9.0)
    S = {k: np.full_like(n_big, off, dtype=np.float32) for k in MATERIALS}
    for i, (mat, w) in enumerate(M.BASE.items()):
        n = P.noise(8.0 + 3 * i, f"base_{mat}", octaves=3)
        S[mat] = (0.12 + w * (0.45 + 0.9 * smoothstep(0.38, 0.72, n))).astype(np.float32)
    for mat, blobs in M.PAINT.items():
        cur = np.maximum(S[mat], 0.05)
        for (cx, cy, rx, ry, st) in blobs:
            cur = np.maximum(cur, 0.10 + 1.15 * P.blob(cx, cy, rx, ry, 0.6, wp) * st)
        S[mat] = cur.astype(np.float32)
    if hasattr(M, "paved"):
        pv = smoothstep(-0.3, 1.2, M.paved(gx, gy).astype(np.float32))
        S["hard"] = np.maximum(np.maximum(S["hard"], 0.05), 0.2 + 1.3 * pv).astype(np.float32)
    S["rocky"] = np.maximum(S["rocky"], (0.06 + 0.8 * (1 - smoothstep(0.6, 4.5, d_co))
                                         * (0.4 + 0.6 * smoothstep(0.3, 0.6, n_mid))).astype(np.float32))
    core, verge, _ = P.road_field(list(M.ROADS.values()))
    S["road"] = (0.05 + 1.3 * core).astype(np.float32)
    S["verge"] = (0.08 + 0.95 * verge * (1 - core)).astype(np.float32)
    S["hard"] = np.maximum(S["hard"], (0.18 + 0.55 * verge * (1 - core)).astype(np.float32))

    is_sea = np.full(n_big.shape, M.WATER == "sea")
    _water_split(P, M, S, F["shallow"].astype(np.float32), F["deep"].astype(np.float32),
                 wob, n_fine, d_wo, is_sea)
    S["planks"] = (-2.0 + 14 * np.clip(deck + 0.15, 0, 0.6)).astype(np.float32)
    knock = np.maximum(smoothstep(0.0, 0.7, swv), smoothstep(-0.30, 0.10, deck))
    for k in LAND + ("rocky",):
        if S[k].max() > -8:
            S[k] = (S[k] - 14.0 * knock).astype(np.float32)
    on_deck = smoothstep(-0.30, 0.10, deck)
    for k in ("sea_s", "sea_d", "lake_s", "lake_d"):
        S[k] = (S[k] - 160.0 * on_deck).astype(np.float32)

    depth_dark = smoothstep(2.0, 9.0, d_ci)
    cs = 1.6 + 12 * cliff_f
    S["cliff_a"] = (cs - 1.0 * depth_dark).astype(np.float32)
    S["cliff_d"] = (cs - 2.6 + 2.6 * depth_dark).astype(np.float32)
    cl_k = smoothstep(0.0, 0.30, cliff_f)
    wk = smoothstep(0.0, 1.2, cliff)
    for k in list(S):
        if not k.startswith("cliff_") and S[k].max() > -8:
            S[k] = (S[k] - 14.0 * cl_k - (40.0 * wk if k.endswith(("_s", "_d")) else 0.0)).astype(np.float32)
    return S


# --------------------------------------------------------------------------- post
def post(rgb, X, Y, P):
    f = P.fields
    sf = lambda a: P.sample_field(np.asarray(a, np.float32), X, Y)
    d_co, d_ci = sf(f["d_co"]), sf(f["d_ci"])
    d_wo, d_wi = sf(f["d_wo"]), sf(f["d_wi"])
    d_fo, d_fi = sf(f["d_fo"]), sf(f["d_fi"])
    # jungle light: big slow gaps in the canopy, fine mottle under it
    dap = P.sample_field(P.noise(6.5, "dapple", octaves=3), X, Y)
    lum_n = P.sample_field(P.noise(18.0, "lumlow", octaves=2), X, Y)
    shade = (0.84 + 0.28 * dap) * (0.96 + 0.08 * lum_n)
    shade *= 1 - 0.26 * (1 - smoothstep(0.0, 1.7, d_co))
    shade *= 1 - 0.26 * smoothstep(1.5, 11.0, d_ci)
    shade *= 1 - 0.32 * (1 - smoothstep(0.0, 2.6, d_fo))
    shade *= 1 - 0.42 * smoothstep(1.5, 10.0, d_fi)
    cf, wf = sf(f["cf"]), sf(f["wf"])
    lip = smoothstep(0.0, 0.03, cf) * (1 - smoothstep(0.03, 0.14, cf))
    wl = smoothstep(0.0, 0.03, wf) * (1 - smoothstep(0.03, 0.12, wf))
    rgb = rgb * shade[..., None] + 26 * lip[..., None] + 12 * wl[..., None]
    wet = (1 - smoothstep(0.0, 1.0, d_wo)) * smoothstep(0.0, 0.25, d_wo)
    rgb *= (1 - 0.14 * wet)[..., None]
    foam = (1 - smoothstep(0.0, 0.32, d_wo + d_wi)) * 0.30
    foam = foam * (1 - smoothstep(-0.05, 0.12, cf))
    rgb = rgb * (1 - foam[..., None]) + np.array([228, 242, 238], np.float32) * foam[..., None]
    dk = sf(f["deck"])
    rail = smoothstep(-0.03, 0.03, dk) * (1 - smoothstep(0.10, 0.34, dk))
    rgb *= (1 - 0.45 * rail)[..., None]
    shadow = (1 - smoothstep(-0.03, 0.03, dk)) * (1 - smoothstep(0.0, 0.55, -dk)) * 0.35
    rgb *= (1 - shadow)[..., None]
    return rgb * np.array([1.01, 1.02, 0.96], np.float32)      # warm, green cast


# --------------------------------------------------------------------------- driver
def bake(key, mat_dir, preview=None, sc=4, only=None):
    wild = key in WILD
    M = importlib.import_module((WILD if wild else TOWN)[key])
    P = Painter(M.W, M.H, mat_dir, seed=3311)
    if wild:
        L = M.build_layout()
        P.sealed_land = getattr(L, "sealed_land", [])
        P.sealed_water = getattr(L, "sealed_water", [])
        scores = build_scores_wild(P, M)
    else:
        scores = build_scores_town(P, M)
    out = ROOT / M.BAKED_DIR
    written = P.bake(MATERIALS, scores, out, chunk_tiles=20, post=post, only=only)
    print(f"{key}: baked {len(written)} chunks -> {out}")
    if preview:
        full = Image.new("RGB", (M.W * TILE_PX, M.H * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        full.resize((M.W * sc, M.H * sc), Image.LANCZOS).save(preview)
        print("preview", preview)


def main():
    allk = list(WILD) + list(TOWN)
    which = [a for a in sys.argv[1:] if a in allk or a == "all"]
    keys = allk if (not which or which[0] == "all") else which
    preview = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    sc = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 4
    only = None
    if "--region" in sys.argv:
        x0, y0, x1, y1 = map(int, sys.argv[sys.argv.index("--region") + 1].split(","))
        only = {(cx, cy) for cx in range(x0 // 20 * 20, x1 + 1, 20) for cy in range(y0 // 20 * 20, y1 + 1, 20)}
    mat_dir, provisional = build_material_dir()
    if provisional:
        print(f"PROVISIONAL textures for {len(provisional)} materials "
              f"(drop real ones in {REAL_DIR.relative_to(ROOT)} to override)")
    for k in keys:
        bake(k, mat_dir, preview if len(keys) == 1 else None, sc, only)


if __name__ == "__main__":
    main()
