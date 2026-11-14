#!/usr/bin/env python3
"""Rebuild Venomancer's Fortitude tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_venomancer_fortitude.py [--check]

SOURCE: data/reference/coa_worksheets/venomancer.md and
data/reference/coa/venomancer.json - 42 real Fortitude talents from
Ascension's own CoA Builder payload. Role: Tank.

THIS TREE WAS THE HEALTHIEST OF THE FOUR and is rebuilt by ADDITION, not
replacement. The shipped version already carried five real procs and
several working mechanics that nothing else in this audit has matched:

  - EXPOSED FLESH, preserved verbatim. A proc on on_damage_taken granting
    10 Rage and stacking a self debuff (+3% physical damage taken, 10
    stacks). It is CoA's actual tank loop - you get hit, you expose
    flesh, you make Rage, you get hit harder - and it works.
  - ADRENAL CARAPACE, preserved. It grants `exposed_flesh_rage_pct`,
    which Exposed Flesh's own grant_resource reads back through
    scale_talent_key. That key is NOT an engine key and greps as dead;
    it is read dynamically by name (status_effects.py:1351), so one
    talent scales another talent's resource grant. The cleanest pattern
    in the whole class and easy to break by "cleaning up" either half.
  - require_form "beetle" on the capstone, which is live.
  - low_health_damage_reduction_pct / low_health_threshold_pct,
    death_threat_retention_pct, stun_duration_reduction_pct - all real
    tank keys, all kept.

So this builder keeps those and spends its effort on the SEVEN DEAD
UNLOCK NODES. Beetle Form, Hivebreak, Locust Swarm, Carapace Crash,
Expulsion, Venomtip Poison and Harden are none of them requires_talent,
so all seven granted abilities the character already had and did nothing.
Only venomancer_barbed_stinger is gated - THE CLASS'S ONLY GATED ABILITY
- and its unlock node is preserved and asserted in main().

WHAT CANNOT BE BUILT. Beetle Slime and Carapace Regeneration are
ground-pool and channelled-drain mechanics with no equivalent. Rage
generation as a stat has no key (rage_generation_pct is dead, and
max_rage is hardcoded 100), which takes Pendo's Charm and half of
Catalyst. Charges have no system (Carapace Regeneration's 3 charges).
"Clears Exposed Flesh stacks to do X, plus 1 sec per stack" - the shape
of four CoA talents - needs a payload that consumes stacks of an
arbitrary effect and reads the count; consumes_stacks_of reads the
caster's own stacks but only extends a DoT's duration, so none of the
four port.

CONVENTIONS, which do not agree with each other:
  all_stats_pct, armor_pct, stamina_pct, max_health_pct (as a TALENT
    effect this one is a FRACTION - see Beetle Endurance)
  physical_damage_taken_pct as a TALENT effect: FRACTION, NEGATIVE
    reduces. Inside a status effect: divided by 100, POSITIVE INCREASES.
    BOTH appear in this tree.
  dodge, hit_rating, ability_*_crit      PERCENT
  ability_*_damage, ability_*_crit_damage, dot_damage   FRACTION
  threat_generation_pct   FRACTION, POSITIVE increases
  *_cost_pct / *_cooldown_pct  FRACTION, POSITIVE MEANS A REDUCTION
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/venomancer_fortitude.json"

#: Beetle Form's Rage-spending strikes.
BEETLE = ["venomancer_hivebreak", "venomancer_carapace_crash",
          "venomancer_chitin_rush"]

#: CoA's tank loop, preserved verbatim from the shipped tree. Granting Rage
#: on being hit AND stacking a self debuff that increases physical damage
#: taken is the whole Fortitude fantasy, and it already worked.
EXPOSED_FLESH_PROC = {
    "trigger": "on_damage_taken", "chance": 50, "icd": 0,
    "grant_resource": {
        "resource": "rage", "amount": 10,
        # Read back by name through get_talent_effect, NOT an engine key.
        # Adrenal Carapace below is what grants it.
        "scale_talent_key": "exposed_flesh_rage_pct",
    },
    "apply_effect": {
        "effect_id": "exposed_flesh_stack", "name": "Exposed Flesh",
        "effect_type": "debuff", "duration": 20, "real_time_seconds": 20,
        "stat_mods": {"physical_damage_taken_pct": 3},
        "max_stacks": 10, "dispel_type": None, "on_target": False,
    },
}

TREE = {
    "spec_name": "Venomancer Fortitude",
    "tree_id": "venomancer_fortitude",
    "description": ("Beetle form and bared chitin - a tank that turns being "
                    "hit into Rage and Rage into retaliation."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from the 42 real CoA Fortitude talents (role "
        "Tank), completing Venomancer. REBUILT BY ADDITION: this tree was "
        "the healthiest of the four and already carried working mechanics "
        "nothing else in the audit matched - Exposed Flesh's Rage loop "
        "(preserved verbatim), Adrenal Carapace scaling it through "
        "scale_talent_key, require_form 'beetle', and the real tank keys "
        "low_health_damage_reduction_pct and death_threat_retention_pct. The "
        "effort went into its SEVEN DEAD UNLOCK NODES, all for non-gated "
        "abilities. barbed_stinger is the class's only gated ability and its "
        "unlock node is preserved and asserted. Not buildable: Beetle Slime "
        "(ground pool), Carapace Regeneration (charges plus a channelled "
        "Rage drain), Rage generation as a stat (rage_generation_pct is "
        "dead), and the four 'clears Exposed Flesh stacks to do X per stack' "
        "talents, which need a payload that consumes and counts stacks of an "
        "arbitrary effect."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"venomancer_fortitude_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"venomancer_fortitude_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "magic_shell", "Magic Shell",
    "Increases all your primary attributes by 15% and your chance to hit by "
    "3%.",
    0, -5,
    effects={"all_stats_pct": 15.0, "hit_rating": 3.0},
    connect=["enchanted_chitin"],
    source="CoA verbatim: 'Level 20 Passive. Increases all primary attributes "
           "by 15% while in Beetle Form. In addition, increases your hit "
           "rating by 3% of all primary attributes.' all_stats_pct is live "
           "and takes percentage POINTS, so CoA's 15% ports. THE BEETLE FORM "
           "GATE IS DROPPED: require_form works on a proc payload and on an "
           "ability, but not as a condition on a flat effects block - so a "
           "form-gated stat bonus cannot be expressed. The hit CONVERSION "
           "cannot be built either (hit_rating is not a conversion target, "
           "the fifth time in this audit), so it is a flat 3%."))

N.append(node(
    "enchanted_chitin", "Enchanted Chitin",
    "Increases your armour by 50%.",
    0, -3,
    effects={"armor_pct": 50.0},
    connect=["reinforced_exoskeleton"],
    source="CoA over 2 ranks: 'Increases your Armor contribution from mail by "
           "25%.' Doubled for the two ranks. No key reads armour by item "
           "class, so it applies to all armour - the Venomancer wears mail "
           "anyway. This is the talent behind Kyle's canon that Beetle Form "
           "multiplies armour from mail to compensate for a shieldless tank; "
           "the multiplication lives here rather than on the form, since a "
           "form cannot gate a flat effect (see Magic Shell). armor_pct takes "
           "percentage POINTS."))

N.append(node(
    "reinforced_exoskeleton", "Reinforced Exoskeleton",
    "Increases your maximum health by 6% and your dodge chance by 6%.",
    0, -1,
    effects={"max_health_pct": 0.06, "dodge": 6.0},
    connect=["hardened_carapace"],
    source="CoA over 2 ranks: 'Increases your maximum health and your dodge "
           "chance by 3%.' Doubled for the two ranks. TWO UNITS IN ONE BLOCK: "
           "AS A TALENT EFFECT max_health_pct is a FRACTION, so 6% is 0.06 - "
           "authoring 6.0 would be 600%, which is what shipped briefly on "
           "Bloodmage Eternal - while `dodge` is a PERCENT rolled against "
           "0-100. Dodge is face value - no DR since 7 Nov 2026."))

N.append(node(
    "hardened_carapace", "Hardened Carapace",
    "Increases your armour by a further 12%.",
    0, 1, ranks=4,
    effects={"armor_pct": 3.0},
    connect=["agitation"],
    source="Kept from the shipped tree, which had this at 4 ranks of 3% "
           "armor_pct. Authored at the PER-RANK 3.0 with its own 4 ranks, so "
           "get_effective_effects() multiplies by points spent to reach 12% - "
           "the description states the ceiling. CoA's own near-duplicate "
           "exoskeleton passives (Empowered, Regrow, Reconstructive) were "
           "consolidated into this and Reinforced Exoskeleton by the Sept "
           "2026 pass, per Kyle's bloat direction, and that consolidation is "
           "kept rather than re-expanded."))

N.append(node(
    "agitation", "Agitation",
    "Dodging an attack generates 3 Rage.",
    0, 3,
    proc={"trigger": "on_avoid", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "rage", "amount": 3}},
    connect=["exposed_flesh"],
    source="CoA verbatim: 'Dodging an attack now generates 3 Rage.' PORTS "
           "EXACTLY - on_avoid is a live trigger (fired from "
           "Character._fire_avoidance_procs alongside on_dodge and on_parry) "
           "and grant_resource takes a flat amount. CoA's 3 Rage kept. The "
           "shipped tree had this node as flat threat_generation_pct instead, "
           "which was not what CoA's talent does at all."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "exposed_flesh", "Exposed Flesh",
    "Hostile attacks against you have a 50% chance to bare your flesh, "
    "generating 10 Rage and increasing your physical damage taken by 3% for "
    "20 seconds, stacking 10 times.",
    1, -4,
    proc=dict(EXPOSED_FLESH_PROC),
    connect=["barbed_stinger"],
    source="PRESERVED VERBATIM from the shipped tree - this is CoA's real "
           "tank loop and it already worked. CoA's tooltip: 'Hostile attacks "
           "against you now have a 50% chance to grant a stack of Exposed "
           "Flesh. Exposed Flesh generates 10 Rage and increases your "
           "Physical Damage taken 3% for 20 seconds, stacking 10 times.' "
           "Note the proc carries BOTH a grant_resource and an apply_effect, "
           "and the debuff lands on the CARRIER (on_target false) because the "
           "downside is yours. INSIDE A STATUS EFFECT "
           "physical_damage_taken_pct is divided by 100 and POSITIVE "
           "INCREASES damage taken, which is why 3 here is a 3% penalty - the "
           "same key on Resilient Shell below is a talent effect where "
           "NEGATIVE reduces. Four CoA talents 'clear Exposed Flesh stacks' "
           "for an effect scaling per stack cleared; no payload consumes "
           "stacks of an arbitrary effect or reads the count, so none of them "
           "are built."))

N.append(node(
    "barbed_stinger", "Barbed Stinger",
    "Teaches Barbed Stinger, flinging a barb that can be ripped back out.",
    1, -2,
    effects={"unlock_ability": "venomancer_barbed_stinger"},
    connect=["vile_fury"],
    source="CoA verbatim: 'Clears Exposed Flesh stacks and flings a Barbed "
           "Stinger into an enemy for 10 sec, plus an additional 1 sec per "
           "cleared stack. Recasting this ability on the same target will rip "
           "the stinger out, pulling them to you and dealing Nature damage, "
           "scaling based on how long the stinger was left in them.' THE ONLY "
           "LOAD-BEARING UNLOCK IN THE WHOLE CLASS: "
           "venomancer_barbed_stinger is the single Venomancer ability "
           "carrying requires_talent, so without this node it is "
           "unobtainable forever. main() asserts it. The stack-clearing, the "
           "pull and the duration-scaled rip all live on the ability's own "
           "behaviour or not at all; the talent only grants it."))

N.append(node(
    "vile_fury", "Vile Fury",
    "Reduces the Rage cost of Hivebreak and Carapace Crash by 20% and "
    "increases your chance to hit by 4%.",
    1, 0,
    effects={"ability_venomancer_hivebreak_cost_pct": 0.20,
             "ability_venomancer_carapace_crash_cost_pct": 0.20,
             "hit_rating": 4.0},
    connect=["resilient_shell"],
    source="CoA over 2 ranks: 'Reduces the Rage cost of Hivebreak and "
           "Carapace Crash by -3 and increases your chance to hit by 2%.' "
           "Doubled for the two ranks. A flat 3 Rage is expressed as a "
           "percentage because costs differ per ability and rank. POSITIVE "
           "reduces, so CoA's minus sign is dropped."))

N.append(node(
    "resilient_shell", "Resilient Shell",
    "Reduces the physical damage you take by 6%.",
    1, 2, ranks=3,
    effects={"physical_damage_taken_pct": -0.02},
    connect=["alacrity"],
    source="Kept from the shipped tree at 3 ranks of -0.02. AS A TALENT "
           "EFFECT physical_damage_taken_pct is a FRACTION where NEGATIVE "
           "reduces, so -0.02 per rank reaches -6% at full investment. The "
           "SAME KEY inside Exposed Flesh's status effect above is divided by "
           "100 and positive increases - both polarities of one key, two "
           "nodes apart, which is why the convention block at the top of this "
           "file spells it out."))

N.append(node(
    "alacrity", "Alacrity",
    "Chitin Rush quickens you, raising your dodge chance by 1% per stack for "
    "2 turns, stacking 8 times.",
    1, 4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["venomancer_chitin_rush"],
          "apply_effect": {"effect_id": "venomancer_alacrity",
                           "name": "Alacrity", "effect_type": "buff",
                           "duration": 2, "max_stacks": 8,
                           "stat_mods": {"dodge": 1.0},
                           "on_target": False}},
    connect=["adrenal_carapace"],
    source="CoA verbatim: 'Damage dealt by Chitin Rush now increases your "
           "dodge chance by 1% for 5 sec, stacking 8 times.' PORTS ALMOST "
           "EXACTLY - CoA's 1% and 8 stacks kept; 5 sec is 2 turns. The "
           "shipped tree had this as a flat 3 ranks of 1% dodge, losing the "
           "ramp entirely. A tank stacking dodge off its own rotation is the "
           "node CoA wrote."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "adrenal_carapace", "Adrenal Carapace",
    "Increases the Rage that Exposed Flesh generates by 20%.",
    2, -4, ranks=2,
    effects={"exposed_flesh_rage_pct": 0.1},
    connect=["cunning"],
    source="PRESERVED from the shipped tree. `exposed_flesh_rage_pct` is NOT "
           "an engine key - it greps as dead - because it is read "
           "DYNAMICALLY BY NAME through get_talent_effect, from Exposed "
           "Flesh's own grant_resource.scale_talent_key "
           "(status_effects.py:1351). So one talent scales another talent's "
           "resource grant, read live on every proc, which means spending or "
           "unspending points here takes effect on the very next hit with no "
           "re-sync. It is the cleanest pattern in the class and trivially "
           "broken by 'cleaning up' either half - deleting this node would "
           "leave Exposed Flesh reading a key nothing grants, and deleting "
           "the scale_talent_key would leave this node dead. Authored at 0.1 "
           "over CoA's 2 ranks, which the rank policy then spreads across 3 "
           "as 0.0667 - so it still reaches the 20% ceiling the description "
           "states, verified at runtime. Writing max_points=2 does NOT keep "
           "it at 2 ranks: spread() rescales anything under 3 that it can "
           "divide, so the per-rank value shown in this file is not the "
           "shipped one. Only nodes already at 3+ ranks, or carrying small "
           "integers, are left alone."))

N.append(node(
    "cunning", "Cunning",
    "Increases the critical strike chance of Chitin Rush by 20% and its "
    "critical strike damage by 10%.",
    2, -2,
    effects={"ability_venomancer_chitin_rush_crit": 20.0,
             "ability_venomancer_chitin_rush_crit_damage": 0.10},
    connect=["natural_weapons"],
    source="CoA verbatim: 'Increases the critical strike chance of Chitin "
           "Rush by 20% and its critical damage by 10%.' Ports exactly. The "
           "shipped tree had Cunning as 5 ranks of flat armor_pct, which is "
           "not what CoA's talent does. Note the units differ in one block: "
           "ability_*_crit is a PERCENT, ability_*_crit_damage a FRACTION."))

N.append(node(
    "natural_weapons", "Natural Weapons",
    "Increases the critical strike chance of your Beetle Form strikes by 10%.",
    2, 0,
    effects={f"ability_{a}_crit": 10.0 for a in BEETLE},
    connect=["chitinous_surge"],
    source="CoA verbatim: 'Increases the critical strike chance of all Beetle "
           "Form abilities by 10%.' No key names a form's abilities as a "
           "group, so the three Rage-spending Beetle strikes are written "
           "out. CoA's 10% kept."))

N.append(node(
    "staggering_blow", "Staggering Blow",
    "Barbed Stinger staggers the enemy, reducing the damage they deal.",
    2, 2, ranks=3,
    proc={"trigger": "on_cast", "chance": 34, "icd": 0,
          "ability_filter": ["venomancer_barbed_stinger"],
          "apply_effect": {"effect_id": "staggering_blow",
                           "name": "Staggered", "effect_type": "debuff",
                           "duration": 2, "max_stacks": 1,
                           "stat_mods": {"damage_dealt_pct": -8.0},
                           "on_target": True}},
    connect=["chitinous_surge"],
    source="Kept from the shipped tree, which paired Barbed Stinger with a "
           "stagger debuff - a real tank mechanic with no direct CoA "
           "equivalent, so it is retained rather than discarded for fidelity. "
           "on_cast rather than on_damage_cast so it fires even when the "
           "stinger is being planted rather than ripped out. 34% chance over "
           "3 ranks reaches 100% at full investment, the project's standard "
           "shape for a guaranteed ranked proc."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "stubborn_exoskeleton", "Stubborn Exoskeleton",
    "Reduces the duration of stuns against you by 15%.",
    3, -4, ranks=3,
    effects={"stun_duration_reduction_pct": 0.05},
    connect=["drown_in_poison"],
    source="PRESERVED from the shipped tree at 3 ranks of 0.05. "
           "stun_duration_reduction_pct is a real tank key, read against "
           "effects flagged is_stun (status_effects.py:699) and floored so a "
           "stun can be shortened but never negated - cc_immune is what does "
           "that. A FRACTION where POSITIVE reduces."))

N.append(node(
    "drown_in_poison", "Drown In Poison",
    "Increases the damage of Venomtip Poison by 30% and of Expulsion by 20%.",
    3, -2,
    effects={"ability_venomancer_venomtip_poison_damage": 0.30,
             "ability_venomancer_expulsion_damage": 0.20},
    connect=["wicked_poison"],
    source="CoA verbatim for both halves: 'Increases the damage of Venomtip "
           "Poison by 30%' and, from Potent Expulsion, 'Increases the damage "
           "dealt by Expulsion by 20%.' Both abilities exist in Frontier and "
           "both had DEAD UNLOCK NODES in the shipped tree - neither is "
           "requires_talent, so those nodes granted abilities the character "
           "already had. Merged into one node with real numbers."))

N.append(node(
    "wicked_poison", "Wicked Poison",
    "Your critical strikes with Beetle Form strikes leave wicked poison, "
    "dealing shadow damage over 2 turns.",
    3, 0,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "ability_filter": BEETLE,
          "apply_effect": {"effect_id": "venomancer_wicked_poison",
                           "name": "Wicked Poison", "effect_type": "dot",
                           "duration": 2, "potency": 40,
                           "damage_school": "shadow", "on_target": True}},
    connect=["slimy"],
    source="CoA verbatim: 'Critical strikes with Chitin Rush, Carapace Crash, "
           "and Hivebreak now apply Wicked Poison. Deals Shadow Damage every "
           "1.5 sec for 6 sec.' PORTS CLOSELY - on_crit with an "
           "ability_filter on exactly CoA's three abilities, and a dot for "
           "CoA's 6 sec as 2 turns. CoA's Beetle Poison node ('allows Wicked "
           "Poison to stack an additional time') is not built: no key "
           "modifies another effect's max_stacks."))

N.append(node(
    "slimy", "Slimy",
    "Taking a hit has a 20% chance to splash slime back, dealing nature "
    "damage over 2 turns.",
    3, 2,
    proc={"trigger": "on_damage_taken", "chance": 20, "icd": 3,
          "apply_effect": {"effect_id": "venomancer_beetle_slime",
                           "name": "Beetle Slime", "effect_type": "dot",
                           "duration": 2, "potency": 30,
                           "damage_school": "nature", "on_target": True}},
    connect=["unbreakable"],
    source="CoA verbatim: 'Direct damage taken now has a 20% chance to create "
           "a pool of Beetle Slime under the enemy. Can only occur once every "
           "3 sec. Beetle Slime deals Nature Damage to up to 10 enemies "
           "within 5 yds every 2 sec for 8 sec.' A GROUND POOL HAS NO "
           "MECHANISM - no ground placement - so the slime becomes a dot on "
           "the attacker, which is where the pool would have been. CoA's 20% "
           "and its 3-second limit both port, the limit as icd 3. CoA's Slimy "
           "Stingers ('Carapace Crash creates a pool under each enemy "
           "struck') is the same mechanic and is not built twice."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "unbreakable", "Unbreakable",
    "While below 35% health, reduces the damage you take by 6%.",
    4, -3, ranks=3,
    effects={"low_health_damage_reduction_pct": 0.02,
             "low_health_threshold_pct": 0.35},
    connect=["beetle_endurance"],
    source="PRESERVED from the shipped tree. BOTH KEYS ARE REAL - "
           "low_health_damage_reduction_pct is read in "
           "entities/character.py and low_health_threshold_pct in "
           "entities/talent_node.py - which makes this one of very few "
           "conditional effects in the whole project that genuinely works. "
           "Health-threshold conditions are otherwise unbuildable (see "
           "Stalking's Virulent Opening and Black Widow, Venom's Venom "
           "Saturation), so this pair is worth knowing about. The reduction "
           "is per-rank and the threshold is not, so the threshold must stay "
           "a flat 0.35 rather than being spread - which is why this node is "
           "authored at its own 3 ranks instead of going through the rank "
           "policy."))

N.append(node(
    "beetle_endurance", "Beetle Endurance",
    "Increases your maximum health by 6%.",
    4, -1, ranks=3,
    effects={"max_health_pct": 0.02},
    connect=["charmed_plating"],
    source="PRESERVED from the shipped tree at 3 ranks of 0.02. AS A TALENT "
           "EFFECT max_health_pct is a FRACTION, so 0.02 per rank reaches 6% "
           "at full investment. Inside a status effect the same key takes "
           "percentage POINTS - the flip that put 0.05% instead of 5% on "
           "Witch Hunter's Black Knight earlier in this audit."))

N.append(node(
    "charmed_plating", "Charmed Plating",
    "Reduces all damage you take by 3% and your chance to be hit by spells "
    "by 2%.",
    4, 1,
    effects={"damage_taken_pct": -0.03, "magic_damage_taken_pct": -0.02},
    connect=["chitinous_surge"],
    source="CoA verbatim: 'Reduces damage taken by all party and raid members "
           "by -3%. Does not stack with similar effects. In addition, reduces "
           "your chance to be hit by spells by -2%.' A TALENT CANNOT REACH AN "
           "ALLY, so the 3% lands on the Venomancer and the description says "
           "'you'. There is no recipient-side 'chance to be hit' key - hit "
           "lives on the attacker - so that half becomes magic damage taken, "
           "the live equivalent. BARE damage_taken_pct IS READ RAW so 3% is "
           "-0.03, while magic_damage_taken_pct as a TALENT effect is also a "
           "fraction where negative reduces."))

N.append(node(
    "chitinous_surge", "Chitinous Surge",
    "Reduces the cooldown of Chitin Rush by 25% and increases its damage by "
    "15%.",
    4, 3,
    effects={"ability_venomancer_chitin_rush_cooldown_pct": 0.25,
             "ability_venomancer_chitin_rush_damage": 0.15},
    connect=["unyielding_will"],
    source="CoA verbatim: 'Reduces the cooldown of Chitin Rush by -3 sec and "
           "increases its damage by 15%.' The damage half ports exactly; 3 "
           "sec is expressed as 25% against the ability's own cooldown. CoA's "
           "Empowered Exoskeleton ('removes the Rage cost of Chitin Rush and "
           "increases its range') is folded in here minus the range, which "
           "means nothing. POSITIVE on a _cooldown_pct reduces."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "unyielding_will", "Unyielding Will",
    "You keep 10% of your threat on death.",
    5, -3, ranks=2,
    effects={"death_threat_retention_pct": 0.05},
    connect=["carapace_regeneration"],
    source="PRESERVED from the shipped tree at 2 ranks of 0.05. "
           "death_threat_retention_pct is read in combat/combat_engine.py and "
           "is a genuinely unusual tank key - it keeps a share of accumulated "
           "threat through a death, so a resurrected tank is not starting "
           "from zero against a boss. No CoA equivalent, retained rather than "
           "discarded for fidelity."))

N.append(node(
    "carapace_regeneration", "Carapace Regeneration",
    "Taking a hit regrows your carapace, reducing the physical damage you "
    "take by 4% per stack for 3 turns, stacking 3 times.",
    5, -1,
    proc={"trigger": "on_damage_taken", "chance": 100, "icd": 1,
          "apply_effect": {"effect_id": "venomancer_carapace_regeneration",
                           "name": "Carapace Regeneration",
                           "effect_type": "buff", "duration": 3,
                           "max_stacks": 3,
                           "stat_mods": {"physical_damage_taken_pct": -4.0},
                           "on_target": False}},
    connect=["charm_of_warding"],
    source="CoA verbatim: '3 Charges, 20 sec recharge. Regenerate your "
           "carapace, reducing your Physical damage taken by -4% and "
           "restoring 1% maximum health every 1 sec, draining 10 Rage every "
           "tick to remain active, stacking 3 times.' THREE WALLS: charges "
           "have no system, there is no periodic trigger for the per-second "
           "heal, and nothing drains a resource per tick to sustain an "
           "effect. Rebuilt as a defensive that stacks from being hit, which "
           "is how a tank would have held it up anyway. CoA's 4% and 3 stacks "
           "kept; 20 sec is 3 turns, with a 1-turn icd so one turn's hits do "
           "not fill all three stacks. INSIDE A STATUS EFFECT "
           "physical_damage_taken_pct is divided by 100 and POSITIVE "
           "increases damage taken, so a reduction is NEGATIVE here - the "
           "opposite sign to Resilient Shell's talent effect."))

N.append(node(
    "charm_of_warding", "Charm of Warding",
    "Taking a hit heals you.",
    5, 1,
    proc={"trigger": "on_damage_taken", "chance": 100, "icd": 1,
          "heal_flat": 55},
    connect=["spider_lord"],
    source="CoA verbatim: 'When a stack of Exposed Flesh is applied you are "
           "now healed for 1% of your maximum health.' No trigger fires when "
           "an effect is APPLIED, so it hangs off the same on_damage_taken "
           "that Exposed Flesh itself uses - which means the two fire "
           "together in practice, exactly as CoA intends. heal_flat is a "
           "flat amount because no payload reads a percentage of maximum "
           "health, the same limit that made Guardian's Veteran of the Third "
           "War and the Witch Doctor's Spiritual Devotee flat. CoA's Reformed "
           "node ('clearing Exposed Flesh stacks restores health based on "
           "stacks cleared') is the per-stack version and is not buildable."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "spider_lord", "Spider Lord",
    "In Beetle Form your strikes generate 2 Rage, and your Beetle Form "
    "strikes hit 30% harder.",
    6, 0,
    effects={f"ability_{a}_damage": 0.30 for a in BEETLE},
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "require_form": "beetle",
          "grant_resource": {"resource": "rage", "amount": 2}},
    source="PRESERVED and extended from the shipped tree. The proc uses "
           "require_form 'beetle', which IS LIVE - one of the few form gates "
           "that works, because require_form is a proc-payload condition "
           "rather than a flat-effect one (which is why Magic Shell's form "
           "gate had to be dropped at tier 0). So this capstone genuinely "
           "only pays out in Beetle Form, closing the Rage loop Exposed Flesh "
           "opens: you get hit for Rage, you spend Rage in form, and striking "
           "in form makes more Rage. The damage half is added here because "
           "the shipped capstone granted nothing but 2 Rage, which is thin "
           "for a tier-6 node."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. tools/talent_ranks.spread() rescales so a
# ranked node lands on exactly the ceiling it had at one rank, and refuses
# nodes carrying small integer durations and unlock_ability nodes.
#
# SEVERAL NODES HERE ARE AUTHORED AT THEIR PER-RANK VALUE with their own
# rank count, preserved from the shipped tree (Hardened Carapace, Resilient
# Shell, Adrenal Carapace, Stubborn Exoskeleton, Unbreakable, Beetle
# Endurance, Unyielding Will, Staggering Blow). The policy skips them because
# max_points is already set, and get_effective_effects() multiplies by points
# spent to reach the ceiling the description states. Unbreakable in
# particular MUST stay per-rank: its threshold key is not a per-rank value
# and spreading it would scale the threshold too.
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
    assert "venomancer_barbed_stinger" in unlocks, (
        "venomancer_barbed_stinger is the ONLY requires_talent ability in "
        "the whole Venomancer class and this tree is its only unlock - "
        "dropping the node makes it unobtainable forever")
    # Exposed Flesh and Adrenal Carapace are two halves of one mechanism.
    scale_users = [n for n in TREE["nodes"]
                   if (n.get("proc") or {}).get("grant_resource", {})
                   .get("scale_talent_key") == "exposed_flesh_rage_pct"]
    scale_granters = [n for n in TREE["nodes"]
                      if "exposed_flesh_rage_pct" in (n.get("effects") or {})]
    assert scale_users and scale_granters, (
        "exposed_flesh_rage_pct is read dynamically by name: Exposed Flesh's "
        "scale_talent_key needs Adrenal Carapace to grant it, and vice "
        "versa. Removing either half silently kills the other.")
    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Venomancer Fortitude: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
