#!/usr/bin/env python3
"""Rebuild Templar's Crusader tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_templar_crusader.py [--check]

SOURCE: data/reference/coa_worksheets/templar.md and
data/reference/coa/templar.json - 37 real Crusader talents from
Ascension's own CoA Builder payload. Role: DPS.

The shipped tree was 24 nodes with FOUR procs. This completes Templar.

LIGHT'S CHOSEN PORTS WHOLE - both halves, and it is the third double
conversion in this class. CoA: "Increases your spell power by 30% of your
Agility and your critical strike rating by 15% of your Intellect."
spell_power and crit_chance_spell are both in STAT_CONVERSION_TARGETS and
agility and intellect are both in STAT_CONVERSION_SOURCES. Templar is the
best-served class in this audit for conversions: Zealot turns attack
power into spell damage, Oathkeeper turns Agility into parry and
Intellect into dodge, and this turns Agility into spell power and
Intellect into crit.

RETRIBUTION USES bonus_pct, which reads the triggering hit's own amount -
one of only three payloads that can (with leech_pct and smart heals). CoA:
"Melee damage dealt now has a 20% chance to strike 2 additional times for
30% of the damage dealt as Holy Damage." Two strikes at 30% is 60% of the
hit, and CoA's 20% chance is exact. What is lost is the Holy typing:
bonus_pct adds to the same hit and takes no school, unlike damage_flat.

CONDEMN STACKS CANNOT BE READ, and four talents read them -
Teachings of the Cathedral, Tyr's Blessing, Templar's Might and
Righteousness. Condemn is a real Frontier ability and a combo generator,
but nothing reads another effect's stack count, and no key modifies
another effect's max_stacks. Each is re-pointed.

THIS TREE OWNS ONE GATED ABILITY: righteous_tempest at tier 4 - the only
one of Templar's three that is not at tier 6. Preserved in place and
asserted.

CONVENTIONS, which do not agree with each other:
  agility_pct, intellect_pct                   percentage POINTS
  all_damage, physical_damage, ability_*_damage,
    crit_damage_physical, ability_*_crit_damage   FRACTION
  crit_chance_physical, crit_chance_spell, haste,
    hit_rating, expertise, ability_*_crit          PERCENT
  bonus_pct                FRACTION of the triggering hit, no school
  leech_pct                FRACTION, reads the hit
  <target>_from_<source>_pct  FRACTION, listed pairs only
  *_cost_pct / *_cooldown_pct  FRACTION, POSITIVE MEANS A REDUCTION

TURN-BASED CUTS. Movement speed (Whirling Tempest, Crusader's Brand's
mount/flee prevention), stealth detection, "every 2nd cast" (Scarlet
Secrets - no cast counter), and health-threshold conditions (Judgement).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/templar_crusader.json"

#: The combo builders, shared across Templar's trees.
BUILDERS = ["templar_righteous_lunge", "templar_condemn",
            "templar_holy_cleave", "templar_vindication",
            "templar_sacred_swing", "templar_argent_blade"]

#: CoA's execute trio.
EXECUTES = ["templar_scarlet_hammer", "templar_titanstrike"]

#: This tree's one talent-gated ability.
GATED = {"templar_righteous_tempest"}

TREE = {
    "spec_name": "Templar Crusader",
    "tree_id": "templar_crusader",
    "description": ("Argent fervor - a crusader whose strikes echo in holy "
                    "light."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from the 37 real CoA Crusader talents (role "
        "DPS), completing Templar. LIGHT'S CHOSEN PORTS WHOLE - spell power "
        "from Agility and crit from Intellect are both legal pairs - making "
        "this the third double conversion in the class. Templar is the "
        "best-served class in the audit for conversions. Retribution uses "
        "bonus_pct, which reads the triggering hit's own amount, so CoA's "
        "'2 additional strikes for 30% of the damage dealt' is exact at 60%. "
        "Condemn stacks cannot be read and four talents read them. Owns "
        "righteous_tempest at tier 4, the only one of Templar's three gated "
        "abilities not at tier 6."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"templar_crusader_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"templar_crusader_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "lights_chosen", "Light's Chosen",
    "Increases your spell power by 30% of your Agility and your spell "
    "critical strike chance by 15% of your Intellect.",
    0, -5,
    effects={"spell_power_from_agility_pct": 0.30,
             "crit_chance_spell_from_intellect_pct": 0.15},
    connect=["aggramars_rage"],
    source="CoA's level 20 passive, verbatim: 'Increases your spell power by "
           "30% of your Agility and your critical strike rating by 15% of "
           "your Intellect.' PORTS WHOLE - spell_power and crit_chance_spell "
           "are both in STAT_CONVERSION_TARGETS, agility and intellect both "
           "in STAT_CONVERSION_SOURCES. The third double conversion in "
           "Templar, after Zealot's Calm Combatant and Oathkeeper's Graceful "
           "Fighter. Both are FRACTIONS."))

N.append(node(
    "aggramars_rage", "Aggramar's Rage",
    "Increases your spell critical strike chance by 6% and your expertise by "
    "10.",
    0, -3,
    effects={"crit_chance_spell": 6.0, "expertise": 10.0},
    connect=["pure_focus"],
    source="CoA over 2 ranks: 'Increases your Holy critical strike chance by "
           "3% and your expertise by 5.' Doubled for the two ranks. There is "
           "no per-school crit key, so Holy crit becomes spell crit - this "
           "spec's spell damage is all Holy. BOTH HALVES PORT because "
           "creature avoidance went in earlier today, making `expertise` a "
           "real stat; before that it reduced a target dodge and parry that "
           "did not exist. Both keys are PERCENT."))

N.append(node(
    "pure_focus", "Pure Focus",
    "Increases your chance to hit by 4% and the damage of Chastise by 10%.",
    0, -1,
    effects={"hit_rating": 4.0, "ability_templar_chastise_damage": 0.10},
    connect=["chivalric"],
    source="CoA over 2 ranks: 'Increases the chance to trigger Scourgebane by "
           "5% and your chance to hit by 2%.' FRONTIER HAS NO SCOURGEBANE "
           "ABILITY, and a 'chance to trigger' it would need the proc that "
           "does not exist either. The hit half is doubled for the two ranks "
           "and ports; the Scourgebane half is re-pointed at Chastise, which "
           "CoA's Righteousness node pairs with Scourgebane."))

N.append(node(
    "chivalric", "Chivalric",
    "Increases your critical strike damage by 15%.",
    0, 1,
    effects={"crit_damage_physical": 0.15},
    connect=["paladin_training"],
    source="CoA verbatim: 'Increases your critical damage with Holy spells "
           "and abilities by 15%.' No per-school crit damage key exists, so "
           "it lands on the physical side - this spec's damage is weapon "
           "strikes typed Holy, and crit_damage_physical is what scales "
           "them. A FRACTION, unlike crit_chance_physical which is a "
           "PERCENT."))

N.append(node(
    "paladin_training", "Paladin Training",
    "Increases the damage of Righteous Lunge and Argent Blade by 20%.",
    0, 3,
    effects={"ability_templar_righteous_lunge_damage": 0.20,
             "ability_templar_argent_blade_damage": 0.20},
    connect=["warrior_of_tyr"],
    source="CoA verbatim: 'Increases the damage of Righteous Lunge and Argent "
           "Blade by 20%.' Ports exactly - both abilities exist in Frontier "
           "and both are combo generators."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "warrior_of_tyr", "Warrior of Tyr",
    "Your strikes have a 10% chance to restore 5 combo.",
    1, -4,
    proc={"trigger": "on_damage_cast", "chance": 10, "icd": 0,
          "ability_filter": BUILDERS,
          "grant_resource": {"resource": "combo", "amount": 5}},
    connect=["retribution"],
    source="CoA verbatim: 'Periodic damage dealt now has a 10% chance to "
           "generate 5 Energy.' Periodic damage has no trigger, so it fires "
           "off casts. CoA's Energy is Frontier's COMBO, a real primary pool "
           "(abilities.py:164) with six generators - so there IS somewhere "
           "for this to go, verified on the Zealot tree through "
           "gain_resource. CoA's 10% and 5 both kept."))

N.append(node(
    "retribution", "Retribution",
    "Your strikes have a 20% chance to echo, striking again for 60% of the "
    "damage dealt.",
    1, -2,
    proc={"trigger": "on_damage_cast", "chance": 20, "icd": 0,
          "ability_filter": BUILDERS,
          "bonus_pct": 0.60},
    connect=["warrior_of_dawn"],
    source="CoA verbatim: 'Melee damage dealt now has a 20% chance to strike "
           "2 additional times for 30% of the damage dealt as Holy Damage.' "
           "USES bonus_pct, which adds a percentage of the TRIGGERING HIT's "
           "own amount to that same hit - one of only three payloads that "
           "read the damage dealt. Two strikes at 30% is 60%, and CoA's 20% "
           "chance is exact. WHAT IS LOST IS THE HOLY TYPING: bonus_pct folds "
           "into the same hit and takes no school, unlike damage_flat, so the "
           "extra damage inherits the strike's own school. Same payload as "
           "Pyromancer Draconic's Aspect of Time."))

N.append(node(
    "warrior_of_dawn", "Warrior of Dawn",
    "Your strikes have a 10% chance to ready Argent Blade again.",
    1, 0,
    proc={"trigger": "on_damage_cast", "chance": 10, "icd": 0,
          "ability_filter": BUILDERS,
          "reset_cooldown": ["templar_argent_blade"]},
    connect=["scourge_defense_training"],
    source="CoA verbatim: 'Melee damage dealt now has a 10% chance to reset "
           "the cooldown and reduce the Energy cost of your next Argent Blade "
           "by -50%.' The reset ports exactly - reset_cooldown as a BARE LIST "
           "means a full reset, and CoA's 10% is kept. The cost reduction on "
           "a NAMED NEXT CAST has no mechanism, so it is dropped rather than "
           "made permanent; Scourge-Defense Training below carries the "
           "empowerment half instead."))

N.append(node(
    "scourge_defense_training", "Scourge-Defense Training",
    "Increases the damage of Argent Blade by 20% and its critical strike "
    "chance by 20%.",
    1, 2,
    effects={"ability_templar_argent_blade_damage": 0.20,
             "ability_templar_argent_blade_crit": 20.0},
    connect=["righteousness"],
    source="CoA verbatim: 'Warrior of Dawn now also increases the damage and "
           "critical strike chance of your next Argent Blade by 20%.' A "
           "talent modifying another talent's proc to empower a named next "
           "cast fails twice over. Granted flat on the ability itself at "
           "CoA's own 20% for both halves - which is what the empowerment "
           "delivered, without the setup. Note the units differ: "
           "ability_*_damage is a FRACTION, ability_*_crit a PERCENT."))

N.append(node(
    "righteousness", "Righteousness",
    "Chastise leaves the enemy taking 10% more damage for 3 turns.",
    1, 4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["templar_chastise"],
          "apply_effect": {"effect_id": "templar_righteousness",
                           "name": "Righteousness", "effect_type": "debuff",
                           "duration": 3, "max_stacks": 1,
                           "stat_mods": {"damage_taken_pct": 0.10},
                           "on_target": True}},
    connect=["teachings_of_the_cathedral"],
    source="CoA verbatim: 'Your Chastise now always triggers Scourgebane on "
           "your target.' FRONTIER HAS NO SCOURGEBANE, so there is nothing to "
           "trigger. Rebuilt as the debuff a guaranteed Scourgebane "
           "represented - Chastise marking a target for more damage. BARE "
           "damage_taken_pct IS READ RAW, so 10% is 0.10; authoring 10.0 "
           "would be +1000% damage taken."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "teachings_of_the_cathedral", "Teachings of the Cathedral",
    "Increases your critical strike chance by 5%.",
    2, -4,
    effects={"crit_chance_physical": 5.0},
    connect=["tyrs_blessing"],
    source="CoA verbatim: 'Your Oath: Condemn now provides 5% additional "
           "critical strike chance.' Oaths do not exist (see the Zealot "
           "builder) and NOTHING READS ANOTHER EFFECT'S STACK COUNT, so a "
           "talent that improves what a Condemn stack provides has nothing to "
           "improve. Granted as flat crit at CoA's own 5%. This is the first "
           "of four Condemn-stack talents in this tree, all re-pointed."))

N.append(node(
    "tyrs_blessing", "Tyr's Blessing",
    "Increases the damage of Condemn by 25%.",
    2, -2,
    effects={"ability_templar_condemn_damage": 0.25},
    connect=["templars_might"],
    source="CoA verbatim: 'Condemn now stacks 1 additional time.' NO KEY "
           "MODIFIES ANOTHER EFFECT'S max_stacks - the same wall that took "
           "Venomancer Fortitude's Beetle Poison and Pyromancer "
           "Incineration's Flames of Focus - so an extra stack cannot be "
           "granted. Re-pointed at Condemn's damage, which is what another "
           "stack was worth."))

N.append(node(
    "templars_might", "Templar's Might",
    "Increases the damage of Righteous Lunge and Chastise by 30%.",
    2, 0,
    effects={"ability_templar_righteous_lunge_damage": 0.30,
             "ability_templar_chastise_damage": 0.30},
    connect=["scarlet_secrets"],
    source="CoA verbatim: 'Your Righteous Lunge and Chastise used on enemies "
           "affected by your Condemn now deal 6% increased damage per stack.' "
           "Two walls: no effect key reads whether a target carries a debuff, "
           "and nothing reads a stack count. Five Condemn stacks at 6% is "
           "30%, granted flat - the ceiling a fully-stacked target would have "
           "reached."))

N.append(node(
    "scarlet_secrets", "Scarlet Secrets",
    "Your critical strikes raise your critical strike chance by 5% for 4 "
    "turns, stacking 3 times.",
    2, 2,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "templar_oath_retribution",
                           "name": "Oath: Retribution",
                           "effect_type": "buff", "duration": 4,
                           "max_stacks": 3,
                           "stat_mods": {"crit_chance_physical": 5.0},
                           "on_target": False}},
    connect=["focused"],
    source="CoA verbatim: 'Every 2nd cast of Argent Blade now grants you "
           "Oath: Retribution. Critical damage increased by 5%.' THERE IS NO "
           "CAST COUNTER - nothing tracks 'every Nth cast of X', the same "
           "wall as Venomancer Stalking's Widow's Kiss - so it fires on crits "
           "instead, which a Crusader does often. CoA's 5% kept and allowed "
           "to stack 3 times to give the node a ramp. INSIDE A STATUS EFFECT "
           "crit_damage_physical takes percentage POINTS, so 5.0 is 5% - "
           "while the SAME KEY on Chivalric at tier 0 is a FRACTION at "
           "0.15."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "focused", "Focused",
    "Increases the damage of Blade of Faith and Righteous Tempest by 25%.",
    3, -4,
    effects={"ability_templar_blade_of_faith_damage": 0.25,
             "ability_templar_righteous_tempest_damage": 0.25},
    connect=["holy_tempest"],
    source="CoA verbatim: 'Increases the damage of Blade of Faith and "
           "Righteous Tempest by 25%.' Ports exactly - both exist in "
           "Frontier. Righteous Tempest is unlocked at tier 4 below, so this "
           "node is worth taking alongside it."))

N.append(node(
    "holy_tempest", "Holy Tempest",
    "Righteous Tempest splashes 40% of its damage onto up to 3 nearby "
    "enemies.",
    3, -2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["templar_righteous_tempest"],
          "splash_damage": {"pct": 0.40, "max_targets": 3,
                            "school": "holy"}},
    connect=["judgement"],
    source="CoA verbatim: 'Damage dealt by Righteous Tempest now spreads "
           "Condemn on affected enemies to a nearby enemy.' SPREADING A "
           "DEBUFF TO A NEW TARGET IS NOT A PAYLOAD - apply_effect lands on "
           "the trigger's own target - so it becomes splash_damage, the same "
           "translation as the Witch Doctor's Malignant and Pyromancer "
           "Draconic's Overwhelming Flames."))

N.append(node(
    "judgement", "Judgement",
    "Increases the damage of Scarlet Hammer and Titanstrike by 25%.",
    3, 0,
    effects={f"ability_{a}_damage": 0.25 for a in EXECUTES},
    connect=["crusaders_brand"],
    source="CoA verbatim: 'Increases the damage of Scourgebane, Scarlet "
           "Hammer, and Titanstrike by 25% on enemies below 20% health.' "
           "Scourgebane does not exist in Frontier. NO EFFECT KEY READS A "
           "TARGET'S HEALTH PERCENTAGE - high_health_damage_threshold_pct is "
           "dead and the working low_health pair on Venomancer Fortitude is "
           "about the carrier's own health - so the execute condition is "
           "dropped and CoA's 25% applies always."))

N.append(node(
    "crusaders_brand", "Crusader's Brand",
    "Your strikes brand the enemy, so their own attacks burn them for holy "
    "damage.",
    3, 2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": BUILDERS,
          "apply_effect": {"effect_id": "templar_crusaders_brand",
                           "name": "Crusader's Brand", "effect_type": "dot",
                           "duration": 3, "potency": 36,
                           "damage_school": "holy", "on_target": True}},
    connect=["righteous_tempest"],
    source="CoA verbatim: 'Brand an enemy for 20 seconds, preventing them "
           "from mounting, fleeing, or increasing their movement speed above "
           "normal, and when they deal direct damage they take Holy Damage. "
           "While marked enemies can always be seen by the Crusader even "
           "while stealthed or invisible.' Frontier HAS Crusader's Brand as "
           "an ability and it is not gated. NOTHING TRIGGERS ON THE TARGET "
           "DEALING DAMAGE - there is no attacker-side retaliation hook on a "
           "debuff - so the brand becomes a dot, which burns them on the same "
           "schedule without needing them to swing. Movement and stealth are "
           "not modelled."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "righteous_tempest", "Righteous Tempest",
    "Teaches Righteous Tempest, a whirling holy strike that hits everything "
    "nearby.",
    4, -3,
    effects={"unlock_ability": "templar_righteous_tempest"},
    connect=["whirling_tempest"],
    source="CoA verbatim: 'Unleash a whirling Oath Breaker, dealing Weapon "
           "Damage plus spell damage to nearby enemies every 1 sec for 3 sec. "
           "Consumes your Oaths, dealing additional damage for each "
           "consumed.' LOAD-BEARING UNLOCK: templar_righteous_tempest carries "
           "requires_talent, so without this node it is unobtainable "
           "forever. It is the ONLY one of Templar's three gated abilities "
           "not at tier 6 - Zealot's Norgannon's Wrath and Oathkeeper's Tome "
           "of Light are both capstones - and it is kept at tier 4 exactly "
           "where the shipped tree had it. The Oath consumption lives on the "
           "ability or not at all."))

N.append(node(
    "whirling_tempest", "Whirling Tempest",
    "Increases your haste by 8%.",
    4, -1,
    effects={"haste": 8.0},
    connect=["scarlet_training"],
    source="CoA verbatim: 'While Righteous Tempest is active you gain 20% "
           "increased movement speed.' MOVEMENT SPEED IS NOT MODELLED and "
           "there is no 'while active' gate either. Rerouted to haste, which "
           "is what speed means in a turn-based fight - acting more often. "
           "NOT a faithful copy and flagged as such."))

N.append(node(
    "scarlet_training", "Scarlet Training",
    "Increases all damage you deal by 10%.",
    4, 1,
    effects={"all_damage": 0.10},
    connect=["holy_fervor"],
    source="CoA's own description for this node is the unresolved token "
           "'$66' - the Builder payload never expands it - so there is no "
           "verbatim text and this is NOT a faithful copy. Named from CoA's "
           "own title and built as flat damage. Flagged so a later pass can "
           "correct it; the same situation as Zealot's Divine Fury ('$64'), "
           "Incineration's Magmatic ('$8a') and Draconic's Draconic Aspect "
           "('$8e')."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "holy_fervor", "Holy Fervor",
    "Argent Blade heals you for 30% of the damage it deals.",
    5, -3,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["templar_argent_blade"],
          "leech_pct": {"pct": 0.30}},
    connect=["templar_zeal"],
    source="CoA's Argent Blade: 'Crush an enemy with argent fervor, dealing "
           "Weapon Damage plus holy spell power, healing you equal to the "
           "damage dealt, and extending the duration of your Oath Chain by 3 "
           "sec.' The self-heal is the ability's own in CoA; this node makes "
           "it a talent because leech_pct READS THE TRIGGERING HIT'S AMOUNT, "
           "so the scaling is real. Priced at 30% rather than CoA's 100%, "
           "which on a 160%-weapon-damage strike would make the spec a tank. "
           "The Oath Chain extension cannot be built."))

N.append(node(
    "templar_zeal", "Templar's Zeal",
    "Increases the critical strike chance of your strikes by 8%.",
    5, -1,
    effects={f"ability_{a}_crit": 8.0 for a in BUILDERS},
    connect=["crusading_strike"],
    source="CoA's Pure Focus and Aggramar's Rage both point at crit, and this "
           "node carries the per-ability version neither does - written out "
           "across all six combo builders, since no key names a group. NOT a "
           "direct port of a single CoA talent: built so tier 5 carries a "
           "real stat node for the rotation rather than a fourth flat damage "
           "line, and flagged as such."))

N.append(node(
    "crusading_strike", "Crusading Strike",
    "Your critical strikes strike again for holy damage.",
    5, 1,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "ability_filter": BUILDERS,
          "damage_flat": 85, "school": "holy"},
    connect=["titanstrike_mastery"],
    source="Built from CoA's Retribution theme - 'strike additional times as "
           "Holy Damage' - but as a FLAT holy strike rather than a bonus_pct, "
           "deliberately: Retribution at tier 1 already uses bonus_pct, and a "
           "damage_flat payload is the only way to get HOLY TYPING, since "
           "bonus_pct folds into the triggering hit and inherits its school. "
           "So the two nodes read differently in play. NOT a direct port of a "
           "single CoA talent and flagged as such. 1-turn icd."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "titanstrike_mastery", "Titanstrike",
    "Increases the damage of Titanstrike and Scarlet Hammer by 50%, and all "
    "damage you deal by 10%.",
    6, 0,
    effects={**{f"ability_{a}_damage": 0.50 for a in EXECUTES},
             "all_damage": 0.10},
    source="Templar's three gated abilities are one per tree and this tree's "
           "sits at tier 4 (Righteous Tempest), so unlike Zealot and "
           "Oathkeeper this capstone grants no ability - it is a pure payoff "
           "node. Built on CoA's execute pair, Titanstrike and Scarlet "
           "Hammer, which Judgement at tier 3 also feeds, plus flat damage. "
           "The shipped tree had no tier-6 node at all for Crusader, so this "
           "is new rather than a rebuild, and it is NOT a port of a specific "
           "CoA talent - flagged as such."))


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
    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Templar Crusader: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points, {len(GATED)} load-bearing unlock")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
