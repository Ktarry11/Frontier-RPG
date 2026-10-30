#!/usr/bin/env python3
"""Salt-wash a building sprite: what a year on a salt pan does to paint.

    python3 tools/asset_pipeline/salt_wash.py

Kyle, on keeping a goblin town on the Shimmering Flats: "We have goblin structures and what we can do
is color tint them to make them look salt washed."

That is the right call and it is cheaper than it sounds, because salt damage is a very specific and
very legible set of changes rather than a generic tint:

  * COLOUR GOES. Salt spray and sun take the chroma out of paint before they take anything else, so
    saturation drops hard - and it drops MORE on the bright, saturated colours goblins paint things,
    which is why a faded red shack reads as faded rather than as a grey shack.
  * EVERYTHING LIFTS. Pale dust settles on every upward-facing surface and the whole sprite moves
    toward the colour of the ground it is standing on.
  * THE RIME IS AT THE BOTTOM. Salt wicks UP out of the ground into the base of a wall and crystallises
    there, so the bottom of a building is whiter than the top. This gradient is the single most
    legible part of the effect: without it the sprite just looks washed out, and with it the sprite
    looks like it is standing in salt.

A STRAIGHT TINT WOULD HAVE MISSED THE THIRD ONE, which is the one that says where the building is.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent.parent
BUILDINGS = ROOT / "assets/buildings"

#: source -> salt-washed name. The goblin set, which is what the Flats town is built out of.
SOURCES = {
    "bb_harbour_inn": "sw_inn",
    "bb_trade_shop": "sw_trade_shop",
    "bb_warehouse": "sw_warehouse",
    "bb_counting_house": "sw_counting_house",
    "bb_lean_shack": "sw_shack",
    "generic_shack_a": "sw_shack_a",
    "generic_shack_b": "sw_shack_b",
    "scrapyard_workshop": "sw_workshop",
}

#: the colour of the ground everything is drifting toward
SALT = np.array([236.0, 234.0, 228.0], np.float32)


def salt_wash(im, desat=0.55, lift=0.26, rime=0.52):
    """desat: how much chroma to take. lift: pull toward SALT. rime: extra at the base."""
    a = np.asarray(im.convert("RGBA")).astype(np.float32)
    rgb, alpha = a[..., :3], a[..., 3:]
    h = rgb.shape[0]

    lum = rgb.mean(axis=2, keepdims=True)
    chroma = np.abs(rgb - lum).mean(axis=2, keepdims=True) / 128.0
    # saturated paint loses more than bare timber does
    pull = desat * (0.55 + 0.75 * np.clip(chroma, 0, 1))
    out = rgb + (lum - rgb) * np.clip(pull, 0, 1)

    # the rime gradient: nothing at the top, strongest in the bottom fifth
    y = np.linspace(0.0, 1.0, h, dtype=np.float32).reshape(h, 1, 1)
    base = np.clip((y - 0.55) / 0.45, 0.0, 1.0) ** 1.6
    amount = np.clip(lift + rime * base, 0.0, 0.95)
    out = out + (SALT.reshape(1, 1, 3) - out) * amount

    return Image.fromarray(np.concatenate([np.clip(out, 0, 255), alpha], axis=2).astype(np.uint8),
                           "RGBA")


def main():
    made = 0
    for src, dst in SOURCES.items():
        p = BUILDINGS / f"{src}.png"
        if not p.exists():
            print(f"  skip {src}: no such building")
            continue
        salt_wash(Image.open(p)).save(BUILDINGS / f"{dst}.png")
        print(f"  {src:26} -> {dst}")
        made += 1
    print(f"{made} salt-washed buildings -> {BUILDINGS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
