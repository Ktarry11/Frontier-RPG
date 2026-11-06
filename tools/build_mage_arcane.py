#!/usr/bin/env python3
"""Rebuild Mage Arcane from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_mage_arcane.py

SOURCE: data/reference/wotlk/mage.json (from Spell.dbc).
Worksheet: data/reference/wotlk_worksheets/mage.md.

ROLE: raw arcane power and mana management. The tree that turns Intellect
into everything else.

TWO REAL STAT CONVERSIONS, and they are the tree's identity. Arcane
Fortitude is "+150% armor from Intellect" and Mind Mastery is "+15% spell
power from Intellect" - both are valid pairings (armor and spell_power are
STAT_CONVERSION_TARGETS, intellect a source) and both are RAW MULTIPLIERS,
not percentages (character.py:1551 does `gained = source * pct`). With
Arcane Mind's +15% Intellect feeding them, this is the one tree where the
conversions compound as the real game intends.

CAST TIMES AND PUSHBACK account for five real talents here - Arcane
Stability, Presence of Mind's instant-cast clause, Arcane Meditation,
Arcane Potency's "next spell", Missile Barrage - and none of it exists.
Each pays out as throughput, cost or crit.

ABILITIES THE REAL TREE WANTS AND WE LACK: Arcane Missiles, Arcane Blast,
Arcane Barrage, Blink, Invisibility, Amplify/Dampen Magic, Slow, Arcane
Power, Frost Ward, Fire Ward. That is the most of any Mage tree, because
Arcane's own spells are mostly absent - arcane_explosion is the only real
Arcane nuke in the kit. Talents on the missing ones are re-aimed at
arcane_explosion and the mage's generic spells, or dropped: Magic
Attunement, Improved Blink, Arcane Empowerment, Arcane Flows and Slow are
DROPPED.

KEPT MANDATORY: Presence of Mind is the only unlock for
mage_presence_of_mind, which is requires_talent.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

T = Tree("mage_arcane", "Mage Arcane",
         "Raw arcane power - Intellect turned into armour, mana and "
         "destruction.")

# ----------------------------------------------------------------- tier 0
T.node("arcane_subtlety", "Arcane Subtlety",
       "Reduces the threat your spells generate by 10% per rank, and your "
       "spells lower the target's resistances for 3 turns.",
       0, -2, 2, effects={"threat_generation_pct": -0.10},
       proc={"trigger": "on_damage_cast", "chance": 50, "icd": 0,
             "apply_effect": {"effect_id": "arcane_subtlety",
                              "name": "Arcane Subtlety",
                              "effect_type": "debuff", "duration": 3,
                              "stat_mods": {"magic_resistance": -20}}},
       source="WotLK row 0: 'Reduces the chance your helpful spells and "
              "damage over time effects will be dispelled by 15%/30% and "
              "reduces your target's resistance to all your spells.' Dispel "
              "resistance does not exist, so that half becomes threat. The "
              "SECOND half IS buildable and was missed on the first pass: "
              "magic_resistance is one of only EIGHT stat_mods a MONSTER "
              "can actually read, and it is FLAT on a monster - so a debuff "
              "really can strip a target's resistance. That is more "
              "faithful than the flat threat node this started as.")

T.node("arcane_focus", "Arcane Focus",
       "Increases your chance to hit by 1% per rank and reduces your spell "
       "costs by 1% per rank.",
       0, 0, 3,
       effects={"hit_rating": 1.0, "all_ability_cost_pct": 0.01},
       source="WotLK row 0, built verbatim with both halves: 'Increases "
              "your chance to hit and reduces the mana cost of your Arcane "
              "spells by 1%/2%/3%.' There is no way to scope either to one "
              "school. all_ability_cost_pct is a FRACTION where POSITIVE IS "
              "A REDUCTION.")

T.node("arcane_stability", "Arcane Stability",
       "Increases the damage of your Arcane Explosion by 3% per rank.",
       0, 2, 5,
       effects={"ability_mage_arcane_explosion_damage": 0.03},
       source="WotLK row 0: 'Reduces the pushback suffered from damaging "
              "attacks while casting Arcane Missiles and Arcane Blast by "
              "14%-70%.' DEPARTURE - no cast times, so no pushback, and "
              "neither named spell exists. arcane_explosion is the kit's "
              "only real Arcane nuke, so the throughput lands there.")

# ----------------------------------------------------------------- tier 1
T.node("arcane_fortitude", "Arcane Fortitude",
       "Increases your armor by 50% of your Intellect per rank.",
       1, -4, 3,
       effects={"armor_from_intellect_pct": 0.50},
       connected_to=["arcane_subtlety"],
       source="WotLK row 1, NEW to our tree, built verbatim: 'Increases "
              "your armor by an amount equal to 50%-150% of your "
              "Intellect.' A REAL stat conversion - armor is a valid "
              "STAT_CONVERSION_TARGET and intellect a valid source. THE "
              "UNIT IS A RAW MULTIPLIER, not a percentage "
              "(character.py:1551), so 0.50 per rank reaches the real 150%. "
              "Pairs with Arcane Mind two tiers down.")

T.node("magic_absorption", "Magic Absorption",
       "Increases all your resistances by 10 per rank.",
       1, -2, 2,
       effects={"fire_resistance": 10, "frost_resistance": 10,
                "nature_resistance": 10, "shadow_resistance": 10,
                "arcane_resistance": 10, "holy_resistance": 10},
       connected_to=["arcane_subtlety"],
       source="WotLK row 1, NEW to our tree: 'Increases all resistances by "
              "1 per level and causes all spells you fully resist to "
              "restore 2% of your total mana.' The resistance half is built "
              "across all six schools; there is no full-resist event for "
              "the mana half. NOTE Kyle's standing rule that magic "
              "resistance gear comes only after level 45 - this is a "
              "talent rather than gear, and a level-60 mage spending here "
              "is well past that line.")

T.node("spell_impact", "Spell Impact",
       "Increases the damage of your Arcane Explosion, Fire Blast and "
       "Fireball by 2% per rank.",
       1, 0, 3,
       effects={"ability_mage_arcane_explosion_damage": 0.02,
                "ability_mage_fire_blast_damage": 0.02,
                "ability_mage_fireball_damage": 0.02},
       connected_to=["arcane_focus"],
       source="WotLK row 1, NEW to our tree, built verbatim for the three "
              "real spells that exist: 'Increases the damage of your Arcane "
              "Explosion, Arcane Blast, Blast Wave, Fire Blast, Scorch, "
              "Fireball and Frostfire Bolt spells by 2%-6%.'")

T.node("arcane_concentration", "Arcane Concentration",
       "Your damaging spells have a 2% chance per rank to make your next "
       "spells cost 40% less for 2 turns.",
       1, 2, 5,
       proc={"trigger": "on_damage_cast", "chance": 2, "icd": 0,
             "apply_effect": {"effect_id": "clearcasting",
                              "name": "Clearcasting",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"all_ability_cost_pct": 40.0},
                              "on_target": False}},
       connected_to=["arcane_focus"],
       source="WotLK row 1: 'Gives you a 2%-10% chance of entering a "
              "Clearcasting state after any damage spell hits a target. The "
              "Clearcasting state reduces the mana cost of your next damage "
              "spell by 100%.' Built with the real chance curve and the "
              "real Clearcasting name. 'Next spell' becomes a 2-turn "
              "window, at 40% rather than 100%, because a window is more "
              "generous than a single cast. MIND THE FLIP: "
              "all_ability_cost_pct is PERCENTAGE POINTS inside a status "
              "effect and a FRACTION as a talent effect. It is Arcane "
              "Potency's trigger in the real tree.")

T.node("student_of_the_mind", "Student of the Mind",
       "Increases your Spirit by 3% per rank.",
       1, 4, 3, effects={"spirit_pct": 3.0},
       connected_to=["arcane_concentration"],
       source="WotLK row 1, NEW to our tree, built verbatim: 'Increases "
              "your total Spirit by 4%/7%/10%.' spirit_pct is PERCENTAGE "
              "POINTS, read off `bonuses` at character.py and divided by "
              "100.")

T.node("focus_magic", "Focus Magic",
       "Your critical strikes grant 3% spell critical chance for 3 turns.",
       1, 6, 1,
       proc={"trigger": "on_crit", "chance": 100, "icd": 0,
             "apply_effect": {"effect_id": "focus_magic",
                              "name": "Focus Magic",
                              "effect_type": "buff", "duration": 3,
                              "stat_mods": {"crit_chance_spell": 3},
                              "on_target": False}},
       connected_to=["arcane_concentration"],
       source="WotLK row 1, NEW to our tree: 'Increases the target's chance "
              "to critically hit with spells by 3%. When the target "
              "critically hits, the caster gains 3% spell crit for 10 sec.' "
              "DEPARTURE on the source only - A TALENT EFFECT CAN NEVER "
              "REACH AN ALLY and no trigger reports an ally's crit, so it "
              "fires on the MAGE'S OWN crit. But the real talent's SHAPE is "
              "a proc, so it is built as one rather than flattened: the "
              "real 3% for the real 10 seconds (3 turns), self-sustaining "
              "off your own crits exactly as the real version "
              "self-sustains off the target's.")

# ----------------------------------------------------------------- tier 2
T.node("arcane_shielding", "Arcane Shielding",
       "Increases the absorption of your Mana Shield by 15% per rank.",
       2, -4, 2,
       effects={"ability_mage_mana_shield_potency": 0.15},
       connected_to=["arcane_fortitude"],
       source="WotLK row 2, built verbatim: 'Decreases the mana lost per "
              "point of damage taken when Mana Shield is active by 17%/33% "
              "and increases the amount absorbed.' The mana-per-point "
              "exchange rate is not modelled, so only the absorb half is "
              "built. ability_<id>_potency scales the ability's own "
              "stat_mods.")

T.node("improved_counterspell", "Improved Counterspell",
       "Reduces the cooldown of your Counterspell by 1 turn per rank.",
       2, -2, 2,
       effects={"ability_mage_counterspell_cooldown": 1},
       connected_to=["magic_absorption"],
       source="WotLK row 2, NEW to our tree: 'Your Counterspell also "
              "silences the target for 2/4 sec.' DEPARTURE - there is no "
              "silence and no interrupt key in this engine at all. "
              "Delivered as availability instead, which is the only way to "
              "make Counterspell better here.")

T.node("presence_of_mind", "Presence of Mind",
       "Teaches Presence of Mind, letting you cast without hesitation.",
       2, 0, 1, node_type="active",
       effects={"unlock_ability": "mage_presence_of_mind"},
       connected_to=["spell_impact"],
       source="WotLK row 2, kept - the ONLY unlock for "
              "mage_presence_of_mind, which is requires_talent. Its "
              "instant-cast clause lives in the ability. It is Arcane "
              "Instability's and Arcane Potency's prerequisite in the real "
              "tree, both preserved below.")

T.node("arcane_meditation", "Arcane Meditation",
       "Restores 8 mana every 5 seconds per rank.",
       2, 2, 3, effects={"mp5": 8},
       connected_to=["arcane_concentration"],
       source="WotLK row 2: 'Allows 17%/33%/50% of your mana regeneration "
              "to continue while casting.' DEPARTURE - there are no cast "
              "times, so regeneration never stops and there is nothing to "
              "restore. Delivered as flat regeneration. mp5 is FLAT and "
              "lands on the attribute.")

T.node("torment_the_weak", "Torment the Weak",
       "Increases your damage by 4% per rank against targets below 35% "
       "health.",
       2, 4, 3, effects={"low_health_damage_pct": 0.04},
       connected_to=["student_of_the_mind"],
       source="WotLK row 2: 'Your Frostbolt, Fireball, Pyroblast, Arcane "
              "Missiles, Arcane Blast and Arcane Barrage spells deal "
              "2%/4%/6% more damage to targets afflicted by a movement "
              "slowing effect.' DEPARTURE - there are no movement slowing "
              "effects and nothing reads a debuff on the target. The "
              "engine's own low-health conditional stands in: "
              "low_health_damage_pct reads the TARGET's health and defaults "
              "to a 35% threshold. low_health_threshold_pct is NOT authored "
              "- it SUMS across talents and the default is already right.")

T.node("arcane_mind", "Arcane Mind",
       "Increases your Intellect by 3% per rank.",
       2, 6, 5, effects={"intellect_pct": 3.0},
       connected_to=["focus_magic"],
       source="WotLK row 2, built verbatim: 'Increases your total Intellect "
              "by 3%-15%.' intellect_pct is PERCENTAGE POINTS. This is the "
              "node that makes Arcane Fortitude and Mind Mastery worth "
              "taking, which is exactly the role it plays in the real "
              "tree.")

# ----------------------------------------------------------------- tier 3
T.node("prismatic_cloak", "Prismatic Cloak",
       "Reduces all damage you take by 2% per rank.",
       3, -2, 3, effects={"damage_taken_pct": -0.02},
       connected_to=["arcane_shielding"],
       source="WotLK row 3, NEW to our tree: 'Reduces all damage taken by "
              "2%/4%/6% and reduces the fade time of your Invisibility "
              "spell.' The mitigation half is built verbatim; Invisibility "
              "does not exist. damage_taken_pct is read RAW on both sides.")

T.node("arcane_instability", "Arcane Instability",
       "Increases your spell damage and critical chance by 1% per rank.",
       3, 0, 3,
       effects={"spell_damage": 0.01, "crit_chance_spell": 1.0},
       connected_to=["presence_of_mind"],
       source="WotLK row 3, built verbatim with both halves: 'Increases the "
              "damage done by your spells and your critical strike chance "
              "by 1%/2%/3%.' spell_damage is a FRACTION and "
              "crit_chance_spell is PERCENTAGE POINTS - mixed conventions "
              "on one node, which no rule infers from the key names. The "
              "real talent requires Presence of Mind, reproduced.")

T.node("arcane_potency", "Arcane Potency",
       "Casting Presence of Mind sharpens your spells, granting 15% spell "
       "critical chance per rank for 2 turns.",
       3, 2, 2,
       proc={"trigger": "on_cast", "chance": 100, "icd": 0,
             "ability_filter": ["mage_presence_of_mind"],
             "apply_effect": {"effect_id": "arcane_potency",
                              "name": "Arcane Potency",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"crit_chance_spell": 30},
                              "on_target": False}},
       connected_to=["presence_of_mind"],
       source="WotLK row 3: 'Increases the critical strike chance of your "
              "next damaging spell by 15%/30% after gaining Clearcasting or "
              "casting Presence of Mind.' Built as the real PROC rather "
              "than flattened into permanent crit, because the real "
              "talent's shape is a trigger and a window. The "
              "Presence-of-Mind half is exact via ability_filter; the "
              "Clearcasting half cannot be built, since nothing reads "
              "whether the ACTOR carries a specific buff. 'Next spell' "
              "becomes a 2-turn window - nothing consumes a buff on use - "
              "and the payload is the real 30%, not rank-scaled, because a "
              "proc's payload does not scale with points. The real talent "
              "requires Presence of Mind, reproduced.")

# ----------------------------------------------------------------- tier 4
T.node("incanters_absorption", "Incanter's Absorption",
       "Your Mana Shield and Ice Barrier raise your spell damage by 10% for "
       "3 turns.",
       4, -2, 3,
       proc={"trigger": "on_cast", "chance": 33, "icd": 0,
             "ability_filter": ["mage_mana_shield", "mage_ice_barrier"],
             "apply_effect": {"effect_id": "incanters_absorption",
                              "name": "Incanter's Absorption",
                              "effect_type": "buff", "duration": 3,
                              "stat_mods": {"damage_dealt_pct": 10.0},
                              "on_target": False}},
       connected_to=["prismatic_cloak"],
       source="WotLK row 4, NEW to our tree: 'When your Mana Shield, Frost "
              "Ward, Fire Ward, or Ice Barrier absorbs damage your spell "
              "damage is increased by 5%-15% for 10 sec.' DEPARTURE on the "
              "trigger - there is no event for an absorb being consumed - "
              "so it fires when the shield is CAST. The two real shields "
              "are in the filter. 10 seconds is 3 turns. NOTE the stat_mod "
              "is damage_dealt_pct in PERCENTAGE POINTS: spell_damage would "
              "be SILENT DEAD DATA here, because it is read through the "
              "talent channel and a status effect's stat_mods go to "
              "get_status_stat_mod.")

T.node("mind_mastery", "Mind Mastery",
       "Increases your spell power by 3% of your Intellect per rank.",
       4, 0, 5,
       effects={"spell_power_from_intellect_pct": 0.03},
       connected_to=["arcane_instability"],
       source="WotLK row 4, built verbatim: 'Increases spell power by "
              "3%-15% of your total Intellect.' A REAL stat conversion, and "
              "the tree's payoff node. THE UNIT IS A RAW MULTIPLIER "
              "(character.py:1551: `gained = source * pct`), so 0.03 per "
              "rank reaches the real 15%; authoring 15 would have granted "
              "fifteen times the mage's Intellect as spell power.")

T.node("netherwind_presence", "Netherwind Presence",
       "Increases your haste by 2% per rank.",
       4, 2, 3, effects={"haste": 2.0},
       connected_to=["arcane_potency"],
       source="WotLK row 5 in the real tree, moved up one tier: 'Increases "
              "your spell haste by 2%/4%/6%.' Built verbatim. haste is "
              "PERCENTAGE POINTS. Moved because this tree lost five "
              "talents to missing abilities and tier 4 would otherwise be "
              "thin.")

# ----------------------------------------------------------------- tier 5
T.node("missile_barrage", "Missile Barrage",
       "Your Fireball and Frostbolt have a 8% chance per rank to strike "
       "again.",
       5, -1, 5,
       proc={"trigger": "on_damage_cast", "chance": 8, "icd": 0,
             "ability_filter": ["mage_fireball", "mage_frostbolt"],
             "damage_flat": 100, "school": "arcane"},
       connected_to=["mind_mastery"],
       source="WotLK row 5: 'Gives your Arcane Blast a 40% chance, and your "
              "Arcane Barrage, Fireball, Frostbolt and Frostfire Bolt a "
              "8%-40% chance, to reduce the channel time of your next "
              "Arcane Missiles.' DEPARTURE - no channelling and no Arcane "
              "Missiles. The real talent's purpose is a free extra volley, "
              "so it is delivered as flat Arcane damage off the two real "
              "spells in its list. proc['school'] only TYPES a damage_flat "
              "payload; it is not a trigger-side filter.")

T.node("spell_power", "Spell Power",
       "Increases the critical damage of your spells by 25% per rank.",
       5, 1, 2, effects={"crit_damage_spell": 0.25},
       connected_to=["netherwind_presence"],
       source="WotLK row 5, built verbatim: 'Increases critical strike "
              "damage bonus of all spells by 25%/50%.' crit_damage_spell is "
              "a FRACTION, read at abilities.py:1460 inside a ternary - so "
              "the probe finds no literal read site and it is nonetheless "
              "live. NOTE it is DEAD inside a status effect; only the "
              "talent-effect form works, which is what this is.")

# ----------------------------------------------------------------- tier 6
T.node("arcane_barrage", "Arcane Barrage",
       "Increases the damage of your Arcane Explosion by 30%.",
       6, 0, 1,
       effects={"ability_mage_arcane_explosion_damage": 0.30},
       connected_to=["missile_barrage"],
       source="WotLK row 10, the capstone: 'Launches several missiles at "
              "the enemy target, causing 386 to 470 Arcane damage.' "
              "DEPARTURE - there is no mage_arcane_barrage ability to "
              "unlock. The capstone instead makes the tree's one real "
              "Arcane nuke hit considerably harder, which is the nearest "
              "honest reading. This is the thinnest capstone in the Mage "
              "and is marked as such: the real talent is a new spell, and a "
              "damage bonus is not a new spell.")


def main():
    return T.write(was="23 nodes, 65 points - 14 proc, 9 with no proc and "
                       "no unlock")


if __name__ == "__main__":
    sys.exit(main())
