#!/usr/bin/env python3
"""Rebuild Venomancer's Vizier tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_venomancer_vizier.py [--check]

SOURCE: data/reference/coa_worksheets/venomancer.md and
data/reference/coa/venomancer.json - 39 real Vizier talents from
Ascension's own CoA Builder payload. Role: Healer.

The shipped tree was 24 nodes with TWO procs. This completes Venomancer,
the worst-measuring class of the 14 that remained at 88.9% scalar-only
across its four specs.

SPIRITUAL HEALING PORTS WHOLE - both halves. crit_chance_spell AND
healing_power are both in STAT_CONVERSION_TARGETS and intellect is in
STAT_CONVERSION_SOURCES, so CoA's level 20 passive is exact. Venomancer
is now the second class in this audit where three of four specs hang off
a real conversion node (Venom on Intellect to spell damage and haste,
Stalking on Intellect to spell damage, this on Intellect to crit and
healing power).

ALMOST EVERYTHING THIS TREE NAMES EXISTS, which is rare. Shadra's Prayer,
Green Salve, Alkahest, Mending Mist, Shadra's Balm, Rejuvenating Venom,
Antivenom, Blight Antidote, Serpent's Fang and Vizier Form are all real
Frontier abilities - only Shadra's Aid is missing. So this tree needed far
less re-pointing than Wind or Stalking.

WHAT CANNOT BE BUILT. Charges, which Alkahest is built on in CoA (2
charges, 12 sec recharge) and which four talents refresh - there is no
charge system, so every "refreshes a charge" becomes a cooldown reset.
"Your next N casts are free/empowered" (Venom Weaving, Cycle of Rebirth,
Sublime Extraction) needs a charge counter. Per-stack reads (Mycelial
Healing feeding Mycelial Replenishment) need a stack count nothing reads.
And Ritual Healing restores four different secondary resources on a
timer, which needs both a periodic trigger and resource types this class
does not have.

CONVENTIONS, which do not agree with each other - and the healing ones
are the worst in the project:
  healing_power_pct        percentage POINTS (character.py:1295, /100)
  healing_taken_pct as a TALENT effect: FRACTION. Inside a status
    effect: percentage POINTS. BOTH appear in this tree.
  max_mana_pct             FRACTION (character.py:1419, raw)
  crit_chance_spell, haste, ability_*_crit    PERCENT
  ability_*_healing, ability_*_crit_damage, healing_done   FRACTION
  splash_heal, shield_pct  FRACTION
  smart_heal_pct           PERCENT
  bare damage_taken_pct inside a status effect   read RAW
  <target>_from_<source>_pct  FRACTION, listed pairs only
  *_cost_pct / *_cooldown_pct  FRACTION, POSITIVE MEANS A REDUCTION

TURN-BASED CUTS. Every cast time (Shadra's Gift, Book of Shadra's
"instant"), spell pushback, every yard, and "tick rate" (The Antidote).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/venomancer_vizier.json"

#: CoA names these three together for healing bonuses.
BLESSINGS = ["venomancer_shadras_prayer", "venomancer_green_salve",
             "venomancer_alkahest"]

#: And these three for scaling bonuses.
MISTS = ["venomancer_serpents_fang", "venomancer_mending_mist",
         "venomancer_shadras_balm"]

TREE = {
    "spec_name": "Venomancer Vizier",
    "tree_id": "venomancer_vizier",
    "description": ("Shadra's grace - a healer who turns Intellect into "
                    "crit and healing power both."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from the 39 real CoA Vizier talents (role "
        "Healer), completing Venomancer - the worst-measuring class of the "
        "14 that remained, at 88.9% scalar-only across four specs. Spiritual "
        "Healing ports whole: crit_chance_spell and healing_power are both "
        "legal conversion targets from intellect. Almost every ability this "
        "tree names already exists in Frontier (only Shadra's Aid is "
        "missing), so it needed far less re-pointing than Wind or Stalking. "
        "Not buildable: CHARGES (Alkahest is charge-based in CoA and four "
        "talents refresh one - every such talent becomes a cooldown reset), "
        "'your next N casts are free', per-stack reads, and Ritual Healing's "
        "four-resource timer."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"venomancer_vizier_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"venomancer_vizier_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "spiritual_healing", "Spiritual Healing",
    "Increases your spell critical strike chance by 20% of your Intellect "
    "and your healing power by 20% of your Intellect.",
    0, -5,
    effects={"crit_chance_spell_from_intellect_pct": 0.20,
             "healing_power_from_intellect_pct": 0.20},
    connect=["fang_blessing"],
    source="CoA verbatim: 'Level 20 Passive. Increases your spell critical "
           "strike rating and your healing power by 20% of your Intellect.' "
           "PORTS WHOLE - crit_chance_spell and healing_power are both in "
           "STAT_CONVERSION_TARGETS and intellect is in "
           "STAT_CONVERSION_SOURCES, so both halves are legal and CoA's 20% "
           "is kept exactly. Both are FRACTIONS. The same pairing that made "
           "the Witch Doctor's Spirit Healer the cleanest node in Brewing."))

N.append(node(
    "fang_blessing", "Fang Blessing",
    "Increases your spell critical strike chance by 6%.",
    0, -3,
    effects={"crit_chance_spell": 6.0},
    connect=["bountiful_gifts"],
    source="CoA over 2 ranks: 'Increases your critical strike chance by 3%.' "
           "Doubled for the two ranks and routed to the spell side, which is "
           "every ability this spec casts. PERCENT, unlike the conversion "
           "above it which is a fraction."))

N.append(node(
    "bountiful_gifts", "Bountiful Gifts",
    "Increases the healing of Shadra's Prayer, Green Salve and Alkahest by "
    "20%.",
    0, -1,
    effects={f"ability_{a}_healing": 0.20 for a in BLESSINGS},
    connect=["advisors_perfidy"],
    source="CoA over 2 ranks: 'Increases the healing of Shadra's Prayer, "
           "Green Salve, and Alkahest by 10%.' Doubled for the two ranks. All "
           "three abilities exist in Frontier - CoA names this trio together "
           "repeatedly, so they are kept as a group."))

N.append(node(
    "advisors_perfidy", "Advisor's Perfidy",
    "Increases the healing of Serpent's Fang, Mending Mist and Shadra's Balm "
    "by 20%.",
    0, 1,
    effects={f"ability_{a}_healing": 0.20 for a in MISTS},
    connect=["venom_glands"],
    source="CoA over 2 ranks: 'Increases the bonus healing scaling of "
           "Serpent's Fang, Mending Mist, and Shadra's Balm by 10%.' Doubled "
           "for the two ranks. There is no key for how much an ability scales "
           "with healing power - the coefficients live on the abilities - so "
           "it is expressed as healing. CoA's second trio, kept as a group."))

N.append(node(
    "venom_glands", "Venom Glands",
    "Increases your healing done by 15%.",
    0, 3,
    effects={"healing_power_pct": 15.0},
    connect=["fangbinder"],
    source="CoA verbatim: 'Increases your healing done by 15% on allies below "
           "35% health or if they are Poisoned.' NEITHER CONDITION CAN BE "
           "READ - no effect key reads a target's health percentage, and none "
           "reads whether a target carries a debuff - so CoA's 15% applies "
           "always. healing_power_pct takes percentage POINTS "
           "(character.py:1295), unlike max_mana_pct which is raw."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "fangbinder", "Fangbinder",
    "Increases the healing of Serpent's Fang by 50%.",
    1, -4,
    effects={"ability_venomancer_serpents_fang_healing": 0.50},
    connect=["mycelial_healing"],
    source="CoA verbatim: 'Increases the healing of Serpent's Fang by 50% and "
           "Serpent's Fang can no longer miss.' The healing half ports "
           "exactly. 'Can no longer miss' has no key - there is no "
           "per-ability hit guarantee, only the attacker's hit_rating - so it "
           "is dropped. Serpent's Fang is the spec's attack-that-heals, which "
           "is why a healer tree keeps buffing it."))

N.append(node(
    "mycelial_healing", "Mycelial Healing",
    "Your heals build mycelium, raising your healing done by 1% per stack for "
    "10 turns, stacking 8 times.",
    1, -2,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "venomancer_mycelial_healing",
                           "name": "Mycelial Healing", "effect_type": "buff",
                           "duration": 10, "max_stacks": 8,
                           "stat_mods": {"healing_power_pct": 1.0},
                           "on_target": False}},
    connect=["soothing_venoms"],
    source="CoA verbatim: 'All effective healing done now increases your "
           "periodic healing done to an ally by 1% for 30 seconds, stacking 8 "
           "times.' PORTS CLOSELY - on_heal_cast is the right trigger, CoA's "
           "1% and 8 stacks are kept, and 30 sec is 10 turns. The buff lands "
           "on the CASTER rather than per-ally, because a proc's apply_effect "
           "cannot be tracked per recipient. CoA's Mycelial Replenishment "
           "consumes these stacks for a burst, which needs a stack count read "
           "and a consume payload - neither exists - so that node is rebuilt "
           "differently at tier 5."))

N.append(node(
    "soothing_venoms", "Soothing Venoms",
    "Increases the critical healing of Shadra's Prayer by 50%.",
    1, 0,
    effects={"ability_venomancer_shadras_prayer_crit_damage": 0.50},
    connect=["the_antidote"],
    source="CoA over 2 ranks: 'Increases the critical healing of Shadra's "
           "Prayer by 25%.' Doubled for the two ranks. ability_*_crit_damage "
           "is the key that scales a critical heal as well as a critical hit "
           "- there is no separate crit_healing key - and it is a FRACTION."))

N.append(node(
    "the_antidote", "The Antidote",
    "Increases the duration of Rejuvenating Venom by 1 turn and its healing "
    "by 20%.",
    1, 2,
    effects={"ability_venomancer_rejuvenating_venom_duration": 1,
             "ability_venomancer_rejuvenating_venom_healing": 0.20},
    connect=["ritualistic"],
    source="CoA verbatim: 'Increases the duration of Rejuvenating Venom by 2 "
           "sec and increases its tick rate by -30%.' 2 sec is a turn. Tick "
           "rate has no meaning per-turn, so that 30% becomes healing - what "
           "a faster tick delivers. The small integer duration keeps this "
           "node out of the rank policy's reach."))

N.append(node(
    "ritualistic", "Ritualistic",
    "Casting Green Salve restores some of your mana.",
    1, 4,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": ["venomancer_green_salve"],
          "grant_resource": {"resource": "mana", "amount": 60}},
    connect=["alkahest_mastery"],
    source="CoA verbatim: 'Casting Green Salve now also refunds you 20% of "
           "your base mana.' grant_resource takes a FLAT `amount` only - "
           "there is no percentage-of-maximum form - so 20% cannot scale with "
           "level. 60 is roughly 20% of a mid-level Venomancer's pool and "
           "less at 60, the same compromise made on the Witch Doctor's "
           "Spiritual Devotee."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "alkahest_mastery", "Alkahest",
    "Increases the healing of Alkahest by 40% and reduces its cooldown by "
    "25%.",
    2, -4,
    effects={"ability_venomancer_alkahest_healing": 0.40,
             "ability_venomancer_alkahest_cooldown_pct": 0.25},
    connect=["good_venom"],
    source="CoA verbatim: 'Bless an ally with Shadra's grace, healing them "
           "and extending the duration of Shadra's Prayer on them by 9 sec. 2 "
           "Charges, 12 sec recharge.' Frontier HAS Alkahest, so this is not "
           "its unlock - the shipped tree's unlock node for it did nothing, "
           "since Alkahest is not requires_talent. THERE IS NO CHARGE SYSTEM, "
           "so the two charges become a shorter cooldown, and the duration "
           "extension on another effect has no payload. POSITIVE on a "
           "_cooldown_pct reduces."))

N.append(node(
    "good_venom", "Good Venom",
    "Rejuvenating Venom splashes 50% of its healing onto the worst-off ally.",
    2, -2,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": ["venomancer_rejuvenating_venom"],
          "splash_heal": {"pct": 0.50, "max_targets": 1}},
    connect=["worship"],
    source="CoA verbatim: 'Rejuvenating Venom will now affect 1 additional "
           "nearby ally.' NO KEY ADDS TARGETS TO AN ABILITY, so it becomes "
           "splash_heal at CoA's one extra ally. splash_heal already "
           "prioritises the worst-off ally, which is what a healer wants. "
           "CoA's Spirit of the Jungle ('increases the proc chance of "
           "Rejuvenating Venom by 10%') modifies the ability's own internal "
           "proc rate, which no key reaches, and is not built."))

N.append(node(
    "worship", "Worship",
    "Your critical heals raise your healing done by 10% for 2 turns.",
    2, 0,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "venomancer_worship",
                           "name": "Worship", "effect_type": "buff",
                           "duration": 2, "max_stacks": 1,
                           "stat_mods": {"healing_power_pct": 10.0},
                           "on_target": False}},
    connect=["shadras_presence"],
    source="CoA verbatim: 'Allows all critical heals to increase periodic "
           "healing the target receives from you by 10% for 5 sec.' on_crit "
           "fires on a critical HEAL as well as a hit, so the trigger is "
           "right. The buff lands on the caster rather than per-target, since "
           "a proc cannot track a per-recipient modifier. CoA's 10% kept; 5 "
           "sec is 2 turns. INSIDE A STATUS EFFECT healing_power_pct is still "
           "percentage POINTS, same as on a talent - unlike healing_taken_pct "
           "below, which flips."))

N.append(node(
    "shadras_presence", "Shadra's Presence",
    "Increases the healing you receive by 6%.",
    2, 2,
    effects={"healing_taken_pct": 0.06},
    connect=["melioration"],
    source="CoA verbatim: 'Allies within 100 yds receive 6% more healing. Does "
           "not stack with similar effects. In addition, your Antivenom now "
           "dispels 1 additional effect.' A TALENT CANNOT REACH AN ALLY - "
           "get_talent_effects() reads only the character's own trees - so "
           "the 6% lands on the Venomancer and the description says 'you'. No "
           "key changes how many effects a dispel removes. AS A TALENT EFFECT "
           "healing_taken_pct is a FRACTION, so 6% is 0.06; inside a status "
           "effect the same key is percentage POINTS, which is the flip that "
           "briefly shipped 1000% on Bloodmage Eternal."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "melioration", "Melioration",
    "Serpent's Fang resets the cooldown of Alkahest.",
    3, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["venomancer_serpents_fang"],
          "reset_cooldown": ["venomancer_alkahest"]},
    connect=["lifemender"],
    source="CoA verbatim: 'Your Serpent's Fang now refreshes a charge of "
           "Alkahest.' There is no charge system, so refreshing a charge "
           "becomes a full cooldown reset - the single-charge equivalent, the "
           "same translation as Guardian Gladiator's Supremacy. "
           "reset_cooldown as a BARE LIST means a full reset. on_damage_cast "
           "because Serpent's Fang is an attack that happens to heal."))

N.append(node(
    "lifemender", "Lifemender",
    "Serpent's Fang splashes 45% of its healing across up to 3 of the "
    "worst-off allies.",
    3, -2,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": ["venomancer_serpents_fang"],
          "splash_heal": {"pct": 0.45, "max_targets": 3}},
    connect=["venomcult_scrolls"],
    source="CoA verbatim: 'Your Serpent's Fang now heals up to 5 additional "
           "nearby allies and Alkahest now heals an additional nearby "
           "target.' splash_heal carries the first half; 3 targets rather "
           "than CoA's 5, because a flat-percentage splash across five is the "
           "strongest raid heal in the tree and this is only tier 3. The "
           "Alkahest half would need a second proc on a different filter and "
           "is dropped rather than merged, since one proc's splash fires on "
           "its own trigger."))

N.append(node(
    "venomcult_scrolls", "Venomcult Scrolls",
    "Increases the healing of Green Salve by 50% and reduces its cooldown by "
    "20%.",
    3, 0,
    effects={"ability_venomancer_green_salve_healing": 0.50,
             "ability_venomancer_green_salve_cooldown_pct": 0.20},
    connect=["widows_watch"],
    source="CoA verbatim: 'Reduces the cooldown of Green Salve by -2 sec and "
           "increases the healing done at the end of the duration by 50%.' "
           "The 50% ports; there is no key for healing 'at the end of the "
           "duration' specifically, so it applies to the ability's healing. 2 "
           "sec is expressed as 20% against its own cooldown. CoA's Book of "
           "Shadra ('doubles the duration, cooldown and healing of Green "
           "Salve, and it now seeks another ally every 6 sec') needs a "
           "periodic retarget and is not built."))

N.append(node(
    "widows_watch", "Widow's Watch",
    "Increases the healing of Mending Mist by 40%.",
    3, 2,
    effects={"ability_venomancer_mending_mist_healing": 0.40},
    connect=["sage"],
    source="CoA verbatim: 'Allies affected by Shadra's Balm now have a 20% "
           "increased chance to resist poison and curse effects.' THERE IS NO "
           "RESIST-CHANCE KEY for a debuff school - the only duration-"
           "reduction key is stun_duration_reduction_pct, read solely against "
           "is_stun effects - so nothing of this talent is buildable as "
           "written. Re-pointed at Mending Mist, the spec's party heal "
           "(target_type 'party', so it genuinely reaches every ally), "
           "keeping the node in the raid-support half of the tree."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "sage", "Sage",
    "Alkahest splashes 40% of its healing onto the worst-off ally.",
    4, -3,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": ["venomancer_alkahest"],
          "splash_heal": {"pct": 0.40, "max_targets": 1}},
    connect=["toxic_communion"],
    source="CoA verbatim: 'Direct healing done by Alkahest now spreads an "
           "active Shadra's Balm from the primary target to a nearby ally.' "
           "SPREADING AN EXISTING EFFECT TO A NEW TARGET IS NOT A PAYLOAD - "
           "apply_effect lands on the trigger's own target - the same wall "
           "that turned the Witch Doctor's Malignant into a splash. Built as "
           "the extra healing the spread delivered."))

N.append(node(
    "toxic_communion", "Toxic Communion",
    "Increases the duration of Shadra's Balm and Mending Mist by 1 turn.",
    4, -1,
    effects={"ability_venomancer_shadras_balm_duration": 1,
             "ability_venomancer_mending_mist_duration": 1},
    connect=["venom_fanatic"],
    source="CoA verbatim: 'Extend the duration of Shadra's Balm and Mending "
           "Mist by 15 sec on all allies within 30 yds.' No payload extends a "
           "live effect, so it is built as a flat duration bonus on both "
           "abilities - which, because Mending Mist is target_type 'party', "
           "does reach every ally. 15 sec would be 5 turns; held to 1 so one "
           "node is not worth more than the rest of the tier combined. The "
           "small integers keep this node out of the rank policy."))

N.append(node(
    "venom_fanatic", "Venom Fanatic",
    "Serpent's Fang splashes 50% of its damage onto up to 2 nearby enemies.",
    4, 1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["venomancer_serpents_fang"],
          "splash_damage": {"pct": 0.50, "max_targets": 2,
                            "school": "nature"}},
    connect=["sublime_extraction"],
    source="CoA verbatim: 'Your Serpent's Fang now strikes 2 additional "
           "nearby enemies.' No key adds targets, so splash_damage at CoA's "
           "two. A healer tree carrying a damage node is correct here: "
           "Serpent's Fang both damages and heals, and three other nodes in "
           "this tree already buff it."))

N.append(node(
    "sublime_extraction", "Sublime Extraction",
    "Casting Green Salve resets the cooldown of Serpent's Fang.",
    4, 3,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": ["venomancer_green_salve"],
          "reset_cooldown": ["venomancer_serpents_fang"]},
    connect=["occultist"],
    source="CoA verbatim: 'Casting Green Salve now resets the cooldown of "
           "Serpent's Fang and removes the cost of your next Serpent's Fang "
           "for 8 seconds.' The reset ports exactly. The free-next-cast half "
           "needs a charge counter, which does not exist - the same wall as "
           "Venom Weaving and Cycle of Rebirth, neither of which is built."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "occultist", "Occultist",
    "Your heals have a 30% chance to reset the cooldown of Alkahest.",
    5, -3,
    proc={"trigger": "on_heal_cast", "chance": 30, "icd": 0,
          "ability_filter": ["venomancer_green_salve",
                             "venomancer_serpents_fang"],
          "reset_cooldown": ["venomancer_alkahest"]},
    connect=["mycelial_replenishment"],
    source="CoA's level 40 passive: 'Casting Green Salve or Serpent's Fang "
           "now has a 30% chance to refresh a charge of Alkahest.' PORTS "
           "ALMOST EXACTLY - CoA's 30% and both named abilities, with the "
           "charge refresh becoming a cooldown reset as elsewhere. "
           "Deliberately stacks with Melioration at tier 3, which resets it "
           "outright off Serpent's Fang, as CoA's two do."))

N.append(node(
    "vizier_form", "Vizier Form",
    "Teaches Vizier Form, the spec's healing shape.",
    5, -5,
    effects={"unlock_ability": "venomancer_vizier_form_ability"},
    connect=["mycelial_replenishment"],
    source="CoA's own description for this node is the unresolved token "
           "'$bc'. LOAD-BEARING UNLOCK, and newly so: Kyle's call on 5 Nov "
           "2026 was that the healing and DPS forms should be level-40 "
           "talents 'like Tree of life or moonkin', while Spider Form and "
           "Beetle Form stay 'learnt via level up' like Bear and Cat. So "
           "venomancer_vizier_form_ability now carries requires_talent at "
           "level_req 40, and without this node it is unobtainable forever. "
           "Placed at tier 5, which opens at 25 points and so is reachable at "
           "level 40; tier 6 needs 30. This is the Tree of Life of the pair - "
           "a healer's dedicated form, taken deep in the healing tree rather "
           "than handed to every Venomancer at level 40 as it was before."))

N.append(node(
    "mycelial_replenishment", "Mycelial Replenishment",
    "Your critical heals restore mana and raise your critical healing by 20% "
    "for 3 turns.",
    5, -1,
    proc={"trigger": "on_crit", "chance": 100, "icd": 2,
          "grant_resource": {"resource": "mana", "amount": 80},
          "apply_effect": {"effect_id": "venomancer_mycelial_replenishment",
                           "name": "Mycelial Replenishment",
                           "effect_type": "buff", "duration": 3,
                           "max_stacks": 1,
                           "stat_mods": {"crit_chance_spell": 20.0},
                           "on_target": False}},
    connect=["serpent_lords_ritual"],
    source="CoA verbatim: 'Increases your critical strike chance and critical "
           "healing done by 20% for 20 seconds and instantly restore 30% of "
           "your maximum mana, but consumes all stacks of Mycelial Healing on "
           "all nearby allies. While active, all periodic critical strikes "
           "heal for an additional 20% of the healing done.' The cost - "
           "consuming Mycelial Healing stacks - cannot be expressed, because "
           "no payload consumes stacks of an arbitrary effect and nothing "
           "reads the count. So the upside is granted without the trade, "
           "which is stated rather than hidden, and held behind a 2-turn "
           "internal cooldown so it is a cooldown rather than permanent. The "
           "mana is flat, since grant_resource has no percentage form."))

N.append(node(
    "shadras_aid", "Shadra's Aid",
    "Reduces all damage you take by 15%.",
    5, 1,
    effects={"damage_taken_pct": -0.15},
    connect=["serpent_lords_ritual"],
    source="CoA verbatim: 'Envelop an ally in Shadra's grace, reducing all "
           "damage taken by -20% and causing direct damage taken to restore "
           "3% maximum health for 15 seconds.' FRONTIER HAS NO SHADRA'S AID "
           "ABILITY - the only Vizier ability CoA names that does not exist - "
           "so this cannot be its unlock, and a talent cannot apply a buff to "
           "an ally. The mitigation lands on the Venomancer at a reduced 15%, "
           "which is the spec's only defensive node. BARE damage_taken_pct IS "
           "READ RAW, so 15% is -0.15 - authoring -15.0 would be a 1500% "
           "reduction, the immortality bug from Boltslinger's Evasive. CoA's "
           "Mycelial Synchronization ('casting Shadra's Aid on an ally also "
           "casts it on yourself') is moot once the ability does not exist."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "serpent_lords_ritual", "Serpent Lord's Ritual",
    "Your heals have a 20% chance to draw on the Serpent Lord's Amulet, "
    "raising your haste by 20% for 3 turns.",
    6, 0,
    effects={"ability_venomancer_mending_mist_healing": 0.30},
    proc={"trigger": "on_heal_cast", "chance": 20, "icd": 1,
          "apply_effect": {"effect_id": "venomancer_serpent_lords_amulet",
                           "name": "Serpent Lord's Amulet",
                           "effect_type": "buff", "duration": 3,
                           "max_stacks": 1,
                           "stat_mods": {"haste": 20.0},
                           "on_target": False}},
    source="CoA verbatim: 'Direct healing done now has a 5% chance to grant "
           "you 5 sec of Serpent Lord's Amulet. If already active, triggering "
           "this will instead extend its duration by 5 seconds. This cannot "
           "extend it past its maximum duration. Serpent Lord's Amulet "
           "increases your spell haste by 20% and reduces your mana costs by "
           "-50%.' CoA's 20% haste ports exactly. The mana-cost half is NOT "
           "built as part of the buff: there is no all-spell cost reduction "
           "key readable from a status effect, and halving every cost from a "
           "proc would be the strongest node in the class - so the capstone "
           "pays flat Mending Mist healing instead. No payload extends a live "
           "effect, so re-triggering refreshes rather than extends. The "
           "chance is raised from CoA's 5% to 20% because a 5% proc on a "
           "3-turn buff would almost never be up in a turn-based fight."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. tools/talent_ranks.spread() rescales so a
# ranked node lands on exactly the ceiling it had at one rank, and refuses
# nodes carrying small integer durations and unlock_ability nodes.
#
# Author the CEILING at one rank and let the policy divide it - writing
# max_points yourself does NOT keep that rank count unless it is already 3+,
# and hand-authoring a ceiling at ranks=3 triples it in play (the bug that
# shipped on Guardian Vanguard's Iron Guardian).
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
    assert "venomancer_vizier_form_ability" in unlocks, (
        "venomancer_vizier_form_ability is requires_talent (Kyle's 5 Nov "
        "2026 call: the healing form is a level-40 talent like Tree of Life) "
        "and this tree is its only unlock - dropping the node makes it "
        "unobtainable forever")
    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    pts = sum(n["max_points"] for n in TREE["nodes"])
    print(f"Venomancer Vizier: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
