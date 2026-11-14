#!/usr/bin/env python3
"""Rebuild Pyromancer's Flameweaving tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_pyromancer_flameweaving.py [--check]

SOURCE: data/reference/coa_worksheets/pyromancer.md and
data/reference/coa/pyromancer.json - 39 real Flameweaving talents from
Ascension's own CoA Builder payload. Role: Healer.

The shipped tree was 23 nodes with SIX procs - the best-off of
Pyromancer's three. This completes Pyromancer.

FIERY FAITH PORTS EXACTLY. CoA's level 40 passive, "increases your spell
critical strike rating by 15% of your Spirit", is a legal conversion:
crit_chance_spell is in STAT_CONVERSION_TARGETS and spirit in
STAT_CONVERSION_SOURCES. A healer whose Spirit buys crit is the spec's
identity, and Scorching Spirit below feeds it.

THE PHOENIX IS NOT A PET, which is lucky. CoA summons one and six talents
read it. Frontier has Phoenix Egg and Phoenix Dive as target_type "party"
ABILITIES instead - nothing in data/abilities/pyromancer.json has a
summon field - so the Phoenix is a party heal you cast, and the talents
that buff it work as ability_* keys. Had it been authored as a pet, those
six nodes would have needed pet_damage/pet_health/pet_armor, which are
DEAD DATA on Pyromancer (see tools/qa_pet_keys.py, written after the
Witch Doctor's Serpent Wards set exactly that trap). The talents that
read the Phoenix DYING (Offering of Executus) still fail - no trigger
fires on a summon's death.

THIS TREE OWNS THREE GATED ABILITIES at tiers 4, 5 and 6 -
kaels_command, sunstrider_array and roaring_pyre - completing
Pyromancer's nine-for-nine pattern. All three preserved and asserted.

HEAT AND EMBERS STILL DO NOT EXIST and this is the third tree they cost.
Lifebinder's Fire triggers on generating an Ember, Sageweaving on
consuming one, Sunstrider Array generates them, and Unfathomably Hot!
generates Heat. All re-pointed.

CONVENTIONS, which do not agree with each other - the healing ones are
the worst in the project:
  healing_power_pct     percentage POINTS, on BOTH sides of the divide
  healing_taken_pct     FRACTION as a talent effect, percentage POINTS
                        inside a status effect
  spirit_pct            percentage POINTS
  shield_pct, splash_heal, leech_pct, ability_*_healing   FRACTION
  smart_heal_pct        PERCENT
  crit_chance_spell, haste, ability_*_crit                PERCENT
  <target>_from_<source>_pct  FRACTION, listed pairs only
  *_cost_pct / *_cooldown_pct  FRACTION, POSITIVE MEANS A REDUCTION

TURN-BASED CUTS. Every cast time (Ember Charm, Sageweaving), "tick rate"
(Burning Crescendo), fear wards (Neltharion's Resolve - no key), and
in-combat mana regeneration (Ashen Priest - no regeneration key exists
at all).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/pyromancer_flameweaving.json"

#: The spec's two direct heals.
HEALS = ["pyromancer_kindle", "pyromancer_cinderheart"]

#: The Phoenix abilities - party-targeted, not a pet.
PHOENIX = ["pyromancer_phoenix_egg", "pyromancer_phoenix_dive"]

#: This tree's three talent-gated abilities.
GATED = {
    "pyromancer_kaels_command",
    "pyromancer_sunstrider_array",
    "pyromancer_roaring_pyre",
}

TREE = {
    "spec_name": "Pyromancer Flameweaving",
    "tree_id": "pyromancer_flameweaving",
    "description": ("Healing fire - a phoenix-keeper who turns Spirit into "
                    "critical heals."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from the 39 real CoA Flameweaving talents (role "
        "Healer), completing Pyromancer. Fiery Faith ports exactly (crit "
        "from Spirit is a legal conversion pair). THE PHOENIX IS NOT A PET - "
        "Frontier has Phoenix Egg and Phoenix Dive as target_type 'party' "
        "abilities, so the six talents reading it work as ability_* keys; had "
        "it been a pet, those nodes would have needed keys that are dead data "
        "on Pyromancer. Owns the last three of Pyromancer's nine gated "
        "abilities, at tiers 4, 5 and 6, preserved and asserted. Heat and "
        "Embers do not exist and this is the third tree they cost."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"pyromancer_flameweaving_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"pyromancer_flameweaving_{c}"
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
    "fiery_faith", "Fiery Faith",
    "Increases your spell critical strike chance by 15% of your Spirit.",
    0, -5,
    effects={"crit_chance_spell_from_spirit_pct": 0.15},
    connect=["scorching_spirit"],
    source="CoA's level 40 passive, verbatim: 'Increases your spell critical "
           "strike rating by 15% of your Spirit.' PORTS EXACTLY - "
           "crit_chance_spell is in STAT_CONVERSION_TARGETS and spirit in "
           "STAT_CONVERSION_SOURCES. A healer whose Spirit buys crit is this "
           "spec's whole identity, and Scorching Spirit below feeds it "
           "directly. A FRACTION."))

N.append(node(
    "scorching_spirit", "Scorching Spirit",
    "Increases your Spirit by 20%.",
    0, -3,
    effects={"spirit_pct": 20.0},
    connect=["ember_charm"],
    source="CoA over 2 ranks: 'Increases your Spirit by 10%.' Doubled for the "
           "two ranks. spirit_pct takes percentage POINTS. Deliberately "
           "adjacent to Fiery Faith, which converts Spirit into crit - the "
           "same builder/converter pairing the Witch Doctor's Staff of the "
           "Coven and Voodoo Power use."))

N.append(node(
    "ember_charm", "Ember Charm",
    "Reduces the mana cost of Kindle and Cinderheart by 15%.",
    0, -1,
    effects={f"ability_{a}_cost_pct": 0.15 for a in HEALS},
    connect=["spirit_of_fire"],
    source="CoA verbatim: 'Reduces the cast time of Cinderheart and Kindle by "
           "15%.' There are no cast times here, so nothing survives as "
           "written. Rerouted to cost, which is what a faster cast buys a "
           "healer - more heals per mana bar. POSITIVE reduces."))

N.append(node(
    "spirit_of_fire", "Spirit of Fire",
    "Increases the absorption of Inferno Barrier and Volcanic Shell by 40%.",
    0, 1,
    effects={"ability_pyromancer_inferno_barrier_duration": 1,
             "ability_pyromancer_volcanic_shell_duration": 1},
    connect=["from_the_ashes"],
    source="CoA over 2 ranks: 'Increases the effectiveness of your absorption "
           "effects by 20%.' Doubled for the two ranks. THERE IS NO GLOBAL "
           "ABSORB-SCALING KEY: my first draft invented "
           "absorb_effectiveness_pct, which audit_talents rejected as read by "
           "no engine code. shield_pct and absorb_pct_max_health are PAYLOAD "
           "fields on a proc, not character stats, so the only live way to "
           "scale an absorb is per-ability through ability_*_potency - which "
           "is what Phoenix Dive uses at tier 3. Written out across the "
           "spec's two other absorbs, Inferno Barrier and Volcanic Shell, so "
           "the three absorb nodes cover different abilities rather than "
           "stacking on one."))

N.append(node(
    "from_the_ashes", "From The Ashes",
    "Increases your healing done by 25%.",
    0, 3,
    effects={"healing_power_pct": 25.0},
    connect=["soothing_flames"],
    source="CoA verbatim: 'Increases your healing done to allies below 35% "
           "health by 25%.' NO EFFECT KEY READS A TARGET'S HEALTH PERCENTAGE "
           "- the working low_health pair on Venomancer Fortitude is about "
           "the CARRIER's own health, not a target's - so the condition is "
           "dropped and CoA's 25% applies always. That is a real buff over "
           "CoA's version, stated rather than hidden, and it sits at tier 0 "
           "accordingly. healing_power_pct takes percentage POINTS."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "soothing_flames", "Soothing Flames",
    "Kindle and Cinderheart leave a lingering warmth, healing the target over "
    "2 turns.",
    1, -4,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": HEALS,
          "apply_effect": {"effect_id": "pyromancer_soothing_flames",
                           "name": "Soothing Flames", "effect_type": "hot",
                           "duration": 2, "potency": 38,
                           "on_target": True}},
    connect=["rekindle"],
    source="CoA verbatim: 'Healing done by Kindle and Cinderheart now "
           "additionally heals the target for 30% of the healing done over 3 "
           "sec.' A trailing heal over 3 sec IS a hot, so this ports in shape "
           "- on_heal_cast with both of CoA's abilities, 3 sec as 2 turns. "
           "The potency is flat because an apply_effect payload cannot read "
           "the triggering heal's amount; leech_pct and bonus_pct are the "
           "only payloads that read it, and neither applies an ongoing "
           "effect."))

N.append(node(
    "rekindle", "Rekindle",
    "Kindle raises your healing done by 5% per stack for 5 turns, stacking "
    "twice.",
    1, -2,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": ["pyromancer_kindle"],
          "apply_effect": {"effect_id": "pyromancer_rekindle",
                           "name": "Rekindle", "effect_type": "buff",
                           "duration": 5, "max_stacks": 2,
                           "stat_mods": {"healing_power_pct": 5.0},
                           "on_target": False}},
    connect=["concentrated_fire"],
    source="CoA verbatim: 'Healing done by Kindle now increases your healing "
           "done on the target 5% for 20 sec, stacking 2 times.' CoA's 5% and "
           "2 stacks kept; 20 sec is 5 turns. The buff lands on the CASTER "
           "rather than per-target, because a proc's apply_effect cannot "
           "track a per-recipient modifier - the same compromise made on "
           "Venomancer Vizier's Mycelial Healing and Worship. INSIDE A STATUS "
           "EFFECT healing_power_pct is still percentage POINTS, same as on a "
           "talent."))

N.append(node(
    "concentrated_fire", "Concentrated Fire",
    "Increases the damage and healing of Cleansing Flames by 20%.",
    1, 0,
    effects={"ability_pyromancer_cleansing_flames_healing": 0.20,
             "ability_pyromancer_cleansing_flames_damage": 0.20},
    connect=["warmth"],
    source="CoA verbatim: 'Increases the damage and healing of Cleansing "
           "Flames by 20%.' Cleansing Flames both damages enemies and heals "
           "allies in CoA, so BOTH keys are authored - one of the few places "
           "an ability genuinely wants an ability_*_healing and an "
           "ability_*_damage together. CoA's Unfathomably Hot! ('each tick "
           "generates 5 additional Heat') is not built: Heat does not exist."))

N.append(node(
    "warmth", "Warmth",
    "Your damage-over-time spells radiate warmth, healing the worst-off ally "
    "for 25% of the damage dealt.",
    1, 2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["pyromancer_ignite", "pyromancer_blaze"],
          "leech_pct": {"pct": 0.25, "smart": True}},
    connect=["living_flame"],
    source="CoA verbatim: 'You now radiate warmth to nearby allies, healing "
           "the lowest health nearby ally equal to 25% of your periodic "
           "damage dealt.' PORTS ALMOST EXACTLY, and it is one of the few "
           "nodes in the audit that needed no reinterpretation: leech_pct "
           "reads the triggering hit's amount, and `smart: true` sends the "
           "healing to the WORST-OFF ALLY rather than the caster - which is "
           "precisely CoA's 'lowest health nearby ally'. CoA's 25% kept. "
           "Periodic damage has no trigger, so it fires off the dots' casts."))

N.append(node(
    "living_flame", "Living Flame",
    "Increases the critical strike chance of Ember Touch by 10%.",
    1, 4,
    effects={"ability_pyromancer_ember_touch_crit": 10.0},
    connect=["flame_bonding"],
    source="CoA verbatim: 'Increases the critical strike chance of Ember "
           "Touch by 10%.' Ports exactly - Ember Touch exists in Frontier. "
           "ability_*_crit is a PERCENT."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "flame_bonding", "Flame Bonding",
    "Reduces the cooldown of Inferno Barrier by 30%.",
    2, -4,
    effects={"ability_pyromancer_inferno_barrier_cooldown_pct": 0.30},
    connect=["lifebinders_fire"],
    source="CoA's level 20 passive: 'Your Inferno Barrier now triggers a -15 "
           "sec reduced cooldown when used on an ally other than yourself.' "
           "NOTHING READS WHO AN ABILITY WAS CAST ON - a talent effect cannot "
           "branch on the target's identity - so the condition is dropped and "
           "the reduction is unconditional. 15 sec is expressed as 30% "
           "against the ability's own cooldown. POSITIVE reduces."))

N.append(node(
    "lifebinders_fire", "Lifebinder's Fire",
    "Your heals stoke the fire, raising your healing done by 3% per stack for "
    "3 turns, stacking 5 times.",
    2, -2,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "pyromancer_lifebinders_fire",
                           "name": "Lifebinder's Fire",
                           "effect_type": "buff", "duration": 3,
                           "max_stacks": 5,
                           "stat_mods": {"healing_power_pct": 3.0},
                           "on_target": False}},
    connect=["ashen_priest"],
    source="CoA verbatim: 'Generating an Ember now increases your healing "
           "done by 3% for 8 sec, stacking 5 times.' EMBERS DO NOT EXIST - "
           "Pyromancer's resource is MANA with no secondary and no ability "
           "carries a `generates` block - so the trigger is re-pointed at "
           "healing, which is what the spec does while generating Embers in "
           "CoA. CoA's 3% and 5 stacks kept; 8 sec is 3 turns."))

N.append(node(
    "ashen_priest", "Ashen Priest",
    "Your critical heals restore mana.",
    2, 0,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "grant_resource": {"resource": "mana", "amount": 70}},
    connect=["sageweaving"],
    source="CoA's level 30 passive: 'Your critical heals now grant allies "
           "Replenishment. In addition, 20% of your mana regeneration "
           "continues while in combat. Replenishment replenishes 5% of "
           "maximum mana per 5 sec for 15 seconds.' Two walls: a proc cannot "
           "grant an effect to allies, and THERE IS NO MANA REGENERATION KEY "
           "AT ALL - the same wall that took Guardian Inspiration's A Hero's "
           "Tale and the Witch Doctor's Spirits. Rebuilt as a direct mana "
           "return to the caster on a critical heal, which is what "
           "Replenishment delivered. Flat, since grant_resource has no "
           "percentage form."))

N.append(node(
    "sageweaving", "Sageweaving",
    "Reduces the mana cost of Kindle and Cinderheart by a further 20%.",
    2, 2,
    effects={f"ability_{a}_cost_pct": 0.20 for a in HEALS},
    connect=["burning_crescendo"],
    source="CoA verbatim: 'Consuming an Ember now reduces the cast time of "
           "your next Cinderheart or Kindle by 15% for 12 sec, stacking 2 "
           "times.' Embers do not exist, there are no cast times, and nothing "
           "empowers a named next cast - three walls. Rerouted to the cost of "
           "the same two abilities, stacking with Ember Charm at tier 0, "
           "which is the throughput the talent bought."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "burning_crescendo", "Burning Crescendo",
    "Increases the healing of Phoenix Egg by 40%.",
    3, -4,
    effects={"ability_pyromancer_phoenix_egg_healing": 0.40},
    connect=["phoenix_dive_mastery"],
    source="CoA verbatim: 'Increases the tick rate of your Phoenix Egg by -2 "
           "sec.' A faster tick has no meaning when ticks are per-turn, so it "
           "becomes healing - what a faster tick delivers. THE PHOENIX IS NOT "
           "A PET HERE: Phoenix Egg is a target_type 'party' ABILITY, so "
           "ability_*_healing reaches it and the whole party benefits. Had it "
           "been authored as a summon, this node would have needed pet keys, "
           "which are dead data on Pyromancer."))

N.append(node(
    "phoenix_dive_mastery", "Phoenix Dive",
    "Increases the absorption of Phoenix Dive by 50%.",
    3, -2,
    effects={"ability_pyromancer_phoenix_dive_duration": 1},
    connect=["lucifrons_rage"],
    source="CoA verbatim: 'Command your Phoenix to swoop to the target ally "
           "and shield allies in their path with fire, absorbing damage for "
           "30 sec, scaling with your Spirit.' Frontier HAS Phoenix Dive as a "
           "party ability and it is NOT gated, so this is not its unlock - "
           "ability_*_potency is the key that scales an absorb, since a shield "
           "is neither damage nor healing. The Spirit scaling lives on the "
           "ability's own coefficients."))

N.append(node(
    "lucifrons_rage", "Lucifron's Rage",
    "Your heals leave allies burning hotter, raising your own fire damage by "
    "15%.",
    3, 0,
    effects={"spell_damage": 0.15},
    connect=["offering_of_executus"],
    source="CoA verbatim: 'Effective healing done by your Phoenix now causes "
           "allies to deal additional Fire damage with all attacks for 6 "
           "seconds.' A TALENT CANNOT GIVE ALLIES A DAMAGE BONUS, and a proc "
           "cannot apply an effect to allies either - apply_effect reaches "
           "the caster or the trigger's target only. So the damage lands on "
           "the Pyromancer and the description says 'your own'. There is no "
           "per-school damage key, so Fire becomes spell_damage; this spec "
           "casts almost nothing else."))

N.append(node(
    "offering_of_executus", "Offering of Executus",
    "Phoenix Egg splashes 50% of its healing across up to 3 of the worst-off "
    "allies.",
    3, 2,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": ["pyromancer_phoenix_egg"],
          "splash_heal": {"pct": 0.50, "max_targets": 3}},
    connect=["kaels_command"],
    source="CoA verbatim: 'When your Phoenix dies or expires, it now heals "
           "all allies within 30 yds equal to its maximum health.' NO TRIGGER "
           "FIRES ON A SUMMON'S DEATH OR ON AN EFFECT EXPIRING - the Phoenix "
           "is not even a summon here - so the death burst cannot exist. "
           "Built as a splash off casting Phoenix Egg instead, which pays the "
           "same healing without waiting for the bird to die. splash_heal "
           "prioritises the worst-off allies."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "kaels_command", "Kael's Command",
    "Teaches Kael's Command, going the Phoenix dormant to radiate healing to "
    "the party.",
    4, -3,
    effects={"unlock_ability": "pyromancer_kaels_command"},
    connect=["neltharions_resolve"],
    source="CoA verbatim: 'Command your Phoenix to go dormant for 10 sec. "
           "While dormant, it radiates healing to nearby allies every 2 sec.' "
           "LOAD-BEARING UNLOCK: pyromancer_kaels_command carries "
           "requires_talent, so without this node it is unobtainable "
           "forever. It is also target_type 'party', so the radiated healing "
           "genuinely reaches every living ally. Kept at tier 4 exactly where "
           "the shipped tree had it, preserving Pyromancer's 4/5/6 pattern."))

N.append(node(
    "neltharions_resolve", "Neltharion's Resolve",
    "Reduces the duration of stuns against you by 25%.",
    4, -1,
    effects={"stun_duration_reduction_pct": 0.25},
    connect=["unfathomably_hot"],
    source="CoA verbatim: 'Place Neltharion's resolve on all party members, "
           "warding them against fear. The next fear effect used against the "
           "target will fail, using up the ward.' THERE IS NO FEAR KEY AND NO "
           "WARD MECHANISM - a one-shot immunity that consumes itself has no "
           "equivalent, cc_immune is permanent while it lasts, and a talent "
           "cannot reach allies. Frontier HAS Neltharion's Resolve as an "
           "ability and it is not gated. Re-pointed at the one "
           "crowd-control key that exists, stun_duration_reduction_pct, read "
           "solely against effects flagged is_stun. A FRACTION where POSITIVE "
           "reduces. NOT a faithful copy - fear and stun are different things "
           "- and flagged as such."))

N.append(node(
    "unfathomably_hot", "Unfathomably Hot!",
    "Increases the healing of Cleansing Flames by 30%.",
    4, 1,
    effects={"ability_pyromancer_cleansing_flames_healing": 0.30},
    connect=["sunstrider_array"],
    source="CoA verbatim: 'Each tick of Cleansing Flames now generates 5 "
           "additional Heat.' Heat does not exist, so there is nothing to "
           "generate. Rerouted to the healing of the same ability, stacking "
           "with Concentrated Fire at tier 1 - which is what more Heat would "
           "have been spent on."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "sunstrider_array", "Sunstrider Array",
    "Teaches Sunstrider Array, a burst window for your healing.",
    5, -3,
    effects={"unlock_ability": "pyromancer_sunstrider_array"},
    connect=["spirit_of_the_phoenix"],
    source="CoA verbatim: 'For 15 sec, you generate 1 Ember every 3 sec and "
           "your Cinderheart generates double the amount of Heat with each "
           "cast.' LOAD-BEARING UNLOCK: pyromancer_sunstrider_array carries "
           "requires_talent. Both halves of what the ability DOES are about "
           "Heat and Embers and so are inert here, but the ability exists and "
           "must remain obtainable, and whatever it does is the ability's "
           "business rather than the talent's. Kept at tier 5."))

N.append(node(
    "spirit_of_the_phoenix", "Spirit of the Phoenix",
    "Your heals shield the target for 20% of the healing done.",
    5, -1,
    proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
          "ability_filter": HEALS,
          "shield_pct": 0.20},
    connect=["roaring_pyre"],
    source="CoA's Living Flame and Spirit of Fire both point at absorbs, and "
           "this node carries the mechanic neither could: shield_pct is a "
           "live payload that converts a share of the triggering heal into an "
           "absorb. A FRACTION. NOT a direct port of any single CoA talent - "
           "it is built from the spec's absorb theme (Phoenix Dive, Inferno "
           "Barrier, Spirit of Fire) to give the tier a real mechanic rather "
           "than a third flat healing scalar, and is flagged as such."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "roaring_pyre", "Roaring Pyre",
    "Teaches Roaring Pyre, and your healing done rises by 20%.",
    6, 0,
    effects={"unlock_ability": "pyromancer_roaring_pyre",
             "healing_power_pct": 20.0},
    source="LOAD-BEARING UNLOCK: pyromancer_roaring_pyre carries "
           "requires_talent, so without this node it is unobtainable "
           "forever. It is target_type 'party' as well. Kept at tier 6, "
           "completing Pyromancer's nine-for-nine gated-ability pattern - "
           "three trees, three gated abilities each, at tiers 4, 5 and 6, "
           "every one accounted for. The flat healing is added because a "
           "capstone that only grants an ability is thin; the same shape as "
           "Incineration's Pyroclasm and Draconic's Death From Above. The "
           "shipped tree's node for this was called Fueling the Fire; renamed "
           "to match the ability it grants, as every other unlock node in "
           "this class does."))


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
    print(f"Pyromancer Flameweaving: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points, {len(GATED)} load-bearing unlocks")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
