"""Which sprite a creature draws, for dungeon floors and combat.

Kyle: "Currently trash mobs are red boxes and dungeon and cave bosses are generic things. We can
afford up to 5 sprite prompts. So about 36 sprites per sheet... Not every trash needs to be unique,
not every boss needs to be unique sprite. But we can get a lot of them."

WHY THIS IS KEYED ON THE NAME AND NOT ON `template`. boss_icons.py maps the 12 stat templates to 8
tinted portraits, which is why every boss in the game looks like one of eight things: `template` is
a COMBAT archetype (how it fights) and the player reads a SPECIES (what it is). "Hexxer Vul'jin"
and "Searing Flamecaller" are both humanoid_caster and should not be the same picture. 439 creatures
appear in caves and 343 of them are bosses, so template-level art was always going to be generic.

So: first match wins, patterns run against the creature's NAME, and the stat template is only the
fallback when nothing matches. One sprite serves many creatures on purpose - every gnoll in the
game is the gnoll sprite, which is exactly the "not every trash needs to be unique" Kyle asked for.

THE SPRITE LIST IS THE ART ORDER. SHEETS below is the thing the prompts in
claude/dungeon_sprite_prompts.md generate, 36 to a sheet, and tools/qa_creature_sprites.py checks
that every cave creature lands on a sprite that some sheet actually produces. A pattern pointing at
a sprite nobody drew is a red box in a dungeon, found by a player rather than by us.
"""
import re
from pathlib import Path

SPRITE_DIR = Path(__file__).parent / "assets" / "creatures"

#: sheet name -> its sprite ids IN DRAW ORDER: the order the art prompt lists them, which is
#: the order the generator lays them out and therefore the order the slicer reads them back.
#:
#: THIS LIST USED TO BE ALPHABETICAL, because it was generated with sorted(). That is a different
#: order from the prompt's, so slicing "in order" would have written the three spiders out as
#: crab_giant and shifted every id on every sheet - including the two sheets whose COUNT matched,
#: where nothing would look wrong until a player met a gnoll drawing as a dwarf. Count agreement
#: is not order agreement. Keep this in the prompt order; reorder the prompt and reorder this.
#:
#: The counts are what the generator ACTUALLY produced, read off the staged contact sheets - it
#: gave one fewer syndicate rogue, boar and skeleton archer than asked, and one extra felhound
#: and two extra spore caps. Asking for a count does not get you that count.
SHEETS = {
    # ---- the Plaguelands (Kyle's sheets 6, 7 and 8, 16 Nov; tools/slice_building_sheet.py, docs/plaguelands_art_prompts.md)
    'plaguelands_creatures': ['pl_plague_eruptor', 'pl_flesh_golem', 'pl_gargoyle', 'pl_crypt_fiend', 'pl_death_knight', 'pl_skeletal_warhorse', 'pl_plaguebat', 'pl_plaguehound', 'pl_carrion_grub', 'pl_frenzied_ghoul', 'pl_skeletal_mage', 'pl_wailing_spirit', 'pl_cult_neophyte', 'pl_cult_plaguebringer', 'pl_necrolyte', 'pl_cauldron_tender', 'pl_dark_caster', 'pl_cult_lieutenant', 'pl_diseased_bear', 'pl_plagued_wolf', 'pl_carrion_vulture', 'pl_blighted_stag', 'pl_plague_slime', 'pl_plaguewood_spider', 'pl_forsaken_apothecary', 'pl_deathguard', 'ad_crusader', 'ad_priestess', 'pl_darrowshire_ghost', 'zm_troll_warrior', 'pl_boss_abomination_farmer', 'pl_boss_lich_magistrate', 'pl_boss_brood_queen', 'pl_boss_bone_colossus', 'pl_rare_plague_rider', 'pl_rare_arch_necromancer'],
    'plaguelands_scarlet': ['sc_monk', 'sc_zealot', 'sc_adept', 'sc_chaplain', 'sc_myrmidon', 'sc_centurion', 'sc_knight', 'sc_inquisitor', 'sc_judicator', 'sc_arcanist', 'sc_war_hound', 'sc_cavalier', 'sc_tp_crusader', 'sc_tp_sniper', 'sc_tp_drill_sergeant', 'sc_tp_inquisitor', 'sc_tp_champion', 'sc_tp_cleric', 'pf_rory_callahan', 'pf_knight', 'pf_chaplain', 'pf_scout', 'pf_sentry', 'pf_quartermaster', 'hg_boss_gatewarden', 'hg_boss_quartermaster', 'hg_boss_pyre_sisters', 'hg_boss_drillmaster', 'hg_boss_high_inquisitor', 'hg_boss_kennelmaster', 'hg_boss_arcanist', 'hg_boss_lady_marden', 'hg_boss_crimson_choir', 'hg_boss_volkov', 'hg_boss_victor_hale', 'hg_scarlet_charger'],
    'plaguelands_dungeon_bosses': ['sm_boss_interrogator', 'sm_boss_bloodmage', 'sm_boss_houndmaster', 'sm_boss_arcanist', 'sm_boss_champion', 'sm_boss_commander', 'sm_boss_high_inquisitor', 'scholo_boss_gargoyle', 'scholo_boss_ghost_lady', 'scholo_boss_bone_construct', 'scholo_boss_frost_lich', 'scholo_boss_alchemist', 'scholo_boss_librarian', 'scholo_boss_instructor', 'scholo_boss_noble_lady', 'scholo_boss_noble_lord', 'scholo_boss_headmaster', 'scholo_ghost_servant', 'strat_boss_ghoul_runt', 'strat_boss_cannon_master', 'strat_boss_archivist', 'strat_boss_grand_crusader', 'strat_boss_dreadlord', 'strat_boss_magistrate', 'strat_boss_crypt_lord', 'strat_boss_baroness', 'strat_boss_lich', 'strat_boss_flesh_golem', 'strat_boss_baron', 'strat_deathcharger', 'pl_boss_cult_necromancer', 'pl_silver_hand_ghost', 'pl_boss_gate_guardian', 'pl_boss_eye_construct', 'pl_boss_chorus_leader', 'pl_boss_abom_butcher'],
    # ---- the Plaguelands' hidden places (Kyle's sheet 10, 17 Nov; docs/plaguelands_secrets_art_prompts.md)
    'plaguelands_secrets': ['ps_woolly_mammoth', 'ps_woolly_rhino', 'ps_dire_wolf', 'ps_giant_elk', 'ps_cave_bear', 'ps_steppe_bison', 'ps_boss_mammoth_matriarch', 'ps_boss_cave_lion', 'ps_boss_walking_glacier', 'ps_stone_age_woman', 'ps_palaeontologist', 'ps_frozen_hunter', 'ps_mere_wisp', 'ps_fen_drowned', 'ps_fen_owl', 'ps_bog_lurker', 'ps_barrow_shade', 'ps_bog_hulk', 'ps_boss_lamplighter', 'ps_boss_bog_hag', 'ps_finnish_scientist', 'ps_forsaken_fisherwoman', 'ps_bog_eel', 'ps_reed_heron', 'ps_eversong_lynx', 'ps_mana_wyrm', 'ps_arcane_remnant', 'ps_sentinel_shade', 'ps_elf_ranger', 'ps_elf_quartermaster', 'ps_boss_magister', 'ps_boss_breach_gnawer', 'ps_gaunt_ghoul', 'ps_scourge_necromancer', 'ps_wardstone', 'ps_dead_elf_ranger'],
    # ---- Deadwind Pass (Kyle's sheets 5 and 7, 18 Nov 2026; docs/deadwind_art_prompts.md, tools/build_deadwind_content.py).
    #      dw_twice_ogre and dw_echo are people (Grull the Younger, the Bridge Echo), so they're parked here on purpose
    'deadwind_creatures': ['dw_tumour_wolf', 'dw_three_age_wolf', 'dw_many_eyed_crow', 'dw_pustule_boar', 'dw_fused_bat', 'dw_cage_deer', 'dw_ogre_brute', 'dw_two_faced_ogre', 'dw_sore_shaman', 'dw_twice_ogre', 'dw_chained_mauler', 'dw_leaking_ogre', 'dw_echo', 'dw_aged_walker', 'dw_shard_wraith', 'dw_many_moments', 'dw_flicker_hound', 'dw_stopped_soldier', 'dw_spectral_servant', 'dw_spectral_stablehand', 'dw_violet_armour', 'dw_book_flock', 'dw_arcane_anomaly', 'dw_dancing_ghost', 'dw_slag_crawler', 'dw_bloated_walker', 'dw_fused_abomination', 'dw_bone_ooze', 'dw_many_arms', 'dw_seep_wyrm', 'dw_widow', 'dw_widow_hatchlings', 'dw_broodmother', 'dw_cave_burrower', 'dw_cave_leech', 'dw_mud_horror'],
    'deadwind_bosses': ['fz_boss_gristlemaw', 'fz_boss_stopped_man', 'fz_boss_vexis', 'fz_boss_glow_eater', 'fz_boss_archivist', 'fz_boss_wound_heart', 'dw_boss_silk_mother', 'dw_boss_drowned_thing', 'dw_rare_three_heads', 'dw_rare_wagon_driver', 'dw_rare_moggrak', 'dw_rare_crow_king'],
    # ---- Azshara (Kyle's sheet 5, 17 Nov; docs/azshara_art_prompts.md)
    'azshara_creatures': ['az_naga_siren', 'az_naga_tidehunter', 'az_naga_sea_witch', 'az_naga_royal_guard', 'az_naga_brute', 'az_serpent_hatchling', 'az_ghost_noble', 'az_ghost_arcanist', 'az_ghost_guard', 'az_ghost_handmaiden', 'az_ghost_hound', 'az_ghost_tormented', 'az_satyr_cursed', 'az_satyr_sorcerer', 'az_satyr_houndmaster', 'az_felhound', 'az_eredar_warlock', 'az_doomguard_sentinel', 'az_blue_drake', 'az_blue_dragonspawn', 'az_blue_whelp', 'az_mana_wyrm_leader', 'az_arcane_construct', 'az_ley_beast', 'az_rot_furbolg', 'az_rot_shaman', 'az_rot_beast', 'az_spore_cloud', 'az_root_horror', 'az_rot_tender', 'az_timber_wolf', 'az_thunder_lizard', 'az_shore_crab', 'az_cliff_hippogryph', 'az_autumn_treant', 'az_russet_boar'],
    # ---- the Drowned Palace's bosses (Kyle's Azshara dungeon sheet, row 6; tools/build_drowned_palace_content.py)
    'drowned_palace': ['vz_boss_ssiriss', 'vz_boss_vashjren', 'vz_boss_chamberlain', 'vz_boss_elaria', 'vz_boss_revenant', 'vz_boss_echo_queen'],
    # ---- the Rotroot Deeps' bosses (Kyle's sheet, 18 Nov 2026; tools/build_rotroot_deeps_content.py)
    'rotroot_deeps': ['fr_boss_mossjaw', 'fr_boss_sporeheart', 'fr_boss_kazthul', 'fr_boss_thornblight', 'fr_boss_xavras', 'fr_elite_guard'],
    # ---- Stonetalon (Kyle's sheet, 15 Nov; docs/stonetalon_art_prompts.md sheet 4)
    'stonetalon': ['st_grim_warrior', 'st_grim_shaman', 'st_grim_hunter', 'st_grim_brute', 'st_grim_mystic', 'st_grim_elder', 'st_venture_logger', 'st_venture_sawyer', 'st_venture_demolitionist', 'st_venture_foreman', 'st_venture_rigger', 'st_venture_shredder', 'st_windshear_harpy', 'st_windshear_witch', 'st_cougar', 'st_bull_elk', 'st_bald_eagle', 'st_black_bear', 'st_ash_elemental', 'st_pumice_golem', 'st_steam_elemental', 'st_basalt_elemental', 'st_bark_beetle', 'st_redwood_ancient', 'st_beetle_mother', 'st_sap_ooze', 'st_canopy_owl', 'st_sky_serpent', 'st_risen_tauren', 'st_risen_stalker', 'st_boss_rigboss_gazzle', 'st_boss_heartrot_queen', 'st_boss_ambermaw', 'st_boss_old_talonwing', 'st_boss_topper_kezzik', 'st_boss_the_eldest'],
    # ---- Felwood (Kyle's sheet, 14 Nov; tools/file_felwood_art.py)
    'felwood': ['fw_blighted_wolf', 'fw_boss_corrupted_ancient', 'fw_boss_demon_lord', 'fw_boss_doom_lord', 'fw_boss_hold_warden', 'fw_boss_master_summoner', 'fw_boss_twin_warlocks', 'fw_bound_voidwalker', 'fw_council_acolyte', 'fw_council_high_warlock', 'fw_council_summoner', 'fw_council_warlock', 'fw_deadwood_alpha', 'fw_deadwood_gardener', 'fw_deadwood_pathfinder', 'fw_deadwood_shaman', 'fw_deadwood_warrior', 'fw_deadwood_watcher', 'fw_doomguard', 'fw_entropic_horror', 'fw_eredar_warlock', 'fw_fel_bear', 'fw_felguard', 'fw_felhound', 'fw_hound_handler', 'fw_imp', 'fw_infernal', 'fw_jadefire_stag', 'fw_satyr_felsworn', 'fw_satyr_hellcaller', 'fw_satyr_lord', 'fw_satyr_rogue', 'fw_satyr_shadowstalker', 'fw_satyr_trickster', 'fw_toxic_ooze', 'fw_warpwood_treant'],
    # ---- 1. the people of the dungeons. 208 cave creatures run on humanoid_* templates,
    #    which is why this sheet is the biggest.
    'humanoids': [
        'bandit_human_1', 'bandit_human_2', 'bandit_human_3', 'cultist_robed_1',
        'cultist_robed_2', 'cultist_robed_3', 'syndicate_rogue_1', 'centaur_1',
        'warden_armoured', 'pirate_captain', 'pirate_cutthroat_1', 'quilboar_1',
        'noble_armoured', 'troll_axe_1', 'champion_plate', 'forsaken_soldier_1',
        'harpy_1', 'matriarch_brood', 'cultist_acolyte', 'pirate_bosun',
        'satyr', 'cult_overseer', 'priest_hooded', 'troll_witchdoctor',
        'furbolg', 'kobold_1', 'dwarf_excavator', 'fel_cultist',
        'forsaken_apothecary', 'goblin_sapper_1', 'archmage_robed', 'executioner_hooded',
        'gnoll_1', 'hunter_ranger', 'ogre_1', 'trogg',
        'goblin_overseer', 'harpy_matriarch', 'orc_deserter', 'quilboar_geomancer',
    ],
    # ---- 2. beasts.
    'beasts': [
        'worg_1', 'worg_2', 'worg_3', 'bear_1',
        'bear_2', 'bear_3', 'boar_1', 'boar_2',
        'panther_1', 'panther_2', 'crocolisk_1', 'crocolisk_2',
        'vulture_1', 'vulture_2', 'kodo_1', 'kodo_2',
        'serpent_1', 'serpent_2', 'hyena_1', 'hyena_2',
        'mutated_thing_1', 'mutated_thing_2', 'raptor_1', 'raptor_2',
        'gorilla_1', 'gorilla_2', 'scorpion', 'basilisk',
        'stag', 'lizard_rock', 'saber_cat', 'ram',
        'thresher', 'toad_giant', 'turtle_snapping', 'bat',
    ],
    # ---- 3. vermin, swarms and the wet things.
    'vermin_aquatic': [
        'spider_1', 'spider_2', 'spider_3', 'drowned_sailor_1',
        'drowned_sailor_2', 'murloc_1', 'murloc_2', 'crawler_shell_1',
        'crawler_shell_2', 'tide_lurker_1', 'tide_lurker_2', 'rat_plague_1',
        'rat_plague_2', 'silithid_worker_1', 'silithid_worker_2', 'eel_electric_1',
        'eel_electric_2', 'spider_broodmother_1', 'spider_broodmother_2', 'crab_giant_1',
        'crab_giant_2', 'naga_myrmidon_1', 'naga_myrmidon_2', 'ooze_acid_1',
        'ooze_acid_2', 'slime_green_1', 'slime_green_2', 'tentacle_horror_1',
        'tentacle_horror_2', 'maggot', 'reefcrawler', 'spider_hatchling',
        'wasp', 'naga_warrior', 'sea_witch',
    ],
    # ---- 4. undead and demons.
    'undead_demon': [
        'zombie_1', 'zombie_2', 'zombie_3', 'zombie_4',
        'skeleton_archer', 'skeleton_marksman', 'wraith_1', 'wraith_2',
        'wraith_3', 'felhound_1', 'felhound_2', 'felhound_3',
        'skeleton_warrior_1', 'skeleton_warrior_2', 'ghoul_1', 'ghoul_2',
        'imp_1', 'imp_2', 'voidwalker_1', 'voidwalker_2',
        'abomination_1', 'abomination_2', 'spectre_1', 'spectre_2',
        'crypt_fiend_1', 'crypt_fiend_2', 'demon_brute_1', 'demon_brute_2',
        'doomguard_1', 'doomguard_2', 'revenant_1', 'revenant_2',
        'banshee', 'necromancer',
    ],
    # ---- 5. elementals, plants and constructs.
    'elemental_plant': [
        'golem_stone_1', 'golem_stone_2', 'golem_stone_3', 'golem_stone_4',
        'elemental_fire_1', 'elemental_fire_2', 'elemental_fire_3', 'elemental_fire_4',
        'vine_strangler_1', 'vine_strangler_2', 'vine_strangler_3', 'elemental_air_1',
        'elemental_air_2', 'elemental_air_3', 'spore_cap_1', 'spore_cap_2',
        'spore_cap_3', 'spore_cap_4', 'spore_cap_5', 'treant_1',
        'treant_2', 'bog_lord_1', 'bog_lord_2', 'crystal_shardling_1',
        'crystal_shardling_2', 'lattice_grown_1', 'lattice_grown_2', 'wisp_1',
        'wisp_2', 'elemental_earth_1', 'elemental_earth_2', 'elemental_water',
        'sapling_thorn', 'crystal_sentinel', 'elemental_arcane',
    ],
    # ---- 6. more of the people, and the factions that had no sprite at all.
    'humanoids_2': [
        'bandit_human_4', 'bandit_human_5', 'bandit_human_6', 'cultist_robed_4',
        'cultist_robed_5', 'cultist_robed_6', 'syndicate_rogue_2', 'syndicate_rogue_3',
        'quilboar_2', 'quilboar_3', 'quilboar_4', 'centaur_2',
        'centaur_3', 'troll_axe_2', 'troll_axe_3', 'harpy_2',
        'harpy_3', 'pirate_cutthroat_2', 'ogre_2', 'forsaken_soldier_2',
        'scarlet_crusader', 'scarlet_priest', 'scarlet_archer', 'twilight_cultist',
        'bloodelf_magister', 'nightelf_sentinel', 'human_militia', 'human_marine',
        'worgen_1', 'worgen_2', 'houndmaster', 'tauren_brave',
        'murloc_oracle', 'kobold_2', 'gnoll_2', 'goblin_sapper_2',
    ],
    # ---- 7. more beasts, and the species that were drawing as the wrong animal.
    'beasts_2': [
        'bear_4', 'bear_5', 'bear_6', 'worg_4',
        'worg_5', 'worg_6', 'boar_3', 'boar_4',
        'spider_4', 'spider_5', 'zombie_5', 'zombie_6',
        'drowned_sailor_3', 'murloc_3', 'murloc_4', 'silithid_worker_3',
        'silithid_worker_4', 'crawler_shell_3', 'crawler_shell_4', 'tide_lurker_3',
        'raptor_3', 'raptor_4', 'panther_3', 'panther_4',
        'vulture_3', 'kodo_3', 'yeti_1', 'yeti_2',
        'scarecrow_golem', 'dragon_whelp', 'dragon_whelp_bronze', 'mountain_giant_granite',
        'mountain_giant_sandstone', 'sprite_darter', 'ghoul_gaunt', 'wraith_pale',
    ],
    # ---- the Dark Iron dwarves sheet (tools/slice_dark_iron_dwarves.py). Four of its thirty
    #    figures are creatures - the Castouts of The Black Strand; the rest are Onyxhollow's people.
    'dark_iron': [
        'dark_iron_digger', 'dark_iron_cutthroat', 'dark_iron_slagcaller', 'dark_iron_warlord',
    ],
}

