#!/usr/bin/env python3
"""Author the Witch Hunter: ability kit + four talent trees.

    PYTHONPATH=. python3 tools/build_witch_hunter.py [--apply]

One of the twelve CoA classes that had base stats, mail armour, Agility and a
Focus pool but no abilities and no talents, so it could not be selected. Four
specs, which is one more than any class authored before it, and the first
class in the game whose primary resource is dict-backed rather than one of
Character's dedicated pools.

SOURCE. reference/coa_sidekick/CLASS_witch-hunter.txt, the four
SPEC_witch-hunter__*.txt pages and reference/coa_sidekick/talents/
witch-hunter.json, captured from ascensionsidekick.com. Every ability and
talent name below is a real CoA name off those pages; nothing is invented to
fill a slot. Identity per that reference:

  Boltslinger  RANGED DPS  "An Outlaw/Survival hybrid built on real tools. A
                           burst-window rogue crossed with a kiting hunter."
                           Builds Bounty Hunter stacks, dumps them into a
                           charged Heartseeking Bolt. Survival is avoidance -
                           Daring Escape, Vault, Pavise - not absorbs.
  Houndmaster  RANGED DPS  "A Survival-Hunter chassis with a heavier pet
                           emphasis. You fight two-plus bodies at once and
                           split incoming damage across hounds." The only
                           spec in this class with a companion.
  Black Knight TANK        "A sticky avoidance tank rather than an anti-caster
                           bruiser." Parry rating is simultaneously its
                           mitigation, its damage and its self-healing stat,
                           because Noctis Blade scales off it.
  Inquisition  MELEE DPS   "A build-and-spend fire/shadow melee. It layers
                           Dawn/Dusk and Purity & Wickedness stacks the way a
                           combo-point class does, then converts them through
                           Flames of Sin."

CoA GIVES EACH CLASS A SHARED CLASS TREE PLUS ONE TREE PER SPEC; Frontier has
no class tree. The best class-tree nodes are therefore distributed into the
spec trees that actually want them - Night Stalker and My Trusty Arbalest into
Boltslinger, Trapper's companion Three Sevens into Houndmaster, Dark Penance
into Black Knight, Refined Combatant and Flexible Fighter into Inquisition -
rather than being dropped. The class-kit ABILITIES those class-tree talents
teach (the three Traps, the Tonics, Vault, Burrow Bolt, Witching Shroud,
Slayer's Mark) are authored as ordinary level-learned abilities, the same way
Guardian's class kit is.

NUMBERS ARE FRONTIER'S, NOT CoA'S. The reference gives identity, role and
rotation shape; it is a fan-made planning tool whose own disclaimer says COA
is pre-meta. Damage curves copy Hunter's and Rogue's shipped shapes - Hunter
because it is the other mail/Agility/ranged/pet class (steady_shot: 9 ranks at
1/6/12/18/24/32/40/48/56, 42 rising to 124) and Rogue because it is the other
flat-cost non-Mana class (sinister_strike: the same 42-to-125 curve on the
same levels). Single-target payoffs use the 5-rank 52-to-151 shape Rogue's
Backstab and Hunter's Aimed Shot share.

FOCUS BUDGET, AND THE REASON THIS CLASS IS A BUILDER/SPENDER. Focus is
declared in combat/abilities.py's ResourceType and mapped as Witch Hunter's
primary in CLASS_RESOURCE_MAP, but it is dict-backed (Character.
secondary_resources), so it has NO regen path at all: Character.
restore_resources_between_turns only refills Energy and Mana, and there is no
current_focus attribute for anything else to top up. A Witch Hunter therefore
starts every fight on 0 Focus and the pool never refills on its own.

That is not a reason to dodge the resource, because CoA's Witch Hunter is
already a builder/spender - its spec pages say so over and over ("Brimming
Hatred: your critical strikes now generate 10 Rage", "your ranged auto attacks
now generate Rage", Quickdraw "generates Rage", Heartseeking Bolt "generates
Rage based on the damage dealt", Hunt "generating 20 Rage", "March of the
Black King refunds Rage", "Neverending Pursuit: critically striking with
Damnation now refunds 40 Rage"). So CoA's Rage maps onto Frontier's Focus and
the kit is built the way Stormbringer's Mana-into-Static chassis already is:

  BUILDERS cost 0 Focus and carry `generates` {"resource": "focus", ...} -
  Shadowblast (+25, the filler every spec presses) and Quickdraw (+25,
  Houndmaster). March of the Black King restores 25 more on an 8-turn
  cooldown, and three talent procs grant Focus off crits, parries and Hunt.
  SPENDERS cost a flat 20-45 Focus. Flat, because a non-Mana pool caps at 100
  and a cost over 100 is permanently uncastable - validate_class.py fails on
  it. Nothing here costs more than 45, so two builder turns always pay for
  the most expensive button in the kit.

Talent effect keys are restricted to ones the engine actually reads, verified
with tools/validate_class.py (which delegates liveness to tools/
audit_talents.py). Casualties worth recording, all noted again on the node
that carries them:

  - Dark Power's "1 Stamina for every 2 Agility" cannot be a real
    <target>_from_<source>_pct conversion: STAT_CONVERSION_TARGETS has no
    stamina entry, so stamina_from_agility_pct is dead. Flat stamina_pct.
  - focus_max is dead even though Character.get_resource_max would read it
    generically for any dict-backed pool - audit_talents only knows the
    *_max keys that appear as literals somewhere, and no shipped tree has
    ever raised a Focus pool. No node tries to.
  - ranged_attack_power is computed from Agility and Strength only and never
    reads the bonus pool, so "+10% ranged attack power" has to go through
    ranged_ap_from_agility_pct instead of a flat grant.
  - ranged_haste and melee_haste are both dead; the engine has one `haste`.
  - There is no silence, no interrupt, no knockback, no movement speed and no
    school lockout in this engine. Every ability whose CoA text is built on
    one of those says so in its own _source.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Hunter's and Rogue's shared shipped rank schedule - see module docstring.
RANK_LEVELS = [1, 6, 12, 18, 24, 32, 40, 48, 56]


def ranks(base, step, cost, start=1, count=9, **extra):
    """Flat-cost rank table on the Hunter/Rogue schedule, starting at `start`.

    Levels past the 9-rank schedule are spaced evenly to stay under 58 so
    every rank is actually reachable at the level 60 cap. `extra` is merged
    into every rank, which is how restore_resource abilities carry the
    `mana_restore_pct` the engine actually reads for them.
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
        rank.update(extra)
        out.append(rank)
    return out


def one(level, cost, value=0, **extra):
    """Single-rank table, for cooldowns and tonics that do not scale."""
    rank = {"rank": 1, "level_req": level, "cost": cost, "effect_value": value}
    rank.update(extra)
    return [rank]


#: The real ranged weapon_types a Witch Hunter is proficient with, per
#: data/items/weapon_types.json's class_weapon_map. Ability.is_ranged_ready
#: compares the equipped Ranged slot's weapon_type against this, so the
#: gate MUST be a list of real weapon_types - a literal `true` would make
#: `equipped_type == True` and brick the ability forever.
CROSSBOWS = ["crossbow", "gun", "thrown"]

#: CoA's Twilight school is shadow-arcane. Frontier has no Twilight, but
#: damage_school accepts a LIST and _school_damage_bonus/
#: get_effective_spell_power consider each component (Sun Cleric's
#: ["holy", "fire"] abilities already do this), so Twilight resolves to both
#: of its real halves rather than collapsing to plain Shadow.
TWILIGHT = ["shadow", "arcane"]


