"""
Tile ID -> texture mapping registry.

world/tiles.py owns tile IDs, walkability, and flat-color fallbacks - this
file is purely additive on top of it and is never required for the game to
run. Every entry maps a tile_id (+ optional biome) to a source sheet path
and pixel rect. ui/tilemap_renderer.py looks up sprites here first and
falls back to tiles.py's flat color if nothing is mapped (missing pack,
bad rect, etc).

Coordinates below were found via tools/tile_mapping/find_flat_tiles.py
(scans a sheet for locally-tileable, non-transparent blocks) plus manual
visual confirmation - see tools/tile_mapping/NOTES.md for the full
candidate contact sheets and reasoning per pack if these ever need
revisiting or extending.

TILE_SIZE: current on-screen render size in pixels. Bumped from the old
16 to 32 specifically to accommodate Forgotten Memories' high-res
(~170px native) art without mud - see NOTES.md "resolution decision".
ui/tilemap_renderer.py and ui/screens/overworld_screen.py both read this
constant rather than hardcoding 32, so changing scale again later is a
one-line change.
"""

TILE_SIZE = 32

# ---------------------------------------------------------------------------
# Sheet paths, relative to the project root (frontier_rpg/).
# ---------------------------------------------------------------------------
SHEETS = {
    # Real Durotar/desert ground textures (10 cropped tiles from an
    # AI-generated Durotar terrain sheet) - replaces the earlier
    # "gen_red_sand"/"gen_red_rock" baked-tint stand-ins flagged in
    # tools/tile_mapping/NOTES.md as "no source pack shipped a genuine
    # red-sand texture". These are real dedicated art, not a tint, and
    # were sitting cropped-and-verified in a prior session's asset pass
    # (crop_work2/terrain1/) but never actually copied into assets/ or
    # wired into this registry - same "designed but never delivered" gap
    # this whole file turned out to have (see this session's real find:
    # every SHEETS entry below this comment pointed at a file that didn't
    # exist on disk). Each entry here is a single tight-cropped PNG, not
    # a multi-tile sheet, so its "rect" in BIOME_TILES is always
    # (0, 0, actual_width, actual_height) - the whole image.
    "durotar_cracked_red_earth_a": "assets/tiles/durotar/cracked_red_earth_a.png",
    "durotar_cracked_red_earth_b": "assets/tiles/durotar/cracked_red_earth_b.png",
    "durotar_cracked_red_earth_c": "assets/tiles/durotar/cracked_red_earth_c.png",
    "durotar_red_earth_to_dry_grass": "assets/tiles/durotar/red_earth_to_dry_grass.png",
    "durotar_dry_grass_patch_a": "assets/tiles/durotar/dry_grass_patch_a.png",
    "durotar_dry_grass_patch_b": "assets/tiles/durotar/dry_grass_patch_b.png",
    "durotar_rocky_red_ground_a": "assets/tiles/durotar/rocky_red_ground_a.png",
    "durotar_rocky_red_ground_b": "assets/tiles/durotar/rocky_red_ground_b.png",
    "durotar_sun_bleached_path_dirt": "assets/tiles/durotar/sun_bleached_path_dirt.png",
    "durotar_red_earth_to_stone": "assets/tiles/durotar/red_earth_to_stone.png",
    "durotar_packed_town_dirt_a": "assets/tiles/durotar/packed_town_dirt_a.png",
    "durotar_packed_town_dirt_b": "assets/tiles/durotar/packed_town_dirt_b.png",
    "durotar_dirt_road_straight": "assets/tiles/durotar/dirt_road_straight.png",
    # Second Durotar art drop (Kyle: "remove the ugly grey rocks scattered
    # everyone and the ugly trees and replace with these") - 20 more
    # sprites: 8 real ground-texture variants, 6 real desert-plant scatter
    # props (5 genuinely distinct plus the tall saguaro), 6 mountain/cliff
    # tiles. The 6 scatter props (09-14) arrived with a baked-in white
    # background plus a leftover black cropping-artifact bar - NOT real
    # transparency despite the files being RGBA - so these went through
    # an actual background-removal pass (brightness/saturation threshold +
    # 1px erosion to kill the anti-aliased white halo, then tight-cropped)
    # before being copied in; see this session's chat for the before/after
    # comparison. jagged_mountain_peak (18) got the same treatment for its
    # dark background (a real standalone peak silhouette, not a seamless
    # tile like the other 5 mountain crops) - confirmed by sampling: 41%
    # of its pixels were pure near-black background vs. 13-27% for the
    # other mountain tiles, which is normal shadow/crevice detail within
    # an actual seamless rock texture, not an artifact.
    "durotar_cracked_red_rock_a": "assets/tiles/durotar/01_cracked_red_rock_A.png",
    "durotar_cracked_red_rock_b": "assets/tiles/durotar/02_cracked_red_rock_B.png",
    "durotar_smooth_red_sandstone": "assets/tiles/durotar/03_smooth_red_sandstone.png",
    "durotar_pebble_strewn_red_earth": "assets/tiles/durotar/04_pebble_strewn_red_earth.png",
    "durotar_rust_streaked_rock": "assets/tiles/durotar/05_rust_streaked_rock.png",
    "durotar_sun_bleached_red_clay": "assets/tiles/durotar/06_sun_bleached_red_clay.png",
    "durotar_red_rock_to_sand_edge": "assets/tiles/durotar/07_red_rock_to_sand_edge.png",
    "durotar_red_rock_rubble_patch": "assets/tiles/durotar/08_red_rock_rubble_patch.png",
    "durotar_barrel_cactus": "assets/tiles/durotar/09_barrel_cactus.png",
    "durotar_tall_saguaro_cactus": "assets/tiles/durotar/10_tall_saguaro_cactus.png",
    "durotar_prickly_scrub_cactus": "assets/tiles/durotar/11_prickly_scrub_cactus_cluster.png",
    "durotar_dry_thornbush": "assets/tiles/durotar/12_dry_thornbush.png",
    "durotar_hardy_desert_shrub": "assets/tiles/durotar/13_hardy_desert_shrub.png",
    "durotar_dead_scrub_twig": "assets/tiles/durotar/14_dead_scrub_twig_cluster.png",
    # Real large-format mountain/cliff wall art (this session, from the
    # same ChatGPT batch as the VoT water below) - replaces the small
    # 184x285 durotar_mountain_rock_face_a/b crops, which read as a
    # visible repeating grid once actually rendered at 32px tile size
    # (Kyle: "we need to fix up the mountains next too", confirmed via
    # an in-game screenshot showing VoT's boundary wall as a small
    # repeating texture, same disease as every other small-crop material
    # this session fixed for ground/floor art). 627x627, no baked
    # border, verified seamless via 3x3 self-tile preview - 2 genuinely
    # different silhouettes (rounded stacked-boulder vs. jagged spire)
    # for real variety instead of one texture repeating everywhere.
    "vot_cliff_wall_a": "assets/tiles/valley_of_trials/cliff_wall_a.png",
    "vot_cliff_wall_b": "assets/tiles/valley_of_trials/cliff_wall_b.png",
    # Real large-format oasis water (this session, same batch as above) -
    # replaces durotar_oasis_water (83x132, same small-crop-at-32px
    # problem, and visibly flatter/more dated than the rest of VoT's
    # upgraded ground once actually rendered next to it - Kyle: "our
    # lake is gone... maybe... make some water tiles next"). Deep and
    # shallow are genuinely distinct source images (darker saturated
    # blue with no visible bottom vs. bright teal-green with visible
    # rocks through it), not a tint of the same image like the earlier
    # programmatic shallow-water variant for the Barrens oases.
    "vot_oasis_deep_water": "assets/tiles/valley_of_trials/oasis_deep_water.png",
    "vot_oasis_shallow_water": "assets/tiles/valley_of_trials/oasis_shallow_water.png",
    "durotar_mountain_rock_face_a": "assets/tiles/durotar/15_mountain_rock_face_A.png",
    "durotar_mountain_rock_face_b": "assets/tiles/durotar/16_mountain_rock_face_B.png",
    "durotar_mountain_base_to_ground": "assets/tiles/durotar/17_mountain_base_to_ground_edge.png",
    "durotar_jagged_mountain_peak": "assets/tiles/durotar/18_jagged_mountain_peak.png",
    "durotar_boulder_wall": "assets/tiles/durotar/19_boulder_wall_impassable.png",
    "durotar_mountain_scree_slope": "assets/tiles/durotar/20_mountain_scree_slope.png",
    "durotar_oasis_water": "assets/tiles/durotar/oasis_water_1.png",
    "durotar_thornbush": "assets/tiles/durotar/thornbush_ground.png",
    # Real cave floor/wall textures (same source: crop_work2/terrain_dungeon/,
    # the Oasis/Cave/Keep-Fortress/Dungeon sheet). Fixes the "cave floor and
    # wall were pixel-identical flat colors" gap the same way the
    # DampDungeons stand-in was meant to (see "cave_mossy" biome comment
    # below) - this is real cave art instead of a mossy-brick European
    # dungeon reuse.
    "cave_floor_rock_1": "assets/tiles/caves/cave_floor_rock_1.png",
    "cave_floor_rock_2": "assets/tiles/caves/cave_floor_rock_2.png",
    "cave_floor_rock_3": "assets/tiles/caves/cave_floor_rock_3.png",
    "cave_wall_1": "assets/tiles/caves/cave_wall_1.png",
    "cave_wall_2": "assets/tiles/caves/cave_wall_2.png",
    "cave_mossy_floor_real": "assets/tiles/caves/mossy_cave_floor.png",
    "cave_water_pool_real": "assets/tiles/caves/cave_water_pool.png",
    "cave_moss_clump_real": "assets/tiles/caves/cave_moss_clump.png",
    "cave_rubble_floor": "assets/tiles/caves/rubble_strewn_floor.png",
    # The Den's real wall art (this session) - was cave_wall_1/2, an
    # 83x132 tall narrow stalactite-formation crop force-squashed into a
    # 32x32 square, producing a visible vertical cross-hatch/aliasing
    # pattern once actually rendered (confirmed via screenshot, not
    # assumed from the aspect ratio alone). Same ChatGPT-sourced batch as
    # the floor chunks, square 627x627, no baked border, verified
    # seamless via 3x3 self-tile preview before use.
    "den_wall_a": "assets/tiles/the_den/cave_wall_chunk_a.png",
    "den_wall_b": "assets/tiles/the_den/cave_wall_chunk_b.png",
    # Orgrimmar city surfaces - real paved-courtyard art for district
    # plazas ("stone" tile_id), distinct from the red-sand ground shared
    # with Durotar (Orgrimmar keeps that palette for its own "sand"/"dirt"
    # since it's carved into the same canyon per the zone's own
    # description - only the worked/paved city surface gets a different
    # texture, not the whole biome).
    "orgrimmar_courtyard_stone": "assets/tiles/orgrimmar/courtyard_stone.png",
    "orgrimmar_fortress_wall": "assets/tiles/orgrimmar/fortress_wall_1.png",
    "fm_tileset": "assets/tiles/forgotten_memories/TileSet.png",
    "fm_water": "assets/tiles/forgotten_memories/WaterTiles-6frames.png",
    "fm_trees": "assets/tiles/forgotten_memories/Trees.png",
    "fm_props": "assets/tiles/forgotten_memories/Props.png",
    "undead_ground": "assets/tiles/undead/Ground_rocks.png",
    "undead_objects": "assets/tiles/undead/Objects.png",
    "caves": "assets/tiles/caves/MainLev2.0.png",
    "water_ice": "assets/tiles/water_ice_sheet.png",
    "topdown_forest": "assets/tiles/topdown_forest/Tileset.png",
    "topdown_forest_deco": "assets/tiles/topdown_forest/Decorations.png",
    "tf_jungle": "assets/tiles/tf_jungle/tf_jungle_tileset.png",
    "damp_dungeons": "assets/tiles/damp_dungeons/Dungeon_WallsAndFloors.png",
    "swamp": "assets/tiles/swamp/tiles/Tile_32.png",
    "damp_dungeons_deco": "assets/tiles/damp_dungeons/DungeonDecorations.png",
    "props_nature": "assets/tiles/props_nature/plants_rocks_food.png",
    "lava": "assets/tiles/lava/freelavatileset-Sheet.png",
    "resurrected_rpg_props": "assets/tiles/resurrected_rpg/Props.png",
    # Paved-road pack (5 palettes: stone/brick/slate/terracotta/cobble) -
    # was sitting unextracted inside the source zip, never wired in. Built
    # for settlement streets (Orgrimmar, town squares), not rustic dirt
    # trails - see NOTES.md "road pack" for why Valley of Trials' own path
    # uses plain sand instead of this.
    "road_stone": "assets/tiles/roads/Road1_stone_ground.png",
    "road_brick": "assets/tiles/roads/Road2_brick_ground.png",
    "road_slate": "assets/tiles/roads/Road3_slate_ground.png",
    "road_terracotta": "assets/tiles/roads/Road4_terracotta_ground.png",
    "road_cobble": "assets/tiles/roads/Road5_cobble_ground.png",
    # Desert rock-pile props (warm tan/orange, individually cropped by the
    # source pack rather than sliced from a grid sheet - each is already a
    # standalone prop with a transparent background). Replaces the old flat
    # gray "small_rocks" crop (props_nature sheet), which was the wrong
    # temperature/tone for a desert biome and read as a generic blob.
    "rock_pile_orange_1": "assets/tiles/rocks/rock_pile_orange/1_small.png",
    "rock_pile_orange_2": "assets/tiles/rocks/rock_pile_orange/2_small.png",
    "rock_pile_orange_3": "assets/tiles/rocks/rock_pile_orange/3_small.png",
    "rock_pile_orange_4": "assets/tiles/rocks/rock_pile_orange/4_small.png",
    # Cave feature props (bones/crystal) - real cluster art instead of
    # reusing generic small_rocks for every feature tag. See zone_generator
    # .py's feature_tiles table for where these actually get scattered.
    "cave_bones_1": "assets/tiles/cave_props/bones_1.png",
    "cave_bones_2": "assets/tiles/cave_props/bones_2.png",
    "cave_bones_3": "assets/tiles/cave_props/bones_3.png",
    "cave_bones_4": "assets/tiles/cave_props/bones_4.png",
    "cave_crystal_1": "assets/tiles/cave_props/crystal_1.png",
    "cave_crystal_2": "assets/tiles/cave_props/crystal_2.png",
    "cave_crystal_3": "assets/tiles/cave_props/crystal_3.png",
    "cave_skull_door_1": "assets/tiles/cave_props/skull_door_1.png",
    "cave_skull_door_2": "assets/tiles/cave_props/skull_door_2.png",
    # Vegetation variety (real bushes/ferns/cacti/trees) - was leaning on
    # 4 rock-pile sprites as the only scatter option everywhere.
    "veg_cactus_1": "assets/tiles/vegetation/cactus_1.png",
    "veg_cactus_2": "assets/tiles/vegetation/cactus_2.png",
    "veg_bush_1": "assets/tiles/vegetation/bush_1.png",
    "veg_bush_2": "assets/tiles/vegetation/bush_2.png",
    "veg_fern_1": "assets/tiles/vegetation/fern_1.png",
    "veg_fern_2": "assets/tiles/vegetation/fern_2.png",
    "veg_oak_tree": "assets/tiles/vegetation/oak_tree_1.png",
    "veg_palm_tree": "assets/tiles/vegetation/palm_tree_1.png",
    # Cave landmark props - dedicated identity pieces beyond bones/crystal.
    "cave_bonfire": "assets/tiles/cave_landmarks/bonfire.png",
    "cave_dark_totem": "assets/tiles/cave_landmarks/dark_totem.png",
    "cave_fire_gate": "assets/tiles/cave_landmarks/fire_gate.png",
    "cave_entrance_deco": "assets/tiles/cave_landmarks/cave_entrance.png",
    "cave_statue_head": "assets/tiles/cave_landmarks/statue_head.png",
    "cave_dragon_bones": "assets/tiles/cave_landmarks/dragon_bones.png",
    "cave_dino_skeleton": "assets/tiles/cave_landmarks/dino_skeleton.png",
    # Seabed decoration for Echo Isles / Sunken Temple Grotto.
    "seabed_coral_blue": "assets/tiles/seabed/coral_blue.png",
    "seabed_coral_pink": "assets/tiles/seabed/coral_pink.png",
    "seabed_coral_red": "assets/tiles/seabed/coral_red.png",
    "seabed_shell_pearl": "assets/tiles/seabed/shell_pearl.png",
    "seabed_shell_brown": "assets/tiles/seabed/shell_brown.png",
    # Naga sea-cave dungeon (Durotar NE, Kyle: "the game's first custom
    # mini-dungeon") - real sourced monster/ruin props, not generic scatter.
    "naga_statue": "assets/tiles/naga_dungeon/naga_statue.png",
    "naga_serpent_skeleton": "assets/tiles/naga_dungeon/serpent_skeleton.png",
    "naga_shipwreck": "assets/tiles/naga_dungeon/shipwreck.png",
    "naga_giant_crab": "assets/tiles/naga_dungeon/giant_crab.png",
    # Ruined-structure props (Tiragarde Keep - "ruined fortress" per Kyle,
    # not a natural cave). Standalone broken-wall/pillar-fragment pieces,
    # not a tileable ground set, so these are visual-layer scatter on top
    # of a normal walkable floor/wall biome, same pattern as bones/crystal.
    "ruin_1": "assets/tiles/ruins/ruin_1.png",
    "ruin_2": "assets/tiles/ruins/ruin_2.png",
    "ruin_3": "assets/tiles/ruins/ruin_3.png",
    "ruin_4": "assets/tiles/ruins/ruin_4.png",
    "ruin_5": "assets/tiles/ruins/ruin_5.png",
    # Baked/tinted stand-in tiles (no source pack had a real match) - see
    # tools/tile_mapping/NOTES.md "red sand tint" for how/why these exist.
    "gen_red_sand": "assets/tiles/generated/durotar_red_sand.png",
    "gen_sand_path": "assets/tiles/generated/durotar_sand_path.png",
    "gen_red_rock": "assets/tiles/generated/durotar_red_rock.png",
    # Darker, desaturated variant of the same rock tile - used for
    # "wall"/"cliff" tile_ids specifically. The plain gen_red_rock and
    # gen_red_sand stand-ins are too close in hue/brightness to read as
    # different materials at a glance (avg (143,80,52) vs (164,90,50) -
    # a wall built from this rock was disappearing into the sand floor
    # next to it, confirmed via screenshot in Orgrimmar). This variant
    # is ~45% darker plus desaturated (avg (80,51,39)) - clearly a
    # different, shadowed material while staying in the same warm
    # red-brown family, not a jarring unrelated color.
    "gen_red_rock_dark": "assets/tiles/generated/durotar_red_rock_dark.png",
    "gen_cave_cold_floor": "assets/tiles/generated/cave_cold_floor.png",
    "gen_cave_cold_wall": "assets/tiles/generated/cave_cold_wall.png",
    # Real Barrens-specific ground/prop art (this session) - replaces the
    # savanna biome's earlier generic stand-ins (fm_tileset grass crop,
    # undead_ground rock/cliff, props_nature bare tree). 15 genuinely
    # distinct seamless grass/scrub textures (edge-blended, verified via
    # 3x3 self-tile render - two of the fifteen had a faint seam pre-blend,
    # fixed with a 20px crossfade on all four edges) plus real acacia
    # tree, barrens cactus, kodo skull, and 5 mountain silhouette variants
    # cropped from a ChatGPT-generated alpha-transparent sheet (confirmed
    # real alpha, not a baked white bg - corner pixel sampled alpha=0).
    "barrens_grass_dry_sparse": "assets/tiles/barrens/grass/dry_grass_sparse.png",
    "barrens_grass_dry_dense": "assets/tiles/barrens/grass/dry_grass_dense.png",
    "barrens_grass_low_bushes": "assets/tiles/barrens/grass/grass_low_bushes.png",
    "barrens_scrub_brush": "assets/tiles/barrens/grass/scrub_brush.png",
    "barrens_grass_tall_dry": "assets/tiles/barrens/grass/tall_dry_grass.png",
    "barrens_grass_with_rocks": "assets/tiles/barrens/grass/grass_with_rocks.png",
    "barrens_thorny_brush": "assets/tiles/barrens/grass/thorny_brush.png",
    "barrens_red_grass_mix": "assets/tiles/barrens/grass/red_grass_mix.png",
    "barrens_low_scrub_bushes": "assets/tiles/barrens/grass/low_scrub_bushes.png",
    "barrens_sparse_grass": "assets/tiles/barrens/grass/sparse_grass.png",
    "barrens_grass_clumps": "assets/tiles/barrens/grass/grass_clumps.png",
    "barrens_mixed_grass_sage": "assets/tiles/barrens/grass/mixed_grass_sage.png",
    "barrens_overgrown_brush": "assets/tiles/barrens/grass/overgrown_brush.png",
    "barrens_grass_with_flowers": "assets/tiles/barrens/grass/grass_with_flowers.png",
    "barrens_windswept_grass": "assets/tiles/barrens/grass/windswept_grass.png",
    "barrens_acacia_tree": "assets/tiles/barrens/props/acacia_tree.png",
    "barrens_cactus": "assets/tiles/barrens/props/barrens_cactus.png",
    "barrens_kodo_skull": "assets/tiles/barrens/props/kodo_skull.png",
    "barrens_mountain_peak": "assets/tiles/barrens/props/mountain_peak.png",
    "barrens_mountain_rock": "assets/tiles/barrens/props/mountain_rock.png",
    "barrens_mountain_cliff": "assets/tiles/barrens/props/mountain_cliff.png",
    "barrens_mountain_hill": "assets/tiles/barrens/props/mountain_hill.png",
    "barrens_rock_outcrop": "assets/tiles/barrens/props/rock_outcrop.png",
    # Oasis water - real still-pond art (reused from the Durotar drop, see
    # that SHEETS block's comment) instead of the generic water_ice sheet
    # the savanna biome was pointed at before. Shallow is a brightness/
    # saturation-adjusted variant of the same source (no second source
    # asset exists) so shallow/deep read as the same water at different
    # depth rather than two unrelated materials - flagged here as a
    # derived variant, not separately-sourced art.
    "barrens_oasis_deep_water": "assets/tiles/barrens/oasis_deep_water.png",
    "barrens_oasis_shallow_water": "assets/tiles/barrens/oasis_shallow_water.png",
}

