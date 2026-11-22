"""
Bake the Ashenvale West painting (forest floor + rivers/lakes/moon water + cliffs + dense-woods canopy + corruption
patches) from seamless materials in assets/tiles/ashenvale/materials/ (the Ashenvale tile sheet, see
claude/ashenvale_tile_prompts.md - the file names are the AV_SHEET stems below).

    python3 tools/bake_ashenvale.py [west|east|felwood_south|felwood_north|stonetalon_east] [--preview out.png] [--scale 4]

Landforms come from tools/handbuilt_ashenvale_west.SPEC.fields() - the SAME analytic functions the tile grid is built
from - plus the tiles that seal_unreachable() turned into canopy / deep water, so painting and collision agree.
Writes assets/tiles/ashenvale/baked_west/ground_<cx>_<cy>.jpg (20x20-tile chunks).

PROVISIONAL TEXTURES: any av_* material that has not been generated yet is synthesised from the old Ashenvale /
corruption / Valley-of-Trials textures (cropped seamless + recoloured).  Drop the real tiles into
assets/tiles/ashenvale/materials/ and re-run: real files always win.
"""
import colorsys
import os
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools.terrain_painter import Painter, smoothstep, TILE_PX, TEX  # noqa: E402

REAL_DIR = ROOT / "assets/tiles/ashenvale/materials"
T = ROOT / "assets/tiles"
AV, AC, HF, VOT = T / "ashenvale", T / "ashenvale_corruption", T / "haunted_forest", T / "vot_cluster"
SIZE = 256

# stem -> (source file, vertical crop offset, (hue, sat, val) or None, speckle or None)
# speckle = ((r,g,b), density, size) scatters flower / pebble dots over the texture.
AV_SHEET = {
    # living forest
    "av_forest_floor":   (AV / "forest_floor_dense.png", 0.5, None, None),
    "av_forest_grass":   (AV / "forest_floor_light.png", 0.5, (92, 0.75, 1.05), None),
    "av_fern_floor":     (AV / "forest_floor_light.png", 0.2, (112, 0.80, 0.78), None),
    "av_root_earth":     (AV / "forest_floor_roots.png", 0.5, (40, 0.50, 0.70), None),
    "av_needle_mulch":   (AV / "forest_floor_roots.png", 0.15, (14, 0.40, 0.78), None),
    "av_bluebell":       (AV / "forest_floor_light.png", 0.8, (100, 0.70, 0.92), ((120, 120, 235), 0.012, 3)),
    "av_road_centre":    (VOT / "vot_road_ruts_a.png", 0.5, (30, 0.42, 0.80), None),
    "av_road_edge":      (VOT / "vot_road_ruts_b.png", 0.5, (40, 0.36, 0.72), None),
    "av_elven_paving":   (VOT / "vot_limestone.png", 0.5, (205, 0.10, 0.92), None),
    "av_mossy_cobble":   (VOT / "vot_limestone.png", 0.2, (95, 0.28, 0.62), None),
    "av_rocky_ground":   (AV / "rocky_forest_ground.png", 0.5, None, None),
    "av_stream_bed":     (VOT / "vot_gravel.png", 0.5, (85, 0.14, 0.70), None),
    "av_lake_mud":       (AV / "forest_floor_roots.png", 0.85, (36, 0.45, 0.58), None),
    "av_lake_shallow":   (AV / "lake_water.png", 0.5, (178, 0.62, 1.55), None),
    "av_lake_deep":      (AV / "lake_water.png", 0.2, (190, 0.80, 0.80), None),
    "av_moon_water":     (AV / "moonwell_water.png", 0.5, (205, 0.52, 1.18), None),
    "av_moon_deep":      (REAL_DIR / "av_moon_water.png", 0.2, (222, 0.70, 0.66), None),
    # water / cliff / coast
    "av_moon_rim":       (AV / "moonwell_rim.png", 0.5, (200, 0.10, 1.35), None),
    "av_cliff_a":        (VOT / "vot_cliff_a.png", 0.5, (262, 0.14, 0.95), None),
    "av_cliff_b":        (VOT / "vot_cliff_b.png", 0.5, (268, 0.16, 0.82), None),
    "av_canopy":         (REAL_DIR / "av_fern_floor.png", 0.35, (112, 0.80, 1.10), "canopy"),
    "av_beach":          (AV / "coastal_sand.png", 0.5, None, None),
    "av_wet_sand":       (AV / "coastal_sand.png", 0.2, (34, 0.55, 0.66), None),
    "av_sea_shallow":    (AV / "shallow_coastal_water.png", 0.5, None, None),
    "av_sea_deep":       (AV / "shallow_coastal_water.png", 0.15, (205, 0.75, 0.50), None),
    # corruption / burned lands
    "av_scorched":       (AC / "scorched_floor.png", 0.5, (30, 0.18, 0.95), None),
    "av_burned_forest":  (HF / "burned_village_ground.png", 0.5, (28, 0.20, 1.75), None),
    "av_fel_earth":      (AV / "corrupted_ground.png", 0.5, None, None),
    "av_corrupt_ground": (AV / "corrupted_ground.png", 0.2, (285, 0.28, 1.15), None),
    "av_satyr_earth":    (AC / "satyr_camp_floor.png", 0.5, None, None),
    "av_plaza_stone":    (VOT / "vot_limestone.png", 0.8, (215, 0.12, 0.98), None),
}

#: North Felwood (Kyle, 14 Nov: "the north is demon wastes"). The living-forest stems are swapped for
#: blighted ones, so the same scores paint dead ground: dark fel-flecked earth for the floor, purple-brown
#: rot for the "grass", bone-strewn scorch where ferns would be, the Twisting Nether showing through
#: where Ashenvale has bluebells, fel water in every lake and river, Hyjal's black rock for cliffs and
#: twisted root-wall for the dead woods.
NORTH_SHEET = {
    "av_forest_floor":   (AC / "fel_pool_bank.png", 0.5, None, None),
    "av_forest_grass":   (AV / "corrupted_ground.png", 0.5, None, None),
    "av_fern_floor":     (AC / "scorched_floor.png", 0.5, (80, 0.10, 0.85), None),
    "av_root_earth":     (AC / "satyr_camp_floor.png", 0.3, (25, 0.30, 0.62), None),
    "av_needle_mulch":   (AC / "scorched_floor.png", 0.2, (30, 0.14, 0.72), None),
    "av_bluebell":       (AC / "void_floor.png", 0.5, None, None),
    "av_road_centre":    (VOT / "vot_road_ruts_a.png", 0.5, (28, 0.30, 0.58), None),
    "av_road_edge":      (VOT / "vot_road_ruts_b.png", 0.5, (32, 0.26, 0.52), None),
    "av_lake_mud":       (AC / "fel_pool_bank.png", 0.2, None, None),
    "av_lake_shallow":   (AC / "fel_pool_water.png", 0.5, None, None),
    "av_lake_deep":      (AC / "fel_pool_water.png", 0.2, (138, 0.80, 0.95), None),
    "av_stream_bed":     (AC / "fel_pool_bank.png", 0.8, (95, 0.35, 0.70), None),
    "av_cliff_a":        (AC / "demon_wastes_wall.png", 0.5, None, None),
    "av_cliff_b":        (AC / "demon_wastes_wall.png", 0.2, (20, 0.20, 0.70), None),
    "av_canopy":         (AC / "corrupted_root_wall.png", 0.5, None, None),
    "av_corrupt_ground": (AV / "corrupted_ground.png", 0.2, (285, 0.30, 0.95), None),
}


#: STONETALON (docs/stonetalon_brief.md). Kyle's Stonetalon tile sheet (docs/stonetalon_art_prompts.md sheet 1,
#: sliced to assets/tiles/stonetalon/materials by tools/slice_tile_sheet.py stonetalon, 15 Nov 2026). Three palettes
#: on the one painter: the East (the blast: grey ash, fireweed through it, splintered wood, pumice; the Rim's dead
#: grass and black ground; the Grimtotem's trampled earth), the West (redwood duff, sorrel, ferns and moss in the
#: vale, the volcano's scoria and steaming ground on the cone, the crater lake), and Sun Rock (red sandstone and
#: the painted tauren plaza).
_STM = T / "stonetalon" / "materials"


def _st(name, off=0.5, rec=None, extra=None):
    return (_STM / f"{name}.png", off, rec, extra)


STONETALON_SHEET = {
    "av_forest_floor":   _st("st_dry_duff"),
    "av_forest_grass":   _st("st_meadow_grass"),
    "av_fern_floor":     _st("st_sword_ferns"),
    "av_root_earth":     _st("st_mossy_roots"),
    "av_needle_mulch":   _st("st_needle_cones"),
    "av_bluebell":       _st("st_ash_fireweed"),
    "av_road_centre":    _st("st_trail"),
    "av_road_edge":      _st("st_trail_edge"),
    "av_elven_paving":   _st("st_camp_earth"),
    "av_mossy_cobble":   _st("st_camp_earth"),
    "av_rocky_ground":   _st("st_pumice_gravel"),
    "av_stream_bed":     _st("st_creek_gravel"),
    "av_lake_mud":       _st("st_mudflow"),
    "av_lake_shallow":   _st("st_crater_shallow", rec=(185, 0.30, 0.85)),
    "av_lake_deep":      _st("st_crater_deep", rec=(200, 0.35, 0.65)),
    "av_cliff_a":        _st("st_granite_cliff"),
    "av_cliff_b":        _st("st_basalt_cliff"),
    "av_canopy":         _st("st_canopy_floor"),
    "av_scorched":       _st("st_ash_splinters"),
    "av_burned_forest":  _st("st_ash_plain"),
    "av_fel_earth":      _st("st_void_ground"),
    "av_corrupt_ground": _st("st_dead_grass"),
    "av_satyr_earth":    _st("st_grimtotem_earth"),
    "av_plaza_stone":    _st("st_tauren_plaza"),
}
STONETALON_WEST_SHEET = dict(STONETALON_SHEET)
STONETALON_WEST_SHEET.update({
    "av_forest_floor":   _st("st_redwood_duff"),
    "av_forest_grass":   _st("st_wet_moss"),
    "av_fern_floor":     _st("st_sword_ferns"),
    "av_root_earth":     _st("st_mossy_roots"),
    "av_needle_mulch":   _st("st_sequoia_litter"),
    "av_bluebell":       _st("st_redwood_sorrel"),
    "av_rocky_ground":   _st("st_granite_lichen"),
    "av_lake_mud":       _st("st_fog_duff"),
    "av_lake_shallow":   _st("st_crater_shallow"),
    "av_lake_deep":      _st("st_crater_deep"),
    "av_scorched":       _st("st_steaming_ground"),
    "av_burned_forest":  _st("st_scoria"),
})
SUN_ROCK_SHEET = dict(STONETALON_SHEET)
SUN_ROCK_SHEET.update({
    "av_forest_floor":   _st("st_meadow_grass"),
    "av_forest_grass":   _st("st_dry_duff"),
    "av_cliff_a":        _st("st_sandstone_cliff"),
    "av_cliff_b":        _st("st_sandstone"),
    "av_elven_paving":   _st("st_camp_earth"),
    "av_rocky_ground":   _st("st_sandstone"),
})
#: THE PLAGUELANDS (docs/plaguelands_design.md). PROVISIONAL: painted from the undead farmland and haunted
#: forest textures already in the library until Kyle's Plaguelands ground sheet (docs/plaguelands_art_prompts.md,
#: sheet 1) is sliced into assets/tiles/plaguelands/ground/, at which point these entries point there instead.
#: Sick olive grass and dead crop rows for the fields, grave dirt and black mud for the blight, burned ground for
#: Andorhal, grey crypt stone for the hubs, and cold grey-blue water for Darrowmere.
UFM, HFM = T / "undead_farmland", T / "haunted_forest"
#: The Plaguelands, painted from Kyle's ground sheet (tools/tile_sheets/plaguelands_ground.png, 16 Nov 2026).
#: West is the golden, sick farmland; East is greyer and wetter, with the Plaguewood's dark floor under its woods.
#: The cliffs stay the Valley of Trials' rock, tinted grey, because the sheet has no cliff face.
PLG = ROOT / "assets/tiles/plaguelands/ground"


