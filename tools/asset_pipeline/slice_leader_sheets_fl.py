"""Slice the leader sheets FL1 and FL2 (docs/faction_leader_art_prompts.md, 22 Nov 2026) into
assets/npcs/leaders/<npc_id>/{down,left,right,up}.png.

    python3 tools/asset_pipeline/slice_leader_sheets_fl.py FL1 sheet.png
    python3 tools/asset_pipeline/slice_leader_sheets_fl.py FL2 sheet.png

Twelve figures in three rows of four, but the generator doesn't keep to its cells (FL2 came back 1199x1312 with the
bottom of the image empty), so this finds each figure by its own outline, exactly as slice_leader_sheet does, and puts
them in reading order: rows cut at the big gaps between figure centres, each row left to right. Same magenta key and the
same shared bottom-centred canvas, so everyone on a sheet stands on one ground line.
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

from tools.asset_pipeline.slice_leader_sheet import key, MIN_BLOB

SHEETS = {
    "FL1": ["cw_thane_ashhold", "es_arch_druid", "tm_elder", "tl_sunreach_magister",
            "dw_halyna", "mg_sandvik", "gs_zankaji", "au_first_speaker",
            "ab_unsworn_scholar", "ab_wreck_captain", "af_warden_prime", "lw_surveyor"],
    "FL2": ["ce_keeper", "ff_last_magistrate", "ff_long_memory", "ce_golem_scholar",
            "af_old_warden", "af_keel_engineer", "ab_lancer_deserter", "ab_wreck_surgeon",
            "sc_warleader", "sc_envoy", "ce_tether_lead", "af_tilt_lead"],
}
ROWS, COLS = 3, 4


def extract(sheet, n):
    rgb = np.asarray(Image.open(sheet).convert("RGB"))
    solid = key(rgb) > 128
    lab, k = ndimage.label(ndimage.binary_dilation(solid, iterations=4))
    blobs = []
    for i in range(1, k + 1):
        m = (lab == i) & solid
        if m.sum() < MIN_BLOB:
            continue
        ys, xs = np.where(m)
        blobs.append({"k": i, "x0": xs.min(), "y0": ys.min(), "y1": ys.max() + 1, "cy": (ys.min() + ys.max()) / 2})
    if len(blobs) != n:
        raise SystemExit(f"found {len(blobs)} figures, expected {n}")
    blobs.sort(key=lambda b: b["cy"])
    gaps = sorted(range(len(blobs) - 1), key=lambda i: blobs[i + 1]["cy"] - blobs[i]["cy"], reverse=True)[:ROWS - 1]
    rows, start = [], 0
    for cut in sorted(gaps) + [len(blobs) - 1]:
        rows.append(sorted(blobs[start:cut + 1], key=lambda b: b["x0"]))
        start = cut + 1
    if [len(r) for r in rows] != [COLS] * ROWS:
        raise SystemExit(f"rows came out {[len(r) for r in rows]}, expected {[COLS] * ROWS}")
    inner = ndimage.binary_erosion(solid, iterations=1)
    ring = inner & ~ndimage.binary_erosion(inner, iterations=2)
    crops = []
    row_of = {b["k"]: i for i, r in enumerate(rows) for b in r}
    for b in [b for r in rows for b in r]:
        mask = (lab == b["k"]) & inner
        ys, xs = np.where(mask)
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        rgba = np.dstack([rgb, np.where(mask, 255, 0).astype(np.uint8)])[y0:y1, x0:x1].copy()
        r_, g_, b_ = (rgba[..., i].astype(int) for i in range(3))
        spill = ring[y0:y1, x0:x1] & (np.minimum(r_, b_) > g_ + 25)
        lim = g_ + 25
        rgba[..., 0] = np.where(spill, np.minimum(r_, lim), r_)
        rgba[..., 2] = np.where(spill, np.minimum(b_, lim), b_)
        crops.append((row_of[b["k"]], Image.fromarray(rgba, "RGBA")))
    # A row drawn bigger than the others (FL2's bottom row came back a quarter taller) is brought down to the
    # others' size: the renderer scales the whole canvas to one height, so a big row would shrink everyone else.
    med = {i: float(np.median([c.height for r, c in crops if r == i])) for i in range(ROWS)}
    base = float(np.median(list(med.values())))
    out = []
    for r, c in crops:
        f = base / med[r]
        if abs(f - 1) > 0.08:
            c = c.resize((max(1, round(c.width * f)), max(1, round(c.height * f))), Image.LANCZOS)
        out.append(c)
    return out


def main(which, sheet, out="assets/npcs/leaders"):
    ids = SHEETS[which]
    crops = extract(sheet, len(ids))
    cw = max(c.width for c in crops) + 8
    ch = max(c.height for c in crops) + 4
    for nid, im in zip(ids, crops):
        canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        canvas.paste(im, ((cw - im.width) // 2, ch - im.height - 2), im)
        d = os.path.join(out, nid)
        os.makedirs(d, exist_ok=True)
        for face in ("down", "left", "right", "up"):
            canvas.save(os.path.join(d, f"{face}.png"))
        print(f"  {nid:<22}{im.size}")
    print(f"{which}: {len(ids)} written, canvas {cw}x{ch}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
