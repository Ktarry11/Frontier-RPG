#!/usr/bin/env python3
"""Rebuild Witch Hunter's Boltslinger tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_witch_hunter_boltslinger.py [--check]

SOURCE: data/reference/coa/witch-hunter.json - 38 real Boltslinger talents
from Ascension's own CoA Builder payload, the same data allthingscoa.com
presents. Role: DPS, and all four Witch Hunter specs are DPS, which is
unusual here.

WHY THIS CLASS FIRST, of the nineteen left. Witch Hunter is the worst tree
set in the game by a wide margin: 86 of its 92 nodes are a bare number,
with SIX procs across four whole specs. Boltslinger itself had 23 nodes and
2 procs. Measured, not guessed - 93% pure scalar against a 20-88% range for
everyone else.

WHAT THE SPEC IS. A crossbow that costs resource and pays it back. CoA's
Boltslinger fires Heartseeking Bolt as its hard hit, keeps Tormentor
ticking, and spends everything on Damnation as an execute - and the
rotation is held together by the resource coming back on crits and big
shots. The old tree had the abilities and none of the economy.

FOCUS, NOT RAGE. This matters on nearly every node. CoA's Witch Hunter is
a Rage class and its talent text says so throughout - "Reduces the Rage
cost of Witchbane", "refunds 40 Rage", "Deplete your rage". Frontier's
Witch Hunter runs on FOCUS (combat/abilities.py: "Witch Hunter":
(ResourceType.FOCUS, None)) and has no Rage at all, so every one of those
is translated. A grant_resource payload naming "rage" here would be a
resource the class cannot hold.

CONVENTIONS, which do not agree with each other:
  armor_penetration_pct, attack_power_pct            percentage POINTS
  crit_damage_physical, all_damage, dot_damage       FRACTION
  ability_*_crit                                     PERCENT
  damage_dealt_pct / damage_taken_pct in a status    percentage POINTS
  damage_taken_pct as a TALENT effect                FRACTION, NEGATIVE
                                                     reduces
  *_cost_pct / *_cooldown_pct      FRACTION, POSITIVE MEANS A REDUCTION
  <target>_from_<source>_pct       FRACTION, pairs from
                                   STAT_CONVERSION_TARGETS/SOURCES only

WHAT IS NOT BUILDABLE, stated per node rather than faked:
  - "Hits an additional nearby enemy" / "strikes an additional target".
    An ability is enemy_aoe or it is not, and no talent key converts one;
    aoe_damage only scales abilities already flagged. Relentless and
    Everything You Have lose that half.
  - Creature-type conditions ("against Undead and Demons"). No effect key
    reads the target's creature type, so Witching Bolt and Silver Bolts
    drop the condition and are repriced for applying always.
  - Health-gated DAMAGE. low_health_healing_pct is the only
    recipient-health conditional and it is heal-side, so Contract Killing's
    above-75%/below-35% windows and Kingdom Hearts' below-20% guarantee
    are both unconditional here.
  - "Your next cast ignores its requirement / incurs no cooldown."
    Nothing suppresses an ability's own gate or cooldown from a buff, so
    Slinging Bolts and Bolt and Dash pay out as damage instead.
  - Party auras. Slayer is "+3% crit to all party and raid members"; a
    talent effect applies to its own character and there is no aura
    mechanism, so it keeps the self half and says "your".

TURN-BASED CUTS. Every yard of range and all movement speed is gone, which
takes Daring Escape's backward jump, Crossbow Frenzy entirely as written,
and Bolt and Dash's speed rider. Channels do not exist, so Twilight
Frenzy's "unable to stop moving for 5 sec" is just its damage. Cast times
do not exist, so Heavy Crossbows' +0.5 sec drawback has nothing to apply
to - noted on that node, since losing a drawback is a buff.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/witch_hunter_boltslinger.json"

#: The two big shots Silver Bolts and friends empower.
BIG_SHOTS = ["witch_hunter_heartseeking_bolt", "witch_hunter_damnation"]

#: What CoA calls "ranged abilities" for this spec, among what we have.
RANGED = ["witch_hunter_shadowblast", "witch_hunter_darkslayer",
          "witch_hunter_heartseeking_bolt", "witch_hunter_damnation",
          "witch_hunter_quickdraw"]

TREE = {
    "spec_name": "Witch Hunter Boltslinger",
    "tree_id": "witch_hunter_boltslinger",
    "description": ("Crossbow killer - spends everything on one shot and "
                    "takes it back off the corpse."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from data/reference/coa/witch-hunter.json "
        "(38 real CoA Boltslinger talents, role DPS). Replaces a 23-node "
        "tree with 2 procs in it. Witch Hunter was the worst tree set in "
        "the game when measured - 86 of 92 nodes a bare number, 6 procs "
        "across four specs - which is why it was taken first of the "
        "nineteen classes left. Every CoA reference to Rage is translated "
        "to FOCUS, which is the resource this class actually has."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source="", active=False):
    entry = {
        "talent_id": f"witch_hunter_boltslinger_{nid}",
        "name": name,
        "description": desc,
        "node_type": "active" if active else "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"witch_hunter_boltslinger_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "mechanized_crossbows", "Mechanized Crossbows",
    "Increases your ranged attack power by 10% of your Agility.",
    0, -5,
    effects={"ranged_ap_from_agility_pct": 0.10},
    connect=["bane_of_witches"],
    source="CoA: 'Increases your ranged attack power by 10% and the range of "
           "your ranged abilities by 5 yds.' Range means nothing in an engine "
           "with no positioning. There is no flat ranged_ap_pct key, so the "
           "10% is expressed as the conversion this engine does support - "
           "ranged_ap is in STAT_CONVERSION_TARGETS and agility is the stat a "
           "crossbow spec stacks."))

N.append(node(
    "rapid_reload", "Rapid Reload",
    "Increases your haste by 8%.",
    0, -3,
    effects={"haste": 8.0},
    connect=["bane_of_witches"],
    source="CoA verbatim: 'Increases your ranged haste by 8%.' There is no "
           "separate ranged haste pool here, and haste on a turn meter means "
           "acting more often rather than drawing faster."))

N.append(node(
    "my_trusty_arbalest", "My Trusty Arbalest",
    "Reduces the Focus cost of Witchbane and Shadowblast by up to 20% and "
    "increases your chance to hit by up to 4%.",
    0, -1, ranks=2,
    effects={"ability_witch_hunter_witchbane_cost_pct": 0.10,
             "ability_witch_hunter_shadowblast_damage": 0.10,
             "hit_rating": 2.0},
    connect=["one_shot"],
    source="CoA verbatim but for the resource: 'Reduces the Rage cost of "
           "Witchbane and Shadowblast by -10% and increases your chance to "
           "hit by 2%.' Rage -> Focus. POSITIVE is the reduction direction "
           "for _cost_pct, which is the opposite of how CoA writes it "
           "('-10%') and the mistake eight talents in this project have "
           "already made."))

N.append(node(
    "heartless", "Heartless",
    "Increases your physical critical strike damage by up to 30%.",
    0, 1, ranks=2,
    effects={"crit_damage_physical": 0.15},
    connect=["one_shot"],
    source="CoA verbatim: 'Increases your Physical ranged critical damage by "
           "15%.' crit_damage_physical is a FRACTION, unlike the crit CHANCE "
           "keys beside it which are percents."))

N.append(node(
    "arbalist", "Arbalist",
    "Increases your attack power by 100% of your Intellect.",
    0, 3,
    effects={"attack_power_from_intellect_pct": 1.00},
    connect=["kingdom_hearts"],
    source="CoA verbatim: 'Level 30 Passive. Increases your attack power by "
           "100% of your Intellect.' A live conversion - attack_power is in "
           "STAT_CONVERSION_TARGETS, intellect in STAT_CONVERSION_SOURCES - "
           "and a genuinely odd one, which is the point: it is what makes a "
           "Witch Hunter want Intellect on a physical kit."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "bane_of_witches", "Bane of Witches",
    "Heartseeking Bolt leaves you dealing 10% more damage for 3 turns.",
    1, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_heartseeking_bolt"],
          "apply_effect": {"effect_id": "witch_hunter_bane_of_witches",
                           "name": "Bane of Witches", "effect_type": "buff",
                           "duration": 3, "max_stacks": 1,
                           "stat_mods": {"damage_dealt_pct": 10.0},
                           "on_target": False}},
    connect=["strafing_shot"],
    source="CoA verbatim: 'Casting Heartseeking Bolt now increases your "
           "Physical damage dealt by 10% for 8 sec.' 8 sec is 3 turns. "
           "damage_dealt_pct is the status-effect route to a damage "
           "multiplier - all_damage is read only through "
           "get_talent_effects(), which never includes status effects - and "
           "it is school-agnostic here, so the Physical restriction is lost. "
           "Was physical_damage +2% per rank over 5 ranks, a flat 10% that "
           "was always on."))

N.append(node(
    "one_shot", "One Shot",
    "Increases the critical strike chance of Heartseeking Bolt by 20%.",
    1, -2,
    effects={"ability_witch_hunter_heartseeking_bolt_crit": 20.0},
    connect=["silver_bolts"],
    source="CoA verbatim. ability_*_crit is a PERCENT. Was 4.0 per rank over "
           "3 ranks, which is 12 against CoA's 20."))

N.append(node(
    "crossbow_expert", "Crossbow Expert",
    "Increases the damage of Shadowblast by 10% and Witchbane by 5%.",
    1, 0, ranks=2,
    effects={"ability_witch_hunter_shadowblast_damage": 0.10,
             "ability_witch_hunter_witchbane_damage": 0.05},
    connect=["silver_bolts"],
    source="CoA verbatim, and already a scalar in CoA, so it stays one."))

N.append(node(
    "kingdom_hearts", "Kingdom Hearts",
    "Heartseeking Bolt returns 20 Focus.",
    1, 2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_heartseeking_bolt"],
          "grant_resource": {"resource": "focus", "amount": 20}},
    connect=["witching_bolt"],
    source="CoA: 'Your Heartseeking Bolt is now guaranteed to critically "
           "strike on enemies below 20% health and it now restores 10% of "
           "your maximum mana.' Two halves, neither portable as written. No "
           "effect key reads the target's health for damage, so the "
           "conditional guarantee is dropped rather than shipped as an "
           "unconditional one. The class has no mana at all - Witch Hunter "
           "is Focus-only - so the restore becomes Focus, as a flat amount "
           "rather than a percentage because pct_max of a Focus pool is not "
           "a shape any existing node uses."))

N.append(node(
    "neverending_pursuit", "Neverending Pursuit",
    "Critical strikes with Damnation refund 40 Focus.",
    1, 4,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_damnation"],
          "grant_resource": {"resource": "focus", "amount": 40}},
    connect=["witching_bolt"],
    source="CoA verbatim but for the resource: 'Critically striking with "
           "Damnation now refunds 40 Rage.' Rage -> Focus. This is the node "
           "the whole spec's economy turns on - Damnation is the dump, and "
           "critting it pays for the next one."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "strafing_shot", "Strafing Shot",
    "Your critical strikes splash 25% of the damage onto up to 3 nearby "
    "enemies as shadow damage.",
    2, -4,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "ability_filter": RANGED,
          "splash_damage": {"pct": 0.25, "max_targets": 3,
                            "school": "shadow"}},
    connect=["arbalest_mastery"],
    source="CoA: 'Critical strikes with ranged abilities now spread Tormentor "
           "to a nearby enemy.' Spreading a DoT to a new target is not a "
           "payload this engine has - apply_effect lands on the trigger's "
           "target, not on a neighbour - so it is built as splash_damage, "
           "which is the closest honest reading of 'your crits hurt the "
           "things next to it'. The school is set to shadow so it matches "
           "Tormentor's flavour rather than arriving as untyped damage. Was "
           "dot_damage +3% per rank, which is not this talent."))

N.append(node(
    "silver_bolts", "Silver Bolts",
    "Increases the damage of Heartseeking Bolt and Damnation by 15%.",
    2, -2,
    effects={f"ability_{a}_damage": 0.15 for a in BIG_SHOTS},
    connect=["relentless"],
    source="CoA: 'Damage dealt by Heartseeking Bolt and Damnation is "
           "increased by 15%, doubled against Undead or Demons or enemies "
           "affected by Shadow Trap.' The doubling is dropped: no effect key "
           "reads the target's creature type, and none reads whether it "
           "carries a specific debuff. CoA's base 15% kept rather than "
           "splitting the difference, since the condition is what the "
           "doubling was priced for."))

N.append(node(
    "tormenting_the_tormented", "Tormenting the Tormented",
    "Increases the critical strike chance of Tormentor by 15%.",
    2, 0,
    effects={"ability_witch_hunter_tormentor_crit": 15.0},
    connect=["relentless"],
    source="CoA: 'Level 50 Passive. Your Tormentor can now critically "
           "strike.' Whether a DoT's ticks can crit is an engine-wide rule "
           "rather than a per-character bonus, so there is nothing for a "
           "talent effect to set. Rebuilt as crit chance on the ability, "
           "which is the same intent - make Tormentor's damage swing - "
           "through a key that is live."))

N.append(node(
    "witching_bolt", "Witching Bolt",
    "Increases the critical strike chance of Damnation by 15%.",
    2, 2,
    effects={"ability_witch_hunter_damnation_crit": 15.0},
    connect=["resourceful_pursuit"],
    source="CoA: 'Increases the critical strike chance of Damnation against "
           "Undead and Demons by 25%.' The creature-type condition has no "
           "key, so it is dropped and 25% is cut to 15% for applying "
           "always. Pairs deliberately with Neverending Pursuit at tier 1: "
           "more Damnation crits is more Focus back."))

N.append(node(
    "enchanted_bolts", "Enchanted Bolts",
    "Increases your spell damage by 5% and your armor penetration by 10%.",
    2, 4,
    effects={"spell_damage": 0.05, "armor_penetration_pct": 10.0},
    connect=["resourceful_pursuit"],
    source="CoA verbatim: 'Increases your Magic damage dealt by 5% and your "
           "Armor penetration by 10%.' armor_penetration_pct takes "
           "percentage POINTS while spell_damage beside it is a fraction, "
           "which is exactly the kind of pairing that ships at 100x or "
           "1/100th if taken on trust."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "arbalest_mastery", "Arbalest Mastery",
    "Each Witchbane you fire makes your damage 5% stronger for 3 turns, "
    "stacking 10 times.",
    3, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_witchbane"],
          "apply_effect": {"effect_id": "witch_hunter_arbalest_mastery",
                           "name": "Arbalest Mastery", "effect_type": "buff",
                           "duration": 3, "max_stacks": 10,
                           "stat_mods": {"damage_dealt_pct": 5.0},
                           "on_target": False}},
    connect=["heavy_crossbows"],
    source="CoA: 'Each subsequent shot of a Witchbane cast deals 15% more "
           "damage, up to a maximum of 150%.' CoA's version ramps WITHIN one "
           "cast, which this engine cannot express - an ability resolves in "
           "one step and nothing counts its individual shots. Rebuilt as a "
           "ramp ACROSS casts, which keeps the identity (Witchbane gets "
           "better the longer you fire it) and lands on the same 150% "
           "ceiling at 10 stacks. Status stat_mods multiply by stacks."))

N.append(node(
    "relentless", "Relentless",
    "Increases the damage of Witchbane by 20%.",
    3, -2,
    effects={"ability_witch_hunter_witchbane_damage": 0.20},
    connect=["heavy_crossbows"],
    source="CoA: 'Allows Witchbane to hit an additional nearby enemy.' No "
           "key adds a target to an ability - it is enemy_aoe or it is not, "
           "and witch_hunter_witchbane is a single-target dot - so this is "
           "repriced as damage rather than authored as an aoe_damage bonus "
           "that would apply to nothing. Was aoe_damage +6% per rank, which "
           "did precisely that: Witchbane is not enemy_aoe, so it scaled "
           "other abilities entirely."))

N.append(node(
    "resourceful_pursuit", "Resourceful Pursuit",
    "Reduces the Focus cost of Tormentor and Damnation by 20%.",
    3, 0,
    effects={"ability_witch_hunter_tormentor_cost_pct": 0.20,
             "ability_witch_hunter_damnation_cost_pct": 0.20},
    connect=["bringing_the_law"],
    source="CoA verbatim but for the resource: 'Reduces the Rage cost of "
           "Tormentor and Damnation by -20%.' The previous tree used the FLAT "
           "_cost keys (3 Focus), which is a different and much smaller thing "
           "on a 100-point pool."))

N.append(node(
    "bringing_the_law", "Bringing the Law",
    "Increases the critical strike chance of Shadowblast by 10%.",
    3, 2,
    effects={"ability_witch_hunter_shadowblast_crit": 10.0},
    connect=["evasive"],
    source="CoA verbatim. Shadowblast is the filler shot, so crit on it "
           "feeds Strafing Shot's splash at tier 2."))

N.append(node(
    "slinging_bolts", "Slinging Bolts",
    "Your ranged damage has an 8% chance to make your next hits 30% "
    "stronger for 2 turns.",
    3, 4,
    proc={"trigger": "on_damage_cast", "chance": 8, "icd": 2,
          "ability_filter": RANGED,
          "apply_effect": {"effect_id": "witch_hunter_slinging_bolts",
                           "name": "Slinging Bolts", "effect_type": "buff",
                           "duration": 2, "max_stacks": 1,
                           "stat_mods": {"damage_dealt_pct": 30.0},
                           "on_target": False}},
    connect=["evasive"],
    source="CoA: 'Level 40 Passive. Direct ranged damage dealt now has an 8% "
           "chance to grant you Slinging Bolts. Can only occur once every 5 "
           "sec. Slinging Bolts: Your next Damnation is usable regardless of "
           "the target's current health.' Nothing suppresses an ability's own "
           "usability gate from a buff, and Frontier's Damnation carries no "
           "health gate to lift in the first place - so the payout becomes "
           "damage. CoA's 8% kept, and its once-every-5-sec becomes icd 2."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "evasive", "Evasive",
    "Twilight Frenzy leaves you taking 20% less damage for 2 turns.",
    4, -3,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_twilight_frenzy"],
          "apply_effect": {"effect_id": "witch_hunter_evasive",
                           "name": "Evasive", "effect_type": "buff",
                           "duration": 2, "max_stacks": 1,
                           "stat_mods": {"damage_taken_pct": -0.20},
                           "on_target": False}},
    connect=["contract_killing"],
    source="CoA verbatim: 'Twilight Frenzy now grants you 20% reduced damage "
           "taken while active.' Built as a window off the cast, since "
           "'while active' needs a channel and channels do not exist here. "
           "NEGATIVE reduces, and damage_taken_pct is the ONE status "
           "stat_mod the engine reads raw rather than dividing by 100 - the "
           "physical_ and magic_ variants beside it ARE divided, which is "
           "why this is -0.20 and Douse's magic_damage_taken_pct was 4.0. "
           "Authored -20.0 first, having written that sentence and then not "
           "followed it - which is 2000% damage reduction. audit_talents "
           "caught it; nothing in the game would have, since the value is "
           "perfectly valid and simply makes the Witch Hunter immortal for "
           "two turns after every Twilight Frenzy."))

N.append(node(
    "escape_artist", "Escape Artist",
    "Daring Escape resets the cooldown of Vault and returns 10 Focus.",
    4, -1,
    proc={"trigger": "on_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_daring_escape"],
          "reset_cooldown": ["witch_hunter_vault"],
          "grant_resource": {"resource": "focus", "amount": 10}},
    connect=["contract_killing"],
    source="CoA verbatim but for the resource: 'Your Daring Escape now resets "
           "the cooldown of Vault and generates 10 Rage.' Rage -> Focus. "
           "on_cast rather than on_damage_cast, because Daring Escape is a "
           "self buff and deals no damage - filtering a damage trigger to it "
           "would have been a proc that never fired, which is the quiet way "
           "this kind of node dies."))

N.append(node(
    "crossbow_frenzy", "Crossbow Frenzy",
    "Increases your haste by 5% and your dodge by 5%.",
    4, 1,
    effects={"haste": 5.0, "dodge": 5.0},
    connect=["dead_and_gone"],
    source="CoA: 'While Twilight Frenzy is active, your movement speed is now "
           "increased by 40%.' Movement speed does not exist and there is no "
           "'while X is active' gate for an effect key, so nothing of this "
           "talent survives as written. Kept as the thing a spinning "
           "crossbowman should get - speed and evasion - rather than dropped, "
           "because the tier needs a plain pick among four procs."))

N.append(node(
    "witchbane_mastery", "Hunter's Cadence",
    "Increases the damage your damage-over-time effects deal by 10%.",
    4, 3,
    effects={"dot_damage": 0.10},
    connect=["dead_and_gone"],
    source="Not a CoA node by this name - it carries CoA's Rapid ('your "
           "Witchbane now deals its full damage over 1 second shorter "
           "period'), which is not buildable: Witchbane is a dot and its "
           "ticks are per-turn, so there is no sub-turn period to compress. "
           "Rebuilt as DoT damage, which is what compressing a DoT's "
           "duration actually buys you. Renamed rather than kept as 'Rapid' "
           "so the tooltip is not promising a timing change it cannot make."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "contract_killing", "Contract Killing",
    "Increases all damage you deal by 10%.",
    5, -3,
    effects={"all_damage": 0.10},
    connect=["bounty_hunter"],
    source="CoA: 'Increases damage dealt against enemies above 75% health and "
           "below 35% health by 15%.' Both windows are recipient-health "
           "conditions on DAMAGE, and the only recipient-health key in the "
           "engine is low_health_healing_pct, which is heal-side. So the "
           "condition is dropped and 15% cut to 10% for applying to "
           "everything - CoA's version misses the middle of a health bar "
           "entirely, which is most of a boss fight."))

N.append(node(
    "heavy_crossbows", "Heavy Crossbows",
    "Increases the damage of Darkslayer by 50%, and your Heartseeking Bolt "
    "and Darkslayer have a 25% chance to strike again.",
    5, -1,
    effects={"ability_witch_hunter_darkslayer_damage": 0.50},
    proc={"trigger": "on_damage_cast", "chance": 25, "icd": 0,
          "ability_filter": ["witch_hunter_heartseeking_bolt",
                             "witch_hunter_darkslayer"],
          "extra_attack": True},
    connect=["bounty_hunter"],
    source="CoA verbatim: 'Increases the damage of Darkslayer by 50%, but "
           "increases its cast time by 0.5 sec. Your Heartseeking Bolt and "
           "Darkslayer now have a 25% chance to strike an additional time.' "
           "Both halves built; extra_attack is the live payload for the "
           "second. NOTE THE LOST DRAWBACK: there are no cast times here, so "
           "the +0.5 sec penalty has nothing to apply to and this node is "
           "strictly better than CoA's. Flagged rather than silently "
           "pocketed - if the tier needs tuning later, this is the node that "
           "gained something in translation."))

N.append(node(
    "dead_and_gone", "Dead and Gone",
    "Increases the duration of Pavise by 1 turn and reduces its cooldown by "
    "30%.",
    5, 1, ranks=2,
    effects={"ability_witch_hunter_pavise_duration": 1,
             "ability_witch_hunter_pavise_cooldown_pct": 0.15},
    connect=["bounty_hunter"],
    source="CoA: 'Your Bolt and Dash now affects an additional use of a "
           "Heartseeking Bolt. Your Pavise now lasts 2 additional sec and has "
           "a -30 sec reduced cooldown.' The Bolt and Dash half needs a "
           "charge counter, which does not exist. The Pavise half ports, with "
           "the cooldown as a percentage because cooldowns are counted in "
           "turns. Positive is the reduction direction."))

N.append(node(
    "slayer", "Slayer",
    "Increases your critical strike chance by 3%.",
    5, 3,
    effects={"crit_chance_physical": 3.0},
    connect=["bounty_hunter"],
    source="CoA: 'Increases critical strike chance of all party and raid "
           "members by 3%. Does not stack with similar effects. In addition, "
           "increases your critical strike chance by 3%.' The raid half has "
           "no mechanism - a talent effect applies to its own character - so "
           "the description says 'your' rather than promising the party a "
           "buff it will not get. crit_chance_physical is a PERCENT."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "bounty_hunter", "Bounty Hunter",
    "Darkslayer and Witchbane mark your quarry, making your next shots 15% "
    "stronger for 3 turns, stacking twice.",
    6, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_darkslayer",
                             "witch_hunter_witchbane"],
          "apply_effect": {"effect_id": "witch_hunter_bounty_hunter",
                           "name": "Bounty Hunter", "effect_type": "buff",
                           "duration": 3, "max_stacks": 2,
                           "stat_mods": {"damage_dealt_pct": 15.0},
                           "on_target": False}},
    source="CoA: 'Casting Darkslayer or Witchbane now applies a stack of "
           "Bounty Hunter to you for 8 sec, which can be consumed by casting "
           "Heartseeking Bolt to deal an additional Physical damage, stacking "
           "2 times.' The build-and-spend shape is half buildable: the "
           "building is a stacking self buff, but CONSUMING it on a specific "
           "cast is not - consumes_stacks_of reads the caster's own stacks "
           "and only extends a DoT's duration, and Heartseeking Bolt is "
           "direct damage. So the stacks pay out continuously instead of in "
           "one burst, which keeps the rotation CoA is after (open with "
           "Darkslayer and Witchbane, then fire the big shot) without a "
           "tooltip promising a detonation that never comes. CoA's 2 stacks "
           "and 8 sec (3 turns) kept."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. See tools/talent_ranks.py - it rescales so a
# ranked node lands on exactly the ceiling it had at one rank. Three ranks
# for everything that can take them; the tier 6 capstone stays a single
# decisive pick, and there are no unlock nodes in this tree (no Witch Hunter
# ability carries requires_talent).
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
    print(f"Witch Hunter Boltslinger: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
