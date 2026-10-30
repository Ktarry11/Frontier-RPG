"""
Bake The Shimmering Flats.

    PYTHONPATH=. python3 tools/bake_shimmering_flats.py [--preview OUT.png]

Same machinery as tools/bake_aspen_zone.py - a Painter, per-material score fields, a post-process - and
the same principle: the ground cover is READ OFF THE LAYOUT'S OWN TERRAIN FUNCTIONS rather than painted
as hand-placed blobs. A zone whose regions are a design decision wants a PAINT table; a zone whose regions
are a consequence of the landform does not, and a salt pan is the second kind all the way down. Salt
collects where the water stood longest, which is the lowest ground, which the elevation model already
knows.

THE BAKE IS THE LEVEL LADDER, because this zone has no other way to show one. There is no altitude to
climb and no pass to walk away from - just distance out onto the pan - so the palette has to carry it:

    the shore     Tanaris sand and scrub dying into the first salt. Warm.
    the near pan  clean white crust, the brightest ground in the game
    the Sink      the crust gets thin and dirty over grey mud, because this is where the water sat
    hive country  chitin, resin, spoil and the dark packed floor the hives bring up with them

So a player who has walked ten minutes east can tell how far out they are by looking down, which is the
only navigation an open pan can offer besides the mounds themselves.

SALT IS SUPPOSED TO HURT. Row 1 of the tile sheet is the brightest material set in the project and it
should stay that way - the zone is called shimmering. post() lifts the pan slightly rather than
flattening it toward everything else's midtones, and the hive materials are the only dark thing out
there, which is what makes a mound read from a long way off.
"""
import importlib
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools.terrain_painter import Painter, smoothstep, TILE_PX         # noqa: E402

TEX_DIR = ROOT / "assets/tiles/shimmering_flats/materials"
ZONES = {"shimmering_flats": "tools.handbuilt_shimmering_flats"}

MATERIALS = {
    # the pan
    "salt":      ("sf_salt_white", "sf_salt_polygon", 1.0),
    "salt_plate": ("sf_salt_plates", "sf_salt_ripple", 1.0),
    "salt_glaze": ("sf_salt_glazed", "sf_salt_white", 1.0),
    "salt_thin": ("sf_salt_clay", "sf_salt_thin_mud", 1.0),
    "salt_dark": ("sf_salt_dark", "sf_stones_salt", 1.0),
    # the Sink, where the crust gives out
    "mud":       ("sf_mud_curled", "sf_clay_saltrim", 1.0),
    "alkali":    ("sf_alkali_yellow", "sf_hardpan_swept", 1.0),
    "dust":      ("sf_dust_hardpan", "sf_hardpan_swept", 1.0),
    "gravel":    ("sf_salt_gravel", "sf_stones_salt", 1.0),
    # hive country
    "chitin":    ("sf_chitin_plate", "sf_carapace_shards", 1.0),
    "resin":     ("sf_resin_poured", "sf_resin_grit", 1.0),
    "spoil":     ("sf_tunnel_spoil", "sf_crust_shattered", 1.0),
    "hive":      ("sf_hive_floor", "sf_hive_film", 1.0),
    # the shore, which is Tanaris arriving early
    "sand":      ("tan_sand_gold", "tan_dust_drift", 1.0),
    "sand_rip":  ("tan_dune_ripple", "tan_sand_pebble", 1.0),
    "scrub":     ("tan_scrub_sand", "tan_wadi_gravel", 1.0),
    "hardpan":   ("tan_hardpan_orange", "tan_sand_pebble", 1.0),
    # roads and the track
    "road":      ("sf_track_rut", None, 1.0),
    "track":     ("sf_salt_glazed", "sf_salt_plates", 1.0),
    # rock
    "cliff_a":   ("tan_rubble_sandstone", "tan_sandstone_floor", 1.0),
    "cliff_h":   ("sf_chitin_plate", "sf_resin_poured", 1.0),     # a hive flank is not sandstone
}
LAND = ("salt", "salt_plate", "salt_glaze", "salt_thin", "salt_dark", "mud", "alkali", "dust",
        "gravel", "chitin", "resin", "spoil", "hive", "sand", "sand_rip", "scrub", "hardpan",
        "road", "track")


