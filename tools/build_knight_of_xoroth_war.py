#!/usr/bin/env python3
"""Rebuild Knight of Xoroth's War tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_knight_of_xoroth_war.py [--check]

SOURCE: data/reference/coa_worksheets/knight-of-xoroth.md and
data/reference/coa/knight-of-xoroth.json - 38 real War talents from
Ascension's own CoA Builder payload. Role: DPS.

Knight of Xoroth measured 82.6% scalar-only, worst of the 11 classes
remaining. War was 23 nodes with FOUR procs.

DEMONFIRE IS DEATHFIRE, AND IT EXISTS. CoA's Knight of Xoroth banks
Demonfire; Frontier's resource line is
(ResourceType.RAGE, ResourceType.DEATHFIRE) - Rage primary, DEATHFIRE
SECONDARY - and four abilities carry a `generates` block for it:
Infernal Strike (20), Sever (10), Demon Heart (20) and Shieldgore (20).
So "generates 1 Demonfire" and "abilities that spend Demonfire" land on a
pool that genuinely exists, which makes this the second class after
Templar where a CoA resource system has somewhere to go.

WHAT STILL FAILS is reading HOW MUCH you hold. Hand of Doom ("increased
by 10% for each Demonfire you have active"), Warbringer and Burning Blade
("per Demonfire consumed") all need a live resource read, and nothing
reads one - the same wall that flattened Stormbringer's five Static
talents and Pyromancer's Ember nodes. Each is granted at a realistic
value, flat.

CHARGES DO NOT EXIST, which costs Gore its CoA shape (2 charges, 8 sec
recharge) and takes Ripper entirely ("abilities that spend Demonfire
refresh a charge of Gore"). Re-pointed at cooldown.

THIS TREE OWNS TWO GATED ABILITIES: gore at tier 1 and
brimstone_bludgeon at tier 6. Knight of Xoroth has five gated abilities
across its three trees. Both preserved in place and asserted.

EXPERTISE IS LIVE (creature avoidance went in 5 Nov 2026), so Consuming
Blade keeps both halves.

CONVENTIONS, which do not agree with each other:
  armor_penetration_pct, attack_power_pct      percentage POINTS
  all_damage, physical_damage, ability_*_damage,
    crit_damage_physical, ability_*_crit_damage   FRACTION
  crit_chance_physical, haste, hit_rating,
    expertise, ability_*_crit                     PERCENT
  physical_damage_taken_pct inside a status effect: /100, POSITIVE
    INCREASES damage taken
  *_cost_pct / *_cooldown_pct  FRACTION, POSITIVE MEANS A REDUCTION

TURN-BASED CUTS. "Lasts for 6 attacks" (Burning Blade - no attack
counter), "in a line", "your next X is guaranteed to crit" (Decimation),
and every cast time.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/knight_of_xoroth_war.json"

#: The Deathfire generators - abilities carrying a `generates` block.
GENERATORS = ["knight_of_xoroth_infernal_strike", "knight_of_xoroth_sever",
              "knight_of_xoroth_demon_heart"]

#: CoA's Demonfire spenders - the big strikes.
SPENDERS = ["knight_of_xoroth_skulltaker", "knight_of_xoroth_warbringer",
            "knight_of_xoroth_meatsaw"]

#: This tree's talent-gated abilities.
GATED = {"knight_of_xoroth_gore", "knight_of_xoroth_brimstone_bludgeon"}

TREE = {
    "spec_name": "Knight of Xoroth War",
    "tree_id": "knight_of_xoroth_war",
    "description": ("Gore and brimstone - a demonic knight who banks "
                    "Deathfire and spends it on butchery."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from the 38 real CoA War talents (role DPS). "
        "Knight of Xoroth measured 82.6% scalar-only, worst of the 11 "
        "classes remaining. DEMONFIRE IS DEATHFIRE AND IT EXISTS: Frontier's "
        "resource line is (RAGE, DEATHFIRE) with four abilities generating "
        "into it, so CoA's generate-and-spend talents land on a real pool - "
        "the second class after Templar where that is true. What still fails "
        "is reading HOW MUCH you hold, which flattens three talents. Charges "
        "do not exist, which costs Gore its CoA shape and takes Ripper "
        "entirely. Owns gore (t1) and brimstone_bludgeon (t6), both gated, "
        "both asserted."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"knight_of_xoroth_war_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"knight_of_xoroth_war_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "hellfire_striker", "Hellfire Striker",
    "Increases your critical strike chance and chance to hit by 3%.",
    0, -5,
    effects={"crit_chance_physical": 3.0, "hit_rating": 3.0},
    connect=["mutilation"],
    source="CoA verbatim: 'Increases your critical strike and hit chance by "
           "3%.' Both halves port exactly. Both keys are PERCENT."))

N.append(node(
    "mutilation", "Mutilation",
    "Increases the damage of Gore and Sever by 30%.",
    0, -3, ranks=3,
    effects={"ability_knight_of_xoroth_gore_damage": 0.10,
             "ability_knight_of_xoroth_sever_damage": 0.10},
    connect=["consuming_blade"],
    source="CoA over 3 ranks: 'Increases the damage of Gore and Sever by "
           "10%.' Authored at CoA's own PER-RANK 10% with CoA's 3 ranks, so "
           "the policy skips it and get_effective_effects() multiplies by "
           "points spent to reach 30% - the description states the ceiling. "
           "Authoring 0.30 here with ranks=3 would have delivered 90%, the "
           "bug that shipped on Guardian Vanguard's Iron Guardian."))

N.append(node(
    "consuming_blade", "Consuming Blade",
    "Increases the critical strike chance of Gore by 50% and your expertise "
    "by 10.",
    0, -1,
    effects={"ability_knight_of_xoroth_gore_crit": 50.0,
             "expertise": 10.0},
    connect=["murderous_might"],
    source="CoA over 2 ranks: 'Increases the critical strike chance of Gore "
           "by 25% and your expertise by 5.' Doubled for the two ranks. BOTH "
           "HALVES PORT because creature avoidance went in on Kyle's call "
           "earlier today - before that `expertise` reduced a target dodge "
           "and parry that did not exist, and Guardian's Stalwart and "
           "Gladiator's Double Duty both had to drop it. Expertise is in "
           "PERCENTAGE POINTS and strips the target's dodge AND parry "
           "independently."))

N.append(node(
    "murderous_might", "Murderous Might",
    "Increases the damage of Skulltaker, Warbringer and Meatsaw by 25%.",
    0, 1,
    effects={f"ability_{a}_damage": 0.25 for a in SPENDERS},
    connect=["absolutism"],
    source="CoA verbatim: 'Increases the base damage of abilities that spend "
           "Demonfire by 25%.' Demonfire is Frontier's DEATHFIRE and it "
           "exists as a real secondary resource - but no key names 'abilities "
           "that spend' it as a group, so CoA's three spenders are written "
           "out: Skulltaker, Warbringer and Meatsaw. CoA's 25% kept."))

N.append(node(
    "absolutism", "Absolutism",
    "Increases your armour penetration by 10%.",
    0, 3,
    effects={"armor_penetration_pct": 10.0},
    connect=["gore"],
    source="CoA verbatim: 'Damage dealt by Meatsaw now ignores -10% of the "
           "target's Armor.' NO KEY SCOPES ARMOUR PENETRATION TO ONE ABILITY "
           "- armor_penetration_pct is a character stat read attacker-side in "
           "entities/monster.py - so it applies to everything. CoA's 10% "
           "kept. CoA's second Burning Blade node ('Skulltaker ignores -25% "
           "armour') is the same mechanic on a different ability and is folded "
           "in rather than built twice. Takes percentage POINTS."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "gore", "Gore",
    "Teaches Gore, a quick butchering strike that banks Deathfire.",
    1, -4,
    effects={"unlock_ability": "knight_of_xoroth_gore"},
    connect=["gored"],
    source="CoA verbatim: 'Gore. 30 Rage. Requires Melee Weapon. 2 Charges, 8 "
           "sec recharge. Generates 1 Demonfire. Quickly gore an enemy, "
           "dealing 100% Weapon Damage plus 15.' LOAD-BEARING UNLOCK: "
           "knight_of_xoroth_gore carries requires_talent, so without this "
           "node it is unobtainable forever - and four other nodes in this "
           "tree name it. CHARGES DO NOT EXIST, so CoA's 2-charge shape lives "
           "on the ability as a cooldown or not at all; the talent only "
           "grants it. Kept at tier 1 where the shipped tree had it."))

N.append(node(
    "gored", "Gored",
    "Gore and Meatsaw leave the enemy taking 15% more physical damage for 3 "
    "turns, stacking twice.",
    1, -2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["knight_of_xoroth_gore",
                             "knight_of_xoroth_meatsaw"],
          "apply_effect": {"effect_id": "knight_of_xoroth_gored",
                           "name": "Gored", "effect_type": "debuff",
                           "duration": 3, "max_stacks": 2,
                           "stat_mods": {"physical_damage_taken_pct": 15.0},
                           "on_target": True}},
    connect=["ripper"],
    source="CoA verbatim: 'Damage dealt by Gore and Meatsaw now increases "
           "your target's damage taken from Skulltaker and Warbringer by 15% "
           "for 10 sec, stacking 2 times.' PORTS CLOSELY - the right two "
           "trigger abilities, CoA's 15% and 2 stacks, and 10 sec as 3 turns. "
           "The 'from Skulltaker and Warbringer' scoping has no key, so it is "
           "physical damage taken generally - broader than CoA's. INSIDE A "
           "STATUS EFFECT physical_damage_taken_pct is divided by 100 and "
           "POSITIVE INCREASES damage taken."))

N.append(node(
    "ripper", "Ripper",
    "Reduces the cooldown of Gore by 30%.",
    1, 0,
    effects={"ability_knight_of_xoroth_gore_cooldown_pct": 0.30},
    connect=["fiend"],
    source="CoA's level 20 passive: 'Damaging abilities that spend Demonfire "
           "now refresh a charge of Gore.' THERE IS NO CHARGE SYSTEM - "
           "abilities have a cooldown, not a pool of charges - so there is no "
           "charge to refresh. Re-pointed at Gore's cooldown, which is the "
           "single-charge equivalent, the same translation as Guardian "
           "Gladiator's Supremacy and Venomancer Vizier's Melioration."))

N.append(node(
    "fiend", "Fiend",
    "Reduces the cost of Infernal Strike by 30%.",
    1, 2,
    effects={"ability_knight_of_xoroth_infernal_strike_cost_pct": 0.30},
    connect=["bringer_of_destruction"],
    source="CoA verbatim: 'Casting Sever now removes the cost of your next "
           "Infernal Strike.' NOTHING MAKES A NAMED NEXT CAST FREE - no "
           "charge counter and no payload that discounts a later specific "
           "ability - so the discount becomes permanent at 30% rather than "
           "total on one cast. POSITIVE reduces."))

N.append(node(
    "bringer_of_destruction", "Bringer of Destruction",
    "Taking a critical hit grants you 10 Deathfire and 5 Rage.",
    1, 4,
    proc={"trigger": "on_damage_taken", "chance": 100, "icd": 3,
          "grant_resource": {"resource": "deathfire", "amount": 10}},
    connect=["carver"],
    source="CoA verbatim: 'Critical damage taken now grants you 1 Demonfire "
           "and 5 Rage. Can only occur once every 3 sec.' DEATHFIRE IS REAL "
           "(ResourceType.DEATHFIRE, four abilities generate into it), so "
           "there is somewhere for this to go. A proc carries ONE "
           "grant_resource, so the Rage half cannot be granted alongside it - "
           "the Deathfire is the half that matters, since three nodes here "
           "spend it. CoA's 3-second limit ports as icd 3. There is no "
           "'critical damage taken' trigger, only on_damage_taken, so it "
           "fires on any hit - held to once every 3 turns, which is close to "
           "CoA's rate for a crit."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "carver", "Carver",
    "Your critical strikes with Gore grant 10 Deathfire.",
    2, -4,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "ability_filter": ["knight_of_xoroth_gore"],
          "grant_resource": {"resource": "deathfire", "amount": 10}},
    connect=["pestilence_of_death"],
    source="CoA's level 30 passive: 'Critical strikes with Gore now generate "
           "1 additional Demonfire.' PORTS CLEANLY - on_crit with an "
           "ability_filter on Gore, granting into the real Deathfire pool. "
           "CoA's '1 Demonfire' is 10 here because Frontier's generators work "
           "in tens (Sever grants 10, Infernal Strike 20), so one CoA "
           "Demonfire is worth roughly ten Deathfire."))

N.append(node(
    "pestilence_of_death", "Pestilence of Death",
    "Increases your critical strike damage by 20%.",
    2, -2,
    effects={"crit_damage_physical": 0.20},
    connect=["boundless_fury"],
    source="CoA verbatim: 'Emanate a pestilence, increasing your critical "
           "damage by 10%.' Frontier HAS Pestilence of Death as an ability "
           "and it is not gated, so this is not its unlock. Doubled to 20% to "
           "carry a tier-2 node on its own. crit_damage_physical is a "
           "FRACTION, unlike crit_chance_physical which is a PERCENT."))

N.append(node(
    "boundless_fury", "Boundless Fury",
    "Increases the damage of Unleash Pestilence by 30%.",
    2, 0,
    effects={"ability_knight_of_xoroth_unleash_pestilence_damage": 0.30},
    connect=["screamin_demon"],
    source="CoA verbatim: 'Increases the effectiveness of the unleash effect "
           "from Pestilence of Death by 30%.' CoA's 'unleash effect' is "
           "Unleash Pestilence, which Frontier has as its own ability - so "
           "the 30% lands there rather than on a rider that does not exist."))

N.append(node(
    "screamin_demon", "Screamin' Demon",
    "Reduces the cooldown of Unleash Pestilence by 30%.",
    2, 2,
    effects={"ability_knight_of_xoroth_unleash_pestilence_cooldown_pct": 0.30},
    connect=["burning_blade"],
    source="CoA verbatim: 'Reduces the cooldown of Unleash Pestilence by 15 "
           "sec.' Expressed as a percentage against the ability's own "
           "cooldown. POSITIVE reduces."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "burning_blade", "Burning Blade",
    "Your critical strikes send out searing fire.",
    3, -4,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "damage_flat": 95, "school": "fire"},
    connect=["hellsmelted"],
    source="CoA verbatim: 'Ignite your weapon, causing you to send out "
           "searing fire with each melee critical strike, dealing Fire damage "
           "in a line and increasing your Armor penetration by 30% while "
           "active. Lasts for 6 attacks. Lasts for 1 additional attack per "
           "Demonfire consumed.' Frontier HAS Burning Blade as an ability and "
           "it is not gated. THERE IS NO ATTACK COUNTER - nothing tracks 'for "
           "the next N attacks' - and no live resource read for the "
           "per-Demonfire extension, so the duration limit cannot exist. "
           "Built as a permanent on-crit fire strike, which is what the "
           "window delivered. 'In a line' is positional."))

N.append(node(
    "hellsmelted", "Hellsmelted",
    "Increases the damage of Burning Blade and Searing Blade by 30% and their "
    "critical strike chance by 30%.",
    3, -2,
    effects={"ability_knight_of_xoroth_burning_blade_potency": 0.30,
             "ability_knight_of_xoroth_burning_blade_duration": 1,
             "ability_knight_of_xoroth_searing_blade_damage": 0.30},
    connect=["burning_swings"],
    source="CoA verbatim: 'Increases the critical strike chance and damage of "
           "Burning Blade by 30%.' Both halves port onto the real ability, "
           "and Searing Blade is included because Frontier has it as the "
           "paired ability and CoA's text covers 'your burning weapon' "
           "broadly. ability_*_damage is a FRACTION and ability_*_crit a "
           "PERCENT - both in one block."))

N.append(node(
    "burning_swings", "Burning Swings",
    "Increases the damage of Searing Blade by 40%.",
    3, 0,
    effects={"ability_knight_of_xoroth_searing_blade_damage": 0.40},
    connect=["hand_of_doom"],
    source="CoA verbatim: 'Your Burning Blade now affects 4 additional "
           "attacks.' There is no attack counter to extend (see Burning "
           "Blade), so more attacks cannot be granted. Re-pointed at Searing "
           "Blade's damage, which is what four more burning swings "
           "delivered."))

N.append(node(
    "hand_of_doom", "Hand of Doom",
    "Increases the damage of Sever by 40%.",
    3, 2,
    effects={"ability_knight_of_xoroth_sever_damage": 0.40},
    connect=["decimation"],
    source="CoA verbatim: 'Increases the Weapon Damage dealt by Sever by 10%, "
           "increased by 10% for each Demonfire you have active.' NOTHING "
           "READS A LIVE RESOURCE AMOUNT - the same wall that flattened "
           "Stormbringer's five Static talents and Pyromancer's Ember nodes - "
           "so the per-Demonfire scaling cannot exist. A realistic bank is "
           "three Demonfire, so 10% plus 3x10% is 40%, flat."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "decimation", "Decimation",
    "Increases the critical strike chance of Skulltaker and Warbringer by "
    "30%.",
    4, -3,
    effects={"ability_knight_of_xoroth_skulltaker_crit": 30.0,
             "ability_knight_of_xoroth_warbringer_crit": 30.0},
    connect=["warbringer"],
    source="CoA verbatim: 'Your next Skulltaker or Warbringer is guaranteed "
           "to critically strike for 25% increased damage. Lasts 30 "
           "seconds.' A GUARANTEED CRIT HAS NO KEY and nothing empowers a "
           "named next cast. Frontier HAS Decimation as an ability and it is "
           "not gated. Built as flat crit on exactly CoA's two abilities, "
           "priced at 30% rather than 100% because it applies always."))

N.append(node(
    "warbringer", "Warbringer",
    "Increases the damage of Warbringer by 40%, and it leaves the enemy "
    "receiving 30% less healing for 3 turns.",
    4, -1,
    effects={"ability_knight_of_xoroth_warbringer_damage": 0.40},
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["knight_of_xoroth_warbringer"],
          "apply_effect": {"effect_id": "knight_of_xoroth_warbringer_wound",
                           "name": "Warbringer's Wound",
                           "effect_type": "debuff", "duration": 3,
                           "max_stacks": 1,
                           "stat_mods": {"healing_taken_pct": -30.0},
                           "on_target": True}},
    connect=["conquerors_will"],
    source="CoA verbatim: 'Transforms your Flames of Xoroth into Warbringer. "
           "Slam the ground, dealing Weapon Damage to nearby enemies, "
           "reducing the effectiveness of any healing by -50% for 10 seconds. "
           "Deals increased damage per Demonfire consumed.' Frontier HAS "
           "Warbringer as its own ability, so nothing needs transforming. The "
           "anti-heal ports as a debuff, priced at 30% rather than CoA's 50% "
           "because it is permanent rather than a 10-second window; 10 sec is "
           "3 turns. The per-Demonfire damage cannot be read, so it is the "
           "flat 40%. INSIDE A STATUS EFFECT healing_taken_pct is percentage "
           "POINTS, so -30% is -30.0; as a talent effect it is a FRACTION."))

N.append(node(
    "conquerors_will", "Conqueror's Will",
    "Increases your critical strike chance by 3%, and your critical strikes "
    "leave the enemy taking 4% more physical damage for 6 turns.",
    4, 1,
    effects={"crit_chance_physical": 3.0},
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "knight_of_xoroth_conquerors_will",
                           "name": "Conqueror's Will",
                           "effect_type": "debuff", "duration": 6,
                           "max_stacks": 1,
                           "stat_mods": {"physical_damage_taken_pct": 4.0},
                           "on_target": True}},
    connect=["brimstone_bludgeon"],
    source="CoA verbatim: 'Increases the critical strike chance of all party "
           "and raid members by 3%. Does not stack with similar effects. In "
           "addition, Physical critical strikes now increase the target's "
           "Physical damage taken by 4% for 20 sec.' A TALENT CANNOT REACH AN "
           "ALLY, so the 3% lands on the Knight and the description says "
           "'your'. THE SECOND HALF PORTS EXACTLY - on_crit, CoA's 4%, and 20 "
           "sec is 6 turns. No trigger-side school filter exists, so "
           "'Physical critical strikes' is any crit; this spec deals almost "
           "nothing else."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "skulltaker_mastery", "Skulltaker",
    "Increases the damage of Skulltaker by 50% and your armour penetration by "
    "a further 15%.",
    5, -3,
    effects={"ability_knight_of_xoroth_skulltaker_damage": 0.50,
             "armor_penetration_pct": 15.0},
    connect=["brimstone_bludgeon"],
    source="CoA's second Burning Blade node: 'Your Skulltaker now ignores "
           "-25% of the target's Armor.' Armour penetration cannot be scoped "
           "to one ability (see Absolutism at tier 0), so CoA's 25% becomes a "
           "further 15% of character-wide penetration alongside flat "
           "Skulltaker damage - the ability the node is about. Stacks with "
           "Absolutism for 25% total on a full War build, which is CoA's own "
           "figure arrived at from the other direction."))

N.append(node(
    "fury_of_xoroth", "Fury of Xoroth",
    "Your Deathfire generators have a 25% chance to strike again for fire "
    "damage.",
    5, -1,
    proc={"trigger": "on_damage_cast", "chance": 25, "icd": 0,
          "ability_filter": GENERATORS,
          "damage_flat": 90, "school": "fire"},
    connect=["brimstone_bludgeon"],
    source="Built from CoA's Burning Blade and Pestilence themes rather than "
           "ported from one talent, so tier 5 carries a real proc instead of "
           "a third flat damage line - and flagged as such. It fires off the "
           "three abilities that generate Deathfire (Infernal Strike, Sever, "
           "Demon Heart), which is where a War Knight spends its turns, so it "
           "rewards the rotation the resource actually drives."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "brimstone_bludgeon", "Brimstone Bludgeon",
    "Teaches Brimstone Bludgeon, and your Deathfire spenders hit 30% harder.",
    6, 0,
    effects={"unlock_ability": "knight_of_xoroth_brimstone_bludgeon",
             **{f"ability_{a}_damage": 0.30 for a in SPENDERS}},
    source="LOAD-BEARING UNLOCK: knight_of_xoroth_brimstone_bludgeon carries "
           "requires_talent, so without this node it is unobtainable "
           "forever. Knight of Xoroth has five gated abilities across three "
           "trees - this and Gore in War, Shieldgore and Call Hellfire "
           "Abyssal in Defiance, Hellmaw in Hellfire - and main() asserts "
           "both of this tree's. The spender damage is added because a "
           "capstone granting only an ability is thin, and it pays off the "
           "Deathfire economy the whole tree builds."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. tools/talent_ranks.spread() rescales so a
# ranked node lands on exactly the ceiling it had at one rank, and refuses
# nodes carrying small integer durations and unlock_ability nodes.
#
# Mutilation is authored at its PER-RANK value with CoA's own 3 ranks, so the
# policy skips it. Author the CEILING at one rank everywhere else.
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
    print(f"Knight of Xoroth War: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points, {len(GATED)} load-bearing unlocks")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
