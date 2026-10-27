#!/usr/bin/env python3
"""Move developer commentary out of player-facing ability descriptions.

Kyle, looking at Geode Barrage's tooltip: "We dont need all the behind the
scenes stuff visible...things like wildclaw is better."

Wildclaw reads "Strike with both weapons at once." Geode Barrage read its own
changelog: "(Real physical damage - was previously miscategorized as a spell
effect_type, which incorrectly scaled it off Spell Power; fixed to match its
own confirmed screenshot data.)"

Both kinds of text live in `description`, which is what the tooltip renders.
The commentary is worth keeping - several of these notes are the only record
that a WOTLK mechanic was deliberately approximated rather than forgotten - so
the original text MOVES to `_design_note` rather than being deleted. `_source`
is left alone; that holds provenance (screenshots), not caveats.

The replacements are written by hand rather than cut with a regex. A first
pass tried splitting each description at the point where the dev voice starts,
and it mangled them: sentences lost their verbs, Pyroblast kept the citation
and moved the flavour, and five abilities were left with no tooltip at all.

Every replacement describes what the ability ACTUALLY does in this engine, not
what its WOTLK original did. Feign Death here really is a damage-reduction
buff, so that is what its tooltip now says - no tooltip promises a mechanic
that does not exist.

Run with --apply to write; without it, prints what would change.
"""
import json
import sys
import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DESCRIPTIONS = {
    # --- Cultist ---
    "cultist_entropic_strike": "A weapon strike wreathed in void energy, applying Seething Void and generating Void Runes.",

    # --- Druid ---
    "druid_mark_of_the_wild": "Blesses the party with the wild's favor, increasing all attributes and granting resistance to Fire, Frost, Nature, Shadow and Arcane damage.",
    "druid_mangle": "Mangles the target with savage claws. Requires Bear or Dire Bear Form.",
    "druid_wild_growth": "Blankets the party in rapid healing that fades as it winds down. Heals up to 5 allies over 3 turns.",
    "druid_swiftmend": "Consumes an active Rejuvenation on the target, instantly healing them for the remainder of that effect.",
    "druid_natures_swiftness": "Your next Nature spell becomes instant and costs no turn to cast.",
    "druid_insect_swarm": "Swarms the target with insects, dealing Nature damage over time.",
    "druid_starfall": "Calls down a rain of stars, dealing Arcane damage to all enemies over time.",
    "druid_typhoon": "A violent gust of wind blasts all enemies for Nature damage.",
    "druid_berserk": "Give in to feral rage, sharply increasing your Attack Power for a short time.",
    "druid_ravage": "A savage pounce that deals heavy damage. Requires Cat Form.",
    "druid_thorns": "Sheathes the target in thorns, increasing the damage they deal.",

    # --- Hunter ---
    "hunter_chimera_shot": "A powerful instant shot that strikes for heavy damage.",
    "hunter_explosive_shot": "Lodges an explosive charge in the target, dealing Fire damage over time.",
    "hunter_black_arrow": "Fires a black arrow that deals Shadow damage over time.",
    "hunter_disengage": "Break away from the fight, sharply reducing the damage you take for a short time.",
    "hunter_feign_death": "Play dead, heavily reducing the damage you take for a short time.",
    "hunter_aspect_of_the_wild": "Assume the Wild's aspect, granting Nature resistance and increased critical strike chance.",

    # --- Mage ---
    "mage_pyroblast": "A massive fiery boulder that deals devastating Fire damage.",
    "mage_ice_barrier": "Surrounds you with ice, absorbing incoming damage.",
    "mage_presence_of_mind": "Your next spell becomes instant and costs no turn to cast.",
    "mage_icy_veins": "Increases your casting speed for a short time.",
    "mage_combustion": "Your spells burn hotter, increasing Spell Critical Strike chance for a few turns.",
    "mage_cold_snap": "A shock of cold clears your mind, instantly resetting all of your ability cooldowns.",
    "mage_mana_shield": "Wraps you in raw mana, reducing the damage you take for a short time.",
    "mage_counterspell": "Disrupts the target's concentration, heavily reducing their spell hit chance for 1 turn.",

    # --- Paladin ---
    "paladin_holy_shock": "Blasts an ally with Holy energy, healing them instantly.",
    "paladin_avengers_shield": "Hurls a holy shield at the target, dealing Holy damage.",
    "paladin_divine_storm": "An instant weapon attack against all nearby enemies.",
    "paladin_redemption": "Calls on the Light to pull an ally back from the brink, restoring a great deal of health.",
    "paladin_seal_of_command": "Your melee attacks have a chance to deal a burst of Holy damage. Judgement consumes this Seal for a heavy detonation.",

    # --- Priest ---
    "priest_penance": "A focused beam of Holy light that heals an ally for a large amount.",
    "priest_circle_of_healing": "Instantly heals your entire party.",
    "priest_shadowform": "Shapeshift into Shadowform, increasing your Spell Power against Shadow damage.",
    "priest_silence": "Silences the target's mind, heavily reducing their spell hit chance for 1 turn.",
    "priest_mind_flay": "Assaults the target's mind, dealing Shadow damage over time.",
    "priest_vampiric_touch": "Afflicts the target with a Shadow damage-over-time effect.",
    "priest_mind_sear": "A wave of shadow energy damages all enemies over time.",
    "priest_fade": "Fade from notice, reducing the damage you take for a short time.",

    # --- Primalist ---
    "primalist_geode_barrage": "Fling stones at an enemy, dealing Physical damage and generating Rage. Shares a cooldown with other Seismic spells.",
    "primalist_seismic_crash": "Create stalactites that strike your enemy 3 times, generating Rage. Shares a cooldown with other Seismic spells.",
    "primalist_stoneshard": "Launch a sharpened stone at an enemy. Deals additional damage per Earthshaping stack.",
    "primalist_seismic_tremor": "Send an escalating tremor through the earth at an enemy. Shares a cooldown with other Seismic spells.",
    "primalist_terrasurge": "Unleash a globe of earth at an enemy, piercing defensive effects and reducing their Armor.",
    "primalist_primal_shred": "Command your pet to shred nearby enemies, causing them to bleed.",
    "primalist_bring_me_their_bones": "A devastating execute against a heavily wounded enemy.",

    # --- Rogue ---
    "rogue_evasion": "Your dodge chance increases sharply for a short time.",
    "rogue_adrenaline_rush": "Doubles your Energy regeneration for a short time.",
    "rogue_mutilate": "A vicious double-dagger strike. Requires daggers in both hands.",
    "rogue_cold_blood": "Your next attack is guaranteed to critically strike.",
    "rogue_hemorrhage": "A vicious strike that deals damage and causes the target to bleed.",
    "rogue_shadow_dance": "Step into the shadows, sharply increasing your Physical Critical Strike chance for a short time.",
    "rogue_kick": "A sharp kick that disrupts the target, heavily reducing their spell hit chance for 1 turn.",
    "rogue_feint": "A feinting strike that draws attention away, reducing the damage you take for a short time.",
    "rogue_vanish": "Vanish from sight, drastically reducing the damage you take for a short time.",

    # --- Shaman ---
    "shaman_stormstrike": "Instantly attacks with both weapons, weakening the target's Nature resistance so your next Nature hits land harder.",
    "shaman_elemental_mastery_cast": "Your next Lightning Bolt, Chain Lightning or Lava Burst becomes instant and costs no turn to cast.",
    "shaman_thunderstorm": "Calls down lightning, damaging all nearby enemies and restoring some of your Mana.",
    "shaman_feral_spirit": "Calls on the spirit wolves, sharply increasing your Attack Power for a short time.",
    "shaman_natures_swiftness": "Your next healing spell becomes instant and costs no turn to cast.",
    "shaman_riptide": "Heals the target immediately and again over time.",
    "shaman_mana_tide_totem": "Calls the tides to restore your focus, increasing your Spirit for a short time.",
    "shaman_earth_shield": "Shields the target with earth, healing them whenever they take damage.",
    "shaman_cleanse_spirit": "Removes one Curse effect from the target.",
    "shaman_strength_of_earth_totem": "Earth totem. Increases Strength and Agility for your party.",
    "shaman_searing_totem": "Fire totem. Sears the target, dealing Fire damage over time.",
    "shaman_mana_spring_totem": "Water totem. Increases maximum Mana for your party.",
    "shaman_call_of_ancestors": "Casts your entire saved totem loadout - up to one totem per element - in a single action.",
    "shaman_water_shield": "Surrounds you with water, increasing your maximum Mana.",
    "shaman_earthbind_totem": "Earth totem. Binds the target to the earth, reducing their Haste.",
    "shaman_reincarnation": "Calls on the ancestors for one more breath, restoring a great deal of health.",
    "shaman_stoneclaw_totem": "Earth totem. Shields the caster, absorbing a burst of damage.",
    "shaman_magma_totem": "Fire totem. Deals Fire damage to all nearby enemies.",
    "shaman_grounding_totem": "Air totem. Grounds incoming magic, sharply increasing your Magic Resistance for a moment.",
    "shaman_stoneskin_totem": "Earth totem. Increases Armor for your party.",
    "shaman_shamanistic_rage": "Reduces all damage taken by 30% and gives your melee attacks a chance to restore Mana, for a short time.",
    "shaman_fire_resistance_totem": "Fire totem. Grants your party a large Fire resistance bonus.",
    "shaman_frost_resistance_totem": "Frost totem. Grants your party a large Frost resistance bonus.",
    "shaman_nature_resistance_totem": "Earth totem. Grants your party a large Nature resistance bonus.",

    # --- Stormbringer ---
    "stormbringer_freewind": "A line of wind and lightning tears through all enemies.",

    # --- Warlock ---
    "warlock_unstable_affliction": "Afflicts the target with an unstable curse dealing Shadow damage over time.",
    "warlock_shadowburn": "Deals Shadow damage, striking far harder against targets below 20% health.",
    "warlock_dark_pact": "Draws on dark power to instantly restore a portion of your Mana.",
    "warlock_metamorphosis": "Take on a demonic shape, increasing your Attack Power and Armor for a short time.",
    "warlock_conflagrate": "Sets the target ablaze for a burst of Fire damage.",
    "warlock_chaos_bolt": "Deals massive Chaos damage that cannot be resisted.",

    # --- Warrior ---
    "warrior_mortal_strike": "A vicious strike that deals heavy weapon damage and wounds the target.",
    "warrior_bladestorm": "A whirling storm of steel, striking all nearby enemies.",
    "warrior_devastate": "A punishing blow that deals heavy weapon damage.",
    "warrior_concussion_blow": "A stunning blow to the head that deals heavy damage.",
    "warrior_shockwave": "A wave of force deals damage to all enemies in front of you.",
    "warrior_bloodthirst": "Instantly attacks the target based on your Attack Power.",
    "warrior_pummel": "A brutal pummel that disrupts the target, heavily reducing their spell hit chance for 1 turn.",
}