def build_scores(P, M):
    S = {}
    gx, gy = P.gx, P.gy
    n_big = P.noise(9.0, "big", octaves=3)
    n_mid = P.noise(4.0, "mid", octaves=3)
    n_fine = P.noise(1.9, "fine", octaves=2)

    f = M.fields(gx, gy)
    cliff = f["cliff"].astype(np.float32)
    elev = M.elevation(gx, gy).astype(np.float32)
    slope = M._slope(gx, gy).astype(np.float32)

    # THE ONE AXIS THIS ZONE HAS.
    east = smoothstep(56.0, 170.0, gx).astype(np.float32)
    # A WIDE OVERLAP, because a desert does not stop at a line. At 30-98 the sand and the salt
    # crossed over inside about ten tiles and the preview had a hard vertical edge down the map.
    shore = (1.0 - smoothstep(22.0, 124.0, gx + 9.0 * n_big)).astype(np.float32)
    # how far below the pan: the Sink, where the crust is thin and dirty
    low = smoothstep(1.2, -1.4, elev).astype(np.float32)
    steep = smoothstep(0.22, 0.55, slope).astype(np.float32)

    # proximity to any hive, which is what brings chitin and spoil to the surface
    hive_near = np.zeros_like(elev)
    for (_n, cx, cy, r, _h, _t) in M.HIVES:
        d = np.hypot(gx - cx, gy - cy) / (r * 2.6)
        hive_near = np.maximum(hive_near, smoothstep(1.0, 0.12, d).astype(np.float32))

    road = (M.road_dist(gx, gy) > 0.0).astype(np.float32)
    track = (M.track_dist(gx, gy) > 0.0).astype(np.float32)

    # ---- the shore: Tanaris arriving early
    S["sand"] = 0.10 + 1.9 * shore * (0.6 + 0.5 * n_big)
    S["sand_rip"] = -0.4 + 2.0 * shore * smoothstep(0.35, 0.75, n_mid)
    S["scrub"] = -0.8 + 2.2 * shore * smoothstep(0.55, 0.85, n_mid + 0.2 * n_fine)
    S["hardpan"] = -0.35 + 1.7 * shore * smoothstep(0.38, 0.74, n_big)

    # ---- the pan. A MOSAIC, NOT A FIELD.
    #
    # The first bake gave salt a baseline of 0.55 plus 2.4, and nothing else on the pan could ever
    # beat it: the whole middle of the map came out one flat white with the polygon texture visibly
    # repeating across it. A salt flat is not uniform - it is plates, ripples, glaze, stained
    # patches and thin spots, and the variation IS the texture. So the baseline is low and every
    # variant competes on noise at similar strength, which also breaks up the tiling that made the
    # first attempt read as wallpaper.
    pan = (1.0 - shore)
    S["salt"] = 0.10 + 1.5 * pan * (1.0 - 0.6 * low)
    S["salt_plate"] = 0.05 + 1.8 * pan * smoothstep(0.30, 0.62, n_mid)
    S["salt_glaze"] = -0.10 + 1.7 * pan * smoothstep(0.42, 0.70, n_fine + 0.2 * n_big)
    S["salt_dark"] = -0.25 + 1.9 * pan * smoothstep(0.38, 0.68, n_big) * (0.5 + 0.8 * east)

    # ---- the Sink. Thin crust over grey mud, and the yellow alkali staining that says
    # "this is where it evaporated last".
    S["salt_thin"] = -0.20 + 2.4 * low * (0.5 + 0.7 * n_mid)
    S["mud"] = -0.45 + 2.6 * low * smoothstep(0.28, 0.66, n_big)
    S["alkali"] = -0.70 + 2.5 * low * smoothstep(0.44, 0.76, n_mid + 0.3 * n_fine)
    S["dust"] = -0.35 + 1.7 * (1.0 - low) * pan * smoothstep(0.38, 0.70, n_fine)
    S["gravel"] = -0.55 + 1.8 * pan * smoothstep(0.50, 0.80, n_big + 0.25 * n_fine)

    # ---- hive country. The only dark ground on the map, which is what makes a mound read.
    S["spoil"] = -1.2 + 3.2 * hive_near * (0.5 + 0.7 * n_mid)
    S["chitin"] = -1.6 + 3.4 * hive_near * smoothstep(0.30, 0.72, n_big)
    S["resin"] = -1.8 + 3.0 * hive_near * smoothstep(0.52, 0.88, n_fine)
    S["hive"] = -2.0 + 3.6 * hive_near * smoothstep(0.62, 0.95, n_mid) * (0.3 + 0.9 * east)

    # ---- made surfaces
    S["road"] = -3.0 + 7.0 * road
    S["track"] = -3.0 + 6.4 * track

    # ---- rock. Sandstone on the shore stacks, chitin on the hive flanks - a mound's side is not
    # sandstone, and painting it as rock was the first thing that looked wrong in the preview.
    wall = smoothstep(0.0, 0.6, cliff).astype(np.float32)
    S["cliff_a"] = -2.0 + 6.0 * wall * (1.0 - hive_near)
    S["cliff_h"] = -2.0 + 6.4 * wall * hive_near

    for k in LAND:
        S[k] = np.where(wall > 0.5, -3.0, S[k]).astype(np.float32)
    for k in ("salt", "salt_plate", "salt_glaze", "salt_thin", "salt_dark", "mud", "alkali",
              "dust", "gravel", "sand", "sand_rip", "scrub", "hardpan"):
        S[k] = (S[k] - 2.2 * steep).astype(np.float32)
    S["road"] = np.where(road > 0.5, 7.0, S["road"]).astype(np.float32)
    S["track"] = np.where(track > 0.5, 6.4, S["track"]).astype(np.float32)
    return {k: v.astype(np.float32) for k, v in S.items()}


def post(rgb, X, Y, P):
    """Lift the pan rather than flattening it. The zone is called shimmering."""
    out = rgb.astype(np.float32)
    lum = out.mean(axis=2, keepdims=True)
    bright = np.clip((lum - 150.0) / 80.0, 0.0, 1.0)
    out = out + bright * 16.0
    return np.clip(out, 0, 255).astype(np.uint8)


def bake(key, preview=None, sc=4):
    M = importlib.import_module(ZONES[key])
    P = Painter(M.W, M.H, TEX_DIR, seed=getattr(M, "SEED", 3540))
    scores = build_scores(P, M)
    out = ROOT / M.BAKED_DIR
    written = P.bake(MATERIALS, scores, out, chunk_tiles=20, post=post)
    print(f"{key}: baked {len(written)} chunks -> {out}")
    if preview:
        full = Image.new("RGB", (M.W * TILE_PX, M.H * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        full.resize((M.W * sc, M.H * sc), Image.LANCZOS).save(preview)
        print("preview", preview)


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    for k in ([a for a in sys.argv[1:] if a in ZONES] or list(ZONES)):
        bake(k, pv)
