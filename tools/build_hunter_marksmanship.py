#!/usr/bin/env python3
"""Rebuild Hunter Marksmanship from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_hunter_marksmanship.py

SOURCE: data/reference/wotlk/hunter.json (from Spell.dbc).
Worksheet: data/reference/wotlk_worksheets/hunter.md.

ROLE: the shot itself. Aimed Shot and Steady Shot, crit and crit damage,
and Chimera Shot at the top.

CAREFUL AIM IS A REAL CONVERSION AND THE TREE'S BEST TALENT. "+100% ranged
attack power from Intellect" maps onto ranged_ap_from_intellect_pct -
ranged_ap is a valid STAT_CONVERSION_TARGET and intellect a valid source -
and it was MEASURED LIVE at +29 ranged attack power off 29 Intellect. The
unit is a RAW MULTIPLIER, not a percentage (character.py:1551 does
`gained = source * pct`).

ABILITIES THE REAL TREE WANTS AND WE LACK: Rapid Fire, Volley, Kill Shot,
Scatter Shot, Silencing Shot. Rapid Killing, Rapid Recuperation and
Silencing Shot are DROPPED; Sniper Training's Kill Shot clause is
re-aimed at Aimed Shot.

WEAPON TYPE DOES NOT EXIST, so Lethal Shots and Ranged Weapon
Specialization drop their "Requires Bows, Crossbows, Guns, Thrown" gate.
Note requires_ranged_weapon IS a real ABILITY field, but there is no
talent-side equivalent and no weapon-class distinction.

UNIT CONVENTIONS: crit_chance_physical / hit_rating / agility_pct /
intellect_pct are PERCENTAGE POINTS; crit_damage_physical / physical_damage
/ all_damage are FRACTIONS; *_from_*_pct is a FRACTION read as a raw
multiplier; ability_<id>_crit is PERCENTAGE POINTS and _damage a FRACTION.

KEPT MANDATORY: Chimera Shot is the only unlock for hunter_chimera_shot,
which is requires_talent.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

#: The shots, for Efficiency and Marked for Death.
SHOTS = ["hunter_steady_shot", "hunter_arcane_shot", "hunter_aimed_shot",
         "hunter_multi_shot"]

T = Tree("hunter_marksmanship", "Hunter Marksmanship",
         "Precision at range - the shot placed exactly where it matters.")

# ----------------------------------------------------------------- tier 0
T.node("improved_concussive_shot", "Improved Concussive Shot",
       "Increases the duration of your Concussive Shot by 1 turn per rank.",
       0, -2, 2,
       effects={"ability_hunter_concussive_shot_duration": 1},
       source="WotLK row 0: 'Increases the duration of your Concussive "
              "Shot's daze effect by 1/2 sec.' Built as duration. Daze "
              "itself has no engine equivalent, but the ability already "
              "exists with its own effect, so extending it is faithful. "
              "Kept from the outgoing tree, corrected from 3 ranks to the "
              "real 2.")

T.node("focused_aim", "Focused Aim",
       "Increases your chance to hit by 1% per rank.",
       0, 0, 3, effects={"hit_rating": 1.0},
       source="WotLK row 0: 'Reduces the pushback suffered from damaging "
              "attacks while casting Steady Shot by 35%/70%, and increases "
              "your chance to hit by 1%/2%/3%.' The hit half is verbatim; "
              "no cast times means no pushback. Kept from the outgoing "
              "tree. hit_rating is PERCENTAGE POINTS and is NOT a valid "
              "STAT_CONVERSION_TARGET.")

T.node("lethal_shots", "Lethal Shots",
       "Increases your critical strike chance by 1% per rank.",
       0, 2, 5, effects={"crit_chance_physical": 1.0},
       source="WotLK row 0: 'Requires Bows, Crossbows, Guns, Thrown. "
              "Increases your critical strike chance with ranged weapons by "
              "1%-5%.' Built minus the weapon gate - there is no "
              "weapon-type key. The outgoing version granted per-ability "
              "crit on two shots, which is Improved Barrage's shape.")

# ----------------------------------------------------------------- tier 1
T.node("careful_aim", "Careful Aim",
       "Increases your ranged attack power by 33% of your Intellect per "
       "rank.",
       1, -4, 3,
       effects={"ranged_ap_from_intellect_pct": 0.33},
       connected_to=["improved_concussive_shot"],
       source="WotLK row 1, built verbatim: 'Increases your ranged attack "
              "power by an amount equal to 33%-100% of your total "
              "Intellect.' A REAL stat conversion and this tree's best "
              "talent - ranged_ap is a valid STAT_CONVERSION_TARGET and "
              "intellect a valid source. MEASURED LIVE at +29 ranged attack "
              "power off 29 Intellect, so the key is a RAW MULTIPLIER and "
              "not a percentage; authoring 100 would have granted a hundred "
              "times the hunter's Intellect. The outgoing node was a proc "
              "with an empty effects dict.")

T.node("go_for_the_throat", "Go for the Throat",
       "Your critical strikes increase your pet's damage for 3 turns.",
       1, -2, 2,
       proc={"trigger": "on_crit", "chance": 50, "icd": 0,
             "apply_effect": {"effect_id": "go_for_the_throat",
                              "name": "Go for the Throat",
                              "effect_type": "buff", "duration": 3,
                              "stat_mods": {"damage_dealt_pct": 8.0},
                              "on_target": False}},
       connected_to=["improved_concussive_shot"],
       source="WotLK row 1: 'Your ranged critical hits cause your pet to "
              "generate 25/50 Focus.' DEPARTURE - pets have NO RESOURCE in "
              "this engine, so there is no Focus to generate, and a talent "
              "effect cannot reach the pet in any case. The buff lands on "
              "the hunter. NOTE the stat_mod is damage_dealt_pct in "
              "PERCENTAGE POINTS: all_damage would be SILENT DEAD DATA "
              "inside a status effect, read through the talent channel while "
              "status stat_mods go to get_status_stat_mod. Kept as a proc "
              "from the outgoing tree.")

T.node("improved_hunters_mark", "Improved Hunter's Mark",
       "Increases the effect of your Hunter's Mark by 10% per rank.",
       1, 0, 3,
       effects={"ability_hunter_hunters_mark_potency": 0.10},
       connected_to=["focused_aim"],
       source="WotLK row 1: 'Increases the bonus attack power granted by "
              "your Hunter's Mark ability by 10%/20%/30%, and reduces the "
              "mana cost.' Built as potency, which scales the ability's own "
              "stat_mods. Kept from the outgoing tree, which used "
              "_duration.")

T.node("improved_arcane_shot", "Improved Arcane Shot",
       "Increases the damage of your Arcane Shot by 5% per rank.",
       1, 2, 3,
       effects={"ability_hunter_arcane_shot_damage": 0.05},
       connected_to=["focused_aim"],
       source="WotLK row 1, built verbatim: 'Increases the damage done by "
              "your Arcane Shot by 5%/10%/15%.' Kept from the outgoing "
              "tree, corrected from 7% to the real 5% per rank.")

T.node("mortal_shots", "Mortal Shots",
       "Increases the critical damage of your abilities by 6% per rank.",
       1, 4, 5, effects={"crit_damage_physical": 0.06},
       connected_to=["lethal_shots"],
       source="WotLK row 1, built verbatim: 'Increases the critical strike "
              "damage bonus of your ranged abilities by 6%-30%.' "
              "crit_damage_physical is a FRACTION, read at abilities.py:1460 "
              "inside a ternary - live despite the probe finding no literal "
              "read site, and DEAD inside a status effect, so the "
              "talent-effect form used here is the only one that works. The "
              "outgoing version was per-ability DAMAGE on Aimed Shot, which "
              "is a different stat. It is Aimed Shot's prerequisite in the "
              "real tree.")

# ----------------------------------------------------------------- tier 2
T.node("concussive_barrage", "Concussive Barrage",
       "Your Multi-Shot and Chimera Shot have a 50% chance per rank to slow "
       "the target for 2 turns.",
       2, -4, 2,
       proc={"trigger": "on_damage_cast", "chance": 50, "icd": 0,
             "ability_filter": ["hunter_multi_shot", "hunter_chimera_shot"],
             "apply_effect": {"effect_id": "concussive_barrage",
                              "name": "Concussive Barrage",
                              "effect_type": "debuff", "duration": 2,
                              "stat_mods": {"haste": -20}}},
       connected_to=["careful_aim"],
       source="WotLK row 2: 'Your successful Chimera Shot and Multi-Shot "
              "attacks have a 50%/100% chance to Daze the target for 4 "
              "sec.' Built with the real ability pair and the real chance "
              "curve. Daze has no engine equivalent, so it is a haste "
              "debuff on the target - which is what a dazed enemy amounts "
              "to here. Kept as a proc from the outgoing tree.")

T.node("improved_stings", "Improved Stings",
       "Increases the damage of your Serpent Sting and Wyvern Sting by 10% "
       "per rank, and reduces your Wyvern Sting cooldown by 1 turn per "
       "rank.",
       2, -2, 3,
       effects={"ability_hunter_serpent_sting_damage": 0.10,
                "ability_hunter_wyvern_sting_cooldown": 1},
       connected_to=["careful_aim"],
       source="WotLK row 2, built verbatim across both real Stings: "
              "'Increases the damage done by your Serpent Sting and Wyvern "
              "Sting by 10%/20%/30%.' Kept from the outgoing tree, "
              "corrected from 5 ranks to the real 3.")

T.node("readiness", "Readiness",
       "Reduces the cooldown of your Aimed Shot and Multi-Shot by 1 turn "
       "per rank.",
       2, 0, 1,
       effects={"ability_hunter_aimed_shot_cooldown": 1,
                "ability_hunter_multi_shot_cooldown": 1},
       connected_to=["improved_hunters_mark"],
       source="WotLK row 2: 'When activated, this ability immediately "
              "finishes the cooldown on your other Hunter abilities.' "
              "DEPARTURE - there is no hunter_readiness ability to unlock. "
              "Delivered as a standing cooldown reduction on the tree's two "
              "cooldown shots. Kept from the outgoing tree. It is Trueshot "
              "Aura's prerequisite, preserved below.")

T.node("efficiency", "Efficiency",
       "Reduces the cost of your shots and stings by 3% per rank.",
       2, 2, 5,
       effects={**{f"ability_{a}_cost_pct": 0.03 for a in SHOTS},
                "ability_hunter_serpent_sting_cost_pct": 0.03},
       connected_to=["improved_arcane_shot"],
       source="WotLK row 2, built verbatim across all four shots and "
              "Serpent Sting: 'Reduces the Mana cost of your Shots and "
              "Stings by 3%-15%.' Kept from the outgoing tree, which used "
              "the FLAT _cost key on two of them.")

T.node("barrage", "Barrage",
       "Increases the damage of your Multi-Shot and Aimed Shot by 4% per "
       "rank.",
       2, 4, 3,
       effects={"ability_hunter_multi_shot_damage": 0.04,
                "ability_hunter_aimed_shot_damage": 0.04},
       connected_to=["mortal_shots"],
       source="WotLK row 2: 'Increases the damage done by your Multi-Shot, "
              "Aimed Shot, and Volley spells by 4%/8%/12%.' Volley does not "
              "exist. Kept from the outgoing tree, which covered Multi-Shot "
              "alone. It is Improved Barrage's prerequisite, preserved "
              "below.")

# ----------------------------------------------------------------- tier 3
T.node("combat_experience", "Combat Experience",
       "Increases your Agility and Intellect by 2% per rank.",
       3, -2, 2,
       effects={"agility_pct": 2.0, "intellect_pct": 2.0},
       connected_to=["improved_stings"],
       source="WotLK row 3, built verbatim: 'Increases your total Agility "
              "and Intellect by 2%/4%.' Both are PERCENTAGE POINTS, read "
              "off `bonuses` and divided by 100. The Intellect half feeds "
              "Careful Aim two tiers up, which is the real pairing. The "
              "outgoing version granted FLAT agility and intellect.")

T.node("ranged_weapon_specialization", "Ranged Weapon Specialization",
       "Increases your physical damage by 2% per rank.",
       3, 0, 3, effects={"physical_damage": 0.02},
       connected_to=["readiness"],
       source="WotLK row 3: 'Requires Ranged Weapon. Increases the damage "
              "you deal with ranged weapons by 2%/4%/5%.' Built minus the "
              "weapon gate. Note requires_ranged_weapon IS a real ABILITY "
              "field in this engine, but there is no talent-side "
              "equivalent. physical_damage is a FRACTION. The outgoing "
              "version was per-ability damage at 5 ranks.")

# ----------------------------------------------------------------- tier 4
T.node("piercing_shots", "Piercing Shots",
       "Your critical strikes have a 33% chance per rank to leave the "
       "target bleeding for 3 turns.",
       4, -4, 3,
       proc={"trigger": "on_crit", "chance": 33, "icd": 0,
             "apply_effect": {"effect_id": "piercing_shots",
                              "name": "Piercing Shots",
                              "effect_type": "dot", "duration": 3,
                              "potency": 45, "damage_school": "physical"}},
       connected_to=["combat_experience"],
       source="WotLK row 4: 'Your critical Aimed, Steady and Chimera Shots "
              "cause the target to bleed for 10%/20%/30% of the damage "
              "dealt over 8 sec.' Built as a real bleed on the real "
              "trigger. Percentage-of-damage is not available to a dot "
              "payload - potency is a FLAT PER-TURN number, where an "
              "ABILITY rank's effect_value is the TOTAL and gets divided - "
              "so 45 a turn over 3 turns (8 seconds) stands in. The "
              "ability_filter is omitted because on_crit already requires a "
              "crit and restricting it would exclude the auto-shot crits "
              "this tree is built to produce. Kept as a proc from the "
              "outgoing tree.")

T.node("trueshot_aura", "Trueshot Aura",
       "Increases your attack power by 10%.",
       4, -2, 1, effects={"attack_power_pct": 10.0},
       connected_to=["readiness"],
       source="WotLK row 4: 'Increases the attack power of party and raid "
              "members within 100 yards by 10%.' DEPARTURE - A TALENT "
              "EFFECT CAN NEVER REACH AN ALLY. The real 10% applies to the "
              "hunter alone. The real talent requires Readiness, which "
              "connected_to reproduces. attack_power_pct is PERCENTAGE "
              "POINTS. The outgoing version granted FLAT attack_power.")

T.node("master_marksman", "Master Marksman",
       "Increases your critical strike chance by 1% per rank and reduces "
       "the cost of your shots by 2% per rank.",
       4, 0, 5,
       effects={"crit_chance_physical": 1.0,
                **{f"ability_{a}_cost_pct": 0.02 for a in SHOTS}},
       connected_to=["ranged_weapon_specialization"],
       source="WotLK row 4, built with both halves: 'Increases your "
              "critical strike chance by 1%-5%, and reduces the Mana cost "
              "of your Steady Shot, Aimed Shot and Arcane Shot by "
              "2%-10%.' Stacks with Efficiency and Lethal Shots, as the "
              "real tree intends. The outgoing version was per-ability "
              "damage.")

T.node("improved_barrage", "Improved Barrage",
       "Increases the critical chance of your Multi-Shot and Aimed Shot by "
       "4% per rank.",
       4, 2, 3,
       effects={"ability_hunter_multi_shot_crit": 4.0,
                "ability_hunter_aimed_shot_crit": 4.0},
       connected_to=["barrage"],
       source="WotLK row 4, NEW to our tree, built verbatim: 'Increases the "
              "critical strike chance of your Multi-Shot and Aimed Shot "
              "abilities by 4%/8%/12%.' The real talent requires Barrage, "
              "which connected_to reproduces. ability_<id>_crit is "
              "PERCENTAGE POINTS.")

# ----------------------------------------------------------------- tier 5
T.node("wild_quiver", "Wild Quiver",
       "Your shots have a 4% chance per rank to loose an additional arrow.",
       5, -2, 3,
       proc={"trigger": "on_damage_cast", "chance": 4, "icd": 0,
             "ability_filter": SHOTS,
             "damage_flat": 85, "school": "physical"},
       connected_to=["piercing_shots"],
       source="WotLK row 5: 'You have a 4%/8%/12% chance to shoot an "
              "additional shot when doing damage, dealing 80% weapon "
              "damage.' Built with the real chance curve. Weapon-damage "
              "scaling is not available to a proc payload, so damage_flat "
              "85 stands in. proc['school'] only TYPES a damage_flat "
              "payload; it is not a trigger-side filter. Kept as a proc "
              "from the outgoing tree.")

T.node("marked_for_death", "Marked for Death",
       "Increases the damage of your shots by 1% per rank and your pet's "
       "damage by 1% per rank.",
       5, 0, 5,
       effects={**{f"ability_{a}_damage": 0.01 for a in SHOTS},
                "pet_damage": 0.01},
       connected_to=["master_marksman"],
       source="WotLK row 5, built verbatim with both halves: 'Increases "
              "your damage done by your shots and the damage done by your "
              "pet's special abilities by 1%-5%.' pet_damage is a FRACTION "
              "read at pet.py:139 - one of only three pet keys that work. "
              "NOTE this talent also appears as Beast Mastery's capstone, "
              "where it takes the slot the unbuildable Beast Mastery talent "
              "would have had; the duplication is deliberate and recorded "
              "in both builders.")

T.node("improved_steady_shot", "Improved Steady Shot",
       "Your Steady Shot has a 5% chance per rank to make your next shots "
       "hit 15% harder.",
       5, 2, 3,
       proc={"trigger": "on_damage_cast", "chance": 5, "icd": 0,
             "ability_filter": ["hunter_steady_shot"],
             "apply_effect": {"effect_id": "improved_steady_shot",
                              "name": "Improved Steady Shot",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"damage_dealt_pct": 15.0},
                              "on_target": False}},
       connected_to=["improved_barrage"],
       source="WotLK row 5, NEW to our tree: 'Your Steady Shot hits have a "
              "5%/10%/15% chance to increase the damage done by your next "
              "Aimed Shot, Arcane Shot or Chimera Shot by 15%.' Built with "
              "the real chance curve, the real ability_filter on Steady "
              "Shot, and the real 15%. Scoping the BUFF to three specific "
              "abilities is not possible - a status effect's stat_mods "
              "apply to everything - so it lifts all damage for 2 turns "
              "instead.")

# ----------------------------------------------------------------- tier 6
T.node("chimera_shot", "Chimera Shot",
       "Teaches Chimera Shot, a shot that refreshes your Sting as it "
       "strikes.",
       6, 0, 1, node_type="active",
       effects={"unlock_ability": "hunter_chimera_shot"},
       connected_to=["marked_for_death"],
       source="WotLK row 10, the capstone, kept - the ONLY unlock for "
              "hunter_chimera_shot, which is requires_talent.")


def main():
    return T.write(was="23 nodes, 69 points - 8 proc, 11 ability-scoped, "
                       "3 flat stat, 1 unlock")


if __name__ == "__main__":
    sys.exit(main())
