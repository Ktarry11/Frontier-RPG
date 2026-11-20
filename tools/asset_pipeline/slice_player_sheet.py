#!/usr/bin/env python3
"""Slice a player sprite sheet (docs/player_sprite_prompts.md) into the player look folders.

    PYTHONPATH=. python3 tools/asset_pipeline/slice_player_sheet.py SHEET.png orc/orc_p1 orc/orc_p2 ... [--dry-run]

One column per character, four rows of facings (down, left, right, up), the same layout as the mount sheets, so the
cutting is tools/asset_pipeline/slice_mount_sheet.py's (it finds the figures rather than trusting the grid, and keys
the magenta with a halo pass). Each column lands in assets/npcs/<folder>/{down,left,right,up}.png, the four files
race_registry.sprite_base_path reads.

Kyle, 20 Nov 2026: about five looks a race, male first ("none of my friends play female"), four facings each, and
nothing in their hands ("that fucks with movement as we saw"), so walk cycles can be drawn on them later.
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
FACINGS = ["down", "left", "right", "up"]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        raise SystemExit(__doc__)
    sheet, folders = args[0], args[1:]
    dry = "--dry-run" in sys.argv
    tmp_rel = "data/_player_slice_tmp"
    tmp = ROOT / tmp_rel
    shutil.rmtree(tmp, ignore_errors=True)
    ids = [f"p{i}" for i in range(len(folders))]
    cmd = [sys.executable, str(ROOT / "tools/asset_pipeline/slice_mount_sheet.py"), sheet, *ids, f"--out={tmp_rel}"]
    cmd += [a for a in sys.argv[1:] if a == "--grid"]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        shutil.rmtree(tmp, ignore_errors=True)
        raise SystemExit(r.stdout + r.stderr)
    try:
        for pid, folder in zip(ids, folders):
            dst = ROOT / "assets/npcs" / folder
            for f in FACINGS:
                src = tmp / f"{pid}_{f}.png"
                if not src.exists():
                    raise SystemExit(f"the slicer made no {src.name}")
                print(f"  {folder}/{f}.png")
                if not dry:
                    dst.mkdir(parents=True, exist_ok=True)
                    shutil.copy(src, dst / f"{f}.png")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"{len(folders)} looks, {len(folders) * 4} sprites{' (dry run)' if dry else ''}")


if __name__ == "__main__":
    main()