#: sprite id -> how many different looks of it the sheets draw, as <id>_1 .. <id>_n.
#: DERIVED FROM USE, not chosen: 78 creatures land on bandit_human and 62 on worg, so those
#: get four looks each, while a sprite one creature uses gets one. The variant is picked by
#: hashing the creature's NAME, so no rule has to know about them and the same creature is
#: always the same picture - the point is that a room of gnolls is not one gnoll stamped out
#: eight times, which is what Kyle means by "not every trash needs to be unique" still
#: leaving room for "but we can get a lot of them".
VARIANTS = {
    'abomination': 2,
    'bandit_human': 6,
    'bear': 6,
    'boar': 4,
    'bog_lord': 2,
    'centaur': 3,
    'crab_giant': 2,
    'crawler_shell': 4,
    'crocolisk': 2,
    'crypt_fiend': 2,
    'crystal_shardling': 2,
    'cultist_robed': 6,
    'demon_brute': 2,
    'doomguard': 2,
    'drowned_sailor': 3,
    'eel_electric': 2,
    'elemental_air': 3,
    'elemental_earth': 2,
    'elemental_fire': 4,
    'felhound': 3,
    'forsaken_soldier': 2,
    'ghoul': 2,
    'gnoll': 2,
    'goblin_sapper': 2,
    'golem_stone': 4,
    'gorilla': 2,
    'harpy': 3,
    'hyena': 2,
    'imp': 2,
    'kobold': 2,
    'kodo': 3,
    'lattice_grown': 2,
    'murloc': 4,
    'mutated_thing': 2,
    'naga_myrmidon': 2,
    'ogre': 2,
    'ooze_acid': 2,
    'panther': 4,
    'pirate_cutthroat': 2,
    'quilboar': 4,
    'raptor': 4,
    'rat_plague': 2,
    'revenant': 2,
    'serpent': 2,
    'silithid_worker': 4,
    'skeleton_warrior': 2,
    'slime_green': 2,
    'spectre': 2,
    'spider': 5,
    'spider_broodmother': 2,
    'spore_cap': 5,
    'syndicate_rogue': 3,
    'tentacle_horror': 2,
    'tide_lurker': 3,
    'treant': 2,
    'troll_axe': 3,
    'vine_strangler': 3,
    'voidwalker': 2,
    'vulture': 3,
    'wisp': 2,
    'worg': 6,
    'worgen': 2,
    'wraith': 3,
    'yeti': 2,
    'zombie': 6,
}

#: sprite id -> set of every sprite the art actually produces.
ALL_SPRITES = {s for v in SHEETS.values() for s in v}

