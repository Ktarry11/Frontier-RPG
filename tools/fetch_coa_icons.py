#!/usr/bin/env python3
"""Fetch real icon art for the CoA classes' skills and talents.

    python3 tools/fetch_coa_icons.py --dry-run          # just check every name resolves
    python3 tools/fetch_coa_icons.py --class barbarian  # fetch and install one class
    python3 tools/fetch_coa_icons.py                    # fetch and install everything mapped

Third in the same family as tools/fetch_classic_ability_icons.py and
tools/fix_talent_icons.py, and built the same way for the same reason: a
hand-curated `id -> icon name` table is exactly why the classic-9 abilities
already look right.

WHY THIS EXISTS. tools/audit_icon_coverage.py reports 1458 abilities and
talents rendering as a flat coloured square and another 190 all drawing the
same `ability_melee` sword. Thirteen classes have no art of their own at
all: barbarian, bloodmage, chronomancer, felsworn, guardian,
knight_of_xoroth, necromancer, pyromancer, ranger, reaper, templar,
witch_doctor and witch_hunter.

fix_talent_icons.py drew a line that is worth restating, because this tool
deliberately sits on the other side of it: it mapped only the classic-9
talents, "because those are real WoW talents with canonical icons that can
be looked up and verified", and sent the homebrew ones to art direction
instead. These CoA talents are homebrew too - there is no canonical icon
for "Trip to the Alehouse". But there are tens of thousands of Blizzard
icons covering every fantasy concept in the game, so a THEMATIC match is
nearly always available and is a great deal better than a coloured square.
So the mapping below is chosen by subject rather than looked up by name,
and the choice is the part that needs a human eye - see the review note at
the bottom.

EVERY FETCH IS VERIFIED, the same way fix_talent_icons.py does it. A wrong
icon name does not 404 cleanly on this CDN in every case - it can return an
HTML error page with a 200 - so a byte-length check or a status check alone
would silently install a broken file. Each response is opened with PIL and
rejected unless it is a real image of a sane size. Nothing is written to
assets/ until it passes.
"""

from __future__ import annotations

import hashlib
import io
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CDN = "https://wow.zamimg.com/images/wow/icons/large/{}.jpg"
ABILITY_DIR = ROOT / "assets/icons/abilities"
TALENT_DIR = ROOT / "assets/icons/talents"

#: id -> Blizzard icon name, or (icon name, hue shift in degrees).
#:
#: THE HUE SHIFT IS NOT DECORATION. 50 of Barbarian's 115 ids map onto a
#: base icon that another id also uses, and without a shift they install
#: BYTE-IDENTICAL files - which is the exact defect tools/fix_talent_icons.py
#: was written to repair ("146 talents shared only 59 icon images ...
#: Starlight Wrath and Arcane Barrage were byte-identical"). Reusing a base
#: is usually right, because most of these pairs are a talent and the
#: ability it modifies and they SHOULD look related; they just must not be
#: the same picture. boss_icon_tint.hue_shift rotates only the Hue channel
#: of an HSV decomposition, so linework, shading and highlights survive
#: intact and only the colour family moves - which is why a flat colour
#: multiply was rejected for the boss portraits and is wrong here too.
#:
#: Shifts are kept small on purpose (Kyle: "rehue them slightly"). Large
#: rotations turn a brown tankard pink and a steel axe green; 15-35 degrees
#: reads as a variant of the same thing.
#:
#: Grouped by class, then by tree, in the order
#: the game data lists them, so a reviewer can read this next to the talent
#: tree and check the choices. Populated class by class; a class absent
#: here simply has not been mapped yet.
MAPPING: dict[str, str] = {}

