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

#: id -> Blizzard icon name. Grouped by class, then by tree, in the order
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
    "barbarian_ancestry_trip_to_the_alehouse": "inv_drink_05",
    "barbarian_ancestry_drinking_frenzy": "ability_warrior_rampage",
    "barbarian_ancestry_fill_level": "inv_drink_12",
    "barbarian_ancestry_frozen_warlord": "spell_frost_frozencore",
    "barbarian_ancestry_improved_ancestral_combat": "spell_nature_ancestralguardian",
    "barbarian_ancestry_ice_cold_bubbles": "spell_frost_frostbolt02",
    "barbarian_ancestry_thanes_guard": "inv_shield_06",
    "barbarian_ancestry_liquid_courage": "inv_drink_09",
    "barbarian_ancestry_cold_brew": "inv_drink_17",
    "barbarian_ancestry_blind_stupor": "spell_shadow_mindsteal",
    "barbarian_ancestry_unified_rage": "ability_warrior_bloodfrenzy",
    "barbarian_ancestry_hodirs_revenge": "spell_frost_wisp",
    "barbarian_ancestry_icebound_ancestry": "spell_frost_arcticwinds",
    "barbarian_ancestry_frost_giants_fury": "spell_frost_frostshock",
    "barbarian_ancestry_the_spins": "spell_nature_spiritwolf",
    "barbarian_ancestry_breaking_morale": "ability_warrior_warcry",
    "barbarian_ancestry_might_of_utgarde": "spell_nature_spiritarmor",
    "barbarian_ancestry_frozen_blades": "ability_warrior_punishingblow",
    "barbarian_ancestry_ancestors_fury": "spell_frost_frostward",
    "barbarian_ancestry_rage_of_the_north": "spell_frost_chillingblast",
    "barbarian_ancestry_uniting_voice": "spell_holy_prayerofspirit",
    "barbarian_ancestry_clanlords_totem": "spell_nature_strengthofearthtotem02",
    "barbarian_ancestry_fury_of_the_north": "spell_frost_summonwaterelemental",
    # --- Brutality: unadorned melee
    "barbarian_brutality_pure_power": "ability_warrior_decisivestrike",
    "barbarian_brutality_reckless_movements": "ability_warrior_innerrage",
    "barbarian_brutality_savage_strength": "ability_rogue_sprint",
    "barbarian_brutality_excessive_power": "spell_shadow_unholyfrenzy",
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
    "barbarian_brutality_whirling_assault": "ability_whirlwind",
    "barbarian_brutality_rancor": "ability_warrior_cleave",
    "barbarian_brutality_thirst_for_battle": "spell_nature_bloodlust",
    "barbarian_brutality_sustaining_swings": "spell_shadow_lifedrain",
    "barbarian_brutality_overkill": "ability_warrior_savageblow",
    "barbarian_brutality_body_builder": "ability_hunter_pet_gorilla",
    "barbarian_brutality_blood_and_glory": "ability_warrior_bloodbath",
    "barbarian_brutality_steelslinger": "ability_warrior_trauma",
    "barbarian_brutality_maximum_carnage": "ability_warrior_bladestorm",
    # --- Headhunting: thrown spears, bleeds, troll
    "barbarian_headhunting_strong_arm": "ability_throw",
    "barbarian_headhunting_puncture_wounds": "ability_rogue_rupture",
    "barbarian_headhunting_gruesome": "ability_rogue_disembowel",
    "barbarian_headhunting_guts_splatter": "ability_warrior_sunder",
    "barbarian_headhunting_frothing_savage": "ability_criticalstrike",
    "barbarian_headhunting_entrails": "inv_misc_organ_01",
    "barbarian_headhunting_to_the_bone": "ability_warrior_riposte",
    "barbarian_headhunting_savage": "ability_druid_mangle2",
    "barbarian_headhunting_spear_thrower": "inv_spear_07",
    "barbarian_headhunting_legacy_of_the_amani": "inv_spear_04",
    "barbarian_headhunting_furious_berserker": "racial_troll_berserk",
    "barbarian_headhunting_no_survivors": "ability_rogue_bloodsplatter",
    "barbarian_headhunting_time_to_kill": "ability_warrior_challange",
    "barbarian_headhunting_hunting_for_sport": "ability_hunter_markedfordeath",
    "barbarian_headhunting_vengeance_for_zuljin": "inv_misc_head_troll_01",
    "barbarian_headhunting_raging_spirit": "spell_shadow_shadowfiend",
    "barbarian_headhunting_payback": "ability_gouge",
    "barbarian_headhunting_skullseeker": "inv_misc_bone_skull_01",
    "barbarian_headhunting_spear_shards": "inv_spear_06",
    "barbarian_headhunting_brutal_form": "spell_nature_healingtouch",
    "barbarian_headhunting_gurubashi_technique": "inv_weapon_shortblade_15",
    "barbarian_headhunting_senjins_guidance": "inv_spear_05",
    "barbarian_headhunting_berserker": "racial_troll_berserk",
    # --- Abilities, blank
    "barbarian_unbridled_rage": "spell_shadow_unholyfrenzy",
    "barbarian_defiance": "ability_warrior_defensivestance",
    "barbarian_jawbreaker": "inv_gauntlets_04",
    "barbarian_maiming_spear": "ability_hunter_snipershot",
    "barbarian_skull_smash": "inv_misc_bone_skull_02",
    "barbarian_ancestral_roar": "spell_nature_ancestralguardian",
    "barbarian_warband": "spell_holy_prayerofhealing",
    "barbarian_thick_skull": "inv_helmet_23",
    "barbarian_hodirs_wrath": "spell_frost_chillingblast",
    "barbarian_onslaught": "ability_warrior_endlessrage",
    "barbarian_battle_vigor": "ability_warrior_bloodfrenzy",
    "barbarian_savage_revelry": "inv_drink_07",
    "barbarian_axe_twirling": "ability_whirlwind",
    "barbarian_ancestral_combat": "spell_nature_spiritwolf",
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
    "barbarian_tavern_brawl": "ability_warrior_punishingblow",
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


def fetch(icon_name):
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
    out = io.BytesIO()
    im.convert("RGBA").save(out, format="PNG")
    return out.getvalue()


def main(argv):
    dry = "--dry-run" in argv
    only = argv[argv.index("--class") + 1] if "--class" in argv else None

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
    for ident, icon in items:
        if ident not in dest:
            continue
        try:
            data = fetch(icon)
        except Exception as exc:                               # noqa: BLE001
            bad += 1
            failures.append((ident, icon, str(exc)[:70]))
            continue
        ok += 1
        if not dry:
            dest[ident].mkdir(parents=True, exist_ok=True)
            (dest[ident] / f"{ident}.png").write_bytes(data)

    print(f"{ok} icon name(s) resolved to real art, {bad} did not"
          f"{' (dry run, nothing written)' if dry else ''}")
    if failures:
        print("\nTHESE NAMES ARE WRONG - fix the mapping, do not install them:")
        for ident, icon, why in failures:
            print(f"    {ident:48} -> {icon:40} {why}")
    return 1 if (bad or unknown) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
