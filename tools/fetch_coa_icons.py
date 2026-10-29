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


MAPPING.update({
    # =================================================================
    # NECROMANCER - Scourge. Animation raises bodies, Death is plague and
    # Shadow, Rime is Kel'Thuzad's frost. Three palettes: sickly green
    # bone for Animation, rot brown-green for Death, lich blue for Rime.
    # =================================================================
    # --- Animation: raising things
    "necromancer_animation_sepulchral_might": ("spell_shadow_sacrificialshield", 40),
    "necromancer_animation_graverobber": ("inv_misc_bone_humanskull_01", 40),
    "necromancer_animation_scourge_disciple": "spell_deathknight_unholypresence",
    "necromancer_animation_runic_animation": ("spell_shadow_animatedead", 40),
    "necromancer_animation_bone_king": ("inv_misc_bone_skull_02", 40),
    "necromancer_animation_forbidden_technique": ("spell_shadow_deadofnight", 40),
    "necromancer_animation_summoning_adept": ("spell_shadow_raisedead", 40),
    "necromancer_animation_skeletal_artillery": ("ability_hunter_snipershot", 40),
    "necromancer_animation_ghoul_mastery": ("ability_racial_cannibalize", 40),
    "necromancer_animation_anti_magic_shell": ("spell_shadow_antimagicshell", 40),
    "necromancer_animation_vampiric_aura": "spell_shadow_lifedrain",
    "necromancer_animation_mindless_fury": ("spell_shadow_unholyfrenzy", 40),
    "necromancer_animation_flesh_symbiosis": ("spell_shadow_skull", 40),
    "necromancer_animation_plague_horde": "spell_shadow_creepingplague",
    "necromancer_animation_crypt_keeper": ("spell_shadow_corpseexplode", 40),
    "necromancer_animation_unrelenting": ("spell_shadow_carrionswarm", 40),
    "necromancer_animation_army_of_the_dead": ("spell_deathknight_armyofthedead", 40),
    "necromancer_animation_underking": ("inv_crown_01", 40),
    "necromancer_animation_long_march": ("spell_shadow_deathpact", 40),
    "necromancer_animation_chomp": "ability_druid_ferociousbite",
    "necromancer_animation_corpse_wagon": ("inv_misc_bone_01", 40),
    "necromancer_animation_plague_protection": ("spell_shadow_antishadow", 40),
    "necromancer_animation_master_animator": "spell_deathknight_summondeathcharger",
    # --- Death: plague and Shadow
    "necromancer_death_damnation": "spell_shadow_shadowfury",
    "necromancer_death_cycle_of_death": "spell_shadow_deathanddecay",
    "necromancer_death_dark_harvester": "spell_shadow_soulleech_3",
    "necromancer_death_rotting_flesh": ("spell_shadow_callofbone", 40),
    "necromancer_death_swarmer": ("spell_shadow_plaguecloud", 200),
    "necromancer_death_necrosis": ("ability_creature_disease_03", 40),
    "necromancer_death_unholy_runes": ("spell_shadow_demonicfortitude", 40),
    "necromancer_death_festering_decay": "ability_creature_disease_05",
    "necromancer_death_crypt_plague": ("spell_deathknight_frostfever", 40),
    "necromancer_death_plague_science": "trade_brewpoison",
    "necromancer_death_fiend": ("spell_shadow_shadowfiend", 40),
    "necromancer_death_mutation": ("spell_shadow_abominationexplosion", 40),
    "necromancer_death_expunge": "spell_shadow_blackplague",
    "necromancer_death_plague_revenant": "ability_creature_disease_01",
    "necromancer_death_apothecarys_cauldron": ("inv_potion_27", 40),
    "necromancer_death_foul_contagion": "spell_shadow_contagion",
    "necromancer_death_pandemic": ("spell_deathknight_bloodplague", 40),
    "necromancer_death_rot_fetishist": "ability_creature_poison_05",
    "necromancer_death_creeping_plagues": ("spell_shadow_plaguecloud", 40),
    "necromancer_death_touch_of_death": "spell_shadow_deathcoil",
    "necromancer_death_death_commander": "spell_shadow_shadowworddominate",
    "necromancer_death_unholy_erosion": "spell_shadow_curseofachimonde",
    "necromancer_death_waking_crypts": ("spell_shadow_deathanddecay", 40),
    # --- Rime: lich frost
    "necromancer_rime_runic_reservoir": "spell_frost_frozencore",
    "necromancer_rime_bone_legion": ("spell_frost_frostbolt02", 40),
    "necromancer_rime_hoarfrost_hands": "spell_frost_iceclaw",
    "necromancer_rime_curse_of_the_lich": ("spell_frost_chainsofice", 40),
    "necromancer_rime_piercing_icicles": ("spell_frost_iceshard", 40),
    "necromancer_rime_frigid_death": ("spell_frost_glacier", 40),
    "necromancer_rime_freeze_dry": "spell_frost_wizardmark",
    "necromancer_rime_frigid_power": "spell_frost_frostward",
    "necromancer_rime_glacier_lord": "spell_frost_icestorm",
    "necromancer_rime_frigidness": "spell_frost_frostshock",
    "necromancer_rime_arch_lich": "spell_frost_summonwaterelemental",
    "necromancer_rime_deathly_chill": ("spell_frost_iceshock", 40),
    "necromancer_rime_necrotic_chains": ("spell_frost_chainsofice", 200),
    "necromancer_rime_permafrost": "spell_frost_wisp",
    "necromancer_rime_icecrown": "inv_crown_02",
    "necromancer_rime_death_and_ice": ("spell_deathknight_icetouch", 40),
    "necromancer_rime_frozen_bodies": "spell_frost_frozenorb",
    "necromancer_rime_champion_of_kelthuzad": "spell_frost_arcticwinds",
    "necromancer_rime_blood_and_ice": "spell_deathknight_bloodpresence",
    "necromancer_rime_harrowing_winds": "spell_frost_icefloes",
    "necromancer_rime_master_lich": "spell_frost_chillingblast",
    "necromancer_rime_raising_the_kirin_tor": ("spell_frost_manarecharge", 40),
    "necromancer_rime_army_of_the_north": "spell_frost_summonwaterelemental_2",
    # --- abilities
    "necromancer_attack": "ability_meleedamage",
    "necromancer_crypt_swarm": "spell_shadow_carrionswarm",
    "necromancer_lichfrost": "spell_frost_frostbolt02",
    "necromancer_flesh_to_worms": "spell_shadow_callofbone",
    "necromancer_glacial_tap": "spell_frost_manarecharge",
    "necromancer_command_hook": "inv_misc_hook_01",
    "necromancer_corpse_explosion": "spell_shadow_corpseexplode",
    "necromancer_deaths_due": "spell_shadow_antishadow",
    "necromancer_bone_tithe": "inv_misc_bone_humanskull_01",
    "necromancer_fetid_ward": "spell_shadow_demonicfortitude",
    "necromancer_anti_magic_shell": "spell_shadow_antimagicshell",
    "necromancer_phylactery": "inv_misc_enggizmos_18",
    "necromancer_ghoulify": "ability_racial_cannibalize",
    "necromancer_mass_grave": "spell_shadow_deadofnight",
    "necromancer_unholy_frenzy": "spell_shadow_unholyfrenzy",
    "necromancer_foul_invocation": "spell_shadow_ritualofsacrifice",
    "necromancer_call_of_the_scourge": "spell_shadow_deathpact",
    "necromancer_plague_of_undeath": "spell_deathknight_bloodplague",
    "necromancer_lichplague": "spell_deathknight_frostfever",
    "necromancer_virulency": "ability_creature_disease_03",
    "necromancer_harvest_plague": "spell_shadow_lifedrain02",
    "necromancer_apothecarys_cauldron": "inv_potion_27",
    "necromancer_ice_barrage": "spell_frost_iceshard",
    "necromancer_glacial_impact": "spell_frost_glacier",
    "necromancer_command_bonefreeze": "spell_frost_chainsofice",
    "necromancer_heartchill": "spell_frost_iceshock",
    "necromancer_lich_form": "spell_shadow_skull",
    "necromancer_chilling_presence": "spell_deathknight_icetouch",
    "necromancer_animate_frost_wyrm": "inv_misc_head_dragon_blue",
    "necromancer_raise_ghoul": "spell_shadow_raisedead",
    "necromancer_raise_skeletal_mage": "spell_shadow_animatedead",
    "necromancer_raise_banshee": "spell_shadow_shadowfiend",
    "necromancer_raise_abomination": "spell_shadow_abominationexplosion",
    "necromancer_animate_skeletal_archers": "ability_hunter_snipershot",
    "necromancer_animate_plaguefather": "spell_shadow_plaguecloud",
    "necromancer_animate_bone_wraith": "inv_misc_bone_skull_02",
    "necromancer_animate_tomb_king": "inv_crown_01",
    "necromancer_march_of_the_dead": "spell_deathknight_armyofthedead",
    "necromancer_sacrifice_undead": "spell_shadow_sacrificialshield",
    "necromancer_corpse_wagon": "inv_misc_bone_01",
})