# =====================================================================
# BARBARIAN - Northrend vrykul (frost, ancestors, ale) crossed with troll
# headhunter (thrown spears, bleeding). Frost icons for the Ancestry tree,
# plain warrior melee for Brutality, thrown/bleed for Headhunting.
# =====================================================================
MAPPING.update({
    # --- Ancestry: frost, ancestors, drink
    "barbarian_ancestry_trip_to_the_alehouse": ("inv_drink_05", 40),
    "barbarian_ancestry_drinking_frenzy": "ability_warrior_rampage",
    "barbarian_ancestry_fill_level": "inv_drink_12",
    "barbarian_ancestry_frozen_warlord": "spell_frost_frozencore",
    "barbarian_ancestry_improved_ancestral_combat": ("spell_nature_spiritarmor", 40),
    "barbarian_ancestry_ice_cold_bubbles": "spell_frost_frostbolt02",
    "barbarian_ancestry_thanes_guard": "inv_shield_06",
    "barbarian_ancestry_liquid_courage": "inv_drink_09",
    "barbarian_ancestry_cold_brew": "inv_drink_17",
    "barbarian_ancestry_blind_stupor": "spell_shadow_mindsteal",
    "barbarian_ancestry_unified_rage": ("ability_warrior_bloodfrenzy", 40),
    "barbarian_ancestry_hodirs_revenge": "spell_frost_wisp",
    "barbarian_ancestry_icebound_ancestry": ("spell_frost_arcticwinds", 40),
    "barbarian_ancestry_frost_giants_fury": "spell_frost_frostshock",
    "barbarian_ancestry_the_spins": ("spell_nature_spiritwolf", 40),
    "barbarian_ancestry_breaking_morale": "ability_warrior_warcry",
    "barbarian_ancestry_might_of_utgarde": ("spell_nature_spiritarmor", 200),
    "barbarian_ancestry_frozen_blades": ("spell_frost_frostbrand", 40),
    "barbarian_ancestry_ancestors_fury": "spell_frost_frostward",
    "barbarian_ancestry_rage_of_the_north": "spell_frost_chillingblast",
    "barbarian_ancestry_uniting_voice": "spell_holy_prayerofspirit",
    "barbarian_ancestry_clanlords_totem": ("spell_nature_strengthofearthtotem02", 40),
    "barbarian_ancestry_fury_of_the_north": "spell_frost_summonwaterelemental",
    # --- Brutality: unadorned melee
    "barbarian_brutality_pure_power": ("ability_warrior_savageblow", 40),
    "barbarian_brutality_reckless_movements": "ability_warrior_innerrage",
    "barbarian_brutality_savage_strength": "ability_rogue_sprint",
    "barbarian_brutality_excessive_power": "spell_nature_unyeildingstamina",
    "barbarian_brutality_bloody_fighter": "ability_criticalstrike",
    "barbarian_brutality_relentless": "ability_warrior_endlessrage",
    "barbarian_brutality_efficient_killer": "ability_warrior_sunder",
    "barbarian_brutality_ogres_strength": "ability_racial_bloodrage",
    "barbarian_brutality_spiked_weapons": "inv_mace_01",
    "barbarian_brutality_anger_issues": "spell_shadow_summonimp",
    "barbarian_brutality_battering_ram": "ability_warrior_shieldbash",
    "barbarian_brutality_horde_breaker": "ability_warrior_riposte",
    "barbarian_brutality_headlopper": "ability_hunter_assassinate",
    "barbarian_brutality_crusher": "inv_hammer_16",
    "barbarian_brutality_whirling_assault": ("ability_warrior_charge", 40),
    "barbarian_brutality_rancor": ("ability_warrior_cleave", 40),
    "barbarian_brutality_thirst_for_battle": "spell_nature_bloodlust",
    "barbarian_brutality_sustaining_swings": "spell_shadow_lifedrain",
    "barbarian_brutality_overkill": ("inv_sword_48", 40),
    "barbarian_brutality_body_builder": "ability_hunter_pet_gorilla",
    "barbarian_brutality_blood_and_glory": "ability_warrior_bloodbath",
    "barbarian_brutality_steelslinger": "ability_warrior_trauma",
    "barbarian_brutality_maximum_carnage": ("ability_warrior_bladestorm", 40),
    # --- Headhunting: thrown spears, bleeds, troll
    "barbarian_headhunting_strong_arm": ("ability_throw", 40),
    "barbarian_headhunting_puncture_wounds": "ability_rogue_rupture",
    "barbarian_headhunting_gruesome": ("ability_rogue_disembowel", 40),
    "barbarian_headhunting_guts_splatter": "ability_warrior_revenge",
    "barbarian_headhunting_frothing_savage": "ability_hunter_swiftstrike",
    "barbarian_headhunting_entrails": "inv_misc_organ_01",
    "barbarian_headhunting_to_the_bone": ("ability_warrior_riposte", 40),
    "barbarian_headhunting_savage": "ability_druid_mangle2",
    "barbarian_headhunting_spear_thrower": ("inv_spear_07", 40),
    "barbarian_headhunting_legacy_of_the_amani": "inv_spear_04",
    "barbarian_headhunting_furious_berserker": ("racial_troll_berserk", 40),
    "barbarian_headhunting_no_survivors": "ability_rogue_bloodsplatter",
    "barbarian_headhunting_time_to_kill": "ability_warrior_challange",
    "barbarian_headhunting_hunting_for_sport": "ability_hunter_markedfordeath",
    "barbarian_headhunting_vengeance_for_zuljin": "inv_misc_head_troll_01",
    "barbarian_headhunting_raging_spirit": "spell_shadow_shadowfiend",
    "barbarian_headhunting_payback": "ability_gouge",
    "barbarian_headhunting_skullseeker": "inv_misc_bone_skull_01",
    "barbarian_headhunting_spear_shards": ("inv_spear_06", 40),
    "barbarian_headhunting_brutal_form": "spell_nature_healingtouch",
    "barbarian_headhunting_gurubashi_technique": "inv_weapon_shortblade_15",
    "barbarian_headhunting_senjins_guidance": ("inv_spear_05", 40),
    "barbarian_headhunting_berserker": "racial_troll_berserk",
    # --- Abilities, blank
    "barbarian_unbridled_rage": "spell_shadow_unholyfrenzy",
    "barbarian_defiance": "ability_warrior_defensivestance",
    "barbarian_jawbreaker": "inv_gauntlets_04",
    "barbarian_maiming_spear": "ability_hunter_snipershot",
    "barbarian_skull_smash": "inv_misc_bone_skull_02",
    "barbarian_ancestral_roar": "ability_druid_challangingroar",
    "barbarian_warband": "spell_holy_prayerofhealing",
    "barbarian_thick_skull": "inv_helmet_23",
    "barbarian_hodirs_wrath": "spell_frost_glacier",
    "barbarian_onslaught": "ability_warrior_focusedrage",
    "barbarian_battle_vigor": "ability_warrior_rallyingcry",
    "barbarian_savage_revelry": "inv_drink_07",
    "barbarian_axe_twirling": "ability_rogue_dualweild",
    "barbarian_ancestral_combat": "spell_nature_spiritarmor",
    "barbarian_ancestral_fury": "spell_shaman_unleashweapon_wind",
    "barbarian_breath_of_the_north": "spell_frost_arcticwinds",
    "barbarian_frozen_blades": "spell_frost_frostbrand",
    "barbarian_frozen_tankard": "inv_drink_16",
    "barbarian_ramhorn_rage": "ability_hunter_pet_ravager",
    "barbarian_ancestors_call": "spell_nature_spiritwolf",
    "barbarian_cheers": "inv_drink_04",
    "barbarian_war_cry": "ability_warrior_battleshout",
    "barbarian_splash_zone": "inv_drink_milk_01",
    "barbarian_ale_of_the_god_king": "inv_drink_21",
    "barbarian_tavern_brawl": "inv_misc_beer_02",
    "barbarian_clanlords_totem": "spell_nature_strengthofearthtotem02",
    # --- Abilities currently sharing ability_melee
    "barbarian_attack": "ability_meleedamage",
    "barbarian_ancestral_strike": "ability_warrior_decisivestrike",
    "barbarian_whirling_advance": "ability_warrior_charge",
    "barbarian_barbaric_whirl": "ability_whirlwind",
    "barbarian_headhunters_spear": "ability_throw",
    "barbarian_smash": "ability_warrior_savageblow",
    "barbarian_brutal_swing": "ability_warrior_cleave",
    "barbarian_decapitate": "inv_sword_48",
    "barbarian_crush": "ability_warrior_shockwave",
    "barbarian_killing_spree": "ability_rogue_murderspree",
    "barbarian_storm_of_steel": "ability_warrior_bladestorm",
    "barbarian_throw_weapon": "ability_rogue_throwingspecialization",
    "barbarian_barbed_spear": "inv_spear_07",
    "barbarian_gutspiller": "ability_rogue_disembowel",
    "barbarian_berserker_rush": "ability_heroicleap",
    "barbarian_berserker_axe": "inv_axe_66",
    "barbarian_impaling_spear": "inv_spear_06",
    "barbarian_javelin_toss": "inv_spear_05",
    "barbarian_spite": "ability_rogue_fanofknives",
    "barbarian_keg_smash": "inv_drink_05",
})


