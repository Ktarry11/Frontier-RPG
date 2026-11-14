#!/usr/bin/env python3
"""Rebuild Venomancer's Stalking tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_venomancer_stalking.py [--check]

SOURCE: data/reference/coa_worksheets/venomancer.md and
data/reference/coa/venomancer.json - 41 real Stalking talents from
Ascension's own CoA Builder payload. Role: DPS.

The shipped tree was 25 nodes with THREE procs.

WHAT THE SPEC IS. The Spider Form melee-poison spec. Venom Fang builds,
and Widowmaker, Rotfang and Facemelter are finishers that REQUIRE SPIDER
FORM - requires_form is live on all three (combat/abilities.py reads it
via is_form_ready), so the form is a real gate and not flavour. Withering
Venom and Nerubian Sting carry the rot.

BROOD MARKS DO NOT EXIST, and they are the spine of the spec. CoA gives
every finisher five damage tiers by mark count ("1 Mark: x1.25 ... 5
Marks: x2.60"), and eight talents generate, consume, count or empower
them. There is no combo-point system here: Venomancer's secondary
resource is None (abilities.py:150), and brood_marks / brood_mark /
combo_points are all read by nothing. Nothing reads another effect's
stack count either, so marks cannot even be faked as a stacking buff that
the finishers read. Every finisher is therefore priced at roughly its
MID-TIER mark value, flat, and each node says so. This is the largest
single thing lost in this tree and it is stated rather than papered over.

PROWLER PORTS HALF. CoA: "spell damage by 25% of Intellect and hit rating
by 3% of Intellect." spell_damage is in STAT_CONVERSION_TARGETS;
HIT_RATING IS NOT - the fourth time in this audit that exact pairing has
cost a node half its text (Witch Doctor's Voodoo Power, Guardian's
Bulwark, Venom's own Shadra's Gift being the lucky exception).

UNLOCK NODES. None of this tree's abilities is talent-gated - the class's
only gated ability, barbed_stinger, is unlocked from Fortitude - so the
old tree's six unlock nodes (Spider Form, Widowmaker, Nerubian Sting,
Withering Venom, Facemelter, Rotfang) all granted abilities the character
already had and did nothing. Replaced with real mechanics. The gate
itself is real and was verified end to end; see the Venom builder.

CONVENTIONS, which do not agree with each other:
  intellect_pct, agility_pct               percentage POINTS
  spell_damage, all_damage, dot_damage, crit_damage_spell,
    ability_*_damage, ability_*_crit_damage   FRACTION
  crit_chance_spell, haste, hit_rating,
    ability_*_crit                            PERCENT
  spell_damage_taken_pct inside a status effect: divided by 100,
    POSITIVE INCREASES damage taken
  splash_damage                            FRACTION
  <target>_from_<source>_pct  FRACTION, listed pairs only
  *_cost_pct / *_cooldown_pct  FRACTION, POSITIVE MEANS A REDUCTION

TURN-BASED CUTS. "Ticks N% faster" and "reduced duration" (Acidfang,
Rotting Sores, Shadra's Seance) have no meaning per-turn; "every 3rd
Venom Fang becomes X" needs a cast counter that does not exist (Widow's
Kiss); health-threshold conditions have no key (Virulent Opening, Black
Widow, Lethality's Diseased check); and Energy regeneration has no key at
all, which takes half of Noxious Empowerment.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/venomancer_stalking.json"

#: The Spider Form finishers - all three carry requires_form="spider".
FINISHERS = ["venomancer_widowmaker", "venomancer_rotfang",
             "venomancer_facemelter"]

#: The builders and rots.
BUILDERS = ["venomancer_venom_fang", "venomancer_nerubian_sting"]
ROTS = ["venomancer_withering_venom", "venomancer_rotfang"]

TREE = {
    "spec_name": "Venomancer Stalking",
    "tree_id": "venomancer_stalking",
    "description": ("Spider form and shadow venom - a stalker whose "
                    "finishers rot a target from the inside."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from the 41 real CoA Stalking talents (role "
        "DPS). BROOD MARKS DO NOT EXIST - CoA gives every finisher five "
        "damage tiers by mark count and eight talents touch them, but there "
        "is no combo-point system (Venomancer's secondary resource is None) "
        "and nothing reads another effect's stack count, so marks cannot "
        "even be faked. Finishers are priced at roughly their mid-tier mark "
        "value, flat. requires_form IS live, so Spider Form is a real gate "
        "on all three finishers. Prowler ports half: spell_damage is a legal "
        "conversion target, hit_rating is not. The old tree's six unlock "
        "nodes were all for non-gated abilities and did nothing."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"venomancer_stalking_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"venomancer_stalking_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "prowler", "Prowler",
    "Increases your spell damage by 25% of your Intellect.",
    0, -5,
    effects={"spell_damage_from_intellect_pct": 0.25},
    connect=["boding_dread"],
    source="CoA verbatim: 'Level 20 Passive. Increases your spell damage by "
           "25% of your Intellect and your hit rating by 3% of your "
           "Intellect.' The spell damage half ports exactly. THE HIT "
           "CONVERSION DOES NOT - hit_rating is not in "
           "STAT_CONVERSION_TARGETS, so authoring it would be skipped in "
           "silence. That is the FOURTH time in this audit this exact "
           "pairing has cost a node half its text, after the Witch Doctor's "
           "Voodoo Power and Guardian's Bulwark; Venom's Shadra's Gift was "
           "the one that got lucky by pairing Intellect with haste instead. "
           "Virulent Resonance below carries flat hit to compensate."))

N.append(node(
    "boding_dread", "Boding Dread",
    "Increases your spell damage by 6% and your spell critical strike chance "
    "by 6%.",
    0, -3,
    effects={"spell_damage": 0.06, "crit_chance_spell": 6.0},
    connect=["glory_to_shadra"],
    source="CoA over 2 ranks: 'Increases your Shadow damage dealt and your "
           "critical strike chance with Shadow spells by 3%.' Doubled for the "
           "two ranks. THERE IS NO PER-SCHOOL DAMAGE OR CRIT KEY - "
           "shadow_damage is read by nothing - so both halves land on the "
           "general spell keys. This spec deals shadow and nature almost "
           "exclusively, so the broader keys are close to equivalent. Note "
           "the units differ: spell_damage is a FRACTION, crit_chance_spell a "
           "PERCENT."))

N.append(node(
    "glory_to_shadra", "Glory To Shadra!",
    "Increases the critical strike chance of Venom Fang and Nerubian Sting by "
    "10%.",
    0, -1,
    effects={f"ability_{a}_crit": 10.0 for a in BUILDERS},
    connect=["virulent_resonance"],
    source="CoA verbatim: 'Increases the critical strike chance of Venom Fang "
           "and Nerubian Sting by 10%.' Ports exactly - both abilities exist "
           "in Frontier. ability_*_crit is a PERCENT."))

N.append(node(
    "virulent_resonance", "Virulent Resonance",
    "Increases your chance to hit by 5% and the damage of your finishers by "
    "10%.",
    0, 1,
    effects={"hit_rating": 5.0,
             **{f"ability_{a}_damage": 0.10 for a in FINISHERS}},
    connect=["venomagus"],
    source="CoA verbatim: 'Increases the effectiveness of Brood Marks by 10% "
           "and your hit chance by 5%.' Brood Marks do not exist, so "
           "'effectiveness of Brood Marks' becomes the damage of the three "
           "abilities that consumed them - which is what mark effectiveness "
           "bought. The 5% hit ports exactly and partly covers what Prowler "
           "lost."))

N.append(node(
    "venomagus", "Venomagus",
    "Increases the damage of Withering Venom by 40%.",
    0, 3,
    effects={"ability_venomancer_withering_venom_damage": 0.40},
    connect=["vile_fangs"],
    source="CoA over 2 ranks: 'Increases the damage of Blight Venom by 20%.' "
           "Blight Venom exists in Frontier but as a SELF BUFF (effect_type "
           "buff, target_type self) - one of the Venoms the class applies to "
           "itself - so it has no damage to increase. Re-pointed at Withering "
           "Venom, the spec's real damaging venom, at the doubled two-rank "
           "value."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "vile_fangs", "Vile Fangs",
    "Increases the damage your damage-over-time spells deal by 20%.",
    1, -4,
    effects={"dot_damage": 0.20},
    connect=["potency"],
    source="CoA verbatim: 'Periodic damage dealt now has a 10% chance to "
           "generate a Brood Mark.' BROOD MARKS DO NOT EXIST - there is no "
           "combo-point system and no resource to grant (Venomancer's "
           "secondary is None), so a mark generator has nothing to generate. "
           "Rerouted to the periodic damage the talent keys on, which keeps "
           "it in the same part of the rotation."))

N.append(node(
    "potency", "Potency",
    "Increases the damage of Venom Fang by 15%, and it leaves the target "
    "taking 3% more spell damage for 5 turns.",
    1, -2,
    effects={"ability_venomancer_venom_fang_damage": 0.15},
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["venomancer_venom_fang"],
          "apply_effect": {"effect_id": "venomancer_potency",
                           "name": "Potency", "effect_type": "debuff",
                           "duration": 5, "max_stacks": 1,
                           "stat_mods": {"spell_damage_taken_pct": 3.0},
                           "on_target": True}},
    connect=["withered"],
    source="CoA verbatim: 'Increases the damage dealt by Venom Fang by 15% "
           "and causes it to increase the target's chance to be critically "
           "struck by spells by 3% for 15 seconds.' THERE IS NO "
           "RECIPIENT-SIDE 'CHANCE TO BE CRIT' KEY - crit lives on the "
           "attacker - so it becomes spell damage taken at CoA's own 3%, the "
           "same translation as the Witch Doctor's Hollow Spirit and "
           "Lightning's Sparks. 15 sec is 5 turns."))

N.append(node(
    "withered", "Withered",
    "Increases the damage of Withering Venom by a further 15%.",
    1, 0,
    effects={"ability_venomancer_withering_venom_damage": 0.15},
    connect=["corrosive_toxin"],
    source="CoA verbatim: 'Increases the spell power scaling of Withering "
           "Venom by 15%.' There is no key for how much an ability scales "
           "with spell power - the coefficients live on the ability - so it "
           "is expressed as damage. Deliberately stacks with Venomagus."))

N.append(node(
    "corrosive_toxin", "Corrosive Toxin",
    "Withering Venom bursts for shadow damage as it takes hold.",
    1, 2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["venomancer_withering_venom"],
          "damage_flat": 85, "school": "shadow"},
    connect=["widows_kiss"],
    source="CoA verbatim: 'Withering Venom now deals an additional Shadow "
           "damage at the end of its duration.' NO TRIGGER FIRES WHEN AN "
           "EFFECT EXPIRES - the same wall as the Witch Doctor's Puppeteer's "
           "Threads and Lightning's Godslayer - so the burst lands on the "
           "cast instead of at the end of the window. Same damage, paid "
           "earlier."))

N.append(node(
    "widows_kiss", "Widow's Kiss",
    "Venom Fang quickens you, raising your haste by 20% for 2 turns.",
    1, 4,
    proc={"trigger": "on_damage_cast", "chance": 33, "icd": 0,
          "ability_filter": ["venomancer_venom_fang"],
          "apply_effect": {"effect_id": "venomancer_widows_kiss",
                           "name": "Widow's Kiss", "effect_type": "buff",
                           "duration": 2, "max_stacks": 1,
                           "stat_mods": {"haste": 20.0},
                           "on_target": False}},
    connect=["acidfang"],
    source="CoA verbatim: 'Every 3rd Venom Fang becomes Widow's Kiss, dealing "
           "increased damage and granting you increased haste. Applies 1 "
           "Brood Mark. Bite an enemy for Shadow damage, increasing your "
           "haste by 20% for 4 seconds.' THERE IS NO CAST COUNTER - nothing "
           "tracks 'every 3rd cast of X' - so 'every 3rd' becomes a 33% "
           "chance, which is the same rate without the predictability. CoA's "
           "20% haste kept; 4 sec is 2 turns. Nothing transforms one ability "
           "into another either, so the bite itself is not built."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "acidfang", "Acidfang",
    "Your critical strikes sharpen your fangs, raising your haste by 2% per "
    "stack for 5 turns, stacking 10 times.",
    2, -4,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "venomancer_acidfang",
                           "name": "Acidfang", "effect_type": "buff",
                           "duration": 5, "max_stacks": 10,
                           "stat_mods": {"haste": 2.0},
                           "on_target": False}},
    connect=["essence_of_decay"],
    source="CoA's level 30 passive: 'Periodic damage dealt now has a 40% "
           "chance, and critical strikes a 100% chance, to grant a stack of "
           "Acidfang. The next Rotfang, Withering Venom, or Facemelter within "
           "15 sec has 1% reduced duration and ticks 2% faster, stacking 10 "
           "times.' Periodic damage has no trigger, so only the crit half "
           "fires - at CoA's own 100%. 'Ticks faster with reduced duration' "
           "has no meaning per-turn and nothing empowers a named next cast, "
           "so the payoff becomes haste, which is what ticking faster means "
           "here. CoA's 10 stacks kept; 15 sec is 5 turns."))

N.append(node(
    "essence_of_decay", "Essence of Decay",
    "Your critical strikes spray decay, striking again for shadow damage.",
    2, -2,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "damage_flat": 95, "school": "shadow"},
    connect=["deadly_kiss"],
    source="CoA verbatim: 'Critical strikes with Widow's Kiss now apply 1 "
           "additional Brood Mark.' Brood Marks do not exist, and Widow's "
           "Kiss is not a separate ability here (see that node). Rerouted to "
           "direct damage on a crit, which is what an extra mark bought - a "
           "bigger finisher. 1-turn internal cooldown so a multi-hit turn "
           "does not multiply it. CoA's Death Spray node ('periodic damage "
           "has a 5% chance to remove the Energy cost from your next Venom "
           "Fang and increase its damage by 20%') needs a free-next-cast and "
           "is not built."))

N.append(node(
    "deadly_kiss", "Deadly Kiss",
    "Increases the critical strike damage of Widowmaker and Venom Fang by "
    "50%.",
    2, 0,
    effects={"ability_venomancer_widowmaker_crit_damage": 0.50,
             "ability_venomancer_venom_fang_crit_damage": 0.50},
    connect=["widowmaker_mastery"],
    source="CoA verbatim: 'Increases critical damage dealt by Widow's Kiss, "
           "Widowmaker and Venom Fang by 50% against Poisoned targets.' There "
           "is no key reading whether a target is Poisoned - no effect key "
           "reads a target's debuffs at all - and this spec poisons "
           "everything anyway, so the condition was nearly always true. "
           "Widow's Kiss is not a separate ability. CoA's 50% kept. "
           "ability_*_crit_damage is a FRACTION."))

N.append(node(
    "lethality", "Lethality",
    "Increases the critical strike chance of Widowmaker by 30%.",
    2, 2,
    effects={"ability_venomancer_widowmaker_crit": 30.0},
    connect=["widowmaker_mastery"],
    source="CoA verbatim: 'Increases the critical strike chance of Widow's "
           "Kiss on Diseased targets by 30%.' Widow's Kiss is not a separate "
           "ability and there is no Diseased check, so it is re-pointed at "
           "Widowmaker - the shadow finisher Widow's Kiss fed in CoA. CoA's "
           "30% kept."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "widowmaker_mastery", "Widowmaker",
    "Increases the damage of Widowmaker by 60%.",
    3, -4,
    effects={"ability_venomancer_widowmaker_damage": 0.60},
    connect=["rotting_sores"],
    source="CoA's Widowmaker consumes Brood Marks for five damage tiers: 1 "
           "Mark x1.25 up to 5 Marks x2.60. NONE OF THAT IS EXPRESSIBLE - no "
           "combo-point system, and nothing reads a stack count - so the "
           "ability is priced at roughly its MID-TIER value, 60%, which is "
           "between CoA's 2-mark and 3-mark multipliers. A Stalking "
           "Venomancer will land finishers at a consistent strength rather "
           "than building to a payoff, which is the single biggest thing this "
           "tree loses. Frontier HAS Widowmaker and it requires Spider Form, "
           "which IS live, so the form gate survives even though the marks do "
           "not."))

N.append(node(
    "rotting_sores", "Rotting Sores",
    "Increases the damage of Rotfang by 60% and your damage-over-time spells "
    "by 15%.",
    3, -2,
    effects={"ability_venomancer_rotfang_damage": 0.60,
             "dot_damage": 0.15},
    connect=["shadras_seance"],
    source="CoA verbatim: 'Increases the tick rate of Rotfang by -20% and "
           "allows its periodic damage dealt to critically strike.' Tick rate "
           "has no meaning per-turn, and there is no per-ability 'can crit' "
           "flag - everything can crit here. Both halves become damage, and "
           "the node carries Rotfang's mark-tier pricing as well (CoA: 1 Mark "
           "240 up to 5 Marks 672, so 60% is the mid-tier equivalent)."))

N.append(node(
    "shadras_seance", "Shadra's Seance",
    "Increases the duration of Facemelter by 1 turn and its damage by 50%.",
    3, 0,
    effects={"ability_venomancer_facemelter_damage": 1,
             "ability_venomancer_facemelter_damage": 0.50},
    connect=["virulent_opening"],
    source="CoA verbatim: 'Facemelter now ticks -20% faster and the duration "
           "is increased by 6 sec.' Tick rate is meaningless per-turn; 6 sec "
           "is 2 turns, held to 1 so the node is not the longest dot "
           "extension in the class. The 50% carries Facemelter's own mark-"
           "tier pricing (CoA: 1 Mark 88 up to 5 Marks 245). The small "
           "integer duration keeps this node out of the rank policy."))

N.append(node(
    "virulent_opening", "Virulent Opening",
    "Increases the damage your damage-over-time spells deal by a further 30%.",
    3, 2,
    effects={"dot_damage": 0.30},
    connect=["vulnerability"],
    source="CoA verbatim: 'Increases the periodic damage dealt by your "
           "Facemelter and Rotfang by 30% while the enemy is above 75% "
           "health.' No effect key reads a target's health percentage, so the "
           "condition is dropped. There is no key for one ability's periodic "
           "damage as distinct from its direct damage either, so CoA's 30% "
           "lands on dot_damage generally."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "vulnerability", "Vulnerability",
    "Your critical strikes leave the target taking 10% more spell damage for "
    "5 turns.",
    4, -3,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "venomancer_vulnerability",
                           "name": "Vulnerability", "effect_type": "debuff",
                           "duration": 5, "max_stacks": 1,
                           "stat_mods": {"spell_damage_taken_pct": 10.0},
                           "on_target": True}},
    connect=["corrosive_bile"],
    source="CoA's level 40 passive: 'While Blight Venom is active, your auto "
           "attacks now have a 10% chance to apply it. In addition, your "
           "offensive critical strikes now increase the target's spell damage "
           "taken by 10% for 15 seconds.' The first half needs a 'while buff "
           "active' gate, which does not exist. THE SECOND HALF PORTS "
           "EXACTLY - on_crit is live, spell_damage_taken_pct is the right "
           "key, CoA's 10%, and 15 sec is 5 turns."))

N.append(node(
    "corrosive_bile", "Corrosive Bile",
    "Facemelter readies Widowmaker again, and Widowmaker splashes 40% of its "
    "damage onto up to 2 nearby enemies.",
    4, -1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["venomancer_facemelter"],
          "reset_cooldown": ["venomancer_widowmaker"]},
    connect=["caustic"],
    source="CoA verbatim: 'After using Facemelter, your next Widowmaker "
           "within 15 seconds now deals 20% increased damage and strikes 2 "
           "additional nearby enemies.' Nothing empowers a named next cast, "
           "so the 'after Facemelter' window becomes a cooldown reset on "
           "Widowmaker - the same 'use Facemelter, then Widowmaker' sequence, "
           "enforced by availability rather than by a buff. The splash half "
           "is described but NOT built as a second payload here, because a "
           "proc carries one reset and adding splash_damage to the same proc "
           "would fire it on Facemelter rather than on Widowmaker - so the "
           "description is corrected to promise only the reset."))

N.append(node(
    "caustic", "Caustic",
    "Reduces the cooldown of your finishers by 20%.",
    4, 1,
    effects={f"ability_{a}_cooldown_pct": 0.20 for a in FINISHERS},
    connect=["black_widow"],
    source="CoA verbatim: 'Reduces the cooldown of Noxious Empowerment by -60 "
           "sec.' FRONTIER HAS NO NOXIOUS EMPOWERMENT ability, so the target "
           "cannot exist. Re-pointed at the three Spider Form finishers, "
           "which is where a Stalking Venomancer wants cooldown. POSITIVE "
           "reduces."))

N.append(node(
    "death_spray", "Death Spray",
    "Reduces the cost of Venom Fang and Nerubian Sting by 20%.",
    4, 3,
    effects={f"ability_{a}_cost_pct": 0.20 for a in BUILDERS},
    connect=["black_widow"],
    source="CoA verbatim: 'Periodic damage dealt now has a 5% chance to "
           "remove the Energy cost from your next Venom Fang or Widow's Kiss "
           "within 8 seconds and increase its damage by 20%. Can occur only "
           "once every 2 sec.' Periodic damage has no trigger and nothing "
           "makes a named next cast free, so the chance-based discount "
           "becomes a flat one on the two builders - the same resource "
           "outcome, reliably."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "black_widow", "Black Widow",
    "Increases the damage of Widowmaker by a further 20% and all damage you "
    "deal by 5%.",
    5, -3,
    effects={"ability_venomancer_widowmaker_damage": 0.20,
             "all_damage": 0.05},
    connect=["contagion"],
    source="CoA verbatim: 'Damage dealt to enemies below 35% health now "
           "reduces the cooldown of Noxious Empowerment by 2 sec. In "
           "addition, your Widowmaker now deals 20% increased damage to "
           "enemies below 35% health.' Noxious Empowerment does not exist "
           "and there is no health-threshold key, so both conditions are "
           "dropped. CoA's 20% on Widowmaker is kept and applies always; the "
           "cooldown half becomes flat damage."))

N.append(node(
    "contagion", "Contagion",
    "Your rots burst, splashing 35% of their damage onto up to 3 nearby "
    "enemies.",
    5, -1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ROTS,
          "splash_damage": {"pct": 0.35, "max_targets": 3,
                            "school": "shadow"}},
    connect=["contagion_spread"],
    source="CoA verbatim: 'For 15 seconds, all periodic damage dealt now has "
           "a 30% chance to burst dealing Shadow damage to 8 enemies within 8 "
           "yds.' Periodic damage has no trigger, so it fires off the rots' "
           "casts; the 15-second window has no gate, so it is permanent; and "
           "8 targets is held to 3, since a flat-percentage splash across "
           "eight would be the strongest cleave in the class."))

N.append(node(
    "contagion_spread", "Shadra's Favour",
    "Increases the damage of your finishers by a further 25%.",
    5, 1,
    effects={f"ability_{a}_damage": 0.25 for a in FINISHERS},
    connect=["noxious_empowerment"],
    source="CoA's Blistering Fangs: 'Casting spells that consume Brood Marks "
           "now refunds 30 Energy when used with at least 5 Brood Marks on "
           "your target.' Brood Marks do not exist, there is no Energy to "
           "refund (Venomancer's secondary resource is None), and no key "
           "reads a mark count - so nothing of this talent survives. Renamed "
           "and rebuilt as finisher damage, which is what spending five marks "
           "bought. NOT a faithful copy and flagged as such; CoA's own name "
           "is kept out of it because the mechanic bears no resemblance."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "noxious_empowerment", "Noxious Empowerment",
    "Your finishers enrage you, raising all your damage by 20% and your haste "
    "by 20% for 4 turns.",
    6, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 2,
          "ability_filter": FINISHERS,
          "apply_effect": {"effect_id": "venomancer_noxious_empowerment",
                           "name": "Noxious Empowerment",
                           "effect_type": "buff", "duration": 4,
                           "max_stacks": 1,
                           "stat_mods": {"damage_dealt_pct": 20.0,
                                         "haste": 20.0},
                           "on_target": False}},
    source="CoA verbatim: 'Enrage for 12 sec, increasing your chance to "
           "trigger Venoms by 50%, your Energy regeneration by 100%, and "
           "increasing your damage dealt by 20% for 12 sec.' Frontier has no "
           "Noxious Empowerment ability, so this capstone BUILDS the enrage "
           "as a proc off the finishers rather than unlocking an active. "
           "CoA's 20% damage is kept and the Energy regeneration half becomes "
           "haste - there is no resource regeneration key anywhere, the same "
           "wall that took A Hero's Tale on Guardian Inspiration and the "
           "Witch Doctor's Spirits. 'Chance to trigger Venoms' has no "
           "mechanism. 12 sec is 4 turns, with a 2-turn internal cooldown so "
           "it is a real cooldown rather than permanent. damage_dealt_pct "
           "inside a status effect is percentage POINTS."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. tools/talent_ranks.spread() rescales so a
# ranked node lands on exactly the ceiling it had at one rank, and refuses
# nodes carrying small integer durations and unlock_ability nodes.
#
# Authoring rule, learned the hard way on Guardian Vanguard's Iron Guardian:
# author the CEILING at one rank and let the policy divide it. Hand-authoring
# max_points=3 keeps the ceiling as the PER-RANK value and triples it.
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
    print(f"Venomancer Stalking: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
