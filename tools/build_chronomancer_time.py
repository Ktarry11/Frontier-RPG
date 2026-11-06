#!/usr/bin/env python3
"""Rebuild Chronomancer's Time tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_chronomancer_time.py [--check]

SOURCE: data/reference/coa_worksheets/chronomancer.md and
data/reference/coa/chronomancer.json - 38 real Time talents from
Ascension's own CoA Builder payload. Role: HEALER.

Time was 23 nodes with 5 procs.

THIS TREE PROMPTED AN ENGINE FIX. Building it meant authoring HoT duration
talents, and measuring one first showed the HoT branch of
Ability._apply_effect divided its fixed total by the TALENTED duration -
so extending a heal-over-time spread the same healing thinner. Accelerated
Recovery went from 7 turns x 29 (203 total) to 11 turns x 18 (198) for a
+4-turn talent: less healing, slower, for points spent. The DoT branch
twenty lines above had been fixed long ago and even documented the bug.
Fixed 6 Nov 2026, along with a new `hot_duration_pct` global key so a
healer tree can extend everything it applies the way a DPS tree can. Eight
talents across seven other trees were shipping inverted.

That matters here because CoA's Time tree is full of them - Eternal, Time
Beacon, Mark of Order, Chronicler all extend heals - and every one would
have been a trap.

THE PERIODIC-TICK TRIGGER STILL DOES NOT EXIST, as in Infinite: a dot or
hot tick runs on the recipient with no caster handle
(status_effects.py:914), so Timeline Tether's "your periodic damage and
healing reduces the cooldown of Fortify Timeline" is re-pointed to
on_heal_cast.

ON_HEAL_CAST PASSES THE CASTER, NEVER THE HEALED ALLY, and a HoT fires no
on_heal_cast at all (it goes through the dot/hot branch, which appends no
heal event). Both are recorded in the project's own talent palette notes
and both bite this tree hard: every CoA talent of the shape "healing done
by X now applies Y to the target" - Mark of Order, Aeon of Oblivion's
damage buff, Constant Recovery - cannot put an effect on the ally. The
only payload that reaches an ally is a smart heal (`smart_heal_pct`, or
`leech_pct` with `smart: true`), which heals the worst-off ally but cannot
buff them. Those talents are therefore turned around to the caster side,
and each node says so rather than promising an ally buff that never lands.

THE AEONS ARE THREE GATED ABILITIES AND THEY STAY THAT WAY. CoA's Aeon of
Protection / Renewal / Oblivion each reshape Epoch and "share a cooldown
with other Aeon spells". There is no shared-cooldown mechanism, but the
abilities already exist in our data with their own effects, so the three
nodes are pure unlocks. Dropping any of them makes that Aeon unobtainable
forever. Fabric of Time is the fourth gated ability in this tree.

SHIELD OF THE AGES IS THE UNIT-CONVENTION TRAP IN MINIATURE and is kept
deliberately as a worked example. Its one stat_mods dict holds two keys
that read in DIFFERENT units:
  damage_taken_pct   - RAW on both sides (character.py:2697 adds the status
                       mod with no division), so -0.03 is -3%
  healing_taken_pct  - PERCENTAGE POINTS in a status effect
                       (character.py:2904 divides by 100), so 5 is +5%
Authoring 0.05 for the second would have delivered 0.05%; authoring -3 for
the first would have delivered -300% damage taken, i.e. healing the player
on every hit. main() asserts both.

WHAT COULD NOT BE BUILT AT ALL:
  - Endless Sands, Bronze Timeways, Wonders of Time, Converge the Infinite
    - all four are cast-time stack mechanics. There are no cast times, and
    nothing reads a stack count, so they fail twice over.
  - Ripple's channel and Eternity Warper's per-Aeon channel variants -
    there is no channelling, and nothing reads which Aeon is active.
  - Timeblender's extra charge - there is no charge system.
  - Ideal Time / Excruciating Discord ("every 30 sec your next ability is
    guaranteed to crit") - no cast counter and no guaranteed-crit key.
  - Time Skip (Roll Back removes 1 more effect) and Continuum Restoration's
    undispellable dispel - nothing parameterises dispel counts or strength.
  - Epic Recovery (Epoch also lands on 5 allies affected by Accelerated
    Recovery) - a talent cannot add targets to an ability, and nothing
    reads who carries a given effect.
  - The Vast Infinite's shared-damage pool - no accumulator exists; this
    killed Puppeteer's Threads and Oathkeeper too. The ability itself is
    ungated and untouched.
  - Nozdormu's / Titan's Gaze - both modify Time Out!'s channel.
  - Through The Aeons (+100% mana regen from Spirit) - mp5 is an
    item-budget stat only and no talent key feeds mana regeneration.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/chronomancer_time.json"

#: Abilities carrying requires_talent that ONLY this tree unlocks.
GATED = {"chronomancer_aeon_of_protection", "chronomancer_aeon_of_renewal",
         "chronomancer_aeon_of_oblivion", "chronomancer_fabric_of_time"}

TREE = {
    "spec_name": "Chronomancer Time",
    "tree_id": "chronomancer_time",
    "description": ("Undoing the wound rather than closing it - a healer "
                    "whose mending runs long and whose Aeons reshape it."),
    "_source_note": (
        "Rebuilt 6 Nov 2026 from the 38 real CoA Time talents (role "
        "HEALER). Building it uncovered and prompted a fix to the HoT "
        "duration bug: the HoT branch divided a fixed total by the TALENTED "
        "duration, so every heal-over-time extension talent in the game was "
        "making healers worse. CoA's Time tree is full of them, so they are "
        "the backbone here and now pay properly, through the new "
        "hot_duration_pct key and the per-ability _duration keys. "
        "on_heal_cast passes the CASTER and never the healed ally, so every "
        "CoA talent of the form 'healing done by X applies Y to the target' "
        "is turned around to the caster side. The four Aeon/Fabric unlocks "
        "are load-bearing and asserted."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20,
                          "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"chronomancer_time_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"chronomancer_time_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


#: Appended wherever CoA keys off a heal landing ON an ally.
ALLY = (
    "CoA puts this effect ON THE HEALED ALLY, which no talent can do. "
    "on_heal_cast passes the CASTER, not the recipient (recorded in the "
    "project's talent palette notes and verified), and the only payload "
    "that reaches an ally at all is a smart heal, which heals the worst-off "
    "ally but cannot buff them. Turned around to the caster side so the "
    "node does something real; the tooltip states the caster-side version "
    "rather than promising an ally buff that never lands.")

N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "sands_of_life", "Sands of Life",
    "Increases your healing power by 25% of your Spirit.",
    0, -4,
    effects={"healing_power_from_spirit_pct": 0.25},
    connect=["patient_mending"],
    source="CoA over 2 ranks: 'Increases your healing power by 25% of your "
           "Spirit.' PORTS EXACTLY - healing_power is in "
           "STAT_CONVERSION_TARGETS and spirit in STAT_CONVERSION_SOURCES. "
           "Was a pure scalar on our side. A FRACTION."))

N.append(node(
    "patient_mending", "Patient Mending",
    "Increases the duration of your heal over time effects by 20%.",
    0, -2,
    effects={"hot_duration_pct": 0.20},
    connect=["time_wizard", "timeless"],
    source="Stands in for CoA's shared-tree Eternal ('Increases the duration "
           "of your Accelerated Recovery by 6 sec and Decomposition by 3 "
           "sec') as this tree's entry point, because duration is what the "
           "spec is about and because hot_duration_pct did not exist until "
           "6 Nov 2026. It is the healing companion to dot_duration_pct, "
           "and it only became worth authoring once the HoT branch stopped "
           "dividing the total by the talented duration - before that fix "
           "this node would have made a healer strictly worse. Per-turn "
           "healing now derives from the ability's own base duration, so "
           "+20% duration is +20% total healing at full per-tick value. "
           "A FRACTION."))

N.append(node(
    "time_wizard", "Time Wizard",
    "Increases the critical strike chance of Reverse Wound, Epoch and "
    "Correct the Mistake by 8%.",
    0, 0,
    effects={"ability_chronomancer_reverse_wound_crit": 8.0,
             "ability_chronomancer_epoch_crit": 8.0,
             "ability_chronomancer_correct_the_mistake_crit": 8.0},
    connect=["fabric_of_time"],
    source="CoA over 2 ranks: 'Increases the critical strike chance of your "
           "Reverse Wound, Epoch, and Correct the Mistake by 8%.' PORTS "
           "EXACTLY, all three abilities, using per-ability crit keys rather "
           "than a global so the node stays the one CoA wrote. Per-ability "
           "crit keys are in PERCENTAGE POINTS. Was a pure scalar on our "
           "side. NOTE for anyone reading this later: heals CAN crit, but "
           "HoTs cannot - 'heals and DoTs never roll crit' in the palette "
           "notes refers to periodic ticks, so these three (two direct "
           "heals and a party heal) are the right targets and Accelerated "
           "Recovery would not have been."))

N.append(node(
    "timeless", "Timeless",
    "Reduces the mana cost of your healing spells by 10%.",
    0, 2,
    effects={"heal_cost_pct": 0.10},
    connect=["keep_accelerating"],
    source="CoA: 'While Endless Sands is active, the mana costs of your "
           "spells and abilities is reduced by -3% per stack.' Both "
           "conditions fail - nothing reads whether another effect is "
           "active, and nothing reads a stack count - so this becomes the "
           "unconditional version at a flat 10%. heal_cost_pct is live "
           "(abilities.py:1226), is a FRACTION, and POSITIVE MEANS A "
           "REDUCTION. Was a pure scalar on our side."))

N.append(node(
    "carbon_dating", "Carbon Dating",
    "Increases the healing of Epoch by 20%.",
    0, 4,
    effects={"ability_chronomancer_epoch_healing": 0.20},
    connect=["cadence_of_time"],
    source="CoA: 'Each stack of Sands of Time now also increases the healing "
           "of your Epoch by 10%.' The per-stack scaling is unbuildable "
           "(nothing reads a stack count), so it lands as a flat 20% on the "
           "same ability - which is what CoA's two stacks amount to. Was a "
           "pure scalar on our side. A FRACTION."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "fabric_of_time", "Fabric of Time",
    "Teaches Fabric of Time, reaching back to undo an ally's wound.",
    1, 0,
    effects={"unlock_ability": "chronomancer_fabric_of_time"},
    connect=["aeon_of_protection", "aeon_of_renewal"],
    source="CoA: 'Alter the fabric of time, healing an ally. Your next Aeon "
           "used within 8 sec will trigger with no cooldown or cost.' "
           "LOAD-BEARING UNLOCK - chronomancer_fabric_of_time carries "
           "requires_talent and this is its only unlock node; dropping it "
           "makes the ability unobtainable forever. The 'next Aeon is free' "
           "clause lives on the ability, not here; nothing waives a "
           "resource cost from a talent."))

N.append(node(
    "keep_accelerating", "Keep Accelerating",
    "Your healing spells have a 35% chance to also mend your most wounded "
    "ally for 25% of the amount healed.",
    1, 2,
    proc={"trigger": "on_heal_cast", "chance": 35, "icd": 0,
          "smart_heal_pct": 25},
    connect=["cadence_of_time"],
    source="CoA: 'Your Accelerated Recovery now also applies to the "
           "lowest-health nearby target.' A talent cannot add a target to "
           "an ability, and a HoT fires no on_heal_cast at all (it goes "
           "through the dot/hot branch, which appends no heal event), so "
           "keying off Accelerated Recovery specifically is doubly "
           "impossible. Built instead as a smart heal off the spec's direct "
           "heals: smart_heal_pct is one of only three payloads that READ "
           "the triggering amount, and it picks the worst-off ally, which is "
           "exactly CoA's 'lowest-health nearby target'. The ability it "
           "keys off changed; the behaviour it produces did not. Was a pure "
           "scalar on our side."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "aeon_of_protection", "Aeon of Protection",
    "Teaches Aeon of Protection, turning Epoch into a shield against what "
    "is coming.",
    2, -2,
    effects={"unlock_ability": "chronomancer_aeon_of_protection"},
    connect=["shield_of_the_ages"],
    source="CoA: 'Increases Epoch's cast time by 15%, healing done by 15%, "
           "and causes it to apply a damage absorption shield equal to 30% "
           "of the amount healed for 8 sec. Shares a cooldown with other "
           "Aeon spells.' LOAD-BEARING UNLOCK. There is no shared-cooldown "
           "mechanism and no cast times, but the ability already exists in "
           "our data carrying its own effects, so this node is the unlock "
           "and nothing else - which is the right shape for a mode-switch "
           "talent anyway."))

N.append(node(
    "aeon_of_renewal", "Aeon of Renewal",
    "Teaches Aeon of Renewal, trading Epoch's burst for healing that keeps "
    "arriving.",
    2, 0,
    effects={"unlock_ability": "chronomancer_aeon_of_renewal"},
    connect=["time_beacon"],
    source="CoA: 'Reduces Epoch's healing by 30%, but causes it to heal for "
           "an additional 50% of the amount healed over 3 sec. Healing done "
           "by this ability cannot critically hit.' LOAD-BEARING UNLOCK. "
           "The cannot-crit clause is free here: HoT ticks never roll crit "
           "in this engine regardless, so CoA's own restriction is already "
           "the behaviour."))

N.append(node(
    "cadence_of_time", "Cadence of Time",
    "Your critical heals increase your healing done by 8% for 5 turns, "
    "stacking up to 5 times.",
    2, 2,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "cadence_of_time",
                           "name": "Cadence of Time",
                           "effect_type": "buff", "duration": 5,
                           "stat_mods": {"healing_power_pct": 8},
                           "max_stacks": 5, "dispel_type": None,
                           "on_target": False}},
    connect=["aeon_of_oblivion"],
    source="CoA: 'Your critical strikes with Epoch now grant Cadence of "
           "Time, increasing the healing of Ripple by 10% for 15 seconds. "
           "Stacks 5 times.' The two ability scopings both go - there is no "
           "per-ability proc trigger, and a status effect cannot carry a "
           "per-ability healing key - so it becomes a general healing buff "
           "off critical heals, keeping CoA's 5 stacks and its 'crit feeds "
           "the next heal' loop. max_stacks is real; nothing can READ the "
           "count, but the effect genuinely stacks. CAREFUL: "
           "healing_power_pct is PERCENTAGE POINTS (character.py:1295 "
           "divides by 100), so 8 is 8% - and it sits twelve lines from "
           "max_mana_pct, which is read raw as a fraction. 15 sec -> 5 "
           "turns. Was a pure scalar on our side."))

N.append(node(
    "a_ripple_in_time", "A Ripple In Time",
    "Your critical heals have a 40% chance to reduce the cooldown of Ripple "
    "by 2 turns.",
    2, 4,
    proc={"trigger": "on_crit", "chance": 40, "icd": 0,
          "reset_cooldown": {"abilities": ["chronomancer_ripple"],
                             "turns": 2}},
    connect=["aeon_of_oblivion"],
    source="CoA: 'Your damaging and healing critical strikes now reduce the "
           "remaining cooldown of Ripple by 1 sec.' PORTS ALMOST EXACTLY - "
           "on_crit covers both damaging and healing crits, and "
           "reset_cooldown with an {abilities, turns} dict shaves turns "
           "rather than resetting outright (a bare list resets fully). "
           "1 sec -> 2 turns because a 1-second shave on a 30-second "
           "cooldown is proportionally about two turns off ten, and a "
           "sub-turn reduction would round to nothing."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "time_beacon", "Time Beacon",
    "Increases the duration of Accelerated Recovery by 3 turns.",
    3, 0,
    effects={"ability_chronomancer_accelerated_recovery_duration": 3},
    connect=["orderly_protector"],
    source="CoA over 2 ranks: 'Increases the duration of effects applied by "
           "your Aeons by 4 sec.' The Aeon scoping cannot be built (nothing "
           "reads which Aeon is active, and the Aeons' effects live on their "
           "own abilities), so it is pointed at the spec's actual HoT. "
           "4 sec -> 3 turns, close enough at ~3 sec per turn given "
           "Accelerated Recovery runs 7. THIS NODE WOULD HAVE BEEN A TRAP "
           "BEFORE 6 Nov 2026: the HoT branch divided its fixed total by "
           "the talented duration, so +3 turns meant the same healing "
           "spread thinner - Accelerated Recovery measured 7 turns x 29 "
           "(203 total) unmodified and 11 x 18 (198) with a +4 talent. Now "
           "per-turn derives from the base duration and this is +3 ticks at "
           "full value. A SMALL INTEGER IN TURNS, so talent_ranks.spread() "
           "refuses to rank it - which is correct; a per-rank duration of "
           "one turn is the smallest unit there is."))

N.append(node(
    "aeon_of_oblivion", "Aeon of Oblivion",
    "Teaches Aeon of Oblivion, spending mana to make Epoch land harder.",
    3, 3,
    effects={"unlock_ability": "chronomancer_aeon_of_oblivion"},
    connect=["shimmering_shard"],
    source="CoA: 'Increases Epoch's mana cost by 30%, critical strike "
           "chance by 10%, and healing done by 15%. In addition, healing "
           "with Epoch now increases the target's damage dealt by 3% for 15 "
           "sec.' LOAD-BEARING UNLOCK. " + ALLY + " In this case the "
           "ally-damage clause is simply dropped rather than turned around, "
           "because a healer buffing their own damage is not what the Aeon "
           "is for; the ability's own stat changes carry the node."))

N.append(node(
    "shield_of_the_ages", "Shield of the Ages",
    "When a critical strike hits you, your damage taken is reduced by 3% "
    "and healing you receive is increased by 5% for 3 turns, stacking up to "
    "3 times.",
    3, -3,
    proc={"trigger": "on_damage_taken", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "shield_of_the_ages",
                           "name": "Shield of the Ages",
                           "effect_type": "buff", "duration": 3,
                           "stat_mods": {"damage_taken_pct": -0.03,
                                         "healing_taken_pct": 5},
                           "max_stacks": 3, "dispel_type": None,
                           "on_target": False}},
    connect=["chronicler"],
    source="CoA: 'When hit by a damaging critical strike, your damage taken "
           "is reduced by 3%, and healing received is increased by 5% for 3 "
           "sec, stacking 3 times.' PORTS ALMOST EXACTLY. The 'critical' "
           "filter is dropped: on_damage_taken gets no attacker and no "
           "ability_id from monsters, so there is nothing to test crit "
           "against. 3 sec -> 3 turns. KEPT AS A WORKED EXAMPLE OF THE "
           "PROJECT'S UNIT TRAP - the two keys in this one stat_mods dict "
           "read in DIFFERENT units. damage_taken_pct is RAW on both sides "
           "(character.py:2697 adds the status mod with no division), so "
           "-0.03 is -3%; authoring -3 would be -300% damage taken, which "
           "heals the player on every hit. healing_taken_pct is PERCENTAGE "
           "POINTS in a status effect (character.py:2904 divides by 100), "
           "so 5 is +5%; authoring 0.05 would deliver 0.05%. Both asserted "
           "in main()."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "orderly_protector", "Orderly Protector",
    "Your healing spells have a 20% chance to reset the cooldown of Fabric "
    "of Time.",
    4, 0,
    proc={"trigger": "on_heal_cast", "chance": 20, "icd": 1,
          "reset_cooldown": ["chronomancer_fabric_of_time"]},
    connect=["cycling_aeons"],
    source="CoA: 'Healing done by your Epoch now increases the healing of "
           "Fabric of Time by 10% for 10 sec, stacking 10 times. Each stack "
           "gives you a 2% chance when you cast Fabric of Time to reset its "
           "own cooldown.' The stacking buff and the per-stack chance both "
           "need a readable stack count, which does not exist, so the two "
           "clauses collapse into the one that can be built: a flat chance "
           "on heal to reset Fabric of Time outright. A BARE LIST resets "
           "fully, unlike the {abilities, turns} form used elsewhere in "
           "this tree - that is the whole difference between the two and it "
           "is easy to type the wrong one. 1-turn ICD so it cannot chain "
           "off a single turn's healing."))

N.append(node(
    "chronicler", "Chronicler",
    "Increases the duration of your heal over time effects by a further "
    "25% and their healing by 15%.",
    4, -3,
    effects={"hot_duration_pct": 0.25, "healing_power_pct": 15},
    connect=["timeline_tether"],
    source="CoA: 'Casting Fortify Timeline now extends the duration of "
           "Accelerated Recovery on all targets within 40 yds by an "
           "additional 10 sec.' There is no positioning and no per-ability "
           "proc trigger, and extending an effect already on OTHER targets "
           "is impossible (no payload extends a live effect's duration), so "
           "this becomes the global version. Stacks additively with Patient "
           "Mending for 45% longer HoTs on a healer who takes both. "
           "MIXED UNITS ON PURPOSE AND BOTH CORRECT: hot_duration_pct is a "
           "FRACTION (0.25 = +25%) while healing_power_pct is PERCENTAGE "
           "POINTS (15 = +15%), because character.py:1295 divides the "
           "latter by 100 and abilities.py reads the former raw. Asserted "
           "in main()."))

N.append(node(
    "shimmering_shard", "Shimmering Shard",
    "Your spells have a 30% chance to increase your damage and healing by "
    "5% for 6 turns, stacking up to 3 times.",
    4, 3,
    proc={"trigger": "on_cast", "chance": 30, "icd": 1,
          "apply_effect": {"effect_id": "shimmering_shard",
                           "name": "Shimmering Shard",
                           "effect_type": "buff", "duration": 6,
                           "stat_mods": {"damage_dealt_pct": 5.0,
                                         "healing_power_pct": 5},
                           "max_stacks": 3, "dispel_type": None,
                           "on_target": False}},
    connect=["timeline_tether"],
    source="CoA: 'Activating Aeon spells now grants you 4% increased damage "
           "and healing for 20 sec, stacking 3 times.' The Aeon scoping "
           "goes (no per-ability proc trigger) and becomes on_cast at 30%, "
           "which fires on any spell and keeps the stacking window "
           "meaningful. 20 sec -> 6 turns, CoA's 3 stacks kept. ANOTHER "
           "CORRECTED 5 Nov 2026, PARTIALLY: this dict carried "
           "all_damage, which is NOT readable from a status effect. The "
           "damage path reads all_damage through get_talent_effect "
           "(abilities.py:1606-1610), which sums talents and the current "
           "stance ONLY; a status effect's stat_mods go to "
           "get_status_stat_mod, from which the damage path reads exactly "
           "one key - damage_dealt_pct, in PERCENTAGE POINTS "
           "(abilities.py:1680-1683). So that half was silent dead data. "
           "healing_power_pct is KEPT: it was briefly changed too, on the "
           "mistaken assumption that it shared the problem, and then "
           "MEASURED - it moves healing_power on a live character, because "
           "_recalculate_derived_stats folds status effects into the same "
           "`bonuses` pool as gear (character.py:1218). Reverted. "
           "audit_talents could not see the all_damage half because that "
           "key HAS read sites, just not from a status effect, which is "
           "the blind spot tools/qa_proc_stat_mods.py now closes. Was a "
           "pure scalar on our side before any of this."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "cycling_aeons", "Cycling Aeons",
    "Reduces the cooldown of your Aeons by 40%.",
    5, 0,
    effects={"ability_chronomancer_aeon_of_protection_cooldown_pct": 0.40,
             "ability_chronomancer_aeon_of_renewal_cooldown_pct": 0.40,
             "ability_chronomancer_aeon_of_oblivion_cooldown_pct": 0.40},
    connect=["the_vast_infinite"],
    source="CoA: 'Reduces the cooldown of your Aeons by -50%.' Built "
           "literally, one key per Aeon, because there is no ability-group "
           "concept to address all three at once. 50% -> 40% because these "
           "are mode switches and a Chronomancer flipping Aeon every other "
           "turn is not the rotation CoA describes. *_cooldown_pct keys are "
           "FRACTIONS and POSITIVE MEANS A REDUCTION, which is the opposite "
           "sign convention from most of the file and has caught this "
           "project before. talented_cooldown floors at 1 turn, so stacked "
           "reductions cannot make these spammable."))

N.append(node(
    "timeline_tether", "Timeline Tether",
    "Your healing spells have a 30% chance to reduce the cooldown of "
    "Fortify Timeline by 2 turns.",
    5, -2,
    proc={"trigger": "on_heal_cast", "chance": 30, "icd": 0,
          "reset_cooldown": {"abilities": ["chronomancer_fortify_timeline"],
                             "turns": 2}},
    connect=["the_vast_infinite"],
    source="CoA: 'Your periodic damage and healing reduces the cooldown of "
           "your Fortify Timeline by 1 sec.' CoA hangs this off PERIODIC "
           "TICKS, which are not a trigger: status_effects.py:914 ticks a "
           "dot or hot by calling the recipient's own take_damage/heal with "
           "no caster reference, so there is nobody to fire a proc on. "
           "Re-pointed to on_heal_cast, which is the closest live trigger "
           "for a healer and keeps the node's purpose - heal often, get "
           "Fortify Timeline back sooner. This is the same loss Infinite "
           "takes seven times over, and it is the class's defining "
           "translation gap."))

N.append(node(
    "mark_of_order", "Mark of Order",
    "Increases your healing done by 10% and the healing of Reverse Wound by "
    "a further 20%.",
    5, 2,
    effects={"healing_power_pct": 10,
             "ability_chronomancer_reverse_wound_healing": 0.20},
    connect=["the_vast_infinite"],
    source="CoA: 'Healing done by Fortify Timeline now applies Mark of "
           "Order. Mark of Order increases the healing of your next Reverse "
           "Wound on the target by 10% for 20 sec. Every 1 sec for the "
           "duration, they gain an additional stack, up to 5.' " + ALLY + " "
           "The per-second stack accrual is separately impossible - there "
           "is no periodic or tick trigger of any kind. Turned around to a "
           "flat caster-side pair that produces the same outcome in play "
           "(Reverse Wound lands harder), at roughly what CoA's five stacks "
           "come to. Was a pure scalar on our side. healing_power_pct is "
           "PERCENTAGE POINTS, the ability key is a FRACTION."))

N.append(node(
    "overcorrection", "Overcorrection",
    "Your healing spells have a 30% chance to leave a mending that heals "
    "you over 4 turns.",
    1, 4,
    proc={"trigger": "on_heal_cast", "chance": 30, "icd": 1,
          "apply_effect": {"effect_id": "overcorrection",
                           "name": "Overcorrection",
                           "effect_type": "hot", "duration": 4,
                           "potency": 18, "dispel_type": None,
                           "on_target": False}},
    connect=["cadence_of_time"],
    source="CoA: 'Overhealing done by Correct the Mistake now applies a "
           "heal over time effect to the ally equal to 30% of the healing "
           "done over 5 seconds.' Three separate gaps: nothing measures "
           "OVERHEALING (the heal path returns the amount healed, not the "
           "surplus); there is no per-ability proc trigger; and " + ALLY + " "
           "So it becomes a self-mending HoT off any heal, which keeps the "
           "node's shape (heal a lot, get a trailing heal) while being "
           "honest about who receives it. 5 sec -> 4 turns. A proc-applied "
           "hot carries `potency` as its PER-TURN healing, unlike an "
           "ability rank's effect_value, which is the TOTAL across the "
           "duration and gets divided - so 18 here is 18 per turn, 72 over "
           "the effect."))

N.append(node(
    "titans_gaze", "Titan's Gaze",
    "Reduces all damage you take by 6% and increases your maximum health "
    "by 5%.",
    4, -1,
    effects={"damage_taken_pct": -0.06, "max_health_pct": 0.05},
    connect=["cycling_aeons"],
    source="CoA: 'Your Time Out! no longer breaks on damage, but now only "
           "reduces damage taken by 15%.' Time Out! is a channel and "
           "nothing controls whether an effect breaks on damage, so the "
           "node is rebuilt as the passive survivability a healer actually "
           "needs, at the mitigation CoA's own clause names. Folded in "
           "CoA's Nozdormu's Gaze, which also modifies Time Out! and is "
           "unbuildable for the same reason. CAREFUL, TWO CONVENTIONS IN "
           "ONE DICT AND BOTH DELIBERATE: as a TALENT effect "
           "damage_taken_pct is read RAW (character.py:2696, so -0.06 is "
           "-6%) and max_health_pct is a FRACTION too - but inside a STATUS "
           "EFFECT max_health_pct becomes percentage points and "
           "damage_taken_pct stays raw, so the pair flips apart depending "
           "on where it is written. These are talent effects, so both are "
           "fractions."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "the_vast_infinite", "The Vast Infinite",
    "Increases the duration of your heal over time effects by a further "
    "35%, your healing done by 20%, and your healing spells have a 40% "
    "chance to mend your most wounded ally for 35% of the amount healed.",
    6, 0,
    effects={"hot_duration_pct": 0.35, "healing_power_pct": 20},
    proc={"trigger": "on_heal_cast", "chance": 40, "icd": 0,
          "smart_heal_pct": 35},
    source="CoA: 'All party and raid members become one, equally sharing "
           "25% of all damage dealt to them for 10 sec, up to a maximum of "
           "100% of their total health. At the end of the duration, all "
           "affected allies are healed equal to the total damage shared "
           "split evenly amongst all allies.' NOT BUILDABLE, and for a "
           "reason this project has hit three times now: there is no "
           "accumulator or deferred-damage pool anywhere in the engine - "
           "the same gap that killed Puppeteer's Threads, Oathkeeper and "
           "Base: Beast Blood - and no trigger fires on an effect expiring. "
           "The ABILITY of the same name exists in our data, is ungated, "
           "and is left exactly as authored; this node is the capstone the "
           "tree has actually been building toward. hot_duration_pct here "
           "takes a Chronomancer who also has Patient Mending and "
           "Chronicler to +80% HoT duration, which on a 7-turn Accelerated "
           "Recovery is 13 turns at full per-tick value - the healer "
           "mirror of Infinite's long dots, and only honest at all since "
           "the HoT branch was fixed on 6 Nov 2026. The smart heal is the "
           "one payload that genuinely reaches an ally and picks the "
           "worst-off one, which is the nearest thing in the engine to "
           "'all party members become one'."))


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

    # The unit conventions this tree walks straight through. Each of these
    # keys reads one way as a talent effect and the other way inside a
    # status effect, and this file holds both kinds side by side.
    for n in TREE["nodes"]:
        eff = n.get("effects") or {}
        for k in ("hot_duration_pct",):
            if k in eff:
                assert 0 < eff[k] < 1, (
                    f"{n['talent_id']}.{k}={eff[k]} - a FRACTION as a "
                    f"talent effect (0.20 = +20%)")
        if "healing_power_pct" in eff:
            assert eff["healing_power_pct"] >= 1, (
                f"{n['talent_id']}.healing_power_pct={eff['healing_power_pct']}"
                f" - PERCENTAGE POINTS (character.py:1295 divides by 100), "
                f"so 0.15 would deliver 0.15%")
        mods = ((n.get("proc") or {}).get("apply_effect") or {}).get("stat_mods") or {}
        if "damage_taken_pct" in mods:
            assert -1 < mods["damage_taken_pct"] < 1, (
                f"{n['talent_id']} damage_taken_pct={mods['damage_taken_pct']}"
                f" - RAW ON BOTH SIDES (character.py:2697 adds the status mod "
                f"with no division), so -3 means -300% damage taken, which "
                f"HEALS the player on every hit")
        if "healing_taken_pct" in mods:
            assert abs(mods["healing_taken_pct"]) >= 1, (
                f"{n['talent_id']} healing_taken_pct="
                f"{mods['healing_taken_pct']} - PERCENTAGE POINTS inside a "
                f"status effect (character.py:2904 divides by 100), so 0.05 "
                f"would deliver 0.05%")

    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Chronomancer Time: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points, {len(GATED)} load-bearing unlocks")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