#: FIRST MATCH WINS, so order matters - the specific sits above the general. Each entry is
#: (compiled pattern on the creature NAME, sprite id).
_RULES = [
    # AZSHARA'S CAVES (tools/build_azshara_caves_content.py): exact names, each to Kyle's Azshara creature sheet.
    # Haldarr borrows Felwood's satyr lord and Hetaera a sea serpent until they have their own art.
    (r"^haldarr\ cursed$", "az_satyr_cursed"),
    (r"^haldarr\ fel-sorcerer$", "az_satyr_sorcerer"),
    (r"^haldarr\ houndmaster$", "az_satyr_houndmaster"),
    (r"^crystalback\ felhound$", "az_felhound"),
    (r"^bound\ highborne\ servant$", "az_ghost_handmaiden"),
    (r"^haldarr\ the\ hornlord$", "fw_satyr_lord"),
    (r"^the\ bound\ magister$", "az_ghost_arcanist"),
    (r"^clutch\ tidehunter$", "az_naga_tidehunter"),
    (r"^clutch\ siren$", "az_naga_siren"),
    (r"^clutch\ brute$", "az_naga_brute"),
    (r"^hetaera's\ brood$", "az_serpent_hatchling"),
    (r"^barnacled\ shorecrab$", "az_shore_crab"),
    (r"^tide-priestess\ sel'thira$", "az_naga_sea_witch"),
    (r"^hetaera$", "serpent_2"),
    # DEADWIND PASS (tools/build_deadwind_content.py, 18 Nov 2026): exact names, Kyle's Deadwind creature sheets.
    # dw_twice_ogre and dw_echo are people (Grull and the Bridge Echo) and never drawn on a hostile.
    (r"^tumour\ wolf$", "dw_tumour_wolf"),
    (r"^pustule\ boar$", "dw_pustule_boar"),
    (r"^many\-eyed\ crow$", "dw_many_eyed_crow"),
    (r"^fused\ bat$", "dw_fused_bat"),
    (r"^tunnel\ slagcrawler$", "dw_slag_crawler"),
    (r"^plot\ risen$", "dw_aged_walker"),
    (r"^grave\ ooze$", "dw_bone_ooze"),
    (r"^grosh'gok\ brute$", "dw_ogre_brute"),
    (r"^grosh'gok\ two\-face$", "dw_two_faced_ogre"),
    (r"^grosh'gok\ sore\-shaman$", "dw_sore_shaman"),
    (r"^chained\ mauler$", "dw_chained_mauler"),
    (r"^deadwind\ widow$", "dw_widow"),
    (r"^widow\ hatchlings$", "dw_widow_hatchlings"),
    (r"^glowsac\ broodmother$", "dw_broodmother"),
    (r"^sickwater\ leech$", "dw_cave_leech"),
    (r"^tarn\ horror$", "dw_mud_horror"),
    (r"^dissolving\ stag$", "dw_cage_deer"),
    (r"^the\ wagon\ driver$", "dw_rare_wagon_driver"),
    (r"^mog'grak\ the\ twice\-born$", "dw_rare_moggrak"),
    (r"^three\-age\ wolf$", "dw_three_age_wolf"),
    (r"^flicker\ hound$", "dw_flicker_hound"),
    (r"^gorge\ slagcrawler$", "dw_slag_crawler"),
    (r"^seep\ wyrm$", "dw_seep_wyrm"),
    (r"^bridge\ onlooker$", "dw_aged_walker"),
    (r"^hollow\ mudhorror$", "dw_mud_horror"),
    (r"^shard\ wraith$", "dw_shard_wraith"),
    (r"^many\ moments$", "dw_many_moments"),
    (r"^arcane\ anomaly$", "dw_arcane_anomaly"),
    (r"^spectral\ servant$", "dw_spectral_servant"),
    (r"^spectral\ stablehand$", "dw_spectral_stablehand"),
    (r"^ballroom\ phantom$", "dw_dancing_ghost"),
    (r"^violet\ sentinel$", "dw_violet_armour"),
    (r"^book\ flock$", "dw_book_flock"),
    (r"^bloated\ walker$", "dw_bloated_walker"),
    (r"^fused\ mass$", "dw_fused_abomination"),
    (r"^many\-armed\ thing$", "dw_many_arms"),
    (r"^old\ three\-heads$", "dw_rare_three_heads"),
    (r"^the\ crow\ king$", "dw_rare_crow_king"),
    (r"^funnel\ widow$", "dw_widow"),
    (r"^nest\ hatchlings$", "dw_widow_hatchlings"),
    (r"^cocoon\ burrower$", "dw_cave_burrower"),
    (r"^the\ silk\ mother$", "dw_boss_silk_mother"),
    (r"^seep\ leech$", "dw_cave_leech"),
    (r"^drain\ horror$", "dw_mud_horror"),
    (r"^bloated\ drowner$", "dw_bloated_walker"),
    (r"^the\ drowned\ thing$", "dw_boss_drowned_thing"),
    (r"^exclusion\ ogre$", "dw_leaking_ogre"),
    (r"^heaped\ abomination$", "dw_fused_abomination"),
    (r"^bursting\ walker$", "dw_bloated_walker"),
    (r"^brood\ seepwidow$", "dw_widow"),
    (r"^brood\ hatchling\ swarm$", "dw_widow_hatchlings"),
    (r"^brood\ burrower$", "dw_cave_burrower"),
    (r"^bubbler\ slagcrawler$", "dw_slag_crawler"),
    (r"^bubbler\ wyrm$", "dw_seep_wyrm"),
    (r"^bubbler\ ooze$", "dw_bone_ooze"),
    (r"^archive\ wraith$", "dw_shard_wraith"),
    (r"^archive\ anomaly$", "dw_arcane_anomaly"),
    (r"^hollow\ guardian$", "dw_violet_armour"),
    (r"^swarming\ pages$", "dw_book_flock"),
    (r"^stopped\ volunteer$", "dw_stopped_soldier"),
    (r"^moment\ without\ end$", "dw_many_moments"),
    (r"^aged\ volunteer$", "dw_aged_walker"),
    (r"^gristlemaw$", "fz_boss_gristlemaw"),
    (r"^broodmother\ vexis$", "fz_boss_vexis"),
    (r"^the\ glow\-eater$", "fz_boss_glow_eater"),
    (r"^archivist\ nine$", "fz_boss_archivist"),
    (r"^the\ stopped\ man$", "fz_boss_stopped_man"),
    (r"^the\ wound's\ heart$", "fz_boss_wound_heart"),
    # FERALAS'S OPEN WORLD (generated by tools/build_feralas_openworld.py; do not edit by hand)
    (r"^longtooth\ runner$", "fe_longtooth_wolf"),
    (r"^feralas\ stag$", "stag"),
    (r"^feralas\ sprite\ darter$", "sprite_darter"),
    (r"^woodpaw\ reaver$", "fe_woodpaw_reaver"),
    (r"^woodpaw\ trapper$", "fe_woodpaw_trapper"),
    (r"^woodpaw\ mystic$", "fe_woodpaw_mystic"),
    (r"^woodpaw\ brute$", "fe_woodpaw_brute"),
    (r"^woodpaw\ hyena$", "fe_hyena"),
    (r"^lower\ wilds\ crocolisk$", "crocolisk_2"),
    (r"^ironfur\ bear$", "fe_ironfur_bear"),
    (r"^grimtotem\ usurper$", "st_grim_warrior"),
    (r"^grimtotem\ bonecaller$", "st_grim_shaman"),
    (r"^grimtotem\ earthbreaker$", "st_grim_brute"),
    (r"^grimtotem\ pathfinder$", "st_grim_hunter"),
    (r"^gordunni\ brute$", "fe_gordunni_brute"),
    (r"^gordunni\ ogre\ mage$", "fe_gordunni_mage"),
    (r"^gordunni\ shaman$", "fe_gordunni_shaman"),
    (r"^gordunni\ mauler$", "fe_gordunni_mauler"),
    (r"^gordunni\ warlord$", "fe_gordunni_warlord"),
    (r"^zukk'ash\ tunneler$", "fe_silithid_tunneler"),
    (r"^zukk'ash\ swarmer$", "fe_silithid_swarmer"),
    (r"^grimfang$", "fe_woodpaw_alpha"),
    (r"^old\ grizzlegut$", "fe_ironfur_bear"),
    (r"^pathfinder\ harrok$", "st_grim_elder"),
    (r"^gash'tok\ the\ gatekeeper$", "fe_gordunni_lord"),
    (r"^fog\ grove\ elk$", "fe_roosevelt_elk"),
    (r"^feralas\ stalker$", "fe_feralas_stalker"),
    (r"^fog\ grove\ ironfur$", "fe_ironfur_bear"),
    (r"^isildien\ brute$", "fe_gordunni_brute"),
    (r"^isildien\ ogre\ mage$", "fe_gordunni_mage"),
    (r"^isildien\ digger$", "fe_gordunni_brute"),
    (r"^hatecrest\ raider$", "fe_naga_raider"),
    (r"^hatecrest\ ruin\-digger$", "fe_naga_digger"),
    (r"^hatecrest\ tide\ priestess$", "fe_naga_priestess"),
    (r"^hatecrest\ makrura$", "fe_makrura"),
    (r"^hatecrest\ coral\ guardian$", "fe_naga_guardian"),
    (r"^sardor\ hydra$", "fe_coast_hydra"),
    (r"^dread\ chimaera$", "fe_chimaera"),
    (r"^frayfeather\ skystalker$", "fe_skystalker"),
    (r"^frayfeather\ windwing$", "fe_windwing"),
    (r"^old\ seven\-point$", "fe_roosevelt_elk"),
    (r"^skull\-taker\ murg$", "fe_gordunni_warlord"),
    (r"^tidelord\ ssaravel$", "fe_naga_priestess"),
    (r"^the\ dread\ matriarch$", "fe_chimaera_matriarch"),
    (r"^antilus\ the\ soarer$", "fe_skystalker"),
    (r"^colossal\ land\ walker$", "fe_forest_giant"),
    (r"^colossal\ sea\ walker$", "fe_sea_giant"),
    (r"^rage\ scar\ yeti$", "fe_rage_scar_yeti"),
    (r"^rage\ scar\ matriarch$", "fe_rage_scar_matriarch"),
    (r"^ravenwind\ raider$", "fe_naga_raider"),
    (r"^ravenwind\ sea\ witch$", "fe_naga_priestess"),
    (r"^ravenwind\ guardian$", "fe_naga_guardian"),
    (r"^ravenwind\ hydra$", "fe_coast_hydra"),
    (r"^dream\ bough\ darter$", "sprite_darter"),
    (r"^dream\-touched\ treant$", "treant_2"),
    (r"^the\ old\ walker$", "fe_forest_giant"),
    (r"^rage\ scar\ old\ bull$", "fe_rage_scar_matriarch"),
    (r"^lady\ szaressa$", "fe_naga_priestess"),
    # END FERALAS'S OPEN WORLD
    # THE ZUKK'ASH HIVE (generated by tools/build_zukkash_hive_content.py; do not edit by hand)
    (r"^zukk'ash\ hive\ worker$", "fe_silithid_tunneler"),
    (r"^zukk'ash\ hive\ warrior$", "fe_silithid_warrior"),
    (r"^zukk'ash\ wasp$", "fe_silithid_swarmer"),
    (r"^zukk'ash\ ravager$", "fe_silithid_ravager"),
    (r"^zukk'ash\ resin\-spitter$", "fe_resin_spitter"),
    (r"^the\ deep\ mother$", "fe_boss_deep_mother"),
    (r"^tunnelmaster\ zix'tal$", "fe_silithid_ravager"),
    # END THE ZUKK'ASH HIVE
    # AZSHARA'S OPEN WORLD (tools/build_azshara_openworld.py): exact names, Kyle's Azshara creature sheet, with
    # Felwood's satyrs and imp in the camps.
    (r"^autumn\ timber\ wolf$", "az_timber_wolf"),
    (r"^russet\ boar$", "az_russet_boar"),
    (r"^cliff\ hippogryph$", "az_cliff_hippogryph"),
    (r"^autumn\ treant$", "az_autumn_treant"),
    (r"^shadowsong\ sentinel$", "az_ghost_guard"),
    (r"^ravencrest\ shade$", "az_ghost_noble"),
    (r"^haldarr\ rogue$", "fw_satyr_rogue"),
    (r"^haldarr\ trickster$", "fw_satyr_trickster"),
    (r"^haldarr\ felsworn$", "fw_satyr_felsworn"),
    (r"^mere\ thunderhide$", "az_thunder_lizard"),
    (r"^mere\ mudclaw$", "az_shore_crab"),
    (r"^vrexx\ the\ hornbreaker$", "fw_satyr_hellcaller"),
    (r"^old\ stormhide$", "az_thunder_lizard"),
    (r"^leyline\ prowler$", "az_ley_beast"),
    (r"^legash\ satyr$", "az_satyr_cursed"),
    (r"^legash\ shadowcaster$", "az_satyr_sorcerer"),
    (r"^legash\ felhound$", "az_felhound"),
    (r"^forlorn\ eredar$", "az_eredar_warlock"),
    (r"^forlorn\ doomguard$", "az_doomguard_sentinel"),
    (r"^forlorn\ imp$", "fw_imp"),
    (r"^mennar\ mana\ wyrm$", "az_mana_wyrm_leader"),
    (r"^azure\ whelp$", "az_blue_whelp"),
    (r"^azure\ dragonspawn$", "az_blue_dragonspawn"),
    (r"^eldarath\ shade$", "az_ghost_tormented"),
    (r"^eldarath\ construct$", "az_arcane_construct"),
    (r"^stormbay\ tidehunter$", "az_naga_tidehunter"),
    (r"^stormbay\ siren$", "az_naga_siren"),
    (r"^stormbay\ myrmidon$", "az_naga_brute"),
    (r"^southridge\ shorecrab$", "az_shore_crab"),
    (r"^southridge\ hatchling$", "az_serpent_hatchling"),
    (r"^warlord\ seth'rak$", "fw_satyr_lord"),
    (r"^gatekeeper\ azgaroth$", "az_doomguard_sentinel"),
    (r"^azurewing$", "az_blue_drake"),
    (r"^reef\ shorecrab$", "az_shore_crab"),
    (r"^drowned\ hound$", "az_ghost_hound"),
    (r"^bitter\ reaches\ raider$", "az_naga_tidehunter"),
    (r"^bitter\ reaches\ wavecaller$", "az_naga_sea_witch"),
    (r"^bitter\ reaches\ brute$", "az_naga_brute"),
    (r"^eldara\ arcane\ guardian$", "az_arcane_construct"),
    (r"^eldara\ mana\ wyrm$", "az_mana_wyrm_leader"),
    (r"^promenade\ noble$", "az_ghost_noble"),
    (r"^promenade\ handmaiden$", "az_ghost_handmaiden"),
    (r"^court\ sentinel$", "az_ghost_guard"),
    (r"^court\ tormented$", "az_ghost_tormented"),
    (r"^court\ naga\ guard$", "az_naga_royal_guard"),
    (r"^zin-malor\ priestess$", "az_naga_sea_witch"),
    (r"^zin-malor\ warden$", "az_naga_royal_guard"),
    (r"^zin-malor\ myrmidon$", "az_naga_brute"),
    (r"^reef\ hydra\ hatchling$", "az_serpent_hatchling"),
    (r"^captain\ ssarith$", "az_naga_royal_guard"),
    (r"^magus\ valethion$", "az_ghost_arcanist"),
    (r"^the\ weeping\ duchess$", "az_ghost_handmaiden"),
    (r"^high\ priestess\ naz'eth$", "az_naga_sea_witch"),
    # THE DROWNED PALACE (tools/build_drowned_palace_content.py): exact names, Kyle's Azshara creature sheet and
    # the Vault boss row (sheet 6).
    (r"^zin-azshari\ myrmidon$", "az_naga_brute"),
    (r"^zin-azshari\ royal\ guard$", "az_naga_royal_guard"),
    (r"^zin-azshari\ siren$", "az_naga_siren"),
    (r"^zin-azshari\ tidecaller$", "az_naga_sea_witch"),
    (r"^hydra\ spawn$", "az_serpent_hatchling"),
    (r"^drowned\ highborne$", "az_ghost_noble"),
    (r"^lady\ ssiriss$", "vz_boss_ssiriss"),
    (r"^the\ drowned\ chamberlain$", "vz_boss_chamberlain"),
    (r"^tidelord\ vashj'ren$", "vz_boss_vashjren"),
    (r"^moonguard\ sentinel$", "az_ghost_guard"),
    (r"^highborne\ spellbinder$", "az_ghost_arcanist"),
    (r"^queen's\ handmaiden$", "az_ghost_handmaiden"),
    (r"^tormented\ courtier$", "az_ghost_tormented"),
    (r"^vault\ hound$", "az_ghost_hound"),
    (r"^arcane\ sentry$", "az_arcane_construct"),
    (r"^mana\ wyrm$", "az_mana_wyrm_leader"),
    (r"^ley\ beast$", "az_ley_beast"),
    (r"^the\ moonguard\ revenant$", "vz_boss_revenant"),
    (r"^magistrix\ elaria\ the\ undying$", "vz_boss_elaria"),
    (r"^echo\ of\ the\ queen$", "vz_boss_echo_queen"),
    # THE ROTROOT DEEPS (tools/build_rotroot_deeps_content.py): exact names, Kyle's Azshara creature sheet and his
    # Rotroot boss sheet; the Gloomhollow satyrs borrow Felwood's shadowstalker.
    (r"^rotroot\ furbolg$", "az_rot_furbolg"),
    (r"^rotroot\ mystic$", "az_rot_shaman"),
    (r"^rotroot\ mauler$", "az_rot_beast"),
    (r"^drifting\ sporecloud$", "az_spore_cloud"),
    (r"^satyr\ rot-tender$", "az_rot_tender"),
    (r"^gloomhollow\ satyr$", "fw_satyr_shadowstalker"),
    (r"^rootbound\ horror$", "az_root_horror"),
    (r"^rotroot\ bodyguard$", "fr_elite_guard"),
    (r"^old\ mossjaw$", "fr_boss_mossjaw"),
    (r"^mother\ sporeheart$", "fr_boss_sporeheart"),
    (r"^rotwarden\ kaz'thul$", "fr_boss_kazthul"),
    (r"^thornblight$", "fr_boss_thornblight"),
    (r"^xavras\ the\ gloomtender$", "fr_boss_xavras"),
    # THE PLAGUELANDS' DUNGEONS (tools/build_plaguelands_dungeons_content.py): Scholomance, Stratholme and
    # Hearthglen, exact names, each to its picture: Kyle's dungeon boss sheet (sheet 8) for the bosses, his
    # Plaguelands and Scarlet sheets and the shared undead art for the trash.
    (r"^scholomance\ student$", "pl_cult_neophyte"),
    (r"^scholomance\ neophyte$", "pl_dark_caster"),
    (r"^scholomance\ necrolyte$", "pl_necrolyte"),
    (r"^scholomance\ dark\ summoner$", "pl_cult_lieutenant"),
    (r"^risen\ guard$", "skeleton_warrior_2"),
    (r"^necrofiend$", "pl_crypt_fiend"),
    (r"^reanimated\ corpse$", "zombie_3"),
    (r"^plagued\ hatchling$", "pl_plaguebat"),
    (r"^kirtonos\ the\ herald$", "scholo_boss_gargoyle"),
    (r"^jandice\ barov$", "scholo_boss_ghost_lady"),
    (r"^rattlegore$", "scholo_boss_bone_construct"),
    (r"^marduk\ blackpool$", "pl_death_knight"),
    (r"^vectus$", "scholo_boss_alchemist"),
    (r"^ras\ frostwhisper$", "scholo_boss_frost_lich"),
    (r"^bone\ minion$", "skeleton_warrior_1"),
    (r"^risen\ aberration$", "pl_plague_eruptor"),
    (r"^risen\ construct$", "pl_flesh_golem"),
    (r"^scholomance\ necromancer$", "pl_boss_cult_necromancer"),
    (r"^spectral\ researcher$", "pl_wailing_spirit"),
    (r"^spectral\ tutor$", "scholo_ghost_servant"),
    (r"^unstable\ corpse$", "zombie_4"),
    (r"^instructor\ malicia$", "scholo_boss_instructor"),
    (r"^doctor\ theolen\ krastinov$", "pl_boss_abom_butcher"),
    (r"^lorekeeper\ polkelt$", "scholo_boss_librarian"),
    (r"^the\ ravenian$", "pl_boss_gate_guardian"),
    (r"^lord\ alexei\ barov$", "scholo_boss_noble_lord"),
    (r"^lady\ illucia\ barov$", "scholo_boss_noble_lady"),
    (r"^darkmaster\ gandling$", "scholo_boss_headmaster"),
    (r"^skeletal\ guardian$", "skeleton_warrior_2"),
    (r"^skeletal\ berserker$", "skeleton_warrior_1"),
    (r"^plague\ ghoul$", "pl_frenzied_ghoul"),
    (r"^ghostly\ citizen$", "pl_darrowshire_ghost"),
    (r"^spectral\ citizen$", "spectre_1"),
    (r"^wailing\ banshee$", "banshee"),
    (r"^fleshflayer\ ghoul$", "ghoul_gaunt"),
    (r"^patchwork\ horror$", "abomination_1"),
    (r"^vengeful\ phantom$", "spectre_2"),
    (r"^rockwing\ gargoyle$", "pl_gargoyle"),
    (r"^crimson\ guardsman$", "sc_centurion"),
    (r"^crimson\ conjuror$", "sc_arcanist"),
    (r"^crimson\ initiate$", "sc_tp_cleric"),
    (r"^crimson\ gallant$", "sc_knight"),
    (r"^crimson\ defender$", "sc_tp_crusader"),
    (r"^crimson\ priest$", "sc_chaplain"),
    (r"^crimson\ rifleman$", "sc_tp_sniper"),
    (r"^crimson\ monk$", "sc_monk"),
    (r"^crimson\ battle\ mage$", "sc_adept"),
    (r"^crimson\ sorcerer$", "sc_tp_inquisitor"),
    (r"^crimson\ inquisitor$", "sc_inquisitor"),
    (r"^skul$", "pl_skeletal_mage"),
    (r"^hearthsinger\ forresten$", "pl_silver_hand_ghost"),
    (r"^the\ unforgiven$", "pl_boss_lich_magistrate"),
    (r"^timmy\ the\ cruel$", "strat_boss_ghoul_runt"),
    (r"^cannon\ master\ willey$", "strat_boss_cannon_master"),
    (r"^archivist\ galford$", "strat_boss_archivist"),
    (r"^grand\ crusader\ dathrohan$", "strat_boss_grand_crusader"),
    (r"^ghoul\ ravener$", "ghoul_1"),
    (r"^mangled\ cadaver$", "zombie_5"),
    (r"^broken\ cadaver$", "zombie_6"),
    (r"^plagued\ crypt\ crawler$", "spider_4"),
    (r"^crypt\ beast$", "pl_crypt_fiend"),
    (r"^undead\ scarab$", "spider_hatchling"),
    (r"^thuzadin\ acolyte$", "pl_cult_plaguebringer"),
    (r"^thuzadin\ shadowcaster$", "pl_dark_caster"),
    (r"^thuzadin\ necromancer$", "necromancer"),
    (r"^rockwing\ screecher$", "pl_plaguebat"),
    (r"^eye\ of\ naxxramas$", "pl_boss_eye_construct"),
    (r"^magistrate\ barthilas$", "strat_boss_magistrate"),
    (r"^stonespine$", "scholo_boss_gargoyle"),
    (r"^nerub'enkan$", "strat_boss_crypt_lord"),
    (r"^baroness\ anastari$", "strat_boss_baroness"),
    (r"^maleki\ the\ pallid$", "strat_boss_lich"),
    (r"^venom\ belcher$", "pl_plague_eruptor"),
    (r"^bile\ spewer$", "abomination_2"),
    (r"^bile\ slime$", "pl_plague_slime"),
    (r"^mindless\ undead$", "zombie_1"),
    (r"^black\ guard\ sentry$", "revenant_2"),
    (r"^ramstein\ the\ gorger$", "strat_boss_flesh_golem"),
    (r"^baron\ rivendare$", "strat_boss_baron"),
    (r"^hearthglen\ arbalest$", "sc_tp_sniper"),
    (r"^hearthglen\ cleric$", "sc_tp_cleric"),
    (r"^hearthglen\ field\ medic$", "sc_chaplain"),
    (r"^hearthglen\ mastiff$", "sc_war_hound"),
    (r"^hearthglen\ templar$", "sc_tp_crusader"),
    (r"^hearthglen\ zealot$", "sc_zealot"),
    (r"^high\ protector\ tarsen$", "hg_boss_gatewarden"),
    (r"^huntsman\ radley$", "hg_boss_kennelmaster"),
    (r"^chirurgeon\ maeve\ ostrowski$", "hg_boss_crimson_choir"),
    (r"^high\ clerist\ hendrick$", "hg_boss_high_inquisitor"),
    (r"^high\ protector\ lorik$", "hg_boss_volkov"),
    (r"^mardenholde\ battle\ priest$", "sc_judicator"),
    (r"^mardenholde\ crossbowman$", "sc_tp_sniper"),
    (r"^mardenholde\ halberdier$", "sc_myrmidon"),
    (r"^mardenholde\ knight$", "sc_tp_champion"),
    (r"^scarlet\ commander\ marjhan$", "hg_boss_arcanist"),
    (r"^armsmaster\ grell$", "hg_boss_quartermaster"),
    (r"^drillmaster\ osric\ pell$", "hg_boss_drillmaster"),
    (r"^high\ general\ abbendis$", "hg_boss_lady_marden"),
    (r"^grand\ crusader\ victor\ hale$", "hg_boss_victor_hale"),
    # STONETALON (tools/build_stonetalon_openworld.py): exact names, each to its picture. Kyle's creature sheet
    # (15 Nov 2026), with the existing art where it fits (docs/stonetalon_art_prompts.md sheet 4).
    (r"^ashvent\ steamling$", "st_steam_elemental"),
    (r"^ashvent\ basalt\ brute$", "st_basalt_elemental"),
    (r"^ashvent\ cinderwraith$", "st_ash_elemental"),
    (r"^cinder\ beetle$", "st_bark_beetle"),
    (r"^magmacore$", "st_basalt_elemental"),
    (r"^the\ ash\ mother$", "st_ash_elemental"),
    # the Eldest Sequoia (the dungeon): trunk and crown
    (r"^venture\ co\.\ trunk\ rigger$", "st_venture_rigger"),
    (r"^venture\ co\.\ hauler$", "st_venture_logger"),
    (r"^venture\ co\.\ sap\ tapper$", "st_venture_foreman"),
    (r"^heartrot\ borer$", "st_bark_beetle"),
    (r"^heartrot\ drone$", "st_beetle_mother"),
    (r"^living\ sap$", "st_sap_ooze"),
    (r"^crown\ owl$", "st_canopy_owl"),
    (r"^crown\ sky\ serpent$", "st_sky_serpent"),
    (r"^venture\ co\.\ topper$", "st_venture_rigger"),
    (r"^venture\ co\.\ crown\ shredder$", "st_venture_shredder"),
    (r"^eldest's\ warden$", "st_redwood_ancient"),
    (r"^rigboss\ gazzle$", "st_boss_rigboss_gazzle"),
    (r"^the\ heartrot\ queen$", "st_boss_heartrot_queen"),
    (r"^ambermaw$", "st_boss_ambermaw"),
    (r"^old\ talonwing$", "st_boss_old_talonwing"),
    (r"^topper\ kezzik$", "st_boss_topper_kezzik"),
    (r"^the\ eldest$", "st_boss_the_eldest"),
    (r"^roosevelt\ elk$", "st_bull_elk"),
    (r"^fog\ cougar$", "st_cougar"),
    (r"^greatwood\ bear$", "st_black_bear"),
    (r"^ridge\ eagle$", "st_bald_eagle"),
    (r"^bark\ beetle$", "st_bark_beetle"),
    (r"^mistwood\ owl$", "st_canopy_owl"),
    (r"^redwood\ ancient$", "st_redwood_ancient"),
    (r"^sap\ ooze$", "st_sap_ooze"),
    (r"^vent\ steamling$", "st_steam_elemental"),
    (r"^basalt\ hulk$", "st_basalt_elemental"),
    (r"^crater\ ash\ wraith$", "st_ash_elemental"),
    (r"^peak\ sky\ serpent$", "st_sky_serpent"),
    (r"^venture\ co\.\ rigger$", "st_venture_rigger"),
    (r"^venture\ co\.\ feller$", "st_venture_sawyer"),
    (r"^venture\ co\.\ cut\ foreman$", "st_venture_foreman"),
    (r"^venture\ co\.\ shredder$", "st_venture_shredder"),
    (r"^gnawheart$", "st_beetle_mother"),
    (r"^grandfather\ burl$", "st_redwood_ancient"),
    (r"^skyreach$", "st_sky_serpent"),
    (r"^saw\-boss\ brakka$", "st_venture_shredder"),
    (r"^grimtotem\ firecaller$", "st_grim_shaman"),
    (r"^venture\ co\.\ shaft\ miner$", "st_venture_logger"),
    (r"^venture\ co\.\ powder\ monkey$", "st_venture_demolitionist"),
    (r"^venture\ co\.\ shift\ boss$", "st_venture_foreman"),
    (r"^pumice\ shard$", "st_pumice_golem"),
    (r"^chimney\ harpy$", "st_windshear_harpy"),
    (r"^driller\ mozzik$", "st_venture_shredder"),
    (r"^old\ pumice$", "st_basalt_elemental"),
    (r"^ridge\ cougar$", "st_cougar"),
    (r"^grey\ elk$", "st_bull_elk"),
    (r"^black\ bear$", "st_black_bear"),
    (r"^ash\ vulture$", "vulture_1"),
    (r"^ash\ drifter$", "st_ash_elemental"),
    (r"^venture\ co\.\ salvager$", "st_venture_logger"),
    (r"^venture\ co\.\ bucker$", "st_venture_sawyer"),
    (r"^venture\ co\.\ blaster$", "st_venture_demolitionist"),
    (r"^venture\ co\.\ yard\ foreman$", "st_venture_foreman"),
    (r"^windshear\ harpy$", "st_windshear_harpy"),
    (r"^windshear\ wind\ witch$", "st_windshear_witch"),
    (r"^windshear\ talon$", "harpy_3"),
    (r"^bull\ elk$", "st_bull_elk"),
    (r"^grimtotem\ raider$", "st_grim_warrior"),
    (r"^grimtotem\ mystic$", "st_grim_mystic"),
    (r"^grimtotem\ spearhunter$", "st_grim_hunter"),
    (r"^grimtotem\ brute$", "st_grim_brute"),
    (r"^risen\ tauren$", "st_risen_tauren"),
    (r"^risen\ stalker$", "st_risen_stalker"),
    (r"^rim\ carrion\ bird$", "vulture_3"),
    (r"^old\ greyhide$", "st_bull_elk"),
    (r"^yard\ boss\ krizzle$", "st_venture_foreman"),
    (r"^matron\ shrieka$", "harpy_matriarch"),
    (r"^broadpaw$", "st_black_bear"),
    (r"^hargol\ bloodhorn$", "st_grim_elder"),
    (r"^the\ risen\ hunter$", "st_risen_tauren"),
    # THE PLAGUELANDS (tools/build_wpl_openworld.py): exact names, each to its picture. Kyle's Plaguelands sheets
    # (16 Nov 2026) give the Scourge, the Cult, the plagued wild and the Scarlets their own art; what the sheets
    # don't draw (plain skeletons, ghouls, snapjaws, drowned) keeps the older undead and beast sprites.
    (r"^plague\-ridden\ wolf$", "pl_plagued_wolf"),
    (r"^diseased\ black\ bear$", "pl_diseased_bear"),
    (r"^plaguewing\ vulture$", "pl_carrion_vulture"),
    (r"^wandering\ skeleton$", "skeleton_warrior_2"),
    (r"^felstone\ cultist$", "pl_cult_neophyte"),
    (r"^felstone\ ghoul$", "ghoul_1"),
    (r"^felstone\ cauldron\ lord$", "pl_plague_eruptor"),
    (r"^dalson's\ ghoul$", "ghoul_2"),
    (r"^dalson's\ skeleton$", "skeleton_warrior_1"),
    (r"^cauldron\ necrolyte$", "pl_necrolyte"),
    (r"^haunt\ banshee$", "banshee"),
    (r"^writhing\ crypt\ fiend$", "pl_crypt_fiend"),
    (r"^haunt\ cult\ tender$", "pl_cauldron_tender"),
    (r"^andorhal\ skeleton$", "skeleton_warrior_2"),
    (r"^andorhal\ abomination$", "abomination_2"),
    (r"^andorhal\ necromancer$", "pl_dark_caster"),
    (r"^andorhal\ skeletal\ archer$", "skeleton_archer"),
    (r"^scarlet\ outrider$", "sc_cavalier"),
    (r"^scarlet\ field\ chaplain$", "sc_chaplain"),
    (r"^drowned\ lakewalker$", "zombie_4"),
    (r"^darrowmere\ snapjaw$", "turtle_snapping"),
    (r"^caer\ darrow\ shade$", "wraith_pale"),
    (r"^caer\ darrow\ ghoul$", "ghoul_gaunt"),
    (r"^farmer\ felstone$", "pl_boss_abomination_farmer"),
    (r"^the\ dalson\ ghost$", "pl_darrowshire_ghost"),
    (r"^mother\ of\ the\ haunt$", "banshee"),
    (r"^magistrate\ andor$", "pl_boss_lich_magistrate"),
    (r"^old\ darrowjaw$", "turtle_snapping"),
    (r"^the\ groundskeeper$", "abomination_1"),
    (r"^rotting\ worg$", "worg_6"),
    (r"^blighted\ stag$", "pl_blighted_stag"),
    (r"^plague\ bat$", "pl_plaguebat"),
    (r"^skeletal\ wanderer$", "skeleton_warrior_1"),
    (r"^scarlet\ lumberjack$", "sc_tp_crusader"),
    (r"^scarlet\ sawyer$", "sc_zealot"),
    (r"^scarlet\ woodsman\ archer$", "sc_tp_sniper"),
    (r"^withering\ ghoul$", "ghoul_gaunt"),
    (r"^withering\ cultist$", "pl_cult_neophyte"),
    (r"^cauldron\ sludge$", "pl_plague_slime"),
    (r"^scarlet\ sentry$", "sc_knight"),
    (r"^hearthglen\ inquisitor$", "sc_inquisitor"),
    (r"^scarlet\ crossbowman$", "sc_tp_sniper"),
    (r"^scarlet\ war\ hound$", "sc_war_hound"),
    (r"^thondroril\ snapjaw$", "turtle_snapping"),
    (r"^riverbank\ ghoul$", "zombie_5"),
    (r"^foreman\ harrow$", "sc_tp_drill_sergeant"),
    (r"^gahrron\ the\ withered$", "abomination_2"),
    (r"^high\ inquisitor\ faulk$", "sc_tp_inquisitor"),
    (r"^old\ thondroril$", "turtle_snapping"),
    (r"^plague\ hound$", "pl_plaguehound"),
    (r"^carrion\ grub$", "pl_carrion_grub"),
    (r"^frenzied\ ghoul$", "pl_frenzied_ghoul"),
    (r"^stone\-winged\ gargoyle$", "pl_gargoyle"),
    (r"^terrordale\ spirit$", "pl_wailing_spirit"),
    (r"^terrordale\ skeletal\ mage$", "pl_skeletal_mage"),
    (r"^terrordale\ ghoul$", "ghoul_1"),
    (r"^marris\ farmhand$", "zombie_2"),
    (r"^stead\ crow$", "pl_carrion_vulture"),
    (r"^plaguewood\ spider$", "pl_plaguewood_spider"),
    (r"^plaguewood\ crypt\ fiend$", "pl_crypt_fiend"),
    (r"^gate\ death\ knight$", "pl_death_knight"),
    (r"^gate\ gargoyle$", "pl_gargoyle"),
    (r"^vale\ plague\ slime$", "pl_plague_slime"),
    (r"^spore\-walker$", "zombie_6"),
    (r"^cult\ plaguebringer$", "pl_cult_plaguebringer"),
    (r"^cult\ cart\ driver$", "pl_dark_caster"),
    (r"^crossing\ abomination$", "pl_flesh_golem"),
    (r"^the\ terror\ of\ the\ dale$", "pl_rare_plague_rider"),
    (r"^old\ marris$", "scarecrow_golem"),
    (r"^the\ plaguewood\ matriarch$", "pl_boss_brood_queen"),
    (r"^gatekeeper\ vorthas$", "pl_death_knight"),
    (r"^the\ fungal\ mass$", "ooze_acid_2"),
    (r"^cartmaster\ corin$", "pl_cult_lieutenant"),
    (r"^blighted\ warhorse$", "pl_skeletal_warhorse"),
    (r"^plague\-rotted\ bear$", "pl_diseased_bear"),
    (r"^carrion\ bat$", "pl_plaguebat"),
    (r"^darrowshire\ spirit$", "pl_darrowshire_ghost"),
    (r"^darrowshire\ ghoul$", "ghoul_gaunt"),
    (r"^blackwood\ drowned$", "zombie_3"),
    (r"^blackwood\ snapjaw$", "turtle_snapping"),
    (r"^tyr's\ hand\ crusader$", "sc_centurion"),
    (r"^tyr's\ hand\ abbot$", "sc_chaplain"),
    (r"^tyr's\ hand\ marksman$", "sc_tp_sniper"),
    (r"^tyr's\ hand\ houndmaster$", "houndmaster"),
    (r"^restless\ lodge\ ranger$", "wraith_2"),
    (r"^mossflayer\ warrior$", "zm_troll_warrior"),
    (r"^mossflayer\ shadowhunter$", "troll_witchdoctor"),
    (r"^mossflayer\ scout$", "troll_axe_2"),
    (r"^scar\ bone\ construct$", "skeleton_warrior_2"),
    (r"^captain\ redpath's\ shade$", "wraith_pale"),
    (r"^the\ blackwood\ drowner$", "zombie_4"),
    (r"^abbot\ varenne$", "sc_tp_cleric"),
    # THE PLAGUELANDS' CAVES (tools/build_plaguelands_caves_content.py): exact names, existing art.
    (r"^writhing\ burrower$", "crypt_fiend_1"),
    (r"^deep\ webspinner$", "spider_3"),
    (r"^haunt\ larva$", "pl_carrion_grub"),
    (r"^brood\ guardian$", "crypt_fiend_2"),
    (r"^broodlord\ szarak$", "crypt_fiend_2"),
    (r"^the\ silken\ bride$", "spider_broodmother_1"),
    (r"^seepwater\ shade$", "spectre_1"),
    (r"^cave\ drowned$", "drowned_sailor_3"),
    (r"^blind\ cave\ bat$", "bat"),
    (r"^seep\ ooze$", "ooze_acid_1"),
    (r"^the\ weeper$", "banshee"),
    (r"^the\ drowned\ hermit$", "drowned_sailor_1"),
    (r"^crypt\ shambler$", "zombie_2"),
    (r"^marris\ ossuary\ guard$", "skeleton_warrior_1"),
    (r"^crypt\ rat\ swarm$", "rat_plague_1"),
    (r"^grave\ wight$", "revenant_1"),
    (r"^sexton\ hollowell$", "revenant_2"),
    (r"^the\ bone\ choir$", "spectre_2"),
    (r"^bone\ miner$", "ghoul_2"),
    (r"^scourge\ pit\ guard$", "skeleton_warrior_2"),
    (r"^marrow\ construct$", "abomination_1"),
    (r"^bone\ dust\ swarm$", "maggot"),
    (r"^overseer\ marrowgrim$", "abomination_2"),
    (r"^the\ ossifier$", "pl_rare_arch_necromancer"),
    # THE SCARLET MONASTERY (tools/build_scarlet_monastery_content.py): exact names, each to its picture,
    # until Kyle's Scarlet sheets come in.
    (r"^scarlet\ torturer$", "executioner_hooded"),
    (r"^scarlet\ scryer$", "sc_inquisitor"),
    (r"^haunting\ phantasm$", "spectre_1"),
    (r"^anguished\ dead$", "zombie_2"),
    (r"^unfettered\ spirit$", "spectre_2"),
    (r"^interrogator\ maelis$", "sm_boss_interrogator"),
    (r"^azshir\ the\ sleepless$", "wraith_pale"),
    (r"^the\ fallen\ champion$", "revenant_1"),
    (r"^bloodmage\ thalnos$", "sm_boss_bloodmage"),
    (r"^scarlet\ adept$", "sc_adept"),
    (r"^scarlet\ gallant$", "sc_knight"),
    (r"^scarlet\ beastmaster$", "sc_tp_crusader"),
    (r"^scarlet\ tracking\ hound$", "sc_war_hound"),
    (r"^scarlet\ monk$", "sc_monk"),
    (r"^houndmaster\ loksey$", "sm_boss_houndmaster"),
    (r"^archivist\ dana\ mercer$", "sc_tp_cleric"),
    (r"^arcanist\ doan$", "sm_boss_arcanist"),
    (r"^scarlet\ trainee$", "human_militia"),
    (r"^scarlet\ soldier$", "sc_zealot"),
    (r"^scarlet\ myrmidon$", "sc_myrmidon"),
    (r"^scarlet\ defender$", "sc_judicator"),
    (r"^scarlet\ evoker$", "sc_arcanist"),
    (r"^sergeant\ major\ cole\ brennan$", "sc_tp_drill_sergeant"),
    (r"^quartermaster\ bram\ ellison$", "sc_knight"),
    (r"^herod$", "sm_boss_champion"),
    (r"^scarlet\ centurion$", "sc_centurion"),
    (r"^scarlet\ sorcerer$", "sc_arcanist"),
    (r"^scarlet\ champion$", "sc_tp_champion"),
    (r"^scarlet\ wizard$", "sc_arcanist"),
    (r"^scarlet\ abbot$", "sc_chaplain"),
    (r"^high\ inquisitor\ aldric$", "revenant_2"),
    (r"^ironspine$", "skeleton_warrior_2"),
    (r"^inquisitor\ vellan\ rook$", "sc_tp_inquisitor"),
    (r"^curator\ halbrecht$", "cult_overseer"),
    (r"^smithmaster\ corra\ bellweather$", "human_militia"),
    (r"^master\-at\-arms\ dorran\ pike$", "sc_myrmidon"),
    (r"^brother\ garrick\ thorne$", "sc_tp_sniper"),
    (r"^captain\ elric\ stane$", "sc_centurion"),
    (r"^brother\ corwin\ ashe$", "sc_tp_cleric"),
    (r"^high\ inquisitor\ whitemane$", "sm_boss_high_inquisitor"),
    (r"^scarlet\ commander\ mograine$", "sm_boss_commander"),
    (r"^ranger\-lord\ saelith$", "wraith_1"),
    (r"^zul'mashar\ the\ last$", "zm_troll_warrior"),
    (r"^the\ bone\ colossus$", "pl_boss_bone_colossus"),
    # FELWOOD (tools/build_felwood_openworld.py): exact names, each to its picture. The South's
    # wildlife uses the existing beast art; the Fel Line's demons and everything in the North use
    # Kyle's Felwood sheet.
    (r"^greywood\ nightsaber$", "panther_1"),
    (r"^old\-growth\ grizzly$", "bear_2"),
    (r"^timberline\ wolf$", "worg_3"),
    (r"^silverhorn\ stag$", "stag"),
    (r"^iris\ snapjaw$", "turtle_snapping"),
    (r"^lakeshore\ crocolisk$", "crocolisk_2"),
    (r"^hollowbark\ treant$", "treant_1"),
    (r"^restless\ wisp$", "wisp_1"),
    (r"^thornpaw\ saber$", "saber_cat"),
    (r"^ruin\ prowler$", "panther_3"),
    (r"^moonlit\ wisp$", "wisp_2"),
    (r"^ivybound\ treant$", "treant_2"),
    (r"^moss\-tusk\ boar$", "boar_3"),
    (r"^blighted\ wolf$", "fw_blighted_wolf"),
    (r"^felwood\ imp$", "fw_imp"),
    (r"^border\ felhound$", "fw_felhound"),
    (r"^felguard\ sentry$", "fw_felguard"),
    (r"^old\ mossback$", "turtle_snapping"),
    (r"^grandfather\ hollowbark$", "treant_2"),
    (r"^saberfang\ the\ elder$", "saber_cat"),
    (r"^ursa\ mossjaw$", "bear_5"),
    (r"^hask'zar\ the\ scarred$", "fw_doomguard"),
    (r"^fel\-rotted\ bear$", "fw_fel_bear"),
    (r"^jadefire\ stag$", "fw_jadefire_stag"),
    (r"^warpwood\ treant$", "fw_warpwood_treant"),
    (r"^jadefire\ rogue$", "fw_satyr_rogue"),
    (r"^jadefire\ trickster$", "fw_satyr_trickster"),
    (r"^jadefire\ shadowstalker$", "fw_satyr_shadowstalker"),
    (r"^jadefire\ felsworn$", "fw_satyr_felsworn"),
    (r"^jadefire\ hellcaller$", "fw_satyr_hellcaller"),
    (r"^seepage\ ooze$", "fw_toxic_ooze"),
    (r"^deadwood\ warrior$", "fw_deadwood_warrior"),
    (r"^deadwood\ den\ watcher$", "fw_deadwood_watcher"),
    (r"^deadwood\ pathfinder$", "fw_deadwood_pathfinder"),
    (r"^deadwood\ shaman$", "fw_deadwood_shaman"),
    (r"^deadwood\ gardener$", "fw_deadwood_gardener"),
    (r"^vor'alith\ the\ turncloak$", "fw_satyr_felsworn"),
    # North Felwood
    (r"^plaguefang\ wolf$", "fw_blighted_wolf"),
    (r"^jadefire\ imp$", "fw_imp"),
    (r"^crater\ imp$", "fw_imp"),
    (r"^felbrand\ infernal$", "fw_infernal"),
    (r"^felbrand\ felguard$", "fw_felguard"),
    (r"^felbrand\ hellhound$", "fw_felhound"),
    (r"^shadow\ council\ acolyte$", "fw_council_acolyte"),
    (r"^shadow\ council\ warlock$", "fw_council_warlock"),
    (r"^jaedenar\ hound\ handler$", "fw_hound_handler"),
    (r"^the\ bloodvenom\ rot$", "fw_toxic_ooze"),
    (r"^pyrrhax\ the\ fallen\ star$", "fw_infernal"),
    (r"^ironbark\ the\ blighted$", "fw_warpwood_treant"),
    # Jaedenar (tools/handbuilt_jaedenar.py)
    (r"^shadow\ council\ high\ warlock$", "fw_council_high_warlock"),
    (r"^shadow\ council\ summoner$", "fw_council_summoner"),
    (r"^bound\ voidwalker$", "fw_bound_voidwalker"),
    (r"^jaedenar\ felguard$", "fw_felguard"),
    (r"^jaedenar\ felhound$", "fw_felhound"),
    (r"^jaedenar\ imp$", "fw_imp"),
    (r"^jaedenar\ doomguard$", "fw_doomguard"),
    (r"^jaedenar\ infernal$", "fw_infernal"),
    (r"^hold\-warden\ gorvash$", "fw_boss_hold_warden"),
    (r"^inquisitor\ xel'thas$", "fw_council_high_warlock"),
    (r"^the\ duskwhisper\ sisters$", "fw_boss_twin_warlocks"),
    (r"^zeth'rak\ the\ pactbound$", "fw_eredar_warlock"),
    (r"^master\ summoner\ kaz'reth$", "fw_boss_master_summoner"),
    (r"^the\ entropic\ horror$", "fw_entropic_horror"),
    (r"^doomlord\ kazrak$", "fw_boss_doom_lord"),
    (r"^grimbark\ the\ chained$", "fw_boss_corrupted_ancient"),
    (r"^zar'gothrax\ the\ unbound$", "fw_boss_demon_lord"),
    (r"^chieftain\ grimpelt$", "fw_deadwood_alpha"),
    (r"^prince\ aelvorn\ the\ unmade$", "fw_satyr_lord"),
    # TEMPEST ISLE, the open world (tools/build_tempest_openworld.py). Named rares and the Dark
    # Iron squatters carry no word a weaker rule could read: "Mother Canopy" is a panther,
    # "Sootwing" a drake and "The Barge-Eater" a crab, and none of them says so.
    (r"^mother canopy$", "panther"),
    (r"^borrik the unhoused$", "dark_iron_warlord"),
    (r"^sootwing$", "dragon_whelp"),
    (r"^the barge-eater$", "crab_giant"),
    (r"^wreck-captain vess'ira$", "naga_warrior"),
    (r"^old scoria$", "elemental_fire"),
    (r"gate-squatter ashpreacher", "dark_iron_slagcaller"),
    (r"gate-squatter", "dark_iron_digger"),
    # TEMPEST ISLE, the two dungeons (14 Nov 2026). Khaz Varun is a Dark Iron city and nearly every
    # name in it fell to a generic rule: its gatewarden, its thane and its berserkers drew as human
    # bandits, a goblin sapper as a ranger, the geyser spirit as a zombie and the rock borers as
    # plague rats. The Dark Iron and goblin art has existed since the Black Strand.
    (r"^gatewarden hrun$", "warden_armoured"),
    (r"^thane morrun the unmade$", "champion_plate"),
    (r"^forge-lord darrok$|^molten thane$", "dark_iron_warlord"),
    (r"^smelter-master vaud$", "dwarf_excavator"),
    (r"^flamespeaker maud$", "dark_iron_slagcaller"),
    (r"^the iron mask$", "executioner_hooded"),
    (r"^powderkeg nix$", "goblin_sapper"),
    (r"^chained berserker$|^ashclaim trespasser$", "dark_iron_cutthroat"),
    (r"^crazed miner$", "dark_iron_digger"),
    (r"^clockwork sentry$|^steam automaton$", "scarecrow_golem"),
    (r"shadow of the forge", "voidwalker"),
    (r"^the ashwretch brood$", "ghoul_gaunt"),
    (r"^the rock-borer queen$", "matriarch_brood"),
    (r"^rock borer$", "maggot"),
    (r"cinder ?hound", "felhound"),
    (r"geyser spirit", "elemental_water"),
    (r"^fire sprite$|^ember swarm$", "wisp"),
    (r"^smoke drake$|^calderaborn drake$", "dragon_whelp_bronze"),
    (r"^karrath the ventlord$", "elemental_fire"),
    (r"^the mountain's heart$", "elemental_earth"),
    # THE ROYAL HIVE (14 Nov 2026), under the Black Strand. Silithid art: the workers for drones,
    # guards and weavers, the shelled crawler for the tunnellers, the grub for larvae, the wasp
    # for the flyers, and the brood mother for the two who rule the hive.
    (r"^hive-mother ahn'thera$|^the brood nurse$", "matriarch_brood"),
    (r"^royal consort zhir'ak$|^hive-warden kasz'ar$|^resin-mother vex'ith$", "silithid_worker"),
    (r"^tunnel-king ruzzak$|^hive tunneler$", "crawler_shell"),
    (r"^brood larva$", "maggot"),
    (r"^venomwing wasp$", "wasp"),
    (r"^royal hive (drone|guard)$|^resin weaver$", "silithid_worker"),
    # THE CASTOUTS (The Black Strand). Dark Iron dwarves put out of Onyxhollow's gate. First in
    # the list because every word in their names belongs to a weaker rule below: a "Digger" is a
    # human bandit, a "Slagcaller" a robed cultist and a "Foreman" an overseer.
    # One picture each and no variants: three creatures cannot reach four hashed looks, and a
    # sprite nothing can select is art nobody sees (tools/qa_creature_sprites.py).
    (r"castout slagcaller", "dark_iron_slagcaller"),
    (r"castout cutthroat", "dark_iron_cutthroat"),
    (r"foreman durn", "dark_iron_warlord"),
    (r"\bcastout\b", "dark_iron_digger"),
    # ===== WHAT IT IS BEATS WHAT IT IS CALLED (12 Nov 2026) =====
    # Kyle, 10 Nov: "Boulder'gor boss should be an ogre" - and the Boulderfist Hall boss too.
    # Both drew as HUMAN bandits. The race rules further down match on the race WORD ("ogre",
    # "kobold", "troll"), and a named boss does not carry it: "Gor'mok the Pit Chief" says
    # nothing about being an ogre, so he fell through to his stat template, humanoid_warrior,
    # which draws a human. tools/qa_creature_sprites.py found 21 named bosses standing in a
    # roster of another race and drawn as a human, and seven whole tribes (Drywhisker kobolds
    # drawn as rats and bandits, Witherbark and Sandfury trolls as bandits and cultists) whose
    # TRIBE name the rules did not know.
    #
    # Named individuals first, by name, then tribes. First match wins, so these sit at the top.
    (r"^(gor'mok the pit chief|mauler krakk|gorbuk the shelf-king|gorbash the thick)$", "ogre"),
    (r"^(warlord krellian|bloodhoof the lamed|verog the dervish|kragg the wall-breaker|"
     r"warbringer gorrak|khan saltmane)$", "centaur"),
    (r"^(wardchief thulg|hagg taurenbane)$", "quilboar"),
    (r"^bramblequeen durga$", "quilboar_geomancer"),
    (r"^skyshriek matron$", "harpy_matriarch"),
    (r"^ka'tesh the last stairkeeper$", "troll_witchdoctor"),
    (r"^(isle headhunter|thaka the unburied)$", "troll_axe"),
    (r"^harbinger veska$", "troll_witchdoctor"),
    (r"^chief grik$", "gnoll"),
    (r"^ssaren the salvage-taker$", "naga_warrior"),
    (r"^gearjaw$", "goblin_overseer"),
    # Tribes. A caster of the tribe gets the tribe's caster where one is drawn.
    (r"drywhisker", "kobold"),
    (r"(witherbark|sandfury|bloodscalp|skullsplitter|vilebranch).*(shadowcaster|venomweaver|"
     r"witch ?doctor|hex\w*|shaman|mystic|shadow ?hunter|priest)", "troll_witchdoctor"),
    (r"witherbark|sandfury|bloodscalp|skullsplitter|vilebranch", "troll_axe"),
    (r"death's head", "quilboar_geomancer"),
    (r"mudsnout|mosshide (?!the)|riverpaw|shadowhide|rothide", "gnoll"),
    (r"saltscale (salvager|reaver)", "murloc"),
    (r"witchwing", "harpy"),
    (r"siren", "sea_witch"),
    # ===== added with sheets 6 and 7 =====
    (r"scarlet.*(crusader|knight|defender|myrmidon|champion|commander|centurion)", "scarlet_crusader"),
    (r"scarlet.*(priest|preacher|chaplain|confessor|zealot|evangel)", "scarlet_priest"),
    (r"scarlet.*(archer|marksman|hunter|tracker|bowman)", "scarlet_archer"),
    (r"scarlet", "scarlet_crusader"),
    (r"twilight", "twilight_cultist"),
    (r"magister|blood ?elf|sunfury|quel'", "bloodelf_magister"),
    (r"sentinel.*(scout|picket|archer|huntress|watcher)|night ?elf|\bkaldorei\b", "nightelf_sentinel"),
    (r"houndmaster|beastmaster|kennel", "houndmaster"),
    (r"\btauren\b|longhorn|grimtotem", "tauren_brave"),
    (r"(murloc|fish).*(oracle|seer|priest|tidecaller)|oracle", "murloc_oracle", {"aquatic", "humanoid"}),
    (r"militia|farmhand|peasant|conscript|footman|watchman|hillsbrad", "human_militia", {"humanoid"}),
    (r"marine|kul ?tiras|sailor|deckhand|boatswain|stranded", "human_marine", {"humanoid"}),
    (r"\byeti\b|wendigo", "yeti"),
    (r"scarecrow|harvest ?golem|harvest ?watcher|strawman", "scarecrow_golem"),
    # GUARDED: "whelp" is a baby dragon to a Razorjaw and a job description to a
    # Felstalker Whelp, which is a demon hound. This rule sits ~50 lines above the demon
    # block, so ungated it won the match and drew a fel hound as a bronze dragonling
    # (Kyle, 2026-10-31: "felpup and felstalker shoulder not be whatever this is").
    (r"whelp|dragonkin|drake|wyrmling", "dragon_whelp", {"beast", "dragon"}),
    (r"sprite ?darter|\bdarter\b|faerie dragon", "sprite_darter"),
    # --- named species that would otherwise be caught by a weaker rule
    (r"broodmother|brood tender|brood queen", "spider_broodmother"),
    (r"hatchling|spiderling", "spider_hatchling"),
    (r"spider|weaver|webspinner|arachn", "spider", {"insect"}),
    (r"silithid.*warrior|hive.*warrior", "silithid_worker"),
    (r"silithid|hive", "silithid_worker"),
    (r"scarab|beetle", "silithid_worker"),
    (r"wasp.*queen|queen.*wasp", "wasp"),
    (r"wasp|hornet|stinger", "wasp"),
    (r"centipede", "maggot"),
    (r"maggot|grub", "maggot"),
    (r"\brats?\b|vermin", "rat_plague"),
    (r"ooze|acid", "ooze_acid", {"insect", "aquatic", "elemental"}),
    (r"slime|sludge|muck", "slime_green", {"insect", "aquatic", "elemental", "beast"}),
    (r"carapace|shardback|crawler", "crawler_shell"),

    # --- aquatic
    (r"(naga|saltscale).*(myrmidon|warrior|guard)", "naga_myrmidon"),
    (r"(naga|saltscale).*(siren|witch|sorcer)|sea witch", "sea_witch"),
    (r"\bnaga\b|saltscale", "naga_warrior"),
    (r"drowned.*(captain|bosun|officer)", "pirate_captain"),
    (r"drowned|waterlogged|sodden", "drowned_sailor"),
    (r"murloc|makrura", "murloc"),
    (r"tidecaller|tide|lurker", "tide_lurker"),
    (r"\beels?\b", "eel_electric"),
    (r"jellyfish", "tentacle_horror"),
    (r"thresher", "thresher"),
    (r"crab", "crab_giant"),
    (r"turtle|snapper", "turtle_snapping"),
    (r"coral", "golem_stone"),
    (r"reef|siltfin|brinescale|brine", "reefcrawler"),
    (r"tentacl|horror", "tentacle_horror"),

    # --- undead
    (r"abomination|stitch", "abomination"),
    (r"skeleton.*(archer|bowman)|bone.*archer", "skeleton_archer"),
    (r"skeleton.*(mage|caster)|bone.*mage", "skeleton_archer"),
    (r"\b(archer|bowman|marksman)\b", "skeleton_archer", {"undead"}),
    (r"skeleton|bonewarden|bone ", "skeleton_warrior"),
    (r"ghoul", "ghoul"),
    (r"zombie|shambler|risen", "zombie"),
    (r"banshee", "banshee"),
    (r"wraith|spectre|specter|shade", "wraith"),
    (r"\bghost\b|apparition|phantom", "spectre"),
    (r"necromancer|animator", "necromancer"),
    (r"lich", "necromancer"),
    (r"gargoyle", "crypt_fiend"),
    (r"crypt", "crypt_fiend"),
    (r"mummy|bound dead", "zombie"),
    (r"revenant", "revenant"),

    # --- demons
    # A "familiar" is an imp in every context this game has one - Vile Familiar was
    # matching no demon rule at all and falling through to demon_caster -> fel_cultist,
    # i.e. drawing a summoned imp as a robed human. Gated to demons so a future
    # witch's cat familiar does not become an imp.
    (r"\bimps?\b", "imp"),
    (r"\bfamiliar\b", "imp", {"demon"}),
    # fel pup / fel whelp: the young of a felhound are a felhound, not a demon_brute.
    (r"felhound|felstalker|fel ?(pup|whelp)|hound of|doomhound", "felhound"),
    (r"voidwalker|void ", "voidwalker"),
    (r"succubus", "fel_cultist"),
    (r"doomguard", "doomguard"),
    (r"infernal", "demon_brute"),
    (r"satyr", "satyr"),
    (r"felsworn|fel |demon", "demon_brute"),

    # --- elementals, plants, constructs
    (r"(fire|flame|ember|magma|molten|lava|cinder|searing|smolder).*(elemental|spirit|guardian|caller|lord)",
     "elemental_fire", {"elemental"}),
    (r"(water|tide|wave|naiad).*(elemental|spirit|lord)", "elemental_water"),
    (r"(earth|stone|rock|granite|crag).*(elemental|spirit|lord)", "elemental_earth"),
    (r"(air|wind|storm|gale|thunder).*(elemental|spirit|lord|caller)", "elemental_air", {"elemental"}),
    (r"(ice|frost|rime|winter).*(elemental|spirit|lord)", "elemental_water"),
    # NOT |wisp in the second group: it used to be, so "Vein-Lit Wisp" drew the arcane ELEMENTAL
    # - a humanoid of folded energy - while the actual wisp sprite, a floating mote with a face,
    # sat unused two rules below. A wisp is a wisp whatever lit it.
    (r"(arcane|mana|spell|vein-lit|veinlit).*(elemental|spirit)", "elemental_arcane"),
    (r"(shadow|void|dark|umbral).*(elemental|spirit|lord)", "elemental_arcane"),
    (r"\bmote\b", "wisp"),
    (r"lattice", "lattice_grown"),
    (r"crystal.*(sentinel|guardian|warden)|amber sentinel", "crystal_sentinel"),
    (r"crystal|shardling|geode|glitter", "crystal_shardling"),
    # Animated Spellblade is the one creature that is arcane-animated rather than rock: gated to
    # the elemental family so Syndicate Spellbinder, a person, is not caught by "spell".
    (r"spellblade|animated|\barcane\b|\bley\b", "elemental_arcane", {"elemental"}),
    (r"dryad", "sapling_thorn"),          # a species, above the "sentinel" title
    (r"chitter", "silithid_worker"),      # Chitterlord Skrix is an insect, not a cultist
    (r"construct|golem|sentinel", "golem_stone", {"elemental", "undead", "demon"}),
    (r"\bwisp\b", "wisp"),
    (r"treant|ancient|bark|timber", "treant", {"plant"}),
    (r"sapling|sprout", "sapling_thorn"),
    (r"spore|gloomcap|fungal|mushroom|myconid", "spore_cap"),
    (r"vine|strangler|thorn|creeper|lasher", "vine_strangler", {"plant"}),
    (r"\bore\b|\bgeode\b", "elemental_earth", {"plant", "elemental"}),
    (r"bog|peat|marsh|mire", "bog_lord", {"plant", "elemental", "beast"}),

    # --- beasts
    # "worgen" is a wolf-headed PERSON and all 8 in the game classify as humanoid; the plain
    # worg rule was drawing them as a quadruped wolf. The gnoll sprite is the beast-headed
    # humanoid on the sheet, so it is the honest stand-in until worgen earn their own cell.
    (r"worgen|gilnean|shadowfang", "worgen"),
    (r"\bworgs?\b|wolf|lupine|howler", "worg"),
    (r"raptor|velocir", "raptor"),
    (r"\bbats?\b|nightwing", "bat"),
    (r"\bbears?\b|ursa", "bear", {"beast"}),
    (r"boar|battleboar|tusker", "boar", {"beast"}),
    (r"hyena|jackal", "hyena"),
    (r"panther|stalker|prowler", "panther", {"beast"}),
    (r"saber|sabre|\bcat\b|lynx", "saber_cat"),
    (r"basilisk", "basilisk"),
    (r"serpent|snake|cobra|adder|viper", "serpent", {"beast"}),
    (r"crocolisk|crocodile|gator", "crocolisk"),
    (r"kodo", "kodo"),
    (r"scorpion|scorpid", "scorpion"),
    (r"\bram\b|goat", "ram"),
    (r"stag|deer|elk", "stag"),
    (r"owlbeast|owlkin", "bear"),
    (r"gorilla|ape", "gorilla"),
    (r"tiger", "saber_cat"),
    (r"vulture|buzzard|carrion bird", "vulture"),
    (r"toad|frog|hopper", "toad_giant"),
    (r"lizard|strider|monitor", "lizard_rock"),
    (r"plainstrider|strider", "vulture"),

    # --- humanoids (broadest, so last)
    (r"gnoll.*(shaman|mystic|caster)", "gnoll"),
    (r"gnoll", "gnoll"),
    (r"kobold.*(taskmaster|foreman|overseer)", "kobold"),
    (r"kobold", "kobold"),
    (r"harpy.*(matriarch|queen)", "harpy_matriarch"),
    (r"harpy|windcaller", "harpy"),
    (r"(quilboar|razorfen|razormane|bristleback).*(geomancer|shaman|mystic|warcaller)",
     "quilboar_geomancer"),
    (r"quilboar|razorfen|razormane|bristleback", "quilboar"),
    (r"centaur|kolkar|galak", "centaur"),
    (r"ogre.*(mage|magus)", "ogre"),
    (r"ogre|mosh'ogg|gordunni|boulderfist", "ogre"),
    (r"troll.*(witch|hex|shadow|priest)", "troll_witchdoctor"),
    (r"troll|zul'|vilebranch|zalazane|gurbashi|bloodscalp|skullsplitter", "troll_axe"),
    (r"trogg", "trogg"),
    (r"furbolg", "furbolg"),
    (r"(bloodsail|southsea|pirate).*(captain|lord)", "pirate_captain"),
    (r"bosun|swabbie|deckhand|gaffer", "pirate_bosun"),
    (r"bloodsail|southsea|pirate|buccaneer|corsair|cutthroat|wrecker", "pirate_cutthroat"),
    (r"syndicate|thug|bandit|brigand|highwayman", "syndicate_rogue"),
    (r"cultist.*(overseer|master|high)", "cult_overseer"),
    (r"acolyte|initiate|novice", "cultist_acolyte"),
    (r"cultist|zealot|twilight", "cultist_robed"),
    (r"apothecary|chemist|plaguebringer", "forsaken_apothecary"),
    (r"forsaken|deathguard", "forsaken_soldier"),
    (r"(venture|goblin).*(overseer|foreman|boss)", "goblin_overseer"),
    (r"goblin|venture|sapper|tinker|dustwheel|boilerman|wheelman", "goblin_sapper"),
    (r"dwarf|excavator|prospector|dark iron|dun garok|rifleman|mountaineer", "dwarf_excavator"),
    (r"deserter|grunt|orc\b", "orc_deserter"),

    # --- TITLES, last of all and above only the stat template.
    # 122 of the creatures reaching this point are BOSSES WITH PERSONAL NAMES - "Archmage Arugal",
    # "Baron Silverlaine", "Aku'mai" - which carry no species at all. Their stat template is the
    # only thing left, and a template is how every boss ended up looking like one of eight things
    # in the first place. A title is weak evidence but it is real evidence: an Archmage is robed
    # and a Captain is armoured, and matching that beats drawing both as the same hooded figure.
    (r"\b(archmage|magus|sorcer\w*|conjur\w*|arcanist|spellbinder)\b", "archmage_robed", {"humanoid"}),
    (r"\b(baron|baroness|lord|lady|duke|count|prince)\b", "noble_armoured", {"humanoid"}),
    (r"\b(captain|admiral|commodore|skipper)\b", "pirate_captain", {"humanoid"}),
    (r"\b(warden|keeper|guardian|sentinel|custodian)\b", "warden_armoured", {"humanoid"}),
    (r"\b(matriarch|queen|broodmother|dam)\b", "matriarch_brood", {"humanoid"}),
    (r"\b(overseer|foreman|taskmaster|master|boss)\b", "cult_overseer", {"humanoid"}),
    (r"\b(priest|prophet|oracle|seer|hierophant|bishop|brother|sister)\b", "priest_hooded", {"humanoid"}),
    (r"\b(hunter|tracker|stalker|ranger|marksman|archer)\b", "hunter_ranger", {"humanoid"}),
    (r"\b(champion|warlord|general|commander|marshal|knight)\b", "champion_plate", {"humanoid"}),
    (r"\b(butcher|executioner|headsman|reaper|slayer)\b", "executioner_hooded", {"humanoid"}),
    (r"\b(apothecary|alchemist|chemist|surgeon)\b", "forsaken_apothecary"),
    (r"\b(shaman|witchdoctor|hexxer|voodoo|totem)\b", "troll_witchdoctor"),
    (r"\b(blade|swordsman|duelist|bladedancer)\b", "champion_plate"),
    (r"\b(searing|burning|flame\w*|ember\w*|cinder\w*)\b", "elemental_fire"),
    (r"\b(deviate|mutated|corrupted|twisted|warped)\b", "mutated_thing"),
    (r"\b(hollow|husk|withered|desiccated)\b", "wraith", {"undead", "humanoid"}),
    (r"\b(hound|fang|maw|howl\w*)\b", "worg"),
]

