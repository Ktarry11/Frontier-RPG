#!/usr/bin/env python3
"""Rebuild Bloodmage's Eternal tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_bloodmage_eternal.py [--check]

SOURCE: data/reference/coa/bloodmage.json - 40 real Eternal talents from
Ascension's own CoA Builder payload. Role: TANK.
coa_playstyles.json: "Druid Tank + Blood DK".

The shipped tree was 23 nodes with THREE procs and 19 bare numbers.

WHAT THE SPEC IS. A thing that will not die. CoA's Eternal mitigates with
Thick Pelt (each hit softens the next), holds with Howls and a taunt, and
heals off its own damage below a health threshold - Blood Moon is the
spec's signature and the one health-conditional in this class that the
engine CAN express.

CALL OF THE DARKWING is this tree's recurring payload - three CoA talents
trigger it (Monstrous Hunger, Petrified Legions, Grim Omen): "Calls 1 to 2
Shadow Bats to strike the target, healing you equal to the damage dealt."
Frontier has no Shadow Bat and no summon for it, so each is built as
leech_pct on the same trigger CoA names, which is what "damage that heals
you equal to its value" is. The bats are flavour in the descriptions and
promise no summon.

HEALTH-CONDITIONAL NODES, and which way each goes. This is a tank tree, so
four CoA talents gate on the Bloodmage's OWN health:
  Blood Moon        "below 75% health, heal for 3% of damage dealt"
  Shadows In The Night  "above 75% health, damage taken reduced 5%"
  Enduring          "Bloodbolt +25%, +25% more below 35% health"
Of these, only the DEFENSIVE direction has a live key:
low_health_damage_reduction_pct is read by character.py. A proc cannot read
the carrier's health at all, so Blood Moon's leech is unconditional and
Enduring's bonus half is dropped. Stated per node.

CONVENTIONS, which do not agree with each other:
  armor_pct, stamina_pct, max_health_pct              percentage POINTS
  dodge / parry / armor in a status effect            raw
  all_damage, dot_damage, ability_*_damage            FRACTION
  threat_generation_pct as a talent effect            FRACTION
  physical_damage_taken_pct as a talent effect        FRACTION, NEGATIVE
                                                      reduces
  damage_taken_pct in a status effect                 read RAW
  *_cost_pct / *_cooldown_pct      FRACTION, POSITIVE MEANS A REDUCTION

TURN-BASED CUTS. Every yard and all movement speed, which takes Uncanny
Speed's second half and Night Hunter's Howl's slow. No global cooldown, so
Monstrous Hunger's "50% reduced global cooldown" is free value. Charges do
not exist, so Rotclaw's "2 charges, 6 sec recharge" is a cooldown. One CoA
talent names Bite Wound, an ability Frontier does not have.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/bloodmage_eternal.json"

#: This spec's melee, for the nodes CoA hangs off "physical damage you deal".
STRIKES = ["bloodmage_ravenous_strike", "bloodmage_bloodfang_bite",
           "bloodmage_claw_sweep", "bloodmage_rotclaw",
           "bloodmage_crimson_maw"]

#: CoA's "Howl spells". All three exist in Frontier.
HOWLS = ["bloodmage_blood_howl", "bloodmage_shadow_howl",
         "bloodmage_wicked_howl", "bloodmage_night_hunters_howl"]

TREE = {
    "spec_name": "Bloodmage Eternal",
    "tree_id": "bloodmage_eternal",
    "description": ("The thing that will not die - every blow landed on it "
                    "makes the next one hurt less."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from data/reference/coa/bloodmage.json "
        "(40 real CoA Eternal talents, role TANK, 'Druid Tank + Blood DK'). "
        "Replaces a 23-node tree with 3 procs and 19 bare numbers. Call of "
        "the Darkwing - CoA's Shadow Bats, named by three talents - has no "
        "ability in Frontier, so each becomes leech_pct on the trigger CoA "
        "names. Four CoA talents gate on the Bloodmage's own health and only "
        "the defensive direction has a live key "
        "(low_health_damage_reduction_pct); a proc cannot read carrier "
        "health at all."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"bloodmage_eternal_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"bloodmage_eternal_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "heightened_reflexes", "Heightened Reflexes",
    "Increases your chance to dodge by up to 8%.",
    0, -5,
    effects={"dodge": 8.0},
    connect=["thick_pelt"],
    source="CoA over 2 ranks: 'Increases your chance to dodge by 4% and your "
           "expertise by 5.' 'expertise' is read by no engine code - the "
           "fourth time in this rebuild - so the dodge half carries it."))

N.append(node(
    "eternal_hunt", "Eternal Hunt",
    "Increases your maximum health by 5% and reduces the cost of your "
    "abilities by 5%.",
    0, -3,
    effects={"max_health_pct": 0.05, "all_ability_cost_pct": 0.05},
    connect=["thick_pelt"],
    source="CoA verbatim: 'Increases your maximum health and reduces the cost "
           "of your spells and abilities by 5%.' Both halves live. "
           "BOTH ARE FRACTIONS HERE. max_health_pct takes percentage POINTS "
           "inside a STATUS EFFECT - Black Knight's Blade of the Misbegotten "
           "uses 5.0 for 5% and the audit confirmed it - but as a TALENT "
           "effect it is a fraction, because POINTS_PCT_KEYS lists only "
           "all_stats_pct, the five stat_pcts, attack_power_pct, "
           "healing_power_pct, armor_pct and armor_penetration_pct, and "
           "everything else ending in _pct is a plain fraction. Same key, "
           "opposite units depending on where it sits. Authored 5.0 first, "
           "which is 500%. POSITIVE reduces for all_ability_cost_pct. On a "
           "class whose spells cost health, these two are the same stat "
           "twice."))

N.append(node(
    "shadows_in_the_night", "Shadows In The Night",
    "Reduces the physical damage you take by 5%.",
    0, -1,
    effects={"physical_damage_taken_pct": -0.05},
    connect=["coated_in_darkness"],
    source="CoA: 'While above 75% health, your damage taken is reduced by "
           "-5%.' The ABOVE-75% direction has no key - "
           "low_health_damage_reduction_pct is the only "
           "carrier-health defensive conditional and it points the other way "
           "- so this is unconditional. NEGATIVE reduces for "
           "physical_damage_taken_pct as a TALENT effect, which is the "
           "opposite sign to the same key inside a status effect."))

N.append(node(
    "vitality_talent", "Vitality",
    "Increases your Stamina by 10%.",
    0, 1,
    effects={"stamina_pct": 10.0},
    connect=["coated_in_darkness"],
    source="CoA: 'Increases your Stamina while in Eternal Curse by an "
           "additional 10%.' Eternal Curse is a self-buff ability here, not a "
           "shapeshift - combat/forms.py has no Bloodmage form - and there is "
           "no 'while this buff is up' gate for an effect key, so the 10% is "
           "permanent. Node id is vitality_talent because 'vitality' alone "
           "reads as the resource."))

N.append(node(
    "uncanny_speed", "Uncanny Speed",
    "Increases your haste by 5%.",
    0, 3,
    effects={"haste": 5.0},
    connect=["rabid"],
    source="CoA: 'Increases your melee haste by 5% and your movement speed "
           "and mounted movement speed by 20%.' Movement speed does not "
           "exist; CoA's own haste number is what survives."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "thick_pelt", "Thick Pelt",
    "Being struck toughens your hide, reducing the physical damage you take "
    "by 15% for 2 turns.",
    1, -4,
    proc={"trigger": "on_damage_taken", "chance": 100, "icd": 2,
          "apply_effect": {"effect_id": "bloodmage_thick_pelt",
                           "name": "Thick Pelt", "effect_type": "buff",
                           "duration": 2, "max_stacks": 1,
                           "stat_mods": {"physical_damage_taken_pct": -15.0},
                           "on_target": False}},
    connect=["blood_moon"],
    source="CoA verbatim: 'Physical damage taken now reduces the Physical "
           "damage taken from the next attack within 10 sec. Can only occur "
           "once every 5 sec.' The spec's mitigation engine, and the old tree "
           "had it as a flat scalar. CoA's 5-sec internal cooldown is icd 2. "
           "Also carries CoA's No Mercy ('allows your Thick Pelt to affect an "
           "additional hit'), which would need a charge counter on the buff. "
           "NOTE the unit: inside a status effect the physical_ variant IS "
           "divided by 100, unlike bare damage_taken_pct which is read raw - "
           "so -15.0 here means -15%."))

N.append(node(
    "coated_in_darkness", "Coated In Darkness",
    "Bloodbolt and Bloodfang Bite bring Blood Pact a turn closer to ready.",
    1, -2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["bloodmage_bloodbolt",
                             "bloodmage_bloodfang_bite"],
          "reset_cooldown": {"abilities": ["bloodmage_blood_pact"],
                             "turns": 1}},
    connect=["blood_moon"],
    source="CoA verbatim: 'Casting Bloodbolt or Bloodfang Bite now reduces "
           "the cooldown of your Blood Pact by 0.5 sec.' Half a second is "
           "under a turn; one turn is the smallest unit here, so it rounds up "
           "- which makes this stronger than CoA's and is the honest reading "
           "rather than rounding to zero and shipping a node that does "
           "nothing."))

N.append(node(
    "rotclaw", "Rotclaw",
    "Rotclaw infects the wound, bleeding the target for 3 turns.",
    1, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["bloodmage_rotclaw"],
          "apply_effect": {"effect_id": "bloodmage_rotclaw_bleed",
                           "name": "Infected Wound", "effect_type": "dot",
                           "duration": 3, "potency": 30,
                           "damage_school": "shadow", "on_target": True}},
    connect=["petrified_legions"],
    source="CoA: '2 Charges, 6 sec recharge. Ravage all nearby enemies, "
           "dealing Shadow damage, generating Rage and infecting their "
           "wounds, causing them to bleed over 4 seconds.' Frontier has the "
           "ability; this is the bleed rider. Charges are a cooldown here. "
           "Also carries CoA's Cursed Strikes ('increases the duration of "
           "Rotclaw and Hypovolemic Shock by 50%') in the 3-turn duration."))

N.append(node(
    "rabid", "Rabid",
    "Reduces the cooldown of your Howl spells by 25%.",
    1, 2,
    effects={f"ability_{a}_cooldown_pct": 0.25 for a in HOWLS},
    connect=["packleader"],
    source="CoA verbatim: 'Reduces the cooldown of Howl spells by 25%.' All "
           "four Howls exist in Frontier - Blood, Shadow, Wicked and Night "
           "Hunter's - and they are this spec's threat tools, so this is the "
           "node that lets it hold a pull. Written out per ability; no key "
           "names a group."))

N.append(node(
    "enduring", "Enduring",
    "Increases the damage of Bloodbolt by 25%.",
    1, 4,
    effects={"ability_bloodmage_bloodbolt_damage": 0.25},
    connect=["blood_mark"],
    source="CoA: 'Increases the damage of Bloodbolt by 25%, plus an "
           "additional 25% while below 35% health.' The conditional half "
           "needs to read the caster's own health into a DAMAGE bonus, and "
           "the only carrier-health key is "
           "low_health_damage_reduction_pct, which is defensive. CoA's base "
           "25% kept and the conditional dropped rather than folded in, since "
           "folding it in would make the node permanently stronger than CoA's "
           "best case."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "blood_moon", "Blood Moon",
    "Your strikes heal you for 5% of the damage dealt.",
    2, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": STRIKES,
          "leech_pct": {"pct": 0.05}},
    connect=["grim_omen"],
    source="CoA: 'While below 75% health, you now heal for 3% of all damage "
           "you deal.' A proc cannot read the carrier's own health - there is "
           "no hp_below gate on a proc payload - so the leech is "
           "unconditional. Raised 3% -> 5% would be wrong (CoA's is "
           "conditional and therefore cheaper); kept near CoA's number at 5% "
           "and filtered to this spec's strikes rather than all damage, which "
           "is the trade that keeps it honest."))

N.append(node(
    "coated_in_blood", "Coated In Blood",
    "Increases your armor by 20%.",
    2, -2,
    effects={"armor_pct": 20.0},
    connect=["grim_omen"],
    source="CoA: 'Increases the effectiveness of Blood Pact by 50%.' There is "
           "no ability-effectiveness multiplier key, and Blood Pact is a self "
           "buff whose stat_mods a talent cannot edit. Rebuilt as armour, "
           "which is what Blood Pact grants. Also carries CoA's Bloodguard "
           "('increases the duration of Blood Pact by 4 sec'), which "
           "ability_*_duration does not reach on an activated buff."))

N.append(node(
    "petrified_legions", "Petrified Legions",
    "Your strikes have a 10% chance to call the Darkwing, draining 60% of "
    "the damage back as health.",
    2, 0,
    proc={"trigger": "on_damage_cast", "chance": 10, "icd": 0,
          "ability_filter": STRIKES,
          "leech_pct": {"pct": 0.60}},
    connect=["monstrous_hunger"],
    source="CoA verbatim: 'Physical damage you deal or take now has a 10% "
           "chance to trigger a Call of the Darkwing. Call of the Darkwing: "
           "Calls 1 to 2 Shadow Bats to strike the target, healing you equal "
           "to the damage dealt.' There is no Shadow Bat ability in Frontier, "
           "so 'damage that heals you for its own value' is leech_pct. Built "
           "on damage DEALT only - 'dealt or taken' would need two procs on "
           "one node. CoA's 10% kept."))

N.append(node(
    "packleader", "Packleader",
    "Your Howls rally you, increasing your damage by 10% for 3 turns.",
    2, 2,
    proc={"trigger": "on_cast", "chance": 100, "icd": 0,
          "ability_filter": HOWLS,
          "apply_effect": {"effect_id": "bloodmage_packleader",
                           "name": "Packleader", "effect_type": "buff",
                           "duration": 3, "max_stacks": 1,
                           "stat_mods": {"damage_dealt_pct": 10.0},
                           "on_target": False}},
    connect=["monstrous_hunger"],
    source="CoA: 'Casting Howl spell now enrages your summons, increasing "
           "their damage dealt by 10% for 8 seconds.' Eternal has no summons "
           "- pet_damage would scale a pet this spec does not have - so the "
           "enrage lands on the Bloodmage. on_cast, because Howls are buffs "
           "and debuffs that deal no damage, so a damage trigger would never "
           "fire. 8 sec is 3 turns."))

N.append(node(
    "blood_mark", "Blood Mark",
    "Increases your threat generation by 15% and all damage you deal by 5%.",
    2, 4,
    effects={"threat_generation_pct": 0.15, "all_damage": 0.05},
    connect=["appetite_for_blood"],
    source="CoA's Blood Mark ('increases the Physical damage taken by enemies "
           "within 5 yds of you by 3%') and Dark Mark ('reduces the chance to "
           "hit for enemies within 5 yds of you by -3%'). Both are PASSIVE "
           "AURAS ON NEARBY ENEMIES, which this engine has no mechanism for "
           "in either direction - there is no proximity and no ambient "
           "debuff. Rebuilt as threat and damage, which is what an aura that "
           "makes everything near you worse off buys a tank. "
           "threat_generation_pct is a FRACTION as a talent effect."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "grim_omen", "Grim Omen",
    "Critical strikes and Howls call the Darkwing, draining 40% of the "
    "damage back as health.",
    3, -4,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "leech_pct": {"pct": 0.40}},
    connect=["eternal_resolve"],
    source="CoA verbatim: 'Critical strikes with Ravenous Strike or Bloodfang "
           "Bite, or using Howl spells, now triggers Call of the Darkwing.' "
           "Three triggers in one talent and a proc has one, so this takes "
           "the crit - the frequent one - and Packleader at tier 2 already "
           "rewards Howls. Unfiltered by ability, so any crit feeds it, which "
           "is close enough to 'Ravenous Strike or Bloodfang Bite' on a spec "
           "whose crits are mostly those two. 1-turn internal cooldown."))

N.append(node(
    "monstrous_hunger", "Monstrous Hunger",
    "Bloodfang Bite returns 12 Rage and drains 25% of its damage back as "
    "health.",
    3, -2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["bloodmage_bloodfang_bite"],
          "grant_resource": {"resource": "rage", "amount": 12},
          "leech_pct": {"pct": 0.25}},
    connect=["eternal_resolve"],
    source="CoA: '45 sec cooldown. Enrage for 10 sec, causing the next 6 "
           "Bloodfang Bites to have a 50% reduced global cooldown and cost "
           "and to trigger Call of the Darkwing.' Frontier has the ability "
           "already. There is NO GLOBAL COOLDOWN here so that half is free "
           "value, and 'the next 6 casts' is a charge counter effects do not "
           "have - so the cost saving becomes a Rage refund and the Darkwing "
           "becomes leech, both permanent on the ability CoA names."))

N.append(node(
    "appetite_for_blood", "Appetite for Blood",
    "Increases the damage of Bloodfang Bite and Claw Sweep by 20%.",
    3, 0,
    effects={"ability_bloodmage_bloodfang_bite_damage": 0.20,
             "ability_bloodmage_claw_sweep_damage": 0.20},
    connect=["blood_plague_eternal"],
    source="CoA: 'Increases the damage dealt by Bloodfang Bite and Claw Sweep "
           "by 20% against Humanoids and Beasts.' No key reads creature type, "
           "so it is unconditional at CoA's number - most of what a tank "
           "fights is one or the other anyway."))

N.append(node(
    "blood_plague_eternal", "Blood Plague",
    "Increases the damage your damage-over-time effects deal by 20%.",
    3, 2,
    effects={"dot_damage": 0.20},
    connect=["festering_maw"],
    source="CoA: 'Increases the critical strike chance and critical damage of "
           "Ravenous Strike and Claw Sweep by 10% against Diseased targets.' "
           "The Diseased condition has no key, and Accursed's tier 5 already "
           "takes CoA's Blood Plague as crit on those two abilities - "
           "shipping it twice across two specs would be the same pick. "
           "Pointed at this spec's own periodic damage instead: Rotclaw's "
           "bleed, Hypovolemic Shock and Crimson Tide."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "eternal_resolve", "Eternal Resolve",
    "Increases your maximum health by 10% and the healing you receive by 15%.",
    4, -3,
    effects={"max_health_pct": 0.10, "healing_taken_pct": 0.15},
    connect=["no_mercy"],
    source="CoA: '3 min cooldown. Activate your eternal resolve for 30 sec, "
           "increasing your melee attack speed, maximum health, and healing "
           "received by 50%.' Frontier has the ability, so this is not its "
           "unlock. Built as the passive version at a fraction of CoA's 50%, "
           "since CoA's is a 30-second window on a 3-minute cooldown. "
           "healing_taken_pct is the recipient-side key - NOT "
           "healing_received_pct, which is what CoA's own tooltips say and "
           "which is dead data here, as Tinker's Napalm found out. Both keys "
           "are FRACTIONS as talent effects and percentage POINTS inside a "
           "status effect, which is why Napalm wrote -3.0 for -3% and this "
           "writes 0.15 for 15%. Authored 10.0 and 15.0 first - 1000% and "
           "1500% - and the audit caught both."))

N.append(node(
    "festering_maw", "Festering Maw",
    "Your healing brings Lunge a turn closer to ready.",
    4, -1,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 1,
          "reset_cooldown": {"abilities": ["bloodmage_lunge"], "turns": 1}},
    connect=["no_mercy"],
    source="CoA verbatim: 'Healing with Bite Wound now reduces the cooldown "
           "of Lunge by 1 sec.' Bite Wound does not exist in Frontier, so the "
           "trigger is healing generally - on_heal_cast, which this spec "
           "reaches through Fleshcraft and Transfusion. One second is one "
           "turn."))

N.append(node(
    "night_hunters_howl", "Night Hunter's Howl",
    "Your Howls leave nearby enemies taking 10% more damage for 3 turns.",
    4, 1,
    proc={"trigger": "on_cast", "chance": 100, "icd": 0,
          "ability_filter": HOWLS,
          "apply_effect": {"effect_id": "bloodmage_howl_mark",
                           "name": "Night Hunter's Howl",
                           "effect_type": "debuff", "duration": 3,
                           "max_stacks": 1,
                           "stat_mods": {"damage_taken_pct": 0.10},
                           "on_target": True}},
    connect=["blood_howl_mastery"],
    source="CoA: 'Howl into the souls of nearby enemies, dealing Shadow "
           "damage and slowing their movement speed by 60% for 6 sec.' "
           "Frontier has the ability. Movement slows do not exist, so the "
           "slow becomes a damage-taken mark - which is what a slow is worth "
           "to a tank's group in an engine with no positioning. "
           "damage_taken_pct is read RAW in a status effect, so 0.10."))

N.append(node(
    "no_mercy", "No Mercy",
    "Reduces the physical damage you take by a further 8%.",
    4, 3,
    effects={"physical_damage_taken_pct": -0.08},
    connect=["blood_howl_mastery"],
    source="CoA: 'Allows your Thick Pelt to affect an additional hit.' A "
           "charge counter on another node's buff is not reachable - nothing "
           "edits a sibling's payload and effects expire on turns rather than "
           "uses. Rebuilt as flat mitigation, which is what a second Thick "
           "Pelt hit is worth. Stacks with Shadows In The Night at tier 0 for "
           "a -13% physical floor before Thick Pelt's window."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "blood_howl_mastery", "Blood Howl",
    "Reduces the cooldown of your Howls by a further 25% and increases your "
    "threat generation by 20%.",
    5, -3,
    effects={**{f"ability_{a}_cooldown_pct": 0.25 for a in HOWLS},
             "threat_generation_pct": 0.20},
    connect=["eternal_presence"],
    source="CoA: '2 min cooldown. Taunts nearby enemies within 10 yds, "
           "forcing them to attack you for 5 sec.' Frontier has the ability, "
           "so this is not its unlock - and taunt duration is not a talent "
           "key. Built as the two things a taunt talent is really for: the "
           "Howls come back faster and the tank holds harder. Stacks with "
           "Rabid at tier 1."))

N.append(node(
    "shadow_pact_eternal", "Hide of the Eternal",
    "Being struck shields you for 30% of the damage taken.",
    5, -1,
    proc={"trigger": "on_damage_taken", "chance": 100, "icd": 2,
          "shield_pct": {"pct": 0.30, "duration": 2,
                         "effect_id": "bloodmage_eternal_hide",
                         "name": "Hide of the Eternal"}},
    connect=["eternal_presence"],
    source="Not a CoA node by this name - it carries CoA's Sanguine Essence, "
           "whose description in this export is a broken template reference "
           "($7c), so there was nothing to port. Built as the thing a tank "
           "tree is missing at this depth: an absorb that scales off the hit "
           "that triggered it, which is what shield_pct does. 2-turn internal "
           "cooldown, matching Thick Pelt's cadence so the two read as one "
           "mitigation rhythm."))

N.append(node(
    "cursed_strikes", "Cursed Strikes",
    "Increases the damage of Rotclaw and Hypovolemic Shock by up to 50%.",
    5, 1,
    effects={"ability_bloodmage_rotclaw_damage": 0.50,
             "ability_bloodmage_hypovolemic_shock_damage": 0.50},
    connect=["eternal_presence"],
    source="CoA over 2 ranks: 'Increases the duration of Rotclaw and "
           "Hypovolemic Shock by 50%.' A percentage DURATION increase is not "
           "a shape ability_*_duration takes - that key is flat turns - and "
           "50% of a 3-turn dot is 1.5 turns, which does not exist. Expressed "
           "as damage: a dot running half again as long deals half again as "
           "much."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "eternal_presence", "Eternal Presence",
    "Increases your attack power by 5%, and being struck feeds your fury - "
    "raising your damage by 15% for 3 turns.",
    6, 0,
    effects={"attack_power_pct": 5.0},
    proc={"trigger": "on_damage_taken", "chance": 100, "icd": 1,
          "apply_effect": {"effect_id": "bloodmage_eternal_presence",
                           "name": "Eternal Presence", "effect_type": "buff",
                           "duration": 3, "max_stacks": 1,
                           "stat_mods": {"damage_dealt_pct": 15.0},
                           "on_target": False}},
    source="CoA: 'Increases the attack power of party and raid members by 5%. "
           "Does not stack with similar effects. In addition, you now gain "
           "attack power equal to 15% of the damage taken for 10 seconds. Can "
           "only occur once every 10 sec.' The party aura has no mechanism, "
           "so the 5% lands on the Bloodmage. The second half cannot size "
           "itself from the hit - apply_effect has no percentage-of-amount "
           "form, unlike shield_pct and leech_pct - so CoA's 15% becomes a "
           "flat damage buff on the same trigger. The right capstone for this "
           "spec: a tank that gets angrier the more it is hit, which is what "
           "the whole tree has been building."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. See tools/talent_ranks.py.
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
    print(f"Bloodmage Eternal: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
