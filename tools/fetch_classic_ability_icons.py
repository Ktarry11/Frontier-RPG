"""Fetch real WoW ability icons for the classic-9 classes and save them as assets/icons/abilities/<ability_id>.png.

Icon CDN: wow.zamimg.com/images/wow/icons/large/<icon_name>.jpg (native 56x56, square).  The ability_id -> icon_name
table below is the single source of truth; re-run to refresh.  Druid/Shaman were done in an earlier pass.

    python3 tools/fetch_classic_ability_icons.py [--sheet out_dir]   # --sheet writes labelled contact sheets for review
"""
import io, os, sys, urllib.request
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets/icons/abilities")
CDN = "https://wow.zamimg.com/images/wow/icons/large/{}.jpg"

ICONS = {
 # ---- Paladin
 "paladin_crusader_strike": "spell_holy_crusaderstrike", "paladin_holy_light": "spell_holy_holybolt",
 "paladin_judgement": "spell_holy_righteousfury", "paladin_consecration": "spell_holy_innerfire",
 "paladin_blessing_of_might": "spell_holy_fistofjustice", "paladin_hammer_of_justice": "spell_holy_sealofmight",
 "paladin_divine_shield": "spell_holy_divineintervention", "paladin_hammer_of_wrath": "ability_thunderclap",
 "paladin_holy_shock": "spell_holy_searinglight", "paladin_avengers_shield": "spell_holy_avengersshield",
 "paladin_divine_storm": "ability_paladin_divinestorm", "paladin_repentance": "spell_holy_prayerofhealing",
 "paladin_flash_of_light": "spell_holy_flashheal", "paladin_cleanse": "spell_holy_renew",
 "paladin_blessing_of_wisdom": "spell_holy_sealofwisdom", "paladin_blessing_of_kings": "spell_magic_magearmor",
 "paladin_exorcism": "spell_holy_excorcism", "paladin_seal_of_righteousness": "ability_thunderbolt",
 "paladin_turn_evil": "spell_holy_turnundead", "paladin_redemption": "spell_holy_resurrection",
 "paladin_lay_on_hands": "spell_holy_layonhands", "paladin_seal_of_command": "ability_warrior_innerrage",
 # ---- Warrior
 "warrior_heroic_strike": "ability_rogue_ambush", "warrior_rend": "ability_gouge",
 "warrior_thunder_clap": "spell_nature_thunderclap", "warrior_battle_shout": "ability_warrior_battleshout",
 "warrior_overpower": "ability_meleedamage", "warrior_demoralizing_shout": "ability_warrior_warcry",
 "warrior_mortal_strike": "ability_warrior_savageblow", "warrior_execute": "inv_sword_48",
 "warrior_bladestorm": "ability_warrior_bladestorm", "warrior_devastate": "inv_sword_11",
 "warrior_concussion_blow": "ability_thunderbolt", "warrior_shockwave": "ability_warrior_shockwave",
 "warrior_bloodthirst": "spell_nature_bloodlust", "warrior_bloodrage": "ability_racial_bloodrage",
 "warrior_cleave": "ability_warrior_cleave", "warrior_disarm": "ability_warrior_disarm",
 "warrior_retaliation": "ability_warrior_challange", "warrior_intimidating_shout": "ability_golemthunderclap",
 "warrior_shield_wall": "ability_warrior_shieldwall", "warrior_charge": "ability_warrior_charge",
 "warrior_intercept": "ability_heroicleap", "warrior_berserker_rage": "spell_nature_ancestralguardian",
 "warrior_whirlwind": "ability_whirlwind", "warrior_pummel": "inv_gauntlets_04",
 "warrior_recklessness": "ability_criticalstrike", "warrior_sunder_armor": "ability_warrior_sunder",
 # ---- Rogue
 "rogue_sinister_strike": "spell_shadow_ritualofsacrifice", "rogue_backstab": "ability_backstab",
 "rogue_eviscerate": "ability_rogue_eviscerate", "rogue_rupture": "ability_rogue_rupture",
 "rogue_evasion": "spell_shadow_shadowward", "rogue_expose_armor": "ability_warrior_riposte",
 "rogue_adrenaline_rush": "spell_shadow_shadowworddominate", "rogue_mutilate": "ability_rogue_shadowstrikes",
 "rogue_cold_blood": "spell_ice_lament", "rogue_hemorrhage": "spell_shadow_lifedrain",
 "rogue_shadow_dance": "ability_rogue_shadowdance", "rogue_slice_and_dice": "ability_rogue_slicedice",
 "rogue_sap": "ability_sap", "rogue_sprint": "ability_rogue_sprint", "rogue_kick": "ability_kick",
 "rogue_gouge": "ability_gouge", "rogue_feint": "ability_rogue_feint", "rogue_vanish": "ability_vanish",
 "rogue_garrote": "ability_rogue_garrote", "rogue_cheap_shot": "ability_cheapshot",
 "rogue_deadly_poison": "ability_rogue_deadlybrew", "rogue_ambush": "ability_rogue_ambush",
 "rogue_crippling_poison": "ability_poisonsting", "rogue_shiv": "inv_throwingknife_04",
 "rogue_blade_flurry": "ability_warrior_punishingblow", "rogue_kidney_shot": "ability_rogue_kidneyshot",
 "rogue_blind": "spell_shadow_mindsteal", "rogue_envenom": "ability_rogue_disembowel",
 "rogue_fan_of_knives": "ability_rogue_fanofknives", "rogue_preparation": "spell_shadow_antishadow",
 "rogue_killing_spree": "ability_rogue_murderspree",
 # ---- Hunter
 "hunter_steady_shot": "ability_hunter_steadyshot", "hunter_arcane_shot": "ability_impalingbolt",
 "hunter_multi_shot": "ability_upgrademoonglaive", "hunter_aimed_shot": "inv_spear_07",
 "hunter_serpent_sting": "ability_hunter_quickshot", "hunter_hunters_mark": "ability_hunter_snipershot",
 "hunter_aspect_of_the_hawk": "spell_nature_ravenform", "hunter_explosive_trap": "spell_fire_selfdestruct",
 "hunter_chimera_shot": "ability_hunter_chimerashot2", "hunter_explosive_shot": "ability_hunter_explosiveshot",
 "hunter_black_arrow": "ability_theblackarrow", "hunter_wyvern_sting": "inv_spear_02",
 "hunter_tame_beast": "ability_hunter_beasttaming", "hunter_mend_pet": "ability_hunter_mendpet",
 "hunter_revive_pet": "ability_hunter_beastsoothe", "hunter_concussive_shot": "spell_frost_stun",
 "hunter_disengage": "ability_rogue_feint", "hunter_freezing_trap": "spell_frost_chainsofice",
 "hunter_feign_death": "ability_rogue_feigndeath", "hunter_scare_beast": "ability_druid_cower",
 "hunter_aspect_of_the_wild": "spell_nature_protectionformnature",
 # ---- Mage
 "mage_fireball": "spell_fire_flamebolt", "mage_frostbolt": "spell_frost_frostbolt02",
 "mage_arcane_explosion": "spell_nature_wispsplode", "mage_blast_wave": "spell_holy_excorcism_02",
 "mage_blizzard": "spell_frost_icestorm", "mage_living_flame": "spell_fire_fireball",
 "mage_arcane_intellect": "spell_holy_magicalsentry", "mage_frost_nova": "spell_frost_frostnova",
 "mage_pyroblast": "spell_fire_fireball02", "mage_ice_barrier": "spell_ice_lament",
 "mage_presence_of_mind": "spell_nature_enchantarmor", "mage_icy_veins": "spell_frost_coldhearted",
 "mage_combustion": "spell_fire_sealoffire", "mage_cold_snap": "spell_frost_wizardmark",
 "mage_cone_of_cold": "spell_frost_glacier", "mage_fire_blast": "spell_fire_fireball",
 "mage_mage_armor": "spell_magic_magearmor", "mage_mana_shield": "spell_shadow_detectlesserinvisibility",
 "mage_counterspell": "spell_frost_iceshock", "mage_polymorph": "spell_nature_polymorph",
 "mage_ice_lance": "spell_frost_frostblast",
 # ---- Warlock
 "warlock_shadow_bolt": "spell_shadow_shadowbolt", "warlock_corruption": "spell_shadow_abominationexplosion",
 "warlock_immolate": "spell_fire_immolation", "warlock_summon_imp": "spell_shadow_summonimp",
 "warlock_summon_voidwalker": "spell_shadow_summonvoidwalker", "warlock_summon_succubus": "spell_shadow_summonsuccubus",
 "warlock_summon_felhunter": "spell_shadow_summonfelhunter", "warlock_curse_of_weakness": "spell_shadow_curseofmannoroth",
 "warlock_drain_life": "spell_shadow_lifedrain02", "warlock_demon_armor": "spell_shadow_ragingscream",
 "warlock_unstable_affliction": "spell_shadow_unstableaffliction_3", "warlock_shadowburn": "spell_shadow_scourgebuild",
 "warlock_dark_pact": "spell_shadow_darkritual", "warlock_metamorphosis": "spell_shadow_demonform",
 "warlock_conflagrate": "spell_fire_fireball", "warlock_chaos_bolt": "spell_fire_fireball02",
 "warlock_shadowfury": "spell_shadow_shadowfury", "warlock_fear": "spell_shadow_possession",
 "warlock_life_tap": "spell_shadow_burningspirit", "warlock_health_funnel": "spell_shadow_lifedrain",
 "warlock_searing_pain": "spell_fire_soulburn", "warlock_curse_of_agony": "spell_shadow_curseofsargeras",
 "warlock_curse_of_recklessness": "spell_shadow_unholystrength", "warlock_banish": "spell_shadow_cripple",
 # ---- Priest
 "priest_smite": "spell_holy_holysmite", "priest_heal": "spell_holy_heal",
 "priest_shadow_word_pain": "spell_shadow_shadowwordpain", "priest_renew": "spell_holy_renew",
 "priest_power_word_fortitude": "spell_holy_wordfortitude", "priest_mind_blast": "spell_shadow_unholyfrenzy",
 "priest_power_word_shield": "spell_holy_powerwordshield", "priest_holy_fire": "spell_holy_searinglight",
 "priest_penance": "spell_holy_penance", "priest_circle_of_healing": "spell_holy_circleofrenewal",
 "priest_shadowform": "spell_shadow_shadowform", "priest_silence": "spell_shadow_impphaseshift",
 "priest_mind_flay": "spell_shadow_siphonmana", "priest_vampiric_touch": "spell_holy_stoicism",
 "priest_mind_sear": "spell_shadow_mindshear", "priest_fade": "spell_magic_lesserinvisibilty",
 "priest_psychic_scream": "spell_shadow_psychicscream", "priest_dispel_magic": "spell_holy_dispelmagic",
 "priest_abolish_disease": "spell_nature_nullifydisease", "priest_prayer_of_healing": "spell_holy_prayerofhealing02",
 "priest_inner_fire": "spell_holy_innerfire",
}


