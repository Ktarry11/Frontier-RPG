#!/usr/bin/env python3
"""Rebuild Ranger's Brigand tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_ranger_brigand.py [--check]

SOURCE: data/reference/coa_worksheets/ranger.md - 39 real Brigand talents.
Role: DPS (melee). Brigand was 23 nodes with 7 procs.

CoA's Focus is our archery_points (Ranger's PRIMARY pool, five
generators), so Focus costs, refunds and generation all port. CoA's
Advantage is a stack count and nothing reads one, so the per-stack scaling
on Assault, Dirty Blades, Quills, Rub It In and Stonemason's Secret is
dropped - the stacking EFFECTS are real, only the read is impossible.

WEAPON TYPE IS NOT READABLE, and Brigand is the spec that cares most.
Eleven of CoA's 39 talents are conditional on a polearm or daggers being
equipped (Beatdown, Trueshot Lodge Training, Ambuscade, Polearm Craft, Tip
of the Spear, Marked for Death, Assault, Dirty Blades, Viper's Bite...).
Nothing in this engine reads weapon type at all, and there is no off-hand
damage key either, so every one of those conditions is dropped and the
node priced for the unconditional version. Each affected node says so.

QUICK-WITTED IS WHY THIS TREE IS WORTH BUILDING: on_avoid is a live
trigger, and Kyle had creature avoidance added on 5 Nov 2026, so a melee
Ranger who dodges now punishes the attacker. Note the trap asserted in
main(): an avoided attack deals ZERO damage, so leech_pct and bonus_pct
yield nothing on that trigger while looking correct - it uses damage_flat.

ARCHERY OWNS low_health_threshold_pct for the class at CoA's 20%, so
Marked for Death and Dastardly use low_health_damage_pct and inherit it
rather than setting their own. Enforced by tools/qa_summing_thresholds.py.

NOT BUILDABLE: Highwayman's "while behind your target" and Outmaneuver's
teleport-and-decoy (no positioning); Rub It In and Sniper's Focus observe a
resource SPEND, which nothing does; Throatpunch needs an interrupt key;
Lacerations asks for a dot to crit, which they never do; Wild Man and
Quills add targets to an ability; Instinctual Combatant guarantees crits on
specific abilities; Dirty Fighter's CoA payload is the literal string
"$80", so their data is broken there.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/ranger_brigand.json"

TREE = {
    "spec_name": "Ranger Brigand",
    "tree_id": "ranger_brigand",
    "description": ("Close work - bleeds, dirty blades, and a counterpunch "
                    "for anything that misses you."),
    "_source_note": (
        "Rebuilt 6 Nov 2026 from the 39 real CoA Brigand talents (role "
        "DPS, melee). Eleven CoA talents are conditional on weapon type "
        "and nothing reads weapon type, so those conditions are all "
        "dropped. Advantage stacks are unreadable. Quick-Witted ports "
        "verbatim off on_avoid, which only became worth building after "
        "creature avoidance landed on 5 Nov 2026. Archery owns the class "
        "execute threshold."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20,
                          "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"ranger_brigand_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"ranger_brigand_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


WEAPON = ("CoA gates this on a weapon type (polearm or daggers). NOTHING "
          "READS WEAPON TYPE anywhere in this engine, and there is no "
          "off-hand damage key either, so the condition is dropped and the "
          "node priced for the unconditional version. Eleven of Brigand's "
          "39 CoA talents carry such a gate.")

ADVANTAGE = ("CoA scales this off ADVANTAGE STACKS; the stacking effect is "
             "real (max_stacks is honoured) but NOTHING READS A STACK "
             "COUNT, so the per-stack scaling is dropped for the flat value "
             "CoA's typical count comes to.")

N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "banditry", "Banditry",
    "Increases your critical strike chance by 4% and reduces all your "
    "ability costs by 10%.",
    0, -4,
    effects={"crit_chance_physical": 4.0, "all_ability_cost_pct": 0.10},
    connect=["close_quarters"],
    source="CoA over 2 ranks: 'Increases your critical strike chance by 2% "
           "and Focus regeneration by 15%.' The crit ports (doubled). "
           "FOCUS REGENERATION HAS NO KEY: energy_regen, energy_regen_pct "
           "and resource_regen_pct are all dead data, authored by several "
           "talents and read by nothing. Repriced as a cost reduction, "
           "which reaches the same place - more shots per pool - through a "
           "key that works. all_ability_cost_pct is a FRACTION where "
           "POSITIVE MEANS A REDUCTION. Was a pure scalar on our side."))

N.append(node(
    "close_quarters", "Close Quarters",
    "Increases your attack power by 6% and your Agility by 6%.",
    0, -2,
    effects={"attack_power_pct": 6.0, "agility_pct": 6},
    connect=["jagged_cuts", "beatdown"],
    source="CoA over 2 ranks: 'Increases your attack power and Agility by "
           "3%.' PORTS EXACTLY, doubled for the two ranks. BOTH KEYS ARE "
           "PERCENTAGE POINTS - and I first authored attack_power_pct as "
           "0.06, assuming it was a fraction like attack_power's cousins, "
           "which audit_talents caught as '0.02%, not 2.0%'. That is the "
           "second time in one night the audit corrected a convention I "
           "guessed from the key name (the other was "
           "stun_duration_reduction_pct on Chronomancer's Timemage, which "
           "IS a fraction). There is no rule to infer it from: the audit is "
           "the only reliable check. Was a pure scalar on our side."))

N.append(node(
    "jagged_cuts", "Jagged Cuts",
    "Increases the damage of Toxic Dart and Ravage by 25% and their "
    "duration by 2 turns.",
    0, 0,
    effects={"ability_ranger_toxic_dart_damage": 0.25,
             "ability_ranger_ravage_damage": 0.25,
             "ability_ranger_toxic_dart_duration": 2,
             "ability_ranger_ravage_duration": 2},
    connect=["knuckleduster"],
    source="CoA: 'Increases the damage and duration of Toxic Dart and "
           "Ravage by 25%.' PORTS EXACTLY, both halves and both abilities - "
           "duration as a flat 2 turns since the key is an integer. BOTH "
           "ARE REAL DAMAGE INCREASES: abilities.py:2777 derives per-turn "
           "damage from the ability's OWN base duration, so a talent "
           "extension adds TICKS at full value rather than thinning a fixed "
           "total. Both dots go 3 -> 5 turns. SMALL INTEGERS IN TURNS, so "
           "spread() refuses to rank this node - correct, since a third of "
           "a turn per rank reads as nothing. Was a pure scalar on our "
           "side."))

N.append(node(
    "dice_games", "Dice Games",
    "Increases the critical strike chance of Wild Strike and Assault by "
    "10%.",
    0, 2,
    effects={"ability_ranger_wild_strike_crit": 10.0,
             "ability_ranger_assault_crit": 10.0},
    connect=["bounty_hunter"],
    source="CoA: 'Increases the critical strike chance of Wild Strike and "
           "Assault by 5%.' PORTS EXACTLY, both abilities, doubled. Wild "
           "Strike generates 14 Focus - the second-biggest generator - so "
           "this feeds Archery Master's crit-to-Focus loop too. Per-ability "
           "crit keys are PERCENTAGE POINTS. Was a pure scalar on our "
           "side."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "knuckleduster", "Knuckleduster",
    "Your attacks restore 6 Focus.",
    1, 0,
    proc={"trigger": "on_weapon_swing", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "archery_points", "amount": 6}},
    connect=["excessive_but_necessary", "highwayman"],
    source="CoA: 'Periodic damage dealt now generates 5 Focus.' CoA fires "
           "this off dot TICKS, which are not a trigger - "
           "status_effects.py:914 ticks on the recipient with no caster "
           "handle - so it is re-pointed to on_weapon_swing, the melee "
           "equivalent. archery_points IS CoA's Focus. grant_resource "
           "routes through the same gain_resource() the five generators "
           "use, so the cap holds. FLAT `amount`; there is no pct_max."))

N.append(node(
    "beatdown", "Beatdown",
    "Your attacks have a 20% chance to find a fault in the target's "
    "defenses, increasing your armor penetration for 3 turns.",
    1, -2,
    effects={"armor_penetration": 60},
    proc={"trigger": "on_weapon_swing", "chance": 20, "icd": 1,
          "apply_effect": {"effect_id": "beatdown", "name": "Beatdown",
                           "effect_type": "buff", "duration": 3,
                           "stat_mods": {"attack_power": 70},
                           "dispel_type": None, "on_target": False}},
    connect=["highwayman"],
    source="CoA level 20 passive: 'Auto attacks now have a 5% chance to "
           "reveal a fault in the enemy's defenses, causing your next "
           "instance of Physical ability damage to ignore Armor. Chance "
           "increased by 15% while wielding a polearm.' " + WEAPON + " "
           "'Your NEXT instance ignores armor' cannot be built - nothing "
           "consumes a one-shot armour bypass the way "
           "bypass_execute_threshold does for execute gates - so the node "
           "carries a flat armor_penetration passive plus a short attack "
           "power window on proc, which is where 'ignore armour once' lands "
           "numerically. armor_penetration is a FLAT rating; "
           "attack_power inside a status effect is FLAT too "
           "(Monster.ability_power_bonus's caster-side twin). Was a pure "
           "scalar on our side."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "excessive_but_necessary", "Excessive But Necessary",
    "Reduces the cooldown of Elude, Knockout and Cutthroat by 35%.",
    2, -2,
    effects={"ability_ranger_elude_cooldown_pct": 0.35,
             "ability_ranger_knockout_cooldown_pct": 0.35,
             "ability_ranger_cutthroat_cooldown_pct": 0.35},
    connect=["bounty_hunter"],
    source="CoA: 'Reduces the cooldown of Elude and Knockout by 4 sec.' "
           "Both are 6-turn cooldowns, so 4 sec is about 35% there. "
           "Extended to Cutthroat from CoA's Stalker ('Reduces the cooldown "
           "of Cutthroat by -15 sec, but reduces the range by -10 yds'), "
           "whose drawback is a range mechanic and therefore free here - "
           "flagged rather than quietly pocketed. *_cooldown_pct keys are "
           "FRACTIONS where POSITIVE MEANS A REDUCTION; talented_cooldown "
           "floors at 1 turn."))

N.append(node(
    "bounty_hunter", "Bounty Hunter",
    "Your attacks have a 30% chance to mark the target, increasing the "
    "damage they take from you by 15% for 3 turns.",
    2, 1,
    proc={"trigger": "on_weapon_swing", "chance": 30, "icd": 0,
          "apply_effect": {"effect_id": "bounty_hunter",
                           "name": "Bounty Hunter",
                           "effect_type": "debuff", "duration": 3,
                           "stat_mods": {"damage_taken_pct": 0.15},
                           "dispel_type": None, "on_target": True}},
    connect=["ambuscade"],
    source="CoA: 'Damage dealt by Flank and Rusty Shiv now increases the "
           "target's damage taken from your Advantage spenders by 25% for 8 "
           "sec.' The debuff ports; the two-ability trigger does not (no "
           "per-ability proc trigger) and 'from your Advantage spenders' "
           "cannot be narrowed, so it applies to all your damage at 15% "
           "instead of 25%. 8 sec -> 3 turns. Folded in CoA's 'Tactical' "
           "Advantage, which does the same thing off Knockout and "
           "Bushwhack. CAREFUL: bare damage_taken_pct is read RAW ON BOTH "
           "SIDES, so 0.15 is 15% and authoring 15 would be +1500%. "
           "Asserted in main()."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "highwayman", "Highwayman",
    "Your critical strikes increase your haste by 15% for 2 turns.",
    3, -2,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "apply_effect": {"effect_id": "highwayman", "name": "Highwayman",
                           "effect_type": "buff", "duration": 2,
                           "stat_mods": {"haste": 15.0},
                           "dispel_type": None, "on_target": False}},
    connect=["pilfering"],
    source="CoA: 'Direct critical strikes while behind your target increase "
           "your haste by 15% for 5 seconds, or for your next 2 attacks.' "
           "PORTS ALMOST EXACTLY - the haste, the value and the window all "
           "survive. Only 'while behind your target' goes: there is no "
           "positioning in this engine at all. 5 sec -> 2 turns, which also "
           "happens to match CoA's own 'next 2 attacks' alternative. haste "
           "is PERCENTAGE POINTS."))

N.append(node(
    "ambuscade", "Ambuscade",
    "Increases the damage of Skullpiercer and Flank by 35% and your "
    "physical damage by 4%.",
    3, 1,
    effects={"ability_ranger_skullpiercer_damage": 0.35,
             "ability_ranger_flank_damage": 0.35,
             "physical_damage": 0.04},
    connect=["quick_witted"],
    source="CoA: 'Increases the base damage of Skullpiercer and Flank by "
           "20%, plus an additional 35% if you have a polearm equipped.' "
           + WEAPON + " The two values are merged at 35% rather than "
           "stacking to 55%, since the condition is gone. The small global "
           "comes from CoA's Trueshot Lodge Training ('+25% off-hand weapon "
           "damage; while wielding a polearm your Physical damage is "
           "increased by 3%'), which fails on both halves - no off-hand key "
           "and no weapon type - so only its unconditional intent lands. "
           "Was a pure scalar on our side."))

N.append(node(
    "focused_fighter", "Focused Fighter",
    "Reduces the cost of Flank, Wild Strike and Assault by 20%.",
    3, 3,
    effects={"ability_ranger_flank_cost_pct": 0.20,
             "ability_ranger_wild_strike_damage": 0.20,
             "ability_ranger_assault_cost_pct": 0.20},
    connect=["marked_for_death"],
    source="CoA: 'Reduces the Focus cost of Flank, Blackjack, and Wild "
           "Strike by -10%.' Blackjack is not in our Ranger book, so "
           "Assault takes its place - it is the spec's execute and the "
           "most expensive thing in the rotation. Doubled to 20%. CoA's "
           "Focus is our archery_points, so these are real cost "
           "reductions on a real pool. FRACTIONS where POSITIVE MEANS A "
           "REDUCTION. Was a pure scalar on our side."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "quick_witted", "Quick-Witted",
    "Avoiding an attack stabs the attacker and slows their attacks for 3 "
    "turns.",
    4, 0,
    proc={"trigger": "on_avoid", "chance": 100, "icd": 0,
          "damage_flat": 85, "school": "physical",
          "apply_effect": {"effect_id": "quick_witted",
                           "name": "Quick-Witted",
                           "effect_type": "debuff", "duration": 3,
                           "stat_mods": {"attack_power": -80},
                           "dispel_type": None, "on_target": True}},
    connect=["pilfering"],
    source="CoA: 'Avoiding an attack now causes you to quickly stab an "
           "enemy with one of the arrows from your quiver, dealing Physical "
           "damage and reducing their attack speed by -20% for 8 seconds.' "
           "PORTS ALMOST VERBATIM, and it is the reason this tree is worth "
           "building: on_avoid is a live trigger covering dodge, parry and "
           "block, and it only became meaningful when Kyle had creature "
           "avoidance added on 5 Nov 2026. THE ATTACK-SPEED HALF BECOMES "
           "FLAT ATTACK POWER: there is no caster-side speed debuff key, "
           "and attack_power is one of only eight status stat_mods a "
           "monster reads (and it is FLAT - 'Flat damage/healing swing from "
           "active buffs and debuffs'). damage_flat RATHER THAN leech_pct "
           "IS LOAD-BEARING: an avoided attack deals ZERO damage, so an "
           "amount-reading payload would deal and heal nothing while "
           "looking correct. Asserted in main(). 8 sec -> 3 turns."))

N.append(node(
    "pilfering", "Pilfering",
    "Increases the damage of Dirty Blades by 10%, and your attacks have a "
    "30% chance to heal you for 20% of the damage dealt.",
    4, 2,
    effects={"ability_ranger_dirty_blades_potency": 0.10},
    proc={"trigger": "on_weapon_swing", "chance": 30, "icd": 0,
          "leech_pct": 20},
    connect=["tip_of_the_spear"],
    source="CoA: 'Adds 10% to the damage dealt by Dirty Blades and causes "
           "its damage dealt to heal you equal to 50% of the value.' PORTS "
           "ALMOST EXACTLY. leech_pct is one of only three proc payloads "
           "that READ the triggering hit's amount, so '% of the damage "
           "dealt' is literally what it computes - and this is the right "
           "trigger for it, unlike Quick-Witted above where the amount is "
           "always zero. The Dirty-Blades scoping on the leech goes (no "
           "per-ability proc trigger) and 50% drops to 20% at a 30% chance "
           "in exchange, since it now fires off every swing rather than "
           "during one short window."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "tip_of_the_spear", "Tip of the Spear",
    "Your attacks have a 15% chance to strike an additional time.",
    5, 0,
    proc={"trigger": "on_weapon_swing", "chance": 15, "icd": 0,
          "extra_attack": True},
    connect=["dastardly"],
    source="CoA: 'While you have a polearm equipped, your Wild Strike now "
           "has a 15% chance to strike 3 additional times.' " + WEAPON + " "
           "`extra_attack` IS A BOOLEAN GIVING EXACTLY ONE EXTRA ATTACK - "
           "it cannot be set to three, and there is no count field - so "
           "CoA's 3 becomes 1 at the same 15% chance. Flagged rather than "
           "faked: the description promises one strike, which is what "
           "happens. The Wild-Strike scoping also goes (no per-ability proc "
           "trigger)."))

N.append(node(
    "marked_for_death", "Marked for Death",
    "Increases your damage against enemies below 20% health by 25%.",
    5, 2,
    effects={"low_health_damage_pct": 0.25},
    connect=["dastardly"],
    source="CoA: 'While you have daggers equipped, direct critical strikes "
           "on enemies below 35% health now have a chance to allow the use "
           "of abilities as if you were in Elude for 5 seconds.' " + WEAPON
           + " 'As if you were in Elude' has no mechanism either - nothing "
           "grants a pseudo-state that other abilities test. What survives "
           "is the execute framing, built with low_health_damage_pct (the "
           "key added 6 Nov 2026 for the 48 CoA talents across 18 classes "
           "worded this way). THIS NODE DOES NOT SET "
           "low_health_threshold_pct: Archery's One Shot, One Kill owns it "
           "for the whole class at CoA's 20%, that key SUMS across talents, "
           "and a character can spend in several Ranger trees - a second "
           "setter would push the window to 40%. Asserted in main() and "
           "enforced class-wide by tools/qa_summing_thresholds.py. Was a "
           "pure scalar on our side."))

N.append(node(
    "barbed_quills", "Barbed Quills",
    "Your attacks have a 35% chance to open a bleed dealing damage over 3 "
    "turns, stacking up to 4 times.",
    5, -2,
    proc={"trigger": "on_weapon_swing", "chance": 35, "icd": 0,
          "apply_effect": {"effect_id": "barbed_quills",
                           "name": "Barbed Quills",
                           "effect_type": "dot", "duration": 3,
                           "potency": 24, "damage_school": "physical",
                           "max_stacks": 4, "dispel_type": None,
                           "on_target": True}},
    connect=["dastardly"],
    source="CoA: 'Damage dealt by Wild Strike and Quills will now tear into "
           "enemies, causing them to bleed for 69 to 75 Physical damage "
           "over 9 sec, stacking 4 times. Damage dealt by Quills now "
           "spreads your periodic effects to 5 enemies within 10 yds and "
           "extends their duration by 2 sec.' The bleed and its 4 stacks "
           "port; the spread clause does not (nothing copies an effect to "
           "other targets, and no payload extends a LIVE effect's "
           "duration). 9 sec -> 3 turns. A proc-applied dot carries "
           "`potency` as PER-TURN damage - 24 a turn, 72 per stack, 288 at "
           "four - where an ABILITY's effect_value is the total and gets "
           "divided."))

N.append(node(
    "assassin", "Assassin",
    "Increases the duration of Knockout, Crippling Shot and Throatpunch by "
    "1 turn, and the healing of Survival Potion by 25%.",
    1, 2,
    effects={"ability_ranger_knockout_duration": 1,
             "ability_ranger_crippling_shot_duration": 1,
             "ability_ranger_throatpunch_duration": 1,
             "ability_ranger_survival_potion_healing": 0.25},
    connect=["dice_games"],
    source="CoA has TWO talents named Assassin in this tree: 'Increases the "
           "duration of Knockout and Crippling Shot by 1 sec' and "
           "'Increases the effectiveness of Instinct by 25%'. Merged, since "
           "a duplicate node NAME is rejected by main(). The durations port "
           "as flat turns; Throatpunch added as the third control ability "
           "of the same shape. Instinct is a restore_resource ability with "
           "no healing or damage key to scale, so its 25% is re-pointed to "
           "Survival Potion, the spec's actual heal. SMALL INTEGERS IN "
           "TURNS, so spread() refuses to rank this node."))

N.append(node(
    "wild_man", "Wild Man",
    "Increases the damage of Wild Strike by 30% and of Quills by 25%.",
    2, 3,
    effects={"ability_ranger_wild_strike_damage": 0.30,
             "ability_ranger_quills_damage": 0.25},
    connect=["focused_fighter"],
    source="CoA: 'Your Wild Strike now strikes 2 additional nearby enemies, "
           "but deals reduced damage with each enemy struck.' NOTHING ADDS "
           "TARGETS TO AN ABILITY - no effect key and no proc payload "
           "touches an ability's target count, which also killed Quills' own "
           "per-stack target scaling and Reaper Soul's Ghastly Hilt - so "
           "both the upside and the stated drawback are dropped together "
           "and the node becomes flat damage. Extended to Quills, whose CoA "
           "talent fails the same way. Wild Strike generates 14 Focus. Was "
           "a pure scalar on our side."))

N.append(node(
    "lacerations", "Lacerations",
    "Increases the damage of your periodic effects by 18%.",
    4, -2,
    effects={"dot_damage": 0.18},
    connect=["quick_witted"],
    source="CoA level 40 passive: 'Allows the periodic damage dealt by "
           "Ravage to critically strike.' NOT BUILDABLE: dot and hot ticks "
           "NEVER roll crit in this engine, and there is no key to let them "
           "- status_effects.py applies a tick as a bare take_damage call "
           "with no crit roll anywhere in the path. CoA leans on this "
           "repeatedly (Archery's Bleeding Edge, Chronomancer's shared "
           "Impeccable Timing) and it fails every time. Repriced as "
           "dot_damage, which is what letting a bleed crit amounts to "
           "numerically and reaches every periodic effect this spec "
           "applies. A FRACTION. Was a pure scalar on our side."))

N.append(node(
    "underhanded", "Underhanded",
    "Increases your attack power by 15% of your Agility.",
    3, -4,
    effects={"attack_power_from_agility_pct": 0.15},
    connect=["highwayman"],
    source="CoA over 2 ranks: 'Increases the attack power scaling of "
           "Skullpiercer by 15%.' A per-ability attack-power SCALING "
           "coefficient is not something any key reaches - the ability keys "
           "are _damage, _healing, _crit, _crit_damage, _cost, _cooldown, "
           "_duration and _potency, and none of them touch how an ability "
           "scales off a stat. Rebuilt as a real conversion instead: "
           "attack_power is in STAT_CONVERSION_TARGETS and agility in "
           "SOURCES, so a Brigand turning Agility into attack power is "
           "legal and reaches every ability rather than one. A FRACTION. "
           "Was a pure scalar on our side."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "dastardly", "Dastardly",
    "Increases your critical damage by 20%, your damage against enemies "
    "below 20% health by a further 25%, and your periodic damage by 15%.",
    6, 0,
    effects={"crit_damage_physical": 0.20,
             "low_health_damage_pct": 0.25,
             "dot_damage": 0.15},
    source="CoA level 50 passive: 'Increases your critical damage dealt by "
           "15% on enemies above 80% health or below 20% health.' The "
           "below-20% half builds with low_health_damage_pct; THE ABOVE-80% "
           "HALF CANNOT - high_health_damage_threshold_pct is dead data, "
           "authored and read by nothing, which also killed Archery's "
           "Opportunist. There is no conditional CRIT key either, only "
           "conditional damage, so CoA's 'critical damage' half becomes an "
           "unconditional crit_damage_physical plus conditional ordinary "
           "damage. The dot_damage ties the capstone to the bleed theme "
           "Jagged Cuts and Barbed Quills build. This node does NOT set "
           "low_health_threshold_pct - Archery owns it at 20%, so this "
           "stacks to 50% execute damage with Marked for Death on the same "
           "window. Was a pure scalar on our side."))


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
        f"Ranger Archery's One Shot, One Kill owns low_health_threshold_pct "
        f"for this class at CoA's 20%, and the key SUMS across talents - a "
        f"second setter gives a Ranger spending in both trees a 40% window. "
        f"Found {setters}")

    AVOIDANCE = ("on_avoid", "on_parry", "on_dodge", "on_block")
    for n in TREE["nodes"]:
        proc = n.get("proc") or {}
        if proc.get("trigger") in AVOIDANCE:
            for payload in ("leech_pct", "bonus_pct", "smart_heal_pct"):
                assert payload not in proc, (
                    f"{n['talent_id']} uses {payload} on "
                    f"{proc['trigger']} - an avoided attack deals 0 damage, "
                    f"so it silently yields nothing. Use damage_flat / "
                    f"heal_flat / grant_resource / apply_effect")
        gr = proc.get("grant_resource")
        if gr:
            assert gr.get("resource") == "archery_points" and "amount" in gr, (
                f"{n['talent_id']} grant_resource must name archery_points "
                f"with a FLAT amount")
        mods = (proc.get("apply_effect") or {}).get("stat_mods") or {}
        if "damage_taken_pct" in mods:
            assert -1 < mods["damage_taken_pct"] < 1, (
                f"{n['talent_id']} damage_taken_pct={mods['damage_taken_pct']}"
                f" - read RAW on both sides, so 15 means +1500%")

    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Ranger Brigand: {len(ids)} nodes, {procs} with procs, {pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