def _plague_sheet(east):
    G = PLG
    return {
        # "root" wins about two fifths of the open ground (it rings every wood), so it carries the base grass
        "av_forest_floor":   (G / ("pl_grey_moss.png" if east else "pl_wpl_grass.png"), 0.5, None, None),
        "av_forest_grass":   (G / ("pl_grass_ash.png" if east else "pl_dead_clover.png"), 0.5, None, None),
        "av_fern_floor":     (G / ("pl_seep_cracks.png" if east else "pl_grass_violet.png"), 0.5, None, None),
        "av_root_earth":     (G / ("pl_epl_grass.png" if east else "pl_wpl_grass_trod.png"), 0.5, None, None),
        "av_needle_mulch":   (G / ("pl_bone_dirt.png" if east else "pl_farm_earth.png"), 0.5, None, None),
        "av_bluebell":       (G / ("pl_terrordale_dust.png" if east else "pl_wheat_stubble.png"), 0.5, None, None),
        "av_road_centre":    (G / "pl_dirt_road.png", 0.5, None, None),
        "av_road_edge":      (G / "pl_cart_ruts.png", 0.5, None, None),
        "av_elven_paving":   (G / ("pl_mossy_flag.png" if east else "pl_andorhal_paving.png"), 0.5, None, None),
        "av_mossy_cobble":   (G / "pl_cobble_weeds.png", 0.5, None, None),
        "av_plaza_stone":    (G / ("pl_lightshope_stone.png" if east else "pl_cobble_road.png"), 0.5, None, None),
        "av_rocky_ground":   (G / "pl_sorrow_gravel.png", 0.5, None, None),
        "av_stream_bed":     (G / "pl_pebble_beach.png", 0.5, None, None),
        "av_lake_mud":       (G / ("pl_grey_shore.png" if east else "pl_reed_marsh.png"), 0.5, None, None),
        "av_lake_shallow":   (G / "pl_lake_shallow.png", 0.5, None, None),
        "av_lake_deep":      (G / "pl_lake_water.png", 0.5, None, None),
        "av_cliff_a":        (VOT / "vot_cliff_a.png", 0.5, (36, 0.16, 1.30), None),
        "av_cliff_b":        (VOT / "vot_cliff_b.png", 0.5, (36, 0.18, 1.15), None),
        "av_canopy":         (G / ("pl_plaguewood_floor.png" if east else "pl_grass_ash.png"), 0.5, None, "canopy"),
        "av_corrupt_ground": (G / ("pl_plague_slime.png" if east else "pl_green_puddles.png"), 0.5, None, None),
        "av_burned_forest":  (G / "pl_scorched_stone.png" if east else G / "pl_ash_soil.png", 0.5, None, None),
    }


#: AZSHARA (docs/azshara_brief.md). Kyle's Azshara ground sheet (docs/azshara_art_prompts.md sheet 1, sliced to
#: assets/tiles/azshara/ground by tools/slice_tile_sheet.py azshara, 17 Nov 2026): red and gold leaf floor, gold
#: grass, crimson undergrowth under the woods, Highborne paving for the ruins, shell beach and teal sea on the coast.
#: The sheet has no cliff face, so the cliffs stay Ashenvale's.
_AZ = T / "azshara" / "ground"


def _az(name, off=0.5, rec=None, extra=None):
    return (_AZ / f"{name}.png", off, rec, extra)


AZSHARA_SHEET = {
    "av_forest_floor":   _az("az_leaf_floor"),
    "av_forest_grass":   _az("az_grass_gold"),
    "av_fern_floor":     _az("az_crimson_brush"),
    "av_root_earth":     _az("az_leaf_gold"),
    "av_needle_mulch":   _az("az_needle_leaf"),
    "av_bluebell":       _az("az_moss_shroom"),
    "av_road_centre":    _az("az_trail"),
    "av_road_edge":      _az("az_grass_trod"),
    "av_elven_paving":   _az("az_highborne_paving"),
    "av_mossy_cobble":   _az("az_paving_leaves"),
    "av_plaza_stone":    _az("az_mossy_flag"),       # the white slabs read as a hole in the ground
    "av_rocky_ground":   _az("az_rock_hill"),
    "av_stream_bed":     _az("az_scree"),
    "av_lake_mud":       _az("az_loam"),
    "av_lake_shallow":   _az("az_sea_shallow"),
    "av_lake_deep":      _az("az_lake_water"),
    "av_canopy":         _az("az_crimson_brush", extra="canopy"),
    "av_beach":          _az("az_shell_beach"),
    "av_wet_sand":       _az("az_wet_sand"),
    "av_sea_shallow":    _az("az_drowned_shallows"),
    "av_sea_deep":       _az("az_sea_deep"),
    "av_scorched":       _az("az_scorched"),
    "av_burned_forest":  _az("az_scorched"),
    "av_fel_earth":      _az("az_felrot_soil"),
    "av_corrupt_ground": _az("az_cursed_soil"),
    "av_satyr_earth":    _az("az_cursed_soil"),
}
#: CENTRAL AZSHARA (tools/handbuilt_azshara_central.py): West's autumn floor, plus the leyline grass round the Mennar
#: Font (the bluebell layer), dig earth in the Talrendis crews' trenches at Eldarath (the plaza layer) and arcane water
#: in the Font itself (the moon-pool layers).
AZSHARA_CENTRAL_SHEET = dict(AZSHARA_SHEET)
AZSHARA_CENTRAL_SHEET.update({
    "av_bluebell":       _az("az_leyline_grass"),
    "av_plaza_stone":    _az("az_dig_earth"),
    "av_moon_water":     _az("az_arcane_water"),
    "av_moon_deep":      _az("az_arcane_water", 0.2),
    "av_moon_rim":       _az("az_crystal_glass"),
})
#: EAST AZSHARA (tools/handbuilt_azshara_east.py): the drowned coast. The forest floor stays autumn in the west; the
#: paving is wet and barnacled marble, the plaza layer the drowned mosaic, the bluebell layer coral stone, rocky ground
#: tide-pool rock, and the satyr layer is SHELL SILT washing up from the shore (the module's satyr_field).
AZSHARA_EAST_SHEET = dict(AZSHARA_SHEET)
AZSHARA_EAST_SHEET.update({
    "av_bluebell":       _az("az_coral_stone"),
    "av_elven_paving":   _az("az_wet_marble"),
    "av_mossy_cobble":   _az("az_barnacle_marble"),
    "av_plaza_stone":    _az("az_drowned_mosaic"),
    "av_rocky_ground":   _az("az_tidepool_rock"),
    "av_satyr_earth":    _az("az_shell_silt"),
    "av_lake_mud":       _az("az_wet_sand"),
})
#: TIMBERMAW HOLD (tools/handbuilt_timbermaw_hold.py): the caldera floor. Gold mountain grass and leaf-strewn earth on
#: the terraces, the Timbermaw's trodden paths and honey clay in the middle, lichen-grey rock for the walls and crags.
TIMBERMAW_HOLD_SHEET = dict(AZSHARA_SHEET)
TIMBERMAW_HOLD_SHEET.update({
    "av_forest_floor":   _az("az_leaf_gold"),
    "av_forest_grass":   _az("az_mountain_grass"),
    "av_fern_floor":     _az("az_moss_shroom"),
    "av_root_earth":     _az("az_grass_trod"),
    "av_road_centre":    _az("az_furbolg_path"),
    "av_road_edge":      _az("az_trail"),
    "av_plaza_stone":    _az("az_honey_clay"),
    "av_elven_paving":   _az("az_mossy_flag"),
    "av_rocky_ground":   _az("az_scree"),
    "av_cliff_a":        _az("az_lichen_stone"),
    "av_cliff_b":        _az("az_scree"),           # the deep mountain: grey scree (rock_hill's orange grass read as mush)
    "av_corrupt_ground": _az("az_felrot_soil"),
})
#: DEADWIND PASS (docs/deadwind_brief.md). Kyle's Deadwind ground sheet (docs/deadwind_art_prompts.md sheet 1, sliced to
#: assets/tiles/deadwind/ground, 18 Nov 2026). West is the dead forest: leaf rot and dead grass, grave flags at Morgan's
#: Plot, the seep (the corrupt layer) glowing through cracks along the stream and in the tunnel. East is where time
#: broke: the bluebell layer is shattered time, the moon pools are stopped water, the corrupt layer is slag and the
#: fel layer black glass round the rupture. The cliffs are the sheet's own black rock and rock wall.
_DW = T / "deadwind" / "ground"


def _dw(name, off=0.5, rec=None, extra=None):
    return (_DW / f"{name}.png", off, rec, extra)


DEADWIND_SHEET = {
    "av_forest_floor":   _dw("dw_dead_floor"),
    "av_forest_grass":   _dw("dw_dead_grass"),
    "av_fern_floor":     _dw("dw_mould_litter"),
    "av_root_earth":     _dw("dw_root_soil"),
    "av_needle_mulch":   _dw("dw_dead_needles"),
    "av_bluebell":       _dw("dw_glow_roots"),
    "av_road_centre":    _dw("dw_broken_cobble"),      # the old pass road, cobbled, the dead grass coming up through it
    "av_road_edge":      _dw("dw_cart_ruts"),
    "av_elven_paving":   _dw("dw_grave_flags"),
    "av_mossy_cobble":   _dw("dw_grave_flags"),
    "av_plaza_stone":    _dw("dw_grave_earth"),
    "av_rocky_ground":   _dw("dw_scree"),
    "av_stream_bed":     _dw("dw_dead_streambed"),
    "av_lake_mud":       _dw("dw_ooze_mud"),
    "av_lake_shallow":   _dw("dw_toxic_water"),
    "av_lake_deep":      _dw("dw_black_pond"),
    "av_moon_water":     _dw("dw_stopped_water"),
    "av_moon_deep":      _dw("dw_stopped_water", 0.2),
    "av_moon_rim":       _dw("dw_shattered_time"),
    "av_cliff_a":        _dw("dw_rock_wall"),
    "av_cliff_b":        _dw("dw_black_rock"),
    "av_canopy":         _dw("dw_black_veins"),
    "av_beach":          _dw("dw_cracked_earth"),
    "av_wet_sand":       _dw("dw_brackish"),
    "av_sea_shallow":    _dw("dw_rust_water"),
    "av_sea_deep":       _dw("dw_black_pond"),
    "av_scorched":       _dw("dw_ash_floor"),
    "av_burned_forest":  _dw("dw_glow_ash"),
    "av_fel_earth":      _dw("dw_seep_cracks"),
    "av_corrupt_ground": _dw("dw_pustule_ground"),
    "av_satyr_earth":    _dw("dw_camp_mud"),
}
DEADWIND_EAST_SHEET = dict(DEADWIND_SHEET)
DEADWIND_EAST_SHEET.update({
    "av_forest_floor":   _dw("dw_ash_floor"),
    "av_forest_grass":   _dw("dw_dead_grass"),
    "av_fern_floor":     _dw("dw_aged_dust"),
    "av_needle_mulch":   _dw("dw_echo_prints"),
    "av_bluebell":       _dw("dw_shattered_time"),
    "av_rocky_ground":   _dw("dw_gorge_floor"),
    "av_elven_paving":   _dw("dw_forsaken_path"),
    "av_plaza_stone":    _dw("dw_stain_rings"),
    "av_corrupt_ground": _dw("dw_slag_crust"),
    "av_fel_earth":      _dw("dw_black_glass"),
    "av_burned_forest":  _dw("dw_glow_ash"),
    "av_satyr_earth":    _dw("dw_rift_rock"),
    "av_cliff_b":        _dw("dw_rift_rock"),
})
#: Ariden's Watch (tools/handbuilt_ariden_watch.py): the camp's trodden mud and Forsaken flagstone inside the wire.
ARIDEN_SHEET = dict(DEADWIND_SHEET)
ARIDEN_SHEET.update({
    "av_road_centre":    _dw("dw_forsaken_path"),
    "av_road_edge":      _dw("dw_camp_mud"),
    "av_elven_paving":   _dw("dw_forsaken_path"),
    "av_plaza_stone":    _dw("dw_camp_mud"),
    "av_forest_grass":   _dw("dw_dead_grass"),
})
#: MOONGLADE (tools/handbuilt_moonglade.py, docs/moonglade_brief.md). Kyle's Moonglade ground sheet
#: (docs/moonglade_art_prompts.md sheet 1, sliced to assets/tiles/moonglade/ground, 18 Nov 2026): lush moonlit grass, moss
#: and star-flowers, moonstone flags for Nighthaven's streets, the lake's clear shallows over sand going down to luminous
#: blue, the Dream's grass round the arch (the fel layer), bramble earth at the barrow door (the corrupt layer), the
#: barrow hill's old earth (the satyr layer), the Wakened's garden beds (the scorch layer), fallen petals (burned).
_MG = T / "moonglade" / "ground"


def _mg(name, off=0.5, rec=None, extra=None):
    return (_MG / f"{name}.png", off, rec, extra)


