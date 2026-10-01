"""
Scan a sheet for the most tileable (locally-repetitive, non-transparent)
32x32 blocks, without needing to know a target color in advance.
Uses local variance as the flatness score - low internal variance but
still textured (not pure solid) reads as good tileable ground.
"""
from PIL import Image
import numpy as np
import sys

def find_candidates(path, block=32, top_n=8, stride=8):
    im = Image.open(path).convert('RGBA')
    arr = np.array(im)
    h, w = arr.shape[:2]
    alpha = arr[:,:,3]
    rgb = arr[:,:,:3].astype(np.float32)

    results = []
    for y in range(0, h - block, stride):
        for x in range(0, w - block, stride):
            a = alpha[y:y+block, x:x+block]
            if a.min() < 250:
                continue
            patch = rgb[y:y+block, x:x+block].reshape(-1, 3)
            std = patch.std(axis=0).mean()
            mean_brightness = patch.mean()
            # skip near-pure-white or near-pure-black (likely bg/outline junk)
            if mean_brightness > 250 or mean_brightness < 5:
                continue
            results.append((std, x, y))

    # We want texture (std > small threshold, not flat plastic) but not chaotic
    # edges (std too high = mixed materials). Sort and take a mid-low band.
    results.sort()
    # filter out near-zero std (flat/empty) then take the lowest-std remainder
    results = [r for r in results if r[0] > 3]
    return results[:top_n]

def build_contact_sheet(path, coords, block, out_path, cols=6):
    """Save a labeled grid image of candidate crops for fast visual review."""
    im = Image.open(path).convert('RGBA')
    cell = 128
    rows = (len(coords) + cols - 1) // cols
    combo = Image.new('RGB', (cell * cols, cell * rows), (30, 30, 30))
    from PIL import ImageDraw
    draw = ImageDraw.Draw(combo)
    for i, (x, y) in enumerate(coords):
        crop = im.crop((x, y, x + block, y + block)).resize((cell, cell), Image.NEAREST)
        px = (i % cols) * cell
        py = (i // cols) * cell
        combo.paste(crop, (px, py))
        draw.text((px + 2, py + 2), f"{i}:{x},{y}", fill=(255, 0, 0))
    combo.save(out_path)
    print(f"saved {out_path} ({len(coords)} candidates)")


if __name__ == "__main__":
    path = sys.argv[1]
    block = int(sys.argv[2]) if len(sys.argv) > 2 else 32
    out = sys.argv[3] if len(sys.argv) > 3 else None
    cands = find_candidates(path, block=block, top_n=24, stride=max(4, block // 4))
    coords = [(x, y) for std, x, y in cands]
    for i, (std, x, y) in enumerate(cands):
        print(f"{i}: {x},{y} std={std:.1f}")
    if out:
        build_contact_sheet(path, coords, block, out)
