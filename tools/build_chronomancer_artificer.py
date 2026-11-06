#!/usr/bin/env python3
"""Rebuild Chronomancer's Artificer tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_chronomancer_artificer.py [--check]

SOURCE: data/reference/coa_worksheets/chronomancer.md and
data/reference/coa/chronomancer.json - 40 real Artificer talents from
Ascension's own CoA Builder payload. Role: DPS (wand/ranged).

Artificer was 23 nodes with 3 procs - the thinnest of Chronomancer's three.

ECHO FRAGMENTS DO NOT EXIST, and they are the spec's entire economy in
CoA. Chronomancer is (ResourceType.MANA, None) at abilities.py:151 - mana
and nothing else - and not one Chronomancer ability carries a `generates`
block. So CoA's whole loop (Wand of Time generates a Fragment; Distortion
and Continuum spells consume them; Shatter Echo "damage increased by 40%
for each Echo Fragment consumed"; every Continuum duration is "3 sec plus
5 sec per Echo Fragment") has nothing to stand on.

This is the Venomancer Brood Marks situation exactly, and the lesson from
that pass is the one applied here: CHECK THE RESOURCE BEFORE ASSUMING IT.
Templar's Combo and Knight of Xoroth's Deathfire are real secondary pools
with real generators, so their CoA talents ported. Brood Marks, Heat,
Embers, Conductive, Oaths and now Echo Fragments are not, so every talent
that counts them has to be flattened to its unconditional version. Each
affected node says which clause was dropped and why.

THE CONTINUUM SPELLS NOW WORK PROPERLY, which they did not when this tree
was surveyed. Singularity Core and Flux Emitter had cooldown 0, duration
60 and buff_scope "raid" - and "raid" sets real_time_seconds to 30 real
MINUTES, after which tick_status_effects skips the effect entirely and the
turn `duration` is never read. A player cast both on turn one and kept
them permanently. Fixed 6 Nov 2026 to buff_scope "combat", cooldown 5,
duration 4, plus exclusive_group "chronomancer_continuum" - which builds
CoA's "Can only have 1 Continuum spell active at a time" exactly, since
applying one effect drops any other sharing the tag. Verified live.

THE PERIODIC-TICK TRIGGER STILL DOES NOT EXIST (status_effects.py:914
ticks a dot on the recipient with no caster handle), so Reverse
Engineering is re-pointed like the seven in Infinite and Time.

WHAT PORTS UNUSUALLY WELL, for once. Three of CoA's Artificer talents land
almost verbatim because they are cooldown and cast mechanics rather than
resource bookkeeping:
  - Temporal Convergence: "Your Wand of Time now has a 40% chance to reset
    its own cooldown" -> a reset_cooldown proc with a bare list, which is
    a full reset. Exact.
  - Wand Mastery: "Wand of Time and Shatter Echo now have a 25% chance to
    unleash Crystal Cannon" -> a cast_ability proc. Exact but for the
    two-ability scoping.
  - Borrowed Time: "Taking Physical damage now heals you equal to 10% of
    the damage dealt" -> leech_pct on on_damage_taken, and leech_pct is
    one of only three payloads that READ the triggering hit's amount.
    Exact.

WHAT COULD NOT BE BUILT AT ALL:
  - Threads of Eternity - needs to read a target's debuffs AND branch on
    which Continuum spell is active AND trigger N instances of another
    ability's damage. Three separate gaps.
  - Clocked In, Bronze Echoes, Aether Compression's cast-while-moving -
    cast-time and movement mechanics, of which this engine has neither.
  - Tamed Incantations / Time Is A Circle / Cheating Time - all three
    extend a LIVE effect's duration, and no payload does that.
  - Sporadic Incantations / Splitting Time - "strikes N additional
    enemies"; nothing adds targets to an ability.
  - Concentrated Fate, Archaeology, Conduction Burst, Pulse Driver - all
    read Echo Fragments or a live Continuum spell.
  - Hands of Time - Accelerate and Decelerate are not in our ability book.
  - Timemage (-30% harmful magic duration) - the only duration-reduction
    key the engine reads is stun_duration_reduction_pct, and it is checked
    solely against effects flagged is_stun (status_effects.py:699).
  - Unstable Chronoglass's spell redirection - no redirect mechanic. The
    ability exists in our data as a debuff and is ungated; untouched.

THIS TREE OWNS SIX GATED ABILITIES - more than any other tree in the game:
artificers_wand, crystal_cannon, shatter_echo, singularity_core,
flux_emitter and paradox_cannon. All six carry requires_talent and this is
their only unlock, so dropping any node makes that ability unobtainable
forever. Asserted in main().
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/chronomancer_artificer.json"

#: Abilities carrying requires_talent that ONLY this tree unlocks. Six is
#: the most of any tree in the game.
GATED = {"chronomancer_artificers_wand", "chronomancer_crystal_cannon",
         "chronomancer_shatter_echo", "chronomancer_singularity_core",
         "chronomancer_flux_emitter", "chronomancer_paradox_cannon"}

TREE = {
    "spec_name": "Chronomancer Artificer",
    "tree_id": "chronomancer_artificer",
    "description": ("A wand and a workshop - ranged attacks empowered by "
                    "Continuum devices, one at a time."),
    "_source_note": (
        "Rebuilt 6 Nov 2026 from the 40 real CoA Artificer talents (role "
        "DPS). ECHO FRAGMENTS DO NOT EXIST - Chronomancer is (MANA, None) "
        "and no ability generates a secondary resource - so CoA's entire "
        "Fragment/Distortion/Continuum economy is flattened to its "
        "unconditional form, the same call Venomancer Stalking's Brood "
        "Marks needed. What the Continuum spells DID gain is CoA's "
        "exclusivity: exclusive_group 'chronomancer_continuum' on "
        "Singularity Core and Flux Emitter means casting one drops the "
        "other, which is 'Can only have 1 Continuum spell active at a "
        "time' built exactly. Three talents port almost verbatim "
        "(Temporal Convergence, Wand Mastery, Borrowed Time) because they "
        "are cooldown and proc mechanics rather than resource counting. "
        "Six load-bearing unlocks, the most of any tree."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20,
                          "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"chronomancer_artificer_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"chronomancer_artificer_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


#: Appended wherever CoA's clause counts Echo Fragments.
FRAGMENTS = (
    "CoA scales this off ECHO FRAGMENTS, which are not a resource this "
    "engine has: Chronomancer is (ResourceType.MANA, None) at "
    "abilities.py:151 and no Chronomancer ability carries a `generates` "
    "block, so there is nothing to count. Flattened to the unconditional "
    "version at roughly what CoA's typical Fragment count comes to. Same "
    "call as Venomancer Stalking's Brood Marks; the lesson both times is "
    "to check the resource before porting the talent, since Templar's "
    "Combo and Knight of Xoroth's Deathfire ARE real and did port.")

N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "artificers_empowerment", "Artificer's Empowerment",
    "Increases your Spirit by 24%.",
    0, -4,
    effects={"spirit_pct": 24},
    connect=["wand_master"],
    source="CoA over 3 ranks: 'Increases your Spirit by 8%.' Three ranks at "
           "8% is 24%, authored as the ceiling at one rank so "
           "talent_ranks.spread() divides it back into three - the opposite "
           "of hand-authoring max_points=3, which leaves the ceiling as the "
           "PER-RANK value and triples it in play. That bug shipped on "
           "Guardian Vanguard's Iron Guardian (promised 15% Stamina, "
           "delivered 45%) and on all four Gladiator Training nodes, and "
           "only a live character reading the stat back caught it. Spirit "
           "is this spec's whole stat: CoA converts it into ranged attack "
           "power, spell damage and hit. spirit_pct is PERCENTAGE POINTS "
           "(character.py:1265 divides by 100)."))

N.append(node(
    "wand_master", "Wand Master",
    "Increases the damage of Wand of Time and Artificer's Wand by 20%.",
    0, -2,
    effects={"ability_chronomancer_wand_of_time_damage": 0.20,
             "ability_chronomancer_artificers_wand_damage": 0.20},
    connect=["wand_expert", "hyperwand"],
    source="CoA over 2 ranks: 'Increases the damage of Wand of Time and "
           "Artificer's Wand by 10%.' PORTS EXACTLY, both abilities, "
           "doubled for the two ranks. Was a pure scalar on our side. "
           "Per-ability damage keys are FRACTIONS."))

N.append(node(
    "wand_expert", "Wand Expert",
    "Increases your ranged attack power by 100% of your Spirit.",
    0, 0,
    effects={"ranged_ap_from_spirit_pct": 1.00},
    connect=["artificers_wand"],
    source="CoA level 20 passive: 'Increases your ranged attack power by "
           "100% of your Spirit and your hit rating by 5% of your Spirit.' "
           "The first half PORTS EXACTLY - ranged_ap is in "
           "STAT_CONVERSION_TARGETS and spirit in STAT_CONVERSION_SOURCES. "
           "The second half is DROPPED: hit_rating is NOT a valid "
           "conversion target, which has now cost seven nodes half their "
           "text across six classes and is the single most-repeated "
           "mistake in this audit. Paired with Artificer's Empowerment "
           "this is the spec's engine - Spirit becomes ranged damage. "
           "Was a pure scalar on our side. A FRACTION."))

N.append(node(
    "hyperwand", "Hyperwand",
    "Increases the damage of Shatter Echo by 30% and your critical damage "
    "by 15%.",
    0, 2,
    effects={"ability_chronomancer_shatter_echo_damage": 0.30,
             "crit_damage_pct": 0.15},
    connect=["temporal_convergence"],
    source="CoA: 'Increases the damage and critical damage of your Shatter "
           "Echo by 30%.' The damage half is per-ability and exact. There "
           "is no per-ability critical-damage key paired with a "
           "per-ability damage key (crit_damage is global or by school), so "
           "the crit half becomes crit_damage_pct at a lower value, since "
           "it now applies to everything. crit_damage_pct is read at "
           "abilities.py:1438 and is a FRACTION. Was a pure scalar on our "
           "side."))

N.append(node(
    "borrowed_time", "Borrowed Time",
    "Taking physical damage heals you for 10% of the damage dealt.",
    0, 4,
    proc={"trigger": "on_damage_taken", "chance": 100, "icd": 1,
          "leech_pct": 10},
    connect=["erode_armaments"],
    source="CoA: 'Taking Physical damage now heals you equal to 10% of the "
           "damage dealt. Can only occur once per sec.' PORTS ALMOST "
           "EXACTLY, and it is one of the few talents in this class that "
           "does. leech_pct is one of only THREE proc payloads that read "
           "the triggering hit's amount (the others being bonus_pct and "
           "smart heals), so '10% of the damage dealt' is literally what it "
           "computes. CoA's once-per-second becomes a 1-turn internal "
           "cooldown. The Physical-only filter is dropped: "
           "on_damage_taken gets no attacker and no ability_id from a "
           "monster, so there is nothing to test the school against - a "
           "limit that has bitten bonus_pct, cast_ability and "
           "ability_filter on this trigger too."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "artificers_wand", "Artificer's Wand",
    "Teaches Artificer's Wand, focusing the wand into a pair of rapid "
    "strikes.",
    1, 0,
    effects={"unlock_ability": "chronomancer_artificers_wand"},
    connect=["discovery", "shatter_echo"],
    source="CoA: 'Transforms your Unmake into Artificer's Wand. Focus to "
           "unleash 2 wand attacks dealing Ranged Weapon damage plus 5 over "
           "1 seconds. Generates 1 Echo Fragment.' LOAD-BEARING UNLOCK - "
           "chronomancer_artificers_wand carries requires_talent and this "
           "is its only unlock node. " + FRAGMENTS + " The ability "
           "replacing Unmake is also not a mechanism here (nothing swaps "
           "one ability for another), so both simply coexist."))

N.append(node(
    "temporal_convergence", "Temporal Convergence",
    "Your ranged attacks have a 40% chance to reset the cooldown of Wand "
    "of Time.",
    1, 2,
    proc={"trigger": "on_weapon_swing", "chance": 40, "icd": 0,
          "reset_cooldown": ["chronomancer_wand_of_time"]},
    connect=["elder_wand"],
    source="CoA: 'Your Wand of Time now has a 40% chance to reset its own "
           "cooldown.' PORTS ALMOST EXACTLY - reset_cooldown with a BARE "
           "LIST is a full reset, as against the {abilities, turns} form "
           "which only shaves turns; getting those two the wrong way round "
           "is an easy and silent mistake. The trigger is on_weapon_swing "
           "rather than Wand of Time specifically, because there is no "
           "per-ability proc trigger, and a wand spec swinging is the "
           "closest honest equivalent. Wand of Time has a 1-turn cooldown, "
           "so this effectively makes it spammable in bursts, which is "
           "what CoA's version does too."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "shatter_echo", "Shatter Echo",
    "Teaches Shatter Echo, flinging a distorted echo of your wand at the "
    "target.",
    2, -1,
    effects={"unlock_ability": "chronomancer_shatter_echo"},
    connect=["magic_sensitivity"],
    source="CoA: 'Launch a distorted echo from your wand at an enemy, "
           "dealing 90% Ranged Weapon damage plus Arcane damage. Damage "
           "increased by 40% for each Echo Fragment consumed.' "
           "LOAD-BEARING UNLOCK. " + FRAGMENTS + " The Fragment scaling is "
           "absorbed into Hyperwand's flat +30% instead, so the ability "
           "still hits hard for a talented Artificer."))

N.append(node(
    "discovery", "Discovery",
    "Your ranged attacks have a 30% chance to unleash a burst of Arcane "
    "damage and restore 30 mana.",
    2, 1,
    proc={"trigger": "on_weapon_swing", "chance": 30, "icd": 0,
          "damage_flat": 40, "school": "arcane",
          "grant_resource": {"resource": "mana", "amount": 30}},
    connect=["elder_wand"],
    source="CoA: 'Casting Artificer's Wand and Wand of Time now grants "
           "Discovery for 30 sec, stacking 4 times. At 3 stacks, your next "
           "Wand of Time or Artificer's Wand causes an additional Arcane "
           "Damage, scaling with Spirit.' The at-3-stacks gate cannot be "
           "built - nothing reads a stack count - so the stacking "
           "bookkeeping collapses into a flat 30% chance for the payoff "
           "itself, which is the part the player actually sees. Folded in "
           "CoA's Archaeology ('Your Discovery now also generates 3% of "
           "your base mana and health') as the mana grant, since that "
           "talent exists only to modify this one. grant_resource takes a "
           "FLAT `amount` - there is no `pct_max` field, and inventing one "
           "on Witch Doctor's Spiritual Devotee would have granted NOTHING "
           "while passing every check. The health half is dropped; "
           "grant_resource does not do health. `school` only types the "
           "damage_flat payload; it is not a trigger-side filter."))

N.append(node(
    "erode_armaments", "Erode Armaments",
    "Your ranged attacks have a 40% chance to sap the target's weapons, "
    "reducing the damage they deal for 2 turns.",
    2, 4,
    proc={"trigger": "on_weapon_swing", "chance": 40, "icd": 0,
          "apply_effect": {"effect_id": "erode_armaments",
                           "name": "Erode Armaments",
                           "effect_type": "debuff", "duration": 2,
                           "stat_mods": {"attack_power": -120},
                           "dispel_type": "magic", "on_target": True}},
    connect=["magic_sensitivity"],
    source="CoA: 'Your Wand attacks now reduce enemy attack power by 208 "
           "for 5 seconds.' PORTS ALMOST EXACTLY and is the node that "
           "justified Infinite's Mind Melt using flat AP too: CoA itself "
           "debuffs a flat attack power number on this class, so flat is "
           "the house style rather than a fudge. attack_power is one of "
           "only eight status stat_mods a monster reads, and it is FLAT - "
           "Monster.ability_power_bonus is 'Flat damage/healing swing from "
           "active buffs and debuffs'. 208 scaled down to 120 because our "
           "monster damage numbers are smaller than CoA's. 5 sec -> 2 "
           "turns."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "crystal_cannon", "Crystal Cannon",
    "Teaches Crystal Cannon, a pair of quick lesser wand strikes that "
    "scale with your Spirit.",
    3, -2,
    effects={"unlock_ability": "chronomancer_crystal_cannon"},
    connect=["wand_mastery"],
    source="CoA level 30 passive: 'Casting Discordance now unleashes the "
           "Crystal Cannon, launching 2 quick lesser Wand attacks at the "
           "enemy over 1 sec, scaling with Spirit.' LOAD-BEARING UNLOCK. "
           "CoA has it fire automatically off Discordance, which needs a "
           "per-ability trigger that does not exist; Wand Mastery at tier 5 "
           "gives it a real proc instead, so the ability does end up firing "
           "on its own for a player who takes both. CoA's Splitting Time "
           "('Crystal Cannon strikes 2 additional nearby enemies') is not "
           "built - nothing adds targets to an ability."))

N.append(node(
    "magic_sensitivity", "Magic Sensitivity",
    "Your critical strikes increase the damage the target takes from you "
    "by 8% for 3 turns.",
    3, 1,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "magic_sensitivity",
                           "name": "Magic Sensitivity",
                           "effect_type": "debuff", "duration": 3,
                           "stat_mods": {"damage_taken_pct": 0.08},
                           "dispel_type": "magic", "on_target": True}},
    connect=["singularity_core"],
    source="CoA: 'Critical strikes with Shatter Echo now increases the "
           "enemy's damage taken from you by 10% for 8 seconds.' PORTS "
           "ALMOST EXACTLY; only the Shatter-Echo scoping goes, since there "
           "is no per-ability proc trigger, and on_crit keeps CoA's "
           "critical requirement intact. 8 sec -> 3 turns, 10% -> 8% "
           "because it now fires off any crit. CAREFUL: bare "
           "damage_taken_pct is read RAW ON BOTH SIDES (monster.py adds the "
           "status mod with no division, unlike physical_ and magic_ which "
           "divide by 100), so 0.08 is 8% and authoring 8 would be +800% "
           "damage taken. Asserted in main(). Was a pure scalar on our "
           "side."))

N.append(node(
    "elder_wand", "Elder Wand",
    "Your ranged attacks have a 30% chance to increase your ranged attack "
    "power for 5 turns, stacking up to 10 times.",
    3, 3,
    proc={"trigger": "on_weapon_swing", "chance": 30, "icd": 0,
          "apply_effect": {"effect_id": "elder_wand", "name": "Elder Wand",
                           "effect_type": "buff", "duration": 5,
                           "stat_mods": {"ranged_ap": 25},
                           "max_stacks": 10, "dispel_type": None,
                           "on_target": False}},
    connect=["flux_emitter"],
    source="CoA: 'Your Wand attacks now have a 30% chance to increase the "
           "damage of Artificer's Wand against the target by 3% for 15 "
           "seconds, stacking 10 times.' The chance, duration and stack "
           "count all port; what cannot is a per-ability damage bonus "
           "living inside a status effect, and 'against the target' would "
           "need the stack to sit on the enemy while buffing the caster. "
           "Turned into a caster-side ranged attack power ramp, which "
           "produces the same shape in play - keep swinging, hit harder - "
           "and still rewards a long fight. 15 sec -> 5 turns. max_stacks "
           "is genuinely honoured even though nothing can READ the count. "
           "Was a pure scalar on our side."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "singularity_core", "Singularity Core",
    "Teaches Singularity Core, a Continuum device that empowers your wand.",
    4, 0,
    effects={"unlock_ability": "chronomancer_singularity_core"},
    connect=["resonance"],
    source="CoA: 'Empower your Wand attacks to deal an additional 50% "
           "Ranged Weapon Damage plus additional Arcane damage for 3 sec "
           "plus 5 sec per Echo Fragment. Can only have 1 Continuum spell "
           "active at a time.' LOAD-BEARING UNLOCK. " + FRAGMENTS + " THE "
           "EXCLUSIVITY IS REAL THOUGH, and it was added to the ability on "
           "6 Nov 2026: exclusive_group 'chronomancer_continuum' on both "
           "this and Flux Emitter means casting either drops the other, "
           "which is CoA's rule verbatim. The same commit fixed the "
           "ability's buff_scope from 'raid' (30 real minutes, turn "
           "duration ignored) to 'combat', and gave it a 5-turn cooldown; "
           "before that both Continuum spells were simply permanent. CoA's "
           "Pulse Driver and Conduction Burst both read 'while a Continuum "
           "spell is active', which nothing can do, so neither is built."))

N.append(node(
    "flux_emitter", "Flux Emitter",
    "Teaches Flux Emitter, a Continuum device that spreads your wand "
    "attacks wide.",
    4, 2,
    effects={"unlock_ability": "chronomancer_flux_emitter"},
    connect=["paradox_cannon"],
    source="CoA: 'Empower Wand attacks to affect up to 2 additional nearby "
           "enemies for 3 sec plus 5 sec per Echo Fragment. Affected "
           "attacks deal less damage per additional enemy hit. Can only "
           "have 1 Continuum spell active at a time.' LOAD-BEARING UNLOCK. "
           "Shares exclusive_group 'chronomancer_continuum' with "
           "Singularity Core, so the two genuinely compete - the choice "
           "CoA built the spec around. The additional-targets half lives on "
           "the ability's own effects; a talent cannot add targets. "
           "Sporadic Incantations ('strikes 1 additional enemy') and "
           "Cheating Time ('extends the duration of Flux Emitter by 4 "
           "sec') are both unbuildable - the second because no payload "
           "extends a LIVE effect's duration."))

N.append(node(
    "intuition", "Intuition",
    "Increases your critical damage by 25% and your critical strike chance "
    "by 4%.",
    4, -2,
    effects={"crit_damage_pct": 0.25, "crit_chance_physical": 4.0},
    connect=["wand_mastery"],
    source="CoA level 50 passive: 'Increases your critical damage by 25%.' "
           "Ports exactly. Folded in CoA's Infinity Stone ('Increases the "
           "critical strike chance of all party and raid members by 3%. In "
           "addition, increases your critical strike chance by 3%') as the "
           "crit-chance half, keeping only the selfish clause: A TALENT "
           "EFFECT CAN NEVER REACH AN ALLY - only a party-targeted ABILITY "
           "can (abilities.py:2064) - and Chronomancer has no aura ability "
           "to convert, unlike Guardian, whose four auras were changed to "
           "target_type 'party' on 5 Nov 2026 for exactly this reason. "
           "crit_damage_pct is a FRACTION; crit_chance_physical is "
           "PERCENTAGE POINTS. Physical rather than spell because this is "
           "the wand spec and its damage comes off ranged attacks. Both "
           "were pure scalars on our side."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "wand_mastery", "Wand Mastery",
    "Your ranged attacks have a 30% chance to unleash Crystal Cannon.",
    5, -1,
    proc={"trigger": "on_weapon_swing", "chance": 30, "icd": 0,
          "cast_ability": "chronomancer_crystal_cannon"},
    connect=["reverse_engineering"],
    source="CoA: 'Wand of Time and Shatter Echo now have a 25% chance to "
           "unleash Crystal Cannon, launching 2 quick lesser Wand auto "
           "attacks at the enemy over 1 seconds, scaling with Spirit. While "
           "Paradox Cannon is active, the chance to trigger this effect is "
           "increased by 10%.' PORTS ALMOST EXACTLY via a cast_ability "
           "proc, which takes a bare ability id. The two-ability scoping "
           "becomes on_weapon_swing (no per-ability trigger) and the "
           "'while Paradox Cannon is active' bonus is dropped (nothing "
           "reads whether an effect is live), so 25% is set at a flat 30%. "
           "NOTE: cast_ability does NOT check that the character has "
           "learned the ability, so this would fire even without Crystal "
           "Cannon's unlock node - but that node is in this tree and at a "
           "lower tier, so a player with this talent has it."))

N.append(node(
    "paradox_cannon", "Paradox Cannon",
    "Teaches Paradox Cannon, a Continuum device that restores your mana.",
    5, 2,
    effects={"unlock_ability": "chronomancer_paradox_cannon"},
    connect=["reverse_engineering"],
    source="CoA: 'Generate 1 Echo Fragment every 2.5 sec for 5 sec, plus an "
           "additional 5 sec per Echo Fragment consumed. Can only have 1 "
           "Continuum spell active at a time.' LOAD-BEARING UNLOCK. "
           + FRAGMENTS + " Our version is already authored as "
           "restore_resource on mana, which is the honest translation of a "
           "resource generator when the resource it generates does not "
           "exist. It applies no status effect, so exclusive_group cannot "
           "reach it and it does not compete with the other two Continuum "
           "spells - half of CoA's rule, and the half that could not be "
           "built."))

N.append(node(
    "resonance", "Resonance",
    "Your ranged attacks have a 35% chance to reduce the cooldown of "
    "Hasten by 2 turns.",
    5, 0,
    proc={"trigger": "on_weapon_swing", "chance": 35, "icd": 0,
          "reset_cooldown": {"abilities": ["chronomancer_hasten"],
                             "turns": 2}},
    connect=["reverse_engineering"],
    source="CoA: 'Casting Artificer's Wand or Crystal Cannon now has a 35% "
           "chance to reduce the cooldown of Hasten by 1 sec.' PORTS "
           "ALMOST EXACTLY - the {abilities, turns} form of reset_cooldown "
           "shaves turns rather than resetting outright, which is what CoA "
           "describes. Only the two-ability scoping goes (no per-ability "
           "proc trigger); on_weapon_swing is the wand spec's equivalent. "
           "1 sec -> 2 turns, since a sub-turn reduction would round to "
           "nothing and Hasten's cooldown is long enough to absorb it."))

N.append(node(
    "fate_twister", "Fate Twister",
    "Reduces the cooldown of Unstable Chronoglass by 50% and Collapse by "
    "30%.",
    5, 4,
    effects={"ability_chronomancer_unstable_chronoglass_cooldown_pct": 0.50,
             "ability_chronomancer_collapse_cooldown_pct": 0.30},
    connect=["reverse_engineering"],
    source="CoA: 'Reduces the cooldown of Unstable Chronoglass by 30 sec.' "
           "Its 1-minute cooldown halved is CoA's 30 seconds exactly, so "
           "this is a faithful port expressed as a percentage because the "
           "key is proportional. Collapse added so the node is not a "
           "one-ability pick on a 10-turn cooldown. *_cooldown_pct keys are "
           "FRACTIONS and POSITIVE MEANS A REDUCTION - the opposite sign "
           "convention from most of this file. talented_cooldown floors at "
           "1 turn, so this cannot delete a cooldown outright."))

N.append(node(
    "conduction_burst", "Conduction Burst",
    "Increases the damage of Shatter Echo by a further 25% and of Crystal "
    "Cannon by 20%.",
    3, 5,
    effects={"ability_chronomancer_shatter_echo_damage": 0.25,
             "ability_chronomancer_crystal_cannon_damage": 0.20},
    connect=["elder_wand"],
    source="CoA: 'Your Shatter Echo now deals 20% additional damage while a "
           "Continuum spell is active.' The conditional cannot be built - "
           "nothing reads whether another effect is live, which also killed "
           "Pulse Driver and Chaos Fusion - so rather than ship a condition "
           "that silently never fires it becomes unconditional at 25%, "
           "stacking with Hyperwand's 30%. Extended to Crystal Cannon so "
           "the node pairs with Wand Mastery, and because CoA's Splitting "
           "Time ('Crystal Cannon strikes 2 additional nearby enemies') "
           "cannot be built either - nothing adds targets to an ability - "
           "so its intent lands here as damage instead. Both FRACTIONS."))

N.append(node(
    "concentrated_fate", "Concentrated Fate",
    "Increases your spell damage by 10% and your ranged attack power by a "
    "further 15% of your Spirit.",
    4, 4,
    effects={"spell_damage": 0.10, "ranged_ap_from_spirit_pct": 0.15},
    connect=["resonance"],
    source="CoA: 'Increases the effectiveness of your Echo Fragments by "
           "20%.' " + FRAGMENTS + " With nothing to be 20% more effective, "
           "the node is rebuilt along the tree's actual spine - Spirit into "
           "ranged damage - stacking with Wand Expert's 100% and the "
           "capstone's 10%. Was a pure scalar on our side. spell_damage is "
           "a FRACTION; the conversion key is a fraction too, and both read "
           "raw."))

N.append(node(
    "timemage", "Timemage",
    "Reduces the duration of stuns against you by 30% and increases your "
    "maximum health by 5%.",
    5, -3,
    effects={"stun_duration_reduction_pct": 0.30, "max_health_pct": 0.05},
    connect=["wand_mastery"],
    source="CoA: 'Reduces the duration of harmful magic effects on you by "
           "-30%.' THE GENERAL VERSION DOES NOT EXIST: the only "
           "duration-reduction key the engine reads is "
           "stun_duration_reduction_pct, and status_effects.py:699 checks "
           "it SOLELY against effects flagged is_stun. So the description "
           "promises stuns and only stuns - the same correction Witch "
           "Doctor Brewing's Spice: Peacebloom needed after it invented "
           "`cc_duration_taken_pct`, which was caught by the audit. Roots "
           "and snares have no mechanic to shorten at all. The health is "
           "added so the node is worth a point on a class that is not "
           "stunned every fight. BOTH KEYS ARE FRACTIONS, and I authored "
           "the first as 30.0 on the assumption it was percentage points - "
           "audit_talents caught it as '1000%' and it was right. So "
           "stun_duration_reduction_pct joins crit_damage_*, all_damage and "
           "the *_cost_pct family as a fraction, against the "
           "crit_chance_*/haste/hit_rating family, which are points. There "
           "is no rule to infer it from the name; the audit is the only "
           "reliable check. max_health_pct is a fraction as a TALENT effect "
           "too, though it becomes percentage points inside a status "
           "effect."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "reverse_engineering", "Reverse Engineering",
    "Increases your ranged attack power by 10% of your Spirit. Your "
    "damaging spells have a 25% chance to grant 20% haste for 3 turns and "
    "restore 60 mana.",
    6, 0,
    effects={"ranged_ap_from_spirit_pct": 0.10},
    proc={"trigger": "on_damage_cast", "chance": 25, "icd": 1,
          "grant_resource": {"resource": "mana", "amount": 60},
          "apply_effect": {"effect_id": "reverse_engineering",
                           "name": "Reverse Engineering",
                           "effect_type": "buff", "duration": 3,
                           "stat_mods": {"haste": 20.0},
                           "dispel_type": None, "on_target": False}},
    source="CoA: 'Periodic damage and healing now has a 15% chance to "
           "increase your haste by 15% for 6 seconds and grant allies "
           "Replenishment. Replenishment replenishes 5% of maximum mana per "
           "5 sec for 15 seconds.' CoA hangs it off PERIODIC TICKS, which "
           "are not a trigger - status_effects.py:914 ticks a dot by "
           "calling the recipient's own take_damage with no caster "
           "reference, so there is nobody to fire a proc on. Re-pointed to "
           "on_damage_cast, the eighth and last talent in this class to "
           "take that loss. The ally Replenishment becomes mana for the "
           "caster: a proc cannot grant a resource to an ally. 6 sec -> 3 "
           "turns, 15% -> 25% because a per-cast roll is far rarer than a "
           "per-tick one. The Spirit conversion is added so the capstone "
           "closes the loop the tree opened with Wand Expert and "
           "Artificer's Empowerment - Spirit into ranged damage - rather "
           "than being a proc alone. haste is PERCENTAGE POINTS; the "
           "conversion key is a FRACTION."))


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

    # Bare damage_taken_pct is read RAW on BOTH sides, unlike its physical_
    # and magic_ siblings, which are divided by 100 inside a status effect.
    # Authoring 8 instead of 0.08 is +800% damage taken.
    for n in TREE["nodes"]:
        mods = ((n.get("proc") or {}).get("apply_effect") or {}).get("stat_mods") or {}
        if "damage_taken_pct" in mods:
            assert -1 < mods["damage_taken_pct"] < 1, (
                f"{n['talent_id']} damage_taken_pct={mods['damage_taken_pct']}"
                f" - bare damage_taken_pct is RAW on both sides, so 8 means "
                f"+800% damage taken, not +8%")
        # grant_resource takes a FLAT `amount`. A `pct_max` field does not
        # exist; inventing one granted nothing at all on Witch Doctor's
        # Spiritual Devotee while passing every check.
        gr = (n.get("proc") or {}).get("grant_resource")
        if gr:
            assert "amount" in gr, (
                f"{n['talent_id']} grant_resource has no `amount` - that is "
                f"the only field status_effects.py:1337 reads, and anything "
                f"else is silently zero")

    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Chronomancer Artificer: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points, {len(GATED)} load-bearing unlocks")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