MOONGLADE_SHEET = {
    "av_forest_floor":   _mg("mg_grass"),
    "av_forest_grass":   _mg("mg_grass_long"),
    "av_fern_floor":     _mg("mg_moss"),
    "av_root_earth":     _mg("mg_forest_floor"),
    "av_needle_mulch":   _mg("mg_clover"),
    "av_bluebell":       _mg("mg_star_flowers"),
    "av_road_centre":    _mg("mg_moon_flags"),
    "av_road_edge":      _mg("mg_river_stones"),
    "av_elven_paving":   _mg("mg_pale_stone"),
    "av_mossy_cobble":   _mg("mg_moon_flags"),
    "av_plaza_stone":    _mg("mg_pale_stone"),
    "av_rocky_ground":   _mg("mg_scree"),
    "av_stream_bed":     _mg("mg_pebbles"),
    "av_lake_mud":       _mg("mg_wet_sand"),
    "av_lake_shallow":   _mg("mg_shallows_stone"),
    "av_lake_deep":      _mg("mg_lake_mid"),
    "av_moon_water":     _mg("mg_moonwell_water"),
    "av_moon_deep":      _mg("mg_lake_moonstone"),
    "av_moon_rim":       _mg("mg_pale_stone"),
    "av_cliff_a":        _mg("mg_cliff_wall"),
    "av_cliff_b":        _mg("mg_mountain_rock"),
    "av_canopy":         _mg("mg_fern_floor", extra="canopy"),
    "av_beach":          _mg("mg_sand"),
    "av_wet_sand":       _mg("mg_wet_sand"),
    "av_sea_shallow":    _mg("mg_shallows_stone"),
    "av_sea_deep":       _mg("mg_lake_deep"),
    "av_scorched":       _mg("mg_garden_loam"),
    "av_burned_forest":  _mg("mg_petal_carpet"),
    "av_fel_earth":      _mg("mg_dream_grass"),
    "av_corrupt_ground": _mg("mg_bramble_earth"),
    "av_satyr_earth":    _mg("mg_barrow_earth"),
}
#: FERALAS (docs/feralas_brief.md). Kyle's Feralas ground sheet (docs/feralas_art_prompts.md sheet 1, sliced to
#: assets/tiles/feralas/ground, 19 Nov 2026; until then the maps stood on Ashenvale's and Stonetalon's ground): the giant
#: forest's moss, loam and ferns, the rivers and the Lower Wilds' marsh, granite and the highland meadow (the bluebell
#: layer, its blue and yellow flowers), the Highborne marble at Dire Maul's gate, the Hive Fields' churned earth (the
#: corrupt layer) and the camps' trampled dirt (the satyr layer).
_FE = T / "feralas" / "ground"


def _fe(name, off=0.5, rec=None, extra=None):
    return (_FE / f"{name}.png", off, rec, extra)


FERALAS_SHEET = {
    "av_forest_floor":   _fe("fe_forest_floor"),
    "av_forest_grass":   _fe("fe_lush_grass"),
    "av_fern_floor":     _fe("fe_fern_floor"),
    "av_root_earth":     _fe("fe_loam_roots"),
    "av_needle_mulch":   _fe("fe_leaf_litter"),
    "av_bluebell":       _fe("fe_highland_meadow"),
    "av_road_centre":    _fe("fe_mud_trail"),
    "av_road_edge":      _fe("fe_loam_roots"),
    "av_elven_paving":   _fe("fe_elven_paving"),
    "av_mossy_cobble":   _fe("fe_marble_moss"),
    "av_plaza_stone":    _fe("fe_marble_moss"),
    "av_rocky_ground":   _fe("fe_granite"),
    "av_stream_bed":     _fe("fe_river_gravel"),
    "av_lake_mud":       _fe("fe_river_mud"),
    "av_lake_shallow":   _fe("fe_river_shallow"),
    "av_lake_deep":      _fe("fe_river_deep"),
    "av_moon_water":     _fe("fe_stream"),
    "av_moon_deep":      _fe("fe_river_deep"),
    "av_moon_rim":       _fe("fe_moss_stones"),
    "av_cliff_a":        _fe("fe_granite_cliff"),
    "av_cliff_b":        _fe("fe_granite_cliff", off=0.2),
    "av_canopy":         _fe("fe_fern_floor", extra="canopy"),
    "av_beach":          _fe("fe_river_gravel"),      # inland, a river's shore is gravel and mud, not sand
    "av_wet_sand":       _fe("fe_river_mud"),
    "av_sea_shallow":    _fe("fe_sea_shallow"),
    "av_sea_deep":       _fe("fe_sea_deep"),
    "av_scorched":       _fe("fe_ogre_dirt"),
    "av_burned_forest":  _fe("fe_blight_grass"),
    "av_fel_earth":      _fe("fe_dream_grass"),
    "av_corrupt_ground": _fe("fe_dug_earth"),
    "av_satyr_earth":    _fe("fe_gnoll_dirt"),
}
#: The Forgotten Coast: the same forest, and the Fog Groves (the graft from our world) are the "corrupt" patches: coast
#: redwood duff, with redwood sorrel and moss as the "bluebell" stem there; the trail is a needle path, and the cliffs
#: over the sea are sea cliff.
FERALAS_COAST_SHEET = dict(FERALAS_SHEET)
FERALAS_COAST_SHEET.update({
    "av_beach":          _fe("fe_beach_sand"),
    "av_wet_sand":       _fe("fe_wet_sand"),
    "av_corrupt_ground": _fe("fe_redwood_duff"),
    "av_bluebell":       _fe("fe_sorrel_moss"),
    "av_road_centre":    _fe("fe_needle_path"),
    "av_cliff_b":        _fe("fe_sea_cliff"),
    "av_rocky_ground":   _fe("fe_tide_rock"),
})
#: Camp Mojache's trodden camp earth, and Feathermoon's silver night elf paving (their own maps, tools/bake_ashenvale_towns.py).
FERALAS_MOJACHE_SHEET = dict(FERALAS_SHEET)
FERALAS_MOJACHE_SHEET.update({
    "av_road_centre":    _fe("fe_camp_earth"),
    "av_plaza_stone":    _fe("fe_camp_earth"),
    "av_satyr_earth":    _fe("fe_camp_earth"),
})
FERALAS_FEATHERMOON_SHEET = dict(FERALAS_COAST_SHEET)
FERALAS_FEATHERMOON_SHEET.update({
    "av_road_centre":    _fe("fe_elven_paving"),
    "av_road_edge":      _fe("fe_moss_stones"),
    "av_plaza_stone":    _fe("fe_elven_paving"),
})
#: The Twin Colossals: higher and colder ground under the giants.
FERALAS_NORTH_SHEET = dict(FERALAS_SHEET)
FERALAS_NORTH_SHEET.update({
    "av_needle_mulch":   _fe("fe_moss_stones"),
    "av_forest_grass":   _fe("fe_highland_meadow"),
})
#: THE WORLD TREE (docs/worldtree_brief.md). Kyle's sheet W1 (docs/worldtree_art_prompts.md, sliced to
#: assets/tiles/worldtree/ground, 19 Nov 2026). Rootwater Isle: jungle by the shore, root bark near the trunk (the
#: "corrupt" layer), the rot in the north-east (the "burned" layer), the lagoons, and the trunk itself as the cliff.
_WT = T / "worldtree" / "ground"


def _wt(name, off=0.5, rec=None, extra=None):
    return (_WT / f"{name}.png", off, rec, extra)


ROOTWATER_SHEET = {
    "av_forest_floor":   _wt("wt_jungle_floor"),
    "av_forest_grass":   _wt("wt_jungle_grass"),
    "av_fern_floor":     _wt("wt_root_moss"),
    "av_root_earth":     _wt("wt_root_mud"),
    "av_needle_mulch":   _wt("wt_bark_leaves"),
    "av_bluebell":       _wt("wt_bark_ferns"),
    "av_road_centre":    _wt("wt_root_bark"),
    "av_road_edge":      _wt("wt_root_moss"),
    "av_elven_paving":   _wt("wt_lashed_planks"),
    "av_mossy_cobble":   _wt("wt_lashed_planks"),
    "av_plaza_stone":    _wt("wt_lashed_planks"),
    "av_rocky_ground":   _wt("wt_root_mat"),
    "av_stream_bed":     _wt("wt_root_sand"),
    "av_lake_mud":       _wt("wt_root_sand"),
    "av_lake_shallow":   _wt("wt_lagoon_shallow"),
    "av_lake_deep":      _wt("wt_lagoon_deep"),
    "av_moon_water":     _wt("wt_lagoon_shallow"),
    "av_moon_deep":      _wt("wt_lagoon_deep"),
    "av_moon_rim":       _wt("wt_root_mat"),
    "av_cliff_a":        _wt("wt_trunk_wall"),
    "av_cliff_b":        _wt("wt_trunk_moss_wall"),
    "av_canopy":         _wt("wt_jungle_floor", extra="canopy"),
    "av_beach":          _wt("wt_reef_sand"),
    "av_wet_sand":       _wt("wt_root_sand"),
    "av_sea_shallow":    _wt("wt_lagoon_shallow"),
    "av_sea_deep":       _wt("wt_sea"),
    "av_scorched":       _wt("wt_root_mud"),
    "av_burned_forest":  _wt("wt_rot_bark"),
    "av_fel_earth":      _wt("wt_sap_seep"),
    "av_corrupt_ground": _wt("wt_root_bark"),
    "av_satyr_earth":    _wt("wt_root_mud"),
}
#: The Lower Boughs (Kyle's sheet W1): bark underfoot, the river and rain pools on the Great Bough, the trunk as the north
#: wall, and the drop (the module's sea field) painted as the jungle canopy far below with haze toward the edges.
LOWER_BOUGHS_SHEET = {
    "av_forest_floor":   _wt("wt_bark_moss"),
    "av_forest_grass":   _wt("wt_bark_leaves"),
    "av_fern_floor":     _wt("wt_bark_ferns"),
    "av_root_earth":     _wt("wt_shade_bark"),
    "av_needle_mulch":   _wt("wt_bark_leaves"),
    "av_bluebell":       _wt("wt_bark_ferns"),
    "av_road_centre":    _wt("wt_branch_bark"),
    "av_road_edge":      _wt("wt_dappled_bark"),
    "av_elven_paving":   _wt("wt_lashed_planks"),
    "av_mossy_cobble":   _wt("wt_lashed_planks"),
    "av_plaza_stone":    _wt("wt_lashed_planks"),
    "av_rocky_ground":   _wt("wt_leaf_mat"),
    "av_stream_bed":     _wt("wt_dappled_bark"),
    "av_lake_mud":       _wt("wt_shade_bark"),
    "av_lake_shallow":   _wt("wt_branch_river"),
    "av_lake_deep":      _wt("wt_rain_pool"),
    "av_moon_water":     _wt("wt_rain_pool"),
    "av_moon_deep":      _wt("wt_rain_pool"),
    "av_moon_rim":       _wt("wt_shade_bark"),
    "av_cliff_a":        _wt("wt_trunk_wall"),
    "av_cliff_b":        _wt("wt_trunk_moss_wall"),
    "av_canopy":         _wt("wt_bark_moss", extra="canopy"),
    "av_beach":          _wt("wt_bark_leaves"),
    "av_wet_sand":       _wt("wt_shade_bark"),
    "av_sea_shallow":    _wt("wt_drop_canopy"),
    "av_sea_deep":       _wt("wt_drop_canopy"),
    "av_scorched":       _wt("wt_shade_bark"),
    "av_burned_forest":  _wt("wt_shade_bark"),
    "av_fel_earth":      _wt("wt_sap_seep"),
    "av_corrupt_ground": _wt("wt_dappled_bark"),
    "av_satyr_earth":    _wt("wt_shade_bark"),
}
#: The Middle Boughs (Kyle's sheet W1): lichen bark and moss on the boughs, the rot as the "corrupt" patches with its
#: mushrooms as the "fel" speckle, sap blight as the "burned" ones, harpy litter as the "bluebell" ones, the first
#: climbers' stone as paving, lashed planks on the bridges (the "plaza" layer), the trunk as the west wall, and the drop
#: as mist, the canopy gone below it.
MIDDLE_BOUGHS_SHEET = {
    "av_forest_floor":   _wt("wt_lichen_bark"),
    "av_forest_grass":   _wt("wt_bark_moss"),
    "av_fern_floor":     _wt("wt_lichen_bark"),
    "av_root_earth":     _wt("wt_shade_bark"),
    "av_needle_mulch":   _wt("wt_bark_leaves"),
    "av_bluebell":       _wt("wt_nest_litter"),
    "av_road_centre":    _wt("wt_branch_bark"),
    "av_road_edge":      _wt("wt_carved_bark"),
    "av_elven_paving":   _wt("wt_city_stone"),
    "av_mossy_cobble":   _wt("wt_city_stone"),
    "av_plaza_stone":    _wt("wt_lashed_planks"),
    "av_rocky_ground":   _wt("wt_shade_bark"),
    "av_stream_bed":     _wt("wt_shade_bark"),
    "av_lake_mud":       _wt("wt_shade_bark"),
    "av_lake_shallow":   _wt("wt_rain_pool"),
    "av_lake_deep":      _wt("wt_rain_pool"),
    "av_moon_water":     _wt("wt_rain_pool"),
    "av_moon_deep":      _wt("wt_rain_pool"),
    "av_moon_rim":       _wt("wt_shade_bark"),
    "av_cliff_a":        _wt("wt_trunk_wall"),
    "av_cliff_b":        _wt("wt_trunk_moss_wall"),
    "av_canopy":         _wt("wt_bark_moss", extra="canopy"),
    "av_beach":          _wt("wt_lichen_bark"),
    "av_wet_sand":       _wt("wt_shade_bark"),
    "av_sea_shallow":    _wt("wt_drop_mist"),
    "av_sea_deep":       _wt("wt_drop_mist"),
    "av_scorched":       _wt("wt_sap_seep"),
    "av_burned_forest":  _wt("wt_sap_seep"),
    "av_fel_earth":      _wt("wt_rot_mushrooms"),
    "av_corrupt_ground": _wt("wt_rot_bark"),
    "av_satyr_earth":    _wt("wt_shade_bark"),
}
#: The Upper Boughs (Kyle's sheets W1 and SK): pale wind-scoured bark, lichen, storm-black bark where the lightning
#: struck ("burned"), the wind-stripped tips ("corrupt"), gold where the light first comes down from above ("bluebell"),
#: lashed planks on the skiff's deck and the rope walk ("plaza"), the trunk as the column in the middle, and the drop as
#: the tops of the clouds, close below.
def _sk(name, off=0.5, rec=None, extra=None):
    return (_WT.parent.parent / "sky/ground" / f"{name}.png", off, rec, extra)


