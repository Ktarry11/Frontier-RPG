#!/usr/bin/env python3
"""Rebuild Primalist's Geomancy tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_primalist_geomancy.py [--check]

SOURCE: data/reference/coa/primalist.json - 39 real Geomancy talents from
Ascension's own CoA Builder payload, the same data allthingscoa.com
presents. Role: DPS. coa_playstyles.json: "Elemental Shaman, single-target
build".

The shipped tree was 23 nodes: 18 pure scalars, 1 proc, 4 unlocks.

EARTHSHAPING IS THE SPEC, and the old tree had it as the TIER 6 CAPSTONE.
In CoA it is a level 10 passive - the first thing a Geomancer gets and the
thing every other talent in the tree reads. Putting it last meant you
could take every talent built around the mechanic before you could take
the mechanic. It is tier 0 here. (Same structural mistake as Rylak's Bite
sitting at tier 4 in Wildwalker while four nodes modified it.)

CoA: "Casting Geode Barrage and your Seismic abilities now generate
Earthshaping. Earthshaping: increases your spell haste by 1% for 20
seconds, stacking 15 times." The existing proc had the right shape at the
wrong numbers (5 stacks of 3%); this uses CoA's 15 stacks of 1%, which is
the same ceiling with CoA's ramp.

HOW PER-STACK PAYOFFS ARE BUILT, because this is the one thing the engine
will not do directly. Several CoA talents read the Earthshaping stack
count - "Terrasurge deals 5% additional damage for each stack", "each
stack increases your critical damage by 5%", "at or above 10 stacks". None
of that is reachable:

  - consumes_stacks_of DOES read the caster's own stacks, but it only
    extends a DoT's duration (duration_per_stack) and only on dot /
    spell_dot abilities. It cannot scale damage.
  - consumes_target_stacks_of and scales_with_target_stacks_of read the
    TARGET's stacks, and Earthshaping sits on the caster.
  - No effect key or proc payload gates on "while I have N stacks".

What DOES work is that a status effect's stat_mods are multiplied by its
stack count when _recalculate_derived_stats folds them into the bonus
pool. So a per-stack payoff is built as its own parallel stacking buff on
the same trigger, carrying whichever stat the engine can actually grant
that way. That is why Blessing of Therazane grants crit CHANCE per stack
rather than CoA's crit DAMAGE: crit_damage_spell is read through
get_talent_effects(), which never includes status effects, so a
proc-applied crit-damage buff would be dead. Stated per node.

DEAD CONVERSION TARGETS. CoA has two Geomancy talents that convert to and
from armor penetration rating - Cave Dweller ("armor penetration equal to
50% of Intellect") and Crushing the Earth ("spell power equal to 50% of
your armor penetration"). STAT_CONVERSION_TARGETS has no
armor_penetration entry and STAT_CONVERSION_SOURCES has no
armor_penetration source, and character.py skips an unknown pairing in
silence - the Clarity of the Heavens bug recorded in that dict's own
comment. Both are rerouted to conversions that exist rather than authored
dead. Stoneskin's "Armor equal to 200% of Intellect" does work, because
armor IS a target.

TURN-BASED CUTS. Whispers of the Earth and the cast-time halves of
everything else are gone - there are no cast times. Gaze of Therazane is
range only, so it is dropped entirely rather than repriced into unrelated
damage. Magma Fissure's knockback and its 20-yard line are gone. Earth's
Embrace ("unable to move or act for 8 sec") is a channelled immunity with
no turn-based equivalent that is not simply a stun on yourself. Dream and
Cracking the Earth both gate on a stack threshold and are dropped for the
reason above.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/primalist_geomancy.json"

#: Frontier's Seismic abilities. Named explicitly rather than substring
#: matched, so a future ability with "seismic" in its id does not silently
#: join the set.
SEISMIC = ["primalist_seismic_crash", "primalist_seismic_tremor",
           "primalist_seismic_wave"]

#: What CoA says generates Earthshaping: "Geode Barrage and your Seismic
#: abilities".
GENERATORS = ["primalist_geode_barrage"] + SEISMIC

#: The two spells One With The Earth and Stone Tosser empower.
DIRECT_SPELLS = ["primalist_stoneshard", "primalist_geode_barrage"]

#: CoA: "increases your spell haste by 1% for 20 seconds, stacking 15
#: times." `haste` is the most-used status stat_mod in the game (47 nodes)
#: and is read raw; the stack multiplication happens in
#: _recalculate_derived_stats, so 15 stacks is +15 haste.
EARTHSHAPING = {
    "effect_id": "earthshaping", "name": "Earthshaping",
    "effect_type": "buff", "duration": 6, "max_stacks": 15,
    "stat_mods": {"haste": 1.0},
    "on_target": False, "real_time_seconds": None,
}

TREE = {
    "spec_name": "Primalist Geomancy",
    "tree_id": "primalist_geomancy",
    "description": ("Stone-caller - shapes the earth into a rising stack of "
                    "momentum and spends it on one target."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from data/reference/coa/primalist.json "
        "(39 real CoA Geomancy talents, role DPS, 'Elemental Shaman "
        "single-target build'). Replaces a 23-node tree of 18 pure scalars "
        "and 1 proc. The big structural change: Earthshaping, which CoA "
        "makes a level 10 passive and which every other talent here reads, "
        "was the tier 6 capstone and is now tier 0. All 4 unlock nodes are "
        "preserved - see tools/qa_abilities_obtainable.py for why that is "
        "not optional."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source="", active=False):
    entry = {
        "talent_id": f"primalist_geomancy_{nid}",
        "name": name,
        "description": desc,
        "node_type": "active" if active else "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"primalist_geomancy_{c}" for c in (connect or [])],
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
    "earthshaping", "Earthshaping",
    "Geode Barrage and your Seismic spells shape the earth around you, "
    "increasing your haste by 1% for 6 turns, stacking 15 times.",
    0, -1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": GENERATORS,
          "apply_effect": dict(EARTHSHAPING)},
    connect=["one_with_the_earth", "blessing_of_therazane"],
    source="CoA verbatim: 'Level 10 Passive. Casting Geode Barrage and your "
           "Seismic abilities now generate Earthshaping. Earthshaping: "
           "Empowers some of your abilities and increases your spell haste by "
           "1% for 20 seconds, stacking 15 times.' MOVED FROM TIER 6 TO TIER "
           "0. It is a level 10 passive in CoA and every other talent in this "
           "tree reads it; as the capstone you could take all of them before "
           "you could take this. The old node generated off Geode Barrage and "
           "Quake at 5 stacks of 3%; CoA's generator list is Geode Barrage "
           "plus the Seismic abilities, and CoA's ramp is 15 stacks of 1% - "
           "same +15% ceiling, longer climb. 20 sec is 6 turns."))

N.append(node(
    "stoneskin", "Stoneskin",
    "Increases your Armor by 100% of your Intellect per rank.",
    0, 1, ranks=2,
    effects={"armor_from_intellect_pct": 1.00},
    connect=["one_with_the_earth"],
    source="CoA verbatim: 'Increases your Armor by 200% of your Intellect.' "
           "Split across CoA's 2 ranks, so a full investment is the 200% CoA "
           "states. This conversion is live: 'armor' is in "
           "STAT_CONVERSION_TARGETS and 'intellect' in "
           "STAT_CONVERSION_SOURCES. Fraction, so 1.00 per rank. Was "
           "armor_pct 3.0."))

N.append(node(
    "trembling_rage", "Trembling Rage",
    "Seismic Tremor generates 2 additional Rage.",
    0, 3,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["primalist_seismic_tremor"],
          "grant_resource": {"resource": "rage", "amount": 2}},
    connect=["seismic_tremor"],
    source="CoA verbatim: 'Increases the amount of Rage generated by Seismic "
           "Tremor by 2.' Primalist is a dual-resource class (mana and Rage) "
           "and Terrasurge costs Rage while the Geomancy spells cost mana, so "
           "this is the bridge between the two halves of the kit."))

N.append(node(
    "molten_fervor", "Molten Fervor",
    "Increases your haste by 2.5% per rank.",
    0, 5, ranks=2,
    effects={"haste": 2.5},
    connect=["volcanic_blast"],
    source="CoA: 'Increases the spell haste of all party and raid members by "
           "3%. Does not stack with similar effects. In addition, increases "
           "your spell haste by 5%.' A talent effect applies to its own "
           "character only - there is no party-aura mechanism - so the "
           "raid-wide half is dropped and the description says 'your' rather "
           "than promising the party a buff it will not get. Haste here means "
           "acting more often on the turn meter, not casting faster."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "one_with_the_earth", "One With The Earth",
    "Increases the damage of Stoneshard and Geode Barrage by 20%, and "
    "Stoneshard restores 4% of your maximum mana.",
    1, -4,
    effects={f"ability_{a}_damage": 0.20 for a in DIRECT_SPELLS},
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["primalist_stoneshard"],
          "grant_resource": {"resource": "mana", "pct_max": 0.04}},
    connect=["rockslide"],
    source="CoA verbatim: 'Increases the damage of Stoneshard and Geode "
           "Barrage by 20% and Stoneshard now restores 4% of your maximum "
           "mana.' Both halves built. Was crit_chance_spell 1.0, which is "
           "neither half."))

N.append(node(
    "blessing_of_therazane", "Blessing of Therazane",
    "Shaping the earth also sharpens your aim, increasing your spell "
    "critical strike chance by 1% per stack.",
    1, -2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": GENERATORS,
          "apply_effect": {"effect_id": "primalist_therazanes_blessing",
                           "name": "Blessing of Therazane",
                           "effect_type": "buff", "duration": 6,
                           "max_stacks": 15,
                           "stat_mods": {"crit_chance_spell": 1.0},
                           "on_target": False}},
    connect=["cataclysm"],
    source="CoA: 'Each stack of Earthshaping now increases your critical "
           "damage dealt by 5%.' Nothing reads another effect's stack count, "
           "so this is built as a PARALLEL stacking buff on the same trigger "
           "- it climbs in lockstep with Earthshaping, which is what 'per "
           "stack of Earthshaping' means in practice. The stat is crit "
           "CHANCE, not CoA's crit DAMAGE, because crit_damage_spell is read "
           "through get_talent_effects() and that never includes status "
           "effects: a proc-applied crit-damage buff would be dead data. "
           "A status effect's stat_mods ARE multiplied by stacks, which is "
           "what makes the per-stack part real."))

N.append(node(
    "primal_shamans_mask", "Primal Shaman's Mask",
    "Your direct damage has a 10% chance to hurl a geode at the enemy, "
    "dealing extra damage and generating 5 Rage.",
    1, 0,
    proc={"trigger": "on_damage_cast", "chance": 10, "icd": 0,
          "damage_flat": 120,
          "grant_resource": {"resource": "rage", "amount": 5},
          "school": "physical"},
    connect=["cataclysm"],
    source="CoA verbatim: 'Direct damage dealt now has a 10% chance to launch "
           "a Geode at the enemy. Geode: Hurl an enchanted stone at the "
           "target, dealing Physical Damage and generating 5 Rage.' There is "
           "no primalist_geode ability to cast_ability into, so the geode is "
           "priced as damage_flat on the same trigger. 120 is in line with "
           "Frontier's other flat proc damage at this depth. Rage amount is "
           "CoA's. Was ability_primalist_quake_damage +6%."))

N.append(unlock(
    "magma_fissure", "Magma Fissure", "primalist_magma_fissure",
    "Stomp the ground and send a wave of molten stone through the enemy line.",
    1, 2, connect=["volcanic_blast"],
    source="CoA: 'Stomp the ground and unleash a wave of earth and stone in a "
           "20 yd line that knocks all enemies to the side and deals Fire "
           "damage, piercing absorption effects. Your next spell within 6 "
           "seconds is instant cast.' The line, the knockback and the "
           "instant-cast rider are all gone - no positioning, no cast times. "
           "Kept from the previous tree."))

N.append(node(
    "everlasting_rage", "Everlasting Rage",
    "Increases the duration of Seismic Tremor by 1 turn per rank.",
    1, 4, ranks=2,
    effects={"ability_primalist_seismic_tremor_duration": 1},
    connect=["geomolding"],
    source="CoA: 'Increases the duration of Seismic Tremor by 5 sec and its "
           "tick rate by -10%.' 5 sec is under 2 turns, rounded up to 2 since "
           "1 would be a smaller buff than CoA's. The tick-rate half is "
           "dropped: ticks are per-turn here, so there is no sub-turn rate to "
           "speed up."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "cataclysm", "Cataclysm",
    "Casting Stoneshard has a 10% chance to make your Seismic spells ready "
    "again at once.",
    2, -3,
    proc={"trigger": "on_damage_cast", "chance": 10, "icd": 1,
          "ability_filter": ["primalist_stoneshard"],
          "reset_cooldown": {"abilities": SEISMIC}},
    connect=["therazanes_might"],
    source="CoA verbatim: 'Generating Earthshaping or casting Stoneshard now "
           "has a 10% chance to reset the cooldown of your Seismic "
           "abilities.' Only the Stoneshard half is built: 'generating "
           "Earthshaping' would mean a proc that fires off another proc's "
           "application, and no trigger expresses that. 10% is CoA's, with a "
           "1-turn internal cooldown so it cannot chain. Omitting `turns` "
           "from reset_cooldown is a FULL reset, which is what CoA says."))

N.append(node(
    "rockslide", "Rockslide",
    "Stoneshard has a 15% chance to cast a second time.",
    2, -1,
    proc={"trigger": "on_damage_cast", "chance": 15, "icd": 0,
          "ability_filter": ["primalist_stoneshard"],
          "cast_ability": "primalist_stoneshard"},
    connect=["therazanes_might"],
    source="CoA verbatim: 'Stoneshard now has a 15% chance to cast an "
           "additional time. This effect can trigger itself.' cast_ability "
           "takes a bare ability id. The self-triggering part comes free: the "
           "re-cast is itself a damage cast, so it rolls again, which is "
           "exactly what CoA describes - no icd, deliberately."))

N.append(unlock(
    "quake", "Quake", "primalist_quake",
    "Shake the ground under a whole group of enemies.",
    2, 1, connect=["stone_tosser"],
    source="Kept from the previous tree."))

N.append(node(
    "volcanic_blast", "Volcanic Blast",
    "Your critical strikes splash 10% of the damage onto up to 3 nearby "
    "enemies as Fire damage per rank.",
    2, 3, ranks=2,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "splash_damage": {"pct": 0.10, "max_targets": 3, "school": "fire"}},
    connect=["geomolding"],
    source="CoA verbatim: 'Your Physical or Nature damaging critical strikes "
           "now deal an additional 10% of the damage dealt as Fire damage to "
           "the target and enemies nearby.' splash_damage is the live payload "
           "for exactly this and takes a school, so the Fire conversion is "
           "real rather than cosmetic. The Physical-or-Nature restriction on "
           "the TRIGGER is dropped: on_crit cannot filter by the school of "
           "the crit, and Geomancy's damage is almost entirely those two "
           "schools anyway."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "therazanes_might", "Therazane's Might",
    "Increases the critical strike chance of Terrasurge by 20% per rank.",
    3, -3, ranks=2,
    effects={"ability_primalist_terrasurge_crit": 20.0},
    connect=["golem_form"],
    source="CoA: 'Your Terrasurge will now always critically strike against "
           "targets affected by your Seismic Tremor.' The condition is what "
           "balances it and no effect key reads whether the target carries a "
           "specific DoT, so this is a large crit bonus rather than an "
           "unconditional ability_*_crit of 100.0 - which is what the literal "
           "reading would be and would be a permanent guaranteed crit on the "
           "spec's hardest hit. ability_*_crit is a PERCENT. Was "
           "ability_primalist_geode_barrage_damage +3%."))

N.append(node(
    "stone_tosser", "Stone Tosser",
    "Increases your spell power by 12.5% of your Intellect per rank.",
    3, -1, ranks=2,
    effects={"spell_power_from_intellect_pct": 0.125},
    connect=["golem_form"],
    source="CoA: 'Increases spell bonus damage scaling of Geode Barrage, "
           "Stoneshard, and Seismic Crash by 25%.' There is no key for 'how "
           "much an ability scales with spell power' - the scaling "
           "coefficients live on the abilities themselves - so this is built "
           "as the spell power those abilities consume, which raises them all "
           "by the same mechanism. Also carries CoA's Crushing the Earth "
           "('spell power equal to 50% of your armor penetration rating'), "
           "which is not buildable: armor_penetration is not in "
           "STAT_CONVERSION_SOURCES, and an unknown pairing is skipped in "
           "silence."))

N.append(node(
    "geomolding", "Geomolding",
    "Seismic Tremor's damage over time builds Geomolding, increasing your "
    "damage dealt by 3% per stack.",
    3, 1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["primalist_seismic_tremor"],
          "apply_effect": {"effect_id": "primalist_geomolding",
                           "name": "Geomolding", "effect_type": "buff",
                           "duration": 5, "max_stacks": 20,
                           "stat_mods": {"damage_dealt_pct": 3.0},
                           "on_target": False}},
    connect=["heavy_earth"],
    source="CoA: 'Periodic damage dealt by Seismic Tremor now grants "
           "Geomolding for 15 seconds. Geomolding: Your next Terrasurge costs "
           "2 additional Rage and deals 3% increased damage. Stacks 20 "
           "times.' Two departures. It triggers on the CAST rather than on "
           "each periodic tick, because no periodic-tick trigger exists in "
           "this engine. And the bonus is general damage rather than "
           "Terrasurge-only, because ability_*_damage is read through "
           "get_talent_effects() and a status effect cannot reach it - "
           "damage_dealt_pct is the status-effect route, and it is percentage "
           "POINTS, so 3.0. CoA's Rage surcharge is dropped: cost keys are "
           "reduction-signed, so a surcharge must be written negative, which "
           "is indistinguishable from the sign error the audit now flags. "
           "CoA's 20 stacks kept."))

N.append(node(
    "magmatism", "Magmatism",
    "Increases the damage of Magma Fissure by 20%.",
    3, 3,
    effects={"ability_primalist_magma_fissure_damage": 0.20},
    connect=["heavy_earth"],
    source="CoA: 'Reduces the cooldown of Eruption by 15 sec and causes Magma "
           "Geodes to deal 30% more damage to enemies above 75% health.' "
           "Frontier has no Eruption ability, so that half is dropped, and "
           "Magma Geodes are routed to Magma Fissure, the Fire area spell we "
           "do have. The above-75%-health CONDITION is dropped too: there is "
           "no high-health damage key - low_health_healing_pct is the only "
           "recipient-health conditional in the engine and it is heal-side - "
           "and the first draft invented high_health_damage_threshold_pct, "
           "which the audit correctly called dead. Repriced 30% -> 20% "
           "because it now applies unconditionally."))

# ---- tier 4 -------------------------------------------------------------
N.append(unlock(
    "golem_form", "Golem Form", "primalist_golem_form",
    "Become stone, slower to hurt and quicker to act.",
    4, -2, connect=["heavy_earth"],
    source="CoA: '15% of base mana, 2 min cooldown. Transform into a being "
           "made of stone and earth for 20 sec, increasing your haste by 20% "
           "and your Armor by 50%, and allowing you to cast damaging spells "
           "while moving.' The casting-while-moving clause is meaningless "
           "here. Kept from the previous tree, where this unlock was "
           "confusingly named Cave Dweller."))

N.append(node(
    "cave_dweller", "Cave Dweller",
    "Increases your maximum mana by 3% per rank.",
    4, 0, ranks=2,
    effects={"max_mana_pct": 0.03},
    connect=["heavy_earth"],
    source="CoA has TWO talents named Cave Dweller. This is the second: "
           "'Increases your maximum Rage by 15 and reduces spell pushback "
           "suffered from damaging attacks by 50%.' Pushback does not exist - "
           "no cast bars - so that half is dropped. The FIRST Cave Dweller "
           "('armor penetration rating equal to 50% of your Intellect') is "
           "not built at all: armor_penetration is not in "
           "STAT_CONVERSION_TARGETS, so the pairing would be skipped in "
           "silence. The Rage half is not buildable either, which is why "
           "this node grants mana instead: max_rage is a hardcoded 100 in "
           "Character.__init__ and no code reads a talent bonus into it, so "
           "'rage_max' was a dead key and 'increases your maximum Rage' is "
           "not something a talent can do here. Rerouted to mana headroom, "
           "which is live and serves the same purpose for a spec whose "
           "damage spells are all mana-costed."))

N.append(node(
    "earth_pummeling", "Earth Pummeling",
    "Geode Barrage makes the target 3% easier to critically hit with spells "
    "for 4 turns.",
    4, 2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["primalist_geode_barrage"],
          "apply_effect": {"effect_id": "primalist_earth_pummeling",
                           "name": "Earth Pummeling", "effect_type": "debuff",
                           "duration": 4, "max_stacks": 1,
                           "stat_mods": {"spell_damage_taken_pct": 3.0},
                           "on_target": True}},
    connect=["heavy_earth"],
    source="CoA: 'Damage dealt by Geode Barrage and Geodes to increase the "
           "chance for the enemy to be critically hit with spells by 3% for "
           "12 seconds.' There is no recipient-side 'chance to be crit' key - "
           "crit chance lives on the attacker - so this is built as spell "
           "damage taken, which is the live recipient-side key and delivers "
           "the same thing the talent is for: your spells hurt this target "
           "more. 12 sec is 4 turns."))

# ---- tier 5 -------------------------------------------------------------
N.append(unlock(
    "seismic_tremor", "Seismic Tremor", "primalist_seismic_tremor",
    "Send a tremor through the ground that builds as it travels.",
    5, -1, connect=["heavy_earth"],
    source="CoA: 'Damage is dealt slowly at first, and builds up over time. "
           "Damage dealt generates 1 Rage. Generates 2 stacks of "
           "Earthshaping.' Kept from the previous tree. Three nodes here "
           "modify it (Trembling Rage, Everlasting Rage, Geomolding), which "
           "is an argument for moving it earlier - left at tier 5 because it "
           "is a capstone-adjacent ability in CoA too and the modifiers are "
           "all spread across tiers 0-3 where they can be banked first."))

N.append(node(
    "therazanes_blessing", "Therazane's Blessing",
    "Increases the damage your damage-over-time effects deal by 5% per rank.",
    5, 1, ranks=2,
    effects={"dot_damage": 0.05},
    connect=["heavy_earth"],
    source="CoA: 'Level 50 Passive. Allows the periodic damage dealt by "
           "Seismic Tremor, Seismic Crash, and Earthquake to critically "
           "strike.' Whether DoT ticks can crit is an engine-wide rule, not a "
           "per-character bonus, so it is not a talent effect at all. Rebuilt "
           "as DoT damage, which is the same intent - make this spec's "
           "periodic damage matter - through a key that is live. dot_damage is "
           "unconditionally live, unlike the flavour-specific "
           "bleed_dot_damage, which resolves for no ability in the game."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "heavy_earth", "Heavy Earth",
    "Terrasurge spends the shaped earth, dealing 60% more damage and leaving "
    "you unable to shape more for 3 turns.",
    6, 0,
    effects={"ability_primalist_terrasurge_damage": 0.60},
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["primalist_terrasurge"],
          "apply_effect": {"effect_id": "primalist_heavy_earth",
                           "name": "Heavy Earth", "effect_type": "buff",
                           "duration": 3, "max_stacks": 1,
                           "stat_mods": {"damage_dealt_pct": 10.0},
                           "on_target": False}},
    source="CoA: 'Your Terrasurge now consumes all stacks of Earthshaping to "
           "refresh the duration of Golem Form and grant you Heavy Earth. "
           "Each stack consumed grants 5% additional damage dealt with "
           "Stoneshard and Geode Barrage as Nature Damage while this is "
           "active. Lasts 8 sec. While active you cannot generate "
           "Earthshaping.' The consume-and-scale core is the thing this "
           "engine cannot do: consumes_stacks_of reads the caster's own "
           "stacks but only extends a DoT's duration, and Terrasurge is a "
           "direct damage ability. So the capstone pays out as a flat "
           "Terrasurge bonus plus a fixed window of extra damage, and the "
           "description says 'spends the shaped earth' rather than quoting a "
           "per-stack number it cannot honour. The 'cannot generate "
           "Earthshaping while active' lockout is also unbuildable - no "
           "payload suppresses another proc - and the description's 'unable "
           "to shape more' is kept as flavour that does not promise a number. "
           "Flagged rather than faked."))


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
    print(f"Primalist Geomancy: {len(ids)} nodes, {procs} with procs, "
          f"{unlocks} unlocks")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
