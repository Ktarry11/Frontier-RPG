#!/usr/bin/env python3
"""Writes data/items/quest_item_icons.json: quest item_id -> icon id.

Icons come from two sheets: qi_* (assets/icons/quest_items, claude/quest_item_icon_prompts.md) and vt_* (the vendor
trash sheet in assets/icons/vendor_trash).  LootItem looks this table up whenever a quest item is created without an
explicit icon_id (drops, quest grants and old saves all go through the same constructor).  Reusing one icon for many
items is intentional (hue shifts can come later).

    python3 tools/build_quest_item_icons.py      # rewrites the json and checks every icon file exists
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

GROUPS = {
    # documents
    "qi_letter": "keep_dispatch scarlet_dispatch sps_deserter_letter rennick_dispatch sep_dispatch uc_oswin_reply",
    "qi_scroll": "burning_blade_orders scarlet_battle_orders plaguemaster_formula uc_sennarath_scroll sp_rite_scroll",
    "qi_papers": "crusade_orders sps_scout_report cult_ledger_bundle uc_sable_report",
    "qi_page": "dig_ledger_page cult_ledger_page pd_surgeon_notes uc_groundskeeper_scrap sps_tome_page fen_logbook_page",
    "qi_ledger": "highwayman_ledger pd_courtier_ledger sps_helbrim_ledger",
    "qi_journal": "pd_voss_codex sp_wl_journal",
    "qi_chart": "waterlogged_chart",
    "qi_ticket": "sps_ferry_ticket uc_muster_slip",
    # keys, seals, tokens
    "qi_key_iron": "captured_farmer_shackle_key",
    "qi_key_brass": "sps_servitor_key",
    "qi_shackle": "fen_cur_collar",
    "qi_signet": "lordaeron_signet pd_noble_signet sp_crow_ring fen_noble_signet",
    "qi_ward_seal": "ward_seal_stone faols_seal_fragment sps_grave_token sps_gilnean_seal",
    "qi_dog_tag": "sps_deserter_tag",
    "qi_prayer_beads": "pilgrim_prayer_beads",
    "qi_coin_pouch": "cultist_hoarded_coin razormane_toll_pouch",
    # containers
    "qi_crate": "salvaged_caravan_crate salvaged_cargo_crate stolen_cargo sps_cargo_crate",
    "qi_strongbox": "waterlogged_strongbox",
    "qi_powder_keg": "bandit_powder_keg powder_charge",
    "qi_seed_sack": "trampled_grain_sack groldom_seed_sack sp_seed_sack",
    "qi_flask": "crude_sludge_sample pd_vat_tissue sps_marsh_sample",
    "qi_vial": "pd_sump_vial uc_stray_vial sps_reagent_vial",
    "qi_clay_jar": "sep_spider_fat",
    "qi_egg": "sunscale_raptor_egg",
    # minerals and relics
    "qi_ore": "mesa_ore ragefire_ore_sample vein_core_sample",
    "qi_crystal": "spire_wind_crystal iceshard_fragment",
    "qi_amber": "hive_amber_shard sps_amber_resin",
    "qi_coral": "sturdy_reef_coral",
    "qi_tablet": "scourge_rune_shard sep_relic_shard",
    "qi_headstone": "weathered_grave_marker",
    "qi_heart_stone": "smouldering_imp_heart peat_heart",
    "qi_chalice": "grave_relic",
    # plants
    "qi_herbs": "sp_harrower_straw",
    "qi_petals": "sagewood_petal",
    "qi_moss": "sp_grave_moss",
    "qi_pumpkin": "blighted_pumpkin sp_rotapple_core",
    "qi_seed_packet": "unburnt_seed_packet",
    "qi_wreath": "sep_wilted_wreath",
    "qi_dewleaf": "nightmare_dewdrop",
    "qi_root": "moonwell_root_sample",
    # tools and trophies
    "qi_horn": "sentinel_signal_horn hunters_horn_shard",
    "qi_lantern": "sps_miner_lamp oil_pressure_gauge",
    "qi_harpoon": "fen_harpoon_head",
    "qi_pennant": "kolkar_warpennant",
    "qi_totem": "hexed_darkspear_totem kolkar_windseer_totem witchwing_hex_totem corrupted_furbolg_totem fang_totem_shard",
    "qi_trophy_cord": "eel_hide_cord skinner_trophy_cord sps_alpha_tooth",
    "qi_gold_thread": "spun_gold_thread",
    # vendor-trash sheet icons that suit quest items
    "vt_feathers": "sunbaked_vulture_feather witchwing_feather razormane_quill_bundle thunderhawk_pinion harpy_roost_down",
    "vt_horn_chunk": "sunworn_horn",
    "vt_raw_hide": "quilboar_battle_hide sunscale_raptor_hide",
    "vt_tusk": "ceremonial_bristleback_tusk battleboar_tusk",
    "vt_chitin_plate": "hardened_silithid_chitin tunnel_guard_chitin",
    "vt_stinger": "silithid_stinger_barb sep_wasp_sting",
    "vt_silk_ball": "den_silk forest_spider_silk",
    "vt_shard": "fel_shard golem_core_shard ore_sprite_shard",
    "vt_pelt": "durotar_prowler_pelt sps_wolf_pelt",
    "vt_ash": "searing_ritual_ash",
    "vt_fish_scales": "tide_etched_scale",
    "vt_pearl": "tidecaller_pearl tide_touched_pearl naralex_dream_pearl oracle_pearl",
    "vt_bone": "hex_bone_shard giant_knucklebone sps_wight_bone sep_bone_marrow",
    "vt_thorn_vine": "tangle_vine_heart",
    "vt_shell": "snapper_shell_plate",
    "vt_geode": "rift_geode",
    "vt_seed_pod": "kraul_seed_pod",
    "vt_venom_gland": "slug_venom_gland venom_sac sp_venom_gland sp_wl_venomsac",
    "vt_broken_dagger": "dervish_curved_blade",
    "vt_spore_cap": "gloomcap_spore_sac",
    "vt_bark": "timberling_heartwood",
    "vt_ghost_vial": "wisp_light_essence",
    "vt_locket": "windrunner_family_locket tarnished_keepsake moldering_locket sep_cracked_locket sp_farmhand_locket",
    "vt_rags": "fel_imp_hoard_scrap stolen_village_scrap sps_quilt_scrap",
    "vt_sigil": "legion_brand_plate sps_cult_sigil",
    "vt_shroud": "tattered_burial_shroud",
    "vt_fang": "hydra_fang sp_slitherer_fang fen_moon_fang",
    "vt_egg_sac": "sp_skitter_sac",
    "vt_fur_tuft": "fen_banshee_lock",
}

# ---- Tanaris 2026-10-30: Glittervein, the Abyssal Sands and the Lashings. Thirty items that
# ---- shipped with no mapping at all, which LootItem resolves to nothing and the UI draws as a
# ---- coloured square. Reusing one icon across several items is the established pattern here.
TANARIS = {
    # --- documents and records. These three zones are full of people keeping books.
    "qi_ledger": "gv_drowned_ledger",
    "qi_papers": "ab_sealed_waybill lsh_chewed_articles",
    "qi_ticket": "lsh_prize_tag",
    "qi_dog_tag": "ab_drovers_tag gv_shift_token",
    # --- survey and dig kit
    "qi_tablet": "ab_second_peg_head gv_bench_marker",
    "qi_ore": "gv_salvaged_iron lsh_ships_nail ab_lifted_brass",
    "qi_powder_keg": "lsh_short_keg",
    "qi_crate": "ab_shrike_crop",
    # --- the seams: this is the zone that is made of crystal
    "qi_crystal": "gv_rough_seam_glass gv_spun_glass gv_struck_shard gv_tideglass_core",
    "vt_geode": "gv_lattice_core ab_fused_shard",
    "vt_shard": "gv_settled_light",
    # --- the water
    "qi_vial": "gv_sealed_deepwater ab_ooze_residue",
    "vt_fish_scales": "ab_wet_scale",
    # --- off things that were alive
    "vt_chitin_plate": "ab_crawler_plate",
    "vt_thorn_vine": "ab_lurker_spur",
    "vt_bone": "ab_salt_knuckle",
    "qi_herbs": "gv_shelf_blindweed",
    # --- rope, net and harness
    "qi_trophy_cord": "lsh_cut_net ab_kodo_harness",
    "qi_chart": "gv_scav_tally",
    # --- CARRIED ITEMS COUNT TOO. grant_items.on_accept creates a quest item through the same
    # --- constructor as a drop, so a letter the giver hands you needs a mapping exactly as much
    # --- as something you loot. Nine of these were missed by looking only at quest_drops.json.
    "qi_journal": "ab_collapse_log gv_tally_book",
    "qi_letter": "ab_ullas_reply gv_ullas_account gv_ullas_finding",
    "qi_page": "gv_copied_column lsh_closing_entry gv_works_order_paper",
    "qi_amber": "gv_cut_plate",
}
GROUPS.update(TANARIS)


def main():
    table = {}
    for icon, ids in GROUPS.items():
        for item_id in ids.split():
            if item_id in table and table[item_id] != icon:
                raise SystemExit(f"{item_id} mapped twice: {table[item_id]} and {icon}")
            table[item_id] = icon
    icon_dirs = [ROOT / "assets" / "icons" / "quest_items", ROOT / "assets" / "icons" / "vendor_trash"]
    missing = sorted({i for i in table.values() if not any((d / f"{i}.png").exists() for d in icon_dirs)})
    if missing:
        raise SystemExit(f"missing icon files: {missing}")
    out = {"_notes": "quest item_id -> icon id. Built by tools/build_quest_item_icons.py. Used by entities/loot_item.py "
                     "when a quest item has no explicit icon_id.", "icons": dict(sorted(table.items()))}
    (ROOT / "data" / "items" / "quest_item_icons.json").write_text(json.dumps(out, indent=1) + "\n")
    print(len(table), "quest items mapped to", len(set(table.values())), "icons")


if __name__ == "__main__":
    main()
