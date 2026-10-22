"""
Bake an Ashenvale town painting (Astranaar, Splintertree Post, Zoram Strand) from the Ashenvale materials.

    python3 tools/bake_ashenvale_towns.py astranaar|splintertree|zoram|all [--preview out.png] [--scale 8]

Reuses tools/bake_ashenvale.build_scores (forest floor, roads, paving, lakes / moon pools / sea, woods canopy) with the
town module standing in for the zone module (see tools/ashenvale_town_kit.py), then adds the pieces towns need on top:
plank decks (bridges, piers, command dais) and patches of sawdust / trampled yard / scorch (M.EXTRA_PATCHES).
Writes assets/tiles/<key>/baked/ground_<cx>_<cy>.jpg.
"""
import importlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.chdir(Path(__file__).resolve().parent.parent)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import numpy as np
from PIL import Image

from tools import bake_ashenvale as AV
from tools.terrain_painter import Painter, smoothstep, TILE_PX

ROOT = AV.ROOT
TOWNS = {"astranaar": "tools.handbuilt_astranaar", "splintertree": "tools.handbuilt_splintertree",
         "zoram": "tools.handbuilt_zoram"}

MATS = dict(AV.MATERIALS)
MATS.update({
    "sawdust": ("av_sawdust_ground", None, 1.0),
    "pl_horde": ("av_horde_planks", None, 1.0),
    "pl_elf": ("av_elf_planks", None, 1.0),
    "pl_pier": ("av_pier_planks", None, 1.0),
})
EXTRA_REAL = ["av_sawdust_ground", "av_horde_planks", "av_elf_planks", "av_pier_planks"]
LAND = ("floor", "grass", "fern", "root", "mulch", "bell", "rocky", "corrupt", "fel", "burned", "scorch", "satyr", "road",
        "verge", "paving", "plaza", "beach", "wet", "mud", "moonrim", "sawdust")


def build_scores(P, M):
    S = AV.build_scores(P, M)
    off = np.float32(-40.0)
    for k in MATS:
        S.setdefault(k, np.full(P.gx.shape, off, np.float32))
    gx, gy = P.gx, P.gy
    wp = P.warp("regions", amp_tiles=1.6, scale=9.0)
    n_fine = P.noise(2.0, "fine", octaves=2)
    cl_k = smoothstep(0.0, 0.30, P.fields["cf"])
    wd_k = smoothstep(0.0, 0.30, P.fields["wf"])
    # ---- hand-placed ground patches (sawdust yards, scorch, trampled camp earth ...)
    for key, blobs in getattr(M, "EXTRA_PATCHES", {}).items():
        cur = np.maximum(S[key], 0.05)
        for (cx, cy, rx, ry, st) in blobs:
            cur = np.maximum(cur, 0.10 + 1.15 * P.blob(cx, cy, rx, ry, 0.6, wp) * st)
        S[key] = (cur - 14.0 * cl_k - 14.0 * wd_k).astype(np.float32)
    # ---- plank decks on top of everything (bridges, piers, daises)
    F = M.fields(gx, gy)
    deck = F["deck"].astype(np.float32)
    plank = getattr(M, "DECK_MAT", "pl_elf")
    on_deck = smoothstep(-0.30, 0.10, deck)
    for k in list(S):
        if k.startswith(("cliff_", "canopy")) or k in ("pl_horde", "pl_elf", "pl_pier"):
            continue
        S[k] = (S[k] - (160.0 if k.endswith(("_s", "_d")) else 14.0) * on_deck).astype(np.float32)
    S[plank] = (-2.0 + 14 * np.clip(deck + 0.15, 0, 0.6)).astype(np.float32)
    return S


def bake(key, mat_dir, preview=None, sc=8):
    M = importlib.import_module(TOWNS[key])
    L = M.build_layout()
    P = Painter(M.W, M.H, mat_dir, seed=2300 + sum(map(ord, key)))
    P.sealed_land = getattr(L, "sealed_land", [])
    P.sealed_water = getattr(L, "sealed_water", [])
    scores = build_scores(P, M)
    out = ROOT / M.BAKED_DIR
    written = P.bake(MATS, scores, out, chunk_tiles=20, post=AV.post)
    print(f"{key}: baked {len(written)} chunks -> {out}")
    if preview:
        full = Image.new("RGB", (M.W * TILE_PX, M.H * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        full.resize((M.W * sc, M.H * sc), Image.LANCZOS).save(preview)
        print("preview", preview)


def main():
    which = [a for a in sys.argv[1:] if a in TOWNS or a == "all"]
    keys = list(TOWNS) if (not which or which[0] == "all") else which
    preview = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    sc = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 8
    mat_dir, provisional = AV.build_material_dir()
    for stem in EXTRA_REAL:
        src = AV.REAL_DIR / f"{stem}.png"
        Image.open(src).convert("RGB").resize((AV.SIZE, AV.SIZE), Image.LANCZOS).save(Path(mat_dir) / f"{stem}.png")
    for k in keys:
        bake(k, mat_dir, preview.replace(".png", f"_{k}.png") if preview else None, sc)


if __name__ == "__main__":
    main()