MAPPING.update({
    # =================================================================
    # CHRONOMANCER - bronze/Infinite dragonflight. Artificer is wands and
    # devices, Infinite is Arcane destruction, Time is the healer. Bronze
    # and gold for Artificer, violet-black Arcane for Infinite, pale gold
    # for Time, so the three trees are not one wall of purple sparkles.
    # =================================================================
    "chronomancer_artificer_artificers_empowerment": "spell_holy_spiritualguidence",
    "chronomancer_artificer_wand_master": ("inv_wand_07", 40),
    "chronomancer_artificer_discovery": "inv_misc_enggizmos_20",
    "chronomancer_artificer_concentrated_fate": ("spell_arcane_arcanetorrent", 40),
    "chronomancer_artificer_artificers_wand": ("inv_wand_11", 40),
    "chronomancer_artificer_wand_expert": "inv_wand_04",
    "chronomancer_artificer_bronze_echoes": ("spell_holy_borrowedtime", 40),
    "chronomancer_artificer_caverns_of_time": "spell_arcane_portaltheramore",
    "chronomancer_artificer_singularity_core": ("spell_arcane_arcane01", 40),
    "chronomancer_artificer_shatter_echo": ("spell_arcane_blast", 40),
    "chronomancer_artificer_elder_wand": "inv_wand_1h_stratholme_d_01",
    "chronomancer_artificer_crystal_cannon": ("inv_misc_gem_crystal_02", 40),
    "chronomancer_artificer_flux_emitter": ("spell_arcane_arcane03", 40),
    "chronomancer_artificer_hyperwand": "inv_wand_08",
    "chronomancer_artificer_infinity_stone": "inv_misc_gem_diamond_03",
    "chronomancer_artificer_splitting_time": ("spell_arcane_arcane04", 40),
    "chronomancer_artificer_paradox_cannon": ("inv_gizmo_pipe_01", 40),
    "chronomancer_artificer_conduction_burst": ("spell_arcane_arcanetactics", 40),
    "chronomancer_artificer_reverse_engineering": "trade_engineering",
    "chronomancer_artificer_intuition": "spell_holy_mindsooth",
    "chronomancer_artificer_time_is_a_circle": ("spell_nature_timestop", 200),
    "chronomancer_artificer_magic_sensitivity": ("spell_arcane_studentofmagic", 40),
    "chronomancer_artificer_pulse_driver": ("spell_arcane_arcaneresilience", 40),
    # --- Infinite: arcane destruction
    "chronomancer_infinite_warpstriker": ("spell_arcane_blink", 40),
    "chronomancer_infinite_deconstruction": ("spell_arcane_massdispel", 40),
    "chronomancer_infinite_rippling_power": "spell_holy_divinespirit",
    "chronomancer_infinite_impeccable_timing": ("spell_shadow_mindbomb", 40),
    "chronomancer_infinite_anomaly_spikes": ("spell_arcane_starfire", 40),
    "chronomancer_infinite_mind_melt": "spell_shadow_mindsteal",
    "chronomancer_infinite_gift_of_the_infinite_dragonflight": "inv_misc_head_dragon_bronze",
    "chronomancer_infinite_distorted_time": ("spell_arcane_mindmastery", 40),
    "chronomancer_infinite_hourglass_of_eternity": ("inv_misc_pocketwatch_02", 40),
    "chronomancer_infinite_magic_erosion": "spell_arcane_manatap",
    "chronomancer_infinite_crown_of_power": "inv_crown_02",
    "chronomancer_infinite_shifting_chaos": ("spell_shadow_seedofdestruction", 40),
    "chronomancer_infinite_black_hole": ("spell_arcane_focusedpower", 40),
    "chronomancer_infinite_destabilize_time": ("spell_frost_stun", 40),
    "chronomancer_infinite_infinite_power": ("spell_arcane_arcanepotency", 40),
    "chronomancer_infinite_timelost_power": "spell_arcane_invocation",
    "chronomancer_infinite_incarnation_of_chaos": ("spell_shadow_demonform", 40),
    "chronomancer_infinite_infinity_crash": ("spell_arcane_prismaticcloak", 40),
    "chronomancer_infinite_time_means_nothing": ("spell_nature_wispsplode", 40),
    "chronomancer_infinite_chaotic_time": "spell_shadow_sealofkings",
    "chronomancer_infinite_aeon_rend": "spell_arcane_arcane02",
    "chronomancer_infinite_null_orbs": "inv_misc_orb_01",
    "chronomancer_infinite_infinite_keeper": ("spell_arcane_arcaneresilience", 200),
    # --- Time: the healer
    "chronomancer_time_time_wizard": "spell_holy_magicalsentry",
    "chronomancer_time_sands_of_life": "inv_misc_dust_02",
    "chronomancer_time_keep_accelerating": ("spell_holy_blessedrecovery", 40),
    "chronomancer_time_endless_sands": "inv_misc_dust_04",
    "chronomancer_time_aeon_of_protection": ("spell_holy_devotionaura", 40),
    "chronomancer_time_carbon_dating": ("spell_nature_timestop", 40),
    "chronomancer_time_through_the_aeons": ("spell_magic_managain", 40),
    "chronomancer_time_timeless": ("spell_holy_borrowedtime", 200),
    "chronomancer_time_aeon_of_renewal": ("spell_holy_renew", 40),
    "chronomancer_time_shimmering_shard": "inv_enchant_shardbrilliantlarge",
    "chronomancer_time_wonders_of_time": "spell_holy_mindvision",
    "chronomancer_time_cadence_of_time": "spell_frost_wizardmark",
    "chronomancer_time_aeon_of_oblivion": ("spell_holy_restoration", 40),
    "chronomancer_time_fabric_of_time": ("spell_holy_flashheal", 40),
    "chronomancer_time_mark_of_order": ("spell_holy_sealofprotection", 200),
    "chronomancer_time_timeline_tether": "spell_holy_searinglightpriest",
    "chronomancer_time_orderly_protector": ("spell_holy_powerwordshield", 40),
    "chronomancer_time_overcorrection": ("spell_holy_prayerofhealing", 40),
    "chronomancer_time_time_skip": ("spell_nature_slowingtotem", 40),
    "chronomancer_time_shield_of_the_ages": ("spell_holy_sealofsalvation", 40),
    "chronomancer_time_converge_the_infinite": ("spell_holy_divineprovidence", 40),
    "chronomancer_time_epic_recovery": ("spell_holy_layonhands", 40),
    "chronomancer_time_the_vast_infinite": "spell_holy_divineillumination",
    # --- abilities
    "chronomancer_attack": "ability_meleedamage",
    "chronomancer_unmake": "spell_arcane_blast",
    "chronomancer_wand_of_time": "inv_wand_07",
    "chronomancer_reverse_wound": "spell_holy_heal",
    "chronomancer_decomposition": "spell_shadow_manaburn",
    "chronomancer_accelerated_recovery": "spell_holy_renew",
    "chronomancer_chronostasis": "spell_frost_stun",
    "chronomancer_roll_back": "spell_arcane_massdispel",
    "chronomancer_discordance": "spell_arcane_arcanetorrent",
    "chronomancer_waves_of_time": "spell_arcane_arcane03",
    "chronomancer_time_out": "spell_nature_timestop",
    "chronomancer_clasp_of_infinity": "spell_frost_chainsofice",
    "chronomancer_babify": "spell_magic_polymorphchicken",
    "chronomancer_fortify_timeline": ("spell_holy_sealofprotection", 40),
    "chronomancer_timeguard": "spell_holy_devotionaura",
    "chronomancer_hasten": "spell_nature_bloodlust",
    "chronomancer_temporal_focus": "spell_arcane_arcanepotency",
    "chronomancer_temporal_anomaly": "inv_misc_orb_04",
    "chronomancer_infinite_shield": "spell_holy_powerwordshield",
    "chronomancer_gravity_bomb": "spell_arcane_focusedpower",
    "chronomancer_chromatic_shard": "inv_misc_gem_crystal_02",
    "chronomancer_melt_reality": "spell_shadow_seedofdestruction",
    "chronomancer_timerend": "spell_arcane_starfire",
    "chronomancer_anomaly_spike": "spell_arcane_arcane01",
    "chronomancer_destabilize_time": "spell_nature_slowingtotem",
    "chronomancer_slipstream": "spell_arcane_blink",
    "chronomancer_infinite_horizon": "spell_arcane_mindmastery",
    "chronomancer_incarnation_of_chaos": "spell_shadow_demonform",
    "chronomancer_epoch": "spell_holy_restoration",
    "chronomancer_correct_the_mistake": "spell_holy_divineprovidence",
    "chronomancer_ripple": "spell_holy_prayerofhealing",
    "chronomancer_aeon_of_resilience": "spell_holy_sealofsalvation",
    "chronomancer_aeon_of_protection": "spell_holy_sealofprotection",
    "chronomancer_aeon_of_renewal": "spell_holy_blessedrecovery",
    "chronomancer_aeon_of_oblivion": "spell_holy_layonhands",
    "chronomancer_fabric_of_time": "spell_holy_flashheal",
    "chronomancer_buy_time": "spell_holy_borrowedtime",
    "chronomancer_continuum_restoration": "spell_holy_dispelmagic",
    "chronomancer_displacement": "spell_arcane_prismaticcloak",
    "chronomancer_artificers_wand": "inv_wand_11",
    "chronomancer_crystal_cannon": "inv_gizmo_pipe_01",
    "chronomancer_shatter_echo": "spell_arcane_arcane04",
    "chronomancer_singularity_core": "spell_arcane_arcanetactics",
    "chronomancer_flux_emitter": "spell_arcane_studentofmagic",
    "chronomancer_paradox_cannon": "spell_magic_managain",
    "chronomancer_aether_compression": "spell_arcane_arcaneresilience",
    "chronomancer_arc_collision": "spell_nature_wispsplode",
    "chronomancer_unstable_chronoglass": "inv_misc_pocketwatch_02",
    "chronomancer_collapse": "spell_shadow_mindbomb",
})


