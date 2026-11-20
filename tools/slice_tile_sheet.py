#!/usr/bin/env python3
"""Slice a ground-TILE sheet into seamless 256x256 textures.

    python3 tools/slice_tile_sheet.py aspen
    python3 tools/slice_tile_sheet.py aspen --preview /tmp/aspen_tiles.png

WHY THIS FILE EXISTS. The Underdark's 48 tiles were sliced with a throwaway script that never got
committed (commit 3db1a14 added the sheet and the building slicer, but nothing that cuts tiles). The
next sheet therefore had nothing to run, and the knowledge of how it was done lived only in a chat log.
This is that script, written down.

TILES ARE NOT SPRITES, AND THE DIFFERENCE IS THE WHOLE JOB:

  * NO MAGENTA KEY. A tile is opaque ground that runs flush to its own edges. Keying it would eat the
    darkest pixels of a charred-earth texture and leave holes in the floor.
  * CUT ON ARITHMETIC CELLS, not connected blobs. The building slicer finds sprites as blobs because a
    building floats on magenta with space around it; a tile has no silhouette to find - it fills its cell
    edge to edge, and its neighbours are touching it.
  * INSET BEFORE RESIZE. Generated sheets never land on a perfect pixel grid, so a cell cut at its exact
    arithmetic bounds picks up a sliver of the tile next door along one edge. That sliver is invisible in
    the sheet and screams once the texture tiles. Every cell is cropped a few pixels inside its bounds.
  * SEAMLESS EDGES. Each tile is then edge-blended with itself so it repeats without a visible grid. This
    is the step that turns a photo of ground into a texture.

ROWS DRIFT. Image generators do not divide 1024 by 6 evenly, and a sheet whose rows creep by a few pixels
will slice fine at the top and badly at the bottom. A set may therefore declare explicit row boundaries
instead of even division - see ROWS_Y in the set definitions.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT_PX = 256          # every tile ships at 256x256, matching the Underdark set
INSET = 4             # pixels trimmed off each cell edge before resizing (see docstring)
BLEND = 22            # width of the seamless edge blend, in output pixels

SETS = {}


def _set(key, cols, rows, sheet, out_dir, names, rows_y=None, drop=(), gutters=False, seam="blend", out_px=OUT_PX):
    """names: whitespace-separated, cols*rows of them. `drop` names are sliced past but not written.
    gutters: the tiles sit apart on magenta, so each one's edges are found rather than divided out."""
    names = names.split()
    assert len(names) == cols * rows, (key, len(names), cols * rows)
    SETS[key] = dict(cols=cols, rows=rows, sheet=sheet, out=out_dir, names=names,
                     rows_y=rows_y, drop=set(drop), gutters=gutters, seam=seam, out_px=out_px)


def _gutter_runs(sheet, axis, want):
    """The spans of a sheet, along one axis, that are mostly tile rather than magenta gutter."""
    a = np.asarray(sheet, dtype=np.int16)
    mag = (a[:, :, 0] > 200) & (a[:, :, 1] < 80) & (a[:, :, 2] > 200)
    filled = (~mag).mean(axis=axis) > 0.5
    runs, start = [], None
    for i, f in enumerate(filled):
        if f and start is None:
            start = i
        elif not f and start is not None:
            runs.append((start, i))
            start = None
    if start is not None:
        runs.append((start, len(filled)))
    runs = [r for r in runs if r[1] - r[0] > 40]
    assert len(runs) == want, f"expected {want} tile spans between the gutters, found {len(runs)}: {runs}"
    return runs


