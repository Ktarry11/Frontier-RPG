#!/usr/bin/env python3
"""Rebuild Rogue Assassination from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_rogue_assassination.py

SOURCE: data/reference/wotlk/rogue.json, from the game's own Spell.dbc.
Worksheet: data/reference/wotlk_worksheets/rogue.md.

ROLE: poisons and bleeds into heavy finishers. Where Subtlety is the
opener, Assassination is the sustained bleed and the crit that feeds it.

WHAT WAS ALREADY RIGHT. This tree was in far better shape than Subtlety -
9 of 23 nodes carried real procs. The rebuild is mostly about five
talents that were wearing the wrong mechanic entirely, and about the four
combo-point talents that could not be built until 5 Nov 2026:

    Malice        was per-ability crit on Mutilate and Eviscerate; the
                  real talent is flat crit chance, and this tree's crit
                  engine depends on it
    Ruthlessness  was an Eviscerate cost cut; really a combo-point proc
    Lethality     was scattered ability damage; really a crit-DAMAGE
                  bonus on combo generators
    Seal Fate     had a proc, now the real one: crits add combo points
    Murder        was Garrote/Rupture damage; really flat all-damage

UNIT CONVENTIONS, each probed with tools/probe_talent_key.py:

    crit_chance_physical     PERCENTAGE POINTS (lands on the attribute)
    crit_damage_physical     FRACTION. Read at abilities.py:1460 inside a
                             ternary, which is why the probe reports no
                             literal read site - it is LIVE, confirmed by
                             reading the line.
    damage_taken_pct         read RAW on BOTH sides: -0.06 is -6%
    healing_taken_pct        FRACTION as a talent effect
    all_damage               FRACTION
    dodge                    PERCENTAGE POINTS
    ability_<id>_crit        PERCENTAGE POINTS
    ability_<id>_damage      FRACTION
    ability_<id>_cost        FLAT

max_energy_bonus IS DEAD. Probed: it reaches the talent bus and has zero
read sites, and the project already recorded it as dead data. So Vigor's
"+10 maximum Energy" cannot be built as written and is delivered as
recurring Energy instead - documented on the node.

low_health_threshold_pct is authored NOWHERE, enforced by the kit. See
tools/wotlk_tree_kit.py.

WHAT IS NOT BUILDABLE, and what each became:

    Fleet Footed        movement speed and snare duration do not exist
                        -> dodge
    Improved Poisons    there is no poison APPLICATION CHANCE to raise
                        -> poison potency instead
    Overkill            stealth does not exist -> Energy on a kill
    Master Poisoner     nothing reads whether the target is poisoned
                        -> flat crit chance
    Cut to the Chase    nothing can refresh another buff's duration
                        -> the finishers grant the haste directly
    Turn the Tables     a talent effect can never reach an ally, and no
                        trigger reports a party member's avoidance
                        -> fires on the rogue's own avoidance
    Hunger For Blood    nothing reads a debuff on the target, so "requires
                        a bleed" cannot gate it -> the bleeds themselves
                        grant it
    Improved Kidney     ability_<id>_potency scales a buff's OWN stat_mods
    Shot                and rogue_kidney_shot has an EMPTY stat_mods dict,
                        so there is nothing to scale -> the proc applies
                        its own damage-taken debuff

DROPPED: Assassin's Resolve, a Cataclysm talent with no WotLK counterpart.
Its low_health_damage_reduction_pct moves onto Deadened Nerves, which is
the real damage-reduction talent in this tree.

KEPT MANDATORY: Cold Blood and Mutilate are the only unlocks for
rogue_cold_blood and rogue_mutilate, both of which are requires_talent.
Dropping either would strand an ability (qa_abilities_obtainable).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

FINISHERS = ["rogue_eviscerate", "rogue_rupture", "rogue_slice_and_dice",
             "rogue_expose_armor", "rogue_kidney_shot", "rogue_envenom"]

#: The combo-point generators, for Lethality and Seal Fate.
GENERATORS = ["rogue_sinister_strike", "rogue_backstab", "rogue_mutilate",
              "rogue_hemorrhage", "rogue_garrote", "rogue_ambush",
              "rogue_cheap_shot", "rogue_gouge", "rogue_shiv"]

T = Tree("rogue_assassination", "Rogue Assassination",
         "Poisons and bleeds, built into lethal finishing moves.")

# ----------------------------------------------------------------- tier 0
T.node("improved_eviscerate", "Improved Eviscerate",
       "Increases the damage of your Eviscerate by 7% per rank.",
       0, -2, 3, effects={"ability_rogue_eviscerate_damage": 0.07},
       source="WotLK row 0: 'Increases the damage done by your Eviscerate "
              "ability by 20%' over 3 ranks. 7% per rank reaches 21%, the "
              "nearest whole percent to the real 20%. The outgoing version "
              "was 10% per rank, which reached 30%.")

T.node("remorseless_attacks", "Remorseless Attacks",
       "After a killing blow, your next strikes land with 40% increased "
       "critical strike chance for 2 turns. 50% chance per rank.",
       0, 0, 2,
       proc={"trigger": "on_kill", "chance": 50, "icd": 0,
             "apply_effect": {"effect_id": "remorseless_attacks",
                              "name": "Remorseless Attacks",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"crit_chance_physical": 40},
                              "on_target": False}},
       source="WotLK row 0: 'After killing an opponent that yields "
              "experience or honor, gives you a 40% increased critical "
              "strike chance on your next Sinister Strike, Hemorrhage, "
              "Backstab, Mutilate, Ambush, or Ghostly Strike. Lasts 20 "
              "sec.' on_kill is a real trigger and 40% is the real number. "
              "Scoping the buff to those six abilities is not possible - a "
              "status effect's stat_mods apply to everything - so it is a "
              "general crit buff for 2 turns (20 sec). Corrected from 5 "
              "ranks to the real 2.")

T.node("malice", "Malice",
       "Increases your critical strike chance by 1% per rank.",
       0, 2, 5, effects={"crit_chance_physical": 1.0},
       source="WotLK row 0: 'Increases your critical strike chance by 5%' "
              "over 5 ranks. Built verbatim. The outgoing version was "
              "2 points of crit on Mutilate and Eviscerate specifically, "
              "which is a different talent - and it mattered, because "
              "Lethality and Seal Fate below both pay off crit, so the "
              "tree's whole engine was running on a per-ability trickle.")

# ----------------------------------------------------------------- tier 1
T.node("ruthlessness", "Ruthlessness",
       "Your finishing moves have a 20% chance per rank to award a combo "
       "point.",
       1, -4, 3,
       proc={"trigger": "on_cast", "chance": 20, "icd": 0,
             "ability_filter": FINISHERS,
             "grant_resource": {"resource": "combo", "amount": 20}},
       connected_to=["improved_eviscerate"],
       source="WotLK row 1: 'Gives your melee finishing moves a 20%/40%/60% "
              "chance to add a combo point to your target.' Built verbatim "
              "now that combo points exist. The outgoing version was a "
              "3-energy cost cut on Eviscerate.")

T.node("vigor", "Vigor",
       "You fight on past exhaustion, recovering 10 Energy whenever you "
       "strike.",
       1, -2, 1,
       proc={"trigger": "on_damage_cast", "chance": 100, "icd": 2,
             "grant_resource": {"resource": "energy", "amount": 10}},
       connected_to=["improved_eviscerate"],
       source="WotLK row 1, NEW to our tree: 'Increases your maximum Energy "
              "by 10.' DEPARTURE - max_energy_bonus is DEAD DATA. Probed "
              "with tools/probe_talent_key.py: it reaches the talent bus "
              "and has zero read sites, and the project had already "
              "recorded it as dead. A larger pool is not expressible, so "
              "the talent delivers the same thing the real one does in "
              "practice - more Energy to spend - as 10 Energy on a strike "
              "every other turn.")

T.node("blood_spatter", "Blood Spatter",
       "Increases the damage of your Garrote and Rupture by 15% per rank.",
       1, 0, 2,
       effects={"ability_rogue_garrote_damage": 0.15,
                "ability_rogue_rupture_damage": 0.15},
       connected_to=["remorseless_attacks"],
       source="WotLK row 1, built verbatim - the real pair of abilities and "
              "the real 30% over 2 ranks. The outgoing version was 12% per "
              "rank on Rupture alone.")

T.node("improved_expose_armor", "Improved Expose Armor",
       "Reduces the Energy cost of your Expose Armor by 5 per rank.",
       1, 2, 2, effects={"ability_rogue_expose_armor_cost": 5},
       connected_to=["malice"],
       source="WotLK row 1, NEW to our tree, built verbatim: the real 10 "
              "Energy over 2 ranks. ability_<id>_cost is FLAT.")

T.node("lethality", "Lethality",
       "Increases the critical strike damage of your abilities by 6% per "
       "rank.",
       1, 4, 5, effects={"crit_damage_physical": 0.06},
       connected_to=["malice"],
       source="WotLK row 1: 'Increases the critical strike damage bonus of "
              "all combo point-generating abilities that do not require "
              "stealth by 30%' over 5 ranks. Scoping crit damage to a set "
              "of abilities is possible only one ability at a time via "
              "ability_<id>_crit_damage, and the 'do not require stealth' "
              "clause has no meaning here anyway, so this uses the "
              "school-wide crit_damage_physical at the real 6% per rank. "
              "That key is a FRACTION and is read at abilities.py:1460 "
              "inside a ternary - the probe reports no literal read site "
              "for it, which is a limitation of the probe, not evidence of "
              "death. The real talent requires Malice; connected_to "
              "reproduces that. The outgoing version was 3% damage "
              "scattered across Eviscerate and Envenom.")

T.node("puncturing_wounds", "Puncturing Wounds",
       "Increases the critical strike chance of your Backstab by 10% per "
       "rank and of your Mutilate by 5% per rank.",
       1, 6, 3,
       effects={"ability_rogue_backstab_crit": 10.0,
                "ability_rogue_mutilate_crit": 5.0},
       connected_to=["lethality"],
       source="WotLK row 1, built verbatim - the real 30% Backstab and 15% "
              "Mutilate over 3 ranks. The outgoing version had the "
              "Backstab half as damage rather than crit, and omitted "
              "Mutilate. ability_<id>_crit is PERCENTAGE POINTS.")

# ----------------------------------------------------------------- tier 2
T.node("fleet_footed", "Fleet Footed",
       "Increases your dodge by 1% per rank.",
       2, -4, 2, effects={"dodge": 1.0},
       connected_to=["ruthlessness"],
       source="WotLK row 2: 'Reduces the duration of all movement impairing "
              "effects by 30% and increases your movement speed by 15%.' "
              "DEPARTURE - this engine has neither movement speed nor "
              "snares, and there is no caster-side speed debuff at all. "
              "Light footwork becomes dodge. The outgoing version did the "
              "same thing at 2% per rank; reduced to 1% because this is a "
              "tier-2 filler, not a defensive pillar.")

T.node("vile_poisons", "Vile Poisons",
       "Increases the damage of your Deadly Poison and Envenom by 7% per "
       "rank.",
       2, -2, 3,
       effects={"ability_rogue_deadly_poison_damage": 0.07,
                "ability_rogue_envenom_damage": 0.07},
       connected_to=["vigor"],
       source="WotLK row 2: 'Increases the damage dealt by your poisons and "
              "Envenom ability by 20%' over 3 ranks, plus a 30% dispel "
              "resistance clause. The damage half is built verbatim. Dispel "
              "RESISTANCE does not exist - dispel_type marks what CAN be "
              "removed and nothing modifies the chance - so that half is "
              "dropped.")

T.node("cold_blood", "Cold Blood",
       "Teaches Cold Blood, guaranteeing a critical strike on your next "
       "offensive ability.",
       2, 0, 1, node_type="active",
       effects={"unlock_ability": "rogue_cold_blood"},
       connected_to=["blood_spatter"],
       source="WotLK row 2, kept - the ONLY unlock for rogue_cold_blood, "
              "which is requires_talent, so dropping this node would "
              "strand the ability (qa_abilities_obtainable). The real "
              "talent's '+100% crit chance on your next ability' is the "
              "ability's own business; there is no guaranteed-crit key for "
              "a talent to set.")

T.node("improved_poisons", "Improved Poisons",
       "Increases the potency of your Deadly Poison by 4% per rank.",
       2, 2, 5, effects={"ability_rogue_deadly_poison_potency": 0.04},
       connected_to=["improved_expose_armor"],
       source="WotLK row 2: 'Increases the chance to apply Deadly Poison to "
              "your target by 20% and the frequency of applying Instant "
              "Poison by 50%.' DEPARTURE - poisons here are ordinary "
              "abilities you cast, with no application-chance roll and no "
              "application frequency to raise, so there is nothing for the "
              "real talent to modify. Potency is the nearest real knob. "
              "Kept from the outgoing tree, which had reached the same "
              "conclusion.")

T.node("improved_kidney_shot", "Improved Kidney Shot",
       "Your Kidney Shot has a 33% chance per rank to leave the target "
       "taking 9% more damage from all sources for 2 turns.",
       2, 4, 3,
       proc={"trigger": "on_cast", "chance": 33, "icd": 0,
             "ability_filter": ["rogue_kidney_shot"],
             "apply_effect": {"effect_id": "improved_kidney_shot",
                              "name": "Improved Kidney Shot",
                              "effect_type": "debuff", "duration": 2,
                              "stat_mods": {"damage_taken_pct": 0.09}}},
       connected_to=["lethality"],
       source="WotLK row 2, NEW to our tree: 'While affected by your Kidney "
              "Shot ability, the target receives an additional 9% damage "
              "from all sources.' Built with the real 9%. It has to be a "
              "PROC rather than ability_rogue_kidney_shot_potency, because "
              "_potency scales a buff's OWN stat_mods and "
              "rogue_kidney_shot has an EMPTY stat_mods dict - there would "
              "be nothing to scale. damage_taken_pct is read RAW on both "
              "sides, so 0.09 is 9%; it is also one of the eight stat_mods "
              "a MONSTER can actually read. Ranked by chance because a "
              "proc's payload does not scale with points.")

T.node("quick_recovery", "Quick Recovery",
       "Increases all healing you receive by 10% per rank.",
       2, 6, 2, effects={"healing_taken_pct": 0.10},
       connected_to=["puncturing_wounds"],
       source="WotLK row 2: 'All healing effects on you are increased by "
              "20%. In addition, your finishing moves refund 80% of their "
              "Energy cost when they fail to hit.' The healing half is "
              "built verbatim over 2 ranks. The refund-on-miss half is "
              "dropped - there is no on-miss trigger, and the cast has "
              "already been charged by the time a miss is rolled. The "
              "outgoing version was a proc.")

# ----------------------------------------------------------------- tier 3
T.node("seal_fate", "Seal Fate",
       "Your critical strikes have a 20% chance per rank to award an "
       "additional combo point.",
       3, -1, 5,
       proc={"trigger": "on_crit", "chance": 20, "icd": 0,
             "grant_resource": {"resource": "combo", "amount": 20}},
       connected_to=["cold_blood"],
       source="WotLK row 3: 'Your critical strikes from abilities that add "
              "combo points have a 20%-100% chance to add an additional "
              "combo point.' Built faithfully now that combo points exist - "
              "the real 20%-per-rank curve to 100% at 5 ranks. The "
              "'abilities that add combo points' restriction is dropped "
              "rather than filtered, because on_crit fires per damaging "
              "hit and listing the nine generators in an ability_filter "
              "would also exclude the auto-attack crit the real talent "
              "does count. The real talent requires Cold Blood, which "
              "connected_to reproduces.")

T.node("murder", "Murder",
       "Increases all damage you deal by 2% per rank.",
       3, 1, 2, effects={"all_damage": 0.02},
       connected_to=["improved_poisons"],
       source="WotLK row 3: 'Increases all damage caused by 4%' over 2 "
              "ranks. Built verbatim - a genuine flat scalar in the real "
              "game too. The outgoing version was 8% damage on Garrote and "
              "Rupture, which is Blood Spatter's job.")

# ----------------------------------------------------------------- tier 4
T.node("deadly_brew", "Deadly Brew",
       "Applying Deadly Poison has a 50% chance per rank to also apply "
       "Crippling Poison.",
       4, -5, 2,
       proc={"trigger": "on_cast", "chance": 50, "icd": 0,
             "ability_filter": ["rogue_deadly_poison"],
             "cast_ability": "rogue_crippling_poison"},
       connected_to=["seal_fate"],
       source="WotLK row 4, NEW to our tree: 'When you apply Instant, Wound "
              "or Mind-Numbing poison to a target, you have a 100% chance "
              "to apply Crippling poison.' Built with the real mechanic - "
              "cast_ability is a real proc payload (status_effects.py:1530) "
              "and both poisons exist here. Only Deadly Poison is in the "
              "filter because Instant, Wound and Mind-Numbing do not exist. "
              "50% per rank reaches the real 100% at 2 ranks.")

T.node("focused_attacks", "Focused Attacks",
       "Your critical strikes have a 33% chance per rank to restore 10 "
       "Energy.",
       4, -3, 3,
       proc={"trigger": "on_crit", "chance": 33, "icd": 0,
             "grant_resource": {"resource": "energy", "amount": 10}},
       connected_to=["seal_fate"],
       source="WotLK row 4, NEW to our tree: 'Your melee critical strikes "
              "have a 100% chance to give you 2 energy.' on_crit and the "
              "Energy grant are both real. 2 Energy against a 100-point "
              "pool regenerating 25 a turn is beneath notice here, so the "
              "amount is 10 and the chance carries the rank curve to 99%, "
              "which is the only way a multi-rank proc can scale.")

T.node("overkill", "Overkill",
       "A killing blow restores 30 Energy.",
       4, -1, 1,
       proc={"trigger": "on_kill", "chance": 100, "icd": 0,
             "grant_resource": {"resource": "energy", "amount": 30}},
       connected_to=["seal_fate"],
       source="WotLK row 4, NEW to our tree: 'While stealthed, and for 20 "
              "seconds after breaking stealth, you regenerate 30% "
              "additional energy.' DEPARTURE - no stealth, and no "
              "energy-regeneration key either (energy_regen and "
              "energy_regen_pct are both dead data). The talent is about "
              "Energy arriving faster at the start of a fight; on_kill is "
              "the nearest real moment, and 30 keeps the real number. The "
              "real talent is Mutilate's prerequisite, which connected_to "
              "preserves below.")

T.node("deadened_nerves", "Deadened Nerves",
       "Reduces all damage you take by 2% per rank, and by a further 5% per rank "
       "while you are below half health.",
       4, 1, 3,
       effects={"damage_taken_pct": -0.02,
                # PER RANK, like every other effect value - 0.05 x 3 ranks
                # is the 15% the dropped Assassin's Resolve granted. First
                # authored as 0.15, which measured as FORTY-FIVE PERCENT on
                # a live rogue at full rank. Nothing flagged it: the key is
                # real, the sign is right, and audit_talents does not know
                # what magnitude was intended.
                "low_health_damage_reduction_pct": 0.05},
       connected_to=["murder"],
       source="WotLK row 4: 'Reduces all damage taken by 6%' over 3 ranks, "
              "built verbatim - damage_taken_pct is read RAW on both sides, "
              "so -0.02 per rank is -6% at full rank. The low-health half "
              "is inherited from the DROPPED Assassin's Resolve, a "
              "Cataclysm talent with no WotLK counterpart: rather than lose "
              "a real working conditional, it moves onto the tree's actual "
              "damage-reduction talent. low_health_damage_reduction_pct "
              "reads the ACTOR's own health and defaults to a 50% "
              "threshold, so low_health_threshold_pct is not authored.")

T.node("find_weakness", "Find Weakness",
       "Increases all damage you deal by 2% per rank.",
       4, 3, 3, effects={"all_damage": 0.02},
       connected_to=["murder"],
       source="WotLK row 4: 'Offensive ability damage increased by 6%' over "
              "3 ranks. all_damage is the closest real key - there is no "
              "ability-versus-autoattack split - so it is built at 2% per "
              "rank. Stacks with Murder, as the real pair does. The "
              "outgoing version was a proc.")

# ----------------------------------------------------------------- tier 5
T.node("master_poisoner", "Master Poisoner",
       "Increases your critical strike chance by 1% per rank.",
       5, -3, 3, effects={"crit_chance_physical": 1.0},
       connected_to=["focused_attacks"],
       source="WotLK row 5: 'Increases the critical hit chance of all "
              "attacks made against any target you have poisoned by 3%, "
              "reduces the duration of all Poison effects applied to you by "
              "50%, and gives Envenom a 100% chance not to consume Deadly "
              "Poison.' DEPARTURE on all three clauses - nothing reads "
              "whether the TARGET carries a given debuff, nothing modifies "
              "an incoming effect's duration by school, and no proc flag "
              "prevents a consume. The crit is kept unconditionally at the "
              "real 1% per rank, which is strictly weaker than the real "
              "talent against a poisoned target and stronger against an "
              "unpoisoned one.")

T.node("mutilate", "Mutilate",
       "Teaches Mutilate, attacking with both weapons and awarding combo "
       "points.",
       5, -1, 1, node_type="active",
       effects={"unlock_ability": "rogue_mutilate"},
       connected_to=["overkill"],
       source="WotLK row 5, kept - the ONLY unlock for rogue_mutilate, "
              "which is requires_talent, so dropping it would strand the "
              "ability. The real talent requires Overkill, which "
              "connected_to reproduces. 'Awards 2 combo points' is now "
              "partly true: rogue_mutilate is a combo generator granting "
              "one point. The '20% more damage against Poisoned targets' "
              "clause needs a target-debuff read, which does not exist.")

T.node("cut_to_the_chase", "Cut to the Chase",
       "Your Eviscerate and Envenom have a 20% chance per rank to quicken "
       "your attacks by 30% for 3 turns.",
       5, 1, 5,
       proc={"trigger": "on_cast", "chance": 20, "icd": 0,
             "ability_filter": ["rogue_eviscerate", "rogue_envenom"],
             "apply_effect": {"effect_id": "cut_to_the_chase",
                              "name": "Cut to the Chase",
                              "effect_type": "buff", "duration": 3,
                              "stat_mods": {"haste": 30},
                              "on_target": False}},
       connected_to=["find_weakness"],
       source="WotLK row 5: 'Your Eviscerate and Envenom abilities have a "
              "100% chance to refresh your Slice and Dice duration to its 5 "
              "combo point maximum.' DEPARTURE - nothing in this engine can "
              "refresh or extend ANOTHER buff's duration from a proc. The "
              "real talent's whole purpose is keeping Slice and Dice up, so "
              "the finishers grant its effect directly instead: haste 30 is "
              "exactly rogue_slice_and_dice's own stat_mod. The real "
              "ability pair and the real 100%-at-full-rank are kept.")

T.node("turn_the_tables", "Turn the Tables",
       "Avoiding an attack has a 33% chance per rank to raise your critical "
       "strike chance by 6% for 2 turns.",
       5, 3, 3,
       proc={"trigger": "on_avoid", "chance": 33, "icd": 1,
             "apply_effect": {"effect_id": "turn_the_tables",
                              "name": "Turn the Tables",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"crit_chance_physical": 6},
                              "on_target": False}},
       connected_to=["find_weakness"],
       source="WotLK row 5: 'Whenever anyone in your party or raid blocks, "
              "dodges, or parries an attack your chance to critically hit "
              "with all combo moves is increased by 6% for 8 sec.' "
              "DEPARTURE on the source only - a talent effect can never "
              "reach an ally and no trigger reports a party member's "
              "avoidance, so it fires on the rogue's own. on_avoid covers "
              "block, dodge and parry together, which is exactly the real "
              "talent's list. The real 6% and the real 8 seconds (2 turns) "
              "are kept. NOTE: on an avoidance trigger the incoming amount "
              "is ZERO, so a bonus_pct or leech_pct payload would be "
              "worthless here - apply_effect is the right shape.")

# ----------------------------------------------------------------- tier 6
T.node("hunger_for_blood", "Hunger For Blood",
       "Applying a bleed enrages you, increasing all your damage by 5% for "
       "3 turns.",
       6, 1, 1,
       proc={"trigger": "on_cast", "chance": 100, "icd": 0,
             "ability_filter": ["rogue_rupture", "rogue_garrote"],
             "apply_effect": {"effect_id": "hunger_for_blood",
                              "name": "Hunger For Blood",
                              "effect_type": "buff", "duration": 3,
                              "stat_mods": {"all_damage": 0.05},
                              "on_target": False}},
       connected_to=["cut_to_the_chase"],
       source="WotLK row 10, the capstone: 'Enrages you, increasing all "
              "damage caused by 5%. Requires a bleed effect to be active on "
              "the target. Lasts 1 min.' DEPARTURE on the gate - nothing "
              "reads a debuff on the target, so 'requires a bleed' cannot "
              "be checked. Instead the two bleeds themselves grant it, "
              "which satisfies the same condition from the other direction: "
              "you cannot have it without having applied a bleed. The real "
              "5% is kept; 1 minute becomes 3 turns, the standard bucket "
              "for a maintained window.")


def main():
    return T.write(was="23 nodes, 65 points - 9 proc, 10 ability-scoped, "
                       "2 flat stat, 2 unlock, 1 conditional")


if __name__ == "__main__":
    sys.exit(main())
