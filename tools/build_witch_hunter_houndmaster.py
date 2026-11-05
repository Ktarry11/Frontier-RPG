#!/usr/bin/env python3
"""Rebuild Witch Hunter's Houndmaster tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_witch_hunter_houndmaster.py [--check]

SOURCE: data/reference/coa/witch-hunter.json - 37 real Houndmaster talents
from Ascension's own CoA Builder payload. Role: DPS.

The shipped tree was 23 nodes with ONE proc in it, and 20 of the 23 were a
bare number.

WHAT THE SPEC IS. A musket and a pack of shadow hounds. CoA's Houndmaster
sends the hounds in with Houndmaster's Call, keeps Shadow Rage up on them,
and fires Quickdraw off its own crits.

THE PET LIMIT decides a third of this tree, exactly as it did for
Primalist's Wildwalker, and the reasoning is recorded there too:

  1. A pet scales off THREE owner talent keys - pet_damage, pet_health,
     pet_armor (entities/pet.py, deliberately narrow so a pet does not
     inherit its owner's gear). Fractions.
  2. Nothing else. A pet does not fire procs - entities/pet.py has no
     fire_proc_trigger call at all - so "your hound's attacks now do X"
     has no mechanism behind it, and neither does a buff that lands ON the
     hound rather than on the Witch Hunter.

Fourteen of CoA's 37 Houndmaster talents are hound-side. Each one is
either routed into pet_damage, re-pointed at the Witch Hunter, or dropped,
and which is stated on the node. Shadow Rage is the clearest case: CoA
puts it on the HOUND ("Casting Shadowblast now grants Shadow Rage to your
Shadow Hound"), and CoA's own Coordinated Killing later puts the same buff
on the PLAYER - so the player version is the one that is buildable, and
the hound version collapses into it rather than being faked.

FOCUS, NOT RAGE. Same as Boltslinger: CoA's Witch Hunter is a Rage class
and Frontier's runs on Focus, so every cost and refund is translated.

CONVENTIONS, which do not agree with each other:
  armor_penetration_pct, attack_power_pct             percentage POINTS
  pet_damage / pet_health / pet_armor                 FRACTION
  ability_*_crit, crit_chance_physical, haste, dodge  PERCENT
  <school>_crit_damage_pct, all_damage, dot_damage    FRACTION
  damage_dealt_pct in a status effect                 percentage POINTS
  damage_taken_pct in a status effect                 read RAW (a fraction)
  *_cost_pct / *_cooldown_pct        FRACTION, POSITIVE MEANS A REDUCTION

TURN-BASED CUTS. Channels do not exist, so Darkflock is its damage and
Anguish's "reduce the channel time" becomes cooldown recovery. Cast times
do not exist, so Darkhunter's "next Darkslayer is instant cast" and Low
Dawn's "channel 0.5 sec quicker" have nothing to apply to. Repulse's
knockback and every yard of range are gone. Two CoA entries here have
broken template descriptions in this export (Sixfold Shot, $48) and are
not built from a guess at what they said.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/witch_hunter_houndmaster.json"

#: The Witch Hunter's three Trap abilities, for CoA's "your Trap spells".
TRAPS = ["witch_hunter_inquisitors_trap", "witch_hunter_shadow_trap",
         "witch_hunter_death_trap"]

#: Direct ranged attacks, for the nodes CoA hangs off them.
RANGED = ["witch_hunter_shadowblast", "witch_hunter_darkslayer",
          "witch_hunter_quickdraw", "witch_hunter_heartseeking_bolt"]

TREE = {
    "spec_name": "Witch Hunter Houndmaster",
    "tree_id": "witch_hunter_houndmaster",
    "description": ("Musket and pack - sends the hounds in and shoots "
                    "whatever they flush out."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from data/reference/coa/witch-hunter.json "
        "(37 real CoA Houndmaster talents, role DPS). Replaces a 23-node "
        "tree with 1 proc in it and 20 bare numbers. Fourteen of CoA's "
        "talents are hound-side and this engine gives a pet three scaling "
        "keys and no procs, so those are routed into pet_damage, "
        "re-pointed at the Witch Hunter, or dropped - stated per node. "
        "Every CoA reference to Rage is translated to Focus."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"witch_hunter_houndmaster_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"witch_hunter_houndmaster_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "expert_shot", "Expert Shot",
    "Increases the damage of Shadowblast by up to 20% and your chance to hit "
    "by up to 4%.",
    0, -5,
    effects={"ability_witch_hunter_shadowblast_damage": 0.20,
             "hit_rating": 4.0},
    connect=["sharpshooter"],
    source="CoA verbatim, and already a scalar in CoA over 2 ranks, so it "
           "stays one. Authored as the full-investment CEILING at one rank "
           "and left to the rank policy to spread - writing CoA's rank-1 "
           "value with ranks=2 and then having the policy bump it to 3 is "
           "what left three descriptions in this tree quoting a per-rank "
           "number that no longer existed."))

N.append(node(
    "dark_mind", "Dark Mind",
    "Increases your critical strike chance by 25% of your Intellect.",
    0, -3,
    effects={"crit_chance_from_intellect_pct": 0.25},
    connect=["sharpshooter"],
    source="CoA verbatim: 'Level 30 Passive. Increases your critical strike "
           "rating by 25% of your Intellect.' A live conversion: crit_chance "
           "is in STAT_CONVERSION_TARGETS (mapping to crit_chance_physical) "
           "and intellect is a source. Pairs with Boltslinger's Arbalist as "
           "the second reason a physical Witch Hunter wants Intellect."))

N.append(node(
    "houndfeeder", "Houndfeeder",
    "Increases your critical strike chance by 4% and your hounds' damage "
    "by 4%.",
    0, -1,
    effects={"crit_chance_physical": 4.0, "pet_damage": 0.04},
    connect=["dark_ranger"],
    source="CoA: 'Increases the critical strike chance of you and your Shadow "
           "Hound by 4%.' A pet's crit is not one of the three keys "
           "entities/pet.py reads off its owner, so the hound half becomes "
           "pet_damage - the closest thing to 'your hound hits harder' that "
           "the engine will actually apply. crit_chance_physical is a PERCENT "
           "and pet_damage is a FRACTION, in the same effects block."))

N.append(node(
    "trapper", "Trapper",
    "Reduces the cooldown of your Trap spells by 25%.",
    0, 1,
    effects={f"ability_{a}_cooldown_pct": 0.25 for a in TRAPS},
    connect=["dark_ranger"],
    source="CoA verbatim: 'Reduces the cooldown of your Trap spells by -25%.' "
           "Written out per ability because there is no key for a named group "
           "of abilities. POSITIVE is the reduction direction, which is the "
           "opposite of CoA's own '-25%' notation."))

N.append(node(
    "hail_of_gunfire", "Hail of Gunfire",
    "Increases your haste by 10%.",
    0, 3,
    effects={"haste": 10.0},
    connect=["reload"],
    source="CoA verbatim: 'Increases your ranged haste by 10%.' No separate "
           "ranged haste pool exists, and haste here means acting more often "
           "on the turn meter."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "sharpshooter", "Sharpshooter",
    "Shadowblast returns 15 Focus.",
    1, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_shadowblast"],
          "grant_resource": {"resource": "focus", "amount": 15}},
    connect=["coordinated_killing"],
    source="CoA: 'Level 20 Passive. Casting Shadowblast now regenerates 5% of "
           "your maximum mana.' The class has no mana - Witch Hunter is "
           "Focus-only - so this becomes Focus, as a flat amount rather than "
           "a percentage of the pool. Shadowblast is the filler, so this is "
           "what pays for the spec's expensive casts."))

N.append(node(
    "dark_ranger", "Dark Ranger",
    "Increases your hounds' damage by up to 10%.",
    1, -2,
    effects={"pet_damage": 0.10},
    connect=["kennel_master"],
    source="CoA verbatim: 'Increases the Shadow damage dealt by your Shadow "
           "Hounds by 5%.' pet_damage is school-agnostic - it scales the "
           "pet's attack_power and spell_power together - so the Shadow "
           "restriction is lost. A FRACTION, not points."))

N.append(node(
    "expulsion_of_evil", "Expulsion of Evil",
    "Your ranged attacks have a 5% chance to make Houndmaster's Call ready "
    "again at once.",
    1, 0,
    proc={"trigger": "on_damage_cast", "chance": 5, "icd": 1,
          "ability_filter": RANGED,
          "reset_cooldown": ["witch_hunter_houndmasters_call"]},
    connect=["scent_of_magic"],
    source="CoA verbatim: 'Direct ranged attacks and abilities now have a 5% "
           "chance to reset the cooldown of Houndmaster's Call.' Ports "
           "directly - CoA's 5% kept, with a 1-turn internal cooldown so it "
           "cannot chain off one flurry."))

N.append(node(
    "reload", "Reload",
    "Reduces the cooldown of Quickdraw by 35%.",
    1, 2,
    effects={"ability_witch_hunter_quickdraw_cooldown_pct": 0.35},
    connect=["pure_agony"],
    source="CoA: 'Reduces the cooldown of Quickdraw by 4 sec.' Quickdraw's "
           "CoA cooldown is 10 sec, so 4 sec is 40% of it; expressed as a "
           "percentage because cooldowns are counted in turns here and a flat "
           "4 would round to one turn either way. Trimmed to 35% rather than "
           "40% because Expulsion of Evil and Scent of Magic are already "
           "shortening this spec's cooldowns."))

N.append(node(
    "pure_agony", "Pure Agony",
    "Increases the critical strike damage of Quickdraw by 50%.",
    1, 4,
    effects={"ability_witch_hunter_quickdraw_crit_damage": 0.50},
    connect=["darkhunter"],
    source="CoA verbatim. ability_*_crit_damage is in the dynamic key family "
           "the engine resolves by name, and it is a FRACTION - unlike "
           "ability_*_crit beside it, which is a percent."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "coordinated_killing", "Coordinated Killing",
    "Unleashing the hounds whips you up too, increasing your damage by 10% "
    "for 3 turns.",
    2, -4,
    proc={"trigger": "on_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_unleash_the_hounds"],
          "apply_effect": {"effect_id": "witch_hunter_shadow_rage",
                           "name": "Shadow Rage", "effect_type": "buff",
                           "duration": 3, "max_stacks": 4,
                           "stat_mods": {"damage_dealt_pct": 10.0},
                           "on_target": False}},
    connect=["decimate"],
    source="CoA verbatim: 'Casting Unleash the Hounds now casts Shadow Rage "
           "on you for 10 sec.' THIS is the buildable Shadow Rage, and it "
           "absorbs CoA's other two. CoA's base Shadow Rage talent puts the "
           "buff on the HOUND off a Shadowblast cast, which no key reaches, "
           "and Lethal Pursuit adds 3 more stacks to it - so the stack count "
           "here is 4, which is CoA's 1 plus Lethal Pursuit's 3, rather than "
           "shipping Lethal Pursuit as a separate node that edits this one's "
           "payload (no key does that either). on_cast, not "
           "on_damage_cast: Unleash the Hounds is a summon and deals no "
           "damage, so a damage trigger would never fire."))

N.append(node(
    "kennel_master", "Kennel Master",
    "Increases your hounds' damage and health by up to 12%.",
    2, -2,
    effects={"pet_damage": 0.12, "pet_health": 0.12},
    connect=["decimate"],
    source="CoA: 'Casting Unleash The Hounds now has a 25% chance to summon "
           "an additional Lesser Shadow Hound for 15 sec.' A proc COULD "
           "cast_ability the summon again, but that is a summon re-triggering "
           "its own trigger - the Rockslide self-chain pattern is fine for a "
           "damage spell and genuinely dangerous for a pet summon, since "
           "nothing caps how many hounds exist. Routed into the hounds you "
           "already have instead, which is the honest version of 'more "
           "hound'."))

N.append(node(
    "darkrider", "Darkrider",
    "Reduces the Focus cost of Shadowblast, Vault and Unleash the Hounds "
    "by 15%.",
    2, 0,
    effects={"ability_witch_hunter_shadowblast_cost_pct": 0.15,
             "ability_witch_hunter_vault_cost_pct": 0.15,
             "ability_witch_hunter_unleash_the_hounds_cost_pct": 0.15},
    connect=["silver_bullets"],
    source="CoA: 'Reduces the Rage cost of Shadowblast, Vault, and Unleash "
           "the Hounds by -10.' Rage -> Focus, and the flat 10 becomes a "
           "percentage so it does not go stale against three different "
           "costs. POSITIVE reduces."))

N.append(node(
    "scent_of_magic", "Scent of Magic",
    "Your critical strikes bring Houndmaster's Call a turn closer to ready.",
    2, 2,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "reset_cooldown": {"abilities": ["witch_hunter_houndmasters_call"],
                             "turns": 1}},
    connect=["silver_bullets"],
    source="CoA: 'Critical strikes now apply Scent of Magic for 15 sec, "
           "causing your Shadow Hound's next Shadow Leap to incur a 10 sec "
           "reduced cooldown.' Shadow Leap is the hound's own ability and has "
           "no cooldown a talent can reach, so this is pointed at "
           "Houndmaster's Call - the player-side ability that sends the "
           "hounds in, which is what CoA's version is really shortening. "
           "turns:1 knocks one turn off rather than resetting outright."))

N.append(node(
    "darkhunter", "Darkhunter",
    "Quickdraw leaves your next hits 20% stronger for 2 turns.",
    2, 4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_quickdraw"],
          "apply_effect": {"effect_id": "witch_hunter_darkhunter",
                           "name": "Darkhunter", "effect_type": "buff",
                           "duration": 2, "max_stacks": 1,
                           "stat_mods": {"damage_dealt_pct": 20.0},
                           "on_target": False}},
    connect=["anguish"],
    source="CoA: 'Your Quickdraw now additionally causes your next Darkslayer "
           "within 15 seconds to be instant cast.' There are no cast times "
           "here, so making something instant is worth nothing and there is "
           "nothing to set. Repriced as damage on the window CoA describes, "
           "which keeps the Quickdraw-into-Darkslayer sequence worth doing. "
           "Also carries CoA's Low Dawn, which compresses a channel that "
           "likewise does not exist."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "decimate", "Decimate",
    "Increases your hounds' damage by 15% and your armor penetration by 10%.",
    3, -4,
    effects={"pet_damage": 0.15, "armor_penetration_pct": 10.0},
    connect=["daredevil"],
    source="CoA: '2 min cooldown. Empowers your Shadow Hounds for 20 sec, "
           "granting them 30% increased damage and haste and allowing them to "
           "ignore Armor.' Built as a passive rather than an activated "
           "window, because a 2-minute cooldown is not a shape this tree has "
           "and 30% for 20 seconds every two minutes averages out near 15% "
           "always. Pet haste is not a reachable key. 'Ignore Armor' is the "
           "Witch Hunter's own armor penetration, since there is no pet "
           "penetration key."))

N.append(node(
    "silver_bullets", "Silver Bullets",
    "Increases the damage of Darkslayer by up to 30%.",
    3, -2,
    effects={"ability_witch_hunter_darkslayer_damage": 0.30},
    connect=["daredevil"],
    source="CoA: 'Increases the damage of Darkslayer by 10%, increased by an "
           "additional 10% against Undead.' No effect key reads the target's "
           "creature type, so the Undead bonus is dropped and CoA's base 10% "
           "kept."))

N.append(node(
    "rampaging_hounds", "Rampaging Hounds",
    "Increases your hounds' damage and health by 10%.",
    3, 0,
    effects={"pet_damage": 0.10, "pet_health": 0.10},
    connect=["veiled_in_darkness"],
    source="CoA: 'Your Shadow Hounds melee attacks now cleave 1 additional "
           "nearby enemy.' No key adds a target to anything, least of all to "
           "a pet's auto attack, which no talent touches at all. Routed into "
           "the two pet keys that do work. This node and Kennel Master are "
           "both 'CoA wanted more hound and the engine offers pet_damage', "
           "which is why they sit in different tiers rather than next to each "
           "other reading as the same pick twice."))

N.append(node(
    "anguish", "Anguish",
    "Your shadow damage has a 10% chance to make Darkflock ready again at "
    "once.",
    3, 2,
    proc={"trigger": "on_damage_cast", "chance": 10, "icd": 1,
          "school": "shadow",
          "reset_cooldown": ["witch_hunter_darkflock"]},
    connect=["veiled_in_darkness"],
    source="CoA: 'Your Shadow damage dealt now has a 5% chance to reduce the "
           "channel time of your next Darkflock within 15 seconds by -50%.' "
           "Channels do not exist, so there is no channel time to halve. "
           "Rebuilt as getting Darkflock back sooner, which is what halving "
           "its channel bought in CoA, and raised 5% -> 10% because a "
           "cooldown reset is worth less than halving a cast."))

N.append(node(
    "bringer_of_darkness", "Bringer of Darkness",
    "Repulse resets the cooldown of Vault and returns 10 Focus.",
    3, 4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_repulse"],
          "reset_cooldown": ["witch_hunter_vault"],
          "grant_resource": {"resource": "focus", "amount": 10}},
    connect=["deal_with_the_devil"],
    source="CoA: 'Your Repulse now resets the cooldown of Vault and makes "
           "your next Vault within 6 sec free of cost.' The reset ports "
           "exactly. 'Free of cost' needs an ability cost key reachable from "
           "a status effect, and cost keys are read only through "
           "get_talent_effects() which never includes status effects - so it "
           "becomes a Focus refund of its own, which is the same saving by a "
           "route that fires."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "defender_of_darkshire", "Defender of Darkshire",
    "Your critical strikes quicken you, increasing your haste by 10% for 2 "
    "turns.",
    4, -3,
    proc={"trigger": "on_crit", "chance": 100, "icd": 2,
          "apply_effect": {"effect_id": "witch_hunter_defender_of_darkshire",
                           "name": "Defender of Darkshire",
                           "effect_type": "buff", "duration": 2,
                           "max_stacks": 1, "stat_mods": {"haste": 10.0},
                           "on_target": False}},
    connect=["lethal_pursuit"],
    source="CoA: 'Critical strikes with ranged auto attacks now increase the "
           "melee haste of your Shadow Hounds by 10% for 5 sec.' Pet haste is "
           "not a reachable key, so the buff lands on the Witch Hunter "
           "instead - CoA's number and the same trigger, pointed at the one "
           "of the two of you a talent can touch. 2-turn internal cooldown so "
           "a crit streak does not keep it permanently up."))

N.append(node(
    "veiled_in_darkness", "Veiled in Darkness",
    "Increases your attack power by 5%.",
    4, -1,
    effects={"attack_power_pct": 5.0},
    connect=["lethal_pursuit"],
    source="CoA: 'A veil of dark magic encircles you at all times, granting "
           "5% increased Attack Power to party and raid members within 100 "
           "yds.' A talent effect applies to its own character and there is "
           "no aura mechanism, so the description says 'your' rather than "
           "promising the party a buff it will never receive. "
           "attack_power_pct takes percentage POINTS."))

N.append(node(
    "loksey_journal", "Loksey's Journal",
    "Increases the damage your damage-over-time effects deal by 10%.",
    4, 1,
    effects={"dot_damage": 0.10},
    connect=["rearmament"],
    source="CoA: 'Increases the damage of Shadow Rage by 20% of your ranged "
           "attack power.' Shadow Rage in this tree is a damage_dealt_pct "
           "buff, not an ability with damage of its own, so there is nothing "
           "for that to scale - and no key adds attack power scaling to a "
           "status effect. Rebuilt as DoT damage, which this spec has real "
           "use for: Darkflock and Death Trap are both periodic."))

N.append(node(
    "rearmament", "Rearmament",
    "Reduces the cooldown of your Traps by a further 20%.",
    4, 3,
    effects={f"ability_{a}_cooldown_pct": 0.20 for a in TRAPS},
    connect=["feast_of_talons"],
    source="CoA: '5 min cooldown. Arm yourself against evil, resetting the "
           "cooldown of all Traps and Decimate.' Frontier has no "
           "witch_hunter_rearmament ability to unlock, and a 5-minute reset "
           "button is not a shape this tree has, so it becomes a permanent "
           "cut to the same cooldowns it would have reset. Stacks with "
           "Trapper at tier 0, deliberately: both are 'traps come back "
           "faster' and together they are the trap build."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "daredevil", "Daredevil",
    "When you are badly hurt, Vault becomes ready again at once and your "
    "hounds surge, dealing 20% more damage for 3 turns.",
    5, -3,
    proc={"trigger": "on_damage_taken", "chance": 15, "icd": 5,
          "reset_cooldown": ["witch_hunter_vault"],
          "apply_effect": {"effect_id": "witch_hunter_daredevil",
                           "name": "Daredevil", "effect_type": "buff",
                           "duration": 3, "max_stacks": 1,
                           "stat_mods": {"damage_dealt_pct": 20.0},
                           "on_target": False}},
    connect=["feast_of_talons"],
    source="CoA: 'Level 40 Passive. When you take damage that would reduce "
           "your health to 35% or less, you summon 3 lesser Shadow Hounds and "
           "reset the cooldown of Vault. Can only occur once every 2 min.' The "
           "Vault reset ports exactly. The health GATE does not: no proc "
           "payload reads the carrier's own health threshold, so it is a 15% "
           "chance on taking damage with a 5-turn internal cooldown, which is "
           "roughly CoA's once-every-2-minutes. The three summoned hounds are "
           "not buildable from a proc (see Kennel Master), so the surge lands "
           "as damage instead and the description says 'your hounds surge' "
           "without promising new ones."))

N.append(node(
    "deal_with_the_devil", "Deal With The Devil",
    "Increases your shadow critical strike damage by 50%.",
    5, -1,
    effects={"shadow_crit_damage_pct": 0.50},
    connect=["feast_of_talons"],
    source="CoA: 'Your and your Shadow Hounds critical damage dealt with "
           "Shadow damage is increased by 50%, but the cost of your spells "
           "and abilities is increased by 25%.' <school>_crit_damage_pct is a "
           "key the engine builds by interpolation, so shadow_crit_damage_pct "
           "is live. The hound half is unreachable. THE DRAWBACK IS DROPPED, "
           "and that is a real loss of CoA's design: cost keys are "
           "reduction-signed, so a 25% surcharge has to be written negative, "
           "which is indistinguishable from the sign error the audit now "
           "flags and which eight talents in this project already made. "
           "Flagged rather than faked - this node is strictly better than "
           "CoA's."))

N.append(node(
    "lethal_pursuit", "Lethal Pursuit",
    "Increases your hounds' damage by 15%.",
    5, 1,
    effects={"pet_damage": 0.15},
    connect=["feast_of_talons"],
    source="CoA: 'Shadow Rage now also grants your Shadow Hounds 10% "
           "increased haste and it now stacks 3 additional times.' Pet haste "
           "is unreachable, and the extra stacks are already folded into "
           "Coordinated Killing's payload at tier 2 (4 stacks = CoA's 1 plus "
           "these 3), because no key edits a sibling node's effect. What is "
           "left is the intent - the hounds get more out of a long fight - as "
           "pet damage."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "feast_of_talons", "Feast of Talons",
    "Darkflock sends the crows out wide, splashing 40% of its damage onto up "
    "to 5 enemies and leaving them bleeding shadow for 3 turns.",
    6, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_darkflock"],
          "splash_damage": {"pct": 0.40, "max_targets": 5,
                            "school": "shadow"},
          "apply_effect": {"effect_id": "witch_hunter_talon_feast",
                           "name": "Feast of Talons", "effect_type": "dot",
                           "duration": 3, "potency": 40,
                           "damage_school": "shadow", "on_target": True}},
    source="CoA: 'Striking at least 5 enemies with Darkflock now causes you "
           "to unleash a flock of crows around each enemy struck, dealing "
           "Twilight Damage over 9 sec.' The 5-enemy THRESHOLD is not "
           "buildable - no payload counts how many targets the triggering "
           "cast hit - so the capstone fires on every Darkflock and spreads "
           "to 5, which is the same shape pointed the other way round. 9 sec "
           "is 3 turns. Twilight is not a damage school here (the six are "
           "arcane, fire, frost, nature, shadow, holy), so both halves are "
           "shadow - CoA's Twilight is shadow-and-holy blended, and shadow is "
           "the half this spec is built on."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. tools/talent_ranks.py rescales so a ranked
# node lands on exactly the ceiling it had at one rank. The tier 6 capstone
# stays a single decisive pick; there are no unlock nodes in this tree,
# since no Witch Hunter ability carries requires_talent.
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
    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Witch Hunter Houndmaster: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
