#!/usr/bin/env python3
"""Rebuild Felsworn's Tyrant tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_felsworn_tyrant.py [--check]

SOURCE: data/reference/coa_worksheets/felsworn.md - 42 real Tyrant
talents, the largest Felsworn spec. Role: TANK.
Tyrant was 23 nodes with 7 procs.

THIS TREE RUNS ON AVOIDANCE, WHICH ONLY BECAME REAL ON 5 Nov 2026 when
Kyle had creature avoidance added (dodge on every template, parry on
humanoids). Before that, dodge and parry as stats were near-inert and the
on_dodge / on_parry / on_avoid triggers had nothing to fire from. CoA's
Tyrant is built on them - Nether Disciple, Illidari Training, Betrayer,
Vengeance Is Mine, Battle Finesse - and four of those now port.

THE TRAP ASSERTED IN main(): an avoided attack deals ZERO damage, so the
payloads that read the triggering hit's amount (leech_pct, bonus_pct,
smart_heal_pct) yield nothing on those triggers while looking perfectly
correct in the data. Everything avoidance-driven here uses
grant_resource, apply_effect, damage_flat or heal_flat.

TYRANT OWNS low_health_threshold_pct FOR THE WHOLE CLASS at CoA's 35%,
which is exactly what felsworn_tyrants_gaze already carries as its
execute_threshold_pct ("Only usable on enemies below 35% health"). So the
class's execute window matches its own execute ability's gate. That key
SUMS across talents and is UNSCALED, and a character can spend in several
trees, so Slayer and Infernal inherit it and set nothing. Enforced by
tools/qa_summing_thresholds.py.

NINE FELSWORN BUFFS HAD DURATIONS THAT WERE NEVER READ, fixed 6 Nov 2026
in the same commit as this tree and NOT optional here. None stated
buff_scope, so all nine inherited the engine's "raid" default - 30 real
MINUTES, with tick_status_effects skipping the effect entirely and the turn
`duration` never consulted. On a tank that is not cosmetic: Demonic Will is
-30% physical damage taken on a 10-turn cooldown and was permanently
active, and Illidan's Guile states 1 turn on an 18-turn cooldown. This tree
is built around those buffs, so they had to work first.

TWO PARTY AURAS CONVERTED to target_type "party" (Eye of the Tyrant,
Infernal Whipcrack), the same call Kyle made for Guardian's four. A talent
effect can never reach an ally; a party ABILITY does.

NOT BUILDABLE: every "while Inner Demon is active" clause (Demon Hide,
Bulwark of Azzinoth, Straight to the Nether, Grommash's Folly) and the
"above 75% health" half of Dark Lord; Carve's channel and everything
scaling off how long it was channelled (Battle Finesse, Quick Carving,
Unholy Endurance's threat, Hellfire Carver, Grommash's Folly's crit ramp) -
there is no channelling; Felspill and Demonic Blood fire on GENERATING
felfury, and nothing observes a resource gain; Abyssal Conditioning raises
Energy regeneration, for which every key is dead; Fel Torpedo and Illidan's
Favor add targets or transform abilities; Tyrannical Resolve's
damage-counting payout needs an accumulator and an on-expiry trigger, two
gaps at once.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/felsworn_tyrant.json"

#: The two party-targeted abilities this tree modifies rather than
#: duplicates. Asserted in main().
PARTY_ABILITIES = ["felsworn_eye_of_the_tyrant",
                   "felsworn_infernal_whipcrack"]

TREE = {
    "spec_name": "Felsworn Tyrant",
    "tree_id": "felsworn_tyrant",
    "description": ("A demon that gets paid for being hit - avoidance "
                    "into felfury, felfury into everything else."),
    "_source_note": (
        "Rebuilt 6 Nov 2026 from the 42 real CoA Tyrant talents (role "
        "TANK), the largest Felsworn spec. Built on the avoidance triggers, "
        "which only became meaningful when creature avoidance landed on "
        "5 Nov 2026 - four CoA talents port off them. Nine Felsworn buffs "
        "whose durations were never read had to be fixed first, because "
        "this tree is built around them and Demonic Will's -30% physical "
        "damage taken was permanently active. Tyrant owns "
        "low_health_threshold_pct for the class at CoA's 35%, matching "
        "tyrants_gaze's own execute gate."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20,
                          "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"felsworn_tyrant_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"felsworn_tyrant_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


DEMON = ("CoA gates this on INNER DEMON BEING ACTIVE, and nothing reads "
         "whether another effect is live. Dropped, priced unconditional. "
         "Four Tyrant talents carry this gate.")

CHANNEL = ("CoA scales this off HOW LONG CARVE WAS CHANNELLED. There is no "
           "channelling in this engine at all - our Carve is a 2-turn "
           "cooldown AoE strike - so nothing can scale off channel "
           "duration. Five Tyrant talents depend on it.")

NO_GAIN = ("CoA fires this on GENERATING Felfury, and nothing observes a "
           "resource gain - there is no on_resource_gain trigger, the same "
           "gap that killed Reaper Domination's Fatesealer and Chronomancer "
           "Time's Purgatory. Re-pointed to a live trigger.")

N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "nether_disciple", "Nether Disciple",
    "Increases your dodge and parry by 8%.",
    0, -4,
    effects={"dodge": 8.0, "parry": 8.0},
    connect=["infernal_constitution"],
    source="CoA over 2 ranks: 'Increases your dodge and parry chance by "
           "4%.' PORTS EXACTLY, doubled - and it would have been nearly "
           "inert a day earlier. Kyle had creature avoidance added on 5 Nov "
           "2026 (dodge on every template, parry on humanoids only), which "
           "is what makes both stats and this whole tree's avoidance "
           "triggers worth having. NOTE `dodge` AND `parry` ARE THE LIVE "
           "KEYS: dodge_chance, parry_chance and block_chance are all dead "
           "data that several talents in this project author. Both in "
           "PERCENTAGE POINTS. Was a pure scalar on our side."))

N.append(node(
    "infernal_constitution", "Infernal Constitution",
    "Increases your maximum health by 12% and your armor by 15%.",
    0, -2,
    effects={"max_health_pct": 0.12, "armor_pct": 15.0},
    connect=["hulking_demon", "burning_legionnaire"],
    source="CoA: 'Increases your maximum health by 10% and increases your "
           "off-hand weapon damage by 30%.' The health ports. THE OFF-HAND "
           "HALF CANNOT: the engine's weapon damage roll does not separate "
           "hands, and there is no off-hand damage key - which also cost "
           "Slayer's Slice & Dice and Trueshot Lodge Training their text. "
           "Replaced with armour, which a tank wants more than off-hand "
           "damage anyway. KEPT UNDER THE CAP DELIBERATELY: "
           "check_talent_balance enforces an armor_pct ceiling of 60 and "
           "Venomancer Fortitude currently breaches it at 62 from two "
           "stacking nodes, so this tree carries exactly one armour node. "
           "max_health_pct as a talent effect is a FRACTION; armor_pct is "
           "PERCENTAGE POINTS. Was a pure scalar on our side."))

N.append(node(
    "hulking_demon", "Hulking Demon",
    "Increases your attack power by 30% of your Stamina.",
    0, 0,
    effects={"attack_power_from_stamina_pct": 0.30},
    connect=["illidari_training"],
    source="CoA level 20 passive: 'Increases your attack power by 30% of "
           "your Stamina and your hit rating by 6% of your Agility.' The "
           "first half PORTS EXACTLY - attack_power is in "
           "STAT_CONVERSION_TARGETS and stamina is in "
           "STAT_CONVERSION_SOURCES, a legal pair, and it is the node that "
           "lets a Tyrant stack Stamina and still hit hard. The second half "
           "is DROPPED: hit_rating is NOT a valid conversion target, which "
           "with stamina-as-a-target has now cost ten nodes half their text "
           "across eight classes and is the most-repeated mistake in this "
           "audit. Note the asymmetry - stamina is a valid SOURCE but not a "
           "valid TARGET. A FRACTION. Was a pure scalar on our side."))

N.append(node(
    "burning_legionnaire", "Burning Legionnaire",
    "Reduces the cost of Twin Slice, Sunder and Felrend by 25%.",
    0, 2,
    effects={"ability_felsworn_twin_slice_cost_pct": 0.25,
             "ability_felsworn_sunder_cost_pct": 0.25,
             "ability_felsworn_felrend_cost_pct": 0.25},
    connect=["outland_slaver"],
    source="CoA: 'Reduces the Energy cost of Twin Slice and Sunder by "
           "-10.' CoA's Energy is our felfury - the single primary pool - "
           "so this is a real cost reduction, extended to Felrend, which "
           "CoA's Outland Slaver also discounts. Twin Slice and Felrend "
           "each generate 20 felfury, so cheapening them compounds with "
           "Vengeance below. *_cost_pct keys are FRACTIONS where POSITIVE "
           "MEANS A REDUCTION. Was a pure scalar on our side."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "illidari_training", "Illidari Training",
    "Dodging an attack generates 10 Felfury.",
    1, 0,
    proc={"trigger": "on_dodge", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "felfury", "amount": 10}},
    connect=["vengeance", "betrayer"],
    source="CoA: 'Dodging an attack now generates 3 Energy.' PORTS "
           "VERBATIM, and it is the node this whole tree is built on: a "
           "Tyrant funds his spenders by being attacked, which is what a "
           "tank does anyway. on_dodge is a live trigger and CoA's Energy "
           "is our felfury. 10 is what Twin Slice generates - one swing's "
           "worth per dodge. LEECH_PCT WOULD BE WRONG HERE and is asserted "
           "against in main(): a dodged attack deals ZERO damage, so an "
           "amount-reading payload silently yields nothing. grant_resource "
           "takes a FLAT `amount`; there is no pct_max field."))

N.append(node(
    "outland_slaver", "Outland Slaver",
    "Increases the damage of Felrend and Fel Fireball by 30%.",
    1, 2,
    effects={"ability_felsworn_felrend_damage": 0.30,
             "ability_felsworn_fel_fireball_damage": 0.30},
    connect=["unholy_endurance"],
    source="CoA over 2 ranks: 'Reduces the cost of your Felrend and Fel "
           "Fireball by 3 and increases their damage dealt by 15%.' The "
           "damage half ports exactly, doubled for the two ranks. The cost "
           "half is already covered by Burning Legionnaire above, so it is "
           "not duplicated here - stacking two cost reductions on Felrend "
           "would reach 50% off a 20-felfury generator, which on a tank "
           "that also gains felfury from dodging would be close to free. "
           "Both FRACTIONS."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "vengeance", "Vengeance",
    "Your attacks have a 60% chance to generate 10 additional Felfury.",
    2, -2,
    proc={"trigger": "on_weapon_swing", "chance": 60, "icd": 0,
          "grant_resource": {"resource": "felfury", "amount": 10}},
    connect=["demonic_fortitude"],
    source="CoA: 'Your Twin Slice and Felrend now have a 60% chance to "
           "generate 1 additional Felfury.' PORTS ALMOST VERBATIM, chance "
           "included; only the two-ability scoping goes, since there is no "
           "per-ability proc trigger - and both named abilities are "
           "weapon strikes, so on_weapon_swing is close to the same thing. "
           "Stacks with Illidari Training so a Tyrant gains felfury from "
           "both attacking and being attacked, which is CoA's design for "
           "the spec."))

N.append(node(
    "betrayer", "Betrayer",
    "Dodging or parrying an attack strikes the attacker for 90 physical "
    "damage.",
    2, 0,
    proc={"trigger": "on_avoid", "chance": 100, "icd": 0,
          "damage_flat": 90, "school": "physical"},
    connect=["demonic_fortitude"],
    source="CoA: 'Dodging attacks causes 40% off-hand Weapon Damage to "
           "attackers and enrages your party and raid members within 20 "
           "yds, increasing their critical strike chance by 2% for 10 "
           "seconds.' THE COUNTERATTACK PORTS: on_avoid is a live trigger "
           "covering dodge, parry and block, and damage_flat delivers a "
           "real hit. Two things do not. The off-hand scaling has no key "
           "(the weapon roll does not separate hands), so the damage is a "
           "flat number. And the party enrage cannot come from a talent at "
           "all - a talent effect never reaches an ally - with no Felsworn "
           "aura ABILITY of that shape to convert either, unlike Eye of the "
           "Tyrant and Infernal Whipcrack, which were converted to "
           "target_type 'party' on 6 Nov 2026. damage_flat RATHER THAN "
           "leech_pct IS LOAD-BEARING: a dodged attack deals zero damage, "
           "so an amount-reading payload would deal nothing. `school` only "
           "TYPES the payload; it is not a trigger-side filter."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "demonic_fortitude", "Demonic Fortitude",
    "Taking damage has a 20% chance to generate 10 Felfury.",
    3, -1,
    proc={"trigger": "on_damage_taken", "chance": 20, "icd": 0,
          "grant_resource": {"resource": "felfury", "amount": 10}},
    connect=["expose"],
    source="CoA: 'While Demonic Will or Hateforged Barrier are active, all "
           "damage taken or avoided now has a 20% chance to generate 1 "
           "Felfury.' PORTS ALMOST EXACTLY, chance included - "
           "on_damage_taken is a live trigger. " + DEMON + " (Both named "
           "buffs would in fact have been permanently active before 6 Nov "
           "2026, when nine Felsworn buffs were found to be 30-real-minute "
           "raid-scope effects whose turn duration was never read, so the "
           "condition would have been trivially true and the node would "
           "have looked correct for the wrong reason.) The 'or avoided' "
           "half is covered by Illidari Training two tiers up."))

N.append(node(
    "unholy_endurance", "Unholy Endurance",
    "Increases the damage of Carve by 20% and your threat generation by "
    "25%.",
    3, 2,
    effects={"ability_felsworn_carve_damage": 0.20,
             "threat_generation_pct": 0.25},
    connect=["expose"],
    source="CoA: 'Increases the damage and threat generated from Carve by "
           "15%.' BOTH HALVES BUILD, the threat as a global rather than "
           "per-ability: threat_generation_pct is live, a FRACTION, and "
           "POSITIVE INCREASES threat - which is what a tank wants and is "
           "the opposite sign convention from the *_cost_pct and "
           "*_cooldown_pct families in this same file, where positive means "
           "a reduction. " + CHANNEL + " so Carve is a plain 2-turn-cooldown "
           "AoE strike here. Was a pure scalar on our side."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "expose", "Expose",
    "Your damaging spells have a 35% chance to leave the target taking 10% "
    "more damage from you for 3 turns.",
    4, -1,
    proc={"trigger": "on_damage_cast", "chance": 35, "icd": 0,
          "apply_effect": {"effect_id": "expose", "name": "Expose",
                           "effect_type": "debuff", "duration": 3,
                           "stat_mods": {"damage_taken_pct": 0.10},
                           "dispel_type": "magic", "on_target": True}},
    connect=["vengeance_is_mine"],
    source="CoA: 'Direct Fire and Shadow spell damage dealt now applies "
           "Expose to enemies. Expose: damage taken from the Felsworn "
           "increased by 10% and the critical strike chance of all allies "
           "against this target is increased by 3% for 8 seconds.' The "
           "debuff's first clause ports at CoA's exact 10%. The ally crit "
           "cannot: a per-target ally buff is beyond even a party ABILITY, "
           "which can only carry flat stat_mods on the caster's allies, not "
           "conditional-on-a-target ones. The Fire/Shadow filter is dropped "
           "- proc['school'] only TYPES a damage_flat payload and is not a "
           "trigger-side filter. 8 sec -> 3 turns. CAREFUL: bare "
           "damage_taken_pct is read RAW ON BOTH SIDES, unlike physical_ "
           "and magic_, so 0.10 is 10% and authoring 10 would be +1000%. "
           "Asserted in main()."))

N.append(node(
    "tyrants_gaze", "Tyrant's Gaze",
    "Increases the damage of Tyrant's Gaze by 40%, its healing by 30%, and "
    "your damage against enemies below 35% health by 20%.",
    4, 2,
    effects={"ability_felsworn_tyrants_gaze_damage": 0.40,
             "ability_felsworn_tyrants_gaze_healing": 0.30,
             "low_health_damage_pct": 0.20,
             "low_health_threshold_pct": 0.35},
    connect=["vengeance_is_mine"],
    source="CoA: 'Set your fiery gaze upon an enemy, dealing Shadowflame "
           "Damage. Damaging an enemy in this way heals you and generates 1 "
           "Felfury. Only usable on enemies below 35% health.' THE EXECUTE "
           "GATE IS ALREADY REAL: felsworn_tyrants_gaze carries "
           "execute_threshold_pct 35, matching CoA exactly, enforced at "
           "abilities.py:1691. It is effect_type damage_and_heal, so it "
           "needs BOTH ability_<id>_damage AND ability_<id>_healing - "
           "authoring only _damage would buff the hit and leave the "
           "self-heal untouched, which is the mistake that left 18 talents "
           "across four classes silently doing nothing before _healing was "
           "accepted. THIS IS THE ONE NODE IN ALL OF FELSWORN THAT SETS "
           "low_health_threshold_pct, deliberately at CoA's 35% so the "
           "class's execute window matches this ability's own gate: that "
           "key SUMS across talents, is UNSCALED so rank does not divide "
           "it, and a character can spend in several trees of their class. "
           "Slayer and Infernal inherit it; a second setter would give 70%. "
           "Tinker once shipped two summing to 0.8. main() asserts exactly "
           "one, and tools/qa_summing_thresholds.py enforces it "
           "class-wide."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "vengeance_is_mine", "Vengeance Is Mine",
    "Avoiding an attack increases your damage by 15% for 3 turns and "
    "generates 10 Felfury.",
    5, 0,
    proc={"trigger": "on_avoid", "chance": 100, "icd": 1,
          "grant_resource": {"resource": "felfury", "amount": 10},
          "apply_effect": {"effect_id": "vengeance_is_mine",
                           "name": "Vengeance Is Mine",
                           "effect_type": "buff", "duration": 3,
                           "stat_mods": {"damage_dealt_pct": 15},
                           "dispel_type": None, "on_target": False}},
    connect=["fel_monstrosity"],
    source="CoA: 'Dodging or parrying an attack now gives you a 10% chance "
           "to make your next 10 instances of damage with Twin Slice deal "
           "30% increased damage and generate 1 Felfury.' PORTS WELL IN "
           "SHAPE: on_avoid covers dodging and parrying together, and one "
           "proc can carry both a grant_resource and an apply_effect. What "
           "cannot be built is 'your next 10 instances' - there is no "
           "charge or use-count system, which also killed Reaper's The Grim "
           "Reaper and Chronomancer Time's Timeblender - so it becomes a "
           "3-turn window, and 'with Twin Slice' widens to all damage "
           "because a status effect carries only generic keys. 10% chance "
           "-> 100% with a 1-turn ICD, since CoA's low chance was "
           "compensating for a 10-instance payout. damage_dealt_pct is "
           "PERCENTAGE POINTS inside a status effect."))

N.append(node(
    "nether_strength", "Nether Strength",
    "Reduces the cooldown of Burning Hatred, Hateforged Barrier and "
    "Demonic Will by 35%.",
    5, 2,
    effects={"ability_felsworn_burning_hatred_cooldown_pct": 0.35,
             "ability_felsworn_hateforged_barrier_cooldown_pct": 0.35,
             "ability_felsworn_demonic_will_cooldown_pct": 0.35},
    connect=["fel_monstrosity"],
    source="CoA: 'Casting Felfury spenders now reduces the cooldown of "
           "Burning Hatred, Hateforged Barrier, and Demonic Will by -1 "
           "sec.' The proc form cannot be built - there is no per-ability "
           "proc trigger and no 'Felfury spender' category - so it becomes "
           "a flat reduction on all three, exactly the abilities CoA names. "
           "Folded in CoA's Mannoroth's Rage, which reduces Burning "
           "Hatred's cooldown by 60 sec. ALL THREE OF THESE WERE AMONG THE "
           "NINE FELSWORN BUFFS whose turn duration was never read until "
           "6 Nov 2026 - they inherited the 'raid' default, meaning 30 real "
           "minutes - so before that fix this node would have been "
           "shortening the cooldown on effects that never expired. "
           "FRACTIONS where POSITIVE MEANS A REDUCTION; talented_cooldown "
           "floors at 1 turn."))

N.append(node(
    "eye_of_the_tyrant", "Eye of the Tyrant",
    "Increases your Stamina and attack power by 6%, and reduces the "
    "cooldown of your Eye of the Tyrant and Infernal Whipcrack auras by "
    "35%.",
    5, -2,
    effects={"stamina_pct": 6, "attack_power_pct": 6.0,
             "ability_felsworn_eye_of_the_tyrant_cooldown_pct": 0.35,
             "ability_felsworn_infernal_whipcrack_cooldown_pct": 0.35},
    connect=["fel_monstrosity"],
    source="CoA: 'Grant 10% increased melee and ranged haste to party and "
           "raid members within 100 yds. Does not stack with similar "
           "effects. In addition, your Stamina and attack power is "
           "increased by 4%.' THE SELFISH HALF PORTS (raised to 6%); THE "
           "PARTY HALF IS REAL BUT NOT FROM HERE, because a talent effect "
           "can never reach an ally. Both felsworn_eye_of_the_tyrant and "
           "felsworn_infernal_whipcrack were converted from target_type "
           "'self' to 'party' on 6 Nov 2026 - the same call Kyle made for "
           "Guardian's four auras on 5 Nov and that was applied to Reaper's "
           "two and Necromancer's three today - so the aura is live and "
           "this talent does what a talent can: make both available far "
           "more often. Folded in CoA's Taskmaster's Army, which reduces "
           "Infernal Whipcrack's cooldown. BOTH PERCENTAGE-STAT KEYS ARE "
           "POINTS: stamina_pct and attack_power_pct both divide by 100, "
           "and audit_talents caught me authoring attack_power_pct as a "
           "fraction on Ranger Brigand tonight."))

N.append(node(
    "pure_hatred", "Pure Hatred",
    "Increases your maximum health by a further 8% and reduces your magic "
    "damage taken by 8%.",
    1, -4,
    effects={"max_health_pct": 0.08, "magic_damage_taken_pct": -0.08},
    connect=["nether_disciple"],
    source="CoA: 'Your Hateforged Barrier now also scales with your maximum "
           "health.' Hateforged Barrier is a 3-turn self-buff in our data "
           "with no absorb amount to rescale - there is no key that changes "
           "what a buff's shield scales off, and shield_pct and "
           "absorb_pct_max_health are PROC PAYLOAD fields rather than "
           "ability modifiers. So the node delivers the health itself plus "
           "magic mitigation, which is what 'your barrier scales with "
           "health' amounts to for a tank. BOTH KEYS ARE FRACTIONS AS "
           "TALENT EFFECTS and both flip inside a status effect, where "
           "max_health_pct becomes percentage points and "
           "magic_damage_taken_pct becomes points AND positive increases "
           "damage taken. Was a pure scalar on our side."))

N.append(node(
    "doomscarring", "Doomscarring",
    "Your attacks have a 35% chance to scar the target, lowering their "
    "armor for 4 turns.",
    2, 2,
    proc={"trigger": "on_weapon_swing", "chance": 35, "icd": 0,
          "apply_effect": {"effect_id": "doomscarring",
                           "name": "Doomscarring",
                           "effect_type": "debuff", "duration": 4,
                           "stat_mods": {"armor": -160},
                           "max_stacks": 3, "dispel_type": None,
                           "on_target": True}},
    connect=["outland_slaver"],
    source="CoA: 'Twin Slice now deals an additional Physical damage and "
           "scars enemies for 12 seconds, increasing your allies' attack "
           "power against them by 45 + 15% Agility.' AN ALLY BUFF SCOPED TO "
           "ONE TARGET is beyond anything the engine offers - a talent "
           "effect never reaches an ally, and even a party ABILITY can only "
           "carry flat stat_mods, not per-target conditional ones, which is "
           "the same wall Expose's ally-crit clause and Reaper's Scars of "
           "Suffering hit. Rebuilt as an armour strip, which lets the "
           "PARTY's physical damage land harder on that target - the same "
           "outcome by a readable route. `armor` on a monster is FLAT "
           "(Monster.armor is base_armor + the status mod), so -160 per "
           "stack and -480 at three. 12 sec -> 4 turns."))

N.append(node(
    "fel_daze", "Fel Daze",
    "Increases the critical strike chance of Fel Fireball by 10%, and your "
    "damaging spells have a 30% chance to weaken the target's attacks for "
    "3 turns.",
    3, 4,
    effects={"ability_felsworn_fel_fireball_crit": 10.0},
    proc={"trigger": "on_damage_cast", "chance": 30, "icd": 0,
          "apply_effect": {"effect_id": "fel_daze", "name": "Fel Daze",
                           "effect_type": "debuff", "duration": 3,
                           "stat_mods": {"attack_power": -95},
                           "dispel_type": "magic", "on_target": True}},
    connect=["unholy_endurance"],
    source="CoA: 'Increases the critical strike chance of Fel Fireball by "
           "10% and it's damage dealt now reduces the enemy's chance to hit "
           "by 3% for 6 sec.' The crit ports verbatim. THERE IS NO "
           "RECIPIENT-SIDE 'CHANCE TO BE HIT' OR ATTACKER-SIDE "
           "hit-reduction KEY a debuff can carry - the eight stat_mods a "
           "monster reads are armor, attack_power, damage_taken_pct, "
           "healing_taken_pct, magic/physical/spell_damage_taken_pct and "
           "magic_resistance - so this becomes a flat attack power "
           "reduction, which reduces incoming damage the same way fewer "
           "landed hits would. Ranger Farstrider's Venom-Coated Seeds "
           "needed the identical substitution. attack_power is FLAT on a "
           "monster. 6 sec -> 3 turns."))

N.append(node(
    "dark_lord", "Dark Lord",
    "Reduces all damage you take by a further 5% and increases your damage "
    "dealt by 5%.",
    4, 4,
    effects={"damage_taken_pct": -0.05, "all_damage": 0.05},
    connect=["tyrants_gaze"],
    source="CoA: 'While above 75% health, your damage taken is reduced by "
           "-5% and damage dealt is increased by 5%.' Both values port; the "
           "condition does not. high_health_damage_threshold_pct is DEAD "
           "DATA - authored somewhere in this project and read by nothing - "
           "and there is no above-health conditional of any kind, only the "
           "below-health low_health_damage_pct added 6 Nov 2026. A tank "
           "node gated on being healthy is also the least useful shape of "
           "that conditional, so making it unconditional loses little of "
           "CoA's intent. BOTH FRACTIONS as talent effects; "
           "damage_taken_pct is read RAW (character.py:2696), so -0.05 is "
           "-5%. Was a pure scalar on our side."))

N.append(node(
    "tyrannical_resolve", "Tyrannical Resolve",
    "Reduces the cooldown of Tyrannical Resolve by 40% and increases your "
    "threat generation by a further 25%.",
    5, 4,
    effects={"ability_felsworn_tyrannical_resolve_cooldown_pct": 0.40,
             "threat_generation_pct": 0.25},
    connect=["tyrants_gaze"],
    source="CoA: 'Taunt nearby enemies for 4 seconds and ignore -50% of all "
           "damage taken for 30 seconds, up to 100% of your maximum health. "
           "When this ends, you unleash a Felfire Blast that leeches health "
           "from nearby enemies based on how many times you took damage "
           "with the effect active.' The ability already exists as a 2-turn "
           "self-buff. ITS PAYOUT NEEDS TWO THINGS THAT DO NOT EXIST: an "
           "accumulator to count damage taken during the window (the gap "
           "that killed Chronomancer's The Vast Infinite, Puppeteer's "
           "Threads and Oathkeeper) and a trigger on the effect EXPIRING. "
           "So the node makes the existing cooldown available more often "
           "and adds threat, stacking with Unholy Endurance to +50%. "
           "THIS BUFF WAS ONE OF THE NINE whose turn duration was never "
           "read until 6 Nov 2026 - at 'raid' scope its stated 2 turns were "
           "actually 30 real minutes, so a -damage-taken tank cooldown on a "
           "16-turn cooldown was simply permanent. threat_generation_pct is "
           "a FRACTION where POSITIVE INCREASES threat."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "fel_monstrosity", "Fel Monstrosity",
    "Increases your Stamina by 25%, reduces all damage you take by 8%, and "
    "avoiding an attack heals you.",
    6, 0,
    effects={"stamina_pct": 25, "damage_taken_pct": -0.08},
    proc={"trigger": "on_avoid", "chance": 100, "icd": 0,
          "heal_flat": 95},
    source="CoA level 50 passive: 'Increases your Stamina by 25% and size "
           "by 10%.' The Stamina ports verbatim (size is cosmetic and there "
           "is no model scaling). Folded in CoA's Bulwark of Azzinoth "
           "('Inner Demon now also reduces your damage taken by 10%'), "
           "whose condition cannot be built - " + DEMON + " - and CoA's "
           "Demonic Will self-heal clause, as the capstone's payoff on the "
           "trigger this entire tree is built on. A fully-talented Tyrant "
           "who dodges now gains felfury (Illidari Training), damage "
           "(Vengeance Is Mine), a counterattack (Betrayer) and a heal, all "
           "from one roll. heal_flat RATHER THAN leech_pct IS THE WHOLE "
           "POINT and is asserted in main(): an avoided attack deals ZERO "
           "damage, so an amount-reading payload would heal nothing while "
           "looking correct. stamina_pct is PERCENTAGE POINTS; "
           "damage_taken_pct as a talent effect is read RAW "
           "(character.py:2696), so -0.08 is -8%."))


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
    assert len(setters) == 1, (
        f"low_health_threshold_pct SUMS across talents and is UNSCALED, and "
        f"a character can spend in several Felsworn trees - exactly one "
        f"node in the CLASS may set it, and Tyrant owns it at CoA's 35%. "
        f"Found {setters}")

    abilities = json.loads(
        (ROOT / "data/abilities/felsworn.json").read_text())["abilities"]
    by_id = {a["ability_id"]: a for a in abilities}

    # The class execute window must match the ability's own gate, or the
    # tree promises damage on targets Tyrant's Gaze cannot even be cast at.
    gaze = by_id.get("felsworn_tyrants_gaze")
    assert gaze is not None and gaze.get("execute_threshold_pct") == 35, (
        "felsworn_tyrants_gaze must keep execute_threshold_pct 35 - this "
        "tree sets the class's low_health_threshold_pct to 0.35 to match "
        "it, and the two drifting apart would be silent")

    # Half this tree's party value depends on these staying party-targeted.
    for aid in PARTY_ABILITIES:
        a = by_id.get(aid)
        assert a is not None and a.get("target_type") == "party", (
            f"{aid} must stay target_type 'party' - the Eye of the Tyrant "
            f"node exists to shorten its cooldown AS a party aura, because "
            f"a talent effect can never reach an ally")

    AVOIDANCE = ("on_avoid", "on_parry", "on_dodge", "on_block")
    for n in TREE["nodes"]:
        proc = n.get("proc") or {}
        if proc.get("trigger") in AVOIDANCE:
            for payload in ("leech_pct", "bonus_pct", "smart_heal_pct"):
                assert payload not in proc, (
                    f"{n['talent_id']} uses {payload} on "
                    f"{proc['trigger']} - an avoided attack deals 0 damage, "
                    f"so it silently yields nothing. Use heal_flat, "
                    f"damage_flat, grant_resource or apply_effect")
        gr = proc.get("grant_resource")
        if gr:
            assert gr.get("resource") == "felfury" and "amount" in gr, (
                f"{n['talent_id']} grant_resource must name felfury with a "
                f"FLAT amount")
        mods = (proc.get("apply_effect") or {}).get("stat_mods") or {}
        if "damage_taken_pct" in mods:
            assert -1 < mods["damage_taken_pct"] < 1, (
                f"{n['talent_id']} damage_taken_pct={mods['damage_taken_pct']}"
                f" - read RAW on both sides, so 10 means +1000%")
        eff = n.get("effects") or {}
        for dead in ("dodge_chance", "parry_chance", "block_chance"):
            assert dead not in eff, (
                f"{n['talent_id']} authors {dead}, read by no engine code - "
                f"the live key is {dead.replace('_chance','')}")

    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Felsworn Tyrant: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points, {len(PARTY_ABILITIES)} party auras modified")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
