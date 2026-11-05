#!/usr/bin/env python3
"""Rebuild Tinker's Demolition tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_tinker_demolition.py [--check]

SOURCE: data/reference/coa/tinker.json tab 73 - 38 real Demolition talents
from Ascension's own CoA Builder payload. Identity from
reference/coa_sidekick: Demolition is "Closest to Survival Hunter,
reflavored fully ranged instead of melee" - a RANGED DPS built on bombs,
burning and a stacking fire debuff.

The shipped tree was 22 nodes, 21 of them a bare number, on real CoA names
(Explosives Expert, Gazlowe's Wisdom, Sparked and Ready!, The BIG Guns!,
Rockadier, Buster Scope). Same pattern as Mechanics: names kept, mechanics
replaced.

NAPALM IS THE SPEC, and the old tree did not have it at all. CoA's Demolition
turns on a stacking fire debuff - "Fire Damage taken increased and healing
received reduced by 3%, stacks 10 times" - that Bomb Toss and the
augmentations apply and that Scrap Shot and the drones then cash in. Three
talents here build it, two pay it off. <school>_damage_taken_pct is a key
the engine builds by interpolation, so fire_damage_taken_pct is live.

TURN-BASED CUTS. Dropped: Mega Scope (range), Build: Oil-Spill Pylon (ground
targeting), Flamethrowing's 30-yard line, and the movement-slow halves of
Firepot Drone. Charges (Firepot Drone's "3 charges, 10 sec recharge") have
no engine support, so it becomes a cooldown. Several CoA nodes are the same
decision twice - Boom Hour and Buster Scope are both "crit on a bomb" - and
collapse into one.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/tinker_demolition.json"

TREE = {
    "spec_name": "Tinker Demolition",
    "tree_id": "tinker_demolition",
    "description": ("Ranged demolitionist - stacks napalm on a target and "
                    "then sets the whole pile alight."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from data/reference/coa/tinker.json tab 73 "
        "(38 real CoA Demolition talents) with identity from "
        "reference/coa_sidekick ('Closest to Survival Hunter, reflavored "
        "fully ranged'). Replaces a 22-node tree carrying real CoA names on "
        "21 pure-scalar effects, and which had no Napalm mechanic at all "
        "despite Napalm being what the spec is built around."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}

NAPALM = {
    "effect_id": "tinker_napalm", "name": "Napalm", "duration": 3,
    "max_stacks": 10, "school": "fire",
    # healing_taken_pct, NOT healing_received_pct. CoA's own tooltips say
    # "healing received", and character.py:2895 names that wording as the
    # CoA-side alias - but the key the engine reads is healing_taken_pct,
    # on both Character.heal and Monster. The alias spelling is dead data.
    # Both values are PERCENT, not fractions: monster.py divides by 100.
    "stat_mods": {"fire_damage_taken_pct": 3.0, "healing_taken_pct": -3.0},
}


def node(nid, name, desc, tier, x, y, *, ranks=1, effects=None, proc=None,
         connect=None, source="", active=False):
    entry = {
        "talent_id": f"tinker_demolition_{nid}",
        "name": name,
        "description": desc,
        "node_type": "active" if active else "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": y,
        "effects": effects or {},
        "connected_to": [f"tinker_demolition_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


def unlock(nid, name, ability, blurb, tier, x, y, *, connect=None, source=""):
    """A node whose job is to TEACH an ability.

    These are not optional decoration. Every ability below carries
    "requires_talent": true, which tells combat/abilities.py not to learn it
    from level_req alone - so an ability with no unlock node anywhere is
    unobtainable forever. The first version of this rebuild dropped all four
    and stranded Bomb Toss, Spider Bomb, Rocket Launcher and Hyperblast
    Barrage. tools/qa_abilities_obtainable.py now fails the build if that
    happens again.
    """
    return node(nid, name, f"Learn {name.rstrip('!')}. {blurb}", tier, x, y,
                effects={"unlock_ability": ability}, connect=connect,
                source=source, active=True)


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "incendiary_bullets", "Incendiary Bullets",
    "Increases the damage of Scrap Shot by 15% per rank and your chance to hit by 2%.",
    0, -4, -6, ranks=2,
    effects={"ability_tinker_scrap_shot_damage": 0.15, "hit_rating": 2.0},
    connect=["bomb_builder"],
    source="CoA verbatim: 'Increases the damage of Scrap Shot by 15% and "
           "increases your chance to hit by 2%.'"))

N.append(node(
    "bomb_builder", "Bomb Builder",
    "Increases Fire damage dealt by you and your constructs by 5%.",
    0, -2, -6,
    effects={"fire_spell_power": 0.05, "pet_damage": 0.05},
    connect=["war_crimes"],
    source="CoA: 'Increases your and your summons Fire Damage dealt by 5%.'"))

N.append(node(
    "boom_hour", "Boom Hour",
    "Increases the critical strike chance of Bomb Toss by 10% and the critical "
    "damage of Rocket Launcher by 10%.",
    0, 0, -6,
    effects={"ability_tinker_bomb_toss_crit": 10.0,
             "ability_tinker_rocket_launcher_crit_damage": 0.10},
    connect=["war_crimes"],
    source="CoA has TWO near-identical nodes here - Boom Hour ('crit chance of "
           "Bomb Toss and Firepot Drone by 10%') and Buster Scope ('critical "
           "damage of Rocket Launcher by 10%'). With ~22 picks in a turn-based "
           "tree, two separate crit passives is one decision wearing two hats, "
           "so they are merged. Firepot Drone has no ability here."))

N.append(node(
    "explosives_expert", "Explosives Expert",
    "Your critical strikes and your constructs' restore mana.",
    0, 2, -6,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "grant_resource": {"resource": "mana", "amount": 40}},
    connect=["sparked_and_ready"],
    source="CoA: 'Direct harmful ability critical strikes from you or your "
           "summons now restores 4% of your maximum mana.' Replaces a "
           "pure-scalar node of the same name."))

N.append(node(
    "tank_buster", "Tank Buster",
    "Your Scrap Shot ignores 25% of the target's armor.",
    0, 4, -6,
    effects={"armor_penetration_pct": 25.0},
    connect=["sparked_and_ready"],
    source="CoA: 'Your Scrap Shot now ignores 25% of the target's Armor when "
           "damaging Burning targets.' The burning condition is not expressible "
           "- there is no per-ability conditional armor pen - so it applies "
           "flat, which is a real buff over CoA and is said so here rather "
           "than hidden."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "war_crimes", "War Crimes",
    "Bomb Toss coats the target in napalm, increasing Fire damage it takes by "
    "3% and reducing healing it receives by 3% for 3 turns, stacking 10 times.",
    1, -3, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["tinker_bomb_toss"],
          "apply_effect": dict(NAPALM)},
    connect=["drone_striker"],
    source="CoA: 'Damage dealt by Explosive Augmentation and Tracer "
           "Augmentation now has a 50% chance to apply an additional stack of "
           "Napalm.' Moved onto Bomb Toss and made reliable: this is the node "
           "that INTRODUCES Napalm to the tree, and a 50% chance on two "
           "augmentations would leave the spec's defining debuff absent most "
           "fights. 8 sec -> 3 turns."))

N.append(node(
    "sparked_and_ready", "Sparked and Ready!",
    "Your Fire damage has a 15% chance to ready a Rocket Launcher, resetting "
    "its cooldown.",
    1, -1, -4,
    proc={"trigger": "on_damage_cast", "chance": 15, "icd": 1,
          "reset_cooldown": ["tinker_rocket_launcher"]},
    connect=["aftermath"],
    source="CoA: 'Fire damage dealt has a 5% chance to grant Sparked and "
           "Ready!, causing your next Rocket Launcher within 10 sec to be "
           "instant cast and deal 20% increased damage.' Instant-cast means "
           "nothing here, so the payoff is the cooldown reset; 5% -> 15% "
           "because a turn is far longer than a real-time GCD and 5% per CAST "
           "would almost never fire. Replaces a pure-scalar node."))

N.append(node(
    "i_need_more_explosions", "I Need More Explosions!",
    "Increases the damage of Sticky Bomb by 5% per rank.",
    1, 1, -4, ranks=3,
    effects={"ability_tinker_sticky_bomb_damage": 0.05},
    connect=["target_acquired"],
    source="CoA verbatim. Was already a scalar in CoA, so it stays one. "
           "SPLIT from 1 rank of 15% into 3 ranks of 5% - the same ceiling, "
           "not a buff. The tree needed more points in its lower tiers to "
           "make its own top tiers reachable at all: tier_requirements gate "
           "tier 5 at 25 points and tier 6 at 30, and the rebuilt tree held "
           "27 points in total with 24 below tier 5, so both tiers were "
           "dead. See tools/qa_talent_tiers_reachable.py."))

N.append(node(
    "machine_synergy", "Machine Synergy",
    "Scrap Shot drives your constructs harder, raising their damage by 5% for "
    "2 turns, stacking 3 times.",
    1, 3, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["tinker_scrap_shot"],
          "apply_effect": {"effect_id": "tinker_machine_synergy",
                           "name": "Machine Synergy", "duration": 2,
                           "max_stacks": 3,
                           "stat_mods": {"pet_damage": 0.05}}},
    connect=["target_acquired"],
    source="CoA: 'Casting Scrap Shot now adds a stack of Machine Synergy to "
           "your active pet and Sentry Turret... 5% damage and 3% haste, "
           "stacking 3 times, for 6 seconds.' Pet haste is not a key here, so "
           "the damage half carries it. 6 sec -> 2 turns."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "drone_striker", "Drone Striker",
    "Scrap Shot drives another stack of napalm into the target.",
    2, -4, -2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["tinker_scrap_shot"],
          "apply_effect": dict(NAPALM)},
    connect=["grenadier"],
    source="CoA: 'Firepot Drone and Scrap Shot now deal 2% increased damage "
           "for each stack of Napalm on the enemy.' NOT built as written, and "
           "deliberately. That per-stack scaling already lives on the ABILITY "
           "(tinker_scrap_shot carries scales_with_target_stacks_of + "
           "damage_per_stack_pct 0.02) and applies whether or not this talent "
           "is spent; there is no effect key that switches it on, so a node "
           "claiming to grant it would grant nothing. Deleting the node was "
           "the other option and is what tinker_scrap_shot's own note "
           "assumed - but three nodes connect through this slot. So the node "
           "keeps CoA's INTENT, 'Scrap Shot gets more out of Napalm', via the "
           "half that is buildable: it puts more Napalm on the target, which "
           "the ability's native scaling then reads. Third Napalm applier in "
           "the tree, matching CoA, which also has three."))

N.append(node(
    "aftermath", "Aftermath",
    "Casting Sticky Bomb makes your next Scrap Shot hit 25% harder.",
    2, -2, -2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["tinker_sticky_bomb"],
          "apply_effect": {"effect_id": "tinker_aftermath", "name": "Aftermath",
                           "duration": 2, "max_stacks": 1,
                           "stat_mods": {"ability_tinker_scrap_shot_damage": 0.25}}},
    connect=["bombastic"],
    source="CoA: 'Casting Sticky Bomb now causes your next 2 Scrap Shots "
           "within 10 seconds to cast -50% faster and deal 25% increased "
           "damage.' Cast speed is meaningless here; the damage half becomes a "
           "2-turn buff."))

N.append(node(
    "target_acquired", "Target Acquired",
    "Your Sticky Bomb and Spider Bomb deal 15% more damage per rank to a "
    "lone target.",
    2, 0, -2, ranks=2,
    effects={"ability_tinker_sticky_bomb_damage": 0.15,
             "ability_tinker_spider_bomb_damage": 0.15},
    connect=["bombastic"],
    source="CoA: '...30% increased damage when it strikes only 1 target.' "
           "There is no single-target conditional on an ability's damage here, "
           "so it applies always. Stated plainly: this is stronger than CoA's."))

N.append(node(
    "duobombers", "Duobombers",
    "Build: Spider Bomb sends out a second bomb, dealing 100% more damage.",
    2, 2, -2,
    effects={"ability_tinker_spider_bomb_damage": 1.00},
    connect=["rocket_engineering"],
    source="CoA: 'Build: Spider Bomb now creates an additional Spider Bomb.' "
           "Two bombs is twice the damage, and doubling the ability is a far "
           "simpler truth than modelling a second summon."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "grenadier", "Grenadier",
    "When napalm reaches 5 stacks the target ignites, taking Fire damage over "
    "3 turns.",
    3, -3, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 2,
          "apply_effect": {"effect_id": "tinker_ignition", "name": "Ignition",
                           "duration": 3, "max_stacks": 1, "school": "fire",
                           "dot_damage": 40}},
    connect=["rockadier"],
    source="CoA: 'When you reach 5 stacks of Napalm on a target you refresh 1 "
           "charge of Build: Firepot Drone.' No Firepot Drone and no charges "
           "here, so the payoff is reflavoured as the fire it would have "
           "delivered. The 5-stack condition is not expressible either; a "
           "2-turn internal cooldown stands in for the pacing."))

N.append(node(
    "bombastic", "Bombastic",
    "Casting Build: Spider Bomb resets the cooldown of Bomb Toss.",
    3, -1, 0,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["tinker_spider_bomb"],
          "reset_cooldown": ["tinker_bomb_toss"]},
    connect=["gazlowes_wisdom"],
    source="CoA: 'Casting Build: Spider Bomb now resets the cooldown of Bomb "
           "Toss and causes your next Bomb Toss within 15 seconds to trigger "
           "no cooldown, global cooldown, or cost.' The reset ports exactly; "
           "the free-cast rider is the same effect twice in an engine with no "
           "GCD, so it is dropped."))

N.append(node(
    "rocket_engineering", "Rocket Engineering",
    "Your critical strikes drive another stack of napalm into the target.",
    3, 1, 0,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "apply_effect": dict(NAPALM)},
    connect=["surprise_launch"],
    source="CoA: 'Direct harmful ability critical strikes now apply an "
           "additional stack of Tracer Augmentation to the target.' Tracer "
           "Augmentation's own stacking mark is not modelled; routed into "
           "Napalm, which is the stacking mark this tree actually has."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "surprise_launch", "Surprise Launch!",
    "Rocket Launcher always critically strikes targets coated in napalm.",
    4, 0, 2,
    effects={"ability_tinker_rocket_launcher_crit": 100.0},
    connect=["bomb_squad"],
    source="CoA: 'When Rocket Launcher is used on enemies affected by Sticky "
           "Bomb it is now guaranteed to critically strike.' The condition "
           "cannot be expressed, so this is a flat guaranteed crit on one "
           "ability - powerful, and deliberately placed at tier 4 behind two "
           "napalm nodes to keep the fantasy intact even though the engine "
           "will not enforce it."))

N.append(node(
    "gazlowes_wisdom", "Gazlowe's Wisdom",
    "Sticky Bomb deals 20% more damage, and all of your area attacks deal "
    "15% more.",
    4, -2, 2,
    effects={"ability_tinker_sticky_bomb_damage": 0.20, "aoe_damage": 0.15},
    connect=["bomb_squad"],
    source="CoA: 'You now spawn 2 Shrapnel Mines under your target when Sticky "
           "Bomb explodes.' Ground-placed mines and Remote Detonation do not "
           "exist here; the shrapnel is expressed as the splash it represents. "
           "Replaces a pure-scalar node of the same name."))

N.append(node(
    "the_big_guns", "The BIG Guns!",
    "Increases your attack power by 2.5% per rank.",
    4, 2, 2, ranks=2,
    effects={"attack_power_pct": 2.5},
    connect=["rockadier"],
    source="CoA: 'Increases the attack power of all party and raid members 5%. "
           "Does not stack with similar effects. In addition, increases your "
           "ranged attack power by 3%.' Party-wide auras are not modelled, so "
           "only the self half is live - the description keeps the party "
           "wording because that is the talent's identity, and it is the one "
           "place here where flavour text outruns the mechanic."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "bomb_squad", "Bomb Squad",
    "Increases your spell power by 50% of your Agility.",
    5, -1, 4,
    effects={"spell_power_from_agility_pct": 0.50},
    connect=["rockadier"],
    source="CoA verbatim: 'Level 40 Passive. Increases your Fire spell power "
           "by 50% of Agility.' A stat conversion, which this engine handles "
           "natively through <target>_from_<source>_pct - but only for the "
           "targets in STAT_CONVERSION_TARGETS, and there is no per-school "
           "spell power in this engine, only spell_power. So the SCHOOL half "
           "is dropped rather than faked: an unknown pairing is skipped "
           "silently by character.py, which is the Clarity of the Heavens "
           "bug recorded in that dict's own comment. The value is a FRACTION "
           "(gained = source * pct), so 0.50, not 50.0 - as written it was a "
           "5000% conversion."))

N.append(node(
    "rocket_pack", "Rocket Pack",
    "Your Fire critical strikes cut the cooldown of your heaviest ordnance.",
    5, 1, 4,
    proc={"trigger": "on_crit", "chance": 100, "icd": 1,
          "reset_cooldown": ["tinker_hyperblast_barrage"]},
    connect=["rockadier"],
    source="CoA: 'Fire critical strikes now reduce the remaining cooldown of "
           "Rockadier by 3 sec.' There is no partial-cooldown-reduction proc "
           "payload - only reset_cooldown - so this resets on a 1-turn "
           "internal cooldown instead, pointed at Hyperblast Barrage, which is "
           "the big cooldown this kit actually has."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "rockadier", "Rockadier",
    "Your Scrap Shot and Rocket Launcher deal 100% more damage.",
    6, 0, 6,
    effects={"ability_tinker_scrap_shot_damage": 1.00,
             "ability_tinker_rocket_launcher_damage": 1.00},
    source="CoA: 'Empowers the next 6 Scrap Shots or Rocket Launchers within "
           "30 sec to deal additional Fire damage equal to 100% of the damage "
           "dealt to up to 10 enemies around the target.' A 3-minute cooldown "
           "window is not a talent shape this tree supports, so the capstone "
           "grants the empowerment permanently at the cost of being the last "
           "pick. Replaces a pure-scalar node of the same name. The splash "
           "half is DROPPED, not approximated: aoe_damage was on this node "
           "and did nothing for it, because neither tinker_scrap_shot nor "
           "tinker_rocket_launcher is is_aoe - aoe_damage would have buffed "
           "other abilities entirely, while the prose promised a splash that "
           "never happened. 'Nearby enemies' is also positional language in "
           "an engine with no positions."))


# ---- the ability unlocks ------------------------------------------------
# Restored after the first version of this rebuild dropped them. See
# unlock()'s docstring: without these four nodes the abilities cannot be
# learned at any level.
N.append(unlock(
    "bomb_toss", "Bomb Toss", "tinker_bomb_toss",
    "Lob a bomb that burns the target over several turns.",
    0, -6, -6, connect=["war_crimes"],
    source="Placed at tier 0 and wired into War Crimes on purpose: War "
           "Crimes procs Napalm off Bomb Toss, so the ability has to be "
           "learnable before the node that cashes it in. Was tier 1."))

N.append(unlock(
    "rocket_launcher", "Rocket Launcher", "tinker_rocket_launcher",
    "A heavy fire rocket aimed at one target.",
    1, 5, -4, connect=["rocket_engineering"],
    source="Also unlocked by the old Invention tree, which is wrong for a "
           "healer spec - it is a fire damage ability and Demolition is the "
           "ranged DPS tree, so it lives here only."))

N.append(unlock(
    "spider_bomb", "Build: Spider Bomb", "tinker_spider_bomb",
    "Builds a walking bomb that detonates among several enemies.",
    3, 3, 0, connect=["the_big_guns"],
    source="Duobombers doubles this ability's damage, so it has to be "
           "learnable in the same tree. Same tier as before."))

N.append(unlock(
    "hyperblast_barrage", "Hyperblast Barrage", "tinker_hyperblast_barrage",
    "Empties everything you have into a crowd at once.",
    4, 4, 2, connect=["rocket_pack"],
    source="Moved from tier 6 to tier 4 deliberately. Rocket Pack sits at "
           "tier 5 and its whole effect is resetting this ability's "
           "cooldown; with the unlock at tier 6 you could take the reset two "
           "tiers before you could take the thing being reset."))


def main():
    check = "--check" in sys.argv
    ids = [n["talent_id"] for n in TREE["nodes"]]
    assert len(ids) == len(set(ids)), "duplicate talent_id"
    for n in TREE["nodes"]:
        for c in n["connected_to"]:
            assert c in ids, f"{n['talent_id']} connects to unknown {c}"
    procs = sum(1 for n in TREE["nodes"] if n.get("proc"))
    print(f"Tinker Demolition: {len(TREE['nodes'])} nodes, {procs} with procs")
    if check:
        print("--check: nothing written")
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
