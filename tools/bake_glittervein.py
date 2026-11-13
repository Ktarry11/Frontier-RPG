#!/usr/bin/env python3
"""
Bake Glittervein - a dead desert rim grading down into a lit oasis, with crystal seams up the wall.

    PYTHONPATH=. python3 tools/bake_glittervein.py [--preview OUT.png]

Kyle: "a mixture of tropical / arcane / mystic...so underdark mixed with barrens oasis style."

THE PAINT IS THE ZONE'S ARGUMENT AND IT HAS TO BE A GRADIENT WITH DEPTH. The whole premise is that
the hole is the only reason anything is alive for a hundred miles, so the top has to be dead sand
and the bottom has to be green, and the player has to be able to SEE that from the rim before
anybody tells them. Props carry some of that; paint carries most of it, because paint covers every
tile and props cover a few hundred.

    depth 0.00-0.15   THE DRY RIM        gold sand, loud, the brightest large area on the map
    depth 0.15-0.45   THE TERRACES       sandstone, layered stone, orange hardpan
    depth 0.45-0.70   THE LIMESTONE      mossed and root-cracked - the first damp
    depth 0.70-0.90   THE GREEN SHELF    leaf litter and sunlit grass
    depth 0.90-1.00   THE WATERLINE      fern, wet limestone, shallow and deep water

THE cen_* TILES WERE MADE FOR THIS ZONE. They came off the Flats/Tanaris sheet with the tan_* half
and have been sitting in the Flats' materials directory since: cen_limestone_moss, cen_limestone_wet,
cen_roots_stone, cen_grass_sunlit, cen_leaf_litter, cen_ferns, cen_water_shallow, cen_water_deep.
Eight tiles nobody has used yet, and this is the map they were drawn for.

THE ARCANE IS THE SEAMS AND NOTHING ELSE. vein_field defines five crystal seams running up the
inside wall - the thing the zone is named for and where its magic resistance gear comes from - so
ud_crystal_floor_* and ud_lattice_floor paint ON THEM and nowhere else. Scattering crystal over the
whole hole would read as a magic zone; confining it to the seams reads as a geological fact, and it
means a player can pick a seam out from the rim and walk down to it.

THE ROCK EDGE IS A HARD EDGE. town_kit marks a tile rock iff cliff > 0, so the paint transition
belongs AT zero, not smoothstepped across it. The Abyssal Sands learned this the expensive way: a
soft window on a map full of gradients gave rock 82% of the paint on a map that was 54% rock, with
four materials never winning at all. This map is one continuous gradient from rim to water, so it
is the same trap, worse.
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

FLATS = ROOT / "assets/tiles/shimmering_flats/materials"
NEEDLES = ROOT / "assets/tiles/southern_needles/materials"
UNDER = ROOT / "assets/tiles/underdark/materials"

#: (family -> (tile, variation partner or None, weight)). The second name is the painter's
#: VARIATION LAYER, not a competing material - a pair inside one family breaks its repeat, whereas
#: two families at similar weights is what makes a leopard print. The partner has to be close in
#: value or it reads as blotches rather than as texture.
# LESS IS MORE (13 Nov 2026). Kyle, of the Shimmering Flats: "Its just TOO many tiles ... too many
# blended tiles which looks gross. Sometimes less is more" - and then asked for the same cut across
# the region. One texture per material, no cross-faded pairs, and materials that were only ever a
# variation on the ground beside them now share its texture. The ranges are one calm rock drawn
# large instead of rubble alternating with scrub, which tiled into a patterned border round the map.
MATERIALS = {
    # --- the dry rim: loud gold, and deliberately the brightest large area
    "sand":      ("tan_sand_gold", None, 1.5),
    "hardpan":   ("tan_sand_pebble", None, 1.5),
    # --- the cliff faces and terrace treads
    "rock":      ("tan_sandstone_floor", None, 2.5),
    "terrace":   ("sn_stone_terrace", None, 1.5),
    # --- the limestone band, where the damp starts
    "limestone": ("cen_limestone_moss", None, 1.5),
    "wet":       ("cen_limestone_wet", None, 1.0),
    # --- the green shelf
    "grass":     ("cen_leaf_litter", None, 1.5),
    "fern":      ("cen_ferns", None, 1.0),
    # --- the pool
    "shallow":   ("cen_water_shallow", None, 1.0),
    "deep":      ("cen_water_deep", None, 1.0),
    # --- the haul road. See the note in build_scores.
    "track":     ("sn_packed_path", None, 1.0),
    # --- the seams, and only the seams
    "crystal":   ("ud_crystal_floor_c", None, 1.0),
    "lattice":   ("ud_lattice_floor", None, 1.0),
}

#: which directory each tile came from. Three sheets feed this map, which is the point of it.
DIRS = {}
for _fam, (_a, _b, _w) in MATERIALS.items():
    for _n in (_a, _b):
        if not _n:
            continue
        DIRS[_n] = (UNDER if _n.startswith("ud_") else
                    NEEDLES if _n.startswith("sn_") else FLATS)

DEAD = 0.0005


def _stage(tmp=ROOT / "assets/tiles/glittervein/_materials"):
    """Painter reads one directory. This map draws from three, so link them into one.

    Symlinks, not copies - the sheets are the source of truth and a copy is a second one that
    silently stops matching the first.
    """
    tmp.mkdir(parents=True, exist_ok=True)
    for name, src in DIRS.items():
        dst = tmp / f"{name}.png"
        want = (src / f"{name}.png").resolve()
        if not want.exists():
            raise FileNotFoundError(f"{want} - {name} is in MATERIALS and not on disk")
        if dst.is_symlink() or dst.exists():
            if dst.resolve() == want:
                continue
            dst.unlink()
        dst.symlink_to(want)
    return tmp


def build_scores(P, M):
    S = {}
    gx, gy = P.gx, P.gy
    n_big = P.noise(9.0, "big", octaves=3)
    n_mid = P.noise(3.6, "mid", octaves=3)
    n_fine = P.noise(1.6, "fine", octaves=2)

    cliff = M.cliff_field(gx, gy).astype(np.float32)
    water = M.water_field(gx, gy).astype(np.float32)
    vein = M.vein_field(gx, gy).astype(np.float32)
    r = M._wr(gx, gy).astype(np.float32)

    # THE DEPTH CURVE, which is the whole gradient. 0 at the rim, 1 at the waterline.
    depth = np.clip((M.R_LIP - r) / (M.R_LIP - M.R_WATER), 0.0, 1.0).astype(np.float32)

    # USE THE COLLISION BOOLEAN, NOT A SMOOTHSTEP OF THE FIELD IT CAME FROM. See the docstring.
    rock = (cliff > 0).astype(np.float32)
    P.fields = {"depth": depth, "rock": rock, "vein": vein, "water": water}

    def dband(lo, hi, soft=0.05):
        return band(depth, lo, hi, soft)

    # --- the rim and the terraces
    S["sand"] = dband(-1.0, 0.18) * (0.72 + 0.5 * band(n_mid, 0.30, 1.2)) * (1 - rock)
    S["hardpan"] = dband(0.10, 0.42) * (0.62 + 0.5 * band(n_mid, -0.2, 0.42)) * (1 - rock)
    S["terrace"] = dband(0.16, 0.52) * (0.60 + 0.5 * band(n_big, 0.22, 1.2)) * (1 - rock)

    # --- the cliff faces. Rock is a hard edge, so it does not need a band to win on.
    S["rock"] = rock * 1.45

    # --- THE HAUL ROAD, and this is a legibility fix rather than decoration. The descent is the
    # zone: one lap down a cut ramp. Painted out of the same depth bands as everything else, the
    # ramp was indistinguishable from the terrace it sits on and the whole interior read as one
    # undifferentiated green-grey mass from above - a player standing on the rim could not see
    # where the way down was. _ramp_lane is already the four-tile strip kept clear of props, so
    # it is exactly the right shape, and goblins have been carting crystal up it for years.
    lane = M._ramp_lane(gx, gy).astype(np.float32)
    S["track"] = lane * (1 - rock) * (0.96 + 0.3 * band(n_fine, -0.3, 0.7)) * 1.38

    # --- the limestone band
    S["limestone"] = dband(0.40, 0.76) * (0.74 + 0.5 * band(n_mid, -0.1, 0.55)) * (1 - rock)
    S["wet"] = dband(0.72, 1.1) * (0.46 + 0.6 * band(n_fine, 0.18, 1.2)) * (1 - rock)

    # --- the green shelf
    S["grass"] = dband(0.66, 0.96) * (0.78 + 0.5 * band(n_big, -0.3, 0.46)) * (1 - rock)
    S["fern"] = dband(0.84, 1.1) * (0.58 + 0.6 * band(n_mid, 0.14, 1.2)) * (1 - rock)

    # --- the pool. Painted off the same field the collision uses, for the same reason as rock.
    S["shallow"] = (water > 0).astype(np.float32) * 1.5
    S["deep"] = (water > 5.0).astype(np.float32) * 1.9

    # --- THE SEAMS. On the vein and nowhere else, and only on the wall where it is exposed.
    on_vein = smoothstep(-1.0, 1.2, vein)
    # A SEAM IS EXPOSED ON A ROCK FACE. Scored on the vein alone it painted amethyst puddles
    # across open terrace floor and over the green shelf, which is where limestone and leaf litter
    # are. Weighting it onto rock puts the crystal in the cliffs the player walks past, which is
    # both what a vein looks like and where the ore nodes and the resistance gear come from.
    face = 0.22 + 0.78 * rock
    S["crystal"] = on_vein * face * (0.9 + 0.6 * band(n_fine, -0.2, 0.6)) * dband(0.08, 0.80) * 1.7
    S["lattice"] = on_vein * face * (0.8 + 0.6 * band(n_fine, 0.4, 1.3)) * dband(0.08, 0.80) * 1.6

    return {k: v.astype(np.float32) for k, v in S.items()}


def post(out, X, Y, P):
    """Light falls off into the hole, and the seams give some of it back."""
    sf = lambda f: P.sample_field(f, X, Y)                              # noqa: E731
    depth = sf(P.fields["depth"])
    vein = sf(P.fields["vein"])

    # THE HOLE GETS DARKER AS IT GOES DOWN, which is the cheapest and most legible way to say
    # "this is deep" on a top-down map. Capped at 32% rather than going to black: the bottom is
    # the destination and a destination you cannot read is a punishment.
    # 0.32 put the whole bottom of the hole into one dark green mass with no terrace legible in
    # it. The depth cue matters less than being able to read the ground you are about to fight on.
    shade = 1.0 - 0.20 * depth
    out = out * shade[..., None]

    # ...and the seams are lit from inside, which is why you can pick one out from the rim.
    # RESTRAINED. At 0.30 with a +26 lift this painted five electric-blue bars across the hole and
    # the crystal tiles underneath did not matter at all. The tile carries the colour; this only
    # has to say "that stone is lit from inside", and the seams are easier to pick out from the
    # rim when they are the only thing glowing than when they are the brightest thing on the map.
    glow = np.clip(smoothstep(-0.5, 2.2, vein), 0, 1) * 0.13
    tint = np.array([0.88, 1.01, 1.16], np.float32)
    out = out * (1 - glow[..., None]) + (out * tint) * glow[..., None] + glow[..., None] * 9.0

    lum = sf(P.noise(5.0, "lum", octaves=2))
    out = out * (0.94 + 0.12 * lum)[..., None]
    return np.clip(out, 0, 255)


def bake(preview=None, sc=4):
    import importlib
    M = importlib.import_module("tools.handbuilt_glittervein")
    tex = _stage()
    P = Painter(M.W, M.H, tex, seed=4912)
    scores = build_scores(P, M)

    keys = list(MATERIALS)
    win = np.stack([scores[k] for k in keys]).argmax(axis=0)
    share = {k: float((win == i).mean()) for i, k in enumerate(keys)}
    print("glittervein: " + "  ".join(f"{k} {v:.1%}" for k, v in
                                      sorted(share.items(), key=lambda kv: -kv[1])))
    dead = [k for k in keys if share[k] < DEAD]
    if dead:
        print(f"glittervein: {len(dead)} material(s) never win and will never be seen: "
              f"{', '.join(dead)}")

    out = ROOT / M.BAKED_DIR
    written = P.bake(MATERIALS, scores, out, chunk_tiles=20, post=post)
    print(f"glittervein: baked {len(written)} chunks -> {out}")
    if preview:
        full = Image.new("RGB", (M.W * TILE_PX, M.H * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        full.resize((M.W * sc, M.H * sc), Image.LANCZOS).save(preview)
        print("preview", preview)


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    bake(pv)
