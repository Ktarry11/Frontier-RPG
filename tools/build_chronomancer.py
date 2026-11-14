#!/usr/bin/env python3
"""Author the Chronomancer: ability kit + three talent trees.

    PYTHONPATH=. python3 tools/build_chronomancer.py [--apply]

Chronomancer is one of the twelve CoA classes that shipped with base stats,
cloth armour, a staff/wand/dagger/tome proficiency and a Mana pool but no
abilities and no talents, so it could not be picked. This builds the missing
half, following tools/build_guardian.py's structure.

SOURCE. reference/coa_sidekick/CLASS_chronomancer.txt and the three
SPEC_chronomancer__*.txt pages for role, rotation and identity;
reference/coa_sidekick/talents/chronomancer.json for every talent name,
description and tier. Every ability and talent name below is a real CoA name
off those files. Identity per that reference:

  Infinite    RANGED DPS  "Closest to an Affliction/Destruction Warlock
                          hybrid rendered in chaos-and-time flavor."
                          Rolling DoTs (Melt Reality, Timerend,
                          Decomposition) feed Anomaly Spikes, stacking haste
                          and cooldown resets, then cash into the
                          Incarnation of Chaos window.
  Time        HEALER      "Closest to Preservation Evoker." Epoch plus
                          Accelerated Recovery, reshaped by whichever of the
                          four Aeons is loaded, on a stack of absorbs.
  Artificer   RANGED DPS  "A stack-driven Arcane Mage crossed with the
                          Essence loop of an Evoker." Wand attacks build,
                          Distortion spells spend, one Continuum active at a
                          time, and nearly the whole kit scales off Spirit.

NUMBERS ARE FRONTIER'S, NOT CoA'S. The reference is a fan-made planning tool
whose own disclaimer says COA is pre-meta. Damage, healing and Mana curves
copy data/abilities/mage.json, the closest shipped cloth caster: 9 ranks at
levels 1/6/12/18/24/32/40/48/56, linear damage growth, and Mana costs that
grow WITH the rank rather than staying flat (mage_fireball 30 -> 102 Mana as
it goes 44 -> 132 damage). Later abilities take fewer ranks, spaced to keep
every rank at or below level 58 so nothing is stranded above the cap.

RESOURCE. Mana, taken from CLASS_RESOURCE_MAP in combat/abilities.py
("Chronomancer": (ResourceType.MANA, None)) - no secondary pool. That is the
single biggest constraint on this class, because CoA gives all three specs a
bespoke second currency:

  Echo Fragments (Artificer)   banked by wand casts, spent on Distortion and
                               Continuum spells
  Sands of Time (Time)         built by Epoch, buffing its own healing
  Order/Chaos charges          spent on Infinite's finishers

None of them can exist: a resource has to be in CLASS_RESOURCE_MAP, and that
map is a shared file this pass does not edit. Every one of them is modelled
instead as cooldowns, stacking proc buffs and ability_<id>_* talents, which
preserves the "build, then spend" rhythm without inventing a pool the engine
would never display or regenerate. Noted again on each node it touches.

Talent effect keys are restricted to ones the engine actually reads, verified
with tools/validate_class.py (liveness delegated to tools/audit_talents.py).
Two mechanics the reference leans on hard turned out to be unreachable and are
recorded where they land:

  Enemy VULNERABILITY debuffs. Infinite's Time Means Nothing and Magic
  Erosion both raise the damage a target takes. Character.take_damage reads
  magic_damage_taken_pct and friends off status effects, but
  Monster.take_damage does not read any of them - it only reads `armor` and
  `attack_power` status mods - so a vulnerability debuff does nothing to the
  thing players actually fight. Both nodes carry caster-side equivalents
  (spell penetration, hit rating, flat spell damage) instead.

  Cast time. Half the class's talents shorten a cast ("Improved Reverse
  Wound", "Bronze Echoes", "Endless Sands", "Aeon of Resilience"). This is a
  turn-based engine with no cast bar, so those land as Mana discounts or
  healing increases, whichever the talent was really buying.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Mage's shipped rank schedule - see module docstring.
RANK_LEVELS = [1, 6, 12, 18, 24, 32, 40, 48, 56]

#: How much faster Mana cost grows than damage does across a rank table.
#: Measured off mage.json: Fireball triples its damage and 3.4x's its cost,
#: Frostbolt 3.05x/3.4x, Arcane Explosion 2.42x/2.6x. A Mana class's higher
#: ranks are meant to cost more per cast, not just hit harder - which is the
#: whole difference from a flat-cost Energy or Rage kit.
COST_GROWTH = 1.15

#: Base costs below are priced against mage.json's own value-per-Mana, read
#: off its rank-1 entries, because a Mana class lives or dies on that number
#: and eyeballing it produced a Chronomancer that lost 42% of its level-20
#: fights in tools/sim_class_balance.py while every other caster won:
#:
#:   direct nuke     Frostbolt 42/25 = 1.7     Fireball 44/30 = 1.5
#:   DoT             Living Flame 54/30 = 1.8
#:   AoE             Arcane Explosion 52/45 = 1.2   Cone of Cold 58/60 = 1.0
#:   AoE DoT         Blizzard 90/70 = 1.3
#:   cooldown nuke   Pyroblast 62/60 = 1.0     Fire Blast 58/55 = 1.1
#:   direct heal     Heal 54/40 = 1.4          Renew 48/35 = 1.4
#:   party heal      Circle of Healing 82/90 = 0.9  Prayer 86/110 = 0.8
#:
#: A DoT's effect_value is its TOTAL across the whole duration, so pricing a
#: 5-turn DoT off a direct nuke's rate overcharges it by the duration. That is
#: the mistake the first pass made on Melt Reality (96 damage for 70 Mana, a
#: rate no Mage spell comes close to paying) and it is why the DoTs below look
#: cheap next to the nukes.


def ranks(base, step, cost, start=1, count=9):
    """Rank table on the Mage schedule, starting at `start`.

    `base`/`step` give linear damage (or healing) growth. Cost rises with
    the rank in proportion to the effect value, steepened by COST_GROWTH.
    Levels past the 9-rank schedule are spaced evenly to stay at or below
    58 so every rank is reachable at the level 60 cap.
    """
    if start == 1:
        levels = RANK_LEVELS[:count]
    else:
        span = max(1, (58 - start) // max(1, count - 1)) if count > 1 else 1
        levels = [min(58, start + i * span) for i in range(count)]
    out = []
    for i, level in enumerate(levels):
        value = base + step * i
        grown = 1.0 + COST_GROWTH * (value / float(base) - 1.0)
        out.append({"rank": i + 1, "level_req": level,
                    "cost": int(round(cost * grown)),
                    "effect_value": int(round(value))})
    return out


def one(level, cost, value=100):
    """Single-rank table, for cooldowns and stances that do not scale.

    value DEFAULTS TO 100, which matters: Ability.use scales a buff's or
    debuff's declared stat_mods by effect_value/100 (combat/abilities.py's
    buff and debuff branches), so a single-rank buff authored with
    effect_value 0 applies literally nothing. tools/build_guardian.py's own
    one() defaults to 0 and every Guardian buff in the game is currently
    dead because of it - verified by reading the scaled mods back off a
    level 60 Guardian. 100 means "the stat_mods as written".
    """
    return [{"rank": 1, "level_req": level, "cost": cost, "effect_value": value}]


def restore(level, cost, pct, extra=0):
    """Rank table for an effect_type="restore_resource" ability.

    These read mana_restore_pct off the rank rather than effect_value (see
    Ability.mana_restore_pct), so the field has to be on the rank dict.
    """
    return [{"rank": 1, "level_req": level, "cost": cost,
             "effect_value": extra, "mana_restore_pct": pct}]


def ability(aid, name, effect_type, description, rank_table, *, cooldown=0,
            duration=0, stat_mods=None, icon=None, source=None, **extra):
    out = {
        "ability_id": f"chronomancer_{aid}",
        "name": name,
        "resource_type": "mana",
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


# ============================================================== ability kit
# Order is roughly the order a player meets them: the shared class kit
# first, then each spec's own spells.
#
# SCHOOL. Everything magical here is arcane. CoA calls Infinite's damage
# "Chromatic" and Artificer's "Arcane"; chromatic is not one of the engine's
# six schools (arcane/fire/frost/nature/shadow/holy), and arcane is the one
# a time mage would plausibly share with Artificer, so the class resolves to
# a single school and its <school>_spell_damage talents all bite. Artificer's
# wand line is the deliberate exception - see Artificer's Wand below.
ABILITIES = [
    ability("attack", "Attack", "damage",
            "A swing of whatever you are holding.", one(1, 0, 0),
            icon=None,
            source="Convention: every class ships a free rank-1 Attack."),

    # ---- shared class kit (CoA's class tree + the spells all three
    # rotations press)
    ability("unmake", "Unmake", "spell_damage",
            "Take a piece of the target out of the present and do not give "
            "it back.",
            ranks(42, 11, 25), target_type="enemy", damage_school="arcane",
            source="CoA class tree: 'Unearthed Pools reduces the cast time "
                   "of Unmake'; Infinite's rotation uses it as a filler and "
                   "Artificer transforms it into Artificer's Wand. Mage's "
                   "Frostbolt curve - the class's cheap, always-available "
                   "nuke."),
    ability("wand_of_time", "Wand of Time", "ranged_damage",
            "A short, precise strike with your wand, landing a fraction "
            "before you make it.",
            ranks(26, 7, 15), cooldown=1, target_type="enemy",
            source="CoA: Wand of Time is a class ability that Infinite "
                   "transforms into Timerend and Artificer uses as its "
                   "fragment generator. ranged_damage, not spell_damage - "
                   "it is a wand swing, and Artificer's Wand Expert "
                   "('increases your ranged attack power by 100% of your "
                   "Spirit') only has something to scale if the engine's "
                   "ranged_attack_power is what drives it."),
    ability("reverse_wound", "Reverse Wound", "heal",
            "Walk the injury backwards to a moment before it happened.",
            ranks(52, 27, 40, start=4, count=6), cooldown=1,
            target_type="ally",
            source="CoA says in all three spec pages that Reverse Wound is "
                   "'your only real self-heal'. Priest's Heal curve."),
    ability("decomposition", "Decomposition", "spell_dot",
            "Let time do to the target in seconds what it would have taken "
            "years to do.",
            ranks(66, 28, 26, start=8, count=6), cooldown=2, duration=3,
            target_type="enemy", damage_school="arcane",
            source="CoA class tree: 'Eternal increases the duration of your "
                   "Accelerated Recovery and Decomposition'. Infinite seeds "
                   "it for proc uptime, Artificer turns it into a Distortion "
                   "spell."),
    ability("accelerated_recovery", "Accelerated Recovery", "hot",
            "Their body heals at the pace it would have taken a month to "
            "manage.",
            ranks(50, 24, 35, start=10, count=6), duration=4,
            target_type="ally",
            source="CoA class tree ability, and half of Time's core loop."),
    ability("chronostasis", "Chronostasis", "debuff",
            "The target keeps moving. It simply takes them longer than it "
            "should.",
            one(12, 25), cooldown=3, duration=2,
            stat_mods={"haste": -25.0}, target_type="enemy",
            buff_scope="combat",
            source="CoA class tree: 'Temporal Dissonance - Chronostasis now "
                   "slows your target's movement speed by an additional "
                   "-10%'. Haste is the engine's real slow (turn_meter.py "
                   "reads it off status effects for turn order), so a slow "
                   "is a haste debuff."),
    ability("roll_back", "Roll Back", "dispel",
            "Return your ally to the version of themselves from a few "
            "seconds ago.",
            one(14, 25, 0), cooldown=3, target_type="ally",
            dispel_type=["magic", "poison", "disease"],
            source="CoA: 'Roll Back to cleanse harmful effects'. A broad "
                   "cleanse, so the full dispel_type tuple rather than one "
                   "school."),
    ability("discordance", "Discordance", "spell_damage",
            "Two moments arrive in the wrong order and everything standing "
            "between them pays for it.",
            ranks(48, 15, 45, start=16, count=6), cooldown=2,
            target_type="enemy_aoe", max_targets=3, damage_school="arcane",
            source="CoA: Discordance is the shared cleave - Infinite's "
                   "Timelost Power widens it, Artificer's Clocked In and "
                   "Caverns of Time bank fragments off it."),
    ability("waves_of_time", "Waves of Time", "spell_damage",
            "A cone of time fractals that arrives twice.",
            ranks(44, 14, 50, start=18, count=5), cooldown=4,
            target_type="enemy_aoe", max_targets=4, damage_school="arcane",
            source="CoA class tree: 'Blast enemies in a frontal cone with "
                   "time fractals, knocking them back slightly. The "
                   "knockback repeats 1 additional time after 2 sec.' There "
                   "is no knockback or displacement in a turn engine, so "
                   "this is the damage half only."),
    ability("time_out", "Time Out!", "buff",
            "Step out of the fight for a moment. The fight does not get a "
            "say.",
            one(20, 0), cooldown=10, duration=2,
            stat_mods={"damage_taken_pct": -0.3, "mp5": 20},
            target_type="self", buff_scope="combat",
            source="CoA class tree, and Time's personal emergency layer: "
                   "'Time Out! and your absorb stack are the emergency "
                   "layer'. The channelled mana regen is the mp5 half."),
    ability("clasp_of_infinity", "Clasp of Infinity", "debuff",
            "A binding that bounces from one enemy to the next and holds "
            "all of them.",
            one(22, 35), cooldown=6, duration=2,
            stat_mods={"haste": -40.0}, target_type="enemy_aoe",
            max_targets=3, buff_scope="combat",
            source="CoA class tree: 'Conjure a magical binding upon an "
                   "enemy that bounces to nearby enemies, rooting them in "
                   "place for 4 seconds.' The engine has one crowd-control "
                   "flag, is_stun, and no root - a bouncing root that still "
                   "lets the target act is a heavy slow here, not a stun."),
    ability("babify", "Babify", "debuff",
            "They are suddenly very small and very cross about it.",
            one(24, 40), cooldown=6, duration=2,
            target_type="enemy", is_stun=True, buff_scope="combat",
            source="CoA class tree: 'Instantly transform all enemies into a "
                   "baby, preventing them from acting ... damage dealt will "
                   "interrupt this effect.' is_stun is the engine's "
                   "incapacitate; the break-on-damage half has no hook, so "
                   "it runs the full two turns."),
    ability("fortify_timeline", "Fortify Timeline", "heal",
            "Shore up the timeline you are all standing in.",
            ranks(60, 20, 75, start=26, count=5), cooldown=5,
            target_type="party",
            source="CoA class tree: 'Fortify the current timeline, "
                   "instantly healing all allies and extending the duration "
                   "of Accelerated Recovery on them by 5 sec.' The extension "
                   "half needs a cast to reach into an existing status "
                   "effect's clock, which nothing supports, so this is the "
                   "instant group heal only."),
    ability("timeguard", "Timeguard", "buff",
            "A guard set on an ally a little ahead of them, where the next "
            "bad thing will arrive.",
            one(28, 50), cooldown=8, duration=3,
            stat_mods={"damage_taken_pct": -0.3}, absorb_pct_max_health=0.1,
            target_type="ally", buff_scope="combat",
            source="CoA class tree: 'causing the next 3 instances of direct "
                   "damage that would reduce the target below 35% health to "
                   "deal 40% less damage'. No health-gated charge system "
                   "exists, so it is a flat cut plus a real absorb for three "
                   "turns."),
    ability("hasten", "Hasten", "buff",
            "Your ally gets to where they were going before they decide to "
            "go there.",
            one(30, 45), cooldown=8, duration=3,
            stat_mods={"haste": 15.0}, target_type="ally",
            buff_scope="combat",
            source="CoA class tree, referenced by The Bieko Effect, Maker of "
                   "Realities and Unmaker of Realities; Artificer calls it "
                   "'Hasten to hand one ally haste and movement speed'."),
    ability("temporal_focus", "Temporal Focus", "buff",
            "You lock yourself into one perfect moment. Nothing reaches in "
            "to move you out of it.",
            one(32, 30), cooldown=12, duration=2,
            stat_mods={"cc_immune": 1}, target_type="self",
            buff_scope="combat",
            source="CoA class tree: 'removing and becoming immune to banish, "
                   "silence, and interrupt effects for 10 seconds'. cc_immune "
                   "is the engine's real immunity flag (checked in "
                   "StatusEffectMixin.apply_status_effect)."),
    ability("temporal_anomaly", "Temporal Anomaly", "buff",
            "Reality bends around you and gives back what it took.",
            one(36, 60), cooldown=12, duration=2,
            absorb_pct_max_health=0.3, target_type="self",
            buff_scope="combat",
            source="CoA class tree: 'causing 50% of the damage taken to be "
                   "absorbed and converted into healing at the end of the "
                   "duration'. An absorb shield is the absorb half; there is "
                   "no deferred release, so the shield simply holds."),
    ability("infinite_shield", "Infinite Shield", "buff",
            "Ten small refusals, handed to an ally one at a time.",
            one(40, 55), cooldown=6, duration=4,
            absorb_pct_max_health=0.18, target_type="ally",
            buff_scope="combat",
            source="CoA class tree: '10 charges ... Each time they take "
                   "damage, they will be healed and lose 1 charge.' Charges "
                   "do not exist; a four-turn absorb is the same trade."),
    ability("gravity_bomb", "Gravity Bomb", "spell_dot",
            "Put a weight on them that nothing nearby can stand far enough "
            "away from.",
            ranks(70, 24, 55, start=44, count=4), cooldown=8, duration=2,
            target_type="enemy_aoe", max_targets=5, damage_school="arcane",
            source="CoA class tree tier 2: 'After 6 seconds they explode for "
                   "Chromatic Damage in a 10 yds radius. Directly before the "
                   "explosion occurs, all enemies within 15 yds are "
                   "teleported to the initial target.' The delay and the "
                   "teleport-in have no hooks; a two-turn AoE DoT is the "
                   "detonation."),

    # ---- Infinite
    ability("chromatic_shard", "Chromatic Shard", "spell_damage",
            "A shard of raw disorder. There is nothing in it to resist.",
            ranks(66, 20, 46, start=10, count=8),
            target_type="enemy", damage_school="arcane",
            source="CoA: 'Your core spender is Chromatic Shard, a chaos bolt "
                   "that pierces immunities and resistances.' No ability "
                   "flag bypasses resistance - Monster.take_damage reduces by "
                   "school resistance unconditionally - but the ATTACKER's "
                   "spell_penetration is subtracted there, which is why the "
                   "Time Means Nothing talent grants it instead of a "
                   "vulnerability debuff. No cooldown: CoA has it getting "
                   "FASTER as Anomaly Spikes land ('reduces the cast time of "
                   "this ability by 10%, stacking 10 times') and the rotation "
                   "says to 'dump Chromatic Shard' through the burst window, "
                   "so Mana is what rations it, not a timer. It is the "
                   "class's second spammable nuke - the shared kit otherwise "
                   "has only Unmake, and a cloth caster with one filler loses "
                   "fights a Mage with Fireball and Frostbolt wins."),
    ability("melt_reality", "Melt Reality", "spell_dot",
            "The target's reality softens and starts to run.",
            ranks(112, 40, 45, start=12, count=7), cooldown=4, duration=4,
            target_type="enemy", damage_school="arcane",
            source="CoA: 'Melt the target's reality, dealing Chromatic "
                   "Damage every 3 sec for 30 seconds. While active, "
                   "periodic damage dealt to the target is replicated for "
                   "20% of the value to all enemies near them.' The "
                   "replication lives on the Shifting Chaos and Infinite "
                   "Keeper talents, which use the engine's splash_damage "
                   "proc payload."),
    ability("timerend", "Timerend", "spell_dot",
            "Tear the fabric and leave the tear open.",
            ranks(44, 15, 22, start=14, count=7), cooldown=2, duration=2,
            target_type="enemy", damage_school="arcane",
            source="CoA: 'Transforms your Wand of Time into Timerend. Rend "
                   "the fabric of time, dealing Chromatic Damage over 6 "
                   "seconds.' Authored as its own spell rather than a "
                   "transform - nothing in the engine replaces one ability "
                   "with another."),
    ability("anomaly_spike", "Anomaly Spike", "spell_damage",
            "Something comes loose and goes looking for the nearest target.",
            ranks(34, 10, 20, start=16, count=6), target_type="enemy",
            damage_school="arcane", requires_talent=True,
            source="CoA: 'Periodic damage dealt now has a chance to launch "
                   "an Anomaly Spike at your target.' A real second spell, "
                   "fired free by the Anomaly Spikes talent's cast_ability "
                   "proc, which is why it exists as an ability at all."),
    ability("destabilize_time", "Destabilize Time", "debuff",
            "Their sense of when to act stops agreeing with everyone "
            "else's.",
            one(26, 35), cooldown=5, duration=3,
            stat_mods={"haste": -20.0, "attack_power": -40},
            target_type="enemy", buff_scope="combat", requires_talent=True,
            source="CoA: 'Reduces enemy casting speed by -10% for 20 "
                   "seconds, increasing by -10% every time they cast.' The "
                   "escalation needs an on-enemy-cast hook; a flat slow plus "
                   "an attack-power cut is the static version. Monsters read "
                   "haste and attack_power off status effects and nothing "
                   "else, so those are the two levers that work on them."),
    ability("slipstream", "Slipstream", "debuff",
            "You put one of them somewhere else for a while.",
            one(34, 45), cooldown=10, duration=2,
            target_type="enemy", is_stun=True, buff_scope="combat",
            source="CoA: 'Target an enemy and slip them into a pocket "
                   "dimension for 5 seconds, banishing them and making them "
                   "immune to damage.' The damage immunity is not "
                   "expressible, so this is a two-turn incapacitate - which "
                   "is the part the rotation actually uses it for ('Use "
                   "Slipstream to remove a dangerous add from the fight')."),
    ability("infinite_horizon", "Infinite Horizon", "buff",
            "You widen everyone's view of what is about to happen.",
            one(44, 70), cooldown=12, duration=4,
            stat_mods={"damage_dealt_pct": 5}, target_type="party",
            buff_scope="combat",
            source="CoA: 'Increases the all damage dealt by party and raid "
                   "members by 3%', and 'Infinite Horizon giving the group a "
                   "flat damage buff is its one support note'. "
                   "damage_dealt_pct is the engine's buff-granted damage key "
                   "(read in Ability._damage_multiplier) and takes percentage "
                   "POINTS, unlike the talent keys."),
    ability("incarnation_of_chaos", "Incarnation of Chaos", "buff",
            "You stop being a person who uses chaos.",
            one(42, 60), cooldown=15, duration=3,
            stat_mods={"damage_dealt_pct": 15, "haste": 10.0},
            target_type="self", buff_scope="combat", requires_talent=True,
            source="CoA: 'Transform into an Incarnate of Chaos, instantly "
                   "resetting the cooldown of Chromatic Shard and causing "
                   "your next cast to not incur a cooldown. In addition, "
                   "your damage dealt is increased by 15% for 15 seconds.' "
                   "Only the damage window is on the ability - the resets "
                   "live on the Infinite Power and Aeon Rend talents, which "
                   "have a real reset_cooldown proc payload to use."),

    # ---- Time
    ability("epoch", "Epoch", "heal",
            "You find the version of them that was not hurt yet and bring "
            "it forward.",
            ranks(64, 30, 45, start=10, count=7), cooldown=1,
            target_type="ally",
            source="CoA: 'Core loop is Epoch (a heal that builds Sands of "
                   "Time stacks) and Accelerated Recovery (a HoT).' Sands of "
                   "Time cannot be a resource (see module docstring), so the "
                   "stack payoff is the Carbon Dating and Epic Recovery "
                   "talents raising Epoch's own healing."),
    ability("correct_the_mistake", "Correct the Mistake", "heal",
            "Whatever just happened to your party, you tell it differently.",
            ranks(76, 26, 100, start=22, count=5), cooldown=4,
            target_type="party",
            source="CoA: 'Retell the fate of party members within 30 yds, "
                   "healing them.' One of Time's two party-wide tools."),
    ability("ripple", "Ripple", "heal",
            "You hold the moment open and let it spread.",
            ranks(96, 32, 120, start=30, count=4), cooldown=6,
            target_type="party",
            source="CoA: 'Channel for up to 5 seconds ... allies within 40 "
                   "yds are healed based on the duration of the channel. "
                   "While channeling, you are immune to stun effects.' There "
                   "is no channel, so it resolves in one turn at full value "
                   "and the stun immunity is dropped - Temporal Focus is "
                   "where the class keeps that."),
    ability("aeon_of_resilience", "Aeon of Resilience", "buff",
            "You take the cheap, quick version of the trick, over and over.",
            one(10, 20), duration=60,
            stat_mods={"haste": 12.0, "mp5": 12},
            target_type="self", buff_scope="raid",
            exclusive_group="chronomancer_aeon",
            source="CoA's level-10 free passive: 'Reduces Epoch's cast time "
                   "by -25% and its mana cost by -10%, and healing done by "
                   "it now reduces the target's damage taken.' Frontier has "
                   "no free passives, so the first Aeon is learned from "
                   "level and the other three are talents. All four share "
                   "exclusive_group, which is the engine's real one-at-a-time "
                   "mechanic and exactly CoA's 'four Aeons that share a "
                   "cooldown'. duration 60 with buff_scope raid is the "
                   "loadout pattern Tinker's Rounds already use for a stance "
                   "that should survive between fights."),
    ability("aeon_of_protection", "Aeon of Protection", "buff",
            "Slower, heavier, and it leaves something behind to take the "
            "next hit.",
            one(18, 25), duration=60,
            stat_mods={"healing_done_pct": 12, "damage_taken_pct": -0.1},
            target_type="self", buff_scope="raid",
            exclusive_group="chronomancer_aeon", requires_talent=True,
            source="CoA: 'Increases Epoch's cast time by 15%, healing done "
                   "by 15%, and causes it to apply a damage absorption "
                   "shield equal to 30% of the amount healed.' A cast buff "
                   "cannot make ANOTHER spell apply a shield, so the absorb "
                   "half is the Orderly Protector talent's shield_pct proc "
                   "and this is the healing and mitigation half."),
    ability("aeon_of_renewal", "Aeon of Renewal", "buff",
            "Less now, more over the next while.",
            one(26, 25), duration=60,
            stat_mods={"healing_done_pct": 18, "haste": -6.0},
            target_type="self", buff_scope="raid",
            exclusive_group="chronomancer_aeon", requires_talent=True,
            source="CoA: 'Reduces Epoch's healing by -30%, but causes it to "
                   "heal for an additional 50% of the amount healed over 3 "
                   "seconds.' Trading burst for total output is the shape; "
                   "the engine cannot split one heal into a direct part and "
                   "a trailing HoT, so it is more healing at a slower pace."),
    ability("aeon_of_oblivion", "Aeon of Oblivion", "buff",
            "Expensive, loud, and it lands when it has to.",
            one(34, 35), duration=60,
            stat_mods={"crit_chance_spell": 12, "healing_done_pct": 10},
            target_type="self", buff_scope="raid",
            exclusive_group="chronomancer_aeon", requires_talent=True,
            source="CoA: 'Increases Epoch's mana cost by 30%, critical "
                   "strike chance by 10%, and healing done by 15%. In "
                   "addition, healing with Epoch now increases the target's "
                   "damage dealt by 3%.' The recipient buff needs a heal to "
                   "apply a buff to its target, which nothing supports."),
    ability("fabric_of_time", "Fabric of Time", "heal",
            "You reach past the injury to the weave behind it.",
            ranks(86, 30, 70, start=34, count=4), cooldown=4,
            target_type="ally", requires_talent=True,
            source="CoA: 'Alter the fabric of time, healing an ally. Your "
                   "next Aeon used within 8 seconds will trigger with no "
                   "cooldown or cost.' The free-Aeon rider is not "
                   "expressible from a heal; the Orderly Protector talent "
                   "carries the rest of this node's identity."),
    ability("buy_time", "Buy Time", "debuff",
            "Everything in that patch of ground stops, including the parts "
            "you would rather keep.",
            one(46, 65), cooldown=14, duration=2,
            target_type="enemy_aoe", max_targets=4, is_stun=True,
            buff_scope="combat",
            source="CoA: 'Put all enemies and allies in an 8 yd radius into "
                   "a stasis, banishing them for 6 seconds, making them "
                   "invulnerable to all effects but unable to move.' The "
                   "friendly-fire half (it freezes allies too) and the "
                   "invulnerability are not expressible, so this is an AoE "
                   "incapacitate on enemies - the use CoA's own rotation "
                   "gives it ('freeze the extra mobs with Buy Time so "
                   "they're locked out while you kill the first')."),
    ability("continuum_restoration", "Continuum Restoration", "dispel",
            "You restore the local continuum, and nothing anyone did to it "
            "stays done.",
            one(38, 45, 0), cooldown=6, target_type="ally",
            dispel_type="magic", dispel_count=2,
            source="CoA: 'Restore the continuum at target location for all "
                   "allies and enemies, removing all beneficial magic "
                   "effects from enemies and harmful magic effects from "
                   "allies. This dispel is potent enough to remove magic "
                   "effects that are normally undispellable.' A dispel reads "
                   "one target, so the enemy-purge half is gone; the "
                   "two-count is the 'potent' half."),
    ability("displacement", "Displacement", "dispel",
            "You pull them to where you are standing, and whatever was "
            "holding them is left behind.",
            one(30, 30, 0), cooldown=8, target_type="ally",
            dispel_type="magic",
            source="CoA: 'Displaces a party or raid member and pulls them to "
                   "you, dispelling root and snare effects from them.' There "
                   "are no root or snare dispel categories (DispelType is "
                   "magic/curse/poison/disease), and no repositioning, so "
                   "this is the cleanse."),

    # ---- Artificer
    ability("artificers_wand", "Artificer's Wand", "ranged_damage",
            "Two quick strikes with the wand, close enough together to "
            "count as one.",
            ranks(38, 11, 20, start=12, count=8), target_type="enemy",
            requires_talent=True,
            source="CoA: 'Transforms your Unmake into Artificer's Wand ... "
                   "unleash 2 wand attacks dealing Ranged Weapon damage. "
                   "Generates 1 Echo Fragment.' ranged_damage deliberately: "
                   "it scales off ranged_attack_power and the Ranged "
                   "weapon roll, so Wand Expert's Spirit conversion is a "
                   "real conversion rather than flavour. The trade is that "
                   "arcane_spell_damage does NOT touch the wand line, which "
                   "is why this tree's wand nodes use all_damage, "
                   "crit_chance_physical and per-ability keys instead."),
    ability("crystal_cannon", "Crystal Cannon", "ranged_damage",
            "The wand fires on its own, twice, and does not ask.",
            ranks(30, 9, 15, start=30, count=5), target_type="enemy",
            requires_talent=True,
            source="CoA: 'Casting Discordance now unleashes the Crystal "
                   "Cannon, launching 2 quick lesser Wand attacks at the "
                   "enemy over 1 seconds, scaling with Spirit.' Fired free "
                   "by the Crystal Cannon talent's cast_ability proc."),
    ability("shatter_echo", "Shatter Echo", "spell_damage",
            "You let go of everything you have been holding back at once.",
            ranks(90, 28, 75, start=22, count=6), cooldown=3,
            target_type="enemy", damage_school="arcane", requires_talent=True,
            source="CoA: 'Distortion Spell. Launch a distorted echo from "
                   "your wand at an enemy ... Damage increased by 40% for "
                   "each Echo Fragment consumed.' Fragments are not a "
                   "resource, so the spend is a cooldown and the Hyperwand "
                   "and Pulse Driver talents are the fragment scaling."),
    ability("singularity_core", "Singularity Core", "buff",
            "A point of compressed time sitting just off your wand hand.",
            one(28, 50), duration=60,
            stat_mods={"damage_dealt_pct": 10, "crit_chance_physical": 6},
            target_type="self", buff_scope="raid",
            exclusive_group="chronomancer_continuum", requires_talent=True,
            source="CoA: 'Continuum Spell. Empower your Wand attacks to deal "
                   "an additional 50% Ranged Weapon Damage ... Can only have "
                   "1 Continuum spell active at a time.' The one-at-a-time "
                   "rule is exclusive_group, the same mechanic the Aeons use. "
                   "The per-fragment duration extension is not expressible."),
    ability("flux_emitter", "Flux Emitter", "buff",
            "The wand's output spreads itself thinner and wider.",
            one(36, 50), duration=60,
            stat_mods={"damage_dealt_pct": 6, "haste": 8.0},
            target_type="self", buff_scope="raid",
            exclusive_group="chronomancer_continuum", requires_talent=True,
            source="CoA: 'Continuum Spell. Empower Wand attacks to affect up "
                   "to 2 additional nearby enemies ... Affected attacks deal "
                   "less damage per additional enemy hit.' A buff cannot "
                   "change another ability's target count, so the cleave "
                   "lives on Splitting Time's aoe_damage and this is the "
                   "throughput half - weaker per hit than Singularity Core, "
                   "matching the trade CoA describes."),
    ability("paradox_cannon", "Paradox Cannon", "restore_resource",
            "You spend a minute you have not had yet.",
            restore(44, 0, 25), cooldown=12, target_type="self",
            restore_resource_type="mana", requires_talent=True,
            source="CoA: 'Continuum Spell. Generate 1 Echo Fragment every 3 "
                   "sec for 5 seconds, plus an additional 5 sec per Echo "
                   "Fragment consumed.' A pure generator with nothing to "
                   "generate - Echo Fragments are not a resource - so it "
                   "banks the thing the rotation actually runs out of, and "
                   "'bank ahead with Paradox Cannon between pulls' still "
                   "reads true. Deliberately NOT in the Continuum "
                   "exclusive_group: restore_resource applies no status "
                   "effect, so it has nothing to be exclusive with."),
    ability("aether_compression", "Aether Compression", "enable_instant_cast",
            "Everything compresses, and the next thing you do takes no time "
            "at all.",
            one(50, 40, 0), cooldown=12, target_type="self", is_instant=True,
            source="CoA: 'Continuum Spell. Artificer's Wand and Reverse "
                   "Wound can be cast while moving for 5 seconds.' Nothing "
                   "moves in this engine, so the closest honest version of "
                   "'your cast stops costing you anything' is the instant-"
                   "cast enabler. Also outside the Continuum exclusive_group, "
                   "because enable_instant_cast does not apply a status "
                   "effect that a group could exclude."),
    ability("arc_collision", "Arc Collision", "spell_dot",
            "A small timestorm, with three of them standing in it.",
            ranks(62, 22, 48, start=48, count=4), cooldown=6, duration=3,
            target_type="enemy_aoe", max_targets=3, damage_school="arcane",
            source="CoA: 'Distortion Spell. Create a timestorm around an "
                   "enemy that causes them and up to 2 nearby enemies to "
                   "take Arcane damage, repeating over 4 seconds.' CoA is "
                   "blunt that it is 'a capped, undertuned timestorm rather "
                   "than a pack nuke - don't build around it', so it is "
                   "capped at 3 and carries no talent support."),
    ability("unstable_chronoglass", "Unstable Chronoglass", "debuff",
            "A pane of warped time, standing where the next spell was going "
            "to go.",
            one(32, 40), cooldown=10, duration=2,
            stat_mods={"hit_chance_spell": -60}, target_type="enemy",
            buff_scope="combat",
            source="CoA: 'Place an Unstable Chronoglass at target location "
                   "that will redirect the next 3 offensive enemy spell "
                   "casts onto itself.' Redirection needs a placed object "
                   "that can be targeted, and the pet system's templates all "
                   "carry their own display_name, so summoning one would put "
                   "'Sentry Turret' on screen. Implemented instead as the "
                   "outcome - the enemy's spells stop landing - the same way "
                   "mage_counterspell stands in for a real interrupt."),
    ability("collapse", "Collapse", "debuff",
            "The moment they are standing in gives way under them.",
            one(40, 45), cooldown=8, duration=2,
            target_type="enemy", is_stun=True, buff_scope="combat",
            source="CoA: 'Collapse sets up a delayed stun'. The delay has no "
                   "hook; the stun is real."),
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


def self_buff(effect_id, name, duration, stat_mods):
    """A proc payload that lands a buff on the CASTER, not the target."""
    return {"effect_id": f"chronomancer_{effect_id}", "name": name,
            "effect_type": "buff", "duration": duration,
            "stat_mods": stat_mods, "on_target": False}


def enemy_debuff(effect_id, name, duration, stat_mods):
    """A proc payload that lands a debuff on the TARGET.

    Only `armor` and `attack_power` do anything here. Monster.take_damage
    reads neither magic_damage_taken_pct nor any school vulnerability key off
    status effects - Character.take_damage does, Monster does not - so an
    enemy-vulnerability debuff is live against players and dead against every
    creature in the game. See the module docstring.
    """
    return {"effect_id": f"chronomancer_{effect_id}", "name": name,
            "effect_type": "debuff", "duration": duration,
            "stat_mods": stat_mods, "on_target": True}


# =============================================================== Infinite
F = "chronomancer_infinite"
INFINITE = tree(
    F, "Chronomancer Infinite",
    "Ranged chaos caster - rolling periodic damage drives Anomaly Spikes, "
    "stacking haste and cooldown resets, which cash out through the "
    "Incarnation of Chaos window.",
    [
        node(F, "warpstriker", "Warpstriker",
             "Reduces the Mana cost of your spells by 2% per rank.",
             0, 0, 5, {"all_ability_cost_pct": 0.02},
             source="CoA: 'Reduces the cost of your spells by -5% and the "
                    "chance for your spells to be dispelled by 10%.' Note "
                    "the SIGN: talented_cost does cost * (1 - pct), so a "
                    "POSITIVE value is the discount. Guardian's Seasoned "
                    "Fighter shipped -0.03 here and makes its abilities 3% "
                    "more expensive per rank."),
        node(F, "deconstruction", "Deconstruction",
             "Increases the critical strike chance of Unmake by 1% per rank.",
             0, 1, 5, {"ability_chronomancer_unmake_crit": 1.0},
             source="CoA: 'Increases the critical strike chance of Unmake by "
                    "5%.'"),
        node(F, "rippling_power", "Rippling Power",
             "Increases your Spirit by 2% per rank.",
             0, 2, 5, {"spirit_pct": 2.0},
             source="CoA class tree: 'Increases your Spirit by 8%.' Spirit "
                    "is the listed primary stat for all three specs, which is "
                    "unusual for a cloth caster and is why this tree, like "
                    "the other two, opens on it."),
        node(F, "impeccable_timing", "Impeccable Timing",
             "Increases the damage of your periodic effects by 4% per rank.",
             0, 3, 3, {"dot_damage": 0.04},
             source="CoA class tree: 'Your periodic damage and healing "
                    "effects can now critically strike.' There is no "
                    "can-DoTs-crit switch (DoT ticks never roll a crit in "
                    "combat/status_effects.py), so the node buys the same "
                    "thing the switch would: more damage out of the ticks."),

        node(F, "anomaly_spikes", "Anomaly Spikes",
             "Your damaging spells have a 12% chance to launch an Anomaly "
             "Spike at your target.",
             1, 0, 3, {"unlock_ability": "chronomancer_anomaly_spike"},
             connect=["warpstriker"],
             proc={"trigger": "on_damage_cast", "chance": 12, "icd": 1,
                   "cast_ability": "chronomancer_anomaly_spike"},
             source="CoA: 'Periodic damage dealt now has a 8% chance to "
                    "launch an Anomaly Spike at your target.' The real "
                    "mechanic, via the engine's cast_ability proc payload - "
                    "it fires the spell free (Ability.use(free=True)). It "
                    "triggers off DAMAGING CASTS rather than off DoT ticks, "
                    "because on_damage_cast is a trigger the engine "
                    "dispatches and a per-tick trigger is not."),
        node(F, "mind_melt", "Mind Melt",
             "Your damaging spells weaken the target's attacks for 3 turns.",
             1, 1, 3, {}, connect=["deconstruction"],
             proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
                   "apply_effect": enemy_debuff(
                       "mind_melt", "Mind Melt", 3, {"attack_power": -25})},
             source="CoA: 'Damage dealt by Melt Reality now also reduces the "
                    "target's primary attributes by -3%, stacking 5 times.' "
                    "Attack power is the only outgoing-damage stat a Monster "
                    "reads off a status effect, so the attribute shred is "
                    "that; stacking is not available to a proc payload."),
        node(F, "gift_of_the_infinite_dragonflight",
             "Gift of the Infinite Dragonflight",
             "Grants spell damage equal to 4% of your Spirit, and 1 spell hit "
             "rating, per rank.",
             1, 2, 5, {"spell_damage_from_spirit_pct": 0.04, "hit_rating": 1},
             connect=["rippling_power"],
             source="CoA's level-20 free passive: 'Increases your spell "
                    "damage by 40% of your Spirit and your spell hit rating "
                    "by 3% of your Spirit.' A real "
                    "<target>_from_<source>_pct conversion, resolved against "
                    "the shared STAT_CONVERSION maps in character.py. The "
                    "hit half cannot be a conversion - hit_rating is a local "
                    "feeding base_miss_chance_*, not a Character attribute - "
                    "so it is flat, the same compromise Guardian's Bulwark "
                    "made."),
        node(F, "distorted_time", "Distorted Time",
             "Reduces the cooldown of Timerend by 1 turn and increases the "
             "duration of Decomposition by 1 turn, per rank.",
             1, 3, 3, {"ability_chronomancer_timerend_cooldown": 1,
                       "ability_chronomancer_decomposition_duration": 1},
             connect=["impeccable_timing"],
             source="CoA: 'Reduces the cooldown of Timerend by -2 sec and "
                    "increases the duration of Decomposition by 3 sec.' "
                    "ability_<id>_<stat> keys are built by interpolation in "
                    "abilities.py, which is why a literal grep calls them "
                    "dead."),

        node(F, "hourglass_of_eternity", "Hourglass of Eternity",
             "Your damaging spells have a 10% chance to grant you 10 haste "
             "for 2 turns.",
             2, 0, 3, {}, connect=["anomaly_spikes"],
             proc={"trigger": "on_damage_cast", "chance": 10, "icd": 2,
                   "apply_effect": self_buff(
                       "hourglass", "Hourglass of Eternity", 2,
                       {"haste": 10.0})},
             source="CoA: 'Periodic damage dealt now has a 5% chance to grant "
                    "you 25% increased haste for 5 seconds.' Same per-tick "
                    "to per-cast move as Anomaly Spikes, same reason."),
        node(F, "magic_erosion", "Magic Erosion",
             "Increases your Arcane spell damage by 2% and grants 1 spell hit "
             "rating per rank.",
             2, 1, 3, {"arcane_spell_damage": 0.02, "hit_rating": 1},
             connect=["mind_melt"],
             source="CoA: 'Your Decomposition now applies Magic Erosion to "
                    "the target, increasing attackers chance to hit the "
                    "target with spells by 3%.' A hit-taken debuff has no "
                    "reader on Monster, so the node grants the caster the "
                    "hit instead - the same outcome for the Chronomancer, "
                    "and honest about who it applies to."),
        node(F, "crown_of_power", "Crown of Power",
             "Increases the damage of Melt Reality by 5% per rank.",
             2, 2, 5, {"ability_chronomancer_melt_reality_damage": 0.05},
             connect=["gift_of_the_infinite_dragonflight"],
             source="CoA: 'Increases the tick rate of Melt Reality by -25%.' "
                    "A DoT's effect_value is its TOTAL across the duration "
                    "here, so a faster tick rate and more damage are the same "
                    "number."),
        node(F, "shifting_chaos", "Shifting Chaos",
             "Your damaging spells spill a tenth of their damage onto up to 3 "
             "other enemies.",
             2, 3, 3, {}, connect=["distorted_time"],
             proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
                   "splash_damage": {"pct": 0.1, "max_targets": 3}},
             source="CoA: 'Your Chromatic Shard and Anomaly Spikes now deal "
                    "an additional 20% their damage dealt as Chromatic Damage "
                    "all nearby enemies', and Melt Reality's own 'periodic "
                    "damage dealt to the target is replicated for 20% of the "
                    "value to all enemies near them'. splash_damage is the "
                    "engine's real version of exactly this."),

        node(F, "black_hole", "Black Hole",
             "Increases the damage of Chromatic Shard and Unmake by 4% per "
             "rank.",
             3, 0, 3, {"ability_chronomancer_chromatic_shard_damage": 0.04,
                       "ability_chronomancer_unmake_damage": 0.04},
             connect=["hourglass_of_eternity"],
             source="CoA: 'Increases the damage of Chromatic Shard, Melt "
                    "Reality and Unmake by 15% against slowed enemies.' "
                    "Nothing can read 'is the target slowed' at damage time, "
                    "so the condition is dropped and the bonus is smaller to "
                    "pay for always being on. Melt Reality is left out "
                    "because Crown of Power already carries it."),
        node(F, "destabilize_time", "Destabilize Time",
             "Teaches Destabilize Time, which slows an enemy's actions and "
             "weakens its attacks.",
             3, 1, 1, {"unlock_ability": "chronomancer_destabilize_time"},
             node_type="active", connect=["magic_erosion"],
             source="CoA lists Destabilize Time as a spec talent, and the "
                    "strengths section leans on it: 'Time Means Nothing and "
                    "Destabilize Time amplify and slow the focus target.'"),
        node(F, "infinite_power", "Infinite Power",
             "Your damaging spells have a 25% chance to pull your damaging "
             "cooldowns forward by 1 turn.",
             3, 2, 3, {}, connect=["crown_of_power"],
             proc={"trigger": "on_damage_cast", "chance": 25, "icd": 1,
                   "reset_cooldown": {
                       "abilities": ["chronomancer_chromatic_shard",
                                     "chronomancer_discordance",
                                     "chronomancer_gravity_bomb",
                                     "chronomancer_melt_reality"],
                       "turns": 1}},
             source="CoA's level-10 free passive: 'Casting damaging spells "
                    "now reduces your damaging spell cooldowns by 10% of "
                    "their remaining cooldown', and the rotation note "
                    "'Infinite Power quietly pulls your cooldowns forward the "
                    "more you cast, so never stop pressing damage'. The "
                    "reset_cooldown proc payload takes a list of ability ids "
                    "and a turn count, so this is the real mechanic rather "
                    "than an approximation - percentage-of-remaining becomes "
                    "a flat turn, which is the only granularity a turn engine "
                    "has."),
        node(F, "timelost_power", "Timelost Power",
             "Increases the damage your area spells deal by 5% per rank.",
             3, 3, 4, {"aoe_damage": 0.05}, connect=["shifting_chaos"],
             source="CoA: 'Your Discordance now strikes 3 additional "
                    "enemies.' An ability's max_targets is fixed at load "
                    "time and no talent key changes it, so a wider cleave "
                    "becomes a harder one."),

        node(F, "incarnation_of_chaos", "Incarnation of Chaos",
             "Teaches Incarnation of Chaos, a burst window that raises all "
             "your damage.",
             4, 0, 1, {"unlock_ability": "chronomancer_incarnation_of_chaos"},
             node_type="active", connect=["black_hole"], total_slots=3,
             source="CoA: 'Burst hinges on Incarnation of Chaos.' The "
                    "spec's one real cooldown, and the thing its whole proc "
                    "engine is ramping toward."),
        node(F, "infinity_crash", "Infinity Crash",
             "Increases the damage of your spell critical strikes by 5% per "
             "rank.",
             4, 1, 3, {"crit_damage_spell": 0.05},
             connect=["destabilize_time"], total_slots=3,
             source="CoA: 'Increases the critical damage of Discordance and "
                    "Chromatic Shard by 50%.' There is no per-ability crit "
                    "damage key, so it is the spec's spell crit damage."),
        node(F, "time_means_nothing", "Time Means Nothing",
             "Grants 6 spell penetration per rank.",
             4, 2, 4, {"spell_penetration": 6}, connect=["infinite_power"],
             total_slots=3,
             source="CoA: 'Damage dealt by Chromatic Shard now increases the "
                    "target's spell damage taken by 10%.' A damage-taken "
                    "debuff is inert against creatures (see the module "
                    "docstring), but the ATTACKER's spell_penetration is "
                    "subtracted from a target's resistance inside both "
                    "Monster.take_damage and Character.take_damage, and it is "
                    "a real talent bonus key (character.py reads "
                    "bonuses['spell_penetration']). So this is the node that "
                    "actually delivers Chromatic Shard's 'pierces immunities "
                    "and resistances'."),

        node(F, "chaotic_time", "Chaotic Time",
             "Increases the damage of Melt Reality by 8% per rank.",
             5, 0, 2, {"ability_chronomancer_melt_reality_damage": 0.08},
             connect=["incarnation_of_chaos"], total_slots=3,
             source="CoA: 'While Incarnation of Chaos is active, your Melt "
                    "Reality deals 30% increased damage and replicates an "
                    "additional 20%.' The during-Incarnation condition has no "
                    "reader, so the bonus is unconditional and smaller."),
        node(F, "aeon_rend", "Aeon Rend",
             "Your damaging spells have a 20% chance to reset Chromatic "
             "Shard.",
             5, 1, 2, {}, connect=["infinity_crash"], total_slots=3,
             proc={"trigger": "on_damage_cast", "chance": 20, "icd": 1,
                   "reset_cooldown": "chronomancer_chromatic_shard"},
             source="CoA: 'Your Chromatic Shard now has a 25% chance to "
                    "strike again and incur no cooldown.' A full reset is "
                    "the closest thing to a free extra cast, and "
                    "reset_cooldown with no turn count is exactly that."),
        node(F, "null_orbs", "Null Orbs",
             "Increases your spell critical strike chance by 1% and the "
             "damage of your spell critical strikes by 6% per rank.",
             5, 2, 2, {"crit_chance_spell": 1.0, "crit_damage_spell": 0.06},
             connect=["time_means_nothing"], total_slots=3,
             source="CoA: 'Periodic critical damage dealt now has a 20% "
                    "chance to grant Null Orbs ... Increases the critical "
                    "damage of Chromatic Shard and Anomaly Spikes based on "
                    "your spell critical strike rating.' A proc that scales "
                    "off a rating it also grants is not expressible; the two "
                    "stats it is made of are."),

        node(F, "infinite_keeper", "Infinite Keeper",
             "Your periodic damage erupts, spilling a third of every damaging "
             "spell onto everything standing near it.",
             6, 0, 1, {"arcane_spell_damage": 0.06, "dot_damage": 0.1},
             node_type="active",
             connect=["chaotic_time", "aeon_rend", "null_orbs"],
             total_slots=1,
             proc={"trigger": "on_damage_cast", "chance": 100, "icd": 3,
                   "splash_damage": {"pct": 0.35, "max_targets": 5}},
             source="Capstone. CoA: 'Using Unmake on an enemy affected by "
                    "your Timerend now causes the enemy to erupt in a vortex "
                    "of sand, dealing Chromatic Damage every 1 sec to up to 8 "
                    "enemies for 6 seconds.' The two-spell combination gate "
                    "cannot be read, so it is a periodic splash on a 3-turn "
                    "internal cooldown - the vortex, without the setup."),
    ],
    "Built from reference/coa_sidekick/SPEC_chronomancer__infinite.txt: "
    "'Closest to an Affliction/Destruction Warlock hybrid rendered in "
    "chaos-and-time flavor.' The tree is shaped by that spec's own loop - "
    "'Most of the work is sequencing your DoTs so Anomaly Spikes and the "
    "haste and cooldown procs are always rolling, then cashing that into the "
    "Incarnation of Chaos window' - so five of its twenty-three nodes are "
    "procs rather than flat stats, which is high for this codebase and "
    "deliberate. Stat priority is Spell Hit > Spell Power > Intellect > Crit "
    "> Spirit > Haste, and Spirit appears as high as it does because Gift of "
    "the Infinite Dragonflight converts it into both of the top two.")


# =================================================================== Time
T = "chronomancer_time"
TIME = tree(
    T, "Chronomancer Time",
    "Healer - Epoch and Accelerated Recovery are the loop, whichever of the "
    "four Aeons is loaded decides what Epoch does, and a stack of absorbs "
    "covers the gaps.",
    [
        node(T, "time_wizard", "Time Wizard",
             "Increases your spell critical strike chance by 1% per rank.",
             0, 0, 5, {"crit_chance_spell": 1.0},
             source="CoA: 'Increases the critical strike chance of your "
                    "Reverse Wound, Epoch, and Correct the Mistake by 8%.' "
                    "Those are three of the spec's four heals, so it is the "
                    "spec's crit node."),
        node(T, "sands_of_life", "Sands of Life",
             "Grants healing power equal to 3% of your Spirit per rank.",
             0, 1, 5, {"healing_power_from_spirit_pct": 0.03},
             source="CoA: 'Increases your healing power by 25% of your "
                    "Spirit.' A real conversion, and the reason this spec's "
                    "stat priority opens on Spirit."),
        node(T, "keep_accelerating", "Keep Accelerating",
             "Increases the healing of Accelerated Recovery by 5% per rank.",
             0, 2, 3,
             {"ability_chronomancer_accelerated_recovery_healing": 0.05},
             source="CoA: 'Your Accelerated Recovery now applies to an "
                    "additional nearby target.' A HoT's recipients come from "
                    "its target_type, which no talent key changes, so the "
                    "second target becomes a stronger first one."),
        node(T, "endless_sands", "Endless Sands",
             "Reduces the Mana cost of your healing spells by 2% per rank.",
             0, 3, 5, {"heal_cost_pct": 0.02},
             source="CoA: 'Cast time of your next Reverse Wounds within 15 "
                    "seconds is reduced by -20%, stacking up to 5 times.' No "
                    "cast times; a cast-time discount on a heal is a Mana "
                    "discount on a heal. Positive is the reduction here, same "
                    "sign convention as all_ability_cost_pct."),

        node(T, "aeon_of_protection", "Aeon of Protection",
             "Teaches Aeon of Protection, which makes your healing heavier "
             "and you harder to hurt.",
             1, 0, 1, {"unlock_ability": "chronomancer_aeon_of_protection"},
             node_type="active", connect=["time_wizard"],
             source="CoA's level-15 passive. The four Aeons share one "
                    "exclusive_group on the ability side, which is CoA's "
                    "'four Aeons that share a cooldown' - see the ability's "
                    "own _source."),
        node(T, "carbon_dating", "Carbon Dating",
             "Increases the healing of Epoch by 4% per rank.",
             1, 1, 5, {"ability_chronomancer_epoch_healing": 0.04},
             connect=["sands_of_life"],
             source="CoA: 'Each stack of Sands of Time now also increases the "
                    "healing of your Epoch by 10%.' Sands of Time is not a "
                    "resource this class can have (see the module "
                    "docstring), so the stack payoff is spent as talent "
                    "points instead of built in the fight."),
        node(T, "through_the_aeons", "Through The Aeons",
             "Grants 4 mana per 5 seconds per rank.",
             1, 2, 5, {"mp5": 4}, connect=["keep_accelerating"],
             source="CoA: 'Activating an Aeon now increases your mana "
                    "regeneration from Spirit by 100% for 8 seconds.' A "
                    "window keyed to activating an Aeon has no trigger; the "
                    "regen is flat and always on."),
        node(T, "timeless", "Timeless",
             "Reduces the Mana cost of your abilities by 2% per rank.",
             1, 3, 3, {"all_ability_cost_pct": 0.02},
             connect=["endless_sands"],
             source="CoA: 'While Endless Sands is active, the mana costs of "
                    "your spells and abilities is reduced by -3% per stack.' "
                    "CoA is explicit that mana is this spec's real limit - "
                    "'Every strong tool sits on a cooldown and costs mana' - "
                    "so the tree carries two cost nodes and an mp5 node."),

        node(T, "aeon_of_renewal", "Aeon of Renewal",
             "Teaches Aeon of Renewal, which trades pace for total healing "
             "done.",
             2, 0, 1, {"unlock_ability": "chronomancer_aeon_of_renewal"},
             node_type="active", connect=["aeon_of_protection"],
             source="CoA's level-30 passive, 'for sustained HoT-heavy "
                    "phases'."),
        node(T, "shimmering_shard", "Shimmering Shard",
             "Increases your healing done by 3% per rank.",
             2, 1, 5, {"healing_done": 0.03}, connect=["carbon_dating"],
             source="CoA: 'Activating Aeon spells now grants you 4% increased "
                    "damage and healing for 20 seconds, stacking 3 times.' "
                    "The stacking window needs an on-Aeon trigger; the "
                    "healing it grants does not."),
        node(T, "wonders_of_time", "Wonders of Time",
             "Increases your haste by 1 per rank.",
             2, 2, 3, {"haste": 1.0}, connect=["through_the_aeons"],
             source="CoA: 'Increases the spell haste of all party and raid "
                    "members by 3%.' A talent effect only ever lands on the "
                    "character who spent the point - there is no party-facing "
                    "talent pool - so the aura is the Chronomancer's own "
                    "haste."),
        node(T, "cadence_of_time", "Cadence of Time",
             "Increases the healing of Ripple by 4% per rank.",
             2, 3, 5, {"ability_chronomancer_ripple_healing": 0.04},
             connect=["timeless"],
             source="CoA: 'Your critical strikes with Epoch now grant Cadence "
                    "of Time, increasing the healing of Ripple by 10%. Stacks "
                    "5 times.'"),

        node(T, "aeon_of_oblivion", "Aeon of Oblivion",
             "Teaches Aeon of Oblivion, the expensive one that lands when it "
             "has to.",
             3, 0, 1, {"unlock_ability": "chronomancer_aeon_of_oblivion"},
             node_type="active", connect=["aeon_of_renewal"],
             source="CoA's level-40 passive - the burst Aeon."),
        node(T, "fabric_of_time", "Fabric of Time",
             "Teaches Fabric of Time, a fast heal that reaches past the "
             "injury.",
             3, 1, 1, {"unlock_ability": "chronomancer_fabric_of_time"},
             node_type="active", connect=["shimmering_shard"],
             source="CoA: 'Fabric of Time lets your next Aeon fire free of "
                    "cost or cooldown.' The free-Aeon half has no hook; the "
                    "heal is real."),
        node(T, "mark_of_order", "Mark of Order",
             "Increases the healing of Reverse Wound by 4% per rank.",
             3, 2, 5,
             {"ability_chronomancer_reverse_wound_healing": 0.04},
             connect=["wonders_of_time"],
             source="CoA: 'Healing done by Fortify Timeline now applies Mark "
                    "of Order. Increases the healing of your next Reverse "
                    "Wound on the target by 10%.' A heal cannot mark its "
                    "recipient for a later heal, so the bonus is "
                    "unconditional."),
        node(T, "timeline_tether", "Timeline Tether",
             "Your casts pull Fortify Timeline forward by 1 turn.",
             3, 3, 4, {}, connect=["cadence_of_time"],
             proc={"trigger": "on_damage_or_heal_cast", "chance": 100,
                   "icd": 1,
                   "reset_cooldown": {
                       "ability": "chronomancer_fortify_timeline",
                       "turns": 1}},
             source="CoA: 'Your periodic damage and healing reduces the "
                    "cooldown of your Fortify Timeline by -1 sec.' The real "
                    "mechanic - on_damage_or_heal_cast is a trigger the "
                    "engine dispatches, and reset_cooldown takes a turn "
                    "count."),

        node(T, "orderly_protector", "Orderly Protector",
             "Your heals have a 30% chance to leave a quarter of the healing "
             "behind as a shield.",
             4, 0, 3, {}, connect=["aeon_of_oblivion"], total_slots=3,
             proc={"trigger": "on_heal_cast", "chance": 30, "icd": 1,
                   "shield_pct": {"pct": 0.25, "duration": 2,
                                  "name": "Orderly Protector"}},
             source="CoA: 'Healing done by your Epoch now increases the "
                    "healing of Fabric of Time by 10%, stacking 10 times. "
                    "Each stack gives you a 2% chance when you cast Fabric of "
                    "Time to reset its own cooldown.' That chain is not "
                    "expressible, so this node carries the absorb Aeon of "
                    "Protection could not: 'causes it to apply a damage "
                    "absorption shield equal to 30% of the amount healed', "
                    "via the shield_pct proc payload."),
        node(T, "overcorrection", "Overcorrection",
             "Your heals spill a fifth of their value onto up to 3 other "
             "allies.",
             4, 1, 3, {}, connect=["fabric_of_time"], total_slots=3,
             proc={"trigger": "on_heal_cast", "chance": 100, "icd": 2,
                   "splash_heal": {"pct": 0.2, "max_targets": 3}},
             source="CoA: 'Overhealing done by Correct the Mistake now "
                    "applies a heal over time effect to the ally equal to 30% "
                    "of the healing done.' Overhealing is not tracked, so the "
                    "spill goes to the allies who can use it."),
        node(T, "time_skip", "Time Skip",
             "Reduces the cooldown of Roll Back by 1 turn and the duration of "
             "stuns against you by 10% per rank.",
             4, 2, 2, {"ability_chronomancer_roll_back_cooldown": 1,
                       "stun_duration_reduction_pct": 0.1},
             connect=["mark_of_order"], total_slots=3,
             source="CoA: 'Your Roll Back now removes 1 additional harmful "
                    "effect.' dispel_count is fixed on the ability, so a more "
                    "frequent cleanse replaces a bigger one. The stun "
                    "resistance is CoA's listed weakness answered directly: "
                    "'a chain-stun or silence landing while your cooldowns "
                    "are down kills you'."),

        node(T, "shield_of_the_ages", "Shield of the Ages",
             "When you are hit, you have a 35% chance to take 6% less damage "
             "and receive 8% more healing for 2 turns, per rank.",
             5, 0, 2, {}, connect=["orderly_protector"], total_slots=3,
             proc={"trigger": "on_damage_taken", "chance": 35, "icd": 1,
                   "apply_effect": self_buff(
                       "shield_of_the_ages", "Shield of the Ages", 2,
                       {"damage_taken_pct": -0.06, "healing_taken_pct": 8})},
             source="CoA: 'When hit by a damaging critical strike, your "
                    "damage taken is reduced by -3%, and healing received is "
                    "increased by 5% for 3 seconds, stacking 3 times.' "
                    "on_crit fires on the CASTER's crits, not on being crit, "
                    "so the trigger is on_damage_taken with a chance standing "
                    "in for 'only on crits'. Note the two units: "
                    "damage_taken_pct is read RAW off a status effect and so "
                    "is a fraction, while healing_taken_pct is divided by 100 "
                    "and so is points - in the same dict."),
        node(T, "converge_the_infinite", "Converge the Infinite",
             "Increases the healing of Correct the Mistake by 10% and your "
             "spell critical strike chance by 1% per rank.",
             5, 1, 2,
             {"ability_chronomancer_correct_the_mistake_healing": 0.1,
              "crit_chance_spell": 1.0},
             connect=["overcorrection"], total_slots=3,
             source="CoA: 'Your next Correct the Mistake has a 1 sec "
                    "increased cast time, but heals for 30% more and is "
                    "guaranteed to critically strike.'"),
        node(T, "epic_recovery", "Epic Recovery",
             "Increases the healing of Epoch by 6% per rank.",
             5, 2, 2, {"ability_chronomancer_epoch_healing": 0.06},
             connect=["time_skip"], total_slots=3,
             source="CoA: 'When you cast Epoch you now also cast a Rank 1 "
                    "Epoch on up to 5 allies affected by Accelerated "
                    "Recovery.' A heal cannot cast a second heal at a "
                    "different rank, so the spec's core heal just gets "
                    "bigger."),

        node(T, "the_vast_infinite", "The Vast Infinite",
             "You take 8% less damage, heal 8% harder, and every blow that "
             "lands on you returns as healing to whoever needs it most.",
             6, 0, 1, {"damage_taken_pct": -0.08, "healing_done": 0.08},
             node_type="active",
             connect=["shield_of_the_ages", "converge_the_infinite",
                      "epic_recovery"],
             total_slots=1,
             proc={"trigger": "on_damage_taken", "chance": 100, "icd": 1,
                   "leech_pct": {"pct": 0.3, "smart": True}},
             source="Capstone. CoA: 'All party and raid members become one, "
                    "equally sharing 25% of all damage dealt to them ... At "
                    "the end of the duration, all affected allies are healed "
                    "equal to the total damage shared.' Damage cannot be "
                    "redirected between combatants, but leech_pct with "
                    "smart:true converts a share of the damage the "
                    "Chronomancer takes into healing on the worst-off ally, "
                    "which is the store-the-damage-release-the-heal shape "
                    "CoA calls the spec's signature. It is a passive rather "
                    "than the 10-second cooldown window."),
    ],
    "Built from reference/coa_sidekick/SPEC_chronomancer__time.txt: 'Closest "
    "to Preservation Evoker ... the four Aeons function like choosing between "
    "burst, mitigation and HoT modes on one cooldown.' That is the spec's one "
    "real idea and the tree spends three of its four ability unlocks on it, "
    "with the fourth Aeon learned from level so a fresh healer always has "
    "one. Stat priority is Spirit > Spell Power > Haste > Intellect > Crit > "
    "MP5, which is why Sands of Life converts Spirit into healing power and "
    "why mana cost shows up three times.")


# ============================================================== Artificer
A = "chronomancer_artificer"
ARTIFICER = tree(
    A, "Chronomancer Artificer",
    "Wand builder/spender - wand attacks run off Spirit through ranged attack "
    "power, Distortion spells are the payoff, and only one Continuum can be "
    "active at a time.",
    [
        node(A, "artificers_empowerment", "Artificer's Empowerment",
             "Increases your Spirit by 2% per rank.",
             0, 0, 5, {"spirit_pct": 2.0},
             source="CoA: 'Increases your Spirit by 8%', 3 ranks. With Wand "
                    "Expert below, this is the whole gearing story: "
                    "'Artificer's Empowerment raises Spirit and Wand Expert "
                    "converts part of it into ranged attack power. Nearly the "
                    "whole kit runs off one stat.'"),
        node(A, "wand_master", "Wand Master",
             "Increases the damage of Wand of Time and Artificer's Wand by 4% "
             "per rank.",
             0, 1, 5, {"ability_chronomancer_wand_of_time_damage": 0.04,
                       "ability_chronomancer_artificers_wand_damage": 0.04},
             source="CoA: 'Increases the damage of Wand of Time and "
                    "Artificer's Wand by 10%.'"),
        node(A, "discovery", "Discovery",
             "Your damaging casts have a 30% chance to grant you 5 haste and "
             "2% physical critical strike chance for 3 turns.",
             0, 2, 3, {},
             proc={"trigger": "on_damage_cast", "chance": 30, "icd": 1,
                   "apply_effect": self_buff(
                       "discovery", "Discovery", 3,
                       {"haste": 5.0, "crit_chance_physical": 2})},
             source="CoA: 'Casting Artificer's Wand and Wand of Time now "
                    "grants Discovery for 30 seconds, stacking 4 times. At 3 "
                    "stacks, your next Wand of Time or Artificer's Wand "
                    "causes an additional Arcane hit.' A proc payload cannot "
                    "stack or count to a threshold, so the stack build is a "
                    "flat window. crit_chance_physical, not spell - the wand "
                    "line rolls its crits off hit_chance_physical and "
                    "crit_chance_physical, because ranged_damage is resolved "
                    "as physical in Ability._roll_crit."),
        node(A, "concentrated_fate", "Concentrated Fate",
             "Increases all damage you deal by 2% per rank.",
             0, 3, 5, {"all_damage": 0.02},
             source="CoA: 'Increases the effectiveness of your Echo Fragments "
                    "by 20%.' Echo Fragments are not a resource (see the "
                    "module docstring), and every spell in the spec is either "
                    "a fragment generator or a fragment spender, so the "
                    "honest reading of 'all your fragments are worth more' is "
                    "all your damage. all_damage also happens to be the only "
                    "key that covers BOTH halves of this spec - "
                    "arcane_spell_damage misses the wand line entirely."),

        node(A, "artificers_wand", "Artificer's Wand",
             "Teaches Artificer's Wand, two quick wand strikes with no "
             "cooldown.",
             1, 0, 1, {"unlock_ability": "chronomancer_artificers_wand"},
             node_type="active", connect=["artificers_empowerment"],
             source="CoA: 'Artificer's Wand is your filler and main Echo "
                    "Fragment generator.' The spec does not work without it, "
                    "so it is the first unlock."),
        node(A, "wand_expert", "Wand Expert",
             "Grants ranged attack power equal to 5% of your Spirit per rank.",
             1, 1, 5, {"ranged_ap_from_spirit_pct": 0.05},
             connect=["wand_master"],
             source="CoA's level-20 free passive: 'Increases your ranged "
                    "attack power by 100% of your Spirit.' A real conversion "
                    "against the shared STAT_CONVERSION maps, and the reason "
                    "the wand line is authored as ranged_damage - this is "
                    "what feeds it. 25% at 5/5 rather than CoA's 100%, "
                    "because this engine's ranged attack power is a much "
                    "larger multiplier on a wand roll than CoA's is."),
        node(A, "bronze_echoes", "Bronze Echoes",
             "Reduces the Mana cost of Artificer's Wand by 3% per rank.",
             1, 2, 5,
             {"ability_chronomancer_artificers_wand_cost_pct": 0.03},
             connect=["discovery"],
             source="CoA: 'Reduces the cast time of Artificer's Wand by -0.2 "
                    "sec.' No cast times; a filler you press constantly is "
                    "gated by its cost instead. Positive is the reduction."),
        node(A, "caverns_of_time", "Caverns of Time",
             "Increases the damage of Discordance by 5% per rank.",
             1, 3, 3,
             {"ability_chronomancer_discordance_damage": 0.05},
             connect=["concentrated_fate"],
             source="CoA: 'Your Discordance now generates 1 Echo Fragment', "
                    "and Discordance is pressed on cooldown in both of this "
                    "spec's rotations."),

        node(A, "singularity_core", "Singularity Core",
             "Teaches Singularity Core, the single-target Continuum.",
             2, 0, 1, {"unlock_ability": "chronomancer_singularity_core"},
             node_type="active", connect=["artificers_wand"],
             source="CoA: 'keep Singularity Core and Decomposition up' on a "
                    "boss. The default Continuum."),
        node(A, "shatter_echo", "Shatter Echo",
             "Teaches Shatter Echo, the spec's burst spender.",
             2, 1, 1, {"unlock_ability": "chronomancer_shatter_echo"},
             node_type="active", connect=["wand_expert"],
             source="CoA: 'Spend banked fragments on Shatter Echo, your main "
                    "burst spender.'"),
        node(A, "elder_wand", "Elder Wand",
             "Increases your physical critical strike chance by 1% per rank.",
             2, 2, 5, {"crit_chance_physical": 1.0},
             connect=["bronze_echoes"],
             source="CoA: 'Your Wand attacks now have a 30% chance to "
                    "increase the damage of Artificer's Wand against the "
                    "target by 3%, stacking 10 times.' A ten-stack ramp on "
                    "one target is not expressible; crit on the wand line is, "
                    "and Critical Strike is third in this spec's stat "
                    "priority."),
        node(A, "crystal_cannon", "Crystal Cannon",
             "Your damaging casts have a 30% chance to fire the Crystal "
             "Cannon.",
             2, 3, 3, {"unlock_ability": "chronomancer_crystal_cannon"},
             connect=["caverns_of_time"],
             proc={"trigger": "on_damage_cast", "chance": 30, "icd": 1,
                   "cast_ability": "chronomancer_crystal_cannon"},
             source="CoA's level-30 free passive: 'Casting Discordance now "
                    "unleashes the Crystal Cannon, launching 2 quick lesser "
                    "Wand attacks at the enemy.' A real free cast via "
                    "cast_ability; the trigger is any damaging cast rather "
                    "than Discordance specifically, since procs cannot name "
                    "the ability that fired them."),

        node(A, "flux_emitter", "Flux Emitter",
             "Teaches Flux Emitter, the cleave Continuum.",
             3, 0, 1, {"unlock_ability": "chronomancer_flux_emitter"},
             node_type="active", connect=["singularity_core"],
             source="CoA: 'On a pack, swap your Continuum to Flux Emitter for "
                    "its 3-4-target cleave.'"),
        node(A, "hyperwand", "Hyperwand",
             "Increases the damage of Shatter Echo by 4% per rank.",
             3, 1, 5,
             {"ability_chronomancer_shatter_echo_damage": 0.04},
             connect=["shatter_echo"],
             source="CoA: 'Increases the damage and critical damage of your "
                    "Shatter Echo by 30%.'"),
        node(A, "infinity_stone", "Infinity Stone",
             "Increases your physical and spell critical strike chance by 1% "
             "per rank.",
             3, 2, 5, {"crit_chance_physical": 1.0, "crit_chance_spell": 1.0},
             connect=["elder_wand"],
             source="CoA: 'Increases the critical strike chance of all party "
                    "and raid members by 3% ... In addition, increases your "
                    "critical strike chance by 3%.' Only the personal half "
                    "can exist - talent effects never reach a party - so the "
                    "node covers both of the spec's two crit pools instead."),
        node(A, "splitting_time", "Splitting Time",
             "Increases the damage your area spells deal by 5% per rank.",
             3, 3, 3, {"aoe_damage": 0.05},
             connect=["crystal_cannon"],
             source="CoA: 'Your Crystal Cannon now strikes 2 additional "
                    "nearby enemies', and Sporadic Incantations' 'Your Flux "
                    "Emitter now strikes 1 additional enemy'. Target counts "
                    "are fixed on the ability, so the extra targets become "
                    "harder area damage - which is also CoA's honest verdict "
                    "on this spec: 'No uncapped AoE.'"),

        node(A, "paradox_cannon", "Paradox Cannon",
             "Teaches Paradox Cannon, which banks Mana between pulls.",
             4, 0, 1, {"unlock_ability": "chronomancer_paradox_cannon"},
             node_type="active", connect=["flux_emitter"], total_slots=3,
             source="CoA: 'Bank ahead with Paradox Cannon between pulls.'"),
        node(A, "conduction_burst", "Conduction Burst",
             "Increases your Arcane spell damage by 3% per rank.",
             4, 1, 3, {"arcane_spell_damage": 0.03}, connect=["hyperwand"],
             total_slots=3,
             source="CoA: 'Your Shatter Echo now deals 20% additional damage "
                    "while a Continuum spell is active.' The Continuum "
                    "condition cannot be read, so it is the spec's Arcane "
                    "damage - which covers Shatter Echo and Arc Collision but "
                    "deliberately not the wand line (ranged_damage resolves "
                    "as physical)."),
        node(A, "reverse_engineering", "Reverse Engineering",
             "Your casts have a 15% chance to grant you 8 haste for 3 turns "
             "and return a little Mana.",
             4, 2, 3, {}, connect=["infinity_stone"], total_slots=3,
             proc={"trigger": "on_damage_or_heal_cast", "chance": 15,
                   "icd": 2,
                   "grant_resource": {"resource": "mana", "amount": 40},
                   "apply_effect": self_buff(
                       "reverse_engineering", "Reverse Engineering", 3,
                       {"haste": 8.0})},
             source="CoA: 'Periodic damage and healing now has a 15% chance "
                    "to increase your haste by 15% for 6 seconds and grant "
                    "allies Replenishment.' Replenishment reaches the party, "
                    "which a proc cannot, so the mana goes to the "
                    "Chronomancer."),

        node(A, "intuition", "Intuition",
             "Increases the damage of your critical strikes by 5% per rank.",
             5, 0, 2, {"crit_damage_physical": 0.05,
                       "crit_damage_spell": 0.05},
             connect=["paradox_cannon"], total_slots=3,
             source="CoA's level-50 free passive: 'Increases your critical "
                    "damage by 25%.' Both pools, because this spec crits with "
                    "both."),
        node(A, "time_is_a_circle", "Time Is A Circle",
             "Your Continuum spells last 1 turn longer per rank.",
             5, 1, 3,
             {"ability_chronomancer_singularity_core_duration": 1,
              "ability_chronomancer_flux_emitter_duration": 1},
             connect=["conduction_burst"], total_slots=3,
             source="CoA's level-40 free passive: 'Casting Wand of Time now "
                    "extends the duration of your Continuum spells by 3 "
                    "sec.' Extension on cast has no hook, so the Continuums "
                    "simply last longer."),
        node(A, "magic_sensitivity", "Magic Sensitivity",
             "Grants 5 spell penetration per rank.",
             5, 2, 3, {"spell_penetration": 5}, connect=["splitting_time"],
             total_slots=3,
             source="CoA: 'Critical strikes with Shatter Echo now increases "
                    "the enemy's damage taken from you by 10%.' A damage-"
                    "taken debuff is inert against creatures, and this spec's "
                    "stat priority puts Spell Penetration second, so the node "
                    "grants the stat the reference says to gear for."),

        node(A, "pulse_driver", "Pulse Driver",
             "Shatter Echo hits half again as hard, and your critical strikes "
             "land heavier still.",
             6, 0, 1,
             {"ability_chronomancer_shatter_echo_damage": 0.15,
              "crit_damage_physical": 0.1, "crit_damage_spell": 0.1},
             node_type="active",
             connect=["intuition", "time_is_a_circle", "magic_sensitivity"],
             total_slots=1,
             source="Capstone. CoA: 'Singularity Core now increases the "
                    "damage of Shatter Echo while its active by 30% and "
                    "allows Shatter Echo to trigger its damage.' The "
                    "Continuum condition is not readable, so the payoff is "
                    "unconditional and smaller - which also matches what CoA "
                    "says the spec is for: 'Bank Echo Fragments into an "
                    "empowered Singularity Core, dump them on Shatter Echo, "
                    "and the sustained spike holds up. Single-target is the "
                    "identity here.'"),
    ],
    "Built from reference/coa_sidekick/SPEC_chronomancer__artificer.txt: "
    "'Closest to a builder/spender ranged caster: a stack-driven Arcane Mage "
    "crossed with the Essence loop of an Evoker.' Two things shape this tree. "
    "First, Echo Fragments cannot be a resource, so the build-and-spend "
    "rhythm is carried by cooldowns and six ability unlocks rather than a "
    "bar. Second, the wand line is authored as ranged_damage so Wand Expert's "
    "Spirit conversion is real - which splits the spec's damage across two "
    "engine paths, physical (wand) and arcane (Distortion), and is why crit "
    "and critical damage appear here in both flavours while "
    "arcane_spell_damage appears only on the spell side. Stat priority is "
    "Spell Hit > Spell Penetration > Spirit > Crit > Haste > Spell Power > "
    "Intellect, and Spell Power sits that low precisely because most of this "
    "kit is not spell damage at all.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the files")
    args = parser.parse_args()

    ability_doc = {
        "class": "Chronomancer",
        "_source_note": __doc__.strip().split("\n\n")[1].replace("\n", " "),
        "abilities": ABILITIES,
    }

    targets = [
        (ROOT / "data/abilities/chronomancer.json", ability_doc),
        (ROOT / "data/talents/chronomancer_infinite.json", INFINITE),
        (ROOT / "data/talents/chronomancer_time.json", TIME),
        (ROOT / "data/talents/chronomancer_artificer.json", ARTIFICER),
    ]

    print(f"{len(ABILITIES)} abilities")
    for path, doc in targets[1:]:
        points = sum(n["max_points"] for n in doc["nodes"])
        print(f"{doc['tree_id']}: {len(doc['nodes'])} nodes, {points} points")

    if not args.apply:
        print("\n(dry run - pass --apply to write)")
        return 0

    for path, doc in targets:
        path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
