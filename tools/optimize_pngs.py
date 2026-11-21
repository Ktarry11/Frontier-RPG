#!/usr/bin/env python3
"""Losslessly repack every PNG the game ships. Idempotent.

    python3 tools/optimize_pngs.py            # every tracked PNG under assets/
    python3 tools/optimize_pngs.py DIR [...]  # just these folders
    python3 tools/optimize_pngs.py --dry      # every 40th file, sizes only, nothing written

Kyle, 20 Nov 2026, on the download's size: "the optimization is good too for pngs". oxipng (pyoxipng) recompresses
each file and drops chunks nothing reads, and every result is decoded and compared pixel by pixel (RGBA) with the
original before it's kept: a file is only replaced if it's smaller and every pixel is the same. No image changes how it
looks, only how tightly it's packed.
"""
import io
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import oxipng
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def _pixels(data):
    with Image.open(io.BytesIO(data)) as im:
        im.load()
        return im.size, im.convert("RGBA").tobytes()


def shrink(path, write=True):
    path = Path(path)
    raw = path.read_bytes()
    try:
        out = oxipng.optimize_from_memory(raw, level=2, strip=oxipng.StripChunks.safe())
    except Exception:            # noqa: BLE001 - a file oxipng can't read is left as it is
        return len(raw), len(raw), "skipped"
    if len(out) >= len(raw):
        return len(raw), len(raw), "kept"
    if _pixels(raw) != _pixels(out):
        return len(raw), len(raw), "differs"
    if write:
        path.write_bytes(out)
    return len(raw), len(out), "smaller"


def tracked_pngs(roots):
    files = subprocess.run(["git", "ls-files", "-z", "--", *[str(r) for r in roots]], cwd=ROOT,
                           capture_output=True, check=True).stdout.decode("utf-8").split("\0")
    return [ROOT / f for f in files if f.lower().endswith(".png")]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    files = tracked_pngs(args or ["assets"])
    if "--dry" in sys.argv:
        files = files[::40]
    print(f"{len(files)} PNGs")
    before = after = 0
    counts = {}
    with ProcessPoolExecutor() as ex:
        dry = "--dry" in sys.argv
        for i, (b, a, what) in enumerate(ex.map(shrink, files, [not dry] * len(files), chunksize=8), 1):
            before += b
            after += a
            counts[what] = counts.get(what, 0) + 1
            if i % 2000 == 0:
                print(f"  {i}/{len(files)}")
    if "--dry" in sys.argv:
        print("(dry run on every 40th file: nothing written)")
    print(f"{before / 1e6:.0f} MB -> {after / 1e6:.0f} MB ({after / max(before, 1):.0%}); {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
