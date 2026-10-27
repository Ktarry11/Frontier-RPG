#!/usr/bin/env python3
"""Replace mass-assigned talent icons with correct per-talent art.

    python3 tools/fix_talent_icons.py            # fetch and install
    python3 tools/fix_talent_icons.py --dry-run  # just check the CDN names resolve

THE PROBLEM
-----------
146 talents shared only 59 icon images. The art itself is real Blizzard art and
looks fine; the ASSIGNMENT was the problem - whoever built it mapped one icon
per "effect archetype" and let it cross class lines. The clearest tells:

  * one arcane-missile icon on two druid BALANCE talents and four mage ARCANE
    talents - Starlight Wrath and Arcane Barrage were byte-identical
  * a tauren head on hunter Longevity, MAGE Arcane Mind, rogue Vitality and
    two warrior talents, because all five happen to be stamina/intellect
    passives
  * a paladin shield on a priest talent

This file is the per-talent mapping that replaces it, in the same shape as
tools/fetch_classic_ability_icons.py - that hand-curated table is exactly why
the ABILITY icons already look right, and talents never got the same pass.

Only the classic-9 talents are mapped here, because those are real WoW talents
with canonical icons that can be looked up and verified. The 30 homebrew
Frontier talents that also share icons are listed at the bottom and need art
direction rather than a lookup.

EVERY FETCH IS VERIFIED. A wrong icon name returns a 404 or an HTML error page
rather than an image, which would silently install a broken file - so each
download is checked for a real decodable image of a sane size before anything
is written, and anything that fails is reported and skipped rather than
guessed at.
"""
import io
import sys
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "icons" / "talents"
CDN = "https://wow.zamimg.com/images/wow/icons/large/{}.jpg"
SIZE = 60  # the size the Frontier talent icons are standardised at

