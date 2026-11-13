"""
Bake Saltwheel - the goblin town on the start line.

    PYTHONPATH=. python3 tools/bake_saltwheel.py [--preview OUT.png]

ONE GRADIENT CARRIES THE WHOLE PICTURE: THE SALT IS COMING IN FROM THE EDGES.

A town on a salt pan does not decay evenly. The rime starts at the rim, where nobody walks and nothing
gets swept, and works inward along every line the traffic has stopped using. The middle of the straight
is still dark, still rutted, still obviously a road - and six tiles off it the white has taken the
ground back. That one gradient says the three things the zone is about (this was a racetrack, it is
being eaten, and people are still here keeping the middle of it clear) without a single prop having to
say any of them, so almost every score below is driven off distance-from-the-straight and
distance-from-the-rim rather than off noise.

NOISE DOES THE TEXTURE. GEOMETRY DOES THE STORY. The opposite - noise deciding where the salt is -
gives a town with decay sprinkled at random over it, which reads as a dirty town rather than a town
losing an argument with its own ground.

THE RUTS ARE THE ONE THING THAT HAD TO BE IN HERE. sf_track_rut came off Kyle's tile sheet and it is
the only tile in the set that is evidence of the sport: two worn lines down the middle of the straight,
still there three years after the last car. They are scored hardest in the exact centre of the road and
nowhere else, because a rut that wanders is just a texture.
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

#: the Flats' own tiles. The town is standing on the zone it belongs to and should be painted out of
#: the same set, so the walk in from the Raceway does not cross a seam.
TEX_DIR = ROOT / "assets/tiles/shimmering_flats/materials"

#: THE PALETTE IS A VALUE PLAN, AND THE TILES WERE CHOSEN BY MEASURING THEM.
#:
#: Three bakes went wrong before anyone measured anything. The first led with salt tiles, which are
#: all near-white, and produced a town with no internal contrast sitting on a near-black rim - a pale
#: slab on a dark carpet. The third swapped in tiles picked by their NAMES - dune_ripple and
#: sand_pebble for "calm pan outside" - and produced bright orange camouflage, because this sheet
#: holds two completely different families and nothing in the filenames says so:
#:
#:    tan_*  Tanaris desert. Mean saturation 87-172. Gold, and loud.
#:    sf_*   the salt flats. Mean saturation 4-39. Near-neutral.
#:
#: Four tan_ tiles are exceptions (quay_tarred 10, basalt_grit 10, plank_bleached 13, deck_oiled 23)
#: and they are the four that belong in a town. Everything else here is sf_. That is not a guideline,
#: it is MAX_SAT below, checked at bake time, because "use the desaturated ones" is not a thing you
#: can see in a 120x100 thumbnail and it is exactly what three bakes got wrong.
#:
#: With saturation held flat, LUMINANCE carries the whole picture:
#:
#:    63-98    the straight. Tar and oiled boards: the only surfaced ground on the pan, and the one
#:             dark thing in the zone. A dark line through a pale town is the strongest read here.
#:    110-156  the town. Trodden, swept, lived-on.
#:    162      the ruts - LIGHTER than the road they are in, because a rut on a salt pan is where the
#:             tar wore through and the white came back up. Two pale lines down a dark road.
#:    169-184  the pan outside the fence. Calm and slightly paler than the town, so the town reads as
#:             the thing that has been walked on.
#:    194-221  the salt itself, at the fence and in the disused corners. The accent, and nothing more:
#:             at a quarter of the map in the earlier bakes it stopped being an accent and the whole
#:             place read as snow.
# LESS IS MORE (13 Nov 2026). Kyle, of the Shimmering Flats: "Its just TOO many tiles ... too many
# blended tiles which looks gross. Sometimes less is more" - and then asked for the same cut across
# the region. One texture per material, no cross-faded pairs, and materials that were only ever a
# variation on the ground beside them now share its texture. The ranges are one calm rock drawn
# large instead of rubble alternating with scrub, which tiled into a patterned border round the map.
MATERIALS = {
    # --- 63-98: the straight
    "tar":      ("tan_quay_tarred", None, 1.0),
    "oiled":    ("tan_deck_oiled", None, 1.0),
    "rut":      ("sf_hardpan_swept", None, 1.0),
    # --- 98-156: the town
    "clay":     ("sf_dust_hardpan", None, 1.5),
    "trodden":  ("sf_hardpan_swept", None, 1.0),
    "gravel":   ("sf_dust_hardpan", None, 1.5),
    "plank":    ("tan_plank_bleached", None, 1.0),
    # --- 169-184: the pan outside the fence
    "pan":      ("sf_dust_hardpan", None, 1.5),
    "pan_grit": ("sf_dust_hardpan", None, 1.5),
    # --- 194-221: the salt
    "rime":     ("sf_salt_white", None, 1.25),
    "glaze":    ("sf_salt_white", None, 1.25),
    "plates":   ("sf_salt_white", None, 1.25),
}

#: mean per-pixel (max-min) channel spread. Everything in this town is near-neutral; the Tanaris gold
#: next door is 87-172 and a single one of those tiles turns the zone into camouflage.
MAX_SAT = 42.0


def check_palette():
    """Every tile in this palette has to be desaturated. See the note above MATERIALS."""
    import numpy as _np
    from PIL import Image as _I
    loud = []
    for fam, (a, b, _w) in MATERIALS.items():
        for n in (a, b):
            if not n:
                continue
            px = _np.asarray(_I.open(TEX_DIR / f"{n}.png").convert("RGB")).astype(float)
            sat = float((px.max(2) - px.min(2)).mean())
            if sat > MAX_SAT:
                loud.append(f"{fam}/{n} sat={sat:.0f}")
    if loud:
        raise AssertionError("saltwheel palette has loud tiles in it (max "
                             f"{MAX_SAT:.0f}): {', '.join(loud)}")


#: a material that never wins is a tile somebody generated for nothing - see bake_shimmering_flats.
DEAD = 0.0005


def build_scores(P, M):
    S = {}
    gx, gy = P.gx, P.gy
    n_big = P.noise(8.0, "big", octaves=3)
    n_mid = P.noise(3.4, "mid", octaves=3)
    n_fine = P.noise(1.5, "fine", octaves=2)

    town = M.town_field(gx, gy).astype(np.float32)
    road = M.straight_field(gx, gy).astype(np.float32)
    on = smoothstep(-0.5, 0.5, town)
    off = 1.0 - on

    # ---- THE TWO DISTANCES THAT DECIDE EVERYTHING ----
    # how far in from the rim you are (0 at the fence, 1 well inside)
    depth = smoothstep(0.0, 16.0, town)
    # how close to the middle of the road (1 on the centreline, 0 off the pavement)
    centre = smoothstep(-1.0, 5.0, road)
    # the pit row and the trade row: the two bands of trodden ground either side of the straight
    rows = smoothstep(9.0, 2.0, np.abs(np.abs(gy - 50.0) - 12.0)) * smoothstep(14.0, 24.0, gx) \
        * smoothstep(106.0, 96.0, gx)

    P.fields = dict(town=town, road=road, on=on, depth=depth, centre=centre)

    # EVERY FAMILY BELOW PARTITIONS ITS NOISE RATHER THAN STACKING THRESHOLDS ON IT.
    #
    # The first version of this baker scored each variant as "its family's mask, times noise above
    # some number", with a different number per variant. That reads like it spreads them out and it
    # does not: within a family the variant with the lowest threshold wins wherever the family is
    # active and the others never fire. Measured on the first bake, gravel, oiled and plank covered
    # 0.0% of the map and paving covered 0.1% - a third of this palette invisible, exactly the way
    # nine of the Flats' twenty-two materials were. band() gives each variant a slice of the noise
    # it owns outright, which is the only version of this that is checkable.

    # ---- 63-98: the straight, the one dark thing in the zone
    track = band(np.abs(gy - 50.0), 2.0, 4.4, soft=1.0)
    S["tar"] = -0.2 + 3.20 * on * centre * band(n_mid, 0.00, 0.72)
    # the oil is on the pit side, around the workshop, and it leaks off the road onto the apron
    pit = smoothstep(46.0, 18.0, np.hypot((gx - 58.0) * 0.7, gy - 62.0))
    S["oiled"] = -0.2 + 3.20 * on * np.maximum(centre * band(n_mid, 0.72, 1.01),
                                               0.80 * pit * band(n_mid, 0.58, 0.82))
    # TWO WORN LINES, NOT ONE STRIPE. Scored as a solid band down the centreline this tile repeated
    # into a visible zipper - the same stamp eighty times, reading as a railway.
    S["rut"] = 0.10 + 3.60 * on * track * smoothstep(0.0, 4.0, road) * band(n_fine, 0.22, 1.01)

    # ---- 98-156: the town
    rows_n = np.maximum(rows, 0.40 * centre)
    S["clay"] = 0.20 + 2.40 * on * rows_n * band(n_mid, 0.00, 0.40)
    S["trodden"] = 0.20 + 2.40 * on * np.maximum(rows_n, 0.55 * depth) * band(n_mid, 0.40, 0.80)
    S["gravel"] = 0.20 + 2.40 * on * np.maximum(0.70 * rows_n, 0.60 * depth) * band(n_big, 0.52, 1.01)
    S["plank"] = 0.10 + 2.50 * on * rows_n * band(n_mid, 0.80, 1.01)

    # ---- 194-221: the salt, at the fence and in the disused corners and NOWHERE ELSE.
    # Squared so it falls away fast - hard at the rim, effectively gone by the time it reaches the
    # rows. Both earlier bakes let this cover a quarter of the town and the place read as snow.
    # ...and it comes in unevenly, or that was the intent. HONESTLY: this barely works. The ring
    # of rime round the town is still more regular than it should be, because the (1-depth)**2 term
    # dominates and the material choice at the boundary is a hard argmax - scaling creep by noise
    # moves the ring in and out by a tile and does not break it up. Left in because it helps a
    # little and costs nothing, flagged because the comment above it used to claim it was the fix
    # and it is not. If the ring needs properly breaking, the lever is depth itself, not creep.
    reach = 0.30 + 1.70 * P.noise(3.2, "creep", octaves=3)
    creep = np.clip((1.0 - depth) ** 2 * 1.30 * reach
                    + 0.26 * (1.0 - centre) * (1.0 - rows) * (1.0 - depth), 0.0, 1.3)
    S["rime"] = -0.50 + 3.10 * on * creep * band(n_fine, 0.00, 0.50)
    S["glaze"] = -0.50 + 3.10 * on * creep * band(n_fine, 0.50, 0.78)
    S["plates"] = -0.50 + 3.10 * on * creep * band(n_fine, 0.78, 1.01)

    # ---- 169-184: outside the fence. Calm, low-contrast, going on forever.
    S["pan"] = 0.30 + 1.50 * off * band(n_big, 0.00, 0.72)
    S["pan_grit"] = 0.30 + 1.50 * off * band(n_big, 0.72, 1.01)

    outside = ("pan", "pan_grit")
    for k in MATERIALS:
        S[k] = S[k] - (10.0 * on if k in outside else 10.0 * off)

    P.scores = S
    return S


def post(rgb, X, Y, P):
    f = P.fields
    sf = lambda a: P.sample_field(a.astype(np.float32), X, Y)          # noqa: E731
    on, depth, centre = sf(f["on"]), sf(f["depth"]), sf(f["centre"])
    out = rgb.copy().astype(np.float32)

    # THE SAME WASH THAT IS ON THE BUILDINGS, ON THE GROUND THEY STAND ON.
    # tools/asset_pipeline/salt_wash.py lifts the sw_* sprites toward the colour of the pan; if the
    # pan itself stayed fully saturated the buildings would read as pasted onto it. Lifting the
    # ground by the same gradient - strongest at the rim, weakest down the middle of the road - is
    # what makes the town and its buildings look like they are being eaten by the same thing.
    bleach = np.clip(0.22 * (1.0 - depth) + 0.10 * (1.0 - centre), 0.0, 0.30) * on
    salt = np.array([236.0, 234.0, 228.0], np.float32)
    out = out + (salt.reshape(1, 1, 3) - out) * bleach[..., None]

    # the road sits darker than everything around it: oil, rubber and three years of not being swept
    # by the wind the way open pan is
    out = out * (1 - 0.17 * (centre * on)[..., None])

    # outside the fence goes down and slightly blue - it is the pan going on forever and it should not
    # compete with the town for attention
    off = (1 - on)[..., None]
    # NO LIP AT THE FENCE. The first version put a bright line all the way round the town, which on
    # a straight-edged field read as a bevel and made the whole place look like a sticker laid on the
    # pan. The edge is wobbled now and it does not want underlining - the town and the ground outside
    # it are the same ground, and the only thing separating them is that one of them gets swept.
    far = out * 0.88
    far = far * 0.82 + far.mean(axis=-1, keepdims=True) * 0.18
    # the transition is wide on purpose: a town's outskirts are a gradient, not a wall
    t = sf(f["town"])
    blend = smoothstep(-7.0, 3.0, t)[..., None]
    out = far * (1 - blend) + out * blend

    lum = P.sample_field(P.noise(5.0, "lum", octaves=2), X, Y)
    out = out * (0.93 + 0.14 * lum)[..., None]
    return np.clip(out, 0, 255)


def bake(preview=None, sc=5):
    import importlib
    M = importlib.import_module("tools.handbuilt_saltwheel")
    zone, _ = M.build_saltwheel_baked()
    print("saltwheel: layout/field agreement", M.verify(zone))

    check_palette()
    P = Painter(M.W, M.H, TEX_DIR, seed=4471)
    scores = build_scores(P, M)

    keys = list(MATERIALS)
    win = np.stack([scores[k] for k in keys]).argmax(axis=0)
    share = {k: float((win == i).mean()) for i, k in enumerate(keys)}
    print("saltwheel: " + "  ".join(f"{k} {v:.1%}" for k, v in sorted(
        share.items(), key=lambda kv: -kv[1])))
    dead = [k for k in keys if share[k] < DEAD]
    if dead:
        print(f"saltwheel: {len(dead)} material(s) never win and will never be seen: {', '.join(dead)}")

    out = ROOT / M.BAKED_DIR
    written = P.bake(MATERIALS, scores, out, chunk_tiles=20, post=post)
    print(f"saltwheel: baked {len(written)} chunks -> {out}")
    if preview:
        full = Image.new("RGB", (M.W * TILE_PX, M.H * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        full.resize((M.W * sc, M.H * sc), Image.LANCZOS).save(preview)
        print("preview", preview)


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    bake(pv)
