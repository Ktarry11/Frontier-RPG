"""
Take the edge lines out of the water textures.

Kyle, 12 Nov, looking at The Lashings: "Do notice a lot of the water tiles have that black
line in them. Theyre not cropped properly."

They were not. These tiles were cut out of larger painted sheets, and the cut took a sliver of
whatever sat beside the water - a dock, a bank, a shadow - along one edge. A 256px tile repeats
every 256px, so that sliver becomes a dark line across the sea at a regular interval. 22 of the
game's 56 water textures had one, found by tiling each 2x2 and looking (an automatic band
detector could not tell a cut line from planks or brick, so the list below is by eye).

For each listed texture - and every copy of it under another material directory:
  1. TRIM 20px off all four edges, which is where the sliver is, and scale back to 256
  2. FLATTEN any slow light-to-dark drift across the tile, which would otherwise wrap into
     a soft stripe
  3. BLEND the edges so the tile wraps: the tile is rolled by half, which puts its seam in the
     middle and its unbroken middle at the edge, and the two are cross-faded over the outer
     fifth. The result tiles in both directions.

Run once. A record of what has been processed is kept beside this script so a second run does
not trim the same tile again; delete a name from it to redo that one from its git original.
After running, rebake every zone that uses these (tools/rebake_water_zones.sh).
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
RECORD = Path(__file__).with_suffix(".done.json")
TRIM = 20
BAND = 0.22

#: By eye, from 2x2 tilings of all 56 distinct water textures.
NAMES = [
    "av_fel_pool_bank", "av_lake_deep", "av_lake_mud", "av_lake_shallow", "av_sea_shallow",
    "asp_pond_deep", "gro_tidepool_a", "cen_water_shallow",
    "hb_pool_shallow", "hb_river_shallow",
    "sp_pool_shallow", "sp_river_shallow", "sp_sea_shallow",
    "sn_pool_deep", "sn_pool_shallow",
    "stv_ocean", "tf_sewer_water", "ud_pool_shallow", "den_water_shallow", "den_water_deep",
    # These three had the sliver cut off already and only needed steps 2 and 3 - no trim.
    "tmp_sea_shallow", "tmp_sea_deep", "tmp_pool_shallow",
]
NO_TRIM = {"tmp_sea_shallow", "tmp_sea_deep", "tmp_pool_shallow"}
#: Already done by hand on 12 Nov (same two steps); listed so the QA covers them.
ALREADY = ["stv_sea_s", "stv_sea_d"]


def wrap_axis(a, axis):
    n = a.shape[axis]
    rolled = np.roll(a, n // 2, axis=axis)
    idx = np.arange(n)
    d = np.minimum(idx, n - 1 - idx) / (n / 2.0)
    w = np.clip(d / BAND, 0, 1)
    w = w * w * (3 - 2 * w)
    shape = [1, 1, 1]
    shape[axis] = n
    w = w.reshape(shape)
    return a * w + rolled * (1 - w)


def flatten(a):
    """Even out a tile that is brighter on one side than the other.

    Several of these were painted with light falling across them, so the top of the tile is
    paler than the bottom. Wrapping such a tile does not hide that - it turns it into a soft
    light-and-dark stripe every 256px, which reads as the same fault as the hard line. The
    slow drift in brightness is measured (a very wide blur) and divided out, leaving the
    ripples and the colour alone.
    """
    from scipy import ndimage as ndi
    # Per channel, not on brightness alone: av_sea_shallow drifts in COLOUR (turquoise at the
    # top, deeper blue at the bottom) at nearly constant brightness, and a brightness-only
    # correction left a blue stripe across the Ashenvale coast.
    out = np.empty_like(a)
    for ch in range(3):
        plane = a[..., ch]
        slow = ndi.gaussian_filter(plane, 44, mode="reflect")
        out[..., ch] = plane * np.clip(plane.mean() / (slow + 1e-6), 0.72, 1.4)
    return out


def fix(path, trim):
    im = Image.open(path).convert("RGB")
    if trim:
        w, h = im.size
        im = im.crop((trim, trim, w - trim, h - trim)).resize((w, h), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    a = flatten(a)
    a = wrap_axis(wrap_axis(a, 0), 1)
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(path)


def seam_ratio(path):
    """How badly the tile's opposite edges disagree, against a normal one-pixel step. A tile
    that wraps scores about 1; the cut tiles scored 3 to 6."""
    lum = np.asarray(Image.open(path).convert("RGB")).astype(float).mean(axis=2)
    rows = abs(lum[0] - lum[-1]).mean() / (abs(lum[1:] - lum[:-1]).mean() + 1e-6)
    cols = abs(lum[:, 0] - lum[:, -1]).mean() / (abs(lum[:, 1:] - lum[:, :-1]).mean() + 1e-6)
    return rows, cols


def copies(name):
    # Not "_materials": that is a STAGING directory a bake copies its textures into each
    # run (Glittervein's is copied from shimmering_flats/materials). Fixing the copy as well
    # as its source would be undone by the next bake, and re-running this on the re-staged
    # file would trim it a second time.
    return sorted(p for p in (ROOT / "assets/tiles").rglob(f"{name}.png")
                  if "_previews" not in p.parts and "baked" not in p.parts
                  and "_materials" not in p.parts)


def main():
    done = json.loads(RECORD.read_text()) if RECORD.exists() else {}
    changed = 0
    for name in NAMES:
        files = copies(name)
        if not files:
            print(f"  ?    {name}: no file found")
            continue
        for path in files:
            key = str(path.relative_to(ROOT))
            digest = hashlib.md5(path.read_bytes()).hexdigest()
            if done.get(key) == digest:
                continue
            fix(path, 0 if name in NO_TRIM else TRIM)
            done[key] = hashlib.md5(path.read_bytes()).hexdigest()
            r, c = seam_ratio(path)
            print(f"  ok   {key}  edges now x{r:.1f} / x{c:.1f}")
            changed += 1
    RECORD.write_text(json.dumps(done, indent=1, sort_keys=True) + "\n")
    print(f"{changed} file(s) fixed, {len(done)} on record")
    return 0


if __name__ == "__main__":
    sys.exit(main())