MAPPING.update({
    # =================================================================
    # FELSWORN - Illidari. Infernal is fel spellcasting (Gul'dan, Sargeras,
    # Archimonde), Slayer is twin warglaives, Tyrant is the demon tank.
    # Fel green throughout, so the trees separate by subject: spell effects
    # for Infernal, blades for Slayer, hide and horns for Tyrant.
    # =================================================================
    "felsworn_infernal_wrath_of_sargeras": "spell_shadow_shadowfury",
    "felsworn_infernal_fel_cannon": "spell_fire_felflamering",
    "felsworn_infernal_guldans_prodigy": "spell_fire_soulburn",
    "felsworn_infernal_hidden_power": "spell_shadow_demoniccirclesummon",
    "felsworn_infernal_illidari_smiter": "ability_warlock_improvedsoulleech",
    "felsworn_infernal_cursed_flames": ("spell_fire_burningspeed", 40),
    "felsworn_infernal_felfire_adept": ("spell_fire_felimmolation", 40),
    "felsworn_infernal_nether_spirit": ("spell_shadow_demonicempathy", 40),
    "felsworn_infernal_black_magic": ("spell_shadow_chilltouch", 40),
    "felsworn_infernal_curse_of_argus": ("spell_shadow_curseofmannoroth", 40),
    "felsworn_infernal_doomsayer": ("spell_shadow_auraofdarkness", 40),
    "felsworn_infernal_fel_infusion": ("spell_fire_fireball", 40),
    "felsworn_infernal_illidari_magi": "spell_shadow_demonictactics",
    "felsworn_infernal_withering": ("spell_shadow_shadowwordpain", 40),
    "felsworn_infernal_archimondes_wrath": "spell_shadow_demonbreath",
    "felsworn_infernal_reckoning": ("spell_fire_selfdestruct", 40),
    "felsworn_infernal_infernal_summoner": ("spell_shadow_summoninfernal", 40),
    "felsworn_infernal_herald_of_the_legion": ("spell_shadow_demonform", 40),
    "felsworn_infernal_dark_magician": ("spell_shadow_lifedrain02", 40),
    "felsworn_infernal_manari_teachings": "inv_misc_book_07",
    "felsworn_infernal_oppressive_ruin": ("spell_shadow_rainoffire", 40),
    "felsworn_infernal_unphased": "spell_shadow_impphaseshift",
    "felsworn_infernal_malice_of_guldan": ("spell_fire_incinerate", 40),
    # --- Slayer: warglaives
    "felsworn_slayer_azzinoths_rage": "ability_warrior_innerrage",
    "felsworn_slayer_slice_and_dice": ("ability_rogue_slicedice", 40),
    "felsworn_slayer_spite": "ability_rogue_quickrecovery",
    "felsworn_slayer_chaos_soldier": "ability_criticalstrike",
    "felsworn_slayer_twin_fury": "ability_rogue_dualweild",
    "felsworn_slayer_dancing_blades": ("ability_warrior_bladestorm", 40),
    "felsworn_slayer_unbound": "ability_rogue_fleetfooted",
    "felsworn_slayer_true_self": ("spell_shadow_demonicempathy", 200),
    "felsworn_slayer_fel_blades": ("inv_weapon_glave_01", 40),
    "felsworn_slayer_a_thousand_cuts": "ability_rogue_fanofknives",
    "felsworn_slayer_fel_instincts": "ability_druid_predatoryinstincts",
    "felsworn_slayer_you_cheat_guldan": ("ability_rogue_unfairadvantage", 40),
    "felsworn_slayer_reckless_assault": ("ability_warrior_punishingblow", 40),
    "felsworn_slayer_legionfall": ("spell_fire_felflamebolt", 40),
    "felsworn_slayer_consumed_by_fel": ("spell_fire_felimmolation", 200),
    "felsworn_slayer_blighted_strikes": ("ability_warrior_savageblow", 40),
    "felsworn_slayer_felguard": "spell_shadow_summonfelguard",
    "felsworn_slayer_perpetual_fury": ("ability_warrior_endlessrage", 40),
    "felsworn_slayer_nether_champion": "ability_warrior_challange",
    "felsworn_slayer_scars_of_suffering": "ability_warrior_bloodbath",
    "felsworn_slayer_whirling_vengeance": "ability_whirlwind",
    "felsworn_slayer_oblivion": "spell_shadow_demonicfortitude",
    "felsworn_slayer_pit_lords_rage": "spell_shadow_summonfelhunter",
    # --- Tyrant: the demon tank
    "felsworn_tyrant_nether_disciple": "ability_parry",
    "felsworn_tyrant_demon_hide": "inv_misc_monsterscales_15",
    "felsworn_tyrant_burning_legionnaire": ("spell_fire_bluefire", 40),
    "felsworn_tyrant_infernal_constitution": "spell_nature_unyeildingstamina",
    "felsworn_tyrant_hulking_demon": "ability_warrior_strengthofarms",
    "felsworn_tyrant_pure_hatred": ("spell_shadow_bloodboil", 40),
    "felsworn_tyrant_dark_lord": ("spell_shadow_shadesofdarkness", 40),
    "felsworn_tyrant_felblade": "inv_sword_61",
    "felsworn_tyrant_illidari_training": ("ability_warrior_defensivestance", 40),
    "felsworn_tyrant_unholy_endurance": "ability_warrior_shieldguard",
    "felsworn_tyrant_vengeance": "ability_warrior_revenge",
    "felsworn_tyrant_burning_commander": "ability_warrior_battleshout",
    "felsworn_tyrant_demonic_fortitude": ("spell_shadow_demonicfortitude", 40),
    "felsworn_tyrant_straight_to_the_nether": "spell_shadow_siphonmana",
    "felsworn_tyrant_expose": "ability_warrior_riposte",
    "felsworn_tyrant_betrayer": "spell_shadow_antishadow",
    "felsworn_tyrant_bulwark_of_azzinoth": "inv_shield_32",
    "felsworn_tyrant_grommashs_folly": "ability_warrior_rampage",
    "felsworn_tyrant_abyssal_conditioning": "spell_shadow_sealofkings",
    "felsworn_tyrant_fel_monstrosity": "spell_shadow_summonvoidwalker",
    "felsworn_tyrant_mannoroths_rage": "spell_shadow_unholyfrenzy",
    "felsworn_tyrant_taskmasters_army": ("ability_warrior_warcry", 40),
    "felsworn_tyrant_vengeance_is_mine": "spell_shadow_deathpact",
    # --- abilities
    "felsworn_attack": "ability_meleedamage",
    "felsworn_twin_slice": "ability_rogue_slicedice",
    "felsworn_fel_fireball": "spell_fire_felfirenova",
    "felsworn_sargeron_smite": "spell_shadow_chilltouch",
    "felsworn_sunder": "ability_warrior_sunder",
    "felsworn_chaos_rush": "ability_heroicleap",
    "felsworn_inner_demon": "spell_shadow_demonform",
    "felsworn_hateforged_barrier": "spell_shadow_antimagicshell",
    "felsworn_cripple": "spell_shadow_curseofachimonde",
    "felsworn_consume_magic": "spell_nature_abolishmagic",
    "felsworn_felbreak": "spell_fire_felflamebolt",
    "felsworn_manaburn": "spell_shadow_manaburn",
    "felsworn_whispers_of_the_pit": "spell_shadow_mindsteal",
    "felsworn_annihilation": "spell_fire_selfdestruct",
    "felsworn_skull_of_guldan": "inv_misc_bone_humanskull_01",
    "felsworn_illidans_guile": "ability_rogue_unfairadvantage",
    "felsworn_azzinoths_assault": "inv_weapon_glave_01",
    "felsworn_annihilan_strike": "ability_warrior_punishingblow",
    "felsworn_glaiving": "inv_sword_72",
    "felsworn_felhoof_charge": "ability_warrior_charge",
    "felsworn_immolation_aura": "spell_fire_felimmolation",
    "felsworn_fury_unleashed": "ability_warrior_endlessrage",
    "felsworn_fury_of_the_illidari": "ability_warrior_bladestorm",
    "felsworn_bane_of_frailty": "spell_shadow_curseofmannoroth",
    "felsworn_blood_of_mannoroth": "spell_shadow_bloodboil",
    "felsworn_ruin": "spell_shadow_rainoffire",
    "felsworn_felwrath": "spell_fire_incinerate",
    "felsworn_bane_of_chaos": "spell_shadow_shadowwordpain",
    "felsworn_felstrike": "spell_fire_burningspeed",
    "felsworn_sargeras_embrace": "spell_shadow_auraofdarkness",
    "felsworn_infernal": "spell_shadow_summoninfernal",
    "felsworn_manafeed": "spell_shadow_lifedrain02",
    "felsworn_fel_infusion": "spell_fire_fireball",
    "felsworn_felrend": "ability_warrior_savageblow",
    "felsworn_carve": "ability_warrior_cleave",
    "felsworn_demonic_will": "spell_shadow_demonicempathy",
    "felsworn_burning_hatred": "spell_fire_bluefire",
    "felsworn_tyrannical_resolve": "ability_warrior_defensivestance",
    "felsworn_tyrants_gaze": "spell_shadow_evileye",
    "felsworn_eye_of_the_tyrant": "spell_shadow_demonicpact",
    "felsworn_infernal_whipcrack": "ability_warrior_warcry",
    "felsworn_doomscarring": "spell_shadow_shadesofdarkness",
    "felsworn_fel_bargain": "spell_shadow_sacrificialshield",
})


