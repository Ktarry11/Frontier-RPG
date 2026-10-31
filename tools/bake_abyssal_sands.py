#!/usr/bin/env python3
"""
Bake The Abyssal Sands - gold desert with eleven holes in it.

    PYTHONPATH=. python3 tools/bake_abyssal_sands.py [--preview OUT.png]

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

MATERIALS = {
    # --- the ranges. NO quay, harbour or road family: this zone has no sea and no road, and
    # carrying three materials that can never win is how a palette rots. The dead-material check
    # reported all three on the first bake and they are gone rather than given a token weight.
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
    "rock":     ("tan_rubble_sandstone", "tan_scrub_sand", 1.0),
    "crag":     ("tan_basalt_grit", None, 1.0),
    # --- 124-140: the road and the ground people have used
    "hardpan":  ("tan_hardpan_orange", "tan_scrub_sand", 1.0),
    "drift":    ("tan_dust_drift", None, 1.0),
    # --- 147-156: the open sand, most of the map
    "sand":     ("tan_sand_gold", "tan_dune_ripple", 1.0),
    "pebble":   ("tan_sand_pebble", None, 1.0),
    # --- 181: the ruins
    "stone":    ("tan_sandstone_floor", "tan_paving_carved", 1.0),
}

#: THE SAND FAMILY HAS TO BE LOUD. See the note above - this is a floor, not a ceiling, and it is the
#: mirror image of bake_saltwheel's MAX_SAT. Only the families that make up the desert body are held
#: to it; rock, tar and harbour dirt are legitimately drab and are exempt.
MIN_SAT = 60.0
LOUD_FAMILIES = ("sand", "pebble", "hardpan", "drift", "stone", "rock")
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
    # THE PAINT HAS TO AGREE WITH THE COLLISION RULE. town_kit marks a tile rock iff cliff > 0,
    # so the transition belongs AT zero. Smoothstepped over (-0.5, 0.5) - which Northern Tanaris
    # gets away with because its ground is mostly flat - rock bled a long way onto walkable ground
    # here, where eleven pits mean gradients everywhere: it took 82% of the paint on a map that is
    # only 55% rock, and four materials never won at all. The window is the fix, not the weights.
    # USE THE COLLISION BOOLEAN, NOT A SMOOTHSTEP OF THE FIELD IT CAME FROM.
    #
    # town_kit marks a tile rock iff cliff > 0. Smoothstepping that same field gives a soft edge,
    # and in a zone where eleven pits put a gradient under nearly everything, "soft" meant rock
    # scored halfway on huge areas of perfectly walkable sand - 82% of the paint on a map that is
    # 54% rock, with four materials never winning at all. Northern Tanaris survives the soft version
    # only because its ground is genuinely flat between landmarks.
    #
    # The collision edge is a hard edge. Painting it as one is not a compromise, it is the truth,
    # and the tile blending softens it at the only scale that matters anyway.
    rock = (cliff > 0).astype(np.float32)
    sea = np.zeros_like(cliff)                  # no water at all here; that is the premise
    # NO ROAD IN THIS ZONE. There was one and it is in a hole. road and rd are kept at zero rather
    # than deleted so the scoring below reads the same as Northern Tanaris's and can be compared.
    rd = np.full_like(cliff, -9.0)
    road = np.zeros_like(cliff)
    # THE PITS ARE WHAT THIS ZONE IS PAINTED AROUND. pit_in is the hole, lip is the ring of spoil
    # thrown up round it, and the lip is where the player actually walks - they are following an
    # edge trying to get past it - so it gets the made-ground materials.
    pit_in = smoothstep(-0.5, 1.5, M._pit_field(gx, gy).astype(np.float32))
    lip = M._rim_lip(gx, gy).astype(np.float32)

    # THE TWO RUINS, AS FIELDS - AND WOBBLED, BECAUSE A PAINT FIELD PAINTS ITS OWN SHAPE.
    #
    # The first bake used the bare primitives: a rectangle for Gadgetzan and an ellipse for
    # Zul'Farrak. They came out as a literal beige rectangle and a literal circle sitting on the
    # sand, with edges a ruler could have drawn. The TERRAIN is allowed to be geometric - Gadgetzan's
    # wall is a rectangle on purpose, because somebody built it - but the GROUND around a ruin is
    # not, and painting it with the same primitive turns the whole quarter into a shape.
    ruin = np.clip(lip, 0.0, 1.0)

    # how close to the coast, for the harbour band
    coast = np.zeros_like(cliff)

    P.fields = dict(cliff=cliff, water=water, rock=rock, sea=sea, road=road, ruin=ruin,
                    pit=pit_in)

    # ---- the ranges. ONE MATERIAL, NOT TWO ALTERNATING: the pair's second tile is the lighter
    # rubble, and letting the painter swap between them freely turned 46% of the map into a leopard
    # print - the same failure the Saltwheel rim had. Rubble gets a thin slice of the noise and the
    # basalt holds the rest, so the ranges read as one mass with weathering in it.
    S["rock"] = -0.3 + 3.40 * rock * (1 - pit_in) * band(n_big, 0.00, 0.82)
    S["crag"] = -0.3 + 3.40 * rock * np.maximum(pit_in, (1 - pit_in) * band(n_big, 0.82, 1.01))

    # ---- the port end
    # ---- the road, and the worn ground that spreads off it
    # THE SPOIL RINGS ARE THIS ZONE'S "WORN GROUND". There is no road, so the thing a player
    # actually walks on - following the lip of a hole, trying to get round it - is freshly turned
    # ground thrown up by the collapse. hardpan was dead on the first bake for being gated on a
    # road that does not exist; it has a real job here instead of a token weight.
    S["hardpan"] = 0.15 + 2.40 * (1 - rock) * ruin * band(n_mid, 0.00, 0.62)
    S["drift"] = 0.15 + 2.40 * (1 - rock) * ruin * band(n_mid, 0.62, 1.01)

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

    # THE HOLES GO DARK, which is the only way a pit reads as a pit from above. At the same value
    # as the surrounding cliff it is a crater with a floor; dropped hard and cooled, it is a hole
    # with no bottom you can see, which is what "abyssal" has to mean here.
    pit = sf(P.fields["pit"])
    deep = out * 0.34
    deep = deep * 0.80 + deep.mean(axis=-1, keepdims=True) * 0.20
    deep = deep * np.array([0.92, 0.96, 1.08], np.float32)
    out = out * (1 - pit[..., None]) + deep * pit[..., None]

    lum = P.sample_field(P.noise(5.0, "lum", octaves=2), X, Y)
    out = out * (0.93 + 0.14 * lum)[..., None]
    return np.clip(out, 0, 255)


def bake(preview=None, sc=5):
    import importlib
    M = importlib.import_module("tools.handbuilt_abyssal_sands")
    check_palette()
    P = Painter(M.W, M.H, TEX_DIR, seed=6611)
    scores = build_scores(P, M)

    keys = list(MATERIALS)
    win = np.stack([scores[k] for k in keys]).argmax(axis=0)
    share = {k: float((win == i).mean()) for i, k in enumerate(keys)}
    print("abyssal_sands: " + "  ".join(f"{k} {v:.1%}" for k, v in
                                           sorted(share.items(), key=lambda kv: -kv[1])))
    dead = [k for k in keys if share[k] < DEAD]
    if dead:
        print(f"abyssal_sands: {len(dead)} material(s) never win and will never be seen: "
              f"{', '.join(dead)}")

    out = ROOT / M.BAKED_DIR
    written = P.bake(MATERIALS, scores, out, chunk_tiles=20, post=post)
    print(f"abyssal_sands: baked {len(written)} chunks -> {out}")
    if preview:
        full = Image.new("RGB", (M.W * TILE_PX, M.H * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        full.resize((M.W * sc, M.H * sc), Image.LANCZOS).save(preview)
        print("preview", preview)


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    bake(pv)
