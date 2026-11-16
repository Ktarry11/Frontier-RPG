"""
Bake the Eldest's Crown painting: bark walkways over open air (tools/handbuilt_eldest_sequoia.py, map 2).

    PYTHONPATH=. python3 tools/bake_eldest_crown.py [--preview out.png] [--scale 6]

Kyle, 15 Nov 2026: "for the crown, do that super cool zepplin tower effect bro! DONT have walls...make it feel
like we are walking in the sky" and, pointing at the loop the branches make in the middle of the map: "keep this
central part trees.... rest is open or very little trees". So the crown has no walls. Off a branch is one of two
things:

  THE HEART OF THE CROWN: the ground the branches ring in (void that the map's border can't reach) is the tree's
      own foliage, a little below the walkways, darker the deeper in it goes, with the branches' shadow on it.
  THE DROP: everything else is the forest floor a very long way down (the zeppelin tower's trick): the canopy of
      the woods below drawn small, under blue haze, with cloud banks drifting between, their shadows on the ground,
      and the branches' shadow thrown far and soft.
  THE FRINGE: Kyle, same evening: "have some light green around the branch, should still be a bit lush". Every
      branch carries a band of light green leaves, one to three tiles wide with a lobed edge, that curls down and
      darkens at its rim before the air starts. Leaves are not floor: the fringe is painted over open air.

The walkways are bark, the platforms where branches meet are bark litter, and every branch edge is drawn as the
round side of a branch: darker toward the edge, a dark underside line, a lit top lip.

The map's floor plan is smoothed first the same way the game smooths it (world/cave_smoothing.py), so the
painting and the walkable ground agree.
"""
import os
import shutil
import sys
import tempfile
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools import handbuilt_eldest_sequoia as ES                          # noqa: E402
from tools.terrain_painter import Painter, smoothstep, TILE_PX, MASK_PX     # noqa: E402

MAT = ROOT / "assets/tiles/stonetalon/materials"
V = lambda *c: np.array(c, np.float32)
HAZE = V(156, 186, 214)        # the blue of a long way down
CLOUD = V(238, 242, 246)
CLOUD_SHADE = V(176, 188, 204)
BARK_DARK = V(46, 28, 18)

#: (texture A, texture B or None, tile scale). Scale under 1 draws the texture smaller: far away.
MATERIALS = {
    "walk":    ("walk", None, 0.8),
    "litter":  ("litter", None, 0.9),
    "foliage": ("foliage", "foliage_b", 1.0),
    "fringe":  ("foliage_b", "foliage", 0.75),
    "far":     ("far_a", "far_b", 0.32),
}
TEXTURES = {"walk": "st_branch_walk", "litter": "st_bark_litter", "foliage": "st_canopy_floor",
            "foliage_b": "st_canopy_floor", "far_a": "st_canopy_floor", "far_b": "st_redwood_sorrel"}


def make_tex_dir():
    d = Path(tempfile.mkdtemp(prefix="crown_tex_"))
    for k, stem in TEXTURES.items():
        im = Image.open(MAT / f"{stem}.png").convert("RGB")
        if k == "foliage_b":
            im = im.transpose(Image.ROTATE_90)      # the same leaves turned, so the heart doesn't tile
        im.save(d / f"{k}.png")
    return d


def floor_plan(zone):
    """True where you can stand: everything that is not the crown's 'wall' (open air)."""
    return np.array([[zone.collision_layer[y][x] not in ("wall", "rock") for x in range(zone.width)]
                     for y in range(zone.height)], bool)