MAPPING.update({
    # =================================================================
    # GUARDIAN - a Roman/gladiator banner-and-shield class. Gladiator is
    # arena one-hand-and-shield, Inspiration is warhorns and ballads (the
    # party-buff tree), Vanguard is the shield wall. Steel and blue for
    # Vanguard, arena bronze for Gladiator, banners and horns for
    # Inspiration.
    # =================================================================
    "guardian_gladiator_might": "ability_warrior_strengthofarms",
    "guardian_gladiator_built_different": "ability_racial_bloodrage",
    "guardian_gladiator_sword_training": "inv_sword_04",
    "guardian_gladiator_legionnaire": "ability_criticalstrike",
    "guardian_gladiator_shield_training": ("ability_defend", 40),
    "guardian_gladiator_tactical_combat": "ability_warrior_shieldmastery",
    "guardian_gladiator_waste_no_movement": "ability_rogue_quickrecovery",
    "guardian_gladiator_upper_hand": "ability_warrior_punishingblow",
    "guardian_gladiator_crashing_force": ("ability_warrior_revenge", 40),
    "guardian_gladiator_myrmidon": ("ability_warrior_shieldbash", 40),
    "guardian_gladiator_double_duty": "ability_dualwield",
    "guardian_gladiator_retiarius": ("inv_misc_net_01", 40),
    "guardian_gladiator_experienced_combatant": "ability_warrior_endlessrage",
    "guardian_gladiator_deadly_blow": ("ability_warrior_savageblow", 40),
    "guardian_gladiator_champion": "ability_warrior_challange",
    "guardian_gladiator_bulwark_rush": "ability_warrior_shieldcharge",
    "guardian_gladiator_shield_combat": "inv_shield_09",
    "guardian_gladiator_clinch_brawler": "inv_gauntlets_04",
    "guardian_gladiator_momentum": ("ability_warrior_bullrush", 40),
    "guardian_gladiator_favor": ("spell_holy_championsbond", 200),
    "guardian_gladiator_one_handed_mastery": "inv_sword_20",
    "guardian_gladiator_calculated_strike": ("ability_warrior_decisivestrike", 40),
    "guardian_gladiator_heroism": ("ability_warrior_rallyingcry", 40),
    # --- Inspiration: banners and ballads
    "guardian_inspiration_leading_the_march": ("ability_warrior_warcry", 40),
    "guardian_inspiration_a_heros_tale": "inv_misc_book_11",
    "guardian_inspiration_dragonslayer": "inv_misc_head_dragon_01",
    "guardian_inspiration_battle_bard": ("inv_misc_drum_01", 40),
    "guardian_inspiration_strength_in_unison": ("spell_holy_prayerofspirit", 40),
    "guardian_inspiration_powerful_voice": ("spell_holy_silence", 40),
    "guardian_inspiration_minstrel": "inv_misc_horn_01",
    "guardian_inspiration_soundwave": ("spell_nature_thunderclap", 40),
    "guardian_inspiration_veteran_of_the_third_war": ("spell_holy_blessedrecovery", 40),
    "guardian_inspiration_spirit_of_battle": ("spell_holy_mindsooth", 40),
    "guardian_inspiration_wars_muse": ("spell_holy_championsgrace", 40),
    "guardian_inspiration_into_the_fray": ("ability_warrior_innerrage", 40),
    "guardian_inspiration_stand_your_ground": "ability_warrior_defensivestance",
    "guardian_inspiration_you_shall_not_fall": "spell_holy_sealofprotection",
    "guardian_inspiration_knights_song": ("spell_holy_devotionaura", 40),
    "guardian_inspiration_fearless": ("ability_warrior_shieldwall", 40),
    "guardian_inspiration_song_of_steel": ("inv_misc_horn_02", 40),
    "guardian_inspiration_dissonance": ("spell_holy_silence", 200),
    "guardian_inspiration_banner_of_conquest": ("inv_banner_02", 40),
    "guardian_inspiration_inspiring_presence": ("spell_holy_auramastery", 40),
    "guardian_inspiration_champions_presence": ("spell_holy_championsbond", 40),
    "guardian_inspiration_bards_manuscript": "inv_scroll_03",
    "guardian_inspiration_field_commander": ("ability_warrior_battleshout", 40),
    # --- Vanguard: the shield wall
    "guardian_vanguard_iron_guardian": "spell_nature_unyeildingstamina",
    "guardian_vanguard_heavy_expert": "ability_parry",
    "guardian_vanguard_footmans_call": ("ability_warrior_shieldbash", 200),
    "guardian_vanguard_with_honor": ("spell_holy_sealofvengeance", 40),
    "guardian_vanguard_knights_conviction": ("ability_warrior_shieldmastery", 40),
    "guardian_vanguard_seasoned_fighter": "ability_warrior_sunder",
    "guardian_vanguard_stalwart": "inv_shield_06",
    "guardian_vanguard_valiant_defender": ("ability_defend", 200),
    "guardian_vanguard_bulwark": ("inv_shield_32", 40),
    "guardian_vanguard_retaliation": ("ability_warrior_revenge", 200),
    "guardian_vanguard_vanguards_shield": "spell_shadow_antimagicshell",
    "guardian_vanguard_bring_down_the_hammer": ("inv_hammer_16", 40),
    "guardian_vanguard_iron_barrier": ("ability_warrior_shieldguard", 40),
    "guardian_vanguard_forceful_impact": ("ability_warrior_shieldcharge", 40),
    "guardian_vanguard_vanguards_might": ("spell_holy_devotionaura", 200),
    "guardian_vanguard_resilient": "spell_holy_devotion",
    "guardian_vanguard_footmans_calling": ("ability_warrior_defensivestance", 40),
    "guardian_vanguard_experienced_soldier": ("ability_warrior_challange", 40),
    "guardian_vanguard_the_green_tower": ("inv_shield_05", 40),
    "guardian_vanguard_hold_the_line": ("ability_warrior_shieldwall", 200),
    "guardian_vanguard_high_guard": "ability_warrior_shieldreflection",
    "guardian_vanguard_shield_unit": ("inv_shield_04", 40),
    "guardian_vanguard_kings_guard": ("ability_warrior_shieldbreak", 40),
    # --- abilities
    "guardian_attack": "ability_meleedamage",
    "guardian_heavy_blow": "inv_hammer_16",
    "guardian_ram": "ability_warrior_shieldbash",
    "guardian_pulverize": "ability_warrior_savageblow",
    "guardian_advance": "ability_warrior_bullrush",
    "guardian_brace": "ability_defend",
    "guardian_raise_shield": "ability_warrior_shieldguard",
    "guardian_bastion": "inv_shield_32",
    "guardian_tower_formation": "inv_shield_05",
    "guardian_line_formation": "inv_shield_04",
    "guardian_challenging_cry": "ability_golemthunderclap",
    "guardian_shield_challenge": "ability_warrior_shieldbreak",
    "guardian_hammer_of_kings": "inv_hammer_20",
    "guardian_hammer_of_the_law": "spell_holy_sealofmight",
    "guardian_lionheart": "spell_holy_blessedrecovery",
    "guardian_final_verdict": "spell_holy_sealofvengeance",
    "guardian_knights_calling": "spell_holy_championsbond",
    "guardian_broad_sweep": "ability_warrior_cleave",
    "guardian_ballad_of_steel": "inv_misc_horn_02",
    "guardian_song_of_steel": "spell_holy_auramastery",
    "guardian_song_of_battle": "inv_misc_drum_01",
    "guardian_inspiring_presence": "spell_holy_prayerofspirit",
    "guardian_standard_of_valiance": "inv_banner_02",
    "guardian_cavalry_charge": "ability_warrior_charge",
    "guardian_champions_presence": "spell_holy_championsgrace",
    "guardian_liberation": "spell_holy_sealofsalvation",
    "guardian_harrowing_melody": "spell_shadow_mindsteal",
    "guardian_heros_march": "ability_warrior_warcry",
    "guardian_voice_of_an_angel": "spell_holy_silence",
    "guardian_soldiers_decree": "ability_warrior_battleshout",
    "guardian_spellcasters_decree": "spell_holy_mindsooth",
    "guardian_heros_decree": "spell_holy_devotionaura",
    "guardian_sound_of_war": "spell_nature_thunderclap",
    "guardian_battle_rush": "ability_heroicleap",
    "guardian_spear_throw": "inv_spear_02",
    "guardian_net_throw": "inv_misc_net_01",
    "guardian_reprisal": "ability_warrior_revenge",
    "guardian_centurion_strike": "ability_warrior_decisivestrike",
    "guardian_glorious_arena": "ability_warrior_rallyingcry",
    "guardian_heroism": "ability_warrior_innerrage",
    "guardian_fearless": "ability_warrior_shieldwall",
})


