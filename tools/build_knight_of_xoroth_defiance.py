#!/usr/bin/env python3
"""Rebuild Knight of Xoroth's Defiance tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_knight_of_xoroth_defiance.py [--check]

SOURCE: data/reference/coa_worksheets/knight-of-xoroth.md and
data/reference/coa/knight-of-xoroth.json - 41 real Defiance talents from
Ascension's own CoA Builder payload. Role: Tank.

The shipped tree was 23 nodes with SIX procs - the best-off of Knight of
Xoroth's three. This completes the class.

WHAT THE SPEC IS. An imp-swarm tank. Shieldgore is the threat strike,
Call: Hellfire Imp fills the field, and Sacrificial Circle cashes the
imps in for health. Rage primary, Deathfire secondary.

HELLFIRE RESOLVE PORTS HALF. CoA: "Increases your block rating by 15% of
your Strength and increases your hit rating by 5% of your Strength."
`block` IS in STAT_CONVERSION_TARGETS and strength IS a source, so the
block conversion is real - but HIT_RATING IS NOT A TARGET, the seventh
time in this audit that pairing has cost a node half its text.

NOTHING COUNTS HOW MANY PETS ARE ACTIVE, and that is the spine of this
spec. Four CoA talents scale off the number of live imps: Hellsmelted
Armor ("each Hellfire Imp active increases your block by 1%"), Imp Guards
("each Hellfire Imp reduces your Physical damage taken by 1%"), Implosion
("increases the amount of imps summoned by 1 for each Demonfire
consumed") and Sacrificial Circle ("25% of each imp's maximum health").
There is no pet count readable from a talent or a payload - pets scale
off pet_damage/pet_health/pet_armor and nothing else - so each is granted
at a realistic three-imp value, flat, and says so.

PETS NEVER FIRE PROCS either (no fire_proc_trigger in entities/pet.py),
which takes Hellfire Reprimand entirely - "your Hellfire Imps now have a
20% chance on hit to launch a firebolt" cannot exist at all.

But the pet KEYS are live on this class, unlike most: Knight of Xoroth
genuinely summons three pets. See the Hellfire builder.

THIS TREE OWNS TWO GATED ABILITIES: shieldgore at tier 1 and
call_hellfire_abyssal at tier 6, completing Knight of Xoroth's five.
Both preserved in place and asserted.

CONVENTIONS, which do not agree with each other:
  strength_pct, stamina_pct, armor_pct, attack_power_pct   POINTS
  block                PERCENT, added to BASE_BLOCK_CHANCE and rolled
  block_value_pct      FRACTION on BOTH sides of the talent/status divide
  physical_damage_taken_pct as a TALENT effect: FRACTION, NEGATIVE
    reduces. Inside a status effect: /100 and POSITIVE increases.
  pet_damage, pet_health, pet_armor, ability_*_damage       FRACTION
  spell_damage_taken_pct inside a status effect: /100, POSITIVE increases
  <target>_from_<source>_pct  FRACTION, listed pairs only
  *_cost_pct / *_cooldown_pct  FRACTION, POSITIVE MEANS A REDUCTION

TURN-BASED CUTS. Movement speed (Speed Demon), corpses, every yard, and
"used with 6 Demonfire" conditions (Stoke the Flames) - nothing reads a
live resource amount.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/knight_of_xoroth_defiance.json"

#: The tank's Rage-spending strikes.
STRIKES = ["knight_of_xoroth_infernal_strike", "knight_of_xoroth_meatsaw",
           "knight_of_xoroth_melt"]

#: This tree's talent-gated abilities.
GATED = {"knight_of_xoroth_shieldgore",
         "knight_of_xoroth_call_hellfire_abyssal"}

TREE = {
    "spec_name": "Knight of Xoroth Defiance",
    "tree_id": "knight_of_xoroth_defiance",
    "description": ("Shield and imp-swarm - a demon knight who tanks behind "
                    "a wall of summoned hellfire."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from the 41 real CoA Defiance talents (role "
        "Tank), completing Knight of Xoroth. Hellfire Resolve ports half - "
        "block from Strength is a legal conversion pair, hit_rating is not, "
        "the seventh time that has cost a node. NOTHING COUNTS HOW MANY PETS "
        "ARE ACTIVE and that is the spine of this spec: four CoA talents "
        "scale off live imp count and each is granted at a realistic "
        "three-imp value, flat. Pets never fire procs either, which takes "
        "Hellfire Reprimand entirely. The pet KEYS are live on this class "
        "though - it genuinely summons three pets. Owns shieldgore (t1) and "
        "call_hellfire_abyssal (t6), both gated, both asserted."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"knight_of_xoroth_defiance_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"knight_of_xoroth_defiance_{c}"
                         for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "hellfire_resolve", "Hellfire Resolve",
    "Increases your chance to block by 15% of your Strength and your chance "
    "to hit by 5%.",
    0, -5,
    effects={"block_from_strength_pct": 0.15, "hit_rating": 5.0},
    connect=["hellfire_forgemaster"],
    source="CoA's level 30 passive: 'Increases your block rating by 15% of "
           "your Strength and increases your hit rating by 5% of your "
           "Strength.' THE BLOCK CONVERSION PORTS - `block` is in "
           "STAT_CONVERSION_TARGETS and strength is a source. THE HIT "
           "CONVERSION DOES NOT - hit_rating is not a target, the seventh "
           "time in this audit that pairing has cost a node half its text - "
           "so it is paid as a flat 5%. `block` is a PERCENT added to "
           "BASE_BLOCK_CHANCE and rolled against 0-100; block_chance is a "
           "DEAD key."))

N.append(node(
    "hellfire_forgemaster", "Hellfire Forgemaster",
    "Increases your block value by 20%.",
    0, -3,
    effects={"block_value_pct": 0.20},
    connect=["a_gift_from_hell"],
    source="CoA verbatim: 'Increases your block value by 20%.' Ports "
           "exactly. block_value_pct is read RAW on BOTH sides of the "
           "talent/status divide - a FRACTION either way - unlike "
           "max_health_pct and healing_taken_pct which flip. Authoring 20.0 "
           "would be 2000%, which is what audit_talents caught on Guardian "
           "Vanguard's Iron Barrier earlier today."))

N.append(node(
    "a_gift_from_hell", "A Gift from Hell",
    "Reduces the Rage cost of Infernal Strike, Meatsaw and Melt by 25%.",
    0, -1,
    effects={f"ability_{a}_cost_pct": 0.25 for a in STRIKES},
    connect=["hellsmelted_armor"],
    source="CoA verbatim: 'Reduces the Rage cost of Infernal Strike, Meatsaw, "
           "and Melt by -10.' All three abilities exist in Frontier and Rage "
           "is the class's real primary resource. A flat 10 is expressed as a "
           "percentage because costs differ per rank. POSITIVE reduces, so "
           "CoA's minus sign is dropped."))

N.append(node(
    "hellsmelted_armor", "Hellsmelted Armor",
    "Increases your chance to block by 6%.",
    0, 1,
    effects={"block": 6.0},
    connect=["imp_guards"],
    source="CoA over 2 ranks: 'Each Hellfire Imp active now increases your "
           "chance to block by 1%.' NOTHING COUNTS HOW MANY PETS ARE ACTIVE - "
           "pets scale off pet_damage/pet_health/pet_armor and nothing else, "
           "and no talent effect or payload reads a live pet count. A "
           "realistic field is three imps, so 1% x 3 imps x 2 ranks is 6%, "
           "flat. This is the first of four imp-count talents in this tree; "
           "each says so on its own node."))

N.append(node(
    "imp_guards", "Imp Guards",
    "Reduces the physical damage you take by 6%.",
    0, 3,
    effects={"physical_damage_taken_pct": -0.06},
    connect=["shieldgore"],
    source="CoA's level 20 passive: 'Each Hellfire Imp now reduces your "
           "Physical damage taken by 1%.' Same wall as Hellsmelted Armor - no "
           "live pet count is readable - so three imps at 1% is 3%, doubled "
           "to 6% because this is the spec's level 20 passive and should "
           "carry a node on its own. AS A TALENT EFFECT "
           "physical_damage_taken_pct is a FRACTION where NEGATIVE reduces; "
           "inside a status effect the same key is divided by 100 and "
           "positive INCREASES damage taken."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "shieldgore", "Shieldgore",
    "Teaches Shieldgore, goring the target with your shield for high threat.",
    1, -4,
    effects={"unlock_ability": "knight_of_xoroth_shieldgore"},
    connect=["bulwark_of_xoroth"],
    source="CoA verbatim: 'Transforms your Infernal Strike into Shieldgore. "
           "Generates 2 Demonfire. Gore the target with your spiked shield, "
           "causing High Threat Fire Damage, scaling with your block value.' "
           "LOAD-BEARING UNLOCK: knight_of_xoroth_shieldgore carries "
           "requires_talent, so without this node it is unobtainable forever "
           "- and it is also one of the four abilities that generate "
           "Deathfire (20 per cast), so losing it would cost the spec its "
           "resource engine too. Nothing transforms one ability into another, "
           "so it is granted alongside Infernal Strike. Kept at tier 1."))

N.append(node(
    "bulwark_of_xoroth", "Bulwark of Xoroth",
    "Shieldgore tears the flesh, bleeding the enemy for physical damage over "
    "3 turns.",
    1, -2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["knight_of_xoroth_shieldgore"],
          "apply_effect": {"effect_id": "knight_of_xoroth_torn_flesh",
                           "name": "Torn Flesh", "effect_type": "dot",
                           "duration": 3, "potency": 34,
                           "damage_school": "physical", "on_target": True}},
    connect=["demonfire_retaliation"],
    source="CoA verbatim: 'Damage dealt by Shieldgore will now apply Torn "
           "Flesh, causing the target to bleed for 105 over 15 seconds.' "
           "PORTS CLEANLY - a bleed IS a dot, and 15 sec is 3 turns (held "
           "short so a tank's threat dot is not the longest in the class). "
           "Note the effect is a dot with a physical school rather than "
           "anything named 'bleed': `bleed_dot_damage` is a dead key, "
           "confirmed earlier in this audit when no ability id contained "
           "'bleed'."))

N.append(node(
    "demonfire_retaliation", "Demonfire Retaliation",
    "Being attacked has a 30% chance to grant 10 Deathfire.",
    1, 0,
    proc={"trigger": "on_damage_taken", "chance": 30, "icd": 0,
          "grant_resource": {"resource": "deathfire", "amount": 10}},
    connect=["hellish_rebuke"],
    source="CoA verbatim: 'Grants you a 30% chance to generate a stack of "
           "Demonfire when attacked.' PORTS EXACTLY - on_damage_taken is a "
           "live trigger, CoA's 30% is kept, and DEATHFIRE IS A REAL "
           "SECONDARY RESOURCE (verified through gain_resource on the War "
           "tree). CoA's '1 stack' is 10 here because Frontier's generators "
           "work in tens - Sever grants 10, Infernal Strike 20 - so one CoA "
           "Demonfire is worth roughly ten Deathfire. A tank that makes "
           "resource by being hit is the same loop as Venomancer "
           "Fortitude's Exposed Flesh."))

N.append(node(
    "hellish_rebuke", "Hellish Rebuke",
    "Being attacked has a 15% chance to erupt, splashing fire onto nearby "
    "enemies.",
    1, 2,
    proc={"trigger": "on_damage_taken", "chance": 15, "icd": 1,
          "damage_flat": 80, "school": "fire"},
    connect=["warden_of_hellfire"],
    source="CoA verbatim: 'Generating a stack of Demon's Blood now has a 15% "
           "chance to trigger a fiery explosion on up to 5 nearby enemies, "
           "dealing Fire damage.' NO TRIGGER FIRES WHEN A RESOURCE IS "
           "GENERATED - there is no on-resource-gain hook - so it hangs off "
           "the same on_damage_taken that Demonfire Retaliation above uses, "
           "which is what generates the stack in practice. The two fire "
           "together, exactly as CoA intends. CoA's 15% kept; 1-turn icd."))

N.append(node(
    "warden_of_hellfire", "Warden of Hellfire",
    "Increases the damage of Skulltaker and Flames of Xoroth by 20%.",
    1, 4,
    effects={"ability_knight_of_xoroth_skulltaker_damage": 0.20,
             "ability_knight_of_xoroth_flames_of_xoroth_damage": 0.20},
    connect=["imp_gang_boss"],
    source="CoA verbatim: 'Increases the damage dealt by Skulltaker and "
           "Flames of Xoroth by 20%.' Ports exactly - both exist in "
           "Frontier."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "imp_gang_boss", "Imp Gang Boss",
    "Increases the damage and health of your imps by 40%.",
    2, -4,
    effects={"pet_damage": 0.40, "pet_health": 0.40},
    connect=["impcaller"],
    source="CoA verbatim: 'Your Call: Hellfire Imp now summons 2 additional "
           "imps.' NO KEY CHANGES HOW MANY PETS AN ABILITY SUMMONS - the "
           "count lives on the ability - so two more imps cannot be bought. "
           "Re-pointed at pet_damage and pet_health, which is a stronger "
           "swarm rather than a bigger one. THE KEYS ARE LIVE HERE because "
           "this class genuinely summons three pets; the same node on the "
           "Witch Doctor or Venomancer would have been dead data (see "
           "tools/qa_pet_keys.py)."))

N.append(node(
    "impcaller", "Impcaller",
    "Infernal Strike has a 25% chance to call a Hellfire Imp to your\n"
    "side, once every 2 turns.",
    2, -2,
    proc={"trigger": "on_damage_cast", "chance": 25, "icd": 2,
          "ability_filter": ["knight_of_xoroth_infernal_strike"],
          "cast_ability": "knight_of_xoroth_call_hellfire_imp"},
    connect=["hellfire_imp_mastery"],
    source="CoA verbatim: 'Transforms your Call: Hellfire Imp into Impcaller. "
           "Your Infernal Strike now summons a Hellfire Imp to aid you in "
           "combat for 10 seconds, but its Rage cost is increased by 10. In "
           "addition, the maximum health of your imps is increased by 30%.' "
           "THE SUMMON HALF PORTS - cast_ability takes a bare ability id, and "
           "Call: Hellfire Imp is auto-learned (not requires_talent), so it "
           "is in the book and can be cast by a payload. Held to 25% with a "
           "2-turn icd rather than every strike, since a free imp per cast "
           "would swarm the field. No key ADDS a cost, so CoA's downside "
           "cannot be charged."))

N.append(node(
    "hellfire_imp_mastery", "Hellfire Legion",
    "Increases the health and armour of your imps by a further 30%.",
    2, 0,
    effects={"pet_health": 0.30, "pet_armor": 0.30},
    connect=["sacrificial_circle"],
    source="CoA's Impcaller carries '+30% maximum health of your imps' as its "
           "third clause, which does not fit on the Impcaller node once that "
           "node is a proc - so it is split out here with armour alongside. "
           "CoA's 30% kept. NOT a separate CoA talent and flagged as such; it "
           "is the remainder of one."))

N.append(node(
    "sacrificial_circle", "Sacrificial Circle",
    "Increases the healing of Sacrificial Circle by 50% and reduces its "
    "cooldown by 25%.",
    2, 2,
    effects={"ability_knight_of_xoroth_sacrificial_circle_healing": 0.50,
             "ability_knight_of_xoroth_sacrificial_circle_cooldown_pct": 0.25},
    connect=["soul_furnace"],
    source="CoA verbatim: 'Sacrifice your Hellfire Imps within 15 yds, "
           "healing you 15% of your maximum health, plus an additional amount "
           "equal to 25% of each of your Hellfire Imp's maximum health.' "
           "Frontier HAS Sacrificial Circle and it is not gated. The "
           "per-imp scaling needs a live pet count, which nothing reads, so "
           "it lives on the ability's own coefficients; the talent makes the "
           "whole thing bigger and more frequent instead. Corpses are not "
           "modelled."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "soul_furnace", "Soul Furnace",
    "Sacrificial Circle shields you for 20% of the healing it does.",
    3, -4,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": ["knight_of_xoroth_sacrificial_circle"],
          "shield_pct": 0.20},
    connect=["demons_breath"],
    source="CoA verbatim: 'Sacrificial Circle now grants you a damage "
           "absorption shield equal to 15% of the total health of each "
           "destroyed imp for 10 sec.' The per-imp scaling needs a pet count "
           "nothing reads, but shield_pct IS a live payload that converts a "
           "share of the triggering HEAL into an absorb - and Sacrificial "
           "Circle is a heal, so the shield scales off something real. A "
           "FRACTION."))

N.append(node(
    "demons_breath", "Demon's Breath",
    "Your critical strikes with Shieldgore erupt for fire damage and grant 10 "
    "Deathfire.",
    3, -2,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "ability_filter": ["knight_of_xoroth_shieldgore"],
          "damage_flat": 90, "school": "fire",
          "grant_resource": {"resource": "deathfire", "amount": 10}},
    connect=["infernal_bulwark"],
    source="CoA verbatim: 'Critical strikes with Shieldgore now unleash an "
           "eruption of hellfire, causing Fire damage and generating 1 "
           "additional Demonfire.' PORTS WHOLE - a proc can carry BOTH a "
           "damage_flat payload and a grant_resource, so both halves of CoA's "
           "text fire from one node. CoA's '1 Demonfire' is 10 Deathfire, "
           "matching Frontier's tens-based generators."))

N.append(node(
    "infernal_bulwark", "Infernal Bulwark",
    "Unleash Pestilence raises your block value by 20% for 6 turns.",
    3, 0,
    proc={"trigger": "on_cast", "chance": 100, "icd": 0,
          "ability_filter": ["knight_of_xoroth_unleash_pestilence"],
          "apply_effect": {"effect_id": "knight_of_xoroth_infernal_bulwark",
                           "name": "Infernal Bulwark", "effect_type": "buff",
                           "duration": 6, "max_stacks": 1,
                           "stat_mods": {"block_value_pct": 0.20},
                           "on_target": False}},
    connect=["stoke_the_flames"],
    source="CoA verbatim: 'Casting Unleash Pestilence now generates 4 stacks "
           "of Demonfire and grants Infernal Bulwark. Increases block value by "
           "20% for 18 sec.' The block buff ports exactly - CoA's 20%, and 18 "
           "sec is 6 turns. A proc carries ONE grant_resource and this one "
           "spends it on the buff, so the 4 Demonfire is dropped; two other "
           "nodes in this tree already grant Deathfire. BLOCK_VALUE_PCT IS "
           "READ RAW inside a status effect as well as outside, so 20% is "
           "0.20 - the flip that audit_talents caught on Guardian Vanguard."))

N.append(node(
    "stoke_the_flames", "Stoke the Flames",
    "Increases the damage of Skulltaker and Melt by 30%.",
    3, 2,
    effects={"ability_knight_of_xoroth_skulltaker_damage": 0.30,
             "ability_knight_of_xoroth_melt_damage": 0.30},
    connect=["implosion"],
    source="CoA verbatim: 'Your Skulltaker and Melt used with 6 Demonfire now "
           "refund 2 Demonfire. Skulltaker used with 6 Demonfire now deals an "
           "additional 30% Fire damage.' NOTHING READS A LIVE RESOURCE AMOUNT, "
           "so 'used with 6 Demonfire' cannot gate anything and the refund "
           "cannot be conditioned. CoA's 30% is granted unconditionally on "
           "both abilities."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "implosion", "Implosion",
    "Increases the damage of Implosion by 40% and reduces its cooldown by "
    "25%.",
    4, -3,
    effects={"ability_knight_of_xoroth_implosion_damage": 0.40,
             "ability_knight_of_xoroth_implosion_cooldown_pct": 0.25},
    connect=["hellfire_reprimand"],
    source="CoA verbatim: 'Explode with hellish fire, dealing Fire damage to "
           "nearby enemies, beckoning Hellfire Imps to aid you in battle for "
           "12 sec, and generating 30 Rage. Deals increased damage and "
           "increases the amount of imps summoned by 1 for each Demonfire "
           "consumed.' Frontier HAS Implosion and it is not gated. The "
           "per-Demonfire scaling needs a live resource read and the imp "
           "count lives on the ability, so neither is buildable. CoA's "
           "Demonfire Command ('reduces the cooldown of Implosion by -10 sec "
           "and its Rage cost by -5') is folded in as the 25% rather than "
           "built as a second node for one ability's cooldown."))

N.append(node(
    "hellfire_reprimand", "Hellfire Reprimand",
    "Your strikes leave the enemy dealing 15% less damage for 3 turns.",
    4, -1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": STRIKES,
          "apply_effect": {
              "effect_id": "knight_of_xoroth_hellfire_reprimand",
              "name": "Hellfire Reprimand", "effect_type": "debuff",
              "duration": 3, "max_stacks": 1,
              "stat_mods": {"damage_dealt_pct": -15.0},
              "on_target": True}},
    connect=["brimstone_knight"],
    source="CoA verbatim: 'Your Hellfire Imps now have a 20% chance on hit to "
           "launch a firebolt dealing Fire damage and reducing enemy attack "
           "power for 10 sec.' PETS NEVER FIRE PROCS - there is no "
           "fire_proc_trigger anywhere in entities/pet.py - so an imp cannot "
           "have a chance-on-hit at all, which makes this talent unbuildable "
           "as written. Re-pointed at the Knight's own strikes carrying the "
           "attack-power debuff, which is the mitigation the firebolts bought "
           "a tank. 10 sec is 3 turns. damage_dealt_pct inside a status "
           "effect is percentage POINTS."))

N.append(node(
    "brimstone_knight", "Brimstone Knight",
    "Increases your spell damage by 3%, and your strikes leave the enemy "
    "taking 10% more spell damage for 5 turns.",
    4, 1,
    effects={"spell_damage": 0.03},
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": STRIKES,
          "apply_effect": {
              "effect_id": "knight_of_xoroth_brimstone_knight",
              "name": "Brimstone Knight", "effect_type": "debuff",
              "duration": 5, "max_stacks": 1,
              "stat_mods": {"spell_damage_taken_pct": 10.0},
              "on_target": True}},
    connect=["speed_demon"],
    source="CoA verbatim: 'Increases your Fire damage dealt by 3% and dealing "
           "Fire damage increases the enemy spell damage taken by 10% for 15 "
           "sec.' BOTH HALVES PORT, with the per-school scoping dropped (no "
           "per-school damage key, and no trigger-side school filter - "
           "proc['school'] only types a damage_flat payload). CoA's 3% and "
           "10% both kept; 15 sec is 5 turns."))

N.append(node(
    "speed_demon", "Speed Demon",
    "Increases your haste by 10%.",
    4, 3,
    effects={"haste": 10.0},
    connect=["call_hellfire_abyssal"],
    source="CoA verbatim: 'Your Suffuse now increases your movement speed by "
           "20%.' MOVEMENT SPEED IS NOT MODELLED and there is no 'while "
           "Suffuse is active' gate either. Rerouted to haste, which is what "
           "speed means in a turn-based fight - acting more often. NOT a "
           "faithful copy and flagged as such, the same treatment as Templar "
           "Crusader's Whirling Tempest."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "demonic_fortitude", "Demonic Fortitude",
    "Increases your Stamina by 12% and your armour by 15%.",
    5, -3,
    effects={"stamina_pct": 12.0, "armor_pct": 15.0},
    connect=["call_hellfire_abyssal"],
    source="Built from CoA's Hellsmelted Armor and Imp Guards themes - both "
           "of which lost their per-imp scaling - so tier 5 carries a real "
           "tank stat node. NOT a port of a specific CoA talent and flagged "
           "as such. Both keys take percentage POINTS."))

N.append(node(
    "legions_presence", "Legion's Presence",
    "Increases the threat you generate by 30% and reduces the physical damage "
    "you take by a further 8%.",
    5, -1,
    effects={"threat_generation_pct": 0.30,
             "physical_damage_taken_pct": -0.08},
    connect=["call_hellfire_abyssal"],
    source="Frontier HAS Legion's Presence as a target_type 'party' ability - "
           "the class's only party-targeted one - and it is not gated, so "
           "this is not its unlock. Built as the threat and mitigation a tank "
           "capstone tier wants, stacking with Imp Guards at tier 0 for 14% "
           "physical reduction on a full Defiance build. threat_generation_pct "
           "is a FRACTION where POSITIVE increases, the opposite polarity to "
           "the _cost_pct family beside it."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "call_hellfire_abyssal", "Call: Hellfire Abyssal",
    "Teaches Call: Hellfire Abyssal, and your demons hit 40% harder.",
    6, 0,
    effects={"unlock_ability": "knight_of_xoroth_call_hellfire_abyssal",
             "pet_damage": 0.40},
    source="LOAD-BEARING UNLOCK: knight_of_xoroth_call_hellfire_abyssal "
           "carries requires_talent, so without this node it is unobtainable "
           "forever. It completes Knight of Xoroth's five gated abilities - "
           "Gore and Brimstone Bludgeon in War, Hellmaw in Hellfire, "
           "Shieldgore and this in Defiance - and main() asserts both of this "
           "tree's. The pet damage is added because a capstone granting only "
           "an ability is thin, and it pays off the swarm the whole tree "
           "builds: with Imp Gang Boss and Hellfire Legion it reaches 80% pet "
           "damage on a full Defiance build. The key is live because this "
           "class really summons."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. tools/talent_ranks.spread() rescales so a
# ranked node lands on exactly the ceiling it had at one rank, and refuses
# nodes carrying small integer durations and unlock_ability nodes.
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
    print(f"Knight of Xoroth Defiance: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points, {len(GATED)} load-bearing unlocks")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
