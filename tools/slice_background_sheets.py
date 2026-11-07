#!/usr/bin/env python3
"""Cut generated 2x2 background sheets into named pack files.

    PYTHONPATH=. python3 tools/slice_background_sheets.py SHEET... [--apply]

Kyle generated eight 1408x768 sheets on 7 Nov against the prompts in
docs/background_prompts.md - twenty backgrounds, which closes every thin
pack tools/qa_combat_backgrounds.py was reporting plus the coast pack that
did not exist at all.

GEOMETRY. Each sheet is 2x2, so a cell is 704x384. Two different kinds of
sheet came back and they need different handling, which is why this takes a
manifest rather than slicing blindly:

  PLAIN      the painterly sheets. Art runs to the cell edge with a thin
             black gutter between cells; trimmed by a few pixels.

  FRAMED     the photoreal coast sheet came back with a white double frame
             and a CAPTION under each image ("Tropical Cove"). Slicing that
             naively bakes the caption into the background, and a label
             reading "Basalt Cliffs" would then sit behind a boss fight
             forever. The frame is found by looking for rows and columns
             that are mostly near-white, and the crop is taken inside it.

NO DOWNSCALING. Existing pack art ranges from 291x224 to 524x379 and the
loader scales to the screen anyway, so these land at their native ~650x320
and look better than what they sit beside.
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKS = ROOT / "assets" / "backgrounds"

COLS = ROWS = 2

#: sheet key -> (kind, [(row, col, pack, stem, what it is)])
#: The description is the record of WHY a cell landed where it did; it is
#: the only thing that makes a wrong call reviewable later.
MANIFEST = {
    "3e8f539f": ("framed", [
        (0, 0, "coast", "c_tropical_cove", "palms and a wrecked hull on turquoise shallows"),
        (0, 1, "coast", "c_basalt_cliffs", "grey northern shore, sea stacks, cold surf"),
        (1, 0, "coast", "c_harbor_lighthouse", "wooden dock and lighthouse over rough water"),
        (1, 1, "coast", "c_mediterranean_ruins", "sandstone arches above clear shallows"),
    ]),
    "b61a0a2e": ("plain", [
        (0, 0, "arena", "s_arena_pit", "gladiator pit, raked stone tiers, crowd"),
        (0, 1, "hive", "s_hive_comb", "honeycomb chamber in amber resin"),
        (1, 0, "fungal", "s_fungal_glow", "giant glowing mushroom cavern"),
        (1, 1, "salt_flat", "s_bone_pan", "cracked white hardpan, bones, red mesas"),
    ]),
    "d5084454": ("plain", [
        (0, 0, "savanna", "s_savanna_acacia", "acacia over golden grass, mesas behind"),
        (0, 1, "savanna_oasis", "s_oasis_pool", "palm-ringed pool in a canyon"),
        (1, 0, "sky", "s_sky_sunrise", "floating ruins above a cloud sea at sunrise"),
        (1, 1, "sky", "s_sky_night", "night sky, crescent moon, nebula"),
    ]),
    "cc9c45ea": ("plain", [
        (0, 0, "crystal", "s_crystal_pool", "teal crystal cavern over still water"),
        (0, 1, "savanna", "s_thorn_pass", "red rock pass under thorn arches and spikes"),
        (1, 0, "jungle", "s_jungle_temple", "stepped temple and idols under canopy"),
        (1, 1, "coast", "c_sunken_temple", "drowned temple steps and runed pillars"),
    ]),
    # Second batch, 7 Nov. Kyle: "We now have like 60+ backgrounds. No reason
    # to reuse the same background over and over. here are some for tanaris,
    # abyssal sands, and glittervein + others". Two of these retire a
    # ZONE_BACKGROUND override that pointed a named zone at the generic
    # desert pack - which is the reuse he is describing, written down.
    "de53f8e0": ("plain", [
        (0, 0, "desert", "s_tanaris_wreck", "sand dunes, wrecked machinery, bones, sandstone arches"),
        (0, 1, "abyssal_sands", "s_abyssal_monoliths", "violet sky, black runed monoliths, crystal shards"),
        (1, 0, "glittervein", "s_glittervein_seam", "red canyon split by green-gold crystal seams"),
        (1, 1, "desert", "s_desert_night", "moonlit dunes, lit arches and a town beyond"),
    ]),
    "7b0ceafd": ("plain", [
        (0, 0, "jungle", "s_jungle_volcano", "red crystal outcrops under a smoking volcano"),
        (0, 1, "frozen_ruins", "s_aurora_ruins", "snowbound ruins and blue crystal under an aurora"),
        (1, 0, "fire_dungeon", "s_lava_hall", "pillared hall over molten rock"),
        (1, 1, "nautical/Flooded", "s_coral_temple", "sunlit coral ruins on the sea floor"),
    ]),
    # Third batch, 7 Nov: settlements. The keep pack had four images for every
    # fort, gate and garrison in the game; these two double it. The hill road
    # goes to mossy_forest because that pack is already the Hillsbrad read
    # (farm cottage, barn) rather than deep woodland.
    "f6d0a66d": ("plain", [
        (0, 0, "mossy_forest", "s_hill_watchtowers", "fenced farm road through green hills, watchtowers"),
        (0, 1, "coast", "c_harbor_town", "timbered harbour town, dock, moored ships"),
        (1, 0, "keep", "s_keep_breached", "breached curtain wall, banners, autumn peaks"),
        (1, 1, "keep", "s_keep_gatehouse", "stone gatehouse and portcullis under storm"),
    ]),
    "304798a9": ("plain", [
        (0, 0, "mountain", "s_canyon_bridges", "red canyon spanned by rope bridges"),
        (0, 1, "coast", "c_sea_stacks", "sea stacks and small boats over turquoise"),
        (1, 0, "mossy_forest", "s_autumn_aspens", "autumn aspens below snowy peaks"),
        (1, 1, "mountain", "s_autumn_ridge", "autumn ridge overlooking a misty range"),
    ]),
}


def _thin_runs(idx, max_len=4):
    """Keep only indices belonging to runs of at most `max_len` consecutive
    values - i.e. keylines, not expanses of bright sky."""
    import numpy as np
    if len(idx) == 0:
        return idx
    keep = []
    start = 0
    for i in range(1, len(idx) + 1):
        if i == len(idx) or idx[i] != idx[i - 1] + 1:
            if i - start <= max_len:
                keep.extend(idx[start:i])
            start = i
    return np.array(keep, dtype=idx.dtype)


def _frame_crop(cell):
    """Inside the white double frame, above the caption."""
    import numpy as np
    a = np.asarray(cell).astype(int)
    near_white = (a.min(axis=2) > 200)
    rows = np.where(near_white.mean(axis=1) > 0.5)[0]
    cols = np.where(near_white.mean(axis=0) > 0.5)[0]
    # A FRAME LINE IS THIN, and that is the only reliable thing about it.
    # Position is not enough: c_mediterranean_ruins has a bright sky and sea
    # haze filling rows 31-86 solid near-white, which an "it is near the
    # edge" rule happily mistook for a frame and cropped the picture down to
    # 243px. A real keyline is one to four rows; a sky is fifty-six.
    h, w = a.shape[:2]
    rows = _thin_runs(rows)
    cols = _thin_runs(cols)
    rows = rows[(rows < h * 0.25) | (rows > h * 0.75)]
    cols = cols[(cols < w * 0.25) | (cols > w * 0.75)]
    if len(rows) < 2 or len(cols) < 2:
        return cell
    # THE INNERMOST LINE, not the outermost. The coast sheet has a DOUBLE
    # frame (lines at rows 10-11 and 18-19), so cropping to the outer one
    # leaves the inner one baked into the background - which is what shipped
    # a white border down the side of c_mediterranean_ruins on the first
    # pass. Take the last line in the top quarter and the first in the
    # bottom quarter.
    mid_r, mid_c = h / 2, w / 2
    top = rows[rows < mid_r].max() if (rows < mid_r).any() else rows.min()
    bottom = rows[rows > mid_r].min() if (rows > mid_r).any() else rows.max()
    left = cols[cols < mid_c].max() if (cols < mid_c).any() else cols.min()
    right = cols[cols > mid_c].min() if (cols > mid_c).any() else cols.max()
    if bottom - top < h * 0.4 or right - left < w * 0.4:
        return cell
    pad = 2
    return cell.crop((left + pad, top + pad, right - pad, bottom - pad))


def _plain_crop(cell, trim=4):
    """Trim the gutter, then take the frame off if there is one.

    A fixed trim is not enough on its own: three of the four painterly
    sheets also came back with a thin white keyline, and 4px left a bright
    border baked into savanna, oasis and both sky backgrounds. Running the
    same frame detector over every sheet and falling back to the plain trim
    when it finds nothing handles both kinds without a per-sheet flag.
    """
    w, h = cell.size
    inner = _frame_crop(cell)
    if inner.size != cell.size:
        return inner
    return cell.crop((trim, trim, w - trim, h - trim))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sheets", nargs="+", type=Path)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", default=None,
                    help="write here instead of assets/backgrounds (for review)")
    args = ap.parse_args()

    from PIL import Image
    dest_root = Path(args.out) if args.out else PACKS
    written = []
    for path in args.sheets:
        key = next((k for k in MANIFEST if k in path.name), None)
        if key is None:
            print(f"  no manifest entry for {path.name}; skipped")
            continue
        kind, cells = MANIFEST[key]
        sheet = Image.open(path).convert("RGB")
        cw, ch = sheet.width // COLS, sheet.height // ROWS
        for r, c, pack, stem, what in cells:
            if pack is None or c >= COLS:
                continue
            cell = sheet.crop((c * cw, r * ch, (c + 1) * cw, (r + 1) * ch))
            art = _frame_crop(cell) if kind == "framed" else _plain_crop(cell)
            target = dest_root / pack / f"{stem}.png"
            if args.apply:
                target.parent.mkdir(parents=True, exist_ok=True)
                art.save(target)
            written.append((pack, stem, art.size, what))

    by_pack = {}
    for pack, stem, size, what in written:
        by_pack.setdefault(pack, []).append((stem, size, what))
    print(f"  {len(written)} backgrounds across {len(by_pack)} packs\n")
    for pack in sorted(by_pack):
        existing = len(list((PACKS / pack).glob("*.png"))) if (PACKS / pack).exists() else 0
        print(f"  {pack}  ({existing} already)")
        for stem, size, what in by_pack[pack]:
            print(f"      {stem:26}{size[0]:>5}x{size[1]:<5} {what}")
    print("\n  written" if args.apply else "\n  (report only; pass --apply to write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
