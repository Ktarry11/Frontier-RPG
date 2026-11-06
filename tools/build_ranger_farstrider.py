#!/usr/bin/env python3
"""Rebuild Ranger's Farstrider tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_ranger_farstrider.py [--check]

SOURCE: data/reference/coa_worksheets/ranger.md - 44 real Farstrider
talents, the largest spec in the CoA data. Role: SUPPORT.
Farstrider was 23 nodes with 4 procs - the thinnest Ranger tree.

THE PARTY AURAS ARE ALREADY ABILITIES, AND THAT SOLVES THIS TREE.

CoA writes seven Farstrider talents as party-wide auras: Horn of War,
Horn of Alacrity, Battle Screech, Battle Prowess, Defense of the Ancients,
Frenzy, Freedom and Command Aura. A TALENT EFFECT CAN NEVER REACH AN ALLY
- which is why Guardian's four auras had to be converted on 5 Nov 2026 and
why Reaper's two were converted today - but all eight of these ALREADY
EXIST in data/abilities/ranger.json as target_type "party" abilities with
correct buff_scope values. Ranger was authored properly on the ability
side.

So the talents do what talents can actually do: shorten those abilities'
cooldowns, lengthen their durations, and make the summons they rely on
hit harder. That is CoA's own Blow the Horns!, Scavenger, Falcon Charmer,
War Falconer and Survivalist, which exist precisely to modify the auras
rather than to be them. The tree ends up MORE faithful than it would have
been by forcing aura effects into talent slots.

RANGER SUMMONS, so pet keys are legal: ranger_summon_war_falcon is a real
summon_pet ability. BUT PETS NEVER FIRE PROCS (no fire_proc_trigger
anywhere in entities/pet.py), nothing reads a live pet count, and no proc
can apply an effect to a pet. That kills nine Farstrider talents outright
- Gutpiercer, Pecking, Coordination, Falcon's Aid, Wingman, Guidance,
Dragonhawk Tamer, Falcon Diving and Aerial Assault all read either pet
damage or how many pets are out. Pets scale off pet_damage, pet_health and
pet_armor and nothing else.

NOT BUILDABLE beyond the above: the Dreamflower system (Forest Herald,
Highlander, Petalkeeper and the shared Dream Flowers passive) needs ground
objects allies walk over; Falcon's Call, Emerald Arrow's flare, Whipvine
Arrow's extra targets and Backstep are all positioning; Thread The Needle
and Phoenix Plumes read Advantage stacks, which nothing counts; Hunting
Tactics reads whether a target is poisoned; Razorquills changes "tick
rate", meaningless at one tick per turn; Windrunner's Reach needs creature
types; Falconstrike and Petalkeeper have broken CoA payloads ("$36",
"$34"), so there is nothing to port.

Archery owns low_health_threshold_pct for the class; nothing here sets it.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/ranger_farstrider.json"

#: The party-targeted abilities this tree modifies rather than duplicates.
#: Asserted in main() - if one of these stops being target_type "party",
#: half this tree's reason for existing is gone and nothing else would say
#: so.
PARTY_ABILITIES = ["ranger_horn_of_war", "ranger_horn_of_alacrity",
                   "ranger_battle_screech", "ranger_battle_prowess",
                   "ranger_defense_of_the_ancients", "ranger_frenzy",
                   "ranger_freedom", "ranger_command_aura"]

TREE = {
    "spec_name": "Ranger Farstrider",
    "tree_id": "ranger_farstrider",
    "description": ("Horns, falcons and poisoned arrows - a ranger who "
                    "makes the whole party hit harder."),
    "_source_note": (
        "Rebuilt 6 Nov 2026 from the 44 real CoA Farstrider talents (role "
        "SUPPORT), the largest spec in the CoA data. CoA writes seven of "
        "them as party auras, and all eight such abilities ALREADY exist "
        "as target_type 'party' in our ability data - so unlike Guardian "
        "and Reaper, nothing needed converting, and the talents modify "
        "those auras (cooldown, duration) exactly as CoA's own Blow the "
        "Horns!, Scavenger and Falcon Charmer do. Ranger summons, so pet "
        "keys are legal, but pets never fire procs and nothing reads a pet "
        "count, which kills nine talents."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20,
                          "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"ranger_farstrider_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"ranger_farstrider_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


PETS = ("Reaper and Ranger both genuinely summon, so pet_damage/pet_health/"
        "pet_armor are legal keys here - but PETS NEVER FIRE PROCS (no "
        "fire_proc_trigger anywhere in entities/pet.py), nothing reads a "
        "live pet count, and no proc can apply an effect to a pet. Nine "
        "Farstrider talents depend on one of those three and are dropped.")

N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "cunning", "Cunning",
    "Reduces the cost of all your abilities by 12%.",
    0, -4,
    effects={"all_ability_cost_pct": 0.12},
    connect=["blow_the_horns"],
    source="CoA over 2 ranks: 'Increases your Focus regeneration by 15%.' "
           "FOCUS REGENERATION HAS NO KEY - energy_regen, energy_regen_pct "
           "and resource_regen_pct are all authored by talents elsewhere in "
           "this project and read by nothing. Repriced as a cost reduction, "
           "which reaches the same place through a key that works. CoA's "
           "Focus is our archery_points, Ranger's primary pool. "
           "all_ability_cost_pct is a FRACTION where POSITIVE MEANS A "
           "REDUCTION. Was a pure scalar on our side."))

N.append(node(
    "blow_the_horns", "Blow the Horns!",
    "Reduces the cooldown of your Horn and Screech auras by 35%.",
    0, -2,
    effects={"ability_ranger_horn_of_war_cooldown_pct": 0.35,
             "ability_ranger_horn_of_alacrity_cooldown_pct": 0.35,
             "ability_ranger_battle_screech_cooldown_pct": 0.35},
    connect=["scavenger", "falcon_charmer"],
    source="CoA over 2 ranks: 'Reduces the cooldown of Horn spells by "
           "-25%.' PORTS EXACTLY and is the clearest example of why this "
           "tree works: Horn of War, Horn of Alacrity and Battle Screech "
           "are already target_type 'party' ABILITIES in our data "
           "(abilities.py:2064 resolves 'party' to all living allies), so "
           "the talent modifies a real party aura instead of trying to BE "
           "one - which a talent effect can never do. CoA's own Blow the "
           "Horns! exists for exactly that purpose. Raised to 35% since the "
           "shared-cooldown clause ('All Ranger's Horn spells share a "
           "cooldown') has no mechanism and the three run independently. "
           "FRACTIONS where POSITIVE MEANS A REDUCTION. Was a pure scalar "
           "on our side."))

N.append(node(
    "scavenger", "Scavenger",
    "Increases the duration of Battle Screech and Horn of War by 2 turns "
    "and reduces the cooldown of Snapseed by 30%.",
    0, 0,
    effects={"ability_ranger_battle_screech_duration": 2,
             "ability_ranger_horn_of_war_duration": 2,
             "ability_ranger_snapseed_cooldown_pct": 0.30},
    connect=["quel_dorei_poison"],
    source="CoA: 'Increases the duration of Battle Screech and reduces the "
           "cooldown of Snapseed by 5 sec.' PORTS EXACTLY, with Horn of War "
           "added so the node covers both aura families. The durations "
           "land on real party abilities - Battle Screech runs 4 turns and "
           "goes to 6. talented_duration reads ability_<id>_duration and "
           "POSITIVE EXTENDS; it went unread long enough that Tinker's Fuel "
           "Injection on Mechsuit Form did nothing at all. SMALL INTEGERS "
           "IN TURNS, so spread() refuses to rank this node. Was a pure "
           "scalar on our side."))

N.append(node(
    "falcon_charmer", "Falcon Charmer",
    "Increases your pets' damage by 25% and their health by 20%.",
    0, 2,
    effects={"pet_damage": 0.25, "pet_health": 0.20},
    connect=["survivalist"],
    source="CoA: 'Increases the duration of War Falcons by 3 sec.' A "
           "summoned pet in this engine has no duration field to extend - "
           "ranger_summon_war_falcon is effect_type summon_pet with "
           "duration 0, and the pet persists until it dies - so CoA's "
           "clause has nothing to act on. Rebuilt as pet scaling, which is "
           "the same intent (your falcons matter more) through the only "
           "keys that reach them. THESE KEYS ARE LEGAL HERE because Ranger "
           "really does summon; tools/qa_pet_keys.py exists because Witch "
           "Doctor Shadow Hunting shipped three of them on a class that "
           "summons nothing. Both FRACTIONS. Was a pure scalar on our "
           "side."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "survivalist", "Survivalist",
    "Reduces the cooldown of Survival Potion by 30% and increases its "
    "healing by 20%.",
    1, 2,
    effects={"ability_ranger_survival_potion_cooldown_pct": 0.30,
             "ability_ranger_survival_potion_healing": 0.20},
    connect=["gutpiercer"],
    source="CoA: 'Reduces the cooldown of Survival Potion by -25%.' PORTS "
           "EXACTLY (raised to 30%), with the healing half added so the "
           "node is worth a point on a support spec. Survival Potion is "
           "effect_type heal, so it takes ability_<id>_HEALING - the key "
           "that went unread while 18 talents across four classes authored "
           "it, because only _damage was ever looked up. Using _damage on a "
           "heal passes every check and does nothing. Was a pure scalar on "
           "our side."))

N.append(node(
    "quel_dorei_poison", "Quel'dorei Poison",
    "Your ranged attacks have a 35% chance to poison the target for 3 "
    "turns.",
    1, 0,
    proc={"trigger": "on_weapon_swing", "chance": 35, "icd": 0,
          "apply_effect": {"effect_id": "queldorei_poison",
                           "name": "Quel'dorei Poison",
                           "effect_type": "dot", "duration": 3,
                           "potency": 22, "damage_school": "nature",
                           "dispel_type": "poison", "on_target": True}},
    connect=["forest_fighter"],
    source="CoA: 'Damage dealt by Woodland Arrow and Emerald Arrow now "
           "poison enemies for 3 seconds, dealing Nature damage every 1 "
           "sec.' The poison ports; the two-ability scoping does not (no "
           "per-ability proc trigger). 3 sec at 1-sec ticks is 3 ticks, "
           "which maps to 3 turns here exactly. A proc-applied dot carries "
           "`potency` as PER-TURN damage - 22 a turn, 66 over the poison - "
           "where an ABILITY rank's effect_value is the TOTAL and gets "
           "divided (abilities.py:2695). dispel_type 'poison' so it can be "
           "cleansed as one, matching the ranger_queldorei_poison ability "
           "already in our data."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "gutpiercer", "Gutpiercer",
    "Your attacks have a 25% chance to lower the target's resistances and "
    "leave them taking 4% more magic damage for 3 turns.",
    2, 2,
    proc={"trigger": "on_weapon_swing", "chance": 25, "icd": 0,
          "apply_effect": {"effect_id": "gutpiercer", "name": "Gutpiercer",
                           "effect_type": "debuff", "duration": 3,
                           "stat_mods": {"magic_resistance": -40,
                                         "magic_damage_taken_pct": 4},
                           "dispel_type": "magic", "on_target": True}},
    connect=["war_falconer"],
    source="CoA: 'Damage dealt by War Falcons and Dragonhawks now has a 15% "
           "chance to reduce the enemy's resistances by 75 and increase "
           "their Magic damage taken by -2% for 15 seconds.' The DEBUFF "
           "ports with both clauses, which is the valuable part - "
           "magic_resistance is one of only eight status stat_mods a "
           "monster reads, and it is FLAT, so -40 genuinely strips "
           "resistance. The TRIGGER does not: " + PETS + " Re-pointed to "
           "the Ranger's own swings. 15 sec -> 3 turns. THE TWO KEYS IN "
           "THIS DICT READ DIFFERENTLY: magic_resistance is a flat rating, "
           "magic_damage_taken_pct is PERCENTAGE POINTS inside a status "
           "effect (monster.py:742 divides by 100) and POSITIVE INCREASES "
           "damage taken - so 4 is +4%, and 0.04 would have been 0.04%. "
           "This node is also the one that will matter most when Kyle's "
           "shelved per-school resistance system lands."))

N.append(node(
    "forest_fighter", "Forest Fighter",
    "Reduces the cooldown of Woodland Arrow and Emerald Arrow by 35%.",
    2, 0,
    effects={"ability_ranger_woodland_arrow_cooldown_pct": 0.35,
             "ability_ranger_emerald_arrow_cooldown_pct": 0.35},
    connect=["venom_coated_seeds"],
    source="CoA: 'Your Skullpiercers or Emerald Arrows used with 5 stacks "
           "of Advantage now reduce the cooldown of Woodland Arrow by 5 "
           "sec.' The Advantage gate cannot be built (nothing reads a stack "
           "count) and there is no per-ability proc trigger, so the "
           "conditional cooldown reduction becomes a flat one on both "
           "arrows. Folded in CoA's War Falconer, which reduces Falcon's "
           "Call - an ability we do not have the positioning for. "
           "FRACTIONS where POSITIVE MEANS A REDUCTION. Was a pure scalar "
           "on our side."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "war_falconer", "War Falconer",
    "Increases your pets' damage by a further 30% and their armor by 25%.",
    3, 2,
    effects={"pet_damage": 0.30, "pet_armor": 0.25},
    connect=["plumes_of_war"],
    source="CoA: 'Reduces the cooldowns of Falcon's Call by -30 sec.' "
           "Falcon's Call is a targeted ground slow that summons a falcon "
           "per enemy caught - entirely positional, and nothing scales how "
           "many pets an ability summons - so the ability is not something "
           "a talent can usefully modify here. Rebuilt as pet scaling, "
           "stacking with Falcon Charmer to 55% pet damage. Folded in CoA's "
           "Aerial Assault and Dragonhawk Tamer, both of which add summons "
           "or targets: " + PETS + " Both FRACTIONS."))

N.append(node(
    "venom_coated_seeds", "Venom-Coated Seeds",
    "Your attacks have a 30% chance to weaken the target's attacks for 3 "
    "turns.",
    3, 0,
    proc={"trigger": "on_weapon_swing", "chance": 30, "icd": 0,
          "apply_effect": {"effect_id": "venom_coated_seeds",
                           "name": "Venom-Coated Seeds",
                           "effect_type": "debuff", "duration": 3,
                           "stat_mods": {"attack_power": -85},
                           "dispel_type": "poison", "on_target": True}},
    connect=["forest_herald"],
    source="CoA: 'Damage dealt by Snapseed now reduces the enemy's chance "
           "to hit by -15% for 10 seconds.' THERE IS NO RECIPIENT-SIDE "
           "'CHANCE TO BE HIT' OR ATTACKER-SIDE hit-reduction KEY that a "
           "debuff can carry - the eight stat_mods a monster reads are "
           "armor, attack_power, damage_taken_pct, healing_taken_pct, "
           "magic/physical/spell_damage_taken_pct and magic_resistance. A "
           "flat attack_power reduction is the nearest real equivalent: "
           "fewer of their hits landing and their hits being smaller both "
           "reduce incoming damage, which is what a support spec wants. "
           "attack_power is FLAT on a monster. The Snapseed scoping goes "
           "(no per-ability proc trigger). 10 sec -> 3 turns. Was a pure "
           "scalar on our side."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "plumes_of_war", "Plumes of War",
    "Increases the critical strike chance of Falconstrike and Emerald "
    "Arrow by 15%, and your critical strikes increase your damage by 5% "
    "for 3 turns, stacking up to 5 times.",
    4, 1,
    effects={"ability_ranger_falconstrike_crit": 15.0,
             "ability_ranger_emerald_arrow_crit": 15.0},
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "apply_effect": {"effect_id": "plumes_of_war",
                           "name": "Plumes of War",
                           "effect_type": "buff", "duration": 3,
                           "stat_mods": {"damage_dealt_pct": 5},
                           "max_stacks": 5, "dispel_type": None,
                           "on_target": False}},
    connect=["thalassian_brand"],
    source="CoA: 'Increases the critical strike chance of Falconstrike and "
           "Emerald Arrow by 15%. In addition, critical strikes with "
           "Falconstrike now increase the damage of subsequent "
           "Falconstrikes by 5% for 15 sec, stacking 5 times.' BOTH HALVES "
           "BUILD, which is unusual for this tree. The crit chance ports "
           "verbatim per ability. The stacking buff keeps CoA's 5% and 5 "
           "stacks; only 'of subsequent Falconstrikes' is widened to all "
           "damage, because a status effect cannot carry a per-ability key. "
           "15 sec -> 3 turns. Per-ability crit keys are PERCENTAGE POINTS; "
           "damage_dealt_pct inside a status effect is percentage points "
           "too. Was a pure scalar on our side."))

N.append(node(
    "forest_herald", "Forest Herald",
    "Your attacks have a 20% chance to mend your most wounded ally.",
    4, -1,
    proc={"trigger": "on_weapon_swing", "chance": 20, "icd": 1,
          "smart_heal_pct": 30},
    connect=["thalassian_brand"],
    source="CoA: 'Casting Toxic Dart and abilities that spend stacks of "
           "Advantage now have a 20% chance to spawn a green Dreamflower at "
           "a random location nearby. When an ally runs over the flower, "
           "they consume it to heal for 3% maximum health and gain 40% "
           "increased movement speed.' THE WHOLE DREAMFLOWER SYSTEM IS "
           "UNBUILDABLE - it needs ground objects that allies walk over, "
           "and there is no positioning of any kind - which also kills "
           "Highlander, Petalkeeper and the shared Dream Flowers passive, "
           "four talents in total. What survives is the intent: a ranger "
           "whose attacks heal the party. smart_heal_pct is one of only "
           "three payloads that reach an ALLY at all, and it picks the "
           "worst-off one, which is the nearest thing to a flower the "
           "hurt player runs to. CoA's 20% chance is kept verbatim."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "thalassian_brand", "Thalassian Brand",
    "Increases the damage of Thalassian Brand by 40% and its duration by 2 "
    "turns.",
    5, 0,
    effects={"ability_ranger_thalassian_brand_damage": 0.40,
             "ability_ranger_thalassian_brand_duration": 2},
    connect=["command_of_the_farstrider"],
    source="CoA: 'Mark an enemy for total destruction, increasing your "
           "allies ranged attack power against the target by 300+ and "
           "dealing 1115 Nature damage every 3 sec for 15 sec.' The ability "
           "already exists as a 4-turn dot. The ALLY half cannot be built - "
           "a talent effect never reaches an ally, and this is a per-target "
           "ally buff, which not even a party ABILITY could express - so "
           "the node boosts the dot instead. THE DURATION IS A REAL DAMAGE "
           "INCREASE: per-turn damage derives from the ability's OWN base "
           "duration (abilities.py:2777), so +2 turns is +2 full-value "
           "ticks, taking it 4 -> 6. SMALL INTEGER IN TURNS, so spread() "
           "refuses to rank this node."))

N.append(node(
    "wingman", "Wingman",
    "Reduces all damage you take by 5% and increases your maximum health "
    "by 6%.",
    5, 2,
    effects={"damage_taken_pct": -0.05, "max_health_pct": 0.06},
    connect=["command_of_the_farstrider"],
    source="CoA: 'Reduces all damage taken by 2% for each War Falcon or "
           "Dragonhawk you have active.' NOTHING READS A LIVE PET COUNT, so "
           "the per-pet scaling cannot exist - " + PETS + " Built as the "
           "flat mitigation CoA's typical two pets would give. Folded in "
           "CoA's Guidance, which scales damage dealt off the same unreadable "
           "count. BOTH KEYS ARE FRACTIONS AS TALENT EFFECTS: "
           "damage_taken_pct is read RAW (character.py:2696) so -0.05 is "
           "-5%, and max_health_pct is a fraction here but PERCENTAGE "
           "POINTS inside a status effect. Was a pure scalar on our side."))

N.append(node(
    "windrunners_reach", "Windrunner's Reach",
    "Increases your critical strike chance by 4% and your ranged attack "
    "power by 20% of your Agility.",
    1, -2,
    effects={"crit_chance_physical": 4.0,
             "ranged_ap_from_agility_pct": 0.20},
    connect=["blow_the_horns"],
    source="CoA over 2 ranks: 'Increases the range of your ranged abilities "
           "by 5 yds. In addition, your critical strike chance against "
           "Undead, Beasts, and Dragonkin is increased by 2%.' Range has no "
           "meaning here and NOTHING READS A CREATURE TYPE - no effect key "
           "or proc condition inspects a monster's family, which also "
           "killed Hunting Tactics' poison check and Brigand's weapon "
           "gates. So the crit becomes unconditional (doubled for the two "
           "ranks) and the range half is replaced by a real conversion: "
           "ranged_ap is in STAT_CONVERSION_TARGETS and agility in SOURCES. "
           "crit_chance_physical is PERCENTAGE POINTS; the conversion key "
           "is a FRACTION. Was a pure scalar on our side."))

N.append(node(
    "hunting_tactics", "Hunting Tactics",
    "Increases the damage of Skullpiercer by 30% and of Falconstrike by "
    "25%.",
    2, -2,
    effects={"ability_ranger_skullpiercer_damage": 0.30,
             "ability_ranger_falconstrike_damage": 0.25},
    connect=["scavenger"],
    source="CoA: 'Damage dealt by Skullpiercer is increased by 30% against "
           "Poisoned targets.' NOTHING READS A TARGET'S DEBUFFS, so the "
           "condition is dropped rather than shipped as something that "
           "silently never fires - the same call Archery's Serrations and "
           "Corrosive Poison needed. The 30% is kept unconditional, which "
           "is a real buff relative to CoA, and extended to Falconstrike so "
           "the node suits this tree rather than Archery's. Was a pure "
           "scalar on our side."))

N.append(node(
    "razorquills", "Razorquills",
    "Increases the damage of your periodic effects by 20%.",
    3, -2,
    effects={"dot_damage": 0.20},
    connect=["venom_coated_seeds"],
    source="CoA: 'Increases the tick rate of Toxic Dart and Emerald Arrows "
           "by -20%.' TICK RATE HAS NO MEANING IN A TURN-BASED ENGINE - a "
           "dot ticks exactly once per turn, full stop - so the clause has "
           "nothing to act on. Repriced as dot_damage, which is what a "
           "faster tick rate amounts to, and widened to every periodic "
           "effect because this tree applies three of them (Quel'dorei "
           "Poison, Toxic Dart, Thalassian Brand). Chronomancer's Crown of "
           "Power and Brigand's Lacerations needed the same treatment. "
           "A FRACTION. Was a pure scalar on our side."))

N.append(node(
    "thread_the_needle", "Thread The Needle",
    "Your critical strikes reduce the cost of your abilities by 20% for 3 "
    "turns, stacking up to 3 times.",
    4, 3,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "apply_effect": {"effect_id": "thread_the_needle",
                           "name": "Thread The Needle",
                           "effect_type": "buff", "duration": 3,
                           "stat_mods": {"all_ability_cost_pct": 20},
                           "max_stacks": 3, "dispel_type": None,
                           "on_target": False}},
    connect=["plumes_of_war"],
    source="CoA: 'Critical strikes with Quick Shot or Falconstrike now "
           "reduce the cast time and cost of your next ability that "
           "consumes Advantage by -34% for 15 seconds, stacking 3 times.' "
           "The COST half ports with CoA's own 3 stacks; the cast-time half "
           "cannot (there are no cast times) and 'that consumes Advantage' "
           "cannot be narrowed (nothing reads a stack count), so it applies "
           "to everything at 20% instead of 34%. The two-ability trigger "
           "becomes on_crit. 15 sec -> 3 turns. all_ability_cost_pct FLIPS "
           "AND I GOT IT WRONG FIRST: it is a FRACTION as a talent effect "
           "(Cunning and Banditry use 0.12) but PERCENTAGE POINTS inside a "
           "status effect, so 20 here is 20% and the 0.20 I authored would "
           "have delivered 0.2%. audit_talents caught it, the third "
           "convention it corrected in one night after "
           "stun_duration_reduction_pct and attack_power_pct. POSITIVE "
           "MEANS A REDUCTION on both sides."))

N.append(node(
    "phoenix_plumes", "Phoenix Plumes",
    "Your critical strikes restore 10 Focus.",
    4, -3,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "archery_points", "amount": 10}},
    connect=["forest_herald"],
    source="CoA: 'Your Skullpiercers and Woodland Arrows used with 5 stacks "
           "of Advantage now restore 3% Focus and summon a War Falcon for 6 "
           "sec.' The Advantage gate and the per-ability scoping both go. "
           "The Focus restore ports - though NOT as a percentage: "
           "grant_resource takes a FLAT `amount` and there is no pct_max "
           "field, which is the exact mistake that made Witch Doctor's "
           "Spiritual Devotee grant NOTHING while passing every check. 10 "
           "flat, which is what Deadshot generates. The falcon summon is "
           "dropped: cast_ability could fire the summon, but a proc that "
           "summons on every crit would flood the field with pets that "
           "nothing can read the count of anyway."))

N.append(node(
    "falcon_diving", "Falcon Diving",
    "Killing an enemy summons a War Falcon to fight alongside you.",
    5, -2,
    proc={"trigger": "on_kill", "chance": 100, "icd": 0,
          "cast_ability": "ranger_summon_war_falcon"},
    connect=["wingman"],
    source="CoA: 'Killing an enemy that yields experience or honor now "
           "summons a War Falcon to aid you in combat for 12 seconds. Can "
           "only occur once every 4 sec.' PORTS VERBATIM, which almost "
           "nothing in this tree does. on_kill is a live trigger and "
           "cast_ability takes a bare ability id, so the summon genuinely "
           "fires - and ranger_summon_war_falcon is ungated, so "
           "cast_ability's known failure mode (it does not check the caster "
           "has learned the ability) cannot bite. The 12-second lifetime is "
           "not expressible - a summoned pet has no duration field and "
           "persists until it dies - and the experience/honor qualifier and "
           "the 4-second limiter are both dropped, since a kill is already "
           "rare enough to need no internal cooldown."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "command_of_the_farstrider", "Command of the Farstrider",
    "Reduces the cooldown of all your party auras by a further 30%, "
    "increases your pets' damage by 25%, and your attacks have a 25% "
    "chance to mend your most wounded ally.",
    6, 0,
    effects={"ability_ranger_horn_of_war_cooldown_pct": 0.30,
             "ability_ranger_horn_of_alacrity_cooldown_pct": 0.30,
             "ability_ranger_battle_screech_cooldown_pct": 0.30,
             "ability_ranger_frenzy_cooldown_pct": 0.30,
             "ability_ranger_command_aura_cooldown_pct": 0.30,
             "pet_damage": 0.25},
    proc={"trigger": "on_weapon_swing", "chance": 25, "icd": 1,
          "smart_heal_pct": 40},
    source="CoA's Command Aura: 'Emanate an aura for 15 seconds, causing "
           "allied players to deal 35% ranged AP additional damage as "
           "Stormstrike Damage when they deal direct damage. Applies "
           "Exhaustion.' That is an ally-side proc - a buff that makes "
           "OTHER players' hits do extra damage - and nothing can do that: "
           "a talent effect never reaches an ally, a party ABILITY can only "
           "carry stat_mods, and no proc can be installed on an ally. The "
           "ranger_command_aura ABILITY exists as a party attack_power_pct "
           "buff, which is the honest approximation, so the capstone makes "
           "it and the other four auras available far more often instead. "
           "That is the right shape for a SUPPORT capstone: five real "
           "party abilities on much shorter cooldowns, stacking with Blow "
           "the Horns! to 65% off the three Horns. Plus the tree's two "
           "other themes - pets and the smart heal - so it pays off "
           "whichever way the tree was spent."))


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
        f"Ranger Archery owns low_health_threshold_pct for this class; the "
        f"key SUMS across talents. Found {setters}")

    # HALF THIS TREE MODIFIES PARTY ABILITIES rather than trying to be a
    # party aura, which a talent effect cannot do. If one of those abilities
    # quietly reverts to target_type "self", the cooldown talents still
    # "work" and the party support silently vanishes - nothing else in the
    # project would report it.
    ranger = json.loads(
        (ROOT / "data/abilities/ranger.json").read_text())["abilities"]
    by_id = {a["ability_id"]: a for a in ranger}
    for aid in PARTY_ABILITIES:
        a = by_id.get(aid)
        assert a is not None, f"{aid} is gone from the ability data"
        assert a.get("target_type") == "party", (
            f"{aid} is target_type {a.get('target_type')!r}, not 'party' - "
            f"this tree's cooldown and duration talents exist to modify it "
            f"AS a party aura, because a talent effect can never reach an "
            f"ally. Guardian's four auras and Reaper's two had to be "
            f"converted for this reason; Ranger's were already correct.")

    # pet keys are only meaningful on a class that summons.
    pet_nodes = [n["talent_id"] for n in TREE["nodes"]
                 if any(k.startswith("pet_") for k in (n.get("effects") or {}))]
    if pet_nodes:
        assert any(a.get("effect_type") == "summon_pet" for a in ranger), (
            f"{pet_nodes} author pet keys but Ranger summons nothing - "
            f"silent dead data, which tools/qa_pet_keys.py exists to catch")

    for n in TREE["nodes"]:
        mods = ((n.get("proc") or {}).get("apply_effect") or {}).get("stat_mods") or {}
        for key in ("magic_damage_taken_pct", "physical_damage_taken_pct"):
            if key in mods:
                assert abs(mods[key]) >= 1, (
                    f"{n['talent_id']} {key}={mods[key]} inside a status "
                    f"effect, where it is PERCENTAGE POINTS")

    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Ranger Farstrider: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points, {len(PARTY_ABILITIES)} party auras modified")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
