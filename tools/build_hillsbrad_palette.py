#!/usr/bin/env python3
"""Assemble assets/tiles/hillsbrad/materials from existing seamless materials.

Kyle: "Don't forget, hillsbrand is still kind of green. This is classic wow."

That is the whole reason this zone does not simply reuse the Silverpine
material set like the rest of the Lordaeron cluster. Measured mean colours:

    sp_cold_grass       (70, 80, 46)   olive, desaturated - the BLIGHT look
    sp_highland_meadow  (112, 117, 68) dry yellow khaki
    av_forest_grass     (73, 96, 25)   actually green, sunlit
    av_bluebell         (47, 74, 48)   green with flowers

Hillsbrad in Classic is the first healthy country south of the plague - the
contrast with Silverpine is the point, so the greens come from the Ashenvale
set and only the genuinely-neutral pieces (tilled farmland, roads, gravel,
flat water) come from Silverpine. The dry Silverpine meadow is kept as
`hb_dry`, used sparingly on the high foothills so the hills read as hills
without reading as blight.

Materials are COPIED, not symlinked: Kyle plays on Windows (the traceback in
his crash report is a C:\\Users path), where a repo full of symlinks is a
problem waiting to happen. ~25 small PNGs.

Idempotent - safe to re-run; only copies what changed.
"""
import hashlib
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "assets/tiles/hillsbrad/materials"

AV = "assets/tiles/ashenvale/materials"
SP = "assets/tiles/silverpine/materials"

#: hillsbrad name -> source file. The hb_ prefix keeps the zone's palette
#: self-contained and greppable, the same way sp_/av_ do for their zones.
PALETTE = {
    # --- the green ---
    "hb_grass":       f"{AV}/av_forest_grass.png",     # base: sunlit green
    "hb_meadow":      f"{AV}/av_bluebell.png",         # flowered hill meadow
    "hb_forest":      f"{AV}/av_forest_floor.png",     # under the oaks
    "hb_fern":        f"{AV}/av_fern_floor.png",
    "hb_moss_rock":   f"{SP}/sp_moss_rock.png",
    # --- worked land ---
    "hb_field":       f"{SP}/sp_farm_field.png",       # tilled furrows, Hillsbrad Fields
    "hb_dry":         f"{SP}/sp_highland_meadow.png",  # high foothills ONLY
    "hb_earth":       f"{SP}/sp_root_earth.png",
    # --- stone ---
    "hb_rocky":       f"{AV}/av_rocky_ground.png",
    "hb_cobble":      f"{AV}/av_mossy_cobble.png",     # green-mossed town paving
    "hb_flagstone":   f"{SP}/sp_flagstone.png",
    "hb_gravel":      f"{SP}/sp_gravel.png",
    "hb_cliff_a":     f"{AV}/av_cliff_a.png",
    "hb_cliff_b":     f"{AV}/av_cliff_b.png",
    "hb_rock_wall":   f"{AV}/av_rock_wall.png",
    # --- roads and timber ---
    "hb_road":        f"{SP}/sp_road_centre.png",
    "hb_verge":       f"{SP}/sp_road_edge.png",
    "hb_planks":      f"{SP}/sp_wood_planks.png",
    "hb_pier":        f"{SP}/sp_pier_planks.png",
    # --- coast and water ---
    "hb_shore":       f"{AV}/av_beach.png",            # warm sand, the Southshore strand
    "hb_wet_sand":    f"{AV}/av_wet_sand.png",
    "hb_marsh":       f"{SP}/sp_marsh_water.png",
    # Flat water: Ashenvale has no *_flat variants and the painter needs them
    # (the renderer draws its own shimmer over flat colour; a textured tile
    # under that reads as two competing water surfaces).
    "hb_sea_shallow": f"{SP}/sp_sea_shallow_flat.png",
    "hb_sea_deep":    f"{SP}/sp_sea_deep_flat.png",
    "hb_pool_shallow": f"{SP}/sp_pool_shallow_flat.png",
    "hb_pool_deep":   f"{SP}/sp_pool_deep_flat.png",
    "hb_river_shallow": f"{SP}/sp_river_shallow_flat.png",
}


#: Rotated copies, generated rather than copied. The base grass tile has a
#: strong diagonal weave; tiled across 160x160 it reads as corduroy ridges
#: over the whole zone (visible immediately in the first bake preview). The
#: painter blends a material's second texture in with ~9-tile noise, so
#: handing it the SAME grass rotated 90 degrees breaks the repeat without
#: introducing a different-looking ground cover. Rotating a seamless tile by
#: a multiple of 90 keeps it seamless, so this is free.
ROTATED = {
    "hb_grass2":  ("hb_grass", 90),
    "hb_grass3":  ("hb_grass", 180),
    "hb_meadow2": ("hb_meadow", 90),
    "hb_forest2": ("hb_forest", 90),
}


def digest(path):
    return hashlib.md5(Path(path).read_bytes()).hexdigest()


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    missing, copied, same = [], 0, 0
    for name, rel in PALETTE.items():
        src = ROOT / rel
        if not src.is_file():
            missing.append(rel)
            continue
        dst = DEST / f"{name}.png"
        if dst.is_file() and digest(dst) == digest(src):
            same += 1
            continue
        shutil.copyfile(src, dst)
        copied += 1
    if missing:
        print("MISSING SOURCES:", *missing, sep="\n  ")
        return 1

    from PIL import Image
    for name, (src_name, deg) in ROTATED.items():
        src = DEST / f"{src_name}.png"
        dst = DEST / f"{name}.png"
        want = Image.open(src).rotate(deg, expand=False)
        if dst.is_file():
            import io
            buf = io.BytesIO()
            want.save(buf, "PNG")
            if digest(dst) == hashlib.md5(buf.getvalue()).hexdigest():
                same += 1
                continue
        want.save(dst)
        copied += 1
    print(f"hillsbrad palette: {copied} copied, {same} already current "
          f"({len(PALETTE)} materials) -> {DEST.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