#: A rule may carry a third element: the creature FAMILIES it is allowed to apply to.
#:
#: Some words are species to one creature and a job title to another. "Stalker" is 7 beasts, 3
#: humanoids, 3 insects and 2 demons; "sentinel" is 5 humanoids, 3 elementals, a plant, an insect
#: and a demon. Deleting the word loses the 7 beasts; keeping it ungated drew Sunbleached Stalker,
#: a Glittervein raider, as a panther, and Dryad Sentinel as a stone golem. entities.vendor_trash
#: .classify already works out what a creature IS from its whole name and its template, so the
#: ambiguous rules ask it rather than guessing from one word.
RULES = [(re.compile(r[0], re.I), r[1], (r[2] if len(r) > 2 else None)) for r in _RULES]

#: Last resort when no name pattern matches: the stat template. Deliberately a small, obvious set -
#: anything landing here is a creature the name rules should probably learn about.
TEMPLATE_FALLBACK = {
    "humanoid_warrior": "bandit_human",
    "humanoid_caster": "cultist_robed",
    "humanoid_ranged": "hunter_ranger",
    "humanoid_rogue": "syndicate_rogue",
    "beast_large": "bear",
    "beast_fast": "worg",
    "beast_basic": "boar",
    "vermin_sneaky": "spider",
    "vermin_swarm": "rat_plague",
    "undead_basic": "zombie",
    "elemental_bruiser": "golem_stone",
    "elemental_caster": "elemental_air",
    "demon_caster": "fel_cultist",
    "demon_hound": "felhound",
    "aquatic_basic": "murloc",
}

