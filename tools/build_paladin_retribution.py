#!/usr/bin/env python3
"""Rebuild Paladin Retribution from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_paladin_retribution.py

SOURCE: data/reference/wotlk/paladin.json (from Spell.dbc).
Worksheet: data/reference/wotlk_worksheets/paladin.md.

ROLE: melee Holy damage. Crusader Strike, Judgement on cooldown, Divine
Storm, and crits feeding everything.

ASHER COLEMAN IS A LEVEL-5 RETRIBUTION PALADIN, which makes this the one
tree in the project with a hash-locked companion downstream of it. He is
safe for three independent reasons and all three were checked rather than
assumed: his kit is two hand-authored abilities loaded DIRECTLY from
data/abilities/asher_unique.json by world/recruit_manager.py, bypassing
the normal per-class ability pipeline entirely; he is fixed at level 5 and
never levels or re-specs, so he has no talent points to spend; and
qa_recruit_talents asserts he is byte-identical through both a fresh build
and a re-hire. That check is re-run after this tree.

CREATURE TYPE DOES NOT EXIST, which costs this tree one clause: Crusade's
"+3% damage against Humanoids, Demons, Undead and Elementals" has nothing
to read. Nothing in this engine reads a creature type.

AURAS AGAIN: Sanctified Retribution and Swift Retribution both improve
auras, and there is no aura system. Both pay out as the thing the aura
was for.

UNIT CONVENTIONS, probed: parry / crit_chance_physical / hit_rating /
haste / expertise are PERCENTAGE POINTS; all_ability_cost_pct is a
FRACTION where POSITIVE IS A REDUCTION (and it FLIPS to points inside a
status effect); all_damage / physical_damage / threat_generation_pct /
stun_duration_reduction_pct are FRACTIONS; *_from_*_pct is a FRACTION read
as a raw multiplier of the source stat.

KEPT MANDATORY: Seal of Command, Repentance and Divine Storm are the only
unlocks for their abilities, all three requires_talent.

NOTE ON CRUSADER STRIKE: it is a tier-5 TALENT in the real game and a
baseline ability here. It is left baseline - regrading it would strand it
behind a talent for the two other specs that already use it, and it is not
requires_talent so no unlock node is needed.

Judgements of the Just has moved OUT of this tree to Protection, where the
real game puts it.

THE DAMAGE KEY INSIDE A PROC'S stat_mods MUST BE damage_dealt_pct, IN
PERCENTAGE POINTS. all_damage, physical_damage, spell_damage and the
per-school <school>_spell_damage keys are read through
get_talent_effect (abilities.py:1606-1610), which sums TALENTS AND THE
CURRENT STANCE and nothing else - a status effect's stat_mods go to
get_status_stat_mod instead, and the damage path reads exactly one key
from there: damage_dealt_pct (abilities.py:1680-1683, divided by 100).
So a proc-applied buff carrying all_damage is SILENT DEAD DATA. Stances
look like a counter-example and are not: stance stat_mods are folded
into get_talent_effects (character.py:628), so they reach the talent
bus. Proc-applied buffs are not.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

T = Tree("paladin_retribution", "Paladin Retribution",
         "Righteous fury - Holy damage delivered at the end of a weapon.")

# ----------------------------------------------------------------- tier 0
T.node("deflection", "Deflection",
       "Increases your parry chance by 1% per rank.",
       0, -1, 5, effects={"parry": 1.0},
       source="WotLK row 0, NEW to our tree: 'Increases your Parry chance "
              "by 1%-5%.' Built verbatim. parry is PERCENTAGE POINTS, "
              "landing through a diminishing-returns curve.")

T.node("benediction", "Benediction",
       "Reduces the cost of your abilities by 2% per rank.",
       0, 1, 5, effects={"all_ability_cost_pct": 0.02},
       source="WotLK row 0: 'Reduces the mana cost of all instant cast "
              "spells by 2%-10%.' There is no cast-time distinction, so it "
              "covers everything. MIND THE KEY: all_ability_cost_pct is a "
              "FRACTION where POSITIVE MEANS A REDUCTION, and it FLIPS to "
              "percentage POINTS inside a status effect. The outgoing "
              "version was a flat cost cut on Crusader Strike alone.")

# ----------------------------------------------------------------- tier 1
T.node("improved_judgements", "Improved Judgements",
       "Reduces the cooldown of your Judgement by 1 turn per rank.",
       1, -5, 2,
       effects={"ability_paladin_judgement_cooldown": 1},
       connected_to=["deflection"],
       source="WotLK row 1: 'Decreases the cooldown of your Judgement "
              "spells by 1/2 sec.' Built as cooldown, which is what the "
              "real talent does. The outgoing version increased Judgement "
              "DAMAGE instead, which is The Art of War's job.")

T.node("vindication", "Vindication",
       "Your strikes have a 50% chance per rank to weaken the target's "
       "attack power for 3 turns.",
       1, -3, 2,
       proc={"trigger": "on_damage_cast", "chance": 50, "icd": 0,
             "apply_effect": {"effect_id": "vindication",
                              "name": "Vindication",
                              "effect_type": "debuff", "duration": 3,
                              "stat_mods": {"attack_power": -46}}},
       connected_to=["deflection"],
       source="WotLK row 1: 'Gives the Paladin's damaging attacks a chance "
              "to reduce the target's attack power by 23/46 for 10 sec.' "
              "Built with the real -46 and the real 10 seconds (3 turns). "
              "attack_power on a monster or inside a status effect is FLAT, "
              "and it is one of the eight stat_mods a MONSTER can actually "
              "read - which matters, because a debuff the enemy cannot read "
              "does nothing. Kept as a proc from the outgoing tree.")

T.node("heart_of_the_crusader", "Heart of the Crusader",
       "Increases your critical strike chance by 1% per rank.",
       1, -1, 3, effects={"crit_chance_physical": 1.0},
       connected_to=["benediction"],
       source="WotLK row 1: 'your Judgement spells will also increase the "
              "critical strike chance of all attacks made against that "
              "target by an additional 1%-3%.' DEPARTURE - there is no "
              "'crit chance against this target' debuff; crit is resolved "
              "from the attacker's own stats, and the only target-side crit "
              "key is crit_taken_reduction, which only reduces. Delivered "
              "as the paladin's own crit. Kept from the outgoing tree, "
              "corrected from 1.5 to the real 1% per rank.")

T.node("conviction", "Conviction",
       "Increases your critical strike chance by 1% per rank.",
       1, 1, 5, effects={"crit_chance_physical": 1.0},
       connected_to=["benediction"],
       source="WotLK row 1: 'Increases your chance to get a critical strike "
              "with all spells and attacks by 1%-5%.' Built verbatim and "
              "kept from the outgoing tree. It is Vengeance's prerequisite "
              "in the real tree, preserved below.")

T.node("improved_blessing_of_might", "Improved Blessing of Might",
       "Increases the attack power your Blessing of Might grants by 12% per "
       "rank.",
       1, 3, 2,
       effects={"ability_paladin_blessing_of_might_potency": 0.12},
       connected_to=["conviction"],
       source="WotLK row 1: 'Increases the attack power bonus of your "
              "Blessing of Might by 12%/25%.' Built verbatim over the real "
              "2 ranks; the outgoing version had 5 ranks of 8%, reaching "
              "40%. ability_<id>_potency scales the ability's own "
              "stat_mods.")

T.node("seal_of_command", "Seal of Command",
       "Teaches Seal of Command, adding Holy damage to every strike.",
       1, 5, 1, node_type="active",
       effects={"unlock_ability": "paladin_seal_of_command"},
       connected_to=["conviction"],
       source="WotLK row 1, kept - the ONLY unlock for "
              "paladin_seal_of_command, which is requires_talent.")

T.node("pursuit_of_justice", "Pursuit of Justice",
       "Increases your chance to hit by 1% per rank.",
       1, 7, 2, effects={"hit_rating": 1.0},
       connected_to=["seal_of_command"],
       source="WotLK row 1: 'Reduces the duration of all Disarm effects by "
              "25%/50% and increases movement and mounted movement speed by "
              "8%/15%.' DEPARTURE - no movement speed and no Disarm "
              "duration modifier. Delivered as accuracy, the nearest "
              "offensive equivalent of closing on a target. Kept from the "
              "outgoing tree, corrected from 1.5 to 1 per rank.")

# ----------------------------------------------------------------- tier 2
T.node("eye_for_an_eye", "Eye for an Eye",
       "Being struck has a 50% chance per rank to lash back at your "
       "attacker.",
       2, -5, 2,
       proc={"trigger": "on_damage_taken", "chance": 50, "icd": 1,
             "damage_flat": 30, "school": "holy"},
       connected_to=["improved_judgements"],
       source="WotLK row 2: 'All criticals against you cause 10%/20% of the "
              "damage taken to the attacker as well.' DEPARTURE on the "
              "trigger - there is no on-crit-TAKEN event, only "
              "on_damage_taken, so icd 1 holds it to once a turn. "
              "Percentage-of-damage-taken reflection is also unavailable: "
              "of the three payloads that read the triggering amount "
              "(bonus_pct, leech_pct, smart heals), none reflects, so "
              "damage_flat 30 is a fixed return typed as Holy. Kept as a "
              "proc from the outgoing tree.")

T.node("two_handed_weapon_specialization", "Two-Handed Weapon Specialization",
       "Increases your physical damage by 2% per rank.",
       2, -3, 3, effects={"physical_damage": 0.02},
       connected_to=["vindication"],
       source="WotLK row 2: 'Increases the damage you deal with two-handed "
              "melee weapons by 2%/4%/6%.' Built minus the weapon gate. The "
              "outgoing version was attack_power_pct, which is a different "
              "stat. physical_damage is a FRACTION.")

T.node("sanctity_of_battle", "Sanctity of Battle",
       "Increases your critical strike chance by 1% per rank and the damage "
       "of your Exorcism and Crusader Strike by 5% per rank.",
       2, -1, 3,
       effects={"crit_chance_physical": 1.0,
                "ability_paladin_exorcism_damage": 0.05,
                "ability_paladin_crusader_strike_damage": 0.05},
       connected_to=["heart_of_the_crusader"],
       source="WotLK row 2, built verbatim with both halves: 'Increases "
              "your chance to critically hit with all spells and attacks by "
              "1%-3% and increases the damage caused by Exorcism and "
              "Crusader Strike by 5%/10%/15%.' The outgoing version had the "
              "damage half on Consecration rather than Exorcism and omitted "
              "the crit.")

T.node("sanctified_retribution", "Sanctified Retribution",
       "Increases all damage you deal by 3%.",
       2, 1, 1, effects={"all_damage": 0.03},
       connected_to=["conviction"],
       source="WotLK row 2: 'Increases the damage caused by Retribution "
              "Aura by 50% and all damage caused by friendly targets "
              "affected by any of your Auras is increased by 3%.' DEPARTURE "
              "- there is no aura system and a talent effect can never "
              "reach an ally, so the real 3% applies to the paladin alone. "
              "The outgoing version was a proc.")

T.node("crusade", "Crusade",
       "Increases all damage you deal by 1% per rank.",
       2, 3, 3, effects={"all_damage": 0.01},
       connected_to=["improved_blessing_of_might"],
       source="WotLK row 2: 'Increases all damage caused by 1%-3% and all "
              "damage caused against Humanoids, Demons, Undead and "
              "Elementals by an additional 1%-3%.' The unconditional half "
              "is built verbatim. The creature-type half cannot be built - "
              "NOTHING in this engine reads a creature type. The outgoing "
              "version was physical_damage, which excludes the paladin's "
              "Holy damage and so missed most of the point.")

# ----------------------------------------------------------------- tier 3
T.node("vengeance", "Vengeance",
       "Your critical strikes have a 33% chance per rank to increase your "
       "damage by 3% for 4 turns.",
       3, -1, 3,
       proc={"trigger": "on_crit", "chance": 33, "icd": 0,
             "apply_effect": {"effect_id": "vengeance", "name": "Vengeance",
                              "effect_type": "buff", "duration": 4,
                              "stat_mods": {"damage_dealt_pct": 3.0},
                              "on_target": False}},
       connected_to=["conviction"],
       source="WotLK row 3: 'Gives you a 1%-3% bonus to Physical and Holy "
              "damage you deal for 30 sec after dealing a critical strike "
              "from a weapon swing, spell, or ability. This effect stacks "
              "up to 3 times.' Built with the real 3% at full effect and 30 "
              "seconds as 4 turns. STACKING IS DROPPED: max_stacks exists "
              "on StatusEffect but NOTHING in this engine reads a stack "
              "count, so a 3-stack version would be indistinguishable from "
              "a 1-stack one. Ranked by chance, since a proc's payload does "
              "not scale with points. The real talent requires Conviction, "
              "reproduced. Kept as a proc from the outgoing tree.")

T.node("divine_purpose", "Divine Purpose",
       "Reduces the duration of Stun effects against you by 15% per rank.",
       3, 1, 2, effects={"stun_duration_reduction_pct": 0.15},
       connected_to=["sanctity_of_battle"],
       source="WotLK row 3: 'Reduces your chance to be hit by spells and "
              "ranged attacks by 2%/4% and gives your Hand of Freedom spell "
              "a 100% chance to remove any Stun effects on the target.' "
              "DEPARTURE - no caster-side miss chance for INCOMING attacks "
              "(hit_chance_spell is a dead talent key set once in "
              "Character.__init__) and no Hand of Freedom. The stun clause "
              "survives, applied to the paladin. Kept from the outgoing "
              "tree, corrected from 3 ranks to the real 2.")

# ----------------------------------------------------------------- tier 4
T.node("the_art_of_war", "The Art of War",
       "Increases the damage of your Judgement, Crusader Strike and Divine "
       "Storm by 5% per rank.",
       4, -5, 2,
       effects={"ability_paladin_judgement_damage": 0.05,
                "ability_paladin_crusader_strike_damage": 0.05,
                "ability_paladin_divine_storm_damage": 0.05},
       connected_to=["vengeance"],
       source="WotLK row 4, NEW to our tree: 'Increases the damage of your "
              "Judgement, Crusader Strike and Divine Storm abilities by "
              "5%/10% and when your melee attacks critically hit your next "
              "Flash of Light or Exorcism is instant.' The damage half is "
              "built verbatim across all three real abilities. The "
              "instant-cast half has nothing to act on - there are no cast "
              "times.")

T.node("repentance", "Repentance",
       "Teaches Repentance, holding an enemy in meditation.",
       4, -3, 1, node_type="active",
       effects={"unlock_ability": "paladin_repentance"},
       connected_to=["vengeance"],
       source="WotLK row 4, kept - the ONLY unlock for paladin_repentance, "
              "which is requires_talent. It is Fanaticism's prerequisite in "
              "the real tree, preserved below.")

T.node("fanaticism", "Fanaticism",
       "Increases the critical strike chance of your Judgement by 6% per "
       "rank and reduces your threat by 10% per rank.",
       4, -1, 3,
       effects={"ability_paladin_judgement_crit": 6.0,
                "threat_generation_pct": -0.10},
       connected_to=["repentance"],
       source="WotLK row 4, built verbatim with both halves: 'Increases the "
              "critical strike chance of all Judgements capable of a "
              "critical hit by 6%-18% and reduces threat caused by all "
              "actions by 10%-30%.' ability_<id>_crit is PERCENTAGE POINTS "
              "and threat_generation_pct is a FRACTION. The outgoing "
              "version was crit on Crusader Strike with no threat clause. "
              "The real talent requires Repentance, reproduced.")

T.node("judgements_of_the_wise", "Judgements of the Wise",
       "Your Judgement restores 200 mana.",
       4, 1, 3,
       proc={"trigger": "on_cast", "chance": 33, "icd": 0,
             "ability_filter": ["paladin_judgement"],
             "grant_resource": {"resource": "mana", "amount": 200}},
       connected_to=["divine_purpose"],
       source="WotLK row 4, NEW to our tree: 'Your damaging Judgement "
              "spells have a 33%-100% chance to grant the Replenishment "
              "effect to up to 10 party or raid members, granting mana "
              "regeneration equal to 1% of their maximum mana per 10 sec.' "
              "DEPARTURE - a talent effect can never reach an ally, so the "
              "mana goes to the paladin. The real chance curve is kept "
              "exactly. grant_resource takes a FLAT amount with no pct_max, "
              "so 200 is a fixed return rather than a percentage of the "
              "pool.")

T.node("sanctified_wrath", "Sanctified Wrath",
       "Increases the critical strike chance of your Hammer of Wrath by 25% "
       "per rank.",
       4, 3, 2,
       effects={"ability_paladin_hammer_of_wrath_crit": 25.0},
       connected_to=["divine_purpose"],
       source="WotLK row 4, NEW to our tree: 'Increases the critical strike "
              "chance of Hammer of Wrath by 25%/50%, reduces the cooldown "
              "of Avenging Wrath by 30/60 secs and while affected by "
              "Avenging Wrath 25%/50% of all damage is converted to "
              "healing.' Only the Hammer of Wrath clause is buildable - "
              "Avenging Wrath does not exist and there is no "
              "damage-to-healing conversion. Built at the real 25% per "
              "rank.")

# ----------------------------------------------------------------- tier 5
T.node("swift_retribution", "Swift Retribution",
       "Increases your haste by 1% per rank.",
       5, -3, 3, effects={"haste": 1.0},
       connected_to=["the_art_of_war"],
       source="WotLK row 5: 'Your auras also increase casting, ranged and "
              "melee attack speeds by 1%-3%.' DEPARTURE - no aura system "
              "and a talent effect cannot reach an ally, so the real 3% "
              "applies to the paladin. haste is PERCENTAGE POINTS. The "
              "outgoing version was a proc.")

T.node("righteous_vengeance", "Righteous Vengeance",
       "Your critical strikes have a 33% chance per rank to leave the target "
       "burning for 3 turns.",
       5, -1, 3,
       proc={"trigger": "on_crit", "chance": 33, "icd": 0,
             "apply_effect": {"effect_id": "righteous_vengeance",
                              "name": "Righteous Vengeance",
                              "effect_type": "dot", "duration": 3,
                              "potency": 45, "damage_school": "holy"}},
       connected_to=["fanaticism"],
       source="WotLK row 5: 'When your Judgement, Crusader Strike and "
              "Divine Storm spells deal a critical strike, your target will "
              "take 10%-30% additional damage over 8 sec.' Built as a real "
              "Holy dot. Percentage-of-damage scaling is not available to a "
              "proc payload - potency is a FLAT PER-TURN number, where an "
              "ABILITY rank's effect_value is the TOTAL and gets divided - "
              "so 45 a turn over 3 turns (8 seconds) is a fixed bleed. The "
              "ability_filter is omitted deliberately: on_crit already "
              "requires a crit, and restricting to the three abilities "
              "would exclude the weapon-swing crits the tree's other "
              "talents are built to produce. Kept as a proc from the "
              "outgoing tree.")

T.node("sheath_of_light", "Sheath of Light",
       "Increases your spell power by 10% of your attack power per rank.",
       5, 1, 3,
       effects={"spell_power_from_ap_pct": 0.10},
       connected_to=["fanaticism"],
       source="WotLK row 5: 'Increases your spell power by an amount equal "
              "to 10%-30% of your attack power and your critical healing "
              "spells heal the target for 60% of the healed amount over 12 "
              "seconds.' The conversion half is a REAL pairing - "
              "spell_power is a valid STAT_CONVERSION_TARGET and ap a valid "
              "source - built at 0.10 per rank to reach the real 30%. THE "
              "UNIT IS A RAW MULTIPLIER, not a percentage "
              "(character.py:1551 does `gained = source * pct`). The "
              "critical-heal-hot clause has no key. The outgoing version "
              "was attack_power_pct plus Flash of Light healing, neither of "
              "which is this talent.")

# ----------------------------------------------------------------- tier 6
T.node("divine_storm", "Divine Storm",
       "Teaches Divine Storm, a whirling strike that mends your allies as "
       "it wounds your enemies.",
       6, 1, 1, node_type="active",
       effects={"unlock_ability": "paladin_divine_storm"},
       connected_to=["righteous_vengeance"],
       source="WotLK row 10, the capstone, kept - the ONLY unlock for "
              "paladin_divine_storm, which is requires_talent.")


def main():
    return T.write(was="23 nodes, 69 points - 7 proc, 7 ability-scoped, "
                       "5 flat stat, 3 unlock, 1 mixed")


if __name__ == "__main__":
    sys.exit(main())
