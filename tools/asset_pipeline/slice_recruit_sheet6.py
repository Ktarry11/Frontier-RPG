"""Slice recruit art sheet 6 (16 characters: a 4x4 sprite sheet and a 4x4 portrait sheet), and the Aetherian NPC
sheets AE-M and AE-W (6x4 each).

    python3 tools/asset_pipeline/slice_recruit_sheet6.py sprites <sheet.png>
    python3 tools/asset_pipeline/slice_recruit_sheet6.py portraits <sheet.png>
    python3 tools/asset_pipeline/slice_recruit_sheet6.py aetherians <men.png> <women.png>
    python3 tools/asset_pipeline/slice_recruit_sheet6.py blood_elves <men.png> <women.png>

The blood elf townsfolk (docs/blood_elf_npc_art_prompts.md, BE-M and BE-W, 21 Nov 2026) are the same 6x4 front-only
layout, sliced to assets/npcs/blood_elf/blood_elf_m1..m24 and blood_elf_w1..w24.

docs/recruit_art_prompts_sheet6.md asks for one 4x4 sprite sheet, one 4x4 portrait sheet, and two 6x4 Aetherian sheets
(front only, like the furbolgs), sliced to assets/npcs/aetherian/aetherian_m1..m24 and aetherian_w1..w24. Figure finding is
slice_recruit_sheet2.figures(): label the non-magenta blobs, group into rows, read left to right, so it doesn't care
about the grid. If the portraits come back as two 4x2 images, pass both and they're read in order.

THE PORTRAITS CAME BACK EDGE TO EDGE (18 Nov 2026): the busts in each row touch their neighbours, so blob-finding
merged them (12 found, not 16). grid_figures() cuts the 4x4 along its magenta gutters instead (the columns and rows
with the least art, near each quarter line) and keys each cell on its own, flames and smoke included. It's used for
portraits whenever figures() miscounts.
"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from slice_recruit_sheet2 import figures  # noqa: E402
import numpy as np  # noqa: E402
from scipy import ndimage  # noqa: E402


def grid_figures(sheet, cols=4, rows=4):
    """Each cell of a cols x rows sheet as an RGBA crop, cut along the magenta gutters, in reading order."""
    rgb = np.asarray(Image.open(sheet).convert("RGB")).astype(np.int32)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    solid = (np.minimum(r, b) - g) < 80
    H, W = solid.shape

    def cuts(profile, n, size):
        out = [0]
        for k in range(1, n):
            lo, hi = int(size * k / n - size / 12), int(size * k / n + size / 12)
            out.append(lo + int(np.argmin(profile[lo:hi])))
        return out + [size]
    xs, ys = cuts(solid.sum(axis=0), cols, W), cuts(solid.sum(axis=1), rows, H)
    inner = ndimage.binary_erosion(solid, iterations=1)
    ring = inner & ~ndimage.binary_erosion(inner, iterations=2)
    rgb8 = rgb.astype(np.uint8)
    crops = []
    for j in range(rows):
        for i in range(cols):
            cell = np.zeros_like(inner)
            cell[ys[j]:ys[j + 1], xs[i]:xs[i + 1]] = True
            mask = inner & cell
            yy, xx = np.where(mask)
            by0, by1, bx0, bx1 = yy.min(), yy.max() + 1, xx.min(), xx.max() + 1
            rgba = np.dstack([rgb8, np.where(mask, 255, 0).astype(np.uint8)])[by0:by1, bx0:bx1].copy()
            r_, g_, b_ = (rgba[..., c].astype(int) for c in range(3))
            spill = ring[by0:by1, bx0:bx1] & (np.minimum(r_, b_) > g_ + 25)
            lim = g_ + 25
            rgba[..., 0] = np.where(spill, np.minimum(r_, lim), r_)
            rgba[..., 2] = np.where(spill, np.minimum(b_, lim), b_)
            crops.append(Image.fromarray(rgba, "RGBA"))
    print(f"  {len(crops)} cells cut at x {xs[1:-1]}, y {ys[1:-1]}")
    return crops

IDS = [
    "ines_druid", "lukas_starcaller", "rafael_tinker", "samir_stormbringer",
    "alvaro_venomancer", "clara_primalist", "raul_barbarian", "federico_templar",
    "connor_shaman", "mauricio_reaper", "etienne_mage", "oliver_suncleric",
    "facundo_chronomancer", "renata_rogue", "tariq_bloodmage", "isabela_mage",
]


def aetherians(men, women, folder="aetherian"):
    """The two 6x4 Aetherian sheets, front only: aetherian_m1..m24 and aetherian_w1..w24, each a down.png on a canvas
    sized like the P6 Aetherians'. The blood elf townsfolk use it too, with folder="blood_elf"."""
    for sheet, tag in ((men, "m"), (women, "w")):
        crops = figures(sheet)
        if len(crops) != 24:
            crops = grid_figures(sheet, cols=6, rows=4)
        if len(crops) != 24:
            raise SystemExit(f"{sheet}: found {len(crops)} figures but need 24")
        cwid = max(c.width for c in crops) + 8
        chei = max(c.height for c in crops) + 4
        for k, im in enumerate(crops, 1):
            canvas = Image.new("RGBA", (cwid, chei), (0, 0, 0, 0))
            canvas.paste(im, ((cwid - im.width) // 2, chei - im.height - 2), im)
            d = os.path.join(f"assets/npcs/{folder}", f"{folder}_{tag}{k}")
            os.makedirs(d, exist_ok=True)
            canvas.save(os.path.join(d, "down.png"))
        print(f"  {folder}_{tag}1..{tag}24 {canvas.size}")


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    kind, sheets = sys.argv[1], sys.argv[2:]
    if kind == "aetherians":
        return aetherians(*sheets)
    if kind == "blood_elves":
        return aetherians(*sheets, folder="blood_elf")
    crops = [c for sheet in sheets for c in figures(sheet)]
    if len(crops) != len(IDS) and kind == "portraits" and len(sheets) == 1:
        crops = grid_figures(sheets[0])
    if len(crops) != len(IDS):
        raise SystemExit(f"found {len(crops)} figures but need {len(IDS)} - refusing to write, because a miscount "
                         f"silently gives everyone after it somebody else's face")
    if kind == "sprites":
        cwid = max(c.width for c in crops) + 8
        chei = max(c.height for c in crops) + 4
        for cid, im in zip(IDS, crops):
            canvas = Image.new("RGBA", (cwid, chei), (0, 0, 0, 0))
            canvas.paste(im, ((cwid - im.width) // 2, chei - im.height - 2), im)
            d = os.path.join("assets/npcs/recruits", cid)
            os.makedirs(d, exist_ok=True)
            canvas.save(os.path.join(d, "down.png"))
            print(f"  {cid:24} {canvas.size}")
    elif kind == "portraits":
        cwid = max(c.width for c in crops)
        chei = max(c.height for c in crops)
        os.makedirs("assets/ui/portraits", exist_ok=True)
        for cid, im in zip(IDS, crops):
            canvas = Image.new("RGBA", (cwid, chei), (0, 0, 0, 0))
            canvas.paste(im, ((cwid - im.width) // 2, chei - im.height), im)
            canvas.save(os.path.join("assets/ui/portraits", f"{cid}.png"))
            print(f"  {cid:24} {canvas.size}")
    else:
        raise SystemExit("first argument must be 'sprites' or 'portraits'")


if __name__ == "__main__":
    main()
