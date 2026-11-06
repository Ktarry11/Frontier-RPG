#!/usr/bin/env python3
"""Rebuild Shaman Restoration from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_shaman_restoration.py

SOURCE: data/reference/wotlk/shaman.json (from Spell.dbc).
Worksheet: data/reference/wotlk_worksheets/shaman.md.

ROLE: healer. Healing Wave and Riptide, Earth Shield on the tank, and the
Water totems keeping everyone's mana up.

SIX MANDATORY UNLOCKS - the most of any tree in the project, now that
Mana Tide Totem is gated here as well: shaman_natures_swiftness,
shaman_riptide, shaman_mana_tide_totem, shaman_earth_shield,
shaman_cleanse_spirit and shaman_call_of_ancestors are all
requires_talent and all unlocked only from this tree. Dropping any node
would strand an ability (qa_abilities_obtainable).

MANA TIDE TOTEM IS A REAL TALENT HERE AND IN WotLK (row 8), which the
totem pass earlier in this session flagged: ours was trainer-learned AND
target_type "self", so a Restoration shaman's signature mana cooldown
refilled only its own bar. The target is fixed and the talent gate is
real.

THE WATER ELEMENT SLOT NOW MATTERS. Mana Spring, Mana Tide and Fire
Resistance Totem all occupy it one at a time after the totem fix, so
Restorative Totems points at a real choice rather than two of thirteen
totems a shaman could all have up.

CAST TIMES, ONE LAST TIME: Improved Healing Wave, Healing Focus, Nature's
Swiftness's instant-cast clause, Tidal Waves and Earth Shield's
channel-protection clause are all written on a system that does not
exist. Each pays out as throughput, cost or crit.

ABILITIES THE REAL TREE WANTS AND WE LACK: Chain Heal, Lesser Healing
Wave, Healing Stream Totem, Reincarnation's talent target, Earthliving
Weapon. Improved Chain Heal and Improved Reincarnation are DROPPED.

UNIT CONVENTIONS: crit_chance_spell is PERCENTAGE POINTS;
healing_done / healing_taken_pct / threat_generation_pct /
stun_duration_reduction_pct / low_health_healing_pct are FRACTIONS;
*_from_*_pct is a FRACTION read as a raw multiplier of the source stat;
ability_<id>_healing is a FRACTION and is the key EVERY heal node here
uses - _damage on a heal is the mistake that left 18 talents dead across
four classes.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

#: Every totem, for Totemic Focus's cost reduction.
TOTEMS = ["shaman_strength_of_earth_totem", "shaman_stoneclaw_totem",
          "shaman_stoneskin_totem", "shaman_earthbind_totem",
          "shaman_searing_totem", "shaman_magma_totem",
          "shaman_frost_resistance_totem", "shaman_mana_spring_totem",
          "shaman_mana_tide_totem", "shaman_fire_resistance_totem",
          "shaman_windfury_totem", "shaman_grounding_totem",
          "shaman_nature_resistance_totem"]

T = Tree("shaman_restoration", "Shaman Restoration",
         "The healing tide - restoration, shields and the totems that "
         "sustain a party.")

# ----------------------------------------------------------------- tier 0
T.node("improved_healing_wave", "Improved Healing Wave",
       "Increases the healing of your Healing Wave by 3% per rank.",
       0, -1, 5,
       effects={"ability_shaman_healing_wave_healing": 0.03},
       source="WotLK row 0: 'Reduces the casting time of your Healing Wave "
              "spell by 0.1-0.5 sec.' DEPARTURE - there are no cast times. "
              "A shorter cast is more throughput, so it is delivered as "
              "healing. USES _healing, not _damage - the key that left 18 "
              "talents silently dead across four classes.")

T.node("totemic_focus", "Totemic Focus",
       "Reduces the mana cost of your totems by 5% per rank.",
       0, 1, 5,
       effects={f"ability_{t}_cost_pct": 0.05 for t in TOTEMS},
       source="WotLK row 0, built verbatim across all thirteen totems: "
              "'Reduces the mana cost of your totems by 5%-25%.' _cost_pct "
              "is a FRACTION where POSITIVE IS A REDUCTION. Kept from the "
              "outgoing tree, which covered three totems with the FLAT "
              "_cost key.")

# ----------------------------------------------------------------- tier 1
T.node("improved_water_shield", "Improved Water Shield",
       "Your critical heals restore 120 mana.",
       1, -5, 3,
       proc={"trigger": "on_crit", "chance": 33, "icd": 0,
             "grant_resource": {"resource": "mana", "amount": 120}},
       connected_to=["improved_healing_wave"],
       source="WotLK row 1, NEW to our tree: 'You have a 33%-100% chance to "
              "instantly gain mana as if you consumed a Water Shield Orb "
              "when you gain a critical effect from your healing spells.' "
              "Built on the real trigger with the real chance curve. Orb "
              "consumption is not expressible - there is no charge system - "
              "so grant_resource delivers a flat 120, since it takes no "
              "pct_max.")

T.node("healing_grace", "Healing Grace",
       "Reduces the threat your healing generates by 5% per rank.",
       1, -3, 3, effects={"threat_generation_pct": -0.05},
       connected_to=["improved_healing_wave"],
       source="WotLK row 1, NEW to our tree: 'Reduces the threat generated "
              "by your healing spells by 5%/10%/15% and reduces the chance "
              "your helpful spells and damage over time effects will be "
              "dispelled.' The threat half is built - there is no "
              "heal-specific threat key, only the global "
              "threat_generation_pct, which is a FRACTION. Dispel "
              "resistance does not exist.")

T.node("tidal_focus", "Tidal Focus",
       "Reduces the cost of your healing spells by 2% per rank.",
       1, -1, 5,
       effects={"ability_shaman_healing_wave_cost_pct": 0.02,
                "ability_shaman_riptide_cost_pct": 0.02,
                "ability_shaman_earth_shield_cost_pct": 0.02},
       connected_to=["totemic_focus"],
       source="WotLK row 1, built verbatim for the three real heals that "
              "exist: 'Reduces the mana cost of your healing spells by "
              "1%-5%.' Chain Heal and Lesser Healing Wave do not exist "
              "here.")

T.node("tidal_force", "Tidal Force",
       "Increases the critical chance of your Healing Wave and Riptide by "
       "15%.",
       1, 1, 1,
       effects={"ability_shaman_healing_wave_crit": 15.0,
                "ability_shaman_riptide_crit": 15.0},
       connected_to=["totemic_focus"],
       source="WotLK row 1: 'Increases the critical effect chance of your "
              "Healing Wave, Lesser Healing Wave and Chain Heal by 60%. "
              "Each critical heal reduces the bonus by 20%.' DEPARTURE - "
              "there is no ability to unlock and nothing decrements a buff "
              "on use, so the real talent's spend-down cannot be modelled. "
              "Delivered as a permanent but far smaller crit bonus on the "
              "two real heals. ability_<id>_crit is PERCENTAGE POINTS.")

T.node("ancestral_healing", "Ancestral Healing",
       "Your critical heals harden you against physical damage for 4 turns.",
       1, 3, 3,
       proc={"trigger": "on_crit", "chance": 33, "icd": 0,
             "apply_effect": {"effect_id": "ancestral_healing",
                              "name": "Ancestral Healing",
                              "effect_type": "buff", "duration": 4,
                              "stat_mods": {"physical_damage_taken_pct": -10.0},
                              "on_target": False}},
       connected_to=["tidal_force"],
       source="WotLK row 1, NEW to our tree: 'Reduces your target's "
              "physical damage taken by 3%-10% for 15 sec after getting a "
              "critical effect from one of your healing spells.' Built with "
              "the real 10% and the real 15 seconds (4 turns). on_target is "
              "False because a talent-sourced effect cannot be aimed at the "
              "heal's recipient, so the shaman carries it - a real "
              "departure. Inside a status effect "
              "physical_damage_taken_pct is PERCENTAGE POINTS, unlike the "
              "BARE damage_taken_pct in the same position, which is read "
              "raw.")

# ----------------------------------------------------------------- tier 2
T.node("healing_way", "Healing Way",
       "Increases the healing of your Healing Wave by 8% per rank.",
       2, -5, 3,
       effects={"ability_shaman_healing_wave_healing": 0.08},
       connected_to=["improved_water_shield"],
       source="WotLK row 2, built verbatim: 'Increases the amount healed by "
              "your Healing Wave spell by 8%-25%.' Stacks with Improved "
              "Healing Wave at tier 0, as the real pair does.")

T.node("restorative_totems", "Restorative Totems",
       "Increases the effect of your Mana Spring and Mana Tide Totems by 7% "
       "per rank.",
       2, -3, 3,
       effects={"ability_shaman_mana_spring_totem_potency": 0.07,
                "ability_shaman_mana_tide_totem_potency": 0.07},
       connected_to=["healing_grace"],
       source="WotLK row 2: 'Increases the effect of your Mana Spring Totem "
              "by 7%/13%/20%, and increases the amount healed by your "
              "Healing Stream Totem.' Healing Stream Totem does not exist; "
              "Mana Tide stands in as the other Water totem. BOTH now "
              "occupy the Water element slot one at a time after the totem "
              "fix, so this talent points at a real choice. It is Mana Tide "
              "Totem's prerequisite in the real tree, preserved below.")

T.node("tidal_mastery", "Tidal Mastery",
       "Increases your spell critical chance by 1% per rank.",
       2, -1, 5, effects={"crit_chance_spell": 1.0},
       connected_to=["tidal_focus"],
       source="WotLK row 2, built verbatim: 'Increases the critical effect "
              "chance of your healing and lightning spells by 1%-5%.' "
              "crit_chance_spell covers all spells rather than those two "
              "groups; there is no way to scope crit to a spell set. "
              "PERCENTAGE POINTS.")

T.node("nature_swiftness", "Nature's Swiftness",
       "Teaches Nature's Swiftness, calling the elements instantly to your "
       "aid.",
       2, 1, 1, node_type="active",
       effects={"unlock_ability": "shaman_natures_swiftness"},
       connected_to=["tidal_force"],
       source="WotLK row 2, kept - the ONLY unlock for "
              "shaman_natures_swiftness, which is requires_talent. Its "
              "instant-cast clause lives in the ability, which is just as "
              "well given there are no cast times for a talent to shorten.")

T.node("focused_mind", "Focused Mind",
       "Reduces the duration of Stun effects against you by 10% per rank.",
       2, 3, 3,
       effects={"stun_duration_reduction_pct": 0.10},
       connected_to=["ancestral_healing"],
       source="WotLK row 2, NEW to our tree: 'Reduces the duration of any "
              "Silence or Interrupt effects used against the Shaman by "
              "10%/20%/30%.' DEPARTURE - there is no silence and no "
              "interrupt key; is_stun is this engine's only incapacitate. "
              "stun_duration_reduction_pct is a FRACTION and floors a stun "
              "at 1 turn.")

# ----------------------------------------------------------------- tier 3
T.node("purification", "Purification",
       "Increases all your healing by 2% per rank.",
       3, -1, 5, effects={"healing_done": 0.02},
       connected_to=["tidal_mastery"],
       source="WotLK row 3, built verbatim: 'Increases the effectiveness of "
              "your healing spells by 2%-10%.' healing_done is a FRACTION "
              "and is the global healing multiplier. It is Cleanse Spirit's "
              "prerequisite in the real tree, preserved below.")

# ----------------------------------------------------------------- tier 4
T.node("natures_guardian", "Nature's Guardian",
       "While badly wounded, increases healing you receive by 6% per rank "
       "and reduces damage taken by 3% per rank.",
       4, -5, 5,
       effects={"low_health_healing_pct": 0.06,
                "low_health_damage_reduction_pct": 0.03},
       connected_to=["healing_way"],
       source="WotLK row 4: 'Whenever a damaging attack brings you below "
              "30% health, your maximum health is increased by 15% for 10 "
              "sec and your threat is reduced.' DEPARTURE on the mechanism "
              "- there is no trigger for CROSSING a health threshold, and "
              "temporary maximum health that is then removed is not "
              "expressible either. Both of the engine's actor-side "
              "low-health conditionals stand in, which fire while you are "
              "hurt rather than at the moment you become hurt. Both share "
              "low_health_threshold_pct's default of 0.5, which is why it "
              "is NOT authored.")

T.node("blessing_of_the_eternals", "Blessing of the Eternals",
       "Increases your spell critical chance by 2% per rank.",
       4, -3, 2, effects={"crit_chance_spell": 2.0},
       connected_to=["restorative_totems"],
       source="WotLK row 4, NEW to our tree: 'Increases the critical effect "
              "chance of your spells by 2%/4%, and increases the chance to "
              "apply the Earthliving heal effect.' Earthliving Weapon does "
              "not exist. The crit half is built verbatim.")

T.node("mana_tide_totem", "Mana Tide Totem",
       "Teaches Mana Tide Totem, restoring mana to your whole party.",
       4, -1, 1, node_type="active",
       effects={"unlock_ability": "shaman_mana_tide_totem"},
       connected_to=["restorative_totems"],
       source="WotLK row 4, kept - the ONLY unlock for "
              "shaman_mana_tide_totem, which is requires_talent. The real "
              "talent requires Restorative Totems, which connected_to "
              "reproduces. NOTE this ability was fixed earlier in the same "
              "session: it was target_type 'self', so a Restoration "
              "shaman's signature mana cooldown refilled only its own bar, "
              "against a real spell that restores mana 'to group members "
              "within 30 yards'. It is now party-targeted and sits in the "
              "Water element slot.")

T.node("natures_blessing", "Nature's Blessing",
       "Increases your healing power by 5% of your Intellect per rank.",
       4, 1, 3,
       effects={"healing_power_from_intellect_pct": 0.05},
       connected_to=["purification"],
       source="WotLK row 4, NEW to our tree, built verbatim: 'Increases "
              "your healing by an amount equal to 5%-15% of your "
              "Intellect.' A REAL stat conversion - healing_power is a "
              "valid STAT_CONVERSION_TARGET and intellect a valid source. "
              "THE UNIT IS A RAW MULTIPLIER, not a percentage "
              "(character.py:1551: `gained = source * pct`), so 0.05 per "
              "rank reaches the real 15%.")

T.node("cleanse_spirit", "Cleanse Spirit",
       "Teaches Cleanse Spirit, lifting poison, disease and curse alike.",
       4, 3, 1, node_type="active",
       effects={"unlock_ability": "shaman_cleanse_spirit"},
       connected_to=["purification"],
       source="WotLK row 4, kept - the ONLY unlock for "
              "shaman_cleanse_spirit, which is requires_talent. The real "
              "talent requires Purification, which connected_to "
              "reproduces. Moved here from the outgoing tree's capstone, "
              "where it was bundled into a node called 'Restoration "
              "Capstone' that had no counterpart in the real tree.")

# ----------------------------------------------------------------- tier 5
T.node("ancestral_awakening", "Ancestral Awakening",
       "Your critical heals call an ancestral spirit to mend your neediest "
       "ally.",
       5, -3, 3,
       proc={"trigger": "on_crit", "chance": 33, "icd": 0,
             "smart_heal": 70},
       connected_to=["natures_guardian"],
       source="WotLK row 5, NEW to our tree: 'When you critically heal with "
              "your Healing Wave, Lesser Healing Wave or Riptide you summon "
              "an Ancestral spirit to heal the lowest health party or raid "
              "member for 10%-30% of the amount healed.' Built with "
              "smart_heal, which is the engine's real 'heal whoever needs "
              "it most' payload and one of only three payloads that can "
              "read a triggering amount - so this is as close to the real "
              "talent as the engine gets. The amount is flat rather than a "
              "percentage of the heal.")

T.node("earth_shield", "Earth Shield",
       "Teaches Earth Shield, warding an ally with the strength of stone.",
       5, -1, 1, node_type="active",
       effects={"unlock_ability": "shaman_earth_shield"},
       connected_to=["natures_blessing"],
       source="WotLK row 5, kept - the ONLY unlock for "
              "shaman_earth_shield, which is requires_talent. Its "
              "channel-protection clause has nothing to act on - there is "
              "no channelling - and its charges are not expressible, so "
              "both live in the ability. It is Improved Earth Shield's "
              "prerequisite, preserved below.")

T.node("improved_earth_shield", "Improved Earth Shield",
       "Increases the healing of your Earth Shield by 10% per rank.",
       5, 1, 2,
       effects={"ability_shaman_earth_shield_healing": 0.10},
       connected_to=["earth_shield"],
       source="WotLK row 5, NEW to our tree: 'Increases the amount of "
              "charges for your Earth Shield by 2, and increases the "
              "healing done by your Earth Shield by 10%/20%.' The healing "
              "half is built verbatim; charges do not exist. The real "
              "talent requires Earth Shield, reproduced. USES _healing.")

T.node("tidal_waves", "Tidal Waves",
       "Casting Riptide quickens your next heals by 20% for 2 turns.",
       5, 3, 5,
       proc={"trigger": "on_cast", "chance": 20, "icd": 0,
             "ability_filter": ["shaman_riptide"],
             "apply_effect": {"effect_id": "tidal_waves",
                              "name": "Tidal Waves",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"haste": 20},
                              "on_target": False}},
       connected_to=["natures_blessing"],
       source="WotLK row 5: 'When you cast Chain Heal or Riptide, you have "
              "a 20%-100% chance to lower the cast time of your Healing "
              "Wave spell by 30% and increase its critical effect chance.' "
              "DEPARTURE - no cast times, so a shorter cast becomes haste. "
              "Chain Heal does not exist, so only Riptide is in the filter. "
              "The real chance curve is kept. Ranked by chance, since a "
              "proc's payload does not scale with points.")

# ----------------------------------------------------------------- tier 6
T.node("riptide", "Riptide",
       "Teaches Riptide, a healing surge that lingers.",
       6, -1, 1, node_type="active",
       effects={"unlock_ability": "shaman_riptide"},
       connected_to=["tidal_waves"],
       source="WotLK row 10, the capstone, kept - the ONLY unlock for "
              "shaman_riptide, which is requires_talent.")

T.node("totemic_mastery", "Call of the Ancestors",
       "Teaches Call of the Ancestors, summoning the help of those who came "
       "before.",
       6, 1, 1, node_type="active",
       effects={"unlock_ability": "shaman_call_of_ancestors"},
       connected_to=["improved_earth_shield"],
       source="Kept - the ONLY unlock for shaman_call_of_ancestors, which "
              "is requires_talent. Not a WotLK talent; a Frontier addition "
              "that stays because dropping it would strand the ability, and "
              "a second tier-6 node gives the capstone row a real choice "
              "rather than a single forced point. The talent_id is kept as "
              "totemic_mastery, its name in the outgoing tree, so nothing "
              "referring to it breaks.")


def main():
    return T.write(was="23 nodes, 72 points - 4 proc, 7 ability-scoped, "
                       "7 flat stat, 5 unlock")


if __name__ == "__main__":
    sys.exit(main())
