#!/usr/bin/env python3
"""Slice the 8x5 magenta-background material sheets (cloth / leather / planks) into 32x32 transparent PNGs.

    python3 tools/slice_material_sheets.py            # all three
    python3 tools/slice_material_sheets.py cloth

Sheets live in tools/icon_sheets/; cell order matches claude/cloth_leather_art_prompts.md and claude/plank_art_prompts.md.
Output: assets/gathering_nodes/<folder>/<prefix>_<slug>.png
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from slice_icon_sheet import key_magenta  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
COLS, ROWS, OUT = 8, 5, 32

CLOTH = ["linen", "wool", "cotton", "hempen", "silk", "mageweave", "spidersilk", "dusk_velvet",
         "gossamer", "thistledown", "runecloth", "netherweave", "frostweave", "emberweave", "moonsilk", "shadowsilk",
         "starweave", "bloodsilk", "felcloth", "soulcloth", "windwool", "imperial_silk", "voidweave", "sunthread",
         "dreamsilk", "chronoweave", "abyssal_velvet", "stormweave", "lightwoven", "wyrmsilk", "phoenix_cloth", "arcanoweave",
         "titanweave", "spiritwoven", "nightmare_lace", "ghostgauze", "starsilk", "worldweave", "genesis_cloth", "primordial_weave"]
LEATHER = ["scrap", "light", "medium", "heavy", "thick", "rugged", "cragscale", "stormscale",
           "stonebound", "dredged", "fiendish", "pristine", "savage", "frostscale", "emberscale", "mossback",
           "duskfang", "bloodtanned", "wyvern", "basilisk", "hydra", "netherdrake", "frostwyrm", "behemoth",
           "manticore", "chimera", "phoenix", "kraken", "thunderlizard", "nightsaber", "lavahound", "sandwurm",
           "voidstalker", "dreamstag", "sunhawk", "chronodrake", "abyssal", "worldserpent", "primordial", "genesis"]
PLANKS = ["ashwood", "oakheart", "softpine", "driftwood", "redbark", "ironbark", "duskwood", "goldenleaf",
          "bramblewood", "marshwillow", "silverbark", "emberwood", "frostpine", "starleaf", "sapglow", "bloodwood",
          "moonpetal", "thornveil", "voidwood", "sunheart", "felbark", "starforged_oak", "bloodroot", "frostheart",
          "molten_ironwood", "stormoak", "nightshade", "radiant_ashenwood", "dreamwillow", "worldbranch", "chronoak", "abysswood",
          "sunderedwood", "wyrmscak", "astral_birch", "ebonthorn", "sylvanheart", "cataclysm_root", "genesis_bough", "worldtree_heartwood"]
BOLTS = ["linen", "wool", "cotton", "hempen", "silk", "mageweave", "spidersilk", "dusk_velvet",
         "gossamer", "thistledown", "runecloth", "netherweave", "frostweave", "emberweave", "moonsilk", "shadowsilk",
         "starweave", "bloodsilk", "felcloth", "soulcloth", "windwool", "imperial_silk", "voidweave", "sunthread",
         "dreamsilk", "chronoweave", "abyssal_velvet", "stormweave", "lightwoven", "wyrmsilk", "phoenix_cloth", "arcanoweave",
         "titanweave", "spiritwoven", "nightmare_lace", "ghostgauze", "starsilk", "worldweave", "genesis_cloth", "primordial_weave"]
SHEETS = {"cloth": ("cloth_sheet.png", "cloth", "cloth", CLOTH),
          "leather": ("leather_sheet.png", "leather", "leather", LEATHER),
          "planks": ("plank_sheet.png", "planks", "plank", PLANKS),
          "bolts": ("bolt_sheet.png", "cloth", "bolt", BOLTS)}


def slice_sheet(kind):
    from scipy import ndimage
    fname, folder, prefix, slugs = SHEETS[kind]
    out_dir = ROOT / "assets" / "gathering_nodes" / folder
    out_dir.mkdir(parents=True, exist_ok=True)
    im = Image.open(ROOT / "tools" / "icon_sheets" / fname).convert("RGB")
    W, H = im.size
    rgba = key_magenta(np.asarray(im).astype(np.float64))
    cw, ch = W / COLS, H / ROWS
    solid = rgba[..., 3] > 24
    solid[:4, :] = solid[-4:, :] = False
    solid[:, :4] = solid[:, -4:] = False
    labels, n = ndimage.label(ndimage.binary_dilation(solid, iterations=3))
    cells = {}
    for lab in range(1, n + 1):
        ys, xs = np.where((labels == lab) & solid)
        if len(ys) < 60:
            continue
        cells.setdefault((int(ys.mean() // ch), int(xs.mean() // cw)), []).append((labels == lab) & solid)
    problems, written = [], 0
    for idx, slug in enumerate(slugs):
        r, c = divmod(idx, COLS)
        blobs = cells.get((r, c))
        if not blobs:
            problems.append(f"{slug}: nothing in cell {r},{c}")
            continue
        if len(blobs) > 1:
            problems.append(f"{slug}: {len(blobs)} blobs merged")
        mask = np.logical_or.reduce(blobs)
        ys, xs = np.where(mask)
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        crop = rgba[y0:y1, x0:x1].copy()
        crop[..., 3] = np.where(mask[y0:y1, x0:x1], crop[..., 3], 0)
        side = int(max(crop.shape[:2]) * 1.06) + 2
        canvas = np.zeros((side, side, 4))
        oy, ox = (side - crop.shape[0]) // 2, (side - crop.shape[1]) // 2
        canvas[oy:oy + crop.shape[0], ox:ox + crop.shape[1]] = crop
        img = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8), "RGBA").resize((OUT, OUT), Image.LANCZOS)
        img.save(out_dir / f"{prefix}_{slug}.png")
        written += 1
    print(f"{kind}: wrote {written}/{len(slugs)} icons to {out_dir}")
    for p in problems + [f"stray blob in cell {k}" for k in cells if k[0] >= ROWS or k[1] >= COLS]:
        print("  WARN", p)


if __name__ == "__main__":
    for k in (sys.argv[1:] or SHEETS):
        slice_sheet(k)
