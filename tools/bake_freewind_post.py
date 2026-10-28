"""
Bake Freewind Post - three mesa tops over a very long drop.

    PYTHONPATH=. python3 tools/bake_freewind_post.py [--preview OUT.png]

THE WHOLE JOB IS SELLING HEIGHT, AND THE ZEPPELIN TOWER ALREADY SOLVED IT.

Kyle: "let's do the 'high in the air' style that you did with the zepplin towers. That fuzzy ground
texture with 'clouds' over it. it gives the look of being high up."

A flat mesa top seen from directly overhead looks exactly like flat ground, because it IS flat ground.
Nothing about the top itself can say "and there is four hundred feet under this". The only thing that can
is what surrounds it, so this baker spends almost all of its effort on the part of the image the player
never walks on:

    THE FAR GROUND  the canyon floor, painted from the same red Needles tiles as the zone above, then
                    PUSHED AWAY - darkened, desaturated toward blue, and blurred, because distance does
                    all three.
    THE CLOUD       a slow noise field drifting across the floor, thickening it in patches. Cloud BELOW
                    you is the single most legible "you are high up" cue there is.
    THE SHADOW      each deck's own silhouette, offset down and to the right, laid dark on the floor. A
                    shadow that far from the thing casting it is what tells the eye how far down it is -
                    and it is the one cue that gives an actual DISTANCE rather than a vague sense of air.

On the decks themselves the palette is plain, because the drama belongs to the drop: wind-scoured
hardpan and pale stone on the tops, and PLANKING on the bridges. The bridges are the only aspen in the
picture, which is the point of the place - the stone is Azeroth's and the wood came off a mountain that
arrived three years ago.
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

#: The far ground is painted from the SAME tiles as the zone overhead, which is why it reads as the same
#: country rather than as a backdrop - the player has walked on that floor and recognises it.
MATERIALS = {
    # --- deck surface: the mesa tops
    "hardpan":  ("sn_hardpan", "sn_dust_pebbles", 1.0),
    "pale":     ("sn_sandstone_pale", "sn_polished_shelf", 1.0),
    "lichen":   ("sn_lichen_orange", "sn_gravel_scatter", 1.0),
    "camp":     ("sn_camp_dirt", "sn_straw", 1.0),
    "terrace":  ("sn_stone_terrace", None, 1.0),
    # --- the bridges: the only aspen in the picture
    "plank":    ("sn_plank_deck", "sn_boardwalk", 1.0),
    "matting":  ("sn_rope_matting", None, 1.0),
    # --- the canyon floor, far below
    "far_sand": ("sn_red_sand", "sn_rippled_sand", 1.0),
    "far_mud":  ("sn_dry_mud", "sn_cracked_clay", 1.0),
    "far_wash": ("sn_wash_gravel", "sn_salt_crust", 1.0),
    "far_scrub": ("sn_desert_scrub", "sn_dust_drift", 1.0),
}


def build_scores(P, M):
    S = {}
    gx, gy = P.gx, P.gy
    n_big = P.noise(10.0, "big", octaves=3)
    n_mid = P.noise(4.0, "mid", octaves=3)
    n_fine = P.noise(1.8, "fine", octaves=2)

    deck = M.deck_field(gx, gy).astype(np.float32)
    bridge = M.bridge_field(gx, gy).astype(np.float32)
    on = smoothstep(-0.5, 0.5, deck)
    br = smoothstep(-0.5, 0.5, bridge)
    top = on * (1 - br)

    P.fields = dict(deck=deck, bridge=bridge, on=on, br=br)

    # ---- the tops. Plain on purpose: the drama is the drop, not the floor you stand on.
    S["hardpan"] = 0.35 + 1.30 * top * (0.55 + 0.45 * n_big)
    S["pale"] = 0.10 + 1.25 * top * smoothstep(0.46, 0.74, n_mid)
    S["lichen"] = 0.05 + 1.10 * top * smoothstep(0.62, 0.86, n_fine)
    # where people actually live - the Long Mesa's middle gets trodden down to camp dirt
    camp = smoothstep(25.0, 9.0, np.hypot((gx - 52) / 1.35, gy - 94))
    S["camp"] = 0.05 + 1.60 * top * camp * (0.6 + 0.4 * n_mid)
    S["terrace"] = 0.02 + 1.30 * top * camp * smoothstep(0.70, 0.92, n_fine)

    # ---- the bridges
    S["plank"] = -0.4 + 2.80 * br
    S["matting"] = -0.6 + 2.40 * br * smoothstep(0.70, 0.92, n_mid)

    # ---- the canyon floor. Scored everywhere and shown only off-deck; post() does the pushing-away.
    off = 1.0 - on
    S["far_sand"] = 0.25 + 1.15 * off * (0.5 + 0.5 * n_big)
    S["far_mud"] = 0.08 + 1.30 * off * smoothstep(0.40, 0.70, n_mid)
    S["far_wash"] = 0.05 + 1.20 * off * smoothstep(0.58, 0.84, n_fine)
    S["far_scrub"] = 0.05 + 1.15 * off * smoothstep(0.50, 0.80, n_big)
    for k in ("hardpan", "pale", "lichen", "camp", "terrace", "plank", "matting"):
        S[k] = S[k] - 10.0 * off
    for k in ("far_sand", "far_mud", "far_wash", "far_scrub"):
        S[k] = S[k] - 10.0 * on

    P.scores = S
    return S


def post(rgb, X, Y, P):
    f = P.fields
    sf = lambda a: P.sample_field(a.astype(np.float32), X, Y)          # noqa: E731
    on, br = sf(f["on"]), sf(f["br"])
    out = rgb.copy().astype(np.float32)

    # ---------------------------------------------------------------- the drop
    # Everything below is applied to the WHOLE image and then masked back to off-deck only, which keeps
    # the deck edge hard. A soft edge here would read as fog on the ground rather than as a cliff.
    far = out * 0.72                                     # distance darkens

    # ...and desaturates toward blue. Aerial perspective: the further away a thing is, the more of the
    # sky between you and it, so red rock four hundred feet down is a duller, bluer red than red rock
    # under your boots. This is why the floor does not just look like the deck with the lights off.
    grey = far.mean(axis=-1, keepdims=True)
    far = far * 0.68 + grey * 0.32
    far = far * np.array([0.90, 0.96, 1.13], np.float32)

    # THE CLOUD. Below you, which is the single most legible "high up" cue there is.
    cloud = P.sample_field(P.noise(7.0, "cloud", octaves=3), X, Y)
    # The floor has to stay READABLE through this. Kyle asked for a fuzzy ground texture with clouds
    # over it; at 0.30 + 0.42 the cloud was the picture and the canyon underneath had vanished, which
    # also swallowed the deck shadows - and the shadows are the cue that gives an actual distance.
    thick = 0.16 + 0.30 * smoothstep(0.34, 0.94, cloud)
    far = far * (1 - thick[..., None]) + np.array([150.0, 162.0, 184.0], np.float32) * thick[..., None]

    # THE SHADOW. Each deck's silhouette, thrown down and to the right onto the floor. This is the cue
    # that gives an actual DISTANCE instead of a vague sense of air - the further the shadow sits from
    # the thing casting it, the higher the thing reads.
    import importlib
    Z = importlib.import_module("tools.handbuilt_freewind_post")
    gx = X.astype(np.float32) / TILE_PX
    gy = Y.astype(np.float32) / TILE_PX
    sh = Z.deck_field(gx - 8.0, gy - 11.0)
    shadow = smoothstep(-2.0, 2.0, sh)
    far = far * (1 - 0.42 * shadow[..., None])

    m = on[..., None]
    out = out * m + far * (1 - m)

    # ---------------------------------------------------------------- the decks
    lum = P.sample_field(P.noise(5.0, "decklum", octaves=2), X, Y)
    out = out * (1 - m) + (out * (0.91 + 0.17 * lum)[..., None]) * m

    # A bright lip all the way round every deck: sunlit stone at the very edge, which separates the top
    # from the drop in one pixel and is what makes the silhouette read.
    d = sf(f["deck"])
    lip = smoothstep(0.0, 0.9, d) * (1 - smoothstep(0.9, 2.6, d))
    out = out + 34 * lip[..., None] * np.array([1.0, 0.94, 0.80], np.float32)

    # the bridges sit a shade darker than the stone - timber in its own shadow, slung between two rims
    out = out * (1 - 0.13 * br[..., None])
    return np.clip(out, 0, 255)


def bake(preview=None, sc=5):
    import importlib
    M = importlib.import_module("tools.handbuilt_freewind_post")
    P = Painter(M.W, M.H, TEX_DIR, seed=911)
    scores = build_scores(P, M)
    out = ROOT / M.BAKED_DIR
    written = P.bake(MATERIALS, scores, out, chunk_tiles=20, post=post)
    print(f"freewind_post: baked {len(written)} chunks -> {out}")
    if preview:
        full = Image.new("RGB", (M.W * TILE_PX, M.H * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        full.resize((M.W * sc, M.H * sc), Image.LANCZOS).save(preview)
        print("preview", preview)


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    bake(pv)