def heart_of_crown(floor):
    """Open air the map's border can't reach without crossing a branch: the ring the branches make."""
    H, W = floor.shape
    out = np.zeros_like(floor)
    q = deque()
    for x in range(W):
        for y in (0, H - 1):
            if not floor[y, x] and not out[y, x]:
                out[y, x] = True
                q.append((x, y))
    for y in range(H):
        for x in (0, W - 1):
            if not floor[y, x] and not out[y, x]:
                out[y, x] = True
                q.append((x, y))
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and not floor[ny, nx] and not out[ny, nx]:
                out[ny, nx] = True
                q.append((nx, ny))
    heart = ~floor & ~out
    # drop little pockets (a notch between two touching branches is not the heart of the crown)
    lab, n = ndi.label(heart)
    for i in range(1, n + 1):
        if (lab == i).sum() < 60:
            heart[lab == i] = False
    return heart


class Fields:
    pass


def build_fields(P, zone):
    F = Fields()
    F.fringe = None
    floor = floor_plan(zone)
    F.floor = floor
    F.heart = heart_of_crown(floor)
    # the walkway edge at mask resolution, organic but within half a tile of the real floor plan
    deck = P.tile_mask(floor, threshold=0.5, noise_amp=0.10, key="deck", sigma=0.9)
    inside = ndi.distance_transform_edt(deck) / MASK_PX            # tiles from the edge, on the branch
    outside = ndi.distance_transform_edt(~deck) / MASK_PX          # tiles from the edge, in the air
    F.sd = (inside - outside).astype(np.float32)                   # signed: + on the branch
    # the heart's foliage runs right up under the branches (no gap of sky between leaf and bark)
    grown = ndi.binary_dilation(F.heart, iterations=3) & ~ndi.binary_dilation(~F.floor & ~F.heart, iterations=1)
    hv = P.tile_mask(grown, threshold=0.5, noise_amp=0.0, key="heart", sigma=1.2, soft=True)
    F.heart_f = np.clip(hv + 0.5, 0.0, 1.0).astype(np.float32)     # 0 in the drop, 1 deep in the heart
    F.heart_depth = (ndi.distance_transform_edt(P.tile_mask(F.heart, key="hd", noise_amp=0.0)) / MASK_PX
                     ).astype(np.float32)
    # the platforms where branches meet are bark litter
    plat = np.zeros_like(floor)
    for (cx, cy, rx, ry, _r, _p, _n) in ES.C_CAVERNS.values():
        ys, xs = np.mgrid[0:zone.height, 0:zone.width]
        plat |= ((xs - cx) / (rx + 1)) ** 2 + ((ys - cy) / (ry + 1)) ** 2 < 1.0
    F.plat = P.tile_mask(plat & floor, threshold=0.5, noise_amp=0.22, key="plat", sigma=1.4, soft=True)
    return F


def fringe_width(P):
    """How far the lush leaves round every branch reach out over the air, in tiles: clumps, some reaching three
    tiles out and some barely past the bark, never a band of even width."""
    clump = P.noise(2.4, "fringe", octaves=2)
    big = P.noise(6.0, "fringe_big", octaves=2)
    return (0.35 + 2.8 * smoothstep(0.38, 0.78, clump) * (0.55 + 0.6 * big)).astype(np.float32)


def fringe_field(P, F):
    """The fringe's reach, with any clump that isn't attached to a branch taken out: leaves grow on wood,
    they don't float. Returns a field that is (tiles in from the clump's edge); below zero is air."""
    if getattr(F, "fringe", None) is None:
        fw = fringe_width(P)
        reach = F.sd + fw
        mask = reach > 0
        lab, _n = ndi.label(mask)
        keep = np.unique(lab[(F.sd > 0) & mask])
        attached = np.isin(lab, keep[keep > 0])
        F.fringe = np.where(attached, reach, np.minimum(reach, -0.5)).astype(np.float32)
    return F.fringe


