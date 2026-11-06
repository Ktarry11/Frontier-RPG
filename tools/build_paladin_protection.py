#!/usr/bin/env python3
"""Rebuild Paladin Protection from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_paladin_protection.py

SOURCE: data/reference/wotlk/paladin.json (from Spell.dbc).
Worksheet: data/reference/wotlk_worksheets/paladin.md.

ROLE: shield tank. Block, armour, Holy damage on every block, and the
tree that turns Strength into spell power.

THE RECURRING WALL IN THIS TREE IS ALLY-TARGETING. Four real talents
redirect or reduce damage for OTHER people - Divine Sacrifice, Divine
Guardian, Blessing of Sanctuary, Shield of the Templar's silence - and in
this engine A TALENT EFFECT CAN NEVER REACH AN ALLY. Only a
party-targeted ABILITY can (abilities.py:2064). There is also no damage
redirection or threat transfer of any kind. Each of those four is rebuilt
as the self-facing part of the same protection, and each node says so.

STAT CONVERSION IS THE TREE'S BEST TALENT AND IT IS REAL. Touched by the
Light is "+60% spell power from Strength", and spell_power_from_strength_pct
is a valid pairing (spell_power is a target, strength a source). The unit
is a RAW MULTIPLIER, not a percentage - character.py:1551 does
`gained = source * pct` - so it is authored at 0.20 per rank.

ABILITIES THE REAL TALENTS WANT AND WE LACK: Hand of Protection, Hand of
Freedom, Divine Protection, Divine Plea, Divine Sacrifice, Righteous Fury,
Devotion Aura, Holy Shield (the ability), Shield Block, Hammer of the
Righteous, Seal of Justice. Recorded per node.

UNIT CONVENTIONS, probed: block / dodge / expertise / strength_pct /
stamina_pct / crit_chance_physical are PERCENTAGE POINTS; armor_pct /
healing_done / healing_taken_pct / physical_damage /
spell_damage_taken_pct / low_health_damage_reduction_pct are FRACTIONS;
damage_taken_pct is read RAW on both sides; max_health_pct is a FRACTION
(character.py:1411, NOT divided by 100).

low_health_threshold_pct is authored NOWHERE - it SUMS, it is UNSCALED,
and the actor-side default of 0.5 is what Ardent Defender wants. The
outgoing tree authored it on Ardent Defender AND on Divine Guardian, which
summed to a threshold above 1.0.

KEPT MANDATORY: Avenger's Shield is the only unlock for
paladin_avengers_shield, which is requires_talent.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

T = Tree("paladin_protection", "Paladin Protection",
         "Shield of the Light - absorb, block and hold the line.")

# ----------------------------------------------------------------- tier 0
T.node("divinity", "Divinity",
       "Increases healing you do and healing you receive by 1% per rank.",
       0, -1, 5,
       effects={"healing_done": 0.01, "healing_taken_pct": 0.01},
       source="WotLK row 0, built verbatim with both halves: 'Increases all "
              "healing done by you and all healing effects on you by "
              "1%-5%.' The outgoing version was max_health_pct, which is "
              "Divine Guardian's shape rather than this talent's.")

T.node("divine_strength", "Divine Strength",
       "Increases your Strength by 3% per rank.",
       0, 1, 5, effects={"strength_pct": 3.0},
       source="WotLK row 0, NEW to our tree, built verbatim: 'Increases "
              "your total Strength by 3%-15%.' strength_pct is PERCENTAGE "
              "POINTS, read off `bonuses` at character.py:1262 and divided "
              "by 100. This node feeds Touched by the Light at tier 5, "
              "which is the pairing that makes a Protection paladin's spell "
              "power work at all.")

# ----------------------------------------------------------------- tier 1
T.node("stoicism", "Stoicism",
       "Reduces the duration of Stun effects against you by 10% per rank.",
       1, -5, 3, effects={"stun_duration_reduction_pct": 0.10},
       connected_to=["divinity"],
       source="WotLK row 1: 'Reduces the duration of all Stun effects by an "
              "additional 10%-30% and reduces the chance your helpful "
              "spells and damage over time effects will be dispelled.' The "
              "stun half is built verbatim; dispel resistance does not "
              "exist. stun_duration_reduction_pct is a FRACTION. Kept from "
              "the outgoing tree, which also carried "
              "magic_damage_taken_pct - removed here because Guarded by the "
              "Light covers spell mitigation at tier 5.")

T.node("divine_sacrifice", "Divine Sacrifice",
       "Reduces all damage you take by 3%.",
       1, -3, 1, effects={"damage_taken_pct": -0.03},
       connected_to=["divinity"],
       source="WotLK row 1, NEW to our tree: '30% of all damage taken by "
              "party members within 30 yards is redirected to the "
              "Paladin.' DEPARTURE - there is NO damage redirection in this "
              "engine, and a talent effect can never reach an ally. The "
              "talent's purpose is that the paladin absorbs what would have "
              "hurt the party; delivered as the paladin taking less itself. "
              "It is Divine Guardian's prerequisite, preserved below.")

T.node("guardians_favor", "Guardian's Favor",
       "Reduces the cooldown of your Divine Shield by 1 turn per rank.",
       1, -1, 2,
       effects={"ability_paladin_divine_shield_cooldown": 1},
       connected_to=["divine_strength"],
       source="WotLK row 1: 'Reduces the cooldown of your Hand of "
              "Protection by 1/2 min and increases the duration of your "
              "Hand of Freedom by 2/4 sec.' DEPARTURE - neither Hand spell "
              "exists. Divine Shield is the paladin's remaining personal "
              "immunity cooldown, so the reduction lands there. Kept from "
              "the outgoing tree.")

T.node("improved_righteous_fury", "Improved Righteous Fury",
       "Reduces all damage you take by 2% per rank.",
       1, 1, 3, effects={"damage_taken_pct": -0.02},
       connected_to=["divine_strength"],
       source="WotLK row 1: 'While Righteous Fury is active, all damage "
              "taken is reduced by 2%/4%/6%.' DEPARTURE on the condition "
              "only - there is no Righteous Fury ability to be active, so "
              "the reduction is unconditional at the real numbers. The "
              "outgoing version also granted threat, which is Vigilance's "
              "job in the Warrior and has no counterpart in this real "
              "talent.")

T.node("anticipation", "Anticipation",
       "Increases your dodge chance by 1% per rank.",
       1, 3, 5, effects={"dodge": 1.0},
       connected_to=["guardians_favor"],
       source="WotLK row 1: 'Increases your chance to dodge by 1%-5%.' "
              "Built verbatim and kept from the outgoing tree.")

T.node("toughness", "Toughness",
       "Increases your armor by 2% per rank.",
       1, 5, 5, effects={"armor_pct": 2.0},
       connected_to=["improved_righteous_fury"],
       source="WotLK row 1: 'Increases your armor value from items by "
              "2%-10% and reduces the duration of all movement slowing "
              "effects by 30%.' Armour half built verbatim; movement "
              "slowing does not exist. armor_pct is a FRACTION. Combined "
              "with Improved Devotion Aura this tree contributes 16 against "
              "check_talent_balance's class ceiling of 60.")

# ----------------------------------------------------------------- tier 2
T.node("divine_guardian", "Divine Guardian",
       "Increases your maximum health by 5% per rank.",
       2, -5, 2, effects={"max_health_pct": 0.05},
       connected_to=["divine_sacrifice"],
       source="WotLK row 2: 'When Divine Sacrifice is activated, your party "
              "and raid members within 30 yards take 10%/20% reduced damage "
              "for 6 sec.' DEPARTURE - a talent effect can never reach an "
              "ally. Delivered as the paladin's own durability. "
              "max_health_pct is a FRACTION read at character.py:1411 "
              "WITHOUT dividing by 100 - verified live. The real talent "
              "requires Divine Sacrifice, which connected_to reproduces. "
              "The outgoing version was a tier-6 node that ALSO authored "
              "low_health_threshold_pct alongside Ardent Defender's copy, "
              "summing the shared threshold above 1.0.")

T.node("improved_hammer_of_justice", "Improved Hammer of Justice",
       "Reduces the cooldown of your Hammer of Justice by 2 turns per rank.",
       2, -3, 2,
       effects={"ability_paladin_hammer_of_justice_cooldown": 2},
       connected_to=["divine_sacrifice"],
       source="WotLK row 2, NEW to our tree: 'Decreases the cooldown of "
              "your Hammer of Justice spell by 10/20 sec.' "
              "ability_<id>_cooldown is FLAT turns; 20 seconds re-derives "
              "as 4 turns over 2 ranks. talented_cooldown clamps at 1 turn "
              "so this cannot reach zero.")

T.node("blessing_of_sanctuary", "Blessing of Sanctuary",
       "Increases your Strength and Stamina by 10% and reduces all damage "
       "you take by 3%.",
       2, -1, 1,
       effects={"strength_pct": 10.0, "stamina_pct": 10.0,
                "damage_taken_pct": -0.03},
       connected_to=["anticipation"],
       source="WotLK row 2: 'Places a Blessing on the friendly target, "
              "reducing damage taken from all sources by 3% for 10 min and "
              "increasing strength and stamina by 10%.' DEPARTURE - a "
              "talent cannot place a blessing on anyone, so all three real "
              "numbers apply to the paladin. Kept from the outgoing tree, "
              "which had flat stamina and block instead of the real "
              "percentages.")

T.node("improved_devotion_aura", "Improved Devotion Aura",
       "Increases your armor by 2% per rank and healing you receive by 2% "
       "per rank.",
       2, 1, 3,
       effects={"armor_pct": 2.0, "healing_taken_pct": 0.02},
       connected_to=["anticipation"],
       source="WotLK row 2, built with both halves: 'Increases the armor "
              "bonus of your Devotion Aura by 50% and increases the amount "
              "healed on any target affected by any of your Auras by 6%.' "
              "There is no aura system, so both clauses apply to the "
              "paladin. The outgoing version was armor_pct alone at 5 "
              "ranks; corrected to the real 3.")

T.node("reckoning", "Reckoning",
       "Blocking has a 2% chance per rank to grant an extra attack.",
       2, 3, 5,
       proc={"trigger": "on_block", "chance": 2, "icd": 0,
             "extra_attack": True},
       connected_to=["toughness"],
       source="WotLK row 2: 'Gives you a 2%-10% chance after blocking or "
              "being hit by any damaging attack that the next 4 weapon "
              "swings within 8 sec will generate an additional attack.' "
              "Built as the real mechanic at the real chance curve. "
              "extra_attack is a BOOLEAN - exactly one extra attack, no "
              "count - so 'the next 4 swings' collapses to one, which is "
              "the engine's ceiling. Kept as a proc from the outgoing "
              "tree.")

# ----------------------------------------------------------------- tier 3
T.node("sacred_duty", "Sacred Duty",
       "Increases your Stamina by 2% per rank and reduces the cooldown of "
       "your Divine Shield by 2 turns per rank.",
       3, -1, 2,
       effects={"stamina_pct": 2.0,
                "ability_paladin_divine_shield_cooldown": 2},
       connected_to=["blessing_of_sanctuary"],
       source="WotLK row 3, built with both halves: 'Increases your total "
              "Stamina by 2%/4%, reduces the cooldown of your Divine Shield "
              "and Divine Protection spells by 30/60 sec.' Divine "
              "Protection does not exist. Stacks with Guardian's Favor on "
              "Divine Shield, as the real pair does. The outgoing version "
              "was stamina_pct alone.")

T.node("one_handed_weapon_specialization", "One-Handed Weapon Specialization",
       "Increases your physical damage by 3% per rank.",
       3, 1, 3, effects={"physical_damage": 0.03},
       connected_to=["improved_devotion_aura"],
       source="WotLK row 3: 'Increases all damage you deal when a "
              "one-handed melee weapon is equipped by 3%-10%.' Built minus "
              "the weapon gate - there is no weapon-type key. Corrected "
              "from the outgoing 5 ranks to the real 3. physical_damage is "
              "a FRACTION.")

# ----------------------------------------------------------------- tier 4
T.node("spiritual_attunement", "Spiritual Attunement",
       "Restores 5 mana every 5 seconds per rank.",
       4, -5, 2, effects={"mp5": 5},
       connected_to=["sacred_duty"],
       source="WotLK row 4, NEW to our tree: 'A passive ability that gives "
              "the Paladin mana when healed by other friendly targets' "
              "spells. The amount of mana gained is equal to 5%/10% of the "
              "amount healed.' DEPARTURE - there is no on-healed trigger; "
              "the proc vocabulary has on_heal_CAST (the caster's own) and "
              "nothing that fires on RECEIVING a heal. Delivered as flat "
              "mana regeneration, which is the same resource by a different "
              "route. mp5 is FLAT.")

T.node("redoubt", "Redoubt",
       "Increases your block chance by 5% per rank, and being struck raises "
       "it further for 2 turns.",
       4, -3, 3, effects={"block": 5.0},
       proc={"trigger": "on_damage_taken", "chance": 10, "icd": 1,
             "apply_effect": {"effect_id": "redoubt", "name": "Redoubt",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"block": 30},
                              "on_target": False}},
       connected_to=["sacred_duty"],
       source="WotLK row 4, built with BOTH halves - a node may carry "
              "effects AND a proc: 'Requires Shields. Increases your block "
              "value by 10%-30% and damaging melee and ranged attacks "
              "against you have a 10% chance to increase your chance to "
              "block by 30%.' DEPARTURE on the first half - block_value_pct "
              "is DEAD DATA (probed, zero read sites), so it grants block "
              "CHANCE instead of block value. The proc half is verbatim: "
              "the real 10% chance and the real +30% block. Weapon gate "
              "dropped. Kept as a proc from the outgoing tree.")

T.node("holy_shield", "Holy Shield",
       "Increases your block chance by 10%, and each block sears your "
       "attacker with Holy light.",
       4, -1, 1, effects={"block": 10.0},
       proc={"trigger": "on_block", "chance": 100, "icd": 0,
             "damage_flat": 35, "school": "holy"},
       connected_to=["blessing_of_sanctuary"],
       source="WotLK row 4: 'Increases chance to block by 30% for 10 sec "
              "and deals 79 Holy damage for each attack blocked while "
              "active. Each block expends a charge. 8 charges.' DEPARTURE - "
              "there is no paladin_holy_shield ability to unlock and no "
              "charge system, so it is a permanent but much smaller block "
              "bonus plus the real Holy damage on block. CRUCIAL: on an "
              "avoidance trigger such as on_block the incoming amount is "
              "ZERO, so bonus_pct or leech_pct would return nothing - "
              "damage_flat is the right payload. proc['school'] only TYPES "
              "a damage_flat payload; it is not a trigger-side filter. The "
              "real talent requires Blessing of Sanctuary and is Avenger's "
              "Shield's prerequisite, both preserved.")

T.node("ardent_defender", "Ardent Defender",
       "While below half health, reduces damage taken by 7% per rank.",
       4, 1, 3,
       effects={"low_health_damage_reduction_pct": 0.07},
       connected_to=["one_handed_weapon_specialization"],
       source="WotLK row 4: 'Damage that takes you below 35% health is "
              "reduced by 7%-20%. In addition, attacks which would "
              "otherwise kill you cause you to be healed.' The mitigation "
              "half is built verbatim at the real 7% per rank; there is no "
              "death-prevention hook for the second half. "
              "low_health_damage_reduction_pct reads the ACTOR's own health "
              "and defaults to a 50% threshold, so "
              "low_health_threshold_pct is NOT authored - it SUMS across "
              "talents and the outgoing tree authored it HERE and on Divine "
              "Guardian, taking the shared threshold above 1.0 and making "
              "both conditionals fire permanently.")

T.node("combat_expertise", "Combat Expertise",
       "Increases your expertise by 2, your Stamina by 2% and your critical "
       "strike chance by 2% per rank.",
       4, 3, 3,
       effects={"expertise": 2.0, "stamina_pct": 2.0,
                "crit_chance_physical": 2.0},
       connected_to=["reckoning"],
       source="WotLK row 4, built verbatim across all three halves: "
              "'Increases your expertise by 2-6, total Stamina and chance "
              "to critically hit by 2%-6%.' The outgoing version granted "
              "FLAT stamina rather than stamina_pct and omitted expertise - "
              "and flat `stamina` is not a valid STAT_CONVERSION_TARGET "
              "either, which is a separate trap this project has paid for. "
              "Corrected from 5 ranks to the real 3.")

# ----------------------------------------------------------------- tier 5
T.node("touched_by_the_light", "Touched by the Light",
       "Increases your spell power by 20% of your Strength per rank.",
       5, -3, 3,
       effects={"spell_power_from_strength_pct": 0.20},
       connected_to=["redoubt"],
       source="WotLK row 5, built verbatim: 'Increases your spell power by "
              "an amount equal to 20%-60% of your Strength and increases "
              "the amount healed by your critical heals by 30%.' The "
              "conversion is a REAL pairing - spell_power is a valid "
              "STAT_CONVERSION_TARGET and strength a valid source. THE UNIT "
              "IS A RAW MULTIPLIER, not a percentage: character.py:1551 "
              "does `gained = source * pct`, so 0.20 per rank reaches the "
              "real 60%. The critical-heal clause has no key. This is the "
              "pairing that makes Divine Strength at tier 0 worth taking. "
              "The outgoing version was stamina_pct plus Holy Light "
              "healing.")

T.node("avengers_shield", "Avenger's Shield",
       "Teaches Avenger's Shield, hurling holy force that leaps between "
       "enemies.",
       5, -1, 1, node_type="active",
       effects={"unlock_ability": "paladin_avengers_shield"},
       connected_to=["holy_shield"],
       source="WotLK row 5, kept - the ONLY unlock for "
              "paladin_avengers_shield, which is requires_talent. The real "
              "talent requires Holy Shield, which connected_to reproduces. "
              "Moved from tier 4 to its real row.")

T.node("shield_of_the_templar", "Shield of the Templar",
       "Reduces all damage you take by 1% per rank and increases your "
       "Avenger's Shield damage by 10% per rank.",
       5, 1, 3,
       effects={"damage_taken_pct": -0.01,
                "ability_paladin_avengers_shield_damage": 0.10},
       connected_to=["avengers_shield"],
       source="WotLK row 5: 'Reduces all damage taken by 1%/2%/3% and "
              "grants your Avenger's Shield a 100% chance to silence your "
              "targets for 3 sec.' The mitigation half is verbatim; there "
              "is no silence key. The Avenger's Shield damage clause is "
              "carried over from the outgoing version, which had it at 15% "
              "per rank. The real talent requires Avenger's Shield, "
              "reproduced.")

T.node("guarded_by_the_light", "Guarded by the Light",
       "Reduces spell damage taken by 3% per rank.",
       5, 3, 2, effects={"spell_damage_taken_pct": -0.03},
       connected_to=["ardent_defender"],
       source="WotLK row 5: 'Reduces spell damage taken by 3%/6% and gives "
              "a 100% chance to refresh the duration of your Divine Plea "
              "when you hit an enemy.' The mitigation half is verbatim; "
              "Divine Plea does not exist and nothing can refresh another "
              "effect's duration anyway. spell_damage_taken_pct is a "
              "FRACTION as a talent effect and NEGATIVE reduces. Kept from "
              "the outgoing tree, corrected from 3 ranks to the real 2.")

T.node("judgements_of_the_just", "Judgements of the Just",
       "Reduces the cooldown of your Hammer of Justice by 1 turn per rank, "
       "and your Judgement slows the target's attacks for 2 turns.",
       5, 5, 2,
       effects={"ability_paladin_hammer_of_justice_cooldown": 1},
       proc={"trigger": "on_cast", "chance": 100, "icd": 0,
             "ability_filter": ["paladin_judgement"],
             "apply_effect": {"effect_id": "judgements_of_the_just",
                              "name": "Judgements of the Just",
                              "effect_type": "debuff", "duration": 2,
                              "stat_mods": {"haste": -20}}},
       connected_to=["ardent_defender"],
       source="WotLK row 5, built with BOTH halves: 'Reduces the cooldown "
              "of your Hammer of Justice by 5/10 sec, increases the "
              "duration of your Seal of Justice effect by 1 sec and your "
              "Judgement spells also reduce the melee attack speed of the "
              "target.' Seal of Justice does not exist. The attack-speed "
              "reduction is the real mechanic and becomes haste -20 on the "
              "target. Stacks with Improved Hammer of Justice. This talent "
              "is in RETRIBUTION in our outgoing data; the real game puts "
              "it in Protection, which is where it sits now.")

# ----------------------------------------------------------------- tier 6
T.node("hammer_of_the_righteous", "Hammer of the Righteous",
       "Increases the damage of your Crusader Strike by 20%.",
       6, 1, 1,
       effects={"ability_paladin_crusader_strike_damage": 0.20},
       connected_to=["shield_of_the_templar"],
       source="WotLK row 10, the capstone: 'Hammer the current target and "
              "up to 2 additional nearby targets, causing 4 times your main "
              "hand damage per second as Holy damage.' DEPARTURE - there is "
              "no paladin_hammer_of_the_righteous ability to unlock and "
              "nothing modifies an ability's target count. Crusader Strike "
              "is the paladin's equivalent instant strike, so the capstone "
              "makes that hit considerably harder instead. Kept from the "
              "outgoing tree, which had it at 8% per rank over 3 ranks.")


def main():
    return T.write(was="23 nodes, 71 points - 7 proc, 1 ability-scoped, "
                       "9 flat stat, 1 unlock, 3 mixed, 2 conditional")


if __name__ == "__main__":
    sys.exit(main())
