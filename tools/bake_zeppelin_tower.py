"""
Bake the Zeppelin Tower painting: a planked timber cross over a hazy drop to the ground far below.

    python3 tools/bake_zeppelin_tower.py [--skin orc|forsaken] [--preview out.png] [--scale 14]

Deck shape comes from tools/handbuilt_zeppelin_tower.deck_field (the same function the tile grid is built from).  Plank direction
follows each arm; the hub planks run east-west, with a girder where an arm meets it.  Writes
assets/tiles/zeppelin_tower/baked[_forsaken]/ground_<cx>_<cy>.jpg.
"""
import os
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools import handbuilt_zeppelin_tower as Z            # noqa: E402
from tools.terrain_painter import Painter, smoothstep, TILE_PX  # noqa: E402

V = lambda *c: np.array(c, np.float32)
SKINS = {
    "orc": dict(src=ROOT / "assets/tiles/vot_cluster", planks="vot_planks", planks_native="h",
                ground=("vot_clay_a", "vot_hardpan"), abyss="vot_rock_dark", baked=Z.BAKED_DIR,
                haze=V(108, 124, 154), iron=V(46, 44, 48), beam=V(58, 38, 22),
                live=V(196, 70, 44), idle=V(150, 146, 140)),
    # the Tirisfal twin: weathered grey boards, withered meadow far below, sickly haze, violet pads
    "forsaken": dict(src=ROOT / "assets/tiles/tirisfal/materials", planks="tf_wood_planks", planks_native="v",
                     ground=("tf_withered_meadow", "tf_dead_grass"), abyss="tf_blight_soil", baked=Z.BAKED_DIR + "_forsaken",
                     haze=V(112, 130, 118), iron=V(40, 42, 44), beam=V(40, 36, 36),
                     live=V(150, 80, 190), idle=V(150, 146, 140)),
}
SKIN = SKINS["orc"]
MATERIALS = {
    "planks":   ("planks_h", None, 0.8),
    "planks_r": ("planks_v", None, 0.8),
    "ground":   ("ground_a", "ground_b", 1.6),
    "abyss":    ("abyss", None, 1.6),
}


def make_tex_dir(skin):
    d = Path(tempfile.mkdtemp(prefix="zep_tex_"))
    src = skin["src"]
    shutil.copy(src / f"{skin['ground'][0]}.png", d / "ground_a.png")
    shutil.copy(src / f"{skin['ground'][1]}.png", d / "ground_b.png")
    shutil.copy(src / f"{skin['abyss']}.png", d / "abyss.png")
    pl = Image.open(src / f"{skin['planks']}.png").convert("RGB")
    rot = pl.transpose(Image.ROTATE_90)
    (pl if skin["planks_native"] == "h" else rot).save(d / "planks_h.png")
    (rot if skin["planks_native"] == "h" else pl).save(d / "planks_v.png")
    return d


def is_vertical(gx, gy):
    """North/south arms + aprons: planks run along the arm (north-south)."""
    return (np.abs(gy - Z.CY) > Z.HUB_R) & (np.abs(gx - Z.CX) < Z.HALF_APRON + 0.01)


def build_scores(P):
    d = Z.deck_field(P.gx, P.gy).astype(np.float32)
    vert = is_vertical(P.gx, P.gy)
    deck = np.clip(d * 8.0, -9.0, 9.0)
    S = {
        "planks": np.where(vert, -9.0, deck).astype(np.float32),
        "planks_r": np.where(vert, deck, -9.0).astype(np.float32),
    }
    n = P.noise(6.0, "ground", octaves=3)
    n2 = P.noise(2.5, "abyss", octaves=2)
    void = np.clip(-d * 8.0, -9.0, 9.0)
    S["ground"] = (void - 0.2 + 0.5 * n).astype(np.float32)
    S["abyss"] = (void - 0.85 + 1.3 * smoothstep(0.55, 0.8, n2) - 0.4 * n).astype(np.float32)
    return S


