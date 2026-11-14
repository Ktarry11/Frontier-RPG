#!/usr/bin/env python3
"""Author the Felsworn: ability kit + three talent trees.

    PYTHONPATH=. python3 tools/build_felsworn.py [--apply]

Felsworn is one of the twelve CoA classes that shipped with base stats,
armour type, weapon proficiency and a resource but no abilities and no
talents, which left it unselectable. Leather, Agility/Intellect hybrid,
Felfury - a demon hunter in all but the trademark, and the only class in
the roster whose three specs are a melee bruiser, a ranged caster and a
tank off one resource.

SOURCE. reference/coa_sidekick/CLASS_felsworn.txt, the three
SPEC_felsworn__*.txt pages and reference/coa_sidekick/talents/felsworn.json,
captured from ascensionsidekick.com. Every ability and talent name below is
a real CoA name off those pages; nothing is invented to fill a slot.
Identity per that reference:

  Slayer    MELEE DPS   "Closest to a Fury Warrior chassis with Demon
                        Hunter flavor bolted on." Dual-wield brawler whose
                        crits spill into off-hand strikes, armour-shred
                        spenders, and leech that only runs inside the
                        Inner Demon window.
  Infernal  RANGED DPS  "Closest to a Warlock flavor with Demon Hunter
                        trim." A Felfury builder-spender caster off Spirit
                        and Spell Power, absorb-piercing nukes, a summoned
                        demon, and a party crit aura.
  Tyrant    TANK        "Closest to Vengeance Demon Hunter's self-sustain
                        tank chassis", with a raid-buff layer stapled on.
                        Resource income comes from being hit.

NUMBERS ARE FRONTIER'S, NOT CoA'S. The reference gives identity, role and
rotation shape; it is a fan-made planning tool whose own disclaimer says
COA is pre-meta. Damage curves copy the two closest shipped classes:
Rogue's leather-melee shape for the physical kit (9 ranks at levels
1/6/12/18/24/32/40/48/56, flat resource cost, linear growth) and Cultist's
for the striker whose weapon hits carry a magic tail.

FELFURY BUDGET, and the one real divergence from CoA. CoA gives this class
"Energy + Demonic Rage" - Energy pays for casts, Felfury is the
builder/spender currency on top. Frontier's CLASS_RESOURCE_MAP gives
Felsworn exactly one pool, ResourceType.FELFURY, and nothing in
Character.restore_resources_between_turns regenerates it: Felfury is a
dict-backed secondary pool (Character.SECONDARY_RESOURCE_MAX, 0-100) with
no passive income at all. So the Energy layer collapses into the builders:
every builder is FREE and carries `generates` (the same mechanism
Stormbringer's Shock->Static builders already use), and every spender pays
Felfury. Fillers generate 20, hard builders 25, Burning Hatred dumps 40
(CoA's "instantly generating 6 Felfury"); spenders cost 20 to 40. Costs
are flat across ranks, because a cost over the 100 cap would make an
ability uncastable forever.

DEMON FORM. CoA's Inner Demon is the class's periodic Demon Form window
and every spec builds riders onto it. combat/forms.py has no Felsworn
entry - FORMS is keyed by class and the module is off-limits here - so
Inner Demon is a plain self-buff with a duration rather than an
effect_type: "shapeshift". That is the better fit anyway: shifting zeroes
the current resource pool by design, and a Felfury class that lost its
whole bar on entering its damage window would be unplayable. Recorded on
the ability.

Talent effect keys are restricted to ones the engine actually reads -
verified with tools/validate_class.py, which delegates liveness to
tools/audit_talents.py. Four casualties worth recording, each noted on its
node: CoA's Armor Penetration talents (Azzinoth's Rage, Fel Blades, Fel
Haze) have no live talent key, so they land as flat physical damage or
ability damage; expertise has none either; Dark Lord's "while ABOVE 75%
health" has no key (the engine only has the low_health_* pair); and
Blighted Strikes' healing-reduction debuff has no healing-taken key.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Rogue's shipped rank schedule - see module docstring.
RANK_LEVELS = [1, 6, 12, 18, 24, 32, 40, 48, 56]


def ranks(base, step, cost, start=1, count=9):
    """Flat-cost rank table on the Rogue schedule, starting at `start`.

    Levels past the 9-rank schedule are spaced evenly to stay under 58 so
    every rank is actually reachable at the level 60 cap.
    """
    if start == 1:
        levels = RANK_LEVELS[:count]
    else:
        span = max(1, (58 - start) // max(1, count - 1)) if count > 1 else 1
        levels = [min(58, start + i * span) for i in range(count)]
    return [{"rank": i + 1, "level_req": lv, "cost": cost,
             "effect_value": int(round(base + step * i))}
            for i, lv in enumerate(levels)]


def one(level, cost, value=0):
    """Single-rank table, for cooldowns and windows that do not scale."""
    return [{"rank": 1, "level_req": level, "cost": cost, "effect_value": value}]


def builds(amount):
    """`generates` payload for a Felfury builder - see module docstring."""
    return {"resource": "felfury", "amount": amount}


def ability(aid, name, effect_type, description, rank_table, *, cooldown=0,
            duration=0, stat_mods=None, icon=None, source=None,
            **extra):
    out = {
        "ability_id": f"felsworn_{aid}",
        "name": name,
        "resource_type": "felfury",
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
# Order is roughly the order a player meets them. `attack` stays first:
# tools/validate_class.py's combat probe executes the first ability that
# succeeds, and a free weapon swing is the one thing always castable.
ABILITIES = [
    ability("attack", "Attack", "damage",
            "A measured strike with your weapon.", one(1, 0, 0),
            source="Convention: every class ships a free rank-1 Attack."),

    # ---- core chassis, all three specs
    ability("twin_slice", "Twin Slice", "damage",
            "Two quick cuts, one from each hand, and the fel in you feeds "
            "on what they open.",
            ranks(40, 11, 0), target_type="enemy", damage_school="physical",
            generates=builds(20),
            source="CoA: the class-wide melee builder - Felwracked counts "
                   "'every 3rd Twin Slice or Fel Fireball', Twin Fury and "
                   "Vengeance both key off it, and Tyrant lists it among the "
                   "things that 'each add 1' Felfury. Rogue's sinister_strike "
                   "curve, free, generating instead of costing."),
    ability("fel_fireball", "Fel Fireball", "spell_damage",
            "A slow green ball of fel fire. You can throw it at a dead run.",
            ranks(34, 10, 0), target_type="enemy",
            damage_school=["shadow", "fire"], is_instant=True,
            generates=builds(20),
            source="CoA: 'Fel Fireball is your filler, generating 1 Felfury "
                   "per cast and usable while moving'. is_instant for the "
                   "while-moving half; the ranged builder all three specs "
                   "share."),
    ability("sargeron_smite", "Sargeron Smite", "damage",
            "Bring the weight of Sargeras down on one target.",
            ranks(56, 16, 30, start=6, count=8), cooldown=2,
            target_type="enemy", damage_school="shadow",
            source="CoA: the spender every spec presses - 'Fel Fireball into "
                   "Sargeron Smite on cooldown' for Infernal, Chaos Soldier "
                   "and Nether Champion scale it for Slayer, and Tyrant lists "
                   "it among the things Felfury is spent on."),
    ability("sunder", "Sunder", "damage",
            "Tear a seam through everything standing in front of you.",
            ranks(38, 11, 30, start=12, count=6), target_type="enemy_aoe",
            max_targets=4, damage_school=["shadow", "fire"],
            source="CoA names Sunder as a Felfury spender in all three specs "
                   "(Tyrant: 'Carve, Sargeron Smite, Sunder and Inner Demon "
                   "are all you have to spend it on'; Burning Rage and Shadow "
                   "Magi both modify it). target_type enemy_aoe, not is_aoe - "
                   "see the _implementation_note on this file's doc."),
    ability("chaos_rush", "Chaos Rush", "damage",
            "Close the gap in a blur of fel and hit whatever is at the end "
            "of it.",
            ranks(32, 11, 0, start=8, count=5), cooldown=2,
            target_type="enemy", damage_school="physical",
            generates=builds(20),
            source="CoA: the class-tree dash - Legion March extends its "
                   "range, Doomstride refreshes a charge, Felguard and "
                   "Felstrider ride on it, Reachwalker and Scars of the Past "
                   "key off it. A gap-closer that builds."),
    ability("inner_demon", "Inner Demon", "buff",
            "You stop holding it back. For a few turns you are the thing "
            "they were warned about.",
            one(20, 0), cooldown=10, duration=3,
            stat_mods={"attack_power_pct": 15.0, "crit_chance_physical": 8.0,
                       "crit_chance_spell": 8.0, "haste": 10.0},
            target_type="self", icon=None,
            source="CoA: 'the Inner Demon window, the kit's periodic power "
                   "state' - the Demon Form every spec builds riders onto. "
                   "NOT effect_type shapeshift: combat/forms.py has no "
                   "Felsworn form and FORMS is keyed by class, and shifting "
                   "zeroes the current resource pool by design, which would "
                   "empty the Felfury bar on entering the damage window. A "
                   "plain self-buff instead. Free to cast so the window is "
                   "never gated behind the resource it is meant to spend."),

    ability("hateforged_barrier", "Hateforged Barrier", "buff",
            "Hatred holds together better than most armour.",
            one(14, 25), cooldown=8, duration=3,
            absorb_pct_max_health=0.25, target_type="self", icon=None,
            source="CoA: 'Hateforged Barrier adds a Stamina-scaled absorb "
                   "that also regenerates a slice of your max health each "
                   "tick'. absorb_pct_max_health is the engine's real absorb "
                   "hook and already scales off max health, which is itself "
                   "Stamina-derived, so the Stamina scaling comes free. The "
                   "regen-while-it-holds half has no hook and is dropped."),
    ability("cripple", "Cripple", "debuff",
            "Their legs go heavy and their words come slow.",
            one(10, 20), cooldown=4, duration=3,
            stat_mods={"haste": -20.0}, target_type="enemy", icon=None,
            source="CoA: 'Cripple slows movement and casting'. haste on a "
                   "monster is read by TurnMeter.update via "
                   "get_status_stat_mod, so this genuinely costs the target "
                   "turns - the closest the engine has to a cast slow."),
    ability("consume_magic", "Consume Magic", "dispel",
            "Take what they were saving and keep it.",
            one(16, 20), cooldown=6, target_type="enemy",
            dispel_type="magic", icon=None,
            source="CoA class tree, Magic Fiend: 'Increases the amount of "
                   "beneficial magic effects stolen by your Consume Magic by "
                   "1'. The steal is a dispel here; nothing in the engine "
                   "moves a stolen buff onto the caster."),
    ability("felbreak", "Felbreak", "debuff",
            "Cut the word out of their mouth.",
            one(24, 20), cooldown=5, duration=1,
            stat_mods={"hit_chance_spell": -25.0}, target_type="enemy",
            is_stun=True, icon=None,
            source="CoA: 'Felbreak is a real interrupt on caster mobs, and "
                   "that's your main group-facing contribution'. A turn "
                   "engine has no cast bar to interrupt, so the honest "
                   "equivalent is costing them the turn: is_stun with a "
                   "1-turn duration, which TurnMeter really does enforce. "
                   "The school lockout rides along as a spell-hit debuff."),
    ability("manaburn", "Manaburn", "damage",
            "Burn what they were going to cast with and let the burning do "
            "the damage.",
            ranks(58, 17, 30, start=18, count=5), cooldown=4,
            target_type="enemy", damage_school="shadow",
            source="CoA class tree: 'Burn an enemy's mana equal to 200% of "
                   "your Stamina. Deals damage equal to the mana drained.' "
                   "Monsters have no mana pool to drain in this engine, so "
                   "only the damage half survives - the drain is flavour."),
    ability("whispers_of_the_pit", "Whispers of the Pit", "debuff",
            "Something underneath starts talking to all of them at once.",
            one(22, 30), cooldown=8, duration=2,
            stat_mods={"haste": -25.0, "attack_power": -30},
            target_type="enemy_aoe", max_targets=5, is_stun=True, icon=None,
            source="CoA class tree: 'Unleash fel energy upon enemies at "
                   "target location, fearing them and slowing their movement "
                   "speed by -80%. Damage caused may interrupt the effect.' "
                   "is_stun covers the fear (the engine's one "
                   "lose-your-turn mechanic); the break-on-damage half has no "
                   "hook, so this fear is not breakable."),
    ability("annihilation", "Annihilation", "buff",
            "You gorge until the next thing you touch cannot survive being "
            "touched.",
            one(26, 25), cooldown=8, duration=2,
            stat_mods={"crit_chance_physical": 40.0,
                       "crit_chance_spell": 40.0},
            target_type="self", icon=None,
            source="CoA class tree: 'guaranteeing your next direct instance "
                   "of damage to critically strike, but causing it to consume "
                   "5% of your maximum health'. No guaranteed-crit flag "
                   "exists, so it is a large crit window instead; the health "
                   "cost has no hook and is dropped rather than faked."),
    ability("skull_of_guldan", "Skull of Gul'dan", "buff",
            "He has been dead a long time and still has something left to "
            "give.",
            one(30, 25), cooldown=14, duration=3,
            stat_mods={"max_health_pct": 0.15, "stamina": 20},
            target_type="self", icon=None,
            source="CoA class tree: 'increasing your maximum health and "
                   "Energy by 25% for 10 seconds'. max_health_pct is a "
                   "FRACTION - health * (1.0 + value) - so 0.15 is +15%, not "
                   "15.0. The Energy half has no Energy pool to raise here."),
    ability("illidans_guile", "Illidan's Guile", "buff",
            "You stop existing for a moment. It is not restful.",
            one(34, 40), cooldown=18, duration=1,
            stat_mods={"damage_taken_pct": -0.8, "haste": -40.0},
            target_type="self", icon=None,
            source="CoA class tree: 'becoming immune to all physical attacks "
                   "and spells for 8 seconds, but during that time you cannot "
                   "attack, move or cast spells'. There is no immunity flag, "
                   "so -80% damage taken stands in, and the cannot-act cost "
                   "is paid as a heavy haste penalty rather than a "
                   "turn-skip the engine cannot express."),

    # ---- Slayer
    ability("azzinoths_assault", "Azzinoth's Assault", "damage",
            "Both blades into the same gap, widening it.",
            ranks(54, 15, 30, start=10, count=7), cooldown=2,
            target_type="enemy", damage_school="physical",
            source="CoA: 'Azzinoth's Assault on cooldown as your armor-shred "
                   "spender (Azzinoth's Rage/Fel Blades; consumes 2 Felfury "
                   "and seeds the loop)'."),
    ability("annihilan_strike", "Annihilan Strike", "damage",
            "One strike with everything behind it, and it lands clean on "
            "anything still healthy enough to be confident.",
            ranks(72, 20, 0, start=14, count=6), cooldown=3,
            target_type="enemy", damage_school="physical",
            generates=builds(25),
            source="CoA: 'Generates 2 Felfury. Unleash a devastating attack, "
                   "dealing 145% Weapon Damage to your target with both "
                   "weapons. Guaranteed to critically strike against enemies "
                   "above 75% health.' The guaranteed crit has no flag; the "
                   "base damage carries it instead."),
    ability("glaiving", "Glaiving", "damage",
            "Off-hand work, fast and low.",
            ranks(30, 9, 0, start=12, count=6), target_type="enemy",
            damage_school="physical", generates=builds(20),
            source="CoA: 'weave Glaiving and Felhoof Charge into the loop for "
                   "reach and cleave' and 'Keep Glaiving in the rotation for "
                   "off-hand damage and Felfury'."),
    ability("felhoof_charge", "Felhoof Charge", "damage",
            "You arrive before they have decided where to stand.",
            ranks(44, 13, 0, start=16, count=5), cooldown=4,
            target_type="enemy", damage_school="physical", is_stun=True,
            generates=builds(20),
            source="CoA: 'Generates 1 Felfury. Charge an enemy, dealing AP "
                   "Physical damage', and 'Use Felhoof Charge to gap-close on "
                   "casters and runners'. A charge lands them on their back, "
                   "so is_stun."),
    ability("immolation_aura", "Immolation Aura", "dot",
            "You burn, and so does anything standing close enough to "
            "matter.",
            ranks(24, 7, 25, start=18, count=5), cooldown=4, duration=3,
            target_type="enemy_aoe", max_targets=4, damage_school="fire",
            source="CoA: 'Open pulls with Immolation Aura for its recurring "
                   "Fire pulse on nearby enemies' - 'dealing fire AP Fire "
                   "Damage to nearby enemies every 3 sec'."),
    ability("fury_unleashed", "Fury Unleashed", "damage",
            "Glaives out, feet moving, and nothing in reach gets a clean "
            "turn.",
            ranks(46, 13, 40, start=24, count=5), cooldown=6,
            target_type="enemy_aoe", max_targets=5, damage_school="physical",
            source="CoA: 'Fury Unleashed is a Bladestorm analog: a spinning "
                   "glaive channel that speeds you up and cleaves all nearby "
                   "enemies with both weapons', 'Dump Fury Unleashed on 3+ "
                   "mob pulls'. The movement-speed and CC-immunity riders "
                   "have no hooks."),
    ability("fury_of_the_illidari", "Fury of the Illidari", "damage",
            "Six places at once, six times, and then you are standing "
            "somewhere else entirely.",
            ranks(118, 34, 40, start=36, count=4), cooldown=8,
            target_type="enemy", damage_school="physical",
            generates=builds(20),
            source="CoA: 'Move quickly from enemy to enemy, attacking them "
                   "every 1 sec with both weapons until 6 assaults are made, "
                   "generating 1 Felfury with each strike', 'its signature "
                   "mobility-burst tool'. Six separate hops have no engine "
                   "shape, so it is one heavy strike that still pays Felfury "
                   "back."),
    ability("bane_of_frailty", "Bane of Frailty", "debuff",
            "Their armour stops being the point.",
            one(20, 20), cooldown=6, duration=3,
            stat_mods={"armor": -140}, target_type="enemy", icon=None,
            source="CoA: 'You open with Bane of Frailty to strip a chunk of "
                   "the target's armor'. Flat armor, not armor_pct: Monster "
                   "resolves armour through get_status_stat_mod('armor') and "
                   "reads no percentage key, so armor_pct on an enemy would "
                   "do nothing."),
    ability("blood_of_mannoroth", "Blood of Mannoroth", "buff",
            "Mannoroth's blood is still in there somewhere and it still "
            "wants a fight.",
            one(32, 30), cooldown=12, duration=3,
            stat_mods={"attack_power_pct": 15.0,
                       "crit_chance_physical": 8.0},
            target_type="self", icon=None,
            source="CoA, Fel Haze: 'While active, Blood of Mannoroth now "
                   "also causes you to ignore all enemy Armor'. The "
                   "armour-ignore half has no talent-side key, so the buff "
                   "carries attack power and crit instead."),

    # ---- Infernal
    ability("ruin", "Ruin", "spell_damage",
            "Doom, delivered. Nothing they put between you and it holds.",
            ranks(76, 22, 40, start=12, count=7), cooldown=2,
            target_type="enemy", damage_school=["shadow", "fire"],
            source="CoA: 'Consumes 2 Felfury. Bring doom upon an enemy, "
                   "dealing Shadowflame Damage to an enemy, piercing all "
                   "absorption effects', 'your hardest-hitting nuke (it "
                   "pierces all absorbs)'. Absorb-piercing has no flag; the "
                   "damage is sized as the kit's single biggest hit instead."),
    ability("felwrath", "Felwrath", "spell_damage",
            "The blast goes wide and takes the pack with it.",
            ranks(38, 11, 35, start=16, count=6), target_type="enemy_aoe",
            max_targets=5, damage_school=["shadow", "fire"],
            source="CoA: 'Consumes 2 Felfury. Blast an enemy and all enemies "
                   "near them with fel magic', 'Felwrath's AoE Shadowflame "
                   "and Infernal's fear-on-drop flip a clumped teamfight'. "
                   "The Inner Demon 5+ target bonus has no conditional hook."),
    ability("bane_of_chaos", "Bane of Chaos", "spell_dot",
            "A slow, patient ruin set working inside them.",
            ranks(28, 9, 0, start=10, count=6), duration=3,
            target_type="enemy", damage_school="shadow",
            generates=builds(20),
            source="CoA: 'Generates 1 Felfury. Unleash fel magic on an enemy, "
                   "dealing 114 Chaos damage over 18 seconds', 'keeping a "
                   "Bane of Chaos rolling on the target (only one Bane at a "
                   "time)'. One-Bane-at-a-time is natural here: a second cast "
                   "refreshes the same effect_id rather than stacking."),
    ability("felstrike", "Felstrike", "spell_dot",
            "A short, bright burn that keeps burning.",
            ranks(26, 8, 20, start=22, count=5), duration=3,
            target_type="enemy", damage_school=["shadow", "fire"],
            source="CoA, Fel Apprentice: 'While Inner Demon is active, your "
                   "Fel Fireball will now unleash a Felstrike on your target. "
                   "Felstrike: Burn an enemy for SP Shadowflame Damage over 6 "
                   "seconds, stacking 3 times.' A real named ability, so it "
                   "is castable here rather than existing only as a rider."),
    ability("sargeras_embrace", "Sargeras Embrace", "spell_dot",
            "You hold the beam on them and they stop getting anywhere.",
            ranks(44, 13, 30, start=30, count=4), cooldown=6, duration=2,
            target_type="enemy", damage_school="shadow",
            source="CoA: 'Channel a beam of fel magic upon an enemy, slowing "
                   "your target's movement speed by 60% for 5.5 seconds and "
                   "dealing Shadowflame Damage at the end of the duration'. "
                   "Authored as a spell_dot: the engine has no channel, and a "
                   "DoT is the closest thing to damage spread over a beam. "
                   "The snare is lost - Cripple remains the real slow."),
    ability("infernal", "Infernal", "summon_pet",
            "Something lands where you pointed. The pack stops looking at "
            "you.",
            one(28, 40), cooldown=15, target_type="self",
            summon_pet_template="infernal", icon=None,
            source="CoA: 'Drop an infernal from the sky with grotesque magic, "
                   "dealing fire SP Fire damage to enemies in the radius, "
                   "horrifying them for 4 seconds, and spawning an Infernal "
                   "to fight by your side for 15 seconds.' NOW A REAL "
                   "INFERNAL: this used to borrow voidwalker and summoned a "
                   "pet named Voidwalker, a Warlock demon, on the reasoning "
                   "that combat/pet_templates.py had no infernal. It has one "
                   "now - a slow, heavy fire bruiser whose signature "
                   "Immolation is real spell_damage/fire, matching CoA's own "
                   "'SP Fire damage'. Still only the pet survives: "
                   "effect_type summon_pet does one thing, so the impact "
                   "damage and the fear are lost."),
    ability("manafeed", "Manafeed", "damage_and_heal",
            "What they were going to spend, you spend instead.",
            ranks(44, 13, 25, start=20, count=5), cooldown=3,
            target_type="enemy", damage_school="shadow",
            source="CoA: 'Manafeed converts a target's burned mana into "
                   "health for you, closer to a Drain Life than a real "
                   "defensive', 'Manafeed is your only heal'. Monsters have "
                   "no mana here, so the heal is unconditional rather than "
                   "dead weight against a mana-less target - a deliberate "
                   "divergence, because the alternative is a spec with no "
                   "self-healing at all."),
    ability("fel_infusion", "Fel Infusion", "buff",
            "The fel coming off you sharpens everyone standing near it.",
            one(34, 25), cooldown=10, duration=4,
            stat_mods={"crit_chance_physical": 3.0,
                       "crit_chance_spell": 3.0},
            target_type="self", buff_scope="party", icon=None,
            source="CoA: 'Increases critical strike chance of all party and "
                   "raid members within 100 by 3%... In addition, increases "
                   "your critical strike chance by 3%', and 'its real group "
                   "contribution is the passive Fel Infusion party/raid crit "
                   "buff'. Passive auras have no shape here, so it is a "
                   "party-scoped cooldown."),

    # ---- Tyrant
    ability("felrend", "Felrend", "damage",
            "A full turn with both weapons out. Everyone close pays for "
            "standing there.",
            ranks(30, 9, 0, start=10, count=7), target_type="enemy_aoe",
            max_targets=4, damage_school="physical", generates=builds(20),
            source="CoA: 'Generates 1 Felfury. Erupt in a whirlwind of "
                   "felfury, striking all enemies within 6 yds with both "
                   "weapons', 'Keep AoE pressure up with Felrend against "
                   "packs'. The tank's threat filler."),
    ability("carve", "Carve", "damage",
            "You take your time winding up and they feel every bit of the "
            "wait.",
            ranks(62, 18, 35, start=14, count=6), cooldown=2,
            target_type="enemy_aoe", max_targets=3, damage_school="physical",
            source="CoA: 'Consumes 2 Felfury. Charge up a powerful attack "
                   "over 2.5 seconds. Upon ending the channel, slash in front "
                   "of you, dealing increased Weapon Damage with both weapons "
                   "based on how long you channel'. No channel exists here, "
                   "so the charge-up is folded into the damage and the "
                   "cooldown. The longer-channel-more-dodge rider (Battle "
                   "Finesse) is lost with it."),
    ability("demonic_will", "Demonic Will", "buff",
            "You decide that this is survivable and that settles it.",
            one(18, 0), cooldown=8, duration=3,
            stat_mods={"physical_damage_taken_pct": -30},
            target_type="self", generates=builds(20), icon=None,
            source="CoA: 'Generates 1 Felfury. Strengthen your will, reducing "
                   "Physical damage taken by -30% for 10 seconds. While "
                   "active, direct damaging abilities heal you for 3% of your "
                   "maximum health.' The heal-on-damage rider has no "
                   "ability-side hook; it lives on the Straight to the Nether "
                   "talent instead.  UNIT FIXED 2026-10-29, and the note that "
                   "used to sit here said the opposite: it claimed "
                   "physical_damage_taken_pct is a FRACTION, authored -0.3, "
                   "and therefore delivered -0.3% instead of -30%. In an "
                   "ABILITY's stat_mods this key is PERCENT POINTS - "
                   "Character.take_damage divides "
                   "get_status_stat_mod('physical_damage_taken_pct') by 100, "
                   "while the bare damage_taken_pct key four lines away in "
                   "the same method is added undivided and IS a fraction. "
                   "The convention is per-key with no naming rule. Measured: "
                   "0.04 took 736 from a 1000 hit, 4.0 took 766. The fix was "
                   "made in the emitted JSON earlier the same day and not "
                   "ported here, so re-running this script silently restored "
                   "the broken value - which is how it was found. "
                   "tools/validate_class.py now errors on both directions and "
                   "names the corrected number."),
    ability("burning_hatred", "Burning Hatred", "buff",
            "Nothing complicated. You are angry and it is useful.",
            one(24, 0), cooldown=12, duration=3,
            stat_mods={"attack_power_pct": 10.0}, target_type="self",
            generates=builds(40), icon=None,
            source="CoA: 'Enrages you, instantly generating 6 Felfury and "
                   "causing your melee damage to leech health to you equal to "
                   "50% of the damage dealt as Chaos damage for 15 seconds.' "
                   "The 6-Felfury dump is the whole point, so this generates "
                   "40 - twice a builder. The leech lives on Felguard and "
                   "Straight to the Nether, where a proc can carry it."),
    ability("tyrannical_resolve", "Tyrannical Resolve", "buff",
            "You tell the room who it is fighting, and then you take it.",
            one(40, 0), cooldown=16, duration=2,
            stat_mods={"damage_taken_pct": -0.5, "taunt": 1,
                       "threat_generation_pct": 200},
            target_type="self", icon=None,
            source="CoA: 'Taunt nearby enemies for 4 seconds and ignore -50% "
                   "of all damage taken for 30 seconds', 'your emergency "
                   "button against anything threatening to kill you'. "
                   "stat_mods taunt is the engine's real taunt hook "
                   "(Ability._apply_effect reads it directly); the Felfire "
                   "burst on expiry has no hook. Note ability stat_mods "
                   "threat_generation_pct is percent POINTS, unlike the "
                   "talent key of the same name, which is a fraction."),
    ability("tyrants_gaze", "Tyrant's Gaze", "damage_and_heal",
            "You look at them properly for the first time and they catch "
            "fire.",
            ranks(92, 26, 30, start=26, count=5), cooldown=5,
            target_type="enemy", damage_school=["shadow", "fire"],
            execute_threshold_pct=35,
            source="CoA: 'Set your fiery gaze upon an enemy... causing them "
                   "to combust, dealing AP Shadowflame Damage. Damaging an "
                   "enemy in this way heals you for AP and generates 1 "
                   "Felfury. Only usable on enemies below 35% health.' The "
                   "35% gate is a real engine field, execute_threshold_pct."),
    ability("eye_of_the_tyrant", "Eye of the Tyrant", "buff",
            "You set the pace and the room keeps up.",
            one(30, 25), cooldown=12, duration=3,
            stat_mods={"haste": 10.0, "attack_power_pct": 5.0},
            target_type="self", buff_scope="party", icon=None,
            source="CoA: 'Grant 10% increased melee and ranged haste to party "
                   "and raid members within 100 yds... In addition, your "
                   "attack power is increased by 5%', 'save Eye of the "
                   "Tyrant's party haste for the pull or burn phase you want "
                   "to reinforce'."),
    ability("infernal_whipcrack", "Infernal Whipcrack", "buff",
            "A crack over their heads, and the whole line finds another "
            "gear.",
            one(36, 30), cooldown=14, duration=3,
            stat_mods={"damage_taken_pct": -0.12, "haste": 10.0},
            target_type="self", buff_scope="party", icon=None,
            source="CoA: 'Enrage up to 8 allies within 20 yds, reducing their "
                   "damage taken by -15% and increasing their haste by 10% "
                   "for 10 seconds', 'drop Infernal Whipcrack to enrage the "
                   "group'. The external-cooldown layer CoA says Vengeance "
                   "Demon Hunter does not have."),
    ability("doomscarring", "Doomscarring", "debuff",
            "The scar stays open and everyone can see where to aim.",
            one(32, 25), cooldown=6, duration=3,
            stat_mods={"armor": -110}, target_type="enemy", icon=None,
            source="CoA: 'scars enemies for 12 seconds, increasing your "
                   "allies' attack power against them by Agility'. Nothing "
                   "grants a buff scoped to one target, so the scar is a "
                   "flat armour break on the enemy - same end result for the "
                   "party's physical damage, without an invented key."),
    ability("fel_bargain", "Fel Bargain", "heal",
            "You trade something you were saving for something you need "
            "now.",
            ranks(190, 100, 40, start=22, count=5), cooldown=6,
            target_type="self", icon=None,
            source="CoA: 'Fel Bargain trades banked Energy into health in a "
                   "pinch'. Banked Felfury here, since that is the only pool "
                   "this class has."),
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


def felfury_proc(trigger, chance, amount, *, icd=0, filters=None):
    """A Felfury-generating proc. The engine scales proc `chance` by
    points_spent for any node with max_points > 1 (Character.
    _sync_talent_procs), so these are authored PER RANK, like effects."""
    out = {"trigger": trigger, "chance": chance, "icd": icd}
    if filters:
        out["ability_filter"] = [f"felsworn_{f}" for f in filters]
    out["grant_resource"] = {"resource": "felfury", "amount": amount}
    return out


# ================================================================= Slayer
S = "felsworn_slayer"
SLAYER = tree(
    S, "Felsworn Slayer",
    "Dual-wield fel melee - crits spill into off-hand strikes, spenders "
    "peel armour off the target, and the leech only runs while Inner Demon "
    "is up.",
    [
        node(S, "azzinoths_rage", "Azzinoth's Rage",
             "Increases your physical damage by 2% per rank.",
             0, 0, 5, {"physical_damage": 0.02},
             source="CoA: 'Increases your Armor penetration by 10% and your "
                    "expertise by 4.' Neither armour penetration nor "
                    "expertise has a live talent key - Guardian's Dirty "
                    "Tactics hit the same wall - so this lands as flat "
                    "physical damage, the same effect against an armoured "
                    "target without inventing a dead key."),
        node(S, "slice_and_dice", "Slice & Dice",
             "Increases the damage of Twin Slice by 6% per rank.",
             0, 1, 5, {"ability_felsworn_twin_slice_damage": 0.06},
             source="CoA: 'Increases your off-hand weapon damage by 25% and "
                    "reduces the Energy cost of Twin Slice by -5.' Twin Slice "
                    "is already free here, so the whole node goes into its "
                    "damage. ability_<id>_<stat> keys are built by "
                    "interpolation in abilities.py, not literals."),
        node(S, "spite", "Spite",
             "Increases your Agility by 2% per rank.",
             0, 2, 5, {"agility_pct": 2.0},
             source="CoA: 'Increases your Agility by 8% and dodge chance by "
                    "3%.' agility_pct is PERCENT POINTS (eff *= 1 + v/100), "
                    "unlike max_health_pct. The dodge half is dropped on "
                    "purpose: Agility already feeds dodge at a quarter point "
                    "each, and with Unbound in the same column this spec was "
                    "ending up with the largest dodge budget of any tree in "
                    "the game, tank trees included."),
        node(S, "chaos_soldier", "Chaos Soldier",
             "Increases your critical strike chance by 1% per rank.",
             0, 3, 5, {"crit_chance_physical": 1.0},
             source="CoA: 'Increases the critical strike chance of Azzinoth's "
                    "Assault and Sargeron Smite by 5%.' Per-ability crit has "
                    "no key, so it is general crit - the spec's stat priority "
                    "puts Critical Strike fourth anyway."),

        node(S, "twin_fury", "Twin Fury",
             "Your critical strikes with Twin Slice and Annihilan Strike "
             "have a 20% chance per rank to generate 8 Felfury.",
             1, 0, 3, {}, connect=["azzinoths_rage"],
             proc=felfury_proc("on_crit", 20, 8,
                               filters=["twin_slice", "annihilan_strike"]),
             source="CoA: 'Critically striking with Twin Slice or Annihilan "
                    "Strike now generates an additional 1 Felfury.' A real "
                    "grant_resource proc, scoped with ability_filter."),
        node(S, "dancing_blades", "Dancing Blades",
             "Your melee critical strikes have a 15% chance per rank to "
             "land an immediate off-hand strike.",
             1, 1, 3, {}, connect=["slice_and_dice"],
             proc={"trigger": "on_crit", "chance": 15, "icd": 1,
                   "extra_attack": 1},
             source="CoA: 'Critical strikes with melee abilities now trigger "
                    "Dancing Blades, dealing off-hand Weapon Damage to up to "
                    "5 nearby enemies.' extra_attack is the engine's real "
                    "free-swing payload; the 5-target spread is not "
                    "expressible, so it hits one."),
        node(S, "unbound", "Unbound",
             "Grants dodge equal to 1% of your Agility, and 1 hit rating, "
             "per rank.",
             1, 2, 5, {"dodge_from_agility_pct": 0.01, "hit_rating": 1},
             connect=["spite"],
             source="CoA: 'Increases your dodge by 15% of your Agility and "
                    "your hit rating by 6% of your Agility.' The dodge half "
                    "is a real <target>_from_<source>_pct conversion; the hit "
                    "half cannot be, because hit_rating is a local feeding "
                    "base_miss_chance_* rather than a Character attribute, so "
                    "it is flat - the same wall Guardian's Bulwark hit. CoA's "
                    "15% of Agility is cut to 5% at full rank: Felsworn's "
                    "base Agility already puts it at 18% dodge before a "
                    "single point is spent, and at CoA's ratio this DPS spec "
                    "measured higher avoidance than any tank in the game."),
        node(S, "true_self", "True Self",
             "Increases your chance to dodge by 1% and your critical strike "
             "damage by 4% per rank.",
             1, 3, 3, {"dodge": 1.0, "crit_damage_physical": 0.04},
             connect=["chaos_soldier"],
             source="CoA: 'Your Inner Demon now grants 10% increased dodge "
                    "chance and critical damage dealt while active.' There is "
                    "no while-a-buff-is-up conditional key, so both halves "
                    "are always on at a smaller value."),

        node(S, "fel_blades", "Fel Blades",
             "Increases the damage of Azzinoth's Assault by 8% per rank.",
             2, 0, 3, {"ability_felsworn_azzinoths_assault_damage": 0.08},
             connect=["twin_fury"],
             source="CoA: 'Damage dealt by Azzinoth's Assault now reduces the "
                    "enemy's armor by -4% for 10 seconds, stacking 5 times.' "
                    "No talent applies a debuff to a target through effects, "
                    "and there is no armour-shred key, so the shred is folded "
                    "into the ability's own damage. The real armour break is "
                    "the Bane of Frailty ability."),
        node(S, "a_thousand_cuts", "A Thousand Cuts",
             "Azzinoth's Assault has a 10% chance per rank to strike a "
             "second time for 30% damage.",
             2, 1, 3, {}, connect=["dancing_blades"],
             proc={"trigger": "on_damage_cast", "chance": 10, "icd": 0,
                   "ability_filter": ["felsworn_azzinoths_assault"],
                   "bonus_pct": 0.3},
             source="CoA: 'Azzinoth's Assault now has a 30% chance to hit an "
                    "additional time with your main-hand Weapon.' bonus_pct "
                    "adds to the same hit, which is what an extra main-hand "
                    "swing amounts to."),
        node(S, "fel_instincts", "Fel Instincts",
             "Increases your haste by 2 per rank.",
             2, 2, 5, {"haste": 2.0}, connect=["unbound"],
             source="CoA: 'Increases the damage of Azzinoth's Assault by 10% "
                    "and causes it to increase your melee haste by 20% for 5 "
                    "seconds.' The damage half is already Fel Blades' job, so "
                    "this node is the haste."),
        node(S, "you_cheat_guldan", "You Cheat, Gul'dan!",
             "Increases your critical strike damage by 4% per rank.",
             2, 3, 3, {"crit_damage_physical": 0.04},
             connect=["true_self"],
             source="CoA: 'Increases your critical damage by 50% against "
                    "enemies above 75% health.' No above-X%-health "
                    "conditional exists (only the low_health_* pair), so it "
                    "is unconditional and much smaller."),

        node(S, "reckless_assault", "Reckless Assault",
             "Increases the damage of Annihilan Strike by 8% per rank.",
             3, 0, 3, {"ability_felsworn_annihilan_strike_damage": 0.08},
             connect=["fel_blades"],
             source="CoA: 'Increases the damage of Azzinoth's Assault, "
                    "Annihilan Strike, and Twin Slice by 15% against slowed "
                    "enemies.' The other two already have damage nodes and "
                    "there is no against-slowed conditional, so this one "
                    "takes Annihilan Strike unconditionally."),
        node(S, "legionfall", "Legionfall",
             "Your melee ability damage has a 7% chance per rank to reset "
             "the cooldown of Annihilan Strike.",
             3, 1, 2, {}, connect=["a_thousand_cuts"],
             proc={"trigger": "on_damage_cast", "chance": 7, "icd": 2,
                   "reset_cooldown": {"ability": "felsworn_annihilan_strike"}},
             source="CoA: 'Melee ability damage now has a 15% chance to reset "
                    "the cooldown of Annihilan Strike.' reset_cooldown is a "
                    "real proc payload - the thing Guardian's King's Guard "
                    "could not reach, because it wanted to reset a different "
                    "ability than the one that triggered it."),
        node(S, "consumed_by_fel", "Consumed By Fel",
             "Increases the damage of Immolation Aura by 8% and all your "
             "periodic damage by 3% per rank.",
             3, 2, 3, {"ability_felsworn_immolation_aura_damage": 0.08,
                       "dot_damage": 0.03},
             connect=["fel_instincts"],
             source="CoA: 'Increases the tick rate of Immolation Aura by "
                    "-25%.' Tick rate is fixed at one per turn here, so a "
                    "faster tick is authored as more damage per tick."),
        node(S, "blighted_strikes", "Blighted Strikes",
             "Increases all damage you deal by 2% per rank.",
             3, 3, 3, {"all_damage": 0.02}, connect=["you_cheat_guldan"],
             source="CoA: 'While Inner Demon is active your melee attacks "
                    "reduce the target's healing received by -20%.' There is "
                    "no healing-taken key anywhere in the engine, so the "
                    "node carries flat damage and the anti-heal identity is "
                    "lost. Worth saying plainly: this is the weakest "
                    "translation in the tree."),

        node(S, "felguard", "Felguard",
             "Your damaging abilities have a 30% chance per rank to heal "
             "you for 6% of the damage dealt.",
             4, 0, 3, {}, connect=["reckless_assault"],
             proc={"trigger": "on_damage_cast", "chance": 30, "icd": 0,
                   "leech_pct": {"pct": 0.06}},
             source="CoA: 'while Inner Demon is active, you now heal for 15% "
                    "of all melee damage dealt', 'Felguard's Inner-Demon "
                    "melee leech keeps you topped up'. leech_pct is the "
                    "engine's real on-damage leech. Window-gating is not "
                    "expressible, so the rate is cut and made chance-based "
                    "instead of always-on."),
        node(S, "perpetual_fury", "Perpetual Fury",
             "Reduces the cooldown of Fury Unleashed by 10% per rank.",
             4, 1, 3,
             {"ability_felsworn_fury_unleashed_cooldown_pct": 0.10},
             connect=["legionfall"],
             source="CoA: 'Dealing damage with Dancing Blades reduces the "
                    "cooldown of Fury Unleashed by -1 sec.' A proc that "
                    "shortens a cooldown has no shape, so it is a flat "
                    "cooldown reduction on the same ability."),
        node(S, "nether_champion", "Nether Champion",
             "Increases your critical strike chance by 1% and your haste by "
             "1 per rank.",
             4, 2, 3, {"crit_chance_physical": 1.0, "haste": 1.0},
             connect=["consumed_by_fel"],
             source="CoA: 'Triggering Dancing Blades now increases the damage "
                    "of next Sargeron Smite by 8%, stacking 5 times.' A "
                    "stacking per-ability buff off another talent's proc is "
                    "two hooks deep; this is the honest flat version."),

        node(S, "scars_of_suffering", "Scars of Suffering",
             "Increases your attack power by 4% per rank.",
             5, 0, 3, {"attack_power_pct": 4.0}, connect=["felguard"],
             total_slots=3,
             source="CoA: 'Casting Azzinoth's Assault now scars the enemy, "
                    "increasing your allies' attack power against them by 15% "
                    "Agility.' Nothing scopes a buff to one target, and CoA "
                    "itself calls this spec 'a bruiser, not a support', so "
                    "the attack power lands on you."),
        node(S, "whirling_vengeance", "Whirling Vengeance",
             "Increases the damage your abilities deal to additional targets "
             "by 10% per rank.",
             5, 1, 2, {"aoe_damage": 0.10}, connect=["perpetual_fury"],
             total_slots=3,
             source="CoA: 'When Fury Unleashed ends, you strike all nearby "
                    "enemies for AP Shadowflame Damage and increase their "
                    "damage taken from Sunder by 100%.' The cleave half "
                    "survives as aoe_damage."),
        node(S, "oblivion", "Oblivion",
             "Increases all damage you deal by 2% per rank.",
             5, 2, 2, {"all_damage": 0.02}, connect=["nether_champion"],
             total_slots=3,
             source="CoA: 'Critically striking now increases your damage "
                    "dealt by 1% for 4 seconds, stacking 10 times.' A "
                    "stacking self-buff off crits is a proc shape the engine "
                    "has, but with no stack cap on a talent-synthesised "
                    "effect it would run away; flat damage instead."),

        node(S, "pit_lords_rage", "Pit Lord's Rage",
             "There is nothing left of you that was holding anything back.",
             6, 0, 1, {"physical_damage": 0.12, "crit_chance_physical": 3.0},
             node_type="active",
             connect=["scars_of_suffering", "whirling_vengeance", "oblivion"],
             total_slots=1,
             source="Capstone. CoA: 'Casting Chaos Rush now increases your "
                    "Physical damage by 15% for 10 seconds. Casting Felhoof "
                    "Charge increases your critical strike chance by 6% for "
                    "15 seconds.' Both riders fold into one always-on payoff, "
                    "which suits a spec CoA rates Dungeon C / Raid A on "
                    "'strong sustained single-target DPS' rather than burst."),
    ],
    "Built from reference/coa_sidekick/SPEC_felsworn__slayer.txt and the "
    "slayer block of reference/coa_sidekick/talents/felsworn.json. CoA calls "
    "this 'a Fury-Warrior-tempo cleave bruiser with Demon Hunter self-leech "
    "and a channeled AoE spin'. Its stat priority is Hit > Expertise > "
    "Agility > Critical Strike > Haste > Armor Penetration, which is why the "
    "tree opens on Agility, crit and hit rather than raw damage, and why "
    "Unbound - the one node that converts Agility into both dodge and hit - "
    "is the biggest in it. Expertise and Armor Penetration have no live "
    "talent keys at all, so the three CoA nodes built on them (Azzinoth's "
    "Rage, Fel Blades, Fel Haze) are translated rather than transcribed.")


# =============================================================== Infernal
I = "felsworn_infernal"
INFERNAL = tree(
    I, "Felsworn Infernal",
    "Ranged Felfury caster - Fel Fireball builds, Ruin and Felwrath spend, "
    "and Spirit is a real damage stat here.",
    [
        node(I, "wrath_of_sargeras", "Wrath of Sargeras",
             "Increases your magic damage by 2% and your chance to hit with "
             "spells by 1% per rank.",
             0, 0, 5, {"spell_damage": 0.02, "hit_chance_spell": 1.0},
             source="CoA: 'Increases your Magic damage dealt by 3% and your "
                    "spell hit chance by 2%.'"),
        node(I, "fel_cannon", "Fel Cannon",
             "Increases your spell critical strike chance by 1% per rank.",
             0, 1, 5, {"crit_chance_spell": 1.0},
             source="CoA: 'Increases the critical strike chance of Fel "
                    "Fireball and Ruin by 15% on enemies above 75% health.' "
                    "No per-ability crit key and no above-X%-health "
                    "conditional, so it is general spell crit - which this "
                    "spec's stat priority wants second anyway."),
        node(I, "guldans_prodigy", "Gul'dan's Prodigy",
             "Increases the damage of Fel Fireball by 6% per rank.",
             0, 2, 5, {"ability_felsworn_fel_fireball_damage": 0.06},
             source="CoA: 'Reduces Energy cost and cast time of Fel Fireball "
                    "by -15%.' Fel Fireball is already free and instant here, "
                    "so the node pays out in damage instead."),
        node(I, "hidden_power", "Hidden Power",
             "Grants spell power equal to 2% of your Spirit and 2% of your "
             "Intellect per rank.",
             0, 3, 5, {"spell_damage_from_spirit_pct": 0.02,
                       "spell_damage_from_intellect_pct": 0.02},
             source="CoA: 'Increases your spell damage by 15% of your "
                    "Intellect and Spirit.' Two real "
                    "<target>_from_<source>_pct conversions, resolved against "
                    "the shared STAT_CONVERSION maps in character.py. This is "
                    "the node that makes Spirit the spec's primary stat."),

        node(I, "illidari_smiter", "Illidari Smiter",
             "Your critical strikes with Fel Fireball have a 25% chance per "
             "rank to generate 8 Felfury.",
             1, 0, 3, {}, connect=["wrath_of_sargeras"],
             proc=felfury_proc("on_crit", 25, 8, filters=["fel_fireball"]),
             source="CoA: 'Critical strikes with Fel Fireball now generate 1 "
                    "Felfury.'"),
        node(I, "cursed_flames", "Cursed Flames",
             "Your critical strikes with Fel Fireball have a 25% chance per "
             "rank to increase your spell critical strike chance by 10% for "
             "2 turns.",
             1, 1, 3, {}, connect=["fel_cannon"],
             proc={"trigger": "on_crit", "chance": 25, "icd": 0,
                   "ability_filter": ["felsworn_fel_fireball"],
                   "apply_effect": {
                       "effect_id": "felsworn_cursed_flames",
                       "name": "Cursed Flames",
                       "effect_type": "buff",
                       "duration": 2,
                       "stat_mods": {"crit_chance_spell": 10.0},
                       "on_target": False}},
             source="CoA: 'Critically striking with Fel Fireball now "
                    "increases the critical strike chance of your next Fel "
                    "Fireball within 10 seconds by 20%.' A crit that buys the "
                    "next crit is a real proc shape here - on_crit with an "
                    "ability_filter and an apply_effect - which is better "
                    "than a flat stat node AND keeps the crit out of the "
                    "tree's permanent budget, which this spec was already "
                    "topping the game in."),
        node(I, "felfire_adept", "Felfire Adept",
             "Increases the damage of Sargeron Smite by 6% per rank.",
             1, 2, 5, {"ability_felsworn_sargeron_smite_damage": 0.06},
             connect=["guldans_prodigy"],
             source="CoA: 'Increases the critical strike chance of Sargeron "
                    "Smite by 10%.' Per-ability crit has no key; per-ability "
                    "damage does."),
        node(I, "nether_spirit", "Nether Spirit",
             "Grants spell critical strike chance equal to 2% of your Spirit "
             "per rank.",
             1, 3, 3, {"crit_chance_spell_from_spirit_pct": 0.02},
             connect=["hidden_power"],
             source="CoA: 'Increases your spell critical strike chance by 20% "
                    "of your Spirit.' A real conversion - crit_chance_spell "
                    "is a live target and spirit a live source. Pairs with "
                    "Hidden Power to make the spec's odd Spirit-first stat "
                    "priority actually true."),

        node(I, "black_magic", "Black Magic",
             "Increases the damage of Ruin and Bane of Chaos by 8% per rank.",
             2, 0, 3, {"ability_felsworn_ruin_damage": 0.08,
                       "ability_felsworn_bane_of_chaos_damage": 0.08},
             connect=["illidari_smiter"],
             source="CoA: 'Increases the damage of your Bane of Chaos and "
                    "Ruin by 10%.'"),
        node(I, "curse_of_argus", "Curse of Argus",
             "Increases all your periodic damage by 4% per rank.",
             2, 1, 3, {"dot_damage": 0.04}, connect=["cursed_flames"],
             source="CoA: 'Each time Bane of Chaos deals damage its damage is "
                    "increased on the target by 1% for 6 seconds, stacking 20 "
                    "times.' A self-ramping DoT has no hook; flat periodic "
                    "damage instead."),
        node(I, "doomsayer", "Doomsayer",
             "Your critical strikes with Sargeron Smite have a 25% chance "
             "per rank to refund 10 Felfury.",
             2, 2, 3, {}, connect=["felfire_adept"],
             proc=felfury_proc("on_crit", 25, 10,
                               filters=["sargeron_smite"]),
             source="CoA: 'Critical strikes with Sargeron Smite now refund 1 "
                    "Felfury. In addition, Sargeron Smite now deals 25% "
                    "increased damage to enemies above 75% of their maximum "
                    "health.' The refund is real; the conditional damage is "
                    "not expressible."),
        node(I, "fel_infusion", "Fel Infusion",
             "Increases your critical strike chance by 1% per rank, with "
             "weapons and with spells.",
             2, 3, 3, {"crit_chance_physical": 1.0, "crit_chance_spell": 1.0},
             connect=["nether_spirit"],
             source="CoA: 'Increases critical strike chance of all party and "
                    "raid members within 100 by 3%... In addition, increases "
                    "your critical strike chance by 3%.' Talents cannot buff "
                    "a party, so the node carries the personal half; the "
                    "party half is the Fel Infusion ABILITY."),

        node(I, "illidari_magi", "Illidari Magi",
             "Your damaging spells have a 12% chance per rank to generate 8 "
             "Felfury.",
             3, 0, 3, {}, connect=["black_magic"],
             proc=felfury_proc("on_damage_cast", 12, 8),
             source="CoA: 'Your periodic damage now has a 20% chance to "
                    "generate 1 Felfury', and the spec note that with this "
                    "specced 'you can spam Felwrath instead of weaving Bane "
                    "into the mix'. Triggers on damage cast rather than on "
                    "each DoT tick, which is the trigger the engine has."),
        node(I, "withering", "Withering",
             "Increases your spell damage by 2% and the damage your spells "
             "deal to additional targets by 2% per rank.",
             3, 1, 3, {"spell_damage": 0.02, "aoe_damage": 0.02},
             connect=["curse_of_argus"],
             source="CoA: 'Your Fel Fireballs used with Felforged active now "
                    "deal 30% increased damage.' Felforged is itself a proc; "
                    "a proc gating a damage bonus is two hooks deep, so this "
                    "is flat."),
        node(I, "archimondes_wrath", "Archimonde's Wrath",
             "Increases your spell critical strike damage by 3% per rank.",
             3, 2, 3, {"crit_damage_spell": 0.03},
             connect=["doomsayer"],
             source="CoA: 'Increases the critical strike chance of your "
                    "Felfury spenders by 1% for every 10 points of Energy you "
                    "have at the time of casting.' Crit that scales off the "
                    "resource you are sitting on has no hook, and there is no "
                    "Energy pool here anyway."),
        node(I, "reckoning", "Reckoning",
             "Increases the damage your spells deal to additional targets by "
             "3% per rank.",
             3, 3, 3, {"aoe_damage": 0.03}, connect=["fel_infusion"],
             source="CoA class tree: 'For 10 seconds, your Fel Fireball is "
                    "free of cost, instant cast, and strikes up to 4 "
                    "targets.' Fel Fireball is already free and instant, so "
                    "what is left of Reckoning is the multi-target half."),

        node(I, "infernal_summoner", "Infernal Summoner",
             "Your damaging spells have a 5% chance per rank to reset the "
             "cooldown of Infernal.",
             4, 0, 3, {}, connect=["illidari_magi"],
             proc={"trigger": "on_damage_cast", "chance": 5, "icd": 3,
                   "reset_cooldown": {"ability": "felsworn_infernal"}},
             source="CoA: 'Direct damage dealt now has a 5% chance to reset "
                    "the cooldown of Infernal.'"),
        node(I, "herald_of_the_legion", "Herald of the Legion",
             "Increases the damage your spells deal to additional targets by "
             "4% and your periodic damage by 3% per rank.",
             4, 1, 3, {"aoe_damage": 0.04, "dot_damage": 0.03},
             connect=["withering"],
             source="CoA: 'Damage dealt by Bane of Chaos now radiates fel "
                    "energy around the enemy, dealing 50% of the damage dealt "
                    "to up to 8 nearby enemies.' A DoT that splashes has no "
                    "hook, so the node pays in cleave and periodic damage."),
        node(I, "dark_magician", "Dark Magician",
             "Reduces the Felfury cost of your abilities by 3% per rank.",
             4, 2, 3, {"all_ability_cost_pct": 0.03},
             connect=["archimondes_wrath"],
             source="CoA: 'While Inner Demon is active, casting Ruin, Sunder, "
                    "or Felwrath now refunds 20 Energy.' With one pool and no "
                    "window conditional, a cost reduction is the same thing "
                    "from the player's side. NOTE THE SIGN: "
                    "Ability.talented_cost computes cost * (1.0 - pct), so a "
                    "POSITIVE all_ability_cost_pct is the discount. Authored "
                    "negative here first and measured: every cost went UP "
                    "15%. data/talents/guardian_vanguard.json's Seasoned "
                    "Fighter still ships at -0.03 with the tooltip 'Reduces "
                    "the Energy cost of your abilities by 3% per rank', so it "
                    "currently makes that spec 15% more expensive at 5/5."),

        node(I, "manari_teachings", "Man'ari Teachings",
             "Increases your spell critical strike damage by 5% per rank.",
             5, 0, 2, {"crit_damage_spell": 0.05},
             connect=["infernal_summoner"], total_slots=3,
             source="CoA: 'Level 50 Passive. Increases your critical damage "
                    "dealt by 100%.' CoA hands this out free at 50; Frontier "
                    "has no free passives, so it costs points and is sized "
                    "like a talent rather than a level reward."),
        node(I, "oppressive_ruin", "Oppressive Ruin",
             "Increases the damage of Ruin by 8% per rank.",
             5, 1, 2, {"ability_felsworn_ruin_damage": 0.08},
             connect=["herald_of_the_legion"], total_slots=3,
             source="CoA: 'Damage dealt by Ruin now absorbs the next 99 "
                    "healing on the target.' No healing-absorb key exists, so "
                    "Ruin simply hits harder."),
        node(I, "unphased", "Unphased",
             "Increases your spell penetration by 4 per rank.",
             5, 2, 3, {"spell_penetration": 4},
             connect=["dark_magician"], total_slots=3,
             source="CoA: 'Level 40 Passive. Increases your spell penetration "
                    "by 20, scaling with your level. In addition, reduces "
                    "spell pushback suffered from damaging attacks by 50% "
                    "while Inner Demon is active.' spell_penetration is real "
                    "and read on both Character and Monster mitigation; there "
                    "is no cast pushback to reduce."),

        node(I, "malice_of_guldan", "Malice of Gul'dan",
             "Everything you land now sets something burning behind it.",
             6, 0, 1, {"crit_chance_spell": 3.0, "crit_damage_spell": 0.08},
             node_type="active",
             connect=["manari_teachings", "oppressive_ruin", "unphased"],
             proc={"trigger": "on_crit", "chance": 40, "icd": 1,
                   "cast_ability": "felsworn_felstrike"},
             total_slots=1,
             source="Capstone. CoA names it as the endgame pick outright: "
                    "'At that crit level, drop Chaotic Intuition for Malice "
                    "of Gul'dan, since Malice procs Felstrikes off your crits "
                    "and out-scales the longer a fight runs.' cast_ability is "
                    "the engine's real free-cast payload, so this one lands "
                    "exactly as described."),
    ],
    "Built from reference/coa_sidekick/SPEC_felsworn__infernal.txt and the "
    "infernal block of reference/coa_sidekick/talents/felsworn.json. CoA's "
    "top-rated Felsworn spec (Dungeon A, Raid S, Arena A, BG S) and 'a ranged "
    "Felfury-builder-spender caster driven off Spell Power'. The unusual "
    "thing about it, and the reason Hidden Power and Nether Spirit are the "
    "two biggest nodes in the tree, is the stat priority: SPIRIT > Critical "
    "Strike > Intellect > Spell Power > Haste. Spirit is a damage stat here "
    "and a crit stat on top of that, which no other caster in the game does. "
    "CoA is also explicit that the self-healing is thin on purpose - "
    "'Manafeed is your only heal' - so the tree has no sustain node at all.")


# ================================================================= Tyrant
T = "felsworn_tyrant"
TYRANT = tree(
    T, "Felsworn Tyrant",
    "Avoidance tank - dodge and parry are the chassis, Felfury comes back "
    "from being hit, and the party gets a cut of your cooldowns.",
    [
        node(T, "nether_disciple", "Nether Disciple",
             "Increases your chance to dodge and to parry by 1% per rank.",
             0, 0, 5, {"dodge": 1.0, "parry": 1.0},
             source="CoA: 'Increases your dodge and parry chance by 3%.' This "
                    "spec has no shield and no block, so dodge and parry are "
                    "the whole avoidance story - CoA: 'The defense is "
                    "anchored to dodge and parry.'"),
        node(T, "demon_hide", "Demon Hide",
             "Increases your Armor by 5% per rank.",
             0, 1, 5, {"armor_pct": 5.0},
             source="CoA: 'While Inner Demon is active, your Armor "
                    "contribution from cloth and leather items is increased "
                    "by 120%.' No per-armour-class key and no window "
                    "conditional, so it is unconditional Armor. Sized large "
                    "on purpose: this is the only tank in the game in "
                    "leather with no shield AND no form, and the note at the "
                    "top of combat/forms.py says armor_pct is exactly the "
                    "lever a shieldless sub-plate tank is meant to be "
                    "balanced with (Bear and Beetle Form carry 70% and 22% "
                    "for the same reason). With Burning Commander this tree "
                    "reaches 35 armor_pct, the same as Guardian Vanguard, "
                    "which needs less because it wears plate and carries a "
                    "shield. armor_pct is PERCENT POINTS, not a fraction."),
        node(T, "burning_legionnaire", "Burning Legionnaire",
             "Reduces the Felfury cost of your abilities by 3% per rank.",
             0, 2, 5, {"all_ability_cost_pct": 0.03},
             source="CoA: 'Reduces the Energy cost of Twin Slice and Sunder "
                    "by -10.' One pool here, so it is a general cost cut - "
                    "which this spec needs, because CoA's own weakness list "
                    "says its resource income dries up the moment it stops "
                    "being the focus. POSITIVE is the discount - see Dark "
                    "Magician in felsworn_infernal for the measurement."),
        node(T, "infernal_constitution", "Infernal Constitution",
             "Increases your total health by 3% per rank.",
             0, 3, 5, {"max_health_pct": 0.03},
             source="CoA: 'Increases your maximum health by 10% and increases "
                    "your off-hand weapon damage by 30%.' NOTE "
                    "max_health_pct is a FRACTION - health * (1.0 + value) - "
                    "not percent points like armor_pct. Guardian shipped this "
                    "key at 2.0 and granted +200% health a rank, reaching "
                    "99,156 effective HP against the next tank's 2,987; "
                    "tools/validate_class.py now fails a value that far off "
                    "convention."),

        node(T, "hulking_demon", "Hulking Demon",
             "Grants attack power equal to 3% of your Stamina, and 1 hit "
             "rating, per rank.",
             1, 0, 5, {"ap_from_stamina_pct": 0.03, "hit_rating": 1},
             connect=["nether_disciple"],
             source="CoA: 'Increases your attack power by 30% of your Stamina "
                    "and your hit rating by 6% of your Agility.' The Stamina "
                    "half is a real conversion; hit_rating cannot be a "
                    "conversion target (it is a local feeding "
                    "base_miss_chance_*), so it is flat. CoA puts Hit first "
                    "in this spec's stat priority, which is why it is here at "
                    "all."),
        node(T, "pure_hatred", "Pure Hatred",
             "Increases your Stamina by 2% per rank.",
             1, 1, 3, {"stamina_pct": 2.0}, connect=["demon_hide"],
             source="CoA: 'Your Hateforged Barrier now also scales with your "
                    "dodge rating.' Hateforged Barrier absorbs a share of max "
                    "health, which is Stamina-derived, so Stamina is the one "
                    "stat that really does make the barrier bigger here. The "
                    "dodge-scaling half has no hook."),
        node(T, "dark_lord", "Dark Lord",
             "Reduces all damage you take by 1% and increases your physical "
             "damage by 2% per rank.",
             1, 2, 3, {"damage_taken_pct": -0.01, "physical_damage": 0.02},
             connect=["burning_legionnaire"],
             source="CoA: 'While above 75% health, your damage taken is "
                    "reduced by -5% and damage dealt is increased by 5%.' The "
                    "engine has a low_health_* conditional pair and nothing "
                    "for the other direction, so both halves are "
                    "unconditional at a smaller value. damage_taken_pct is a "
                    "FRACTION."),
        node(T, "felblade", "Felblade",
             "Grants spell power equal to 2% of your Agility per rank.",
             1, 3, 5, {"spell_damage_from_agility_pct": 0.02},
             connect=["infernal_constitution"],
             source="CoA: 'Level 40 Passive. Damage dealt by Fel Fireball, "
                    "Sargeron Smite, and Twin Slice now additionally scales "
                    "with your Agility.' The spell side of that is a real "
                    "conversion; the physical abilities already scale off "
                    "Agility through attack power."),

        node(T, "illidari_training", "Illidari Training",
             "Damage you take has a 20% chance per rank to generate 8 "
             "Felfury.",
             2, 0, 3, {}, connect=["hulking_demon"],
             proc=felfury_proc("on_damage_taken", 20, 8),
             source="CoA: 'Dodging an attack now generates 3 Energy', and "
                    "'Resource income comes from being hit, through Illidari "
                    "Training's dodge-to-Energy'. There is no on-dodge "
                    "trigger, so on_damage_taken carries it - the same "
                    "trigger Warrior Protection's Shield Specialization "
                    "already uses for exactly this."),
        node(T, "unholy_endurance", "Unholy Endurance",
             "Increases the damage of Carve by 8% and your threat generation "
             "by 4% per rank.",
             2, 1, 3, {"ability_felsworn_carve_damage": 0.08,
                       "threat_generation_pct": 0.04},
             connect=["pure_hatred"],
             source="CoA: 'Increases the damage and threat generated from "
                    "Carve by 15%.' Note the key: threat_generation_pct as a "
                    "TALENT effect is a fraction and only started working in "
                    "992ed62 - every threat talent in the game read a key the "
                    "combat engine did not."),
        node(T, "vengeance", "Vengeance",
             "Twin Slice and Felrend have a 20% chance per rank to generate "
             "5 extra Felfury.",
             2, 2, 3, {}, connect=["dark_lord"],
             proc=felfury_proc("on_damage_cast", 20, 5,
                               filters=["twin_slice", "felrend"]),
             source="CoA: 'Your Twin Slice and Felrend now have a 60% chance "
                    "to generate 1 additional Felfury.' 3 ranks at 20% is "
                    "CoA's 60% exactly, because _sync_talent_procs scales a "
                    "proc's chance by points_spent."),
        node(T, "burning_commander", "Burning Commander",
             "Increases your Armor by 2%, and grants a further Armor equal "
             "to 2% of your Agility, per rank.",
             2, 3, 5, {"armor_pct": 2.0, "armor_from_agility_pct": 0.02},
             connect=["felblade"],
             source="CoA: 'Level 10 Passive. Allows you to wield a Two-Handed "
                    "Axe, Mace, or Sword in each hand and grants you "
                    "additional Armor and magic resistance based on your "
                    "dodge rating.' Weapon proficiency is set in "
                    "weapon_types.json, not by a talent, and dodge rating is "
                    "not a conversion source - Agility, which feeds dodge, "
                    "is. The magic-resistance half is dropped."),

        node(T, "demonic_fortitude", "Demonic Fortitude",
             "While below 35% health, you take 8% less damage per rank.",
             3, 0, 3, {"low_health_damage_reduction_pct": 0.08,
                       "low_health_threshold_pct": 0.35},
             connect=["illidari_training"],
             source="CoA: 'While Demonic Will or Hateforged Barrier are "
                    "active, all damage taken or avoided now has a 20% chance "
                    "to generate 1 Felfury.' Illidari Training already covers "
                    "damage-taken-to-Felfury, and a while-a-defensive-is-up "
                    "conditional has no hook, so this node takes the "
                    "engine's real last-stand pair instead - the thing a tank "
                    "tree needs and CoA's version of the spec gets from "
                    "Tyrannical Resolve."),
        node(T, "straight_to_the_nether", "Straight to the Nether",
             "Carve and Sargeron Smite have a 34% chance per rank to leech "
             "10% of the damage dealt as health.",
             3, 1, 3, {}, connect=["unholy_endurance"],
             proc={"trigger": "on_damage_cast", "chance": 34, "icd": 0,
                   "ability_filter": ["felsworn_carve",
                                      "felsworn_sargeron_smite"],
                   "leech_pct": {"pct": 0.10}},
             source="CoA: 'While Inner Demon is active, Carve and Sargeron "
                    "Smite now leeches 20% of the damage dealt from the "
                    "initial strike as Shadowflame Damage', and 'Sustain "
                    "hangs on channeling Carve, your biggest heal window "
                    "through Straight to the Nether's leech'. Window-gating "
                    "is not expressible, so the rate is halved and made "
                    "chance-based."),
        node(T, "expose", "Expose",
             "Your damaging abilities have a 34% chance per rank to leave "
             "the target taking 4% more physical damage for 3 turns.",
             3, 2, 3, {}, connect=["vengeance"],
             proc={"trigger": "on_damage_cast", "chance": 34, "icd": 1,
                   "apply_effect": {
                       "effect_id": "felsworn_expose",
                       "name": "Expose",
                       "effect_type": "debuff",
                       "duration": 3,
                       "stat_mods": {"physical_damage_taken_pct": 4.0},
                       "on_target": True}},
             source="PHYSICAL_DAMAGE_TAKEN_PCT IN A STATUS STAT_MOD IS IN PERCENT "
                    "POINTS, NOT A FRACTION. This was 0.04, i.e. +0.04% "
                    "instead of +4%, so the debuff did nothing measurable "
                    "- verified by applying it and taking a 1000-damage "
                    "hit: 0.04 gave 736, 4.0 gives 766. Note that the "
                    "bare damage_taken_pct key beside it IS a fraction, "
                    "and so is block_value_pct; the convention is per-key "
                    "with no naming rule, so check how the engine reads "
                    "the exact key before authoring a value. "
                    "CoA: 'Damage taken from the Felsworn increased by 10% "
                    "and the critical strike chance of all allies against "
                    "this target is increased by 3%.' The ally-crit half "
                    "cannot be scoped to a target, so only the "
                    "damage-amplification half ships."),
        node(T, "betrayer", "Betrayer",
             "Blows that land on you are answered with an off-hand strike "
             "for 70 damage, 15% of the time per rank.",
             3, 3, 2, {}, connect=["burning_commander"],
             proc={"trigger": "on_damage_taken", "chance": 15, "icd": 0,
                   "damage_flat": 70},
             source="CoA: 'Dodging attacks causes 40% off-hand Weapon Damage "
                    "to attackers and enrages your party and raid members "
                    "within 20 yds, increasing their critical strike chance "
                    "by 2%.' No on-dodge trigger and no party-scoped proc "
                    "payload, so only the counter-strike survives."),

        node(T, "bulwark_of_azzinoth", "Bulwark of Azzinoth",
             "Reduces all damage you take by 2% per rank.",
             4, 0, 3, {"damage_taken_pct": -0.02},
             connect=["demonic_fortitude"],
             source="CoA: 'Inner Demon now also reduces your damage taken by "
                    "-10%.' No window conditional, so it is always on at a "
                    "fifth the value."),
        node(T, "grommashs_folly", "Grommash's Folly",
             "Your critical strikes have a 34% chance per rank to heal you "
             "for 70.",
             4, 1, 3, {}, connect=["straight_to_the_nether"],
             proc={"trigger": "on_crit", "chance": 34, "icd": 0,
                   "heal_flat": 70},
             source="CoA: 'you now heal equal to 50% of all damage dealt by "
                    "critical strikes with auto attacks', 'Grommash's Folly "
                    "heals off crits during Inner Demon'. A flat heal rather "
                    "than a share of the hit, because heal_flat is what the "
                    "on_crit trigger carries."),
        node(T, "abyssal_conditioning", "Abyssal Conditioning",
             "Increases your haste by 1 and your threat generation by 5% per "
             "rank.",
             4, 2, 3, {"haste": 1.0, "threat_generation_pct": 0.05},
             connect=["expose"],
             source="CoA: 'Casting Felfury spenders now increases your Energy "
                    "regeneration by 5% for 10 seconds, stacking up to 4 "
                    "times.' Felfury has no regeneration to speed up, so the "
                    "node buys turns instead - haste, plus the threat a "
                    "dungeon tank wants out of them."),

        node(T, "fel_monstrosity", "Fel Monstrosity",
             "Increases your Stamina by 3% per rank.",
             5, 0, 2, {"stamina_pct": 3.0}, connect=["bulwark_of_azzinoth"],
             total_slots=3,
             source="CoA: 'Level 50 Passive. Increases your Stamina by 25% "
                    "and size by 10%.' Frontier has no free passives, so it "
                    "costs points; there is no character scale to change."),
        node(T, "mannoroths_rage", "Mannoroth's Rage",
             "Reduces the cooldown of Burning Hatred by 15% per rank.",
             5, 1, 2,
             {"ability_felsworn_burning_hatred_cooldown_pct": 0.15},
             connect=["grommashs_folly"], total_slots=3,
             source="CoA: 'Reduces the cooldown of Burning Hatred by -60 sec "
                    "and removes its Energy cost.' Burning Hatred is already "
                    "free here, so the node is purely the cooldown."),
        node(T, "taskmasters_army", "Taskmaster's Army",
             "Infernal Whipcrack lasts 1 turn longer per rank.",
             5, 2, 2,
             {"ability_felsworn_infernal_whipcrack_duration": 1},
             connect=["abyssal_conditioning"], total_slots=3,
             source="CoA: 'Reduces the cooldown of Infernal Whipcrack by -30 "
                    "sec and it now affects all allies and its radius is "
                    "increased by 15 yds.' buff_scope party already reaches "
                    "the whole group, so the node buys uptime instead."),

        node(T, "vengeance_is_mine", "Vengeance Is Mine",
             "They have been hitting you for a while now. It has been going "
             "into something.",
             6, 0, 1, {"damage_taken_pct": -0.06, "dodge": 3.0},
             node_type="active",
             connect=["fel_monstrosity", "mannoroths_rage",
                      "taskmasters_army"],
             proc={"trigger": "on_damage_taken", "chance": 25, "icd": 1,
                   "grant_resource": {"resource": "felfury", "amount": 15}},
             total_slots=1,
             source="Capstone. CoA: 'Dodging or parrying an attack now gives "
                    "you a 10% chance to make your next 10 instances of "
                    "damage with Twin Slice deal 30% increased damage and "
                    "generate 1 Felfury.' Kept as the thing CoA says this "
                    "spec lives and dies on - mitigation plus avoidance plus "
                    "resource off being hit - since its listed weakness is "
                    "that 'Resource income comes from being hit... Stop being "
                    "the focus and your Energy and Felfury dry up right when "
                    "you want to fight back'."),
    ],
    "Built from reference/coa_sidekick/SPEC_felsworn__tyrant.txt and the "
    "tyrant block of reference/coa_sidekick/talents/felsworn.json. CoA rates "
    "it Dungeon A / Raid S / Arena S / BG S and calls it 'a Vengeance-DH "
    "self-sustain tank with a raid-buff layer stapled on'. Two things shape "
    "the tree. First, there is no shield anywhere in this spec, so every "
    "point that would go to block in a plate tree goes to dodge, parry or "
    "flat Armor instead - its stat priority ends on 'Dodge Rating (fuels "
    "self-buff scaling)'. Second, CoA's own weakness list says the resource "
    "economy only works while something is meleeing you, which is why "
    "Illidari Training, Vengeance and the capstone are all Felfury procs and "
    "why Burning Legionnaire's cost reduction sits in tier 0. The "
    "group-facing layer (Infernal Whipcrack, Eye of the Tyrant, Doomscarring) "
    "lives in the ability kit, because talents cannot buff a party.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the files")
    args = parser.parse_args()

    ability_doc = {
        "class": "Felsworn",
        "_source_note": __doc__.strip().split("\n\n")[1].replace("\n", " "),
        "_implementation_note": (
            "AoE abilities use target_type 'enemy_aoe' plus max_targets, NOT "
            "an is_aoe flag. is_aoe is a Monster-ability field "
            "(entities/monster.py); combat/abilities.py's "
            "_ability_from_data never reads it for a player ability, and "
            "Ability._apply_effect decides AoE off "
            "target_type == 'enemy_aoe'. The seven is_aoe flags currently in "
            "data/abilities/guardian.json therefore do nothing, and those "
            "abilities hit one target."),
        "abilities": ABILITIES,
    }

    targets = [
        (ROOT / "data/abilities/felsworn.json", ability_doc),
        (ROOT / "data/talents/felsworn_slayer.json", SLAYER),
        (ROOT / "data/talents/felsworn_infernal.json", INFERNAL),
        (ROOT / "data/talents/felsworn_tyrant.json", TYRANT),
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
