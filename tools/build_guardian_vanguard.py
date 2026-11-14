#!/usr/bin/env python3
"""Rebuild Guardian's Vanguard tree from the real CoA data.

    PYTHONPATH=. python3 tools/build_guardian_vanguard.py [--check]

SOURCE: data/reference/coa_worksheets/guardian.md and
data/reference/coa/guardian.json - 33 real Vanguard talents from
Ascension's own CoA Builder payload. Role: Tank.

Guardian measured the worst of the 16 classes left: 69 nodes, 11 procs,
58 of them scalar-only, 84%.

WHAT THE SPEC IS. A shield tank that lives on the block roll. Raise
Shield, Brace and the two Formations are the defensive cycle; Pulverize,
Ram and Heavy Blow pay for themselves in threat. ON_BLOCK IS A LIVE
TRIGGER, which is what makes this spec buildable at all - four CoA talents
hang off blocking and all four port.

THE BLOCK KEYS, and they do not agree:
  block            PERCENT - added to BASE_BLOCK_CHANCE and rolled against
                   0-100 (character.py:1355). block_chance is DEAD.
  block_value_pct  FRACTION - a raw multiplier on the value blocked
                   (character.py:1348)
  parry, dodge     PERCENT, rolled; face value - no DR since 7 Nov 2026
                   (character.py:1332). parry_chance and dodge_chance are
                   both DEAD.
So a node raising both the chance and the value carries a percent and a
fraction side by side, which is this project's standard hazard.

OTHER CONVENTIONS:
  stamina_pct, armor_pct, attack_power_pct   percentage POINTS
  all_damage, physical_damage, dot_damage,
    ability_*_damage                         FRACTION
  hit_rating, haste, ability_*_crit          PERCENT
  threat_generation_pct   FRACTION, NEGATIVE reduces
  physical_damage_taken_pct / magic_damage_taken_pct as a TALENT effect:
    FRACTION, NEGATIVE reduces. Inside a status effect: divided by 100 and
    POSITIVE increases.
  bare damage_taken_pct inside a status effect   read RAW
  *_cost_pct / *_cooldown_pct   FRACTION, POSITIVE MEANS A REDUCTION

DEAD KEYS THIS TREE WANTED. `expertise` is read by nothing, which takes
half of Stalwart. `max_energy_bonus` is read by nothing, which takes half
of Valiant Defender. `block_chance`, `parry_chance` and `dodge_chance` all
read plausibly and are all dead - the live names are `block`, `parry`,
`dodge`.

TURN-BASED CUTS. Every "in a line" and every yard, which is most of what a
Formation means. Silence has no key, which takes half of Hammer of the
Law. There is no critical-block mechanic, which takes Iron Barrier as
written, and no immunity key for incapacitate or knockback, which takes
Hold the Line - an ability Frontier does not have either.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data/talents/guardian_vanguard.json"

#: The spec's Energy-spending strikes.
STRIKES = ["guardian_pulverize", "guardian_ram", "guardian_broad_sweep"]

#: The two Formations.
FORMATIONS = ["guardian_tower_formation", "guardian_line_formation"]

TREE = {
    "spec_name": "Guardian Vanguard",
    "tree_id": "guardian_vanguard",
    "description": ("Shield and formation - a tank that turns every block "
                    "into threat, armour and retaliation."),
    "_source_note": (
        "Rebuilt 5 Nov 2026 from the 33 real CoA Vanguard talents (role "
        "Tank). Guardian measured the worst of the 16 classes remaining at "
        "84% scalar-only nodes. ON_BLOCK is a live trigger and all four of "
        "CoA's blocking talents port. Dead keys this tree wanted and did not "
        "get: expertise, max_energy_bonus, block_chance, parry_chance, "
        "dodge_chance - the live names are block, parry, dodge. No "
        "critical-block mechanic exists (Iron Barrier re-pointed) and no "
        "immunity key (Hold the Line dropped; Frontier has no such ability "
        "either)."),
    "tier_requirements": {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30},
    "nodes": [],
}


def node(nid, name, desc, tier, x, *, ranks=1, effects=None, proc=None,
         connect=None, source=""):
    entry = {
        "talent_id": f"guardian_vanguard_{nid}",
        "name": name,
        "description": desc,
        "node_type": "passive",
        "tier": tier,
        "max_points": ranks,
        "cost_per_point": 1,
        "hex_x": x,
        "hex_y": tier * 2 - 6,
        "effects": effects or {},
        "connected_to": [f"guardian_vanguard_{c}" for c in (connect or [])],
    }
    if proc:
        entry["proc"] = proc
    if source:
        entry["_source"] = source
    return entry


N = TREE["nodes"]

# ---- tier 0 -------------------------------------------------------------
N.append(node(
    "iron_guardian", "Iron Guardian",
    "Increases your Stamina by 15%.",
    0, -5,
    effects={"stamina_pct": 15.0},
    connect=["heavy_expert"],
    source="CoA over 3 ranks: 'Increases your Stamina by 5%.' Authored as the "
           "full-investment CEILING at one rank and left to the rank policy to "
           "spread - NOT hand-authored at ranks=3, which would have kept 15.0 "
           "per rank and delivered 45% at full investment, because "
           "get_effective_effects() multiplies every numeric effect by points "
           "spent. stamina_pct takes percentage POINTS. The "
           "worksheet tagged this 'needs: pet-summon', which is wrong - "
           "there is no Iron Guardian pet in CoA's text, and the Guardian "
           "summons nothing (see tools/qa_pet_keys.py)."))

N.append(node(
    "heavy_expert", "Heavy Expert",
    "Increases your chance to parry and dodge by 4% and your armour by 20%.",
    0, -3,
    effects={"parry": 4.0, "dodge": 4.0, "armor_pct": 20.0},
    connect=["knights_conviction"],
    source="CoA verbatim: 'Increases your chance to parry and dodge by 4% "
           "and increase your Armor contribution from mail and plate items "
           "by 20%.' No key reads armour by item class, so the 20% applies to "
           "all armour - the Guardian wears plate anyway. THE LIVE KEYS ARE "
           "`parry` AND `dodge`, both PERCENT; parry_chance and dodge_chance "
           "read plausibly and are read by nothing. Dodge passes through "
           "face value since 7 Nov 2026, so 4% dodge is exactly 4% "
           "less than 4% parry."))

N.append(node(
    "knights_conviction", "Knight's Conviction",
    "Increases your block value by 50% and your chance to block by 2%.",
    0, -1,
    effects={"block_value_pct": 0.50, "block": 2.0},
    connect=["seasoned_fighter"],
    source="CoA over 2 ranks: 'Increases the block value provided by Raise "
           "Shield by 25% and your block chance by 1%.' Doubled for the two "
           "ranks. 'Provided by Raise Shield' cannot be scoped - block value "
           "is a character stat, not an ability's - so it applies always. "
           "TWO UNITS IN ONE EFFECTS BLOCK: block_value_pct is a raw "
           "FRACTION (0.50 is +50%) and `block` is a PERCENT added to the "
           "base chance and rolled against 0-100 (2.0 is +2 points)."))

N.append(node(
    "stalwart", "Stalwart",
    "Increases your block value by 20% and your expertise by 4.",
    0, 1,
    effects={"block_value_pct": 0.20, "expertise": 4.0},
    connect=["seasoned_fighter"],
    source="CoA over 2 ranks: 'Increases your block value by 10% and your "
           "expertise by 4.' Doubled for the two ranks - and BOTH HALVES NOW "
           "PORT. `expertise` was a dead key when this tree was first "
           "rebuilt: it reduces a target's dodge and parry, and monsters had "
           "neither, so Monster.take_damage rolled no avoidance at all. Kyle "
           "had creature avoidance encoded the same day (dodge on every "
           "template, parry on humanoids only, block as a shield hook), which "
           "made expertise live, so the half that was dropped is restored. "
           "It is in PERCENTAGE POINTS and subtracts from the target's dodge "
           "AND parry independently, as in WoW: 4 expertise takes a "
           "humanoid_warrior from 13% avoidance to 5%."))

N.append(node(
    "seasoned_fighter", "Seasoned Fighter",
    "Reduces the Energy cost of Pulverize, Ram and Broad Sweep by 10%.",
    0, 3,
    effects={f"ability_{a}_cost_pct": 0.10 for a in STRIKES},
    connect=["footmans_call"],
    source="CoA verbatim. All three abilities exist in Frontier and the "
           "Guardian's resource is Energy (abilities.py:153), so the costs "
           "are real. POSITIVE reduces."))

# ---- tier 1 -------------------------------------------------------------
N.append(node(
    "bulwark", "Bulwark",
    "Increases your block value by 25% and your chance to hit by 5%.",
    1, -4,
    effects={"block_value_pct": 0.25, "hit_rating": 5.0},
    connect=["retaliation"],
    source="CoA's level 20 passive: 'Increases your block value by 25% and "
           "your hit rating by 5% of your Stamina.' The block half ports "
           "exactly. The hit conversion does NOT - hit_rating is not in "
           "STAT_CONVERSION_TARGETS, the same wall that took the spell-hit "
           "half of the Witch Doctor's Voodoo Power - so it is paid as a flat "
           "5% hit instead, which works as a direct stat even though it "
           "cannot be a conversion target."))

N.append(node(
    "footmans_call", "Footman's Call",
    "Increases the damage of Pulverize by 20%.",
    1, -2,
    effects={"ability_guardian_pulverize_damage": 0.20},
    connect=["retaliation"],
    source="CoA verbatim: 'Damage dealt by Pulverize is increased by 15, plus "
           "an additional amount scaling with your block value.' No key makes "
           "an ability's damage scale off a defensive stat - the coefficients "
           "live on the ability - so the whole thing is expressed as damage, "
           "which is what a block-value rider would have delivered on a tank "
           "already stacking block value from three nodes in tier 0."))

N.append(node(
    "with_honor", "With Honor",
    "Reduces the cooldown of Ram by 25%.",
    1, 0,
    effects={"ability_guardian_ram_cooldown_pct": 0.25},
    connect=["vanguards_shield"],
    source="CoA verbatim: 'Reduces the cooldown of Ram by -4 sec.' Expressed "
           "as a percentage because a flat second count is below a turn. "
           "POSITIVE reduces, so CoA's minus sign is dropped - authoring "
           "-0.25 would have LENGTHENED the cooldown."))

N.append(node(
    "honorbound", "Honorbound",
    "Reduces the Energy cost of Shield Challenge by 50%.",
    1, 2,
    effects={"ability_guardian_shield_challenge_cost_pct": 0.50},
    connect=["vanguards_shield"],
    source="CoA verbatim: 'Removes the Energy cost of Shield Challenge.' A "
           "full cost removal is expressible (1.0) but makes the ability free "
           "forever from a tier-1 node, so it is priced at half. CoA pairs "
           "this with Shieldbound ('no longer has a cooldown, but costs 10 "
           "additional Energy'), which is NOT built: nothing removes an "
           "ability's cooldown outright, and no key adds to a cost - "
           "_cost_pct is positive-reduces, so the trade-off cannot be "
           "expressed in either direction."))

N.append(node(
    "retaliation", "Retaliation",
    "Blocking an attack strikes the attacker back for physical damage.",
    1, 4,
    proc={"trigger": "on_block", "chance": 100, "icd": 0,
          "damage_flat": 55, "school": "physical"},
    connect=["iron_barrier"],
    source="CoA verbatim: 'Successful blocks now deal 51 + 5% AP Physical "
           "damage to the attacker, scaling with defense rating. Can only "
           "occur once per sec.' PORTS ALMOST EXACTLY - on_block is a live "
           "trigger and damage_flat with a school is a live payload. CoA's 51 "
           "becomes 55 flat; the AP and defense-rating riders cannot be read "
           "into a payload, which is why it is flat. 'Once per sec' needs no "
           "internal cooldown when a turn is three seconds."))

# ---- tier 2 -------------------------------------------------------------
N.append(node(
    "iron_barrier", "Iron Barrier",
    "Blocking an attack hardens your guard, raising your block value by 15% "
    "for 3 turns.",
    2, -4,
    proc={"trigger": "on_block", "chance": 100, "icd": 1,
          "apply_effect": {"effect_id": "guardian_iron_barrier",
                           "name": "Iron Barrier", "effect_type": "buff",
                           "duration": 3, "max_stacks": 1,
                           "stat_mods": {"block_value_pct": 0.15},
                           "on_target": False}},
    connect=["vanguards_might"],
    source="CoA's level 30 passive: 'Your successful blocks now have a 50% "
           "chance to critically block for twice the normal amount.' THERE IS "
           "NO CRITICAL BLOCK MECHANIC - blocking resolves as a flat value "
           "against the hit, with no crit roll anywhere in that path - so a "
           "doubled block cannot happen. Rebuilt as a block that makes the "
           "next blocks bigger, which is the same outcome spread over turns "
           "instead of landing at random. block_value_pct IS READ RAW ON BOTH "
           "SIDES - a fraction as a talent effect AND inside a status effect, "
           "unlike max_health_pct and healing_taken_pct, which flip between "
           "the two. My first draft authored 15.0 here on the assumption it "
           "flipped, which audit_talents reported as 1500%; 15% is 0.15."))

N.append(node(
    "vanguards_shield", "Vanguard's Shield",
    "Blocking or striking builds your guard, reducing magic damage taken by "
    "2% per stack for 10 turns, stacking 10 times.",
    2, -2,
    proc={"trigger": "on_block", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "guardian_vanguards_shield",
                           "name": "Vanguard's Shield", "effect_type": "buff",
                           "duration": 10, "max_stacks": 10,
                           "stat_mods": {"magic_damage_taken_pct": -2.0},
                           "on_target": False}},
    connect=["resilient"],
    source="CoA verbatim: 'Blocking an attack or landing an auto attack now "
           "grants a stack of Vanguard for 1 min, stacking 10 times. Magic "
           "Damage taken reduced by 2%. Whenever you are hit by a spell, you "
           "lose 1 stack of this effect.' CoA's 2% and 10 stacks kept, and 1 "
           "min is 10 turns. THE SPEND-ON-SPELL-HIT HALF IS DROPPED: no "
           "payload removes a stack of an effect, so the ramp has no drain "
           "and this is stronger than CoA's. The auto-attack half is dropped "
           "too, so the stacks come from blocking alone rather than from two "
           "triggers - a second proc would double-stack on a turn where both "
           "happen. INSIDE A STATUS EFFECT magic_damage_taken_pct is divided "
           "by 100 and POSITIVE INCREASES damage taken, so a reduction is "
           "NEGATIVE here; as a talent effect it is a raw fraction where "
           "negative also reduces."))

N.append(node(
    "resilient", "Resilient",
    "Blocking an attack steadies you, raising your maximum health by 8% for "
    "5 turns.",
    2, 0,
    proc={"trigger": "on_block", "chance": 100, "icd": 1,
          "apply_effect": {"effect_id": "guardian_resilient",
                           "name": "Resilient", "effect_type": "buff",
                           "duration": 5, "max_stacks": 1,
                           "stat_mods": {"max_health_pct": 8.0},
                           "on_target": False}},
    connect=["battle_wary"],
    source="CoA verbatim: 'Blocking an attack while Raise Shield is active "
           "now increases your maximum health by 308 + 10% Stamina + 11% AP "
           "for 15 seconds.' The 'while Raise Shield is active' gate does not "
           "exist - nothing reads whether a buff is up - so it fires on any "
           "block, with a 1-turn internal cooldown so a multi-hit turn does "
           "not refresh it repeatedly. The flat-plus-scaling number becomes a "
           "percentage, which is what it amounts to on a stamina-stacking "
           "tank. INSIDE A STATUS EFFECT max_health_pct takes percentage "
           "POINTS, so 8% is 8.0 - 0.08 would have been 0.08%, which is the "
           "mistake that shipped briefly on Witch Hunter's Black Knight."))

N.append(node(
    "battle_wary", "Battle Wary",
    "Reduces the cooldown of Advance and Battle Rush by 30%.",
    2, 2,
    effects={"ability_guardian_advance_cooldown_pct": 0.30,
             "ability_guardian_battle_rush_cooldown_pct": 0.30},
    connect=["kings_guard"],
    source="CoA verbatim. Both abilities exist in Frontier. POSITIVE "
           "reduces."))

# ---- tier 3 -------------------------------------------------------------
N.append(node(
    "vanguards_might", "Vanguard's Might",
    "Heavy Blow steels you, reducing all damage you take by 5% for 2 turns.",
    3, -4,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["guardian_heavy_blow"],
          "apply_effect": {"effect_id": "guardian_vanguards_might",
                           "name": "Vanguard's Might", "effect_type": "buff",
                           "duration": 2, "max_stacks": 1,
                           "stat_mods": {"damage_taken_pct": -0.05},
                           "on_target": False}},
    connect=["bring_down_the_hammer"],
    source="CoA verbatim: 'Your Heavy Blow now causes you to emanate an aura "
           "for 5 sec that reduces all damage taken by 5% for party members.' "
           "There is no party-aura mechanism, so the 5% lands on the Guardian "
           "and the description says 'you'. BARE damage_taken_pct IS READ "
           "RAW, so 5% is -0.05 - authoring -5.0 would be a 500% damage "
           "reduction, which is the immortality bug that shipped briefly on "
           "Boltslinger's Evasive at -20.0."))

N.append(node(
    "bring_down_the_hammer", "Bring Down The Hammer!",
    "Heavy Blow leaves the enemy reeling, dealing physical damage over 2 "
    "turns.",
    3, -2,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["guardian_heavy_blow"],
          "apply_effect": {"effect_id": "guardian_bring_down_the_hammer",
                           "name": "Bring Down The Hammer!",
                           "effect_type": "dot", "duration": 2,
                           "potency": 34, "damage_school": "physical",
                           "on_target": True}},
    connect=["valorous_strikes"],
    source="CoA verbatim: 'Damage dealt by Heavy Blow now deals an additional "
           "20% of the damage dealt every 1 sec for 3 seconds.' A repeated "
           "strike over 3 sec IS a dot, so this ports closely. The potency is "
           "flat rather than a share of the hit, because an apply_effect "
           "payload cannot read the triggering ability's damage."))

N.append(node(
    "kings_guard", "King's Guard",
    "Pulverize and Ram have a 10% chance to ready Raise Shield again.",
    3, 0,
    proc={"trigger": "on_damage_cast", "chance": 10, "icd": 0,
          "ability_filter": ["guardian_pulverize", "guardian_ram"],
          "reset_cooldown": ["guardian_raise_shield"]},
    connect=["shield_unit"],
    source="CoA verbatim: 'Your Pulverize and Ram now have a 10% chance to "
           "reset the cooldown of Raise Shield.' PORTS EXACTLY - CoA's 10%, "
           "and reset_cooldown as a BARE LIST is a full reset, which is what "
           "'reset the cooldown' means. Note the chance is authored at 10 and "
           "the rank policy will spread it: at 3 ranks it becomes 3, reaching "
           "9% at full investment rather than 10, which the description "
           "rounds to 10% as the ceiling."))

N.append(node(
    "valorous_strikes", "Valorous Strikes",
    "Your weapon swings have a 10% chance to strike twice and leave the "
    "target 3% less likely to hit you for 5 turns.",
    3, 2,
    proc={"trigger": "on_weapon_swing", "chance": 10, "icd": 0,
          "extra_attack": True,
          "apply_effect": {"effect_id": "guardian_valorous_strikes",
                           "name": "Valorous Strikes",
                           "effect_type": "debuff", "duration": 5,
                           "max_stacks": 1,
                           "stat_mods": {"hit_rating": -3.0},
                           "on_target": True}},
    connect=["order_in_the_court"],
    source="CoA verbatim: 'Auto attacks now have a 10% chance to strike an "
           "additional time and reduce your target's chance to hit by -3% for "
           "15 seconds.' PORTS EXACTLY - on_weapon_swing is the live auto-"
           "attack trigger, extra_attack is a live boolean payload, and 15 "
           "sec is 5 turns. CoA's 10% and 3% both kept. A tank reducing the "
           "boss's hit chance is real mitigation here because hit_rating is "
           "rolled on the attacker's side."))

# ---- tier 4 -------------------------------------------------------------
N.append(node(
    "shield_unit", "Shield Unit",
    "Taking damage stokes your fury, raising your attack power by 3% per "
    "stack for 10 turns, stacking 5 times.",
    4, -3,
    proc={"trigger": "on_damage_taken", "chance": 100, "icd": 0,
          "apply_effect": {"effect_id": "guardian_shield_unit",
                           "name": "Shield Unit", "effect_type": "buff",
                           "duration": 10, "max_stacks": 5,
                           "stat_mods": {"attack_power_pct": 3.0},
                           "on_target": False}},
    connect=["plate_buster"],
    source="CoA verbatim: 'Each time you take damage, you gain 5% of the "
           "damage taken as attack power for 1 min.' NOTHING CONVERTS AN "
           "EVENT'S AMOUNT INTO A STAT - a payload cannot read the hit's size "
           "into a stat_mod - so an uncapped percentage of damage taken is "
           "not expressible, and it would be unbounded on a tank regardless. "
           "Rebuilt as a stacking percentage with a ceiling: 5 stacks of 3% "
           "is 15% attack power at cap, and 1 min is 10 turns. "
           "attack_power_pct takes percentage POINTS."))

N.append(node(
    "order_in_the_court", "Order In The Court",
    "Hammer of the Law cows the enemy, reducing the damage they deal by 10% "
    "for 3 turns.",
    4, -1,
    proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
          "ability_filter": ["guardian_hammer_of_the_law"],
          "apply_effect": {"effect_id": "guardian_order_in_the_court",
                           "name": "Order In The Court",
                           "effect_type": "debuff", "duration": 3,
                           "max_stacks": 1,
                           "stat_mods": {"damage_dealt_pct": -10.0},
                           "on_target": True}},
    connect=["the_green_tower"],
    source="CoA verbatim: 'Damage dealt by Hammer of the Law now reduces the "
           "damage dealt by affected enemies by -10% for 8 seconds.' Ports "
           "exactly - CoA's 10%, and 8 sec is 3 turns. Hammer of the Law "
           "exists in Frontier; CoA's silence rider on the ability itself is "
           "not a talent and has no key anyway. damage_dealt_pct inside a "
           "status effect is percentage POINTS."))

N.append(node(
    "the_green_tower", "The Green Tower",
    "Reduces the Energy cost of your Formations by 25% and raises the threat "
    "they generate by 25%.",
    4, 1,
    effects={**{f"ability_{a}_cost_pct": 0.25 for a in FORMATIONS},
             "threat_generation_pct": 0.25},
    connect=["wreck_formation"],
    source="CoA verbatim: 'Reduces the Energy cost of your Formations and "
           "increases their effectiveness by 25%.' Both Formations exist in "
           "Frontier. 'Effectiveness' has no single key for a Formation - "
           "they are stances, not damage - so the 25% is paid as threat, "
           "which is what a tank's Formation is for and what the spec's own "
           "level 10 passive already keys on. threat_generation_pct is a "
           "FRACTION where POSITIVE increases, the opposite polarity to the "
           "_cost_pct keys beside it in the same block."))

N.append(node(
    "valiant_defender", "Valiant Defender",
    "Increases the damage of Pulverize and Broad Sweep by 10%.",
    4, 3,
    effects={"ability_guardian_pulverize_damage": 0.10,
             "ability_guardian_broad_sweep_damage": 0.10},
    connect=["wreck_formation"],
    source="CoA verbatim: 'Increases your maximum Energy by 15 and increases "
           "the damage of Pulverize and Broad Sweep by 10%.' THE MAXIMUM "
           "ENERGY HALF IS DROPPED: max_energy_bonus is read by nothing, and "
           "the primary resource pool is not talent-settable - the same shape "
           "as max_rage being hardcoded at 100. The damage half ports "
           "exactly."))

# ---- tier 5 -------------------------------------------------------------
N.append(node(
    "plate_buster", "Plate Buster",
    "Critical strikes with Ram bring Bastion a turn closer to ready.",
    5, -3,
    proc={"trigger": "on_crit", "chance": 100, "icd": 0,
          "ability_filter": ["guardian_ram"],
          "reset_cooldown": {"abilities": ["guardian_bastion"], "turns": 1}},
    connect=["shieldlords_strength"],
    source="CoA verbatim: 'Critical strikes with Ram now reduces the "
           "remaining cooldown of Hold the Line by 4 sec.' FRONTIER HAS NO "
           "HOLD THE LINE ABILITY, and CoA's version is an immunity to "
           "incapacitate, disorient, knockback and grip - none of which have "
           "a key here - so the target cannot exist either. Re-pointed at "
           "Bastion, the spec's real long-cooldown defensive, which is what "
           "Hold the Line occupies in CoA's kit. 4 sec is a turn."))

N.append(node(
    "wreck_formation", "Wreck Formation",
    "Melee critical strikes have a 50% chance to ready Hammer of the Law "
    "again.",
    5, -1,
    proc={"trigger": "on_crit", "chance": 50, "icd": 0,
          "reset_cooldown": ["guardian_hammer_of_the_law"]},
    connect=["shieldlords_strength"],
    source="CoA verbatim: 'Melee critical strikes now have a 50% chance to "
           "reset the cooldown of Hammer of the Law. Casting Standard of "
           "Valiance now increases your attack power by 10% for 6 sec.' The "
           "first half ports exactly - CoA's 50%, bare-list reset_cooldown "
           "for a full reset. The second half would need a second proc on a "
           "different trigger; it is dropped rather than merged, because "
           "on_crit would not have fired on Standard of Valiance, a self "
           "buff that deals no damage. THERE IS NO TRIGGER-SIDE MELEE FILTER "
           "- proc school only types a damage_flat payload - so this fires on "
           "any crit, which on a shield tank is almost always melee."))

N.append(node(
    "forceful_impact", "Forceful Impact",
    "Raise Shield and Heavy Blow extend Brace by 1 turn.",
    5, 1,
    effects={"ability_guardian_brace_duration": 1},
    connect=["shieldlords_strength"],
    source="CoA verbatim: 'Casting Raise Shield and Heavy Blow now extends "
           "the duration of your Brace by 1 sec. Brace cannot be extended "
           "beyond its maximum duration.' No payload extends a live effect's "
           "duration - consumes_stacks_of is the only thing that does and it "
           "reads the caster's own stacks to lengthen a DoT - so this is "
           "built as a flat duration bonus on Brace itself, which is the same "
           "outcome without the trigger. The small integer keeps this node "
           "out of the rank policy's reach."))

# ---- tier 6 -------------------------------------------------------------
N.append(node(
    "shieldlords_strength", "Shieldlord's Strength",
    "Increases your Stamina by 15% and the damage of Heavy Blow and Hammer "
    "of the Law by 40%.",
    6, 0,
    effects={"stamina_pct": 15.0,
             "ability_guardian_heavy_blow_damage": 0.40,
             "ability_guardian_hammer_of_the_law_damage": 0.40},
    source="CoA verbatim: 'You may now use two-handed Maces and can now equip "
           "two-handed Maces with a shield. Your Heavy Blow and Hammer of the "
           "Law now deal additional damage scaling with your Stamina and your "
           "Stamina is increased by 15%.' The weapon-rule half is not a "
           "talent effect - equip rules live on items, and a two-hander with "
           "a shield would need the slot system changed, which is well "
           "outside a talent. Stamina-scaling damage has no key (coefficients "
           "live on the ability), so it is paid as flat damage. CoA's 15% "
           "Stamina ports exactly, and stacks with Iron Guardian at tier 0 "
           "for 30% on a pure-Vanguard build. CoA's own Paragon node at this "
           "tier is the unresolved token '$32' and is not built."))


# ---- rank policy --------------------------------------------------------
# Kyle's call, 5 Nov 2026: multi-rank the real mechanics rather than padding
# the tree with flat scalars. tools/talent_ranks.spread() rescales so a
# ranked node lands on exactly the ceiling it had at one rank, and refuses
# nodes carrying small integer durations.
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
    print(f"Guardian Vanguard: {len(ids)} nodes, {procs} with procs, "
          f"{pts} points")
    if check:
        return 0
    OUT.write_text(json.dumps(TREE, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
