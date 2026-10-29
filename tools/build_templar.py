#!/usr/bin/env python3
"""Author the Templar: ability kit + three talent trees.

    PYTHONPATH=. python3 tools/build_templar.py [--apply]

Templar is one of the twelve CoA classes that shipped with base stats, armour
type, weapon proficiency and a resource but no abilities and no talents, so it
could not be selected. It is the only Combo class in the game
(CLASS_RESOURCE_MAP: "Templar": (ResourceType.COMBO, None), commented
"Opener -> Followup -> Combo Breaker chain"), and in CoA it is the Oath class:
every builder banks an Oath, and the finishers are literally called Oath
Breakers.

SOURCE. reference/coa_sidekick/CLASS_templar.txt, the three
SPEC_templar__*.txt pages and reference/coa_sidekick/talents/templar.json,
captured from ascensionsidekick.com. Every ability and talent name below is a
real CoA name off those pages; nothing is invented to fill a slot. Identity
per that reference:

  Zealot      MELEE DPS  "Closest to a Retribution Paladin's Holy Power loop,
                         where builders bank Oaths and a finisher spends
                         them." Dual-wield and DoT-forward (Condemn plus
                         Blade of Faith) with a Zealotry proc engine off the
                         off-hand rather than one clean nuke finisher.
  Oathkeeper  TANK       "Closest to a Brewmaster Monk fused with Mistweaver
                         fistweaving." Avoidance and absorbs rather than
                         block, and a damage-into-healing loop: Benediction
                         heals off Stamina, Condemn heals off its own damage.
  Crusader    MELEE DPS  "Closest to retail Retribution Paladin." Typed Oaths
                         that stack simultaneously on one shared Oath Chain,
                         so the job is keeping the Chain alive rather than
                         banking and dumping.

COMBO BUDGET. 100 pool (Character.SECONDARY_RESOURCE_MAX - Combo is a
dict-backed secondary with no override), and unlike Energy it has NO passive
regeneration: Character.restore_resources_between_turns regenerates Energy and
Mana only. Combo exists purely to be banked and spent, which is exactly what a
combo-point chain wants, so:

  Oath builders    cost 0 and carry generates {"resource": "combo",
                   "amount": 20}. 20 Combo is one Oath, so the pool holds
                   five, the same bank a real combo-point class carries.
  Oath Breakers    cost a flat 40 (two Oaths), 60 (three) or 80 (the whole
                   bank for Righteous Tempest). Flat across ranks, like the
                   Rogue's, because a cost over 100 would make an ability
                   uncastable forever - validate_class.py fails on that.
  everything else  costs 0 or 20 and is throttled by its cooldown. CoA pays
                   for Librams, Testaments and Divine Force out of a separate
                   Energy pool the Frontier Templar does not have, so the
                   honest translation is that they do not compete with the
                   Oath bank.

NUMBERS ARE FRONTIER'S, NOT CoA'S. Damage curves copy the Rogue's shipped
shape (sinister_strike: 9 ranks at levels 1/6/12/18/24/32/40/48/56, flat
resource cost, linear growth), because the Rogue is the closest shipped
class - leather, one action a turn, builders into finishers. The cycle is
sized so a build-build-spend loop lands near the shipped per-turn throughput
of the Rogue's energy-limited filler rather than above it: at rank 9 two
builders plus Chastise is 82 + 82 + 234 over three turns, 133 a turn, against
the Warrior/Guardian filler's ~128.

FOUR ENGINE CONVENTIONS THIS FILE HAD TO GET RIGHT, all of them traps:

  buff effect_value   A buff or debuff's stat_mods are multiplied by
                      effect_value / 100 (Ability._apply_effect, "stat_mods
                      scale with rank via effect_value acting as a
                      multiplier"). effect_value 0 therefore zeroes every
                      stat_mod on the ability. `one()` below defaults to 100
                      for that reason; the shipped Rogue buffs all use 100.
  damage from a buff  A buff cannot raise outgoing damage through
                      physical_damage / spell_damage / holy_spell_damage:
                      Ability._damage_multiplier reads those through
                      _talent() -> get_talent_effect, which sees talents,
                      stances and forms only, never status effects. The key
                      a buff has to use is damage_dealt_pct (percent POINTS),
                      with healing_done_pct for healing.
  _taken_pct units    damage_taken_pct is a FRACTION from both sources, but
                      physical_damage_taken_pct and magic_damage_taken_pct
                      are a FRACTION in a talent's effects and percentage
                      POINTS in an ability or proc's stat_mods. Same for
                      threat_generation_pct: 0.08 in a talent, 200 in a buff.
  AoE                 is target_type "enemy_aoe" plus max_targets. The
                      `is_aoe` field is not read by anything - see the
                      findings note at the bottom of this docstring.

Talent effect keys are restricted to ones the engine actually reads, verified
with tools/validate_class.py, which delegates liveness to
tools/audit_talents.py. CoA mechanics this engine cannot express, and what
each one became instead, are recorded in the _source note on the node or
ability that carries them. The recurring ones: there is no stagger/delayed
damage, no silence, no movement speed, no expertise, no off-hand split, and no
Oath Chain timer, so Keeping the Oath is flat mitigation, Interdict is a spell
hit-chance debuff, Courage-style speed is haste, expertise is hit rating,
off-hand damage is flat physical damage, and the Chain is simply the Combo
bank itself.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Rogue's shipped rank schedule - see module docstring.
RANK_LEVELS = [1, 6, 12, 18, 24, 32, 40, 48, 56]

#: One Oath. Builders generate this much Combo; Oath Breakers spend multiples
#: of it, so the tooltip arithmetic a player does is in whole Oaths.
OATH = 20


def ranks(base, step, cost, start=1, count=9, heal=0, heal_step=0):
    """Flat-cost rank table on the Rogue schedule, starting at `start`.

    Levels past the 9-rank schedule are spaced evenly to stay under 58 so
    every rank is actually reachable at the level 60 cap.

    `heal`/`heal_step` fill the per-rank heal_value key that effect_type
    "damage_and_heal" reads (Ability.heal_value) - without it the heal side of
    Argent Blade and Titanstrike would be nothing but healing-power scaling.
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
        if heal:
            rank["heal_value"] = int(round(heal + heal_step * i))
        out.append(rank)
    return out


def one(level, cost, value=100):
    """Single-rank table, for cooldowns and stances that do not scale.

    value defaults to 100, NOT 0. A buff/debuff's stat_mods are scaled by
    effect_value / 100 in Ability._apply_effect, so a one-rank buff authored
    with effect_value 0 grants exactly nothing - every shipped Rogue buff
    (Slice and Dice, Sprint, Feint, Kick) carries 100 for this reason. Pass
    value=0 only for effect_types that ignore effect_value entirely (dispel,
    reset_cooldowns).
    """
    return [{"rank": 1, "level_req": level, "cost": cost, "effect_value": value}]


def ability(aid, name, effect_type, description, rank_table, *, cooldown=0,
            duration=0, stat_mods=None, icon="ability_melee", source=None,
            builder=False, **extra):
    out = {
        "ability_id": f"templar_{aid}",
        "name": name,
        "resource_type": "combo",
        "cooldown": cooldown,
        "effect_type": effect_type,
        "duration": duration,
        "stat_mods": stat_mods or {},
        "description": description,
        "ranks": rank_table,
        "icon_id": icon,
    }
    if builder:
        out["generates"] = {"resource": "combo", "amount": OATH}
    if source:
        out["_source"] = source
    out.update(extra)
    return out


