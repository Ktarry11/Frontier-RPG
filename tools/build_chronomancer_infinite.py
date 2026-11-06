#!/usr/bin/env python3
"""Rebuild Chronomancer's Infinite tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_chronomancer_infinite.py [--check]

SOURCE: data/reference/coa_worksheets/chronomancer.md and
data/reference/coa/chronomancer.json - 38 real Infinite talents from
Ascension's own CoA Builder payload. Role: DPS.

Chronomancer measured 122 CoA talents against our 67, 42 of those pure
scalars. Infinite was 23 nodes with 7 procs.

THE CLASS-DEFINING TRANSLATION LOSS: CoA'S "PERIODIC DAMAGE DEALT" HOOK
DOES NOT EXIST HERE AND CANNOT CHEAPLY BE MADE TO.

Chronomancer's whole identity in CoA is that its damage-over-time ticks
are themselves a trigger. Seven talents across its three trees read it:
Anomaly Spikes ("Periodic damage dealt now has a 8% chance to launch an
Anomaly Spike"), Hourglass of Eternity, Null Orbs, Chaotic Time, Reverse
Engineering, Timeline Tether and the shared Impeccable Timing.

There is no tick trigger in this engine, and the reason is structural, not
an oversight. StatusEffectMixin.tick_status_effects (status_effects.py:914)
applies a DoT with a bare `self.take_damage(effect.tick_potency(), ...)` -
it runs on the TARGET and holds no reference to who cast the effect. The
method's own THREAT GAP note says so outright: "status effects only store
potency/duration/school, not a caster or engine handle". With no caster
there is nobody to fire a proc ON, so `on_periodic` cannot be added
without threading a (caster, engine) pair through every StatusEffect.

Every one of those talents is therefore re-pointed to `on_damage_cast`,
which fires when the Chronomancer casts a damaging spell. The class still
plays as a proc-heavy caster; what is lost is that the procs come off the
CAST rather than off the TICK, so a Chronomancer who applies dots and then
waits generates nothing. Flagged in each node's _source, and worth raising
with Kyle as a real engine gap rather than burying.

LONG DOTS ARE THIS SPEC'S POINT, and the engine rewards extending them
properly. abilities.py:2777: "per_turn is derived from the ability's OWN
base duration, not the talented one, so extending a DoT adds TICKS rather
than thinning the same total across more turns." So a talent that extends
a dot is a straight damage increase at full per-tick value - unlike
editing the ability's base duration, where per_turn = total/base_duration
and the total has to be raised alongside (which is what was done to
Chronomancer's six dots in the preceding commit). `dot_duration_pct` is
live at abilities.py:2766 as a FRACTION and lengthens every dot the caster
applies. Distorted Time and the capstone both use it.

ARCANE_SPELL_DAMAGE IS LIVE, AND I FIRST RECORDED THE OPPOSITE. Corrected
6 Nov 2026.

I grepped for the literal string "arcane_spell_damage", found nothing in
the engine, and wrote it up as dead data - in this docstring, in the
Chronomancer Infinite commit message and in
claude/engine_findings_2026_11_06.md. That was wrong.

`<school>_spell_damage` IS NEVER WRITTEN LITERALLY. It is built with an
f-string at abilities.py:1371 - `self._talent(caster,
f"{real}_spell_damage")` - inside _school_damage_bonus, resolved against
the school the ability actually deals that cast. So every school's key is
read, arcane included. Measured live over 1500 casts of Unmake (whose
damage_school is "arcane"): baseline 157.7, with +50%
arcane_spell_damage 236.6, ratio exactly 1.500.

A GREP FOR A LITERAL KEY NAME CANNOT SEE A DYNAMICALLY BUILT KEY, and this
project already knew that - Venomancer Fortitude's exposed_flesh_rage_pct
is recorded as "greps dead but works dynamically" and has asserts
protecting both halves for exactly this reason. I failed to apply the
lesson one class later. The reliable test is to spend the key on a live
character and measure, which is what settled it.

Time Means Nothing now uses arcane_spell_damage, which is what CoA's
"magic damage dealt" means on this class.

GIFT OF THE INFINITE DRAGONFLIGHT LOSES HALF ITS TEXT. CoA: "Increases
your spell damage by 40% of your Spirit and your spell hit rating by 3% of
your Spirit." The first half ports exactly - `spell_damage` is in
STAT_CONVERSION_TARGETS and `spirit` in STAT_CONVERSION_SOURCES. The
second does not: `hit_rating` is NOT a valid conversion target (this has
now cost seven nodes half their text across six classes), and
`hit_chance_spell` is set once in Character.__init__ and never fed from
bonuses, so it is dead as a talent key too. Dropped rather than faked.

MIND MELT USES FLAT ATTACK POWER, which is less of a departure than it
looks. A monster reads only eight status stat_mods (armor, attack_power,
damage_taken_pct, healing_taken_pct, magic/physical/spell_damage_taken_pct,
magic_resistance), and `attack_power` is FLAT - Monster.ability_power_bonus
is "Flat damage/healing swing from active buffs and debuffs". CoA's "-3%
primary attributes" has no home among those, but CoA itself uses flat AP
reduction on this class (Artificer's Erode Armaments: "reduce enemy attack
power by 208"), so a flat debuff is the house style rather than a fudge.

WHAT COULD NOT BE BUILT AT ALL:
  - Chromatic Shard "piercing immunities and resistances" - no key.
  - Chronological / Paradox / Warping Reality / Chaos Fusion - all four are
    cast-time or movement mechanics. There are no cast times and no
    positioning, so "your next X is instant" is inert. Repriced as
    cooldown or damage where the node still had a point, dropped where it
    did not.
  - Pure Chaos's time loop (lock yourself out of all spells but one,
    repeating every 1 sec) - no mechanic locks an ability set, and no proc
    repeats on a timer.
  - Slipstream's banish-and-replace - the ability exists and is ungated;
    the reposition half has no engine support.
  - Excruciating Discord ("Discordances used with Chronological are
    guaranteed to crit") - depends on Chronological, which is inert, and
    nothing grants a guaranteed crit on a specific ability.
  - Unearthed Power / Chromatic Shard stacks - nothing reads a stack count,
    so "6% per stack" cannot scale off anything.
  - Aeon Rend "strike again and incur no cooldown" - `extra_attack` is a
    boolean giving exactly one extra attack and cannot be scoped to an
    ability, so this builds as a reset_cooldown proc instead.
  - Infinite Guard (Temporal Resilience/Swiftness/Restoration) - those
    three spells do not exist in our Chronomancer book.

THIS TREE OWNS THREE GATED ABILITIES: anomaly_spike, destabilize_time and
incarnation_of_chaos. All three carry requires_talent and this is their
only unlock, so dropping a node makes them unobtainable forever.
Asserted in main().
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/chronomancer_infinite.json"

#: Abilities carrying requires_talent that ONLY this tree unlocks.
GATED = {"chronomancer_anomaly_spike", "chronomancer_destabilize_time",
         "chronomancer_incarnation_of_chaos"}

TREE = {
    "spec_name": "Chronomancer Infinite",
    "tree_id": "chronomancer_infinite",
    "description": ("Chaos out of order - a caster who rots a target over "
                    "a dozen turns and lets the decay do the killing."),
    "_source_note": (
        "Rebuilt 6 Nov 2026 from the 38 real CoA Infinite talents (role "
        "DPS). The spec's defining hook - 'periodic damage dealt has a "
        "chance to...' - has no engine equivalent: the DoT tick path "
        "(status_effects.py:914) runs on the target with no caster handle, "
        "so there is nothing to fire a proc on. All seven such talents are "
        "re-pointed to on_damage_cast and each says so. Long dots are the "
        "spec's point and the engine pays for extending them properly: "
        "talent extensions add TICKS at full per-turn value "
        "(abilities.py:2777), unlike raising an ability's base duration. "
        "arcane_spell_damage is LIVE - corrected 6 Nov 2026 after I wrongly grepped it as dead; <school>_spell_damage is built with an f-string at abilities.py:1371, so a literal grep cannot see it."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20,
                          "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"chronomancer_infinite_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"chronomancer_infinite_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


#: The re-point note, appended to every talent CoA hangs off a dot tick.
PERIODIC = (
    "CoA hangs this off PERIODIC DAMAGE, which does not exist as a trigger. "
    "status_effects.py:914 applies a dot with a bare self.take_damage() on "
    "the TARGET and holds no caster reference - its own THREAT GAP note "
    "says status effects store 'potency/duration/school, not a caster or "
    "engine handle' - so there is nobody to fire a proc on. Re-pointed to "
    "on_damage_cast: it fires on the Chronomancer's damaging casts instead "
    "of on their ticks, so a player who dots and waits gets nothing. This "
    "is the class's single biggest translation loss and it affects seven "
    "talents across all three trees.")

N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "gift_of_the_infinite_dragonflight", "Gift of the Infinite Dragonflight",
    "Increases your spell damage by 40% of your Spirit.",
    0, -4,
    effects={"spell_damage_from_spirit_pct": 0.40},
    connect=["temporal_decay"],
    source="CoA level 20 passive: 'Increases your spell damage by 40% of "
           "your Spirit and your spell hit rating by 3% of your Spirit.' "
           "The first half PORTS EXACTLY - spell_damage is in "
           "STAT_CONVERSION_TARGETS and spirit in STAT_CONVERSION_SOURCES. "
           "The second half is DROPPED, both ways: hit_rating is not a "
           "valid conversion target, and hit_chance_spell is set once in "
           "Character.__init__ (line 147) and never fed from bonuses, so a "
           "talent writing it is silent. Was a pure scalar on our side. "
           "A FRACTION."))

N.append(node(
    "temporal_decay", "Temporal Decay",
    "Increases the damage of your periodic effects by 12%.",
    0, -2,
    effects={"dot_damage": 0.12},
    connect=["warpstriker", "deconstruction"],
    source="Not a single CoA talent - the tree needs an entry point for the "
           "dot identity Kyle asked for, and dot_damage is the only global "
           "periodic key the engine reads (abilities.py:1601). Stands in "
           "for CoA's Infinite Horizon clause 'your Unmake and Timerend "
           "gain an additional 20% bonus spell scaling', which cannot be "
           "built as written (there is no per-ability spell-scaling key, "
           "only flat damage). A FRACTION."))

N.append(node(
    "warpstriker", "Warpstriker",
    "Reduces the mana cost of your spells by 5%.",
    0, 0,
    effects={"all_ability_cost_pct": 0.05},
    connect=["anomaly_spikes"],
    source="CoA over 2 ranks: 'Reduces the cost of your spells by -5% and "
           "the chance for your spells to be dispelled by 10%.' The cost "
           "half ports; all_ability_cost_pct is a FRACTION and POSITIVE "
           "MEANS A REDUCTION. The dispel-resistance half has no key and is "
           "dropped. Was a pure scalar on our side too, but of the wrong "
           "kind - this is at least the scalar CoA wrote."))

N.append(node(
    "deconstruction", "Deconstruction",
    "Increases the critical strike chance of Unmake by 5%.",
    0, 2,
    effects={"ability_chronomancer_unmake_crit": 5.0},
    connect=["mind_melt"],
    source="CoA over 2 ranks: 'Increases the critical strike chance of "
           "Unmake by 5%.' Ports exactly. Per-ability crit keys are in "
           "PERCENTAGE POINTS. Was a pure scalar on our side."))

N.append(node(
    "time_means_nothing", "Time Means Nothing",
    "Increases your Arcane damage by 6%.",
    0, 4,
    effects={"arcane_spell_damage": 0.06},
    connect=["chromatic_shard_mastery"],
    source="CoA: 'Increases your magic damage dealt by 3% and damage dealt "
           "by Chromatic Shard now increases the target's spell damage "
           "taken by 10% for 30 seconds.' THE MAGIC SCOPING NOW PORTS, "
           "corrected 6 Nov 2026: arcane_spell_damage is live, read via an "
           "f-string at abilities.py:1371 inside _school_damage_bonus and "
           "resolved against the school the ability actually deals. I had "
           "written this node as all_damage after grepping for the literal "
           "key and concluding it was dead - a grep cannot see a "
           "dynamically built key, and measuring it live gave a ratio of "
           "exactly 1.500. Chronomancer's whole kit is Arcane/Chromatic, so "
           "the scoped key reaches essentially everything this class casts "
           "while still being the honest translation of 'magic damage "
           "dealt'; doubled to 6% since it is now narrower than all_damage. "
           "The Chromatic Shard debuff half moves to its own node "
           "(Chromatic Shard Mastery) where it can carry a real proc. "
           "A FRACTION."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "anomaly_spikes", "Anomaly Spikes",
    "Your damaging spells have a 25% chance to launch an Anomaly Spike at "
    "your target.",
    1, -1,
    effects={"unlock_ability": "chronomancer_anomaly_spike"},
    proc={"trigger": "on_damage_cast", "chance": 25, "icd": 0,
          "cast_ability": "chronomancer_anomaly_spike"},
    connect=["erosion"],
    source="CoA over 2 ranks: 'Periodic damage dealt now has a 8% chance to "
           "launch an Anomaly Spike at your target.' LOAD-BEARING UNLOCK - "
           "chronomancer_anomaly_spike carries requires_talent and this is "
           "its only unlock node in the game; dropping it makes the ability "
           "unobtainable forever. " + PERIODIC + " The chance is raised "
           "from 8% to 25% to compensate: CoA's 8% fires off every tick of "
           "every dot on every target, which in a long fight is dozens of "
           "rolls, where on_damage_cast rolls once per cast. cast_ability "
           "takes a bare ability id and the ability must be in the caster's "
           "book, which the unlock guarantees."))

N.append(node(
    "chromatic_shard_mastery", "Chromatic Shard",
    "Increases the damage of Chromatic Shard by 20%, and your critical "
    "strikes increase the target's spell damage taken by 10% for 4 turns.",
    1, 3,
    effects={"ability_chronomancer_chromatic_shard_damage": 0.20},
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "temporal_fracture",
                           "name": "Temporal Fracture",
                           "effect_type": "debuff", "duration": 4,
                           "stat_mods": {"spell_damage_taken_pct": 10},
                           "dispel_type": "magic", "on_target": True}},
    connect=["hourglass_of_eternity"],
    source="CoA, Time Means Nothing's second clause: 'damage dealt by "
           "Chromatic Shard now increases the target's spell damage taken "
           "by 10% for 30 seconds.' Split onto its own node so it can carry "
           "a real proc. The trigger is on_crit rather than 'Chromatic "
           "Shard specifically' because there is no per-ability proc "
           "trigger; a crit is the closest thing to a meaningful cast and "
           "keeps the debuff from being permanent. spell_damage_taken_pct "
           "FLIPS: it is a FRACTION read raw as a talent effect "
           "(character.py:2753) but PERCENTAGE POINTS inside a status "
           "effect (monster.py:740 divides by 100), so 10 here is 10%. "
           "30 sec -> 4 turns at ~3 sec per turn. CoA's Chromatic Shard "
           "also pierces immunities and resistances, which has no key."))

N.append(node(
    "erosion", "Erosion",
    "Increases the damage of your Anomaly Spikes by 20% and your periodic "
    "damage by 8%.",
    1, 1,
    effects={"ability_chronomancer_anomaly_spike_damage": 0.20,
             "dot_damage": 0.08},
    connect=["distorted_time"],
    source="CoA's Erasion: 'Increases the chance to trigger Anomaly Spikes "
           "by 5% and their damage by 20%.' The damage half ports exactly. "
           "The trigger-chance half cannot: the chance lives on Anomaly "
           "Spikes' own proc dict and no effect key edits another node's "
           "proc chance. Replaced with dot_damage, which keeps the node "
           "about the same loop. Renamed from CoA's 'Erasion' only in that "
           "our data already had no such node - the name is CoA's. "
           "Both FRACTIONS."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "mind_melt", "Mind Melt",
    "Your damaging spells have a 30% chance to sap the target's strength, "
    "reducing the damage they deal for 5 turns.",
    2, 2,
    proc={"trigger": "on_damage_cast", "chance": 30, "icd": 0,
          "apply_effect": {"effect_id": "mind_melt_stack", "name": "Mind Melt",
                           "effect_type": "debuff", "duration": 5,
                           "stat_mods": {"attack_power": -25},
                           "max_stacks": 5, "dispel_type": "magic",
                           "on_target": True}},
    connect=["crown_of_power"],
    source="CoA: 'Damage dealt by Melt Reality now also reduces the "
           "target's primary attributes by -3% for 15 sec, stacking 5 "
           "times.' MAX_STACKS IS REAL AND IS KEPT (status effects stack "
           "natively), but nothing can READ the stack count, so the "
           "tier-6 End of Time clause that scales off it is built "
           "differently - see that node. '-3% primary attributes' has no "
           "home: a monster reads exactly eight status stat_mods (armor, "
           "attack_power, damage_taken_pct, healing_taken_pct, "
           "magic/physical/spell_damage_taken_pct, magic_resistance) and "
           "attack_power is FLAT (Monster.ability_power_bonus: 'Flat "
           "damage/healing swing from active buffs and debuffs'). -25 per "
           "stack, -125 at five. Flat AP reduction is CoA's own house style "
           "on this class - Artificer's Erode Armaments reduces enemy "
           "attack power by a flat 208. 15 sec -> 5 turns. The trigger is "
           "not Melt Reality specifically: no per-ability proc trigger."))

N.append(node(
    "hourglass_of_eternity", "Hourglass of Eternity",
    "Your damaging spells have a 20% chance to grant 25% haste for 2 turns.",
    2, 4,
    proc={"trigger": "on_damage_cast", "chance": 20, "icd": 2,
          "apply_effect": {"effect_id": "hourglass_of_eternity",
                           "name": "Hourglass of Eternity",
                           "effect_type": "buff", "duration": 2,
                           "stat_mods": {"haste": 25.0},
                           "dispel_type": None, "on_target": False}},
    connect=["infinity_crash"],
    source="CoA: 'Periodic damage dealt now has a 5% chance to grant you "
           "25% increased haste for 5 sec.' " + PERIODIC + " 5% -> 20% for "
           "the same reason as Anomaly Spikes (per-cast rolls are far rarer "
           "than per-tick ones), with a 2-turn internal cooldown so it "
           "cannot chain. 5 sec -> 2 turns. haste is in PERCENTAGE POINTS, "
           "so 25.0 is 25%."))

N.append(node(
    "distorted_time", "Distorted Time",
    "Increases the duration of your periodic effects by 20%.",
    2, 0,
    effects={"dot_duration_pct": 0.20},
    connect=["magic_erosion"],
    source="CoA: 'Reduces the cooldown of Timerend by -2 sec and increases "
           "the duration of Decomposition by 3 sec.' Generalised to every "
           "dot because dot_duration_pct is live (abilities.py:2766, a "
           "FRACTION) and is the one key that makes the spec's whole point "
           "pay off: abilities.py:2777 derives per-turn damage from the "
           "ability's OWN base duration, not the talented one, so an "
           "extension adds TICKS at full value rather than thinning the "
           "same total. This is a straight damage increase, and it is the "
           "mechanism Kyle's 'Chronomancer is a lot of DoTs' instruction "
           "actually wants - unlike editing a base duration, where "
           "per_turn = total/base_duration and the total has to move too. "
           "The Timerend cooldown half is dropped: our Timerend has no "
           "cooldown to reduce. Was a pure scalar on our side."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "destabilize_time", "Destabilize Time",
    "Teaches Destabilize Time, shaking a target loose from the present.",
    3, -2,
    effects={"unlock_ability": "chronomancer_destabilize_time"},
    connect=["black_hole"],
    source="CoA: 'Reduces enemy casting speed by -10% for 20 seconds, "
           "increasing by -10% every time they cast. Gaining stacks does "
           "not extend the duration.' LOAD-BEARING UNLOCK - "
           "chronomancer_destabilize_time carries requires_talent and this "
           "is its only unlock node. The talent itself is the unlock and "
           "nothing more: there is no caster-side speed debuff key (that "
           "gap has now cost nodes on four classes), and nothing escalates "
           "a debuff when the TARGET acts. The ability already exists in "
           "our data as a debuff and is left as authored."))

N.append(node(
    "magic_erosion", "Magic Erosion",
    "Increases the damage of Decomposition by 15%, and your critical "
    "strikes leave the target 4% easier to hit with spells for 6 turns.",
    3, 0,
    effects={"ability_chronomancer_decomposition_damage": 0.15},
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "magic_erosion", "name": "Magic Erosion",
                           "effect_type": "debuff", "duration": 6,
                           "stat_mods": {"magic_damage_taken_pct": 4},
                           "dispel_type": "magic", "on_target": True}},
    connect=["null_orbs"],
    source="CoA: 'Your Decomposition now deals 10% more damage and applies "
           "Magic Erosion to the target, increasing attackers chance to hit "
           "the target with spells by 3% for 30 seconds.' The damage half "
           "ports (raised to 15% to carry the node alone). The hit-chance "
           "half cannot: there is no recipient-side 'chance to be hit' key "
           "anywhere, so it is repriced as magic_damage_taken_pct, which is "
           "the same direction - more of the Chronomancer's damage lands on "
           "this target. That key is PERCENTAGE POINTS inside a status "
           "effect, so 4 is 4%. 30 sec -> 6 turns. Was a pure scalar on our "
           "side."))

N.append(node(
    "infinity_crash", "Infinity Crash",
    "Increases your spell critical damage by 50%.",
    3, 4,
    effects={"crit_damage_spell": 0.50},
    connect=["chaotic_time"],
    source="CoA: 'Increases the critical damage of Discordance and "
           "Chromatic Shard by 50%.' The two-ability scoping is dropped "
           "because per-ability crit-damage keys exist but would halve the "
           "node's reach for no gain on a spec that casts little else; "
           "crit_damage_spell is the honest global version. A FRACTION "
           "(crit_damage_* keys are fractions, unlike crit_chance_*, which "
           "are percentage points - the two sit side by side in the same "
           "data and read opposite ways). Was a pure scalar on our side."))

N.append(node(
    "crown_of_power", "Crown of Power",
    "Increases the damage of Melt Reality by 25%.",
    3, 2,
    effects={"ability_chronomancer_melt_reality_damage": 0.25},
    connect=["incarnation_of_chaos"],
    source="CoA: 'Increases the tick rate of Melt Reality by 25%.' Tick "
           "rate has no meaning in a turn-based engine - a dot ticks once "
           "per turn, full stop - and raising its duration instead would "
           "stretch a 10-turn dot past most fights. Repriced as damage, "
           "which is what a faster tick rate amounts to in CoA. Melt "
           "Reality is the spec's long dot: 'every 3 sec for 30 sec' is "
           "exactly 10 turns here. Was a pure scalar on our side. "
           "A FRACTION."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "black_hole", "Black Hole",
    "Increases the damage of your periodic effects by 15%.",
    4, -2,
    effects={"dot_damage": 0.15},
    connect=["timelost_power"],
    source="CoA: 'Increases the damage of Chromatic Shard, Melt Reality and "
           "Unmake by 15% against slowed enemies.' The conditional is "
           "dropped: nothing reads whether a target is slowed (no payload "
           "or effect key inspects a target's debuffs), and a condition "
           "that silently never fires is worse than no condition. Kept at "
           "15% against the spec's dots instead, which covers Melt Reality "
           "and Decomposition. Was a pure scalar on our side. A FRACTION."))

N.append(node(
    "null_orbs", "Null Orbs",
    "Your critical strikes have a 35% chance to grant Null Orbs, increasing "
    "your spell critical damage by 40% for 3 turns.",
    4, 0,
    proc={"trigger": "on_crit", "chance": 35, "icd": 1,
          "apply_effect": {"effect_id": "null_orbs", "name": "Null Orbs",
                           "effect_type": "buff", "duration": 3,
                           "stat_mods": {"crit_damage_spell": 40},
                           "dispel_type": None, "on_target": False}},
    connect=["eternity"],
    source="CoA: 'Periodic critical damage dealt now has a 20% chance to "
           "grant Null Orbs for 8 seconds. Null Orbs increases the critical "
           "damage of Chromatic Shard and Anomaly Spikes based on your "
           "spell critical strike rating.' " + PERIODIC + " on_crit is the "
           "closest live trigger and keeps CoA's 'critical' half intact. "
           "The 'based on your crit rating' scaling is dropped - no stat "
           "feeds a status effect's own magnitude. 8 sec -> 3 turns. "
           "CAREFUL: crit_damage_spell is a FRACTION as a talent effect but "
           "this is a STATUS EFFECT stat_mod, where the same key is read in "
           "PERCENTAGE POINTS - hence 40, not 0.40. Authoring 0.40 here "
           "would have delivered 0.4%. Was a pure scalar on our side."))

N.append(node(
    "incarnation_of_chaos", "Incarnation of Chaos",
    "Teaches Incarnation of Chaos, becoming chaos itself for a short time.",
    4, 2,
    effects={"unlock_ability": "chronomancer_incarnation_of_chaos"},
    connect=["chaotic_time"],
    source="CoA: 'Transform into an Incarnate of Chaos, instantly resetting "
           "the cooldown of Chromatic Shard and causing your next cast to "
           "not incur a cooldown. In addition, your damage dealt is "
           "increased by 15% for 15 seconds.' LOAD-BEARING UNLOCK - "
           "chronomancer_incarnation_of_chaos carries requires_talent and "
           "this is its only unlock node. The ability itself already "
           "carries the damage buff; the cooldown-reset clauses live on the "
           "ability, not here. CoA's Chaos Fusion and Pure Chaos both key "
           "off this being active - Chaos Fusion is a movement mechanic "
           "(inert: no positioning) and Pure Chaos locks the player out of "
           "all spells but one on a 1-second repeat (no mechanic locks an "
           "ability set, and no proc repeats on a timer), so neither is "
           "built."))

N.append(node(
    "chaotic_time", "Chaotic Time",
    "Your damaging spells have a 25% chance to reduce the cooldown of "
    "Incarnation of Chaos by 2 turns.",
    4, 4,
    proc={"trigger": "on_damage_cast", "chance": 25, "icd": 1,
          "reset_cooldown": {"abilities": ["chronomancer_incarnation_of_chaos"],
                             "turns": 2}},
    connect=["end_of_time"],
    source="CoA: 'While Incarnation of Chaos is active, your Melt Reality "
           "deals 30% increased damage and replicates an additional 20%. In "
           "addition, periodic damage dealt now reduces the cooldown of "
           "Incarnation of Chaos by -1 sec.' The cooldown clause is the "
           "buildable half and it is built: reset_cooldown with an "
           "{abilities, turns} dict shaves turns rather than fully "
           "resetting (a bare list would reset outright). " + PERIODIC + " "
           "The 'while Incarnation is active' conditional on the damage "
           "half is dropped - no effect key reads whether another effect is "
           "live - and the replication clause has no mechanism (no payload "
           "copies damage to other targets as a percentage). Was a pure "
           "scalar on our side."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "timelost_power", "Timelost Power",
    "Increases the damage of Discordance by 25% and your spell damage by 4%.",
    5, -1,
    effects={"ability_chronomancer_discordance_damage": 0.25,
             "spell_damage": 0.04},
    connect=["infinite_horizon"],
    source="CoA: 'Your Discordance now strikes 3 additional enemies.' "
           "Nothing adds targets to an ability - no effect key and no proc "
           "payload touches an ability's target count - so the node is "
           "repriced as damage on the same ability plus a small global, "
           "which is what three extra targets amounts to on a spec that "
           "casts Discordance as filler. Was a pure scalar on our side. "
           "Both FRACTIONS."))

N.append(node(
    "eternity", "Eternity",
    "While a target is rooted by your Clasp of Infinity, your damage "
    "against them is increased. Increases all damage you deal by 5%.",
    5, 1,
    effects={"all_damage": 0.05},
    connect=["infinite_keeper"])
    )
N[-1]["_source"] = (
    "CoA: 'Your Clasp of Infinity now increases your damage dealt to the "
    "target by 15%.' The conditional cannot be built - nothing reads a "
    "target's debuffs, so 'to the target' and 'while rooted' are both "
    "unreachable - so it lands as a flat 5% all_damage, priced down from "
    "15% because it is now unconditional. The description keeps the "
    "flavour sentence but states the real mechanic second, so the tooltip "
    "does not promise a condition the engine will not honour. A FRACTION.")

N.append(node(
    "end_of_time", "End of Time",
    "Increases the damage of your periodic effects by 18% and your spell "
    "critical strike chance by 4%.",
    5, 3,
    effects={"dot_damage": 0.18, "crit_chance_spell": 4.0},
    connect=["infinite_keeper"],
    source="CoA has TWO talents called End of Time in this tree. The "
           "tier-5 one: 'Mind Melt now also increases the target's periodic "
           "damage taken from you by 6% per stack.' Per-stack scaling is "
           "unbuildable - nothing reads a stack count anywhere in the "
           "engine - and there is no periodic-specific damage-taken key "
           "either, so both halves fail. Repriced to the caster side as "
           "dot_damage plus crit, which keeps the node a dot payoff. (The "
           "other End of Time, 'at the end of Clasp of Infinity you launch "
           "an Anomaly Spike at affected enemies', needs an on-expiry "
           "trigger, which does not exist.) dot_damage is a FRACTION; "
           "crit_chance_spell is PERCENTAGE POINTS. The two sit in the same "
           "dict and read opposite ways."))

N.append(node(
    "infinite_horizon", "Infinite Horizon",
    "Increases your spell damage by 8%.",
    5, -3,
    effects={"spell_damage": 0.08},
    connect=["infinite_keeper"],
    source="CoA: 'Increases the all damage dealt by party and raid members "
           "by 3%. Does not stack with similar effects. In addition, your "
           "Unmake and Timerend gain an additional 20% bonus spell "
           "scaling.' THE PARTY HALF CANNOT BE BUILT FROM A TALENT - a "
           "talent effect never reaches an ally; only a party-targeted "
           "ABILITY does (abilities.py:2064 resolves target_type 'party' to "
           "all living allies). Guardian's auras were converted to party "
           "abilities for exactly this reason, but Chronomancer has no aura "
           "ability to hang this on, so it stays selfish and the "
           "description does not claim otherwise. The spell-scaling half "
           "has no key (only flat damage keys exist). A FRACTION."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "infinite_keeper", "Infinite Keeper",
    "Increases the damage of your periodic effects by 45%. Your critical "
    "strikes have a 40% chance to launch an Anomaly Spike.",
    6, 0,
    effects={"dot_damage": 0.45},
    proc={"trigger": "on_crit", "chance": 40, "icd": 0,
          "cast_ability": "chronomancer_anomaly_spike"},
    source="CoA: 'Using Unmake on an enemy affected by your Timerend now "
           "causes the enemy to erupt in a vortex of sand, dealing "
           "Chromatic Damage every 1 sec to up to 8 enemies for 6 sec in an "
           "8 yd radius.' The combo condition is unbuildable twice over - "
           "nothing reads a target's debuffs, and there is no per-ability "
           "proc trigger - and the 8-yard radius has no positioning to "
           "stand on. Rebuilt as the capstone the spec's own tree has been "
           "building toward. ORIGINALLY THIS CARRIED +30% DOT DURATION TOO, "
           "and it was removed on 6 Nov 2026 after fight length was "
           "measured: stacked with Distorted Time's 20% it took Melt "
           "Reality to 9 turns, and a 9-turn dot delivers about a third of "
           "its damage on trash (2-3 turns) and two thirds on a boss (5-6). "
           "ONE duration node per tree is the rule now - Distorted Time "
           "keeps it, this trades its share for damage, so a fully "
           "talented Melt Reality lands at 7 turns rather than 9. "
           "dot_damage reaches the same place without pushing the dot past "
           "the window it is played in. A FRACTION."))


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
    # The two dot keys are this spec's whole identity and read opposite ways
    # from their status-effect namesakes; assert the fractions stayed
    # fractions so a later edit cannot quietly ship 2000% duration.
    for n in TREE["nodes"]:
        for k in ("dot_damage", "dot_duration_pct"):
            v = (n.get("effects") or {}).get(k)
            if v is not None:
                assert 0 < v < 1, (
                    f"{n['talent_id']}.{k}={v} - these are FRACTIONS as "
                    f"talent effects (0.20 = +20%); a value >= 1 means "
                    f"someone authored percentage points")
    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Chronomancer Infinite: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points, {len(GATED)} load-bearing unlocks")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