MAPPING.update({
    # =================================================================
    # KNIGHT OF XOROTH - a hell knight. Defiance is the shield tank,
    # Hellfire is Shadowflame casting, War is the butcher. Dull iron and
    # orange hellfire for Defiance, shadowflame violet-orange for Hellfire,
    # blood and cleavers for War.
    # =================================================================
    "knight_of_xoroth_defiance_hellsmelted_armor": "inv_shield_09",
    "knight_of_xoroth_defiance_demonfire_plating": "inv_chest_plate04",
    "knight_of_xoroth_defiance_a_gift_from_hell": ("spell_fire_bluefire", 40),
    "knight_of_xoroth_defiance_hellfire_forgemaster": "ability_warrior_shieldmastery",
    "knight_of_xoroth_defiance_shieldgore": ("ability_warrior_shieldbreak", 40),
    "knight_of_xoroth_defiance_imp_guards": ("spell_shadow_summonimp", 40),
    "knight_of_xoroth_defiance_imp_aura": "spell_shadow_impphaseshift",
    "knight_of_xoroth_defiance_xorothian_finesse": "ability_parry",
    "knight_of_xoroth_defiance_hellfire_resolve": "ability_defend",
    "knight_of_xoroth_defiance_demonfire_retaliation": "ability_warrior_revenge",
    "knight_of_xoroth_defiance_forgefiends_bulwark": ("inv_shield_32", 40),
    "knight_of_xoroth_defiance_black_skull_shield": "inv_misc_bone_skull_02",
    "knight_of_xoroth_defiance_demonic_bulwark": "ability_warrior_shieldguard",
    "knight_of_xoroth_defiance_infernal_bulwark": ("spell_shadow_deathpact", 40),
    "knight_of_xoroth_defiance_brimstone_buckler": "inv_shield_06",
    "knight_of_xoroth_defiance_hellfire_sieger": ("spell_fire_selfdestruct", 40),
    "knight_of_xoroth_defiance_demolisher": "ability_golemthunderclap",
    "knight_of_xoroth_defiance_soul_furnace": ("spell_fire_sealoffire", 40),
    "knight_of_xoroth_defiance_warden_of_hellfire": "spell_fire_masterofelements",
    "knight_of_xoroth_defiance_imp_gang_boss": ("spell_shadow_summonfelguard", 40),
    "knight_of_xoroth_defiance_hellwrath": "spell_shadow_antimagicshell",
    "knight_of_xoroth_defiance_fiery_retribution": "spell_fire_felimmolation",
    "knight_of_xoroth_defiance_call_hellfire_abyssal": ("spell_shadow_summoninfernal", 40),
    # --- Hellfire: shadowflame
    "knight_of_xoroth_hellfire_combusting_blade": "spell_fire_fireball",
    "knight_of_xoroth_hellfire_invasion": "spell_fire_flameshock",
    "knight_of_xoroth_hellfire_flamewrath": ("spell_fire_flamebolt", 40),
    "knight_of_xoroth_hellfire_infernal_pursuit": "spell_fire_burningspeed",
    "knight_of_xoroth_hellfire_hellmaw": ("spell_shadow_shadowfury", 40),
    "knight_of_xoroth_hellfire_burning_power": ("spell_fire_meteorstorm", 40),
    "knight_of_xoroth_hellfire_to_ashes": "spell_fire_incinerate",
    "knight_of_xoroth_hellfire_hellfire_embers": "spell_fire_elementaldevastation",
    "knight_of_xoroth_hellfire_cinderblade": ("spell_fire_searingtotem", 40),
    "knight_of_xoroth_hellfire_shadowflame_forge": ("spell_shadow_chilltouch", 40),
    "knight_of_xoroth_hellfire_seething_strikes": ("ability_warrior_savageblow", 40),
    "knight_of_xoroth_hellfire_infernal_steel": ("spell_fire_moltenblood", 40),
    "knight_of_xoroth_hellfire_brimstone_flames": "spell_fire_felflamebolt",
    "knight_of_xoroth_hellfire_brimstone_splinters": ("spell_fire_flameblades", 40),
    "knight_of_xoroth_hellfire_infernal_pummeling": ("spell_fire_fireball02", 40),
    "knight_of_xoroth_hellfire_inferno_blast": "spell_fire_soulburn",
    "knight_of_xoroth_hellfire_rain_of_chaos": "spell_shadow_rainoffire",
    "knight_of_xoroth_hellfire_partners_in_flames": "spell_shadow_summonfelhunter",
    "knight_of_xoroth_hellfire_doom": ("spell_shadow_auraofdarkness", 40),
    "knight_of_xoroth_hellfire_into_the_maw": ("spell_fire_felfirenova", 40),
    "knight_of_xoroth_hellfire_hellbringer": ("spell_fire_lavaspawn", 40),
    "knight_of_xoroth_hellfire_punisher": "spell_fire_playingwithfire",
    "knight_of_xoroth_hellfire_hellfire_form": ("spell_shadow_demonform", 40),
    # --- War: the butcher
    "knight_of_xoroth_war_mutilation": "ability_rogue_disembowel",
    "knight_of_xoroth_war_hellfire_striker": "ability_criticalstrike",
    "knight_of_xoroth_war_xorothian_strength": "ability_warrior_strengthofarms",
    "knight_of_xoroth_war_war_pig": "ability_hunter_pet_boar",
    "knight_of_xoroth_war_gore": ("ability_gouge", 40),
    "knight_of_xoroth_war_jagged_edge": "ability_rogue_rupture",
    "knight_of_xoroth_war_consuming_blade": "spell_shadow_lifedrain",
    "knight_of_xoroth_war_demonic_frenzy": "spell_shadow_unholyfrenzy",
    "knight_of_xoroth_war_gored": ("ability_warrior_bullrush", 40),
    "knight_of_xoroth_war_murderous_might": ("inv_sword_48", 40),
    "knight_of_xoroth_war_chop_shop": "inv_axe_09",
    "knight_of_xoroth_war_absolutism": "ability_warrior_sunder",
    "knight_of_xoroth_war_hellsmelted": ("spell_fire_flameblades", 200),
    "knight_of_xoroth_war_knight_of_pestilence": ("spell_shadow_plaguecloud", 40),
    "knight_of_xoroth_war_hand_of_doom": "spell_shadow_demonictactics",
    "knight_of_xoroth_war_bringer_of_destruction": "ability_warrior_bloodbath",
    "knight_of_xoroth_war_the_butcher": ("inv_axe_17", 40),
    "knight_of_xoroth_war_conquerors_will": "ability_warrior_challange",
    "knight_of_xoroth_war_screamin_demon": "spell_shadow_ragingscream",
    "knight_of_xoroth_war_render": "ability_warrior_trauma",
    "knight_of_xoroth_war_gorged": "ability_racial_cannibalize",
    "knight_of_xoroth_war_hellknight": "ability_warrior_rampage",
    "knight_of_xoroth_war_brimstone_bludgeon": ("inv_mace_18", 40),
    # --- abilities
    "knight_of_xoroth_attack": "ability_meleedamage",
    "knight_of_xoroth_infernal_strike": "ability_warrior_decisivestrike",
    "knight_of_xoroth_sever": "ability_warrior_savageblow",
    "knight_of_xoroth_meatsaw": "inv_axe_17",
    "knight_of_xoroth_skulltaker": "inv_sword_48",
    "knight_of_xoroth_suffuse": "spell_fire_sealoffire",
    "knight_of_xoroth_melt": "spell_fire_moltenblood",
    "knight_of_xoroth_flames_of_xoroth": "spell_fire_fireball02",
    "knight_of_xoroth_flesh_hook": "inv_misc_hook_01",
    "knight_of_xoroth_chainwhip": "ability_hunter_snipershot",
    "knight_of_xoroth_chains_of_malice": "spell_shadow_chilltouch",
    "knight_of_xoroth_dread": "spell_shadow_auraofdarkness",
    "knight_of_xoroth_black_shield": "inv_shield_32",
    "knight_of_xoroth_demon_heart": "inv_misc_organ_04",
    "knight_of_xoroth_burning_rage": "spell_fire_bluefire",
    "knight_of_xoroth_juggernaut": "ability_warrior_bullrush",
    "knight_of_xoroth_unleash_pestilence": "spell_shadow_plaguecloud",
    "knight_of_xoroth_pestilence_of_death": "spell_shadow_deathpact",
    "knight_of_xoroth_pestilence_of_apocalypse": "spell_fire_selfdestruct",
    "knight_of_xoroth_shieldgore": "ability_warrior_shieldbreak",
    "knight_of_xoroth_call_hellfire_imp": "spell_shadow_summonimp",
    "knight_of_xoroth_call_hellfire_abyssal": "spell_shadow_summoninfernal",
    "knight_of_xoroth_implosion": "spell_fire_felfirenova",
    "knight_of_xoroth_sacrificial_circle": "spell_shadow_ritualofsacrifice",
    "knight_of_xoroth_curse_of_xoroth": "spell_shadow_curseofmannoroth",
    "knight_of_xoroth_chains_of_xoroth": "spell_frost_chainsofice",
    "knight_of_xoroth_hellfire_bellows": "spell_fire_lavaspawn",
    "knight_of_xoroth_legions_presence": "spell_shadow_demonicpact",
    "knight_of_xoroth_gore": "ability_gouge",
    "knight_of_xoroth_warbringer": "ability_warrior_charge",
    "knight_of_xoroth_brimstone_bludgeon": "inv_mace_18",
    "knight_of_xoroth_decimation": "spell_shadow_demonicfortitude",
    "knight_of_xoroth_burning_blade": "spell_fire_flameblades",
    "knight_of_xoroth_searing_blade": "spell_fire_searingtotem",
    "knight_of_xoroth_seeking_flame": "spell_fire_flamebolt",
    "knight_of_xoroth_hellmaw": "spell_shadow_shadowfury",
    "knight_of_xoroth_hellfire_form": "spell_shadow_demonform",
    "knight_of_xoroth_hellstorm": "spell_fire_meteorstorm",
    "knight_of_xoroth_summon_greater_imp": "spell_shadow_summonfelguard",
})