#: What a creature of each family looks like when no rule matched it at all. Checked BEFORE the
#: stat template, because a template says how a thing fights and a family says what it is.
#: (family, template) -> sprite, checked before FAMILY_FALLBACK. A family says what a thing is and
#: a template says how it fights, and for demons that difference is the whole read: Vile Familiar,
#: Bazzalan and Yarrog Baneshadow are casters, and the family alone drew all three as a hulking
#: melee brute.
FAMILY_TEMPLATE_FALLBACK = {
    ("demon", "demon_caster"): "fel_cultist",
    ("demon", "humanoid_caster"): "fel_cultist",
    # An undead that fights at range is a skeleton with a bow. Only one creature in the game is
    # actually NAMED "Skeleton Archer", so without this the second archer sprite had no customer.
    ("undead", "humanoid_ranged"): "skeleton_archer",
}

#: What family each stat template implies. Used to decide whether the template still has anything
#: useful to say about a creature the name rules missed.
TEMPLATE_FAMILY = {
    "humanoid_warrior": "humanoid", "humanoid_caster": "humanoid", "humanoid_ranged": "humanoid",
    "humanoid_rogue": "humanoid", "beast_large": "beast", "beast_fast": "beast",
    "beast_basic": "beast", "vermin_sneaky": "insect", "vermin_swarm": "insect",
    "undead_basic": "undead", "elemental_bruiser": "elemental", "elemental_caster": "elemental",
    "demon_caster": "demon", "demon_hound": "demon", "aquatic_basic": "aquatic",
}

