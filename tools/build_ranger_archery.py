#!/usr/bin/env python3
"""Rebuild Ranger's Archery tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_ranger_archery.py [--check]

SOURCE: data/reference/coa_worksheets/ranger.md and
data/reference/coa/ranger.json - 35 real Archery talents. Role: DPS.

Ranger measured 50 of its 64 matched talents as pure scalars on our side,
the second-worst in the audit. Archery was 23 nodes with 5 procs.

FOCUS IS REAL, ADVANTAGE IS NOT, and that split decides most of this tree.
Ranger is (ResourceType.ARCHERY_POINTS, None) at abilities.py:165 - so
archery_points is the PRIMARY pool, like Templar's Combo - and five
abilities generate it (quick_shot 12, hunting_shot 15, deadshot 10,
ravage 12, wild_strike 14, vipers_bite 8). CoA's "Focus" is exactly that
pool, so every Focus cost, Focus refund and Focus generation talent ports.

CoA's "Advantage" is a STACK COUNT, and nothing in this engine reads a
stack count. Ten Archery talents scale off it - Precision Shot's damage,
Skirmish's duration, Neurotoxin's silence, Incendiary Shot, Maximum Power,
Masterful Archery, Headshots Only, Elven Enchantments - and every one of
them loses that scaling. The stacking EFFECTS are real (max_stacks works);
only reading the count is impossible.

THE EXECUTE PAIR PORTS VERBATIM, as it did for Reaper. Our Deadshot
already carries execute_threshold_pct 20, matching CoA's "Only usable on
enemies below 20% health" exactly, and Silent, But Deadly is CoA's
"8% chance to allow you to use Deadshot regardless of the target's health"
- which is the bypass_execute_threshold proc flag, consumed on use.

ARCHERY OWNS low_health_threshold_pct FOR THE WHOLE CLASS at CoA's own
20%, because that key SUMS across talents and a character can spend in
several trees. Brigand's Marked for Death and Dastardly inherit it.
Enforced by tools/qa_summing_thresholds.py.

NOT BUILDABLE (each recorded on its node where one survives):
  Opportunist and Dastardly's first half need an ABOVE-health conditional
  (high_health_damage_threshold_pct is dead data); Serrations and Corrosive
  Poison read whether a target is bleeding or poisoned; Hawkeye and
  Headshots Only fire off periodic ticks, which are not a trigger
  (status_effects.py:914 ticks on the recipient with no caster handle);
  Lethal Wounds and Razorquills change "tick rate", which has no meaning
  when a dot ticks once per turn; Deadeye, Light Arrows and Brutal Shot's
  line are range mechanics; Pathfinder, Skirmish and Elven Enchantments
  read whether another effect is active; An Arrow for Everything scales
  Quivers, which are plain self-buffs here.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/ranger_archery.json"

#: CoA's Focus. Five abilities generate it; it is Ranger's PRIMARY pool.
GENERATORS = ["ranger_quick_shot", "ranger_hunting_shot", "ranger_deadshot",
              "ranger_ravage", "ranger_wild_strike", "ranger_vipers_bite"]

TREE = {
    "spec_name": "Ranger Archery",
    "tree_id": "ranger_archery",
    "description": ("Bow discipline - long shots, open wounds, and a "
                    "finisher that only works on the dying."),
    "_source_note": (
        "Rebuilt 6 Nov 2026 from the 35 real CoA Archery talents (role "
        "DPS). CoA's Focus is our archery_points, Ranger's PRIMARY "
        "resource with five generators, so every Focus talent ports. CoA's "
        "Advantage is a stack count and nothing reads one, so ten talents "
        "lose that scaling. The execute pair ports verbatim: Deadshot "
        "already carries execute_threshold_pct 20 and Silent, But Deadly "
        "is the bypass_execute_threshold proc. This tree owns "
        "low_health_threshold_pct for the class, at CoA's 20%."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20,
                          "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"ranger_archery_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"ranger_archery_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


#: Appended wherever CoA scales a talent off Advantage stacks.
ADVANTAGE = (
    "CoA scales this off ADVANTAGE STACKS. The stacking effect itself is "
    "buildable (max_stacks is honoured) but NOTHING READS A STACK COUNT "
    "anywhere in this engine, so the per-stack scaling is dropped and the "
    "node lands on the flat value CoA's typical stack count comes to. Ten "
    "Archery talents take this loss.")

#: Appended wherever CoA fires off a dot tick.
PERIODIC = (
    "CoA fires this off PERIODIC DAMAGE, which is not a trigger: "
    "status_effects.py:914 ticks a dot by calling the recipient's own "
    "take_damage with no caster reference, so there is nobody to fire a "
    "proc on. Re-pointed to a live trigger. Eight Chronomancer talents "
    "took the same loss.")

N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "devastating_shots", "Devastating Shots",
    "Increases your critical strike chance by 4% and your hit chance by 2%.",
    0, -4,
    effects={"crit_chance_physical": 4.0, "hit_rating": 2.0},
    connect=["improved_serrated_shot"],
    source="CoA over 2 ranks: 'Increases your critical strike chance by 2% "
           "and your hit chance by 1%.' PORTS EXACTLY, doubled for the two "
           "ranks. Both keys are PERCENTAGE POINTS. Was a pure scalar on "
           "our side, and in this one case that is what CoA wrote too."))

N.append(node(
    "improved_serrated_shot", "Improved Serrated Shot",
    "Increases the damage of Serrated Shot by 30% and its duration by 2 "
    "turns.",
    0, -2,
    effects={"ability_ranger_serrated_shot_damage": 0.30,
             "ability_ranger_serrated_shot_duration": 2},
    connect=["studded_arrows", "superb_shot"],
    source="CoA: 'Increases the damage of Serrated Shot by 30%.' The damage "
           "ports exactly. The duration is added from CoA's A Quick Demise "
           "('Auto shots have a 20% chance to extend Serrated Shot by 2 "
           "sec'), whose proc form cannot be built - no payload extends a "
           "LIVE effect's duration - but whose intent lands as a flat "
           "extension. THAT IS A REAL DAMAGE INCREASE on a dot, not a "
           "dilution: abilities.py:2777 derives per-turn damage from the "
           "ability's OWN base duration, so a talent extension adds TICKS "
           "at full value. Serrated Shot goes 3 -> 5 turns. SMALL INTEGER "
           "IN TURNS, so talent_ranks.spread() refuses to rank this node."))

N.append(node(
    "studded_arrows", "Studded Arrows",
    "Increases the damage of Quick Shot by 20% and of Skullpiercer by 15%.",
    0, 0,
    effects={"ability_ranger_quick_shot_damage": 0.20,
             "ability_ranger_skullpiercer_damage": 0.15},
    connect=["archery_master"],
    source="CoA over 2 ranks: 'Increases the ranged weapon damage dealt by "
           "Quick Shot by 10%.' Doubled for the two ranks. Extended to "
           "Skullpiercer from CoA's New-Age Archery, so the node covers the "
           "spec's two filler shots rather than one. Quick Shot is the "
           "biggest Focus generator at 12, so this is the node that pays "
           "for the rotation. Was a pure scalar on our side."))

N.append(node(
    "boots_of_elvenkind", "Boots of Elvenkind",
    "Increases your Agility by 10% and your ranged attack power by 20% of "
    "your Agility.",
    0, 2,
    effects={"agility_pct": 10, "ranged_ap_from_agility_pct": 0.20},
    connect=["pierced"],
    source="CoA: 'Increases your Agility by 5% and reduces the duration of "
           "movement slowing effects on you by -20%.' The Agility ports "
           "(doubled, since the second half is dead). Slow-duration "
           "reduction has no key: the only duration-reduction the engine "
           "reads is stun_duration_reduction_pct, checked solely against "
           "is_stun effects (status_effects.py:699), and roots and snares "
           "have no mechanic at all. Replaced with CoA's own shared Nimble "
           "passive ('ranged haste by 20% of your Agility') re-pointed to "
           "ranged attack power, since ranged_ap is in "
           "STAT_CONVERSION_TARGETS and agility in SOURCES - a legal pair. "
           "agility_pct is PERCENTAGE POINTS (character.py:1266); the "
           "conversion key is a FRACTION. Was a pure scalar on our side."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "superb_shot", "Superb Shot",
    "Your ranged attacks restore 8 Focus.",
    1, -2,
    proc={"trigger": "on_weapon_swing", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "archery_points", "amount": 8}},
    connect=["skirmish"],
    source="CoA: 'Damage dealt by Auto Shot now restores 4 Focus.' PORTS "
           "VERBATIM. archery_points IS CoA's Focus - Ranger's primary pool "
           "with five generators - and grant_resource routes through the "
           "same gain_resource() those five use, so the cap is respected. "
           "8 rather than 4 because this fires on a swing where CoA's auto "
           "shot fires continuously. The `amount` field is FLAT; there is "
           "no pct_max field."))

N.append(node(
    "archery_master", "Archery Master",
    "Your critical strikes restore 12 Focus.",
    1, 0,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "archery_points", "amount": 12}},
    connect=["skirmish"],
    source="CoA: 'Critical strikes with Quick Shot now generate an "
           "additional stack of Advantage.' " + ADVANTAGE + " Built as the "
           "Focus equivalent instead, which is the pool that actually "
           "exists - 12 is what Quick Shot itself generates, so a crit on "
           "it now pays double, which is CoA's intent even if the currency "
           "differs. Only the Quick-Shot scoping goes (no per-ability proc "
           "trigger)."))

N.append(node(
    "pierced", "Pierced",
    "Your critical strikes open a bleed dealing damage over 3 turns.",
    1, 2,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "apply_effect": {"effect_id": "pierced", "name": "Pierced",
                           "effect_type": "dot", "duration": 3,
                           "potency": 26, "damage_school": "physical",
                           "dispel_type": None, "on_target": True}},
    connect=["serrations"],
    source="CoA: 'Critical strikes with Skullpiercer and Precision Shot "
           "cause the enemy to bleed for an additional 50% damage of the "
           "damage dealt over 4 sec.' PORTS ALMOST EXACTLY - only the "
           "two-ability scoping goes (no per-ability proc trigger) and the "
           "'50% of the damage dealt' becomes a fixed potency, because "
           "apply_effect cannot read the triggering hit's amount (only "
           "bonus_pct, leech_pct and smart heals do, and none of them apply "
           "an effect). 4 sec -> 3 turns. A proc-applied dot carries "
           "`potency` as PER-TURN damage, unlike an ability rank's "
           "effect_value, which is the TOTAL and gets divided - so 26 here "
           "is 26 a turn, 78 over the bleed."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "skirmish", "Skirmish",
    "Increases your critical strike chance by 10% and reduces all your "
    "ability costs by 15%.",
    2, -1,
    effects={"crit_chance_physical": 10.0, "all_ability_cost_pct": 0.15},
    connect=["mortal_shots"],
    source="CoA: 'Increases your critical strike chance by 15% and reduces "
           "your Focus costs by 25%. Lasts 4 sec for each stack of "
           "Advantage.' " + ADVANTAGE + " Since the duration was the part "
           "that scaled, and a self-buff with no readable stack count has "
           "no duration to compute, this becomes a flat passive at "
           "two-thirds the values - a permanent 10%/15% rather than a "
           "burst window. The ranger_skirmish ABILITY still exists "
           "separately as a 3-turn crit buff, so the burst form is in the "
           "game; this node is its passive floor. all_ability_cost_pct is a "
           "FRACTION where POSITIVE MEANS A REDUCTION; "
           "crit_chance_physical is percentage points."))

N.append(node(
    "serrations", "Serrations",
    "Increases the damage of your periodic effects by 20%.",
    2, 2,
    effects={"dot_damage": 0.20},
    connect=["strike_where_it_hurts"],
    source="CoA over 2 ranks: 'Increases your damage against bleeding or "
           "Poisoned targets by 5%.' NOTHING READS A TARGET'S DEBUFFS, so "
           "the condition cannot be built and a condition that silently "
           "never fires is worse than none. Re-pointed to dot_damage, which "
           "keeps the node about the same thing - this spec's bleeds and "
           "poisons - from the causing side rather than the reading side. "
           "Folded in CoA's Lethal Wounds and Razorquills, both of which "
           "change 'tick rate': meaningless when a dot ticks exactly once "
           "per turn. A FRACTION."))

N.append(node(
    "mortal_shots", "Mortal Shots",
    "Reduces the cooldown of Crippling Shot by 40% and of Skullpiercer by "
    "25%.",
    2, 0,
    effects={"ability_ranger_crippling_shot_cooldown_pct": 0.40,
             "ability_ranger_skullpiercer_cooldown_pct": 0.25},
    connect=["swiftshot"],
    source="CoA: 'Reduces the cooldown of Crippling Shot by -4 sec.' "
           "Crippling Shot's cooldown is 4 turns, so -4 sec is about 40% "
           "there. Extended to Skullpiercer so the node is not a "
           "one-ability pick. *_cooldown_pct keys are FRACTIONS and "
           "POSITIVE MEANS A REDUCTION - the opposite sign convention from "
           "most of this file; talented_cooldown floors at 1 turn. Was a "
           "pure scalar on our side."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "swiftshot", "Swiftshot",
    "Your ranged attacks have a 30% chance to leave the target taking 11% "
    "more physical damage for 3 turns.",
    3, -1,
    proc={"trigger": "on_weapon_swing", "chance": 30, "icd": 0,
          "apply_effect": {"effect_id": "swiftshot", "name": "Swiftshot",
                           "effect_type": "debuff", "duration": 3,
                           "stat_mods": {"physical_damage_taken_pct": 11},
                           "dispel_type": None, "on_target": True}},
    connect=["hunting_with_precision"],
    source="CoA: 'Damage dealt by Precision Shot now increases enemy "
           "Physical damage taken by 11% for 10 sec.' PORTS ALMOST EXACTLY; "
           "only the Precision-Shot scoping goes (no per-ability proc "
           "trigger). 10 sec -> 3 turns, CoA's 11% kept verbatim. CAREFUL: "
           "physical_damage_taken_pct is PERCENTAGE POINTS inside a status "
           "effect (monster.py:736 divides by 100) where as a TALENT effect "
           "it is a fraction - so 11 here is 11%, and 0.11 would have "
           "delivered 0.11%."))

N.append(node(
    "strike_where_it_hurts", "Strike Where It Hurts",
    "Your critical strikes increase the damage the target takes from you "
    "by 10% for 4 turns.",
    3, 2,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "strike_where_it_hurts",
                           "name": "Strike Where It Hurts",
                           "effect_type": "debuff", "duration": 4,
                           "stat_mods": {"damage_taken_pct": 0.10},
                           "dispel_type": None, "on_target": True}},
    connect=["silent_but_deadly"],
    source="CoA: 'Your ability critical strikes now increase the damage the "
           "target takes from bleeds by 30% for 15 sec.' The bleed scoping "
           "cannot be built - there is no bleed-specific damage-taken key "
           "and bleed_dot_damage is dead data on the caster side - so it "
           "becomes a general damage-taken debuff at 10%. 15 sec -> 4 "
           "turns. CAREFUL: bare damage_taken_pct is read RAW ON BOTH SIDES "
           "(no /100), unlike its physical_ and magic_ siblings, so 0.10 is "
           "10% and authoring 10 would be +1000%. Asserted in main(). Was a "
           "pure scalar on our side."))

N.append(node(
    "hunting_with_precision", "Hunting with Precision",
    "Increases the damage of Hunting Shot by 35% and of Precision Shot by "
    "25%.",
    3, 0,
    effects={"ability_ranger_hunting_shot_damage": 0.35,
             "ability_ranger_precision_shot_damage": 0.25},
    connect=["maximum_power"],
    source="CoA: 'Your Hunting Shot now deals 25% increased damage for each "
           "subsequent target it ricochets to.' Nothing counts how many "
           "targets an ability hit, so the per-target scaling is dropped "
           "and the flat damage raised to 35% to compensate. Extended to "
           "Precision Shot from CoA's New-Age Archery. Hunting Shot "
           "generates 15 Focus, the most of any Ranger ability. Was a pure "
           "scalar on our side."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "maximum_power", "Maximum Power",
    "Increases the damage of your ranged abilities by 8% and your critical "
    "damage by 20%.",
    4, -1,
    effects={"physical_damage": 0.08, "crit_damage_physical": 0.20},
    connect=["one_shot_one_kill"],
    source="CoA: 'Abilities used with 5 stacks of Advantage now refresh the "
           "duration of your active Skirmish by 5 sec.' Unbuildable three "
           "times over: " + ADVANTAGE + " no payload extends a LIVE "
           "effect's duration, and nothing reads whether Skirmish is "
           "active. Rebuilt as the flat damage the node is reached for. "
           "Folded in CoA's shared Sharpshooter passive ('Adds 25% to the "
           "bonuses that your stacks of Advantage provide'), which has "
           "nothing to add to. Both FRACTIONS. Was a pure scalar on our "
           "side."))

N.append(node(
    "corrosive_poison", "Corrosive Poison",
    "Increases your armor penetration by 100.",
    4, 2,
    effects={"armor_penetration": 100},
    connect=["silent_but_deadly"],
    source="CoA: 'Your ranged abilities against Poisoned targets now "
           "ignores 25% of enemy armor.' The condition cannot be built "
           "(nothing reads a target's debuffs) and armor_penetration is "
           "FLAT rather than proportional, so '25% of enemy armor' has no "
           "expressible form - there is no armor_pen_pct key, and "
           "inventing one would have been silent. Built as a flat 100 "
           "rating, unconditional. armor_penetration IS live "
           "(monster.py:659, via _pen_flat). A FLAT RATING, which is why it "
           "looks out of place beside this file's fractions. Was a pure "
           "scalar on our side."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "silent_but_deadly", "Silent, But Deadly",
    "Your ranged attacks have a 20% chance to let your next Deadshot be "
    "used on a target at any health.",
    5, 0,
    proc={"trigger": "on_weapon_swing", "chance": 20, "icd": 2,
          "apply_effect": {"effect_id": "silent_but_deadly",
                           "name": "Silent, But Deadly",
                           "effect_type": "buff", "duration": 3,
                           "stat_mods": {},
                           "proc": {"bypass_execute_threshold": True},
                           "dispel_type": None, "on_target": False}},
    connect=["one_shot_one_kill"],
    source="CoA: 'Direct Physical damage dealt now has an 8% chance to "
           "allow you to use Deadshot regardless of the targets health for "
           "8 seconds.' PORTS VERBATIM, which is rare. "
           "bypass_execute_threshold is a real proc flag read at "
           "abilities.py:1691, and the engine CONSUMES it on use - its own "
           "comment calls it 'a single guaranteed-usable window, not a "
           "permanent ignore-HP state'. Our Deadshot already carries "
           "execute_threshold_pct 20, matching CoA's 'Only usable on "
           "enemies below 20% health' exactly. 8 sec -> 3 turns, 8% -> 20% "
           "with a 2-turn ICD since a swing is rarer than CoA's continuous "
           "auto shots. THE NESTED `proc` INSIDE apply_effect WORKS BUT IS "
           "NOT INSPECTED BY THE AUDIT - without it this applies an empty "
           "buff and does nothing while passing every check - so main() "
           "asserts it. Same shape as Reaper Harvest's Extinction."))

N.append(node(
    "one_shot_one_kill", "One Shot, One Kill",
    "Increases the damage of Deadshot by 75% and your damage against "
    "enemies below 20% health by 20%.",
    5, 2,
    effects={"ability_ranger_deadshot_damage": 0.75,
             "low_health_damage_pct": 0.20,
             "low_health_threshold_pct": 0.20},
    connect=["pierced_quiver"],
    source="CoA: 'Increases the damage of Deadshot by 75%.' PORTS EXACTLY. "
           "The conditional half is added using low_health_damage_pct (the "
           "key added 6 Nov 2026 for the 48 CoA talents across 18 classes "
           "worded that way), and THIS IS THE ONE NODE IN ALL OF RANGER "
           "THAT SETS low_health_threshold_pct: that key SUMS across "
           "talents, is UNSCALED so rank does not divide it, and a "
           "character can spend in several trees of their class. 0.20 is "
           "CoA's own Deadshot threshold, so the whole class's execute "
           "window matches the ability's gate. Brigand's Marked for Death "
           "and Dastardly inherit it rather than setting their own - a "
           "second setter would push the window to 40%, and Tinker once "
           "shipped two summing to 0.8. main() asserts exactly one setter, "
           "and tools/qa_summing_thresholds.py enforces it class-wide. Was "
           "a pure scalar on our side."))

N.append(node(
    "pierced_quiver", "Elven Enchantments",
    "Increases the damage of your Poison and Searing Quivers by 25% and "
    "your periodic damage by a further 10%.",
    5, -2,
    effects={"ability_ranger_poison_quiver_damage": 0.25,
             "ability_ranger_searing_quiver_damage": 0.25,
             "dot_damage": 0.10},
    connect=["hawkeye"],
    source="CoA: 'Increases the damage dealt by your Searing and Poison "
           "Quivers by 25%. In addition, dealing damage with Searing or "
           "Poison Quiver now grants a stack of Elven Enchantments: cast "
           "time of the next Incendiary Shot within 10 sec is reduced by "
           "10% and critical strike chance increased by 10%, stacking 10 "
           "times.' The first clause ports exactly. The second fails three "
           "ways: there are no cast times, " + ADVANTAGE.split('. ')[1] +
           ", and nothing reads whether another effect is active. Replaced "
           "with dot_damage, since both Quivers are damage-over-time "
           "flavours in our data."))

N.append(node(
    "neurotoxin_arrow", "Neurotoxin Arrow",
    "Increases the damage of Neurotoxin Arrow by 30% and reduces the "
    "duration of stuns against you by 25%.",
    1, -4,
    effects={"ability_ranger_neurotoxin_arrow_damage": 0.30,
             "stun_duration_reduction_pct": 0.25},
    connect=["devastating_shots"],
    source="CoA: 'Shoot at an enemy's throat with a toxin-laced arrow, "
           "dealing Nature damage and silencing them for 1 sec. Duration "
           "increased by 1 sec per stack of Advantage.' The ability already "
           "exists in our data. THERE IS NO SILENCE OR INTERRUPT KEY "
           "anywhere in this engine - the same gap that killed Reaper's "
           "Sever and Brigand's Throatpunch - and " + ADVANTAGE.split('. ')[1]
           + ". So the node becomes a damage boost plus the one "
           "crowd-control key that IS read: stun_duration_reduction_pct, "
           "checked solely against is_stun effects "
           "(status_effects.py:699), which inverts CoA's direction but is "
           "the only CC mechanic available. BOTH KEYS ARE FRACTIONS - I "
           "authored stun_duration_reduction_pct as percentage points on "
           "Chronomancer's Timemage and audit_talents caught it as 1000%; "
           "there is no way to infer the convention from the name."))

N.append(node(
    "masterful_archery", "Masterful Archery",
    "Your critical strikes increase the damage of your next shots by 10% "
    "for 3 turns, stacking up to 5 times.",
    4, 0,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "apply_effect": {"effect_id": "masterful_archery",
                           "name": "Masterful Archery",
                           "effect_type": "buff", "duration": 3,
                           "stat_mods": {"damage_dealt_pct": 10},
                           "max_stacks": 5, "dispel_type": None,
                           "on_target": False}},
    connect=["silent_but_deadly"],
    source="CoA: 'While in Elude, gain a stack of Masterful Archery every 2 "
           "sec. Your next Precision Shot now deals 10% increased damage "
           "for 10 seconds, stacking up to 5 times.' The trigger fails "
           "twice - nothing reads whether Elude is active, and there is no "
           "periodic or tick trigger to accrue stacks on a timer - so it "
           "moves to on_crit, which this tree already keys off four times. "
           "CoA's 5 stacks and 10% are kept verbatim and genuinely stack; "
           "only READING the count is impossible, which is why the buff is "
           "general damage rather than Precision-Shot-specific (a status "
           "effect cannot carry a per-ability key). 10 sec -> 3 turns. "
           "damage_dealt_pct is PERCENTAGE POINTS inside a status effect."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "hawkeye", "Hawkeye",
    "Your ranged attacks have a 35% chance to fire a second Quick Shot, "
    "and your periodic damage is increased by 20%.",
    6, 0,
    effects={"dot_damage": 0.20},
    proc={"trigger": "on_weapon_swing", "chance": 35, "icd": 1,
          "cast_ability": "ranger_quick_shot"},
    source="CoA: 'You now fire an arrow every 3 sec at enemies within 30 "
           "yds affected by your Hunting Shot, dealing 75% Ranged Weapon "
           "Damage. Scales with Hunting Shot modifiers.' A repeating timed "
           "arrow cannot be built - there is no periodic or tick trigger of "
           "any kind, " + PERIODIC.split('. ')[1] + " - and nothing reads "
           "which targets carry an effect. Rebuilt as a cast_ability proc "
           "firing Quick Shot, which is the closest live thing to 'an extra "
           "arrow goes out': it costs nothing when it fires and Quick Shot "
           "also generates 12 Focus, so the capstone feeds the rotation "
           "twice over. Quick Shot is ungated, so cast_ability's known "
           "failure mode - it does not check the caster has learned the "
           "ability - cannot bite here. The dot_damage half ties the "
           "capstone to the bleed theme Serrations and Pierced build."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# with flat scalars. spread() preserves the full-investment ceiling, refuses
# unlock nodes and small integer durations, and since 6 Nov 2026 leaves
# UNSCALED_EFFECT_KEYS (low_health_threshold_pct) alone.
from tools.talent_ranks import rankable, spread  # noqa: E402

for _n in TREE["nodes"]:
    if _n["max_points"] < 3 and _n["tier"] < 6 and rankable(_n):
        spread(_n, 3)


def main():
    check = "--check" in sys.argv
    ids = [n["talent_id"] for n in TREE["nodes"]]
    assert len(ids) == len(set(ids)), "duplicate talent_id"
    names = [n["name"] for n in TREE["nodes"]]
    assert len(names) == len(set(names)), "duplicate node NAME"
    for n in TREE["nodes"]:
        for c in n["connected_to"]:
            assert c in ids, f"{n['talent_id']} connects to unknown {c}"

    setters = [n["talent_id"] for n in TREE["nodes"]
               if "low_health_threshold_pct" in (n.get("effects") or {})]
    assert len(setters) == 1, (
        f"low_health_threshold_pct SUMS across talents and is UNSCALED, and "
        f"a character can spend in several Ranger trees - exactly one node "
        f"in the CLASS may set it, and Archery owns it. Found {setters}")

    sbd = next(n for n in TREE["nodes"]
               if n["talent_id"] == "ranger_archery_silent_but_deadly")
    assert (sbd["proc"]["apply_effect"].get("proc", {})
            .get("bypass_execute_threshold")), (
        "Silent, But Deadly IS the bypass_execute_threshold flag - without "
        "the nested proc it applies an empty buff and does nothing at all, "
        "while passing every check in the project (the audit does not "
        "inspect nested procs)")

    for n in TREE["nodes"]:
        proc = n.get("proc") or {}
        gr = proc.get("grant_resource")
        if gr:
            assert gr.get("resource") == "archery_points" and "amount" in gr, (
                f"{n['talent_id']} grant_resource must name archery_points "
                f"(CoA's Focus, Ranger's primary pool) with a FLAT amount")
        mods = (proc.get("apply_effect") or {}).get("stat_mods") or {}
        if "damage_taken_pct" in mods:
            assert -1 < mods["damage_taken_pct"] < 1, (
                f"{n['talent_id']} damage_taken_pct={mods['damage_taken_pct']}"
                f" - read RAW on both sides, so 10 means +1000%")
        for key in ("physical_damage_taken_pct", "magic_damage_taken_pct"):
            if key in mods:
                assert abs(mods[key]) >= 1, (
                    f"{n['talent_id']} {key}={mods[key]} inside a status "
                    f"effect, where it is PERCENTAGE POINTS - a fraction "
                    f"here delivers a hundredth of the intent")

    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Ranger Archery: {len(ids)} nodes, {procs} with procs, {pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
