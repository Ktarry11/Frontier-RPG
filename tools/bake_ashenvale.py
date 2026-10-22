"""
Bake the Ashenvale West painting (forest floor + rivers/lakes/moon water + cliffs + dense-woods canopy + corruption
patches) from seamless materials in assets/tiles/ashenvale/materials/ (the Ashenvale tile sheet, see
claude/ashenvale_tile_prompts.md - the file names are the AV_SHEET stems below).

    python3 tools/bake_ashenvale.py [west] [--preview out.png] [--scale 4]

Landforms come from tools/handbuilt_ashenvale_west.SPEC.fields() - the SAME analytic functions the tile grid is built
from - plus the tiles that seal_unreachable() turned into canopy / deep water, so painting and collision agree.
Writes assets/tiles/ashenvale/baked_west/ground_<cx>_<cy>.jpg (20x20-tile chunks).

PROVISIONAL TEXTURES: any av_* material that has not been generated yet is synthesised from the old Ashenvale /
corruption / Valley-of-Trials textures (cropped seamless + recoloured).  Drop the real tiles into
assets/tiles/ashenvale/materials/ and re-run: real files always win.
"""
import colorsys
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

REAL_DIR = ROOT / "assets/tiles/ashenvale/materials"
T = ROOT / "assets/tiles"
AV, AC, HF, VOT = T / "ashenvale", T / "ashenvale_corruption", T / "haunted_forest", T / "vot_cluster"
SIZE = 256

# stem -> (source file, vertical crop offset, (hue, sat, val) or None, speckle or None)
# speckle = ((r,g,b), density, size) scatters flower / pebble dots over the texture.
AV_SHEET = {
    # living forest
    "av_forest_floor":   (AV / "forest_floor_dense.png", 0.5, None, None),
    "av_forest_grass":   (AV / "forest_floor_light.png", 0.5, (92, 0.75, 1.05), None),
    "av_fern_floor":     (AV / "forest_floor_light.png", 0.2, (112, 0.80, 0.78), None),
    "av_root_earth":     (AV / "forest_floor_roots.png", 0.5, (40, 0.50, 0.70), None),
    "av_needle_mulch":   (AV / "forest_floor_roots.png", 0.15, (14, 0.40, 0.78), None),
    "av_bluebell":       (AV / "forest_floor_light.png", 0.8, (100, 0.70, 0.92), ((120, 120, 235), 0.012, 3)),
    "av_road_centre":    (VOT / "vot_road_ruts_a.png", 0.5, (30, 0.42, 0.80), None),
    "av_road_edge":      (VOT / "vot_road_ruts_b.png", 0.5, (40, 0.36, 0.72), None),
    "av_elven_paving":   (VOT / "vot_limestone.png", 0.5, (205, 0.10, 0.92), None),
    "av_mossy_cobble":   (VOT / "vot_limestone.png", 0.2, (95, 0.28, 0.62), None),
    "av_rocky_ground":   (AV / "rocky_forest_ground.png", 0.5, None, None),
    "av_stream_bed":     (VOT / "vot_gravel.png", 0.5, (85, 0.14, 0.70), None),
    "av_lake_mud":       (AV / "forest_floor_roots.png", 0.85, (36, 0.45, 0.58), None),
    "av_lake_shallow":   (AV / "lake_water.png", 0.5, (178, 0.62, 1.55), None),
    "av_lake_deep":      (AV / "lake_water.png", 0.2, (190, 0.80, 0.80), None),
    "av_moon_water":     (AV / "moonwell_water.png", 0.5, (205, 0.52, 1.18), None),
    "av_moon_deep":      (REAL_DIR / "av_moon_water.png", 0.2, (222, 0.70, 0.66), None),
    # water / cliff / coast
    "av_moon_rim":       (AV / "moonwell_rim.png", 0.5, (200, 0.10, 1.35), None),
    "av_cliff_a":        (VOT / "vot_cliff_a.png", 0.5, (262, 0.14, 0.95), None),
    "av_cliff_b":        (VOT / "vot_cliff_b.png", 0.5, (268, 0.16, 0.82), None),
    "av_canopy":         (REAL_DIR / "av_fern_floor.png", 0.35, (112, 0.80, 1.10), "canopy"),
    "av_beach":          (AV / "coastal_sand.png", 0.5, None, None),
    "av_wet_sand":       (AV / "coastal_sand.png", 0.2, (34, 0.55, 0.66), None),
    "av_sea_shallow":    (AV / "shallow_coastal_water.png", 0.5, None, None),
    "av_sea_deep":       (AV / "shallow_coastal_water.png", 0.15, (205, 0.75, 0.50), None),
    # corruption / burned lands
    "av_scorched":       (AC / "scorched_floor.png", 0.5, (30, 0.18, 0.95), None),
    "av_burned_forest":  (HF / "burned_village_ground.png", 0.5, (28, 0.20, 1.75), None),
    "av_fel_earth":      (AV / "corrupted_ground.png", 0.5, None, None),
    "av_corrupt_ground": (AV / "corrupted_ground.png", 0.2, (285, 0.28, 1.15), None),
    "av_satyr_earth":    (AC / "satyr_camp_floor.png", 0.5, None, None),
    "av_plaza_stone":    (VOT / "vot_limestone.png", 0.8, (215, 0.12, 0.98), None),
}


