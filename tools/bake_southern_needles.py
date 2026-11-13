"""
Bake Southern Thousand Needles.

    PYTHONPATH=. python3 tools/bake_southern_needles.py [--preview OUT.png]

Paints from the real sliced set (assets/tiles/southern_needles/materials, 47 tiles) rather than the
recoloured Valley-of-Trials stand-ins the other Barrens zones still run on.

PAINTED BY ELEVATION, BECAUSE THE ZONE IS ONLY TWO HEIGHTS.

The Aspen Wilderness needed a whole thaw-and-drainage model to decide its ground. This zone does not,
and pretending otherwise would be dishonest about the landform. Thousand Needles is a floor and a set of
tops with a hard edge between them, so the palette is three bands and a few overlays:

    THE TOPS    wind-scoured hardpan, pale sandstone, orange lichen on bare stone. Dry and thin, because
                nothing holds soil up there.
    THE RIM     layered and iron-banded sandstone, crumbling edges, scree and rubble at the foot. This is
                the only band with any vertical information in it and it does all the work of saying
                "cliff" from directly above.
    THE FLOOR   red sand, cracked mud, dust drift, hoof-churned ground. Wash gravel and salt crust where
                the dry channels run.

Two bands sit across that:
    THE ASPEN TAIL in the north - row 5 of the sheet, which is aspen litter lying ON red soil. It is the
                last of the overlay and it stops at a hard line.
    THE SEAM itself, painted as a one-tile band and not a gradient, same as the Aspen Wilderness's.

sn_undercut is deliberately NOT used as a field material. It is a shadowed overhang and reads as a scene;
at field weights it tiles as a repeating cave mouth. It earns its place only directly under a rim.

LIGHTING. The hillshade reads the gradient of the TILE-grid elevation, precomputed in build_scores and
sampled in post(). Differencing elevation across PIXELS is the bug that quietly halved the brightness of
the entire Aspen Wilderness - at 32 px to a tile the gradient came out near zero and the shade term
pinned flat. A mesa zone would show it even worse, because here the gradient is the whole picture.
"""
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

TEX_DIR = ROOT / "assets/tiles/southern_needles/materials"
ZONES = {"southern_needles": "tools.handbuilt_southern_needles"}

# LESS IS MORE - the same lesson as the Shimmering Flats, the same day. Kyle, 13 Nov: "Its just TOO
# many tiles ... too many blended tiles which looks gross. Sometimes less is more." And of this zone:
# "very boring with little to see".
#
# Both were the same fault. Twenty-seven materials, most a cross-faded pair, spread over the floor and
# the tops alike - so the floor and a mesa top were the SAME red mottle, and the only thing that told
# them apart was a thin ring. From above a mesa read as a crater. Nine things now, one texture each:
#
#     floor     red sand. All of the canyon floor.
#     top       pale capstone. Every mesa top, and nothing else - the colour IS the height.
#     wall      layered stone, the rim
#     wash      the dry channels
#     aspen     the Rockies coming down from the north (see ASPEN BLEEDS below)
#     road, pool_s, pool_d, spring
MATERIALS = {
    "floor":   ("sn_red_sand", None, 2.0),
    "top":     ("sn_sandstone_pale", None, 2.0),
    "wall":    ("sn_layered_stone", None, 1.5),
    "wash":    ("sn_wash_gravel", None, 1.5),
    "aspen":   ("sn_duff_on_red", None, 1.5),
    "road":    ("sn_packed_path", None, 1.0),
    "pool_s":  ("sn_pool_shallow", None, 1.0),
    "pool_d":  ("sn_pool_deep", None, 1.0),
    "spring":  ("sn_spring_grass", None, 1.0),
}
LAND = ("floor", "top", "wash", "aspen", "road", "spring")

#: How far a mesa throws its shadow, in tiles per unit of height. The sun is in the north-west.
SHADOW_RUN = 0.75
SHADOW_MAX = 11


def aspen_edge(M, gx, n_big):
    """The row where the aspen stops, at each column. NOT A LINE.

    ASPEN BLEEDS. This used to be a ruled seam one tile wide at ASPEN_Y - "The Integration did not
    blend" - and from above it was a horizontal line drawn across the map with forest above it and
    desert below. Kyle, 13 Nov: "Aspen is basically the rockies (my home) bleeding into 1000 needles."
    A range does not end at a latitude. It comes down in tongues along the high ground and gives out
    in the low, so the edge wanders by a dozen tiles either way and the last of it is patches.
    """
    return (M.ASPEN_Y + 13.0 * np.sin(gx * 0.045 + 0.7) + 7.0 * np.sin(gx * 0.117 + 2.1)
            + 16.0 * (n_big - 0.5)).astype(np.float32)


