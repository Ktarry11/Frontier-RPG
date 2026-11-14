#!/usr/bin/env python3
"""Rebuild Felsworn's Slayer tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_felsworn_slayer.py [--check]

SOURCE: data/reference/coa_worksheets/felsworn.md - 38 real Slayer
talents. Role: DPS (dual-wield melee). Slayer was 23 nodes with 5 procs.
49 of Felsworn's 66 matched talents were pure scalars.

CoA SPLITS ITS RESOURCE IN TWO AND WE HAVE ONE POOL. CoA's Felsworn spends
"Energy" and separately banks 0-5 "Felfury" as a point mechanic. Ours is
(ResourceType.FELFURY, None) - felfury is the single PRIMARY pool - and
eleven abilities generate it (twin_slice 20, annihilan_strike 25,
burning_hatred 40, glaiving, chaos_rush, felhoof_charge, felrend,
fury_of_the_illidari, bane_of_chaos, fel_fireball, demonic_will). So CoA's
Energy costs and its Felfury generation BOTH land on felfury, and the
"consumes 2 Felfury" gating has nothing separate to consume. Every
"spender" and "generator" talent therefore works; the two-currency
interplay does not.

THE AVOIDANCE AND EXPERTISE KEYS ARE LIVE AS OF 5 Nov 2026, when Kyle had
creature avoidance added (dodge on every template, parry on humanoids).
Azzinoth's Rage's "+4 expertise" ports for real - that key was read by
nothing for most of this audit and cost Guardian's Stalwart and Gladiator's
Double Duty their text - and Spite's and Unbound's dodge is worth having.

WHAT COULD NOT BE BUILT, each recorded on its node where one survives:
  - EVERY "while Inner Demon is active" clause - True Self, Blighted
    Strikes, Chaotic, Fel Haze, Felguard's second half. Nothing reads
    whether another effect is live. That is five talents in this tree
    alone, and it is CoA's main Slayer conditional.
  - Every "above 75% health" clause - You Cheat, Gul'dan! and Annihilan
    Strike's guaranteed crit. high_health_damage_threshold_pct is dead
    data, authored and read by nothing, and there is no guaranteed-crit
    key either.
  - Off-hand weapon damage (Slice & Dice, Infernal Constitution) - the
    engine's weapon roll does not separate hands.
  - Weapon-type gates (Reckless Assault's slowed enemies, the
    one-handed/polearm requirements) and "against slowed enemies", which
    needs to read a target's debuffs.
  - Felguard's party haste aura - Felsworn has no aura ABILITY for this
    one to modify, unlike Infernal's Fel Infusion and Tyrant's Eye of the
    Tyrant and Infernal Whipcrack, all three of which were converted to
    target_type "party" on 6 Nov 2026. A talent effect can never reach an
    ally, so this half is simply dropped rather than faked.
  - Dancing Blades (the shared level-10 passive) and everything keyed on
    it - Nether Champion, Perpetual Fury. It is an on-crit cleave that
    would need to be an ability first.
  - Consumed By Fel changes Immolation Aura's "tick rate", meaningless at
    one tick per turn.
  - Azzinoth's Battery and Infernal Doom ("chance not to consume Felfury")
    - nothing intercepts a resource SPEND, only grants.

Tyrant owns low_health_threshold_pct for the class at CoA's 35%, which is
what felsworn_tyrants_gaze already carries as its execute_threshold_pct.
Nothing here sets it. Enforced by tools/qa_summing_thresholds.py.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/felsworn_slayer.json"

TREE = {
    "spec_name": "Felsworn Slayer",
    "tree_id": "felsworn_slayer",
    "description": ("Two glaives and no patience - crits that feed "
                    "themselves and a cooldown that resets on contact."),
    "_source_note": (
        "Rebuilt 6 Nov 2026 from the 38 real CoA Slayer talents (role DPS). "
        "CoA splits Energy and Felfury into two currencies and we have one "
        "pool (FELFURY, primary, eleven generators), so costs and "
        "generation both land on it while the two-currency interplay does "
        "not. Expertise and dodge are live keys only since creature "
        "avoidance landed on 5 Nov 2026. Five talents die on 'while Inner "
        "Demon is active' and two more on 'above 75% health', neither of "
        "which the engine can read."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20,
                          "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"felsworn_slayer_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"felsworn_slayer_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


DEMON = ("CoA gates this on INNER DEMON BEING ACTIVE. Nothing reads whether "
         "another effect is live - the same gap that killed Hard Bargain, "
         "Pathfinder, Chaos Fusion and Permafrost on other classes - so the "
         "condition is dropped and the node priced for being unconditional. "
         "Five Slayer talents carry this gate; it is CoA's main conditional "
         "for the spec.")

HIGH_HP = ("CoA gates this on the target being ABOVE 75% health. "
           "high_health_damage_threshold_pct is DEAD DATA - authored "
           "somewhere in this project and read by nothing - and there is no "
           "above-health conditional of any kind, only the below-health "
           "low_health_damage_pct added 6 Nov 2026. Dropped.")

N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "azzinoths_rage", "Azzinoth's Rage",
    "Increases your armor penetration by 120 and your expertise by 12.",
    0, -4,
    effects={"armor_penetration": 120, "expertise": 12.0},
    connect=["spite"],
    source="CoA over 3 ranks: 'Increases your Armor penetration by 10% and "
           "your expertise by 4.' BOTH HALVES PORT, and the second would "
           "not have a day ago: `expertise` was read by NO engine code for "
           "most of this audit - it reduces a target's dodge and parry, and "
           "monsters had neither - which cost Guardian's Stalwart and "
           "Gladiator's Double Duty their text outright. Kyle had creature "
           "avoidance added on 5 Nov 2026 (dodge on every template, parry "
           "on humanoids) and expertise became a real stat. It is in "
           "PERCENTAGE POINTS and subtracts from dodge AND parry "
           "independently. armor_penetration is FLAT, not proportional, so "
           "CoA's '10%' has no expressible form - there is no armor_pen_pct "
           "key. Both tripled for the three ranks. Was a pure scalar on our "
           "side."))

N.append(node(
    "spite", "Spite",
    "Increases your Agility by 16% and your dodge by 6%.",
    0, -2,
    effects={"agility_pct": 16, "dodge": 6.0},
    connect=["chaos_soldier", "twin_fury"],
    source="CoA over 2 ranks: 'Increases your Agility by 8% and dodge "
           "chance by 3%.' PORTS EXACTLY, doubled. NOTE `dodge` IS THE LIVE "
           "KEY: `dodge_chance` is dead data that several talents in this "
           "project author, and the same trap exists for parry/parry_chance "
           "and block/block_chance. agility_pct is PERCENTAGE POINTS "
           "(character.py:1266 divides by 100) and so is dodge - two keys, "
           "same convention for once. Was a pure scalar on our side."))

N.append(node(
    "chaos_soldier", "Chaos Soldier",
    "Increases the critical strike chance of Azzinoth's Assault and "
    "Sargeron Smite by 10%.",
    0, 0,
    effects={"ability_felsworn_azzinoths_assault_crit": 10.0,
             "ability_felsworn_sargeron_smite_crit": 10.0},
    connect=["legionfall"],
    source="CoA: 'Increases the critical strike chance of Azzinoth's "
           "Assault and Sargeron Smite by 5%.' PORTS EXACTLY, both "
           "abilities, doubled. This tree keys off crits five times "
           "(Twin Fury, Legionfall, Demonic Machinations, Oblivion, the "
           "capstone), so crit chance is its real currency. Per-ability "
           "crit keys are PERCENTAGE POINTS. Was a pure scalar on our "
           "side."))

N.append(node(
    "unbound", "Unbound",
    "Increases your dodge by 15% of your Agility.",
    0, 2,
    effects={"dodge_from_agility_pct": 0.15},
    connect=["fel_blades"],
    source="CoA level 30 passive: 'Increases your dodge by 15% of your "
           "Agility and your hit rating by 6% of your Agility.' The dodge "
           "half PORTS EXACTLY - dodge is in STAT_CONVERSION_TARGETS and "
           "agility in STAT_CONVERSION_SOURCES, a legal pair. The hit half "
           "is DROPPED: hit_rating is NOT a valid conversion target, which "
           "with stamina has now cost nine nodes half their text across "
           "eight classes and is the most-repeated mistake in this audit. "
           "A conversion target must name a REAL attribute - 'block' wrote "
           "a phantom one for months and silently killed Sun Cleric "
           "Seraphim's Clarity of the Heavens. A FRACTION. Was a pure "
           "scalar on our side."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "twin_fury", "Twin Fury",
    "Your critical strikes generate 10 Felfury.",
    1, -1,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "felfury", "amount": 10}},
    connect=["fel_instincts"],
    source="CoA: 'Critically striking with Twin Slice or Annihilan Strike "
           "now generates an additional 1 Felfury.' PORTS ALMOST VERBATIM - "
           "only the two-ability scoping goes, since there is no "
           "per-ability proc trigger. CoA'S TWO CURRENCIES COLLAPSE INTO "
           "ONE HERE: CoA banks Felfury as a 0-5 point mechanic separate "
           "from the Energy it spends, while ours is the single primary "
           "pool, so '1 Felfury' becomes 10 felfury - half what Twin Slice "
           "itself generates. grant_resource routes through the same "
           "gain_resource() the eleven generators use, so the cap holds, "
           "and its `amount` is FLAT (there is no pct_max field)."))

N.append(node(
    "legionfall", "Legionfall",
    "Your attacks have a 15% chance to reset the cooldown of Annihilan "
    "Strike.",
    1, 1,
    proc={"trigger": "on_weapon_swing", "chance": 15, "icd": 0,
          "reset_cooldown": ["felsworn_annihilan_strike"]},
    connect=["fel_instincts"],
    source="CoA: 'Melee ability damage now has a 15% chance to reset the "
           "cooldown of Annihilan Strike.' PORTS VERBATIM, chance included. "
           "reset_cooldown WITH A BARE LIST is a full reset, as against the "
           "{abilities, turns} form which only shaves turns - confusing the "
           "two is silent and easy. Annihilan Strike has a 3-turn cooldown "
           "and generates 25 felfury, the second-biggest generator, so this "
           "node is the spec's engine."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "fel_blades", "Fel Blades",
    "Your attacks have a 35% chance to strip the target's armor for 3 "
    "turns, stacking up to 5 times.",
    2, 2,
    proc={"trigger": "on_weapon_swing", "chance": 35, "icd": 0,
          "apply_effect": {"effect_id": "fel_blades", "name": "Fel Blades",
                           "effect_type": "debuff", "duration": 3,
                           "stat_mods": {"armor": -140},
                           "max_stacks": 5, "dispel_type": None,
                           "on_target": True}},
    connect=["demonic_machinations"],
    source="CoA: 'Damage dealt by Azzinoth's Assault now reduces the "
           "enemy's armor by -4% for 10 seconds, stacking 5 times.' The "
           "debuff and its 5 stacks port. Two departures: the "
           "Azzinoth's-Assault scoping goes (no per-ability proc trigger), "
           "and `armor` on a monster is FLAT - Monster.armor is "
           "max(0, base_armor + get_status_stat_mod('armor')) - so CoA's "
           "'-4%' becomes -140 per stack, -700 at five. armor is one of "
           "only eight status stat_mods a monster reads. 10 sec -> 3 turns. "
           "Was a pure scalar on our side."))

N.append(node(
    "fel_instincts", "Fel Instincts",
    "Increases the damage of Azzinoth's Assault by 20%, and your critical "
    "strikes increase your haste by 20% for 2 turns.",
    2, 0,
    effects={"ability_felsworn_azzinoths_assault_damage": 0.20},
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "apply_effect": {"effect_id": "fel_instincts",
                           "name": "Fel Instincts",
                           "effect_type": "buff", "duration": 2,
                           "stat_mods": {"haste": 20.0},
                           "dispel_type": None, "on_target": False}},
    connect=["a_thousand_cuts"],
    source="CoA: 'Increases the damage of Azzinoth's Assault by 10% and "
           "causes it to increase your melee haste by 20% for 5 seconds.' "
           "BOTH HALVES PORT, the second re-pointed from Azzinoth's Assault "
           "to any crit (no per-ability proc trigger) with a 1-turn "
           "internal cooldown so it cannot chain. The melee scoping on "
           "haste is dropped: there is no separate melee-haste key, only "
           "`haste`, which in a turn-based engine means acting more often. "
           "5 sec -> 2 turns, CoA's 20% kept verbatim. Was a pure scalar on "
           "our side."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "demonic_machinations", "Demonic Machinations",
    "Your critical strikes open a bleed dealing damage over 3 turns.",
    3, 2,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "apply_effect": {"effect_id": "demonic_machinations",
                           "name": "Demonic Machinations",
                           "effect_type": "dot", "duration": 3,
                           "potency": 30, "damage_school": "physical",
                           "dispel_type": None, "on_target": True}},
    connect=["pit_lords_strength"],
    source="CoA: 'Critical strikes with Sargeron Smite now cause the target "
           "to bleed for an additional 50% of the damage dealt over 5 sec.' "
           "PORTS ALMOST EXACTLY. Only the Sargeron-Smite scoping goes, and "
           "'50% of the damage dealt' becomes a fixed potency because "
           "apply_effect cannot read the triggering hit's amount - only "
           "bonus_pct, leech_pct and smart heals do, and none of those "
           "apply an effect. 5 sec -> 3 turns. A proc-applied dot carries "
           "`potency` as PER-TURN damage (30 a turn, 90 total) where an "
           "ABILITY rank's effect_value is the TOTAL and gets divided "
           "(abilities.py:2695)."))

N.append(node(
    "a_thousand_cuts", "A Thousand Cuts",
    "Your attacks have a 30% chance to strike an additional time.",
    3, 0,
    proc={"trigger": "on_weapon_swing", "chance": 30, "icd": 0,
          "extra_attack": True},
    connect=["scars_of_the_past"],
    source="CoA: 'Azzinoth's Assault now has a 30% chance to hit an "
           "additional time with your main-hand Weapon.' PORTS ALMOST "
           "VERBATIM - `extra_attack` is a BOOLEAN giving exactly one extra "
           "attack, which is precisely what CoA asks for here (unlike "
           "Ranger's Tip of the Spear, where CoA wanted three and the key "
           "cannot express it). The main-hand scoping is dropped: the "
           "engine's weapon roll does not separate hands, which is also why "
           "Slice & Dice and Infernal Constitution lose their off-hand "
           "clauses. The Azzinoth's-Assault scoping goes too (no "
           "per-ability proc trigger), and CoA's 30% is kept."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "pit_lords_strength", "Pit Lord's Strength",
    "Increases the damage of Annihilation and Annihilan Strike by 30%.",
    4, 2,
    effects={"ability_felsworn_annihilation_potency": 0.30,
             "ability_felsworn_annihilan_strike_damage": 0.30},
    connect=["oblivion"],
    source="CoA over 2 ranks: 'Your Annihilation now affects 1 additional "
           "attack.' Annihilation is a self-buff in our data, not an "
           "attack-counting mechanic, and nothing adds attacks to an "
           "ability (extra_attack is a proc payload, not an ability "
           "modifier), so the node becomes flat damage on both Annihilan "
           "abilities. Annihilan Strike generates 25 felfury. Both "
           "FRACTIONS."))

N.append(node(
    "scars_of_the_past", "Scars of the Past",
    "Reduces the cost of Chaos Rush by 25%, and your attacks have a 25% "
    "chance to heal you for 20% of the damage dealt.",
    4, 0,
    effects={"ability_felsworn_chaos_rush_damage": 0.25},
    proc={"trigger": "on_weapon_swing", "chance": 25, "icd": 0,
          "leech_pct": 20},
    connect=["oblivion"],
    source="CoA: 'Reduces the Energy cost of Chaos Rush by -5 and casting "
           "Chaos Rush now heals you for 81 + 20% Stamina + 33% AP.' Both "
           "halves port in shape. CoA's Energy is our felfury (the single "
           "primary pool), so the cost reduction is real. The heal becomes "
           "a leech off any swing rather than a flat Stamina/AP-scaled "
           "number on one ability: leech_pct is one of only THREE proc "
           "payloads that READ the triggering hit's amount, which makes it "
           "the honest way to express 'heals based on your attack power' - "
           "and it is the right trigger for it, unlike on an avoidance "
           "trigger where the amount is always zero. Folded in CoA's "
           "Felguard second clause ('while Inner Demon is active you heal "
           "for 15% of all melee damage dealt'): " + DEMON))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "oblivion", "Oblivion",
    "Your critical strikes increase your damage by 2% for 3 turns, "
    "stacking up to 10 times.",
    5, 0,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "oblivion", "name": "Oblivion",
                           "effect_type": "buff", "duration": 3,
                           "stat_mods": {"damage_dealt_pct": 2},
                           "max_stacks": 10, "dispel_type": None,
                           "on_target": False}},
    connect=["pit_lords_rage"],
    source="CoA: 'Critically striking now increases your damage dealt by 1% "
           "for 4 seconds, stacking 10 times.' PORTS ALMOST VERBATIM - "
           "trigger, 10 stacks and shape all intact, the rate doubled to 2% "
           "because 4 seconds is barely more than one turn and the window "
           "here is 3. max_stacks is genuinely honoured even though nothing "
           "can READ the count. damage_dealt_pct is PERCENTAGE POINTS "
           "inside a status effect, which is the BUFF-side companion to the "
           "talent damage keys. Was a pure scalar on our side."))

N.append(node(
    "you_cheat_guldan", "You Cheat, Gul'dan!",
    "Increases your physical critical damage by 50%.",
    5, 2,
    effects={"crit_damage_physical": 0.50},
    connect=["pit_lords_rage"],
    source="CoA: 'Increases your critical damage by 50% against enemies "
           "above 75% health.' " + HIGH_HP + " So CoA's 50% is kept "
           "unconditional, which is a straight buff relative to CoA and is "
           "flagged as such rather than quietly pocketed - the alternative "
           "was a node that silently never fired. Folded in Annihilan "
           "Strike's 'guaranteed to critically strike against enemies above "
           "75% health', which fails for the same reason plus a second one: "
           "nothing grants a guaranteed crit on a specific ability. "
           "crit_damage_* keys are FRACTIONS, unlike the crit_chance_* "
           "family. Was a pure scalar on our side."))

N.append(node(
    "burning_rage", "Burning Rage",
    "Increases the damage of Sunder and Immolation Aura by 20% and reduces "
    "their cost by 20%.",
    1, -4,
    effects={"ability_felsworn_sunder_damage": 0.20,
             "ability_felsworn_immolation_aura_damage": 0.20,
             "ability_felsworn_sunder_cost_pct": 0.20,
             "ability_felsworn_immolation_aura_cost_pct": 0.20},
    connect=["azzinoths_rage"],
    source="CoA: 'Increases the damage and reduces the cost of Sunder and "
           "Immolation Aura by 20%.' PORTS VERBATIM, both halves and both "
           "abilities - one of the few CoA talents in this tree that needs "
           "no translation at all. Immolation Aura is a fire dot at "
           "target_type enemy_aoe. *_damage keys are FRACTIONS; *_cost_pct "
           "keys are fractions too, but POSITIVE MEANS A REDUCTION, which "
           "is the opposite sign convention from most of this file."))

N.append(node(
    "glaiving", "Glaiving",
    "Increases the damage of Fury Unleashed and Glaiving by 40% and "
    "reduces Fury Unleashed's cost by 30%.",
    2, -2,
    effects={"ability_felsworn_fury_unleashed_damage": 0.40,
             "ability_felsworn_glaiving_damage": 0.40,
             "ability_felsworn_fury_unleashed_cost_pct": 0.30},
    connect=["spite"],
    source="CoA: 'Increases the damage dealt and reduces the Energy cost of "
           "Fury Unleashed by 50%.' PORTS EXACTLY (40%/30%), extended to "
           "Glaiving, which generates 20 felfury and had no node. CoA's "
           "Energy is our felfury - the single primary pool - so the cost "
           "reduction is real. Fury Unleashed is CoA's 5-second spinning "
           "channel; ours is a 6-turn-cooldown AoE strike, since there is "
           "no channelling, which also drops its movement-speed and "
           "CC-immunity clauses."))

N.append(node(
    "reachwalker", "Reachwalker",
    "Reduces the cooldown of Felhoof Charge, Chaos Rush and Fury of the "
    "Illidari by 35%.",
    3, -2,
    effects={"ability_felsworn_felhoof_charge_cooldown_pct": 0.35,
             "ability_felsworn_chaos_rush_cooldown_pct": 0.35,
             "ability_felsworn_fury_of_the_illidari_cooldown_pct": 0.35},
    connect=["fel_blades"],
    source="CoA: 'Casting Chaos Rush now reduces the cooldown of Felhoof "
           "Charge by 2 sec.' The proc form cannot be built (no per-ability "
           "proc trigger) so it becomes a flat reduction, extended to both "
           "named abilities plus Fury of the Illidari. Folded in CoA's "
           "Perpetual Fury, which reduces Fury Unleashed's cooldown off "
           "Dancing Blades - an on-crit cleave that does not exist as an "
           "ability here, so nothing can trigger off it. FRACTIONS where "
           "POSITIVE MEANS A REDUCTION; talented_cooldown floors at 1 turn, "
           "so stacking these cannot make the abilities spammable."))

N.append(node(
    "felcaked_blades", "Felcaked Blades",
    "Increases your attack power by 20% of your Agility and the damage of "
    "Twin Slice by 25%.",
    4, -2,
    effects={"attack_power_from_agility_pct": 0.20,
             "ability_felsworn_twin_slice_damage": 0.25},
    connect=["demonic_machinations"],
    source="CoA level 50 passive: 'Twin Slice and Sargeron Smite now "
           "additionally scale with your Agility.' A per-ability stat "
           "SCALING coefficient is not something any key reaches - the "
           "ability keys are _damage, _healing, _crit, _crit_damage, _cost, "
           "_cooldown, _duration and _potency, and none touch how an "
           "ability scales off a stat. Built as a real global conversion "
           "instead: attack_power is in STAT_CONVERSION_TARGETS and agility "
           "in SOURCES, a legal pair, so a Slayer's Agility genuinely "
           "becomes attack power and reaches every ability rather than two. "
           "Plus flat damage on Twin Slice, the spec's filler and a "
           "20-felfury generator. Both FRACTIONS."))

N.append(node(
    "whirling_vengeance", "Whirling Vengeance",
    "Reduces the cooldown of Fury Unleashed by 40%, and your attacks have "
    "a 30% chance to leave the target taking 12% more damage for 3 turns.",
    5, -2,
    effects={"ability_felsworn_fury_unleashed_cooldown_pct": 0.40},
    proc={"trigger": "on_weapon_swing", "chance": 30, "icd": 0,
          "apply_effect": {"effect_id": "whirling_vengeance",
                           "name": "Whirling Vengeance",
                           "effect_type": "debuff", "duration": 3,
                           "stat_mods": {"damage_taken_pct": 0.12},
                           "dispel_type": None, "on_target": True}},
    connect=["a_thousand_cuts"],
    source="CoA: 'Reduces the cooldown of Fury Unleashed by -60 sec. When "
           "Fury Unleashed ends, you strike all nearby enemies for "
           "Shadowflame Damage and increase their damage taken from Sunder "
           "by 100% for 15 seconds.' The cooldown ports. THE SECOND HALF "
           "NEEDS AN ON-EXPIRY TRIGGER, which does not exist - no trigger "
           "fires when an effect ends, the same gap that killed "
           "Chronomancer's End of Time and The Vast Infinite, Reaper's "
           "Blood Frenzy burst and Painmail, and Ranger's Chasing Death. So "
           "the damage-taken debuff is re-pointed to a swing proc and "
           "widened from Sunder-only to all damage at 12% rather than 100%. "
           "CAREFUL: bare damage_taken_pct is read RAW ON BOTH SIDES - "
           "unlike physical_ and magic_, which divide by 100 inside a "
           "status effect - so 0.12 is 12% and authoring 12 would be "
           "+1200%. Was a pure scalar on our side."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "pit_lords_rage", "Pit Lord's Rage",
    "Increases your physical damage by 15% and your critical strike chance "
    "by 6%, and your critical strikes generate a further 10 Felfury.",
    6, 0,
    effects={"physical_damage": 0.15, "crit_chance_physical": 6.0},
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "felfury", "amount": 10}},
    source="CoA: 'Casting Chaos Rush now increases your Physical damage by "
           "15% for 10 sec. Casting Felhoof Charge increases your critical "
           "strike chance by 6% for 15 sec.' Both values port verbatim; "
           "what cannot is their per-ability triggering, since there is no "
           "per-ability proc trigger, so two short windows become two "
           "passives. The felfury grant stacks with Twin Fury so a "
           "fully-talented Slayer banks 20 per crit - which is one full "
           "Twin Slice's worth, and the closest this single-pool engine "
           "gets to CoA's separate 0-5 Felfury bank filling up. Was a pure "
           "scalar on our side. physical_damage is a FRACTION; "
           "crit_chance_physical is percentage points."))


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
        f"Felsworn Tyrant owns low_health_threshold_pct for this class at "
        f"CoA's 35% (which felsworn_tyrants_gaze already carries as its "
        f"execute_threshold_pct), and the key SUMS across talents. "
        f"Found {setters}")

    for n in TREE["nodes"]:
        eff = n.get("effects") or {}
        # dodge_chance / parry_chance / block_chance are DEAD keys that
        # several talents in this project author. The live names have no
        # _chance suffix.
        for dead in ("dodge_chance", "parry_chance", "block_chance"):
            assert dead not in eff, (
                f"{n['talent_id']} authors {dead}, which is read by no "
                f"engine code - the live key is {dead.replace('_chance','')}")
        proc = n.get("proc") or {}
        gr = proc.get("grant_resource")
        if gr:
            assert gr.get("resource") == "felfury" and "amount" in gr, (
                f"{n['talent_id']} grant_resource must name felfury "
                f"(Felsworn's single primary pool, eleven generators) with "
                f"a FLAT amount")
        if proc.get("trigger") in ("on_avoid", "on_parry", "on_dodge",
                                   "on_block"):
            for payload in ("leech_pct", "bonus_pct", "smart_heal_pct"):
                assert payload not in proc, (
                    f"{n['talent_id']} uses {payload} on "
                    f"{proc['trigger']} - an avoided attack deals 0 damage, "
                    f"so it silently yields nothing")

    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Felsworn Slayer: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