#: talent_id -> WoW icon name. Chosen per talent, matched to what the talent
#: actually does and to its class's school, which is the whole point.
ICONS = {
    # ── DRUID ────────────────────────────────────────────────────────────
    "druid_balance_starlight_wrath": "spell_nature_abolishmagic",
    "druid_balance_wrath_of_cenarius": "ability_druid_twilightswrath",
    "druid_restoration_gift_of_the_earthmother": "spell_nature_giftofthewild",
    "druid_restoration_naturalist": "spell_nature_healingtouch",
    "druid_restoration_natures_bounty": "spell_nature_resistnature",
    "druid_restoration_living_spirit": "spell_nature_spiritarmor",
    "druid_restoration_restoration_mastery": "spell_nature_rejuvenation",
    "druid_feral_nurturing_instinct": "ability_druid_healinginstincts",
    "druid_feral_rend_and_tear": "ability_druid_disembowel",
    "druid_feral_shredding_attacks": "spell_shadow_vampiricaura",
    "druid_feral_natural_reaction": "ability_druid_demoralizingroar",
    # ── MAGE ─────────────────────────────────────────────────────────────
    "mage_arcane_arcane_barrage": "ability_mage_arcanebarrage",
    "mage_arcane_arcane_blast": "spell_arcane_blast",
    "mage_arcane_arcane_impact": "spell_nature_wispsplode",
    "mage_arcane_arcane_instability": "spell_shadow_teleport",
    "mage_arcane_arcane_mind": "spell_shadow_charm",
    "mage_arcane_magic_absorption": "spell_nature_astralrecalgroup",
    "mage_arcane_magic_attunement": "spell_nature_removecurse",
    "mage_arcane_improved_counterspell": "spell_frost_iceshock",
    "mage_fire_firestarter": "spell_fire_sealoffire",
    "mage_fire_playing_with_fire": "spell_fire_playingwithfire",
    "mage_fire_dragons_breath": "inv_misc_head_dragon_01",
    # ── ROGUE ────────────────────────────────────────────────────────────
    "rogue_assassination_assassins_resolve": "ability_rogue_deadlybrew",
    "rogue_assassination_relentless_strikes": "ability_warrior_decisivestrike",
    "rogue_assassination_assassination_mastery": "ability_rogue_disembowel",
    "rogue_assassination_hunger_for_blood": "ability_rogue_hungerforblood",
    "rogue_assassination_mutilate": "ability_rogue_shadowstrikes",
    "rogue_assassination_puncturing_wounds": "ability_criticalstrike",
    "rogue_assassination_turn_the_tables": "ability_rogue_turnthetables",
    "rogue_assassination_blood_spatter": "ability_rogue_bloodsplatter",
    "rogue_assassination_improved_poisons": "ability_poisons",
    "rogue_combat_combat_potency": "inv_weapon_shortblade_38",
    "rogue_combat_vitality": "ability_rogue_quickrecovery",
    "rogue_combat_riposte": "ability_warrior_challange",
    "rogue_combat_prey_on_the_weak": "ability_rogue_preyontheweak",
    "rogue_combat_savage_combat": "ability_druid_mangle",
    "rogue_combat_dagger_specialization": "inv_weapon_shortblade_05",
    "rogue_combat_mace_specialization": "inv_mace_01",
    "rogue_combat_killing_spree": "ability_rogue_murderspree",
    "rogue_combat_bandits_guile": "ability_rogue_waylay",
    "rogue_subtlety_subtlety_mastery": "ability_rogue_sanguinaryvein",
    "rogue_subtlety_heightened_senses": "ability_ambush",
    "rogue_subtlety_premeditation": "spell_shadow_possession",
    "rogue_subtlety_honor_among_thieves": "ability_rogue_honoramongstthieves",
    "rogue_subtlety_shadow_dance": "ability_rogue_shadowdance",
    "rogue_subtlety_slaughter_from_the_shadows": "ability_rogue_slaughterfromtheshadows",
    # ── WARRIOR ──────────────────────────────────────────────────────────
    "warrior_arms_arms_mastery": "ability_warrior_improveddisciplines",
    "warrior_arms_last_stand": "spell_holy_ashestoashes",
    "warrior_fury_cruelty": "ability_rogue_eviscerate",
    "warrior_fury_fury_mastery": "ability_warrior_bloodfrenzy",
    "warrior_fury_armored_to_the_teeth": "inv_shoulder_20",
    "warrior_fury_bloodbath": "ability_warrior_bloodbath",
    "warrior_protection_iron_will": "spell_magic_magearmor",
    "warrior_protection_vitality": "spell_holy_blessingofstamina",
    "warrior_protection_sword_and_board": "ability_warrior_swordandboard",
    "warrior_protection_concussion_blow": "ability_thunderbolt",
    "warrior_protection_last_stand": "spell_holy_ashestoashes",
    "warrior_protection_protection_mastery": "ability_warrior_safeguard",
    # ── PALADIN ──────────────────────────────────────────────────────────
    "paladin_holy_holy_capstone": "ability_paladin_blessedmending",
    "paladin_holy_beacon_of_light": "ability_paladin_beaconoflight",
    "paladin_holy_divine_favor": "spell_holy_heal",
    "paladin_holy_light_grace": "spell_holy_healingaura",
    "paladin_protection_guarded_by_the_light": "ability_paladin_shieldofthetemplar",
    "paladin_protection_improved_holy_shield": "spell_holy_blessingofprotection",
    "paladin_protection_protection_capstone": "spell_holy_aspiration",
    "paladin_protection_sacred_duty": "spell_holy_divineintervention",
    "paladin_protection_shield_of_the_templar": "spell_holy_greaterblessingofsanctuary",
    "paladin_protection_combat_expertise": "spell_holy_weaponmastery",
    "paladin_protection_touched_by_the_light": "spell_holy_healingfocus",
    "paladin_protection_divine_guardian": "spell_holy_powerwordbarrier",
    "paladin_retribution_sheath_of_light": "ability_paladin_sheathoflight",
    "paladin_retribution_crusader_strike_mastery": "spell_holy_crusaderstrike",
    "paladin_retribution_heart_of_the_crusader": "spell_holy_holysmite",
    "paladin_retribution_retribution_capstone": "ability_paladin_judgementsofthejust",
    "paladin_retribution_sanctified_retribution": "spell_holy_mindvision",
    # ── PRIEST ───────────────────────────────────────────────────────────
    "priest_holy_blessed_resilience": "spell_nature_mentalquickness",
    "priest_holy_body_and_soul": "spell_holy_symbolofhope",
    "priest_holy_circle_of_healing": "spell_holy_circleofrenewal",
    "priest_holy_healing_prayers": "spell_holy_prayerofhealing02",
    "priest_holy_holy_mastery": "spell_holy_holyprotection",
    "priest_holy_spirit_of_redemption": "inv_enchant_essenceeternallarge",
    "priest_discipline_twin_disciplines": "spell_holy_wordfortitude",
    "priest_discipline_enlightenment": "spell_holy_greaterheal",
    "priest_discipline_grace": "spell_holy_sealofprotection",
    "priest_discipline_divine_aegis": "spell_holy_devineaegis",
    "priest_discipline_pain_suppression": "spell_holy_painsupression",
    "priest_shadow_shadow_mastery_capstone": "spell_shadow_devouringplague",
    "priest_shadow_darkness": "spell_shadow_twilight",
    # ── WARLOCK ──────────────────────────────────────────────────────────
    "warlock_demonology_demonic_brutality": "spell_shadow_summonvoidwalker",
    "warlock_demonology_demonic_resilience": "spell_shadow_demonicfortitude",
    "warlock_demonology_fel_vitality": "spell_shadow_lifedrain",
    "warlock_demonology_decimation": "spell_shadow_shadowfury",
    "warlock_destruction_improved_shadow_bolt": "spell_shadow_shadowbolt",
    "warlock_destruction_shadowburn": "spell_shadow_scourgebuild",
    "warlock_destruction_fire_and_brimstone": "ability_warlock_fireandbrimstone",
    "warlock_destruction_backlash": "spell_shadow_rune",
    "warlock_destruction_shadow_and_flame": "spell_shadow_shadowandflame",
    "warlock_affliction_amplify_curse": "spell_shadow_contagion",
    "warlock_affliction_malediction": "spell_shadow_curseofachimonde",
    "warlock_affliction_shadow_embrace": "spell_shadow_shadowembrace",
    # ── HUNTER ───────────────────────────────────────────────────────────
    "hunter_beast_mastery_longevity": "ability_druid_mastershapeshifter",
    "hunter_beast_mastery_invigoration": "ability_hunter_invigeration",
    "hunter_beast_mastery_focused_fire": "ability_hunter_focusedaim",
    "hunter_beast_mastery_bestial_wrath": "ability_druid_ferociousbite",
    "hunter_beast_mastery_the_beast_within": "ability_hunter_beastwithin",
    "hunter_marksmanship_improved_concussive_shot": "spell_frost_stun",
    "hunter_marksmanship_improved_stings": "ability_hunter_quickshot",
    "hunter_survival_survivalist": "ability_hunter_survivalinstincts",
    "hunter_survival_deterrence": "ability_whirlwind",
    "hunter_survival_thrill_of_the_hunt": "ability_hunter_thrillofthehunt",
    "hunter_survival_expose_weakness": "ability_rogue_findweakness",
    "hunter_survival_noxious_stings": "ability_hunter_potentvenom",
    # ── SHAMAN ───────────────────────────────────────────────────────────
    "shaman_enhancement_mental_dexterity": "ability_hunter_swiftstrike",
    "shaman_enhancement_feral_spirit": "spell_shaman_feralspirit",
    "shaman_enhancement_improved_ghost_wolf": "spell_nature_spiritwolf",
    "shaman_restoration_natures_guidance": "spell_nature_healingwavelesser",
}