# ---------------------------------------------------------------------------
# Biomes. A zone name (Tilemap.name, e.g. "Undercity", "Ashenvale West")
# maps to a biome_id here; the biome_id selects which texture set a tile_id
# resolves to. Zones not listed fall back to "default", which currently
# uses grassland textures where available and None (flat color) elsewhere.
#
# Only biomes with confirmed, checked assets are wired below. Savanna/
# oasis, tropical, port-town, and Orgrimmar urban-stone are deliberately
# left unmapped (-> default -> flat color) rather than faked with a
# mismatched pack. See NOTES.md "unconfirmed biomes" for what's missing.
# ---------------------------------------------------------------------------
ZONE_BIOME = {
    # Desert / red-sand (Valley of Trials, Durotar, Razor Hill) - the
    # actual WoW palette per Kyle's reference art is red sand + rust rock,
    # NOT green grass. These use baked/tinted crops (see
    # assets/tiles/generated/ + tools/tile_mapping/NOTES.md "red sand
    # tint") since no source pack shipped a genuine red-sand texture -
    # flagged as a stand-in, not a purpose-made asset.
    "Valley of Trials": "desert_oasis",
    "Durotar": "desert",
    "Razor Hill": "desert",

    # Mythical forest (Ashenvale) - reuses Forgotten Memories' tree color
    # variants (teal/gold "fantasy" trees) for the sparkle/beauty read Kyle
    # asked for, plus Resurrected RPG's sandstone ruins props.
    "Ashenvale West": "mythical_forest",
    "Ashenvale East": "mythical_forest",
    "Astranaar": "mythical_forest",
    "Zoram Strand": "mythical_forest",
    "Splintertree Post": "mythical_forest",

    # Decayed forest (Silverpine + Tirisfal undead-starting-area zones) -
    # darker Forgotten Memories tree variant (orange/dark), desaturated
    # ruins reusing the same Resurrected RPG props at lower "life".
    "Silverpine North": "decayed_forest",
    "Silverpine South": "decayed_forest",
    "The Sepulcher": "decayed_forest",
    "Fenris Isle": "decayed_forest",
    "Deathknell": "decayed_forest",
    "Eastern Tirisfal": "decayed_forest",
    "Western Tirisfal": "decayed_forest",
    "Brill": "decayed_forest",

    # Undead capital - the undead/ ash-ground pack directly
    "Undercity": "undead",

    # Orgrimmar - urban capital, carved into red rock canyon (same
    # geology as surrounding Durotar - it's built INTO the rock per WoW's
    # actual geography, not a separate gray-stone city dropped in).
    "Orgrimmar": "orgrimmar",

    # Tropical (Echo Isles) - tf_jungle pack: vivid grass, canopy trees,
    # calm teal pond water (no wave animation, matches Kyle's "not active
    # looking" note for still water bodies).
    "Echo Isles": "tropical",

    # Savanna/scrubland (The Barrens - Central/Northern/Southern, Crossroads,
    # Camp Taurajo). Ratchet (port town) and Orgrimmar (urban capital) are
    # still deliberately unmapped - see NOTES.md "unconfirmed biomes".
    "The Barrens": "savanna",
    "Central Barrens": "savanna",
    "Northern Barrens": "savanna",
    "Southern Barrens": "savanna",
    "Crossroads": "savanna",
    "Camp Taurajo": "savanna",
}

