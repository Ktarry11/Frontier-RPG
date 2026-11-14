#!/usr/bin/env python3
"""Rebuild Primalist's Grovekeeper tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_primalist_grovekeeper.py [--check]

SOURCE: data/reference/coa/primalist.json - 35 real Grovekeeper talents
from Ascension's own CoA Builder payload, the same data allthingscoa.com
presents. Role: SUPPORT. coa_playstyles.json: "Enhancement Shaman +
Mistweaver Monk - a support that also does high DPS and healing".

The shipped tree was 22 nodes: 13 pure scalars, 5 procs, 4 unlocks. Most of
the scalars were 3-5 ranks of "+5-8% healing on one specific heal", stacked
four deep on the same three abilities.

WHAT THE SPEC IS. Damage and healing are the same action. CoA's Grovekeeper
swings a hammer and allies get healed for it (Hammer of Life), heals and
gets faster for it (Battleweaver), crits with its attack and the party gets
topped up (Elemental Cascade), heals a crit and hits harder (Infusion of
Neptulon). Every one of those is a loop between the two halves, and the old
tree had the loop in only two places.

CONVENTIONS, which do not agree with each other:
  leech_pct / splash_heal                       FRACTION (0.20 = 20%)
  smart_heal_pct                                PERCENT (divided by 100)
  damage_dealt_pct / healing_done_pct
    in a status effect                          percentage POINTS
  haste / parry / attack_power in a status      raw ("10.0" = 10)
  all_damage / healing_done as talent effects   FRACTION
  strength_pct / attack_power_pct               percentage POINTS
  magic_damage_taken_pct as a talent effect     FRACTION, NEGATIVE reduces
  *_cost_pct / *_cooldown_pct        FRACTION, POSITIVE MEANS A REDUCTION

THE PARTY-AURA PROBLEM, which hits this spec harder than any other.
Grovekeeper is a SUPPORT spec, and eight of CoA's 35 talents are "all party
and raid members get +X%": Grovekeeper's Presence, Protector's Hand,
Vitality Surge, Infused With Power, Ring of Life, Flourishing Growth, Molten
Fervor's cousin, Sacred Grove's aura. A talent effect applies to its own
character and there is no aura mechanism at all. Each of these keeps the
half that lands on the Primalist and its DESCRIPTION SAYS "your", rather
than promising the party a buff it will never receive. That is the single
biggest fidelity loss in this tree and it is deliberate: a support tooltip
that lies about helping the party is worse than one that is honest about
helping only its caster.

WHAT ELSE IS NOT BUILDABLE, stated rather than faked:
  - Bramblepatch does not exist as an ability, so Keeper of the Grove and
    Grove Tender's CoA versions (both "while inside your Bramblepatch")
    have nothing to attach to.
  - "Your next cast within N sec costs less" needs an ability cost key
    reachable from a status effect, and cost keys are read only through
    get_talent_effects(), which never includes status effects. Primal Power
    is rerouted for that reason.
  - Nothing reads another effect's stack count, so Running on Instinct's
    stack payoff is built as a parallel stacking buff instead.
  - "Increases the number of targets hit" has no key: an ability is
    enemy_aoe or it is not, and aoe_damage only scales ones already
    flagged. Tears of the Earthmother and Blessing of Neptulon's bounce
    are both dropped.

TURN-BASED CUTS. Every yard radius is gone. Ride the Wave is movement speed
only and is dropped entirely rather than repriced into unrelated value.
Spirit Charge is a gap-closer and is built as its healing half only.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/primalist_grovekeeper.json"

SEISMIC = ["primalist_seismic_crash", "primalist_seismic_tremor",
           "primalist_seismic_wave"]

#: The heals this spec actually has, for the nodes CoA writes as "effective
#: healing done".
HEALS = ["primalist_hand_of_the_earthmother", "primalist_seismic_wave",
         "primalist_grove_tender"]

TREE = {
    "spec_name": "Primalist Grovekeeper",
    "tree_id": "primalist_grovekeeper",
    "description": ("Hammer and grove both - every blow landed is healing "
                    "for someone, and every heal makes the next blow land "
                    "harder."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from data/reference/coa/primalist.json "
        "(35 real CoA Grovekeeper talents, role SUPPORT, 'Enhancement "
        "Shaman + Mistweaver Monk'). Replaces a 22-node tree of 13 pure "
        "scalars, most of them 3-5 ranks of '+5-8% healing' stacked four "
        "deep on the same three abilities. The spec's identity is the loop "
        "between damage and healing and the old tree had it in two places. "
        "All 4 unlock nodes are preserved - see "
        "tools/qa_abilities_obtainable.py. NOTE the party-aura problem in "
        "this module's docstring: eight CoA talents here are raid-wide "
        "buffs with no mechanism in this engine, and each keeps only its "
        "self half, with the description worded to match."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source="", active=False):
    entry = {
        "talent_id": f"primalist_grovekeeper_{nid}",
        "name": name,
        "description": desc,
        "node_type": "active" if active else "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"primalist_grovekeeper_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


def unlock(nid, name, ability, blurb, tier, x, *, connect=None, source=""):
    return node(nid, name, f"Learn {name.rstrip('!')}. {blurb}", tier, x,
                effects={"unlock_ability": ability}, connect=connect,
                source=source, active=True)


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "hammer_of_life", "Hammer of Life",
    "20% of the damage you deal is healed onto your most wounded ally.",
    0, -5,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "leech_pct": {"pct": 0.20, "smart": True}},
    connect=["battleweaver"],
    source="CoA verbatim: 'Your melee attacks and abilities now heal up to 3 "
           "nearby allies and damage up to 3 nearby enemies equal to 20% of "
           "the damage dealt.' This is the spec's thesis in one talent. "
           "leech_pct with smart:true routes it to the worst-off ally; the "
           "'up to 3 allies' part is not reachable, because splash_heal sizes "
           "itself from a HEAL and this fires off damage. The mirrored "
           "damage half is dropped rather than doubled up with splash_damage, "
           "which would make a support talent a DPS talent. CoA's 20% kept."))

N.append(node(
    "natures_fury", "Nature's Fury",
    "Your weapon swings have a 20% chance to restore 5% of your maximum mana.",
    0, -3,
    proc={"trigger": "on_weapon_swing", "chance": 20, "icd": 0,
          "grant_resource": {"resource": "mana", "pct_max": 0.05}},
    connect=["battleweaver"],
    source="CoA verbatim: 'Auto attacks now have a 20% chance to deal Weapon "
           "Damage and restore 5% of your maximum mana.' The extra weapon "
           "damage is dropped and the mana kept, which is the half that "
           "matters: Primalist is dual-resource and a Grovekeeper's heals are "
           "mana while its attacks are Rage, so swinging has to pay for "
           "casting. CoA's 20% and 5% both kept."))

N.append(node(
    "tranquil_mind", "Tranquil Mind",
    "Increases your damage and healing done by up to 4%.",
    0, -1, ranks=2,
    effects={"all_damage": 0.02, "healing_done": 0.02},
    connect=["power_hammer"],
    source="CoA verbatim: 'Increases your damage and healing done by 4%.' "
           "Split over CoA's 2 ranks. One of the few genuinely scalar talents "
           "in this tree, and it is the right one to keep scalar because it "
           "is the only node that touches both halves of the spec at once. "
           "Both keys are FRACTIONS as talent effects."))

N.append(node(
    "ancient_power", "Ancient Power",
    "Increases your Strength by up to 5% and your chance to hit by up to 3%.",
    0, 1, ranks=2,
    effects={"strength_pct": 2.5, "hit_rating": 1.5},
    connect=["verdant_warrior"],
    source="CoA verbatim: 'Increases your Strength by 5% and your hit chance "
           "by 3%.' Split over CoA's 2 ranks. Was 3.0/2 per rank, which "
           "overshot CoA at full ranks. strength_pct takes percentage POINTS. "
           "Also carries CoA's Grovekeeper's Presence ('+1% hit for you AND "
           "party and raid members'), whose raid half has no mechanism."))

N.append(unlock(
    "grove_training", "Grove Training", "primalist_grove_tender",
    "A patch of green that keeps mending an ally turn after turn.",
    0, 3, connect=["natures_blessing"],
    source="Kept from the previous tree. CoA's own Grove Tender talent "
           "('while inside your Bramblepatch your Seismic abilities have 80% "
           "reduced cooldown') is not buildable - Bramblepatch does not exist "
           "as an ability here - so this node stays what it is, the unlock "
           "for the hot."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "battleweaver", "Battleweaver",
    "Your healing drives you on, increasing your haste and damage by 2% per "
    "stack for 2 turns, stacking 3 times.",
    1, -5,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "primalist_battleweaver",
                           "name": "Battleweaver", "effect_type": "buff",
                           "duration": 2, "max_stacks": 3,
                           "stat_mods": {"haste": 2.0,
                                         "damage_dealt_pct": 2.0},
                           "on_target": False}},
    connect=["earths_guidance"],
    source="CoA verbatim: 'Effective healing now increases your melee haste "
           "and damage by 2% for 5 seconds, stacking 3 times.' Ports almost "
           "exactly - both stats, CoA's 2% and CoA's 3 stacks. 5 sec is 2 "
           "turns. damage_dealt_pct is the status-effect route to a damage "
           "multiplier (all_damage is read only through get_talent_effects(), "
           "which never includes status effects) and takes percentage POINTS, "
           "while haste beside it is raw. Status stat_mods multiply by "
           "stacks, so 3 stacks is +6 haste and +6% damage."))

N.append(node(
    "power_hammer", "Power Hammer",
    "Your damage generates 3 additional Rage, more reliably per rank.",
    1, -3, ranks=2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "rage", "amount": 3}},
    connect=["crashing_out"],
    source="CoA: 'You now generate 10% more Rage from damage dealt, increased "
           "by 15% while a two-handed weapon is equipped.' The two-hander "
           "condition is dropped: there is no 'while wielding X' gate for an "
           "effect key. NOT built as a rage-generation multiplier, which was "
           "the first draft and was dead: rage generation is hardcoded "
           "(Character.take_damage adds actual * 0.2, CombatEngine adds a "
           "flat amount on attacks) with no talent hook anywhere, so "
           "'rage_generation_pct' read as nothing. Built instead as a flat "
           "grant on the same event, the way Seismically Efficient and "
           "Wildwalker's Rips and Tears already do it. The ranks scale the "
           "proc CHANCE rather than the amount - that is how a multi-rank "
           "proc node works here - so 1 point is a 50% chance and 2 points "
           "is every hit, which is why the description says 'more reliably' "
           "rather than quoting a bigger number."))

N.append(node(
    "hand_of_a_god", "Hand of a God",
    "Reduces the Rage cost of Hand of the Earthmother by 25%.",
    1, -1,
    effects={"ability_primalist_hand_of_the_earthmother_cost_pct": 0.25},
    connect=["resilient_roots"],
    source="CoA: 'Reduces the Rage cost of Hand of the Earthmother by -5.' "
           "Expressed as a percentage rather than a flat 5, because a flat "
           "number set against one ability's cost goes stale the moment that "
           "cost is retuned. POSITIVE is the reduction direction. Also "
           "carries CoA's Primal Power ('casting Seismic Wave makes your next "
           "Hand of the Earthmother cost 50% less within 8 sec'), which is "
           "not buildable: a 'next cast is cheaper' window has to reach an "
           "ability cost key from a status effect, and cost keys are read "
           "only through get_talent_effects()."))

N.append(node(
    "verdant_warrior", "Verdant Warrior",
    "Increases the damage of Wildclaw by 7.5% per rank.",
    1, 1, ranks=2,
    effects={"ability_primalist_wildclaw_damage": 0.075},
    connect=["elemental_cascade"],
    source="CoA verbatim: 'Increases the damage of Wildclaw by 15%.' Split "
           "over CoA's 2 ranks. Wildclaw is this spec's Rage-costed attack "
           "and what Elemental Cascade keys off, so it wants a damage node "
           "feeding it."))

N.append(unlock(
    "eternally_chosen", "Eternally Chosen", "primalist_blessing_of_neptulon",
    "A blessing that keeps the whole party mending.",
    1, 3, connect=["natures_blessing"],
    source="Kept from the previous tree. CoA's own Blessing of Neptulon "
           "talent ('your Hand of the Earthmother now bounces to 1 ally near "
           "the primary target') is not buildable - there is no key that adds "
           "targets to an ability - so this node stays the unlock for the "
           "party hot."))

# ---- tier 2 -------------------------------------------------------------
N.append(unlock(
    "seismic_wave", "Seismic Wave", "primalist_seismic_wave",
    "A wave that heals everyone it rolls past and hurts everything else.",
    2, -5, connect=["earths_guidance"],
    source="CoA: 'Create a seismic wave of healing water around you, healing "
           "up to 8 allies and dealing Nature damage to enemies in a 25 yd "
           "radius.' The ability is damage_and_heal, which is this spec in "
           "one cast. Kept from the previous tree."))

N.append(node(
    "earths_guidance", "Earth's Guidance",
    "Your Seismic spells have a 20% chance to bring all your Seismic spells "
    "a turn closer to ready.",
    2, -3,
    proc={"trigger": "on_damage_or_heal_cast", "chance": 20, "icd": 1,
          "ability_filter": SEISMIC,
          "reset_cooldown": {"abilities": SEISMIC, "turns": 1}},
    connect=["crashing_out"],
    source="CoA verbatim: 'Damage and healing done by Seismic spells now has "
           "a 20% chance to reduce the cooldown of all Seismic spells by -1 "
           "sec.' on_damage_or_heal_cast is the right trigger precisely "
           "because Seismic Wave does both, and it is the one trigger in the "
           "game that catches either. CoA's 20% kept, 1-turn internal "
           "cooldown so it cannot chain."))

N.append(node(
    "resilient_roots", "Resilient Roots",
    "Reduces the cost of your healing by 4% per rank.",
    2, -1, ranks=3,
    effects={"heal_cost_pct": 0.04},
    connect=["infusion_of_neptulon"],
    source="Not a CoA node - kept from the previous tree at 2% -> 4%. A "
           "support that heals on mana while fighting on Rage needs a mana "
           "efficiency pick, and this tier is otherwise all procs. "
           "heal_cost_pct is the alias of healing_spell_cost_pct and positive "
           "is the reduction direction."))

N.append(node(
    "natures_blessing", "Nature's Blessing",
    "Seismic Wave leaves its healing working, mending the target for 3 more "
    "turns.",
    2, 2,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": ["primalist_seismic_wave"],
          "apply_effect": {"effect_id": "primalist_natures_blessing",
                           "name": "Nature's Blessing", "effect_type": "hot",
                           "duration": 3, "potency": 28,
                           "on_target": True}},
    connect=["sacred_grove"],
    source="CoA verbatim: 'Healing allies with Seismic Wave now heals them "
           "for an additional 20% of the healing done every 3 sec for 9 sec.' "
           "9 sec is 3 turns and 3 sec is one tick, so the shape ports. A "
           "proc-applied hot takes a flat potency - there is no 'percentage "
           "of the triggering heal' form for apply_effect, unlike shield_pct "
           "and splash_heal - so 20% of a Seismic Wave is approximated as 28 "
           "per turn."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "crashing_out", "Crashing Out",
    "Increases the damage of Seismic Crash by 30%.",
    3, -4,
    effects={"ability_primalist_seismic_crash_damage": 0.30},
    connect=["thorns"],
    source="CoA verbatim: 'Increases the damage of Seismic Crash by 30%.' "
           "Already a scalar in CoA, so it stays one. Also carries CoA's "
           "Tears of the Earthmother ('increases the amount of targets hit by "
           "Seismic Spike by 4'), which has no key - target counts are a "
           "property of the ability, not a talent bonus - and names an "
           "ability Frontier does not have."))

N.append(node(
    "elemental_cascade", "Elemental Cascade",
    "Critical strikes with Wildclaw wash healing over your most wounded ally.",
    3, -2,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "ability_filter": ["primalist_wildclaw"],
          "smart_heal_pct": 40},
    connect=["infusion_of_neptulon"],
    source="CoA verbatim: 'Critical strikes with Wildclaw now unleash an "
           "Elemental Cascade: restores health to allies in a 12 yd radius "
           "around you.' The radius is gone and the heal routes to the "
           "worst-off ally via smart_heal_pct, which is the payload for "
           "exactly that. NOTE it is a PERCENT - status_effects.py divides by "
           "100 - unlike splash_heal and leech_pct beside it, which are "
           "fractions. 40 means 40% of the crit that triggered it."))

N.append(unlock(
    "sacred_grove", "Sacred Grove", "primalist_sacred_grove",
    "Raise a grove that mends everyone standing in it.",
    3, 0, connect=["ring_of_life"],
    source="CoA: 'Create a Sacred Grove for 16 sec, instantly healing all "
           "nearby party and raid members. While active, up to 12 allies in "
           "the grove receive 25% increased healing, and regain 3% of their "
           "missing health, Rage, and mana every 2 sec.' The ability itself "
           "is a party hot, which covers the healing; the increased-healing "
           "aura and the resource regeneration have no mechanism. Kept from "
           "the previous tree, where this unlock was confusingly named Ring "
           "of Life."))

N.append(node(
    "douse", "Douse",
    "Your Seismic spells leave the enemy taking 4% more magic damage for 3 "
    "turns.",
    3, 2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": SEISMIC,
          "damage_flat": 40, "school": "frost",
          "apply_effect": {"effect_id": "primalist_douse",
                           "name": "Douse", "effect_type": "debuff",
                           "duration": 3, "max_stacks": 1,
                           "stat_mods": {"magic_damage_taken_pct": 4.0},
                           "on_target": True}},
    connect=["ring_of_life"],
    source="CoA verbatim: 'Striking an enemy with Seismic spells now deals an "
           "additional Frost damage and reduces all resistances by 75 and "
           "increases their Magic damage taken by -2% for 10 seconds.' The "
           "flat Frost damage and the magic-vulnerability both port; the "
           "resistance reduction is dropped because there is no "
           "recipient-side all-resistance key, and magic damage taken is "
           "already the thing that reduction was for. 10 sec is 3 turns. "
           "Raised 2% -> 4% because the resistance half is gone. In a status "
           "effect this key is percentage POINTS and POSITIVE means MORE "
           "damage taken - the opposite sign to the same key as a talent "
           "effect, which is the trap Call of the Mountain documents."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "infusion_of_neptulon", "Infusion of Neptulon",
    "Critically healing an ally increases your attack power by 15% for 3 "
    "turns.",
    4, -3,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "ability_filter": HEALS,
          "apply_effect": {"effect_id": "primalist_infusion_of_neptulon",
                           "name": "Infusion of Neptulon",
                           "effect_type": "buff", "duration": 3,
                           "max_stacks": 1,
                           "stat_mods": {"attack_power_pct": 15.0},
                           "on_target": False}},
    connect=["running_on_instinct"],
    source="CoA verbatim: 'Critically healing an ally now increases your "
           "attack power by 15% for your next 3 attacks. Lasts 12 seconds.' "
           "The 'next 3 attacks' charge counter has no mechanism - effects "
           "expire on turns, not on uses - so it is the 12-second window "
           "alone, which is 3 turns either way. CoA's 15% kept. This is the "
           "other direction of the spec's loop: Hammer of Life turns damage "
           "into healing, this turns healing into damage."))

N.append(node(
    "thorns", "Thorns",
    "Taking physical damage has a 10% chance to wrap the attacker in thorns, "
    "dealing nature damage over 2 turns.",
    4, -1,
    proc={"trigger": "on_damage_taken", "chance": 10, "icd": 1,
          "apply_effect": {"effect_id": "primalist_thorns",
                           "name": "Thorns", "effect_type": "dot",
                           "duration": 2, "potency": 45,
                           "damage_school": "nature", "on_target": True}},
    connect=["running_on_instinct"],
    source="CoA: 'Physical damage dealt or taken now has a 10% chance to "
           "unleash Thorns on an enemy: create thorns around an enemy, "
           "rooting them and dealing Nature Damage over 6 seconds. Direct "
           "damage taken may end this effect.' The root is positional and "
           "dropped. Built on damage TAKEN only rather than both halves: "
           "'dealt or taken' would need two procs on one node, and the taken "
           "side is the one that reads as thorns. CoA's 10% kept with a "
           "1-turn internal cooldown. 6 sec is 2 turns."))

N.append(node(
    "ring_of_life", "Ring of Life",
    "Reduces the magic damage you take by 10% and increases your healing "
    "done by 6%.",
    4, 1,
    effects={"magic_damage_taken_pct": -0.10, "healing_done": 0.06},
    connect=["ancient_of_lore"],
    source="CoA verbatim: 'Allies within 40 yds receive 6% increased healing. "
           "Does not stack with similar effects. In addition, your Magic "
           "damage taken is reduced by 10%.' The aura half has no mechanism, "
           "so the 6% applies to the Grovekeeper's own healing done and the "
           "description says 'your'. NEGATIVE reduces for "
           "magic_damage_taken_pct as a TALENT effect - the opposite sign to "
           "the same key inside a status effect, which Douse above uses "
           "positively to INCREASE damage taken. Both are correct; the key "
           "simply means different directions in the two places."))

N.append(node(
    "vitality_surge", "Vitality Surge",
    "Your healing has a 25% chance to quicken you, increasing your haste by "
    "5% for 3 turns.",
    4, 3,
    proc={"trigger": "on_heal_cast", "chance": 25, "icd": 2,
          "apply_effect": {"effect_id": "primalist_vitality_surge",
                           "name": "Vitality Surge", "effect_type": "buff",
                           "duration": 3, "max_stacks": 1,
                           "stat_mods": {"haste": 5.0},
                           "on_target": False}},
    connect=["ancient_of_lore"],
    source="CoA: 'All effective healing done now has a 25% chance to increase "
           "the haste of party and raid members by 5% for 20 seconds. Does "
           "not stack with similar effects.' Self-only, for the party-aura "
           "reason in this module's docstring, and the description says "
           "'you'. CoA's 25% and 5% kept; 20 sec cut to 3 turns so it is not "
           "permanently up at a 25% roll per heal. Also carries CoA's Infused "
           "With Power, which is the same talent pointed at crit instead of "
           "haste and would be the same node twice."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "running_on_instinct", "Running on Instinct",
    "Primal Rush builds momentum, increasing your damage by 5% per stack for "
    "4 turns, stacking 5 times.",
    5, -2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["primalist_primal_rush"],
          "apply_effect": {"effect_id": "primalist_running_on_instinct",
                           "name": "Running on Instinct",
                           "effect_type": "buff", "duration": 4,
                           "max_stacks": 5,
                           "stat_mods": {"damage_dealt_pct": 5.0},
                           "on_target": False}},
    connect=["earthmothers_warden"],
    source="CoA: 'Passing through allies with Primal Rush now heals up to 5 "
           "of them and grants a stack of Running on Instinct: damage of "
           "Wildclaw and Seismic spells is increased by 5% for 20 seconds, "
           "stacking 5 times.' The 'passing through allies' heal is "
           "positional and dropped. The stacking damage is built as a "
           "parallel buff, which is the pattern for every per-stack payoff "
           "in this class - nothing reads another effect's stack count. It is "
           "general damage rather than Wildclaw-and-Seismic-only, because "
           "ability_*_damage cannot be reached from a status effect. CoA's 5 "
           "stacks and 5% kept; 20 sec is 4 turns."))

N.append(node(
    "ancient_of_lore", "Ancient of Lore",
    "While below 35% mana, your healing is up to 12% stronger.",
    5, 0, ranks=2,
    effects={"low_mana_healing_pct": 0.06},
    connect=["earthmothers_warden"],
    source="Not a CoA node - kept from the previous tree at 2% -> 6% over 2 "
           "ranks instead of 4. low_mana_healing_pct is the 'desperate' half "
           "of a real conditional the engine reads off the caster's own mana "
           "against low_health_threshold_pct's 35% default, and it matters "
           "for a spec that spends mana healing while spending Rage "
           "fighting."))

N.append(node(
    "earthmothers_warden", "Earthmother's Warden",
    "Reduces the cooldown of your Seismic spells by 15% per rank.",
    5, 2, ranks=2,
    effects={f"ability_{a}_damage": 0.15 for a in SEISMIC},
    # _damage, not _cooldown_pct: ALL THREE Seismic spells have
    # cooldown 0, so a cooldown reduction was silent dead data on every
    # one of them (tools/qa_ability_scoped_fields.py, 6 Nov 2026). All
    # three do deal damage - Crash is damage, Tremor a dot, Wave a
    # damage_and_heal - so _damage lands on each.
    connect=["aftershock"],
    source="CoA verbatim: 'Reduces the cooldown of your Seismic abilities by "
           "-2 sec.' Expressed as a percentage because cooldowns are counted "
           "in turns here. POSITIVE is the reduction direction - authored "
           "negative this would make the spec's rotation SLOWER while its "
           "tooltip promised faster, which is the mistake eight talents in "
           "this project have already made and which the audit now flags. "
           "Written out per ability because there is no key for a named "
           "group."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "aftershock", "Aftershock",
    "Every heal you land also strikes your enemies, and every blow you land "
    "mends your party.",
    6, 0,
    proc={"trigger": "on_damage_or_heal_cast", "chance": 100, "icd": 0,
          "splash_heal": {"pct": 0.25, "max_targets": 5},
          "splash_damage": {"pct": 0.25, "max_targets": 5,
                            "school": "nature"}},
    connect=None,
    source="The capstone, and the only node in the game that fires both "
           "splash payloads off one trigger. on_damage_or_heal_cast catches "
           "either half, so a heal splashes healing to five allies and a hit "
           "splashes Nature damage to five enemies, from the same point. "
           "That is Grovekeeper's whole thesis - damage and healing are the "
           "same action - made literal, and it is the right shape for the "
           "capstone because it is the one place CoA's Hammer of Life "
           "('heal up to 3 nearby allies AND damage up to 3 nearby "
           "enemies') can actually be built in full: at tier 0 that talent "
           "has to pick one side, because leech_pct sizes from damage and "
           "splash_heal sizes from a heal. Here both are available because "
           "the trigger fires on both. Replaces a proc node of the same "
           "name whose payload was a single flat damage roll."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026, asked directly: multi-rank the real mechanics
# rather than padding the tree back out with flat scalars.
#
# Rebuilding a spec from CoA trades multi-rank scalars for single-rank
# mechanics, which is the point - but it also cut this tree's POINT
# CAPACITY to around 31 against a project median of 71, and a character
# earns 56 points by level 60 that a pure-spec build must be able to spend
# in ONE tree. See tools/talent_ranks.py, which does the rescaling so a
# ranked node lands on exactly the ceiling it had at one rank.
#
# Three ranks for every node that can take them. Left at one rank:
#   - unlock nodes, since an ability cannot be learned a third of the way
#   - the tier 6 capstone, which reads as a single decisive pick
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
    unlocks = sum(1 for n in TREE["nodes"] if "unlock_ability" in n["effects"])
    print(f"Primalist Grovekeeper: {len(ids)} nodes, {procs} with procs, "
          f"{unlocks} unlocks")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