# ============================================================== ability kit
# Order is roughly the order a player meets them: the shared Oath chain
# first, then the Librams and Testaments, then each spec's own kit.
ABILITIES = [
    ability("attack", "Attack", "damage",
            "A measured strike with your weapon.", one(1, 0, 0),
            source="Convention: every class ships a free rank-1 Attack. It is "
                   "also the hook ProcTrigger.ON_WEAPON_SWING fires off, "
                   "which is what Zealotry listens for."),

    # ---- the Oath chain, all three specs
    ability("righteous_lunge", "Righteous Lunge", "damage",
            "Cover the ground between you and strike on the way in. Grants "
            "an Oath.",
            ranks(26, 7, 0), builder=True, target_type="enemy",
            source="CoA: 'Open with Righteous Lunge to close the gap; it "
                   "grants its own Oath', and 'Righteous Lunge is the only "
                   "real engage'. Its Oath 'makes your abilities damage and "
                   "heal for more'. The baseline builder for every spec."),
    ability("chastise", "Chastise", "spell_damage",
            "Call down a single hard blow of Holy force. Consumes two Oaths.",
            ranks(74, 20, 2 * OATH), target_type="enemy",
            damage_school="holy", icon=None,
            source="CoA: Chastise is the Oath Breaker all three specs share "
                   "('dump an Oath Breaker: Chastise, Blade of Faith, Divine "
                   "Fury or Righteous Upheaval'). The cheap finisher, so it "
                   "carries no cooldown - the Oath bank is its gate."),
    ability("condemn", "Condemn", "spell_dot",
            "Mark an enemy as condemned, burning them with Holy damage over "
            "4 turns. Grants an Oath.",
            ranks(64, 17, 0, start=4, count=8), duration=4, builder=True,
            target_type="enemy", damage_school="holy", icon=None,
            source="CoA: 'Condemn for the crit Oath and its stacking Holy "
                   "damage-over-time', and 'Condemn carries a huge share of "
                   "your damage per press'. Oathkeeper's Uther's Legacy and "
                   "Crusader's Tyr's Blessing both key off it."),
    ability("holy_cleave", "Holy Cleave", "spell_damage",
            "A wide sweep of Holy light that catches up to three enemies. "
            "Grants an Oath.",
            ranks(36, 10, 0, start=6, count=8), builder=True,
            target_type="enemy_aoe", max_targets=3, damage_school="holy",
            icon=None,
            source="CoA: 'Build Holy Cleave for the extra-target Oath; around "
                   "10 stacks covers a normal pull'. Its Oath 'makes your "
                   "abilities strike an additional nearby target', which has "
                   "no engine hook, so the cleave is on the ability itself."),
    ability("temple_guardian", "Temple Guardian", "heal",
            "Charge to your allies' side. Everyone who sees you come is "
            "steadier for it.",
            ranks(50, 17, 0, start=8, count=7), cooldown=4,
            target_type="party", icon=None,
            source="CoA: 'Temple Guardian is your gap-closer and opener. It "
                   "charges to an ally, healing you both, 3 charges on a 35 "
                   "sec recharge'. There is no two-target heal and no charge "
                   "system, so it heals the party on a short cooldown."),
    ability("benediction", "Benediction", "heal",
            "Speak a blessing over a wounded ally. Consumes two Oaths.",
            ranks(96, 34, 2 * OATH, start=10, count=7), cooldown=2,
            target_type="ally", icon=None,
            source="CoA: 'Benediction is your baseline reactive heal. It "
                   "scales with Stamina and consumes banked Oaths for extra "
                   "healing'. The Stamina scaling is a real conversion key - "
                   "see Oathkeeper's Fortified Body."),
    ability("blade_of_faith", "Blade of Faith", "spell_dot",
            "Drive your faith into the wound and leave it burning for 5 "
            "turns. Consumes three Oaths.",
            ranks(125, 32, 3 * OATH, start=12, count=7), cooldown=4,
            duration=5, target_type="enemy", damage_school="holy", icon=None,
            source="CoA: 'Blade of Faith, a long, hard-critting DoT' and "
                   "'Unleash a devastating Oath Breaker ... dealing AP Holy "
                   "damage over 21 seconds'. Chained against Righteous "
                   "Upheaval rather than spammed."),
    ability("divine_force", "Divine Force", "spell_damage",
            "Leap at an enemy hard enough to put them on the ground and stop "
            "whatever they were saying.",
            ranks(58, 16, OATH, start=16, count=6), cooldown=5,
            target_type="enemy", damage_school="holy", is_stun=True,
            icon=None,
            source="CoA class tree: 'Leap at an enemy with divine force, "
                   "stunning them for 6 seconds, dealing AP Holy damage, and "
                   "interrupting non-player spellcasting'. The stun is real; "
                   "the interrupt has no engine hook, and Interdict below "
                   "carries the caster-shutdown half of the kit."),
    ability("interdict", "Interdict", "debuff",
            "Forbid an enemy from sinning. For 2 turns their spells will not "
            "find their mark.",
            one(20, 0), cooldown=6, duration=2,
            stat_mods={"hit_chance_spell": -70}, target_type="enemy",
            icon=None,
            source="CoA: 'Interdict silences a target and locks Undead and "
                   "Demons out of healing'. No silence or cast-interrupt "
                   "mechanic exists, so this follows the shipped Rogue Kick "
                   "convention and guts the target's spell hit chance "
                   "instead."),
    ability("silverhand_incantation", "Silverhand Incantation", "damage_and_heal",
            "Throw a holy hammer and follow it in. It lands hard on everyone "
            "in front of you and mends everyone behind you. Consumes two "
            "Oaths.",
            ranks(80, 22, 2 * OATH, start=32, count=5, heal=70, heal_step=20),
            cooldown=8, target_type="enemy_aoe", max_targets=4,
            heal_scope="party", damage_school="holy", icon=None,
            source="CoA class tree: 'toss a holy hammer at your target, "
                   "charging you to them ... you deal AP Holy damage to all "
                   "nearby enemies and heal nearby allies for the same "
                   "amount'. damage_and_heal with heal_scope party is exactly "
                   "that shape."),

    # ---- Librams. One at a time: exclusive_group is passed straight to the
    # StatusEffect, so applying a new Libram replaces the active one.
    ability("libram_of_consecration", "Libram of Consecration", "buff",
            "Read the consecration aloud. Everything you do for the next 3 "
            "turns lands with Holy force behind it, increasing your damage "
            "by 10%.",
            one(14, 0), cooldown=6, duration=3,
            stat_mods={"damage_dealt_pct": 10.0}, target_type="self",
            buff_scope="combat", exclusive_group="templar_libram", icon=None,
            source="CoA: 'Libram of Consecration adds Holy damage to your "
                   "damaging abilities' and 'Only one Libram can be active at "
                   "a time'. damage_dealt_pct is the key a BUFF has to use - "
                   "a buff's stat_mods never reach _damage_multiplier's "
                   "talent lookups."),
    ability("libram_of_fervor", "Libram of Fervor", "buff",
            "Read the fervor aloud, and your training answers in a language "
            "it does not usually speak. Grants spell power equal to 30% of "
            "your Agility and attack power equal to 30% of your Intellect "
            "for 3 turns.",
            one(18, 0), cooldown=6, duration=3,
            stat_mods={"spell_power_from_agility_pct": 0.30,
                       "ap_from_intellect_pct": 0.30},
            target_type="self", buff_scope="combat",
            exclusive_group="templar_libram", icon=None,
            source="CoA class tree, verbatim: 'granting you spell power equal "
                   "to 30% of your Agility and attack power equal to 30% of "
                   "your Intellect for 20 seconds'. Both are real "
                   "<target>_from_<source>_pct conversions, and the "
                   "conversion loop in _recalculate_derived_stats reads the "
                   "shared bonus pool, so a buff can carry them."),
    ability("libram_of_zeal", "Libram of Zeal", "buff",
            "Read the zeal aloud and stop pacing yourself. Increases your "
            "haste by 20 for 3 turns.",
            one(22, 0), cooldown=6, duration=3, stat_mods={"haste": 20.0},
            target_type="self", buff_scope="combat",
            exclusive_group="templar_libram", icon=None,
            source="CoA Zealot: 'Libram of Zeal ... increasing your melee "
                   "haste by 20%'."),
    ability("libram_of_tenacity", "Libram of Tenacity", "buff",
            "Read the tenacity aloud. Physical blows land 20% lighter for 3 "
            "turns.",
            one(26, 0), cooldown=10, duration=3,
            stat_mods={"physical_damage_taken_pct": -20.0},
            target_type="self", buff_scope="combat",
            exclusive_group="templar_libram", icon=None,
            source="CoA class tree: 'reducing your Physical Damage taken by "
                   "-30% for 20 seconds'. Trimmed to -20% because it sits on "
                   "a 10 turn cooldown next to Guardian's Raise Shield "
                   "(-40%, 2 turns) rather than being a panic button. NOTE "
                   "the units: physical_damage_taken_pct is percentage "
                   "POINTS in an ability's stat_mods and a FRACTION in a "
                   "talent's effects."),
    ability("libram_of_grace", "Libram of Grace", "hot",
            "Read the grace aloud. For 3 turns the light that follows you "
            "mends whoever is standing in it.",
            ranks(150, 45, 0, start=30, count=5), cooldown=8, duration=3,
            target_type="party", icon=None,
            source="CoA: 'Libram of Grace makes each of them restore health "
                   "to you and nearby allies, which on a large pull is party "
                   "throughput'. The one Libram that is NOT in the exclusive "
                   "group: the hot branch of _apply_effect does not pass "
                   "exclusive_group to the StatusEffect it builds, so the "
                   "one-Libram-at-a-time rule cannot bind a heal-over-time."),

    # ---- Testaments. CoA's Sacred Restraint blocks a second Testament for a
    # minute, which exclusive_group models for the ones that leave a buff.
    ability("testament_of_fortitude", "Testament of Fortitude", "hot",
            "Stop fighting and meditate. Closes your wounds over 3 turns.",
            ranks(260, 80, 0, start=24, count=5), cooldown=12, duration=3,
            target_type="self", icon=None,
            source="CoA class tree: 'Meditate for 15 seconds, restoring 5% of "
                   "your maximum health every 1 sec and reducing damage taken "
                   "by -50%'. The mitigation half is dropped: a HOT's "
                   "stat_mods never reach get_status_stat_mod, which is where "
                   "damage_taken_pct is read, so it would have been silently "
                   "inert. The heal is the half worth keeping."),
    ability("testament_of_will", "Testament of Will", "dispel",
            "Break an ally free of whatever is holding them in place.",
            one(28, 0, 0), cooldown=8, target_type="ally",
            dispel_type="movement", icon=None,
            source="CoA class tree: 'Break an ally free of worldly "
                   "constraints, making them immune to all movement "
                   "impairing effects for 10 seconds'. No immunity window "
                   "exists; a movement dispel is the honest half."),
    ability("testament_of_faith", "Testament of Faith", "heal",
            "A prayer you only get to make once in a while, and it works.",
            ranks(300, 95, 0, start=34, count=5), cooldown=10,
            target_type="ally", icon=None,
            source="CoA Oathkeeper weaknesses: 'Testament of Faith and the "
                   "class kit's Libram of Tenacity each live on their own "
                   "cooldown'. Its own class-tree node Final Prayer 'doubles "
                   "the healing done to you by Testament of Fortitude and "
                   "Testament of Faith', so it is a burst heal. Sacred "
                   "Restraint cannot bind it - an instant heal leaves no "
                   "StatusEffect for exclusive_group to sit on."),
    ability("testament_of_hope", "Testament of Hope", "buff",
            "Two of you walk out of the light. Blows meant for you land 20% "
            "lighter for 3 turns.",
            one(38, 0), cooldown=14, duration=3,
            stat_mods={"damage_taken_pct": -0.20}, target_type="self",
            buff_scope="combat", exclusive_group="templar_testament",
            icon=None,
            source="CoA class tree: 'Summons 2 copies of yourself that charge "
                   "at a nearby enemy and aid you in combat ... each copy "
                   "reduces all damage you take by -10%'. summon_pet needs a "
                   "template from combat/pet_templates.py and none of the "
                   "fifteen is a mirror of the caster, so the copies are "
                   "represented by the mitigation they grant: two copies, "
                   "-10% each, -20%. damage_taken_pct is a FRACTION."),

    # ---- Zealot
    ability("vindication", "Vindication", "damage",
            "A short, zealous strike that gets straight to the point. Grants "
            "an Oath.",
            ranks(34, 10, 0, start=10, count=7), builder=True,
            target_type="enemy",
            source="CoA Zealot: 'Righteous Lunge and Vindication are your "
                   "Oath builders, each granting an Oath, and Vindication "
                   "triggers Zealotry'. Its own Oath gives 'your damaging "
                   "abilities a 10% chance to trigger Zealotry'."),
    ability("righteous_upheaval", "Righteous Upheaval", "damage",
            "Bring everything you have been holding back down at once. "
            "Consumes three Oaths.",
            ranks(96, 27, 3 * OATH, start=20, count=6), cooldown=3,
            target_type="enemy",
            source="CoA Zealot: 'Unleash a dominating Oath Breaker, dealing "
                   "SP Physical damage, increased by 3% for each time you "
                   "triggered Zealotry during your Oath Chain'. Physical, not "
                   "Holy, which is why it is the one Zealot finisher that "
                   "does not want Holy scaling."),
    ability("divine_fury", "Divine Fury", "spell_damage",
            "A cleaving blow of Holy fire that comes apart on impact and "
            "catches up to four enemies. Consumes two Oaths.",
            ranks(66, 19, 2 * OATH, start=26, count=5), cooldown=4,
            target_type="enemy_aoe", max_targets=4, damage_school="holy",
            icon=None,
            source="CoA Zealot: 'Every ~10 Zealotries your Chastise becomes "
                   "Divine Fury, a cleave holy hit that shreds armor'. There "
                   "is no ability-transform mechanic, so it is its own "
                   "button, and the armour shred is dropped - a damage "
                   "ability cannot also apply a debuff."),
    ability("force_of_golganneth", "Force of Golganneth", "spell_dot",
            "Detonate. The light keeps going off for 3 turns and everything "
            "nearby stays inside it.",
            ranks(165, 46, OATH, start=36, count=4), cooldown=12, duration=3,
            target_type="enemy_aoe", max_targets=5, damage_school="holy",
            icon=None,
            source="CoA Zealot: 'Force of Golganneth is a two-minute "
                   "cooldown that explodes for holy damage and triggers "
                   "Zealotry on every nearby enemy for several seconds' and "
                   "'Force of Golganneth is your best AoE button'. A "
                   "repeating explosion over several seconds is a DoT here."),
    ability("mortal_abdication", "Mortal Abdication", "damage",
            "One strike, delivered like a verdict.",
            ranks(140, 40, OATH, start=40, count=4), cooldown=8,
            target_type="enemy",
            source="CoA names Mortal Abdication twice as a Zealot cooldown "
                   "(One With The Light 'reduces the cooldown of Librams, "
                   "Force of Golganneth, and Mortal Abdication', and Libram "
                   "of Zeal is read 'from your Libram of Mortal "
                   "Abdication') without ever stating what it does. "
                   "Implemented as the single-target counterpart to Force of "
                   "Golganneth on the same cooldown band, which is the only "
                   "thing the surrounding text supports. GAP: its real "
                   "mechanic is not in the reference."),
    ability("norgannons_wrath", "Norgannon's Wrath", "spell_damage",
            "Leap, hang a moment, and come down as a column of light. "
            "Consumes two Oaths.",
            ranks(200, 60, 2 * OATH, start=46, count=3), cooldown=10,
            target_type="enemy_aoe", max_targets=5, damage_school="holy",
            requires_talent=True, icon=None,
            source="CoA Zealot tier-6 talent, verbatim: 'Target an enemy and "
                   "leap into the air. After a short delay, you blast them "
                   "with immense holy force, dealing holy AP Holy damage to "
                   "up to 10 enemies within 5 yds'. A talent in CoA, so a "
                   "talent here: unlocked by the Zealot capstone, hence "
                   "requires_talent. The immunity-piercing and the "
                   "damage/healing-done debuff have no engine hooks."),

    # ---- Oathkeeper
    ability("sacred_swing", "Sacred Swing", "damage",
            "Swing wide at everything in front of you. Grants an Oath.",
            ranks(32, 9, 0, start=10, count=7), cooldown=2, builder=True,
            target_type="enemy_aoe", max_targets=3,
            source="CoA Oathkeeper: 'Sacred Swing (usable off an avoided "
                   "attack)' and 'Use Sacred Swing on cooldown whenever it's "
                   "up, after a dodge or parry, for cheap AoE damage and a "
                   "Staffguard absorb'. The dodge/parry gate has no engine "
                   "hook - no ability can require a recent avoidance - so it "
                   "sits on a 2 turn cooldown instead, which is the closest "
                   "honest throttle. Staffguard is the talent that reads it."),
    ability("reckoning", "Reckoning", "spell_damage",
            "Call the whole pull to account at once, striking up to four "
            "enemies. Consumes two Oaths.",
            ranks(72, 20, 2 * OATH, start=16, count=6), cooldown=2,
            target_type="enemy_aoe", max_targets=4, damage_school="holy",
            icon=None,
            source="CoA Oathkeeper: 'Spend into Reckoning as your default "
                   "Oath Breaker while leveling. It deals AoE Holy damage and "
                   "restores Energy per enemy struck'. The Energy refund is "
                   "dropped - a finisher that refunded Combo would undo its "
                   "own cost, and the Templar has no second pool to refund "
                   "into. Sacred Resistance is the talent that reads it."),
    ability("absolution", "Absolution", "buff",
            "Make yourself the only thing in the room worth hitting.",
            one(20, 0), cooldown=8, duration=2,
            stat_mods={"threat_generation_pct": 200}, target_type="self",
            buff_scope="combat", icon=None,
            source="CoA Oathkeeper: 'Taunt all enemies within 8 yds for 4 "
                   "seconds', 'Pull with Absolution to taunt and establish "
                   "threat' and 'Use Absolution to peel adds off the actual "
                   "healer'. Implemented as a threat_generation_pct buff, the "
                   "convention Guardian's Challenging Cry (200) and Cultist's "
                   "Twilight Domain (180) already use - an ability buff's "
                   "stat_mods are percentage POINTS here, unlike a talent's "
                   "effects, which are fractions."),
    ability("barrier_of_light", "Barrier of Light", "buff",
            "Put a wall of light around your allies. Healing reaches them 30% "
            "better through it.",
            one(30, 0), cooldown=10, duration=3,
            stat_mods={"healing_taken_pct": 30.0}, target_type="party",
            buff_scope="combat", icon=None,
            source="CoA Oathkeeper: 'Emit saving light, increasing the "
                   "healing received by nearby allies by 40% for 15 seconds. "
                   "For the duration, threat generated by your allies is "
                   "redirected to you.' The redirect half is dropped: one "
                   "stat_mods dict applies to every recipient, so a threat "
                   "key here would land on the allies too, which is backwards."),
    ability("spiritual_abdication", "Spiritual Abdication", "buff",
            "Set your own body aside for 3 turns. What is left standing is "
            "harder to hurt.",
            one(40, 0), cooldown=12, duration=3,
            stat_mods={"damage_taken_pct": -0.15, "armor_pct": 15.0},
            target_type="self", buff_scope="combat", icon=None,
            source="CoA Oathkeeper's Spiritual Abdicator node ('Your "
                   "Spiritual Abdication now reduces damage taken by an "
                   "additional -5% per copy') is the only mention of the "
                   "ability, and it names copies and damage reduction, so "
                   "this is Testament of Hope's defensive sibling. GAP: the "
                   "ability's own tooltip is not in the reference."),
    ability("tome_of_light", "Tome of Light", "buff",
            "Open the tome. For 3 turns a shield of light takes the hits "
            "instead of you.",
            one(44, 0), cooldown=15, duration=3, absorb_pct_max_health=0.40,
            target_type="self", buff_scope="combat", requires_talent=True,
            icon=None,
            source="CoA Oathkeeper: 'Tome of Light shields for 100% of max "
                   "health', 'Pop Tome of Light's full-health shield as your "
                   "defensive cooldown when a burst AoE phase hits'. A "
                   "tier-6 talent in CoA, so a talent here. 100% of max "
                   "health is far outside what any shipped absorb does "
                   "(Cultist's Eldritch Bastion, the biggest, is 0.35), so "
                   "it lands at 0.40 - the largest in the game, without being "
                   "triple the next one."),

    # ---- Crusader
    ability("argent_blade", "Argent Blade", "damage_and_heal",
            "A blow struck with argent fervour. What it takes out of them "
            "comes back into you. Grants an Oath.",
            ranks(84, 24, 0, start=12, count=7, heal=40, heal_step=12),
            cooldown=2, builder=True, target_type="enemy",
            source="CoA Crusader: 'Crush an enemy with argent fervor ... "
                   "healing you equal to the damage dealt, and extending the "
                   "duration of your Oath Chain by 3 sec', 'keep Argent Blade "
                   "flowing to extend the Oath Chain'. There is no Oath Chain "
                   "timer, so extending it becomes generating an Oath, which "
                   "is the same thing: the Combo bank IS the Chain. The heal "
                   "goes through heal_scope lowest_ally, so solo it lands on "
                   "the Templar as written, and in a party it finds whoever "
                   "needs it more."),
    ability("titanstrike", "Titanstrike", "damage_and_heal",
            "Finish a wounded enemy and take back what the fight cost you. "
            "Consumes two Oaths.",
            ranks(190, 54, 2 * OATH, start=22, count=6, heal=70, heal_step=22),
            cooldown=3, target_type="enemy", execute_threshold_pct=35,
            source="CoA Crusader: 'Titanstrike is your execute below 35% "
                   "health and heals you for the damage dealt, twice that "
                   "with Titanfall talented'. execute_threshold_pct is a "
                   "PERCENT here, not a fraction - the engine compares it "
                   "against target health on a 0-100 scale, and every shipped "
                   "execute (Warrior 20, Cultist 35, Primalist 25/50) is "
                   "written that way."),
    ability("righteous_tempest", "Righteous Tempest", "dot",
            "Open up and keep turning for 3 turns. Consumes four Oaths, the "
            "whole bank.",
            ranks(210, 58, 4 * OATH, start=28, count=5), cooldown=8,
            duration=3, target_type="enemy_aoe", max_targets=5,
            requires_talent=True, damage_school="physical", icon=None,
            source="CoA Crusader: 'Unleash a whirling Oath Breaker, dealing "
                   "Weapon Damage plus SP damage to nearby enemies ... every "
                   "1 sec for 3 seconds' and 'Righteous Tempest consumes the "
                   "entire bank for a 3-second whirl'. The only 80-cost "
                   "ability in the kit, which is the whole 100 pool minus one "
                   "Oath. A talent in CoA, so requires_talent here."),
    ability("scarlet_hammer", "Scarlet Hammer", "spell_damage",
            "Drop a scarlet hammer on them from somewhere above.",
            ranks(110, 31, 2 * OATH, start=30, count=5), cooldown=4,
            target_type="enemy", damage_school="holy", icon=None,
            source="CoA Crusader: 'Drop a scarlet hammer on an enemy for 155% "
                   "Weapon Damage plus 35 as Holy Damage and reduce their "
                   "Armor by 555 for 10 seconds'. Reached in CoA by casting "
                   "Argent Blade under Warrior of Dawn, which no "
                   "ability-transform mechanic can express, so it is its own "
                   "button. The armour reduction is dropped for the same "
                   "reason as Divine Fury's."),
    ability("crusaders_brand", "Crusader's Brand", "debuff",
            "Brand an enemy. They are not getting away from you, and they "
            "will feel it every time they swing.",
            one(24, 0), cooldown=6, duration=3, stat_mods={"haste": -20.0},
            target_type="enemy", icon=None,
            source="CoA Crusader: 'Crusader's Brand pins a runner so they "
                   "cannot flee, mount, or speed away, and reveals them "
                   "through stealth'. No movement, mount or stealth systems "
                   "exist, so the pin is a haste slow, the shipped "
                   "convention for a snare (Rogue's Crippling Poison, -30)."),
    ability("divine_charge", "Divine Charge", "buff",
            "You and yours come up onto the light and move. Increases the "
            "party's haste by 15 for 3 turns.",
            one(42, 0), cooldown=12, duration=3, stat_mods={"haste": 15.0},
            target_type="party", buff_scope="combat", icon=None,
            source="CoA Crusader: 'Divine Charge gives the party a mounted "
                   "speed burst outdoors that does not break on casting', "
                   "'Divine Charge only works outdoors, so it is not your "
                   "dungeon opener'. There is no indoor/outdoor gate and no "
                   "movement speed, so it is a party haste window. The "
                   "trample damage is dropped."),
    ability("testament_of_strength", "Testament of Strength", "buff",
            "Swear the strength oath. For 3 turns Titanstrike needs no "
            "wounded enemy, and everything you do hits 25% harder.",
            one(46, 0), cooldown=15, duration=3,
            stat_mods={"damage_dealt_pct": 25.0}, target_type="self",
            buff_scope="combat", exclusive_group="templar_testament",
            proc={"bypass_execute_threshold": True}, icon=None,
            source="CoA Crusader tier-6: 'Your next 3 Titanstrikes are usable "
                   "regardless of your target's health percentage and deal "
                   "25% increased damage. Lasts 1 minute.' The HP-gate "
                   "bypass is real, not an approximation: a buff carrying "
                   "proc.bypass_execute_threshold is exactly what use() "
                   "checks before the execute gate (the hook Warrior's Sudden "
                   "Death was written for). One use per cast, since use() "
                   "strips the effect when it spends it."),
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


# ================================================================== Zealot
Z = "templar_zealot"
ZEALOT = tree(
    Z, "Templar Zealot",
    "Oath melee DPS with a proc engine underneath it. Builders bank Oaths, "
    "Zealotry fires off your own swings, and the damage lives in two long "
    "Holy damage-over-time effects rather than one clean nuke.",
    [
        node(Z, "martial_paladin", "Martial Paladin",
             "Increases your Agility by 2% and your hit rating by 1 per rank.",
             0, 0, 5, {"agility_pct": 2.0, "hit_rating": 1},
             source="CoA: 'Increases your Agility by 5% and your chance to "
                    "hit by 3%' (2 ranks). Agility is the Templar's primary "
                    "stat, and the spec's priority leads 'Attack Power ... "
                    "Agility (AP + crit)'."),
        node(Z, "solemn_soldier", "Solemn Soldier",
             "Increases your haste by 2 and your hit rating by 1 per rank.",
             0, 1, 5, {"haste": 2.0, "hit_rating": 1},
             source="CoA: 'Increases your melee haste by 5% and expertise by "
                    "5' (2 ranks). There is no expertise stat in this engine "
                    "and no key for one, so the expertise half lands as hit "
                    "rating, which is the other 'stop missing' stat the "
                    "spec's priority caps first."),
        node(Z, "bursting_impact", "Bursting Impact",
             "Increases your physical damage by 2% per rank.",
             0, 2, 5, {"physical_damage": 0.02},
             source="CoA: 'Increases your off-hand weapon damage by 25%'. "
                    "This engine has one weapon damage figure and no "
                    "main-hand/off-hand split, so an off-hand buff can only "
                    "be flat physical damage."),
        node(Z, "calm_combatant", "Calm Combatant",
             "Grants spell power equal to 6% of your attack power per rank.",
             0, 3, 5, {"spell_damage_from_ap_pct": 0.06},
             source="CoA free level-20 passive, verbatim: 'Increases your "
                    "Holy spell damage by 30% of your attack power'. 5 ranks "
                    "of 6% is exactly that 30%. This node is why a leather "
                    "Agility class can press Holy abilities at all - without "
                    "it Chastise and Condemn scale off a spell power stat "
                    "the Templar never gears."),

        node(Z, "condemnation", "Condemnation",
             "Increases the damage of Condemn by 6% per rank.",
             1, 0, 5, {"ability_templar_condemn_damage": 0.06},
             connect=["martial_paladin"],
             source="CoA has two separate Zealot nodes called Condemnation, "
                    "one raising the crit Condemn grants and one giving "
                    "Condemn a chance to trigger Zealotry. Neither shape "
                    "exists here (an ability cannot grant crit, and a "
                    "per-ability proc chance has no hook), so the one node "
                    "carries Condemn's damage, which is where CoA says most "
                    "of the spec's damage lives."),
        node(Z, "zealotry", "Zealotry",
             "Your Attacks strike a second time for 40% of their damage.",
             1, 1, 1, {}, connect=["solemn_soldier"],
             proc={"trigger": "on_weapon_swing", "chance": 100, "icd": 0,
                   "bonus_pct": 0.40},
             source="CoA free level-10 passive: 'Your off-hand auto attacks "
                    "now trigger Zealotry. Zealotry (Proc): Deals 40% "
                    "off-hand Weapon Damage as Holy Damage.' "
                    "ON_WEAPON_SWING fires only off the class's own "
                    "<prefix>_attack, which is as close to 'auto attack' as "
                    "this engine gets. The bonus hit carries no school: a "
                    "talent's synthetic StatusEffect is built without a "
                    "damage_school, so bonus_pct damage resolves untyped "
                    "rather than as Holy."),
        node(Z, "blade_sermon", "Blade Sermon",
             "Increases your Holy damage by 2% per rank.",
             1, 2, 5, {"holy_spell_damage": 0.02},
             connect=["bursting_impact"],
             source="CoA: 'Increases the Weapon Damage dealt by Zealotry by "
                    "10%' (2 ranks). Zealotry's proc damage cannot be scaled "
                    "by a talent key, so the node scales the Holy half of the "
                    "kit it belongs to instead."),
        node(Z, "chakra_of_power", "Chakra of Power",
             "Your Attacks restore 10 Combo.",
             1, 3, 1, {}, connect=["calm_combatant"],
             proc={"trigger": "on_weapon_swing", "chance": 100, "icd": 0,
                   "grant_resource": {"resource": "combo", "amount": 10}},
             source="CoA: 'Melee attacks now restore 1 Energy, plus an "
                    "additional 2 Energy when they critically strike', and "
                    "'Chakra of Power refunds Energy on melee hits so the "
                    "loop rarely starves'. Combo has no passive regeneration "
                    "at all, so this is the only thing in the game that "
                    "generates it outside a builder. One point, not three: "
                    "grant_resource's amount is fixed, not scaled by rank."),

        node(Z, "one_punch_man", "One-Punch Man",
             "Increases the damage of Chastise and Righteous Upheaval by 8% "
             "per rank.",
             2, 0, 3, {"ability_templar_chastise_damage": 0.08,
                       "ability_templar_righteous_upheaval_damage": 0.08},
             connect=["condemnation"],
             source="CoA: 'Increases the the damage of Oath Breakers and "
                    "Titanstrike by 20%'. Titanstrike belongs to Crusader, so "
                    "this names Zealot's own two Oath Breakers."),
        node(Z, "iron_penance", "Iron Penance",
             "Your damage leaves the target taking 2% more physical damage "
             "per rank for 3 turns.",
             2, 1, 3, {}, connect=["zealotry"],
             proc={"trigger": "on_damage_cast", "chance": 20, "icd": 1,
                   "apply_effect": {
                       "effect_id": "templar_iron_penance",
                       "name": "Iron Penance",
                       "effect_type": "debuff",
                       "duration": 3,
                       "stat_mods": {"physical_damage_taken_pct": 2.0},
                       "on_target": True}},
             source="CoA: 'Dealing damage with Zealotry now applies Iron "
                    "Penance to the target, increasing their Physical damage "
                    "taken by you by 1% for 3 seconds, stacking 10 times'. "
                    "The ten-stack ramp has no hook here, so the per-rank "
                    "value carries it instead. NOTE the units: a proc's "
                    "apply_effect stat_mods are percentage POINTS, the "
                    "opposite of the same key in a talent's effects."),
        node(Z, "deliverance", "Deliverance",
             "Increases your critical strike damage by 4% per rank.",
             2, 2, 5, {"crit_damage_physical": 0.04},
             connect=["blade_sermon"],
             source="CoA: 'Critically striking with Vindication or Righteous "
                    "Lunge now deals 50% additional Physical damage'. A "
                    "per-ability crit damage key exists, but the spec's two "
                    "builders are both physical, so one crit damage node "
                    "covers them without splitting the point."),
        node(Z, "heavens_finest", "Heaven's Finest",
             "Reduces the Combo cost of your abilities by 3% per rank.",
             2, 3, 5, {"all_ability_cost_pct": -0.03},
             connect=["chakra_of_power"],
             source="CoA: 'At 6 stacks, increases your Energy regeneration by "
                    "100% for 8 seconds'. Combo regeneration does not exist "
                    "to increase, and combo_max is reported dead by the "
                    "validator even though get_resource_max would read it, "
                    "so the honest version of 'the loop starves less' is a "
                    "cheaper loop."),

        node(Z, "upheave", "Upheave!",
             "Increases the critical strike damage of Righteous Upheaval by "
             "10% per rank.",
             3, 0, 2, {"ability_templar_righteous_upheaval_crit_damage": 0.10},
             connect=["one_punch_man"],
             source="CoA: 'Increases the critical damage of Righteous "
                    "Upheaval by 20%'. ability_<id>_crit_damage is a real "
                    "key, read in _crit_damage_bonus by interpolation - a "
                    "literal grep calls the whole family dead."),
        node(Z, "transcending_strikes", "Transcending Strikes",
             "Reduces the cooldown of Divine Force by 1 turn per rank.",
             3, 1, 2, {"ability_templar_divine_force_cooldown": 1},
             connect=["zealotry", "iron_penance"],
             source="CoA: 'Your Divine Force will now trigger a -30 sec "
                    "reduced cooldown when used on enemies affected by Blade "
                    "of Faith'. The conditional cannot be expressed, so the "
                    "reduction is unconditional and smaller."),
        node(Z, "battle_hardened", "Battle Hardened",
             "Reduces the cooldown of Righteous Upheaval by 1 turn per rank.",
             3, 2, 2, {"ability_templar_righteous_upheaval_cooldown": 1},
             connect=["deliverance"],
             source="CoA: 'Reduces the cooldown of Righteous Upheaval by -5 "
                    "sec'."),
        node(Z, "priest_training", "Priest Training",
             "Your damage knits you back together.",
             3, 3, 3, {}, connect=["heavens_finest"],
             proc={"trigger": "on_damage_cast", "chance": 20, "icd": 1,
                   "heal_flat": 40},
             source="CoA: 'Triggering Zealotry now also heals you for 3% of "
                    "your missing health'. A heal sized off missing health "
                    "has no payload shape, so it is a flat heal - the spec's "
                    "only sustain, which matches CoA: 'There's no self-heal "
                    "to lean on'."),

        node(Z, "unbroken_creed", "Unbroken Creed",
             "Your damage has a 15% chance per rank to give you an extra "
             "attack.",
             4, 0, 3, {}, connect=["upheave"],
             proc={"trigger": "on_damage_cast", "chance": 15, "icd": 1,
                   "extra_attack": True},
             source="CoA free level-50 passive: 'When you use a damaging Oath "
                    "Breaker or Divine Fury you now consume the stacks and "
                    "auto attack your target an amount of times equal to your "
                    "stack count'. extra_attack is a genuine second swing "
                    "that rolls its own hit and crit, which also means it "
                    "re-triggers Zealotry - the stacking count is what is "
                    "missing, not the mechanic."),
        node(Z, "devotion_of_khazgoroth", "Devotion of Khaz'goroth",
             "Increases your haste by 2 and your attack power by 2% per rank.",
             4, 1, 3, {"haste": 2.0, "attack_power_pct": 2.0},
             connect=["transcending_strikes", "battle_hardened"],
             source="CoA: 'Increases all party and raid member's melee and "
                    "ranged haste by 10%'. A talent's effects only ever apply "
                    "to its owner - there is no party-scoped talent effect - "
                    "so the raid haste CoA credits this spec with is on the "
                    "Templar alone."),
        node(Z, "holy_upheaval", "Holy Upheaval",
             "Increases the damage of Righteous Upheaval by 10% and your "
             "area damage by 4% per rank.",
             4, 2, 3, {"ability_templar_righteous_upheaval_damage": 0.10,
                       "aoe_damage": 0.04},
             connect=["priest_training"],
             source="CoA free level-30 passive: 'Increases the effectiveness "
                    "Righteous Upheaval gains per trigger of Zealotry by "
                    "100%'. Righteous Upheaval has no Zealotry counter here, "
                    "so doubling its scaling becomes raising its damage."),

        node(Z, "might_of_aggramar", "Might of Aggramar",
             "Increases the damage of Blade of Faith by 10% and all your "
             "damage over time by 3% per rank.",
             5, 0, 2, {"ability_templar_blade_of_faith_damage": 0.10,
                       "dot_damage": 0.03},
             connect=["unbroken_creed"], total_slots=3,
             source="CoA tier-6: 'Physical damage dealt now has a 25% chance "
                    "to increase the tick rate and reduce cooldown of your "
                    "next Blade of Faith by -10%, stacking 5 times'. Tick "
                    "rate is fixed at one tick per turn here, so faster ticks "
                    "become more damage."),
        node(Z, "one_with_the_light", "One With The Light",
             "Reduces the cooldown of Force of Golganneth and Mortal "
             "Abdication by 1 turn per rank.",
             5, 1, 2, {"ability_templar_force_of_golganneth_cooldown": 1,
                       "ability_templar_mortal_abdication_cooldown": 1},
             connect=["devotion_of_khazgoroth"], total_slots=3,
             source="CoA tier-6: 'Casting Oath Breakers now triggers Zealotry "
                    "on your target and reduces the cooldown of Librams, "
                    "Force of Golganneth, and Mortal Abdication by -1 sec'. "
                    "The cooldown half is the half that fits."),
        node(Z, "fury_of_aggramar", "Fury of Aggramar",
             "Libram of Consecration and Libram of Zeal last 1 turn longer "
             "per rank.",
             5, 2, 2, {"ability_templar_libram_of_consecration_duration": 1,
                       "ability_templar_libram_of_zeal_duration": 1},
             connect=["holy_upheaval"], total_slots=3,
             source="CoA tier-6: 'Increases the damage dealt by Libram of "
                    "Consecration by 100% and the effectiveness of your "
                    "Librams by 25%'. Libram effectiveness has no key, but "
                    "uptime does, and a rolling Libram cycle is what CoA says "
                    "the spec is doing: 'Cycle your Librams for a rolling "
                    "steroid'."),

        node(Z, "norgannons_wrath", "Norgannon's Wrath",
             "Grants Norgannon's Wrath, a leaping blast of Holy force that "
             "lands on up to five enemies.",
             6, 0, 1, {"unlock_ability": "templar_norgannons_wrath"},
             node_type="active",
             connect=["might_of_aggramar", "one_with_the_light",
                      "fury_of_aggramar"],
             total_slots=1,
             source="Capstone, and a real CoA tier-6 TE node rather than a "
                    "passive dressed as one. CoA rates Zealot B in dungeons "
                    "and B in raids on 'Solid sustained single-target DPS ... "
                    "high throughput ceiling', so the payoff is a button, not "
                    "a permanent multiplier."),
    ],
    "Built from reference/coa_sidekick/SPEC_templar__zealot.txt and the zealot "
    "half of reference/coa_sidekick/talents/templar.json. CoA calls this 'a "
    "Retribution Paladin's Holy Power loop, where builders bank Oaths and a "
    "finisher spends them', with the difference that it is 'dual-wield and "
    "DoT-forward (Condemn plus Blade of Faith) with a Zealotry proc engine off "
    "the off-hand rather than one clean nuke finisher'. Two things drove the "
    "selection. First, the Zealotry engine: this is the only spec in the game "
    "whose basic Attack is a rotational button, because Zealotry, Chakra of "
    "Power and Iron Penance all hang off ON_WEAPON_SWING, which fires only "
    "from templar_attack. Second, the stat priority leads with Attack Power "
    "because 'Calm Combatant scales Holy damage off AP' - so the AP-to-spell-"
    "power conversion is a tier-0 node, not a late one. CoA's optional Chakra "
    "of Light overlay ('turns your Oath Breakers into ally heals') is left "
    "out: nothing can convert a damage ability into a heal.")


# ============================================================== Oathkeeper
O = "templar_oathkeeper"
OATHKEEPER = tree(
    O, "Templar Oathkeeper",
    "Avoidance tank with a damage-into-healing loop. Dodge and parry come off "
    "Agility and Intellect rather than a shield, absorbs sit on top, and the "
    "Oath Breakers you spend can be heals instead of hits.",
    [
        node(O, "bells_of_light", "Bells of Light",
             "Increases your hit rating by 1 and your Stamina by 2 per rank.",
             0, 0, 5, {"hit_rating": 1, "stamina": 2},
             source="CoA: 'Increases your, and hit chance by 3%' (2 ranks - "
                    "the scrape lost a clause). The spec's stat priority "
                    "opens 'Hit Rating (until your specials stop missing a "
                    "+3-level target)', which for a tank is a threat stat."),
        node(O, "paragon", "Paragon",
             "Increases your Stamina by 3 per rank.",
             0, 1, 5, {"stamina": 3},
             source="CoA: 'Increases your Stamina by 10, plus an additional "
                    "amount equal to 10% of your Agility'. The Agility half "
                    "cannot be a conversion: STAT_CONVERSION_TARGETS has no "
                    "stamina entry, because no Character attribute is written "
                    "by one, so it is flat Stamina only."),
        node(O, "blessed_padding", "Blessed Padding",
             "Increases your Armor by 3% per rank.",
             0, 2, 5, {"armor_pct": 3.0},
             source="CoA: 'Increases your Armor contribution from mail items "
                    "by 50% and reduces damage taken from area of effect "
                    "attacks by -10%' (2 ranks). The Frontier Templar wears "
                    "leather, not mail (data/items/armor_types.json), and "
                    "there is no per-armour-type or AoE-taken key, so it is "
                    "plain Armor. NOTE armor_pct is percentage POINTS, unlike "
                    "most _pct keys."),
        node(O, "graceful_fighter", "Graceful Fighter",
             "Grants parry equal to 4% of your Agility and dodge equal to 4% "
             "of your Intellect per rank.",
             0, 3, 5, {"parry_from_agility_pct": 0.04,
                       "dodge_from_intellect_pct": 0.04},
             source="CoA free level-20 passive, verbatim: 'Increases your "
                    "parry rating by 20% of Agility and your dodge rating by "
                    "20% of Intellect'. 5 ranks of 4% is exactly that 20%. "
                    "This is the node that makes Oathkeeper an avoidance tank "
                    "rather than a block tank, and the reason the tree spends "
                    "almost nothing on block even though the class carries a "
                    "shield."),

        node(O, "sacred_oath", "Sacred Oath",
             "Increases your critical strike chance by 1% and reduces all "
             "damage you take by 1% per rank.",
             1, 0, 5, {"crit_chance_physical": 1.0, "damage_taken_pct": -0.01},
             connect=["bells_of_light"],
             source="CoA: 'Critical strikes now remove 1 sec from the "
                    "duration of Oathkeeper when used', where Oathkeeper is "
                    "the stagger pool. Nothing delays damage in this engine, "
                    "so shortening the delay becomes taking less of it, and "
                    "the crit that triggers it is on the same node."),
        node(O, "staffguard", "Staffguard",
             "Your damage raises a shield for a quarter of what you dealt.",
             1, 1, 1, {}, connect=["paragon"],
             proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
                   "ability_filter": ["templar_sacred_swing"],
                   "shield_pct": {"pct": 0.25,
                                  "effect_id": "templar_staffguard",
                                  "name": "Staffguard"}},
             source="CoA: 'Casting Sacred Swing now grants you Staffguard, "
                    "absorbing Stamina damage, scaling with Stamina, parry "
                    "and dodge rating, for 8 seconds'. shield_pct sizes the "
                    "absorb off the triggering hit rather than off Stamina, "
                    "which is the closest the payload set gets; "
                    "ability_filter pins it to Sacred Swing exactly as CoA "
                    "words it."),
        node(O, "conviction", "Conviction",
             "Increases your haste by 2 per rank.",
             1, 2, 5, {"haste": 2.0}, connect=["blessed_padding"],
             source="CoA: 'Casting Sacred Swing now increases your melee "
                    "haste by 5% for 15 seconds, stacking 4 times'. A "
                    "cast-driven stacking buff needs a proc with an "
                    "apply_effect; as a flat stat it is simply the haste the "
                    "stack would have reached, always on."),
        node(O, "parry_dance", "Parry Dance",
             "Increases your parry chance by 1% per rank.",
             1, 3, 3, {"parry": 1.0}, connect=["graceful_fighter"],
             source="CoA: 'When you critically strike with auto attacks or "
                    "parry an attack, your chance to parry is now increased "
                    "by 3% for 5 seconds, stacking 5 times'. Parry is full "
                    "avoidance here, not partial like block, which is why the "
                    "per-rank number is small."),

        node(O, "way_of_the_monk", "Way of the Monk",
             "Increases your dodge and parry chance by 1% per rank.",
             2, 0, 3, {"dodge": 1.0, "parry": 1.0}, connect=["sacred_oath"],
             source="CoA: 'Damage dealt by Sacred Swing and Reckoning now "
                    "reduces casting speed by -10% for 10 seconds'. There is "
                    "no cast speed to slow, so the node carries the avoidance "
                    "the spec is built on instead and keeps its name."),
        node(O, "uthers_legacy", "Uther's Legacy",
             "Condemn heals you for a quarter of the damage it deals.",
             2, 1, 1, {}, connect=["staffguard"],
             proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
                   "ability_filter": ["templar_condemn"],
                   "leech_pct": 0.25},
             source="CoA: 'Your Condemn now heals you for 75% of the damage "
                    "dealt', and 'Uther's Legacy even makes Condemn heal you "
                    "off the damage it deals, so the spec both tanks hits and "
                    "turns those same hits into sustain'. 75% on the full "
                    "damage of a free builder is more sustain than any "
                    "shipped leech, so it lands at 25%. leech_pct fires on "
                    "the cast, so the periodic ticks do not feed it - the "
                    "ticks run through tick_status_effects, which has no "
                    "caster reference to proc from."),
        node(O, "holy_warstaff", "Holy Warstaff",
             "Increases the damage of Reckoning by 8% per rank.",
             2, 2, 3, {"ability_templar_reckoning_damage": 0.08},
             connect=["conviction"],
             source="CoA: 'Increases the damage of Reckoning by 20%'."),
        node(O, "sacred_resistance", "Sacred Resistance",
             "Increases your Armor by 3% per rank.",
             2, 3, 5, {"armor_pct": 3.0}, connect=["parry_dance"],
             source="CoA: 'Casting Reckoning now increases your Armor by 15% "
                    "for 15 seconds', and 'Sacred Resistance bumps your Armor "
                    "when you cast it'. A cast-triggered window needs a proc "
                    "with an apply_effect; flat Armor is the always-on "
                    "version of the same number."),

        node(O, "untainted", "Untainted",
             "Your heals leave you taking 2% less physical damage per rank "
             "for 3 turns.",
             3, 0, 3, {}, connect=["way_of_the_monk"],
             proc={"trigger": "on_heal_cast", "chance": 100, "icd": 2,
                   "apply_effect": {
                       "effect_id": "templar_untainted",
                       "name": "Untainted",
                       "effect_type": "buff",
                       "duration": 3,
                       "stat_mods": {"physical_damage_taken_pct": -2.0},
                       "on_target": False}},
             source="CoA: 'Effectively healing yourself now reduces your "
                    "Physical damage taken by Stamina for 8 seconds. Can only "
                    "occur every 15 sec', and the strengths page names 'the "
                    "Physical damage reduction Untainted passively procs off "
                    "its own healing'. The icd carries the real internal "
                    "cooldown. Units: percentage POINTS inside a proc."),
        node(O, "disciplined_mind", "Disciplined Mind",
             "Increases the healing done by Benediction by 10% per rank.",
             3, 1, 2, {"ability_templar_benediction_healing": 0.10},
             connect=["uthers_legacy"],
             source="CoA: 'Increases the healing of Benediction by 15% and "
                    "causes it to dispel 1 poison and disease effect' (2 "
                    "ranks). A talent cannot add a dispel to an ability, so "
                    "the healing half carries the node. ability_<id>_healing "
                    "is live and was dead for months - eighteen talents were "
                    "authored on it before only _damage was read."),
        node(O, "fortified_body", "Fortified Body",
             "Increases your total health by 2% and grants healing power "
             "equal to 3% of your Stamina per rank.",
             3, 2, 3, {"max_health_pct": 0.02,
                       "healing_power_from_stamina_pct": 0.03},
             connect=["holy_warstaff"],
             source="CoA: 'Allies within 40 yds receive 6% more healing ... "
                    "Additionally, increases your maximum health by 6%', and "
                    "Benediction 'scales with Stamina'. Allied healing "
                    "received is not a talent-scoped effect, so the node "
                    "carries the Stamina-to-healing conversion that makes "
                    "Benediction work instead. NOTE max_health_pct is a "
                    "FRACTION: 0.02 is +2%. Guardian shipped 2.0 on this key "
                    "and measured 99,156 effective HP against the next tank's "
                    "2,987."),
        node(O, "duty_calls", "Duty Calls",
             "Increases all damage you deal by 2% per rank.",
             3, 3, 3, {"all_damage": 0.02}, connect=["sacred_resistance"],
             source="CoA: 'Casting abilities that grant an Oath now increases "
                    "your damage dealt and movement speed by 2% for 15 "
                    "seconds, stacking 5 times'. There is no movement speed "
                    "key, and the stacking ramp has no hook, so the damage "
                    "half is flat."),

        node(O, "barrier_of_light", "Barrier of Light",
             "Increases your threat generation by 8% per rank.",
             4, 0, 3, {"threat_generation_pct": 0.08},
             connect=["untainted"],
             source="CoA: 'For the duration, threat generated by your allies "
                    "is redirected to you', and 'Barrier of Light to pull "
                    "allies' threat onto yourself'. Threat redirection has no "
                    "hook, but threat generation does, and this is the tree's "
                    "only threat node - set at Warrior Defiance's 8%/rank so "
                    "the two tanks hold aggro equally. NOTE the key: "
                    "threat_generation_pct is a FRACTION in a talent and "
                    "percentage POINTS in an ability's stat_mods, and the "
                    "talent side only started working in 992ed62."),
        node(O, "battlepriest", "Battlepriest",
             "Reduces the magic damage you take by 2% per rank.",
             4, 1, 3, {"magic_damage_taken_pct": -0.02},
             connect=["disciplined_mind", "fortified_body"],
             source="CoA: 'While above 80% health or below 20% health, you now "
                    "take 20% reduced Magic damage'. The two-ended condition "
                    "cannot be expressed - low_health_damage_reduction_pct "
                    "covers one end and nothing covers the other - so it is "
                    "unconditional and much smaller. Talent units: FRACTION."),
        node(O, "lightkeeper", "Lightkeeper",
             "Increases your parry chance by 1% and the damage of Condemn by "
             "6% per rank.",
             4, 2, 3, {"parry": 1.0,
                       "ability_templar_condemn_damage": 0.06},
             connect=["duty_calls"],
             source="CoA tier-6: 'Periodic damage dealt by Condemn now has a "
                    "15% chance to increase your parry chance by 2% ... "
                    "stacking 3 times' and 'also has a 15% chance to burst'. "
                    "Condemn's ticks cannot proc anything (see Uther's "
                    "Legacy), so both halves become flat: the parry it would "
                    "have stacked to, and more Condemn damage."),

        node(O, "mending_ward", "Mending Ward",
             "While below 35% health, you take 8% less damage per rank.",
             5, 0, 2, {"low_health_damage_reduction_pct": 0.08},
             connect=["barrier_of_light"], total_slots=3,
             source="CoA tier-6: 'Next instance of direct damage taken while "
                    "below 35% maximum health will consume these stacks to "
                    "heal you'. A one-shot consumed heal has no payload "
                    "shape, so the node carries the engine's low-health "
                    "mitigation instead. Deliberately WITHOUT "
                    "low_health_threshold_pct: talent effects are summed per "
                    "point, so a 2-rank node carrying 0.35 would reach 0.70 "
                    "and count 70% health as 'low'. take_damage defaults the "
                    "threshold to 0.35 when the key is absent, which is the "
                    "number CoA wants anyway."),
        node(O, "eternal_blessing", "Eternal Blessing",
             "Increases your Holy damage by 4% and your healing done by 4% "
             "per rank.",
             5, 1, 2, {"holy_spell_damage": 0.04, "healing_done": 0.04},
             connect=["battlepriest"], total_slots=3,
             source="CoA tier-6: 'Increases your Holy damage and healing done "
                    "by 15% for 30 seconds'. A timed window becomes a "
                    "passive, which is the usual trade when the mechanic is a "
                    "cooldown and the slot is a talent."),
        node(O, "spiritual_abdicator", "Spiritual Abdicator",
             "Reduces all damage you take by 3% per rank.",
             5, 2, 2, {"damage_taken_pct": -0.03},
             connect=["lightkeeper"], total_slots=3,
             source="CoA: 'Your Spiritual Abdication now reduces damage taken "
                    "by an additional -5% per copy'. damage_taken_pct is a "
                    "FRACTION from both talents and buffs, unlike its "
                    "physical_ and magic_ siblings."),

        node(O, "tome_of_light", "Tome of Light",
             "Grants Tome of Light, a shield that absorbs 40% of your maximum "
             "health.",
             6, 0, 1, {"unlock_ability": "templar_tome_of_light"},
             node_type="active",
             connect=["mending_ward", "eternal_blessing",
                      "spiritual_abdicator"],
             total_slots=1,
             source="Capstone, and a real CoA tier-6 TE node. CoA: 'Tome of "
                    "Light shields for 100% of max health and Staffguard and "
                    "Untainted absorb repeatedly, which answers burst "
                    "windows'. The spec's whole case is layers - 'In an "
                    "extended skirmish you do not die' - and its stated "
                    "weakness is that 'once Tome of Light and the absorbs are "
                    "spent you tank the next chain raw', so the capstone is "
                    "the biggest layer rather than a passive."),
    ],
    "Built from reference/coa_sidekick/SPEC_templar__oathkeeper.txt and the "
    "oathkeeper half of reference/coa_sidekick/talents/templar.json. CoA calls "
    "this 'a Brewmaster Monk fused with Mistweaver fistweaving', rated A in "
    "dungeons, A in raids and A in battlegrounds. Two decisions shaped the "
    "tree. First, it is an AVOIDANCE tank, not a block tank: its free level-20 "
    "passive converts Agility into parry and Intellect into dodge, and its "
    "stat priority is Hit > Expertise > Agility > Stamina > Crit > Haste, with "
    "no block rating anywhere in it. The Templar carries a shield "
    "(weapon_types.json: sword_1h, mace_1h, shield) but this tree deliberately "
    "spends nothing on block chance or block value, which is what separates it "
    "from the other shield tank in the game. Second, the spec's defining "
    "passive is a Stagger clone - 'You now delay 40% of direct damage taken, "
    "instead taking it over 8 seconds' - and nothing in this engine delays "
    "damage. Every node that touched the stagger pool (Keeping the Oath, "
    "Sacred Oath, Holy Books) became flat mitigation instead, and that is the "
    "single largest departure from the reference in this class.")


