#!/usr/bin/env python3
"""Rebuild Templar's Oathkeeper tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_templar_oathkeeper.py [--check]

SOURCE: data/reference/coa_worksheets/templar.md and
data/reference/coa/templar.json - 39 real Oathkeeper talents from
Ascension's own CoA Builder payload. Role: Tank.

The shipped tree was 23 nodes with THREE procs.

WHAT THE SPEC IS. A two-handed tank. Sacred Swing and Reckoning are the
threat strikes, Benediction the self-heal, and Oathkeeper the signature
defensive. Combo is the resource (see the Zealot builder - it is a real
primary pool with six generators).

GRACEFUL FIGHTER PORTS WHOLE - both halves, and it is the most unusual
conversion node in the audit. CoA: "Increases your parry rating by 20% of
Agility and your dodge rating by 20% of Intellect." parry AND dodge are
both in STAT_CONVERSION_TARGETS, and agility and intellect are both in
STAT_CONVERSION_SOURCES - so a tank that gears Intellect for dodge is
real, exactly as CoA wrote it.

OATHKEEPER ITSELF CANNOT BE BUILT, and three talents read it. CoA: "40%
of damage taken is now delayed and dealt to you over 8 seconds." Nothing
defers incoming damage - take_damage applies it immediately, and there is
no accumulator to hold a deferred pool. The same wall that took the Witch
Doctor's Puppeteer's Threads and Brewing's Base: Beast Blood, which is
the identical "damage taken becomes damage over time" mechanic. Sacred
Oath, Holy Books and the ability's own behaviour all go; the nodes are
re-pointed at real mitigation.

STAFFGUARD USES absorb_pct_max_health, a payload field most of this audit
has not needed: an apply_effect can carry a shield sized as a percentage
of the recipient's maximum health (status_effects.py:1479). That is the
one way to build "absorbs damage, scaling with Stamina" without reading a
stat into a payload.

THIS TREE OWNS ONE GATED ABILITY: tome_of_light at tier 6. Preserved and
asserted.

CONVENTIONS, which do not agree with each other:
  agility_pct, intellect_pct, armor_pct, attack_power_pct   POINTS
  max_health_pct as a TALENT effect: FRACTION
  healing_taken_pct as a TALENT effect: FRACTION
  dodge, parry, hit_rating, haste, expertise                PERCENT
  physical_damage_taken_pct as a TALENT effect: FRACTION, NEGATIVE
    reduces. Inside a status effect: /100 and POSITIVE increases.
  ability_*_damage, ability_*_healing                       FRACTION
  <target>_from_<source>_pct  FRACTION, listed pairs only
  *_cost_pct / *_cooldown_pct  FRACTION, POSITIVE MEANS A REDUCTION

TURN-BASED CUTS. Movement speed (Absolution, Duty Calls), "casting speed
reduced" (Way of the Monk - no caster-side speed debuff key), taunt
radius, and weapon-type requirements (CoA gates Sacred Swing and
Reckoning on two-handers; requires_weapon does not exist).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/templar_oathkeeper.json"

#: The two-handed threat strikes.
STRIKES = ["templar_sacred_swing", "templar_reckoning"]

#: The combo builders, as on the Zealot tree.
BUILDERS = ["templar_righteous_lunge", "templar_condemn",
            "templar_holy_cleave", "templar_vindication",
            "templar_sacred_swing", "templar_argent_blade"]

#: This tree's one talent-gated ability.
GATED = {"templar_tome_of_light"}

TREE = {
    "spec_name": "Templar Oathkeeper",
    "tree_id": "templar_oathkeeper",
    "description": ("Oath and warstaff - a two-handed tank who turns "
                    "Intellect into dodge."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from the 39 real CoA Oathkeeper talents (role "
        "Tank). GRACEFUL FIGHTER PORTS WHOLE and is the most unusual "
        "conversion in the audit: parry from 20% of Agility AND dodge from "
        "20% of Intellect are both legal pairs, so a tank gearing Intellect "
        "for dodge is real exactly as CoA wrote it. OATHKEEPER ITSELF cannot "
        "be built - 'damage taken is delayed and dealt over 8 seconds' needs "
        "an accumulator that does not exist, the same wall as the Witch "
        "Doctor's Puppeteer's Threads - and three talents read it. Staffguard "
        "uses absorb_pct_max_health, a payload field for a shield sized off "
        "maximum health."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"templar_oathkeeper_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"templar_oathkeeper_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "graceful_fighter", "Graceful Fighter",
    "Increases your parry chance by 20% of your Agility and your dodge "
    "chance by 20% of your Intellect.",
    0, -5,
    effects={"parry_from_agility_pct": 0.20,
             "dodge_from_intellect_pct": 0.20},
    connect=["paragon"],
    source="CoA's level 20 passive, verbatim: 'Increases your parry rating by "
           "20% of Agility and your dodge rating by 20% of Intellect.' PORTS "
           "WHOLE, and it is the most unusual conversion node in this audit: "
           "parry AND dodge are both in STAT_CONVERSION_TARGETS, and agility "
           "and intellect are both in STAT_CONVERSION_SOURCES, so CoA's "
           "cross-pairing works exactly as written. A tank that gears "
           "Intellect for dodge is a real build here. Both are FRACTIONS. "
           "Note dodge and parry are both face value since 7 Nov 2026 (no DR), "
           "so the Intellect half is worth slightly less per point."))

N.append(node(
    "paragon", "Paragon",
    "Increases your Stamina by 10% and your Agility by 10%.",
    0, -3,
    effects={"stamina_pct": 10.0, "agility_pct": 10.0},
    connect=["bells_of_light"],
    source="CoA verbatim: 'Increases your Stamina by 10, plus an additional "
           "amount equal to 10% of your Agility.' A FLAT 10 Stamina is "
           "meaningless at level 60 scale, and stamina_from_agility_pct is "
           "NOT a legal conversion - stamina is not in "
           "STAT_CONVERSION_TARGETS, which cost Witch Hunter's Black Knight "
           "the same half earlier in this audit. Built as percentage Stamina "
           "plus the Agility that Graceful Fighter above converts into parry. "
           "Both keys take percentage POINTS."))

N.append(node(
    "bells_of_light", "Bells of Light",
    "Increases your Agility, Intellect and chance to hit by 6%.",
    0, -1,
    effects={"agility_pct": 6.0, "intellect_pct": 6.0, "hit_rating": 6.0},
    connect=["graceful_oath"],
    source="CoA over 2 ranks: 'Increases your Agility, Intellect, and hit "
           "chance by 3%.' Doubled for the two ranks. All three port, and "
           "both stats feed Graceful Fighter - Agility into parry, Intellect "
           "into dodge - which is why a Templar tank wants a caster stat at "
           "all. agility_pct and intellect_pct take POINTS; hit_rating is a "
           "PERCENT."))

N.append(node(
    "graceful_oath", "Sacred Oath",
    "Reduces the physical damage you take by 8%.",
    0, 1,
    effects={"physical_damage_taken_pct": -0.08},
    connect=["grace_of_amanthul"],
    source="CoA verbatim: 'Critical strikes now remove 1 sec from the "
           "duration of Oathkeeper when used. Oathkeeper: 40% of damage taken "
           "is now delayed and dealt to you over 8 seconds.' OATHKEEPER "
           "CANNOT BE BUILT: nothing defers incoming damage - take_damage "
           "applies it immediately and there is no accumulator to hold a "
           "deferred pool - so there is no duration to shorten either. This "
           "is the same wall that took the Witch Doctor's Puppeteer's Threads "
           "and Brewing's Base: Beast Blood, which is the identical 'damage "
           "taken becomes damage over time' idea. Re-pointed at straight "
           "physical mitigation, which is what delaying 40% of a hit buys a "
           "tank. AS A TALENT EFFECT physical_damage_taken_pct is a FRACTION "
           "where NEGATIVE reduces."))

N.append(node(
    "grace_of_amanthul", "Grace of Aman'thul",
    "Reduces the cost of Righteous Lunge and Sacred Swing by 20%.",
    0, 3,
    effects={"ability_templar_righteous_lunge_damage": 0.20,
             "ability_templar_sacred_swing_damage": 0.20},
    connect=["staffguard"],
    source="CoA verbatim: 'Reduces the Energy cost of Righteous Lunge by -5 "
           "and Sacred Swing by -10.' CoA's Templar spends Energy; "
           "Frontier's spends COMBO, a real primary pool with six generators "
           "(see the Zealot builder), so there is a genuine cost to cut. The "
           "two different flat amounts become one percentage, since costs "
           "differ per rank anyway. POSITIVE reduces."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "staffguard", "Staffguard",
    "Sacred Swing raises a guard, absorbing damage equal to 8% of your "
    "maximum health for 3 turns.",
    1, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["templar_sacred_swing"],
          "apply_effect": {"effect_id": "templar_staffguard",
                           "name": "Staffguard", "effect_type": "buff",
                           "duration": 3, "max_stacks": 1,
                           "absorb_pct_max_health": 0.08,
                           "on_target": False}},
    connect=["sacred_resistance"],
    source="CoA verbatim: 'Casting Sacred Swing now grants you Staffguard, "
           "absorbing damage, scaling with Stamina, parry and dodge rating, "
           "for 8 sec.' USES absorb_pct_max_health, a payload field most of "
           "this audit has not needed: an apply_effect can carry a shield "
           "sized as a percentage of the recipient's maximum health "
           "(status_effects.py:1479). That is the one honest way to build "
           "'absorbs, scaling with Stamina' - a payload cannot read a stat, "
           "but maximum health already carries Stamina, so the scaling is "
           "real rather than faked. 8 sec is 3 turns."))

N.append(node(
    "sacred_resistance", "Sacred Resistance",
    "Reckoning hardens you, raising your armour by 15% for 5 turns.",
    1, -2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["templar_reckoning"],
          "apply_effect": {"effect_id": "templar_sacred_resistance",
                           "name": "Sacred Resistance", "effect_type": "buff",
                           "duration": 5, "max_stacks": 1,
                           "stat_mods": {"armor_pct": 15.0},
                           "on_target": False}},
    connect=["conviction"],
    source="CoA verbatim: 'Casting Reckoning now increases your Armor by 15% "
           "for 15 seconds.' PORTS EXACTLY - CoA's 15%, and 15 sec is 5 "
           "turns. armor_pct takes percentage POINTS inside a status effect "
           "as well as on a talent, so 15.0 is right on both sides."))

N.append(node(
    "conviction", "Conviction",
    "Sacred Swing quickens you, raising your haste by 5% per stack for 5 "
    "turns, stacking 4 times.",
    1, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["templar_sacred_swing"],
          "apply_effect": {"effect_id": "templar_conviction",
                           "name": "Conviction", "effect_type": "buff",
                           "duration": 5, "max_stacks": 4,
                           "stat_mods": {"haste": 5.0},
                           "on_target": False}},
    connect=["holy_warstaff"],
    source="CoA verbatim: 'Casting Sacred Swing now increases your melee "
           "haste by 5% for 15 seconds, stacking 4 times.' PORTS EXACTLY - "
           "CoA's 5% and 4 stacks, 15 sec as 5 turns. One of the cleanest "
           "nodes in the tree because it asks for nothing the engine lacks."))

N.append(node(
    "holy_warstaff", "Holy Warstaff",
    "Increases the damage of Reckoning by 20%.",
    1, 2,
    effects={"ability_templar_reckoning_damage": 0.20},
    connect=["parry_dance"],
    source="CoA verbatim: 'Increases the damage of Reckoning by 20%.' Ports "
           "exactly. CoA gates Reckoning on two-handed weapons; "
           "requires_weapon does not exist as a talent condition, so the "
           "weapon requirement lives on the ability or not at all - the same "
           "limit that made Guardian Gladiator's four Training nodes "
           "unconditional."))

N.append(node(
    "parry_dance", "Parry Dance",
    "Parrying an attack raises your parry chance by 3% per stack for 2 turns, "
    "stacking 5 times.",
    1, 4,
    proc={"trigger": "on_parry", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "templar_parry_dance",
                           "name": "Parry Dance", "effect_type": "buff",
                           "duration": 2, "max_stacks": 5,
                           "stat_mods": {"parry": 3.0},
                           "on_target": False}},
    connect=["disciplined_mind"],
    source="CoA verbatim: 'When you critically strike with auto attacks or "
           "parry an attack, your chance to parry is now increased by 3% for "
           "5 sec, stacking 5 times.' on_parry IS a live trigger (fired from "
           "Character._fire_avoidance_procs), so the parry half ports exactly "
           "- CoA's 3% and 5 stacks, 5 sec as 2 turns. The auto-attack-crit "
           "half is dropped rather than merged: two triggers would need two "
           "procs and would double-stack on a turn where both happen."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "disciplined_mind", "Disciplined Mind",
    "Increases the healing of Benediction by 30%.",
    2, -4,
    effects={"ability_templar_benediction_healing": 0.30},
    connect=["justicar_of_the_light"],
    source="CoA over 2 ranks: 'Increases the healing of Benediction by 15% "
           "and causes it to dispel 1 poison and disease effect.' Doubled for "
           "the two ranks. No key adds a dispel to an ability - dispelling is "
           "an effect_type, not a rider - so that half is dropped."))

N.append(node(
    "justicar_of_the_light", "Justicar of the Light",
    "Reduces the cooldown of Benediction by 50%.",
    2, -2,
    effects={"ability_templar_benediction_cooldown_pct": 0.50},
    connect=["guardian_of_the_light"],
    source="CoA verbatim: 'Removes the cooldown from Benediction, but "
           "increases its Energy cost by 10.' A FULL COOLDOWN REMOVAL is "
           "expressible (1.0) but would make the tank's self-heal spammable, "
           "and NO KEY ADDS A COST - _cost_pct is positive-reduces, so CoA's "
           "downside cannot be charged in either direction. Priced at half "
           "the cooldown with no penalty, which is the honest middle."))

N.append(node(
    "guardian_of_the_light", "Guardian of the Light",
    "Reduces the cost of Temple Guardian by 50%.",
    2, 0,
    effects={"ability_templar_temple_guardian_healing": 0.50},
    connect=["way_of_the_monk"],
    source="CoA verbatim: 'Casting Benediction now reduces the cost of your "
           "next Temple Guardian by -50% for 6 seconds.' Nothing discounts a "
           "named next cast, so the 50% is permanent. Temple Guardian is "
           "target_type 'party', so making it cheaper is real party value - "
           "the same reasoning as Zealot's Force of Golganneth node."))

N.append(node(
    "way_of_the_monk", "Way of the Monk",
    "Sacred Swing and Reckoning leave the enemy dealing 10% less damage for 3 "
    "turns, stacking twice.",
    2, 2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": STRIKES,
          "apply_effect": {"effect_id": "templar_way_of_the_monk",
                           "name": "Way of the Monk",
                           "effect_type": "debuff", "duration": 3,
                           "max_stacks": 2,
                           "stat_mods": {"damage_dealt_pct": -10.0},
                           "on_target": True}},
    connect=["fortified_body"],
    source="CoA verbatim: 'Damage dealt by Sacred Swing and Reckoning now "
           "reduces casting speed by 10% for 10 sec, stacking 2 times.' THERE "
           "IS NO CASTER-SIDE SPEED DEBUFF KEY - haste is attacker-side and "
           "nothing slows a target's casting - so it becomes a damage "
           "reduction, which is the mitigation a slowed caster represents to "
           "a tank. CoA's 10% and 2 stacks kept; 10 sec is 3 turns. "
           "damage_dealt_pct inside a status effect is percentage POINTS."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "fortified_body", "Fortified Body",
    "Increases your maximum health by 6% and the healing you receive by 6%.",
    3, -4,
    effects={"max_health_pct": 0.06, "healing_taken_pct": 0.06},
    connect=["call_of_the_monastery"],
    source="CoA verbatim: 'Allies within 40 yds receive 6% more healing. Does "
           "not stack with similar effects. Additionally, increases your "
           "maximum health by 6%.' A TALENT CANNOT REACH AN ALLY, so the "
           "healing-received half lands on the Templar too and the "
           "description says 'you'. BOTH KEYS ARE FRACTIONS AS TALENT EFFECTS "
           "- max_health_pct and healing_taken_pct each flip to percentage "
           "POINTS inside a status effect, which is exactly the pair that "
           "shipped 600% and 1000% on earlier trees before being caught."))

N.append(node(
    "call_of_the_monastery", "Call of the Monastery",
    "Increases your attack power by 10%.",
    3, -2,
    effects={"attack_power_pct": 10.0},
    connect=["faith_guard"],
    source="CoA verbatim: 'Increases the attack power of all party and raid "
           "members 5%. Does not stack with similar effects. In addition, "
           "increases your attack power by 5%.' A talent cannot reach an "
           "ally, so CoA's two 5% halves land on the Templar as a single "
           "10%. attack_power_pct takes percentage POINTS."))

N.append(node(
    "faith_guard", "Faith Guard",
    "Increases the damage of Chastise by 30% and the threat you\n"
    "generate by 20%.",
    3, 0,
    effects={"ability_templar_chastise_damage": 0.30,
             "threat_generation_pct": 0.20},
    connect=["disciplined_blows"],
    source="CoA verbatim: 'While a Libram is active, your Chastise will now "
           "unleash a line of holy power, dealing High Threat Holy damage.' "
           "The 'while a Libram is active' gate has no key - nothing reads "
           "whether a buff is up - and a line is positional. Built as damage "
           "plus threat on Chastise, which is what High Threat means for a "
           "tank. threat_generation_pct is a FRACTION where POSITIVE "
           "increases, the opposite polarity to the _cost_pct keys."))

N.append(node(
    "disciplined_blows", "Disciplined Blows",
    "Your heals pulse holy power, striking the enemy for holy damage.",
    3, 2,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 1,
          "damage_flat": 70, "school": "holy"},
    connect=["absolution"],
    source="CoA verbatim: 'Your healing done triggers a holy pulse around "
           "healed targets, dealing Holy damage to nearby enemies. Can only "
           "occur once every 0.5 sec.' on_heal_cast with a damage_flat "
           "payload is the right shape - a tank healing itself and damaging "
           "what it is holding. The pulse lands on the current target rather "
           "than around the healed ally, since a payload has no radius. "
           "1-turn icd covers CoA's rate limit."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "absolution", "Absolution",
    "Increases the threat you generate by 30% and your armour by 10%.",
    4, -3,
    effects={"threat_generation_pct": 0.30, "armor_pct": 10.0},
    connect=["holy_books"],
    source="CoA verbatim: 'Taunt all enemies within 8 yds for 4 sec and "
           "increase your movement speed by 50% for 4 sec.' Frontier HAS "
           "Absolution as an ability and it is not gated, so this is not its "
           "unlock. An AoE taunt is the ability's own business and movement "
           "speed is positional, so the talent is built as the threat and "
           "survivability a taunt node should carry for a tank."))

N.append(node(
    "holy_books", "Holy Books",
    "Reduces all damage you take by 7%.",
    4, -1,
    effects={"damage_taken_pct": -0.07},
    connect=["duty_calls"],
    source="CoA's level 30 passive: 'Using a Libram now removes 70% of the "
           "delayed damage from Oathkeeper.' OATHKEEPER'S DELAYED DAMAGE DOES "
           "NOT EXIST (see Sacred Oath at tier 0 - nothing defers incoming "
           "damage), so there is no pool to clear. Re-pointed at flat "
           "mitigation, which is what clearing 70% of a deferred hit "
           "amounted to. BARE damage_taken_pct IS READ RAW, so 7% is -0.07 - "
           "authoring -7.0 would be a 700% reduction, the immortality bug "
           "from Boltslinger's Evasive."))

N.append(node(
    "duty_calls", "Duty Calls",
    "Your strikes build resolve, raising your damage by 2% per stack for 5 "
    "turns, stacking 5 times.",
    4, 1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": BUILDERS,
          "apply_effect": {"effect_id": "templar_duty_calls",
                           "name": "Duty Calls", "effect_type": "buff",
                           "duration": 5, "max_stacks": 5,
                           "stat_mods": {"damage_dealt_pct": 2.0},
                           "on_target": False}},
    connect=["barrier_of_light"],
    source="CoA verbatim: 'Casting abilities that grant an Oath now increases "
           "your damage dealt and movement speed by 2% for 15 sec, stacking 5 "
           "times.' Oaths do not exist (see the Zealot builder), so it fires "
           "off the combo builders - which in CoA are the abilities that "
           "grant Oaths, so the stacks build in the same part of the "
           "rotation. Movement speed is positional. CoA's 2% and 5 stacks "
           "kept; 15 sec is 5 turns."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "barrier_of_light", "Barrier of Light",
    "Increases the healing you receive by 20% and reduces the cooldown of "
    "Barrier of Light by 30%.",
    5, -3,
    effects={"healing_taken_pct": 0.20,
             "ability_templar_barrier_of_light_cooldown_pct": 0.30},
    connect=["sacred_swing_mastery"],
    source="CoA verbatim: 'Emit saving light, increasing the healing received "
           "by nearby party and raid members by 40% for 15 sec. For the "
           "duration, threat generated by your allies is redirected to you.' "
           "Frontier HAS Barrier of Light as a target_type 'party' ability "
           "and it is not gated, so this is not its unlock - and because the "
           "ABILITY is party-targeted, its own healing bonus does reach "
           "allies. The talent's own 20% lands on the Templar (a talent "
           "cannot reach an ally) at half CoA's figure. Threat redirection "
           "has no mechanism. AS A TALENT EFFECT healing_taken_pct is a "
           "FRACTION."))

N.append(node(
    "sacred_swing_mastery", "Sacred Swing",
    "Increases the damage of Sacred Swing by 40% and the threat you\n"
    "generate by 15%.",
    5, -1,
    effects={"ability_templar_sacred_swing_damage": 0.40,
             "threat_generation_pct": 0.15},
    connect=["tome_of_light"],
    source="CoA verbatim: 'Swing at enemies in front of you, dealing 125% "
           "High Threat Weapon Damage, slowing their attack and movement "
           "speed by 20% for 10 sec. Only usable after avoiding an attack.' "
           "Frontier HAS Sacred Swing and it is not gated. The "
           "'only usable after avoiding an attack' condition lives on the "
           "ability, not here - no talent key gates usability - and attack "
           "speed has no key. Built as damage plus the High Threat the "
           "tooltip names."))

N.append(node(
    "paragon_of_light", "Paragon of Light",
    "Increases your dodge and parry chance by 4% each.",
    5, 1,
    effects={"dodge": 4.0, "parry": 4.0},
    connect=["tome_of_light"],
    source="CoA's Parry Dance and Graceful Fighter both point at avoidance, "
           "and this node carries the flat version neither does. NOT a direct "
           "port of a single CoA talent - built from the spec's avoidance "
           "theme so tier 5 has a defensive stat node rather than a third "
           "damage line, and flagged as such. Both keys are PERCENT and "
           "both now matter MORE than they did this morning: creature "
           "avoidance went in today, which means expertise exists, which "
           "means avoidance is a two-sided stat rather than player-only."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "tome_of_light", "Tome of Light",
    "Teaches Tome of Light, and reduces all damage you take by 8%.",
    6, 0,
    effects={"unlock_ability": "templar_tome_of_light",
             "damage_taken_pct": -0.08},
    source="LOAD-BEARING UNLOCK: templar_tome_of_light carries "
           "requires_talent, so without this node it is unobtainable "
           "forever. Templar has exactly three gated abilities, one per tree "
           "- Zealot's Norgannon's Wrath, Crusader's Righteous Tempest and "
           "this - and main() asserts this one. The mitigation is added "
           "because a capstone granting only an ability is thin, and a tank "
           "capstone should be defensive. BARE damage_taken_pct IS READ RAW, "
           "so 8% is -0.08; it stacks with Holy Books at tier 4 for 15% on a "
           "full Oathkeeper build."))


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
    print(f"Templar Oathkeeper: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points, {len(GATED)} load-bearing unlock")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
