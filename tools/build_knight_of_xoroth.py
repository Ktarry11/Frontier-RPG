#!/usr/bin/env python3
"""Author the Knight of Xoroth: ability kit + three talent trees.

    PYTHONPATH=. python3 tools/build_knight_of_xoroth.py [--apply]

Knight of Xoroth is one of the twelve CoA classes that shipped with base
stats, plate armour, shield proficiency and a resource pair but no abilities
and no talents, so it was unselectable. This authors it end to end, on the
pattern tools/build_guardian.py set.

SOURCE. reference/coa_sidekick/CLASS_knight-of-xoroth.txt, the three
SPEC_knight-of-xoroth__*.txt pages, and the full talent dump in
reference/coa_sidekick/talents/knight-of-xoroth.json. Every ability and
talent name below is a real CoA name off those pages; nothing is invented to
fill a slot. Identity per that reference:

  Defiance  TANK       "Closest to Blood Death Knight, with a strong
                       secondary nod to Vengeance Demon Hunter." Builds
                       Deathfire off shield strikes and dumps it into a
                       self-heal, then layers block, critical block and
                       absorbs on top. Imps are mitigation: each one up
                       cuts a damage school.
  War       MELEE DPS  "Closest to a retail Fury/Blood-hybrid Death
                       Knight." Two-hand builder with bleeds and burns,
                       Deathfire payoffs, and Gore's lifesteal as its only
                       sustain. No damage-reduction cooldown of its own.
  Hellfire  MELEE DPS  "Closest to Vengeance Demon Hunter, re-tuned as a
                       pure damage spec rather than a tank." Melee/caster
                       hybrid: Strength feeds spell power, Deathfire feeds
                       Fire finishers, and there is no defensive at all.

NUMBERS ARE FRONTIER'S, NOT CoA'S. The reference gives identity, role and
rotation shape; it is a fan-made planning tool whose own disclaimer says COA
is pre-meta. Damage curves copy Warrior's shipped shape (heroic_strike: 9
ranks at levels 1/6/12/18/24/32/40/48/56, flat resource cost, linear growth)
because Warrior is the other Rage plate class and the two should scale
alongside each other.

RESOURCES. CLASS_RESOURCE_MAP gives (RAGE, DEATHFIRE). Rage is the primary
100-point pool with no passive regen, so costs are flat across ranks and sit
in Warrior's own authored band (5 to 30: heroic_strike 20, mortal_strike 30,
overpower 5). Deathfire is the secondary pool and the class-defining
mechanic, CoA's Demonfire: builders generate it, finishers spend it.
Character.SECONDARY_RESOURCE_MAX caps it at 100 with no override, so one
CoA Demonfire stack is modelled as 10 Deathfire - builders grant 10 or 20,
finishers cost 30 to 50, which is the 3-to-5-stack spend CoA's rotations
describe. A cost over 100 would make an ability uncastable forever.

Talent effect keys are restricted to ones the engine actually reads -
verified with tools/validate_class.py, which delegates liveness to
tools/audit_talents.py. Two casualties worth recording:

  CoA's Ragefist ("Increases your maximum Rage by 10") and Heart of Xoroth
  ("Demon's Blood stacks 5 additional times") both want a bigger resource
  pool. Character.get_resource_max only honours <resource>_max for
  SECONDARY resources, so rage_max is dead by construction, and while
  deathfire_max would be read, nothing in the engine names it as a literal
  so validate_class.py correctly reports it dead. Neither node is in these
  trees.

  CoA's Demon's Blood - a stacking buff every melee hit grants, which half
  the class tree scales off - has no engine hook: a talent cannot define a
  new stacking resource. Where a node's real text reads off Demon's Blood
  stacks, it carries the payoff those stacks were buying instead, and says
  so in its _source.

CONVENTIONS THIS SCRIPT FIXES RELATIVE TO build_guardian.py. Guardian is the
reference implementation and its structure is copied closely, but five of
its data conventions are wrong against the engine and are NOT copied here.
See the report at the bottom of this docstring:

  1. A buff/debuff ability's stat_mods are scaled by effect_value/100
     (Ability._apply_effect). Guardian ships effect_value 0 on all 16 of its
     buffs, which multiplies every stat_mod by zero. Every shipped buff in
     every other class uses 100. Buffs here use 100.
  2. AoE is driven by target_type="enemy_aoe" (+ max_targets), not by
     "is_aoe": _ability_from_data never reads is_aoe at all. Guardian's six
     AoE abilities are authored target_type="enemy" + is_aoe, so they are
     single-target, and its One Man Army aoe_damage talent is dead.
  3. buff_scope is only ("raid", "combat") and controls DURATION, not who
     the buff lands on. Who it lands on is target_type="party". Guardian's
     nine party buffs are self-only 30-minute raid buffs.
  4. restore_resource reads mana_restore_pct off the RANK dict, not
     effect_value, so Guardian's Knight's Calling restores 0.
  5. all_ability_cost_pct is applied as cost * (1 - pct), so POSITIVE is the
     discount. Guardian's Seasoned Fighter is authored -0.03, which makes
     every ability 15% more expensive at 5 points.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Warrior's shipped rank schedule - see module docstring.
RANK_LEVELS = [1, 6, 12, 18, 24, 32, 40, 48, 56]

PREFIX = "knight_of_xoroth"


def ranks(base, step, cost, start=1, count=9, restore_pct=None):
    """Flat-cost rank table on the Warrior schedule, starting at `start`.

    Levels past the 9-rank schedule are spaced evenly to stay under 58 so
    every rank is actually reachable at the level 60 cap.

    restore_pct, when given, is the per-rank "% of the pool restored" that
    effect_type="restore_resource" actually reads (Ability.mana_restore_pct
    comes off the RANK dict, not off effect_value).
    """
    if start == 1:
        levels = RANK_LEVELS[:count]
    else:
        span = max(1, (58 - start) // max(1, count - 1)) if count > 1 else 1
        levels = [min(58, start + i * span) for i in range(count)]
    out = []
    for i, lv in enumerate(levels):
        rank = {"rank": i + 1, "level_req": lv, "cost": cost,
                "effect_value": int(round(base + step * i))}
        if restore_pct is not None:
            rank["mana_restore_pct"] = int(round(restore_pct[0] + restore_pct[1] * i))
        out.append(rank)
    return out


def one(level, cost, value=100):
    """Single-rank table, for cooldowns and stances that do not scale.

    The default effect_value is 100, not 0. A buff or debuff multiplies its
    whole stat_mods dict by effect_value/100, so 0 silently zeroes the
    buff - see convention note 1 in the module docstring.
    """
    return [{"rank": 1, "level_req": level, "cost": cost, "effect_value": value}]


def ability(aid, name, effect_type, description, rank_table, *, cooldown=0,
            duration=0, stat_mods=None, icon="ability_melee", source=None,
            resource="rage", **extra):
    out = {
        "ability_id": f"{PREFIX}_{aid}",
        "name": name,
        "resource_type": resource,
        "cooldown": cooldown,
        "effect_type": effect_type,
        "duration": duration,
        "stat_mods": stat_mods or {},
        "description": description,
        "ranks": rank_table,
        "icon_id": icon,
    }
    if source:
        out["_source"] = source
    out.update(extra)
    return out


def deathfire(amount):
    """`generates` payload for a Deathfire builder. 10 Deathfire = one CoA
    Demonfire stack (see RESOURCES in the module docstring)."""
    return {"resource": "deathfire", "amount": amount}


# ============================================================== ability kit
# Order is roughly the order a player meets them: shared class kit first,
# then the three specs. CoA puts most of these in one shared class tree plus
# a tree per spec; Frontier has no shared tree, so the class-tree abilities
# are simply part of the kit and the spec-tree ones are gated by
# requires_talent + an unlock_ability node.
ABILITIES = [
    ability("attack", "Attack", "damage",
            "A measured strike with your weapon.", one(1, 0, 0),
            source="Convention: every class ships a free rank-1 Attack."),

    # ---- shared class kit
    ability("infernal_strike", "Infernal Strike", "damage",
            "Drive your weapon in and let the hellfire in it bite. The "
            "burn feeds the fire you carry.",
            ranks(42, 11, 20), target_type="enemy",
            generates=deathfire(20),
            source="CoA: 'weave a cheap filler strike in Infernal Strike, "
                   "which generates 2 Demonfire'. The universal filler, on "
                   "Warrior's heroic_strike curve."),
    ability("sever", "Sever", "damage",
            "A short, economical cut. You take what the swing gives you.",
            ranks(32, 9, 10, start=6, count=8), target_type="enemy",
            generates=deathfire(10),
            source="CoA: 'using Sever to top up rage'. Cheapest strike in "
                   "the kit, so it is the one you press when the pool is "
                   "empty."),
    ability("meatsaw", "Meatsaw", "damage",
            "A grinding, two-handed sweep that catches whoever is pressed "
            "in beside your target.",
            ranks(34, 10, 25, start=10, count=7),
            target_type="enemy_aoe", max_targets=3,
            source="CoA: 'Meatsaw (hits nearby enemies)'. target_type "
                   "enemy_aoe + max_targets is what the engine actually "
                   "reads for a limited cleave; the is_aoe flag is never "
                   "read at load time."),
    ability("skulltaker", "Skulltaker", "damage",
            "Spend the fire banked in you on one downward blow. The more "
            "you have stored, the less of them is left.",
            ranks(76, 22, 40, start=12, count=7), cooldown=1,
            target_type="enemy", resource="deathfire",
            source="CoA: 'dump stacked Demonfire into Skulltaker for its "
                   "scaling finisher: more damage per stack'. The class's "
                   "single-target Deathfire spender, shared by all three "
                   "specs. 40 Deathfire is CoA's 4-stack spend."),
    ability("suffuse", "Suffuse", "heal",
            "Let the mortal half of you surface for a moment. What it "
            "closes stays closed.",
            ranks(60, 26, 50, start=12, count=7), cooldown=2,
            target_type="self", icon=None, resource="deathfire",
            source="CoA: 'You spend Demonfire on Suffuse, an instant "
                   "self-heal that scales off Stamina and defensive stats, "
                   "so you top yourself off constantly as a side effect of "
                   "pressing your rotation.' Frontier heals scale off "
                   "healing_power, not Stamina or defense rating, so the "
                   "Stamina scaling is lost; the Deathfire-funded "
                   "self-sustain loop, which is the actual identity, is "
                   "intact. VALUE RESOLVED 2026-10-29: this script and the "
                   "shipped JSON disagreed - data had cost 30 / effect_value "
                   "150-570, this script had cost 50 / 60-216 - which means "
                   "one side was edited and the other never re-run. Kept "
                   "THESE values because they sit in the peer band for a "
                   "single-target self-heal (Paladin Holy Light 52-162, "
                   "Priest Heal 54-166, Shaman Healing Wave 56-171) while "
                   "the data's 150 at rank 1 was roughly 3x that AND "
                   "cheaper. A one-line revert if the 30/150 table was "
                   "deliberate."),
    ability("melt", "Melt", "spell_dot",
            "The wound will not close while it is still burning.",
            ranks(48, 14, 20, start=14, count=6), cooldown=3, duration=3,
            target_type="enemy", damage_school="fire", icon=None,
            source="CoA names Melt beside Infernal Strike and Meatsaw in "
                   "'A Gift from Hell' (the Rage-cost cut) and in "
                   "'Infernal Pummeling', which makes it the target's "
                   "damage amp. The burn half is what the engine can "
                   "express, so it is a Fire DoT."),
    ability("flames_of_xoroth", "Flames of Xoroth", "damage",
            "Hellfire comes off your weapon in a sheet and takes everything "
            "in front of you with it.",
            ranks(42, 13, 30, start=16, count=6), cooldown=3,
            target_type="enemy_aoe", max_targets=4, damage_school="fire",
            source="CoA: 'Your AoE comes from Flames of Xoroth'. Present in "
                   "all three specs (War transforms it into Warbringer, "
                   "Defiance into Hellfire Bellows)."),
    ability("flesh_hook", "Flesh Hook", "ranged_damage",
            "The hook goes out, bites, and brings them back to you.",
            ranks(38, 11, 15, start=8, count=6), cooldown=4,
            target_type="enemy",
            source="CoA: 'Flesh Hook (pulls the enemy to you)', 'Flesh Hook "
                   "is your only reach tool'. ranged_damage - it is thrown. "
                   "The engine has no forced-reposition mechanic, so the "
                   "pull itself is flavour."),
    ability("chainwhip", "Chainwhip", "damage",
            "The chain comes round low and hard, and whatever they were "
            "saying stops.",
            ranks(44, 13, 15, start=10, count=6), cooldown=3,
            target_type="enemy",
            source="CoA: 'Swing a chain at an enemy dealing Physical damage "
                   "and silencing them for 2 seconds, generating a large "
                   "amount of threat.' The engine has no silence category "
                   "(see StatusEffect.is_stun, the only incapacitate), so "
                   "the damage and its threat are what lands."),
    ability("chains_of_malice", "Chains of Malice", "damage",
            "Chains out of nothing, wrapped tight. They are not going "
            "anywhere and they are not doing anything.",
            ranks(46, 14, 20, start=18, count=5), cooldown=6,
            target_type="enemy", is_stun=True,
            source="CoA: 'Lock an enemy down with magical chains, stunning "
                   "them and dragging them with you for 5 seconds.' The "
                   "stun is real; the drag is not modellable."),
    ability("dread", "Dread", "buff",
            "You stop being a thing they can ignore.",
            one(14, 10), cooldown=6, duration=2,
            stat_mods={"threat_generation_pct": 180}, target_type="self",
            icon=None,
            source="The class tree's Dread, which is the one node whose "
                   "tooltip the scrape could not capture ('(see builder "
                   "tooltip)'), so the MECHANIC here is Frontier's choice "
                   "rather than CoA's: the kit otherwise has no taunt, and "
                   "Defiance is a main tank. Implemented as a "
                   "threat_generation_pct buff, the convention Guardian's "
                   "Challenging Cry (200) and Cultist's Twilight Domain "
                   "(180) already use - ability buff stat_mods are percent "
                   "POINTS here, unlike talent effects, which are "
                   "fractions."),
    ability("black_shield", "Black Shield", "buff",
            "Something between you and the next blow. It does not have to "
            "be yours.",
            one(20, 25), cooldown=8, duration=3, target_type="self",
            absorb_pct_max_health=0.18, buff_scope="combat", icon=None,
            source="CoA: 'Consume all of your Demon's Blood stacks to "
                   "create a demonic shield that absorbs 860 damage, "
                   "increased by 20% per Demon's Blood stack'. Demon's "
                   "Blood has no engine hook, so the absorb is a flat "
                   "share of max health instead of a stack-scaled number."),
    ability("demon_heart", "Demon Heart", "restore_resource",
            "Reach inward for the part of you that was put there, and let "
            "it answer.",
            ranks(0, 0, 0, start=22, count=4, restore_pct=(40, 5)),
            cooldown=10, target_type="self", restore_resource_type="rage",
            generates=deathfire(20), icon=None,
            source="CoA: 'Embrace your inner demon, instantly generating 6 "
                   "stacks of Demonfire and 50 Rage.' Both halves are "
                   "real: restore_resource refills Rage (off the rank's "
                   "mana_restore_pct, which is where the engine reads the "
                   "amount) and `generates` pays the Deathfire."),
    ability("burning_rage", "Burning Rage", "buff",
            "Past a certain point nothing anyone does to you registers as "
            "a reason to stop.",
            one(26, 0), cooldown=12, duration=2,
            stat_mods={"cc_immune": 1, "haste": 10.0}, target_type="self",
            buff_scope="combat", icon=None,
            source="CoA: 'Enrage, generating 15 Rage every 1 sec and making "
                   "you immune to incapacitate, banish, and polymorph "
                   "effects for 6 seconds. Usable while incapacitated.' "
                   "cc_immune is a real stat_mod the engine checks before "
                   "applying an incapacitate. The Rage-per-second half "
                   "belongs to Demon Heart instead - one ability cannot "
                   "both buff and restore."),
    ability("juggernaut", "Juggernaut", "buff",
            "You stop giving ground, and stop noticing the reasons to.",
            one(30, 25), cooldown=12, duration=3,
            stat_mods={"damage_taken_pct": -0.25}, target_type="self",
            buff_scope="combat", icon=None,
            source="CoA: 'Consume all of your Demon's Blood to become a "
                   "juggernaut, reducing all damage taken by 30% for 10 "
                   "seconds.' The tick-healing half and the Demon's Blood "
                   "cost are not modellable; -25% for 3 turns on a 12-turn "
                   "cooldown sits just under Warrior's Shield Wall (-40%, "
                   "2 turns) deliberately, since every spec gets this one."),
    ability("unleash_pestilence", "Unleash Pestilence", "damage",
            "Whatever you have been radiating, let it all go at once.",
            ranks(54, 16, 30, start=28, count=5), cooldown=6,
            target_type="enemy_aoe", max_targets=5,
            source="CoA: 'Unleashes your active Pestilence to trigger a "
                   "powerful effect.' Which Pestilence is up changes what "
                   "it does in CoA; the engine has no such branch, so it is "
                   "one AoE burst regardless."),
    ability("pestilence_of_death", "Pestilence of Death", "buff",
            "You carry an air about you that the dying recognise.",
            one(24, 20), duration=0,
            stat_mods={"crit_chance_physical": 8.0, "crit_chance_spell": 8.0},
            target_type="self", exclusive_group="knight_of_xoroth_pestilence",
            icon=None,
            source="CoA: 'Emanate a pestilence, increasing your critical "
                   "damage by 10%.' No buff-sourced crit-DAMAGE key exists "
                   "(crit_damage_physical is read off talents only), so it "
                   "grants crit CHANCE instead. One Pestilence at a time, "
                   "so the two share an exclusive_group."),
    ability("pestilence_of_apocalypse", "Pestilence of Apocalypse", "buff",
            "The air around you turns thin and hot, and everything in it "
            "burns easier.",
            one(34, 20), duration=0,
            stat_mods={"damage_dealt_pct": 8}, target_type="self",
            exclusive_group="knight_of_xoroth_pestilence", icon=None,
            source="CoA: 'causing targets within 8 yds to take 10% "
                   "increased Fire damage from you'. The engine has no "
                   "per-enemy aura; damage_dealt_pct on the Knight is the "
                   "same arithmetic from the other side."),

    # ---- Defiance
    ability("shieldgore", "Shieldgore", "damage",
            "Put the spikes of your shield through them. It is the loudest "
            "thing you can do.",
            ranks(46, 13, 20, start=10, count=7), target_type="enemy",
            damage_school="fire", generates=deathfire(20),
            requires_talent=True,
            source="CoA: 'Transforms your Infernal Strike into Shieldgore. "
                   "Generates 2 Demonfire. Gore the target with your spiked "
                   "shield, causing High Threat Fire Damage, scaling with "
                   "your block value.' Block-value scaling has no hook on "
                   "the damage path, so the damage is flat; the Deathfire "
                   "generation and the threat from a big hit are what the "
                   "spec's whole loop actually runs on."),
    ability("call_hellfire_imp", "Call: Hellfire Imp", "summon_pet",
            "One of them is always listening. It comes when called and it "
            "soaks what it is pointed at.",
            one(12, 0, 0), cooldown=6, target_type="self",
            summon_pet_template="hellfire_imp", generates={"resource": "rage",
                                                           "amount": 20},
            icon=None,
            source="CoA: 'Beckon 1 Hellfire Imp to aid you in battle for 12 "
                   "seconds and generate 20 Rage. Threat generated by "
                   "Hellfire Imps is transferred to you.' CoA calls it 'a "
                   "free rage battery that also summons a body', so the "
                   "Rage is the generates payload. NOW ITS OWN TEMPLATE: "
                   "this reused the Warlock's 'imp' and summoned a pet "
                   "named Imp, which was the most defensible of the "
                   "mismatches fixed in Oct 2026 - an imp summoning an Imp. "
                   "It was split out anyway because CoA names the creature "
                   "(Call: Hellfire Abyssal's own tooltip reads 'Costs 15 "
                   "less Rage for each active Hellfire Imp') and because "
                   "this class's Summon: Greater Imp now has a real template "
                   "of its own, so leaving this one on the Warlock's roster "
                   "would have given one class an 'Imp' and a 'Greater Imp' "
                   "from two different places with the Warlock's fire "
                   "numbers underneath. 'hellfire_imp' is deliberately much "
                   "weaker than the Warlock Imp it replaced - Knight of "
                   "Xoroth's called demons are a side channel, not its "
                   "damage identity."),
    ability("call_hellfire_abyssal", "Call: Hellfire Abyssal", "summon_pet",
            "Something much larger lands where you pointed, and stays.",
            one(40, 35, 0), cooldown=15, target_type="self",
            summon_pet_template="hellfire_abyssal", requires_talent=True,
            icon=None,
            source="CoA: 'Call down a Hellfire Abyssal from the sky to crash "
                   "down upon the targeted 8 yd area, dealing AP Fire "
                   "damage. The abyssal remains to aid you in battle for 15 "
                   "seconds and emits an aura that reduces the damage taken "
                   "by party and raid members within 40 yds by 5%.' NOW A "
                   "REAL ABYSSAL: this used to borrow voidwalker and "
                   "summoned a pet named Voidwalker, picked as the tankiest "
                   "demon then in pet_templates.py. The template now exists "
                   "- the slowest and most armoured of this class's three "
                   "called demons, with a real Fire signature. The party "
                   "aura is still carried by the capstone NODE that unlocks "
                   "this, which remains the only place the engine can "
                   "express it: a pet-cast party buff resolves onto the pet "
                   "alone, which the template's _source spells out."),
    ability("implosion", "Implosion", "damage",
            "Let the stored fire out all at once, in every direction, and "
            "take the recoil as fuel.",
            ranks(60, 18, 40, start=24, count=5), cooldown=4,
            target_type="enemy_aoe", max_targets=5, damage_school="fire",
            resource="deathfire", generates={"resource": "rage", "amount": 30},
            source="CoA: 'Explode with hellish fire, dealing Fire damage to "
                   "nearby enemies, beckoning Hellfire Imps to aid you in "
                   "battle, and generating 30 Rage. Deals increased damage "
                   "... for each Demonfire consumed.' Spends Deathfire and "
                   "pays Rage, which is the one place the class's two pools "
                   "trade in that direction. The imp summon cannot ride "
                   "along on a damage ability."),
    ability("sacrificial_circle", "Sacrificial Circle", "heal",
            "You made them. You can spend them.",
            ranks(260, 90, 20, start=28, count=4), cooldown=8,
            target_type="self", icon=None,
            source="CoA: 'Sacrifice your Hellfire Imps within 15 yds, "
                   "healing you 15% of your maximum health, plus an "
                   "additional amount equal to 25% of each of your Hellfire "
                   "Imp's maximum health.' The engine cannot consume your "
                   "own pets as a cost, so it is a flat emergency heal on a "
                   "long cooldown. The Soul Furnace absorb that CoA leaves "
                   "behind is the Defiance node of that name."),
    ability("curse_of_xoroth", "Curse of Xoroth", "spell_dot",
            "A word spoken over them that keeps working after you have "
            "stopped paying attention.",
            ranks(70, 20, 25, start=30, count=4), cooldown=4, duration=3,
            target_type="enemy", damage_school=["fire", "shadow"], icon=None,
            source="CoA: 'Curse an enemy for 15 seconds, dealing Shadowflame "
                   "Damage over 15 seconds. Your next Shieldgore within 12 "
                   "seconds grants you Black Shield.' There is no "
                   "shadowflame school; the engine supports a COMBINED "
                   "school list (Sun Cleric's Radiant Flame is "
                   "['holy', 'fire']), so Fire plus Shadow is literal. The "
                   "Black Shield priming is not modellable."),
    ability("chains_of_xoroth", "Chains of Xoroth", "debuff",
            "Chains across the ground. Crossing it costs more than they "
            "have.",
            one(26, 20), cooldown=6, duration=2,
            stat_mods={"haste": -20.0}, target_type="enemy_aoe", icon=None,
            source="CoA: 'Create demonic chains at target location that slow "
                   "enemies inside by -80% for 5 seconds. At the end of the "
                   "duration, it pulls all affected enemies to it.' The "
                   "slow is real; the terminal pull is not. Same "
                   "haste-negative snare shape Guardian's Net Throw uses."),
    ability("hellfire_bellows", "Hellfire Bellows", "damage",
            "You breathe out and the fire goes both ways.",
            ranks(50, 15, 25, start=32, count=5), cooldown=3,
            target_type="enemy_aoe", max_targets=4, damage_school="fire",
            source="CoA: 'Transforms your Flames of Xoroth into Hellfire "
                   "Bellows. Bellow fire on all enemies in a 6 yd cone in "
                   "front of and behind you.' Frontier has no facing, so "
                   "the cone is a capped cleave."),
    ability("legions_presence", "Legion's Presence", "buff",
            "For a while the people fighting beside you are fighting for "
            "something older than you.",
            one(44, 30), cooldown=12, duration=3,
            stat_mods={"damage_dealt_pct": 10}, target_type="party",
            buff_scope="combat", icon=None,
            source="CoA: 'Emanate an aura to allies within 25 yds for 15 "
                   "seconds, increasing their damage dealt by 10%.' "
                   "target_type party is what makes a buff land on allies; "
                   "buff_scope only chooses between a 30-minute raid buff "
                   "and a turn-based combat one."),

    # ---- War
    ability("gore", "Gore", "damage",
            "Quick, low, and already pulling back out.",
            ranks(40, 12, 15, start=10, count=7), cooldown=2,
            target_type="enemy", generates=deathfire(10),
            requires_talent=True,
            source="CoA: '2 Charges, 8 sec recharge. Generates 1 Demonfire. "
                   "Quickly gore an enemy.' Charges have no engine "
                   "equivalent, so it is a 2-turn cooldown. CoA gates Gore "
                   "behind two maxed War talents, so it is talent-unlocked "
                   "here too."),
    ability("warbringer", "Warbringer", "damage",
            "Bring the weapon down on the ground instead of on them. It "
            "reaches further that way.",
            ranks(52, 16, 25, start=22, count=5), cooldown=4,
            target_type="enemy_aoe", max_targets=4,
            source="CoA: 'Transforms your Flames of Xoroth into Warbringer. "
                   "Slam the ground, dealing Weapon Damage to nearby "
                   "enemies, reducing the effectiveness of any healing by "
                   "-50% for 10 seconds.' A damage ability cannot also "
                   "apply a debuff, so the anti-heal is lost here; "
                   "healing_taken_pct exists but only on a debuff ability, "
                   "and War's own page calls the cleave the point."),
    ability("brimstone_bludgeon", "Brimstone Bludgeon", "damage",
            "One swing for everything standing close enough to regret it.",
            ranks(96, 28, 30, start=40, count=4), cooldown=5,
            target_type="enemy_aoe", max_targets=4, requires_talent=True,
            source="CoA: 'Walking in and popping Brimstone Bludgeon is the "
                   "opener: heavy weapon damage to the pack that also "
                   "unleashes Pestilence of Death'. The spec's keystone and "
                   "its tier-6 pick, so it is unlocked by the capstone "
                   "node. The Pestilence unleash is a separate button here."),
    ability("decimation", "Decimation", "buff",
            "You already know where this one lands.",
            one(36, 20), cooldown=8, duration=2,
            stat_mods={"crit_chance_physical": 40.0}, target_type="self",
            buff_scope="combat", icon=None,
            source="CoA: 'Your next Skulltaker or Warbringer is guaranteed "
                   "to critically strike for 25% increased damage.' Nothing "
                   "can guarantee a crit or restrict a buff to the next "
                   "cast of two named abilities, so it is a large crit "
                   "window instead - the same shape as Warrior's "
                   "Recklessness (crit_chance_physical 100)."),
    ability("burning_blade", "Burning Blade", "buff",
            "The blade catches and stays caught.",
            one(30, 20), cooldown=10, duration=3,
            stat_mods={"armor_penetration_pct": 30, "attack_power": 40},
            target_type="self", buff_scope="combat", icon=None,
            source="CoA: 'Ignite your weapon, causing you to send out "
                   "searing fire with each melee critical strike, dealing "
                   "Fire damage in a line and increasing your Armor "
                   "penetration by 30% while active.' The armour "
                   "penetration is literal; the on-crit fire line is the "
                   "War tree's Hellsmelted node."),
    ability("searing_blade", "Searing Blade", "damage",
            "A strike that arrives already hot.",
            ranks(60, 18, 20, start=26, count=5), cooldown=3,
            target_type="enemy", damage_school="fire",
            source="CoA names Searing Blade in War's Domination ('Melee "
                   "critical strikes now reduce the cooldown of Searing "
                   "Blade'), which is all the reference says about it, so "
                   "it is authored as the spec's mid-cooldown Fire strike."),

    # ---- Hellfire
    ability("seeking_flame", "Seeking Flame", "spell_damage",
            "The fire goes and finds them. It is slower to leave than to "
            "arrive.",
            ranks(40, 12, 15, start=12, count=7), cooldown=1,
            target_type="enemy", damage_school="fire",
            generates=deathfire(10), icon=None,
            source="CoA: 'Generates 1 Demonfire. Sear an enemy, dealing "
                   "Fire damage', and 'Seeking Flame's slow keeps targets "
                   "in reach'. The engine has no slow on a damage ability, "
                   "so the slow is lost and the Deathfire generation is "
                   "the mechanical half."),
    ability("hellmaw", "Hellmaw", "spell_dot",
            "You open something in them that keeps chewing.",
            ranks(90, 26, 40, start=16, count=6), cooldown=3, duration=3,
            target_type="enemy", damage_school=["fire", "shadow"],
            resource="deathfire", requires_talent=True, icon=None,
            source="CoA: 'Burn an enemy with a fiery strike, dealing "
                   "Shadowflame Damage, plus an additional amount over 12 "
                   "seconds. Deals 20% increased damage per Demonfire "
                   "consumed.' Hellmaw is a Hellfire tree pick in CoA, so "
                   "it is talent-unlocked. Shadowflame is the combined "
                   "['fire', 'shadow'] school."),
    ability("hellfire_form", "Hellfire Form", "buff",
            "You stop pretending the thing inside you is a passenger.",
            one(40, 40), cooldown=12, duration=3,
            stat_mods={"damage_dealt_pct": 20, "crit_chance_spell": 15.0},
            target_type="self", buff_scope="combat", resource="deathfire",
            icon=None,
            source="CoA: 'Enter your Hellfire Form, increasing your Fire "
                   "damage dealt by 20% and Fire critical strike chance by "
                   "15% for 15 seconds', 'the Metamorphosis-style "
                   "transformation cooldown'. Not effect_type shapeshift: "
                   "combat/forms.py is a shared file and has no Hellfire "
                   "Form, so it is a buff. damage_dealt_pct is "
                   "school-agnostic in this engine, so the Fire "
                   "restriction is lost."),
    ability("hellstorm", "Hellstorm", "spell_damage",
            "The sky over them stops behaving and starts falling.",
            ranks(80, 24, 50, start=38, count=4), cooldown=6,
            target_type="enemy_aoe", max_targets=6, damage_school="fire",
            resource="deathfire", icon=None,
            source="CoA: 'Create a hellstorm, dealing Fire damage to up to "
                   "8 nearby enemies. Embers then flare every 1 sec ... "
                   "Duration is increased by 100% for each stack of "
                   "Demonfire consumed.' The ember ticks would need a "
                   "damage ability that also lays a DoT, which the engine "
                   "does not have, so it is one large capped AoE hit."),
    ability("summon_greater_imp", "Summon: Greater Imp", "summon_pet",
            "A bigger one, and a worse temper.",
            one(18, 25, 0), cooldown=10, target_type="self",
            summon_pet_template="greater_imp", icon=None,
            source="CoA: 'Teaches you Summon: Greater Imp ... Greater Imp "
                   "has various combat abilities that provide excellent "
                   "single target damage and control.' NOW A REAL GREATER "
                   "IMP: this used to borrow felhunter and summoned a pet "
                   "named Felhunter, picked as the demon with a real "
                   "single-target kit. The template now exists, tuned up "
                   "against this class's own Hellfire Imp rather than down "
                   "from the Warlock's Felhunter, since 'excellent single "
                   "target damage' is the brief. The 'control' half is not "
                   "authored - every control shape here is a debuff or the "
                   "is_stun flag, and a pet never casts a debuff. CoA makes "
                   "this a free level-10 passive of the Hellfire tree; "
                   "Frontier has no free passives, so it is an ordinary "
                   "summon the whole class can train."),
]


# ============================================================ talent helpers

def node(tree, tid, name, description, tier, slot, max_points, effects,
         *, node_type="passive", connect=None, proc=None, source=None,
         total_slots=4):
    """One talent node. `slot` is 0-based across the tier's row.

    Hex layout copies the shipped trees: hex_y = -6 + 2*tier, hex_x odd and
    spaced by 2, centred on the row, so tiers narrow toward the capstone.
    """
    span = (total_slots - 1) * 2
    out = {
        "talent_id": f"{tree}_{tid}",
        "name": name,
        "description": description,
        "node_type": node_type,
        "tier": tier,
        "max_points": max_points,
        "cost_per_point": 1,
        "hex_x": -span // 2 + slot * 2,
        "hex_y": -6 + 2 * tier,
        "effects": effects,
        "connected_to": [f"{tree}_{c}" for c in (connect or [])],
    }
    if proc:
        out["proc"] = proc
    if source:
        out["_source"] = source
    return out


TIER_REQUIREMENTS = {"0": 0, "1": 5, "2": 10, "3": 15, "4": 20, "5": 25, "6": 30}


def tree(tree_id, spec_name, description, nodes, source):
    return {
        "spec_name": spec_name,
        "tree_id": tree_id,
        "description": description,
        "_source_note": source,
        "tier_requirements": TIER_REQUIREMENTS,
        "nodes": nodes,
    }


def A(aid):
    """Full ability_id, for the ability_<id>_<stat> talent keys."""
    return f"{PREFIX}_{aid}"


# =============================================================== Defiance
D = "knight_of_xoroth_defiance"
DEFIANCE = tree(
    D, "Knight of Xoroth Defiance",
    "Plate shield tank. Shieldgore banks Deathfire, Suffuse spends it to "
    "heal you, and block, critical block and absorbs stack on top. Every "
    "imp you have out is mitigation.",
    [
        node(D, "hellsmelted_armor", "Hellsmelted Armor",
             "Increases your chance to block by 2% per rank.",
             0, 0, 5, {"block": 2.0},
             source="CoA: 'Each Hellfire Imp active now increases your "
                    "chance to block by 1%.' Per-imp scaling has no hook, "
                    "so it is flat block chance. Note block is TWO stats "
                    "here: `block` is the shield-gated CHANCE, block value "
                    "is the flat amount absorbed (block_value_pct)."),
        node(D, "demonfire_plating", "Demonfire Plating",
             "Reduces all damage you take by 1% and increases your Stamina "
             "by 2% per rank.",
             0, 1, 5, {"damage_taken_pct": -0.01, "stamina_pct": 2.0},
             source="CoA class tree: 'Reduces your damage taken by -2% and "
                    "increases your Stamina by 3%.' NOTE the two keys use "
                    "opposite conventions - damage_taken_pct is a FRACTION "
                    "(-0.01 = -1%) and stamina_pct is percentage POINTS "
                    "(2.0 = +2%)."),
        node(D, "a_gift_from_hell", "A Gift from Hell",
             "Reduces the Rage cost of your abilities by 3% per rank.",
             0, 2, 5, {"all_ability_cost_pct": 0.03},
             source="CoA: 'Reduces the Rage cost of Infernal Strike, "
                    "Meatsaw, and Melt by -10.' Ability.talented_cost does "
                    "cost * (1 - pct), so a POSITIVE value is the discount; "
                    "authored negative it becomes a surcharge."),
        node(D, "hellfire_forgemaster", "Hellfire Forgemaster",
             "Increases the damage your blocks absorb by 4% per rank.",
             0, 3, 5, {"block_value_pct": 0.04},
             source="CoA: 'Increases your block value by 20%.' Block VALUE, "
                    "the other half of the two-stat block system - a "
                    "fraction, not percentage points."),

        node(D, "shieldgore", "Shieldgore",
             "Teaches Shieldgore, a high-threat shield strike that burns "
             "and banks 20 Deathfire.",
             1, 0, 1, {"unlock_ability": A("shieldgore")},
             node_type="active", connect=["hellsmelted_armor"],
             source="CoA: 'Transforms your Infernal Strike into "
                    "Shieldgore'. A free spec pick in CoA and the button "
                    "the entire rotation is built on, so it is the first "
                    "real node in the tree."),
        node(D, "imp_guards", "Imp Guards",
             "Reduces the physical damage you take by 1% per rank.",
             1, 1, 3, {"physical_damage_taken_pct": -0.01},
             connect=["demonfire_plating"],
             source="CoA: 'Each Hellfire Imp now reduces your Physical "
                    "damage taken by 1%.' Flat, since nothing can read a "
                    "live pet count. CoA gives this free at level 20."),
        node(D, "imp_aura", "Imp Aura",
             "Reduces the magic damage you take by 1% per rank.",
             1, 2, 3, {"magic_damage_taken_pct": -0.01},
             connect=["a_gift_from_hell"],
             source="CoA: 'Each Hellfire Imp now reduces your Magic damage "
                    "taken by 1%.' The magic half of Imp Guards, and the "
                    "reason CoA says this tank 'covers magic as well as "
                    "melee'."),
        node(D, "xorothian_finesse", "Xorothian Finesse",
             "Increases your chance to parry by 1% per rank.",
             1, 3, 5, {"parry": 1.0}, connect=["hellfire_forgemaster"],
             source="CoA class tree: 'Increases your chance to parry by "
                    "5%.' Parry is full avoidance, unlike block, and CoA's "
                    "stat priority puts Dodge and Parry above Block."),

        node(D, "hellfire_resolve", "Hellfire Resolve",
             "Grants block value equal to 3% of your Strength, and 1 hit "
             "rating, per rank.",
             2, 0, 5, {"block_value_from_strength_pct": 0.03, "hit_rating": 1},
             connect=["shieldgore"],
             source="CoA: 'Increases your block rating by 15% of your "
                    "Strength and increases your hit rating by 5% of your "
                    "Strength.' The block half is a real "
                    "<target>_from_<source>_pct conversion resolved against "
                    "character.py's shared STAT_CONVERSION maps. The hit "
                    "half cannot be: hit_rating is a local feeding "
                    "base_miss_chance_*, not a Character attribute, so it "
                    "is flat hit instead - the same wall Guardian's Bulwark "
                    "hit."),
        node(D, "demonfire_retaliation", "Demonfire Retaliation",
             "Taking a hit has a 10% chance per rank to bank 8 Deathfire.",
             2, 1, 3, {}, connect=["imp_guards"],
             proc={"trigger": "on_damage_taken", "chance": 10, "icd": 0,
                   "grant_resource": {"resource": "deathfire", "amount": 8}},
             source="CoA: 'Grants you a 30% chance to generate a stack of "
                    "Demonfire when attacked.' Literal: a real "
                    "grant_resource proc into the secondary pool. Proc "
                    "chance is scaled by points_spent on a multi-rank node "
                    "(Character._sync_talent_procs), so 10 here is 30% at "
                    "3 points."),
        node(D, "forgefiends_bulwark", "Forgefiend's Bulwark",
             "Taking a hit has a 10% chance per rank to enrage you, "
             "increasing your damage by 10% for 3 turns.",
             2, 2, 3, {}, connect=["imp_aura"],
             proc={"trigger": "on_damage_taken", "chance": 10, "icd": 1,
                   "apply_effect": {
                       "effect_id": "knight_of_xoroth_forgefiends_bulwark",
                       "name": "Forgefiend's Bulwark",
                       "effect_type": "buff",
                       "duration": 3,
                       "stat_mods": {"damage_dealt_pct": 10},
                       "on_target": False}},
             source="CoA: 'Successful blocks, parries and dodges now have a "
                    "30% chance to Enrage you, increasing your damage dealt "
                    "by 10% for 10 seconds.' There is no on-block trigger, "
                    "so on_damage_taken stands in for the whole "
                    "block/parry/dodge set."),
        node(D, "black_skull_shield", "Black Skull Shield",
             "Increases the damage of Shieldgore by 8% and reduces its Rage "
             "cost by 2 per rank.",
             2, 3, 3, {f"ability_{A('shieldgore')}_damage": 0.08,
                       f"ability_{A('shieldgore')}_cost": 2},
             connect=["xorothian_finesse"],
             source="CoA: 'Reduces the Rage cost of Shieldgore by -5 and "
                    "increases its damage by 25%.' Both halves literal. "
                    "ability_<id>_<stat> keys are built by interpolation in "
                    "abilities.py, so a literal grep calls them dead."),

        node(D, "demonic_bulwark", "Demonic Bulwark",
             "Your blocks absorb an additional 5% of the damage dealt to "
             "you, per rank.",
             3, 0, 3, {"block_bonus_reduction": 0.05},
             connect=["hellfire_resolve"],
             source="CoA: 'Your successful blocks now have a 30% chance to "
                    "critically block for twice the normal amount.' "
                    "block_bonus_reduction is the engine's existing "
                    "critical-block hook, read in Character.take_damage. "
                    "The chance roll becomes a flat bonus."),
        node(D, "infernal_bulwark", "Infernal Bulwark",
             "Unleash Pestilence banks 20 Deathfire and increases the "
             "damage your blocks absorb by 20% for 3 turns.",
             3, 1, 1, {}, connect=["imp_guards"],
             proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
                   "ability_filter": [A("unleash_pestilence")],
                   "grant_resource": {"resource": "deathfire", "amount": 20},
                   "apply_effect": {
                       "effect_id": "knight_of_xoroth_infernal_bulwark",
                       "name": "Infernal Bulwark",
                       "effect_type": "buff",
                       "duration": 3,
                       "stat_mods": {"block_value_pct": 0.2},
                       "on_target": False}},
             source="CoA: 'Casting Unleash Pestilence now generates 4 stacks "
                    "of Demonfire and grants Infernal Bulwark: increases "
                    "block value by 20% for 18 seconds.' Both halves "
                    "literal, with ability_filter restricting the trigger "
                    "to Unleash Pestilence itself."),
        node(D, "brimstone_buckler", "Brimstone Buckler",
             "Taking a hit has a 10% chance per rank to call a Hellfire "
             "Imp.",
             3, 2, 3, {}, connect=["imp_aura"],
             proc={"trigger": "on_damage_taken", "chance": 10, "icd": 2,
                   "cast_ability": A("call_hellfire_imp")},
             source="CoA: 'Successful blocks now have a 30% chance to summon "
                    "1 Hellfire Imp to aid you in battle for 12 seconds. Can "
                    "only occur once every 3 sec.' cast_ability fires the "
                    "real summon, so the imp is a real pet; the icd is the "
                    "3-second lockout. on_damage_taken stands in for the "
                    "missing on-block trigger."),
        node(D, "hellfire_sieger", "Hellfire Sieger",
             "While below 35% health, you take 8% less damage per rank.",
             3, 3, 3, {"low_health_damage_reduction_pct": 0.08,
                       "low_health_threshold_pct": 0.35},
             connect=["black_skull_shield"],
             source="CoA: 'Doubles the absorption of Black Shield while "
                    "below 35% health.' Nothing can double an absorb "
                    "conditionally, so the node keeps the 35% threshold and "
                    "pays out as the engine's low-health mitigation pair "
                    "instead. low_health_threshold_pct is in "
                    "UNSCALED_EFFECT_KEYS, so it stays 35% at every rank."),

        node(D, "demolisher", "Demolisher",
             "Increases your threat generation by 8% and reduces the "
             "physical damage you take by 1% per rank.",
             4, 0, 3, {"threat_generation_pct": 0.08,
                       "physical_damage_taken_pct": -0.01},
             connect=["demonic_bulwark"],
             source="CoA: 'Casting Flesh Hook or Chainwhip now taunts the "
                    "target for 2 seconds and reduces your Physical damage "
                    "taken by -5% for 10 seconds.' A talent cannot add a "
                    "taunt to an existing ability (that is what the kit's "
                    "Dread is for), so this is the tree's threat node. 8% "
                    "per rank over 3 ranks is +24%, the same band as "
                    "Warrior Protection's Defiance and Guardian Vanguard's "
                    "Footman's Call, so the three plate tanks hold threat "
                    "equally. Note the key: threat_generation_pct is a "
                    "FRACTION as a talent effect and percentage POINTS as "
                    "an ability buff stat_mod."),
        node(D, "soul_furnace", "Soul Furnace",
             "Your heals have a 34% chance per rank to leave a shield "
             "absorbing 15% of the amount healed.",
             4, 1, 3, {}, connect=["infernal_bulwark"],
             proc={"trigger": "on_heal_cast", "chance": 34, "icd": 1,
                   "shield_pct": {"pct": 0.15, "duration": 3,
                                  "effect_id": "knight_of_xoroth_soul_furnace",
                                  "name": "Soul Furnace"}},
             source="CoA: 'Sacrificial Circle now grants you a damage "
                    "absorption shield equal to 15% of the total health of "
                    "each destroyed imp for 10 sec.' Imp health is not "
                    "readable from a proc; shield_pct sizes the absorb off "
                    "the heal that triggered it, which is the same "
                    "'heal, then keep part of it as armour' shape."),
        node(D, "warden_of_hellfire", "Warden of Hellfire",
             "Increases the damage of Skulltaker and Flames of Xoroth by 8% "
             "per rank.",
             4, 2, 3, {f"ability_{A('skulltaker')}_damage": 0.08,
                       f"ability_{A('flames_of_xoroth')}_damage": 0.08},
             connect=["brimstone_buckler"],
             source="CoA: 'Increases the damage dealt by Skulltaker and "
                    "Flames of Xoroth by 20%.' Literal."),

        node(D, "imp_gang_boss", "Imp Gang Boss",
             "Increases your pets' damage and health by 6% per rank.",
             5, 0, 2, {"pet_damage": 0.06, "pet_health": 0.06},
             connect=["demolisher"], total_slots=3,
             source="CoA: 'Your Call: Hellfire Imp now summons 2 additional "
                    "imps', plus Demonic Grit's '+15% total health'. The "
                    "engine supports one pet at a time, so more imps is not "
                    "available; a bigger, tougher imp is."),
        node(D, "hellwrath", "Hellwrath",
             "Increases the amount Black Shield absorbs by 10% and your "
             "Stamina by 2% per rank.",
             5, 1, 3, {f"ability_{A('black_shield')}_potency": 0.10,
                       "stamina_pct": 2.0},
             connect=["soul_furnace"], total_slots=3,
             source="CoA: 'Your Demon's Blood can now stack 5 additional "
                    "times and each stack now increases the absorption "
                    "amount of Black Shield by 1%.' Demon's Blood has no "
                    "engine hook, so the node pays the absorb directly. "
                    "ability_<id>_potency is the buff-magnitude key, read "
                    "in the buff branch of Ability._apply_effect."),
        node(D, "fiery_retribution", "Fiery Retribution",
             "Taking a hit has a 15% chance per rank to refresh Sacrificial "
             "Circle and Implosion.",
             5, 2, 2, {}, connect=["warden_of_hellfire"], total_slots=3,
             proc={"trigger": "on_damage_taken", "chance": 15, "icd": 2,
                   "reset_cooldown": {"abilities": [A("sacrificial_circle"),
                                                    A("implosion")]}},
             source="CoA: 'Each time a Hellfire Imp dies, you reduce the "
                    "cooldown of Sacrificial Circle by -2 sec and Implosion "
                    "by -1 sec.' There is no on-pet-death trigger, so it "
                    "fires off damage taken instead - which is when an imp "
                    "would have died. reset_cooldown is a real proc payload "
                    "and takes a list."),

        node(D, "call_hellfire_abyssal", "Call: Hellfire Abyssal",
             "Teaches Call: Hellfire Abyssal. While you fight, you and your "
             "allies take 5% less damage.",
             6, 0, 1, {"unlock_ability": A("call_hellfire_abyssal"),
                       "damage_taken_pct": -0.05},
             node_type="active",
             connect=["imp_gang_boss", "hellwrath", "fiery_retribution"],
             total_slots=1,
             source="Capstone. CoA: 'Call down a Hellfire Abyssal ... emits "
                    "an aura that reduces the damage taken by party and raid "
                    "members within 40 yds by 5%.' A talent's effects apply "
                    "to the Knight only, so the 5% is personal rather than "
                    "party-wide - the ally half is the one piece of this "
                    "node the engine cannot carry."),
    ],
    "Built from reference/coa_sidekick/SPEC_knight-of-xoroth__defiance.txt "
    "and the defiance block of talents/knight-of-xoroth.json. CoA rates it "
    "Dungeon A / Raid C and calls it 'Closest to Blood Death Knight, with a "
    "strong secondary nod to Vengeance Demon Hunter' - 'the core identifying "
    "loop sits close to Death Strike's math: build a stacking resource off "
    "your own weapon-swing abilities (Shieldgore to Demonfire), then dump it "
    "into a self-heal'. Its stat priority is Defense (to crit-immunity) > "
    "Stamina > Dodge > Parry > Block > Strength > Armor, which is why this "
    "tree buys avoidance (Xorothian Finesse) and Stamina before block, and "
    "why Strength is spent through a conversion (Hellfire Resolve) rather "
    "than taken raw. CoA's listed weaknesses are honoured rather than "
    "patched: no node here heals or shields an ally, and nothing in it "
    "breaks crowd control.")


# =================================================================== War
W = "knight_of_xoroth_war"
WAR = tree(
    W, "Knight of Xoroth War",
    "Two-hand melee damage. Gore and Meatsaw bank Deathfire, Skulltaker "
    "spends it, and Gore's lifesteal is the only thing keeping you up.",
    [
        node(W, "mutilation", "Mutilation",
             "Increases the damage of Gore and Sever by 6% per rank.",
             0, 0, 5, {f"ability_{A('gore')}_damage": 0.06,
                       f"ability_{A('sever')}_damage": 0.06},
             source="CoA: 'Increases the damage of Gore and Sever by 10%.' "
                    "Literal, spread over 5 ranks instead of 3."),
        node(W, "hellfire_striker", "Hellfire Striker",
             "Increases your critical strike chance by 1% and your hit "
             "rating by 1 per rank.",
             0, 1, 5, {"crit_chance_physical": 1.0, "hit_rating": 1},
             source="CoA: 'Increases your critical strike and hit chance by "
                    "3%.' CoA's stat priority for this spec leads with Hit "
                    "'until your specials stop missing a +3-level target', "
                    "so the hit half is first-tier on purpose."),
        node(W, "xorothian_strength", "Xorothian Strength",
             "Increases your Strength by 2% per rank.",
             0, 2, 5, {"strength_pct": 2.0},
             source="CoA class tree: 'Increases your Strength by 5%.' "
                    "Percentage POINTS, not a fraction."),
        node(W, "war_pig", "War Pig",
             "Increases your physical damage by 2% per rank.",
             0, 3, 5, {"physical_damage": 0.02},
             source="CoA class tree: 'Increases your Physical damage dealt "
                    "by 4%.'"),

        node(W, "gore", "Gore",
             "Teaches Gore, a fast strike on a short cooldown that banks 10 "
             "Deathfire.",
             1, 0, 1, {"unlock_ability": A("gore")}, node_type="active",
             connect=["mutilation"],
             source="CoA gates Gore behind two maxed War talents and the "
                    "whole spec is built on it ('build Demonfire with Gore'), "
                    "so it is the tree's first pick."),
        node(W, "jagged_edge", "Jagged Edge",
             "Dealing damage has a 34% chance per rank to return 5 Rage.",
             1, 1, 3, {}, connect=["hellfire_striker"],
             proc={"trigger": "on_damage_cast", "chance": 34, "icd": 1,
                   "grant_resource": {"resource": "rage", "amount": 5}},
             source="CoA: 'Increases your Rage generated from damage dealt "
                    "by 20%.' There is no Rage-per-damage multiplier to "
                    "scale - Rage only arrives from the basic Attack (see "
                    "CombatEngine) - so the node grants it directly on a "
                    "proc instead."),
        node(W, "consuming_blade", "Consuming Blade",
             "Increases the critical strike chance of Gore by 3% per rank.",
             1, 2, 5, {f"ability_{A('gore')}_crit": 3.0},
             connect=["xorothian_strength"],
             source="CoA: 'Increases the critical strike chance of Gore by "
                    "25% and your expertise by 5.' There is no expertise "
                    "stat on Character, so only the crit half lands. "
                    "ability_<id>_crit is added straight to the roll in "
                    "Ability._crit_chance, so it is percentage points."),
        node(W, "demonic_frenzy", "Demonic Frenzy",
             "Increases your haste by 2 per rank.",
             1, 3, 5, {"haste": 2.0}, connect=["war_pig"],
             source="CoA: 'Casting Sever now increases your attack speed by "
                    "20% for 10 seconds. Casting Gore extends the duration.' "
                    "A self-maintained attack-speed window with no engine "
                    "shape, so it is flat haste."),

        node(W, "gored", "Gored",
             "Increases the damage of Warbringer by 10% per rank.",
             2, 0, 3, {f"ability_{A('warbringer')}_damage": 0.10},
             connect=["gore"],
             source="CoA: 'Damage dealt by Gore and Meatsaw now increases "
                    "your target's damage taken from Skulltaker and "
                    "Warbringer by 15%.' A stacking target-side debuff "
                    "applied by two other abilities has no shape, so the "
                    "payoff lands on Warbringer directly."),
        node(W, "murderous_might", "Murderous Might",
             "Increases the damage of Skulltaker by 10% and the healing of "
             "Suffuse by 5% per rank.",
             2, 1, 3, {f"ability_{A('skulltaker')}_damage": 0.10,
                       f"ability_{A('suffuse')}_healing": 0.05},
             connect=["jagged_edge"],
             source="CoA: 'Increases the damage of abilities that spend "
                    "Demonfire by 25%.' Skulltaker and Suffuse are this "
                    "spec's two Deathfire spenders, so both are named. A "
                    "heal's per-ability key is ability_<id>_healing, not "
                    "_damage."),
        node(W, "chop_shop", "Chop Shop",
             "Increases your critical strike chance by 1% per rank.",
             2, 2, 5, {"crit_chance_physical": 1.0},
             connect=["consuming_blade"],
             source="CoA: 'Each stack of Demon's Blood now increases the "
                    "critical strike chance of Sever and Meatsaw by 1%.' "
                    "Demon's Blood stacks are not modellable, so the crit "
                    "is unconditional."),
        node(W, "absolutism", "Absolutism",
             "Increases your armor penetration by 2% per rank.",
             2, 3, 3, {"armor_penetration_pct": 2.0},
             connect=["demonic_frenzy"],
             source="CoA: 'Damage dealt by Meatsaw now ignores -10% of the "
                    "target's Armor.' A real armour-penetration stat exists "
                    "and is read in the derived-stat pass, but not per "
                    "ability, so it applies to everything. Note "
                    "armor_penetration_pct takes percentage POINTS."),

        node(W, "hellsmelted", "Hellsmelted",
             "Your critical strikes send out searing fire, dealing 55 extra "
             "damage.",
             3, 0, 3, {}, connect=["gored"],
             proc={"trigger": "on_crit", "chance": 34, "icd": 1,
                   "damage_flat": 55},
             source="CoA: Burning Blade 'causes you to send out searing fire "
                    "with each melee critical strike, dealing Fire damage in "
                    "a line', and Hellsmelted 'increases the critical strike "
                    "chance and damage of Burning Blade by 30%'. The on-crit "
                    "fire is the real mechanic; the line shape is not "
                    "available."),
        node(W, "knight_of_pestilence", "Knight of Pestilence",
             "Increases the damage of Unleash Pestilence by 10% per rank.",
             3, 1, 3, {f"ability_{A('unleash_pestilence')}_damage": 0.10},
             connect=["murderous_might"],
             source="CoA: 'Increases the critical damage of your Pestilences "
                    "by 50%.' There is no per-ability crit-damage-of-a-buff "
                    "key, so the burst the Pestilence unleashes is what gets "
                    "scaled."),
        node(W, "hand_of_doom", "Hand of Doom",
             "Increases the damage of Sever by 8% per rank.",
             3, 2, 3, {f"ability_{A('sever')}_damage": 0.08},
             connect=["chop_shop"],
             source="CoA: 'Increases the Weapon Damage dealt by Sever by "
                    "10%, increased by 10% for each Demonfire you have "
                    "active.' The Deathfire-count scaling is not readable "
                    "from a talent, so the base half lands."),
        node(W, "bringer_of_destruction", "Bringer of Destruction",
             "Taking a critical hit has a 15% chance per rank to bank 10 "
             "Deathfire.",
             3, 3, 2, {}, connect=["absolutism"],
             proc={"trigger": "on_damage_taken", "chance": 15, "icd": 2,
                   "grant_resource": {"resource": "deathfire", "amount": 10}},
             source="CoA: 'Critical damage taken now grants you 1 Demonfire "
                    "and 5 Rage. Can only occur once every 3 sec.' There is "
                    "no on-critically-hit trigger, so it fires off damage "
                    "taken at a low chance; the icd is CoA's own lockout."),

        node(W, "the_butcher", "The Butcher",
             "Increases the damage of Meatsaw by 10% per rank.",
             4, 0, 3, {f"ability_{A('meatsaw')}_damage": 0.10},
             connect=["hellsmelted"],
             source="CoA: 'Damage dealt by Meatsaw now increases the damage "
                    "dealt by subsequent Meatsaws by 10% ... stacking 5 "
                    "times.' The ramp is not modellable, so it is a flat "
                    "multiplier."),
        node(W, "conquerors_will", "Conqueror's Will",
             "Increases your critical strike chance by 1% and your physical "
             "damage by 2% per rank.",
             4, 1, 3, {"crit_chance_physical": 1.0, "physical_damage": 0.02},
             connect=["knight_of_pestilence"],
             source="CoA: 'Increases the critical strike chance of all party "
                    "and raid members by 3%. In addition, Physical critical "
                    "strikes now increase the target's Physical damage taken "
                    "by 4%.' A talent's effects reach the Knight only, so "
                    "the party half is lost - which is the whole of what CoA "
                    "lists as this spec's group support."),
        node(W, "screamin_demon", "Screamin' Demon",
             "Reduces the cooldown of Unleash Pestilence by 1 turn per "
             "rank.",
             4, 2, 3, {f"ability_{A('unleash_pestilence')}_cooldown": 1},
             connect=["hand_of_doom"],
             source="CoA: 'Reduces the cooldown of Unleash Pestilence by -15 "
                    "sec.' Ability.talented_cooldown keeps at least 1 turn "
                    "of any cooldown, so three ranks against a 6-turn base "
                    "cannot delete it."),

        node(W, "render", "Render",
             "Grants haste equal to 3% of your Strength per rank.",
             5, 0, 2, {"haste_from_strength_pct": 0.03},
             connect=["the_butcher"], total_slots=3,
             source="CoA: 'Increases your melee haste rating by 30% of your "
                    "Strength.' A real <target>_from_<source>_pct conversion "
                    "- haste is a conversion target and strength a source in "
                    "character.py's shared maps."),
        node(W, "gorged", "Gorged",
             "Gore has a 34% chance per rank to leech half the damage it "
             "deals back to you.",
             5, 1, 3, {}, connect=["conquerors_will"], total_slots=3,
             proc={"trigger": "on_damage_cast", "chance": 34, "icd": 0,
                   "ability_filter": [A("gore")],
                   "leech_pct": {"pct": 0.5}},
             source="CoA: 'Gore now heals you for 50% of the damage dealt "
                    "over 3 sec', and CoA calls Gorged 'a Death Strike and "
                    "lifesteal analog' that is this spec's only sustain. "
                    "leech_pct heals off the triggering hit, and "
                    "ability_filter keeps it on Gore where CoA puts it. The "
                    "3-stack Brimstone Bludgeon payoff is not modellable."),
        node(W, "hellknight", "Hellknight",
             "Increases your physical damage by 3% and your critical strike "
             "chance by 1% per rank.",
             5, 2, 2, {"physical_damage": 0.03, "crit_chance_physical": 1.0},
             connect=["screamin_demon"], total_slots=3,
             source="CoA: 'While above 75% health, all direct Physical "
                    "damage dealt will grant a stack of Hellknight: "
                    "Physical Damage and critical strike chance increased by "
                    "1%, stacking 5 times.' There is no above-X%-health "
                    "conditional (only the low-health pair), so the stacked "
                    "payoff is granted outright at a smaller size."),

        node(W, "brimstone_bludgeon", "Brimstone Bludgeon",
             "Teaches Brimstone Bludgeon, a heavy cleave on everything near "
             "your target. Increases your physical damage by 8%.",
             6, 0, 1, {"unlock_ability": A("brimstone_bludgeon"),
                       "physical_damage": 0.08},
             node_type="active",
             connect=["render", "gorged", "hellknight"], total_slots=1,
             source="Capstone. CoA: 'Brimstone Bludgeon, which transforms "
                    "Sever, is the AoE keystone', and it is a tier-6 pick in "
                    "the real tree too. CoA rates this spec 'Middling "
                    "sustained single-target DPS on patchwork fights - high "
                    "throughput ceiling', so the capstone is a cleave "
                    "button, not a single-target one."),
    ],
    "Built from reference/coa_sidekick/SPEC_knight-of-xoroth__war.txt and the "
    "war block of talents/knight-of-xoroth.json. CoA calls it 'Closest to a "
    "retail Fury/Blood-hybrid Death Knight' and 'a self-sufficient Str/AP "
    "melee bruiser'. Its stat priority is Hit > Expertise > Strength > Armor "
    "Penetration > Critical Strike > Haste, which is why Hit sits in tier 0 "
    "(Hellfire Striker) and Haste is the last thing the tree buys (Render). "
    "Expertise has no Character stat, so the two nodes that grant it in CoA "
    "(Consuming Blade, Greater Imp) keep only their other half. CoA's listed "
    "weaknesses are kept: there is no damage-reduction node anywhere in this "
    "tree and no node that heals anyone but the Knight.")


# ============================================================== Hellfire
H = "knight_of_xoroth_hellfire"
HELLFIRE = tree(
    H, "Knight of Xoroth Hellfire",
    "Melee and Fire magic together. Strength feeds your spell power, "
    "Infernal Strike and Seeking Flame bank Deathfire, and Hellmaw and "
    "Hellstorm spend it. Nothing here keeps you alive.",
    [
        node(H, "combusting_blade", "Combusting Blade",
             "Increases your Intellect by 2% and reduces the Rage cost of "
             "Infernal Strike by 1 per rank.",
             0, 0, 5, {"intellect_pct": 2.0,
                       f"ability_{A('infernal_strike')}_cost": 1},
             source="CoA: 'Increases your Intellect by 5% and reduces the "
                    "Rage cost of Infernal Strike by -5.' Both halves "
                    "literal. Intellect matters to this spec and no other "
                    "Knight spec, because Burning Power turns it into attack "
                    "power."),
        node(H, "invasion", "Invasion",
             "Increases your Fire damage by 2% per rank.",
             0, 1, 5, {"fire_spell_damage": 0.02},
             source="CoA: 'All Fire damage dealt is increased by 10% to "
                    "enemies above 80% health.' There is no above-X%-health "
                    "conditional, so the bonus is unconditional and smaller. "
                    "<school>_spell_damage keys are assembled from the "
                    "ability's real school at cast time, so they only reach "
                    "spell_damage and spell_dot abilities, not weapon "
                    "strikes that happen to be Fire."),
        node(H, "flamewrath", "Flamewrath",
             "Increases the critical strike chance of Seeking Flame by 4% "
             "per rank.",
             0, 2, 5, {f"ability_{A('seeking_flame')}_crit": 4.0},
             source="CoA: 'Increases the critical strike chance of Seeking "
                    "Flame by 20%.' Literal, as percentage points added to "
                    "that ability's own roll."),
        node(H, "infernal_pursuit", "Infernal Pursuit",
             "Increases your haste by 2 per rank.",
             0, 3, 5, {"haste": 2.0},
             source="CoA: 'Increases your melee haste by 3% and reduces the "
                    "duration of root effects against you by -15%.' There "
                    "is no root category in this engine - is_stun is the "
                    "only incapacitate - so only the haste lands."),

        node(H, "hellmaw", "Hellmaw",
             "Teaches Hellmaw, a Shadowflame strike that keeps burning. "
             "Costs 40 Deathfire.",
             1, 0, 1, {"unlock_ability": A("hellmaw")}, node_type="active",
             connect=["combusting_blade"],
             source="CoA gates Hellmaw behind two maxed talents and the "
                    "rotation dumps into it ('dump stacked Demonfire into "
                    "Hellmaw for a big Shadowflame hit-and-burn'), so it is "
                    "the tree's first pick."),
        node(H, "burning_power", "Burning Power",
             "Grants spell power equal to 3% of your Strength and attack "
             "power equal to 3% of your Intellect, per rank.",
             1, 1, 5, {"spell_damage_from_strength_pct": 0.03,
                       "ap_from_intellect_pct": 0.03},
             connect=["invasion"],
             source="CoA: 'Increases your attack power by 100% of your "
                    "Intellect and your spell damage by 50% of your "
                    "Strength.' Both are real "
                    "<target>_from_<source>_pct conversions. This node is "
                    "the whole reason the spec is a melee/caster hybrid "
                    "rather than two half-specs, and why CoA's stat "
                    "priority for it runs Spell Hit > Spell Power > "
                    "Strength."),
        node(H, "to_ashes", "To Ashes",
             "Increases your spell critical strike chance by 1% per rank.",
             1, 2, 3, {"crit_chance_spell": 1.0}, connect=["flamewrath"],
             source="CoA: 'Increases the critical strike chance of abilities "
                    "that spend Demonfire by 5%.' Per-ability crit is "
                    "available but this names a whole category, so it is "
                    "general spell crit."),
        node(H, "hellfire_embers", "Hellfire Embers",
             "Increases your pets' damage by 6% per rank.",
             1, 3, 3, {"pet_damage": 0.06}, connect=["infernal_pursuit"],
             source="CoA: 'Increases the Fire damage dealt by your Hellfire "
                    "Imp by 30% against enemies above 80% maximum health.' "
                    "The health gate and the school restriction are not "
                    "available; the pet damage is."),

        node(H, "cinderblade", "Cinderblade",
             "Grants spell critical strike chance equal to 2% of your "
             "Intellect, and 1% spell hit, per rank.",
             2, 0, 5, {"crit_chance_spell_from_intellect_pct": 0.02,
                       "hit_chance_spell": 1.0},
             connect=["hellmaw"],
             source="CoA: 'Increases your critical strike rating by 20% of "
                    "your Intellect and your spell hit chance by 6%.' Both "
                    "halves literal; the crit half is a real conversion."),
        node(H, "shadowflame_forge", "Shadowflame Forge",
             "Hellmaw lasts 1 turn longer per rank.",
             2, 1, 2, {f"ability_{A('hellmaw')}_duration": 1},
             connect=["burning_power"],
             source="CoA: 'Increases the duration of Hellmaw by 3 sec.' "
                    "Ability.talented_duration derives a DoT's per-turn "
                    "damage from its BASE duration, so an extension adds "
                    "ticks rather than thinning the total."),
        node(H, "seething_strikes", "Seething Strikes",
             "Increases the damage of Sever by 8% per rank.",
             2, 2, 3, {f"ability_{A('sever')}_damage": 0.08},
             connect=["to_ashes"],
             source="CoA: 'Increases the damage of Sever by 30% against "
                    "Burning targets and it now increases the targets chance "
                    "to be critically struck by 3%.' There is no burning "
                    "condition and no target-side crit-taken debuff, so the "
                    "damage is unconditional and smaller."),
        node(H, "infernal_steel", "Infernal Steel",
             "Reduces the Deathfire cost of Hellmaw by 8% per rank.",
             2, 3, 3, {f"ability_{A('hellmaw')}_cost_pct": 0.08},
             connect=["hellfire_embers"],
             source="CoA: 'Casting Skulltaker with 6 Demonfire stacks now "
                    "causes your next Hellmaw within 15 seconds to tick "
                    "-25% faster and cost -50% less Rage.' The conditional "
                    "window is not modellable, so the discount is "
                    "permanent and smaller. POSITIVE is the discount on a "
                    "_cost_pct key."),

        node(H, "brimstone_flames", "Brimstone Flames",
             "Increases the damage of Seeking Flame by 10% per rank.",
             3, 0, 3, {f"ability_{A('seeking_flame')}_damage": 0.10},
             connect=["cinderblade"],
             source="CoA: 'Damage dealt by Seeking Flame is increased by 20% "
                    "on enemies affected by Pestilence of Apocalypse.' The "
                    "aura condition is not readable, so it is flat."),
        node(H, "brimstone_splinters", "Brimstone Splinters",
             "Seeking Flame has a 20% chance per rank to bank 10 extra "
             "Deathfire.",
             3, 1, 3, {}, connect=["shadowflame_forge"],
             proc={"trigger": "on_damage_cast", "chance": 20, "icd": 0,
                   "ability_filter": [A("seeking_flame")],
                   "grant_resource": {"resource": "deathfire", "amount": 10}},
             source="CoA: 'Grants Seeking Flame a 30% chance to generate 1 "
                    "additional Demonfire when it deals damage.' Literal, "
                    "with ability_filter holding it to Seeking Flame."),
        node(H, "infernal_pummeling", "Infernal Pummeling",
             "Increases the damage of Flames of Xoroth by 10% per rank.",
             3, 2, 3, {f"ability_{A('flames_of_xoroth')}_damage": 0.10},
             connect=["seething_strikes"],
             source="CoA: 'Melt now increases the damage your target takes "
                    "from Flames of Xoroth and Skulltaker by 10%.' A "
                    "target-side amp applied by a third ability has no "
                    "shape, so the payoff goes straight onto Flames of "
                    "Xoroth."),
        node(H, "inferno_blast", "Inferno Blast",
             "Increases your spell critical strike damage by 4% per rank.",
             3, 3, 2, {"crit_damage_spell": 0.04},
             connect=["infernal_steel"],
             source="CoA: 'Increases your critical damage against Burning "
                    "targets by 20%.' No burning condition, so it is "
                    "general. crit_damage_spell is a fraction added to the "
                    "crit multiplier."),

        node(H, "rain_of_chaos", "Rain of Chaos",
             "Increases the damage of your damage-over-time effects by 5% "
             "and your Fire damage by 2% per rank.",
             4, 0, 3, {"dot_damage": 0.05, "fire_spell_damage": 0.02},
             connect=["brimstone_flames"],
             source="CoA: 'Casting Flames of Xoroth with 6 Demonfire now "
                    "calls down a Rain of Chaos: molten rain burns enemies "
                    "in the area causing Fire Damage over 9 seconds.' A "
                    "conditional second DoT is not available, so the node "
                    "scales the burns the spec already has."),
        node(H, "partners_in_flames", "Partners in Flames",
             "Your critical strikes have a 25% chance to increase your "
             "damage by 5% for 3 turns.",
             4, 1, 3, {}, connect=["brimstone_splinters"],
             proc={"trigger": "on_crit", "chance": 25, "icd": 2,
                   "apply_effect": {
                       "effect_id": "knight_of_xoroth_partners_in_flames",
                       "name": "Partners in Flames",
                       "effect_type": "buff",
                       "duration": 3,
                       "stat_mods": {"damage_dealt_pct": 5},
                       "on_target": False}},
             source="CoA: 'Fire damage dealt by your Greater Imp now has a "
                    "25% chance to empower you, increasing your damage dealt "
                    "by 5% for 10 seconds.' A pet's damage cannot fire the "
                    "owner's proc, so the Knight's own crits trigger it. "
                    "Chance is not rank-scaled here because it is already "
                    "CoA's own number; the ranks buy nothing else, so this "
                    "node is deliberately the flattest in the tree."),
        node(H, "doom", "Doom",
             "Increases your pets' damage and health by 6% per rank.",
             4, 2, 3, {"pet_damage": 0.06, "pet_health": 0.06},
             connect=["infernal_pummeling"],
             source="CoA: 'Transforms your Greater Imp into a Doomguard for "
                    "12 seconds. While transformed, your Doomguard deals 20% "
                    "more damage.' There is no pet transformation, so it is "
                    "a permanent, smaller version of the same thing."),

        node(H, "into_the_maw", "Into the Maw",
             "Increases the damage of your area attacks by 10% per rank.",
             5, 0, 3, {"aoe_damage": 0.10}, connect=["rain_of_chaos"],
             total_slots=3,
             source="CoA: 'Hellmaw causes a Hellfire Explosion at the end of "
                    "its duration, dealing additional Fire damage to all "
                    "nearby enemies.' A terminal explosion is not "
                    "available, so the node pays the spec's AoE instead. "
                    "aoe_damage is only read for target_type enemy_aoe "
                    "abilities, which is what Hellstorm, Flames of Xoroth "
                    "and Unleash Pestilence are."),
        node(H, "hellbringer", "Hellbringer",
             "Increases all damage you deal by 3% per rank.",
             5, 1, 2, {"all_damage": 0.03},
             connect=["partners_in_flames"], total_slots=3,
             source="CoA: 'Increases the all damage dealt by party and raid "
                    "members by 3%.' A talent reaches the Knight only, so "
                    "the party half is lost."),
        node(H, "punisher", "Punisher",
             "Increases your spell damage by 3% per rank.",
             5, 2, 2, {"spell_damage": 0.03}, connect=["doom"],
             total_slots=3,
             source="CoA: 'Increases the attack power and spell power "
                    "scaling of Seeking Flame by 25%.' Scaling "
                    "coefficients are not talent-addressable, so the node "
                    "raises spell damage, which is what that scaling was "
                    "buying."),

        node(H, "hellfire_form", "Hellfire Form",
             "Teaches Hellfire Form. Increases your Fire damage by 5%.",
             6, 0, 1, {"unlock_ability": A("hellfire_form"),
                       "fire_spell_damage": 0.05},
             node_type="active",
             connect=["into_the_maw", "hellbringer", "punisher"],
             total_slots=1,
             source="Capstone. CoA: 'Hellfire Form is also the "
                    "Metamorphosis-style transformation cooldown', 'Pop "
                    "Hellfire Form against tougher fights, banking Demonfire "
                    "first for max duration'. It is a tier-2 pick in the real "
                    "tree, promoted to the capstone here because Frontier "
                    "has one capstone and this is the spec's defining "
                    "button."),
    ],
    "Built from reference/coa_sidekick/SPEC_knight-of-xoroth__hellfire.txt "
    "and the hellfire block of talents/knight-of-xoroth.json. CoA rates it "
    "Raid A and calls it 'Closest to Vengeance Demon Hunter, re-tuned as a "
    "pure damage spec rather than a tank', with the warning that 'Vengeance's "
    "actual survival kit ... isn't present here, and there isn't even a "
    "self-shield to stand in for it'. That is honoured literally: this tree "
    "has no mitigation node, no absorb and no heal, and the only defensives "
    "available to the spec are the shared class kit's Suffuse and Black "
    "Shield, which CoA calls 'picks that compete with damage'. Its stat "
    "priority is Spell Hit > Spell Power > Strength > Critical Strike > "
    "Haste > Intellect, so spell hit (Cinderblade) and the Strength-to-spell "
    "power conversion (Burning Power) are bought before anything else.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the files")
    args = parser.parse_args()

    ability_doc = {
        "class": "Knight of Xoroth",
        "_source_note": __doc__.strip().split("\n\n")[1].replace("\n", " "),
        "abilities": ABILITIES,
    }

    targets = [
        (ROOT / f"data/abilities/{PREFIX}.json", ability_doc),
        (ROOT / f"data/talents/{PREFIX}_defiance.json", DEFIANCE),
        (ROOT / f"data/talents/{PREFIX}_war.json", WAR),
        (ROOT / f"data/talents/{PREFIX}_hellfire.json", HELLFIRE),
    ]

    print(f"{len(ABILITIES)} abilities")
    for path, doc in targets[1:]:
        points = sum(n["max_points"] for n in doc["nodes"])
        print(f"{doc['tree_id']}: {len(doc['nodes'])} nodes, {points} points")

    if not args.apply:
        print("\n(dry run - pass --apply to write)")
        return 0

    for path, doc in targets:
        path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