UPPER_BOUGHS_SHEET = {
    "av_forest_floor":   _wt("wt_wind_bark"),
    "av_forest_grass":   _wt("wt_lichen_bark"),
    "av_fern_floor":     _wt("wt_wind_bark"),
    "av_root_earth":     _wt("wt_wind_bark"),
    "av_needle_mulch":   _wt("wt_lichen_bark"),
    "av_bluebell":       _sk("sk_gold_leaves"),
    "av_road_centre":    _wt("wt_branch_bark"),
    "av_road_edge":      _wt("wt_carved_bark"),
    "av_elven_paving":   _wt("wt_lashed_planks"),
    "av_mossy_cobble":   _wt("wt_lashed_planks"),
    "av_plaza_stone":    _wt("wt_lashed_planks"),
    "av_rocky_ground":   _wt("wt_lichen_bark"),
    "av_stream_bed":     _wt("wt_wind_bark"),
    "av_lake_mud":       _wt("wt_wind_bark"),
    "av_lake_shallow":   _wt("wt_rain_pool"),
    "av_lake_deep":      _wt("wt_rain_pool"),
    "av_moon_water":     _wt("wt_rain_pool"),
    "av_moon_deep":      _wt("wt_rain_pool"),
    "av_moon_rim":       _wt("wt_wind_bark"),
    "av_cliff_a":        _wt("wt_high_trunk_wall"),
    "av_cliff_b":        _wt("wt_high_trunk_wall"),
    "av_canopy":         _wt("wt_wind_bark", extra="canopy"),
    "av_beach":          _wt("wt_wind_bark"),
    "av_wet_sand":       _wt("wt_lichen_bark"),
    "av_sea_shallow":    _sk("sk_cloud_sun"),
    "av_sea_deep":       _sk("sk_cloud_solid"),
    "av_scorched":       _wt("wt_scorched_bark"),
    "av_burned_forest":  _wt("wt_storm_bark"),
    "av_fel_earth":      _sk("sk_gold_tips"),
    "av_corrupt_ground": _wt("wt_wind_bark"),
    "av_satyr_earth":    _wt("wt_wind_bark"),
}
#: The Cloudbreak (sheets W1 and SK): wind-scoured bark on the last branches, hung with fog low down ("corrupt") and lit
#: gold near the top ("bluebell"), the rope ladders' rungs ("plaza"), the chamber's heartwood floor ("paved"), the old
#: stone wall the mural is painted on (the cliff), and cloud all round, thick enough that the drop doesn't show.
CLOUDBREAK_SHEET = dict(UPPER_BOUGHS_SHEET)
CLOUDBREAK_SHEET.update({
    "av_corrupt_ground": _sk("sk_cloud_moss"),
    "av_fel_earth":      _sk("sk_cloud_moss"),
    "av_bluebell":       _sk("sk_crown_bark"),
    "av_elven_paving":   _wt("wt_heartwood_floor"),
    "av_mossy_cobble":   _wt("wt_heartwood_floor"),
    "av_cliff_a":        _sk("sk_ancient_wall"),
    "av_cliff_b":        _sk("sk_ancient_wall_vines"),
    "av_sea_shallow":    _sk("sk_cloud_solid"),
    "av_sea_deep":       _sk("sk_cloud_solid"),
})
#: The Great Settlement (Kyle's sheet W1, the city row): heartwood floors and market planks on the platforms, the Rise's
#: stone, the Trades' red clay yards, carved bark between the Lantern Ward's homes, the trunk as the north wall, and the
#: hollow inside the tree (the module's sea field) painted as lantern-lit depths with the lower tiers far below.
GREAT_SETTLEMENT_SHEET = {
    "av_forest_floor":   _wt("wt_market_planks"),
    "av_forest_grass":   _wt("wt_heartwood_floor"),
    "av_fern_floor":     _wt("wt_heartwood_floor"),
    "av_root_earth":     _wt("wt_carved_bark"),
    "av_needle_mulch":   _wt("wt_market_planks"),
    "av_bluebell":       _wt("wt_garden_soil"),
    "av_road_centre":    _wt("wt_city_stone"),
    "av_road_edge":      _wt("wt_market_planks"),
    "av_elven_paving":   _wt("wt_city_plaza"),
    "av_mossy_cobble":   _wt("wt_city_stone"),
    "av_plaza_stone":    _wt("wt_city_plaza"),
    "av_rocky_ground":   _wt("wt_lashed_planks"),
    "av_stream_bed":     _wt("wt_city_stone"),
    "av_lake_mud":       _wt("wt_city_stone"),
    "av_lake_shallow":   _wt("wt_city_pool"),
    "av_lake_deep":      _wt("wt_city_pool"),
    "av_moon_water":     _wt("wt_city_pool"),
    "av_moon_deep":      _wt("wt_city_pool"),
    "av_moon_rim":       _wt("wt_city_stone"),
    "av_cliff_a":        _wt("wt_trunk_wall"),
    "av_cliff_b":        _wt("wt_trunk_moss_wall"),
    "av_canopy":         _wt("wt_heartwood_floor", extra="canopy"),
    "av_beach":          _wt("wt_lashed_planks"),
    "av_wet_sand":       _wt("wt_carved_bark"),
    "av_sea_shallow":    _wt("wt_drop_lanterns"),
    "av_sea_deep":       _wt("wt_drop_lanterns"),
    "av_scorched":       _wt("wt_red_clay"),
    "av_burned_forest":  _wt("wt_red_clay"),
    "av_fel_earth":      _wt("wt_sap_seep"),
    "av_corrupt_ground": _wt("wt_carved_bark"),
    "av_satyr_earth":    _wt("wt_carved_bark"),
}
#: The Sunward Crown (Kyle's sheets SK1-SK19): the first sky map. Gold grass and gold moss on the crown's canopy, gold
#: roots and fallen gold leaves, gold flowers ("bluebell"), white stone and old slabs on the stones, the seal and the
#: Ascendancy's decks ("paved"), deck planks on the chains ("plaza"), dew pools; the walkable cloud of the shelf
#: ("satyr", from the module's satyr_field) and the Stormbank's dark cloud ("burned"); and the islands' undersides for
#: the rock under every edge that isn't cloud (tools/bake_ashenvale.sky_cut: the drop itself is cut out).
CROWN_SHEET = {
    "av_forest_floor":   _sk("sk_gold_grass"),
    "av_forest_grass":   _sk("sk_gold_grass"),
    "av_fern_floor":     _sk("sk_gold_moss"),
    "av_root_earth":     _sk("sk_gold_roots"),
    "av_needle_mulch":   _sk("sk_gold_leaves"),
    "av_bluebell":       _sk("sk_gold_flowers"),
    "av_road_centre":    _sk("sk_pale_path"),
    "av_road_edge":      _sk("sk_crown_bark"),
    "av_elven_paving":   _sk("sk_white_stone"),
    "av_mossy_cobble":   _sk("sk_ancient_slabs"),
    "av_plaza_stone":    _sk("sk_deck_planks"),
    "av_rocky_ground":   _sk("sk_gold_roots"),
    "av_stream_bed":     _sk("sk_falls_rocks"),
    "av_lake_mud":       _sk("sk_lake_sand"),
    "av_lake_shallow":   _sk("sk_sky_pool"),
    "av_lake_deep":      _sk("sk_lake_deep"),
    "av_moon_water":     _sk("sk_sky_pool"),
    "av_moon_deep":      _sk("sk_lake_deep"),
    "av_moon_rim":       _sk("sk_lake_sand"),
    "av_cliff_a":        _sk("sk_island_underside"),
    "av_cliff_b":        _sk("sk_island_cliff"),
    "av_canopy":         _sk("sk_gold_leaves", extra="canopy"),
    "av_beach":          _sk("sk_gold_leaves"),
    "av_wet_sand":       _sk("sk_gold_roots"),
    "av_sea_shallow":    _sk("sk_cloud_sun"),
    "av_sea_deep":       _sk("sk_cloud_sun"),
    "av_scorched":       _sk("sk_cloud_storm"),
    "av_burned_forest":  _sk("sk_cloud_storm"),
    "av_fel_earth":      _sk("sk_gold_tips"),
    "av_corrupt_ground": _sk("sk_crown_bark"),
    "av_satyr_earth":    _sk("sk_cloud_solid"),
}
#: Lenswatch (sheets SK): the survey's anchored island. Bare island rock with gold grass where it's caught soil, white
#: stone where the camp is paved ("paved"), pale deck on the gangways and the ship ("plaza"), the court's pools, and
#: the rock underside hanging below (sky_cut).
LENSWATCH_SHEET = dict(CROWN_SHEET)
LENSWATCH_SHEET.update({
    "av_forest_floor":   _sk("sk_island_rock"),
    "av_root_earth":     _sk("sk_island_rock"),
    "av_rocky_ground":   _sk("sk_island_rock"),
    "av_needle_mulch":   _sk("sk_gold_moss"),
    "av_beach":          _sk("sk_island_rock"),
    "av_wet_sand":       _sk("sk_island_rock"),
    "av_road_centre":    _sk("sk_white_stone"),
    "av_road_edge":      _sk("sk_island_rock"),
    "av_plaza_stone":    _sk("sk_deck_pale"),
})
#: The Celestial Expanse (sheets SK): the open day sky. Spring and dew grass on the islands with wind-grass, clover and
#: sky-flower meadows ("bluebell"), island rock at the rims where the soil runs out ("beach"), ruin moss on the
#: Orbiting Ruins ("corrupt"), rubble at the Silent Forge and the Golem Fields ("burned"), cobbled trails, the river and
#: its pools, old stone spans ("plaza"), and walkable cloud on the Whale Shallows ("satyr").
EXPANSE_SHEET = dict(CROWN_SHEET)
EXPANSE_SHEET.update({
    "av_forest_floor":   _sk("sk_spring_grass"),
    "av_forest_grass":   _sk("sk_dew_grass"),
    "av_fern_floor":     _sk("sk_wind_grass"),
    "av_root_earth":     _sk("sk_dew_grass"),
    "av_needle_mulch":   _sk("sk_clover"),
    "av_bluebell":       _sk("sk_skyflower_meadow"),
    "av_road_centre":    _sk("sk_cobble_path"),
    "av_road_edge":      _sk("sk_turf_stones"),
    "av_elven_paving":   _sk("sk_ancient_slabs"),
    "av_mossy_cobble":   _sk("sk_ruin_moss"),
    "av_plaza_stone":    _sk("sk_ancient_slabs"),
    "av_rocky_ground":   _sk("sk_wind_grass"),
    "av_stream_bed":     _sk("sk_falls_rocks"),
    "av_lake_mud":       _sk("sk_clover"),
    "av_lake_shallow":   _sk("sk_river_shallows"),
    "av_lake_deep":      _sk("sk_river"),
    "av_moon_rim":       _sk("sk_island_rock"),
    "av_canopy":         _sk("sk_spring_grass", extra="canopy"),
    "av_beach":          _sk("sk_island_rock"),
    "av_wet_sand":       _sk("sk_island_rock"),
    "av_scorched":       _sk("sk_ruin_rubble"),
    "av_burned_forest":  _sk("sk_ruin_rubble"),
    "av_corrupt_ground": _sk("sk_ruin_moss"),
    "av_fel_earth":      _sk("sk_crystal_sand"),
})
#: The Anchorfields (sheets SK and AE): the engine country at dawn. Dew and wind grass on the shards, clover and
#: sky-flowers on the Estates' lawns ("bluebell"), marble cobbles where the estate and Keelstone are paved, cracked
#: engine paving round the Gearwork and the Seized Anchor ("burned"), crystal ash where the Slipping Anchor bleeds
#: ("corrupt"), island rock at the rims, old stone on the bridges ("plaza").
ANCHOR_SHEET = dict(EXPANSE_SHEET)
ANCHOR_SHEET.update({
    "av_forest_floor":   _sk("sk_dew_grass"),
    "av_forest_grass":   _sk("sk_wind_grass"),
    "av_fern_floor":     _sk("sk_spring_grass"),
    "av_elven_paving":   _sk("ae_marble_cobbles"),
    "av_scorched":       _sk("ae_cracked_paving"),
    "av_burned_forest":  _sk("ae_cracked_paving"),
    "av_corrupt_ground": _sk("ff_crystal_ash"),
    "av_mossy_cobble":   _sk("ae_engraved_stone"),
})
#: The Ascendant Bastions (sheets SK, AE, FF, VY): the Ascendancy's ground under a storm. Wind grass, slate gravel and
#: storm rock on the natural rocks; the fort, the quay, the piers and the gun platforms paved whole in dark slate cobbles
#: (the module's paving_field); pale marble cobbled roads with engraved-stone verges; scorched bronze round the guns
#: and the collectors ("burned"); the Ashwake's ash-grey slate ("corrupt"); riveted bronze plates on the chain bridges
#: ("plaza").
ASC_SHEET = dict(EXPANSE_SHEET)
ASC_SHEET.update({
    "av_forest_floor":   _sk("sk_wind_grass"),
    "av_forest_grass":   _sk("vy_slate_gravel"),
    "av_fern_floor":     _sk("sk_storm_rock"),
    "av_root_earth":     _sk("vy_slate_gravel"),
    "av_needle_mulch":   _sk("sk_wind_grass"),
    "av_rocky_ground":   _sk("sk_storm_rock"),
    "av_lake_mud":       _sk("vy_slate_gravel"),
    "av_bluebell":       _sk("sk_wind_grass"),
    "av_canopy":         _sk("sk_wind_grass", extra="canopy"),
    "av_road_centre":    _sk("ae_marble_cobbles"),
    "av_road_edge":      _sk("ae_engraved_stone"),
    "av_elven_paving":   _sk("ff_ash_cobbles"),
    "av_mossy_cobble":   _sk("ff_ash_cobbles"),
    "av_plaza_stone":    _sk("ae_engine_plates"),
    "av_scorched":       _sk("ff_burnt_bronze"),
    "av_burned_forest":  _sk("ff_burnt_bronze"),
    "av_corrupt_ground": _sk("vy_slate_gravel"),
    "av_moon_rim":       _sk("sk_storm_rock"),
})
#: Aurelion (sheet AE): a city of white and gold. Slabs with gold lines and white marble everywhere underfoot (the
#: ground layers that are grass elsewhere), the Grand Avenue and the ring roads in gold-striped avenue marble with
#: cobbled verges, veined palace marble on the plazas and before the palace ("paved"), the gardens' lawns ("bluebell"),
#: the Eighth's Rest's worn and cracked paving ("burned"), the glowing channel and the pools in teal tiled water,
#: white marble on the bridges ("plaza"), and the rim stone where the rings end.
AURELION_SHEET = dict(EXPANSE_SHEET)
AURELION_SHEET.update({
    "av_forest_floor":   _sk("ae_grand_paving"),
    "av_forest_grass":   _sk("ae_marble_bronze"),
    "av_fern_floor":     _sk("ae_grand_paving"),
    "av_root_earth":     _sk("ae_marble_bronze"),
    "av_needle_mulch":   _sk("ae_grand_paving"),
    "av_rocky_ground":   _sk("ae_marble_bronze"),
    "av_lake_mud":       _sk("ae_marble_bronze"),
    "av_canopy":         _sk("ae_terrace_lawn", extra="canopy"),
    "av_bluebell":       _sk("ae_terrace_lawn"),
    "av_road_centre":    _sk("ae_avenue_marble"),
    "av_road_edge":      _sk("ae_marble_cobbles"),
    "av_elven_paving":   _sk("ae_palace_marble"),
    "av_mossy_cobble":   _sk("ae_marble_bronze"),
    "av_plaza_stone":    _sk("ae_avenue_marble"),
    "av_scorched":       _sk("ae_cracked_paving"),
    "av_burned_forest":  _sk("ae_cracked_paving"),
    "av_lake_shallow":   _sk("ae_gold_pool"),
    "av_lake_deep":      _sk("ae_reflecting_pool"),
    "av_stream_bed":     _sk("ae_gold_pool"),
})
#: The Fading Firmament (sheets SK and FF): the dying heart under a failing violet dusk. Dead grey grass over the
#: islands with grey crystal ash where it's worn through, the void's violet light coming up through cracks at the rims
#: ("beach"), violet crystal rubble where the ground's breaking ("corrupt") speckled with violet shards ("fel"), burnt
#: bronze round the forges and the guns ("burned"), ash cobbles on the roads with ash verges, the old plate's ruined
#: gold-trimmed marble where it was paved ("paved"), and the old slabs on the bridges ("plaza").
FIRMAMENT_SHEET = dict(EXPANSE_SHEET)
FIRMAMENT_SHEET.update({
    "av_forest_floor":   _sk("ff_dead_grass"),
    "av_forest_grass":   _sk("ff_dead_grass"),
    "av_fern_floor":     _sk("ff_dead_grass"),
    "av_root_earth":     _sk("ff_dead_grass"),
    "av_needle_mulch":   _sk("ff_crystal_ash"),
    "av_rocky_ground":   _sk("ff_crystal_ash"),
    "av_lake_mud":       _sk("ff_dead_grass"),
    "av_bluebell":       _sk("ff_dead_grass"),
    "av_canopy":         _sk("ff_dead_grass", extra="canopy"),
    "av_road_centre":    _sk("ff_ash_cobbles"),
    "av_road_edge":      _sk("ff_crystal_ash"),
    "av_elven_paving":   _sk("ff_island_rubble"),
    "av_mossy_cobble":   _sk("ff_island_rubble"),
    "av_plaza_stone":    _sk("sk_ancient_slabs"),
    "av_scorched":       _sk("ff_burnt_bronze"),
    "av_burned_forest":  _sk("ff_burnt_bronze"),
    "av_corrupt_ground": _sk("ff_crumbling_stone"),
    "av_beach":          _sk("ff_void_cracks"),
    "av_wet_sand":       _sk("ff_crystal_ash"),
    "av_moon_rim":       _sk("ff_void_crumbs"),
    "av_fel_earth":      _sk("ff_violet_shards"),
})
#: DAWNHAVEN (docs/dawnhaven_brief.md, 21 Nov 2026): the blood elves' isle off Azshara, painted from Kyle's Azshara
#: ground until its own sheet lands. Amberleaf Glade leans gold (gold leaf litter and gold grass under the trees);
#: Duskfall Woods leans red (crimson brush and red leaf litter under a lower sun).
#: DAWNHAVEN (docs/dawnhaven_art_prompts.md sheet DH1, Kyle 21 Nov 2026): the isle's own ground, over Azshara's for the
#: few layers DH1 doesn't draw (the trodden road edge, the stream bed, lake mud, scorch).
_DH = T / "dawnhaven" / "ground"


