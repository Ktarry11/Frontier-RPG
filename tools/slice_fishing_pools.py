#!/usr/bin/env python3
"""Slice Kyle's fishing pool sheet (6 x 5) into the 30 pool, junk and salvage sprites.

    python3 tools/slice_fishing_pools.py

Sheet: tools/icon_sheets/fishing_pools.png. Cell order and file names are the ones in
claude/fishing_pool_art_prompts.md. Uses slice_icon_sheet's soft magenta keying, which is right
for these: a pool is a patch of water whose edge fades out.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import slice_icon_sheet as S  # noqa: E402

OUT = ROOT / "assets" / "gathering_nodes" / "fishing_pools"
NAMES = [
    "pool_fresh", "pool_river", "pool_coast", "pool_whirlpool", "pool_bubbling", "pool_reeds",
    "pool_swamp", "pool_jungle", "pool_oasis", "pool_brine", "pool_ice_hole", "pool_cave",
    "pool_plagued", "pool_deep_sea", "pool_storm", "pool_glowing", "pool_lava", "pool_moonlit",
    "junk_floating", "junk_wreckage", "junk_crate", "junk_barrel", "junk_net", "junk_goblin_scrap",
    "salvage_chest", "salvage_bottle", "salvage_bones", "salvage_oil_slick", "pool_blood", "junk_seaweed",
]


def defringe(path):
    """Fade the purple halo out of a sprite's soft edge.

    The water was painted fading into magenta, so the outer ring of every pool is water mixed
    with pink, and the keying leaves it as a violet rim. Near the edge only, a pixel loses alpha
    in proportion to how much more red-and-blue it has than green; then the whole edge is feathered
    a little so the pool sits in the game's water instead of on it.
    """
    import numpy as np
    from PIL import Image
    from scipy import ndimage
    a = np.asarray(Image.open(path).convert("RGBA")).astype(np.float64)
    alpha = a[..., 3]
    edge = ndimage.binary_dilation(alpha < 12, iterations=12)
    pink = np.clip((np.minimum(a[..., 0], a[..., 2]) - a[..., 1] - 6.0) / 34.0, 0.0, 1.0)
    alpha = np.where(edge, alpha * (1.0 - pink), alpha)
    depth = ndimage.distance_transform_edt(alpha > 40)
    alpha = alpha * np.clip(depth / 5.0, 0.0, 1.0)
    a[..., 3] = alpha
    Image.fromarray(a.round().astype(np.uint8), "RGBA").save(path)


def main():
    S.COLS, S.ROWS, S.OUT_SIZE = 6, 5, 96
    S.NAMES["fishing_pools"] = ("fishing_pools", NAMES)
    problems = S.slice_sheet("fishing_pools", ROOT / "tools/icon_sheets/fishing_pools.png", out_dir=OUT)
    for path in OUT.glob("*.png"):
        defringe(path)
    print(f"{len(list(OUT.glob('*.png')))} sprites in {OUT.relative_to(ROOT)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