#: CLASS CRESTS, which live somewhere else entirely:
#: assets/ui/class_icons/<class>.png, read by the character creation
#: screen. That directory holds exactly the original nine, so all 21 CoA
#: classes show up blank on the one screen every new player sees first -
#: the most visible single art gap in the game, and the cheapest to close.
#: These are chosen to be distinguishable at 36px in a list of thirty, so
#: they separate by SHAPE first: Felsworn, Knight of Xoroth and Cultist are
#: all dark-and-horned by theme, and colour is the first thing that
#: disappears at that size.
CLASS_CRESTS: dict[str, str] = {
    "necromancer": "spell_shadow_raisedead",
    "pyromancer": "spell_fire_fireball02",
    "cultist": "spell_shadow_evileye",
    "starcaller": "spell_nature_starfall",
    "sun_cleric": "spell_holy_divineillumination",
    "tinker": "trade_engineering",
    "runemaster": "inv_misc_rune_01",
    "primalist": "spell_nature_spiritwolf",
    "reaper": "spell_shadow_soulleech_3",
    "venomancer": "ability_creature_poison_06",
    "chronomancer": "spell_nature_timestop",
    "bloodmage": "spell_shadow_lifedrain",
    "guardian": "ability_warrior_shieldguard",
    "stormbringer": "spell_nature_callstorm",
    "felsworn": "spell_shadow_summonfelhunter",
    "barbarian": "ability_warrior_rampage",
    "witch_doctor": "inv_misc_idol_03",
    "witch_hunter": "inv_weapon_crossbow_10",
    "knight_of_xoroth": "spell_shadow_deathpact",
    "templar": "spell_holy_crusaderaura",
    "ranger": "ability_hunter_mastermarksman",
}
CREST_DIR = ROOT / "assets/ui/class_icons"


