"""
Bake the Central Barrens painting (ground + water + cliffs + decks) from seamless
materials in assets/tiles/central_barrens/materials/ (the golden-savannah tile sheet,
tiles 1-28, sliced to cb_*.png - see claude/barrens_tile_prompts.md).

    python3 tools/bake_central_barrens.py [--preview out.png] [--scale 4]

Landforms come from tools/handbuilt_central_barrens.fields() - the SAME analytic
functions the tile grid is built from - so painting and collision agree.
Writes assets/tiles/central_barrens/baked/ground_<cx>_<cy>.jpg (15x15 chunks of 20x20).

PROVISIONAL TEXTURES: any cb_* material that has not been generated yet is synthesised on
the fly from the Valley-of-Trials set (hue-shifted to golden savannah) so the pipeline can
run end to end.  Drop the real tiles into assets/tiles/central_barrens/materials/ and re-run:
real files always win.
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

from tools import handbuilt_central_barrens as CB          # noqa: E402
from tools.terrain_painter import Painter, smoothstep, TILE_PX  # noqa: E402

REAL_DIR = ROOT / "assets/tiles/central_barrens/materials"
VOT_DIR = ROOT / "assets/tiles/vot_cluster"

# sheet order (tiles 1-28) -> file stem; (provisional source, hue deg, sat x, val x)
SHEET = [
    ("cb_gold_grass", "vot_sagegrass", 46, 0.80, 1.45),
    ("cb_tall_grass", "vot_sagegrass", 50, 0.95, 1.20),
    ("cb_sparse_grass", "vot_dune", 44, 0.55, 1.05),
    ("cb_cracked_earth", "vot_clay_a", 36, 0.52, 1.05),
    ("cb_cracked_pebbles", "vot_clay_pebbles", 36, 0.50, 1.05),
    ("cb_road_centre", "vot_road_ruts_a", 36, 0.40, 1.15),
    ("cb_road_edge", "vot_road_ruts_b", 36, 0.40, 1.10),
    ("cb_sandstone_hardpan", "vot_hardpan", 40, 0.42, 1.05),
    ("cb_red_clay", "vot_clay_a", 20, 0.95, 0.95),
    ("cb_wash_gravel", "vot_gravel", 38, 0.35, 1.05),
    ("cb_wash_mud", "vot_mudshore", 34, 0.45, 1.00),
    ("cb_dust_drift", "vot_dune", 42, 0.45, 1.10),
    ("cb_bone_earth", "vot_bonesand", 42, 0.40, 1.05),
    ("cb_thorn_litter", "vot_cinder", 34, 0.45, 0.95),
    ("cb_camp_earth", "vot_camp_prints", 32, 0.55, 0.95),
    ("cb_oasis_grass", "vot_greengrass", 88, 0.85, 1.05),
    ("cb_oasis_mud", "vot_mudshore", 30, 0.55, 0.70),
    ("cb_oasis_shallow", "vot_water_shallow", None, 1, 1),
    ("cb_oasis_deep", "vot_water_deep", None, 1, 1),
    ("cb_cliff_a", "vot_cliff_a", 34, 0.50, 1.10),
    ("cb_cliff_b", "vot_cliff_b", 32, 0.48, 1.05),
    ("cb_rock_dark", "vot_rock_dark", 28, 0.40, 0.85),
    ("cb_chalk_cliff", "vot_limestone", 44, 0.18, 1.18),
    ("cb_beach_sand", "vot_dune", 46, 0.38, 1.25),
    ("cb_wet_sand", "vot_dune", 40, 0.50, 0.80),
    ("cb_sea_shallow", "vot_water_shallow", None, 1, 1),
    ("cb_sea_deep", "vot_water_deep", None, 1, 1),
    ("cb_salt_pan", "vot_limestone", 50, 0.10, 1.30),
    ("cb_planks", "vot_planks", None, 1, 1),            # tile 30 (Crossroads sheet) - same wood
]


def _recolour(img, hue, sat, val):
    a = np.asarray(img.convert("RGB"), np.float32) / 255.0
    mx, mn = a.max(2), a.min(2)
    lum = a.mean(2)
    v = np.clip((lum - lum.mean()) * 1.0 + lum.mean(), 0, 1) * val
    out = np.zeros_like(a)
    h = hue / 360.0
    r, g, b = colorsys.hsv_to_rgb(h, 1.0, 1.0)
    base = np.array([r, g, b], np.float32)
    s = np.clip(sat, 0, 1)
    gray = np.repeat(v[..., None], 3, 2)
    tint = v[..., None] * base[None, None, :]
    out = gray * (1 - s) + tint * s
    return Image.fromarray(np.clip(out * 255, 0, 255).astype(np.uint8))


def build_material_dir():
    """Real tiles from REAL_DIR where they exist, otherwise recoloured stand-ins."""
    tmp = Path(tempfile.mkdtemp(prefix="cb_mat_"))
    provisional = []
    for stem, src, hue, sat, val in SHEET:
        real = REAL_DIR / f"{stem}.png"
        if real.exists():
            Image.open(real).convert("RGB").save(tmp / f"{stem}.png")
            continue
        im = Image.open(VOT_DIR / f"{src}.png").convert("RGB")
        if hue is not None:
            im = _recolour(im, hue, sat, val)
        im.save(tmp / f"{stem}.png")
        provisional.append(stem)
    # alt mixes use the cliff / road stems directly
    return tmp, provisional


MATERIALS = {
    "gold":    ("cb_gold_grass", "cb_sparse_grass", 1.0),
    "tall":    ("cb_tall_grass", None, 1.0),
    "sparse":  ("cb_sparse_grass", None, 1.0),
    "cracked": ("cb_cracked_earth", "cb_cracked_pebbles", 1.0),
    "hard":    ("cb_sandstone_hardpan", None, 1.0),
    "clay":    ("cb_red_clay", None, 1.0),
    "wash_g":  ("cb_wash_gravel", None, 1.0),
    "wash_m":  ("cb_wash_mud", None, 1.0),
    "dust":    ("cb_dust_drift", None, 1.0),
    "bone":    ("cb_bone_earth", None, 1.0),
    "thorn":   ("cb_thorn_litter", None, 1.0),
    "camp":    ("cb_camp_earth", None, 1.0),
    "lush":    ("cb_oasis_grass", None, 1.0),
    "o_mud":   ("cb_oasis_mud", None, 1.0),
    "beach":   ("cb_beach_sand", None, 1.0),
    "wet":     ("cb_wet_sand", None, 1.0),
    "salt":    ("cb_salt_pan", None, 1.0),
    "road":    ("cb_road_centre", "cb_road_edge", 1.0),
    "verge":   ("cb_road_edge", None, 1.0),
    "planks":  ("cb_planks", None, 1.0),
    "lake_s":  ("cb_oasis_shallow", None, 1.0),
    "lake_d":  ("cb_oasis_deep", None, 1.0),
    "sea_s":   ("cb_sea_shallow", None, 1.0),
    "sea_d":   ("cb_sea_deep", None, 1.0),
    "cliff_a": ("cb_cliff_a", "cb_cliff_b", 1.0),
    "cliff_d": ("cb_rock_dark", None, 1.0),
    "cliff_c": ("cb_chalk_cliff", None, 1.0),
}


def build_scores(P):
    S = {}
    gx, gy = P.gx, P.gy
    wp = P.warp("regions", amp_tiles=2.6, scale=13.0)
    n_big = P.noise(11.0, "big", octaves=3)
    n_big2 = P.noise(14.0, "big2", octaves=3)
    n_mid = P.noise(5.0, "mid", octaves=3)
    n_fine = P.noise(2.0, "fine", octaves=2)

    F = CB.fields(gx, gy)
    wob = (P.noise(3.0, "shorewob", octaves=3) - 0.5) * 0.9
    sh_ext, dp_ext = F["shallow"], F["deep"]
    cliff = F["cliff"].astype(np.float32)
    deck = F["deck"].astype(np.float32)
    cliff_f = np.clip(cliff * 0.5, -0.4, 0.6).astype(np.float32)
    sw = (sh_ext + wob).astype(np.float32)
    d_water_out = np.maximum(-sw, 0)
    d_water_in = np.maximum(sw, 0)
    d_cliff_out = ndi.gaussian_filter(np.maximum(-cliff, 0), 1.2)
    d_cliff_in = ndi.gaussian_filter(np.maximum(cliff, 0), 1.2)
    P.fields = dict(cliff=cliff, deck=deck, d_wo=d_water_out, d_wi=d_water_in,
                    d_co=d_cliff_out, d_ci=d_cliff_in, cf=cliff_f)
    sea_side = gx > 244.0                       # the east sea + Southfury river; everything else is oasis water

    # -------- base country: short golden grass, with tall / sparse / cracked patches
    S["gold"] = np.full_like(n_big, 0.55)
    S["tall"] = 0.18 + 0.75 * smoothstep(0.60, 0.80, n_big)
    S["sparse"] = 0.26 + 0.70 * smoothstep(0.58, 0.80, n_mid) * (0.55 + 0.45 * smoothstep(0.3, 0.6, n_big2))
    dry_zone = np.maximum.reduce([P.blob(235, 150, 40, 70, 0.8, wp), P.blob(150, 215, 60, 22, 0.8, wp),
                                  P.blob(45, 170, 28, 40, 0.8, wp)])
    S["cracked"] = 0.20 + 0.75 * np.maximum(smoothstep(0.60, 0.78, n_big2) * 0.9 * (0.4 + 0.6 * dry_zone),
                                             dry_zone * 0.55 * smoothstep(0.45, 0.65, n_mid))
    S["clay"] = 0.05 + 0.95 * np.maximum.reduce([
        P.blob(240, 242, 10, 8, 0.7, wp) * smoothstep(0.35, 0.6, n_mid),
        P.blob(16, 72, 8, 10, 0.7, wp) * smoothstep(0.35, 0.6, n_mid),
        P.blob(100, 275, 9, 6, 0.7, wp) * smoothstep(0.4, 0.6, n_mid),
        P.blob(168, 30, 8, 6, 0.7, wp) * smoothstep(0.4, 0.6, n_mid)])
    mesa_skirt = 1 - smoothstep(0.8, 6.0, d_cliff_out)
    S["hard"] = 0.10 + 0.90 * np.maximum(mesa_skirt * (0.35 + 0.65 * smoothstep(0.35, 0.6, n_mid)),
                                          P.blob(130, 98, 20, 14, 0.8, wp) * 0.8)
    S["dust"] = 0.08 + 0.90 * np.maximum.reduce([
        P.blob(40, 255, 22, 14, 0.8, wp) * smoothstep(0.35, 0.6, n_mid),
        P.blob(215, 272, 20, 10, 0.8, wp) * smoothstep(0.35, 0.6, n_mid),
        P.blob(20, 195, 10, 12, 0.8, wp) * smoothstep(0.4, 0.6, n_mid),
        smoothstep(0.78, 0.9, n_fine) * dry_zone * 0.6])
    S["bone"] = 0.08 + 0.92 * np.maximum.reduce([
        P.blob(205, 120, 15, 10, 0.8, wp) * (0.6 + 0.4 * smoothstep(0.3, 0.6, n_fine)),
        P.blob(47, 255, 8, 6, 0.7, wp), P.blob(224, 276, 9, 5, 0.7, wp),
        P.blob(88, 224, 4, 3, 0.7, wp), P.blob(104, 84, 6, 5, 0.7, wp) * 0.8])
    S["thorn"] = 0.08 + 0.92 * np.maximum.reduce([
        P.blob(130, 252, 14, 10, 0.8, wp), P.blob(170, 252, 14, 10, 0.8, wp),
        P.blob(50, 46, 14, 10, 0.8, wp), P.blob(56, 54, 8, 9, 0.8, wp),
        P.blob(60, 58, 14, 14, 0.8, wp) * smoothstep(0.5, 0.7, n_mid)])
    camp_fields = [P.blob(cx, cy, rx, ry, 0.7, wp) for (cx, cy, rx, ry) in CB.CAMP_PATCHES.values()]
    S["camp"] = 0.08 + 0.95 * np.maximum.reduce(camp_fields)
    S["salt"] = 0.05 + 0.95 * np.maximum.reduce([
        P.blob(226, 232, 11, 4.5, 0.7, wp) * smoothstep(0.3, 0.6, n_mid),
        P.blob(112, 176, 4, 3, 0.7, wp), P.blob(70, 100, 4, 3, 0.7, wp)])

    # -------- dry riverbeds (painted only): gravel flanks a muddy bed
    wd = CB.wash_dist(gx, gy).astype(np.float32)
    wd_in = np.clip(wd, -2, 2.5)
    S["wash_g"] = 0.05 + 1.3 * smoothstep(-0.4, 0.6, wd_in)
    S["wash_m"] = 0.04 + 1.3 * smoothstep(0.8, 1.7, wd_in) * (0.6 + 0.4 * smoothstep(0.3, 0.6, n_fine))

    # -------- oases: lush grass halo + dark wet mud rim (lakes only, not the sea)
    lake_out = np.where(sea_side, 99.0, d_water_out)
    halo = (1 - smoothstep(2.0, 11.0, lake_out)) * (0.55 + 0.45 * smoothstep(0.3, 0.6, n_mid))
    S["lush"] = 0.06 + 1.0 * halo + 0.9 * np.maximum(P.blob(76, 198, 22, 14, 0.8, wp) * 0.5, 0)
    S["lush"] = np.maximum(S["lush"], 0.06 + 0.8 * P.blob(82, 84, 22, 16, 0.8, wp) * smoothstep(0.35, 0.6, n_mid))
    S["tall"] = np.maximum(S["tall"], 0.2 + 0.8 * halo * smoothstep(0.2, 0.5, n_fine))
    S["o_mud"] = 0.08 + 1.1 * (1 - smoothstep(0.4, 2.2, lake_out)) * (0.75 + 0.25 * n_fine)

    # -------- coast: pale beach sand, wet sand at the surf, mud on the river banks
    sea_out = np.where(sea_side, d_water_out, 99.0)
    S["beach"] = 0.06 + 1.0 * (1 - smoothstep(1.0, 8.0, sea_out)) * (0.6 + 0.4 * smoothstep(0.25, 0.6, n_fine))
    S["wet"] = 0.06 + 1.1 * (1 - smoothstep(0.3, 1.7, sea_out))

    # -------- roads
    core, verge, _ = P.road_field(list(CB.ROADS.values()))
    S["road"] = 0.05 + 1.3 * core
    S["verge"] = 0.08 + 0.95 * verge * (1 - core)
    S["hard"] = np.maximum(S["hard"], 0.18 + 0.55 * verge * (1 - core))

    # -------- water (continuous scores -> anti-aliased shorelines)
    w_s = np.clip(sh_ext + wob, -4, 6)
    w_d = np.clip(dp_ext + wob, -6, 6)
    base_s = (1.6 + 10 * w_s).astype(np.float32)
    base_d = (1.6 + 10 * w_s + 2.5 * w_d).astype(np.float32)
    off = np.float32(-40.0)
    S["sea_s"] = np.where(sea_side, base_s, off).astype(np.float32)
    S["sea_d"] = np.where(sea_side, base_d, off).astype(np.float32)
    S["lake_s"] = np.where(sea_side, off, base_s).astype(np.float32)
    S["lake_d"] = np.where(sea_side, off, base_d).astype(np.float32)
    knock = np.maximum(smoothstep(0.0, 0.7, sw), smoothstep(-0.30, 0.10, deck))
    S["planks"] = (-2.0 + 14 * np.clip(deck + 0.15, 0, 0.6)).astype(np.float32)
    for k in ("gold", "tall", "sparse", "cracked", "hard", "clay", "wash_g", "wash_m", "dust", "bone", "thorn",
              "camp", "lush", "o_mud", "beach", "wet", "salt", "road", "verge"):
        S[k] = (S[k] - 14.0 * knock).astype(np.float32)
    on_deck = smoothstep(-0.30, 0.10, deck)
    for k in ("sea_s", "sea_d", "lake_s", "lake_d"):
        S[k] = (S[k] - 160.0 * on_deck).astype(np.float32)

    # -------- cliffs (continuous): sandstone bands, dark depths, chalk streaks
    depth_dark = smoothstep(2.0, 9.0, d_cliff_in)
    cs = 1.6 + 12 * cliff_f
    S["cliff_a"] = (cs - 1.0 * depth_dark).astype(np.float32)
    S["cliff_c"] = (cs - 1.0 - 5.0 * (1 - smoothstep(0.72, 0.86, n_big2)) - 2 * depth_dark).astype(np.float32)
    S["cliff_d"] = (cs - 2.6 + 2.6 * depth_dark).astype(np.float32)
    cl_k = smoothstep(0.0, 0.30, cliff_f)
    wk = smoothstep(0.0, 1.2, cliff)
    for k in list(S):
        if not k.startswith("cliff_"):
            S[k] = (S[k] - 14.0 * cl_k - (40.0 * wk if k.endswith(("_s", "_d")) else 0.0)).astype(np.float32)
    return S


def post(rgb, X, Y, P):
    f = P.fields
    sf = lambda a: P.sample_field(a.astype(np.float32), X, Y)
    d_co, d_ci = sf(f["d_co"]), sf(f["d_ci"])
    d_wo, d_wi = sf(f["d_wo"]), sf(f["d_wi"])
    lum_n = P.sample_field(P.noise(18.0, "lumlow", octaves=2), X, Y)
    shade = 0.94 + 0.12 * lum_n
    shade *= 1 - 0.26 * (1 - smoothstep(0.0, 1.7, d_co))
    shade *= 1 - 0.26 * smoothstep(1.5, 11.0, d_ci)
    cf = sf(f["cf"])
    lip = smoothstep(0.0, 0.03, cf) * (1 - smoothstep(0.03, 0.14, cf))
    rgb = rgb * shade[..., None] + 26 * lip[..., None]
    wet = (1 - smoothstep(0.0, 1.0, d_wo)) * smoothstep(0.0, 0.25, d_wo)
    rgb *= (1 - 0.14 * wet)[..., None]
    foam = (1 - smoothstep(0.0, 0.30, d_wo + d_wi)) * 0.30
    foam = foam * (1 - smoothstep(-0.05, 0.12, cf))
    rgb = rgb * (1 - foam[..., None]) + np.array([225, 240, 240], np.float32) * foam[..., None]
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
    mat_dir, provisional = build_material_dir()
    if provisional:
        print(f"PROVISIONAL textures for {len(provisional)} materials: {', '.join(provisional[:6])}...")
    P = Painter(CB.W, CB.H, mat_dir, seed=31)
    scores = build_scores(P)
    out = ROOT / CB.BAKED_DIR
    written = P.bake(MATERIALS, scores, out, chunk_tiles=20, post=post)
    print(f"baked {len(written)} chunks -> {out}")
    if preview:
        sc = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 4
        full = Image.new("RGB", (CB.W * TILE_PX, CB.H * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        full.resize((CB.W * sc, CB.H * sc), Image.LANCZOS).save(preview)
        print("preview", preview)


if __name__ == "__main__":
    main()