# Dungeons key off a separate lookup since they're generated via
# generate_cave(theme=...) rather than a fixed zone name - ZoneManager
# marks tilemap.is_cave True for these. tilemap_renderer checks this dict
# by tilemap.name for caves specifically (dungeon names are distinct
# enough there's no collision with the overworld zone list above).
CAVE_BIOME = {
    "Ragefire Chasm": "cave_warm",       # caves_rpgw green/warm variant
    "Plague Depths": "cave_sick",        # caves_rpgw purple/wine variant
    "Blackfathom Deeps": "cave_cold",    # caves_rpgw blue-gray variant
    "Grom's Rest": "cave_warm",
    "Widow's Lair": "cave_dark",         # caves_rpgw dark ash variant
    "Shadowfang Keep": "cave_dark",
    "Ambermill Tower": "cave_warm",
    "Shadowpine Altar": "cave_sick",

    # Small named caves tied to specific overworld zones (see
    # world/zone_generator.py cave_specs) - themed to match their parent
    # zone rather than reusing the generic caves_rpgw palette everywhere.
    # Valley of Trials / Durotar caves -> DampDungeons' warm stone (still
    # reads as "cave", not literally red, but pairs better with a desert
    # exterior than caves_rpgw's cooler tones did).
    "The Den": "cave_mossy",
    "Burning Blade Coven": "cave_demonic",
    "Drygulch Ravine": "cave_canyon",
    "Skull Rock": "cave_demonic",
    "Tiragarde Keep": "cave_dark",
    "Dustwind Cave": "cave_dustwind",
    # Echo Isles caves - flooded/roots per their cave_specs feature tags,
    # DampDungeons' mossy stone fits a damp tropical cave better than a
    # dry desert or ash-cave palette would.
    "Sunken Temple Grotto": "cave_flooded_ruins",
    "Zalazane's Hollow": "cave_troll_ruins",
    "Sunken Grotto of the Deep": "cave_naga",

    # Wailing Caverns - lush, waterlogged, nightmare-corrupted swamp
    # cavern (per the generator's own flavour text: "waterlogged and
    # overgrown"). Deliberately distinct from cave_mossy (DampDungeons'
    # warm dry stone) - this needs to read wet/fungal, not desert-adjacent.
    "Wailing Caverns": "cave_swamp",

    # Razorfen Kraul - quilboar thorn-tunnel dungeon. Dry packed dirt +
    # gray rock walls + dense bramble, matching the Razorfen Approach
    # overworld subzone it connects from (savanna_thornscrub).
    "Razorfen Kraul": "cave_thornscrub",
}

DEFAULT_BIOME = "grassland"

# ---------------------------------------------------------------------------
# Subzone overrides. Named sub-regions inside a zone - registered via
# Tilemap.add_subzone(), same mechanism the encounter-table system already
# uses - that should read visually distinct from their parent zone's biome,
# not just have different creature/prop scatter. Keyed by subzone display
# name (Tilemap.get_subzone_at()["name"]), checked BEFORE the parent
# ZONE_BIOME/CAVE_BIOME lookup. A subzone with no entry here falls through
# to the parent zone's biome unchanged - adding a subzone rect for
# encounter-table purposes never silently changes its look.
#
# IMPORTANT: keys are matched by NAME ONLY, not by which zone registered
# them - if two different zones both register a subzone called "X", both
# get the same override. This is how Field of Giants/Razorfen Approach
# ended up correctly textured in the LIVE "Southern Barrens" zone despite
# being originally built against the old standalone "The Barrens" zone
# (world/zone_generator.py's generate_the_barrens - defined but never
# called from create_all_zones, i.e. dead code, unreachable in-game). Kyle
# flagged this ambiguity - verify with get_subzone_biome() against the
# actual live zone before assuming a mapping applies, don't just check the
# name exists here.
# ---------------------------------------------------------------------------
SUBZONE_BIOME = {
    # Field of Giants - kodo bone fields / silithid country. No sourced pack
    # has real bone-pile or insect-mound art (checked props_nature, undead,
    # topdown_forest - nothing fits), so this reuses the same gray boulder
    # crop as small_rocks game-wide as a STAND-IN scatter, not real bone
    # art - see NOTES.md "Field of Giants bone stand-in" if a real pack
    # shows up later. Ground stays plain "savanna", not a fake bone-ground
    # biome - only the visual-layer scatter is denser/different here.
    # Live in Southern Barrens (generate_southern_barrens).
    "Field of Giants": "savanna_bones",
    # Witchwing Terrace - elevated, cliff-ringed plateau. DEAD MAPPING as
    # of this writing - only ever registered inside generate_the_barrens()
    # (world/zone_generator.py), which is never called from
    # create_all_zones(). No live zone currently has a subzone by this
    # name, so this entry does nothing in the actual game right now. Left
    # in rather than deleted in case that zone gets wired up later, but
    # don't assume it's doing anything without checking.
    "Witchwing Terrace": "savanna_cliff",
    # Razorfen Approach - dense thorn scrub leading into Razorfen Kraul.
    # Darker, denser ground foreshadowing the dungeon below. Live in
    # Southern Barrens (generate_southern_barrens).
    "Razorfen Approach": "savanna_thornscrub",

    # Barrens oases - real tropical grass/palm read instead of dry savanna
    # scrub leaking into a supposed water pocket. All 3 live in Central
    # Barrens (generate_central_barrens); matched by name so if either
    # Northern or Southern Barrens ever register an oasis with one of
    # these exact names, it gets the same treatment automatically.
    "Lushwater Oasis": "savanna_oasis",
    "The Forgotten Pools": "savanna_oasis",
    "Raider's Rest Oasis": "savanna_oasis",

    # ---- Added this session: live split-zone subzones that had zero
    # texture coverage (base savanna ground only, no visual identity). ----

    # Slug Fens (Northern Barrens, west) - wet muddy bog, ~40% shallow
    # water per the generator's own carve loop. Ground swaps to the same
    # swamp bog-floor tile as Wailing Caverns (open-air use, not just
    # cave-coded) - genuinely muddy/waterlogged read, distinct from open
    # savanna. Water uses the textured wavy water_ice crop, not the flat
    # calm-pond fill - same reasoning as Wailing Caverns: the flat crop
    # reads as an unmapped color at this water density, not as a puddle.
    "Slug Fens": "barrens_fen",
    # Harpy Roost (Northern Barrens, north) - rocky cliffs, dense "rock"
    # collision clusters per the generator. Ground swaps to gray stone so
    # the whole roost reads as rocky terrain underfoot, not savanna dirt
    # with rock scatter on top.
    "Harpy Roost": "savanna_cliff",

    # Central Barrens' three oases (Lushwater, Forgotten Pools, Raider's
    # Rest) - see "savanna_oasis" SUBZONE_BIOME entry above (this session,
    # Kyle: "fix up the oasis subzones to be tropical") for the live
    # mapping. This zone used to point these 3 names at "savanna_pond"
    # (generic savanna grass + textured-but-still-savanna water) - that
    # biome block still exists below but is now orphaned/unreferenced,
    # left in rather than deleted in case anything else keys off it
    # later, per the same "don't assume, verify" caution as the
    # Witchwing Terrace dead-mapping note above.
    
    # Kolkar Plains (Central Barrens) - deliberately NOT given a distinct
    # biome. The generator's own comment says this is open savanna with no
    # special terrain, only placed for encounter-table/lore purposes
    # (Kolkar centaur camps) - texturing it differently would misrepresent
    # what's actually there. Plain "savanna" (the parent zone's biome) is
    # correct and intentional, not a coverage gap.

    # Bael Modan (Southern Barrens, NW) - dwarf excavation ruins. "stone"
    # base ground (elliptical dig site) ringed by "rock" collision. Ground
    # reuses the same neutral gray stone as savanna_cliff/Harpy Roost
    # (proven tileable, consistent "generic rock" language game-wide)
    # rather than resurrected_rpg's prop sheet, which has real ruins
    # material (sandstone obelisks, cracked angel statues, rubble) but
    # isn't a tileable ground texture - used instead as visual-layer
    # rubble scatter on top, for genuine "excavated ruins" character
    # beyond just "rocky area" (which Harpy Roost already covers).
    "Bael Modan": "bael_modan",
}




def get_subzone_biome(tilemap, x, y):
    """Return a subzone-specific biome_id for this tile if one is mapped,
    else None. Callers fall back to the parent zone's biome on None -
    this is purely an override layer, never a replacement for ZONE_BIOME."""
    get_subzone_at = getattr(tilemap, "get_subzone_at", None)
    if not get_subzone_at:
        return None
    subzone = get_subzone_at(x, y)
    if not subzone:
        return None
    return SUBZONE_BIOME.get(subzone["name"])


