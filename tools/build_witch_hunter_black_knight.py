#!/usr/bin/env python3
"""Rebuild Witch Hunter's Black Knight tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_witch_hunter_black_knight.py [--check]

SOURCE: data/reference/coa/witch-hunter.json - 38 real Black Knight talents
from Ascension's own CoA Builder payload. Role: DPS, though it reads as an
off-tank: most of its talents are avoidance, absorbs and self-healing.

The shipped tree was 23 nodes with TWO procs and 20 bare numbers. This is
the fourth and last Witch Hunter spec; the class went from 6 procs across
92 nodes to 44 across 114.

WHAT THE SPEC IS. A two-hander and a blood price. Black Knight marks
everything with Shadow Brand, takes health back out of every swing (Noctis
Blade heals for half its damage, Grasp of the Undying leeches, Witchblight
and Shadowstorm both drain), and turns avoidance into resource.

SHADOW BRAND CANNOT BE CONSUMED BY A TALENT, which is the one real loss
here. CoA's Night King is "Noctis Blade now consumes Shadow Brand to deal
50% increased damage" - and consuming a target's stacks IS a live mechanism
(consumes_target_stacks_of, which Starcaller is built on), but it is a
property of the ABILITY, set in data/abilities, not something a talent
effect can switch on. Tinker's Drone Striker hit the identical wall. So
Night King pays out as flat Noctis Blade damage and says so.

CONVENTIONS, which do not agree with each other:
  agility_pct, armor_pct, armor_penetration_pct        percentage POINTS
  parry / dodge / haste / armor in a status            raw ("4.0" = 4)
  all_damage, shadow_spell_damage, crit_damage_*       FRACTION
  damage_dealt_pct in a status effect                  percentage POINTS
  damage_taken_pct in a status effect                  read RAW
  *_cost_pct / *_cooldown_pct      FRACTION, POSITIVE MEANS A REDUCTION
  <target>_from_<source>_pct       FRACTION, listed pairs only

WHAT IS NOT BUILDABLE, stated per node:
  - Weapon-type gates. Half this tree says "while wielding a two-handed
    weapon" and there is no "while wielding X" condition for an effect key
    or a proc, so those apply unconditionally.
  - "Strikes an additional nearby enemy" (Shadowy Tendrils, Guardbreaker).
  - Armour contribution by ITEM TYPE (Dark Chivalry's "from mail items").
  - "expertise" is read by no engine code (Secret Society).
  - Health-threshold gates on a proc (Undying's below-75%, Clinch
    Fighting's would-otherwise-kill-you). No proc payload reads the
    carrier's own health, so those become chances with internal cooldowns.
  - Making another ability free (Dawn Knight): cost keys are read only
    through get_talent_effects(), which never includes status effects.
  - Party-wide Replenishment (Foresight), and transferring party damage to
    yourself (Gaze of the Black Knight) - there is no mechanism that
    redirects damage between characters.

TURN-BASED CUTS. Every yard and the pull on Chains of Darkness are gone.
One CoA entry here has a broken template description (Secret of Raven
Hill, $4a) and is not built from a guess.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/witch_hunter_black_knight.json"

#: The spec's own damaging abilities, for "direct ability damage".
STRIKES = ["witch_hunter_noctis_blade", "witch_hunter_desecrate",
           "witch_hunter_pommel_smash", "witch_hunter_dawn_blade",
           "witch_hunter_witchblight", "witch_hunter_guard_strike"]

#: CoA: "Shadow Brand: Marks the target for 12 seconds, dealing High Threat
#: Shadow Damage over 12 seconds." 12 sec is 4 turns.
SHADOW_BRAND = {
    "effect_id": "witch_hunter_shadow_brand", "name": "Shadow Brand",
    "effect_type": "dot", "duration": 4, "potency": 22,
    "damage_school": "shadow", "on_target": True,
}

TREE = {
    "spec_name": "Witch Hunter Black Knight",
    "tree_id": "witch_hunter_black_knight",
    "description": ("Two-hander and a blood price - brands everything and "
                    "drinks its way back up."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from data/reference/coa/witch-hunter.json "
        "(38 real CoA Black Knight talents, role DPS, playing as an "
        "off-tank). Replaces a 23-node tree with 2 procs and 20 bare "
        "numbers. Fourth and last Witch Hunter spec: the class went from 6 "
        "procs across 92 nodes to 44 across 114. Half of CoA's talents here "
        "are gated on wielding a two-handed weapon and this engine has no "
        "'while wielding X' condition, so those apply unconditionally. "
        "Every CoA reference to Rage is translated to Focus."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"witch_hunter_black_knight_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"witch_hunter_black_knight_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "shadow_brand", "Shadow Brand",
    "Your ability damage brands the target, burning it with shadow for 4 "
    "turns.",
    0, -5,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": STRIKES,
          "apply_effect": dict(SHADOW_BRAND)},
    connect=["shadow_order"],
    source="CoA verbatim: 'Direct ability damage now applies Shadow Brand to "
           "enemies. Shadow Brand: Marks the target for 12 seconds, dealing "
           "High Threat Shadow Damage over 12 seconds.' 12 sec is 4 turns. "
           "This is the mark three other nodes in the tree read, and the old "
           "tree had no form of it. 'High Threat' is not a property a dot "
           "carries here - threat_generation_pct is a character stat - so the "
           "threat half is lost."))

N.append(node(
    "dark_penance", "Dark Penance",
    "Increases your Agility by up to 4% and your parry and dodge by up to 4%.",
    0, -3,
    effects={"agility_pct": 4.0, "parry": 4.0, "dodge": 4.0},
    connect=["dark_riposte"],
    source="CoA over 2 ranks: 'Increases your Agility and your chance to "
           "parry and dodge by 2%.' Authored as the full-investment ceiling "
           "at one rank and left to the rank policy. agility_pct takes "
           "percentage POINTS; parry and dodge are read raw."))

N.append(node(
    "dusk_knight", "Dusk Knight",
    "Increases your parry by 40% of your Agility and your dodge by 25% of "
    "your Intellect.",
    0, -1,
    effects={"parry_from_agility_pct": 0.40, "dodge_from_intellect_pct": 0.25},
    connect=["dark_riposte"],
    source="CoA verbatim: 'Level 20 Passive. Increases your parry rating by "
           "40% of your Agility and your dodge rating by 25% of your "
           "Intellect.' Both pairings are live - parry and dodge are in "
           "STAT_CONVERSION_TARGETS, agility and intellect are sources. "
           "Conversions are FRACTIONS. This is the third Witch Hunter node "
           "that makes Intellect matter on a physical kit, after "
           "Boltslinger's Arbalist and Houndmaster's Dark Mind."))

N.append(node(
    "dark_power", "Dark Power",
    "Increases your Stamina by 12%.",
    0, 1,
    effects={"stamina_pct": 12.0},
    connect=["no_regrets"],
    source="CoA: 'Level 30 Passive. You now gain 1 Stamina for every 2 "
           "Agility.' NOT buildable as the conversion it is. STAMINA IS NOT A "
           "CONVERSION TARGET - STAT_CONVERSION_TARGETS holds attack_power, "
           "ranged_ap, spell_power, healing_power, armor, block_value, parry, "
           "dodge, haste and the two crit chances, and nothing else - so "
           "stamina_from_agility_pct is skipped in silence by "
           "character.py, the Clarity of the Heavens failure recorded in that "
           "dict's own comment. Authored that way first and the audit caught "
           "it. Rebuilt as a flat Stamina percentage, which is what the "
           "conversion was for on a spec that stacks Agility anyway. "
           "stamina_pct takes percentage POINTS."))

N.append(node(
    "dark_chivalry", "Dark Chivalry",
    "Increases your armor by 20%.",
    0, 3,
    effects={"armor_pct": 20.0},
    connect=["secret_society"],
    source="CoA: 'Increases your Armor contribution from mail items by 100%.' "
           "There is no per-armour-type scaling in this engine - armour is "
           "one number by the time a talent sees it - so the mail condition "
           "is dropped and 100% cut to 20%, since it now applies to every "
           "piece rather than to one armour class. armor_pct takes percentage "
           "POINTS."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "grasp_of_the_undying", "Grasp of the Undying",
    "Your weapon swings have a 25% chance to leech 20% of the damage back as "
    "health.",
    1, -4,
    proc={"trigger": "on_weapon_swing", "chance": 25, "icd": 0,
          "leech_pct": {"pct": 0.20}},
    connect=["noctis_protection"],
    source="CoA verbatim: 'Level 10 Passive. Auto attacks while wielding a "
           "two-handed weapon now have a 25% chance to unleash Grasp of the "
           "Undying, leeching health from the target.' The two-handed gate is "
           "dropped - no 'while wielding X' condition exists. leech_pct "
           "without smart:true heals the carrier, which is what this is for; "
           "with it, the heal would go to the worst-off ALLY instead, which "
           "is a different talent. Also carries CoA's Shadowy Tendrils "
           "('strikes 2 additional nearby enemies'), which no key can add."))

N.append(node(
    "shadow_order", "Shadow Order",
    "Increases the damage of Shadow Brand by up to 40% and the damage of "
    "your damage-over-time effects by up to 10%.",
    1, -2,
    effects={"ability_witch_hunter_shadow_brand_damage": 0.40,
             "dot_damage": 0.10},
    connect=["wide_swings"],
    source="CoA over 2 ranks: 'Increases the damage of Shadow Brand by 20% "
           "and your hit rating by 3% of your Agility.' The hit conversion is "
           "NOT built: hit_rating is not in STAT_CONVERSION_TARGETS, so "
           "hit_rating_from_agility_pct would be skipped in silence - the "
           "Clarity of the Heavens failure. Replaced with dot_damage, which "
           "raises the brand the same way and is live. Note the brand applied "
           "by this tree's tier 0 node is a proc-applied dot and is NOT "
           "affected by ability_witch_hunter_shadow_brand_damage, which keys "
           "off the ABILITY of that id - both exist, so the key is not dead, "
           "but it reaches the cast version only."))

N.append(node(
    "dark_riposte", "Dark Riposte",
    "Parrying an attack restores health and 10 Focus.",
    1, 0,
    proc={"trigger": "on_parry", "chance": 100, "icd": 0,
          "heal_flat": 60,
          "grant_resource": {"resource": "focus", "amount": 10}},
    connect=["wicked_intent"],
    source="CoA verbatim but for the resource: 'Parrying enemy attacks now "
           "restores 5% of your missing health and Rage.' Rage -> Focus. "
           "'5% of missing health' is not a payload shape - heal_flat is a "
           "number and there is no percentage-of-missing form - so it is a "
           "flat 60. on_parry is a live trigger this class otherwise never "
           "uses, and the whole avoidance half of the spec hangs off it."))

N.append(node(
    "no_regrets", "No Regrets",
    "March of the Black King hardens you, increasing your armor by 15% for "
    "3 turns.",
    1, 2,
    proc={"trigger": "on_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_march_of_the_black_king"],
          "apply_effect": {"effect_id": "witch_hunter_no_regrets",
                           "name": "No Regrets", "effect_type": "buff",
                           "duration": 3, "max_stacks": 1,
                           "stat_mods": {"armor_pct": 15.0},
                           "on_target": False}},
    connect=["dark_juggernaut"],
    source="CoA verbatim: 'Your March of the Black King now increases your "
           "Armor by 15%.' on_cast rather than on_damage_cast: March of the "
           "Black King is restore_resource and deals no damage, so a damage "
           "trigger would never have fired on it - the same trap Coordinated "
           "Killing avoided in Houndmaster."))

N.append(node(
    "secret_society", "Secret Society",
    "Increases your Shadow spell damage by up to 8% and your spell critical "
    "strike chance by up to 8%.",
    1, 4,
    effects={"shadow_spell_damage": 0.08, "crit_chance_spell": 8.0},
    connect=["witch_knight"],
    source="CoA over 2 ranks: 'Increases your Shadow critical strike chance "
           "and Shadow damage dealt by 4% and your expertise by 5.' "
           "'expertise' is read by no engine code, so that half is dropped - "
           "third time in this rebuild. Crit chance is not school-specific "
           "here, so the Shadow restriction survives only on the damage "
           "half. shadow_spell_damage is a <school>_spell_damage key the "
           "engine builds by interpolation."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "noctis_protection", "Noctis Protection",
    "Noctis Blade shields you for 60% of the damage it deals.",
    2, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_noctis_blade"],
          "shield_pct": {"pct": 0.60, "duration": 2,
                         "effect_id": "witch_hunter_noctis_shield",
                         "name": "Noctis Protection"}},
    connect=["witch_knight"],
    source="CoA: 'Casting Noctis Blade now applies a shield absorbing 266 + "
           "200% Stamina + 10% AP damage for 4 seconds.' shield_pct sizes "
           "the absorb from the TRIGGERING amount rather than from a stat "
           "formula, which is the only form the payload has - so it is 60% of "
           "the hit instead of a Stamina-scaled number. 4 sec is 2 turns. "
           "Noctis Blade already heals for half its damage, so this makes it "
           "the spec's whole defensive turn."))

N.append(node(
    "wide_swings", "Wide Swings",
    "Increases the damage of Noctis Blade by 20%.",
    2, -2,
    effects={"ability_witch_hunter_noctis_blade_damage": 0.20},
    connect=["bulwark_of_darkness"],
    source="CoA: 'Increases the damage of Noctis Blade and Grasp of the "
           "Undying by 20% on enemies affected by Shadow Brand.' No effect "
           "key reads whether the target carries a debuff, so the condition "
           "is dropped; CoA's 20% is kept because Shadow Brand is on "
           "everything anyway once tier 0 is taken. Grasp of the Undying is a "
           "proc rather than an ability, so there is no "
           "ability_*_damage key for it."))

N.append(node(
    "wicked_intent", "Wicked Intent",
    "Desecrate has a 15% chance to make Noctis Blade ready again at once.",
    2, 0,
    proc={"trigger": "on_damage_cast", "chance": 15, "icd": 0,
          "ability_filter": ["witch_hunter_desecrate"],
          "reset_cooldown": ["witch_hunter_noctis_blade"]},
    connect=["shadowstorm"],
    source="CoA verbatim: 'Casting Desecrate now has a 15% chance to reset "
           "the cooldown of Noctis Blade.' Ports directly."))

N.append(node(
    "dark_juggernaut", "Dark Juggernaut",
    "Desecrate restores health.",
    2, 2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_desecrate"],
          "heal_flat": 110},
    connect=["shadowstorm"],
    source="CoA: 'Desecrate now restores health plus an additional 1% maximum "
           "health for each target struck affected by Shadow Brand.' Nothing "
           "counts how many targets a cast hit, and nothing reads how many of "
           "them carry a debuff, so the per-target scaling is dropped and the "
           "base heal kept as a flat amount."))

N.append(node(
    "calm_under_pressure", "Calm Under Pressure",
    "Reduces the cooldown of Stoicism by 40% and Burrow Bolt by 25%.",
    2, 4,
    effects={"ability_witch_hunter_stoicism_cooldown_pct": 0.40,
             "ability_witch_hunter_burrow_bolt_cooldown_pct": 0.25},
    connect=["dark_barrier"],
    source="CoA: 'Reduces the cooldown of Stoicism by -30 sec and Burrow Bolt "
           "by -5 sec.' Both expressed as percentages because cooldowns are "
           "counted in turns here. POSITIVE reduces."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "witch_knight", "Witch Knight",
    "Your ability damage grants Witching, increasing your haste by 10% and "
    "your magic resistance for 3 turns, stacking 3 times.",
    3, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": STRIKES,
          "apply_effect": {"effect_id": "witch_hunter_witching",
                           "name": "Witching", "effect_type": "buff",
                           "duration": 3, "max_stacks": 3,
                           "stat_mods": {"haste": 10.0,
                                         "magic_resistance": 10.0},
                           "on_target": False}},
    connect=["undying"],
    source="CoA: 'Direct ability damage with a two-handed weapon now reduces "
           "the remaining cooldown of your Tonics by 1 sec and grants "
           "Witching. Witching: Increases magic resistances by 10%, and melee "
           "haste by 10% for 8 sec, stacking 3 times.' The two-handed gate is "
           "dropped. The Tonic cooldown rider is dropped too: a proc can "
           "reset_cooldown, but doing that AND applying a stacking buff off "
           "one trigger would make this node the whole tier. CoA's numbers "
           "and 3 stacks kept; 8 sec is 3 turns."))

N.append(node(
    "shadowstorm", "Shadowstorm",
    "Pommel Smash has a 20% chance to leech 35% of its damage back as health.",
    3, -2,
    proc={"trigger": "on_damage_cast", "chance": 20, "icd": 0,
          "ability_filter": ["witch_hunter_pommel_smash"],
          "leech_pct": {"pct": 0.35}},
    connect=["undying"],
    source="CoA verbatim: 'Damage dealt by Pommel Smash now has a 20% chance "
           "to trigger a Shadowstorm. Shadowstorm: Leeches health from "
           "enemies within 8 yds.' The radius is gone; the leech is the "
           "talent. CoA's 20% kept."))

N.append(node(
    "bulwark_of_darkness", "Bulwark of Darkness",
    "Increases the damage of Dawn Blade by 25%.",
    3, 0,
    effects={"ability_witch_hunter_dawn_blade_damage": 0.25},
    connect=["clinch_fighting"],
    source="CoA: 'Damage dealt by Dawn Blade is now increased by 5% for each "
           "stack of Pommel Smash on the target.' Pommel Smash leaves no "
           "stacks in Frontier, and nothing reads another effect's stack "
           "count in any case, so the per-stack scaling is dropped and "
           "priced as a flat 25% - five stacks' worth of CoA's bonus."))

N.append(node(
    "dark_barrier", "Dark Barrier",
    "Increases the duration of Stoicism by 2 turns.",
    3, 2,
    effects={"ability_witch_hunter_stoicism_duration": 2},
    connect=["guardbreaker"],
    source="CoA: 'Increases the duration of Stoicism by 5 sec.' 5 sec is "
           "under 2 turns, rounded up since 1 would be less than CoA's. NOTE "
           "this node is deliberately left OUT of the rank policy's reach by "
           "carrying a small integer effect - a duration cannot be divided "
           "across ranks, so tools/talent_ranks.rankable() refuses it. See "
           "that function for why: re-ranking a +1 turn node multiplied the "
           "ceiling instead of splitting it."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "undying", "Undying",
    "Dawn Blade sharpens your next Noctis Blade, increasing its critical "
    "strike chance by 40% for 3 turns.",
    4, -3,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_dawn_blade"],
          "apply_effect": {"effect_id": "witch_hunter_undying",
                           "name": "Undying", "effect_type": "buff",
                           "duration": 3, "max_stacks": 1,
                           "stat_mods": {"crit_chance_physical": 40.0},
                           "on_target": False}},
    connect=["night_king"],
    source="CoA: 'While below 75% maximum health, Dawn Blade now increases "
           "the critical strike chance of Noctis Blade by 40% for 10 "
           "seconds.' Two losses. No proc payload reads the carrier's own "
           "health, so the below-75% gate is dropped. And a status effect "
           "cannot carry ability_witch_hunter_noctis_blade_crit, because "
           "per-ability keys are read through get_talent_effects() which "
           "never includes status effects - so the 40% is general physical "
           "crit for the window instead of Noctis-only. CoA's number and "
           "10 sec (3 turns) kept."))

N.append(node(
    "clinch_fighting", "Clinch Fighting",
    "Taking a heavy blow steadies you, healing you and increasing the damage "
    "of Noctis Blade by 50% for 2 turns.",
    4, -1,
    proc={"trigger": "on_damage_taken", "chance": 10, "icd": 8,
          "heal_flat": 400,
          "apply_effect": {"effect_id": "witch_hunter_clinch_fighting",
                           "name": "Clinch Fighting", "effect_type": "buff",
                           "duration": 2, "max_stacks": 1,
                           "stat_mods": {"damage_dealt_pct": 25.0},
                           "on_target": False}},
    connect=["night_king"],
    source="CoA: 'Attacks which would otherwise kill you now heal you for 50% "
           "maximum health and increases the damage of Noctis Blade by 50% "
           "for 6 seconds. Can only occur once every 2 min.' A cheat-death "
           "trigger does not exist - no proc reads 'this hit would have "
           "killed me' - so it is a 10% chance on taking damage with an "
           "8-turn internal cooldown, which is roughly CoA's "
           "once-every-2-minutes. The damage half is general rather than "
           "Noctis-only for the same status-effect reason as Undying, and is "
           "halved to 25% because it now applies to everything."))

N.append(node(
    "guardbreaker", "Guardbreaker",
    "Increases the damage of Pommel Smash by up to 40%.",
    4, 1,
    effects={"ability_witch_hunter_pommel_smash_damage": 0.40},
    connect=["blade_of_the_misbegotten"],
    source="CoA over 2 ranks: 'Your Pommel Smash now strikes an additional "
           "nearby enemy.' No key adds a target to an ability, so this is "
           "repriced as damage - the same call as Boltslinger's Relentless, "
           "and made the same way rather than authoring an aoe_damage bonus "
           "that would apply to nothing (pommel_smash is single-target)."))

N.append(node(
    "foresight", "Foresight",
    "Your critical strikes restore 12 Focus.",
    4, 3,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "grant_resource": {"resource": "focus", "amount": 12}},
    connect=["blade_of_the_misbegotten"],
    source="CoA: 'Your direct Physical critical strikes now grant allies "
           "Replenishment. In addition, Dawn Blade is now guaranteed to "
           "critically strike against Undead or Demons. Replenishment: "
           "Replenishes 5% of maximum mana per 5 sec for 15 seconds.' There "
           "is no mechanism that grants ALLIES a resource effect from a proc "
           "- grant_resource pays the carrier - and no key reads creature "
           "type, so both halves land on the Witch Hunter as Focus. 1-turn "
           "internal cooldown so a crit streak does not refill the bar."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "night_king", "Night King",
    "Increases the damage of Noctis Blade by 50%.",
    5, -3,
    effects={"ability_witch_hunter_noctis_blade_damage": 0.50},
    connect=["gaze_of_the_black_knight"],
    source="CoA: 'Noctis Blade now consumes Shadow Brand to deal 50% "
           "increased damage.' THE CONSUME IS THE ONE REAL LOSS IN THIS TREE. "
           "Consuming a target's stacks is a live mechanism - "
           "consumes_target_stacks_of, which Starcaller's whole class is "
           "built on - but it is a property of the ABILITY, set in "
           "data/abilities/, and no talent effect switches it on. Tinker's "
           "Drone Striker hit the identical wall and is documented there. So "
           "the 50% is granted flat and the description does not promise a "
           "consume that will not happen."))

N.append(node(
    "blade_of_the_misbegotten", "Blade of the Misbegotten",
    "Dawn Blade feeds you, increasing your maximum health by 5% per stack "
    "for 3 turns, stacking 3 times.",
    5, -1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_dawn_blade"],
          "apply_effect": {"effect_id": "witch_hunter_misbegotten",
                           "name": "Blade of the Misbegotten",
                           "effect_type": "buff", "duration": 3,
                           "max_stacks": 3,
                           "stat_mods": {"max_health_pct": 5.0},
                           "on_target": False}},
    connect=["gaze_of_the_black_knight"],
    source="CoA: 'Damage dealt by Dawn Blade now increases your health by 15% "
           "of the damage dealt for 8 seconds, stacking 3 times.' A status "
           "effect cannot size itself from the triggering amount unless the "
           "payload does it (shield_pct and leech_pct can; apply_effect "
           "cannot), so the gain is a percentage of max health instead of a "
           "percentage of the hit. CoA's 3 stacks and 8 sec (3 turns) kept. "
           "max_health_pct takes percentage POINTS inside a status effect, so "
           "5.0 - authored 0.05 first, which is 0.05% and would have been a "
           "node that did visibly nothing. The audit caught it; a status "
           "stat_mod of 0.05 is perfectly valid and simply too small to "
           "notice in play, which is the worst kind of wrong."))

N.append(node(
    "destroyer_of_evil", "Destroyer of Evil",
    "Dawn Blade leaves the target burning with twilight for 3 turns.",
    5, 1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_hunter_dawn_blade"],
          "apply_effect": {"effect_id": "witch_hunter_twilight_burn",
                           "name": "Destroyer of Evil", "effect_type": "dot",
                           "duration": 3, "potency": 30,
                           "damage_school": "shadow", "on_target": True}},
    connect=["gaze_of_the_black_knight"],
    source="CoA: 'Damage dealt by Dawn Blade now deals an additional 20% of "
           "the damage dealt as Twilight Damage every 1 sec for 3 seconds.' "
           "Twilight is not one of this engine's six schools (arcane, fire, "
           "frost, nature, shadow, holy), so it is shadow - the half of CoA's "
           "Twilight this spec is built on. A proc-applied dot takes a flat "
           "potency, so 20% of a Dawn Blade is approximated at 30 a turn."))

N.append(node(
    "dawn_knight", "Dawn Knight",
    "Avoiding an attack has a 40% chance to make your next hits 25% stronger "
    "for 3 turns.",
    5, 3,
    proc={"trigger": "on_avoid", "chance": 40, "icd": 1,
          "apply_effect": {"effect_id": "witch_hunter_dawn_knight",
                           "name": "Dawn Knight", "effect_type": "buff",
                           "duration": 3, "max_stacks": 1,
                           "stat_mods": {"damage_dealt_pct": 25.0},
                           "on_target": False}},
    connect=["gaze_of_the_black_knight"],
    source="CoA: 'Level 50 Passive. Avoiding damage or dealing damage with "
           "auto attacks now has a 40% chance to grant you Dawn Knight. Dawn "
           "Knight: Your next Dawn Blade within 15 seconds is free of cost "
           "and deals 25% increased damage.' Built on the AVOID half only - "
           "one proc, one trigger, and avoidance is this spec's theme. "
           "Making a cast free is not reachable from a status effect (cost "
           "keys go through get_talent_effects()), and the 25% applies "
           "generally rather than to Dawn Blade alone for the same reason. "
           "CoA's 40% and 15 sec (3 turns) kept."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "gaze_of_the_black_knight", "Gaze of the Black Knight",
    "Your ability damage wraps you in a shield absorbing 40% of it, and your "
    "critical strikes make you 15% harder to hurt for 2 turns.",
    6, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": STRIKES,
          "shield_pct": {"pct": 0.40, "duration": 2,
                         "effect_id": "witch_hunter_black_gaze",
                         "name": "Gaze of the Black Knight"},
          "apply_effect": {"effect_id": "witch_hunter_dark_oath",
                           "name": "Dark Oath", "effect_type": "buff",
                           "duration": 2, "max_stacks": 1,
                           "stat_mods": {"damage_taken_pct": -0.15},
                           "on_target": False}},
    source="CoA: '3 min cooldown. Apply a dark shield to yourself, absorbing "
           "damage and then gaze upon your party members, causing 25% of the "
           "damage they take to be transferred to you for 12 sec.' The "
           "TRANSFER is not buildable at all: nothing in this engine "
           "redirects damage from one character to another, and inventing it "
           "from a talent is not a thing a payload can do. So the capstone "
           "keeps the half that works - the absorb - and pairs it with Dark "
           "Oath, which CoA attaches to Knight's Seal ('reducing all damage "
           "taken by -20% for 8 seconds'), because a capstone that only "
           "absorbed would read as a weaker Noctis Protection. "
           "damage_taken_pct is read RAW in a status effect, so -0.15 is "
           "-15%; the physical_ and magic_ variants beside it would be "
           "-15.0, and getting that backwards is a 1500% reduction - which "
           "is exactly what Boltslinger's Evasive shipped as before the audit "
           "caught it."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. tools/talent_ranks.py rescales so a ranked
# node lands on exactly the ceiling it had at one rank. The capstone stays a
# single pick; there are no unlock nodes, since no Witch Hunter ability
# carries requires_talent.
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
    print(f"Witch Hunter Black Knight: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
