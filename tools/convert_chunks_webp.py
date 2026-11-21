#!/usr/bin/env python3
"""Convert every baked JPEG map chunk to WebP. Idempotent.

    python3 tools/convert_chunks_webp.py              # convert all of assets/tiles
    python3 tools/convert_chunks_webp.py DIR [DIR...] # just these folders
    python3 tools/convert_chunks_webp.py --dry        # sizes only, nothing written

Kyle, 20 Nov 2026: "how is this 2.4gb....can we clean up some old useless bloat", then "Let's work on webP
conversion?". The sky maps already bake WebP (with alpha); this does the same for every opaque chunk, at the same
quality the bakers now write (tools/terrain_painter.py, quality 88). Each ground_<cx>_<cy>.jpg becomes
ground_<cx>_<cy>.webp and the JPEG is deleted. Nothing needs to know: every zone module registers and checks its
chunks through world/chunk_paths.py, which finds whichever extension is on disk.
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
QUALITY = 88


def convert(path):
    path = Path(path)
    out = path.with_suffix(".webp")
    before = path.stat().st_size
    with Image.open(path) as im:
        im.convert("RGB").save(out, "WEBP", quality=QUALITY, method=6)
    after = out.stat().st_size
    path.unlink()
    return before, after


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry" in sys.argv
    roots = [Path(a) for a in args] or [ROOT / "assets/tiles"]
    files = sorted(p for r in roots for p in r.rglob("ground_*.jpg"))
    total = sum(p.stat().st_size for p in files)
    print(f"{len(files)} JPEG chunks, {total / 1e6:.0f} MB")
    if dry or not files:
        return 0
    before = after = 0
    with ProcessPoolExecutor(max_workers=max(1, (os.cpu_count() or 2) - 1)) as ex:
        for i, (b, a) in enumerate(ex.map(convert, files, chunksize=16), 1):
            before += b
            after += a
            if i % 1000 == 0:
                print(f"  {i}/{len(files)}")
    print(f"converted {len(files)}: {before / 1e6:.0f} MB -> {after / 1e6:.0f} MB ({after / before:.0%})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
