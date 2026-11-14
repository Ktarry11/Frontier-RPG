#!/usr/bin/env python3
"""Rebuild Guardian's Gladiator tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_guardian_gladiator.py [--check]

SOURCE: data/reference/coa_worksheets/guardian.md and
data/reference/coa/guardian.json - 33 real Gladiator talents from
Ascension's own CoA Builder payload. Role: DPS.

WHAT THE SPEC IS. A sword-and-board DPS that turns defensive stats into
offence: Shield Training gives block rating from Strength, Shield Combat
turns block rating into attack power, and Centurion Strike is the engine.
Energy is the resource.

THERE IS NO "WHILE X IS EQUIPPED" GATE. CoA's four Training nodes - Sword,
Axe, Mace, Polearm, twelve ranks between them - each apply only while that
weapon class is held. No key reads the equipped weapon's type:
requires_weapon, requires_weapon_type and weapon_type-as-a-talent-
condition are all absent (weapon_type exists only in entities/boss_loot.py,
for generating items). So all four are built UNCONDITIONAL and priced
DOWN accordingly - roughly half CoA's value, since CoA charges for a
bonus you only get with the right weapon and this one is always on. The
player still chooses between them, so the node that matches their weapon
is the one worth taking; it just no longer stops working when they swap.

DEAD KEYS THIS TREE WANTED. `expertise` is read by nothing, which takes
half of Double Duty - the second CoA tree in a row to want it. `max_energy`
is read only in entities/pet.py, never for a character, which takes
Retiarius entirely; the primary resource pool is not talent-settable, the
same shape as max_rage being hardcoded at 100 and Vanguard's
max_energy_bonus.

ARMOR PENETRATION IS LIVE, read in entities/monster.py, which is what
saves Mace Training.

CONVENTIONS, which do not agree with each other:
  attack_power_pct, strength_pct, stamina_pct, agility_pct,
    armor_penetration_pct                        percentage POINTS
  all_damage, physical_damage, dot_damage, crit_damage_physical,
    ability_*_damage, ability_*_crit_damage      FRACTION
  crit_chance_physical, haste, hit_rating, block,
    ability_*_crit                               PERCENT
  block_value_pct      FRACTION on BOTH sides
  healing_taken_pct inside a status effect       percentage POINTS
  *_cost_pct / *_cooldown_pct  FRACTION, POSITIVE MEANS A REDUCTION

TURN-BASED CUTS. Every yard, which takes Polearm Training's whole stated
bonus and half of No Retreating!. Charges have no system, which takes
Supremacy as written and Heroism. Rooted-target conditions (No Escape) and
debuff-presence conditions (Clinch Brawler, Pinned Down!) cannot be read -
no effect key asks whether a target carries an effect.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/guardian_gladiator.json"

#: The spec's two signature strikes.
SIGNATURE = ["guardian_centurion_strike", "guardian_reprisal"]

#: Everything that spends Energy on a swing.
SPENDERS = ["guardian_broad_sweep", "guardian_spear_throw",
            "guardian_centurion_strike"]

TREE = {
    "spec_name": "Guardian Gladiator",
    "tree_id": "guardian_gladiator",
    "description": ("Sword, shield and spear - a duellist who turns block "
                    "rating into attack power."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from the 33 real CoA Gladiator talents (role "
        "DPS), completing Guardian - the worst-measuring class of the 16 "
        "that remained, at 84% scalar-only nodes. NO 'WHILE X IS EQUIPPED' "
        "GATE EXISTS, so CoA's four weapon Training nodes are built "
        "unconditional at roughly half value. Dead keys it wanted: "
        "`expertise` (half of Double Duty, the second CoA tree in a row to "
        "want it) and `max_energy` for a character (all of Retiarius). "
        "armor_penetration_pct IS live, which saves Mace Training."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"guardian_gladiator_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"guardian_gladiator_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "might", "Might",
    "Increases your attack power by 10%.",
    0, -5,
    effects={"attack_power_pct": 10.0},
    connect=["built_different"],
    source="CoA over 2 ranks: 'Increases your attack power by 5%.' Doubled "
           "for the two ranks and authored as the full-investment ceiling. "
           "Percentage POINTS."))

N.append(node(
    "built_different", "Built Different",
    "Increases your Strength and Stamina by 4%.",
    0, -3,
    effects={"strength_pct": 4.0, "stamina_pct": 4.0},
    connect=["sword_training"],
    source="CoA verbatim: 'Increases your Strength and Stamina by 4%.' Both "
           "keys take percentage POINTS. Strength matters doubly here - the "
           "spec's level 20 passive turns it into block rating and its level "
           "40 passive turns block rating back into attack power."))

N.append(node(
    "sword_training", "Sword Training",
    "Increases your melee haste by 15%.",
    0, -1,
    effects={"haste": 15.0},
    connect=["axe_training"],
    source="CoA over 3 ranks: 'While a sword is equipped, your melee haste is "
           "increased by 10%.' NO WEAPON-TYPE GATE EXISTS, so this is "
           "unconditional. CoA's three ranks would be 30% haste; priced at "
           "15% because CoA charges for a bonus that stops working when you "
           "swap weapons and this one never does. Authored as the CEILING at one "
           "rank and spread to 3 by the rank policy - hand-authoring ranks=3 "
           "would have kept 15.0 per rank and delivered 45%, since "
           "get_effective_effects() multiplies by points spent. PERCENT."))

N.append(node(
    "axe_training", "Axe Training",
    "Increases your critical strike chance by 3% and your critical strike "
    "damage by 8%.",
    0, 1,
    effects={"crit_chance_physical": 3.0, "crit_damage_physical": 0.08},
    connect=["mace_training"],
    source="CoA over 3 ranks: 'While an axe is equipped, your critical strike "
           "chance is increased by 2% and critical damage increased by 5%.' "
           "Unconditional and halved, as Sword Training above - CoA's three "
           "ranks would be 6% and 15%. TWO UNITS IN ONE BLOCK: "
           "crit_chance_physical is a PERCENT, crit_damage_physical a "
           "FRACTION."))

N.append(node(
    "mace_training", "Mace Training",
    "Increases your armour penetration by 12%.",
    0, 3,
    effects={"armor_penetration_pct": 12.0},
    connect=["polearm_training"],
    source="CoA over 3 ranks: 'While a mace is equipped, your armor "
           "penetration is increased by 8%.' Unconditional and halved - CoA's "
           "three ranks would be 24%. armor_penetration_pct IS live, read in "
           "entities/monster.py, which is the only reason this node survives "
           "at all; it takes percentage POINTS."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "polearm_training", "Polearm Training",
    "Increases your physical damage by 9%.",
    1, -4,
    effects={"physical_damage": 0.09},
    connect=["upper_hand"],
    source="CoA over 3 ranks: 'Allows you to wield polearms and to wield them "
           "with a shield equipped. While a polearm is equipped, your melee "
           "abilities have 2 yds increased range.' BOTH HALVES ARE "
           "UNBUILDABLE: equip rules live on items, not talents, and there is "
           "no positioning in this engine, so increased range means nothing. "
           "Rerouted to flat physical damage so the node is worth a point at "
           "all - the one Training node whose CoA bonus had nothing behind "
           "it, rather than just no gate."))

N.append(node(
    "legionnaire", "Legionnaire",
    "Increases the critical strike damage of Centurion Strike and Reprisal "
    "by 20%.",
    1, -2,
    effects={f"ability_{a}_crit_damage": 0.20 for a in SIGNATURE},
    connect=["upper_hand"],
    source="CoA over 2 ranks: 'Increases the critical damage of Centurion "
           "Strike and Reprisal by 10%.' Doubled for the two ranks. Both "
           "abilities exist in Frontier. ability_*_crit_damage is a FRACTION, "
           "unlike ability_*_crit beside it in other nodes, which is a "
           "PERCENT."))

N.append(node(
    "crashing_force", "Crashing Force",
    "Increases the damage of Centurion Strike and Reprisal by 30%.",
    1, 0,
    effects={f"ability_{a}_damage": 0.30 for a in SIGNATURE},
    connect=["tactical_combat"],
    source="CoA over 2 ranks: 'Increases the damage of your Centurion Strike "
           "and Reprisal by 15%.' Doubled for the two ranks."))

N.append(node(
    "double_duty", "Double Duty",
    "Increases your chance to hit by 5% and your expertise by 4.",
    1, 2,
    effects={"hit_rating": 5.0, "expertise": 4.0},
    connect=["tactical_combat"],
    source="CoA verbatim: 'Increases your hit chance by 5% and expertise by "
           "4.' BOTH HALVES NOW PORT. This was the second CoA tree in a row "
           "to want `expertise` - Vanguard's Stalwart wanted the same 4 - and "
           "flagging it as a pattern rather than a one-off is what prompted "
           "Kyle to have creature avoidance encoded (dodge on every creature "
           "template, parry on humanoids only, block as a hook for "
           "shield-carrying humanoids). 20 CoA talents across 11 classes want "
           "the stat, so it is now live for the 8 of those classes still to "
           "be rebuilt. The two halves are NOT duplicates: hit_rating beats "
           "the attacker-side hit roll, expertise reduces the target's dodge "
           "and parry, which are separate checks."))

N.append(node(
    "upper_hand", "Upper Hand",
    "Your weapon swings have a 20% chance to strike an extra time.",
    1, 4,
    proc={"trigger": "on_weapon_swing", "chance": 20, "icd": 0,
          "extra_attack": True},
    connect=["waste_no_movement"],
    source="CoA verbatim: 'Your melee auto attacks now have a 20% chance to "
           "strike 2 additional times.' on_weapon_swing is the live auto-"
           "attack trigger and extra_attack is a live BOOLEAN payload - it "
           "grants one extra attack, not a count, so CoA's '2 additional "
           "times' cannot be expressed. CoA's 20% kept."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "tactical_combat", "Tactical Combat",
    "Increases your block value by 16% and your chance to block by 4%.",
    2, -4,
    effects={"block_value_pct": 0.16, "block": 4.0},
    connect=["supremacy"],
    source="CoA over 2 ranks: 'Increases your block value by 8% and chance to "
           "block by 2%.' Doubled for the two ranks. A DPS spec wanting block "
           "is not a mistake here - Shield Combat, the spec's level 40 "
           "passive, turns block rating into attack power. TWO UNITS: "
           "block_value_pct is a raw FRACTION on both sides of the talent/"
           "status divide, while `block` is a PERCENT added to the base "
           "chance; block_chance is DEAD."))

N.append(node(
    "waste_no_movement", "Waste No Movement",
    "Reduces the Energy cost of Broad Sweep, Spear Throw and Centurion "
    "Strike by 15%.",
    2, -2,
    effects={f"ability_{a}_cost_pct": 0.15 for a in SPENDERS},
    connect=["champion"],
    source="CoA verbatim: 'Reduces the Energy cost of Broad Sweep, Spear "
           "Throw, and Centurion Strike by -5.' A flat 5 Energy is expressed "
           "as a percentage because costs differ per ability and per rank. "
           "POSITIVE reduces, so CoA's minus sign is dropped."))

N.append(node(
    "myrmidon", "Myrmidon",
    "Increases the damage of Ram and Broad Sweep by 25%.",
    2, 0,
    effects={"ability_guardian_ram_damage": 0.25,
             "ability_guardian_broad_sweep_damage": 0.25},
    connect=["bulwark_rush"],
    source="CoA verbatim: 'Increases the damage of Ram and Broad Sweep by "
           "25%.' Ports exactly."))

N.append(node(
    "one_handed_mastery", "One-Handed Mastery",
    "Increases all damage you deal by 10%.",
    2, 2,
    effects={"all_damage": 0.10},
    connect=["deadly_blow"],
    source="CoA verbatim: 'Increases your damage dealt by 10% while a "
           "one-handed weapon is equipped.' No weapon-type gate exists, as "
           "with the four Training nodes, so this is unconditional. Kept at "
           "CoA's full 10% rather than halved, because a sword-and-board DPS "
           "is holding a one-hander in every build this tree supports - the "
           "condition was nearly always true rather than a real choice."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "supremacy", "Supremacy",
    "Centurion Strike resets the cooldown of Reprisal.",
    3, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["guardian_centurion_strike"],
          "reset_cooldown": ["guardian_reprisal"]},
    connect=["momentum"],
    source="CoA verbatim: 'Casting Centurion Strike now refreshes a charge of "
           "Reprisal.' THERE IS NO CHARGE SYSTEM - abilities have a cooldown, "
           "not a pool of charges - so refreshing a charge becomes a full "
           "cooldown reset, which is the single-charge equivalent. "
           "reset_cooldown as a BARE LIST means a full reset."))

N.append(node(
    "champion", "Champion",
    "Increases the duration of Raise Shield by 1 turn.",
    3, -2,
    effects={"ability_guardian_raise_shield_duration": 1},
    connect=["momentum"],
    source="CoA verbatim: 'Your Centurion Strike now extends the duration of "
           "Raise Shield on you by 3 sec.' No payload extends a live effect's "
           "duration, so it is built as a flat duration bonus on Raise Shield "
           "itself - the same outcome without the trigger. 3 sec is a turn. "
           "The small integer keeps this node out of the rank policy's "
           "reach."))

N.append(node(
    "bulwark_rush", "Bulwark Rush",
    "Battle Rush braces you, raising your block value by 20% for 2 turns.",
    3, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["guardian_battle_rush"],
          "apply_effect": {"effect_id": "guardian_bulwark_rush",
                           "name": "Bulwark Rush", "effect_type": "buff",
                           "duration": 2, "max_stacks": 1,
                           "stat_mods": {"block_value_pct": 0.20},
                           "on_target": False}},
    connect=["deadly_blow"],
    source="CoA verbatim: 'Casting Battle Rush increases your block rating by "
           "25% of Strength for 6 seconds.' A payload cannot read a stat into "
           "a stat_mod, so the Strength scaling becomes a flat percentage. 6 "
           "sec is 2 turns. block_value_pct IS READ RAW INSIDE A STATUS "
           "EFFECT as well as outside it, so 20% is 0.20 - authoring 20.0 "
           "would be 2000%, which is exactly what audit_talents caught on "
           "Vanguard's Iron Barrier earlier today."))

N.append(node(
    "deadly_blow", "Deadly Blow",
    "Centurion Strike and Broad Sweep leave the enemy bleeding for physical "
    "damage over 2 turns.",
    3, 2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["guardian_centurion_strike",
                             "guardian_broad_sweep"],
          "apply_effect": {"effect_id": "guardian_deadly_blow",
                           "name": "Deadly Blow", "effect_type": "dot",
                           "duration": 2, "potency": 36,
                           "damage_school": "physical", "on_target": True}},
    connect=["no_retreating"],
    source="CoA verbatim: 'Your Centurion Strike and Broad Sweep now bleed an "
           "additional 20% of the damage dealt over 2 seconds.' A bleed IS a "
           "dot, so this ports closely. The potency is flat rather than a "
           "share of the hit, because an apply_effect payload cannot read the "
           "triggering ability's damage. NOTE the effect is a dot with a "
           "physical school rather than anything named 'bleed' - "
           "`bleed_dot_damage` is a dead key, confirmed earlier this session "
           "when no ability id contained 'bleed'."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "momentum", "Momentum",
    "Your strikes bring Centurion Strike a turn closer to ready.",
    4, -3,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
          "ability_filter": ["guardian_pulverize", "guardian_ram",
                             "guardian_broad_sweep"],
          "reset_cooldown": {"abilities": ["guardian_centurion_strike"],
                             "turns": 1}},
    connect=["heroic_effort"],
    source="CoA verbatim: 'Melee damage dealt now reduces the cooldown of "
           "your Chivlary by -2 sec.' FRONTIER HAS NO CHIVALRY ABILITY (CoA's "
           "own spelling), so the target cannot exist. Re-pointed at "
           "Centurion Strike, this spec's engine ability and the thing every "
           "other node in the tree feeds. 2 sec is a turn, with a 1-turn "
           "internal cooldown so a multi-hit turn does not stack reductions."))

N.append(node(
    "no_escape", "No Escape",
    "Ram brings Battle Rush three turns closer to ready.",
    4, -1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["guardian_ram"],
          "reset_cooldown": {"abilities": ["guardian_battle_rush"],
                             "turns": 3}},
    connect=["heroic_effort"],
    source="CoA verbatim: 'Ram now reduces the cooldown of your Battle Rush "
           "by 10 sec when used against a rooted enemy.' THE ROOTED CONDITION "
           "CANNOT BE READ - no effect key asks whether a target carries an "
           "effect, the same wall that took seven Witch Doctor talents - so "
           "it fires on any Ram. 10 sec is 3 turns."))

N.append(node(
    "pinned_down", "Pinned Down!",
    "Spear Throw pins the target, reducing the healing they receive by 30% "
    "for 3 turns.",
    4, 1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["guardian_spear_throw"],
          "apply_effect": {"effect_id": "guardian_pinned_down",
                           "name": "Pinned Down!", "effect_type": "debuff",
                           "duration": 3, "max_stacks": 1,
                           "stat_mods": {"healing_taken_pct": -30.0},
                           "on_target": True}},
    connect=["clinch_brawler"],
    source="CoA verbatim: 'Damage dealt by Spear Throw now refreshes the "
           "duration of Net Throw on your target.' No payload extends or "
           "refreshes an existing effect on a target. Rebuilt from CoA's own "
           "Spear Throw ability text instead - 'reducing the effectiveness of "
           "any healing by -50% for 10 seconds' - which is the same tool "
           "(Spear Throw locking a target down) expressed with a live key. "
           "Priced at 30% rather than 50% because it is permanent here "
           "rather than a 10-second window. INSIDE A STATUS EFFECT "
           "healing_taken_pct is percentage POINTS, so -30% is -30.0; as a "
           "talent effect the same key is a FRACTION."))

N.append(node(
    "heroic_effort", "Heroic Effort",
    "Centurion Strike grants Glory, raising your damage by 4% per stack for "
    "5 turns, stacking 3 times.",
    4, 3,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["guardian_centurion_strike"],
          "apply_effect": {"effect_id": "guardian_glory",
                           "name": "Glory", "effect_type": "buff",
                           "duration": 5, "max_stacks": 3,
                           "stat_mods": {"damage_dealt_pct": 4.0},
                           "on_target": False}},
    connect=["clinch_brawler"],
    source="CoA verbatim: 'Casting Centurion Strike now grants 1 stack of "
           "Glory.' Glory is the spec's level 10 passive in CoA ('Your Ram now "
           "grants you a stack of Glory. At 3 stacks, your next Ram deals "
           "150% increased damage'). THE 3-STACK THRESHOLD CANNOT BE READ - "
           "nothing reads another effect's stack count - so Glory is built as "
           "a plain ramp: 3 stacks of 4% is 12% damage at cap, reached by "
           "casting rather than by a payoff cast. CoA's Heroism node, which "
           "keys on 'whenever you reach 3 stacks of Glory or 20 stacks of "
           "Favor', is NOT built for the same reason - two stack thresholds "
           "and a free-next-cast, none of which exist."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "clinch_brawler", "Clinch Brawler",
    "Increases the critical strike chance of Centurion Strike by 25%.",
    5, -3,
    effects={"ability_guardian_centurion_strike_crit": 25.0},
    connect=["final_verdict_mastery"],
    source="CoA verbatim: 'Centurion Strike is now guaranteed to critically "
           "strike against enemies affected by Net Throw.' A GUARANTEED CRIT "
           "HAS NO KEY and the debuff condition cannot be read, so a flat "
           "crit bonus is the honest nearest thing. Priced at 25% rather than "
           "100%, since it applies always rather than only after a Net "
           "Throw. ability_*_crit is a PERCENT."))

N.append(node(
    "no_retreating", "No Retreating!",
    "Increases the damage of Spear Throw by 45%.",
    5, -1,
    effects={"ability_guardian_spear_throw_damage": 0.45},
    connect=["final_verdict_mastery"],
    source="CoA verbatim: 'While in combat, every 2 sec, increase the range "
           "and Energy cost of your next Spear Throw by 1 and its damage "
           "dealt by 3%, stacking up to 15 times.' Three walls: there is no "
           "periodic trigger to tick a stack on, no key adds to a cost, and "
           "range means nothing. Fifteen stacks of 3% is 45%, granted flat - "
           "the same ceiling a full ramp would have reached, without the "
           "wind-up or the rising cost."))

N.append(node(
    "earthsplitter", "Earthsplitter",
    "Broad Sweep splits the ground, splashing 40% of its damage onto up to 3 "
    "nearby enemies, and costs 20% less.",
    5, 1,
    effects={"ability_guardian_broad_sweep_cost_pct": 0.20},
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["guardian_broad_sweep"],
          "splash_damage": {"pct": 0.40, "max_targets": 3,
                            "school": "physical"}},
    connect=["final_verdict_mastery"],
    source="CoA verbatim: 'Casting Broad Sweep now increases the amount of "
           "enemies struck by your next Broad Sweep by 1 and reduces its "
           "Energy cost by 10% for 6 sec, stacking 3 times.' NO KEY ADDS "
           "TARGETS TO AN ABILITY - the count lives on the ability - so the "
           "growing cleave becomes splash_damage, which is how every "
           "added-targets talent in this audit has been built. Three stacks "
           "of 10% cost is 20% (held below the full 30% because it is "
           "permanent rather than a 6-second window), and three stacks of one "
           "extra target is 3 splash targets."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "final_verdict_mastery", "Final Verdict",
    "Increases the damage of Final Verdict by 50%, and a killing blow readies "
    "it again.",
    6, 0,
    effects={"ability_guardian_final_verdict_damage": 0.50},
    proc={"trigger": "on_kill", "chance": 100, "icd": 0,
          "reset_cooldown": ["guardian_final_verdict"]},
    source="CoA verbatim: 'Give the final verdict to your target, dealing "
           "Physical damage and healing you for 15% of your maximum health. "
           "Only usable on enemies below 20% health. Killing blows reset the "
           "cooldown of this ability.' Frontier HAS Final Verdict as an "
           "ability, so this is not its unlock and the execute threshold "
           "lives on the ability rather than here. BOTH HALVES OF THIS "
           "CAPSTONE ARE REAL: on_kill is a live trigger and reset_cooldown "
           "as a bare list is a full reset, so the chain-execute CoA "
           "describes - kill, reset, kill again - works exactly as written. "
           "That makes it one of the few capstones in this whole audit that "
           "needed no reinterpretation at all. The self-heal is on the "
           "ability, not the talent."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. tools/talent_ranks.spread() rescales so a
# ranked node lands on exactly the ceiling it had at one rank, and refuses
# nodes carrying small integer durations.
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
    print(f"Guardian Gladiator: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