def ability(aid, name, effect_type, description, rank_table, *, cooldown=0,
            duration=0, stat_mods=None, icon=None, source=None, **extra):
    out = {
        "ability_id": f"witch_hunter_{aid}",
        "name": name,
        "resource_type": "focus",
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
# Order is roughly the order a player meets them: shared chassis first, then
# the four specs in the order the reference lists them.
ABILITIES = [
    ability("attack", "Attack", "damage",
            "A measured strike with your weapon.", one(1, 0, 0),
            icon="ability_melee",
            source="Convention: every class ships a free rank-1 Attack. It is "
                   "also this class's only truly unconditional action, which "
                   "matters more here than elsewhere - a Witch Hunter opens "
                   "every fight on 0 Focus."),

    # ---- shared chassis: the class kit all four specs press
    ability("shadowblast", "Shadowblast", "ranged_damage",
            "A short, flat shot you can take from anywhere, and the one that "
            "settles you into the fight.",
            ranks(42, 10, 0), target_type="enemy",
            generates={"resource": "focus", "amount": 25},
            source="CoA names Shadowblast in three of the four spec trees as "
                   "the thing everything else is measured against (My Trusty "
                   "Arbalest cuts its cost, Expert Shot raises its damage, "
                   "Sharpshooter makes casting it restore resource, Darkrider "
                   "cuts its cost again), so it is the class filler. THE FOCUS "
                   "BUILDER: costs nothing, banks 25. Hunter's steady_shot "
                   "curve exactly - 9 ranks, 42 rising to 124. Deliberately "
                   "NOT gated on a ranged weapon, the same way none of "
                   "Hunter's shots are, so the kit still functions unarmed."),
    ability("darkslayer", "Darkslayer", "ranged_damage",
            "A heavy, deliberate bolt. You take the extra moment to place it.",
            ranks(56, 16, 30, start=10, count=8), cooldown=2,
            target_type="enemy", requires_ranged_weapon=CROSSBOWS,
            source="CoA: Boltslinger's Heavy Crossbows 'increases the damage "
                   "of Darkslayer by 50%, but increases its cast time by 0.5 "
                   "sec' and Houndmaster's Silver Bullets and Darkhunter both "
                   "scale it, so it is shared rather than spec-owned. The "
                   "signature crossbow shot, so it is one of the few abilities "
                   "that really does require the weapon."),
    ability("dawn_blade", "Dawn Blade", "damage",
            "Bring the blade round in a clean, bright arc.",
            ranks(44, 11, 25), target_type="enemy", icon="ability_melee",
            source="CoA scales Dawn Blade from both Black Knight (Bulwark of "
                   "Darkness, Destroyer of Evil, Undying, Dawn Knight, "
                   "Foresight, Blade of the Misbegotten) and Inquisition "
                   "(Protector of Darkshire, Interrogator, Dusk), so it is a "
                   "class strike, not a spec one. The melee half of the "
                   "chassis, on the same curve as Shadowblast."),
    ability("burrow_bolt", "Burrow Bolt", "ranged_damage",
            "A bolt with a line on it. Whatever it hits comes to you.",
            ranks(40, 12, 20, start=14, count=6), cooldown=4,
            target_type="enemy",
            source="CoA: 'Shoot a bolt with a rope attached to it at an enemy "
                   "dealing AP Physical damage and pulling them to you'. Both "
                   "Inquisition and Black Knight list it as a gap-closer. The "
                   "pull itself has no engine hook - there is no position in a "
                   "turn-based fight to drag anything to - so it lands as the "
                   "damage half on a short cooldown."),
    ability("vault", "Vault", "buff",
            "Push off and cover ground you had no business covering.",
            one(10, 0), cooldown=3, duration=1,
            stat_mods={"dodge": 20.0}, target_type="self",
            source="CoA: 'Dash in the direction you are moving. Distance "
                   "scales with movement speed.' Movement is not a thing this "
                   "engine models, so the dash lands as the brief window of "
                   "not-being-where-the-attack-is that it buys. Free, because "
                   "every spec's escape plan is built on having it."),
    ability("witching_shroud", "Witching Shroud", "buff",
            "You step sideways out of the spellwork and it closes over empty "
            "air.",
            one(26, 0), cooldown=12, duration=1,
            stat_mods={"magic_damage_taken_pct": -0.5, "cc_immune": 1},
            target_type="self",
            source="CoA: 'Enter a powerful stealth mode for 3 seconds, "
                   "granting immunity to all harmful magic effects... Usable "
                   "while stunned or feared.' cc_immune is the engine's real "
                   "crowd-control immunity flag (StatusEffectMixin reads it "
                   "before applying a stun), paired with heavy magic "
                   "mitigation. The 'only usable for 10 seconds after being "
                   "hit by a magical critical strike' condition has no hook, "
                   "so it is a plain 12-turn cooldown instead."),
    ability("witchblood_tonic", "Witchblood Tonic", "dispel",
            "Bitter, black, and it takes the curse with it.",
            one(18, 15), cooldown=8, target_type="ally", dispel_type="curse",
            source="CoA: 'Drink a shadowy tonic, removing all curse effects "
                   "from you and reducing all Magic damage taken by -40% for "
                   "10 seconds.' Both spec pages that mention it name only the "
                   "cleanse ('Witchblood Tonic's curse cleanse'), so the "
                   "cleanse is what it is - no effect_type does a dispel AND a "
                   "buff in one cast, and the -40% magic window is dropped "
                   "rather than faked. target_type 'ally' is the shipped "
                   "convention for every friendly cleanse in the game."),
    ability("vampiric_tonic", "Vampiric Tonic", "buff",
            "For a little while, what you take off them stays with you.",
            one(30, 20), cooldown=10, duration=3, target_type="self",
            proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
                  "leech_pct": 0.20},
            source="CoA: 'Drink a vampiric tonic, allowing Physical damage "
                   "dealt to heal you equal to 20% of the damage dealt for 10 "
                   "seconds.' A real leech_pct proc carried on the buff's own "
                   "StatusEffect, which is exactly 20% of the triggering hit. "
                   "Three of the four spec pages call this the class's only "
                   "real healing outside their own spec."),
    ability("slayers_mark", "Slayer's Mark", "debuff",
            "You name them out loud. Everything after that is easier.",
            one(34, 20), cooldown=6, duration=3,
            stat_mods={"physical_damage_taken_pct": 0.08}, target_type="enemy",
            source="CoA: 'Mark an enemy, increasing the attack power of all "
                   "attackers against that target by 150 and your critical "
                   "strike chance against them by 3%.' A debuff's stat_mods "
                   "land on the ENEMY here, so the attacker-side wording is "
                   "turned round into the defender-side key that means the "
                   "same thing - physical_damage_taken_pct on the marked "
                   "target, read from status effects in Character.take_damage."),
    ability("inquisitors_trap", "Inquisitor's Trap", "debuff",
            "Laid where they will walk, and it goes off badly for everyone "
            "standing near it.",
            one(22, 25), cooldown=6, duration=2,
            stat_mods={"haste": -25.0}, target_type="enemy_aoe", max_targets=5,
            source="CoA: 'a cruel trap... silencing them and all enemies in a "
                   "5 yd radius for 6 seconds.' There is no silence in this "
                   "engine, and Guardian's Hammer of the Law set the precedent "
                   "of NOT dressing a silence up as a stun, so it lands as a "
                   "heavy haste debuff on the pack. The 'first enemy to "
                   "approach' trigger has no hook either; it is cast."),
    ability("shadow_trap", "Shadow Trap", "debuff",
            "The ground goes dark under them and they stop where they are.",
            one(16, 30), cooldown=8, duration=1, target_type="enemy_aoe",
            is_stun=True, max_targets=5,
            source="CoA: 'stunning them for 4 seconds and dealing AP Shadow "
                   "damage over 8 seconds'. The real stun - is_stun is only "
                   "read in the debuff branch, so a stun has to be a debuff "
                   "and cannot also be the DoT. Both Boltslinger and "
                   "Inquisition cite the class traps as the only hard control "
                   "they have ('stuns and silences come from class-kit traps "
                   "an enemy has to walk into'), so the stun is the half "
                   "that matters."),
    ability("death_trap", "Death Trap", "dot",
            "A quiet mark, and then a debt that comes due.",
            ranks(34, 10, 25, start=28, count=5), cooldown=5, duration=3,
            target_type="enemy", damage_school="shadow",
            source="CoA: 'a death trap... marking them for death, causing them "
                   "to take AP Shadow damage after 1 minute.' A one-minute "
                   "fuse is meaningless in turns, so it is a real Shadow DoT."),

    # ---- Black Knight
    ability("noctis_blade", "Noctis Blade", "damage_and_heal",
            "A stroke you have practised more than any other, and it gives "
            "something back.",
            ranks(58, 16, 25, start=10, count=7), cooldown=2,
            target_type="enemy", icon="ability_melee",
            source="CoA: 'Strike an enemy, dealing 100% Weapon Damage plus 26, "
                   "scaling with your parry rating, and healing you for 50% of "
                   "the damage dealt.' The spec's whole identity - 'Noctis "
                   "Blade is your on-demand self-heal, an active strike on a "
                   "short cooldown whose damage and self-heal both scale with "
                   "your parry rating.' damage_and_heal is the real effect_type "
                   "for that. Scaling off parry specifically is not something "
                   "an ability can declare, so the TREE does it: Dusk Knight "
                   "converts Agility into parry and Dark Penance raises it."),
    ability("pommel_smash", "Pommel Smash", "damage",
            "Short, ugly, and it lands where the armour does not reach.",
            ranks(38, 10, 20, start=6, count=8), target_type="enemy",
            icon="ability_melee",
            source="CoA: 'Pommel Smash strikes feed Shadowstorm, a chance to "
                   "trigger a Shadowstorm burst', and Guardbreaker makes it "
                   "cleave. The spec's cheap filler, so it is cheaper than "
                   "Dawn Blade and has no cooldown."),
    ability("shadow_brand", "Shadow Brand", "dot",
            "A mark that burns cold and will not be ignored.",
            ranks(26, 8, 20, start=12, count=6), duration=3,
            target_type="enemy", damage_school="shadow",
            stat_mods={"threat_generation_pct": 180},
            source="CoA: 'Marks the target for 12 seconds, dealing 36 High "
                   "Threat Shadow Damage over 12 seconds.' The 'High Threat' "
                   "wording is why it carries a threat_generation_pct buff - "
                   "percent POINTS as an ability stat_mod, unlike the tree's "
                   "fractions. CoA applies it automatically off direct ability "
                   "damage; nothing hooks that, so it is cast."),
    ability("guard_strike", "Guard Strike", "damage",
            "Drive the hilt into them hard enough that whatever they were "
            "saying stops.",
            ranks(50, 14, 20, start=20, count=6), cooldown=4,
            target_type="enemy", icon="ability_melee",
            source="CoA: 'Bash an enemy with your weapon's hilt, interrupting "
                   "them and preventing any spell from that school of magic "
                   "from being cast for 3 seconds', and the spec blurb calls "
                   "this 'the kit's only caster answer'. There is no interrupt "
                   "and no school lockout in this engine, so the whole "
                   "anti-caster half is gone and what remains is a cheap "
                   "mid-cooldown strike. This is the single biggest gap "
                   "between CoA's Black Knight and Frontier's."),
    ability("desecrate", "Desecrate", "damage",
            "Answer the blow you just turned aside, and the ones standing "
            "behind it.",
            ranks(36, 10, 30, start=16, count=6), cooldown=3,
            target_type="enemy_aoe", damage_school="shadow", max_targets=5,
            source="CoA: 'Desecrate up to 8 enemies in front of you, dealing "
                   "Weapon Damage plus 18 as Shadow damage, piercing "
                   "resistances. Only usable after avoiding an attack.' The "
                   "avoidance gate has no hook - nothing records 'you just "
                   "dodged' as a castable condition - so it is a plain "
                   "cooldown. target_type enemy_aoe is what actually makes an "
                   "ability hit more than one target; the is_aoe field several "
                   "shipped files carry is never read."),
    ability("chains_of_darkness", "Chains of Darkness", "debuff",
            "Reach out, take hold of all of them at once, and make yourself "
            "the only thing worth looking at.",
            one(24, 25), cooldown=5, duration=2,
            stat_mods={"taunt": 1, "threat_generation_pct": 200},
            target_type="enemy_aoe", max_targets=5,
            source="CoA: 'Pull all nearby enemies to you, dealing shadow AP "
                   "Shadow damage and taunting them for 3 seconds', listed in "
                   "the control suite as 'pull plus taunt to yank a target off "
                   "an ally'. {'taunt': 1} is the engine's real taunt flag, "
                   "handled in Ability.use rather than any one effect_type "
                   "branch; the shipped tank taunts across Cultist, Starcaller, "
                   "Venomancer and Primalist all use exactly this shape."),
    ability("stoicism", "Stoicism", "buff",
            "Set yourself and decide that this is survivable.",
            one(28, 20), cooldown=10, duration=3,
            stat_mods={"damage_taken_pct": -0.2}, target_type="self",
            source="CoA never prints Stoicism's own tooltip, but two Black "
                   "Knight talents exist only to modify it (Calm Under "
                   "Pressure cuts its cooldown by 30 sec, Dark Barrier extends "
                   "it by 5 sec), which makes it a real mitigation cooldown. "
                   "Sized below Guardian's Raise Shield (-40%) because this "
                   "spec gets Gaze of the Black Knight on top."),
    ability("march_of_the_black_king", "March of the Black King", "restore_resource",
            "Let the dark out and let it carry you a while.",
            ranks(18, 2, 0, start=22, count=5, mana_restore_pct=25),
            cooldown=8, target_type="self", restore_resource_type="focus",
            source="CoA: 'Expel darkness from within you, dealing 55 Shadow "
                   "damage to nearby enemies over 10 seconds. Generates 5 Rage "
                   "every 2 sec', and the spec's strengths say 'March of the "
                   "Black King refunds Rage. You rarely go dry.' Frontier's "
                   "Focus is CoA's Rage here (see the module docstring), so "
                   "this is the tank's own Focus refill. NOTE the engine reads "
                   "mana_restore_pct OFF THE RANK for restore_resource, not "
                   "effect_value - Guardian's Knight's Calling omits it and "
                   "restores 0."),
    ability("knights_seal", "Knight's Seal", "dot",
            "Lay the old oath on them and let it do the work.",
            ranks(30, 9, 25, start=30, count=5), cooldown=5, duration=3,
            target_type="enemy", damage_school="shadow",
            source="CoA: 'Curse an enemy, dealing shadow AP Shadow damage "
                   "every 2 sec and applying Dark Oath to you, reducing all "
                   "damage taken by 5% for 8 seconds.' A single cast cannot "
                   "both DoT an enemy and buff the caster, so the Dark Oath "
                   "half is dropped and the DoT kept."),
    ability("witching_idol", "Witching Idol", "dispel",
            "Plant it, and whatever is in your friends' heads loses its grip.",
            one(32, 20), cooldown=6, target_type="ally", dispel_type="magic",
            dispel_count=2,
            source="CoA: 'Drop a Witching Idol that periodically dispels fear, "
                   "sleep, and charm effects every 3 sec from party members "
                   "within 20 yds.' DispelType has only magic/curse/poison/"
                   "disease, and fear, sleep and charm are all Magic effects in "
                   "WoW, so it cleanses Magic - two at a time, standing in for "
                   "the periodic tick, which has no hook."),
    ability("witchblight", "Witchblight", "damage_and_heal",
            "Let it all out at once. Everything close enough pays, and you "
            "come back up.",
            ranks(60, 18, 40, start=40, count=4), cooldown=10,
            target_type="enemy_aoe", damage_school="shadow", max_targets=5,
            source="CoA: 'Explode with dark energy, dealing shadow AP Shadow "
                   "damage to up to 10 enemies within 8 yds and healing you for "
                   "20% of your maximum health. Each target struck is "
                   "guaranteed to miss their next instance of damage.' "
                   "damage_and_heal carries the damage and the self-heal; the "
                   "guaranteed-miss rider has no hook."),
    ability("gaze_of_the_black_knight", "Gaze of the Black Knight", "buff",
            "You look at them, and for a while what happens to them happens "
            "to you instead.",
            one(50, 40), cooldown=18, duration=3,
            stat_mods={"damage_taken_pct": -0.15}, target_type="self",
            absorb_pct_max_health=0.25,
            source="CoA: 'Apply a dark shield to yourself, absorbing AP damage "
                   "and then gaze upon your party members, causing 25% of the "
                   "damage they take to be transferred to you for 12 seconds.' "
                   "The absorb is real (absorb_pct_max_health is read for cast "
                   "buffs). The party-damage REDIRECTION is not expressible - "
                   "no effect routes one combatant's incoming damage to "
                   "another - so the mitigation lands on the Black Knight "
                   "instead. CoA calls this 'rare group damage-redirection' and "
                   "'one long-cooldown panic button', and it is the spec's one "
                   "real loss in translation."),

    # ---- Boltslinger
    ability("tormentor", "Tormentor", "spell_dot",
            "A bolt that sits in the wound and keeps asking questions.",
            ranks(30, 9, 25, start=12, count=6), cooldown=2, duration=3,
            target_type="enemy", damage_school=TWILIGHT,
            requires_ranged_weapon=CROSSBOWS,
            source="CoA: 'Fire a deadly bolt dealing Twilight Damage plus "
                   "ranged AP over 14 seconds', and the rotation opens with "
                   "it - 'Open with Tormentor to lay its DoT'. Twilight is "
                   "shadow-arcane (see TWILIGHT). CoA explicitly lists it among "
                   "the abilities that 'want a ranged crossbow equipped'."),
    ability("witchbane", "Witchbane", "dot",
            "You do not stop shooting until the magazine does.",
            ranks(34, 10, 35, start=20, count=6), cooldown=4, duration=3,
            target_type="enemy", damage_school="physical",
            requires_ranged_weapon=CROSSBOWS,
            source="CoA: 'Unleash a series of devastating shots dealing ranged "
                   "AP Physical damage over 3 seconds' - a channel, so a "
                   "physical DoT rather than one hit. Arbalest Mastery ('each "
                   "subsequent shot deals 15% more') and Rapid ('full damage "
                   "over 1 second shorter') both scale it in the tree."),
    ability("heartseeking_bolt", "Heartseeking Bolt", "ranged_damage",
            "Take the extra breath. Put it exactly where it needs to go.",
            ranks(70, 20, 40, start=24, count=6), cooldown=3,
            target_type="enemy", requires_ranged_weapon=CROSSBOWS,
            source="CoA: 'Charge up a powerful bolt that deals 200% Ranged "
                   "Weapon Damage plus shadow SP to an enemy and reduces their "
                   "healing received by 30% for 10 seconds.' The spec's payoff "
                   "button - 'build Bounty Hunter stacks... then spend them on "
                   "a charged Heartseeking Bolt for burst'. The anti-heal rider "
                   "is a debuff and a damage cast cannot carry one, so it is "
                   "dropped; healing_taken_pct exists but only as a debuff's "
                   "own stat_mods."),
    ability("twilight_frenzy", "Twilight Frenzy", "damage",
            "Spin up and keep firing, and do not stop moving.",
            ranks(38, 11, 35, start=30, count=5), cooldown=6,
            target_type="enemy_aoe", damage_school=TWILIGHT, max_targets=5,
            requires_ranged_weapon=CROSSBOWS,
            source="CoA: 'Spin around, unable to stop moving for 5 seconds, "
                   "firing shots at nearby enemies for 50% Ranged Weapon Damage "
                   "plus as Twilight Damage. Can dodge and parry while active.' "
                   "The spec's cleave. Evasive and Crossbow Frenzy in the tree "
                   "are what CoA layers on top of it."),
    ability("damnation", "Damnation", "ranged_damage",
            "Spend everything you have left on one bolt.",
            ranks(96, 26, 45, start=40, count=4), cooldown=4,
            target_type="enemy", execute_threshold_pct=35,
            requires_ranged_weapon=CROSSBOWS,
            source="CoA: 'Deplete your rage to shoot a powerful bolt... "
                   "converting each point of Rage into additional damage. Only "
                   "usable on enemies below 35% health.' execute_threshold_pct "
                   "is PERCENT in this engine (Warrior's Execute 20, "
                   "Netherstrike and Electrocute 35), matching CoA's 35 "
                   "exactly. 'Deplete your rage' is not a cost shape the engine "
                   "has - costs are fixed per rank - so it costs the most Focus "
                   "of anything in the class instead."),
    ability("daring_escape", "Daring Escape", "buff",
            "Go backwards faster than they expected, and let the shots go "
            "where you were.",
            one(22, 0), cooldown=5, duration=1,
            stat_mods={"dodge": 30.0}, target_type="self",
            source="CoA: 'Jump backwards, causing all ranged attacks to miss "
                   "you for 2 seconds.' Nothing distinguishes incoming RANGED "
                   "attacks from melee ones, so the guaranteed miss becomes a "
                   "large dodge window - the strongest one in the class, which "
                   "is right for a spec whose summary is 'not being caught is "
                   "the defense'."),
    ability("pavise", "Pavise", "buff",
            "Drive the shield into the dirt and work from behind it.",
            one(44, 25), cooldown=12, duration=3, target_type="self",
            absorb_pct_max_health=0.18,
            source="CoA: Pavise Crossbowman 'teaches you how to use Shields and "
                   "teaches you Pavise. Slam your shield into the ground, "
                   "forming a pavise for 10 sec. While you remain near it, "
                   "hostile spells targeting you are deflected.' The shield "
                   "proficiency half is already true - weapon_types.json gives "
                   "Witch Hunter shields - and spell deflection has no hook, so "
                   "it lands as a real absorb. Authored at level 44 rather than "
                   "talent-unlocked so the spec has it without spending its "
                   "capstone, and the tree's Dead and Gone extends it."),
    ability("slayer", "Slayer", "buff",
            "Point out the soft parts and everyone starts hitting them.",
            one(36, 25), cooldown=10, duration=4,
            stat_mods={"crit_chance_physical": 3.0, "crit_chance_spell": 3.0},
            target_type="party", buff_scope="combat",
            source="CoA: 'Increases critical strike chance of all party and "
                   "raid members by 3%... In addition, increases your critical "
                   "strike chance by 3%.' The raid buff the spec's own blurb "
                   "sells it on ('brings raid crit (Slayer)'). target_type "
                   "'party' with buff_scope 'combat' is the shipped shape for a "
                   "real party buff; buff_scope only accepts 'raid' or "
                   "'combat' and silently rewrites anything else."),

    # ---- Houndmaster
    ability("houndmasters_whistle", "Houndmaster's Whistle", "summon_pet",
            "One note, and something comes out of the dark that answers to "
            "you.",
            one(1, 0, 100), target_type="self", is_instant=True,
            summon_pet_template="wolf",
            source="CoA: 'Summons a permanent Shadowhound companion to aid you "
                   "in combat.' Modelled on Hunter's Tame Beast - the only "
                   "effect_type that actually calls Character.summon_pet is "
                   "summon_pet with a template that already exists in "
                   "combat/pet_templates.py. 'wolf' is the shipped hound-shaped "
                   "template (melee beast, Energy, base_attack 22). "
                   "effect_type 'summon' summons NOTHING - four Tinker "
                   "abilities shipped that way and were silently empty for "
                   "months."),
    ability("unleash_the_hounds", "Unleash the Hounds", "summon_pet",
            "Let the rest of them off the chain.",
            one(20, 25), cooldown=8, target_type="self",
            summon_pet_template="raptor",
            source="CoA: 'Summon 1 Lesser Shadow Hound to aid you in combat for "
                   "20 seconds', with Kennel Master adding more. The engine "
                   "keeps ONE active pet, so a second summon replaces the "
                   "first rather than standing beside it - the 'temporary "
                   "lesser hounds' half of CoA's hound stack cannot be built. "
                   "'raptor' is the other existing melee-beast template, so "
                   "this is a faster, sharper hound rather than a second wolf."),
    ability("quickdraw", "Quickdraw", "ranged_damage",
            "The shot you take before you have decided to take it.",
            ranks(48, 14, 0, start=14, count=6), cooldown=2,
            target_type="enemy",
            generates={"resource": "focus", "amount": 25},
            source="CoA: 'Unleash a quick shot, dealing 175% Ranged Weapon "
                   "Damage plus ranged AP Physical damage and generates Rage. "
                   "Only usable after critically striking with an ability.' The "
                   "crit gate has no hook, so it is a 2-turn cooldown instead - "
                   "and the Rage generation is real, which makes this the "
                   "spec's own Focus builder alongside Shadowblast."),
    ability("houndmasters_call", "Houndmaster's Call", "damage",
            "Send them in. They know what to do.",
            ranks(52, 15, 30, start=18, count=6), cooldown=3,
            target_type="enemy", damage_school="shadow",
            source="CoA: 'Command your Shadow Hounds to leap upon an enemy "
                   "target, dealing two strikes for ranged AP Shadow damage.' "
                   "A pet cannot be ordered to strike from the owner's cast in "
                   "this engine, so the hounds' damage resolves as the owner's "
                   "Shadow strike. Expulsion of Evil in the tree resets it."),
    ability("darkflock", "Darkflock", "spell_dot",
            "Crows. A lot of them, and they stay a while.",
            ranks(32, 9, 35, start=26, count=5), cooldown=6, duration=3,
            target_type="enemy_aoe", damage_school="shadow", max_targets=5,
            source="CoA: 'Channel for 8 seconds, commanding a flock of crows to "
                   "deal SP Shadow damage to enemies in a wide cone every 2 "
                   "sec. Can channel while moving.' spell_dot because CoA "
                   "scales it off spell power, not AP - the spec's stat "
                   "priority lists Spell Power for exactly this ('feeds the "
                   "minor Shadow portions of Darkflock/Feast of Talons')."),
    ability("repulse", "Repulse", "damage",
            "A short, loud burst that puts everything in front of you on its "
            "back foot.",
            ranks(34, 10, 25, start=22, count=5), cooldown=4,
            target_type="enemy_aoe", damage_school="shadow", max_targets=4,
            source="CoA: 'Emit a burst of shadow from your musket that strikes "
                   "enemies in front of you, dealing 57 Shadow damage and "
                   "knocking all affected targets back.' The spec blurb calls "
                   "it 'a frontal knockback' and its only on-demand control. "
                   "There is no knockback and no position, so what survives is "
                   "the cone damage."),
    ability("decimate", "Decimate", "buff",
            "Work them up until they stop being careful.",
            one(38, 25), cooldown=12, duration=3,
            stat_mods={"attack_power_pct": 15.0, "haste": 8.0},
            target_type="self",
            source="CoA: 'Empowers your Shadow Hounds for 20 seconds, granting "
                   "them 30% increased damage and haste and allowing them to "
                   "ignore Armor.' A cast buff cannot reach the pet: Pet reads "
                   "its owner's pet_damage/pet_health/pet_armor TALENTS when it "
                   "is built, and nothing else, so a temporary buff on the owner "
                   "never touches it. The talent tree carries the real hound "
                   "scaling (Dark Ranger, Loksey's Journal, Decimate's own node, "
                   "Lethal Pursuit) and this ability keeps the burst window on "
                   "the Houndmaster instead."),
    ability("darkfeast", "Darkfeast", "heal",
            "Take something back out of the dark. It costs later, not now.",
            ranks(170, 90, 30, start=30, count=5), cooldown=8,
            target_type="self",
            source="CoA: 'Darkfeast is your on-demand heal.' The spec's "
                   "weaknesses are blunt about it being nearly all the healing "
                   "there is, so it is a real heal on a long cooldown rather "
                   "than a trickle. Hunter's Revive Pet curve, scaled down."),
    ability("rearmament", "Rearmament", "reset_cooldowns",
            "Reload everything, including the things you have already used.",
            one(46, 25), cooldown=20, target_type="self",
            source="CoA: 'Arm yourself against evil, resetting the cooldown of "
                   "all Traps and Decimate', and the spec blurb leads with it - "
                   "'your Trap spells, reset on demand by Rearmament'. "
                   "reset_cooldowns is a real effect_type; it does not take a "
                   "filter, so it resets the whole book rather than only the "
                   "traps, which is why its own cooldown is the longest in the "
                   "class."),

    # ---- Inquisition
    ability("smite_evil", "Smite Evil", "damage",
            "A flat, bright stroke that catches more than one of them.",
            ranks(40, 11, 25, start=6, count=8), target_type="enemy_aoe",
            damage_school="holy", max_targets=3, icon="ability_melee",
            source="CoA: 'Strike an enemy with your blade, dealing Weapon "
                   "Damage plus 25 as Holy damage to them and 5 nearby "
                   "enemies.' The spec's cheap cleaving filler; Flames of the "
                   "Sinned in the tree gives it a chance to strike twice."),
    ability("dusk_blade", "Dusk Blade", "damage_and_heal",
            "Both blades, and you keep some of what comes off them.",
            ranks(54, 15, 30, start=12, count=7), cooldown=2,
            target_type="enemy", damage_school="shadow", icon="ability_melee",
            source="CoA: 'Strike an enemy with both weapons, dealing Weapon "
                   "Damage plus shadow SP Shadow damage, piercing resistances. "
                   "Heals for 25% of damage dealt.' The spec's sustain - 'Dusk "
                   "Blade is your health siphon' and 'the payoff is... grinding "
                   "a fight out with Dusk Blade's siphon'."),
    ability("purifiers_edge", "Purifier's Edge", "damage",
            "The edges come up hot and stay that way.",
            ranks(56, 16, 30, start=16, count=7), cooldown=3,
            target_type="enemy", damage_school="fire", icon="ability_melee",
            source="CoA: 'Strike an enemy with searing blades, dealing Weapon "
                   "Damage plus 20 with both weapons as Fire damage. Grants "
                   "Flames of Sin or increases the duration by 3 sec.' Flames "
                   "of Sin is a stacking auto-attack rider with no engine "
                   "shape; the tree's Searing Hilt carries the attack-speed "
                   "half instead."),
    ability("torchlight", "Torchlight", "spell_damage",
            "Throw it and let it stick.",
            ranks(44, 13, 25, start=20, count=6), cooldown=2,
            target_type="enemy", damage_school="fire",
            source="CoA: 'Throw a torch at an enemy, dealing fire SP Fire "
                   "damage, and causing up to 5 of the next attacks you make "
                   "against them to grant you Flames of Sin.' spell_damage "
                   "because CoA gives it an SP coefficient and the spec's stat "
                   "priority puts Spell Power above Agility for exactly this "
                   "group of casts. Sinner and Dawn in the tree are its "
                   "payoff nodes."),
    ability("fiery_judgement", "Fiery Judgement", "spell_damage",
            "Say what they are, and let it catch.",
            ranks(40, 12, 30, start=26, count=5), cooldown=3,
            target_type="enemy_aoe", damage_school="fire", max_targets=4,
            source="CoA: 'Judge an enemy, dealing fire SP Fire damage to them "
                   "and nearby enemies.' The spell-power-scaled AoE half of "
                   "the fire kit; Cinder and Ashes raises its SP scaling."),
    ability("flourish", "Flourish", "damage",
            "A long, showy pass with both blades that happens to be the most "
            "efficient thing you could have done.",
            ranks(42, 12, 35, start=32, count=5), cooldown=6,
            target_type="enemy_aoe", damage_school="fire", max_targets=4,
            icon="ability_melee",
            source="CoA: 'Perform an advanced flourish, dealing AP Fire damage "
                   "to nearby enemies, repeating every 4 sec, and causing your "
                   "Flames of Sin to cleave up to 3 additional enemies for 20 "
                   "seconds.' The repeat and the Flames cleave have no hook; "
                   "the AoE strike does."),
    ability("hunt", "Hunt", "damage",
            "Close the gap before they have finished deciding to run.",
            ranks(44, 13, 20, start=24, count=5), cooldown=5,
            target_type="enemy", icon="ability_melee",
            source="CoA: 'Charge an enemy, slowing their movement speed by "
                   "-70% for 2 seconds and generating 20 Rage. 2 Charges, 25 "
                   "sec recharge.' Neither charges nor movement speed exist "
                   "here, so it is a cheap gap-closer on a real cooldown - and "
                   "the tree's The Hunt Continues carries the Focus generation "
                   "CoA puts on the ability itself."),
    ability("stake", "Stake", "damage",
            "You have been carrying this for exactly this moment.",
            ranks(92, 25, 30, start=36, count=4), cooldown=3,
            target_type="enemy", execute_threshold_pct=35,
            icon="ability_melee",
            source="CoA: 'Drive your concealed stake into the chest of an "
                   "injured enemy, dealing AP Physical damage... Only usable on "
                   "enemies at or below 35% health.' The spec's execute, at "
                   "CoA's own 35."),
    ability("darkslayers_lantern", "Darkslayer's Lantern", "debuff",
            "Open the shutter. Nothing in the light moves for a moment.",
            one(42, 35), cooldown=10, duration=1, target_type="enemy_aoe",
            is_stun=True, max_targets=5,
            source="CoA: 'Empower a lantern with your Flames of Sin and let it "
                   "shine, dealing AP Fire damage and stunning all enemies "
                   "within 5 yds for 5 seconds', described in the strengths as "
                   "'an AoE stun for locking down a pack'. A stun has to be a "
                   "debuff for is_stun to be read, so the Fire damage half is "
                   "dropped and the stun kept - the stun is what the rotation "
                   "presses it for."),
    ability("pyro_tonic", "Pyro Tonic", "buff",
            "It burns on the way down and keeps burning.",
            one(30, 20), cooldown=12, duration=3,
            stat_mods={"damage_dealt_pct": 20.0}, target_type="self",
            source="CoA: 'Drink a fiery tonic, increasing your Fire damage "
                   "dealt by 20% and your critical damage by 10% for 15 "
                   "seconds.' damage_dealt_pct is the engine's one generic "
                   "outgoing-damage buff key and it is PERCENT POINTS (divided "
                   "by 100 in _damage_multiplier), unlike the tree's fire "
                   "keys. There is no fire-only buff key - the per-school "
                   "damage keys are talent-only - so 20% lands on all of the "
                   "Inquisitor's damage rather than just the Fire half."),
    ability("monster_hunting", "Monster Hunting", "buff",
            "You have done this before and everyone can tell.",
            one(40, 25), cooldown=12, duration=4,
            stat_mods={"haste": 10.0}, target_type="party",
            buff_scope="combat",
            source="CoA: 'Increases melee and ranged haste of party and raid "
                   "members within 100 yds by 10%.' The raid buff the spec's "
                   "S-tier raid rating is partly sold on ('brings raid haste "
                   "(Monster Hunting)'). The '+10% damage against Undead and "
                   "Demons' half has no creature-type hook."),
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


# ============================================================== Boltslinger
B = "witch_hunter_boltslinger"
BOLTSLINGER = tree(
    B, "Witch Hunter Boltslinger",
    "Mobile crossbow skirmisher - builds into a charged Heartseeking Bolt and "
    "survives on avoidance rather than armour.",
    [
        node(B, "rapid_reload", "Rapid Reload",
             "Increases your haste by 2 per rank.",
             0, 0, 5, {"haste": 2.0},
             source="CoA: 'Increases your ranged haste by 8%.' ranged_haste is "
                    "dead - the engine has one haste stat - so it is plain "
                    "haste at the rate every shipped tree uses."),
        node(B, "mechanized_crossbows", "Mechanized Crossbows",
             "Grants ranged attack power equal to 3% of your Agility per rank.",
             0, 1, 5, {"ranged_ap_from_agility_pct": 0.03},
             source="CoA: 'Increases your ranged attack power by 10% and the "
                    "range of your ranged abilities by 5 yds.' A flat "
                    "ranged_attack_power grant is dead - the stat is computed "
                    "from Agility and Strength in _recalculate_derived_stats "
                    "and never reads the bonus pool - so this is a real "
                    "<target>_from_<source>_pct conversion off the spec's own "
                    "primary stat ('Agility (RAP/crit/dodge)'). Range is not "
                    "modelled."),
        node(B, "night_stalker", "Night Stalker",
             "Increases your critical strike chance by 1% per rank.",
             0, 2, 5, {"crit_chance_physical": 1.0},
             source="CoA class tree: 'Increases your critical strike chance by "
                    "3%.' Pulled into this tree because the spec's stat "
                    "priority says 'Critical Strike (Brimming Hatred/Lucky Shot "
                    "both key off crits for rage and armor-shred)'."),
        node(B, "my_trusty_arbalest", "My Trusty Arbalest",
             "Reduces the Focus cost of your abilities by 2% and grants 1 hit "
             "rating per rank.",
             0, 3, 5, {"all_ability_cost_pct": 0.02, "hit_rating": 1},
             source="CoA: 'Reduces the Rage cost of Witchbane and Shadowblast "
                    "by -10% and increases your chance to hit by 2%.' There is "
                    "no two-ability cost key, only per-ability and global, so "
                    "it discounts the whole book at a smaller rate. Hit leads "
                    "this spec's stat priority."),

        node(B, "heartless", "Heartless",
             "Increases your critical strike damage by 5% per rank.",
             1, 0, 3, {"crit_damage_physical": 0.05},
             connect=["rapid_reload"],
             source="CoA: 'Increases your Physical ranged critical damage by "
                    "15%.' No ranged-only crit damage key exists."),
        node(B, "enchanted_bolts", "Enchanted Bolts",
             "Increases your spell damage by 3% and your armor penetration by "
             "2% per rank.",
             1, 1, 3, {"spell_damage": 0.03, "armor_penetration_pct": 2.0},
             connect=["mechanized_crossbows"],
             source="CoA: 'Increases your Magic damage dealt by 5% and your "
                    "Armor penetration by 10%.' Both halves are real: "
                    "armor_penetration_pct is PERCENT POINTS (divided by 100 "
                    "in _recalculate_derived_stats) and is finally consumed in "
                    "take_damage's physical branch."),
        node(B, "crossbow_expert", "Crossbow Expert",
             "Increases the damage of Witchbane by 5% and Shadowblast by 4% "
             "per rank.",
             1, 2, 5, {"ability_witch_hunter_witchbane_damage": 0.05,
                       "ability_witch_hunter_shadowblast_damage": 0.04},
             connect=["night_stalker"],
             source="CoA: 'Increases the damage of Shadowblast by 10% and "
                    "Witchbane by 5%.' ability_<id>_damage keys are built by "
                    "string interpolation in abilities.py - a literal grep "
                    "calls them dead, which is why 48 of them were once "
                    "reported so."),
        node(B, "brimming_hatred", "Brimming Hatred",
             "Your critical strikes restore 10 Focus, no more than once per "
             "turn.",
             1, 3, 1, {}, connect=["my_trusty_arbalest"],
             proc={"trigger": "on_crit", "chance": 100, "icd": 1,
                   "grant_resource": {"resource": "focus", "amount": 10}},
             source="CoA class tree: 'Your critical strikes now generate 10 "
                    "Rage. Can only occur every 3 sec.' CoA's Rage is "
                    "Frontier's Focus for this class (module docstring), and "
                    "grant_resource is a real proc payload that goes through "
                    "the same gain_resource every builder ability uses. One "
                    "point, because a proc's numbers do not scale with ranks."),

        node(B, "one_shot", "One Shot",
             "Increases the critical strike chance of Heartseeking Bolt by 4% "
             "per rank.",
             2, 0, 3, {"ability_witch_hunter_heartseeking_bolt_crit": 4.0},
             connect=["heartless"],
             source="CoA: 'Increases the critical strike chance of Heartseeking "
                    "Bolt by 20%.' ability_<id>_crit is percentage points, the "
                    "same unit as crit_chance_physical."),
        node(B, "silver_bolts", "Silver Bolts",
             "Increases the damage of Heartseeking Bolt and Damnation by 5% "
             "per rank.",
             2, 1, 3, {"ability_witch_hunter_heartseeking_bolt_damage": 0.05,
                       "ability_witch_hunter_damnation_damage": 0.05},
             connect=["enchanted_bolts"],
             source="CoA: 'Damage dealt by Heartseeking Bolt and Damnation is "
                    "increased by 15%, doubled against Undead or Demons or "
                    "enemies affected by Shadow Trap.' No creature-type or "
                    "debuff-conditional damage hook, so the flat half only."),
        node(B, "strafing_shot", "Strafing Shot",
             "Increases the damage of your damage-over-time effects by 3% per "
             "rank.",
             2, 2, 3, {"dot_damage": 0.03}, connect=["crossbow_expert"],
             source="CoA: 'Critical strikes with ranged abilities now spread "
                    "Tormentor to a nearby enemy.' Spreading a DoT on crit has "
                    "no engine shape (a proc can apply a NEW effect but not "
                    "copy an existing one to another target), so the node pays "
                    "out as DoT damage instead - Tormentor and Witchbane are "
                    "both DoTs, which is what the spread was worth."),
        node(B, "bane_of_witches", "Bane of Witches",
             "Increases your physical damage by 2% per rank.",
             2, 3, 5, {"physical_damage": 0.02}, connect=["brimming_hatred"],
             source="CoA: 'Casting Heartseeking Bolt now increases your "
                    "Physical damage dealt by 10% for 8 seconds.' A "
                    "self-buff-on-cast proc would need an apply_effect keyed to "
                    "one ability; the rotation keeps Heartseeking Bolt on "
                    "cooldown anyway, so this is the passive version of the "
                    "same number."),

        node(B, "arbalest_mastery", "Arbalest Mastery",
             "Increases the damage of Witchbane by 6% per rank.",
             3, 0, 3, {"ability_witch_hunter_witchbane_damage": 0.06},
             connect=["one_shot"],
             source="CoA: 'Each subsequent shot of a Witchbane cast deals 15% "
                    "more damage, up to a maximum of 150%.' A ramping channel "
                    "is not expressible; the average is."),
        node(B, "resourceful_pursuit", "Resourceful Pursuit",
             "Reduces the Focus cost of Tormentor by 3 and Damnation by 3 per "
             "rank.",
             3, 1, 3, {"ability_witch_hunter_tormentor_cost": 3,
                       "ability_witch_hunter_damnation_cost": 3},
             connect=["silver_bolts"],
             source="CoA: 'Reduces the Rage cost of Tormentor and Damnation by "
                    "-20%.' ability_<id>_cost is a FLAT reduction applied "
                    "before the percentage one, so 3 a rank off a 25 and a 45 "
                    "cost lands near CoA's 20%."),
        node(B, "relentless", "Relentless",
             "Increases the damage your abilities deal to additional targets by "
             "6% per rank.",
             3, 2, 3, {"aoe_damage": 0.06}, connect=["strafing_shot"],
             source="CoA: 'Allows Witchbane to hit an additional nearby "
                    "enemy.' Adding a target to a specific ability is not a "
                    "talent shape - max_targets is authored on the ability - so "
                    "the node raises AoE damage. NOTE aoe_damage is only read "
                    "when target_type is 'enemy_aoe', which is why every AoE "
                    "ability in this class uses that rather than the is_aoe "
                    "field, which nothing reads."),
        node(B, "escape_artist", "Escape Artist",
             "Daring Escape lasts 1 turn longer and Vault's cooldown is "
             "reduced by 1 turn.",
             3, 3, 1, {"ability_witch_hunter_daring_escape_duration": 1,
                       "ability_witch_hunter_vault_cooldown": 1},
             connect=["bane_of_witches"],
             source="CoA: 'Your Daring Escape now resets the cooldown of Vault "
                    "and generates 10 Rage.' A cooldown RESET from one cast has "
                    "no talent shape, so the reset becomes a flat cooldown "
                    "reduction and the escape window gets longer."),

        node(B, "evasive", "Evasive",
             "Reduces all damage you take by 2% per rank.",
             4, 0, 3, {"damage_taken_pct": -0.02},
             connect=["arbalest_mastery"], total_slots=3,
             source="CoA: 'Twilight Frenzy now grants you -20% reduced damage "
                    "taken while active.' Conditioning it on one ability being "
                    "up is not expressible, so it is passive and much smaller."),
        node(B, "crossbow_frenzy", "Crossbow Frenzy",
             "Increases your chance to dodge by 1% and your haste by 1 per "
             "rank.",
             4, 1, 3, {"dodge": 1.0, "haste": 1.0},
             connect=["resourceful_pursuit"], total_slots=3,
             source="CoA: 'While Twilight Frenzy is active, your movement speed "
                    "is now increased by 40%.' Movement speed is not modelled; "
                    "what it bought this spec was not being hit, so the node "
                    "carries dodge."),
        node(B, "neverending_pursuit", "Neverending Pursuit",
             "Your critical strikes with Damnation restore 40 Focus.",
             4, 2, 1, {}, connect=["relentless"], total_slots=3,
             proc={"trigger": "on_crit", "chance": 100, "icd": 0,
                   "ability_filter": ["witch_hunter_damnation"],
                   "grant_resource": {"resource": "focus", "amount": 40}},
             source="CoA: 'Critically striking with Damnation now refunds 40 "
                    "Rage.' ability_filter narrows a proc to named abilities - "
                    "a real payload key, read off the authored trees - so this "
                    "is CoA's node exactly, Focus for Rage."),

        node(B, "contract_killing", "Contract Killing",
             "Increases all damage you deal by 3% per rank.",
             5, 0, 3, {"all_damage": 0.03}, connect=["evasive"],
             total_slots=3,
             source="CoA: 'Increases damage dealt against enemies above 75% "
                    "health and below 35% health by 15%.' There is no "
                    "health-banded damage key (low_health_* reads the CASTER's "
                    "health, not the target's), so it is flat."),
        node(B, "heavy_crossbows", "Heavy Crossbows",
             "Increases the damage of Darkslayer by 8% per rank.",
             5, 1, 3, {"ability_witch_hunter_darkslayer_damage": 0.08},
             connect=["neverending_pursuit"], total_slots=3,
             source="CoA: 'Increases the damage of Darkslayer by 50%, but "
                    "increases its cast time by 0.5 sec. Your Heartseeking Bolt "
                    "and Darkslayer now have a 25% chance to strike an "
                    "additional time.' Cast time does not exist in a turn "
                    "engine, so the drawback is gone and the bonus is "
                    "proportionally smaller."),
        node(B, "dead_and_gone", "Dead and Gone",
             "Pavise lasts 1 turn longer and its cooldown is reduced by 2 turns "
             "per rank.",
             5, 2, 2, {"ability_witch_hunter_pavise_duration": 1,
                       "ability_witch_hunter_pavise_cooldown": 2},
             connect=["crossbow_frenzy"], total_slots=3,
             source="CoA: 'Your Pavise now lasts 2 additional sec and has a -30 "
                    "sec reduced cooldown.'"),

        node(B, "bounty_hunter", "Bounty Hunter",
             "You have been building to one shot this whole time, and it lands "
             "where you meant it to.",
             6, 0, 1, {"ability_witch_hunter_heartseeking_bolt_damage": 0.30,
                       "crit_damage_physical": 0.15},
             node_type="active",
             connect=["contract_killing", "heavy_crossbows", "dead_and_gone"],
             total_slots=1,
             source="Capstone. CoA: 'Casting Darkslayer or Witchbane now "
                    "applies a stack of Bounty Hunter to you for 8 seconds, "
                    "which can be consumed by casting Heartseeking Bolt to deal "
                    "an additional ranged AP Physical damage, stacking 2 "
                    "times.' A build-and-consume stack counter has no engine "
                    "shape, so the two stacks' worth of bonus is baked into "
                    "Heartseeking Bolt directly."),
    ],
    "Built from reference/coa_sidekick/SPEC_witch-hunter__boltslinger.txt and "
    "the boltslinger spec tree in reference/coa_sidekick/talents/"
    "witch-hunter.json. CoA calls this 'an Outlaw/Survival hybrid built on real "
    "tools... a burst-window rogue crossed with a kiting hunter', and the tree "
    "follows its stat priority (Hit > Expertise > Agility > Armor Penetration > "
    "Crit > Haste) by spending real points on hit rating, Agility-to-ranged-AP "
    "and armour penetration rather than on raw attack power. Expertise has no "
    "key in this engine at all, which is the one priority entry nothing here "
    "can serve.")


# ============================================================== Houndmaster
H = "witch_hunter_houndmaster"
HOUNDMASTER = tree(
    H, "Witch Hunter Houndmaster",
    "Pet-centric ranged spec - fights two bodies at once, splits incoming "
    "damage across the hounds, and builds Focus off its own auto-attacks.",
    [
        node(H, "dark_ranger", "Dark Ranger",
             "Increases your hound's damage by 4% per rank.",
             0, 0, 5, {"pet_damage": 0.04},
             source="CoA: 'Increases the Shadow damage dealt by your Shadow "
                    "Hounds by 5%.' pet_damage is one of the three keys Pet "
                    "deliberately reads off its owner's talents when it is "
                    "built, and a FRACTION (0.06 is the shipped value in "
                    "Stormbringer Wind and Primalist Wildwalker)."),
        node(H, "expert_shot", "Expert Shot",
             "Increases the damage of Shadowblast by 5% and grants 1 hit rating "
             "per rank.",
             0, 1, 5, {"ability_witch_hunter_shadowblast_damage": 0.05,
                       "hit_rating": 1},
             source="CoA: 'Increases the damage of Shadowblast by 10% and your "
                    "hit chance by 2%.' Hit leads this spec's stat priority "
                    "too."),
        node(H, "houndfeeder", "Houndfeeder",
             "Increases your critical strike chance by 1% per rank.",
             0, 2, 5, {"crit_chance_physical": 1.0},
             source="CoA: 'Increases the critical strike chance of you and your "
                    "Shadow Hound by 4%.' A pet has its own crit_chance off its "
                    "template and there is no pet_crit key, so only the "
                    "owner's half is real."),
        node(H, "hail_of_gunfire", "Hail of Gunfire",
             "Increases your haste by 2 per rank.",
             0, 3, 5, {"haste": 2.0},
             source="CoA: 'Increases your ranged haste by 10%.' Same "
                    "ranged_haste gap as Boltslinger's Rapid Reload."),

        node(H, "kennel_master", "Kennel Master",
             "Increases your hound's health by 4% per rank.",
             1, 0, 5, {"pet_health": 0.04}, connect=["dark_ranger"],
             source="CoA: 'Casting Unleash The Hounds now has a 25% chance to "
                    "summon an additional Lesser Shadow Hound for 15 seconds.' "
                    "The engine keeps ONE pet, so a second hound is impossible; "
                    "what the extra body bought was more hound to go round, "
                    "which pet_health delivers honestly."),
        node(H, "silver_bullets", "Silver Bullets",
             "Increases the damage of Darkslayer by 6% per rank.",
             1, 1, 3, {"ability_witch_hunter_darkslayer_damage": 0.06},
             connect=["expert_shot"],
             source="CoA: 'Increases the damage of Darkslayer by 10%, increased "
                    "by an additional 10% against Undead.' No creature-type "
                    "hook, so the flat half only."),
        node(H, "darkrider", "Darkrider",
             "Reduces the Focus cost of your abilities by 3% per rank.",
             1, 2, 4, {"all_ability_cost_pct": 0.03}, connect=["houndfeeder"],
             source="CoA: 'Reduces the Rage cost of Shadowblast, Vault, and "
                    "Unleash the Hounds by -10.' Shadowblast and Vault are "
                    "already free in Frontier (they are the builders), so a "
                    "three-ability flat cut would mostly hit nothing - it "
                    "discounts the whole book instead."),
        node(H, "trapper", "Trapper",
             "Reduces the cooldown of Shadow Trap and Death Trap by 1 turn per "
             "rank.",
             1, 3, 3, {"ability_witch_hunter_shadow_trap_cooldown": 1,
                       "ability_witch_hunter_death_trap_cooldown": 1},
             connect=["hail_of_gunfire"],
             source="CoA: 'Reduces the cooldown of your Trap spells by -25%', "
                    "with the class tree's Three Sevens and Trap Card extending "
                    "them. Trap duration is not a thing - a Frontier trap is "
                    "cast, not placed - so only the cooldown half survives."),

        node(H, "loksey_journal", "Loksey's Journal",
             "Increases your hound's damage by 4% per rank.",
             2, 0, 3, {"pet_damage": 0.04}, connect=["kennel_master"],
             source="CoA: 'Increases the damage of Shadow Rage by 20% of your "
                    "ranged attack power.' Shadow Rage is a hound buff, so "
                    "scaling it is scaling the hound. A pet cannot read its "
                    "owner's attack power (Pet deliberately does not inherit "
                    "the owner's stats or gear), so this is flat pet damage."),
        node(H, "rampaging_hounds", "Rampaging Hounds",
             "Increases the damage your abilities deal to additional targets by "
             "6% per rank.",
             2, 1, 3, {"aoe_damage": 0.06}, connect=["silver_bullets"],
             source="CoA: 'Your Shadow Hounds melee attacks now cleave 1 "
                    "additional nearby enemy.' A pet's targeting is not "
                    "talentable, so the cleave lands on the Houndmaster's own "
                    "AoE."),
        node(H, "defender_of_darkshire", "Defender of Darkshire",
             "Increases your hound's armor by 5% per rank.",
             2, 2, 3, {"pet_armor": 0.05}, connect=["darkrider"],
             source="CoA: 'Critical strikes with ranged auto attacks now "
                    "increase the melee haste of your Shadow Hounds by 10% for "
                    "5 seconds.' There is no pet_haste key, and the spec's "
                    "whole premise is splitting damage across hounds, so the "
                    "third live pet key carries this node instead."),
        node(H, "scent_of_magic", "Scent of Magic",
             "Reduces the cooldown of Houndmaster's Call by 1 turn per rank.",
             2, 3, 2, {"ability_witch_hunter_houndmasters_call_cooldown": 1},
             connect=["trapper"],
             source="CoA: 'Critical strikes now apply Scent of Magic for 15 "
                    "seconds, causing your Shadow Hound's next Shadow Leap to "
                    "incur a -10 sec reduced cooldown.' Houndmaster's Call is "
                    "Frontier's version of the hound leap, so the reduction "
                    "lands there."),

        node(H, "decimate", "Decimate",
             "Increases your hound's damage by 4% per rank.",
             3, 0, 3, {"pet_damage": 0.04}, connect=["loksey_journal"],
             source="CoA: 'Empowers your Shadow Hounds for 20 seconds, granting "
                    "them 30% increased damage and haste and allowing them to "
                    "ignore Armor.' The ABILITY of the same name keeps the "
                    "Houndmaster's burst window; this node is the permanent "
                    "hound damage, which is the only half a pet can receive."),
        node(H, "pure_agony", "Pure Agony",
             "Increases the critical strike damage of Quickdraw by 8% per rank.",
             3, 1, 3, {"ability_witch_hunter_quickdraw_crit_damage": 0.08},
             connect=["rampaging_hounds"],
             source="CoA: 'Increases the critical damage of Quickdraw by 50%.' "
                    "ability_<id>_crit_damage is a real per-ability key, read "
                    "in _crit_damage_bonus."),
        node(H, "reload", "Reload",
             "Reduces the cooldown of Quickdraw by 1 turn.",
             3, 2, 1, {"ability_witch_hunter_quickdraw_cooldown": 1},
             connect=["defender_of_darkshire"],
             source="CoA: 'Reduces the cooldown of Quickdraw by -4 sec.' "
                    "Quickdraw is a 2-turn cooldown, and talented_cooldown "
                    "floors at 1, so one rank is all there is room for."),
        node(H, "anguish", "Anguish",
             "Increases your Shadow spell damage by 3% per rank.",
             3, 3, 3, {"shadow_spell_damage": 0.03}, connect=["scent_of_magic"],
             source="CoA: 'Your Shadow damage dealt now has a 5% chance to "
                    "reduce the channel time of your next Darkflock by -50%.' "
                    "Channel time is not modelled; Darkflock is the spec's one "
                    "spell-power cast, so the node raises the school it deals "
                    "in. shadow_spell_damage is built at runtime as "
                    "f'{school}_spell_damage' - another family a literal scan "
                    "would call dead."),

        node(H, "shadewalker", "Shadewalker",
             "Grants attack power equal to 3% of your Intellect per rank.",
             4, 0, 3, {"ap_from_intellect_pct": 0.03}, connect=["decimate"],
             total_slots=3,
             source="CoA stat priority: 'Intellect (Shadewalker converts Int "
                    "into AP and Dark Mind converts Int into crit rating)'. A "
                    "real conversion, resolved against the shared "
                    "STAT_CONVERSION maps in character.py. No other ranged spec "
                    "in the game wants Intellect; these two nodes are why this "
                    "one does."),
        node(H, "dark_mind", "Dark Mind",
             "Grants critical strike chance equal to 2% of your Intellect per "
             "rank.",
             4, 1, 3, {"crit_from_intellect_pct": 0.02},
             connect=["pure_agony"], total_slots=3,
             source="CoA: 'Increases your critical strike rating by 25% of your "
                    "Intellect.' The other half of the Intellect pair."),
        node(H, "daredevil", "Daredevil",
             "While below 35% health, you take 6% less damage per rank.",
             4, 2, 3, {"low_health_damage_reduction_pct": 0.06,
                       "low_health_threshold_pct": 0.35},
             connect=["anguish"], total_slots=3,
             source="CoA: 'When you take damage that would reduce your health "
                    "to 35% or less, you summon 3 lesser Shadow Hounds and "
                    "reset the cooldown of Vault', described as 'the main safety "
                    "net' and 'the emergency bail-out'. Neither the extra hounds "
                    "nor the reset is expressible, so the engine's own "
                    "low-health mitigation pair carries it - at CoA's own 35% "
                    "threshold."),

        node(H, "lethal_pursuit", "Lethal Pursuit",
             "Increases your hound's damage by 4% per rank.",
             5, 0, 3, {"pet_damage": 0.04}, connect=["shadewalker"],
             total_slots=3,
             source="CoA: 'Shadow Rage now also grants your Shadow Hounds 10% "
                    "increased haste and it now stacks 3 additional times.' "
                    "pet_haste does not exist; stacking does not either. The "
                    "throughput does."),
        node(H, "veiled_in_darkness", "Veiled in Darkness",
             "Increases your attack power by 3% per rank.",
             5, 1, 3, {"attack_power_pct": 3.0}, connect=["dark_mind"],
             total_slots=3,
             source="CoA: 'A veil of dark magic encircles you at all times, "
                    "granting 5% increased Attack Power to party and raid "
                    "members within 100 yds', which is what the spec's raid "
                    "rating is sold on. A talent cannot grant a party aura - "
                    "talent effects only ever apply to their own character - so "
                    "the Houndmaster keeps it. The real party-facing buffs in "
                    "this class are abilities (Slayer, Monster Hunting)."),
        node(H, "expulsion_of_evil", "Expulsion of Evil",
             "Your ranged attacks have a 15% chance to reset the cooldown of "
             "Houndmaster's Call.",
             5, 2, 1, {}, connect=["daredevil"], total_slots=3,
             proc={"trigger": "on_damage_cast", "chance": 15, "icd": 1,
                   "reset_cooldown": {"ability_id": "witch_hunter_houndmasters_call"}},
             source="CoA: 'Direct ranged attacks and abilities now have a 5% "
                    "chance to reset the cooldown of Houndmaster's Call.' "
                    "reset_cooldown IS a real proc payload - the one cooldown "
                    "reset the engine can actually do - so this node is CoA's "
                    "exactly, at a higher chance because a turn is longer than "
                    "a cast."),

        node(H, "deal_with_the_devil", "Deal With the Devil",
             "Everything you and the hounds land hits harder, and everything "
             "costs more.",
             6, 0, 1, {"crit_damage_physical": 0.20, "crit_damage_spell": 0.20,
                       "pet_damage": 0.15, "all_ability_cost_pct": 0.10},
             node_type="active",
             connect=["lethal_pursuit", "veiled_in_darkness",
                      "expulsion_of_evil"],
             total_slots=1,
             source="Capstone. CoA: 'Your and your Shadow Hounds critical "
                    "damage dealt with Shadow damage is increased by 50%, but "
                    "the cost of your spells and abilities is increased by "
                    "25%.' The real drawback is kept - all_ability_cost_pct "
                    "POSITIVE is a cost increase, and it is the only node in "
                    "this class that charges you for itself."),
    ],
    "Built from reference/coa_sidekick/SPEC_witch-hunter__houndmaster.txt and "
    "the houndmaster spec tree in reference/coa_sidekick/talents/"
    "witch-hunter.json. CoA calls it 'a Survival-Hunter chassis with a heavier "
    "pet emphasis'. THE STRUCTURAL LIMIT on this spec: CoA's hound stack is a "
    "permanent Shadowhound plus temporary lesser hounds from Unleash the "
    "Hounds, Kennel Master and Daredevil, and Frontier keeps exactly ONE active "
    "pet - a second summon replaces the first. So every 'more hounds' talent is "
    "redirected into the three pet keys the engine really reads (pet_damage, "
    "pet_health, pet_armor), which makes this one strong hound rather than a "
    "pack. The Intellect nodes are not decoration: CoA's stat priority puts "
    "Intellect fourth, above Spell Power, because Shadewalker and Dark Mind "
    "both convert it.")


# ============================================================= Black Knight
K = "witch_hunter_black_knight"
BLACK_KNIGHT = tree(
    K, "Witch Hunter Black Knight",
    "Avoidance tank - parry is its mitigation, its damage and its healing all "
    "at once, because Noctis Blade scales off it.",
    [
        node(K, "dark_penance", "Dark Penance",
             "Increases your Agility by 2% and your chance to parry and dodge "
             "by 1% per rank.",
             0, 0, 5, {"agility_pct": 2.0, "parry": 1.0, "dodge": 1.0},
             source="CoA: 'Increases your Agility and your chance to parry and "
                    "dodge by 2%.' Both parry and dodge are real full-avoidance "
                    "stats here, additive off the same bonus pool as gear."),
        node(K, "shadow_order", "Shadow Order",
             "Increases the damage of Shadow Brand by 8% and grants 1 hit "
             "rating per rank.",
             0, 1, 5, {"ability_witch_hunter_shadow_brand_damage": 0.08,
                       "hit_rating": 1},
             source="CoA: 'Increases the damage of Shadow Brand by 20% and your "
                    "hit rating by 3% of your Agility.' hit_rating is a local "
                    "feeding base_miss_chance_*, not a Character attribute, so "
                    "it cannot be a <target>_from_<source>_pct conversion "
                    "target - the same wall Guardian's Bulwark hit. Flat hit "
                    "rating instead, which is what this spec's stat priority "
                    "leads with anyway."),
        node(K, "dark_chivalry", "Dark Chivalry",
             "Increases your Armor by 3% per rank.",
             0, 2, 5, {"armor_pct": 3.0},
             source="CoA: 'Increases your Armor contribution from mail items by "
                    "100%', which the class page calls 'doubled mail armor'. "
                    "There is no armor-from-mail key (armor_multiplier exists "
                    "only in loot_generator and is never read as a talent), so "
                    "it is flat Armor percent. NOTE armor_pct is PERCENT POINTS "
                    "(3.0 = +3%), unlike max_health_pct below."),
        node(K, "wide_swings", "Wide Swings",
             "Increases the damage of Noctis Blade by 6% per rank.",
             0, 3, 5, {"ability_witch_hunter_noctis_blade_damage": 0.06},
             source="CoA: 'Increases the damage of Noctis Blade and Grasp of "
                    "the Undying by 20% on enemies affected by Shadow Brand.' "
                    "No debuff-conditional hook, so flat - and since Noctis "
                    "Blade is damage_and_heal, every point here also raises the "
                    "self-heal."),

        node(K, "dusk_knight", "Dusk Knight",
             "Grants parry equal to 3% of your Agility and dodge equal to 2% of "
             "your Intellect per rank.",
             1, 0, 5, {"parry_from_agility_pct": 0.03,
                       "dodge_from_intellect_pct": 0.02},
             connect=["dark_penance"],
             source="CoA level-20 passive: 'Increases your parry rating by 40% "
                    "of your Agility and your dodge rating by 25% of your "
                    "Intellect.' Two real conversions, both pairings valid "
                    "against STAT_CONVERSION_TARGETS/SOURCES. This is the "
                    "single most important node in the tree: CoA's stat "
                    "priority says parry rating 'scales Noctis Blade's damage "
                    "AND its 150%-of-damage self-heal', so parry is this spec's "
                    "offence, sustain and mitigation at once."),
        node(K, "dark_power", "Dark Power",
             "Increases your Stamina by 2% and reduces the chance you are "
             "critically hit by 1% per rank.",
             1, 1, 5, {"stamina_pct": 2.0, "crit_taken_reduction": 1.0},
             connect=["shadow_order"],
             source="CoA level-30 passive: 'You now gain 1 Stamina for every 2 "
                    "Agility.' stamina_from_agility_pct is DEAD - "
                    "STAT_CONVERSION_TARGETS has no stamina entry, so the "
                    "pairing fails silently - hence flat stamina_pct. The "
                    "crit-taken reduction rides here because every tank tree "
                    "needs a path to crit immunity and this is the tree's one "
                    "survivability-stat node; CoA's own stat priority opens "
                    "with the hit and expertise caps rather than Defense, so "
                    "there is no better home for it."),
        node(K, "no_regrets", "No Regrets",
             "Increases your Armor by 3%, your chance to block by 2%, and the "
             "damage your blocks absorb by 4% per rank.",
             1, 2, 3, {"armor_pct": 3.0, "block": 2.0, "block_value_pct": 0.04},
             connect=["dark_chivalry"],
             source="CoA: 'Your March of the Black King now increases your "
                    "Armor by 15%.' Conditioning Armor on a cooldown being up "
                    "is not expressible, so it is passive. Block comes with it "
                    "because weapon_types.json gives Witch Hunter shields, and "
                    "BLOCK IS TWO STATS: `block` is the shield-gated CHANCE in "
                    "percentage points (it stays 0 with no shield equipped) and "
                    "block_value_pct is a FRACTION scaling how much a blocked "
                    "hit loses. This is the tree's only block node, because "
                    "CoA's Black Knight is a two-hander spec and block is "
                    "Frontier's addition, not CoA's."),
        node(K, "secret_society", "Secret Society",
             "Increases your Shadow spell damage by 3% and your spell critical "
             "strike chance by 1% per rank.",
             1, 3, 3, {"shadow_spell_damage": 0.03, "crit_chance_spell": 1.0},
             connect=["wide_swings"],
             source="CoA: 'Increases your Shadow critical strike chance and "
                    "Shadow damage dealt by 4% and your expertise by 5.' "
                    "Expertise has no key in this engine; the Shadow halves are "
                    "both real."),

        node(K, "dark_riposte", "Dark Riposte",
             "Blows you turn aside knit you back together and return 10 Focus.",
             2, 0, 1, {}, connect=["dusk_knight"],
             proc={"trigger": "on_parry", "chance": 100, "icd": 0,
                   "heal_flat": 60,
                   "grant_resource": {"resource": "focus", "amount": 10}},
             source="CoA: 'Parrying enemy attacks now restores 5% of your "
                    "missing health and Rage.' on_parry is a real trigger "
                    "(Character.take_damage fires ('on_parry', 'on_avoid') off "
                    "its avoidance roll), so this is CoA's node literally - "
                    "every parry, not a chance on every hit. The 5%-of-missing "
                    "shape has no payload key, so it is a flat heal plus a flat "
                    "Focus grant. The Focus half matters: this is the tank's "
                    "second income stream alongside March of the Black King, "
                    "and it keys off the stat the whole spec already gears "
                    "for."),
        node(K, "clinch_fighting", "Clinch Fighting",
             "While below 35% health, you take 6% less damage per rank.",
             2, 1, 3, {"low_health_damage_reduction_pct": 0.06,
                       "low_health_threshold_pct": 0.35},
             connect=["dark_power"],
             source="CoA: 'Attacks which would otherwise kill you now heal you "
                    "for 50% maximum health and increases the damage of Noctis "
                    "Blade by 50% for 6 seconds.' A cheat-death has no engine "
                    "hook; the low-health mitigation pair is the honest version "
                    "of surviving the hit that was going to land."),
        node(K, "bulwark_of_darkness", "Bulwark of Darkness",
             "Increases the damage of Dawn Blade by 6% per rank.",
             2, 2, 4, {"ability_witch_hunter_dawn_blade_damage": 0.06},
             connect=["no_regrets"],
             source="CoA: 'Damage dealt by Dawn Blade is now increased by 5% "
                    "for each stack of Pommel Smash on the target.' Stack "
                    "counting is not expressible, so the flat equivalent."),
        node(K, "destroyer_of_evil", "Destroyer of Evil",
             "Increases the damage of your Shadow damage-over-time effects by "
             "4% per rank.",
             2, 3, 3, {"shadow_dot_damage": 0.04}, connect=["secret_society"],
             source="CoA: 'Damage dealt by Dawn Blade now deals an additional "
                    "20% of the damage dealt as Twilight Damage every 1 sec for "
                    "3 seconds.' Appending a DoT to another ability's hit is "
                    "what applies_dot_pct does on an ABILITY, not a talent, so "
                    "the node scales the Shadow DoTs the spec already has "
                    "(Shadow Brand, Knight's Seal, Death Trap). "
                    "<school>_dot_damage is built at runtime in "
                    "_damage_multiplier."),

        node(K, "guardbreaker", "Guardbreaker",
             "Increases the damage your abilities deal to additional targets by "
             "8% per rank.",
             3, 0, 3, {"aoe_damage": 0.08}, connect=["dark_riposte"],
             source="CoA: 'Your Pommel Smash now strikes an additional nearby "
                    "enemy.' Target counts live on the ability, not the talent, "
                    "so this raises what Desecrate and Witchblight do to the "
                    "pack - which is what this spec's dungeon rating is built "
                    "on ('AoE pulls and threat')."),
        node(K, "undying", "Undying",
             "Increases the critical strike chance of Noctis Blade by 4% per "
             "rank.",
             3, 1, 3, {"ability_witch_hunter_noctis_blade_crit": 4.0},
             connect=["clinch_fighting"],
             source="CoA: 'While below 75% maximum health, Dawn Blade now "
                    "increases the critical strike chance of Noctis Blade by "
                    "40% for 10 seconds.' The condition and the chain have no "
                    "hooks; the crit does, and a bigger Noctis Blade crit is "
                    "also a bigger heal."),
        node(K, "dark_barrier", "Dark Barrier",
             "Stoicism lasts 1 turn longer per rank.",
             3, 2, 2, {"ability_witch_hunter_stoicism_duration": 1},
             connect=["bulwark_of_darkness"],
             source="CoA: 'Increases the duration of Stoicism by 5 sec.'"),
        node(K, "foresight", "Foresight",
             "Increases the critical strike chance of Dawn Blade by 4% per "
             "rank.",
             3, 3, 3, {"ability_witch_hunter_dawn_blade_crit": 4.0},
             connect=["destroyer_of_evil"],
             source="CoA: 'Your direct Physical critical strikes now grant "
                    "allies Replenishment... In addition, Dawn Blade is now "
                    "guaranteed to critically strike against Undead or Demons.' "
                    "The ally mana regen cannot be granted by a talent (talent "
                    "effects never leave their own character) and mp5 would do "
                    "nothing for a class with no Mana pool, so what survives is "
                    "the guaranteed-crit half, as a real crit chance on Dawn "
                    "Blade. CoA sells the spec's raid rating on this node "
                    "('brings mana replenish (Foresight)'), so it is the "
                    "biggest party-facing loss in the tree."),

        node(K, "witch_knight", "Witch Knight",
             "Increases your Shadow resistance by 2% and your haste by 1 per "
             "rank.",
             4, 0, 3, {"shadow_resist_pct": 0.02, "haste": 1.0},
             connect=["guardbreaker"], total_slots=3,
             source="CoA: 'Direct ability damage with a two-handed weapon now "
                    "reduces the remaining cooldown of your Tonics by -1 sec "
                    "and grants Witching. Witching: increases magic resistances "
                    "by 10%, and melee haste by 10% for 8 seconds, stacking 3 "
                    "times.' Both halves of Witching are real keys; the stacking "
                    "and the tonic-cooldown rider are not. Frontier also gives "
                    "Witch Hunter no two-handed proficiency at all "
                    "(weapon_types.json: sword_1h, axe_1h, thrown, shield, gun, "
                    "crossbow), so CoA's whole two-hander framing for this spec "
                    "is gone - it is a one-hand-and-shield tank here."),
        node(K, "night_king", "Night King",
             "Increases the damage of Noctis Blade by 6% per rank.",
             4, 1, 3, {"ability_witch_hunter_noctis_blade_damage": 0.06},
             connect=["undying"], total_slots=3,
             source="CoA: 'Noctis Blade now consumes Shadow Brand to deal 50% "
                    "increased damage.' Consuming a debuff for a bonus is not "
                    "expressible; the bonus is."),
        node(K, "dark_juggernaut", "Dark Juggernaut",
             "Increases your threat generation by 6% per rank.",
             4, 2, 3, {"threat_generation_pct": 0.06}, connect=["dark_barrier"],
             total_slots=3,
             source="CoA: 'Desecrate now restores shadow AP health plus an "
                    "additional 1% maximum health for each target struck "
                    "affected by Shadow Brand.' Per-target conditional "
                    "self-healing has no hook, and this tree had no threat node "
                    "at all, which a main tank cannot ship without. NOTE the "
                    "key: threat_generation_pct as a TALENT effect is a "
                    "FRACTION (0.06), while the same name in an ability's "
                    "stat_mods is PERCENT POINTS (180, 200 - see Shadow Brand "
                    "and Chains of Darkness above)."),

        node(K, "shadowstorm", "Shadowstorm",
             "Increases your Shadow spell damage by 3% per rank.",
             5, 0, 3, {"shadow_spell_damage": 0.03}, connect=["witch_knight"],
             total_slots=3,
             source="CoA: 'Damage dealt by Pommel Smash now has a 20% chance to "
                    "trigger a Shadowstorm. Shadowstorm: leeches AP health from "
                    "enemies within 8 yds.' A chained AoE leech is not a proc "
                    "payload shape; the school it deals in is real."),
        node(K, "blade_of_the_misbegotten", "Blade of the Misbegotten",
             "Increases your total health by 2% per rank.",
             5, 1, 2, {"max_health_pct": 0.02}, connect=["night_king"],
             total_slots=3,
             source="CoA: 'Damage dealt by Dawn Blade now increases your health "
                    "by 15% of the damage dealt for 8 seconds, stacking 3 "
                    "times.' A stacking temporary health pool is not "
                    "expressible. NOTE max_health_pct is a FRACTION - health * "
                    "(1.0 + value) - not percent points like armor_pct. "
                    "Guardian shipped it at 2.0 (+200% a rank), reached 26,700 "
                    "health and 99,156 effective HP against the next tank's "
                    "2,987, and validate_class.py passed it with zero errors "
                    "before the magnitude check existed."),
        node(K, "dark_intuition", "Dark Intuition",
             "Turning an attack aside sharpens you: your parry rises by 4% and "
             "your haste by 4 for a few turns.",
             5, 2, 1, {}, connect=["dark_juggernaut"], total_slots=3,
             proc={"trigger": "on_avoid", "chance": 100, "icd": 0,
                   "apply_effect": {
                       "effect_id": "witch_hunter_dark_intuition",
                       "name": "Dark Intuition",
                       "effect_type": "buff",
                       "duration": 3,
                       "stat_mods": {"parry": 4.0, "haste": 4.0},
                       "on_target": False}},
             source="CoA class tree: 'Whenever you parry or dodge an attack, "
                    "your attack speed is increased by 5%, and your parry "
                    "chance by 2% for 15 seconds, stacking 2 times.' on_avoid "
                    "is exactly 'parry or dodge' - the trigger fires from both "
                    "branches of take_damage's avoidance roll - so this node is "
                    "CoA's wording with nothing approximated except the stack "
                    "count, which is folded into one larger application. It "
                    "replaces Secret of Raven Hill, the one Black Knight talent "
                    "CoA prints no tooltip for at all ('see builder tooltip'), "
                    "because a real avoidance payoff is the heart of a spec CoA "
                    "calls 'a sticky avoidance tank'."),

        node(K, "gaze_of_the_black_knight", "Gaze of the Black Knight",
             "You take the attention and the damage both, and you keep "
             "standing.",
             6, 0, 1, {"damage_taken_pct": -0.12, "threat_generation_pct": 0.15},
             node_type="active",
             connect=["shadowstorm", "blade_of_the_misbegotten",
                      "dark_intuition"],
             total_slots=1,
             source="Capstone, sharing its name with the ABILITY of the same "
                    "name - CoA's capstone IS that spell, and Frontier needs it "
                    "castable, so the ability carries the absorb and the node "
                    "carries the permanent version of what the gaze was for. "
                    "CoA: Black Knight is 'a solid main-tank for raid bosses' "
                    "with 'high throughput ceiling'.")
    ],
    "Built from reference/coa_sidekick/SPEC_witch-hunter__black-knight.txt and "
    "the black-knight spec tree in reference/coa_sidekick/talents/"
    "witch-hunter.json. CoA: 'It plays like a sticky avoidance tank rather than "
    "an anti-caster bruiser.' The tree spends far more on parry and dodge than "
    "on block because its stat priority reads Hit > Expertise > Agility > PARRY "
    "RATING > Armor Penetration > Crit > Haste, and parry there is explicitly "
    "an offensive and healing stat as well as an avoidance one. Block appears "
    "only twice, because Frontier gives this class a shield even though CoA's "
    "Black Knight is a two-hander spec - the reverse of Guardian, whose whole "
    "chassis is block. TWO THINGS DO NOT SURVIVE TRANSLATION: Guard Strike's "
    "interrupt and school lockout, which CoA calls 'the kit's only caster "
    "answer', and Gaze of the Black Knight's party damage redirection. Neither "
    "has an engine hook, and both are called out on their own abilities.")


# =============================================================== Inquisition
Q = "witch_hunter_inquisition"
INQUISITION = tree(
    Q, "Witch Hunter Inquisition",
    "Build-and-spend fire and shadow melee - layers stacks like a combo-point "
    "class and grinds fights out on Dusk Blade's siphon.",
    [
        node(Q, "flexible_fighter", "Flexible Fighter",
             "Increases your Agility by 2% per rank.",
             0, 0, 5, {"agility_pct": 2.0},
             source="CoA: 'Increases your Agility by 6%.'"),
        node(Q, "brooding_hatred", "Brooding Hatred",
             "Increases your physical damage by 2% and grants 1 hit rating per "
             "rank.",
             0, 1, 5, {"physical_damage": 0.02, "hit_rating": 1},
             source="CoA: 'Increases your off-hand Weapon Damage by 20% and "
                    "increases your chance to hit by 3%.' Off-hand damage is "
                    "not separately talentable - get_weapon_damage_roll applies "
                    "a fixed 50% off-hand penalty - so it lands as physical "
                    "damage. CoA's stat priority opens with 'Hit (both the "
                    "melee special-attack hit cap and the spell hit cap)'."),
        node(Q, "sermon_of_flame", "Sermon of Flame",
             "Increases your Fire spell damage by 3% per rank.",
             0, 2, 5, {"fire_spell_damage": 0.03},
             source="CoA: 'Increases your Fire damage dealt by 5%.' "
                    "fire_spell_damage is assembled at runtime as "
                    "f'{school}_spell_damage' and read for every ability whose "
                    "damage_school is fire - which in this spec is most of "
                    "them."),
        node(Q, "refined_combatant", "Refined Combatant",
             "Increases your critical strike chance by 1% per rank.",
             0, 3, 5, {"crit_chance_physical": 1.0},
             source="CoA: 'Increases your expertise by 10.' Expertise has no "
                    "key in this engine at all - no attribute, no bonus-pool "
                    "entry, nothing reading it - so the node carries the crit "
                    "that sits next to it in the same stat priority. This is "
                    "the one priority entry no spec in this class can serve."),

        node(Q, "protector_of_darkshire", "Protector of Darkshire",
             "Increases the damage of Dawn Blade and Dusk Blade by 5% per rank.",
             1, 0, 5, {"ability_witch_hunter_dawn_blade_damage": 0.05,
                       "ability_witch_hunter_dusk_blade_damage": 0.05},
             connect=["flexible_fighter"],
             source="CoA: 'Increases the damage of Dawn Blade and Dusk Blade by "
                    "15%.' Dusk Blade is damage_and_heal, so every point here "
                    "also raises the siphon the spec lives on."),
        node(Q, "malice", "Malice",
             "Grants spell damage equal to 3% of your Agility per rank.",
             1, 1, 3, {"spell_damage_from_agility_pct": 0.03},
             connect=["brooding_hatred"],
             source="CoA level-30 passive: 'Increases your Fire spell damage by "
                    "50% of your Agility and your attack power by 100% of your "
                    "Intellect.' A real conversion, and the reason this melee "
                    "spec's Fire casts scale at all - CoA's stat priority puts "
                    "Spell Power above Agility because 'Fiery Judgment, Dawn "
                    "Blade, Searing Blade, Burning Light and Interrogate all "
                    "carry an SP coefficient equal to or larger than their AP "
                    "coefficient'."),
        node(Q, "holy_frenzy", "Holy Frenzy",
             "Increases your haste by 2 per rank.",
             1, 2, 3, {"haste": 2.0}, connect=["sermon_of_flame"],
             source="CoA: 'Increases your melee haste by 15%.' melee_haste is "
                    "dead; the engine has one haste."),
        node(Q, "interrogator", "Interrogator",
             "Increases the damage of your Fire damage-over-time effects by 4% "
             "per rank.",
             1, 3, 3, {"fire_dot_damage": 0.04}, connect=["refined_combatant"],
             source="CoA level-20 passive: 'Damage dealt by Dawn Blade now "
                    "deals an additional 100% of the damage dealt over 10 "
                    "seconds as Fire damage.' Appending a DoT to another "
                    "ability's hit is applies_dot_pct on an ABILITY, not a "
                    "talent key, so the node scales Fire DoTs instead. "
                    "fire_dot_damage is built at runtime as "
                    "f'{real}_dot_damage' in _damage_multiplier."),

        node(Q, "dawn", "Dawn",
             "Increases the damage of Torchlight by 8% per rank.",
             2, 0, 3, {"ability_witch_hunter_torchlight_damage": 0.08},
             connect=["protector_of_darkshire"],
             source="CoA: 'Dealing Fire damage now increases the damage dealt "
                    "by Torchlight and Dusk Blade by 2% for 5 seconds, stacking "
                    "10 times.' The stack counter is not expressible; the "
                    "ten-stack payoff is, flattened onto the ability the "
                    "rotation spends it on."),
        node(Q, "dusk", "Dusk",
             "Increases the damage of Stake by 8% per rank.",
             2, 1, 3, {"ability_witch_hunter_stake_damage": 0.08},
             connect=["malice"],
             source="CoA: 'Dealing Physical damage now increases the damage "
                    "dealt by Stake and Dawn Blade by 2% for 5 seconds, "
                    "stacking 10 times.' The Dawn/Dusk pair is CoA's "
                    "combo-point layer and the reason the spec is called "
                    "build-and-spend; both nodes keep the name and the payoff "
                    "target."),
        node(Q, "searing_hilt", "Searing Hilt",
             "Increases your haste by 1 and your physical damage by 2% per "
             "rank.",
             2, 2, 3, {"haste": 1.0, "physical_damage": 0.02},
             connect=["holy_frenzy"],
             source="CoA: 'Purifier's Edge now grants you Searing Hilt for 10 "
                    "seconds. Searing Hilt: increases your melee attack speed "
                    "by 10% for 10 seconds.' An on-cast self-buff keyed to one "
                    "ability is not a talent shape; the rotation keeps "
                    "Purifier's Edge on cooldown, so it is passive."),
        node(Q, "cinder_and_ashes", "Cinder and Ashes",
             "Increases your Fire spell damage by 3% per rank.",
             2, 3, 3, {"fire_spell_damage": 0.03}, connect=["interrogator"],
             source="CoA: 'Increases the spell power scaling of Purifier's Edge "
                    "and Fiery Judgement by 25%.' Per-ability spell-power "
                    "coefficients are not talentable - the scaling is baked into "
                    "the effect_type - so it raises the school both abilities "
                    "deal in."),

        node(Q, "sinner", "Sinner",
             "Increases the damage of Torchlight by 10% per rank.",
             3, 0, 3, {"ability_witch_hunter_torchlight_damage": 0.10},
             connect=["dawn"],
             source="CoA: 'Increases the damage of Torchlight by 100%.' Halved "
                    "and spread across ranks, because Frontier's talents are "
                    "per-rank and a doubling in one node has no precedent in "
                    "any shipped tree."),
        node(Q, "duskwood_renegade", "Duskwood Renegade",
             "Reduces the cooldown of Burrow Bolt by 1 turn per rank.",
             3, 1, 2, {"ability_witch_hunter_burrow_bolt_cooldown": 1},
             connect=["dusk"],
             source="CoA: 'Reduces the cooldown of Burrow Bolt by -5 sec.' One "
                    "of the two gap-closers CoA says this spec needs to stay on "
                    "a kiter."),
        node(Q, "flames_of_the_sinned", "Flames of the Sinned",
             "Smite Evil has a 25% chance to strike again for an additional 30% "
             "damage.",
             3, 2, 1, {}, connect=["searing_hilt"],
             proc={"trigger": "on_damage_cast", "chance": 25, "icd": 0,
                   "ability_filter": ["witch_hunter_smite_evil"],
                   "bonus_pct": 0.30},
             source="CoA: 'Your Smite Evil now has a 25% chance to strike "
                    "again. While you have Flames of Sin active, the chance to "
                    "trigger this effect is increased by 10%.' bonus_pct adds "
                    "to the same hit that triggered it, which is what a 'strike "
                    "again' really is here; the Flames of Sin conditional half "
                    "has no hook."),
        node(Q, "sin_eater", "Sin Eater",
             "Increases the damage of Purifier's Edge by 6% per rank.",
             3, 3, 4, {"ability_witch_hunter_purifiers_edge_damage": 0.06},
             connect=["cinder_and_ashes"],
             source="CoA: 'Increases the amount of next attacks that grant "
                    "Flames of Sin through Torchlight by 5.' Flames of Sin is a "
                    "stacking auto-attack rider with no engine shape, so the "
                    "node pays out on the fire strike the spec spends it on."),

        node(Q, "monster_hunting", "Monster Hunting",
             "Increases your haste by 1 and all damage you deal by 2% per rank.",
             4, 0, 3, {"haste": 1.0, "all_damage": 0.02}, connect=["sinner"],
             total_slots=3,
             source="CoA: 'Increases melee and ranged haste of party and raid "
                    "members within 100 yds by 10%... In addition, increases "
                    "your damage dealt against Undead and Demons by 10%.' The "
                    "party aura is an ABILITY in Frontier (a talent's effects "
                    "never leave its own character) and there is no "
                    "creature-type hook, so this node is the personal half."),
        node(Q, "heartstopper", "Heartstopper",
             "Increases the critical strike chance of Stake by 4% per rank.",
             4, 1, 3, {"ability_witch_hunter_stake_crit": 4.0},
             connect=["duskwood_renegade"], total_slots=3,
             source="CoA: 'Casting Purifier's Edge or Fiery Judgement now has a "
                    "30% chance to allow the use of Stake within 8 seconds "
                    "regardless of the target's health percentage.' A "
                    "bypass_execute_threshold proc exists in the engine but only "
                    "as an ability's own effect, not a talent payload, so the "
                    "node raises Stake's crit instead - which is what CoA's own "
                    "'Evil Doers, Beware!' passive does anyway."),
        node(Q, "burned_alive", "Burned Alive",
             "Increases your critical strike chance by 1% and your critical "
             "strike damage by 5% per rank.",
             4, 2, 3, {"crit_chance_physical": 1.0, "crit_damage_physical": 0.05},
             connect=["flames_of_the_sinned"], total_slots=3,
             source="CoA: 'Increases your critical strike chance by 25% on "
                    "enemies below 20% health.' No target-health band, so it is "
                    "flat and much smaller."),

        node(Q, "torch_the_wicked", "Torch the Wicked!",
             "Increases your haste by 1 and your Fire spell damage by 3% per "
             "rank.",
             5, 0, 3, {"haste": 1.0, "fire_spell_damage": 0.03},
             connect=["monster_hunting"], total_slots=3,
             source="CoA: 'Dealing damage with Flames of Sin now grants 2% "
                    "attack speed, stacking up to 12 times for 6 seconds. "
                    "Additionally, Pyro Tonic now also resets the cooldown of "
                    "Torchlight.' Neither the stack nor the reset is a talent "
                    "shape; both halves of what they bought are."),
        node(Q, "hatred_and_vitriol", "Hatred & Vitriol",
             "Increases your armor penetration by 3% per rank.",
             5, 1, 3, {"armor_penetration_pct": 3.0},
             connect=["heartstopper"], total_slots=3,
             source="CoA: 'Damage dealt by Stake now ignores enemy armor and "
                    "its critical strikes refund half of its cost.' Ignoring "
                    "armour IS armor_penetration_pct, finally consumed in "
                    "take_damage's physical branch - just spread across the "
                    "whole kit rather than one ability."),
        node(Q, "lightbringer", "Lightbringer",
             "Reduces the Focus cost of your abilities by 3% per rank.",
             5, 2, 2, {"all_ability_cost_pct": 0.03},
             connect=["burned_alive"], total_slots=3,
             source="CoA: 'Damage dealt by Dusk Blade now has a 15% chance to "
                    "reduce the mana cost of your next Purifier's Edge by "
                    "-100%.' A one-shot free cast is not a talent shape; a real "
                    "discount is."),

        node(Q, "purity_and_wickedness", "Purity & Wickedness",
             "One blade brings the light up and the other takes it away, and "
             "neither of them stops.",
             6, 0, 1, {"physical_damage": 0.10, "fire_spell_damage": 0.08,
                       "shadow_spell_damage": 0.08},
             node_type="active",
             connect=["torch_the_wicked", "hatred_and_vitriol", "lightbringer"],
             total_slots=1,
             source="Capstone. CoA: 'Main-hand auto attacks now apply a stack "
                    "of Purity to the target, increasing the Fire and Holy "
                    "damage you deal to them by 2% per stack, stacking 6 times. "
                    "Off-hand auto attacks now apply a stack of Wickedness... "
                    "increasing the Shadow and Physical damage you deal to them "
                    "by 2% per stack.' Two independent target-side stack "
                    "counters are not expressible, so the node grants both "
                    "halves of the six-stack payoff at once - which is also "
                    "what CoA's S-tier raid rating assumes you have, since "
                    "'uninterrupted uptime is what it pays for'.")
    ],
    "Built from reference/coa_sidekick/SPEC_witch-hunter__inquisition.txt and "
    "the inquisition spec tree in reference/coa_sidekick/talents/"
    "witch-hunter.json. CoA rates it Raid S - 'top-tier sustained single-target "
    "DPS on patchwork fights' - and calls it 'a build-and-spend fire/shadow "
    "melee... sustain is grind-it-out via Dusk Blade rather than a burst-window "
    "finisher'. The unusual thing about this spec, and the reason for Malice and "
    "the three Fire-school nodes, is its stat priority: Hit > Expertise > SPELL "
    "POWER > Agility > Crit > Haste. A melee spec that wants spell power above "
    "its own primary stat only makes sense because Fiery Judgement, Torchlight "
    "and Dawn Blade all carry SP coefficients, and Malice converts Agility into "
    "spell damage to pay for it.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the files")
    args = parser.parse_args()

    ability_doc = {
        "class": "Witch Hunter",
        "_source_note": __doc__.strip().split("\n\n")[1].replace("\n", " "),
        "abilities": ABILITIES,
    }

    targets = [
        (ROOT / "data/abilities/witch_hunter.json", ability_doc),
        (ROOT / "data/talents/witch_hunter_boltslinger.json", BOLTSLINGER),
        (ROOT / "data/talents/witch_hunter_houndmaster.json", HOUNDMASTER),
        (ROOT / "data/talents/witch_hunter_black_knight.json", BLACK_KNIGHT),
        (ROOT / "data/talents/witch_hunter_inquisition.json", INQUISITION),
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