def build_scores(P, F):
    on = np.clip(F.sd * 6.0, -9.0, 9.0)
    off = -on
    heart = F.heart_f
    n = P.noise(3.0, "litter", octaves=2)
    fringe = np.clip(fringe_field(P, F) * 6.0, -9.0, 9.0) * (F.sd < 0.3)
    S = {
        "fringe": np.where(F.sd < 0.0, fringe, -9.0).astype(np.float32),
        "walk": on.astype(np.float32),
        "litter": (on - 0.6 + 4.0 * F.plat + 0.4 * n).astype(np.float32),
        "foliage": (off - 2.0 + 4.0 * heart - np.clip(fringe, 0, 9.0)).astype(np.float32),
        "far": (off - 2.0 + 4.0 * (1.0 - heart) - np.clip(fringe, 0, 9.0)).astype(np.float32),
    }
    S["walk"] = np.minimum(S["walk"], S["walk"] - 4.0 * np.clip(F.plat, 0, 1) + 1.0).astype(np.float32)
    return S


def post_factory(F):
    def post(rgb, X, Y, P):
        out = rgb.copy()
        raw = rgb          # the leaves as painted, before the drop's haze and cloud go over them
        sd = P.sample_field(F.sd, X, Y)
        heart = P.sample_field(F.heart_f, X, Y)
        depth = P.sample_field(F.heart_depth, X, Y)
        branch = sd > 0
        air = ~branch

        # ---------------------------------------------------------------- the drop: far ground under haze
        cl = P.sample_field(P.noise(13.0, "cloud", octaves=4), X, Y)
        cl_sh = P.sample_field(P.noise(13.0, "cloud", octaves=4), X - 2.5 * TILE_PX, Y - 4.0 * TILE_PX)
        cl_lo = P.sample_field(P.noise(13.0, "cloud", octaves=4), X + 0.6 * TILE_PX, Y + 0.9 * TILE_PX)
        # the land a long way down: dark forest and paler clearings in big patches, and a river through it
        land = P.sample_field(P.noise(22.0, "land", octaves=3), X, Y)
        clear = smoothstep(0.55, 0.70, land)
        far = out * 0.78
        far = far * (1 - 0.45 * clear[..., None]) + V(128, 140, 84) * (0.45 * clear[..., None])
        far = far * (0.82 + 0.30 * smoothstep(0.25, 0.75, land)[..., None])
        gx, gy = X / TILE_PX, Y / TILE_PX
        rv = np.abs(gx - (30 + 0.55 * gy + 9.0 * np.sin(gy / 9.0) + 4.0 * np.sin(gy / 3.7)))
        river = smoothstep(1.3, 0.5, rv)
        bank = smoothstep(2.4, 1.2, rv) * (1 - river)
        far = far * (1 - 0.35 * bank[..., None]) + V(150, 140, 100) * (0.35 * bank[..., None])
        far = far * (1 - river[..., None]) + V(82, 120, 138) * river[..., None]
        # cloud shadows on the ground far below, before the haze, so the haze softens them
        far = far * (1.0 - 0.32 * smoothstep(0.56, 0.70, cl_sh)[..., None])
        # the branches' shadow, thrown far and soft
        sh_far = P.sample_field(F.sd, X - 3.5 * TILE_PX, Y - 5.5 * TILE_PX)
        far = far * (1.0 - 0.28 * smoothstep(-3.0, 1.5, sh_far)[..., None])
        haze = 0.36 + 0.14 * P.sample_field(P.noise(7.0, "haze", octaves=2), X, Y)
        far = far * (1 - haze[..., None]) + HAZE * haze[..., None]
        # cloud banks drifting between you and the ground: lit tops, shaded undersides
        c = smoothstep(0.57, 0.80, cl) * (0.75 + 0.25 * smoothstep(0.5, 0.9, cl))
        under = smoothstep(0.0, 0.06, cl - cl_lo)
        ccol = CLOUD * (1 - 0.55 * under[..., None]) + CLOUD_SHADE * (0.55 * under[..., None])
        far = far * (1 - 0.92 * c[..., None]) + ccol * (0.92 * c[..., None])
        # a little more haze right under the branches' edge, so the drop reads as a drop
        rim_mist = smoothstep(-2.5, 0.0, sd) * (1 - heart)
        far = far * (1 - 0.12 * rim_mist[..., None]) + HAZE * (0.12 * rim_mist[..., None])

        # ---------------------------------------------------------------- the heart: the tree's own foliage
        fol = out * (0.80 - 0.30 * smoothstep(0.0, 9.0, depth))[..., None]
        sh_near = P.sample_field(F.sd, X - 0.7 * TILE_PX, Y - 1.2 * TILE_PX)
        fol = fol * (1.0 - 0.42 * smoothstep(-0.6, 0.6, sh_near)[..., None])
        # where the foliage thins at the heart's edge it opens onto the drop
        out = np.where(air[..., None], far * (1 - heart[..., None]) + fol * heart[..., None], out)

        # the lush fringe: clumps of light green leaves round every branch, over the drop and into the heart
        inside = P.sample_field(fringe_field(P, F), X, Y)       # tiles in from the clump's outer edge
        fr = air & (inside > 0)
        dome = smoothstep(0.0, 0.9, inside)                      # each clump rounds over and darkens at its rim
        tint = P.sample_field(P.noise(1.2, "fringe_tint", octaves=2), X, Y)
        lush = raw * V(1.18, 1.38, 0.86)                         # the leaf texture kept, pushed light and lush
        lush = lush * (0.55 + 0.50 * dome[..., None]) * (0.90 + 0.22 * tint[..., None])
        lush = lush * (0.78 + 0.22 * smoothstep(-0.8, 0.0, -sd)[..., None])   # the branch shades its own leaves
        out = np.where(fr[..., None], lush, out)
        # a soft drop shadow of the leaves on the air just past them (only near: the heart, not the far ground)
        past = air & ~fr & (inside > -0.6) & (heart > 0.5)
        out = np.where(past[..., None], out * 0.72, out)

        # ---------------------------------------------------------------- the branch: a round side, not a cut
        lum = P.sample_field(P.noise(5.0, "barklum", octaves=2), X, Y)
        out = np.where(branch[..., None], out * (0.92 + 0.14 * lum[..., None]), out)
        roll = smoothstep(0.0, 1.1, sd)                                  # darker toward the edge
        out = np.where(branch[..., None], out * (0.55 + 0.45 * roll[..., None]), out)
        under_line = branch & (sd < 0.16)
        out = np.where(under_line[..., None], out * 0.30 + BARK_DARK * 0.70, out)
        # light from the north-west: a lit lip on the edges that face it
        gy_, gx_ = np.gradient(P.sample_field(F.sd, X, Y))
        facing = smoothstep(0.0, 0.6, (gx_ + gy_) * 4.0)
        lip = branch & (sd > 0.16) & (sd < 0.45)
        out = np.where(lip[..., None], out + 34.0 * facing[..., None], out)
        return out
    return post


