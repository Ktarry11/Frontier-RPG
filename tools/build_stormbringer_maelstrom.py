#!/usr/bin/env python3
"""Rebuild Stormbringer's Maelstrom tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_stormbringer_maelstrom.py [--check]

SOURCE: data/reference/coa_worksheets/stormbringer.md and
data/reference/coa/stormbringer.json - 36 real Maelstrom talents from
Ascension's own CoA Builder payload. Role: DPS.

WHAT THE SPEC IS. The frost-and-water half of Stormbringer: Stormflow
channels, Drown and Deluge control, Torrential Wrath spends Static. CoA
layers a second stacking resource on top called Conductive, and that is
where most of this tree goes wrong here.

WHIRLING MAELSTROM PORTS WHOLE. CoA's level 20 passive - "Increases your
spell haste by 20% of your Intellect" - is a legal conversion: haste is
in STAT_CONVERSION_TARGETS and intellect in STAT_CONVERSION_SOURCES. That
makes three of Stormbringer's and all three Witch Doctor specs now
hanging off a real conversion node, which is how CoA builds its casters.

CONDUCTIVE CANNOT EXIST. Six talents read its stack count - Voltaic
Mastery ("5% per stack"), Hydromatic ("10% per stack"), Kinetic Energy
("casting a spell that consumes Conductive"), Bursting ("increases the
stack value"), Shockingly Powerful ("chance to not consume"), and Deluge
itself ("Consumes Conductive") - and NOTHING READS ANOTHER EFFECT'S STACK
COUNT, nor is there a payload that consumes stacks of an arbitrary
effect. CoA's own Conductive ability description is the unresolved token
'$56', so there is no authoritative text to work from either. Each of the
six is granted flat at its realistic ceiling and says so.

NO EXECUTE GATE FOR A TALENT. Lethal Current wants "+30% crit against
enemies below 20% health". `execute_threshold` is an ABILITY property,
not a talent-settable one, and high_health_damage_threshold_pct is a dead
key - so the condition is dropped and the bonus priced down.

UNLOCK NODES. The old tree carried four - Torrential Wrath, Stormflow,
Deluge and Drown - and NONE of those abilities carries requires_talent,
so all four granted something the character already had and did nothing.
They are replaced with real mechanics on the same abilities. (Contrast
Wind, where five unlocks are load-bearing and asserted.)

CONVENTIONS, which do not agree with each other:
  intellect_pct, armor_pct                 percentage POINTS
  spell_damage, all_damage, dot_damage, crit_damage_spell,
    ability_*_damage, ability_*_crit_damage   FRACTION
  crit_chance_spell, haste, hit_rating,
    ability_*_crit                            PERCENT
  spell_damage_taken_pct inside a status effect: divided by 100,
    POSITIVE INCREASES damage taken
  leech_pct, splash_damage                 FRACTION
  <target>_from_<source>_pct               FRACTION, listed pairs only
  *_cost_pct / *_cooldown_pct  FRACTION, POSITIVE MEANS A REDUCTION

TURN-BASED CUTS. Channelling, which takes the "while channeling
Stormflow" gate off three talents (Unbridled Flow, Storm Synergy, Amped
Flow); every cast time; "ticks 20% faster" (Unstable); interrupt and
silence, which have no keys at all (Mystic Thunder); and immunity
(Thunder Ward).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/stormbringer_maelstrom.json"

#: The spec's frost/water kit.
WATER = ["stormbringer_stormflow", "stormbringer_drown",
         "stormbringer_deluge", "stormbringer_torrential_wrath"]

TREE = {
    "spec_name": "Stormbringer Maelstrom",
    "tree_id": "stormbringer_maelstrom",
    "description": ("Frost, flood and thunder - a caster who drowns the "
                    "field and turns Intellect into speed."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from the 36 real CoA Maelstrom talents (role "
        "DPS), completing Stormbringer - the worst-measuring class of the 15 "
        "that remained, at 89.6% scalar-only. Whirling Maelstrom ports whole "
        "(haste from intellect is a legal conversion pair). CONDUCTIVE, "
        "CoA's second stacking resource, cannot exist: six talents read its "
        "stack count and nothing reads another effect's stack count, and "
        "CoA's own Conductive description is the unresolved token '$56'. All "
        "six are granted flat at their ceiling. The old tree's four unlock "
        "nodes were all for non-gated abilities and did nothing; replaced "
        "with real mechanics."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"stormbringer_maelstrom_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"stormbringer_maelstrom_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "whirling_maelstrom", "Whirling Maelstrom",
    "Increases your spell haste by 20% of your Intellect.",
    0, -5,
    effects={"haste_from_intellect_pct": 0.20},
    connect=["cloudsurfer"],
    source="CoA verbatim: 'Level 20 Passive. Increases your spell haste by "
           "20% of your Intellect.' PORTS WHOLE - haste is in "
           "STAT_CONVERSION_TARGETS and intellect in STAT_CONVERSION_SOURCES, "
           "so this is a legal pair and CoA's 20% is kept exactly. It is a "
           "FRACTION. A caster whose primary stat buys turn speed is the "
           "spec's whole identity, the same shape as the Witch Doctor's three "
           "Spirit conversions."))

N.append(node(
    "cloudsurfer", "Cloudsurfer",
    "Increases the damage of Shock by 20%.",
    0, -3,
    effects={"ability_stormbringer_shock_damage": 0.20},
    connect=["torrential_rage"],
    source="CoA verbatim: 'Increases the damage of Shock by 20%.' Ports "
           "exactly. Shock is the spec's Static builder, so this is its "
           "filler node."))

N.append(node(
    "torrential_rage", "Torrential Rage",
    "Increases the damage of Torrential Wrath and Stormflow by 30%.",
    0, -1,
    effects={"ability_stormbringer_torrential_wrath_damage": 0.30,
             "ability_stormbringer_stormflow_damage": 0.30},
    connect=["disciple_of_thorim"],
    source="CoA over 2 ranks: 'Increases the damage of Torrential Wrath and "
           "Stormflow by 15%.' Doubled for the two ranks and authored as the "
           "full-investment ceiling. Both abilities exist in Frontier."))

N.append(node(
    "disciple_of_thorim", "Disciple of Thorim",
    "Increases your chance to hit by 6%.",
    0, 1, ranks=3,
    effects={"hit_rating": 2.0},
    connect=["hydro_powered"],
    source="CoA over 3 ranks: 'Reduces the cast time of your Torrential Wrath "
           "by 0.2 sec and increases your hit chance by 2%.' There are no "
           "cast times, so only the hit half survives. Authored at CoA's own "
           "PER-RANK 2% with CoA's 3 ranks, which reaches 6% at full "
           "investment - get_effective_effects() multiplies by points spent, "
           "so the per-rank value is what goes in the file and the "
           "description states the ceiling. Authoring 6.0 here with ranks=3 "
           "would have delivered 18%, which is the bug that shipped on "
           "Guardian Vanguard's Iron Guardian earlier today."))

N.append(node(
    "hydro_powered", "Hydro Powered",
    "Increases the critical strike damage of your spells by 35%.",
    0, 3,
    effects={"crit_damage_spell": 0.35},
    connect=["prodigy_of_lei_shen"],
    source="CoA verbatim: 'Increases your spell critical damage by 35%.' "
           "Ports exactly. crit_damage_spell is a FRACTION, unlike "
           "crit_chance_spell which is a PERCENT."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "prodigy_of_lei_shen", "Prodigy of Lei Shen",
    "Increases the critical strike chance of Stormflow by 25%.",
    1, -4,
    effects={"ability_stormbringer_stormflow_crit": 25.0},
    connect=["blessing_of_lei_shen"],
    source="CoA verbatim: 'Allows your Stormflow to critically strike.' There "
           "is no per-ability 'can crit' flag - every ability can crit here - "
           "so the talent has nothing to switch on. Rerouted to crit chance "
           "on the same ability, which is what CoA's version delivers in "
           "practice: Stormflow crits where it did not before."))

N.append(node(
    "blessing_of_lei_shen", "Blessing of Lei Shen",
    "Stormflow heals you for 25% of the damage it deals.",
    1, -2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["stormbringer_stormflow"],
          "leech_pct": {"pct": 0.25}},
    connect=["undertow"],
    source="CoA verbatim: 'Damage dealt by Stormflow now heals you equal to "
           "the damage dealt.' leech_pct is a live payload and reads the "
           "triggering hit's amount, so this is one of the few CoA talents "
           "whose scaling CAN be expressed. Priced at 25% rather than CoA's "
           "100%: full leech on a channelled nuke would make the spec "
           "unkillable in a turn-based fight, where a channel resolves as a "
           "single cast rather than ticking against incoming damage. "
           "FRACTION."))

N.append(node(
    "undertow", "Undertow",
    "Increases the critical strike chance of Drown by 50%.",
    1, 0,
    effects={"ability_stormbringer_drown_crit": 50.0},
    connect=["conduit"],
    source="CoA over 2 ranks: 'Increases the critical strike chance of Drown "
           "by 25%.' Doubled for the two ranks."))

N.append(node(
    "raining_and_pouring", "Raining and Pouring",
    "Increases the critical strike damage of Torrential Wrath and Electrocute "
    "by 30%.",
    1, 2,
    effects={"ability_stormbringer_torrential_wrath_crit_damage": 0.30,
             "ability_stormbringer_electrocute_crit_damage": 0.30},
    connect=["conduit"],
    source="CoA verbatim: 'Increases the critical damage of your Torrential "
           "Wrath and Electrocute by 30%.' Ports exactly. "
           "ability_*_crit_damage is a FRACTION, while ability_*_crit on the "
           "two nodes beside it is a PERCENT - the same tree carries both."))

N.append(node(
    "conduit", "Conduit",
    "Your frost spells leave the target taking 4% more spell damage per "
    "stack for 3 turns, stacking 4 times.",
    1, 4,
    proc={"trigger": "on_damage_cast", "chance": 60, "icd": 0,
          "ability_filter": WATER,
          "apply_effect": {"effect_id": "stormbringer_conduit",
                           "name": "Conduit", "effect_type": "debuff",
                           "duration": 3, "max_stacks": 4,
                           "stat_mods": {"spell_damage_taken_pct": 4.0},
                           "on_target": True}},
    connect=["washed_away"],
    source="CoA verbatim: 'Dealing Frost damage now has a 60% chance to "
           "increase the damage the target takes from Electrocute by 15% for "
           "10 sec, stacking up to 4 times.' THERE IS NO TRIGGER-SIDE DAMAGE-"
           "SCHOOL FILTER - proc['school'] only types a damage_flat payload - "
           "so 'dealing Frost damage' becomes an ability_filter on the spec's "
           "frost kit. And no key makes a target take more damage from ONE "
           "named ability, so it becomes spell damage taken generally, priced "
           "down from 15% to 4% per stack because it now boosts everything "
           "rather than Electrocute alone. CoA's 60% chance and 4 stacks "
           "kept; 10 sec is 3 turns."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "washed_away", "Washed Away",
    "Reduces the cooldown of Drown by 35%.",
    2, -4,
    effects={"ability_stormbringer_drown_cooldown_pct": 0.35},
    connect=["flow_of_wrath"],
    source="CoA verbatim: 'Reduces the cooldown of Drown by -15 sec.' "
           "Expressed as a percentage because CoA's 15 seconds is measured "
           "against a 1-minute cooldown that does not exist in those units "
           "here. POSITIVE reduces, so CoA's minus sign is dropped."))

N.append(node(
    "flow_of_wrath", "Flow of Wrath",
    "Increases your spell critical strike chance by 15%.",
    2, -2,
    effects={"crit_chance_spell": 15.0},
    connect=["voltaic_mastery"],
    source="CoA verbatim: 'Increases your critical strike chance by 15% "
           "against enemies affected by Drown.' No effect key reads whether a "
           "target carries a debuff, so the condition is dropped and CoA's "
           "15% applies always. Drown is a 1-minute cooldown rather than a "
           "rotational debuff, so this IS a real buff over CoA's version "
           "rather than a formality - stated rather than hidden, and it sits "
           "at tier 2 accordingly."))

N.append(node(
    "voltaic_mastery", "Voltaic Mastery",
    "Increases the damage of Deluge by 25%.",
    2, 0,
    effects={"ability_stormbringer_deluge_damage": 0.25},
    connect=["kinetic_energy"],
    source="CoA verbatim: 'Damage dealt by Deluge is increased by 5% for each "
           "stack of Conductive.' CONDUCTIVE CANNOT EXIST - nothing reads "
           "another effect's stack count, and CoA's own Conductive "
           "description is the unresolved token '$56', so even its cap is "
           "unknown. Five stacks at 5% is the standard assumption across "
           "CoA's stacking buffs, giving 25% flat."))

N.append(node(
    "kinetic_energy", "Kinetic Energy",
    "Your spells charge you, raising your spell critical strike chance by 2% "
    "per stack for 3 turns, stacking 3 times.",
    2, 2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "stormbringer_kinetic_energy",
                           "name": "Kinetic Energy", "effect_type": "buff",
                           "duration": 3, "max_stacks": 3,
                           "stat_mods": {"crit_chance_spell": 2.0},
                           "on_target": False}},
    connect=["lethal_current"],
    source="CoA verbatim: 'Casting a spell that consumes Conductive now "
           "grants you a stack of Kinetic Energy. Critical strike chance "
           "increased by 2%, stacking 3 times, for 10 sec. Additional "
           "applications do not refresh the duration.' The Conductive "
           "condition cannot be read, so it fires on any damage cast. CoA's "
           "2% and 3 stacks kept, 10 sec is 3 turns. The no-refresh rule has "
           "no equivalent - re-application always refreshes here - which "
           "makes this slightly stronger than CoA's."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "lethal_current", "Lethal Current",
    "Increases the critical strike chance of Electrocute by 25%.",
    3, -4,
    effects={"ability_stormbringer_electrocute_crit": 25.0},
    connect=["bursting"],
    source="CoA over 2 ranks: 'Increases the critical strike chance of "
           "Electrocute by 30% against enemies below 20% health.' THERE IS NO "
           "EXECUTE GATE AVAILABLE TO A TALENT - execute_threshold is an "
           "ABILITY property and high_health_damage_threshold_pct is a dead "
           "key - so the condition cannot be expressed. Priced at 25% total "
           "rather than CoA's 60% over two ranks, because it now applies at "
           "every health level instead of only the last fifth."))

N.append(node(
    "bursting", "Bursting",
    "Increases the damage of Drown by 30%.",
    3, -2,
    effects={"ability_stormbringer_drown_damage": 0.30},
    connect=["unbridled_flow"],
    source="CoA verbatim: 'Increases the stack value of Drowning by 20%.' "
           "Drowning is Drown's own stacking mechanic (CoA: 'each time you "
           "generate a stack of Conductive you increase their...' - the text "
           "is truncated in the Builder payload itself), and no key modifies "
           "another effect's per-stack value. Rerouted to the ability's "
           "damage, which is what a bigger stack value buys."))

N.append(node(
    "unbridled_flow", "Unbridled Flow",
    "Increases the damage of Shock by a further 15%.",
    3, 0,
    effects={"ability_stormbringer_shock_damage": 0.15},
    connect=["unstable"],
    source="CoA's level 30 passive: 'Damage dealt by Shock is now increased "
           "by 15% while channeling Stormflow.' THERE IS NO CHANNELLING - a "
           "cast resolves within a turn - so the gate cannot exist. CoA's 15% "
           "is granted permanently. This is the first of three talents whose "
           "whole condition is 'while channeling Stormflow' (with Storm "
           "Synergy and Amped Flow); Storm Synergy is not built at all, since "
           "'Electrocute can be used while channeling' has nothing left once "
           "channelling is gone."))

N.append(node(
    "amped_flow", "Amped Flow",
    "Shock splashes 75% of its damage onto 1 nearby enemy.",
    3, 2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["stormbringer_shock"],
          "splash_damage": {"pct": 0.75, "max_targets": 1,
                            "school": "frost"}},
    connect=["unstable"],
    source="CoA verbatim: 'While channeling Stormflow, your Shock now strikes "
           "1 additional target at 75% value.' The channel gate is gone (see "
           "Unbridled Flow) but the rest ports closely - CoA's 1 extra target "
           "at exactly 75% value, as splash_damage, since no key adds targets "
           "to an ability. One of the cleaner translations in this tree "
           "because CoA already stated it as a percentage."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "unstable", "Unstable",
    "Your critical strikes quicken the flow, raising your haste by 15% for 2 "
    "turns.",
    4, -3,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "apply_effect": {"effect_id": "stormbringer_unstable",
                           "name": "Unstable", "effect_type": "buff",
                           "duration": 2, "max_stacks": 1,
                           "stat_mods": {"haste": 15.0},
                           "on_target": False}},
    connect=["stormcloud"],
    source="CoA verbatim: 'Your direct damage critical strikes cause your "
           "Stormflow to tick 20% faster for 3 sec.' A faster tick has no "
           "meaning when ticks are per-turn, and nothing modifies one "
           "ability's tick rate. Rerouted to haste, which is what 'faster' "
           "means in a turn-based fight - acting more often. 1-turn internal "
           "cooldown so a crit streak does not hold it up permanently."))

N.append(node(
    "stormcloud", "Stormcloud",
    "Torrential Wrath gathers a cloud overhead, leaving the target taking 20% "
    "more spell damage for 5 turns.",
    4, -1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["stormbringer_torrential_wrath"],
          "apply_effect": {"effect_id": "stormbringer_stormcloud",
                           "name": "Stormcloud", "effect_type": "debuff",
                           "duration": 5, "max_stacks": 1,
                           "stat_mods": {"spell_damage_taken_pct": 20.0},
                           "on_target": True}},
    connect=["hydromatic"],
    source="CoA verbatim: 'Summon a cloud above an enemy target's head for 15 "
           "sec, causing them to take 20% additional damage from your spells. "
           "Using Torrential Wrath on an enemy affected by Stormcloud causes "
           "a Geyser to erupt beneath them.' The first half ports exactly - "
           "CoA's 20%, and 15 sec is 5 turns. The Geyser needs a "
           "debuff-presence check, which no key provides, so the follow-up "
           "eruption is dropped. INSIDE A STATUS EFFECT "
           "spell_damage_taken_pct is divided by 100 and POSITIVE INCREASES "
           "damage taken, which is what a debuff wants."))

N.append(node(
    "hydromatic", "Hydromatic",
    "Increases the damage of Electrocute by 50%.",
    4, 1,
    effects={"ability_stormbringer_electrocute_damage": 0.50},
    connect=["static_electricity"],
    source="CoA's level 50 passive: 'Your Electrocute is now affected by "
           "Conductive, increasing its damage by 10% per stack.' Conductive "
           "cannot exist (see Voltaic Mastery). Five stacks at 10% is 50% "
           "flat - the ceiling a fully-stacked Maelstrom would have reached."))

N.append(node(
    "conductor_in_charge", "Conductor In Charge",
    "Increases all damage you deal by 8%.",
    4, 3,
    effects={"all_damage": 0.08},
    connect=["static_electricity"],
    source="CoA verbatim: 'Increases all damage dealt by party and raid "
           "members by 3% and your Frost damage dealt by 5%. Does not stack "
           "with similar effects.' A TALENT CANNOT REACH AN ALLY - "
           "get_talent_effects() reads only the character's own trees - and "
           "there is no per-school damage key for the Frost half. Both halves "
           "land on the Stormbringer as a single 8% (CoA's 3 plus 5), and the "
           "description says 'you' rather than promising a raid buff the "
           "engine will not deliver. Contrast Wind, where the party buffs are "
           "real because they are ABILITIES."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "static_electricity", "Static Electricity",
    "Critical strikes with Torrential Wrath bring Drown two turns closer to "
    "ready.",
    5, -3,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "ability_filter": ["stormbringer_torrential_wrath"],
          "reset_cooldown": {"abilities": ["stormbringer_drown"],
                             "turns": 2}},
    connect=["stormfury"],
    source="CoA verbatim: 'Critical strikes with Torrential Wrath now spawn "
           "an Electrified Water Elemental to aid you in combat for 20 sec. "
           "When an Electrified Water Elemental dissipates, the cooldown of "
           "your Drown is reduced by -2 sec.' A talent cannot summon a pet - "
           "there is no summon payload, and Stormbringer's only pet is the "
           "Air Elemental on the Wind tree - and no trigger fires when a pet "
           "dies. So the elemental is cut and its PURPOSE is kept: the Drown "
           "cooldown reduction, delivered directly off the crit that would "
           "have spawned it. CoA's Electrified Waters node is the same "
           "mechanic keyed on Drown being up and is folded in here rather "
           "than built twice."))

N.append(node(
    "spheres_of_power", "Spheres of Power",
    "Your spells have a 25% chance to loose a power sphere, striking for "
    "spellstorm damage.",
    5, -1,
    proc={"trigger": "on_damage_cast", "chance": 25, "icd": 0,
          "damage_flat": 120, "school": "arcane"},
    connect=["stormfury"],
    source="CoA verbatim: 'Your direct damage dealt now has a 25% chance to "
           "summon a Power Sphere that will move towards your target. Can "
           "only have 1 Power Sphere up at a time. Power Sphere will redirect "
           "its movement towards enemies you cast Stormflow on. Upon reaching "
           "the target, it deals Spellstorm Damage to them and enemies "
           "within 5 yds.' A travelling projectile is positional and there is "
           "no summon payload, so the sphere becomes the damage it would have "
           "delivered, immediately. CoA's 25% kept. Spellstorm is typed "
           "arcane, the engine's generic magic school."))

N.append(node(
    "mystic_thunder", "Mystic Thunder",
    "Increases the damage of Torrential Wrath by 40%.",
    5, 1,
    effects={"ability_stormbringer_torrential_wrath_damage": 0.40},
    connect=["stormfury"],
    source="CoA verbatim: 'Interrupt the target's current spell cast and then "
           "mark them for 5 seconds. If they cast again while marked they are "
           "silenced for 3 seconds.' NEITHER INTERRUPT NOR SILENCE HAS A KEY, "
           "and a mark read by a later action needs a debuff-presence check "
           "that does not exist - so none of this talent is buildable as "
           "written. It is the second node in this audit to lose everything "
           "to the missing silence key (after Lightning's Tome of Lightning). "
           "Rerouted to damage on the spec's Static spender so the node is "
           "worth a point."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "stormfury", "Stormfury",
    "Your spells call down the storm, striking for nature damage and leaving "
    "the sky raining on your target for 3 turns.",
    6, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
          "ability_filter": WATER,
          "damage_flat": 110, "school": "nature",
          "apply_effect": {"effect_id": "stormbringer_stormfury",
                           "name": "Stormfury", "effect_type": "dot",
                           "duration": 3, "potency": 58,
                           "damage_school": "nature", "on_target": True}},
    source="CoA verbatim: 'Depletes 50 Static. Summon a flurry of rain, wind, "
           "and lightning from the sky for 20 seconds. Every 2 sec, enemies "
           "within 30 yds of the caster are zapped with lightning, dealing "
           "Nature damage.' A persistent area effect centred on the caster "
           "has no mechanism - there is no ground placement and no periodic "
           "trigger - so the capstone pays the same damage two ways instead: "
           "an immediate strike plus a dot, both off the frost kit, with a "
           "1-turn internal cooldown so casting two frost spells in a turn "
           "does not double it. This is the one payload combination that gets "
           "close to 'a storm that keeps hitting', and both halves are live: "
           "damage_flat with a school, and apply_effect carrying a dot."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. tools/talent_ranks.spread() rescales so a
# ranked node lands on exactly the ceiling it had at one rank, and refuses
# nodes carrying small integer durations and unlock_ability nodes.
#
# NOTE Disciple of Thorim is deliberately authored at CoA's PER-RANK value
# with CoA's own 3 ranks, so the policy skips it (max_points is already 3)
# and get_effective_effects() multiplies 2.0 by points spent to reach 6%.
# Every other ranked node here is authored at the CEILING for the policy to
# divide. Hand-authoring a ceiling at ranks=3 is what tripled five nodes on
# Guardian earlier today.
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
    print(f"Stormbringer Maelstrom: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
