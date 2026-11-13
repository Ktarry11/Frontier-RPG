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

# LESS IS MORE. Kyle, 13 Nov, looking at the map: "Its just TOO many tiles. thats the problem. There
# are too many blended tiles which looks gross. Sometimes less is more."
#
# This table used to hold twenty-seven materials, most of them a pair of textures cross-faded by
# noise, and a great deal of care had gone into making sure every one of them appeared somewhere
# (see band(), which exists to stop any of them losing). That was the mistake: the measure of
# success was "all the tiles got used", and the result was a pan made of forty-odd textures all
# visible at once. A salt flat is ONE surface. Seven things now, one texture each, no pairs:
#
#     salt      the pan. All of it.
#     sink      the low basin where the crust is thin - one soft grey region, not a mosaic
#     sand      the western shore
#     hive      the dark ground a mound stands on, and the mound
#     rock      the rim mountains and the stacks' sides
#     road      a road, and the Raceway ring
#     alpine    the north-west corner Kyle asked for ("very very small alpine bleeding through")
#
# The other forty textures stay on disk. Unused art is cheaper than a zone that looks like a
# sample book.
MATERIALS = {
    "salt":     ("sf_salt_white", None, 2.0),
    "sink":     ("sf_salt_dark", None, 2.0),
    "sand":     ("tan_sand_gold", None, 2.0),
    "hive":     ("sf_hive_floor", None, 1.5),
    "rock":     ("tan_sandstone_floor", None, 2.5),
    "road":     ("sf_dust_hardpan", None, 1.0),
    "alpine":   ("../../aspen/materials/asp_scree", None, 1.0),
}
LAND = ("salt", "sink", "sand", "road", "alpine")

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
    n_fine = P.noise(1.9, "fine", octaves=2)

    f = M.fields(gx, gy)
    cliff = f["cliff"].astype(np.float32)
    elev = M.elevation(gx, gy).astype(np.float32)

    # Where the desert stops. Wide, and wandering, because a desert does not stop at a line.
    shore = (1.0 - smoothstep(34.0, 78.0, gx + 9.0 * n_big)).astype(np.float32)
    # The basin floor - the Sink - and nowhere else.
    low = smoothstep(-0.55, -1.6, elev + 0.25 * n_big).astype(np.float32)

    # a mound and the apron of dark ground it stands on
    hive_near = np.zeros_like(elev)
    for (_n, cx, cy, r, _h, _t) in M.HIVES:
        d = np.hypot(gx - cx, gy - cy) / (r * 1.3)
        hive_near = np.maximum(hive_near, smoothstep(1.0, 0.55, d + 0.10 * n_big).astype(np.float32))

    # the mountains: everything that stands above the pan near the map edge and is not a stack
    de = np.minimum(np.minimum(gx, M.W - gx), np.minimum(gy, M.H - gy))
    in_stack = np.zeros_like(elev)
    for (_n, cx, cy, rx, ry, _h) in M.STACKS:
        in_stack = np.maximum(in_stack, (M._stack_r(gx, gy, cx, cy, rx, ry) < 1.15).astype(np.float32))
    mount = (smoothstep(1.2, 3.0, elev + 0.6 * n_big) * smoothstep(64.0, 44.0, de)
             * (1.0 - in_stack) * (1.0 - hive_near)).astype(np.float32)
    wall = smoothstep(0.0, 0.6, cliff).astype(np.float32)

    S["salt"] = 1.0 + 0.0 * elev
    S["sand"] = -0.2 + 2.6 * shore
    S["sink"] = -0.2 + 2.4 * low * (1.0 - shore)
    S["hive"] = -1.0 + 5.0 * hive_near
    S["rock"] = -1.0 + 6.0 * np.maximum(mount, wall * (1.0 - hive_near))

    # "very very small" (Kyle), in the north-west corner where the Aspen range comes over
    nw = smoothstep(1.0, 0.10, np.hypot((gx - 46.0) / 54.0, (gy - 46.0) / 48.0)).astype(np.float32)
    S["alpine"] = -1.2 + 2.6 * nw * smoothstep(0.55, 0.80, n_big) - 6.0 * mount

    # a road and the Raceway ring: the same swept ground, with no kerb
    rd = np.maximum(M.road_dist(gx, gy), M.track_dist(gx, gy) - 1.2).astype(np.float32)
    S["road"] = -3.0 + 7.5 * smoothstep(-0.8, 0.4, rd + 0.4 * n_fine) - 8.0 * mount - 8.0 * wall

    for k in LAND:
        S[k] = (S[k] - 6.0 * np.maximum(mount, wall)).astype(np.float32)

    # for post(): the TILE-grid gradient, the same way Southern Needles lights its mesas
    # PER TILE, not per sample: the grid is four samples to a tile, and a gradient taken across
    # samples is a quarter of the slope - which is why the first hillshade here lit nothing.
    per_tile = 1.0 / float(gx[0, 1] - gx[0, 0])
    P.fields = {"dzdx": (np.gradient(elev, axis=1) * per_tile).astype(np.float32),
                "dzdy": (np.gradient(elev, axis=0) * per_tile).astype(np.float32),
                "mount": mount, "elev": elev}
    return {k: np.asarray(v, np.float32) for k, v in S.items()}


def post(rgb, X, Y, P):
    """Lift the pan rather than flattening it. The zone is called shimmering."""
    out = rgb.astype(np.float32)
    f = getattr(P, "fields", None) or {}
    if f:
        sf = lambda a: P.sample_field(a.astype(np.float32), X, Y)          # noqa: E731
        # HILLSHADE, sun from the north-west. There was none, so a mountain range, a hive and a
        # stack were all flat discs of a different colour: the rim read as a frame, the stacks as
        # rings. With it the rim is ground going up and a mound is a cone.
        # one slow drift of light across everything, so a single texture over a hundred tiles
        # does not read as wallpaper
        lum = P.sample_field(P.noise(17.0, "lum", octaves=2), X, Y)
        out = out * (0.94 + 0.10 * lum)[..., None]
        gxs, gys = sf(f["dzdx"]), sf(f["dzdy"])
        # + not -: a slope that FACES the north-west is the lit one (see bake_southern_needles.post)
        shade = np.clip(1.0 + 0.30 * (gxs * 0.70 + gys * 0.70), 0.55, 1.35)
        out = out * shade[..., None]
        # the range sits back: a little darker and cooler than the pan it holds
        m = sf(f["mount"])[..., None]
        out = out * (1.0 - 0.10 * m) * (1.0 - m + m * np.array([0.97, 0.98, 1.03], np.float32))
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
    alp = share["alpine"]
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