def _recolour(a, hue, sat, val):
    """a float 0..1 HxWx3 -> luminance-preserving tint."""
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


def synth(stem, seed=3):
    path, off, rec, extra = AV_SHEET[stem]
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
    rng = np.random.default_rng(seed + sum(map(ord, stem)))
    if extra == "canopy":
        # layered leaf crowns: bright lobes over a dark understory
        lobes = ndi.gaussian_filter(rng.random((SIZE, SIZE)).astype(np.float32), 5.0, mode="wrap")
        lobes = (lobes - lobes.min()) / (lobes.max() - lobes.min() + 1e-6)
        fine = ndi.gaussian_filter(rng.random((SIZE, SIZE)).astype(np.float32), 1.6, mode="wrap")
        fine = (fine - fine.min()) / (fine.max() - fine.min() + 1e-6)
        k = (0.62 + 0.75 * (lobes > 0.52) * (0.45 + 0.55 * fine))[..., None]
        a = a * k
    elif extra:
        col, dens, size = extra
        dots = rng.random((SIZE, SIZE)) < dens
        dots = ndi.binary_dilation(dots, iterations=size - 2) if size > 2 else dots
        c = np.array(col, np.float32) / 255.0
        a = np.where(dots[..., None], a * 0.25 + c * 0.75, a)
    return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))


def build_material_dir():
    tmp = Path(tempfile.mkdtemp(prefix="av_mat_"))
    provisional = []
    for stem in AV_SHEET:
        real = REAL_DIR / f"{stem}.png"
        if real.exists():
            Image.open(real).convert("RGB").resize((SIZE, SIZE), Image.LANCZOS).save(tmp / f"{stem}.png")
            continue
        synth(stem).save(tmp / f"{stem}.png")
        provisional.append(stem)
    return tmp, provisional


