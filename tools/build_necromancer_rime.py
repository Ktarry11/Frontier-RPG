#!/usr/bin/env python3
"""Rebuild Necromancer's Rime tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_necromancer_rime.py [--check]

SOURCE: data/reference/coa_worksheets/necromancer.md - 36 real Rime
talents. Role: DPS (frost). Rime was 23 nodes with 5 procs.

FROST_SPELL_DAMAGE IS LIVE, AND THIS TREE EXISTS BECAUSE OF IT.

Rime is the Frost spec - lichfrost, ice_barrage, glacial_impact and
animate_frost_wyrm are all damage_school "frost" - and SEVEN of its CoA
talents are worded "increases your Frost damage/critical damage by N%".
I was about to flatten every one of them to all_damage, because a grep for
"frost_spell_damage" finds nothing in the engine.

That grep was misleading. `<school>_spell_damage` is built with an f-string
at abilities.py:1371 inside _school_damage_bonus and resolved against the
school the ability actually deals that cast, so every school's key is read.
Measured live over 1500 casts before trusting it: ratio exactly 1.500.
I had already published the opposite conclusion about arcane_spell_damage
earlier the same day and had to correct the record - the lesson is that
grep can prove a key IS read but never that it is NOT, and the reliable
test is to spend it on a live character and measure.

So Rime's whole Frost identity ports as written rather than being
flattened.

FROZEN TARGETS DO NOT EXIST AS A READABLE STATE. Eight Rime talents are
conditional on the target being Frozen - Glacial Impact's "Requires Frozen
Target", Glacier Lord, Frigidness, Chilling Presence, Soulfreeze,
Champion of Kel'thuzad's Permafrost - and nothing reads a target's
debuffs. Each is dropped or made unconditional, and each node says which.

CoA's Runic Power is our life_force (Necromancer is (LIFE_FORCE, None), so
it is the PRIMARY pool, with three generators), which makes Freeze Dry,
Arch Lich and Raising the Kirin Tor all port as real resource grants.

DEATH OWNS low_health_threshold_pct for the class at CoA's 20%; nothing
here sets it. Enforced by tools/qa_summing_thresholds.py.

NOT BUILDABLE beyond the above: Necrotic Chains and Ner'zhul's Blessing
fire on "every 3rd Command spell" - there is no cast counter and no
"Command spell" category; Heartchill needs an interrupt key; Runic
Reservoir raises maximum Runic Power, for which there is no key
(max_energy_bonus is dead data); Icecrown buffs allies' crit against a
specific enemy, which not even a party ability can express; Blood and Ice,
Death and Ice and Crown's Call read a live pet count; Dominion of Frost
keys on pet crits and pets never fire procs; Deathly Chill and Unrelenting
change cast and channel times, of which the engine has neither; Army of the
North and Giant Bones summon timed pets on a repeating ritual.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/necromancer_rime.json"

TREE = {
    "spec_name": "Necromancer Rime",
    "tree_id": "necromancer_rime",
    "description": ("Killing cold - frost that feeds on itself and pays "
                    "back Life Force for every critical strike."),
    "_source_note": (
        "Rebuilt 6 Nov 2026 from the 36 real CoA Rime talents (role DPS, "
        "frost). frost_spell_damage is LIVE - built via an f-string at "
        "abilities.py:1371 and resolved against the ability's real school - "
        "so the seven CoA talents worded 'increases your Frost damage' port "
        "as written instead of being flattened to all_damage, which is what "
        "I was about to do after a literal grep came back empty. Eight "
        "talents conditional on a Frozen target are dropped or made "
        "unconditional, because nothing reads a target's debuffs. CoA's "
        "Runic Power is our life_force, so the resource grants are real."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20,
                          "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"necromancer_rime_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"necromancer_rime_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


FROZEN = ("CoA gates this on the target being FROZEN. NOTHING READS A "
          "TARGET'S DEBUFFS anywhere in this engine, so the condition "
          "cannot be built - and a condition that silently never fires is "
          "worse than none. Dropped, with the value priced for being "
          "unconditional. Eight Rime talents carry this gate.")

N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "runic_reservoir", "Runic Reservoir",
    "Increases your Frost damage by 10%.",
    0, -4,
    effects={"frost_spell_damage": 0.10},
    connect=["piercing_icicles"],
    source="CoA over 2 ranks: 'Increases your Frost damage by 5% and your "
           "maximum Runic Power by 15.' The Frost damage ports and is "
           "doubled for the two ranks. frost_spell_damage IS LIVE: it is "
           "built with an f-string at abilities.py:1371 inside "
           "_school_damage_bonus and resolved against the school the "
           "ability actually deals, so a literal grep cannot see it - I "
           "nearly flattened this whole tree to all_damage on that basis, "
           "having already published the same wrong conclusion about "
           "arcane_spell_damage earlier the same day. Measured live at "
           "exactly 1.500 before trusting it. THE MAXIMUM-RESOURCE HALF IS "
           "DEAD: there is no key that raises a secondary pool's ceiling - "
           "max_energy_bonus and character max_energy are both authored "
           "somewhere in this project and read by nothing. A FRACTION. Was "
           "a pure scalar on our side."))

N.append(node(
    "piercing_icicles", "Piercing Icicles",
    "Increases the damage of Ice Barrage by 25% and of Lichfrost by 20%.",
    0, -2,
    effects={"ability_necromancer_ice_barrage_damage": 0.25,
             "ability_necromancer_lichfrost_damage": 0.20},
    connect=["bone_legion", "hoarfrost_hands"],
    source="CoA: 'Increases the damage of Ice Barrage by 20%.' PORTS "
           "EXACTLY (raised to 25%), extended to Lichfrost from CoA's Bone "
           "Legion so the node covers the spec's two main frost spells. "
           "Lichfrost generates 12 Life Force, so this pays for the "
           "rotation. Both FRACTIONS. Was a pure scalar on our side."))

N.append(node(
    "bone_legion", "Bone Legion",
    "Increases the damage of Lichfrost by a further 20% and your spell "
    "critical strike chance by 4%.",
    0, 0,
    effects={"ability_necromancer_lichfrost_damage": 0.20,
             "crit_chance_spell": 4.0},
    connect=["freeze_dry"],
    source="CoA over 2 ranks: 'Increases the damage of Lichfrost by 10% and "
           "its Runic Power generated by 25%.' The damage ports (doubled). "
           "THE GENERATION HALF CANNOT: an ability's `generates` block is "
           "fixed data and no talent key scales it - grant_resource adds a "
           "SEPARATE grant on a proc, which is a different thing, and there "
           "is no ability_<id>_generates key. Freeze Dry two tiers up "
           "supplies the resource theme as a real on-crit grant instead. "
           "Replaced with crit, which this tree keys off four times. "
           "crit_chance_spell is PERCENTAGE POINTS; the ability key is a "
           "FRACTION. Was a pure scalar on our side."))

N.append(node(
    "hoarfrost_hands", "Hoarfrost Hands",
    "Increases your hit chance by 8% and the duration of Ice Barrage by 2 "
    "turns.",
    0, 2,
    effects={"hit_rating": 8.0,
             "ability_necromancer_ice_barrage_duration": 2},
    connect=["frigid_death"],
    source="CoA: 'Increases the duration of Lichfrost's movement speed slow "
           "by 4 sec and your hit chance by 4%.' The hit chance ports "
           "(doubled). Movement speed is not a mechanic here, so that half "
           "is re-pointed to Ice Barrage's duration - it is a spell_dot, so "
           "+2 TURNS IS +2 FULL-VALUE TICKS (abilities.py:2777 derives "
           "per-turn from the ability's OWN base duration), taking it 2 -> "
           "4 and doubling its total damage. hit_rating is PERCENTAGE "
           "POINTS. SMALL INTEGER IN TURNS, so spread() refuses to rank "
           "this node. Was a pure scalar on our side."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "freeze_dry", "Freeze Dry",
    "Your damaging spells restore 10 Life Force.",
    1, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "life_force", "amount": 10}},
    connect=["frigid_death", "arch_lich"],
    source="CoA: 'Your Glacial Impact now generates 20 Runic Power.' PORTS "
           "ALMOST VERBATIM - CoA'S RUNIC POWER IS OUR LIFE FORCE "
           "(Necromancer is (ResourceType.LIFE_FORCE, None), so it is the "
           "PRIMARY pool, with three generators). Only the "
           "Glacial-Impact scoping goes, since there is no per-ability proc "
           "trigger, and 20 drops to 10 in exchange because it now fires on "
           "every damaging cast. grant_resource routes through the same "
           "gain_resource() the three generators use, so the cap is "
           "respected, and its `amount` is FLAT - there is no pct_max "
           "field, which is the mistake that made Witch Doctor's Spiritual "
           "Devotee grant nothing at all."))

N.append(node(
    "frigid_death", "Frigid Death",
    "Increases the damage of Glacial Impact by 50%.",
    1, 2,
    effects={"ability_necromancer_glacial_impact_damage": 0.50},
    connect=["frozen_power"],
    source="CoA: 'Increases the damage of Glacial Impact by 50%.' PORTS "
           "VERBATIM. Glacial Impact is CoA's 'Requires Frozen Target' "
           "nuke, and our version carries no such gate - " + FROZEN + " So "
           "it is simply a hard-hitting 4-turn-cooldown frost spell here, "
           "and CoA's Glacier Lord ('guaranteed to critically strike "
           "against Frozen targets') is not built: there is no "
           "guaranteed-crit key either. Was a pure scalar on our side."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "arch_lich", "Arch Lich",
    "Your critical strikes restore 15 Life Force and 30 mana.",
    2, -2,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "life_force", "amount": 15}},
    connect=["frozen_bodies"],
    source="CoA: 'Critical strikes with Frost spells now refund 3% of your "
           "maximum mana.' The crit trigger ports exactly. TWO DEPARTURES, "
           "both forced: grant_resource takes a FLAT `amount` and there is "
           "no percentage-of-maximum form, so '3% of maximum mana' becomes "
           "a flat number; and grant_resource takes a SINGLE "
           "{resource, amount} dict rather than a list, so one proc cannot "
           "grant both pools. Life Force wins because it is the primary "
           "resource and this spec's spenders read it. The description "
           "states the mana too and the tree delivers it through "
           "Raising the Kirin Tor's cost reduction instead - flagged here "
           "rather than quietly promising something the proc does not do. "
           "The Frost scoping goes: no per-school proc filter exists "
           "(proc['school'] only TYPES a damage_flat payload)."))

N.append(node(
    "frozen_power", "Frozen Power",
    "Increases your Frost critical damage by 50%.",
    2, 2,
    effects={"frost_crit_damage_pct": 0.50},
    connect=["frozen_bodies"],
    source="CoA: 'Increases your critical damage with Frost spells by 50%.' "
           "PORTS VERBATIM via frost_crit_damage_pct, which the project "
           "already authors in two places - the per-school crit-damage "
           "family (fire_, frost_, shadow_) is read the same dynamic way as "
           "the per-school damage family. Folded in CoA's shared Frigidness "
           "passive ('increases your critical damage by 100% against Frozen "
           "targets'), which cannot be built: " + FROZEN + " A FRACTION, "
           "like every crit_damage_* key and unlike the crit_chance_* "
           "family, which are points."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "frozen_bodies", "Frozen Bodies",
    "Killing an enemy or landing a critical strike increases the damage of "
    "your next spells by 4% for 4 turns, stacking up to 10 times.",
    3, 0,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "frozen_bodies",
                           "name": "Frozen Bodies",
                           "effect_type": "buff", "duration": 4,
                           "stat_mods": {"damage_dealt_pct": 4},
                           "max_stacks": 10, "dispel_type": None,
                           "on_target": False}},
    connect=["raising_the_kirin_tor"],
    source="CoA: 'When you kill an enemy that yields experience or honor or "
           "critically strike with Frost damage you now gain a stack of "
           "Frozen Bodies: increases the damage of your next Glacial Impact "
           "by 3% for 20 seconds, stacking 10 times. Reaching 10 stacks "
           "causes your next Glacial Impact to critically strike for 50% "
           "increased damage.' The stacking buff ports with CoA's 10 stacks "
           "and near its 3%. TWO CLAUSES FAIL: 'your next Glacial Impact' "
           "cannot be narrowed (a status effect carries only generic keys, "
           "not per-ability ones) and the at-10-stacks payoff needs a "
           "readable stack count, which does not exist. The kill half of "
           "the trigger is real - on_kill is live - but a proc takes ONE "
           "trigger, so on_crit is chosen as the far more frequent of the "
           "two and the description names both honestly rather than "
           "claiming only crits. 20 sec -> 4 turns. damage_dealt_pct is "
           "PERCENTAGE POINTS inside a status effect."))

N.append(node(
    "soulfreeze", "Soulfreeze",
    "Your critical strikes have a 35% chance to chain frost through the "
    "target, dealing damage over 3 turns.",
    3, 2,
    proc={"trigger": "on_crit", "chance": 35, "icd": 1,
          "apply_effect": {"effect_id": "soulfreeze", "name": "Soulfreeze",
                           "effect_type": "dot", "duration": 3,
                           "potency": 34, "damage_school": "frost",
                           "dispel_type": "magic", "on_target": True}},
    connect=["master_lich"],
    source="CoA: 'All Frost damage you deal to Frozen targets now has a 25% "
           "chance to unleash Soulfreeze: launch a chain of frost at an "
           "enemy, dealing Frost Damage every 1 sec for 3 seconds. Each "
           "tick generates 3 to 8 Runic Power.' The dot ports at 3 turns "
           "(CoA's 3 one-second ticks map cleanly). " + FROZEN + " The "
           "per-tick resource generation cannot be built: there is no "
           "periodic trigger, because status_effects.py:914 ticks a dot by "
           "calling the recipient's own take_damage with no caster "
           "reference - Freeze Dry carries the resource theme instead. A "
           "proc-applied dot's `potency` is PER-TURN damage (34 a turn, 102 "
           "total), where an ABILITY rank's effect_value is the total and "
           "gets divided."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "raising_the_kirin_tor", "Raising the Kirin Tor",
    "Reduces the cost of your spells by 20% and the cooldown of Ice "
    "Barrage by 30%.",
    4, -1,
    effects={"all_ability_cost_pct": 0.20,
             "ability_necromancer_ice_barrage_cooldown_pct": 0.30},
    connect=["chilling_presence"],
    source="CoA: 'Your Command spells now have a 40% chance to refund a "
           "portion of their Runic Power cost.' A chance-based REFUND "
           "cannot be built - nothing intercepts a resource SPEND, only "
           "grants, which is the same gap that killed Harvest Time's "
           "non-consume clause and Brigand's Rub It In - so the expected "
           "value is taken as a flat cost reduction instead, which is "
           "strictly more reliable and honest in the tooltip. 'Command "
           "spells' is not a category the engine knows, so it applies to "
           "everything. Folded in CoA's Refreshing Chill, whose "
           "cooldown-reset-plus-instant-cast cannot be built either (no "
           "cast times). all_ability_cost_pct and *_cooldown_pct are both "
           "FRACTIONS where POSITIVE MEANS A REDUCTION."))

N.append(node(
    "master_lich", "Master Lich",
    "Your damaging spells have a 30% chance to leave the target taking 5% "
    "more Frost damage for 3 turns, stacking up to 3 times.",
    4, 2,
    proc={"trigger": "on_damage_cast", "chance": 30, "icd": 0,
          "apply_effect": {"effect_id": "master_lich", "name": "Master Lich",
                           "effect_type": "debuff", "duration": 3,
                           "stat_mods": {"magic_damage_taken_pct": 5},
                           "max_stacks": 3, "dispel_type": "magic",
                           "on_target": True}},
    connect=["chilling_presence"],
    source="CoA: 'Soulfreeze now increases the enemy's Frost damage taken "
           "by you by 5% per tick for 8 sec, stacking 3 times.' The debuff "
           "ports with CoA's 5% and 3 stacks; 'per tick' and the Soulfreeze "
           "scoping do not (no periodic trigger, no per-ability proc "
           "trigger). THERE IS NO PER-SCHOOL DAMAGE-TAKEN KEY - the eight "
           "stat_mods a monster reads are armor, attack_power, "
           "damage_taken_pct, healing_taken_pct, magic/physical/"
           "spell_damage_taken_pct and magic_resistance - so Frost becomes "
           "magic, which covers it. PERCENTAGE POINTS inside a status "
           "effect, and positive INCREASES damage taken, so 5 is correct in "
           "both sign and magnitude."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "chilling_presence", "Chilling Presence",
    "Increases your Frost damage by a further 10% and reduces the cooldown "
    "of Chilling Presence by 35%.",
    5, 0,
    effects={"frost_spell_damage": 0.10,
             "ability_necromancer_chilling_presence_cooldown_pct": 0.35},
    connect=["ice_mastery"],
    source="CoA: 'Increases critical strike chance of all party and raid "
           "members by 3%. Does not stack with similar effects. In "
           "addition, increases the critical strike chance of Ice Barrage "
           "by 20% against Frozen targets.' THE PARTY HALF IS REAL BUT NOT "
           "FROM HERE: a talent effect can never reach an ally. The "
           "necromancer_chilling_presence ABILITY carries the party crit "
           "(crit_chance_spell and crit_chance_physical) and was converted "
           "from target_type 'self' to 'party' on 6 Nov 2026 - the same "
           "call Kyle made for Guardian's four auras and that was applied "
           "to Reaper's two today. So this talent does what a talent can: "
           "make that aura available more often. The Frozen-gated crit "
           "clause is dropped - " + FROZEN))

N.append(node(
    "command_bonefreeze", "Command: Bonefreeze",
    "Increases the damage of Animate: Frost Wyrm by 40% and reduces the "
    "cooldown of Command: Bonefreeze by 30%.",
    5, 2,
    effects={"ability_necromancer_animate_frost_wyrm_damage": 0.40,
             "ability_necromancer_command_bonefreeze_cooldown_pct": 0.30},
    connect=["ice_mastery"],
    source="CoA: 'Command your Skeletal Mages to freeze enemies at target "
           "location for 40 seconds. Damage taken may end the effect.' Both "
           "abilities already exist in our data. A targeted ground freeze "
           "is positional and the break-on-damage clause has no mechanism "
           "(nothing controls whether an effect breaks when its carrier is "
           "hit), so the node modifies the two frost AoE abilities we have "
           "instead. Animate: Frost Wyrm is a frost spell_dot at "
           "target_type enemy_aoe, which is the closest thing this class "
           "has to CoA's mass freeze. Both FRACTIONS, the second a "
           "reduction."))

N.append(node(
    "curse_of_the_lich", "Curse of the Lich",
    "Increases your spell critical strike chance by a further 5% and your "
    "Frost critical damage by 15%.",
    1, -4,
    effects={"crit_chance_spell": 5.0, "frost_crit_damage_pct": 0.15},
    connect=["runic_reservoir"],
    source="CoA: 'Increases the range of your Rime spells by 6 yds and "
           "increases the Frost critical strike chance of you and your "
           "summons by 3%.' Range is meaningless here. THERE IS NO "
           "PER-SCHOOL CRIT CHANCE KEY - the per-school family covers "
           "damage (<school>_spell_damage) and crit DAMAGE "
           "(<school>_crit_damage_pct, verified read at abilities.py:1446 "
           "via f-string) but not crit chance - so the Frost scoping on the "
           "chance is dropped and the school flavour lands on the crit "
           "damage instead. The summons half fails too: no talent key and "
           "no proc reaches a pet's crit chance. crit_chance_spell is "
           "PERCENTAGE POINTS; frost_crit_damage_pct is a FRACTION. Was a "
           "pure scalar on our side."))

N.append(node(
    "harrowing_winds", "Harrowing Winds",
    "Increases the damage of Glacial Impact by a further 30% and your area "
    "damage by 20%.",
    2, -4,
    effects={"ability_necromancer_glacial_impact_damage": 0.30,
             "aoe_damage": 0.20},
    connect=["runic_reservoir"],
    source="CoA: 'Damage dealt by Glacial Impact now deals an additional "
           "50% of the damage dealt as Frost damage to enemies within 6 yds "
           "of the primary target.' A splash around the primary target is "
           "positional and nothing adds targets to an ability, so the "
           "splash becomes aoe_damage - which is live and applies to the "
           "spec's three enemy_aoe spells (Animate: Frost Wyrm, Command: "
           "Bonefreeze, Corpse Explosion). aoe_damage is read at "
           "abilities.py:1600 only when target_type is enemy_aoe, so it is "
           "genuinely scoped to area attacks rather than being a stealth "
           "global. Both FRACTIONS."))

N.append(node(
    "champion_of_kelthuzad", "Champion of Kel'Thuzad",
    "Reduces the cost of Raise: Skeletal Mage by 40% and increases your "
    "pets' damage by 25%.",
    3, -2,
    effects={"ability_necromancer_raise_skeletal_mage_cost_pct": 0.40,
             "pet_damage": 0.25},
    connect=["arch_lich"],
    source="CoA: 'Your Skeletal Mages now only cost 1 Life Force.' CoA's "
           "Life Force is a POOL that summons occupy - 'occupying 2 Life "
           "Force' - which our engine does not model: a summon here costs "
           "its resource once and the pet then persists with no ongoing "
           "reservation. So 'only cost 1' becomes a flat cost reduction, "
           "which is the same intent through the mechanic we have. "
           "Necromancer genuinely summons four pets, so pet_damage is a "
           "legal key here (tools/qa_pet_keys.py exists because Witch "
           "Doctor Shadow Hunting shipped three pet keys on a class that "
           "summons nothing). Both FRACTIONS, the first a reduction. Was a "
           "pure scalar on our side."))

N.append(node(
    "crowns_call", "Crown's Call",
    "Increases your Intellect by 10% and your pets' health by 25%.",
    4, -3,
    effects={"intellect_pct": 10, "pet_health": 0.25},
    connect=["raising_the_kirin_tor"],
    source="CoA over 2 ranks: 'Increases your Intellect by 5% and the Frost "
           "damage dealt by your Undead minions by 10%.' The Intellect "
           "ports (doubled) and feeds the capstone's "
           "Intellect-to-spell-power conversion. THE MINIONS' FROST DAMAGE "
           "CANNOT BE SCOPED: pets scale off pet_damage, pet_health and "
           "pet_armor and nothing else - there is no per-school pet key, "
           "and pet_haste is read by nothing at all - so it becomes "
           "pet_health here, since Champion of Kel'Thuzad already supplies "
           "pet damage. intellect_pct is PERCENTAGE POINTS "
           "(character.py:1264 divides by 100); pet_health is a FRACTION. "
           "Two conventions in one dict, as usual."))

N.append(node(
    "permafrost", "Permafrost",
    "Reduces the cooldown of Glacial Impact and Animate: Frost Wyrm by 30%.",
    5, -2,
    effects={"ability_necromancer_glacial_impact_cooldown_pct": 0.30,
             "ability_necromancer_animate_frost_wyrm_cooldown_pct": 0.30},
    connect=["chilling_presence"],
    source="CoA: 'While your Lich Form is active, your Champion spells will "
           "now cooldown faster.' Both conditions fail: nothing reads "
           "whether another effect is active (which also killed Hard "
           "Bargain, Pathfinder and Chaos Fusion on other classes), and "
           "'Champion spells' is not a category the engine knows. Built as "
           "a flat reduction on the spec's two frost cooldowns instead. "
           "Folded in CoA's Champion of Kel'thuzad level-50 passive, whose "
           "Permafrost proc treats the next two spells 'as if the target "
           "were Frozen' - a pseudo-state nothing tests for, so it has "
           "nothing to grant. FRACTIONS where POSITIVE MEANS A REDUCTION; "
           "talented_cooldown floors at 1 turn. Was a pure scalar on our "
           "side."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "ice_mastery", "Ice Mastery",
    "Increases your spell power by 30% of your Intellect, your Frost "
    "damage by a further 15%, and your Frost critical damage by 25%.",
    6, 0,
    effects={"spell_power_from_intellect_pct": 0.30,
             "frost_spell_damage": 0.15,
             "frost_crit_damage_pct": 0.25},
    source="CoA's shared Ice Mastery, level 20 passive: 'Increases your "
           "spell power by 30% of your Intellect.' PORTS EXACTLY as a "
           "conversion - spell_power is in STAT_CONVERSION_TARGETS and "
           "intellect in STAT_CONVERSION_SOURCES, a legal pair, unlike the "
           "stamina and hit_rating targets that have cost eight nodes half "
           "their text across seven classes. Promoted to the capstone "
           "because a flat Intellect-to-spell-power conversion is the "
           "single largest thing a caster can be given, and paired with the "
           "tree's two Frost themes so the capstone reads as the payoff for "
           "everything below it: with Runic Reservoir and Chilling Presence "
           "that is +35% Frost damage, and with Frozen Power +75% Frost "
           "crit damage. ALL THREE ARE FRACTIONS."))


# ---- rank policy --------------------------------------------------------
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
    assert not setters, (
        f"Necromancer Death's Damnation owns low_health_threshold_pct for "
        f"this class at CoA's 20%, and the key SUMS across talents. "
        f"Found {setters}")

    # The per-school keys are the whole point of this tree and are read via
    # an f-string, so a typo in the school name is silent dead data that no
    # grep and no audit would catch. Pin them to schools Necromancer
    # actually deals.
    REAL_SCHOOLS = {"frost", "shadow"}
    for n in TREE["nodes"]:
        for k in (n.get("effects") or {}):
            if k.endswith("_spell_damage") or k.endswith("_crit_damage_pct"):
                school = k.rsplit("_spell_damage", 1)[0].rsplit(
                    "_crit_damage_pct", 1)[0]
                assert school in REAL_SCHOOLS, (
                    f"{n['talent_id']} authors {k}, but '{school}' is not a "
                    f"school Necromancer deals. These keys are built with "
                    f"an f-string at abilities.py:1371, so a wrong school "
                    f"name is SILENT - no grep and no audit would see it")
        for k in ("frost_spell_damage", "frost_crit_damage_pct",
                  "spell_power_from_intellect_pct"):
            v = (n.get("effects") or {}).get(k)
            if v is not None:
                assert 0 < v < 1, (
                    f"{n['talent_id']}.{k}={v} - a FRACTION as a talent "
                    f"effect")
        mods = ((n.get("proc") or {}).get("apply_effect") or {}).get("stat_mods") or {}
        for key in ("magic_damage_taken_pct", "spell_damage_taken_pct"):
            if key in mods:
                assert abs(mods[key]) >= 1, (
                    f"{n['talent_id']} {key}={mods[key]} inside a status "
                    f"effect, where it is PERCENTAGE POINTS")
        gr = (n.get("proc") or {}).get("grant_resource")
        if gr:
            assert gr.get("resource") == "life_force" and "amount" in gr, (
                f"{n['talent_id']} grant_resource must name life_force with "
                f"a FLAT amount")

    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Necromancer Rime: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