#: Homebrew Frontier talents that also share icons. They have no canonical
#: lookup - picking art for them is an art-direction call, not a fetch, so
#: they are listed rather than guessed at.
FRONTIER_UNRESOLVED = [
    "runemaster (15)", "primalist (13)", "cultist (2)",
]


def fetch(icon_name):
    """-> PIL.Image, or raises. A wrong icon name returns a 404 or an HTML
    error body rather than a JPEG, so this insists on something that actually
    decodes as a sane-sized image before any file is written."""
    req = urllib.request.Request(CDN.format(icon_name), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        if r.status != 200:
            raise ValueError(f"HTTP {r.status}")
        data = r.read()
    if len(data) < 500:
        raise ValueError(f"suspiciously small ({len(data)}B) - probably an error page")
    img = Image.open(io.BytesIO(data))
    img.load()
    if min(img.size) < 32:
        raise ValueError(f"too small: {img.size}")
    return img.convert("RGBA")


def main():
    dry = "--dry-run" in sys.argv
    ok, bad = [], []
    for i, (tid, icon) in enumerate(sorted(ICONS.items()), 1):
        try:
            img = fetch(icon)
            if not dry:
                img.resize((SIZE, SIZE), Image.LANCZOS).save(OUT / f"{tid}.png")
            ok.append(tid)
            print(f"  [{i:3d}/{len(ICONS)}] ok   {tid:46s} {icon}")
        except Exception as exc:
            bad.append((tid, icon, str(exc)[:60]))
            print(f"  [{i:3d}/{len(ICONS)}] FAIL {tid:46s} {icon}  <- {exc}")

    print(f"\n{'checked' if dry else 'installed'}: {len(ok)}/{len(ICONS)}")
    if bad:
        print(f"\n{len(bad)} icon names did not resolve - these keep their old art "
              f"rather than being replaced with a broken file:")
        for tid, icon, why in bad:
            print(f"    {tid:46s} {icon:42s} {why}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