# =====================================================================
# BLOODMAGE - San'layn. The talents name Lana'thel, Valanar, Keleseth,
# Taldaram and Atherann, so the whole class is blood and Shadow and
# everything in it is red. The four trees are deliberately pulled apart by
# SUBJECT rather than colour, because 92 red talents in one palette read as
# one undifferentiated smear on the talent screen:
#   Accursed    feral - fangs, claws, the body as a weapon
#   Eternal     defensive and nocturnal - hide, plate, blood as armour
#   Fleshweaver the healer - stitching, organs, surgery
#   Sanguine    the caster - bolts, chalices, sigils
# =====================================================================
MAPPING.update({
    # --- Accursed: feral
    "bloodmage_accursed_rage": ("ability_warrior_rampage", 40),
    "bloodmage_accursed_barely_human": ("spell_shadow_twistedfaith", 40),
    "bloodmage_accursed_forbidden_power": ("spell_shadow_shadowpower", 40),
    "bloodmage_accursed_killer_instinct": "ability_druid_predatoryinstincts",
    "bloodmage_accursed_dark_hunt": ("spell_shadow_painspike", 40),
    "bloodmage_accursed_crimson_expedition": "ability_criticalstrike",
    "bloodmage_accursed_one_mans_curse": ("spell_shadow_blackplague", 40),
    "bloodmage_accursed_relentless": "ability_warrior_endlessrage",
    "bloodmage_accursed_gore_barrage": ("ability_rogue_bloodsplatter", 40),
    "bloodmage_accursed_unchained": ("spell_shadow_unholyfrenzy", 40),
    "bloodmage_accursed_blood_shards": "inv_misc_gem_bloodstone_01",
    "bloodmage_accursed_cruel_intent": "ability_rogue_dualweild",
    "bloodmage_accursed_everlasting_hunt": "ability_hunter_huntervswild",
    "bloodmage_accursed_fang_over_fang": ("ability_druid_ferociousbite", 200),
    "bloodmage_accursed_dark_sigil": "inv_misc_rune_06",
    "bloodmage_accursed_sanguine_scripture": "inv_misc_book_11",
    "bloodmage_accursed_battleweaver": "spell_shadow_shadowward",
    "bloodmage_accursed_crimson_feast": ("spell_deathknight_bloodtap", 40),
    "bloodmage_accursed_terrorizer": "spell_shadow_possession",
    "bloodmage_accursed_night_hunter": "ability_stealth",
    "bloodmage_accursed_blood_scent": "ability_tracking",
    "bloodmage_accursed_darkcasting": ("spell_shadow_curseofachimonde", 200),
    "bloodmage_accursed_ultra_instinct": "ability_druid_primalprecision",
    # --- Eternal: defensive, nocturnal
    "bloodmage_eternal_heightened_reflexes": "ability_rogue_quickrecovery",
    "bloodmage_eternal_eternal_hunt": ("spell_shadow_lifedrain02", 200),
    "bloodmage_eternal_uncanny_movement": "ability_rogue_sprint",
    "bloodmage_eternal_thick_pelt": "inv_misc_pelt_wolf_01",
    "bloodmage_eternal_vitality": "spell_nature_unyeildingstamina",
    "bloodmage_eternal_shadows_in_the_night": ("spell_shadow_nethercloak", 40),
    "bloodmage_eternal_feral_strength": ("ability_druid_catform", 40),
    "bloodmage_eternal_no_mercy": "ability_warrior_shieldguard",
    "bloodmage_eternal_blood_moon": "spell_nature_elementalprecision_1",
    "bloodmage_eternal_infection": ("ability_creature_disease_02", 40),
    "bloodmage_eternal_appetite_for_blood": ("ability_druid_rake", 40),
    "bloodmage_eternal_rejuvenating_shadows": ("spell_shadow_shadowmend", 40),
    "bloodmage_eternal_grim_omen": ("spell_shadow_requiem", 40),
    "bloodmage_eternal_iron_claws": "inv_gauntlets_04",
    "bloodmage_eternal_blood_mark": ("spell_shadow_antishadow", 40),
    "bloodmage_eternal_dark_mark": "spell_shadow_auraofdarkness",
    "bloodmage_eternal_uncanny_speed": "ability_rogue_fleetfooted",
    "bloodmage_eternal_rabid": ("ability_druid_challangingroar", 40),
    "bloodmage_eternal_eternal_presence": ("spell_deathknight_bloodpresence", 40),
    "bloodmage_eternal_bloodmoon_power": ("spell_shadow_summonvoidwalker", 40),
    "bloodmage_eternal_enraging_wounds": "ability_warrior_bloodbath",
    "bloodmage_eternal_bloody_claws": ("ability_druid_mangle2", 40),
    "bloodmage_eternal_eyes_in_the_night": "spell_shadow_evileye",
    # --- Fleshweaver: the healer
    "bloodmage_fleshweaver_gift_of_lanathel": ("spell_shadow_soulgem", 40),
    "bloodmage_fleshweaver_organ_orbs": "inv_misc_organ_01",
    "bloodmage_fleshweaver_consolidation": "spell_nature_timestop",
    "bloodmage_fleshweaver_raging_hunger": ("spell_shadow_bloodboil", 200),
    "bloodmage_fleshweaver_teachings_of_lanathel": "inv_misc_book_09",
    "bloodmage_fleshweaver_excess_blood": "spell_holy_healingaura",
    "bloodmage_fleshweaver_spice_of_life": ("spell_shadow_curseofsargeras", 40),
    "bloodmage_fleshweaver_blood_redistribution": ("spell_holy_blessedrecovery", 40),
    "bloodmage_fleshweaver_black_heart": "inv_misc_organ_04",
    "bloodmage_fleshweaver_sanguine_scion": ("spell_shadow_lifedrain", 200),
    "bloodmage_fleshweaver_waves_of_blood": ("spell_holy_prayerofhealing02", 40),
    "bloodmage_fleshweaver_universal_donor": ("spell_holy_sealofsacrifice", 40),
    "bloodmage_fleshweaver_gruesome_rituals": ("spell_shadow_ritualofsacrifice", 40),
    "bloodmage_fleshweaver_dissipation": ("spell_shadow_dispersion", 40),
    "bloodmage_fleshweaver_crimson_scion": "spell_shadow_sealofkings",
    "bloodmage_fleshweaver_vitality_for_later": "spell_holy_sealofwisdom",
    "bloodmage_fleshweaver_sovereignty": ("spell_holy_circleofrenewal", 40),
    "bloodmage_fleshweaver_heart_rupturer": ("inv_misc_organ_02", 40),
    "bloodmage_fleshweaver_invigorated_flesh": ("spell_shadow_siphonmana", 200),
    "bloodmage_fleshweaver_fleshbending": ("spell_shadow_improvedvampiricembrace", 40),
    "bloodmage_fleshweaver_red_thirst": ("spell_shadow_demonbreath", 40),
    "bloodmage_fleshweaver_bloodcraft": ("spell_shadow_shadowbolt", 40),
    "bloodmage_fleshweaver_flesh_foundry": ("spell_shadow_corpseexplode", 40),
    # --- Sanguine: the caster
    "bloodmage_sanguine_atheranns_wickedness": ("spell_shadow_curseofmannoroth", 40),
    "bloodmage_sanguine_darkfallens_embrace": ("spell_shadow_vampiricaura", 40),
    "bloodmage_sanguine_blood_banquet": ("inv_drink_22", 40),
    "bloodmage_sanguine_cunning_of_atherann": ("spell_shadow_mindtwisting", 40),
    "bloodmage_sanguine_the_cup_runneth_over": "inv_drink_05",
    "bloodmage_sanguine_twisted_magic": ("spell_shadow_curseofachimonde", 40),
    "bloodmage_sanguine_bloodwell_eruption": ("spell_shadow_plaguecloud", 40),
    "bloodmage_sanguine_blood_parasites": ("spell_shadow_creepingplague", 40),
    "bloodmage_sanguine_lifedrinker": ("spell_shadow_lifedrain02", 40),
    "bloodmage_sanguine_enthraller": "spell_shadow_shadowworddominate",
    "bloodmage_sanguine_hematoma": ("spell_shadow_siphonmana", 40),
    "bloodmage_sanguine_dominion_of_blood": ("spell_holy_powerwordshield", 40),
    "bloodmage_sanguine_agonizing_pain": "spell_shadow_shadowwordpain",
    "bloodmage_sanguine_reckless_abandon": "spell_shadow_unstableaffliction_3",
    "bloodmage_sanguine_essence_harvester": "spell_shadow_soulleech_2",
    "bloodmage_sanguine_the_council_assembled": "spell_shadow_gathershadows",
    "bloodmage_sanguine_swarm_of_flies": "spell_shadow_carrionswarm",
    "bloodmage_sanguine_dark_presence": "spell_shadow_darkritual",
    "bloodmage_sanguine_crimson_curse": ("ability_rogue_rupture", 40),
    "bloodmage_sanguine_torture": ("spell_shadow_misery", 40),
    "bloodmage_sanguine_thirst_for_blood": ("spell_deathknight_butcher2", 40),
    "bloodmage_sanguine_blood_lord": ("spell_shadow_shadowfury", 40),
    "bloodmage_sanguine_crimson_terror": ("spell_shadow_bloodboil", 40),
})