def bake(preview=None, scale=6):
    zone, L = ES.build_crown_baked()
    from world.cave_smoothing import smooth, secret_guard, record
    opened = smooth(zone, secret_guard(zone.name))
    record(zone.name, opened)
    print(f"{zone.name}: {len(opened)} snag tiles opened")
    tex = make_tex_dir()
    try:
        P = Painter(zone.width, zone.height, tex, seed=347)
        F = build_fields(P, zone)
        print(f"branches {int(F.floor.sum())} tiles, heart of the crown {int(F.heart.sum())} tiles, "
              f"drop {int((~F.floor & ~F.heart).sum())} tiles")
        scores = build_scores(P, F)
        out = ROOT / ES.BAKED["crown"]
        for old in out.glob("ground_*.jpg"):
            old.unlink()
        written = P.bake(MATERIALS, scores, out, chunk_tiles=20, post=post_factory(F))
    finally:
        shutil.rmtree(tex, ignore_errors=True)
    print(f"baked {len(written)} chunks -> {out}")
    if preview:
        full = Image.new("RGB", (zone.width * TILE_PX, zone.height * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        full.resize((zone.width * scale, zone.height * scale), Image.LANCZOS).save(preview)
        print("preview", preview)
    return written


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    sc = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 6
    bake(pv, sc)
