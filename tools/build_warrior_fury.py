#!/usr/bin/env python3
"""Rebuild Warrior Fury from the real 3.3.5a tree.

    PYTHONPATH=. python3 tools/build_warrior_fury.py

SOURCE: data/reference/wotlk/warrior.json (from Spell.dbc).
Worksheet: data/reference/wotlk_worksheets/warrior.md.

ROLE: two-weapon rage dump. Enrage effects, haste off crits, and shouts
that buff the party.

STANCE GATING IS USED HERE, and it is the first talent in the project to
use it. Improved Berserker Stance is written "while in Berserker Stance",
and a talent's require_form is checked against BOTH current_form and
current_stance (abilities.py:812), with combat/stances.py defining
battle / defensive / berserker. So the real conditional is buildable
exactly as written rather than being dropped or made unconditional.

ENRAGE AND WRECKING CREW MUST NOT STACK - the real talents both say so,
and Wrecking Crew lives in Arms. Both now apply an effect carrying
exclusive_group "warrior_enrage", so applying one drops the other
(status_effects.py:717). That is the mechanism CoA's Tinker rounds already
use for a one-at-a-time slot.

DEAD KEYS ROUTED AROUND: rage_generation_pct (Unbridled Wrath, Improved
Berserker Rage) - probed, zero read sites. Both deliver flat rage from a
proc instead.

NOT EXPRESSIBLE, and what each became:

    Armored to the Teeth   "+3 AP per 108 armor" needs armor as a
                           STAT_CONVERSION_SOURCE and it is not one (the
                           sources are strength, agility, intellect,
                           spirit, stamina, ap, attack_power, spell_power,
                           weapon, str_int) -> flat attack power
    Dual Wield Spec        no off-hand exists -> a small all-damage bonus,
                           deliberately under the conversion estimate
    Piercing Howl          no daze, no movement speed -> Intimidating
                           Shout duration
    Improved Cleave        modifies Cleave's "bonus damage" component,
                           which we do not model separately from its
                           damage -> a smaller straight damage bonus
    Blood Craze            no on-crit-TAKEN trigger -> on_damage_taken
    Death Wish             no such ability -> rides Berserker Rage, which
                           is the ability it most resembles
    Heroic Fury            no immobilisation to remove -> keeps only the
                           Intercept cooldown reset, which IS real
    Rampage                a talent effect can NEVER reach an ally -> the
                           warrior's own crit
    Bloodsurge             no Slam ability and no instant-cast mechanic
                           -> an extra attack off the same three abilities
    Titan's Grip           no weapon slots to change -> flat attack power

KEPT MANDATORY: Bloodthirst is the only unlock for warrior_bloodthirst,
which is requires_talent.

THE DAMAGE KEY INSIDE A PROC'S stat_mods MUST BE damage_dealt_pct, IN
PERCENTAGE POINTS. all_damage, physical_damage, spell_damage and the
per-school <school>_spell_damage keys are read through
get_talent_effect (abilities.py:1606-1610), which sums TALENTS AND THE
CURRENT STANCE and nothing else - a status effect's stat_mods go to
get_status_stat_mod instead, and the damage path reads exactly one key
from there: damage_dealt_pct (abilities.py:1680-1683, divided by 100).
So a proc-applied buff carrying all_damage is SILENT DEAD DATA. Stances
look like a counter-example and are not: stance stat_mods are folded
into get_talent_effects (character.py:628), so they reach the talent
bus. Proc-applied buffs are not.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from wotlk_tree_kit import Tree  # noqa: E402

#: Enrage and Arms' Wrecking Crew share this, so only one can be up -
#: both real talents say "does not stack with" the other.
ENRAGE_GROUP = "warrior_enrage"

T = Tree("warrior_fury", "Warrior Fury",
         "Two-weapon frenzy - rage, haste and relentless aggression.")

# ----------------------------------------------------------------- tier 0
T.node("armored_to_the_teeth", "Armored to the Teeth",
       "Increases your attack power by 1% per rank.",
       0, -2, 3, effects={"attack_power_pct": 1.0},
       source="WotLK row 0: 'Increases your attack power by 1/2/3 for every "
              "108 armor value you have.' DEPARTURE - armour is not a "
              "STAT_CONVERSION_SOURCE, so attack power cannot be derived "
              "from it; the sources are strength, agility, intellect, "
              "spirit, stamina, ap, attack_power, spell_power, weapon and "
              "str_int. Delivered as flat attack power instead. The "
              "outgoing version was armor_pct, which is the input side of "
              "the real talent rather than its output.")

T.node("booming_voice", "Booming Voice",
       "Increases the duration of your Battle Shout and Demoralizing Shout "
       "by 1 turn per rank.",
       0, 0, 2,
       effects={"ability_warrior_battle_shout_duration": 1,
                "ability_warrior_demoralizing_shout_duration": 1},
       source="WotLK row 0: 'Increases the area of effect and duration of "
              "your Battle Shout, Demoralizing Shout and Commanding Shout "
              "by 25%/50%.' Area of effect has no meaning here and "
              "Commanding Shout does not exist. ability_<id>_duration is "
              "FLAT turns and POSITIVE EXTENDS. Kept from the outgoing "
              "tree, corrected from 3 ranks to the real 2.")

T.node("cruelty", "Cruelty",
       "Increases your critical strike chance by 1% per rank.",
       0, 2, 5, effects={"crit_chance_physical": 1.0},
       source="WotLK row 0: 'Increases your chance to get a critical strike "
              "with melee weapons by 5%' over 5 ranks. Built verbatim, "
              "weapon gate dropped. Kept from the outgoing tree.")

# ----------------------------------------------------------------- tier 1
T.node("improved_cleave", "Improved Cleave",
       "Increases the damage of your Cleave by 15% per rank.",
       1, -5, 3, effects={"ability_warrior_cleave_damage": 0.15},
       connected_to=["armored_to_the_teeth"],
       source="WotLK row 1: 'Increases the bonus damage done by your Cleave "
              "ability by 40%/80%/120%.' DEPARTURE in magnitude - the real "
              "talent scales Cleave's flat BONUS damage component, which "
              "this engine does not model separately from the ability's "
              "damage, so authoring 40% per rank would be a 120% increase "
              "to the whole ability. 15% per rank reaching 45% is the "
              "conservative reading. Kept from the outgoing tree at the "
              "same value.")

T.node("improved_demoralizing_shout", "Improved Demoralizing Shout",
       "Increases the attack-power reduction of your Demoralizing Shout by "
       "8% per rank.",
       1, -3, 5,
       effects={"ability_warrior_demoralizing_shout_potency": 0.08},
       connected_to=["armored_to_the_teeth"],
       source="WotLK row 1: 'Increases the melee attack power reduction of "
              "your Demoralizing Shout by 8%-40%.' Built verbatim at the "
              "real 8% per rank over the real 5 ranks; the outgoing version "
              "was 3 ranks of 10%. ability_<id>_potency scales the "
              "ability's own stat_mods, which is exactly what this needs.")

T.node("piercing_howl", "Piercing Howl",
       "Increases the duration of your Intimidating Shout by 1 turn.",
       1, -1, 1,
       effects={"ability_warrior_intimidating_shout_duration": 1},
       connected_to=["booming_voice"],
       source="WotLK row 1: 'Causes all enemies within 10 yards to be "
              "Dazed, reducing movement speed by 50% for 6 sec.' DEPARTURE "
              "- no daze, no movement speed, no radius. Delivered as "
              "duration on the warrior's actual fear/crowd-control shout, "
              "which is the nearest thing in the kit. Kept from the "
              "outgoing tree.")

T.node("unbridled_wrath", "Unbridled Wrath",
       "Your swings have a 10% chance per rank to generate 5 Rage.",
       1, 1, 5,
       proc={"trigger": "on_weapon_swing", "chance": 10, "icd": 0,
             "grant_resource": {"resource": "rage", "amount": 5}},
       connected_to=["booming_voice"],
       source="WotLK row 1: 'Gives you a chance to generate an additional "
              "rage point when you deal melee damage with a weapon.' Built "
              "as the real mechanic. One rage is beneath notice against a "
              "100-point pool, so the amount is 5 and the chance carries "
              "the rank curve to 50%. Kept as a proc from the outgoing "
              "tree.")

T.node("blood_craze", "Blood Craze",
       "Being struck has a 33% chance per rank to regenerate health over 3 "
       "turns.",
       1, 3, 3,
       proc={"trigger": "on_damage_taken", "chance": 33, "icd": 1,
             "apply_effect": {"effect_id": "blood_craze",
                              "name": "Blood Craze",
                              "effect_type": "hot", "duration": 3,
                              "potency": 25, "on_target": False}},
       connected_to=["cruelty"],
       source="WotLK row 1: 'Regenerates 2%/4%/6% of your total Health over "
              "6 sec after being the victim of a critical strike.' "
              "DEPARTURE on the trigger - there is no on-crit-TAKEN event, "
              "only on_damage_taken, so icd 1 keeps it to once a turn "
              "rather than firing on everything. A proc-applied hot states "
              "PER-TURN healing as `potency`, and percentage-of-health "
              "healing is not available to a proc payload, so 25 a turn "
              "over 3 turns (6 seconds) is a flat equivalent. Kept as a "
              "proc from the outgoing tree.")

T.node("commanding_presence", "Commanding Presence",
       "Increases the attack power your Battle Shout grants by 5% per rank.",
       1, 5, 5,
       effects={"ability_warrior_battle_shout_potency": 0.05},
       connected_to=["cruelty"],
       source="WotLK row 1: 'Increases the melee attack power bonus of your "
              "Battle Shout and the health bonus of your Commanding Shout "
              "by 5%-25%.' Commanding Shout does not exist. Built verbatim "
              "for Battle Shout; kept from the outgoing tree, corrected "
              "from 8% to the real 5% per rank.")

# ----------------------------------------------------------------- tier 2
T.node("dual_wield_specialization", "Dual Wield Specialization",
       "Your two-weapon fighting increases all your damage by 1% per rank.",
       2, -5, 5, effects={"all_damage": 0.01},
       connected_to=["improved_cleave"],
       source="WotLK row 2: 'Increases the damage done by your offhand "
              "weapon by 5%-25%.' DEPARTURE - there is no off-hand in this "
              "engine and no off-hand damage key. An off-hand carries "
              "roughly a third of a dual-wielder's damage, so +25% off-hand "
              "is on the order of +8% total; 1% per rank reaching 5% is "
              "deliberately UNDER that, because the conversion is an "
              "estimate. The outgoing version was a proc.")

T.node("precision", "Precision",
       "Increases your chance to hit by 1% per rank.",
       2, -3, 3, effects={"hit_rating": 1.0},
       connected_to=["improved_demoralizing_shout"],
       source="WotLK row 2: 'Increases your chance to hit with melee "
              "weapons by 1%/2%/3%.' Built verbatim and kept from the "
              "outgoing tree. hit_rating is PERCENTAGE POINTS and is NOT a "
              "valid STAT_CONVERSION_TARGET - it can be granted directly "
              "but never converted into from another stat.")

T.node("improved_execute", "Improved Execute",
       "Reduces the Rage cost of your Execute by 2 per rank.",
       2, -1, 2, effects={"ability_warrior_execute_cost": 2},
       connected_to=["piercing_howl"],
       source="WotLK row 2: 'Reduces the rage cost of your Execute ability "
              "by 2/5.' Built at 2 per rank, reaching 4 against the real 5. "
              "Kept from the outgoing tree.")

T.node("death_wish", "Death Wish",
       "Your Berserker Rage now also increases your physical damage by 20% "
       "while increasing damage taken by 5%.",
       2, 1, 1,
       proc={"trigger": "on_cast", "chance": 100, "icd": 0,
             "ability_filter": ["warrior_berserker_rage"],
             "apply_effect": {"effect_id": "death_wish",
                              "name": "Death Wish",
                              "effect_type": "buff", "duration": 3,
                              "stat_mods": {"damage_dealt_pct": 20.0,
                                            "damage_taken_pct": 0.05},
                              "on_target": False}},
       connected_to=["unbridled_wrath"],
       source="WotLK row 2, NEW to our tree: 'When activated you become "
              "enraged, increasing your physical damage by 20% but "
              "increasing all damage taken by 5%. Lasts 30 sec.' DEPARTURE "
              "- there is no warrior_death_wish ability to unlock, so it "
              "rides Berserker Rage, the ability it most resembles. Both "
              "real numbers are kept. MIND THE UNITS: physical_damage is a "
              "FRACTION (0.20) while damage_taken_pct inside a status "
              "stat_mods is PERCENTAGE POINTS (5.0) - mixed conventions in "
              "one dict, which audit_talents is the only reliable check "
              "for. It is also Bloodthirst's prerequisite in the real tree, "
              "preserved below.")

T.node("enrage", "Enrage",
       "Being struck has a 6% chance per rank to enrage you, increasing all "
       "your damage by 10% for 4 turns.",
       2, 3, 5,
       proc={"trigger": "on_damage_taken", "chance": 6, "icd": 0,
             "apply_effect": {"effect_id": "enrage", "name": "Enrage",
                              "effect_type": "buff", "duration": 4,
                              "stat_mods": {"damage_dealt_pct": 10.0},
                              "exclusive_group": ENRAGE_GROUP,
                              "on_target": False}},
       connected_to=["blood_craze"],
       source="WotLK row 2: 'Gives you a 6%-30% chance to receive a 10% "
              "damage bonus for 12 sec after being the victim of a damaging "
              "attack. This effect does not stack with Wrecking Crew.' "
              "Built verbatim including the real 6%-per-rank curve to 30%, "
              "the real 10%, and the real 12 seconds (4 turns). THE "
              "NON-STACKING CLAUSE IS REAL AND NOW ENFORCED: both this and "
              "Arms' Wrecking Crew carry exclusive_group "
              f"'{ENRAGE_GROUP}', so applying either drops the other "
              "(status_effects.py:717) - the same one-at-a-time mechanism "
              "the Tinker's ammo rounds use. The outgoing version was a "
              "proc with no exclusivity, so an Arms/Fury hybrid could hold "
              "both.")

T.node("improved_intercept", "Improved Intercept",
       "Reduces the cooldown of your Intercept by 1 turn per rank.",
       2, 5, 2, effects={"ability_warrior_intercept_cooldown": 1},
       connected_to=["commanding_presence"],
       source="WotLK row 2, NEW to our tree: 'Reduces the cooldown of your "
              "Intercept ability by 5/10 sec.' ability_<id>_cooldown is "
              "FLAT turns; 10 seconds re-derives as 2 turns over 2 ranks.")

# ----------------------------------------------------------------- tier 3
T.node("improved_berserker_rage", "Improved Berserker Rage",
       "Your Berserker Rage generates 20 Rage.",
       3, -2, 2,
       proc={"trigger": "on_cast", "chance": 50, "icd": 0,
             "ability_filter": ["warrior_berserker_rage"],
             "grant_resource": {"resource": "rage", "amount": 20}},
       connected_to=["dual_wield_specialization"],
       source="WotLK row 3, NEW to our tree: 'The Berserker Rage ability "
              "will generate 10/20 rage when used.' Built as the real "
              "mechanic with the real 20 rage; the chance carries the rank "
              "curve to 100% because a proc's payload does not scale with "
              "points. A talent cannot modify an ability's own `generates` "
              "block, and rage_generation_pct is dead data.")

T.node("flurry", "Flurry",
       "Your critical strikes have a 20% chance per rank to quicken your "
       "attacks by 25% for 2 turns.",
       3, 0, 5,
       proc={"trigger": "on_crit", "chance": 20, "icd": 0,
             "apply_effect": {"effect_id": "flurry", "name": "Flurry",
                              "effect_type": "buff", "duration": 2,
                              "stat_mods": {"haste": 25},
                              "on_target": False}},
       connected_to=["enrage"],
       source="WotLK row 3: 'Increases your attack speed by 5%-25% for your "
              "next 3 swings after dealing a melee critical strike.' Built "
              "with the real 25% at full rank. 'Next 3 swings' is not "
              "expressible - nothing counts swings or consumes a buff on "
              "use - so it is a 2-turn window instead. Ranked by chance "
              "because a proc's payload does not scale. haste inside status "
              "stat_mods is PERCENTAGE POINTS. Kept as a proc from the "
              "outgoing tree.")

# ----------------------------------------------------------------- tier 4
T.node("intensify_rage", "Intensify Rage",
       "Reduces the cooldown of your Bloodrage, Berserker Rage and "
       "Recklessness by 1 turn per rank.",
       4, -4, 3,
       effects={"ability_warrior_bloodrage_cooldown": 1,
                "ability_warrior_berserker_rage_cooldown": 1,
                "ability_warrior_recklessness_cooldown": 1},
       connected_to=["improved_berserker_rage"],
       source="WotLK row 4: 'Reduces the cooldown of your Bloodrage, "
              "Berserker Rage, Recklessness and Death Wish abilities by "
              "11%/22%/33%.' All three real abilities that exist here are "
              "covered; Death Wish is a talent rather than an ability in "
              "our build. Authored as FLAT turns rather than the real "
              "percentage because _cooldown_pct would compound awkwardly "
              "across three different cooldowns. The outgoing version "
              "covered two of the three.")

T.node("furious_attacks", "Furious Attacks",
       "Your swings have a 25% chance per rank to reduce healing on the "
       "target by 25% for 3 turns.",
       4, -2, 2,
       proc={"trigger": "on_weapon_swing", "chance": 25, "icd": 0,
             "apply_effect": {"effect_id": "furious_attacks",
                              "name": "Furious Attacks",
                              "effect_type": "debuff", "duration": 3,
                              "stat_mods": {"healing_taken_pct": -25.0}}},
       connected_to=["improved_berserker_rage"],
       source="WotLK row 4: 'Your normal melee attacks have a chance to "
              "reduce all healing done to the target by 25% for 10 sec. "
              "This can stack up to 2 times.' Built with the real 25% and "
              "the real 10 seconds (3 turns). Stacking is dropped - "
              "max_stacks exists on StatusEffect but nothing in this engine "
              "READS a stack count, so a 2-stack version would be "
              "indistinguishable from a 1-stack one. healing_taken_pct is "
              "one of the eight stat_mods a MONSTER can actually read, and "
              "inside a status effect it is PERCENTAGE POINTS. Kept as a "
              "proc from the outgoing tree.")

T.node("bloodthirst", "Bloodthirst",
       "Teaches Bloodthirst, a strike that feeds on the wounds it opens.",
       4, 0, 1, node_type="active",
       effects={"unlock_ability": "warrior_bloodthirst"},
       connected_to=["death_wish"],
       source="WotLK row 4, kept - the ONLY unlock for "
              "warrior_bloodthirst, which is requires_talent. The real "
              "talent requires Death Wish, which connected_to reproduces.")

T.node("improved_whirlwind", "Improved Whirlwind",
       "Increases the damage of your Whirlwind by 10% per rank.",
       4, 2, 2, effects={"ability_warrior_whirlwind_damage": 0.10},
       connected_to=["flurry"],
       source="WotLK row 4: 'Increases the damage of your Whirlwind ability "
              "by 10%/20%.' Built verbatim; kept from the outgoing tree, "
              "corrected from 12% to the real 10% per rank.")

T.node("improved_berserker_stance", "Improved Berserker Stance",
       "While in Berserker Stance, increases your Strength by 4% per rank "
       "and reduces your threat by 2% per rank.",
       4, 4, 5,
       effects={"strength_pct": 4.0, "threat_generation_pct": -0.02},
       require_form="berserker",
       connected_to=["flurry"],
       source="WotLK row 4, NEW to our tree: 'Increases Strength by 4%-20% "
              "and reduces threat caused by 2%-10% while in Berserker "
              "Stance.' BUILT WITH THE REAL STANCE CONDITION, which makes "
              "this the first talent in the project to use require_form for "
              "a STANCE rather than a shapeshift. A talent's require_form "
              "is checked against both current_form and current_stance "
              "(abilities.py:812), and combat/stances.py defines "
              "battle/defensive/berserker, so 'while in Berserker Stance' "
              "is expressible exactly as written instead of being dropped "
              "or made unconditional. strength_pct is PERCENTAGE POINTS "
              "(read at character.py:1262 off `bonuses`, divided by 100) "
              "and threat_generation_pct is a FRACTION.")

# ----------------------------------------------------------------- tier 5
T.node("heroic_fury", "Heroic Fury",
       "Being struck resets the cooldown of your Intercept.",
       5, -3, 1,
       proc={"trigger": "on_damage_taken", "chance": 100, "icd": 5,
             "reset_cooldown": "warrior_intercept"},
       connected_to=["intensify_rage"],
       source="WotLK row 5, NEW to our tree: 'Removes any Immobilization "
              "effects and refreshes the cooldown of your Intercept "
              "ability.' The Intercept reset is real and built with "
              "reset_cooldown (status_effects.py:1207). Immobilisation does "
              "not exist to remove. DEPARTURE on the trigger - the real "
              "talent is an activated ability and we have none, so it fires "
              "reactively with icd 5 to keep it a cooldown rather than a "
              "permanent reset.")

T.node("rampage", "Rampage",
       "Increases your critical strike chance by 5%.",
       5, -1, 1, effects={"crit_chance_physical": 5.0},
       connected_to=["bloodthirst"],
       source="WotLK row 5: 'Increases ranged and melee critical hit chance "
              "of all party and raid members within 100 yds by 5%.' "
              "DEPARTURE - A TALENT EFFECT CAN NEVER REACH AN ALLY in this "
              "engine; only a party-targeted ABILITY can "
              "(abilities.py:2064). So the real 5% applies to the warrior "
              "alone. Kept from the outgoing tree, which was 4%. The real "
              "talent requires Bloodthirst, which connected_to "
              "reproduces.")

T.node("unending_fury", "Unending Fury",
       "Increases the damage of your Whirlwind and Bloodthirst by 2% per "
       "rank.",
       5, 1, 5,
       effects={"ability_warrior_whirlwind_damage": 0.02,
                "ability_warrior_bloodthirst_damage": 0.02},
       connected_to=["bloodthirst"],
       source="WotLK row 5, NEW to our tree: 'Increases the damage done by "
              "your Slam, Whirlwind and Bloodthirst abilities by 2%-10%.' "
              "Slam does not exist; the other two are built verbatim at the "
              "real 2% per rank.")

T.node("bloodsurge", "Bloodsurge",
       "Your Heroic Strike, Bloodthirst and Whirlwind have a 20% chance per "
       "rank to grant an extra attack.",
       5, 3, 3,
       proc={"trigger": "on_cast", "chance": 20, "icd": 0,
             "ability_filter": ["warrior_heroic_strike",
                                "warrior_bloodthirst",
                                "warrior_whirlwind"],
             "extra_attack": True},
       connected_to=["bloodthirst"],
       source="WotLK row 5: 'Your Heroic Strike, Bloodthirst, and Whirlwind "
              "hits have a 7%/13%/20% chance of making your next Slam "
              "instant for 5 sec.' DEPARTURE - there is no Slam ability and "
              "no cast-time system, so 'makes your next Slam instant' has "
              "nothing to act on. The real ability list is kept exactly and "
              "the payoff becomes an extra attack, which is the nearest "
              "thing to a free follow-up swing. extra_attack is a BOOLEAN. "
              "The real talent requires Bloodthirst, reproduced.")

# ----------------------------------------------------------------- tier 6
T.node("titans_grip", "Titan's Grip",
       "Increases your attack power by 8%.",
       6, 1, 1, effects={"attack_power_pct": 8.0},
       connected_to=["unending_fury"],
       source="WotLK row 10, the capstone: 'Allows you to equip two-handed "
              "axes, maces and swords in one hand. While you have a "
              "two-handed weapon equipped in one hand, your physical damage "
              "done is reduced by 10%.' DEPARTURE - there are no weapon "
              "slots or weapon classes to change, so the real talent's "
              "entire mechanism is absent. Its PURPOSE is a large damage "
              "gain bought with a penalty; delivered as flat attack power. "
              "Kept from the outgoing tree at the same value. "
              "attack_power_pct is PERCENTAGE POINTS.")


def main():
    return T.write(was="23 nodes, 65 points - 9 proc, 9 ability-scoped, "
                       "4 flat stat, 1 unlock")


if __name__ == "__main__":
    sys.exit(main())
