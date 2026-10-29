#!/usr/bin/env python3
"""Author the Ranger: ability kit + three talent trees.

    PYTHONPATH=. python3 tools/build_ranger.py [--apply]

Ranger is one of the twelve CoA classes that shipped with base stats, armour
type, weapon proficiency and a resource but no abilities and no talents, so it
could not be selected. Built as a sibling of tools/build_guardian.py and to
the same rules.

SOURCE. reference/coa_sidekick/CLASS_ranger.txt, the three
SPEC_ranger__*.txt pages, and reference/coa_sidekick/talents/ranger.json
(the real talent trees: 39 class-tree nodes plus 40/40/45 per spec). Every
ability and talent name below is a real CoA name off those pages. Identity
per that reference:

  Archery     RANGED DPS    "Closest to retail Marksmanship Hunter." A pure
                            builder-spender bow kit with no support layer at
                            all: no auras, no party buffs, no healing. Silence
                            into burst into an execute. Raid S, Arena D.
  Brigand     MELEE DPS     "Assassination Rogue crossed with Outlaw's utility
                            toolkit." Daggers in melee range, bleeds feeding
                            bonus-damage strikes, and more hard CC than a pure
                            DPS kit normally gets.
  Farstrider  RANGED DPS    "Closest to Augmentation Evoker." Horns and party
              SUPPORT       auras layered over a real ranged rotation, with
                            summoned War Falcons and nature arrows. Its damage
                            is middling on purpose; the party is the payoff.

NUMBERS ARE FRONTIER'S, NOT CoA'S. The reference gives identity, role and
rotation shape; it is a fan-made planning tool whose own disclaimer says COA
is pre-meta. Damage curves copy Hunter's and Rogue's shipped shape
(steady_shot / sinister_strike: 9 ranks at levels 1/6/12/18/24/32/40/48/56,
flat resource cost, linear growth) because Ranger is the other leather
Agility class and should scale alongside them rather than on a curve of its
own invention.

ARCHERY POINTS. Taken from CLASS_RESOURCE_MAP in combat/abilities.py:
(ResourceType.ARCHERY_POINTS, None), whose own comment reads "Ranger: banks
toward a payoff". Two things about that pool shape the whole kit:

  1. It is DICT-BACKED. archery_points is not in Character._RESOURCE_ATTRS,
     so it lives in Character.secondary_resources, caps at 100
     (SECONDARY_RESOURCE_MAX) and starts a new character at ZERO.
  2. It has NO REGENERATION. Character.restore_resources_between_turns only
     regenerates Energy (+25/turn) and Mana (Spirit-based);
     restore_resources_out_of_combat_step only Energy. Nothing anywhere
     refills archery_points.

So the kit cannot be priced "against the regen" the way Guardian's Energy is,
because the regen is zero. The only engine-supported source is an ability's
`generates` field (Ability._generate_resource), which is exactly CoA's own
loop: in CoA, Quick Shot costs Focus and banks ADVANTAGE, and the spenders
eat Advantage. Frontier collapses Focus and Advantage into one pool, so the
honest translation is:

  BUILDERS cost 0 and generate 12-15 Archery Points. Quick Shot (all specs),
  Hunting Shot (Archery), Ravage and Wild Strike (Brigand).
  SPENDERS cost a FLAT 15-40 across every rank. Three builders pay for one
  big spender, which is the 5-stack Advantage window CoA's rotations describe.

Nothing costs more than 40, so no rank of anything is ever uncastable, and
the combat probe can always act because Attack and the builders are free.

Talent effect keys are restricted to ones the engine actually reads, verified
with tools/validate_class.py (liveness delegated to tools/audit_talents.py).
Casualties worth recording, each noted again on the node that hit it:

  silenced / rooted   Seven shipped abilities across five classes set these
                      as debuff stat_mods and NOTHING reads either one. So
                      Neurotoxin Arrow's silence, Whipvine Arrow's root and
                      Throatpunch's school lockout cannot be modelled. They
                      carry a haste reduction instead, which is what a snare
                      actually buys in a turn engine.
  party talent buffs  Talent effects resolve against the owning Character
                      only (Character.get_talent_effects), so Brigand's Guile
                      of the Cutthroat and Farstrider's Command Aura cannot
                      hand the party anything from a talent node. The two
                      specs' real party buffs are ABILITIES instead, and
                      those nodes carry the self half of their tooltip.
  bleed_dot_damage    Live, but Ability._damage_multiplier only adds it when
                      the literal substring "bleed" is in the ability_id, so
                      it would be dead against ranger_serrated_shot and
                      ranger_ravage. Those nodes use dot_damage. The one
                      place the flavour keys DO work is
                      ranger_queldorei_poison, whose id carries "poison".
  ranged AP scaling   There is no ranged_attack_power_pct key, and a flat
                      ranged_attack_power talent effect is silently dropped:
                      Character._recalculate_derived_stats computes
                      ranged_attack_power from Agility and Strength and never
                      adds a bonus-pool term for it (unlike attack_power).
                      It passes the liveness check because "ranged_attack_
                      power" appears as a string literal in get_stat_sheet.
                      Archery's Sharpshooter uses the real conversion key,
                      ranged_ap_from_agility_pct, which does work.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Hunter's and Rogue's shipped rank schedule - see module docstring.
RANK_LEVELS = [1, 6, 12, 18, 24, 32, 40, 48, 56]


def ranks(base, step, cost, start=1, count=9, **extra):
    """Flat-cost rank table on the Hunter/Rogue schedule, starting at `start`.

    Levels past the 9-rank schedule are spaced evenly to stay under 58 so
    every rank is actually reachable at the level 60 cap. `extra` keys are
    copied onto every rank dict, which is how restore_resource abilities
    carry mana_restore_pct (a real rank key read by Ability.mana_restore_pct,
    NOT effect_value - Guardian's Knight's Calling restores 0 because it set
    effect_value and left mana_restore_pct unset).
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
        rank.update({k: (v[i] if isinstance(v, list) else v)
                     for k, v in extra.items()})
        out.append(rank)
    return out


def one(level, cost, value=0, **extra):
    """Single-rank table, for abilities whose rank carries no magnitude.

    Only correct for effect_types that ignore effect_value entirely
    (summon_pet, dispel). Buffs and debuffs must use full() - see below.
    """
    rank = {"rank": 1, "level_req": level, "cost": cost, "effect_value": value}
    rank.update(extra)
    return [rank]


def full(level, cost, scale=100, **extra):
    """Single-rank table for a BUFF or DEBUFF, at full strength.

    A buff's and a debuff's effect_value is not a magnitude, it is a PERCENT
    SCALAR applied to the ability's whole stat_mods dict:

        scaled = v * (self.effect_value / 100.0)     - Ability._apply_effect

    so 100 means "the stat_mods as written" and 0 means the buff silently
    does nothing at all. Every shipped class follows it (hunter_aspect_of_
    the_hawk ranks 33/56/78/100, rogue_evasion 43/71/100,
    warrior_shield_wall 100), and it is easy to miss because the rank dict
    still validates, the buff still applies, and the status effect still
    shows up on the character with a stat_mods dict full of zeroes. The
    whole Ranger buff suite was authored at 0 on the first pass and every
    one of the twenty was inert; the shipped Guardian has the same problem
    across all eighteen of its buffs and debuffs, including Raise Shield,
    Bastion, both Formations, both taunts and all three Decrees.
    """
    rank = {"rank": 1, "level_req": level, "cost": cost, "effect_value": scale}
    rank.update(extra)
    return [rank]


def banks(amount):
    """An ability's `generates` payload. The only source of Archery Points."""
    return {"resource": "archery_points", "amount": amount}


#: The three ranged weapon types a Ranger can carry (weapon_types.json's
#: class_weapon_map for Ranger is sword_1h/dagger/fist_weapon/thrown/bow/gun/
#: crossbow). Passed as a LIST, never as `true`: Ability.
#: is_ranged_weapon_ready compares the equipped weapon_type against this
#: value, so requires_ranged_weapon: true would resolve to
#: `equipped_type == True` and make the ability permanently uncastable.
BOW_GUN_CROSSBOW = ["bow", "gun", "crossbow"]


