"""
Bake the Aspen Wilderness.

    PYTHONPATH=. python3 tools/bake_aspen_zone.py [--preview OUT.png]

Same machinery as tools/bake_underdark_zone.py and tools/bake_hillsbrad.py - a Painter, per-material score
fields, a post-process - with one difference that is the whole point of this file.

EVERY OTHER ZONE PAINTS BY HAND-DRAWN BLOBS. Hillsbrad and the Underdark declare a PAINT table: put fungus
here, put gravel there, each an ellipse the author placed. That is the right tool for a zone whose regions
are a design decision.

A MOUNTAIN'S GROUND COVER IS NOT A DESIGN DECISION. It follows the terrain, and if it does not, the eye
knows immediately - snow in a valley bottom, meadow on a headwall, a creek bed running across a ridge.
So this baker reads the layout's own elevation, slope and drainage functions and paints from them:

  ELEVATION  decides the big bands. Duff and meadow low down, needle mat through the middle, scree and
             bedrock above treeline, and snow that starts as patches and goes solid near the top.
  SLOPE      decides rock. Steep ground sheds its soil, so the steeper it gets the more bedrock and talus
             show through whatever band it is in. This is why ridges read as ridges from above.
  DRAINAGE   decides wet. Creek gravel and mud follow the incision, not a painted ellipse, so a drainage
             bottom looks like a drainage bottom for its whole length.
  THE BURN   is the one hand-placed region, because a fire IS an event somebody chose, not a consequence
             of the terrain.

SNOW LIES WHERE SNOW LIES. It survives in the lee and in hollows, so the snow score takes a bonus from
flatness and from the concavity the terracing leaves behind, rather than being a clean altitude line. A
hard snowline reads as a contour map; a ragged one reads as a mountain in spring.
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

TEX_DIR = ROOT / "assets/tiles/aspen/materials"
ZONES = {"aspen": "tools.handbuilt_aspen_wilderness"}

MATERIALS = {
    "duff":      ("asp_duff_gold", "asp_duff_brown", 1.0),
    "duff_mix":  ("asp_grass_duff", "asp_log_litter", 1.0),
    "needle":    ("asp_needle_mat", "asp_needle_cones", 1.0),
    "needle_dk": ("asp_needle_dark", "asp_shade_dirt", 1.0),
    "deadfall":  ("asp_deadfall", "asp_root_cracked", 1.0),
    "moss":      ("asp_mossy_roots", "asp_fern_floor", 1.0),
    "grass":     ("asp_grass_summer", "asp_grass_seed", 1.0),
    "meadow":    ("asp_wildflower", "asp_fireweed", 1.0),
    "grazed":    ("asp_turf_grazed", "asp_grass_matted", 1.0),
    "dry_grass": ("asp_grass_dry", "asp_dirt_grazed", 1.0),
    "dirt":      ("asp_dirt_path", "asp_dry_dirt", 1.0),
    "burn":      ("asp_char_ground", "asp_ash_patch", 1.0),
    "gravel":    ("asp_creek_gravel", "asp_grey_gravel", 1.0),
    "mud":       ("asp_mud_bank", "asp_wet_stone", 1.0),
    "scree":     ("asp_scree", "asp_talus", 1.0),
    "granite":   ("asp_granite", "asp_granite_lichen", 1.0),
    "snow":      ("asp_snow_patch", "asp_snow_packed", 1.0),
    "ice":       ("asp_pond_ice", None, 1.0),
    "seam":      ("asp_red_dust", "asp_red_grass", 1.0),
    "road":      ("asp_dirt_path", None, 1.0),
    "verge":     ("asp_grass_dry", None, 1.0),
    "pool_s":    ("asp_creek_bed", "asp_pond_shallow", 1.0),
    "pool_d":    ("asp_pond_deep", None, 1.0),
    "cliff_a":   ("asp_bedrock", "asp_granite", 1.0),
    "cliff_d":   ("asp_stone_frost", "asp_talus", 1.0),
}
LAND = ("duff", "duff_mix", "needle", "needle_dk", "deadfall", "moss", "grass", "meadow", "grazed",
        "dry_grass", "dirt", "burn", "gravel", "mud", "scree", "granite", "snow", "seam", "road", "verge")

# SNOW IS A HINT, NOT A BAND. Kyle, 2026-10-27: "in some areas we can have snow and ice (small patches to
# indicate 'peaks') ... use it sparingly!" An even snowline above TREELINE would blanket the top fifth of a
# 210x180 map in white and read as a cake rather than a range. So the snow score is deliberately starved:
# it needs ALL THREE of near-summit altitude, a flat lee pocket to sit in, and a high noise draw, and it is
# capped so it can never win on open slope. What the eye gets is a handful of bright patches high up, which
# is what tells it those are the peaks - the rest of the alpine stays grey rock. SNOW_BUDGET is the share
# of walkable land the verifier allows to come out white.
SNOW_BUDGET = 0.09


def build_scores(P, M):
    S = {}
    gx, gy = P.gx, P.gy
    n_big = P.noise(9.0, "big", octaves=3)
    n_mid = P.noise(4.0, "mid", octaves=3)
    n_fine = P.noise(1.8, "fine", octaves=2)

    f = M.fields(gx, gy)
    cliff = f["cliff"].astype(np.float32)
    water = f["shallow"].astype(np.float32)
    deep = f["deep"].astype(np.float32)

    # The layout's own terrain functions. This is the whole idea of this baker - see the module docstring.
    elev = M.elevation(gx, gy).astype(np.float32)
    slope = M._slope(gx, gy).astype(np.float32)
    inc = M._incision(gx, gy).astype(np.float32)
    chute = M._chute(gx, gy).astype(np.float32)

    TL, KR = M.TREELINE, M.KRUMMHOLZ
    alp = smoothstep(KR, TL + 2.0, elev)            # 0 forest, 1 alpine
    high = smoothstep(TL, TL + 6.0, elev)           # the top of the range
    low = 1.0 - smoothstep(-4.0, 3.0, elev)         # the Barrens floor and the first benches
    steep = smoothstep(0.26, 0.60, slope)
    flat = 1.0 - smoothstep(0.08, 0.30, slope)
    wet = smoothstep(2.0, 6.5, inc)                 # how deep in a drainage

    cliff_f = np.clip(cliff * 0.5, -0.4, 0.6).astype(np.float32)
    # Light direction, computed HERE on the tile grid and sampled in post(). post() used to difference the
    # elevation across adjacent PIXELS, but elevation changes per TILE and there are 32 pixels to a tile,
    # so the gradient came out ~0.0015, `shade` pinned at a flat 0.5, and the post-process quietly halved
    # the brightness of the entire zone. The map was not dark because the materials were dark; it was dark
    # because of a unit mismatch in its own lighting.
    dzdx = (M.elevation(gx + 1.0, gy) - M.elevation(gx - 1.0, gy)).astype(np.float32) * 0.5
    dzdy = (M.elevation(gx, gy + 1.0) - M.elevation(gx, gy - 1.0)).astype(np.float32) * 0.5

    P.fields = dict(cliff=cliff, cf=cliff_f, water=water, deep=deep,
                    elev=elev, slope=slope, alp=alp, steep=steep, dzdx=dzdx, dzdy=dzdy)

    # THE VALLEYS ARE THE SUBJECT. Rock is now crest-ness (see cliff_field), so everything NOT on a crest
    # is walkable timber, and that timber is most of the map. Kyle, on the first bake: "don't lose out of
    # the gorgeous green too." The dark needle-and-moss ribbons in the drainages were the only part of that
    # bake worth keeping, so here they stop being ribbons - green is the default state of this mountain
    # below treeline, and brown duff is what happens on the dry shoulders between the creeks.
    crest = M._relief(gx, gy).astype(np.float32)
    forest = (1 - alp)

    # THE PALETTE HAS TO LIVE BELOW THE ROCK BAR.
    #
    # The previous pass keyed gold aspen duff to high `crest`, on the reasoning that aspen likes the dry
    # shoulders. That is true and it baked almost black anyway, because ROCK is also keyed to high crest
    # (cliff_field, bar ~0.34 low down) - so every tile dry enough to qualify for duff had already turned
    # to cliff, and the only ground left showing was valley bottom, which is the darkest thing in the set.
    # A material band is only visible in the range of ground that is still walkable.
    #
    # So the forest floor is banded on DRAINAGE DEPTH instead, which varies across the whole walkable
    # range rather than only at its rocky end:
    #     draw   down in a creek bottom  -> dark needle, moss, fern. The deep green.
    #     mid    the open slopes between -> GOLD ASPEN DUFF. This is most of the zone and most of its look.
    #     dry    up near the spur crests -> dry grass and litter, just before it goes to rock.
    # Thresholds are MEASURED off the incision field on walkable land, not guessed: median 6.4, 70th
    # 7.8, 85th 8.9. At (2.6, 6.8) `draw` was ~1 over half the zone, dark needle mat won 52% of the dry
    # land, and the whole descent baked as mud. A creek bottom is the top quarter of the incision, not
    # the top half. Re-check with tools/aspen_palette_report.py after touching any of these.
    draw = smoothstep(7.2, 9.4, inc)                 # 1 only in the bottom of a real drainage
    mid = (1.0 - draw) * smoothstep(0.55, -0.35, crest)
    dry = smoothstep(-0.15, 0.30, crest)

    # ---- the green, in the draws
    S["needle"] = 0.25 + 1.30 * forest * draw * (0.60 + 0.40 * n_mid)
    S["needle_dk"] = 0.10 + 1.25 * forest * smoothstep(8.4, 9.8, inc) * (0.55 + 0.45 * n_fine)
    S["moss"] = 0.08 + 1.10 * forest * draw * smoothstep(0.40, 0.76, n_fine)
    S["deadfall"] = 0.05 + 0.70 * forest * draw * smoothstep(0.70, 0.92, n_mid)

    # ---- the gold, on the slopes. The zone is named after these trees; this is the band that says so.
    S["duff"] = 0.30 + 1.55 * forest * mid * (0.52 + 0.48 * n_big)
    S["duff_mix"] = 0.20 + 1.20 * forest * mid * smoothstep(0.38, 0.72, n_mid)

    # ---- open ground: meadow on the flats, grazed turf in the parks, dry grass near the crests
    S["grass"] = 0.20 + 1.25 * forest * np.maximum(flat, 0.45 * mid) * (0.45 + 0.55 * n_big)
    S["meadow"] = 0.05 + 1.15 * forest * flat * smoothstep(0.56, 0.84, n_mid)
    # ALPINE TURF. `grazed` used to be killed off by (1 - high), which was right when the high ground was
    # an unreachable headwall. Now it is the basin the player arrives in, and bare scree from edge to
    # edge reads as a quarry. Above treeline the flats hold cropped turf and matted grass - tundra - and
    # only the steep ground is stone.
    S["grazed"] = 0.05 + 0.95 * flat * smoothstep(0.52, 0.78, n_big) * np.maximum(forest, 0.85 * alp)
    S["dry_grass"] = np.maximum(0.05 + 0.90 * forest * dry * (0.5 + 0.5 * n_fine),
                                0.05 + 0.80 * alp * flat * smoothstep(0.34, 0.68, n_mid))
    S["dirt"] = 0.02 + 0.40 * steep * forest * smoothstep(0.66, 0.88, n_fine)

    # ---- THE BURN: the one hand-placed region, because a fire is an event rather than a consequence
    burn = P.blob(150, 84, 44.0, 20.0, 0.7, P.warp("burn", amp_tiles=2.4, scale=9.0))
    S["burn"] = 0.05 + 1.30 * burn * (1 - alp) * (0.55 + 0.45 * n_mid)

    # ---- wet: follows the incision, so a drainage bottom looks like one for its whole length
    S["gravel"] = 0.08 + 1.15 * smoothstep(8.0, 9.6, inc) * (1 - alp)
    S["mud"] = 0.05 + 0.95 * smoothstep(1.0, 0.0, -water) * (0.5 + 0.5 * n_fine)

    # ---- rock: steep ground sheds its soil, and above treeline there is nothing else
    # Below treeline, talus spills off CRESTS, not off valley walls - scoring it on `steep` here is what
    # put grey down every drainage in the first bake.
    S["scree"] = 0.05 + 1.25 * np.maximum(alp * (0.4 + 0.6 * steep),
                                          forest * 0.60 * smoothstep(0.9, 2.1, crest))
    S["granite"] = 0.05 + 1.20 * alp * steep * (0.6 + 0.4 * n_mid)

    # ---- SNOW: patches that read as peaks, and nothing more (see SNOW_BUDGET at the top of this file)
    #
    # Three conditions, ALL required, which is what keeps it to patches:
    #   summit  near the top of the range only, well above the general treeline
    #   pocket  a flat lee hollow - the only place late snow actually survives
    #   drift   a thin wind-packed line in a crack, which gets a quarter of the weight
    # The -0.75 floor means that failing the pocket draw puts snow below bare rock, so open alpine slope
    # stays grey however high it is. That asymmetry is the whole trick: a few white eyes on the dark rock
    # tell you where the summits are, and a blanket would not.
    summit = smoothstep(TL + 2.2, TL + 6.5, elev)
    # MORE OF IT, 13 Nov 2026. Kyle: "Aspen can have that golden snow and sun alpine mountain
    # feel." The October rule (snow "sparingly", a hint not a band) left the top of the range grey
    # rock under a cold tint, which is the opposite of a sunlit summit. Still patches, still only
    # near the top - but wider pockets and longer drifts, so the high ground is bright.
    pocket = flat * smoothstep(0.44, 0.74, n_mid)
    drift = smoothstep(0.62, 0.88, n_fine)
    S["snow"] = -0.60 + 3.10 * summit * (0.95 * pocket + 0.42 * drift)
    # ...and snowfields across the open alpine, which is where the eye expects them. The pocket
    # rule alone put almost all of it on the flat ground at the very top of the map - which is the
    # Barrens seam, orange, with white blobs on it.
    S["snow"] = np.maximum(S["snow"], -0.60 + 2.6 * alp * smoothstep(0.50, 0.68, n_mid) * (1.0 - 0.6 * steep))
    S["snow"] = S["snow"] - 5.0 * smoothstep(26.0, 16.0, gy)        # not on the seam

    # ---- THE SEAM: Barrens ground, in a hard line, only at the very top of the map
    seam = smoothstep(21.0, 12.0, gy) * (0.75 + 0.25 * n_fine)
    S["seam"] = -0.4 + 2.2 * seam
    # Nothing else wins up there - the point of the seam is that it does NOT blend.
    for k in ("duff", "duff_mix", "needle", "needle_dk", "grass", "meadow", "moss", "deadfall"):
        S[k] = S[k] - 3.0 * smoothstep(20.0, 13.0, gy)

    # ---- slide paths: swept to gravel and grass, which is why they read as stripes down the timber
    sw = np.clip(chute, 0, None)
    S["gravel"] = np.maximum(S["gravel"], 0.10 + 0.85 * smoothstep(0.0, 3.0, sw))
    S["grass"] = np.maximum(S["grass"], 0.10 + 0.70 * smoothstep(0.0, 3.5, sw) * (1 - alp))

    for k in LAND:
        S.setdefault(k, np.full_like(n_big, -9.0))

    core, verge, _ = P.road_field(list(M.ROADS.values()))
    S["road"] = (0.05 + 1.3 * core).astype(np.float32)
    S["verge"] = np.maximum(0.05, 0.25 + 0.9 * verge * (1 - core)).astype(np.float32)

    wetmask = (water > 0.0).astype(np.float32)
    S["pool_s"] = np.clip(1.6 * water, -9.0, 9.0).astype(np.float32)
    S["pool_d"] = np.clip(1.8 * deep, -9.0, 9.0).astype(np.float32) - 0.4
    # ICE only skins the high tarns. Scored inside the water group and hard-gated on wetmask, so it can
    # never appear on dry ground; down in the timber the open-water tiles win and the creeks run.
    S["ice"] = (1.6 * water - 0.35 + 1.25 * smoothstep(KR + 1.5, TL + 2.5, elev)
                - 14.0 * (1 - wetmask)).astype(np.float32)
    for k in LAND:
        S[k] = (S[k] - 12.0 * wetmask).astype(np.float32)

    depth_dark = smoothstep(2.0, 9.0, np.maximum(cliff, 0))
    cs = 1.6 + 12 * cliff_f
    S["cliff_a"] = (cs - 1.0 * depth_dark).astype(np.float32)
    S["cliff_d"] = (cs - 2.4 + 2.6 * depth_dark + 3.0 * alp).astype(np.float32)   # frost-split rock up high
    cl_k = smoothstep(0.0, 0.30, cliff_f)
    for k in list(S):
        if not k.startswith("cliff_"):
            S[k] = (S[k] - 14.0 * cl_k).astype(np.float32)
    for k in MATERIALS:
        S.setdefault(k, np.full_like(S["duff"], -9.0))
    P.scores = S
    return S


def post(rgb, X, Y, P):
    """Light the range. A mountain is read by its shading, so this does more work than a flat zone's."""
    f = P.fields
    sf = lambda a: P.sample_field(a.astype(np.float32), X, Y)          # noqa: E731
    elev, slope, alp = sf(f["elev"]), sf(f["slope"]), sf(f["alp"])
    lum_n = P.sample_field(P.noise(14.0, "lumlow", octaves=2), X, Y)

    out = rgb * (0.93 + 0.07 * lum_n)[..., None]

    # ALTITUDE LIGHT. Up high the air is thinner and the ground is pale rock and snow; down in the timber
    # it is darker. Kept gentle - this is a tint, not an exposure control.
    lift = smoothstep(0.0, 20.0, elev)
    out = out * (0.95 + 0.17 * lift)[..., None]

    # HILLSHADE, sun from the north-west. The single thing that makes relief legible from above: without
    # it the ridges and the valleys are the same brightness and the map reads flat. Centred on 1.0 so it
    # LIGHTS the map rather than dimming it, and driven by the tile-scale gradient computed in
    # build_scores - see the note there about the unit mismatch that made this halve the whole zone.
    gxs, gys = sf(f["dzdx"]), sf(f["dzdy"])
    # + NOT -. This read 1 + k * (-dzdx - dzdy), which brightens the slopes that face SOUTH-EAST:
    # the comment said north-west and the arithmetic said the opposite. Lit from below-right, a
    # ridge reads as a trench - the same fault that made Southern Needles' mesas look like craters
    # (found there 13 Nov 2026). A slope that FACES the north-west rises toward the south-east,
    # so its gradient is positive in both axes.
    # WEST of north-west: the range runs east-west and falls away to the south, so a sun square in
    # the north-west puts the whole alpine face in shade. Mostly from the west, the ridges still
    # light on one side and the high ground stays in the sun.
    shade = np.clip(1.0 + 0.95 * (gxs * 0.92 + gys * 0.30), 0.70, 1.42)
    out = out * shade[..., None]

    # GOLDEN SUN, BLUE SHADE. Kyle, 13 Nov: "that golden snow and sun alpine mountain feel" - and
    # this is the Rockies, which is his home. The light was white and the high ground was tinted
    # cold, so the summits read as overcast. Now a slope facing the sun is warmed toward gold and
    # one turned away is cooled toward blue: late-afternoon light, which is what puts gold on snow.
    sun = np.clip((shade - 1.0) / 0.42, 0.0, 1.0)[..., None]
    dark = np.clip((1.0 - shade) / 0.30, 0.0, 1.0)[..., None]
    out = out * (1.0 + sun * np.array([0.12, 0.05, -0.12], np.float32))
    out = out * (1.0 + dark * np.array([-0.07, -0.02, 0.09], np.float32))

    # SNOW ON THE ROCK. The alpine band is cliff, and no ground material can win on a cliff - so
    # the snow score above could never put snow where the eye wants it most, on the high face.
    # Laid here instead, over whatever rock is there: ledges and gullies of it across the alpine,
    # thicker with height, lit gold where the sun is on it and blue where it is not.
    snow_n = P.sample_field(P.noise(3.2, "snowface", octaves=3), X, Y)
    # ON THE ROCK ONLY (cf > 0): the first pass snowed over the tarn and the road up to the pass.
    snow = (np.clip(alp, 0, 1) * smoothstep(0.55, 0.69, snow_n + 0.10 * smoothstep(10.0, 24.0, elev))
            * smoothstep(17.0, 25.0, Y / float(TILE_PX))
            * smoothstep(0.0, 0.08, sf(f["cf"])) * (1.0 - smoothstep(-0.5, 0.4, sf(f["water"]))))[..., None]
    snow_rgb = np.array([246.0, 244.0, 238.0], np.float32) * (0.80 + 0.20 * shade[..., None])
    snow_rgb = snow_rgb * (1.0 + sun * np.array([0.02, -0.02, -0.14], np.float32))
    snow_rgb = snow_rgb * (1.0 + dark * np.array([-0.10, -0.04, 0.06], np.float32))
    out = out * (1.0 - 0.88 * snow) + snow_rgb * 0.88 * snow

    # Warm the timber; leave the high ground to the sun and the shade above rather than cooling
    # all of it.
    cool = np.clip(alp, 0, 1)[..., None]
    out = out * ((1 - cool) * np.array([1.05, 1.02, 0.94], np.float32)
                 + cool * np.array([1.03, 1.01, 0.98], np.float32))

    wd = sf(f["water"])
    depth = smoothstep(0.4, 4.0, wd)
    out = out * (1 - 0.30 * depth[..., None]) + np.array([30.0, 62.0, 84.0], np.float32) * 0.36 * depth[..., None]

    cf = sf(f["cf"])
    lip = smoothstep(0.0, 0.03, cf) * (1 - smoothstep(0.03, 0.14, cf))
    out = out + 14 * lip[..., None] * np.array([0.92, 0.90, 0.84], np.float32)
    return np.clip(out, 0, 255)


def bake(key, preview=None, sc=4):
    M = importlib.import_module(ZONES[key])
    P = Painter(M.W, M.H, TEX_DIR, seed=getattr(M, "SEED", 541))
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
