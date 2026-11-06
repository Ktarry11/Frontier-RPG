#!/usr/bin/env python3
"""Rebuild Warrior Arms from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_warrior_arms.py

SOURCE: data/reference/wotlk/warrior.json, from the game's own Spell.dbc.
Worksheet: data/reference/wotlk_worksheets/warrior.md.

ROLE: two-handed burst. Mortal Strike, Overpower off an opening, bleeds
from crits, and Execute when the target is finished.

WHY THIS TREE NEEDED IT: 16 of 23 nodes had no proc and no unlock, and it
was the second-worst in the project after Subtlety. It was also the
LOWEST-point tree in the game at 58, only two above the 56 floor, so a
level-60 Arms warrior had almost no room to choose.

RAGE IS THE PROBLEM THIS TREE KEEPS RUNNING INTO. rage_generation_pct IS
DEAD DATA - probed with tools/probe_talent_key.py, zero read sites, and
already recorded as dead in the project. Three real Arms talents are
written as rage generation:

    Improved Charge    "+10 rage from Charge"
    Anger Management   "1 rage per 3 seconds"
    Endless Rage       "25% more rage from damage dealt"

None can be built as written. All three are delivered as a grant_resource
proc instead, which is the same rage arriving by a different route, and
each node says so.

STANCES ARE REAL AND USABLE, which matters for two trees. combat/stances.py
defines battle / defensive / berserker, and a talent's require_form field
is checked against BOTH current_form and current_stance
(abilities.py:812) - so a stance-gated talent IS buildable. Arms does not
need it; Fury and Protection do.

UNIT CONVENTIONS, each probed:

    parry, expertise, haste            PERCENTAGE POINTS
    crit_chance_physical               PERCENTAGE POINTS
    strength_pct, stamina_pct          PERCENTAGE POINTS. Read at
                                       character.py:1262-1263 off `bonuses`
                                       and divided by 100 - the probe finds
                                       no literal read site because the
                                       line does not call
                                       get_talent_effect. They are LIVE.
    armor_penetration_pct              PERCENTAGE POINTS (lands /100)
    crit_damage_physical               FRACTION
    physical_damage                    FRACTION
    threat_generation_pct              FRACTION as a talent effect
    stun_duration_reduction_pct        FRACTION, not points - audit_talents
                                       has caught this authored as 30.0
    ability_<id>_crit                  PERCENTAGE POINTS
    ability_<id>_damage                FRACTION
    ability_<id>_cost / _cooldown      FLAT

WEAPON TYPE DOES NOT EXIST, so Poleaxe, Mace and Sword Specialization all
drop their equipment gate and keep their effect.

ABILITIES THE REAL TREE WANTS AND WE DO NOT HAVE: Slam, Revenge,
Hamstring, Shield Block, Shield Slam. Talents written on those are either
dropped or re-aimed at a real ability, recorded per node.

DROPPED, with reasons: Improved Hamstring (no Hamstring ability, and
immobilise does not exist), Juggernaut (its whole text is about using
Charge in combat and stance restrictions, neither of which this engine
models), Improved Slam (no Slam, and no cast times to shorten).

IMPROVED THUNDER CLAP IS GONE FROM THIS TREE. The outgoing Arms tree
carried it and the first draft of this rebuild kept it as a documented
placement departure - but it is PROTECTION-ONLY in the real game (row 0),
and the Protection rebuild in the same commit adds it there. Keeping both
would have let a hybrid stack two copies of the same real talent. That
leaves tier 3 with two nodes, Weapon Mastery and Trauma, which is what the
real tree's rows 4-5 hold once Improved Hamstring is dropped.

KEPT MANDATORY: Mortal Strike and Bladestorm are the only unlocks for
warrior_mortal_strike and warrior_bladestorm, both requires_talent.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

T = Tree("warrior_arms", "Warrior Arms",
         "Two-handed weapon mastery - crushing single-target burst.")

# ----------------------------------------------------------------- tier 0
T.node("improved_heroic_strike", "Improved Heroic Strike",
       "Reduces the Rage cost of your Heroic Strike by 1 per rank.",
       0, -2, 3, effects={"ability_warrior_heroic_strike_cost": 1},
       source="WotLK row 0: 'Reduces the cost of your Heroic Strike ability "
              "by 1/2/3 rage points.' Built verbatim. The outgoing version "
              "was 2 per rank, reaching 6 against the real 3.")

T.node("deflection", "Deflection",
       "Increases your parry chance by 1% per rank.",
       0, 0, 5, effects={"parry": 1.0},
       source="WotLK row 0: 'Increases your Parry chance by 5%' over 5 "
              "ranks. Built verbatim and kept from the outgoing tree. parry "
              "is PERCENTAGE POINTS, landing through a diminishing-returns "
              "curve so the realised value is slightly under nominal.")

T.node("improved_rend", "Improved Rend",
       "Increases the bleed damage of your Rend by 10% per rank.",
       0, 2, 2, effects={"ability_warrior_rend_damage": 0.10},
       source="WotLK row 0: 'Increases the bleed damage done by your Rend "
              "ability by 10%/20%.' Built verbatim over the real 2 ranks; "
              "the outgoing version had 3 ranks of 10%, reaching 30%.")

# ----------------------------------------------------------------- tier 1
T.node("improved_charge", "Improved Charge",
       "Charging generates 10 additional Rage.",
       1, -5, 2,
       proc={"trigger": "on_cast", "chance": 50, "icd": 0,
             "ability_filter": ["warrior_charge"],
             "grant_resource": {"resource": "rage", "amount": 10}},
       connected_to=["improved_heroic_strike"],
       source="WotLK row 1, NEW to our tree: 'Increases the amount of rage "
              "generated by your Charge ability by 5/10.' DEPARTURE in "
              "mechanism only - a talent cannot modify an ability's own "
              "`generates` block, and rage_generation_pct is DEAD DATA "
              "(probed: zero read sites). Delivered as a grant_resource "
              "proc filtered to Charge, which puts the same rage in the "
              "same place. The chance carries the rank curve to 100% "
              "because a proc's payload does not scale with points.")

T.node("improved_overpower", "Improved Overpower",
       "Increases the critical strike chance of your Overpower by 25% per "
       "rank.",
       1, -3, 2, effects={"ability_warrior_overpower_crit": 25.0},
       connected_to=["improved_heroic_strike"],
       source="WotLK row 1: 'Increases the critical strike chance of your "
              "Overpower ability by 25%/50%.' Built verbatim. The outgoing "
              "version reduced Overpower's COOLDOWN instead, which is "
              "Unrelenting Assault's job in the real tree.")

T.node("iron_will", "Iron Will",
       "Reduces the duration of Stun effects used against you by 7% per "
       "rank.",
       1, -1, 3, effects={"stun_duration_reduction_pct": 0.07},
       connected_to=["deflection"],
       source="WotLK row 1: 'Reduces the duration of all Stun and Charm "
              "effects used against you by 20%' over 3 ranks. Charm does "
              "not exist; is_stun is this engine's only incapacitate. "
              "stun_duration_reduction_pct is a FRACTION, not points - "
              "audit_talents caught it being authored as 30.0 elsewhere in "
              "the project. Note it floors a stun at 1 turn, so it can "
              "shorten but never negate. Kept from the outgoing tree, "
              "corrected from 0.1 to 0.07 so three ranks reach 21%, the "
              "nearest whole percent per rank to the real 20%, rather "
              "than the 30% the outgoing value reached.")

T.node("anger_management", "Anger Management",
       "You generate 5 Rage every other turn.",
       1, 1, 1,
       proc={"trigger": "on_damage_cast", "chance": 100, "icd": 2,
             "grant_resource": {"resource": "rage", "amount": 5}},
       connected_to=["deflection"],
       source="WotLK row 1: 'Generates 1 rage per 3 seconds.' One rage per "
              "3 seconds is one rage per turn; delivered as 5 every other "
              "turn, which is the same rate rounded into something "
              "noticeable. It has to be a proc because there is no "
              "passive-regeneration key for rage at all - "
              "rage_generation_pct is dead. Kept as a proc from the "
              "outgoing tree.")

T.node("tactical_mastery", "Tactical Mastery",
       "Increases the threat generated by your Mortal Strike and "
       "Bloodthirst by 5% per rank.",
       1, 3, 3, effects={"threat_generation_pct": 0.05},
       connected_to=["improved_rend"],
       source="WotLK row 1: 'You retain up to an additional 5/10/15 of your "
              "rage points when you change stances. Also greatly increases "
              "the threat generated by your Bloodthirst and Mortal Strike "
              "abilities when you are in Defensive Stance.' DEPARTURE - "
              "stance switching costs rage (stances.py STANCE_SWITCH_COST) "
              "but nothing modifies how much is retained, and threat has no "
              "per-ability key, only the global threat_generation_pct. So "
              "the threat half is built globally and unconditionally rather "
              "than gated to Defensive Stance - it could have been gated "
              "with require_form, but Arms is not a tanking tree and a "
              "stance gate on a tier-1 node would make it dead weight for "
              "the spec that takes it. The outgoing version was a cost cut "
              "on Mortal Strike.")

T.node("impale", "Impale",
       "Increases the critical strike damage of your abilities by 10% per "
       "rank.",
       1, 5, 2, effects={"crit_damage_physical": 0.10},
       connected_to=["improved_rend"],
       source="WotLK row 1: 'Increases the critical strike damage bonus of "
              "your abilities by 10%/20%.' Built verbatim. "
              "crit_damage_physical is a FRACTION, read at abilities.py:1460 "
              "inside a ternary - the probe reports no literal read site, "
              "which is a probe limitation and not evidence of death. The "
              "outgoing version was 4 points of crit CHANCE on two "
              "abilities, a different stat entirely.")

T.node("deep_wounds", "Deep Wounds",
       "Your critical strikes have a 33% chance per rank to cause a bleed, "
       "dealing damage over 3 turns.",
       1, 7, 3,
       proc={"trigger": "on_crit", "chance": 33, "icd": 0,
             "apply_effect": {"effect_id": "deep_wounds",
                              "name": "Deep Wounds",
                              "effect_type": "dot", "duration": 3,
                              "potency": 40,
                              "damage_school": "physical"}},
       connected_to=["impale"],
       source="WotLK row 2: 'Requires Melee Weapon. Your critical strikes "
              "cause the opponent to bleed, dealting 16%/32%/48% of your "
              "melee weapon's average damage over 6 sec.' Built as the real "
              "mechanic. Weapon-damage scaling is not available to a proc "
              "payload - potency is a flat per-turn number - so 40 per turn "
              "over 3 turns is a fixed bleed instead. NOTE a proc-applied "
              "dot states PER-TURN damage as `potency`, where an ABILITY "
              "rank's effect_value is the TOTAL and gets divided; getting "
              "that backwards is a 3x error in either direction. 6 seconds "
              "is 3 turns, the standard bucket. The real talent requires "
              "Impale, which connected_to reproduces.")

# ----------------------------------------------------------------- tier 2
T.node("poleaxe_specialization", "Poleaxe Specialization",
       "Increases your critical strike chance by 1% per rank.",
       2, -5, 5, effects={"crit_chance_physical": 1.0},
       connected_to=["improved_overpower"],
       source="WotLK row 2: 'Requires One-Handed Axes, Polearms, Two-Handed "
              "Axes. Increases your chance to get a critical strike and the "
              "critical damage caused with Axes and Polearms by 5%.' "
              "DEPARTURE - no weapon-type key, so the gate is dropped. Only "
              "the crit CHANCE half is kept; adding the crit-damage half "
              "too would double up on Impale two rows above. The outgoing "
              "version was flat attack_power_pct.")

T.node("two_handed_weapon_specialization", "Two-Handed Weapon Specialization",
       "Increases your physical damage by 2% per rank.",
       2, -3, 3, effects={"physical_damage": 0.02},
       connected_to=["improved_overpower"],
       source="WotLK row 2, NEW to our tree: 'Increases the damage you deal "
              "with two-handed melee weapons by 2%/4%/6%.' Built verbatim "
              "minus the weapon gate. physical_damage is a FRACTION with "
              "four real read sites.")

T.node("sweeping_strikes", "Sweeping Strikes",
       "Increases the damage of your Whirlwind and Cleave by 20%.",
       2, -1, 1,
       effects={"ability_warrior_whirlwind_damage": 0.20,
                "ability_warrior_cleave_damage": 0.20},
       connected_to=["iron_will"],
       source="WotLK row 2: 'Your next 5 melee attacks strike an additional "
              "nearby opponent.' DEPARTURE - nothing in this engine "
              "modifies how many targets an ability hits. max_targets caps "
              "an existing AoE rather than widening a single-target hit, and "
              "there is no attack-counter to spend down. Delivered as "
              "damage on the two abilities that ALREADY hit multiple "
              "targets, which is the nearest honest reading. Kept from the "
              "outgoing tree, which reached the same conclusion. The real "
              "talent is Mortal Strike's prerequisite, preserved below.")

T.node("taste_for_blood", "Taste for Blood",
       "Your Rend has a 33% chance per rank to reset the cooldown of your "
       "Overpower.",
       2, 1, 3,
       proc={"trigger": "on_cast", "chance": 33, "icd": 0,
             "ability_filter": ["warrior_rend"],
             "reset_cooldown": "warrior_overpower"},
       connected_to=["anger_management"],
       source="WotLK row 2, NEW to our tree: 'Whenever your Rend ability "
              "causes damage, you have a 33%/66%/100% chance of allowing "
              "the use of your Overpower ability for 9 sec.' Built as the "
              "real mechanic - reset_cooldown is a real proc payload "
              "(status_effects.py:1207) and knocking Overpower's cooldown "
              "off IS 'allowing the use of' it. The real chance curve is "
              "exact. The 9-second window and the 1-charge clause are not "
              "expressible - no charge system - so the reset is immediate "
              "and unconditional instead.")

T.node("mace_specialization", "Mace Specialization",
       "Your attacks ignore 3% of your target's armor per rank.",
       2, 3, 5, effects={"armor_penetration_pct": 3.0},
       connected_to=["tactical_mastery"],
       source="WotLK row 2, NEW to our tree: 'Your attacks with maces "
              "ignore up to 15% of your opponent's armor.' The real 15% "
              "over 5 ranks, minus the weapon gate. "
              "armor_penetration_pct is PERCENTAGE POINTS - it lands on the "
              "attribute divided by 100, so 3.0 is 3%, and it is read by "
              "monster.py:658 via getattr on the ATTACKER rather than "
              "through get_talent_effect.")

T.node("sword_specialization", "Sword Specialization",
       "Your swings have a 2% chance per rank to grant an extra attack.",
       2, 5, 5,
       proc={"trigger": "on_weapon_swing", "chance": 2, "icd": 0,
             "extra_attack": True},
       connected_to=["deep_wounds"],
       source="WotLK row 2, NEW to our tree: 'Requires One-Handed Swords, "
              "Two-Handed Swords. Gives you a 10% chance to get an extra "
              "attack on the same target after hitting your target with "
              "your Sword.' extra_attack is a BOOLEAN - exactly one extra "
              "attack, no count - which is precisely what the real talent "
              "grants. 2% per rank reaches the real 10% at 5 ranks. Weapon "
              "gate dropped.")

# ----------------------------------------------------------------- tier 3
T.node("weapon_mastery", "Weapon Mastery",
       "Increases your expertise by 2 per rank.",
       3, -2, 2, effects={"expertise": 2.0},
       connected_to=["poleaxe_specialization"],
       source="WotLK row 3: 'Reduces the chance for your attacks to be "
              "dodged by 1%/2% and reduces the duration of all Disarm "
              "effects used against you by 25%/50%.' Reducing the chance to "
              "be dodged IS expertise, so that half is exact. Disarm "
              "duration is not modifiable. The outgoing version granted "
              "hit_rating - which, before creature avoidance was added for "
              "humanoids and bosses, was genuinely indistinguishable from "
              "expertise; Kyle's own note was 'expertise is basically hit "
              "rating unless we can encode parry and dodge in enemies'. Now "
              "that they are encoded, this node is meaningfully different.")

T.node("trauma", "Trauma",
       "Increases the damage of your Rend by 15% per rank.",
       3, 0, 2, effects={"ability_warrior_rend_damage": 0.15},
       connected_to=["sweeping_strikes"],
       source="WotLK row 3: 'Your melee critical strikes increase the "
              "effectiveness of Bleed effects on the target by 15%/30% for "
              "1 min.' DEPARTURE - nothing can modify an EXISTING effect's "
              "potency from outside it, and bleed_dot_damage is dead data. "
              "Delivered as direct Rend damage, which is the bleed this "
              "tree actually applies. Kept from the outgoing tree at the "
              "real 15% per rank.")

# ----------------------------------------------------------------- tier 4
T.node("second_wind", "Second Wind",
       "Being struck has a 50% chance per rank to generate 20 Rage.",
       4, -4, 2,
       proc={"trigger": "on_damage_taken", "chance": 50, "icd": 2,
             "grant_resource": {"resource": "rage", "amount": 20}},
       connected_to=["weapon_mastery"],
       source="WotLK row 4: 'Whenever you are struck by a Stun or "
              "Immobilize effect you will generate 10/20 rage and 5%/10% of "
              "your total health over 10 sec.' DEPARTURE on the trigger - "
              "nothing fires when the actor BECOMES stunned, and there is "
              "no immobilise. on_damage_taken is the nearest real moment. "
              "The real 20 rage is kept; the heal-over-time half is dropped "
              "rather than doubling the node's value. Kept as a proc from "
              "the outgoing tree.")

T.node("mortal_strike", "Mortal Strike",
       "Teaches Mortal Strike, a vicious wound that weakens healing on the "
       "target.",
       4, -2, 1, node_type="active",
       effects={"unlock_ability": "warrior_mortal_strike"},
       connected_to=["sweeping_strikes"],
       source="WotLK row 4, kept - the ONLY unlock for "
              "warrior_mortal_strike, which is requires_talent, so dropping "
              "it would strand the ability. The real talent requires "
              "Sweeping Strikes, which connected_to reproduces.")

T.node("improved_mortal_strike", "Improved Mortal Strike",
       "Increases the damage of your Mortal Strike by 3% per rank and "
       "reduces its cooldown by 1 turn.",
       4, 0, 3,
       effects={"ability_warrior_mortal_strike_damage": 0.03,
                "ability_warrior_mortal_strike_cooldown": 1},
       connected_to=["mortal_strike"],
       source="WotLK row 4, NEW to our tree: 'Increases the damage caused "
              "by your Mortal Strike ability by 3%/6%/10% and reduces the "
              "cooldown by 1 sec.' Both halves built. The cooldown key is "
              "FLAT turns and authored at 1 PER RANK, which over 3 ranks "
              "takes Mortal Strike's 3-turn cooldown to its 1-turn floor - "
              "talented_cooldown clamps at 1, so this cannot reach zero. "
              "The real talent requires Mortal Strike, reproduced.")

T.node("strength_of_arms", "Strength of Arms",
       "Increases your Strength and Stamina by 2% per rank and your "
       "expertise by 2 per rank.",
       4, 2, 2,
       effects={"strength_pct": 2.0, "stamina_pct": 2.0, "expertise": 2.0},
       connected_to=["trauma"],
       source="WotLK row 4, NEW to our tree: 'Increases your total Strength "
              "and Stamina by 2%/4% and your Expertise by 2/4.' Built "
              "verbatim, all three halves. strength_pct and stamina_pct are "
              "PERCENTAGE POINTS, read at character.py:1262-1263 off the "
              "`bonuses` dict and divided by 100 - the probe finds no "
              "literal read site because that line does not call "
              "get_talent_effect, so they LOOK dead and are not.")

T.node("unrelenting_assault", "Unrelenting Assault",
       "Reduces the cooldown of your Overpower by 1 turn per rank and "
       "increases its damage by 10% per rank.",
       4, 4, 2,
       effects={"ability_warrior_overpower_cooldown": 1,
                "ability_warrior_overpower_damage": 0.10},
       connected_to=["trauma"],
       source="WotLK row 4, NEW to our tree: 'Reduces the cooldown of your "
              "Overpower and Revenge abilities by 2/4 secs and increases "
              "the damage done by both abilities by 10%/20%.' Revenge does "
              "not exist here, so only the Overpower half is built - with "
              "both of its clauses at the real numbers.")

# ----------------------------------------------------------------- tier 5
T.node("sudden_death", "Sudden Death",
       "Your strikes have a 3% chance per rank to let you Execute "
       "regardless of the target's health.",
       5, -3, 3,
       proc={"trigger": "on_damage_cast", "chance": 3, "icd": 0,
             "apply_effect": {"effect_id": "sudden_death",
                              "name": "Sudden Death",
                              "effect_type": "buff", "duration": 2,
                              "proc": {"bypass_execute_threshold": True},
                              "on_target": False}},
       connected_to=["second_wind"],
       source="WotLK row 5: 'Your melee hits have a 3%/6%/9% chance of "
              "allowing the use of Execute regardless of the target's "
              "health state. In addition, you keep at least 10 rage after "
              "using Execute.' Built with the real mechanic and the real "
              "chance curve: bypass_execute_threshold is a real proc FLAG, "
              "CONSUMED ON USE, and execute_threshold_pct is enforced at "
              "abilities.py:1741. The rage-retention half is dropped. NOTE "
              "the nested proc inside apply_effect works but is NOT "
              "inspected by audit_talents, so this one is verified by "
              "spending it on a live warrior rather than by the audit.")

T.node("endless_rage", "Endless Rage",
       "You generate 5 additional Rage whenever you strike.",
       5, -1, 1,
       proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
             "grant_resource": {"resource": "rage", "amount": 5}},
       connected_to=["second_wind"],
       source="WotLK row 5: 'You generate 25% more rage from damage dealt.' "
              "DEPARTURE - rage_generation_pct is DEAD DATA (probed, zero "
              "read sites, already recorded as dead in the project), so a "
              "percentage increase to rage generation cannot be expressed "
              "at all. Delivered as flat rage on a strike, icd 1 so it is "
              "once a turn. Kept as a proc from the outgoing tree.")

T.node("wrecking_crew", "Wrecking Crew",
       "Your critical strikes have a 20% chance per rank to enrage you, "
       "increasing all your damage by 10% for 4 turns.",
       5, 1, 5,
       proc={"trigger": "on_crit", "chance": 20, "icd": 0,
             "apply_effect": {"effect_id": "wrecking_crew",
                              "name": "Wrecking Crew",
                              "effect_type": "buff", "duration": 4,
                              "stat_mods": {"all_damage": 0.10},
                              "on_target": False}},
       connected_to=["improved_mortal_strike"],
       source="WotLK row 5: 'Your melee critical hits Enrage you, "
              "increasing all damage caused by 2%-10% for 12 sec.' Built "
              "with the real 10% at full rank and the real 12 seconds (4 "
              "turns). Ranked by CHANCE rather than magnitude because a "
              "proc's chance scales with points_spent and its payload does "
              "not - 2%-to-10% at a fixed chance is not authorable. The "
              "'does not stack with Enrage' clause is handled by "
              "exclusive_group in Fury, where Enrage lives. The outgoing "
              "version was a 1-point proc.")

T.node("blood_frenzy", "Blood Frenzy",
       "Increases your haste by 5% per rank.",
       5, 3, 2, effects={"haste": 5.0},
       connected_to=["unrelenting_assault"],
       source="WotLK row 5: 'Increases your melee attack speed by 5%/10%. "
              "In addition your Rend and Deep Wounds abilities also "
              "increase all physical damage caused to that target by 2%/4%.' "
              "The haste half is built verbatim at the real 10%. The "
              "target-debuff half needs a bleed-presence read on the target, "
              "which does not exist. haste is PERCENTAGE POINTS. The "
              "outgoing version was Rend damage, which is Trauma's job.")

# ----------------------------------------------------------------- tier 6
T.node("bladestorm", "Bladestorm",
       "Teaches Bladestorm, whirling through every nearby enemy.",
       6, 1, 1, node_type="active",
       effects={"unlock_ability": "warrior_bladestorm"},
       connected_to=["wrecking_crew"],
       source="WotLK row 10, the capstone, kept - the ONLY unlock for "
              "warrior_bladestorm, which is requires_talent. The real "
              "talent's repeated whirlwind over 6 seconds is the ability's "
              "own business; there are no channelled or repeating effects "
              "for a talent to express.")


def main():
    return T.write(was="23 nodes, 58 points - 4 proc, 9 ability-scoped, "
                       "5 flat stat, 2 unlock, 1 mixed  (LOWEST-point tree "
                       "in the project)")


if __name__ == "__main__":
    sys.exit(main())
