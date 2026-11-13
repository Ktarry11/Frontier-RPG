#!/usr/bin/env python3
"""Remove the sliver of a NEIGHBOURING icon left on the edge of a sliced icon.

    python3 tools/clean_icon_edges.py [--apply] [DIR ...]      (default: assets/gathering_nodes)

Kyle, 13 Nov 2026, with a screenshot of an ore node wearing a dark sliver on its left side: "why
are we having so many issues cropping gatherables?"

WHY IT KEEPS HAPPENING. The sheets come back from the image generator with the icons roughly, not
exactly, on the grid - one drifts a few pixels toward its neighbour. The slicer cuts on the exact
grid, so the cell next door keeps the edge of the one that drifted. 41 of the 518 gatherable icons
had one. Cutting on the grid cannot fix that; looking at what was cut can.

THE RULE. In each icon, find the separate pieces of solid pixels. The biggest is the icon. Any
other piece that TOUCHES THE EDGE of the image and is under a quarter of the icon's size is a
neighbour's sliver and is erased. A piece that does not touch the edge is left alone - that is a
spark, a leaf, a loose pebble that belongs to the picture.

It does not, and cannot, repair the other half of the same fault: the icon that drifted has lost
that sliver. Those are listed (--clipped) for re-slicing by hand.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
SOLID = 40          # alpha above this counts as part of a picture
SHARE = 0.25        # a sliver is smaller than this share of the icon


def slivers(alpha):
    """Boolean mask of the pixels that are a neighbour's sliver."""
    solid = alpha > SOLID
    out = np.zeros_like(solid)
    if not solid.any():
        return out
    lab, n = ndimage.label(solid, structure=np.ones((3, 3)))
    if n < 2:
        return out
    sizes = ndimage.sum(solid, lab, range(1, n + 1))
    main = sizes.max()
    h, w = solid.shape
    for i, size in enumerate(sizes, 1):
        if size == main or size >= main * SHARE:
            continue
        ys, xs = np.where(lab == i)
        if xs.min() == 0 or ys.min() == 0 or xs.max() == w - 1 or ys.max() == h - 1:
            out |= lab == i
    return out


def clipped(alpha):
    """How much of the image border the MAIN piece sits on, 0..1 - a high number means the icon
    itself was cut off by the slice."""
    solid = alpha > 160
    if not solid.any():
        return 0.0
    border = np.concatenate([solid[0], solid[-1], solid[:, 0], solid[:, -1]])
    return float(border.mean())


def scan(dirs):
    for d in dirs:
        for path in sorted((ROOT / d).rglob("*.png")):
            yield path


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dirs = args or ["assets/gathering_nodes"]
    apply = "--apply" in sys.argv
    found = 0
    for path in scan(dirs):
        im = Image.open(path).convert("RGBA")
        px = np.array(im)
        mask = slivers(px[..., 3])
        if mask.any():
            found += 1
            print(f"  sliver  {path.relative_to(ROOT)}  ({int(mask.sum())} px)")
            if apply:
                px[mask] = 0
                Image.fromarray(px, "RGBA").save(path)
        elif "--clipped" in sys.argv and clipped(px[..., 3]) > 0.12:
            print(f"  CLIPPED {path.relative_to(ROOT)}  ({clipped(px[..., 3]):.0%} of its border is solid)")
    print(f"{found} icon(s) with a neighbour's sliver" + (" - removed" if apply and found else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