# ---------------------------------------------------------------------------
# Per-biome tile_id -> (sheet_key, rect, smooth?) mapping.
# rect = (x, y, w, h) in source sheet pixels. smooth=True routes through
# get_tile_sprite_smooth (bilinear) - used only for the high-res Forgotten
# Memories sheets being downscaled; everything else stays crisp
# nearest-neighbor (smooth=False, the default when omitted).
#
# Not every tile_id needs an entry per biome - unmapped tile_ids fall back
# to tiles.py's flat color automatically, so partial biome coverage is
# safe and expected (e.g. no biome currently maps "lava" or "boat").
# ---------------------------------------------------------------------------
BIOME_TILES = {
    "desert": {
        # Real Durotar ground art (was gen_red_sand/gen_red_rock, baked
        # tints flagged in NOTES.md as stand-ins since "no source pack
        # shipped a genuine red-sand texture" - a real one exists now,
        # see SHEETS' durotar_* entries above). Each entry below is a
        # LIST of real variants, not one fixed texture (Kyle: "I don't
        # want one uniform tile across the board" - the first pass of
        # this fix mapped exactly one crop per tile_id despite having
        # 3 real cracked-earth variants and 2 real rocky-ground variants
        # on hand, which produced an obvious grid-repeat pattern once
        # actually rendered). get_texture_entry picks a variant
        # deterministically per tile position, not randomly per frame.
        "sand": [
            ("durotar_cracked_red_earth_a", (0, 0, 113, 118), True),
            ("durotar_cracked_red_earth_b", (0, 0, 116, 118), True),
            ("durotar_cracked_red_earth_c", (0, 0, 115, 118), True),
            ("durotar_pebble_strewn_red_earth", (0, 0, 138, 165), True),
            ("durotar_sun_bleached_red_clay", (0, 0, 139, 165), True),
        ],
        "dirt": [
            ("durotar_cracked_red_earth_b", (0, 0, 116, 118), True),
            ("durotar_cracked_red_earth_c", (0, 0, 115, 118), True),
            ("durotar_red_earth_to_dry_grass", (0, 0, 111, 118), True),
            ("durotar_red_rock_rubble_patch", (0, 0, 138, 165), True),
        ],
        "path": ("durotar_sun_bleached_path_dirt", (0, 0, 115, 118), True),
        # "stone"/"rock" now pull from the second art drop's real ground
        # set (cracked red rock A/B, smooth sandstone, rust-streaked rock)
        # instead of reusing the same rocky_red_ground crop both tile_ids
        # already shared - more real variety, not the same 2 textures
        # doing double duty everywhere.
        "stone": [
            ("durotar_rocky_red_ground_a", (0, 0, 113, 118), True),
            ("durotar_cracked_red_rock_a", (0, 0, 138, 165), True),
            ("durotar_smooth_red_sandstone", (0, 0, 138, 165), True),
        ],
        "rock": [
            ("durotar_cracked_red_rock_b", (0, 0, 139, 165), True),
            ("durotar_rust_streaked_rock", (0, 0, 138, 165), True),
            ("durotar_rocky_red_ground_b", (0, 0, 117, 118), True),
        ],
        # "wall"/"cliff" now use the real mountain rock-face/boulder-wall
        # art (second drop) instead of the flat red_earth_to_stone crop -
        # a genuine cliff material, not ground art doing double duty as a
        # wall texture.
        "wall": [
            ("vot_cliff_wall_a", (0, 0, 627, 627), True),
            ("vot_cliff_wall_b", (0, 0, 627, 627), True),
        ],
        "cliff": [
            ("vot_cliff_wall_b", (0, 0, 627, 627), True),
            ("vot_cliff_wall_a", (0, 0, 627, 627), True),
        ],
        # Calm oasis-style water crop (real art, replaces the fm_water
        # sheet reference which - like every other SHEETS entry before
        # this session's Durotar/cave/Orgrimmar pass - pointed at a file
        # that was never actually added to assets/tiles/).
        "shallow_water": ("vot_oasis_shallow_water", (0, 0, 627, 627), True),
        "deep_water": ("vot_oasis_deep_water", (0, 0, 627, 627), True),
        # "tree" - Kyle: "remove the ugly grey rocks scattered everyone
        # and the ugly trees" - was a single reused thornbush crop. Now
        # the tall saguaro as the default "tree" collision-layer read
        # (Durotar has no real trees per the reference art, a saguaro is
        # the closest thing to a tall desert landmark), with the barrel
        # cactus and prickly-pear cluster as real alternate silhouettes
        # so a scatter pass doesn't stamp one identical cactus everywhere.
        "tree": [
            ("durotar_tall_saguaro_cactus", (0, 0, 154, 257), True),
            ("durotar_barrel_cactus", (0, 0, 164, 145), True),
            ("durotar_prickly_scrub_cactus", (0, 0, 161, 190), True),
        ],
        # All 5 non-saguaro cacti/scrub variants scattered across
        # small_rocks/bushes (Kyle: "all 5 cacti variation can be
        # scattered") - was the rocky-ground crop reused as fake
        # "small_rocks" scatter, a real material mismatch (ground texture
        # standing in for a rock prop). Real desert plant variety now.
        "small_rocks": [
            ("durotar_barrel_cactus", (0, 0, 164, 145), True),
            ("durotar_hardy_desert_shrub", (0, 0, 151, 184), True),
            ("durotar_dead_scrub_twig", (0, 0, 141, 177), True),
        ],
        "bushes": [
            ("durotar_dry_thornbush", (0, 0, 156, 203), True),
            ("durotar_hardy_desert_shrub", (0, 0, 151, 184), True),
            ("durotar_prickly_scrub_cactus", (0, 0, 161, 190), True),
            ("durotar_dead_scrub_twig", (0, 0, 141, 177), True),
        ],
    },
    # Valley of Trials specifically - same red-sand ground as "desert" but
    # with a calm, non-animated pond (Kyle: ponds shouldn't look "active").
    # Everything else identical to "desert", including the same real
    # multi-variant texture lists (not one uniform tile) - only water
    # differs.
    "desert_oasis": {
        "sand": [
            ("durotar_cracked_red_earth_a", (0, 0, 113, 118), True),
            ("durotar_cracked_red_earth_b", (0, 0, 116, 118), True),
            ("durotar_cracked_red_earth_c", (0, 0, 115, 118), True),
            ("durotar_pebble_strewn_red_earth", (0, 0, 138, 165), True),
            ("durotar_sun_bleached_red_clay", (0, 0, 139, 165), True),
        ],
        "dirt": [
            ("durotar_cracked_red_earth_c", (0, 0, 115, 118), True),
            ("durotar_red_earth_to_dry_grass", (0, 0, 111, 118), True),
            ("durotar_red_rock_rubble_patch", (0, 0, 138, 165), True),
        ],
        "path": ("durotar_sun_bleached_path_dirt", (0, 0, 115, 118), True),
        "stone": [
            ("durotar_rocky_red_ground_a", (0, 0, 113, 118), True),
            ("durotar_cracked_red_rock_a", (0, 0, 138, 165), True),
            ("durotar_smooth_red_sandstone", (0, 0, 138, 165), True),
        ],
        "rock": [
            ("durotar_cracked_red_rock_b", (0, 0, 139, 165), True),
            ("durotar_rust_streaked_rock", (0, 0, 138, 165), True),
            ("durotar_rocky_red_ground_b", (0, 0, 117, 118), True),
        ],
        "wall": [
            ("durotar_mountain_rock_face_a", (0, 0, 184, 285), True),
            ("durotar_boulder_wall", (0, 0, 186, 285), True),
        ],
        "cliff": [
            ("durotar_mountain_rock_face_b", (0, 0, 184, 285), True),
            ("durotar_mountain_scree_slope", (0, 0, 183, 285), True),
        ],
        "tree": [
            ("durotar_tall_saguaro_cactus", (0, 0, 154, 257), True),
            ("durotar_barrel_cactus", (0, 0, 164, 145), True),
            ("durotar_prickly_scrub_cactus", (0, 0, 161, 190), True),
        ],
        "small_rocks": [
            ("durotar_barrel_cactus", (0, 0, 164, 145), True),
            ("durotar_hardy_desert_shrub", (0, 0, 151, 184), True),
            ("durotar_dead_scrub_twig", (0, 0, 141, 177), True),
        ],
        "bushes": [
            ("durotar_dry_thornbush", (0, 0, 156, 203), True),
            ("durotar_hardy_desert_shrub", (0, 0, 151, 184), True),
            ("durotar_prickly_scrub_cactus", (0, 0, 161, 190), True),
            ("durotar_dead_scrub_twig", (0, 0, 141, 177), True),
        ],
        # Real cropped oasis-water art (was the missing fm_water sheet
        # reference).
        "shallow_water": ("durotar_oasis_water", (0, 0, 83, 132), True),
        "deep_water": ("durotar_oasis_water", (0, 0, 83, 132), True),
    },
    # Orgrimmar - urban capital carved into red rock, same canyon as
    # Durotar per the zone's own description. Ground/rock now uses the
    # real Durotar terrain art (was gen_red_sand/gen_red_rock baked tints,
    # same gap as Durotar itself - see that biome's comment above). "stone"
    # specifically gets real paved-courtyard art (district plazas are a
    # genuinely worked city surface, not raw ground) rather than reusing
    # the rocky-ground crop - the one real material difference between
    # "this is Orgrimmar's built city" and "this is the surrounding desert".
    "orgrimmar": {
        # "stone" was wired to a genuinely wrong asset - courtyard_stone.png
        # turned out to be a wall banner/tapestry sprite (red Horde banner
        # on a wall backdrop), not ground texture at all. Caught by
        # rendering an actual screenshot (Kyle: "org floors are fucked
        # up") and then opening the source file directly rather than
        # trusting the variable name. No real Orgrimmar courtyard/paving
        # art is sourced yet (checked every file in assets/tiles/orgrimmar/
        # - only 2 exist: this mistaken one and a genuine fortress wall
        # texture, correctly used for "wall" below). Falling back to
        # Durotar's real rocky-ground variant list rather than leaving
        # the wrong banner in or inventing a second wrong placeholder -
        # Orgrimmar sits in Durotar, so reused desert stone is at least
        # geographically honest until real paved-courtyard art is sourced.
        "stone": [
            ("durotar_rocky_red_ground_a", (0, 0, 113, 118), True),
            ("durotar_smooth_red_sandstone", (0, 0, 138, 165), True),
        ],
        "dirt": [
            ("durotar_cracked_red_earth_a", (0, 0, 113, 118), True),
            ("durotar_cracked_red_earth_b", (0, 0, 116, 118), True),
            ("durotar_red_rock_rubble_patch", (0, 0, 138, 165), True),
        ],
        "sand": [
            ("durotar_cracked_red_earth_a", (0, 0, 113, 118), True),
            ("durotar_cracked_red_earth_c", (0, 0, 115, 118), True),
            ("durotar_pebble_strewn_red_earth", (0, 0, 138, 165), True),
        ],
        "path": [
            ("durotar_packed_town_dirt_a", (0, 0, 114, 126), True),
            ("durotar_packed_town_dirt_b", (0, 0, 114, 126), True),
        ],
        "rock": [
            ("durotar_rocky_red_ground_b", (0, 0, 117, 118), True),
            ("durotar_cracked_red_rock_b", (0, 0, 139, 165), True),
        ],
        # Real mountain wall/cliff art (second drop), matching the same
        # swap made in "desert"/"desert_oasis" above - was the flat
        # red_earth_to_stone ground crop reused as a wall texture.
        "wall": [
            ("orgrimmar_fortress_wall", (0, 0, 87, 132), True),
            ("durotar_boulder_wall", (0, 0, 186, 285), True),
        ],
        "cliff": [
            ("durotar_mountain_rock_face_a", (0, 0, 184, 285), True),
            ("durotar_mountain_scree_slope", (0, 0, 183, 285), True),
        ],
    },
    "tropical": {
        "grass": ("tf_jungle", (32, 16, 16, 16), False),
        "dirt": ("tf_jungle", (272, 32, 16, 16), False),
        "tree": ("tf_jungle", (240, 80, 80, 96), False),  # single canopy tree
        "deep_forest": ("tf_jungle", (160, 208, 144, 112), False),  # giant multi-trunk tree, dense grove read
        # REAL BUG FOUND + FIXED: "fm_water" sheet key points at
        # assets/tiles/forgotten_memories/WaterTiles-6frames.png, which
        # doesn't exist on disk - the ENTIRE ocean surrounding Echo Isles
        # (zone.fill("deep_water", "base") over the whole 160x160 map, no
        # water_chunks laid down - 100% dependent on this per-tile
        # fallback) was silently rendering as flat gray/background color,
        # not the "beautiful crystal blue" Kyle asked for when this was
        # first fixed - that earlier fix pointed at the right idea (a
        # genuinely blue, non-green crop) but the file itself was never
        # real. Repointed at barrens_oasis_deep_water/shallow_water -
        # confirmed real and on disk, and confirmed genuinely blue (RGB
        # ~19,123,145 / ~50,153,175 - sampled directly, not assumed) vs.
        # tf_jungle's old rejected teal-green fill.
        "shallow_water": ("barrens_oasis_shallow_water", (0, 0, 83, 132), True),
        "deep_water": ("barrens_oasis_deep_water", (0, 0, 83, 132), True),
        # Visual-layer scatter (Kyle: "spice up the general zones with
        # props") - tropical flowers and a mossy rock cluster, both native
        # to tf_jungle so the palette matches the ground/trees already in
        # use rather than importing a mismatched pack just for these two.
        "flowers": ("tf_jungle", (17, 52, 13, 57), False),
        "small_rocks": ("tf_jungle", (16, 115, 64, 44), False),
        # Real coral/shell decoration (sourced seabed pack) for beach/shore
        # tiles near water - Echo Isles is a tropical island chain, coral
        # washed up on shore reads far better than reused jungle rock.
        "coral_blue": ("seabed_coral_blue", (0, 0, 64, 64), False),
        "coral_red": ("seabed_coral_red", (0, 0, 64, 64), False),
        "shell": ("seabed_shell_pearl", (0, 0, 32, 32), False),
        "palm_tree": ("veg_palm_tree", (0, 0, 128, 128), False),
    },
    # The Barrens - dry tan dirt + sparse yellow-sprig grass (Forgotten
    # Memories' tan dirt-patch tile, bottom-right/top-right quadrants of the
    # same source block - see NOTES.md if this needs revisiting). No real
    # acacia-tree asset exists in any sourced pack, so "tree" reuses the
    # bare gnarled tree (props_nature) already used as Durotar's "bushes" -
    # a real limitation, not a mismatch we're pretending isn't there.
    # Rock/cliff reuse the same neutral gray undead_ground crop as
    # grassland/decayed_forest for a consistent "generic outcrop" read.
    # Oasis water reuses the calm still-pond (topdown_forest) exactly like
    # desert_oasis and tropical, since Barrens oases shouldn't look "active".
    "savanna": {
        "dirt": ("fm_tileset", (1573, 447, 128, 131), True),
        # Real Barrens ground art (this session) - 15 genuinely distinct
        # seamless grass/scrub variants replacing the single generic
        # fm_tileset crop. get_texture_entry's position-hash picks a
        # variant deterministically per-tile so the ground reads as real
        # terrain variety instead of a visible repeating grid (same
        # mechanism Durotar's cracked_red_earth_a/b/c already uses).
        "grass": [
            ("barrens_grass_dry_sparse", (0, 0, 251, 251), False),
            ("barrens_grass_dry_dense", (0, 0, 251, 251), False),
            ("barrens_grass_low_bushes", (0, 0, 250, 250), False),
            ("barrens_scrub_brush", (0, 0, 251, 251), False),
            ("barrens_grass_tall_dry", (0, 0, 251, 251), False),
            ("barrens_grass_with_rocks", (0, 0, 251, 251), False),
            ("barrens_thorny_brush", (0, 0, 251, 251), False),
            ("barrens_red_grass_mix", (0, 0, 250, 250), False),
            ("barrens_low_scrub_bushes", (0, 0, 251, 251), False),
            ("barrens_sparse_grass", (0, 0, 251, 251), False),
            ("barrens_grass_clumps", (0, 0, 251, 251), False),
            ("barrens_mixed_grass_sage", (0, 0, 251, 251), False),
            ("barrens_overgrown_brush", (0, 0, 250, 250), False),
            ("barrens_grass_with_flowers", (0, 0, 251, 251), False),
            ("barrens_windswept_grass", (0, 0, 251, 251), False),
        ],
        "grass_tuft": ("barrens_grass_dry_sparse", (0, 0, 251, 251), False),
        # REAL BUG FOUND + FIXED: "stone" pointed at "undead_ground" ->
        # assets/tiles/undead/Ground_rocks.png, which doesn't exist on
        # disk (confirmed - whole undead/ folder has no Ground_rocks.png)
        # - silently fell back to tiles.py's flat gray rect, visible as a
        # gray blotch anywhere Harpy Roost's rocky-cliff subzone painted
        # "stone" tiles. Repointed at barrens_grass_with_rocks - already
        # real/registered/on-disk, already used in this same biome's
        # "grass" variant list, and thematically exact for rocky ground
        # (distinct from the deliberately-unmapped "rock"/"small_rocks"
        # scatter tile_ids just below, which Kyle asked removed outright).
        "stone": ("barrens_grass_with_rocks", (0, 0, 251, 251), False),
        # "rock" was left deliberately unmapped (Kyle: "the rocks are
        # trash, we can remove them from the Barrens" - the old generic
        # gray undead_ground/props_nature crops never matched the biome).
        # Re-requested this pass with real art now available: Harpy
        # Roost's cliffs paint ~950 "rock" collision tiles at 40% density
        # (see generate_northern_barrens), which were rendering as flat
        # gray with no mapping at all - now uses the real registered
        # Barrens rock-outcrop art (already used in this biome's "cliff"
        # list below), not the old mismatched undead/props_nature crops.
        "rock": ("barrens_mountain_rock", (0, 0, 269, 294), False),
        "small_rocks": ("barrens_rock_outcrop", (0, 0, 268, 307), False),
        "cliff": [
            ("barrens_mountain_peak", (0, 0, 263, 294), False),
            ("barrens_mountain_rock", (0, 0, 269, 294), False),
            ("barrens_mountain_cliff", (0, 0, 261, 294), False),
            ("barrens_mountain_hill", (0, 0, 259, 294), False),
            ("barrens_rock_outcrop", (0, 0, 268, 307), False),
        ],
        "tree": ("barrens_acacia_tree", (0, 0, 329, 307), False),
        "cactus": ("barrens_cactus", (0, 0, 221, 307), False),
        "bushes": ("barrens_thorny_brush", (0, 0, 251, 251), False),
        "kodo_skull": ("barrens_kodo_skull", (0, 0, 265, 294), False),
        "flowers": ("tf_jungle", (17, 52, 13, 57), False),
        "shallow_water": ("barrens_oasis_shallow_water", (0, 0, 83, 132), False),
        "deep_water": ("barrens_oasis_deep_water", (0, 0, 83, 132), False),
    },
    # Field of Giants - identical ground/water/tree to "savanna", only
    # small_rocks differs: same gray boulder crop as everywhere else, but
    # this is a real limitation flagged, not real bone/silithid-mound art
    # (none exists in any sourced pack - see SUBZONE_BIOME comment above).
    # zone_generator's existing "small_rocks" visual-layer scatter calls
    # (already placed here for the kodo bone field / silithid dressing)
    # get this stand-in automatically since they resolve through this
    # biome once the subzone override is wired into the renderer.
    "savanna_bones": {
        "dirt": ("fm_tileset", (1573, 447, 128, 131), True),
        "grass": ("fm_tileset", (1573, 319, 128, 128), True),
        "grass_tuft": ("fm_tileset", (1573, 319, 128, 128), True),
        # REAL BUG FOUND + FIXED: "undead_ground" sheet key points at
        # assets/tiles/undead/Ground_rocks.png - the whole undead/ asset
        # folder doesn't exist on disk, so every tile_id using it was
        # silently falling back to tiles.py's flat gray rect. Repointed
        # "stone"/"rock"/"wall"/"cliff" everywhere this file used
        # "undead_ground" at real, disk-verified cave floor/wall crops -
        # same fix pattern applied across every cave biome earlier this
        # session, reused here since no dedicated gray-stone Barrens/
        # grassland/undead art exists yet (real content gap for a future
        # asset pass, not fixable by repointing alone for a truly themed
        # result).
        "stone": ("cave_floor_rock_1", (0, 0, 85, 132), True),
        "rock": ("cave_wall_1", (0, 0, 83, 132), True),
        "cliff": ("cave_wall_2", (0, 0, 90, 132), True),
        "tree": ("props_nature", (310, 235, 40, 145), False),
        "bushes": ("props_nature", (310, 235, 40, 145), False),
        # Stand-in for bone piles/silithid mounds - gray boulder, not real
        # bone art. Flag stays here until a real pack is sourced.
        "small_rocks": ("props_nature", (400, 126, 101, 113), False),
        "shallow_water": ("water_ice", (36, 73, 24, 24), False),
        "deep_water": ("water_ice", (42, 73, 24, 24), False),
    },
    # Witchwing Terrace - elevated stone plateau. Base ground swaps to the
    # same gray stone used for savanna's rock/cliff, so the whole plateau
    # reads as bare stone underfoot rather than tan dirt with a stone ring.
    "savanna_cliff": {
        # Same missing "undead_ground" bug as savanna_bones above -
        # repointed at real cave floor/wall crops throughout (this biome
        # is Harpy Roost's rocky-cliff ground, so every tile_id here was
        # gray-blotching before this fix, not just "stone").
        "dirt": ("cave_floor_rock_2", (0, 0, 89, 132), True),
        "grass": ("cave_floor_rock_3", (0, 0, 88, 132), True),
        "grass_tuft": ("cave_floor_rock_2", (0, 0, 89, 132), True),
        "stone": ("cave_floor_rock_1", (0, 0, 85, 132), True),
        "rock": ("cave_wall_1", (0, 0, 83, 132), True),
        "cliff": ("cave_wall_2", (0, 0, 90, 132), True),
        "small_rocks": ("props_nature", (400, 126, 101, 113), False),
        # Added when this biome got reused for Harpy Roost (Northern
        # Barrens) - the original Witchwing Terrace context never needed
        # water (dead zone, no water in its generator), but Northern
        # Barrens' base fill rolls shallow_water game-wide including here,
        # so leaving this unmapped showed flat blue squares on the
        # otherwise-textured stone ground.
        "shallow_water": ("water_ice", (36, 73, 24, 24), False),
        "deep_water": ("water_ice", (42, 73, 24, 24), False),
    },
    # Razorfen Approach - dense thorn scrub leading into Razorfen Kraul.
    # Ground swaps to Forgotten Memories' dark-green grass variant (already
    # used for decayed_forest) to read visibly darker/denser than open
    # savanna, foreshadowing the dungeon below without needing new assets.
    "savanna_thornscrub": {
        "dirt": ("fm_tileset", (1573, 447, 128, 131), True),
        "grass": ("fm_tileset", (768, 189, 32, 32), True),
        "grass_tuft": ("fm_tileset", (768, 189, 32, 32), True),
        # Same missing "undead_ground" bug as savanna_bones above.
        "stone": ("cave_floor_rock_1", (0, 0, 85, 132), True),
        "rock": ("cave_wall_1", (0, 0, 83, 132), True),
        "cliff": ("cave_wall_2", (0, 0, 90, 132), True),
        "tree": ("props_nature", (310, 235, 40, 145), False),
        # Thorn scrub itself - zone_generator already places dense "bushes"
        # collision tiles here (see generate_the_barrens' Razorfen Approach
        # loop), this just makes sure they render as the bare-tree sprite
        # like everywhere else rather than falling back to flat color.
        "bushes": ("props_nature", (310, 235, 40, 145), False),
        "small_rocks": ("props_nature", (400, 126, 101, 113), False),
    },
    # Barrens oases (Lushwater Oasis, The Forgotten Pools, Raider's Rest
    # Oasis - all 3 in Central Barrens) - Kyle: "we need oasis grass tiles
    # and also tropical trees... likely echo island tiles." The oasis ring
    # generator (generate_central_barrens) previously set the outer ring
    # to plain "grass", which resolved through the parent "savanna" biome
    # to dry sun-baked scrub - wrong read for a water pocket meant to
    # look lush against the surrounding dead-flat savanna. Reuses
    # tf_jungle's real grass crop and the genuine veg_palm_tree art
    # already proven working in the "tropical" biome (Echo Isles) rather
    # than inventing new oasis-specific art - same palette Kyle already
    # approved for tropical water, just applied to these 3 named pockets
    # via SUBZONE_BIOME instead of a whole zone.
    "savanna_oasis": {
        "dirt": ("tf_jungle", (272, 32, 16, 16), False),
        "grass": ("tf_jungle", (32, 16, 16, 16), False),
        "grass_tuft": ("tf_jungle", (32, 16, 16, 16), False),
        "palm_tree": ("veg_palm_tree", (0, 0, 128, 128), False),
        "tree": ("veg_palm_tree", (0, 0, 128, 128), False),
        "flowers": ("tf_jungle", (17, 52, 13, 57), False),
        # Same missing "fm_water" bug as the "tropical" biome above -
        # repointed at the same real barrens_oasis_deep_water/
        # shallow_water crops (genuinely blue, confirmed on disk) rather
        # than the dead fm_water reference.
        "shallow_water": ("barrens_oasis_shallow_water", (0, 0, 83, 132), True),
        "deep_water": ("barrens_oasis_deep_water", (0, 0, 83, 132), True),
    },
    # Slug Fens (Northern Barrens). Northern Barrens' own base fill uses
    # "grass"/"dirt"/"shallow_water" (not "dirt"-primary like Central/
    # Southern Barrens), so this biome covers those specific tile_ids
    # rather than mirroring the "savanna" family's tile_id set 1:1. Ground
    # is the same swamp bog-floor tile as Wailing Caverns - genuinely
    # muddy/waterlogged, appropriate for open-air fens too, not just cave
    # interiors. Water uses the textured wavy water_ice crop, not the flat
    # calm-pond fill - the generator rolls shallow_water on ~40% of tiles
    # in this subzone, same density problem as Wailing Caverns where the
    # flat crop reads as an unmapped color rather than a puddle.
    "barrens_fen": {
        "grass": ("swamp", (0, 0, 32, 32), False),
        "dirt": ("swamp", (0, 0, 32, 32), False),
        "grass_tuft": ("swamp", (0, 0, 32, 32), False),
        "shallow_water": ("water_ice", (36, 73, 24, 24), False),
        "deep_water": ("water_ice", (42, 73, 24, 24), False),
        # Fen scrub - generator places "bushes" collision at 15% density
        # throughout. Bare-tree crop, same as every other bushes mapping.
        "bushes": ("props_nature", (310, 235, 40, 145), False),
    },
    # Central Barrens' three oases (Lushwater, Forgotten Pools, Raider's
    # Rest) - all three use the identical concentric-ring generator code
    # (deep_water core -> shallow_water -> grass fringe), so one biome
    # covers all three by name (see SUBZONE_BIOME comment). Ground/tree
    # inherit the parent "savanna" look; water uses the same textured
    # water_ice crop as everywhere else (previously the flat calm-color
    # fill - swapped for a less-bland look, single static frame so it's
    # still not "active"-looking, just has real surface detail now).
    "savanna_pond": {
        "dirt": ("fm_tileset", (1573, 447, 128, 131), True),
        "grass": ("fm_tileset", (1573, 319, 128, 128), True),
        "grass_tuft": ("fm_tileset", (1573, 319, 128, 128), True),
        "tree": ("props_nature", (310, 235, 40, 145), False),
        "shallow_water": ("water_ice", (36, 73, 24, 24), False),
        "deep_water": ("water_ice", (42, 73, 24, 24), False),
    },
    # Bael Modan (Southern Barrens) - dwarf excavation ruins. Ground is the
    # same neutral gray stone as Harpy Roost/savanna_cliff (proven
    # tileable). small_rocks swaps to a real ruins-rubble crop
    # (resurrected_rpg's sandstone rubble prop, sourced but never wired
    # into any biome before this) instead of the generic gray boulder used
    # everywhere else, for genuine "excavated dig site" character - this
    # is real art, not a stand-in flag like Field of Giants' bones.
    "bael_modan": {
        # Same missing "undead_ground" bug as savanna_bones above.
        "stone": ("cave_floor_rock_1", (0, 0, 85, 132), True),
        "rock": ("cave_wall_1", (0, 0, 83, 132), True),
        "cliff": ("cave_wall_2", (0, 0, 90, 132), True),
        "small_rocks": ("resurrected_rpg", (13, 320, 67, 80), False),
    },
    "grassland": {
        "grass": ("fm_tileset", (70, 70, 60, 60), True),
        "dirt": ("fm_tileset", (1344, 378, 32, 32), True),
        # Same missing "undead_ground" bug as savanna_bones above.
        "stone": ("cave_floor_rock_1", (0, 0, 85, 132), True),
        "shallow_water": ("water_ice", (36, 73, 24, 24), False),
        "deep_water": ("water_ice", (42, 73, 24, 24), False),
    },
    "mythical_forest": {
        "grass": ("fm_tileset", (70, 70, 60, 60), True),
        "dirt": ("fm_tileset", (1344, 378, 32, 32), True),
        "tree": ("fm_trees", (336, 0, 170, 170), True),  # teal "fantasy" tree
        "deep_forest": ("fm_trees", (0, 0, 170, 170), True),  # orange variant, dense read
        "shallow_water": ("water_ice", (36, 73, 24, 24), False),
        "deep_water": ("water_ice", (42, 73, 24, 24), False),
    },
    "decayed_forest": {
        "grass": ("fm_tileset", (768, 189, 32, 32), True),   # dark-green variant
        "dirt": ("fm_tileset", (1344, 378, 32, 32), True),
        "tree": ("fm_trees", (0, 0, 170, 170), True),        # orange/autumn = decayed read
        "deep_forest": ("fm_trees", (0, 0, 170, 170), True),
        "shallow_water": ("water_ice", (0, 104, 24, 24), False),
        "deep_water": ("water_ice", (0, 104, 24, 24), False),
    },
    "undead": {
        # Same missing "undead_ground" bug as savanna_bones above - the
        # irony being this is the ONE biome literally named for that
        # sheet. No real Undercity/Plaguelands-themed art has ever been
        # sourced (whole undead/ asset folder is missing) - repointed at
        # the neutral gray cave floor/wall crops as a working stand-in,
        # same as everywhere else in this pass. A real decayed/diseased-
        # ground texture is still a genuine content gap for later.
        "stone": ("cave_floor_rock_1", (0, 0, 85, 132), True),
        "dirt": ("cave_floor_rock_2", (0, 0, 89, 132), True),
        "wall": ("cave_wall_1", (0, 0, 83, 132), True),
        "cliff": ("cave_wall_2", (0, 0, 90, 132), True),
        "deep_water": ("water_ice", (0, 104, 24, 24), False),
    },
    "cave_warm": {
        "bones": ("cave_bones_1", (0, 0, 32, 32), False),
        "bones_2": ("cave_bones_2", (0, 0, 64, 64), False),
        "bones_3": ("cave_bones_3", (0, 0, 32, 32), False),
        "crystal": ("cave_crystal_1", (0, 0, 64, 64), False),
        "crystal_2": ("cave_crystal_2", (0, 0, 64, 64), False),
        # REAL BUG: "caves" sheet key points at assets/tiles/caves/
        # MainLev2.0.png, which doesn't exist on disk - every tile using
        # it was silently falling back to tiles.py's flat solid-color
        # rect (no error, just a flat-looking room). Repointed at the
        # real, disk-verified cave_floor_rock_*/cave_wall_* crops (same
        # files cave_mossy already uses successfully below). Ragefire
        # Chasm and Ambermill Tower use this biome.
        "stone": [
            ("cave_floor_rock_1", (0, 0, 85, 132), True),
            ("cave_floor_rock_2", (0, 0, 89, 132), True),
            ("cave_floor_rock_3", (0, 0, 88, 132), True),
        ],
        "dirt": [
            ("cave_floor_rock_2", (0, 0, 89, 132), True),
            ("cave_floor_rock_3", (0, 0, 88, 132), True),
        ],
        "rock": [
            ("cave_wall_1", (0, 0, 83, 132), True),
            ("cave_wall_2", (0, 0, 90, 132), True),
        ],
        "wall": [
            ("cave_wall_2", (0, 0, 90, 132), True),
            ("cave_wall_1", (0, 0, 83, 132), True),
        ],
        "cliff": ("cave_wall_1", (0, 0, 83, 132), True),
    },
    "cave_sick": {
        "bones": ("cave_bones_1", (0, 0, 32, 32), False),
        "bones_2": ("cave_bones_2", (0, 0, 64, 64), False),
        "bones_3": ("cave_bones_3", (0, 0, 32, 32), False),
        "crystal": ("cave_crystal_1", (0, 0, 64, 64), False),
        "crystal_2": ("cave_crystal_2", (0, 0, 64, 64), False),
        # Plague Depths. Same missing "caves" sheet bug as cave_warm -
        # repointed at the real cave floor/wall crops.
        "stone": [
            ("cave_floor_rock_1", (0, 0, 85, 132), True),
            ("cave_floor_rock_2", (0, 0, 89, 132), True),
            ("cave_floor_rock_3", (0, 0, 88, 132), True),
        ],
        "dirt": [
            ("cave_floor_rock_2", (0, 0, 89, 132), True),
            ("cave_floor_rock_3", (0, 0, 88, 132), True),
        ],
        "rock": [
            ("cave_wall_1", (0, 0, 83, 132), True),
            ("cave_wall_2", (0, 0, 90, 132), True),
        ],
        "wall": [
            ("cave_wall_2", (0, 0, 90, 132), True),
            ("cave_wall_1", (0, 0, 83, 132), True),
        ],
        "cliff": ("cave_wall_1", (0, 0, 83, 132), True),
    },
    "cave_cold": {
        "bones": ("cave_bones_1", (0, 0, 32, 32), False),
        "bones_2": ("cave_bones_2", (0, 0, 64, 64), False),
        "bones_3": ("cave_bones_3", (0, 0, 32, 32), False),
        "crystal": ("cave_crystal_1", (0, 0, 64, 64), False),
        "crystal_2": ("cave_crystal_2", (0, 0, 64, 64), False),
        # Blackfathom Deeps. Doubly broken: "gen_cave_cold_floor"/
        # "gen_cave_cold_wall" pointed at assets/tiles/generated/
        # cave_cold_floor.png / cave_cold_wall.png - never actually
        # generated, also missing on disk. Repointed at the real cave
        # floor/wall crops (no blue-toned alternative exists yet - a real
        # content gap for later, but this at least gives Blackfathom
        # actual floor/wall texture instead of flat color).
        "stone": [
            ("cave_floor_rock_1", (0, 0, 85, 132), True),
            ("cave_floor_rock_2", (0, 0, 89, 132), True),
            ("cave_floor_rock_3", (0, 0, 88, 132), True),
        ],
        "dirt": [
            ("cave_floor_rock_2", (0, 0, 89, 132), True),
            ("cave_floor_rock_3", (0, 0, 88, 132), True),
        ],
        "rock": [
            ("cave_wall_1", (0, 0, 83, 132), True),
            ("cave_wall_2", (0, 0, 90, 132), True),
        ],
        "wall": [
            ("cave_wall_2", (0, 0, 90, 132), True),
            ("cave_wall_1", (0, 0, 83, 132), True),
        ],
        "cliff": ("cave_wall_1", (0, 0, 83, 132), True),
    },
    "cave_dark": {
        "ruin": ("ruin_3", (0, 0, 64, 64), False),
        "ruin_2": ("ruin_4", (0, 0, 48, 48), False),
        "ruin_3": ("ruin_5", (0, 0, 32, 32), False),
        "bones": ("cave_bones_1", (0, 0, 32, 32), False),
        "bones_2": ("cave_bones_2", (0, 0, 64, 64), False),
        "bones_3": ("cave_bones_3", (0, 0, 32, 32), False),
        "crystal": ("cave_crystal_1", (0, 0, 64, 64), False),
        "crystal_2": ("cave_crystal_2", (0, 0, 64, 64), False),
        # Widow's Lair, Shadowfang Keep, Tiragarde Keep. Same missing
        # "caves" sheet bug as cave_warm - this is the biome for the keep
        # SE of Razor Hill (Kyle's named example for "large empty space
        # without any tiles between rooms... an ugly hallway or just
        # empty gap"). Repointed at the real cave floor/wall crops.
        "stone": [
            ("cave_floor_rock_1", (0, 0, 85, 132), True),
            ("cave_floor_rock_2", (0, 0, 89, 132), True),
            ("cave_floor_rock_3", (0, 0, 88, 132), True),
        ],
        "dirt": [
            ("cave_floor_rock_2", (0, 0, 89, 132), True),
            ("cave_floor_rock_3", (0, 0, 88, 132), True),
        ],
        "rock": [
            ("cave_wall_1", (0, 0, 83, 132), True),
            ("cave_wall_2", (0, 0, 90, 132), True),
        ],
        "wall": [
            ("cave_wall_2", (0, 0, 90, 132), True),
            ("cave_wall_1", (0, 0, 83, 132), True),
        ],
        "cliff": ("cave_wall_1", (0, 0, 83, 132), True),
    },
    # Sunken Temple Grotto - genuinely flooded, not just "cave with some
    # water tiles" (Kyle: "its in the name"). Same floor/wall as cave_mossy
    # (damp pebbled stone / mossy brick already reads as overgrown-wet) but
    # swaps water to the calm fm_water crop instead of the choppy
    # water_ice chevron pattern every other cave was stuck with - a flooded
    # temple should read as still, submerged water, not whitewater rapids.
    # REAL BUG FOUND + FIXED (Kyle re-investigation): "damp_dungeons" sheet
    # key points at assets/tiles/damp_dungeons/Dungeon_WallsAndFloors.png,
    # which doesn't exist on disk, and "fm_water" is also missing - same
    # silent-flat-color-fallback bug as every other cave biome. Floor/wall
    # repointed at the real cave_floor_rock_*/cave_wall_* files, water
    # repointed at cave_water_pool_real (also real, already proven
    # elsewhere in this file).
    #
    # "bushes"/"small_rocks"/"ruin"/"ruin_2"/"ruin_3"/"coral_*"/"shell*"/
    # "statue" below are ALSO missing on disk (veg_fern_2, props_nature,
    # ruin_3/4/5, seabed_*, cave_statue_head - checked directly, none of
    # these files exist anywhere in the project). That's a real, separate
    # content gap - no ruin/coral/fern/statue prop art was ever actually
    # sourced - left flagged here rather than silently faked with
    # unrelated art. These prop tile_ids will keep rendering flat-color
    # fallback until real art is sourced for them; only floor/wall/water
    # (the tiles that actually fill "between rooms") are fixed.
    "cave_flooded_ruins": {
        "stone": [
            ("cave_floor_rock_1", (0, 0, 85, 132), True),
            ("cave_floor_rock_2", (0, 0, 89, 132), True),
            ("cave_floor_rock_3", (0, 0, 88, 132), True),
        ],
        "dirt": [
            ("cave_floor_rock_2", (0, 0, 89, 132), True),
            ("cave_floor_rock_3", (0, 0, 88, 132), True),
        ],
        "rock": [
            ("cave_wall_1", (0, 0, 83, 132), True),
            ("cave_wall_2", (0, 0, 90, 132), True),
        ],
        "wall": [
            ("cave_wall_2", (0, 0, 90, 132), True),
            ("cave_wall_1", (0, 0, 83, 132), True),
        ],
        "cliff": ("cave_wall_1", (0, 0, 83, 132), True),
        "shallow_water": ("cave_water_pool_real", (0, 0, 79, 132), True),
        "deep_water": ("cave_water_pool_real", (0, 0, 79, 132), True),
        "bushes": ("veg_fern_2", (0, 0, 64, 64), False),
        "small_rocks": ("props_nature", (400, 126, 101, 113), False),
        "ruin": ("ruin_3", (0, 0, 64, 64), False),
        "ruin_2": ("ruin_4", (0, 0, 48, 48), False),
        "ruin_3": ("ruin_5", (0, 0, 32, 32), False),
        "coral_blue": ("seabed_coral_blue", (0, 0, 64, 64), False),
        "coral_red": ("seabed_coral_red", (0, 0, 64, 64), False),
        "shell": ("seabed_shell_pearl", (0, 0, 32, 32), False),
    },
    # Naga sea-cave (Durotar NE coast) - the game's first fully hand-built
    # mini-dungeon, not a generate_cave() template instance. Same damp-
    # stone/calm-water base as cave_flooded_ruins (both are "wet cave"
    # biomes) but with its own dedicated prop set: real sourced monster/
    # ruin assets (serpent skeleton, shipwreck, giant crab, naga trident
    # statue) instead of the ruin-rubble pieces the Echo Isles caves use.
    "cave_naga": {
        "stone": [
            ("cave_floor_rock_1", (0, 0, 85, 132), True),
            ("cave_floor_rock_2", (0, 0, 89, 132), True),
            ("cave_floor_rock_3", (0, 0, 88, 132), True),
        ],
        "dirt": [
            ("cave_floor_rock_2", (0, 0, 89, 132), True),
            ("cave_floor_rock_3", (0, 0, 88, 132), True),
        ],
        "rock": [
            ("cave_wall_1", (0, 0, 83, 132), True),
            ("cave_wall_2", (0, 0, 90, 132), True),
        ],
        "wall": [
            ("cave_wall_2", (0, 0, 90, 132), True),
            ("cave_wall_1", (0, 0, 83, 132), True),
        ],
        "cliff": ("cave_wall_1", (0, 0, 83, 132), True),
        "shallow_water": ("cave_water_pool_real", (0, 0, 79, 132), True),
        "deep_water": ("cave_water_pool_real", (0, 0, 79, 132), True),
        "small_rocks": ("props_nature", (400, 126, 101, 113), False),
        "coral_blue": ("seabed_coral_blue", (0, 0, 64, 64), False),
        "coral_pink": ("seabed_coral_pink", (0, 0, 128, 128), False),
        "shell": ("seabed_shell_pearl", (0, 0, 32, 32), False),
        "shell_brown": ("seabed_shell_brown", (0, 0, 128, 128), False),
    },
    # Zalazane's Hollow - sunken TROLL RUINS, not a root-choked warren.
    # Same flooded-appropriate palette as Sunken Temple Grotto (both are
    # Echo Isles caves), but the signature feature is broken
    # architecture/statuary rather than root tangles - the ruin props
    # sourced for Tiragarde Keep fit equally well here (weathered
    # stonework, not tied to one specific location).
    "cave_troll_ruins": {
        "stone": [
            ("cave_floor_rock_1", (0, 0, 85, 132), True),
            ("cave_floor_rock_2", (0, 0, 89, 132), True),
            ("cave_floor_rock_3", (0, 0, 88, 132), True),
        ],
        "dirt": [
            ("cave_floor_rock_2", (0, 0, 89, 132), True),
            ("cave_floor_rock_3", (0, 0, 88, 132), True),
        ],
        "rock": [
            ("cave_wall_1", (0, 0, 83, 132), True),
            ("cave_wall_2", (0, 0, 90, 132), True),
        ],
        "wall": [
            ("cave_wall_2", (0, 0, 90, 132), True),
            ("cave_wall_1", (0, 0, 83, 132), True),
        ],
        "cliff": ("cave_wall_1", (0, 0, 83, 132), True),
        "shallow_water": ("cave_water_pool_real", (0, 0, 79, 132), True),
        "deep_water": ("cave_water_pool_real", (0, 0, 79, 132), True),
        "bushes": ("veg_fern_2", (0, 0, 64, 64), False),
        "small_rocks": ("props_nature", (400, 126, 101, 113), False),
        "ruin": ("ruin_3", (0, 0, 64, 64), False),
        "ruin_2": ("ruin_4", (0, 0, 48, 48), False),
        "ruin_3": ("ruin_5", (0, 0, 32, 32), False),
        "coral_blue": ("seabed_coral_blue", (0, 0, 64, 64), False),
        "shell": ("seabed_shell_pearl", (0, 0, 32, 32), False),
        # A big troll-ruins landmark - a broken carved statue head half-
        # buried in the temple floor, placed sparingly (see feature_tiles'
        # low density for "statue").
        "statue": ("cave_statue_head", (0, 0, 64, 64), False),
    },
    # Burning Blade Coven - demonic cultist den, not a generic lava-warm
    # cave. cave_warm's dark floor + mossy wall (already fixed earlier this
    # session) plus lava (already good) and a skull-jaw door prop for the
    # ritual/cultist read.
    # Drygulch Ravine - open-air red-rock canyon, NOT a dungeon (Kyle: "its
    # just [in] the name, its a ravine"). Reuses Durotar's actual red-sand
    # floor and red-rock-dark cliff textures directly (same "gen_red_*"
    # generated stand-ins desert/desert_oasis/orgrimmar already share) so
    # it genuinely looks like the same Durotar canyon country continuing
    # underground/enclosed, not a new palette. "tree" reuses desert's
    # cactus prop for the same reason.
    "cave_canyon": {
        "sand": [
            ("durotar_cracked_red_earth_a", (0, 0, 113, 118), True),
            ("durotar_cracked_red_earth_c", (0, 0, 115, 118), True),
            ("durotar_pebble_strewn_red_earth", (0, 0, 138, 165), True),
        ],
        "dirt": [
            ("durotar_cracked_red_earth_b", (0, 0, 116, 118), True),
            ("durotar_red_earth_to_dry_grass", (0, 0, 111, 118), True),
            ("durotar_red_rock_rubble_patch", (0, 0, 138, 165), True),
        ],
        "path": ("durotar_sun_bleached_path_dirt", (0, 0, 115, 118), True),
        "stone": [
            ("durotar_rocky_red_ground_a", (0, 0, 113, 118), True),
            ("durotar_cracked_red_rock_a", (0, 0, 138, 165), True),
        ],
        "rock": [
            ("durotar_rocky_red_ground_b", (0, 0, 117, 118), True),
            ("durotar_cracked_red_rock_b", (0, 0, 139, 165), True),
        ],
        # A real canyon wall - mountain rock face art, matching the
        # "canyon" biome name properly instead of reusing flat ground.
        "wall": [
            ("durotar_mountain_rock_face_a", (0, 0, 184, 285), True),
            ("durotar_mountain_rock_face_b", (0, 0, 184, 285), True),
        ],
        "cliff": [
            ("durotar_boulder_wall", (0, 0, 186, 285), True),
            ("durotar_mountain_scree_slope", (0, 0, 183, 285), True),
        ],
        "tree": [
            ("durotar_tall_saguaro_cactus", (0, 0, 154, 257), True),
            ("durotar_barrel_cactus", (0, 0, 164, 145), True),
        ],
        "small_rocks": [
            ("durotar_hardy_desert_shrub", (0, 0, 151, 184), True),
            ("durotar_dead_scrub_twig", (0, 0, 141, 177), True),
        ],
    },
    "cave_demonic": {
        # Same missing "caves" sheet bug as cave_warm - repointed at real
        # cave floor/wall crops. Skull Rock and Burning Blade Coven both
        # already have full chunk-art coverage so this rarely surfaces in
        # practice, but fixed for correctness/consistency regardless.
        "stone": [
            ("cave_floor_rock_1", (0, 0, 85, 132), True),
            ("cave_floor_rock_2", (0, 0, 89, 132), True),
            ("cave_floor_rock_3", (0, 0, 88, 132), True),
        ],
        "dirt": [
            ("cave_floor_rock_2", (0, 0, 89, 132), True),
            ("cave_floor_rock_3", (0, 0, 88, 132), True),
        ],
        "rock": [
            ("cave_wall_1", (0, 0, 83, 132), True),
            ("cave_wall_2", (0, 0, 90, 132), True),
        ],
        "wall": [
            ("cave_wall_2", (0, 0, 90, 132), True),
            ("cave_wall_1", (0, 0, 83, 132), True),
        ],
        "cliff": ("cave_wall_1", (0, 0, 83, 132), True),
        # "lava" sheet key ("lava" -> assets/tiles/.../lava.png) is missing
        # on disk and no substitute lava/fel art exists anywhere in the
        # project (checked via find) - real content gap, left as-is rather
        # than mapped to unrelated art.
        "lava": ("lava", (488, 208, 16, 16), False),
        # Fire-gate arch replaces the skull-door as the primary cultist
        # landmark - a flame-lit stone archway with a demon-face carving
        # reads as ritual architecture more clearly than a door alone.
        # Skull-door kept as secondary scatter for variety.
        "fire_gate": ("cave_fire_gate", (0, 0, 64, 64), False),
        "skull_door": ("cave_skull_door_1", (0, 0, 64, 64), False),
        "skull_door_2": ("cave_skull_door_2", (0, 0, 64, 64), False),
        "dark_totem": ("cave_dark_totem", (0, 0, 64, 64), False),
        "small_rocks": ("props_nature", (400, 126, 101, 113), False),
    },
    # Dustwind Cave - harpy nesting cave. No harpy/feather/nest asset
    # exists anywhere in the currently-sourced packs (checked props_nature,
    # the craftpix wildlife pack - that's creature sprites, not scatter
    # decoration - and the undead objects folder). Bones/carrion is the
    # closest available read ("predator's lair strewn with kills") and at
    # least isn't generic gray rock, but this is a real gap, not a design
    # choice - flagging for a future asset pass rather than pretending
    # bones = harpy.
    "cave_dustwind": {
        # Same missing "caves" sheet bug as cave_warm - repointed at real
        # cave floor/wall crops.
        "stone": [
            ("cave_floor_rock_1", (0, 0, 85, 132), True),
            ("cave_floor_rock_2", (0, 0, 89, 132), True),
            ("cave_floor_rock_3", (0, 0, 88, 132), True),
        ],
        "dirt": [
            ("cave_floor_rock_2", (0, 0, 89, 132), True),
            ("cave_floor_rock_3", (0, 0, 88, 132), True),
        ],
        "rock": [
            ("cave_wall_1", (0, 0, 83, 132), True),
            ("cave_wall_2", (0, 0, 90, 132), True),
        ],
        "wall": [
            ("cave_wall_2", (0, 0, 90, 132), True),
            ("cave_wall_1", (0, 0, 83, 132), True),
        ],
        "cliff": ("cave_wall_1", (0, 0, 83, 132), True),
        "bones": ("cave_bones_1", (0, 0, 32, 32), False),
        "bones_2": ("cave_bones_2", (0, 0, 64, 64), False),
        "bones_3": ("cave_bones_3", (0, 0, 32, 32), False),
        "small_rocks": ("props_nature", (400, 126, 101, 113), False),
    },
    "cave_mossy": {
        # Real cropped cave floor/wall art (was damp_dungeons/cave_bones/
        # cave_crystal - all missing packs, same gap as everywhere else in
        # this file before this session's Durotar/caves pass). Floor and
        # wall use genuinely different crops so a cave's walls stay
        # visually distinct from its floor (the exact thing "we need
        # walls inside caves so we can see where the path is" was about,
        # now backed by real art instead of a missing-pack fallback).
        # "stone"/"rock" each get real variant lists (3 floor crops, 2
        # wall crops) rather than one fixed texture repeated everywhere.
        "stone": [
            ("cave_floor_rock_1", (0, 0, 85, 132), True),
            ("cave_floor_rock_2", (0, 0, 89, 132), True),
            ("cave_floor_rock_3", (0, 0, 88, 132), True),
        ],
        "dirt": [
            ("cave_floor_rock_2", (0, 0, 89, 132), True),
            ("cave_floor_rock_3", (0, 0, 88, 132), True),
        ],
        "rock": [
            ("den_wall_a", (0, 0, 627, 627), True),
            ("den_wall_b", (0, 0, 627, 627), True),
        ],
        "wall": [
            ("den_wall_b", (0, 0, 627, 627), True),
            ("den_wall_a", (0, 0, 627, 627), True),
        ],
        "cliff": ("den_wall_a", (0, 0, 627, 627), True),
        "shallow_water": ("cave_water_pool_real", (0, 0, 79, 132), True),
        "deep_water": ("cave_water_pool_real", (0, 0, 79, 132), True),
        "bushes": ("cave_moss_clump_real", (0, 0, 77, 132), True),
        "small_rocks": ("cave_rubble_floor", (0, 0, 78, 132), True),
        # "bones"/"bones_2"/"bones_3" - The Den's "bones" feature scatter
        # (see generate_cave's feature_tiles table) calls these 3 tile_ids,
        # and NONE were mapped in this biome - checked directly (searching
        # for the string inside this dict block, not just the file -
        # "bones" LOOKED covered because it's mentioned in a comment
        # above, a real false-positive). Confirmed via an actual rendered
        # screenshot: 3 different flat gray fallback boxes scattered
        # across The Den's floor. First fix attempt pointed these at
        # SHEETS' "cave_bones_1/2/3/4" entries, assuming registered ==
        # real - checked the actual files on disk and assets/tiles/
        # cave_props/ doesn't exist at all, so that would've just traded
        # one broken texture for another. No real bone art exists
        # anywhere in the project (searched the whole assets/tiles tree).
        # Left genuinely unmapped here rather than faked - The Den's own
        # generation is instead post-processed in zone_generator.py to
        # not place "bones"/"bones_2"/"bones_3" at all (Kyle scoped this
        # session to The Den specifically, not the shared generate_cave()
        # feature table that every "bones"-feature cave uses).
    },
    # Wailing Caverns - lush, waterlogged, nightmare-corrupted swamp cave.
    # Deliberately NOT reusing cave_mossy's DampDungeons warm-dry stone -
    # this needs a wetter, sicklier read to match "waterlogged and
    # overgrown" + stagnant water throughout every chamber per the
    # generator's own flavour text. Ground is the swamp pack's bog-floor
    # tile (dark purple, olive-moss speckle) - unused by any other biome
    # until now, sourced but never wired (see NOTES.md asset inventory).
    # Walls are DampDungeons' mossy green-brick block, distinct from
    # cave_mossy's plain stone crop. Water uses the textured wavy
    # water_ice crop rather than the flat calm-pond fill used elsewhere -
    # see the "shallow_water" entry comment below for why (density).
    "cave_swamp": {
        "bones": ("cave_bones_1", (0, 0, 32, 32), False),
        "bones_2": ("cave_bones_2", (0, 0, 64, 64), False),
        "bones_3": ("cave_bones_3", (0, 0, 32, 32), False),
        "crystal": ("cave_crystal_1", (0, 0, 64, 64), False),
        "crystal_2": ("cave_crystal_2", (0, 0, 64, 64), False),
        "dirt": ("swamp", (0, 0, 32, 32), False),
        # Cave walls (generator fills the whole map with "stone" on the
        # collision layer, then carves chambers out of it - "stone" here
        # IS the wall material, not floor). Mossy green-brick, distinct
        # from the bog-floor "dirt" crop above so walls read as solid
        # boundaries instead of blending into open floor.
        "stone": ("damp_dungeons", (0, 208, 16, 16), False),
        "rock": ("damp_dungeons", (0, 208, 16, 16), False),
        "wall": ("damp_dungeons", (0, 208, 16, 16), False),
        "cliff": ("damp_dungeons", (0, 208, 16, 16), False),
        # Stagnant water covers up to ~30% of every chamber here (see the
        # generator's carve(wet=True) calls) - much denser than the sparse
        # oasis-pond accent this calm-water crop was designed for. The flat
        # solid-teal calm-pond crop (used sparingly elsewhere) reads as an
        # unmapped/debug color at this density, so this uses the textured
        # wavy water_ice crop instead (same one grassland/undead use) -
        # still calm/non-animated in the sense that it's a single static
        # frame, just has actual surface texture instead of a flat fill.
        "shallow_water": ("water_ice", (36, 73, 24, 24), False),
        "deep_water": ("water_ice", (42, 73, 24, 24), False),
        # Root tangles / fungal bloom scatter (the generator's own
        # "bushes" visual-layer placement at 6% density throughout) -
        # bare-tree crop reused the same way cave_mossy uses it for roots.
        "bushes": ("props_nature", (310, 235, 40, 145), False),
        # Green vine/moss patch (DampDungeons) for extra overgrown texture
        # variety on top of the bog floor - not placed by the generator
        # yet, available if a future visual-layer pass wants it.
        "flowers": ("damp_dungeons", (32, 48, 16, 16), False),
    },
    # Razorfen Kraul - quilboar thorn-tunnel dungeon. Same dry-dirt/gray-
    # rock/bramble palette as the Razorfen Approach overworld subzone it
    # connects from (savanna_thornscrub), so the transition from surface
    # to dungeon reads as continuous rather than an arbitrary palette
    # jump. Ground uses the darker Forgotten Memories grass variant
    # (savanna_thornscrub's ground) rather than plain savanna tan, for
    # the same "denser/darker" foreshadowing read.
    "cave_thornscrub": {
        "bones": ("cave_bones_1", (0, 0, 32, 32), False),
        "bones_2": ("cave_bones_2", (0, 0, 64, 64), False),
        "bones_3": ("cave_bones_3", (0, 0, 32, 32), False),
        "crystal": ("cave_crystal_1", (0, 0, 64, 64), False),
        "crystal_2": ("cave_crystal_2", (0, 0, 64, 64), False),
        # Same missing "undead_ground" bug as savanna_bones above.
        "stone": ("cave_floor_rock_1", (0, 0, 85, 132), True),
        "dirt": ("fm_tileset", (1573, 447, 128, 131), True),
        "rock": ("cave_wall_1", (0, 0, 83, 132), True),
        "wall": ("cave_wall_1", (0, 0, 83, 132), True),
        "cliff": ("cave_wall_2", (0, 0, 90, 132), True),
        # Bramble thorn scatter - the generator's own "signature feature"
        # comment calls these real collision hazards, not decoration -
        # bare-tree crop as the thorn-tangle read, consistent with every
        # other "bushes" mapping in the savanna family.
        "bushes": ("props_nature", (310, 235, 40, 145), False),
        "small_rocks": ("props_nature", (400, 126, 101, 113), False),
    },
}