MATERIALS = {
    "floor":   ("av_forest_floor", "av_fern_floor", 1.0),
    "grass":   ("av_forest_grass", None, 1.0),
    "fern":    ("av_fern_floor", None, 1.0),
    "root":    ("av_root_earth", None, 1.0),
    "mulch":   ("av_needle_mulch", None, 1.0),
    "bell":    ("av_bluebell", None, 1.0),
    "road":    ("av_road_centre", "av_road_edge", 1.0),
    "verge":   ("av_road_edge", None, 1.0),
    "paving":  ("av_elven_paving", "av_mossy_cobble", 1.0),
    "plaza":   ("av_plaza_stone", None, 1.0),
    "rocky":   ("av_rocky_ground", None, 1.0),
    "stream":  ("av_stream_bed", None, 1.0),
    "mud":     ("av_lake_mud", None, 1.0),
    "lake_s":  ("av_lake_shallow", None, 1.0),
    "lake_d":  ("av_lake_deep", None, 1.0),
    "moon_s":  ("av_moon_water", None, 1.0),
    "moon_d":  ("av_moon_deep", None, 1.0),
    "moonrim": ("av_moon_rim", None, 1.0),
    "sea_s":   ("av_sea_shallow", None, 1.0),
    "sea_d":   ("av_sea_deep", None, 1.0),
    "beach":   ("av_beach", None, 1.0),
    "wet":     ("av_wet_sand", None, 1.0),
    "cliff_a": ("av_cliff_a", "av_cliff_b", 1.0),
    "cliff_d": ("av_cliff_b", None, 1.0),
    "canopy":  ("av_canopy", None, 1.0),
    "scorch":  ("av_scorched", None, 1.0),
    "burned":  ("av_burned_forest", None, 1.0),
    "fel":     ("av_fel_earth", None, 1.0),
    "corrupt": ("av_corrupt_ground", None, 1.0),
    "satyr":   ("av_satyr_earth", None, 1.0),
}


def _tile_soft(P, tiles, key):
    """Smooth mask-grid field (about -1..1) from a list of (x, y) tile coords."""
    g = np.zeros((P.H, P.W), np.float32)
    for (x, y) in tiles:
        g[y, x] = 1.0
    return P.tile_mask(g, threshold=0.5, noise_amp=0.10, key=key, sigma=0.9, soft=True).astype(np.float32)


