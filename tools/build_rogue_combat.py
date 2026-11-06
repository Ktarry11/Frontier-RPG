#!/usr/bin/env python3
"""Rebuild Rogue Combat from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_rogue_combat.py

SOURCE: data/reference/wotlk/rogue.json, from the game's own Spell.dbc.
Worksheet: data/reference/wotlk_worksheets/rogue.md.

ROLE: the sustained-damage, weapon-centric spec. Where Assassination
bleeds and Subtlety opens, Combat just keeps swinging - more attacks, more
Energy, more uptime.

THE CENTRAL PROBLEM WITH THIS TREE, stated up front because it shapes a
third of it: WEAPON TYPE DOES NOT EXIST IN THIS ENGINE. There is no
weapon-type key of any kind, and no off-hand. Combat is the WotLK tree
most built around both:

    Dual Wield Specialization   "+50% offhand damage"
    Close Quarters Combat       "Requires Daggers, Fist Weapons"
    Mace Specialization         "attacks with maces ignore 15% armor"
    Hack and Slash              "Requires One-Handed Axes, Swords"
    Combat Potency              "off-hand melee attacks"
    Unfair Advantage            "100% of your MAIN HAND weapon's damage"
    Blade Twisting              "Requires Melee Weapon"

Seven talents, all gated on equipment this engine cannot inspect. Each is
rebuilt as the EFFECT the real talent produces, with the weapon gate
dropped - so Mace Specialization becomes armour penetration outright
rather than armour penetration with a mace, and Combat Potency fires on
any swing rather than an off-hand one. That is a real loss of texture and
it is recorded per node rather than smoothed over.

UNIT CONVENTIONS, probed with tools/probe_talent_key.py:

    parry, dodge, expertise, haste   PERCENTAGE POINTS
    hit_rating                       PERCENTAGE POINTS
    crit_chance_physical             PERCENTAGE POINTS
    armor_penetration_pct            PERCENTAGE POINTS (lands /100)
    attack_power_pct                 PERCENTAGE POINTS
    stamina_pct                      PERCENTAGE POINTS
    all_damage, crit_damage_physical FRACTION
    damage_taken_pct                 RAW on both sides
    ability_<id>_duration            FLAT turns, positive EXTENDS
    ability_<id>_cost                FLAT
    ability_<id>_cooldown            FLAT turns

extra_attack is a BOOLEAN - exactly one extra attack, no count - which is
what Hack and Slash and Unfair Advantage both want.

energy_regen and energy_regen_pct ARE BOTH DEAD DATA, which matters here
because Vitality and Adrenaline Rush are both written as Energy
regeneration. Vitality is rebuilt as a recurring Energy proc; Adrenaline
Rush stays an unlock, since the ability itself is where that lives.

KEPT MANDATORY: Adrenaline Rush and Evasion are the only unlocks for
rogue_adrenaline_rush and rogue_evasion, both requires_talent. Note the
outgoing tree carried the Evasion unlock on a node whose talent_id was
rogue_combat_RIPOSTE while its display name was "Evasion" - a leftover
from an earlier pass. Both talents are real in WotLK, so this tree now has
Riposte and Evasion as separate, correctly-named nodes.

ALSO FIXED HERE, as data rather than talents: rogue_blade_flurry and
rogue_killing_spree had unlock nodes but were NOT requires_talent, so both
were trainable anyway and both talent points bought nothing - the same
half-finished gating found on the Druid forms. Both are real WotLK talents
and are now gated. See tools/gate_rogue_talent_abilities.py.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

FINISHERS = ["rogue_eviscerate", "rogue_rupture", "rogue_slice_and_dice",
             "rogue_expose_armor", "rogue_kidney_shot", "rogue_envenom"]

T = Tree("rogue_combat", "Rogue Combat",
         "Relentless weapon work - more swings, more Energy, more uptime.")

# ----------------------------------------------------------------- tier 0
T.node("improved_gouge", "Improved Gouge",
       "Increases the duration of your Gouge by 1 turn per rank.",
       0, -2, 3, effects={"ability_rogue_gouge_duration": 1},
       source="WotLK row 0: 'Increases the effect duration of your Gouge "
              "ability by 0.5/1/1.5 sec.' Built as duration, which is what "
              "the real talent does - ability_<id>_duration is FLAT turns "
              "and POSITIVE EXTENDS. The outgoing version reduced Gouge's "
              "COOLDOWN instead, which is a different talent.")

T.node("improved_sinister_strike", "Improved Sinister Strike",
       "Reduces the Energy cost of your Sinister Strike by 3 per rank.",
       0, 0, 2, effects={"ability_rogue_sinister_strike_cost": 3},
       source="WotLK row 0: 'Reduces the Energy cost of your Sinister "
              "Strike ability by 3/5.' Built verbatim over the real 2 ranks "
              "(the outgoing version had 3 ranks).")

T.node("dual_wield_specialization", "Dual Wield Specialization",
       "Your relentless two-weapon work increases all your damage by 2% "
       "per rank.",
       0, 2, 5, effects={"all_damage": 0.02},
       source="WotLK row 0: 'Increases the damage done by your offhand "
              "weapon by 50%.' DEPARTURE - there is NO off-hand in this "
              "engine and no off-hand damage key. A main-and-off-hand rogue "
              "deals roughly a third of its damage with the off hand, so "
              "+50% off-hand is on the order of +15% total; 2% per rank "
              "reaches 10%, deliberately under that rather than over, "
              "because the conversion is an estimate and this is a "
              "5-point tier-0 node. The outgoing version was a proc.")

# ----------------------------------------------------------------- tier 1
T.node("improved_slice_and_dice", "Improved Slice and Dice",
       "Increases the duration of your Slice and Dice by 1 turn per rank.",
       1, -5, 2, effects={"ability_rogue_slice_and_dice_duration": 1},
       connected_to=["improved_gouge"],
       source="WotLK row 1: 'Increases the duration of your Slice and Dice "
              "ability by 25%/50%.' Slice and Dice runs 3 turns here, so a "
              "50% extension is +1.5 turns; 1 per rank over 2 ranks "
              "reaches +2, the nearest whole-turn pair. Kept from the "
              "outgoing tree, corrected from 3 ranks to the real 2.")

T.node("endurance", "Endurance",
       "Reduces the cooldown of your Sprint and Evasion by 1 turn per rank "
       "and increases your Stamina by 2% per rank.",
       1, -3, 2,
       effects={"ability_rogue_sprint_cooldown": 1,
                "ability_rogue_evasion_cooldown": 1,
                "stamina_pct": 2.0},
       connected_to=["improved_gouge"],
       source="WotLK row 1, built verbatim including the real Stamina half "
              "that the outgoing version omitted. 'Reduces the cooldown of "
              "your Sprint and Evasion abilities by 30/60 sec and increases "
              "your total Stamina by 2%/4%.' stamina_pct is PERCENTAGE "
              "POINTS.")

T.node("deflection", "Deflection",
       "Increases your parry chance by 2% per rank.",
       1, -1, 3, effects={"parry": 2.0},
       connected_to=["improved_sinister_strike"],
       source="WotLK row 1: 'Increases your Parry chance by 2%/4%/6%.' "
              "Built verbatim at the real 3 ranks; the outgoing version was "
              "5 ranks of 1%. parry is PERCENTAGE POINTS, though it lands "
              "on the attribute through a diminishing-returns curve, so the "
              "realised value is slightly under the nominal one.")

T.node("riposte", "Riposte",
       "Parrying an attack lets you riposte, striking back immediately and "
       "awarding a combo point.",
       1, 1, 1,
       proc={"trigger": "on_parry", "chance": 100, "icd": 1,
             "extra_attack": True,
             "grant_resource": {"resource": "combo", "amount": 20}},
       connected_to=["deflection"],
       source="WotLK row 2: 'A strike that becomes active after parrying an "
              "opponent's attack. This attack deals 150% weapon damage and "
              "slows their melee attack speed by 20% for 30 sec. Awards 1 "
              "combo point.' Built as the real reactive mechanic: on_parry "
              "is a real trigger, extra_attack is a BOOLEAN granting "
              "exactly one extra attack, and the combo point is real now. "
              "The attack-speed slow is dropped to keep the payload to what "
              "an avoidance trigger can carry - NOTE that on_parry reports "
              "an incoming amount of ZERO, so any bonus_pct or leech_pct "
              "payload here would be worth nothing. The real talent "
              "requires Deflection, which connected_to reproduces. The "
              "outgoing tree had no Riposte - its node of that talent_id "
              "was displaying as 'Evasion' and carrying Evasion's unlock.")

T.node("close_quarters_combat", "Close Quarters Combat",
       "Increases your critical strike chance by 1% per rank.",
       1, 3, 5, effects={"crit_chance_physical": 1.0},
       connected_to=["dual_wield_specialization"],
       source="WotLK row 1: 'Requires Daggers, Fist Weapons. Increases your "
              "chance to get a critical strike with Daggers and Fist "
              "Weapons by 1%-5%.' DEPARTURE - there is no weapon-type key, "
              "so the gate is dropped and the crit applies always. The real "
              "number is kept. The real talent requires Dual Wield "
              "Specialization, which connected_to reproduces.")

T.node("precision", "Precision",
       "Increases your chance to hit by 1% per rank.",
       1, 5, 5, effects={"hit_rating": 1.0},
       connected_to=["dual_wield_specialization"],
       source="WotLK row 1: 'Increases your chance to hit with weapon and "
              "poison attacks by 1%-5%.' Built verbatim and kept from the "
              "outgoing tree, which already had it right. hit_rating is "
              "PERCENTAGE POINTS - and note it is NOT a valid "
              "STAT_CONVERSION_TARGET, so it can be granted directly like "
              "this but never converted into from another stat.")

# ----------------------------------------------------------------- tier 2
T.node("improved_kick", "Improved Kick",
       "Your Kick deals 15% more damage per rank.",
       2, -5, 2, effects={"ability_rogue_kick_damage": 0.15},
       connected_to=["improved_slice_and_dice"],
       source="WotLK row 2: 'Gives your Kick ability a 50%/100% chance to "
              "silence the target for 2 sec.' DEPARTURE - there is no "
              "silence and no interrupt key in this engine; is_stun is the "
              "only incapacitate, and turning a Kick into a stun would make "
              "a tier-2 filler stronger than Kidney Shot. Delivered as Kick "
              "damage instead, which is the weakest honest reading of the "
              "talent and is recorded as such.")

T.node("mace_specialization", "Mace Specialization",
       "Your attacks ignore 3% of your target's armor per rank.",
       2, -3, 5, effects={"armor_penetration_pct": 3.0},
       connected_to=["endurance"],
       source="WotLK row 2: 'Your attacks with maces ignore up to 15% of "
              "your opponent's armor.' DEPARTURE on the weapon gate only - "
              "no weapon-type key - so the real 15% over 5 ranks applies "
              "always. armor_penetration_pct is PERCENTAGE POINTS: it lands "
              "on the attribute divided by 100, so 3.0 is 3%. Authoring "
              "0.03 would have shipped 0.03%. The outgoing version was a "
              "proc.")

T.node("improved_sprint", "Improved Sprint",
       "Reduces the cooldown of your Sprint by 1 turn per rank.",
       2, -1, 2, effects={"ability_rogue_sprint_cooldown": 1},
       connected_to=["deflection"],
       source="WotLK row 2: 'Gives a 100% chance to remove all Movement "
              "Impairing effects when you activate your Sprint ability.' "
              "DEPARTURE - no movement impairment exists to remove, and "
              "the three CoA talents authored as dispel_type 'movement' "
              "were found to remove nothing at all because that is not a "
              "real DispelType. Delivered as Sprint availability instead, "
              "which stacks with Endurance as the real pair does.")

T.node("blade_flurry", "Blade Flurry",
       "Teaches Blade Flurry, striking an additional nearby opponent.",
       2, 1, 1, node_type="active",
       effects={"unlock_ability": "rogue_blade_flurry"},
       connected_to=["riposte"],
       source="WotLK row 2, kept. rogue_blade_flurry was NOT requires_"
              "talent, so this node bought nothing - the ability was "
              "trainable anyway, the same half-finished gating found on the "
              "Druid forms. Blade Flurry IS a real WotLK talent, so the "
              "ability is now gated (tools/gate_rogue_talent_abilities.py) "
              "and this point finally buys it.")

T.node("lightning_reflexes", "Lightning Reflexes",
       "Increases your dodge by 2% per rank and your haste by 3% per rank.",
       2, 3, 3, effects={"dodge": 2.0, "haste": 3.0},
       connected_to=["close_quarters_combat"],
       source="WotLK row 2: 'Increases your Dodge chance by 2%/4%/6% and "
              "gives you 10% melee haste.' Built with both halves - the "
              "outgoing version was 5 ranks of dodge alone and omitted the "
              "haste, which is the reason this talent is taken. 3% per rank "
              "reaches 9%, the nearest whole percent to the real 10%. Both "
              "keys are PERCENTAGE POINTS.")

T.node("hack_and_slash", "Hack and Slash",
       "Your strikes have a 5% chance per rank to grant an extra attack.",
       2, 5, 5,
       proc={"trigger": "on_weapon_swing", "chance": 5, "icd": 0,
             "extra_attack": True},
       connected_to=["precision"],
       source="WotLK row 2: 'Requires One-Handed Axes, One-Handed Swords. "
              "Gives you a 5% chance to get an extra attack on the same "
              "target after hitting your target with your Sword or Axe.' "
              "Built as the real mechanic minus the weapon gate, which does "
              "not exist. extra_attack is a BOOLEAN - exactly one extra "
              "attack, there is no count - which is precisely what the real "
              "talent grants. 5% per rank reaches 25%, higher than the real "
              "flat 5%, because a proc's chance is the ONLY thing that "
              "scales with points: the alternative was a 1-rank node, and "
              "the real talent is 5 ranks.")

T.node("aggression", "Aggression",
       "Increases the damage of your Sinister Strike, Backstab and "
       "Eviscerate by 3% per rank.",
       2, 7, 5,
       effects={"ability_rogue_sinister_strike_damage": 0.03,
                "ability_rogue_backstab_damage": 0.03,
                "ability_rogue_eviscerate_damage": 0.03},
       connected_to=["precision"],
       source="WotLK row 2, built verbatim - the real three abilities and "
              "the real 15% over 5 ranks. Kept from the outgoing tree, "
              "which had it at 5% per rank (25% at full rank).")

# ----------------------------------------------------------------- tier 3
T.node("weapon_expertise", "Weapon Expertise",
       "Increases your expertise by 5 per rank.",
       3, -2, 2, effects={"expertise": 5.0},
       connected_to=["blade_flurry"],
       source="WotLK row 3: 'Increases your expertise by 5/10.' Built "
              "verbatim. expertise is PERCENTAGE POINTS and is a real key "
              "with real read sites - it reduces a target's dodge and parry "
              "against you, which is why Kyle's note that 'expertise is "
              "basically hit rating unless we can encode parry and dodge in "
              "enemies' led to creature avoidance being added for humanoids "
              "and bosses. The outgoing version granted hit_rating instead, "
              "which is the thing expertise was ALREADY indistinguishable "
              "from before that change - so this node is only now "
              "meaningfully different. The real talent requires Blade "
              "Flurry, which connected_to reproduces.")

T.node("blade_twisting", "Blade Twisting",
       "Increases the damage of your Sinister Strike and Backstab by 5% per "
       "rank, and your strikes have a 10% chance per rank to daze the "
       "target.",
       3, 0, 2,
       effects={"ability_rogue_sinister_strike_damage": 0.05,
                "ability_rogue_backstab_damage": 0.05},
       proc={"trigger": "on_damage_cast", "chance": 10, "icd": 1,
             "apply_effect": {"effect_id": "blade_twisting",
                              "name": "Blade Twisting",
                              "effect_type": "debuff", "duration": 2,
                              "stat_mods": {"haste": -15}}},
       connected_to=["lightning_reflexes"],
       source="WotLK row 3: 'Requires Melee Weapon. Increases the damage "
              "dealt by Sinister Strike and Backstab by 5%/10%, and your "
              "damaging melee attacks have a 5%/10% chance to Daze the "
              "target for 8 sec.' Built with BOTH halves - a node may carry "
              "effects AND a proc, and this is the clearest case for it in "
              "the tree. Daze has no engine equivalent, so it is a haste "
              "debuff on the target for 8 seconds (2 turns). The weapon "
              "gate is dropped. The outgoing version was a proc only, with "
              "no damage half.")

# ----------------------------------------------------------------- tier 4
T.node("vitality", "Vitality",
       "Your strikes return 15 Energy, once every other turn.",
       4, -4, 3,
       proc={"trigger": "on_damage_cast", "chance": 33, "icd": 2,
             "grant_resource": {"resource": "energy", "amount": 15}},
       connected_to=["weapon_expertise"],
       source="WotLK row 4: 'Increases your Energy regeneration rate by "
              "8%/16%/25%.' DEPARTURE - energy_regen, energy_regen_pct and "
              "resource_regen_pct are ALL DEAD DATA in this engine, "
              "confirmed by probe and already recorded in the project. "
              "Energy regeneration is a flat 25 per turn in "
              "restore_resources_between_turns and nothing modifies it. "
              "Delivered as recurring Energy on a strike instead, which is "
              "the same resource arriving by a different route. The "
              "outgoing version was flat agility_pct, which is not this "
              "talent at all.")

T.node("throwing_specialization", "Throwing Specialization",
       "Increases the damage of your Shiv by 10% per rank.",
       4, -2, 2, effects={"ability_rogue_shiv_damage": 0.10},
       connected_to=["weapon_expertise"],
       source="WotLK row 4, NEW to our tree: 'Increases the range of Throw "
              "and Deadly Throw by 2/4 yards and gives your Deadly Throw a "
              "50%/100% chance to interrupt the target for 3 sec.' "
              "DEPARTURE - no range, no Throw or Deadly Throw ability, and "
              "no interrupt key. Of the rogue's abilities, Shiv is the "
              "closest to a thrown-weapon strike, so the node pays out "
              "there. This is the thinnest substitution in the tree and is "
              "marked as such: almost nothing of the real talent survives "
              "except that it is a small offensive utility node at tier 4.")

T.node("adrenaline_rush", "Adrenaline Rush",
       "Teaches Adrenaline Rush, flooding you with Energy.",
       4, 0, 1, node_type="active",
       effects={"unlock_ability": "rogue_adrenaline_rush"},
       connected_to=["blade_twisting"],
       source="WotLK row 4, kept - the ONLY unlock for "
              "rogue_adrenaline_rush, which is requires_talent, so dropping "
              "it would strand the ability. The real talent's '+100% Energy "
              "regeneration for 15 sec' lives in the ability rather than "
              "here, which is just as well given that no regeneration key "
              "is read.")

T.node("nerves_of_steel", "Nerves of Steel",
       "Reduces all damage you take by 1% per rank.",
       4, 2, 2, effects={"damage_taken_pct": -0.01},
       connected_to=["blade_twisting"],
       source="WotLK row 4, NEW to our tree: 'Reduces damage taken while "
              "affected by Stun and Fear effects by 15%/30%.' DEPARTURE - "
              "nothing reads whether the ACTOR is currently stunned as a "
              "condition on a damage-taken modifier (is_stun exists on the "
              "effect, but there is no conditional damage key keyed to it), "
              "and there is no Fear at all. Delivered unconditionally at a "
              "much smaller number - 1% per rank against the real 15% - "
              "precisely because it is now always on rather than "
              "situational. damage_taken_pct is read RAW.")

T.node("combat_potency", "Combat Potency",
       "Your swings have a 20% chance per rank to generate 15 Energy.",
       4, 4, 5,
       proc={"trigger": "on_weapon_swing", "chance": 20, "icd": 0,
             "grant_resource": {"resource": "energy", "amount": 15}},
       connected_to=["aggression"],
       source="WotLK row 4: 'Gives your successful off-hand melee attacks a "
              "20% chance to generate 15 Energy.' Built with the real "
              "chance and the real 15 Energy; the off-hand gate is dropped "
              "because there is no off-hand, so it fires on any swing. "
              "Kept from the outgoing tree, which had this right. NOTE the "
              "chance reaches 100% at 5 ranks here where the real talent "
              "stays at 20% - unavoidable, since a proc's chance is the "
              "only thing points can scale.")

# ----------------------------------------------------------------- tier 5
T.node("unfair_advantage", "Unfair Advantage",
       "Dodging an attack has a 50% chance per rank to let you strike back "
       "immediately.",
       5, -3, 2,
       proc={"trigger": "on_dodge", "chance": 50, "icd": 1,
             "extra_attack": True},
       connected_to=["vitality"],
       source="WotLK row 5, NEW to our tree: 'Whenever you dodge an attack "
              "you gain an Unfair Advantage, striking back for 100% of your "
              "main hand weapon's damage. This cannot occur more than once "
              "per second.' Built as the real mechanic - on_dodge is real "
              "and extra_attack is exactly 'strike back once'. icd 1 is the "
              "once-per-second clause. 50% per rank reaches the real 100% "
              "at 2 ranks. The main-hand clause is moot with no off-hand.")

T.node("surprise_attacks", "Suprise Attacks",
       "Increases the damage of your Sinister Strike, Backstab, Shiv, "
       "Hemorrhage and Gouge by 10%.",
       5, -1, 1,
       effects={"ability_rogue_sinister_strike_damage": 0.10,
                "ability_rogue_backstab_damage": 0.10,
                "ability_rogue_shiv_damage": 0.10,
                "ability_rogue_hemorrhage_damage": 0.10,
                "ability_rogue_gouge_damage": 0.10},
       connected_to=["adrenaline_rush"],
       source="WotLK row 9: 'Your finishing moves can no longer be dodged, "
              "and the damage dealt by your Sinister Strike, Backstab, "
              "Shiv, Hemorrhage and Gouge abilities is increased by 10%.' "
              "The damage half is built verbatim across all five real "
              "abilities. 'Can no longer be dodged' is dropped - there is "
              "no per-ability undodgeable flag, and expertise is the only "
              "avoidance-reduction channel. The real talent requires "
              "Adrenaline Rush, which connected_to reproduces. The name "
              "keeps Blizzard's original typo, 'Suprise Attacks', because "
              "that is what the source data says. The outgoing version "
              "covered Eviscerate and Envenom, which are finishers - the "
              "opposite of this talent's list.")

T.node("prey_on_the_weak", "Prey on the Weak",
       "Increases your damage by 3% per rank against targets below 35% "
       "health.",
       5, 1, 5, effects={"low_health_damage_pct": 0.03},
       connected_to=["combat_potency"],
       source="WotLK row 9: 'Your critical strike damage is increased by "
              "4%-20% when the target has less health than you (as a "
              "percentage of total health).' DEPARTURE - nothing compares "
              "two combatants' health percentages, so the condition becomes "
              "the engine's own low-health conditional: "
              "low_health_damage_pct reads the TARGET's health and defaults "
              "to a 35% threshold. That is narrower than the real talent "
              "(which fires whenever the target is merely worse off than "
              "you) so the number is higher per rank to compensate: 3% "
              "reaching 15%. It modifies all damage rather than crit "
              "damage specifically. low_health_threshold_pct is NOT "
              "authored - it SUMS across talents and the default is "
              "already right. The outgoing version was flat crit chance "
              "with no condition at all.")

T.node("savage_combat", "Savage Combat",
       "Increases your attack power by 2% per rank.",
       5, 3, 2, effects={"attack_power_pct": 2.0},
       connected_to=["combat_potency"],
       source="WotLK row 9: 'Increases your total attack power by 2%/4% and "
              "all physical damage caused to enemies you have poisoned is "
              "increased by 2%/4%.' The attack-power half is built verbatim. "
              "The poisoned-target half needs a target-debuff read, which "
              "does not exist. attack_power_pct is PERCENTAGE POINTS - "
              "audit_talents has caught this being authored as a fraction "
              "elsewhere in the project. The outgoing version was a proc.")

# ----------------------------------------------------------------- tier 6
T.node("killing_spree", "Killing Spree",
       "Teaches Killing Spree, attacking relentlessly while taking less "
       "notice of anything else.",
       6, 1, 1, node_type="active",
       effects={"unlock_ability": "rogue_killing_spree"},
       connected_to=["prey_on_the_weak"],
       source="WotLK row 10, the capstone, kept. Like Blade Flurry, "
              "rogue_killing_spree was NOT requires_talent, so this point "
              "bought nothing - the ability was trainable regardless. "
              "Killing Spree IS a real WotLK capstone talent, so the "
              "ability is now gated and the point buys it. Corrected from "
              "2 points to the real 1.")


def main():
    return T.write(was="23 nodes, 69 points - 6 proc, 10 ability-scoped, "
                       "6 flat stat, 4 unlock")


if __name__ == "__main__":
    sys.exit(main())