# ---------------------------------------------------------------------------------------------------------
# THE ASPEN WILDERNESS (Northern Thousand Needles). 8x6 = 48 cells.
#
# Kyle, 2026-10-27, on the first generated sheet: "its fine but don't use the modern road." The bottom row
# came back with asphalt, a lane marking and a concrete slab on it. Those three are DROPPED rather than
# sliced-and-ignored: nothing from Earth appears in the world yet, and leaving dead assets in the repo
# fights the standing cleanup rule. The row's remaining five - red dust, dry red grass, the hard line where
# red dust meets leaf duff, and the gravels - are Azerothian ground and the seam, so they stay.
# ---------------------------------------------------------------------------------------------------------
_set("aspen", 8, 6, "tools/tile_sheets/aspen_tiles.png", "assets/tiles/aspen/materials", """
    asp_duff_gold asp_duff_brown asp_dirt_path asp_grass_duff asp_log_litter asp_mossy_roots asp_fern_floor asp_needle_dark
    asp_needle_mat asp_needle_cones asp_dry_dirt asp_deadfall asp_shade_dirt asp_root_cracked asp_char_ground asp_ash_patch
    asp_grass_summer asp_grass_seed asp_wildflower asp_fireweed asp_turf_grazed asp_grass_matted asp_grass_dry asp_dirt_grazed
    asp_creek_gravel asp_creek_bed asp_pond_shallow asp_pond_deep asp_mud_bank asp_reed_shallows asp_wet_stone asp_pond_ice
    asp_granite asp_granite_lichen asp_scree asp_talus asp_snow_patch asp_snow_packed asp_bedrock asp_stone_frost
    _drop_asphalt _drop_asphalt_line asp_gravel_shoulder _drop_concrete asp_red_dust asp_red_grass asp_seam_line asp_grey_gravel
""", rows_y=[0, 192, 368, 537, 698, 857, 1024],
   drop=("_drop_asphalt", "_drop_asphalt_line", "_drop_concrete"))
#: Measured off the sheet, not divided. Row heights come out 192/176/169/161/159/167 where an even split
#: would be a flat 171 - the first row is 21px taller than the last. Cutting this one evenly lines up at
#: the top and walks progressively further into the wrong row on the way down, which is exactly the drift
#: the module docstring warns about and is invisible until a texture tiles.


# ---------------------------------------------------------------------------------------------------------
# SOUTHERN THOUSAND NEEDLES. 8x6 = 48 cells, one dropped.
#
# Mesa country, plus the tail of the aspen overlay along its northern edge (row 5) and Freewind's own
# settlement ground (row 6). Row 5 is the REVERSE of the Aspen Wilderness's seam: up there Barrens dust
# meets leaf mould, down here leaf mould meets red stone.
#
# DROPPED: row 6 column 7 came back as a hide-drying rack seen from above - a prop, not a ground texture.
# It would tile as a repeating rack. The drying rack already exists as a real prop on the prop sheet
# (sn_drying_rack), so nothing is lost and a dead asset is not left in the repo.
#
# KEPT WITH A WARNING: sn_undercut (row 2, column 4) is a shadowed overhang and reads as a scene. It is
# fine as a sparse accent under a rim and wrong as a field material - the baker must not score it broadly.
# ---------------------------------------------------------------------------------------------------------
_set("southern_needles", 8, 6, "tools/tile_sheets/southern_needles_tiles.png",
     "assets/tiles/southern_needles/materials", """
    sn_hardpan sn_dust_pebbles sn_cracked_clay sn_dry_grass sn_sandstone_pale sn_lichen_orange sn_gravel_scatter sn_packed_path
    sn_layered_stone sn_iron_banded sn_crumbling_rim sn_undercut sn_scree sn_rubble_base sn_stone_cracks sn_polished_shelf
    sn_red_sand sn_rippled_sand sn_wash_gravel sn_salt_crust sn_dry_mud sn_dust_drift sn_hoof_churned sn_desert_scrub
    sn_pool_shallow sn_pool_deep sn_wet_sand sn_reed_bed sn_damp_soil sn_spring_grass sn_mossy_stone sn_salt_rime
    sn_duff_on_red sn_seam_line sn_needle_sand sn_grass_dirt_mix sn_pine_duff sn_root_cracked sn_shaded_red sn_leaves_sandstone
    sn_camp_dirt sn_straw sn_plank_deck sn_boardwalk sn_rope_matting sn_firepit_ash _drop_drying_stakes sn_stone_terrace
""", rows_y=[0, 182, 351, 511, 680, 846, 1024], drop=("_drop_drying_stakes",))
#: Measured off the sheet, not divided. Rows come out 182/169/160/169/166/178 where an even split would be
#: a flat 171 - the first row is 22px taller than the third. Columns ARE even to within a pixel, so only
#: the rows need declaring. Same drift the aspen sheet had; see the module docstring.


