#!/usr/bin/env python3
"""Rebuild Witch Doctor's Shadow Hunting tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_witch_doctor_shadowhunting.py [--check]

SOURCE: data/reference/coa_worksheets/witch-doctor.md and
data/reference/coa/witch-doctor.json - 40 real Shadow Hunting talents from
Ascension's own CoA Builder payload. Role: DPS.
coa_playstyles.json: "Predominantly Marksmanship Hunter, with minor Shaman
and Warlock touches".

The shipped tree was 23 nodes with THREE procs and most of the rest bare
numbers.

WHAT THE SPEC IS. A ranged-weapon caster. Reclamation and Malefic Arrow
are bow shots that collect Spirits; Spirit Glaive and Spirit Eclipse spend
them; Serpent Wards do the rest of the work.

SEN'JIN'S APPRENTICE PORTS WHOLE - all three conversions. ranged_ap is in
STAT_CONVERSION_TARGETS and both intellect and agility are in
STAT_CONVERSION_SOURCES, so CoA's level 40 passive is real in full. With
Voodoo Power (Spirit to spell damage) and Spirit Healer (Spirit to healing
power), all three Witch Doctor specs now hang off a real conversion node,
which is what CoA built them around.

THE SERPENT WARD WALL, and it is total. Five CoA talents here buff Serpent
Wards: Voodoo Fire, Berserking, Viper Ward, Spirit Striker and Serpent
Handler. Pets in this engine scale off exactly three keys - pet_damage,
pet_health, pet_armor - and PETS NEVER FIRE PROCS; there is no
fire_proc_trigger anywhere in entities/pet.py. Ward haste does not exist
either (pet_haste is read by nothing).

Worse: THE WITCH DOCTOR HAS NO PETS AT ALL. Nothing in
data/abilities/witch_doctor.json summons one, and Call of Sseratus -
CoA's "summon 4 Serpent Wards near you" - was already translated by an
earlier pass into an enemy_aoe spell_dot, pulsing wards rendered as an
area spell. So the three pet keys are DEAD DATA on this class: live
engine keys with nothing to apply them to, invisible to audit_talents
because the keys are genuinely read elsewhere (five Hunter and Warlock
talents). My first draft of this tree put pet_damage, pet_health and
pet_armor on three nodes, which would have done nothing whatsoever while
passing every check. All three are re-pointed at the abilities Frontier
actually has, and tools/qa_pet_keys.py now checks this across every
class.

NO PER-SCHOOL DAMAGE KEY EXISTS. Only all_damage, spell_damage,
physical_damage, dot_damage, aoe_damage and splash_damage are read;
nature_damage, shadow_damage and magic_damage are read by nothing, and
ranged_damage is an ability EFFECT TYPE (combat/abilities.py:1006), not a
bonus key. So every "increases your Nature and Shadow damage" talent
lands on all_damage or spell_damage, stated per node.

CONVENTIONS, which do not agree with each other:
  agility_pct, intellect_pct, spirit_pct      percentage POINTS
  all_damage, spell_damage, physical_damage,
    dot_damage, ability_*_damage              FRACTION
  crit_chance_physical, haste, hit_rating,
    ability_*_crit                            PERCENT
  crit_damage_physical, ability_*_crit_damage FRACTION
  attack_power_pct                            percentage POINTS
  healing_taken_pct / damage_taken_pct / damage_dealt_pct
    inside a status effect                    POINTS, except bare
                                              damage_taken_pct read RAW
  splash_damage, leech_pct                    FRACTION
  *_cost_pct / *_cooldown_pct   FRACTION, POSITIVE MEANS A REDUCTION
  <target>_from_<source>_pct    FRACTION, listed pairs only

TURN-BASED CUTS. Stealth and movement speed (Shadowstalker), every cast
time, every yard, and the "every 1 sec while X is active" cooldown drains
(Vol'jin's Blessing, Residual Energy) - there is no periodic trigger.
Silence has no key at all, which takes Spirit Shock's whole mechanic.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/witch_doctor_shadowhunting.json"

#: The spec's bow shots.
SHOTS = ["witch_doctor_reclamation", "witch_doctor_malefic_arrow"]

#: The Spirit spenders.
SPENDERS = ["witch_doctor_spirit_glaive", "witch_doctor_spirit_eclipse"]

#: CoA's Spirit, as on the Voodoo tree: a stacking self buff. The health
#: and mana regeneration is not buildable (no per-turn regeneration key),
#: so the stat half carries it.
SPIRIT = {
    "effect_id": "witch_doctor_spirit", "name": "Spirit",
    "effect_type": "buff", "duration": 4, "max_stacks": 5,
    "stat_mods": {"spirit_pct": 2.0},
    "on_target": False, "real_time_seconds": None,
}

TREE = {
    "spec_name": "Witch Doctor Shadowhunting",
    "tree_id": "witch_doctor_shadowhunting",
    "description": ("Bow, glaive and serpent - a ranged hunter who turns "
                    "Intellect into attack power and spends Spirits."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from the 40 real CoA Shadow Hunting talents "
        "(role DPS, 'Predominantly Marksmanship Hunter, with minor Shaman "
        "and Warlock touches'). Replaces a 23-node tree with 3 procs. "
        "Sen'jin's Apprentice ports whole - all three conversions are legal "
        "pairs. Five talents buff Serpent Wards and hit the pet wall: pets "
        "scale off pet_damage/pet_health/pet_armor only and NEVER fire "
        "procs, so Ward proc chances and Ward haste cannot exist. No "
        "per-school damage key is read by anything, so Nature and Shadow "
        "bonuses land on all_damage or spell_damage."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"witch_doctor_shadowhunting_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"witch_doctor_shadowhunting_{c}"
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
    "senjins_apprentice", "Sen'jin's Apprentice",
    "Increases your ranged attack power by 100% of your Intellect, and your "
    "ranged attack power and spell power by 25% of your Agility.",
    0, -5,
    effects={"ranged_ap_from_intellect_pct": 1.00,
             "ranged_ap_from_agility_pct": 0.25,
             "spell_power_from_agility_pct": 0.25},
    connect=["loas_strength"],
    source="CoA verbatim: 'Level 40 Passive. Increases your ranged attack "
           "power by 100% of your Intellect and your ranged attack power and "
           "spell power by 25% of your Agility.' PORTS WHOLE - all three "
           "conversions are legal: ranged_ap and spell_power are both in "
           "STAT_CONVERSION_TARGETS, intellect and agility both in "
           "STAT_CONVERSION_SOURCES. This is what makes the spec coherent - "
           "a bow user who gears Intellect. All FRACTIONS."))

N.append(node(
    "loas_strength", "Loa's Strength",
    "Increases your Agility by 6% and all damage you deal by 6%.",
    0, -3,
    effects={"agility_pct": 6.0, "all_damage": 0.06},
    connect=["village_wisdom"],
    source="CoA over 2 ranks: 'Increases your Agility and your Nature and "
           "Shadow damage dealt by 3%.' Doubled for the two ranks and "
           "authored as the full-investment ceiling. THERE IS NO PER-SCHOOL "
           "DAMAGE KEY - nature_damage, shadow_damage and magic_damage are "
           "read by nothing, and ranged_damage is an ability effect type, "
           "not a bonus - so it lands on all_damage. That is broader than "
           "CoA's, which is noted rather than hidden; this spec deals "
           "almost nothing outside those two schools anyway. agility_pct "
           "takes percentage POINTS, all_damage a FRACTION."))

N.append(node(
    "village_wisdom", "Village Wisdom",
    "Increases your chance to hit by 5% and the damage of Reclamation by "
    "15%.",
    0, -1,
    effects={"hit_rating": 5.0,
             "ability_witch_doctor_reclamation_damage": 0.15},
    connect=["improved_malefic_arrow"],
    source="CoA verbatim. Both halves live and Reclamation is a real "
           "Frontier ability - the spec's Spirit-collecting shot. hit_rating "
           "is a PERCENT; note it works as a flat stat here even though it "
           "is NOT a valid conversion target, which is what killed the "
           "spell-hit half of Voodoo Power on the DPS tree."))

N.append(node(
    "improved_malefic_arrow", "Improved Malefic Arrow",
    "Reduces the cooldown of Malefic Arrow by 20%.",
    0, 1,
    effects={"ability_witch_doctor_malefic_arrow_cooldown_pct": 0.20},
    connect=["shadow_enchantments"],
    source="CoA over 2 ranks: 'Reduces the cooldown of Malefic Arrow by -2 "
           "sec.' Expressed as a percentage because a flat second is below a "
           "turn; 20% is the two ranks' worth against the ability's own "
           "cooldown. POSITIVE reduces, so CoA's minus sign is dropped - "
           "authoring -0.20 would have LENGTHENED the cooldown."))

N.append(node(
    "shadow_enchantments", "Shadow Enchantments",
    "Increases the duration of your Jinxes by 1 turn and the damage of Hex "
    "of Malice by 50%.",
    0, 3,
    effects={"ability_witch_doctor_shrinking_jinx_duration": 1,
             "ability_witch_doctor_lethargy_jinx_duration": 1,
             "ability_witch_doctor_malignant_jinx_duration": 1,
             "ability_witch_doctor_hex_of_malice_damage": 0.50},
    connect=["hex_of_death"],
    source="CoA over 2 ranks: 'Increases the duration and effectiveness of "
           "your Jinxes by 25%.' All three Jinxes written out because no key "
           "names a group. 'Effectiveness' has no key for a Jinx - they are "
           "control, not damage - so the 25% over two ranks is paid on Hex of "
           "Malice, the curse this spec actually scales. The small integer "
           "durations keep this node out of the rank policy's reach."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "soul_feeder", "Soul Feeder",
    "Increases the damage of Malefic Arrow by 25%.",
    1, -4,
    effects={"ability_witch_doctor_malefic_arrow_damage": 0.25},
    connect=["spirit_hunting"],
    source="CoA verbatim: 'Increases the damage dealt by Malefic Arrow by 5% "
           "for each active Spirit on you.' NOTHING READS ANOTHER EFFECT'S "
           "STACK COUNT - the same wall as Voodoo's Loa Spirits and Soul "
           "Marionette, Geomancy's Earthshaping and Bloodmage's Thirst. Five "
           "Spirits at 5% is 25%, granted flat, which loses the build-up but "
           "lands on the same ceiling a Spirit-capped Witch Doctor would "
           "have had."))

N.append(node(
    "spiritual_devotee", "Spiritual Devotee",
    "Reclamation restores 30 mana.",
    1, -2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_doctor_reclamation"],
          "grant_resource": {"resource": "mana", "amount": 30}},
    connect=["spirit_hunting"],
    source="CoA verbatim: 'Collecting a Spirit now instantly restores 3% of "
           "your maximum mana.' No trigger fires when an effect is applied, "
           "so it hangs off Reclamation instead - the ability whose whole "
           "purpose is collecting a Spirit, so the two fire together in "
           "practice. GRANT_RESOURCE TAKES A FLAT `amount` ONLY "
           "(status_effects.py:1337) - there is no percentage-of-maximum "
           "form, and my first draft used an invented `pct_max` field, which "
           "would have been read as amount=0 and granted NOTHING while "
           "passing every check. So CoA's 3% cannot scale with level: 30 is "
           "roughly 3% of a level-40 Witch Doctor's mana and nearer 2% at "
           "60. Verified gain_resource('mana', n) works at runtime."))

N.append(node(
    "umbral_glaive", "Umbral Glaive",
    "Increases the damage of Spirit Glaive by 20%.",
    1, 0,
    effects={"ability_witch_doctor_spirit_glaive_damage": 0.20},
    connect=["eye_of_kimbul"],
    source="CoA's own description for this node is the unresolved token "
           "'$42' - the Builder payload never expands it, so there is no "
           "verbatim text to port and this is NOT a faithful copy. Named for "
           "Spirit Glaive and built as its damage, which is what every other "
           "Glaive talent in the tree does. Flagged so a later pass can "
           "correct it if the real text surfaces. Same situation as "
           "Brewing's Mixologist ('$40') and Spirit Volley ('$44') below."))

N.append(node(
    "serpents_guile", "Serpent's Guile",
    "Malefic Arrow leaves venom in the wound, dealing nature damage over 2 "
    "turns.",
    1, 2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_doctor_malefic_arrow"],
          "apply_effect": {"effect_id": "witch_doctor_serpents_guile",
                           "name": "Serpent's Guile", "effect_type": "dot",
                           "duration": 2, "potency": 32,
                           "damage_school": "nature", "on_target": True}},
    connect=["eye_of_kimbul"],
    source="CoA verbatim: 'Your Malefic Arrow now deals an additional 15% of "
           "its damage dealt every 1 sec for 4 seconds as Nature damage.' A "
           "repeated strike over 4 sec IS a dot, so this ports closely. The "
           "dot's potency is flat rather than a percentage of the hit, "
           "because an apply_effect payload cannot read the triggering "
           "ability's damage."))

N.append(node(
    "hex_of_death", "Hex of Death",
    "Malefic Arrow curses the target, reducing the healing they receive by "
    "20% for 3 turns, stacking twice.",
    1, 4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_doctor_malefic_arrow"],
          "apply_effect": {"effect_id": "witch_doctor_hex_of_death",
                           "name": "Hex of Death", "effect_type": "debuff",
                           "duration": 3, "max_stacks": 2,
                           "stat_mods": {"healing_taken_pct": -20.0},
                           "on_target": True}},
    connect=["darkspear_traditionalist"],
    source="CoA verbatim: 'Damage dealt by Malefic Arrow now reduces the "
           "targets healing received by -20% for 10 seconds, stacking 2 "
           "times.' Ports exactly - CoA's 20% and 2 stacks, and 10 sec is 3 "
           "turns. INSIDE A STATUS EFFECT healing_taken_pct is percentage "
           "POINTS, so -20% is -20.0; as a TALENT effect the same key is a "
           "FRACTION, where -20.0 would have been -2000%. Both units appear "
           "in the Brewing tree on adjacent nodes."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "spirit_hunting", "Spirit Hunting",
    "Malefic Arrow has a 15% chance to collect a Spirit, each raising your "
    "Spirit by 2% for 4 turns, stacking 5 times.",
    2, -4,
    proc={"trigger": "on_damage_cast", "chance": 15, "icd": 0,
          "ability_filter": ["witch_doctor_malefic_arrow"],
          "apply_effect": dict(SPIRIT)},
    connect=["godslayer"],
    source="CoA verbatim: 'Each active Spirit gives you a 15% chance when you "
           "cast Malefic Arrow to generate an additional Spirit.' The "
           "per-Spirit scaling cannot be read (see Soul Feeder), so the 15% "
           "is flat rather than per stack. CoA's own Spirit buff - 5 stacks, "
           "12 sec - becomes 5 stacks over 4 turns carrying spirit_pct; the "
           "health and mana regeneration has no per-turn key, which is the "
           "same trim made on the Voodoo tree."))

N.append(node(
    "darkspear_traditionalist", "Darkspear Traditionalist",
    "Increases your haste by 10%, and Hex of Malice has a 20% chance to "
    "collect a Spirit.",
    2, -2,
    effects={"haste": 10.0},
    proc={"trigger": "on_damage_cast", "chance": 20, "icd": 0,
          "ability_filter": ["witch_doctor_hex_of_malice"],
          "apply_effect": dict(SPIRIT)},
    connect=["dambalas_lethality"],
    source="CoA verbatim: 'Emanate a powerful aura, granting 10% increased "
           "melee and ranged haste to party and raid members. Does not stack "
           "with similar effects. Periodic damage dealt by Hex of Malice now "
           "has a 20% chance to collect a Spirit.' The aura has no party "
           "mechanism, so the 10% lands on the Witch Doctor and the "
           "description says 'your'. Periodic damage has no trigger, so the "
           "Spirit chance fires off Hex of Malice's CAST rather than its "
           "ticks - CoA's 20% kept."))

N.append(node(
    "eye_of_kimbul", "Eye of Kimbul",
    "Your critical strikes mark the target, making it take 1% more damage "
    "per mark for 5 turns, stacking 5 times.",
    2, 0,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "witch_doctor_eye_of_kimbul",
                           "name": "Eye of Kimbul", "effect_type": "debuff",
                           "duration": 5, "max_stacks": 5,
                           "stat_mods": {"damage_taken_pct": 0.01},
                           "on_target": True}},
    connect=["bwonsamdis_edge"],
    source="CoA verbatim: 'Critical strikes now apply Eye of Kimbul to "
           "enemies for 15 sec. Increases damage dealt and critical strike "
           "chance against this target by 1%, stacking 5 times. While "
           "affected, enemies cannot stealth or turn invisible.' CoA's 1% and "
           "5 stacks kept, 15 sec is 5 turns. BARE damage_taken_pct IS READ "
           "RAW, so 1% is 0.01 - authoring 1.0 would be +100% damage taken "
           "per stack, 500% at cap. The 'cannot be crit against' half has no "
           "recipient-side key, and stealth is not modelled."))

N.append(node(
    "dambalas_lethality", "Dambala's Lethality",
    "Increases the damage of Shadowflare by 50%.",
    2, 2,
    effects={"ability_witch_doctor_shadowflare_damage": 0.50},
    connect=["bwonsamdis_edge"],
    source="CoA verbatim: 'After using Spirit Eclipse, the damage of your "
           "next Shadowflare within 15 seconds is increased by 50%.' No "
           "payload discounts or empowers a later specific cast, and nothing "
           "reads whether a buff is up, so the condition is dropped and "
           "CoA's 50% is permanent. Stronger than CoA's, stated rather than "
           "hidden."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "godslayer", "Godslayer",
    "Spirit Glaive carries through, splashing 45% of its damage onto up to 3 "
    "nearby enemies.",
    3, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_doctor_spirit_glaive"],
          "splash_damage": {"pct": 0.45, "max_targets": 3,
                            "school": "shadow"}},
    connect=["the_true_spirit"],
    source="CoA verbatim: 'Your Spirit Glaive now deals an additional 54 + "
           "19% shadow SP + 14% ranged AP Shadow damage to up to 5 nearby "
           "enemies at the end of its duration.' No trigger fires when an "
           "effect expires, so the extra damage lands on the cast instead of "
           "at the end of the window. max_targets 3 rather than CoA's 5, "
           "because a flat-percentage splash across five is the strongest "
           "cleave in the tree and this is only tier 3."))

N.append(node(
    "bwonsamdis_edge", "Bwonsamdi's Edge",
    "Increases the damage of Spirit Eclipse by 40%.",
    3, -2,
    effects={"ability_witch_doctor_spirit_eclipse_damage": 0.40},
    connect=["the_true_spirit"],
    source="CoA verbatim: 'Your Spirit Eclipse now deals 40% increased damage "
           "when it explodes on impact.' The on-impact explosion is not a "
           "separable component here - Spirit Eclipse is one enemy_aoe "
           "ability - so the 40% applies to the whole thing."))

N.append(node(
    "the_true_spirit", "The True Spirit",
    "Increases the damage of Spirit Glaive and Spirit Eclipse by 30%.",
    3, 0,
    effects={f"ability_{a}_damage": 0.30 for a in SPENDERS},
    connect=["residual_energy"],
    source="CoA verbatim: 'Summoning a Serpent Ward or Spirit now increases "
           "the damage of your next Spirit Glaive or Spirit Eclipse by 6% for "
           "10 sec, stacking 5 times.' Two walls at once: no trigger fires "
           "on a summon, and nothing empowers a 'next' specific cast. Five "
           "stacks of 6% is 30%, granted flat to both spenders - the same "
           "ceiling, without the ramp."))

N.append(node(
    "voodoo_fire", "Voodoo Fire",
    "Call of Sseratus splashes 35% of its damage onto up to 3 nearby "
    "enemies.",
    3, 2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_doctor_call_of_sseratus"],
          "splash_damage": {"pct": 0.35, "max_targets": 3,
                            "school": "fire"}},
    connect=["berserking"],
    source="CoA over 2 ranks: 'Your Serpent Ward's attacks now have a 20% "
           "chance to shoot Voodoo Fire, dealing Fire damage to up to 3 "
           "nearby enemies.' TWO WALLS. First, pets never fire procs - there "
           "is no fire_proc_trigger anywhere in entities/pet.py - so a Ward "
           "cannot have a proc chance at all. Second and decisive: THE WITCH "
           "DOCTOR HAS NO PETS. Nothing in data/abilities/witch_doctor.json "
           "summons one, and Call of Sseratus - CoA's 'summon 4 Serpent "
           "Wards' - was already translated by an earlier pass into an "
           "enemy_aoe spell_dot. So pet_damage/pet_health/pet_armor are DEAD "
           "DATA on this class: live engine keys with nothing to apply them "
           "to, which audit_talents cannot catch because the keys are read "
           "somewhere. My first draft used pet_damage here and on two other "
           "nodes. Rerouted to a splash off Call of Sseratus, which is the "
           "Ward ability as Frontier actually has it. CoA's 3 targets kept; "
           "its own numbers were a mangled COND/GT expression in the Builder "
           "payload and were not portable regardless."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "residual_energy", "Residual Energy",
    "Increases your spell damage by 10% and reduces the cooldown of Spirit "
    "Glaive by 20%.",
    4, -3,
    effects={"spell_damage": 0.10,
             "ability_witch_doctor_spirit_glaive_cooldown_pct": 0.20},
    connect=["a_price_to_pay"],
    source="CoA verbatim: 'At the end of Shadow Avatar's duration you become "
           "a Lesser Shadow Avatar. Increases magic damage dealt by 10% and "
           "reduces the cooldown of Spirit Glaive by 20% every 1 sec. Lasts "
           "for 8 seconds.' Three walls: no on-expiry trigger, no periodic "
           "trigger for the per-second drain, and no magic_damage key - "
           "spell_damage is the live equivalent. Both halves granted "
           "permanently at CoA's own numbers, read once rather than once a "
           "second. POSITIVE on a _cooldown_pct reduces."))

N.append(node(
    "berserking", "Berserking",
    "Your damage-over-time spells send you into a frenzy, raising your haste "
    "by 3% per stack for 5 turns, stacking 3 times.",
    4, -1,
    proc={"trigger": "on_damage_cast", "chance": 25, "icd": 0,
          "ability_filter": ["witch_doctor_hex_of_malice",
                             "witch_doctor_call_of_sseratus"],
          "apply_effect": {"effect_id": "witch_doctor_berserking",
                           "name": "Berserking", "effect_type": "buff",
                           "duration": 5, "max_stacks": 3,
                           "stat_mods": {"haste": 3.0},
                           "on_target": False}},
    connect=["a_price_to_pay"],
    source="CoA verbatim: 'Periodic damage dealt now has a 25% chance to "
           "increase the haste of your Serpent Wards by 3% for 15 sec, "
           "stacking up to 3 times.' Three walls: no periodic trigger, "
           "pet_haste is read by nothing, and the Witch Doctor has no pets "
           "at all (see Voodoo Fire). So the haste lands on the Witch Doctor "
           "and fires off the dots' casts rather than their ticks. CoA's 25% "
           "chance, 3% per stack and 3 stacks all kept; 15 sec is 5 turns."))

N.append(node(
    "strength_of_da_loa", "Strength of Da Loa",
    "Increases your attack power by 5% and your Spirit by 10%.",
    4, 1,
    effects={"attack_power_pct": 5.0, "spirit_pct": 10.0},
    connect=["voodoo_hunger"],
    source="CoA verbatim: 'Increases the attack power of party and raid "
           "members by 5%. Does not stack with similar effects. In addition, "
           "health and mana restoration provided by your Spirits now occurs "
           "-50% more often.' The aura has no mechanism, so the 5% lands on "
           "the Witch Doctor. The Spirit regeneration half cannot be made "
           "more frequent - the regeneration itself is not built (no "
           "per-turn key), so 'more often' has nothing to act on - and is "
           "paid as Spirit instead, which every Witch Doctor spec scales. "
           "Both keys take percentage POINTS."))

N.append(node(
    "hexfire_mass", "Hexfire Mass",
    "Hex of Malice has a 30% chance to call the serpents, dealing nature "
    "damage to several enemies over time.",
    4, 3,
    proc={"trigger": "on_damage_cast", "chance": 30, "icd": 3,
          "ability_filter": ["witch_doctor_hex_of_malice"],
          "cast_ability": "witch_doctor_call_of_sseratus"},
    connect=["voodoo_hunger"],
    source="CoA verbatim: 'Damage dealt by Hex of Malice now has a 30% "
           "chance to summon a Serpent Ward on top of your enemy for 10 "
           "seconds to aid you in combat. Can only occur once every 3 sec.' "
           "CoA's 30% and its one-in-three-seconds limit both port - the "
           "limit as a 1-turn internal cooldown would be too loose, so icd 3 "
           "holds it to CoA's rate. Periodic damage has no trigger, so it "
           "fires off the cast. cast_ability takes a bare ability id, and the "
           "ability must be in the caster's own book - Call of Sseratus is "
           "auto-learned at 26, not talent-gated, so it is. The description "
           "says what the ability ACTUALLY does: Frontier's Call of Sseratus "
           "is an enemy_aoe spell_dot, not a pet summon, so promising 'a "
           "Serpent Ward at your side' would have been text with nothing "
           "behind it."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "a_price_to_pay", "A Price To Pay",
    "Spirit Eclipse resets Spirit Glaive and leaves you striking 25% harder "
    "with it for 3 turns.",
    5, -3,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_doctor_spirit_eclipse"],
          "reset_cooldown": ["witch_doctor_spirit_glaive"],
          "apply_effect": {"effect_id": "witch_doctor_a_price_to_pay",
                           "name": "A Price To Pay", "effect_type": "buff",
                           "duration": 3, "max_stacks": 1,
                           "stat_mods": {"damage_dealt_pct": 25.0},
                           "on_target": False}},
    connect=["bwonsamdis_gift"],
    source="CoA verbatim: 'Casting Spirit Eclipse with 5 Spirits now resets "
           "the cooldown of Spirit Glaive and causes your next cast within 8 "
           "sec to be guaranteed to critically strike. Spirit Glaives used in "
           "this way will reduce the cooldown of Shadowstalker by 15 sec.' "
           "The 5-Spirit condition cannot be read (see Soul Feeder). A "
           "GUARANTEED CRIT HAS NO KEY - crit_chance_physical at 100 would be "
           "a permanent stat, not a one-shot - so the window pays flat damage "
           "instead. reset_cooldown as a BARE LIST means a full reset, which "
           "is CoA's. The Shadowstalker rider is dropped: that ability is "
           "stealth and movement, neither of which is modelled."))

N.append(node(
    "voodoo_hunger", "Voodoo Hunger",
    "Your shots feed the hunger, raising the damage of your next shots by 3% "
    "per stack for 3 turns, stacking 10 times.",
    5, -1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": SHOTS,
          "apply_effect": {"effect_id": "witch_doctor_voodoo_hunger",
                           "name": "Voodoo Hunger", "effect_type": "buff",
                           "duration": 3, "max_stacks": 10,
                           "stat_mods": {"damage_dealt_pct": 3.0},
                           "on_target": False}},
    connect=["bwonsamdis_gift"],
    source="CoA verbatim: 'While Shadowstalker or Mirage is active, every 0.5 "
           "sec you now gain a stack of Voodoo Hunger. Increases the damage "
           "of your next Malefic Arrow by 10%, stacking 10 times. Lasts 8 "
           "sec.' Three walls: no 'while active' gate, no periodic trigger to "
           "tick the stacks on, and no 'next cast' empowerment. Rebuilt so "
           "the shots themselves build the stacks, which is the same ramp "
           "reached by playing rather than by standing in stealth. CoA's 10 "
           "stacks kept; 10% per stack would be 100% damage, so it is priced "
           "at 3% for 30% at cap. damage_dealt_pct inside a status effect is "
           "percentage POINTS."))

N.append(node(
    "serpent_handler", "Serpent Handler",
    "Increases the damage of Call of Sseratus by 40% and the damage your "
    "damage-over-time spells deal by 15%.",
    5, 1,
    effects={"ability_witch_doctor_call_of_sseratus_damage": 0.40,
             "dot_damage": 0.15},
    connect=["bwonsamdis_gift"],
    source="CoA verbatim: 'Increases the cooldown of Call of Sseratus by 5 "
           "sec, but increases the amount of Serpent Wards summoned by it by "
           "2.' Two more Wards cannot be bought: no key changes how many "
           "targets or summons an ability has, and the Witch Doctor has no "
           "pets regardless (see Voodoo Fire). Without the upside the "
           "downside should not be charged either, so the longer cooldown is "
           "dropped too. Rerouted to the damage of the same ability plus the "
           "spec's dots, which is what two more pulsing Wards would have "
           "delivered. CoA's trade-off is lost, stated rather than hidden."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "bwonsamdis_gift", "Bwonsamdi's Gift",
    "Bwonsamdi's favour: your haste rises by 15%, Reclamation strikes 60% "
    "harder, and your shots bring Mimic Ward a turn closer to ready.",
    6, 0,
    effects={"haste": 15.0,
             "ability_witch_doctor_reclamation_damage": 0.60},
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": SHOTS,
          "reset_cooldown": {"abilities": ["witch_doctor_mimic_ward"],
                             "turns": 1}},
    source="CoA verbatim: 'While Mimic Ward is active, you now gain 15% "
           "increased ranged haste and your Reclamation transforms into "
           "Spirit Volley. Each Spirit now increases the damage of Spirit "
           "Volley by 3%. In addition, direct ranged abilty damage dealt now "
           "reduces the cooldown of Mimic Ward by -0.5 sec.' Four things "
           "fail: the 'while active' gate, transforming one ability into "
           "another, the per-Spirit scaling, and CoA's own Spirit Volley "
           "node whose description is the unresolved token '$44'. Rebuilt as "
           "the three parts that do work - CoA's 15% haste, the Reclamation "
           "empowerment that Spirit Volley was meant to be, and the Mimic "
           "Ward cooldown feed at a turn rather than half a second. Five "
           "Spirits at 3% is the 15% folded into the 60%."))


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
    print(f"Witch Doctor Shadowhunting: {len(ids)} nodes, {procs} with "
          f"procs, {pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