def ability(aid, name, effect_type, description, rank_table, *, cooldown=0,
            duration=0, stat_mods=None, icon=None, source=None, **extra):
    out = {
        "ability_id": f"ranger_{aid}",
        "name": name,
        "resource_type": "archery_points",
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
# Order is roughly the order a player meets them. Attack comes first because
# validate_class.py's combat probe walks the spellbook in order and stops on
# the first ability that successfully executes.
ABILITIES = [
    ability("attack", "Attack", "damage",
            "A measured strike with your weapon.", one(1, 0, 0),
            icon="ability_melee",
            source="Convention: every class ships a free rank-1 Attack. "
                   "Also the target of extra_attack procs, which look up "
                   "'<class_prefix>_attack' by name (see "
                   "StatusEffectMixin.fire_proc_trigger) - Brigand's Tip of "
                   "the Spear needs this id to exist."),

    # ---- class chassis: the CoA class tree's own abilities, all three specs
    ability("quick_shot", "Quick Shot", "ranged_damage",
            "A fast, flat shot. Nothing clever, and it keeps your quiver "
            "working.",
            ranks(36, 9, 0), target_type="enemy", generates=banks(12),
            source="CoA: 'Spam Quick Shot ... at range while banking "
                   "Advantage stacks'. The baseline builder for Archery and "
                   "Farstrider and the class's only level-1 shot, so it is "
                   "free and generates - see the module docstring on why "
                   "builders cannot cost anything. Hunter steady_shot's "
                   "9-rank curve, flattened because it is the cheap filler."),
    ability("skullpiercer", "Skullpiercer", "ranged_damage",
            "Put the arrow through the gap in their helm.",
            ranks(70, 20, 40, start=20, count=6), cooldown=3,
            target_type="enemy",
            source="CoA names Skullpiercer as the hardest-hitting Advantage "
                   "spender in all three specs ('Spend Skullpiercer at 5 "
                   "Advantage as your hardest scaling nuke'). The most "
                   "expensive thing in the kit at 40, which is three "
                   "builders' worth."),
    ability("toxic_dart", "Toxic Dart", "dot",
            "A dart dipped in something that does not stop working when it "
            "lands.",
            ranks(50, 16, 20, start=8, count=7), cooldown=2, duration=3,
            target_type="enemy",
            source="CoA lists Toxic Dart in all three specs' rotations. Left "
                   "as a PHYSICAL dot rather than a nature-school one: "
                   "Ability._apply_effect routes a schooled dot through the "
                   "spell-power/spell-hit path, and a Ranger has no spell "
                   "power, so a 'real' poison school would quietly make the "
                   "class's own poison its weakest ability."),
    ability("crippling_shot", "Crippling Shot", "debuff",
            "An arrow through the leg. They will still come, slower.",
            one(12, 15), cooldown=4, duration=2,
            stat_mods={"haste": -30.0}, target_type="enemy",
            source="CoA class tree: 'slowing movement speed by -50% and "
                   "knocking them off their mounts'. There is no movement "
                   "speed in a turn engine; a haste cut is the same thing "
                   "here, and haste on a debuff is read live by "
                   "turn_meter.py's get_status_stat_mod('haste')."),
    ability("snapseed", "Snapseed", "ranged_damage",
            "A seed pod that bursts hard enough to put someone on their back.",
            ranks(40, 12, 15, start=6, count=7), cooldown=2,
            target_type="enemy",
            source="CoA class tree: 'Toss a snapseed at an enemy, dealing "
                   "ranged AP Physical damage and knocking them back'. The "
                   "knockback has no engine hook."),
    ability("cutthroat", "Cutthroat", "ranged_damage",
            "A heavy arrow placed where it takes the fight out of them for a "
            "moment.",
            ranks(54, 16, 25, start=16, count=6), cooldown=5,
            target_type="enemy", is_stun=True,
            source="CoA class tree: 'Shoot a powerful arrow that deals Weapon "
                   "Damage plus 40 and stuns the target for 1 seconds'."),
    ability("knockout", "Knockout", "debuff",
            "They go down, and whatever was eating at them goes with them.",
            one(22, 20), cooldown=6, duration=2, is_stun=True,
            stat_mods={"haste": -25.0}, target_type="enemy",
            source="CoA class tree: 'Knock an enemy out, incapacitating them "
                   "for 4 seconds and removing bleed and poison effects from "
                   "them'. is_stun carries the incapacitate. Stripping the "
                   "target's own DoTs would need a hostile dispel, which "
                   "effect_type 'dispel' does not do (it cleanses allies)."),
    ability("briar_veil", "Briar Veil", "buff",
            "Thorns and leaves come up around you and nothing quite lands.",
            one(10, 15), cooldown=5, duration=2,
            stat_mods={"dodge": 25.0}, target_type="self", buff_scope="combat",
            source="CoA class tree: 'increasing your dodge chance by 50% and "
                   "causing dodging attacks to restore 2% maximum health and "
                   "5 Focus'. The dodge is real; the on-dodge refund has no "
                   "proc trigger (the engine dispatches on_damage_taken, not "
                   "on_avoid)."),
    ability("adrenaline_rush", "Adrenaline Rush", "buff",
            "Everything speeds up except you, which is the point.",
            one(26, 20), cooldown=10, duration=3,
            stat_mods={"haste": 20.0}, target_type="self", buff_scope="combat",
            source="CoA class tree: 'Surge with vitality, dispeling all "
                   "harmful effects from yourself and increasing your "
                   "movement speed by 40%'. One ability cannot both buff and "
                   "dispel, so this is the haste window CoA's Archery "
                   "rotation presses ('Adrenaline Rush open distance')."),
    ability("elude", "Elude", "buff",
            "You stop being somewhere they are looking.",
            one(18, 15), cooldown=6, duration=2,
            stat_mods={"crit_chance_physical": 15.0}, target_type="self",
            buff_scope="combat",
            source="CoA gates a third of the class tree behind Elude "
                   "('Elude stealth-window abilities'). There is no stealth "
                   "in this engine, so Elude lands as the opener window its "
                   "own talents describe - CoA's Woodland Stalker is 'While "
                   "in Elude, your critical strike chance is increased by "
                   "20%'."),
    ability("snatch", "Snatch", "debuff",
            "Their weapon is in your hand now. They are taking it badly.",
            one(24, 15), cooldown=6, duration=2,
            stat_mods={"attack_power": -45}, target_type="enemy",
            source="CoA class tree: 'Snatch an enemy's melee weapons, "
                   "disarming them for 4 seconds'. Disarm is not a state the "
                   "engine tracks; an attack power debuff is what a disarm "
                   "costs the target."),
    ability("survival_potion", "Survival Potion", "heal",
            "Bitter, and it works.",
            ranks(170, 90, 0, start=14, count=6), cooldown=8,
            target_type="self",
            source="CoA class tree: the panic button, 'dispelling all poison "
                   "and disease effects'. Free because it is a potion. Costed "
                   "at 0 Archery Points deliberately: a Ranger who has spent "
                   "the bank and is about to die should not be unable to "
                   "drink."),
    ability("instinct", "Instinct", "restore_resource",
            "You stop thinking about the shot and simply take it.",
            ranks(0, 0, 0, start=10, count=5, mana_restore_pct=[25, 30, 35, 40, 45]),
            cooldown=8, target_type="self",
            restore_resource_type="archery_points",
            source="CoA: 'Casting Instinct now also restores 40 extra Focus' "
                   "(Brigand) and 'Increases the effectiveness of Instinct'. "
                   "The one ability that refills the bank directly, which "
                   "matters because nothing in the engine regenerates "
                   "archery_points. mana_restore_pct is the rank key "
                   "Ability.mana_restore_pct actually reads - effect_value is "
                   "ignored by the restore_resource branch."),

    # ---- Archery
    ability("precision_shot", "Precision Shot", "ranged_damage",
            "You take the extra half-second and it is worth it.",
            ranks(62, 18, 30, start=10, count=7), cooldown=2,
            target_type="enemy",
            source="CoA: 'Precision Shot (main nuke, scales per stack)'. The "
                   "Aimed Shot of the spec and the thing every Archery talent "
                   "is pointed at."),
    ability("hunting_shot", "Hunting Shot", "ranged_damage",
            "The arrow comes off the first one and finds the next.",
            ranks(34, 9, 0, start=12, count=6), cooldown=2,
            target_type="enemy_aoe", max_targets=3, generates=banks(15),
            source="CoA: 'Fire a shot that ricochets between 3 enemies ... "
                   "Generates 1 stack of Advantage for each enemy hit'. The "
                   "AoE builder, hence free and the largest generator. "
                   "max_targets 3 is the real ricochet count; target_type "
                   "enemy_aoe is what the engine reads for AoE (Ability."
                   "_apply_effect sets is_aoe from target_type, so the "
                   "is_aoe FIELD some shipped abilities carry is inert)."),
    ability("serrated_shot", "Serrated Shot", "dot",
            "A barbed head that does more coming out than going in.",
            ranks(56, 18, 25, start=14, count=6), cooldown=3, duration=3,
            target_type="enemy",
            source="CoA: 'spend into Precision Shot (main nuke) or Serrated "
                   "Shot (bleed)'."),
    ability("deadshot", "Deadshot", "ranged_damage",
            "One arrow, and the fight is over.",
            ranks(130, 38, 20, start=22, count=6), cooldown=3,
            target_type="enemy", execute_threshold_pct=20,
            generates=banks(10), requires_ranged_weapon=BOW_GUN_CROSSBOW,
            source="CoA: 'the sub-20%-HP execute Deadshot', 'Generates 2 "
                   "Advantage'. execute_threshold_pct is PERCENT in this "
                   "engine (Warrior Execute 20, Cultist 35, Primalist 50), "
                   "not a fraction. One of the two abilities gated on a real "
                   "ranged weapon, because CoA defines it purely in Ranged "
                   "Weapon Damage ('250% Ranged Weapon Damage plus 20')."),
    ability("neurotoxin_arrow", "Neurotoxin Arrow", "ranged_damage",
            "Toxin on the head, and the arrow goes through the throat.",
            ranks(60, 18, 25, start=18, count=6), cooldown=5,
            target_type="enemy",
            source="CoA: 'Openers lean on Neurotoxin Arrow's silence', "
                   "'Neurotoxin Arrow's silence into Precision Shot ... "
                   "deletes a caught target'. The silence is NOT modellable: "
                   "'silenced' is set as a debuff stat_mod by seven shipped "
                   "abilities and read by no engine code. Shipped as the hard "
                   "opener hit without it rather than as a tooltip that lies."),
    ability("incendiary_shot", "Incendiary Shot", "ranged_damage",
            "The arrow is already burning when it leaves the string.",
            ranks(42, 12, 30, start=26, count=5), cooldown=4,
            target_type="enemy_aoe", max_targets=5,
            source="CoA: 'On packs, swap to Incendiary Shot/Brutal Shot', "
                   "'up to 5 enemies within 6 yds'. Physical rather than "
                   "Fire: the ranged_damage branch hardcodes physical in "
                   "take_damage, so damage_school on a ranged_damage ability "
                   "is inert - naming a school would read as a feature and "
                   "do nothing."),
    ability("brutal_shot", "Brutal Shot", "ranged_damage",
            "A volley down a line, and the line stops being a line.",
            ranks(76, 22, 40, start=30, count=5), cooldown=5,
            target_type="enemy_aoe", max_targets=4,
            requires_ranged_weapon=BOW_GUN_CROSSBOW,
            source="CoA: 'Fire a volley of powerful shots that pierce "
                   "through Armor ... to all targets in a 40 yd line'. The "
                   "other ranged-weapon-gated ability, same reasoning as "
                   "Deadshot ('450% Ranged Weapon Damage plus 300')."),
    ability("skirmish", "Skirmish", "buff",
            "The fight narrows down to the next three shots.",
            one(34, 25), cooldown=10, duration=3,
            stat_mods={"crit_chance_physical": 15.0}, target_type="self",
            buff_scope="combat",
            source="CoA: 'Skirmish's crit and Focus-cost window sharpens the "
                   "whole sequence', 'Increases your critical strike chance "
                   "by 15% and reduces your Focus costs by -25%'. The cost "
                   "half cannot ride along: all_ability_cost_pct is read "
                   "through get_talent_effect, which does not see status "
                   "effects, so a buff carrying it would do nothing."),
    ability("poison_quiver", "Poison Quiver", "buff",
            "Every head in the quiver goes through the same jar first.",
            one(20, 20), duration=0, stat_mods={"attack_power": 30},
            target_type="self", buff_scope="raid",
            exclusive_group="ranger_quiver",
            source="CoA: 'Only one Quiver buff, Poison or Searing, can be "
                   "active at a time, so a lot of the play is picking the "
                   "right one'. Same exclusive_group, which is the engine's "
                   "real one-at-a-time hook (Tinker's Rounds use it)."),
    ability("searing_quiver", "Searing Quiver", "buff",
            "Heads left in the coals until just before you need them.",
            one(20, 20), duration=0,
            stat_mods={"crit_chance_physical": 5.0},
            target_type="self", buff_scope="raid",
            exclusive_group="ranger_quiver",
            source="CoA: Searing Quiver is the burst option against Poison's "
                   "sustained pressure, so it carries crit where Poison "
                   "carries flat power."),

    # ---- Brigand
    ability("ravage", "Ravage", "dot",
            "You open them up and leave them to it.",
            ranks(46, 14, 0, start=4, count=8), cooldown=2, duration=3,
            target_type="enemy", generates=banks(12),
            source="CoA: 'Ravage first to lay the bleed and bank an Advantage "
                   "stack', 'Generates 1 Advantage'. Brigand's opener and one "
                   "of its two free builders."),
    ability("wild_strike", "Wild Strike", "damage",
            "A short, fast cut that is already on its way back.",
            ranks(38, 10, 0, start=6, count=8), target_type="enemy",
            icon="ability_melee", generates=banks(14),
            source="CoA: 'Weave Wild Strike to build further Advantage "
                   "(Ravager makes it generate an extra stack)'. Melee "
                   "`damage`, not ranged_damage - this is the spec that "
                   "fights in dagger range, and it is what lets the class act "
                   "with no bow equipped."),
    ability("rusty_shiv", "Rusty Shiv", "damage",
            "Not a good knife. Close enough.",
            ranks(30, 9, 15, start=2, count=8), target_type="enemy",
            icon="ability_melee",
            source="CoA names Rusty Shiv with Flank as the pair Bounty Hunter "
                   "reads ('Damage dealt by Flank and Rusty Shiv now "
                   "increases the target's damage taken')."),
    ability("flank", "Flank", "damage",
            "You come in from the side they are not watching.",
            ranks(52, 15, 20, start=10, count=7), cooldown=2,
            target_type="enemy", icon="ability_melee",
            source="CoA: 'Flank from behind for the Beatdown/Bounty payoff'. "
                   "Position is not a concept here, so the bonus Flank gets "
                   "for being behind the target is baked into its base "
                   "damage rather than conditional."),
    ability("bushwhack", "Bushwhack", "damage",
            "You are behind them before they finish turning round.",
            ranks(46, 14, 20, start=16, count=6), cooldown=5,
            target_type="enemy", is_stun=True, icon="ability_melee",
            source="CoA: 'Bushwhack (teleport-behind plus stun) plays like "
                   "Shadowstep-into-Cheap-Shot'. The teleport has no engine "
                   "hook; the stun does."),
    ability("assault", "Assault", "damage",
            "They are finished. This is just the part where they find out.",
            ranks(124, 36, 30, start=20, count=6), cooldown=3,
            target_type="enemy", execute_threshold_pct=20, icon="ability_melee",
            source="CoA: 'Dump with Assault once a few Advantage stacks are "
                   "banked, especially below 20% health where it hits "
                   "hardest', 'Only usable on enemies below 20% health'."),
    ability("vipers_bite", "Viper's Bite", "damage",
            "Four strikes in the time most people manage one.",
            ranks(84, 24, 35, start=28, count=5), cooldown=4,
            target_type="enemy", icon="ability_melee", generates=banks(8),
            source="CoA: 'Fire Viper's Bite whenever the target is bleeding "
                   "to cash in its bonus-damage strikes', 'Generates 2 "
                   "Advantage'. The 'if the target is bleeding' bonus has no "
                   "engine hook - no ability can test the target's active "
                   "effects - so it is priced as an unconditional hard hit."),
    ability("throatpunch", "Throatpunch", "debuff",
            "They were about to say something.",
            one(28, 20), cooldown=6, duration=2,
            stat_mods={"haste": -35.0}, target_type="enemy",
            source="CoA: 'Throatpunch (spell-school interrupt/lockout)'. A "
                   "school lockout is not expressible - 'silenced' as a "
                   "debuff stat_mod is read by nothing - so this is the "
                   "heaviest haste cut in the kit, which is the closest a "
                   "turn engine gets to taking someone's next cast away."),
    ability("quills", "Quills", "ranged_damage",
            "A handful of darts, thrown low and wide.",
            ranks(38, 11, 30, start=24, count=5), cooldown=4,
            target_type="enemy_aoe", max_targets=5,
            source="CoA: 'Launch darts at up to 5 nearby enemies'. The one "
                   "ranged ability in an otherwise melee spec, which is why "
                   "CoA calls Brigand's trash cleave 'solid' while its "
                   "single-target raid damage is D."),
    ability("hookshot", "Hookshot", "damage",
            "The hook finds the wound you already made.",
            ranks(50, 15, 25, start=22, count=5), cooldown=4,
            target_type="enemy", icon="ability_melee",
            source="CoA: 'Hookshot to yank a breakaway bleeding add back'. "
                   "The pull is not modellable; the hit is."),
    ability("dirty_blades", "Dirty Blades", "buff",
            "Whatever is on the blades is not coming off between fights.",
            one(30, 20), cooldown=8, duration=3,
            stat_mods={"attack_power": 50, "crit_chance_physical": 4.0},
            target_type="self", buff_scope="combat",
            source="CoA: 'your melee auto attacks deal an additional 30% of "
                   "the damage dealt as Nature damage and reduces your "
                   "target's healing received'. An on-swing damage rider is a "
                   "proc, not a buff stat_mod, so this carries flat power and "
                   "crit for the same window instead."),
    ability("outmaneuver", "Outmaneuver", "damage",
            "You were never where they were swinging.",
            ranks(100, 30, 40, start=34, count=4), cooldown=8,
            target_type="enemy", icon="ability_melee",
            source="CoA: 'Outmaneuver's teleport-in, decoy, teleport-back is "
                   "a Shadowstep-with-Preparation-reset analog'. Reduced to "
                   "its damage, which is the only half of a three-step "
                   "teleport the engine can express."),

    # ---- Farstrider
    ability("emerald_arrow", "Emerald Arrow", "ranged_damage",
            "You hold the draw until the arrowhead goes green, then let go.",
            ranks(66, 20, 30, start=18, count=6), cooldown=3,
            target_type="enemy",
            source="CoA: 'Dump into Skullpiercer (hits hardest at full "
                   "stacks) or Emerald Arrow (Nature burst that also scales "
                   "per stack) as your default finisher'. Physical for the "
                   "same reason as Incendiary Shot: damage_school is inert on "
                   "a ranged_damage ability."),
    ability("woodland_arrow", "Woodland Arrow", "ranged_damage",
            "A plain arrow with old work carved into the shaft.",
            ranks(50, 15, 25, start=12, count=6), cooldown=2,
            target_type="enemy",
            source="CoA: 'chain Woodland Arrow during the pull to shave the "
                   "Horn cooldown back down ... so a buff is active on nearly "
                   "every pull'. The cooldown refund cannot live on the "
                   "ability (nothing lets a cast reduce another ability's "
                   "cooldown), so it moved onto Blow the Horns! in the tree, "
                   "which is the other half of the same CoA mechanic."),
    ability("whipvine_arrow", "Whipvine Arrow", "ranged_damage",
            "The vines go out with the arrow and take hold where it lands.",
            ranks(44, 13, 25, start=26, count=5), cooldown=4,
            target_type="enemy_aoe", max_targets=3,
            source="CoA: 'Swap to Whipvine Arrow as your finisher when you "
                   "need to keep moving; it also roots', 'Hits 1 additional "
                   "nearby target per stack of Advantage'. The root is not "
                   "modellable ('rooted' as a debuff stat_mod is read by "
                   "nothing), so this keeps the per-stack extra targets as a "
                   "flat 3-target cleave and drops the root."),
    ability("falconstrike", "Falconstrike", "ranged_damage",
            "The shot goes out low and something goes with it.",
            ranks(58, 17, 25, start=20, count=6), cooldown=3,
            target_type="enemy",
            source="CoA: 'Quick Shot ... is the hook for Forest Fighter's and "
                   "the Falconstrike transformation, where every 5th Quick "
                   "Shot becomes Falconstrike'. Every-fifth-cast transforms "
                   "have no engine hook, so it is its own button on a short "
                   "cooldown."),
    ability("queldorei_poison", "Quel'dorei Poison", "dot",
            "An old recipe. Nobody has improved on it.",
            ranks(44, 14, 20, start=16, count=6), cooldown=3, duration=3,
            target_type="enemy",
            source="CoA: 'Open tougher fights with Toxic Dart and Quel'dorei "
                   "Poison for DoT pressure'. The ability_id deliberately "
                   "carries the word 'poison': Ability._damage_multiplier "
                   "only adds poison_dot_damage when that substring is in the "
                   "id, so this is the one place the flavour key is live."),
    ability("falcons_call", "Falcon's Call", "debuff",
            "You whistle once and the sky answers.",
            one(24, 20), cooldown=6, duration=2,
            stat_mods={"haste": -30.0}, target_type="enemy_aoe",
            source="CoA: 'open with Falcon's Call (AoE slow + Falcon "
                   "summons)', 'slowing up to 8 enemies'. The slow is the "
                   "half the engine can carry; the summons are their own "
                   "ability below."),
    ability("summon_war_falcon", "Call War Falcon", "summon_pet",
            "It has been waiting somewhere above you this whole time.",
            one(16, 25), cooldown=6, target_type="self",
            summon_pet_template="raptor", is_instant=True,
            source="CoA: 'Falconstrike/Falcon's Call/Falcon Diving to summon "
                   "War Falcons and Dragonhawks'. effect_type summon_pet with "
                   "a template that exists in combat/pet_templates.py - only "
                   "'wolf' and 'raptor' do, and there is no bird. Raptor is "
                   "the closer of the two for a diving attacker (fast, "
                   "bleed-flavoured, speed 1.3); the gap is that the pet's "
                   "display name will read Raptor, not War Falcon."),
    ability("horn_of_war", "Horn of War", "buff",
            "Two notes. Everyone knows what they mean.",
            one(22, 20), cooldown=8, duration=4,
            stat_mods={"crit_chance_physical": 5.0}, target_type="party",
            buff_scope="combat", exclusive_group="ranger_horn",
            generates=banks(8),
            source="CoA: 'On a shared cooldown you drop a Horn, Horn of War "
                   "for crit or Horn of Alacrity for haste', 'Generates 1 "
                   "Advantage'. Shared cooldown is the exclusive_group. "
                   "target_type party is what actually reaches allies - "
                   "buff_scope only chooses between a 30-minute raid buff and "
                   "a turn-based combat window, and several shipped classes "
                   "set buff_scope 'party' expecting it to do the targeting, "
                   "which silently makes their combat cooldowns last 30 real "
                   "minutes."),
    ability("horn_of_alacrity", "Horn of Alacrity", "buff",
            "A longer note, and the whole line picks up the pace.",
            one(32, 20), cooldown=8, duration=4,
            stat_mods={"haste": 12.0}, target_type="party",
            buff_scope="combat", exclusive_group="ranger_horn",
            generates=banks(8),
            source="The haste Horn of the same pair. Same cost, same "
                   "cooldown, same group - CoA's choice is which one the pull "
                   "wants, not which one is better."),
    ability("battle_screech", "Battle Screech", "buff",
            "It is not a pleasant sound and it is not meant to be.",
            one(28, 25), cooldown=8, duration=4,
            stat_mods={"attack_power": 45, "spell_power": 45},
            target_type="party", buff_scope="combat",
            source="CoA: 'Empower party and raid members, increasing their "
                   "attack or spell power'. Both stats, because the engine "
                   "has no 'whichever one the ally uses' switch and halving "
                   "it for casters would make the spec worse in exactly the "
                   "group it is built for."),
    ability("battle_prowess", "Battle Prowess", "buff",
            "You tell them where to aim and they listen.",
            one(24, 20), duration=0, stat_mods={"hit_rating": 2},
            target_type="party", buff_scope="raid",
            source="CoA: 'Battle Prowess (party hit)', 'Increases chance to "
                   "hit with all spells and attacks by 1% for you and party "
                   "and raid members'. hit_rating is 1 rating = 1% less miss "
                   "in this engine."),
    ability("defense_of_the_ancients", "Defense of the Ancients", "buff",
            "Old wood holds. So does anyone standing near it.",
            one(40, 25), duration=0, stat_mods={"armor_pct": 15.0},
            target_type="party", buff_scope="raid",
            source="CoA: 'Defense of the Ancients' armor' aura. armor_pct is "
                   "percentage POINTS (Character._recalculate_derived_stats "
                   "divides it by 100), so 15.0 is +15%."),
    ability("frenzy", "Frenzy", "buff",
            "Short, loud, and over before anyone can think better of it.",
            one(50, 30), cooldown=15, duration=2,
            stat_mods={"haste": 25.0}, target_type="party",
            buff_scope="combat",
            source="CoA: 'Frenzy's haste', 'Enrage all nearby allies, "
                   "increasing their haste by 30% for 20 seconds. After being "
                   "affected by this spell, allies cannot benefit from "
                   "similar effects for 5 minutes'. The exhaustion debuff is "
                   "not modellable, so the long cooldown carries it."),
    ability("freedom", "Freedom", "dispel",
            "Whatever has hold of them lets go.",
            one(30, 20), cooldown=8, target_type="party",
            dispel_type="movement",
            source="CoA: 'Freedom cleanses roots and snares off the group'. "
                   "dispel_type movement is the existing hook (Guardian's "
                   "Liberation uses it)."),
    ability("thalassian_brand", "Thalassian Brand", "dot",
            "You mark them, and everyone else knows who to shoot.",
            ranks(60, 18, 30, start=36, count=4), cooldown=8, duration=4,
            target_type="enemy",
            source="CoA: 'Thalassian Brand to mark a priority target, which "
                   "grants your allies bonus ranged attack power against it "
                   "and ticks Nature damage'. The ally-side ranged AP bonus is "
                   "target-conditional and has no engine hook, so the ability "
                   "is the Nature tick and the capstone pays the rest."),
    ability("backstep", "Backstep", "buff",
            "One long step backwards, taken early.",
            one(14, 10), cooldown=3, duration=1,
            stat_mods={"dodge": 15.0}, target_type="self",
            buff_scope="combat",
            source="CoA: 'Backstep repositions you on a hit-and-run kill', "
                   "'Leap backwards up to 10 yds'. A leap is a dodge window "
                   "here."),
    ability("command_aura", "Command Aura", "buff",
            "For a moment everyone is shooting at the same thing at the same "
            "time.",
            one(54, 30), cooldown=15, duration=3,
            stat_mods={"attack_power_pct": 10.0}, target_type="party",
            buff_scope="combat",
            source="CoA: 'Command Aura's shared bonus damage', 'causing "
                   "allied players to deal 35% ranged AP additional damage "
                   "when they deal direct damage'. An on-hit rider on every "
                   "ally is not expressible; a party attack power window is. "
                   "attack_power_pct is percentage POINTS."),
]


# ============================================================ talent helpers

def node(tree, tid, name, description, tier, slot, max_points, effects,
         *, node_type="passive", connect=None, proc=None, source=None,
         total_slots=4):
    """One talent node. `slot` is 0-based across the tier's row.

    Hex layout copies the shipped trees: hex_y = -6 + 2*tier, hex_x spaced by
    2 and centred on the row, so tiers narrow toward the capstone.
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


def bank_proc(trigger, chance, amount, *, icd=0, abilities=None):
    """A proc that banks Archery Points.

    _sync_talent_procs multiplies proc["chance"] by points_spent when
    max_points > 1, so a multi-rank bank proc genuinely scales and its
    tooltip can honestly say "per rank". The PAYLOAD does not scale, which
    is why no node here states a per-rank payload on a proc.
    """
    out = {"trigger": trigger, "chance": chance, "icd": icd,
           "grant_resource": {"resource": "archery_points", "amount": amount}}
    if abilities:
        out["ability_filter"] = abilities
    return out


# ================================================================= Archery
A = "ranger_archery"
ARCHERY = tree(
    A, "Ranger Archery",
    "Pure ranged damage. Quick Shot and Hunting Shot bank Archery Points, "
    "Precision Shot and Skullpiercer spend them, and Deadshot finishes. No "
    "auras, no party buffs, no healing anywhere in the tree.",
    [
        node(A, "boots_of_elvenkind", "Boots of Elvenkind",
             "Increases your Agility by 2% per rank.",
             0, 0, 5, {"agility_pct": 2.0},
             source="CoA: 'Increases your Agility by 5% and reduces the "
                    "duration of movement slowing effects on you by -20%'. "
                    "Movement slows are not a thing in a turn engine, so the "
                    "node is the Agility half. agility_pct is percentage "
                    "POINTS."),
        node(A, "devastating_shots", "Devastating Shots",
             "Increases your critical strike chance by 1% and your hit rating "
             "by 1 per rank.",
             0, 1, 5, {"crit_chance_physical": 1.0, "hit_rating": 1},
             source="CoA: 'Increases your critical strike chance by 2% and "
                    "your hit chance by 1%'. Matches the spec's stat "
                    "priority, which opens with 'Hit Rating (until your "
                    "specials stop missing a +3-level target)' and then "
                    "Agility and Crit."),
        node(A, "studded_arrows", "Studded Arrows",
             "Increases the damage of Quick Shot by 5% per rank.",
             0, 2, 5, {"ability_ranger_quick_shot_damage": 0.05},
             source="CoA: 'Increases the ranged weapon damage dealt by Quick "
                    "Shot by 10%'. ability_<id>_<stat> keys are built by "
                    "interpolation in abilities.py, so a literal grep of the "
                    "engine calls them dead."),
        node(A, "improved_serrated_shot", "Improved Serrated Shot",
             "Increases the damage of Serrated Shot by 6% per rank.",
             0, 3, 5, {"ability_ranger_serrated_shot_damage": 0.06},
             source="CoA: 'Increases the damage of Serrated Shot by 30%'."),

        node(A, "archery_master", "Archery Master",
             "Your critical strikes have a 20% chance per rank to bank 5 "
             "Archery Points.",
             1, 0, 3, {}, connect=["boots_of_elvenkind"],
             proc=bank_proc("on_crit", 20, 5, icd=1),
             source="CoA: 'Critical strikes with Quick Shot now generate an "
                    "additional stack of Advantage', and 'Advantage "
                    "generation through Archery Master and Hunting Shot "
                    "depends on crits and hits landing'. Unfiltered rather "
                    "than Quick-Shot-only because a crit proc that can only "
                    "fire off the free filler would be worth almost nothing "
                    "once the rotation moves to spenders."),
        node(A, "new_age_archery", "New-Age Archery",
             "Increases the damage of Precision Shot and Skullpiercer by 5% "
             "per rank.",
             1, 1, 5, {"ability_ranger_precision_shot_damage": 0.05,
                       "ability_ranger_skullpiercer_damage": 0.05},
             connect=["devastating_shots"],
             source="CoA: 'Increases the damage of Skullpiercer and Precision "
                    "Shot by 20%'. The two spenders the whole rotation funnels "
                    "into, so this is the tree's largest single node."),
        node(A, "lethal_wounds", "Lethal Wounds",
             "Increases the damage of your periodic effects by 4% per rank.",
             1, 2, 3, {"dot_damage": 0.04}, connect=["studded_arrows"],
             source="CoA: 'Increases the tick rate of your periodic damage "
                    "effects by -20%'. Tick rate is fixed at one tick per "
                    "turn here, so faster ticks become more damage per tick, "
                    "which is the same total. dot_damage rather than "
                    "bleed_dot_damage: the flavour keys only apply when the "
                    "ability_id contains 'bleed' or 'poison'."),
        node(A, "superb_shot", "Superb Shot",
             "Your Attack and Quick Shot have a 34% chance per rank to bank 3 "
             "Archery Points.",
             1, 3, 3, {}, connect=["improved_serrated_shot"],
             proc=bank_proc("on_damage_cast", 34, 3,
                            abilities=["ranger_attack", "ranger_quick_shot"]),
             source="CoA: 'Damage dealt by Auto Shot now restores 4 Focus', "
                    "and 'Lean on Sniper's Focus and Superb Shot to keep "
                    "Focus flowing rather than sitting to regen'. There is no "
                    "auto-shot step in this engine, so ability_filter pins it "
                    "to the two free attacks, which is what Auto Shot is "
                    "here."),

        node(A, "corrosive_poison", "Corrosive Poison",
             "Increases your armor penetration by 2% per rank.",
             2, 0, 5, {"armor_penetration_pct": 2.0}, connect=["archery_master"],
             source="CoA: 'Your ranged abilities against Poisoned targets now "
                    "ignores 25% of enemy armor', and the spec's stat "
                    "priority lists Armor Penetration fourth. Unconditional, "
                    "because no ability can test whether the target is "
                    "poisoned. armor_penetration_pct is percentage POINTS."),
        node(A, "hunting_with_precision", "Hunting with Precision",
             "Increases the damage of Hunting Shot by 6% and the damage you "
             "deal to additional targets by 4% per rank.",
             2, 1, 3, {"ability_ranger_hunting_shot_damage": 0.06,
                       "aoe_damage": 0.04},
             connect=["new_age_archery"],
             source="CoA: 'Your Hunting Shot now deals 25% increased damage "
                    "for each subsequent target it ricochets to'. "
                    "Per-ricochet escalation is not expressible, so it splits "
                    "into the ability's own damage plus the engine's real "
                    "aoe_damage key."),
        node(A, "pierced", "Pierced",
             "Your critical strikes have a 25% chance per rank to leave the "
             "target bleeding.",
             2, 2, 3, {}, connect=["lethal_wounds"],
             proc={"trigger": "on_crit", "chance": 25, "icd": 1,
                   "apply_effect": {
                       "effect_id": "ranger_pierced",
                       "name": "Pierced",
                       "effect_type": "dot",
                       "duration": 3,
                       "potency": 24,
                       "damage_school": "physical",
                       "on_target": True}},
             source="CoA: 'Critical strikes with Skullpiercer and Precision "
                    "Shot cause the enemy to bleed for an additional 50% "
                    "damage of the damage dealt over 4 seconds'. A proc "
                    "payload cannot be a fraction of the triggering hit AND a "
                    "DoT at once (bonus_pct is instant damage), so the bleed "
                    "carries a flat potency."),
        node(A, "mortal_shots", "Mortal Shots",
             "Reduces the cooldown of Crippling Shot by 1 turn per rank.",
             2, 3, 2, {"ability_ranger_crippling_shot_cooldown": 1},
             connect=["superb_shot"],
             source="CoA: 'Reduces the cooldown of Crippling Shot by -4 sec'. "
                    "Crippling Shot's snare is one of only two pieces of "
                    "control the spec has, per its own weakness list, so "
                    "shortening it is a real pick."),

        node(A, "opportunist", "Opportunist",
             "Increases the critical strike chance of Precision Shot by 3% "
             "per rank.",
             3, 0, 3, {"ability_ranger_precision_shot_crit": 3.0},
             connect=["corrosive_poison"],
             source="CoA: 'Increases the critical strike chance of Precision "
                    "Shot by 50% on enemies above 80% health'. The health "
                    "condition has no hook, so it is unconditional and "
                    "smaller. ability_<id>_crit is added straight to crit "
                    "chance, so it is percentage POINTS."),
        node(A, "strike_where_it_hurts", "Strike Where It Hurts",
             "Increases your critical strike damage by 5% per rank.",
             3, 1, 3, {"crit_damage_physical": 0.05},
             connect=["hunting_with_precision"],
             source="CoA: 'Your ability critical strikes now increase the "
                    "damage the target takes from bleeds by 30%'. A crit that "
                    "amplifies a separate DoT is not expressible, so the node "
                    "pays out on the crit itself."),
        node(A, "skirmisher", "Skirmisher",
             "Increases the damage of Toxic Dart by 6% per rank.",
             3, 2, 3, {"ability_ranger_toxic_dart_damage": 0.06},
             connect=["pierced"],
             source="CoA: 'Increases the damage and tick rate of Toxic Dart "
                    "by -30%, but reduces the duration of its damaging effect "
                    "by -30%'. The trade cancels out in a one-tick-per-turn "
                    "engine, so only the damage half survives."),
        node(A, "maximum_power", "Maximum Power",
             "Skirmish lasts 1 turn longer per rank.",
             3, 3, 2, {"ability_ranger_skirmish_duration": 1},
             connect=["mortal_shots"],
             source="CoA: 'Abilities used with 5 stacks of Advantage now "
                    "refresh the duration of your active Skirmish by 5 sec'. "
                    "Conditional refresh becomes flat uptime."),

        node(A, "hawkeye", "Hawkeye",
             "Your shots have a 12% chance per rank to loose a free Quick "
             "Shot at your target.",
             4, 0, 3, {}, connect=["opportunist"],
             proc={"trigger": "on_damage_cast", "chance": 12, "icd": 1,
                   "cast_ability": "ranger_quick_shot"},
             source="CoA: 'You now fire an arrow every 3 sec at enemies "
                    "within 30 yds affected by your Hunting Shot'. A timed "
                    "background arrow has no scheduler here; cast_ability "
                    "fires the real Quick Shot for free (Ability.use(free="
                    "True)), which also means it banks its Archery Points."),
        node(A, "masterful_archery", "Masterful Archery",
             "Increases your Physical damage by 2% per rank.",
             4, 1, 3, {"physical_damage": 0.02},
             connect=["strike_where_it_hurts"],
             source="CoA: 'While in Elude, gain a stack of Masterful Archery "
                    "every 2 sec ... Your next Precision Shot now deals 10% "
                    "increased damage, stacking up to 5 times'. A stacking "
                    "out-of-combat ramp is not expressible, so it lands flat."),
        node(A, "a_quick_demise", "A Quick Demise",
             "Serrated Shot lasts 1 turn longer per rank.",
             4, 2, 2, {"ability_ranger_serrated_shot_duration": 1},
             connect=["skirmisher"],
             source="CoA: 'Auto shots now have a 20% chance to extend the "
                    "duration of your Serrated Shot by 2 sec'."),

        node(A, "sharpshooter", "Sharpshooter",
             "Grants ranged attack power equal to 3% of your Agility per "
             "rank.",
             5, 0, 3, {"ranged_ap_from_agility_pct": 0.03},
             connect=["hawkeye"], total_slots=3,
             source="CoA: 'Adds 25% to the bonuses that your stacks of "
                    "Advantage provide'. A real <target>_from_<source>_pct "
                    "conversion, resolved against the shared "
                    "STAT_CONVERSION_TARGETS/SOURCES maps in character.py. "
                    "This is the only working way to raise a Ranger's ranged "
                    "attack power from a talent: there is no "
                    "ranged_attack_power_pct key, and a flat "
                    "ranged_attack_power effect is dropped because "
                    "_recalculate_derived_stats computes that stat from "
                    "Agility and Strength with no bonus-pool term."),
        node(A, "bleeding_edge", "Bleeding Edge",
             "Increases the damage of your periodic effects by a further 5% "
             "per rank.",
             5, 1, 2, {"dot_damage": 0.05},
             connect=["masterful_archery"], total_slots=3,
             source="CoA: 'Allows the periodic damage dealt by Serrated Shot "
                    "to critically strike'. DoTs cannot crit in this engine - "
                    "_apply_effect's dot branch rolls no crit - so the node "
                    "pays the average of that crit chance as flat DoT damage "
                    "instead."),
        node(A, "one_shot_one_kill", "One Shot, One Kill",
             "Increases the damage of Deadshot by 10% per rank.",
             5, 2, 2, {"ability_ranger_deadshot_damage": 0.10},
             connect=["a_quick_demise"], total_slots=3,
             source="CoA: 'Increases the damage of Deadshot by 75%'."),

        node(A, "silent_but_deadly", "Silent, But Deadly",
             "Your Physical damage has an 8% chance to let you fire Deadshot "
             "at a target of any health for 2 turns, and your Physical damage "
             "is increased by 8%.",
             6, 0, 1, {"physical_damage": 0.08},
             connect=["sharpshooter", "bleeding_edge", "one_shot_one_kill"],
             total_slots=1,
             proc={"trigger": "on_damage_cast", "chance": 8, "icd": 2,
                   "apply_effect": {
                       "effect_id": "ranger_silent_but_deadly",
                       "name": "Silent, But Deadly",
                       "effect_type": "buff",
                       "duration": 2,
                       "stat_mods": {},
                       "on_target": False,
                       "proc": {"bypass_execute_threshold": True}}},
             source="Capstone. CoA: 'Direct Physical damage dealt now has an "
                    "8% chance to allow you to use Deadshot regardless of the "
                    "targets health for 8 seconds', and 'Finish with the "
                    "sub-20%-HP execute Deadshot, which Silent, But Deadly "
                    "can occasionally unlock early'. The real mechanic, not an "
                    "approximation: Ability.use checks every carried effect "
                    "for proc['bypass_execute_threshold'] before enforcing "
                    "execute_threshold_pct, and consumes the window on use."),
    ],
    "Built from reference/coa_sidekick/SPEC_ranger__archery.txt: 'Closest to "
    "retail Marksmanship Hunter ... Despite the class name, judge it as a "
    "pure MM-Hunter DPS spec.' The thing to respect about this spec is what "
    "it does NOT have: CoA is explicit that there is 'no party-buff or "
    "support layer at all here. No auras, no haste or crit sharing, no "
    "healing whatsoever', and 'No heal anywhere in the spec: no shield, no "
    "HoT, no proc-heal. You live on positioning.' So this tree has no ally "
    "effect and no healing node of any kind, which is deliberate and is why "
    "it is the only one of the three without one. Its stat priority (Hit > "
    "Agility > Crit > Armor Penetration > Haste) is why Devastating Shots "
    "carries hit rating and Corrosive Poison carries armor penetration.")


# ================================================================= Brigand
B = "ranger_brigand"
BRIGAND = tree(
    B, "Ranger Brigand",
    "Melee assassin. Ravage and Wild Strike bank Archery Points and lay "
    "bleeds, Assault and Viper's Bite and Skullpiercer spend them, and the "
    "control suite is deeper than a pure damage kit usually gets.",
    [
        node(B, "banditry", "Banditry",
             "Increases your critical strike chance by 1% per rank.",
             0, 0, 5, {"crit_chance_physical": 1.0},
             source="CoA: 'Increases your critical strike chance by 2% and "
                    "Focus regeneration by 15%'. Nothing regenerates "
                    "archery_points, so only the crit half can exist."),
        node(B, "close_quarters", "Close Quarters",
             "Increases your attack power and Agility by 2% per rank.",
             0, 1, 5, {"attack_power_pct": 2.0, "agility_pct": 2.0},
             source="CoA: 'Increases your attack power and Agility by 3%'. "
                    "Both keys are percentage POINTS."),
        node(B, "jagged_cuts", "Jagged Cuts",
             "Increases the damage of Ravage and Toxic Dart by 5% per rank.",
             0, 2, 5, {"ability_ranger_ravage_damage": 0.05,
                       "ability_ranger_toxic_dart_damage": 0.05},
             source="CoA: 'Increases the damage and duration of Toxic Dart "
                    "and Ravage by 25%'. Damage only: adding duration here "
                    "would stack with Lacerations lower in the tree and push "
                    "a 3-turn DoT past the length of most fights."),
        node(B, "dice_games", "Dice Games",
             "Increases the critical strike chance of Wild Strike and Assault "
             "by 2% per rank.",
             0, 3, 5, {"ability_ranger_wild_strike_crit": 2.0,
                       "ability_ranger_assault_crit": 2.0},
             source="CoA: 'Increases the critical strike chance of Wild "
                    "Strike and Assault by 5%'."),

        node(B, "ravager", "Ravager",
             "Your Wild Strike has a 34% chance per rank to bank 4 Archery "
             "Points.",
             1, 0, 3, {}, connect=["banditry"],
             proc=bank_proc("on_damage_cast", 34, 4,
                            abilities=["ranger_wild_strike"]),
             source="CoA: 'Your Wild Strike now generates 1 additional "
                    "Advantage'. ability_filter is the engine's real "
                    "per-ability proc gate (see fire_proc_trigger), so this "
                    "genuinely only fires off Wild Strike."),
        node(B, "knuckleduster", "Knuckleduster",
             "Your attacks have a 20% chance per rank to bank 4 Archery "
             "Points.",
             1, 1, 3, {}, connect=["close_quarters"],
             proc=bank_proc("on_damage_cast", 20, 4, icd=1),
             source="CoA: 'Periodic damage dealt now generates 5 Focus'. A "
                    "DoT tick fires no proc trigger in this engine - "
                    "fire_proc_trigger is called from the cast path, not the "
                    "tick path - so this generates off casts instead, with an "
                    "internal cooldown so it reads as periodic rather than "
                    "per-button."),
        node(B, "underhanded", "Underhanded",
             "Increases the damage of Skullpiercer by 5% per rank.",
             1, 2, 5, {"ability_ranger_skullpiercer_damage": 0.05},
             connect=["jagged_cuts"],
             source="CoA: 'Increases the attack power scaling of Skullpiercer "
                    "by 15%'. Scaling coefficients are not per-ability "
                    "tunable, so it is flat damage."),
        node(B, "beatdown", "Beatdown",
             "Increases your armor penetration by 2% per rank.",
             1, 3, 3, {"armor_penetration_pct": 2.0}, connect=["dice_games"],
             source="CoA: 'Auto attacks now have a 5% chance to reveal a fault "
                    "in the enemy's defenses, causing your next instance of "
                    "Physical ability damage to ignore Armor'. A one-shot "
                    "armour-ignore flag has no hook, and the spec's stat "
                    "priority lists Armor Penetration above Crit, so it is "
                    "real armour penetration at a lower rate."),

        node(B, "guile_of_the_cutthroat", "Guile of the Cutthroat",
             "Increases your attack power by 2% and all damage you deal by 2% "
             "per rank.",
             2, 0, 3, {"attack_power_pct": 2.0, "all_damage": 0.02},
             connect=["ravager"],
             source="CoA: 'Increases party and raid member's melee and ranged "
                    "attack power by 5% ... In addition, increases your damage "
                    "dealt by 3%', and CoA calls this 'its only support tool'. "
                    "A talent cannot reach the party - "
                    "Character.get_talent_effects resolves against its own "
                    "character only - so this node is the self half of the "
                    "real tooltip, and the party-facing work in this class "
                    "lives on Farstrider's Horn abilities."),
        node(B, "bounty_hunter", "Bounty Hunter",
             "Your Flank and Rusty Shiv have a 34% chance per rank to leave "
             "the target taking 4% more Physical damage.",
             2, 1, 3, {}, connect=["knuckleduster"],
             proc={"trigger": "on_damage_cast", "chance": 34, "icd": 1,
                   "ability_filter": ["ranger_flank", "ranger_rusty_shiv"],
                   "apply_effect": {
                       "effect_id": "ranger_bounty",
                       "name": "Bounty",
                       "effect_type": "debuff",
                       "duration": 3,
                       "stat_mods": {"physical_damage_taken_pct": 4.0},
                       "on_target": True}},
             source="CoA: 'Damage dealt by Flank and Rusty Shiv now increases "
                    "the target's damage taken from your Advantage spenders "
                    "by 25%'. Narrowing it to spenders only is not "
                    "expressible, so it is all Physical damage at a much "
                    "smaller number. physical_damage_taken_pct inside a "
                    "status effect is percentage POINTS - character.py divides "
                    "the school-specific damage-taken keys by 100, unlike "
                    "plain damage_taken_pct, which it reads raw."),
        node(B, "ambuscade", "Ambuscade",
             "Increases the damage of Flank by 6% per rank.",
             2, 2, 3, {"ability_ranger_flank_damage": 0.06},
             connect=["underhanded"],
             source="CoA: 'Increases the damage of Skullpiercer and Flank by "
                    "20%, plus an additional 35% if you have a polearm "
                    "equipped'. Ranger has no polearm proficiency in "
                    "weapon_types.json, and Skullpiercer is already covered "
                    "by Underhanded, so this is the Flank half."),
        node(B, "focused_fighter", "Focused Fighter",
             "Reduces the Archery Point cost of your abilities by 3% per "
             "rank.",
             2, 3, 2, {"all_ability_cost_pct": 0.03}, connect=["beatdown"],
             source="CoA: 'Reduces the Focus cost of Flank, Blackjack, and "
                    "Wild Strike by -10%'. POSITIVE is the reduction here: "
                    "talented_cost does cost * (1.0 - pct). Guardian's "
                    "Seasoned Fighter shipped this key negative, which makes "
                    "its abilities 3% per rank MORE expensive than the "
                    "tooltip promises."),

        node(B, "highwayman", "Highwayman",
             "Your critical strikes have a 25% chance per rank to increase "
             "your haste by 10 for 2 turns.",
             3, 0, 3, {}, connect=["guile_of_the_cutthroat"],
             proc={"trigger": "on_crit", "chance": 25, "icd": 1,
                   "apply_effect": {
                       "effect_id": "ranger_highwayman",
                       "name": "Highwayman",
                       "effect_type": "buff",
                       "duration": 2,
                       "stat_mods": {"haste": 10.0},
                       "on_target": False}},
             source="CoA: 'Direct critical strikes while behind your target "
                    "increase your haste by 15% for 5 seconds'. Facing is not "
                    "tracked, so the 'behind' condition is dropped."),
        node(B, "pilfering", "Pilfering",
             "Your attacks have a 20% chance per rank to heal you for 8% of "
             "the damage dealt.",
             3, 1, 3, {}, connect=["bounty_hunter"],
             proc={"trigger": "on_damage_cast", "chance": 20, "icd": 1,
                   "leech_pct": 0.08},
             source="CoA: 'causes its damage dealt to heal you equal to 50% "
                    "of the value', and the spec's weakness list says 'No "
                    "real self-heal. The small Pilfering and Dirty Blades "
                    "leech will not carry you through focus fire.' So this is "
                    "the spec's only sustain and it is deliberately thin. "
                    "leech_pct is a real proc payload read in "
                    "status_effects.py."),
        node(B, "wild_man", "Wild Man",
             "Increases the damage you deal to additional targets by 6% per "
             "rank.",
             3, 2, 3, {"aoe_damage": 0.06}, connect=["ambuscade"],
             source="CoA: 'Your Wild Strike now strikes 2 additional nearby "
                    "enemies, but deals reduced damage with each enemy "
                    "struck'. A talent cannot turn a single-target ability "
                    "into a cleave (target_type is authored on the ability), "
                    "so this scales Quills and the rest of the spec's real "
                    "AoE instead. CoA rates Brigand's trash cleave solid and "
                    "its single-target raid damage D, which this keeps true."),
        node(B, "stalker", "Stalker",
             "Reduces the cooldown of Cutthroat by 1 turn per rank.",
             3, 3, 2, {"ability_ranger_cutthroat_cooldown": 1},
             connect=["focused_fighter"],
             source="CoA: 'Reduces the cooldown of Cutthroat by -15 sec, but "
                    "reduces the range of Cutthroat by -10 yds'. Range is not "
                    "a cost this engine can charge, so the downside is gone "
                    "and the node is smaller."),

        node(B, "tip_of_the_spear", "Tip of the Spear",
             "Your weapon swings have a 15% chance per rank to strike again.",
             4, 0, 3, {}, connect=["highwayman"],
             proc={"trigger": "on_weapon_swing", "chance": 15, "icd": 1,
                   "extra_attack": True},
             source="CoA: 'your Wild Strike now has a 15% chance to strike 3 "
                    "additional times'. extra_attack is the engine's real "
                    "Windfury mechanic: a genuine second swing through "
                    "Ability.use, found by the '<class_prefix>_attack' naming "
                    "convention, so it rolls its own hit and crit."),
        node(B, "marked_for_death", "Marked for Death",
             "Increases your Physical damage by 2% per rank.",
             4, 1, 3, {"physical_damage": 0.02}, connect=["pilfering"],
             source="CoA: 'direct critical strikes on enemies below 35% "
                    "health now have a chance to allow the use of abilities "
                    "as if you were in Elude'. Elude is a buff here rather "
                    "than a state abilities check, so there is nothing to "
                    "unlock; the node pays flat damage."),
        node(B, "tactical_advantage", "'Tactical' Advantage",
             "Increases the damage of Bushwhack by 8% per rank.",
             4, 2, 2, {"ability_ranger_bushwhack_damage": 0.08},
             connect=["wild_man"],
             source="CoA: 'Knockout and Bushwhack now increases your damage "
                    "dealt against the target by 10% for 5 seconds'. A "
                    "target-specific damage window has no hook, so the node "
                    "front-loads it onto Bushwhack's own hit."),

        node(B, "dastardly", "Dastardly",
             "Increases your critical strike damage by 5% per rank.",
             5, 0, 3, {"crit_damage_physical": 0.05},
             connect=["tip_of_the_spear"], total_slots=3,
             source="CoA: 'Increases your critical damage dealt by 15% on "
                    "enemies above 80% health or below 20% health'. Both ends "
                    "of a health bar is most of a fight, so it is "
                    "unconditional and smaller."),
        node(B, "lacerations", "Lacerations",
             "Increases the damage of your periodic effects by 6% per rank.",
             5, 1, 2, {"dot_damage": 0.06},
             connect=["marked_for_death"], total_slots=3,
             source="CoA: 'Allows the periodic damage dealt by Ravage to "
                    "critically strike'. Same gap as Archery's Bleeding Edge: "
                    "DoTs do not crit in this engine, so the node pays the "
                    "average instead."),
        node(B, "rub_it_in", "Rub It In",
             "Your attacks have a 20% chance per rank to refund 5 Archery "
             "Points.",
             5, 2, 2, {}, connect=["tactical_advantage"], total_slots=3,
             proc=bank_proc("on_damage_cast", 20, 5, icd=1),
             source="CoA: 'Each stack of Advantage spent now gives you a 20% "
                    "chance to refund 1 stack of Advantage'. There is no "
                    "'on spend' trigger, so it keys off the cast."),

        node(B, "instinctual_combatant", "Instinctual Combatant",
             "Grants attack power equal to 10% of your Agility, and increases "
             "your critical strike chance by 4%.",
             6, 0, 1, {"ap_from_agility_pct": 0.10,
                       "crit_chance_physical": 4.0},
             node_type="active",
             connect=["dastardly", "lacerations", "rub_it_in"],
             total_slots=1,
             source="Capstone. CoA: 'Instinct now grants you an additional "
                    "10% of your Agility as melee attack power' and "
                    "'guarantees your next 3 Skullpiercers or Assaults within "
                    "20 seconds to critically strike'. The conversion is "
                    "real and literal; guaranteed crits are not expressible, "
                    "so they become flat crit chance. A real "
                    "<target>_from_<source>_pct key."),
    ],
    "Built from reference/coa_sidekick/SPEC_ranger__brigand.txt: 'Closest to "
    "Assassination Rogue crossed with Outlaw's utility toolkit', 'a "
    "dagger-wielding melee assassin, not a healer despite the archetype tag'. "
    "Its stat priority is Hit > Expertise > Agility > Armor Penetration > "
    "Crit > Haste, which is why Beatdown carries armour penetration above "
    "Banditry's crit. Expertise has no key in this engine, so it is the one "
    "line of that priority with nothing to spend on. CoA's own weakness list "
    "drives the shape of the back half: 'No real self-heal' (Pilfering is the "
    "only sustain node and it is small), 'Nothing breaks a stun, root, or "
    "fear' (no node offers one), and 'Built entirely around daggers in melee "
    "range with no ranged pressure' (Quills is the only ranged ability and "
    "Wild Man scales it rather than adding another).")


# ============================================================== Farstrider
F = "ranger_farstrider"
FARSTRIDER = tree(
    F, "Ranger Farstrider",
    "Ranged damage and party support. Horns and screeches buff the group on a "
    "shared cooldown, War Falcons fight alongside you, and Emerald and "
    "Woodland Arrows spend the bank while the party keeps the buff.",
    [
        node(F, "cunning", "Cunning",
             "Reduces the Archery Point cost of your abilities by 2% per "
             "rank.",
             0, 0, 5, {"all_ability_cost_pct": 0.02},
             source="CoA: 'Increases your Focus regeneration by 15%'. Nothing "
                    "in the engine regenerates archery_points, so the honest "
                    "translation of a regeneration node is a cheaper kit: it "
                    "buys the same number of extra casts per bank. POSITIVE "
                    "is the reduction (talented_cost does cost * (1 - pct))."),
        node(F, "windrunners_reach", "Windrunner's Reach",
             "Increases your critical strike chance by 1% per rank.",
             0, 1, 5, {"crit_chance_physical": 1.0},
             source="CoA: 'Increases the range of your ranged abilities by 5 "
                    "yds. In addition, your critical strike chance against "
                    "Undead, Beasts, and Dragonkin is increased by 2%'. "
                    "Neither range nor creature type is a thing the ability "
                    "system can read, so the crit is unconditional."),
        node(F, "falcon_charmer", "Falcon Charmer",
             "Increases your War Falcon's health and armor by 4% per rank.",
             0, 2, 5, {"pet_health": 0.04, "pet_armor": 0.04},
             source="CoA: 'Increases the duration of War Falcons by 3 sec'. "
                    "Summoned pets here are persistent rather than timed, so "
                    "'lasts longer' becomes 'survives longer'. pet_health and "
                    "pet_armor are live because this spec actually summons "
                    "one (Call War Falcon, effect_type summon_pet)."),
        node(F, "survivalist", "Survivalist",
             "Increases the healing done by Survival Potion by 6% per rank.",
             0, 3, 5, {"ability_ranger_survival_potion_healing": 0.06},
             source="CoA: 'Reduces the cooldown of Survival Potion by -25%', "
                    "and 'Drink Survival Potion yourself when eating poison "
                    "or disease damage'. A flat cooldown key would take 5 "
                    "turns off an 8-turn cooldown at full rank, so the node "
                    "scales the heal instead. ability_<id>_healing is the key "
                    "the heal path reads; ability_<id>_damage is ignored for "
                    "heals, which is how 18 talents across four classes "
                    "silently did nothing."),

        node(F, "blow_the_horns", "Blow the Horns!",
             "Reduces the cooldown of your Horns by 1 turn per rank.",
             1, 0, 2, {"ability_ranger_horn_of_war_cooldown": 1,
                       "ability_ranger_horn_of_alacrity_cooldown": 1},
             connect=["cunning"],
             source="CoA: 'Reduces the cooldown of Horn spells by -25%', and "
                    "'Woodland Arrow and the passive Blow the Horns! chip "
                    "that cooldown back down, so a skilled Ranger keeps a "
                    "Horn up far more than the raw cooldown suggests'. "
                    "Woodland Arrow's half of that cannot exist - no cast can "
                    "shorten another ability's cooldown - so the whole "
                    "mechanic is concentrated here."),
        node(F, "dream_flowers", "Dream Flowers",
             "Your critical strikes have a 25% chance per rank to heal you "
             "for 40.",
             1, 1, 3, {}, connect=["windrunners_reach"],
             proc={"trigger": "on_crit", "chance": 25, "icd": 1,
                   "heal_flat": 40},
             source="CoA: 'Your damaging critical strikes now spawn a green "
                    "Dream Flower ... When an ally runs over the flower, they "
                    "consume it to heal for 3% maximum health'. There are no "
                    "ground objects and no running over them, so the heal "
                    "lands on the Ranger directly. CoA's own weakness note "
                    "holds either way: 'Dream Flowers and Phoenix Plumes only "
                    "fire off crits and finisher hits.'"),
        node(F, "hunting_tactics", "Hunting Tactics",
             "Increases the damage of Skullpiercer by 5% per rank.",
             1, 2, 5, {"ability_ranger_skullpiercer_damage": 0.05},
             connect=["falcon_charmer"],
             source="CoA: 'Damage dealt by Skullpiercer is increased by 30% "
                    "against Poisoned targets'. No ability can test the "
                    "target's effects, so it is unconditional and smaller."),
        node(F, "razorquills", "Razorquills",
             "Increases the damage of your periodic effects by 4% per rank.",
             1, 3, 3, {"dot_damage": 0.04}, connect=["survivalist"],
             source="CoA: 'Increases the tick rate of Toxic Dart and Emerald "
                    "Arrows by -20%'. One tick per turn is fixed, so faster "
                    "ticks become harder ones."),

        node(F, "venom_coated_seeds", "Venom-Coated Seeds",
             "Increases the damage of Snapseed and Quel'dorei Poison by 6% "
             "per rank.",
             2, 0, 3, {"ability_ranger_snapseed_damage": 0.06,
                       "ability_ranger_queldorei_poison_damage": 0.06},
             connect=["blow_the_horns"],
             source="CoA: 'Damage dealt by Snapseed now reduces the enemy's "
                    "chance to hit by -15%'. hit_chance_taken on a monster "
                    "debuff is read by nothing, so the node is damage on both "
                    "of the spec's poison-flavoured abilities instead."),
        node(F, "thread_the_needle", "Thread the Needle",
             "Your critical strikes have a 25% chance per rank to increase "
             "your haste by 10 for 2 turns.",
             2, 1, 3, {}, connect=["dream_flowers"],
             proc={"trigger": "on_crit", "chance": 25, "icd": 1,
                   "apply_effect": {
                       "effect_id": "ranger_thread_the_needle",
                       "name": "Thread the Needle",
                       "effect_type": "buff",
                       "duration": 2,
                       "stat_mods": {"haste": 10.0},
                       "on_target": False}},
             source="CoA: 'Critical strikes with Quick Shot or Falconstrike "
                    "now reduce the cast time and cost of your next ability "
                    "that consumes Advantage by -34%'. Cast time is haste "
                    "here; the cost half cannot ride along, because "
                    "all_ability_cost_pct is read through get_talent_effect "
                    "and never sees a status effect's stat_mods."),
        node(F, "forest_herald", "Forest Herald",
             "Your attacks have a 15% chance per rank to heal you for 30.",
             2, 2, 3, {}, connect=["hunting_tactics"],
             proc={"trigger": "on_damage_cast", "chance": 15, "icd": 1,
                   "heal_flat": 30},
             source="CoA: 'Casting Toxic Dart and abilities that spend stacks "
                    "of Advantage now have a 20% chance to spawn a green "
                    "Dreamflower'. Same ground-object gap as Dream Flowers, "
                    "and the second half of what CoA means by 'No external "
                    "healer needed.'"),
        node(F, "guidance", "Guidance",
             "Increases your Physical damage by 2% per rank.",
             2, 3, 3, {"physical_damage": 0.02}, connect=["razorquills"],
             source="CoA: 'Increases your Physical and Nature damage dealt by "
                    "1% for each War Falcon or Dragonhawk you have active'. "
                    "Nothing can count active pets at damage time, so it is "
                    "flat."),

        node(F, "wingman", "Wingman",
             "Reduces all damage you take by 2% per rank.",
             3, 0, 3, {"damage_taken_pct": -0.02},
             connect=["venom_coated_seeds"],
             source="CoA: 'Reduces all damage taken by -2% for each War "
                    "Falcon or Dragonhawk you have active'. Pet-count scaling "
                    "has no hook, so the per-falcon rate becomes a per-rank "
                    "rate. damage_taken_pct is a FRACTION, not percentage "
                    "points - this is the key convention the shipped Guardian "
                    "got wrong on max_health_pct and reached 99,156 effective "
                    "HP."),
        node(F, "gutpiercer", "Gutpiercer",
             "Your attacks have a 20% chance per rank to leave the target "
             "taking 3% more Magic damage.",
             3, 1, 3, {}, connect=["thread_the_needle"],
             proc={"trigger": "on_damage_cast", "chance": 20, "icd": 1,
                   "apply_effect": {
                       "effect_id": "ranger_gutpiercer",
                       "name": "Gutpiercer",
                       "effect_type": "debuff",
                       "duration": 3,
                       "stat_mods": {"magic_damage_taken_pct": 3.0},
                       "on_target": True}},
             source="CoA: 'Damage dealt by War Falcons and Dragonhawks now "
                    "has a 15% chance to reduce the enemy's resistances by 75 "
                    "and increase their Magic damage taken'. A pet's hits "
                    "fire no proc on the owner, so it keys off the Ranger's "
                    "own casts. The magic debuff is the spec's real support "
                    "contribution to a caster group. School-specific "
                    "damage-taken keys inside a status effect are percentage "
                    "POINTS."),
        node(F, "plumes_of_war", "Plumes of War",
             "Increases the critical strike chance of Falconstrike and "
             "Emerald Arrow by 3% per rank.",
             3, 2, 3, {"ability_ranger_falconstrike_crit": 3.0,
                       "ability_ranger_emerald_arrow_crit": 3.0},
             connect=["forest_herald"],
             source="CoA: 'Increases the critical strike chance of "
                    "Falconstrike and Emerald Arrow by 15%. In addition, "
                    "critical strikes with Falconstrike now increase the "
                    "damage of subsequent Falconstrikes by 5%, stacking 5 "
                    "times'. The stacking half has no hook."),
        node(F, "scavenger", "Scavenger",
             "Battle Screech lasts 1 turn longer per rank.",
             3, 3, 2, {"ability_ranger_battle_screech_duration": 1},
             connect=["guidance"],
             source="CoA: 'Increases the duration of Battle Screech and "
                    "reduces the cooldown of Snapseed by 5 sec'."),

        node(F, "falcons_aid", "Falcon's Aid",
             "Increases your War Falcon's damage by 6% per rank.",
             4, 0, 3, {"pet_damage": 0.06}, connect=["wingman"],
             source="CoA: 'Periodic damage dealt now has a 10% chance to "
                    "summon a War Falcon to aid you in battle for 6 seconds'. "
                    "Pets here are summoned and persistent rather than "
                    "proc-spawned and timed, so more falcons becomes a better "
                    "falcon. pet_damage is live for this spec because it has "
                    "a real companion."),
        node(F, "forest_fighter", "Forest Fighter",
             "Increases the damage of Woodland Arrow and Emerald Arrow by 6% "
             "per rank.",
             4, 1, 3, {"ability_ranger_woodland_arrow_damage": 0.06,
                       "ability_ranger_emerald_arrow_damage": 0.06},
             connect=["gutpiercer"],
             source="CoA: 'Your Skullpiercers or Emerald Arrows used with 5 "
                    "stacks of Advantage now reduce the cooldown of Woodland "
                    "Arrow by -5 sec'. Conditional cooldown reduction from "
                    "another cast has no hook, so the node makes the pair hit "
                    "harder instead."),
        node(F, "to_the_skies", "To the Skies!",
             "Reduces the cooldown of Backstep by 1 turn per rank.",
             4, 2, 2, {"ability_ranger_backstep_cooldown": 1},
             connect=["plumes_of_war"],
             source="CoA: 'Reduces the cooldown of Bushcraft Glider by -30 "
                    "sec'. Bushcraft Glider is overworld movement, which this "
                    "kit has no equivalent of, so the node moves onto "
                    "Backstep, the spec's other repositioning tool. CoA lists "
                    "the two together: 'Backstep, Bushcraft Glider and Falcon "
                    "Guide's speed proc make you hard to pin down.'"),

        node(F, "frenzy", "Frenzy",
             "Increases your haste by 2 per rank.",
             5, 0, 3, {"haste": 2.0}, connect=["falcons_aid"], total_slots=3,
             source="CoA: 'Frenzy's haste' is one of the free spec passives "
                    "and also a party cooldown. The party half is the Frenzy "
                    "ability; this node is the Ranger's own share, since a "
                    "talent cannot reach allies."),
        node(F, "defense_of_the_ancients", "Defense of the Ancients",
             "Increases your Armor by 4% per rank.",
             5, 1, 2, {"armor_pct": 4.0}, connect=["forest_fighter"],
             total_slots=3,
             source="CoA: 'Defense of the Ancients' armor' aura, same split "
                    "as Frenzy: the party aura is the ability, this is the "
                    "Ranger's own armour. armor_pct is percentage POINTS."),
        node(F, "pecking", "Pecking",
             "Increases the damage you deal to additional targets by 6% per "
             "rank.",
             5, 2, 2, {"aoe_damage": 0.06}, connect=["to_the_skies"],
             total_slots=3,
             source="CoA: 'Your War Falcons and Dragonhawks now have a 25% "
                    "chance to deal additional Physical damage to 3 nearby "
                    "enemies'. Pet AoE is not something a talent can add to a "
                    "pet template, so the node scales the Ranger's own cleave "
                    "(Whipvine Arrow, Quills, Incendiary Shot)."),

        node(F, "coordination", "Coordination",
             "Increases your critical strike chance by 4%, your critical "
             "strike damage by 10%, and your War Falcon's damage by 6%.",
             6, 0, 1, {"crit_chance_physical": 4.0,
                       "crit_damage_physical": 0.10,
                       "pet_damage": 0.06},
             node_type="active",
             connect=["frenzy", "defense_of_the_ancients", "pecking"],
             total_slots=1,
             source="Capstone. CoA: 'Your War Falcons and Dragonhawks now "
                    "grant you a stack of Coordination when they deal damage "
                    "... Increases your critical strike chance and critical "
                    "damage by 1% for 15 seconds, stacking 10 times.' A pet's "
                    "hits fire no proc on the owner, so the 10-stack ramp "
                    "lands as its maximum value held permanently, and the "
                    "falcon gets a share of it. Chosen over Thalassian Brand "
                    "as the capstone because Brand is already a real ability "
                    "in the kit and CoA rates this spec's own throughput "
                    "'moderate' - a passive ceiling fits better than another "
                    "button."),
    ],
    "Built from reference/coa_sidekick/SPEC_ranger__farstrider.txt: 'Closest "
    "to Augmentation Evoker ... its identity is built around empowering "
    "allies' output ... It still does meaningful personal ranged damage on "
    "its own Advantage builder/finisher loop, with only minor incidental "
    "healing rather than a real HPS rotation.' That split is why the ally "
    "work is all ABILITIES (the two Horns on a shared exclusive_group, Battle "
    "Screech, Battle Prowess, Defense of the Ancients, Frenzy, Command Aura, "
    "Freedom) and the tree is the Ranger's own half: talent effects resolve "
    "against the owning character only. Stat priority is Hit > Agility > Crit "
    "> Haste > Armor Penetration, which is why this is the one Ranger tree "
    "with a haste node and no armour penetration node.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the files")
    args = parser.parse_args()

    ability_doc = {
        "class": "Ranger",
        "_source_note": __doc__.strip().split("\n\n")[1].replace("\n", " "),
        "abilities": ABILITIES,
    }

    targets = [
        (ROOT / "data/abilities/ranger.json", ability_doc),
        (ROOT / "data/talents/ranger_archery.json", ARCHERY),
        (ROOT / "data/talents/ranger_brigand.json", BRIGAND),
        (ROOT / "data/talents/ranger_farstrider.json", FARSTRIDER),
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
