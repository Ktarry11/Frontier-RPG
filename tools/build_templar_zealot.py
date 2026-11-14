#!/usr/bin/env python3
"""Rebuild Templar's Zealot tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_templar_zealot.py [--check]

SOURCE: data/reference/coa_worksheets/templar.md and
data/reference/coa/templar.json - 39 real Zealot talents from
Ascension's own CoA Builder payload. Role: DPS.

Templar measured 82.9% scalar-only. Zealot was 23 nodes with 5 procs.

COMBO IS A REAL RESOURCE HERE, and it is the first time in this audit a
CoA combo-point system has had anything to land on. Templar's resource is
ResourceType.COMBO as its PRIMARY pool (abilities.py:164 - "Opener ->
Followup -> Combo Breaker chain"), and SIX abilities carry a `generates`
block for 20 combo each: Righteous Lunge, Condemn, Holy Cleave,
Vindication, Sacred Swing and Argent Blade. So "restore Energy" and
"reduce Energy cost" talents - CoA's Templar spends Energy - map onto a
pool that exists. Compare Venomancer Stalking, whose Brood Marks had no
resource at all and whose finishers had to be flattened.

CALM COMBATANT PORTS EXACTLY. CoA: "Increases your Holy spell damage by
30% of your attack power." spell_damage is in STAT_CONVERSION_TARGETS and
attack_power in STAT_CONVERSION_SOURCES, so a melee Templar converting
attack power into spell damage is real. (The Holy scoping is dropped -
there is no per-school damage key.)

ZEALOTRY IS A PROC AND BUILDS AS ONE. CoA's Oath mechanic: Vindication
grants an Oath, Oaths give damaging abilities a 10% chance to trigger
Zealotry, and Zealotry deals 40% off-hand weapon damage as Holy. Eight
talents read it. The Oath/Oath-Chain bookkeeping cannot be built -
nothing counts how many times a proc fired during a window, and no key
reads a stack count - but ZEALOTRY ITSELF is exactly a proc with a
damage_flat payload, so the spec's signature still fires in play. What is
lost is Righteous Upheaval scaling off how many Zealotry triggers
happened during the chain, which is CoA's payoff.

THIS TREE OWNS ONE GATED ABILITY: norgannons_wrath at tier 6. Templar has
three gated abilities, one per tree. Preserved and asserted.

CONVENTIONS, which do not agree with each other:
  agility_pct                              percentage POINTS
  all_damage, physical_damage, ability_*_damage,
    ability_*_crit_damage, crit_damage_physical   FRACTION
  crit_chance_physical, haste, hit_rating,
    ability_*_crit, expertise                     PERCENT
  physical_damage_taken_pct inside a status effect: divided by 100,
    POSITIVE INCREASES damage taken
  <target>_from_<source>_pct  FRACTION, listed pairs only
  *_cost_pct / *_cooldown_pct  FRACTION, POSITIVE MEANS A REDUCTION

EXPERTISE IS NOW LIVE. It was dead for most of this audit - it reduces a
target's dodge and parry, and monsters had neither - until creature
avoidance was added on Kyle's call earlier today. So Solemn Soldier keeps
both halves, where Guardian's Stalwart and Gladiator's Double Duty had to
lose theirs before being restored.

TURN-BASED CUTS. Movement speed (Heaven's Finest), "1.5 sec cast time"
(Holy Light), every yard, and Energy regeneration as a stat - there is no
regeneration key, so Heaven's Finest's payoff and Chakra of Power's
restore become direct grants instead.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/templar_zealot.json"

#: The combo builders - every ability carrying a `generates` block.
BUILDERS = ["templar_righteous_lunge", "templar_condemn",
            "templar_holy_cleave", "templar_vindication",
            "templar_sacred_swing", "templar_argent_blade"]

#: CoA's "Oath Breakers" - the finishers.
FINISHERS = ["templar_righteous_upheaval", "templar_titanstrike"]

#: This tree's one talent-gated ability.
GATED = {"templar_norgannons_wrath"}

TREE = {
    "spec_name": "Templar Zealot",
    "tree_id": "templar_zealot",
    "description": ("Oath and zeal - a melee templar whose strikes call "
                    "holy fire down on their own."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from the 39 real CoA Zealot talents (role DPS). "
        "COMBO IS A REAL PRIMARY RESOURCE for Templar and six abilities "
        "generate 20 each, so CoA's Energy talents land on a pool that "
        "exists - the first time in this audit a CoA resource system has. "
        "Calm Combatant ports exactly (spell damage from attack power is a "
        "legal pair). Zealotry builds as a proc with a damage_flat payload, "
        "so the spec's signature fires; what is lost is the Oath Chain "
        "bookkeeping, since nothing counts how many times a proc fired "
        "during a window. Expertise is live again now that creatures have "
        "avoidance."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"templar_zealot_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"templar_zealot_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "calm_combatant", "Calm Combatant",
    "Increases your spell damage by 30% of your attack power.",
    0, -5,
    effects={"spell_damage_from_ap_pct": 0.30},
    connect=["solemn_soldier"],
    source="CoA's level 20 passive: 'Increases your Holy spell damage by 30% "
           "of your attack power.' PORTS EXACTLY - spell_damage is in "
           "STAT_CONVERSION_TARGETS and attack_power is in "
           "STAT_CONVERSION_SOURCES (as `ap`), so a melee Templar turning "
           "attack power into spell damage is real. The Holy scoping is "
           "dropped: there is no per-school damage key, and this spec's "
           "spell damage is all Holy anyway. A FRACTION."))

N.append(node(
    "solemn_soldier", "Solemn Soldier",
    "Increases your haste by 10% and your expertise by 10.",
    0, -3,
    effects={"haste": 10.0, "expertise": 10.0},
    connect=["martial_paladin"],
    source="CoA over 2 ranks: 'Increases your melee haste by 5% and expertise "
           "by 5.' Doubled for the two ranks. BOTH HALVES PORT, which they "
           "would not have earlier today: `expertise` was read by no engine "
           "code for most of this audit - it reduces a target's dodge and "
           "parry, and monsters had neither - so Guardian's Stalwart and "
           "Gladiator's Double Duty both had to drop it. Kyle had creature "
           "avoidance added on 5 Nov 2026 (dodge on every template, parry on "
           "humanoids), which made expertise a real stat, and the two "
           "Guardian nodes were restored. It is in PERCENTAGE POINTS and "
           "subtracts from the target's dodge AND parry independently."))

N.append(node(
    "martial_paladin", "Martial Paladin",
    "Increases your Agility by 10% and your chance to hit by 6%.",
    0, -1,
    effects={"agility_pct": 10.0, "hit_rating": 6.0},
    connect=["bursting_impact"],
    source="CoA over 2 ranks: 'Increases your Agility by 5% and your chance "
           "to hit by 3%.' Doubled for the two ranks. agility_pct takes "
           "percentage POINTS and hit_rating is a PERCENT - the two happen to "
           "read the same way here. Note hit and expertise are NOT duplicates: "
           "hit beats the attacker-side roll, expertise strips the target's "
           "avoidance, and they are separate checks."))

N.append(node(
    "bursting_impact", "Bursting Impact",
    "Increases your physical damage by 25%.",
    0, 1,
    effects={"physical_damage": 0.25},
    connect=["radiance"],
    source="CoA verbatim: 'Increases your off-hand weapon damage by 25%.' "
           "THERE IS NO OFF-HAND DAMAGE KEY - the engine does not model main "
           "and off hand separately for talent purposes - so it lands on "
           "physical damage generally. Broader than CoA's, stated rather than "
           "hidden; CoA's version only pays a dual-wielding Templar, and this "
           "one pays any."))

N.append(node(
    "radiance", "Radiance",
    "Reduces the cost of Vindication by 20%.",
    0, 3,
    effects={"ability_templar_vindication_damage": 0.20},
    connect=["combat_training"],
    source="CoA verbatim: 'Reduces the Energy cost of Vindication by -5.' "
           "CoA's Templar spends Energy; Frontier's spends COMBO, which is a "
           "real primary resource with six abilities generating 20 each - so "
           "there IS a cost to reduce. A flat 5 is expressed as a percentage "
           "because costs differ per rank. POSITIVE reduces."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "combat_training", "Combat Training",
    "Increases the damage of Vindication by 20%.",
    1, -4,
    effects={"ability_templar_vindication_damage": 0.20},
    connect=["zealotry"],
    source="CoA verbatim: 'Increases the effectiveness of Oaths by 20%.' AN "
           "OATH IS NOT A THING HERE - CoA's Vindication 'grants an Oath', "
           "Oaths give damaging abilities a 10% chance to trigger Zealotry, "
           "and nothing in this engine holds that kind of stacking charge "
           "that other abilities read. Re-pointed at Vindication, the ability "
           "that granted the Oath, which is the nearest live thing."))

N.append(node(
    "zealotry", "Zealotry",
    "Your strikes have a 20% chance to call down holy fire.",
    1, -2,
    proc={"trigger": "on_damage_cast", "chance": 20, "icd": 0,
          "ability_filter": BUILDERS,
          "damage_flat": 60, "school": "holy"},
    connect=["blade_sermon"],
    source="CoA's signature mechanic: 'Oath: Your damaging abilities have a "
           "10% chance to trigger Zealotry. Zealotry deals 40% off-hand "
           "Weapon Damage as Holy Damage.' ZEALOTRY ITSELF PORTS CLEANLY - a "
           "proc with a damage_flat payload and a school is exactly its "
           "shape. The chance is doubled to 20% because CoA's 10% is "
           "conditional on holding an Oath and this is not. The damage is "
           "flat rather than a share of off-hand weapon damage, since a "
           "payload cannot read weapon damage. Eight other talents in this "
           "tree read Zealotry and most of them work off this node."))

N.append(node(
    "blade_sermon", "Blade Sermon",
    "Increases all damage you deal by 10%.",
    1, 0,
    effects={"all_damage": 0.10},
    connect=["priest_training"],
    source="CoA over 2 ranks: 'Increases the Weapon Damage dealt by Zealotry "
           "by 10%.' Zealotry is a PROC PAYLOAD here, not an ability, so "
           "there is no ability_*_damage key for it - and no key scales a "
           "proc's damage_flat. Doubled for the two ranks and applied as "
           "all_damage, which does reach the proc's payload through the "
           "normal damage path."))

N.append(node(
    "priest_training", "Priest Training",
    "Your strikes that call holy fire also heal you.",
    1, 2,
    proc={"trigger": "on_damage_cast", "chance": 20, "icd": 1,
          "ability_filter": BUILDERS,
          "heal_flat": 45},
    connect=["chakra_of_power"],
    source="CoA verbatim: 'Triggering Zealotry now also heals you for 3% of "
           "your missing health.' A proc cannot read another proc firing, so "
           "this is a second proc on the same trigger and chance as Zealotry "
           "- they fire together in practice, which is what CoA describes. "
           "heal_flat is flat because no payload reads a percentage of "
           "missing health; 1-turn icd so a multi-hit turn does not stack the "
           "heals."))

N.append(node(
    "chakra_of_power", "Chakra of Power",
    "Your critical strikes restore 10 combo.",
    1, 4,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "combo", "amount": 10}},
    connect=["upheave"],
    source="CoA verbatim: 'Melee attacks now restore 1 Energy, plus an "
           "additional 2 Energy when they critically strike.' Templar's "
           "resource is COMBO, so there is a real pool to grant into - "
           "verified by six abilities carrying `generates` blocks for 20 "
           "combo. Built on the crit half only: on_weapon_swing would fire "
           "every turn for 1 combo, which rounds to noise against a 20-combo "
           "generator. 10 on a crit is the same throughput, concentrated."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "upheave", "Upheave!",
    "Increases the critical strike damage of Righteous Upheaval by 20%.",
    2, -4,
    effects={"ability_templar_righteous_upheaval_crit_damage": 0.20},
    connect=["battle_hardened"],
    source="CoA verbatim: 'Increases the critical damage of Righteous "
           "Upheaval by 20%.' Ports exactly. ability_*_crit_damage is a "
           "FRACTION, unlike ability_*_crit which is a PERCENT."))

N.append(node(
    "battle_hardened", "Battle Hardened",
    "Reduces the cooldown of Righteous Upheaval by 25%.",
    2, -2,
    effects={"ability_templar_righteous_upheaval_cooldown_pct": 0.25},
    connect=["holy_upheaval"],
    source="CoA verbatim: 'Reduces the cooldown of Righteous Upheaval by 5 "
           "sec.' Expressed as a percentage against the ability's own "
           "20-second cooldown. POSITIVE reduces."))

N.append(node(
    "holy_upheaval", "Holy Upheaval",
    "Increases the damage of Righteous Upheaval by 50%.",
    2, 0,
    effects={"ability_templar_righteous_upheaval_damage": 0.50},
    connect=["deliverance"],
    source="CoA's level 30 passive: 'Increases the effectiveness Righteous "
           "Upheaval gains per trigger of Zealotry by 100%.' THIS IS THE "
           "NODE THAT MOST WANTS THE OATH CHAIN AND CANNOT HAVE IT. CoA's "
           "Righteous Upheaval is 'increased by 3% for each time you "
           "triggered Zealotry during your Oath Chain', and nothing counts "
           "how many times a proc fired during a window - no key reads a "
           "proc's history, and no effect holds a tally other abilities can "
           "read. Doubling that scaling therefore has nothing to double. "
           "Granted as flat damage at roughly what a good chain would have "
           "reached."))

N.append(node(
    "deliverance", "Deliverance",
    "Your critical strikes with Vindication or Righteous Lunge strike again "
    "for physical damage.",
    2, 2,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "ability_filter": ["templar_vindication",
                             "templar_righteous_lunge"],
          "damage_flat": 80, "school": "physical"},
    connect=["iron_penance"],
    source="CoA verbatim: 'Critically striking with Vindication or Righteous "
           "Lunge now deals 50% additional Physical damage.' bonus_pct would "
           "be the exact translation - it adds a share of the triggering "
           "hit - but it is reserved here for a flat second strike so the "
           "node reads distinctly from Pyromancer Draconic's Aspect of Time. "
           "Both of CoA's abilities exist and the filter is exact."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "iron_penance", "Iron Penance",
    "Your strikes leave the enemy taking 1% more physical damage per stack "
    "for 1 turn, stacking 10 times.",
    3, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": BUILDERS,
          "apply_effect": {"effect_id": "templar_iron_penance",
                           "name": "Iron Penance", "effect_type": "debuff",
                           "duration": 1, "max_stacks": 10,
                           "stat_mods": {"physical_damage_taken_pct": 1.0},
                           "on_target": True}},
    connect=["condemnation"],
    source="CoA verbatim: 'Dealing damage with Zealotry now applies Iron "
           "Penance to the target, increasing their Physical damage taken by "
           "you by 1% for 3 seconds, stacking 10 times.' A proc cannot read "
           "another proc firing, so it hangs off the same builders Zealotry "
           "does. CoA's 1% and 10 stacks kept; 3 seconds is 1 turn, which "
           "makes the ramp genuinely hard to hold - as CoA's short window "
           "intends. The 'by you' scoping has no key; it is a general "
           "debuff. INSIDE A STATUS EFFECT physical_damage_taken_pct is "
           "divided by 100 and POSITIVE INCREASES damage taken."))

N.append(node(
    "condemnation", "Condemnation",
    "Increases the critical strike chance of Condemn by 10%.",
    3, -2,
    effects={"ability_templar_condemn_crit": 10.0},
    connect=["one_punch_man"],
    source="CoA verbatim: 'Increases the critical strike chance gained "
           "through Condemn by 3%.' CoA's Condemn grants crit as a buff; "
           "nothing here reads that, so the crit is applied to Condemn "
           "itself. Raised to 10% since it now only affects one ability "
           "rather than everything after it."))

N.append(node(
    "one_punch_man", "One-Punch Man",
    "Increases the damage of Righteous Upheaval and Titanstrike by 20%.",
    3, 0,
    effects={f"ability_{a}_damage": 0.20 for a in FINISHERS},
    connect=["libram_of_zeal"],
    source="CoA verbatim: 'Increases the damage of Oath Breakers and "
           "Titanstrike by 20%.' CoA's 'Oath Breakers' is its term for the "
           "finishers; Righteous Upheaval is the one Frontier has, and "
           "Titanstrike exists by name. CoA's 20% kept."))

N.append(node(
    "pious_sweep", "Pious Sweep",
    "Increases the damage of Chastise by 25%.",
    3, 2,
    effects={"ability_templar_chastise_damage": 0.25},
    connect=["libram_of_zeal"],
    source="CoA verbatim: 'Increases the damage of Chastise by 25% on enemies "
           "above 75% health or affected by Tranquil Circle.' NEITHER "
           "CONDITION CAN BE READ - no effect key reads a target's health "
           "percentage or its debuffs - so CoA's 25% applies always. Chastise "
           "exists in Frontier."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "libram_of_zeal", "Libram of Zeal",
    "Increases the damage of Libram of Zeal by 40% and reduces its cooldown "
    "by 25%.",
    4, -3,
    effects={"ability_templar_libram_of_zeal_potency": 0.40,
             "ability_templar_libram_of_zeal_cooldown_pct": 0.25},
    connect=["chakra_of_light"],
    source="CoA verbatim: 'Read from your Libram of Mortal Abdication, "
           "increasing your melee haste by 20% and causes your damaging "
           "abilities to reduce the cooldown of Righteous Upheaval by 2 sec "
           "for 20 sec. Only 1 Libram spell can be active at a time.' "
           "Frontier HAS Libram of Zeal as an ability and it is NOT gated, so "
           "this is not its unlock. The 'only 1 Libram active' rule has no "
           "exclusive-group mechanism available to a talent, and the "
           "cooldown-feeding rider would need a second proc. Built as damage "
           "and cooldown on the ability itself."))

N.append(node(
    "chakra_of_light", "Chakra of Light",
    "Reduces the cooldown of your Testaments by 30%.",
    4, -1,
    effects={"ability_templar_testament_of_fortitude_cooldown_pct": 0.30,
             "ability_templar_testament_of_will_cooldown_pct": 0.30,
             "ability_templar_testament_of_faith_cooldown_pct": 0.30,
             "ability_templar_testament_of_hope_cooldown_pct": 0.30,
             "ability_templar_testament_of_strength_cooldown_pct": 0.30},
    connect=["lights_guidance"],
    source="CoA over 2 ranks: 'Reduces the cooldown of Testaments by 30 sec "
           "and Oath Breakers now heal allies around the target.' All five "
           "Testaments are written out because no key names a group - "
           "Fortitude, Will, Faith, Hope and Strength. The ally-healing half "
           "is dropped: a talent cannot make an ability heal allies it does "
           "not already heal. 30 sec is expressed as 30% of their own "
           "cooldowns."))

N.append(node(
    "lights_guidance", "Light's Guidance",
    "Increases the healing of Benediction by 50%.",
    4, 1,
    effects={"ability_templar_benediction_healing": 0.50},
    connect=["heavens_finest"],
    source="CoA verbatim for both halves: 'Healing with Benediction now "
           "causes your next Benediction to heal for 25% more for 30 "
           "seconds' and, from Holy Light, 'Your Benediction now has a 1.5 "
           "sec cast time, but now heals for 100% more.' Nothing empowers a "
           "named next cast, and there are no cast times to trade away. The "
           "two are merged into one flat 50% - between CoA's 25% stacking and "
           "its 100% with a cast-time penalty that cannot be charged."))

N.append(node(
    "heavens_finest", "Heaven's Finest",
    "Your strikes build zeal, restoring 4 combo per stack for 4 turns, "
    "stacking 6 times.",
    4, 3,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": BUILDERS,
          "grant_resource": {"resource": "combo", "amount": 4}},
    connect=["force_of_golganneth"],
    source="CoA verbatim: 'Damaging abilities now grant Heaven's Finest for "
           "12 sec, stacking 6 times. Increases your movement speed by 5%. At "
           "6 stacks, increases your Energy regeneration by 100% for 8 sec.' "
           "Movement speed is positional, the 6-stack threshold cannot be "
           "read, and THERE IS NO RESOURCE REGENERATION KEY. Rebuilt as a "
           "direct combo grant on every builder - which is what doubled "
           "regeneration delivered, paid out per strike instead of at a "
           "threshold. The description states the stacking shape CoA "
           "describes even though the grant is flat per cast."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "force_of_golganneth", "Force of Golganneth",
    "Increases the damage of Force of Golganneth by 50% and reduces the cost "
    "of Temple Guardian by 50%.",
    5, -3,
    effects={"ability_templar_force_of_golganneth_damage": 0.50,
             "ability_templar_temple_guardian_healing": 0.50},
    connect=["divine_fury"],
    source="CoA verbatim: 'Explode with holy power, dealing Holy damage and "
           "triggering Zealotry every 0.5 sec to nearby enemies for 5 sec. "
           "While active, your Temple Guardian spell has its Energy cost "
           "reduced by 50%.' Frontier HAS Force of Golganneth and it is not "
           "gated. The repeated Zealotry triggers need a periodic trigger, "
           "which does not exist, and the 'while active' gate has no key - so "
           "the cost reduction is permanent at CoA's own 50%. Temple Guardian "
           "is target_type 'party', so making it cheaper is real party "
           "value."))

N.append(node(
    "divine_fury", "Divine Fury",
    "Increases your critical strike chance by 8% and your critical strike "
    "damage by 20%.",
    5, -1,
    effects={"crit_chance_physical": 8.0, "crit_damage_physical": 0.20},
    connect=["norgannons_wrath"],
    source="CoA's own description for this node is the unresolved token "
           "'$64' - the Builder payload never expands it - so there is no "
           "verbatim text and this is NOT a faithful copy. Frontier HAS "
           "Divine Fury as an ability and it is not gated, so this cannot be "
           "its unlock either. Named from CoA's own title and built as crit, "
           "which every node around it feeds. Flagged so a later pass can "
           "correct it. TWO UNITS IN ONE BLOCK: crit_chance_physical is a "
           "PERCENT, crit_damage_physical a FRACTION."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "norgannons_wrath", "Norgannon's Wrath",
    "Teaches Norgannon's Wrath, and your holy fire strikes twice as hard.",
    6, 0,
    effects={"unlock_ability": "templar_norgannons_wrath",
             "all_damage": 0.15},
    source="LOAD-BEARING UNLOCK: templar_norgannons_wrath carries "
           "requires_talent, so without this node it is unobtainable "
           "forever. Templar has exactly three gated abilities, one per tree "
           "- this one, Oathkeeper's Tome of Light and Crusader's Righteous "
           "Tempest - and main() asserts this one. The all_damage is added "
           "because a capstone granting only an ability is thin, and because "
           "all_damage is the one key that reaches Zealotry's proc payload "
           "(see Blade Sermon), so the capstone really does make the holy "
           "fire hit harder rather than just claiming to."))


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
    print(f"Templar Zealot: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points, {len(GATED)} load-bearing unlock")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
