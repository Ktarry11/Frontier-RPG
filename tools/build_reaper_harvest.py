#!/usr/bin/env python3
"""Rebuild Reaper's Harvest tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_reaper_harvest.py [--check]

SOURCE: data/reference/coa_worksheets/reaper.md and
data/reference/coa/reaper.json - 39 real Harvest talents from Ascension's
own CoA Builder payload. Role: DPS.

Reaper measured 121 CoA talents against our 67, 46 of those pure scalars.
Harvest was 23 nodes with 7 procs.

THIS IS THE BEST-PORTING TREE IN THE AUDIT SO FAR, and the reason is worth
stating: almost everything Harvest does keys off systems this engine
actually has.

SOULS ARE A REAL RESOURCE, with more generators than any class yet seen.
Reaper is (ResourceType.MANA, ResourceType.SOULS) at abilities.py:149 and
THIRTEEN abilities carry a `generates` block for souls - reap, murder,
wraithblade, scythe_rush, spectre_stride, withering_touch, crows_harvest,
doomrend, slaughter, dirge, deathchaser, dreadwake, requiem. So CoA's Soul
Fragments and Reaped Souls land on a pool that exists, and
`grant_resource: {"resource": "souls"}` routes through the same
gain_resource() those thirteen use, caps included.

CoA's "Runic Power" maps cleanly onto mana: every Reaper ability in our
data is resource_type mana, so "-10 Runic Power cost" is a mana cost
reduction and ports as one. Compare Chronomancer's Echo Fragments or
Venomancer's Brood Marks, which had no pool at all and had to be
flattened. CHECK THE RESOURCE FIRST - it has gone both ways four times now.

THE EXECUTE MECHANIC IS REAL ON BOTH SIDES, which is new as of today.
  - execute_threshold_pct already gates whether an ability may be used on
    a wounded target, and our Slaughter already carries CoA's exact 35%.
  - bypass_execute_threshold is a real proc flag (abilities.py:1691-1710),
    consumed on use as "a single guaranteed-usable window, not a permanent
    ignore-HP state" - which is CoA's Extinction word for word.
  - low_health_damage_pct was added 6 Nov 2026 while surveying this very
    tree, because SEVEN Harvest talents are worded "against enemies below
    35% health" and there was no key for it. 48 talents across 18 of the 21
    classes want it; it is the most common unbuildable conditional in the
    whole CoA data set. Verified at 0.993x above the threshold and 1.481x
    below it over 600 casts.
That means Hemorrhage, Executioner, Unbound and Extinction all build as
written rather than being repriced into scalars.

CRIT FROM STRENGTH IS A LEGAL PAIR and nobody had used it: "crit_chance"
is in STAT_CONVERSION_TARGETS (mapping to crit_chance_physical) and
"strength" is in STAT_CONVERSION_SOURCES, so Executioner's "critical
strike rating by 20% of your Strength" ports exactly. Worth remembering -
a conversion target has to name a REAL attribute, and "block" wrote a
phantom one for months.

WHAT COULD NOT BE BUILT AT ALL:
  - Harvesting Grounds, and This Is My Domain which modifies it - a
    persistent ground effect that pulls fleeing enemies back to its
    centre. No positioning of any kind.
  - The Grim Reaper - needs a charge system.
  - Crimson Thirst's and Mortal's End's stack payoffs ("at 5 stacks it
    also heals you", "allows Extinction to stack an additional time") -
    nothing reads a stack count. The stacking buffs themselves are real;
    only the read is impossible.
  - The Time Has Come ("10% more damage against slowed targets") - nothing
    reads a target's debuffs.
  - Blood Harvester (party-wide crit) - a talent effect never reaches an
    ally; only a party-targeted ABILITY does, and Reaper has no aura to
    convert the way Guardian's four were on 5 Nov 2026.
  - Sever - an interrupt plus a school lockout. There is no silence or
    interrupt key.
  - Redshade - CoA's own payload is the literal string "$be", i.e. their
    data is broken here, so there is nothing to port.
  - Doomrend's healing-absorb shield ON AN ENEMY - no absorb applies to a
    target, and healing_taken_pct is the nearest readable equivalent, so
    Blood Fueled folds into that instead.

THIS TREE OWNS TWO GATED ABILITIES: harvest_time and blood_frenzy. Both
carry requires_talent and this is their only unlock, so dropping a node
makes them unobtainable forever. Asserted in main().
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/reaper_harvest.json"

#: Abilities carrying requires_talent that ONLY this tree unlocks.
GATED = {"reaper_harvest_time", "reaper_blood_frenzy"}

#: The soul generators - every ability with a `generates` block. Thirteen,
#: the most of any class, which is why CoA's soul talents port here.
GENERATORS = ["reaper_reap", "reaper_murder", "reaper_wraithblade",
              "reaper_scythe_rush", "reaper_spectre_stride",
              "reaper_withering_touch", "reaper_crows_harvest",
              "reaper_doomrend", "reaper_slaughter", "reaper_dirge",
              "reaper_deathchaser", "reaper_dreadwake", "reaper_requiem"]

TREE = {
    "spec_name": "Reaper Harvest",
    "tree_id": "reaper_harvest",
    "description": ("Finish what is already dying - a two-hander spec that "
                    "hits hardest on a wounded target."),
    "_source_note": (
        "Rebuilt 6 Nov 2026 from the 39 real CoA Harvest talents (role "
        "DPS). The best-porting tree in this audit: SOULS are a real "
        "secondary resource with thirteen generators, CoA's Runic Power "
        "maps onto mana, and the execute mechanic is real on both sides - "
        "execute_threshold_pct gates the ability, bypass_execute_threshold "
        "is a real consumed proc flag that is CoA's Extinction verbatim, "
        "and low_health_damage_pct was added while surveying this tree "
        "because seven of its talents needed it. Executioner's crit from "
        "Strength is a legal conversion pair nobody had used. Two "
        "load-bearing unlocks, asserted."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20,
                          "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"reaper_harvest_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"reaper_harvest_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


#: Appended to every node using the key added for this tree.
EXECUTE = (
    "Uses low_health_damage_pct, added to the engine on 6 Nov 2026 "
    "specifically because this tree needed it seven times and there was no "
    "key for 'damage against enemies below X% health' - the most common "
    "unbuildable conditional in the CoA data (48 talents, 18 of 21 "
    "classes). It is read in _damage_multiplier when a recipient is known, "
    "is a FRACTION, and shares low_health_threshold_pct (default 35%) with "
    "every other conditional in the engine. THAT THRESHOLD KEY SUMS ACROSS "
    "TALENTS - two nodes at 0.35 would give 'below 70%' - so this tree "
    "carries exactly one, on Executioner, and main() asserts it.")

N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "bountiful_harvest", "Bountiful Harvest",
    "Increases the damage of Reap and Murder by 25%.",
    0, -4,
    effects={"ability_reaper_reap_damage": 0.25,
             "ability_reaper_murder_damage": 0.25},
    connect=["maw_knight"],
    source="CoA: 'Increases the damage of Reap and Murder by 25%.' PORTS "
           "EXACTLY, both abilities. Reap and Murder are the spec's two "
           "cheapest soul generators (10 and 15 souls), so this is the "
           "node that makes the filler worth pressing. Was a pure scalar "
           "on our side. Per-ability damage keys are FRACTIONS."))

N.append(node(
    "maw_knight", "Maw Knight",
    "Increases the critical strike chance of Doomrend by 10%.",
    0, -2,
    effects={"ability_reaper_doomrend_crit": 10.0},
    connect=["sanguine_harvester", "dark_fate"],
    source="CoA over 2 ranks: 'Increases the critical strike chance of "
           "Doomrend by 5%.' PORTS EXACTLY, doubled for the two ranks. "
           "Doomrend generates 15 souls and is the opener this tree keeps "
           "coming back to - three later nodes read it. Was a pure scalar "
           "on our side. Per-ability crit keys are PERCENTAGE POINTS, "
           "unlike the damage keys above, which are fractions; the two sit "
           "side by side all over this project and read opposite ways."))

N.append(node(
    "sanguine_harvester", "Sanguine Harvester",
    "Increases your haste by 20%.",
    0, 0,
    effects={"haste": 20.0},
    connect=["red_wake"],
    source="CoA over 2 ranks: 'Increases your melee haste by 10%.' Doubled "
           "for the two ranks. The melee scoping is dropped - there is no "
           "separate melee-haste key, only `haste`, which in a turn-based "
           "engine means acting more often rather than swinging faster. "
           "Was a pure scalar on our side. PERCENTAGE POINTS."))

N.append(node(
    "dark_fate", "Dark Fate",
    "Reduces the mana cost of Crow's Harvest and Wraithblade by 20%.",
    0, 2,
    effects={"ability_reaper_crows_harvest_cost_pct": 0.20,
             "ability_reaper_wraithblade_cost_pct": 0.20},
    connect=["crimson_wraith"],
    source="CoA: 'Reduces the cost of Crow's Harvest by -10 Runic Power.' "
           "CoA'S RUNIC POWER IS OUR MANA - every Reaper ability in our "
           "data is resource_type mana - so a Runic Power cost reduction "
           "ports as a mana cost reduction. 10 off Crow's Harvest's 30 is "
           "a third; set at 20% and extended to Wraithblade (CoA's Blood "
           "Wraith reduces that one too) so the node is not a one-ability "
           "pick. *_cost_pct keys are FRACTIONS and POSITIVE MEANS A "
           "REDUCTION - the opposite sign convention from most of this "
           "file. Was a pure scalar on our side."))

N.append(node(
    "crimson_wraith", "Crimson Wraith",
    "Increases your physical critical damage by 20%.",
    0, 4,
    effects={"crit_damage_physical": 0.20},
    connect=["hemorrhage"],
    source="CoA over 2 ranks: 'Increases your critical stike damage by "
           "10%.' (CoA's own typo.) Doubled for the two ranks, scoped to "
           "physical because this spec's damage is all weapon-based. Was a "
           "pure scalar on our side. crit_damage_* keys are FRACTIONS; "
           "crit_chance_* keys are percentage points."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "red_wake", "Red Wake",
    "Your critical strikes generate 10 additional souls.",
    1, 0,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "souls", "amount": 10}},
    connect=["harvest_time", "crimson_death"],
    source="CoA: 'Direct damage critical strikes now generate an additional "
           "Soul Fragment.' PORTS EXACTLY. grant_resource routes through "
           "the same gain_resource() the thirteen soul generators use, so "
           "caps are respected automatically. 10 souls because that is what "
           "Reap and Spectre Stride each generate - one fragment in this "
           "economy's own units. The `amount` field is FLAT; there is no "
           "`pct_max` field, and inventing one on Witch Doctor's Spiritual "
           "Devotee would have granted NOTHING while passing every check. "
           "The direct-damage filter is dropped: on_crit carries no "
           "ability_id to test, though periodic ticks never roll crit "
           "anyway, so in practice only direct damage can fire this."))

N.append(node(
    "hemorrhage", "Hemorrhage",
    "Increases your damage against enemies below 35% health by 15%.",
    1, 4,
    effects={"low_health_damage_pct": 0.15},
    connect=["genocide"],
    source="CoA: 'Increases the damage and critical strike chance of your "
           "abilities by 10% against enemies below 35% health.' " + EXECUTE
           + " The crit-chance half is dropped: there is no conditional "
           "crit key, only conditional damage, so the damage half is set at "
           "15% to carry the node. Was a pure scalar on our side - and the "
           "scalar it was reduced to is exactly the failure this rebuild "
           "exists to undo."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "harvest_time", "Harvest Time",
    "Teaches Harvest Time, the moment the field is ready.",
    2, -2,
    effects={"unlock_ability": "reaper_harvest_time"},
    connect=["darkrend_scythe"],
    source="CoA: 'Increases your damage and critical strike chance by 15% "
           "and gives your spells that require Soul Infusion a 50% chance "
           "to not consume the effect for 15 sec.' LOAD-BEARING UNLOCK - "
           "reaper_harvest_time carries requires_talent and this is its "
           "only unlock node; dropping it makes the ability unobtainable "
           "forever. The damage and crit buff lives on the ability itself. "
           "The refund clause cannot be built: nothing intercepts a "
           "resource SPEND, only grants, so 'a chance not to consume' has "
           "no hook. CoA's Deathbringer ('doubles the duration of Blood "
           "Frenzy, Harvest Time and Harvesting Grounds') is folded into "
           "the capstone instead."))

N.append(node(
    "crimson_death", "Crimson Death",
    "Your critical strikes have a 25% chance to strike again with "
    "Slaughter, free of cost.",
    2, 0,
    proc={"trigger": "on_crit", "chance": 25, "icd": 1,
          "cast_ability": "reaper_slaughter"},
    connect=["souls_for_the_slaughter"],
    source="CoA: 'Your Slaughter now has a 20% chance to cast an additional "
           "time free of cost.' PORTS ALMOST EXACTLY via a cast_ability "
           "proc, which takes a bare ability id and costs nothing when it "
           "fires - so 'free of cost' is literally true. Only the "
           "Slaughter-specific trigger goes (there is no per-ability proc "
           "trigger), replaced by on_crit at 25% with a 1-turn internal "
           "cooldown so it cannot chain. NOTE: cast_ability does NOT check "
           "that the caster has learned the ability - but Slaughter is "
           "ungated, so there is nothing to check here."))

N.append(node(
    "genocide", "Genocide",
    "Increases the damage and critical damage of Slaughter by 20%.",
    2, 3,
    effects={"ability_reaper_slaughter_damage": 0.20,
             "ability_reaper_slaughter_crit_damage": 0.20},
    connect=["extinction"],
    source="CoA: 'Increases the critical damage and critical strike chance "
           "of Slaughter by 10%.' The crit-damage half ports as a "
           "per-ability key (one of the few abilities in the project with "
           "both _damage and _crit_damage authored). The crit-CHANCE half "
           "is swapped for straight damage, since Crimson Death already "
           "keys this tree off crits and a third crit-chance node would "
           "stack into the same wall. Doubled from CoA's 10%. Was a pure "
           "scalar on our side. Both FRACTIONS."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "darkrend_scythe", "Darkrend Scythe",
    "Your attacks have a 35% chance to open a bleed dealing damage over 4 "
    "turns, stacking up to 5 times.",
    3, -2,
    proc={"trigger": "on_weapon_swing", "chance": 35, "icd": 0,
          "apply_effect": {"effect_id": "darkrend_scythe",
                           "name": "Darkrend Scythe",
                           "effect_type": "dot", "duration": 4,
                           "potency": 22, "damage_school": "physical",
                           "max_stacks": 5, "dispel_type": None,
                           "on_target": True}},
    connect=["blood_knight"],
    source="CoA: 'Damage dealt by Doomrend and Crow's Harvest now applies a "
           "bleed, dealing Physical damage every 2 sec for 10 sec, stacking "
           "5 times. Additional applications do not refresh the duration.' "
           "The bleed, its duration and its 5 stacks all port. 10 sec -> 4 "
           "turns (CoA ticks every 2 sec, so this is 5 ticks there and 4 "
           "here). The two-ability scoping becomes on_weapon_swing; the "
           "no-refresh clause cannot be built, since nothing controls "
           "whether a reapplication refreshes. NOTE a real difference from "
           "a dot ABILITY: a proc-applied dot carries `potency` directly as "
           "its PER-TURN damage, where an ability's rank effect_value is "
           "the TOTAL across the duration (abilities.py:2695) and gets "
           "divided. So 22 here is 22 per turn, 88 over the dot, 440 at "
           "five stacks - not 22 total."))

N.append(node(
    "souls_for_the_slaughter", "Souls for the Slaughter",
    "Your critical strikes increase your physical damage by 20% for 2 "
    "turns.",
    3, 0,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "apply_effect": {"effect_id": "souls_for_the_slaughter",
                           "name": "Souls for the Slaughter",
                           "effect_type": "buff", "duration": 2,
                           "stat_mods": {"damage_dealt_pct": 20},
                           "dispel_type": None, "on_target": False}},
    connect=["ruin"],
    source="CoA: 'Critical strikes with Slaughter now cause your auto "
           "attacks to deal an additional 85% Shadow damage for 5 sec.' "
           "There is no 'add a school's damage to your autos' key and no "
           "per-school damage key the engine reads for Shadow on the "
           "caster side, so this becomes a flat outgoing-damage window, "
           "which is the same shape in play. 5 sec -> 2 turns. "
           "damage_dealt_pct is the BUFF-side companion to the talent "
           "keys (abilities.py reads it from active status effects, same "
           "'+N% more' convention) and is in PERCENTAGE POINTS inside a "
           "status effect, so 20 is 20%."))

N.append(node(
    "extinction", "Extinction",
    "Your critical strikes have a 30% chance to let your next Slaughter be "
    "used on a target at any health.",
    3, 3,
    proc={"trigger": "on_crit", "chance": 30, "icd": 1,
          "apply_effect": {"effect_id": "extinction", "name": "Extinction",
                           "effect_type": "buff", "duration": 3,
                           "stat_mods": {},
                           "proc": {"bypass_execute_threshold": True},
                           "dispel_type": None, "on_target": False}},
    connect=["doomer"],
    source="CoA level 20 passive: 'Direct Physical damage dealt now has a "
           "5% chance to grant you Extinction for 10 seconds. Extinction: "
           "Your next Slaughter is usable regardless of the target's health "
           "and costs -10 less Runic Power.' THIS PORTS VERBATIM, which is "
           "rare. bypass_execute_threshold is a real proc flag read at "
           "abilities.py:1691 and the engine CONSUMES it on use - its own "
           "comment calls it 'a single guaranteed-usable window, not a "
           "permanent ignore-HP state' and says 'a future ability/talent "
           "can grant this bypass the same way'. That is CoA's Extinction "
           "word for word, including the one-shot semantics. Slaughter "
           "already carries execute_threshold_pct 35, matching CoA's own "
           "number. 10 sec -> 3 turns, 5% -> 30% because CoA's per-hit roll "
           "happens far more often than a crit. The cost reduction is "
           "dropped (Dark Fate covers costs). The nested `proc` inside "
           "apply_effect works but IS NOT INSPECTED BY THE AUDIT, so there "
           "is no static safety net on this node - main() asserts it "
           "instead. CoA's Mortal's End ('allows Extinction to stack an "
           "additional time') cannot be built: nothing reads a stack "
           "count."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "blood_knight", "Blood Knight",
    "Your critical strikes have a 50% chance to generate 15 additional "
    "souls.",
    4, -2,
    proc={"trigger": "on_crit", "chance": 50, "icd": 0,
          "grant_resource": {"resource": "souls", "amount": 15}},
    connect=["blood_frenzy"],
    source="CoA: 'Critical strikes with Doomrend now refund a Reaped "
           "Soul.' Ports as a second soul grant on crit, stacking with Red "
           "Wake for a Reaper who takes both - which is CoA's intent, since "
           "the two talents sit in the same tree and do the same thing to "
           "different abilities. The Doomrend scoping goes (no per-ability "
           "proc trigger) and is priced down to a 50% chance in exchange. "
           "15 souls is what Doomrend itself generates, so a crit on it now "
           "pays double, exactly as CoA describes. Souls are a REAL "
           "resource here - thirteen abilities generate them - which is why "
           "this node does something and Chronomancer's Echo Fragment "
           "equivalents could not."))

N.append(node(
    "ruin", "Ruin",
    "Your attacks have a 30% chance to mark the target, increasing the "
    "damage they take by 10% for 3 turns.",
    4, 0,
    proc={"trigger": "on_weapon_swing", "chance": 30, "icd": 0,
          "apply_effect": {"effect_id": "ruin", "name": "Ruin",
                           "effect_type": "debuff", "duration": 3,
                           "stat_mods": {"damage_taken_pct": 0.10},
                           "dispel_type": "magic", "on_target": True}},
    connect=["deathbringer"],
    source="CoA: 'Damage dealt by Murder now applies Ruin to enemies for 10 "
           "sec. Ruin increases damage taken by Doomrend and Slaughter by "
           "25% for 10 sec. Using Doomrend on a target afflicted by Ruin "
           "will increase your haste by 15% for 5 sec.' The debuff ports; "
           "the per-ability scoping does not (a status effect cannot carry "
           "a per-ability damage-taken key), so it becomes a general "
           "damage-taken increase at 10%. The haste clause needs to read "
           "the target's debuffs, which nothing does. 10 sec -> 3 turns. "
           "CAREFUL: bare damage_taken_pct is read RAW ON BOTH SIDES - "
           "character.py:2697 and monster.py add the status mod with no "
           "division, unlike physical_ and magic_, which divide by 100 - so "
           "0.10 is 10% and authoring 10 would be +1000% damage taken. "
           "Asserted in main()."))

N.append(node(
    "doomer", "Doomer",
    "Increases the damage of Doomrend and Slaughter by 30%.",
    4, 3,
    effects={"ability_reaper_doomrend_damage": 0.30,
             "ability_reaper_slaughter_damage": 0.30},
    connect=["executioner"],
    source="CoA: 'Increases the damage of Doomrend and Slaughter by 30%.' "
           "PORTS EXACTLY, both abilities. Stacks with Genocide's 20% on "
           "Slaughter for a Reaper who takes both, which is CoA's own "
           "arrangement. Was a pure scalar on our side. Both FRACTIONS."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "blood_frenzy", "Blood Frenzy",
    "Teaches Blood Frenzy, a rising tide of shadow that breaks at the end.",
    5, -1,
    effects={"unlock_ability": "reaper_blood_frenzy"},
    connect=["deathbringer"],
    source="CoA: 'Casting Harvest Time with an enemy targeted now unleashes "
           "a Blood Frenzy. Deals Shadow Damage to your target every 0.75 "
           "sec for 7.5 seconds. At the end of the duration, the target "
           "takes an additional 457 + 45% AP Shadow Damage.' LOAD-BEARING "
           "UNLOCK - reaper_blood_frenzy carries requires_talent and this "
           "is its only unlock node. CoA has it fire automatically off "
           "Harvest Time, which needs a per-ability trigger that does not "
           "exist, so it stays a castable. The end-of-duration burst "
           "cannot be built: no trigger fires on an effect EXPIRING, which "
           "is the same gap that killed Chronomancer's End of Time and The "
           "Vast Infinite."))

N.append(node(
    "executioner", "Executioner",
    "Increases your critical strike chance by 20% of your Strength, and "
    "your damage against enemies below 35% health by a further 25%.",
    5, 1,
    effects={"crit_chance_from_strength_pct": 0.20,
             "low_health_damage_pct": 0.25,
             "low_health_threshold_pct": 0.35},
    connect=["deathbringer"],
    source="CoA level 40 passive: 'Increases your critical strike rating by "
           "20% of your Strength. In addition, increases your Armor "
           "penetration by 30% against enemies below 35% health.' BOTH "
           "HALVES BUILD. The conversion is a LEGAL PAIR nobody had used "
           "before: 'crit_chance' is in STAT_CONVERSION_TARGETS (mapping to "
           "crit_chance_physical) and 'strength' is in "
           "STAT_CONVERSION_SOURCES. A conversion target must name a REAL "
           "attribute - 'block' wrote a phantom one for months and killed "
           "Sun Cleric Seraphim's Clarity of the Heavens outright - and "
           "crit_chance_physical is real. The armour-penetration half "
           "becomes conditional damage instead: armor_penetration is live "
           "(monster.py:659) but FLAT, so a '30%' of it has no meaning. "
           + EXECUTE + " THIS IS THE ONE NODE IN THE TREE THAT SETS "
           "low_health_threshold_pct, deliberately: that key SUMS across "
           "talents, so a second node setting it would push the window to "
           "70% rather than 35%. 0.35 restates the engine default "
           "explicitly so CoA's own number is recorded rather than "
           "inherited by accident. Asserted in main()."))

N.append(node(
    "unbound", "Unbound",
    "Increases the damage of Reliquary of the Lost by 40% and your "
    "physical critical damage by a further 15%.",
    5, 4,
    effects={"ability_reaper_reliquary_of_the_lost_damage": 0.40,
             "crit_damage_physical": 0.15},
    connect=["executioner"],
    source="CoA: 'Your Reliquary of the Lost is now guaranteed to "
           "critically strike for 25% increased damage on enemies below 20% "
           "health.' Three separate problems: nothing grants a guaranteed "
           "crit on a specific ability; a second low_health_threshold_pct "
           "would SUM with Executioner's and move the whole tree's window "
           "to 55%; and CoA's 20% differs from the 35% every other node "
           "here uses. Rebuilt as flat per-ability damage plus crit damage, "
           "which is where a guaranteed crit would have landed anyway."))

N.append(node(
    "callous_soul", "Callous Soul",
    "Increases your armor penetration by 60.",
    1, 2,
    effects={"armor_penetration": 60},
    connect=["genocide"],
    source="CoA: 'Increases the amount of armor Soulrend causes you to "
           "ignore by 10%.' armor_penetration is live (monster.py:659, via "
           "_pen_flat) but FLAT, not proportional, so CoA's '10% more of an "
           "amount' has no expressible form - there is no armor_pen_pct key "
           "and inventing one would have been silent. Built as a flat 60 "
           "rating, and generalised off Soulrend because the key is "
           "attacker-side and global rather than per-ability. A FLAT "
           "RATING, deliberately not a fraction, which is why the value "
           "looks out of place next to this tree's 0.x effects."))

N.append(node(
    "blood_wraith", "Blood Wraith",
    "Increases the damage of Wraithblade by 50% and reduces its mana cost "
    "by a further 15%.",
    4, 5,
    effects={"ability_reaper_wraithblade_damage": 0.50,
             "ability_reaper_wraithblade_cost_pct": 0.15},
    connect=["executioner"],
    source="CoA: 'Wraithblade now deals an additional 100% Weapon Damage "
           "and its Runic Power cost is reduced by -20.' Both halves port - "
           "CoA's Runic Power is our mana - with the damage priced at 50% "
           "rather than 100% because Wraithblade is already this class's "
           "biggest soul generator at 25 and Dark Fate at tier 0 discounts "
           "it too. Stacking the two cost reductions reaches 35%, and "
           "*_cost_pct is a FRACTION where POSITIVE MEANS A REDUCTION."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "deathbringer", "Deathbringer",
    "Doubles the duration of Blood Frenzy and Harvest Time, increases your "
    "damage against enemies below 35% health by a further 30%, and your "
    "critical strikes generate 20 additional souls.",
    6, 0,
    effects={"ability_reaper_blood_frenzy_duration": 3,
             "ability_reaper_harvest_time_duration": 3,
             "low_health_damage_pct": 0.30},
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "souls", "amount": 20}},
    source="CoA: 'Doubles the duration of Blood Frenzy, Harvest Time, and "
           "Harvesting Grounds.' The two buildable halves port as flat "
           "per-ability duration extensions - talented_duration reads "
           "ability_<id>_duration and POSITIVE EXTENDS, and it went unread "
           "for long enough that Tinker's Fuel Injection on Mechsuit Form "
           "did nothing at all. Harvesting Grounds is dropped (a "
           "persistent ground effect that pulls fleeing enemies back has no "
           "positioning to stand on). Folded in the tree's two running "
           "themes so the capstone is a payoff rather than a duration "
           "footnote: a third helping of execute damage, and a third soul "
           "grant on crit stacking with Red Wake and Blood Knight - a "
           "fully-talented Reaper crit generates 45 souls, which is three "
           "fragments in this economy's units and is what CoA's "
           "stacked-refund talents amount to. The duration values are "
           "SMALL INTEGERS IN TURNS, so talent_ranks.spread() refuses to "
           "rank this node, which is correct."))


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

    # low_health_threshold_pct SUMS across talents (it is in
    # UNSCALED_EFFECT_KEYS so it does not scale with rank, but it still
    # adds). Tinker once had two summing to 0.8, i.e. "below 80% health",
    # which is most of a fight. Exactly one node here may set it.
    setters = [n["talent_id"] for n in TREE["nodes"]
               if "low_health_threshold_pct" in (n.get("effects") or {})]
    assert len(setters) == 1, (
        f"low_health_threshold_pct SUMS across talents, so two nodes "
        f"setting 0.35 give 'below 70% health', not 35%. Exactly one node "
        f"may set it; found {setters}")

    # Extinction's whole mechanic is a nested proc inside an apply_effect,
    # which the audit does not inspect - there is no static safety net on
    # it, so assert it here.
    ext = next(n for n in TREE["nodes"]
               if n["talent_id"] == "reaper_harvest_extinction")
    assert (ext["proc"]["apply_effect"].get("proc", {})
            .get("bypass_execute_threshold")), (
        "Extinction IS the bypass_execute_threshold flag - without the "
        "nested proc it applies an empty buff and the talent does nothing "
        "at all, while passing every check in the project")

    # Bare damage_taken_pct is RAW on both sides, unlike physical_/magic_,
    # which are divided by 100 inside a status effect.
    for n in TREE["nodes"]:
        mods = ((n.get("proc") or {}).get("apply_effect") or {}).get("stat_mods") or {}
        if "damage_taken_pct" in mods:
            assert -1 < mods["damage_taken_pct"] < 1, (
                f"{n['talent_id']} damage_taken_pct={mods['damage_taken_pct']}"
                f" - read RAW on both sides, so 10 means +1000%, not +10%")
        gr = (n.get("proc") or {}).get("grant_resource")
        if gr:
            assert gr.get("resource") == "souls" and "amount" in gr, (
                f"{n['talent_id']} grant_resource must name souls (Reaper's "
                f"real secondary, with 13 generators) and carry a FLAT "
                f"`amount` - the only field status_effects.py:1337 reads")

    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Reaper Harvest: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points, {len(GATED)} load-bearing unlocks")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
