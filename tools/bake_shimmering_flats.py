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
    # THE ALPINE BLEED, north-west only. Kyle: "The north western should have very very small alpine
    # bleeding through." Geographically that is exactly where it belongs - the Aspen Wilderness gate
    # is at (6, 40) and the range comes in over that corner, so this is the tail of the same overlay
    # Southern Needles carries in its top fifth, two zones further along and nearly gone.
    #
    # Borrowed straight from the aspen set by relative path rather than copied: Painter resolves
    # tex_dir / name, so a name can walk out of its own directory. Copying four textures to get four
    # textures would leave two sets to keep in step.
    "alp_duff":  ("../../aspen/materials/asp_duff_gold", "../../aspen/materials/asp_needle_mat", 1.0),
    "alp_scree": ("../../aspen/materials/asp_scree", "../../aspen/materials/asp_granite", 1.0),
    "alp_snow":  ("../../aspen/materials/asp_snow_patch", None, 1.0),
    # rock
    "cliff_a":   ("tan_rubble_sandstone", "tan_sandstone_floor", 1.0),
    "cliff_h":   ("sf_chitin_plate", "sf_resin_poured", 1.0),     # a hive flank is not sandstone
}
LAND = ("salt", "salt_plate", "salt_glaze", "salt_thin", "salt_dark", "mud", "alkali", "dust",
        "gravel", "chitin", "resin", "spoil", "hive", "sand", "sand_rip", "scrub", "hardpan",
        "road", "track", "alp_duff", "alp_scree", "alp_snow")

#: VERY VERY SMALL, and a number rather than an adjective. The share of walkable land the alpine
#: bleed is allowed to take; bake() prints what it actually came out at. The aspen baker does the
#: same with its snow for the same reason - "use it sparingly" is not a thing you can check.
ALPINE_BUDGET = 0.025