FAMILY_FALLBACK = {
    "humanoid": "bandit_human", "beast": "bear", "insect": "silithid_worker", "aquatic": "murloc", "undead": "zombie",
    "elemental": "golem_stone", "demon": "demon_brute", "plant": "spore_cap",
}

#: ART THAT EXISTS BUT NOTHING CURRENTLY SELECTS. Kyle: "don't toss the other stuff... Useful
#: later don't lose them just rename them!" A sheet sometimes draws more of something than the
#: game has creatures for - only one creature in the game is a Skeleton Archer, and the sheet drew
#: two. The spare keeps its file under a name that says what it is, and sits here so
#: tools/qa_creature_sprites.py counts it as parked rather than as dead weight. Give one a rule
#: the moment a creature earns it.
SPARE = {
    # Azshara's open-world creatures (docs/azshara_brief.md): sliced and installed with the caves, given to
    # creatures when the creature and quest pass comes. They come off this list then.
    # the great sequoia's bosses (docs/stonetalon_art_prompts.md sheet 4): drawn for the Stonetalon dungeon, which
    # isn't built yet. They come off this list when its bosses exist.
    "demon_brute_2": "second demon brute. Freed up 2026-10-31 when Fel Pup stopped resolving "
                     "here (it is a felhound, not a brute) and no other creature's name hash "
                     "reaches this variant. Kept, not deleted - the next brute-shaped demon "
                     "takes it.",
    "wraith_pale": "fourth wraith; 11 wraith creatures spread over 3 looks.",
    "mountain_giant_granite": "NOTHING IN THE GAME IS A MOUNTAIN GIANT - the only 'giant' names "
                              "are Giant Crab and Giant Spider, where giant is an adjective. Held "
                              "for Feralas and Azshara, which are giant country.",
    "mountain_giant_sandstone": "see mountain_giant_granite.",
    "skeleton_marksman": "second skeleton archer; the game has one archer creature, the sheet "
                         "drew two. Wire up when a second undead ranged type exists.",

    # Parked 2026-10-31, when 61 unreachable creatures were deleted from creatures.json - early
    # generic drafts that later passes replaced with named rosters (Fire Cultist and Magma
    # Elemental became Searing Blade Pyromancer and Molten Elemental; Scarlet Marksman became
    # Scarlet Bowman). The creatures went; the ART is fine and stays, per Kyle on the first
    # sprite sheets: "don't toss the other stuff... Useful later don't lose them just rename
    # them!" Each of these had exactly one customer and now has none.
    "skeleton_archer": "its only customer was the creature Skeleton Archer, a deleted draft. "
                       "The game still has skeletons - wire up when one is a ranged type.",
    "kobold_2": "second kobold look; its users were Rotting Kobold and Savage Rotting Kobold, "
                "both deleted drafts. Live kobolds all reach kobold_1.",
    "elemental_fire_1": "drawn for the deleted Magma/Lava draft set. Ragefire Chasm's real "
                        "roster resolves elsewhere; hold for a fire zone.",
    "spectre_2": "second spectre; its user was the deleted Cursed Spirit draft.",
    "vine_strangler_2": "second strangler; its user was the deleted Twisted Sapling draft.",
}


