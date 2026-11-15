#!/usr/bin/env python3
"""Friendly Timbermaw furbolgs and treants for the Emerald Reclamation, recoloured from the Felwood sheet.

    PYTHONPATH=. python3 tools/build_reclamation_npc_art.py [--preview OUT.png]

Kyle, 14 Nov 2026: "can we recolour some of the hostile furbolgs and the treants to be actual sprites
(quest givers or vendors) in town for The Emerald Reclamation?"

The Deadwood on Kyle's sheet are the right SHAPES for the Timbermaw - same people, before the fel took
them - and the warpwood treant and the corrupted ancient are the right shapes for the forest's own
guardians. What marks them as fel is colour: green rot on the fur, green glowing eyes and sap, a sick
dark coat. So the recolour does three things:

  1. FEL GREEN -> MOONLIGHT. Every strongly green pixel (the rot, the eyes, the totem glow, the sap)
     turns Elune silver-blue at the same brightness: a glow stays a glow, it just stops being fel.
  2. THE COAT WARMS. The furbolgs' dark, sick brown is lifted and pushed toward the Timbermaw's honey
     brown; the treants' bark gets a little warmer and greener.
  3. Nothing else moves: the shapes, the gear and the outline are Kyle's drawing.

Writes NPC-only appearance folders the race registry reads (world/race_registry.py): assets/npcs/
furbolg/furbolg_<n>/ and assets/npcs/treant/treant_<n>/, each with the one drawn facing as
down/left/right/up (single-facing NPC art, like the older packs).
"""
import colorsys
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/creatures"

FURBOLGS = ["fw_deadwood_warrior", "fw_deadwood_watcher", "fw_deadwood_pathfinder", "fw_deadwood_shaman",
            "fw_deadwood_gardener", "fw_deadwood_alpha"]
TREANTS = ["fw_warpwood_treant", "fw_boss_corrupted_ancient"]
MOON = 0.57          # hue of Elune silver-blue (0..1)


def recolour(path, coat_hue, coat_sat, coat_lift):
    a = np.asarray(Image.open(path).convert("RGBA")).astype(np.float32) / 255.0
    rgb, alpha = a[..., :3], a[..., 3:]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    v = mx
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    # hue in 0..1
    h = np.zeros_like(mx)
    d = np.maximum(mx - mn, 1e-6)
    h = np.where(mx == r, ((g - b) / d) % 6, h)
    h = np.where(mx == g, (b - r) / d + 2, h)
    h = np.where(mx == b, (r - g) / d + 4, h)
    h = (h / 6.0) % 1.0

    fel = (h > 0.17) & (h < 0.45) & (s > 0.35) & (v > 0.25)          # yellow-green through green
    coat = ~fel & (s < 0.75)
    h2, s2, v2 = h.copy(), s.copy(), v.copy()
    # 1. fel green -> moonlight, brightness kept
    h2[fel] = MOON
    s2[fel] = np.clip(s[fel] * 0.55, 0, 1)
    v2[fel] = np.clip(v[fel] * 1.05, 0, 1)
    # 2. the coat warms toward its target hue
    k = 0.65
    dh = ((coat_hue - h[coat] + 0.5) % 1.0) - 0.5
    h2[coat] = (h[coat] + k * dh) % 1.0
    s2[coat] = np.clip(s[coat] * coat_sat, 0, 1)
    v2[coat] = np.clip(v[coat] * coat_lift + 0.02, 0, 1)

    out = np.zeros_like(rgb)
    hh, ss, vv = h2 * 6.0, s2, v2
    i = np.floor(hh).astype(int) % 6
    f = hh - np.floor(hh)
    p, q, t = vv * (1 - ss), vv * (1 - ss * f), vv * (1 - ss * (1 - f))
    for idx, (cr, cg, cb) in enumerate(((vv, t, p), (q, vv, p), (p, vv, t), (p, q, vv), (t, p, vv), (vv, p, q))):
        m = i == idx
        out[..., 0][m], out[..., 1][m], out[..., 2][m] = cr[m], cg[m], cb[m]
    res = np.concatenate([out, alpha], axis=2)
    return Image.fromarray((np.clip(res, 0, 1) * 255).astype(np.uint8), "RGBA")


def write(race, n, im):
    d = ROOT / "assets/npcs" / race / f"{race}_{n}"
    d.mkdir(parents=True, exist_ok=True)
    for facing in ("down", "left", "right", "up"):
        im.save(d / f"{facing}.png")
    return d


def main():
    made = []
    for n, stem in enumerate(FURBOLGS, 1):
        made.append(write("furbolg", n, recolour(SRC / f"{stem}.png", coat_hue=0.085, coat_sat=1.15, coat_lift=1.22)))
    for n, stem in enumerate(TREANTS, 1):
        made.append(write("treant", n, recolour(SRC / f"{stem}.png", coat_hue=0.10, coat_sat=1.05, coat_lift=1.12)))
    print(f"{len(made)} appearance folders written")
    if "--preview" in sys.argv:
        out = sys.argv[sys.argv.index("--preview") + 1]
        pairs = [(SRC / f"{s}.png", ROOT / "assets/npcs/furbolg" / f"furbolg_{i}" / "down.png")
                 for i, s in enumerate(FURBOLGS, 1)]
        pairs += [(SRC / f"{s}.png", ROOT / "assets/npcs/treant" / f"treant_{i}" / "down.png")
                  for i, s in enumerate(TREANTS, 1)]
        W = 220
        sheet = Image.new("RGBA", (W * len(pairs), W * 2), (70, 70, 70, 255))
        for c, (a, b) in enumerate(pairs):
            for r, pth in enumerate((a, b)):
                im = Image.open(pth).convert("RGBA")
                im.thumbnail((W - 10, W - 10))
                sheet.alpha_composite(im, (c * W + (W - im.width) // 2, r * W + (W - im.height) // 2))
        sheet.save(out)
        print("preview", out)


if __name__ == "__main__":
    main()