def build_scores(P, M):
    """M = the zone module (handbuilt_ashenvale_west or _east) providing SPEC and the plan data."""
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
    sh_ext, dp_ext = F["shallow"].astype(np.float32), F["deep"].astype(np.float32)
    cliff = F["cliff"].astype(np.float32)
    woods = F["woods"].astype(np.float32)

    # tiles sealed by seal_unreachable: collision-only cliffs that must LOOK like walls (canopy / deep water)
    sl = getattr(P, "sealed_land", None)
    sw_t = getattr(P, "sealed_water", None)
    if sl:
        woods = np.maximum(woods, 1.4 * _tile_soft(P, sl, "sealland") + 0.4)
        woods = np.where(_tile_soft(P, sl, "sealland") > 0.02, np.maximum(woods, 1.2), woods).astype(np.float32)
    if sw_t:
        dp_ext = np.maximum(dp_ext, 1.4 * _tile_soft(P, sw_t, "sealwater") + 0.2).astype(np.float32)

    cliff_f = np.clip(cliff * 0.5, -0.4, 0.6).astype(np.float32)
    woods_f = np.clip(woods * 0.5, -0.4, 0.6).astype(np.float32)
    sw = (sh_ext + wob).astype(np.float32)
    d_water_out = np.maximum(-sw, 0)
    d_water_in = np.maximum(sw, 0)
    d_cliff_out = ndi.gaussian_filter(np.maximum(-cliff, 0), 1.2)
    d_cliff_in = ndi.gaussian_filter(np.maximum(cliff, 0), 1.2)
    d_woods_out = ndi.gaussian_filter(np.maximum(-woods, 0), 1.2)
    d_woods_in = ndi.gaussian_filter(np.maximum(woods, 0), 1.2)
    P.fields = dict(cliff=cliff, d_wo=d_water_out, d_wi=d_water_in, d_co=d_cliff_out, d_ci=d_cliff_in,
                    cf=cliff_f, wf=woods_f, d_fo=d_woods_out, d_fi=d_woods_in)

    # -------- the forest floor: dark mossy base, lighter grass in clearings, ferns / roots / needle mulch patches
    clear = np.maximum.reduce([P.blob(cx, cy, rx * 1.05, ry * 1.05, 0.8, wp) for (cx, cy, rx, ry) in M.CLEARINGS])
    open_land = smoothstep(2.0, 12.0, d_woods_out)            # far from any massif -> sunlit
    S["floor"] = np.full_like(n_big, 0.62)
    S["grass"] = 0.15 + 0.85 * np.maximum(clear * (0.55 + 0.45 * smoothstep(0.3, 0.6, n_mid)),
                                          smoothstep(0.60, 0.78, n_big) * (0.35 + 0.65 * open_land))
    S["fern"] = 0.16 + 0.80 * smoothstep(0.62, 0.80, n_mid) * (0.45 + 0.55 * (1 - open_land))
    edge_w = 1 - smoothstep(0.2, 2.6, d_woods_out)            # at the foot of the massifs: gnarled roots
    S["root"] = 0.14 + 0.80 * np.maximum(edge_w * (0.55 + 0.45 * smoothstep(0.35, 0.6, n_fine)),
                                         smoothstep(0.72, 0.86, n_big2) * 0.6)
    S["mulch"] = 0.12 + 0.80 * smoothstep(0.64, 0.80, n_big2) * (0.4 + 0.6 * (1 - open_land))
    bells = [P.blob(*b, 0.75, wp) for b in getattr(M, "BLUEBELL_PATCHES", [])]
    S["bell"] = 0.05 + 0.95 * (np.maximum.reduce(bells) if bells else 0) * smoothstep(0.30, 0.55, n_fine)
    rocky_skirt = (1 - smoothstep(0.6, 5.0, d_cliff_out)) * (0.4 + 0.6 * smoothstep(0.3, 0.6, n_mid))
    S["rocky"] = 0.08 + 0.9 * np.maximum(rocky_skirt, smoothstep(0.80, 0.92, n_big2) * 0.7)

    # -------- corruption / burned ground around the furbolg dens and satyr lairs
    cor = [P.blob(*b, 0.8, wp) for b in getattr(M, "CORRUPT_PATCHES", [])]
    burn = [P.blob(*b, 0.8, wp) for b in getattr(M, "BURNED_PATCHES", [])]
    cm = np.maximum.reduce(cor) if cor else np.zeros_like(n_big)
    bm = np.maximum.reduce(burn) if burn else np.zeros_like(n_big)
    S["corrupt"] = 0.04 + 0.95 * cm * (0.6 + 0.4 * smoothstep(0.3, 0.6, n_mid))
    S["fel"] = 0.04 + 0.95 * cm * smoothstep(0.55, 0.78, n_fine) * smoothstep(0.1, 0.5, cm)
    S["burned"] = 0.04 + 0.95 * bm
    S["scorch"] = 0.04 + 0.95 * bm * smoothstep(0.55, 0.75, n_mid)
    S["satyr"] = 0.03 + 0.95 * getattr(M, "satyr_field", lambda P_, wp_: np.zeros_like(n_big))(P, wp)

    # -------- roads, paved gates, the moonwell's silver paving
    core, verge, _ = P.road_field(list(M.ROADS.values()))
    S["road"] = 0.05 + 1.3 * core
    S["verge"] = 0.08 + 0.95 * verge * (1 - core)
    pav = [P.blob(*b, 0.55, wp) for b in getattr(M, "PAVED_PATCHES", [])]
    S["paving"] = 0.04 + 1.1 * (np.maximum.reduce(pav) if pav else 0) * (0.9 + 0.1 * n_fine)
    S["plaza"] = 0.03 + 1.1 * getattr(M, "plaza_field", lambda P_, wp_: np.zeros_like(n_big))(P, wp)

    # -------- water: sea / lakes & rivers / moon-pools
    sea_ext = M.sea(gx, gy) if getattr(M, "sea", None) else np.full_like(n_big, -99.0)
    sea_side = sea_ext > -3.0
    moon_zone = np.zeros_like(n_big, bool)
    for (cx, cy, r) in getattr(M, "MOON_POOLS", []):
        moon_zone |= (np.hypot(gx - cx, gy - cy) < r)
    lake_out = np.where(sea_side, 99.0, d_water_out)
    near_moon = np.where(moon_zone, d_water_out, 99.0)
    S["mud"] = 0.08 + 1.1 * (1 - smoothstep(0.35, 2.0, lake_out)) * (0.75 + 0.25 * n_fine)
    S["moonrim"] = 0.04 + 1.2 * (1 - smoothstep(0.2, 1.3, near_moon))
    sea_out = np.where(sea_side, d_water_out, 99.0)
    S["beach"] = 0.06 + 1.0 * (1 - smoothstep(1.0, 8.0, sea_out)) * (0.6 + 0.4 * smoothstep(0.25, 0.6, n_fine))
    S["wet"] = 0.06 + 1.1 * (1 - smoothstep(0.3, 1.7, sea_out))

    w_s = np.clip(sh_ext + wob, -4, 6)
    w_d = np.clip(dp_ext + wob, -6, 6)
    base_s = (1.6 + 10 * w_s).astype(np.float32)
    base_d = (1.6 + 10 * w_s + 2.5 * w_d).astype(np.float32)
    off = np.float32(-40.0)
    S["sea_s"] = np.where(sea_side, base_s, off).astype(np.float32)
    S["sea_d"] = np.where(sea_side, base_d, off).astype(np.float32)
    S["lake_s"] = np.where(sea_side | moon_zone, off, base_s).astype(np.float32)
    S["lake_d"] = np.where(sea_side | moon_zone, off, base_d).astype(np.float32)
    S["moon_s"] = np.where(moon_zone & ~sea_side, base_s, off).astype(np.float32)
    S["moon_d"] = np.where(moon_zone & ~sea_side, base_d, off).astype(np.float32)
    # fords: the river is wadeable here, show the pebble bed through the water
    near_ford = np.zeros_like(n_big)
    for (fx, fy, fr) in spec.fords:
        near_ford = np.maximum(near_ford, np.clip(1 - np.hypot(gx - fx, gy - fy) / fr, 0, 1))
    S["stream"] = (-2.0 + 12 * np.clip(sw + 0.4, 0, 1) * near_ford + 0.6 * near_ford).astype(np.float32)
    S["stream"] = np.maximum(S["stream"], (0.04 + 0.9 * (1 - smoothstep(0.0, 0.9, d_water_in)) *
                                            smoothstep(0.0, 0.3, d_water_in) * near_ford).astype(np.float32))
    knock = smoothstep(0.0, 0.7, sw)
    for k in ("floor", "grass", "fern", "root", "mulch", "bell", "rocky", "corrupt", "fel", "burned", "scorch",
              "satyr", "road", "verge", "paving", "plaza", "beach", "wet", "mud", "moonrim"):
        S[k] = (S[k] - 14.0 * knock).astype(np.float32)
    S["lake_s"] = (S["lake_s"] - 6.0 * near_ford * np.clip(1 - np.maximum(sw, 0) * 1.5, 0, 1)).astype(np.float32)

    # -------- cliffs (rock) and the dense-woods canopy (both impassable, drawn differently)
    depth_dark = smoothstep(2.0, 9.0, d_cliff_in)
    cs = 1.6 + 12 * cliff_f
    S["cliff_a"] = (cs - 1.0 * depth_dark).astype(np.float32)
    S["cliff_d"] = (cs - 2.6 + 2.6 * depth_dark).astype(np.float32)
    S["canopy"] = (1.6 + 12 * woods_f).astype(np.float32)
    cl_k = smoothstep(0.0, 0.30, cliff_f)
    wd_k = smoothstep(0.0, 0.30, woods_f)
    for k in list(S):
        if k.startswith("cliff_") or k == "canopy":
            continue
        S[k] = (S[k] - 14.0 * cl_k - 14.0 * wd_k - (40.0 * smoothstep(0.0, 1.2, cliff) if k.endswith(("_s", "_d")) else 0.0)
                ).astype(np.float32)
    # a mesa wins over a woods blob where both overlap, and vice versa the canopy must not paint over rock
    S["canopy"] = (S["canopy"] - 16.0 * cl_k).astype(np.float32)
    S["cliff_a"] = (S["cliff_a"] - 16.0 * wd_k * (1 - cl_k)).astype(np.float32)
    S["cliff_d"] = (S["cliff_d"] - 16.0 * wd_k * (1 - cl_k)).astype(np.float32)
    return S


