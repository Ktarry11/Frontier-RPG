#!/usr/bin/env python3
"""Slice a race's walk sheet (docs/player_sprite_prompts.md, "Walk cycles") into the player look folders.

    PYTHONPATH=. python3 tools/asset_pipeline/slice_walk_rows.py SHEET.png orc/orc_p1 orc/orc_p2 ... [--dry-run]

Kyle, 20 Nov 2026: the chat takes three pictures at most, so a race's whole turnaround sheet (five men, four facings)
goes up as ONE reference, and the sheet that comes back is five columns (the men) by six rows:

    row 1  walking down, left foot forward        row 4  walking up, right foot forward
    row 2  walking down, right foot forward       row 5  walking right, left foot forward
    row 3  walking up, left foot forward          row 6  walking right, right foot forward

The standing frame between the steps is the look's own down/up/right.png (the turnaround), so the renderer's 1-2-3-2
(ui/tilemap_renderer._walk_frame) plays left foot, stand, right foot, stand. Walking left is walking right mirrored,
the way the standing left is on most of these looks. Cut by tools/asset_pipeline/slice_mount_sheet.py's figure finder.
"""
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent.parent
ROWS = ["down_1", "down_3", "up_1", "up_3", "right_1", "right_3"]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        raise SystemExit(__doc__)
    sheet, folders = args[0], args[1:]
    dry = "--dry-run" in sys.argv
    sys.path.insert(0, str(ROOT / "tools/asset_pipeline"))
    import slice_mount_sheet as SM
    tmp = ROOT / "data/_walk_slice_tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    ids = [f"w{i}" for i in range(len(folders))]
    SM.FACINGS, SM.ROWS, SM.OUT = ROWS, len(ROWS), tmp
    argv = sys.argv
    sys.argv = [argv[0], sheet, *ids] + [a for a in argv[1:] if a == "--grid"]
    try:
        SM.main()
        for wid, folder in zip(ids, folders):
            dst = ROOT / "assets/npcs" / folder
            if not (dst / "down.png").exists():
                raise SystemExit(f"{folder} has no standing look to walk from")
            frames = {r: tmp / f"{wid}_{r}.png" for r in ROWS}
            missing = [r for r, p in frames.items() if not p.exists()]
            if missing:
                raise SystemExit(f"the slicer made no {missing} for {folder}")
            if dry:
                print(f"  {folder}: walk_down/up/right/left 1-3")
                continue
            for r, p in frames.items():
                shutil.copy(p, dst / f"walk_{r}.png")
            for d in ("down", "up", "right"):          # the stand between the steps is the turnaround's own frame
                shutil.copy(dst / f"{d}.png", dst / f"walk_{d}_2.png")
            for n in (1, 2, 3):                         # left is right mirrored
                ImageOps.mirror(Image.open(dst / f"walk_right_{n}.png")).save(dst / f"walk_left_{n}.png")
            print(f"  {folder}: 12 walk frames")
    finally:
        sys.argv = argv
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
