#!/usr/bin/env python3
"""Rebuild Knight of Xoroth's Hellfire tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_knight_of_xoroth_hellfire.py [--check]

SOURCE: data/reference/coa_worksheets/knight-of-xoroth.md and
data/reference/coa/knight-of-xoroth.json - 36 real Hellfire talents from
Ascension's own CoA Builder payload. Role: DPS.

The shipped tree was 23 nodes with TWO procs.

BURNING POWER PORTS WHOLE - both halves, and it is the strangest stat
pairing in the audit. CoA: "Increases your attack power by 100% of your
Intellect and your spell damage by 50% of your Strength." attack_power
and spell_damage are both in STAT_CONVERSION_TARGETS, and intellect and
strength are both in STAT_CONVERSION_SOURCES - so a melee demon knight
whose Intellect IS its attack power, and whose Strength IS its spell
damage, is real exactly as CoA wrote it. Cinderblade adds crit from
Intellect on top.

PET KEYS ARE LIVE ON THIS CLASS, which matters because they are dead data
on most. Knight of Xoroth genuinely summons - call_hellfire_imp,
call_hellfire_abyssal and summon_greater_imp all carry summon fields - so
pet_damage, pet_health and pet_armor reach something real here. Contrast
the Witch Doctor's Serpent Wards and Venomancer's Fungarians, where the
same keys would have been silent (see tools/qa_pet_keys.py). What still
fails is PET HASTE - pet_haste is read by nothing - which takes Hellfire
Rituals, and anything that transforms a pet, which takes Doom.

DEMONFIRE IS DEATHFIRE AND IT EXISTS (see the War builder), but reading
how much you hold does not - so "per Demonfire consumed", "with 6
Demonfire" and "when you spend at least 4 Demonfire stacks" all flatten.
That takes Hellmaw's scaling, Rain of Chaos and Claws of Hell.

THIS TREE OWNS ONE GATED ABILITY: hellmaw at tier 1. hellfire_form has an
unlock node at tier 6 but is NOT gated, so that node granted an ability
the character already had - replaced with real mechanics.

CONVENTIONS, which do not agree with each other:
  intellect_pct, strength_pct, attack_power_pct   percentage POINTS
  all_damage, spell_damage, dot_damage, pet_damage, pet_health,
    ability_*_damage, crit_damage_physical           FRACTION
  crit_chance_physical, crit_chance_spell, haste,
    hit_rating, ability_*_crit                       PERCENT
  spell_damage_taken_pct inside a status effect: /100, POSITIVE
    INCREASES damage taken
  <target>_from_<source>_pct  FRACTION, listed pairs only
  *_cost_pct / *_cooldown_pct  FRACTION, POSITIVE MEANS A REDUCTION

TURN-BASED CUTS. Health-threshold conditions (Invasion, Hellfire Embers),
"while Hellfire Form is active" gates (Grotesque), and every yard.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/knight_of_xoroth_hellfire.json"

#: The fire strikes this spec is built on.
FIRE = ["knight_of_xoroth_hellmaw", "knight_of_xoroth_seeking_flame",
        "knight_of_xoroth_flames_of_xoroth"]

#: CoA's Demonfire spenders.
SPENDERS = ["knight_of_xoroth_skulltaker", "knight_of_xoroth_warbringer",
            "knight_of_xoroth_meatsaw"]

#: This tree's talent-gated ability.
GATED = {"knight_of_xoroth_hellmaw"}

TREE = {
    "spec_name": "Knight of Xoroth Hellfire",
    "tree_id": "knight_of_xoroth_hellfire",
    "description": ("Shadowflame and imps - a demon knight whose Intellect "
                    "is its attack power."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from the 36 real CoA Hellfire talents (role "
        "DPS). BURNING POWER PORTS WHOLE and is the strangest stat pairing "
        "in the audit: attack power from 100% of Intellect AND spell damage "
        "from 50% of Strength, both legal pairs. PET KEYS ARE LIVE on this "
        "class - it genuinely summons three pets - unlike the Witch Doctor "
        "and Venomancer where the same keys would be dead data. pet_haste is "
        "still read by nothing, which takes Hellfire Rituals, and nothing "
        "transforms a pet, which takes Doom. Owns hellmaw (t1, gated); "
        "hellfire_form's tier-6 unlock node was dead because that ability is "
        "not gated, and is replaced with real mechanics."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"knight_of_xoroth_hellfire_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"knight_of_xoroth_hellfire_{c}"
                         for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "burning_power", "Burning Power",
    "Increases your attack power by 100% of your Intellect and your spell "
    "damage by 50% of your Strength.",
    0, -5,
    effects={"attack_power_from_intellect_pct": 1.00,
             "spell_damage_from_strength_pct": 0.50},
    connect=["cinderblade"],
    source="CoA's level 20 passive, verbatim: 'Increases your attack power by "
           "100% of your Intellect and your spell damage by 50% of your "
           "Strength.' PORTS WHOLE, and it is the strangest stat pairing in "
           "this audit: attack_power and spell_damage are both in "
           "STAT_CONVERSION_TARGETS, intellect and strength both in "
           "STAT_CONVERSION_SOURCES, so CoA's deliberate crossing works "
           "exactly. A melee demon knight whose Intellect IS its attack "
           "power is a real build here. Both are FRACTIONS."))

N.append(node(
    "cinderblade", "Cinderblade",
    "Increases your spell critical strike chance by 20% of your Intellect and "
    "your chance to hit by 6%.",
    0, -3,
    effects={"crit_chance_spell_from_intellect_pct": 0.20,
             "hit_rating": 6.0},
    connect=["combusting_blade"],
    source="CoA's level 30 passive: 'Increases your critical strike rating by "
           "20% of your Intellect and your spell hit chance by 6%.' The "
           "conversion PORTS EXACTLY. The hit half is a flat 6% rather than a "
           "conversion, since hit_rating is NOT in STAT_CONVERSION_TARGETS - "
           "the sixth time in this audit that has cost a node. Together with "
           "Burning Power above, Intellect buys this spec attack power AND "
           "crit, which is why a plate melee class wants a caster stat."))

N.append(node(
    "combusting_blade", "Combusting Blade",
    "Increases your Intellect by 10% and reduces the Rage cost of Infernal "
    "Strike by 20%.",
    0, -1,
    effects={"intellect_pct": 10.0,
             "ability_knight_of_xoroth_infernal_strike_cost_pct": 0.20},
    connect=["to_ashes"],
    source="CoA over 2 ranks: 'Increases your Intellect by 5% and reduces the "
           "Rage cost of Infernal Strike by 5.' Doubled for the two ranks. "
           "Intellect is this spec's real scaling stat through Burning Power "
           "and Cinderblade, so this is a damage node wearing a caster's "
           "clothes. A flat 5 Rage is expressed as a percentage; POSITIVE "
           "reduces."))

N.append(node(
    "to_ashes", "To Ashes",
    "Increases the critical strike chance of Skulltaker, Warbringer and "
    "Meatsaw by 5%.",
    0, 1,
    effects={f"ability_{a}_crit": 5.0 for a in SPENDERS},
    connect=["flamewrath"],
    source="CoA verbatim: 'Increases the critical strike chance of abilities "
           "that spend Demonfire by 5%.' Demonfire is Frontier's DEATHFIRE "
           "and real, but no key names 'abilities that spend it' as a group, "
           "so CoA's three spenders are written out - the same treatment as "
           "War's Murderous Might. CoA's 5% kept."))

N.append(node(
    "flamewrath", "Flamewrath",
    "Increases the critical strike chance of Seeking Flame by 20%.",
    0, 3,
    effects={"ability_knight_of_xoroth_seeking_flame_crit": 20.0},
    connect=["hellmaw"],
    source="CoA verbatim: 'Increases the critical strike chance of Seeking "
           "Flame by 20%.' Ports exactly - Seeking Flame exists in Frontier "
           "and is a Deathfire generator."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "hellmaw", "Hellmaw",
    "Teaches Hellmaw, a shadowflame strike that burns over time.",
    1, -4,
    effects={"unlock_ability": "knight_of_xoroth_hellmaw"},
    connect=["invasion"],
    source="CoA verbatim: 'Burn an enemy with a fiery strike, dealing "
           "Shadowflame Damage, plus an additional amount over 12 seconds. "
           "Deals 20% increased damage per Demonfire consumed.' LOAD-BEARING "
           "UNLOCK: knight_of_xoroth_hellmaw carries requires_talent, so "
           "without this node it is unobtainable forever. The per-Demonfire "
           "scaling cannot be read (nothing reads a live resource amount) and "
           "lives on the ability or not at all; the talent only grants it. "
           "Kept at tier 1 where the shipped tree had it."))

N.append(node(
    "invasion", "Invasion",
    "Increases all damage you deal by 20%.",
    1, -2,
    effects={"all_damage": 0.20},
    connect=["pestilence_of_apocalypse"],
    source="CoA over 2 ranks: 'All Fire damage dealt is increased by 10% to "
           "enemies above 80% health.' Doubled for the two ranks. TWO WALLS: "
           "there is no per-school damage key, and NO EFFECT KEY READS A "
           "TARGET'S HEALTH PERCENTAGE. So it becomes all_damage applying "
           "always - broader and more reliable than CoA's, stated rather "
           "than hidden. This spec deals almost nothing but fire and "
           "shadowflame, so the school widening costs little."))

N.append(node(
    "pestilence_of_apocalypse", "Pestilence of Apocalypse",
    "Your fire strikes leave the enemy taking 10% more spell damage for 4 "
    "turns.",
    1, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": FIRE,
          "apply_effect": {
              "effect_id": "knight_of_xoroth_pestilence_apocalypse",
              "name": "Pestilence of Apocalypse", "effect_type": "debuff",
              "duration": 4, "max_stacks": 1,
              "stat_mods": {"spell_damage_taken_pct": 10.0},
              "on_target": True}},
    connect=["seeking_flame"],
    source="CoA verbatim: 'Emanate the Pestilence of Apocalypse, causing "
           "nearby enemies to take 10% increased Fire damage from you.' "
           "Frontier HAS Pestilence of Apocalypse as an ability and it is not "
           "gated, so this is not its unlock. There is no per-school "
           "damage-taken key beyond the existing siblings, so Fire becomes "
           "spell damage taken at CoA's own 10%; the 'from you' scoping has "
           "no key either. INSIDE A STATUS EFFECT spell_damage_taken_pct is "
           "divided by 100 and POSITIVE INCREASES damage taken."))

N.append(node(
    "seeking_flame", "Seeking Flame",
    "Increases the damage of Seeking Flame by 30% and reduces its cooldown by "
    "30%.",
    1, 2,
    effects={"ability_knight_of_xoroth_seeking_flame_damage": 0.30,
             "ability_knight_of_xoroth_seeking_flame_cooldown_pct": 0.30},
    connect=["hellfire_embers"],
    source="CoA verbatim: 'Seeking Flame. 20 Rage. 6 sec cooldown. Generates "
           "1 Demonfire. Sear an enemy, dealing Fire damage.' Frontier HAS "
           "Seeking Flame and it is NOT gated, so this cannot be its unlock. "
           "Built as damage and cooldown on the real ability. CoA's Grotesque "
           "('while Hellfire Form is active, Seeking Flame has no cooldown') "
           "needs a 'while active' gate that no key provides, and is folded "
           "in here as the cooldown reduction rather than built separately."))

N.append(node(
    "hellfire_embers", "Hellfire Embers",
    "Increases the damage your Hellfire Imp deals by 30%.",
    1, 4,
    effects={"pet_damage": 0.30},
    connect=["calamity"],
    source="CoA verbatim: 'Increases the Fire damage dealt by your Hellfire "
           "Imp by 30% against enemies above 80% maximum health.' PET_DAMAGE "
           "IS LIVE ON THIS CLASS - Knight of Xoroth genuinely summons "
           "(call_hellfire_imp, call_hellfire_abyssal, summon_greater_imp all "
           "carry summon fields), so the key reaches something real. That is "
           "not true of most classes: the same key would have been dead data "
           "on the Witch Doctor and Venomancer, which is what "
           "tools/qa_pet_keys.py checks. The health-threshold condition "
           "cannot be read, so CoA's 30% applies always."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "calamity", "Calamity",
    "Increases the damage of Unleash Pestilence by 25%.",
    2, -4,
    effects={"ability_knight_of_xoroth_unleash_pestilence_damage": 0.25},
    connect=["claws_of_hell"],
    source="CoA verbatim: 'Increases the damage of the Unleash effect of "
           "Pestilence of Apocalypse by 25% and its duration is increased by "
           "5 sec.' CoA's 'Unleash effect' is Unleash Pestilence, which "
           "Frontier has as its own ability. The duration half is dropped: it "
           "refers to the Pestilence buff rather than the Unleash, and no key "
           "extends another effect's duration."))

N.append(node(
    "claws_of_hell", "Claws of Hell",
    "Increases the damage of your Deathfire spenders by 20%.",
    2, -2,
    effects={f"ability_{a}_damage": 0.20 for a in SPENDERS},
    connect=["seething_strikes"],
    source="CoA verbatim: 'When you spend at least 4 Demonfire stacks you now "
           "refresh the duration of your Unleash Apocalypse on the target.' "
           "Two walls: nothing reads how much Deathfire a cast spent, and no "
           "payload refreshes a live effect's duration. So neither half is "
           "buildable. Re-pointed at the spenders' damage, which is what "
           "spending four Demonfire was for."))

N.append(node(
    "seething_strikes", "Seething Strikes",
    "Increases the damage of Sever by 30%, and it leaves the enemy taking 3% "
    "more spell damage for 4 turns.",
    2, 0,
    effects={"ability_knight_of_xoroth_sever_damage": 0.30},
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["knight_of_xoroth_sever"],
          "apply_effect": {
              "effect_id": "knight_of_xoroth_seething_strikes",
              "name": "Seething Strikes", "effect_type": "debuff",
              "duration": 4, "max_stacks": 1,
              "stat_mods": {"spell_damage_taken_pct": 3.0},
              "on_target": True}},
    connect=["inferno_blast"],
    source="CoA verbatim: 'Increases the damage of Sever by 30% against "
           "Burning targets and it now increases the targets chance to be "
           "critically struck by 3% for 12 seconds.' The Burning condition "
           "cannot be read - no effect key reads a target's debuffs - and "
           "this spec burns everything anyway. THERE IS NO RECIPIENT-SIDE "
           "'CHANCE TO BE CRIT' KEY, so that becomes spell damage taken at "
           "CoA's own 3%; 12 sec is 4 turns."))

N.append(node(
    "inferno_blast", "Inferno Blast",
    "Increases your critical strike damage by 40%.",
    2, 2,
    effects={"crit_damage_physical": 0.40},
    connect=["infernal_pummeling"],
    source="CoA over 2 ranks: 'Increases your critical damage against Burning "
           "targets by 20%.' Doubled for the two ranks. The Burning condition "
           "cannot be read, so CoA's figure applies always. "
           "crit_damage_physical is a FRACTION."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "infernal_pummeling", "Infernal Pummeling",
    "Melt leaves the enemy taking 10% more damage for 4 turns.",
    3, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["knight_of_xoroth_melt"],
          "apply_effect": {
              "effect_id": "knight_of_xoroth_infernal_pummeling",
              "name": "Infernal Pummeling", "effect_type": "debuff",
              "duration": 4, "max_stacks": 1,
              "stat_mods": {"damage_taken_pct": 0.10},
              "on_target": True}},
    connect=["rain_of_chaos"],
    source="CoA verbatim: 'Melt now increases the damage your target takes "
           "from Flames of Xoroth and Skulltaker by 10%.' The per-ability "
           "scoping has no key, so it is damage taken generally at CoA's own "
           "10%. BARE damage_taken_pct IS READ RAW, so 10% is 0.10 - "
           "authoring 10.0 would be +1000% damage taken, the mirror of the "
           "-20.0 that briefly made Boltslinger immortal."))

N.append(node(
    "rain_of_chaos", "Rain of Chaos",
    "Flames of Xoroth calls down molten rain, burning the enemy for fire "
    "damage over 3 turns.",
    3, -2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["knight_of_xoroth_flames_of_xoroth"],
          "apply_effect": {"effect_id": "knight_of_xoroth_rain_of_chaos",
                           "name": "Rain of Chaos", "effect_type": "dot",
                           "duration": 3, "potency": 46,
                           "damage_school": "fire", "on_target": True}},
    connect=["hellfire_rituals"],
    source="CoA verbatim: 'Casting Flames of Xoroth with 6 Demonfire now "
           "calls down a Rain of Chaos. Molten rain burns enemies in the area "
           "causing Fire Damage over 9 sec.' The 6-Demonfire condition cannot "
           "be read (nothing reads a live resource amount), so it fires on "
           "every cast. A burning area over 9 sec IS a dot, so the rest ports "
           "in shape - 9 sec as 3 turns, landing on the target rather than an "
           "area since there is no ground placement."))

N.append(node(
    "hellfire_rituals", "Hellfire Rituals",
    "Increases the health and armour of your demons by 30%.",
    3, 0,
    effects={"pet_health": 0.30, "pet_armor": 0.30},
    connect=["indiscriminate"],
    source="CoA verbatim: 'Critical strikes with Skulltaker now increases the "
           "haste of your Greater Imp by 15% for 8 seconds.' TWO WALLS: "
           "PET_HASTE IS READ BY NOTHING, and no proc payload can apply an "
           "effect to a pet - apply_effect reaches the caster or the "
           "trigger's target only. Re-pointed at the two remaining live pet "
           "keys, which is a longer-lived demon rather than a faster one. The "
           "keys DO work here because this class really summons; the same "
           "node on the Witch Doctor would have been dead data."))

N.append(node(
    "indiscriminate", "Indiscriminate",
    "Seeking Flame splashes 45% of its damage onto up to 3 nearby enemies.",
    3, 2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["knight_of_xoroth_seeking_flame"],
          "splash_damage": {"pct": 0.45, "max_targets": 3,
                            "school": "fire"}},
    connect=["doom"],
    source="CoA verbatim: 'Seeking Flame now spreads Hellmaw and Melt from "
           "the target to up to 3 enemies within 6 yds.' SPREADING DOTS TO "
           "NEW TARGETS IS NOT A PAYLOAD - apply_effect lands on the "
           "trigger's own target - so it becomes splash_damage at CoA's three "
           "targets, the same translation as the Witch Doctor's Malignant and "
           "Templar Crusader's Holy Tempest."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "doom", "Doom",
    "Increases the damage your demons deal by a further 40%.",
    4, -3,
    effects={"pet_damage": 0.40},
    connect=["hellbringer"],
    source="CoA verbatim: 'Transforms your Greater Imp into a Doomguard for "
           "12 seconds. While transformed, your Doomguard deals 20% more "
           "damage, and its auto attacks ignite the target, dealing 10% of "
           "the damage dealt as Fire damage over 6 seconds, stacking 6 "
           "times.' NOTHING TRANSFORMS A PET, and PETS NEVER FIRE PROCS - "
           "there is no fire_proc_trigger anywhere in entities/pet.py - so "
           "the ignite rider cannot exist either. Re-pointed at pet_damage, "
           "stacking with Hellfire Embers at tier 1 for 70% on a full "
           "Hellfire build, which is what a Doomguard was worth."))

N.append(node(
    "hellbringer", "Hellbringer",
    "Increases all damage you deal by a further 10%.",
    4, -1,
    effects={"all_damage": 0.10},
    connect=["grotesque"],
    source="CoA verbatim: 'Increases the all damage dealt by party and raid "
           "members by 3%. Does not stack with similar effects.' A TALENT "
           "CANNOT REACH AN ALLY - get_talent_effects() reads only the "
           "character's own trees - so the 3% lands on the Knight and the "
           "description says 'you'. Raised to 10% because it covers one "
           "character instead of five, the same reasoning as the Witch "
           "Doctor's Spirit of Battle."))

N.append(node(
    "grotesque", "Grotesque",
    "Your fire strikes grant 5 Deathfire.",
    4, 1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
          "ability_filter": FIRE,
          "grant_resource": {"resource": "deathfire", "amount": 5}},
    connect=["hellfire_form"],
    source="CoA verbatim: 'While Hellfire Form is active, your Seeking Flame "
           "now has no cooldown and generates an additional Demonfire.' The "
           "'while active' gate has no key and the cooldown half is already "
           "carried by the Seeking Flame node at tier 1. What survives is the "
           "extra Demonfire, granted off every fire strike rather than only "
           "in form - DEATHFIRE IS REAL (ResourceType.DEATHFIRE, four "
           "abilities generate into it), verified through gain_resource on "
           "the War tree. 1-turn icd so a multi-strike turn does not flood "
           "the pool."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "hellfire_form", "Hellfire Form",
    "Increases your spell damage by 20% and your spell critical strike chance "
    "by 15%.",
    5, -3,
    effects={"spell_damage": 0.20, "crit_chance_spell": 15.0},
    connect=["molten_fury"],
    source="CoA verbatim: 'Enter your Hellfire Form, increasing your Fire "
           "damage dealt by 20% and Fire critical strike chance by 15% for 15 "
           "sec.' Frontier HAS Hellfire Form as an ability and it is NOT "
           "talent-gated - the shipped tree carried an unlock node for it at "
           "tier 6, which therefore granted an ability the character already "
           "had and did nothing. This replaces that with the form's own "
           "numbers as a permanent passive: CoA's 20% and 15%, with the "
           "per-school scoping dropped (no per-school damage or crit key "
           "exists). Moved from tier 6 to 5 so tier 6 can carry a real "
           "capstone."))

N.append(node(
    "molten_fury", "Molten Fury",
    "Your critical strikes with fire strikes burn for extra fire damage.",
    5, -1,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "ability_filter": FIRE,
          "damage_flat": 100, "school": "fire"},
    connect=["hellstorm"],
    source="Built from CoA's Inferno Blast and Rain of Chaos themes rather "
           "than ported from one talent, so tier 5 carries a proc instead of "
           "a third flat damage line - and flagged as such. It fires off the "
           "three fire strikes the whole tree buffs, so it rewards the "
           "rotation the spec actually runs."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "hellstorm", "Hellstorm",
    "Increases the damage of Hellstorm and your fire strikes by 40%, and your "
    "damage-over-time spells by 25%.",
    6, 0,
    effects={"ability_knight_of_xoroth_hellstorm_damage": 0.40,
             **{f"ability_{a}_damage": 0.40 for a in FIRE},
             "dot_damage": 0.25},
    source="Frontier HAS Hellstorm as an ability and it is not gated, so this "
           "capstone grants nothing - the tree's only gated ability is "
           "Hellmaw at tier 1. Built as a pure payoff node on the three fire "
           "strikes the tree is about plus Hellstorm itself, and the dot "
           "bonus reaches Hellmaw's burn and Rain of Chaos at tier 3. NOT a "
           "port of a specific CoA talent - the shipped tree's tier 6 was a "
           "dead unlock node for Hellfire Form, whose real numbers now sit at "
           "tier 5 - and flagged as such."))


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
    print(f"Knight of Xoroth Hellfire: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points, {len(GATED)} load-bearing unlock")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