def make_seamless(im, blend=BLEND):
    """Cross-fade opposite edges so the texture repeats without a seam.

    Mirrors the strip from the far edge over the near one under a linear ramp. Done on both axes. The
    middle of the tile is untouched, so detail survives; only the outer `blend` pixels are mixed.
    """
    a = np.asarray(im, dtype=np.float32)
    h, w = a.shape[:2]
    b = min(blend, h // 4, w // 4)
    if b < 2:
        return Image.fromarray(a.astype(np.uint8))
    ramp = np.linspace(0.0, 1.0, b, dtype=np.float32)[:, None, None]
    # vertical: blend the top rows with the mirrored bottom rows
    top, bot = a[:b].copy(), a[-b:].copy()
    a[:b] = top * ramp + bot[::-1] * (1 - ramp)
    ramp_h = ramp.transpose(1, 0, 2)
    left, right = a[:, :b].copy(), a[:, -b:].copy()
    a[:, :b] = left * ramp_h + right[:, ::-1] * (1 - ramp_h)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def _noise2(h, w, rng, freqs=(3, 6, 11)):
    """Smooth zero-mean, unit-ish noise of shape (h, w)."""
    n = np.zeros((h, w), dtype=np.float32)
    for f in freqs:
        g = rng.random((f, f)).astype(np.float32)
        n += np.asarray(Image.fromarray(g).resize((w, h), Image.BICUBIC), dtype=np.float32) / f
    return (n - n.mean()) / (n.std() + 1e-6)


def make_seamless_overlap(im, frac=0.22, seed=0):
    """Seamless by overlap, for painted tiles whose content runs in bands (reeds, a meadow) where an edge
    cross-fade leaves a visible straight seam.

    Cut the tile short by B = frac of its size on each axis, and cross-fade its first B rows with the B rows
    that come after the cut. Those rows are the painting's own continuation, so the result wraps with no
    mirroring: the last row kept runs straight into the first. The cross-fade's boundary is warped by noise,
    so it is a ragged blend and never a line. Returns a smaller square; the caller resizes it."""
    rng = np.random.default_rng(seed)
    a = np.asarray(im, dtype=np.float32)
    for axis in (0, 1):
        if axis == 1:
            a = a.transpose(1, 0, 2)
        h, w = a.shape[:2]
        B = max(4, int(h * frac))
        n = h - B
        y = np.arange(B, dtype=np.float32)[:, None] / (B - 1)               # 0 at the top, 1 at row B-1
        warp = 0.35 * _noise2(1, w, rng, (4, 9))[0][None, :]               # where along x the fade sits
        t = np.clip((y - 0.5 - warp * 0.5) / 0.5 + 0.5, 0.0, 1.0)
        t = t * t * (3 - 2 * t)                                             # smoothstep
        head = a[:B] * t[:, :, None] + a[n:n + B] * (1 - t[:, :, None])   # row 0 is the continuation of row n-1
        a = np.concatenate([head, a[B:n]], axis=0)
        if axis == 1:
            a = a.transpose(1, 0, 2)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def slice_set(key, preview=None):
    s = SETS[key]
    sheet = Image.open(ROOT / s["sheet"]).convert("RGB")   # RGB, never RGBA: tiles are opaque ground
    W, H = sheet.size
    cols, rows = s["cols"], s["rows"]
    ys = s["rows_y"] or [round(i * H / rows) for i in range(rows + 1)]
    assert len(ys) == rows + 1, (key, len(ys))
    out_dir = ROOT / s["out"]
    out_dir.mkdir(parents=True, exist_ok=True)

    if s.get("gutters"):
        xr, yr = _gutter_runs(sheet, 0, cols), _gutter_runs(sheet, 1, rows)
    written, dropped = [], []
    for r in range(rows):
        for c in range(cols):
            name = s["names"][r * cols + c]
            if s.get("gutters"):
                (x0, x1), (y0, y1) = xr[c], yr[r]
            else:
                x0, x1 = round(c * W / cols), round((c + 1) * W / cols)
                y0, y1 = ys[r], ys[r + 1]
            if name in s["drop"]:
                dropped.append(name)
                continue
            # Inset before resizing - see the module docstring on why the arithmetic bounds are not safe.
            cell = sheet.crop((x0 + INSET, y0 + INSET, x1 - INSET, y1 - INSET))
            if s.get("seam") == "overlap":
                cell = make_seamless_overlap(cell, seed=r * cols + c).resize((s["out_px"], s["out_px"]), Image.LANCZOS)
                cell.save(out_dir / f"{name}.png")
            else:
                cell = cell.resize((s["out_px"], s["out_px"]), Image.LANCZOS)
                make_seamless(cell).save(out_dir / f"{name}.png")
            written.append(name)

    print(f"{key}: {len(written)} tiles -> {s['out']}")
    if dropped:
        print(f"  dropped on purpose: {', '.join(dropped)}")
    if preview:
        pv = Image.new("RGB", (cols * 128, rows * 128), (20, 20, 24))
        for i, name in enumerate(s["names"]):
            if name in s["drop"]:
                continue
            t = Image.open(out_dir / f"{name}.png").resize((128, 128), Image.LANCZOS)
            pv.paste(t, ((i % cols) * 128, (i // cols) * 128))
        pv.save(preview)
        print("  preview", preview)
    return written


# ---------------------------------------------------------------------------------------------------------
# THE SHIMMERING FLATS + TANARIS. 8x6 = 48 cells, one sheet feeding two zones.
#
# One sheet because the two zones share a border and half a palette: the Flats' salt gives out into
# Tanaris' sand, and generating them separately would have produced two sets that do not meet. The Drowning
# Floor already does this the other way round - it paints from the Southern Needles set because the cave is
# the inside of the same rock - so Tanaris borrowing from this directory is the established pattern rather
# than a shortcut.
#
# ROW HEIGHTS WERE MEASURED, AND CAME BACK EVEN: 180/181/181/181/181/182 against an even split of 181, and
# the columns the same. That is worth recording precisely BECAUSE the aspen sheet did not - it came back
# 192/176/169/161/159/167, where cutting evenly walks progressively into the wrong row down the image. The
# check is cheap and the failure is silent, so it gets run every time rather than assumed either way.
# ---------------------------------------------------------------------------------------------------------
_set("shimmering_flats", 8, 6, "tools/tile_sheets/shimmering_flats_tiles.png",
     "assets/tiles/shimmering_flats/materials", """
    sf_salt_white sf_salt_polygon sf_salt_plates sf_salt_clay sf_salt_thin_mud sf_salt_ripple sf_salt_dark sf_salt_glazed
    sf_mud_curled sf_clay_saltrim sf_dust_hardpan sf_salt_gravel sf_track_rut sf_stones_salt sf_alkali_yellow sf_hardpan_swept
    sf_chitin_plate sf_resin_poured sf_tunnel_spoil sf_crust_shattered sf_hive_floor sf_resin_grit sf_carapace_shards sf_hive_film
    tan_sand_gold tan_dune_ripple tan_sand_pebble tan_hardpan_orange tan_wadi_gravel tan_sandstone_floor tan_dust_drift tan_scrub_sand
    tan_paving_carved tan_flagstone_buried tan_rubble_sandstone tan_basalt_grit tan_deck_oiled tan_plank_bleached tan_harbour_dirt tan_quay_tarred
    cen_limestone_wet cen_limestone_moss cen_water_shallow cen_water_deep cen_leaf_litter cen_ferns cen_roots_stone cen_grass_sunlit
""")


# ---------------------------------------------------------------------------------------------------------
# THE PLAGUELANDS (docs/plaguelands_art_prompts.md sheet 1, Kyle 16 Nov 2026). 8x6 = 48 seamless cells.
_set("plaguelands", 8, 6, "tools/tile_sheets/plaguelands_ground.png", "assets/tiles/plaguelands/ground", """
    pl_wpl_grass pl_wpl_grass_trod pl_wheat_stubble pl_farm_earth pl_grass_violet pl_cart_ruts pl_dead_clover pl_grass_ash
    pl_epl_grass pl_ash_soil pl_green_puddles pl_grey_moss pl_seep_cracks pl_bone_dirt pl_plaguewood_floor pl_terrordale_dust
    pl_scourge_slab pl_scourge_cracked pl_ziggurat_step pl_necro_grate pl_plague_slime pl_blight_mud pl_corpse_pit pl_rune_circle
    pl_cobble_road pl_cobble_weeds pl_dirt_road pl_andorhal_paving pl_mossy_flag pl_lightshope_stone pl_bulwark_earth pl_sorrow_gravel
    pl_scarlet_flag pl_cathedral_runner pl_monastery_floor pl_hearthglen_cobble pl_keep_floor pl_uther_marble pl_paleflame_stone pl_scorched_stone
    pl_lake_water pl_lake_shallow pl_plague_water pl_black_pond pl_grey_shore pl_pebble_beach pl_cold_sea pl_reed_marsh""")

# THE PLAGUELANDS' DUNGEONS (sheet 5, Kyle 16 Nov 2026): the Monastery, Scholomance, Stratholme's two sides,
# Hearthglen's town and Mardenholde Keep. 6x6 seamless cells.
_set("plaguelands_dungeon", 6, 6, "tools/tile_sheets/plaguelands_dungeon_ground.png",
     "assets/tiles/plaguelands/dungeon_ground", """
    sm_crypt sm_parquet sm_armory sm_nave sm_carpet sm_wall
    scholo_flag scholo_ritual scholo_crypt scholo_marble scholo_wall scholo_ossuary
    strat_burned_cobble strat_bastion strat_market strat_charred_wood strat_wall strat_ash
    strat_scourge_street strat_ziggurat strat_slaughter strat_grate strat_frost strat_baron_hall
    hg_cobble hg_square hg_gravel hg_chapel hg_barracks hg_mosaic
    mh_flag mh_throne_carpet mh_wall mh_kennel mh_library mh_burned""")

# STONETALON (docs/stonetalon_art_prompts.md sheet 1, Kyle 15 Nov 2026). 8x6 = 48 cells: the redwood vale,
# the sequoia slopes, the Blowdown, the volcano, Sun Rock / the Grimtotem / the Mulgore Rim, and the inside of
# the great sequoia. Rows MEASURED: 181/165/164/162/163/189 (the first and last run tall); columns even at 192.
# ---------------------------------------------------------------------------------------------------------
_set("stonetalon", 8, 6, "tools/tile_sheets/stonetalon_tiles.png", "assets/tiles/stonetalon/materials", """
    st_redwood_duff st_redwood_sorrel st_sword_ferns st_wet_moss st_fog_duff st_mossy_roots st_bark_litter st_creek_gravel
    st_sequoia_litter st_needle_cones st_meadow_grass st_granite_lichen st_dry_duff st_trail st_trail_edge st_granite_cliff
    st_ash_plain st_ash_fireweed st_ash_splinters st_pumice_gravel st_mudflow st_ash_dunes st_ash_gully st_ash_path
    st_basalt st_scoria st_sulphur st_steaming_ground st_obsidian st_basalt_cliff st_crater_deep st_crater_shallow
    st_sandstone st_tauren_plaza st_camp_earth st_sandstone_cliff st_grimtotem_earth st_dead_grass st_dark_seep st_void_ground
    st_heartwood_floor st_ring_wall st_inner_bark_wall st_sap_pool st_beetle_galleries st_branch_walk st_canopy_floor st_sky_below
""", rows_y=[0, 181, 346, 510, 672, 835, 1024])

# Kyle's sheet 9 (17 Nov 2026), docs/plaguelands_secrets_art_prompts.md: tundra and ice, fen and barrows, an
# elven waystation and a Scourge breach. Painted for the Plaguelands' hidden maps and kept general (cl_ =
# cold lands) because Winterspring will want the same snow and ice. Tiles sit apart on magenta gutters.
_set("cold_lands", 6, 6, "tools/tile_sheets/cold_lands_tiles.png", "assets/tiles/cold_lands/ground", """
    cl_snow_wind cl_snow_steppe cl_glacier_ice cl_river_ice cl_stone_frost cl_snow_trampled
    cl_icehole_water cl_scree_snow cl_glacier_wall cl_moraine cl_lichen_rock_snow cl_ochre_snow
    cl_sphagnum cl_floating_moss cl_peat_water cl_reed_bed cl_causeway_stones cl_fen_shallow
    cl_mere_deep cl_amani_paving cl_barrow_turf cl_drowned_grass cl_mud_bank cl_wet_sand
    cl_elven_paving cl_golden_meadow cl_silver_grass cl_fallen_leaves cl_elven_road cl_reflecting_pool
    cl_gold_to_grey cl_scourge_cracks cl_elven_paving_broken cl_plague_grass cl_bone_soil cl_burned_leaves
""", gutters=True, seam="overlap")


# AZSHARA (docs/azshara_art_prompts.md sheet 1, Kyle 17 Nov 2026). 8x6 = 48 cells on a 1254x1254 sheet, so the
# cells are taller than wide and are resized square. It came from the first version of the prompt, so cell 16 is a
# snow-dusted rock and cell 40 a kelp-tangled floor (the rewrite asks for two walls there). Rows MEASURED (Kyle spotted
# bad crops): 209/209/209/190/195/242, so even division put a strip of row 4 across the top of row 5 and a strip of
# drowned marble across the top of the water. Columns are even.
_set("azshara", 8, 6, "tools/tile_sheets/azshara_ground.png", "assets/tiles/azshara/ground", """
    az_leaf_floor az_leaf_gold az_grass_gold az_grass_trod az_loam az_crimson_brush az_needle_leaf az_moss_shroom
    az_rock_hill az_scree az_lichen_stone az_mountain_grass az_trail az_furbolg_path az_honey_clay az_snow_rock
    az_cursed_soil az_scorched az_felrot_soil az_dig_earth az_plank_walk az_dig_sand az_leyline_grass az_crystal_glass
    az_highborne_paving az_paving_leaves az_moon_mosaic az_mossy_flag az_marble_road az_marble_terrace az_violet_tile az_plaza_slab
    az_wet_marble az_barnacle_marble az_drowned_mosaic az_coral_stone az_seaweed_marble az_shell_silt az_tidepool_rock az_kelp_floor
    az_sea_deep az_sea_shallow az_drowned_shallows az_lake_water az_wet_sand az_shell_beach az_storm_surf az_arcane_water
""", rows_y=[0, 209, 418, 627, 817, 1012, 1254])


# DEADWIND PASS (docs/deadwind_art_prompts.md sheets 1 and 6, Kyle 18 Nov 2026). Both came back smaller than asked
# (1536x1024 and 1448x1086). The dungeon sheet is an even 8x6 grid. The ground sheet's columns are even but its
# rows are not: measured on the seams, they fall at 187/365/512/662/835 against an even 171/341/512/683/853, and
# cutting evenly left a strip of the next row along the top or bottom of most tiles.
_set("deadwind", 8, 6, "tools/building_sheets/deadwind_ground.png", "assets/tiles/deadwind/ground", """
    dw_dead_floor dw_ash_floor dw_dead_grass dw_root_soil dw_mould_litter dw_dead_needles dw_cracked_earth dw_mud_path
    dw_black_rock dw_scree dw_gorge_floor dw_rock_wall dw_broken_cobble dw_cart_ruts dw_grave_earth dw_grave_flags
    dw_seep_cracks dw_glow_ash dw_slag_crust dw_stain_rings dw_ooze_mud dw_pustule_ground dw_rust_sludge dw_flesh_mat
    dw_flesh_growth dw_black_veins dw_bruise_mould dw_bone_crust dw_sick_moss dw_glow_roots dw_web_floor dw_egg_floor
    dw_shattered_time dw_aged_dust dw_stopped_water dw_rift_rock dw_echo_prints dw_black_glass dw_forsaken_path dw_camp_mud
    dw_black_pond dw_toxic_water dw_brackish dw_dead_streambed dw_rust_water dw_cave_floor dw_cave_seep dw_cave_wall
""", rows_y=[0, 187, 365, 512, 662, 835, 1024])
_set("deadwind_dungeon", 8, 6, "tools/building_sheets/deadwind_dungeon_tiles.png", "assets/tiles/fallout_zone", """
    fz_gouged_rock fz_gravel fz_seep_rock fz_ash_earth fz_scorched_rock fz_rubble fz_rock_wall fz_seep_wall
    fz_slag fz_stain_rings fz_ooze_stone fz_deep_ash fz_corroded fz_crystal_floor fz_slag_wall fz_ooze_pool
    fz_flesh fz_flesh_stone fz_bone_mat fz_root_flesh fz_blisters fz_sinew fz_flesh_wall fz_bone_wall
    fz_shattered fz_black_glass fz_echo_stone fz_stopped_water fz_aged_dust fz_light_cracks fz_glass_wall fz_stopped_wall
    fz_fused fz_wound_tissue fz_eye_flesh fz_glow_veins fz_tar fz_bone_crystal fz_wound_wall fz_sunk_wall
    fz_toxic_deep fz_toxic_shallow fz_black_water fz_rust_water fz_quiet_stone fz_ash_stone fz_iron_grate fz_tower_flags
""")



# MOONGLADE (docs/moonglade_art_prompts.md sheet 1, Kyle 18 Nov 2026). 1536x1024, columns even, rows measured on the
# seams (182/356/511/668/831): the same uneven rows the Deadwind sheet had.
_set("moonglade", 8, 6, "tools/building_sheets/moonglade_ground.png", "assets/tiles/moonglade/ground", """
    mg_grass mg_grass_long mg_star_flowers mg_wildflowers mg_moss mg_glow_moss mg_clover mg_silver_meadow
    mg_forest_floor mg_fern_floor mg_root_earth mg_petal_carpet mg_garden_loam mg_mushroom_grass mg_dew_litter mg_deep_shade
    mg_footpath mg_moon_flags mg_river_stones mg_pale_stone mg_mountain_rock mg_cliff_wall mg_scree mg_boardwalk
    mg_sand mg_wet_sand mg_pebbles mg_shallows_sand mg_shallows_stone mg_reeds mg_lilies mg_mud_shore
    mg_lake_mid mg_lake_mid_dark mg_lake_deep mg_lake_deepest mg_lake_mirror mg_lake_ripple mg_lake_moonstone mg_moonwell_water
    mg_dream_grass mg_dream_flowers mg_barrow_earth mg_barrow_flags mg_root_floor mg_bramble_earth mg_island_sand mg_black_pool
""", rows_y=[0, 182, 356, 511, 668, 831, 1024])

# FERALAS (docs/feralas_art_prompts.md sheets 1 and 8, Kyle 19 Nov 2026). The ground sheet came back 1536x1024 with
# uneven rows, measured on the seams (180/359/512/666/829); the Zukk'ash Hive's is 1448x1086 and even. The hive's
# tiles keep the wd_ ids and folder the prompts named before the cave was renamed (the Writhing Deep is the
# Plaguelands' spider cave; these are only file names).
_set("feralas", 8, 6, "tools/building_sheets/feralas_ground.png", "assets/tiles/feralas/ground", """
    fe_forest_floor fe_loam_roots fe_lush_grass fe_fern_floor fe_moss fe_leaf_litter fe_mud_trail fe_deep_shade
    fe_redwood_duff fe_swordfern fe_sorrel_moss fe_fog_duff fe_nurse_rot fe_moss_stones fe_needle_path fe_mist_moss
    fe_river_mud fe_marsh_grass fe_river_shallow fe_river_deep fe_reed_water fe_river_gravel fe_stream fe_falls_foam
    fe_beach_sand fe_wet_sand fe_sea_shallow fe_sea_mid fe_sea_deep fe_tide_rock fe_shingle fe_sea_cliff
    fe_granite fe_granite_cliff fe_marble_moss fe_inlay_ruin fe_ogre_dirt fe_gnoll_dirt fe_cave_grit fe_highland_meadow
    fe_dug_earth fe_resin_crust fe_deep_sand fe_blight_grass fe_dream_grass fe_dream_flowers fe_camp_earth fe_elven_paving
""", rows_y=[0, 180, 359, 512, 666, 829, 1024])
_set("zukkash_hive", 8, 6, "tools/building_sheets/feralas_hive_tiles.png", "assets/tiles/feralas/writhing_deep", """
    wd_earth wd_root_earth wd_moss_earth wd_burrow wd_chitin_earth wd_mud wd_root_wall wd_resin_wall
    wd_resin wd_resin_pools wd_egg_floor wd_webbing wd_dug_ridges wd_chitin_floor wd_honeycomb_wall wd_chitin_wall
    wd_old_resin wd_gold_veins wd_egg_shells wd_larval_slime wd_stained_earth wd_bone_floor wd_pillar_wall wd_pit_edge
    wd_water_shallow wd_water_deep wd_resin_water wd_seep wd_wet_stone wd_moss_stone wd_wet_wall wd_scum_water
    wd_tunnel_dug wd_earth_to_sand wd_dark_sand wd_sand_mushrooms wd_sand_blocks wd_claw_tracks wd_gouged_wall wd_sand_wall
    wd_blue_fungus_sand wd_violet_fungus_sand wd_ash_stone wd_cracked_ash wd_fungal_mat wd_resin_chunks wd_fungus_wall wd_buried_wall
""")

# THE SKY (docs/sky_art_prompts.md, written by tools/write_sky_art_prompts.py; Kyle's sheets SK1 and SK2, 19 Nov 2026).
# The names come from the prompt script, so the slice can't drift from what was asked for. Seam rows measured.
def _sky_tile_sets():
    sys.path.insert(0, str(ROOT / "tools"))
    import write_sky_art_prompts as SKY
    rows = {"SK1": [0, 182, 352, 512, 672, 840, 1024], "SK2": [0, 182, 353, 511, 693, 864, 1024],
            "SK17": [0, 180, 362, 543, 724, 905, 1086], "SK17B": [0, 192, 374, 512, 650, 836, 1024]}
    for s in SKY.SHEETS:
        if s["kind"] == "tiles" and s["key"] in rows:
            ids = [i for _t, items in s["rows"] for _x, i in items]
            # SK17 came back as 6 x 6 (36 of the 48 asked for, in order): the last 12 are still to draw
            cols = 6 if s["key"] == "SK17" else 8
            _set(f"sky_{s['key'].lower()}", cols, 6, f"tools/building_sheets/sky_{s['key'].lower()}.png",
                 s["out"].rstrip("/"), " ".join(ids[:cols * 6]), rows_y=rows[s["key"]])
    # BK1, the sky layers: six 512px cells, kept at 512 (they're stretched behind whole screens)
    _set("sky_bk1", 3, 2, "tools/building_sheets/sky_bk1.png", "assets/tiles/sky/backdrop",
         "sky_far_gold sky_far_day sky_far_storm sky_far_dusk sky_far_dawn sky_wisps", out_px=512)


_sky_tile_sets()


# THE WORLD TREE (docs/worldtree_art_prompts.md, Kyle's sheet W1, 19 Nov 2026). Names from the doc's slice table.
def _md_slice_names(doc, sheet_key):
    text = (ROOT / doc).read_text(encoding="utf-8")
    i = text.index(f"## SHEET {sheet_key}:")
    j = text.index("### Slice order", i)
    out = []
    for line in text[j:].splitlines()[3:]:
        if not line.startswith("|") or line.startswith(("|---", "| row")):
            if out:
                break
            continue
        out += [c.strip() for c in line.strip("|").split("|")[1:]]
    return out


_set("worldtree_w1", 8, 6, "tools/building_sheets/worldtree_w1.png", "assets/tiles/worldtree/ground",
     " ".join(_md_slice_names("docs/worldtree_art_prompts.md", "W1")), rows_y=[0, 187, 363, 512, 663, 836, 1024])


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    keys = [a for a in sys.argv[1:] if a in SETS] or list(SETS)
    for k in keys:
        slice_set(k, pv)