MAPPING.update({
    # --- Bloodmage abilities. The ten at the bottom were on the generic
    # ability_melee sword, same as Barbarian's twenty.
    "bloodmage_bloodbolt": "spell_shadow_shadowbolt",
    "bloodmage_bloodmoon_blast": "spell_shadow_painspike",
    "bloodmage_blood_tap": "spell_deathknight_bloodtap",
    "bloodmage_fleshcraft": "spell_shadow_shadowmend",
    "bloodmage_blood_pact": "spell_shadow_sacrificialshield",
    "bloodmage_liquify": "spell_shadow_dispersion",
    "bloodmage_shadow_howl": "spell_shadow_demonbreath",
    "bloodmage_wicked_howl": "spell_shadow_unholyfrenzy",
    "bloodmage_hemostasis": "spell_shadow_lifedrain",
    "bloodmage_scarlet_delirium": "spell_shadow_mindtwisting",
    "bloodmage_transfusion": "spell_holy_sealofsacrifice",
    "bloodmage_blood_veil": "spell_holy_powerwordshield",
    "bloodmage_blood_rite": "spell_shadow_deathpact",
    "bloodmage_valanars_vengeance": "spell_shadow_vampiricaura",
    "bloodmage_keleseths_calamity": "spell_shadow_shadowfury",
    "bloodmage_atheranns_anguish": "spell_shadow_plaguecloud",
    "bloodmage_sanguine_rupture": "spell_shadow_corpseexplode",
    "bloodmage_taldarams_torment": "spell_shadow_curseofsargeras",
    "bloodmage_shadow_hemorrhage": "spell_shadow_lifedrain02",
    "bloodmage_malediction": "spell_shadow_curseofmannoroth",
    "bloodmage_vampiric_fang": "spell_shadow_improvedvampiricembrace",
    "bloodmage_blood_craving": "spell_deathknight_butcher2",
    "bloodmage_aneurysm": "spell_shadow_mindrot",
    "bloodmage_sacrificial_rite": "spell_shadow_ritualofsacrifice",
    "bloodmage_transgression": "spell_shadow_shadowpower",
    "bloodmage_blood_curse": "spell_shadow_blackplague",
    "bloodmage_accursed_form": "spell_shadow_twistedfaith",
    "bloodmage_veinburst": "ability_rogue_bloodsplatter",
    "bloodmage_hemoburst": "spell_shadow_bloodboil",
    "bloodmage_bloodsurge": "ability_warrior_bloodfrenzy",
    "bloodmage_final_embrace": "spell_shadow_soulleech_3",
    "bloodmage_endure_the_curse": "spell_shadow_antimagicshell",
    "bloodmage_eternal_curse": "spell_deathknight_bloodpresence",
    "bloodmage_rotclaw": "ability_creature_disease_02",
    "bloodmage_blood_howl": "ability_druid_challangingroar",
    "bloodmage_bare_fangs": "ability_druid_ferociousbite",
    "bloodmage_night_hunters_howl": "spell_shadow_ragingscream",
    "bloodmage_eternal_resolve": "ability_warrior_rampage",
    "bloodmage_monstrous_hunger": "spell_shadow_burningspirit",
    "bloodmage_hypovolemic_shock": "spell_shadow_siphonmana",
    "bloodmage_sanguine_mend": "spell_holy_blessedrecovery",
    "bloodmage_heartbreak": "inv_misc_organ_02",
    "bloodmage_hemoglobe": "spell_holy_circleofrenewal",
    "bloodmage_crimson_tide": "spell_shadow_creepingplague",
    "bloodmage_dark_liturgy": "spell_holy_prayerofhealing02",
    "bloodmage_darkfallen_lament": "spell_shadow_summonvoidwalker",
    "bloodmage_arterial_bind": "spell_shadow_impphaseshift",
    "bloodmage_purify_blood": "spell_shadow_antishadow",
    "bloodmage_hemal_excision": "spell_shadow_curseofachimonde",
    "bloodmage_sanguine_essence": "spell_shadow_soulgem",
    "bloodmage_gorge": "inv_drink_22",
    "bloodmage_vampyrs_kiss": "spell_shadow_misery",
    "bloodmage_infuse": "spell_shadow_requiem",
    "bloodmage_blood_cursed_armor": "spell_shadow_nethercloak",
    "bloodmage_bloodthorns": "spell_nature_thorns",
    # --- were on the generic sword
    "bloodmage_attack": "ability_meleedamage",
    "bloodmage_lunge": "ability_heroicleap",
    "bloodmage_reave": "ability_druid_rake",
    "bloodmage_ravenous_strike": "ability_druid_mangle2",
    "bloodmage_puncturing_fangs": ("ability_druid_ferociousbite", 40),
    "bloodmage_aortic_assault": "ability_rogue_rupture",
    "bloodmage_crimson_maw": "ability_druid_catform",
    "bloodmage_ravenous_bite": ("spell_shadow_lifedrain", 40),
    "bloodmage_bloodfang_bite": "ability_racial_cannibalize",
    "bloodmage_claw_sweep": "ability_druid_swipe",
})


