"""
Bake the six Durotar cave paintings.

    python3 tools/bake_durotar_caves.py [slug ...] [--preview DIR]

slugs: dustwind tiragarde skull_rock drygulch thunder_ridge grotto   (default: all)

Same pipeline as tools/bake_vot_caves.py (seamless materials -> one continuous
painting, registered as ground+water+obstacle chunks).  Each cave is a SPEC:

  floors: {material: [(cx, cy, rx, ry), ...]}   regions where a floor wins
  walls : {material: [(cx, cy, rx, ry), ...]}   regions where a wall type wins
  The first floor / wall material is the base everywhere else.
  pools / lava are read from the built zone (analytic pools + lava tiles).
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

from tools import handbuilt_durotar_caves as C                    # noqa: E402
from tools.bake_vot_caves import (wall_fields, finish_scores,       # noqa: E402
                                  pool_water_scores, make_post)
from tools.terrain_painter import Painter, smoothstep, MASK_PX, TILE_PX  # noqa: E402

TEX = ROOT / "assets/tiles"
CS = "caves/seamless/"
VC = "vot_cluster/"


def M(a, b=None, s=1.0):
    return (a, b, s)


MAT_DIR = ROOT / "assets/tiles/durotar_caves/materials"


def dim(name, f):
    """Darkened copy of a seamless material (generated once, committed)."""
    out = f"durotar_caves/materials/{Path(name).name}_dim{int(f * 100)}"
    fn = TEX / (out + ".png")
    if not fn.exists():
        MAT_DIR.mkdir(parents=True, exist_ok=True)
        im = np.asarray(Image.open(TEX / (name + ".png")).convert("RGB"), np.float32)
        Image.fromarray(np.clip(im * f, 0, 255).astype(np.uint8)).save(fn)
    return out


# ---------------------------------------------------------------- the specs
SPECS = {}

SPECS["dustwind"] = dict(
    build="build_dustwind", seed=41, slug="dustwind",
    materials={
        "floor":   M(VC + "den_floor_a", VC + "den_floor_pebble"),
        "sand":    M(dim(VC + "den_floor_sand", 0.85)),
        "bonesand": M(dim(VC + "vot_bonesand", 0.70)),
        "burrow":  M(VC + "vot_burrow"),
        "nest":    M(VC + "den_floor_nest"),
        "damp":    M(VC + "den_floor_damp"),
        "water_s": M(VC + "den_water_shallow"),
        "water_d": M(VC + "den_water_deep"),
        "wall":    M(VC + "den_wall_a", VC + "den_wall_b"),
        "bones":   M(VC + "den_wall_bones"),
    },
    floor_keys=["floor", "sand", "bonesand", "burrow", "nest", "damp"],
    wall_keys=["wall", "bones"],
    floors={
        "sand": [(40, 59, 10, 4), (40, 41, 15, 8), (40, 33, 7, 4), (28, 39, 6, 5), (52, 39, 6, 5)],
        "bonesand": [(14, 57, 10, 6), (15, 23, 11, 7), (8, 26, 4, 4)],
        "burrow": [(63, 52, 8, 5), (69, 55, 4, 3)],
        "nest": [(66, 26, 10, 7), (40, 11, 14, 8), (40, 5, 7, 4)],
    },
    walls={"bones": [(14, 56, 14, 9), (15, 22, 14, 9), (66, 26, 6, 4)]},
    pools=[C.DW_POOLS],
    cfg=dict(ao=0.42, depth=0.86, lip=26, lip_col=(1.0, 0.82, 0.62), deep_dark=0.35,
             foam_col=(200, 235, 235), glows=[]),
)

SPECS["tiragarde"] = dict(
    build="build_tiragarde", seed=53, slug="tiragarde",
    materials={
        "stone":   M(CS + "keep_floor_a"),
        "yard":    M(CS + "castle_floor_a", CS + "castle_floor_b_a"),
        "rubble":  M(CS + "rubble_strewn_floor_a"),
        "straw":   M(CS + "keep_kennel_a"),
        "deck":    M(dim(CS + "gro_deck_a", 0.85)),
        "wall":    M(CS + "keep_wall_a"),
        "wall_c":  M(CS + "castle_wall_a"),
        "wall_d":  M(CS + "castle_wall_dark_a"),
    },
    floor_keys=["stone", "yard", "rubble", "straw", "deck"],
    wall_keys=["wall", "wall_c", "wall_d"],
    floors={
        "yard": [(45, 56, 18, 8), (45, 74, 8, 3)],
        "rubble": [(76, 34, 8, 8), (60, 56, 4, 3), (34, 62, 3, 2)],
        "straw": [(14, 58, 6, 6), (76, 58, 6, 6)],
        "deck": [(45, 10, 20, 6)],
    },
    walls={"wall_c": [(45, 56, 26, 12), (14, 34, 9, 9), (45, 12, 28, 8)],
           "wall_d": [(76, 34, 11, 11), (45, 75, 12, 5)]},
    pools=[],
    cfg=dict(ao=0.46, depth=0.70, lip=18, lip_col=(0.85, 0.85, 0.9), deep_dark=0.3,
             foam_col=(200, 220, 230), glows=[]),
)

SPECS["skull_rock"] = dict(
    build="build_skull_rock", seed=67, slug="skull_rock",
    materials={
        "floor":   M("vot_cluster/bbc_floor_a", "vot_cluster/bbc_floor_cracks"),
        "ash":     M(CS + "rf_ash_floor_a"),
        "obs":     M("vot_cluster/bbc_floor_obsidian"),
        "bones":   M("vot_cluster/bbc_floor_bones"),
        "straw":   M(CS + "keep_kennel_a"),
        "rune":    M("vot_cluster/bbc_rune_red"),
        "lava":    M(CS + "rf_lava_floor_a"),
        "wall":    M("vot_cluster/bbc_wall_a"),
        "basalt":  M(CS + "rf_basalt_wall_a"),
        "magma":   M(CS + "rf_lava_wall_a"),
        "crys":    M("vot_cluster/bbc_wall_crystal_red"),
    },
    floor_keys=["floor", "ash", "obs", "bones", "straw", "rune"],
    wall_keys=["wall", "basalt", "magma", "crys"],
    floors={
        "ash": [(55, 43, 20, 9), (20, 55, 12, 9)],
        "obs": [(55, 64, 14, 6), (55, 17, 17, 9), (55, 83, 8, 3)],
        "bones": [(89, 28, 10, 6), (100, 60, 6, 4)],
        "straw": [(92, 57, 11, 8)],
        "rune": [(55, 18, 7, 5)],
    },
    walls={"basalt": [(55, 64, 20, 12), (22, 28, 14, 10), (55, 83, 14, 8)],
           "magma": [(55, 41, 24, 10), (20, 55, 16, 12)],
           "crys": [(55, 14, 22, 13), (89, 28, 14, 9)]},
    pools=[],
    lava=True,
    cfg=dict(ao=0.50, depth=0.90, lip=30, lip_col=(1.0, 0.5, 0.3), deep_dark=0.5,
             foam_col=(140, 170, 190), glows=[("d_lava", (170, 62, 12), 2.6, 0.9)]),
)


SPECS["drygulch"] = dict(
    build="build_drygulch", seed=79, slug="drygulch",
    materials={
        "dirt":    M(VC + "vot_clay_a", VC + "vot_clay_pebbles"),
        "hardpan": M(VC + "vot_hardpan"),
        "gravel":  M(VC + "vot_gravel"),
        "bones":   M(dim(VC + "vot_bonesand", 0.82)),
        "camp":    M(VC + "vot_camp_prints"),
        "cinder":  M(VC + "vot_cinder"),
        "mud":     M(VC + "vot_mudshore"),
        "water_s": M(VC + "vot_water_shallow"),
        "water_d": M(VC + "vot_water_deep"),
        "cliff":   M(VC + "vot_cliff_a", VC + "vot_cliff_b"),
        "dark":    M(VC + "vot_rock_dark"),
    },
    floor_keys=["dirt", "hardpan", "gravel", "bones", "camp", "cinder", "mud"],
    wall_keys=["cliff", "dark"],
    floors={
        "hardpan": [(47, 60, 8, 8), (36, 52, 7, 4), (60, 50, 7, 4), (47, 28, 6, 6)],
        "gravel": [(47, 68, 11, 5), (47, 42, 10, 6)],
        "bones": [(22, 42, 10, 7), (70, 24, 8, 6), (47, 13, 14, 7)],
        "camp": [(70, 43, 10, 7)],
        "cinder": [(28, 22, 8, 6)],
        "mud": [(47, 43, 7, 5)],
    },
    walls={},
    pools=[C.DG_POOLS],
    cfg=dict(ao=0.38, depth=0.52, lip=22, lip_col=(1.0, 0.75, 0.5), deep_dark=0.35,
             foam_col=(210, 220, 200), glows=[]),
)

SPECS["thunder_ridge"] = dict(
    build="build_thunder_ridge", seed=83, slug="thunder_ridge",
    materials={
        "basalt":  M(CS + "rf_basalt_floor_a"),
        "gravel":  M(dim(VC + "vot_gravel", 0.62), dim(VC + "vot_gravel_flat", 0.62)),
        "hardpan": M(dim(VC + "vot_hardpan", 0.6)),
        "cinder":  M(VC + "vot_cinder"),
        "mud":     M(VC + "vot_mudshore"),
        "nest":    M(dim(VC + "den_floor_nest", 0.9)),
        "water_s": M(VC + "vot_water_shallow"),
        "water_d": M(VC + "vot_water_deep"),
        "wall":    M(CS + "rf_basalt_wall_a"),
        "cliff":   M(VC + "vot_rock_dark"),
        "storm":   M(CS + "rf_obsidian_wall_a"),
    },
    floor_keys=["basalt", "gravel", "hardpan", "cinder", "mud", "nest"],
    wall_keys=["wall", "cliff", "storm"],
    floors={
        "gravel": [(45, 83, 9, 3), (45, 64, 11, 6), (45, 52, 4, 5), (45, 30, 4, 6), (45, 40, 8, 4)],
        "hardpan": [(32, 62, 5, 3), (58, 62, 5, 3), (72, 58, 8, 5)],
        "cinder": [(22, 25, 9, 6), (45, 12, 12, 6)],
        "mud": [(19, 58, 8, 5), (72, 58, 7, 5)],
        "nest": [(45, 8, 8, 4), (72, 57, 6, 3), (68, 25, 7, 4)],
    },
    walls={"cliff": [(20, 60, 14, 14), (70, 56, 14, 14)],
           "storm": [(45, 10, 24, 12), (22, 25, 14, 10), (68, 25, 14, 10)]},
    pools=[C.TR_POOLS],
    cfg=dict(ao=0.42, depth=0.70, lip=24, lip_col=(0.75, 0.85, 1.0), deep_dark=0.4,
             foam_col=(210, 225, 235), glows=[]),
)

SPECS["grotto"] = dict(
    build="build_grotto", seed=97, slug="grotto",
    materials={
        "floor":   M(CS + "gro_cave_floor_a"),
        "sand":    M(dim(CS + "gro_sand_a", 0.62)),
        "temple":  M(CS + "gro_temple_floor_a"),
        "pearl":   M(dim(CS + "gro_pearl_floor_a", 0.60)),
        "deck":    M(dim(CS + "gro_deck_a", 0.9)),
        "kelp":    M(CS + "gro_kelp_floor_a"),
        "deep":    M(CS + "gro_deep_floor_a"),
        "water_s": M(CS + "gro_tidepool_a"),
        "water_d": M(CS + "gro_deep_floor_a"),
        "wall":    M(CS + "gro_cave_wall_a"),
        "coral":   M(CS + "gro_coral_wall_a"),
        "twall":   M(CS + "gro_temple_wall_a"),
        "vent":    M(CS + "gro_vent_wall_a"),
    },
    floor_keys=["floor", "sand", "temple", "pearl", "deck", "kelp", "deep"],
    wall_keys=["wall", "coral", "twall", "vent"],
    floors={
        "sand": [(55, 89, 10, 4), (88, 50, 12, 9), (55, 76, 6, 3)],
        "temple": [(55, 25, 18, 8), (55, 8, 19, 6), (55, 17, 5, 5)],
        "pearl": [(19, 79, 8, 5)],
        "deck": [(25, 50, 13, 8)],
        "kelp": [(92, 76, 9, 5)],
        "deep": [(55, 68, 14, 5)],
    },
    walls={"coral": [(19, 79, 14, 10), (92, 76, 14, 10), (88, 50, 16, 12)],
           "twall": [(55, 25, 24, 12), (55, 8, 24, 10)],
           "vent": [(55, 5, 10, 4), (25, 50, 18, 12)]},
    pools=[C.SG_POOLS],
    cfg=dict(ao=0.42, depth=0.86, lip=20, lip_col=(0.6, 0.9, 1.0), deep_dark=0.5,
             foam_col=(200, 240, 245), glows=[]),
)


# --------------------------------------------------------------- the baker
def region(P, wp, ellipses, noise=None):
    out = np.zeros((P.mh, P.mw), np.float32)
    for (cx, cy, rx, ry) in ellipses:
        out = np.maximum(out, P.blob(cx, cy, rx, ry, 0.8, wp))
    if noise is not None:
        out = out * noise
    return out


def bake_spec(key, preview=None):
    spec = SPECS[key]
    zone, L = getattr(C, spec["build"])()
    P = Painter(zone.width, zone.height, TEX, seed=spec["seed"])
    wall_f, wall, d_in, d_out = wall_fields(P, zone)
    n_big = P.noise(9.0, key + "_big", octaves=3)
    n_mid = P.noise(4.0, key + "_mid", octaves=3)
    n_fine = P.noise(2.0, key + "_fine", octaves=2)
    wp = P.warp(key + "_regions", amp_tiles=1.5, scale=8.0)
    S = {}
    fk, wk = spec["floor_keys"], spec["wall_keys"]
    S[fk[0]] = np.full_like(n_big, 0.50)
    for k in fk[1:]:
        ell = spec["floors"].get(k, [])
        if not ell:
            S[k] = np.full_like(n_big, -1.0)
            continue
        mod = 0.65 + 0.35 * smoothstep(0.30, 0.60, n_mid)
        S[k] = (0.10 + 0.95 * region(P, wp, ell) * mod).astype(np.float32)
    S[wk[0]] = np.full_like(n_big, 0.0)
    for k in wk[1:]:
        ell = spec["walls"].get(k, [])
        if not ell:
            S[k] = np.full_like(n_big, -1.0)
            continue
        S[k] = (-0.8 + 2.6 * region(P, wp, ell) * smoothstep(0.30, 0.58, n_mid + 0.15 * n_fine)).astype(np.float32)
    S = finish_scores(S, fk, wk, wall_f, d_in, n_big)

    fields = dict(wall_f=wall_f.astype(np.float32), d_in=d_in.astype(np.float32),
                  d_out=d_out.astype(np.float32))
    # lava tiles
    if spec.get("lava"):
        lava_b = np.array([[b == "lava" for b in row] for row in zone.base_layer])
        lava_f = P.tile_mask(lava_b, 0.5, 0.18, key + "_lavam", sigma=0.9, soft=True)
        d_lava = ndi.gaussian_filter(P.edt(~(lava_f > 0)) / MASK_PX, 1.0)
        S["lava"] = (1.4 + 10 * np.clip(lava_f, -0.4, 0.6)).astype(np.float32)
        for k in fk:
            S[k] = np.where(lava_f > 0.05, -2.0, S[k]).astype(np.float32)
        S["lava"] = np.where(wall_f > 0.1, -2.0, S["lava"]).astype(np.float32)
        fields["d_lava"] = d_lava.astype(np.float32)
    # analytic water pools
    if spec["pools"]:
        pools = [pl for grp in spec["pools"] for pl in grp]
        s, d = pool_water_scores(P, S, pools)
        inw = s > 0.45
        for k in fk:
            S[k] = np.where(inw, -2.0, S[k]).astype(np.float32)
        fields["pool_s"] = s.astype(np.float32)
        fields["pool_d"] = d.astype(np.float32)
    # water read from the built zone's shallow/deep water TILES (old-Builder dungeons, e.g. Blackfathom Deeps)
    if spec.get("tile_water"):
        sh_b = np.array([[b in ("shallow_water", "deep_water") for b in row] for row in zone.base_layer])
        dp_b = np.array([[b == "deep_water" for b in row] for row in zone.base_layer])
        s = np.clip(4 * P.tile_mask(sh_b, 0.5, 0.15, key + "_ws", sigma=0.9, soft=True), -4, 6)
        d = np.clip(4 * P.tile_mask(dp_b, 0.5, 0.15, key + "_wd", sigma=0.9, soft=True), -6, 6) if dp_b.any() \
            else np.full_like(s, -4.0)
        S["water_s"] = (1.6 + 10 * s).astype(np.float32)
        S["water_d"] = (1.6 + 10 * s + 10 * d).astype(np.float32)
        inw = s > 0.45
        for k in fk:
            S[k] = np.where(inw, -2.0, S[k]).astype(np.float32)
        for k in wk:
            S[k] = np.where(inw, -2.0, S[k]).astype(np.float32)
        fields["pool_s"] = s.astype(np.float32)
        fields["pool_d"] = d.astype(np.float32)
    mats = dict(spec["materials"])
    # drop materials with no score (e.g. water when no pools)
    for k in list(mats):
        if k not in S:
            del mats[k]
    cfg = dict(spec["cfg"])
    cfg["foam_col"] = np.array(cfg["foam_col"], np.float32)
    P.fields = fields
    out = ROOT / C.BAKED.format(spec["slug"])
    written = P.bake(mats, S, out, chunk_tiles=20, post=make_post(cfg), hscale=0.20)
    print(f"{zone.name}: baked {len(written)} chunks -> {out}")
    if preview:
        full = Image.new("RGB", (zone.width * TILE_PX, zone.height * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        Path(preview).mkdir(parents=True, exist_ok=True)
        pth = Path(preview) / f"{spec['slug']}_full.png"
        full.resize((zone.width * 12, zone.height * 12), Image.LANCZOS).save(pth)
        print("preview", pth)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    if pv and pv in args:
        args.remove(pv)
    for k in (args or list(SPECS)):
        bake_spec(k, pv)
