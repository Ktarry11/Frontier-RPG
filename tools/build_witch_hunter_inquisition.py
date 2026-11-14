#!/usr/bin/env python3
"""Rebuild Witch Hunter's Inquisition tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_witch_hunter_inquisition.py [--check]

SOURCE: data/reference/coa/witch-hunter.json - 39 real Inquisition talents
from Ascension's own CoA Builder payload. Role: DPS.

The shipped tree was 23 nodes with ONE proc and 20 bare numbers, several of
them pointed at the right abilities with the wrong mechanic ("Dawn" as
+8% Torchlight damage, when CoA's Dawn is a stacking buff off Fire damage).

THIS IS THE MOST FAITHFUL TREE IN THE REBUILD SO FAR, because the abilities
are all here. Frontier has Dawn Blade, Dusk Blade, Purifier's Edge, Fiery
Judgement, Torchlight, Stake, Flourish, Hunt, Smite Evil, Pyro Tonic and
Darkslayer's Lantern - every ability this spec's talents name except
Sixfold Shot, whose CoA description in this export is a broken template
reference anyway. So almost nothing had to be re-pointed.

WHAT THE SPEC IS. Dual-wielding Fire and Holy, built on three stacking
things:
  FLAMES OF SIN - a self buff Dawn Blade grants and that Purifier's Edge,
    Fiery Judgement, Stake, Torchlight and Flourish all extend. CoA's
    version adds Fire damage to your auto attacks.
  DAWN and DUSK - Fire damage stacks Dawn, Physical damage stacks Dusk,
    and each empowers the opposite half of the kit.
  PURITY and WICKEDNESS - main-hand and off-hand auto attacks stack
    different debuffs on the target.

DAWN AND DUSK CANNOT KEY OFF DAMAGE SCHOOL, and this was worth finding out
before authoring rather than after. proc["school"] only types a damage_flat
payload (combat/status_effects.py:1190) and there is NO trigger-side school
filter anywhere in the engine - on_damage_cast cannot be narrowed to Fire
or Physical. So Dawn and Dusk are filtered by ABILITY instead, split along
the same line CoA splits them: the Fire abilities feed Dawn, the physical
ones feed Dusk. Same effect, reached by a gate that exists.

CONVENTIONS, which do not agree with each other:
  agility_pct, armor_penetration_pct, attack_power_pct   percentage POINTS
  crit_chance_physical, ability_*_crit, haste            PERCENT
  all_damage, fire_spell_damage, ability_*_crit_damage   FRACTION
  damage_dealt_pct in a status effect                    percentage POINTS
  <target>_from_<source>_pct      FRACTION, listed pairs only
  *_cost_pct / *_cooldown_pct     FRACTION, POSITIVE MEANS A REDUCTION

WHAT IS NOT BUILDABLE, stated per node:
  - Off-hand weapons are not a separate damage source, so Brooding
    Hatred's "+20% off-hand damage" and Brushin' Off The Dusk's "off-hand
    auto attacks strike 2 additional times" have nothing to attach to, and
    Purity & Wickedness cannot tell the two hands apart.
  - "expertise" is read by no engine code (Refined Combatant).
  - Health-gated damage and crit. Burned Alive's below-20% crit bonus,
    Evil Doers Beware's above-75% guarantee and Stake's own below-35%
    requirement are all recipient-health conditions on damage, and the
    engine's only recipient-health key is heal-side.
  - A buff cannot make another ability free or usable (Lightbringer,
    Heartstopper): ability cost keys are read only through
    get_talent_effects(), which never includes status effects.
  - Nothing reads another effect's stack count, so Cycle of Despair's
    "reaching 20 stacks with both buffs consumes them" has no hook, and
    Sin Eater cannot add charges to a sibling node's payload.
  - No party auras (Monster Hunting).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/witch_hunter_inquisition.json"

#: What CoA treats as this spec's Fire abilities - they grant or extend
#: Flames of Sin and they feed Dawn.
FIRE_KIT = ["witch_hunter_purifiers_edge", "witch_hunter_fiery_judgement",
            "witch_hunter_torchlight", "witch_hunter_flourish",
            "witch_hunter_dawn_blade"]

#: The physical half, which feeds Dusk.
PHYSICAL_KIT = ["witch_hunter_stake", "witch_hunter_dusk_blade",
                "witch_hunter_pommel_smash", "witch_hunter_guard_strike"]

#: Flames of Sin. CoA: "Using Dawn Blade now grants you Flames of Sin for 3
#: sec, causing your auto attacks to deal an additional 30% of the damage
#: dealt as Fire damage." Built as a damage buff rather than an auto-attack
#: rider, since no key adds a school's damage to weapon swings.
FLAMES_OF_SIN = {
    "effect_id": "witch_hunter_flames_of_sin", "name": "Flames of Sin",
    "effect_type": "buff", "duration": 2, "max_stacks": 1,
    "stat_mods": {"damage_dealt_pct": 15.0},
    "on_target": False, "real_time_seconds": None,
}

TREE = {
    "spec_name": "Witch Hunter Inquisition",
    "tree_id": "witch_hunter_inquisition",
    "description": ("Blade in each hand and both of them burning - keeps "
                    "the fire lit and feeds it everything."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from data/reference/coa/witch-hunter.json "
        "(39 real CoA Inquisition talents, role DPS). Replaces a 23-node "
        "tree with 1 proc and 20 bare numbers. The most faithful rebuild so "
        "far, because Frontier already has every ability these talents name "
        "except Sixfold Shot - Dawn Blade, Dusk Blade, Purifier's Edge, "
        "Fiery Judgement, Torchlight, Stake, Flourish, Hunt, Smite Evil, "
        "Pyro Tonic and Darkslayer's Lantern are all present, so almost "
        "nothing had to be re-pointed. Dawn and Dusk are filtered by "
        "ability rather than by damage school, because the engine has no "
        "trigger-side school filter. Every CoA reference to Rage is "
        "translated to Focus."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"witch_hunter_inquisition_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"witch_hunter_inquisition_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "flames_of_sin", "Flames of Sin",
    "Dawn Blade sets your blades alight, increasing your damage by 15% for "
    "2 turns.",
    0, -5,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_dawn_blade"],
          "apply_effect": dict(FLAMES_OF_SIN)},
    connect=["purifiers_edge_training"],
    source="CoA's level 10 passive, and the thing the whole tree is built "
           "around: 'Using Dawn Blade now grants you Flames of Sin for 3 sec, "
           "causing your auto attacks to deal an additional 30% of the damage "
           "dealt as Fire damage.' No key adds a school's damage to weapon "
           "swings, so it is a general damage buff instead - 15% rather than "
           "30%, because CoA's applies only to autos and this applies to "
           "everything. 3 sec is 2 turns. The old tree had no form of this at "
           "all."))

N.append(node(
    "sermon_of_flame", "Sermon of Flame",
    "Increases your Fire spell damage by up to 10%.",
    0, -3,
    effects={"fire_spell_damage": 0.10},
    connect=["purifiers_edge_training"],
    source="CoA verbatim over 2 ranks: 'Increases your Fire damage dealt by "
           "5%.' Authored as the full-investment ceiling at one rank and left "
           "to the rank policy. fire_spell_damage is a <school>_spell_damage "
           "key the engine builds by interpolation, so it is live."))

N.append(node(
    "flexible_fighter", "Flexible Fighter",
    "Increases your Agility by 6%.",
    0, -1,
    effects={"agility_pct": 6.0},
    connect=["malice"],
    source="CoA verbatim. agility_pct takes percentage POINTS - the previous "
           "tree had 2.0 per rank over 5 ranks, which is 10% and overshot "
           "CoA."))

N.append(node(
    "brooding_hatred", "Brooding Hatred",
    "Increases your attack power by up to 10% and your chance to hit by up "
    "to 6%.",
    0, 1,
    effects={"attack_power_pct": 10.0, "hit_rating": 6.0},
    connect=["malice"],
    source="CoA over 2 ranks: 'Increases your off-hand Weapon Damage by 20% "
           "and increases your chance to hit by 3%.' Off-hand damage is not a "
           "separate source in this engine - there is no off-hand key at all - "
           "so that half becomes attack power, which is what a dual-wielder "
           "gets out of it. Hit is CoA's, doubled for the 2 ranks."))

N.append(node(
    "refined_combatant", "Refined Combatant",
    "Increases your physical critical strike chance by 3%.",
    0, 3,
    effects={"crit_chance_physical": 3.0},
    connect=["holy_frenzy"],
    source="CoA: 'Increases your expertise by 10.' 'expertise' is read by no "
           "engine code, so authoring it would have been a dead key - the "
           "same finding as Primalist's Raptor Talons and Mountain King's "
           "Tilling the Earth. Rerouted to crit, which is the melee stat this "
           "tier is otherwise missing."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "purifiers_edge_training", "Searing Hilt",
    "Purifier's Edge quickens you, increasing your haste by 10% for 2 turns, "
    "and relights Flames of Sin.",
    1, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_purifiers_edge"],
          "apply_effect": [
              {"effect_id": "witch_hunter_searing_hilt",
               "name": "Searing Hilt", "effect_type": "buff",
               "duration": 2, "max_stacks": 1,
               "stat_mods": {"haste": 10.0}, "on_target": False},
              dict(FLAMES_OF_SIN)]},
    connect=["dawn"],
    source="CoA: 'Purifier's Edge now grants you Searing Hilt for 10 sec. "
           "Searing Hilt: Increases your melee attack speed by 10% for 10 "
           "sec.' Attack speed is haste here. The second half of this node is "
           "CoA's Purifier's Edge itself - 'Grants Flames of Sin or increases "
           "the duration by 3 sec' - which is why apply_effect takes a LIST: "
           "one roll lands a buff on the Witch Hunter and relights the "
           "spec's core buff at the same time. Extending a duration is not a "
           "payload, so re-applying is how the extension is expressed."))

N.append(node(
    "malice", "Malice",
    "Increases your Fire spell damage by 50% of your Agility and your attack "
    "power by 100% of your Intellect.",
    1, -2,
    effects={"spell_power_from_agility_pct": 0.50,
             "attack_power_from_intellect_pct": 1.00},
    connect=["dusk"],
    source="CoA verbatim: 'Level 30 Passive. Increases your Fire spell damage "
           "by 50% of your Agility and your attack power by 100% of your "
           "Intellect.' Both pairings are live. The SCHOOL half is dropped "
           "rather than faked: there is no per-school spell power in this "
           "engine, only spell_power, and fire_spell_power is not in "
           "STAT_CONVERSION_TARGETS - the same thing Tinker's Bomb Squad ran "
           "into. Previous tree had 0.03 per rank over 3 ranks, i.e. 9% "
           "against CoA's 50%."))

N.append(node(
    "holy_frenzy", "Holy Frenzy",
    "Increases your haste by 15%.",
    1, 0,
    effects={"haste": 15.0},
    connect=["interrogator"],
    source="CoA verbatim: 'Increases your melee haste by 15%.'"))

N.append(node(
    "protector_of_darkshire", "Protector of Darkshire",
    "Increases the damage of Dawn Blade and Dusk Blade by 15%.",
    1, 2,
    effects={"ability_witch_hunter_dawn_blade_damage": 0.15,
             "ability_witch_hunter_dusk_blade_damage": 0.15},
    connect=["interrogator"],
    source="CoA verbatim, and already a scalar in CoA, so it stays one. These "
           "are the two abilities Dawn and Dusk pay off into."))

N.append(node(
    "the_hunt_continues", "The Hunt Continues",
    "Hunt returns 35 Focus and costs 15% less.",
    1, 4,
    effects={"ability_witch_hunter_hunt_cost_pct": 0.15},
    proc={"trigger": "on_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_hunt"],
          "grant_resource": {"resource": "focus", "amount": 35}},
    connect=["scarlet_inquisitor"],
    source="CoA: 'Hunt now generates an additional 15 Rage and the mana cost "
           "is reduced by -15%.' Rage -> Focus, and CoA's base Hunt already "
           "generates 20, so the total it describes is 35 - built as the full "
           "35 on this node, since Frontier's Hunt has no generation of its "
           "own to add to. on_cast rather than on_damage_cast: Hunt is a "
           "charge that slows, and filtering a damage trigger to it would "
           "have been a proc that never fired. Also carries CoA's Evil Never "
           "Sleeps, which extends Hunt's slow - movement does not exist."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "dawn", "Dawn",
    "Your Fire abilities stoke the dawn, increasing your damage by 2% per "
    "stack for 2 turns, stacking 10 times.",
    2, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": FIRE_KIT,
          "apply_effect": {"effect_id": "witch_hunter_dawn",
                           "name": "Dawn", "effect_type": "buff",
                           "duration": 2, "max_stacks": 10,
                           "stat_mods": {"damage_dealt_pct": 2.0},
                           "on_target": False}},
    connect=["fiery_judgement_mastery"],
    source="CoA: 'Dealing Fire damage now increases the damage dealt by "
           "Torchlight and Dusk Blade by 2% for 5 seconds, stacking 10 "
           "times.' Two departures, both forced. The TRIGGER cannot be 'Fire "
           "damage' - proc['school'] only types a damage_flat payload "
           "(status_effects.py:1190) and no trigger-side school filter exists "
           "- so it is filtered to this spec's Fire abilities instead, which "
           "is the same set CoA means. And the PAYOFF cannot be two named "
           "abilities, because ability_*_damage is read only through "
           "get_talent_effects() and a status effect cannot reach it, so it "
           "is general damage. CoA's 2% and 10 stacks kept; 5 sec is 2 turns. "
           "Was ability_witch_hunter_torchlight_damage +8%, a flat number "
           "with no stacking at all."))

N.append(node(
    "dusk", "Dusk",
    "Your physical strikes gather the dusk, increasing your damage by 2% per "
    "stack for 2 turns, stacking 10 times.",
    2, -2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": PHYSICAL_KIT,
          "apply_effect": {"effect_id": "witch_hunter_dusk",
                           "name": "Dusk", "effect_type": "buff",
                           "duration": 2, "max_stacks": 10,
                           "stat_mods": {"damage_dealt_pct": 2.0},
                           "on_target": False}},
    connect=["fiery_judgement_mastery"],
    source="CoA: 'Dealing Physical damage now increases the damage dealt by "
           "Stake and Dawn Blade by 2% for 5 seconds, stacking 10 times.' The "
           "mirror of Dawn and translated the same way, filtered to the "
           "physical half of the kit. Keeping the pair as two separate nodes "
           "matters: CoA's design is that you alternate Fire and physical to "
           "hold both, and collapsing them into one buff would have removed "
           "the only reason to."))

N.append(node(
    "interrogator", "Interrogator",
    "Dawn Blade leaves the target burning for 3 turns.",
    2, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_dawn_blade"],
          "apply_effect": {"effect_id": "witch_hunter_interrogator_burn",
                           "name": "Interrogation", "effect_type": "dot",
                           "duration": 3, "potency": 35,
                           "damage_school": "fire", "on_target": True}},
    connect=["cinder_and_ashes"],
    source="CoA: 'Level 20 Passive. Damage dealt by Dawn Blade now deals an "
           "additional 100% of the damage dealt over 10 sec as Fire damage.' "
           "A proc-applied dot takes a flat potency - there is no "
           "'percentage of the triggering hit' form for apply_effect, unlike "
           "shield_pct and splash_damage - so 100% of a Dawn Blade is "
           "approximated at 35 per turn over 3 turns. Was fire_dot_damage "
           "+4%, which scaled dots this spec did not have."))

N.append(node(
    "cinder_and_ashes", "Cinder and Ashes",
    "Increases the damage of Purifier's Edge and Fiery Judgement by 25%.",
    2, 2,
    effects={"ability_witch_hunter_purifiers_edge_damage": 0.25,
             "ability_witch_hunter_fiery_judgement_damage": 0.25},
    connect=["sinner"],
    source="CoA: 'Increases the spell power scaling of Purifier's Edge and "
           "Fiery Judgement by 25%.' There is no key for how much an ability "
           "scales with spell power - the coefficients live on the abilities "
           "themselves - so this is expressed as damage, which is what the "
           "scaling buys."))

N.append(node(
    "scarlet_inquisitor", "Scarlet Inquisitor",
    "Reduces the Focus cost of your Traps and Brands by 50%.",
    2, 4,
    effects={"ability_witch_hunter_inquisitors_trap_cost_pct": 0.50,
             "ability_witch_hunter_shadow_trap_cost_pct": 0.50,
             "ability_witch_hunter_death_trap_cost_pct": 0.50,
             "ability_witch_hunter_shadow_brand_cost_pct": 0.50},
    connect=["sinner"],
    source="CoA verbatim but for the resource: 'Reduces the mana cost of your "
           "Traps and Brands by -50%.' Written out per ability, since there is "
           "no key for a named group. POSITIVE reduces."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "fiery_judgement_mastery", "Fiery Judgement",
    "Fiery Judgement relights Flames of Sin and splashes 30% of its damage "
    "onto up to 5 enemies as fire.",
    3, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_fiery_judgement"],
          "splash_damage": {"pct": 0.30, "max_targets": 5, "school": "fire"},
          "apply_effect": dict(FLAMES_OF_SIN)},
    connect=["burned_alive"],
    source="CoA's Fiery Judgement: 'Judge an enemy, dealing Fire damage to "
           "them and nearby enemies. Grants Flames of Sin or increases the "
           "duration by 3 sec.' Both halves built - the splash is what "
           "'nearby enemies' means in an engine with no positions, and the "
           "relight is the same re-application Searing Hilt uses."))

N.append(node(
    "sinner", "Sinner",
    "Increases the damage of Torchlight by 100%.",
    3, -2,
    effects={"ability_witch_hunter_torchlight_damage": 1.00},
    connect=["burned_alive"],
    source="CoA verbatim: 'Increases the damage of Torchlight by 100%.' A "
           "doubling is a big scalar, and it is CoA's own number - Torchlight "
           "is cheap and its base damage is small. Previous tree had this at "
           "0.1 per rank over 3 ranks."))

N.append(node(
    "duskwood_renegade", "Duskwood Renegade",
    "Reduces the cooldown of Burrow Bolt by 40%.",
    3, 0,
    effects={"ability_witch_hunter_burrow_bolt_cooldown_pct": 0.40},
    connect=["torch_the_wicked"],
    source="CoA over 2 ranks: 'Reduces the cooldown of Burrow Bolt by -5 "
           "sec.' Expressed as a percentage because cooldowns are counted in "
           "turns here. The previous tree used the FLAT _cooldown key at 1 "
           "per rank, which is a different and much larger thing on a "
           "short-cooldown ability."))

N.append(node(
    "flames_of_the_sinned", "Flames of the Sinned",
    "Your Smite Evil has a 25% chance to strike again.",
    3, 2,
    proc={"trigger": "on_damage_cast", "chance": 25, "icd": 0,
          "ability_filter": ["witch_hunter_smite_evil"],
          "extra_attack": True},
    connect=["torch_the_wicked"],
    source="CoA: 'Your Smite Evil now has a 25% chance to strike again. While "
           "you have Flames of Sin active, the chance to trigger this effect "
           "is increased by 10%.' The conditional increase needs a 'while this "
           "buff is up' gate, which no proc has, so CoA's base 25% stands "
           "alone. extra_attack is the live payload."))

N.append(node(
    "stake_training", "Stake",
    "Stake relights Flames of Sin and ignores the target's armor.",
    3, 4,
    effects={"armor_penetration_pct": 15.0},
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_stake"],
          "apply_effect": dict(FLAMES_OF_SIN)},
    connect=["heartstopper"],
    source="CoA's Stake plus Hatred & Vitriol: 'Drive a stake through the "
           "chest of an injured enemy... ignoring enemy armor. Grants Flames "
           "of Sin.' and 'Damage dealt by Stake now ignores enemy armor and "
           "its critical strikes refund half of its cost.' Per-ability armor "
           "penetration is not a key - armor_penetration_pct is a character "
           "stat - so the 'ignores armor' half is the Witch Hunter's own "
           "penetration. The crit refund is dropped: 'half of its cost' needs "
           "to read an ability's cost at proc time, which grant_resource "
           "cannot do. Stake's own below-35%-health requirement lives on the "
           "ABILITY, not here."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "burned_alive", "Burned Alive",
    "Increases your physical critical strike chance by 8% and your critical "
    "strike damage by 15%.",
    4, -3,
    effects={"crit_chance_physical": 8.0, "crit_damage_physical": 0.15},
    connect=["purity_and_wickedness"],
    source="CoA: 'Increases your critical strike chance by 25% on enemies "
           "below 20% health.' A recipient-health condition on CRIT, and the "
           "engine's only recipient-health key is low_health_healing_pct, "
           "which is heal-side. So 25%-when-nearly-dead becomes 8% always "
           "plus crit damage - a smaller number that applies through the "
           "whole fight rather than a large one in its last seconds. Also "
           "carries CoA's Evil Doers Beware ('Stake is guaranteed to "
           "critically strike enemies above 75% health'), unbuildable for the "
           "same reason."))

N.append(node(
    "torch_the_wicked", "Torch the Wicked!",
    "Flames of Sin burning makes your strikes land faster, increasing your "
    "haste by 2% per stack for 2 turns, stacking 12 times.",
    4, -1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": FIRE_KIT,
          "apply_effect": {"effect_id": "witch_hunter_torch_the_wicked",
                           "name": "Torch the Wicked", "effect_type": "buff",
                           "duration": 2, "max_stacks": 12,
                           "stat_mods": {"haste": 2.0},
                           "on_target": False}},
    connect=["purity_and_wickedness"],
    source="CoA: 'Dealing damage with Flames of Sin now grants 2% attack "
           "speed, stacking up to 12 times for 6 seconds. Application of this "
           "effect does not refresh the duration. Additionally, Pyro Tonic "
           "now also resets the cooldown of Torchlight.' Flames of Sin here "
           "is a damage buff rather than a damage SOURCE, so there is no "
           "'damage dealt by it' to hang off - filtered to the Fire abilities "
           "that grant it instead. CoA's 2% and 12 stacks kept. The "
           "no-refresh rule and the Pyro Tonic rider are both dropped: "
           "re-application always refreshes here, and a proc cannot reset a "
           "cooldown off another ability's cast and also do this."))

N.append(node(
    "monster_hunting", "Monster Hunting",
    "Increases your haste by 10% and all damage you deal by 10%.",
    4, 1,
    effects={"haste": 10.0, "all_damage": 0.10},
    connect=["lightbringer"],
    source="CoA: 'Increases melee and ranged haste of party and raid members "
           "within 100 yds by 10%. Does not stack with similar effects. In "
           "addition, increases your damage dealt against Undead and Demons "
           "by 10%.' The raid aura has no mechanism and the creature-type "
           "condition has no key, so both halves land on the Witch Hunter "
           "unconditionally and the description says 'your'."))

N.append(node(
    "heartstopper", "Heartstopper",
    "Increases the critical strike chance of Stake by 30%.",
    4, 3,
    effects={"ability_witch_hunter_stake_crit": 30.0},
    connect=["lightbringer"],
    source="CoA: 'Level 40 Passive. Casting Purifier's Edge or Fiery "
           "Judgement now has a 30% chance to allow the use of Stake within 8 "
           "seconds regardless of the target's health percentage.' Nothing "
           "lifts an ability's own usability gate from a buff, so the "
           "unlocking half is not buildable. Rebuilt as making Stake hit "
           "harder when you do get to use it. ability_*_crit is a PERCENT."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "lightbringer", "Lightbringer",
    "Reduces the Focus cost of Purifier's Edge by 40%.",
    5, -3,
    effects={"ability_witch_hunter_purifiers_edge_cost_pct": 0.40},
    connect=["purity_and_wickedness"],
    source="CoA: 'Damage dealt by Dusk Blade now has a 15% chance to reduce "
           "the mana cost of your next Purifier's Edge by -100%. This effect "
           "has a 25% chance to not be consumed.' A chance at a free cast "
           "needs an ability cost key reachable from a status effect, and cost "
           "keys are read only through get_talent_effects(). Flattened into a "
           "permanent discount instead - 15% of 100% off, with a chance to "
           "persist, averages out near this - which is the honest version of "
           "the same saving."))

N.append(node(
    "cycle_of_despair", "Cycle of Despair",
    "Increases all damage you deal by 10% and your haste by 10%.",
    5, -1,
    effects={"all_damage": 0.10, "haste": 10.0},
    connect=["purity_and_wickedness"],
    source="CoA: 'Increases the amount of stacks of Dawn and Dusk by 10. In "
           "addition, reaching 20 stacks with both buffs will consume them to "
           "grant you 20% increased damage, melee haste, movement speed, and "
           "critical strike chance for 6 seconds.' Nothing reads another "
           "effect's stack count, so neither raising a sibling node's "
           "max_stacks nor detecting 20-and-20 is buildable - the same limit "
           "Geomancy's Earthshaping payoffs and Mountain King's Call of the "
           "Mountain hit. The payout is granted permanently at half CoA's "
           "value, since CoA's is a burst you have to earn twice over."))

N.append(node(
    "brushin_off_the_dusk", "Brushin' Off The Dusk",
    "Your physical strikes have a 10% chance to strike again.",
    5, 1,
    proc={"trigger": "on_damage_cast", "chance": 10, "icd": 0,
          "ability_filter": PHYSICAL_KIT,
          "extra_attack": True},
    connect=["purity_and_wickedness"],
    source="CoA over 2 ranks: 'Your off-hand auto attacks now have a 10% "
           "chance to strike 2 additional times.' Off-hand autos are not a "
           "thing a talent can reach - there is no off-hand key and no "
           "auto-attack-hand distinction - so it is filtered to the physical "
           "abilities instead, which is the closest set. 'Strike 2 additional "
           "times' is one extra_attack: the payload is a boolean, not a "
           "count."))

N.append(node(
    "pyro_tonic", "Pyro Tonic",
    "Increases your Fire spell damage by 20% and your critical strike damage "
    "by 10%.",
    5, 3,
    effects={"fire_spell_damage": 0.20, "crit_damage_physical": 0.10},
    connect=["purity_and_wickedness"],
    source="CoA: '2 min cooldown. Drink a fiery tonic, increasing your Fire "
           "damage dealt by 20% and your critical damage by 10% for 15 sec.' "
           "Frontier HAS a witch_hunter_pyro_tonic ability, so this node is "
           "not its unlock - no Witch Hunter ability carries requires_talent, "
           "so the whole class is learned by level. Built as the passive "
           "version of the same two numbers, since a 2-minute cooldown is not "
           "a shape this tree has."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "purity_and_wickedness", "Purity & Wickedness",
    "Your strikes mark the target, making it take 2% more damage per stack "
    "for 3 turns, stacking 6 times.",
    6, 0,
    proc={"trigger": "on_weapon_swing", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "witch_hunter_purity",
                           "name": "Purity & Wickedness",
                           "effect_type": "debuff", "duration": 3,
                           "max_stacks": 6,
                           "stat_mods": {"damage_taken_pct": 0.02},
                           "on_target": True}},
    source="CoA: 'Main-hand auto attacks now apply a stack of Purity to the "
           "target, increasing the Fire and Holy damage you deal to them by "
           "2% per stack, stacking 6 times. Off-hand auto attacks now apply a "
           "stack of Wickedness... increasing the Shadow and Physical damage "
           "you deal to them by 2% per stack.' The two-hand split is not "
           "buildable - nothing distinguishes main-hand from off-hand - so "
           "the two debuffs collapse into one, which is also why the node "
           "keeps both names. Per-school recipient keys exist "
           "(<school>_damage_taken_pct) but there is no 'Fire and Holy "
           "together' form, so it is damage_taken_pct: all schools, which is "
           "what holding both stacks would have meant anyway. NOTE the unit - "
           "damage_taken_pct is the ONE status stat_mod read RAW rather than "
           "divided by 100, so 2% is 0.02 here while the "
           "physical_/magic_ variants beside it would be 2.0. Torchlight's "
           "stack consumption is dropped: nothing reads another effect's "
           "stacks."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. tools/talent_ranks.py rescales so a ranked
# node lands on exactly the ceiling it had at one rank. The capstone stays a
# single pick; there are no unlock nodes, since no Witch Hunter ability
# carries requires_talent.
from tools.talent_ranks import rankable, spread  # noqa: E402

for _n in TREE["nodes"]:
    if _n["max_points"] < 3 and _n["tier"] < 6 and rankable(_n):
        spread(_n, 3)


def main():
    check = "--check" in sys.argv
    ids = [n["talent_id"] for n in TREE["nodes"]]
    assert len(ids) == len(set(ids)), "duplicate talent_id"
    names = [n["name"] for n in TREE["nodes"]]
    assert len(names) == len(set(names)), "duplicate node NAME"
    for n in TREE["nodes"]:
        for c in n["connected_to"]:
            assert c in ids, f"{n['talent_id']} connects to unknown {c}"
    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Witch Hunter Inquisition: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
