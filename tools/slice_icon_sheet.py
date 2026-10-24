#!/usr/bin/env python3
"""Slice an 8x6 magenta-background icon sheet into 48 transparent square PNGs.

    python3 tools/slice_icon_sheet.py trash  tools/icon_sheets/vendor_trash_sheet.png
    python3 tools/slice_icon_sheet.py quest  tools/icon_sheets/quest_items_sheet.png

Each cell is keyed against #FF00FF (soft alpha ramp + magenta despill so dark outlines don't get a pink halo),
cropped to the icon's bounding box, padded to a square and resized to 96x96.  Output names come from the NAMES
tables below (same order as the prompts in claude/vendor_trash_icon_prompts.md and claude/quest_item_icon_prompts.md).
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
COLS, ROWS = 8, 6
OUT_SIZE = 96

NAMES = {
    "trash": ("vendor_trash", [
        "vt_pelt", "vt_claw", "vt_fang", "vt_tusk", "vt_feathers", "vt_horn_chunk", "vt_fur_tuft", "vt_wing_membrane",
        "vt_raw_hide", "vt_chitin_plate", "vt_stinger", "vt_mandibles", "vt_venom_gland", "vt_silk_ball", "vt_egg_sac", "vt_dried_scales",
        "vt_fish_scales", "vt_fin", "vt_shell", "vt_pearl", "vt_bone", "vt_jawbone", "vt_shroud", "vt_grave_dust",
        "vt_ghost_vial", "vt_grave_ring", "vt_core", "vt_shard", "vt_slag", "vt_mote", "vt_geode", "vt_ash",
        "vt_demon_horn", "vt_brimstone", "vt_sigil", "vt_charred_claw", "vt_bark", "vt_seed_pod", "vt_thorn_vine", "vt_spore_cap",
        "vt_broken_dagger", "vt_tin_cup", "vt_locket", "vt_map_scrap", "vt_dice", "vt_idol", "vt_arrowheads", "vt_rags",
    ]),
    "quest": ("quest_items", [
        "qi_letter", "qi_scroll", "qi_ledger", "qi_page", "qi_papers", "qi_journal", "qi_chart", "qi_ticket",
        "qi_key_iron", "qi_key_brass", "qi_shackle", "qi_signet", "qi_ward_seal", "qi_dog_tag", "qi_prayer_beads", "qi_coin_pouch",
        "qi_crate", "qi_strongbox", "qi_powder_keg", "qi_seed_sack", "qi_flask", "qi_vial", "qi_clay_jar", "qi_egg",
        "qi_ore", "qi_crystal", "qi_amber", "qi_coral", "qi_gem", "qi_tablet", "qi_headstone", "qi_heart_stone",
        "qi_herbs", "qi_petals", "qi_moss", "qi_pumpkin", "qi_seed_packet", "qi_wreath", "qi_dewleaf", "qi_root",
        "qi_horn", "qi_lantern", "qi_harpoon", "qi_pennant", "qi_totem", "qi_trophy_cord", "qi_chalice", "qi_gold_thread",
    ]),
}


def key_magenta(rgb):
    """-> RGBA float array. Soft alpha from distance to #FF00FF, un-mix the magenta from edge pixels, then strip the
    remaining magenta spill from pixels touching the background (fur / feather tips pick up a purple fringe)."""
    from scipy import ndimage
    mag = np.array([255.0, 0.0, 255.0])
    dist = np.sqrt(((rgb - mag) ** 2).sum(axis=2))
    alpha = np.clip((dist - 80.0) / 100.0, 0.0, 1.0)
    a = alpha[..., None]
    safe = np.maximum(a, 1e-3)
    clean = np.clip((rgb - (1.0 - a) * mag) / safe, 0, 255)
    clean = np.where(a > 0.02, clean, 0.0)
    near_bg = ndimage.binary_dilation(alpha < 0.05, iterations=3)
    spill = np.maximum(0.0, np.minimum(clean[..., 0], clean[..., 2]) - clean[..., 1] * 1.05 - 8.0)
    spill = np.where(near_bg & (alpha > 0.0), spill, 0.0)
    clean[..., 0] -= spill
    clean[..., 2] -= spill
    return np.dstack([np.clip(clean, 0, 255), alpha * 255.0])


def slice_sheet(kind, sheet_path, out_dir=None):
    from scipy import ndimage
    folder, names = NAMES[kind]
    out_dir = Path(out_dir) if out_dir else ROOT / "assets" / "icons" / folder
    out_dir.mkdir(parents=True, exist_ok=True)
    im = Image.open(sheet_path).convert("RGB")
    W, H = im.size
    rgba = key_magenta(np.asarray(im).astype(np.float64))
    cw, ch = W / COLS, H / ROWS
    # The generated sheets are not on a perfect pixel grid (rows drift by ~10px), so icons are found as connected
    # blobs (dilated so multi-part icons like dice or arrowheads stay together) and assigned to the grid cell that
    # holds their centre.
    solid = rgba[..., 3] > 24
    solid[:4, :] = solid[-4:, :] = False
    solid[:, :4] = solid[:, -4:] = False
    labels, n = ndimage.label(ndimage.binary_dilation(solid, iterations=3))
    cells = {}
    for lab in range(1, n + 1):
        ys, xs = np.where((labels == lab) & solid)
        if len(ys) < 60:
            continue
        cell = (int(ys.mean() // ch), int(xs.mean() // cw))
        cells.setdefault(cell, []).append((labels == lab) & solid)
    problems = []
    written = 0
    for idx, name in enumerate(names):
        r, c = divmod(idx, COLS)
        blobs = cells.get((r, c))
        if not blobs:
            problems.append(f"{name}: no icon found in cell {r},{c}")
            continue
        if len(blobs) > 1:
            problems.append(f"{name}: {len(blobs)} separate blobs merged")
        mask = np.logical_or.reduce(blobs)
        ys, xs = np.where(mask)
        bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        crop = rgba[by0:by1, bx0:bx1].copy()
        crop[..., 3] = np.where(mask[by0:by1, bx0:bx1], crop[..., 3], 0)
        side = int(max(crop.shape[0], crop.shape[1]) * 1.10) + 2
        canvas = np.zeros((side, side, 4))
        oy, ox = (side - crop.shape[0]) // 2, (side - crop.shape[1]) // 2
        canvas[oy:oy + crop.shape[0], ox:ox + crop.shape[1]] = crop
        img = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8), "RGBA").resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS)
        img.save(out_dir / f"{name}.png")
        written += 1
    extra = [k for k in cells if k[0] >= ROWS or k[1] >= COLS]
    print(f"{kind}: wrote {written} icons to {out_dir}")
    for p in problems + [f"stray blob in cell {k}" for k in extra]:
        print("  WARN", p)
    return problems


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in NAMES:
        sys.exit(__doc__)
    slice_sheet(sys.argv[1], sys.argv[2])
