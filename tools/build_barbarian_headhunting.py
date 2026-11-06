#!/usr/bin/env python3
"""Rebuild Barbarian's Headhunting tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_barbarian_headhunting.py [--check]

SOURCE: data/reference/coa_worksheets/barbarian.md - 33 real Headhunting
talents. Role: DPS (thrown/ranged). Headhunting was 23 nodes with 8 procs.

Energy is the whole pool on both sides (Barbarian is
(ResourceType.ENERGY, None) and CoA's Barbarian spends Energy), so every
cost and refund talent lands on the pool it names - no translation, unlike
Felsworn's Energy/Felfury split or Ranger's Focus/Advantage.

BORN IN BLOOD IS THE SPEC'S HOOK AND IT IS A BUFF WE DO NOT HAVE. CoA's
Headhunting hangs six talents off it - Furious Berserker and Vengeance For
Zul'jin grant it, Savage and Mounting Fury extend it, Bloody Fighter adds a
stack, Brutal Form changes its tick rate. There is no barbarian_born_in_blood
ability, and even with one, "restoring 18 health and 12 Energy over 3
seconds" is a HoT plus a per-tick resource grant, and nothing observes a
dot or hot tick (status_effects.py:914 ticks on the recipient with no
caster handle). Those six collapse into two nodes that grant the health
and energy directly on a real trigger.

Brutality owns low_health_threshold_pct for the class at 0.35, matching
the execute_threshold_pct added to barbarian_decapitate on 6 Nov 2026.
Nothing here sets it. Enforced by tools/qa_summing_thresholds.py.

NOT BUILDABLE beyond the above: Skullseeker's "above 80% health" -
high_health_damage_threshold_pct is dead data and there is no above-health
conditional; Frothing Savage reads whether a target is bleeding, and
Manhunter whether it is a Humanoid, neither of which anything reads; Axe
Twirling, Spear Shards, Impaling Spear's shatter and Spite's multi-throw
all add targets to an ability, which nothing does; Berserker's escalating
proc chance needs a counter; Gurubashi Technique and Sen'jin's Guidance
transform one ability into another; Headhunting and Vital Spirit are cast
time and range; Guts Spilled is a sub-effect of Gutspiller with no separate
handle, so Payback and To The Bone retarget to the parent dot.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/barbarian_headhunting.json"

TREE = {
    "spec_name": "Barbarian Headhunting",
    "tree_id": "barbarian_headhunting",
    "description": ("Spears and axes at distance - bleeds that stack and "
                    "a throw that keeps coming back."),
    "_source_note": (
        "Rebuilt 6 Nov 2026 from the 33 real CoA Headhunting talents (role "
        "DPS, thrown). Energy is the whole pool on both sides, so the cost "
        "and refund talents need no translation. Six CoA talents hang off "
        "Born in Blood, a buff we do not have and whose per-tick resource "
        "restore would need a periodic trigger that does not exist; they "
        "collapse into two nodes granting health and energy on a real "
        "trigger. Brutality owns the class execute threshold."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20,
                          "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"barbarian_headhunting_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"barbarian_headhunting_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


BLOOD = ("CoA hangs this on BORN IN BLOOD, a buff that does not exist in "
         "our ability data - and whose own text ('restoring 18 health and "
         "12 Energy over 3 seconds') is a HoT plus a per-tick resource "
         "grant, which would need a periodic trigger the engine does not "
         "have. Six Headhunting talents depend on it; they are collapsed "
         "into direct grants on live triggers.")

N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "strong_arm", "Strong Arm",
    "Increases the damage of your spears by 25% and your hit chance by 6%.",
    0, -4,
    effects={"ability_barbarian_headhunters_spear_damage": 0.25,
             "ability_barbarian_maiming_spear_potency": 0.25,
             "ability_barbarian_impaling_spear_damage": 0.25,
             "ability_barbarian_barbed_spear_damage": 0.25,
             "ability_barbarian_javelin_toss_damage": 0.25,
             "hit_rating": 6.0},
    connect=["gruesome"],
    source="CoA: 'Increases the damage of Spears by 15% and your hit chance "
           "by 3%.' PORTS EXACTLY, doubled. 'SPEARS' IS A CoA ABILITY "
           "CATEGORY AND THE ENGINE HAS NO SUCH CONCEPT - there is no "
           "ability-group key - so all five spear abilities are written out "
           "individually. That matters: a single ability_barbarian_spears_* "
           "key would have been silent dead data, since the lookup is "
           "ability_<exact id>_damage. hit_rating is live as a FLAT bonus "
           "in PERCENTAGE POINTS; it is only invalid as a CONVERSION "
           "target. Was a pure scalar on our side."))

N.append(node(
    "gruesome", "Gruesome",
    "Increases the damage of Throw Weapon, Gutspiller and Berserker Axe by "
    "20%.",
    0, -2,
    effects={"ability_barbarian_throw_weapon_damage": 0.20,
             "ability_barbarian_gutspiller_damage": 0.20,
             "ability_barbarian_berserker_axe_damage": 0.20},
    connect=["puncture_wounds", "spear_thrower"],
    source="CoA over 2 ranks: 'Increases the damage of Throw Weapon, "
           "Gutspiller, and Guts Spilled by 10%.' Doubled for the two "
           "ranks. Guts Spilled is a SUB-EFFECT of Gutspiller in CoA (its "
           "every-6-seconds bleed-out) with no separate ability id here, so "
           "it has no handle of its own - Berserker Axe takes its place as "
           "the spec's third throw. CoA's Payback ('increases the damage "
           "dealt by your Guts Spilled by 75%') fails the same way and is "
           "folded in as part of this 20%. All FRACTIONS. Was a pure scalar "
           "on our side."))

N.append(node(
    "guts_splatter", "Guts Splatter",
    "Increases your armor penetration by 120.",
    0, 0,
    effects={"armor_penetration": 120},
    connect=["furious_berserker"],
    source="CoA over 2 ranks: 'Your Gutspiller now allows your abilities to "
           "ignore 10% of the enemy's Armor.' The conditional ('while "
           "Gutspiller is on the target') cannot be built - nothing reads a "
           "target's debuffs - and armor_penetration is FLAT rather than "
           "proportional, so '10% of the enemy's Armor' has no expressible "
           "form: there is no armor_pen_pct key and inventing one would "
           "have been silent. Built as a flat 120 rating, unconditional. "
           "Folded in CoA's Hunting for Sport ('while Unbridled Rage is "
           "active, your attacks now ignore 20% of the target's Armor'), "
           "which fails on both halves for the same reasons plus a third: "
           "nothing reads whether another effect is live. armor_penetration "
           "IS live (monster.py:659, via _pen_flat). A FLAT RATING. Was a "
           "pure scalar on our side."))

N.append(node(
    "to_the_bone", "To The Bone",
    "Your attacks have a 35% chance to break the target's defenses, "
    "lowering their armor for 4 turns.",
    0, 2,
    proc={"trigger": "on_weapon_swing", "chance": 35, "icd": 0,
          "apply_effect": {"effect_id": "break_armor", "name": "Break",
                           "effect_type": "debuff", "duration": 4,
                           "stat_mods": {"armor": -150},
                           "max_stacks": 5, "dispel_type": None,
                           "on_target": True}},
    connect=["frothing_savage"],
    source="CoA: 'Increases the critical strike chance of Guts Spilled by "
           "10% and it now applies Break to the target and critically "
           "striking with it will apply an additional stack. Break: break "
           "an enemy's defenses, reducing their armor by -4% for 30 "
           "seconds, stacking 5 times.' The Break debuff ports with CoA's 5 "
           "stacks; Guts Spilled has no ability id of its own to scope "
           "either the crit or the trigger to, and the extra-stack-on-crit "
           "clause would need the proc to know it crit. `armor` on a "
           "monster is FLAT (Monster.armor is base_armor plus the status "
           "mod), so CoA's '-4%' becomes -150 per stack, -750 at five. 30 "
           "sec -> 4 turns. armor is one of only eight status stat_mods a "
           "monster reads."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "puncture_wounds", "Puncture Wounds",
    "Your critical strikes open a bleed dealing damage over 3 turns, "
    "stacking up to 3 times.",
    1, -2,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "puncture_wounds",
                           "name": "Puncture Wounds",
                           "effect_type": "dot", "duration": 3,
                           "potency": 28, "damage_school": "physical",
                           "max_stacks": 3, "dispel_type": None,
                           "on_target": True}},
    connect=["deep_fury"],
    source="CoA: 'Critical strikes with Spears now causes enemies to bleed "
           "for 6 sec.' PORTS ALMOST VERBATIM; only the Spears scoping goes "
           "(no per-ability proc trigger, and 'Spears' is not an engine "
           "category anyway - see Strong Arm). 6 sec -> 3 turns, with 3 "
           "stacks added since this spec applies bleeds from four "
           "directions. A proc-applied dot carries `potency` as PER-TURN "
           "damage - 28 a turn, 84 per stack, 252 at three - where an "
           "ABILITY rank's effect_value is the TOTAL across the duration "
           "and gets divided (abilities.py:2695). Note dot_duration_pct "
           "does NOT reach a proc-applied dot: it is read in the ability "
           "dot branch, not the proc payload path."))

N.append(node(
    "spear_thrower", "Spear Thrower",
    "Your ranged attacks have a 30% chance to reset the cooldown of "
    "Headhunter's Spear.",
    1, 0,
    proc={"trigger": "on_weapon_swing", "chance": 30, "icd": 0,
          "reset_cooldown": ["barbarian_headhunters_spear"]},
    connect=["furious_berserker"],
    source="CoA level 30 passive: 'Casting Throw Weapon now has a 30% "
           "chance to reset the cooldown of your Spears.' PORTS ALMOST "
           "VERBATIM, chance included. reset_cooldown WITH A BARE LIST is a "
           "full reset, as against the {abilities, turns} form which only "
           "shaves turns. Scoped to Headhunter's Spear rather than all five "
           "spears: it is the one that generates Energy (25), so resetting "
           "it feeds the rotation, and resetting five cooldowns at once off "
           "a 30% swing proc would be the whole spec."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "furious_berserker", "Furious Berserker",
    "Your critical strikes restore 12 Energy and heal you.",
    2, 0,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "grant_resource": {"resource": "energy", "amount": 12},
          "heal_flat": 40},
    connect=["frothing_savage", "deep_fury"],
    source="CoA: 'Critical strikes with Barbed Spear now grants Born in "
           "Blood. Born in Blood: battle fuels your vitality, restoring 18 "
           "health and 12 Energy over 3 seconds.' " + BLOOD + " So the "
           "grant becomes immediate rather than a HoT, with CoA's exact 12 "
           "Energy and a flat heal. One proc can carry both a "
           "grant_resource and a heal_flat, which is why this one node does "
           "both halves. Folded in CoA's Vengeance For Zul'jin, which "
           "grants the same buff off Berserker Rush. grant_resource's "
           "`amount` is FLAT; there is no percentage-of-maximum form."))

N.append(node(
    "frothing_savage", "Frothing Savage",
    "Increases the critical strike chance of your spears and Berserker Axe "
    "by 16%.",
    2, 2,
    effects={"ability_barbarian_headhunters_spear_crit": 16.0,
             "ability_barbarian_barbed_spear_crit": 16.0,
             "ability_barbarian_impaling_spear_crit": 16.0,
             "ability_barbarian_berserker_axe_crit": 16.0},
    connect=["payback"],
    source="CoA over 2 ranks: 'Increases the critical strike chance of "
           "Spears and Berserker Axe by 8% against bleeding targets.' The "
           "crit ports (doubled) but THE CONDITION DOES NOT: nothing reads "
           "whether a target is bleeding, or carries any other debuff, "
           "which also cost Ranger's Serrations and Corrosive Poison and "
           "Necromancer's Fiend their conditionals. Kept unconditional "
           "rather than shipping something that silently never fires. "
           "Written per ability because 'Spears' is a CoA category with no "
           "engine equivalent. Per-ability crit keys are PERCENTAGE POINTS. "
           "Was a pure scalar on our side."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "deep_fury", "Deep Fury",
    "Your attacks have a 35% chance to reduce the cooldown of Unbridled "
    "Rage and Axe Twirling by 2 turns.",
    3, -1,
    proc={"trigger": "on_weapon_swing", "chance": 35, "icd": 1,
          "reset_cooldown": {"abilities": ["barbarian_unbridled_rage",
                                           "barbarian_axe_twirling"],
                             "turns": 2}},
    connect=["payback"],
    source="CoA: 'Direct Physical damage dealt now reduces the cooldown of "
           "Unbridled Rage by -1 sec.' PORTS ALMOST EXACTLY - the "
           "{abilities, turns} form of reset_cooldown shaves turns rather "
           "than resetting outright, which is what CoA describes. Extended "
           "to Axe Twirling from CoA's Time To Kill! ('reduces the cooldown "
           "of Axe Twirling by -15 sec'). 1 sec -> 2 turns, since a "
           "sub-turn reduction would round to nothing."))

N.append(node(
    "payback", "Payback",
    "Increases the damage of Gutspiller and Impaling Spear by 40% and your "
    "periodic damage by 15%.",
    3, 2,
    effects={"ability_barbarian_gutspiller_damage": 0.40,
             "ability_barbarian_impaling_spear_damage": 0.40,
             "dot_damage": 0.15},
    connect=["no_survivors"],
    source="CoA: 'Increases the damage dealt by your Guts Spilled by 75%.' "
           "Guts Spilled is a SUB-EFFECT of Gutspiller with no ability id "
           "of its own, so the buff lands on the parent dot and on Impaling "
           "Spear, the spec's other dot, with dot_damage covering the "
           "periodic half globally. dot_damage is the global periodic key "
           "(abilities.py:1601) and reaches Storm of Steel too. 75% split "
           "across two abilities plus a global rather than stacked on one. "
           "All FRACTIONS. Was a pure scalar on our side."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "no_survivors", "No Survivors",
    "Increases the duration of Maiming Spear, Barbed Spear and Gutspiller "
    "by 2 turns.",
    4, 0,
    effects={"ability_barbarian_maiming_spear_duration": 2,
             "ability_barbarian_gutspiller_duration": 2,
             "ability_barbarian_impaling_spear_duration": 2},
    connect=["raging_spirit", "power_tosser"],
    source="CoA: 'Increases the duration of Axe Twirling, Maiming Spear, "
           "and Barbed Spear by 5 sec.' 5 sec -> 2 turns. Barbed Spear is a "
           "ranged_damage ability with no duration and Axe Twirling is a "
           "self-buff, so Gutspiller and Impaling Spear - the spec's two "
           "dots - take their place, where the extension is worth far more: "
           "+2 TURNS ON A DOT ADDS TICKS AT FULL PER-TURN VALUE, because "
           "abilities.py:2777 derives per_turn from the ability's OWN base "
           "duration rather than the talented one. Both go 3 -> 5 turns and "
           "their totals rise by two thirds. Maiming Spear keeps its "
           "extension as a debuff. SMALL INTEGERS IN TURNS, so "
           "talent_ranks.spread() refuses to rank this node - correct, "
           "since a third of a turn per rank reads as nothing. Was a pure "
           "scalar on our side."))

N.append(node(
    "berserker", "Berserker",
    "Your critical strikes have a 30% chance to throw an extra Berserker "
    "Axe.",
    4, 2,
    proc={"trigger": "on_crit", "chance": 30, "icd": 0,
          "cast_ability": "barbarian_berserker_axe"},
    connect=["power_tosser"],
    source="CoA: 'While enraged, your ranged critical strikes now grant you "
           "Berserker. Berserker: your ranged abilities have a 20% chance "
           "to unleash Berserker Throw, dealing 75% Ranged Weapon Damage. "
           "While active, every offensive ranged ability used increases its "
           "chance to trigger by 2%.' THREE LAYERS, ONE SURVIVES: 'while "
           "enraged' reads whether an effect is live, the escalating chance "
           "needs a counter, and a proc that grants a proc-carrying buff "
           "would be a nested proc the audit cannot inspect. Built as the "
           "payoff directly - a cast_ability proc firing Berserker Axe, "
           "which costs nothing when it fires. Berserker Axe is ungated, so "
           "cast_ability's known failure mode (it does not check the caster "
           "has learned the ability) cannot bite here. Was a pure scalar on "
           "our side."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "raging_spirit", "Raging Spirit",
    "Reduces the cost of all your abilities by 15% and increases your "
    "ranged attack power by 20% of your Agility.",
    5, -1,
    effects={"all_ability_cost_pct": 0.15,
             "ranged_ap_from_agility_pct": 0.20},
    connect=["gurubashi_technique"],
    source="CoA: 'Casting Unbridled Rage now grants you 30 Energy and it "
           "now also removes the Energy cost of your Spirit spells while "
           "active.' The grant needs a per-ability proc trigger and the "
           "cost waiver needs both an active-effect read and a 'Spirit "
           "spells' category, none of which exist - and nothing waives a "
           "cost outright. So it becomes a flat cost reduction, which is "
           "the reliable version of the same intent. Folded in CoA's "
           "Power Tosser ('damage dealt by Throw Weapon now scales with "
           "your Agility') as a real conversion: ranged_ap is in "
           "STAT_CONVERSION_TARGETS and agility in SOURCES, a legal pair "
           "that reaches every ranged ability rather than one. "
           "all_ability_cost_pct is a FRACTION where POSITIVE MEANS A "
           "REDUCTION; the conversion key is a fraction too."))

N.append(node(
    "power_tosser", "Power Tosser",
    "Increases your ranged attack power by a further 25% of your Agility "
    "and your critical damage by 25%.",
    5, 1,
    effects={"ranged_ap_from_agility_pct": 0.25, "crit_damage_pct": 0.25},
    connect=["gurubashi_technique"],
    source="CoA level 50 passive: 'Damage dealt by Throw Weapon now scales "
           "with your Agility.' Built as the conversion rather than a "
           "per-ability scaling coefficient, which no key reaches - the "
           "ability keys are _damage, _healing, _crit, _crit_damage, _cost, "
           "_cooldown, _duration and _potency, and none touch how an "
           "ability scales off a stat. Stacks with Raging Spirit to 45% of "
           "Agility as ranged attack power, which is this spec's whole "
           "stat identity. crit_damage_pct is read at abilities.py:1438 and "
           "is a FRACTION, as is the conversion key."))

N.append(node(
    "skullseeker", "Skullseeker",
    "Increases your critical strike chance by 8%.",
    5, 3,
    effects={"crit_chance_physical": 8.0},
    connect=["gurubashi_technique"],
    source="CoA: 'Increases your critical strike chance against enemies "
           "above 80% health by 25%.' CoA gates this on the target being "
           "ABOVE 80% health. high_health_damage_threshold_pct is DEAD DATA "
           "and there is no above-health conditional of any kind - only the "
           "below-health low_health_damage_pct added 6 Nov 2026 - so the "
           "condition is dropped and 25% cut to 8% precisely because it is "
           "now unconditional and permanent where CoA's applies only to "
           "opening hits. Brutality carries a node of the same name and "
           "CoA's own data has it twice, which is why the values differ: "
           "each is priced for its own tree. crit_chance_physical is "
           "PERCENTAGE POINTS. Was a pure scalar on our side."))

N.append(node(
    "axe_twirling", "Axe Twirling",
    "Reduces the cooldown of Axe Twirling by 40% and increases your area "
    "damage by 20%.",
    1, 2,
    effects={"ability_barbarian_axe_twirling_cooldown_pct": 0.40,
             "aoe_damage": 0.20},
    connect=["to_the_bone"],
    source="CoA: 'Display mastery over throwing weapons for 10 sec, causing "
           "Throw Weapon, Gutspiller, and Berserker Axe to strike 2 "
           "additional nearby enemies.' The ability already exists as a "
           "3-turn self-buff. NOTHING ADDS TARGETS TO AN ABILITY - no "
           "effect key and no proc payload touches an ability's target "
           "count, which also killed Spear Shards, Impaling Spear's "
           "shatter, Spite's multi-throw and Ranger's Wild Man - so the "
           "intent lands as aoe_damage, which IS live and is read at "
           "abilities.py:1600 only when target_type is enemy_aoe, so it is "
           "genuinely scoped to area attacks. Folded in CoA's Time To Kill! "
           "('reduces the cooldown of Axe Twirling by -15 sec'), which "
           "names the same ability."))

N.append(node(
    "manhunter", "Manhunter",
    "Increases your critical strike chance by 5% and your physical damage "
    "by 8%.",
    2, -2,
    effects={"crit_chance_physical": 5.0, "physical_damage": 0.08},
    connect=["puncture_wounds"],
    source="CoA: 'Increases critical strike chance of all party and raid "
           "members by 3%. Does not stack with similar effects. In "
           "addition, increases your damage dealt by 10% against "
           "Humanoids.' NEITHER HALF SURVIVES AS WRITTEN: a talent effect "
           "can never reach an ally, and Barbarian has no 'Manhunter' "
           "ABILITY to convert to target_type 'party' the way Ancestry's "
           "eight auras already are; and NOTHING READS A CREATURE TYPE - no "
           "effect key or proc condition inspects a monster's family, which "
           "also cost Ranger's Windrunner's Reach its text. So both become "
           "selfish and unconditional. crit_chance_physical is PERCENTAGE "
           "POINTS; physical_damage is a FRACTION."))

N.append(node(
    "brutal_form", "Brutal Form",
    "Increases the healing of Ancestral Roar and Savage Revelry by 30%.",
    3, -3,
    effects={"ability_barbarian_ancestral_roar_healing": 0.30,
             "ability_barbarian_savage_revelry_healing": 0.30},
    connect=["puncture_wounds"],
    source="CoA: 'Increases the tick rate of Born in Blood by 25%, allows "
           "its healing to scale with your Agility, and it can now "
           "critically heal you.' THREE CLAUSES, NONE BUILDABLE: Born in "
           "Blood does not exist as an ability here; tick rate is "
           "meaningless when an effect ticks once per turn; and a HoT's "
           "ticks never roll crit in this engine, with no key to allow it "
           "(CoA asks for that repeatedly - Necromancer's Impeccable "
           "Timing, Reaper's Lacerations, Ranger's Bleeding Edge - and it "
           "fails every time). Re-pointed to the class's two real heals. "
           "BOTH TAKE ability_<id>_HEALING, not _damage: Ancestral Roar and "
           "Savage Revelry are effect_type heal, and _damage on a heal "
           "passes every check while doing nothing, which is how 18 talents "
           "across four classes were silently dead before _healing was "
           "accepted. Both FRACTIONS."))

N.append(node(
    "spite", "Spite",
    "Increases the damage of Spite and Javelin Toss by 35% and reduces "
    "Spite's cooldown by 30%.",
    4, -3,
    effects={"ability_barbarian_spite_damage": 0.35,
             "ability_barbarian_javelin_toss_damage": 0.35,
             "ability_barbarian_spite_cooldown_pct": 0.30},
    connect=["furious_berserker"],
    source="CoA: 'Quickly unleash 3 Berserker Throws at your target and "
           "then fling yourself back a great distance, dealing 125% Ranged "
           "Weapon Damage, scaling with modifiers to Berserker Axe.' The "
           "ability already exists on an 8-turn cooldown. Its multi-throw "
           "cannot be built (nothing adds attacks or targets to an ability) "
           "and the reposition has no positioning to use, so the node "
           "boosts it and Javelin Toss directly. Folded in CoA's Sen'jin's "
           "Guidance, which transforms Throw Weapon into Javelin Toss - "
           "nothing transforms one ability into another - so its crit "
           "clause lands here as damage instead. *_cooldown_pct is a "
           "FRACTION where POSITIVE MEANS A REDUCTION; the damage keys are "
           "fractions too but add rather than subtract."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "gurubashi_technique", "Gurubashi Technique",
    "Your ranged attacks have a 25% chance to throw a second weapon, and "
    "your periodic damage is increased by 20%.",
    6, 0,
    effects={"dot_damage": 0.20},
    proc={"trigger": "on_weapon_swing", "chance": 25, "icd": 0,
          "cast_ability": "barbarian_throw_weapon"},
    source="CoA: 'Casting Throw Weapon now has a 25% chance to transform "
           "your next cast of it within 8 sec into Rapid Throw.' NOTHING "
           "TRANSFORMS ONE ABILITY INTO ANOTHER - that killed Sen'jin's "
           "Guidance too, and Felsworn's Fel Torpedo - so the 25% chance is "
           "kept and cashed as a free extra Throw Weapon instead, which is "
           "what Rapid Throw amounts to. cast_ability takes a bare ability "
           "id and costs nothing when it fires; Throw Weapon is ungated, so "
           "cast_ability's known failure mode cannot bite. The dot_damage "
           "half ties the capstone to the bleed theme Puncture Wounds, "
           "Payback and No Survivors build, stacking with Payback to +35%."))


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
        f"Barbarian Brutality's Overkill owns low_health_threshold_pct for "
        f"this class at 0.35; the key SUMS across talents. Found {setters}")

    # Every ability-scoped key must name an ability that EXISTS. 'Spears'
    # is a CoA category with no engine equivalent, so this tree writes five
    # of them out individually - and a typo there is silent dead data,
    # because the lookup is ability_<exact id>_<field>.
    abilities = {a["ability_id"] for a in json.loads(
        (ROOT / "data/abilities/barbarian.json").read_text())["abilities"]}
    FIELDS = ("_damage", "_healing", "_crit", "_crit_damage", "_cost_pct",
              "_cooldown_pct", "_duration", "_potency")
    for n in TREE["nodes"]:
        for k in (n.get("effects") or {}):
            if not k.startswith("ability_"):
                continue
            for f in FIELDS:
                if k.endswith(f):
                    aid = k[len("ability_"):-len(f)]
                    assert aid in abilities, (
                        f"{n['talent_id']} authors {k}, but "
                        f"'{aid}' is not a Barbarian ability - the lookup "
                        f"is ability_<exact id>_<field>, so this is silent "
                        f"dead data that no grep or audit would catch")
                    break
        proc = n.get("proc") or {}
        gr = proc.get("grant_resource")
        if gr:
            assert gr.get("resource") == "energy" and "amount" in gr, (
                f"{n['talent_id']} grant_resource must name energy with a "
                f"FLAT amount")
        for aid in (proc.get("reset_cooldown") or []) if isinstance(
                proc.get("reset_cooldown"), list) else (
                proc.get("reset_cooldown") or {}).get("abilities", []):
            assert aid in abilities, (
                f"{n['talent_id']} resets {aid}, which is not a Barbarian "
                f"ability")
        ca = proc.get("cast_ability")
        if ca:
            assert ca in abilities, (
                f"{n['talent_id']} casts {ca}, which is not a Barbarian "
                f"ability")

    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Barbarian Headhunting: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
