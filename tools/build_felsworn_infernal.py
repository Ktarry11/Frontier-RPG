#!/usr/bin/env python3
"""Rebuild Felsworn's Infernal tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_felsworn_infernal.py [--check]

SOURCE: data/reference/coa_worksheets/felsworn.md - 38 real Infernal
talents. Role: DPS (caster). Infernal was 23 nodes with 6 procs.

SHADOWFLAME IS A COMBINED SCHOOL AND THE ENGINE HANDLES IT PROPERLY, which
is the find that shapes this tree. Felsworn's caster abilities carry
damage_school ["shadow", "fire"] - fel_fireball, sunder, ruin, felwrath,
felstrike, tyrants_gaze - and _school_damage_bonus (abilities.py:1358-1372)
walks EVERY component of a school list, so a shadow_spell_damage talent and
a fire_spell_damage talent BOTH apply to a Shadowflame spell. Its docstring
says so: "Bailing out on those meant a combined-school ability could never
receive ANY school damage bonus". Combined KEYS like shadow_fire_spell_damage
also match if any named component is the ability's real school.

These keys are built with f-strings, so a literal grep finds nothing - I
had already wrongly published arcane_spell_damage as dead on that basis
earlier the same day and had to correct the record. Measured live before
trusting them. main() pins every school name used here to one Felsworn
actually deals, because a typo would be SILENT: no grep and no audit can
see a dynamically built key.

CoA'S TWO CURRENCIES COLLAPSE INTO ONE. CoA spends "Energy" and banks 0-5
"Felfury"; ours is (ResourceType.FELFURY, None), a single primary pool with
eleven generators. So Illidari Smiter, Illidari Magi and Doomsayer's
generation clauses all land, while the "consumes 2 Felfury" gating and
Azzinoth's Battery / Infernal Doom ("chance not to consume Felfury") do
not - nothing intercepts a resource SPEND, only grants.

FEL INFUSION'S PARTY HALF IS REAL because the ABILITY was converted from
target_type "self" to "party" on 6 Nov 2026, the same call Kyle made for
Guardian's four auras. A talent effect can never reach an ally.

NOT BUILDABLE: every "while Inner Demon is active" clause (Dark Magician,
Hidden Power's second half, Unphased's second half) and every "above 75%
health" clause (Fel Cannon, Doomsayer's second half) - nothing reads
whether an effect is live, and high_health_damage_threshold_pct is dead
data; Felforged, Sculptor of Doom, The True Blessing and Gul'dan's Prodigy
are cast-time mechanics; Infernal Ruin and Fury of Archimonde need a cast
counter or a cumulative-resource counter; Curse of Argus and Chaotic
Intuition need a readable stack count; Herald of the Legion and Fel
Flamecasting spread effects to other targets; Felbreak needs an interrupt
key; Archimonde's Wrath scales off the live resource amount, which nothing
reads.

Tyrant owns low_health_threshold_pct for the class at CoA's 35%.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/felsworn_infernal.json"

#: Schools Felsworn actually deals. Asserted against every per-school key.
REAL_SCHOOLS = {"shadow", "fire", "physical"}

TREE = {
    "spec_name": "Felsworn Infernal",
    "tree_id": "felsworn_infernal",
    "description": ("Shadowflame - fel magic that banks its own fury and "
                    "drops infernals when it crits."),
    "_source_note": (
        "Rebuilt 6 Nov 2026 from the 38 real CoA Infernal talents (role "
        "DPS, caster). Shadowflame is a COMBINED school (['shadow','fire']) "
        "and _school_damage_bonus walks every component, so both "
        "shadow_spell_damage and fire_spell_damage apply to the spec's "
        "Shadowflame spells - verified live after wrongly calling "
        "arcane_spell_damage dead earlier the same day. CoA's Energy and "
        "Felfury collapse into our single felfury pool. Fel Infusion's "
        "party half is real only because the ABILITY was converted to "
        "target_type 'party'. Five talents die on 'while Inner Demon is "
        "active' and two on 'above 75% health'."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20,
                          "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"felsworn_infernal_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"felsworn_infernal_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


DEMON = ("CoA gates this on INNER DEMON BEING ACTIVE, and nothing reads "
         "whether another effect is live. Dropped, with the value priced "
         "unconditional. Five Infernal talents carry this gate.")

HIGH_HP = ("CoA gates this on the target being ABOVE 75% health. "
           "high_health_damage_threshold_pct is DEAD DATA and there is no "
           "above-health conditional of any kind - only the below-health "
           "low_health_damage_pct added 6 Nov 2026. Dropped.")

N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "wrath_of_sargeras", "Wrath of Sargeras",
    "Increases your Shadow and Fire damage by 6% and your hit chance by 4%.",
    0, -4,
    effects={"shadow_spell_damage": 0.06, "fire_spell_damage": 0.06,
             "hit_rating": 4.0},
    connect=["felfire_adept"],
    source="CoA over 2 ranks: 'Increases your Magic damage dealt by 3% and "
           "your spell hit chance by 2%.' PORTS EXACTLY, doubled. 'Magic "
           "damage' on this class means Shadowflame, which carries "
           "damage_school ['shadow','fire'] - and _school_damage_bonus "
           "WALKS EVERY COMPONENT OF A SCHOOL LIST (abilities.py:1358-1372, "
           "whose own comment says bailing out on lists 'meant a "
           "combined-school ability could never receive ANY school damage "
           "bonus'), so both keys apply to every Shadowflame spell and "
           "stack. Authoring the two separately rather than a combined "
           "shadow_fire_spell_damage key also means they reach the spec's "
           "pure-shadow abilities (sargeron_smite, bane_of_chaos) and pure "
           "fire (immolation_aura). hit_rating is live as a FLAT bonus in "
           "PERCENTAGE POINTS - it is only invalid as a CONVERSION target. "
           "The two school keys are FRACTIONS. Was a pure scalar on our "
           "side."))

N.append(node(
    "felfire_adept", "Felfire Adept",
    "Increases the critical strike chance of Sargeron Smite and Fel "
    "Fireball by 10%.",
    0, -2,
    effects={"ability_felsworn_sargeron_smite_crit": 10.0,
             "ability_felsworn_fel_fireball_crit": 10.0},
    connect=["black_magic", "hidden_power"],
    source="CoA over 2 ranks: 'Increases the critical strike chance of "
           "Sargeron Smite by 10%.' PORTS EXACTLY, extended to Fel "
           "Fireball, which four other nodes in this tree read. This spec "
           "keys off crits six times, so crit chance is its real currency. "
           "Per-ability crit keys are PERCENTAGE POINTS. Was a pure scalar "
           "on our side."))

N.append(node(
    "hidden_power", "Hidden Power",
    "Increases your spell damage by 15% of your Intellect and 15% of your "
    "Spirit.",
    0, 0,
    effects={"spell_damage_from_intellect_pct": 0.15,
             "spell_damage_from_spirit_pct": 0.15},
    connect=["illidari_smiter"],
    source="CoA level 20 passive: 'Increases your spell damage by 15% of "
           "your Intellect and Spirit. In addition, Inner Demon now "
           "increases your spell damage and critical strike chance by an "
           "additional 20% of your Spirit.' THE FIRST HALF PORTS EXACTLY as "
           "two conversions - spell_damage is in STAT_CONVERSION_TARGETS "
           "and both intellect and spirit are in SOURCES, so both pairs are "
           "legal. " + DEMON + " Both FRACTIONS. Was a pure scalar on our "
           "side."))

N.append(node(
    "black_magic", "Black Magic",
    "Increases the damage of Bane of Chaos and Ruin by 20%.",
    0, 2,
    effects={"ability_felsworn_bane_of_chaos_damage": 0.20,
             "ability_felsworn_ruin_damage": 0.20},
    connect=["nether_spirit"],
    source="CoA over 2 ranks: 'Increases the damage of your Bane of Chaos "
           "and Ruin by 10%.' PORTS EXACTLY, both abilities, doubled. Bane "
           "of Chaos is a shadow spell_dot that generates 20 felfury; Ruin "
           "is the spec's Shadowflame nuke. Both FRACTIONS. Was a pure "
           "scalar on our side."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "illidari_smiter", "Illidari Smiter",
    "Your critical strikes generate 10 Felfury.",
    1, 0,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "felfury", "amount": 10}},
    connect=["cursed_flames", "illidari_magi"],
    source="CoA: 'Critical strikes with Fel Fireball now generate 1 "
           "Felfury.' PORTS ALMOST VERBATIM; only the Fel-Fireball scoping "
           "goes (no per-ability proc trigger). Folded in CoA's Doomsayer "
           "('critical strikes with Sargeron Smite now refund 1 Felfury'), "
           "which is the same mechanic on a different ability - its second "
           "clause, +25% damage above 75% health, fails: " + HIGH_HP + " "
           "CoA banks Felfury as a 0-5 point mechanic separate from the "
           "Energy it spends; ours is the single primary pool, so '1 "
           "Felfury' becomes 10 felfury - half what Fel Fireball itself "
           "generates. grant_resource's `amount` is FLAT; there is no "
           "pct_max field."))

N.append(node(
    "nether_spirit", "Nether Spirit",
    "Increases your spell critical strike chance by 20% of your Spirit.",
    1, 2,
    effects={"crit_chance_spell_from_spirit_pct": 0.20},
    connect=["illidari_magi"],
    source="CoA: 'Increases your spell critical strike rating by 20% of "
           "your Spirit.' PORTS EXACTLY - crit_chance_spell is in "
           "STAT_CONVERSION_TARGETS and spirit is in SOURCES, a legal pair "
           "that four other trees in this project already use. Spirit is "
           "this spec's secondary stat (Hidden Power converts it to spell "
           "damage too), so the two nodes compound. A FRACTION. Was a pure "
           "scalar on our side."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "illidari_magi", "Illidari Magi",
    "Your damaging spells have a 25% chance to generate 10 Felfury.",
    2, 1,
    proc={"trigger": "on_damage_cast", "chance": 25, "icd": 0,
          "grant_resource": {"resource": "felfury", "amount": 10}},
    connect=["infernal_summoner"],
    source="CoA: 'Your periodic damage now has a 20% chance to generate 1 "
           "Felfury.' CoA FIRES THIS OFF DOT TICKS, which are not a "
           "trigger: status_effects.py:914 ticks a dot by calling the "
           "recipient's own take_damage with no caster reference, so there "
           "is nobody to fire a proc on. Re-pointed to on_damage_cast at "
           "25%. This is the same loss eight Chronomancer talents, three "
           "Necromancer and two Ranger ones take, and it is the single "
           "most-repeated unbuildable trigger in the CoA data."))

N.append(node(
    "cursed_flames", "Cursed Flames",
    "Your critical strikes increase your spell critical strike chance by "
    "20% for 3 turns.",
    2, -1,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "apply_effect": {"effect_id": "cursed_flames",
                           "name": "Cursed Flames",
                           "effect_type": "buff", "duration": 3,
                           "stat_mods": {"crit_chance_spell": 20.0},
                           "dispel_type": None, "on_target": False}},
    connect=["malice_of_guldan"],
    source="CoA: 'Critically striking with Fel Fireball now increases the "
           "critical strike chance of your next Fel Fireball within 10 "
           "seconds by 20%.' PORTS ALMOST VERBATIM - CoA's 20% kept - with "
           "only the two Fel-Fireball scopings widened: there is no "
           "per-ability proc trigger, and a status effect cannot carry a "
           "per-ability crit key, only the generic one. 10 sec -> 3 turns, "
           "and a 1-turn internal cooldown so it cannot chain off itself "
           "indefinitely. crit_chance_spell inside a status effect is "
           "PERCENTAGE POINTS, same as on the talent side."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "infernal_summoner", "Infernal Summoner",
    "Your damaging spells have a 10% chance to reset the cooldown of "
    "Infernal.",
    3, 1,
    proc={"trigger": "on_damage_cast", "chance": 10, "icd": 2,
          "reset_cooldown": ["felsworn_infernal"]},
    connect=["oppressive_ruin"],
    source="CoA: 'Direct damage dealt now has a 5% chance to reset the "
           "cooldown of Infernal.' PORTS VERBATIM in shape - "
           "reset_cooldown WITH A BARE LIST is a full reset, as against the "
           "{abilities, turns} form which only shaves turns. 5% -> 10% with "
           "a 2-turn internal cooldown, because Infernal is a 15-turn "
           "summon and chaining resets off a caster's rapid casts would "
           "flood the field. felsworn_infernal IS a real summon_pet "
           "ability, so this genuinely produces a pet. CoA's Infernal Ruin "
           "('every 3rd Ruin or Felwrath spawns an Infernal') cannot be "
           "built: there is no cast counter anywhere in the engine."))

N.append(node(
    "malice_of_guldan", "Malice of Gul'dan",
    "Your critical strikes have a 60% chance to burn the target for 3 "
    "turns and restore 5 Felfury.",
    3, -1,
    proc={"trigger": "on_crit", "chance": 60, "icd": 0,
          "grant_resource": {"resource": "felfury", "amount": 5},
          "apply_effect": {"effect_id": "felstrike_proc",
                           "name": "Felstrike",
                           "effect_type": "dot", "duration": 3,
                           "potency": 28, "damage_school": "shadow",
                           "max_stacks": 3, "dispel_type": "magic",
                           "on_target": True}},
    connect=["unphased"],
    source="CoA: 'Direct critical strikes now have a 60% chance to trigger "
           "a Felstrike and generate a Fragment of Malice. Felstrike: burn "
           "an enemy for Shadowflame Damage over 6 sec, stacking 3 times. "
           "Fragment of Malice: restores 5 Energy and increases your "
           "critical strike chance by 10% for 5 sec.' PORTS UNUSUALLY WELL: "
           "the 60% chance, the 3-stack dot and the resource restore all "
           "build, with CoA's Energy being our felfury. A single proc can "
           "carry both a grant_resource and an apply_effect, which is why "
           "this one node does both halves. The Fragment's crit buff is "
           "dropped - Cursed Flames already supplies that window and "
           "stacking a second would double-count. 6 sec -> 3 turns. The dot "
           "is authored shadow rather than the combined ['shadow','fire'] "
           "because a status effect's damage_school is a single string."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "oppressive_ruin", "Oppressive Ruin",
    "Your damaging spells have a 30% chance to reduce the target's healing "
    "received by 25% for 3 turns.",
    4, 1,
    proc={"trigger": "on_damage_cast", "chance": 30, "icd": 0,
          "apply_effect": {"effect_id": "oppressive_ruin",
                           "name": "Oppressive Ruin",
                           "effect_type": "debuff", "duration": 3,
                           "stat_mods": {"healing_taken_pct": -25},
                           "dispel_type": "magic", "on_target": True}},
    connect=["fel_infusion"],
    source="CoA: 'Damage dealt by Ruin now absorbs the next 99 healing on "
           "the target based on rank, up to 226 at rank 7, for 8 sec.' A "
           "HEALING ABSORB ON AN ENEMY HAS NO MECHANIC - absorbs are "
           "caster-side proc payloads (shield_pct, absorb_pct_max_health) "
           "and cannot be applied to a target - so this becomes a "
           "percentage healing reduction, which is the readable equivalent: "
           "healing_taken_pct is one of only eight status stat_mods a "
           "monster reads. The Ruin scoping goes (no per-ability proc "
           "trigger). 8 sec -> 3 turns. PERCENTAGE POINTS inside a status "
           "effect (character.py:2904 divides by 100), so -25 is -25% and "
           "-0.25 would have been -0.25%. Was a pure scalar on our side."))

N.append(node(
    "unphased", "Unphased",
    "Increases your spell penetration by 20 and your Shadow and Fire "
    "damage by a further 5%.",
    4, -1,
    effects={"spell_penetration": 20,
             "shadow_spell_damage": 0.05, "fire_spell_damage": 0.05},
    connect=["mannari_teachings"],
    source="CoA level 40 passive: 'Increases your spell penetration by 20, "
           "scaling with your level. In addition, reduces spell pushback "
           "suffered from damaging attacks by 50% while Inner Demon is "
           "active.' The penetration PORTS EXACTLY: spell_penetration is a "
           "FLAT rating fed into a real attribute (character.py:1382) and "
           "read attacker-side by both Character and Monster take_damage "
           "against magic_resistance, so it works today - and it is one of "
           "the talents that will pay for Kyle's shelved per-school "
           "resistance system. Spell pushback does not exist as a mechanic, "
           "and " + DEMON + " The level-scaling clause is dropped: talent "
           "effects do not scale with character level. Was a pure scalar on "
           "our side."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "fel_infusion", "Fel Infusion",
    "Increases your spell critical strike chance by 3% and reduces the "
    "cooldown of Fel Infusion by 35%.",
    5, 0,
    effects={"crit_chance_spell": 3.0,
             "ability_felsworn_fel_infusion_cooldown_pct": 0.35},
    connect=["mannari_teachings"],
    source="CoA: 'Increases critical strike chance of all party and raid "
           "members within 100 by 3%. Does not stack with similar effects. "
           "In addition, increases your critical strike chance by 3%.' THE "
           "PARTY HALF IS REAL BUT NOT FROM HERE: a talent effect can never "
           "reach an ally. The felsworn_fel_infusion ABILITY carries the "
           "party crit (crit_chance_physical and crit_chance_spell) and was "
           "converted from target_type 'self' to 'party' on 6 Nov 2026 - "
           "the same call Kyle made for Guardian's four auras on 5 Nov and "
           "that was applied to Reaper's two and Necromancer's three today. "
           "So this talent does what a talent can: CoA's own selfish 3% "
           "plus making that aura available more often. The does-not-stack "
           "clause has no mechanism short of every class's equivalent aura "
           "sharing an exclusive_group, which is a project-wide decision. "
           "Was a pure scalar on our side."))

N.append(node(
    "sargeras_embrace", "Sargeras Embrace",
    "Increases the damage of Sargeras Embrace by 45% and its duration by 2 "
    "turns.",
    5, 2,
    effects={"ability_felsworn_sargeras_embrace_damage": 0.45,
             "ability_felsworn_sargeras_embrace_duration": 2},
    connect=["mannari_teachings"],
    source="CoA: 'Channel a beam of fel magic upon an enemy, slowing their "
           "movement speed by 60% for 5.5 sec and dealing Shadowflame "
           "Damage at the end of the duration.' The ability already exists "
           "as a 2-turn shadow spell_dot. CoA's channel, its slow and its "
           "end-of-duration payload are all unbuildable - there is no "
           "channelling, movement speed is not a mechanic, and no trigger "
           "fires when an effect expires - so the node boosts the dot we "
           "have. +2 TURNS IS +2 FULL-VALUE TICKS, not a dilution: "
           "abilities.py:2777 derives per-turn damage from the ability's "
           "OWN base duration, so the dot doubles from 2 turns to 4 at "
           "unchanged per-tick damage. SMALL INTEGER IN TURNS, so "
           "talent_ranks.spread() refuses to rank this node."))

N.append(node(
    "guldans_prodigy", "Gul'dan's Prodigy",
    "Reduces the cost of Fel Fireball and Felwrath by 25% and increases "
    "Felwrath's damage by 25%.",
    1, -4,
    effects={"ability_felsworn_fel_fireball_damage": 0.25,
             "ability_felsworn_felwrath_cost_pct": 0.25,
             "ability_felsworn_felwrath_damage": 0.25},
    connect=["wrath_of_sargeras"],
    source="CoA: 'Reduces Energy cost and cast time of Fel Fireball by "
           "-15%.' The cost half ports - CoA's Energy is our felfury, the "
           "single primary pool - and the cast-time half is dropped, since "
           "there are no cast times. Extended to Felwrath, CoA's "
           "'Consumes 2 Felfury' AoE, whose own talents all key on Inner "
           "Demon and are therefore unbuildable. Fel Fireball generates 20 "
           "felfury, so cheapening it compounds. *_cost_pct keys are "
           "FRACTIONS where POSITIVE MEANS A REDUCTION. Was a pure scalar "
           "on our side."))

N.append(node(
    "fel_cannon", "Fel Cannon",
    "Increases the critical strike chance of Ruin and Felwrath by 15%.",
    2, -3,
    effects={"ability_felsworn_ruin_crit": 15.0,
             "ability_felsworn_felwrath_crit": 15.0},
    connect=["felfire_adept"],
    source="CoA: 'Increases the critical strike chance of Fel Fireball and "
           "Ruin by 15% on enemies above 75% health.' " + HIGH_HP + " So "
           "CoA's 15% is kept unconditional - a straight buff relative to "
           "CoA, flagged rather than pocketed quietly, because the "
           "alternative was a node that silently never fired. Pointed at "
           "Ruin and Felwrath rather than Fel Fireball, which Felfire Adept "
           "already covers. Per-ability crit keys are PERCENTAGE POINTS. "
           "Was a pure scalar on our side."))

N.append(node(
    "shadow_magi", "Shadow Magi",
    "Reduces the cooldown of Annihilation, Sunder and Ruin by 35%.",
    3, 3,
    effects={"ability_felsworn_annihilation_cooldown_pct": 0.35,
             "ability_felsworn_sunder_damage": 0.35,
             "ability_felsworn_ruin_cooldown_pct": 0.35},
    connect=["illidari_magi"],
    source="CoA: 'Reduces the cooldown of Annihilation by -15 sec and "
           "Sunder by -4 sec.' PORTS EXACTLY in shape, with Ruin added as "
           "the spec's main nuke. Annihilation is a 8-turn self-buff and "
           "Sunder is an AoE with no cooldown in our data, so the "
           "percentages land differently than CoA's flat seconds - the key "
           "is proportional and there is no flat-seconds form. FRACTIONS "
           "where POSITIVE MEANS A REDUCTION; talented_cooldown floors at 1 "
           "turn."))

N.append(node(
    "withering", "Withering",
    "Increases the damage of Fel Fireball by 30% and your spell damage by "
    "5%.",
    4, 3,
    effects={"ability_felsworn_fel_fireball_damage": 0.30,
             "spell_damage": 0.05},
    connect=["oppressive_ruin"],
    source="CoA: 'Your Fel Fireballs used with Felforged active now deal "
           "30% increased damage.' Felforged is a cast-time proc ('your "
           "next 3 Fel Fireballs have a -30% reduced cast time') and there "
           "are no cast times, so it does not exist here - which means "
           "nothing can gate off it either. CoA's 30% is therefore kept "
           "unconditional on Fel Fireball, with a small global added. Fel "
           "Fireball is the spec's filler and a 20-felfury generator, so "
           "three nodes in this tree point at it. Both FRACTIONS. Was a "
           "pure scalar on our side."))

N.append(node(
    "felshock", "Felshock",
    "Your critical strikes leave the target taking 8% more magic damage "
    "for 4 turns.",
    5, -2,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "felshock", "name": "Felshock",
                           "effect_type": "debuff", "duration": 4,
                           "stat_mods": {"magic_damage_taken_pct": 8},
                           "dispel_type": "magic", "on_target": True}},
    connect=["unphased"],
    source="CoA: 'Direct critical strikes with Felfury spenders now extend "
           "the duration of Inner Demon by 1 sec and cause enemies struck "
           "to have a 3% increased chance to be hit by spells for 12 sec.' "
           "TWO CLAUSES, BOTH REBUILT: no payload extends a LIVE effect's "
           "duration, and there is no recipient-side 'chance to be hit' key "
           "anywhere - the eight stat_mods a monster reads are armor, "
           "attack_power, damage_taken_pct, healing_taken_pct, "
           "magic/physical/spell_damage_taken_pct and magic_resistance. "
           "Repriced as magic damage taken, which is the same direction "
           "(more of this caster's damage lands) through a key that works, "
           "and raised to 8% since it replaces both clauses. 12 sec -> 4 "
           "turns. PERCENTAGE POINTS inside a status effect, and positive "
           "INCREASES damage taken, so 8 is right in both sign and "
           "magnitude - 0.08 would have been 0.08%."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "mannari_teachings", "Man'ari Teachings",
    "Increases your critical damage by 100% and your Shadow and Fire "
    "damage by a further 10%.",
    6, 0,
    effects={"crit_damage_pct": 1.00,
             "shadow_spell_damage": 0.10, "fire_spell_damage": 0.10},
    source="CoA level 50 passive: 'Increases your critical damage dealt by "
           "100%.' PORTS VERBATIM, which for a capstone of this size is "
           "worth noting - CoA really does double crit damage here. "
           "crit_damage_pct is read at abilities.py:1438 and is a FRACTION, "
           "so 1.00 is +100%; it stacks on top of CRIT_DAMAGE_MULTIPLIER "
           "rather than replacing it. Paired with the tree's school theme "
           "so the capstone pays off everything below it: with Wrath of "
           "Sargeras and Unphased that is +21% to every Shadowflame spell, "
           "and this spec crits six different ways to cash the crit damage "
           "in. All three keys are FRACTIONS. Was a pure scalar on our "
           "side."))


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
        f"CoA's 35%; the key SUMS across talents. Found {setters}")

    # THE PER-SCHOOL KEYS ARE THIS TREE'S SPINE and are built with
    # f-strings at abilities.py:1371, so a typo in the school name is
    # SILENT - no grep and no audit can see it.
    for n in TREE["nodes"]:
        for k in (n.get("effects") or {}):
            if k.endswith("_spell_damage") and "_from_" not in k:
                school = k[: -len("_spell_damage")]
                assert school in REAL_SCHOOLS, (
                    f"{n['talent_id']} authors {k}, but '{school}' is not a "
                    f"school Felsworn deals. These keys are built with an "
                    f"f-string, so a wrong school name does nothing at all "
                    f"and nothing would report it")

    # Fel Infusion's whole party value depends on the ABILITY staying
    # party-targeted. If it reverts, the cooldown talent still "works" and
    # the party crit silently vanishes.
    abilities = json.loads(
        (ROOT / "data/abilities/felsworn.json").read_text())["abilities"]
    aura = next((a for a in abilities
                 if a["ability_id"] == "felsworn_fel_infusion"), None)
    assert aura is not None and aura.get("target_type") == "party", (
        "felsworn_fel_infusion must stay target_type 'party' - this tree's "
        "Fel Infusion node exists to shorten its cooldown AS a party aura, "
        "because a talent effect can never reach an ally")

    for n in TREE["nodes"]:
        proc = n.get("proc") or {}
        gr = proc.get("grant_resource")
        if gr:
            assert gr.get("resource") == "felfury" and "amount" in gr, (
                f"{n['talent_id']} grant_resource must name felfury with a "
                f"FLAT amount")
        mods = (proc.get("apply_effect") or {}).get("stat_mods") or {}
        if "healing_taken_pct" in mods:
            assert abs(mods["healing_taken_pct"]) >= 1, (
                f"{n['talent_id']} healing_taken_pct="
                f"{mods['healing_taken_pct']} inside a status effect, where "
                f"it is PERCENTAGE POINTS")

    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Felsworn Infernal: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
