#!/usr/bin/env python3
"""Rebuild Barbarian's Brutality tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_barbarian_brutality.py [--check]

SOURCE: data/reference/coa_worksheets/barbarian.md - 38 real Brutality
talents. Role: DPS (melee). Brutality was 23 nodes with 8 procs.
48 of Barbarian's 67 matched talents were pure scalars.

ENERGY IS THE WHOLE POOL AND CoA AGREES. Barbarian is
(ResourceType.ENERGY, None) at abilities.py:160 and CoA's Barbarian spends
Energy too - no second currency, unlike Felsworn's Energy/Felfury split or
Ranger's Focus/Advantage. So every CoA cost, refund and regeneration
talent in this tree lands on the pool it names. Three abilities generate
it (headhunters_spear 25, hodirs_wrath 40, savage_revelry 20).

THE EXECUTE GATE WAS ADDED TO MAKE THIS TREE WORK. CoA's Decapitate is
"Only usable on enemies below 35% health" and ours had no gate at all,
which left Overkill, Steelslinger and Beheader with nothing to key off.
execute_threshold_pct 35 was added to barbarian_decapitate on 6 Nov 2026 -
a real restriction on an ability players could previously use any time,
taken deliberately for CoA authenticity and recorded on the ability. The
other three classes with an execute (Reaper, Ranger, Felsworn) already
carried CoA's own numbers.

BRUTALITY THEREFORE OWNS low_health_threshold_pct FOR THE CLASS at 0.35,
matching Decapitate's gate. That key SUMS across talents and is UNSCALED,
and a character can spend in several trees, so Headhunting and Ancestry
inherit it. Enforced by tools/qa_summing_thresholds.py.

NOT BUILDABLE, each recorded on its node where one survives:
  - Whirling Assault and Skullseeker's "above 80% health" -
    high_health_damage_threshold_pct is dead data and there is no
    above-health conditional of any kind.
  - Born in Blood and everything keyed on it (Mounting Fury, Savage) -
    it is a CoA buff we do not have, and its stack count would be
    unreadable anyway.
  - Beheader ("scoring a kill blow refunds 100% of maximum Energy") -
    on_kill is a live trigger but grant_resource takes a FLAT amount with
    no percentage-of-maximum form, so it builds as a flat grant instead.
  - Reckful ("30% chance to not trigger a cooldown") - nothing intercepts
    a cooldown being set, only resets one after the fact.
  - Hail of Hammers and Storm of Steel's channel - no cast times, no
    channelling.
  - Battering Ram's two-handed gate and Body Builder's
    "when Strength is lower than Agility" - nothing reads weapon type or
    compares two of the caster's own stats.
  - Utter Devastation's consumable guaranteed crit - no guaranteed-crit
    key and no consumable buff state.
  - Steel Fury's per-strike ramp and Maximum Carnage's spinning channel.
  - Symbol of the Warspear's party attack power - a talent effect can
    never reach an ally, and Barbarian has no "Symbol" ABILITY to modify
    (unlike Ancestry, where eight party abilities already exist).
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/barbarian_brutality.json"

TREE = {
    "spec_name": "Barbarian Brutality",
    "tree_id": "barbarian_brutality",
    "description": ("Big weapons, short tempers - crits that pay for "
                    "themselves and a finisher for anything wounded."),
    "_source_note": (
        "Rebuilt 6 Nov 2026 from the 38 real CoA Brutality talents (role "
        "DPS). Energy is the whole pool on both sides - no second currency "
        "to translate, unlike Felsworn or Ranger - so every cost and refund "
        "talent lands. execute_threshold_pct 35 was added to "
        "barbarian_decapitate to match CoA and give this tree's execute "
        "theme something to key off; Brutality owns the class's "
        "low_health_threshold_pct at the same 0.35. Four talents die on "
        "'above 80% health', which has no conditional at all."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20,
                          "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"barbarian_brutality_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"barbarian_brutality_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


HIGH_HP = ("CoA gates this on the target being ABOVE 80% health. "
           "high_health_damage_threshold_pct is DEAD DATA - authored "
           "somewhere in this project and read by nothing - and there is no "
           "above-health conditional of any kind, only the below-health "
           "low_health_damage_pct added 6 Nov 2026. Dropped, with the value "
           "kept unconditional and the gain flagged rather than pocketed "
           "quietly.")

N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "pure_power", "Pure Power",
    "Increases the damage of Smash by 30% and your expertise by 10.",
    0, -4,
    effects={"ability_barbarian_smash_damage": 0.30, "expertise": 10.0},
    connect=["reckless_movements"],
    source="CoA over 2 ranks: 'Increases the damage of Smash by 15% and "
           "your expertise by 5.' PORTS EXACTLY, doubled - and the second "
           "half would have been dead a day earlier. `expertise` was read "
           "by NO engine code for most of this audit, because it reduces a "
           "target's dodge and parry and monsters had neither, which cost "
           "Guardian's Stalwart and Gladiator's Double Duty their text "
           "outright. Kyle had creature avoidance added on 5 Nov 2026 and "
           "it became a real stat. It is in PERCENTAGE POINTS and subtracts "
           "from dodge AND parry independently; the ability key is a "
           "FRACTION. Was a pure scalar on our side."))

N.append(node(
    "reckless_movements", "Reckless Movements",
    "Increases the damage of Ancestral Strike and Barbaric Whirl by 20%.",
    0, -2,
    effects={"ability_barbarian_ancestral_strike_damage": 0.20,
             "ability_barbarian_barbaric_whirl_damage": 0.20},
    connect=["bloody_fighter", "relentless"],
    source="CoA: 'Increases the damage of Ancestral Strike and Barbaric "
           "Whirl by 20%.' PORTS VERBATIM, both abilities - one of the few "
           "CoA talents in this tree needing no translation at all. "
           "Ancestral Strike is the spec's zero-cooldown filler, so three "
           "nodes here point at it. Both FRACTIONS. Was a pure scalar on "
           "our side."))

N.append(node(
    "bloody_fighter", "Bloody Fighter",
    "Increases the critical strike chance of Brutal Swing and Smash by "
    "10%.",
    0, 0,
    effects={"ability_barbarian_brutal_swing_crit": 10.0,
             "ability_barbarian_smash_crit": 10.0},
    connect=["crusher"],
    source="CoA over 2 ranks: 'Increases the critical strike chance of "
           "Brutal Swing and Smash by 5%.' PORTS EXACTLY, doubled. This "
           "tree keys off crits six times (Relentless, Headlopper, Anger "
           "Issues, Sustaining Swings, Spiked Weapons, the capstone), so "
           "crit chance is its real currency. Per-ability crit keys are "
           "PERCENTAGE POINTS, unlike the damage keys above, which are "
           "fractions. Was a pure scalar on our side."))

N.append(node(
    "efficient_killer", "Efficient Killer",
    "Reduces the cost of all your abilities by 15%.",
    0, 2,
    effects={"all_ability_cost_pct": 0.15},
    connect=["thirst_for_battle"],
    source="CoA: 'Reduces the Energy cost of your spells and abilities by "
           "10%.' PORTS VERBATIM (raised to 15%) - CoA's Energy IS our "
           "energy, since Barbarian is (ResourceType.ENERGY, None) with no "
           "second currency, which makes this one of the cleanest resource "
           "ports in the whole audit. all_ability_cost_pct is a FRACTION as "
           "a talent effect where POSITIVE MEANS A REDUCTION; it flips to "
           "percentage POINTS inside a status effect, which caught me on "
           "Ranger Farstrider tonight. Was a pure scalar on our side."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "relentless", "Relentless",
    "Your critical strikes restore 10 Energy.",
    1, -1,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "energy", "amount": 10}},
    connect=["headlopper"],
    source="CoA level 20 passive: 'Critical strikes with Ancestral Strike "
           "and Brutal Swing now refund 10 Energy.' PORTS VERBATIM, "
           "including the exact amount - only the two-ability scoping goes, "
           "since there is no per-ability proc trigger. grant_resource "
           "routes through the same gain_resource() the class's three "
           "generators use, so the cap is respected, and its `amount` is "
           "FLAT: there is no pct_max field, which is why CoA's Thirst for "
           "Battle ('regenerate 25% of your maximum Energy') and Beheader "
           "('refunds 100% of your maximum Energy') both become flat "
           "numbers too. Inventing a percentage field on Witch Doctor's "
           "Spiritual Devotee granted NOTHING while passing every check."))

N.append(node(
    "thirst_for_battle", "Thirst for Battle",
    "Your attacks have a 25% chance to restore 15 Energy.",
    1, 2,
    proc={"trigger": "on_weapon_swing", "chance": 25, "icd": 0,
          "grant_resource": {"resource": "energy", "amount": 15}},
    connect=["spiked_weapons"],
    source="CoA: 'Your Smash now regenerate 25% of your maximum Energy.' "
           "The restore ports; the percentage does not, because "
           "grant_resource takes a FLAT `amount` with no "
           "percentage-of-maximum form. The Smash scoping goes too (no "
           "per-ability proc trigger), so it becomes a 25% chance on any "
           "swing. Folded in CoA's Beheader ('scoring a kill blow with "
           "Decapitate now refunds 100% of your maximum Energy') - on_kill "
           "IS a live trigger, but a proc takes one trigger and the swing "
           "version fires far more often, so the kill form is dropped "
           "rather than given its own node."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "crusher", "Crusher",
    "Your attacks have a 20% chance to reset the cooldown of Crush.",
    2, 0,
    proc={"trigger": "on_weapon_swing", "chance": 20, "icd": 0,
          "reset_cooldown": ["barbarian_crush"]},
    connect=["horde_breaker", "anger_issues"],
    source="CoA over 2 ranks: 'Melee auto attacks now have a 10% chance to "
           "reset the cooldown of Crush.' PORTS VERBATIM, doubled for the "
           "two ranks. reset_cooldown WITH A BARE LIST is a full reset, as "
           "against the {abilities, turns} form which only shaves turns - "
           "confusing the two is silent and easy to do. Folded in CoA's "
           "Power Swings ('reduces the cooldown of Crush by -5 sec'), which "
           "names the same ability. Crush is a 5-turn-cooldown AoE, so this "
           "is a real throughput node."))

N.append(node(
    "spiked_weapons", "Spiked Weapons",
    "Increases your physical critical damage by 20% and your armor "
    "penetration by 100.",
    2, 2,
    effects={"crit_damage_physical": 0.20, "armor_penetration": 100},
    connect=["overkill"],
    source="CoA: 'Increases the critical damage of Crush, Brutal Swing, and "
           "Decapitate by 20%.' CoA's 20% is kept but widened to a global, "
           "because this tree crits six different ways and three "
           "per-ability crit-damage keys would be narrower than CoA "
           "intends. Folded in CoA's Battering Ram ('while wielding a "
           "two-handed weapon, you bypass 10% of enemy armor'), whose "
           "weapon-type gate cannot be built - nothing reads weapon type - "
           "and whose '10% of armor' has no proportional form, since "
           "armor_penetration is FLAT. crit_damage_* keys are FRACTIONS; "
           "armor_penetration is a flat rating, which is why they look "
           "mismatched here. Was a pure scalar on our side."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "headlopper", "Headlopper",
    "Your critical strikes open a bleed dealing damage over 3 turns.",
    3, -2,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "apply_effect": {"effect_id": "headlopper", "name": "Headlopper",
                           "effect_type": "dot", "duration": 3,
                           "potency": 32, "damage_school": "physical",
                           "dispel_type": None, "on_target": True}},
    connect=["ancestral_trauma"],
    source="CoA: 'Your critical strikes with Decapitate now cause the enemy "
           "to bleed, dealing an additional 30% of the damage dealt over 5 "
           "seconds.' PORTS ALMOST EXACTLY. The Decapitate scoping goes (no "
           "per-ability proc trigger) and '30% of the damage dealt' becomes "
           "a fixed potency, because apply_effect cannot read the "
           "triggering hit's amount - only bonus_pct, leech_pct and smart "
           "heals do, and none of them apply an effect. 5 sec -> 3 turns. A "
           "proc-applied dot carries `potency` as PER-TURN damage (32 a "
           "turn, 96 total) where an ABILITY rank's effect_value is the "
           "TOTAL and gets divided (abilities.py:2695)."))

N.append(node(
    "horde_breaker", "Horde Breaker",
    "Your attacks have a 35% chance to wound the target, increasing their "
    "physical damage taken by 8% for 4 turns.",
    3, 0,
    proc={"trigger": "on_weapon_swing", "chance": 35, "icd": 0,
          "apply_effect": {"effect_id": "wounded", "name": "Wounded",
                           "effect_type": "debuff", "duration": 4,
                           "stat_mods": {"physical_damage_taken_pct": 8},
                           "max_stacks": 2, "dispel_type": None,
                           "on_target": True}},
    connect=["anger_issues"],
    source="CoA: 'Your Crush now applies Wounded to enemies for 1 min and "
           "is now guaranteed to critically strike enemies affected by "
           "Headbutt. Wounded increases Physical Damage taken by 4% for 1 "
           "min.' The Wounded debuff ports at double value over 2 stacks. "
           "The guaranteed-crit clause fails twice: nothing grants a "
           "guaranteed crit on a specific ability, and 'enemies affected by "
           "Headbutt' needs to read a target's debuffs. 1 min -> 4 turns. "
           "CAREFUL: physical_damage_taken_pct is PERCENTAGE POINTS inside "
           "a status effect (monster.py:736 divides by 100) where as a "
           "TALENT effect it is a fraction - so 8 is 8%, and 0.08 would "
           "have delivered 0.08%."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "anger_issues", "Anger Issues",
    "Your critical strikes have a 35% chance to reduce the cooldown of "
    "Killing Spree and Unbridled Rage by 2 turns.",
    4, 0,
    proc={"trigger": "on_crit", "chance": 35, "icd": 1,
          "reset_cooldown": {"abilities": ["barbarian_killing_spree",
                                           "barbarian_unbridled_rage"],
                             "turns": 2}},
    connect=["overkill", "ogres_strength"],
    source="CoA: 'Scoring a critical strike against an enemy now reduces "
           "the cooldown of Carnage by -4 sec.' Carnage is not in our "
           "ability book, so the node is re-pointed at Killing Spree and "
           "Unbridled Rage, the spec's two real cooldowns. Folded in CoA's "
           "Deep Fury ('direct Physical damage dealt now reduces the "
           "cooldown of Unbridled Rage by -1 sec'), which names the same "
           "ability. The {abilities, turns} form of reset_cooldown shaves "
           "turns rather than resetting outright, which is what CoA "
           "describes - a BARE LIST would reset them fully."))

N.append(node(
    "ancestral_trauma", "Ancestral Trauma",
    "Increases your attack power by 25% of your Strength.",
    4, -2,
    effects={"attack_power_from_strength_pct": 0.25},
    connect=["ogres_strength"],
    source="CoA level 50 passive: 'Damage dealt by Ancestral Strike and "
           "Crush now scales with your Strength.' A per-ability stat "
           "SCALING coefficient is not something any key reaches - the "
           "ability keys are _damage, _healing, _crit, _crit_damage, _cost, "
           "_cooldown, _duration and _potency, and none touch how an "
           "ability scales off a stat. Rebuilt as a real global conversion: "
           "attack_power is in STAT_CONVERSION_TARGETS and strength in "
           "SOURCES, a legal pair, so a Barbarian's Strength genuinely "
           "becomes attack power and reaches every ability rather than two. "
           "Folded in CoA's Body Builder, whose 'when your Strength is "
           "lower than your Agility' clause cannot be built: nothing "
           "compares two of the caster's own stats. A FRACTION."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "overkill", "Overkill",
    "Increases the critical strike chance of Decapitate and Headhunter's "
    "Spear by 30%, and your damage against enemies below 35% health by "
    "25%.",
    5, 1,
    effects={"ability_barbarian_decapitate_crit": 30.0,
             "ability_barbarian_headhunters_spear_crit": 30.0,
             "low_health_damage_pct": 0.25,
             "low_health_threshold_pct": 0.35},
    connect=["sustaining_swings"],
    source="CoA: 'Increases the critical strike chance of Decapitate and "
           "Headhunter's Spear by 30% against targets below 20% health.' "
           "The crit chance ports verbatim at CoA's 30% on both abilities, "
           "unconditional - there is no conditional CRIT key, only "
           "conditional damage - with the conditional half added as "
           "low_health_damage_pct, the key introduced 6 Nov 2026 for the 48 "
           "CoA talents across 18 of the 21 classes worded this way. THIS "
           "IS THE ONE NODE IN ALL OF BARBARIAN THAT SETS "
           "low_health_threshold_pct, at 0.35 to match the "
           "execute_threshold_pct added to barbarian_decapitate the same "
           "day (CoA: 'Only usable on enemies below 35% health'), so the "
           "class's execute window and its execute ability's own gate "
           "agree. That key SUMS across talents, is UNSCALED so rank does "
           "not divide it, and a character can spend in several trees - "
           "Headhunting and Ancestry inherit it, and a second setter would "
           "give 70%. Tinker once shipped two summing to 0.8. main() "
           "asserts exactly one and tools/qa_summing_thresholds.py enforces "
           "it class-wide. Was a pure scalar on our side."))

N.append(node(
    "ogres_strength", "Ogre's Strength",
    "Increases your Strength by 25%.",
    5, -1,
    effects={"strength_pct": 25},
    connect=["sustaining_swings"],
    source="CoA level 40 passive: 'Increases your Strength by 25%.' PORTS "
           "VERBATIM, which for a node this large is worth noting. "
           "strength_pct is PERCENTAGE POINTS (character.py:1262 divides by "
           "100), so 25 is 25% - and it compounds with Ancestral Trauma one "
           "tier below, which converts that Strength into attack power, so "
           "the two nodes are deliberately adjacent. Was a pure scalar on "
           "our side."))

N.append(node(
    "whirling_assault", "Whirling Assault",
    "Increases the damage of Whirling Advance by 60% and of Barbaric Whirl "
    "by 30%.",
    5, 3,
    effects={"ability_barbarian_whirling_advance_damage": 0.60,
             "ability_barbarian_barbaric_whirl_damage": 0.30},
    connect=["sustaining_swings"],
    source="CoA: 'Increases the damage of Whirling Advance by 300% on "
           "enemies above 80% health.' " + HIGH_HP + " CoA's 300% is cut to "
           "60% precisely because it is now unconditional - a 300% "
           "unconditional damage increase on an AoE would dwarf everything "
           "else in the tree, where CoA's version only applies to opening "
           "hits. Extended to Barbaric Whirl, which CoA's Steelslinger also "
           "buffs ('increases its damage dealt by 100% on enemies below 35% "
           "health') and which fails the same way in the other direction - "
           "Overkill already owns the class's below-health threshold, so a "
           "second conditional node here would have had to share it. Both "
           "FRACTIONS. Was a pure scalar on our side."))

N.append(node(
    "killing_spree", "Killing Spree",
    "Increases the damage of Killing Spree and Berserker Rush by 35%.",
    1, -4,
    effects={"ability_barbarian_killing_spree_damage": 0.35,
             "ability_barbarian_berserker_rush_damage": 0.35},
    connect=["pure_power"],
    source="CoA: 'Charge at an enemy, dealing Physical damage. Can only be "
           "used within 6 seconds of scoring a killing blow or applying "
           "Born in Blood.' The ability already exists on a 6-turn "
           "cooldown. ITS USE WINDOW CANNOT BE BUILT: execute_threshold_pct "
           "gates on the TARGET's health, not on whether the caster "
           "recently killed something, and there is no on_kill-granted "
           "usability state - bypass_execute_threshold is the only "
           "consumable gate flag and it goes the other way. Born in Blood "
           "is a CoA buff we do not have. So the node boosts both charge "
           "abilities instead. Both FRACTIONS."))

N.append(node(
    "storm_of_steel", "Storm of Steel",
    "Increases the damage of Storm of Steel by 40% and its duration by 2 "
    "turns.",
    2, -3,
    effects={"ability_barbarian_storm_of_steel_damage": 0.40,
             "ability_barbarian_storm_of_steel_duration": 2},
    connect=["reckless_movements"],
    source="CoA: 'Begin striking your target every 0.5 sec for 80% Weapon "
           "Damage for 3 sec.' Ours is a 3-turn dot on a 6-turn cooldown, "
           "since there is no channelling. BOTH HALVES ARE REAL DAMAGE: "
           "+2 turns on a dot ADDS TICKS at full per-turn value, because "
           "abilities.py:2777 derives per_turn from the ability's OWN base "
           "duration rather than the talented one - so the dot goes 3 -> 5 "
           "turns and its total rises by two thirds on top of the 40%. "
           "Folded in CoA's Steel Fury, whose per-strike ramp ('increases "
           "the damage of its subsequent strikes by 4%, stacking 10 times') "
           "needs a readable stack count, and whose +2.5 sec duration this "
           "node delivers. SMALL INTEGER IN TURNS, so talent_ranks.spread() "
           "refuses to rank this node."))

N.append(node(
    "maximum_carnage", "Maximum Carnage",
    "Increases the damage of Unbridled Rage's follow-up by 30% and your "
    "area damage by 20%.",
    3, 2,
    effects={"ability_barbarian_unbridled_rage_damage": 0.30,
             "aoe_damage": 0.20},
    connect=["horde_breaker"],
    source="CoA: 'Casting Unbridled Rage now causes you to begin swinging "
           "your weapon around you dealing Physical damage to up to 5 "
           "nearby enemies over 5 seconds.' A follow-up AoE that starts "
           "when a buff is cast needs a per-ability proc trigger, which "
           "does not exist, so the node becomes flat damage on Unbridled "
           "Rage plus aoe_damage. aoe_damage is read at abilities.py:1600 "
           "ONLY when target_type is enemy_aoe, so it is genuinely scoped "
           "to area attacks rather than a stealth global - this spec has "
           "five (Whirling Advance, Barbaric Whirl, Brutal Swing, Crush, "
           "Keg Smash). Folded in CoA's Utter Devastation, whose "
           "consumable guaranteed crit has no mechanism. Both FRACTIONS. "
           "Was a pure scalar on our side."))

N.append(node(
    "skullseeker", "Skullseeker",
    "Increases your critical strike chance by 8% and your physical damage "
    "by 6%.",
    4, 2,
    effects={"crit_chance_physical": 8.0, "physical_damage": 0.06},
    connect=["anger_issues"],
    source="CoA: 'Increases your critical strike chance against enemies "
           "above 80% health by 25%.' " + HIGH_HP + " CoA's 25% is cut to "
           "8% precisely because it is now unconditional and permanent "
           "where CoA's applies only to opening hits. The physical damage "
           "is added so the node is not a bare crit scalar. "
           "crit_chance_physical is PERCENTAGE POINTS; physical_damage is a "
           "FRACTION - two conventions in one dict, which is this project's "
           "default state. Was a pure scalar on our side."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "sustaining_swings", "Sustaining Swings",
    "Your attacks have a 25% chance to heal you for 15% of the damage "
    "dealt and strike an additional time.",
    6, 0,
    proc={"trigger": "on_weapon_swing", "chance": 25, "icd": 0,
          "leech_pct": 15, "extra_attack": True},
    source="CoA: 'Melee attacks now have an 8% chance to heal you for 10% "
           "of the damage dealt and cause your next Ancestral Strike to "
           "deal 50% increased damage.' THE LEECH PORTS EXACTLY: leech_pct "
           "is one of only THREE proc payloads that READ the triggering "
           "hit's amount, so '% of the damage dealt' is literally what it "
           "computes - and on_weapon_swing is the right trigger for it, "
           "unlike the avoidance triggers where the amount is always zero "
           "and it would silently heal nothing. 'Your next Ancestral Strike "
           "deals 50% more' cannot be built: nothing marks a specific "
           "ability's next cast. Replaced with CoA's own Rancor ('your "
           "Brutal Swing now triggers an additional auto attack'), since "
           "`extra_attack` is a BOOLEAN giving exactly one extra attack, "
           "which is precisely what Rancor asks for. One proc can carry "
           "both payloads, which is why the capstone does both halves. 8% "
           "-> 25% because it is the capstone."))


# ---- rank policy --------------------------------------------------------
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

    setters = [n["talent_id"] for n in TREE["nodes"]
               if "low_health_threshold_pct" in (n.get("effects") or {})]
    assert len(setters) == 1, (
        f"low_health_threshold_pct SUMS across talents and is UNSCALED, and "
        f"a character can spend in several Barbarian trees - exactly one "
        f"node in the CLASS may set it, and Brutality owns it at 0.35. "
        f"Found {setters}")

    # The class execute window is set to 0.35 to match Decapitate's own
    # gate, which was added on 6 Nov 2026. If the ability loses it, this
    # tree's Overkill promises execute damage on targets it cannot reach.
    abilities = json.loads(
        (ROOT / "data/abilities/barbarian.json").read_text())["abilities"]
    dec = next((a for a in abilities
                if a["ability_id"] == "barbarian_decapitate"), None)
    assert dec is not None and dec.get("execute_threshold_pct") == 35, (
        "barbarian_decapitate must keep execute_threshold_pct 35 - this "
        "tree sets the class low_health_threshold_pct to 0.35 to match it, "
        "and the two drifting apart would be silent")

    for n in TREE["nodes"]:
        proc = n.get("proc") or {}
        gr = proc.get("grant_resource")
        if gr:
            assert gr.get("resource") == "energy" and "amount" in gr, (
                f"{n['talent_id']} grant_resource must name energy "
                f"(Barbarian's single primary pool) with a FLAT amount - "
                f"there is no percentage-of-maximum form")
        if proc.get("trigger") in ("on_avoid", "on_parry", "on_dodge",
                                   "on_block"):
            for payload in ("leech_pct", "bonus_pct", "smart_heal_pct"):
                assert payload not in proc, (
                    f"{n['talent_id']} uses {payload} on "
                    f"{proc['trigger']} - an avoided attack deals 0 damage")
        mods = (proc.get("apply_effect") or {}).get("stat_mods") or {}
        for key in ("physical_damage_taken_pct", "magic_damage_taken_pct"):
            if key in mods:
                assert abs(mods[key]) >= 1, (
                    f"{n['talent_id']} {key}={mods[key]} inside a status "
                    f"effect, where it is PERCENTAGE POINTS")

    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Barbarian Brutality: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
