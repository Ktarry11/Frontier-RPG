#!/usr/bin/env python3
"""Rebuild Reaper's Domination tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_reaper_domination.py [--check]

SOURCE: data/reference/coa_worksheets/reaper.md and
data/reference/coa/reaper.json - 37 real Domination talents from
Ascension's own CoA Builder payload. Role: TANK.

Domination was 23 nodes with 4 procs.

THE AVOIDANCE TRIGGERS MAKE THIS TREE WORK, and they only became worth
building on 5 Nov 2026. on_avoid, on_parry, on_dodge and on_block are all
live triggers, and Kyle had creature avoidance added that day (dodge on
every template, parry on humanoids) which made `expertise` a real stat for
the first time. CoA's Domination is built on avoidance - Empyrean
Fortitude, Soul Slip and Soul Knight all key off parrying or dodging - and
all three port almost verbatim here.

ONE TRAP ON THOSE TRIGGERS, asserted in main(): the payloads that READ the
triggering hit's amount (leech_pct, bonus_pct) see ZERO on an avoided
attack, because an avoided attack deals no damage. They would heal and add
nothing while looking perfectly correct in the data. Anything firing off
avoidance uses grant_resource, apply_effect, damage_flat or heal_flat.

REAPER ACTUALLY SUMMONS PETS, unlike most classes this audit has touched:
reaper_spectral_scythe and reaper_spectral_warden are real summon_pet
abilities with real templates, and Spectral Scythe costs 35 SOULS, so
CoA's "consumes Reaped Souls" is literally true. That makes pet_damage,
pet_health and pet_armor legal keys here - they would have been silent
dead data on a petless class, which is what tools/qa_pet_keys.py exists to
catch after Witch Doctor Shadow Hunting shipped three of them.

BUT PETS NEVER FIRE PROCS (there is no fire_proc_trigger anywhere in
entities/pet.py), nothing reads a live pet count, no proc can apply an
effect to a pet, and pet_haste is read by nothing. So Warden of the Lost
("damage dealt by Spectral Scythes reduces the cooldown of Spectral
Warden"), Siphon Anima ("when you summon a Spectral Scythe you heal for 5%
of your damage dealt"), Spirit Army's extra summons and Spectral Scythe's
"1 per Reaped Soul active" are all unbuildable. Pets scale off the three
keys above and nothing else.

STAMINA AND ARMOR PENETRATION ARE NOT CONVERSION TARGETS, which costs this
tree two talents' worth of text. Behemoth's "Armor penetration by 10% of
your Strength" and Dark Soul's "Stamina equal to your Armor penetration
rating" both need a target that STAT_CONVERSION_TARGETS does not contain -
it holds attack_power/ap, ranged_ap, spell_power/spell_damage,
healing_power, armor, block_value/block, parry, dodge, haste, crit_chance/
crit and crit_chance_spell, and nothing else. A conversion target must
name a REAL attribute: "block" wrote a phantom one for months and silently
killed Sun Cleric Seraphim's Clarity of the Heavens. Both halves become
flat bonuses instead.

THE CLASS THRESHOLD IS OWNED BY HARVEST. Final Requiem uses
low_health_damage_pct but does NOT set low_health_threshold_pct, because
that key SUMS across talents and a character can spend in several trees of
their class - Harvest's Executioner sets 0.35 for all of Reaper. Asserted
here and enforced across every class by tools/qa_summing_thresholds.py.

WHAT COULD NOT BE BUILT AT ALL:
  - Fatesealer and Spirit Culling's second clause - both trigger on
    GENERATING a soul, and nothing observes a resource gain. There is no
    on_resource_gain trigger.
  - Painmail - stacks that pay out when they EXPIRE NATURALLY. No trigger
    fires on an effect expiring, and nothing reads a stack count. Two gaps.
  - Harnessed Life ("25% chance to not consume a stack") - nothing
    intercepts stack consumption.
  - Hard Bargain, Spirit Culling's first clause, Intimidating Presence -
    all read whether another effect is currently active.
  - Dreadknight's "armor contribution from mail and plate" - armour is not
    tracked by item type - and "reduces the chance for spells to hit you",
    for which there is no recipient-side hit key.
  - Essence Binder ("steals the target's health and Strength") - no stat
    theft mechanic; a debuff cannot move a stat to the caster.
  - Spirit Realm, To The Shadowlands, Well of Eternity - radius and
    sub-turn duration clauses.
  - Decimation - CoA's payload is the literal string "$c2", so their data
    is broken and there is nothing to port. Redshade in Harvest was the
    same.

THIS TREE OWNS THREE GATED ABILITIES: ethereal_guard, spectral_warden and
eater_of_souls. All three carry requires_talent and this is their only
unlock. Asserted in main().

ETHEREAL GUARD WAS CONVERTED TO A PARTY ABILITY (6 Nov 2026), like Soul's
Death's Presence: CoA has it reduce damage taken by party and raid
members, a talent effect cannot reach an ally, and a party-targeted
ability can. On a TANK this is the aura that most needs to actually land.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/reaper_domination.json"

#: Abilities carrying requires_talent that ONLY this tree unlocks.
GATED = {"reaper_ethereal_guard", "reaper_spectral_warden",
         "reaper_eater_of_souls"}

TREE = {
    "spec_name": "Reaper Domination",
    "tree_id": "reaper_domination",
    "description": ("A tank who turns every parried blow into a soul and "
                    "every soul into something that fights for him."),
    "_source_note": (
        "Rebuilt 6 Nov 2026 from the 37 real CoA Domination talents (role "
        "TANK). Built on the avoidance triggers - on_parry, on_dodge, "
        "on_avoid - which only became worth using after Kyle had creature "
        "avoidance added on 5 Nov 2026. Empyrean Fortitude, Soul Slip and "
        "Soul Knight all port almost verbatim. Reaper genuinely summons "
        "pets (Spectral Scythe costs 35 souls), so pet_damage/pet_health/"
        "pet_armor are legal here - but pets never fire procs, so every "
        "talent keyed on pet damage is dropped. Stamina and armor "
        "penetration are NOT conversion targets, which costs Behemoth and "
        "Dark Soul half their text. Final Requiem does not set the class "
        "threshold; Harvest's Executioner owns it. Three load-bearing "
        "unlocks, asserted."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20,
                          "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"reaper_domination_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"reaper_domination_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


#: Appended wherever CoA's clause fires on gaining a soul.
NO_GAIN_TRIGGER = (
    "CoA fires this on GENERATING a Reaped Soul, and nothing in this engine "
    "observes a resource gain - there is no on_resource_gain trigger, the "
    "same gap that killed Chronomancer Time's Purgatory. Re-pointed to a "
    "trigger that does exist and that this spec presses constantly.")

#: Appended wherever CoA's clause depends on the pets.
NO_PET_PROCS = (
    "Reaper really does summon pets - spectral_scythe and spectral_warden "
    "are summon_pet abilities with real templates - but PETS NEVER FIRE "
    "PROCS (no fire_proc_trigger anywhere in entities/pet.py), nothing "
    "reads a live pet count, and no proc can apply an effect to a pet. "
    "Pets scale off pet_damage, pet_health and pet_armor and nothing else.")

N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "empyrean_fortitude", "Empyrean Fortitude",
    "Increases your parry chance by 5%, and parrying an attack restores 12 "
    "mana.",
    0, -4,
    effects={"parry": 5.0},
    proc={"trigger": "on_parry", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "mana", "amount": 12}},
    connect=["dark_soldier"],
    source="CoA: 'Increases your parry chance by 5% and parrying an attack "
           "now generates 2 Runic Power.' BOTH HALVES PORT VERBATIM, which "
           "needed two separate things to be true. on_parry is a live "
           "trigger, and parry only became worth having on 5 Nov 2026 when "
           "Kyle had creature avoidance added - before that monsters could "
           "not attack in a way parry answered, and `parry` as a stat was "
           "near-inert. CoA's Runic Power is our mana. NOTE `parry` is the "
           "live key and PERCENTAGE POINTS; `parry_chance` is dead data "
           "that several talents authored. grant_resource's `amount` is "
           "FLAT. leech_pct would be wrong here and is asserted against in "
           "main(): a parried attack deals ZERO damage, so an "
           "amount-reading payload silently yields nothing."))

N.append(node(
    "dark_soldier", "Dark Soldier",
    "Increases your hit chance by 6% and reduces magic damage taken by 6%.",
    0, -2,
    effects={"hit_rating": 6.0, "magic_damage_taken_pct": -0.06},
    connect=["behemoth", "dominator"],
    source="CoA over 2 ranks: 'Increases your hit chance and reduces your "
           "Magic damage taken by -3%.' PORTS EXACTLY, doubled for the two "
           "ranks. hit_rating is live as a FLAT bonus in PERCENTAGE POINTS "
           "(it is only invalid as a CONVERSION target). "
           "magic_damage_taken_pct as a TALENT effect is a FRACTION read "
           "raw (character.py:2748), where inside a STATUS EFFECT the same "
           "key is percentage points AND a positive value INCREASES damage "
           "taken - so this pair flips twice depending on where it is "
           "written. Negative here means mitigation. Was a pure scalar on "
           "our side."))

N.append(node(
    "behemoth", "Behemoth",
    "Increases your Stamina by 20% and your armor penetration by 80.",
    0, 0,
    effects={"stamina_pct": 20, "armor_penetration": 80},
    connect=["soul_slip"],
    source="CoA level 20 passive: 'Increases your Stamina by 20% and your "
           "Armor penetration by 10% of your Strength.' The Stamina half "
           "ports. THE CONVERSION HALF CANNOT: armor_penetration is not in "
           "STAT_CONVERSION_TARGETS, so 'armor pen from Strength' has no "
           "legal pairing and would have written a phantom attribute that "
           "nothing reads. Built as a flat 80 rating instead - "
           "armor_penetration IS live (monster.py:659, via _pen_flat), just "
           "flat rather than convertible. stamina_pct is PERCENTAGE POINTS "
           "(character.py:1263 divides by 100); armor_penetration is a FLAT "
           "RATING, which is why it sits oddly beside the fractions in this "
           "file. Was a pure scalar on our side."))

N.append(node(
    "dominator", "Dominator",
    "Reduces the mana cost of Soul Strike by 25% and of Dreadwake by 15%.",
    0, 2,
    effects={"ability_reaper_soul_strike_cost_pct": 0.25,
             "ability_reaper_dreadwake_cost_pct": 0.15},
    connect=["lifestealer"],
    source="CoA: 'Reduces the Runic Power cost of Soul Strike by $/10s;s1.' "
           "CoA's own payload is a broken template string there, so the "
           "number is invented rather than ported - 25% on the spec's main "
           "attack. Folded in CoA's Hard Bargain clause 'your Dreadwake "
           "costs -5 less Runic Power', whose 'while Tormented Souls is "
           "active' condition cannot be built (nothing reads whether "
           "another effect is live). *_cost_pct keys are FRACTIONS where "
           "POSITIVE MEANS A REDUCTION. Was a pure scalar on our side."))

N.append(node(
    "dreadknight", "Dreadknight",
    "Increases your armor by 16% and your maximum health by 8%.",
    0, 4,
    effects={"armor_pct": 16.0, "max_health_pct": 0.08},
    connect=["soul_knight"],
    source="CoA over 2 ranks: 'Increases your armor contribution from mail "
           "and plate items by 20% and reduces the chance for spells to hit "
           "you by -2%.' Neither qualifier survives: armour is not tracked "
           "by item type, and there is no recipient-side 'chance to be hit' "
           "key anywhere (Chronomancer's Magic Erosion hit the same wall "
           "from the attacker's side). Rebuilt as flat armour plus health, "
           "the two things a tank wants from this node. KEPT WELL UNDER THE "
           "CAP ON PURPOSE: check_talent_balance enforces an armor_pct "
           "ceiling of 60 and Venomancer Fortitude currently breaches it at "
           "62 from two stacking nodes, so this tree carries exactly one "
           "armour node. armor_pct is PERCENTAGE POINTS; max_health_pct as "
           "a talent effect is a FRACTION. Was a pure scalar on our side."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "soul_slip", "Soul Slip",
    "Avoiding an attack has a 50% chance to harvest 10 souls from the "
    "attacker.",
    1, 0,
    proc={"trigger": "on_avoid", "chance": 50, "icd": 0,
          "grant_resource": {"resource": "souls", "amount": 10}},
    connect=["soultaker", "jailers_will"],
    source="CoA level 30 passive: 'Avoiding attacks now has a 50% chance to "
           "harvest a Soul Fragment from the attacker.' PORTS VERBATIM, "
           "chance included. on_avoid is a live trigger covering dodge, "
           "parry and block, and souls are a real resource with thirteen "
           "generators, so both halves land. 10 souls is what Reap "
           "generates - one fragment in this economy's units. This node is "
           "the spec's engine: a Domination Reaper funds his soul spenders "
           "by being attacked, which is what a tank does anyway."))

N.append(node(
    "lifestealer", "Lifestealer",
    "Increases the healing of Soul Strike by 30%.",
    1, 3,
    effects={"ability_reaper_soul_strike_healing": 0.30},
    connect=["soul_knight"],
    source="CoA: 'Increases the missing health generated by Soul Strike by "
           "3%.' Soul Strike is effect_type damage_and_heal in our data, so "
           "it takes ability_<id>_HEALING for its heal half - a key that "
           "went unread while 18 talents across four classes authored it, "
           "because only _damage was ever looked up. Using _damage here "
           "would buff the damage and leave the heal alone, which is the "
           "opposite of CoA's intent and would pass every check. The "
           "missing-health scaling cannot be built (nothing scales a heal "
           "off the recipient's deficit), so it is a flat 30%. Was a pure "
           "scalar on our side. A FRACTION."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "soultaker", "Soultaker",
    "Your attacks have a 30% chance to reduce the cooldown of Tormented "
    "Souls by 2 turns.",
    2, -2,
    proc={"trigger": "on_weapon_swing", "chance": 30, "icd": 1,
          "reset_cooldown": {"abilities": ["reaper_tormented_souls"],
                             "turns": 2}},
    connect=["ethereal_guard"],
    source="CoA: 'Damage dealt with Dreadwake now reduces the cooldown of "
           "Tormented Souls by -1 sec.' PORTS ALMOST EXACTLY - the "
           "{abilities, turns} form of reset_cooldown shaves turns rather "
           "than resetting outright, which is what CoA describes; a BARE "
           "LIST would reset it fully, and confusing the two is silent. "
           "Only the Dreadwake scoping goes (no per-ability proc trigger). "
           "Folded in CoA's shared Tormentor passive, which also shortens "
           "Tormented Souls but triggers on consuming Soul Infusion - and "
           "nothing observes a resource spend. 1 sec -> 2 turns, since a "
           "sub-turn reduction rounds to nothing. Was a pure scalar on our "
           "side."))

N.append(node(
    "jailers_will", "Jailer's Will",
    "Increases the damage of Soul Strike by 30% and your attack power by "
    "15% of your Strength.",
    2, 1,
    effects={"ability_reaper_soul_strike_damage": 0.30,
             "attack_power_from_strength_pct": 0.15},
    connect=["well_of_souls"],
    source="CoA: 'Soul Strike now deals 30% Strength increased damage, "
           "scaling with Strength.' The per-ability damage ports exactly, "
           "and the Strength scaling becomes a real conversion: "
           "attack_power is in STAT_CONVERSION_TARGETS and strength in "
           "STAT_CONVERSION_SOURCES, so this is a LEGAL PAIR, unlike "
           "Behemoth's armor-pen-from-Strength two tiers below, which has "
           "no valid target. Both keys are FRACTIONS. Was a pure scalar on "
           "our side."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "ethereal_guard", "Ethereal Guard",
    "Teaches Ethereal Guard, a ward that blunts what strikes your party.",
    3, -2,
    effects={"unlock_ability": "reaper_ethereal_guard"},
    connect=["spectral_warden"],
    source="CoA: 'Reduces the damage taken by party and raid members by "
           "-3%. Does not stack with similar effects. In addition, "
           "increases your melee haste by 10%.' LOAD-BEARING UNLOCK - "
           "reaper_ethereal_guard carries requires_talent and this is its "
           "only unlock node. THE PARTY HALF IS REAL ONLY BECAUSE THE "
           "ABILITY WAS CONVERTED on 6 Nov 2026 from target_type 'self' to "
           "'party': a talent effect can never reach an ally, while a "
           "party-targeted ability resolves to all living allies "
           "(abilities.py:2064) and degrades to the caster alone with no "
           "party context. Same call Kyle made for Guardian's four auras on "
           "5 Nov 2026, and on a TANK it is the aura that most needs to "
           "land. Its damage_taken_pct of -0.03 is correct as authored: "
           "that key is read RAW on both sides, unlike physical_ and "
           "magic_, which divide by 100 inside a status effect. The "
           "does-not-stack clause has no mechanism short of every class's "
           "equivalent aura sharing an exclusive_group, which is a "
           "project-wide decision."))

N.append(node(
    "soul_knight", "Soul Knight",
    "Avoiding an attack increases healing you receive by 4% and reduces "
    "magic damage taken by 3% for 3 turns, stacking up to 5 times.",
    3, 2,
    proc={"trigger": "on_avoid", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "soul_knight", "name": "Soul Knight",
                           "effect_type": "buff", "duration": 3,
                           "stat_mods": {"healing_taken_pct": 4,
                                         "magic_damage_taken_pct": -3},
                           "max_stacks": 5, "dispel_type": None,
                           "on_target": False}},
    connect=["soulstorm"],
    source="CoA: 'Your successful parries and dodges increase all healing "
           "you receive by 2% and reduce all Magic damage taken by -2% for "
           "10 seconds, stacking 5 times.' PORTS ALMOST VERBATIM. on_avoid "
           "covers parries and dodges together, and CoA's 5 stacks are kept "
           "and genuinely stack (nothing can READ the count, but the effect "
           "does accumulate). 10 sec -> 3 turns, values raised slightly "
           "since the window is shorter. BOTH KEYS IN THIS DICT ARE "
           "PERCENTAGE POINTS because this is a STATUS EFFECT: "
           "healing_taken_pct is divided by 100 at character.py:2904 and "
           "magic_damage_taken_pct at character.py:2762 - whereas as TALENT "
           "effects both are fractions, and a positive "
           "magic_damage_taken_pct in a status effect INCREASES damage "
           "taken, hence the negative. Authoring 0.04 and -0.03 here would "
           "have delivered 0.04% and -0.03%, i.e. nothing. Asserted in "
           "main(). Was a pure scalar on our side."))

N.append(node(
    "well_of_souls", "Well of Souls",
    "Your attacks have a 35% chance to reduce the cooldown of Spectral "
    "Scythe by 2 turns.",
    3, 4,
    proc={"trigger": "on_weapon_swing", "chance": 35, "icd": 1,
          "reset_cooldown": {"abilities": ["reaper_spectral_scythe"],
                             "turns": 2}},
    connect=["soulstorm"],
    source="CoA: 'Damage dealt by Soul Strike and Murder now reduces the "
           "cooldown of Spectral Scythe by -1 sec.' PORTS ALMOST EXACTLY; "
           "only the two-ability scoping goes. Folded in CoA's Warden of "
           "the Lost, which does the same thing but keyed on damage dealt "
           "BY the pets - " + NO_PET_PROCS + " 1 sec -> 2 turns. Was a pure "
           "scalar on our side."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "spectral_warden", "Spectral Warden",
    "Teaches Spectral Warden, a guardian summoned out of the souls you "
    "have taken.",
    4, -2,
    effects={"unlock_ability": "reaper_spectral_warden"},
    connect=["spirit_army"],
    source="CoA: 'Summon a spectral guardian to fight along side you for 20 "
           "sec and apply an absorption shield to up to 8 allies within 20 "
           "yds, absorbing 199 + Sta*1.5 damage. Threat generated by the "
           "Spectral Warden is redirected to the Reaper.' LOAD-BEARING "
           "UNLOCK - reaper_spectral_warden carries requires_talent and "
           "this is its only unlock node. The summon is real: it is an "
           "effect_type summon_pet ability with a spectral_warden template. "
           "The party absorption shield cannot come from here - a talent "
           "cannot reach an ally and there is no party-wide absorb key - "
           "and threat redirection has no mechanism. CoA's Life Tap "
           "(cooldown -60 sec, heals for 200% of pet damage) is dropped for "
           "the second clause: " + NO_PET_PROCS))

N.append(node(
    "soulstorm", "Soulstorm",
    "Your attacks have a 40% chance to refund 15 souls.",
    4, 2,
    proc={"trigger": "on_weapon_swing", "chance": 40, "icd": 0,
          "grant_resource": {"resource": "souls", "amount": 15}},
    connect=["final_requiem"],
    source="CoA: 'Requiem and Soulrend now have a 40% chance to refund a "
           "Reaped Soul.' PORTS ALMOST EXACTLY, chance included; only the "
           "two-ability scoping goes. 15 souls matches what Requiem itself "
           "generates. Stacks with Soul Slip for a tank who is both "
           "swinging and being hit, which is CoA's design for this spec - "
           "the two together fund Spectral Scythe's 35-soul cost about "
           "every other turn. Folded in CoA's Fatesealer and Spirit "
           "Culling's second clause, both of which trigger on generating a "
           "soul: " + NO_GAIN_TRIGGER))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "spirit_army", "Spirit Army",
    "Increases your pets' damage by 40% and their health by 30%.",
    5, -1,
    effects={"pet_damage": 0.40, "pet_health": 0.30},
    connect=["eater_of_souls"],
    source="CoA: 'Your Spectral Warden now causes you to summon 2 "
           "additional Spectral Wardens, but their duration is reduced by "
           "-8 sec. In addition, increases the amount absorbed by the "
           "shield granted by Spectral Warden by 100%.' Nothing changes how "
           "many pets an ability summons, and the shield is the party "
           "absorb that cannot exist, so the node is rebuilt as straight "
           "pet scaling - which is the same intent (your summons are "
           "stronger) through the only keys that reach them. THESE KEYS ARE "
           "LEGAL HERE and would have been silent dead data on most "
           "classes: Reaper genuinely summons, via spectral_scythe (35 "
           "souls) and spectral_warden. tools/qa_pet_keys.py exists because "
           "Witch Doctor Shadow Hunting shipped three pet keys on a class "
           "that summons nothing. Both FRACTIONS."))

N.append(node(
    "final_requiem", "Final Requiem",
    "Increases your damage against enemies below 35% health by 20%.",
    5, 1,
    effects={"low_health_damage_pct": 0.20},
    connect=["eater_of_souls"],
    source="CoA over 2 ranks: 'Increases your critical strike chance with "
           "abilities that deal Shadow damage by 15% against enemies below "
           "20% health.' There is no conditional CRIT key, only conditional "
           "damage, and no per-school crit filter, so both qualifiers "
           "collapse into low_health_damage_pct - the key added on 6 Nov "
           "2026 because 48 talents across 18 of the 21 classes are worded "
           "this way. CoA'S 20% THRESHOLD IS DELIBERATELY NOT HONOURED and "
           "this node does NOT set low_health_threshold_pct: that key SUMS "
           "across talents, it is UNSCALED so rank does not divide it, and "
           "a character can spend in several trees of their class. "
           "Harvest's Executioner sets 0.35 for all of Reaper; a second "
           "setter here would give a Reaper who spends in both a 55% "
           "window. Tinker once shipped two summing to 0.8. main() asserts "
           "no node here sets it, and tools/qa_summing_thresholds.py "
           "enforces the one-per-class rule everywhere."))

N.append(node(
    "intimidating_presence", "Intimidating Presence",
    "Your attacks have a 30% chance to leave the target taking 10% more "
    "damage from you for 3 turns.",
    5, 3,
    proc={"trigger": "on_weapon_swing", "chance": 30, "icd": 0,
          "apply_effect": {"effect_id": "intimidating_presence",
                           "name": "Intimidating Presence",
                           "effect_type": "debuff", "duration": 3,
                           "stat_mods": {"damage_taken_pct": 0.10},
                           "dispel_type": None, "on_target": True}},
    connect=["eater_of_souls"],
    source="CoA: 'Bolstered Form now increases the damage nearby enemies "
           "take from you by 15% for 15 seconds.' The debuff ports; its "
           "trigger does not, since nothing reads whether Bolstered Form is "
           "active and there is no per-ability proc trigger, so it fires "
           "off swings instead. 15 sec -> 3 turns, 15% -> 10% because it is "
           "now unconditional. CAREFUL: bare damage_taken_pct is read RAW "
           "ON BOTH SIDES, so 0.10 is 10% and authoring 10 would be +1000% "
           "damage taken. Asserted in main(). Was a pure scalar on our "
           "side."))

N.append(node(
    "spectral_scythe", "Spectral Scythe",
    "Reduces the soul cost of Spectral Scythe by 25% and increases your "
    "pets' armor by 30%.",
    1, -3,
    effects={"ability_reaper_spectral_scythe_cost_pct": 0.25,
             "pet_armor": 0.30},
    connect=["empyrean_fortitude"],
    source="CoA: 'Summons 1 Spectral Scythe for each Reaped Soul active "
           "which attack a nearby enemy for 20 seconds. Striking enemies "
           "with Soul Strike causes the Spectral Scythe to attack that "
           "enemy and 5 nearby enemies. Consumes Reaped Souls and Soul "
           "Infusion.' Nothing changes how many pets an ability summons and "
           "nothing reads a live soul count, so the per-soul scaling is "
           "out; " + NO_PET_PROCS + " What IS real is the cost: our "
           "Spectral Scythe is resource_type SOULS at 35, so CoA's "
           "'consumes Reaped Souls' is literally true and a cost reduction "
           "is the honest way to express 'you get more of them'. *_cost_pct "
           "is a FRACTION where POSITIVE MEANS A REDUCTION; pet_armor is a "
           "fraction too."))

N.append(node(
    "dark_soul", "Dark Soul",
    "Increases your Stamina by a further 12% and your armor penetration by "
    "60.",
    2, 4,
    effects={"stamina_pct": 12, "armor_penetration": 60},
    connect=["well_of_souls"],
    source="CoA level 40 passive: 'Increases your Stamina equal to your "
           "Armor penetration rating.' NOT BUILDABLE AS A CONVERSION, in "
           "both directions: stamina is not in STAT_CONVERSION_TARGETS (nor "
           "is hit_rating - between them those two absences have cost eight "
           "nodes half their text across seven classes), and "
           "armor_penetration is not in STAT_CONVERSION_SOURCES either, so "
           "there is no legal pairing available. Built as both halves flat, "
           "stacking with Behemoth, which is the same net effect CoA is "
           "reaching for on a Stamina tank. stamina_pct is PERCENTAGE "
           "POINTS; armor_penetration is a FLAT RATING."))

N.append(node(
    "essence_binder", "Essence Binder",
    "Your attacks have a 30% chance to steal the target's strength for 3 "
    "turns, weakening them while you strike harder.",
    3, -4,
    proc={"trigger": "on_weapon_swing", "chance": 30, "icd": 1,
          "apply_effect": {"effect_id": "essence_binder",
                           "name": "Essence Binder",
                           "effect_type": "debuff", "duration": 3,
                           "stat_mods": {"attack_power": -90},
                           "dispel_type": "magic", "on_target": True}},
    connect=["ethereal_guard"],
    source="CoA: 'Soul Strike now steals some of the target's health and "
           "Strength for 12 seconds, granting it to you at increased "
           "value.' THERE IS NO STAT THEFT MECHANIC - a debuff cannot move "
           "a stat to the caster, and no payload reads a target's stats at "
           "all - so only the target's half is built: a flat attack power "
           "reduction, which is what losing Strength means for a monster. "
           "attack_power is one of only eight status stat_mods a monster "
           "reads and it is FLAT (Monster.ability_power_bonus: 'Flat "
           "damage/healing swing from active buffs and debuffs'). The "
           "description says 'while you strike harder' because the tree's "
           "own Jailer's Will supplies that half through a real Strength "
           "conversion; this node does not claim it mechanically. 12 sec -> "
           "3 turns."))

N.append(node(
    "spirit_realm", "Spirit Realm",
    "Increases the healing of Deathwind by 30% and all healing you receive "
    "by 6%.",
    4, 4,
    effects={"ability_reaper_deathwind_healing": 0.30,
             "healing_taken_pct": 0.06},
    connect=["final_requiem"],
    source="CoA: 'Your Deathwind now also increases your healing taken by "
           "10% while you stand within its radius.' The radius condition "
           "has no positioning to stand on, so the healing-taken bonus is "
           "unconditional at 6% instead of 10%. The Deathwind half uses "
           "ability_<id>_HEALING because Deathwind is a HOT - using _damage "
           "would be silent on a heal. CAREFUL: healing_taken_pct as a "
           "TALENT effect is a FRACTION, which is why this is 0.06 - inside "
           "a STATUS EFFECT the same key is percentage points, as it is on "
           "Soul Knight two tiers up, where it is written as 4. The same "
           "key, both conventions, in one tree. Also folded in CoA's Eater "
           "of Souls clause 'the healing done by Deathwind is increased by "
           "10%', since the capstone could not carry it."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "eater_of_souls", "Eater of Souls",
    "Teaches Eater of Souls. Avoiding an attack also mends you, and your "
    "pets strike 25% harder.",
    6, 0,
    effects={"unlock_ability": "reaper_eater_of_souls",
             "pet_damage": 0.25},
    proc={"trigger": "on_avoid", "chance": 100, "icd": 0,
          "heal_flat": 70},
    source="CoA: 'Reaching 3 Reaped Souls now reduces your Physical damage "
           "taken by 10% and you regain 1% of your maximum health every 2 "
           "sec for 10 sec. This will not trigger while already active. In "
           "addition, the healing done by Deathwind is increased by 10%.' "
           "LOAD-BEARING UNLOCK - reaper_eater_of_souls carries "
           "requires_talent and this is its only unlock node, and the "
           "ability already carries CoA's -10% physical damage taken plus "
           "its own proc. The 'reaching 3 souls' trigger cannot be built: "
           + NO_GAIN_TRIGGER + " So the capstone pays out on avoidance "
           "instead, which is what this whole tree is built on - Empyrean "
           "Fortitude, Soul Slip and Soul Knight all key off the same "
           "event, and a tank who parries now heals, banks souls and stacks "
           "mitigation from one roll. heal_flat RATHER THAN leech_pct IS "
           "THE WHOLE POINT: an avoided attack deals ZERO damage, so an "
           "amount-reading payload would heal nothing while looking "
           "correct. Asserted in main(). The pet scaling stacks with Spirit "
           "Army to 65%, which is where CoA's extra Wardens land."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. tools/talent_ranks.spread() rescales so a
# ranked node lands on exactly the ceiling it had at one rank, refuses
# nodes carrying small integer durations and unlock_ability nodes, and
# since 6 Nov 2026 leaves UNSCALED_EFFECT_KEYS alone.
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

    setters = [n["talent_id"] for n in TREE["nodes"]
               if "low_health_threshold_pct" in (n.get("effects") or {})]
    assert not setters, (
        f"Reaper Harvest's Executioner already sets low_health_threshold_pct "
        f"for this class, and the key SUMS across talents - a second setter "
        f"gives a Reaper spending in both trees a 55% execute window. "
        f"Found {setters}")

    AVOIDANCE = ("on_avoid", "on_parry", "on_dodge", "on_block")
    for n in TREE["nodes"]:
        proc = n.get("proc") or {}
        # THE TRAP THIS WHOLE TREE SITS ON: an avoided attack deals ZERO
        # damage, so any payload that reads the triggering amount yields
        # nothing while looking perfectly correct in the data.
        if proc.get("trigger") in AVOIDANCE:
            for payload in ("leech_pct", "bonus_pct", "smart_heal_pct"):
                assert payload not in proc, (
                    f"{n['talent_id']} uses {payload} on "
                    f"{proc['trigger']} - an avoided attack deals 0 damage, "
                    f"so it silently heals/adds nothing. Use heal_flat, "
                    f"damage_flat, grant_resource or apply_effect")
        mods = (proc.get("apply_effect") or {}).get("stat_mods") or {}
        if "damage_taken_pct" in mods:
            assert -1 < mods["damage_taken_pct"] < 1, (
                f"{n['talent_id']} damage_taken_pct={mods['damage_taken_pct']}"
                f" - read RAW on both sides, so 10 means +1000%")
        # Inside a STATUS EFFECT these two are PERCENTAGE POINTS, where as
        # talent effects they are fractions. 0.04 would deliver 0.04%.
        for key in ("healing_taken_pct", "magic_damage_taken_pct",
                    "physical_damage_taken_pct"):
            if key in mods:
                assert abs(mods[key]) >= 1, (
                    f"{n['talent_id']} {key}={mods[key]} inside a status "
                    f"effect, where the key is PERCENTAGE POINTS - a "
                    f"fraction here delivers a hundredth of the intent")

    # pet_damage/pet_health/pet_armor are only meaningful on a class that
    # summons. Reaper does, via two summon_pet abilities - assert it rather
    # than trusting the memory of it.
    pet_nodes = [n["talent_id"] for n in TREE["nodes"]
                 if any(k.startswith("pet_") for k in (n.get("effects") or {}))]
    if pet_nodes:
        reaper = json.loads(
            (ROOT / "data/abilities/reaper.json").read_text(encoding="utf-8"))["abilities"]
        summons = [a["ability_id"] for a in reaper
                   if a.get("effect_type") == "summon_pet"]
        assert summons, (
            f"{pet_nodes} author pet keys but Reaper summons nothing - "
            f"those keys would be silent dead data, which is exactly what "
            f"tools/qa_pet_keys.py exists to catch")

    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Reaper Domination: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points, {len(GATED)} load-bearing unlocks")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
