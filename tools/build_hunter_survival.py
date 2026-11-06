#!/usr/bin/env python3
"""Rebuild Hunter Survival from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_hunter_survival.py

SOURCE: data/reference/wotlk/hunter.json (from Spell.dbc).
Worksheet: data/reference/wotlk_worksheets/hunter.md.

ROLE: traps, bleeds and Agility. The tree that turns Stamina into attack
power and Explosive Shot into the hunter's hardest hit.

HUNTER VS. WILD IS A REAL CONVERSION. "+30% attack power from Stamina"
maps onto attack_power_from_stamina_pct - attack_power is a valid
STAT_CONVERSION_TARGET and stamina a valid source - and it was MEASURED
LIVE at +14 attack power off a hunter's Stamina. The unit is a RAW
MULTIPLIER (character.py:1551).

THREE MANDATORY UNLOCKS, all at the deep end of the tree and all with real
prerequisites in the real game: hunter_wyvern_sting, hunter_black_arrow and
hunter_explosive_shot are requires_talent and unlocked only from here.

TRAPS ARE WHERE THIS TREE LOSES MOST. Real Survival is built on Frost Trap,
Snake Trap, Immolation Trap, Freezing Arrow and the "target is trapped"
condition, and we have exactly two traps - Explosive Trap and Freezing
Trap. Lock and Load, Entrapment and Point of No Escape all need to read
whether a target is trapped or frozen, and NOTHING in this engine reads a
debuff on a target. Each is rebuilt as an unconditional version.

ABILITIES THE REAL TREE WANTS AND WE LACK: Raptor Strike, Mongoose Bite,
Counterattack, Scatter Shot, Kill Shot, Frost Trap, Snake Trap, Immolation
Trap. Savage Strikes, Counterattack, Scatter Shot, Survival Tactics and
Hawk Eye are DROPPED.

UNIT CONVENTIONS: agility_pct / stamina_pct / parry / crit_chance_physical
are PERCENTAGE POINTS; damage_taken_pct is read RAW;
low_health_damage_reduction_pct / *_from_*_pct are FRACTIONS.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

TRAPS = ["hunter_explosive_trap", "hunter_freezing_trap"]

T = Tree("hunter_survival", "Hunter Survival",
         "Traps, poisons and hard-won instinct - the hunter who comes "
         "home.")

# ----------------------------------------------------------------- tier 0
T.node("improved_tracking", "Improved Tracking",
       "Increases all your damage by 1% per rank.",
       0, -2, 5, effects={"all_damage": 0.01},
       source="WotLK row 0: 'While tracking Beasts, Demons, Dragonkin, "
              "Elementals, Giants, Humanoids and Undead, all damage done "
              "to those targets is increased by 1%-5%.' DEPARTURE - "
              "NOTHING in this engine reads a creature type, and there is "
              "no tracking state either. Delivered unconditionally at the "
              "real per-rank value, which in practice is what the real "
              "talent amounts to once you are tracking the right thing. "
              "The outgoing version was Serpent Sting damage.")

T.node("surefooted", "Surefooted",
       "Increases your chance to hit by 1% per rank.",
       0, 0, 3, effects={"hit_rating": 1.0},
       source="WotLK row 1: 'Reduces the duration of movement impairing "
              "effects by 10%/20%/30%.' DEPARTURE - there is no movement "
              "impairment at all, and the three CoA talents authored as "
              "dispel_type 'movement' were found to remove nothing, "
              "because that is not a real DispelType. Sure footing becomes "
              "accuracy. Kept from the outgoing tree.")

T.node("survivalist", "Survivalist",
       "Increases your Stamina by 2% per rank.",
       0, 2, 5, effects={"stamina_pct": 2.0},
       source="WotLK row 1, built verbatim: 'Increases your Stamina by "
              "2%-10%.' stamina_pct is PERCENTAGE POINTS. The outgoing "
              "version granted max_health_pct, which is downstream of "
              "Stamina rather than the talent - and the distinction "
              "matters here, because Hunter vs. Wild converts STAMINA into "
              "attack power. It is Hunter vs. Wild's prerequisite in the "
              "real tree, preserved below.")

# ----------------------------------------------------------------- tier 1
T.node("entrapment", "Entrapment",
       "Your traps have a 20% chance per rank to hold the target fast for 1 "
       "turn.",
       1, -4, 3,
       proc={"trigger": "on_cast", "chance": 20, "icd": 0,
             "ability_filter": TRAPS,
             "apply_effect": {"effect_id": "entrapment",
                              "name": "Entrapment",
                              "effect_type": "debuff", "duration": 1,
                              "is_stun": True}},
       connected_to=["improved_tracking"],
       source="WotLK row 1: 'When your Frost Trap or Snake Trap are "
              "triggered you entrap all afflicted targets, preventing them "
              "from moving for 4 sec.' DEPARTURE - neither named trap "
              "exists, and 'when triggered' has no event (nothing fires on "
              "a trap being sprung). It fires on the trap being CAST "
              "instead, against the two traps we have. Preventing movement "
              "becomes is_stun, this engine's only incapacitate. The "
              "outgoing version extended Freezing Trap's duration.")

T.node("trap_mastery", "Trap Mastery",
       "Increases the damage of your Explosive Trap by 10% per rank and the "
       "duration of your Freezing Trap by 1 turn per rank.",
       1, -2, 3,
       effects={"ability_hunter_explosive_trap_damage": 0.10,
                "ability_hunter_freezing_trap_duration": 1},
       connected_to=["improved_tracking"],
       source="WotLK row 1, built verbatim for the two traps that exist: "
              "'Frost Trap and Freezing Trap - Increases the duration by "
              "10%/20%/30%. Immolation Trap, Explosive Trap and Black Arrow "
              "- increases the damage.' Kept from the outgoing tree, which "
              "covered Explosive Trap alone.")

T.node("deflection", "Deflection",
       "Increases your parry chance by 1% per rank.",
       1, 0, 3, effects={"parry": 1.0},
       connected_to=["surefooted"],
       source="WotLK row 1: 'Increases your chance to parry by 1%/2%/3%, "
              "and reduces the duration of all Disarm effects used against "
              "you.' The parry half is verbatim; Disarm duration is not "
              "modifiable. Kept from the outgoing tree, corrected from 5 "
              "ranks to the real 3. It is Counterattack's prerequisite in "
              "the real tree; Counterattack does not exist here.")

T.node("survival_instincts", "Survival Instincts",
       "Reduces all damage you take by 2% per rank and increases the "
       "critical chance of your shots by 2% per rank.",
       1, 2, 2,
       effects={"damage_taken_pct": -0.02,
                "ability_hunter_arcane_shot_crit": 2.0,
                "ability_hunter_steady_shot_crit": 2.0},
       connected_to=["survivalist"],
       source="WotLK row 1, built verbatim with both halves: 'Reduces all "
              "damage taken by 2%/4% and increases the critical strike "
              "chance of your Arcane Shot, Steady Shot and Explosive Shot "
              "by 2%/4%.' damage_taken_pct is read RAW on both sides. The "
              "outgoing version used low_health_damage_reduction_pct AND "
              "low_health_threshold_pct, which is Fiery Payback's shape and "
              "put this class one node from a summing-threshold breach.")

# ----------------------------------------------------------------- tier 2
T.node("hunter_vs_wild", "Hunter vs. Wild",
       "Increases your attack power by 10% of your Stamina per rank.",
       2, -4, 3,
       effects={"attack_power_from_stamina_pct": 0.10},
       connected_to=["entrapment"],
       source="WotLK row 2, built verbatim: 'Increases you and your pet's "
              "attack power and ranged attack power equal to 10%-30% of "
              "your total Stamina.' A REAL stat conversion - attack_power "
              "is a valid STAT_CONVERSION_TARGET and stamina a valid "
              "source. MEASURED LIVE at +14 attack power, so the key is a "
              "RAW MULTIPLIER and not a percentage (character.py:1551). The "
              "pet half cannot be built - a talent effect cannot reach the "
              "pet, which reads only pet_damage/health/armor from its "
              "owner. The real talent requires Survivalist, which "
              "connected_to reproduces and which is the Stamina that feeds "
              "this. The outgoing node was a proc with an empty effects "
              "dict.")

T.node("tnt", "T.N.T",
       "Increases the damage of your Explosive Trap, Explosive Shot and "
       "Black Arrow by 5% per rank.",
       2, -2, 3,
       effects={"ability_hunter_explosive_trap_damage": 0.05,
                "ability_hunter_explosive_shot_damage": 0.05,
                "ability_hunter_black_arrow_damage": 0.05},
       connected_to=["trap_mastery"],
       source="WotLK row 2, NEW to our tree, built verbatim for the three "
              "real abilities that exist: 'Increases the damage done by "
              "your Explosive Shot, Explosive Trap, Black Arrow and "
              "Immolation Trap by 5%/10%/15%.' Stacks with Trap Mastery on "
              "Explosive Trap, as the real pair does.")

T.node("killer_instinct", "Killer Instinct",
       "Increases your critical strike chance by 1% per rank.",
       2, 0, 3, effects={"crit_chance_physical": 1.0},
       connected_to=["deflection"],
       source="WotLK row 2, built verbatim: 'Increases your critical strike "
              "chance with all attacks by 1%/2%/3%.' The outgoing version "
              "granted per-ability crit. It is Wyvern Sting's prerequisite "
              "in the real tree, preserved below.")

T.node("lock_and_load", "Lock and Load",
       "Your traps have a 33% chance per rank to reset the cooldown of your "
       "Explosive Shot.",
       2, 2, 3,
       proc={"trigger": "on_cast", "chance": 33, "icd": 0,
             "ability_filter": TRAPS,
             "reset_cooldown": "hunter_explosive_shot"},
       connected_to=["survival_instincts"],
       source="WotLK row 2: 'You have a 100% chance when you trap a target "
              "with Freezing Trap, Freezing Arrow or Frost Trap to "
              "generate 2 charges of Lock and Load, causing your next 2 "
              "Explosive Shots to cost no mana and trigger no cooldown.' "
              "Built with the real spirit via reset_cooldown, a real proc "
              "payload (status_effects.py:1207), fired off the traps we "
              "have. Charges do not exist and 'when you trap a target' has "
              "no event, so it fires on the cast. Kept as a proc from the "
              "outgoing tree.")

# ----------------------------------------------------------------- tier 3
T.node("lightning_reflexes", "Lightning Reflexes",
       "Increases your Agility by 3% per rank.",
       3, -2, 5, effects={"agility_pct": 3.0},
       connected_to=["hunter_vs_wild"],
       source="WotLK row 3, NEW to our tree, built verbatim: 'Increases "
              "your Agility by 3%-15%.' agility_pct is PERCENTAGE POINTS "
              "and flows into both ranged and melee attack power, so this "
              "is the tree's broadest offensive node. It is Expose "
              "Weakness's prerequisite, preserved below.")

T.node("resourcefulness", "Resourcefulness",
       "Reduces the cost of your traps and Black Arrow by 20% per rank and "
       "their cooldown by 1 turn per rank.",
       3, 0, 3,
       effects={**{f"ability_{t}_cost_pct": 0.20 for t in TRAPS},
                "ability_hunter_black_arrow_cost_pct": 0.20,
                "ability_hunter_explosive_trap_cooldown": 1},
       connected_to=["lock_and_load"],
       source="WotLK row 3, built verbatim: 'Reduces the mana cost of all "
              "traps, melee abilities and Black Arrow by 20%-60% and "
              "reduces the cooldown.' There are no melee abilities in this "
              "kit to cover. Kept from the outgoing tree, which used the "
              "FLAT _cost key.")

# ----------------------------------------------------------------- tier 4
T.node("expose_weakness", "Expose Weakness",
       "Your critical strikes raise your attack power for 3 turns.",
       4, -4, 3,
       proc={"trigger": "on_crit", "chance": 33, "icd": 0,
             "apply_effect": {"effect_id": "expose_weakness",
                              "name": "Expose Weakness",
                              "effect_type": "buff", "duration": 3,
                              "stat_mods": {"attack_power": 120},
                              "on_target": False}},
       connected_to=["lightning_reflexes"],
       source="WotLK row 4: 'Your ranged criticals have a 100% chance to "
              "grant you Expose Weakness, increasing your attack power by "
              "an amount equal to 10%-30% of your Agility for 7 sec.' Built "
              "on the real trigger. Scaling a PROC's payload from a stat is "
              "not possible - stat conversions are a talent-effect "
              "mechanism, not a payload one - so attack_power 120 is flat. "
              "attack_power inside a status effect is FLAT and is summed "
              "from active effects like any gear bonus. The real talent "
              "requires Lightning Reflexes, reproduced. Kept as a proc from "
              "the outgoing tree.")

T.node("master_tactician", "Master Tactician",
       "Your shots have a 10% chance to raise your critical strike chance "
       "by 2% per rank for 3 turns.",
       4, -2, 5,
       proc={"trigger": "on_damage_cast", "chance": 10, "icd": 0,
             "apply_effect": {"effect_id": "master_tactician",
                              "name": "Master Tactician",
                              "effect_type": "buff", "duration": 3,
                              "stat_mods": {"crit_chance_physical": 10},
                              "on_target": False}},
       connected_to=["lightning_reflexes"],
       source="WotLK row 4: 'Your successful ranged attacks have a 10% "
              "chance to increase your critical strike chance with all "
              "attacks by 2%-10% for 8 sec.' Built with the real 10% "
              "trigger chance - note the chance is NOT rank-scaled here, "
              "because the real talent scales its MAGNITUDE and a proc's "
              "payload cannot scale with points. So the payload carries the "
              "full 10% and the chance stays at the real flat 10%. 8 "
              "seconds is 3 turns. The outgoing node was a 1-point proc.")

T.node("wyvern_sting", "Wyvern Sting",
       "Teaches Wyvern Sting, a shot that puts the target to sleep.",
       4, 0, 1, node_type="active",
       effects={"unlock_ability": "hunter_wyvern_sting"},
       connected_to=["killer_instinct"],
       source="WotLK row 4, kept - the ONLY unlock for hunter_wyvern_sting, "
              "which is requires_talent. The real talent requires Killer "
              "Instinct, which connected_to reproduces. It is Noxious "
              "Stings' prerequisite, preserved below.")

T.node("noxious_stings", "Noxious Stings",
       "Increases the damage of your Serpent Sting and Wyvern Sting by 5% "
       "per rank.",
       4, 2, 3,
       effects={"ability_hunter_serpent_sting_damage": 0.05,
                "ability_hunter_wyvern_sting_damage": 0.05},
       connected_to=["wyvern_sting"],
       source="WotLK row 4: 'If Wyvern Sting is dispelled, the dispeller is "
              "also afflicted by Wyvern Sting, and increases all damage "
              "done by your Stings by 5%/10%/15%.' There is no dispel "
              "trigger, so only the damage half is built - verbatim, across "
              "both real Stings. The real talent requires Wyvern Sting, "
              "reproduced. Kept from the outgoing tree.")

T.node("thrill_of_the_hunt", "Thrill of the Hunt",
       "Your critical strikes have a 33% chance per rank to restore 150 "
       "mana.",
       4, 4, 3,
       proc={"trigger": "on_crit", "chance": 33, "icd": 0,
             "grant_resource": {"resource": "mana", "amount": 150}},
       connected_to=["resourcefulness"],
       source="WotLK row 4: 'Gives you a 33%-100% chance to regain 40% of "
              "the mana cost of any shot when it critically hits.' Built "
              "with the real chance curve on the real trigger. A refund "
              "proportional to the shot's cost is not available - "
              "grant_resource takes a FLAT amount with no pct_max - so 150 "
              "stands in. It is Hunting Party's prerequisite, preserved "
              "below. Kept as a proc from the outgoing tree.")

# ----------------------------------------------------------------- tier 5
T.node("point_of_no_escape", "Point of No Escape",
       "Increases your critical strike chance by 2% per rank.",
       5, -4, 2, effects={"crit_chance_physical": 2.0},
       connected_to=["expose_weakness"],
       source="WotLK row 5, NEW to our tree: 'Increases the critical strike "
              "chance of all of your attacks on targets affected by your "
              "Frost Trap, Freezing Trap or Freezing Arrow by 3%/6%.' "
              "DEPARTURE - NOTHING in this engine reads a debuff on the "
              "target, so 'affected by your trap' cannot be checked. "
              "Delivered unconditionally at a smaller value, since it is "
              "now always on rather than situational.")

T.node("black_arrow", "Black Arrow",
       "Teaches Black Arrow, a shadow-fletched shot that weakens its "
       "target.",
       5, -2, 1, node_type="active",
       effects={"unlock_ability": "hunter_black_arrow"},
       connected_to=["master_tactician"],
       source="WotLK row 5, kept - the ONLY unlock for hunter_black_arrow, "
              "which is requires_talent. It is Explosive Shot's "
              "prerequisite, preserved below. Moved from tier 4 to its real "
              "row.")

T.node("hunting_party", "Hunting Party",
       "Increases your Agility by 1% per rank and your haste by 1% per "
       "rank.",
       5, 0, 3,
       effects={"agility_pct": 1.0, "haste": 1.0},
       connected_to=["thrill_of_the_hunt"],
       source="WotLK row 5: 'Increases your total Agility by an additional "
              "1%/2%/3%, and your Arcane Shot, Explosive Shot and Steady "
              "Shot critical strikes have a chance to grant party and raid "
              "members 3% melee and ranged haste.' The Agility half is "
              "verbatim; the party-haste half cannot reach an ally, so the "
              "haste applies to the hunter. The real talent requires Thrill "
              "of the Hunt, reproduced. The outgoing node was a proc with "
              "an empty effects dict.")

T.node("sniper_training", "Sniper Training",
       "Increases the critical chance of your Aimed Shot by 5% per rank and "
       "its damage by 3% per rank.",
       5, 2, 3,
       effects={"ability_hunter_aimed_shot_crit": 5.0,
                "ability_hunter_aimed_shot_damage": 0.03},
       connected_to=["noxious_stings"],
       source="WotLK row 5: 'Increases the critical strike chance of your "
              "Kill Shot ability by 5%/10%/15%, and while standing still "
              "for 6 seconds increases the damage of your Steady Shot.' "
              "Kill Shot does not exist and there is no standing-still "
              "state, so both clauses land on Aimed Shot, the tree's "
              "remaining heavy shot. Kept from the outgoing tree.")

# ----------------------------------------------------------------- tier 6
T.node("explosive_shot", "Explosive Shot",
       "Teaches Explosive Shot, firing a charge that detonates inside the "
       "target.",
       6, 0, 1, node_type="active",
       effects={"unlock_ability": "hunter_explosive_shot"},
       connected_to=["black_arrow"],
       source="WotLK row 10, the capstone, kept - the ONLY unlock for "
              "hunter_explosive_shot, which is requires_talent. The real "
              "talent requires Black Arrow, which connected_to "
              "reproduces.")


def main():
    return T.write(was="23 nodes, 63 points - 7 proc, 10 ability-scoped, "
                       "3 flat stat, 3 unlock, 1 conditional")


if __name__ == "__main__":
    sys.exit(main())
