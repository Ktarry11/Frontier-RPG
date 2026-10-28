#!/usr/bin/env python3
"""Slice a ground-TILE sheet into seamless 256x256 textures.

    python3 tools/slice_tile_sheet.py aspen
    python3 tools/slice_tile_sheet.py aspen --preview /tmp/aspen_tiles.png

WHY THIS FILE EXISTS. The Underdark's 48 tiles were sliced with a throwaway script that never got
committed (commit 3db1a14 added the sheet and the building slicer, but nothing that cuts tiles). The
next sheet therefore had nothing to run, and the knowledge of how it was done lived only in a chat log.
This is that script, written down.

TILES ARE NOT SPRITES, AND THE DIFFERENCE IS THE WHOLE JOB:

  * NO MAGENTA KEY. A tile is opaque ground that runs flush to its own edges. Keying it would eat the
    darkest pixels of a charred-earth texture and leave holes in the floor.
  * CUT ON ARITHMETIC CELLS, not connected blobs. The building slicer finds sprites as blobs because a
    building floats on magenta with space around it; a tile has no silhouette to find - it fills its cell
    edge to edge, and its neighbours are touching it.
  * INSET BEFORE RESIZE. Generated sheets never land on a perfect pixel grid, so a cell cut at its exact
    arithmetic bounds picks up a sliver of the tile next door along one edge. That sliver is invisible in
    the sheet and screams once the texture tiles. Every cell is cropped a few pixels inside its bounds.
  * SEAMLESS EDGES. Each tile is then edge-blended with itself so it repeats without a visible grid. This
    is the step that turns a photo of ground into a texture.

ROWS DRIFT. Image generators do not divide 1024 by 6 evenly, and a sheet whose rows creep by a few pixels
will slice fine at the top and badly at the bottom. A set may therefore declare explicit row boundaries
instead of even division - see ROWS_Y in the set definitions.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT_PX = 256          # every tile ships at 256x256, matching the Underdark set
INSET = 4             # pixels trimmed off each cell edge before resizing (see docstring)
BLEND = 22            # width of the seamless edge blend, in output pixels

SETS = {}


def _set(key, cols, rows, sheet, out_dir, names, rows_y=None, drop=()):
    """names: whitespace-separated, cols*rows of them. `drop` names are sliced past but not written."""
    names = names.split()
    assert len(names) == cols * rows, (key, len(names), cols * rows)
    SETS[key] = dict(cols=cols, rows=rows, sheet=sheet, out=out_dir, names=names,
                     rows_y=rows_y, drop=set(drop))


# ---------------------------------------------------------------------------------------------------------
# THE ASPEN WILDERNESS (Northern Thousand Needles). 8x6 = 48 cells.
#
# Kyle, 2026-10-27, on the first generated sheet: "its fine but don't use the modern road." The bottom row
# came back with asphalt, a lane marking and a concrete slab on it. Those three are DROPPED rather than
# sliced-and-ignored: nothing from Earth appears in the world yet, and leaving dead assets in the repo
# fights the standing cleanup rule. The row's remaining five - red dust, dry red grass, the hard line where
# red dust meets leaf duff, and the gravels - are Azerothian ground and the seam, so they stay.
# ---------------------------------------------------------------------------------------------------------
_set("aspen", 8, 6, "tools/tile_sheets/aspen_tiles.png", "assets/tiles/aspen/materials", """
    asp_duff_gold asp_duff_brown asp_dirt_path asp_grass_duff asp_log_litter asp_mossy_roots asp_fern_floor asp_needle_dark
    asp_needle_mat asp_needle_cones asp_dry_dirt asp_deadfall asp_shade_dirt asp_root_cracked asp_char_ground asp_ash_patch
    asp_grass_summer asp_grass_seed asp_wildflower asp_fireweed asp_turf_grazed asp_grass_matted asp_grass_dry asp_dirt_grazed
    asp_creek_gravel asp_creek_bed asp_pond_shallow asp_pond_deep asp_mud_bank asp_reed_shallows asp_wet_stone asp_pond_ice
    asp_granite asp_granite_lichen asp_scree asp_talus asp_snow_patch asp_snow_packed asp_bedrock asp_stone_frost
    _drop_asphalt _drop_asphalt_line asp_gravel_shoulder _drop_concrete asp_red_dust asp_red_grass asp_seam_line asp_grey_gravel
