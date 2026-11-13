#!/usr/bin/env python3
"""
Bake Northern Tanaris - gold desert between a dead city and a live port.

    PYTHONPATH=. python3 tools/bake_northern_tanaris.py [--preview OUT.png]

THE PALETTE RULE HERE IS THE EXACT OPPOSITE OF SALTWHEEL'S, AND THAT IS THE POINT.

tools/bake_saltwheel.py enforces MAX_SAT: every tile in that town has to be near-neutral, because a
salt pan is, and three bakes were thrown away discovering that the loud tan_* tiles turned it into
orange camouflage. Those same loud tiles are exactly what this zone wants. tan_sand_gold at saturation
172 was a disaster on a salt flat and is simply what sand looks like in Tanaris.

So this baker checks a FLOOR instead of a ceiling, on the sand family only: MIN_SAT below. A desert
painted out of the desaturated half of that sheet would come out grey and look like the Flats with
the contrast turned down - which is the same mistake in the other direction and just as invisible in
a thumbnail. The two checks disagree on purpose and each one is right about its own zone.

THE VALUE PLAN, darkest to lightest:

    63-102   THE RANGES AND THE PORT. Basalt in the mountains, tar and harbour dirt at the quay. The
             two dark things in the zone are its two edges, which frames the desert between them.
    124-140  THE ROAD AND THE WORN GROUND either side of it. Wadi gravel and hardpan: this is where
             people and carts have been, and it is a shade darker than the open sand because that is
             what traffic does to a desert.
    147-156  THE OPEN SAND. Most of the map. Gold, loud, and deliberately the brightest large area -
             the player should feel exposed crossing it, and value does that better than any prop.
    181      THE RUINS. Exposed sandstone is the lightest thing here, which makes Zul'Farrak and
             Gadgetzan's walls read as pale shapes against the sand rather than as more sand.
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
from tools.bake_shimmering_flats import band                           # noqa: E402

#: The Tanaris tiles were sliced into the Flats' materials directory when Kyle generated that sheet -
#: one sheet covered both zones, so the tan_* half has been sitting here waiting for this zone.
TEX_DIR = ROOT / "assets/tiles/shimmering_flats/materials"

# LESS IS MORE (13 Nov 2026). Kyle, of the Shimmering Flats: "Its just TOO many tiles ... too many
# blended tiles which looks gross. Sometimes less is more" - and then asked for the same cut across
# the region. One texture per material, no cross-faded pairs, and materials that were only ever a
# variation on the ground beside them now share its texture. The ranges are one calm rock drawn
# large instead of rubble alternating with scrub, which tiled into a patterned border round the map.
MATERIALS = {
    # --- 63-102: the ranges, and the port
    # THE RANGES ARE SANDSTONE, NOT BASALT. tan_basalt_grit is near-black volcanic grit at
    # luminance 63, and at 45% of the map it did not read as mountains at all - it read as void,
    # with every desert edge becoming a stark silhouette against it. Tanaris is sandstone country.
    # The basalt survives as a thin accent for the shadowed crags, which is the only place that
    # value belongs.
    # PAIRED, because one tile across 44% of a map repeats visibly - the rubble has a strong
    # pattern in it and at 1:1 over that area it read as houndstooth. The second name is the
    # painter's variation layer, not a competing material, which is the distinction that matters:
    # two MATERIALS at similar weights is what made the leopard print, a pair inside one material
    # is what breaks up its repeat.
    # THE VARIATION PARTNER HAS TO BE CLOSE IN VALUE. Paired with tan_sandstone_floor (luminance
    # 181 against the rubble's 127) the variation layer read as pale blotches across the ranges -
    # patchy snow on a desert. tan_scrub_sand is 134 to the rubble's 127 and 111 saturation to its
    # 108, so it breaks the repeat without being visible as a second thing.
    "rock":     ("tan_sandstone_floor", None, 2.5),
    "crag":     ("tan_sandstone_floor", None, 2.5),
    "quay":     ("tan_quay_tarred", None, 1.0),
    "harbour":  ("tan_harbour_dirt", None, 1.0),
    # --- 124-140: the road and the ground people have used
    "road":     ("tan_wadi_gravel", None, 1.0),
    "hardpan":  ("tan_sand_pebble", None, 1.5),
    "drift":    ("tan_sand_gold", None, 1.5),
    # --- 147-156: the open sand, most of the map
    "sand":     ("tan_sand_gold", None, 1.5),
    "pebble":   ("tan_sand_pebble", None, 1.5),
    # --- 181: the ruins
    "stone":    ("tan_paving_carved", None, 1.0),
}

#: THE SAND FAMILY HAS TO BE LOUD. See the note above - this is a floor, not a ceiling, and it is the
#: mirror image of bake_saltwheel's MAX_SAT. Only the families that make up the desert body are held
#: to it; rock, tar and harbour dirt are legitimately drab and are exempt.
MIN_SAT = 60.0
LOUD_FAMILIES = ("sand", "pebble", "hardpan", "drift", "road", "stone", "rock")
DEAD = 0.0005


def check_palette():
    from PIL import Image as _I
    quiet = []
    for fam in LOUD_FAMILIES:
        a, b, _w = MATERIALS[fam]
        for n in (a, b):
            if not n:
                continue
            px = np.asarray(_I.open(TEX_DIR / f"{n}.png").convert("RGB")).astype(float)
            sat = float((px.max(2) - px.min(2)).mean())
            if sat < MIN_SAT:
                quiet.append(f"{fam}/{n} sat={sat:.0f}")
    if quiet:
        raise AssertionError(f"the desert body has drab tiles in it (min {MIN_SAT:.0f}): "
                             f"{', '.join(quiet)}")


def build_scores(P, M):
    S = {}
    gx, gy = P.gx, P.gy
    n_big = P.noise(9.0, "big", octaves=3)
    n_mid = P.noise(3.6, "mid", octaves=3)
    n_fine = P.noise(1.6, "fine", octaves=2)

    cliff = M.cliff_field(gx, gy).astype(np.float32)
    water = M.water_field(gx, gy).astype(np.float32)
    rd = M.road_dist(gx, gy).astype(np.float32)
    rock = smoothstep(-0.5, 0.5, cliff)
    sea = smoothstep(-0.5, 2.0, water)
    road = smoothstep(-0.5, 1.2, rd)

    # THE TWO RUINS, AS FIELDS - AND WOBBLED, BECAUSE A PAINT FIELD PAINTS ITS OWN SHAPE.
    #
    # The first bake used the bare primitives: a rectangle for Gadgetzan and an ellipse for
    # Zul'Farrak. They came out as a literal beige rectangle and a literal circle sitting on the
    # sand, with edges a ruler could have drawn. The TERRAIN is allowed to be geometric - Gadgetzan's
    # wall is a rectangle on purpose, because somebody built it - but the GROUND around a ruin is
    # not, and painting it with the same primitive turns the whole quarter into a shape.
    from tools.tirisfal_kit import wob
    G = M.GAD
    jitter = 3.2 * wob(gx * 0.11, gy * 0.10) + 1.4 * wob(gx * 0.31, gy * 0.27)
    gad = smoothstep(5.0, -3.0, np.maximum(
        np.maximum(G["x0"] - gx, gx - G["x1"]), np.maximum(G["y0"] - gy, gy - G["y1"])) + jitter)
    _n, zx, zy, zrx, zry, _h = M.RUINS[0]
    zf = smoothstep(1.45, 0.80, np.hypot((gx - zx) / zrx, (gy - zy) / zry)
                    + 0.09 * wob(gx * 0.13, gy * 0.12))
    ruin = np.maximum(gad, zf)

    # how close to the coast, for the harbour band
    coast = smoothstep(-16.0, -1.0, water)

    P.fields = dict(cliff=cliff, water=water, rock=rock, sea=sea, road=road, ruin=ruin)
    # RELIEF FOR THE LIGHT. There is no elevation model here - a range is a mask - so the mask is
    # the height: softened, and its slope taken PER TILE (the grid is four samples to a tile).
    from scipy.ndimage import gaussian_filter
    _h = gaussian_filter((8.0 * rock).astype(np.float32), 5.0)
    _pt = 1.0 / float(gx[0, 1] - gx[0, 0])
    P.fields["dzdx"] = (np.gradient(_h, axis=1) * _pt).astype(np.float32)
    P.fields["dzdy"] = (np.gradient(_h, axis=0) * _pt).astype(np.float32)

    # ---- the ranges. ONE MATERIAL, NOT TWO ALTERNATING: the pair's second tile is the lighter
    # rubble, and letting the painter swap between them freely turned 46% of the map into a leopard
    # print - the same failure the Saltwheel rim had. Rubble gets a thin slice of the noise and the
    # basalt holds the rest, so the ranges read as one mass with weathering in it.
    S["rock"] = -0.3 + 3.40 * rock * band(n_big, 0.00, 0.82)
    S["crag"] = -0.3 + 3.40 * rock * band(n_big, 0.82, 1.01)

    # ---- the port end
    S["quay"] = -0.5 + 3.00 * coast * (1 - rock) * band(n_mid, 0.00, 0.55)
    S["harbour"] = -0.5 + 3.00 * coast * (1 - rock) * band(n_mid, 0.55, 1.01)

    # ---- the road, and the worn ground that spreads off it
    S["road"] = -0.4 + 3.30 * road * (1 - rock)
    worn = smoothstep(-9.0, 0.0, rd) * (1 - road)
    S["hardpan"] = 0.15 + 2.20 * (1 - rock) * np.maximum(worn, 0.45 * ruin) * band(n_mid, 0.00, 0.62)
    S["drift"] = 0.15 + 2.20 * (1 - rock) * worn * band(n_mid, 0.62, 1.01)

    # ---- the ruins: exposed stone, the lightest thing in the zone
    # BROKEN PAVING SHOWING THROUGH SAND, not a slab. Scored as a solid fill the ruin field painted
    # its own outline - a beige rectangle at Gadgetzan and a beige circle at Zul'Farrak, both with
    # edges a ruler could have drawn. Gating it on noise means the stone appears in PATCHES inside
    # the ruin and the sand comes through between them, so the quarter has a texture instead of a
    # border.
    S["stone"] = -0.3 + 3.10 * ruin * (1 - rock) * band(n_mid, 0.00, 0.58)

    # ---- the open sand: most of the map, and the brightest large area on it
    open_ = (1 - rock) * (1 - coast) * (1 - 0.7 * ruin)
    # THREE WAYS, NOT TWO. The first bake gave the gold tile two thirds of the open desert and the
    # result was a flat saturated slab - 32% of the map in one tone, which reads as a colour field
    # rather than as ground. Dust drift is pulled out of the worn-ground family and given a share of
    # the open sand as well, so the dunes have something to break against.
    S["sand"] = 0.70 + 1.40 * open_ * band(n_big, 0.00, 0.44)
    S["pebble"] = 0.70 + 1.40 * open_ * band(n_big, 0.44, 0.76)
    S["drift"] = np.maximum(S["drift"], 0.70 + 1.40 * open_ * band(n_big, 0.76, 1.01))

    # water wins outright where there is water
    for k in MATERIALS:
        S[k] = S[k] - 12.0 * sea
    P.scores = S
    return S


def post(rgb, X, Y, P):
    f = P.fields
    sf = lambda a: P.sample_field(a.astype(np.float32), X, Y)          # noqa: E731
    rock, sea, road, ruin = sf(f["rock"]), sf(f["sea"]), sf(f["road"]), sf(f["ruin"])
    out = rgb.copy().astype(np.float32)
    # HILLSHADE, sun in the north-west: a slope FACING it rises toward the south-east. These zones
    # had none, so a mountain range was a flat band of a different colour round the map.
    shade = np.clip(1.0 + 0.55 * (sf(f["dzdx"]) * 0.70 + sf(f["dzdy"]) * 0.70), 0.55, 1.40)
    out = out * shade[..., None]

    # SUN. A desert at noon is bleached in the open and holds its colour in shade, so the open sand
    # is lifted and desaturated slightly while the rock keeps its chroma. Without this the sand and
    # the ruins sit at the same apparent brightness and the landmarks stop being landmarks.
    openness = np.clip(1.0 - rock - 0.5 * ruin, 0.0, 1.0)
    glare = 0.12 * openness
    out = out + (np.float32(246.0) - out) * glare[..., None]

    # the road is darker and greyer than the sand either side - traffic, and whatever they laid
    out = out * (1 - 0.14 * road[..., None])
    grey = out.mean(axis=-1, keepdims=True)
    out = out * (1 - 0.20 * road[..., None]) + grey * (0.20 * road[..., None])

    # the ranges sit in their own shadow and go slightly cool, which pushes them back
    cool = rock[..., None] * np.array([0.93, 0.96, 1.06], np.float32)
    out = out * (1 - rock[..., None]) + out * cool

    # THE SEA. Deep water goes dark and blue; the shallows keep some sand through them, which is what
    # makes a coast read as a coast rather than as a blue rectangle stuck to the edge.
    w = sf(f["water"])
    deep = smoothstep(0.0, 4.0, w)
    shal = sea * (1 - deep)
    out = out * (1 - shal[..., None]) + (out * 0.72 + np.array([40.0, 95.0, 110.0], np.float32) * 0.45) \
        * shal[..., None]
    out = out * (1 - deep[..., None]) + np.array([16.0, 44.0, 66.0], np.float32) * deep[..., None]

    lum = P.sample_field(P.noise(5.0, "lum", octaves=2), X, Y)
    out = out * (0.93 + 0.14 * lum)[..., None]
    return np.clip(out, 0, 255)


def bake(preview=None, sc=5):
    import importlib
    M = importlib.import_module("tools.handbuilt_northern_tanaris")
    check_palette()
    P = Painter(M.W, M.H, TEX_DIR, seed=6610)
    scores = build_scores(P, M)

    keys = list(MATERIALS)
    win = np.stack([scores[k] for k in keys]).argmax(axis=0)
    share = {k: float((win == i).mean()) for i, k in enumerate(keys)}
    print("northern_tanaris: " + "  ".join(f"{k} {v:.1%}" for k, v in
                                           sorted(share.items(), key=lambda kv: -kv[1])))
    dead = [k for k in keys if share[k] < DEAD]
    if dead:
        print(f"northern_tanaris: {len(dead)} material(s) never win and will never be seen: "
              f"{', '.join(dead)}")

    out = ROOT / M.BAKED_DIR
    written = P.bake(MATERIALS, scores, out, chunk_tiles=20, post=post)
    print(f"northern_tanaris: baked {len(written)} chunks -> {out}")
    if preview:
        full = Image.new("RGB", (M.W * TILE_PX, M.H * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        full.resize((M.W * sc, M.H * sc), Image.LANCZOS).save(preview)
        print("preview", preview)


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    bake(pv)