def _dh(name, off=0.5, rec=None, extra=None):
    return (_DH / f"{name}.png", off, rec, extra)


_DAWNHAVEN = dict(AZSHARA_SHEET)
_DAWNHAVEN.update({
    "av_elven_paving":   _dh("dh_elven_paving"),
    "av_mossy_cobble":   _dh("dh_paving_cracked"),
    "av_plaza_stone":    _dh("dh_mossy_flag"),
    "av_rocky_ground":   _dh("dh_red_cliff"),
    "av_lake_shallow":   _dh("dh_mere_water"),
    "av_beach":          _dh("dh_shell_beach"),
    "av_wet_sand":       _dh("dh_wet_sand"),
    "av_sea_shallow":    _dh("dh_sea_shallow"),
    "av_sea_deep":       _dh("dh_sea_deep"),
    "av_fel_earth":      _dh("dh_barrow_earth"),
    "av_corrupt_ground": _dh("dh_barrow_earth"),
    "av_satyr_earth":    _dh("dh_coral_sand"),
    "av_moon_water":     _dh("dh_light_water"),
    "av_moon_deep":      _dh("dh_light_water", 0.2),
})
#: Amberleaf Glade, the gold south
AMBERLEAF_SHEET = dict(_DAWNHAVEN)
AMBERLEAF_SHEET.update({
    "av_forest_floor":   _dh("dh_leaf_gold"),
    "av_forest_grass":   _dh("dh_gold_grass"),
    "av_fern_floor":     _dh("dh_crimson_brush"),
    "av_root_earth":     _dh("dh_leaf_red"),
    "av_needle_mulch":   _dh("dh_leaf_trail"),
    "av_bluebell":       _dh("dh_moss_shroom"),
    "av_road_centre":    _dh("dh_leaf_trail"),
    "av_canopy":         _dh("dh_crimson_brush", extra="canopy"),
})
#: Duskfall Woods, the red north under a lower sun; the bluebell layer is the Wildmana Thicket's ley grass
DUSKFALL_SHEET = dict(_DAWNHAVEN)
DUSKFALL_SHEET.update({
    "av_forest_floor":   _dh("dh_dusk_floor"),
    "av_forest_grass":   _dh("dh_crimson_brush"),
    "av_fern_floor":     _dh("dh_leaf_red"),
    "av_root_earth":     _dh("dh_leaf_gold"),
    "av_needle_mulch":   _dh("dh_moss_shroom"),
    "av_bluebell":       _dh("dh_ley_grass"),
    "av_road_centre":    _dh("dh_leaf_trail"),
    "av_plaza_stone":    _dh("dh_paving_cracked"),
    "av_mossy_cobble":   _dh("dh_mossy_flag"),
    "av_canopy":         _dh("dh_leaf_red", extra="canopy"),
})
#: Firstlight Spire, the town: white and gold paving, a gold road
FIRSTLIGHT_SHEET = dict(AMBERLEAF_SHEET)
FIRSTLIGHT_SHEET.update({
    "av_road_centre":    _dh("dh_gold_road"),
    "av_plaza_stone":    _dh("dh_elven_paving"),
    "av_mossy_cobble":   _dh("dh_elven_paving"),
    "av_forest_grass":   _dh("dh_gold_grass"),
})
WPL_SHEET = _plague_sheet(east=False)
EPL_SHEET = _plague_sheet(east=True)
ZONE_SHEETS = {"wpl_south": WPL_SHEET, "wpl_north": WPL_SHEET, "epl_west": EPL_SHEET, "epl_east": EPL_SHEET, "felwood_north": NORTH_SHEET, "stonetalon_east": STONETALON_SHEET,
               "stonetalon_west": STONETALON_WEST_SHEET, "sun_rock": SUN_ROCK_SHEET,
               "azshara_west": AZSHARA_SHEET,
               "dawnhaven_amberleaf": AMBERLEAF_SHEET, "dawnhaven_duskfall": DUSKFALL_SHEET,
               "firstlight_spire": FIRSTLIGHT_SHEET,
               "feralas_high_wilderness": FERALAS_SHEET, "feralas_twin_colossals": FERALAS_NORTH_SHEET,
               "feralas_forgotten_coast": FERALAS_COAST_SHEET, "feralas_mojache": FERALAS_MOJACHE_SHEET,
               "feralas_feathermoon": FERALAS_FEATHERMOON_SHEET, "timbermaw_hold": TIMBERMAW_HOLD_SHEET,
               "azshara_central": AZSHARA_CENTRAL_SHEET, "azshara_east": AZSHARA_EAST_SHEET,
               "deadwind_west": DEADWIND_SHEET, "deadwind_east": DEADWIND_EAST_SHEET, "ariden_watch": ARIDEN_SHEET,
               "moonglade": MOONGLADE_SHEET, "worldtree_rootwater_isle": ROOTWATER_SHEET,
               "worldtree_lower_boughs": LOWER_BOUGHS_SHEET,
               "worldtree_middle_boughs": MIDDLE_BOUGHS_SHEET,
               "worldtree_upper_boughs": UPPER_BOUGHS_SHEET,
               "worldtree_cloudbreak": CLOUDBREAK_SHEET,
               "worldtree_sunward_crown": CROWN_SHEET,
               "worldtree_lenswatch": LENSWATCH_SHEET,
               "worldtree_celestial_expanse": EXPANSE_SHEET,
               "worldtree_anchorfields": ANCHOR_SHEET,
               "worldtree_aurelion": AURELION_SHEET,
               "worldtree_ascendant_bastions": ASC_SHEET,
               "worldtree_fading_firmament": FIRMAMENT_SHEET,
               "worldtree_great_settlement": GREAT_SETTLEMENT_SHEET}

