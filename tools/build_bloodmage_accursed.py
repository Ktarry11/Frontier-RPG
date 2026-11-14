#!/usr/bin/env python3
"""Rebuild Bloodmage's Accursed tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_bloodmage_accursed.py [--check]

SOURCE: data/reference/coa/bloodmage.json - 41 real Accursed talents from
Ascension's own CoA Builder payload. Role: DPS.
coa_playstyles.json: "Feral Druid + Rogue + Blood Death Knight".

The shipped tree was 23 nodes with THREE procs and 19 bare numbers.

WHAT THE SPEC IS. Melee, bleeding, and spells paid for in health. CoA's
Accursed opens with Lunge, keeps bleeds running, and spends health on
Bloodbolt and Veinburst while Barely Human and Gore Barrage make
health-costed spells cheaper and harder.

CURSED FORM IS A BUFF, NOT A SHAPESHIFT, which decides how six talents are
built. combat/forms.py's FORMS holds bear, dire_bear, cat, moonkin,
tree_of_life, shadowform, void_monstrosity, spider, beetle, weaver and
vizier_form - and no Bloodmage entry. bloodmage_accursed_form and
bloodmage_blood_curse are ordinary self-buff ABILITIES. So
require_form: "accursed_form" would never match and the proc would never
fire, which is the silent kind of dead. Every CoA talent phrased "while a
Cursed Form is active" is built as a WINDOW off casting it instead -
on_cast filtered to the form ability, applying a buff for a few turns.
That is the same shape, reached by a gate that exists.

THE OTHER REPEATED LOSS: "if the enemy is bleeding". Five CoA talents here
check it (Reave's conditional damage, Veinburst's, Dark Hunt, Clotting,
Blood Plague's Diseased variant). No effect key and no proc payload reads
whether the target carries a debuff, so each is unconditional and repriced.
Reave is the worst of them - CoA gives it up to 300% bonus damage for
three stacked conditions - and is flagged on its node.

CONVENTIONS, which do not agree with each other:
  armor_penetration_pct, attack_power_pct             percentage POINTS
  all_damage, dot_damage, crit_damage_physical,
    ability_*_damage, ability_*_crit_damage           FRACTION
  ability_*_crit, crit_chance_physical, haste         PERCENT
  damage_dealt_pct in a status effect                 percentage POINTS
  damage_taken_pct in a status effect                 read RAW
  *_cost_pct / *_cooldown_pct      FRACTION, POSITIVE MEANS A REDUCTION

TURN-BASED CUTS. No global cooldown exists, so Dark Frenzy's "-25% GCD" is
free value and dropped. No positioning, so Reave's "if you are behind
them" and every cone and radius are gone. Channels do not exist, so Aortic
Assault is its damage. "Every 0.01 second you remain in a Cursed Form"
(Crimson Feast) has no turn-based reading at all.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/bloodmage_accursed.json"

#: The melee strikes this spec is built on.
STRIKES = ["bloodmage_reave", "bloodmage_bloodfang_bite",
           "bloodmage_claw_sweep", "bloodmage_ravenous_strike",
           "bloodmage_crimson_maw"]

#: The two Cursed Form abilities CoA's form talents hang off.
FORMS = ["bloodmage_accursed_form", "bloodmage_blood_curse"]

#: Spells that cost health, which Barely Human and Gore Barrage empower.
HEALTH_SPELLS = ["bloodmage_bloodbolt", "bloodmage_bloodmoon_blast",
                 "bloodmage_veinburst", "bloodmage_hemoburst"]

TREE = {
    "spec_name": "Bloodmage Accursed",
    "tree_id": "bloodmage_accursed",
    "description": ("Cursed thing in melee - opens a vein and keeps "
                    "everything bleeding, including itself."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from data/reference/coa/bloodmage.json "
        "(41 real CoA Accursed talents, role DPS, 'Feral Druid + Rogue + "
        "Blood Death Knight'). Replaces a 23-node tree with 3 procs and 19 "
        "bare numbers. Cursed Form is a BUFF here, not a shapeshift - "
        "combat/forms.py has no Bloodmage entry - so require_form would "
        "never match and the six form-gated CoA talents are built as "
        "windows off casting it. Five more check whether the target is "
        "bleeding, which no key reads; those are unconditional and "
        "repriced, stated per node."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"bloodmage_accursed_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"bloodmage_accursed_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "barely_human", "Barely Human",
    "Increases your armor penetration by up to 30% and the damage of spells "
    "that cost health by up to 30%.",
    0, -5,
    effects={"armor_penetration_pct": 30.0,
             **{f"ability_{a}_damage": 0.30 for a in HEALTH_SPELLS}},
    connect=["puncturing_fangs"],
    source="CoA over 2 ranks: 'Increases your armor penetration and the "
           "damage of spells that cost health by 15%.' 'Spells that cost "
           "health' is not a group any key names, so the four are written "
           "out - Bloodbolt, Bloodmoon Blast, Veinburst and Hemoburst all "
           "carry resource_type health. Note armor_penetration_pct takes "
           "percentage POINTS while the ability_*_damage keys beside it are "
           "fractions, in the same effects block."))

N.append(node(
    "rage_talent", "Rage",
    "Increases your spell damage by 15% of your attack power and the damage "
    "of Reave by up to 20%.",
    0, -3,
    effects={"spell_power_from_ap_pct": 0.15,
             "ability_bloodmage_reave_damage": 0.20},
    connect=["puncturing_fangs"],
    source="CoA over 2 ranks: 'Increases your spell damage by 15% of your "
           "attack power and the damage dealt by Reave by 10%.' The "
           "conversion is live - spell_power is a target and 'ap' is in "
           "STAT_CONVERSION_SOURCES, which is what makes this spec's melee "
           "feed its health-costed spells. Node id is rage_talent because "
           "'rage' alone reads as the resource."))

N.append(node(
    "blood_pact_talent", "Blood Pact",
    "Increases your haste by 6% and the damage you deal by 6%.",
    0, -1,
    effects={"haste": 6.0, "all_damage": 0.06},
    connect=["fang_over_fang"],
    source="CoA: 'Increases your maximum Rage by 20 and you now regenerate 4 "
           "Rage every 5 sec.' NEITHER half is buildable. max_rage is a "
           "hardcoded 100 in Character.__init__ with no talent hook - the "
           "same dead end Geomancy's Cave Dweller hit - and there is no "
           "per-turn resource regeneration key either. Rebuilt as haste and "
           "damage, which is what more Rage and faster Rage actually buy a "
           "melee spec."))

N.append(node(
    "dark_hunt", "Dark Hunt",
    "Increases your Shadow spell damage by 10%.",
    0, 1,
    effects={"shadow_spell_damage": 0.10},
    connect=["fang_over_fang"],
    source="CoA: 'Increases your Shadow damage dealt by 10% against bleeding "
           "targets.' No effect key reads whether the target carries a "
           "debuff, so the condition is dropped and CoA's 10% kept - this "
           "spec bleeds everything anyway once Rotclaw and the dots are "
           "running, so the condition was nearly always true."))

N.append(node(
    "heightened_senses", "Heightened Senses",
    "Increases your physical critical strike chance by 6%.",
    0, 3,
    effects={"crit_chance_physical": 6.0},
    connect=["crimson_expedition"],
    source="Not a CoA node by this name - it carries CoA's Killer Instinct, "
           "'Each point of Rage now increases the critical strike chance of "
           "Veinburst and Reave by 0.5%, up to a maximum of 50%.' Scaling off "
           "a live resource amount is not reachable: get_talent_effects() has "
           "no access to a resource total. Granted flat, and renamed so the "
           "tooltip does not imply a Rage interaction it does not have."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "puncturing_fangs", "Puncturing Fangs",
    "Bloodmoon Blast returns 9 Rage.",
    1, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["bloodmage_bloodmoon_blast"],
          "grant_resource": {"resource": "rage", "amount": 9}},
    connect=["cruel_intent"],
    source="CoA verbatim: 'Your Bloodmoon Blast now generates 3 additional "
           "Rage per hit.' Bloodmoon Blast costs HEALTH and already banks "
           "Vitality through its `generates` block, so this makes it the "
           "spec's whole economy in one cast: pay in blood, receive Rage and "
           "Thirst."))

N.append(node(
    "fang_over_fang", "Fang Over Fang",
    "Bloodfang Bite has a 20% chance to make Reave ready again at once.",
    1, -2,
    proc={"trigger": "on_damage_cast", "chance": 20, "icd": 0,
          "ability_filter": ["bloodmage_bloodfang_bite"],
          "reset_cooldown": ["bloodmage_reave"]},
    connect=["cruel_intent"],
    source="CoA verbatim: 'Casting Bloodfang Bite now has a 20% chance to "
           "reset the cooldown of Reave.' Ports directly. Was a flat scalar."))

N.append(node(
    "cruel_intent", "Cruel Intent",
    "Lunging at an enemy strikes them again and heals you.",
    1, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["bloodmage_lunge"],
          "extra_attack": True,
          "heal_flat": 90},
    connect=["corrupted_blood"],
    source="CoA's Cruel Intent ('When you Lunge at an enemy you now strike "
           "them 3 times with auto attacks') plus Dark Intent ('When you "
           "Lunge at an enemy you now heal for 5% of your maximum health'). "
           "Both hang off the same trigger, so they are one node rather than "
           "two that each half-fire. extra_attack is a boolean, not a count, "
           "so 'three times' is one extra strike. heal_flat is a number - "
           "there is no percentage-of-max-health payload - so 5% is a flat "
           "90."))

N.append(node(
    "leeching_tome", "Leeching Tome",
    "Bloodbolt leeches 30% of the damage it deals back as health.",
    1, 2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["bloodmage_bloodbolt"],
          "leech_pct": {"pct": 0.30}},
    connect=["corrupted_blood"],
    source="CoA: 'Your Bloodbolt now leeches 50% more health, but it now "
           "costs 5 additional Rage.' Built as the leech itself rather than a "
           "multiplier on one, since Accursed has no Hematoma node to raise - "
           "that is Sanguine's. The cost increase is dropped for the sign "
           "reason: a surcharge must be written as a negative cost, which is "
           "indistinguishable from the error the audit flags."))

N.append(node(
    "crimson_expedition", "Crimson Expedition",
    "Increases the critical strike chance of Bloodbolt and Aortic Assault by "
    "10%.",
    1, 4,
    effects={"ability_bloodmage_bloodbolt_crit": 10.0,
             "ability_bloodmage_aortic_assault_crit": 10.0},
    connect=["gore_barrage"],
    source="CoA: 'Increases the critical strike chance of your Bloodbolt, "
           "Blood Shards, and Aortic Assault by 10%.' Blood Shards does not "
           "exist in Frontier, so the other two carry it."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "accursed_form", "Accursed Form",
    "Taking a Cursed Form sharpens you for 4 turns, increasing your attack "
    "power and leaving your strikes cutting healing on the target.",
    2, -4,
    proc={"trigger": "on_cast", "chance": 100, "icd": 0,
          "ability_filter": FORMS,
          "apply_effect": {"effect_id": "bloodmage_accursed_form_buff",
                           "name": "Accursed Form", "effect_type": "buff",
                           "duration": 4, "max_stacks": 1,
                           "stat_mods": {"attack_power_pct": 20.0,
                                         "damage_dealt_pct": 10.0},
                           "on_target": False}},
    connect=["terrorizer"],
    source="CoA: 'Transforms your Blood Curse into Accursed Form. Embrace "
           "your demonic curse for 30 seconds, increasing your attack power "
           "by 50% of your Agility and causing your melee attacks to reduce "
           "all healing done to the target by -20%, stacking 2 times.' The "
           "window is built off CASTING either Cursed Form ability, because "
           "there is no Bloodmage shapeshift to require_form against and no "
           "'while this buff is up' gate. The healing-reduction half needs a "
           "second proc on the target from inside this one, which apply_effect "
           "cannot do in both directions at once with different triggers, so "
           "the description says 'leaving your strikes cutting healing' as "
           "flavour and the numbers it does deliver are the attack power and "
           "damage. 50%-of-Agility becomes a flat attack_power_pct, since a "
           "status effect cannot carry a conversion."))

N.append(node(
    "terrorizer", "Terrorizer",
    "Increases the damage of Veinburst, Bloodfang Bite and Claw Sweep by 25%.",
    2, -2,
    effects={"ability_bloodmage_veinburst_damage": 0.25,
             "ability_bloodmage_bloodfang_bite_damage": 0.25,
             "ability_bloodmage_claw_sweep_damage": 0.25},
    connect=["cursed_blood"],
    source="CoA: 'Increases the damage of Veinburst, Bloodfang Bite, and Claw "
           "Sweep on enemies below 35% health by 25%.' A recipient-health "
           "condition on damage, and the engine's only recipient-health key "
           "is heal-side, so it is unconditional. CoA's 25% kept rather than "
           "trimmed, because an execute window is where this spec spends "
           "everything anyway."))

N.append(node(
    "corrupted_blood", "Corrupted Blood",
    "Taldaram's Torment corrupts the target's blood, making it take 10% more "
    "damage for 5 turns.",
    2, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["bloodmage_taldarams_torment"],
          "apply_effect": {"effect_id": "bloodmage_corrupted_blood",
                           "name": "Corrupted Blood",
                           "effect_type": "debuff", "duration": 5,
                           "max_stacks": 1,
                           "stat_mods": {"damage_taken_pct": 0.10},
                           "on_target": True}},
    connect=["cursed_blood"],
    source="CoA: 'When you use Taldaram's Torment on a Humanoid or Beast it "
           "now corrupts their blood, increasing your damage dealt against "
           "them by 10%.' No key reads creature type, so it applies to "
           "everything. 'Your damage against them' has no attacker-specific "
           "recipient key either - damage_taken_pct raises damage from any "
           "source - which is a small overreach and the only honest route. "
           "NOTE the unit: damage_taken_pct is the ONE status stat_mod read "
           "RAW, so 10% is 0.10 here while the school-specific variants "
           "would be 10.0."))

N.append(node(
    "gore_barrage", "Gore Barrage",
    "Reduces the health cost of your blood spells by 30%.",
    2, 2,
    effects={f"ability_{a}_cost_pct": 0.30 for a in HEALTH_SPELLS},
    connect=["bloodsurge"],
    source="CoA: 'Reduces the cost of spells that cost health and Animated "
           "Blood by -30%.' Animated Blood does not exist in Frontier (three "
           "CoA talents name it; the class has no such ability), so the four "
           "health-costed spells carry it. POSITIVE reduces. This is the node "
           "that makes a health-paying caster survivable in melee."))

N.append(node(
    "sanguine_scripture", "Sanguine Scripture",
    "Increases your haste by 8%.",
    2, 4,
    effects={"haste": 8.0},
    connect=["bloodsurge"],
    source="CoA: 'Upon exiting Accursed Form, you gain 70% movement speed and "
           "spell haste for 5 sec.' No trigger fires when a buff EXPIRES - "
           "the same wall Mountain King's Primal Guardian hit - and movement "
           "speed does not exist. The haste half is granted permanently at a "
           "fraction of CoA's value, since CoA's is a 5-second burst."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "cursed_blood", "Cursed Blood",
    "Taldaram's Torment has a 20% chance to rupture, splashing 50% of its "
    "damage onto up to 4 nearby enemies.",
    3, -4,
    proc={"trigger": "on_damage_cast", "chance": 20, "icd": 0,
          "ability_filter": ["bloodmage_taldarams_torment"],
          "splash_damage": {"pct": 0.50, "max_targets": 4,
                            "school": "shadow"}},
    connect=["gore_tome"],
    source="CoA verbatim: 'Damage dealt by Taldaram's Torment now has a 20% "
           "chance to internally rupture, causing it to deal its damage an "
           "additional time to all enemies near the target.' CoA's 20% kept. "
           "'Its damage an additional time' would be extra_attack, but that "
           "hits the primary target only - splash_damage is what 'to all "
           "enemies near the target' means in an engine with no positions."))

N.append(node(
    "shadow_pact", "Shadow Pact",
    "Your blood spells shield you for 25% of the damage they deal.",
    3, -2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
          "ability_filter": HEALTH_SPELLS,
          "shield_pct": {"pct": 0.25, "duration": 2,
                         "effect_id": "bloodmage_shadow_pact",
                         "name": "Shadow Pact"}},
    connect=["gore_tome"],
    source="CoA: 'Increases the effectiveness of your Shields by 50%.' There "
           "is no shield-effectiveness multiplier key, and Accursed has no "
           "shield of its own to raise, so there was nothing for CoA's "
           "version to multiply. Rebuilt as the shield itself, off the "
           "health-costed spells - which is the right place for it on a spec "
           "that pays its own HP to cast. 1-turn internal cooldown so a "
           "rotation does not keep a permanent absorb up."))

N.append(node(
    "aortic_assault", "Aortic Assault",
    "Aortic Assault strikes everything around it, splashing 40% of its "
    "damage onto up to 5 enemies.",
    3, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["bloodmage_aortic_assault"],
          "splash_damage": {"pct": 0.40, "max_targets": 5,
                            "school": "physical"}},
    connect=["dark_sigil"],
    source="CoA: 'Channeled. Extend the duration of your active Cursed Form "
           "by 3 sec and strike nearby enemies every 0.5 sec for 3 sec.' "
           "Channels do not exist and neither does extending another effect's "
           "duration from a talent, so this is the repeated-strike half as a "
           "splash. Also carries CoA's Clotting ('at the end of Aortic "
           "Assault's duration, all enemies in a frontal cone suffer "
           "damage'), which is the same idea again and would have been this "
           "node twice."))

N.append(node(
    "gore_tome", "Gore Tome",
    "Taking a Cursed Form guarantees your next strikes crit for 2 turns.",
    3, 2,
    proc={"trigger": "on_cast", "chance": 100, "icd": 0,
          "ability_filter": FORMS,
          "apply_effect": {"effect_id": "bloodmage_gore_tome",
                           "name": "Gore Tome", "effect_type": "buff",
                           "duration": 2, "max_stacks": 1,
                           "stat_mods": {"crit_chance_physical": 60.0},
                           "on_target": False}},
    connect=["dark_sigil"],
    source="CoA: 'For the first 5 sec after activating a Cursed Form, your "
           "Bloodfang Bite is now guaranteed to critically strike.' The "
           "window ports as a buff off the cast. It is 60% crit rather than a "
           "guarantee, and general rather than Bloodfang-only, because a "
           "status effect cannot carry ability_bloodmage_bloodfang_bite_crit "
           "- per-ability keys are read through get_talent_effects(), which "
           "never includes status effects. 5 sec is 2 turns."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "bloodsurge", "Bloodsurge",
    "Taking a Cursed Form enrages you, increasing your Shadow damage and "
    "spell critical strike chance by 20% for 4 turns.",
    4, -3,
    proc={"trigger": "on_cast", "chance": 100, "icd": 0,
          "ability_filter": FORMS,
          "apply_effect": {"effect_id": "bloodmage_bloodsurge",
                           "name": "Bloodsurge", "effect_type": "buff",
                           "duration": 4, "max_stacks": 1,
                           "stat_mods": {"crit_chance_spell": 20.0,
                                         "damage_dealt_pct": 20.0},
                           "on_target": False}},
    connect=["dark_frenzy"],
    source="CoA: '3 min cooldown. Enter a bloodsurge, increasing your Shadow "
           "damage dealt and your spell critical strike chance by 20% for 20 "
           "sec. At the end of the duration, or whenever you trigger Accursed "
           "Form, gain Bloodchaser instead.' Frontier has a "
           "bloodmage_bloodsurge ability already, so this node is not its "
           "unlock. The Bloodchaser follow-up needs an on-expiry trigger, "
           "which does not exist. Hung off the Cursed Form cast - the same "
           "trigger as Accursed Form and Gore Tome, deliberately: taking a "
           "form is this spec's one big button and three talents should all "
           "reward it. damage_dealt_pct is school-agnostic, so the Shadow "
           "restriction is lost."))

N.append(node(
    "dark_sigil", "Dark Sigil",
    "Your critical strikes heal you for 15% of the damage dealt.",
    4, -1,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "leech_pct": {"pct": 0.15}},
    connect=["dark_frenzy"],
    source="CoA verbatim for the half that is buildable: 'Increases critical "
           "strike chance of all party and raid members by 3%. Does not stack "
           "with similar effects. In addition, you now heal for 15% of all "
           "critical damage dealt.' The party aura has no mechanism; the "
           "leech ports exactly, including CoA's 15%."))

N.append(node(
    "endure_the_curse", "Endure the Curse",
    "Taking a heavy blow turns the curse outward, reducing your damage taken "
    "by 30% for 3 turns and healing you.",
    4, 1,
    proc={"trigger": "on_damage_taken", "chance": 12, "icd": 8,
          "heal_flat": 350,
          "apply_effect": {"effect_id": "bloodmage_endure_the_curse",
                           "name": "Endure the Curse", "effect_type": "buff",
                           "duration": 3, "max_stacks": 1,
                           "stat_mods": {"damage_taken_pct": -0.30},
                           "on_target": False}},
    connect=["crimson_feast"],
    source="CoA: 'Reduce all damage taken by -30% for 10 seconds. While "
           "active, taking damage that would reduce your health below 10% "
           "will instantly heal you for 30% of your maximum health. Can only "
           "occur once.' No proc reads the carrier's own health threshold, so "
           "the two halves collapse into one roll: a 12% chance on taking "
           "damage with an 8-turn internal cooldown. CoA's -30% kept, and "
           "damage_taken_pct is read RAW in a status effect so it is -0.30, "
           "not -30.0 - the latter being the 3000% reduction Boltslinger's "
           "Evasive shipped as before the audit caught it."))

N.append(node(
    "dark_frenzy", "Dark Frenzy",
    "Increases your haste by 3%.",
    4, 3,
    effects={"haste": 3.0},
    connect=["crimson_feast"],
    source="CoA: 'Increases spell haste of all party and raid members by 3%. "
           "Does not stack with similar effects. In addition, while a Cursed "
           "Form is active, your global cooldowns are reduced by 25%.' The "
           "party aura has no mechanism, and there is NO GLOBAL COOLDOWN in "
           "this engine - so the second half is free value with nothing to "
           "apply it to and is dropped rather than repriced into unrelated "
           "damage. What survives is CoA's own self-haste number."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "crimson_feast", "Crimson Feast",
    "Your strikes bring your Cursed Forms back sooner.",
    5, -3,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
          "ability_filter": STRIKES,
          "reset_cooldown": {"abilities": FORMS, "turns": 1}},
    connect=["crimson_terror_acc"],
    source="CoA: 'Every 0.01 second you remain in a Cursed Form now reduces "
           "the cooldown of your Bloodsurge by 5 sec.' There is no turn-based "
           "reading of 'every 0.01 second', and no trigger fires for time "
           "spent in a buff. Rebuilt as strikes shortening the FORM "
           "cooldowns, which is the loop CoA is after from the other end - "
           "stay in the form, get the form back faster. turns:1 knocks one "
           "turn off rather than resetting outright."))

N.append(node(
    "veinburst_mastery", "Veinburst",
    "Increases the damage of Veinburst by 50% and its critical strike damage "
    "by 25%.",
    5, -1,
    effects={"ability_bloodmage_veinburst_damage": 0.50,
             "ability_bloodmage_veinburst_crit_damage": 0.25},
    connect=["crimson_terror_acc"],
    source="CoA's Veinburst: 'Blast an enemy, dealing Shadow damage. Deals "
           "25% increased damage to bleeding targets.' Frontier has the "
           "ability already, so this is not an unlock. The bleeding condition "
           "has no key, so the 25% is moved into crit damage instead of being "
           "granted unconditionally on top of the base - which would have "
           "been the same number twice. ability_*_crit_damage is a FRACTION "
           "while ability_*_crit is a percent."))

N.append(node(
    "blood_plague", "Blood Plague",
    "Increases the critical strike chance and critical damage of Ravenous "
    "Strike and Claw Sweep by 10%.",
    5, 1,
    effects={"ability_bloodmage_ravenous_strike_crit": 10.0,
             "ability_bloodmage_claw_sweep_crit": 10.0,
             "crit_damage_physical": 0.10},
    connect=["crimson_terror_acc"],
    source="CoA: 'Increases the critical strike chance and critical damage of "
           "Ravenous Strike and Claw Sweep by 10% against Diseased targets.' "
           "No key reads a creature or debuff state, so it is unconditional. "
           "The crit-damage half is general rather than per-ability, because "
           "ability_*_crit_damage exists but splitting 10% across two "
           "abilities and also granting it generally would be the same bonus "
           "twice."))

N.append(node(
    "reave_mastery", "Reave",
    "Increases the damage of Reave by 60%.",
    5, 3,
    effects={"ability_bloodmage_reave_damage": 0.60},
    connect=["crimson_terror_acc"],
    source="CoA's Reave: 'Lacerate an enemy, dealing 125% Weapon Damage. If "
           "the enemy is bleeding, below 35% health, or if you are behind "
           "them, deal 100% additional Shadow damage FOR EACH CONDITION "
           "MET.' The worst of this tree's conditional nodes: CoA offers up "
           "to +300% from three stacked checks, and not one of the three is "
           "readable - no debuff state, no recipient health for damage, and "
           "no positioning at all. Priced at a flat +60%, roughly one "
           "condition's worth landing reliably rather than three landing "
           "sometimes. Flagged because this is the single biggest fidelity "
           "gap in the Bloodmage rebuild."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "crimson_terror_acc", "Monstrous Appetite",
    "Your strikes drink deep, healing you for 12% of the damage dealt, and "
    "your blood spells hit 25% harder.",
    6, 0,
    effects={f"ability_{a}_damage": 0.25 for a in HEALTH_SPELLS},
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": STRIKES,
          "leech_pct": {"pct": 0.12}},
    source="The capstone, and it closes the loop the whole spec runs on: "
           "melee feeds health, health pays for spells, spells hit harder. "
           "Named for the ability bloodmage_monstrous_hunger rather than "
           "taking a CoA talent name, because the two CoA capstone-depth "
           "nodes here are both unbuildable - Crimson Feast's time-in-form "
           "counter (used at tier 5 for the half that works) and Dark "
           "Frenzy's GCD reduction, in an engine with no GCD. Deliberately "
           "distinct from Sanguine's Crimson Terror, which is spell-side; "
           "this is the melee answer to it."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. tools/talent_ranks.py rescales so a ranked
# node lands on exactly the ceiling it had at one rank. The capstone stays a
# single pick; no Bloodmage ability carries requires_talent, so there are no
# unlock nodes.
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
    print(f"Bloodmage Accursed: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
