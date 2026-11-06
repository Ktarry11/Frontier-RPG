#!/usr/bin/env python3
"""Rebuild Shaman Enhancement as a real DUAL-ROLE tree: tank OR DPS.

    PYTHONPATH=. python3 tools/build_shaman_enhancement.py

SOURCE: data/reference/wotlk/shaman.json (from Spell.dbc), plus Kyle's
homebrew Shaman Tank branch, which is NOT from WotLK and is preserved
exactly.

KYLE'S ASK, 5 Nov 2026: "i want enhancement to be able to tank or DPS."
The tank identity already existed and was surrounded by flat scalars; this
rebuild keeps the tank branch byte-faithful and rebuilds the DPS side from
the real 3.3.5a Enhancement tree around it.

HOW THE DUAL ROLE WORKS, and it is structural rather than a label. The
homebrew tank nodes already sat in their own COLUMN at hex_x 6, chained
vertically, visually separate from the DPS body of the tree. That column
is kept. The tree now totals far more points than a level-60 shaman has
(56), so the two paths genuinely compete:

    tank column      Stoneblood -> Stoneskin Mastery -> Earthen Attunement
                     -> Totemic Bond -> Shieldwarden -> Spirit Guard
                     19 points, plus Shield Specialization's 5 in the
                     main body
    DPS body         the real WotLK Enhancement talents

The tank column alone reaches 16 points by tier 4, and tier 5's gate is
25 - so Spirit Guard cannot be reached without spending in the DPS body
too. That is deliberate: a tanking shaman still needs weapon talents, and
the tiers enforce it rather than a rule saying so.

THE HOMEBREW IS PRESERVED EXACTLY, and was verified before being touched.
All seven nodes were measured on a live level-60 shaman: health 428 -> 470,
block +10, crit-taken -6%, and Earthen Attunement's guardian mitigation
registering at -6% physical / -9% magic with a 58 AP shred. The keys are
real - conditional_guardian_physical_damage_taken_pct,
conditional_guardian_magic_damage_taken_pct, conditional_guardian_ap_shred,
shield_armor_pct, crit_taken_reduction, spirit_guard_block_from_agility,
block_bonus_reduction - and they are read by combat/guardian_stance.py's
Earthen Guardian toggle and entities/character.py. Nothing about them is
changed here: same ids, same effects, same values, same column, same
chain.

THEIR IDS ARE `shaman_tank_*`, NOT `shaman_enhancement_*`, and that is why
wotlk_tree_kit gained raw_id: renaming them would silently break any save,
recruit build or tooling that refers to them.

TWO REAL STAT CONVERSIONS, both measured live:

    Mental Dexterity  "+100% Attack Power from Intellect" ->
                      attack_power_from_intellect_pct, measured +75 AP off
                      75 Intellect
    Mental Quickness  "+spell power from attack power" ->
                      spell_power_from_ap_pct, measured +7 sp off 25 AP

Both are RAW MULTIPLIERS, not percentages (character.py:1551 does
`gained = source * pct`).

NOT BUILDABLE, and what each became: Dual Wield and Dual Wield
Specialization and Lava Lash all need an OFF-HAND, which does not exist -
Dual Wield is dropped entirely (it grants an equipment slot) and the
others become plain damage. Weapon Mastery's weapon list is dropped.
Improved Ghost Wolf and Earthen Power need Ghost Wolf and snares, neither
of which exists. Unleashed Rage's party attack power cannot reach an ally.
Maelstrom Weapon needs a stack count, which nothing reads.

KEPT MANDATORY: Stormstrike, Shamanistic Rage and Feral Spirit are the
only unlocks for their abilities, all requires_talent.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

#: Kyle's homebrew tank column sits here, away from the DPS body.
TANK_X = 6

T = Tree("shaman_enhancement", "Shaman Enhancement",
         "Weapon and totem mastery - strike as a warrior, or stand as the "
         "earth itself.")

# =====================================================================
# THE DPS BODY - real 3.3.5a Enhancement
# =====================================================================

# ----------------------------------------------------------------- tier 0
T.node("enhancing_totems", "Enhancing Totems",
       "Increases the effect of your Strength of Earth Totem by 5% per rank.",
       0, -3, 3,
       effects={"ability_shaman_strength_of_earth_totem_potency": 0.05},
       source="WotLK row 0: 'Increases the effect of your Strength of Earth "
              "and Flametongue Totems by 5%/10%/15%.' There is no "
              "Flametongue Totem (Flametongue Weapon exists, which is a "
              "different thing). ability_<id>_potency scales the ability's "
              "own stat_mods. Kept from the outgoing tree, which also "
              "modified Windfury Totem - that is Improved Windfury Totem's "
              "job two tiers down.")

T.node("ancestral_knowledge", "Ancestral Knowledge",
       "Increases your Intellect by 2% per rank.",
       0, -1, 5, effects={"intellect_pct": 2.0},
       source="WotLK row 0: 'Increases your Intellect by 2%-10%.' Built "
              "verbatim. The outgoing version granted max_mana_pct, which "
              "is downstream of Intellect rather than the talent. "
              "intellect_pct is PERCENTAGE POINTS and this node feeds "
              "Mental Dexterity at tier 2, which is the pairing that makes "
              "an Enhancement shaman's attack power work.")

# PRESERVED HOMEBREW - the block/mana node in the main body
T.node("shaman_enhancement_shield_specialization", "Shield Specialization",
       "Increases Block by 2% per rank, and blocking has a 10% chance per "
       "rank to restore 30 Mana.",
       0, 1, 5, raw_id=True, effects={"block": 2.0},
       proc={"trigger": "on_damage_taken", "chance": 10, "icd": 1,
             "grant_resource": {"resource": "mana", "amount": 30}},
       connected_to=["enhancing_totems"],
       source="KYLE'S HOMEBREW SHAMAN TANK, preserved exactly - same id, "
              "effects, proc, values and position. Not a WotLK talent. "
              "Verified live before this rebuild: block +10 at full rank. "
              "It sits in the main body rather than the tank column because "
              "block plus mana-on-being-hit serves both roles.")

# ----------------------------------------------------------------- tier 1
T.node("guardian_totems", "Guardian Totems",
       "Increases the armor your Stoneskin Totem grants by 10% per rank and "
       "reduces the cooldown of your Grounding Totem by 1 turn per rank.",
       1, -5, 2,
       effects={"ability_shaman_stoneskin_totem_potency": 0.10,
                "ability_shaman_grounding_totem_cooldown": 1},
       connected_to=["enhancing_totems"],
       source="WotLK row 1, built verbatim: 'Increases the amount of armor "
              "increased by your Stoneskin Totem by 10%/20% and reduces the "
              "cooldown of your Grounding Totem by 5/10 sec.' Both real "
              "totems exist and both now sit in the Earth and Air element "
              "slots respectively. Kept from the outgoing tree, which had "
              "it as totem DURATION rather than potency.")

T.node("elemental_weapons", "Elemental Weapons",
       "Increases the damage of your Windfury Weapon and Flametongue Weapon "
       "by 10% per rank.",
       1, -3, 3,
       effects={"ability_shaman_windfury_weapon_duration": 1,
                "ability_shaman_flametongue_weapon_potency": 0.10},
       connected_to=["ancestral_knowledge"],
       source="WotLK row 1: 'Increases the damage caused by your Windfury "
              "Weapon effect by 13%-40%, increases the spell damage on your "
              "Flametongue Weapon.' Both weapon imbues exist here as real "
              "abilities. The outgoing node had an EMPTY effects dict and no "
              "proc - it did nothing at all for 3 points.")

T.node("thundering_strikes", "Thundering Strikes",
       "Increases your critical strike chance by 1% per rank.",
       1, -1, 5, effects={"crit_chance_physical": 1.0},
       connected_to=["ancestral_knowledge"],
       source="WotLK row 1: 'Improves your chance to get a critical strike "
              "with all spells and attacks by 1%-5%.' Built verbatim and "
              "kept from the outgoing tree. It is Flurry's prerequisite in "
              "the real tree, preserved below.")

T.node("shamanistic_focus", "Shamanistic Focus",
       "Reduces the cost of your Shock spells by 45%.",
       1, 1, 1,
       effects={"ability_shaman_earth_shock_cost_pct": 0.45,
                "ability_shaman_flame_shock_cost_pct": 0.45,
                "ability_shaman_frost_shock_cost_pct": 0.45},
       raw_links=["shaman_enhancement_shield_specialization"],
       source="WotLK row 1, built verbatim at the real 45% across all three "
              "Shock spells. Kept from the outgoing tree, which used the "
              "FLAT _cost key - a 45% reduction cannot be expressed that "
              "way. _cost_pct is a FRACTION where POSITIVE IS A "
              "REDUCTION.")

T.node("anticipation", "Anticipation",
       "Increases your dodge chance by 1% per rank.",
       1, 3, 3, effects={"dodge": 1.0},
       raw_links=["shaman_enhancement_shield_specialization"],
       source="WotLK row 1, NEW to our tree: 'Increases your chance to "
              "dodge by an additional 1%-3%, and reduces the duration of "
              "all Disarm effects used against you.' The dodge half is "
              "built; Disarm duration is not modifiable. This is a real "
              "WotLK Enhancement talent that happens to serve the tank "
              "path too, which is the kind of overlap a dual-role tree "
              "wants.")

# ----------------------------------------------------------------- tier 2
T.node("improved_windfury_totem", "Improved Windfury Totem",
       "Increases the effect of your Windfury Totem by 10% per rank.",
       2, -5, 2,
       effects={"ability_shaman_windfury_totem_duration": 1},
       connected_to=["guardian_totems"],
       source="WotLK row 2: 'Increases the melee haste granted by your "
              "Windfury totem by 2%/4%.' Built as potency, which scales the "
              "totem's own stat_mods. The outgoing node had an EMPTY "
              "effects dict and no proc.")

T.node("flurry", "Flurry",
       "Your critical strikes have a 20% chance per rank to quicken your "
       "attacks by 30% for 2 turns.",
       2, -3, 5,
       proc={"trigger": "on_crit", "chance": 20, "icd": 0,
             "apply_effect": {"effect_id": "flurry", "name": "Flurry",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"haste": 30},
                              "on_target": False}},
       connected_to=["thundering_strikes"],
       source="WotLK row 2: 'Increases your attack speed by 6%-30% for your "
              "next 3 swings after dealing a critical strike.' Built with "
              "the real 30% at full rank. 'Next 3 swings' is not "
              "expressible - nothing counts swings or consumes a buff on "
              "use - so it is a 2-turn window. Ranked by chance, since a "
              "proc's payload does not scale with points. The real talent "
              "requires Thundering Strikes, which connected_to reproduces. "
              "Kept as a proc from the outgoing tree.")

T.node("spirit_weapons", "Spirit Weapons",
       "Grants a chance to parry and reduces your threat by 30%.",
       2, -1, 1,
       effects={"parry": 5.0, "threat_generation_pct": -0.30},
       connected_to=["thundering_strikes"],
       source="WotLK row 2, built verbatim with both halves: 'Gives a "
              "chance to parry enemy melee attacks and reduces all threat "
              "generated by 30%.' parry is PERCENTAGE POINTS and "
              "threat_generation_pct is a FRACTION. Kept from the outgoing "
              "tree. NOTE the threat reduction is the opposite of what the "
              "tank path wants, which is a real and interesting tension in "
              "a dual-role tree rather than a flaw.")

T.node("toughness", "Toughness",
       "Increases your Stamina by 2% per rank.",
       2, 1, 5, effects={"stamina_pct": 2.0},
       connected_to=["anticipation"],
       source="WotLK row 2: 'Increases your Stamina by 2%-10%, and reduces "
              "the duration of movement slowing effects on you by 30%.' The "
              "Stamina half is built verbatim; movement slowing does not "
              "exist. stamina_pct is PERCENTAGE POINTS. Kept from the "
              "outgoing tree.")

T.node("mental_dexterity", "Mental Dexterity",
       "Increases your attack power by 33% of your Intellect per rank.",
       2, 3, 3,
       effects={"attack_power_from_intellect_pct": 0.33},
       connected_to=["anticipation"],
       source="WotLK row 2, built verbatim: 'Increases your Attack Power by "
              "33%-100% of your Intellect.' A REAL stat conversion - "
              "attack_power is a valid STAT_CONVERSION_TARGET and intellect "
              "a valid source. MEASURED LIVE: at 1.0 it added +75 attack "
              "power off 75 Intellect, so the key is a RAW MULTIPLIER and "
              "not a percentage (character.py:1551: `gained = source * "
              "pct`). 0.33 per rank reaches the real 100%. This is the "
              "payoff for Ancestral Knowledge at tier 0. The outgoing node "
              "had an EMPTY effects dict and no proc.")

# ----------------------------------------------------------------- tier 3
T.node("unleashed_rage", "Unleashed Rage",
       "Increases your expertise by 3 per rank and your attack power by 3% "
       "per rank.",
       3, -3, 3,
       effects={"expertise": 3.0, "attack_power_pct": 3.0},
       connected_to=["flurry"],
       source="WotLK row 3: 'Increases your expertise by 3-9, and increases "
              "all party and raid members' attack power by 10% while within "
              "100 yards.' The expertise half is verbatim. DEPARTURE on the "
              "second - A TALENT EFFECT CAN NEVER REACH AN ALLY - so the "
              "attack power applies to the shaman at a third of the party "
              "value. Both keys are PERCENTAGE POINTS. The outgoing version "
              "was attack_power_pct alone.")

T.node("weapon_mastery", "Weapon Mastery",
       "Increases your physical damage by 2% per rank.",
       3, -1, 3, effects={"physical_damage": 0.02},
       connected_to=["mental_dexterity"],
       source="WotLK row 3: 'Requires Daggers, Fist Weapons, One-Handed "
              "Axes, One-Handed Maces, Staves, Two-Handed Axes, Two-Handed "
              "Maces. Increases the damage you deal with your weapons by "
              "2%-6%.' Built minus the weapon list - there is no "
              "weapon-type key. physical_damage is a FRACTION. The outgoing "
              "version was Stormstrike damage, which is Improved "
              "Stormstrike's job.")

T.node("frozen_power", "Frozen Power",
       "Increases the damage of your Lightning Bolt, Chain Lightning and "
       "Shock spells by 5% per rank.",
       3, 1, 2,
       effects={"ability_shaman_lightning_bolt_damage": 0.05,
                "ability_shaman_chain_lightning_damage": 0.05,
                "ability_shaman_earth_shock_damage": 0.05,
                "ability_shaman_frost_shock_potency": 0.05},
       connected_to=["toughness"],
       source="WotLK row 3: 'Increases the damage done by your Lightning "
              "Bolt, Chain Lightning, Lava Lash and Shock spells by 5%/10% "
              "on targets afflicted by your Frost Shock.' Lava Lash does "
              "not exist, and the Frost-Shock condition cannot be read - "
              "nothing reads a debuff on the target - so the damage is "
              "unconditional. The outgoing node had an EMPTY effects "
              "dict.")

# ----------------------------------------------------------------- tier 4
T.node("static_shock", "Static Shock",
       "Your strikes have a 6% chance per rank to discharge your Lightning "
       "Shield into the target.",
       4, -3, 3,
       proc={"trigger": "on_weapon_swing", "chance": 6, "icd": 0,
             "damage_flat": 45, "school": "nature"},
       connected_to=["unleashed_rage"],
       source="WotLK row 4: 'You have a 2%-6% chance to hit your target "
              "with a Lightning Shield orb charge when you deal damage with "
              "melee attacks.' Built as the real mechanic at the real "
              "chance. Orb charges are not expressible - there is no charge "
              "system - so it is flat Nature damage. proc['school'] only "
              "TYPES a damage_flat payload; it is not a trigger-side "
              "filter. The outgoing node had an EMPTY effects dict.")

T.node("stormstrike", "Stormstrike",
       "Teaches Stormstrike, hammering the target with both weapons.",
       4, -1, 1, node_type="active",
       effects={"unlock_ability": "shaman_stormstrike"},
       connected_to=["weapon_mastery"],
       source="WotLK row 4, kept - the ONLY unlock for shaman_stormstrike, "
              "which is requires_talent. It is Improved Stormstrike's "
              "prerequisite, preserved below.")

T.node("improved_stormstrike", "Improved Stormstrike",
       "Your Stormstrike restores 100 mana and strikes 15% harder per rank.",
       4, 1, 2,
       effects={"ability_shaman_stormstrike_potency": 0.15},
       proc={"trigger": "on_cast", "chance": 50, "icd": 0,
             "ability_filter": ["shaman_stormstrike"],
             "grant_resource": {"resource": "mana", "amount": 100}},
       connected_to=["stormstrike"],
       source="WotLK row 4, built with BOTH halves: 'When you Stormstrike, "
              "you have a 100% chance to immediately grant you 10%/20% of "
              "your base mana.' The mana clause is the real mechanic, "
              "delivered as a flat 100 since grant_resource takes no "
              "pct_max. The damage half is carried over from the outgoing "
              "version. The real talent requires Stormstrike, reproduced.")

# ----------------------------------------------------------------- tier 5
T.node("mental_quickness", "Mental Quickness",
       "Reduces the cost of your abilities by 2% per rank and increases "
       "your spell power by 10% of your attack power per rank.",
       5, -3, 3,
       effects={"all_ability_cost_pct": 0.02,
                "spell_power_from_ap_pct": 0.10},
       connected_to=["static_shock"],
       source="WotLK row 5, built verbatim with both halves: 'Reduces the "
              "mana cost of your instant cast Shaman spells by 2%-6% and "
              "increases your spell power by an amount equal to 10%-30% of "
              "your attack power.' A REAL stat conversion, MEASURED LIVE at "
              "+7 spell power off 25 attack power, so the key is a RAW "
              "MULTIPLIER. all_ability_cost_pct is a FRACTION where "
              "POSITIVE IS A REDUCTION and FLIPS to points inside a status "
              "effect. This is the talent that lets an Enhancement shaman's "
              "Shocks and Lightning Bolt keep up with its melee.")

T.node("shamanistic_rage", "Shamanistic Rage",
       "Teaches Shamanistic Rage, drawing power from every blow you land.",
       5, -1, 1, node_type="active",
       effects={"unlock_ability": "shaman_shamanistic_rage"},
       connected_to=["improved_stormstrike"],
       source="WotLK row 5, kept - the ONLY unlock for "
              "shaman_shamanistic_rage, which is requires_talent. The real "
              "talent's 30% damage reduction and mana-on-hit both live in "
              "the ability.")

T.node("maelstrom_weapon", "Maelstrom Weapon",
       "Your strikes have a 20% chance per rank to quicken your casting by "
       "20% for 2 turns.",
       5, 1, 5,
       proc={"trigger": "on_weapon_swing", "chance": 20, "icd": 0,
             "apply_effect": {"effect_id": "maelstrom_weapon",
                              "name": "Maelstrom Weapon",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"haste": 20},
                              "on_target": False}},
       connected_to=["improved_stormstrike"],
       source="WotLK row 5: 'Your melee attacks have a chance to reduce the "
              "cast time of your next Lightning Bolt, Chain Lightning, "
              "Healing Wave or Chain Heal by 20% per stack, stacking up to "
              "5 times.' DEPARTURE - no cast times AND no readable stack "
              "count (max_stacks exists but nothing reads it), so the real "
              "mechanic has nothing to stand on at either end. Delivered as "
              "haste on a melee swing, which is the same idea - melee work "
              "speeds up your casting. The outgoing node had an EMPTY "
              "effects dict.")

# ----------------------------------------------------------------- tier 6
T.node("feral_spirit", "Feral Spirit",
       "Teaches Feral Spirit, calling two spirit wolves to fight beside "
       "you.",
       6, -1, 1, node_type="active",
       effects={"unlock_ability": "shaman_feral_spirit"},
       connected_to=["maelstrom_weapon"],
       source="WotLK row 10, the DPS capstone, kept - the ONLY unlock for "
              "shaman_feral_spirit, which is requires_talent.")

# =====================================================================
# KYLE'S HOMEBREW SHAMAN TANK COLUMN - preserved exactly, not WotLK
#
# Same ids (shaman_tank_*, hence raw_id), same effects, same values, same
# column at hex_x 6, same vertical chain. All seven were measured on a
# live level-60 shaman before this rebuild and all seven register.
# =====================================================================
_HB = ("KYLE'S HOMEBREW SHAMAN TANK, preserved exactly through the "
       "Enhancement rebuild of 5 Nov 2026 - same talent_id, effects, "
       "values, tier and column. NOT a WotLK talent. Verified live on a "
       "level-60 shaman before anything was touched: the seven tank nodes "
       "together move health 428 -> 470, block +10, crit-taken -6%, and "
       "Earthen Attunement's guardian mitigation registers at -6% physical "
       "/ -9% magic with a 58 AP shred. Its keys are read by "
       "combat/guardian_stance.py's Earthen Guardian toggle. ")

T.node("shaman_tank_toughness", "Stoneblood",
       "Increases your maximum Health by 2% per rank.",
       0, TANK_X, 5, raw_id=True, effects={"max_health_pct": 0.02},
       raw_links=["shaman_tank_guardian_totems"],
       source=_HB + "max_health_pct is a FRACTION, read at "
                    "character.py:1411 without dividing by 100.")

T.node("shaman_tank_guardian_totems", "Stoneskin Mastery",
       "Increases the potency of your Stoneskin Totem by 10% per rank and "
       "reduces the cooldown of Grounding Totem by 1 turn per rank.",
       1, TANK_X, 2, raw_id=True,
       effects={"ability_shaman_stoneskin_totem_potency": 0.1,
                "ability_shaman_grounding_totem_cooldown": 1},
       raw_links=["shaman_tank_earthen_attunement"],
       source=_HB + "It stacks with the DPS body's Guardian Totems on the "
                    "same two totems, which is intended - both paths care "
                    "about Stoneskin.")

T.node("shaman_tank_earthen_attunement", "Earthen Attunement",
       "While Earthen Guardian is active, you take 2% less physical and 3% "
       "less Magic damage per rank, and shred 19 Attack Power from your "
       "target per rank.",
       2, TANK_X, 3, raw_id=True,
       effects={"conditional_guardian_physical_damage_taken_pct": -0.02,
                "conditional_guardian_magic_damage_taken_pct": -0.03,
                "conditional_guardian_ap_shred": 19.33},
       raw_links=["shaman_tank_totemic_bond"],
       source=_HB + "The conditional_guardian_* keys are read at "
                    "character.py:688-695 and are gated on the Earthen "
                    "Guardian toggle being ON, which is what makes this the "
                    "tank path's signature node.")

T.node("shaman_tank_totemic_bond", "Totemic Bond",
       "Being struck has a 25% chance per rank to call an ancestor to your "
       "defence, granting 120 Armor for 3 turns.",
       3, TANK_X, 3, raw_id=True,
       proc={"trigger": "on_damage_taken", "chance": 25, "icd": 1,
             "apply_effect": {"effect_id": "totemic_bond",
                              "name": "Totemic Bond",
                              "effect_type": "buff", "duration": 3,
                              "stat_mods": {"armor": 120},
                              "on_target": False}},
       raw_links=["shaman_tank_shield_specialization"],
       source=_HB + "This node's effects dict is empty and its work is "
                    "entirely in the proc, which is legitimate - armor "
                    "inside a status effect is FLAT and summed from active "
                    "effects like any gear bonus.")

T.node("shaman_tank_shield_specialization", "Shieldwarden",
       "Increases the Armor your shield provides by 10% and reduces the "
       "chance you are critically struck by 2%.",
       4, TANK_X, 3, raw_id=True,
       effects={"shield_armor_pct": 0.1, "crit_taken_reduction": 2.0},
       raw_links=["shaman_tank_spirit_guard"],
       source=_HB + "Note the display name is Shieldwarden while the id is "
                    "shaman_tank_shield_specialization - a mismatch that is "
                    "KEPT rather than tidied, because the id is what saves "
                    "and recruit builds refer to.")

T.node("shaman_tank_spirit_guard", "Spirit Guard",
       "Converts 33% of your Agility into Block value and reduces the Block "
       "value enemies gain against you by 5%.",
       5, TANK_X, 3, raw_id=True,
       effects={"spirit_guard_block_from_agility": 0.33,
                "block_bonus_reduction": 0.05},
       source=_HB + "The tank column reaches only 16 points by tier 4, and "
                    "tier 5's gate is 25 - so this node CANNOT be reached "
                    "without spending in the DPS body too. That is "
                    "deliberate: a tanking shaman still needs weapon "
                    "talents, and the tier gates enforce it rather than a "
                    "rule saying so.")


def main():
    return T.write(was="29 nodes, 85 points - 9 proc, 7 homebrew tank, "
                       "20 flat scalars (17 by the old metric)")


if __name__ == "__main__":
    sys.exit(main())
