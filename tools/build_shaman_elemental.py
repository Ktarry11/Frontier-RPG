#!/usr/bin/env python3
"""Rebuild Shaman Elemental from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_shaman_elemental.py

SOURCE: data/reference/wotlk/shaman.json (from Spell.dbc).
Worksheet: data/reference/wotlk_worksheets/shaman.md.

ROLE: caster shaman. Lightning Bolt and Chain Lightning, Lava Burst off
Flame Shock, and Fire totems doing work in the background.

FIRE TOTEM TALENTS ARE NOW MEANINGFUL, which they were not before. Call of
Flame and Elemental Fury both modify Searing and Magma Totem, and those
two now occupy the Fire element slot (one at a time) after the totem fix
earlier in this session - so the talents point at totems a player actually
chooses between rather than two of thirteen they could all have up.

CAST TIMES ARE THE WALL AGAIN: Eye of the Storm (pushback), Lightning
Mastery (cast time), Elemental Mastery's instant-cast clause and Shamanism
all depend on a system that does not exist. Each pays out as throughput.

ABILITIES THE REAL TREE WANTS AND WE LACK: Fire Nova, Wind Shear, Totem of
Wrath. Improved Fire Nova and Elemental Reach are dropped; Totem of Wrath
becomes a spell-power talent since there is no totem to summon.

UNIT CONVENTIONS: crit_chance_spell / crit_chance_physical / hit_rating are
PERCENTAGE POINTS; damage_taken_pct is read RAW; crit_damage_spell /
threat_generation_pct / spell_damage are FRACTIONS; mp5 is FLAT;
ability_<id>_cost_pct is a FRACTION where POSITIVE IS A REDUCTION.

KEPT MANDATORY: Elemental Mastery and Thunderstorm are the only unlocks
for shaman_elemental_mastery_cast and shaman_thunderstorm.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

#: The Shock spells and the Lightning spells, used by several talents.
SHOCKS = ["shaman_earth_shock", "shaman_flame_shock", "shaman_frost_shock"]
LIGHTNING = ["shaman_lightning_bolt", "shaman_chain_lightning"]

T = Tree("shaman_elemental", "Shaman Elemental",
         "Mastery of storm and fire - lightning, lava and the totems that "
         "feed them.")

# ----------------------------------------------------------------- tier 0
T.node("convection", "Convection",
       "Reduces the cost of your Shock and Lightning spells by 2% per rank.",
       0, -1, 5,
       effects={f"ability_{a}_cost_pct": 0.02
                for a in SHOCKS + LIGHTNING + ["shaman_lava_burst"]},
       source="WotLK row 0: 'Reduces the mana cost of your Shock, Lightning "
              "Bolt, Chain Lightning, Lava Burst, and Wind Shear spells by "
              "2%-10%.' Built verbatim for the five that exist; Wind Shear "
              "does not. _cost_pct is a FRACTION where POSITIVE IS A "
              "REDUCTION. The outgoing tree had no cost talent at all.")

T.node("concussion", "Concussion",
       "Increases the damage of your Lightning and Shock spells by 1% per "
       "rank.",
       0, 1, 5,
       effects={f"ability_{a}_damage": 0.01
                for a in SHOCKS + LIGHTNING + ["shaman_lava_burst"]},
       source="WotLK row 0, built verbatim: 'Increases the damage done by "
              "your Lightning Bolt, Chain Lightning, Thunderstorm, Lava "
              "Burst and Shock spells by 1%-5%.' All five real spells that "
              "exist are covered.")

# ----------------------------------------------------------------- tier 1
T.node("call_of_flame", "Call of Flame",
       "Increases the damage of your Searing and Magma Totems by 5% per "
       "rank and of your Lava Burst by 2% per rank.",
       1, -5, 3,
       effects={"ability_shaman_searing_totem_damage": 0.05,
                "ability_shaman_magma_totem_damage": 0.05,
                "ability_shaman_lava_burst_damage": 0.02},
       connected_to=["convection"],
       source="WotLK row 1, built verbatim: 'Increases the damage done by "
              "your Fire Totems and Fire Nova by 5%-15%, and damage done by "
              "your Lava Burst spell by 2%-6%.' Fire Nova does not exist; "
              "the two Fire totems do, and they now occupy the Fire element "
              "slot one at a time after the totem fix, so this talent "
              "points at a real choice. Kept from the outgoing tree, which "
              "had it as a flat scalar.")

T.node("reverberation", "Reverberation",
       "Reduces the cooldown of your Shock spells by 1 turn.",
       1, -3, 5,
       effects={f"ability_{a}_cooldown": 1 for a in SHOCKS},
       connected_to=["convection"],
       source="WotLK row 1: 'Reduces the cooldown of your Shock and Wind "
              "Shear spells by 0.2-1 sec.' Built as 1 turn flat across all "
              "three Shocks - ability_<id>_cooldown is FLAT turns and "
              "talented_cooldown clamps at 1, so five ranks cannot drive a "
              "Shock to zero. Wind Shear does not exist.")

T.node("elemental_warding", "Elemental Warding",
       "Reduces all damage you take by 2% per rank.",
       1, -1, 3, effects={"damage_taken_pct": -0.02},
       connected_to=["concussion"],
       source="WotLK row 1, NEW to our tree, built verbatim: 'Reduces all "
              "damage taken by 2%/4%/6%.' damage_taken_pct is read RAW on "
              "both sides.")

T.node("elemental_devastation", "Elemental Devastation",
       "Your spell criticals raise your melee critical chance by 9% for 3 "
       "turns.",
       1, 1, 3,
       proc={"trigger": "on_crit", "chance": 33, "icd": 0,
             "apply_effect": {"effect_id": "elemental_devastation",
                              "name": "Elemental Devastation",
                              "effect_type": "buff", "duration": 3,
                              "stat_mods": {"crit_chance_physical": 9},
                              "on_target": False}},
       connected_to=["concussion"],
       source="WotLK row 1, NEW to our tree: 'Your non-periodic offensive "
              "spell crits will increase your chance to get a critical "
              "strike with melee attacks by 3%-9% for 10 sec.' Built with "
              "the real 9% and the real 10 seconds (3 turns). Ranked by "
              "chance, since a proc's payload does not scale with points. "
              "The 'non-periodic' restriction is moot here - dots never "
              "roll crit in this engine at all.")

T.node("elemental_fury", "Elemental Fury",
       "Increases the critical damage of your spells by 20% per rank.",
       1, 3, 5, effects={"crit_damage_spell": 0.20},
       connected_to=["elemental_devastation"],
       source="WotLK row 1: 'Increases the critical strike damage bonus of "
              "your Searing and Magma Totems and your Fire, Frost, and "
              "Nature spells by 20%-100%.' Built as school-wide spell crit "
              "damage - crit_damage_spell is a FRACTION, read at "
              "abilities.py:1460 inside a ternary, which is why the probe "
              "finds no literal read site and it is nonetheless live. NOTE "
              "this key is DEAD inside a status effect; it only works as a "
              "talent effect, which is what this is. It is Lightning "
              "Mastery's prerequisite, preserved below.")

# ----------------------------------------------------------------- tier 2
T.node("elemental_focus", "Elemental Focus",
       "Your spell criticals have a 33% chance per rank to make your next "
       "spells cheaper for 2 turns.",
       2, -5, 3,
       proc={"trigger": "on_crit", "chance": 33, "icd": 0,
             "apply_effect": {"effect_id": "elemental_focus",
                              "name": "Clearcasting",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"all_ability_cost_pct": 40.0},
                              "on_target": False}},
       connected_to=["call_of_flame"],
       source="WotLK row 1: 'After landing a non-periodic critical strike "
              "with a Fire, Frost, or Nature damage spell, you enter a "
              "Clearcasting state, reducing the mana cost of your next 2 "
              "damage or healing spells by 40%.' Built with the real 40% "
              "and the real Clearcasting name. 'Next 2 spells' becomes a "
              "2-turn window - nothing counts casts or consumes a buff on "
              "use. MIND THE FLIP: all_ability_cost_pct is PERCENTAGE "
              "POINTS inside a status effect (40.0) and a FRACTION as a "
              "talent effect. It is Call of Thunder's prerequisite.")

T.node("call_of_thunder", "Call of Thunder",
       "Increases the critical chance of your Lightning Bolt and Chain "
       "Lightning by 5%.",
       2, -3, 1,
       effects={"ability_shaman_lightning_bolt_crit": 5.0,
                "ability_shaman_chain_lightning_crit": 5.0},
       connected_to=["elemental_focus"],
       source="WotLK row 2, built verbatim: 'Increases the critical strike "
              "chance of your Lightning Bolt, Chain Lightning and "
              "Thunderstorm spells by an additional 5%.' "
              "ability_<id>_crit is PERCENTAGE POINTS. The real talent "
              "requires Elemental Focus, which connected_to reproduces, and "
              "is Elemental Mastery's prerequisite.")

T.node("eye_of_the_storm", "Eye of the Storm",
       "Reduces the threat your spells generate by 10% per rank.",
       2, -1, 3, effects={"threat_generation_pct": -0.10},
       connected_to=["elemental_warding"],
       source="WotLK row 2: 'Reduces the pushback suffered from damaging "
              "attacks while casting Lightning Bolt, Chain Lightning, Lava "
              "Burst and Healing Wave by 70%.' DEPARTURE - no cast times "
              "and so no pushback. Being able to cast under pressure is "
              "closest to not drawing attention, so it pays out as threat. "
              "threat_generation_pct is a FRACTION.")

T.node("unrelenting_storm", "Unrelenting Storm",
       "Restores 8 mana every 5 seconds per rank.",
       2, 1, 3, effects={"mp5": 8},
       connected_to=["elemental_warding"],
       source="WotLK row 2, NEW to our tree: 'Regenerate mana equal to "
              "4%-12% of your Intellect every 5 sec, even while casting.' "
              "DEPARTURE - mp5 cannot be derived from a stat (mp5 is not a "
              "STAT_CONVERSION_TARGET), and there is no casting state to be "
              "exempt from. Delivered as flat regeneration. mp5 is FLAT and "
              "lands on the attribute.")

T.node("elemental_precision", "Elemental Precision",
       "Increases your chance to hit by 1% per rank.",
       2, 3, 3, effects={"hit_rating": 1.0},
       connected_to=["elemental_fury"],
       source="WotLK row 3: 'Increases your chance to hit with Fire, Frost "
              "and Nature spells by 1%/2%/3% and reduces the threat caused "
              "by those spells.' The hit half is built verbatim; the threat "
              "half is Eye of the Storm's job here, so it is not doubled. "
              "hit_rating is PERCENTAGE POINTS and is NOT a valid "
              "STAT_CONVERSION_TARGET.")

# ----------------------------------------------------------------- tier 3
T.node("lightning_mastery", "Lightning Mastery",
       "Increases the damage of your Lightning Bolt, Chain Lightning and "
       "Lava Burst by 2% per rank.",
       3, -1, 5,
       effects={"ability_shaman_lightning_bolt_damage": 0.02,
                "ability_shaman_chain_lightning_damage": 0.02,
                "ability_shaman_lava_burst_damage": 0.02},
       connected_to=["elemental_fury"],
       source="WotLK row 3: 'Reduces the cast time of your Lightning Bolt, "
              "Chain Lightning, and Lava Burst spells by 0.1-0.5 sec.' "
              "DEPARTURE - no cast times. A shorter cast is more "
              "throughput, so it is delivered as damage on the same three "
              "real spells. The real talent requires Elemental Fury, which "
              "connected_to reproduces.")

T.node("booming_echoes", "Booming Echoes",
       "Reduces the cooldown of your Flame Shock and Frost Shock by 1 turn "
       "and increases their damage by 10% per rank.",
       3, 1, 2,
       effects={"ability_shaman_flame_shock_cooldown": 1,
                "ability_shaman_frost_shock_cooldown": 1,
                "ability_shaman_flame_shock_damage": 0.10,
                "ability_shaman_frost_shock_damage": 0.10},
       connected_to=["elemental_precision"],
       source="WotLK row 4, NEW to our tree, built verbatim with both "
              "halves: 'Reduces the cooldown of your Flame Shock and Frost "
              "Shock spells by an additional 1/2 sec., and increases the "
              "direct damage of those spells by 10%/20%.' Stacks with "
              "Reverberation on both Shocks; talented_cooldown clamps at 1 "
              "turn.")

# ----------------------------------------------------------------- tier 4
T.node("elemental_mastery", "Elemental Mastery",
       "Teaches Elemental Mastery, bending the elements to your will.",
       4, -3, 1, node_type="active",
       effects={"unlock_ability": "shaman_elemental_mastery_cast"},
       connected_to=["call_of_thunder"],
       source="WotLK row 4, kept - the ONLY unlock for "
              "shaman_elemental_mastery_cast, which is requires_talent. The "
              "real talent requires Call of Thunder, which connected_to "
              "reproduces. Its instant-cast clause lives in the ability "
              "rather than here, which is just as well given there are no "
              "cast times.")

T.node("elemental_oath", "Elemental Oath",
       "Increases your spell damage by 5% per rank.",
       4, -1, 2, effects={"spell_damage": 0.05},
       connected_to=["elemental_mastery"],
       source="WotLK row 4, NEW to our tree: 'While Clearcasting from "
              "Elemental Focus is active, you deal 5%/10% more spell "
              "damage. In addition, party and raid members gain 5% spell "
              "critical chance.' DEPARTURE on both clauses - nothing reads "
              "whether the ACTOR carries a specific buff as a condition on "
              "a damage modifier, and a talent effect can never reach an "
              "ally. Delivered unconditionally at the real 10%. The real "
              "talent requires Elemental Mastery, reproduced. spell_damage "
              "is a FRACTION.")

T.node("storm_earth_and_fire", "Storm, Earth and Fire",
       "Reduces the cooldown of your Chain Lightning by 1 turn and "
       "increases your Earthbind Totem's duration by 1 turn per rank.",
       4, 1, 3,
       effects={"ability_shaman_chain_lightning_cooldown": 1,
                "ability_shaman_earthbind_totem_duration": 1},
       connected_to=["booming_echoes"],
       source="WotLK row 4: 'Reduces the cooldown of your Chain Lightning "
              "spell by 0.5-2.5 sec, your Earthbind Totem also has a "
              "33%-100% chance to root targets, and increases the damage "
              "done by your Flame Shock.' Rooting does not exist (no "
              "movement to impair), so the Earthbind clause becomes "
              "duration instead. Flame Shock damage is Booming Echoes' job "
              "here. Kept from the outgoing tree, which was a flat "
              "scalar.")

T.node("lightning_overload", "Lightning Overload",
       "Your Lightning Bolt and Chain Lightning have an 11% chance per rank "
       "to strike again.",
       4, 3, 3,
       proc={"trigger": "on_damage_cast", "chance": 11, "icd": 0,
             "ability_filter": LIGHTNING,
             "damage_flat": 90, "school": "nature"},
       connected_to=["booming_echoes"],
       source="WotLK row 4, NEW to our tree: 'Gives your Lightning Bolt and "
              "Chain Lightning spells an 11%-33% chance to cast a second, "
              "similar spell on the same target at no additional cost.' "
              "Built as the real mechanic at the real chance curve, with "
              "the real ability_filter. Casting a copy of the triggering "
              "spell is not available as a payload - cast_ability names a "
              "FIXED ability, not 'the one that fired' - so it is flat "
              "Nature damage instead, which is what the second bolt would "
              "have delivered.")

# ----------------------------------------------------------------- tier 5
T.node("astral_shift", "Astral Shift",
       "While badly wounded, reduces all damage you take by 10% per rank.",
       5, -3, 3,
       effects={"low_health_damage_reduction_pct": 0.10},
       connected_to=["elemental_oath"],
       source="WotLK row 5, NEW to our tree: 'When stunned, feared or "
              "silenced you shift into the Astral Plane reducing all damage "
              "taken by 10%-30% for the duration of the effect.' DEPARTURE "
              "- nothing reads whether the ACTOR is currently stunned as a "
              "condition on a damage modifier, and there is no fear or "
              "silence. The engine's own 'in trouble' conditional stands "
              "in. low_health_damage_reduction_pct reads the ACTOR's health "
              "and defaults to a 50% threshold, so "
              "low_health_threshold_pct is NOT authored.")

T.node("totem_of_wrath", "Totem of Wrath",
       "Increases your spell power by 60.",
       5, -1, 1, effects={"spell_power": 60},
       connected_to=["elemental_oath"],
       source="WotLK row 5: 'Summons a Totem of Wrath with 5 health at the "
              "feet of the caster. The totem increases spell power by 100 "
              "for all party and raid members.' DEPARTURE - there is no "
              "Totem of Wrath ability to summon and a talent effect can "
              "never reach an ally. Delivered as spell power for the shaman "
              "at a reduced value, since it is now permanent and personal "
              "rather than a totem occupying a Fire slot. spell_power in a "
              "talent effect is FLAT.")

T.node("shamanism", "Shamanism",
       "Increases the damage of your Lightning Bolt, Chain Lightning and "
       "Lava Burst by 4% per rank.",
       5, 1, 5,
       effects={"ability_shaman_lightning_bolt_damage": 0.04,
                "ability_shaman_chain_lightning_damage": 0.04,
                "ability_shaman_lava_burst_damage": 0.04},
       connected_to=["lightning_overload"],
       source="WotLK row 5: 'Your Lightning Bolt and Chain Lightning spells "
              "gain an additional 4%-20% and your Lava Burst gains an "
              "additional 5%-25% of your bonus spell damage effects.' "
              "Spell-power coefficients are not exposed to talents, so it "
              "is delivered as direct damage at the real per-rank value. "
              "Stacks with Lightning Mastery, as the real pair does.")

T.node("lava_flows", "Lava Flows",
       "Increases the critical damage of your Lava Burst by 8% per rank.",
       5, 3, 3,
       effects={"ability_shaman_lava_burst_crit_damage": 0.08},
       connected_to=["lightning_overload"],
       source="WotLK row 5, NEW to our tree: 'Increases the critical strike "
              "damage bonus of your Lava Burst spell by an additional "
              "8%-24%, and when your Flame Shock is dispelled you gain "
              "haste.' The crit-damage half is built verbatim; there is no "
              "dispel trigger. ability_<id>_crit_damage is a FRACTION - and "
              "note the key's parse must try the LONGEST suffix first, or "
              "ability_X_crit_damage reads as ability 'X_crit' plus field "
              "'damage'.")

# ----------------------------------------------------------------- tier 6
T.node("thunderstorm", "Thunderstorm",
       "Teaches Thunderstorm, calling down lightning and refilling your "
       "mana.",
       6, -1, 1, node_type="active",
       effects={"unlock_ability": "shaman_thunderstorm"},
       connected_to=["shamanism"],
       source="WotLK row 10, the capstone, kept - the ONLY unlock for "
              "shaman_thunderstorm, which is requires_talent.")


def main():
    return T.write(was="23 nodes, 74 points - 7 proc, 9 ability-scoped, "
                       "6 flat stat, 1 unlock")


if __name__ == "__main__":
    sys.exit(main())
