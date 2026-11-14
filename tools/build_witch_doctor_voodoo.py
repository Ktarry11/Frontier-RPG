#!/usr/bin/env python3
"""Rebuild Witch Doctor's Voodoo tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_witch_doctor_voodoo.py [--check]

SOURCE: data/reference/coa/witch-doctor.json - 32 real Voodoo talents from
Ascension's own CoA Builder payload. Role: DPS.
coa_playstyles.json: "Shadow Priest + Destruction Warlock".

The shipped tree was 23 nodes with THREE procs and 19 bare numbers.

WHAT THE SPEC IS. Spirit is the stat and the resource both. CoA's Voodoo
converts Spirit into spell damage (Voodoo Power, the level 20 passive),
collects Spirits off its own damage and healing to regenerate, keeps Hex of
Malice ticking, and detonates Puppeteer's Threads.

PUPPETEER'S THREADS IS AN ACCUMULATOR, which this engine has no form of.
CoA's level 10 passive: "Damaging abilities leave Puppeteer's Threads on
enemies for 10 seconds. Damage taken from the Witch Doctor STORES 15% of
its value. When the effect ends the damage stored is dealt instantly."
Nothing here banks damage against a target and detonates it on expiry -
there is no on-expiry trigger and no accumulator field - so Threads is
built as a plain dot: the same damage, paid out over the window instead of
at the end of it. Four other talents reference Threads and each is
re-pointed, stated on its node.

SPIRITS ARE A STACKING BUFF, not a resource. CoA's Spirit "regenerates
health and mana every 4 sec for 12 sec, stacking 5 times" and five talents
collect or extend them. Built as a stacking self buff carrying spirit_pct,
which is the part that matters (Loa Spirits: "each active Spirit now
increases your Spirit by 2%"), because per-turn resource regeneration is
not a key this engine has.

CONVENTIONS, which do not agree with each other:
  spirit_pct, intellect_pct                            percentage POINTS
  shadow_spell_damage, spell_damage, dot_damage,
    ability_*_damage, ability_*_crit_damage             FRACTION
  ability_*_crit, crit_chance_spell, haste, hit_rating  PERCENT
  damage_dealt_pct / spell_damage_taken_pct
    inside a status effect                              percentage POINTS
  *_cost_pct / *_cooldown_pct      FRACTION, POSITIVE MEANS A REDUCTION
  <target>_from_<source>_pct       FRACTION, listed pairs only

TURN-BASED CUTS. Every cast time, which takes Dark Magic entirely as
written, and every yard, which takes Prolonged Malice's range half. "Ticks
-10% faster" (Voodoo Mind, Dark Loa's Blessing) has no meaning when ticks
are per-turn. Casting while moving (Puppeteer's Grasp) and rooting yourself
(Soul Marionette) are both positional.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/witch_doctor_voodoo.json"

#: The spec's direct nukes.
NUKES = ["witch_doctor_malefic_wrath", "witch_doctor_bad_juju",
         "witch_doctor_hexfire", "witch_doctor_shadowflare"]

#: Everything that damages, for Puppeteer's Threads.
DAMAGERS = NUKES + ["witch_doctor_hex_of_malice",
                    "witch_doctor_shadow_puppets"]

#: CoA's Spirit: a stacking self buff. "Each active Spirit now increases
#: your Spirit by 2%" is the half that is buildable - per-turn health and
#: mana regeneration is not a key this engine has.
SPIRIT = {
    "effect_id": "witch_doctor_spirit", "name": "Spirit",
    "effect_type": "buff", "duration": 4, "max_stacks": 5,
    "stat_mods": {"spirit_pct": 2.0},
    "on_target": False, "real_time_seconds": None,
}

TREE = {
    "spec_name": "Witch Doctor Voodoo",
    "tree_id": "witch_doctor_voodoo",
    "description": ("Hexes and effigies - turns Spirit into spell damage "
                    "and leaves threads in everything it touches."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from data/reference/coa/witch-doctor.json "
        "(32 real CoA Voodoo talents, role DPS, 'Shadow Priest + "
        "Destruction Warlock'). Replaces a 23-node tree with 3 procs and 19 "
        "bare numbers. Puppeteer's Threads is an ACCUMULATOR in CoA - it "
        "banks 15% of damage taken and detonates on expiry - and this engine "
        "has neither an accumulator nor an on-expiry trigger, so it is a "
        "plain dot paying the same damage out over the window. Spirits are "
        "a stacking self buff rather than a resource."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"witch_doctor_voodoo_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"witch_doctor_voodoo_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "voodoo_power", "Voodoo Power",
    "Increases your spell damage by 50% of your Spirit.",
    0, -5,
    effects={"spell_power_from_spirit_pct": 0.50},
    connect=["puppeteers_threads"],
    source="CoA verbatim: 'Level 20 Passive. Increases your spell damage by "
           "50% of your Spirit and your spell hit rating by 5% of your "
           "Spirit.' The hit conversion is NOT built - hit_rating is not in "
           "STAT_CONVERSION_TARGETS, so it would be skipped in silence, the "
           "fourth time this exact pairing has come up. Spell power from "
           "Spirit is the whole class fantasy: a caster that stacks the "
           "healer stat."))

N.append(node(
    "staff_of_the_coven", "Staff of the Coven",
    "Increases your Spirit by up to 24% and your chance to hit by up to 6%.",
    0, -3,
    effects={"spirit_pct": 24.0, "hit_rating": 6.0},
    connect=["puppeteers_threads"],
    source="CoA over 3 ranks: 'Increases your Spirit by 8% and your hit "
           "chance by 2%.' Authored as the full-investment ceiling at one "
           "rank and left to the rank policy. spirit_pct takes percentage "
           "POINTS; with Voodoo Power above, Spirit is this spec's damage "
           "stat, so this is a damage node wearing a healer's clothes."))

N.append(node(
    "stranglethorn_style", "Stranglethorn Style",
    "Increases your spell critical strike chance by 4% and reduces your "
    "threat generation by 20%.",
    0, -1,
    effects={"crit_chance_spell": 4.0, "threat_generation_pct": -0.20},
    connect=["loa_spirits"],
    source="CoA verbatim. Both halves live. threat_generation_pct is a "
           "FRACTION as a talent effect and NEGATIVE reduces, which is the "
           "opposite sign to the _cost_pct and _cooldown_pct family."))

N.append(node(
    "zalazanes_malice", "Zalazane's Malice",
    "Increases the damage of Hex of Malice by 15% and the duration of your "
    "Jinxes by 1 turn.",
    0, 1,
    effects={"ability_witch_doctor_hex_of_malice_damage": 0.15,
             "ability_witch_doctor_shrinking_jinx_duration": 1,
             "ability_witch_doctor_lethargy_jinx_duration": 1,
             "ability_witch_doctor_malignant_jinx_duration": 1},
    connect=["ritual_hexing"],
    source="CoA verbatim: 'Increases the damage of Hex of Malice by 15% and "
           "the duration of Jinxes by 2 sec.' All three Jinxes exist in "
           "Frontier - Shrinking, Lethargy and Malignant - and are written "
           "out because no key names a group. 2 sec rounds to 1 turn. NOTE "
           "this node is deliberately outside the rank policy's reach: it "
           "carries small integer durations, which cannot be divided across "
           "ranks, so tools/talent_ranks.rankable() refuses it."))

N.append(node(
    "its_da_voodoo", "It's Da Voodoo",
    "Increases the damage of Shadowflare by 25%.",
    0, 3,
    effects={"ability_witch_doctor_shadowflare_damage": 0.25},
    connect=["hollow_spirit"],
    source="CoA verbatim. Shadowflare is the spec's enemy_aoe nuke, so this "
           "is its area damage node."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "puppeteers_threads", "Puppeteer's Threads",
    "Your damaging spells leave threads in the target, unravelling for "
    "shadow damage over 3 turns.",
    1, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": DAMAGERS,
          "apply_effect": {"effect_id": "witch_doctor_puppeteers_threads",
                           "name": "Puppeteer's Threads",
                           "effect_type": "dot", "duration": 3,
                           "potency": 26, "damage_school": "shadow",
                           "on_target": True}},
    connect=["loa_spirits"],
    source="CoA's level 10 passive and the thing four other talents read: "
           "'Damaging abilities now leave behind Puppeteer's Threads on "
           "enemies for 10 seconds. Damage taken from the Witch Doctor stores "
           "15% of its value. When the effect ends the damage stored is dealt "
           "instantly.' AN ACCUMULATOR WITH A DELAYED DETONATION, and this "
           "engine has neither half: nothing banks damage against a target, "
           "and no trigger fires when an effect expires. Built as a plain dot "
           "- the same damage, paid out across the window rather than at the "
           "end of it. The old tree had no form of this at all."))

N.append(node(
    "loa_spirits", "Loa Spirits",
    "Your damage and healing have a 15% chance to collect a Spirit, each "
    "raising your Spirit by 2% for 4 turns, stacking 5 times.",
    1, -2,
    proc={"trigger": "on_damage_or_heal_cast", "chance": 16, "icd": 0,
          "apply_effect": dict(SPIRIT)},
    connect=["hexplosion"],
    source="CoA over 2 ranks: 'Damage dealt and healing done now has a 8% "
           "chance to collect a Spirit. In addition, each active Spirit now "
           "increases your Spirit by 2%.' Doubled to 16 for the two ranks, "
           "which the rank policy then spreads over three as 5 - so 15% at "
           "full investment, and the description says 15. "
           "on_damage_or_heal_cast is the one trigger catching both halves of "
           "'damage dealt and healing done'. The Spirit's own health and mana "
           "regeneration is dropped - there is no per-turn resource "
           "regeneration key - and the stat half is what five other CoA "
           "talents here are actually for."))

N.append(node(
    "overflowing_juju", "Overflowing Juju",
    "Increases the damage of Malefic Wrath, Shadowflare and Bad Juju by 20%.",
    1, 0,
    effects={"ability_witch_doctor_malefic_wrath_damage": 0.20,
             "ability_witch_doctor_shadowflare_damage": 0.20,
             "ability_witch_doctor_bad_juju_damage": 0.20},
    connect=["ritual_hexing"],
    source="CoA: 'Increases the spell power scaling of Malefic Wrath, "
           "Shadowflare, and Bad Juju by 20%.' There is no key for how much "
           "an ability scales with spell power - the coefficients live on the "
           "abilities - so it is expressed as damage, which is what the "
           "scaling buys."))

N.append(node(
    "jindos_wrath", "Jin'do's Wrath",
    "Increases the critical strike chance of Hexfire by 25% and its critical "
    "damage by 25%.",
    1, 2,
    effects={"ability_witch_doctor_hexfire_crit": 25.0,
             "ability_witch_doctor_hexfire_crit_damage": 0.25},
    connect=["growing_malice"],
    source="CoA verbatim: 'Increases the critical strike chance and critical "
           "damage of Hexfire by 25%.' Both halves live, and note the units "
           "differ in the same effects block: ability_*_crit is a PERCENT "
           "while ability_*_crit_damage is a FRACTION."))

N.append(node(
    "hollow_spirit", "Hollow Spirit",
    "Shadowflare and Hexfire leave the target taking 3% more spell damage "
    "for 4 turns.",
    1, 4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_doctor_shadowflare",
                             "witch_doctor_hexfire"],
          "apply_effect": {"effect_id": "witch_doctor_hollow_spirit",
                           "name": "Hollow Spirit", "effect_type": "debuff",
                           "duration": 4, "max_stacks": 1,
                           "stat_mods": {"spell_damage_taken_pct": 3.0},
                           "on_target": True}},
    connect=["growing_malice"],
    source="CoA: 'Damage dealt by Shadowflare and Hexfire now increases the "
           "chance enemies are critically struck by 3% for 12 seconds.' There "
           "is no recipient-side 'chance to be crit' key - crit lives on the "
           "attacker - so this becomes spell damage taken, the live "
           "recipient-side key, which delivers what the talent is for. 12 sec "
           "is 4 turns and CoA's 3% is kept."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "ritual_hexing", "Ritual Hexing",
    "Increases the damage of Bad Juju, Malefic Wrath and Hexfire by up to "
    "20%.",
    2, -4,
    effects={"ability_witch_doctor_bad_juju_damage": 0.20,
             "ability_witch_doctor_malefic_wrath_damage": 0.20,
             "ability_witch_doctor_hexfire_damage": 0.20},
    connect=["malignant"],
    source="CoA over 2 ranks: 'Increases the damage of Bad Juju, Malefic "
           "Wrath and Hexfire by 10% against enemies affected by Hex of "
           "Malice.' No effect key reads whether the target carries a debuff, "
           "so the condition is dropped - and Hex of Malice is on everything "
           "in this spec's rotation anyway, so it was nearly always true."))

N.append(node(
    "growing_malice", "Growing Malice",
    "Increases the damage your damage-over-time spells deal by 30%.",
    2, -2,
    effects={"dot_damage": 0.30},
    connect=["malignant"],
    source="CoA: 'Each tick of Hex of Malice increases the damage of the next "
           "tick on the enemy by 3%, stacking 10 times.' A per-tick ramp needs "
           "a periodic trigger, which this engine does not have, and a dot "
           "cannot read its own previous tick. Ten stacks of 3% is 30%, "
           "granted flat - which loses CoA's build-up but lands on the same "
           "ceiling, and applies to Shadow Puppets and Puppeteer's Threads "
           "too rather than Hex of Malice alone."))

N.append(node(
    "hexplosion", "Hexplosion",
    "Your critical strikes send you into a hexplosion, increasing your haste "
    "by 20% for 2 turns.",
    2, 0,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "apply_effect": {"effect_id": "witch_doctor_hexplosion",
                           "name": "Hexplosion", "effect_type": "buff",
                           "duration": 2, "max_stacks": 1,
                           "stat_mods": {"haste": 20.0},
                           "on_target": False}},
    connect=["voodoo_unleashed"],
    source="CoA verbatim: 'Your offensive critical strikes now increase your "
           "haste by 20% for 6 sec.' Ports exactly - CoA's 20%, and 6 sec is "
           "2 turns. 1-turn internal cooldown so a crit streak does not keep "
           "it permanently up. Haste here means acting more often on the turn "
           "meter."))

N.append(node(
    "dark_magic", "Dark Magic",
    "Reduces the mana cost of Malefic Wrath and Bad Juju by 20%.",
    2, 2,
    effects={"ability_witch_doctor_malefic_wrath_cost_pct": 0.20,
             "ability_witch_doctor_bad_juju_cost_pct": 0.20},
    connect=["voodoo_unleashed"],
    source="CoA: 'Reduces the cast time of Malefic Wrath and Bad Juju by -0.5 "
           "sec.' There are no cast times here, so nothing of this talent "
           "survives as written. Rerouted to cost, which is what a shorter "
           "cast buys in practice - more casts per unit of mana. POSITIVE "
           "reduces."))

N.append(node(
    "beware_da_voodoo", "Beware Da Voodoo",
    "Increases the duration of Mimic Ward by 1 turn.",
    2, 4,
    effects={"ability_witch_doctor_mimic_ward_duration": 1},
    connect=["de_other_side"],
    source="CoA over 2 ranks: 'Increases the duration of Mimic Ward and "
           "Spirits by 4 sec.' The Spirits half would mean editing Loa "
           "Spirits' payload, which no key does. Mimic Ward is a real "
           "Frontier ability and its duration is reachable. Like Zalazane's "
           "Malice, the small integer keeps this node out of the rank "
           "policy."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "malignant", "Malignant",
    "Bad Juju and Hexfire spread the hex, splashing 40% of their damage onto "
    "up to 2 nearby enemies.",
    3, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_doctor_bad_juju",
                             "witch_doctor_hexfire"],
          "splash_damage": {"pct": 0.40, "max_targets": 2,
                            "school": "shadow"}},
    connect=["voodoo_strings"],
    source="CoA verbatim: 'Damage dealt by Bad Juju and Hexfire now spreads "
           "Hex of Malice to up to 1 nearby enemy.' Spreading a DoT to a new "
           "target is not a payload - apply_effect lands on the trigger's "
           "target, not a neighbour - so it is splash_damage, which is the "
           "honest reading of 'the hex reaches the thing next to it'. "
           "max_targets 2 rather than CoA's 1, since a splash that reaches "
           "one extra enemy is what CoA describes."))

N.append(node(
    "voodoo_strings", "Voodoo Strings",
    "Bad Juju strikes again, lashing the target for nature damage over 2 "
    "turns.",
    3, -2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_doctor_bad_juju"],
          "apply_effect": {"effect_id": "witch_doctor_voodoo_strings",
                           "name": "Voodoo Strings", "effect_type": "dot",
                           "duration": 2, "potency": 38,
                           "damage_school": "nature", "on_target": True}},
    connect=["voodoo_spirits"],
    source="CoA: 'When Bad Juju is used on enemies affected by Puppeteer's "
           "Threads, it strikes an additional time every 1 sec for 30% of the "
           "damage dealt over 3 sec as Nature damage.' The Threads condition "
           "has no key - nothing reads whether the target carries a debuff - "
           "and Threads is applied by every damaging spell anyway once tier 1 "
           "is taken, so the condition was nearly always true. A repeated "
           "strike over 3 sec IS a dot, which is what it is built as."))

N.append(node(
    "voodoo_unleashed", "Voodoo Unleashed",
    "Bad Juju brings Shadow Puppets a turn closer to ready.",
    3, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_doctor_bad_juju"],
          "reset_cooldown": {"abilities": ["witch_doctor_shadow_puppets"],
                             "turns": 1}},
    connect=["voodoo_spirits"],
    source="CoA: 'Your Mimic Wards now also cast Bad Juju and casting Bad "
           "Juju now reduces the cooldown of Shadow Puppets by 3 sec.' The "
           "first half would need a ward to cast a spell, which no payload "
           "does from a talent. The second ports: 3 sec is one turn."))

N.append(node(
    "de_other_side", "De Other Side",
    "Shadow Puppets feed you, increasing your damage by 1% per stack for 5 "
    "turns, stacking 10 times.",
    3, 2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_doctor_shadow_puppets"],
          "apply_effect": {"effect_id": "witch_doctor_de_other_side",
                           "name": "De Other Side", "effect_type": "buff",
                           "duration": 5, "max_stacks": 10,
                           "stat_mods": {"damage_dealt_pct": 1.0},
                           "on_target": False}},
    connect=["prolonged_malice"],
    source="CoA: 'Damage dealt by Shadow Puppets now increases your damage "
           "and critical strike chance by 1% for 20 sec, stacking up to 10 "
           "times. Additional procs do not refresh the duration.' CoA's 1% "
           "and 10 stacks kept; 20 sec is 5 turns. The crit half is dropped "
           "so the node is not two stats stacking ten deep. The no-refresh "
           "rule has no equivalent - re-application always refreshes here, "
           "which makes this slightly stronger than CoA's."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "voodoo_spirits", "Voodoo Spirits",
    "Hexfire snaps the threads, detonating them for 50% of its damage and "
    "collecting a Spirit.",
    4, -3,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_doctor_hexfire"],
          "splash_damage": {"pct": 0.50, "max_targets": 1,
                            "school": "shadow"},
          "apply_effect": dict(SPIRIT)},
    connect=["malicious_golems"],
    source="CoA verbatim: 'Hexfire now snaps your Puppeteer's Threads on your "
           "target, unleashing its damage on them instantly and collecting "
           "one Spirit.' This is the closest CoA gets to letting you detonate "
           "Threads on purpose, and the detonation itself is unbuildable (see "
           "the Threads node - no accumulator, no on-expiry trigger). Built "
           "as a burst of extra damage on the target plus the Spirit, which "
           "is what snapping the threads gets you. max_targets 1 so the "
           "splash lands on the primary rather than spreading."))

N.append(node(
    "prolonged_malice", "Prolonged Malice",
    "Increases the duration of Hex of Malice by 2 turns.",
    4, -1,
    effects={"ability_witch_doctor_hex_of_malice_duration": 2},
    connect=["malicious_golems"],
    source="CoA: 'Increases the duration of your Hex of Malice by 6 sec and "
           "the range of your offensive Voodoo spells by 6 yds.' Range means "
           "nothing here. 6 sec is 2 turns."))

N.append(node(
    "voice_of_bwonsamdi", "Voice of Bwonsamdi",
    "Your damage-over-time spells unleash a trapped spirit, striking for "
    "shadow damage.",
    4, 1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
          "ability_filter": ["witch_doctor_hex_of_malice",
                             "witch_doctor_shadow_puppets"],
          "damage_flat": 95, "school": "shadow"},
    connect=["dark_effigy"],
    source="CoA: '1 min cooldown. Let the spirit of Bwonsamdi possess you for "
           "20 sec. Dealing periodic damage unleashes a trapped voodoo spirit "
           "at enemies, exploding for Shadow damage.' Frontier has the ability "
           "already, so this is not its unlock. Periodic damage has no trigger "
           "here, so it fires off the dots' CASTS instead, permanently rather "
           "than in a 20-second window - with a 1-turn internal cooldown so "
           "casting both dots in one turn does not double it. Also carries "
           "CoA's The Price of Power ('Voice of Bwonsamdi now increases your "
           "Spirit by 100%'), which needs a 'while active' gate that no "
           "effect key has."))

N.append(node(
    "dark_loas_blessing", "Dark Loa's Blessing",
    "Increases all damage you deal by 3%.",
    4, 3,
    effects={"all_damage": 0.03},
    connect=["dark_effigy"],
    source="CoA: 'Increases the all damage dealt by party and raid members by "
           "3%. Does not stack with similar effects. In addition, your Shadow "
           "Puppets now deals damage -20% faster.' The raid aura has no "
           "mechanism, so the 3% lands on the Witch Doctor and the "
           "description says 'you'. 'Deals damage faster' has no meaning when "
           "ticks are per-turn."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "dark_effigy", "Dark Effigy",
    "Bad Juju and Hexfire strike two more enemies, and Shadowflare hits 50% "
    "harder.",
    5, -3,
    effects={"ability_witch_doctor_shadowflare_damage": 0.50},
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_doctor_bad_juju",
                             "witch_doctor_hexfire"],
          "splash_damage": {"pct": 0.60, "max_targets": 2,
                            "school": "shadow"}},
    connect=["soul_marionette"],
    source="CoA verbatim: 'Your Bad Juju and Hexfire now strike 2 additional "
           "nearby enemies. Shadowflare now deals 50% increased damage to "
           "enemies affected by Puppeteer's Threads.' Both halves built; the "
           "Threads condition is dropped as elsewhere. Deliberately stacks "
           "with Malignant at tier 3 rather than replacing it - CoA has both, "
           "and a Voodoo doctor who takes both gets a real cleave."))

N.append(node(
    "malicious_golems", "Malicious Golems",
    "War Golem makes you act faster, increasing your haste by 30% for 5 "
    "turns.",
    5, -1,
    proc={"trigger": "on_cast", "chance": 100, "icd": 0,
          "ability_filter": ["witch_doctor_war_golem"],
          "apply_effect": {"effect_id": "witch_doctor_malicious_golems",
                           "name": "Malicious Golems", "effect_type": "buff",
                           "duration": 5, "max_stacks": 1,
                           "stat_mods": {"haste": 30.0},
                           "on_target": False}},
    connect=["soul_marionette"],
    source="CoA: 'Summoning your War Golem now increases your spell haste by "
           "30% for 20 sec. In addition, periodic damage dealt by Hex of "
           "Malice and damage dealt by Shadow Puppets will reduce the "
           "cooldown of War Golem by 0.5 sec.' The haste half ports exactly - "
           "CoA's 30%, 20 sec is 5 turns. on_cast, because War Golem is a "
           "self buff that deals no damage, so a damage trigger would never "
           "have fired. The cooldown rider would need a second proc; half a "
           "second rounds below a turn anyway."))

N.append(node(
    "the_price_of_power", "The Price of Power",
    "Increases your Spirit by 20% and your spell damage by 10%.",
    5, 1,
    effects={"spirit_pct": 20.0, "spell_damage": 0.10},
    connect=["soul_marionette"],
    source="CoA: 'Voice of Bwonsamdi now increases your Spirit by 100%.' A "
           "'while this buff is active' gate does not exist for an effect "
           "key, and 100% Spirit permanently would be the strongest node in "
           "the game given Voodoo Power converts it to spell damage. Priced at "
           "20% plus a flat damage bonus - a fifth of CoA's number, applying "
           "always rather than in a 20-second window on a 1-minute "
           "cooldown."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "soul_marionette", "Soul Marionette",
    "Your spells pull the strings, raising your haste by 2% per stack for 4 "
    "turns, stacking 10 times - and your nukes hit 30% harder.",
    6, 0,
    effects={"ability_witch_doctor_malefic_wrath_damage": 0.30,
             "ability_witch_doctor_bad_juju_damage": 0.30},
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": NUKES,
          "apply_effect": {"effect_id": "witch_doctor_soul_marionette",
                           "name": "Soul Marionette", "effect_type": "buff",
                           "duration": 4, "max_stacks": 10,
                           "stat_mods": {"haste": 2.0},
                           "on_target": False}},
    source="CoA: '1 min cooldown. Root yourself for 8 sec and create 5 clones "
           "that channel on you, applying a stack of Soul Marionette. "
           "Increases your haste by 1% per stack. At 20 stacks, you transform "
           "into a powerful spirit, increasing the damage of Malefic Wrath and "
           "Bad Juju by 30% and guaranteeing it to critically strike for 15 "
           "sec.' Three things are unbuildable: rooting yourself is "
           "positional, the clones have no ability, and the 20-stack "
           "THRESHOLD cannot be read - nothing reads another effect's stack "
           "count, the same wall Geomancy's Earthshaping and Bloodmage's "
           "Thirst nodes hit. So the capstone grants both halves at once: the "
           "stacking haste builds off the nukes it is meant to empower, and "
           "the 30% damage is permanent. CoA's 10 stacks at 2% reaches the "
           "same ceiling as 20 at 1%."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. See tools/talent_ranks.py - it rescales so a
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
    print(f"Witch Doctor Voodoo: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