# THE PLAGUELANDS' PEOPLE AND DUNGEON BOSSES (Kyle's sheets 7 and 8, 16 Nov 2026), parked until their creatures
# exist: Scholomance, Stratholme and Hearthglen are carved but not yet wired (docs/plaguelands_dungeons_structure.md),
# and the Pale Flame, Forsaken and Argent Dawn figures go on the zone's people when its towns are rebuilt. Each comes
# off this list the moment a creature or an NPC draws it.
for _sid in ("ad_crusader ad_priestess pl_deathguard pl_forsaken_apothecary pf_chaplain pf_knight pf_quartermaster "
             "pf_rory_callahan pf_scout pf_sentry hg_scarlet_charger strat_deathcharger pl_silver_hand_ghost "
             "scholo_ghost_servant").split():
    SPARE.setdefault(_sid, "a Plaguelands figure, parked until the zone's people or the dungeon it's for are wired")
for _sid in [x for x in SHEETS["plaguelands_scarlet"] + SHEETS["plaguelands_dungeon_bosses"]
             if x.startswith(("hg_boss_", "scholo_boss_", "strat_boss_", "pl_boss_"))]:
    SPARE.setdefault(_sid, "a Plaguelands dungeon boss, parked until Scholomance, Stratholme or Hearthglen is wired")

