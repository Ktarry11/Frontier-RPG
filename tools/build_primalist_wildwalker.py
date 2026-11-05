#!/usr/bin/env python3
"""Rebuild Primalist's Wildwalker tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_primalist_wildwalker.py [--check]

SOURCE: data/reference/coa/primalist.json - 39 real Wildwalker talents from
Ascension's own CoA Builder payload, the same data allthingscoa.com
presents. Role: DPS. coa_playstyles.json gives Wildwalker no plays_like
comparison, which is fair - CoA's version is a melee beast-master with a
permanent pet, built on bleeds and on Rage traded back and forth between
the two of them.

The shipped tree was 26 nodes: 18 pure scalars, 1 proc, 7 unlocks. Several
carried real CoA names (Fury of the Wild, Torn to Shreds, Elemental
Berserker, Rips and Tears, Spinebreaker) on bonuses of +2% to a stat.

WHAT THE SPEC IS. Bleeds and Rage churn. Totemic Smash and Rylak's Bite
open wounds, those wounds feed Rage back, and Rage buys more of both.

THE PET LIMIT, which decides a third of this tree. Fourteen of CoA's 39
Wildwalker talents are about the pet, and this engine supports exactly two
things in that direction:

  1. The pet scales off THREE owner talent keys - pet_damage, pet_health,
     pet_armor (entities/pet.py, deliberately narrow so the pet does not
     inherit the owner's gear). Those are fractions.
  2. Nothing else. A pet does not fire procs: entities/pet.py has no
     fire_proc_trigger call at all, so "damage dealt by your pet applies
     X" has no mechanism behind it.

So every CoA talent of the form "your pet's attacks do something" is
either rerouted onto the Primalist's own attacks or dropped, and which one
is stated per node. Not approximated into a pet buff that pretends to be
the original. Dropped outright for this reason: Bring Me Their Bones' pet
stack-consumption (the ABILITY is still unlocked here, just not CoA's
talent wrapper around it), Bloody Claws, Spiritual Frenzy, Throat Clamp,
and the pet halves of Sharpened Claws and Fury of the Wild.

CONVENTIONS, none of which agree with each other, and each of which is a
way to ship a node that looks authored and does nothing:
  strength_pct, attack_power_pct, armor_penetration_pct   percentage POINTS
  every other _pct effect key                             FRACTION
  physical_damage_taken_pct in a status effect            percentage POINTS
  *_cost_pct / *_cooldown_pct        FRACTION, POSITIVE MEANS A REDUCTION
  pet_damage / pet_health / pet_armor                     FRACTION
  aoe_damage      only applies to abilities whose target_type is enemy_aoe

A DEAD KEY THIS TREE WAS ALREADY SHIPPING. Rending Claws scaled
bleed_dot_damage, which the engine assembles as f"{flavour}_dot_damage"
and only resolves while some ability's id contains "bleed". No ability in
the game does, in any class, so the node did nothing. It uses dot_damage
here, which is unconditionally live. audit_talents.py had the key
hardcoded as live and now computes it from the ability data instead, which
is what surfaced this.

TURN-BASED CUTS. Wild At Heart reduces a global cooldown, and there is no
GCD here, so it is dropped rather than repriced into free value. Charges
("2 charges, 10 sec recharge") have no engine support and become
cooldowns. Every yard radius and both dashes are gone. Savage Frenzy's
movement-speed half is dropped and its damage half kept. CoA has TWO
different talents both named Pulverize; they get distinct ids and the
second is renamed in-game so the tree does not show the same word twice.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/primalist_wildwalker.json"

#: The two openers every bleed node in this tree hangs off.
OPENERS = ["primalist_totemic_smash", "primalist_rylaks_bite"]

#: Frontier's Seismic abilities, for the nodes CoA writes as "your Seismic
#: abilities". Named explicitly rather than matched on the substring so a
#: future ability called "seismic" something does not silently join the set.
SEISMIC = ["primalist_seismic_crash", "primalist_seismic_tremor",
           "primalist_seismic_wave"]

#: The bleed Torn to Shreds opens. Stacks twice, as CoA has it.
REND = {
    "effect_id": "primalist_rend", "name": "Rent Flesh",
    "effect_type": "dot", "duration": 4, "potency": 18,
    "max_stacks": 2, "damage_school": "physical", "on_target": True,
}

TREE = {
    "spec_name": "Primalist Wildwalker",
    "tree_id": "primalist_wildwalker",
    "description": ("Beast-master in the thick of it - opens wounds with a "
                    "pet at your heel and turns the bleeding into Rage."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from data/reference/coa/primalist.json "
        "(39 real CoA Wildwalker talents, role DPS). Replaces a 26-node "
        "tree of 18 pure scalars and 1 proc, several of them real CoA names "
        "on a +2% stat. All 7 unlock nodes are preserved - see "
        "tools/qa_abilities_obtainable.py for why that is not optional. "
        "Fourteen of CoA's talents are pet-side and this engine gives a pet "
        "three scaling keys and no procs, so those are rerouted or dropped "
        "per node rather than faked."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source="", active=False):
    entry = {
        "talent_id": f"primalist_wildwalker_{nid}",
        "name": name,
        "description": desc,
        "node_type": "active" if active else "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"primalist_wildwalker_{c}" for c in (connect or [])],
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
    "wild_rampage", "Wild Rampage",
    "Increases your attack power by 5% and your chance to hit by 2% per rank.",
    0, -5, ranks=2,
    effects={"attack_power_pct": 5.0, "hit_rating": 2.0},
    connect=["rips_and_tears"],
    source="CoA verbatim: 'Increases your attack power by 5% and your chance "
           "to hit by 2%.' One of the few CoA Wildwalker talents that really "
           "is a flat scalar, so it stays one. attack_power_pct takes "
           "percentage POINTS, so 5.0."))

N.append(node(
    "raptor_talons_passive", "Raptor Talons",
    "Increases your Strength by 5% per rank.",
    0, -3, ranks=2,
    effects={"strength_pct": 5.0},
    connect=["rips_and_tears"],
    source="CoA: 'Increases your Strength by 5% and your expertise by 4.' "
           "The expertise half is dropped: 'expertise' is read by no engine "
           "code, so authoring it would have been a dead key. strength_pct "
           "takes percentage POINTS."))

N.append(node(
    "rending_claws", "Rending Claws",
    "Increases the damage your damage-over-time effects deal by 4% per rank.",
    0, -1, ranks=3,
    effects={"dot_damage": 0.04},
    connect=["torn_to_shreds"],
    source="WAS bleed_dot_damage, which was DEAD. The engine assembles that "
           "key as f'{flavour}_dot_damage' in Ability._damage_multiplier and "
           "only reads it while some ability's id contains 'bleed' - and no "
           "ability in the game does, in any class, so this node scaled "
           "nothing. dot_damage is unconditionally live. The description now "
           "says 'damage-over-time' rather than 'bleeds' because that is "
           "what it applies to."))

N.append(node(
    "pulverize", "Pulverize",
    "Increases the critical strike chance of Totemic Smash by 10% per rank.",
    0, 1, ranks=2,
    effects={"ability_primalist_totemic_smash_crit": 10.0},
    connect=["totemic_smash"],
    source="CoA verbatim: 'Increases the critical strike chance of Totemic "
           "Smash by 10%.' ability_*_crit is a PERCENT. CoA has a second, "
           "different talent also called Pulverize - see pulverizing_strikes "
           "below, renamed so the tree does not show the word twice."))

N.append(node(
    "wild_rage", "Wild Rage",
    "Rylak's Bite no longer costs Rage.",
    0, 3,
    effects={"ability_primalist_rylaks_bite_cost_pct": 1.0},
    connect=["rylaks_bite"],
    source="CoA verbatim: 'Removes the Rage cost of Rylak's Bite.' A full "
           "1.0 reduction, and POSITIVE is the reduction direction - "
           "talented_cost does cost * (1 - pct). Authored negative it would "
           "have DOUBLED the cost, which is the mistake eight talents in "
           "this project already made."))

# ---- tier 1 -------------------------------------------------------------
N.append(unlock(
    "primal_shred", "Primal Shred", "primalist_primal_shred",
    "Your pet tears into several enemies at once, leaving them bleeding.",
    1, -5, connect=["primal_resurgence"],
    source="CoA: 'Command your pet to shred up to 5 enemies within 8 yds, "
           "causing them to bleed over 21 seconds.' Kept from the previous "
           "tree. The yard radius is dropped; the ability is already "
           "enemy_aoe."))

N.append(node(
    "rips_and_tears", "Rips and Tears",
    "Your weapon swings generate 2 extra Rage.",
    1, -3,
    proc={"trigger": "on_weapon_swing", "chance": 100, "icd": 0,
          "grant_resource": {"resource": "rage", "amount": 2}},
    connect=["primal_resurgence"],
    source="CoA: 'Periodic damage dealt by you or your pet now generates 2 "
           "Rage for you and 5 Focus for your pet.' Rerouted off periodic "
           "damage onto weapon swings, because there is no periodic-tick "
           "trigger in this engine - the trigger list is on_damage_cast, "
           "on_crit, on_damage_taken, on_cast, on_heal_cast, "
           "on_weapon_swing, on_kill, on_block, on_damage_or_heal_cast, "
           "on_avoid, on_parry, and a DoT tick fires none of them. The pet's "
           "Focus half is dropped: a pet has no resource a talent can reach. "
           "Rage per swing keeps the intent, which is that sustained damage "
           "pays for the next Rylak's Bite. Was the Primal Shred unlock, "
           "which is now its own node."))

N.append(unlock(
    "rylaks_bite", "Rylak's Bite", "primalist_rylaks_bite",
    "You and your pet close on an enemy together and maul it.",
    1, -1, connect=["torn_to_shreds"],
    source="CoA: '20 Rage, 2 charges, 10 sec recharge. You and your pet rush "
           "towards an enemy and strike them for 120% Weapon Damage.' Charges "
           "have no engine support and are already a cooldown on the ability. "
           "MOVED from tier 4 to tier 1: four nodes in this tree reference "
           "this ability (Wild Rage, Torn to Shreds, Primal Rage, "
           "Lacerations) and with the unlock at tier 4 you could take all of "
           "them before you could take the thing they modify."))

N.append(unlock(
    "totem_warrior", "Totem Warrior", "primalist_spirit_beast_master",
    "Call a spirit beast to fight alongside you.",
    1, 1, connect=["packmaster"],
    source="The pet itself, so everything pet-side in this tree depends on "
           "it. Kept from the previous tree."))

N.append(node(
    "primal_resurgence", "Primal Resurgence",
    "Seismic Crash generates 10 additional Rage.",
    1, 3,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["primalist_seismic_crash"],
          "grant_resource": {"resource": "rage", "amount": 10}},
    connect=["earthshaker"],
    source="CoA verbatim: 'Seismic Crash now generates an additional 10 Rage "
           "and Seismic Spike now generates 3 additional Rage.' Frontier has "
           "no Seismic Spike, so only the Crash half is built. This is the "
           "mana-to-Rage bridge the spec needs: Seismic Crash costs mana and "
           "Wildwalker's openers cost Rage."))

# ---- tier 2 -------------------------------------------------------------
N.append(unlock(
    "totemic_smash", "Totemic Smash", "primalist_totemic_smash",
    "Smash the ground, striking your target and everything near it.",
    2, -5, connect=["elemental_berserker"],
    source="MOVED from tier 5 to tier 2 for the same reason as Rylak's Bite: "
           "Pulverize, Torn to Shreds, Primal Rage, Elemental Berserker and "
           "Pulverizing Strikes all modify it."))

N.append(node(
    "torn_to_shreds", "Torn to Shreds",
    "Totemic Smash and Rylak's Bite leave the target bleeding for 4 turns, "
    "stacking twice.",
    2, -3,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": OPENERS,
          "apply_effect": dict(REND)},
    connect=["lacerations"],
    source="CoA verbatim: 'Totemic Smash and Rylak's Bite now causes enemies "
           "to bleed over 12 sec, stacking 2 times.' 12 sec is 4 turns and "
           "the stack count is CoA's. This is the node that gives the spec "
           "its bleeds; the old tree's version was "
           "ability_primalist_primal_shred_damage +8%, a flat number on a "
           "different ability entirely."))

N.append(unlock(
    "spinebreaker", "Spinebreaker", "primalist_raptor_talons",
    "A heavy strike aimed at the spine.",
    2, -1, connect=["primal_rage"],
    source="Kept from the previous tree, which already paired this name with "
           "the raptor_talons ability. CoA's own Spinebreaker text is one of "
           "several entries in this export whose description is a broken "
           "template reference, so there is nothing to port from it."))

N.append(node(
    "earthshaker", "Earthshaker",
    "Increases the damage dealt by your Seismic abilities by 10%.",
    2, 1,
    effects={f"ability_{a}_damage": 0.10 for a in SEISMIC},
    connect=["tremors"],
    source="CoA: 'Increases the damage dealt by Seismic abilities by 10% and "
           "allows their periodic damage to critically strike.' The crit half "
           "is an engine-wide rule about whether DoT ticks can crit, not a "
           "per-character bonus, so it is not a talent effect and is dropped. "
           "Written out per ability because there is no key for a named group "
           "of abilities."))

N.append(node(
    "packmaster", "Packmaster",
    "Increases your pet's damage by 6% and its health by 6% per rank.",
    2, 3, ranks=3,
    effects={"pet_damage": 0.06, "pet_health": 0.06},
    connect=["savage_frenzy"],
    source="Not a CoA node by this name, but it is the shape every one of "
           "CoA's pet-scaling talents has to take here: pet_damage, "
           "pet_health and pet_armor are the only three keys entities/pet.py "
           "reads off its owner. Carries CoA's Fury of the Wild ('when you "
           "cast a Boon, you cast it on your pet at 50% effectiveness'), "
           "which is not buildable as written - a talent cannot make an "
           "ability fire twice at different targets. Fractions, not points."))

# ---- tier 3 -------------------------------------------------------------
N.append(unlock(
    "primal_rush", "Primal Rush", "primalist_primal_rush",
    "Charge through a group, hitting everything in reach.",
    3, -4, connect=["bring_me_their_bones"],
    source="Kept from the previous tree."))

N.append(node(
    "primal_rage", "Primal Rage",
    "Totemic Smash refreshes Rylak's Bite, making it ready again at once.",
    3, -2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["primalist_totemic_smash"],
          "reset_cooldown": ["primalist_rylaks_bite"]},
    connect=["pulverizing_strikes"],
    source="CoA verbatim: 'Casting Totemic Smash now refreshes a charge of "
           "Rylak's Bite.' Charges are cooldowns here, so refreshing a charge "
           "is a cooldown reset. reset_cooldown takes a bare list as well as "
           "a dict (status_effects.py wraps it), and omitting `turns` is a "
           "FULL reset, which is what refreshing a charge means."))

N.append(node(
    "lacerations", "Lacerations",
    "Your critical strikes make the target take 15% more physical damage for "
    "3 turns.",
    3, 0,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "primalist_laceration",
                           "name": "Laceration", "effect_type": "debuff",
                           "duration": 3, "max_stacks": 1,
                           "stat_mods": {"physical_damage_taken_pct": 15.0},
                           "on_target": True}},
    connect=["sharpened_claws"],
    source="CoA: 'Melee critical strikes now increase the effectiveness of "
           "bleed effects on the target by 30% for 15 seconds.' There is no "
           "key for 'bleed effectiveness on this target' - the only live "
           "recipient-side damage key is <school>_damage_taken_pct - so this "
           "becomes physical damage taken, which raises the bleeds AND the "
           "melee that applied them. Halved from 30% to 15% for exactly that "
           "reason: it now covers more than CoA's version did. That key is "
           "percentage POINTS inside a status effect, so 15.0. 15 sec is 5 "
           "turns, cut to 3 so it has to be re-earned."))

N.append(node(
    "wild_vigor", "Wild Vigor",
    "Increases your maximum health by 2% per rank.",
    3, 2, ranks=3,
    effects={"max_health_pct": 0.02},
    connect=["savage_frenzy"],
    source="Not a CoA node - kept from the previous tree. A melee spec with "
           "a pet needs somewhere to put points that is not more damage, and "
           "this tier is otherwise all offence."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "savage_frenzy", "Savage Frenzy",
    "Landing a critical strike enrages you, increasing your damage by 20% "
    "for 2 turns.",
    4, -3,
    proc={"trigger": "on_crit", "chance": 100, "icd": 3,
          "apply_effect": {"effect_id": "primalist_savage_frenzy",
                           "name": "Savage Frenzy", "effect_type": "buff",
                           "duration": 2, "max_stacks": 1,
                           "stat_mods": {"damage_dealt_pct": 20.0},
                           "on_target": False}},
    connect=["elemental_berserker"],
    source="CoA: '15% of base mana, 3 min cooldown. Enrage you and your pet "
           "for 18 sec, increasing damage dealt by 20%, and attack speed and "
           "movement speed by 30%.' Movement speed is dropped (no "
           "positioning) and attack speed with it - haste here means acting "
           "more often, which is not what a 30% attack-speed buff on top of "
           "20% damage is for. The pet half is dropped. Built as a crit proc "
           "on a 3-turn internal cooldown rather than an activated ability, "
           "because Frontier has no primalist_savage_frenzy ability to "
           "unlock and a 3-minute cooldown is not a shape this tree has. "
           "The key is damage_dealt_pct, NOT all_damage: a proc-applied "
           "buff cannot reach all_damage, which abilities.py looks up "
           "through get_talent_effects() and that never includes status "
           "effects. damage_dealt_pct is the status-effect route to the "
           "same multiplier, read through get_status_stat_mod, and it takes "
           "percentage POINTS, so 20.0."))

N.append(node(
    "sharpened_claws", "Sharpened Claws",
    "Your critical strikes increase your armor penetration by 5% for 3 "
    "turns, stacking 3 times.",
    4, -1,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "primalist_sharpened_claws",
                           "name": "Sharpened Claws", "effect_type": "buff",
                           "duration": 3, "max_stacks": 3,
                           "stat_mods": {"armor_penetration_pct": 5.0},
                           "on_target": False}},
    connect=["pulverizing_strikes"],
    source="CoA verbatim: 'Your direct critical strikes now increase your and "
           "your pet's Armor penetration by 5% for 10 seconds, stacking 3 "
           "times.' The pet half is dropped - pet_armor is the pet's own "
           "armour, not its penetration, and there is no pet-penetration key. "
           "armor_penetration_pct is percentage POINTS and is read off the "
           "attacker by Monster.take_damage; a status effect reaches it "
           "because _recalculate_derived_stats folds status stat_mods into "
           "the same bonus pool as gear and talents, scaled by stacks."))

N.append(node(
    "tremors", "Tremors",
    "Your attacks have a 10% chance to make your Seismic abilities ready "
    "again at once.",
    4, 1,
    proc={"trigger": "on_damage_cast", "chance": 10, "icd": 1,
          "reset_cooldown": {"abilities": SEISMIC}},
    connect=["elemental_berserker"],
    source="CoA: 'Level 30 Passive. Periodic damage now has a 10% chance to "
           "reset the cooldown of your Seismic abilties and cause your next "
           "cast within 10 seconds to be free of cost.' Rerouted off periodic "
           "damage onto casts, same reason as Rips and Tears - no "
           "periodic-tick trigger exists. The free-cast rider is dropped: "
           "there is no 'next cast is free' payload, and a cost reduction "
           "would be a different talent. CoA's 10% chance is kept exactly, "
           "with a 1-turn internal cooldown so it cannot chain."))

# ---- tier 5 -------------------------------------------------------------
N.append(unlock(
    "bring_me_their_bones", "Bring Me Their Bones",
    "primalist_bring_me_their_bones",
    "Mark an enemy, then break it open.",
    5, -3, connect=["elemental_berserker"],
    source="CoA: 'Mark an enemy for 15 sec, causing damage dealt by your "
           "pet's abilities to the target to add a stack. At 5 stacks, your "
           "pet consumes this buff to deal damage ignoring Armor.' The whole "
           "stack-and-consume wrapper is pet-proc driven and therefore not "
           "buildable; the ability itself exists in Frontier and is unlocked "
           "here, which is the part that works. Kept from the previous tree, "
           "where it was named Frenzied Roar."))

N.append(node(
    "pulverizing_strikes", "Pulverizing Strikes",
    "Critical strikes with Totemic Smash deal 50% additional damage.",
    5, -1,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "ability_filter": ["primalist_totemic_smash"],
          "bonus_pct": 0.50},
    connect=["elemental_berserker"],
    source="CoA's SECOND Pulverize: 'Critical strikes with Totemic Smash now "
           "trigger the area of effect portion of its damage an additional "
           "time.' Renamed because CoA ships two different talents under the "
           "one name and a tree showing Pulverize twice reads like a bug. "
           "There is no payload that re-fires one component of an ability, so "
           "it is priced as bonus_pct, which adds to the SAME hit rather than "
           "staging a phantom follow-up - the closest honest equivalent of "
           "'that portion lands twice'."))

N.append(node(
    "primal_instincts", "Primal Instincts",
    "Increases your physical critical strike chance by 1% per rank.",
    5, 1, ranks=3,
    effects={"crit_chance_physical": 1.0},
    connect=["elemental_berserker"],
    source="Not a CoA node - carries the two scalar crit nodes the previous "
           "tree had under different names (Killer's Path, Hunter's Focus) "
           "into one place, because everything else at this depth is a proc "
           "and the tier needs a plain pick. crit_chance_physical is a "
           "PERCENT."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "elemental_berserker", "Elemental Berserker",
    "Increases the area damage dealt by Totemic Smash and Primal Shred by 30%.",
    6, 0,
    effects={"aoe_damage": 0.30},
    source="CoA verbatim: 'Increases the area damage dealt by Totemic Smash "
           "by 30%, but it now costs 5 additional Rage.' The Rage surcharge "
           "is dropped rather than authored as a negative _cost: the flat and "
           "percentage cost keys are both reduction-signed, so a surcharge "
           "has to be written negative, which is indistinguishable from the "
           "sign error eight talents in this project have already made and "
           "which the audit now flags. aoe_damage only applies to abilities "
           "whose target_type is enemy_aoe - Totemic Smash and Primal Shred "
           "both are, which is why the description names both instead of "
           "promising a Totemic-Smash-only bonus it cannot deliver."))


def main():
    check = "--check" in sys.argv
    ids = [n["talent_id"] for n in TREE["nodes"]]
    assert len(ids) == len(set(ids)), "duplicate talent_id"
    names = [n["name"] for n in TREE["nodes"]]
    assert len(names) == len(set(names)), f"duplicate node NAME: {names}"
    for n in TREE["nodes"]:
        for c in n["connected_to"]:
            assert c in ids, f"{n['talent_id']} connects to unknown {c}"
    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    unlocks = sum(1 for n in TREE["nodes"] if "unlock_ability" in n["effects"])
    print(f"Primalist Wildwalker: {len(ids)} nodes, {procs} with procs, "
          f"{unlocks} unlocks")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