def get_biome_for_zone(zone_name, is_cave=False):
    """Resolve a zone/tilemap name to a biome_id. Caves check CAVE_BIOME
    first since dungeon names don't overlap the overworld ZONE_BIOME list."""
    if is_cave and zone_name in CAVE_BIOME:
        return CAVE_BIOME[zone_name]
    return ZONE_BIOME.get(zone_name, DEFAULT_BIOME)


def get_texture_entry(biome_id, tile_id, x=None, y=None):
    """Return (sheet_path, rect, smooth) for a tile_id in a biome, or None
    if unmapped - callers must fall back to tiles.py's flat color on None.

    A BIOME_TILES entry can be either a single (sheet_key, rect, smooth)
    tuple (unchanged behaviour - every biome not explicitly given
    variants below still renders exactly one texture) or a list of such
    tuples for real variety. When a list and (x, y) are both given, the
    variant is picked deterministically from tile position (same tile
    always renders the same variant - a real render, not visual noise
    that shifts every frame) via a cheap hash, not randomness (this
    function has no RNG dependency and shouldn't gain one - a save/reload
    or a second render of the same zone must look identical). Kyle: "I
    don't want one uniform tile across the board" - the earlier version
    of this fix mapped exactly one texture per tile_id despite real
    source variants (cracked_red_earth_a/b/c etc) being available, which
    produced a visible grid-repeat pattern once actually rendered.
    """
    biome_tiles = BIOME_TILES.get(biome_id)
    if not biome_tiles:
        return None
    entry = biome_tiles.get(tile_id)
    if not entry:
        return None
    # Variant list vs single entry: a single entry is a 3-tuple whose
    # first element is a string (the sheet_key); a variant list is a
    # list/tuple of such 3-tuples. Checking the outer type this way
    # (rather than requiring callers to wrap single entries in a
    # length-1 list) keeps every existing single-texture BIOME_TILES
    # entry in this file working with zero changes.
    if isinstance(entry, list):
        if not entry:
            return None
        if x is not None and y is not None:
            # 2D bit-mixing hash (splitmix-style), NOT the previous
            # (x*7 + y*13) % len(entry) linear stride. Kyle: "the tiles
            # look nauseating in durotar as they are just diagonal
            # repeats" - confirmed by rendering an actual screenshot
            # (not just headless assertions) and by hand-tracing the old
            # formula: every diagonal (x-y = constant) maps to the same
            # index, and every row is a fixed cyclic shift of the row
            # above, by construction, for ANY x*a+y*b linear form with
            # small variant counts. No amount of edge-blending or better
            # source art fixes a picker that's mathematically guaranteed
            # to band - this had to be a real 2D scramble, not a tweak.
            # System-wide fix (this function has the only call site,
            # per a grep before making this change), so every biome
            # using variant lists benefits, not just the zone tested.
            h = (x * 0x9E3779B1) ^ (y * 0x85EBCA77)
            h &= 0xFFFFFFFF
            h ^= (h >> 16)
            h = (h * 0x27D4EB2F) & 0xFFFFFFFF
            h ^= (h >> 15)
            idx = h % len(entry)
        else:
            idx = 0
        chosen = entry[idx]
    else:
        chosen = entry
    sheet_key, rect, smooth = chosen
    sheet_path = SHEETS.get(sheet_key)
    if not sheet_path:
        return None
    return (sheet_path, rect, smooth)
