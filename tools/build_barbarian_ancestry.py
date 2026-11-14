#!/usr/bin/env python3
"""Rebuild Barbarian's Ancestry tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_barbarian_ancestry.py [--check]

SOURCE: data/reference/coa_worksheets/barbarian.md - 42 real Ancestry
talents, the largest Barbarian spec. Role: SUPPORT.
Ancestry was 23 nodes with only 3 PROCS - the thinnest tree in the entire
97-tree project, and the last one in the CoA rebuild.

THE PARTY AURAS ARE ALREADY ABILITIES, which solves this tree the way it
solved Ranger Farstrider. CoA writes nine Ancestry talents as party-wide
auras - Frozen Blades, Ancestral Wisdom, Ancestral Fury, Crystal
Enhancements, Uniting Voice, Splash Zone, Ramhorn Rage, War Cry, Cheers! -
and EIGHT such abilities already exist in data/abilities/barbarian.json as
target_type "party" (warband, ancestral_fury, frozen_blades, ramhorn_rage,
war_cry, splash_zone, tavern_brawl, clanlords_totem), plus cheers as an
ally-targeted buff. Barbarian was authored properly on the ability side.

A TALENT EFFECT CAN NEVER REACH AN ALLY - which is why Guardian's four
auras had to be converted on 5 Nov 2026, and Reaper's two, Necromancer's
three and Felsworn's three today - so the talents do what talents can:
shorten those auras' cooldowns, lengthen their durations, and make the
Honored Ancestor hit harder. That is what CoA's own Uniting Voice, Time To
Kill! and No Survivors exist to do.

BARBARIAN SUMMONS, so pet keys are legal: barbarian_ancestors_call is a
real summon_pet ability with a template. But pets never fire procs (no
fire_proc_trigger anywhere in entities/pet.py), nothing reads a live pet
count, and no proc reaches a pet - so The Spins, Drunken Frenzy and Ale of
The God-King's empowerment all become flat pet scaling.

FROST IS REAL HERE. hodirs_wrath, breath_of_the_north and frozen_tankard
all carry damage_school "frost", and frost_spell_damage is live - built via
an f-string at abilities.py:1371 and resolved against the ability's real
school, which is why a literal grep finds nothing. main() pins every
school name used to one Barbarian actually deals, because a typo would be
silent.

THE TANKARD AND ITS FILL LEVEL STACKS DO NOT EXIST. Barbarian is
(ResourceType.ENERGY, None) - no secondary pool - and nothing reads a stack
count anyway, so CoA's whole drinking economy (Drinking Frenzy, Liquid
Courage, Ice Cold Bubbles, Cold Brew, Improved Ancestral Combat, The Finest
Ale, and the "empties your Tankard" clauses on Ramhorn Rage, Ale of The
God-King and Breath of The North) has nothing to stand on. Seven talents.

NOT BUILDABLE beyond the above: Thane's Grip and Thane's Guard gate on
weapon and shield types, which nothing reads; Ancestral Combat's
"lasts until triggered 20 times" needs a use counter; Blind Stupor reduces
casting speed, for which there is no key; Icebound Ancestry and Hodir's
Revenge gate on Frozen targets, which needs a target's debuffs; Cheers!'s
damage redirection has no mechanism.

Brutality owns low_health_threshold_pct for the class at 0.35.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/barbarian_ancestry.json"

#: The party-targeted abilities this tree modifies rather than duplicates.
#: Asserted in main() - if one reverts to "self", the cooldown and duration
#: talents still "work" while the party support silently vanishes.
PARTY_ABILITIES = ["barbarian_warband", "barbarian_ancestral_fury",
                   "barbarian_frozen_blades", "barbarian_ramhorn_rage",
                   "barbarian_war_cry", "barbarian_splash_zone",
                   "barbarian_tavern_brawl", "barbarian_clanlords_totem"]

#: Schools Barbarian actually deals. Asserted against per-school keys.
REAL_SCHOOLS = {"frost", "physical"}

TREE = {
    "spec_name": "Barbarian Ancestry",
    "tree_id": "barbarian_ancestry",
    "description": ("Ale, ancestors and frost - a barbarian who makes the "
                    "whole warband hit harder."),
    "_source_note": (
        "Rebuilt 6 Nov 2026 from the 42 real CoA Ancestry talents (role "
        "SUPPORT), the largest Barbarian spec and the thinnest tree in the "
        "project at 3 procs. CoA writes nine of its talents as party auras "
        "and eight such abilities ALREADY exist as target_type 'party' - "
        "Barbarian was authored properly on the ability side, like Ranger - "
        "so the talents modify those auras instead of trying to be them. "
        "Barbarian summons, so pet keys are legal, but pets never fire "
        "procs. The Tankard's Fill Level stacks do not exist, which costs "
        "seven talents. Last tree of the CoA rebuild."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20,
                          "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"barbarian_ancestry_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"barbarian_ancestry_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


TANKARD = ("CoA scales this off FILL LEVEL, the Tankard's stack mechanic. "
           "Barbarian is (ResourceType.ENERGY, None) with no secondary "
           "pool, and nothing reads a stack count anyway, so there is "
           "nothing to count. Seven Ancestry talents depend on it; each is "
           "flattened to its unconditional form. Same situation as "
           "Chronomancer's Echo Fragments and Venomancer's Brood Marks - "
           "and the reason CHECK THE RESOURCE FIRST is a standing rule, "
           "since Templar's Combo, Reaper's Souls and Ranger's Focus all "
           "turned out to be real.")

PETS = ("Barbarian genuinely summons - barbarian_ancestors_call is a real "
        "summon_pet ability - so pet_damage/pet_health/pet_armor are legal "
        "keys here, which tools/qa_pet_keys.py exists to police after Witch "
        "Doctor Shadow Hunting shipped three on a class that summons "
        "nothing. But PETS NEVER FIRE PROCS (no fire_proc_trigger anywhere "
        "in entities/pet.py), nothing reads a live pet count, and no proc "
        "can apply an effect to a pet, so the Honored Ancestor's own "
        "behaviour cannot be changed - only its scaling.")

N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "trip_to_the_alehouse", "Trip to the Alehouse",
    "Increases the damage of Keg Smash by 20% and your area damage by 15%.",
    0, -4,
    effects={"ability_barbarian_keg_smash_damage": 0.20,
             "aoe_damage": 0.15},
    connect=["drinking_frenzy"],
    source="CoA over 2 ranks: 'Increases the damage of Keg Smash by 10% and "
           "its range by 3 yds.' The damage ports (doubled); range is not a "
           "mechanic here. Replaced with aoe_damage, which IS live and is "
           "read at abilities.py:1600 only when target_type is enemy_aoe - "
           "so it is genuinely scoped to area attacks, and Keg Smash is one "
           "of five this spec has. Both FRACTIONS. Was a pure scalar on our "
           "side."))

N.append(node(
    "drinking_frenzy", "Drinking Frenzy",
    "Increases your hit chance by 5% and your pets' damage by 20%.",
    0, -2,
    effects={"hit_rating": 5.0, "pet_damage": 0.20},
    connect=["uniting_voice", "frost_giants_fury"],
    source="CoA: 'Your melee attacks now have a 15% chance to grant a stack "
           "of Fill Level. In addition, your chance to hit is increased by "
           "5%.' The hit chance ports verbatim. " + TANKARD + " Replaced "
           "with pet damage, which is the tree's other theme. hit_rating is "
           "live as a FLAT bonus in PERCENTAGE POINTS - it is only invalid "
           "as a CONVERSION target, which with stamina has cost ten nodes "
           "half their text across eight classes. pet_damage is a FRACTION. "
           "Was a pure scalar on our side."))

N.append(node(
    "uniting_voice", "Uniting Voice",
    "Reduces the cooldown of Ancestral Roar and Warband by 35% and "
    "increases Ancestral Roar's healing by 25%.",
    0, 0,
    effects={"ability_barbarian_ancestral_roar_cooldown_pct": 0.35,
             "ability_barbarian_warband_cooldown_pct": 0.35,
             "ability_barbarian_ancestral_roar_healing": 0.25},
    connect=["ancestral_wisdom"],
    source="CoA: 'Casting Ancestral Roar now increases haste of party and "
           "raid members by 5% for 20 sec. Does not stack with similar "
           "effects. Critical strikes extend the duration of the buff by 1 "
           "sec.' THE PARTY HASTE IS REAL BUT NOT FROM A TALENT - a talent "
           "effect can never reach an ally. barbarian_ancestral_fury and "
           "barbarian_warband already carry party haste and healing as "
           "target_type 'party' ABILITIES (abilities.py:2064 resolves "
           "'party' to all living allies), so this talent does what a "
           "talent can: make them available more often. The "
           "extend-on-crit clause cannot be built either - no payload "
           "extends a LIVE effect's duration. Ancestral Roar is "
           "effect_type heal, so its buff takes ability_<id>_HEALING; "
           "_damage on a heal does nothing while passing every check. Was "
           "a pure scalar on our side."))

N.append(node(
    "frost_giants_fury", "Frost Giant's Fury",
    "Increases your Frost damage by 12% and your haste by 10%.",
    0, 2,
    effects={"frost_spell_damage": 0.12, "haste": 10.0},
    connect=["icebound_ancestry"],
    source="CoA: 'Casting Breath of the North now grants you 10% melee "
           "attack speed, plus an additional 20% when using a two-handed "
           "weapon, for 8 sec.' The haste ports as a passive: there is no "
           "per-ability proc trigger, and the two-handed clause cannot be "
           "built because nothing reads weapon type (which also cost "
           "Thane's Grip, Thane's Guard and eleven Felsworn Slayer talents "
           "their conditions). Folded in CoA's Ancestor's Fury ('Unbridled "
           "Rage now also increases your Frost damage by 10%'), whose "
           "trigger fails the same way. frost_spell_damage IS LIVE - built "
           "via an f-string at abilities.py:1371 inside "
           "_school_damage_bonus and resolved against the ability's real "
           "school, so a literal grep cannot see it; this spec has three "
           "frost abilities (Hodir's Wrath, Breath of the North, Frozen "
           "Tankard). A FRACTION; haste is PERCENTAGE POINTS. Was a pure "
           "scalar on our side."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "ancestral_wisdom", "Ancestral Wisdom",
    "Reduces the cooldown of your party auras by 35%.",
    1, 0,
    effects={"ability_barbarian_ancestral_fury_potency": 0.35,
             "ability_barbarian_frozen_blades_potency": 0.35,
             "ability_barbarian_splash_zone_cooldown_pct": 0.35,
             "ability_barbarian_clanlords_totem_cooldown_pct": 0.35},
    connect=["cold_brew", "the_spins"],
    source="CoA: 'Increases chance to hit with all spells and attacks by 1% "
           "for you and party and raid members. Does not stack with similar "
           "effects.' A TALENT EFFECT CAN NEVER REACH AN ALLY, and unlike "
           "Guardian, Reaper, Necromancer and Felsworn there was nothing to "
           "convert here - all eight of Barbarian's aura abilities were "
           "ALREADY target_type 'party'. So rather than build a selfish "
           "shadow of CoA's aura, this node makes four of those real auras "
           "available far more often, which is a thing only a talent can "
           "do. That is the same solution Ranger Farstrider's Blow the "
           "Horns! uses, and it makes the tree MORE faithful than forcing "
           "aura effects into talent slots would. FRACTIONS where POSITIVE "
           "MEANS A REDUCTION; talented_cooldown floors at 1 turn."))

N.append(node(
    "icebound_ancestry", "Icebound Ancestry",
    "Increases the critical strike chance of your Frost abilities by 15%.",
    1, 2,
    effects={"ability_barbarian_breath_of_the_north_crit": 15.0,
             "ability_barbarian_hodirs_wrath_crit": 15.0,
             "ability_barbarian_frozen_tankard_crit": 15.0},
    connect=["the_spins"],
    source="CoA: 'Increases the critical strike chance of Breath of the "
           "North by 10%. In addition, your attacks now ignore Armor "
           "against Frozen targets.' The crit ports (raised to 15%) and is "
           "extended to the spec's other two frost abilities. The armour "
           "clause fails twice: nothing reads a target's debuffs, so "
           "'against Frozen targets' is unreachable, and armor_penetration "
           "is FLAT rather than proportional so 'ignore Armor' has no "
           "all-or-nothing form. CoA's Hodir's Revenge gates on Frozen the "
           "same way. Per-ability crit keys are PERCENTAGE POINTS. Was a "
           "pure scalar on our side."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "cold_brew", "Cold Brew",
    "Your critical strikes restore 12 Energy.",
    2, -1,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "energy", "amount": 12}},
    connect=["liquid_courage"],
    source="CoA: 'Critical strikes with Frost damage now generate a stack "
           "of Fill Level. Can only occur once per sec.' " + TANKARD + " "
           "Re-pointed to the pool that DOES exist - Energy, Barbarian's "
           "single primary resource - so the node keeps its shape (crit, "
           "get resource) through a mechanic that works. The Frost scoping "
           "goes: there is no per-school proc filter, since proc['school'] "
           "only TYPES a damage_flat payload. grant_resource routes through "
           "the same gain_resource() the class's three generators use, so "
           "the cap holds, and its `amount` is FLAT."))

N.append(node(
    "the_spins", "The Spins",
    "Increases your pets' damage by a further 30% and their health by 25%.",
    2, 1,
    effects={"pet_damage": 0.30, "pet_health": 0.25},
    connect=["blind_stupor"],
    source="CoA: 'Casting Keg Smash now causes your Honored Ancestor to "
           "perform an Ancestral Whirl attack upon nearby enemies.' "
           + PETS + " So an ancestor that mimics your abilities cannot be "
           "built, and the node becomes flat pet scaling - the same intent "
           "(your ancestor matters more) through the only keys that reach "
           "it. Folded in CoA's Drunken Frenzy ('Unbridled Rage now "
           "increases your Honored Ancestor's Physical damage by 15%') and "
           "Ale of The God-King's empowerment, both of which fail the same "
           "way. Both FRACTIONS. Was a pure scalar on our side."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "liquid_courage", "Liquid Courage",
    "Reduces all damage you take by 6% and increases your maximum health "
    "by 8%.",
    3, -1,
    effects={"damage_taken_pct": -0.06, "max_health_pct": 0.08},
    connect=["frostbite"],
    source="CoA: 'Each Fill Level stack now reduces your damage taken by "
           "-2%.' " + TANKARD + " Built as the flat mitigation CoA's "
           "typical three stacks would give, plus health so the node is "
           "worth a point on a support spec. BOTH KEYS ARE FRACTIONS AS "
           "TALENT EFFECTS: damage_taken_pct is read RAW "
           "(character.py:2696), so -0.06 is -6%, and max_health_pct is a "
           "fraction here but PERCENTAGE POINTS inside a status effect - "
           "the same key, two conventions, depending on where it is "
           "written. Was a pure scalar on our side."))

N.append(node(
    "blind_stupor", "Blind Stupor",
    "Your attacks have a 35% chance to daze the target, weakening their "
    "attacks for 4 turns.",
    3, 1,
    proc={"trigger": "on_weapon_swing", "chance": 35, "icd": 0,
          "apply_effect": {"effect_id": "blind_stupor",
                           "name": "Blind Stupor",
                           "effect_type": "debuff", "duration": 4,
                           "stat_mods": {"attack_power": -100},
                           "dispel_type": None, "on_target": True}},
    connect=["frostbite"],
    source="CoA: 'Damage dealt by Keg Smash now reduces enemies' casting "
           "speed by 30% for 15 sec.' THERE IS NO CASTER-SIDE SPEED DEBUFF "
           "KEY - that gap has now cost nodes on five classes, including "
           "Chronomancer's Destabilize Time, whose entire mechanic it was - "
           "so this becomes a flat attack power reduction, which weakens "
           "the target's output the way a slower cast would. attack_power "
           "is one of only eight status stat_mods a monster reads and it is "
           "FLAT (Monster.ability_power_bonus: 'Flat damage/healing swing "
           "from active buffs and debuffs'). The Keg Smash scoping goes (no "
           "per-ability proc trigger). 15 sec -> 4 turns."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "frostbite", "Frostbite",
    "Your Frost damage has a 35% chance to freeze the target, dealing "
    "damage over 3 turns.",
    4, 0,
    proc={"trigger": "on_damage_cast", "chance": 35, "icd": 0,
          "apply_effect": {"effect_id": "frostbite", "name": "Frostbite",
                           "effect_type": "dot", "duration": 3,
                           "potency": 26, "damage_school": "frost",
                           "dispel_type": "magic", "on_target": True}},
    connect=["ramhorn_rage", "unified_rage"],
    source="CoA: 'Breath of The North now causes the target to bleed for an "
           "additional 30% of its damage over 6 sec as Frost damage.' The "
           "dot ports; the Breath-of-the-North scoping does not (no "
           "per-ability proc trigger), and '30% of its damage' becomes a "
           "fixed potency because apply_effect cannot read the triggering "
           "hit's amount - only bonus_pct, leech_pct and smart heals do, "
           "and none of them apply an effect. The description says 'your "
           "Frost damage' loosely: proc['school'] is NOT a trigger-side "
           "filter, it only types a damage_flat payload, so this fires on "
           "any damaging cast. 6 sec -> 3 turns. A proc-applied dot carries "
           "`potency` as PER-TURN damage (26 a turn, 78 total)."))

N.append(node(
    "unified_rage", "Unified Rage",
    "Reduces the cooldown of Unbridled Rage and Ancestral Combat by 35% "
    "and increases your physical damage by 6%.",
    4, 2,
    effects={"ability_barbarian_unbridled_rage_cooldown_pct": 0.35,
             "ability_barbarian_ancestral_combat_potency": 0.35,
             "physical_damage": 0.06},
    connect=["war_cry"],
    source="CoA: 'Your Unbridled Rage now increases your chance to trigger "
           "Ancestral Combat by 25%.' Ancestral Combat is a self-buff in "
           "our data rather than a proc, so there is no trigger chance to "
           "raise - and nothing reads whether Unbridled Rage is active "
           "anyway. Rebuilt as cooldown reductions on both named abilities "
           "plus a small global. Folded in CoA's Improved Ancestral Combat "
           "('reduces the Energy cost by -10 and allows it to trigger 3 "
           "additional times'), whose second clause needs a use counter: "
           "nothing counts how many times an effect has fired. FRACTIONS "
           "where POSITIVE MEANS A REDUCTION, beside a fraction that adds - "
           "the two sign conventions sit in one dict. Was a pure scalar on "
           "our side."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "ramhorn_rage", "Ramhorn Rage",
    "Reduces the cooldown of Ramhorn Rage and Warband by 40% and increases "
    "their healing by 25%.",
    5, -1,
    effects={"ability_barbarian_ramhorn_rage_cooldown_pct": 0.40,
             "ability_barbarian_warband_cooldown_pct": 0.40,
             "ability_barbarian_ramhorn_rage_healing": 0.25,
             "ability_barbarian_warband_healing": 0.25},
    connect=["ancestral_spirit"],
    source="CoA: 'Enrage party and raid members within 8 yds for 3 sec, "
           "regenerating 2% of their maximum health every 1.5 sec. Melee "
           "auto attacks extend the duration of this effect by 2 sec, up to "
           "a maximum of 15 sec. This ability empties your Tankard.' Both "
           "abilities already exist as target_type 'party' HOTs, so THE "
           "PARTY HEALING IS REAL - it just cannot come from a talent. The "
           "extend-on-auto-attack clause cannot be built (no payload "
           "extends a LIVE effect's duration) and " + TANKARD + " So this "
           "talent makes two real party heal-over-times stronger and far "
           "more frequent. BOTH TAKE ability_<id>_HEALING, not _damage: "
           "they are HOTs, and _damage on a heal passes every check while "
           "doing nothing."))

N.append(node(
    "war_cry", "War Cry",
    "Reduces the cooldown of War Cry and Tavern Brawl by 40% and increases "
    "your attack power by 8%.",
    5, 1,
    effects={"ability_barbarian_war_cry_cooldown_pct": 0.40,
             "ability_barbarian_tavern_brawl_cooldown_pct": 0.40,
             "attack_power_pct": 8.0},
    connect=["ancestral_spirit"],
    source="CoA: 'Unleash a blood curdling war cry, increasing melee and "
           "ranged attack speed by 20%, and attack power by 150 of party "
           "and raid members within 25 yds for 20 sec. Allies cannot "
           "benefit from this spell again for 5 min.' Both abilities exist "
           "as target_type 'party' buffs, so the party effect is real and "
           "this talent shortens their cooldowns. The 5-minute exhaustion "
           "lockout has no mechanism - nothing prevents a buff being "
           "reapplied to the same target - which also cost Ranger's Frenzy "
           "and Command Aura their drawbacks, so this is a case where "
           "losing CoA's restriction is a straight gain and is flagged "
           "rather than pocketed quietly. attack_power_pct is PERCENTAGE "
           "POINTS, which audit_talents caught me authoring as a fraction "
           "on Ranger Brigand tonight."))

N.append(node(
    "crystal_enhancements", "Crystal Enhancements",
    "Increases your armor by 18% and reduces the cooldown of Clanlord's "
    "Totem and Frozen Blades by 30%.",
    5, 3,
    effects={"armor_pct": 18.0,
             "ability_barbarian_clanlords_totem_cooldown_pct": 0.30,
             "ability_barbarian_frozen_blades_potency": 0.30},
    connect=["ancestral_spirit"],
    source="CoA: 'You now emanate an aura around you, increasing the Armor "
           "of party and raid members by 390. Does not stack with similar "
           "effects.' A talent effect can never reach an ally, and there is "
           "no Barbarian 'Crystal Enhancements' ABILITY to convert - but "
           "clanlords_totem and frozen_blades ARE party abilities, so the "
           "node takes CoA's armour selfishly and makes those two "
           "available more often. KEPT UNDER THE CAP DELIBERATELY: "
           "check_talent_balance enforces an armor_pct ceiling of 60 and "
           "Venomancer Fortitude currently breaches it at 62 from two "
           "stacking nodes, so this tree carries exactly one armour node. "
           "armor_pct is PERCENTAGE POINTS. Was a pure scalar on our "
           "side."))

N.append(node(
    "ice_cold_bubbles", "Ice Cold Bubbles",
    "Increases your Frost damage by a further 10% and the damage of Frozen "
    "Tankard by 30%.",
    1, -4,
    effects={"frost_spell_damage": 0.10,
             "ability_barbarian_frozen_tankard_damage": 0.30},
    connect=["trip_to_the_alehouse"],
    source="CoA over 2 ranks: 'Each Fill Level stack now also increases "
           "Frost damage dealt by 2%.' " + TANKARD + " Built as the flat "
           "value CoA's typical five stacks would give, plus damage on "
           "Frozen Tankard, which no other node touches. Stacks with Frost "
           "Giant's Fury and the Frost theme generally. frost_spell_damage "
           "is live via an f-string lookup; both keys are FRACTIONS."))

N.append(node(
    "cheers", "Cheers!",
    "Your healing spells have a 30% chance to mend your most wounded ally.",
    2, -3,
    proc={"trigger": "on_heal_cast", "chance": 30, "icd": 1,
          "smart_heal_pct": 30},
    connect=["drinking_frenzy"],
    source="CoA: 'Designate an ally as your drinking partner for 30 min, "
           "reducing all damage they take by 5%, and causing 10% of all "
           "damage they take to be redirected to you.' THE REDIRECTION HAS "
           "NO MECHANISM - nothing reroutes damage from one combatant to "
           "another, which is the same gap that killed Chronomancer's The "
           "Vast Infinite and Reaper's Spectral Warden threat transfer - "
           "and a talent cannot put a damage-reduction buff on a chosen "
           "ally either. The barbarian_cheers ABILITY exists as an "
           "ally-targeted buff and carries that half. So the talent does "
           "the thing a talent CAN do for allies: smart_heal_pct, one of "
           "only three payloads that reach an ally at all, which picks the "
           "worst-off one. NOTE on_heal_cast passes the CASTER, never the "
           "healed ally, and a HoT fires no on_heal_cast at all - so this "
           "keys off the spec's direct heals (Ancestral Roar, Savage "
           "Revelry), not Warband or Ramhorn Rage."))

N.append(node(
    "ancestral_combat", "Ancestral Combat",
    "Your attacks have a 25% chance to strike an additional time.",
    3, 3,
    proc={"trigger": "on_weapon_swing", "chance": 25, "icd": 0,
          "extra_attack": True},
    connect=["icebound_ancestry"],
    source="CoA: 'Empower yourself, granting your Physical damage dealt a "
           "25% chance to trigger an additional main hand attack as Frost "
           "damage on your target and grant a stack of Fill Level. Lasts "
           "until triggered 20 times.' THE CORE PORTS VERBATIM, chance "
           "included: `extra_attack` is a BOOLEAN giving exactly one extra "
           "attack, which is precisely what CoA asks for. Three things do "
           "not - 'lasts until triggered 20 times' needs a use counter, the "
           "Fill Level stack does not exist, and the extra attack cannot be "
           "retyped as Frost (extra_attack carries no school, unlike "
           "damage_flat). Built as a passive rather than the 30-second "
           "self-buff, since a talent cannot grant a proc-carrying window "
           "without a nested proc the audit cannot inspect."))

N.append(node(
    "the_finest_ale", "The Finest Ale",
    "Increases the healing of Savage Revelry by 35% and reduces its "
    "cooldown by 30%.",
    4, -2,
    effects={"ability_barbarian_savage_revelry_healing": 0.35,
             "ability_barbarian_savage_revelry_cooldown_pct": 0.30},
    connect=["liquid_courage"],
    source="CoA: 'Your Ale of The God-King no longer empties your "
           "Tankard.' " + TANKARD + " With no Tankard to empty, the talent "
           "has literally nothing to act on, so it is re-pointed to Savage "
           "Revelry - the spec's self-heal, which also generates 20 Energy "
           "and had no node. It is effect_type heal, so it takes "
           "ability_<id>_HEALING: _damage on a heal passes every check "
           "while doing nothing, which is how 18 talents across four "
           "classes were silently dead before _healing was accepted. The "
           "cooldown key is a FRACTION where POSITIVE MEANS A REDUCTION."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "ancestral_spirit", "Ancestral Spirit",
    "Reduces the cost of all your abilities by 20%, increases your pets' "
    "damage by a further 35%, and your critical strikes restore 15 Energy.",
    6, 0,
    effects={"all_ability_cost_pct": 0.20, "pet_damage": 0.35},
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "energy", "amount": 15}},
    source="CoA over 2 ranks: 'Reduces the Energy cost of your Spirit "
           "spells and increases the duration of your Shouts by -50%.' "
           "'Spirit spells' and 'Shouts' are CoA ability CATEGORIES and the "
           "engine has no such concept - there is no ability-group key, "
           "which is the same wall 'Spears' hit in Headhunting and 'Command "
           "spells' hit across Necromancer - so the cost reduction becomes "
           "global, which is what it amounts to on a spec whose whole kit "
           "is Spirit spells. The capstone then pays off the tree's two "
           "other themes: pet damage stacking with Drinking Frenzy and The "
           "Spins to +85%, and a second Energy grant stacking with Cold "
           "Brew to 27 per crit. LAST NODE OF THE CoA REBUILD - all 21 "
           "classes, 63 trees. all_ability_cost_pct is a FRACTION where "
           "POSITIVE MEANS A REDUCTION; pet_damage is a fraction that "
           "adds."))


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
        f"Barbarian Brutality's Overkill owns low_health_threshold_pct for "
        f"this class at 0.35; the key SUMS across talents. Found {setters}")

    abilities = json.loads(
        (ROOT / "data/abilities/barbarian.json").read_text(encoding="utf-8"))["abilities"]
    by_id = {a["ability_id"]: a for a in abilities}

    # MOST OF THIS TREE MODIFIES PARTY ABILITIES rather than trying to be a
    # party aura, which a talent effect cannot do. If one of them quietly
    # reverts to target_type "self", every cooldown talent here still
    # "works" and the party support silently vanishes - nothing else in the
    # project would report it.
    for aid in PARTY_ABILITIES:
        a = by_id.get(aid)
        assert a is not None, f"{aid} is gone from the ability data"
        assert a.get("target_type") == "party", (
            f"{aid} is target_type {a.get('target_type')!r}, not 'party' - "
            f"this tree's cooldown and healing talents exist to modify it "
            f"AS a party aura, because a talent effect can never reach an "
            f"ally. Guardian's four, Reaper's two, Necromancer's three and "
            f"Felsworn's three all had to be converted; Barbarian's eight "
            f"were already correct.")

    # pet keys are silent dead data on a class that does not summon.
    pet_nodes = [n["talent_id"] for n in TREE["nodes"]
                 if any(k.startswith("pet_") for k in (n.get("effects") or {}))]
    if pet_nodes:
        assert any(a.get("effect_type") == "summon_pet" for a in abilities), (
            f"{pet_nodes} author pet keys but Barbarian summons nothing")
    for n in TREE["nodes"]:
        assert "pet_haste" not in (n.get("effects") or {}), (
            f"{n['talent_id']} authors pet_haste, read by no engine code")

    # Per-school keys are built with f-strings, so a wrong school is silent.
    for n in TREE["nodes"]:
        for k in (n.get("effects") or {}):
            if k.endswith("_spell_damage") and "_from_" not in k:
                school = k[: -len("_spell_damage")]
                assert school in REAL_SCHOOLS, (
                    f"{n['talent_id']} authors {k}, but '{school}' is not a "
                    f"school Barbarian deals - these keys are built with an "
                    f"f-string at abilities.py:1371, so a wrong name does "
                    f"nothing and nothing would report it")

    # Every ability-scoped key must name a real ability: the lookup is
    # ability_<exact id>_<field>, so a typo is silent dead data.
    FIELDS = ("_damage", "_healing", "_crit", "_crit_damage", "_cost_pct",
              "_cooldown_pct", "_duration", "_potency")
    for n in TREE["nodes"]:
        for k in (n.get("effects") or {}):
            if not k.startswith("ability_"):
                continue
            for f in FIELDS:
                if k.endswith(f):
                    aid = k[len("ability_"):-len(f)]
                    assert aid in by_id, (
                        f"{n['talent_id']} authors {k}, but '{aid}' is not "
                        f"a Barbarian ability - silent dead data")
                    break
        gr = (n.get("proc") or {}).get("grant_resource")
        if gr:
            assert gr.get("resource") == "energy" and "amount" in gr, (
                f"{n['talent_id']} grant_resource must name energy with a "
                f"FLAT amount")

    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Barbarian Ancestry: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points, {len(PARTY_ABILITIES)} party auras modified")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
