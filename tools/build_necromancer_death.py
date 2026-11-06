#!/usr/bin/env python3
"""Rebuild Necromancer's Death tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_necromancer_death.py [--check]

SOURCE: data/reference/coa_worksheets/necromancer.md - 38 real Death
talents. Role: DPS (shadow diseases). Death was 23 nodes with 6 procs.

Necromancer was the WORST offender in the whole audit: 52 of its 66
matched talents were pure scalars on our side.

THIS IS THE DISEASE SPEC AND THE ENGINE PAYS FOR IT PROPERLY.
  - dot_duration_pct is live (abilities.py:2766, a FRACTION) and extending
    a dot ADDS TICKS at full per-turn value rather than thinning a fixed
    total, because per_turn derives from the ability's OWN base duration
    (abilities.py:2777). So CoA's Necrosis ("increases the duration of your
    diseases by 25%") is a straight damage increase, built exactly as
    written.
  - shadow_spell_damage is live. Every Death ability is damage_school
    "shadow", so CoA's Damnation ("increases your Shadow damage by 5%")
    ports verbatim. I nearly flattened this to all_damage: a grep for the
    literal key finds nothing because <school>_spell_damage is built with
    an f-string at abilities.py:1371, and I had wrongly recorded
    arcane_spell_damage as dead on that basis earlier the same day.
    Measured live at a ratio of exactly 1.500 before trusting it.
  - low_health_damage_pct (added 6 Nov 2026) covers CoA's three execute
    conditionals - Damnation's "doubled against enemies below 35% health",
    Plague Science's "100% increased damage to enemies below 20%" and
    Creeping Crypt. DEATH OWNS low_health_threshold_pct FOR THE CLASS at
    CoA's 20%; Rime and Animation inherit it. That key SUMS across talents
    and a character can spend in several trees, so a second setter would
    give a 40% window. Enforced by tools/qa_summing_thresholds.py.
  - spell_penetration is a real flat stat read attacker-side by both
    Character and Monster take_damage, so Unholy Erosion ports exactly -
    and it is the talent that will pay for the per-school resistance
    system Kyle has shelved.

CRYPT PLAGUE AND EXPUNGE STACKS ARE UNREADABLE. Nothing in this engine
reads a stack count, which kills Withering ("allows Crypt Plague to stack 5
additional times" - the stacks exist, the read does not), Expediting Death
("each stack of Expunge increases damage taken by 5%"), Touch of Death and
Waking Crypts' per-disease scaling. The stacking EFFECTS build; only
counting them is impossible.

NECROMANCER SUMMONS FOUR PETS (raise_ghoul, raise_skeletal_mage,
raise_banshee, raise_abomination), so pet keys are legal - but pets never
fire procs, nothing reads a live pet count, and no proc reaches a pet.
That kills Pandemic, Parasite Plague, Putricide's Formula, Rotting Flesh's
minion clause and Death Commander's minion half. Those go to Animation,
which is the pet tree, as flat pet scaling.

NOT BUILDABLE beyond the above: Mutation and Rotting Flesh's haste-scaling
change "tick rate", meaningless at one tick per turn; Rot Fetishist
replicates periodic damage as direct damage, for which there is no
mechanism; Virulency's copy-and-infest needs to read and reapply a
target's debuffs; Plague of Undeath's dispel-detonation needs a trigger on
being dispelled; Crypt Explosion and Creeping Plagues add targets;
Wormfood summons a timed exploding pet; Master of Death and Expunge key off
"Command spells", which is not a category the engine knows.
Apothecary's Cauldron's party half is real only because the ABILITY was
converted to target_type "party" on 6 Nov 2026.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/necromancer_death.json"

#: CoA's Runic Power is our life_force - Necromancer's PRIMARY pool
#: (LIFE_FORCE, None), with three generators.
GENERATORS = ["necromancer_crypt_swarm", "necromancer_lichfrost",
              "necromancer_flesh_to_worms"]

TREE = {
    "spec_name": "Necromancer Death",
    "tree_id": "necromancer_death",
    "description": ("Plague as a weapon - diseases that run long, hit "
                    "harder the closer the target is to dying."),
    "_source_note": (
        "Rebuilt 6 Nov 2026 from the 38 real CoA Death talents (role DPS). "
        "Necromancer was the worst offender in the audit at 52 of 66 "
        "matched talents being pure scalars. The engine pays for a disease "
        "spec properly: dot_duration_pct adds ticks at full value, "
        "shadow_spell_damage is live (every Death ability is school "
        "'shadow'), low_health_damage_pct covers CoA's three execute "
        "conditionals and spell_penetration is a real stat. Crypt Plague "
        "and Expunge stacks are unreadable, which costs four talents their "
        "scaling. Death owns low_health_threshold_pct for the class at "
        "CoA's 20%."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20,
                          "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"necromancer_death_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"necromancer_death_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


STACKS = ("CoA scales this off a STACK COUNT (Crypt Plague or Expunge). The "
          "stacking effect itself is buildable - max_stacks is honoured - "
          "but NOTHING READS A STACK COUNT anywhere in this engine, so the "
          "per-stack scaling is dropped for the flat value CoA's typical "
          "count comes to.")

PETS = ("CoA keys this on the Undead minions. Necromancer genuinely summons "
        "four (raise_ghoul, raise_skeletal_mage, raise_banshee, "
        "raise_abomination) so pet_damage/pet_health/pet_armor are legal - "
        "but PETS NEVER FIRE PROCS (no fire_proc_trigger anywhere in "
        "entities/pet.py), nothing reads a live pet count, and no proc can "
        "apply an effect to a pet. The minion clause is therefore dropped "
        "here; flat pet scaling lives in the Animation tree.")

N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "cycle_of_death", "Cycle of Death",
    "Increases your haste by 10% and your Shadow damage by 4%.",
    0, -4,
    effects={"haste": 10.0, "shadow_spell_damage": 0.04},
    connect=["damnation"],
    source="CoA: 'Increases your spell haste by 5%.' Doubled, with a small "
           "Shadow bonus added so the tree's entry point establishes its "
           "school. haste is PERCENTAGE POINTS; shadow_spell_damage is a "
           "FRACTION and is LIVE - built via an f-string at "
           "abilities.py:1371 inside _school_damage_bonus and resolved "
           "against the ability's real school, so a literal grep cannot "
           "see it. Every Death ability is damage_school 'shadow'. Was a "
           "pure scalar on our side."))

N.append(node(
    "damnation", "Damnation",
    "Increases your Shadow damage by 10%, and your damage against enemies "
    "below 20% health by a further 20%.",
    0, -2,
    effects={"shadow_spell_damage": 0.10,
             "low_health_damage_pct": 0.20,
             "low_health_threshold_pct": 0.20},
    connect=["necrosis", "dark_harvester"],
    source="CoA over 2 ranks: 'Increases your Shadow damage by 5%, doubled "
           "against enemies below 35% health.' BOTH HALVES PORT, which "
           "needed two things that did not exist this morning: "
           "shadow_spell_damage is live (see Cycle of Death) and "
           "low_health_damage_pct was added 6 Nov 2026 for the 48 CoA "
           "talents across 18 of the 21 classes worded this way. CoA's "
           "'doubled' becomes a second conditional bonus rather than a "
           "literal doubling, because the key adds rather than multiplies. "
           "THIS IS THE ONE NODE IN ALL OF NECROMANCER THAT SETS "
           "low_health_threshold_pct: that key SUMS across talents, is "
           "UNSCALED so rank does not divide it, and a character can spend "
           "in several trees of their class. 0.20 is CoA's own Plague "
           "Science threshold, so the class's execute window is consistent. "
           "Rime and Animation inherit it; a second setter would give 40%. "
           "main() asserts exactly one, and "
           "tools/qa_summing_thresholds.py enforces it class-wide. Was a "
           "pure scalar on our side."))

N.append(node(
    "necrosis", "Necrosis",
    "Increases the duration of your diseases by 25%.",
    0, 0,
    effects={"dot_duration_pct": 0.25},
    connect=["swarmer"],
    source="CoA: 'Increases the duration of your diseases by 25%.' PORTS "
           "VERBATIM, and it is the single most valuable node in the tree. "
           "dot_duration_pct is live at abilities.py:2766 as a FRACTION, "
           "and extending a dot is a STRAIGHT DAMAGE INCREASE rather than a "
           "dilution: abilities.py:2777 derives per-turn damage from the "
           "ability's OWN base duration, not the talented one, so +25% "
           "duration is +25% total damage at full per-tick value. (Editing "
           "an ability's BASE duration behaves the opposite way - "
           "effect_value is the total and gets divided - which is why "
           "Chronomancer's six dots needed their totals raised alongside.) "
           "Necromancer has five shadow dots for this to act on: Flesh to "
           "Worms, Plague of Undeath, Lichplague, Virulency and Animate: "
           "Plaguefather. Was a pure scalar on our side."))

N.append(node(
    "dark_harvester", "Dark Harvester",
    "Increases your critical strike chance by 6% and your hit chance by 6%.",
    0, 2,
    effects={"crit_chance_spell": 6.0, "hit_rating": 6.0},
    connect=["plague_science"],
    source="CoA: 'Increases your critical strike and hit chance by 3%.' "
           "PORTS EXACTLY, doubled. Both keys are PERCENTAGE POINTS. "
           "crit_chance_spell rather than the physical variant because this "
           "is a caster. hit_rating is live as a flat bonus - it is only "
           "invalid as a CONVERSION TARGET, which has cost eight nodes half "
           "their text across seven classes. Was a pure scalar on our "
           "side."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "swarmer", "Swarmer",
    "Your damaging spells restore 8 Life Force.",
    1, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "life_force", "amount": 8}},
    connect=["plague_revenant", "expunge"],
    source="CoA: 'Increases the Runic Power generated by Crypt Swarm by 2 "
           "per tick.' CoA'S RUNIC POWER IS OUR LIFE FORCE - Necromancer is "
           "(ResourceType.LIFE_FORCE, None), so it is the PRIMARY pool, and "
           "three abilities generate it (crypt_swarm 20, flesh_to_worms 15, "
           "lichfrost 12). 'Per tick' cannot be built: there is no periodic "
           "trigger, because status_effects.py:914 ticks a dot by calling "
           "the recipient's own take_damage with no caster reference. "
           "Re-pointed to on_damage_cast. grant_resource routes through the "
           "same gain_resource() the three generators use, so the cap "
           "holds, and its `amount` is FLAT - there is no pct_max field, "
           "which is the mistake that made Witch Doctor's Spiritual Devotee "
           "grant nothing at all while passing every check."))

N.append(node(
    "plague_science", "Plague Science",
    "Increases the damage of your periodic effects by 25%.",
    1, 2,
    effects={"dot_damage": 0.25},
    connect=["foul_contagion"],
    source="CoA level 20 passive: 'Your diseases and Crypt Swarm now deal "
           "100% increased damage to enemies below 20% health.' The "
           "conditional half is already covered by Damnation, which owns "
           "the class threshold at CoA's own 20% - stacking a second "
           "low_health_damage_pct here would be fine (the key adds) but "
           "setting the THRESHOLD again would push the window to 40%, so "
           "this node takes the unconditional form instead and the two "
           "divide the work. dot_damage is the global periodic key "
           "(abilities.py:1601) and a FRACTION. Was a pure scalar on our "
           "side."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "plague_revenant", "Plague Revenant",
    "Your critical strikes apply a plague dealing Shadow damage over 4 "
    "turns.",
    2, -2,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "apply_effect": {"effect_id": "crypt_plague",
                           "name": "Crypt Plague",
                           "effect_type": "dot", "duration": 4,
                           "potency": 28, "damage_school": "shadow",
                           "max_stacks": 5, "dispel_type": "disease",
                           "on_target": True}},
    connect=["expunge"],
    source="CoA: 'Critical strikes now apply a stack of Crypt Plague.' "
           "PORTS ALMOST VERBATIM - on_crit is a live trigger and the "
           "stacking dot is real, with CoA's Withering ('allows Crypt "
           "Plague to stack 5 additional times') folded in as max_stacks 5. "
           + STACKS + " dispel_type 'disease' so it cleanses as one, "
           "matching how CoA treats it. A proc-applied dot carries "
           "`potency` as PER-TURN damage - 28 a turn, 112 per stack - where "
           "an ABILITY rank's effect_value is the TOTAL and gets divided "
           "(abilities.py:2695). Note Necrosis does NOT extend this: "
           "dot_duration_pct is read in the ability dot branch, not in the "
           "proc payload path, so a proc-applied dot keeps its authored "
           "duration."))

N.append(node(
    "expunge", "Expunge",
    "Your damaging spells have a 30% chance to leave the target taking 10% "
    "more Shadow damage for 3 turns, stacking up to 2 times.",
    2, 0,
    proc={"trigger": "on_damage_cast", "chance": 30, "icd": 0,
          "apply_effect": {"effect_id": "expunge", "name": "Expunge",
                           "effect_type": "debuff", "duration": 3,
                           "stat_mods": {"magic_damage_taken_pct": 10},
                           "max_stacks": 2, "dispel_type": "magic",
                           "on_target": True}},
    connect=["festering_decay"],
    source="CoA: 'Casting Command spells on an enemy now applies Expunge if "
           "they are Diseased. Expunge increases the target's damage taken "
           "from your Necromancer diseases by 10% for 10 seconds, stacking "
           "2 times.' THREE CONDITIONS FAIL AND ONE SURVIVES: 'Command "
           "spells' is not a category the engine knows, 'if they are "
           "Diseased' needs to read a target's debuffs, and 'from your "
           "diseases' cannot be narrowed (there is no periodic-specific "
           "damage-taken key). What builds is the debuff itself at CoA's "
           "10% and 2 stacks, as magic damage taken - which is what this "
           "caster deals. CAREFUL: magic_damage_taken_pct is PERCENTAGE "
           "POINTS inside a status effect (character.py:2762 and "
           "monster.py:742 divide by 100) where as a TALENT effect it is a "
           "fraction, AND a positive value INCREASES damage taken - so 10 "
           "here is the right sign and the right magnitude. CoA's "
           "Expediting Death and Touch of Death both scale off this stack "
           "count: " + STACKS))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "foul_contagion", "Foul Contagion",
    "Increases the duration of Flesh to Worms and Plague of Undeath by 2 "
    "turns.",
    3, 2,
    effects={"ability_necromancer_flesh_to_worms_duration": 2,
             "ability_necromancer_plague_of_undeath_duration": 2},
    connect=["unholy_runes"],
    source="CoA: 'Applying Crypt Plague now extends the duration of Flesh "
           "to Worms on the target by 1 sec.' The trigger cannot be built "
           "(no payload extends a LIVE effect's duration, and there is no "
           "per-ability proc trigger) so it becomes a flat extension on the "
           "spec's two main diseases. +2 TURNS IS +2 FULL-VALUE TICKS, not "
           "a dilution, for the same reason Necrosis works - per-turn "
           "derives from the ability's own base duration. Both go 4 -> 6 "
           "turns, and Necrosis's 25% applies on top. SMALL INTEGERS IN "
           "TURNS, so talent_ranks.spread() refuses to rank this node. Was "
           "a pure scalar on our side."))

N.append(node(
    "festering_decay", "Festering Decay",
    "Reduces the cost of your spells by 15% and your critical strikes "
    "increase the target's spell damage taken by 10% for 4 turns.",
    3, 0,
    effects={"all_ability_cost_pct": 0.15},
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "festering_decay",
                           "name": "Festering Decay",
                           "effect_type": "debuff", "duration": 4,
                           "stat_mods": {"spell_damage_taken_pct": 10},
                           "dispel_type": "magic", "on_target": True}},
    connect=["waking_crypts"],
    source="CoA: 'Reduces the cost of Command spells by 15% and causes them "
           "to increase the target's spell damage taken by 10% for 15 sec.' "
           "BOTH HALVES BUILD, widened from 'Command spells' (not an engine "
           "category) to all spells and to on_crit respectively. 15 sec -> "
           "4 turns. TWO CONVENTIONS, BOTH CORRECT: all_ability_cost_pct is "
           "a FRACTION as a talent effect where POSITIVE MEANS A REDUCTION "
           "(it flips to percentage POINTS inside a status effect, which "
           "caught me on Ranger Farstrider's Thread The Needle), and "
           "spell_damage_taken_pct is percentage POINTS inside a status "
           "effect where as a talent effect it is a fraction. Was a pure "
           "scalar on our side."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "unholy_runes", "Unholy Runes",
    "Increases the damage of Crypt Swarm by 20% and of Corpse Explosion by "
    "15%.",
    4, 2,
    effects={"ability_necromancer_crypt_swarm_damage": 0.20,
             "ability_necromancer_corpse_explosion_damage": 0.15},
    connect=["death_commander"],
    source="CoA: 'Increases the damage of Crypt Swarm by 15%.' PORTS "
           "EXACTLY (raised to 20%), extended to Corpse Explosion so the "
           "node covers both of the spec's direct nukes. Crypt Swarm is the "
           "biggest Life Force generator at 20, so this pays for the "
           "rotation. Was a pure scalar on our side. Both FRACTIONS."))

N.append(node(
    "death_commander", "Death Commander",
    "Your damaging spells have a 20% chance to increase your haste by 20% "
    "for 3 turns.",
    4, 0,
    proc={"trigger": "on_damage_cast", "chance": 20, "icd": 2,
          "apply_effect": {"effect_id": "death_commander",
                           "name": "Death Commander",
                           "effect_type": "buff", "duration": 3,
                           "stat_mods": {"haste": 20.0},
                           "dispel_type": None, "on_target": False}},
    connect=["waking_crypts"],
    source="CoA: 'Periodic damage dealt now has a 10% chance to increase "
           "your and your Undead minion's haste by 20% for 8 seconds.' The "
           "periodic trigger does not exist (see Swarmer), so this is "
           "re-pointed to on_damage_cast with the chance doubled and a "
           "2-turn internal cooldown - a per-cast roll happens once where a "
           "per-tick roll happens dozens of times. " + PETS + " "
           "(pet_haste is separately read by nothing at all, so even on the "
           "pet tree that half would be silent.) 8 sec -> 3 turns, CoA's "
           "20% haste kept verbatim."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "unholy_erosion", "Unholy Erosion",
    "Increases your spell penetration by 50.",
    5, -2,
    effects={"spell_penetration": 50},
    connect=["waking_crypts"],
    source="CoA level 50 passive: 'Increases your spell penetration by 50, "
           "scaling with your level.' PORTS EXACTLY. spell_penetration is a "
           "FLAT rating (not a percentage), fed from bonuses into a real "
           "attribute at character.py:1382 and read attacker-side by both "
           "Character.take_damage and Monster.take_damage against their "
           "magic_resistance - so it works today, not just in principle. "
           "This is one of the talents that will pay for Kyle's shelved "
           "per-school resistance system ('a caster should be punished if "
           "they use fireball against a flame elemental, unless they have "
           "spell penetration'); when the six base_*_resist fields land on "
           "creature templates, this node already beats them. The "
           "level-scaling clause is dropped: talent effects do not scale "
           "with character level. Was a pure scalar on our side, which here "
           "is what CoA wrote too."))

N.append(node(
    "apothecarys_cauldron", "Apothecary's Cauldron",
    "Increases your Shadow damage by a further 8% and reduces the cooldown "
    "of Apothecary's Cauldron by 30%.",
    5, 1,
    effects={"shadow_spell_damage": 0.08,
             "ability_necromancer_apothecarys_cauldron_cooldown_pct": 0.30},
    connect=["waking_crypts"],
    source="CoA: 'Increases the spell haste of all party and raid members "
           "by 3%. Does not stack with similar effects. In addition, "
           "increases your Magic damage dealt by 3%.' THE PARTY HALF IS "
           "REAL, but not from here: a talent effect can never reach an "
           "ally. The necromancer_apothecarys_cauldron ABILITY carries the "
           "party haste, and it was converted from target_type 'self' to "
           "'party' on 6 Nov 2026 - the same call Kyle made for Guardian's "
           "four auras and that was applied to Reaper's two today. So this "
           "talent does what a talent can: make that aura available more "
           "often, plus CoA's own selfish Magic damage clause as "
           "shadow_spell_damage. *_cooldown_pct is a FRACTION where "
           "POSITIVE MEANS A REDUCTION. Was a pure scalar on our side."))

N.append(node(
    "plague_of_undeath", "Plague of Undeath",
    "Increases the damage of Plague of Undeath by 35%, and your critical "
    "strikes reduce the target's healing received by 20% for 3 turns.",
    1, -2,
    effects={"ability_necromancer_plague_of_undeath_damage": 0.35},
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "plague_of_undeath_mortal",
                           "name": "Plague of Undeath",
                           "effect_type": "debuff", "duration": 3,
                           "stat_mods": {"healing_taken_pct": -20},
                           "dispel_type": "disease", "on_target": True}},
    connect=["damnation"],
    source="CoA: 'Disease an enemy dealing Plague damage every 3 sec and "
           "reduces the targets Holy healing received by -40% for 20 "
           "seconds. If Plague of Undeath is dispelled, the enemy takes "
           "damage and is stunned for 5 seconds.' The ability already "
           "exists as a 4-turn shadow dot. The healing reduction ports (the "
           "Holy scoping dropped - healing_taken_pct is school-agnostic) "
           "and is a real mortal-strike effect: healing_taken_pct is one of "
           "only eight status stat_mods a monster reads. THE DISPEL "
           "DETONATION CANNOT BE BUILT: no trigger fires when an effect is "
           "dispelled, the same gap that killed Reaper Soul's Soulrot. "
           "20 sec -> 3 turns, 40% -> 20% since it now comes off any crit. "
           "healing_taken_pct is PERCENTAGE POINTS inside a status effect "
           "(character.py:2904 divides by 100), so -20 is -20%."))

N.append(node(
    "lichplague", "Lichplague",
    "Increases the damage of Lichplague and Virulency by 30%.",
    2, 2,
    effects={"ability_necromancer_lichplague_damage": 0.30,
             "ability_necromancer_virulency_damage": 0.30},
    connect=["plague_science"],
    source="CoA: 'Disease an enemy, dealing Plague damage every 3 sec for "
           "18 seconds. Damage increased by 4% for each Necromancer disease "
           "on the enemy.' Both abilities already exist as shadow dots. THE "
           "PER-DISEASE SCALING CANNOT BE BUILT - nothing counts how many "
           "effects are on a target, which also killed Waking Crypts' and "
           "Fiend's conditionals - so it becomes flat damage on both. "
           "18 seconds is 6 turns at ~3 sec per turn, against our 4; "
           "Necrosis and the capstone together take it to 6.2, which lands "
           "almost exactly on CoA's window. Both FRACTIONS."))

N.append(node(
    "creeping_crypt", "Creeping Crypt",
    "Increases the critical strike chance of Flesh to Worms and Lichplague "
    "by 25%.",
    2, -4,
    effects={"ability_necromancer_flesh_to_worms_crit": 25.0,
             "ability_necromancer_lichplague_crit": 25.0},
    connect=["damnation"],
    source="CoA: 'Increases the critical strike chance of Flesh to Worms by "
           "25% against enemies below 35% maximum health.' There is no "
           "CONDITIONAL CRIT key - low_health_damage_pct covers damage only "
           "- so the condition is dropped and CoA's 25% kept unconditional, "
           "extended to Lichplague as the spec's other core disease. WORTH "
           "KNOWING WHAT THIS ACTUALLY BUYS: these are spell_dot abilities, "
           "and a dot's periodic TICKS never roll crit in this engine, so "
           "the crit chance applies to the application hit rather than the "
           "ticks. CoA has a shared Impeccable Timing talent specifically "
           "to let periodic damage crit and it cannot be built either. "
           "Flagged rather than left to look like a 25% dot buff. "
           "Per-ability crit keys are PERCENTAGE POINTS."))

N.append(node(
    "fiend", "Fiend",
    "Increases the damage of Lichfrost by 25% and your spell critical "
    "damage by 20%.",
    3, -2,
    effects={"ability_necromancer_lichfrost_damage": 0.25,
             "crit_damage_spell": 0.20},
    connect=["festering_decay"],
    source="CoA: 'Increases the damage and critical damage of Lichfrost by "
           "20% against diseased targets.' The condition cannot be built "
           "(nothing reads a target's debuffs) so rather than ship "
           "something that silently never fires, both halves go "
           "unconditional - the damage per-ability, the crit damage as a "
           "global, since there is no per-ability crit-damage key paired "
           "with a per-ability damage key on this ability. Lichfrost is a "
           "FROST ability on a shadow spec, which is why it gets its own "
           "node here rather than riding shadow_spell_damage. "
           "crit_damage_spell is a FRACTION; crit_chance_* keys are points. "
           "Was a pure scalar on our side."))

N.append(node(
    "master_of_death", "Master of Death",
    "Increases the damage of Harvest Plague by 30% and its healing by 25%.",
    3, 4,
    effects={"ability_necromancer_harvest_plague_damage": 0.30,
             "ability_necromancer_harvest_plague_healing": 0.25},
    connect=["lichplague"],
    source="CoA: 'Casting Command spells on an enemy now applies Crypt "
           "Plague.' Plague Revenant already applies Crypt Plague off crits "
           "and owns that mechanic for the spec, and 'Command spells' is "
           "not a category the engine knows, so repeating it would be a "
           "duplicate. Re-pointed to Harvest Plague, the spec's "
           "damage_and_heal ability, which had no node at all. IT NEEDS "
           "BOTH KEYS: a damage_and_heal ability's heal half reads "
           "ability_<id>_HEALING and its damage half reads _damage - "
           "authoring only _damage would buff the hit and leave the heal "
           "untouched, which is the mistake that left 18 talents across "
           "four classes silently doing nothing before _healing was "
           "accepted. Added 6 Nov 2026 after qa_recruit_talents reported "
           "'Stelios Dukas at level 64 joins with 3 unspent talent "
           "point(s)': a recruit scaled above 60 needs a tree holding 60 "
           "points, and this spec had 57. Both FRACTIONS."))

N.append(node(
    "mutation", "Mutation",
    "Increases the damage of your periodic effects by a further 18%.",
    4, -2,
    effects={"dot_damage": 0.18},
    connect=["death_commander"],
    source="CoA: 'For the next 15 sec your diseases mutate causing them to "
           "act with accelerated lethality, allowing your freshly applied "
           "diseases to tick 50% faster.' TICK RATE HAS NO MEANING IN A "
           "TURN-BASED ENGINE - a dot ticks exactly once per turn, full "
           "stop - so there is nothing for 'tick 50% faster' to act on. "
           "Repriced as dot_damage, which is what a faster tick rate "
           "amounts to, and made passive since the 15-second window would "
           "be a 5-turn self-buff a talent cannot grant on its own. CoA "
           "leans on tick-rate language repeatedly (Chronomancer's Crown of "
           "Power, Ranger's Lethal Wounds and Razorquills, Rotting Flesh) "
           "and it fails every time. A FRACTION. Was a pure scalar on our "
           "side."))

N.append(node(
    "fleshcrafting", "Fleshcrafting",
    "Increases the duration of Unholy Frenzy by 2 turns and reduces its "
    "cooldown by 35%.",
    5, -4,
    effects={"ability_necromancer_unholy_frenzy_duration": 2,
             "ability_necromancer_unholy_frenzy_cooldown_pct": 0.35},
    connect=["unholy_erosion"],
    source="CoA: 'Increases the duration Unholy Frenzy by 5 sec and casting "
           "Command spells now reduces its cooldown by -1 sec.' Both halves "
           "port, the second as a flat cooldown reduction since 'Command "
           "spells' is not a category the engine knows and there is no "
           "per-ability proc trigger. Folded in CoA's Unstable Frenzy "
           "('reduces the cooldown of Unholy Frenzy by -60 sec'), which "
           "names the same ability. 5 sec -> 2 turns, taking it 3 -> 5. "
           "Unholy Frenzy was NOT one of the buffs whose duration was dead "
           "data - it is correctly combat-scoped - but Reaper had eleven "
           "that were, so this was checked rather than assumed. SMALL "
           "INTEGER IN TURNS, so spread() refuses to rank this node."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "waking_crypts", "Waking Crypts",
    "Increases the duration of your diseases by a further 30%, their "
    "damage by 25%, and the damage of Crypt Plague by 50%.",
    6, 0,
    effects={"dot_duration_pct": 0.30, "dot_damage": 0.25,
             "shadow_spell_damage": 0.10},
    source="CoA: 'Increases the damage of Crypt Plague by 50% and Crypt "
           "Swarm now deals 4% more damage for each Necromancer disease you "
           "have on the target.' The per-disease scaling cannot be built - "
           "nothing counts how many effects are on a target, which is the "
           "same gap that killed Lichplague's and Fiend's conditionals - so "
           "the capstone instead doubles down on what this tree is for. "
           "dot_duration_pct stacks additively with Necrosis for +55% "
           "disease duration, which on a Flesh to Worms already extended "
           "+2 turns by Foul Contagion is 6 base turns becoming 9 - at full "
           "per-tick value, so it is a genuine 50% damage increase on the "
           "spec's core dot rather than a slower one. Crypt Plague's 50% "
           "arrives through shadow_spell_damage, since the proc-applied dot "
           "has no per-ability key to target. ALL THREE ARE FRACTIONS."))


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
    assert len(setters) == 1, (
        f"low_health_threshold_pct SUMS across talents and is UNSCALED, and "
        f"a character can spend in several Necromancer trees - exactly one "
        f"node in the CLASS may set it, and Death owns it. Found {setters}")

    # The two dot keys are this spec's identity and read as FRACTIONS as
    # talent effects. A value >= 1 means someone authored points.
    for n in TREE["nodes"]:
        for k in ("dot_damage", "dot_duration_pct", "shadow_spell_damage"):
            v = (n.get("effects") or {}).get(k)
            if v is not None:
                assert 0 < v < 1, (
                    f"{n['talent_id']}.{k}={v} - a FRACTION as a talent "
                    f"effect (0.25 = +25%)")
        mods = ((n.get("proc") or {}).get("apply_effect") or {}).get("stat_mods") or {}
        for key in ("magic_damage_taken_pct", "spell_damage_taken_pct",
                    "physical_damage_taken_pct"):
            if key in mods:
                assert abs(mods[key]) >= 1, (
                    f"{n['talent_id']} {key}={mods[key]} inside a status "
                    f"effect, where it is PERCENTAGE POINTS - a fraction "
                    f"here delivers a hundredth of the intent")
        gr = (n.get("proc") or {}).get("grant_resource")
        if gr:
            assert gr.get("resource") == "life_force" and "amount" in gr, (
                f"{n['talent_id']} grant_resource must name life_force "
                f"(CoA's Runic Power, Necromancer's primary pool) with a "
                f"FLAT amount")

    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Necromancer Death: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