def post(rgb, X, Y, P):
    f = P.fields
    sf = lambda a: P.sample_field(a.astype(np.float32), X, Y)
    d_co, d_ci = sf(f["d_co"]), sf(f["d_ci"])
    d_wo, d_wi = sf(f["d_wo"]), sf(f["d_wi"])
    d_fo, d_fi = sf(f["d_fo"]), sf(f["d_fi"])
    # twilight dapple: big slow light patches under the canopy plus a little fine mottling
    dap = P.sample_field(P.noise(7.0, "dapple", octaves=3), X, Y)
    lum_n = P.sample_field(P.noise(18.0, "lumlow", octaves=2), X, Y)
    shade = (0.86 + 0.26 * dap) * (0.96 + 0.08 * lum_n)
    shade *= 1 - 0.26 * (1 - smoothstep(0.0, 1.7, d_co))      # rock: dark foot
    shade *= 1 - 0.26 * smoothstep(1.5, 11.0, d_ci)
    shade *= 1 - 0.30 * (1 - smoothstep(0.0, 2.6, d_fo))      # woods: shadow pooled at the treeline
    shade *= 1 - 0.40 * smoothstep(1.5, 10.0, d_fi)           # ... and deep inside the massif
    cf = sf(f["cf"])
    lip = smoothstep(0.0, 0.03, cf) * (1 - smoothstep(0.03, 0.14, cf))
    wf = sf(f["wf"])
    wl = smoothstep(0.0, 0.03, wf) * (1 - smoothstep(0.03, 0.12, wf))
    rgb = rgb * shade[..., None] + 26 * lip[..., None] + 12 * wl[..., None]
    wet = (1 - smoothstep(0.0, 1.0, d_wo)) * smoothstep(0.0, 0.25, d_wo)
    rgb *= (1 - 0.14 * wet)[..., None]
    foam = (1 - smoothstep(0.0, 0.30, d_wo + d_wi)) * 0.26
    foam = foam * (1 - smoothstep(-0.05, 0.12, cf))
    rgb = rgb * (1 - foam[..., None]) + np.array([225, 240, 240], np.float32) * foam[..., None]
    rgb = rgb * np.array([0.97, 0.99, 1.04], np.float32)       # cool twilight cast
    return rgb