def post(rgb, X, Y, P):
    gx, gy = X / TILE_PX, Y / TILE_PX
    d = Z.deck_field(gx, gy)
    deck = d > 0
    dxc, dyc = gx - Z.CX, gy - Z.CY
    out = rgb.copy()

    # ---------------------------------------------------------------- the void: far ground under haze
    cloud = P.sample_field(P.noise(9.0, "cloud", octaves=3), X, Y)
    haze = 0.46 + 0.16 * smoothstep(0.2, 0.9, cloud)
    far = out * 0.78
    far = far * (1 - haze[..., None]) + SKIN['haze'] * haze[..., None]
    sh = Z.deck_field(gx - 1.1, gy - 1.9)                       # the deck's shadow on the ground far below
    shadow = smoothstep(-2.4, 2.4, sh)
    far = far * (1 - 0.30 * shadow[..., None])
    out = np.where(deck[..., None], out, far)

    # ---------------------------------------------------------------- deck surface
    lum = P.sample_field(P.noise(5.0, "decklum", octaves=2), X, Y)
    out = np.where(deck[..., None], out * (0.90 + 0.18 * lum[..., None]), out)

    # girders where each arm meets the hub, and a ring of iron around the middle
    gird = (np.abs(np.abs(dyc) - Z.HUB_R) < 0.22) & (np.abs(dxc) < Z.HALF_ARM + 0.2)
    gird |= (np.abs(np.abs(dxc) - Z.HUB_R) < 0.22) & (np.abs(dyc) < Z.HALF_ARM + 0.2)
    ring = np.abs(np.hypot(dxc, dyc) - 6.4) < 0.17
    ring |= np.hypot(dxc, dyc) < 0.55
    spoke = ((np.abs(dxc) < 0.10) | (np.abs(dyc) < 0.10)) & (np.hypot(dxc, dyc) < 6.4)
    metal = (gird | ring | spoke) & deck
    out = np.where(metal[..., None], out * 0.35 + SKIN['iron'] * 0.65, out)
    bolt = ((np.abs(dxc * 2 - np.round(dxc * 2)) < 0.07) & (np.abs(gird * 1.0) > 0)) & (np.abs(dyc) > 5)
    out = np.where((bolt & metal)[..., None], out * 0.7 + 70.0 * 0.3, out)

    # painted landing pads at every portal tile: red on the live berths, grey on the reserved ones
    for key, (px, py) in Z.PORTALS.items():
        r = np.hypot(gx - (px + 0.5), gy - (py + 0.5))
        col = SKIN['live'] if key in Z.LIVE_PORTALS else SKIN['idle']
        band = (np.abs(r - 1.55) < 0.12) | (r < 0.18)
        out = np.where((band & deck)[..., None], out * 0.35 + col * 0.65, out)

    # stair head: tread lines running across the southern gangway end
    treads = (gy > Z.TIP1 - 4.2) & (np.abs(dxc) < 3.5) & deck
    saw = (gy % 1.0)
    out = np.where(treads[..., None], out * (0.78 + 0.24 * saw[..., None]), out)

    # ---------------------------------------------------------------- rim: outer beam, then a lit top edge
    beam = deck & (d < 0.34)
    lip = deck & (d >= 0.34) & (d < 0.46)
    out = np.where(beam[..., None], out * 0.28 + SKIN['beam'] * 0.72, out)
    out = np.where(lip[..., None], out * 0.8 + 40.0, out)
    # rail posts every two tiles around the rim
    along = np.where(np.abs(dxc) < np.abs(dyc), gy, gx)
    post_hit = deck & (d < 0.34) & (np.abs((along % 2.0) - 1.0) < 0.16)
    out = np.where(post_hit[..., None], out * 0.4 + SKIN['iron'] * 0.6, out)
    return out


def main():
    global SKIN
    preview = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    skin_name = sys.argv[sys.argv.index("--skin") + 1] if "--skin" in sys.argv else "orc"
    SKIN = SKINS[skin_name]
    tex = make_tex_dir(SKIN)
    try:
        P = Painter(Z.W, Z.H, tex, seed=57)
        scores = build_scores(P)
        out = ROOT / SKIN["baked"]
        written = P.bake(MATERIALS, scores, out, chunk_tiles=20, post=post)
    finally:
        shutil.rmtree(tex, ignore_errors=True)
    print(f"baked {len(written)} chunks -> {out}")
    if preview:
        sc = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 14
        full = Image.new("RGB", (Z.W * TILE_PX, Z.H * TILE_PX))
        for fn, cx, cy, w, h in written:
            full.paste(Image.open(fn), (cx * TILE_PX, cy * TILE_PX))
        full.resize((Z.W * sc, Z.H * sc), Image.LANCZOS).save(preview)
        print("preview", preview)


if __name__ == "__main__":
    main()
