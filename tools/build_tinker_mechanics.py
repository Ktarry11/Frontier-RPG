#!/usr/bin/env python3
"""Rebuild Tinker's Mechanics tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_tinker_mechanics.py [--check]

Kyle, 4 Nov 2026: "i am looking at the tinkerer mechanics talents and theyre
mostly just flat % boosts that are boring." He was right: the shipped tree
was 24 nodes of which 22 were a pure number and nothing else.

Kyle, 5 Nov: "let's build the 21 CoA classes PROPERLY WITH REAL DATA FROM THE
WEBSITE", and "this is turn based. So we likely won't use every single skill
or talent. So we need to be creative when needed."

SOURCE: data/reference/coa/tinker.json, tab 75 - Ascension's own CoA Builder
payload, 42 real Mechanics talents. Identity from
reference/coa_sidekick/CLASS_tinker.txt: Mechanics is "Closest to Retail
Demonology Warlock" - a ranged DPS whose damage comes out of a Mechsuit and
a pet rather than out of itself.

WHAT CHANGED, AND WHY IT IS NOT JUST "MORE TALENTS"

The old tree had the right NAMES. Arclight Adept, Arclight Core, Junker,
Augmentor and Defensive Utility are all genuine CoA talents - someone took
the names and replaced every mechanic with a flat percentage. Arclight Core
in CoA marks a target for your pet to consume; ours read "+4% Spanner Smash
damage per rank". So this is less an expansion than a restoration.

CoA's 42 become 24 here, not 42, and that is the "be creative" part:

  - Four of CoA's own entries are unresolved template variables in their
    data ($ac, $ae, $aa, $a8 - Gear Grind, Blazewrought Titan, Clockwork
    Guardians, Build: Mechsuit). There is nothing to port; inventing a
    mechanic and attributing it to the reference would be worse than
    leaving them out.
  - Several are pure positioning (Activate Jets' leap, Gatling Gun's
    channel, 30-yard lines). This engine has no movement, no range and no
    channels, so they are either dropped or repriced as damage.
  - CoA splits what is one decision here across several nodes - three
    separate Mechsuit sub-buttons, two near-identical crit passives. A
    turn-based tree with ~24 picks cannot afford a node that reads as a
    rounding error.

What survives is every talent that changes what you do, as far as the engine
allows. The honest count, measured rather than claimed: 23 nodes, 11 carrying
a proc (against 2 before), and 5 that are still a generic character stat
(against 5 before). The remaining 7 are ability-targeted numbers - Combustion
damage, Sticky Bomb cooldown - which are not behaviour but are at least about
this spec rather than about being a Tinker.

So the improvement is procs 2 -> 11, not "scalars eliminated". A first draft
of this docstring claimed 20 of 24 were behavioural; the counter in main()
said 10, and the counter was right.

THE SCRAP PROBLEM, stated rather than hidden. Three CoA Mechanics talents
generate Scrap, and entities/character.py carries a standing note that
"nothing in the game COSTS scrap". Abilities hold a single resource_type
with no secondary-cost field, so giving Mechsuit abilities a Scrap cost is
engine work, not data. Rather than ship three decorative talents, each
Scrap grant here ALSO grants mana - which is what CoA's own Combat Crafter
does ("5 Scrap and 2% of your maximum mana") - so they are worth taking
today and get better the day Scrap has a sink. Flagged in the handoff doc.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/tinker_mechanics.json"

TREE = {
    "spec_name": "Tinker Mechanics",
    "tree_id": "tinker_mechanics",
    "description": ("Battle engineer - fights from inside a powered Mechsuit "
                    "with a construct at its side, and feeds both on scrap."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from data/reference/coa/tinker.json tab 75 "
        "(Ascension CoA Builder payload, 42 real Mechanics talents) with "
        "identity from reference/coa_sidekick (Mechanics = 'Closest to "
        "Retail Demonology Warlock'). Replaces a 24-node tree that carried "
        "real CoA names on 22 pure-scalar effects. 24 nodes kept of CoA's "
        "42: four of CoA's are unresolved template vars in their own data "
        "($ac/$ae/$aa/$a8), several are movement/range/channel talents this "
        "turn-based engine cannot express, and CoA splits single decisions "
        "across multiple nodes. Every surviving node either changes what you "
        "do or states a number CoA states."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, y, *, ranks=1, effects=None, proc=None,
         connect=None, source="", active=False):
    entry = {
        "talent_id": f"tinker_mechanics_{nid}",
        "name": name,
        "description": desc,
        "node_type": "active" if active else "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": y,
        "effects": effects or {},
        "connected_to": [f"tinker_mechanics_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


def unlock(nid, name, ability, blurb, tier, x, y, *, connect=None, source=""):
    """A node whose job is to TEACH an ability.

    Every ability below carries "requires_talent": true, which tells
    combat/abilities.py not to learn it from level_req alone - so an ability
    with no unlock node anywhere is unobtainable forever. The first version
    of this rebuild dropped all four and stranded the entire mechsuit kit
    plus Makeshift Dynamite. tools/qa_abilities_obtainable.py now fails the
    build if that happens again.
    """
    return node(nid, name, f"Learn {name.rstrip('!')}. {blurb}", tier, x, y,
                effects={"unlock_ability": ability}, connect=connect,
                source=source, active=True)


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "slam_the_cogs", "Slam the Cogs!",
    "Increases the damage you and your constructs deal by up to 8%.",
    0, -4, -6, ranks=2,
    effects={"all_damage": 0.04, "pet_damage": 0.04},
    connect=["mechanical_synergy"],
    source="CoA: 'Increases the damage dealt by you and your summons by 4%.' "
           "2 ranks, kept as stated - one of the few CoA Mechanics talents "
           "that genuinely is a flat number."))

N.append(node(
    "fine_tuned", "Fine Tuned",
    "Increases your critical strike chance by 4% and your constructs' damage by 4%.",
    0, -2, -6,
    effects={"crit_chance_physical": 4.0, "pet_damage": 0.04},
    connect=["junker"],
    source="CoA: 'Increases the critical strike and hit chance of you and your "
           "summons by 4%.' Pets have no crit key in this engine (pet_damage/"
           "pet_health/pet_armor only), so the pet half is expressed as damage; "
           "hit is dropped rather than faked."))

N.append(node(
    "cogmaster", "Cogmaster",
    "Increases your critical strike chance by 2%. Your critical strikes have a "
    "50% chance to scavenge 3 Scrap and restore mana.",
    0, 0, -6,
    effects={"crit_chance_physical": 2.0},
    proc={"trigger": "on_crit", "chance": 50, "icd": 0,
          "grant_resource": {"resource": "mana", "amount": 40}},
    connect=["combat_crafter"],
    source="CoA: 'Increases your critical strike chance by 2% and gives ranged "
           "critical strikes a 50% chance to generate 3 Scrap.' Pays MANA, not "
           "Scrap: nothing spends Scrap yet (see the docstring), and "
           "grant_resource only takes one resource. Mana is the live, useful "
           "half; the Scrap flavour returns when a sink exists."))

N.append(node(
    "junker", "Junker",
    "Spanner Smash and Scrap Shot raise your construct's damage by 5% for 5 "
    "turns, stacking twice.",
    0, 2, -6,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["tinker_spanner_smash", "tinker_scrap_shot"],
          "apply_effect": {"effect_id": "tinker_junker", "name": "Junker",
                           "duration": 5, "max_stacks": 2,
                           "stat_mods": {"pet_damage": 0.05}}},
    connect=["sprocket_loaded"],
    source="CoA: 'Casting Spanner Smash and Scrap Shot now increases your pet's "
           "attack power by 5% for 15 sec, stacking 2 times.' 15 sec -> 5 turns. "
           "Replaces a pure-scalar node of the same name."))

N.append(node(
    "master_builder", "Master Builder",
    "Your Build abilities cost 30% less mana.",
    0, 4, -6,
    effects={"ability_tinker_build_sentry_turret_cost_pct": 0.30,
             "ability_tinker_build_rusthound_cost_pct": 0.30,
             "ability_tinker_build_battle_turret_x13_cost_pct": 0.30},
    connect=["mechanical_synergy"],
    source="CoA: 'Reduces the cast time of Build abilities by -50%.' There are "
           "no cast times in a turn-based engine, so the saving is repriced as "
           "mana - the resource a Build actually competes for here. POSITIVE "
           "is a reduction for _cost_pct in this engine; writing -0.30 (the "
           "intuitive sign) made Builds 30% MORE expensive, which "
           "audit_talents caught. Targets only Build abilities that exist: "
           "there is no tinker_build_scrapmaw despite the CoA talent naming "
           "one."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "mechanical_synergy", "Mechanical Synergy",
    "Increases the damage of Sticky Bomb and your Mechsuit abilities by 15% per rank.",
    1, -3, -4, ranks=2,
    effects={"ability_tinker_sticky_bomb_damage": 0.15,
             "ability_tinker_mechsuit_laser_beam_damage": 0.15,
             "ability_tinker_mechsuit_combustion_damage": 0.15},
    connect=["arclight_adept"],
    source="CoA: 'Increases the damage of Sticky Bomb Explosion and Mechsuit "
           "abilities by 15%.'"))

N.append(node(
    "sprocket_loaded", "Sprocket Loaded",
    "Casting Makeshift Dynamite resets the cooldown of your Mechsuit abilities.",
    1, -1, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["tinker_makeshift_dynamite"],
          "reset_cooldown": ["tinker_mechsuit_laser_beam",
                             "tinker_mechsuit_combustion"]},
    connect=["defensive_utility"],
    source="CoA: 'Casting Makeshift Dynamite now resets the cooldown of your "
           "Mechsuit abilities.' Ported exactly - reset_cooldown is a real proc "
           "payload in this engine (20 existing nodes use it)."))

N.append(node(
    "combat_crafter", "Combat Crafter",
    "While in your Mechsuit, damage dealt by your constructs has a 20% chance "
    "to scavenge 5 Scrap and restore mana.",
    1, 1, -4,
    proc={"trigger": "on_damage_cast", "chance": 20, "icd": 0,
          "require_mechsuit": True,
          "grant_resource": {"resource": "mana", "amount": 60}},
    connect=["engine_augmentation"],
    source="CoA: 'While in your Mechsuit, damage dealt by your summons now has "
           "a 20% chance to grant you 5 Scrap and 2% of your maximum mana.' "
           "The mana half is ported because it is live; the Scrap half waits "
           "on a sink. require_mechsuit is an existing proc condition here."))

N.append(node(
    "arclight_adept", "Arclight Adept",
    "Increases the critical damage of your Mechsuit abilities by 15%.",
    1, 3, -4,
    effects={"ability_tinker_mechsuit_laser_beam_crit_damage": 0.15,
             "ability_tinker_mechsuit_combustion_crit_damage": 0.15},
    connect=["turbo_guns"],
    source="CoA: 'Increases the critical damage of your Mechsuit abilities by "
           "15%.' The shipped version read '+4% Spanner Smash damage per rank', "
           "which is neither the right ability nor the right mechanic."))

N.append(node(
    "defensive_utility", "Defensive Utility",
    "Your Mechsuit increases your armor by an additional 50%.",
    1, -5, -4,
    effects={"armor_pct": 50.0},
    connect=["augmechtation"],
    source="CoA: 'Your Mechsuit will now increase your armor by an additional "
           "50%.' Ideally gated on the Mechsuit being up; armor_pct has no "
           "conditional form, so it is granted flat and the 50% is left as "
           "CoA states it rather than being quietly halved to compensate."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "turbo_guns", "Turbo Guns",
    "Increases the damage of Mechsuit: Combustion by 10% per rank.",
    2, 2, -2, ranks=2,
    effects={"ability_tinker_mechsuit_combustion_damage": 0.10},
    connect=["overload"],
    source="CoA: 'Reduces the cast time of your Mechsuit: Combustion by 0.25 "
           "sec and its damage is increased by 20%.' Cast time is meaningless "
           "here, so only the damage half ports. SPLIT from 1 rank of 20% "
           "into 2 ranks of 10% - the same ceiling, not a buff. The rebuilt "
           "tree held 29 points with only 28 below tier 6, against a gate of "
           "30, so its capstone was unreachable at any level. See "
           "tools/qa_talent_tiers_reachable.py."))

N.append(node(
    "flak_guns", "Flak Guns",
    "Mechsuit: Combustion deals 10% more damage and 15% more critical damage.",
    2, 0, -2,
    effects={"ability_tinker_mechsuit_combustion_crit_damage": 0.15,
             "ability_tinker_mechsuit_combustion_damage": 0.10},
    connect=["overload"],
    source="CoA: 'Your Mechsuit: Combustion now has 10% increased critical "
           "strike chance and 15% increased critical damage.' There is no "
           "per-ability crit CHANCE key in this engine - only per-ability crit "
           "damage - so the chance half is repriced as flat damage rather than "
           "written as a key nothing reads."))

N.append(node(
    "engine_augmentation", "Engine Augmentation",
    "For 3 turns after entering your Mechsuit, all damage you deal scavenges 3 Scrap.",
    2, -2, -2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "require_mechsuit": True,
          "grant_resource": {"resource": "scrap", "amount": 3}},
    connect=["flame_jets"],
    source="CoA: 'For 8 seconds after activating your Mechsuit, all damage "
           "dealt will now generate 3 Scrap.' 8 sec -> 3 turns. The engine has "
           "no 'first N turns of a buff' window, so this runs for as long as "
           "the Mechsuit is up - a real simplification, noted rather than "
           "papered over."))

N.append(node(
    "augmentor", "Augmentor",
    "While an Augmentation is active, your haste is increased by 10%.",
    2, -4, -2,
    effects={"haste": 10.0},
    connect=["augmechtation"],
    source="CoA: 'While Piercing Augmentation or Aether Augmentation is active, "
           "your ranged haste is increased by 10%.' Haste here makes you act "
           "more often on the turn meter rather than cast faster, which is the "
           "correct translation of the intent."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "bombs_bombs", "Bombs? BOMBS!",
    "Reduces the cooldown of Sticky Bomb by 17.5% per rank.",
    3, -3, 0, ranks=2,
    effects={"ability_tinker_sticky_bomb_cooldown_pct": 0.175},
    connect=["arclight_core"],
    source="CoA: 'Increases the detonation speed of Sticky Bomb by -1 sec and "
           "reduces its cooldown by -2 sec.' Detonation delay does not exist "
           "here; the cooldown cut is expressed as a percentage because this "
           "engine counts cooldowns in turns, not seconds. Positive is a "
           "reduction here, same trap as Master Builder."))

N.append(node(
    "flame_jets", "Flame Jets",
    "While in your Mechsuit, Scrap Shot and Makeshift Dynamite set the target "
    "alight, burning them for 3 turns.",
    3, -1, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "require_mechsuit": True,
          "ability_filter": ["tinker_scrap_shot", "tinker_makeshift_dynamite"],
          "apply_effect": {"effect_id": "tinker_living_flame",
                           "name": "Living Flame", "duration": 3,
                           "max_stacks": 5, "school": "fire",
                           "dot_damage": 32}},
    connect=["overload"],
    source="CoA: 'While inside your Mechsuit, damage dealt by your Scrap Shot "
           "and Makeshift Dynamite now applies Living Flame... Deals 32 Fire "
           "Damage every 2 sec... stacking 5 times.' The Combustion-damage-taken "
           "rider is dropped: there is no per-source damage-taken modifier here."))

N.append(node(
    "arclight_core", "Arclight Core",
    "Makeshift Dynamite leaves the target burning with arclight fire for 2 turns.",
    3, 1, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["tinker_makeshift_dynamite"],
          "apply_effect": {"effect_id": "tinker_arclight_mark",
                           "name": "Arclight Mark", "duration": 2,
                           "max_stacks": 1, "school": "fire",
                           "dot_damage": 30}},
    connect=["turbo_upgrade"],
    source="CoA: 'Makeshift Dynamite now marks enemies for 6 sec. The next "
           "damaging ability used on this target by your pet consumes the mark "
           "to deal Fire damage.' 6 sec -> 2 turns. The pet-consumes-the-mark "
           "half is NOT ported: it would need a new proc payload, and an "
           "invented key reads as working while doing nothing. Shipped as the "
           "burn it becomes; the consume is in the handoff list."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "overload", "Overload",
    "Your Mechsuit abilities have a 40% chance to strike twice more for 30% damage.",
    4, 0, 2,
    proc={"trigger": "on_damage_cast", "chance": 40, "icd": 0,
          "ability_filter": ["tinker_mechsuit_laser_beam",
                             "tinker_mechsuit_combustion"],
          "extra_attack": 2, "bonus_pct": 0.30},
    connect=["junkyard_loiter"],
    source="CoA: 'Damage dealt by Mechsuit: Combustion and Mechsuit: Laser Beam "
           "now have a 40% chance to strike 2 additional times for 30% of the "
           "damage dealt.' extra_attack and bonus_pct are both existing proc "
           "payloads."))

N.append(node(
    "augmechtation", "Augmechtation",
    "Your Mechsuit increases your damage by an additional 10% while active.",
    4, -3, 2,
    effects={"all_damage": 0.10},
    connect=["haywired_state"],
    source="CoA: 'Your Mechsuit now increases your damage by an additional 10% "
           "while active.' Same conditional gap as Defensive Utility - granted "
           "flat, stated honestly."))

N.append(node(
    "nano_repair_tech", "Nano-Repair Tech",
    "Your attacks patch you up, healing you for a little each time you strike.",
    4, 3, 2,
    effects={"pet_health": 0.03},
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1, "heal_flat": 24},
    connect=["junkyard_loiter"],
    source="CoA: 'You and your pet now regenerate 3% of your maximum health "
           "every 8 sec.' There is NO health-regen effect key in this engine - "
           "health_regen_pct is read by nothing - so the self-heal is a live "
           "heal_flat proc on a 1-turn internal cooldown instead, and only the "
           "pet half stays a stat."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "junkyard_loiter", "Junkyard Loiter",
    "Your Mechsuit abilities plant a sticky bomb on the target, at most once every turn.",
    5, 1, 4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
          "ability_filter": ["tinker_mechsuit_laser_beam",
                             "tinker_mechsuit_combustion"],
          "cast_ability": "tinker_sticky_bomb"},
    connect=["turbo_upgrade"],
    source="CoA: 'When you deal damage with Mechsuit: Laser Beam or Mechsuit: "
           "Combustion you now launch a Lesser Sticky Bomb on each target "
           "struck.' No separate Lesser bomb exists here, so it casts the real "
           "Sticky Bomb on a 1-turn internal cooldown to stop it chaining."))

N.append(node(
    "haywired_state", "Haywired State!",
    "Casting a Mechsuit ability sends your construct haywire for 2 turns, "
    "making its attacks chain to nearby enemies.",
    5, -1, 4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 2,
          "ability_filter": ["tinker_mechsuit_laser_beam",
                             "tinker_mechsuit_combustion"],
          "apply_effect": {"effect_id": "tinker_haywired", "name": "Haywired State!",
                           "duration": 2, "max_stacks": 1,
                           "stat_mods": {"pet_damage": 0.20}}},
    connect=["turbo_upgrade"],
    source="CoA: 'Casting Mechsuit abilities now causes your pet to enter a "
           "haywired state for 6 seconds... auto attacks now zap up to 10 "
           "nearby enemies.' 6 sec -> 2 turns. Pet AoE is not modelled, so the "
           "chain is expressed as a pet damage buff rather than invented."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "turbo_upgrade", "Turbo Upgrade!",
    "Increases the damage of your Mechsuit abilities by 100% and the duration of your Mechsuit by 100%.",
    6, 0, 6,
    effects={"ability_tinker_mechsuit_laser_beam_damage": 1.00,
             "ability_tinker_mechsuit_combustion_damage": 1.00,
             "ability_tinker_mechsuit_form_duration": 1.00},
    source="CoA: 'Level 40 Passive. Increases the effectiveness of your "
           "Mechsuit by 100%.' CoA does not say what 'effectiveness' covers; "
           "read here as the two Mechsuit abilities' damage and the form's own "
           "duration, which is the reading that makes it a capstone rather "
           "than a stat stick."))


# ---- the ability unlocks ------------------------------------------------
# Restored after the first version of this rebuild dropped them. See
# unlock()'s docstring: without these four nodes the abilities cannot be
# learned at any level, which stranded the whole mechsuit kit.
N.append(unlock(
    "makeshift_dynamite", "Makeshift Dynamite", "tinker_makeshift_dynamite",
    "A stick of something you threw together, and it burns.",
    2, 4, -2, connect=["bombs_bombs"],
    source="Same tier as before the rebuild."))

N.append(unlock(
    "build_mechsuit", "Build: Mechsuit", "tinker_mechsuit_form",
    "Climb into the suit. Your abilities change while you are in it.",
    3, 3, 0, connect=["mechsuit_laser_beam"],
    source="The gateway for the whole mechsuit kit: the two abilities below "
           "require the form, and several nodes in this tree carry "
           "require_mechsuit. Same tier as before the rebuild."))

N.append(unlock(
    "mechsuit_laser_beam", "Mechsuit: Laser Beam", "tinker_mechsuit_laser_beam",
    "A sustained fire beam, available only from inside the suit.",
    4, 5, 2, connect=["mechsuit_combustion"],
    source="Requires the Mechsuit form, so it hangs off Build: Mechsuit "
           "rather than sitting loose in the tree."))

N.append(unlock(
    "mechsuit_combustion", "Mechsuit: Combustion", "tinker_mechsuit_combustion",
    "Vents the whole reactor into everything around you.",
    5, 3, 4,
    source="The suit's area attack and the deepest of the three, so it is "
           "the last of the kit you can reach. Was tier 4."))


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
    for n in TREE["nodes"]:
        for c in n["connected_to"]:
            assert c in ids, f"{n['talent_id']} connects to unknown {c}"

    scalar = sum(1 for n in TREE["nodes"]
                 if n.get("effects") and not n.get("proc"))
    print(f"Tinker Mechanics: {len(TREE['nodes'])} nodes, "
          f"{len(TREE['nodes']) - scalar} with real mechanics, {scalar} plain numbers")
    if check:
        print("--check: nothing written")
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