# =====================================================================
# Fetch / verify / install
# =====================================================================

def real_ids():
    """Every ability_id and talent_id in the game, with its destination."""
    dest = {}
    for f in (ROOT / "data/abilities").glob("*.json"):
        for a in json.loads(f.read_text()).get("abilities", []):
            dest[a["ability_id"]] = ABILITY_DIR
    for f in (ROOT / "data/talents").glob("*.json"):
        nodes = json.loads(f.read_text()).get("nodes") or []
        if isinstance(nodes, dict):
            nodes = list(nodes.values())
        for n in nodes:
            if n.get("talent_id"):
                dest[n["talent_id"]] = TALENT_DIR
    return dest


def fetch(icon_name, hue=0):
    """Return PNG bytes for an icon, or raise with a reason.

    VERIFIES THE IMAGE, not the status code. A wrong name on this CDN can
    come back 200 with an HTML error body, which a length check or a
    status check would happily write to disk as a .png. PIL opening it is
    the only check that actually distinguishes art from an error page.
    """
    from PIL import Image
    req = urllib.request.Request(CDN.format(icon_name),
                                 headers={"User-Agent": "frontier-rpg-asset-fetch"})
    with urllib.request.urlopen(req, timeout=20) as r:
        ctype = r.headers.get("content-type", "")
        data = r.read()
    if not ctype.startswith("image/"):
        raise ValueError(f"not an image (content-type {ctype!r})")
    im = Image.open(io.BytesIO(data))
    im.load()
    if min(im.size) < 32:
        raise ValueError(f"suspiciously small: {im.size}")
    im = im.convert("RGBA")
    if hue:
        # Reuse the repo's own tint, rather than a second implementation.
        sys.path.insert(0, str(ROOT))
        from boss_icon_tint import hue_shift
        im = hue_shift(im, hue)
    out = io.BytesIO()
    im.save(out, format="PNG")
    return out.getvalue()