""", rows_y=[0, 192, 368, 537, 698, 857, 1024],
   drop=("_drop_asphalt", "_drop_asphalt_line", "_drop_concrete"))
#: Measured off the sheet, not divided. Row heights come out 192/176/169/161/159/167 where an even split
#: would be a flat 171 - the first row is 21px taller than the last. Cutting this one evenly lines up at
#: the top and walks progressively further into the wrong row on the way down, which is exactly the drift
#: the module docstring warns about and is invisible until a texture tiles.


def make_seamless(im, blend=BLEND):
    """Cross-fade opposite edges so the texture repeats without a seam.

    Mirrors the strip from the far edge over the near one under a linear ramp. Done on both axes. The
    middle of the tile is untouched, so detail survives; only the outer `blend` pixels are mixed.
    """
    a = np.asarray(im, dtype=np.float32)
    h, w = a.shape[:2]
    b = min(blend, h // 4, w // 4)
    if b < 2:
        return Image.fromarray(a.astype(np.uint8))
    ramp = np.linspace(0.0, 1.0, b, dtype=np.float32)[:, None, None]
    # vertical: blend the top rows with the mirrored bottom rows
    top, bot = a[:b].copy(), a[-b:].copy()
    a[:b] = top * ramp + bot[::-1] * (1 - ramp)
    ramp_h = ramp.transpose(1, 0, 2)
    left, right = a[:, :b].copy(), a[:, -b:].copy()
    a[:, :b] = left * ramp_h + right[:, ::-1] * (1 - ramp_h)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def slice_set(key, preview=None):
    s = SETS[key]
    sheet = Image.open(ROOT / s["sheet"]).convert("RGB")   # RGB, never RGBA: tiles are opaque ground
    W, H = sheet.size
    cols, rows = s["cols"], s["rows"]
    ys = s["rows_y"] or [round(i * H / rows) for i in range(rows + 1)]
    assert len(ys) == rows + 1, (key, len(ys))
    out_dir = ROOT / s["out"]
    out_dir.mkdir(parents=True, exist_ok=True)

    written, dropped = [], []
    for r in range(rows):
        for c in range(cols):
            name = s["names"][r * cols + c]
            x0, x1 = round(c * W / cols), round((c + 1) * W / cols)
            y0, y1 = ys[r], ys[r + 1]
            if name in s["drop"]:
                dropped.append(name)
                continue
            # Inset before resizing - see the module docstring on why the arithmetic bounds are not safe.
            cell = sheet.crop((x0 + INSET, y0 + INSET, x1 - INSET, y1 - INSET))
            cell = cell.resize((OUT_PX, OUT_PX), Image.LANCZOS)
            make_seamless(cell).save(out_dir / f"{name}.png")
            written.append(name)

    print(f"{key}: {len(written)} tiles -> {s['out']}")
    if dropped:
        print(f"  dropped on purpose: {', '.join(dropped)}")
    if preview:
        pv = Image.new("RGB", (cols * 128, rows * 128), (20, 20, 24))
        for i, name in enumerate(s["names"]):
            if name in s["drop"]:
                continue
            t = Image.open(out_dir / f"{name}.png").resize((128, 128), Image.LANCZOS)
            pv.paste(t, ((i % cols) * 128, (i // cols) * 128))
        pv.save(preview)
        print("  preview", preview)
    return written


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    keys = [a for a in sys.argv[1:] if a in SETS] or list(SETS)
    for k in keys:
        slice_set(k, pv)