def _recolour(a, hue, sat, val):
    """a float 0..1 HxWx3 -> luminance-preserving tint."""
    lum = a.mean(2)
    v = np.clip(lum, 0, 1) * val
    r, g, b = colorsys.hsv_to_rgb(hue / 360.0, 1.0, 1.0)
    tint = v[..., None] * np.array([r, g, b], np.float32)[None, None, :]
    gray = np.repeat(v[..., None], 3, 2)
    return gray * (1 - sat) + tint * sat


def _seamless(a):
    n = a.shape[0]
    b = np.roll(a, (n // 2, n // 2), axis=(0, 1))
    t = (np.arange(n, dtype=np.float32) + 0.5) / n
    wx = 0.5 - 0.5 * np.cos(2 * np.pi * t)
    wgt = np.sqrt(np.outer(wx, wx))[..., None]
    return a * wgt + b * (1 - wgt)


def synth(stem, seed=3, sheet=None):
    path, off, rec, extra = (sheet or AV_SHEET)[stem]
    im = Image.open(path).convert("RGB")
    w, h = im.size
    s = min(w, h) - 6
    x0 = (w - s) // 2
    y0 = int((h - s) * off)
    im = im.crop((x0, y0, x0 + s, y0 + s)).resize((SIZE, SIZE), Image.LANCZOS)
    a = np.asarray(im, np.float32) / 255.0
    if rec is not None:
        a = _recolour(a, *rec)
    a = _seamless(a)
    rng = np.random.default_rng(seed + sum(map(ord, stem)))
    if extra == "canopy":
        # layered leaf crowns: bright lobes over a dark understory
        lobes = ndi.gaussian_filter(rng.random((SIZE, SIZE)).astype(np.float32), 5.0, mode="wrap")
        lobes = (lobes - lobes.min()) / (lobes.max() - lobes.min() + 1e-6)
        fine = ndi.gaussian_filter(rng.random((SIZE, SIZE)).astype(np.float32), 1.6, mode="wrap")
        fine = (fine - fine.min()) / (fine.max() - fine.min() + 1e-6)
        k = (0.62 + 0.75 * (lobes > 0.52) * (0.45 + 0.55 * fine))[..., None]
        a = a * k
    elif extra:
        col, dens, size = extra
        dots = rng.random((SIZE, SIZE)) < dens
        dots = ndi.binary_dilation(dots, iterations=size - 2) if size > 2 else dots
        c = np.array(col, np.float32) / 255.0
        a = np.where(dots[..., None], a * 0.25 + c * 0.75, a)
    return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))


def build_material_dir(overrides=None):
    """overrides: {stem: AV_SHEET-style entry} a zone paints with instead (North Felwood's demon wastes)."""
    tmp = Path(tempfile.mkdtemp(prefix="av_mat_"))
    provisional = []
    overrides = overrides or {}
    for stem in AV_SHEET:
        if stem in overrides:
            synth(stem, sheet={stem: overrides[stem]}).save(tmp / f"{stem}.png")
            continue
        real = REAL_DIR / f"{stem}.png"
        if real.exists():
            Image.open(real).convert("RGB").resize((SIZE, SIZE), Image.LANCZOS).save(tmp / f"{stem}.png")
            continue
        synth(stem).save(tmp / f"{stem}.png")
        provisional.append(stem)
    return tmp, provisional


MATERIALS = {
    "floor":   ("av_forest_floor", "av_fern_floor", 1.0),
    "grass":   ("av_forest_grass", None, 1.0),
    "fern":    ("av_fern_floor", None, 1.0),
    "root":    ("av_root_earth", None, 1.0),
    "mulch":   ("av_needle_mulch", None, 1.0),
    "bell":    ("av_bluebell", None, 1.0),
    "road":    ("av_road_centre", "av_road_edge", 1.0),
    "verge":   ("av_road_edge", None, 1.0),
    "paving":  ("av_elven_paving", "av_mossy_cobble", 1.0),
    "plaza":   ("av_plaza_stone", None, 1.0),
    "rocky":   ("av_rocky_ground", None, 1.0),
    "stream":  ("av_stream_bed", None, 1.0),
    "mud":     ("av_lake_mud", None, 1.0),
    "lake_s":  ("av_lake_shallow", None, 1.0),
    "lake_d":  ("av_lake_deep", None, 1.0),
    "moon_s":  ("av_moon_water", None, 1.0),
    "moon_d":  ("av_moon_deep", None, 1.0),
    "moonrim": ("av_moon_rim", None, 1.0),
    "sea_s":   ("av_sea_shallow", None, 1.0),
    "sea_d":   ("av_sea_deep", None, 1.0),
    "beach":   ("av_beach", None, 1.0),
    "wet":     ("av_wet_sand", None, 1.0),
    "cliff_a": ("av_cliff_a", "av_cliff_b", 1.0),
    "cliff_d": ("av_cliff_b", None, 1.0),
    "canopy":  ("av_canopy", None, 1.0),
    "scorch":  ("av_scorched", None, 1.0),
    "burned":  ("av_burned_forest", None, 1.0),
    "fel":     ("av_fel_earth", None, 1.0),
    "corrupt": ("av_corrupt_ground", None, 1.0),
    "satyr":   ("av_satyr_earth", None, 1.0),
}


def _tile_soft(P, tiles, key):
    """Smooth mask-grid field (about -1..1) from a list of (x, y) tile coords."""
    g = np.zeros((P.H, P.W), np.float32)
    for (x, y) in tiles:
        g[y, x] = 1.0
    return P.tile_mask(g, threshold=0.5, noise_amp=0.10, key=key, sigma=0.9, soft=True).astype(np.float32)


