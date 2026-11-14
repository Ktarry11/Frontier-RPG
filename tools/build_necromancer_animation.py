#!/usr/bin/env python3
"""Rebuild Necromancer's Animation tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_necromancer_animation.py [--check]

SOURCE: data/reference/coa_worksheets/necromancer.md - 37 real Animation
talents. Role: DPS (summoner). Animation was 23 nodes with 5 procs.

THIS IS THE PET TREE, AND THE ENGINE'S PET SUPPORT IS THREE KEYS WIDE.

Necromancer genuinely summons - raise_ghoul, raise_skeletal_mage,
raise_banshee and raise_abomination are all effect_type summon_pet with
real templates - so pet_damage, pet_health and pet_armor are legal here.
tools/qa_pet_keys.py exists because Witch Doctor Shadow Hunting shipped
three of them on a class that summons nothing, and they were silent in play
while passing every check.

But that is the whole of it. PETS NEVER FIRE PROCS - there is no
fire_proc_trigger anywhere in entities/pet.py - NOTHING READS A LIVE PET
COUNT, no proc can apply an effect to a pet, no talent reaches a pet's
crit chance or haste (pet_haste is read by nothing at all), and nothing
changes how many pets an ability summons.

That is fourteen of CoA's 37 Animation talents, and it is most of what the
spec is about:
  Ghoul Mastery, Depravity, Plague Horde, Chomp     - pet damage triggers
  Scourge Disciple, Army of the Dead, Flesh         - live pet counts
    Symbiosis, Blood and Ice, Death and Ice
  Skeletal Artillery, Unrelenting Army              - extra summons
  Anti-Magic Shell                                  - a shield ON a pet
  Sepulchral Might                                   - converts pet Stamina
  Fetid Mark                                         - per-minion damage taken

Every one of them is rebuilt as flat pet scaling or re-pointed to the
caster, and each node records which. The result is a spec whose summons are
genuinely much stronger, but which cannot have the pet-driven proc chains
CoA writes. Closing that gap means threading a (caster, engine) pair into
Pet and giving it a fire_proc_trigger - the same change that would give
dots a periodic trigger and fix the DoT threat gap. Three problems, one
fix, and worth its own job rather than a workaround here.

CoA's Runic Power is our life_force (Necromancer is (LIFE_FORCE, None), the
PRIMARY pool, three generators), so the resource talents port. CoA's "Life
Force" as a RESERVATION pool that summons occupy does NOT exist - a summon
costs its resource once and the pet persists - so Master Animator
("increases your maximum Life Force by 1") and Champion of Kel'Thuzad have
nothing to act on and become cost reductions.

Death owns low_health_threshold_pct for the class at CoA's 20%; nothing
here sets it. Enforced by tools/qa_summing_thresholds.py.

NOT BUILDABLE beyond the above: Summoning Ritual and March of the Dead's
positioning; Bone King's instant-cast clause; Graverobber and Unrelenting
reduce cast and channel times, of which the engine has neither; Putrifier
and Summoning Prodigy extend a summon's lifetime, and a summoned pet has no
duration field; Crypt Keeper adds bounce targets; Long March swaps a
cooldown for a cast time.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/necromancer_animation.json"

#: The four real summons. Asserted in main() before any pet key is trusted.
SUMMONS = ["necromancer_raise_ghoul", "necromancer_raise_skeletal_mage",
           "necromancer_raise_banshee", "necromancer_raise_abomination"]

TREE = {
    "spec_name": "Necromancer Animation",
    "tree_id": "necromancer_animation",
    "description": ("An army that does the work - raised minions made "
                    "stronger, cheaper and faster to call."),
    "_source_note": (
        "Rebuilt 6 Nov 2026 from the 37 real CoA Animation talents (role "
        "DPS, summoner). Necromancer genuinely summons four pets, so "
        "pet_damage/pet_health/pet_armor are legal - but pets never fire "
        "procs, nothing reads a live pet count, no proc reaches a pet, and "
        "nothing changes how many an ability summons. That is FOURTEEN of "
        "CoA's 37 talents, rebuilt as flat pet scaling or re-pointed to the "
        "caster, each recorded. Closing the gap means giving Pet a "
        "fire_proc_trigger, which would also give dots a periodic trigger "
        "and fix the DoT threat gap - three problems, one fix, its own "
        "job."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20,
                          "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"necromancer_animation_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"necromancer_animation_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


PET_TRIGGER = (
    "CoA fires this off the MINIONS' damage. PETS NEVER FIRE PROCS - there "
    "is no fire_proc_trigger anywhere in entities/pet.py - so there is no "
    "event to hang it on. Rebuilt as flat pet scaling or re-pointed to the "
    "Necromancer's own casts. Fourteen Animation talents take this loss.")

PET_COUNT = (
    "CoA scales this off HOW MANY MINIONS ARE ACTIVE. Nothing reads a live "
    "pet count anywhere in this engine, so the per-pet scaling cannot "
    "exist. Built as the flat value CoA's typical minion count comes to.")

N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "graverobber", "Graverobber",
    "Reduces the cost of your Raise and Animate spells by 30%.",
    0, -4,
    effects={"ability_necromancer_raise_ghoul_cost_pct": 0.30,
             "ability_necromancer_raise_skeletal_mage_cost_pct": 0.30,
             "ability_necromancer_raise_banshee_cost_pct": 0.30,
             "ability_necromancer_raise_abomination_cost_pct": 0.30},
    connect=["sepulchral_might"],
    source="CoA: 'Reduces the mana cost and cast time of your Raise and "
           "Animate spells by -30%.' The cost half ports exactly, written "
           "out per ability because there is no ability-group concept to "
           "address all four summons at once. The cast-time half is dropped: "
           "there are no cast times. *_cost_pct keys are FRACTIONS where "
           "POSITIVE MEANS A REDUCTION. Was a pure scalar on our side."))

N.append(node(
    "sepulchral_might", "Sepulchral Might",
    "Increases your Stamina by 10% and your pets' health by 30%.",
    0, -2,
    effects={"stamina_pct": 10, "pet_health": 0.30},
    connect=["scourge_disciple", "forbidden_technique"],
    source="CoA over 2 ranks: 'Increases your Stamina by 5%. Increases your "
           "spell damage by an amount equal to 15% of the total of your "
           "Raised minion's Stamina.' The Stamina ports (doubled). THE "
           "CONVERSION CANNOT: STAT_CONVERSION_SOURCES holds strength, "
           "agility, intellect, spirit, stamina, ap, attack_power, "
           "spell_power, weapon and str_int - all read off the CASTER - and "
           "there is no mechanism to read a PET's stat at all, let alone "
           "sum it across minions. Re-pointed to pet_health, which keeps "
           "the node about minion durability. stamina_pct is PERCENTAGE "
           "POINTS (character.py:1263); pet_health is a FRACTION. Was a "
           "pure scalar on our side."))

N.append(node(
    "forbidden_technique", "Forbidden Technique",
    "Reduces the cooldown of your Animate spells by 35%.",
    0, 0,
    effects={"ability_necromancer_animate_skeletal_archers_cooldown_pct": 0.35,
             "ability_necromancer_animate_plaguefather_cooldown_pct": 0.35,
             "ability_necromancer_animate_bone_wraith_cooldown_pct": 0.35,
             "ability_necromancer_animate_tomb_king_cooldown_pct": 0.35},
    connect=["ghoul_mastery"],
    source="CoA: 'Casting Command spells now reduces the cooldown of your "
           "Animates by -1 sec.' The proc form cannot be built - 'Command "
           "spells' is not a category the engine knows and there is no "
           "per-ability proc trigger - so it becomes a flat reduction on "
           "all four Animates. Folded in CoA's Runic Animation, which "
           "reduces the same cooldowns by -20%. FRACTIONS where POSITIVE "
           "MEANS A REDUCTION; talented_cooldown floors at 1 turn, so "
           "stacking cannot make these spammable. Was a pure scalar on our "
           "side."))

N.append(node(
    "scourge_disciple", "Scourge Disciple",
    "Increases your haste by 12% and your pets' damage by 20%.",
    0, 2,
    effects={"haste": 12.0, "pet_damage": 0.20},
    connect=["mindless_fury"],
    source="CoA: 'Each active Skeletal Archer now increases your haste by "
           "5%.' " + PET_COUNT + " CoA's Animate: Skeletal Archers summons "
           "3 (and its own Skeletal Artillery talent adds a fourth), so "
           "two-to-three active is the realistic case and 12% is priced "
           "there rather than at the 15-20% a full set would give. Pet "
           "damage added so the node reads as a summoner's node rather than "
           "a bare haste scalar. haste is PERCENTAGE POINTS; pet_damage is "
           "a FRACTION. Was a pure scalar on our side."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "ghoul_mastery", "Ghoul Mastery",
    "Increases your pets' damage by a further 30%, and your damaging "
    "spells have a 20% chance to grant you 25% haste for 3 turns.",
    1, 0,
    effects={"pet_damage": 0.30},
    proc={"trigger": "on_damage_cast", "chance": 20, "icd": 2,
          "apply_effect": {"effect_id": "frenzied_ghoul",
                           "name": "Frenzied Ghoul",
                           "effect_type": "buff", "duration": 3,
                           "stat_mods": {"haste": 25.0},
                           "dispel_type": None, "on_target": False}},
    connect=["bone_king", "summoner"],
    source="CoA: 'Damage dealt by your Ghouls now has a 15% chance to "
           "transform them into a Frenzied Ghoul, increasing haste by 40% "
           "for 10 seconds.' " + PET_TRIGGER + " The haste buff is "
           "re-pointed to the CASTER, which is a real departure and the "
           "description says so - it is the Necromancer who speeds up, not "
           "the ghoul. (Even on the pet side it would have been silent: "
           "pet_haste is read by nothing at all, and no proc can apply an "
           "effect to a pet.) 10 sec -> 3 turns, 40% -> 25% with a 2-turn "
           "internal cooldown since it now fires off the player's own "
           "casts. The pet damage is the node's honest version of 'your "
           "ghouls hit harder'. Was a pure scalar on our side."))

N.append(node(
    "summoner", "Summoner",
    "Reduces the cost and cooldown of Sacrifice Undead by 25% and "
    "increases its healing by 30%.",
    1, 2,
    effects={"ability_necromancer_sacrifice_undead_cost_pct": 0.25,
             "ability_necromancer_sacrifice_undead_cooldown_pct": 0.25,
             "ability_necromancer_sacrifice_undead_healing": 0.30},
    connect=["mindless_fury"],
    source="CoA: 'Reduces the mana cost and cooldown of Sacrifice Undead by "
           "-20%.' PORTS EXACTLY, both halves, raised to 25%, with the "
           "healing added so the node is worth a point. Sacrifice Undead is "
           "effect_type heal in our data, so it takes "
           "ability_<id>_HEALING - the key that went unread while 18 "
           "talents across four classes authored it, because only _damage "
           "was ever looked up. Using _damage on a heal passes every check "
           "and does nothing at all. Was a pure scalar on our side."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "bone_king", "Bone King",
    "Your damaging spells have a 20% chance to make your next spell free.",
    2, -2,
    proc={"trigger": "on_damage_cast", "chance": 20, "icd": 2,
          "apply_effect": {"effect_id": "bone_king", "name": "Bone King",
                           "effect_type": "buff", "duration": 2,
                           "stat_mods": {"all_ability_cost_pct": 60},
                           "dispel_type": None, "on_target": False}},
    connect=["skeletal_artillery"],
    source="CoA: 'Casting Command spells now has a 15% chance to make your "
           "next Lichfrost or Blight free of cost and instant cast.' "
           "'Command spells' is not an engine category, there is no "
           "per-ability proc trigger, and there are no cast times - so what "
           "survives is the cost clause, as a short window of heavily "
           "reduced cost rather than a literal free cast: NOTHING WAIVES A "
           "RESOURCE COST OUTRIGHT, and nothing intercepts a spend, which "
           "is the same gap that killed Harvest Time's non-consume clause "
           "and Brigand's Rub It In. 60% off for 2 turns is the honest "
           "approximation and the description says 'free' loosely rather "
           "than claiming a mechanic that does not exist. CAREFUL: "
           "all_ability_cost_pct FLIPS - a FRACTION as a talent effect but "
           "PERCENTAGE POINTS inside a status effect, so 60 here is 60% and "
           "0.60 would have delivered 0.6%. audit_talents caught exactly "
           "that mistake on Ranger Farstrider's Thread The Needle tonight."))

N.append(node(
    "mindless_fury", "Mindless Fury",
    "Your spells increase your haste by 2% for 3 turns, stacking up to 5 "
    "times.",
    2, 1,
    proc={"trigger": "on_cast", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "mindless_fury",
                           "name": "Mindless Fury",
                           "effect_type": "buff", "duration": 3,
                           "stat_mods": {"haste": 2.0},
                           "max_stacks": 5, "dispel_type": None,
                           "on_target": False}},
    connect=["plague_horde"],
    source="CoA: 'Casting Animate or Command spells now increases your "
           "haste by 1% for 10 seconds, stacking 5 times.' PORTS ALMOST "
           "VERBATIM - on_cast fires on any spell, CoA's 5 stacks are kept "
           "and genuinely stack (nothing can READ the count, but the effect "
           "accumulates), and the rate is doubled to 2% because the window "
           "is shorter. 10 sec -> 3 turns. haste inside a status effect is "
           "PERCENTAGE POINTS, same as on the talent side."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "skeletal_artillery", "Skeletal Artillery",
    "Increases the damage of Animate: Skeletal Archers by 40% and of "
    "Animate: Plaguefather by 30%.",
    3, -2,
    effects={"ability_necromancer_animate_skeletal_archers_damage": 0.40,
             "ability_necromancer_animate_plaguefather_damage": 0.30},
    connect=["anti_magic_shell"],
    source="CoA over 2 ranks: 'Your Animate: Skeletal Archers now summons 1 "
           "additional Skeletal Archer.' NOTHING CHANGES HOW MANY PETS AN "
           "ABILITY SUMMONS - no effect key and no proc payload touches "
           "summon counts - which also killed Unrelenting Army and Spirit "
           "Army on Reaper. Our Animate: Skeletal Archers is a spell_damage "
           "enemy_aoe ability rather than a true summon, so extra damage is "
           "the faithful translation of an extra archer. Extended to "
           "Plaguefather, whose CoA talent fails the same way. Both "
           "FRACTIONS. Was a pure scalar on our side."))

N.append(node(
    "plague_horde", "Plague Horde",
    "Your damaging spells have a 25% chance to spread a plague to nearby "
    "enemies, dealing Shadow damage over 3 turns.",
    3, 1,
    proc={"trigger": "on_damage_cast", "chance": 25, "icd": 0,
          "apply_effect": {"effect_id": "zombie_plague",
                           "name": "Zombie Plague",
                           "effect_type": "dot", "duration": 3,
                           "potency": 26, "damage_school": "shadow",
                           "dispel_type": "disease", "on_target": True}},
    connect=["fetid_mark"],
    source="CoA: 'Damage dealt by your Undead minions now has a 10% chance "
           "to cast Plague Horde on themselves for 5 sec and emit Zombie "
           "Plague, dealing Plague damage to their target. Plague Horde: "
           "Enrage for 5 sec, increasing their critical strike chance by "
           "10%.' " + PET_TRIGGER + " The Enrage half is separately "
           "impossible (no proc can apply an effect to a pet, and no talent "
           "reaches a pet's crit chance), so only Zombie Plague survives, "
           "fired off the Necromancer's own casts at 25%. A proc-applied "
           "dot carries `potency` as PER-TURN damage - 26 a turn, 78 total "
           "- where an ABILITY rank's effect_value is the TOTAL and gets "
           "divided (abilities.py:2695). Note dot_duration_pct does not "
           "reach this: it is read in the ability dot branch, not the proc "
           "payload path."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "anti_magic_shell", "Anti-Magic Shell",
    "Increases your pets' armor by 40% and reduces your magic damage taken "
    "by 8%.",
    4, -2,
    effects={"pet_armor": 0.40, "magic_damage_taken_pct": -0.08},
    connect=["flesh_symbiosis"],
    source="CoA: 'When you summon a Raised minion, it now raises with a "
           "shield absorbing Magic damage equal to 40% of their maximum "
           "health.' AN ABSORB ON A PET CANNOT BE BUILT: no proc can apply "
           "an effect to a pet, there is no on-summon trigger, and "
           "shield_pct and absorb_pct_max_health are PROC PAYLOAD fields "
           "that would need a pet recipient. Rebuilt as pet armour plus the "
           "caster's own magic mitigation - CoA's intent (the summoner's "
           "side survives magic) reaching both halves of the pair through "
           "keys that work. magic_damage_taken_pct as a TALENT effect is a "
           "FRACTION read raw (character.py:2748), so -0.08 is -8%; inside "
           "a STATUS EFFECT the same key is percentage points AND positive "
           "INCREASES damage taken. pet_armor is a FRACTION. Was a pure "
           "scalar on our side."))

N.append(node(
    "fetid_mark", "Fetid Mark",
    "Your damaging spells have a 30% chance to leave the target taking 10% "
    "more damage from you for 3 turns.",
    4, 1,
    proc={"trigger": "on_damage_cast", "chance": 30, "icd": 0,
          "apply_effect": {"effect_id": "fetid_mark", "name": "Fetid Mark",
                           "effect_type": "debuff", "duration": 3,
                           "stat_mods": {"damage_taken_pct": 0.10},
                           "max_stacks": 3, "dispel_type": "magic",
                           "on_target": True}},
    connect=["flesh_symbiosis"],
    source="CoA: 'Dealing Shadow damage now increases the damage the target "
           "takes from your Skeletal Warriors by 1% for 10 seconds, "
           "stacking 10 times.' The debuff ports; 'from your Skeletal "
           "Warriors' cannot be narrowed (there is no per-source "
           "damage-taken key, and a pet's damage is not separable), so it "
           "applies to all your damage at 10% over 3 stacks instead of 1% "
           "over 10. 10 sec -> 3 turns. CAREFUL: bare damage_taken_pct is "
           "read RAW ON BOTH SIDES - unlike its physical_ and magic_ "
           "siblings, which divide by 100 inside a status effect - so 0.10 "
           "is 10% and authoring 10 would be +1000%. Asserted in main()."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "flesh_symbiosis", "Flesh Symbiosis",
    "Increases your armor by 20% and your maximum health by 8%.",
    5, -1,
    effects={"armor_pct": 20.0, "max_health_pct": 0.08},
    connect=["master_animator"],
    source="CoA: 'Each Abomination or Decaying Colossus active now "
           "increases your total Armor and magic resistance by 30% and "
           "causes you to periodically regenerate 2% maximum health every 5 "
           "sec.' " + PET_COUNT + " The periodic self-heal is separately "
           "impossible - there is no periodic or tick trigger of any kind - "
           "so it becomes maximum health instead. KEPT UNDER THE CAP ON "
           "PURPOSE: check_talent_balance enforces an armor_pct ceiling of "
           "60 and Venomancer Fortitude currently breaches it at 62 from "
           "two stacking nodes, so this tree carries exactly one armour "
           "node. armor_pct is PERCENTAGE POINTS; max_health_pct as a "
           "talent effect is a FRACTION. Was a pure scalar on our side."))

N.append(node(
    "corpse_wagon", "Corpse Wagon",
    "Increases the damage of Corpse Explosion by 25% and reduces the "
    "cooldown of Corpse Wagon by 35%.",
    5, 1,
    effects={"ability_necromancer_corpse_explosion_damage": 0.25,
             "ability_necromancer_corpse_wagon_cooldown_pct": 0.35},
    connect=["master_animator"],
    source="CoA: 'Increases all damage dealt by party and raid members by "
           "3%. Does not stack with similar effects. In addition, increases "
           "the damage of Corpse Explosion by 25%.' The Corpse Explosion "
           "half ports verbatim. THE PARTY HALF IS REAL BUT NOT FROM HERE: "
           "a talent effect can never reach an ally. The "
           "necromancer_corpse_wagon ABILITY carries the party "
           "damage_dealt_pct and was converted from target_type 'self' to "
           "'party' on 6 Nov 2026 - the same call Kyle made for Guardian's "
           "four auras and that was applied to Reaper's two today. So this "
           "talent does what a talent can: make that aura available more "
           "often. *_cooldown_pct is a FRACTION where POSITIVE MEANS A "
           "REDUCTION. Was a pure scalar on our side."))

N.append(node(
    "depravity", "Depravity",
    "Increases your pets' damage by a further 25%, and your critical "
    "strikes deal additional Shadow damage.",
    1, -4,
    effects={"pet_damage": 0.25},
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "damage_flat": 55, "school": "shadow"},
    connect=["graverobber"],
    source="CoA: 'Increases the melee haste of your Undead minions by 5% "
           "and gives their critical melee auto attacks an 50% chance to "
           "trigger Bone Club, dealing 40% of the damage dealt as Shadow "
           "Damage.' BOTH HALVES FAIL ON THE PET SIDE: pet_haste is read by "
           "nothing at all, and " + PET_TRIGGER + " Rebuilt as pet damage "
           "plus the Bone Club payload fired off the Necromancer's own "
           "crits, which is a real departure the description states. "
           "`school` only TYPES the damage_flat payload - it is not a "
           "trigger-side filter, so this fires on any crit, not only "
           "shadow ones."))

N.append(node(
    "crypt_keeper", "Crypt Keeper",
    "Increases the damage of Crypt Swarm by 30%, your area damage by 20%, "
    "and your pets' health by 20%.",
    2, 4,
    effects={"ability_necromancer_crypt_swarm_damage": 0.30,
             "aoe_damage": 0.20, "pet_health": 0.20},
    connect=["mindless_fury"],
    source="CoA: 'Your Crypt Swarm now bounces to 2 additional nearby "
           "enemies, at 30% reduced value per enemy struck.' NOTHING ADDS "
           "TARGETS TO AN ABILITY, so both the upside and the stated "
           "drawback are dropped together and the node becomes flat damage "
           "plus aoe_damage. aoe_damage is read at abilities.py:1600 only "
           "when target_type is enemy_aoe, so it is genuinely scoped to "
           "area attacks - this spec has five. Crypt Swarm is the biggest "
           "Life Force generator at 20. Both FRACTIONS. Was a pure scalar "
           "on our side."))

N.append(node(
    "army_of_the_dead", "Army of the Dead",
    "Increases your pets' armor by a further 30% and your spell critical "
    "strike chance by 5%.",
    3, 4,
    effects={"pet_armor": 0.30, "crit_chance_spell": 5.0},
    connect=["plague_horde"],
    source="CoA: 'While only 1 Abomination is active, the critical strike "
           "chance of your Ghouls is increased by 10% and haste by 10%.' "
           + PET_COUNT + " And even with a count, no talent key reaches a "
           "pet's crit chance or haste - pets scale off pet_damage, "
           "pet_health and pet_armor and nothing else. So the crit moves to "
           "the caster and the pet half becomes armour, which Anti-Magic "
           "Shell also supplies. pet_armor is a FRACTION; crit_chance_spell "
           "is PERCENTAGE POINTS. Was a pure scalar on our side."))

N.append(node(
    "putrifier", "Putrifier",
    "Increases the duration of Ghoulify and Mass Grave by 1 turn and "
    "reduces their cooldowns by 30%.",
    4, 4,
    effects={"ability_necromancer_ghoulify_duration": 1,
             "ability_necromancer_mass_grave_duration": 1,
             "ability_necromancer_ghoulify_cooldown_pct": 0.30,
             "ability_necromancer_mass_grave_cooldown_pct": 0.30},
    connect=["fetid_mark"],
    source="CoA: 'Increases the durations of Ghoulify and Mass Grave by "
           "25%.' Both abilities exist as 2-turn debuffs, and the duration "
           "key is an integer, so 25% becomes +1 turn - a 50% extension, "
           "which overshoots CoA slightly and is the smallest step the key "
           "can express. Cooldown reductions added so the node is worth a "
           "point on a control pair. SMALL INTEGERS IN TURNS, so "
           "talent_ranks.spread() refuses to rank this node, which is "
           "correct: a third of a turn per rank reads as nothing."))

N.append(node(
    "master_of_death", "Master of Death",
    "Your damaging spells have a 25% chance to restore 12 Life Force and "
    "deal additional Shadow damage.",
    5, -3,
    proc={"trigger": "on_damage_cast", "chance": 25, "icd": 0,
          "damage_flat": 60, "school": "shadow",
          "grant_resource": {"resource": "life_force", "amount": 12}},
    connect=["flesh_symbiosis"],
    source="CoA's Master of Death: 'Casting Command spells on an enemy now "
           "applies Crypt Plague.' Death's Plague Revenant already applies "
           "Crypt Plague off crits and owns that mechanic for the class, "
           "and 'Command spells' is not a category the engine knows, so "
           "repeating it here would be a duplicate. Rebuilt from CoA's "
           "Lich's Prodigy instead ('Your Glacial Tap now generates an "
           "additional 20 Runic Power, but its cost is increased by 25%') - "
           "the generation half is real, since CoA's Runic Power is our "
           "life_force and Necromancer is (LIFE_FORCE, None) with three "
           "generators. The stated drawback cannot be built: no talent key "
           "ADDS a resource cost, only reduces one, so it is dropped and "
           "the chance lowered to 25% in exchange rather than handing out a "
           "free upside. grant_resource's `amount` is FLAT - there is no "
           "pct_max field. `school` only TYPES the damage_flat payload."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "master_animator", "Master Animator",
    "Increases your pets' damage by a further 35% and their health by 30%, "
    "and reduces the cost of your Raise and Animate spells by a further "
    "30%.",
    6, 0,
    effects={"pet_damage": 0.35, "pet_health": 0.30,
             "ability_necromancer_raise_ghoul_cost_pct": 0.30,
             "ability_necromancer_raise_skeletal_mage_cost_pct": 0.30,
             "ability_necromancer_raise_banshee_cost_pct": 0.30,
             "ability_necromancer_raise_abomination_cost_pct": 0.30},
    source="CoA: 'Increases your maximum Life Force by 1.' CoA'S LIFE FORCE "
           "IS A RESERVATION POOL - its summons 'occupy' 1 to 3 of it, so "
           "raising the maximum means fielding one more minion - AND THAT "
           "MODEL DOES NOT EXIST HERE. Our summons cost their resource once "
           "and the pet then persists with nothing reserved, and there is no "
           "key that raises a secondary pool's ceiling anyway "
           "(max_energy_bonus and character max_energy are both authored "
           "somewhere in this project and read by nothing). So the capstone "
           "delivers the same outcome - more and stronger minions - through "
           "the keys that work: pet scaling stacking with Scourge Disciple, "
           "Ghoul Mastery and Sepulchral Might to +85% pet damage and +90% "
           "pet health, plus cost reductions stacking with Graverobber to "
           "60% off every summon, which is as close to 'field another "
           "minion' as the engine gets. All FRACTIONS; the cost keys are "
           "reductions."))


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
        f"this class; the key SUMS across talents. Found {setters}")

    # THIS TREE IS BUILT ON pet_* KEYS, which are silent dead data on a
    # class that does not summon - exactly what tools/qa_pet_keys.py exists
    # to catch after Witch Doctor Shadow Hunting shipped three. Assert the
    # summons rather than trusting the memory of them.
    abilities = json.loads(
        (ROOT / "data/abilities/necromancer.json").read_text(encoding="utf-8"))["abilities"]
    by_id = {a["ability_id"]: a for a in abilities}
    for aid in SUMMONS:
        a = by_id.get(aid)
        assert a is not None and a.get("effect_type") == "summon_pet", (
            f"{aid} is not a summon_pet ability any more - every pet_* key "
            f"in this tree becomes silent dead data if Necromancer stops "
            f"summoning")

    # pet_haste is read by NOTHING. If a later edit reaches for it here it
    # would look exactly like the three keys that do work.
    for n in TREE["nodes"]:
        eff = n.get("effects") or {}
        assert "pet_haste" not in eff, (
            f"{n['talent_id']} authors pet_haste, which is read by no "
            f"engine code at all - pets scale off pet_damage, pet_health "
            f"and pet_armor and nothing else")
        for k in ("pet_damage", "pet_health", "pet_armor"):
            if k in eff:
                assert 0 < eff[k] < 1, (
                    f"{n['talent_id']}.{k}={eff[k]} - a FRACTION")
        mods = ((n.get("proc") or {}).get("apply_effect") or {}).get("stat_mods") or {}
        if "damage_taken_pct" in mods:
            assert -1 < mods["damage_taken_pct"] < 1, (
                f"{n['talent_id']} damage_taken_pct={mods['damage_taken_pct']}"
                f" - read RAW on both sides, so 10 means +1000%")
        if "all_ability_cost_pct" in mods:
            assert mods["all_ability_cost_pct"] >= 1, (
                f"{n['talent_id']} all_ability_cost_pct="
                f"{mods['all_ability_cost_pct']} inside a status effect, "
                f"where the key is PERCENTAGE POINTS - a fraction here "
                f"delivers a hundredth of the intent")

    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Necromancer Animation: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points, {len(SUMMONS)} summons asserted")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