# ================================================================ Crusader
C = "templar_crusader"
CRUSADER = tree(
    C, "Templar Crusader",
    "Oath melee DPS that holds its bank instead of dumping it. Several Oaths "
    "ride at once, Argent Blade keeps them alive and heals off its own "
    "damage, and Titanstrike finishes what is left.",
    [
        node(C, "pure_focus", "Pure Focus",
             "Increases your critical strike chance by 1% and your hit rating "
             "by 1 per rank.",
             0, 0, 5, {"crit_chance_physical": 1.0, "hit_rating": 1},
             source="CoA: 'Increases the chance to trigger Scourgebane by 5% "
                    "and your chance to hit by 2%' (2 ranks). A proc's chance "
                    "cannot be raised by a separate talent, so the "
                    "Scourgebane half becomes crit, which is the next stat in "
                    "the spec's priority."),
        node(C, "lights_chosen", "Light's Chosen",
             "Grants spell power equal to 6% of your Agility and critical "
             "strike chance equal to 3% of your Intellect per rank.",
             0, 1, 5, {"spell_power_from_agility_pct": 0.06,
                       "crit_chance_from_intellect_pct": 0.03},
             source="CoA free level-20 passive, verbatim: 'Increases your "
                    "spell power by 30% of your Agility and your critical "
                    "strike rating by 15% of your Intellect'. 5 ranks of 6% "
                    "and 3% are exactly those numbers. Both are real "
                    "<target>_from_<source>_pct conversions."),
        node(C, "aggramars_rage", "Aggramar's Rage",
             "Increases your spell critical strike chance by 1% and your hit "
             "rating by 1 per rank.",
             0, 2, 5, {"crit_chance_spell": 1.0, "hit_rating": 1},
             source="CoA: 'Increases your Holy critical strike chance by 3% "
                    "and your expertise by 5' (2 ranks). Holy crit is spell "
                    "crit here, and expertise does not exist as a stat or a "
                    "key, so it lands as hit rating."),
        node(C, "chivalric", "Chivalric",
             "Increases your spell critical strike damage by 4% per rank.",
             0, 3, 5, {"crit_damage_spell": 0.04},
             source="CoA: 'Increases your critical damage with Holy spells "
                    "and abilities by 15%'. holy_crit_damage_pct is live, but "
                    "the whole Crusader Holy kit is spell-school here, so the "
                    "general key covers it without splitting hairs."),

        node(C, "paladin_training", "Paladin Training",
             "Increases the damage of Righteous Lunge and Argent Blade by 6% "
             "per rank.",
             1, 0, 5, {"ability_templar_righteous_lunge_damage": 0.06,
                       "ability_templar_argent_blade_damage": 0.06},
             connect=["pure_focus"],
             source="CoA: 'Increases the damage of Righteous Lunge and Argent "
                    "Blade by 20%'. These are the spec's two builders, and "
                    "CoA's whole case for it is that holding the bank beats "
                    "spending it, so the builders are where the points go."),
        node(C, "warrior_of_tyr", "Warrior of Tyr",
             "Your damage has a 10% chance per rank to restore 8 Combo.",
             1, 1, 3, {}, connect=["lights_chosen"],
             proc={"trigger": "on_damage_cast", "chance": 10, "icd": 1,
                   "grant_resource": {"resource": "combo", "amount": 8}},
             source="CoA: 'Periodic damage dealt now has a 10% chance to "
                    "generate 5 Energy', and 'Energy is the fuel that "
                    "Improved Scarlet Hammer and Warrior of Tyr feed back'. "
                    "Periodic ticks cannot proc (they run through "
                    "tick_status_effects with no caster), so it listens for "
                    "casts instead."),
        node(C, "righteousness", "Righteousness",
             "Increases your Holy damage by 2% per rank.",
             1, 2, 5, {"holy_spell_damage": 0.02},
             connect=["aggramars_rage"],
             source="CoA: 'Your Chastise now always triggers Scourgebane on "
                    "your target'. A guaranteed proc on one named ability has "
                    "no shape here, so the node raises the Holy damage both "
                    "Chastise and Scourgebane deal."),
        node(C, "scourgebane", "Scourgebane",
             "Your damage has a 20% chance to strike again for a quarter as "
             "much.",
             1, 3, 1, {}, connect=["chivalric"],
             proc={"trigger": "on_damage_cast", "chance": 20, "icd": 0,
                   "bonus_pct": 0.25},
             source="CoA free level-10 passive, verbatim: 'Direct damage dealt "
                    "now has a 20% chance to strike an enemy with "
                    "Scourgebane, dealing an additional AP Holyflame Damage'. "
                    "The extra hit carries no school: a talent's synthetic "
                    "StatusEffect is built without a damage_school, so "
                    "Holyflame resolves untyped."),

        node(C, "divine_strikes", "Divine Strikes",
             "Increases the damage of Argent Blade by 8% per rank.",
             2, 0, 3, {"ability_templar_argent_blade_damage": 0.08},
             connect=["paladin_training"],
             source="CoA: 'Damage dealt by Scourgebane now increases the "
                    "damage of Argent Blade by 5% for 6 seconds, stacking 10 "
                    "times'. The stack ramp has no hook; the node is the "
                    "damage it ramps to."),
        node(C, "radiant_blade", "Radiant Blade",
             "Increases all damage you deal by 2% per rank.",
             2, 1, 3, {"all_damage": 0.02}, connect=["warrior_of_tyr"],
             source="CoA: 'Increases the effectiveness of Oath: Righteous "
                    "Lunge by 25%' (2 ranks). That Oath 'makes your abilities "
                    "damage and heal for more' across the whole kit, so a "
                    "global damage node is the closest honest reading."),
        node(C, "focused", "Focused",
             "Increases the damage of Blade of Faith and Righteous Tempest by "
             "8% per rank.",
             2, 2, 3, {"ability_templar_blade_of_faith_damage": 0.08,
                       "ability_templar_righteous_tempest_damage": 0.08},
             connect=["righteousness"],
             source="CoA: 'Increases the damage of Blade of Faith and "
                    "Righteous Tempest by 25%'."),
        node(C, "retribution", "Retribution",
             "Your damage has a 15% chance per rank to strike again for 15% "
             "as much.",
             2, 3, 3, {}, connect=["scourgebane"],
             proc={"trigger": "on_damage_cast", "chance": 15, "icd": 1,
                   "bonus_pct": 0.15},
             source="CoA: 'Melee damage dealt now has a 20% chance to strike 2 "
                    "additional times for 30% of the damage dealt as Holy "
                    "Damage'. One bonus hit rather than two, because "
                    "bonus_pct resolves once per fire."),

        node(C, "templars_might", "Templar's Might",
             "Increases the damage of Chastise by 8% per rank.",
             3, 0, 3, {"ability_templar_chastise_damage": 0.08},
             connect=["divine_strikes"],
             source="CoA: 'Your Righteous Lunge and Chastise used on enemies "
                    "affected by your Condemn now deal 6% increased damage "
                    "per stack'. No ability can read another's debuff stacks, "
                    "so the bonus is unconditional and smaller."),
        node(C, "tyrs_blessing", "Tyr's Blessing",
             "Increases the damage of Condemn by 8% and all your damage over "
             "time by 2% per rank.",
             3, 1, 2, {"ability_templar_condemn_damage": 0.08,
                       "dot_damage": 0.02},
             connect=["radiant_blade"],
             source="CoA: 'Condemn now stacks 1 additional time'. Condemn is "
                    "one DoT here rather than a stacking one, so another "
                    "stack is more damage."),
        node(C, "serendipity", "Serendipity",
             "Reduces the Combo cost of your abilities by 3% per rank.",
             3, 2, 3, {"all_ability_cost_pct": -0.03},
             connect=["focused"],
             source="CoA: 'Increases the all damage dealt by party and raid "
                    "members by 3% ... In addition, reduces the cost of your "
                    "spells and abilities by -5%'. The party half is not a "
                    "talent-scoped effect; the cost half is, and it is what "
                    "lets this spec hold Oaths instead of spending them."),
        node(C, "judgement", "Judgement",
             "Increases the damage of Titanstrike by 8% per rank.",
             3, 3, 3, {"ability_templar_titanstrike_damage": 0.08},
             connect=["retribution"],
             source="CoA: 'Increases the damage of Scourgebane, Scarlet "
                    "Hammer, and Titanstrike by 25% on enemies below 20% "
                    "health'. Titanstrike is already execute-gated at 35%, so "
                    "its damage carries the node and the condition is "
                    "redundant."),

        node(C, "scarlet_training", "Scarlet Training",
             "Increases the damage of Scarlet Hammer by 10% per rank.",
             4, 0, 3, {"ability_templar_scarlet_hammer_damage": 0.10},
             connect=["templars_might"],
             source="CoA free level-30 passive: 'Casting Argent Blade while "
                    "Warrior of Dawn is active now transforms your next "
                    "Chastise into Scarlet Hammer'. The transform cannot be "
                    "expressed, so Scarlet Hammer is its own ability and this "
                    "node is what makes it worth pressing."),
        node(C, "holy_edge", "Holy Edge",
             "Increases your area damage by 8% per rank.",
             4, 1, 2, {"aoe_damage": 0.08},
             connect=["tyrs_blessing", "serendipity"],
             source="CoA: 'Damage dealt by Scourgebane and Scarlet Hammer now "
                    "strikes 1 additional nearby enemy' (2 ranks). Extra "
                    "targets on a proc have no hook, so the node scales the "
                    "cleave the spec already has."),
        node(C, "martial_training", "Martial Training",
             "Increases the damage of Chastise by 8% and your physical damage "
             "by 2% per rank.",
             4, 2, 3, {"ability_templar_chastise_damage": 0.08,
                       "physical_damage": 0.02},
             connect=["judgement"],
             source="CoA free level-50 passive: 'Your Chastise now deals an "
                    "additional 50% Weapon Damage'. Chastise is a Holy "
                    "ability here, so the weapon-damage half lands as general "
                    "physical damage rather than on Chastise's own school."),

        node(C, "titanfall", "Titanfall",
             "Increases the healing done by Titanstrike by 12% per rank.",
             5, 0, 2, {"ability_templar_titanstrike_healing": 0.12},
             connect=["scarlet_training"], total_slots=3,
             source="CoA tier-6: 'Your Titanstrike now heals you for twice the "
                    "damage dealt'. Doubling it outright would make the "
                    "spec's incidental self-heal its main sustain, which CoA "
                    "is explicit it is not: 'The healing is incidental "
                    "self-heal off Argent Blade and Titanstrike, not "
                    "throughput'."),
        node(C, "argent_knight", "Argent Knight",
             "Increases the damage of Righteous Tempest by 10% and of Condemn "
             "by 6% per rank.",
             5, 1, 2, {"ability_templar_righteous_tempest_damage": 0.10,
                       "ability_templar_condemn_damage": 0.06},
             connect=["holy_edge"], total_slots=3,
             source="CoA tier-6: 'Increases the damage dealt by Righteous "
                    "Tempest and Condemn by 30%. Additionally, Righteous "
                    "Tempest now reduces all damage taken by -20% while "
                    "active.' The mitigation half would need the talent to "
                    "edit an ability's buff, which no key does."),
        node(C, "legacy_of_the_silver_hand", "Legacy of the Silver Hand",
             "Increases your spell critical strike chance by 1% and your "
             "spell critical strike damage by 4% per rank.",
             5, 2, 2, {"crit_chance_spell": 1.0, "crit_damage_spell": 0.04},
             connect=["martial_training"], total_slots=3,
             source="CoA tier-6: 'Casting Argent Blade or Scarlet Hammer now "
                    "guarantees your next 2 instances of damage dealt by "
                    "Scourgebane to critically strike. Increases the critical "
                    "damage of Scourgebane by 15%.' A proc's crits cannot be "
                    "guaranteed, so both halves become real crit stats. CoA "
                    "calls this 'the crit/Scourgebane build' and the "
                    "competing pick to Testament of Strength."),

        node(C, "scarlet_champion", "Scarlet Champion",
             "Increases your spell critical strike chance by 3%, and your "
             "critical strikes increase your damage by 4% for 3 turns.",
             6, 0, 1, {"crit_chance_spell": 3.0}, node_type="active",
             connect=["titanfall", "argent_knight",
                      "legacy_of_the_silver_hand"],
             total_slots=1,
             proc={"trigger": "on_crit", "chance": 100, "icd": 1,
                   "apply_effect": {
                       "effect_id": "templar_scarlet_champion",
                       "name": "Scarlet Champion",
                       "effect_type": "buff",
                       "duration": 3,
                       "stat_mods": {"damage_dealt_pct": 4.0},
                       "on_target": False}},
             source="Capstone, and a real CoA tier-6 TE node. CoA: 'Your "
                    "damaging critical strikes now increase your Holy damage "
                    "dealt by 2% for 20 seconds, stacking 5 times ... At 5 "
                    "stacks, you are granted High General'. The five-stack "
                    "ramp and the High General payoff have no hook, so the "
                    "buff carries the value it would have reached. The buff "
                    "uses damage_dealt_pct, not holy_spell_damage: a status "
                    "effect's stat_mods never reach _damage_multiplier's "
                    "talent lookups, so a school damage key on a BUFF is "
                    "inert even though the same key on a talent works."),
    ],
    "Built from reference/coa_sidekick/SPEC_templar__crusader.txt and the "
    "crusader half of reference/coa_sidekick/talents/templar.json. CoA rates "
    "this S in raids and A in arena, 'Closest to retail Retribution "
    "Paladin', and is emphatic about the one thing that makes it different: "
    "'Crusader runs a typed-Oath engine, and reading it as a generic "
    "combo-point pool is the most common mistake ... Holy Power is fungible "
    "and patient, whereas Crusader's Oaths are typed, each builder granting a "
    "different buff, and they decay on a shared Oath Chain. That makes it a "
    "stack-maintenance spec far more than a bank-and-dump one.' Frontier's "
    "Combo pool IS a generic combo-point pool, and there is no Oath Chain "
    "timer, so the typing cannot survive the translation. What survives is the "
    "incentive: Serendipity and the builder damage nodes pay you for holding a "
    "full bank and pressing builders, while the only thing worth emptying it "
    "for is Righteous Tempest at 80 Combo. Two further gaps worth stating. "
    "CoA gates the best finishers behind a two-handed weapon ('The finisher "
    "kit is 2H-weapon-gated'), and the Frontier Templar has no two-handed "
    "proficiency at all (weapon_types.json: sword_1h, mace_1h, shield), so "
    "nothing here is weapon-gated. And Sacred Restraint, which stops Testament "
    "of Fortitude and Testament of Strength competing, only binds the "
    "Testaments that leave a buff behind, because exclusive_group lives on the "
    "StatusEffect a cast creates.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the files")
    args = parser.parse_args()

    ability_doc = {
        "class": "Templar",
        "_source_note": __doc__.strip().split("\n\n")[1].replace("\n", " "),
        "abilities": ABILITIES,
    }

    targets = [
        (ROOT / "data/abilities/templar.json", ability_doc),
        (ROOT / "data/talents/templar_zealot.json", ZEALOT),
        (ROOT / "data/talents/templar_oathkeeper.json", OATHKEEPER),
        (ROOT / "data/talents/templar_crusader.json", CRUSADER),
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