def main(argv):
    dry = "--dry-run" in argv
    only = argv[argv.index("--class") + 1] if "--class" in argv else None

    if "--crests" in argv:
        seen, ok, bad = {}, 0, 0
        CREST_DIR.mkdir(parents=True, exist_ok=True)
        for cls, icon in sorted(CLASS_CRESTS.items()):
            try:
                data = fetch(icon)
            except Exception as exc:                           # noqa: BLE001
                bad += 1
                print(f"    BAD  {cls:20} {icon:40} {str(exc)[:50]}")
                continue
            digest = hashlib.sha1(data).hexdigest()
            if digest in seen:
                print(f"    DUPE {cls:20} identical to {seen[digest]}")
                bad += 1
                continue
            seen[digest] = cls
            ok += 1
            if not dry:
                (CREST_DIR / f"{cls}.png").write_bytes(data)
        print(f"{ok} crest(s) resolved, {bad} problem(s)"
              f"{' (dry run, nothing written)' if dry else ''}")
        return 1 if bad else 0

    dest = real_ids()
    items = sorted(MAPPING.items())
    if only:
        items = [(k, v) for k, v in items if k.startswith(only)]
    if not items:
        print(f"nothing mapped for {only!r}" if only else "MAPPING is empty")
        return 1

    # A mapped id that is not a real id in the game data is a typo that
    # would otherwise write a file nothing ever reads.
    unknown = [k for k, _ in items if k not in dest]
    if unknown:
        print(f"{len(unknown)} mapped id(s) do not exist in the game data:")
        for u in unknown:
            print(f"    {u}")
        print()

    ok = bad = 0
    failures = []
    seen, identical = {}, []
    for ident, icon in items:
        if ident not in dest:
            continue
        name, hue = (icon if isinstance(icon, tuple) else (icon, 0))
        try:
            data = fetch(name, hue)
        except Exception as exc:                               # noqa: BLE001
            bad += 1
            failures.append((ident, name, str(exc)[:70]))
            continue
        ok += 1
        # NO TWO IDS MAY INSTALL THE SAME BYTES. This is the check that
        # stops this tool recreating the problem fix_talent_icons.py
        # exists to fix. Sharing a base icon is fine and often right;
        # installing the identical file twice is not, and a hue shift is
        # how a shared base becomes two distinct icons.
        digest = hashlib.sha1(data).hexdigest()
        if digest in seen:
            identical.append((ident, seen[digest], name, hue))
        else:
            seen[digest] = ident
        if not dry:
            dest[ident].mkdir(parents=True, exist_ok=True)
            (dest[ident] / f"{ident}.png").write_bytes(data)

    print(f"{ok} icon name(s) resolved to real art, {bad} did not"
          f"{' (dry run, nothing written)' if dry else ''}")
    if failures:
        print("\nTHESE NAMES ARE WRONG - fix the mapping, do not install them:")
        for ident, icon, why in failures:
            print(f"    {ident:48} -> {icon:40} {why}")
    if identical:
        print(f"\n{len(identical)} id(s) installed art BYTE-IDENTICAL to another id.")
        print("Give one of each pair a hue shift - MAPPING accepts")
        print('(icon_name, degrees) - or pick a different base icon:')
        for ident, other, name, hue in identical:
            print(f"    {ident:46} same as {other:46} ({name}, hue {hue})")
    return 1 if (bad or unknown or identical) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