def main():
    apply = "--apply" in sys.argv
    seen, changed = set(), 0
    for path in sorted(glob.glob(os.path.join(ROOT, "data/abilities/*.json"))):
        data = json.load(open(path))
        items = data if isinstance(data, list) else data.get("abilities", data)
        seq = items if isinstance(items, list) else list(items.values())
        dirty = False
        for a in seq:
            if not isinstance(a, dict):
                continue
            aid = a.get("ability_id")
            if aid not in DESCRIPTIONS:
                continue
            seen.add(aid)
            old = a.get("description") or ""
            new = DESCRIPTIONS[aid]
            if old == new:
                continue
            changed += 1
            if apply:
                a["description"] = new
                if old and old not in (a.get("_design_note") or ""):
                    prev = a.get("_design_note")
                    a["_design_note"] = (prev + " " + old).strip() if prev else old
                dirty = True
            else:
                print(f"--- {aid}\n  OLD: {old[:110]}...\n  NEW: {new}\n")
        if apply and dirty:
            with open(path, "w") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
                fh.write("\n")

    missing = sorted(set(DESCRIPTIONS) - seen)
    print(f"{'rewrote' if apply else 'would rewrite'} {changed} descriptions")
    if missing:
        print(f"!! {len(missing)} ids in the table matched no ability: {missing}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
