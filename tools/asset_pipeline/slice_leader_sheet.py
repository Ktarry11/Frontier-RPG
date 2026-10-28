"""Slice the faction-leader + MerchantTusk sheet into assets/npcs/leaders/<npc_id>/down.png.

    python3 tools/asset_pipeline/slice_leader_sheet.py sheet.png [--out assets/npcs/leaders]

SEVEN FIGURES, AND NOT ON A GRID. slice_recruit_sheet assigns each connected blob to the cell holding
most of its pixels, which is right for a sheet whose 24 figures really are in a 6x4 lattice. This sheet
is 4 on the top row and 3 on the bottom with a blank fourth cell, and the generator did not space them
evenly - Longtread sits far right of where a quarter-width cell would put him, and the bottom row's
three are nowhere near the first three columns. A fixed grid would hand two leaders to one cell and
leave another empty.

So this finds the figures by their OWN bounding boxes and sorts them into reading order: split on the
vertical gap between the rows, then order each row left to right. The only assumption is that the rows
do not overlap vertically, which is true of any sheet laid out as rows and is checked below.

Same keying as the recruit slicer, deliberately - one magenta key for the project.
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

#: Reading order: top row left-to-right, then bottom row. Matches
#: claude/faction_leader_art_prompts.md.
IDS = ["merchanttusk", "org_thrall", "uc_sylvanas", "taurajo_elder",
       "echo_isles_troll_elder", "ratchet_gazlowe", "kb_codex_master"]

#: MerchantTusk is one troll in three cities, so his one sprite is copied to all three npc_ids.
TUSK_IDS = ["uc_banker", "fw_banker", "org_banker"]

MIN_BLOB = 4000      # px, after dilation - a figure, not a stray speck of anti-aliasing


def key(rgb):
    """Alpha 0..255 from magenta-ness; hard magenta -> 0. Same curve as slice_recruit_sheet."""
    a = rgb.astype(np.int32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mag = np.minimum(r, b) - g
    return np.clip((170 - mag) * 255 // 90, 0, 255).astype(np.uint8)


def extract(sheet):
    rgb = np.asarray(Image.open(sheet).convert("RGB"))
    alpha = key(rgb)
    solid = alpha > 128
    # Dilate before labelling so a staff head separated from the hand by a bright highlight, or a
    # feather tip, stays part of its owner rather than becoming its own "figure".
    lab, n = ndimage.label(ndimage.binary_dilation(solid, iterations=4))

    blobs = []
    for k in range(1, n + 1):
        m = (lab == k) & solid
        if m.sum() < MIN_BLOB:
            continue
        ys, xs = np.where(m)
        blobs.append({"k": k, "x0": xs.min(), "x1": xs.max() + 1,
                      "y0": ys.min(), "y1": ys.max() + 1, "cy": ys.mean()})
    if len(blobs) != len(IDS):
        raise SystemExit(f"found {len(blobs)} figures, expected {len(IDS)} - check the sheet, or raise "
                         f"MIN_BLOB if a figure split, or lower it if a speck was counted")

    # Rows: sort by vertical centre and cut at the largest gap between consecutive centres. Checked
    # rather than assumed - if the "rows" actually overlap, the split is meaningless and we say so.
    blobs.sort(key=lambda b: b["cy"])
    gaps = [(blobs[i + 1]["cy"] - blobs[i]["cy"], i) for i in range(len(blobs) - 1)]
    _, cut = max(gaps)
    top, bottom = blobs[:cut + 1], blobs[cut + 1:]
    if max(b["y1"] for b in top) > min(b["y0"] for b in bottom):
        print("  note: the two rows overlap vertically; ordering by row centre anyway")
    ordered = sorted(top, key=lambda b: b["x0"]) + sorted(bottom, key=lambda b: b["x0"])

    inner = ndimage.binary_erosion(solid, iterations=1)
    ring = inner & ~ndimage.binary_erosion(inner, iterations=2)
    crops = []
    for b, name in zip(ordered, IDS):
        mask = (lab == b["k"]) & inner
        ys, xs = np.where(mask)
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        rgba = np.dstack([rgb, np.where(mask, 255, 0).astype(np.uint8)])[y0:y1, x0:x1].copy()
        r_, g_, b_ = (rgba[..., i].astype(int) for i in range(3))
        # De-magenta the outermost ring: keyed edges keep a pink fringe that reads as a halo in game.
        spill = ring[y0:y1, x0:x1] & (np.minimum(r_, b_) > g_ + 25)
        lim = g_ + 25
        rgba[..., 0] = np.where(spill, np.minimum(r_, lim), r_)
        rgba[..., 2] = np.where(spill, np.minimum(b_, lim), b_)
        crops.append(Image.fromarray(rgba, "RGBA"))
        print(f"  {name:<24}{crops[-1].size}  at x{x0}-{x1} y{y0}-{y1}")
    return crops


def main(sheet, out):
    crops = extract(sheet)
    # ONE SHARED CANVAS, bottom-centred, exactly as the recruit slicer does it: the renderer anchors on
    # height, so figures pasted onto a common canvas all stand on the same ground line and a raised
    # staff just reaches higher instead of shrinking the person holding it.
    cw = max(c.width for c in crops) + 8
    ch = max(c.height for c in crops) + 4
    for name, im_ in zip(IDS, crops):
        canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        canvas.paste(im_, ((cw - im_.width) // 2, ch - im_.height - 2), im_)
        targets = TUSK_IDS if name == "merchanttusk" else [name]
        for t in targets:
            d = os.path.join(out, t)
            os.makedirs(d, exist_ok=True)
            # Four identical facings, same as every other NPC in the project - the walk-cycle pass is
            # separate future work and get_npc_sprite does not care that the files match.
            for face in ("down", "left", "right", "up"):
                canvas.save(os.path.join(d, f"{face}.png"))
        print(f"  wrote {name} -> {', '.join(targets)}")
    print(f"canvas {cw}x{ch}")


if __name__ == "__main__":
    out = "assets/npcs/leaders"
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    main(sys.argv[1], out)
