#!/usr/bin/env python3
"""Rebuild Priest Holy from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_priest_holy.py

SOURCE: data/reference/wotlk/priest.json (from Spell.dbc).
Worksheet: data/reference/wotlk_worksheets/priest.md.

ROLE: throughput healer. Renew, direct heals, Circle of Healing, and
Spirit converted into spell power.

CAST TIMES AGAIN: Healing Focus (pushback), Divine Fury (cast time), Surge
of Light (instant cast), Serendipity (cast time) are all written on a
system that does not exist. Each is rebuilt as the throughput or resource
the real talent exists to provide.

ABILITIES THE REAL TREE WANTS AND WE LACK: Flash Heal, Greater Heal,
Binding Heal, Holy Nova, Divine Hymn, Prayer of Mending, Lightwell. That
is seven, so most heal-named talents land on priest_heal, priest_renew or
priest_prayer_of_healing. Lightwell is DROPPED outright - it is a
clickable object and nothing in this engine is remotely like one.

THE TREE'S BEST TALENT IS A REAL STAT CONVERSION. Spiritual Guidance is
"+25% spell power from Spirit", and spirit IS a valid
STAT_CONVERSION_SOURCE. The unit is a RAW MULTIPLIER
(character.py:1551 does `gained = source * pct`), so it is authored at
0.05 per rank.

Test of Faith uses low_health_healing_pct, the FRIENDLY-side mirror of
low_health_damage_pct. Note it is not ability-scoped, so it applies to all
healing rather than the real talent's named list.

UNIT CONVENTIONS: crit_chance_spell / crit_taken_reduction / spirit_pct
are PERCENTAGE POINTS; healing_done / spell_damage_taken_pct /
low_health_healing_pct / ability_<id>_healing are FRACTIONS; mp5 is FLAT;
*_from_*_pct is a FRACTION read as a raw multiplier.

EVERY HEAL NODE USES ability_<id>_HEALING, never _damage. That exact
mistake left 18 talents across four classes silently dead.

KEPT MANDATORY: Circle of Healing is the only unlock for
priest_circle_of_healing, which is requires_talent.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

T = Tree("priest_holy", "Priest Holy",
         "The Light's own healer - throughput, Renew and group restoration.")

# ----------------------------------------------------------------- tier 0
T.node("healing_focus", "Healing Focus",
       "Reduces the cost of your Heal by 5% per rank.",
       0, -2, 2, effects={"ability_priest_heal_cost_pct": 0.05},
       source="WotLK row 0: 'Reduces the pushback suffered from damaging "
              "attacks while casting any healing spell by 35%/70%.' "
              "DEPARTURE - there are no cast times and so no pushback. The "
              "talent exists so a healer keeps healing under fire; "
              "delivered as cost. _cost_pct is a FRACTION where POSITIVE IS "
              "A REDUCTION. Kept from the outgoing tree, corrected from 3 "
              "ranks to the real 2.")

T.node("improved_renew", "Improved Renew",
       "Increases the healing of your Renew by 5% per rank.",
       0, 0, 3, effects={"ability_priest_renew_healing": 0.05},
       source="WotLK row 0: 'Increases the amount healed by your Renew "
              "spell by 5%/10%/15%.' Built verbatim over the real 3 ranks; "
              "the outgoing version had 5 ranks. USES _healing, not "
              "_damage.")

T.node("holy_specialization", "Holy Specialization",
       "Increases your spell critical chance by 1% per rank.",
       0, 2, 5, effects={"crit_chance_spell": 1.0},
       source="WotLK row 0: 'Increases the critical effect chance of your "
              "Holy spells by 1%-5%.' Built verbatim - crit_chance_spell "
              "covers all spells rather than one school, and every Priest "
              "heal here is Holy. Kept from the outgoing tree.")

# ----------------------------------------------------------------- tier 1
T.node("desperate_prayer", "Desperate Prayer",
       "Being struck hard mends you, healing over 2 turns.",
       1, -6, 1,
       proc={"trigger": "on_damage_taken", "chance": 100, "icd": 4,
             "apply_effect": {"effect_id": "desperate_prayer",
                              "name": "Desperate Prayer",
                              "effect_type": "hot", "duration": 2,
                              "potency": 60, "on_target": False}},
       source="WotLK row 1: 'Instantly heals the caster for 263 to 325.' "
              "DEPARTURE - there is no priest_desperate_prayer ability to "
              "unlock. Delivered as a reactive self-heal with icd 4, which "
              "keeps it a cooldown rather than constant healing. A "
              "proc-applied hot states PER-TURN healing as `potency`. The "
              "outgoing version granted max_health_pct, which is not this "
              "talent.")

T.node("spell_warding", "Spell Warding",
       "Reduces all spell damage taken by 2% per rank.",
       1, -4, 5, effects={"spell_damage_taken_pct": -0.02},
       connected_to=["healing_focus"],
       source="WotLK row 1, NEW to our tree, built verbatim: 'Reduces all "
              "spell damage taken by 2%-10%.' spell_damage_taken_pct is a "
              "FRACTION as a talent effect and NEGATIVE reduces - the "
              "opposite sign to its meaning inside a status effect.")

T.node("blessed_recovery", "Blessed Recovery",
       "Being critically struck heals you over 2 turns.",
       1, -2, 3,
       proc={"trigger": "on_damage_taken", "chance": 33, "icd": 1,
             "apply_effect": {"effect_id": "blessed_recovery",
                              "name": "Blessed Recovery",
                              "effect_type": "hot", "duration": 2,
                              "potency": 35, "on_target": False}},
       connected_to=["improved_renew"],
       source="WotLK row 1: 'After being struck by a melee or ranged "
              "critical hit, Blessed Recovery heals you for 5%/10%/15% of "
              "the damage taken over 6 sec.' DEPARTURE on the trigger - "
              "there is no on-crit-TAKEN event, so on_damage_taken with icd "
              "1 stands in. Healing as a percentage of the damage taken is "
              "also unavailable: of the payloads that read the triggering "
              "amount, none applies a hot. 6 seconds is 2 turns. Kept as a "
              "proc from the outgoing tree.")

T.node("divine_fury", "Divine Fury",
       "Increases the damage of your Smite and Holy Fire and the healing of "
       "your Heal by 3% per rank.",
       1, 0, 5,
       effects={"ability_priest_smite_damage": 0.03,
                "ability_priest_holy_fire_damage": 0.03,
                "ability_priest_heal_healing": 0.03},
       connected_to=["improved_renew"],
       source="WotLK row 1: 'Reduces the casting time of your Smite, Holy "
              "Fire, Heal and Greater Heal spells by 0.1-0.5 sec.' "
              "DEPARTURE - no cast times. A shorter cast is more "
              "throughput, so it is delivered as throughput on the three "
              "named spells that exist. NOTE the Heal clause uses _healing "
              "and the damage clauses use _damage - mixing them on one node "
              "is correct and getting it wrong is the 18-dead-talents "
              "mistake. Kept from the outgoing tree. It is Searing Light's "
              "prerequisite in the real tree, preserved below.")

T.node("inspiration", "Inspiration",
       "Your critical heals harden the target against physical damage.",
       1, 2, 3,
       proc={"trigger": "on_crit", "chance": 33, "icd": 0,
             "apply_effect": {"effect_id": "inspiration",
                              "name": "Inspiration",
                              "effect_type": "buff", "duration": 4,
                              "stat_mods": {"physical_damage_taken_pct": -10.0},
                              "on_target": False}},
       connected_to=["holy_specialization"],
       source="WotLK row 1: 'Reduces your target's physical damage taken by "
              "5%/10% for 15 sec after getting a critical effect from your "
              "Flash Heal, Heal or Greater Heal.' Built with the real 10% "
              "and 15 seconds as 4 turns. on_target is False because a "
              "talent-sourced effect cannot be aimed at the heal's "
              "recipient, so the priest carries it - a real departure. "
              "MIND THE UNIT: inside a status effect "
              "physical_damage_taken_pct is PERCENTAGE POINTS (-10.0), "
              "unlike the BARE damage_taken_pct in the same position, which "
              "is read raw. Kept as a proc from the outgoing tree.")

# ----------------------------------------------------------------- tier 2
T.node("holy_reach", "Holy Reach",
       "Increases the healing of your Circle of Healing and Prayer of "
       "Healing by 5% per rank.",
       2, -5, 2,
       effects={"ability_priest_circle_of_healing_healing": 0.05,
                "ability_priest_prayer_of_healing_healing": 0.05},
       connected_to=["spell_warding"],
       source="WotLK row 2: 'Increases the range of your Smite and Holy "
              "Fire spells and the radius of your Prayer of Healing, Holy "
              "Nova, Divine Hymn and Circle of Healing spells by 10%/20%.' "
              "DEPARTURE - there is no range or radius in this engine. A "
              "wider heal reaches more people, so it is delivered as "
              "healing on the two group heals that exist. Kept from the "
              "outgoing tree.")

T.node("healing_prayers", "Healing Prayers",
       "Reduces the cost of your Prayer of Healing by 10% per rank.",
       2, -3, 2,
       effects={"ability_priest_prayer_of_healing_cost_pct": 0.10},
       connected_to=["spell_warding"],
       source="WotLK row 2: 'Reduces the mana cost of your Prayer of "
              "Healing and Prayer of Mending spell by 10%/20%.' Prayer of "
              "Mending does not exist. Kept from the outgoing tree, which "
              "used the FLAT _cost key.")

T.node("improved_healing", "Improved Healing",
       "Reduces the cost of your Heal and Penance by 5% per rank.",
       2, -1, 3,
       effects={"ability_priest_heal_cost_pct": 0.05,
                "ability_priest_penance_cost_pct": 0.05},
       connected_to=["blessed_recovery"],
       source="WotLK row 2: 'Reduces the mana cost of your Lesser Heal, "
              "Heal, Greater Heal, Divine Hymn and Penance spells by "
              "5%/10%/15%.' Built verbatim for the two that exist. Stacks "
              "with Healing Focus on priest_heal. Kept from the outgoing "
              "tree.")

T.node("spirit_of_redemption", "Spirit of Redemption",
       "Increases your Spirit by 5%.",
       2, 1, 1, effects={"spirit_pct": 5.0},
       connected_to=["divine_fury"],
       source="WotLK row 2: 'Increases total Spirit by 5% and upon death, "
              "the priest becomes the Spirit of Redemption for 15 sec.' The "
              "Spirit half is verbatim. DEPARTURE on the second - there is "
              "no on-death hook and no post-death state. The outgoing "
              "version granted FLAT spirit; spirit_pct is PERCENTAGE "
              "POINTS. It feeds Spiritual Guidance one column across.")

T.node("searing_light", "Searing Light",
       "Increases the damage of your Smite, Holy Fire and Penance by 5% per "
       "rank.",
       2, 3, 2,
       effects={"ability_priest_smite_damage": 0.05,
                "ability_priest_holy_fire_damage": 0.05,
                "ability_priest_penance_damage": 0.05},
       connected_to=["divine_fury"],
       source="WotLK row 2, built verbatim for the three real spells that "
              "exist: 'Increases the damage of your Smite, Holy Fire, Holy "
              "Nova and Penance spells by 5%/10%.' The real talent requires "
              "Divine Fury, which connected_to reproduces. Kept from the "
              "outgoing tree, corrected from 3 ranks to the real 2.")

T.node("spiritual_guidance", "Spiritual Guidance",
       "Increases your spell power by 5% of your Spirit per rank.",
       2, 5, 5,
       effects={"spell_power_from_spirit_pct": 0.05},
       connected_to=["inspiration"],
       source="WotLK row 2, built verbatim: 'Increases spell power by "
              "5%-25% of your total Spirit.' A REAL stat conversion - "
              "spell_power is a valid STAT_CONVERSION_TARGET and spirit a "
              "valid source. THE UNIT IS A RAW MULTIPLIER, not a "
              "percentage: character.py:1551 does `gained = source * pct`, "
              "so 0.05 per rank reaches the real 25%. Authoring 25 would "
              "have granted twenty-five times the priest's Spirit as spell "
              "power. The outgoing version granted FLAT spirit and FLAT "
              "healing_power, which is neither the conversion nor its "
              "magnitude.")

# ----------------------------------------------------------------- tier 3
T.node("surge_of_light", "Surge of Light",
       "Your spell criticals have a 50% chance per rank to make your next "
       "spells cheaper for 2 turns.",
       3, -1, 2,
       proc={"trigger": "on_crit", "chance": 50, "icd": 0,
             "apply_effect": {"effect_id": "surge_of_light",
                              "name": "Surge of Light",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"all_ability_cost_pct": 25.0},
                              "on_target": False}},
       connected_to=["improved_healing"],
       source="WotLK row 3, NEW to our tree: 'Your spell criticals have a "
              "25%/50% chance to cause your next Smite or Flash Heal spell "
              "to be instant cast, cost no mana but be incapable of a "
              "critical hit.' DEPARTURE - no cast times, so 'instant' has "
              "nothing to act on, and nothing consumes a buff on use. The "
              "mana clause survives as a temporary cost reduction. MIND THE "
              "FLIP: all_ability_cost_pct is PERCENTAGE POINTS inside a "
              "status effect (25.0) and a FRACTION as a talent effect - "
              "this key is the one audit_talents has caught most often in "
              "this project.")

T.node("spiritual_healing", "Spiritual Healing",
       "Increases all your healing by 2% per rank.",
       3, 1, 5, effects={"healing_done": 0.02},
       connected_to=["searing_light"],
       source="WotLK row 3, NEW to our tree, built verbatim: 'Increases the "
              "amount healed by your healing spells by 2%-10%.' "
              "healing_done is a FRACTION and is the global healing "
              "multiplier.")

# ----------------------------------------------------------------- tier 4
T.node("holy_concentration", "Holy Concentration",
       "Your critical heals restore 180 mana.",
       4, -5, 3,
       proc={"trigger": "on_crit", "chance": 33, "icd": 0,
             "grant_resource": {"resource": "mana", "amount": 180}},
       connected_to=["surge_of_light"],
       source="WotLK row 4, NEW to our tree: 'Your mana regeneration from "
              "spirit is increased by 16%-50% for 8 sec after you "
              "critically heal.' DEPARTURE - there is no key that modifies "
              "mana regeneration at all (resource_regen_pct is dead data), "
              "so a temporary regeneration boost cannot be built. Delivered "
              "as mana on the same trigger the real talent uses.")

T.node("body_and_soul", "Body and Soul",
       "Increases the duration of your Power Word: Shield by 1 turn per "
       "rank.",
       4, -3, 2,
       effects={"ability_priest_power_word_shield_duration": 1},
       connected_to=["surge_of_light"],
       source="WotLK row 4: 'When you cast Power Word: Shield, you increase "
              "the target's movement speed by 30%/60% for 4 sec, and you "
              "have a 100% chance to cleanse the target of all poison "
              "effects.' DEPARTURE - no movement speed, and a "
              "talent-sourced effect cannot be aimed at the shield's "
              "target. Delivered as shield duration, which is the clause's "
              "real beneficiary. ability_<id>_duration is FLAT turns and "
              "POSITIVE EXTENDS. Kept from the outgoing tree.")

T.node("empowered_healing", "Empowered Healing",
       "Increases the healing of your Heal by 4% per rank.",
       4, -1, 5, effects={"ability_priest_heal_healing": 0.04},
       connected_to=["spiritual_healing"],
       source="WotLK row 4: 'Your Greater Heal spell gains an additional "
              "8%-40% and your Flash Heal and Binding Heal gain an "
              "additional 4%-20% of your bonus healing effects.' None of "
              "the three named spells exist; priest_heal stands in for all "
              "of them at the middle value. Kept from the outgoing tree, "
              "corrected from 5% to 4% per rank.")

T.node("blessed_resilience", "Blessed Resilience",
       "Increases your healing by 1% per rank and reduces the chance you "
       "are critically hit by 2% per rank.",
       4, 1, 3,
       effects={"healing_done": 0.01, "crit_taken_reduction": 2.0},
       connected_to=["spiritual_healing"],
       source="WotLK row 4, built with both halves: 'Increases the "
              "effectiveness of your healing spells by 1%-3%, and critical "
              "hits made against you have a 20%-60% chance to prevent the "
              "critical.' Preventing a crit outright is not expressible, "
              "but crit_taken_reduction - which lowers an attacker's crit "
              "chance against you (abilities.py:1317) - is the same idea "
              "and is a live key in PERCENTAGE POINTS. Kept from the "
              "outgoing tree, which had the crit half only.")

T.node("serendipity", "Serendipity",
       "Your heals have a 33% chance per rank to quicken you by 12% for 2 "
       "turns.",
       4, 3, 3,
       proc={"trigger": "on_heal_cast", "chance": 33, "icd": 0,
             "apply_effect": {"effect_id": "serendipity",
                              "name": "Serendipity",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"haste": 12},
                              "on_target": False}},
       connected_to=["empowered_healing"],
       source="WotLK row 4: 'When you heal with Binding Heal or Flash Heal, "
              "the cast time of your next Greater Heal or Prayer of Healing "
              "spell is reduced by 4%-12%.' DEPARTURE - no cast times. A "
              "shorter cast is haste, so that is what it grants, at the "
              "real 12%. Kept as a proc from the outgoing tree.")

# ----------------------------------------------------------------- tier 5
T.node("empowered_renew", "Empowered Renew",
       "Increases the healing of your Renew by 5% per rank.",
       5, -3, 3, effects={"ability_priest_renew_healing": 0.05},
       connected_to=["holy_concentration"],
       source="WotLK row 5: 'Your Renew spell gains an additional 5%-15% of "
              "your bonus healing effects, and your Renew will instantly "
              "heal the target for 1-3 ticks worth of healing.' The "
              "throughput half is built verbatim. The instant-tick clause "
              "cannot be built - nothing converts a hot's pending ticks "
              "into a direct heal. Stacks with Improved Renew. Kept from "
              "the outgoing tree.")

T.node("circle_of_healing", "Circle of Healing",
       "Teaches Circle of Healing, mending everyone around your target.",
       5, -1, 1, node_type="active",
       effects={"unlock_ability": "priest_circle_of_healing"},
       connected_to=["empowered_healing"],
       source="WotLK row 5, kept - the ONLY unlock for "
              "priest_circle_of_healing, which is requires_talent. Moved "
              "from tier 3 to its real row.")

T.node("divine_providence", "Divine Providence",
       "Increases the healing of your Circle of Healing and Prayer of "
       "Healing by 2% per rank.",
       5, 1, 5,
       effects={"ability_priest_circle_of_healing_healing": 0.02,
                "ability_priest_prayer_of_healing_healing": 0.02},
       connected_to=["circle_of_healing"],
       source="WotLK row 5: 'Increases the amount healed by Circle of "
              "Healing, Binding Heal, Holy Nova, Prayer of Healing, Divine "
              "Hymn and Prayer of Mending by 2%-10%.' Built verbatim for the "
              "two that exist. Stacks with Holy Reach. Kept from the "
              "outgoing tree.")

T.node("test_of_faith", "Test of Faith",
       "Increases your healing by 4% per rank on targets below half health.",
       5, 3, 3, effects={"low_health_healing_pct": 0.04},
       connected_to=["serendipity"],
       source="WotLK row 5: 'Increases healing by 4%-12% on friendly "
              "targets at or below 50% health.' Built as a REAL "
              "conditional: low_health_healing_pct is the friendly-side "
              "mirror of low_health_damage_pct and is a live key. NOTE it "
              "is not ability-scoped, so it lifts all healing rather than "
              "a named list - which the real talent also does. "
              "low_health_threshold_pct is NOT authored: it SUMS across "
              "talents and the default is already what this wants. The "
              "outgoing version was a proc with no conditional at all.")

# ----------------------------------------------------------------- tier 6
T.node("guardian_spirit", "Guardian Spirit",
       "A guardian watches over you, greatly increasing healing you receive "
       "while badly wounded.",
       6, 1, 1,
       effects={"low_health_healing_pct": 0.20,
                "low_health_damage_reduction_pct": 0.10},
       connected_to=["test_of_faith"],
       source="WotLK row 10, the capstone: 'Calls upon a guardian spirit to "
              "watch over the friendly target. The spirit increases the "
              "healing received by the target by 40%... and will sacrifice "
              "itself to prevent the target from dying.' DEPARTURE - no "
              "ability to unlock, a talent effect can never reach an ally, "
              "and there is no death-prevention hook. Delivered as both "
              "real clauses applied to the priest and conditioned on being "
              "badly hurt, which is when the real spell is cast. Both keys "
              "share low_health_threshold_pct's default, which is why it is "
              "not authored. The outgoing version was a proc with an empty "
              "effects dict.")


def main():
    return T.write(was="23 nodes, 72 points - 8 proc, 9 ability-scoped, "
                       "2 flat stat, 1 unlock, 3 mixed")


if __name__ == "__main__":
    sys.exit(main())
