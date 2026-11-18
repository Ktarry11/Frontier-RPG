#!/usr/bin/env python3
"""Slice the 6x5 magenta-background BUILDING sheet into 30 transparent PNGs in assets/buildings/.

    python3 tools/slice_building_sheet.py tools/building_sheets/eastern_kingdoms_buildings.png
    python3 tools/slice_building_sheet.py <sheet.png> --preview /tmp/ek_buildings.png

Same magenta key as the icon sheets (tools/slice_icon_sheet.key_magenta: soft alpha ramp plus a despill pass so
dark eaves and timber edges don't come back with a pink fringe). Prompts and the cell order live in
claude/eastern_kingdoms_building_prompts.md - NAMES below is that table, and the two must stay in step.

Two things differ from slice_icon_sheet, both because these are buildings and not inventory icons:

  * no square padding and no fixed output size. An icon is a 96x96 square by contract; a building is a sprite
    placed by its bottom-centre with a declared height in tiles, so it keeps its own aspect.
  * RELATIVE SCALE IS PRESERVED. Every sprite is cropped to its own bounding box but NOT normalised, so a
    cottage stays smaller than a barn exactly as drawn. Normalising per-cell is right for a sheet of unrelated
    objects (a feather and a strongbox) and wrong here, where a cottage drawn at a cottage's size is the
    information. Same reasoning as the potion sheet's PRESERVE_SCALE.

The generated sheets are never on a perfect pixel grid - rows drift - so sprites are found as connected blobs
and assigned to whichever cell holds their centre, rather than cut on arithmetic cell boundaries.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from slice_icon_sheet import key_magenta  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

#: set name -> (cols, rows, output dir, names in grid order left-to-right then top-to-bottom)
SETS = {}


def _set(key, cols, rows, out, names):
    names = names.split()
    assert len(names) == cols * rows, (key, len(names), cols * rows)
    SETS[key] = (cols, rows, out, names)


#: THE PLAGUELANDS (docs/plaguelands_art_prompts.md sheets 2 and 3, Kyle 16 Nov 2026).
_set("plaguelands_buildings", 6, 6, "assets/buildings", """
    pl_bulwark_gate pl_bulwark_apothecary pl_bulwark_palisade pl_bulwark_barracks pl_bulwark_bat_roost pl_bulwark_wagon_shed
    pf_keep pf_chapel pf_training_yard pf_hall pf_gate pf_stable
    lh_chapel lh_command_tent lh_flight_perch crown_guard_tower cg_palisade_tent lh_field_hospital
    sc_town_house sc_chapel sc_barracks hearthglen_gatehouse mardenholde_tower sc_bell_tower
    tyr_town_hall tyr_abbey tyr_dock_warehouse tyr_harbour_tower sc_courtyard_gate sc_stable
    sm_facade strat_gates scholo_entrance hearthglen_keep_gate scourge_ziggurat scourge_spire""")
_set("plaguelands_props", 6, 6, "assets/tiles/plaguelands/props", """
    pl_cauldron_live pl_cauldron_dead pl_cauldron_platform pl_corpse_sacks pl_meat_wagon pl_runoff_pool
    pl_farmhouse_burned pl_barn_plagued pl_pumpkin_rot pl_windmill_broken pl_fence_broken pl_wheat_stook
    pl_ruin_wall pl_clock_stump pl_ruin_arch pl_stall_burned pl_darrowshire_doll pl_knight_statue
    pl_scourge_banner pl_bone_barricade pl_necro_obelisk pl_ghoul_pit pl_butcher_block pl_skull_pile
    sc_war_tent sc_pyre sc_supply_cart pf_banner pf_field_tent pf_weapon_rack
    pl_plaguewood_tree pl_dead_oak pl_blight_pine ql_lantern_post zm_ruin_block pl_plague_mushrooms""")

#: sheets 4, 6, 7 and 8 (Kyle 16 Nov 2026): the dungeons' furniture, and the Plaguelands' creatures and bosses.
_set("plaguelands_dungeon_props", 6, 6, "assets/tiles/plaguelands/dungeon_props", """
    sm_pew sm_candelabra sm_bookshelf sm_lectern sm_weapon_rack sm_altar
    sm_sarcophagus sm_interrogation_chair sm_training_dummy sm_glass_window sm_saint_statue sm_supply_crates
    scholo_alchemy_table scholo_desk scholo_golem_table scholo_ritual_stone scholo_specimen_jars scholo_iron_cage
    strat_stall_burned strat_fountain strat_ziggurat_brazier strat_rubble strat_grain_cart strat_wall
    hg_throne hg_war_table hg_banner hg_organ hg_choir_stall hg_kennel
    sc_treasure_chest scourge_bone_chest hg_reliquary dg_wall_torch dg_chandelier silver_hand_symbol""")
_set("plaguelands_creatures", 6, 6, "assets/creatures/_src/plaguelands", """
    pl_plague_eruptor pl_flesh_golem pl_gargoyle pl_crypt_fiend pl_death_knight pl_skeletal_warhorse
    pl_plaguebat pl_plaguehound pl_carrion_grub pl_frenzied_ghoul pl_skeletal_mage pl_wailing_spirit
    pl_cult_neophyte pl_cult_plaguebringer pl_necrolyte pl_cauldron_tender pl_dark_caster pl_cult_lieutenant
    pl_diseased_bear pl_plagued_wolf pl_carrion_vulture pl_blighted_stag pl_plague_slime pl_plaguewood_spider
    pl_forsaken_apothecary pl_deathguard ad_crusader ad_priestess pl_darrowshire_ghost zm_troll_warrior
    pl_boss_abomination_farmer pl_boss_lich_magistrate pl_boss_brood_queen pl_boss_bone_colossus pl_rare_plague_rider pl_rare_arch_necromancer""")
_set("plaguelands_scarlet", 6, 6, "assets/creatures/_src/plaguelands", """
    sc_monk sc_zealot sc_adept sc_chaplain sc_myrmidon sc_centurion
    sc_knight sc_inquisitor sc_judicator sc_arcanist sc_war_hound sc_cavalier
    sc_tp_crusader sc_tp_sniper sc_tp_drill_sergeant sc_tp_inquisitor sc_tp_champion sc_tp_cleric
    pf_rory_callahan pf_knight pf_chaplain pf_scout pf_sentry pf_quartermaster
    hg_boss_gatewarden hg_boss_quartermaster hg_boss_pyre_sisters hg_boss_drillmaster hg_boss_high_inquisitor hg_boss_kennelmaster
    hg_boss_arcanist hg_boss_lady_marden hg_boss_crimson_choir hg_boss_volkov hg_boss_victor_hale hg_scarlet_charger""")
_set("plaguelands_dungeon_bosses", 6, 6, "assets/creatures/_src/plaguelands", """
    sm_boss_interrogator sm_boss_bloodmage sm_boss_houndmaster sm_boss_arcanist sm_boss_champion sm_boss_commander
    sm_boss_high_inquisitor scholo_boss_gargoyle scholo_boss_ghost_lady scholo_boss_bone_construct scholo_boss_frost_lich scholo_boss_alchemist
    scholo_boss_librarian scholo_boss_instructor scholo_boss_noble_lady scholo_boss_noble_lord scholo_boss_headmaster scholo_ghost_servant
    strat_boss_ghoul_runt strat_boss_cannon_master strat_boss_archivist strat_boss_grand_crusader strat_boss_dreadlord strat_boss_magistrate
    strat_boss_crypt_lord strat_boss_baroness strat_boss_lich strat_boss_flesh_golem strat_boss_baron strat_deathcharger
    pl_boss_cult_necromancer pl_silver_hand_ghost pl_boss_gate_guardian pl_boss_eye_construct pl_boss_chorus_leader pl_boss_abom_butcher""")

_set("ek_buildings", 6, 5, "assets/buildings", """
    ek_watermill ek_mill_sluice ek_granary ek_millstone_shelter ek_apothecarium ek_plague_vat_platform
    ek_forsaken_field_tent ek_forsaken_watchtower ek_cottage_small ek_cottage_medium ek_townhouse ek_village_inn
    ek_village_chapel ek_smithy_forge ek_stable_block ek_barn ek_trading_post ek_fishery_shed
    ek_boathouse ek_sawmill_shed ek_tannery ek_apiary_shelter ek_border_watchtower ek_gatehouse
    ek_barracks_hall ek_command_tent ek_ruined_gatehouse ek_burnt_cottage ek_syndicate_house ek_wayshrine""")

#: Generic high-elven architecture in the classic crimson and gold. Deliberately NOT Underdark-specific:
#: Kael's Bastion gets its look by hue-shifting these, and Silvermoon/Ghostlands/Eversong reuse the originals.
_set("blood_elf", 6, 5, "assets/buildings", """
    be_house_small be_house_medium be_manor be_townhouse be_inn be_shop
    be_market_stall be_smithy be_alchemist be_sanctum be_spire be_grand_spire
    be_great_hall be_library be_temple be_barracks be_guard_post be_gatehouse
    be_wall_arch be_arcane_well be_portal_frame be_stable be_storehouse be_treasury
    be_observatory be_pavilion be_command_tent be_ruined_house be_ruined_tower be_obelisk""")

#: The giant mushrooms are the Underdark's TREES - cells 1-4 are scattered by the forest pass, so their
#: relative scale against the camp gear and rubble is load-bearing, not cosmetic.
_set("underdark_props", 6, 6, "assets/tiles/underdark/props", """
    ud_shroom_tall_violet ud_shroom_squat_ochre ud_shroom_cluster_blue ud_shroom_canopy ud_shroom_small ud_shelf_fungus
    ud_crystal_violet ud_crystal_cyan ud_lattice_growth ud_crystal_spire ud_geode_open ud_crystal_float
    ud_glow_pool ud_lichen_boulder ud_moss_curtain ud_spore_vent ud_ice_stalagmites ud_frozen_crate
    ud_survey_tripod ud_arcane_brazier ud_field_desk ud_codex_crates ud_specimen_rack ud_codex_banner
    ud_dig_scaffold ud_codex_tent ud_broken_column ud_fallen_arch ud_statue_armless ud_masonry_rubble
    ud_floating_stone ud_rune_stone ud_fungal_shelf ud_fungal_node ud_cocooned_shape ud_stalagmites""")

#: BANDIT / OUTLAW buildings (claude/bandit_building_prompts.md). Kyle, 2026-11-01: "not caveman or
#: archaic or anything" - these are tradesmen and dispossessed gentry who turned, so the sheet is
#: competent human architecture that has been seized and barricaded. Cell 23 is the one deliberately
#: crude building on it.
_set("bandit", 6, 5, "assets/buildings", """
    bd_brigand_hall bd_counting_house bd_captains_quarters bd_barricaded_townhouse bd_seized_chapel bd_strongroom
    bd_seized_watermill bd_powder_store bd_arms_workshop bd_carpenter_shop bd_mason_shed bd_warehouse
    bd_seized_farmhouse bd_commandeered_barn bd_grain_store bd_cart_shed bd_stock_pen bd_well_house
    bd_gate_barricade bd_lookout_tower bd_guard_post bd_palisade_section bd_sentry_leanto bd_winch_house
    bd_dock_house bd_boat_shed bd_hideout_entrance bd_interrogation_house bd_fence_shop bd_burnt_house""")

#: ORC GARRISON buildings (claude/orc_building_prompts.md). The eleven orc buildings already in the
#: library are Valley-of-Trials starter architecture - huts, tents, hide. Kyle: "actual buildings and not
#: just huts and shacks." Cells 28-30 are orc construction with Forsaken tenants, for Hammerfall.
_set("orc", 6, 5, "assets/buildings", """
    orc_war_hall orc_warchief_lodge orc_barracks_longhouse orc_officers_house orc_great_gatehouse orc_stockade_section
    orc_war_forge orc_armoury orc_siege_workshop orc_tannery_hall orc_butchery orc_supply_store
    orc_spirit_lodge orc_totem_court orc_great_totem orc_warbeast_stable orc_kennel_block orc_pyre_platform
    orc_mess_hall orc_brew_house orc_warlock_tower orc_healer_house orc_quartermaster_post orc_smokehouse
    orc_watch_tower orc_guard_post orc_signal_beacon orc_forsaken_apothecary orc_deathguard_post orc_bone_yard_shed""")

#: THE ASPEN WILDERNESS props. Cells 1-10 are the zone's TREES - aspen and lodgepole - so like the
#: Underdark's giant mushrooms they get scattered by the forest pass and their relative scale against the
#: brush and camp gear is load-bearing. Nothing from Earth is on this sheet (Kyle, 2026-10-27: "we dont
#: want anything from our world yet"); the burn and the seam row is the range's own violence instead.
#: SOUTHERN THOUSAND NEEDLES props. Row 4 is the whole Freewind idea in six objects - rope, aspen timber
#: and the gear to span a gap between mesas. Nothing on this sheet is Earth-made; the aspen is the only
#: imported thing on it and it arrived as trees.
_set("southern_needles_props", 6, 6, "assets/tiles/southern_needles/props", """
    sn_rock_spire sn_boulder_red sn_layered_stack sn_split_stone sn_rock_arch sn_toppled_column
    sn_barrel_cactus sn_saguaro sn_thornbush sn_desert_sage sn_dead_shrub sn_grass_tuft
    sn_kodo_skull sn_rib_bones sn_hide_frame sn_driftwood_salt sn_clay_vessel sn_stone_pile
    sn_rope_coil sn_anchor_post sn_plank_stack sn_scaffold sn_pulley_hoist sn_bridge_upright
    sn_hide_tent sn_totem_aspen sn_cook_fire sn_drying_rack sn_water_trough sn_hide_banner
    sn_windsock sn_streamers sn_lookout_platform sn_cairn sn_rope_railing sn_spear_bundle""")

_set("aspen_props", 6, 6, "assets/tiles/aspen/props", """
    asp_aspen_tall asp_aspen_bare asp_aspen_young asp_aspen_clump asp_aspen_fallen asp_aspen_stump
    asp_pine_tall asp_pine_bent asp_pine_krummholz asp_pine_young asp_snag_standing asp_deadfall_pile
    asp_willow_thicket asp_fireweed asp_huckleberry asp_ferns asp_grass_tussock asp_wildflowers
    asp_boulder asp_boulder_lichen asp_boulder_split asp_talus_pile asp_beaver_dam asp_beaver_lodge
    tau_timber_stack tau_hide_tent_small tau_totem_carved tau_drying_rack tau_hitching_post tau_cook_fire
    asp_snag_charred asp_stump_burned asp_trunk_snapped asp_dead_scrub asp_red_drift asp_elk_skull""")

#: TAUREN BUILDINGS, general purpose (Kyle: "keep them general enough to reuse as needed"). Camp Taurajo,
#: Freewind Post and anything tauren later all draw from this one set. Traditional hide-and-pole
#: architecture; Freewind's aspen-timber rebuild is a recolour experiment first, not a second sheet.
_set("tauren", 6, 5, "assets/buildings", """
    tau_tent_small tau_tent_medium tau_tent_large tau_longhouse tau_elder_lodge tau_yurt
    tau_great_lodge tau_spirit_lodge tau_hearth_lodge tau_meeting_shelter tau_bonfire_pavilion tau_trading_post
    tau_smithy tau_tannery tau_carver_shop tau_herb_hut tau_bowyer tau_kiln
    tau_storehouse tau_food_cache tau_kodo_pen tau_stable tau_water_trough tau_watchtower
    tau_gate_arch tau_palisade tau_totem_pole tau_footbridge tau_tent_burned tau_lodge_collapsed""")

#: ENTRANCE ART, sheet 2 (claude/entrance_art_prompts_2.md): the way OUT seen from inside, road
#: gates by region, and entrances for the newer zones' dungeons. The ent_ prefix is what lets a
#: sprite stand over a portal tile (world/portal_art.py).
_set("entrances_2", 6, 4, "assets/tiles/cave_entrances", """
    ent_exit_cave_daylight ent_exit_stone_stairs ent_exit_mine_adit ent_exit_ice_tunnel ent_exit_crystal ent_exit_flooded_stairs
    ent_exit_ship_hatch ent_exit_gangplank ent_gate_kodo_tusks ent_gate_lychgate ent_gate_tollgate ent_gate_standing_stones
    ent_gate_sand_pylons ent_gate_rope_bridge ent_gate_snow_logs ent_gate_basalt_storm ent_gate_goblin_port ent_gate_crystal_arch
    ent_ogre_mound ent_kobold_dig ent_shipwreck_hull ent_dwarven_vault ent_salt_sinkhole ent_sunken_belltower""")

#: ENTRANCE ART, sheet 3 (claude/entrance_art_prompts_3_4.md): town gates, boat landings, and
#: six more road gates. Row 4 was ASKED for side-on and came back facing the camera, so those
#: six are filed as plain front-facing gates; the side-on piece is still missing.
_set("entrances_3", 6, 4, "assets/tiles/cave_entrances", """
    ent_town_tauren_totems ent_town_nightelf_bridge ent_town_forsaken_gate ent_town_troll_gate ent_town_wheel_arch ent_town_highelf_gate
    ent_town_headframe_gate ent_town_charred_gate ent_town_whalerib_gate ent_town_pirate_gate ent_gate_wall_breach ent_gate_pass_cairns
    ent_dock_pier ent_dock_troll ent_dock_goblin ent_dock_forsaken ent_dock_nightelf ent_dock_slipway
    ent_gate_logs ent_gate_stone_pillars ent_gate_tusk_banners ent_gate_sandstone ent_gate_bamboo ent_gate_snowpine""")

#: Sheet 4: the way OUT by dungeon flavour, and doors that lead deeper. Kyle generated it twice
#: and kept both ("i downloaded both"), so the second take is the same list with _b - a second
#: look for each, which matters where one dungeon has several exits.
_set("entrances_4a", 6, 4, "assets/tiles/cave_entrances", """
    ent_exit_crypt_stairs ent_exit_spider_web ent_exit_troll_temple ent_exit_lava_fissure ent_exit_ogre_hall ent_exit_kobold_tunnel
    ent_exit_dwarven_vault ent_exit_keep_gate ent_exit_tower_door ent_exit_root_hollow ent_exit_sewer_grate ent_exit_salt_shaft
    ent_exit_bramble ent_exit_wreck_hull ent_exit_bell_window ent_exit_slot_canyon ent_exit_fern_cavern ent_exit_coral_arch
    ent_door_ship_cabin ent_door_ship_hatch_down ent_door_stairs_down ent_door_bronze_pipe ent_door_ice_steps ent_door_crystal_rift""")
_set("entrances_4b", 6, 4, "assets/tiles/cave_entrances", """
    ent_exit_crypt_stairs_b ent_exit_spider_web_b ent_exit_troll_temple_b ent_exit_lava_fissure_b ent_exit_ogre_hall_b ent_exit_kobold_tunnel_b ent_exit_dwarven_vault_b ent_exit_keep_gate_b ent_exit_tower_door_b ent_exit_root_hollow_b ent_exit_sewer_grate_b ent_exit_salt_shaft_b ent_exit_bramble_b ent_exit_wreck_hull_b ent_exit_bell_window_b ent_exit_slot_canyon_b ent_exit_fern_cavern_b ent_exit_coral_arch_b ent_door_ship_cabin_b ent_door_ship_hatch_down_b ent_door_stairs_down_b ent_door_bronze_pipe_b ent_door_ice_steps_b ent_door_crystal_rift_b""")

#: DARK IRON buildings (assets/buildings/_src/tempest_dark_iron_buildings_sheet_30.png). Drawn for
#: Tempest Isle and first used for Onyxhollow, the Dark Iron town under the Abyssal Sands (Kyle, 13
#: Nov 2026: "We have all the art"). Rows: the works, the heavy plant, the town and its ruins, forge
#: gear, street furniture.
#: ORC TOWN buildings, sheet 2 (claude/orc_building_prompts_2.md). Sheet 1 was a garrison: nobody lived
#: anywhere, the inn/bank/auction/flight master had no orc building, and the watch tower stood in every
#: town 26 times. Homes, services, and second versions of the most used pieces.
_set("orc_town", 6, 5, "assets/buildings", """
    orc_inn orc_bank orc_auction_hall orc_wyvern_roost orc_general_store orc_market_stalls
    orc_training_hall orc_hunters_lodge orc_shadow_den orc_earth_lodge orc_herbalist_house orc_engineer_shop
    orc_house_large orc_house_medium orc_house_small orc_townhouse orc_house_row orc_crafter_house
    orc_house_small_b orc_house_medium_b orc_town_well orc_covered_market orc_fighting_pit orc_elder_house
    orc_stone_watch_tower orc_wall_tower orc_town_gate orc_granary orc_trading_post orc_storehouse""")

#: SIDE-ON ROAD GATES (claude/side_gate_prompts.md): single gateposts, A and B of each style. A road
#: leaving east or west gets one post either side of it (world/exit_frames.py), because an image model
#: draws a whole gate face-on whatever it is asked.
_set("side_gateposts", 6, 4, "assets/tiles/cave_entrances", """
    ent_side_standing_stones_a ent_side_standing_stones_b ent_side_wall_breach_a ent_side_wall_breach_b ent_side_lychgate_a ent_side_lychgate_b
    ent_side_moonlit_a ent_side_moonlit_b ent_side_kodo_tusks_a ent_side_kodo_tusks_b ent_side_goblin_port_a ent_side_goblin_port_b
    ent_side_whalerib_a ent_side_whalerib_b ent_side_sand_pylons_a ent_side_sand_pylons_b ent_side_tollgate_a ent_side_tollgate_b
    ent_side_stone_pillars_a ent_side_stone_pillars_b ent_side_charred_a ent_side_charred_b ent_side_bamboo_a ent_side_logs_a""")

#: FELWOOD (claude/felwood_art_prompts.md, sheets 1 and 2). The creatures cut to a staging folder and are
#: filed into assets/creatures/ by tools/file_felwood_art.py; the buildings and props likewise, split
#: between assets/buildings/ and assets/tiles/felwood/props/.
_set("felwood_creatures", 6, 6, "assets/creatures/_src/felwood", """
    fw_deadwood_warrior fw_deadwood_watcher fw_deadwood_pathfinder fw_deadwood_shaman fw_deadwood_gardener fw_deadwood_alpha
    fw_satyr_rogue fw_satyr_trickster fw_satyr_shadowstalker fw_satyr_felsworn fw_satyr_hellcaller fw_satyr_lord
    fw_felguard fw_infernal fw_imp fw_felhound fw_doomguard fw_eredar_warlock
    fw_council_acolyte fw_council_summoner fw_council_warlock fw_bound_voidwalker fw_hound_handler fw_council_high_warlock
    fw_fel_bear fw_blighted_wolf fw_toxic_ooze fw_warpwood_treant fw_entropic_horror fw_jadefire_stag
    fw_boss_hold_warden fw_boss_twin_warlocks fw_boss_corrupted_ancient fw_boss_doom_lord fw_boss_master_summoner fw_boss_demon_lord""")

_set("felwood", 6, 6, "assets/tiles/felwood/_src", """
    fw_moonwell_shrine fw_sentinel_hall fw_druid_treehouse fw_inn fw_hippogryph_roost fw_supply_house
    fw_timbermaw_lodge fw_timbermaw_totem fw_purified_moonwell fw_sentinel_tower fw_stake_barricade fw_sentinel_tent
    fw_jaedenar_gatehouse fw_taken_hall fw_summoning_dais fw_cult_tent fw_fel_obelisk fw_shard_cage
    fw_corrupted_tree fw_dead_ironwood fw_fel_crystals fw_fel_pool fw_fel_mushrooms fw_corrupted_log
    fw_infernal_crater fw_fel_brazier fw_demon_portal fw_deadwood_hut fw_deadwood_totem fw_demon_bones
    fw_ashenvale_tree fw_half_cleansed_tree fw_highborne_column fw_fallen_statue fw_highborne_arch fw_moonflowers""")

#: STONETALON (docs/stonetalon_art_prompts.md sheets 2 and 3, Kyle 15 Nov 2026). Both cut straight to the props
#: folder; the two buildings (the bunkhouse and the lookout tower) are copied on to assets/buildings by
#: tools/file_stonetalon_art.py.
_set("stonetalon_creatures", 6, 6, "assets/creatures/_src/stonetalon", """
    st_grim_warrior st_grim_shaman st_grim_hunter st_grim_brute st_grim_mystic st_grim_elder
    st_venture_logger st_venture_sawyer st_venture_demolitionist st_venture_foreman st_venture_rigger st_venture_shredder
    st_windshear_harpy st_windshear_witch st_cougar st_bull_elk st_bald_eagle st_black_bear
    st_ash_elemental st_pumice_golem st_steam_elemental st_basalt_elemental st_bark_beetle st_redwood_ancient
    st_beetle_mother st_sap_ooze st_canopy_owl st_sky_serpent st_risen_tauren st_risen_stalker
    st_boss_rigboss_gazzle st_boss_heartrot_queen st_boss_ambermaw st_boss_old_talonwing st_boss_topper_kezzik st_boss_the_eldest""")

_set("stonetalon_trees", 4, 4, "assets/tiles/stonetalon/props", """
    st_redwood_giant st_redwood_twin st_redwood_young st_redwood_ring
    st_sequoia_great st_sequoia_mature st_sequoia_scarred st_sequoia_young
    st_log_redwood st_sequoia_rootplate st_giant_snag st_logged_stump
    st_redwood_hollow st_nurse_log st_redwood_burl st_canopy_overlay""")

_set("stonetalon", 6, 6, "assets/tiles/stonetalon/props", """
    st_log_deck st_saw_rig st_steam_winch st_venture_bunkhouse st_shredder_wreck st_sawdust_burner
    st_log_sled st_sawdust_pile st_venture_sign st_powder_kegs st_venture_tower st_climbing_rig
    st_fumarole st_steam_vents st_obsidian_boulder st_lava_tube_mouth st_pumice_pile st_cinder_cone
    st_grim_war_totem st_grim_tent st_grim_drum st_grim_palisade st_grim_stone_circle st_grim_hide_rack
    st_harpy_nest st_wind_spire st_wind_arch st_mine_entrance st_ore_cart st_scout_camp
    st_rim_thorn_fence st_burial_platform st_rim_cairn st_ferns_big st_sorrel_patch st_moss_boulder""")

_set("dark_iron", 6, 5, "assets/buildings", """
    di_smeltery di_great_hall di_gatehouse di_barracks di_watchtower di_wall_section
    di_blast_furnace di_boiler_works di_mine_head di_crane_warehouse di_smithy di_vault
    di_inn di_shop di_shrine di_ruined_hall di_ruined_tower di_ruined_gate
    di_forge_anvil di_bellows di_crucible di_ore_cart di_steam_pipes di_slag_heap
    di_brazier di_crane_hook di_cage di_rune_obelisk di_dwarf_statue di_rubble""")

#: DARK IRON DWARVES (assets/creatures/_src/tempest_dark_iron_dwarves_sheet_30.png). People, not
#: buildings, but the same magenta sheet and the same need to keep relative scale. Cut to a staging
#: folder; tools/slice_dark_iron_dwarves.py files each one as an Onyxhollow NPC or a creature.
#: Rows: the guard, the trades, the casters, the castouts, the lords.
_set("dark_iron_dwarves", 6, 5, "assets/creatures/_src/dark_iron_dwarves", """
    did_guard_axe did_guard_spear did_crossbow did_captain did_cleaver did_sapper
    did_smith did_stoker did_miner did_engineer did_cooper did_scholar
    did_pyromancer did_censer did_runesmith did_shadowcaller did_geomancer did_alchemist
    did_chained did_ragged did_iron_mask did_crawler did_ash_cultist did_molten_brute
    did_thane did_warlord did_dark_seer did_gilded_engineer did_flame_lord did_elder""")

#: Kyle's market sheets, 15 Nov 2026 (docs/market_town_art_prompts.md). The Forsaken had three buildings and the
#: goblin ports fourteen; the props are the mailboxes by every inn and the market dressing.
_set("forsaken_town", 6, 5, "assets/buildings", """
    forsaken_inn forsaken_bank forsaken_auction_house forsaken_post_office forsaken_apothecary forsaken_general_store
    forsaken_blacksmith forsaken_tailor forsaken_mage_tower forsaken_shadow_chapel forsaken_bat_roost forsaken_barracks
    forsaken_house_large forsaken_house_medium_b forsaken_house_small_b forsaken_townhouse forsaken_house_row forsaken_crafter_house
    forsaken_mausoleum forsaken_crypt_entrance forsaken_well forsaken_cauldron_yard forsaken_gallows_square forsaken_town_hall_b
    forsaken_granary forsaken_storehouse forsaken_windmill forsaken_watch_tower forsaken_town_gate forsaken_stable""")

_set("goblin_town", 6, 5, "assets/buildings", """
    gob_auction_house gob_bank gob_post_office gob_inn gob_emporium gob_counting_house_b
    gob_engineering_workshop gob_alchemy_lab gob_shipwright gob_tavern_shack gob_fish_market gob_zeppelin_tower
    gob_house_large gob_house_medium gob_house_small gob_stacked_houses gob_houseboat gob_boarding_house
    gob_warehouse_b gob_cargo_crane gob_dock_office gob_lighthouse gob_customs_house gob_barracks
    gob_racing_garage gob_salvage_yard gob_shredder_hangar gob_water_tower gob_fireworks_shop gob_town_gate""")

#: AZSHARA (docs/azshara_art_prompts.md sheets 2 to 6, Kyle 17 Nov 2026). The Landing's and the Hold's sheets go
#: whole to assets/buildings (tl_ and tm_); sheet 6 goes whole to the Azshara creature folder and its 24 set pieces
#: (the fr_ and vz_ props, not the bosses or the elite guard) are moved on by hand to assets/tiles/dungeon_props.
_set("azshara_props", 6, 6, "assets/tiles/azshara/props", """
    az_autumn_tree az_gold_tree az_birch_trio az_autumn_log az_crimson_bush az_lichen_boulder
    az_broken_spire az_toppled_column az_moon_arch az_noble_statue az_ruin_wall az_dry_fountain
    az_drowned_spire az_barnacle_statue az_coral_arch az_drowned_obelisk az_coral_cluster az_giant_clam
    az_dig_scaffold az_relic_crate az_containment_pylon az_dig_cart az_survey_stakes az_covered_find
    az_arcane_crystal az_leyline_node az_crystal_tree az_scale_pile az_mana_tower az_glow_shrooms
    az_satyr_totem az_fel_bonfire az_cursed_tree az_wreck_prow az_naga_banner az_tide_altar""")
_set("talrendis", 6, 6, "assets/buildings", """
    tl_command_hall tl_inn tl_gatehouse tl_wind_rider_roost tl_quartermaster tl_dock
    tl_orc_barracks tl_orc_forge tl_war_tent tl_lumber_stack tl_stone_crane tl_log_watchtower
    tl_magister_pavilion tl_research_tent tl_ward_pylon tl_field_spire tl_scribes_canopy tl_mana_cell_rack
    tl_sorting_shed tl_relic_cage tl_rail_cart tl_stone_sledge tl_column_pile tl_vault_crate
    tl_split_wall tl_notice_board tl_shared_fire tl_sparring_ring tl_mess_table tl_signpost
    tl_orc_longboat tl_elf_skiff tl_dig_entrance tl_survey_tower tl_sandbags tl_cairn""")
_set("timbermaw_hold", 6, 6, "assets/buildings", """
    tm_elders_great_lodge tm_inn tm_long_hall tm_cliff_lodge tm_round_den tm_carvers_hall
    tm_cliff_terrace tm_stair_ramp tm_rope_bridge tm_cave_lodge tm_lookout tm_totem_gate
    tm_hive_tree tm_skep_row tm_honey_store tm_honey_press tm_candle_stand tm_smoke_pot
    tm_great_totem tm_ancestor_shrine tm_sacred_spring tm_bonfire_pit tm_paw_stone tm_drum_circle
    tm_smithy tm_tannery tm_market_stall tm_woodpile tm_herb_rack tm_supply_cache
    tm_deep_gate tm_gate_guard_post tm_warning_totem tm_rockfall tm_fel_crack tm_war_banner""")
_set("azshara_creatures", 6, 6, "assets/creatures/_src/azshara", """
    az_naga_siren az_naga_tidehunter az_naga_sea_witch az_naga_royal_guard az_naga_brute az_serpent_hatchling
    az_ghost_noble az_ghost_arcanist az_ghost_guard az_ghost_handmaiden az_ghost_hound az_ghost_tormented
    az_satyr_cursed az_satyr_sorcerer az_satyr_houndmaster az_felhound az_eredar_warlock az_doomguard_sentinel
    az_blue_drake az_blue_dragonspawn az_blue_whelp az_mana_wyrm_leader az_arcane_construct az_ley_beast
    az_rot_furbolg az_rot_shaman az_rot_beast az_spore_cloud az_root_horror az_rot_tender
    az_timber_wolf az_thunder_lizard az_shore_crab az_cliff_hippogryph az_autumn_treant az_russet_boar""")
_set("azshara_dungeons", 6, 6, "assets/creatures/_src/azshara", """
    fr_burial_niche fr_fel_mushrooms fr_rotten_beam fr_crystal_vein fr_corrupt_totem fr_ooze_pool
    fr_ritual_circle fr_root_wall fr_fungus_gate fr_root_cage fr_spore_vent fr_root_throne
    vz_drowned_colonnade vz_flooded_stair vz_coral_throne vz_fallen_chandelier vz_naga_shrine vz_drowned_shelf
    vz_vault_door vz_artifact_pedestal vz_water_mirror vz_treasure_pile vz_ancient_well vz_queens_throne
    fr_boss_mossjaw fr_boss_sporeheart fr_boss_kazthul fr_boss_thornblight fr_boss_xavras fr_elite_guard
    vz_boss_ssiriss vz_boss_vashjren vz_boss_chamberlain vz_boss_elaria vz_boss_revenant vz_boss_echo_queen""")
#: THE BANKS AND AUCTION HOUSES (docs/bank_auction_art_prompts.md, Kyle 17 Nov 2026): one grand bank (MerchantTusk's
#: tusk-coin sign) and one grand auction house (the gavel and scales) in each of six styles.
_set("bank_auction", 4, 3, "assets/buildings", """
    bank_orc ah_orc bank_forsaken ah_forsaken
    bank_tauren ah_tauren bank_blood_elf ah_blood_elf
    bank_goblin ah_goblin bank_human ah_human""")
_set("market_props", 6, 5, "assets/tiles/market/props", """
    mailbox_orc mailbox_orc_b mailbox_troll mailbox_forsaken mailbox_forsaken_b mailbox_tauren
    mailbox_tauren_b mailbox_goblin mail_tube_goblin parcel_cart mail_sacks notice_board
    podium_orc podium_goblin auction_block_forsaken trading_rock_tauren goods_table price_board
    crate_stack barrel_group ore_bar_pile cloth_rack herb_rack hide_frame
    strongbox merchant_scales counting_machine coin_chest auction_gong market_stall_small""")


#: SMOKE DRAWN OVER A MAGENTA KEY COMES BACK PURPLE. A generator asked for a lodge with a smoke hole
#: draws the plume semi-transparent, and whatever is behind it - the key - bleeds through. Keying then
#: gives a correctly-shaped wisp in the wrong colour, which is invisible against dark ground and obvious
#: against snow or pale grass.
#:
#: This cannot be a blanket despill: tauren decoration is full of legitimate violet beadwork and the
#: Aspen set has fireweed, which really is magenta. So it is opt-in per sprite and confined to the top
#: fraction of that sprite, where a plume lives and hanging beads do not.
#: {sprite: fraction of height treated, measured from the top}
DESPILL_TOP = {"tau_great_lodge": 0.22, "di_smeltery": 0.30, "di_boiler_works": 0.30,
               "di_steam_pipes": 0.30, "fw_infernal_crater": 0.45,
               "gob_alchemy_lab": 0.25, "forsaken_apothecary": 0.25, "gob_auction_house": 0.12}


def _despill_plume(cut, frac):
    """Neutralise magenta-cast pixels in the top `frac` of a sprite, keeping luminance and alpha."""
    out = cut.copy()
    h = out.shape[0]
    band = out[:max(1, int(h * frac))]
    rgb = band[..., :3]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    # Any strong colour cast on a SEMI-TRANSPARENT pixel in this band, not just magenta. Over-subtracting
    # the key leaves a green edge exactly where it removed a magenta one, so testing only for magenta
    # trades a purple wisp for a green one. Smoke is achromatic; the opaque roof ring below it is not
    # touched, which is what the alpha test protects.
    chroma = rgb.max(axis=-1) - rgb.min(axis=-1)
    a = band[..., 3]
    # Two cases, and it needs both. Restricting to semi-transparent pixels alone leaves the opaque magenta
    # smudge where the plume meets the smoke hole; testing only for magenta leaves the green edge the key
    # over-subtracted. Magenta is safe to treat at ANY alpha here because the structure underneath is brown
    # and orange - warm colours have b well BELOW g, so the roof ring never matches.
    magenta = (r - g > 22) & (b - g > 22) & (a > 8)
    cast = (chroma > 22) & (a > 8) & (a < 205)
    bad = magenta | cast
    if bad.any():
        lum = (0.299 * r + 0.587 * g + 0.114 * b)[bad]
        for ch in range(3):
            rgb[..., ch][bad] = lum
    return out


def _settles(name):
    """Entrance art that is a MASS - a cave mouth, a mound, a hull, a stair cut out of its wall -
    rather than something standing on posts. Kyle, 12 Nov, of the kobold dig on a riverbank and
    a ship's stair on a deck: "try to blend these better". A mass cut out with a hard edge reads
    as a sticker; a gate on two posts does not, and softening it would only eat the posts."""
    if not name.startswith("ent_"):
        return False
    return not name.startswith(("ent_gate_", "ent_town_", "ent_dock_"))


def _settle_into_ground(cut):
    """Fade a sprite's silhouette edge to nothing, a little at the top and a lot at the foot.

    The foot is where a prop meets the ground it was not painted on, so that is where the hard
    cut-out line shows; the top is sky-side and only needs the stair-step taken off. The fade is
    by distance from the silhouette's own edge, so holes in the art (the gap in a railing) fade
    too and nothing is blurred - colour is untouched, only alpha.
    """
    from scipy import ndimage
    out = cut.copy()
    a = out[..., 3]
    h = a.shape[0]
    dist = ndimage.distance_transform_edt(a > 40)
    width = 3.0 + 13.0 * (np.arange(h) / max(1, h - 1)) ** 1.5         # px: 3 at the top, 16 at the foot
    out[..., 3] = a * np.clip(dist / width[:, None], 0.0, 1.0) ** 0.8
    return out


#: A blob this big ANCHORS a cell - it is the building body. Buildings are far larger than icons, so the icon
#: slicer's 60px floor would let keying dirt anchor a cell on its own.
MIN_BLOB = 1500
#: ...but a detached chimney, banner, lantern, weathervane or wheel paddle is far SMALLER than that and must
#: still be merged into its building, so anything above plain keying noise is kept as long as its cell already
#: has an anchor. Found by testing: a 20x22 chimney left 10px clear of its roof is 440px and was being
#: silently dropped, which cost the sprite its whole top.
MIN_PART = 60


def slice_sheet(which, sheet_path, out_dir=None, preview=None):
    COLS, ROWS, default_out, NAMES = SETS[which]
    from scipy import ndimage
    out_dir = Path(out_dir) if out_dir else ROOT / default_out
    out_dir.mkdir(parents=True, exist_ok=True)

    im = Image.open(sheet_path).convert("RGB")
    W, H = im.size
    rgba = key_magenta(np.asarray(im).astype(np.float64))
    cw, ch = W / COLS, H / ROWS

    solid = rgba[..., 3] > 24
    solid[:4, :] = solid[-4:, :] = False          # a sheet edge that is not quite magenta is not a building
    solid[:, :4] = solid[:, -4:] = False
    # Dilation bridges a detached chimney or banner back onto its building. Too much of it welds NEIGHBOURING
    # buildings together instead: a tall sprite overflows its cell, touches the one in the next row, the merged
    # blob's centre lands in one cell and the other comes up empty. Found with the blood elf sheet, where the
    # grand spire (449px in a 250px row) swallowed the shop above it. Two is enough to catch a loose chimney
    # and not enough to cross the gap between two drawn buildings.
    labels, n = ndimage.label(ndimage.binary_dilation(solid, iterations=2))

    cells, parts = {}, {}
    for lab in range(1, n + 1):
        m = (labels == lab) & solid
        area = m.sum()
        if area < MIN_PART:
            continue
        ys, xs = np.where(m)
        key = (int(ys.mean() // ch), int(xs.mean() // cw))
        (cells if area >= MIN_BLOB else parts).setdefault(key, []).append(m)

    problems, written = [], []
    for idx, name in enumerate(NAMES):
        r, c = divmod(idx, COLS)
        blobs = cells.get((r, c))
        if not blobs:
            problems.append(f"{name}: no building found in cell r{r} c{c}")
            continue
        # A building is one object, but chimneys, banners and wheel paddles can key as their own blobs, so
        # everything whose centre lands in the cell is merged rather than taking only the largest.
        mask = np.logical_or.reduce(blobs + parts.get((r, c), []))
        ys, xs = np.where(mask)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        cut = rgba[y0:y1, x0:x1].copy()
        cut[..., 3] *= mask[y0:y1, x0:x1]         # drop a neighbour bleeding into this bounding box
        if name in DESPILL_TOP:
            cut = _despill_plume(cut, DESPILL_TOP[name])
        if _settles(name):
            cut = _settle_into_ground(cut)
        img = Image.fromarray(cut.astype(np.uint8), "RGBA")
        img.save(out_dir / f"{name}.png")
        written.append((name, img.size))
        n_extra = len(blobs) - 1 + len(parts.get((r, c), []))
        if n_extra:
            problems.append(f"{name}: {n_extra} detached part(s) merged in (chimney/banner?) - eyeball it")

    for (name, size) in written:
        print(f"  {name:28} {size[0]:4}x{size[1]:<4}")
    print(f"\n{len(written)}/{len(NAMES)} sliced -> {out_dir}")
    if written:
        tall = max(written, key=lambda w: w[1][1])
        short = min(written, key=lambda w: w[1][1])
        print(f"relative scale kept: tallest {tall[0]} {tall[1][1]}px, shortest {short[0]} {short[1][1]}px")
    for p in problems:
        print(f"  !! {p}")

    if preview:
        _preview(written, out_dir, preview)
    return written, problems


def _preview(written, out_dir, path):
    """One contact sheet of everything that was cut, on a mid grey so alpha fringing shows up."""
    cols = 6
    cells = [Image.open(out_dir / f"{n}.png") for (n, _) in written]
    cw = max(c.width for c in cells) + 16
    rh = max(c.height for c in cells) + 16
    rows = (len(cells) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cw, rows * rh), (110, 110, 115, 255))
    for i, c in enumerate(cells):
        r, k = divmod(i, cols)
        sheet.alpha_composite(c, (k * cw + (cw - c.width) // 2, r * rh + (rh - c.height) - 8))
    sheet.convert("RGB").save(path)
    print(f"preview -> {path}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2 or args[0] not in SETS:
        raise SystemExit(f"usage: slice_building_sheet.py <{'|'.join(SETS)}> <sheet.png> [--preview OUT]")
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    slice_sheet(args[0], args[1], preview=pv)