def bake(zone="west", preview=None, scale=4, only=None):
    if zone == "west":
        from tools import handbuilt_ashenvale_west as M
    else:
        from tools import handbuilt_ashenvale_east as M
    mat_dir, provisional = build_material_dir()
    if provisional:
        print(f"PROVISIONAL textures for {len(provisional)} materials: {', '.join(provisional[:8])}...")
    P = Painter(M.W, M.H, mat_dir, seed=2101)
    # build the layout once so sealed pockets are painted as walls
    L = M.build_layout()
    P.sealed_land = getattr(L, "sealed_land", [])
    P.sealed_water = getattr(L, "sealed_water", [])
    scores = build_scores(P, M)
    out = ROOT / M.BAKED_DIR
    written = P.bake(MATERIALS, scores, out, chunk_tiles=20, post=post, only=only)
    print(f"baked {len(written)} chunks -> {out}")
    if preview:
        full = Image.new("RGB", (M.W * TILE_PX, M.H * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        full.resize((M.W * scale, M.H * scale), Image.LANCZOS).save(preview)
        print("preview", preview)


def main():
    preview = None
    if "--preview" in sys.argv:
        preview = sys.argv[sys.argv.index("--preview") + 1]
    sc = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 4
    zone = "east" if "east" in sys.argv else "west"
    only = None
    if "--region" in sys.argv:       # x0,y0,x1,y1 in tiles: bake only the 20x20 chunks touching it (fast look-dev)
        x0, y0, x1, y1 = map(int, sys.argv[sys.argv.index("--region") + 1].split(","))
        only = {(cx, cy) for cx in range(x0 // 20 * 20, x1 + 1, 20) for cy in range(y0 // 20 * 20, y1 + 1, 20)}
    bake(zone, preview, sc, only)


if __name__ == "__main__":
    main()