def fetch(name):
    req = urllib.request.Request(CDN.format(name), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return Image.open(io.BytesIO(r.read())).convert("RGB")


def main():
    cache = {}; fails = []
    for aid, name in ICONS.items():
        try:
            im = cache.get(name) or fetch(name); cache[name] = im
            if im.size[0] != im.size[1]: fails.append((aid, name, f"not square {im.size}")); continue
            im.save(os.path.join(OUT, aid + ".png"))
        except Exception as e:
            fails.append((aid, name, str(e)[:60]))
    print(f"saved {len(ICONS) - len(fails)}/{len(ICONS)}")
    for f in fails: print("FAIL", f)
    if "--sheet" in sys.argv:
        d = sys.argv[sys.argv.index("--sheet") + 1]; os.makedirs(d, exist_ok=True)
        by = {}
        for aid in ICONS: by.setdefault(aid.split("_")[0], []).append(aid)
        for cls, ids in by.items():
            cols = 6; cell_w, cell_h = 150, 96
            rows = (len(ids) + cols - 1) // cols
            sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), (24, 24, 32)); dr = ImageDraw.Draw(sheet)
            for i, aid in enumerate(ids):
                p = os.path.join(OUT, aid + ".png")
                if not os.path.exists(p): continue
                ic = Image.open(p).convert("RGB").resize((56, 56))
                x, y = (i % cols) * cell_w, (i // cols) * cell_h
                sheet.paste(ic, (x + 47, y + 4)); dr.text((x + 4, y + 64), aid.split("_", 1)[1][:24], fill=(230, 230, 230))
            sheet.save(os.path.join(d, cls + ".png"))

if __name__ == "__main__":
    main()