MAPPING.update({
    # =================================================================
    # PYROMANCER - dragonflight fire. Draconic is the Aspects (Alexstrasza,
    # Nozdormu, Neltharion, Deathwing), Flameweaving is the healer with the
    # Phoenix, Incineration is pure burn. Everything is fire, so the trees
    # separate by subject: dragons and wings for Draconic, phoenix and
    # embers for Flameweaving, molten rock and explosions for Incineration.
    # =================================================================
    "pyromancer_draconic_critical_pressure": ("spell_fire_playingwithfire", 40),
    "pyromancer_draconic_alexstraszas_gift": ("inv_misc_head_dragon_red", 40),
    "pyromancer_draconic_flamer": ("spell_fire_burningspeed", 40),
    "pyromancer_draconic_pyromancy": ("spell_fire_fire", 40),
    "pyromancer_draconic_mad_aspects_scepter": ("inv_misc_head_dragon_black", 40),
    "pyromancer_draconic_searing_flames": ("spell_fire_lavaspawn", 200),
    "pyromancer_draconic_draconic_tempest": ("spell_fire_windsofwoe", 40),
    "pyromancer_draconic_cinderstorm": ("spell_fire_flameshock", 40),
    "pyromancer_draconic_dragons_edge": "spell_fire_masterofelements",
    "pyromancer_draconic_flames_of_the_aspects": ("inv_misc_head_dragon_bronze", 40),
    "pyromancer_draconic_overwhelming_flames": ("spell_fire_selfdestruct", 40),
    "pyromancer_draconic_black_magic": ("spell_shadow_chilltouch", 40),
    "pyromancer_draconic_earthwarder": "spell_nature_earthquake",
    "pyromancer_draconic_draconic_rage": ("spell_fire_meteorstorm", 200),
    "pyromancer_draconic_fire_and_brimstone": "spell_fire_felflamebolt",
    "pyromancer_draconic_ascender": ("ability_racial_flayer", 40),
    "pyromancer_draconic_echo_of_nozdormu": ("spell_nature_timestop", 40),
    "pyromancer_draconic_blackflight_resurgence": ("inv_misc_monsterscales_15", 40),
    "pyromancer_draconic_legacy_of_deathwing": ("inv_misc_head_dragon_01", 40),
    "pyromancer_draconic_inner_flame": ("spell_holy_innerfire", 200),
    "pyromancer_draconic_aspect_of_eternity": ("spell_arcane_arcane03", 40),
    "pyromancer_draconic_aspect_of_earth": "spell_nature_stoneclawtotem",
    "pyromancer_draconic_death_from_above": ("ability_hunter_pet_dragonhawk", 40),
    # --- Flameweaving: the healer
    "pyromancer_flameweaving_scorching_spirit": "spell_holy_divinespirit",
    "pyromancer_flameweaving_ember_charm": "inv_misc_gem_ruby_01",
    "pyromancer_flameweaving_soothing_flames": ("spell_holy_flashheal", 40),
    "pyromancer_flameweaving_from_the_ashes": ("spell_fire_elemental_totem", 200),
    "pyromancer_flameweaving_spirit_of_fire": ("spell_fire_sealoffire", 200),
    "pyromancer_flameweaving_living_flame": ("spell_fire_flamebolt", 40),
    "pyromancer_flameweaving_rekindle": "spell_holy_heal",
    "pyromancer_flameweaving_touched_by_fire": "spell_holy_searinglight",
    "pyromancer_flameweaving_cauterizing_wounds": "spell_holy_blessedrecovery",
    "pyromancer_flameweaving_shielded_by_flames": ("spell_fire_firearmor", 40),
    "pyromancer_flameweaving_fiery_faith": ("spell_holy_innerfire", 40),
    "pyromancer_flameweaving_ashen_priest": "spell_magic_managain",
    "pyromancer_flameweaving_burning_passion": "spell_holy_prayerofhealing",
    "pyromancer_flameweaving_tender_touch": ("spell_holy_layonhands", 40),
    "pyromancer_flameweaving_warmth": ("spell_holy_sealofsalvation", 40),
    "pyromancer_flameweaving_sageweaving": "spell_holy_borrowedtime",
    "pyromancer_flameweaving_kaels_command": ("spell_fire_bluefire", 40),
    "pyromancer_flameweaving_neltharions_resolve": "spell_holy_sealofprotection",
    "pyromancer_flameweaving_spirit_of_the_phoenix": ("spell_fire_elementaldevastation", 40),
    "pyromancer_flameweaving_sunstrider_array": ("spell_holy_divineillumination", 40),
    "pyromancer_flameweaving_burning_crescendo": ("spell_holy_restoration", 40),
    "pyromancer_flameweaving_scepter_of_fire": "inv_staff_goldfeathered_01",
    "pyromancer_flameweaving_fueling_the_fire": ("spell_fire_searingtotem", 40),
    # --- Incineration: pure burn
    "pyromancer_incineration_magnitude_10": "spell_fire_fireball",
    "pyromancer_incineration_cataclysmic_power": ("spell_fire_flamebolt", 200),
    "pyromancer_incineration_embrace_the_fire": ("spell_fire_immolation", 40),
    "pyromancer_incineration_fire_safety": ("spell_fire_firebolt02", 40),
    "pyromancer_incineration_searing_power": ("spell_fire_soulburn", 40),
    "pyromancer_incineration_explosive": ("spell_fire_fireball02", 40),
    "pyromancer_incineration_pyromaniac": ("spell_fire_incinerate", 40),
    "pyromancer_incineration_stoke": ("spell_fire_flameshock", 200),
    "pyromancer_incineration_wreath_of_flames": ("spell_fire_flameblades", 40),
    "pyromancer_incineration_melting_point": ("spell_fire_moltenblood", 40),
    "pyromancer_incineration_molten_storm": ("spell_fire_volcano", 40),
    "pyromancer_incineration_fiery_passion": ("spell_fire_burnout", 40),
    "pyromancer_incineration_lighting_the_fuse": ("spell_fire_sealoffire", 40),
    "pyromancer_incineration_to_ashes": ("spell_fire_burningspeed", 200),
    "pyromancer_incineration_combustion": ("spell_fire_selfdestruct", 200),
    "pyromancer_incineration_rapid_incineration": ("spell_fire_lavaspawn", 40),
    "pyromancer_incineration_pillar_of_flame": ("spell_fire_elemental_totem", 40),
    "pyromancer_incineration_destroyers_legacy": ("spell_fire_meteorstorm", 40),
    "pyromancer_incineration_dark_iron_legacy": ("spell_fire_masterofelements", 40),
    "pyromancer_incineration_fired_up": ("spell_fire_playingwithfire", 200),
    "pyromancer_incineration_flamespiller": ("spell_fire_felflamering", 40),
    "pyromancer_incineration_arsonist": ("spell_fire_fire", 200),
    "pyromancer_incineration_pyroclasm": ("spell_fire_felfirenova", 40),
    # --- abilities
    "pyromancer_attack": "ability_meleedamage",
    "pyromancer_flare_bolt": "spell_fire_flamebolt",
    "pyromancer_blaze": "spell_fire_immolation",
    "pyromancer_lava_shard": "spell_fire_volcano",
    "pyromancer_dragons_wrath": "inv_misc_head_dragon_red",
    "pyromancer_ember_touch": "spell_holy_flashheal",
    "pyromancer_meteor": "spell_fire_meteorstorm",
    "pyromancer_flame_step": "spell_fire_burningspeed",
    "pyromancer_cindergrip": "spell_fire_flameshock",
    "pyromancer_gaze_of_ysera": "inv_misc_head_dragon_green",
    "pyromancer_dragon_leap": "ability_racial_flayer",
    "pyromancer_firestorm": "spell_fire_windsofwoe",
    "pyromancer_circle_of_fire": "spell_fire_felflamering",
    "pyromancer_cataclysm": "spell_fire_selfdestruct",
    "pyromancer_volcanic_shell": "spell_fire_firearmor",
    "pyromancer_inferno_barrier": "spell_fire_moltenblood",
    "pyromancer_essence_of_malygos": "inv_misc_head_dragon_blue",
    "pyromancer_grace_of_alexstrasza": "spell_holy_restoration",
    "pyromancer_ignis_ultimatus": "spell_fire_soulburn",
    "pyromancer_eruption": "spell_fire_burnout",
    "pyromancer_ignite": "spell_fire_firebolt02",
    "pyromancer_explode": "spell_fire_fireball02",
    "pyromancer_pillar_of_flame": "spell_fire_elemental_totem",
    "pyromancer_slag_barrage": "spell_fire_lavaspawn",
    "pyromancer_pyroclasm": "spell_fire_felfirenova",
    "pyromancer_fired_up": "spell_fire_playingwithfire",
    "pyromancer_kindle": "spell_fire_sealoffire",
    "pyromancer_cinderheart": "spell_holy_layonhands",
    "pyromancer_cleansing_flames": "spell_fire_fire",
    "pyromancer_phoenix_egg": "spell_fire_elementaldevastation",
    "pyromancer_kaels_command": "spell_fire_bluefire",
    "pyromancer_roaring_pyre": "spell_fire_searingtotem",
    "pyromancer_phoenix_dive": "ability_hunter_pet_dragonhawk",
    "pyromancer_burn_impurities": "spell_fire_incinerate",
    "pyromancer_sunstrider_array": "spell_holy_divineillumination",
    "pyromancer_destroyers_maw": "inv_misc_head_dragon_black",
    "pyromancer_firefall": "spell_fire_flameblades",
    "pyromancer_flames_of_neltharion": "inv_misc_monsterscales_15",
    "pyromancer_echo_of_nozdormu": "spell_nature_timestop",
    "pyromancer_death_from_above": "inv_misc_head_dragon_bronze",
    "pyromancer_breath_of_neltharion": "spell_shadow_chilltouch",
    "pyromancer_draconic_invocation": "spell_arcane_arcane03",
    "pyromancer_aspects_blessing": "spell_holy_sealofsalvation",
    "pyromancer_draconic_aspect": "inv_misc_head_dragon_01",
    "pyromancer_inner_flame": "spell_holy_innerfire",
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
