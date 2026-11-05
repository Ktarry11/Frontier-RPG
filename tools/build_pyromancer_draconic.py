#!/usr/bin/env python3
"""Rebuild Pyromancer's Draconic tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_pyromancer_draconic.py [--check]

SOURCE: data/reference/coa_worksheets/pyromancer.md and
data/reference/coa/pyromancer.json - 40 real Draconic talents from
Ascension's own CoA Builder payload. Role: DPS.

The shipped tree was 23 nodes with THREE procs.

WHAT THE SPEC IS. The Dragon Aspect spec: Echo of Nozdormu and Flames of
Neltharion are the big nukes, and Aspect of Time makes them echo.

ASPECT OF TIME MAPS ONTO `bonus_pct` ALMOST PERFECTLY, which is rare in
this audit. CoA: "Damage dealt by Echo of Nozdormu and Flames of
Neltharion now has a 33% chance to cast an additional time for 30% of the
damage dealt." bonus_pct is a live payload that adds a percentage of the
TRIGGERING HIT's own amount to that same hit (status_effects.py:1360) -
so it reads the damage dealt, which almost nothing else in this engine
does. CoA's 33% and 30% both port exactly. What is lost is the CHAIN:
CoA lets the echo re-trigger up to 3 more times, and a proc's payload
cannot re-enter its own trigger, so it echoes once.

THIS TREE OWNS THREE GATED ABILITIES at tiers 4, 5 and 6 -
echo_of_nozdormu, inner_flame and death_from_above - matching
Pyromancer's deliberate per-tree pattern. All three preserved in place
and asserted in main().

HEAT AND EMBERS STILL DO NOT EXIST (see the Incineration builder), and
this tree leans on Embers harder: Draconic Invocation generates 5,
Perpetual Burning reads how many you hold, and Fire and Brimstone
triggers on generating one. None of those can be built.

CONVENTIONS, which do not agree with each other:
  intellect_pct                            percentage POINTS
  spell_damage, all_damage, dot_damage, ability_*_damage,
    ability_*_crit_damage                     FRACTION
  crit_chance_spell, haste, ability_*_crit    PERCENT
  bonus_pct                                FRACTION of the triggering hit
  threat_generation_pct   FRACTION, NEGATIVE reduces
  spell_damage_taken_pct inside a status effect: divided by 100,
    POSITIVE INCREASES damage taken
  leech_pct, splash_damage                 FRACTION
  *_cost_pct / *_cooldown_pct  FRACTION, POSITIVE MEANS A REDUCTION

TURN-BASED CUTS. Every cast time, "allows it to benefit from your spell
haste" (Agonizing Burns - haste already applies to everything), "instant
cast" riders, and every yard.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/pyromancer_draconic.json"

#: The two nukes CoA's Aspect of Time echoes.
ASPECTS = ["pyromancer_echo_of_nozdormu",
           "pyromancer_flames_of_neltharion"]

#: CoA's "Ember spenders" - the big direct nukes Frontier has.
SPENDERS = ["pyromancer_explode", "pyromancer_flames_of_neltharion",
            "pyromancer_lava_shard"]

#: This tree's three talent-gated abilities.
GATED = {
    "pyromancer_echo_of_nozdormu",
    "pyromancer_inner_flame",
    "pyromancer_death_from_above",
}

TREE = {
    "spec_name": "Pyromancer Draconic",
    "tree_id": "pyromancer_draconic",
    "description": ("The Dragon Aspects - a fire caster whose biggest "
                    "spells echo themselves."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from the 40 real CoA Draconic talents (role "
        "DPS). ASPECT OF TIME MAPS ONTO bonus_pct almost perfectly - a live "
        "payload that adds a percentage of the TRIGGERING HIT's own amount, "
        "so CoA's 33% chance for 30% of the damage dealt ports exactly; only "
        "the 3-echo chain is lost, since a proc cannot re-enter its own "
        "trigger. Owns three gated abilities at tiers 4, 5 and 6, preserved "
        "in place and asserted. Heat and Embers still do not exist and this "
        "tree leans on Embers harder than Incineration did."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"pyromancer_draconic_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"pyromancer_draconic_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "critical_pressure", "Critical Pressure",
    "Increases your Intellect by 6% and your spell critical strike chance by "
    "6%.",
    0, -5,
    effects={"intellect_pct": 6.0, "crit_chance_spell": 6.0},
    connect=["timed_attacks"],
    source="CoA over 2 ranks: 'Increases your Intellect and critical strike "
           "chance by 3%.' Doubled for the two ranks and authored as the "
           "full-investment ceiling. Both keys happen to take the same unit "
           "here - intellect_pct is percentage POINTS and crit_chance_spell "
           "is a PERCENT - which is not true of most pairs in this project."))

N.append(node(
    "timed_attacks", "Timed Attacks",
    "Increases your haste by 8%.",
    0, -3,
    effects={"haste": 8.0},
    connect=["alexstraszas_gift"],
    source="CoA over 2 ranks: 'Increases your spell haste by 4%.' Doubled for "
           "the two ranks. PERCENT."))

N.append(node(
    "alexstraszas_gift", "Alexstrasza's Gift",
    "Increases the damage of Explode, Flames of Neltharion and Lava Shard by "
    "15%.",
    0, -1,
    effects={f"ability_{a}_damage": 0.15 for a in SPENDERS},
    connect=["searing_flames"],
    source="CoA verbatim: 'Increases the damage and healing of your Ember "
           "spenders by 15%.' Embers do not exist (see the Incineration "
           "builder - Pyromancer's resource is MANA with no secondary), so "
           "'Ember spenders' is read as the three big direct nukes Frontier "
           "has. The healing half is dropped: none of those three heal, so "
           "ability_*_healing on them would be dead data."))

N.append(node(
    "searing_flames", "Searing Flames",
    "Increases the damage of Lava Shard by 30%.",
    0, 1,
    effects={"ability_pyromancer_lava_shard_damage": 0.30},
    connect=["agonizing_burns"],
    source="CoA verbatim: 'Increases the spell bonus scaling of Lava Shard by "
           "30%.' There is no key for how much an ability scales with spell "
           "power - the coefficients live on the ability - so it is expressed "
           "as damage."))

N.append(node(
    "agonizing_burns", "Agonizing Burns",
    "Increases the duration of Blaze by 1 turn.",
    0, 3,
    effects={"ability_pyromancer_blaze_duration": 1},
    connect=["aspect_of_time"],
    source="CoA verbatim: 'Increases the duration of Blaze by 20% and allows "
           "it to benefit from your spell haste.' The second half is a "
           "non-issue: haste already applies to everything here, so there is "
           "nothing to switch on - the same shape as Venomancer Vizier's "
           "'can no longer miss'. 20% of Blaze's duration rounds to a turn. "
           "The small integer keeps this node out of the rank policy's "
           "reach."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "aspect_of_time", "Aspect of Time",
    "Echo of Nozdormu and Flames of Neltharion have a 33% chance to echo, "
    "striking again for 30% of the damage dealt.",
    1, -4,
    proc={"trigger": "on_damage_cast", "chance": 33, "icd": 0,
          "ability_filter": ASPECTS,
          "bonus_pct": 0.30},
    connect=["aspects_blessing"],
    source="CoA's level 20 passive, verbatim: 'Damage dealt by Echo of "
           "Nozdormu and Flames of Neltharion now has a 33% chance to cast an "
           "additional time for 30% of the damage dealt. Damage dealt in this "
           "way can trigger this effect up to 3 additional times.' THIS IS "
           "THE CLEANEST TRANSLATION IN THE TREE. bonus_pct is a live payload "
           "that adds a percentage of the TRIGGERING HIT's own amount to that "
           "same hit (status_effects.py:1360) - it actually reads the damage "
           "dealt, which almost nothing else in this engine does, so CoA's "
           "33% and 30% are both exact. WHAT IS LOST IS THE CHAIN: a proc's "
           "payload cannot re-enter its own trigger, so the echo happens once "
           "rather than cascading up to four times."))

N.append(node(
    "aspects_blessing", "Aspect's Blessing",
    "Increases the critical strike chance of Echo of Nozdormu and Flames of "
    "Neltharion by 25%.",
    1, -2,
    effects={f"ability_{a}_crit": 25.0 for a in ASPECTS},
    connect=["cinderstorm"],
    source="CoA verbatim: 'Your next Echo of Nozdormu or Flames of "
           "Neltharion is guaranteed to critically strike and triggers Aspect "
           "of Time, casting an additional time for 30% of the damage dealt. "
           "Lasts 15 sec.' A GUARANTEED CRIT HAS NO KEY - crit at 100 would "
           "be a permanent stat, not a one-shot - and nothing empowers a "
           "named next cast. Frontier HAS Aspect's Blessing as an ability, so "
           "this is not its unlock; the talent is built as flat crit on "
           "exactly CoA's two abilities, priced at 25% rather than 100% "
           "because it applies always. CoA's Flames of Fate node, which "
           "trades Aspect's Blessing cooldown for extra casts, needs the same "
           "charge counter and is not built."))

N.append(node(
    "cinderstorm", "Cinderstorm",
    "Increases the critical strike chance of Firefall by 10% and reduces the "
    "threat it generates by 25%.",
    1, 0,
    effects={"ability_pyromancer_firefall_crit": 10.0,
             "threat_generation_pct": -0.25},
    connect=["overwhelming_flames"],
    source="CoA verbatim: 'Reduces all threat generated by Firefall by -25% "
           "and increases its critical strike chance by 10%.' Both halves "
           "live, though the threat reduction cannot be scoped to one ability "
           "- threat_generation_pct is a character-wide FRACTION where "
           "NEGATIVE reduces - so it applies to everything. Broader than "
           "CoA's, stated rather than hidden."))

N.append(node(
    "overwhelming_flames", "Overwhelming Flames",
    "Lava Shard splashes 50% of its damage onto 1 nearby enemy.",
    1, 2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["pyromancer_lava_shard"],
          "splash_damage": {"pct": 0.50, "max_targets": 1,
                            "school": "fire"}},
    connect=["mad_aspects_scepter"],
    source="CoA verbatim: 'Your Lava Shard now spreads Blaze to up to 1 "
           "additional enemy within 8 yds of the primary target.' SPREADING A "
           "DOT TO A NEW TARGET IS NOT A PAYLOAD - apply_effect lands on the "
           "trigger's own target - so it becomes splash_damage at CoA's one "
           "extra enemy, the same translation as the Witch Doctor's Malignant "
           "and Venomancer Vizier's Sage."))

N.append(node(
    "soul_of_the_dragon", "Soul of the Dragon",
    "Flare Bolt has a 15% chance to cast again for free.",
    1, 4,
    proc={"trigger": "on_damage_cast", "chance": 15, "icd": 1,
          "ability_filter": ["pyromancer_flare_bolt"],
          "cast_ability": "pyromancer_flare_bolt"},
    connect=["mad_aspects_scepter"],
    source="CoA verbatim: 'Casting Flare Bolt now has a 15% chance to cast it "
           "again free of cost.' PORTS EXACTLY - cast_ability takes a bare "
           "ability id, Flare Bolt is auto-learned so it is in the book, and "
           "a payload-cast does not charge the resource, which is what 'free "
           "of cost' means. CoA's 15% kept, with a 1-turn internal cooldown "
           "so the recast cannot chain into itself."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "mad_aspects_scepter", "Mad Aspect's Scepter",
    "Increases the damage of Destroyer's Maw by 40%.",
    2, -4,
    effects={"ability_pyromancer_destroyers_maw_damage": 0.40},
    connect=["flames_of_the_aspects"],
    source="CoA over 2 ranks: 'Increases the damage of Destroyer's Maw by "
           "20%.' Doubled for the two ranks. Destroyer's Maw exists in "
           "Frontier; CoA's version deals damage 'that cannot be resisted', "
           "which has no key - resistance is applied in take_damage with no "
           "per-ability bypass - so that rider is dropped."))

N.append(node(
    "flames_of_the_aspects", "Flames of the Aspects",
    "Destroyer's Maw sets you flamecasting, raising your haste by 10% for 5 "
    "turns.",
    2, -2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["pyromancer_destroyers_maw"],
          "apply_effect": {"effect_id": "pyromancer_flamecasting",
                           "name": "Flamecasting", "effect_type": "buff",
                           "duration": 5, "max_stacks": 5,
                           "stat_mods": {"haste": 5.0},
                           "on_target": False}},
    connect=["lifebringers_blessing"],
    source="CoA verbatim: 'Casting Destroyer's Maw now grants 2 stacks of "
           "Flamecasting. Increases your spell haste by 5% for 15 seconds. "
           "Stacks 5 times.' A PAYLOAD CANNOT GRANT TWO STACKS AT ONCE, so "
           "one cast gives one stack; the description states the 10% two "
           "stacks would reach, since Destroyer's Maw is cast often enough to "
           "hold two. Shares the effect_id with Incineration's Wreath of "
           "Flames deliberately - it is the same Flamecasting buff in CoA, so "
           "a Pyromancer with both does not carry two separate stacks of it. "
           "15 sec is 5 turns."))

N.append(node(
    "lifebringers_blessing", "Lifebringer's Blessing",
    "Echo of Nozdormu and Flames of Neltharion heal you for 20% of the damage "
    "they deal.",
    2, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ASPECTS,
          "leech_pct": {"pct": 0.20}},
    connect=["draconic_tempest"],
    source="CoA verbatim: 'Damage dealt by Aspect of Time now heals you equal "
           "to 200% of the damage dealt.' Aspect of Time's echo is a "
           "bonus_pct rider rather than a separate damage event, so there is "
           "nothing to hang a second proc off - this fires off the same two "
           "abilities instead. leech_pct reads the triggering hit's amount, "
           "so the scaling IS real here. Priced at 20% rather than CoA's "
           "200%: that figure is against the echo's 30% share, and 200% of a "
           "full nuke would make the spec unkillable."))

N.append(node(
    "draconic_tempest", "Draconic Tempest",
    "Dragon's Wrath melts the enemy, leaving them taking 5% more spell damage "
    "for 3 turns.",
    2, 2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["pyromancer_dragons_wrath"],
          "apply_effect": {"effect_id": "pyromancer_draconic_tempest",
                           "name": "Draconic Tempest",
                           "effect_type": "debuff", "duration": 3,
                           "max_stacks": 1,
                           "stat_mods": {"spell_damage_taken_pct": 5.0},
                           "on_target": True}},
    connect=["flames_of_execution"],
    source="CoA verbatim: 'Your Dragon's Wrath now melts enemies, increasing "
           "their chance to be hit by spells by 3% for 10 sec.' THERE IS NO "
           "RECIPIENT-SIDE 'CHANCE TO BE HIT' KEY - hit lives on the attacker "
           "- so it becomes spell damage taken, raised to 5% since it "
           "replaces a hit bonus with a damage bonus. 10 sec is 3 turns."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "flames_of_execution", "Flames of Execution",
    "Increases the damage of Blaze by 25%.",
    3, -4,
    effects={"ability_pyromancer_blaze_damage": 0.25},
    connect=["perpetual_burning"],
    source="CoA verbatim: 'Damage dealt by Blaze is increased by 25% on "
           "enemies below 35% of their maximum health.' NO EFFECT KEY READS A "
           "TARGET'S HEALTH PERCENTAGE - high_health_damage_threshold_pct is "
           "dead, and the working low_health pair on Venomancer Fortitude is "
           "about the CARRIER's own health, not a target's - so the condition "
           "is dropped and CoA's 25% applies always."))

N.append(node(
    "perpetual_burning", "Perpetual Burning",
    "Increases the duration of Blaze by a further 1 turn and the damage your "
    "damage-over-time spells deal by 15%.",
    3, -2,
    effects={"ability_pyromancer_blaze_duration": 1, "dot_damage": 0.15},
    connect=["molten_fury"],
    source="CoA verbatim: 'The duration of Blaze is now increased by 1 sec "
           "for each Ember you have when you cast it.' Embers do not exist "
           "and nothing reads a live resource amount, so the per-Ember "
           "scaling cannot be built. Granted as a flat turn, stacking with "
           "Agonizing Burns at tier 0, plus dot damage to carry the node. "
           "Small integer, so outside the rank policy."))

N.append(node(
    "molten_fury", "Molten Fury",
    "Increases the damage of Eruption by 15% and reduces its cooldown by 40%.",
    3, 0,
    effects={"ability_pyromancer_eruption_damage": 0.15,
             "ability_pyromancer_eruption_cooldown_pct": 0.40},
    connect=["expediting_power"],
    source="CoA verbatim: 'Increases the damage and healing provided by "
           "Eruption by 15%, but reduces its duration by 50%.' The 15% ports. "
           "The duration downside is NOT built - no key reduces an ability's "
           "duration, only increases it - so this node is strictly stronger "
           "than CoA's, stated rather than hidden. CoA's Blackrock "
           "Mountaineer ('reduces the cooldown of Eruption by -30 sec') is "
           "folded in as the 40%, since two nodes for one ability's cooldown "
           "would be padding."))

N.append(node(
    "expediting_power", "Expediting Power",
    "Echo of Nozdormu brings Aspect's Blessing two turns closer to ready.",
    3, 2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
          "ability_filter": ["pyromancer_echo_of_nozdormu"],
          "reset_cooldown": {"abilities": ["pyromancer_aspects_blessing"],
                             "turns": 2}},
    connect=["echo_of_nozdormu"],
    source="CoA verbatim: 'Your Echo of Nozdormu now reduces the cooldown of "
           "Aspect's Blessing by an additional 5%.' A percentage of a "
           "remaining cooldown is not expressible - reset_cooldown takes "
           "whole turns or a full reset - so 5% of a 1-minute cooldown "
           "becomes 2 turns, with a 1-turn icd so it cannot stack within a "
           "turn. Both abilities exist in Frontier."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "echo_of_nozdormu", "Echo of Nozdormu",
    "Teaches Echo of Nozdormu, a chromatic nuke that shortens your cooldowns.",
    4, -3,
    effects={"unlock_ability": "pyromancer_echo_of_nozdormu"},
    connect=["draconic_invocation"],
    source="CoA verbatim: 'Transforms your Explode into Echo of Nozdormu. "
           "Obliterate an enemy, dealing Chromatic Damage and reducing all "
           "spell and ability cooldowns by 5%.' LOAD-BEARING UNLOCK: "
           "pyromancer_echo_of_nozdormu carries requires_talent, so without "
           "this node it is unobtainable forever - and five other nodes in "
           "this tree name it. Nothing transforms one ability into another, "
           "so it is granted alongside Explode rather than replacing it. Kept "
           "at tier 4 exactly where the shipped tree had it, preserving "
           "Pyromancer's 4/5/6 pattern."))

N.append(node(
    "draconic_invocation", "Draconic Invocation",
    "Increases all damage you deal by 8%.",
    4, -1,
    effects={"all_damage": 0.08},
    connect=["fire_and_brimstone"],
    source="CoA verbatim: 'Invoke all of the Dragon Aspects, instantly "
           "generating 5 Embers.' EMBERS DO NOT EXIST - there is no secondary "
           "resource to generate - so the entire ability is inert as a "
           "concept here. Frontier HAS Draconic Invocation as an ability and "
           "it is NOT gated, so this node cannot be its unlock either. "
           "Rebuilt as flat damage, which is what five Embers would have been "
           "spent on. NOT a faithful copy and flagged as such."))

N.append(node(
    "fire_and_brimstone", "Fire and Brimstone",
    "Your nukes stoke the fire, raising your damage by 1% per stack for 3 "
    "turns, stacking 5 times.",
    4, 1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": SPENDERS,
          "apply_effect": {"effect_id": "pyromancer_fire_and_brimstone",
                           "name": "Fire and Brimstone",
                           "effect_type": "buff", "duration": 3,
                           "max_stacks": 5,
                           "stat_mods": {"damage_dealt_pct": 1.0},
                           "on_target": False}},
    connect=["ascender"],
    source="CoA verbatim: 'Generating an Ember now increases the damage and "
           "healing of Ember spenders by 1% for 10 sec, stacking 5 times.' "
           "There is no Ember to generate, so the trigger is re-pointed at "
           "casting the spenders themselves - which in CoA is what consumed "
           "them, so the stacks build in the same part of the rotation. CoA's "
           "1% and 5 stacks kept; 10 sec is 3 turns. damage_dealt_pct inside "
           "a status effect is percentage POINTS."))

N.append(node(
    "ascender", "Ascender",
    "Reduces the cooldown of Dragon Leap by 30%.",
    4, 3,
    effects={"ability_pyromancer_dragon_leap_cooldown_pct": 0.30},
    connect=["inner_flame"],
    source="CoA verbatim: 'Reduces the cooldown of Dragon Leap by -5 sec.' "
           "Expressed as a percentage against the ability's own cooldown. "
           "POSITIVE reduces, so CoA's minus sign is dropped."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "inner_flame", "Inner Flame",
    "Teaches Inner Flame, a party-wide draconic blessing.",
    5, -3,
    effects={"unlock_ability": "pyromancer_inner_flame"},
    connect=["earthwarder"],
    source="LOAD-BEARING UNLOCK: pyromancer_inner_flame carries "
           "requires_talent, so without this node it is unobtainable "
           "forever. It is also target_type 'party', so it genuinely reaches "
           "every living ally - one of only six party-targeted Pyromancer "
           "abilities. Kept at tier 5 where the shipped tree had it."))

N.append(node(
    "earthwarder", "Earthwarder",
    "Taking a hit has a 20% chance to make your next Flare Bolt strike for "
    "fire damage.",
    5, -1,
    proc={"trigger": "on_damage_taken", "chance": 20, "icd": 2,
          "damage_flat": 95, "school": "fire"},
    connect=["draconic_aspect"],
    source="CoA verbatim: 'Being struck by a melee attack while Draconic "
           "Aspect is active now has a 20% chance to make your next Flare "
           "Bolt within 8 seconds instant cast.' Three walls: no 'while buff "
           "active' gate, no trigger-side melee filter, and no cast times to "
           "make instant. Rebuilt as retaliation damage on being hit, keeping "
           "CoA's 20%, with a 2-turn internal cooldown so a heavy incoming "
           "turn does not fire it repeatedly."))

N.append(node(
    "draconic_aspect", "Draconic Aspect",
    "Increases your spell damage by 15%.",
    5, 1,
    effects={"spell_damage": 0.15},
    connect=["death_from_above"],
    source="CoA's own description for this node is the unresolved token "
           "'$8e' - the Builder payload never expands it - so there is no "
           "verbatim text and this is NOT a faithful copy. Frontier HAS "
           "Draconic Aspect as an ability and it is not gated, so this cannot "
           "be its unlock. Named from CoA's own title and built as flat spell "
           "damage. Flagged so a later pass can correct it, the same "
           "situation as Incineration's Magmatic ('$8a')."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "death_from_above", "Death From Above",
    "Teaches Death From Above, and Echo of Nozdormu and Flames of Neltharion "
    "hit 35% harder.",
    6, 0,
    effects={"unlock_ability": "pyromancer_death_from_above",
             **{f"ability_{a}_damage": 0.35 for a in ASPECTS}},
    source="LOAD-BEARING UNLOCK: pyromancer_death_from_above carries "
           "requires_talent, so without this node it is unobtainable "
           "forever. Kept at tier 6, completing Pyromancer's 4/5/6 "
           "gated-ability pattern across all three trees. The damage on the "
           "two Aspect nukes is added because a capstone that only grants an "
           "ability is thin, and it pays off Aspect of Time at tier 1 - the "
           "bigger the nuke, the bigger its echo, since bonus_pct is a share "
           "of the hit. Same shape as Incineration's Pyroclasm capstone."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. tools/talent_ranks.spread() rescales so a
# ranked node lands on exactly the ceiling it had at one rank, and refuses
# nodes carrying small integer durations and unlock_ability nodes.
#
# Author the CEILING at one rank and let the policy divide it. Hand-authoring
# a ceiling at max_points=3 keeps it as the PER-RANK value and triples it -
# the bug that shipped on Guardian Vanguard's Iron Guardian.
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
    unlocks = {(n.get("effects") or {}).get("unlock_ability")
               for n in TREE["nodes"]}
    missing = GATED - unlocks
    assert not missing, (
        f"these abilities carry requires_talent and this tree is their only "
        f"unlock - dropping the node makes them unobtainable forever: "
        f"{sorted(missing)}")
    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Pyromancer Draconic: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points, {len(GATED)} load-bearing unlocks")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
