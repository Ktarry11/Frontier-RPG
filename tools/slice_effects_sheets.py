#!/usr/bin/env python3
"""Slice Kyle's ten environment-effect sheets (docs/environment_effects_art_prompts.md, EFX1 to EFX10).

    PYTHONPATH=. python3 tools/slice_effects_sheets.py

Sources: tools/building_sheets/efx1.png .. efx10.png (1536x1024 each, delivered 21 Nov 2026; art sources are
gitignored like every other sheet). Four kinds, as the doc sets out:

  light (EFX1, EFX2, EFX10)  3 x 3 panels on black, added over the screen: written as RGB, black stays black
  shade (EFX3)               3 x 3 panels on white, multiplied over the screen: written as RGB, white stays white
  layers (EFX4, EFX5)        3 x 3 panels on black, scrolled and added: made seamless on all four sides here (a
                             half-offset copy cross-faded over the seams), since a generated "tileable" panel never
                             quite is
  sprites (EFX6 to EFX9)     6 x 4 cells on magenta: keyed to RGBA by unmixing the magenta out of every pixel it
                             bled into (glows and smoke were painted half over it), trimmed to the art

Panels are cut a little inside their cell so the gutters never show. Two shade panels (the canopy dapple and the
cloud shadows) and EFX9's three water tiles are made seamless too.
"""
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools/building_sheets"
OUT = ROOT / "assets/effects"

LIGHT1 = ["light_autumn_rays", "light_jungle_shafts", "light_desert_glare", "light_dawn", "light_dusk",
          "light_overcast", "light_golden_canopy", "light_winter_sun", "light_sun_bloom"]
LIGHT2 = ["light_moonlight", "light_fel_glow", "light_plague_miasma", "light_arcane_shimmer", "light_cave_skylight",
          "light_crystal_cave", "light_ember_underglow", "light_holy_column", "light_aurora_glow"]
SHADE = ["shade_canopy_dapple", "shade_jungle_canopy", "shade_cloud_shadows", "shade_cave_vignette", "shade_night",
         "shade_haunted", "shade_storm_gloom", "shade_underwater", "shade_dust_haze"]
WEATHER = ["wx_rain_light", "wx_downpour", "wx_snow_light", "wx_blizzard", "wx_sandstorm", "wx_ashfall", "wx_drizzle",
           "wx_sea_spray", "wx_leaf_drift"]
ATMOS = ["atm_ground_fog", "atm_fog_bank", "atm_swamp_mist", "atm_plague_fog", "atm_waterfall_mist", "atm_steam",
         "atm_golden_motes", "atm_fireflies", "atm_void_wisps"]
SKY = ["sky_lightning_a", "sky_lightning_b", "sky_lightning_flash", "sky_aurora", "sky_shooting_stars",
       "sky_falling_star", "sky_rift_glow", "sky_rainbow", "sky_heat_shimmer"]
P1 = ["p_leaf_maple", "p_leaf_aspen", "p_leaf_oak", "p_leaf_dry", "p_leaf_elven", "p_leaf_green",
      "p_petal_pink", "p_petal_white", "p_petal_gold", "p_seed_dandelion", "p_seed_maple", "p_pollen",
      "p_snowflake", "p_snow_soft", "p_raindrop", "p_rain_splash", "p_ripple", "p_spray",
      "p_ember", "p_ash_burning", "p_ash", "p_dust_puff", "p_sand_swirl", "p_feather_white"]
P2 = ["p_mote_arcane", "p_mote_holy", "p_mote_void", "p_mote_fel", "p_mana_spark", "p_star_twinkle",
      "p_firefly", "p_wisp_light", "p_spore_fel", "p_spore_plague", "p_seed_glow", "p_sap_drop",
      "p_smoke_grey", "p_smoke_black", "p_steam", "p_cloud_small", "p_gas_poison", "p_shadow_wisp",
      "p_spark_lightning", "p_shard_crystal", "p_bubble", "p_bubbles", "p_rune_gold", "p_feather_black"]
LIFE = ["life_geese", "life_crow", "life_gull", "life_vulture", "life_parrots", "life_raven",
        "life_monarch", "life_butterfly_blue", "life_dragonfly", "life_moth", "life_bats", "life_bees",
        "life_duck", "life_swan", "life_fish", "life_fish_school", "life_fish_big", "life_lily_frog",
        "shadow_hawk", "shadow_flock", "shadow_wyvern", "shadow_dragon", "shadow_zeppelin", "shadow_griffin"]
FX = ["fx_caustics_deep", "fx_caustics_shallow", "fx_sun_sparkle", "fx_shore_foam", "fx_fall_foam", "fx_fall_mist",
      "fx_splash", "fx_geyser", "fx_mud_bubble", "fx_lava_bubble", "fx_steam_vent", "fx_fountain_spray",
      "fx_dust_devil", "fx_dust_step", "fx_leaf_pile", "fx_mushroom_ring", "fx_glow_mushrooms", "fx_scorch",
      "fx_puddle", "fx_drip", "fx_slime_pool", "fx_fel_crack", "fx_arcane_circle", "fx_snow_swirl"]