def build_scores(P, M):
    """M = the zone module (handbuilt_ashenvale_west or _east) providing SPEC and the plan data."""
    S = {}
    gx, gy = P.gx, P.gy
    spec = M.SPEC
    wp = P.warp("regions", amp_tiles=2.4, scale=13.0)
    n_big = P.noise(11.0, "big", octaves=3)
    n_big2 = P.noise(14.0, "big2", octaves=3)
    n_mid = P.noise(5.0, "mid", octaves=3)
    n_fine = P.noise(2.0, "fine", octaves=2)

    F = spec.fields(gx, gy)
    wob = (P.noise(3.0, "shorewob", octaves=3) - 0.5) * 0.9
    sh_ext, dp_ext = F["shallow"].astype(np.float32), F["deep"].astype(np.float32)
    cliff = F["cliff"].astype(np.float32)
    woods = F["woods"].astype(np.float32)

    # tiles sealed by seal_unreachable: collision-only cliffs that must LOOK like walls (canopy / deep water)
    sl = getattr(P, "sealed_land", None)
    sw_t = getattr(P, "sealed_water", None)
    if sl:
        woods = np.maximum(woods, 1.4 * _tile_soft(P, sl, "sealland") + 0.4)
        woods = np.where(_tile_soft(P, sl, "sealland") > 0.02, np.maximum(woods, 1.2), woods).astype(np.float32)
    if sw_t:
        dp_ext = np.maximum(dp_ext, 1.4 * _tile_soft(P, sw_t, "sealwater") + 0.2).astype(np.float32)

    cliff_f = np.clip(cliff * 0.5, -0.4, 0.6).astype(np.float32)
    woods_f = np.clip(woods * 0.5, -0.4, 0.6).astype(np.float32)
    sw = (sh_ext + wob).astype(np.float32)
    d_water_out = np.maximum(-sw, 0)
    d_water_in = np.maximum(sw, 0)
    d_cliff_out = ndi.gaussian_filter(np.maximum(-cliff, 0), 1.2)
    d_cliff_in = ndi.gaussian_filter(np.maximum(cliff, 0), 1.2)
    d_woods_out = ndi.gaussian_filter(np.maximum(-woods, 0), 1.2)
    d_woods_in = ndi.gaussian_filter(np.maximum(woods, 0), 1.2)
    P.fields = dict(cliff=cliff, d_wo=d_water_out, d_wi=d_water_in, d_co=d_cliff_out, d_ci=d_cliff_in,
                    cf=cliff_f, wf=woods_f, d_fo=d_woods_out, d_fi=d_woods_in)

    # -------- the forest floor: dark mossy base, lighter grass in clearings, ferns / roots / needle mulch patches
    clear = np.maximum.reduce([P.blob(cx, cy, rx * 1.05, ry * 1.05, 0.8, wp) for (cx, cy, rx, ry) in M.CLEARINGS])
    open_land = smoothstep(2.0, 12.0, d_woods_out)            # far from any massif -> sunlit
    S["floor"] = np.full_like(n_big, 0.62)
    S["grass"] = 0.15 + 0.85 * np.maximum(clear * (0.55 + 0.45 * smoothstep(0.3, 0.6, n_mid)),
                                          smoothstep(0.60, 0.78, n_big) * (0.35 + 0.65 * open_land))
    S["fern"] = 0.16 + 0.80 * smoothstep(0.62, 0.80, n_mid) * (0.45 + 0.55 * (1 - open_land))
    edge_w = 1 - smoothstep(0.2, 2.6, d_woods_out)            # at the foot of the massifs: gnarled roots
    S["root"] = 0.14 + 0.80 * np.maximum(edge_w * (0.55 + 0.45 * smoothstep(0.35, 0.6, n_fine)),
                                         smoothstep(0.72, 0.86, n_big2) * 0.6)
    S["mulch"] = 0.12 + 0.80 * smoothstep(0.64, 0.80, n_big2) * (0.4 + 0.6 * (1 - open_land))
    bells = [P.blob(*b, 0.75, wp) for b in getattr(M, "BLUEBELL_PATCHES", [])]
    S["bell"] = 0.05 + 0.95 * (np.maximum.reduce(bells) if bells else 0) * smoothstep(0.30, 0.55, n_fine)
    lawns = [P.blob(*b, 0.3, wp) for b in getattr(M, "LAWN_PATCHES", [])]   # whole lawns, not flower speckle
    if lawns:
        S["bell"] = np.maximum(S["bell"], 0.05 + 1.1 * np.maximum.reduce(lawns))
    rocky_skirt = (1 - smoothstep(0.6, 5.0, d_cliff_out)) * (0.4 + 0.6 * smoothstep(0.3, 0.6, n_mid))
    S["rocky"] = 0.08 + 0.9 * np.maximum(rocky_skirt, smoothstep(0.80, 0.92, n_big2) * 0.7)

    # -------- corruption / burned ground around the furbolg dens and satyr lairs
    cor = [P.blob(*b, 0.8, wp) for b in getattr(M, "CORRUPT_PATCHES", [])]
    burn = [P.blob(*b, 0.8, wp) for b in getattr(M, "BURNED_PATCHES", [])]
    cm = np.maximum.reduce(cor) if cor else np.zeros_like(n_big)
    bm = np.maximum.reduce(burn) if burn else np.zeros_like(n_big)
    if getattr(M, "burned_field", None):         # a map can paint its "burned" ground from a field (the Stormbank)
        bm = np.maximum(bm, M.burned_field(P, wp))
    P.fields["cm"] = cm.astype(np.float32)
    lush = getattr(M, "LUSH", 0.0)       # South Felwood: Kyle, 14 Nov: "make southern more vibrant"
    if lush:
        live = 1 - np.clip(cm * 1.4, 0, 1)
        S["grass"] = S["grass"] + lush * 0.55 * live * (0.5 + 0.5 * smoothstep(0.3, 0.7, n_mid))
        S["fern"] = S["fern"] + lush * 0.30 * live * smoothstep(0.45, 0.75, n_fine)
        S["bell"] = S["bell"] + lush * 0.22 * live * smoothstep(0.62, 0.82, n_big2)
        S["mulch"] = S["mulch"] - lush * 0.35 * live
        S["root"] = S["root"] - lush * 0.20 * live
    # Stonetalon East: inside the blast nothing living shows through the ash (BURN_SUPPRESS on the zone module)
    burn_k = getattr(M, "BURN_SUPPRESS", 0.0)
    if burn_k:
        for k in ("floor", "grass", "fern", "root", "mulch"):
            S[k] = S[k] - burn_k * bm
    dark_k = getattr(M, "DARK_SUPPRESS", 0.0)
    if dark_k:
        for k in ("floor", "grass", "fern", "root", "mulch", "bell"):
            S[k] = S[k] - dark_k * cm
    S["corrupt"] = 0.04 + 0.95 * cm * (0.6 + 0.4 * smoothstep(0.3, 0.6, n_mid))
    S["fel"] = 0.04 + 0.95 * cm * smoothstep(0.55, 0.78, n_fine) * smoothstep(0.1, 0.5, cm)
    S["burned"] = 0.04 + 0.95 * bm
    S["scorch"] = 0.04 + 0.95 * bm * smoothstep(0.55, 0.75, n_mid)
    S["satyr"] = 0.03 + 0.95 * getattr(M, "satyr_field", lambda P_, wp_: np.zeros_like(n_big))(P, wp)

    # -------- roads, paved gates, the moonwell's silver paving
    core, verge, _ = P.road_field(list(M.ROADS.values()))
    S["road"] = 0.05 + 1.3 * core
    S["verge"] = 0.08 + 0.95 * verge * (1 - core)
    pav = [P.blob(*b, 0.55, wp) for b in getattr(M, "PAVED_PATCHES", [])]
    S["paving"] = 0.04 + 1.1 * (np.maximum.reduce(pav) if pav else 0) * (0.9 + 0.1 * n_fine)
    if getattr(M, "paving_field", None):        # a map can pave whole built shapes (the Bastions' fort, quay and guns)
        S["paving"] = np.maximum(S["paving"], 0.04 + 1.1 * M.paving_field(P, wp))
    S["plaza"] = 0.03 + 1.1 * getattr(M, "plaza_field", lambda P_, wp_: np.zeros_like(n_big))(P, wp)

    # -------- water: sea / lakes & rivers / moon-pools
    sea_ext = M.sea(gx, gy) if getattr(M, "sea", None) else np.full_like(n_big, -99.0)
    sea_side = sea_ext > -3.0
    moon_zone = np.zeros_like(n_big, bool)
    for (cx, cy, r) in getattr(M, "MOON_POOLS", []):
        moon_zone |= (np.hypot(gx - cx, gy - cy) < r)
    lake_out = np.where(sea_side, 99.0, d_water_out)
    near_moon = np.where(moon_zone, d_water_out, 99.0)
    S["mud"] = 0.08 + 1.1 * (1 - smoothstep(0.35, 2.0, lake_out)) * (0.75 + 0.25 * n_fine)
    S["moonrim"] = 0.04 + 1.2 * (1 - smoothstep(0.2, 1.3, near_moon))
    sea_out = np.where(sea_side, d_water_out, 99.0)
    S["beach"] = 0.06 + 1.0 * (1 - smoothstep(1.0, 8.0, sea_out)) * (0.6 + 0.4 * smoothstep(0.25, 0.6, n_fine))
    S["wet"] = 0.06 + 1.1 * (1 - smoothstep(0.3, 1.7, sea_out))

    w_s = np.clip(sh_ext + wob, -4, 6)
    w_d = np.clip(dp_ext + wob, -6, 6)
    base_s = (1.6 + 10 * w_s).astype(np.float32)
    base_d = (1.6 + 10 * w_s + 2.5 * w_d).astype(np.float32)
    off = np.float32(-40.0)
    S["sea_s"] = np.where(sea_side, base_s, off).astype(np.float32)
    S["sea_d"] = np.where(sea_side, base_d, off).astype(np.float32)
    S["lake_s"] = np.where(sea_side | moon_zone, off, base_s).astype(np.float32)
    S["lake_d"] = np.where(sea_side | moon_zone, off, base_d).astype(np.float32)
    S["moon_s"] = np.where(moon_zone & ~sea_side, base_s, off).astype(np.float32)
    S["moon_d"] = np.where(moon_zone & ~sea_side, base_d, off).astype(np.float32)
    # fords: the river is wadeable here, show the pebble bed through the water
    near_ford = np.zeros_like(n_big)
    for (fx, fy, fr) in spec.fords:
        near_ford = np.maximum(near_ford, np.clip(1 - np.hypot(gx - fx, gy - fy) / fr, 0, 1))
    S["stream"] = (-2.0 + 12 * np.clip(sw + 0.4, 0, 1) * near_ford + 0.6 * near_ford).astype(np.float32)
    S["stream"] = np.maximum(S["stream"], (0.04 + 0.9 * (1 - smoothstep(0.0, 0.9, d_water_in)) *
                                            smoothstep(0.0, 0.3, d_water_in) * near_ford).astype(np.float32))
    knock = smoothstep(0.0, 0.7, sw)
    for k in ("floor", "grass", "fern", "root", "mulch", "bell", "rocky", "corrupt", "fel", "burned", "scorch",
              "satyr", "road", "verge", "paving", "plaza", "beach", "wet", "mud", "moonrim"):
        S[k] = (S[k] - 14.0 * knock).astype(np.float32)
    S["lake_s"] = (S["lake_s"] - 6.0 * near_ford * np.clip(1 - np.maximum(sw, 0) * 1.5, 0, 1)).astype(np.float32)

    # a sky map's walkable cloud (the Sunward Crown): the ground's own materials don't show on it at all
    sup = getattr(M, "ground_suppress", None)
    if sup is not None:
        m = sup(gx, gy)
        for k in ("floor", "grass", "fern", "root", "mulch", "bell", "rocky", "corrupt", "fel", "road", "verge",
                  "beach", "wet", "mud", "moonrim"):
            S[k] = (S[k] - 3.0 * m).astype(np.float32)

    # -------- cliffs (rock) and the dense-woods canopy (both impassable, drawn differently)
    depth_dark = smoothstep(2.0, 9.0, d_cliff_in)
    cs = 1.6 + 12 * cliff_f
    S["cliff_a"] = (cs - 1.0 * depth_dark).astype(np.float32)
    S["cliff_d"] = (cs - 2.6 + 2.6 * depth_dark).astype(np.float32)
    S["canopy"] = (1.6 + 12 * woods_f).astype(np.float32)
    cl_k = smoothstep(0.0, 0.30, cliff_f)
    wd_k = smoothstep(0.0, 0.30, woods_f)
    for k in list(S):
        if k.startswith("cliff_") or k == "canopy":
            continue
        S[k] = (S[k] - 14.0 * cl_k - 14.0 * wd_k - (40.0 * smoothstep(0.0, 1.2, cliff) if k.endswith(("_s", "_d")) else 0.0)
                ).astype(np.float32)
    # a mesa wins over a woods blob where both overlap, and vice versa the canopy must not paint over rock
    S["canopy"] = (S["canopy"] - 16.0 * cl_k).astype(np.float32)
    S["cliff_a"] = (S["cliff_a"] - 16.0 * wd_k * (1 - cl_k)).astype(np.float32)
    S["cliff_d"] = (S["cliff_d"] - 16.0 * wd_k * (1 - cl_k)).astype(np.float32)
    return S


def drop_depth(rgb, X, Y, drop):
    """Make the drop read as a long way down (docs/worldtree_brief.md, "How it's drawn"): what's far below fades toward
    the haze of height, the boughs throw a soft shadow down onto it from the top-left light, and the bark darkens where
    each bough rounds away at its edge. drop = {"sea": the module's sea field, "haze": RGB, "fade": 0..1,
    "shadow": (dx, dy) in tiles, "sat": how much colour distance leaves (0.55 by default; the city keeps its lanterns)}."""
    sea = drop["sea"]
    gx, gy = X / TILE_PX, Y / TILE_PX
    s = sea(gx, gy)
    below = smoothstep(-0.3, 0.9, s)                                     # 1 over the drop
    far = smoothstep(0.0, 10.0, s)                                       # deeper into the void, further down
    haze = np.array(drop.get("haze", (104, 142, 128)), np.float32)
    k = (drop.get("fade", 0.42) + 0.18 * far) * below
    lum = rgb.mean(axis=2, keepdims=True)
    flat = lum + (rgb - lum) * drop.get("sat", 0.55)                  # distance takes the colour out
    rgb = rgb * (1 - below[..., None]) + flat * below[..., None]
    rgb = rgb * (1 - k[..., None]) + haze * k[..., None]
    dx, dy = drop.get("shadow", (3.0, 5.0))
    cast = 1 - smoothstep(-3.0, 3.5, sea(gx - dx, gy - dy))              # bark up-left of here shades the canopy
    rgb = rgb * (1 - 0.42 * cast * below)[..., None]
    rim = smoothstep(-2.2, 0.0, s) * (1 - below)                         # the bough's edge falling away
    rgb = rgb * (1 - 0.38 * rim)[..., None]
    return rgb


def sky_cut(rgb, X, Y, P):
    """A sky map's drop, cut out (M.SKY; docs/worldtree_brief.md, "How it's drawn"). The ground stays where the land is,
    the drop goes clear so the renderer's cloud sea shows through, and under each island's southern edge its rock
    underside hangs down into the void, darkening and thinning away (the camera looks a little north, so the south
    face is the one you see): "Edges sell the height." Where the land is walkable cloud (SKY["cloud"], a function of
    tile x, y giving 0..1; the Sunward Crown's shelf), there's no rock under it: the cloud's edge is soft, and what
    hangs below it is a short, pale billow fading out. Returns (rgb, alpha 0..1)."""
    sky = P.sky_spec
    sea = sky["sea"]
    cloud_fn = sky.get("cloud")
    gx, gy = X / TILE_PX, Y / TILE_PX
    s = sea(gx, gy)
    cl_here = cloud_fn(gx, gy) if cloud_fn else np.zeros_like(s)
    land = 1 - smoothstep(-0.35 - 0.9 * cl_here, 0.25, s)
    depth = float(sky.get("underside", 4.0))
    depth_c = float(sky.get("cloud_underside", 2.2))
    under = np.zeros_like(s)
    under_c = np.zeros_like(s)
    for d in np.linspace(0.35, depth, 10):
        above = 1 - smoothstep(-0.3, 0.3, sea(gx, gy - d))               # land d tiles north of here
        under = np.maximum(under, above * (1 - d / depth) ** 0.8)
        if cloud_fn is not None and d <= depth_c:
            under_c = np.maximum(under_c, above * np.clip(1 - d / depth_c, 0, 1) ** 1.6)
    under = under * (1 - land)
    under_c = under_c * (1 - land)
    cl_above = cloud_fn(gx, gy - 1.0) if cloud_fn else np.zeros_like(s)
    # the rock: the map's cliff stone stretched down the face, banded, with a few roots and drips hanging lower
    tex = P.tex(sky.get("rock") or MATERIALS["cliff_a"][0])
    sx = (X % TEX).astype(np.int32)
    sy = ((Y * 0.45) % TEX).astype(np.int32)
    rock = tex[sy, sx].astype(np.float32)
    band = 0.80 + 0.20 * np.sin(Y / TILE_PX * 2.3 + P.sample_field(P.noise(5.0, "strata"), X, Y) * 3.0)
    rock = rock * band[..., None] * (0.38 + 0.55 * under)[..., None]
    roots = smoothstep(0.62, 0.80, P.sample_field(P.noise(1.3, "roots", octaves=1), X * 4.0, Y * 0.25))
    under_a = np.clip(under * 1.15 + roots * under * 0.5, 0, 1)
    if cloud_fn is not None:
        # the cloud's underside: its own texture squashed down, a little shadowed and blue, fading to nothing
        ctex = P.tex(sky.get("cloud_tex") or MATERIALS["satyr"][0])
        csy = ((Y * 0.6) % TEX).astype(np.int32)
        puff = ctex[csy, sx].astype(np.float32) * (0.72 + 0.22 * under_c)[..., None]
        puff = puff * np.array([0.96, 0.98, 1.04], np.float32)
        k = cl_above[..., None]
        rock = rock * (1 - k) + puff * k
        under_a = under_a * (1 - cl_above) + np.clip(under_c * 0.9, 0, 1) * cl_above
    rgb = rgb * land[..., None] + rock * (1 - land)[..., None]
    rim = smoothstep(-1.0, 0.0, s) * land                                 # the lip darkens where it rounds over
    rgb = rgb * (1 - 0.30 * rim * (1 - cl_here) + 0.06 * rim * cl_here)[..., None]
    lift = float(sky.get("cloud_lift", 0.0))     # walkable cloud lit brighter than the ground's shading leaves it
    if lift:
        rgb = rgb * (1 + lift * cl_here * land)[..., None]
    if cloud_fn is not None:
        # WALKABLE CLOUD THAT LOOKS SOLID. Kyle, 21 Nov 2026, on the Sunward Crown: "the cloud tiles... need to APPEAR
        # dense....right now it looks like im out of bounds... if we use cloud tiles they need to LOOK solid". The
        # shelf used the same soft cumulus as the sky far below, so standing on it read as standing on nothing. Now
        # it's shaded as a surface: big soft mounds lit from the top left, with shadow pooling in the dips between
        # them, so it reads as ground you could kick. Only where the cloud is land (cl_here * land); the drop and
        # the rock islands are untouched.
        hf = P.noise(4.5, "cloud_relief", octaves=2)
        h = P.sample_field(hf, X, Y)
        e = TILE_PX * 0.35
        hx = P.sample_field(hf, X + e, Y) - P.sample_field(hf, X - e, Y)
        hy = P.sample_field(hf, X, Y + e) - P.sample_field(hf, X, Y - e)
        relief = 1.0 - 1.7 * (0.5 * hx + hy)               # facing the top light brightens, away darkens
        relief = relief * (0.86 + 0.20 * h)                # the dips between mounds sit in a little shadow
        k = (cl_here * land)[..., None]
        rgb = rgb * (1 - k) + rgb * np.clip(relief, 0.76, 1.16)[..., None] * k
        # a firm, slightly shadowed lip where the cloud ends, so its edge reads as an edge
        lip = smoothstep(-1.4, -0.2, s) * (1 - smoothstep(-0.2, 0.3, s)) * cl_here
        rgb = rgb * (1 - 0.22 * lip)[..., None]
    alpha = np.maximum(land, under_a)
    return rgb, alpha