def band(n, lo, hi, soft=0.07):
    """1 inside a noise band, 0 outside, with soft shoulders.

    THE FIX FOR NINE DEAD MATERIALS. The first version gated each variant in a family on "noise
    above X" with a different X - mud at 0.28, alkali at 0.44, dust at 0.38 - which reads like it
    spreads them out and does not: whichever variant has the LOWEST threshold wins everywhere its
    family is active, and the rest never fire at all. Measured, nine of the twenty-two materials
    covered 0.0% of the map, which is a third of the tiles Kyle generated sitting unused.

    Bands partition the noise instead of stacking thresholds on it, so each variant owns a slice
    and all of them appear.
    """
    return (smoothstep(lo - soft, lo + soft, n) * smoothstep(hi + soft, hi - soft, n)).astype(np.float32)


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
    shore = (1.0 - smoothstep(20.0, 92.0, gx + 7.0 * n_big)).astype(np.float32)
    # how far below the pan: the Sink, where the crust is thin and dirty
    # TIGHT. At smoothstep(1.2, -1.4) this was about half-on across the ENTIRE pan, because the
    # pan sits at elevation zero - so the Sink's mud spread everywhere and the salt flat stopped
    # being mostly salt. The Sink is the basin floor, not "anywhere low-ish".
    low = smoothstep(-0.15, -1.7, elev).astype(np.float32)
    steep = smoothstep(0.22, 0.55, slope).astype(np.float32)

    # proximity to any hive, which is what brings chitin and spoil to the surface
    hive_near = np.zeros_like(elev)
    for (_n, cx, cy, r, _h, _t) in M.HIVES:
        d = np.hypot(gx - cx, gy - cy) / (r * 2.6)
        hive_near = np.maximum(hive_near, smoothstep(1.0, 0.12, d).astype(np.float32))

    road = (M.road_dist(gx, gy) > 0.0).astype(np.float32)
    track = (M.track_dist(gx, gy) > 0.0).astype(np.float32)

    # ---- the shore: Tanaris arriving early. Banded, so all four appear - see band().
    S["sand"] = -0.15 + 2.0 * shore * band(n_big, -1.0, 0.42)
    S["sand_rip"] = -0.15 + 2.0 * shore * band(n_big, 0.42, 0.66)
    S["hardpan"] = -0.15 + 2.0 * shore * band(n_big, 0.66, 2.0)
    S["scrub"] = -0.15 + 1.9 * shore * band(n_mid + 0.25 * n_fine, 0.58, 2.0)

    # ---- the pan. A MOSAIC, NOT A FIELD.
    #
    # The first bake gave salt a baseline of 0.55 plus 2.4, and nothing else on the pan could ever
    # beat it: the whole middle of the map came out one flat white with the polygon texture visibly
    # repeating across it. A salt flat is not uniform - it is plates, ripples, glaze, stained
    # patches and thin spots, and the variation IS the texture.
    pan = (1.0 - shore)
    dry = (1.0 - low)
    S["salt"] = 0.10 + 1.9 * pan * dry * band(n_mid, -1.0, 0.40)
    S["salt_plate"] = 0.10 + 1.9 * pan * dry * band(n_mid, 0.40, 0.66)
    S["salt_glaze"] = 0.05 + 1.8 * pan * dry * band(n_fine + 0.2 * n_big, 0.62, 2.0)
    S["salt_dark"] = -0.10 + 1.8 * pan * band(n_mid, 0.66, 2.0) * (0.5 + 0.8 * east)

    # ---- the Sink. Thin crust over grey mud, and the yellow alkali staining that says
    # "this is where it evaporated last".
    S["salt_thin"] = -0.10 + 2.3 * low * band(n_big, -1.0, 0.34)
    S["mud"] = -0.10 + 2.4 * low * band(n_big, 0.34, 0.58)
    S["alkali"] = -0.10 + 2.4 * low * band(n_big, 0.58, 2.0)
    S["dust"] = -0.20 + 1.7 * pan * dry * band(n_fine, 0.30, 0.52)
    S["gravel"] = -0.25 + 1.7 * pan * band(n_big + 0.25 * n_fine, 0.70, 2.0)

    # ---- hive country. The only dark ground on the map, which is what makes a mound read.
    S["spoil"] = -0.30 + 3.0 * hive_near * band(n_mid, -1.0, 0.40)
    S["chitin"] = -0.30 + 3.0 * hive_near * band(n_mid, 0.40, 0.62)
    S["resin"] = -0.30 + 3.0 * hive_near * band(n_mid, 0.60, 0.74)
    S["hive"] = -0.30 + 3.0 * hive_near * band(n_mid, 0.74, 2.0)

    # ---- the alpine bleed. AIMED AT WALKABLE GROUND, not at the corner. The first version keyed
    # off low gx AND low gy, which is the map corner - and the map corner is rim, where every land
    # material is suppressed anyway. It measured 0.01%: not "very very small", just absent.
    nw = smoothstep(1.0, 0.10, np.hypot((gx - 46.0) / 54.0, (gy - 46.0) / 48.0)).astype(np.float32)
    S["alp_duff"] = -1.05 + 2.4 * nw * band(n_mid, -1.0, 0.50)
    S["alp_scree"] = -1.05 + 2.4 * nw * band(n_mid, 0.50, 0.72)
    S["alp_snow"] = -1.10 + 2.4 * nw * band(n_mid, 0.72, 2.0)

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
    # WHAT ACTUALLY WON, BEFORE SPENDING THREE MINUTES PAINTING IT.
    #
    # Two things this catches that a preview does not. The alpine bleed has to be "very very small"
    # (Kyle) and the first attempt measured 0.0% - absent rather than small, and no amount of
    # looking at a 200x180 thumbnail would have told me which. And a material that NEVER wins is a
    # tile somebody generated for nothing: nine of twenty-two were dead at one point, a third of
    # the sheet, every one of them invisible in the render by definition.
    keys = list(MATERIALS)
    win = np.stack([scores[k] for k in keys]).argmax(axis=0)
    share = {k: float((win == i).mean()) for i, k in enumerate(keys)}
    alp = sum(share[k] for k in ("alp_duff", "alp_scree", "alp_snow"))
    flag = "  <-- over ALPINE_BUDGET" if alp > ALPINE_BUDGET else ""
    print(f"{key}: alpine bleed {alp:.2%} of the map (budget {ALPINE_BUDGET:.1%}){flag}")
    dead = [k for k in keys if share[k] < 0.0005]
    if dead:
        print(f"{key}: {len(dead)} material(s) never win and will never be seen: "
              f"{', '.join(dead)}")

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