# the Plaguelands' dungeons are wired (16 Nov 2026): the art their creatures draw comes off the spare list
for _sid in ('abomination_1 abomination_2 banshee ghoul_1 ghoul_gaunt hg_boss_arcanist hg_boss_crimson_choir hg_boss_drillmaster hg_boss_gatewarden hg_boss_high_inquisitor hg_boss_kennelmaster hg_boss_lady_marden hg_boss_quartermaster hg_boss_victor_hale hg_boss_volkov necromancer pl_boss_abom_butcher pl_boss_cult_necromancer pl_boss_eye_construct pl_boss_gate_guardian pl_boss_lich_magistrate pl_crypt_fiend pl_cult_lieutenant pl_cult_neophyte pl_cult_plaguebringer pl_dark_caster pl_darrowshire_ghost pl_death_knight pl_flesh_golem pl_frenzied_ghoul pl_gargoyle pl_necrolyte pl_plague_eruptor pl_plague_slime pl_plaguebat pl_silver_hand_ghost pl_skeletal_mage pl_wailing_spirit revenant_2 sc_adept sc_arcanist sc_centurion sc_chaplain sc_inquisitor sc_judicator sc_knight sc_monk sc_myrmidon sc_tp_champion sc_tp_cleric sc_tp_crusader sc_tp_inquisitor sc_tp_sniper sc_war_hound sc_zealot scholo_boss_alchemist scholo_boss_bone_construct scholo_boss_frost_lich scholo_boss_gargoyle scholo_boss_ghost_lady scholo_boss_headmaster scholo_boss_instructor scholo_boss_librarian scholo_boss_noble_lady scholo_boss_noble_lord scholo_ghost_servant skeleton_warrior_1 skeleton_warrior_2 spectre_1 spectre_2 spider_4 spider_hatchling strat_boss_archivist strat_boss_baron strat_boss_baroness strat_boss_cannon_master strat_boss_crypt_lord strat_boss_flesh_golem strat_boss_ghoul_runt strat_boss_grand_crusader strat_boss_lich strat_boss_magistrate zombie_1 zombie_3 zombie_4 zombie_5 zombie_6'.split()):
    SPARE.pop(_sid, None)

# Kyle's sheet 10 (17 Nov 2026): the hidden places' creatures and three of their people wear it. These have nobody
# to wear them yet: a camp, a fisherwoman, wildlife and set dressing for when the hidden places get more people.
for _sid in ("ps_stone_age_woman ps_palaeontologist ps_frozen_hunter ps_forsaken_fisherwoman ps_bog_eel ps_reed_heron "
             "ps_wardstone ps_dead_elf_ranger").split():
    SPARE.setdefault(_sid, "sheet 10 figure for the Plaguelands' hidden places, parked until someone stands there")
# worn by people, not creatures: copied to assets/npcs/leaders/<their id>/down.png, which is where the renderer
# looks for a named person's own figure
for _sid in ("ps_finnish_scientist", "ps_elf_ranger", "ps_elf_quartermaster"):
    SPARE.setdefault(_sid, "sheet 10 figure worn by a named person (assets/npcs/leaders), not by a creature")
# Deadwind's two who aren't people any more (tools/build_deadwind.py): worn by Grull the Younger and the Bridge Echo
# through their own NPC races (assets/npcs/ogre, assets/npcs/echo), never by a hostile
for _sid in ("dw_twice_ogre", "dw_echo"):
    SPARE.setdefault(_sid, "a Deadwind figure worn by a named person (Grull, the Bridge Echo), not by a creature")

DEFAULT = "bandit_human"

#: 23 rules used to name species no creature in the game actually has - gargoyle, dryad, tiger,
#: lich. They were written from imagination while the sprite list was, and when SHEETS was rebuilt
#: from real usage their art was correctly dropped, leaving the rules pointing at nothing. Rather
#: than delete them or spend scarce cells on monsters that do not exist, each now resolves to its
#: nearest drawn neighbour: add a gargoyle later and it draws the crypt fiend until it earns art.


def _family(name, template):
    try:
        from entities.vendor_trash import classify
        return classify(name or "", template)[0]
    except Exception:
        return None


_HIDDEN = None


def _hidden_sprites():
    """Exact names -> sprite, for the hidden zones' creatures (data/creatures/hidden_sprites.json,
    written by tools/build_hidden_content.py). Kept out of _RULES so nothing here names them."""
    global _HIDDEN
    if _HIDDEN is None:
        import json
        try:
            _HIDDEN = json.loads((Path(__file__).resolve().parent / "data/creatures/hidden_sprites.json")
                                 .read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _HIDDEN = {}
    return _HIDDEN


def sprite_for(name, template=None):
    """-> sprite id for a creature. Never None, so nothing ever renders as a red box again."""
    if name in _hidden_sprites():
        return _hidden_sprites()[name]
    fam = None
    for rx, sprite, only in RULES:
        if not rx.search(name or ""):
            continue
        if only is not None:
            if fam is None:
                fam = _family(name, template)
            if fam not in only:
                continue        # right word, wrong kind of creature - keep looking
        return sprite
    # A non-humanoid that matched nothing gets its FAMILY's sprite rather than its stat template's.
    # Chitterlord Skrix is an insect on a humanoid_caster template, and the template alone drew it
    # as a robed cultist.
    fam = fam if fam is not None else _family(name, template)
    if (fam, template) in FAMILY_TEMPLATE_FALLBACK:
        return FAMILY_TEMPLATE_FALLBACK[(fam, template)]
    # THE TEMPLATE WINS WHEN IT AGREES WITH THE FAMILY, because it is the more specific of the
    # two: beast_fast -> worg says more than beast -> bear. Putting the family first made Alpha
    # Fenris, a beast_fast wolf boss, draw as a bear. The family only takes over when the two
    # disagree - an insect on a humanoid_caster template, where the template is simply wrong
    # about what the thing is.
    if TEMPLATE_FAMILY.get(template) == fam and template in TEMPLATE_FALLBACK:
        return TEMPLATE_FALLBACK[template]
    if fam in FAMILY_FALLBACK:
        return FAMILY_FALLBACK[fam]
    return TEMPLATE_FALLBACK.get(template, DEFAULT)


def sprite_file(name, template=None):
    """-> the sprite id to actually draw for this creature, variant included.

    The variant is chosen by hashing the creature's name, which keeps it stable across sessions
    and across machines without storing anything: the same gnoll is always the same gnoll.
    """
    base = sprite_for(name, template)
    n = VARIANTS.get(base)
    if not n:
        return base
    # zlib.crc32 rather than hash(): Python's hash is randomised per process, so a creature would
    # change its appearance every time the game restarted.
    import zlib
    return f"{base}_{zlib.crc32((name or '').encode('utf-8')) % n + 1}"


def sprite_path(sprite_id):
    return SPRITE_DIR / f"{sprite_id}.png"