def post(rgb, X, Y, P):
    f = P.fields
    sf = lambda a: P.sample_field(a.astype(np.float32), X, Y)
    d_co, d_ci = sf(f["d_co"]), sf(f["d_ci"])
    d_wo, d_wi = sf(f["d_wo"]), sf(f["d_wi"])
    d_fo, d_fi = sf(f["d_fo"]), sf(f["d_fi"])
    # twilight dapple: big slow light patches under the canopy plus a little fine mottling
    dap = P.sample_field(P.noise(7.0, "dapple", octaves=3), X, Y)
    lum_n = P.sample_field(P.noise(18.0, "lumlow", octaves=2), X, Y)
    shade = (0.86 + 0.26 * dap) * (0.96 + 0.08 * lum_n)
    shade *= 1 - 0.26 * (1 - smoothstep(0.0, 1.7, d_co))      # rock: dark foot
    shade *= 1 - 0.26 * smoothstep(1.5, 11.0, d_ci)
    shade *= 1 - 0.30 * (1 - smoothstep(0.0, 2.6, d_fo))      # woods: shadow pooled at the treeline
    shade *= 1 - 0.40 * smoothstep(1.5, 10.0, d_fi)           # ... and deep inside the massif
    cf = sf(f["cf"])
    lip = smoothstep(0.0, 0.03, cf) * (1 - smoothstep(0.03, 0.14, cf))
    wf = sf(f["wf"])
    wl = smoothstep(0.0, 0.03, wf) * (1 - smoothstep(0.03, 0.12, wf))
    rgb = rgb * shade[..., None] + 26 * lip[..., None] + 12 * wl[..., None]
    wet = (1 - smoothstep(0.0, 1.0, d_wo)) * smoothstep(0.0, 0.25, d_wo)
    rgb *= (1 - 0.14 * wet)[..., None]
    foam = (1 - smoothstep(0.0, 0.30, d_wo + d_wi)) * 0.26
    foam = foam * (1 - smoothstep(-0.05, 0.12, cf))
    drop = getattr(P, "drop", None)
    if drop:
        # a map over a long fall (the World Tree's tiers, M.DROP): the module's sea field is the drop, so no surf
        s_here = drop["sea"](X / TILE_PX, Y / TILE_PX)
        foam = foam * smoothstep(0.6, 2.2, np.abs(s_here))
    rgb = rgb * (1 - foam[..., None]) + np.array([225, 240, 240], np.float32) * foam[..., None]
    if drop:
        rgb = drop_depth(rgb, X, Y, drop)
    rgb = rgb * np.array([0.97, 0.99, 1.04], np.float32)       # cool twilight cast
    grade = getattr(P, "grade", None)
    if grade:
        # Living ground gets more colour and light; the corruption keeps its sick, dim cast.
        sat, val = grade
        live = 1 - np.clip(sf(f["cm"]) * 1.4, 0, 1)
        lum = rgb.mean(axis=2, keepdims=True)
        k_s = (1 + (sat - 1) * live)[..., None]
        k_v = (1 + (val - 1) * live)[..., None]
        rgb = (lum + (rgb - lum) * k_s) * k_v
    lift = getattr(P, "lift", None)
    if lift:
        # the whole map, corruption and all (North Felwood: its blighted textures are dark at source)
        sat, val = lift
        lum = rgb.mean(axis=2, keepdims=True)
        rgb = (lum + (rgb - lum) * sat) * val
    light = getattr(P, "light", None)
    if light:
        # a map's own light, last of all (the Cloudbreak: fog at the foot of the climb, gold at the top)
        rgb = light(rgb, X / TILE_PX, Y / TILE_PX)
    return rgb


def bake(zone="west", preview=None, scale=4, only=None):
    if zone == "west":
        from tools import handbuilt_ashenvale_west as M
    elif zone == "felwood_south":
        # South Felwood is "high level Ashenvale" (Kyle, 14 Nov): the same materials and the same painter,
        # with more of the corruption palette as it runs north.
        from tools import handbuilt_felwood_south as M
    elif zone == "felwood_north":
        # North Felwood is the demon wastes: the same painter and plan, painted from the corruption
        # palette (NORTH_SHEET) so nothing in it reads as living forest.
        from tools import handbuilt_felwood_north as M
    elif zone == "wpl_south":
        # South Western Plaguelands (docs/plaguelands_design.md)
        from tools import handbuilt_wpl_south as M
    elif zone == "wpl_north":
        from tools import handbuilt_wpl_north as M
    elif zone == "epl_west":
        from tools import handbuilt_epl_west as M
    elif zone == "epl_east":
        from tools import handbuilt_epl_east as M
    elif zone == "stonetalon_west":
        from tools import handbuilt_stonetalon_west as M
    elif zone == "azshara_west":
        # West Azshara (docs/azshara_brief.md): autumn forest, Kyle's Azshara ground sheet (AZSHARA_SHEET)
        from tools import handbuilt_azshara_west as M
    elif zone == "dawnhaven_amberleaf":
        # Amberleaf Glade (docs/dawnhaven_brief.md): Dawnhaven's south, gold autumn (AMBERLEAF_SHEET)
        from tools import handbuilt_dawnhaven_amberleaf as M
    elif zone == "dawnhaven_duskfall":
        # Duskfall Woods: Dawnhaven's north, red autumn (DUSKFALL_SHEET)
        from tools import handbuilt_dawnhaven_duskfall as M
    elif zone == "azshara_east":
        # East Azshara (docs/azshara_brief.md): the drowned coast (AZSHARA_EAST_SHEET)
        from tools import handbuilt_azshara_east as M
    elif zone == "azshara_central":
        # Central Azshara (docs/azshara_brief.md): the leylines, Eldarath and the Bay of Storms (AZSHARA_CENTRAL_SHEET)
        from tools import handbuilt_azshara_central as M
    elif zone == "deadwind_west":
        # Deadwind West (docs/deadwind_quest_plan.md): the tunnel, the dead forest, Morgan's Plot, the ogres (DEADWIND_SHEET)
        from tools import handbuilt_deadwind_west as M
    elif zone == "deadwind_east":
        # Deadwind East: the gorge, broken time, Karazhan's crag and the rupture under the wheel (DEADWIND_EAST_SHEET)
        from tools import handbuilt_deadwind_east as M
    elif zone.startswith(("feralas_", "worldtree_")):
        # Feralas (docs/feralas_brief.md): the three open maps, FERALAS_SHEET / FERALAS_COAST_SHEET
        import importlib
        M = importlib.import_module(f"tools.handbuilt_{zone}")
    elif zone == "stonetalon_east":
        # Stonetalon East: the blast zone, painted from the Aspen materials (STONETALON_SHEET)
        from tools import handbuilt_stonetalon_east as M
    else:
        from tools import handbuilt_ashenvale_east as M
    mat_dir, provisional = build_material_dir(ZONE_SHEETS.get(zone))
    if provisional:
        print(f"PROVISIONAL textures for {len(provisional)} materials: {', '.join(provisional[:8])}...")
    P = Painter(M.W, M.H, mat_dir, seed=2101)
    # build the layout once so sealed pockets are painted as walls
    L = M.build_layout()
    P.sealed_land = getattr(L, "sealed_land", [])
    P.sealed_water = getattr(L, "sealed_water", [])
    P.grade = getattr(M, "GRADE", None)
    P.lift = getattr(M, "LIFT", None)
    P.light = getattr(M, "LIGHT", None)
    P.drop = dict(getattr(M, "DROP"), sea=M.sea) if getattr(M, "DROP", None) else None
    if getattr(M, "SKY", None):
        # a sky map: the drop is cut out and the cloud sea is the renderer's (ui/tilemap_renderer._draw_sky)
        P.sky_spec = dict(M.SKY, sea=M.sea)
        P.sky = sky_cut
        P.drop = None
    scores = build_scores(P, M)
    out = ROOT / M.BAKED_DIR
    mats = MATERIALS
    if getattr(P, "sky_spec", None) and P.sky_spec.get("cloud"):
        # Walkable cloud drawn at near scale, its puffs a few tiles across, so it reads as cloud right under your
        # feet and not as the cloud sea a mile below (Kyle, 21 Nov 2026: "if we use cloud tiles they need to LOOK
        # solid"). Only the sky maps; the satyr earth this slot paints elsewhere keeps its scale.
        mats = dict(MATERIALS)
        a, b, sc_ = mats["satyr"]
        mats["satyr"] = (a, b, sc_ * float(P.sky_spec.get("cloud_scale", 2.6)))
    written = P.bake(mats, scores, out, chunk_tiles=20, post=post, only=only)
    print(f"baked {len(written)} chunks -> {out}")
    if preview:
        full = Image.new("RGB", (M.W * TILE_PX, M.H * TILE_PX))
        for fn, cx, cy, w, h in written:
            im = Image.open(fn)
            if im.mode == "RGBA":          # a sky map: preview it over a flat sky blue so the cut reads
                bg = Image.new("RGBA", im.size, (150, 185, 225, 255))
                bg.alpha_composite(im)
                im = bg.convert("RGB")
            full.paste(im, (cx * TILE_PX, cy * TILE_PX))
        full.resize((M.W * scale, M.H * scale), Image.LANCZOS).save(preview)
        print("preview", preview)


def main():
    preview = None
    if "--preview" in sys.argv:
        preview = sys.argv[sys.argv.index("--preview") + 1]
    sc = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 4
    zone = next((z for z in ("worldtree_fading_firmament", "worldtree_ascendant_bastions", "worldtree_aurelion", "worldtree_anchorfields", "worldtree_celestial_expanse", "worldtree_lenswatch", "worldtree_sunward_crown", "worldtree_cloudbreak", "worldtree_upper_boughs", "worldtree_middle_boughs", "worldtree_great_settlement", "worldtree_lower_boughs", "worldtree_rootwater_isle", "feralas_high_wilderness", "feralas_forgotten_coast", "feralas_twin_colossals", "deadwind_west", "deadwind_east", "azshara_east", "azshara_central", "azshara_west", "dawnhaven_amberleaf", "dawnhaven_duskfall", "wpl_south", "wpl_north", "epl_west", "epl_east", "felwood_north", "felwood_south", "stonetalon_east", "stonetalon_west", "east") if z in sys.argv), "west")
    only = None
    if "--region" in sys.argv:       # x0,y0,x1,y1 in tiles: bake only the 20x20 chunks touching it (fast look-dev)
        x0, y0, x1, y1 = map(int, sys.argv[sys.argv.index("--region") + 1].split(","))
        only = {(cx, cy) for cx in range(x0 // 20 * 20, x1 + 1, 20) for cy in range(y0 // 20 * 20, y1 + 1, 20)}
    bake(zone, preview, sc, only)


if __name__ == "__main__":
    main()
