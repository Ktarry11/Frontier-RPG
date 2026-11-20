#!/usr/bin/env python3
"""Slice a race's walk sheet (docs/player_sprite_prompts.md, "Walk cycles") into the player look folders.

    PYTHONPATH=. python3 tools/asset_pipeline/slice_walk_rows.py SHEET.png orc/orc_p1 orc/orc_p2 ... [--dry-run]

Kyle, 20 Nov 2026: the chat takes three pictures at most, so a race's whole turnaround sheet (five men, four facings)
goes up as ONE reference, and the sheet that comes back is five columns (the men) by six rows:

    row 1  walking down, left foot forward        row 4  walking up, right foot forward
    row 2  walking down, right foot forward       row 5  walking right, left foot forward
    row 3  walking up, left foot forward          row 6  walking right, right foot forward

The standing frame between the steps is the look's own down/up/right.png (the turnaround), so the renderer's 1-2-3-2
(ui/tilemap_renderer._walk_frame) plays left foot, stand, right foot, stand; write_cycle puts all three on one canvas at
one scale so he doesn't change size mid-stride. Walking left is walking right mirrored. A sheet of three men or two works
the same (one folder per column). Cut by tools/asset_pipeline/slice_mount_sheet.py's figure finder.
"""
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent.parent
ROWS = ["down_1", "down_3", "up_1", "up_3", "right_1", "right_3"]


def write_cycle(dst, walk):
    """Put one man's steps and his standing frame on one canvas per direction.

    The renderer scales every frame to the same height (ui/sprite_loader._npc_frame), so frames cut tight at different
    sizes would make him grow and shrink as he walks: the walk sheet is drawn at another scale from the turnaround,
    and a stride stands a little lower than a stand. So each step is scaled to his standing height in that direction,
    a touch shorter, and each direction's three frames share one canvas, feet on its bottom edge, centred. Walking
    left is walking right mirrored."""
    def bbox(im):
        return im.getbbox() or (0, 0, im.width, im.height)

    def trim(im):
        return im.crop(bbox(im))

    stand = {d: trim(Image.open(dst / f"{d}.png").convert("RGBA")) for d in ("down", "up", "right")}
    dirs = [d for d in ("down", "up", "right") if f"{d}_1" in walk and f"{d}_3" in walk]
    walk = {k: trim(v) for k, v in walk.items()}
    # each step to its own direction's standing height, a touch shorter (a stride drops the head a little): the
    # generator's scale drifts from row to row (it squeezes the side rows), so one factor for the whole man left the
    # squeezed steps small
    STRIDE = 0.97

    def fit(n, im):
        k = stand[n.split("_")[0]].height * STRIDE / im.height
        return im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)

    walk = {n: fit(n, im) for n, im in walk.items()}
    for d in dirs:
        trio = [walk[f"{d}_1"], stand[d], walk[f"{d}_3"]]
        W = max(im.width for im in trio) + 6
        H = max(im.height for im in trio) + 3
        for n, im in zip((1, 2, 3), trio):
            canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            canvas.paste(im, ((W - im.width) // 2, H - im.height), im)
            canvas.save(dst / f"walk_{d}_{n}.png")
            if d == "right":
                ImageOps.mirror(canvas).save(dst / f"walk_left_{n}.png")


def argv_rows():
    return list(sys.argv[1:])


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
    # --rows=down_1,down_3,... for a sheet that came back short (a direction with only one step is left standing)
    rows = next((a.split("=", 1)[1].split(",") for a in argv_rows() if a.startswith("--rows=")), ROWS)
    SM.FACINGS, SM.ROWS, SM.OUT = rows, len(rows), tmp
    argv = sys.argv
    sys.argv = [argv[0], sheet, *ids] + [a for a in argv[1:] if a == "--grid"]
    try:
        SM.main()
        for wid, folder in zip(ids, folders):
            dst = ROOT / "assets/npcs" / folder
            if not (dst / "down.png").exists():
                raise SystemExit(f"{folder} has no standing look to walk from")
            frames = {r: tmp / f"{wid}_{r}.png" for r in rows}
            missing = [r for r, p in frames.items() if not p.exists()]
            if missing:
                raise SystemExit(f"the slicer made no {missing} for {folder}")
            if dry:
                print(f"  {folder}: walk_down/up/right/left 1-3")
                continue
            write_cycle(dst, {r: Image.open(p).convert("RGBA") for r, p in frames.items()})
            done = [d for d in ("down", "up", "right") if f"{d}_1" in rows and f"{d}_3" in rows]
            print(f"  {folder}: walking {', '.join(done)}{' (and left)' if 'right' in done else ''}")
    finally:
        sys.argv = argv
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
