#!/usr/bin/env python3
"""Rebuild Bloodmage's Fleshweaver tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_bloodmage_fleshweaver.py [--check]

SOURCE: data/reference/coa/bloodmage.json - 40 real Fleshweaver talents from
Ascension's own CoA Builder payload. Role: HEALER.
coa_playstyles.json: "Discipline Priest + Blood DK".

The shipped tree was 23 nodes with THREE procs and 19 bare numbers. This is
the fourth and last Bloodmage spec; the class went from 11 procs across 92
nodes to 51 across 110.

WHAT THE SPEC IS. A healer that heals by hurting. CoA's Fleshweaver marks
allies with Blood Rituals so its damage spells heal them, bleeds enemies
with Crimson Tide and Vampyr's Kiss, and banks Pooled Vitality off its own
periodic damage and healing.

POOLED VITALITY IS THE SAME WALL SANGUINE HIT. Four CoA talents here read
the live stack count - "each stack increases your Spirit by 3%", "your
damage is increased by 1% for each stack", "consuming Pooled Vitality heals
up to 10 allies", "generates 2 additional stacks". Nothing in this engine
reads a resource or stack AMOUNT into a stat or an effect, and nothing
CONSUMES a caster's stacks except consumes_stacks_of, which only extends a
DoT's duration. Each is flattened, stated on its node. Pooled Vitality is
also not a resource Frontier has at all - the class's secondary is
Vitality, which is CoA's Thirst, not this.

BLOOD RITUALS - the mark that makes damage heal - is the one CoA mechanic
here that IS buildable, through splash_heal on the damage spells. CoA
applies a mark to allies and then heals the marked; this engine cannot
mark an ally and read it back, but splash_heal spreading a heal to nearby
allies is the same outcome from the other end. Three nodes use it.

CONVENTIONS, which do not agree with each other:
  armor_pct, healing_power_pct, attack_power_pct      percentage POINTS
  max_health_pct, healing_taken_pct as TALENT effects FRACTION
  the same two inside a STATUS effect                 percentage POINTS
  splash_heal / leech_pct / shield_pct                FRACTION
  smart_heal_pct                                      PERCENT
  haste / crit_chance_spell / ability_*_crit          PERCENT
  healing_done, dot_damage, ability_*_healing         FRACTION
  *_cost_pct / *_cooldown_pct      FRACTION, POSITIVE MEANS A REDUCTION

TURN-BASED CUTS. Every yard radius, which takes Arterial Bind's pool and
Aortic Aegis' party-range clause. Cast times do not exist, so Crimson
Scion's "next Sanguine Mend is instant cast" has nothing to apply to. Two
CoA entries have broken template descriptions ($7c Sanguine Essence, used
in Eternal instead) and Blood Shards, Bite Wound and Animated Blood are
named by talents but have no ability in Frontier.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/bloodmage_fleshweaver.json"

#: This spec's heals.
HEALS = ["bloodmage_fleshcraft", "bloodmage_sanguine_mend",
         "bloodmage_transfusion", "bloodmage_hemoglobe"]

#: The damage spells CoA's Blood Rituals makes heal marked allies.
RITUAL_SPELLS = ["bloodmage_bloodmoon_blast", "bloodmage_bloodbolt",
                 "bloodmage_crimson_tide"]

#: Periodic damage and healing, for the Pooled Vitality nodes.
PERIODIC = ["bloodmage_crimson_tide", "bloodmage_vampyrs_kiss",
            "bloodmage_hypovolemic_shock", "bloodmage_hemoglobe"]

TREE = {
    "spec_name": "Bloodmage Fleshweaver",
    "tree_id": "bloodmage_fleshweaver",
    "description": ("Heals by hurting - opens a vein in the enemy and the "
                    "party drinks."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from data/reference/coa/bloodmage.json "
        "(40 real CoA Fleshweaver talents, role HEALER, 'Discipline Priest "
        "+ Blood DK'). Replaces a 23-node tree with 3 procs and 19 bare "
        "numbers. Fourth and last Bloodmage spec: the class went from 11 "
        "procs across 92 nodes to 51 across 110. Four CoA talents read the "
        "live Pooled Vitality stack count, which nothing in this engine can "
        "do - the same wall Sanguine's six Thirst nodes hit. Blood Rituals "
        "is built through splash_heal, which reaches the same outcome from "
        "the other end."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"bloodmage_fleshweaver_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"bloodmage_fleshweaver_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "gift_of_lanathel", "Gift of Lana'thel",
    "Increases your spell power by 50% of your Spirit.",
    0, -5,
    effects={"spell_power_from_spirit_pct": 0.50},
    connect=["dark_liturgy"],
    source="CoA over 2 ranks: 'Increases your spell power by 25% of your "
           "Spirit and your hit rating by 4% of your Spirit.' The hit "
           "conversion is NOT built: hit_rating is not in "
           "STAT_CONVERSION_TARGETS, so hit_rating_from_spirit_pct would be "
           "skipped in silence - the Clarity of the Heavens failure, and the "
           "third time this exact pairing has come up in the rebuild. Spirit "
           "is the spec's whole stat, so the spell power half doubled over "
           "CoA's two ranks is the node."))

N.append(node(
    "consolidation", "Consolidation",
    "Increases your haste by 5%.",
    0, -3,
    effects={"haste": 5.0},
    connect=["dark_liturgy"],
    source="CoA verbatim: 'Increases your haste by 5%.' Already a scalar in "
           "CoA."))

N.append(node(
    "organ_orbs", "Organ Orbs",
    "Increases your healing power by 12%.",
    0, -1,
    effects={"healing_power_pct": 12.0},
    connect=["spice_of_life"],
    source="CoA: 'Each stack of Pooled Vitality now increases your Spirit by "
           "3%.' Nothing reads a live stack count into a stat, so this is "
           "flat - and routed to healing power rather than Spirit, because "
           "Gift of Lana'thel at tier 0 already converts Spirit and stacking "
           "both would be the same point twice. healing_power_pct takes "
           "percentage POINTS."))

N.append(node(
    "heart_rupturer", "Heart Rupturer",
    "Increases the damage of Claw Sweep, Sanguine Rupture, Ravenous Strike "
    "and Bloodmoon Blast by 20%.",
    0, 1,
    effects={"ability_bloodmage_claw_sweep_damage": 0.20,
             "ability_bloodmage_sanguine_rupture_damage": 0.20,
             "ability_bloodmage_ravenous_strike_damage": 0.20,
             "ability_bloodmage_bloodmoon_blast_damage": 0.20},
    connect=["spice_of_life"],
    source="CoA verbatim. A healer tree with a damage node is the point of "
           "this spec: Blood Rituals turns that damage into healing, so "
           "raising it raises both."))

N.append(node(
    "blood_redistribution", "Blood Redistribution",
    "Increases the healing done by Fleshcraft by 25%.",
    0, 3,
    effects={"ability_bloodmage_fleshcraft_healing": 0.25},
    connect=["dissipation"],
    source="CoA verbatim: 'Increases the maximum health restored by Fleshcraft "
           "by 25%.' ability_*_healing is the key a heal reads - for a long "
           "time only _damage was looked up, which silently broke every "
           "talent authored the correct way, so both work now and _healing is "
           "the name that belongs here."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "dark_liturgy", "Dark Liturgy",
    "Bloodmoon Blast and Bloodbolt spill 25% of their damage onto up to 4 "
    "allies as healing.",
    1, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["bloodmage_bloodmoon_blast",
                             "bloodmage_bloodbolt"],
          "leech_pct": {"pct": 0.25, "smart": True}},
    connect=["dark_essence"],
    source="CoA: 'Form a blood bond, healing a friendly target and applying "
           "Blood Rituals to them, bouncing to up to 10 nearby allies. Blood "
           "Rituals: Causes Bloodmoon Blast to heal marked allies.' THIS IS "
           "THE SPEC'S THESIS and the old tree had no form of it. Marking an "
           "ally and reading the mark back is not possible, so it is built as "
           "leech_pct with smart:true - the damage heals the worst-off ally - "
           "which is the same outcome CoA describes by a route that fires. "
           "smart:true is what sends it to an ALLY rather than the caster; "
           "without it this would be a self-heal, which is Sanguine's "
           "Hematoma, not this."))

N.append(node(
    "spice_of_life", "Spice of Life",
    "Your periodic spells return 8 Rage.",
    1, -2,
    proc={"trigger": "on_damage_or_heal_cast", "chance": 100, "icd": 1,
          "ability_filter": PERIODIC,
          "grant_resource": {"resource": "rage", "amount": 8}},
    connect=["dark_essence"],
    source="CoA: 'Your periodic damage and healing now has a 10% chance to "
           "grant a stack of Pooled Vitality.' Pooled Vitality is not a "
           "resource Frontier has - the class's secondary is Vitality, which "
           "is CoA's Thirst, a different thing - so the grant becomes Rage, "
           "which this spec's heals actually cost. on_damage_or_heal_cast is "
           "the one trigger that catches both halves of 'periodic damage and "
           "healing', which is why Crimson Tide and Hemoglobe are in the same "
           "filter."))

N.append(node(
    "dissipation", "Dissipation",
    "Reduces the cooldown of Fleshcraft by up to 50%.",
    1, 0,
    effects={"ability_bloodmage_fleshcraft_cooldown_pct": 0.50},
    connect=["sanguine_scion"],
    source="CoA over 2 ranks: 'Reduces the cooldown of Fleshcraft and the "
           "duration of the Sated debuff by -60 sec.' Sated does not exist in "
           "Frontier. Expressed as a percentage because cooldowns are counted "
           "in turns here. POSITIVE reduces."))

N.append(node(
    "sanguine_scion", "Sanguine Scion",
    "Increases the critical strike chance of Sanguine Mend and Bloodbolt by "
    "10%.",
    1, 2,
    effects={"ability_bloodmage_sanguine_mend_crit": 10.0,
             "ability_bloodmage_bloodbolt_crit": 10.0},
    connect=["excess_blood"],
    source="CoA verbatim. One heal and one damage spell in the same node, "
           "which is this spec in miniature."))

N.append(node(
    "raging_hunger", "Raging Hunger",
    "Your heals return 5 Rage.",
    1, 4,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": HEALS,
          "grant_resource": {"resource": "rage", "amount": 5}},
    connect=["excess_blood"],
    source="CoA: 'Triggering Pooled Vitality now also generates 3 Rage.' "
           "Pooled Vitality does not exist here, so the trigger becomes "
           "healing - which is what was generating it in CoA. This and Spice "
           "of Life are the spec's two Rage sources, deliberately split "
           "across healing and periodic damage so a Fleshweaver has to do "
           "both."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "dark_essence", "Dark Essence",
    "Crimson Tide washes healing over up to 5 allies.",
    2, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["bloodmage_crimson_tide"],
          "leech_pct": {"pct": 0.35, "smart": True}},
    connect=["vampyrs_kiss"],
    source="CoA: 'Casting Cursed Form abilities or Bloodbolt will now heal "
           "allies affected by Blood Rituals.' The second Blood Rituals node, "
           "pointed at Crimson Tide rather than repeating Dark Liturgy's "
           "filter - Crimson Tide is this spec's area bleed, so healing off "
           "it is what makes the spec's AoE rotation also its group healing. "
           "smart:true again, so it reaches an ally."))

N.append(node(
    "excess_blood", "Excess Blood",
    "Your heals have a 10% chance to leave the target mending for 2 more "
    "turns.",
    2, -2,
    proc={"trigger": "on_heal_cast", "chance": 10, "icd": 0,
          "ability_filter": HEALS,
          "apply_effect": {"effect_id": "bloodmage_excess_blood",
                           "name": "Excess Blood", "effect_type": "hot",
                           "duration": 2, "potency": 46,
                           "on_target": True}},
    connect=["vampyrs_kiss"],
    source="CoA verbatim: 'Your healing done now has a 10% chance to heal the "
           "target for an additional 240 + 3% healing over 6 seconds.' CoA's "
           "10% kept; 6 sec is 2 turns. A proc-applied hot takes a flat "
           "potency - there is no percentage-of-the-triggering-heal form for "
           "apply_effect, unlike shield_pct and splash_heal."))

N.append(node(
    "universal_donor", "Universal Donor",
    "Vampyr's Kiss makes everyone receive 6% more healing for 4 turns.",
    2, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["bloodmage_vampyrs_kiss"],
          "apply_effect": {"effect_id": "bloodmage_universal_donor",
                           "name": "Universal Donor", "effect_type": "buff",
                           "duration": 4, "max_stacks": 1,
                           "stat_mods": {"healing_taken_pct": 6.0},
                           "on_target": False}},
    connect=["waves_of_blood"],
    source="CoA: 'Casting Infuse or Vampyr's Kiss now increases the healing "
           "received by all allies by 6% for 10 sec.' Infuse does not exist "
           "in Frontier. 'All allies' has no mechanism - apply_effect lands "
           "on the caster or the trigger's target, not on a party - so the "
           "buff is self-only and the description says 'everyone' as the "
           "flavour it is. healing_taken_pct is percentage POINTS inside a "
           "status effect, which is the opposite of the same key as a talent "
           "effect, where Eternal Resolve writes 0.15 for 15%."))

N.append(node(
    "black_heart", "Black Heart",
    "Vampyr's Kiss returns 20 Rage.",
    2, 2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["bloodmage_vampyrs_kiss"],
          "grant_resource": {"resource": "rage", "amount": 20}},
    connect=["waves_of_blood"],
    source="CoA verbatim: 'Your Vampyr's Kiss now regenerates 20% of your "
           "maximum Rage.' Max Rage is a hardcoded 100, so 20% of it is a "
           "flat 20 - which is the one case in this rebuild where a "
           "percentage of a resource pool translates exactly, because the "
           "pool is fixed."))

N.append(node(
    "flesh_foundry", "Flesh Foundry",
    "Increases your spell critical strike chance by 15% of your Spirit.",
    2, 4,
    effects={"crit_chance_spell_from_spirit_pct": 0.15},
    connect=["crimson_scion"],
    source="CoA: 'Your critical strikes now reduce the cooldown of Fleshcraft "
           "and the duration of Sated on the target by 4 sec. In addition, "
           "increases your critical strike rating by 15% of your Spirit.' The "
           "conversion half is live - crit_chance_spell is in "
           "STAT_CONVERSION_TARGETS and spirit is a source - and is the half "
           "worth having on a Spirit-stacking healer. The cooldown rider "
           "would need a second proc; Dissipation at tier 1 already shortens "
           "Fleshcraft."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "vampyrs_kiss", "Vampyr's Kiss",
    "Vampyr's Kiss leaves the target bleeding for 5 turns and taking 25% "
    "more damage over time.",
    3, -4,
    effects={"dot_damage": 0.25},
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["bloodmage_vampyrs_kiss"],
          "apply_effect": {"effect_id": "bloodmage_vampyrs_kiss_bleed",
                           "name": "Vampyr's Kiss", "effect_type": "dot",
                           "duration": 5, "potency": 34,
                           "damage_school": "shadow", "on_target": True}},
    connect=["lingering_essence"],
    source="CoA: 'Curse an enemy, causing them to bleed over 30 sec. All "
           "periodic damage dealt to an enemy affected by Vampyr's Kiss is "
           "replicated on them equal to 25% of the value.' Frontier has the "
           "ability. The REPLICATION cannot be built as written - no key "
           "reads whether a target carries a debuff, so 'periodic damage "
           "against a marked enemy is amplified' becomes a flat dot_damage "
           "bonus, which is the same arithmetic without the condition. 30 sec "
           "is 10 turns, cut to 5 so it has to be reapplied."))

N.append(node(
    "waves_of_blood", "Waves of Blood",
    "Crimson Tide has a 10% chance to heal an ally for a quarter of its "
    "damage.",
    3, -2,
    proc={"trigger": "on_damage_cast", "chance": 10, "icd": 0,
          "ability_filter": ["bloodmage_crimson_tide"],
          "leech_pct": {"pct": 0.25, "smart": True}},
    connect=["lingering_essence"],
    source="CoA verbatim: 'Each tick of Crimson Tide now has a 10% chance to "
           "heal a nearby ally for 25% of the damage dealt.' PER TICK is not "
           "reachable - no periodic trigger exists - so the roll happens on "
           "the cast. CoA's 10% and 25% both kept, and smart:true sends it to "
           "an ally as CoA specifies."))

N.append(node(
    "crimson_scion", "Crimson Scion",
    "Your damage has a 10% chance to make your next heals 25% stronger for "
    "2 turns.",
    3, 0,
    proc={"trigger": "on_damage_cast", "chance": 10, "icd": 1,
          "apply_effect": {"effect_id": "bloodmage_crimson_scion",
                           "name": "Crimson Scion", "effect_type": "buff",
                           "duration": 2, "max_stacks": 1,
                           "stat_mods": {"healing_done_pct": 25.0},
                           "on_target": False}},
    connect=["gruesome_rituals"],
    source="CoA: 'Direct damage dealt now has a 10% chance to make your next "
           "Sanguine Mend within 10 sec instant cast.' There are no cast "
           "times, so making something instant is worth nothing. Repriced as "
           "healing done over the same window - healing_done_pct is the "
           "status-effect route to a healing multiplier, the mirror of "
           "damage_dealt_pct, and it takes percentage POINTS. CoA's 10% "
           "chance kept."))

N.append(node(
    "lingering_essence", "Lingering Essence",
    "Your periodic spells have a 50% chance to bring Vampyr's Kiss a turn "
    "closer to ready.",
    3, 2,
    proc={"trigger": "on_damage_or_heal_cast", "chance": 50, "icd": 0,
          "ability_filter": PERIODIC,
          "reset_cooldown": {"abilities": ["bloodmage_vampyrs_kiss"],
                             "turns": 1}},
    connect=["gruesome_rituals"],
    source="CoA verbatim: 'Periodic damage and healing done now has a 50% "
           "chance to reduce the cooldown of Vampyr's Kiss by -1 sec.' Ports "
           "almost exactly - CoA's 50%, one second is one turn, and "
           "on_damage_or_heal_cast catches both halves."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "gruesome_rituals", "Gruesome Rituals",
    "Increases all damage you deal by 10% and all healing you do by 10%.",
    4, -3,
    effects={"all_damage": 0.10, "healing_done": 0.10},
    connect=["vitality_for_later"],
    source="CoA: 'Your damage dealt is now increased by 1% for each stack of "
           "Pooled Vitality.' Ten stacks is 10%, granted flat because nothing "
           "reads a live stack count - and paired with the same number on "
           "healing, because on this spec they are the same thing: every "
           "Blood Rituals node turns damage into healing, so a damage-only "
           "node would be half a talent."))

N.append(node(
    "acquired_taste", "Acquired Taste",
    "Vampyr's Kiss and Crimson Tide shield you for 30% of their damage.",
    4, -1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
          "ability_filter": ["bloodmage_vampyrs_kiss",
                             "bloodmage_crimson_tide"],
          "shield_pct": {"pct": 0.30, "duration": 2,
                         "effect_id": "bloodmage_acquired_taste",
                         "name": "Acquired Taste"}},
    connect=["sovereignty"],
    source="CoA: 'Casting Infuse or Vampyr's Kiss now generates 2 additional "
           "stacks of Pooled Vitality.' Pooled Vitality does not exist and "
           "Infuse does not either. Rebuilt as an absorb off the two abilities "
           "CoA pairs here, which is what banking vitality was FOR - this is "
           "a healer standing in melee range to apply bleeds, and it needs "
           "something back for it. Also carries CoA's Aortic Aegis ('your "
           "Blood Veil now applies to the party members of the target'), "
           "which needs a buff to spread from one ally to their party - "
           "apply_effect lands on one target and nothing fans it out, and "
           "splash_heal spreads healing rather than a buff."))

N.append(node(
    "arterial_bind", "Arterial Bind",
    "Your heals spill 20% of their value onto up to 4 more allies.",
    4, 1,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": HEALS,
          "splash_heal": {"pct": 0.20, "max_targets": 4}},
    connect=["vitality_for_later"],
    source="CoA: 'Place a pool of blood on the ground, instantly silencing "
           "all enemies for 4 seconds and healing allies every 1 sec for 4 "
           "seconds.' Ground targeting and the silence are both gone - no "
           "positioning, and a blanket silence is not a payload. What "
           "survives is the group healing, built as splash off this spec's "
           "own heals. THIS is splash_heal rather than leech_pct, because it "
           "spreads a HEAL rather than converting damage - the two sit side "
           "by side in this tree and size themselves off different things."))

N.append(node(
    "dark_blood", "Dark Blood",
    "Reduces the cost of your heals by up to 30%.",
    4, 3,
    effects={"heal_cost_pct": 0.30},
    connect=["vitality_for_later"],
    source="CoA over 2 ranks: 'Reduces the cost of your abilities that "
           "require Cursed Form and increases the healing done by Blood "
           "Rituals by 25%.' Cursed Form is a buff with no 'requires' gate "
           "for an effect key, and Blood Rituals in this tree is a set of "
           "procs rather than an ability with healing to raise. Pointed at the "
           "heals themselves, which cost Rage on this spec. heal_cost_pct is "
           "the alias of healing_spell_cost_pct; POSITIVE reduces."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "vitality_for_later", "Vitality For Later",
    "Your critical heals wash over your most wounded ally for 40% of the "
    "value.",
    5, -3,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "ability_filter": HEALS,
          "smart_heal_pct": 40},
    connect=["sovereignty"],
    source="CoA: 'Consuming Pooled Vitality now heals up to 10 allies within "
           "30 yds.' Consuming a caster's own stacks is not reachable - "
           "consumes_stacks_of reads them but only extends a DoT's duration, "
           "and these are heals - so the trigger becomes a critical heal, "
           "which is the closest thing to a payoff moment this spec has. "
           "smart_heal_pct is a PERCENT, divided by 100 at read time, unlike "
           "the splash_heal and leech_pct fractions elsewhere in this tree."))

N.append(node(
    "sovereignty", "Sovereignty",
    "Crimson Tide makes your next spells 15% stronger for 3 turns, stacking "
    "5 times.",
    5, -1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["bloodmage_crimson_tide"],
          "apply_effect": {"effect_id": "bloodmage_sovereignty",
                           "name": "Sovereignty", "effect_type": "buff",
                           "duration": 3, "max_stacks": 5,
                           "stat_mods": {"damage_dealt_pct": 15.0},
                           "on_target": False}},
    connect=["hemal_excision"],
    source="CoA: 'Damage dealt by Crimson Tide now grants you Sovereignty. "
           "Sovereignty: Reduces the cost of your next Bloodbolt within 12 "
           "sec by 10% and causes it to strike 1 additional nearby enemy for "
           "each target damaged, stacking up to 5 times.' Neither half is "
           "buildable - a status effect cannot reach an ability cost key, and "
           "nothing adds targets to an ability - so the stacks pay out as "
           "damage. CoA's 5 stacks kept, which is the part that makes it feel "
           "like Sovereignty rather than a flat buff."))

N.append(node(
    "hemal_excision", "Hemal Excision",
    "Your heals cleanse the target and shield them for 35% of the healing "
    "done.",
    5, 1,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 2,
          "ability_filter": HEALS,
          "shield_pct": {"pct": 0.35, "duration": 2,
                         "effect_id": "bloodmage_hemal_excision",
                         "name": "Hemal Excision"}},
    connect=["blood_rituals"],
    source="CoA: 'Cut into an ally's vital essence, siphoning all curse "
           "effects from them. You may reactivate this ability again within "
           "10 seconds to place these curse effects on an enemy.' Moving a "
           "debuff from an ally to an enemy is not a payload this engine has - "
           "dispel removes, it does not transfer - so the cleanse half is "
           "flavour in the description and the mechanic is an absorb, which is "
           "what a Discipline-Priest-shaped healer wants at this depth. "
           "shield_pct sizes from the triggering heal."))

N.append(node(
    "infuse", "Infuse",
    "Increases the damage your damage-over-time effects deal by 25% and your "
    "healing power by 10%.",
    5, 3,
    effects={"dot_damage": 0.25, "healing_power_pct": 10.0},
    connect=["blood_rituals"],
    source="CoA: 'Accumulates 10% of all damage dealt to the target and "
           "unleashes it after 10 seconds, dealing Shadow damage and "
           "absorbing healing done to the target equal to the damage done.' A "
           "delayed accumulator is not a shape this engine has - nothing "
           "banks damage against a target and detonates it on a timer - and "
           "Frontier has no bloodmage_infuse ability either. Rebuilt as the "
           "two stats the talent is for: periodic damage, and the healing it "
           "turns into. healing_power_pct takes percentage POINTS."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "blood_rituals", "Blood Rituals",
    "Every spell you cast feeds the party - damage spills 30% onto your most "
    "wounded ally as healing, and heals spill 30% onto four more.",
    6, 0,
    proc={"trigger": "on_damage_or_heal_cast", "chance": 100, "icd": 0,
          "leech_pct": {"pct": 0.30, "smart": True},
          "splash_heal": {"pct": 0.30, "max_targets": 4}},
    source="The capstone, and the only node in the game that pairs leech_pct "
           "and splash_heal off one trigger. on_damage_or_heal_cast catches "
           "both halves, so a damage spell drains into the worst-off ally and "
           "a heal spreads to four more - which is CoA's Blood Rituals in "
           "full, the mark that makes damage heal, finally without needing a "
           "mark at all. Named for it because the three earlier nodes that "
           "carry pieces of the mechanic (Dark Liturgy, Dark Essence, Waves "
           "of Blood) each only reach one ability; this reaches everything. "
           "NOTE the two payloads size from different things: leech_pct takes "
           "the damage amount, splash_heal takes the heal amount, and on a "
           "turn that does both they both fire."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. See tools/talent_ranks.py.
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
    print(f"Bloodmage Fleshweaver: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