#: sheet -> (kind, names, folder)
SHEETS = {1: ("panel", LIGHT1, "light"), 2: ("panel", LIGHT2, "light"), 3: ("panel", SHADE, "shade"),
          4: ("layer", WEATHER, "weather"), 5: ("layer", ATMOS, "weather"), 6: ("sprite", P1, "particles"),
          7: ("sprite", P2, "particles"), 8: ("sprite", LIFE, "life"), 9: ("sprite", FX, "ground"),
          10: ("panel", SKY, "light")}
SEAMLESS_SHADE = {"shade_canopy_dapple", "shade_cloud_shadows"}
TILES = {"fx_caustics_deep", "fx_caustics_shallow", "fx_sun_sparkle"}     # EFX9's cells that fill edge to edge
INSET = 9


def seamless(img):
    """Cross-fade a half-offset copy over the seams, so the panel tiles on all four sides."""
    a = np.asarray(img, np.float32)
    h, w = a.shape[:2]
    b = np.roll(np.roll(a, h // 2, 0), w // 2, 1)
    yy = np.abs(np.linspace(-1, 1, h))[:, None]
    xx = np.abs(np.linspace(-1, 1, w))[None, :]
    edge = np.clip(np.maximum(yy, xx) * 1.6 - 0.6, 0, 1)            # 0 in the middle, 1 at the edges
    edge = edge[..., None] if a.ndim == 3 else edge
    out = a * (1 - edge) + b * edge
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), img.mode)


def soft_key(img):
    """Magenta to alpha, unmixing every pixel the magenta bled into. Generated glows, smoke and steam were painted
    half over the background, so their pink is the background showing through: observed = a * colour + (1 - a) *
    magenta, solved for a and the colour. A pixel only counts as bled-into when its red and blue sit level the way
    magenta's do; real violet (blue well above red, a void mote, an arcane rune) is left exactly as painted."""
    a = np.asarray(img.convert("RGB"), np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mag = np.clip((np.minimum(r, b) - g) / 255.0, 0, 1)
    level = np.clip(1.0 - np.abs(r - b) / 110.0, 0, 1)
    m = mag * level
    alpha = np.clip(1.0 - m / 0.60, 0.0, 1.0)
    M = np.array([250.0, 4.0, 253.0])
    keep = np.maximum(alpha, 0.04)[..., None]
    col = (a - (1 - keep) * M) / keep
    # unmixing a near-grey pixel overshoots into green: no unmixed pixel may come out greener than it is red or blue
    gmax = np.maximum(col[..., 0], col[..., 2])
    col[..., 1] = np.where(alpha < 0.999, np.minimum(col[..., 1], gmax), col[..., 1])
    out = np.dstack([np.clip(col, 0, 255), alpha * 255]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def trim(img, pad=4):
    bbox = img.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    if not bbox:
        return img
    x0, y0, x1, y1 = bbox
    return img.crop((max(0, x0 - pad), max(0, y0 - pad), min(img.width, x1 + pad), min(img.height, y1 + pad)))


def main():
    made = 0
    for n, (kind, names, folder) in SHEETS.items():
        src = SRC / f"efx{n}.png"
        if not src.exists():
            print(f"missing {src}")
            continue
        im = Image.open(src).convert("RGB")
        cols, rows = (3, 3) if kind in ("panel", "layer") else (6, 4)
        cw, ch = im.width / cols, im.height / rows
        (OUT / folder).mkdir(parents=True, exist_ok=True)
        for i, name in enumerate(names):
            c, r = i % cols, i // cols
            box = (int(c * cw), int(r * ch), int((c + 1) * cw), int((r + 1) * ch))
            if kind in ("panel", "layer"):
                cell = im.crop((box[0] + INSET, box[1] + INSET, box[2] - INSET, box[3] - INSET))
                if kind == "layer" or name in SEAMLESS_SHADE:
                    cell = seamless(cell)
                cell.save(OUT / folder / f"{name}.png")
            else:
                cell = im.crop(box)
                if name in TILES:
                    # the tile fills its cell: find the art's edges (where the magenta stops) and keep the inside
                    a = np.asarray(cell, np.int16)
                    pink = (a[..., 0] > 200) & (a[..., 2] > 200) & (a[..., 1] < 80)
                    ys, xs = np.nonzero(~pink)
                    t = cell.crop((xs.min() + 6, ys.min() + 6, xs.max() - 6, ys.max() - 6))
                    seamless(t).save(OUT / folder / f"{name}.png")
                else:
                    trim(soft_key(cell)).save(OUT / folder / f"{name}.png")
            made += 1
    print(f"{made} effects sliced to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
