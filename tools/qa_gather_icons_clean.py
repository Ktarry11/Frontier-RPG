#!/usr/bin/env python3
"""No gatherable icon carries a sliver of the icon that sat next to it on its sheet.

    python3 tools/qa_gather_icons_clean.py

Kyle, 13 Nov 2026: "why are we having so many issues cropping gatherables?" - 48 of 518 had one.
See tools/clean_icon_edges.py for why it happens; run it with --apply after slicing any new sheet.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))


def main():
    import clean_icon_edges as C
    bad, n = [], 0
    for path in C.scan(["assets/gathering_nodes"]):
        n += 1
        if C.slivers(np.array(Image.open(path).convert("RGBA"))[..., 3]).any():
            bad.append(str(path.relative_to(ROOT)))
    print(f"{n} gatherable icons")
    if bad:
        print(f"FAIL: {len(bad)} with a neighbour's sliver on the edge - run "
              f"python3 tools/clean_icon_edges.py --apply")
        for b in bad[:20]:
            print("  " + b)
        return 1
    print("OK: none carries a piece of its neighbour")
    return 0


if __name__ == "__main__":
    sys.exit(main())
