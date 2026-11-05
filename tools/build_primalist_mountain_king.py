#!/usr/bin/env python3
"""Rebuild Primalist's Mountain King tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_primalist_mountain_king.py [--check]

SOURCE: data/reference/coa/primalist.json - 41 real Mountain King talents
from Ascension's own CoA Builder payload, the same data allthingscoa.com
presents. Role: TANK. coa_playstyles.json: "Enhancement Shaman", which for
a tank spec means it holds threat by hitting things rather than by sitting
still.

The shipped tree was 22 nodes: 14 pure scalars, 2 procs, 6 unlocks, and
most of the scalars were 5 ranks of +2-3% armour or threat.

WHAT THE SPEC IS, and it is two things the old tree had neither of:

  1. EARTH'S RAGE. CoA: "Damage dealt by Primal Rush and Quake now grant
     Earth's Rage - increases haste by 2% for 8 seconds, stacking 5
     times", with Mountain Thane adding a sixth stack and Call of the
     Mountain paying out at full stacks. A tank that speeds up the longer
     it swings.
  2. AVOIDANCE AS A RESOURCE. Spiritbound turns a dodge or parry into
     Rage, Mountain Mover banks stacks off it. This engine has on_avoid,
     on_parry and on_block as real triggers and the old tree used none of
     them - which for a tank spec is the whole interesting half missing.

CONVENTIONS, which do not agree with each other:
  parry / dodge / haste / armor in a status effect      raw, "4.0" = 4%
  armor_pct, stamina_pct, attack_power_pct              percentage POINTS
  threat_generation_pct, physical_damage_taken_pct
    as TALENT effects                                   FRACTION
  damage_dealt_pct in a status effect                   percentage POINTS
  *_cost_pct / *_cooldown_pct        FRACTION, POSITIVE MEANS A REDUCTION

WHAT IS NOT BUILDABLE HERE, stated rather than faked:
  - Off-hand weapons are not modelled as a separate damage source, so
    Stone Soldier's "+30% off hand damage" and Terrasmash's "damage dealt
    by your off hand weapon" have nothing to attach to.
  - Charges do not exist, so Rock Solid ("+5 charges of Rock Barrier") and
    Quakeformer ("refresh a charge of Quake") become cooldown work.
  - No trigger fires when a buff EXPIRES, so Primal Guardian ("when
    Earthen Avatar, Bearskin or Rock Barrier is removed or expires") has
    no hook and is rerouted.
  - Nothing reads another effect's stack count, so Call of the Mountain
    ("reaching 5 stacks of Earth's Rage") cannot gate on it - same limit
    as Geomancy's Earthshaping payoffs.
  - "expertise" is read by no engine code, so Tilling the Earth keeps only
    its Bash half.
  - max_rage is a hardcoded 100 with no talent hook, so nothing here
    raises it.

TURN-BASED CUTS. Every yard radius and frontal cone is gone, Mountain
Fury's pull with them. Movement speed on Earth's Rage is dropped and the
haste half kept. Replenishment's "allies within 100 yds" is a party effect
with no aura mechanism, so Resources of the Earth is rerouted to the
Primalist's own regeneration. Two CoA entries in this export - Mountain
Avatar and Seismic Smash - have broken template descriptions ($d2, $d4)
and are built from their names and tree position only.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/primalist_mountain_king.json"

SEISMIC = ["primalist_seismic_crash", "primalist_seismic_tremor",
           "primalist_seismic_wave"]

#: CoA: "Damage dealt by Primal Rush and Quake now grant Earth's Rage."
RAGE_GENERATORS = ["primalist_primal_rush", "primalist_quake"]

#: CoA: "Increases movement speed by 4% and haste by 2% for 8 seconds,
#: stacking 5 times." Movement speed is dropped; haste is the half that
#: means anything on a turn meter. Status stat_mods are multiplied by the
#: stack count, so 5 stacks is +10 haste.
EARTHS_RAGE = {
    "effect_id": "primalist_earths_rage", "name": "Earth's Rage",
    "effect_type": "buff", "duration": 3, "max_stacks": 5,
    "stat_mods": {"haste": 2.0},
    "on_target": False, "real_time_seconds": None,
}

TREE = {
    "spec_name": "Primalist Mountain King",
    "tree_id": "primalist_mountain_king",
    "description": ("Stone-clad thane - turns every blow dodged into Rage "
                    "and speeds up the longer the fight runs."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from data/reference/coa/primalist.json "
        "(41 real CoA Mountain King talents, role TANK, 'Enhancement "
        "Shaman'). Replaces a 22-node tree of 14 pure scalars and 2 procs, "
        "most of the scalars 5 ranks of +2-3% armour or threat. The two "
        "things the spec is built on were both absent: Earth's Rage, the "
        "stacking haste the whole tree keys off, and avoidance as a "
        "resource - this engine has on_avoid, on_parry and on_block as real "
        "triggers and the old tree used none of them. All 6 unlock nodes "
        "are preserved - see tools/qa_abilities_obtainable.py."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source="", active=False):
    entry = {
        "talent_id": f"primalist_mountain_king_{nid}",
        "name": name,
        "description": desc,
        "node_type": "active" if active else "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"primalist_mountain_king_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


def unlock(nid, name, ability, blurb, tier, x, *, connect=None, source=""):
    return node(nid, name, f"Learn {name.rstrip('!')}. {blurb}", tier, x,
                effects={"unlock_ability": ability}, connect=connect,
                source=source, active=True)


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "unyielding_form", "Unyielding Form",
    "Increases your parry and dodge chance by 1.5% per rank.",
    0, -5, ranks=2,
    effects={"parry": 1.5, "dodge": 1.5},
    connect=["king_of_the_mountain"],
    source="CoA: 'Increases your parry and dodge chance by 3% and your Armor "
           "contribution from mail and plate by 25%.' Armour-by-armour-type "
           "is not a key - there is no per-armour-class scaling in this "
           "engine - so that half is dropped. Split over CoA's 2 ranks, so a "
           "full investment is CoA's 3%. Was armor_pct 6.0, which is neither "
           "half of this talent."))

N.append(node(
    "granite_hide", "Granite Hide",
    "Increases your armor by 3% per rank.",
    0, -3, ranks=4,
    effects={"armor_pct": 3.0},
    connect=["king_of_the_mountain"],
    source="Not a CoA node - kept from the previous tree. A tank tree needs "
           "a plain armour pick and this is it; armor_pct takes percentage "
           "POINTS."))

N.append(node(
    "earthen_resolve", "Earthen Resolve",
    "Increases your threat generation by 3% per rank.",
    0, -1, ranks=3,
    effects={"threat_generation_pct": 0.03},
    connect=["blessed_by_the_earth"],
    source="Not a CoA node - kept from the previous tree at 2% -> 3%. Threat "
           "is how a tank does its job and this is the only node in the tree "
           "that supplies it directly. FRACTION as a talent effect, unlike "
           "the status-effect buff version the engine divides by 100."))

N.append(node(
    "seismically_efficient", "Seismically Efficient",
    "Seismic Crash generates 5 additional Rage.",
    0, 1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["primalist_seismic_crash"],
          "grant_resource": {"resource": "rage", "amount": 5}},
    connect=["spiritbound"],
    source="CoA verbatim: 'Increases the Rage generated from Seismic Crash by "
           "5 and Seismic Spike by 2.' Frontier has no Seismic Spike, so only "
           "the Crash half is built. Seismic Crash costs mana and this spec's "
           "defensive abilities cost Rage, so this is the bridge between the "
           "two halves of a dual-resource class."))

N.append(node(
    "stone_soldier", "Stone Soldier",
    "Increases your attack power by 3% and your chance to hit by 1.5% per "
    "rank.",
    0, 3, ranks=2,
    effects={"attack_power_pct": 3.0, "hit_rating": 1.5},
    connect=["bash"],
    source="CoA: 'Increases the damage of your off hand weapon by 30% and "
           "your chance to hit by 3%.' Off-hand weapons are not a separate "
           "damage source in this engine, so that half becomes general attack "
           "power rather than a key that would read as nothing. Hit split "
           "over CoA's 2 ranks."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "king_of_the_mountain", "King of the Mountain",
    "Increases your parry, dodge and haste by 15% of your Strength.",
    1, -5,
    effects={"parry_from_strength_pct": 0.15,
             "dodge_from_strength_pct": 0.15,
             "haste_from_strength_pct": 0.15},
    connect=["mountain_mover"],
    source="CoA verbatim: 'Level 20 Passive. Increases your parry, dodge, and "
           "haste rating by 15% of your Strength.' All three pairings are "
           "live - parry, dodge and haste are all in "
           "STAT_CONVERSION_TARGETS and strength is in "
           "STAT_CONVERSION_SOURCES. Conversions are FRACTIONS. The previous "
           "tree had this at 0.01 per rank over 4 ranks, i.e. 4% against "
           "CoA's 15%."))

N.append(unlock(
    "mountain_hammer", "Mountain Hammer", "primalist_mountain_hammer",
    "Hurl a hammer that leaves the target reeling.",
    1, -3, connect=["everythings_a_nail"],
    source="CoA: 'Throw a hammer at an enemy dealing Physical damage and "
           "stunning them for 5 seconds.' Kept from the previous tree, where "
           "this unlock was confusingly named Mountain Mover."))

N.append(node(
    "blessed_by_the_earth", "Blessed by the Earth",
    "Primal Rush and Quake grant Earth's Rage, increasing your haste by 2% "
    "for 3 turns, stacking 5 times.",
    1, -1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": RAGE_GENERATORS,
          "apply_effect": dict(EARTHS_RAGE)},
    connect=["raging_earth"],
    source="CoA verbatim: 'Damage dealt by Primal Rush and Quake now grant "
           "Earth's Rage. Earth's Rage: Increases movement speed by 4% and "
           "haste by 2% for 8 seconds, stacking 5 times.' This is the "
           "mechanic the rest of the tree keys off and the old tree had no "
           "form of it. Movement speed is dropped; haste on a turn meter "
           "means acting more often, which is what a ramping tank wants. 8 "
           "sec is 3 turns. Status stat_mods multiply by stacks, so 5 stacks "
           "is +10 haste."))

N.append(unlock(
    "quake", "Quake", "primalist_quake",
    "Stomp the ground and slow everything standing on it.",
    1, 1, connect=["quakeformer"],
    source="CoA: 'Stomp the ground, dealing Weapon Damage plus Nature damage "
           "to enemies within 8 yds and reduces their melee and ranged haste "
           "by 20% for 10 sec.' Kept from the previous tree. One of the two "
           "Earth's Rage generators, so it has to be learnable at the same "
           "depth as Blessed by the Earth."))

N.append(node(
    "spiritbound", "Spiritbound",
    "Dodging or parrying an attack grants you 5 Rage and brings your Seismic "
    "abilities a turn closer to ready.",
    1, 3,
    proc={"trigger": "on_avoid", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "rage", "amount": 5},
          "reset_cooldown": {"abilities": SEISMIC, "turns": 1}},
    connect=["mountain_mover"],
    source="CoA verbatim: 'Avoiding attacks now grants you 5 Rage and reduces "
           "the cooldown of your Seismic abilities by -1 sec.' Ports almost "
           "exactly: on_avoid is a real trigger, and reset_cooldown with "
           "turns:1 knocks one turn off rather than fully resetting. This is "
           "the node that makes avoidance a resource instead of just damage "
           "the tank did not take."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "mountain_mover", "Mountain Mover",
    "Dodging or parrying an attack grants a stack of Mountain Mover, "
    "increasing your parry by 2% for 3 turns, stacking 5 times.",
    2, -5,
    proc={"trigger": "on_avoid", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "primalist_mountain_mover",
                           "name": "Mountain Mover", "effect_type": "buff",
                           "duration": 3, "max_stacks": 5,
                           "stat_mods": {"parry": 2.0},
                           "on_target": False}},
    connect=["call_of_the_mountain"],
    source="CoA: 'Avoiding an attack grants a stack of Mountain Mover for 10 "
           "sec, stacking 5 times. Wildclaw consumes Mountain Mover stacks to "
           "cost 10% less Rage per stack.' The consume-for-cost half is not "
           "buildable twice over: nothing reads another effect's stack count, "
           "and ability cost keys are read through get_talent_effects() which "
           "never includes status effects. So the stacks pay out as parry "
           "instead - avoidance begetting avoidance - which keeps the "
           "snowball CoA is after through a stat a status effect can "
           "actually grant. CoA's 5 stacks and 10 sec (3 turns) kept."))

N.append(node(
    "bash", "Bash",
    "Your weapon swings have a 30% chance to stun the target for a turn.",
    2, -3,
    proc={"trigger": "on_weapon_swing", "chance": 30, "icd": 2,
          "apply_effect": {"effect_id": "primalist_bash_stun",
                           "name": "Bash", "effect_type": "debuff",
                           "duration": 1, "stat_mods": {},
                           "is_stun": True, "on_target": True}},
    connect=["tilling_the_earth"],
    source="CoA verbatim: 'Your auto attacks have a 30% chance to deal 50% "
           "Weapon Damage and stun them for 1 seconds.' is_stun in an "
           "apply_effect payload is live (Mage Fire's Impact uses it). CoA's "
           "30% chance kept, with a 2-turn internal cooldown: a 1-turn stun "
           "at 30% per swing with no icd would chain-lock a target in a "
           "turn-based fight in a way a 1-second stun never does in real "
           "time. The extra 50% weapon damage is dropped - the stun is the "
           "talent."))

N.append(node(
    "everythings_a_nail", "Everything's A Nail",
    "Increases the damage of Mountain Hammer by 25% per rank.",
    2, -1, ranks=2,
    effects={"ability_primalist_mountain_hammer_damage": 0.25},
    connect=["earthenforged_barrier"],
    source="CoA verbatim: 'Increases the damage of Mountain Hammer by 50%.' "
           "Split over 2 ranks at the same ceiling. Replaces the previous "
           "tree's Mountain Hammer Mastery, which was 5 ranks of +8%."))

N.append(node(
    "thanes_guidance", "Thane's Guidance",
    "Your weapon swings bring Mountain Hammer a turn closer to ready.",
    2, 1,
    proc={"trigger": "on_weapon_swing", "chance": 100, "icd": 0,
          "reset_cooldown": {"abilities": ["primalist_mountain_hammer"],
                             "turns": 1}},
    connect=["raging_earth"],
    source="CoA verbatim: 'Auto attacks now reduce the cooldown of Mountain "
           "Hammer by -1 sec.' A second of real-time cooldown is a turn here, "
           "so this ports directly. Also carries CoA's Hammer Time! ('your "
           "Mountain Hammer now strikes up to 5 enemies'), which is not "
           "built: primalist_mountain_hammer is single-target, and no talent "
           "key converts an ability to enemy_aoe - aoe_damage only applies to "
           "abilities already flagged that way."))

N.append(node(
    "quakeformer", "Quakeformer",
    "Casting Wildclaw or a Seismic ability has a 25% chance to make Quake "
    "ready again at once.",
    2, 3,
    proc={"trigger": "on_damage_cast", "chance": 25, "icd": 1,
          "ability_filter": ["primalist_wildclaw"] + SEISMIC,
          "reset_cooldown": ["primalist_quake"]},
    connect=["tilling_the_earth"],
    source="CoA verbatim: 'Casting Wildclaw and Seismic abilities now has a "
           "25% chance to refresh a charge of Quake.' Charges are cooldowns "
           "here, so refreshing one is a full reset. CoA's 25% kept, with a "
           "1-turn internal cooldown so it cannot chain. Quake is an Earth's "
           "Rage generator, so this feeds the spec's ramp."))

# ---- tier 3 -------------------------------------------------------------
N.append(unlock(
    "rock_barrier", "Rock Barrier", "primalist_rock_barrier",
    "Wrap yourself in stone that soaks up what gets through.",
    3, -4, connect=["call_of_the_mountain"],
    source="Kept from the previous tree."))

N.append(node(
    "earthenforged_barrier", "Earthenforged Barrier",
    "Increases the armor Rock Barrier provides by 50% and reduces the cost of "
    "your abilities by 15% while it holds.",
    3, -2,
    effects={"ability_primalist_rock_barrier_potency": 0.50,
             "all_ability_cost_pct": 0.15},
    connect=["primal_guardian"],
    source="CoA: 'Increases the Armor provided by Rock Barrier by 50% and it "
           "now reduces the cost of your spells and abilities by -25% for the "
           "duration.' The armour half ports exactly. The cost reduction "
           "cannot be conditioned on Rock Barrier being active - there is no "
           "'while this buff is up' gate for an effect key - so it is "
           "unconditional and cut from 25% to 15% to pay for that. Positive "
           "is the reduction direction for _cost_pct. Also carries CoA's Rock "
           "Solid ('+5 charges of Rock Barrier'), which charges do not exist "
           "to support."))

N.append(node(
    "raging_earth", "Raging Earth",
    "Quake opens a fissure that burns the ground for 2 turns.",
    3, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["primalist_quake"],
          "apply_effect": {"effect_id": "primalist_fissure",
                           "name": "Fissure", "effect_type": "dot",
                           "duration": 2, "potency": 30,
                           "damage_school": "nature", "on_target": True}},
    connect=["earthen_avatar"],
    source="CoA verbatim: 'Your Quake now creates a fissure beneath you that "
           "deals an additional Nature damage every 2 sec for 6 seconds.' "
           "6 sec is 2 turns. 'Beneath you' is positional and means nothing "
           "here, so the fissure lands on the target instead of on the "
           "ground. A proc-applied dot takes a flat potency - there is no "
           "'percentage of attack power' form for apply_effect - so 30 per "
           "turn, in line with Frontier's other mid-level dots."))

N.append(node(
    "mountain_thane", "Mountain Thane",
    "Increases your Stamina by 2.5% per rank.",
    3, 2, ranks=2,
    effects={"stamina_pct": 2.5},
    connect=["earthen_avatar"],
    source="CoA: 'Increases your Stamina by 5% and causes Earth's Rage to "
           "stack 1 additional time.' Split over CoA's 2 ranks. The extra "
           "Earth's Rage stack is dropped: max_stacks lives on the effect "
           "Blessed by the Earth applies, and no key edits a sibling node's "
           "payload. stamina_pct takes percentage POINTS."))

N.append(node(
    "tilling_the_earth", "Tilling the Earth",
    "Increases the chance for Bash to trigger by 3% per rank.",
    3, 4, ranks=2,
    effects={"ability_primalist_wildclaw_crit": 3.0},
    connect=["shattering"],
    source="CoA: 'Increases the chance to trigger Bash by 3% and increases "
           "your expertise by 5.' Neither half is buildable as written: "
           "'expertise' is read by no engine code, and a talent cannot raise "
           "ANOTHER node's proc chance - the chance lives on Bash's own "
           "payload. Rerouted to crit on Wildclaw, the auto-attack-adjacent "
           "ability Bash hangs off, so the point still buys more out of "
           "swinging. Flagged rather than authored as a key that reads as "
           "nothing."))

# ---- tier 4 -------------------------------------------------------------
N.append(unlock(
    "earthen_avatar", "Earthen Avatar", "primalist_earthen_avatar",
    "Become the mountain for a few turns.",
    4, -3, connect=["mountain_fury"],
    source="CoA: 'Become an avatar of the earth, increasing your damage dealt "
           "and reducing your damage taken by 15%, and increasing your melee "
           "haste by 20% for 20 seconds. Immune to stuns, roots, and snares.' "
           "Kept from the previous tree."))

N.append(node(
    "call_of_the_mountain", "Call of the Mountain",
    "Increases your parry chance by 5% and reduces the physical damage you "
    "take by 5%.",
    4, -1,
    effects={"parry": 5.0, "physical_damage_taken_pct": -0.05},
    connect=["mountain_fury"],
    source="CoA: 'Level 40 Passive. Reaching 5 stacks of Earth's Rage now "
           "grants Call of the Mountain: increases your parry chance by 5% "
           "and reduces damage taken by -5%.' Nothing reads another effect's "
           "stack count, so the gate is dropped and the payout is permanent - "
           "the same limit Geomancy's Earthshaping payoffs run into. CoA's "
           "numbers kept because they are modest enough to stand "
           "unconditionally. NEGATIVE is the reduction direction for "
           "physical_damage_taken_pct as a talent effect, which is the "
           "opposite of the _cost_pct and _cooldown_pct convention - the "
           "previous tree's Steadfast Stance had this right."))

N.append(node(
    "primal_guardian", "Primal Guardian",
    "Taking a heavy blow steels you, increasing your haste and parry by 10% "
    "for 3 turns.",
    4, 1,
    proc={"trigger": "on_damage_taken", "chance": 20, "icd": 3,
          "apply_effect": {"effect_id": "primalist_primal_guardian",
                           "name": "Primal Guardian", "effect_type": "buff",
                           "duration": 3, "max_stacks": 1,
                           "stat_mods": {"haste": 10.0, "parry": 10.0},
                           "on_target": False}},
    connect=["mountain_fury"],
    source="CoA: 'When Earthen Avatar, Bearskin or Rock Barrier is removed or "
           "expires, you now gain 10% melee haste and parry chance for 15 "
           "seconds.' NO TRIGGER FIRES WHEN A BUFF EXPIRES - the trigger list "
           "is cast, crit, damage dealt, damage taken, weapon swing, kill, "
           "block, avoid and parry, and none of them is 'an effect fell off "
           "me'. Rerouted onto taking damage at a 20% chance with a 3-turn "
           "internal cooldown, which lands it at roughly the cadence a "
           "defensive cooldown expiring would. CoA's two stats and 10% kept; "
           "15 sec is 3 turns."))

N.append(unlock(
    "terrasurge", "Terrasurge", "primalist_terrasurge",
    "Hurl a globule of earth that strips the target's armour.",
    4, 3, connect=["mountain_fury"],
    source="CoA: 'Unleash a massive globule of earth at an enemy, dealing "
           "Physical damage and reducing their Armor by -50% for 10 sec. "
           "Pierces through absorption, deflection, and reflection effects.' "
           "Kept from the previous tree. Worth knowing: Geomancy's capstone "
           "Heavy Earth buffs Terrasurge, and THIS is the only node in the "
           "game that unlocks it - a Geomancer taking that capstone has to "
           "reach into this tree for the ability, which is a real "
           "cross-spec dependency rather than an oversight."))

# ---- tier 5 -------------------------------------------------------------
N.append(unlock(
    "mountain_fury", "Mountain Fury",
    "primalist_judgement_of_the_three_hammers",
    "Call down the judgement of three hammers.",
    5, -2, connect=["mountain_avatar"],
    source="CoA's Judgement of The Three Hammers: 'While active, dealing "
           "direct damage has a 20% chance to hurl 3 hammers over 2 seconds, "
           "each dealing Physical damage.' Kept from the previous tree, which "
           "already paired this name with that ability. CoA's Mountain Fury "
           "is a separate frontal-cone pull that Frontier has no ability for; "
           "the cone and the pull are both positional anyway."))

N.append(node(
    "shattering", "Shattering",
    "Your critical strikes sharpen you further, increasing your damage by 1% "
    "per stack for 3 turns, stacking 10 times.",
    5, 0,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "primalist_shattering",
                           "name": "Shattering", "effect_type": "buff",
                           "duration": 3, "max_stacks": 10,
                           "stat_mods": {"damage_dealt_pct": 1.0},
                           "on_target": False}},
    connect=["mountain_avatar"],
    source="CoA: 'Damage dealt by each hammer triggered by Judgment of The "
           "Three Hammers now grants you 1% increased critical strike chance "
           "and damage for 10 seconds, stacking up to 10 times.' The hammers "
           "are an ability's internal proc, not something a talent trigger "
           "sees, so this hangs off crits instead. The crit-chance half is "
           "dropped and the damage half kept, because stacking both would "
           "make it self-feeding. damage_dealt_pct is the status-effect route "
           "to a damage multiplier and takes percentage POINTS. CoA's 10 "
           "stacks and 1% kept."))

N.append(node(
    "earth_destroyer", "Earth Destroyer",
    "Reduces the cooldown of Judgement of the Three Hammers by 10% per rank.",
    5, 2, ranks=2,
    effects={"ability_primalist_judgement_of_the_three_hammers_cooldown_pct": 0.10},
    connect=["mountain_avatar"],
    source="CoA: 'Reduces the cooldown of Mountain Fury by -20 sec and "
           "increases the duration by 4 sec.' Routed onto the ability this "
           "tree actually unlocks under the Mountain Fury name. Expressed as "
           "a percentage because cooldowns are counted in turns here, not "
           "seconds. Positive is the reduction direction. The duration half "
           "is dropped: ability_*_duration applies to dots and hots, and this "
           "is an activated buff window."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "mountain_avatar", "Mountain Avatar",
    "At full Earth's Rage you are the mountain - blocking a blow sheds stone "
    "that batters everything around you.",
    6, 0,
    proc={"trigger": "on_block", "chance": 100, "icd": 0,
          "splash_damage": {"pct": 0.60, "max_targets": 5,
                            "school": "nature"},
          "grant_resource": {"resource": "rage", "amount": 5}},
    source="CoA's description for this node in the export is a broken "
           "template reference ($d2), so there is no tooltip to port and it "
           "is built from its name and its position as the tank capstone. "
           "on_block is a live trigger this tree otherwise never uses, which "
           "makes the capstone reward the thing a Mountain King does more "
           "than anyone else: stand in front. splash_damage carries a school, "
           "so the shed stone is really Nature damage rather than cosmetic, "
           "and the Rage grant keeps it feeding the spec's resource loop. "
           "The 'at full Earth's Rage' framing is flavour and deliberately "
           "promises no number: nothing reads another effect's stack count, "
           "and a description that quoted one would be lying."))


def main():
    check = "--check" in sys.argv
    ids = [n["talent_id"] for n in TREE["nodes"]]
    assert len(ids) == len(set(ids)), "duplicate talent_id"
    names = [n["name"] for n in TREE["nodes"]]
    assert len(names) == len(set(names)), "duplicate node NAME"
    for n in TREE["nodes"]:
        for c in n["connected_to"]:
            assert c in ids, f"{n['talent_id']} connects to unknown {c}"
    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    unlocks = sum(1 for n in TREE["nodes"] if "unlock_ability" in n["effects"])
    print(f"Primalist Mountain King: {len(ids)} nodes, {procs} with procs, "
          f"{unlocks} unlocks")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