def build_scores(P, M):
    S = {}
    gx, gy = P.gx, P.gy
    n_big = P.noise(11.0, "big", octaves=3)
    n_mid = P.noise(4.5, "mid", octaves=3)

    f = M.fields(gx, gy)
    cliff = f["cliff"].astype(np.float32)
    water = f["shallow"].astype(np.float32)
    deep = f["deep"].astype(np.float32)

    elev = M.elevation(gx, gy).astype(np.float32)
    slope = M._slope(gx, gy).astype(np.float32)
    wash = np.clip(M._wash(gx, gy), 0, None).astype(np.float32)

    top = smoothstep(5.0, 9.0, elev)
    rim = smoothstep(0.9, 2.4, slope)
    edge = aspen_edge(M, gx, n_big)
    aspen = smoothstep(edge + 5.0, edge - 5.0, gy)
    # ...and the last of it, a little further south than the edge: patches, not a fade
    aspen = np.maximum(aspen, smoothstep(edge + 22.0, edge + 4.0, gy) * smoothstep(0.66, 0.74, n_mid))

    cliff_f = np.clip(cliff * 0.5, -0.4, 0.6).astype(np.float32)
    dzdx = (M.elevation(gx + 1.0, gy) - M.elevation(gx - 1.0, gy)).astype(np.float32) * 0.5
    dzdy = (M.elevation(gx, gy + 1.0) - M.elevation(gx, gy - 1.0)).astype(np.float32) * 0.5

    # THE SHADOW A MESA THROWS. Walk toward the sun; if the ground there stands higher than the
    # light could clear, this spot is in shade. It is the strongest height cue there is from above,
    # and the zone had none: a 17-high tower and the floor beside it were lit the same.
    shadow = np.zeros_like(elev)
    for k in range(1, SHADOW_MAX + 1):
        ahead = M.elevation(gx - k * 0.75, gy - k * 0.75).astype(np.float32)
        shadow = np.maximum(shadow, smoothstep(0.4, 2.4, ahead - elev - k / SHADOW_RUN * 0.75))

    P.fields = dict(cliff=cliff, cf=cliff_f, water=water, deep=deep, elev=elev, slope=slope,
                    top=top, rim=rim, dzdx=dzdx, dzdy=dzdy, shadow=shadow.astype(np.float32))

    S["floor"] = 0.50 + 0.0 * elev
    S["top"] = -0.5 + 3.0 * top
    S["wash"] = -0.3 + 1.6 * smoothstep(1.30, 2.05, wash) * (1 - top)
    S["aspen"] = -0.5 + 2.6 * aspen * (1 - top)

    core, _verge, _ = P.road_field(list(M.ROADS.values()))
    S["road"] = (0.05 + 1.5 * core).astype(np.float32)

    wetmask = (water > 0.0).astype(np.float32)
    S["pool_s"] = np.clip(1.6 * water, -9.0, 9.0).astype(np.float32)
    S["pool_d"] = np.clip(1.8 * deep, -9.0, 9.0).astype(np.float32) - 0.4
    # the spring margin: the only green on the floor, and it is three tiles wide
    S["spring"] = (1.2 * smoothstep(-2.5, 0.2, water) - 0.45 - 9.0 * wetmask).astype(np.float32)
    for k in LAND:
        S[k] = (S[k] - 12.0 * wetmask).astype(np.float32)

    S["wall"] = (1.6 + 12 * cliff_f).astype(np.float32)
    cl_k = smoothstep(0.0, 0.30, cliff_f)
    for k in list(S):
        if k != "wall":
            S[k] = (S[k] - 14.0 * cl_k).astype(np.float32)
    P.scores = S
    return {k: np.asarray(v, np.float32) for k, v in S.items()}


def post(rgb, X, Y, P):
    """Light the mesas. In a zone that is two flat heights, the light IS the elevation."""
    f = P.fields
    sf = lambda a: P.sample_field(a.astype(np.float32), X, Y)          # noqa: E731
    top = sf(f["top"])
    lum = P.sample_field(P.noise(15.0, "lum", octaves=2), X, Y)

    out = rgb * (0.92 + 0.12 * lum)[..., None]

    # HILLSHADE, sun in the NORTH-WEST - and for the first time actually from there. The term was
    # 1 + k * (-dzdx - dzdy), which lights the slopes that face south-east: every mesa had its bright
    # edge at the bottom right and its dark edge at the top left. The eye assumes light from the top
    # left, so that reads as a hole. It is the whole reason the mesas looked like craters.
    gxs, gys = sf(f["dzdx"]), sf(f["dzdy"])
    shade = np.clip(1.0 + 0.50 * (gxs * 0.70 + gys * 0.70), 0.50, 1.40)
    out = out * shade[..., None]

    # the shadow a mesa throws across the floor (and across a lower mesa)
    sh = sf(f["shadow"])[..., None]
    out = out * (1.0 - 0.42 * sh) * (1.0 - sh + sh * np.array([0.92, 0.95, 1.06], np.float32))

    # The tops catch the sun. Lifting them is what makes the skyline read.
    out = out * (1.0 + 0.14 * top)[..., None]

    # Warm the whole zone - this is red rock country.
    out = out * np.array([1.04, 0.99, 0.94], np.float32)

    wd = sf(f["water"])
    depth = smoothstep(0.4, 4.0, wd)
    out = out * (1 - 0.28 * depth[..., None]) + np.array([40, 92, 96], np.float32) * 0.34 * depth[..., None]
    return np.clip(out, 0, 255)


def bake(key, preview=None, sc=4):
    import importlib
    M = importlib.import_module(ZONES[key])
    P = Painter(M.W, M.H, TEX_DIR, seed=getattr(M, "SEED", 733))
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
